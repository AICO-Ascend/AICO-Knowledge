---
paper_num: "36"
title: "HC: Manifold-Constrained Hyper-Connections"
authors: "Zhenda Xie*†, Yixuan Wei*, Huanqi Cao*, Chenggang Zhao, Chengqi Deng, Jiashi Li, Damai Dai, Huazuo Gao, Jiang Chang, Kuai Yu, Liang Zhao, Shangyan Zhou, Zhean Xu, Zhengyan Zhang, Wangding Zeng, Shengding Hu, Yuqing Wang,"
date: "2026/1/5"
arxiv: "https://arxiv.org/abs/2512.24880"
pdf: "papers/hc-manifold-constrained-hyper-connections.pdf"
slug: "hc-manifold-constrained-hyper-connections"
tags: []
---

# HC: Manifold-Constrained Hyper-Connections

> [!abstract] 摘要（原文）
> 1\. 💡 针对Hyper-Connections (HC) 在扩展残差流宽度时面临的训练不稳定性和可扩展性受限问题，本文提出了Manifold-Constrained Hyper-Connections (mHC)。 2. 🛠️ mHC通过将HC的残差连接空间投影到由双随机矩阵构成的特定流形上，并结合如Sinkhorn-Knopp算法进行约束，从而恢复了恒等映射特性，同时通过基础设施优化（如内核融合和重计算）提升了效率。 3. 🚀 实验证明，mHC显著增强了大规模训练的稳定性，提供了实质性的性能提升和优越的可扩展性，且仅引入了微不足道的额外计算开销。

## 元信息
- **发表日期**: 2026/1/5
- **作者**: Zhenda Xie*†, Yixuan Wei*, Huanqi Cao*, Chenggang Zhao, Chengqi Deng, Jiashi Li, Damai Dai, Huazuo Gao, Jiang Chang, Kuai Yu, Liang Zhao, Shangyan Zhou, Zhean Xu, Zhengyan Zhang, Wangding Zeng, Shengding Hu, Yuqing Wang,
- **arXiv**: https://arxiv.org/abs/2512.24880
- **本地 PDF**: `papers/hc-manifold-constrained-hyper-connections.pdf`
- **页数**: 19

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-fig01.png]]
*整页渲染: ![[assets/hc-manifold-constrained-hyper-connections-p01.png]]*
> [!quote] caption
> Illustrations of Residual Connection Paradigms. This figure compares the structural

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

The figure compares three residual connection schemes across three panels. **(a) Residual Connection**: input **x_l** passes through Layer **F**, with its output added (⊕) back to **x_l** via a skip connection to form **x_{l+1}**. **(b) Hyper-Connections (HC)**: expand this by inserting three learnable mapping modules — Pre Mapping (**H_l^pre**, input side), Post Mapping (**H_l^post**, output side), and Res Mapping (**H_l^res**, residual branch) — producing hidden states **h_l^in, h_l^out, h_l^post, h_l^res**. **(c) Manifold-Constrained HC (mHC)**: retains the same structure but projects each mapping onto a constrained manifold via **P_M^pre(·), P_M^post(·), P_M^res(·)** (green blocks). 

**Key takeaway:** mHC restricts hyper-connection weights to a manifold, stabilizing training and preserving signal magnitude compared to unconstrained HC, which can suffer from exploding/vanishing hidden states.

**Caption (verbatim):**

(a) Residual Connection   (b) Hyper-Connections (HC)   (c) Manifold-Constrained HC (*m*HC)

### Figure 2 (p.7) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-fig02.png]]
*整页渲染: ![[assets/hc-manifold-constrained-hyper-connections-p07.png]]*
> [!quote] caption
> Training Instability of Hyper-Connections (HC). This figure illustrates (a) the absolute

> [!tip] 技术解读（多模态）
> **Figure 3 — Description (main figure):**

Figure 3 has two side-by-side log-scale plots of Amax Gain Magnitude (y-axis) vs. Layer Index *l* (x-axis, 0–60, with each Transformer block unrolled into Attention + FFN sub-layers).

- **(a) Single-Layer Mapping H_l^res:** Forward Signal Gain and Backward Gradient Gain both hover near 1 across interior layers, with sharp spikes only at the first and last layers.
- **(b) Composite Mapping:** The forward product ∏ H_l,i^res stays bounded (~10–20), but the backward gradient product grows roughly exponentially, peaking near ~10³–10⁴ around the middle layers before dropping at the ends.

**Key takeaway:** Although per-layer mappings are well-conditioned, the *composed* backward gradient gain explodes across depth, revealing a depth-wise backward-pass instability inherent to Hyper-Connections.

**Caption (verbatim):**

> Figure 3 | Propagation Instability of Hyper-Connections (HC). This figure illustrates the propagation dynamics of (a) the single-layer mapping $\mathcal{H}_l^{\text{res}}$ and (b) the composite mapping $\prod_{i=1}^{L-l}\mathcal{H}_{l,i}^{\text{res}}$ within the 27B model. The layer index $l$ ($x$-axis) unrolls each standard Transformer block into two independent layers (Attention and FFN). The Amax Gain Magnitude ($y$-axis) is calculated as the maximum absolute row sum (for the forward signal) and column sum (for the backward gradient), averaged over all tokens in a selected sequence.

### Figure 3 (p.7) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-fig03.png]]
*整页渲染: ![[assets/hc-manifold-constrained-hyper-connections-p07.png]]*
> [!quote] caption
> Propagation Instability of Hyper-Connections (HC). This figure illustrates the

> [!tip] 技术解读（多模态）
> **Figure 3 — Description (main figure):**

Figure 3 has two side-by-side log-scale plots of Amax Gain Magnitude (y-axis) vs. Layer Index *l* (x-axis, 0–60, with each Transformer block unrolled into Attention + FFN sub-layers).

- **(a) Single-Layer Mapping H_l^res:** Forward Signal Gain and Backward Gradient Gain both hover near 1 across interior layers, with sharp spikes only at the first and last layers.
- **(b) Composite Mapping:** The forward product ∏ H_l,i^res stays bounded (~10–20), but the backward gradient product grows roughly exponentially, peaking near ~10³–10⁴ around the middle layers before dropping at the ends.

**Key takeaway:** Although per-layer mappings are well-conditioned, the *composed* backward gradient gain explodes across depth, revealing a depth-wise backward-pass instability inherent to Hyper-Connections.

**Caption (verbatim):**

> Figure 3 | Propagation Instability of Hyper-Connections (HC). This figure illustrates the propagation dynamics of (a) the single-layer mapping $\mathcal{H}_l^{\text{res}}$ and (b) the composite mapping $\prod_{i=1}^{L-l}\mathcal{H}_{l,i}^{\text{res}}$ within the 27B model. The layer index $l$ ($x$-axis) unrolls each standard Transformer block into two independent layers (Attention and FFN). The Amax Gain Magnitude ($y$-axis) is calculated as the maximum absolute row sum (for the forward signal) and column sum (for the backward gradient), averaged over all tokens in a selected sequence.

### Figure 4 (p.12) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-fig04.png]]
*整页渲染: ![[assets/hc-manifold-constrained-hyper-connections-p12.png]]*
> [!quote] caption
> Communication-Computation Overlapping for mHC. We extend the DualPipe

> [!tip] 技术解读（多模态）
> ## Figure Description

The figure is a Gantt-style timeline showing a parallelized training schedule for a Mixture-of-Experts (MoE) transformer layer across **three concurrent streams**:

- **Normal Compute Stream** (top): Sequences MLP (B) → MLP (W) → MLP (F), then ATTN (B) → ATTN (W) → Whole Stage Recompute (B) → ATTN (F). Backward, weight-gradient, and forward blocks are arranged so recomputation precedes forward attention.
- **Communication Stream** (middle): Interleaves expert-parallel ops (DISPATCH F/B, COMBINE F/B) with pipeline-parallel ops (PP Send/Recv F/B), overlapped against compute.
- **High Priority Compute Stream** (bottom): Carries only the post-residual synchronization points (𝓕ᴹ_post,res (F/B)).

Vertical hatched markers (𝓕ᴹ_pre, 𝓕ᴬ_pre, 𝓕ᴬ_post,res, 𝓕ᴹ_post,res) denote barrier/synchronization events between streams.

**Key Technical Takeaway:** The schedule demonstrates *stream-level overlap* of MoE all-to-all communication (dispatch/combine) and PP point-to-point transfers with MLP/Attention kernels, exploiting CUDA multi-stream concurrency so that the heavier forward attention (with whole-stage recompute) is hidden behind collective communication.

## Caption (verbatim, transcribed from figure labels)

*No standalone caption text is present in the figure; the figure consists only of the labeled timeline shown above with stream labels "Normal Compute Stream", "Communication Stream", "High Priority Compute Stream" and in-block labels: MLP (B), MLP (W), MLP (F), ATTN (B), ATTN (W), Whole Stage Recompute (B), ATTN (F), DISPATCH (F), DISPATCH (B), COMBINE (F), PP Send Recv (F), PP Send Recv (B), COMBINE (B), and barrier markers 𝓕ᴹ_pre (B), 𝓕ᴬ_post,res (B), 𝓕ᴬ_pre (B), 𝓕ᴬ_pre (F), 𝓕ᴬ_post,res (F), 𝓕ᴹ_pre (F), 𝓕ᴹ_post,res (F), 𝓕ᴹ_post,res (B).*

### Figure 5 (p.12) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-fig05.png]]
*整页渲染: ![[assets/hc-manifold-constrained-hyper-connections-p12.png]]*
> [!quote] caption
> Training Stability of Manifold-Constrained Hyper-Connections (mHC). This figure

> [!tip] 技术解读（多模态）
> **Figure Description:**

The figure presents a two-panel comparison of three reinforcement-learning methods—**Baseline** (gray), **HC** (light blue), and **mHC** (dark blue)—plotted over 10⁷ episodes on log-scale x-axes.

- **(a) Cumulative Regret:** Baseline remains flat at a high constant value, while both HC and mHC rise sub-linearly, with mHC consistently achieving the lowest cumulative regret throughout training.
- **(b) Average Loss:** All three methods decrease, but HC exhibits high variance/noise; Baseline and mHC decay smoothly and nearly overlap, with mHC tracking Baseline closely while still outperforming HC.

**Key takeaway (≤120 words):**
The figure evaluates HC vs. mHC against a non-curriculum Baseline on a long-horizon task (10⁷ episodes). Both variants reduce cumulative regret relative to Baseline, but HC's loss curve is unstable. **mHC achieves the best of both worlds**: it matches Baseline's smooth, stable training dynamics while delivering lower cumulative regret than HC, indicating that the modification preserves exploration benefits of hierarchical curricula without destabilizing optimization.

**Verbatim caption transcription:**

(a) Cumulative regret over episodes   (b) Average loss over episodes

### Figure 6 (p.13) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-fig06.png]]
*整页渲染: ![[assets/hc-manifold-constrained-hyper-connections-p13.png]]*
> [!quote] caption
> Scaling properties of mHC compared to the Baseline. (a) Compute Scaling Curve.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Figure 6** presents a 2×2 grid of line plots comparing Baseline (black, flat reference) vs. *m*HC (blue) across two experimental dimensions:

- **(a) Compute Scaling Curve** — X-axis: FLOPs (log scale, ~10²¹ to 10²²), plotted across compute-optimal configurations spanning 3B → 9B → 27B parameter models.
- **(b) Token Scaling Curve** — X-axis: FLOPs (2 to ~5×10²¹), tracking the 3B model's trajectory over training tokens.

Each subfigure contains paired Y-axes: **Absolute Loss Gap** (left, –0.04 to 0.02) and **Relative Loss Ratio** (right, 98.0% to 101.0%). The Baseline is normalized to 0 / 100%, while the blue *m*HC line stays consistently below (≈ –0.025 to –0.015 absolute; ≈ 98.5–99.2% relative).

**Key takeaway (≈45 words):** *m*HC's loss-reduction advantage over the Baseline is preserved — and only marginally attenuated — as compute scales from 3B to 27B and as training tokens increase, demonstrating that the method transfers favorably to large-scale pre-training regimes without saturation.

## Caption (verbatim)

**Figure 6 | Scaling properties of *m*HC compared to the Baseline. (a) Compute Scaling Curve.** Solid lines depict the performance gap across different compute budgets. Each point represents a specific compute-optimal configuration of model size and dataset size, scaling from 3B and 9B to 27B parameters. **(b) Token Scaling Curve.** Trajectory of the 3B model during training. Each point represents the model's performance at different training tokens. Detailed architectures and training configurations are provided in Appendix A.1.

### Figure 7 (p.14) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-fig07.png]]
*整页渲染: ![[assets/hc-manifold-constrained-hyper-connections-p14.png]]*
> [!quote] caption
> Propagation Stability of Manifold-Constrained Hyper-Connections (mHC). This

> [!tip] 技术解读（多模态）
> ## Main Figure (Figure 8): Visualizations of Learnable Mappings

**Architecture / Components.** A 2×6 grid of heatmap matrices comparing **HC (top row)** vs. **mHC (bottom row)** at three depth slices — single-layer mappings (H₁^res, H₃₀^res, H₆₀^res) and composite mappings (∏₃₀, ∏₃₀, ∏₆₀). Each cell shows an averaged mapping weight; **row sums along the y-axis** annotate the **forward signal gain**, while **column sums along the x-axis** annotate the **backward gradient gain**.

**Data Flow.** Token activations are routed through these learnable mapping matrices layer-by-layer. Single-layer mappings are composed multiplicatively across depth to form the composite mappings, propagating signals forward and gradients backward through the network.

**Key Technical Takeaway.** HC matrices exhibit extreme, unbounded values (e.g., −251.4, −475.3, +509.1) and wildly oscillating gain magnitudes — confirming the instability problem of vanilla Hyper-Connections. In contrast, mHC matrices stay near-doubly-stochastic, with entries clustered close to 1/width and gains tightly bounded near 1.0 (typically 0.95–1.11), thanks to the Sinkhorn-Knopp projection that enforces the manifold constraint at ~20 iterations.

## Caption (verbatim)

> **Figure 8 | Visualizations of Learnable Mappings.** This figure displays representative single-layer and composite mappings for HC (first row) and *m*HC (second row). Each matrix is computed by averaging over all tokens within a selected sequence. The labels annotated along the y-axis and x-axis indicate the forward signal gain (row sum) and the backward gradient gain (column sum), respectively.

### Figure 8 (p.14) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-fig08.png]]
*整页渲染: ![[assets/hc-manifold-constrained-hyper-connections-p14.png]]*
> [!quote] caption
> Visualizations of Learnable Mappings. This figure displays representative single-

> [!tip] 技术解读（多模态）
> ## Main Figure (Figure 8): Visualizations of Learnable Mappings

**Architecture / Components.** A 2×6 grid of heatmap matrices comparing **HC (top row)** vs. **mHC (bottom row)** at three depth slices — single-layer mappings (H₁^res, H₃₀^res, H₆₀^res) and composite mappings (∏₃₀, ∏₃₀, ∏₆₀). Each cell shows an averaged mapping weight; **row sums along the y-axis** annotate the **forward signal gain**, while **column sums along the x-axis** annotate the **backward gradient gain**.

**Data Flow.** Token activations are routed through these learnable mapping matrices layer-by-layer. Single-layer mappings are composed multiplicatively across depth to form the composite mappings, propagating signals forward and gradients backward through the network.

**Key Technical Takeaway.** HC matrices exhibit extreme, unbounded values (e.g., −251.4, −475.3, +509.1) and wildly oscillating gain magnitudes — confirming the instability problem of vanilla Hyper-Connections. In contrast, mHC matrices stay near-doubly-stochastic, with entries clustered close to 1/width and gains tightly bounded near 1.0 (typically 0.95–1.11), thanks to the Sinkhorn-Knopp projection that enforces the manifold constraint at ~20 iterations.

## Caption (verbatim)

> **Figure 8 | Visualizations of Learnable Mappings.** This figure displays representative single-layer and composite mappings for HC (first row) and *m*HC (second row). Each matrix is computed by averaging over all tokens within a selected sequence. The labels annotated along the y-axis and x-axis indicate the forward signal gain (row sum) and the backward gradient gain (column sum), respectively.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.6) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-tab01.png]]
> [!quote] caption
> | Ablation Study of HC Components. When a specific mapping ( H pre

> [!tip] 表格解读（多模态）
> **Note:** The provided image shows a **table** (Table 1, an ablation study), not a main figure with architecture/components/data flow. I will therefore describe the table's content and transcribe its caption as requested.

**Description of the Table (Table 1 — Ablation Study):**
The table presents an ablation study of "HC Components," evaluating the contribution of three mappings — ℋₗʳᵉˢ, ℋₗᵖʳᵉ, and ℋₗᵖᵒˢᵗ — against an "Absolute Loss Gap" metric. Each column corresponds to one component being toggled or evaluated, probing how dimensional consistency is preserved when specific mappings are disabled.

**Key Technical Takeaway:**
The authors enforce dimensional consistency by replacing disabled mappings with structurally motivated defaults: **1/n uniform weights for ℋₗᵖʳᵉ, all-ones weights for ℋₗᵖᵒˢᵗ, and the identity matrix for ℋₗʳᵉˢ** — enabling isolated measurement of each component's individual impact.

**Caption (transcribed verbatim, noting truncation of the right edge):**

> Table 1 | **Ablation Study of HC Components.** When a specific mapping (ℋₗᵖʳᵉ, ℋₗᵖᵒˢᵗ, ℋₗʳᵉˢ) is disabled, we employ a fixed mapping to maintain dimensional consistency: uniform weights of 1/n for ℋₗᵖʳᵉ, uniform weights of ones for ℋₗᵖᵒˢᵗ, and the identity matrix for ℋₗʳᵉˢ.

*(The sentence "ℋₗʳᵉˢ is disabled..." portion on the right margin is clipped in the image; the visible text ends cleanly at "identity matrix for ℋₗʳᵉˢ." The table body rows are not visible — only the column headers: ℋₗʳᵉˢ | ℋₗᵖʳᵉ | ℋₗᵖᵒˢᵗ | Absolute Loss Gap.)*

### Table 2 (p.8) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-tab02.png]]
> [!quote] caption
> | Comparison of Memory Access Costs Per Token. This analysis accounts for the overhead introduced by the residual stream maintenance in the forward pass, excluding the internal I/O of the layer function F .

> [!tip] 表格解读（多模态）
> The provided content is a **table** (Table 2), not a figure with architecture/components/data flow. Below is a description based on the table provided.

**Description (≈120 words):**
The figure is actually Table 2, a compact data table with four columns — *Method*, *Operation*, *Read (Elements)*, *Write (Elements)* — and a single visible data row for the "Residual" method, whose "Residual Merge" operation performs **2C** reads and **C** writes per token. No architectural diagram, schematic, or data-flow arrows are shown; the table merely quantifies element-level memory traffic during the forward pass. A partial second row is faintly visible beneath the rule but is cut off in the provided snippet. **Key takeaway:** residual-stream maintenance incurs a per-token memory-access cost of 2C reads + 1C writes, a non-trivial overhead that the authors explicitly factor in when comparing methods (note: internal I/O of ℱ is excluded by construction).

**Caption (verbatim):**
"Table 2 | Comparison of Memory Access Costs Per Token. This analysis accounts for the overhead introduced by the residual stream maintenance in the forward pass, excluding the internal I/O of the layer function ℱ."

### Table 3 (p.11) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-tab03.png]]
> [!quote] caption
> | Stored and Recomputed Intermediate Activations We list per token activation pre- served for the backward pass and the transient activation recomputed in 𝐿 𝑟 consecutive layers. Layer 𝑙 0 represents the first layer in 𝐿 𝑟 layers and layer 𝑙 is in [ 𝑙 0 , 𝑙 0 + 𝐿 𝑟 − 1 ] .

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**

The table (Table 3) enumerates intermediate activations handled during backpropagation in *mHC*-kernel recomputation, split into resident vs. transient memory. Two activations are *persistently stored*: the block input **x_l₀** (size *nC*, kept once per block of *L_r* layers) and the projected output **𝒻(ℋₗ^pre xₗ, 𝒲ₗ)** (size *C*, kept every layer). Three activations (**xₗ**, **ℋₗ^pre xₗ**, **RMSNorm(ℋₗ^pre xₗ)**) are recomputed *transiently* inside each block, contributing a per-block overhead of (*n*+2)*C* × *L_r* elements that sets the peak memory. Equation (20) balances resident term *nC*⌈*L*/*L_r*⌉ against transient term (*n*+2)*C*·*L_r* to derive the optimal block size *L_r*\* ≈ √(*nL*/(*n*+2)).

**Key takeaway:** Optimal recomputation block size grows as √*L*, trading resident vs. transient memory.

**Verbatim caption:**

Table 3 | **Stored and Recomputed Intermediate Activations** We list per token activation preserved for the backward pass and the transient activation recomputed in *L_r* consecutive layers. Layer *l*₀ represents the first layer in *L_r* layers and layer *l* is in [*l*₀, *l*₀ + *L_r* − 1].

### Table 5 (p.19) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-tab05.png]]
> [!quote] caption
> | Detailed Model Specifications and Hyper-parameters. This table presents the architec- tural configurations for the 3B, 9B, and 27B models based on the DeepSeek-V3 (Liu et al., 2024b) architecture. It outlines the specific hyper-parameters for m HC and HC, including the residual stream expansion an

> [!tip] 表格解读（多模态）
> ## Description

The table is **Table 5**, a specification sheet comparing four model configurations: **3B, 9B, 27B** (DeepSeek-V3-style), and a **3B/1T-tokens** variant. It is organized into four blocks:

1. **Capacity** — Vocab/Active/Total parameters (e.g., 27B has 4.14B active of 27.0B total).
2. **Architecture** — MoE layers (12 → 30), routed experts (64/72), 6 active + 2 shared experts, **MLA attention** with RoPE, RMSNorm, and **mHC/HC** expansion (n=4, gating α=0.01, Sinkhorn-Knopp t_max=20).
3. **Data** — 4 096 context, batch size 320 → 2 560, training steps 30k → 100k, tokens 39.3B → 1.05T.
4. **Optimization** — AdamW (β=(0.9, 0.95)), step LR schedule (8.6e-4 → 4.0e-4), 2 000-step warmup, weight decay 0.1.

**Key takeaway:** All variants keep MoE sparsity (only ~15–20% of total params active) and a uniform MLA + mHC backbone, scaling mainly via layers/dimensions; learning rate shrinks with model size while tokens-per-param and batch grow, preserving training stability across the 3B→27B sweep.

## Caption (verbatim)

**Table 5 | Detailed Model Specifications and Hyper-parameters.** This table presents the architectural configurations for the 3B, 9B, and 27B models based on the DeepSeek-V3 (Liu et al., 2024b) architecture. It outlines the specific hyper-parameters for *m*HC and HC, including the residual stream expansion and Sinkhorn–Knopp settings, alongside the optimization and training protocols used in the experiments.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf{x}_{l+1} = \mathbf{x}_l + \mathcal{F}(\mathbf{x}_l, \mathcal{W}_l),
$$

$$
\mathbf{x}_L = \mathbf{x}_l + \sum_{i=l}^{L-1} \mathcal{F}(\mathbf{x}_i, \mathcal{W}_i),
$$

$$
\mathbf{x}_{l+1} = \mathcal{H}_{l}^{\mathrm{res}}\mathbf{x}_l + \mathcal{H}_{l}^{\mathrm{post}\, \top}\mathcal{F}(\mathcal{H}_{l}^{\mathrm{pre}}\mathbf{x}_l, \mathcal{W}_l),
$$

$$
\mathbf{x}_{L} = \left(\prod_{i=1}^{L-l}\mathcal{H}_{L-i}^{\mathrm{res}}\right)\mathbf{x}_l + \sum_{i=l}^{L-1}\left(\prod_{j=1}^{L-1-i}\mathcal{H}_{L-j}^{\mathrm{res}}\right)\mathcal{H}_{i}^{\mathrm{post}\, \top}\mathcal{F}(\mathcal{H}_{i}^{\mathrm{pre}}\mathbf{x}_i, \mathcal{W}_i),
$$

$$
\begin{cases} \tilde{\mathbf{x}}_l = \text{RMSNorm}(\mathbf{x}_l) \\ \hpre{l} = \alpha_l^\mathrm{pre} \cdot \tanh(\theta^\mathrm{pre}_l \tilde{\mathbf{x}}^\top_l) + \mathbf{b}_l^\mathrm{pre} \\ \hpost{l} = \alpha_l^\mathrm{post} \cdot \tanh(\theta^\mathrm{post}_l \tilde{\mathbf{x}}^\top_l) + \mathbf{b}_l^\mathrm{post} \\ \hres{l} = \alpha_l^\mathrm{res} \cdot \tanh(\theta^\mathrm{res}_l \tilde{\mathbf{x}}^\top_l) + \mathbf{b}_l^\mathrm{res}, \\ \end{cases}
$$

$$
\mathcal{P}_{\mathcal{M}^\mathrm{res}}(\hres{l}) \coloneq \left\{ \hres{l} \in \mathbb{R}^{n \times n} \mid \hres{l}\mathbf{1}_n = \mathbf{1}_n, \ \mathbf{1}^\top_n\hres{l} = \mathbf{1}^\top_n, \ \hres{l} \geq 0 \right\},
$$

$$
\begin{cases} \vec{\mathbf{x}}'_l = \text{RMSNorm}(\vec{\mathbf{x}}_l) \\ \tlhpre{l} = \alpha_l^\mathrm{pre} \cdot (\vec{\mathbf{x}}'_l\phi^\mathrm{pre}_l) + \mathbf{b}_l^\mathrm{pre} \\ \tlhpost{l} = \alpha_l^\mathrm{post} \cdot (\vec{\mathbf{x}}'_l\phi^\mathrm{post}_l) + \mathbf{b}_l^\mathrm{post} \\ \tlhres{l} = \alpha_l^\mathrm{res} \cdot \text{mat}(\vec{\mathbf{x}}'_l\phi^\mathrm{res}_l) + \mathbf{b}_l^\mathrm{res}, \\ \end{cases}
$$

$$
\begin{cases} \hpre{l} = \sigma(\tlhpre{l}) \\ \hpost{l} = 2\sigma(\tlhpost{l}) \\ \hres{l} = \text{Sinkhorn-Knopp}(\tlhres{l}), \end{cases}
$$

$$
\mathbf{M}^{(t)} = \mathcal{T}_r\left(\mathcal{T}_c(\mathbf{M}^{(t-1)})\right),
$$

$$
L_r^* = \arg\min_{L_r} \left[ nC\times \left\lceil\frac{L}{L_r}\right\rceil + (n+2)C\times L_r \right] \approx \sqrt{\frac{nL}{n+2}}.
$$

## 技术点深读（DEEP）

![[deep/hc-manifold-constrained-hyper-connections]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/hc-manifold-constrained-hyper-connections.txt`（55403 字符）供引用检索。