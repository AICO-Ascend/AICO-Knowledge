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

### Figure 1 (p.4) ⭐深度解读
![[assets/crops/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation-fig01.png]]
*整页渲染: ![[assets/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation-p04.png]]*
> [!quote] caption
> Recall from Equation 1 that the per-token latency of speculative decoding is 𝐿= (𝑇draft + 𝑇verify)/𝜏. Autoregressive drafters achieve high 𝜏but pay 𝑇draft ∝𝛾; parallel drafters collapse 𝑇draft to a single pass but sacrifice 𝜏because each position is predicted independently. Meanwhile, fixed-length verification wastes 𝑇verify on low-confidence suffix tokens that are almost certain to be rejected. D

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图示 DSpark 三轮解码循环**：
① 目标模型由 prompt A/B/C 自回归生成锚点 D；
② D 进入起草模块——并行主干对 E–H 一次输出 logits，序贯头顺次解码得到置信度 c₁–c₄，硬件感知调度器按置信保留 E/F/G、丢弃低置信的 H；
③ 目标模型并行验证 D–G，接受 E/F（✓），否决 G（✗）并改写为 G* 作为下一轮锚点。

**原文论证**：自回归起草 T_draft∝γ、纯并行起草则牺牲 τ；DSpark 以"并行主干＋序贯头"折中，并以**置信调度**取代定长验证，避免在 c₄ 这类低置信 token 上浪费 T_verify，整体压缩 L = (T_draft + T_verify)/τ。

**论文作用**：作为方法总览图，具象化 Equation 1 的三项延迟权衡，并为 Table 1 中"DSpark 平均接受长度反超 Eagle3"的反直觉结论提供机制支撑。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.11) ⭐深度解读
![[assets/crops/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation-tab01.png]]
> [!quote] caption
> | Main speculative decoding results. We report accepted length ( 𝜏 ) per decoding round (higher is better) for different target models and domains. Bold marks the best results.

> [!tip] 表格解读（多模态）
> 【图文联合解读】核心对象与结构：表格列出 4 个目标模型（Qwen3-4B/8B/14B、Gemma4-12B）× 3 个 drafter（Eagle3 自回归、DFlash 并行、DSpark）× 9 个 benchmark（Math：GSM8K/MATH/AIME25；Code：MBPP/HumanEval/LCB；Chat：MT-Bench/Alpaca/Arena-Hard）的 τ 值。DSpark 在全部 36 格几乎全部加粗为最佳，例如 Qwen3-4B GSM8K：Eagle3 5.14、DFlash 5.40、DSpark 6.11。

关键结论：DSpark 的 τ 一致反超两类基线，证明其同时具备自回归式高接受长度与并行式低 draft 延迟，验证 Figure 1 所述"打破 τ 与 T_draft 权衡"的机制。

链路作用：作为主实验表，为 Figure 1 的延迟分解公式 L=(T_draft+T_verify)/τ 提供端到端实证支撑，奠定方法优越性的核心证据。

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