---
paper_num: "26"
title: "HYPER-CONNECTIONS"
authors: ""
date: "2026/1/19"
arxiv: "https://arxiv.org/abs/2409.19606"
pdf: "papers/hyper-connections.pdf"
slug: "hyper-connections"
tags: []
---

# HYPER-CONNECTIONS

> [!abstract] 摘要（原文）
> 1\. ✨ 这项研究引入了hyper-connections，作为Residual Connections的一种有效替代方案，旨在解决梯度消失和表示崩溃之间的跷跷板效应。 2. 🧠 理论上，hyper-connections通过可学习的深度和宽度连接，并支持动态调整层间连接强度及实现序列-并行双重性，从而优化网络层排布。 3. 🚀 实验结果表明，hyper-connections在LLMs（包括dense和MoE模型）以及Vision任务中均显著提升了性能，同时仅引入可忽略的计算和参数开销。

## 元信息
- **发表日期**: 2026/1/19
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2409.19606
- **本地 PDF**: `papers/hyper-connections.pdf`
- **页数**: 37

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/hyper-connections-fig01.png]]
*整页渲染: ![[assets/hyper-connections-p01.png]]*
> [!quote] caption
> The performance of the baseline model OLMoE-1B-7B and the model with hyper- connections, OLMoE-1B-7B-DHC×4. (1) and (2) show the training loss (0.99 EMA smoothed) and the C4-en validation loss, respectively. Our method converges 1.8 times faster compared to the baseline and maintains a significant advantage at the 500B tokens. (3) and (4) show the accuracy curves on HellaSwag and ARC-Challenge, de

> [!tip] 技术解读（多模态）
> **Figure description**

This is a four-panel empirical comparison (not an architecture diagram) plotting two model variants — `OLMoE-1B-7B` (baseline, red) vs `OLMoE-1B-7B-DHC×4` (hyper-connections, blue) — as a function of training tokens (100B → 500B):
1. Training loss (0.99 EMA smoothed) — blue sits below red throughout.
2. C4-en validation loss — same trend.
3. HellaSwag accuracy (%) — blue higher.
4. ARC-Challenge accuracy (%) — blue higher.

Annotations mark a "×1.8" convergence-speedup gap at ~0.027 / 0.028 loss. Lightly shaded regions indicate variance across runs.

**Key takeaway**: Hyper-connections yield ~1.8× faster convergence and sustained downstream-accuracy gains (HellaSwag, ARC-Challenge) over standard residual connections, without changing the underlying architecture.

**Caption (verbatim)**

"Figure 1: The performance of the baseline model `OLMoE-1B-7B` and the model with hyper-connections, `OLMoE-1B-7B-DHC×4`. (1) and (2) show the training loss (0.99 EMA smoothed) and the C4-en validation loss, respectively. Our method converges 1.8 times faster compared to the baseline and maintains a significant advantage at the 500B tokens. (3) and (4) show the accuracy curves on `HellaSwag` and `ARC-Challenge`, demonstrating the superior performance of the `OLMoE-1B-7B-DHC×4` model."

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/hyper-connections-fig02.png]]
*整页渲染: ![[assets/hyper-connections-p02.png]]*
> [!quote] caption
> Hyper-connections (HC) with an expansion rate of n = 2. (a) Residual connections. (b) Hyper-connections: β1, β2, α0,0, α0,1, α1,0, α1,1, α2,1, and α2,2 are learnable scalars or scalars predicted by the network , depending on the specific HC version. These connections enable lateral information exchange and vertical integration of features across depths. The Transformer with HC is shown in Fig. 17.

> [!tip] 技术解读（多模态）
> # Figure 2 Description

**Architecture/Components:** Figure 2 compares four connection schemes at expansion rate n=2:
- **(a) Residual connections:** A single layer adds its output to the input h (baseline).
- **(b) Hyper-connections (HC):** Input h is split into n=2 hidden vectors (h₁, h₂). Learnable scalars (α for layer-to-hidden weights; β for hidden-to-hidden weights) route information from the layer output back into the hidden vectors, plus lateral links between h₁ and h₂.
- **(c) Depth-connections:** Vertical-only path—a weighted sum between layer output and h₁ via scalar α.
- **(d) Width-connections:** Lateral-only path—information exchange between h₁ and h₂ via β scalars.

**Data flow:** Hidden vectors → layer (attention/FFN) → weighted α aggregation → update hidden vectors → β lateral mixing → next layer.

**Key technical takeaway:** HC generalizes residual connections by making connection strengths learnable (α, β scalars), enabling both flexible vertical feature integration (depth) and lateral hidden-vector exchange (width); n=1 collapses back to residual behavior, so n>1 is essential for performance gains.

---

## Caption (verbatim)

Figure 2: **Hyper-connections (HC) with an expansion rate of** n = 2. (a) Residual connections. (b) Hyper-connections: β₁, β₂, α₀,₀, α₀,₁, α₁,₀, α₁,₁, α₂,₁, and α₂,₂ are learnable scalars or scalars predicted by the network , depending on the specific HC version. These connections enable lateral information exchange and vertical integration of features across depths. The Transformer with HC is shown in Fig. 17. They can be decoupled into depth-connections and width-connections. (c) Depth-connections perform a weighted sum between the layer output and the hidden vector h₁. (d) Width-connections allow information exchange between the hidden vectors h₁ and h₂.

### Figure 3 (p.2) ⭐深度解读
![[assets/crops/hyper-connections-fig03.png]]
*整页渲染: ![[assets/hyper-connections-p02.png]]*
> [!quote] caption
> Cosine similarity be- tween the input of the current and the previous layers for the OLMo-1B models (Groeneveld et al., 2024). The curve represents the median of similarity, while the shaded area indicates the range be- tween the 5th and 95th percentiles.

> [!tip] 技术解读（多模态）
> # Figure 2 Description

**Architecture/Components:** Figure 2 compares four connection schemes at expansion rate n=2:
- **(a) Residual connections:** A single layer adds its output to the input h (baseline).
- **(b) Hyper-connections (HC):** Input h is split into n=2 hidden vectors (h₁, h₂). Learnable scalars (α for layer-to-hidden weights; β for hidden-to-hidden weights) route information from the layer output back into the hidden vectors, plus lateral links between h₁ and h₂.
- **(c) Depth-connections:** Vertical-only path—a weighted sum between layer output and h₁ via scalar α.
- **(d) Width-connections:** Lateral-only path—information exchange between h₁ and h₂ via β scalars.

**Data flow:** Hidden vectors → layer (attention/FFN) → weighted α aggregation → update hidden vectors → β lateral mixing → next layer.

**Key technical takeaway:** HC generalizes residual connections by making connection strengths learnable (α, β scalars), enabling both flexible vertical feature integration (depth) and lateral hidden-vector exchange (width); n=1 collapses back to residual behavior, so n>1 is essential for performance gains.

---

## Caption (verbatim)

Figure 2: **Hyper-connections (HC) with an expansion rate of** n = 2. (a) Residual connections. (b) Hyper-connections: β₁, β₂, α₀,₀, α₀,₁, α₁,₀, α₁,₁, α₂,₁, and α₂,₂ are learnable scalars or scalars predicted by the network , depending on the specific HC version. These connections enable lateral information exchange and vertical integration of features across depths. The Transformer with HC is shown in Fig. 17. They can be decoupled into depth-connections and width-connections. (c) Depth-connections perform a weighted sum between the layer output and the hidden vector h₁. (d) Width-connections allow information exchange between the hidden vectors h₁ and h₂.

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/hyper-connections-fig04.png]]
*整页渲染: ![[assets/hyper-connections-p05.png]]*
> [!quote] caption
> Sequential and parallel arrangements of hyper-connections with n = 2.

> [!tip] 技术解读（多模态）
> **Figure 4 Description:**

Figure 4 illustrates two hyper-connection topologies with expansion rate n = 2, showing how a learnable matrix determines layer arrangement.

**Components (shared by both subfigures):**
- Blue/yellow rectangular token blocks (residual stream + expanded inputs)
- Rounded "layer 1" / "layer 2" modules
- ⊕ summation nodes connecting layer outputs back into the stream
- Directed arrows encoding weighted connections (the hyper-connection matrix entries)

**(a) Sequential Arrangement:** Lower-triangular HC = `(0,1;1,1)`; each layer feeds forward, and the depth connection degenerates into a standard residual connection.

**(b) Parallel Arrangement:** Odd/even HC matrices `(0,1,0;1,1,1;1,1,1)` and `(0,0,1;0,1,0;1,0,1)` route both layers' inputs simultaneously — analogous to parallel transformer blocks.

**Key takeaway:** The same layer stack yields sequential or parallel behavior purely from the HC matrix pattern, enabling a learnable sequential–parallel duality beyond fixed architectural choices.

**Caption (verbatim):**
> Figure 4: Sequential and parallel arrangements of hyper-connections with n = 2.

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/hyper-connections-fig05.png]]
*整页渲染: ![[assets/hyper-connections-p06.png]]*
> [!quote] caption
> Comparison of training loss curves for different expansion rate. The left subfigure includes models with dynamic hyper-connections (DHC) at various expansion rates, while the right subfigure shows the effect of omitting the tanh function. Both subfigures illustrate how increasing the expansion rate leads to improved training loss performance over 500B tokens. Results are smoothed using an exponent

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Figure 5** consists of two side-by-side line plots comparing training loss curves across 100–500B tokens for the OLMo-1B model.

- **Left subplot**: Compares the baseline OLMo-1B against DHC variants at expansion rates ×1, ×2, ×4, ×8 (with tanh).
- **Right subplot**: Compares the baseline against the same DHC variants but **without the tanh activation**.
- **Axes**: x = tokens (billions); y = training loss (~2.40–2.60), smoothed via EMA (coefficient 0.99).
- **Data flow**: Each curve represents a separate model run, with loss decreasing monotonically as training progresses; higher expansion rates yield lower final loss.

**Key takeaway**: Increasing the DHC expansion rate consistently lowers training loss, and removing the tanh function yields the best results (OLMo-1B-DHC×8 W/O tanh reaches 2.777 V2 Eval loss, bolded in Table 1), indicating the tanh activation may be unnecessary or even detrimental at high expansion rates.

## Caption (verbatim)

> **Figure 5:** Comparison of training loss curves for different expansion rate. The left subfigure includes models with dynamic hyper-connections (DHC) at various expansion rates, while the right subfigure shows the effect of omitting the tanh function. Both subfigures illustrate how increasing the expansion rate leads to improved training loss performance over 500B tokens. Results are smoothed using an exponential moving average with a coefficient of 0.99.

### Figure 6 (p.8) ⭐深度解读
![[assets/crops/hyper-connections-fig06.png]]
*整页渲染: ![[assets/hyper-connections-p08.png]]*
> [!quote] caption
> (1) and (2) Training loss (0.99 EMA smoothed) and C4-en validation loss for OLMo-7B and OLMo-7B-DHC×4 models. (3) and (4) Accuracy curves on hellaswag and sciq, demonstrating the superior performance of the OLMo-7B-DHC×4 model.

> [!tip] 技术解读（多模态）
> **Figure 6 Description:**

**Architecture/Components/Data Flow:** Figure 6 is a 1×4 panel of line plots tracking two models—OLMo-7B (red) and OLMo-7B-DHC×4 (blue)—across training from 100B to ~500B tokens. Panels (1)–(2) plot loss on the y-axis: (1) Training Loss (0.99 EMA smoothed, range ~2.2–2.4) and (2) C4-en validation Loss (~2.5–2.7). Panels (3)–(4) plot downstream accuracy: (3) HellaSwag Acc. (~55–70%) and (4) SciQ Acc. (~82–92%). Shaded bands indicate variance/uncertainty across runs.

**Key Technical Takeaway:** OLMo-7B-DHC×4 (Dynamic Hyper-Connections ×4) consistently outperforms the OLMo-7B baseline on all four metrics throughout training—achieving lower loss curves and higher downstream accuracy—and crucially eliminates the loss spikes seen in the baseline, yielding more stable optimization.

**Caption (verbatim):**
"Figure 6: (1) and (2) Training loss (0.99 EMA smoothed) and C4-en validation loss for `OLMo-7B` and `OLMo-7B-DHC×4` models. (3) and (4) Accuracy curves on `hellaswag` and `sciq`, demonstrating the superior performance of the `OLMo-7B-DHC×4` model."

### Figure 7 (p.9) ⭐深度解读
![[assets/crops/hyper-connections-fig07.png]]
*整页渲染: ![[assets/hyper-connections-p09.png]]*
> [!quote] caption
> Visualization of connection matrices for hyper-connections and various related baseline methods. The attention layers, which have odd ids, are marked with green tick marks.

> [!tip] 技术解读（多模态）
> **Main figure (Figure 7) description:**

Figure 7 is a panel of five triangular heatmaps (32×32) visualizing learned inter-layer connection weights, with a shared color scale ranging from −1.0 (blue) to +1.0 (red). The five panels compare: (1) Hyper-Connection, (2) Post-Norm, (3) Pre-Norm, (4) Pre-Norm PTB, and (5) Two-hop Residual. Rows represent destination layers (0–32) and columns represent source layers; attention layers (odd ids) are marked with green tick marks on the axes. The x-axes are labeled with values 0–32 in increments of 4.

**Key technical takeaway:**
Hyper-connections learn a much richer, sparser, and more selective routing pattern (mostly white/near-zero with a few strong red and blue entries, including PTB-style shortcut signals), whereas Pre-Norm, Pre-Norm PTB, and Two-hop Residual show uniform, dense near-1.0 lower-triangular patterns — indicating that standard residual variants propagate information uniformly, while DHC dynamically routes layer outputs.

**Caption (verbatim):**
"Figure 7: Visualization of connection matrices for hyper-connections and various related baseline methods. The attention layers, which have odd ids, are marked with green tick marks."

### Figure 8 (p.14) ⭐深度解读
![[assets/crops/hyper-connections-fig08.png]]
*整页渲染: ![[assets/hyper-connections-p14.png]]*
> [!quote] caption
> Comparison between transformers with hyper-connections and that with residual connec- tions. 14

> [!tip] 技术解读（多模态）
> ## Description

The figure contrasts two architectures side-by-side:

**Left (Residual Connections):** A standard Transformer stack alternating **Attention** and **FFN** blocks, each followed by a fixed additive skip (`+`) that propagates a single hidden state `h⁰ → … → hᴸ` straight through the network.

**Right (Hyper-Connections):** The input `h⁰` is **repeated** into multiple parallel streams (here `h¹₁, h¹₂`). Each layer introduces a small sub-network of **learnable coefficients**:
- **αᵢ,ᵣ,ᶜ weights** (blue/orange) gate how each input stream mixes into every stream fed into Attention/FFN,
- **β weights** (green) scale each output stream after the sub-layer.

The streams are then re-combined via additive nodes, yielding two outputs `hᴸ₁, hᴸ₂` that are summed into the final `hᴸ`.

**Key technical takeaway:** Hyper-Connections replace the rigid identity skip with a **learnable, multi-stream mixing matrix** (α inputs + β outputs), giving the model a flexible routing knob on top of the standard residual path — a strict generalization of residual connections, not a replacement of the sub-layers themselves.

## Caption (verbatim)

**Figure 8:** Comparison between transformers with hyper-connections and that with residual connections.

### Figure 9 (p.17) ⭐深度解读
![[assets/crops/hyper-connections-fig09.png]]
*整页渲染: ![[assets/hyper-connections-p17.png]]*
> [!quote] caption
> Loss curves in V3 validation sets and accuracy curves on downstream tasks for OLMoE-1B7B and OLMoE-1B7B-DHC×4 models. 17

> [!tip] 技术解读（多模态）
> **Description:**
The figure is a 7-row × 4-column grid of line plots comparing two MoE (Mixture-of-Experts) models — `OLMoE-1B-7B` (red) vs `OLMoE-1B-7B-DHC×4` (blue) — trained over ~500B tokens (x-axis). The top three rows plot **validation loss** across 12 V3 datasets (training loss, C4 en, Dolma subsets: books/cc/pes2o/reddit/stack/wiki, ICE, m2d2-s2orc, Pile, WikiText-103). The bottom four rows plot **downstream accuracy** on 16 benchmarks spanning MMLU variants, HellaSwag, SciQ, ARC-Easy/Challenge, PIQA, WinoGrande, OpenBookQA, BoolQ, COPA, CommonsenseQA, and SocialIQA. **Key takeaway:** Across nearly every panel, the DHC×4 variant sits below (loss) or above (accuracy) the baseline, indicating the routing/expert-activation modification yields consistent gains in both pretraining loss and zero-shot task accuracy, with the gap visible from ~100B tokens onward.

**Caption (verbatim):**
Figure 9: Loss curves in V3 validation sets and accuracy curves on downstream tasks for `OLMoE-1B7B` and `OLMoE-1B7B-DHC×4` models.

### Figure 10 (p.18) ⭐深度解读
![[assets/crops/hyper-connections-fig10.png]]
*整页渲染: ![[assets/hyper-connections-p18.png]]*
> [!quote] caption
> Loss curves in V3 validation set and accuracy curves on downstream tasks for OLMo-7B and OLMo-7B-DHC×4 models. 18

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

The figure is a 6×3 grid of line plots comparing two 7B-scale language models — `OLMo-7B` (red) and `OLMo-7B-DHCx4` (blue) — across training tokens (100B–500B, x-axis). The top four rows display validation loss curves on eleven pretraining datasets (c4, dolma books/cc/pes2o/reddit/stack/wiki, ice, m2d2-s2orc, pile, wikitext-103); the bottom two rows show accuracy on seven downstream benchmarks (HellaSwag, SciQ, COPA, OpenbookQA, PIQA, WinoGrande, ARC-Easy). In every panel the blue DHCx4 curve sits below the red baseline on loss plots and above it on accuracy plots.

**Key takeaway:** The DHC×4 enhancement yields consistent, monotonic improvements over the baseline OLMo-7B across all 18 evaluation domains throughout training, confirming its scalability to 7B parameters.

**Caption (verbatim):**
Figure 10: Loss curves in V3 validation set and accuracy curves on downstream tasks for `OLMo-7B` and `OLMo-7B-DHC×4` models.

### Figure 11 (p.20) ⭐深度解读
![[assets/crops/hyper-connections-fig11.png]]
*整页渲染: ![[assets/hyper-connections-p20.png]]*
> [!quote] caption
> Training loss curves of ViT/16-Large and ViT/16-Large-DHC×2, smoothed using an

> [!tip] 技术解读（多模态）
> **Figure Description**

The main figure is a line plot titled "Training Loss" comparing two model variants over training. **Components:**
- **X-axis:** Steps (30,000 → 90,000)
- **Y-axis:** Loss (0.2 → 1.8), smoothed via EMA (decay = 0.999)
- **Curves:** Red = ViT/16-Large (baseline); Blue = ViT/16-Large-DHC×2 (augmented with Dynamic Hyper-Connections, expansion factor 2)

Both curves descend smoothly from ~1.8 to ~0.25, with the DHC variant tracking slightly below the baseline throughout. The gap is widest in the mid-training region (50k–70k steps) and narrows toward the end.

**Key Technical Takeaway:** Hyper-Connections provide a small but consistent loss reduction over the baseline; however, the advantage shrinks late in training, indicating diminishing returns as the model converges on repeated dataset passes.

**Caption (verbatim):**
"Figure 11: Training loss curves of ViT/16-Large and ViT/16-Large-DHC×2, smoothed using an Exponential Moving Average (EMA) with a decay rate of 0.999. The gain from Hyper-Connections decreases as training progresses, likely due to pass over the same dataset across many epochs, resulting in diminishing returns from the additional capacity provided by Hyper-Connections."

### Figure 12 (p.21) ⭐深度解读
![[assets/crops/hyper-connections-fig12.png]]
*整页渲染: ![[assets/hyper-connections-p21.png]]*
> [!quote] caption
> Distribution of weights of last DHC in ViT-Base/16-DHC×2 model. F MORE VISUALIZATION AND ANALYSIS

> [!tip] 技术解读（多模态）
> **Description of the main figure:**

The figure is a grid of frequency histograms (7 rows × 3 columns) visualizing the distribution of learned weights in the last Dynamic Hyper-Connection (DHC) layer of a ViT-Base/16-DHC×2 model. The three columns correspond to three ImageNet classes rendered in distinct colors: "33:loggerhead turtle" (blue), "998:capitulum" (green), and "779:school bus" (orange). The rows display histograms for seven distinct weight parameters of the DHC module — β₁, β₂, α_{1,0}, α_{1,1}, α_{1,2}, α_{2,0}, and α_{2,1} — with frequency on the y-axis and parameter value on the x-axis. The β weights cluster near their endpoints (~0.95 and ~1.20), while α weights span continuous ranges, and the "school bus" class shows a sharp, narrow concentration at the lower bound, indicating strong class-specific specialization of connection weights.

**Caption verbatim:**

Figure 12: Distribution of weights of last DHC in ViT-Base/16-DHC×2 model.

### Figure 13 (p.22) ⭐深度解读
![[assets/crops/hyper-connections-fig13.png]]
*整页渲染: ![[assets/hyper-connections-p22.png]]*
> [!quote] caption
> Visualization of unfolded connection matrix.

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

The figure comprises two rows of five triangular heatmaps (Figure 13a and 13b), each row showing unfolded connection matrices **C⁽⁰⁾, C⁽¹⁾, C⁽²⁾, C⁽³⁾, C⁽⁴⁾** for the four hyper-hiddens plus the input hidden state. Rows represent target tokens (0–32) and columns represent source tokens (0–32), with color encoding connection strength from −1.0 (blue) to +1.0 (red). (a) corresponds to the **DHC model** and (b) to the **SHC model**. Vertical green tick marks flag attention layers (odd-indexed). The lower-triangular structure reflects causal token dependencies; visible vertical stripes indicate long-range skip connections across layers.

**Key takeaway:** SHC reproduces DHC's connection patterns exactly but exhibits more PTB-like blocks (e.g., layers 13–18), enabling token-independent parallelization.

**Caption (verbatim):**

Figure 13: **Visualization of unfolded connection matrix.** Matrices from left to right are **C⁽⁰⁾**(Connections for {**h₀ʲ**}ⱼ₌₀^{L+1}), **C⁽ⁱ⁾** (Connections for {**hᵢʲ**}ⱼ₌₀^{L+1}) for *i* ∈ {1, 2, 3, 4}. The attention layers, which have odd ids, are marked with green tick marks. (a) Connection matrix for DHC model. (b) Connection matrix for SHC model.

### Figure 14 (p.23) ⭐深度解读
![[assets/crops/hyper-connections-fig14.png]]
*整页渲染: ![[assets/hyper-connections-p23.png]]*
> [!quote] caption
> Comparison of unfolded connection matrices for OLMo-1B-DHC×1, OLMo-1B-DHC×2 and OLMo-1B-DHC×4 model.

> [!tip] 技术解读（多模态）
> **Figure Description:**

The figure presents three triangular heatmaps (a, b, c) visualizing unfolded inter-layer connection matrices for OLMo-1B variants with different DHC (Dynamic Hybrid Connection) scaling factors (×1, ×2, ×4). Both axes index layers 0–32; cell color encodes connection weight from −1.00 (blue) to +1.00 (red). The lower-triangular structure reflects how earlier layers can route signals forward to later layers. Panel (a) shows a sparse pattern with an arrow highlighting a "wasted" layer 17 that has no outgoing connections, while panels (b) and (c) exhibit denser, more uniform triangular connectivity.

**Key technical takeaway:** HC×1 fails because the matrix lacks the Λ-shaped pattern and drops a layer (here, layer 17) entirely, causing gradient vanishing akin to post-norm transformers; scaling to ×2 or ×4 restores the full triangular connectivity needed for stable training.

**Caption (verbatim):**
Figure 14: Comparison of unfolded connection matrices for OLMo-1B-DHC×1, OLMo-1B-DHC×2 and OLMo-1B-DHC×4 model.

### Figure 15 (p.31) ⭐深度解读
![[assets/crops/hyper-connections-fig15.png]]
*整页渲染: ![[assets/hyper-connections-p31.png]]*
> [!quote] caption
> Training loss curves of related works, smoothed using Exponential Moving Average (EMA) with a decay rate of 0.99. 31

> [!tip] 技术解读（多模态）
> **Figure 15 — Description:**

The figure is a line chart titled "Training Loss" comparing five OLMo-1B architectural variants: baseline OLMo-1B (red), OLMo-1B-ResiDual (blue), OLMo-1B-Altupx2 (green), OLMo-1B-DHCx2 (purple), and OLMo-1B-DHCx2 W/O tanh (orange). The x-axis tracks training progress in Tokens (Billions), spanning ~0–500B, while the y-axis shows Loss from ~2.4 to 2.9. All curves descend monotonically from ~2.88 toward ~2.4, exhibiting visible loss spikes (notably ~100B and ~250B tokens) characteristic of training instabilities. Curves are smoothed via EMA (decay 0.99).

**Key takeaway:** Despite architectural differences, all variants converge to comparable loss (~2.4), with DHCx2 variants achieving marginally lower final loss than baseline and Altupx2, suggesting architectural modifications preserve—and slightly improve—optimization behavior.

**Caption verbatim:**

Figure 15: Training loss curves of related works, smoothed using Exponential Moving Average (EMA) with a decay rate of 0.99.

### Figure 16 (p.32) ⭐深度解读
![[assets/crops/hyper-connections-fig16.png]]
*整页渲染: ![[assets/hyper-connections-p32.png]]*
> [!quote] caption
> Training loss curves of DHC with tanh over 500 billion tokens, smoothed using

> [!tip] 技术解读（多模态）
> **Figure Description (≤120 words):**

Two line plots showing training loss curves. **Components:** Each plot compares five model variants — OLMo-1B (baseline, red), OLMo-1B-DHCx1, x2, x4, and x8 — distinguished by color (blue, green, purple, orange). **Data flow:** Loss values (y-axis, ~2.35–2.60) are plotted against training tokens (x-axis, 0–1000B), smoothed via EMA (decay=0.99). Figure 16 uses DHC with tanh; Figure 17 uses DHC without tanh. Both plots show characteristic downward-concave decay with loss spikes around 250B and 350B tokens (marked by red vertical indicators).

**Key Technical Takeaway:** Higher DHC scaling factors (x4, x8) consistently achieve lower training loss than the OLMo-1B baseline, with the x4 variant reaching the lowest loss in both configurations — demonstrating that DHC improves optimization efficiency regardless of tanh inclusion, though the no-tanh variant (Fig. 17) shows slightly steeper separation between scaling factors.

---

**Caption (verbatim):**

> Figure 16: Training loss curves of DHC with `tanh` over 500 billion tokens, smoothed using Exponential Moving Average (EMA) with a decay rate of 0.99.

> Figure 17: Training loss curves of DHC without `tanh` over 500 billion tokens, smoothed using Exponential Moving Average (EMA) with a decay rate of 0.99.

### Figure 17 (p.32) ⭐深度解读
![[assets/crops/hyper-connections-fig17.png]]
*整页渲染: ![[assets/hyper-connections-p32.png]]*
> [!quote] caption
> Training loss curves of DHC without tanh over 500 billion tokens, smoothed using

> [!tip] 技术解读（多模态）
> **Figure Description (≤120 words):**

Two line plots showing training loss curves. **Components:** Each plot compares five model variants — OLMo-1B (baseline, red), OLMo-1B-DHCx1, x2, x4, and x8 — distinguished by color (blue, green, purple, orange). **Data flow:** Loss values (y-axis, ~2.35–2.60) are plotted against training tokens (x-axis, 0–1000B), smoothed via EMA (decay=0.99). Figure 16 uses DHC with tanh; Figure 17 uses DHC without tanh. Both plots show characteristic downward-concave decay with loss spikes around 250B and 350B tokens (marked by red vertical indicators).

**Key Technical Takeaway:** Higher DHC scaling factors (x4, x8) consistently achieve lower training loss than the OLMo-1B baseline, with the x4 variant reaching the lowest loss in both configurations — demonstrating that DHC improves optimization efficiency regardless of tanh inclusion, though the no-tanh variant (Fig. 17) shows slightly steeper separation between scaling factors.

---

**Caption (verbatim):**

> Figure 16: Training loss curves of DHC with `tanh` over 500 billion tokens, smoothed using Exponential Moving Average (EMA) with a decay rate of 0.99.

> Figure 17: Training loss curves of DHC without `tanh` over 500 billion tokens, smoothed using Exponential Moving Average (EMA) with a decay rate of 0.99.

### Figure 18 (p.33) ⭐深度解读
![[assets/crops/hyper-connections-fig18.png]]
*整页渲染: ![[assets/hyper-connections-p33.png]]*
> [!quote] caption
> Training loss curves comparied with parallel transformer blocks (PTB), smoothed using

> [!tip] 技术解读（多模态）
> **Description (Figure 18 – Training Loss curves):**

The plot is a line graph titled **"Training Loss"** comparing four 1B-parameter model variants during pretraining. The **x-axis** shows training progress in tokens (billions, 0–500), and the **y-axis** shows the smoothed loss (≈2.4–2.9). Four curves are plotted:

- **OLMo-1B** (red) — baseline
- **OLMo-1B-PTB** (blue) — Parallel Transformer Blocks baseline
- **OLMo-1B-DHCx4 W/O tanh** (green) — ablation
- **OLMo-1B-DHCx4** (purple) — proposed DHC variant

All curves descend monotonically with characteristic loss spikes (likely learning-rate warmup/decay steps), and DHCx4 consistently sits below the other variants after ~100B tokens.

**Key takeaway:** DHCx4 yields a lower training loss than both the vanilla OLMo-1B and the Parallel Transformer Blocks baseline, indicating better optimization efficiency without auxiliary compute overhead.

**Caption (verbatim):**
"Figure 18: Training loss curves compared with parallel transformer blocks (PTB), smoothed using Exponential Moving Average (EMA) with a decay rate of 0.99."

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.6) ⭐深度解读
![[assets/crops/hyper-connections-tab01.png]]
> [!quote] caption
> Ablation study on expansion rates n with training on 500 B tokens.

> [!tip] 表格解读（多模态）
> ## Description (102 words)

The figure presents two side-by-side line plots comparing **training loss vs. tokens (100–500 B)** for OLMo-1B variants. The **left subfigure** compares the OLMo-1B-baseline (red) against four Dynamic Hyper-Connections (DHC) variants at expansion rates ×1, ×2, ×4, and ×8. The **right subfigure** replays the same five configurations but with the tanh activation omitted ("W/O tanh"). All curves decay monotonically with characteristic step-downs near 250 B and 350 B tokens, smoothed via an exponential moving average (α = 0.99).

**Key technical takeaway:** Increasing the DHC expansion rate consistently lowers training loss, with DHC×8 yielding the best loss in both subfigures, while removing tanh slightly degrades performance yet preserves the same monotonic expansion-rate ordering.

---

## Caption (verbatim, with cut-off portions)

> …re 5: Comparison of training loss curves for different expansion rate. The left subfigure includ[…]
> …dels with dynamic hyper-connections (DHC) at various expansion rates, while the right subfig[…]
> …s the effect of omitting the tanh function. Both subfigures illustrate how increasing the expan[…]
> …leads to improved training loss performance over 500B tokens. Results are smoothed usin[…]
> …nential moving average with a coefficient of 0.99.

*(Also visible below: "Table 1: Ablation study on expansion rates n with training on 500 B tokens.")*

### Table 2 (p.7) ⭐深度解读
![[assets/crops/hyper-connections-tab02.png]]
> [!quote] caption
> Ablation study on static and dynamic hyper-connections with training on 500 B tokens.

> [!tip] 表格解读（多模态）
> # Main Figure / System Description

**Note:** No figure image is visible in the provided excerpt — only the ablation study text and a table caption. The description below is reconstructed from the text, which references **Fig. 5 (training-loss curves)** and **Table 2 (SHC vs. DHC ablation)**.

### Architecture / Components / Data Flow (inferred)
- **Hyper-Connection (HC) layer** wraps residual connections; each layer produces *n* residual streams (expansion rate *n*).
- **Dynamic HC (DHC):** stream mixing weights *α* (with **tanh** non-linearity) are learned per layer per stream from current activations → input-dependent routing.
- **Static HC (SHC):** the same *α* mixing but weights are fixed/learned independent of input.
- Default config: *n = 4*, tanh activated, suffix **-DHC**.
- Forward flow: input → split into *n* streams → layer computes output → DHC module generates α → tanh(α) re-weights and aggregates *n* stream outputs → next block.

### Key Technical Takeaway
Dynamic Hyper-Connections with *n = 4* deliver the best accuracy–efficiency trade-off: at *n = 4* DHC substantially outperforms SHC and the baseline, while pushing *n* beyond 4 (to *n = 8*) yields marginal gains. Crucially, DHC training losses *monotonically decrease* without the loss spikes seen in baseline runs, indicating improved optimization stability — and the additional parameter/FLOPs overhead is negligible.

### Verbatim Caption
**Table 2:** Ablation study on static and dynamic hyper-connections with training on 500 B tokens.

### Table 7 (p.15) ⭐深度解读
![[assets/crops/hyper-connections-tab07.png]]
> [!quote] caption
> Comparison of number of parameters.

> [!tip] 表格解读（多模态）
> **Description:**

This is **Table 7**, a four-column comparison table titled *"Comparison of number of parameters."* It benchmarks the parameter overhead of adding HC (Hierarchical Compression) modules — specifically **SHC** and **DHC** variants at ×2 and ×4 scales — onto three base language models: **OLMo-1B**, **OLMo-7B**, and the Mixture-of-Experts **OLMoE-1B-7B**. The columns report (1) HC-specific parameter count in billions, (2) total model parameters in billions, and (3) the resulting percentage increase (△ rate) versus the unmodified baseline. Baselines (OLMo-1B, OLMo-7B, OLMoE-1B-7B) have no HC params and no rate change. The full model sizes range from ~1.18B to ~6.92B parameters.

**Key Technical Takeaway (≤120 words):**

The HC modules introduce an **extremely lightweight parameter overhead**, with the largest relative increase being only **+0.03349%** (OLMo-1B-DHC×4). Notably, DHC adds more params than SHC at the same scale (e.g., 0.000394B vs 0.0000077B at ×4), and scaling factor ×4 roughly doubles the overhead compared to ×2. The HC param cost grows negligibly relative to total model size, especially for larger architectures like OLMo-7B (+0.02286%) and OLMoE-1B-7B (+0.00570%). This confirms HC's design philosophy: achieving representational gains via minimal architectural expansion rather than brute-force parameter scaling.

**Verbatim Caption:**

*Table 7: Comparison of number of parameters.*

### Table 8 (p.16) ⭐深度解读
![[assets/crops/hyper-connections-tab08.png]]
> [!quote] caption
> FLOPs per token in forward pass.

> [!tip] 表格解读（多模态）
> The image presents a comparative data table (not an architecture diagram), which I'll describe as requested.

**Architecture/Components/Data Flow:** Table 8 is structured as a 4-column matrix — *Method*, *HC FLOPs (G)*, *Total FLOPs (G)*, and *Total FLOPs Δ rate (%)* — with two horizontal rules separating three model groups: OLMo-1B (5 baseline/HC variants), OLMo-7B (2 rows), and OLMoE-1B-7B Mixture-of-Experts (2 rows). Data flows left→right, isolating the HC module's standalone FLOP cost from the model's total per-token forward-pass cost. Below the table, a "Memory Footprint" paragraph details activation-memory equations.

**Key Technical Takeaway:** Adding HC layers (expansion rate up to ×4) increases total per-token FLOPs by at most +0.208% (OLMoE-1B-7B-DHC×4) and only +0.147% on the 7B model — confirming HC introduces negligible computational overhead while its memory cost can be amortized by discarding/recomputing hidden states, leaving practical training/inference cost effectively unchanged.

**Caption (verbatim):** *Table 8: FLOPs per token in forward pass.*

### Table 9 (p.16) ⭐深度解读
![[assets/crops/hyper-connections-tab09.png]]
> [!quote] caption
> Measured Memory Footprint on 8 GPUs.

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**
The table (Table 9) benchmarks measured GPU memory of baseline OLMo models against their SHC and DHC variants on 8 GPUs, organized into three model families: dense OLMo-1B (micro-batch 16,384), dense OLMo-7B (micro-batch 2,048), and MoE OLMoE-1B-7B (micro-batch 4,096). Columns report Method, Memory (GB), relative Memory Δ Rate (%), and per-GPU micro-batch size. OLMo-1B grows 41.11 → 51.85 GB with SHC×4 (+26.0%) and to 51.86 GB with DHC×4 (+26.1%); OLMo-7B rises +28.28% under DHC×4, whereas the MoE OLMoE-1B-7B incurs only +9.7%. **Key takeaway:** DHC×4 overhead is roughly 3× lower in the Mixture-of-Experts variant (~10%) than in dense OLMo models (~26–28%), showing that this technique scales more favorably when expert routing amortizes the extra hidden-state tensors.

**Caption (verbatim):**
Table 9: Measured Memory Footprint on 8 GPUs.

### Table 10 (p.19) ⭐深度解读
![[assets/crops/hyper-connections-tab10.png]]
> [!quote] caption
> Benchmarking class-conditional image generation on ImageNet 256 × 256, with cfg=1.50. NP , P , and R are short for Numerical Precision, Precision, and Recall, respectively.

> [!tip] 表格解读（多模态）
> **Description of Main Figure (Table 10):**

Table 10 is a benchmarking comparison grid evaluating four DiT (Diffusion Transformer) variants on class-conditional ImageNet generation (256×256, cfg=1.50). Rows enumerate model configurations: DiT-XL/2 (FP32 baseline, 675M), DiT-XL/2 (FP16 + QK-Norm, 675M), DiT-1B/2 (FP16 + QK-Norm, 983M), and DiT-XL/2-SHC×2 (FP16 + QK-Norm, 675M). Columns report hyperparameters—NP, QK-Norm usage, parameter count—and quality metrics: FID↓, sFID↓, IS↑, Precision↑, Recall↑. Arrows denote whether higher or lower is better.

**Key Takeaway:** DiT-XL/2-SHC×2 (675M) matches or beats the larger DiT-1B/2 (983M) on FID/sFID/IS with same precision and QK-Norm—showing hyper-connections recover ~50% more parameters' worth of performance for free.

**Caption (verbatim):**

Table 10: Benchmarking class-conditional image generation on ImageNet 256×256, with cfg=1.50. NP, P, and R are short for Numerical Precision, Precision, and Recall, respectively.

### Table 11 (p.19) ⭐深度解读
![[assets/crops/hyper-connections-tab11.png]]
> [!quote] caption
> Accuracy on ImageNet. ViT*/16 refers to the results reported by (Dosovitskiy et al., 2020), whereas ViT/16 denotes our re-implemented baseline. SHC and DHC indicate that residual connections are replaced with static and dynamic hyper-connections, respectively.

> [!tip] 表格解读（多模态）
> **Description (98 words):**
This results table compares ImageNet top-1 accuracy across Vision Transformer variants under two model scales (Base: 85M params; Large: 307M params). Four configurations are evaluated: ViT*/16 (reference at 384×224), and ViT/16, ViT/16-SHC×2, ViT/16-DHC×2 at 224×224, where the latter two replace residual connections with static and dynamic hyper-connections, respectively. Key finding: dynamic hyper-connections (DHC×2) yield the largest gains, pushing the Large model to 79.94% (bolded) — exceeding both the re-implemented baseline (77.25%) and even the higher-resolution ViT*/16 reference (76.53%). SHC provides intermediate gains (78.38%), suggesting input-dependent connectivity scaling benefits from learned, dynamic routing.

**Caption (verbatim transcription):**
Table 11: Accuracy on ImageNet. **ViT**/16 refers to the results reported by (Dosovitskiy et al., 2020), whereas ViT/16 denotes our re-implemented baseline. SHC and DHC indicate that residual connections are replaced with static and dynamic hyper-connections, respectively.

### Table 12 (p.20) ⭐深度解读
![[assets/crops/hyper-connections-tab12.png]]
> [!quote] caption
> Training hyperparameters for ViT.

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**
The figure is a two-column hyperparameter configuration table for Vision Transformer (ViT) training, listing 10 key settings. The left column enumerates training components (optimizer, scheduler, regularization, augmentation, precision), while the right column specifies their values: a relatively high learning rate (0.003), large batch size (4096), cosine annealing schedule with 10k-step linear warmup, Mixup augmentation (α=0.2), 300 epochs, AdamW optimizer with standard β values and ε=1e−8, gradient clipping at 1.0, strong weight decay (0.3), dropout 0.1, and bf16 mixed-precision training.

**Key takeaway:** The combination of large batch size (4096), high weight decay (0.3), aggressive Mixup (α=0.2), and bf16 precision indicates a recipe optimized for stable, large-scale ViT training where regularization compensates for the high-capacity model.

**Caption (verbatim):**
Table 12: Training hyperparameters for ViT.

### Table 13 (p.30) ⭐深度解读
![[assets/crops/hyper-connections-tab13.png]]
> [!quote] caption
> OLMo’s default configuration was evaluated using multiple metrics. Perplexity (PPL) and loss were used for the V2 and V3 Validation Sets, while zero-shot testing was applied to the Downstream Benchmarks. However, the grey benchmarks were excluded from our analysis due to the instability of their per

> [!tip] 表格解读（多模态）
> **Note:** No figure is present in the provided content—only a table caption (Table 13) under the section heading "Validation Sets and Downstream Tasks." I'll describe what the described table conveys and transcribe its caption verbatim.

**Description of Table 13 (as conveyed by the caption):**

**Components / Data Flow:**
- **Subject:** OLMo's default configuration.
- **Evaluation stream — Validation Sets (V2 and V3):** Metrics used = **Perplexity (PPL)** and **loss**.
- **Evaluation stream — Downstream Benchmarks:** Metric used = **zero-shot testing**.
- **Filtered subset:** Grey benchmarks were excluded from analysis.

**Key Technical Takeaway (≤120 words):**
The table operationalizes a two-pronged evaluation pipeline for OLMo: intrinsic quality is measured on held-out validation corpora via PPL and loss (V2/V3), while task generalization is gauged through zero-shot benchmark scores. Crucially, the authors flag instability in certain downstream indicators—termed "grey benchmarks"—and deliberately drop them, acknowledging that single-shot metric noise could undermine conclusions. This distinction reinforces a best practice: separate intrinsic (likelihood-based) measures from extrinsic (task-based) ones, and disclose any benchmarking artifacts that compromise reproducibility. Result robustness hinges less on which metric scores highest and more on which metrics are trustworthy signals of progress.

**Caption (verbatim):**
"Table 13: OLMo's default configuration was evaluated using multiple metrics. Perplexity (PPL) and loss were used for the V2 and V3 Validation Sets, while zero-shot testing was applied to the Downstream Benchmarks. However, the grey benchmarks were excluded from our analysis due to the instability of their performance indicators."

### Table 14 (p.31) ⭐深度解读
![[assets/crops/hyper-connections-tab14.png]]
> [!quote] caption
> Downstream Benchmarks for OLMoE.

> [!tip] 表格解读（多模态）
> **Main figure description:**

This is not an architecture/data-flow figure but rather **Table 14**, a single-column reference table listing 12 downstream NLP evaluation benchmarks used to assess the OLMoE model. Each row pairs a lowercase task name (e.g., `piqa`, `hellaswag`, `winogrande`, `openbook_qa`, `sciq`, `arc_easy`, `arc_challenage`, `copa`, `boolq`, `commonsense_qa`, `social_iqa`, `mmlu`) with its original citation (e.g., Bisk et al., 2020; Zellers et al., 2019; Hendrycks et al., 2021). The set spans commonsense reasoning (PIQA, HellaSwag, WinoGrande, SocialIQA), science QA (OpenBookQA, SciQ, ARC-Easy/Challenge), reading comprehension (BoolQ), causal reasoning (COPA), and broad knowledge (MMLU, CommonsenseQA).

**Key technical takeaway:** OLMoE is evaluated across a *diverse mix* of ~12 standardized reasoning and knowledge benchmarks rather than a narrow suite, allowing broad generalization claims; notably, "ARC-Challenge" is misspelled as `arc_challenage` in the table.

**Caption transcribed verbatim:**

> **Table 14: Downstream Benchmarks for OLMoE.**

### Table 15 (p.33) ⭐深度解读
![[assets/crops/hyper-connections-tab15.png]]
> [!quote] caption
> Results on downstream benchmarks for 1B models.

> [!tip] 表格解读（多模态）
> **Description:** This is a single-row results table (Table 15) evaluating the OLMo-1B model across seven standard downstream NLP benchmarks, presented as numerical scores with an averaged column. The columns list the model name on the left, followed by benchmark tasks (arc_easy, copa, hellaswag, openbook_qa, piqa, sciq, winogrande), and conclude with an "avg." summary column on the right. The single data row reports OLMo-1B's scores: 56.8 / 76.0 / 56.1 / 33.8 / 74.4 / 85.1 / 55.6, averaging 62.5. There is no architectural diagram or data-flow component — it is purely a benchmark comparison table. **Key takeaway:** OLMo-1B achieves a mean score of 62.5 across reasoning, commonsense, and question-answering tasks, with strongest performance on sciq (85.1) and weakest on openbook_qa (33.8), indicating uneven task generalization at the 1B-parameter scale.

**Caption (verbatim):** Table 15: Results on downstream benchmarks for 1B models.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\left|\theta_{\texttt{SHC}}\right|= |\theta_{\mathbf{B}}| + |\theta_{\mathbf{A}}|= n + n \cdot (n+1)=n \cdot (n+2),
$$

$$
P_{\texttt{extra}}=\left|\theta_{\texttt{SHC}}\right| \times 2 \times L,
$$

$$
P_{\texttt{extra}}=\left|\theta_{\texttt{DHC}}\right| \times 2 \times L,
$$

$$
\mathbf{\hat{h}} = \mathcal{T}(\texttt{Norm}(\mathbf{h})) + \mathbf{h}.
$$

$$
\mathbf{\hat{h}} = \mathcal{T}(\mathbf{h}) + \mathbf{h}.
$$

$$
\mathcal{HC}_{PreNorm}=\begin{pmatrix} 0 & 1 \\ 1 & 1 \\ \end{pmatrix}
$$

$$
\begin{aligned} \mathbf{\hat{H}} &= \mathcal{HC}(\mathcal{T}, \mathbf{H}) \\ &=\mathbf{B}^\intercal\mathcal{T}(\mathbf{H}^\intercal\mathbf{A_m})^\intercal + \mathbf{A_r}^\intercal\mathbf{H} \\ &=\mathcal{T}(\mathbf{h})^\intercal + \mathbf{h}^\intercal \\ &=\mathbf{\hat{h}}^\intercal. \end{aligned}
$$

$$
\mathbf{h}' = \mathcal{T}(\mathbf{h})
$$

$$
\mathbf{\hat{h}} = \texttt{Norm}(\mathbf{h} + \mathbf{h}')
$$

$$
\mathcal{T} = \mathcal{C} \circ \mathcal{T} \circ \mathcal{A},
$$

$$
\mathcal{HC}_{PostNorm}=\begin{pmatrix} 0 & \frac{1}{\sqrt{\sigma_{\mathbf{h}}^2 + \sigma_{\mathbf{h}'}^2 + 2\sigma_{\mathbf{h}\mathbf{h}'}}} \\ 1 & \frac{1}{\sqrt{\sigma_{\mathbf{h}}^2 + \sigma_{\mathbf{h}'}^2 + 2\sigma_{\mathbf{h}\mathbf{h}'}}} \\ \end{pmatrix}=\begin{pmatrix} 0 & \mathbf{B} \\ \mathbf{A}_m & \mathbf{A}_r \\ \end{pmatrix}.
$$

$$
\mathbf{\hat{H}}=\mathbf{\hat{h}}^\intercal.
$$

$$
\sigma_{\mathbf{h} + \mathbf{h}'} = \sqrt{\sigma_{\mathbf{h}}^2 + \sigma_{\mathbf{h}'}^2 + 2\sigma_{\mathbf{h}\mathbf{h}'}}.
$$

$$
\begin{aligned} \mathbf{\hat{h}} &= \text{Norm}(\mathbf{h}' + \mathbf{h}) \\ &= \frac{\mathbf{h}' + \mathbf{h} - \mu_{\mathbf{h}' + \mathbf{h}}}{\sigma_{\mathbf{h} + \mathbf{h}'}} \\ &= \frac{1}{\sigma_{\mathbf{h}' + \mathbf{h}}} (\mathbf{h}' + \mathbf{h}) \\ &= \frac{1}{\sqrt{\sigma_{\mathbf{h}}^2 + \sigma_{\mathbf{h}'}^2 + 2\sigma_{\mathbf{h}\mathbf{h}'}}} (\mathbf{h}' + \mathbf{h}) \end{aligned}
$$

$$
\begin{aligned} \mathbf{\hat{H}} &= \mathbf{B}^\intercal \mathbf{h}'^\intercal + \mathbf{H}' \\ &= \mathbf{B}^\intercal \mathbf{h}'^\intercal + \mathbf{A}_r \mathbf{H} \\ &= \mathbf{B}^\intercal \mathbf{h}'^\intercal + \mathbf{A}_r \mathbf{h}^\intercal \\ &= \frac{1}{\sqrt{\sigma_{\mathbf{h}}^2 + \sigma_{\mathbf{h}'}^2 + 2\sigma_{\mathbf{h}\mathbf{h}'}}} \mathbf{h}'^\intercal + \frac{1}{\sqrt{\sigma_{\mathbf{h}}^2 + \sigma_{\mathbf{h}'}^2 + 2\sigma_{\mathbf{h}\mathbf{h}'}}} \mathbf{h}^\intercal &= \mathbf{\hat{h}}^\intercal. \end{aligned}
$$

$$
\mathcal{HC}=\begin{pmatrix} \mathbf{0}_{1 \times 1} & \mathbf{1}_{1 \times n}\\ \mathbf{e}_1 & \mathbf{e}_{n\times n} \end{pmatrix},
$$

$$
\mathbf{h}_i^{k+1} = \mathbf{h}_j^{k+1}
$$

$$
\mathbf{h}^{k+1}=\sum_{i=1}^{n}(\mathcal{T}^{k\times n+i}(\mathbf{h}^{k}) + \mathbf{h}^k).
$$

$$
\mathcal{HC}^{\{ k \mid k-1 \equiv 0 \pmod{n} \}}= \begin{pmatrix} \mathbf{0}_{1\times 1} & \mathbf{e}_1^\intercal \\ \mathbf{1}_{n\times 1} & \mathbf{1}_{n\times n}, \end{pmatrix}
$$

$$
\mathcal{HC}^{\{ k \mid k-1 \equiv i \pmod{n}, i \neq 0 \}}= \begin{pmatrix} \mathbf{0}_{1\times 1} & \mathbf{e}_i^\intercal \\ \mathbf{e}_i & \mathbf{e}_{n\times n}, \end{pmatrix}.
$$

## 技术点深读（DEEP）

![[deep/hyper-connections]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/hyper-connections.txt`（82287 字符）供引用检索。