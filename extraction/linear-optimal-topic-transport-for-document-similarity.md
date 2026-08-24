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

### Figure 1 (p.7) ⭐深度解读
![[assets/crops/linear-optimal-topic-transport-for-document-similarity-fig01.png]]
*整页渲染: ![[assets/linear-optimal-topic-transport-for-document-similarity-p07.png]]*
> [!quote] caption
> k-NN classification performance across datasets affects mean test error in the CLASSIC dataset. 531

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图1 解读**

**1) 核心对象与数据**：该柱状图比较了10种文档表示/距离方法（nBOW、SIF、Cosine、RWMD、HOfTT、HOTT、WMD-T20、LOTT、LOTT-5、LOTT-10）在6个数据集上的k-NN分类平均测试误差（%）。其中LOTT系本文提出的三种变体（含不同rank或embed层选择）。

**2) 关键结论**：在ohsumed上LOTT表现偏弱（52%），但加锚点增强的LOTT-5/10降至48/46，差距收窄；而在其余5个数据集上，LOTT/LOTT-5/10均处于最低误差区间，例如bbcsport LOTT-10=7%（仅略低于WMD-T20的6%），classic LOTT-10=5%为该数据集最优，amazon/reuters LOTT-10=11/9%与WMD-T20持平或更优。整体说明LOTT系列在跨数据集下与WMD-T20、RWMD这一类SOTA基线具有可比或更优的k-NN表现，验证其在标准距离度量路线下的有效性。

**3) 在论文中的作用**：该图为方法实验链路的**主结果展示**，为后续段落所引"影响CLASSIC均值误差"等更细致的分析提供全景对比，支撑本文关于"线性最优主题传输可作为文档相似度替代度量"的核心论断。

### Figure 2 (p.8) ⭐深度解读
![[assets/crops/linear-optimal-topic-transport-for-document-similarity-fig02.png]]
*整页渲染: ![[assets/linear-optimal-topic-transport-for-document-similarity-p08.png]]*
> [!quote] caption
> t-SNE on CLASSIC

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图以 2×2 网格对比 LOTT、SBERT、HOTT、nBoW 四种方法在 CLASSIC 数据集（4 类、CACM/MED/CRAN/CISI）上的 t-SNE 二维投影。直观可见：LOTT 与 HOTT 形成颜色分明、类内紧凑的簇群；SBERT 各类有重叠；nBoW 散点几乎混为一体。原文借此论证 LOTT 嵌入具备良好的语义结构，类内一致性与类间分离度均优，为文档相似度度量提供可解释的表征依据，支撑其在主实验中的优越性。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/linear-optimal-topic-transport-for-document-similarity-tab01.png]]
> [!quote] caption
> Dataset statistics for evaluation

> [!tip] 表格解读（多模态）
> 【图文联合解读】表1列出6个评估数据集的统计：BBCSPORT(737篇，词典3657，均长116.5词，5类)、TWITTER(3108/1205/9.7/3)、OHSUMED(9152/8261/59.4/10)、CLASSIC(7093/5813/38.5/4)、REUTERS(7674/5495/35.7/8)、AMAZON(8000/16753/44.3/4)。原文借此论证LOT方法在词典规模(1205–16753)、文档平均长度(9.7–116.5词)、类别数(3–10)高度异构的语料上均有效，体现主题传输的领域普适性。该表是后续k-NN分类(图1)与迁移距离对比实验的数据基础，支撑方法在跨域文档相似性任务中的鲁棒性结论。

### Table 2 (p.6) ⭐深度解读
![[assets/crops/linear-optimal-topic-transport-for-document-similarity-tab02.png]]
> [!quote] caption
> Standardized throughput of LOTT and other methods, normalized relative to the throughput of HOTT.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 联合解读**

1) **核心数据**：6 个数据集（BBCSPORT、AMAZON、OHSUMED、CLASSIC、REUTERS、TWITTER）上，WMD20、HOFTT、HOTT 与 LOTT-{1,5,10,15} 的标准化吞吐（以 HOTT=1 为基准）。WMD20/HOFTT 均 <0.4，慢于 HOTT；而 LOTT 系列均显著高于 HOTT——BBCSPORT 仅约 11–13 倍，TWITTER/CLASSIC/REUTERS 约 85–102 倍，AMAZON 高达 165–182 倍，呈现"数据集越大、加速越显著"的趋势。

2) **论证结论**：LOTT 在保持与 HOTT 同等聚类质量（呼应 Figure 2 的 t-SNE 视觉对比）的前提下，实现数量级推理加速，并优于 WMD20、HOFTT 等基线，验证了"线性最优主题传输"在效率上的优势。

3) **论文链路作用**：与 Figure 2（质量证据）互补，构成"质量持平 + 吞吐飞跃"的双重论证，支撑 LOTT 作为 HOTT 可扩展替代方案的核心贡献。

## 关键公式（原文截图，无 LaTeX 源 — 引用前请核对图片）

### 公式截图 (p.2)
![[assets/crops/linear-optimal-topic-transport-for-document-similarity-eq01.png]]
> 原文文本线索：`Γp,q = {γ ∈(R+)n×m : γ1m = µ, γT 1n = ν}.`

### 公式截图 (p.3)
![[assets/crops/linear-optimal-topic-transport-for-document-similarity-eq02.png]]
> 原文文本线索：`Fσ(µ) = T µ`

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