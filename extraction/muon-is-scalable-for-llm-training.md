---
paper_num: "64"
title: "Muon is Scalable for LLM Training"
authors: ""
date: "2025/2/24"
arxiv: "https://arxiv.org/abs/2502.16982"
pdf: "papers/muon-is-scalable-for-llm-training.pdf"
slug: "muon-is-scalable-for-llm-training"
tags: [training]
---

# Muon is Scalable for LLM Training

> [!abstract] 摘要（原文）
> Recently, the Muon optimizer based on matrix orthogonalization has demonstrated strong results in training small-scale language models, but the scalability to larger models has not been proven. We identify two crucial techniques for scaling up Muon: (1) adding weight decay and (2) carefully adjusting the per-parameter update scale. These techniques allow Muon to work out-of-the-box on large-scale training without the need of hyper-parameter tuning. Scaling law experiments indicate that Muon achieves $\sim\!2\times$ computational efficiency compared to AdamW with compute optimal training. Based on these improvements, we introduce Moonlight, a 3B/16B-parameter Mixture-of-Expert (MoE) model trained with 5.7T tokens using Muon. Our model improves the current Pareto frontier, achieving better performance with much fewer training FLOPs compared to prior models. We open-source our distributed Muon implementation that is memory optimal and communication efficient. We also release the pretrained, instruction-tuned, and intermediate checkpoints to support future research.

## 元信息
- **发表日期**: 2025/2/24
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2502.16982
- **本地 PDF**: `papers/muon-is-scalable-for-llm-training.pdf`
- **页数**: 19

## 图表（原文 caption + 页码）

### Figure 1 (p.1)
![[assets/muon-is-scalable-for-llm-training-p01.png]]
> [!quote] caption
> Scaling up with Muon. (a) Scaling law experiments comparing Muon and Adam. Muon is ∼2× more computational efficient than Adam with compute optimal training. (b) The MMLU performance of our Moonlight model optimized with Muon and other comparable models. Moonlight advances the Pareto frontier of performance vs training FLOPs. ∗Corresponding author: zhouxinyu@moonshot.cn[cs.LG] 24 Feb 2025

### Figure 2 (p.4)
![[assets/muon-is-scalable-for-llm-training-p04.png]]
> [!quote] caption
> Validation loss curves for AdamW (green), Muon without weight decay (red), and Muon with weight decay (blue).

### Figure 3 (p.7)
![[assets/muon-is-scalable-for-llm-training-p07.png]]
> [!quote] caption
> Fitted scaling law curves for Muon and AdamW optimizers.

### Figure 4 (p.10)
![[assets/muon-is-scalable-for-llm-training-p10.png]]
> [!quote] caption
> SVD entropy of weight matrices across different training iterations. We categorize the weight matrices into 6 different groups: 1) AttnQO denotes the weight matrices related to the query and output projection in the attention layer; 2) AttnKV denotes the weight matrices related to the key and value projection in the attention layer; 3) Experts denotes the weight matrices in expert models; 4) Share

### Figure 5 (p.15)
![[assets/muon-is-scalable-for-llm-training-p15.png]]
> [!quote] caption
> Optimization Landscapes for Scaling Law Hyper-parameters Across FLOPs Budgets

### Figure 6 (p.15)
![[assets/muon-is-scalable-for-llm-training-p15.png]]
> [!quote] caption
> D

### Figure 7 (p.17)
![[assets/muon-is-scalable-for-llm-training-p17.png]]
> [!quote] caption
> Training dynamics comparison between Moonlight and Moonlight-A

### Figure 8 (p.9)
![[assets/muon-is-scalable-for-llm-training-p09.png]]
> [!quote] caption
> 6.

### Figure 9 (p.18)
![[assets/muon-is-scalable-for-llm-training-p18.png]]
> [!quote] caption
> Distribution of singular values for each weight matrix in the attention layers. We use WC to denote the weight matrices at each layer that compress the hidden states to the shared latent spaces for keys and values, WV to denote the weight matrices up-projecting the values from the latent space, WO to denote the output projection matrices, and WKR, WKC, WQR and WQC to denote the projection matrices

### Figure 10 (p.19)
![[assets/muon-is-scalable-for-llm-training-p19.png]]
> [!quote] caption
> Distribution of singular values for each weight matrix in the feed-forward network (FFN) layers. We use WI, WV and WO to denote the weight matrices involved in the FFN layer with SwiGLU activation function, where WI represents the input projection to the Swish1 function, WV represents the extra input projection interacting with Swish1 activations, and WO represents the output projection. We use E0

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
H(\sigma) = -\frac{1}{\log n}\sum_{i=1}^n \frac{\sigma^2_i}{\sum_{j=1}^n \sigma^2_j} \log \frac{\sigma^2_i}{\sum_{j=1}^n \sigma^2_j} \notag
$$

$$
\mathbf{M}_t &= \mu \mathbf{M}_{t-1} + \nabla\mathcal{L}_t(\mathbf{W}_{t-1}) \notag \\ \mathbf{O}_t &= \text{Newton-Schulz}(\mathbf{M}_t)\text{\footnotemark[1]} \\ \mathbf{W}_t &= \mathbf{W}_{t-1} - \eta_t \mathbf{O}_t \notag
$$

$$
\mathbf{X}_k &= a \mathbf{X}_{k-1} + b (\mathbf{X}_{k-1} \mathbf{X}_{k-1}^\mathrm{T}) \mathbf{X}_{k-1} + c (\mathbf{X}_{k-1} \mathbf{X}_{k-1}^\mathrm{T})^2 \mathbf{X}_{k-1}
$$

$$
\mathbf{W}_t = \mathbf{W}_{t-1} - \eta_t (\mathbf{O}_t + \lambda \mathbf{W}_{t-1})
$$

$$
\mathbf{W}_t = \mathbf{W}_{t-1} - \eta_t (0.2\cdot\mathbf{O}_t\cdot\sqrt{\max(A,B)} + \lambda \mathbf{W}_{t-1})
$$

$$
\mathbf{W}_t = \mathbf{W}_{t-1} - \eta_t (0.2\cdot\mathbf{O}_t\cdot\sqrt{H} + \lambda \mathbf{W}_{t-1})
$$

$$
\mathbf{W}_t = \mathbf{W}_{t-1} - \eta_t (0.2\cdot\mathbf{O}_t/\mathop{\text{RMS}}(\mathbf{O}_t) + \lambda \mathbf{W}_{t-1})
$$

## 相关论文

- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core
- [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] — From ATOP to ZCube: Automated Topology Optimization Pipeline and A Highly Cost-Effective Network Topology for Large Model Training
- [[zero-memory-optimizations-toward-training-trillion-parameter-models]] — ZeRO: Memory Optimizations Toward Training Trillion Parameter Models
- [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] — GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints
- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey

## 技术点深读（DEEP）

![[deep/muon-is-scalable-for-llm-training]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/muon-is-scalable-for-llm-training.txt`（55936 字符）供引用检索。