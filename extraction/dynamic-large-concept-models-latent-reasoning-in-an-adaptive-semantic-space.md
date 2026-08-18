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

### Figure 1 (p.4)
![[assets/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-p04.png]]
> [!quote] caption
> 3.1

### Figure 9 (p.7)
![[assets/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-p07.png]]
> [!quote] caption
> 4.3

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