# 计算通信并行 CoC (Communication Over Computation)

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/mcore/communication-over-computation.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/mcore/communication-over-computation.md

# 计算通信并行 CoC (Communication Over Computation) — 一体化深度解读

---

## 【定位】

这篇文档解决**昇腾LLM分布式训练中 ColumnParallelLinear / RowParallelLinear 内"计算–通信"串行依赖导致的硬件空闲等待问题**，并提供两种使能方式（Python脚本切分张量、融合大Kernel）在训练场景下实现**计算与通信的流水化掩盖**。

---

## 【技术要点】

1. **问题的根源**：在张量并行（TP）的 ColumnParallelLinear / RowParallelLinear 前向与反向中，Matmul（计算）与 AllReduce（不开启序列并行）/ AllGather+ReduceScatter（开启序列并行）**存在位置毗邻 + 顺序依赖**（后一步的输入是前一步输出），二者被串行执行时，计算流与通信流各自存在空闲气泡，吞吐未最大化。

2. **方案一 — Python脚本侧切分**：将张量沿 Matmul 左矩阵的 m 轴进一步切分为 **2 / 4 / 8 份**，使每个子 tensor 的"计算子任务"和"通信子任务"在 Python 侧流水线交织，从而增大两条流水线的利用率。

3. **方案二 — 融合大Kernel**：基于**昇腾 MTE 远端内存访问**能力，将计算与通信在**单个算子内部**拆为更细粒度的子任务进行流水掩盖，属于算子级融合实现。

4. **支持的通信场景与顺序灵活性**：覆盖 **ALL_REDUCE、ALL_GATHER、REDUCE_SCATTER** 三种通信原语，并支持**灵活设置"先通信或先计算"**的顺序。

5. **融合算子矩阵**：已支持 `MATMUL_ALL_REDUCE`、`MATMUL_REDUCE_SCATTER`（均为"先计算后通信"）及其**确定性计算版本**；`ALL_GATHER_MATMUL`、`ALL_GATHER_MATMUL_V2`（均为"先通信后计算"，V2 版支持获取 AllGather 中间结果）。

6. **量化融合**：在 fp16 格式下，`MATMUL_ALL_REDUCE` 支持 **w8A16 伪量化**，粒度为 **per tensor / per channel / per group**。

7. **约束与硬件兼容**：脚本侧切分要求 Matmul 左矩阵的 m 轴长度必须为切分数（2/4/8）的**倍数**，且在切分数量较大时容易出现 **host bound** 问题，对耗时差异大的片段不适用；融合算子目前**仅支持 TP=8**；**不兼容 `--use-ascend-mc2`**，**暂未适配 MoE 模型**；**Atlas A2 / A3 训练系列产品完全支持**，**Ascend 950 系列产品不支持融合算子**。

---

## 【关键机制与数据】

**整体机制（原文："问题分析"节）**：

- 在 LLM 训练中，张量并行层（ColumnParallelLinear、RowParallelLinear）的**前向与反向**天然形成"计算—通信"成对结构：
  - 计算端：Matmul；
  - 通信端：不开序列并行时为 AllReduce，开启序列并行时为 AllGather 与 ReduceScatter。
- 这两类操作**位置毗邻**，且因**顺序依赖**（后一步输入 = 前一步输出）被强制串行，从而在硬件执行时间线上同时出现"计算空闲、通信等待"的空隙。

**方案一机制（原文："Python脚本侧实现"节）**：

- 由用户层 Python 脚本按 **2 / 4 / 8** 份对张量进一步切分；
- 在子张量粒度上**交叠**发起计算子任务与通信子任务（顺序可配置：先通信或先计算）；
- **数据流要点**：m 轴必须可被切分数整除 → 张量被切分 → 各子片独立进入 Matmul + 集合通信流水；
- **收益边界（原文）**：在"计算片段与通信片段耗时相近"时收益最明显；切分数较大或二者耗时差异大时易出现 host bound，得不到预期加速。

**方案二机制（原文："融合算子实现"节）**：

- 利用**昇腾 MTE（Memory Transfer Engine）远端内存访问**能力，将原本跨两个算子（Matmul + 集合通信）的执行流程**融合到一个大 Kernel 内部**；
- 在算子内部按细粒度子任务方式切分计算与通信，实现二者的时间线重叠；
- **数据流要点**：通信原语不再作为独立算子出现，而是内嵌于 Matmul 算子的执行流中（先计算后通信 / 先通信后计算两种顺序各有对应算子）。

**性能/收益说明**：原文**未给出**具体的加速比、吞吐提升百分比或端到端训练 step 耗时对比数据；亦未提供 m 轴切分数对 host bound 影响的量化阈值。**原文无性能数据。**

---

## 【表格解读】

**原文无表格**。

---

## 【公式解读】

**原文无公式**（无 LaTeX 或伪代码形式的数学表达式）。

---

## 【关联】

- **`--use-ascend-mc2` 特性**：文中明确指出 CoC **暂不兼容** `--use-ascend-mc2`，二者为互斥关系（用户需在脚本中选择其一）。

- **序列并行（Sequence Parallelism）**：原文在通信端区分了"不开启序列并行时通信为 AllReduce"、"开启序列并行时通信为 AllGather 和 ReduceScatter"，表明 CoC 的通信覆盖能力与 Megatron 风格的序列并行开关**正交但联动**：无论是否开启 SP，CoC 都能找到对应的通信原语做流水化。

- **量化路径**：在 fp16 + w8A16 伪量化场景中，CoC 通过 `MATMUL_ALL_REDUCE` 融合算子提供支持，意味着该特性会与**权重伪量化训练**管线在算子级别耦合（粒度 per tensor / per channel / per group）。

- **ATB / CANN 依赖**：融合算子路径依赖 **ATB（Ascend Tensor Boost）**，需先安装 **CANN-NNAL** 包并 `source /usr/local/Ascend/nnal/atb/set_env.sh`；HDK 与 CANN 的版本门槛分别为 **2024 RC2 之后** 与 **2024 RC4 之后**。

- **Atlas 硬件矩阵**：**Atlas A2 / A3 训练系列产品**完整支持 CoC（含融合算子），**Ascend 950 系列产品**仅支持 Python 脚本路径，**不支持融合算子**。

- **MoE 模型**：原文明确"**当前暂未适配 MoE 模型**"，是 CoC 的功能边界之一。

- **Megatron-Core 张量并行结构（ColumnParallelLinear / RowParallelLinear）**：CoC 的优化目标即这两种 TP 层，定位为 Megatron-Core 路径下 mcore 通信–计算流水的本地增强。

---

## 【使用方法】

### 入口开关

启用 CoC 的总开关为 **`--use-ascend-coc`**；其后通过附加参数在"Python脚本实现"与"融合算子实现"二者中**择一**使用。

### 场景一：通过 Python 脚本使能

在训练脚本中添加：

```text
    --use-ascend-coc \
    --coc-parallel-num 2   # 取值可为 2 / 4 / 8
```

- **`--coc-parallel-num`**：指定 Matmul 左矩阵 m 轴的切分数，可设为 **2、4 或 8**。
- 限制：m 轴长度必须是该切分数的倍数；切分数较大或计算/通信耗时差距大时可能 host bound。

### 场景二：通过融合算子使能

**前置依赖**：必须先安装 **ATB**：

- 安装 **CANN-NNAL** 包之后，执行 `source /usr/local/Ascend/nnal/atb/set_env.sh`。

在训练脚本中添加：

```text
    --use-ascend-coc \
    --coc-fused-kernel      # 注意：当前只支持 TP=8 的场景
```

### 参数优先级规则

当 **`--coc-parallel-num > 1`** 与 **`--coc-fused-kernel`** 同时出现时，**`--coc-fused-kernel` 优先级更高**，会覆盖 `--coc-parallel-num > 1` 的设置。

### 版本与硬件要求（原文）

- **HDK**：**2024 RC2 之后**版本；
- **CANN**：**2024 RC4 之后**版本；
- **Atlas A2 训练系列产品 / Atlas A3 训练系列产品**：完全支持；
- **Ascend 950 系列产品**：不支持融合算子（仅可走 Python 脚本路径）；
- **不兼容** `--use-ascend-mc2`；**暂未适配 MoE 模型**。
