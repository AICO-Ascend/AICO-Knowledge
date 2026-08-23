---
paper_num: "20"
title: "DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence"
authors: "Towards Highly Efficient Million-Token Context Intelligence DeepSeek-AI research@deepseek.com"
date: "2026/4/28"
arxiv: "https://arxiv.org/abs/2606.19348"
pdf: "papers/deepseek-v4-towards-highly-efficient-million-token-context-intelligence.pdf"
slug: "deepseek-v4-towards-highly-efficient-million-token-context-intelligence"
tags: [long-context]
---

# DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence

> [!abstract] 摘要（原文）
> 1\. 🚀 DeepSeek-V4 系列模型，包括 DeepSeek-V4-Pro 和 DeepSeek-V4-Flash，支持百万级上下文长度，并采用混合注意力机制（CSA 和 HCA）显著提升了长上下文处理效率，相比 DeepSeek-V3.2 大幅降低了 FLOPs 和 KV 缓存占用。 2. 💡 该系列在架构上引入了流形约束超连接 (mHC) 以增强残差连接，并采用 Muon 优化器以实现更快收敛和更高训练稳定性。 3. 🏆 DeepSeek-V4-Pro-Max 在核心任务上重新定义了开放模型的领先水平，其能力通过专家训练和策略蒸馏 (OPD) 的两阶段后训练流程得到整合与增强。

## 元信息
- **发表日期**: 2026/4/28
- **作者**: Towards Highly Efficient Million-Token Context Intelligence DeepSeek-AI research@deepseek.com
- **arXiv**: https://arxiv.org/abs/2606.19348
- **本地 PDF**: `papers/deepseek-v4-towards-highly-efficient-million-token-context-intelligence.pdf`
- **页数**: 58

## 图表（原文 caption + 页码）

### Figure 1 (p.14) ⭐深度解读
![[assets/crops/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-fig01.png]]
*整页渲染: ![[assets/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-p14.png]]*
> [!quote] caption
> 2.4. Muon Optimizer

> [!tip] 技术解读（多模态）
> **1) 架构/组件/数据流描述（≤150字）**

算法流程：梯度计算 → 动量累积（Nesterov） → 混合Newton-Schulz正交化（10步：8步快速收敛+2步稳定） → 更新矩阵RMS重缩放（复用AdamW超参） → 权重衰减更新。双优化器策略：嵌入层、预测头、RMSNorm、mHC门控与静态偏置保留AdamW，其余模块统一用Muon。注意力侧通过对Q与KV做RMSNorm，使logits不再爆炸，从而弃用QK-Clip。

**2) 关键技术要点**

混合Newton-Schulz双阶段系数策略：前8步用 *(3.4445, 4.7750, 2.0315)* 快速把奇异值推向1，后2步切换为 *(2, 1.5, 0.5)* 精细稳定到1，兼顾收敛速度与数值精度。

**3) Caption 逐字转录**

```
Algorithm 1  Muon Optimizer for DeepSeek-V4

Require: Learning rate η, momentum β, weight decay ω, update rescaling factor W
 1: for each training step B do
 2:    for each logically independent weight, matrix R^(l,n) do
 3:       G = ∇_B L_B, B ← B                              Compute gradients
 4:       "M_B = β·"M_B + B                                 Accumulate momentum buffer
 5:       O_B = HybridNewtonSchulz("M_B, β, B)             Nesterov trick and hybrid Newton-Schulz
 6:       $B = $O_B / max(||·||,<,,"·W                     Rescale the update RMS
 7:       θ_B = θ_B − η·1"·[θ_B − ω·[$_B                   Perform weight decay and update
 8:    end for
 9: end for
```

（注：原图中第6–7行部分符号（带 "*""[]""$" 等字形）疑似 PDF 字体渲染异常；其中 `1""·` 应为 `1ᵀ·`（转置），`||·||<,,"` 应为更新矩阵的谱范数 `||·||_σ`，`[$_B` 应为 `θ_B` 的旧值项的标量系数。具体数学符号请以原文 PDF 为准。）

### Figure 5 (p.15) ⭐深度解读
![[assets/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-p15.png]]
> [!quote] caption
> This forms a fine-grained pipeline among experts, keeping both computation and communication continuous throughout the wave. The wave-based scheduling speeds up the 15

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】DeepSeek-V4 细粒度 EP(Fig.5)：MoE 层拆 Dispatch/Linear-1/Linear-2/Combine 四段。Comet 仅粗粒度重叠 Dispatch↔L1、L2↔Combine；本方案把 expert 再切 wave，一波 dispatch 完即开算、下一波并行 dispatch→稳态下「当前波计算+下一波 token 传输+上一波结果回送」三路并发=连续计算-通信流水。因单层通信<计算，融合成单流水 kernel 藏住互连延迟→低带宽互连也不掉吞吐。架构核心图，与 MoE/EP 相关。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
X_{l+1} = B_{l} X_l + C_{l} \mathcal{F}_{l}(A_{l} X_l),
$$

$$
B_l \in \mathcal{M} \coloneq \{ M \in \mathbb{R}^{n \times n} \mid M\mathbf{1}_n = \mathbf{1}_n, \; \mathbf{1}_n^T M = \mathbf{1}_n^T, \; M \geq 0 \}.
$$

$$
M^{(t)} = \mathcal{T}_r(\mathcal{T}_c(M^{(t-1)})),
$$

$$
\mathcal{C}^{\text{SprsComp}}_t = \left\{ C^{\text{Comp}}_{s} ~\Big|~ I_{t, s} \in \operatorname{Top-k} (I_{t, :}) \right\}.
$$

$$
[\mathbf{q}_{t, 1};\mathbf{q}_{t, 2};...;\mathbf{q}_{t, n_{h}}] = \mathbf{q}_{t} = \mathbf{c}_{t}^{Q} \cdot W^{UQ},
$$

$$
\mathbf{o}_{t,i} = \operatorname{CoreAttn}\left( \texttt{query=}\mathbf{q}_{t,i}, \texttt{key=}\mathcal{C}^{\text{SprsComp}}_t, \texttt{value=}\mathcal{C}^{\text{SprsComp}}_t \right),
$$

$$
s_{h, i, j} = \frac{\operatorname{Exp}(z_{h, i, j})}{\sum_k \operatorname{Exp}(z_{h, i, k}) + \operatorname{Exp}(z^{\prime}_h)},
$$

$$
M_k = a M_{k-1} + b (M_{k-1} M_{k-1}^T) M_{k-1} + c (M_{k-1} M_{k-1}^T)^2 M_{k-1}.
$$

$$
\mathcal{L}_{\text{OPD}}(\theta) = \sum_{i=1}^{N} w_i \cdot \text{D}_{\text{KL}} \left( \pi_{\theta} \parallel \pi_{E_i} \right).
$$

$$
\tilde{A}_l &= \alpha_l^\mathrm{pre} \cdot (\hat{X}_l W^\mathrm{pre}_l) + S_l^\mathrm{pre}, \\ \tilde{B}_l &= \alpha_l^\mathrm{res} \cdot \operatorname{Mat}(\hat{X}_l W^\mathrm{res}_l) + S_l^\mathrm{res}, \\ \tilde{C}_l &= \alpha_l^\mathrm{post} \cdot (\hat{X}_l W^\mathrm{post}_l)^T + S_l^\mathrm{post},
$$

$$
A_l &= \sigma(\tilde{A}_l), \\ C_l &= 2\sigma(\tilde{C}_l).
$$

$$
C^{a} &= H \cdot W^{aKV}, \quad C^{b} = H \cdot W^{bKV}, \\ Z^{a} &= H \cdot W^{aZ}, \quad~~ Z^{b} = H \cdot W^{bZ},
$$

$$
[S^a_{mi:m(i+1)-1};S^b_{m(i-1):mi-1}] &= \operatorname{Softmax}_{\text{row}}([Z^{a}_{mi:m(i+1)-1} + B^a;Z^{b}_{m(i-1):mi-1} + B^b]), \\ C^{\text{Comp}}_{i} &= \sum_{j=mi}^{m(i+1)-1} S^a_j \odot C^{a}_{j} + \sum_{j=m(i-1)}^{mi-1} S^b_j \odot C^{b}_{j},
$$

$$
\mathbf{c}_{t}^{Q} &= \mathbf{h}_{t} \cdot W^{DQ}, \\ [\mathbf{q}_{t, 1}^{I};\mathbf{q}_{t, 2}^{I};...;\mathbf{q}_{t, n_{h}^{I}}^{I}] = \mathbf{q}_{t}^{I} &= \mathbf{c}_{t}^{Q} \cdot W^{IUQ},
$$

$$
[w_{t, 1}^I; w_{t, 2}^I; ...; w_{t, n_{h}^{I}}^I] = \mathbf{w}_t^I & = \mathbf{h}_{t} \cdot W^w, \\ I_{t, s} & = \sum_{h=1}^{n_h^I} w_{t, h}^I \cdot \text{ReLU}\left(\mathbf{q}^{I}_{t, h} \cdot K^{\text{IComp}}_{s}\right),
$$

$$
C &= H \cdot W^{KV}, \\ Z &= H \cdot W^{Z},
$$

$$
S_{m^{\prime}i:m^{\prime}(i+1)-1} &= \operatorname{Softmax}_{\text{row}}(Z_{m^{\prime}i:m^{\prime}(i+1)-1} + B), \\ C^{\text{Comp}}_{i} &= \sum_{j=m^{\prime}i}^{m^{\prime}(i+1)-1} S_j \odot C_{j}.
$$

$$
\mathbf{c}_{t}^{Q} &= \mathbf{h}_{t} \cdot W^{DQ}, \\ [\mathbf{q}_{t, 1};\mathbf{q}_{t, 2};...;\mathbf{q}_{t, n_{h}}] = \mathbf{q}_{t} &= \mathbf{c}_{t}^{Q} \cdot W^{UQ},
$$

## 相关论文

- [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] — LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and Verification

## 技术点深读（DEEP）

![[deep/deepseek-v4-towards-highly-efficient-million-token-context-intelligence]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/deepseek-v4-towards-highly-efficient-million-token-context-intelligence.txt`（45725 字符）供引用检索。