# INDUCTOR_ASCEND_ENABLE_COSTMODEL

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/costmodel/INDUCTOR_ASCEND_ENABLE_COSTMODEL.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/costmodel/INDUCTOR_ASCEND_ENABLE_COSTMODEL.md

【定位】
本文档描述 `INDUCTOR_ASCEND_ENABLE_COSTMODEL` 这一环境变量所控制的 Inductor-Ascend CostModel 预筛选能力——在 Triton 后端 precompile 之前，利用 Triton-Ascend 的 CostModel 对候选 config 进行耗时预测并据此重排/筛选，从而削减后续编译与实测 profiling 的开销。

【技术要点】
1. **控制对象**：Inductor-Ascend 的 CostModel 预筛选功能（默认关闭）。
2. **默认值**：未设置、`0`、`false`、`no` 均视为关闭。
3. **开启值**：`1`、`true`、`yes` 启用预筛选。
4. **作用阶段**：Triton 后端 precompile 之前；为每个候选 config 生成 TTIR 并送入 Triton-Ascend 的 CostModel 后端预测耗时。
5. **作用结果**：依据预测耗时重排并筛选候选 config，减少后续编译与实测 profiling 的数量。
6. **边界条件**：仅在候选 config 数量 > 1 时生效；config 数量 ≤ 1 时不会调用 CostModel；CostModel 后端不可用、返回异常或无有效预测时静默跳过，使用原始 config 集合。
7. **依赖前提**：需环境中已安装带有 CostModel 后端的 Triton-Ascend 包。
8. **最终决定权**：CostModel 仅作预筛选，最终可用 config 仍以 precompile 与后续 autotune 结果为准。

【关键机制与数据】
**工作原理（原文未给出具体性能数据，仅描述流程）**：

候选 config 集合 ──►（开启本特性时）为每个 config 生成 TTIR ──► 调用 Triton-Ascend CostModel 后端预测耗时 ──► 按预测耗时重排/筛选 config ──► 进入 Triton 后端 precompile 与后续实测 profiling ──► autotune 选出最终 config。

**关键约束（原文直引）**：
- "该功能仅影响Triton后端存在多个候选config的场景。config数量小于等于1时不会调用CostModel。"
- "CostModel用于预筛选config，不替代后续编译和实测profiling。"
- "如果CostModel后端不可用、返回结果异常或没有有效预测结果，会跳过CostModel预筛选，继续使用原始config集合。"

原文未给出耗时节省比例、预测准确率、config 缩减比例等量化数据。

【表格解读】

| 值 | 说明 |
|---|---|
| 未设置、0、false、no | 关闭CostModel预筛选（默认值） |
| 1、true、yes | 开启CostModel预筛选 |

**逐行解读**：
- **第一行**：列出关闭 CostModel 预筛选的多种等价写法（环境变量未设置、或显式设为 `0`/`false`/`no`），并明确这是默认行为；含义上覆盖了"未显式开启"的全部常规表达，便于在不同 shell / 配置风格下统一识别。
- **第二行**：列出开启 CostModel 预筛选的等价写法（`1`/`true`/`yes`），与第一行构成完整的二值开关语义；任何一种写法都会触发文档所述的"生成 TTIR → CostModel 预测 → 重排/筛选 config"流程。

【公式解读】
原文无公式。

【关联】
- **与 Triton 后端的关系**：本特性作用于 Triton 后端 precompile 之前，仅在 Triton 后端存在多个候选 config 时才介入；与其它后端（如 Inductor 其它 codegen 后端）的联动方式原文未涉及。
- **与 Triton-Ascend CostModel 后端的关系**：本特性依赖 Triton-Ascend 包内嵌的 CostModel 后端提供耗时预测能力，是功能启用与运行的前置依赖；CostModel 后端异常时本特性静默降级。
- **与 precompile / autotune 的上下游关系**：本特性位于 precompile 之前的预筛选环节，输出被压缩后的候选 config 集合；该集合进入后续 precompile 与实测 profiling，最终可用 config 由 autotune 决定——即 CostModel 仅影响候选池，不决定最终选型。
- **与中间表示 TTIR 的关系**：候选 config 在送入 CostModel 前需先生成 TTIR，说明 CostModel 接收的输入形式是 Triton-IR 级别的中间表示，而非高层 config 描述。
- **与硬件平台的关系**：文档明确支持型号为 "Atlas A5 系列产品"，其它昇腾型号是否可用原文未涉及。
- 内部链接：原文未提供任何内部链接。

【使用方法】
通过环境变量启用：

```shell
export INDUCTOR_ASCEND_ENABLE_COSTMODEL=1
```

可接受值：`1` / `true` / `yes`（开启），以及 `0` / `false` / `no` / 不设置（关闭，默认）。启用前需确认环境中已安装包含 CostModel 后端的 Triton-Ascend 包，且运行场景为 Triton 后端存在多个候选 config。
