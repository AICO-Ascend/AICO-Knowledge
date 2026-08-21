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
![[assets/hc-manifold-constrained-hyper-connections-p01.png]]
> [!quote] caption
> Illustrations of Residual Connection Paradigms. This figure compares the structural

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 1)

The figure presents three side-by-side diagrams comparing residual connection paradigms:

**(a) Residual Connection:** Simplest form. Single stream: input `x_l` passes through Layer `F`, is added (⊕) with a skip connection, producing `x_{l+1}`.

**(b) Hyper-Connections (HC):** Expands the residual stream into multiple parallel vectors (`x_l` stack). Four learned linear mappings orchestrate the flow:
- **Res Mapping** `H_l^res` → produces `h_l^res` (residual stream)
- **Pre Mapping** `H_l^pre` → produces `h_l^in` (input to Layer F)
- Layer `F` → produces `h_l^out`
- **Post Mapping** `H_l^post` → produces `h_l^post`
Outputs aggregated (⊕) into `x_{l+1}` stack.

**(c) Manifold-Constrained HC (mHC):** Identical topology to HC, but each mapping is replaced by a **manifold-projected** operator `P_M^res`, `P_M^pre`, `P_M^post` (shown in green). These constrain the matrices onto a specific geometric manifold, unlike the unconstrained `H_l` matrices in HC.

**Key Technical Takeaway (≤120 words):**
Standard residual connections preserve an *identity mapping* property essential for stable deep training. Hyper-Connections (HC) widen the residual stream with four unconstrained linear mappings (`H_l^res`, `H_l^pre`, `H_l^post`, etc.), boosting expressivity but breaking identity mapping—causing training instability, poor scalability, and memory overhead. **mHC solves this by wrapping each mapping with a manifold-projection operator `P_M(·)`**, restricting the matrices to a constrained subspace where the identity property is restored. The result: HC's capacity gains are retained while training stability and scalability are recovered, enabling effective large-scale training. In essence, mHC adds a *geometric inductive bias* to HC without altering its top-level data flow.

## Caption (Verbatim)

> Figure 1 | **Illustrations of Residual Connection Paradigms.** This figure compares the structural design of (a) standard Residual Connection, (b) Hyper-Connections (HC), and (c) our proposed **Manifold-Constrained Hyper-Connections (mHC)**. Unlike the unconstrained HC, *mHC* focuses on optimizing the residual connection space by projecting the matrices onto a constrained manifold to ensure stability.

### Figure 2 (p.7) ⭐深度解读
![[assets/hc-manifold-constrained-hyper-connections-p07.png]]
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
![[assets/hc-manifold-constrained-hyper-connections-p07.png]]
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
![[assets/hc-manifold-constrained-hyper-connections-p12.png]]
> [!quote] caption
> Communication-Computation Overlapping for mHC. We extend the DualPipe

> [!tip] 技术解读（多模态）
> # Main Figure Description

**Architecture/Components/Data Flow:**
Figure 4 depicts a DualPipe-style timeline scheduling diagram with three parallel horizontal streams:

1. **Normal Compute Stream** — Forward/backward MLP and Attention kernels (MLP(B), MLP(W), MLP(F), ATTN(B), ATTN(W), ATTN(F)) with a "Whole Stage Recompute (B)" block for backward recomputation, bracketed by residual-input/output markers (𝓕ᵖʳᵉ, �ᵖᵒˢᵗ,ʳᵉˢ for both Attention 𝓕ᴬ and MLP 𝓕ᴹ).
2. **Communication Stream** — All-to-all ops (DISPATCH/COMBINE in F or B) interleaved with point-to-point pipeline-parallel sends/receives (PP Send Recv).
3. **High Priority Compute Stream** — Hosts the small post-residual kernels (𝓕ᵖᵒˢᵗ,ʳᵉˢ) that must finish before the next pipeline stage begins.

**Key Takeaway:** By moving the residual-output kernels onto a dedicated high-priority compute stream, mHC hides the additional cost of hyper-connection residual recombination under otherwise idle communication bubbles, preserving DualPipe's overlap efficiency.

# Caption (verbatim)

**Figure 4 | Communication-Computation Overlapping for *m*HC.** We extend the DualPipe schedule to handle the overhead introduced by *m*HC. Lengths of each block are illustrative only and do not represent actual duration. (F), (B), (W) refers to forward pass, backward pass, weight gradient computation, respectively. 𝓕ᴬ and 𝓕ᴹ represents kernels corresponded to Attention and MLP, respectively.

### Figure 5 (p.12) ⭐深度解读
![[assets/hc-manifold-constrained-hyper-connections-p12.png]]
> [!quote] caption
> Training Stability of Manifold-Constrained Hyper-Connections (mHC). This figure

> [!tip] 技术解读（多模态）
> # Main Figure Description

**Architecture/Components/Data Flow:**
Figure 4 depicts a DualPipe-style timeline scheduling diagram with three parallel horizontal streams:

1. **Normal Compute Stream** — Forward/backward MLP and Attention kernels (MLP(B), MLP(W), MLP(F), ATTN(B), ATTN(W), ATTN(F)) with a "Whole Stage Recompute (B)" block for backward recomputation, bracketed by residual-input/output markers (𝓕ᵖʳᵉ, �ᵖᵒˢᵗ,ʳᵉˢ for both Attention 𝓕ᴬ and MLP 𝓕ᴹ).
2. **Communication Stream** — All-to-all ops (DISPATCH/COMBINE in F or B) interleaved with point-to-point pipeline-parallel sends/receives (PP Send Recv).
3. **High Priority Compute Stream** — Hosts the small post-residual kernels (𝓕ᵖᵒˢᵗ,ʳᵉˢ) that must finish before the next pipeline stage begins.

**Key Takeaway:** By moving the residual-output kernels onto a dedicated high-priority compute stream, mHC hides the additional cost of hyper-connection residual recombination under otherwise idle communication bubbles, preserving DualPipe's overlap efficiency.

# Caption (verbatim)

**Figure 4 | Communication-Computation Overlapping for *m*HC.** We extend the DualPipe schedule to handle the overhead introduced by *m*HC. Lengths of each block are illustrative only and do not represent actual duration. (F), (B), (W) refers to forward pass, backward pass, weight gradient computation, respectively. 𝓕ᴬ and 𝓕ᴹ represents kernels corresponded to Attention and MLP, respectively.

### Figure 6 (p.13) ⭐深度解读
![[assets/hc-manifold-constrained-hyper-connections-p13.png]]
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
![[assets/hc-manifold-constrained-hyper-connections-p14.png]]
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
![[assets/hc-manifold-constrained-hyper-connections-p14.png]]
> [!quote] caption
> Visualizations of Learnable Mappings. This figure displays representative single-

> [!tip] 技术解读（多模态）
> ## Main Figure (Figure 8): Visualizations of Learnable Mappings

**Architecture / Components.** A 2×6 grid of heatmap matrices comparing **HC (top row)** vs. **mHC (bottom row)** at three depth slices — single-layer mappings (H₁^res, H₃₀^res, H₆₀^res) and composite mappings (∏₃₀, ∏₃₀, ∏₆₀). Each cell shows an averaged mapping weight; **row sums along the y-axis** annotate the **forward signal gain**, while **column sums along the x-axis** annotate the **backward gradient gain**.

**Data Flow.** Token activations are routed through these learnable mapping matrices layer-by-layer. Single-layer mappings are composed multiplicatively across depth to form the composite mappings, propagating signals forward and gradients backward through the network.

**Key Technical Takeaway.** HC matrices exhibit extreme, unbounded values (e.g., −251.4, −475.3, +509.1) and wildly oscillating gain magnitudes — confirming the instability problem of vanilla Hyper-Connections. In contrast, mHC matrices stay near-doubly-stochastic, with entries clustered close to 1/width and gains tightly bounded near 1.0 (typically 0.95–1.11), thanks to the Sinkhorn-Knopp projection that enforces the manifold constraint at ~20 iterations.

## Caption (verbatim)

> **Figure 8 | Visualizations of Learnable Mappings.** This figure displays representative single-layer and composite mappings for HC (first row) and *m*HC (second row). Each matrix is computed by averaging over all tokens within a selected sequence. The labels annotated along the y-axis and x-axis indicate the forward signal gain (row sum) and the backward gradient gain (column sum), respectively.

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