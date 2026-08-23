---
paper_num: "48"
title: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM"
authors: ""
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2104.04473"
pdf: "papers/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm.pdf"
slug: "efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm"
tags: [training, architecture]
---

# Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM

> [!abstract] 摘要（原文）
> 1\. 🎯 针对GPU内存限制和训练时间过长等大规模语言模型挑战，本文提出了PTD-P（Pipeline, Tensor, Data Parallelism）组合并行策略。 2. 🚀 PTD-P通过引入新颖的交错式流水线调度（interleaved pipelining schedule）和Scatter/Gather通信优化，显著提高了吞吐量，同时保持内存效率。 3. 💪 在3072个A100 GPU上，该方法为万亿参数模型实现了502 petaFLOP/s的总吞吐量，达到单GPU理论峰值的52%，使得训练时间可缩短至约3个月。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2104.04473
- **本地 PDF**: `papers/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm.pdf`
- **页数**: 13

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig01.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p01.png]]*
> [!quote] caption
> Trend of sizes of state-of-the-art Natural Language Pro- cessing (NLP) models with time. The number of floating-point op- erations to train these models is increasing at an exponential rate.

> [!tip] 技术解读（多模态）
> **Figure Description**

Figure 1 is a semi-log scatter plot showing the growth of state-of-the-art NLP model sizes over time. The **x-axis** spans 2018–2021 (Year), and the **y-axis** is "Number of parameters (in billions)" on a logarithmic scale from 10⁻² to 10³. Six labeled data points trace an upward trajectory: ELMo (94M, 2018), BERT-L (340M, 2018–2019), GPT-2 (1.5B, 2019), Megatron-LM (8.3B, 2019–2020), Turing-NLG (17.2B, 2020), and GPT-3 (175B, 2020). A red dotted reference line approximates the exponential trend. There is no data-flow or architectural pipeline—this figure is purely an empirical trend visualization motivating the paper's parallel-training contributions.

**Key Technical Takeaway (≈55 words)**

State-of-the-art NLP model parameter counts have grown roughly three orders of magnitude in just two years (ELMo 94M → GPT-3 175B), following a near-exponential curve on a log scale. This explosive scaling—coupled with the cited ~288-year single-V100 training time for GPT-3—directly motivates the paper's combined tensor + pipeline + data parallelism approach for multi-GPU clusters.

**Caption (verbatim):**

Figure 1: Trend of sizes of state-of-the-art Natural Language Processing (NLP) models with time. The number of floating-point operations to train these models is increasing at an exponential rate.

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig02.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]]*
> [!quote] caption
> Combination of tensor and pipeline model parallelism (MP) used in this work for transformer-based models.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Figure 4** illustrates two pipeline-parallel training schedules across 4 devices over time:

**Architecture/Components:**
- **Top diagram (Default 1F1B):** Devices process microbatches (1–8) in a one-forward-one-backward pattern, followed by a second batch (9–12). A vertical "pipeline flush" line marks the weight-update boundary; gray cells = idle/bubble time.
- **Bottom diagram (Interleaved 1F1B):** Each device is assigned multiple model chunks (here, 2). Dark colors = first chunk, light colors = second chunk. Each chunk runs its own mini 1F1B cycle, reducing the idle bubble.

**Data flow:** Time progresses left→right; rows are device ranks; the pipeline flush partitions training into weight-update boundaries.

## Key Technical Takeaway

Interleaved scheduling reduces the pipeline bubble by assigning multiple model chunks per device, so each device alternates between chunks during idle gaps — increasing utilization without changing per-device memory footprint. (53 words)

## Caption (Verbatim)

**Figure 4:** Default and interleaved 1F1B pipeline schedules. The top figure shows the default non-interleaved 1F1B schedule. The bottom figure shows the interleaved 1F1B schedule, where each device is assigned multiple chunks (in this case, 2). Dark colors show the first chunk and light colors show the second chunk. The size of the pipeline bubble is smaller (the pipeline flush happens sooner in the interleaved timeline).

### Figure 3 (p.3) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig03.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]]*
> [!quote] caption
> GPipe pipeline schedule with forward passes (blue) for all microbatches (represented by numbers) followed by backward passes (green). The gray area represents the pipeline bubble. For simplicity, we assume that the backward pass takes twice as long as the forward pass. The efficiency of the pipeline schedule does not depend on this factor. Each batch in this example consists of 8 microbatches, and

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Figure 4** illustrates two pipeline-parallel training schedules across 4 devices over time:

**Architecture/Components:**
- **Top diagram (Default 1F1B):** Devices process microbatches (1–8) in a one-forward-one-backward pattern, followed by a second batch (9–12). A vertical "pipeline flush" line marks the weight-update boundary; gray cells = idle/bubble time.
- **Bottom diagram (Interleaved 1F1B):** Each device is assigned multiple model chunks (here, 2). Dark colors = first chunk, light colors = second chunk. Each chunk runs its own mini 1F1B cycle, reducing the idle bubble.

**Data flow:** Time progresses left→right; rows are device ranks; the pipeline flush partitions training into weight-update boundaries.

## Key Technical Takeaway

Interleaved scheduling reduces the pipeline bubble by assigning multiple model chunks per device, so each device alternates between chunks during idle gaps — increasing utilization without changing per-device memory footprint. (53 words)

## Caption (Verbatim)

**Figure 4:** Default and interleaved 1F1B pipeline schedules. The top figure shows the default non-interleaved 1F1B schedule. The bottom figure shows the interleaved 1F1B schedule, where each device is assigned multiple chunks (in this case, 2). Dark colors show the first chunk and light colors show the second chunk. The size of the pipeline bubble is smaller (the pipeline flush happens sooner in the interleaved timeline).

### Figure 4 (p.3) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig04.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]]*
> [!quote] caption
> Default and interleaved 1F1B pipeline schedules. The top figure shows the default non-interleaved 1F1B schedule. The bottom figure shows the interleaved 1F1B schedule, where each device is assigned multiple chunks (in this case, 2). Dark colors show the first chunk and light colors show the second chunk. The size of the pipeline bubble is smaller (the pipeline flush happens sooner in the interleav

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Figure 4** illustrates two pipeline-parallel training schedules across 4 devices over time:

**Architecture/Components:**
- **Top diagram (Default 1F1B):** Devices process microbatches (1–8) in a one-forward-one-backward pattern, followed by a second batch (9–12). A vertical "pipeline flush" line marks the weight-update boundary; gray cells = idle/bubble time.
- **Bottom diagram (Interleaved 1F1B):** Each device is assigned multiple model chunks (here, 2). Dark colors = first chunk, light colors = second chunk. Each chunk runs its own mini 1F1B cycle, reducing the idle bubble.

**Data flow:** Time progresses left→right; rows are device ranks; the pipeline flush partitions training into weight-update boundaries.

## Key Technical Takeaway

Interleaved scheduling reduces the pipeline bubble by assigning multiple model chunks per device, so each device alternates between chunks during idle gaps — increasing utilization without changing per-device memory footprint. (53 words)

## Caption (Verbatim)

**Figure 4:** Default and interleaved 1F1B pipeline schedules. The top figure shows the default non-interleaved 1F1B schedule. The bottom figure shows the interleaved 1F1B schedule, where each device is assigned multiple chunks (in this case, 2). Dark colors show the first chunk and light colors show the second chunk. The size of the pipeline bubble is smaller (the pipeline flush happens sooner in the interleaved timeline).

### Figure 5 (p.5) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig05.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p05.png]]*
> [!quote] caption
> Blocks of transformer model partitioned with tensor model parallelism (figures borrowed from Megatron [40]). 𝑓and 𝑔 are conjugate. 𝑓is the identity operator in the forward pass and all- reduce in the backward pass, while 𝑔is the reverse. relevant for the pipeline bubble size. We qualitatively describe how communication time behaves and present cost models for amount of communication; however, we d

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 5)

The figure shows how transformer blocks are partitioned for tensor model parallelism across two devices.

**(a) MLP:** Input X is split by operator *f* into two replicas; each row passes through its own weight column (XA₁, XA₂), then GeLU → Y₁, Y₂. The outputs are multiplied by rows of B = [B₁; B₂] (Y₁B₁, Y₂B₂), merged via operator *g*, passed through Dropout, and concatenated to Z = Dropout(YB).

**(b) Self-Attention:** The same partitioning scheme splits the Q, K, V heads across devices (Q = [Q₁,Q₂], K = [K₁,K₂], V = [V₁,V₂]). Each device independently performs scaled-dot-product attention and dropout, then recombines via *g* before dropout to yield Z.

**Key takeaway:** *f* and *g* are conjugate operators—*f* is identity in the forward pass / all-reduce in the backward pass, while *g* does the reverse. This duality lets both MLP and attention layers be distributed without altering the mathematical result.

*(Figure 6, for context, shows that pipeline bubble fraction rises sharply with data-parallel size d, especially when b′ is small.)*

---

## Caption (verbatim)

**Figure 5:** Blocks of transformer model partitioned with tensor model parallelism (figures borrowed from Megatron [40]). *f* and *g* are conjugate. *f* is the identity operator in the forward pass and all-reduce in the backward pass, while *g* is the reverse.

*(Sub-labels within the figure: "(a) MLP." and "(b) Self-Attention.")*

### Figure 6 (p.5) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig06.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p05.png]]*
> [!quote] caption
> Fraction of time spent idling due to pipeline flush (pipeline bubble size) versus data-parallel size (𝑑), for different numbers of GPUs (𝑛) and ratio of batch size to microbatch size (𝑏′ = 𝐵/𝑏).

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 5)

The figure shows how transformer blocks are partitioned for tensor model parallelism across two devices.

**(a) MLP:** Input X is split by operator *f* into two replicas; each row passes through its own weight column (XA₁, XA₂), then GeLU → Y₁, Y₂. The outputs are multiplied by rows of B = [B₁; B₂] (Y₁B₁, Y₂B₂), merged via operator *g*, passed through Dropout, and concatenated to Z = Dropout(YB).

**(b) Self-Attention:** The same partitioning scheme splits the Q, K, V heads across devices (Q = [Q₁,Q₂], K = [K₁,K₂], V = [V₁,V₂]). Each device independently performs scaled-dot-product attention and dropout, then recombines via *g* before dropout to yield Z.

**Key takeaway:** *f* and *g* are conjugate operators—*f* is identity in the forward pass / all-reduce in the backward pass, while *g* does the reverse. This duality lets both MLP and attention layers be distributed without altering the mathematical result.

*(Figure 6, for context, shows that pipeline bubble fraction rises sharply with data-parallel size d, especially when b′ is small.)*

---

## Caption (verbatim)

**Figure 5:** Blocks of transformer model partitioned with tensor model parallelism (figures borrowed from Megatron [40]). *f* and *g* are conjugate. *f* is the identity operator in the forward pass and all-reduce in the backward pass, while *g* is the reverse.

*(Sub-labels within the figure: "(a) MLP." and "(b) Self-Attention.")*

### Figure 7 (p.6) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig07.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p06.png]]*
> [!quote] caption
> Per-GPU throughput versus microbatch size for a GPT model with a billion parameters (128 attention heads, hidden size of 4096, 4 transformer layers).

> [!tip] 技术解读（多模态）
> **Figure 7 Description**

**Components:** A 2D line plot with a single curve (blue, circular markers) tracking per-GPU throughput as a function of microbatch size.

**Axes:**
- Y-axis: "Achieved teraFLOP/s per GPU" (linear scale, 0–100)
- X-axis: "Microbatch size" (categorical: 1, 2, 4, 8, 16)

**Data flow / trend:** Throughput rises monotonically with microbatch size — starting near ~70 TFLOPs/s at size 1, climbing to ~85 at size 2, and asymptotically approaching ~90 TFLOPs/s at sizes 8–16, indicating diminishing returns at higher microbatch values.

**Key takeaway:** Larger microbatch sizes (≥4) unlock substantially higher per-GPU utilization (≈1.3× gain) on a billion-parameter GPT model, since smaller microbatches leave the GPU under-utilized during compute-bound transformer operations.

**Caption (verbatim):**
*Figure 7: Per-GPU throughput versus microbatch size for a GPT model with a billion parameters (128 attention heads, hidden size of 4096, 4 transformer layers).*

### Figure 8 (p.6) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig08.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p06.png]]*
> [!quote] caption
> Behavior of normalized estimated throughput (time com- puted as 𝑡= (𝑏′/𝑏+ 𝑝−1) ·  𝑡𝑓(𝑏) + 𝑡𝑏(𝑏)) with respect to the mi- crobatch size 𝑏for the same GPT model from Figure 7.

> [!tip] 技术解读（多模态）
> **Figure 7 Description**

**Components:** A 2D line plot with a single curve (blue, circular markers) tracking per-GPU throughput as a function of microbatch size.

**Axes:**
- Y-axis: "Achieved teraFLOP/s per GPU" (linear scale, 0–100)
- X-axis: "Microbatch size" (categorical: 1, 2, 4, 8, 16)

**Data flow / trend:** Throughput rises monotonically with microbatch size — starting near ~70 TFLOPs/s at size 1, climbing to ~85 at size 2, and asymptotically approaching ~90 TFLOPs/s at sizes 8–16, indicating diminishing returns at higher microbatch values.

**Key takeaway:** Larger microbatch sizes (≥4) unlock substantially higher per-GPU utilization (≈1.3× gain) on a billion-parameter GPT model, since smaller microbatches leave the GPU under-utilized during compute-bound transformer operations.

**Caption (verbatim):**
*Figure 7: Per-GPU throughput versus microbatch size for a GPT model with a billion parameters (128 attention heads, hidden size of 4096, 4 transformer layers).*

### Figure 9 (p.7) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig09.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p07.png]]*
> [!quote] caption
> Scatter/gather communication optimization. Light blue blocks are layers in the first pipeline stage, and dark blue blocks are layers in the second pipeline stage. Without the scatter/gather optimization, the same tensor is sent redundantly over inter-node

> [!tip] 技术解读（多模态）
> ## Figure 9 Description

**Architecture/Components:** Two paired GPU groups (numbered 1–2 and 3–4) are connected intra-node via NVLink (green) and inter-node via InfiniBand (red bars). Light-blue blocks represent the first pipeline stage; dark-blue blocks represent the second.

**Data Flow:**
- **(a) Without optimization:** The full tensor is sent redundantly across all InfiniBand links between every GPU pair of consecutive stages — 8× the necessary traffic (matches the tensor-model-parallel size of 8).
- **(b) With optimization:** Each rank splits its output into equal chunks and **scatters** only one chunk per InfiniBand link (e.g., rank 1 → rank 3, rank 2 → rank 4). On the receiver, an **all-gather** over the fast NVLink re-materializes the full tensor.

**Key Technical Takeaway:** Scatter/gather reduces inter-node InfiniBand volume per stage pair by a factor of *t* (tensor-parallel size), cutting communication to bsh/t per stage pair — making communication-intensive schedules (e.g., interleaved pipeline parallelism) feasible.

## Caption (verbatim)

**Figure 9:** Scatter/gather communication optimization. Light blue blocks are layers in the first pipeline stage, and dark blue blocks are layers in the second pipeline stage. Without the scatter/gather optimization, the same tensor is sent redundantly over inter-node InfiniBand links. Instead, at the sender, we can scatter the tensor into smaller chunks, reducing the sizes of tensors sent over InfiniBand links. The final tensor can then be rematerialized at the receiver using a gather operation.

### Figure 10 (p.8) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig10.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p08.png]]*
> [!quote] caption
> Throughput per GPU of PTD-P and ZeRO-3 for two differ- ent GPT models (the 175B GPT-3 model is shown with dotted lines, and the 530B model is shown with solid lines). Global batch sizes are fixed and ZeRO-3 is used without any model parallelism.

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 10)

**Architecture/Components:** A 2-axis line chart comparing per-GPU throughput (y-axis: Achieved teraFLOP/s per GPU, 0–200) against GPU count (x-axis: ~768 to ~1920). Four series are plotted: **ZeRO-3, 175B** (blue dashed/circles), **ZeRO-3, 530B** (blue solid/diamonds), **PTD-P, 175B** (orange dashed/triangles), and **PTD-P, 530B** (orange solid/squares).

**Data Flow:** As GPUs scale up, PTD-P lines remain nearly flat (~140–160 teraFLOP/s), while ZeRO-3 lines degrade sharply (down to ~40–50 teraFLOP/s). PTD-P dominates at all GPU counts, with the gap widening at scale.

**Key Takeaway:** PTD-P scales more gracefully than ZeRO-3 (without tensor parallelism) due to reduced cross-node communication—outperforming ZeRO-3 by ~70% on both model sizes at higher GPU counts under fixed global batch size.

## Caption (verbatim)

**Figure 10:** Throughput per GPU of PTD-P and ZeRO-3 for two different GPT models (the 175B GPT-3 model is shown with dotted lines, and the 530B model is shown with solid lines). Global batch sizes are fixed and ZeRO-3 is used without any model parallelism.

### Figure 11 (p.9) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig11.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]]*
> [!quote] caption
> Throughput per GPU of pipeline parallelism using two different batch sizes in a weak-scaling experiment setup (model size increases with the pipeline-parallel size). 12 24 36 48 60

> [!tip] 技术解读（多模态）
> **Figure 11 — Description (≤120 words):**

The figure is a line chart plotting achieved teraFLOP/s per GPU (y-axis, 0–200) against pipeline-parallel size (x-axis: 1, 2, 4, 8) for a weak-scaling experiment where model size grows proportionally to the pipeline degree. Two series are shown: **Batch size = 8** (blue circles) and **Batch size = 128** (orange diamonds).

- The **large-batch (128)** curve stays roughly flat near ~170–175 TF/s/GPU across all pipeline depths.
- The **small-batch (8)** curve drops steeply from ~165 → ~85 TF/s/GPU as the pipeline grows.

**Key takeaway:** Larger batch sizes amortize the pipeline bubble overhead, preserving throughput as pipeline-parallel size increases; small batches suffer dramatically because the bubble fraction (b−1)/m grows with pipeline depth.

**Caption (verbatim):**

> Figure 11: Throughput per GPU of pipeline parallelism using two different batch sizes in a weak-scaling experiment setup (model size increases with the pipeline-parallel size).

### Figure 12 (p.9) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig12.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]]*
> [!quote] caption
> Throughput per GPU of interleaved and non-interleaved schedules for a GPT model (175 billion parameters) on 96 GPUs. and a microbatch size of 1. As we increase the number of pipeline stages, we also increase the size of the model by proportionally increasing the number of layers in the model, e.g., with a pipeline- parallel size of 1, we use a model with 3 transformer layers and 15 billion paramet

> [!tip] 技术解读（多模态）
> **Figure 11 — Description (≤120 words):**

The figure is a line chart plotting achieved teraFLOP/s per GPU (y-axis, 0–200) against pipeline-parallel size (x-axis: 1, 2, 4, 8) for a weak-scaling experiment where model size grows proportionally to the pipeline degree. Two series are shown: **Batch size = 8** (blue circles) and **Batch size = 128** (orange diamonds).

- The **large-batch (128)** curve stays roughly flat near ~170–175 TF/s/GPU across all pipeline depths.
- The **small-batch (8)** curve drops steeply from ~165 → ~85 TF/s/GPU as the pipeline grows.

**Key takeaway:** Larger batch sizes amortize the pipeline bubble overhead, preserving throughput as pipeline-parallel size increases; small batches suffer dramatically because the bubble fraction (b−1)/m grows with pipeline depth.

**Caption (verbatim):**

> Figure 11: Throughput per GPU of pipeline parallelism using two different batch sizes in a weak-scaling experiment setup (model size increases with the pipeline-parallel size).

### Figure 13 (p.9) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig13.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]]*
> [!quote] caption
> Throughput per GPU of various parallel configurations that combine pipeline and tensor model parallelism using a GPT model with 162.2 billion parameters and 64 A100 GPUs.

> [!tip] 技术解读（多模态）
> **Figure 11 — Description (≤120 words):**

The figure is a line chart plotting achieved teraFLOP/s per GPU (y-axis, 0–200) against pipeline-parallel size (x-axis: 1, 2, 4, 8) for a weak-scaling experiment where model size grows proportionally to the pipeline degree. Two series are shown: **Batch size = 8** (blue circles) and **Batch size = 128** (orange diamonds).

- The **large-batch (128)** curve stays roughly flat near ~170–175 TF/s/GPU across all pipeline depths.
- The **small-batch (8)** curve drops steeply from ~165 → ~85 TF/s/GPU as the pipeline grows.

**Key takeaway:** Larger batch sizes amortize the pipeline bubble overhead, preserving throughput as pipeline-parallel size increases; small batches suffer dramatically because the bubble fraction (b−1)/m grows with pipeline depth.

**Caption (verbatim):**

> Figure 11: Throughput per GPU of pipeline parallelism using two different batch sizes in a weak-scaling experiment setup (model size increases with the pipeline-parallel size).

### Figure 14 (p.10) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig14.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]]*
> [!quote] caption
> Throughput per GPU of various parallel configurations that combine data and pipeline model parallelism using a GPT model with 5.9 billion parameters, three different batch sizes, mi- crobatch size of 1, and 64 A100 GPUs. (2, 32) (4, 16) (8, 8) (16, 4) (32, 2) (Tensor-parallel size, Data-parallel size) 0 50 100 150 200

> [!tip] 技术解读（多模态）
> **Figure Description**

The page contains three line charts measuring **Achieved teraFLOP/s per GPU** for GPT model training on 64 A100 GPUs:

- **Figure 14** — Throughput vs. (Pipeline-parallel, Data-parallel) sizes for a 5.9B-param GPT at batch=32 and 512, microbatch=1. Both curves slope downward as pipeline size grows (32 → 90–40 teraFLOP/s), while data parallelism alone sustains higher throughput.

- **Figure 15** — Same metric vs. (Tensor-parallel, Data-parallel) sizes. All three batch sizes (32, 128, 512) drop sharply (125 → ~25 teraFLOP/s) as tensor-parallel size increases from 2 to 32, since all-to-all communication dominates.

- **Figure 16** — Throughput vs. microbatch size for a (t,p)=(8,8) config on a 91B-param GPT. Curves are nearly flat (~155 teraFLOP/s for batch=512; ~155→120 for batch=128) across microbatch = 1–8.

**Key Technical Takeaway (≤120 words):** Tensor parallelism is most efficient *within* a node (DGX A100, 8 GPUs) because it avoids expensive all-to-all communication across nodes, while pipeline parallelism uses cheap point-to-point links that scale across nodes. Optimal configuration matches tensor-parallel size to GPUs/node (8) and uses pipeline parallelism across nodes to scale further. Increasing pipeline-parallel size enlarges the pipeline bubble and hurts throughput; increasing tensor-parallel size inflates all-to-all cost; and microbatch size must be tuned (best ≈2 for the 91B model) to balance bubble size against GPU kernel arithmetic intensity. Data parallelism alone cannot scale beyond ~1500 GPUs due to memory and optimizer-state limits.

**Caption (verbatim):**

*Figure 14: Throughput per GPU of various parallel configurations that combine data and pipeline model parallelism using a GPT model with 5.9 billion parameters, three different batch sizes, microbatch size of 1, and 64 A100 GPUs.*

*Figure 15: Throughput per GPU of various parallel configurations that combine data and tensor model parallelism using a GPT model with 5.9 billion parameters, three different batch sizes, microbatch size of 1, and 64 A100 GPUs.*

*Figure 16: Throughput per GPU of a (t, p) = (8, 8) parallel configuration for different microbatch sizes on a GPT model with 91 billion parameters, for two different batch sizes using 64 A100 GPUs.*

### Figure 15 (p.10) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig15.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]]*
> [!quote] caption
> Throughput per GPU of various parallel configurations that combine data and tensor model parallelism using a GPT model with 5.9 billion parameters, three different batch sizes, microbatch size of 1, and 64 A100 GPUs. 1 2 4 8

> [!tip] 技术解读（多模态）
> **Figure Description**

The page contains three line charts measuring **Achieved teraFLOP/s per GPU** for GPT model training on 64 A100 GPUs:

- **Figure 14** — Throughput vs. (Pipeline-parallel, Data-parallel) sizes for a 5.9B-param GPT at batch=32 and 512, microbatch=1. Both curves slope downward as pipeline size grows (32 → 90–40 teraFLOP/s), while data parallelism alone sustains higher throughput.

- **Figure 15** — Same metric vs. (Tensor-parallel, Data-parallel) sizes. All three batch sizes (32, 128, 512) drop sharply (125 → ~25 teraFLOP/s) as tensor-parallel size increases from 2 to 32, since all-to-all communication dominates.

- **Figure 16** — Throughput vs. microbatch size for a (t,p)=(8,8) config on a 91B-param GPT. Curves are nearly flat (~155 teraFLOP/s for batch=512; ~155→120 for batch=128) across microbatch = 1–8.

**Key Technical Takeaway (≤120 words):** Tensor parallelism is most efficient *within* a node (DGX A100, 8 GPUs) because it avoids expensive all-to-all communication across nodes, while pipeline parallelism uses cheap point-to-point links that scale across nodes. Optimal configuration matches tensor-parallel size to GPUs/node (8) and uses pipeline parallelism across nodes to scale further. Increasing pipeline-parallel size enlarges the pipeline bubble and hurts throughput; increasing tensor-parallel size inflates all-to-all cost; and microbatch size must be tuned (best ≈2 for the 91B model) to balance bubble size against GPU kernel arithmetic intensity. Data parallelism alone cannot scale beyond ~1500 GPUs due to memory and optimizer-state limits.

**Caption (verbatim):**

*Figure 14: Throughput per GPU of various parallel configurations that combine data and pipeline model parallelism using a GPT model with 5.9 billion parameters, three different batch sizes, microbatch size of 1, and 64 A100 GPUs.*

*Figure 15: Throughput per GPU of various parallel configurations that combine data and tensor model parallelism using a GPT model with 5.9 billion parameters, three different batch sizes, microbatch size of 1, and 64 A100 GPUs.*

*Figure 16: Throughput per GPU of a (t, p) = (8, 8) parallel configuration for different microbatch sizes on a GPT model with 91 billion parameters, for two different batch sizes using 64 A100 GPUs.*

### Figure 16 (p.10) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig16.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]]*
> [!quote] caption
> Throughput per GPU of a (𝑡, 𝑝) = (8, 8) parallel configura- tion for different microbatch sizes on a GPT model with 91 billion parameters, for two different batch sizes using 64 A100 GPUs. importance of using both tensor and pipeline model parallelism in conjunction to train a 161-billion-parameter GPT model (32 trans- former layers to support pipeline-parallel size of 32, 128 attention heads, hid

> [!tip] 技术解读（多模态）
> **Figure Description**

The page contains three line charts measuring **Achieved teraFLOP/s per GPU** for GPT model training on 64 A100 GPUs:

- **Figure 14** — Throughput vs. (Pipeline-parallel, Data-parallel) sizes for a 5.9B-param GPT at batch=32 and 512, microbatch=1. Both curves slope downward as pipeline size grows (32 → 90–40 teraFLOP/s), while data parallelism alone sustains higher throughput.

- **Figure 15** — Same metric vs. (Tensor-parallel, Data-parallel) sizes. All three batch sizes (32, 128, 512) drop sharply (125 → ~25 teraFLOP/s) as tensor-parallel size increases from 2 to 32, since all-to-all communication dominates.

- **Figure 16** — Throughput vs. microbatch size for a (t,p)=(8,8) config on a 91B-param GPT. Curves are nearly flat (~155 teraFLOP/s for batch=512; ~155→120 for batch=128) across microbatch = 1–8.

**Key Technical Takeaway (≤120 words):** Tensor parallelism is most efficient *within* a node (DGX A100, 8 GPUs) because it avoids expensive all-to-all communication across nodes, while pipeline parallelism uses cheap point-to-point links that scale across nodes. Optimal configuration matches tensor-parallel size to GPUs/node (8) and uses pipeline parallelism across nodes to scale further. Increasing pipeline-parallel size enlarges the pipeline bubble and hurts throughput; increasing tensor-parallel size inflates all-to-all cost; and microbatch size must be tuned (best ≈2 for the 91B model) to balance bubble size against GPU kernel arithmetic intensity. Data parallelism alone cannot scale beyond ~1500 GPUs due to memory and optimizer-state limits.

**Caption (verbatim):**

*Figure 14: Throughput per GPU of various parallel configurations that combine data and pipeline model parallelism using a GPT model with 5.9 billion parameters, three different batch sizes, microbatch size of 1, and 64 A100 GPUs.*

*Figure 15: Throughput per GPU of various parallel configurations that combine data and tensor model parallelism using a GPT model with 5.9 billion parameters, three different batch sizes, microbatch size of 1, and 64 A100 GPUs.*

*Figure 16: Throughput per GPU of a (t, p) = (8, 8) parallel configuration for different microbatch sizes on a GPT model with 91 billion parameters, for two different batch sizes using 64 A100 GPUs.*

### Figure 17 (p.11) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig17.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p11.png]]*
> [!quote] caption
> Throughput (in sequences per second) with and without activation recomputation for a GPT model with 145 billion param- eters using 128 A100 GPUs ((𝑡, 𝑝) = (8, 16)). 12 24 36 48 60

> [!tip] 技术解读（多模态）
> ## Figure Description (≤120 words)

Two line-chart performance comparisons from the Megatron-LM paper:

**Figure 17 — Activation Recomputation (top):** Plots throughput (sequences/sec, y-axis) vs. batch size (1–256, log scale) for a 145B-param GPT model on 128 A100 GPUs. Two curves: *Act. recomputation* (blue) and *W/o act. recomp* (orange). Without recomputation, throughput peaks early (~3.75 at batch 8) then plateaus. With recomputation, it climbs steadily to ~8 at batch 256.

**Figure 18 — Scatter/Gather Optimization (bottom):** Plots achieved teraFLOP/s/GPU vs. batch size (12–60) for a 175B-param GPT-3 model on 96 A100s. *Scatter/gather optimization* (orange) consistently outperforms *Unoptimized* (blue), reaching ~150 vs. ~130 teraFLOP/s/GPU at batch 60.

**Key takeaway:** Optimizations trade a small-batch penalty for large-batch scalability — recomputation trades ~33% throughput at small batches for ~2× gain at batch 256 by shrinking the pipeline bubble; scatter/gather yields a consistent ~11–15% speedup across batch sizes.

---

## Captions (verbatim)

**Figure 17:** Throughput (in sequences per second) with and without activation recomputation for a GPT model with 145 billion parameters using 128 A100 GPUs ((*t*, *p*) = (8, 16)).

**Figure 18:** Throughput per GPU with and without the scatter/gather optimization for a GPT model with 175 billion parameters using 96 A100 GPUs and the interleaved schedule.

### Figure 18 (p.11) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig18.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p11.png]]*
> [!quote] caption
> Throughput per GPU with and without the scatter/gather optimization for a GPT model with 175 billion parameters using 96 A100 GPUs and the interleaved schedule.

> [!tip] 技术解读（多模态）
> ## Figure Description (≤120 words)

Two line-chart performance comparisons from the Megatron-LM paper:

**Figure 17 — Activation Recomputation (top):** Plots throughput (sequences/sec, y-axis) vs. batch size (1–256, log scale) for a 145B-param GPT model on 128 A100 GPUs. Two curves: *Act. recomputation* (blue) and *W/o act. recomp* (orange). Without recomputation, throughput peaks early (~3.75 at batch 8) then plateaus. With recomputation, it climbs steadily to ~8 at batch 256.

**Figure 18 — Scatter/Gather Optimization (bottom):** Plots achieved teraFLOP/s/GPU vs. batch size (12–60) for a 175B-param GPT-3 model on 96 A100s. *Scatter/gather optimization* (orange) consistently outperforms *Unoptimized* (blue), reaching ~150 vs. ~130 teraFLOP/s/GPU at batch 60.

**Key takeaway:** Optimizations trade a small-batch penalty for large-batch scalability — recomputation trades ~33% throughput at small batches for ~2× gain at batch 256 by shrinking the pipeline bubble; scatter/gather yields a consistent ~11–15% speedup across batch sizes.

---

## Captions (verbatim)

**Figure 17:** Throughput (in sequences per second) with and without activation recomputation for a GPT model with 145 billion parameters using 128 A100 GPUs ((*t*, *p*) = (8, 16)).

**Figure 18:** Throughput per GPU with and without the scatter/gather optimization for a GPT model with 175 billion parameters using 96 A100 GPUs and the interleaved schedule.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.8) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-tab01.png]]
> [!quote] caption
> Weak-scaling throughput for GPT models ranging from 1 billion to 1 trillion parameters.

> [!tip] 表格解读（多模态）
> ## Figure Description

**Components & Data Flow:** The line chart plots **achieved teraFLOP/s per GPU** (y-axis, 50–200) against **number of GPUs** (x-axis, weak-scaling regime) for several GPT model sizes. Four series compare two partitioning strategies: **ZeRO-3** (blue: 175B dashed-circles, 530B solid-diamonds) and a parallel/PDS-style scheme (orange: solid squares and dashed triangles). Each line traces throughput as GPUs are added alongside parameter count growth from 1B → 1T.

**Key Takeaway:** ZeRO-3 throughput **degrades sharply with scale** (175B drops from ~145 → ~50 TFLOP/s/GPU), while the parallel strategy sustains **~150–170 TFLOP/s/GPU** across the same range — i.e., roughly **3× higher efficiency** at large model sizes, demonstrating better compute utilization under weak scaling.

*(104 words)*

---

## Caption (verbatim)

> **Table 1:** Weak-scaling throughput for GPT models ranging from 1 billion to 1 trillion parameters.

### Table 2 (p.9) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-tab02.png]]
> [!quote] caption
> Comparison of PTD Parallelism to ZeRO-3 (without model paralllelism). The 530-billion-parameter GPT model did not fit on 560 GPUs when using a microbatch size of 4 with ZeRO-3, so we increased the number of GPUs used to 640 and global batch size to 2560 to provide a throughput estimate (relevant row

> [!tip] 表格解读（多模态）
> ## Figure Description

The figure (Table 2) presents two side-by-side line plots benchmarking **PTD Parallelism vs. ZeRO-3** (without model parallelism) on a 530B-parameter GPT model, measuring **Achieved teraFLOP/s per GPU**.

**Components:**
- **Y-axis (both plots):** Achieved throughput in teraFLOP/s per GPU (range 0–200).
- **Left plot:** X-axis sweeps values 1, 2, 4, 8 (likely data-parallel degree); compares **Batch size 8** (blue) vs. **Batch size 128** (orange).
- **Right plot:** X-axis shows DP×MP-style tuples (2,32), (4,16), (8,8), (16,4), (32,2); compares **Batch size 32** (blue) vs. **Batch size 128** (orange).
- Each series uses markers (circles/diamonds) connected by lines.

**Key technical takeaway:** PTD Parallelism (orange) sustains ~150–175 teraFLOP/s/GPU across all configurations, while ZeRO-3 (blue) degrades sharply as the data-parallel dimension grows — dropping below 100 teraFLOP/s/GPU at degree 8 — demonstrating PTD's superior scalability at large batch sizes.

## Caption (verbatim)

> **Table 2:** Comparison of PTD Parallelism to ZeRO-3 (without model parallelism). The 530-billion-parameter GPT model did not fit on 560 GPUs when using a microbatch size of 4 with ZeRO-3, so we increased the number of GPUs used to 640 and global batch size to 2560 to provide a throughput estimate (relevant row marked in table with a *).

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
P = 12lh^2\left(1 + \dfrac{13}{12h}+\dfrac{V+s}{12lh}\right).
$$

$$
F=96Bslh^2\left(1 + \dfrac{s}{6h} + \dfrac{V}{16lh}\right).
$$

$$
\text{End-to-end training time} \approx \dfrac{8TP}{nX}.
$$

$$
[Y_1, Y_2]= [\textrm{GeLU}(XA_1), \textrm{GeLU}(XA_2)]. \nonumber
$$

$$
B=\begin{bmatrix} B_1 \\ B_2 \end{bmatrix}, \ Y = [Y_1, Y_2]. \nonumber
$$

$$
\left(b' / b + p - 1\right) \cdot \left(t_f(b) + t_b(b)\right).
$$

## 相关论文

- [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] — From ATOP to ZCube: Automated Topology Optimization Pipeline and A Highly Cost-Effective Network Topology for Large Model Training
- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey
- [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] — MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs
- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core

## 技术点深读（DEEP）

![[deep/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm.txt`（74320 字符）供引用检索。