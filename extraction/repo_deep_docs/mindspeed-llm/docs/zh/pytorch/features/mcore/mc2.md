# Ascend MC2

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/mcore/mc2.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/mcore/mc2.md

# Ascend MC2 深度解读

## 【定位】

本文档介绍昇腾自研的 MC2（Matmul + Collective Communication）融合算子能力，用于解决大模型训练中开启 TP（张量并行）与 SP（序列并行）后 matmul 计算与集合通信操作（all-reduce / all_gather / reduce_scatter）之间的强依赖所导致的串行等待闲置问题，通过算子融合与子任务流水化提升硬件利用率。

## 【技术要点】

1. **版本约束**：仅支持 CANN 8.0.RC2 与 Ascend HDK 24.1.RC2 及其后续迭代版本；非指定版本可能触发"系统级的异常行为"（含运行时错误）。
2. **默认开关**：MindSpeed-LLM 中 MC2 默认关闭，需在 `mindspeed_llm/training/arguments.py` 的 `validate_args_decorator` 函数中将 `args.use_ascend_mc2 = False` 注释掉才能启用。
3. **精度风险**：文档显式标注"使能 MC2 可能在部分模型带来精度问题"。
4. **融合机制**：MC2 将 matmul 计算与集合通信融合到同一算子中，并把大任务切分为较小的计算子任务和通信子任务，通过流水方式使二者互相掩盖。
5. **Python 侧实现**：通过 MC2 融合算子接口替代原本串行的 matmul 与 all_gather/reduce_scatter，代码参考 `mc2_linears_seq_parallel.py`。
6. **使用限制**：A5 机型暂不支持该特性；mcore 场景下（开启 `--use-mcore-models`）的 MoE 模型 MLP 部分不使能 MC2。

## 【关键机制与数据】

- **依赖关系识别**（原文）：
  - 开启 TP + 不开启 SP：存在 matmul 计算 ↔ all-reduce 操作的强依赖。
  - 开启 TP + SP：存在 matmul 计算 ↔ all_gather/reduce_scatter 操作的强依赖。
- **问题根因**（原文）：模型参数量较大时，该处的通信量和计算量都较大，串行执行会引入"较长的等待闲置时间"。
- **优化思路**（原文）：算子融合 + 任务切分（计算子任务 / 通信子任务）+ 子任务流水互相掩盖 → "减少等待和闲置时间，提高利用率"。
- **使用效果**（原文）："在开启 TP 和 SP 的训练场景下，使用 MC2 可以减少内存开销并提高计算效率"。
- **接口依赖**：底层调用 `torch_npu.npu_mm_all_reduce_base`（链接指向昇腾官方文档，文档版本标注为 60RC1，注意与正文 8.0.RC2 表述并存）。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

- **上游特性 / 触发条件**：TP（张量并行）与 SP（序列并行）——本文反复强调"开启了 TP 和 SP 的训练场景"为典型使用场景。
- **下游 / 冲突模块**：
  - mcore 路径（`--use-mcore-models`）下的 MoE 模型的 MLP 部分会绕过 MC2。
  - 非 mcore 路径未在文中单列。
- **代码实现层**：通过 `mindspeed/core/tensor_parallel/ascend_turbo/mc2_linears_seq_parallel.py` 替换 Python 侧原串行调用。
- **硬件 / 驱动依赖**：CANN 8.0.RC2、Ascend HDK 24.1.RC2；A5 机型不支持。
- **算子接口**：依赖 `torch_npu.npu_mm_all_reduce_base`（昇腾 torch_npu PTA 算子）。
- **内部链接**：原文无内部链接，仅提供两个外部链接（gitcode 代码实现、昇腾官方接口说明）。

## 【使用方法】

1. **修改默认开关**：将 `mindspeed_llm/training/arguments.py` 中 `validate_args_decorator` 内的 `args.use_ascend_mc2 = False` 注释掉。
2. **训练启动参数**：设置 `--use-ascend-mc2` 即可使能 MC2 算子。
3. **使用建议**：开启 TP + SP 时建议同步开启 MC2 以获得进一步优化。
4. **环境与机型门槛**：CANN ≥ 8.0.RC2、Ascend HDK ≥ 24.1.RC2；A5 机型不可用。
