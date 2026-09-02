# Ascend MC2

> 仓 `mindspeed` · 路径 `docs/zh/features/mc2.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/mc2.md

# Ascend MC2 文档深度解读

## 【定位】

本文档描述了昇腾自研 MC2 融合算子在 MindSpeed 中的集成方案：通过将大模型训练中 Tensor Parallel（TP）与 Sequence Parallel（SP）场景下存在强依赖关系的 `matmul` 计算与集合通信（`all-reduce` / `all_gather` / `reduce_scatter`）融合为单一算子，以流水掩盖方式降低串行等待开销、提升整体利用率。

## 【技术要点】

- **适用版本限制**：仅支持 CANN 8.0.RC2 与 Ascend HDK 24.1.RC2 及其后续迭代版本，原文明确警告非指定版本可能触发运行时错误等系统级异常。
- **问题域定位**：针对「TP+SP 开启」场景中 `matmul` 与集合通信之间的强依赖；当模型参数量较大时，通信量与计算量都很高，串行执行引入显著等待闲置时间。
- **融合机制**：MC2 通过「融合算子」将 `matmul` 与集合通信融合，把大任务切分为较小的「计算子任务」与「通信子任务」，并以流水方式使二者相互掩盖。
- **Python 侧改造点**：MindSpeed 在 Python 脚本层将原本串行的 `matmul` 与 `all_gather` / `reduce_scatter` 调用，通过 MC2 融合算子接口替换为一次融合调用。
- **底层算子接口**：调用昇腾官方 `mc2_operators_api`，并非 MindSpeed 自研算子。
- **权重冻结兼容**：同时支持「权重冻结」与「权重不冻结」两种场景，前者通过 `requires_grad=False` 实现，原文给出两种冻结粒度的示例代码。
- **启用方式**：仅需 CLI 开关 `--use-ascend-mc2`，但前提必须同时开启 `--sequence-parallel`。
- **显式不兼容项**：(1) MoE 模型不支持；(2) 不兼容 `--use-ascend-coc`（计算通信并行 CoC 特性）；(3) 不支持 Atlas 900 A3 硬件。

## 【关键机制与数据】

- **原文（背景）**：在「开启 TP 但不开启 SP」时，呈现 `matmul` 与 `all-reduce` 的强依赖；在「TP+SP 同时开启」时，呈现 `matmul` 与 `all_gather` / `reduce_scatter` 的强依赖。
- **原文（机制）**：MC2 不是简单地把两个算子合并成一个更大的算子一次性执行，而是「将较大的计算和通信任务切分成了较小的计算子任务和通信子任务」，通过子任务级的流水实现通信与计算的互相掩盖（overlap）。
- **原文（实现位置）**：具体 Python 侧实现见 `mindspeed/core/tensor_parallel/ascend_turbo/mc2_linears_seq_parallel.py`；底层算子走昇腾 `mc2_operators_api`。
- **原文（效果）**：在开启 TP+SP 的训练场景下，使用 MC2「可以减少内存开销并提高计算效率」。原文未给出具体百分比、加速比、显存节省数值等量化指标。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。文中以「`matmul` 计算与集合通信操作的融合」+「任务切分 + 流水掩盖」的自然语言描述说明机制，未给出任何数学表达式或伪代码公式。

## 【关联】

- **直接关联的实现模块**：内部链接指向 `../../../mindspeed/core/tensor_parallel/ascend_turbo/mc2_linears_seq_parallel.py`，这是 MindSpeed 在 Python 层将串行 `matmul` 与 `all_gather` / `reduce_scatter` 改写为 MC2 融合算子调用的具体实现位置，路径前缀 `ascend_turbo` 暗示该能力属于「昇腾 Turbo 加速套件」中的张量并行子模块。
- **依赖的底层算子**：MC2 算子本身由昇腾提供，文档外链 `mc2_operators_api`（`https://www.hiascend.com/document/detail/zh/Pytorch/60RC1/apiref/apilist/ptaoplist_000449.html`），MindSpeed 只做上层封装与开关控制。
- **互斥特性**：与 `--use-ascend-coc`（CoC 计算通信并行特性）不兼容，二者只能选其一；同时 MoE 路径未适配 MC2。
- **上游依赖**：依赖 TP（Tensor Parallel）与 SP（Sequence Parallel）的开启，文档反复强调「**同时需要确保开启**`--sequence-parallel`」。
- **适配的模型层**：示例代码引用 `megatron.core.tensor_parallel.layers.ColumnParallelLinear` 与 `RowParallelLinear`，表明其替换对象是 Megatron 风格 TP 线性层（典型为 LLM 的 QKV/FFN 投影）。
- **硬件/软件边界**：仅在指定版本的 CANN + HDK 上验证；硬件上排除 Atlas 900 A3。

## 【使用方法】

- **启用开关**：在训练命令中添加 `--use-ascend-mc2`。
- **强前置条件**：必须同时开启 `--sequence-parallel`（原文使用加粗强调「**同时需要确保开启**`--sequence-parallel`」）。
- **环境要求**：CANN 8.0.RC2 及以上、Ascend HDK 24.1.RC2 及以上；硬件不支持 Atlas 900 A3。
- **权重冻结（可选）**：
  - 全部冻结：`for param in model.parameters(): param.requires_grad = False`
  - 选择性冻结：除 `output_layer` 外，遍历 `ColumnParallelLinear` 与 `RowParallelLinear`，将其所有参数设为 `requires_grad=False`。
- **已知不兼容**：MoE 模型；`--use-ascend-coc`。
