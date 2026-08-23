---
paper_num: "29"
title: "Dynamic Large Concept Models: Latent Reasoning in an Adaptive Semantic Space"
authors: "Adaptive Semantic Space 1ByteDance Seed, 2University of Manchester, 3Mila - Quebec AI Institute, 4Tsinghua University , 5M-A-P"
date: "2026/1/19"
arxiv: "https://arxiv.org/abs/2512.24617"
pdf: "papers/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space.pdf"
slug: "dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space"
tags: []
---

# Dynamic Large Concept Models: Latent Reasoning in an Adaptive Semantic Space

> [!abstract] 摘要（原文）
> 1\. 🌟 Dynamic Large Concept Models (DLCM) 提出了一种分层语言建模框架，通过从潜在表示中学习语义边界，并将计算从 Token 转移到压缩概念空间，以解决大型语言模型中信息密度不均匀的问题。 2. 💡 该模型通过动态分割变长概念并在压缩概念空间中进行深度推理，同时引入了压缩感知缩放律和用于异构模块解耦 μP 参数化，实现了计算资源的自适应分配。 3. 📈 在实际应用中，DLCM 在匹配推理 FLOPs 的情况下，将计算重新分配到更高容量的推理主干网络中，在12个零样本 benchmarks 中平均提高了2.69%，在推理主导型任务上表现尤为突出。

## 元信息
- **发表日期**: 2026/1/19
- **作者**: Adaptive Semantic Space 1ByteDance Seed, 2University of Manchester, 3Mila - Quebec AI Institute, 4Tsinghua University , 5M-A-P
- **arXiv**: https://arxiv.org/abs/2512.24617
- **本地 PDF**: `papers/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space.pdf`
- **页数**: 24

## 图表（原文 caption + 页码）

### Figure 1 (p.4) ⭐深度解读
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-fig01.png]]
*整页渲染: ![[assets/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-p04.png]]*
> [!quote] caption
> 3.1

> [!tip] 技术解读（多模态）
> **Description**

The figure depicts a chunked-compression architecture for efficient transformer inference. **Panel (a)** shows the overall pipeline: input tokens are segmented and pooled into compressed chunks (C₁–C₄), fed through an Encoder whose KV outputs are consumed by a Decoder. **Panel (b)** details boundary detection, where consecutive tokens are merged into a chunk when their similarity metric exceeds a threshold τᵢ, with each token assigned to a chunk. **Panel (c)** illustrates decoder cross-attention, in which query tokens q₁–q₅ selectively attend to only the relevant compressed chunks (here, positions 1, 3, and 4) rather than the full token sequence. **Key takeaway:** boundary-aware pooling shrinks the effective sequence length, reducing KV-cache memory and attention FLOPs while preserving retrieval-relevant granularity for long-context inference.

**Caption verbatim**

(a) Overview Architecture
(b) Boundary Detection & Pooling
(c) Decoder Cross-Attention

### Figure 9 (p.7) ⭐深度解读
![[assets/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-p07.png]]
> [!quote] caption
> 4.3

> [!tip] 技术解读（多模态）
> # Description

**Note:** This page contains no rendered figure—it is a text-heavy section (Sections 3.6, 4, 4.1–4.3) that *references* "Figure 2" (attention mask illustration) and "Figure 9" (speedup plot, not shown). The figure-equivalent content here is the conceptual data flow described in text:

## Architecture / Components / Data Flow (as described)

1. **Inputs:** Tokens t₁…t_L (queries) and concept features c₁…c_M (keys/values), with variable-length mapping where each concept c_j spans a segment of tokens.
2. **Problem:** Ragged attention mask—direct Flex Attention is inefficient due to dynamic mask generation and irregular memory access.
3. **Solution — Concept Replication:** Replicate each concept feature c_j to fill its segment length, producing K̃ = repeat(c, segment_lengths) and Ṽ = repeat(c, segment_lengths). This aligns KV length with query length L.
4. **Compute:** Run FlashAttention's **VarLen** kernel (causal-style self-attention) on the replicated KV, since K/V are locally constant within each segment.
5. **Training loss:** L = L_CE + L_a (cross-entropy + load-balancing, Eq. 15), with RMSNorm on Q and K (Eq. 16).

## Key Technical Takeaway
Concept replication converts irregular concept-token cross-attention into a uniform-length VarLen self-attention problem, yielding **1.26×–1.73× speedup** over Flex Attention by trading a small memory cost for highly optimized CUDA kernels.

## Caption (verbatim from the page)

No figure caption is present on this page. The page's opening line reads:

> "**3.6 Training Objective** — The total loss combines next-token prediction with adaptive compression:
> 
> L = L_CE + L_a       (15)
> 
> where L_CE is cross-entropy on output tokens and L_a is the load-balancing loss."

The only in-line figure references are: *"Figure 2"* (ragged-boundary attention mask) and *"Figure 9"* (plotted speedup T_FA = T_8 ).

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.9) ⭐深度解读
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-tab01.png]]
> [!quote] caption
> Statistics of the pretraining data.

> [!tip] 表格解读（多模态）
> # Description of the Main Figure/Table

**Note:** The image does not contain an architectural diagram but rather **Table 1**, which summarizes the composition of the pretraining data.

**Structure (table layout):**
- **Columns:** Data Source | Ratio | Tokens (B)
- **Rows (4 data sources + Total):**
  1. Nemotron-CC [15] (English Web) — 50% — 500 B tokens
  2. MAP-CC [5] (Chinese Web) — 25% — 250 B tokens
  3. OpenCoder-Pretrain [10] — 15% — 150 B tokens
  4. MegaMath-Web [19] — 10% — 100 B tokens
  5. **Total** — 100% — 1,000 B tokens
- **Data flow implied:** Tokens from four heterogeneous sources are mixed by fixed sampling ratio to form a unified 1T-token pretraining corpus.

**Key takeaway:** The corpus balances general multilingual web text (English+Chinese, 75%) with domain-specific code (15%) and math (10%) data, yielding a total of ~1T tokens.

---

# Verbatim Caption

**Table 1** Statistics of the pretraining data.

| Data Source | Ratio | Tokens (B) |
|---|---|---|
| Nemotron-CC [15] (English Web) | 50% | 500 |
| MAP-CC [5] (Chinese Web) | 25% | 250 |
| OpenCoder-Pretrain [10] | 15% | 150 |
| MegaMath-Web [19] | 10% | 100 |
| Total | 100% | 1,000 |

### Table 2 (p.15) ⭐深度解读
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-tab02.png]]
> [!quote] caption
> Performance Comparison: DLCM vs. Baseline. Zero-shot accuracy (%) categorized by task type. Improvements are shown in green and regressions in red .

> [!tip] 表格解读（多模态）
> **Note:** The image contains **Table 2** (a performance comparison), not an architecture/data-flow figure. I'll describe the table and provide a takeaway.

---

### Table Structure / Data Flow

The table is a side-by-side benchmark comparison organized into **three stacked task groups**:

1. **Commonsense / Reasoning (top block)** — 8 tasks (Commonsense QA, HellaSwag, Winogrande, OpenBookQA, PIQA, ARC Challenge, ARC Easy, MMLU)
2. **Reading Comprehension / NLU (middle block)** — 2 tasks (BoolQ, RACE)
3. **Multilingual / Chinese (bottom block)** — 2 tasks (C-Eval, CMMLU)

Each row carries four cells: **Task**, **DLCM (Ours) score**, **Baseline score**, **Diff.** (color-coded green = gain, red = regression). Bold marks the higher of each pair. A final **Average** row aggregates overall gain (+2.69, green).

### Key Technical Takeaway

DLCM nets a +2.69 average zero-shot gain by winning on boundary-sensitive tasks (PIQA +2.42, OpenBookQA +3.00, C-Eval +1.71) but regresses on dense reading-style tasks (BoolQ −1.47, RACE −0.72), suggesting concept compression strengthens high-level semantic coherence at the cost of fine-grained token precision in mid-sequence regions.

---

### Caption (verbatim)

**Table 2 Performance Comparison: DLCM vs. Baseline.** Zero-shot accuracy (%) categorized by task type. Improvements are shown in green and regressions in red.

### Table 4 (p.17) ⭐深度解读
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-tab04.png]]
> [!quote] caption
> Ablation Study: Global Parser vs. Normal. Performance comparison on downstream tasks. Both models aim for a target compression ratio of R = 4 . The Global Parser achieves a realized ratio much closer to the target while consistently improving accuracy on most tasks.

> [!tip] 表格解读（多模态）
> **Description (Table 4 structure & key takeaway):**

Table 4 is an ablation comparison matrix benchmarking a **Global Parser** model against a **Normal** baseline across six downstream reasoning benchmarks (ARC Challenge, ARC Easy, Commonsense QA, HellaSwag, OpenBookQA, PIQA), all evaluated under Accuracy. Each row reports the model's score; the bottom rows aggregate an average improvement (+2.1%) and the realized compression ratio (3.92 vs. 3.15, target R=4). Bolded cells indicate the per-task winner. Global Parser wins 5/6 tasks, with only OpenBookQA favoring Normal.

**Key takeaway:** A globally-aware parsing strategy delivers a tighter realized compression ratio (3.92 ≈ target 4) *and* a +2.1% mean accuracy gain, showing that ratio fidelity and downstream utility are not in tension.

**Caption (verbatim):**

> **Table 4 Ablation Study: Global Parser vs. Normal.** Performance comparison on downstream tasks. Both models aim for a target compression ratio of R =4. The **Global Parser** achieves a realized ratio much closer to the target while consistently improving accuracy on most tasks.

### Table 5 (p.18) ⭐深度解读
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-tab05.png]]
> [!quote] caption
> Average tokens per concept across content types and compression ratios. Values represent the actual granularity achieved for each target compression setting.

> [!tip] 表格解读（多模态）
> No figure is present in this image.

The image shows only text content from page 18 of the paper:
- **Table 5 caption** (top of page)
- **Section 9: Conclusion** (the body text)
- **Page number 18** (bottom)

There is no main architecture diagram, figure, or visualization rendered in this image — only the textual conclusion discussing Dynamic Large Concept Models (DLCM) and the table caption referencing token granularity across content types/compression ratios.

If you intended to share a figure (e.g., the DLCM architecture diagram showing token → concept hierarchy, or a results plot), the image content did not transmit successfully, or the correct file was not attached. Could you re-upload the figure you'd like described? Once provided, I can:

1. Describe its architecture/components/data flow plus one key technical takeaway (≤120 words)
2. Transcribe the caption verbatim

### Table 6 (p.7) ⭐深度解读
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-tab06.png]]
> [!quote] caption
> provides detailed performance . To more intuitively analyze the performance trends, we have plotted the speedup ( T /T ) in Figure 9 .

> [!tip] 表格解读（多模态）
> **Description of Figure 2 (based on surrounding text, as the figure itself is not visible in the provided image):**

The figure illustrates the **concept replication strategy** for efficient cross-attention. On the conceptual side, concepts c₁ and c₂ map to variable-length token groups (e.g., t_1 maps to c_1, while t_2, t_3 map to c₂), producing a "ragged" attention mask. The figure contrasts this with the replication strategy: each concept feature c_j is expanded along the token dimension (K' and V' via `expand(segment_lengths)`), aligning Key/Value length with Query length (L) so a standard L×L FlashAttention-Varlen kernel can replace an irregular L×M Flex Attention mask.

**Key Technical Takeaway:** Concept replication converts variable-length concept-token mappings into a fixed self-attention shape, enabling hardware-optimal FlashAttention (VarLen) kernels instead of costly dynamic Flex Attention masks.

**Caption (verbatim from the text):**
> "As illustrated in Figure 2, when tokens **t**₋₁g belong to concept c₁, and tokens **t**₋₂, **t**₋₃g belong to c₂, the resulting attention mask effectively has a 'ragged' boundary."

*Note: No standalone figure caption is shown in the provided image—only the in-text reference above. The figure itself is not rendered in the supplied content.*

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf{q}_t = \mathbf{W}_q \mathbf{h}_t, \quad \mathbf{k}_t = \mathbf{W}_k \mathbf{h}_t
$$

$$
p_t = \frac{1 - \cos(\mathbf{q}_{t-1}, \mathbf{k}_t)}{2} = \frac{1}{2} \left( 1 - \frac{\mathbf{q}_{t-1}^{\top}\mathbf{k}_t}{\|\mathbf{q}_{t-1}\|_2 \|\mathbf{k}_t\|_2} \right)
$$

$$
\mathbf{c}_k^{\text{raw}} = \frac{1}{|S_k|} \sum_{t \in S_k} \mathbf{h}_t, \quad \mathbf{c}_k = \mathbf{W}_{\text{up}}\mathbf{c}_k^{\text{raw}}
$$

$$
\mathcal{L}_{\text{aux}} = \frac{R}{R-1} \left[ (R-1) \cdot F_{\text{global}} \cdot G_{\text{global}} + (1 - F_{\text{global}}) \cdot (1 - G_{\text{global}}) \right] - 1
$$

$$
\tilde{\mathbf{Z}} = \mathcal{S}(\mathbf{Z})
$$

$$
\Psi(\mathbf{H}, \mathbf{Z}) = \text{Softmax}\left( \frac{\mathbf{Q}\mathbf{K}^\top}{\sqrt{d_{\text{head}}}} + \mathbf{M} \right) \mathbf{V}\mathbf{W}_O + \mathbf{H}
$$

$$
\mathcal{L} = \mathcal{L}_{\text{CE}} + \lambda \mathcal{L}_{\text{aux}}
$$

$$
\mathbf{Q}' = \text{RMSNorm}(\mathbf{Q}), \quad \mathbf{K}' = \text{RMSNorm}(\mathbf{K})
$$

$$
\tilde{\mathbf{K}} = \texttt{repeat\_interleave}(\mathbf{K}, \text{segment\_lengths}), \quad \tilde{\mathbf{V}} = \texttt{repeat\_interleave}(\mathbf{V}, \text{segment\_lengths})
$$

$$
s_{\text{token}} = \frac{d_{\text{token}}}{d_{\text{base}}}, \quad s_{\text{concept}} = \frac{d_{\text{concept}}}{d_{\text{base}}}
$$

$$
\text{logits} = \frac{1}{s_{\text{token}}} \cdot (\mathbf{h}_{\text{final}} W_{\text{unemb}}^\top)
$$

$$
L(N, D, R, P) = E_0 + \frac{A_{\text{token}}} {(N(1-P) + t_{\text{token}})^{\delta_1}} + \frac{A_{\text{concept}} \, R^{\gamma}} {(NP + t_{\text{concept}})^{\delta_2}} + \frac{A_{\text{data}}} {(D + t_{\text{data}})^{\alpha}}.
$$

$$
\Delta_{\text{decay}} = k \, L_{\text{stable}}^{\,a} R^{\,b} N^{\,c}
$$

$$
\nabla_{\theta} \mathcal{L}_{\text{total}} = \underbrace{\nabla_{\theta} \mathcal{L}_{\text{CE}}}_{\text{anti-compression}} + \lambda \underbrace{\nabla_{\theta} \mathcal{L}_{\text{aux}}}_{\text{pro-compression}}
$$

$$
\mathbf{H} &= \mathcal{E}(\mathbf{x}) && \text{(Encoding)} \\ \mathbf{C} &= \Phi(\mathbf{H}) && \text{(Segmentation \& Pooling)} \\ \mathbf{Z} &= \mathcal{M}(\mathbf{C}) && \text{(Concept Reasoning)} \\ \hat{\mathbf{y}} &= \mathcal{D}(\Psi(\mathbf{H}, \mathbf{Z})) && \text{(Decoding)}
$$

$$
G_{\text{global}} &= \frac{1}{|\mathcal{T}|} \sum_{(i,t) \in \mathcal{T}} p_{i,t} && \text{(expected boundary rate)} \\ F_{\text{global}} &= \frac{1}{|\mathcal{T}|} \sum_{(i,t) \in \mathcal{T}} b_{i,t} && \text{(actual boundary rate)}
$$

$$
\mathbf{Q} &= \mathbf{H}\mathbf{W}_Q, \quad \text{where } \mathbf{W}_Q \in \mathbb{R}^{d_{\text{token}} \times d_{\text{head}}} \\ \mathbf{K} &= \tilde{\mathbf{Z}}\mathbf{W}_K, \quad \mathbf{V} = \tilde{\mathbf{Z}}\mathbf{W}_V, \quad \text{where } \mathbf{W}_{K,V} \in \mathbb{R}^{d_{\text{concept}} \times d_{\text{head}}}
$$

$$
\eta_{\mathcal{E}, \mathcal{D}} &= \eta^{\text{base}}_{\text{token}} \cdot s_{\text{token}}^{-1} \\ \eta_{\mathcal{M}} &= \eta^{\text{base}}_{\text{concept}} \cdot s_{\text{concept}}^{-1}
$$

## 技术点深读（DEEP）

![[deep/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space.txt`（61312 字符）供引用检索。