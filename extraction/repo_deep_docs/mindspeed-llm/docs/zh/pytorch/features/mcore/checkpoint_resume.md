# 断点续训

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/mcore/checkpoint_resume.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/mcore/checkpoint_resume.md

# mindspeed-llm 断点续训（Checkpoint Resume Training）文档深度解读

---

## 【定位】

本文档描述了在昇腾 NPU 大规模分布式预训练中，**因硬件故障或资源调度等原因导致训练中断后，从最近保存的检查点恢复训练状态（模型参数、优化器状态、随机状态、迭代步数、学习率调度器）并继续训练的能力**——即"断点续训（Checkpoint Resume Training）"功能的使用方式与硬性约束。

---

## 【技术要点】

1. **分布式优化器是续训的前置条件**：必须开启 `--use-distributed-optimizer`，使优化器状态按数据并行方式分布保存（写入 `distrib_optim.pt`），否则后续恢复时无法正确加载优化器分片。
2. **三类禁止设置的"破窗"参数**：续训场景下 `--finetune`、`--no-load-optim`、`--no-load-rng` 任意一个被设置，都会跳过优化器状态或随机状态的加载，导致续训退化为"仅加载权重"的冷启动；保存场景下 `--no-save-optim`、`--no-load-rng`（笔误，应为 `--no-save-rng`）同理会丢失续训所需的中间状态。
3. **周期性检查点保存**：通过 `--save /your/checkpoint/path` 与 `--save-interval 500`（每 500 步一次）将完整状态落盘，目录按 `iter_<迭代步>/mp_rank_<TP>_000/` 双层组织，单个 rank 下同时存放 `distrib_optim.pt`（分布式优化器分片）与 `model_optim_rng.pt`（模型权重 + 优化器 + 随机状态）。
4. **断点自动定位机制**：恢复时只需传入 `--load ${CHECKPOINT_PATH}`，系统会读取目录下的 `latest_checkpointed_iteration.txt` 自动定位到最新迭代步数，并据此加载 `iter_<步数>` 子目录。
5. **完整恢复四项状态**：恢复后不仅加载模型参数，还包括 Adam 等优化器的 momentum / variance、学习率调度器状态、已完成的训练步数，从而避免重复训练。
6. **三组硬性约束保证可恢复性**：检查点文件完整无损；恢复时的 batch size / 模型结构 / 训练步数 / 优化器类型必须与保存时一致；NPU 数量与 TP/DP 并行策略必须保持不变。

---

## 【关键机制与数据】

**工作原理与数据流**：

- **保存数据流（原文）**：训练运行时 → 触发条件满足（如每 500 步）→ 序列化 `model_optim_rng.pt`（含模型权重 + 优化器 + 随机状态）与 `distrib_optim.pt`（分布式优化器分片）→ 同时写入 `latest_checkpointed_iteration.txt` 标记最新可用版本。
- **加载数据流（原文）**：启动预训练并传入 `--load` → 系统读取 `latest_checkpointed_iteration.txt` → 解析最新 `iter_<步数>` 目录 → 按当前 rank 的 `mp_rank_xx_yyy` 路径加载对应分片 → 还原模型参数、优化器状态（含 Adam momentum/variance）、学习率调度器、迭代步数与随机状态。
- **典型日志输出（原文）**：
  ```
  successfully loaded checkpoint from xx at iteration x
  (min, max) time across ranks:
  load-checkpoint ....................:(9289.88, 9288.22)
  ```
  原文给出的 `load-checkpoint` 耗时区间为 `(9289.88, 9288.22)` 秒（按括号标注顺序为 min/max，这是用户在 `xx` 与 `x` 处的占位符，未给出具体 NPU 数 / 模型规模等上下文）。

> 注：原文未给出端到端吞吐、收敛曲线、保存耗时占比等性能数据，仅有上述一次性加载耗时区间，故不展开推断。

---

## 【表格解读】

### 表格 1：断点续训前提条件参数表（原文逐字还原）

| 参数                            | 说明                             |
|-------------------------------|--------------------------------|
| `--use-distributed-optimizer` | 必须开启，使优化器状态也按数据并行方式分布保存，便于后续恢复 |
| `--finetune`                  | ❌ 不可设置，否则会跳过优化器状态加载            |
| `--no-load-optim`             | ❌ 不可设置，否则不会恢复优化器状态（如学习率、动量等）   |
| `--no-load-rng`               | ❌ 不可设置，否则不会恢复随机状态              |

**逐行解读**：

- **`--use-distributed-optimizer`（必开）**：开启后 Megatron 风格的分布式优化器会将 optimizer state 按 DP 维度切分并各自持久化，避免在恢复时出现单点加载/广播瓶颈，是续训能落到每个 DP rank 的基础。
- **`--finetune`（禁开）**：该参数用于微调场景，会显式绕过 optimizer 与 rng 的加载路径，若误开则相当于把"续训"降级为"基于预训练权重的二次训练"，动量与方差都会从 0 重新累积。
- **`--no-load-optim`（禁开）**：与 `--finetune` 不同但效果相近——它显式跳过 optimizer state 加载，会导致恢复后的学习率 / 动量 / 方差回到初始值，破坏收敛连续性。
- **`--no-load-rng`（禁开）**：随机状态（DataLoader 采样位置、Dropout 随机数、ZeRO 切分随机种子等）若不复位，会出现 dropout mask 不一致、micro-batch 采样偏移等问题，使恢复后的训练轨迹与未中断时无法严格对齐。

### 表格 2：保存训练权重参数表（原文逐字还原）

| 参数                            | 说明                             |
|-------------------------------|--------------------------------|
| `--use-distributed-optimizer` | 必须开启，使优化器状态也按数据并行方式分布保存，便于后续恢复 |
| `--no-save-optim`             | ❌ 不可设置，否则不会保存优化器状态（如学习率、动量等）   |
| `--no-save-rng`               | ❌ 不可设置，否则不会保存随机状态              |

**逐行解读**：

- **`--use-distributed-optimizer`（必开）**：与"加载"侧要求一致，保证"保存"侧也是按 DP 分片写入 `distrib_optim.pt`，从而与 `--load` 时按 rank 读取的分片格式完全对等。
- **`--no-save-optim`（禁开）**：禁用后会从持久化内容中剔除 optimizer state，恢复时即使满足加载侧条件，也只能拿到权重，等价于一次"裸权重恢复"，Adam 的 m/v 全部丢失。
- **`--no-save-rng`（禁开）**：禁用后随机状态不会被序列化，恢复时即使后续步骤不显式 `--no-load-rng`，也会因没有可加载内容而退化；原文以 ❌ 形式强调此为强制性约束。

---

## 【公式解读】

原文无公式。

（文档属于工程使用说明，仅涉及参数配置、目录结构、日志样例，未出现任何 LaTeX 公式或伪代码算法推导。）

---

## 【关联】

**与其他特性的耦合关系（基于文中明文涉及项）**：

- **`--use-distributed-optimizer` 与分布式优化器特性**：该参数是 MindSpeed-LLM 分布式优化器特性的入口开关，文档贯穿"保存"与"加载"两阶段都要求开启，实质上是要求续训能力建立在分布式优化器之上。
- **`--finetune` 与微调（Finetune）特性**：文档显式声明续训与微调互斥——使用 `--finetune` 会跳过 optimizer / rng 加载，意味着用户在微调场景下若想复用 optimizer 状态，不能简单开启 `--finetune`，需另寻路径（本文未给出）。
- **`--save / --save-interval` 与检查点保存机制**：保存侧依赖框架内置的 checkpoint 序列化能力，目录结构 `iter_<N>/mp_rank_<TP>_<DP>/{distrib_optim.pt, model_optim_rng.pt}` 与 `latest_checkpointed_iteration.txt` 标记文件是续训的"输入契约"。
- **与并行策略的关系**：使用约束第 3 条提到 TP/DP 并行策略需保持不变，说明续训能力与 TP（张量并行）、DP（数据并行）切分紧耦合——若切分维度变化，`mp_rank_xx_yyy` 路径与分片张量形状都会失配。
- **与硬件/NPU 拓扑的关系**：使用约束第 3 条同时要求 NPU 数量不变，提示续训对集合通信组（TP/DP group）的 rank 编号有强假设。

> 原文未提供任何内部链接（"（无）"），故未引用其他特性文档做交叉解读。

---

## 【使用方法】

**1. 续训前置参数（启动预训练时设置）**：
```bash
--use-distributed-optimizer   # 必开
# 禁止同时设置：--finetune / --no-load-optim / --no-load-rng
```

**2. 保存侧配置**：
```bash
--save /your/checkpoint/path \
--save-interval 500   # 每 500 步保存一次（原文示例值）
```
保存产物结构：
```shell
/your/checkpoint/path/
├── latest_checkpointed_iteration.txt
├── iter_0000001/
│   └── mp_rank_00_000/
│       ├── distrib_optim.pt
│       └── model_optim_rng.pt
└── iter_0000500/
    └── ...
```

**3. 恢复侧启动命令片段**：
```text
CHECKPOINT_PATH=/your/checkpoint/path

--use-distributed-optimizer  # 使用分布式优化器（必选）
--load ${CHECKPOINT_PATH}
```
系统自动读取 `latest_checkpointed_iteration.txt` 定位最新迭代步并恢复全部状态。

**4. 恢复成功日志标识**：
```shell
successfully loaded checkpoint from xx at iteration x
(min, max) time across ranks:
load-checkpoint ....................:(9289.88, 9288.22)
```

**5. 硬性使用约束**：
- 文件完整性：$CHECKPOINT_PATH 下检查点文件完整无损；
- 配置一致性：恢复时的 batch size、模型结构、训练步数、优化器类型需与保存时一致；
- 分布式环境匹配：NPU 数量与 TP/DP 并行策略保持不变，否则会导致加载失败。
