# Checkpoint-based Resumable Training

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/checkpoint_resume.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/checkpoint_resume.md

# 一体化深度解读: Checkpoint-based Resumable Training

## 【定位】

这篇文档解决**大规模模型预训练过程中,因硬件故障或资源调度等原因导致训练中断后,如何通过检查点(checkpoint)机制无缝恢复训练**的问题。它围绕"启动参数配置 → 周期性保存检查点 → 中断后加载恢复 → 验证恢复结果"四个环节,给出在昇腾 NPU 分布式环境下使用该能力的完整指引。

---

## 【技术要点】

1. **分布式优化器是前提条件**: 必须启用 `--use-distributed-optimizer`,使优化器状态以分布式方式跨 data parallel 维度保存,这是后续能被正确恢复的基础。
2. **三类"反向"参数不可设置**: `--finetune`、`--no-load-optim`、`--no-load-rng` 任一被启用,都会导致优化器状态或随机状态不被恢复,系统无法"真正续训"。
3. **检查点由系统按间隔自动保存**: 通过 `--save $SAVE_PATH` 指定路径、`--save-interval` 指定间隔(如示例中每 500 步保存一次),自动落盘模型权重、优化器状态、训练迭代数、随机状态四类内容。
4. **检查点目录按 iteration 组织**: 每次保存生成 `iter_xxxxxxxx/` 子目录,根目录下的 `latest_checkpointed_iteration.txt` 记录最新迭代号,恢复时系统自动读取该文件定位最新检查点。
5. **恢复入口是 `--load`**: 通过 `torchrun pretrain_gpt.py --load $CHECKPOINT_PATH` 触发,系统读取 `latest_checkpointed_iteration.txt` 自动定位最新检查点并恢复模型与优化器状态。
6. **三类恢复完整性约束**: 检查点文件完整、训练配置(batch size/模型结构/迭代数/优化器类型)一致、分布式环境(NPU 数量与 TP/DP 并行策略)不变,任一不满足都会导致加载失败或恢复语义失效。

---

## 【关键机制与数据】

**工作原理与数据流(以原文为依据)**:

- **保存阶段**: 启动训练时配置 `--save $SAVE_PATH` 与 `--save-interval`(原文示例 `--save-interval 500`),训练循环每 500 步触发一次全量检查点落盘。每个 iteration 目录下按 `mp_rank_xx_xxx` 划分,内含两份核心文件: `distrib_optim.pt`(分布式优化器状态)与 `model_optim_rng.pt`(模型权重 + 优化器状态 + 随机状态的合集,原文未进一步拆解)。
- **加载阶段**: 通过 `--load $CHECKPOINT_PATH` 触发,系统读取 `$CHECKPOINT_PATH/latest_checkpointed_iteration.txt`,自动定位到最近一次保存的 `iter_xxxxxxxx/` 目录,从中恢复四类内容:模型参数、优化器状态(含 Adam 的 momentum 与 variance)、学习率调度器状态、已完成迭代数(防止重复训练)。
- **性能数据(原文)**:
  - `--save-interval 500`: 每 500 步保存一次(原文示例值)。
  - `load-checkpoint` 时间(原文日志): `(min, max) time across ranks: load-checkpoint: (9289.88, 9288.22)` —— 即在所有 rank 上,加载检查点耗时最小约 9288.22、最大约 9289.88(单位原文未注明,通常为秒级或毫秒级 log 字段,此处仅按原文数字如实呈现)。
- **典型日志**: `successfully loaded checkpoint from xx at iteration x`,其中 `xx` 为路径、`x` 为恢复到的迭代号。

---

## 【表格解读】

### 表 1: 续训前置参数(Prerequisites)

| Parameter | Description |
|---|---|
| `--use-distributed-optimizer` | This Parameter must be enabled. This saves the optimizer state across data parallel ranks in a distributed manner, which makes later restoration easier. |
| `--finetune` | ❌ Do not set this option. Otherwise, the system skips loading the optimizer state. |
| `--no-load-optim` | ❌ Do not set this option. Otherwise, the system does not restore the optimizer state, such as the learning rate and momentum. |
| `--no-load-rng` | ❌ Do not set this option. Otherwise, the system does not restore the random state. |

逐行解读:
- 第 1 行 `--use-distributed-optimizer`: 续训的"必选项",必须开启,作用是将优化器状态按 DP 维度分布式保存,从而使后续能从检查点恢复优化器状态。
- 第 2 行 `--finetune`: 续训场景下的"禁用项",原文用 ❌ 标注;若设置,系统会跳过加载优化器状态,等同于把加载行为退化为纯微调加载。
- 第 3 行 `--no-load-optim`: 续训场景下的"禁用项";若设置,Adam 的 learning rate、momentum 等优化器内部状态不会恢复。
- 第 4 行 `--no-load-rng`: 续训场景下的"禁用项";若设置,随机数生成器状态不恢复,可能引入 dropout、数据 shuffle 等随机性的非确定性差异。

原文补充警示: 上述三项 `--finetune` / `--no-load-optim` / `--no-load-rng` 任一被设置,都会让系统无法"真正续训"。

### 表 2: 保存阶段的关键参数

| Parameter | Description |
|---|---|
| `--use-distributed-optimizer` | This parameter must be enabled. This saves the optimizer state across data parallel ranks in a distributed manner, which makes later restoration easier. |
| `--no-save-optim` | ❌ Do not set this option. Otherwise, the system does not save the optimizer state, such as the learning rate and momentum. |
| `--no-save-rng` | ❌ Do not set this option. Otherwise, the system does not save the random state. |

逐行解读:
- 第 1 行 `--use-distributed-optimizer`: 与表 1 一致,是保存阶段的"必选项",决定优化器状态的落盘形态(分布式)。
- 第 2 行 `--no-save-optim`: 保存阶段的"禁用项";若设置,优化器状态不会被保存,后续即使启用 `--load` 也无法恢复 learning rate / momentum。
- 第 3 行 `--no-save-rng`: 保存阶段的"禁用项";若设置,随机状态不会落盘,恢复后随机行为无法完全复现。

注意: 表 2 没有 `--finetune` 项,因为 `--finetune` 主要影响"加载"语义,不影响"保存"语义。

---

## 【公式解读】

原文无公式(无 LaTeX 或伪代码形式的数学表达式)。文档核心是参数配置与目录结构描述,未涉及任何公式推导。

---

## 【关联】

原文未提供内部链接(内部链接字段标注为"无")。基于文档内容可识别的相关要素如下:

- **脚本入口**: 文档以 `pretrain_gpt.py` 作为示例启动脚本,说明该特性面向 GPT 类预训练任务,属于 Megatron-Core(mcore) 训练流程。
- **依赖特性**: `--use-distributed-optimizer`(分布式优化器)是续训能力的"前置依赖",文档反复强调必须开启;该特性本身应属 mindspeed-llm 中优化器模块的一部分(原文未给出其独立文档链接)。
- **互补特性**: 与"检查点保存/加载"相关的 feature(如 `model_optim_rng.pt`、`distrib_optim.pt` 的具体 schema)在原文中未单独列出,但表明本特性建立在 Megatron-Core 的 checkpointing 子系统之上。
- **配套约束**: 使用约束中提到的 TP/DP 并行策略一致性,表明本特性与 `tensor_model_parallel_size`、`pipeline_model_parallel_size` 等并行配置项强耦合(原文未展开)。

---

## 【使用方法】

### 启动前参数配置(续训前置条件)
- `--use-distributed-optimizer`: **必须启用**。
- `--finetune`: **不要设置**。
- `--no-load-optim`: **不要设置**。
- `--no-load-rng`: **不要设置**。

### 保存检查点
```bash
--save /your/checkpoint/path \
--save-interval 500   # Save every 500 steps.
```
- 保存路径: `--save $SAVE_PATH`。
- 保存间隔: `--save-interval`(原文示例值为 500 步)。
- 保存阶段额外禁用项: `--no-save-optim`、`--no-save-rng` 均**不要设置**。
- 每次保存产出(原文目录结构):
  ```
  /your/checkpoint/path/
  |-- latest_checkpointed_iteration.txt
  |-- iter_0000001/
  |   |-- mp_rank_00_000
  |   |   |-- distrib_optim.pt
  |   |   |-- model_optim_rng.pt
  |   |-- ...
  |-- iter_0000500/
      |-- ...
  ```

### 加载以恢复训练
```bash
--use-distributed-optimizer \  # Use the distributed optimizer. Required.

...

torchrun ${DISTRIBUTED_ARGS} pretrain_gpt.py \
    [other parameters...] \
    --load $CHECKPOINT_PATH \
```
- `--load $CHECKPOINT_PATH`: 指向之前的保存根路径(即含 `latest_checkpointed_iteration.txt` 的目录)。
- 系统行为: 自动读取 `latest_checkpointed_iteration.txt` → 找到最新 iteration → 恢复模型参数、优化器状态(Adam momentum 与 variance)、学习率调度器状态、已完成迭代数。

### 验证恢复结果
恢复成功时打印日志(原文示例):
```
successfully loaded checkpoint from xx at iteration x
(min, max) time across ranks:
load-checkpoint ....................:(9289.88, 9288.22)
```

### 使用约束(原文 Usage Constraints)
1. **文件完整性**: 确保 `$CHECKPOINT_PATH` 下检查点文件完整未损坏。
2. **训练配置一致性**: batch size、模型结构、训练迭代数、优化器类型等需与保存时一致。
3. **分布式环境匹配**: NPU 数量与 TP/DP 等并行策略需保持不变,否则加载会失败。
