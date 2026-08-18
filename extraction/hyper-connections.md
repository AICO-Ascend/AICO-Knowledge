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
![[assets/hyper-connections-p01.png]]
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
![[assets/hyper-connections-p02.png]]
> [!quote] caption
> Hyper-connections (HC) with an expansion rate of n = 2. (a) Residual connections. (b) Hyper-connections: β1, β2, α0,0, α0,1, α1,0, α1,1, α2,1, and α2,2 are learnable scalars or scalars predicted by the network , depending on the specific HC version. These connections enable lateral information exchange and vertical integration of features across depths. The Transformer with HC is shown in Fig. 17.

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】Hyper-Connections 架构(Fig.2)：(a) 传统残差连接=层输出与单隐层 h 求和；(b) HC n=2 把输入复制成两个隐向量 h1/h2，层输出经可学习标量(β,α)路由回→加权连接矩阵灵活跨深+宽组合特征。解耦成 (c) depth-connections（层输出与 h1 加权和）+ (d) width-connections（h1/h2 横向混合）。核心：用可学习、输入依赖的路由替固定恒等 skip，让网络自主调制 skip 强度→缓解固定 Pre/Post-Norm 残差的表征塌缩+梯度消失。架构核心图。

### Figure 3 (p.2) ⭐深度解读
![[assets/hyper-connections-p02.png]]
> [!quote] caption
> Cosine similarity be- tween the input of the current and the previous layers for the OLMo-1B models (Groeneveld et al., 2024). The curve represents the median of similarity, while the shaded area indicates the range be- tween the 5th and 95th percentiles.

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】Hyper-Connections 架构(Fig.2)：(a) 传统残差连接=层输出与单隐层 h 求和；(b) HC n=2 把输入复制成两个隐向量 h1/h2，层输出经可学习标量(β,α)路由回→加权连接矩阵灵活跨深+宽组合特征。解耦成 (c) depth-connections（层输出与 h1 加权和）+ (d) width-connections（h1/h2 横向混合）。核心：用可学习、输入依赖的路由替固定恒等 skip，让网络自主调制 skip 强度→缓解固定 Pre/Post-Norm 残差的表征塌缩+梯度消失。架构核心图。

### Figure 4 (p.5) ⭐深度解读
![[assets/hyper-connections-p05.png]]
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

### Figure 5 (p.6)
![[assets/hyper-connections-p06.png]]
> [!quote] caption
> Comparison of training loss curves for different expansion rate. The left subfigure includes models with dynamic hyper-connections (DHC) at various expansion rates, while the right subfigure shows the effect of omitting the tanh function. Both subfigures illustrate how increasing the expansion rate leads to improved training loss performance over 500B tokens. Results are smoothed using an exponent

### Figure 6 (p.8)
![[assets/hyper-connections-p08.png]]
> [!quote] caption
> (1) and (2) Training loss (0.99 EMA smoothed) and C4-en validation loss for OLMo-7B and OLMo-7B-DHC×4 models. (3) and (4) Accuracy curves on hellaswag and sciq, demonstrating the superior performance of the OLMo-7B-DHC×4 model.

### Figure 7 (p.9)
![[assets/hyper-connections-p09.png]]
> [!quote] caption
> Visualization of connection matrices for hyper-connections and various related baseline methods. The attention layers, which have odd ids, are marked with green tick marks.

### Figure 8 (p.14)
![[assets/hyper-connections-p14.png]]
> [!quote] caption
> Comparison between transformers with hyper-connections and that with residual connec- tions. 14

### Figure 9 (p.17)
![[assets/hyper-connections-p17.png]]
> [!quote] caption
> Loss curves in V3 validation sets and accuracy curves on downstream tasks for OLMoE-1B7B and OLMoE-1B7B-DHC×4 models. 17

### Figure 10 (p.18)
![[assets/hyper-connections-p18.png]]
> [!quote] caption
> Loss curves in V3 validation set and accuracy curves on downstream tasks for OLMo-7B and OLMo-7B-DHC×4 models. 18

### Figure 11 (p.20)
![[assets/hyper-connections-p20.png]]
> [!quote] caption
> Training loss curves of ViT/16-Large and ViT/16-Large-DHC×2, smoothed using an

### Figure 12 (p.21)
![[assets/hyper-connections-p21.png]]
> [!quote] caption
> Distribution of weights of last DHC in ViT-Base/16-DHC×2 model. F MORE VISUALIZATION AND ANALYSIS

### Figure 13 (p.22)
![[assets/hyper-connections-p22.png]]
> [!quote] caption
> Visualization of unfolded connection matrix.

### Figure 14 (p.23)
![[assets/hyper-connections-p23.png]]
> [!quote] caption
> Comparison of unfolded connection matrices for OLMo-1B-DHC×1, OLMo-1B-DHC×2 and OLMo-1B-DHC×4 model.

### Figure 15 (p.31)
![[assets/hyper-connections-p31.png]]
> [!quote] caption
> Training loss curves of related works, smoothed using Exponential Moving Average (EMA) with a decay rate of 0.99. 31

### Figure 16 (p.32)
![[assets/hyper-connections-p32.png]]
> [!quote] caption
> Training loss curves of DHC with tanh over 500 billion tokens, smoothed using

### Figure 17 (p.32)
![[assets/hyper-connections-p32.png]]
> [!quote] caption
> Training loss curves of DHC without tanh over 500 billion tokens, smoothed using

### Figure 18 (p.33)
![[assets/hyper-connections-p33.png]]
> [!quote] caption
> Training loss curves comparied with parallel transformer blocks (PTB), smoothed using

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