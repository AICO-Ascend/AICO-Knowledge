---
paper_num: "65"
title: "Attention Residuals"
authors: ""
date: "2026/3/16"
arxiv: "https://arxiv.org/abs/2603.15031"
pdf: "papers/attention-residuals.pdf"
slug: "attention-residuals"
tags: []
---

# Attention Residuals

> [!abstract] 摘要（原文）
> Residual connections with PreNorm are standard in modern LLMs, yet they accumulate all layer outputs with fixed unit weights. This uniform aggregation causes uncontrolled hidden-state growth with depth, progressively diluting each layer's contribution. We propose Attention Residuals (AttnRes), which replaces this fixed accumulation with softmax attention over preceding layer outputs, allowing each layer to selectively aggregate earlier representations with learned, input-dependent weights. To address the memory and communication overhead of attending over all preceding layer outputs for large-scale model training, we introduce Block AttnRes, which partitions layers into blocks and attends over block-level representations, reducing the memory footprint while preserving most of the gains of full AttnRes. Combined with cache-based pipeline communication and a two-phase computation strategy, Block AttnRes becomes a practical drop-in replacement for standard residual connections with minimal overhead. Scaling law experiments confirm that the improvement is consistent across model sizes, and ablations validate the benefit of content-dependent depth-wise selection. We further integrate AttnRes into the Kimi Linear architecture (48B total / 3B activated parameters) and pre-train on 1.4T tokens, where AttnRes mitigates PreNorm dilution, yielding more uniform output magnitudes and gradient distribution across depth, and improves downstream performance across all evaluated tasks.

## 元信息
- **发表日期**: 2026/3/16
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2603.15031
- **本地 PDF**: `papers/attention-residuals.pdf`
- **页数**: 21

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/attention-residuals-fig01.png]]
*整页渲染: ![[assets/attention-residuals-p01.png]]*
> [!quote] caption
> Overview of Attention Residuals. (a) Standard Residuals: standard residual connections with uniform additive accumulation. (b) Full AttnRes: each layer selectively aggregates all previous layer outputs via learned attention weights. (c) Block AttnRes: layers are grouped into blocks, reducing memory from O(Ld) to O(Nd).[cs.CL] 16 Mar 2026

> [!tip] 技术解读（多模态）
> **Architecture & Data Flow**

The figure compares three residual-connection strategies in a stacked Transformer-MoE block. **(a) Standard Residuals** cascade Attention and MoE layers with fixed additive accumulation (⊕), uniformly mixing all prior outputs. **(b) Full AttnRes** replaces this with softmax attention (Q·K^T over V, ∝-op) so each layer learns input-dependent weights over all preceding representations. **(c) Block AttnRes** groups consecutive layers into blocks (Block n-1, n-2…), attending only over block-level summaries, which lowers memory from O(Ld) to O(Nd) while retaining most of the gain.

**Key Takeaway:** Softmax-weighted, content-dependent aggregation of prior layer outputs mitigates PreNorm dilution, producing more uniform magnitudes and gradient flow across depth than fixed-unit residual accumulation.

---

**Caption (verbatim):**

Figure 1: Overview of Attention Residuals. **(a)** Standard Residuals: standard residual connections with uniform additive accumulation. **(b)** Full AttnRes: each layer selectively aggregates all previous layer outputs via learned attention weights. **(c)** Block AttnRes: layers are grouped into blocks, reducing memory from O(Ld) to O(Nd).

### Figure 2 (p.5) ⭐深度解读
![[assets/crops/attention-residuals-fig02.png]]
*整页渲染: ![[assets/attention-residuals-p05.png]]*
> [!quote] caption
> PyTorch-style pseudo code for Block Attention Residuals. block_attn_res computes softmax attention over block representations using a learned pseudo-query wl; forward is a single-layer pass that maintains partial_block (bi n, intra-block residual) and blocks ([b0, . . . , bn−1], inter-block history).

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

Figure 2 presents two PyTorch functions implementing Block Attention Residuals. `block_attn_res` stacks previously-completed block tensors with the running intra-block partial sum, RMSNorm-normalizes them, then uses a single learned pseudo-query weight `proj` (no per-token queries) to compute softmax attention weights, producing a weighted sum `h`. `forward` runs a single transformer layer while maintaining two residual streams: a `partial_block` (intra-block running sum, reset every `block_size/2` layers) and a `blocks` list (inter-block history, emitted at block boundaries). `block_attn_res` is applied twice per layer — once before self-attention and once before the MLP — so the layer input mixes both histories. **Key takeaway:** collapsing attention sources from L hidden states to N block representations cuts attention memory from O(L) → O(N) and compute from O(L²) → O(N²), with N≈8 reportedly retaining most of Full AttnRes's benefit.

**Caption (verbatim):**

Figure 2: PyTorch-style pseudo code for Block Attention Residuals. block_attn_res computes softmax attention over block representations using a learned pseudo-query w_l; forward is a single-layer pass that maintains partial_block (b_n^i, intra-block residual) and blocks ({b_0, …, b_{n−1}}, inter-block history).

### Figure 3 (p.6) ⭐深度解读
![[assets/crops/attention-residuals-fig03.png]]
*整页渲染: ![[assets/attention-residuals-p06.png]]*
> [!quote] caption
> Cache-based pipeline communication example with 4 physical ranks and 2 virtual stages per rank, where hatched boxes denote end of AttnRes blocks. Numbers indicate micro-batch indices. Each rank caches previously received blocks; stage transitions only transmit incremental blocks (+[b1, b2]) instead of the full history. naïve implementation. During inference, repeated access to accumulated block re

> [!tip] 技术解读（多模态）
> ## Figure Description

The diagram illustrates a **cache-based pipeline communication scheme** for distributed training with 4 physical ranks (rows) and 2 virtual stages per rank (columns).

**Components & Data Flow:**
- Each row = a physical rank processing micro-batches (boxes labeled 1, 2)
- Hatched boxes mark the end of an AttnRes block
- Left column (Virtual Stage 0, pink): full pipeline warm-up where ranks progressively receive accumulated block history in brackets `[b₀]`, `[b₀,b₁]`, etc.
- Arrows show inter-rank transmission along the pipeline (Rank 0 → 1 → 2 → 3)
- Right column (Virtual Stage 1, blue): steady-state where ranks only exchange **incremental** blocks (`+[b₁,b₂]`, `+[b₂,b₃]`) because previously received blocks remain cached locally

**Key Technical Takeaway:** Cross-stage caching reduces per-transition communication from O(C) to O(P)—a **V× speedup**—by re-using locally cached blocks instead of re-sending the full accumulated history at every stage transition, enabling full overlap with computation during steady-state 1F1B.

## Caption (Verbatim)

**Figure 3:** Cache-based pipeline communication example with 4 physical ranks and 2 virtual stages per rank, where hatched boxes denote end of AttnRes blocks. Numbers indicate micro-batch indices. Each rank caches previously received blocks; stage transitions only transmit incremental blocks (+ [b₁, b₂]) instead of the full history.

### Figure 4 (p.9) ⭐深度解读
![[assets/crops/attention-residuals-fig04.png]]
*整页渲染: ![[assets/attention-residuals-p09.png]]*
> [!quote] caption
> Scaling law curves for Attention Residuals. Both Full and Block AttnRes consistently outperform the baseline across all scales. Block AttnRes closely tracks Full AttnRes, recovering most of the gain at the largest scale. PFLOP/s-days, Block AttnRes reaches 1.692 versus the Baseline’s 1.714, equivalent to a 1.25× compute advantage.

> [!tip] 技术解读（多模态）
> ## Figure 4 — Scaling-Law Curves for Attention Residuals

**Chart type:** Log-log scaling-law scatter/fit plot.

**Axes:**
- **X-axis:** PFLOP/s-days (compute), spanning ≈ 0.5 → 5.
- **Y-axis:** Validation Loss, ≈ 1.70 → 1.90.

**Components (three fitted curves with star markers for measured runs):**
| Curve | Color / Style | Power-law fit |
|---|---|---|
| Baseline | Blue dashed | 1.891 × C^(−0.057) |
| Full AttnRes | Red dashed | 1.865 × C^(−0.057) |
| Block AttnRes | Orange dashed | 1.870 × C^(−0.058) |

**Annotations:** A double-headed arrow labeled **"1.25×"** sits between the Baseline curve and the AttnRes curves, indicating the compute-equivalent advantage at the largest measured scale.

**Data flow (interpretation):** Each star is a trained MoE (194M–528M active params, Table 2); curves are least-squares power-law fits on (compute, loss). Baseline sits strictly above both AttnRes variants; Full and Block AttnRes are nearly coincident, with Block AttnRes tightening toward Full AttnRes as compute grows.

**Key takeaway:** Attention Residuals yield a Pareto improvement—roughly a **1.25× compute advantage** at the largest scale—while Block AttnRes recovers most of Full AttnRes's gain, making it a memory-efficient substitute.

**Caption (verbatim):**
> Figure 4: Scaling law curves for Attention Residuals. Both Full and Block AttnRes consistently outperform the baseline across all scales. Block AttnRes closely tracks Full AttnRes, recovering most of the gain at the largest scale.

### Figure 5 (p.10) ⭐深度解读
![[assets/crops/attention-residuals-fig05.png]]
*整页渲染: ![[assets/attention-residuals-p10.png]]*
> [!quote] caption
> Training dynamics of Baseline and Block AttnRes. (a) Validation loss during training. (b) Each transformer block’s output magnitude at the end of training. (c) Each transformer block’s gradient magnitude.

> [!tip] 技术解读（多模态）
> **Main figure description:**

Figure 5 is a 3-panel comparison of a Baseline (blue) vs. Block AttnRes (red) transformer across training metrics. (a) Validation loss vs. step (~20k–110k): AttnRes tracks slightly below Baseline throughout, with the gap widening near the end. (b) Output magnitude vs. block index (0–~27): Baseline magnitudes grow monotonically with depth to ~12 (PreNorm dilution), while AttnRes stays bounded near ~1–2 with a periodic pattern. (c) Gradient magnitude (×10⁻⁵) vs. block index: Baseline shows a huge early-layer spike (~2.4) that decays sharply, whereas AttnRes yields a nearly uniform distribution. 

**Key takeaway:** Block AttnRes fixes PreNorm's hidden-state blow-up and produces balanced gradient flow across depth, yielding consistently lower validation loss.

**Caption (verbatim):**

Figure 5: Training dynamics of Baseline and Block AttnRes. **(a)** Validation loss during training. **(b)** Each transformer block's output magnitude at the end of training. **(c)** Each transformer block's gradient magnitude.

### Figure 6 (p.11) ⭐深度解读
![[assets/crops/attention-residuals-fig06.png]]
*整页渲染: ![[assets/attention-residuals-p11.png]]*
> [!quote] caption
> Effect of block size on validation loss (16-layer model). • Language understanding and reasoning: MMLU [13], MMLU-Pro Hard [55], GPQA-Diamond [41], BBH [48], ARC-Challenge [6], HellaSwag [65], and TriviaQA [21]. • Reasoning (Code and Math): GSM8K [7], MGSM [44], Math [25], CMath [14], HumanEval [5], and MBPP [1]. • Chinese language understanding: CMMLU [26] and C-Eval [19].

> [!tip] 技术解读（多模态）
> **Figure 6 Description**

Figure 6 is a line chart plotting **validation loss (y-axis, ~1.735–1.770)** against **block size S (x-axis: 32, 16, 8, 4, 2)** for a 16-layer transformer. It overlays three series: a gray dashed **Baseline (PreNorm)** at 1.766, a red dashed **Full AttnRes** reference at 1.737 (annotated "i.e. S=1"), and a solid red **Block AttnRes** curve with labeled data points (1.757 → 1.753 → 1.748 → 1.746 → 1.746). Data flow: block size is the only swept hyperparameter; loss is measured on validation set.

**Key takeaway:** Block AttnRes smoothly interpolates between baseline (~1.766) and Full AttnRes (1.737); loss degrades gracefully as S grows, with S=4 already matching S=2 (1.746) — yielding a sweet-spot memory/accuracy trade-off (≈8 blocks per layer).

**Caption (verbatim):**
"Figure 6: Effect of block size on validation loss (16-layer model)."

### Figure 7 (p.12) ⭐深度解读
![[assets/crops/attention-residuals-fig07.png]]
*整页渲染: ![[assets/attention-residuals-p12.png]]*
> [!quote] caption
> Architecture sweep under fixed compute (≈6.5 × 1019 FLOPs, ≈2.3 × 108 active parameters). Each cell reports validation loss for a (dmodel/Lb, H/Lb) configuration, where Lb = L/2 is the number of Transformer blocks; the star marks the optimum.

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

The figure presents two side-by-side heatmaps comparing validation loss across a 5×5 architectural grid: **(a) Baseline** (left) and **(b) Attention Residuals / AttnRes** (right). Axes are model width-per-block `d_model/L_b` ∈ {15, 30, 45, 60, 75} on the x-axis and attention-heads-per-block `H/L_b` ∈ {0.3, 0.4, 0.5, 0.6, 0.7} on the y-axis, where `L_b = L/2` is the number of Transformer blocks. Each cell reports validation loss under a fixed compute budget (≈ 6.5×10¹⁹ FLOPs, ≈ 2.3×10⁸ active parameters), color-coded blue→red (low→high loss), with a star marking each optimum.

**Key takeaway:** Both methods share an optimum at `H/L_b ≈ 0.3`, but AttnRes shifts the width optimum from `d_model/L_b ≈ 60` (loss 1.847) to `d_model/L_b ≈ 45` (loss 1.802) and beats the baseline in all 25 cells by 0.019–0.063 — suggesting AttnRes enables **narrower, deeper-favoring** configurations under fixed compute.

**Caption verbatim:**

> Figure 7: Architecture sweep under fixed compute (≈ 6.5 × 10¹⁹ FLOPs, ≈ 2.3 × 10⁸ active parameters). Each cell reports validation loss for a (d_model/L_b, H/L_b) configuration, where L_b = L/2 is the number of Transformer blocks; the star marks the optimum.

### Figure 8 (p.13) ⭐深度解读
![[assets/crops/attention-residuals-fig08.png]]
*整页渲染: ![[assets/attention-residuals-p13.png]]*
> [!quote] caption
> Depth-wise attention weight distributions for a 16-head model with full (top) and block (bottom) Attention Residuals, averaged over tokens. The model has 16 attention and 16 MLP layers. Each row shows how the lth attention (left) or MLP (right) layer distributes weight over previous sources. Diagonal dominance indicates locality remains the primary information pathway, while persistent weights on 

> [!tip] 技术解读（多模态）
> ## Figure Description

The figure presents a 2×2 grid of heatmaps visualizing the **learned attention residual weights (α_{l→l′})** in a 16-head transformer model. The four panels compare:

- **Top row – Full AttnRes:** Pre-Attn (left) and Pre-MLP (right) weight distributions across 16 layers (rows) over ~30 source positions (columns).
- **Bottom row – Block AttnRes (N=8):** Same Pre-Attn / Pre-MLP split, but with 8 blocks along the source axis (compression via shared parameters).
- A shared **blue colorbar (Weight)** maps intensity 0 → ~0.8.

**Data flow:** Each layer (row) routes its attention/MLP inputs to previous sources/blocks (columns); weights are averaged across 16 heads and tokens. Hatched upper-right regions indicate invalid future sources.

**Key takeaway:** Block-level compression (N=8) yields sharper, more decisive diagonal-dominant weights than the full variant while preserving locality, embedding persistence (source 0), and skip-connection structure—acting as implicit regularization.

## Caption (verbatim)

**Figure 8:** Depth-wise attention weight distributions for a 16-head model with full (top) and block (bottom) Attention Residuals, averaged over tokens. The model has 16 attention and 16 MLP layers. Each row shows how the *l*th attention (left) or MLP (right) layer distributes weight over previous sources. Diagonal dominance indicates locality remains the primary information pathway, while persistent weights on source 0 (embedding) and occasional off-diagonal concentrations reveal learned skip connections. Block attention (*N* = 8) recovers the essential structure with sharper, more decisive weight distributions.

### Figure 9 (p.15) ⭐深度解读
![[assets/crops/attention-residuals-fig09.png]]
*整页渲染: ![[assets/attention-residuals-p15.png]]*
> [!quote] caption
> Depth mixing matrices M for four residual variants (L=4; Block AttnRes uses block size S=2). Highway is shown with scalar gates for clarity. AttnRes panels show unnormalized ϕ scores; background colors group entries that share the same source (Full AttnRes) or the same source block (Block AttnRes). • Standard residual [12], hl = hl−1 + fl−1(hl−1). Expanding gives hl = Pl−1 i=0 vi, so Mi→l = 1 for 

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

The figure presents four depth mixing matrices **M** (L=4) representing how each layer's hidden state composes from earlier layer outputs across different residual variants. Top row: **Highway** uses scalar gates g producing a 1‑semiseparable M with cumulative carry products γ; **(m)HC** uses learned transitions A_l and stream mixers α, β yielding an m‑semiseparable M. Bottom row: **Full AttnRes** computes dense, input-dependent φ(w_i, k_i) scores giving a rank-L M; **Block AttnRes** groups layers into N blocks sharing block-level keys b_n, making M rank between N and N+S. Background colors in the AttnRes panels group entries sharing the same source (Full) or source block (Block).

**Key takeaway:** All four variants collapse into a single linear mixing view M·v, exposing their effective rank (1 → m → N → L) and clarifying that AttnRes is not fundamentally new but a particular instance of structured, input-dependent depth mixing.

**Caption (verbatim):**

Figure 9: Depth mixing matrices **M** for four residual variants (*L*=4; Block AttnRes uses block size *S*=2). Highway is shown with scalar gates for clarity. AttnRes panels show unnormalized φ scores; background colors group entries that share the same source (Full AttnRes) or the same source block (Block AttnRes).

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.8) ⭐深度解读
![[assets/crops/attention-residuals-tab01.png]]
> [!quote] caption
> Memory access cost per token per layer incurred by the residual mechanism under each scheme. The internal I/O of the layer function f l is excluded. For AttnRes, both Full and Block variants use the two-phase inference schedule described in Appendix B ; amortized costs are averaged over N layers wit

> [!tip] 表格解读（多模态）
> **Note:** The page provided contains no figure—only running prose and the caption/header for **Table 1** (a tabular numerical comparison, not a diagram). Accordingly, I cannot describe an architecture, components, or data flow that is not shown. Below I describe what *is* present, structured as requested, and transcribe the caption exactly.

**Description of Table 1 (only artifact shown):** A small numerical table comparing per-token, per-layer memory-access cost (reads/writes in units of *d*, the hidden dimension) across residual-mechanism schemes. Columns correspond to baselines and the proposed *AttnRes* scheme in two variants (Full / Block); rows cover a Phase-1 / Phase-2 split plus an amortized total. **Key takeaway:** by batching residual operations across an *N*-layer block, AttnRes amortizes reads to ≈(N/S + 3)*d* with only 2*d* writes—substantially below (m)HC-style residual generalizations, yielding <2% inference-latency overhead in practice.

**Caption verbatim:**
> Table 1: Memory access cost per token per layer incurred by the residual mechanism under each scheme. The internal I/O of the layer function *f<sub>l</sub>* is excluded. For AttnRes, both Full and Block variants use the two-phase inference schedule described in Appendix B; amortized costs are averaged over *N* layers within a block. Typical values: *L*=128, *N*=8, *S*=*L*/*N*=16, *m*=4.

### Table 2 (p.9) ⭐深度解读
![[assets/crops/attention-residuals-tab02.png]]
> [!quote] caption
> Baseline vs Block AttnRes ( N = 8 ) vs Full AttnRes vs mHC(-lite) [ 64 ]: Model configurations, Hyperparameters, and Validation Loss.

> [!tip] 表格解读（多模态）
> **Description:**

The figure is a results table (Table 2) rather than an architectural diagram, so I'll describe its structure and data:

- **Columns / components:** Three header groups — (1) model configuration: # Act. Params, Tokens, L_b, H, d_model, d_ff, lr, batch size; (2) Val. Loss, split into four variants: Baseline, Block AttnRes, Full AttnRes, mHC(-lite).
- **Rows:** Five model scales (194M → 528M activated parameters), each a different size where depth (L_b), heads (H), width (d_model, d_ff), batch size, and tokens grow monotonically while learning rate decays from 2.99×10⁻³ to 2.02×10⁻³.
- **Data flow:** Each row compares validation loss across the four methods at matched scale; bold cells mark the best loss per row.
- **Key takeaway:** Full AttnRes wins four of five scales (lowest loss across 194M–528M), with mHC(-lite) marginally best only at 241M, suggesting AttnRes is the most consistently competitive residual design across model sizes.

**Caption (verbatim):**

*Table 2: Baseline vs Block AttnRes (N = 8) vs Full AttnRes vs mHC(-lite) [64]: Model configurations, Hyperparameters, and Validation Loss.*

### Table 3 (p.10) ⭐深度解读
![[assets/crops/attention-residuals-tab03.png]]
> [!quote] caption
> Performance comparison of AttnRes with the baseline, both after the same pre-training recipe. Best per-row results are bolded .

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**
This table benchmarks AttnRes against a baseline across 15 downstream tasks organized into three categories: *General* (MMLU, MMLU-Pro, GPQA-Diamond, BBH, ARC-Challenge, HellaSwag, TriviaQA), *Math & Code* (GSM8K, MGSM, Math, CMath, HumanEval, MBPP), and *Chinese* (CMMLU, C-Eval). Each row reports both models' scores, with the best per-row value bolded. **Key takeaway:** Under identical pre-training, AttnRes matches or beats the baseline on virtually every benchmark—notably +7.5 on GPQA-Diamond, +3.1 on HumanEval, +2.9 on C-Eval—with only MMLU-Pro tied. Consistent gains across reasoning, math, code, and Chinese benchmarks suggest AttnRes is a drop-in architectural upgrade requiring no recipe change.

**Caption (verbatim):**
Table 3: Performance comparison of AttnRes with the baseline, both after the same pre-training recipe. Best per-row results are **bolded**.

### Table 4 (p.11) ⭐深度解读
![[assets/crops/attention-residuals-tab04.png]]
> [!quote] caption
> Ablation on key components of AttnRes (16-layer model).

> [!tip] 表格解读（多模态）
> ## Description of Main Figure (Figure 6)

**Architecture/Components:** A line plot showing validation loss (y-axis, range ~1.735–1.770) versus block size *S* (x-axis: 32, 16, 8, 4, 2) on a 16-layer model. It overlays three references: a horizontal gray dashed line for the **Baseline** (1.766), a horizontal red dashed line for the **Full AttnRes** (1.737), and a solid red curve for **Block AttnRes** with annotated points (1.757 → 1.753 → 1.748 → 1.746 → 1.746).

**Data flow:** The curve traces how loss evolves as residual-attention communication between layers becomes finer-grained (smaller S = more frequent cross-layer mixing).

**Key technical takeaway:** Block AttnRes loss decreases monotonically as block size shrinks, plateauing near *S*=4–2 at 1.746—approaching but not matching Full AttnRes (1.737), while substantially beating the 1.766 baseline. This indicates that deeper cross-layer information flow within a 16-layer model is critical, and very fine blocking yields diminishing returns compared to full dense mixing.

## Caption (verbatim)

**Figure 6:** Effect of block size on validation loss (16-layer model).

### Table 5 (p.14) ⭐深度解读
![[assets/crops/attention-residuals-tab05.png]]
> [!quote] caption
> Comparison of residual update mechanisms. Weight : whether the mixing coefficients are architecture-fixed, learned-static (fixed after training), or input-dependent (dynamic). Source : which earlier representations layer l can access. Normalization is omitted from most formulas for clarity.

> [!tip] 表格解读（多模态）
> **Description (≈115 words):**
Table 5 is a taxonomic comparison of residual update mechanisms, structured into three logical groupings separated by horizontal rules: (1) **Single-state recurrence**, where layer *l* receives only **h**_{l−1} (Residual, ReZero, LayerScale, Highway, DeepNorm, KEEL); (2) **Multi-state recurrence**, where layer *l* receives *m* parallel streams (SiameseNorm uses 2 streams; HC/mHC uses *m* streams; DDL uses *d_v* streams, operating on outer products **k**_l **v**_l^⊤); and (3) **Cross-layer access**, where *l* can read arbitrary prior outputs [**h**_1, …, **h**_{l−1}] through concatenation or weighted sums (DenseNet, DenseFormer, MRLA). Four columns—Method, Update rule, Weight (Fixed / Static / Dynamic), Source—encode the data flow and gating behavior. **Key takeaway:** methods are principally differentiated along two axes—*which* prior representations are reachable and *whether* their mixing coefficients are architecture-fixed, learned-static, or input-dynamically modulated.

**Caption (verbatim):**
Table 5: Comparison of residual update mechanisms. *Weight*: whether the mixing coefficients are architecture-fixed, learned-static (fixed after training), or input-dependent (dynamic). *Source*: which earlier representations layer *l* can access. Normalization is omitted from most formulas for clarity.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\bm{h}_{l} = \brickred{\alpha_{0 \to l}} \cdot \bm{h}_1 + \sum_{i=1}^{l-1} \brickred{\alpha_{i \to l}} \cdot f_i(\bm{h}_{i})
$$

$$
\brickred{\alpha_{i \to l}} = \frac{\phi\left(\bm{q}_{l}, \bm{k}_{i}\right)}{\sum_{j=0}^{l-1} \phi\left(\bm{q}_{l}, \bm{k}_{j}\right)}
$$

$$
\bm{q}_{l} = \bm{w}_{l}, \quad \quad \bm{k}_{i} = \bm{v}_{i} = \begin{cases} \bm{h}_1 & i = 0 \\ f_i(\bm{h}_{i}) & 1 \leq i \leq l-1 \end{cases}
$$

$$
\bm{h}_{l} = \sum_{i=0}^{l-1} \brickred{\alpha_{i \to l}} \cdot \bm{v}_{i}
$$

$$
\bm{b}_n = \sum_{j \in \mathcal{B}_n} f_j(\bm{h}_j)
$$

$$
\mathbf{V} = \begin{cases} [\bm{b}_0, \bm{b}_1, \ldots, \bm{b}_{n-1}]^\top & \text{if } i = 1 \text{ (first layer of block } n\text{)} \\ [\bm{b}_0, \bm{b}_1, \ldots, \bm{b}_{n-1}, \bm{b}_n^{i-1}]^\top & \text{if } i \geq 2 \text{ (subsequent layers)} \\ \end{cases}
$$

$$
\mathrm{Comm}_{\text{na\"ive}} = \sum_{j=1}^{C-1} jN_p \cdot d = \frac{C(C{-}1)}{2}\,N_p d.
$$

$$
\mathrm{Comm}_{\text{cached}} = \underbrace{\frac{P(P{-}1)}{2}\, N_p d}_{\text{first virtual stage}} + \underbrace{(V{-}1)\, P^2\, N_p d}_{\text{subsequent virtual stages}}.
$$

$$
\mathbf{W}_t = \mathbf{W}_{t-1} - \eta\,\nabla\ell(\mathbf{W}_{t-1};\, \bm{x}_t),
$$

$$
\mathbf{M}_{i \to l} = \bm{\beta}_{i}^\top \, \mathbf{A}_{i+1 \to l}^{\times} \, \bm{\alpha}_{l},
$$

$$
\mathrm{Read}_{\text{inter}}^{(n)} = 2(n-1)Sd,
$$

$$
\mathrm{Read}_{\text{inter}} = \sum_{n=1}^{N} 2(n-1)Sd = 2Sd \cdot \frac{N(N-1)}{2} = dL(N-1).
$$

$$
\mathrm{Write}_{\text{inter}} = Ld
$$

$$
\mathrm{Read}_{\text{intra}}^{(n)} = \sum_{t=1}^{S} 2(t-1)d = S(S-1)d.
$$

$$
\mathrm{Read}_{\text{total}} = dL(N-1) + N \cdot S(S-1)d, \qquad \mathrm{Write}_{\text{total}} = 2Ld.
$$

$$
\text{Read per layer} = (N-1)d + (S-1)d = (S + N - 2)d, \qquad \text{Write per layer} = 2d,
$$

$$
\boxed{\;\text{Total I/O per layer} = (S + N)\,d.\;}
$$

$$
\begin{bmatrix} \bm{h}_1 \\ \bm{h}_2 \\ \vdots \\ \bm{h}_L \end{bmatrix} = \begin{bmatrix} 1 & & & \\ 1 & 1 & & \\ \vdots & \vdots & \ddots & \\ 1 & 1 & \cdots & 1 \end{bmatrix} \begin{bmatrix} \bm{v}_0 \\ \bm{v}_1 \\ \vdots \\ \bm{v}_{L-1} \end{bmatrix}
$$

$$
\mathbf{H}_{l} = \mathbf{H}_{l-1} \mathbf{A}_{l} + f_{l-1}(\mathbf{H}_{l-1} \bm{\alpha}_{l-1})\, \bm{\beta}_{l-1}^\top,
$$

## 技术点深读（DEEP）

![[deep/attention-residuals]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/attention-residuals.txt`（73664 字符）供引用检索。