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
![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p01.png]]
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
![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p05.png]]
> [!quote] caption
> Execution time of kernels for vary- ing input lengths, with a uniform batch size of 1 and 16 heads.

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 2) — Description:**

The figure is a line plot comparing kernel execution time (ms, y-axis, 0–64) against input length (x-axis, 2K→64K) for two attention implementations: **DPLR** (teal dashed line) and **KDA (ours)** (solid blue line). Both curves start near 0 ms at 2K. DPLR grows approximately exponentially, climbing steeply past ~48 ms by 64K. KDA remains nearly flat across 2K–32K (~0–8 ms) and only rises to ~30 ms at 64K, consistently sitting below DPLR. Conditions: batch size = 1, 16 heads.

**Key Technical Takeaway:** KDA eliminates the second-level chunk matmuls of DPLR (Equation 9) by binding decay variables **a**, **b** into **k**, dropping four chunk matmuls to two and yielding ~2× kernel speedup, with the gap widening at long sequences (64K).

**Caption (verbatim):**
> Figure 2: Execution time of kernels for varying input lengths, with a uniform batch size of 1 and 16 heads.

### Figure 3 (p.5) ⭐深度解读
![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p05.png]]
> [!quote] caption
> Neural Parameterization

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 2) — Description:**

The figure is a line plot comparing kernel execution time (ms, y-axis, 0–64) against input length (x-axis, 2K→64K) for two attention implementations: **DPLR** (teal dashed line) and **KDA (ours)** (solid blue line). Both curves start near 0 ms at 2K. DPLR grows approximately exponentially, climbing steeply past ~48 ms by 64K. KDA remains nearly flat across 2K–32K (~0–8 ms) and only rises to ~30 ms at 64K, consistently sitting below DPLR. Conditions: batch size = 1, 16 heads.

**Key Technical Takeaway:** KDA eliminates the second-level chunk matmuls of DPLR (Equation 9) by binding decay variables **a**, **b** into **k**, dropping four chunk matmuls to two and yielding ~2× kernel speedup, with the gap widening at long sequences (64K).

**Caption (verbatim):**
> Figure 2: Execution time of kernels for varying input lengths, with a uniform batch size of 1 and 16 heads.

### Figure 4 (p.7) ⭐深度解读
![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p07.png]]
> [!quote] caption
> Results on synthetic tasks: palindrome, multi query associative recall, and the state tracking.

> [!tip] 技术解读（多模态）
> **Figure description (≤120 words):**

Figure 4 is a 2×3 grid comparing three linear-attention models—**KDA** (solid blue, circles), **GDN** (dashed teal, stars), and **Mamba2** (dashed orange, triangles)—on three synthetic tasks: Palindrome, MQAR, and Stack. The **top row** plots peak Accuracy (%) versus sequence length (256–2048 tokens), revealing that KDA and GDN maintain near-perfect accuracy at short lengths while Mamba2 collapses to 0% beyond 512 tokens on Palindrome and Stack. The **bottom row** plots Accuracy versus training steps (0–20K) at fixed 1,024-token context, showing KDA converges fastest (≈5K steps) and Mamba2 fails entirely. **Key takeaway:** KDA is the only method that simultaneously achieves fast convergence and robustness to long context across all three copying/recall benchmarks, outperforming both GDN (slower convergence, accuracy drop at 2048) and Mamba2 (fails on state-tracking tasks).

**Caption (verbatim):**

Figure 4: Results on synthetic tasks: palindrome, multi query associative recall, and the state tracking.

### Figure 5 (p.9) ⭐深度解读
![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p09.png]]
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
![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p12.png]]
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
![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p13.png]]
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