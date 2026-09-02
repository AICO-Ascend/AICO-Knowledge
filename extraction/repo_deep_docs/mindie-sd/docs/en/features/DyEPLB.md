# Dynamic Expert Load Balancing

> 仓 `mindie-sd` · 路径 `docs/en/features/DyEPLB.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/en/features/DyEPLB.md

# 文档深度解读：Dynamic Expert Load Balancing (DyEPLB)

---

## 【定位】

本文档解决 **DiT-MoE 视觉生成模型在 Expert Parallelism (EP) 部署中的"时空双重异质性"专家负载不均衡问题**——视觉数据的强空间局部性导致特定专家过载，而扩散模型去噪过程又使专家激活分布具有显著时间动态性，传统静态负载均衡策略失效，因此需要一种运行时动态调整专家权重的方案来保证推理效率。

---

## 【技术要点】

1. **运行时动态专家权重调整**：根据各 Rank 的负载信息动态调整专家权重分布，实现专家负载均衡与模型推理加速。
2. **非侵入式设计**：全局同步检查点与权重更新位置由模型实现方按需选择，不强制绑定特定代码位置。
3. **异步流水线处理**：算法计算与专家权重拼接通过额外线程与进程执行，最小化对主推理流程的影响。
4. **三种 EP 通信模式**：
   - **A2A**（标准 all-to-all）：通信均衡，适合通用场景
   - **AG**（all-gather）：需要对变换矩阵与 expert scores 做额外 matmul，适合需要全局同步的场景
   - **EX**（可控模式）：通过 `max_move` 参数限制专家迁移规模，适合与 offload 共存以降低峰值显存
5. **关键插入点**：在 MoE forward 中，需在 `npu_moe_init_routing` **之后** 与 `npu_grouped_matmul_finalize_routing` **之前** 插入负载收集与权重替换逻辑。
6. **与 CPU offload 的互斥提醒**：DyEPLB 涉及 H2D 数据传输，与 [CPU offload](cpu_offload.md) 同时启用时存在带宽竞争，需自行调整执行时序。

---

## 【关键机制与数据】

### 整体工作流程

1. **启动 EPLB 调度进程（独立进程）**：通过 `python -m mindiesd.eplb.eplb_scheduler` 启动，监听 `--host localhost --port 50001`，运行模式为 `--mode A2A`（示例）。
2. **模型侧初始化**：在 `model.init()` 之后，为 MoE 模块挂载 `ExpertLoadCollector`（负责收集每步专家负载）与 `DynamicDispatcher`（负责按需更新专家权重与映射）；通过 `construct_expert_info_transfer_pool` 建立 Rank 与调度进程之间的 socket 通信（IP/port/auth_key 三元组）。
3. **推理中每次 step 的循环**：
   - `npu_moe_init_routing` 生成 `expanded_tokens / expanded_row_idx / expanded_indices`
   - `expert_load_collector.collect_expert_load(expanded_indices)` 记录本步各 expert 命中分布
   - `dispatcher.check_consistency()` 判断是否需要触发重排（通过 `update_flag` 标记）
   - 若 `update_flag` 为真：`dispatcher.update_module_weight_and_map()` 返回新的 `weight1/weight2/local_expert_num/device_indices_map/local_expert_indices_map/local_expert_list`，并就地替换
   - 之后继续执行 `npu_grouped_matmul_finalize_routing`
4. **AG 模式专属步骤**：当 `EP_AG` 且 `self.dispatcher.update_flag` 为真时，需额外执行：
   ```
   expert_trans_tensor = self.dispatcher.get_expert_trans_tensor()
   trans_scores = torch.matmul(scores, expert_trans_tensor)
   ```
   即对原始 scores 左乘一个变换张量得到新的分配分数。

### 性能与数据要点（原文）

- 原文未提供具体的吞吐、时延、加速比等性能数据。
- 原文仅以 `world_size=2` 作为示例启动参数。
- `lb_interval`（EPLB 间隔步数）默认值为 `1`（即每步都收集）。
- `auth_key` 默认值为字面字符串 `"secret_key"`，并通过环境变量 `EPLB_AUTH_KEY` 注入。
- 示意图为 `figures/dyeplb_image_1.png`（原文中以图片形式展示，未提供文字数据）。

---

## 【表格解读】

### 表 1：EPLB Scheduler 启动参数（Integration Process 第 1 步）

| Parameter | Default | Description |
|------|--------|------|
| `world_size` | Required | Number of EPs |
| `expert_num` | Required | Number of global experts |
| `block_num` | Required | Number of MoE layers |
| `max_move` | — | Maximum number of experts to move in EX mode |
| `redundant` | — | Number of redundant experts |
| `mode` | Required | A2A / AG / EX |
| `auth_key` | `secret_key` | Reads the `EPLB_AUTH_KEY` environment variable by default |

**解读**：这是独立调度进程 `mindiesd.eplb.eplb_scheduler` 的命令行参数表。其中 `world_size / expert_num / block_num / mode` 为必填项——三者共同决定调度器所服务的 EP 拓扑规模、全局专家池规模与可均衡的 MoE 层数；`max_move` 仅在 `EX` 模式下生效，控制单次重排中可迁移的专家上限，从而约束峰值显存；`redundant` 字段在原表中仅以破折号"—"标注默认，未给出具体缺省值，需由用户显式传入；`auth_key` 默认值为字符串 `secret_key`（注意是字面量，不是占位符），同时支持通过 `EPLB_AUTH_KEY` 环境变量覆盖，用于调度进程与各 Rank 端通信的鉴权。

### 表 2：`ExpertLoadCollector` 类参数

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| `expert_num` | `int` | Yes | - | Number of global experts |
| `lb_interval` | `int` | No | `1` | EPLB interval steps |

**解读**：Collector 是挂在每个 MoE block 上的轻量级负载采样器。`expert_num` 必须与全局专家总数对齐以正确索引 `expanded_indices`；`lb_interval` 默认为 1 意味着"每步都收集"，增大该值可降低收集频率以减少开销，但相应地调度器响应滞后。

### 表 3：`DynamicDispatcher` 类参数

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| `expert_num` | `int` | Yes | - | Number of global experts |
| `weight1` | `Tensor` | Yes | - | UP weight |
| `weight2` | `Tensor` | Yes | - | DOWN weight |
| `rank_in_group` | `int` | Yes | - | Rank number within the EP communication group |
| `ep_size` | `int` | Yes | - | Number of EPs |

**解读**：Dispatcher 是真正负责按调度进程下发的策略重排本地专家权重的组件。`weight1 / weight2` 对应 MoE 中 up-projection 与 down-projection 的两份专家权重张量；`rank_in_group / ep_size` 标识当前 Rank 在 EP 通信域中的位置和总规模——这两个参数决定了本 Rank 应保留哪些专家、应向哪些 Rank 发送/接收哪些专家，是权重切片与 all-to-all 重排的基础。

### 表 4：`construct_expert_info_transfer_pool` 函数参数

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| `module` | `Module` | Yes | - | Initialized model |
| `rank_in_group` | `int` | Yes | - | Rank number within the EP communication group |
| `device` | `int` | Yes | - | Device number corresponding to the rank |
| `ip` | `str` | Yes | - | Same as the server IP |
| `port` | `int` | Yes | - | Same as the server port |
| `auth_key` | `str` | No | `secret_key` | Reads the `EPLB_AUTH_KEY` environment variable by default |

**解读**：该函数在每个 Rank 上启动通信 worker 线程池，连接调度进程。`module` 必须是已经完成 `init()` 的模型，以便 Dispatcher 能在 worker 线程中通过 `update_module_weight_and_map()` 安全地修改模型参数；`ip / port` 必须与 `eplb_scheduler` 启动时指定的地址一致；`device` 是当前 Rank 对应的 NPU 设备号，H2D 权重拷贝会落到该设备上；`auth_key` 与表 1 同义，默认 `secret_key` 并支持环境变量覆盖。

---

## 【公式解读】

原文无公式。

文档中出现的最接近"公式"的表达是一段 PyTorch 代码片段（位于 Integration Process 第 3 步，AG 模式专属）：

```python
expert_trans_tensor = self.dispatcher.get_expert_trans_tensor()
trans_scores = torch.matmul(scores, expert_trans_tensor)
```

**逐行解读**：
- `expert_trans_tensor`：由 Dispatcher 根据当前全局专家分布生成的变换张量，其形状与 `scores` 在专家维度上相容，用于将原始 token–expert 亲和度分数线性映射到 all-gather 模式所需的分配空间。
- `scores`：原始的 token 对各 expert 的打分矩阵。
- `torch.matmul(scores, expert_trans_tensor)`：标准矩阵乘法，将原始 scores 左乘变换张量，得到 `trans_scores`，供后续 all-gather 路径下的 expert 选择使用。

此表达式并非严格意义的数学公式，而是 AG 模式相对于 A2A 模式的额外计算开销所在——A2A 通过 all-to-all 直接搬运专家权重，而 AG 模式则通过变换矩阵在分数层面"重路由"。

---

## 【关联】

### 与文末内部链接的关系

- **[cpu_offload.md](cpu_offload.md)**：文档在 Technical Features 的 "Mutual exclusion reminder with CPU offload" 小节明确指出，DyEPLB 涉及 H2D（Host-to-Device）数据传输，与 CPU offload 同时启用时会争夺 PCIe/HBM 带宽。EX 模式通过 `max_move` 参数限制专家迁移规模，部分缓解与 offload 共存时的峰值显存问题，但用户仍需自行调整执行时序以避免带宽争抢。

### 模块上下游关系

- **上游（被调用方）**：
  - `mindiesd.eplb.eplb_scheduler`（独立进程，全局决策者）
  - 华为 NPU 算子 `torch_npu.npu_moe_init_routing`（提供 `expanded_indices` 供负载收集）
- **下游（调用方）**：
  - 华为 NPU 算子 `torch_npu.npu_grouped_matmul_finalize_routing`（消费更新后的 `weight1/weight2` 与本地专家映射）
- **同层组件**：
  - `ExpertLoadCollector`（采集侧）↔ `DynamicDispatcher`（执行侧）↔ `task_manager.construct_expert_info_transfer_pool`（通信侧）三者协同，构成完整的"采样 → 决策 → 重排"闭环。

---

## 【使用方法】

### 1. 启动 EPLB 调度进程（独立进程）

原文给出示例命令：

```shell
python -m mindiesd.eplb.eplb_scheduler \
    --world_size 2 \
    --host localhost \
    --port 50001 \
    --mode A2A
```

必填参数：`--world_size`、`--expert_num`、`--block_num`、`--mode`（A2A / AG / EX）；可选参数：`--max_move`（EX 模式）、`--redundant`、auth_key 通过 `EPLB_AUTH_KEY` 环境变量注入。

### 2. 模型侧接入（Python 代码模板）

```python
from mindiesd.eplb.dispatcher import DynamicDispatcher
from mindiesd.eplb.collector import ExpertLoadCollector
from mindiesd.eplb.task_manager import construct_expert_info_transfer_pool

model.init()

model.moe_module.block.expert_load_collector = ExpertLoadCollector(expert_num, lb_interval)
model.moe_module.block.dispatcher = DynamicDispatcher(expert_num, weight1, weight2, rank_in_group, ep_size)

if eplb_enabled:
    construct_expert_info_transfer_pool(
        module=model, rank_in_group=rank_in_group, device=device,
        ip=host, port=port, auth_key=auth_key
    )

model.forward()
```

### 3. 在 MoE forward 中插入采集/重排点

```python
expanded_tokens, expanded_row_idx, expanded_indices = torch_npu.npu_moe_init_routing(
    tokens, row_idx, indices, tokens.shape[0])

self.expert_load_collector.collect_expert_load(expanded_indices)
self.dispatcher.check_consistency()

if self.dispatcher.update_flag:
    weight1, weight2, local_expert_num, device_indices_map, \
        local_expert_indices_map, local_expert_list = \
        self.dispatcher.update_module_weight_and_map()
    self.weight1 = weight1
    self.weight2 = weight2
    self.local_expert_num = local_expert_num

tokens = torch_npu.npu_grouped_matmul_finalize_routing()
```

### 4. AG 模式额外步骤

在 AG 模式下，需要在 scores 被使用之前插入变换矩阵乘法：

```python
if EP_AG and self.dispatcher.update_flag:
    expert_trans_tensor = self.dispatcher.get_expert_trans_tensor()
    trans_scores = torch.matmul(scores, expert_trans_tensor)
```

### 5. 模式选择建议（原文）

- **A2A**：标准 all-to-all EP，通信均衡，**通用场景推荐**。
- **AG**：all-gather EP，需额外 matmul，**适合需要全局同步的场景**。
- **EX**：通过 `max_move` 限制专家迁移规模，**适合与 offload 共存以降低峰值显存**。

### 注意事项（原文）

- 算法计算与权重拼接通过额外线程/进程执行，**应避免阻塞主推理流**。
- 与 [CPU offload](cpu_offload.md) 同时启用时存在 H2D 带宽竞争，需自行调整执行时序。
- 原文未涉及 yaml/TOML 配置文件、环境变量全量清单、CLI 子命令 help 文本。

## 图文联合解读

- `dyeplb_image_1.png`: **1) 图内容**：左侧为Block i的ViT-MoE模块结构（Visual Tokens→Self-Attention→Cross-Attention→MoE Block→Hidden States）；右侧细化MoE数据流（Input Hidden→Gate→TopK→Token Dispatch→多个Router Expert→Token Combine→Output Hidden），并以Device/Host分隔线划开——Device侧Load Collector收集负载，Host侧Fast Planning Algorithm异步规划，再通过Weight Update回注Combine，虚线表示Async Transfer与Selective Module。

**2) 技术结论**：论证负载采集与专家权重调整均放在主推理流的旁路上异步执行，全局同步不阻塞关键路径，可动态重平衡各Rank的专家负载。

**3) 与文档关系**：图示直接支撑文档所提"非侵入式设计"与"异步流水线处理"两大特征，回应DiT-MoE因视觉空间局部性与扩散时间动态性导致的传统静态均衡失效问题。
