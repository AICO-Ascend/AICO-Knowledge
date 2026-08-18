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

### Figure 1 (p.1) ⭐深度解读
![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p01.png]]
> [!quote] caption
> Overview of conversion from multi-head to multi-query attention. Key and value projection matri- ces from all heads are mean pooled into a single head.

> [!tip] 技术解读（多模态）
> **Description (architecture/data flow):**
The figure illustrates the conversion of a multi-head attention (MHA) checkpoint into a multi-query attention (MQA) checkpoint. On the left, **H** independent key projection matrices (K₁, K₂, …, K_H) each map inputs of dimension d_h into d_model. These H parallel projections are aggregated through a vertical **"Mean Pool"** block (the figure caption also notes value projections undergo the same treatment), collapsing all per-head parameters into a single representative head. The pooled parameters then seed one unified **Key Projection K_MQ** block, which again outputs d_h — yielding a single shared key/value head that all query heads attend to.

**Key technical takeaway:**
Mean-pooling the H per-head key/value projection matrices into one head is a parameter-free, compute-cheap conversion step that outperforms single-head picking or random reinitialization, enabling effective MQA uptraining from existing MHA checkpoints.

**Caption (verbatim):**
"Figure 1: Overview of conversion from multi-head to multi-query attention. Key and value projection matrices from all heads are mean pooled into a single head."

### Figure 2 (p.2) ⭐深度解读
![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p02.png]]
> [!quote] caption
> Overview of grouped-query method. Multi-head attention has H query, key, and value heads. Multi-query attention shares single key and value heads across all query heads. Grouped-query attention instead shares single key and value heads for each group of query heads, interpolating between multi-head and multi-query attention. a small proportion α of its original training steps on the same pre-train

> [!tip] 技术解读（多模态）
> ## Figure Description

The figure visually compares three transformer attention variants side-by-side, each rendered as stacked rows of rectangular blocks representing **Queries** (blue, bottom), **Keys** (pink/red, middle), and **Values** (yellow/orange, top):

- **Multi-head (left):** Each query head has its own dedicated key and value head — H independent K/V projections.
- **Grouped-query (center):** Query heads are partitioned into G groups; each group shares a single key head and value head, with dashed lines indicating the pooling/mapping from queries to shared K/V.
- **Multi-query (right):** All H query heads share one single key and value head — the most aggressive sharing (the limiting case where G = 1).

**Key takeaway:** Grouped-query attention is an interpolation point between MHA (high quality, high KV-cache cost) and MQA (low cost, lower quality), allowing a tunable quality/efficiency trade-off by choosing the number of groups G.

## Caption (Verbatim)

Figure 2: Overview of grouped-query method. Multi-head attention has H query, key, and value heads. Multi-query attention shares single key and value heads across all query heads. Grouped-query attention instead shares single key and value heads for each *group* of query heads, interpolating between multi-head and multi-query attention.

### Figure 3 (p.3) ⭐深度解读
![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p03.png]]
> [!quote] caption
> Uptrained MQA yields a favorable tradeoff compared to MHA with higher quality and faster speed than MHA-Large, and GQA achieves even better performance with similar speed gains and comparable quality to MHA-XXL. Average perfor- mance on all tasks as a function of average inference time per sample for T5-Large and T5-XXL with multi- head attention, and 5% uptrained T5-XXL with MQA and GQA-8 attenti

> [!tip] 技术解读（多模态）
> # Figure 3 Description

**Architecture/Components:** A 2D scatter plot comparing four T5 model variants on a speed-vs-quality axis. X-axis: "Time per sample (ms)" (0 to ~1.5); Y-axis: "Performance" (46 to ~47.2). Four data points are plotted — **MHA-Large** (pink, lower-left, ~0.37 ms / 46.0), **MQA-XXL** (orange, ~0.24 ms / 46.6), **GQA-XXL** (blue, ~0.28 ms / 47.1), and **MHA-XXL** (pink, upper-right, ~1.51 ms / 47.2).

**Data flow / narrative:** The plot visualizes a Pareto-style tradeoff between inference speed and task-averaged quality for summarization, translation, and QA benchmarks.

**Key technical takeaway:** Even with only 5% extra pretraining, **MQA-XXL runs ~6× faster than MHA-XXL** with only ~0.6 points of quality loss, while **GQA-XXL closes nearly all of that gap** (≈47.1 vs 47.2) at comparable speed — making grouped-query attention a near-free quality upgrade over multi-query attention.

---

**Caption verbatim:**

"Figure 3: **Uptrained MQA yields a favorable tradeoff compared to MHA with higher quality and faster speed than MHA-Large, and GQA achieves even better performance with similar speed gains and comparable quality to MHA-XXL.** Average performance on all tasks as a function of average inference time per sample for T5-Large and T5-XXL with multi-head attention, and 5% uptrained T5-XXL with MQA and GQA-8 attention."

### Figure 4 (p.4) ⭐深度解读
![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]]
> [!quote] caption
> Performance comparison of different check- point conversion methods for T5-Large uptrained to MQA with proportion α = 0.05. ‘Mean’ mean-pools key and value heads, ‘First’ selects the first head and ‘Random’ initializes heads from scratch. be useful. Both MQA and GQA gain from 5% uptraining with diminishing returns from 10%. 0

> [!tip] 技术解读（多模态）
> **Figure 6 (main figure) — Architecture/Components/Data Flow:**

- **Axes:** X = number of GQA groups {1, 4, 8, 16, 32, 64} (log scale); Y = inference time per sample (s, 0–~2.5).
- **Series:** Three attention variants on GQA-XXL (input 2048, output 512):
  - **MHA** (red dotted) — constant baseline ≈ 2.5 s (single head shared across all groups as reference ceiling).
  - **MQA** (orange dotted) — constant baseline ≈ 0.5 s (1-group reference floor).
  - **GQA** (blue solid with square markers) — tunable line sweeping from 1 → 64 groups.
- **Data flow / shape:** Flat plateau from 1 to ~8 groups near the MQA floor (~0.5 s), gentle rise through 16–32 groups, then a steep ascent to ≈ 2.5 s at 64 groups, converging toward MHA.

**Key technical takeaway (≤120 words):** GQA interpolates smoothly between MQA and MHA along the *time* dimension. Going from 1 → 8 groups adds only modest inference overhead, while moving toward 64 groups rapidly approaches MHA's latency. This makes GQA-8 the chosen Pareto-sweet spot: it retains most of MQA's KV-cache / memory-bandwidth savings without the steep slowdown of finer groupings. The curve demonstrates that grouping query heads is a *contiguous*, not discrete, knob over compute–quality trade-offs in attention.

**Caption (verbatim):**
"Figure 6: Time per sample for GQA-XXL as a function of the number of GQA groups with input length 2048 and output length 512. Going from 1 (MQA) to 8 groups adds modest inference overhead, with increasing cost to adding more groups."

### Figure 5 (p.4) ⭐深度解读
![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]]
> [!quote] caption
> Performance as a function of uptraining pro- portion for T5 XXL models with MQA and GQA-8.

> [!tip] 技术解读（多模态）
> **Figure 6 (main figure) — Architecture/Components/Data Flow:**

- **Axes:** X = number of GQA groups {1, 4, 8, 16, 32, 64} (log scale); Y = inference time per sample (s, 0–~2.5).
- **Series:** Three attention variants on GQA-XXL (input 2048, output 512):
  - **MHA** (red dotted) — constant baseline ≈ 2.5 s (single head shared across all groups as reference ceiling).
  - **MQA** (orange dotted) — constant baseline ≈ 0.5 s (1-group reference floor).
  - **GQA** (blue solid with square markers) — tunable line sweeping from 1 → 64 groups.
- **Data flow / shape:** Flat plateau from 1 to ~8 groups near the MQA floor (~0.5 s), gentle rise through 16–32 groups, then a steep ascent to ≈ 2.5 s at 64 groups, converging toward MHA.

**Key technical takeaway (≤120 words):** GQA interpolates smoothly between MQA and MHA along the *time* dimension. Going from 1 → 8 groups adds only modest inference overhead, while moving toward 64 groups rapidly approaches MHA's latency. This makes GQA-8 the chosen Pareto-sweet spot: it retains most of MQA's KV-cache / memory-bandwidth savings without the steep slowdown of finer groupings. The curve demonstrates that grouping query heads is a *contiguous*, not discrete, knob over compute–quality trade-offs in attention.

**Caption (verbatim):**
"Figure 6: Time per sample for GQA-XXL as a function of the number of GQA groups with input length 2048 and output length 512. Going from 1 (MQA) to 8 groups adds modest inference overhead, with increasing cost to adding more groups."

### Figure 6 (p.4) ⭐深度解读
![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]]
> [!quote] caption
> Time per sample for GQA-XXL as a function of the number of GQA groups with input length 2048 and output length 512. Going from 1 (MQA) to 8 groups adds modest inference overhead, with increasing cost to adding more groups. is especially helpful for long inputs (Pope et al., 2022; de Jong et al., 2022). Rabe (2023) indepen- dently developed GQA with public implementa- tion. Other works have explore

> [!tip] 技术解读（多模态）
> **Figure 6 (main figure) — Architecture/Components/Data Flow:**

- **Axes:** X = number of GQA groups {1, 4, 8, 16, 32, 64} (log scale); Y = inference time per sample (s, 0–~2.5).
- **Series:** Three attention variants on GQA-XXL (input 2048, output 512):
  - **MHA** (red dotted) — constant baseline ≈ 2.5 s (single head shared across all groups as reference ceiling).
  - **MQA** (orange dotted) — constant baseline ≈ 0.5 s (1-group reference floor).
  - **GQA** (blue solid with square markers) — tunable line sweeping from 1 → 64 groups.
- **Data flow / shape:** Flat plateau from 1 to ~8 groups near the MQA floor (~0.5 s), gentle rise through 16–32 groups, then a steep ascent to ≈ 2.5 s at 64 groups, converging toward MHA.

**Key technical takeaway (≤120 words):** GQA interpolates smoothly between MQA and MHA along the *time* dimension. Going from 1 → 8 groups adds only modest inference overhead, while moving toward 64 groups rapidly approaches MHA's latency. This makes GQA-8 the chosen Pareto-sweet spot: it retains most of MQA's KV-cache / memory-bandwidth savings without the steep slowdown of finer groupings. The curve demonstrates that grouping query heads is a *contiguous*, not discrete, knob over compute–quality trade-offs in attention.

**Caption (verbatim):**
"Figure 6: Time per sample for GQA-XXL as a function of the number of GQA groups with input length 2048 and output length 512. Going from 1 (MQA) to 8 groups adds modest inference overhead, with increasing cost to adding more groups."

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.2 `et al., 2020). For α = 0.05, training took approxi-`
- p.3 `proportion α = 0.05. We see that a larger up-`
- p.4 `MQA with proportion α = 0.05. ‘Mean’ mean-pools`

## 相关论文

- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[zero-memory-optimizations-toward-training-trillion-parameter-models]] — ZeRO: Memory Optimizations Toward Training Trillion Parameter Models
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey
- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] — From ATOP to ZCube: Automated Topology Optimization Pipeline and A Highly Cost-Effective Network Topology for Large Model Training

## 技术点深读（DEEP）

![[deep/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints.txt`（23726 字符）供引用检索。