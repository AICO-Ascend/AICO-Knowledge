# Ascend MC2

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/mc2.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/mc2.md

# Ascend MC2 文档一体化深度解读

## 【定位】

本篇文档阐述 MindSpeed LLM 框架中 **Ascend MC2 特性**——一种针对 LLM 训练中 Matmul 计算与集合通信算子强依赖场景，通过算子融合（operator fusion）+ 流水（pipeline）实现通信-计算重叠的优化方案，用以降低显存开销并提升计算效率。

---

## 【技术要点】

1. **依赖环境**：仅支持 `CANN 8.0.RC2`、`Ascend HDK 24.1.RC2` 或后续版本；低版本运行可能异常（原文："behave abnormally, including runtime errors"）。
2. **默认开关**：MC2 在 MindSpeed LLM 中**默认禁用**；启用方式是在 `mindspeed_llm/training/arguments.py` 的 `validate_args_decorator` 函数中**注释掉** `args.use_ascend_mc2 = False`。
3. **触发场景**：仅在同时启用 **Tensor Parallelism (TP) + Sequence Parallelism (SP)** 时推荐开启；纯 TP（SP 关）场景下解决 Matmul↔AllReduce 强依赖，TP+SP 场景下解决 Matmul↔AllGather / ReduceScatter 强依赖。
4. **核心机制**：算子融合 + 任务切分 + 流水调度——将大块计算/通信任务拆分为更小的"计算子任务"与"通信子任务"，通过 pipeline 让二者重叠（"reduces waiting and idle time and improves utilization"）。
5. **接入接口**：Python 侧通过 MC2 operator interface 融合原顺序执行的 Matmul 与 AllGather/ReduceScatter；底层算子为 `torch_npu.npu_mm_all_reduce_base`。
6. **边界与局限**：在 MCore 场景下，若启用 `--use-mcore-models`，**MoE 模型的 MLP 部分不会启用 MC2**（原文："the MLP part of MoE models does not enable MC2"）；且官方警示"**Enabling MC2 may affect accuracy for some models**"。

---

## 【关键机制与数据】

**工作原理（原文 Issue Analysis + Solution 段）**：
- 在 LLM 训练启用 TP/SP 时，Matmul 与集合通信（SP 关：AllReduce；SP 开：AllGather/ReduceScatter）之间存在**强数据依赖**；当模型参数规模大时，"both communication and computation are heavy here"。
- 顺序执行（sequential）模式下，前后依赖导致通信-计算串行化，产生 **long waiting and idle time**（长等待与空闲）。
- MC2 方案：使用**算子融合**（operator fusion）把 Matmul 与集合通信合并；将大任务**切分**为更小的计算子任务与通信子任务；通过 **pipeline** 让通信与计算子任务**重叠**执行，从而压缩空泡、提升利用率。

**数据流（原文 Approach 段）**：
- 入口：`mindspeed/core/tensor_parallel/ascend_turbo/mc2_linears_seq_parallel.py`（代码实现入口，指向 `core_r0.8.0` 分支）。
- 落点算子：`torch_npu.npu_mm_all_reduce_base`（昇腾 PyTorch 适配层提供的 Matmul+AllReduce 融合基础算子）。

**性能/效果（原文 Effects 段，原文未给出量化数字）**：
- 原文只定性描述："MC2 can **reduce memory overhead** and **improve computation efficiency**"——未提供具体百分比/加速比等量化数据。

---

## 【表格解读】

原文无表格（全文未出现任何参数表、性能对比表或配置项表格）。

---

## 【公式解读】

原文无公式（未出现任何 LaTeX 公式或伪代码形式表达式）。

---

## 【关联】

文中提到的关联模块/特性/上下游：

- **TP（Tensor Parallelism，张量并行）**：MC2 的前置依赖条件之一，文档中反复强调"TP and SP enabled"为推荐触发场景。
- **SP（Sequence Parallelism，序列并行）**：MC2 的另一前置依赖；SP 关时通信为 AllReduce，SP 开时通信为 AllGather/ReduceScatter——MC2 需要适配这两种不同通信模式。
- **MCore（Megatron-Core 模型路径）**：通过 `--use-mcore-models` 启用；MC2 在该路径下有一个明确边界——**MoE 模型的 MLP 部分不会启用 MC2**。
- **MoE 模型**：与 MCore 路径联动，MLP 层在 MCore + MC2 共存时被排除。
- **底层算子接口 `torch_npu.npu_mm_all_reduce_base`**：MC2 的硬件适配落点，定义在 `ptaoplist_000449.html` 文档。
- **框架开关 `args.use_ascend_mc2`**：位于 `mindspeed_llm/training/arguments.py` 的 `validate_args_decorator`，是全局 Feature 开关。

文末内部链接：**(无)**——文档中给出的 `gitcode.com/...` 与 `hiascend.com/...` 均为**外链**（代码仓子模块链接与昇腾官方 API 文档），并未指向本仓其他 feature 文档。

---

## 【使用方法】

原文涉及两类启用方式：

1. **代码层开关（取消禁用）**：在 `mindspeed_llm/training/arguments.py` 的 `validate_args_decorator` 函数中，注释掉 `args.use_ascend_mc2 = False` 这一行。

2. **命令行开关**：设置 `--use-ascend-mc2` 以启用 MC2 算子（原文："Set `--use-ascend-mc2` to enable the MC2 operator."）。

原文未给出具体的配置文件路径、环境变量、超参（如切分粒度、pipeline stage 数等）——这些细节需到 `mindspeed/core/tensor_parallel/ascend_turbo/mc2_linears_seq_parallel.py` 代码实现中查阅。
