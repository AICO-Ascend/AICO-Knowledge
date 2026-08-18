---
paper_num: "49"
title: "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism"
authors: "Model Parallelism Mohammad Shoeybi 1 2 Mostofa Patwary 1 2 Raul Puri 1 2 Patrick LeGresley 2 Jared Casper 2 Bryan Catanzaro 2"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/1909.08053"
pdf: "papers/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism.pdf"
slug: "megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism"
tags: [training]
---

# Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism

> [!abstract] 摘要（原文）
> 1\. 🚀 Megatron-LM 提出了一种简单高效的层内模型并行方法，通过在原生 PyTorch 中少量修改即可训练数十亿参数的 Transformer 模型。 2. 📈 该方法成功地将 Transformer 模型扩展到 8.3 亿参数，使用 512 个 GPU 实现了 15.1 PetaFLOPs 的可持续性能和 76% 的扩展效率，并与流水线并行互补。 3. 💡 研究还发现 BERT 模型中 Layer Normalization 的放置对模型扩展至关重要，并用 GPT-2 和 BERT 模型在 WikiText103、LAMBADA 和 RACE 等数据集上取得了 SOTA 结果。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Model Parallelism Mohammad Shoeybi 1 2 Mostofa Patwary 1 2 Raul Puri 1 2 Patrick LeGresley 2 Jared Casper 2 Bryan Catanzaro 2
- **arXiv**: https://arxiv.org/abs/1909.08053
- **本地 PDF**: `papers/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism.pdf`
- **页数**: 15

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p02.png]]
> [!quote] caption
> Model (blue) and model+data (green) parallel FLOPS as a function of number of GPUs. Model parallel (blue): up to 8-way model parallel weak scaling with approximately 1 billion parameters per GPU (e.g. 2 billion for 2 GPUs and 4 billion for 4 GPUs). Model+data parallel (green): similar conﬁguration as model parallel combined with 64-way data parallel. a baseline by training a model of 1.2 billion p

> [!tip] 技术解读（多模态）
> ## Figure 1 Description

**Components / Plot type:** A log–log scatter plot showing achieved throughput (PetaFLOPs per second, y-axis) versus cluster size (number of GPUs, x-axis, 1 → ~1000). Three series are plotted:
- **Blue dots — "model parallel":** weak-scaling run, up to ~8 GPUs, covering ≈1 → 8 billion total parameters (~1 B params/GPU).
- **Green dots — "model + data parallel":** the same per-GPU model partitioned 8-way, augmented with 64-way data parallelism, scaling from ~100 to ~500 GPUs.
- **Dashed line — "linear":** ideal linear-scaling reference.

**Data flow / trend:** Both series track the linear reference closely across roughly four orders of magnitude in GPU count, with the green series extending throughput from ~0.2 PFLOPs/s (model-only) up to ~15 PFLOPs/s at 512 GPUs.

**Key technical takeaway:** Combining intra-layer (tensor) model parallelism with data parallelism preserves near-linear weak-scaling, sustaining **15.1 PFLOPs/s (76% scaling efficiency)** on 512 GPUs when training an 8.3 B-parameter GPT-2 — a result unattainable by model parallelism alone, which saturates around 8 GPUs.

## Caption (verbatim)

*Figure 1.* Model (blue) and model+data (green) parallel FLOPS as a function of number of GPUs. Model parallel (blue): up to 8-way parallel weak scaling with approximately 1 billion parameters per GPU (e.g. 2 billion for 2 GPUs and 4 billion for 4 GPUs). Model+data parallel (green): similar configuration as model parallel combined with 64-way data parallel.

### Figure 2 (p.3) ⭐深度解读
![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p03.png]]
> [!quote] caption
> Transformer Architecture. Purple blocks correspond to fully connected layers. Each blue block represents a single trans- former layer that is replicated N times. and compute efﬁciency. The original transformer formula- tion was designed as a machine translation architecture that transforms an input sequence into another output sequence using two parts, an Encoder and Decoder. However, recent work 

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Architecture & Data Flow (Figure 2 — Transformer Architecture):**

The diagram depicts a single Transformer layer (blue block) that is replicated N× times (×L). Information flows bottom-up:

1. **Input stage:** Token/position embeddings → dropout
2. **Attention sub-block** (with residual "Add" around it):
   - Self-Attention & Attention Dropout → Dropout → Layer Norm
3. **MLP sub-block** (with residual "Add" around it):
   - MLP FC+IH → GeLU → MLP FC+IH → Dropout → Layer Norm
4. **Output stage:** Headed up to Output layer, Heads, and Loss

Purple blocks denote fully-connected layers; the blue enclosure marks one full transformer layer.

**Key Technical Takeaway:**
Megatron-LM uses a **pre-norm** configuration (LayerNorm applied *before* the attention/MLP sub-layers, *not* after as in the original Vaswani et al. 2017 design) combined with **GeLU** nonlinearities. This pre-norm arrangement is critical because it stabilizes gradients and enables training of multi-billion-parameter transformer models — something the original post-norm design struggles with at scale.

---

## Caption (Verbatim)

> **Figure 2.** Transformer Architecture. Purple blocks correspond to fully connected layers. Each blue block represents a single transformer layer that is replicated N times.

### Figure 3 (p.4) ⭐深度解读
![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p04.png]]
> [!quote] caption
> Blocks of Transformer with Model Parallelism. f and g are conjugate. f is an identity operator in the forward pass and all reduce in the backward pass while g is an all reduce in the forward pass and identity in the backward pass.

> [!tip] 技术解读（多模态）
> ## Description

The figure illustrates **Figure 3** of the Megatron-LM paper, showing how Transformer blocks are partitioned across GPUs using **model parallelism**.

**Panel (a) – MLP block:** Input *X* is replicated across workers via an identity **f** operator. The weight matrix *A = [A₁, A₂]* is split **column-wise**, so each GPU independently computes X·Aᵢ → GeLU → Yᵢ (removing a synchronization point inside GeLU). The second GEMM uses *B = [B₁, B₂]* split **row-wise**, consuming Yᵢ directly. Outputs are combined through a **g** operator (all-reduce in forward, identity in backward), then passed to Dropout → Z.

**Panel (b) – Self-Attention block:** *X* is again broadcast via *f*. Per-head parameters are partitioned column-wise: Q=[Q₁,Q₂], K=[K₁,K₂], V=[V₁,V₂], so each attention head's Q·K·V computation is **local to one GPU**. The subsequent output projection uses row-wise-split *B*, and *g* fuses the heads back together before Dropout.

**Key takeaway (≤120 words):**
By partitioning GEMMs along the *output* dimension of the first matmul and the *input* dimension of the second, Megatron eliminates the synchronization point inside GeLU and performs attention-head matmuls locally per GPU. Communication is reduced to **only two all-reduces per transformer layer** (one in each direction of the conjugate f/g pair, implemented as custom autograd Functions). This simple primitive-based approach requires no compiler/rewriting and scales efficiently for multi-billion-parameter training.

## Verbatim Caption

*Figure 3. Blocks of Transformer with Model Parallelism. f and g are conjugate. f is an identity operator in the forward pass and all reduce in the backward pass while g is an all reduce in the forward pass and identity in the backward pass.*

### Figure 4 (p.5) ⭐深度解读
![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p05.png]]
> [!quote] caption
> Communication operations in a transformer layer. There are 4 total communication operations in the forward and backward pass of a single model parallel transformer layer. contains a portion of the embedding table, an all-reduce (g operator) is required after the input embedding. For the output embedding, one approach is to perform the parallel GEMM [Y1, Y2] = [XE1, XE2] to obtain the logits, add a

> [!tip] 技术解读（多模态）
> ## Figure 4 Description

**Architecture & Components:** Figure 4 depicts a single model-parallel transformer layer with input X entering from the left and output Y exiting on the right. The pipeline contains: LayerNorm → Self-Attention (Q/K/V Linear + output Linear) → Dropout → residual add (+) → LayerNorm → MLP (Linear → GeLU → Linear) → Dropout → residual add (+). Two dashed regions mark the **Model Parallel** segments (self-attention and MLP), while LayerNorm, dropout, and residual additions are replicated locally on each GPU.

**Data Flow:** Activations flow left-to-right through the layer; residual arrows bypass each parallel block to the addition nodes.

**Key Technical Takeaway:** Megatron-LM avoids inter-GPU communication for LayerNorm, dropout, and residuals by **duplicating them on every GPU**, restricting all-reduce collectives to the boundaries of the parallel regions — yielding just 2 all-reduces per layer per direction (4 total across forward+backward), preserving compute-bound throughput without a custom compiler.

## Caption (Verbatim)

*Figure 4.* Communication operations in a transformer layer. There are 4 total communication operations in the forward and backward pass of a single model parallel transformer layer.

### Figure 5 (p.6) ⭐深度解读
![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p06.png]]
> [!quote] caption
> Model and model + data parallel weak scaling efﬁciency as a function of the number of GPUs. done by scaling the batch-size, however, this approach does not address training large models that do not ﬁt on a single GPU and it leads to training convergence degradation for large batch sizes. In contrast, here we use weak scaling to train larger models that were not possible otherwise. The baseline for

> [!tip] 技术解读（多模态）
> **Description of Main Figure (Figure 5):**

This is a grouped bar chart comparing **weak scaling efficiency** (Y-axis, 0–100%) across GPU counts (X-axis, log scale: 1, 2, 4, 8, …, 64, 128, 256, 512). Two series are shown:
- **Model Parallel** (blue bars): 1 GPU = 100%, 2 = 95%, 4 = 82%, 8 = 77%
- **Model + Data Parallel** (green bars): 64 = 96%, 128 = 83%, 256 = 79%, 512 = 74%

The chart contrasts pure model-parallel scaling (small GPU counts, up to 8 GPUs holding an 8.3B-parameter model) against hybrid model+data parallelism (scaling from 64 up to 512 GPUs on the 8.3B model).

**Key technical takeaway:** Megatron-LM sustains 74–77% weak-scaling efficiency even when expanding from 8 GPUs to 512 GPUs, demonstrating that model+data parallelism enables training multi-billion-parameter models that wouldn't otherwise fit on a single GPU, with only modest efficiency loss as the cluster grows.

**Caption (verbatim):**
*"Figure 5. Model and model + data parallel weak scaling efficiency as a function of the number of GPUs."*

### Figure 6 (p.7) ⭐深度解读
![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p07.png]]
> [!quote] caption
> Validation set perplexity. All language models are trained for 300k iterations. Larger language models converge notice- ably faster and converge to lower validation perplexities than their smaller counterparts.

> [!tip] 技术解读（多模态）
> ## Figure 6 Description

**Architecture/Components/Data Flow:**
Figure 6 is a line chart plotting **LM Perplexity** (y-axis, range 8–24) against **Iterations in thousands** (x-axis, 0–300). Three learning curves represent GPT-2 models at different scales, distinguished by color:
- **355M** (blue) — top curve, plateauing near ~16
- **2.5B** (red) — middle curve, plateauing near ~10
- **8.3B** (yellow/orange) — bottom curve, plateauing near ~9

All models share a single training pipeline (identical optimizer, batch schedule, and token budget), trained for 300k iterations; the only varying input is model capacity (parameters, layers, hidden size per Table 2).

**Key Technical Takeaway (≤120 words):**
Scaling GPT-2 yields monotonic improvements in both convergence *speed* and *final perplexity*. The 8.3B model reaches perplexities unattainable by smaller variants within the same iteration budget, while the 355M curve flattens earliest at the highest perplexity floor. This demonstrates that compute-optimal training favors larger models — bigger architectures leverage the fixed 300k-step budget more efficiently, achieving lower loss with no architectural or training-curve modification. (88 words)

## Caption (Verbatim)

> **Figure 6.** Validation set perplexity. All language models are trained for 300k iterations. Larger language models converge noticeably faster and converge to lower validation perplexities than their smaller counterparts.

### Figure 7 (p.8) ⭐深度解读
![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p08.png]]
> [!quote] caption
> Training loss for BERT model using the original architec- ture (a) and the rearranged architecture (b). Left ﬁgure shows the training loss for 336M and 752M BERT model. While the original architecture performs well on the 336M model, the modiﬁcations in (b) enable stable training with lower training loss.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Architecture diagrams (left):**
- **(a) Original BERT:** Input → LayerNorm → Self-Attention → (add residual) → LayerNorm → MLP → (add residual) → output — LayerNorm applied *before* each sub-layer.
- **(b) Rearranged:** Input → Self-Attention → (add residual) → LayerNorm → MLP → (add residual) → LayerNorm → output — LayerNorm moved *after* the residual connection.

**Loss plot (right):** Training loss vs. iterations (×1000) for three configurations:
- 🟧 336M using arch. (a) — converges stably
- 🟥 752M using arch. (a) — **diverges** (loss spikes near iteration ~200K)
- 🟦 752M using arch. (b) — trains stably with the lowest loss

**Key takeaway:** The position of LayerNorm matters critically for training stability — the original pre-norm arrangement fails at 752M scale, whereas moving LayerNorm post-residual enables stable training of larger BERT models.

## Caption (verbatim)

*Figure 7. Training loss for BERT model using the original architecture (a) and the rearranged architecture (b). Left figure shows the training loss for 336M and 752M BERT model. While the original architecture performs well on the 336M model, the modifications in (b) enable stable training with lower training loss.*

### Figure 8 (p.12) ⭐深度解读
![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p12.png]]
> [!quote] caption
> Grouping of GPUs for hybrid model and data parallelism with 8-way model parallel and 64-way data parallel. C. Text Samples

> [!tip] 技术解读（多模态）
> ## Figure Description

**Architecture/Components:**
The diagram illustrates a 2D grid of **512 GPUs** organized along two parallelism axes:
- **Model-parallel axis (horizontal/within-group):** 64 model-parallel groups, each containing 8 GPUs (e.g., GPU-1…GPU-8, GPU-9…GPU-16, …, GPU-505…GPU-512). Color coding differentiates the first GPU (yellow) from the remaining seven (pink) within each group.
- **Data-parallel axis (vertical/across-groups):** 8 data-parallel groups formed by selecting one GPU (same rank) from each of the 64 model-parallel groups — yielding the cross-cutting lines on the right labeled "data parallel group 1" and "data parallel group 8."

**Key Takeaway:** Hybrid parallelism decomposes the workload as **N_model × N_data = 64 × 8 = 512 GPUs**, where each GPU simultaneously participates in one intra-layer (tensor) group and one inter-layer replication group — enabling scaling beyond what either axis alone can support.

## Caption (verbatim)

*Figure 8.* Grouping of GPUs for hybrid model and data parallelism with 8-way model parallel and 64-way data parallel.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
Y = \textrm{GeLU}(XA)
$$

$$
X = [X_1, X_2], \ A=\begin{bmatrix} A_1 \\ A_2 \end{bmatrix}.
$$

$$
[Y_1, Y_2]= [\textrm{GeLU}(XA_1), \textrm{GeLU}(XA_2)]
$$

$$
PPL= \exp({-\frac{1}{T_o}\sum_{t}^{T} \text{log} P(t|0:t-1))}
$$

## 相关论文

- [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] — Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
- [[zero-memory-optimizations-toward-training-trillion-parameter-models]] — ZeRO: Memory Optimizations Toward Training Trillion Parameter Models
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core
- [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] — GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey
- [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] — MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs

## 技术点深读（DEEP）

![[deep/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism.txt`（68294 字符）供引用检索。