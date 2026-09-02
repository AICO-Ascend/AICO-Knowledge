# 断点续训功能使用介绍

> 仓 `mindspeed-llm` · 路径 `docs/zh/mindspore/features/checkpoint_resume.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/mindspore/features/checkpoint_resume.md

# 断点续训功能 — 一体化深度解读

## 【定位】

本文档阐述了在昇腾大规模预训练场景下，因硬件故障或资源调度导致训练中断时，如何通过检查点（Checkpoint）机制保存与恢复模型/优化器状态，实现从断点处无缝继续训练的能力。

---

## 【技术要点】

1. **分布式优化器是续训的前置条件**：必须在启动脚本的 `GPT_ARGS` 中开启 `--use-distributed-optimizer`，使优化器状态按数据并行方式分布保存；并且**严禁**同时设置 `--finetune` 或 `--no-load-optim`，否则优化器状态（含动量、方差、学习率等）将不会被恢复，"续训"退化为"权重初始化重启"。
2. **周期性检查点保存**：通过 `--save $SAVE_PATH` 指定路径、`--save-interval 500` 指定频率（每 500 步），自动持久化模型权重、优化器状态、训练步数与随机状态。
3. **检查点目录结构双轨**：每个迭代步（如 `iter_0000001/`、`iter_0000500/`）下按模型并行 rank 拆分（`mp_rank_00_000`），每个 rank 文件夹包含两份关键文件——`distrib_optim.pt`（分布式优化器分片）与 `model_optim_rng.pt`（模型参数 + 优化器状态 + 随机种子的合并存档）。
4. **自动断点定位机制**：保存目录下固定存在 `latest_checkpointed_iteration.txt` 文件，加载时由系统自动读取该文件确定最新迭代步数，无需人工指定 `--load-iteration`。
5. **启动加载方式**：通过 `--load $CHECKPOINT_PATH` 触发恢复，加载对象同时覆盖模型参数、Adam 的 momentum/variance、学习率调度器状态以及已完成步数。
6. **环境强一致性约束**：恢复时 NPU 卡数与 TP/DP 切分必须与保存时一致，batch size、模型结构、优化器类型也必须保持，否则会导致加载失败。

---

## 【关键机制与数据】

### 工作原理（三阶段闭环）

**保存阶段**——训练运行时，只要 `--save` 路径被配置、且到达 `--save-interval`（原文示例为 500 步）所规定的步数，系统会触发一次完整快照，将模型权重与优化器状态序列化到磁盘；同时将当前迭代步数写入全局索引文件 `latest_checkpointed_iteration.txt`，形成"最新一份可恢复存档"的指针。

**定位阶段**——训练恢复启动时，`msrun` 拉起 `pretrain_gpt.py` 并传入 `--load $CHECKPOINT_PATH`；框架打开该路径下的 `latest_checkpointed_iteration.txt`，读取其中的最大迭代编号，从而决定从哪一个 `iter_xxxxxxx` 子目录加载。

**恢复阶段**——按当前进程的模型并行 rank（如 `mp_rank_00_000`），并行加载 `model_optim_rng.pt`（模型主体与随机种子）和 `distrib_optim.pt`（分布式优化器分片）；同时从检查点元数据中还原学习率调度器与已完成步数，使下一次 forward 从断点正确接续。

### 数据流（以原文目录结构为骨架）

```
SAVE_PATH/
├── latest_checkpointed_iteration.txt     ← 索引文件，记录最新 iter
├── iter_0000001/                          ← 第 1 次快照
│   └── mp_rank_00_000/
│        ├── distrib_optim.pt              ← 分布式优化器分片
│        └── model_optim_rng.pt            ← 模型权重 + 优化器状态 + 随机数
└── iter_0000500/                          ← 第 500 步快照（与 500 步保存间隔对应）
    └── mp_rank_00_000/
         ├── distrib_optim.pt
         └── model_optim_rng.pt
```

### 性能/日志数据（原文）
- 保存频率：原文示例 `500` 步。
- 加载耗时日志样例：`load-checkpoint ....................:(9289.88, 9288.22)`，单位为毫秒，括号内为跨 rank 的 `(min, max)` 时间，原文标注 `across ranks(ms)`。

---

## 【表格解读】

### 关键参数说明表（原文逐字还原）

| 参数 | 说明 |
|------|------|
| `--use-distributed-optimizer` | 必须开启，使优化器状态也按数据并行方式分布保存，便于后续恢复 |
| `--finetune` | ❌ 不可设置，否则会跳过优化器状态加载 |
| `--no-load-optim` | ❌ 不可设置，否则不会恢复优化器状态（如学习率、动量等） |

**逐行解读：**

- **第一行 `--use-distributed-optimizer`**：这是续训链路的**使能开关**。分布式优化器把 Adam 的动量与方差按 DP 维度切分到各 rank 上独立保存，相当于把"一份巨大的优化器状态"拆成多份小文件，从而既降低单卡显存压力，又使每张 NPU 能各自恢复自己负责的那一份状态。
- **第二行 `--finetune`**：被显式打上 `❌` 红色禁用标记。`--finetune` 模式下框架假设你只是加载预训练权重做下游微调，因此**主动跳过**优化器状态加载——这与"续训"语义直接冲突，所以禁止并存。
- **第三行 `--no-load-optim`**：同样被禁用。该参数会让加载阶段**根本不读**优化器 checkpoint，导致动量、方差、学习率全部归零，等同于把训练"打回原点"。原文用括号补充说明了它影响的字段——学习率与动量。

> **整张表的核心意图**：这是一份"参数兼容性约束清单"，通过三条规则告诉用户：要真正"续训"必须满足"分布式优化器开"且"finetune 关"且"不跳过优化器加载"这一组互斥关系，否则系统的优化器状态恢复路径会被切断。

---

## 【公式解读】

**原文无公式。** 全文不涉及任何数学表达式或伪代码公式，仅以 bash/shell 命令片段和日志样例呈现配置与行为。

---

## 【关联】

本文档在特性层面与以下模块/能力存在隐含依赖（基于文末"内部链接: (无)"可知本文未主动给出跳转链接，但根据内容可推断如下关联关系）：

- **分布式优化器（Distributed Optimizer）**：被本文反复强调为续训的"必选前置"，因此本文与上游 `Distributed Optimizer` 功能文档强耦合。
- **优化器状态（Optimizer States，含 Adam 的 momentum / variance）**：文中明确点出这是恢复对象的子项，关联到优化器实现的存储格式。
- **学习率调度器（LR Scheduler）**：被列入"自动恢复内容"，与训练脚本中的 scheduler 配置相关。
- **`msrun` 启动器**：本文出现 `msrun ${DISTRIBUTED_ARGS} pretrain_gpt.py` 的标准启动范式，表明本特性运行于 MindSpore + 昇腾 NPU 的 `msrun` 分布式运行时之上。
- **并行策略（TP / DP）**：文末注意事项 #3 明确要求 NPU 数量和 TP/DP 与保存时一致，意味着本特性与并行切分配置是强耦合的。

---

## 【使用方法】

### 1. 启动训练时开启续训能力（保存侧）

在 `GPT_ARGS` 中：
```bash
GPT_ARGS="
    [其他参数...] \
    --use-distributed-optimizer
"
```
并禁止添加 `--finetune` 与 `--no-load-optim`。

### 2. 配置保存路径与频率
```bash
--save /your/checkpoint/path \
--save-interval 500
```

### 3. 从断点恢复训练（加载侧）

```bash
GPT_ARGS="
    [其他参数...] \
    --use-distributed-optimizer
"

msrun ${DISTRIBUTED_ARGS} pretrain_gpt.py \
    [其他参数...] \
    --load $CHECKPOINT_PATH
```

### 4. 验证是否成功恢复

训练启动日志中出现以下内容即为成功（原文样例）：
```
successfully loaded checkpoint from xx at iteration x
(min, max) time across ranks(ms):
load-checkpoint ....................:(9289.88, 9288.22)
```

### 5. 注意事项（原文）
- 检查 `$CHECKPOINT_PATH` 下文件完整无损。
- 恢复时 batch size、模型结构、训练步数、优化器类型需与保存时一致。
- NPU 数量与 TP/DP 并行策略需保持不变。
