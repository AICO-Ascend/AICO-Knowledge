---
paper_num: "55"
title: "Gated Delta Networks: Improving Mamba2 with Delta Rule"
authors: ""
date: "2024/12/9"
arxiv: "https://arxiv.org/abs/2412.06464"
pdf: "papers/gated-delta-networks-improving-mamba2-with-delta-rule.pdf"
slug: "gated-delta-networks-improving-mamba2-with-delta-rule"
tags: [architecture]
---

# Gated Delta Networks: Improving Mamba2 with Delta Rule

> [!abstract] 摘要（原文）
> 1. Linear Transformers have gained attention as efﬁcient alternatives to standard Transformers, but their performance in retrieval and long-context tasks has been limited. To address these limitations, recent work has explored two distinct mech- anisms: gating for adaptive memory control and the delta update rule for pre- cise memory modiﬁcations. We observe that these mechanisms

## 元信息
- **发表日期**: 2024/12/9
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2412.06464
- **本地 PDF**: `papers/gated-delta-networks-improving-mamba2-with-delta-rule.pdf`
- **页数**: 22

## 图表（原文 caption + 页码）

### Figure 1 (p.7) ⭐MiniMax深度解读
![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p07.png]]
> [!quote] caption
> Visualization of the (hybrid) architecture and block design of Gated DeltaNet models.

> [!tip] 技术解读（MiniMax 多模态）
> 【MiniMax 解读】Gated DeltaNet 架构(Fig.1)：delta-rule 线性注意力 + 乘性门控(α,β)增联想召回；H1/H2 混合变体把 Gated DeltaNet 与 Mamba2(SSM) + Sliding-Window Attention 交错，融合选择性长程记忆+结构化递归+局部上下文。block 设计：q/k 路径=线性投影+shortconv+SiLU+L2norm，v=线性投影+shortconv+SiLU，α/β=线性投影，输出 gate=线性投影+SiLU。Wiki ppl 16.42、zero-shot 55.32，H2 混合 ppl 15.91 最优。线性注意力/SSM 架构核心图。

### Figure 2 (p.8)
![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p08.png]]
> [!quote] caption
> Length extrapolation on six long benchmarks.

### Figure 3 (p.9)
![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p09.png]]
> [!quote] caption
> Training throughput comparison of 1.3B models on a single H100 GPU. standalone mixers: Samba outperforms Mamba, while Gated DeltaNet-H1 and -H2 outperform

## 全文文本
全文已存 `extraction/fulltext/gated-delta-networks-improving-mamba2-with-delta-rule.txt`（79000 字符）供引用检索。