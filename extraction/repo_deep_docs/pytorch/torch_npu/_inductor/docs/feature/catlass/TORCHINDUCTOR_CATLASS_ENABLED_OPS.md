# TORCHINDUCTOR_CATLASS_ENABLED_OPS （同社区TORCHINDUCTOR_CUTLASS_ENABLED_OPS）

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/catlass/TORCHINDUCTOR_CATLASS_ENABLED_OPS.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/catlass/TORCHINDUCTOR_CATLASS_ENABLED_OPS.md

# TORCHINDUCTOR_CATLASS_ENABLED_OPS 文档深度解读

## 【定位】
本文档描述 TorchNPU 中环境变量 `TORCHINDUCTOR_CATLASS_ENABLED_OPS` 的作用——它用于指定哪些矩阵乘类算子可启用 catlass 后端加速路径，并与上游 PyTorch 社区的 `TORCHINDUCTOR_CUTLASS_ENABLED_OPS` 保持同名同义映射。

## 【技术要点】
1. **变量同义性**：昇腾侧 `TORCHINDUCTOR_CATLASS_ENABLED_OPS` 与社区 `TORCHINDUCTOR_CUTLASS_ENABLED_OPS` 在语义与命名上对齐，便于跨生态代码迁移。
2. **可控算子范围**：作用于矩阵乘类的四个算子 —— `mm`、`addmm`、`bmm`、`grouped_mm`。
3. **默认启用集**：缺省值 `"mm,addmm,bmm"`（即 `grouped_mm` 不在默认开启集合内，需用户显式追加）。
4. **配置方式**：通过标准 shell 环境变量 `export` 设置，字符串以逗号分隔算子名。
5. **完整启用示例**：将 `grouped_mm` 一并开启 —— `export TORCHINDUCTOR_CATLASS_ENABLED_OPS="mm,addmm,bmm,grouped_mm"`。
6. **硬件依赖**：仅在 **Atlas A5 系列产品** 上受支持。
7. **使用约束**：原文标注"无"，即不存在额外的运行时限制说明。

## 【关键机制与数据】
- **机制**：环境变量作为 Inductor 后端调度器的白名单，命中列表中的算子会被路由到 catlass 后端执行，未命中则走默认路径。
- **默认值**：原文: 默认配置为 `TORCHINDUCTOR_CATLASS_ENABLED_OPS="mm,addmm,bmm"`，即 `grouped_mm` 默认不启用。
- **完整配置**：原文: `"mm,addmm,bmm,grouped_mm"` 表示四个算子全部开启 catlass 后端。
- **性能数据**：原文未涉及任何性能数字、加速比、吞吐量或基准测试结果。

## 【表格解读】
原文无表格。

## 【公式解读】
原文无公式。

## 【关联】
- **同名映射关系**：与 PyTorch 社区变量 `TORCHINDUCTOR_CUTLASS_ENABLED_OPS`（上游 CUTLASS 后端开关）形成一一对应，catlass 是昇腾对 CUTLASS 思路的适配实现。
- **后端归属**：变量前缀 `TORCHINDUCTOR_` 表明其作用于 `torch.compile` / Inductor 编译路径，而非 eager 模式。
- **算子作用域**：限定为矩阵乘及其带偏置变体（`addmm`）、批矩阵乘（`bmm`）、分组矩阵乘（`grouped_mm`），与 GEMM 类算子族强绑定。
- **硬件绑定**：通过 `<term>Atlas A5 系列产品</term>` 与昇腾硬件产品族绑定，非 A5 系列产品不在本文档支持范围内。
- **内部链接**：原文末尾无内部链接信息。

## 【使用方法】
- **启用命令**（原文）:
  ```shell
  export TORCHINDUCTOR_CATLASS_ENABLED_OPS="mm,addmm,bmm,grouped_mm"
  ```
- **默认行为**：不设置时按 `"mm,addmm,bmm"` 自动生效（原文给出默认配置）。
- **最小子集示例**：若仅需开启 `mm`，原文未直接给出单一算子的 export 示例，但按格式可写为 `"mm"`（原文未涉及，谨慎外推）。
- **使用约束**：原文标注"无"，未给出兼容性、版本、shape 维度等额外约束说明。
- **依赖前提**：原文未涉及，需运行在 Atlas A5 系列产品上（原文支持型号一节明确）。
