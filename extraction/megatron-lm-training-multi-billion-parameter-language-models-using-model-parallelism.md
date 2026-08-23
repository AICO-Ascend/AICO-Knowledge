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
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig01.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p02.png]]*
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
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig02.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p03.png]]*
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
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig03.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p04.png]]*
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
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig04.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p05.png]]*
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
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig05.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p06.png]]*
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
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig06.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p07.png]]*
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
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig07.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p08.png]]*
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
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig08.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p12.png]]*
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

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.6) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab01.png]]
> [!quote] caption
> Parameters used for scaling studies. Hidden size per atten-

> [!tip] 表格解读（多模态）
> **Description**

The figure presents a scaling study for BERT-like transformer models. **Table 1** enumerates four model configurations spanning 1.2B–8.3B parameters, sweeping hidden size (1536→3072), attention heads (16→32), and layers (40→72), with parallelism scaled accordingly (1→8 model-parallel GPUs, up to 512 model+data-parallel GPUs). Hidden size per attention head is held fixed at 96. The accompanying **bar chart** contrasts scaling efficiency (percentage on the y-axis) between pure *Model Parallel* (blue, 100/95/82/77%) and *Model + Data Parallel* (green, 96/83/79/74%) configurations, showing that combining model and data parallelism maintains competitive utilization as model size grows.

**Key takeaway**: Pure model parallelism preserves throughput more reliably at extreme scale, while model+data parallelism degrades faster as parameters increase from 1.2B to 8.3B, suggesting optimizer-state and communication overhead dominate at larger configurations.

**Caption (verbatim):**

*Table 1. Parameters used for scaling studies. Hidden size per attention head is kept constant at 96.*

### Table 2 (p.7) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab02.png]]
> [!quote] caption
> Model conﬁgurations used for GPT-2.

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**

The figure is a tabular specification (Table 2) summarizing three GPT-2 model variants — 355M, 2.5B, and 8.3B parameters — used in training experiments. Each row reports the number of transformer layers, hidden (embedding) dimension, number of attention heads, the per-head dimensionality (Hidden Size ÷ Attn Heads), the count of GPUs used for distributed training, and the resulting wall-clock time per epoch in days. The data flow is implicitly left-to-right: as the parameter count scales up (~24× from smallest to largest), depth grows from 24 → 72 layers, hidden size from 1024 → 3072, and attention heads from 16 → 24, while training time per epoch stays sub-3 days thanks to GPU parallelism scaling to 512 devices.

**Key takeaway:** Training cost (days/epoch) does not scale linearly with parameters, because distributed training across more GPUs keeps wall-clock time nearly constant.

**Caption (verbatim):**

*Table 2. Model configurations used for GPT-2.*

### Table 3 (p.7) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab03.png]]
> [!quote] caption
> Zero-shot results. SOTA are from ( Khandelwal et al. ,

> [!tip] 表格解读（多模态）
> **Description:**

Table 3 presents a zero-shot evaluation benchmark comparing three transformer language model scales (355M, 2.5B, 8.3B parameters) against prior state-of-the-art (SOTA). Each row reports two metrics: Wikitext103 Perplexity (lower is better) and LAMBADA Accuracy (higher is better). Results scale monotonically with model size—perplexity drops from 19.31 → 12.76 → 10.81, while accuracy climbs from 45.18% → 61.73% → 66.51%. The previous SOTA baselines (15.79 perplexity from Khandelwal et al.; 63.24% accuracy from Radford et al.) are shown in the bottom row for direct comparison.

**Key takeaway:** The 8.3B model surpasses prior SOTA on both benchmarks (≈31% perplexity reduction, ~3.3 absolute accuracy gain), confirming that scale alone—without task-specific fine-tuning—delivers state-of-the-art zero-shot performance.

**Caption (verbatim):**

> Table 3. Zero-shot results. SOTA are from (Khandelwal et al., 2019) for Wikitext103 and (Radford et al., 2019) for LAMBADA.

### Table 4 (p.7) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab04.png]]
> [!quote] caption
> Model conﬁgurations used for BERT. Parameter Layers Hidden Attention Total Count Size Heads GPUs 336M 24 1024 16 128 1.3B 24 2048 32 256 3.9B 48 2560 40 512

> [!tip] 表格解读（多模态）
> There is no figure present in the provided content — only **Table 4** and a paragraph of body text. I cannot describe an architecture diagram, components, or data flow that isn't shown.

What is provided:

**Table 4 (caption transcribed verbatim):**

> *Table 4.* Model configurations used for BERT.

| Parameter Count | Layers | Hidden Size | Attention Heads | Total GPUs |
|---|---|---|---|---|
| 336M | 24 | 1024 | 16 | 128 |
| 1.3B | 24 | 2048 | 32 | 256 |
| 3.9B | 48 | 2560 | 40 | 512 |

**Surrounding text excerpt:** The paragraph discusses dataset overlap statistics — noting "10.8% overlap," the LAMBADA test set (Paperno et al., 2016) with "at most 1.4% overlap," and the WikiText103 test set's "9.09% overlap with the WikiText103 training set" (Radford et al., 2019) — concluding that no test documents were inadvertently included in training data.

If you intended to share an architecture figure, please re-upload the image or provide its description, and I'll be happy to summarize it within the 120-word limit.

### Table 5 (p.8) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab05.png]]
> [!quote] caption
> Development set results for MNLI, QQP, SQuAD 1.1 and SQuAD 2.0 and test set results for RACE. The trained tokens represents

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**

The table benchmarks several pretrained transformer language models across five downstream NLP tasks (MNLI, QQP, SQuAD 1.1, SQuAD 2.0, and RACE), with metrics including accuracy, F1, and Exact Match (EM). It compares RoBERTa, ALBERT, XLNet, and three Megatron variants (336M, 1.3B, 3.9B parameters), plus two ensembles. A "trained tokens ratio" column normalizes compute budget against the 336M Megatron baseline, isolating the effect of model scale.

**Key takeaway:** Megatron-3.9B matches or exceeds every prior single-model result (e.g., 91.4 MNLI, 95.5/90.0 SQuAD 1.1, 91.2/88.5 SQuAD 2.0, 89.5 RACE) under the same token budget, and its ensemble (95.8/90.5, 91.7/89.0, 90.9) surpasses the ALBERT ensemble — showing that parameter scaling, not just training tokens, drives state-of-the-art gains.

**Caption (verbatim):**

Table 5. Development set results for MNLI, QQP, SQuAD 1.1 and SQuAD 2.0 and test set results for RACE. The trained tokens represents consumed tokens during model pretraining (proportional to batch size times number of iterations) normalized by consumed tokens during model pretraining for our 336M model.

### Table 6 (p.11) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab06.png]]
> [!quote] caption
> presents the hyperparameters used for each model and task during ﬁnetuning.

> [!tip] 表格解读（多模态）
> # Description

**No figure is present in this image.** The page contains only textual content: a list of bibliography/references entries (Vaswani et al. on Attention/Transformers, GLUE benchmark, XLNet, large-batch CNN training, BERT training optimization, Defending Against Neural Fake News, and Aligning Books and Movies), followed by an **appendix section header** "A. BERT Finetuning Hyperparameters."

There are no architecture diagrams, components, data-flow illustrations, or tables visible — only references and the introductory sentence to an appendix.

**Key technical takeaway (limited):** The page itself implies the upcoming Table 6 catalogs per-task BERT finetuning hyperparameters (likely batch size, learning rate, epochs), but without the actual table, no concrete numerical/architectural detail can be reported.

# Verbatim transcription of the caption/title text

> **A. BERT Finetuning Hyperparameters**
>
> Table 6 presents the hyperparameters used for each model and task during finetuning.

(All other text on the page consists of BibTeX-style bibliography entries, not a figure caption.)

### Table 7 (p.15) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab07.png]]
> [!quote] caption
> Effect of number of attention heads on scaling on 8.3

> [!tip] 表格解读（多模态）
> **Description**

The image is a table (Table 7), not a diagrammatic figure, so it contains no architecture/component/data-flow schematic. Instead, it presents a 3-column, 4-row empirical comparison of attention-head configurations on a fixed 8.3B-parameter model using 8-way model parallelism.

- **Columns:** Attention heads · Hidden size per head · Scaling Efficiency
- **Rows (heads / hidden-per-head / efficiency):** 16 / 192 / 82% · 24 / 128 / 80% · 32 / 96 / 77%
- **Structure:** A double horizontal rule separates the header and footer, with a single rule under the header row; the product of heads × hidden size is held roughly constant (~3072), isolating the effect of head count.

**Key technical takeaway (≤120 words):** Increasing the number of attention heads while proportionally shrinking the per-head hidden dimension degrades scaling efficiency on an 8.3B-parameter model with 8-way parallelism. Going from 16 to 32 heads (192→96 hidden/head) costs 5 percentage points of efficiency (82%→77%). This implies that, at this scale, fine-grained head partitioning pays an overhead—likely communication/synchronization costs across parallelism ranks—that outweighs benefits from finer-grained attention decomposition. The result suggests a practical sweet spot around 16–24 heads per layer for efficiently training multi-billion-parameter transformers under tensor/model parallelism.

**Caption (verbatim):** *Table 7. Effect of number of attention heads on scaling on 8.3 billion of parameters with 8-way model parallelism.*

### Table 8 (p.15) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab08.png]]
> [!quote] caption
> Speedup obtained for the 1.2 billion parameters model

> [!tip] 表格解读（多模态）
> # Description of Table 8

Table 8 reports empirical speedup measurements for a **1.2-billion-parameter** language model trained with **model parallelism** while holding the per-iteration batch size constant at **8 samples**.

## Components Shown
- **Columns (input axis):** Number of GPUs ∈ {1, 2, 4, 8}
- **Rows (output axis):** Speedup factor (normalized to single-GPU baseline)
- **Data values:** 1.0 → 1.64 → 2.34 → 2.98

## Data Flow / Reading
Single-GPU run is the reference (1.0×). Adding GPUs theoretically multiplies compute, but reported speedup grows sub-linearly (1.64×, 2.34×, 2.98× — never reaching 2×, 4×, or 8×).

## Key Technical Takeaway
Speedup exhibits **diminishing returns**: a second GPU yields ~64% wall-clock reduction, but beyond that, communication and per-GPU memory-bandwidth overhead dominate, so 8 GPUs deliver only ~3× rather than the ideal 8×. This quantifies the scaling ceiling of naive model parallelism.

---

## Caption (Verbatim Transcription)

*Table 8. Speedup obtained for the 1.2 billion parameters model using model parallelism while keeping the batch size constant.*

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