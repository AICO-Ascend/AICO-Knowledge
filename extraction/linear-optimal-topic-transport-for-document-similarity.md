---
paper_num: "37"
title: "Linear Optimal Topic Transport for Document Similarity"
authors: "Anonymous ACL submission"
date: "2026/1/17"
arxiv: "https://openreview.net/forum?id=f8SlF0Vzbq"
pdf: "papers/linear-optimal-topic-transport-for-document-similarity.pdf"
slug: "linear-optimal-topic-transport-for-document-similarity"
tags: []
---

# Linear Optimal Topic Transport for Document Similarity

> [!abstract] 摘要（原文）
> 1. 🚀 LOTT（Linear Optimal Topic Transport）是一种新颖的文档分类方法，它利用线性化最优传输嵌入（LOT embedding）技术，在保持与传统Optimal Transport方法（如HOTT）相当的分类准确性的同时，显著提高了计算效率和可扩展性。 2. 💡 该方法通过主题建模将文档表示为潜在主题分布，并使用LOT将这些分布映射到欧几里得空间，从而将文档相似度计算从复杂的Wasserstein距离近似为更高效的L2距离。 3. ⚙️ LOTT引入了参数化的参考分布（如高斯混合），允许用户根据任务需求权衡计算速度和分类精度，使其成为处理大规模文本数据和低数据场景的灵活工具。

## 元信息
- **发表日期**: 2026/1/17
- **作者**: Anonymous ACL submission
- **arXiv**: https://openreview.net/forum?id=f8SlF0Vzbq
- **本地 PDF**: `papers/linear-optimal-topic-transport-for-document-similarity.pdf`
- **页数**: 15

## 图表（原文 caption + 页码）

### Figure 1 (p.7)
![[assets/linear-optimal-topic-transport-for-document-similarity-p07.png]]
> [!quote] caption
> k-NN classification performance across datasets affects mean test error in the CLASSIC dataset. 531

### Figure 2 (p.8)
![[assets/linear-optimal-topic-transport-for-document-similarity-p08.png]]
> [!quote] caption
> t-SNE on CLASSIC

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.2 `matrix C = (cij) ∈Rn×m, where cij represents`
- p.2 `γ = (γij) that redistributes mass from X to Y,`
- p.2 `Γp,q = {γ ∈(R+)n×m : γ1m = µ, γT 1n = ν}.`
- p.3 `Fσ(µ) = T µ`
- p.3 `LOTT(dk1, dk2) = ∥Fσ( ¯dk1) −Fσ( ¯dk2)∥σ`
- p.4 `LOT( ¯dk) = [z1, z2, . . . , z|T|] ∈R|T|d.`

## 技术点深读（DEEP）

![[deep/linear-optimal-topic-transport-for-document-similarity]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/linear-optimal-topic-transport-for-document-similarity.txt`（58255 字符）供引用检索。