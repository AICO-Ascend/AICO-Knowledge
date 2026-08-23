---
paper_num: "63"
title: "Kimi Linear: An Expressive, Efficient Attention Architecture"
authors: ""
date: "2025/10/30"
arxiv: "https://arxiv.org/abs/2510.26692"
pdf: "papers/kimi-linear-an-expressive-efficient-attention-architecture.pdf"
slug: "kimi-linear-an-expressive-efficient-attention-architecture"
tags: []
---

# Kimi Linear: An Expressive, Efficient Attention Architecture

> [!abstract] 摘要（原文）
> We introduce Kimi Linear, a hybrid linear attention architecture that, for the first time, outperforms full attention under fair comparisons across various scenarios -- including short-context, long-context, and reinforcement learning (RL) scaling regimes. At its core lies Kimi Delta Attention (KDA), an expressive linear attention module that extends Gated DeltaNet with a finer-grained gating mechanism, enabling more effective use of limited finite-state RNN memory. Our bespoke chunkwise algorithm achieves high hardware efficiency through a specialized variant of the Diagonal-Plus-Low-Rank (DPLR) transition matrices, which substantially reduces computation compared to the general DPLR formulation while remaining more consistent with the classical delta rule. We pretrain a Kimi Linear model with 3B activated parameters and 48B total parameters, based on a layerwise hybrid of KDA and Multi-Head Latent Attention (MLA). Our experiments show that with an identical training recipe, Kimi Linear outperforms full MLA with a sizeable margin across all evaluated tasks, while reducing KV cache usage by up to 75% and achieving up to 6 times decoding throughput for a 1M context. These results demonstrate that Kimi Linear can be a drop-in replacement for full attention architectures with superior performance and efficiency, including tasks with longer input and output lengths. To support further research, we open-source the KDA kernel and vLLM implementations, and release the pre-trained and instruction-tuned model checkpoints.

## 元信息
- **发表日期**: 2025/10/30
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2510.26692
- **本地 PDF**: `papers/kimi-linear-an-expressive-efficient-attention-architecture.pdf`
- **页数**: 28

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig01.png]]
*整页渲染: ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p01.png]]*
> [!quote] caption
> (a) Performance vs. acceleration. With strict fair comparisons with 1.4T training tokens, on MMLU-Pro (4k context length, red stars), Kimi Linear leads performance (51.0) at similar speed. On RULER (128k context length, blue circles), it is Pareto-optimal, achieving top performance (84.3) and 3.98× acceleration. (b) Time per output token (TPOT) vs. decoding length. Kimi Linear (blue line) maintain

> [!tip] 技术解读（多模态）
> ## Figure 1 Description

**Panel (a) — Performance vs. Acceleration:** A scatter plot with decoding acceleration (1×–4×) on the x-axis and performance (45–60 / 50–90 dual scale) on the y-axis. Blue circles plot RULER-128k scores (Kimi Linear 84.3, MLA 81.3, GDN-H 80.5); red stars plot MMLU-Pro-4k scores (Kimi Linear 51.0, GDN-H 47.9, MLA 47.2). A dashed Pareto-frontier curve shows Kimi Linear dominates at long context.

**Panel (b) — TPOT vs. Decoding Length:** Line plot of time-per-output-token (ms) from 4K to 1M tokens. MLA (teal dashed) and GDN-H (orange dashed) curve steeply upward, while Kimi Linear (purple solid) stays nearly flat, with annotations of 4.8×, 5.7×, and 6.3× speedups over MLA at 512K, 1M, and beyond.

**Key takeaway:** Kimi Linear breaks the linear-attention performance ceiling—matching full-attention quality while delivering up to 6.3× decoding speedup at 1M tokens via chunkwise DPLR transition matrices.

## Caption (verbatim)

Figure 1: (a) Performance vs. acceleration. With strict fair comparisons with 1.4T training tokens, on MMLU-Pro (4k context length, red stars), Kimi Linear leads performance (51.0) at similar speed. On RULER (128k context length, blue circles), it is Pareto-optimal, achieving top performance (84.3) and 3.98× acceleration. (b) Time per output token (TPOT) vs. decoding length. Kimi Linear (blue line) maintains a low TPOT, matching GDN-H and outperforming MLA at long sequences. This enables larger batches, yielding a 6.3× faster TPOT (1.84ms vs. 11.48ms) than MLA at 1M tokens.

### Figure 2 (p.5) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig02.png]]
*整页渲染: ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p05.png]]*
> [!quote] caption
> Execution time of kernels for vary- ing input lengths, with a uniform batch size of 1 and 16 heads.

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 2) — Description:**

The figure is a line plot comparing kernel execution time (ms, y-axis, 0–64) against input length (x-axis, 2K→64K) for two attention implementations: **DPLR** (teal dashed line) and **KDA (ours)** (solid blue line). Both curves start near 0 ms at 2K. DPLR grows approximately exponentially, climbing steeply past ~48 ms by 64K. KDA remains nearly flat across 2K–32K (~0–8 ms) and only rises to ~30 ms at 64K, consistently sitting below DPLR. Conditions: batch size = 1, 16 heads.

**Key Technical Takeaway:** KDA eliminates the second-level chunk matmuls of DPLR (Equation 9) by binding decay variables **a**, **b** into **k**, dropping four chunk matmuls to two and yielding ~2× kernel speedup, with the gap widening at long sequences (64K).

**Caption (verbatim):**
> Figure 2: Execution time of kernels for varying input lengths, with a uniform batch size of 1 and 16 heads.

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig03.png]]
*整页渲染: ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p05.png]]*
> [!quote] caption
> Neural Parameterization

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 2) — Description:**

The figure is a line plot comparing kernel execution time (ms, y-axis, 0–64) against input length (x-axis, 2K→64K) for two attention implementations: **DPLR** (teal dashed line) and **KDA (ours)** (solid blue line). Both curves start near 0 ms at 2K. DPLR grows approximately exponentially, climbing steeply past ~48 ms by 64K. KDA remains nearly flat across 2K–32K (~0–8 ms) and only rises to ~30 ms at 64K, consistently sitting below DPLR. Conditions: batch size = 1, 16 heads.

**Key Technical Takeaway:** KDA eliminates the second-level chunk matmuls of DPLR (Equation 9) by binding decay variables **a**, **b** into **k**, dropping four chunk matmuls to two and yielding ~2× kernel speedup, with the gap widening at long sequences (64K).

**Caption (verbatim):**
> Figure 2: Execution time of kernels for varying input lengths, with a uniform batch size of 1 and 16 heads.

### Figure 4 (p.7) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig04.png]]
*整页渲染: ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p07.png]]*
> [!quote] caption
> Results on synthetic tasks: palindrome, multi query associative recall, and the state tracking.

> [!tip] 技术解读（多模态）
> **Figure description (≤120 words):**

Figure 4 is a 2×3 grid comparing three linear-attention models—**KDA** (solid blue, circles), **GDN** (dashed teal, stars), and **Mamba2** (dashed orange, triangles)—on three synthetic tasks: Palindrome, MQAR, and Stack. The **top row** plots peak Accuracy (%) versus sequence length (256–2048 tokens), revealing that KDA and GDN maintain near-perfect accuracy at short lengths while Mamba2 collapses to 0% beyond 512 tokens on Palindrome and Stack. The **bottom row** plots Accuracy versus training steps (0–20K) at fixed 1,024-token context, showing KDA converges fastest (≈5K steps) and Mamba2 fails entirely. **Key takeaway:** KDA is the only method that simultaneously achieves fast convergence and robustness to long context across all three copying/recall benchmarks, outperforming both GDN (slower convergence, accuracy drop at 2048) and Mamba2 (fails on state-tracking tasks).

**Caption (verbatim):**

Figure 4: Results on synthetic tasks: palindrome, multi query associative recall, and the state tracking.

### Figure 5 (p.9) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig05.png]]
*整页渲染: ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p09.png]]*
> [!quote] caption
> The fitted scaling law curves for MLA and Kimi Linear. balanced positional bias across layers, which improves robustness and extrapolation at long ranges, leading to stronger long-context performance. Regarding long context performance, as shown in Table 5, Kimi Linear achieves the best average score across different long context benchmarks, which verifies the benefits we claim in the last section

> [!tip] 技术解读（多模态）
> **Figure 5 Description:**

The figure is a log-log scatter plot comparing two fitted scaling-law curves over five MoE model checkpoints (sized 653M–1.7B activated parameters, per Table 2). It plots **Loss (y-axis)** against **PFLOP/s-days** (compute, x-axis).

**Components / data flow:**
- **Blue dashed curve (MLA baseline):** 2.3092 × C^(−0.0536), with blue star markers at each model size.
- **Red dashed curve (Kimi Linear):** 2.2879 × C^(−0.0527), with red star markers.
- Both curves descend monotonically as compute increases; the red curve lies consistently below the blue.
- A double-headed arrow annotated **"1.16×"** between the two curves in the mid-range (≈10 PFLOP/s-days) highlights the horizontal compute gap at equal loss.

**Key takeaway (≤120 words):**
At iso-loss, Kimi Linear reaches the same training loss using ~1.16× less compute than the MLA baseline — a measurable, architecture-level efficiency gain rather than a tuning artifact. Because the two curves stay roughly parallel (similar exponents −0.0527 vs −0.0536), the advantage holds across scales from 653M to 1.7B activated params and from 38.8B to 128B training tokens, suggesting the gain transfers to larger compute budgets.

**Caption verbatim:**
"Figure 5: The fitted scaling law curves for MLA and Kimi Linear."

### Figure 6 (p.12) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig06.png]]
*整页渲染: ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p12.png]]*
> [!quote] caption
> The training and test accuracy curves for Kimi Linear@1.4T and MLA@1.4T during Math RL training. Kimi Linear consistently outperforms the full attention baseline by a sizable margin during the whole RL process.

> [!tip] 技术解读（多模态）
> **Figure Description (≤120 words):**

The figure contains three line-plot panels comparing **MLA@1.4T** (dashed green) against **Kimi Linear@1.4T** (solid purple) during Math RL training:

- **(a)** Training accuracy vs. training steps (y-axis: 20–65). Kimi Linear's accuracy curve rises more steeply and stays consistently above MLA from ~step 20 onward.
- **(b)** Accuracy on the **MATH 500** test set (y-axis: 70–94). Kimi Linear tracks above MLA across the full trajectory with similar fluctuation patterns.
- **(c)** Accuracy on **AIME 2025** (y-axis: 10–25). The largest relative gap appears here, with Kimi Linear reaching ~22% vs MLA's ~19%.

All curves share a comparable x-axis range (~0–110). Data flow: training-progress → per-checkpoint evaluation → plotted accuracy points.

**Key takeaway:** Kimi Linear exhibits faster convergence and a widening accuracy gap over full-attention MLA throughout RL, indicating that linearized attention improves optimization dynamics for reasoning-intensive long sequences.

**Caption verbatim:**
*Figure 6: The training and test accuracy curves for Kimi Linear@1.4T and MLA@1.4T during Math RL training. Kimi Linear consistently outperforms the full attention baseline by a sizable margin during the whole RL process.*

### Figure 7 (p.13) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig07.png]]
*整页渲染: ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p13.png]]*
> [!quote] caption
> (a) The prefilling time of MLA (full attention), hybrid GDN-H and our Kimi Linear. (b) The time per output token (TPOT) for MLA, GDN-H and Kimi Linear during decoding. (We use batch size = 1 here for tests.) performance curves are virtually indistinguishable, confirming that our method maintains high efficiency. The hybrid

> [!tip] 技术解读（多模态）
> **Description:**

The figure (Figure 7) presents two side-by-side line plots comparing latency performance across three attention architectures—MLA (full attention, dashed teal), hybrid GDN-H (orange), and Kimi Linear (purple)—as a function of sequence length (4K → 1M tokens, log-scale x-axis).

- **Subplot (a)** plots Prefilling Latency (s, y: 0–60+). MLA's curve rises steeply at long contexts (~65 s at 1M), while Kimi Linear and GDN-H remain near-flat (~22 s). Annotated speedups: **2.6×** (512K) and **2.9×** (1M).
- **Subplot (b)** plots TPOT (ms, y: 5–15) during decoding. MLA reaches ~17 ms at 1M; Kimi Linear stays at ~8 ms. Annotated speedups: **1.8×** (512K) and **2.2×** (1M).

**Data flow:** context length → measured wall-clock latency → plotted per architecture.

**Key takeaway:** Kimi Linear matches MLA at short contexts (<16K) but scales far better, achieving 2.9× prefill and 2.2× decode speedups at 1M tokens with batch size 1.

**Caption (verbatim):**
"Figure 7: (a) The prefilling time of MLA (full attention), hybrid GDN-H and our Kimi Linear. (b) The time per output token (TPOT) for MLA, GDN-H and Kimi Linear during decoding. (We use batch size = 1 here for tests.)"

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.8) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab01.png]]
> [!quote] caption
> Ablation study on the hybrid ratio of KDA to MLA attention and other key components. We list the training and validation perplexities (lower is better) for comparison. The best-performing model, used in our final experiments, is highlighted in gray.

> [!tip] 表格解读（多模态）
> **Figure description (Table 1):**
Table 1 is an ablation study comparing configurations of a hybrid KDA/MLA attention model. Two metrics are reported—training perplexity (PPL) and validation PPL, with arrows indicating "lower is better." The top block sweeps the **Hybrid ratio** (KDA:MLA) at {3:1, 0:1, 1:1, 7:1, 15:1}. The 3:1 ratio is highlighted in gray as the best (Training PPL = 9.23, Validation PPL = 5.65). A lower block ablations component choices: removing the output gate (9.25 / 5.67), using a Swish output gate (9.43 / 5.81), and removing the convolution layer (9.29 / 5.70). (98 words)

**Key takeaway:** A 3:1 KDA-to-MLA hybrid ratio is optimal; replacing the dedicated output gate with Swish degrades validation PPL most (+0.16), while the convolution layer contributes marginally.

**Caption (verbatim):**
"Table 1: Ablation study on the hybrid ratio of KDA to MLA attention and other key components. We list the training and validation perplexities (lower is better) for comparison. The best-performing model, used in our final experiments, is highlighted in gray."

### Table 2 (p.9) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab02.png]]
> [!quote] caption
> Model configurations and hyperparameters for scaling law experiments.

> [!tip] 表格解读（多模态）
> ## Main Figure Description

The bottom panel is a **log–log scaling-law plot** of validation loss (y-axis, ≈2.00–2.25) against activated-parameter count C (x-axis, log scale around 10¹). Star markers denote empirical measurements for five MoE configurations from Table 2 (653M → 1.7B activated params), with two power-law fits overlaid: **MLA** (blue dashed, 2.3092·C⁻⁰·⁰⁵³⁶) and **Kimi Linear** (red dashed, 2.2879·C⁻⁰·⁰⁵²⁷). A double-arrow annotation labelled "**1.16×**" highlights the constant loss-equivalent parameter-efficiency gap, meaning Kimi Linear matches MLA's loss with ≈1.16× fewer activated parameters across scales.

**Key takeaway:** Both attention variants exhibit nearly identical scaling exponents (~−0.053), indicating that the MoE architecture — not the attention kernel — governs loss-vs-compute behavior; switching to linear attention yields a flat, constant multiplicative compute savings at every scale tested.

## Caption (verbatim)

> **Table 2:** Model configurations and hyperparameters for scaling law experiments.
>
> [Column headers: # Act. Params.† | Head | Layer | Hidden | Tokens | lr | batch size‡]
>
> 653M | 16 | 16 | 1216 | 38.8B | 2.006 × 10⁻³ | 336
> 878M | 18 | 18 | 1376 | 59.8B | 1.790 × 10⁻³ | 432
> 1.1B | 20 | 20 | 1536 | 85.2B | 1.617 × 10⁻³ | 512
> 1.4B | 22 | 22 | 1632 | 102.5B | 1.486 × 10⁻³ | 576
> 1.7B | 24 | 24 | 1776 | 128.0B | 1.371 × 10⁻³ | 640
>
> † Denotes the number of activated parameters in our MoE models, excluding embeddings.
> ‡ All models were trained with a context length of 4,096.

### Table 3 (p.11) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab03.png]]
> [!quote] caption
> Performance comparison of Kimi Linear with the full-attention MLA baseline and the hybrid GDN baseline, all after the same pretraining recipe. Kimi Linear consistently outperforms both MLA and GDN-H on short-context pretrain evaluations. Best per-column results are bolded .

> [!tip] 表格解读（多模态）
> ## Description

The image is a **performance comparison table** (Table 3), not a figure. It contrasts three model variants — **MLA** (full-attention baseline), **GDN-H** (hybrid GDN baseline), and **Kimi Linear** — all trained on **1.4T tokens** under the same recipe. Results are grouped into three capability buckets: *General* (HellaSwag, ARC-challenge, Winogrande, BBH, MMLU, MMLU-Pro, TriviaQA), *Math & Code* (GSM8K, MATH, EvalPlus, CRUXEval-I/O-cot), and *Chinese* (CEval, CMMLU). Best per-row scores are **bolded**.

**Key takeaway:** Kimi Linear wins **12 of 14** short-context benchmarks, matching MLA only on MATH (54.7) and losing to GDN-H solely on EvalPlus (60.2 vs 63.1) — evidencing that linear attention is a competitive, often superior drop-in for full attention at matched compute. (85 words)

## Caption (verbatim)

> **Table 3:** Performance comparison of Kimi Linear with the full-attention MLA baseline and the hybrid GDN baseline, all after the same pretraining recipe. Kimi Linear consistently outperforms both MLA and GDN-H on short-context pretrain evaluations. Best per-column results are **bolded**.

### Table 4 (p.11) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab04.png]]
> [!quote] caption
> Performance comparison of Kimi Linear with the full-attention MLA baseline and the hybrid GDN baseline, all using the same SFT recipe after pretraining. Kimi Linear consistently outperforms both MLA and GDN-H on short-context instruction-tuned benchmarks. Best per-column results are bolded .

> [!tip] 表格解读（多模态）
> **Description:**

This is **Table 4** (a benchmark comparison, not an architecture diagram). It tabulates post-SFT accuracy/numerical scores across three attention mechanisms — **MLA** (full attention baseline), **GDN-H** (hybrid Gated DeltaNet baseline), and **Kimi Linear** — all trained on the same 1.4T tokens with an identical SFT recipe. Results are split into two benchmark families: *General* (BBH, MMLU variants, GPQA-Diamond, LiveBench) and *Math & Code* (AIME 2025, MATH500, HMMT 2025, PolyMath-en, LiveCodeBench v6, EvalPlus). Best per-row values are bolded.

**Key takeaway:** Kimi Linear's linear-attention design *matches or beats* both full attention (MLA) and the hybrid GDN-H across the board — most decisively on math/code reasoning (AIME, HMMT, PolyMath, LiveCodeBench) — showing that a well-tuned linear kernel need not sacrifice instruction-tuned downstream quality versus quadratic attention. (~88 words)

**Caption (verbatim):**

"Table 4: Performance comparison of Kimi Linear with the full-attention MLA baseline and the hybrid GDN baseline, all using the same SFT recipe after pretraining. Kimi Linear consistently outperforms both MLA and GDN-H on short-context instruction-tuned benchmarks. Best per-column results are **bolded**."

### Table 5 (p.12) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab05.png]]
> [!quote] caption
> Comparisons of Kimi Linear with MLA, GDN-H, and Kimi Linear (RoPE) across long-context benchmarks. The last column reports the overall average ( ↑ ). All models is trained on 1.4T tokens. Best per-column results are bolded .

> [!tip] 表格解读（多模态）
> **Description of the main figure (Table 5 + companion line plots):**

The table benchmarks four attention mechanisms—MLA, GDN-H, Kimi Linear (RoPE), and the full Kimi Linear—across eight long-context evaluations (RULER, MRCR, HELMET-ICL, LongBench V2, Frames, RepoQA, and Long Code Arena split into Lib/Commit), with all models matched at 1.4T training tokens. The three line plots below it track MLA versus Kimi Linear across scales, with Kimi Linear consistently trending above MLA.

**Key technical takeaway (≤120 words):** Kimi Linear attains the highest overall average (54.5) versus MLA (52.2), GDN-H (51.2), and its RoPE ablation (51.8), claiming the best score on 5/8 benchmarks—particularly memory-retrieval tasks (RULER 84.3, MRCR 29.6, HELMET-ICL 90.0) and code retrieval (Lib 37.1). The scaling plots show Kimi Linear's advantage widening at larger compute, indicating that the linear-attention design—rather than the positional encoding—is the dominant driver of long-context gains, while maintaining strong performance on math/logic benchmarks where MLA and GDN-H lead.

**Caption (verbatim):**

Table 5: Comparisons of Kimi Linear with MLA, GDN-H, and Kimi Linear (RoPE) across long-context benchmarks. The last column reports the overall average (↑). All models is trained on 1.4T tokens. Best per-column results are **bolded**.

### Table 6 (p.14) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab06.png]]
> [!quote] caption
> An overview of attention mechanisms in their mathematically equivalent recurrent ( o t ) and parallel ( O ) forms. We omitted the normalization term and β t to achieve a more concise representation. The function ϕ refers to the infinite-dimensional feature space corresponding to the exponential kern

> [!tip] 表格解读（多模态）
> **Description of the main figure (Table 6):**

The table presents Self-Attention (SA) in two mathematically equivalent forms side-by-side. In the **recurrent form**, the output at time step $t$ is computed as $\boldsymbol{o}_t = \sum_{j=1}^{t} \exp(\boldsymbol{q}_t^\top \boldsymbol{k}_j)\boldsymbol{v}_j$, summing over previous positions sequentially using query ($\boldsymbol{q}$), key ($\boldsymbol{k}$), and value ($\boldsymbol{v}$) vectors. In the **parallel form**, the same operation is vectorized as $\boldsymbol{O} = (\exp(\boldsymbol{Q}\boldsymbol{K}^\top) \odot \boldsymbol{M})\boldsymbol{V}$, where $\boldsymbol{M}$ serves as the causal mask restricting attention to past tokens, and $\odot$ denotes element-wise (Hadamard) multiplication. The framework leverages the exponential kernel trick $\phi(\boldsymbol{q})^\top\phi(\boldsymbol{k}) = \exp(\boldsymbol{q}^\top\boldsymbol{k})$ via an infinite-dimensional feature map $\phi$.

**Key takeaway:** Recurrent and parallel attention formulations are mathematically equivalent—the recurrent view enables O(1) inference memory via KV-caching, while the parallel form enables O(n²) but GPU-friendly training, with mask $\boldsymbol{M}$ preserving causality in both.

**Caption (verbatim):**

Table 6: An overview of attention mechanisms in their mathematically equivalent recurrent ($\boldsymbol{o}_t$) and parallel ($\boldsymbol{O}$) forms. We omitted the normalization term and $\beta_t$ to achieve a more concise representation. The function $\phi$ refers to the infinite-dimensional feature space corresponding to the exponential kernel, i.e., $\phi(\boldsymbol{q})^\top\phi(\boldsymbol{k}) = \exp(\boldsymbol{q}^\top\boldsymbol{k})$.

### Table 7 (p.16) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab07.png]]
> [!quote] caption
> An overview of different attention mechanisms through the lens of state updating rules and their learning objective under the TTT framework [ 90 ]. We ignore all normalizer terms and activation/kernel functions for brevity.

> [!tip] 表格解读（多模态）
> ## Description of the Main Table

This **table** (not a figure) presents a unified comparison of five sequence-modeling mechanisms (LA, RetNet, Mamba2, GLA, HGRN2) recast through the **Test-Time Training (TTT)** lens. It is organized into three columns:

- **Column 1 — Model name & reference** (the five attention variants).
- **Column 2 — Objective ℒ**, expressed as a combination of a key–value inner-product term and a magnitude regularizer on the hidden state **S** (e.g., a Frobenius-norm penalty with scalar, scalar-per-step, or diagonal gating via √(1−α)).
- **Column 3 — Update rule S_t = S_{t−1} − ∇_{S_{t−1}} ℒ**, showing each model's recurrent state transition closed-form.

**Key technical takeaway:** Every modern linear/state-space attention variant is equivalent to **one gradient-descent step of a single TTT-style loss**, differing only in *how* the regularization term gates the previous state (none, scalar decay α, or diagonal vector 1−α_t). This recasts diverse architectures as special cases of an implicit optimization procedure, enabling end-to-end learning of the optimizer itself. (~98 words)

## Caption (Verbatim Transcription)

**Table 7:** An overview of different attention mechanisms through the lens of state updating rules and their learning objective under the TTT framework [90]. We ignore all normalizer terms and activation/kernel functions for brevity.

### Table 8 (p.28) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab08.png]]
> [!quote] caption
> Performance of Kimi-Linear-Base and Moonlight-Base across diverse tasks.

> [!tip] 表格解读（多模态）
> The visible content shows **Section D of the Kimi Linear technical report**, not an architectural diagram. It presents text-based results rather than a figure with components/data flow. The section describes training Kimi Linear on a 5.7T token dataset with 3× sparsity, comparing it against Moonlight.

**Key technical takeaway:** Kimi Linear@5.7T achieves 94.8 on RULER at 1M context length, outperforming Moonlight (which couldn't be evaluated beyond its 8K limit, shown as "-") across nearly all benchmarks, validating it as a viable, more efficient alternative to full attention.

**Caption (verbatim):**
"Table 8: Performance of Kimi-Linear-Base and Moonlight-Base across diverse tasks."

*Note:* The actual table data (benchmark scores, columns, rows) is not visible in the provided image snippet — only the caption and surrounding paragraph are shown. If you need a description of the table's contents, please share the image containing the table itself.

### Table 9 (p.28) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab09.png]]
> [!quote] caption
> Performance of Kimi-Linear-Instruct and Moonlight-Instruct across diverse tasks.

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**
Table 8 is a benchmark comparison matrix contrasting two MoE language models—Kimi-Linear-Base and Moonlight-Base—across four evaluation domains: General (6 tasks), Math (4 tasks), Code (4 tasks), and Chinese (2 tasks). Columns report per-task scores with consistent few-shot settings (5-, 4-, 8-, 6-, 0-, 1-shot variants). Both models share 3B activated params, MoE architecture, and 5.7T training tokens, but Kimi-Linear-Base has 3× the total parameters (48B vs. 16B) and a redesigned attention mechanism with 3× sparsity. Kimi-Linear-Base dominates every row—e.g., MATH (58.5 vs 45.3), GSM8k (86.3 vs 77.2), CRUXEval-O (67.0 vs 46.6), and C-Eval (83.3 vs 77.6). **Key takeaway:** sparsity-driven linear attention matches or beats dense attention at substantially larger total capacity while keeping the activated compute budget constant.

**Caption (verbatim):**
Table 8: Performance of Kimi-Linear-Base and Moonlight-Base across diverse tasks.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf{S}_t = \left(\mathbf{I}-\beta_t\bm{k}_{t}\bm{k}_{t}^{\top}\right)\brickred{\operatorname{Diag}\left(\bm{\alpha}_t \right)}\mathbf{S}_{t-1} + \beta_t\bm{k}_{t}\bm{v}_{t}^{\top}\in\mathbb{R}^{d_k\times d_v}; \qquad \bm{o}_t = \mathbf{S}^\top_t \bm{q}_t\in\mathbb{R}^{d_v}
$$

$$
\begin{aligned} \mathbf{S}_{[t]}^r & = \underbrace{\left(\prod_{i=1}^r \left(\mathbf{I} - \beta_{[t]}^i \boldsymbol{k}_{[t]}^i \boldsymbol{k}_{[t]}^{i\top}\right) \brickred{\operatorname{Diag}(\boldsymbol{\alpha}_{[t]}^i)}\right)}_{:= \mathbf{P}_{[t]}^r} \cdot\mathbf{S}_{[t]}^{0} + \underbrace{\sum_{i=1}^{r} \left(\prod_{j=i+1}^r \left(\mathbf{I} - \beta_{[t]}^j \boldsymbol{k}_{[t]}^j \boldsymbol{k}_{[t]}^{j\top}\right)\brickred{\operatorname{Diag}(\boldsymbol{\alpha}_{[t]}^j)}\right)\cdot\beta_{[t]}^i \boldsymbol{k}_{[t]}^i\boldsymbol{v}_{[t]}^{i\top}}_{:=\mathbf{H}_{[t]}^r} \end{aligned}
$$

$$
\mathbf{S}_{[t+1]} = \brickred{\operatorname{Diag}(\boldsymbol{\gamma}_{[t]}^C)} \mathbf{S}_{[t]} + \left(\brickred{\bm{\Gamma}_{[t]}^{i\rightarrow C}} \odot \mathbf{K}_{[t]}\right)^\top \left(\mathbf{U}_{[t]} - \mathbf{W}_{[t]} \mathbf{S}_{[t]}\right) \in \mathbb{R}^{d_k\times d_v}
$$

$$
\mathbf{O}_{[t]} = \underbrace{\left(\brickred{{\bm{\Gamma}}_{[t]}^{1\rightarrow C}} \odot\mathbf{Q}_{[t]}\right) \mathbf{S}_{[t]}}_\text{inter chunk} + \underbrace{\operatorname{Tril}\left(\left(\brickred{{\bm{\Gamma}}_{[t]}^{1\rightarrow C}} \odot \mathbf{Q}_{[t]} \right) \left(\frac{\mathbf{K}_{[t]}}{\brickred{{\bm{\Gamma}}_{[t]}^{1\rightarrow C}}} \right)^\top \right)}_\text{intra chunk} \underbrace{\left(\mathbf{U}_{[t]} - \mathbf{W}_{[t]} \mathbf{S}_{[t]}\right)}_{\text{``pseudo''-value term}} \in \mathbb{R}^{C\times d_v}
$$

$$
\begin{aligned} \bm{o}_t = \mathbf{W}_o\left( \operatorname{Sigmoid}\left(\mathbf{W}_g^{\uparrow}\mathbf{W}_g^{\downarrow} \bm{x}_t\right)\odot \operatorname{RMSNorm}\left(\operatorname{KDA}\left( \bm{q}_t,\bm{k}_t,\bm{v}_t,\brickred{\bm{\alpha}_t},\beta_t \right) \right)\right) \end{aligned}
$$

$$
s_{t,i} = \bm{q}_t^{\top} \left( \prod_{j=i+1}^t \mathbf{R}_j\right) \bm{k}_i
$$

$$
\mathrm{FLOPs}_{\text{Attn}}(T; d_h) \;=\; 2 T^2 d_h.
$$

$$
\mathbf{S}_{t}=\brickred{\mathbf{A}_t}\mathbf{S}_{t-1} + \bm{k}_t\bm{v}_t^\top,\quad\bm{o}_{t}=\mathbf{S}_t^\top\bm{q}_t.
$$

$$
\mathbf{P}_{[t]}^r = \brickred{\operatorname{Diag}(\boldsymbol{\gamma}_{[t]}^r)} - \sum_{i=1}^{r} \brickred{\operatorname{Diag}(\boldsymbol{\gamma}_{[t]}^{i\rightarrow r})} \boldsymbol{k}_{[t]}^i \boldsymbol{w}_{[t]}^{i\top}
$$

$$
\boldsymbol{w}_{[t]}^r = \beta_{[t]}^r \left( \brickred{\operatorname{Diag}(\boldsymbol{\gamma}_{[t]}^r)} \boldsymbol{k}_{[t]}^r - \sum_{i=1}^{r-1} \boldsymbol{w}_{[t]}^i\left( \boldsymbol{k}_{[t]}^{i\top}\brickred{\operatorname{Diag}\left(\boldsymbol{\gamma}_{[t]}^{i\rightarrow r} \right)}\boldsymbol{k}_{[t]}^r \right) \right)
$$

$$
\mathbf{H}_{[t]}^r = \sum_{i=1}^{r} \brickred{\operatorname{Diag}\left(\boldsymbol{\gamma}_{[t]}^{i\rightarrow r}\right)} \boldsymbol{k}_{[t]}^i \boldsymbol{u}_{[t]}^{i\top}
$$

$$
\boldsymbol{u}_{[t]}^r = \beta_{[t]}^r \left(\boldsymbol{v}_{[t]}^r - \sum_{i=1}^{r-1}\boldsymbol{u}_{[t]}^i \left(\boldsymbol{k}_{[t]}^{i\top} \brickred{\operatorname{Diag}\left(\boldsymbol{\gamma}_{[t]}^{i\rightarrow r}\right)} \boldsymbol{k}_{[t]}^r\right) \right)
$$

$$
\boldsymbol{w}_{[t]}^r &= \beta_{[t]}^r \left( \brickred{\operatorname{Diag}(\boldsymbol{\gamma}_{[t]}^r)} \boldsymbol{k}_{[t]}^r - \sum_{i=1}^{r-1} \boldsymbol{w}_{[t]}^i\left( \boldsymbol{k}_{[t]}^{i\top}\brickred{\operatorname{Diag}\left(\boldsymbol{\gamma}_{[t]}^{i\rightarrow r} \right)}\boldsymbol{k}_{[t]}^r \right) \right) \\ \boldsymbol{u}_{[t]}^r &= \beta_{[t]}^r \left(\boldsymbol{v}_{[t]}^r - \sum_{i=1}^{r-1}\boldsymbol{u}_{[t]}^i \left(\boldsymbol{k}_{[t]}^{i\top} \brickred{\operatorname{Diag}\left(\boldsymbol{\gamma}_{[t]}^{i\rightarrow r}\right)} \boldsymbol{k}_{[t]}^r\right) \right)
$$

$$
\mathbf{M}_{[t]}&=\left(\mathbf{I} + \operatorname{StrictTril} \left(\operatorname{Diag}\left(\beta_{[t]}\right) \left(\brickred{{\bm{\Gamma}}_{[t]}^{1\rightarrow C}} \odot \mathbf{K}_{[t]} \right) \left(\frac{\mathbf{K}_{[t]}}{\brickred{\bm{\Gamma}_{[t]}^{1\rightarrow C}}} \right)^\top\right) \right)^{-1} \operatorname{Diag}\left(\beta_{[t]}\right)\\ \mathbf{W}_{[t]} &= \mathbf{M}_{[t]} \left(\brickred{{\bm{\Gamma}}_{[t]}^{1\rightarrow C}}\odot\mathbf{K}_{[t]}\right), \quad\quad\quad \mathbf{U}_{[t]}=\mathbf{M}_{[t]} \mathbf{V}_{[t]}
$$

$$
\bm{q}^h_t,\bm{k}^h_t &= \operatorname{L2Norm}(\operatorname{Swish}(\operatorname{ShortConv}(\mathbf{W}^h_{q/k}\bm{x}_t)))\in \mathbb{R}^{d_k}\\ \bm{v}^h_t &= \operatorname{Swish}(\operatorname{ShortConv}(\mathbf{W}^h_v\bm{x}_t))\in \mathbb{R}^{d_v} \\ \brickred{\bm{\alpha}^h_t} &= f(\mathbf{W}_{\alpha}^{\uparrow}\mathbf{W}_{\alpha}^{\downarrow}\bm{x}_t) \in [0,1]^{d_k}\\ \beta^h_t &= \operatorname{Sigmoid}(\mathbf{W}_{\beta}^h\bm{x}_t) \in [0,1]\\
$$

$$
\bm{o}_t = \sum_{i=1}^t \left( \bm{q}_t^{\top} \left(\prod_{j=i+1}^t\brickred{\mathbf{A}_j}\left(\mathbf{I}-\beta_j\bm{k}_j\bm{k}_j^\top\right) \right)\bm{k}_j\right) \bm{v}_j
$$

$$
\mathrm{FLOPs}_{\text{KDA}}(T; C, d_h) &= 6 T d_h^2 + 3 T C d_h + T C^2.
$$

$$
\mathbf{S}_t = \mathbf{S}_{t-1} + \bm{k}_t \bm{v}_t^\top, \qquad \bm{o}_t = \mathbf{S}_t^\top \bm{q}_t .
$$

$$
\mathcal{L}_t(\mathbf{S}) = -\langle \mathbf{S}^\top \bm{k}_t, \bm{v}_t \rangle ,
$$

$$
\mathcal{L}_t(\mathbf{S}) = \tfrac{1}{2}\|\mathbf{S}^\top\bm{k}_t - \bm{v}_t\|^2 .
$$

## 技术点深读（DEEP）

![[deep/kimi-linear-an-expressive-efficient-attention-architecture]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/kimi-linear-an-expressive-efficient-attention-architecture.txt`（94726 字符）供引用检索。