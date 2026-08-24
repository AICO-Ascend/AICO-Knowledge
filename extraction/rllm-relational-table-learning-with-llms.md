---
paper_num: "70"
title: "rLLM: Relational Table Learning with LLMs"
authors: "Weichen Li1, Xiaotong Huang1, Jianwu Zheng1, Zheng Wang1, Chaokun Wang2, Li Pan1, Jianhua Li1 1 Shanghai Jiao Tong University, China 2 Tsinghua University, China {wzheng,panli,lijh888}@sjtu.edu.cn,chaokun@tsinghua.edu.cn"
date: "2024/7/29"
arxiv: "https://arxiv.org/abs/2407.20157"
pdf: "papers/rllm-relational-table-learning-with-llms.pdf"
slug: "rllm-relational-table-learning-with-llms"
tags: []
---

# rLLM: Relational Table Learning with LLMs

> [!abstract] 摘要（原文）
> We introduce rLLM (relationLLM), a PyTorch library designed for Relational Table Learning (RTL) with Large Language Models (LLMs). The core idea is to decompose state-of-the-art Graph Neural Networks, LLMs, and Table Neural Networks into standardized modules, to enable the fast construction of novel RTL-type models in a simple "combine, align, and co-train" manner. To illustrate the usage of rLLM, we introduce a simple RTL method named \textbf{BRIDGE}. Additionally, we present three novel relational tabular datasets (TML1M, TLF2K, and TACM12K) by enhancing classic datasets. We hope rLLM can serve as a useful and easy-to-use development framework for RTL-related tasks. Our code is available at: this https URL.

## 元信息
- **发表日期**: 2024/7/29
- **作者**: Weichen Li1, Xiaotong Huang1, Jianwu Zheng1, Zheng Wang1, Chaokun Wang2, Li Pan1, Jianhua Li1 1 Shanghai Jiao Tong University, China 2 Tsinghua University, China {wzheng,panli,lijh888}@sjtu.edu.cn,chaokun@tsinghua.edu.cn
- **arXiv**: https://arxiv.org/abs/2407.20157
- **本地 PDF**: `papers/rllm-relational-table-learning-with-llms.pdf`
- **页数**: 6

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/rllm-relational-table-learning-with-llms-fig01.png]]
*整页渲染: ![[assets/rllm-relational-table-learning-with-llms-p01.png]]*
> [!quote] caption
> Trends in global data volume and in LLM token costs by data type

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

左图为2010–2025年全球数据量堆叠柱状图（单位ZB），总量从约30ZB增至约100ZB，其中Video/Image占比最大，Text仅约20ZB。右图为LLM分词成本堆叠面积图（单位trillion dollar），到2025年升至约5000，但Text逆袭成为最大成本项。图中标注指出："语言数据虽量小但token成本高"、"多模态数据虽量大但成本相对低"。

论文借此引出关键结论：**结构化表格数据**虽规模有限，却长期被LLM高昂的token开销与语义理解需求所忽视，因而亟需专门的关系表学习方法（即rLLM）。该图作为开篇动机证据，与Table 1（数据集汇总）衔接，为后续方法设计与基准实验提供问题驱动的论证支撑。

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/rllm-relational-table-learning-with-llms-fig02.png]]
*整页渲染: ![[assets/rllm-relational-table-learning-with-llms-p02.png]]*
> [!quote] caption
> The architecture of rLLM analyzed using GNNs. This design efficiently captures inter-table dependencies with minimal architectural complexity.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

图示rLLM自下而上的三层架构：①底层**Data Engine**含Data Loader、Graph Builder、Table Marker三个组件；②中层**Modules**整合三类——GNNs（GraphConv、GraphTransform）、LLMs（Prediction、Enhancement）、TNNs（TableConv、TableTransform）；③顶层**Models**提供Combine、Align、Co-Train三种范式。

原文借此论证其"以最小架构复杂度高效捕获表间依赖"的核心设计理念——通过数据→模块→模型的分层解耦，将异构模型（GNN/LLM/TNN）统一在统一接口下。

该图是全文方法总纲，为后续模块化实现与Table 2的RelBench等基准分类精度对比实验提供整体框架支撑。

### Figure 3 (p.2) ⭐深度解读
![[assets/crops/rllm-relational-table-learning-with-llms-fig03.png]]
*整页渲染: ![[assets/rllm-relational-table-learning-with-llms-p02.png]]*
> [!quote] caption
> Base data structure in rLLM. Arrows indicate inher- itance relationships and parentheses indicate containment relationships. data, respectively. Overall, this design meets the familiar storage and processing requirements of relational table data consist of table data and foreign key relationships.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

图示rLLM基础数据结构：底层"ABC (Python)"和"Dataset (Pytorch)"通过继承箭头指向统一的"Dataset"基类；后者派生"Cora、IMDB、Titanic..."等具体数据集，并通过花括号（containment）包含右上方虚线框内的"GraphData"与"TableData"两个抽象父类，二者再分别由"BaseGraph"和"BaseTable"继承实现。

原文以此论证：rLLM数据层以单一Dataset类统一封装图数据与表数据（含外键关系），同时满足关系表数据的存储与处理需求。该图是论文方法链路的底层基石——为后续表学习、图神经网络与外键建模提供了可继承、可扩展的标准化数据接口。

### Figure 4 (p.3) ⭐深度解读
![[assets/crops/rllm-relational-table-learning-with-llms-fig04.png]]
*整页渲染: ![[assets/rllm-relational-table-learning-with-llms-p03.png]]*
> [!quote] caption
> The architecture of BRIDGE columns, which can vary greatly in nature. Due to the diverse types of features and the often limited information provided by tables with fewer columns, it is crucial to map or transform some columns into higher-dimensional feature spaces to enhance the sample in- formation. The TableConv module facilitates multi-layer interactive learning among feature columns to extrac

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示BRIDGE双路架构：左侧关系表（Table I/II含PK，Table III含PK+FK）经Table Encoder升维为表格嵌入；非表格特征（图结构等）旁路直连Graph Encoder（GNN），二者融合后输出。

**技术结论**：TableConv将异构列特征映射至高维空间，以弥补列数少、样本信息不足的缺陷；非表格特征旁路设计则避免图结构信息在表格编码中损失。

**论文作用**：作为BRIDGE总框图，串联"关系表→表格嵌入→图嵌入→预测"全链路，为后续TableConv与GNN融合的实验提供架构基础。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/rllm-relational-table-learning-with-llms-tab01.png]]
> [!quote] caption
> Summary of the datasets.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 联合解读**

Table 1 汇总三个关系表基准：**TML1M**（users 6,040/5、movies 3,883/11、ratings 1,000,209/4；关系表 user–movie；标签为用户年龄段，7 类，划分 140/500/1000）、**TLF2K**（artists 9,047/10、user_artists 80,009/3、user_friends 12,717/3；user–artist 与 user–user；标签为艺术家流派，11 类）、**TACM12K**（papers 12,499/5、authors 17,431/3、citations 30,789/2、writings 37,055/2；paper–paper、paper–author；标签为论文会议，14 类）。

原文借此论证两点：① 数据集覆盖电影、社交、学术三类异构 schema，关系表数量与类别数（7→11→14）逐级递增，体现基准的多样性与难度梯度；② 统一 Train/Val/Test 划分与节点级分类标签，为后续章节在 rLLM 框架下公平比较不同关系表学习方法提供了可复现实验链路。

### Table 2 (p.5) ⭐深度解读
![[assets/crops/rllm-relational-table-learning-with-llms-tab02.png]]
> [!quote] caption
> Classification accuracy.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 联合解读**

该表列出 rLLM 框架的 3 个关系表分类基准：

- **TML1M**：users/movies/ratings（6,040–1,000,209 行），预测用户年龄段，7 类，#Train=140
- **TLF2K**：artists/user_artists/user_friends（9,047–80,009 行），预测艺术家流派，11 类，#Train=220
- **TACM12K**：papers/authors/citations/writings（12,499–37,055 行），预测论文会议，14 类，#Train=280

**技术结论**：数据集覆盖二部图（user-movie）、异构多关系（user-artist + user-user、paper-author + paper-paper）等多种图结构，且训练样本极少（140–280），专门检验模型在少样本、多表关联场景下的泛化能力。

**作用**：作为论文下游分类实验的统一评测基座，为 GNN、LLM 等基线方法提供可比标准，支撑 rLLM 在关系表学习任务上的有效性论证。

## 技术点深读（DEEP）

![[deep/rllm-relational-table-learning-with-llms]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/rllm-relational-table-learning-with-llms.txt`（31984 字符）供引用检索。