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
![[assets/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-p04.png]]
> [!quote] caption
> 3.1

> [!tip] 技术解读（多模态）
> # Note on Figure Availability

The image provided shows **page 4 of the paper containing only text** (sections 2.2 and 3.1 with equations). **Figure 1 itself is not visible** in the supplied image — it is only referenced ("The overall architecture is illustrated in Figure 1"). Without seeing the actual figure, I cannot transcribe its caption verbatim. Below I reconstruct the architecture from the in-text description and equations (Eqs. 1–4):

## Architecture Description (from §3.1)

**Four-stage data flow:**
1. **Encoding (H = E(X))** — extracts fine-grained token representations from input X.
2. **Dynamic Segmentation (C = S(H))** — detects semantic boundaries and pools tokens into variable-length concept chunks.
3. **Concept-Level Reasoning (Z = M(C))** — performs deep computation on the compressed concept sequence.
4. **Token-Level Decoding (Y = D(H, Z))** — reconstructs token predictions by attending to both original token states H and reasoned concepts Z.

**Key takeaway:** DCLM is a *decoder-only* adaptation of H-Net's hierarchical concept reasoning — boundaries are learned end-to-end (no fixed sentence priors), and token decoding is conditioned jointly on raw token encodings **and** compressed concept representations, enabling adaptive compute allocation in standard autoregressive LLMs.

## Verbatim Transcription

**Caption:** *Not visible in the provided image.*

**Equations from §3.1 (verbatim):**
| Equation | Label | Number |
|---|---|---|
| H = E(X) | (Encoding) | (1) |
| C = S(H) | (Segmentation & Pooling) | (2) |
| Z = M(C) | (Concept Reasoning) | (3) |
| Y = D(H, Z) | (Decoding) | (4) |

If you can share the page containing Figure 1, I can provide the actual caption transcription.

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