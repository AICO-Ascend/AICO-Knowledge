# 后训练数据系统

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/data_module_design.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/data_module_design.md

# 一体化深度解读：mindspeed-rl 后训练数据系统

---

## 【定位】

本篇文档系统描述 mindspeed-rl 中**后训练数据调度模块（DataModule）的设计、机制与配置**，解决 LLM 强化学习（RL）后训练流程中推理框架与训练框架之间"多角色、多 DP、强耦合"的复杂数据流转与高并发读写问题，使各计算实例解绑于统一的中心化数据通道。

---

## 【技术要点】

1. **角色定位**：数据系统是连接**推理框架**与**训练框架**的"转运港口"，负责生产者→缓存→消费者的三步调度，各实例数据不再相互绑定。
2. **DataStrategy 双实现**：
   - **TD（TransferDock）**：单机内存队列，适合低并发/开发调试。
   - **TQ（TransferQueue）**：分片队列，支持高并发与分布式读写。
3. **数据通道选择**：通过 `rl_config.data_strategy` 指定，取值支持 `td / transfer_dock / dock` 或 `tq / transfer_queue / queue`，**默认 `td`**；由 `DataStrategy` 在 Trainer 中初始化并下发到各 Worker。
4. **高并发设计**：将一次访问拆为**数据采样**与**数据读写**两个过程，Index 未指定时走采样路径，Index 已指定时直接进入读写路径，以消除阻塞。
5. **Worker 读写逻辑**：每个循环依据 `self.all_consumed()` 决定是否继续；调用 `dispatch_transfer_dock_data()` 读、`collect_transfer_dock_data()` 写，所有任务面向单一数据源。
6. **关键 batch_size 关系（GRPO）**：`mini_batch_size ≤ global_batch_size`，**等于时为 on-policy，小于时为 off-policy**；各 micro_batch_size 设置时需考虑 `n_samples_per_prompt` 已被乘入。

---

## 【关键机制与数据】

### 工作原理与数据流

1. **三步数据流**：① 数据生产者（推理侧）将生成数据写入数据系统；② 数据系统写入预先分配的缓存区并更新状态；③ 数据消费者（训练侧）请求足量数据后，组织为 Batch 返回。**（原文："数据生产者将生成数据写入到数据系统中；数据系统将数据存储至预先分配的缓存区，并更新数据状态；数据消费者向数据系统发送请求……"）**
2. **集中式管理**：所有推理与训练实例的数据均存放在数据调度模块中统一调度，**避免了各个实例之间的绑定，提高了整体计算资源的利用率**（原文）。
3. **初始化机制**：数据系统在 `Trainer` 类中初始化，将引用作为参数传递给各 Worker，**保证各 Worker 共享同一数据模块实例**（原文）。
4. **采样/读写分离消除阻塞**：
   - 用户**未指定 Index**（如各类读请求）→ 派生类扫描并采样可读写 Index；
   - 用户**直接指定 Index**（如写请求需先读出再按 Index 写回）→ 直接进入数据读写阶段；
   - 数据读写阶段以采样或指定的 Index 进行访问，**完全消除了数据阻塞**（原文）。
5. **未来演进**：当前为单节点设计，**千卡以上大规模训练时可能成为瓶颈**；未来将支持分布式存储，**控制平面与数据平面分离**，管理节点维护数据状态、读写分布在各存储节点，**缓解网络带宽瓶颈与 IO 瓶颈**（原文）。

### 性能/规模数据

- 原文未提供具体的吞吐量、延迟、加速比或卡数基准数字；仅以"千卡以上大规模训练时可能成为瓶颈"做定性描述。

---

## 【表格解读】

### 表 1：DataStrategy 取值与别名（原文逐字还原）

| 值 | 含义 |
|:--|:--|
| `td` / `transfer_dock` / `dock` | 使用 TransferDock |
| `tq` / `transfer_queue` / `queue` | 使用 TransferQueue |

**解读**：同一实现支持三种字符串别名，便于迁移与兼容。`td` 偏向单机内存（开发），`tq` 偏向分片队列（高并发分布式）。

### 表 2：高并发场景下"采样/读写"阻塞矩阵（原文逐字还原）

| 并发场景 | 使用方式 | 数据采样过程 | 数据读写过程 |
|:----:|:----:|:----:|:----:|
| RL 角色间 | 给定 Index 访问 | 无阻塞 | 无阻塞 |
| RL 角色间 | 随机访问 | 无阻塞 | 无阻塞 |
| RL 角色内 | 给定 Index 访问 | 无阻塞 | 无阻塞 |
| RL 角色内 | 随机访问 | 有阻塞 | 无阻塞 |

**解读**：唯一存在阻塞的情形是"角色内 + 随机访问"的数据采样阶段；只要进入数据读写阶段（无论场景/访问方式），均可实现无阻塞。这印证了"采样/读写分离"设计的核心收益：**把阻塞收敛在采样环节**，读写路径全免阻塞。

### 表 3：batch_size 类核心参数（原文逐字还原）

| 参数名 | 参数位置 | 说明 |
|:----|:----|:----|
| `global_batch_size` | `megatron_training` | 每个 iteration 所处理的 Prompt 数量；对于 GRPO 算法，在代码中将自动与 `n_samples_per_prompt` 相乘 |
| `mini_batch_size` | `rl_config` | 每次更新 actor update 的 Prompt 数量；对于 GRPO 算法，在代码中将自动与 `n_samples_per_prompt` 相乘。该值需小于等于 `global_batch_size`，等于时即为 on-policy 算法，小于时为 off-policy 算法 |
| `actor_forward_micro_batch_size` | `rl_config` | actor 每次前向的 (Prompt, Response) 对数量；对于 GRPO 算法，设置时需指定考虑 `n_samples_per_prompt` 之后的值 |
| `ref_forward_micro_batch_size` | `rl_config` | ref 每次前向的 (Prompt, Response) 对数量；对于 GRPO 算法，设置时需指定考虑 `n_samples_per_prompt` 之后的值 |
| `micro_batch_size` | `actor_config` | 对于 actor update 任务每次前向+反向的 (Prompt, Response) 对数量；对于 GRPO 算法，设置时需指定考虑 `n_samples_per_prompt` 之后的值 |

**解读**：这是后训练数据量从"全局→分片→单次前向/反向"的层级关系。`global_batch_size` 与 `mini_batch_size` 的等/不等关系直接决定算法是 on-policy 还是 off-policy；GRPO 下需要在用户视角之外再乘以 `n_samples_per_prompt`，所以 micro 类参数设置时必须以"乘过之后"的样本数为基准。

### 表 4：dispatch_size 性能调优可选参数（原文逐字还原）

| 参数名 | 参数位置 | 说明 |
|:----|:----|:----|
| `actor_rollout_dispatch_size` | `config_cls/rl_config.py` | 【可选参数】actor rollout 的每路 DP 每次从 TD 中读出的 (Prompt, Response) 对的数据量；默认设置为 `global_batch_size * n_samples_per_prompt / actor_rollout_dp_size` |
| `actor_logprob_dispatch_size` | `config_cls/rl_config.py` | 【可选参数】actor logprob 的每路 DP 每次从 TD 中读出的 (Prompt, Response) 对的数据量；默认设置为 `global_batch_size * n_samples_per_prompt / actor_logprob_dp_size` |
| `actor_update_dispatch_size` | `config_cls/rl_config.py` | 【可选参数】actor update 的每路 DP 每次从 TD 中读出的 (Prompt, Response) 对的数据量；默认设置为 `global_batch_size * n_samples_per_prompt / actor_update_dp_size` |
| `ref_dispatch_size` | `config_cls/rl_config.py` | 【可选参数】ref logprob 的每路 DP 每次从 TD 中读出的 (Prompt, Response) 对的数据量；默认设置为 `global_batch_size * n_samples_per_prompt / ref_logprob_dp_size` |
| `reward_dispatch_size` | `config_cls/rl_config.py` | 【可选参数】reward 每路 DP（若有）每次从 TD 中读出的 (Prompt, Response) 对的数据量；对于 Reward Model，默认设置为 `global_batch_size * n_samples_per_prompt / reward_dp_size`；对于规则奖励默认设置为 `global_batch_size * n_samples_per_prompt`；手动设置时对于 GRPO 算法需保证为 `n_samples_per_prompt` 的整数倍 |
| `adv_dispatch_size` | `config_cls/rl_config.py` | 【可选参数】advantage 每次从 TD 中读出的 (Prompt, Response) 对的数据量；默认设置为 `global_batch_size * n_samples_per_prompt` |

**解读**：默认值通式为 `global_batch_size * n_samples_per_prompt / <对应角色 dp_size>`，即"按 DP 路数平均切分"。`reward_dispatch_size` 是唯一例外：Reward Model 仍按 DP 平均，但规则奖励不走 DP，需注意手动设置时须为 `n_samples_per_prompt` 的整数倍以保持 GRPO 的样本完整切片。

### 表 5：数据通道选择参数（原文逐字还原）

| 参数名 | 参数位置 | 说明 |
|:--|:--|:--|
| `data_strategy` | `config_cls/rl_config.py` | 数据通道选择：`td` 或 `tq`，默认 `td` |

**解读**：与表 1 的别名表配合使用；这里仅保留两种规范值（`td` / `tq`），是配置侧的"主入口"。

---

## 【公式解读】

原文未给出严格意义的数学公式，但有若干"默认值表达式"，按公式形式**逐字保留**如下并解释：

**(1) 各 dispatch_size 默认值（角色侧）**

$$
\text{dispatch\_size}_{\text{role}} \;=\; \frac{\text{global\_batch\_size} \times \text{n\_samples\_per\_prompt}}{\text{role\_dp\_size}}
$$

- `global_batch_size`：每个 iteration 的 Prompt 数量（来自 `megatron_training`）。
- `n_samples_per_prompt`：GRPO 下每个 Prompt 采样数（自动相乘）。
- `role_dp_size`：对应角色（actor_rollout / actor_logprob / actor_update / ref / reward）的 DP 路数。
- 作用：将"一次 iteration 的总 (Prompt, Response) 对"按 DP 平均分发；`role` ∈ {actor_rollout, actor_logprob, actor_update, ref}。
- 适用表 4 中前 4 行 + `reward_dispatch_size`（Reward Model 路径）。

**(2) 规则奖励的 reward_dispatch_size 默认值**

$$
\text{reward\_dispatch\_size}_{\text{rule}} \;=\; \text{global\_batch\_size} \times \text{n\_samples\_per\_prompt}
$$

- 符号含义同上。
- 作用：规则奖励不走 DP，因此不分片，整 iteration 一次性读出。
- 适用：`reward_dispatch_size` 的"规则奖励"路径。

**(3) adv_dispatch_size 默认值**

$$
\text{adv\_dispatch\_size} \;=\; \text{global\_batch\_size} \times \text{n\_samples\_per\_prompt}
$$

- 符号含义同上。
- 作用：advantage 计算不分 DP，整 iteration 一次性读出。

**(4) on-policy / off-policy 判别式**

$$
\text{mini\_batch\_size} \;=\; \text{global\_batch\_size} \;\;\Rightarrow\;\; \text{on-policy}
$$

$$
\text{mini\_batch\_size} \;<\; \text{global\_batch\_size} \;\;\Rightarrow\;\; \text{off-policy}
$$

- `mini_batch_size`：每次 actor update 的 Prompt 数量（`rl_config`）。
- `global_batch_size`：每 iteration 的 Prompt 数量。
- 作用：仅通过两 batch size 的等/不等关系区分 on/off-policy，无需引入额外算法标志位。

---

## 【关联】

文档显式涉及的上下游/相关模块（原文无内部链接，依据正文还原）：

- **Trainer（训练器）**：唯一进行数据系统初始化的位置；同时负责将 `DataStrategy` 选定的数据通道下发到各 Worker。
- **Worker（执行体）**：通过 `self.all_consumed()` 判定循环是否继续，调用 `dispatch_transfer_dock_data()` 读取、`collect_transfer_dock_data()` 写回；引用由 Trainer 注入。
- **`DataStrategy`**：数据通道的统一选择器，决定下发 TD 还是 TQ。
- **TransferDock（TD）**：单机内存队列实现，低并发/调试首选。
- **TransferQueue（TQ）**：分片队列实现，支持高并发与分布式读写。
- **推理框架 / 训练框架**：作为数据"生产者"与"消费者"的上下游两端，通过数据系统解耦。
- **`rl_config` / `config_cls/rl_config.py` / `megatron_training` / `actor_config`**：参数载体位置，分别承载 batch_size 类、dispatch_size 类、data_strategy 等配置。
- **RL 角色（generate_sequence、compute_log_prob、update、ref、reward、advantage 等）**：并发读写的数据使用者。
- **未来演进目标**：分布式存储 + 控制面/数据面分离，以缓解千卡规模下的网络与 IO 瓶颈。

---

## 【使用方法】

### 启用方式

1. **选择数据通道**（必选其一，默认 `td`）：
   ```yaml
   rl_config:
     data_strategy: td   # 或 tq；亦支持别名 transfer_dock / dock / transfer_queue / queue
   ```
2. **设置 batch_size 体系**（在 yaml 中分别落到对应位置）：
   ```yaml
   megatron_training:
     global_batch_size: <N>             # 每 iteration 的 Prompt 数
   rl_config:
     mini_batch_size: <M>                # M<=N；等于 N 即 on-policy
     actor_forward_micro_batch_size: <…> # GRPO 下需考虑已乘 n_samples_per_prompt
     ref_forward_micro_batch_size:   <…>
   actor_config:
     micro_batch_size: <…>               # actor update 前向+反向
   ```
3. **（可选）性能调优 dispatch_size**：在 `config_cls/rl_config.py` 路径下覆盖下列参数：
   ```yaml
   rl_config:
     actor_rollout_dispatch_size:   <global_batch_size * n_samples_per_prompt / actor_rollout_dp_size>
     actor_logprob_dispatch_size:   <…/ actor_logprob_dp_size>
     actor_update_dispatch_size:    <…/ actor_update_dp_size>
     ref_dispatch_size:             <…/ ref_logprob_dp_size>
     reward_dispatch_size:          # Rule：= global_batch_size * n_samples_per_prompt；
                                     # RM ：= global_batch_size * n_samples_per_prompt / reward_dp_size；
                                     # 手动设置时 GRPO 下须为 n_samples_per_prompt 整数倍
     adv_dispatch_size:             <global_batch_size * n_samples_per_prompt>
   ```
4. **运行约束**：dispatch_size 默认值会自动按 DP 平均；若手动指定，**GRPO 算法下需保证相关值为 `n_samples_per_prompt` 的整数倍**（原文："手动设置时对于 GRPO 算法需保证为 n_samples_per_prompt 的整数倍"）。

### 关键调用约定（来自 Worker 读写逻辑）

- 每轮循环先检查 `self.all_consumed()`；若本 GBS 仍有未处理数据则继续。
- 读：`dispatch_transfer_dock_data()`；写：`collect_transfer_dock_data()`。
- 初始化入口：Trainer；引用透传：各 Worker 共享同一数据模块实例。

> 原文未提供具体启动命令/CLI 示例或环境变量配置；如需 CLI 入口，请参考 mindspeed-rl 仓库主入口文档（本文档未涉及）。

## 图文联合解读

- `td_init.png`: **1) 图中内容**：左侧 RayGRPOTrainer 内含一个"初始化 GRPOTransferDock"模块，三条箭头从该模块扇出，分别指向右侧 ActorHybridWorker、ReferenceWorker 及省略号所示的更多 Worker，示意 Trainer 将同一数据通道实例下发给各计算节点。

**2) 技术结论**：采用**单实例共享**的数据初始化模式——数据调度模块仅在 Trainer 内构造一次，通过引用传递被所有 Worker 复用，实现集中式数据管理与实例解耦。

**3) 与文档论点关系**：图直接印证文档"数据系统在 Trainer 类初始化→作为参数传递给各 Worker→保证各 Worker 基于相同数据模块实例"的核心论述，是"转运港口"架构中数据通道统一性的可视化体现。
- `td_interaction_logic.png`: **图文联合解读**

1) **图的内容**：流程图描绘了Worker的计算循环：开始→定义数据需求→判断"是否仍有数据待消费"→是则循环执行`dispatch_transfer_dock_data`读数据→执行计算任务→`collect_transfer_dock_data`写数据→回到判断节点；否则结束任务。

2) **论证的技术结论**：Worker以"读—算—写"原子循环驱动，每轮按需向TransferDock通道取数与回写；通过条件判断实现自动终止，避免空转，体现TD作为"转运港口"在Worker侧的标准化消费模式。

3) **与文档关系**：对应文档"Worker读写逻辑"小节，展示TD策略下`dispatch`/`collect`接口的调用时序，与"无绑定调度、集中式管理"的论点互为印证。
