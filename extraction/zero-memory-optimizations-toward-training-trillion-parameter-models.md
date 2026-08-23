---
paper_num: "47"
title: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models"
authors: "Parameter Models Samyam Rajbhandari∗, JeﬀRasley∗, Olatunji Ruwase, Yuxiong He {samyamr, jerasley, olruwase, yuxhe}@microsoft.com"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/1910.02054"
pdf: "papers/zero-memory-optimizations-toward-training-trillion-parameter-models.pdf"
slug: "zero-memory-optimizations-toward-training-trillion-parameter-models"
tags: [training]
---

# ZeRO: Memory Optimizations Toward Training Trillion Parameter Models

> [!abstract] 摘要（原文）
> 1\. 针对训练万亿参数深度学习模型面临的内存限制，该论文提出了 ZeRO (Zero Redundancy Optimizer)，一种通过消除现有数据并行 (DP) 和模型并行 (MP) 冗余来优化内存的新方法。 2. ZeRO 核心包括 ZeRO-DP（数据并行内存优化）分阶段分区优化器状态、梯度和参数，以及 ZeRO-R（残余内存优化）管理激活、临时缓冲区和内存碎片。 3. ZeRO-100B 的实现使在 400 个 GPU 上高效训练 170B 参数的模型成为可能，相比最先进技术，模型大小增加 8 倍，吞吐量提升 10 倍，并简化了大型模型的训练应用。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Parameter Models Samyam Rajbhandari∗, JeﬀRasley∗, Olatunji Ruwase, Yuxiong He {samyamr, jerasley, olruwase, yuxhe}@microsoft.com
- **arXiv**: https://arxiv.org/abs/1910.02054
- **本地 PDF**: `papers/zero-memory-optimizations-toward-training-trillion-parameter-models.pdf`
- **页数**: 24

## 图表（原文 caption + 页码）

### Figure 1 (p.3) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig01.png]]
*整页渲染: ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p03.png]]*
> [!quote] caption
> Comparing the per-device memory consumption of model states, with three stages of

> [!tip] 技术解读（多模态）
> **Figure Description (≤120 words):**

The figure compares per-device memory consumption across four configurations distributed over N GPUs (gpu_0 … gpu_{N-1}), where each bar is stacked from **Parameters** (blue), **Gradients** (orange), and **Optimizer States** (green):

- **Baseline** – all three components replicated on every GPU → (2+2+K)·Ψ = **120 GB**
- **P_os** – optimizer states sharded across N_d → 2Ψ + 2Ψ + (K·Ψ)/N_d = **31.4 GB**
- **P_os+g** – optimizer states + gradients sharded → 2Ψ + ((2+K)·Ψ)/N_d = **16.6 GB**
- **P_os+g+p** – all components sharded → ((2+2+K)·Ψ)/N_d = **1.9 GB**

**Key takeaway:** Progressively partitioning optimizer states, gradients, and parameters across the data-parallel degree N_d cuts per-device memory by ~63× (120 GB → 1.9 GB) for a 7.5 B-parameter model with N_d = 64, K = 12 (mixed-precision + Adam).

**Caption (verbatim):**

> Figure 1: Comparing the per-device memory consumption of model states, with three stages of *ZeRO*-DP optimizations. Ψ denotes model size (number of parameters), K denotes the memory multiplier of optimizer states, and N_d denotes DP degree. In the example, we assume a model size of Ψ = 7.5B and DP of N_d = 64 with K = 12 based on mixed-precision training with Adam optimizer.

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig02.png]]
*整页渲染: ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p04.png]]*
> [!quote] caption
> ZeRO training throughput and speedup w.r.t SOTA baseline for varying model sizes.

> [!tip] 技术解读（多模态）
> **Figure 2 Description**

The figure is a dual-axis combination chart comparing ZeRO against baseline model-parallel (MP) systems across model sizes (1.5B–170B parameters):
- **Bars (gray):** ZeRO speed-up vs. SOTA, right axis (0–12×). Speed-up grows with model size, peaking ~10× at 100B.
- **Markers (left axis, Tflops/GPU):** Green circles = ZeRO throughput (steady ~25–40 Tflops), orange triangles = Baseline-MP, red triangles = Baseline w. internode MP (collapses below ~5 Tflops beyond 40B).
- **Reference lines:** 15 Pflops (dotted) and 10 Pflops (dashed) hardware ceilings.

**Key takeaway:** ZeRO sustains near-peak GPU throughput across all model sizes while baseline MP throughput collapses beyond 40B parameters, demonstrating that ZeRO eliminates the communication/compute degradation of internode model parallelism.

**Caption (verbatim):**

> Figure 2: *ZeRO* training throughput and speedup w.r.t SOTA baseline for varying model sizes. For *ZeRO*, the MP always fit in a node, while for baseline, models larger than 40B require MP across nodes.

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig03.png]]
*整页渲染: ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p05.png]]*
> [!quote] caption
> Superlinear scalability and per GPU training throughput of a 60B parameter model using ZeRO-100B. 38 TFlops per GPU, and aggregate performance over 15 Petaﬂops. This is more than 10x improvement in training speed compared to SOTA for the same model size.

> [!tip] 技术解读（多模态）
> ## Figure Description (Architecture/Components/Data Flow)

The figure is a dual-axis scalability chart benchmarking a 60B-parameter model trained with **ZeRO-100B** across GPU counts of 64, 128, 256, and 400.

**Components:**
- **X-axis:** Number of GPUs (64 → 400)
- **Left Y-axis (log):** Total Performance in Tflops (1024–16384)
- **Right Y-axis (linear):** Per-GPU Performance in Tflops (0–40)
- **Gray bars:** Per-GPU throughput
- **Green line:** Observed aggregate Tflops
- **Blue line:** Ideal linear-scaling reference

**Data flow:** As GPU count increases, per-GPU bars rise from ~25 → ~38 Tflops, and the green curve climbs above the blue reference line, widening at 400 GPUs.

**Key takeaway:** ZeRO-100B achieves *superlinear* scaling—doubling GPUs more than doubles throughput—because higher data-parallel degree shrinks per-GPU model-state memory, enabling larger micro-batches per device.

## Caption (verbatim)

**Figure 3:** Superlinear scalability and per GPU training throughput of a 60B parameter model using *Ze*RO-100B.

### Figure 4 (p.16) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig04.png]]
*整页渲染: ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]]*
> [!quote] caption
> Max model throughput with ZeRO-DP.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The main figure (Figure 4) is a **scatter plot comparing data-parallel training throughput** across model scales:

**Axes:** X = Model Size (Billions of Parameters, 0–14B); Y = Throughput per GPU (TFlops, 0–55).

**Components / Data flow:**
- **ZeRO-DP** (green circles) — partitioned optimizer states; throughput rises from ~40 → peaks ~47 TFlops/GPU at 6–8B params, then drops as model size exceeds GPU memory.
- **Baseline-DP** (orange triangles) — replicates full optimizer states across GPUs; capped near ~17–20 TFlops/GPU due to memory limits.
- **4.5 Pflops aggregate** (blue dashed reference line) — the target cluster-wide compute floor (~35 TFlops/GPU sustained).

**Key technical takeaway:** ZeRO-DP breaks the *memory-induced throughput ceiling* of standard data parallelism — it sustains >40 TFlops/GPU across 2–10B-parameter models (≈2.5× Baseline-DP) and even 13–14B params still matches the aggregate throughput target, enabling large-model training on commodity GPU clusters without model parallelism.

## Caption (verbatim)

**Figure 4:** Max model throughput with *ZeRO*-DP.

### Figure 5 (p.16) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig05.png]]
*整页渲染: ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]]*
> [!quote] caption
> SOTA Turing-NLG enabled by ZeRO.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The main figure (Figure 4) is a **scatter plot comparing data-parallel training throughput** across model scales:

**Axes:** X = Model Size (Billions of Parameters, 0–14B); Y = Throughput per GPU (TFlops, 0–55).

**Components / Data flow:**
- **ZeRO-DP** (green circles) — partitioned optimizer states; throughput rises from ~40 → peaks ~47 TFlops/GPU at 6–8B params, then drops as model size exceeds GPU memory.
- **Baseline-DP** (orange triangles) — replicates full optimizer states across GPUs; capped near ~17–20 TFlops/GPU due to memory limits.
- **4.5 Pflops aggregate** (blue dashed reference line) — the target cluster-wide compute floor (~35 TFlops/GPU sustained).

**Key technical takeaway:** ZeRO-DP breaks the *memory-induced throughput ceiling* of standard data parallelism — it sustains >40 TFlops/GPU across 2–10B-parameter models (≈2.5× Baseline-DP) and even 13–14B params still matches the aggregate throughput target, enabling large-model training on commodity GPU clusters without model parallelism.

## Caption (verbatim)

**Figure 4:** Max model throughput with *ZeRO*-DP.

### Figure 6 (p.16) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig06.png]]
*整页渲染: ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]]*
> [!quote] caption
> Max model size .

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The main figure (Figure 4) is a **scatter plot comparing data-parallel training throughput** across model scales:

**Axes:** X = Model Size (Billions of Parameters, 0–14B); Y = Throughput per GPU (TFlops, 0–55).

**Components / Data flow:**
- **ZeRO-DP** (green circles) — partitioned optimizer states; throughput rises from ~40 → peaks ~47 TFlops/GPU at 6–8B params, then drops as model size exceeds GPU memory.
- **Baseline-DP** (orange triangles) — replicates full optimizer states across GPUs; capped near ~17–20 TFlops/GPU due to memory limits.
- **4.5 Pflops aggregate** (blue dashed reference line) — the target cluster-wide compute floor (~35 TFlops/GPU sustained).

**Key technical takeaway:** ZeRO-DP breaks the *memory-induced throughput ceiling* of standard data parallelism — it sustains >40 TFlops/GPU across 2–10B-parameter models (≈2.5× Baseline-DP) and even 13–14B params still matches the aggregate throughput target, enabling large-model training on commodity GPU clusters without model parallelism.

## Caption (verbatim)

**Figure 4:** Max model throughput with *ZeRO*-DP.

### Figure 7 (p.16) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig07.png]]
*整页渲染: ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]]*
> [!quote] caption
> Max cache allo- cated.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The main figure (Figure 4) is a **scatter plot comparing data-parallel training throughput** across model scales:

**Axes:** X = Model Size (Billions of Parameters, 0–14B); Y = Throughput per GPU (TFlops, 0–55).

**Components / Data flow:**
- **ZeRO-DP** (green circles) — partitioned optimizer states; throughput rises from ~40 → peaks ~47 TFlops/GPU at 6–8B params, then drops as model size exceeds GPU memory.
- **Baseline-DP** (orange triangles) — replicates full optimizer states across GPUs; capped near ~17–20 TFlops/GPU due to memory limits.
- **4.5 Pflops aggregate** (blue dashed reference line) — the target cluster-wide compute floor (~35 TFlops/GPU sustained).

**Key technical takeaway:** ZeRO-DP breaks the *memory-induced throughput ceiling* of standard data parallelism — it sustains >40 TFlops/GPU across 2–10B-parameter models (≈2.5× Baseline-DP) and even 13–14B params still matches the aggregate throughput target, enabling large-model training on commodity GPU clusters without model parallelism.

## Caption (verbatim)

**Figure 4:** Max model throughput with *ZeRO*-DP.

### Figure 8 (p.16) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig08.png]]
*整页渲染: ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]]*
> [!quote] caption
> Throughput per GPU. a Bert-Large model for a data sample. Even if we assume the same sequence length and the total number of samples required to train the model, training a 1T model would take 140 days, assuming the same hardware and similar computational eﬃciency.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The main figure (Figure 4) is a **scatter plot comparing data-parallel training throughput** across model scales:

**Axes:** X = Model Size (Billions of Parameters, 0–14B); Y = Throughput per GPU (TFlops, 0–55).

**Components / Data flow:**
- **ZeRO-DP** (green circles) — partitioned optimizer states; throughput rises from ~40 → peaks ~47 TFlops/GPU at 6–8B params, then drops as model size exceeds GPU memory.
- **Baseline-DP** (orange triangles) — replicates full optimizer states across GPUs; capped near ~17–20 TFlops/GPU due to memory limits.
- **4.5 Pflops aggregate** (blue dashed reference line) — the target cluster-wide compute floor (~35 TFlops/GPU sustained).

**Key technical takeaway:** ZeRO-DP breaks the *memory-induced throughput ceiling* of standard data parallelism — it sustains >40 TFlops/GPU across 2–10B-parameter models (≈2.5× Baseline-DP) and even 13–14B params still matches the aggregate throughput target, enabling large-model training on commodity GPU clusters without model parallelism.

## Caption (verbatim)

**Figure 4:** Max model throughput with *ZeRO*-DP.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.11) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab01.png]]
> [!quote] caption
> Per-device memory consumption of diﬀerent optimizations in ZeRO -DP as a function of DP degree . Bold-faced text are the combinations for which the model can ﬁt into a cluster of 32GB V100 GPUs.

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**
The referenced table presents **per-device GPU memory consumption** across multiple *ZeRO-DP* optimization configurations, parameterized by the **data-parallel degree (N_d)**. The rows/columns correspond to different combinations of ZeRO stage optimizations (model states and/or optimizer/temporal/gradient partitioning), with **bold-faced cells** marking combinations that successfully fit a model onto **32GB V100 GPUs**. The accompanying narrative highlights the architectural split: in standard data parallelism each device stores 2Ψ + 14Ψ = **16Ψ bytes** of model states, whereas ZeRO partitions those states across N_d devices, yielding 2Ψ + 14Ψ/N_d ≈ **2Ψ bytes** at large N_d. *Key takeaway:* Sharding optimizer states + FP16 gradients across data-parallel ranks provides an **~8× reduction** in per-device state memory, enabling trillion-parameter-scale training on commodity GPU clusters.

**Caption (verbatim):**
"Table 1: Per-device memory consumption of different optimizations in *Ze*RO-DP as a function of DP degree . Bold-faced text are the combinations for which the model can fit into a cluster of 32GB V100 GPUs."

### Table 2 (p.13) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab02.png]]
> [!quote] caption
> Maximum model size through memory analysis (left) and the measured model size when running with ZeRO-OS (right). The measured model size with P os matches the theoretical maximum, demonstrating that our memory analysis provides realistic upper bounds on model sizes.

> [!tip] 表格解读（多模态）
> **Main Figure (Table 2) — Memory Bound Validation**

The table presents a two-column side-by-side comparison: the **left** column lists the theoretical maximum model size derived from the ZeRO memory analysis (computed as the largest model that fits within a fixed per-GPU memory budget), while the **right** column lists the actual model size successfully run under ZeRO-OS (Optimizer State partitioning, $P_{os}$). Each row pairs the analytical bound against the empirical result, with matching rows indicating the theoretical limit is attainable in practice.

**Key technical takeaway:** The measured model sizes under $P_{os}$ exactly match the theoretical ceilings from the memory analysis, confirming that the analytical model produces tight (not loose) upper bounds and is a reliable predictor for budgeting large-model training on memory-constrained GPUs.

**Verbatim caption:**

*Table 2: Maximum model size through memory analysis (left) and the measured model size when running with ZeRO-OS (right). The measured model size with $P_{os}$ matches the theoretical maximum, demonstrating that our memory analysis provides realistic upper bounds on model sizes.*

### Table 3 (p.18) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab03.png]]
> [!quote] caption
> ZeRO conﬁgurations

> [!tip] 表格解读（多模态）
> The visible content does not contain a main figure — only a table caption heading and surrounding body paragraph text. No architectural diagram, components, or data-flow elements are rendered in the image.

Caption (transcribed verbatim):

**Table 3: ZeRO configurations**

### Table 4 (p.19) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab04.png]]
> [!quote] caption
> Conﬁgurations for diﬀerent model sizes, number of layers, and hidden dimensions (HD) across Figures 2, 3, 4.

> [!tip] 表格解读（多模态）
> **Description of the main figure (Figure 8):**
The figure compares two large language model sizes (60B and 170B parameters) across several optimization configurations. Its likely components: an x-axis (model size or optimization level — baseline, C4, C5, and the activation-CPU-offloading scheme P_a+cpu), a y-axis reporting either peak achievable throughput (tokens/sec) or memory footprint, with grouped bars/lines per model. Data flow: GPU forward/backward activations → measured during training, where P_a+cpu streams activations between GPU HBM and CPU DRAM. The plot highlights that C4 maximizes speed/memory efficiency for the 60B model, while C5 becomes necessary only beyond a memory threshold (e.g., 170B), trading CPU transfer latency for the ability to fit the model.

**Key technical takeaway (≤120 words):**
Memory-saving optimizations and raw throughput are not monotonically tied. Reducing memory permits larger batches and thus higher performance — *unless* the optimization introduces host-device traffic. For the 60B model, C5 lowers memory but incurs CPU–GPU activation movement, *degrading* throughput versus C4. For the 170B model, however, C5 (or P_a+cpu) is mandatory to fit weights/activations in device memory at all; smaller batch sizes under tighter memory caps would otherwise cripple utilization. **Practical implication:** activate P_a+cpu *conditionally* — only when smaller, faster configurations would otherwise OOM or force batch sizes so small that effective TFLOPS collapse. Training stacks should gate offloading on a memory-pressure threshold rather than enabling it by default.

**Caption transcription (verbatim):**
Table 4: Configurations for different model sizes, number of layers, and hidden dimensions (HD) across Figures 2, 3, 4.

### Table 8 (p.23) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab08.png]]
> [!quote] caption
> Model conﬁgurations for Figure 5 related to memory allocated with diﬀerent ZeRO conﬁgurations.

> [!tip] 表格解读（多模态）
> **Description:**

The provided image does not display the actual table content — only the page header/caption and a lone period are visible; the table itself (rows of ZeRO-related model configuration parameters) is not rendered in the image excerpt.

**Key technical takeaway:**
ZeRO (Zero Redundancy Optimizer) partitions optimizer state, gradients, and/or parameters across data-parallel workers to reduce per-GPU memory consumption, enabling training of larger models with the same hardware budget — at the cost of additional communication.

**Verbatim caption transcription:**

> Table 8: Model configurations for Figure 5 related to memory allocated with different ZeRO configurations.

### Table 10 (p.24) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab10.png]]
> [!quote] caption
> Model conﬁgurations for Figure 7 related to evaluating maximum model sizes vs throughput while using only data-parallelism.

> [!tip] 表格解读（多模态）
> The user requested a description of a figure, but the image actually shows the caption of a table (Table 10) plus surrounding explanatory paragraphs — no figure is visually present. I cannot fabricate figure content, so I will describe what can be inferred from the caption and surrounding text, then transcribe the caption verbatim.

**Description (inferred from caption + surrounding text):**
Table 10 lists the hyperparameter/parallelism configurations (model size, hidden size, attention heads, model-parallel size MP, data-parallel size DP, global batch size, total GPUs) used for the Figure 7 "max model size vs throughput" sweep under data-parallelism-only training. Configurations are constrained so that hidden size ÷ attention heads, hidden size ÷ MP, and attention heads ÷ MP are integers, and total GPUs = MP × DP is constrained to ≤400 (e.g., baseline 170B uses 256 GPUs, DP=1, incurring no DP communication). **Key takeaway:** Even when the baseline is granted an artificial advantage (fewer GPUs, no DP communication overhead), ZeRO still delivers the gains reported in the paper — and since throughput is normalized per GPU, the comparison remains apples-to-apples.

**Caption transcribed verbatim:**
"Table 10: Model configurations for Figure 7 related to evaluating maximum model sizes vs throughput while using only data-parallelism."

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\frac{batch \times seq\_length \times n \times h}{B_{gpu}} \leq \frac{24 \times n \times h^2}{B_{data}}
$$

## 相关论文

- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core
- [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] — GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey
- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[muon-is-scalable-for-llm-training]] — Muon is Scalable for LLM Training

## 技术点深读（DEEP）

![[deep/zero-memory-optimizations-toward-training-trillion-parameter-models]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/zero-memory-optimizations-toward-training-trillion-parameter-models.txt`（67057 字符）供引用检索。