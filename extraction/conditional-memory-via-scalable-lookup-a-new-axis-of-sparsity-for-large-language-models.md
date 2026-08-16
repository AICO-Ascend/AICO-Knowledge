---
paper_num: "35"
title: "Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models"
authors: "A New Axis of Sparsity for Large Language Models Xin Cheng1,2∗, Rui Tian2∗, Wangding Zeng2, Damai Dai2, Qinyu Chen2, Bingxuan Wang2, Zhenda Xie2, Kezhao Huang2, Xingkai Yu2 Chengqi Deng2, Shangyan Zhou2, Chenggang Zhao2,"
date: "2026/1/17"
arxiv: "https://arxiv.org/abs/2601.07372"
pdf: "papers/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models.pdf"
slug: "conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models"
tags: []
---

# Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models

> [!abstract] 摘要（原文）
> 1\. 💡 论文引入条件记忆作为 LLMs 稀疏性的补充轴，通过 Engram 模块实现，该模块利用现代化的 N-gram 嵌入提供 O(1) 知识查找，以解决 Transformer 在静态知识检索上的低效问题。 2. 🔬 通过对稀疏性分配问题的研究，作者发现 MoE（神经计算）和 Engram（静态记忆）之间存在 U 形缩放定律，混合分配能严格超越纯 MoE，在 iso-parameter 和 iso-FLOPs 的对比下，Engram-27B 在推理、代码和数学任务上表现更优。 3. 🚀 机制分析显示 Engram 有效减轻了早期层级的静态重建负担，从而加深了网络的有效深度并释放了注意力容量以处理全局上下文，实现了卓越的长上下文处理能力，同时其确定性寻址还支持基础设施感知的运行时预取，实现了显著的系统效率。

## 元信息
- **发表日期**: 2026/1/17
- **作者**: A New Axis of Sparsity for Large Language Models Xin Cheng1,2∗, Rui Tian2∗, Wangding Zeng2, Damai Dai2, Qinyu Chen2, Bingxuan Wang2, Zhenda Xie2, Kezhao Huang2, Xingkai Yu2 Chengqi Deng2, Shangyan Zhou2, Chenggang Zhao2,
- **arXiv**: https://arxiv.org/abs/2601.07372
- **本地 PDF**: `papers/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models.pdf`
- **页数**: 35

## 图表（原文 caption + 页码）

### Figure 2 (p.6)
![[assets/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-p06.png]]
> [!quote] caption
> During training, to accommodate large-scale embedding tables, we employ standard model parallelism by sharding the tables across available GPUs. An All-to-All communication primitive is used to gather active rows in the forward pass and dispatch gradients in the backward pass, enabling the total memory capacity to scale linearly with the number of accelerators.

### Figure 5 (p.16)
![[assets/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-p16.png]]
> [!quote] caption
> We find that three components yield the most significant gains: (i) branch- specific fusion within the multi-branch backbone, (ii) context-aware gating, and (iii) tokenizer compression. Removing any of these causes the largest regressions in validation loss. Specifically, for the “w/o multi branch” ablation, we retain the mHC backbone structure but replace the branch-specific gating with a single 

### Figure 7 (p.18)
![[assets/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-p18.png]]
> [!quote] caption
> The results demonstrate a distinct pattern of selectivity. The gating mechanism consistently activates (shown in red) upon completing local, static patterns. In English, we observe strong activations on multi-token named entities (e.g., “Alexander the Great”, “the Milky Way”) and formulaic phrases (e.g., “By the way”, “Princess of Wales”). This behavior generalizes effectively across languages. In

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.3 `Formally, given an input sequence 𝑋= (𝑥1, . . . , 𝑥𝑇) and hidden states H(ℓ) ∈R𝑇×𝑑at layer ℓ,`
- p.4 `The gated output is defined as ˜v𝑡= 𝛼𝑡· v𝑡. This design enforces semantic alignment: if the`
- p.7 `• 𝐶= 2 × 1020 FLOPs: 𝑃tot ≈5.7B and 𝑃act = 568M. The baseline (𝜌= 1) has a total of 106 experts.`
- p.7 `• 𝐶= 6 × 1020 FLOPs: 𝑃tot ≈9.9B and 𝑃act = 993M. The baseline (𝜌= 1) has a total of 99 experts.`
- p.8 `regime (𝐶= 6 × 1020), validation loss improves from 1.7248 (at 𝜌= 100%) to 1.7109 near the`
- p.16 `Val Loss = 1.768, a substantial improvement over the MoE baseline (Δ = 0.04). All structural`

## 全文文本
全文已存 `extraction/fulltext/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models.txt`（100228 字符）供引用检索。