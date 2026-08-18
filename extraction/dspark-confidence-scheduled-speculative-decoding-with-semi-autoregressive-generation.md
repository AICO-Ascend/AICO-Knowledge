---
paper_num: "8"
title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
authors: "Semi-Autoregressive Generation Xin Cheng1,2,∗, Xingkai Yu2,∗, Chenze Shao2,∗, Jiashi Li2,∗, Yunfan Xiong2,∗ Yi Qian2, Jiaqi Zhu2, Shirong Ma2, Xiaokang Zhang2, Jiasheng Ye2, Qinyu Chen2, Chengqi Deng2, Jiping Yu2, Damai "
date: "2024/1/1"
arxiv: "https://arxiv.org/abs/2607.05147"
pdf: "papers/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation.pdf"
slug: "dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation"
tags: [speculative]
---

# DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation

> [!abstract] 摘要（原文）
> 1\. 🚀 DSpark 引入了一种半自回归生成架构，通过在并行主干网络中集成轻量级序列模块，在保持高吞吐生成速度的同时，有效缓解了传统并行 Draft model 常见的后缀准确率衰减问题。 2. 💡 为了优化系统级效率，DSpark 提出了置信度调度验证（Confidence-Scheduled Verification）机制，利用校准后的生存概率和负载感知调度器，根据实时引擎负载动态分配验证预算，从而最大化整体吞吐量。 3. 📈 大规模生产部署实测表明，DSpark 相比现有工业基线显著扩展了交互边界，在满足严格时延约束的前提下，将生成速度提升了 60%–85%，有效突破了 LLM 在高并发 serving 系统中的性能瓶颈。

## 元信息
- **发表日期**: 2024/1/1
- **作者**: Semi-Autoregressive Generation Xin Cheng1,2,∗, Xingkai Yu2,∗, Chenze Shao2,∗, Jiashi Li2,∗, Yunfan Xiong2,∗ Yi Qian2, Jiaqi Zhu2, Shirong Ma2, Xiaokang Zhang2, Jiasheng Ye2, Qinyu Chen2, Chengqi Deng2, Jiping Yu2, Damai 
- **arXiv**: https://arxiv.org/abs/2607.05147
- **本地 PDF**: `papers/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation.pdf`
- **页数**: 33

## 图表（原文 caption + 页码）

### Figure 1 (p.4)
![[assets/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation-p04.png]]
> [!quote] caption
> Recall from Equation 1 that the per-token latency of speculative decoding is 𝐿= (𝑇draft + 𝑇verify)/𝜏. Autoregressive drafters achieve high 𝜏but pay 𝑇draft ∝𝛾; parallel drafters collapse 𝑇draft to a single pass but sacrifice 𝜏because each position is predicted independently. Meanwhile, fixed-length verification wastes 𝑇verify on low-confidence suffix tokens that are almost certain to be rejected. D

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
P(X \mid x_0) = \prod_{k=1}^{\gamma} p_k(x_k \mid x_0, x_{<k}), \qquad p_k(v \mid x_0, x_{<k}) = \frac{ \exp\!\left(U_k(v) + B_k(x_0, x_{<k}, v)\right) }{ \sum_{u \in \mathcal{V}} \exp\!\left(U_k(u) + B_k(x_0, x_{<k}, u)\right) }.
$$

$$
B(x_{k-1},\, \cdot\,) = W_1[x_{k-1}] \, W_2 \;\in\; \RR^{V},
$$

$$
\begin{aligned} s_k = \sigma(W_g\, z_k)& \odot s_{k-1} \;+\; \bigl(1 - \sigma(W_g\, z_k)\bigr) \odot \tanh(W_c\, z_k), \\ &B_k(x_{<k},\, \cdot\,) = W_2^\top\, \tanh(W_o\, z_k), \end{aligned}
$$

$$
c_k = \sigma\bigl(w^\top [h_k;\, W_1[x_{k-1}]]\bigr),
$$

$$
c_k^* = 1 - \tfrac{1}{2}\|p_k^d - p_k^t\|_1.
$$

$$
\Ll_{\text{ce}} = -\sum_{k=1}^{\gamma} w_k \log p^d_{k}(x_k^*),
$$

$$
\Ll_{\text{tv}} = \sum_{k=1}^{\gamma} w_k \|p_k^d - p_k^t\|_1.
$$

$$
\Ll_{\text{conf}} = -\sum_{k=1}^{\gamma} w_k \bigl[c_k^* \log c_k + (1 - c_k^*) \log(1 - c_k)\bigr].
$$

$$
\Ll = \alpha_{\text{ce}}\,\Ll_{\text{ce}} + \alpha_{\text{tv}}\,\Ll_{\text{tv}} + \alpha_{\text{conf}}\,\Ll_{\text{conf}}
$$

$$
L = \frac{T_{\text{draft}} + T_{\text{verify}}}{\tau}.
$$

$$
H_{\text{ctx}} = \mathrm{RMSNorm}\bigl(W_c\,[H^{(l_1)};\, \ldots;\, H^{(l_m)}]\bigr),
$$

$$
K_i = [W_i^K H_{\text{ctx}};\; W_i^K H_d], \quad V_i = [W_i^V H_{\text{ctx}};\; W_i^V H_d].
$$

$$
\Theta_0 &= 1 \cdot \mathrm{SPS}(1) = 1.0, \\ \Theta_1 &= (1 + 0.8) \cdot \mathrm{SPS}(2) = 0.9.
$$

$$
\mathrm{SPS}(1) = 1.0,\qquad \mathrm{SPS}(2) = 0.5,\qquad \mathrm{SPS}(3) = 0.45.
$$

$$
a_2 = a_1 c_2
$$

$$
a_2 = 0.8 \times 0.9 = 0.72.
$$

$$
\Theta_2 = (1 + 0.8 + 0.72) \times 0.45 = 1.134.
$$

$$
\Theta_2 = (1 + 0.8 + 0) \times 0.45 = 0.81.
$$

$$
p_{\mathrm{t}}(A)=0.7,\qquad p_{\mathrm{t}}(B)=0.3,
$$

$$
p_{\mathrm{d}}(A)=0.5,\qquad p_{\mathrm{d}}(B)=0.5.
$$

## 相关论文

- [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] — LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and Verification
- [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] — JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting
- [[dflash-block-diffusion-for-flash-speculative-decoding]] — DFlash: Block Diffusion for Flash Speculative Decoding
- [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] — MEDUSA: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads
- [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] — SpecExtend: A Drop-in Enhancement for Speculative Decoding of Long Sequences
- [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] — EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty

## 技术点深读（DEEP）

![[deep/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation.txt`（102452 字符）供引用检索。