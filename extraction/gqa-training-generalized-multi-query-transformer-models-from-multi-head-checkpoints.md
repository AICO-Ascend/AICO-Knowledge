---
paper_num: "39"
title: "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints"
authors: "Multi-Head Checkpoints Joshua Ainslie∗, James Lee-Thorp∗, Michiel de Jong∗† Yury Zemlyanskiy, Federico Lebrón, Sumit Sanghai Google Research"
date: "2026/1/7"
arxiv: "https://arxiv.org/abs/2305.13245"
pdf: "papers/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints.pdf"
slug: "gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints"
tags: [training]
---

# GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints

> [!abstract] 摘要（原文）
> 1\. 🧐 Transformer解码器推理因加载注意力键值而存在内存带宽瓶颈，Multi-Query Attention (MQA) 能缓解此问题但常导致质量下降。 2. 🚀 本文提出一种通过少量计算将现有Multi-Head Attention (MHA) 模型“uptrain”为MQA模型的方案，并引入了Grouped-Query Attention (GQA)，作为MHA和MQA之间的中间形式。 3. ✨ 实验表明，经过“uptrain”的GQA模型在保持接近MHA质量的同时，实现了与MQA相当的推理速度，提供了更优的性能-效率权衡。

## 元信息
- **发表日期**: 2026/1/7
- **作者**: Multi-Head Checkpoints Joshua Ainslie∗, James Lee-Thorp∗, Michiel de Jong∗† Yury Zemlyanskiy, Federico Lebrón, Sumit Sanghai Google Research
- **arXiv**: https://arxiv.org/abs/2305.13245
- **本地 PDF**: `papers/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints.pdf`
- **页数**: 7

## 图表（原文 caption + 页码）

### Figure 1 (p.1)
![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p01.png]]
> [!quote] caption
> Overview of conversion from multi-head to multi-query attention. Key and value projection matri- ces from all heads are mean pooled into a single head.

### Figure 2 (p.2)
![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p02.png]]
> [!quote] caption
> Overview of grouped-query method. Multi-head attention has H query, key, and value heads. Multi-query attention shares single key and value heads across all query heads. Grouped-query attention instead shares single key and value heads for each group of query heads, interpolating between multi-head and multi-query attention. a small proportion α of its original training steps on the same pre-train

### Figure 3 (p.3)
![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p03.png]]
> [!quote] caption
> Uptrained MQA yields a favorable tradeoff compared to MHA with higher quality and faster speed than MHA-Large, and GQA achieves even better performance with similar speed gains and comparable quality to MHA-XXL. Average perfor- mance on all tasks as a function of average inference time per sample for T5-Large and T5-XXL with multi- head attention, and 5% uptrained T5-XXL with MQA and GQA-8 attenti

### Figure 4 (p.4)
![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]]
> [!quote] caption
> Performance comparison of different check- point conversion methods for T5-Large uptrained to MQA with proportion α = 0.05. ‘Mean’ mean-pools key and value heads, ‘First’ selects the first head and ‘Random’ initializes heads from scratch. be useful. Both MQA and GQA gain from 5% uptraining with diminishing returns from 10%. 0

### Figure 5 (p.4)
![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]]
> [!quote] caption
> Performance as a function of uptraining pro- portion for T5 XXL models with MQA and GQA-8.

### Figure 6 (p.4)
![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]]
> [!quote] caption
> Time per sample for GQA-XXL as a function of the number of GQA groups with input length 2048 and output length 512. Going from 1 (MQA) to 8 groups adds modest inference overhead, with increasing cost to adding more groups. is especially helpful for long inputs (Pope et al., 2022; de Jong et al., 2022). Rabe (2023) indepen- dently developed GQA with public implementa- tion. Other works have explore

## 全文文本
全文已存 `extraction/fulltext/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints.txt`（23726 字符）供引用检索。