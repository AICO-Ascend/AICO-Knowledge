# 非对齐PP和VPP切分

> 仓 `mindspeed` · 路径 `docs/zh/features/unaligned-pipeline.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/unaligned-pipeline.md

# 「非对齐PP和VPP切分」Feature 文档深度解读

## 【定位】

这篇文档针对类Megatron-LM大模型训练中PP（流水并行）与VPP（虚拟流水并行）范式下因嵌入层、对数几率层、多token预测等模块带来的计算不均衡问题，介绍了一种允许用户在每个PP层/VPP层上**非等量**分配transformer layer层数、以动态平衡流水线计算负载的机制。

---

## 【技术要点】

1. **核心机制**：通过参数 `--pipeline-num-transformer-layers` 显式指定每个PP阶段中各VPP阶段的transformer layer层数，使各流水线阶段的计算量不再强制相等。
2. **参数表达形式**：使用**二维矩阵**表示——第一维（纵轴/行）表示 pp_rank，第二维（横轴/列）表示 vpp_rank；元素值即为该 (pp_rank, vpp_rank) 处的transformer层数。
3. **总层数约束**：矩阵中所有元素之和必须与 `--num-layers` 保持一致（原文注意事项第1条）。
4. **VPP等切默认行为**：框架默认VPP仍按等切处理，因此单个PP阶段内的总层数必须能被 `--num-layers-per-virtual-pipeline-stage` 整除（原文注意事项第2条）。
5. **无VPP场景**：可使用一维列表表达，仅按pp_rank分配层数。
6. **性能目标**：通过消除/减少流水线"空泡"（bubble），提升系统吞吐量与硬件资源利用率。

---

## 【关键机制与数据】

**工作原理**：
- 传统PP/VPP默认按 transformer layer 总数 `--num-layers` 在各阶段间**等分**，忽略了 Embedding Layer、Logits Layer、Multi-Token Prediction 等辅助模块引入的额外计算开销。
- 引入非对齐切分后，可将**更多**transformer layer 分配到不含/少含这些重计算模块的PP阶段，从而让所有阶段的"transformer + 辅助模块"总耗时趋于均衡。
- 文档通过 2D 矩阵直接控制每个 (pp_rank, vpp_rank) 的层数，与底层调度对接。

**原文给出的示例**（非性能数字，而是结构示例）：
- `pipeline_num_transformer_layers = [[0,1],[1,1]*4,[1,0]]`，pp_rank=0，vpp_rank=1 → 该位置有 **1 层** layer。
- `pipeline_num_transformer_layers = [[1],[2]*4,[1]]`（无VPP场景），pp_rank=1 → 该位置有 **2 层** layer。

**性能数据**：原文仅以"预期能够显著减少流水线中的空泡现象"做定性描述，未给出具体的加速比、空泡比例、吞吐量提升等量化数字（原文未涉及具体性能数据）。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档涉及以下上下游模块与并行概念（依据文末内部链接信息为"无"，以下关联均来自原文上下文）：

- **PP（Pipeline Parallelism，流水并行）**：本文切分的主体维度之一，由参数中的第一维（pp_rank）控制。
- **VPP（Virtual Pipeline Parallelism，虚拟流水并行）**：本文切分的另一维度，由参数中的第二维（vpp_rank）控制，受 `--num-layers-per-virtual-pipeline-stage` 约束。
- **嵌入层（Embedding Layer）**：被列为引发不均衡的因素之一，非对齐切分通过调整 transformer 层分布间接补偿其开销。
- **对数几率层（Logits Layer）**：同样为不均衡来源，被包含在切分考量中。
- **多token预测（Multi-Token Prediction, MTP）**：原文提到的另一个末端重计算模块。
- **上游配置项**：与 `--num-layers`（总层数约束）、`--num-layers-per-virtual-pipeline-stage`（单PP阶段VPP等切粒度）共同作用。
- **流水线空泡（pipeline bubble）**：本文所要消除/缓解的直接目标现象。

---

## 【使用方法】

**命令行参数**：
- 启用开关：使用 `--pipeline-num-transformer-layers` 参数。

**参数格式**：
- 启用VPP时使用二维矩阵：`--pipeline-num-transformer-layers [[0,1],[1,1]*4,[1,0]]`
  - 第一维对应 pp_rank（行），第二维对应 vpp_rank（列）。
  - 示例中 `[1,1]*4` 表示该行重复4次（即4个PP stage各自对应同一组VPP层数）。
- 未启用VPP时使用一维列表：`--pipeline_num_transformer_layers = [[1],[2]*4,[1]]`，直接按 pp_rank 指定层数。

**约束条件**（原文注意事项）：
1. 矩阵中所有层数之和必须等于 `--num-layers`。
2. 因框架默认VPP仍按等切处理，单个PP stage的总层数须能被 `--num-layers-per-virtual-pipeline-stage` 整除；最终生效以矩阵中层数控制为准。
