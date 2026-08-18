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
![[assets/rllm-relational-table-learning-with-llms-p01.png]]
> [!quote] caption
> Trends in global data volume and in LLM token costs by data type

> [!tip] 技术解读（多模态）
> **Figure 1 Description:**

Figure 1 is a two-panel composite illustrating the cost asymmetry between data volume and LLM processing expenses.

**Left panel** — Stacked bar chart showing Global Data Volume (Zettabytes) by data type from 2010–2025, with categories Video, Image, Audio, Text, and Structured data stacked vertically. Volume rises from ~30 ZB (2010) to ~100 ZB (2025), with Video/Image dominating the totals.

**Right panel** — Stacked area chart showing projected LLM Token Costs (trillion dollars) over the same period. Despite their large volume, Video/Image contribute a small cost sliver, while Text and Structured data occupy the dominant lower region. Costs escalate exponentially, approaching ~$5,000 trillion by 2025.

**Key takeaway:** LLM token costs are dominated by language-type and structured data, not multimedia — motivating efficient Relational Table Learning (RTL) over direct LLM ingestion of all data.

**Caption (verbatim):** Figure 1: Trends in global data volume and in LLM token costs by data type

### Figure 2 (p.2) ⭐深度解读
![[assets/rllm-relational-table-learning-with-llms-p02.png]]
> [!quote] caption
> The architecture of rLLM analyzed using GNNs. This design efficiently captures inter-table dependencies with minimal architectural complexity.

> [!tip] 技术解读（多模态）
> ## Description of Main Figure (Figure 2)

**Architecture / Components / Data Flow:**
The figure depicts the **three-layer hierarchical architecture** of rLLM, with upward arrows indicating data/control progression:

1. **Data Engine Layer** (blue, bottom): foundational ingestion — `Data Loader`, `Graph Builder`, `Table Marker`.
2. **Module Layer** (green, middle): reusable neural building blocks grouped by paradigm — **GNNs** (`GraphConv`, `GraphTransform`), **LLMs** (`Prediction`, `Enhancement`), **TNNs** (`TableConv`, `TableTransform`).
3. **Models Layer** (orange, top): high-level algorithms (`Combine`, `Align`, `Co-Train`, …) that compose modules from the layer below.

**Key Technical Takeaway:**
The strict separation of *data ingestion*, *modular neural primitives*, and *compositional model algorithms* lets users mix-and-match graph, language, and tabular building blocks to assemble novel Relational Table Learning models without rewriting data pipelines.

## Caption (verbatim)

**Figure 2: The architecture of rLLM**

### Figure 3 (p.2) ⭐深度解读
![[assets/rllm-relational-table-learning-with-llms-p02.png]]
> [!quote] caption
> Base data structure in rLLM. Arrows indicate inher- itance relationships and parentheses indicate containment relationships. data, respectively. Overall, this design meets the familiar storage and processing requirements of relational table data consist of table data and foreign key relationships.

> [!tip] 技术解读（多模态）
> ## Description of Main Figure (Figure 2)

**Architecture / Components / Data Flow:**
The figure depicts the **three-layer hierarchical architecture** of rLLM, with upward arrows indicating data/control progression:

1. **Data Engine Layer** (blue, bottom): foundational ingestion — `Data Loader`, `Graph Builder`, `Table Marker`.
2. **Module Layer** (green, middle): reusable neural building blocks grouped by paradigm — **GNNs** (`GraphConv`, `GraphTransform`), **LLMs** (`Prediction`, `Enhancement`), **TNNs** (`TableConv`, `TableTransform`).
3. **Models Layer** (orange, top): high-level algorithms (`Combine`, `Align`, `Co-Train`, …) that compose modules from the layer below.

**Key Technical Takeaway:**
The strict separation of *data ingestion*, *modular neural primitives*, and *compositional model algorithms* lets users mix-and-match graph, language, and tabular building blocks to assemble novel Relational Table Learning models without rewriting data pipelines.

## Caption (verbatim)

**Figure 2: The architecture of rLLM**

### Figure 4 (p.3) ⭐深度解读
![[assets/rllm-relational-table-learning-with-llms-p03.png]]
> [!quote] caption
> The architecture of BRIDGE columns, which can vary greatly in nature. Due to the diverse types of features and the often limited information provided by tables with fewer columns, it is crucial to map or transform some columns into higher-dimensional feature spaces to enhance the sample in- formation. The TableConv module facilitates multi-layer interactive learning among feature columns to extrac

> [!tip] 技术解读（多模态）
> # Figure 4: Architecture of BRIDGE

## Description of Main Figure

The diagram depicts a two-stage encoding pipeline processing relational tabular data.

**Components & Data Flow:**
1. **Relational Tabular-data (input):** Multiple linked tables (Table I, II, III, …) connected via Primary Key (PK)–Foreign Key (FK) relationships, capturing inter-table structure.
2. **Table Encoder:** Consumes the raw tables, extracts "Tabular features," and projects them into "Tabular embeddings" — handling heterogeneous column types within each table.
3. **Graph Encoder:** Receives both the tabular embeddings *and* the **non-tabular features** (explicit graph structure plus other auxiliary features) representing FK-based sample-to-sample associations.
4. **Output:** Joint representation produced by the graph encoder.

## Key Technical Takeaway

BRIDGE simplifies Relational Data Learning (RDL) by (a) reducing multi-table input to a single target table plus one selected relational neighbor table, (b) preprocessing all remaining tables into dense embeddings, and (c) modeling the residual FK structure with a GNN. This decouples tabular-feature learning (Table Encoder, e.g., TableTransform/TableConv) from relational-graph reasoning (Graph Encoder, e.g., GraphTransform/GraphConv), enabling concurrent exploitation of intra-table heterogeneity and inter-table dependencies.

## Caption (Verbatim)

**Figure 4: The architecture of BRIDGE**

## 技术点深读（DEEP）

![[deep/rllm-relational-table-learning-with-llms]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/rllm-relational-table-learning-with-llms.txt`（31984 字符）供引用检索。