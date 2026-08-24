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

Figure 1 由左右两幅子图组成，定量呈现 2010–2025 年趋势：

- **左图（堆叠柱状图，单位 ZB）**：全球数据总量从 2010 年约 30 ZB 增至 2025 年约 100 ZB，其中 Video（橙色，约 40+ ZB）与 Image（黄色）占比最大，Structured data（浅蓝，约 10 ZB）体量最小。
- **右图（堆叠面积图，单位万亿 $）**：LLM token 成本由近 0 增至约 5000 万亿 $；其中 **Text**（中蓝色）与 **Structured data**（底部浅蓝）占绝对主体，而 Video/Image 仅占薄薄一层。

论文借此论证的关键结论：**多模态数据体量大但 token 化成本低，语言/结构化数据体量小却消耗绝大部分 token 成本**——即 LLM 处理结构化数据的"性价比"问题被严重低估。

在论文整体链路中，该图作为引言动机，引出 rLLM 项目核心议题：如何用 LLM 高效建模 Relational Table（结构化数据），为后续 Table 1（基准数据集综述）与方法部分提供必要性铺垫。

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/rllm-relational-table-learning-with-llms-fig02.png]]
*整页渲染: ![[assets/rllm-relational-table-learning-with-llms-p02.png]]*
> [!quote] caption
> The architecture of rLLM analyzed using GNNs. This design efficiently captures inter-table dependencies with minimal architectural complexity.

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图展示rLLM三层架构：底层Data Engine含Data Loader、Graph Builder、Table Marker三个组件；中层Modules分为GNN（图卷积/图变换）、LLM（预测/增强）、TNN（表卷积/表变换）三类共6个模块；上层Models含Combine、Align、Co-Train三种范式。原文借此论证：仅以简洁的三层结构即可高效捕获跨表依赖。作用上，该图是论文方法骨架，串联异构模型与统一数据处理流程，为Table 2的对比实验提供标准化实现框架。

### Figure 3 (p.2) ⭐深度解读
![[assets/crops/rllm-relational-table-learning-with-llms-fig03.png]]
*整页渲染: ![[assets/rllm-relational-table-learning-with-llms-p02.png]]*
> [!quote] caption
> Base data structure in rLLM. Arrows indicate inher- itance relationships and parentheses indicate containment relationships. data, respectively. Overall, this design meets the familiar storage and processing requirements of relational table data consist of table data and foreign key relationships.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示 rLLM 的基础数据结构继承/包含关系。核心对象包括：`Dataset`（同时继承 Python 的 `ABC` 与 PyTorch 的 `Dataset` 基类），其内含（括号关系）两个子类层级——`GraphData ← BaseGraph` 与 `TableData ← BaseTable`，分别承载图数据与表数据；箭头向上指向 `Cora、IMDB、Titanic…` 等具体数据集实例。

原文借此论证：rLLM 通过这一统一容器同时兼容表数据与外键关系，使两种异构数据可在同一 `Dataset` 下被一致地存储与批处理，从而满足关系表学习的"存储+处理"双重需求。

在整体方法链中，它是 rLLM 框架的数据入口层，为上游模型（如图神经网络/LLM）在关系表任务（如节点分类、回归）上的训练提供标准化、可扩展的数据抽象，使不同领域数据集（Cora、IMDB、Titanic 等）均能即插即用，构成实验可复现性的基础。

### Figure 4 (p.3) ⭐深度解读
![[assets/crops/rllm-relational-table-learning-with-llms-fig04.png]]
*整页渲染: ![[assets/rllm-relational-table-learning-with-llms-p03.png]]*
> [!quote] caption
> The architecture of BRIDGE columns, which can vary greatly in nature. Due to the diverse types of features and the often limited information provided by tables with fewer columns, it is crucial to map or transform some columns into higher-dimensional feature spaces to enhance the sample in- formation. The TableConv module facilitates multi-layer interactive learning among feature columns to extrac

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（≤220字）**

图示BRIDGE架构：左侧Table I/II（含PK）与Table III（含PK+FK，多FK连接）构成关系表数据；中间Tabular features经Table Encoder升维映射为Tabular embeddings，再与顶部Non-tabular features（图结构等）在Graph Encoder中融合，最终输出预测。

原文论证：表格列特征类型多样、信息有限，需映射至高维空间以增强样本表征；TableConv通过多层列间交互学习完成特征提取。

作用：作为方法总览图，揭示BRIDGE"表编码+图编码"双路融合范式——统一处理关系型表格数据与外部非表格特征，是后续TableConv/GraphConv模块设计、消融与基准实验验证的整体框架基础。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/rllm-relational-table-learning-with-llms-tab01.png]]
> [!quote] caption
> Summary of the datasets.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 1 汇总三个关系表基准：TML1M（6040 用户 /3883 电影 /100 万评分，建用户-电影图，预测用户年龄段 7 类）、TLF2K（9047 艺术家 + 8 万用户-艺术家关系，预测流派 11 类）、TACM12K（12499 论文 /17431 作者 /3 万引用，预测会议 14 类），统一 Train/Val/Test = [140–280/500/1000] 小样本切分。论文借此论证 rLLM 可跨异构关系表（用户-物品、用户-用户、论文-作者）统一建模节点分类任务，覆盖不同类别粒度，承接 Fig 1 的"结构化数据膨胀"动机，为后续方法提供跨领域标准化评测基座。

### Table 2 (p.5) ⭐深度解读
![[assets/crops/rllm-relational-table-learning-with-llms-tab02.png]]
> [!quote] caption
> Classification accuracy.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读**

该表实为**关系型数据集统计**，列出三组基准：TML1M（用户-电影-评分，3表，用户年龄7分类，训练仅140）、TLF2K（艺术家-用户关系-好友，3表，艺术流派11分类，训练220）、TACM12K（论文-作者-引用-著作，4表，论文会议14分类，训练280）。各数据集均含2–4张表（行数从3,883至1,000,209不等），通过外键关系（如user-movie、paper-author）构成典型RDB结构。

该表作用：①量化定义实验场景——小训练集（140–280）、固定验证/测试集（500/1000），体现**少样本关系学习**设定；②覆盖异构领域（推荐/音乐/学术），类别数7–14保证任务难度梯度；③为rLLM方法提供**统一评测土壤**，支撑后续跨数据集的分类性能对比，验证其在不同表规模与关系复杂度下的泛化能力。

## 技术点深读（DEEP）

![[deep/rllm-relational-table-learning-with-llms]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/rllm-relational-table-learning-with-llms.txt`（31984 字符）供引用检索。