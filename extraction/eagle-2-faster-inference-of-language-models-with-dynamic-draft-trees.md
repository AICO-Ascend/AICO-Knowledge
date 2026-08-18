---
paper_num: "5"
title: "EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees"
authors: "Yuhui Li♠ Fangyun Wei‡ Chao Zhang♠ Hongyang Zhang♣† ♠Peking University ‡Microsoft Research ♣University of Waterloo †Vector Institute hongyang.zhang@uwaterloo.ca"
date: "2024/6/24"
arxiv: "https://arxiv.org/abs/2406.16858"
pdf: "papers/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees.pdf"
slug: "eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees"
tags: [speculative]
---

# EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees

> [!abstract] 摘要（原文）
> 1\. 🚀 EAGLE-2 提出了一种基于上下文的动态草稿树结构，通过利用 draft model 的置信度得分来准确近似标记的接受率，从而突破了静态草稿树的局限性。 2. 💡 该方法在不改变原始 LLM 输出分布的前提下实现了无损加速，无需额外训练即可动态调整草稿树结构，显著提升了推理过程中的 token 接受数量。 3. 📈 在多项生成任务的广泛评估中，EAGLE-2 相比 EAGLE-1 实现了 20%-40% 的进一步提速，在多种主流模型上表现出 3.05x-4.26x 的显著推理加速效果。

## 元信息
- **发表日期**: 2024/6/24
- **作者**: Yuhui Li♠ Fangyun Wei‡ Chao Zhang♠ Hongyang Zhang♣† ♠Peking University ‡Microsoft Research ♣University of Waterloo †Vector Institute hongyang.zhang@uwaterloo.ca
- **arXiv**: https://arxiv.org/abs/2406.16858
- **本地 PDF**: `papers/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees.pdf`
- **页数**: 12

## 图表（原文 caption + 页码）

### Figure 1 (p.1)
![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p01.png]]
> [!quote] caption
> Speedup ratios of different methods at tempera- ture=1. For speculative sampling, the Vicuna series uses

### Figure 2 (p.2)
![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p02.png]]
> [!quote] caption
> Speedup ratios of different methods at temperature=0. For speculative sampling, the Vicuna series uses Vicuna- 68M as the draft model. LLaMA2-Chat 7B, 13B, and LLaMA3-Instruct 8B lack suitable draft models and are marked as N/A. LLaMA2-Chat 70B and LLaMA3-Instruct 70B use LLaMA2-Chat 7B and LLaMA3-Instruct 8B as draft models, respectively. In Table 1, we present comparisons with additional methods

### Figure 3 (p.3)
![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]]
> [!quote] caption
> Comparison of standard speculative sampling and EAGLE. For simplicity, EAGLE’s tree-structured draft is shown only in the verification stage, while the illustration of the drafting stage uses a chain-structured draft. Here, ti denotes the i-th token embedding, and fi denotes the i-th feature vector in the second-to-top-layer of LLM before LM head. the token sequence ta, ta+1, · · · , tb. Speculati

### Figure 4 (p.3)
![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]]
> [!quote] caption
> Differences between EAGLE and EAGLE-2. EA- GLE always uses a fixed draft shape. When the query is “10+2=”, the next token is very likely to be correctly pre- dicted as “1”. However, with a static draft tree, EAGLE would still add two candidates, even though the probability of the other candidate “3” being correct is very low. EAGLE- 2, on the other hand, adjusts the shape of draft tree based on th

### Figure 5 (p.3)
![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]]
> [!quote] caption
> Overall, the acceptance rate of draft tokens is position-dependent, with the highest acceptance rate at position P1 and the lowest at position P6. Draft tokens in the upper left side of the draft tree (such as position P1) have higher acceptance rates, while those in the lower 3

### Figure 6 (p.4)
![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p04.png]]
> [!quote] caption
> Average acceptance rates for different confidence score intervals of the draft model. The red dashed line connects (0,0) and (1,1) to aid in visual assessment. The original LLM is Vicuna 7B. aspects: how to expand the draft tree (Section 4.1) and how to rerank draft tokens (Section 4.2). During the expansion phase, we input the most promising nodes from the latest layer of the draft tree into the 

### Figure 7 (p.5)
![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p05.png]]
> [!quote] caption
> Illustration of EAGLE-2. The numbers beside the edges represent the confidence scores of the draft model, and the numbers in brackets within the blocks represent the value of the nodes. During the expansion phase, we select the top 2 nodes with the highest value from the current layer (orange blocks) as inputs to the draft model and connect the generated tokens (green blocks) to the draft tree. In

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
V_i=\prod_{t_j \in \text{Path}\left(\text{root}, t_i\right)} p_j \approx \prod_{t_j \in \text{Path}\left(\text{root}, t_i\right)} c_j,
$$

## 相关论文

- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]] — BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DIFFUSION LANGUAGE MODELS
- [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] — MEDUSA: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads
- [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] — JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting
- [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] — EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty
- [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] — DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation

## 技术点深读（DEEP）

![[deep/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees.txt`（46933 字符）供引用检索。