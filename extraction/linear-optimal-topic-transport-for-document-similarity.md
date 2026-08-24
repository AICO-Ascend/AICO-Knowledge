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
> 【图文联合解读】Table 1列出6个文本分类基准数据集（BBCSport、Twitter、OHSUMED、CLASSIC、Reuters、Amazon）的核心统计量：文档数|D|（737–9152）、词表规模V（1205–16753）、平均词数AVG(w)（9.7–116.5）及类别数（3–10），覆盖从短文（Twitter仅9.7词/1205词表）到长文档（BBCSport达116.5词/3657词表）、从少类（3类）到多类（OHSUMED 10类）的多样化场景。该表通过呈现数据规模与领域异质性，为后续实验论证LOTR方法在不同词表丰富度、文档长度及类别结构下的鲁棒性与泛化能力提供统一评估基准，是连接主题传输理论推导与实证性能验证的关键实验依据。

### Table 2 (p.6) ⭐深度解读
![[assets/crops/linear-optimal-topic-transport-for-document-similarity-tab02.png]]
> [!quote] caption
> Standardized throughput of LOTT and other methods, normalized relative to the throughput of HOTT.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读**

表2以HOTT吞吐量为基准（归一化为1.000），在6个文档数据集（BBCSPORT、TWITTER、OHSUMED、CLASSIC、REUTERS、AMAZON）上对比WMD20、HOFTT及LOTT四个变体（LOTT-1/5/10/15）的标准化吞吐量。

**核心数据**：WMD20（0.074–0.397）与HOFTT（0.177–0.388）吞吐量均低于HOTT；而LOTT在所有数据集上大幅领先——BBCSPORT约11–12倍，AMAZON高达165–182倍，OHSUMED约124–136倍，TWITTER/CLASSIC/REUTERS介于85–102倍。

**关键结论**：LOTT将HOTT的二次复杂度降为线性，实现数十至上百倍的吞吐加速；迭代次数越少（LOTT-1）通常越快；数据规模越大加速比越显著，有力验证了线性OT的实用优势。

**论文作用**：与质量评估表互补，从效率维度支撑论文"线性OT可行且可扩展"的核心论点。

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