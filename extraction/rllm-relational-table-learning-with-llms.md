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
> **Main Figure Description (≤120 words):**

The figure presents two side-by-side visualizations framing the rLLM motivation. **Left panel (stacked bar):** Global data volume (Zettabytes, 2010–2025) split across five modalities—Structured data, Text, Audio, Image, and Video—growing from ~30 ZB to ~100 ZB. **Right panel (stacked area):** Projected LLM tokenization cost (trillion USD, 2010–2025) over the same modalities. Two annotations highlight an inversion: multimodal data (Video/Image) dominates volume but incurs low token cost, whereas Text volume is small but tokenization cost is disproportionately high. Together, the charts motivate applying LLMs to relational/structured tabular data, where high cost-per-volume tradeoffs must be managed.

**Key takeaway:** Volume does not equal LLM cost—tokenization economics favor multimodal data over text, motivating efficient relational-table encodings.

**Caption (verbatim):**
> "Trend in Global Data Volume by Data Type (2010-2025) — Trend in LLM Token Costs by Data Type (2010-2025). Source: The rLLM (relationLLM) project."

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/rllm-relational-table-learning-with-llms-fig02.png]]
*整页渲染: ![[assets/rllm-relational-table-learning-with-llms-p02.png]]*
> [!quote] caption
> The architecture of rLLM analyzed using GNNs. This design efficiently captures inter-table dependencies with minimal architectural complexity.

> [!tip] 技术解读（多模态）
> ## Architecture Description

The figure depicts a three-tier hierarchical framework with upward data flow:

1. **Data Engine (bottom, blue)** — foundational layer containing `Data Loader`, `Graph Builder`, and `Table Marker`, responsible for ingesting raw inputs and constructing structured representations (graphs, tables).

2. **Modules (middle, green)** — modeling primitives grouped by modality:
   - **GNNs**: GraphConv, GraphTransform
   - **LLMs**: Prediction, Enhancement
   - **TNNs**: TableConv, TableTransform

3. **Models (top, orange)** — high-level strategies: `Combine`, `Align`, `Co-Train` (plus extensibility markers).

Arrows indicate sequential upward propagation: raw data → structured representations → learned modules → composed models.

## Key Technical Takeaway

The framework's core insight is the **separation of concerns across three abstraction levels** — data construction, per-modality learning, and multi-model integration. This decoupling lets practitioners swap Graph/LLM/Table encoders independently and plug in different composition strategies (combine, align, co-train) without rewriting the entire pipeline, fostering reusability and modular extensibility across heterogeneous data modalities.

## Caption (Verbatim Transcription)

> **Models**: Combine | Align | Co-Train | …
> **Modules**: GNNs (GraphConv, GraphTransform) | LLMs (Prediction, Enhancement) | TNNs (TableConv, TableTransform) | …
> **Data Engine**: Data Loader | Graph Builder | Table Marker | …

### Figure 3 (p.2) ⭐深度解读
![[assets/crops/rllm-relational-table-learning-with-llms-fig03.png]]
*整页渲染: ![[assets/rllm-relational-table-learning-with-llms-p02.png]]*
> [!quote] caption
> Base data structure in rLLM. Arrows indicate inher- itance relationships and parentheses indicate containment relationships. data, respectively. Overall, this design meets the familiar storage and processing requirements of relational table data consist of table data and foreign key relationships.

> [!tip] 技术解读（多模态）
> # Figure Description

**Architecture/Components:**
The UML-style class diagram illustrates a unified `Dataset` framework (dark blue node) that inherits from two parents: `ABC (Python)` for abstract base class enforcement and `Dataset (Pytorch)` for native PyTorch compatibility. Concrete dataset instances (light blue: *Cora, IMDB, Titanic…*) branch from this class. The dashed expansion on the right shows the two modality branches — `BaseGraph` → `GraphData` (for graph-structured data like Cora/IMDB) and `BaseTable` → `TableData` (for tabular data like Titanic), with `…` denoting additional variants.

**Data Flow:** User-defined datasets instantiate through the `Dataset` superclass, gaining both PyTorch DataLoader integration and modality-specific base-class behavior.

**Key Technical Takeaway:** By combining Python's `ABC` with PyTorch's `Dataset` via multiple inheritance, the framework enforces strict interface contracts while remaining fully compatible with the PyTorch ecosystem, supporting heterogeneous data modalities (graph and tabular) under one cohesive API.

# Caption (Verbatim)

*(No printed caption text is visible in the figure beyond node labels: "ABC (Python)", "Dataset (Pytorch)", "Dataset", "Cora, IMDB, Titanic…", "BaseGraph", "GraphData", "BaseTable", "TableData", "…".)*

### Figure 4 (p.3) ⭐深度解读
![[assets/crops/rllm-relational-table-learning-with-llms-fig04.png]]
*整页渲染: ![[assets/rllm-relational-table-learning-with-llms-p03.png]]*
> [!quote] caption
> The architecture of BRIDGE columns, which can vary greatly in nature. Due to the diverse types of features and the often limited information provided by tables with fewer columns, it is crucial to map or transform some columns into higher-dimensional feature spaces to enhance the sample in- formation. The TableConv module facilitates multi-layer interactive learning among feature columns to extrac

> [!tip] 技术解读（多模态）
> **Description of the main figure (architecture/components/data flow + key takeaway):**

The figure depicts a two-stage neural architecture for learning from relational tabular data. **Data flow:** Relational tables (Tables I, II, III) linked by primary/foreign keys are flattened into tabular features, which are passed through a **Table Encoder** (depicted as an attention/transformer block) to produce tabular embeddings. These embeddings, together with non-tabular inputs (e.g., graph structure and other features) routed via a side branch, are fed into a **Graph Encoder** (a GNN) that fuses both modalities and emits the final **Output**.

**Key technical takeaway:** Modeling tabular data and graph topology in *separate but jointly-trained encoders* lets the system exploit foreign-key relational links as explicit graph edges while preserving dense feature interactions through the table encoder—a practical recipe for unifying schema-relational learning with graph representation learning.

**Caption transcription (verbatim):**

No standalone caption text is present beneath or within the figure. The visible in-image labels are:

> Non-tabular features (i.e., graph structure and other features) · PK Primary Key · FK Foreign Key · Tabular features · Tabular embeddings · Output · Relational Tabular-data · Table Encoder · Graph Encoder · Table I · Table II · Table III

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/rllm-relational-table-learning-with-llms-tab01.png]]
> [!quote] caption
> Summary of the datasets.

> [!tip] 表格解读（多模态）
> **Architecture / Components**
The figure is a tabular summary (Table 1) compiling three heterogeneous relational datasets used in the study: (1) a **MovieLens-style dataset** with `users`, `movies`, and a `ratings` relation, labeled for user age range (7 classes); (2) a **Last.fm-style dataset** with `artists`, `user_artists`, and `user_friends` relations, labeled for artist genre (11 classes); and (3) an **academic dataset** with `papers`, `authors`, `citations`, and `writings` relations, labeled for paper conference (14 classes). Columns report row/column counts per table, relation tables, label semantics, class count, and a fixed train/val/test split (`N/500/1000`).

**Key Technical Takeaway**
Train-split scales with class count (140→220→280), suggesting per-class balanced sampling, while val/test are kept constant for fair cross-dataset benchmarking of relational models.

(99 words)

**Caption (verbatim):**
Table 1: Summary of the datasets.

### Table 2 (p.5) ⭐深度解读
![[assets/crops/rllm-relational-table-learning-with-llms-tab02.png]]
> [!quote] caption
> Classification accuracy.

> [!tip] 表格解读（多模态）
> **Description of Table 2:**

This is a benchmark comparison table (not an architectural figure) presenting **classification accuracy** across three tabular/relational datasets (TML1M, TLF2K, TACM12K) for five methods: a Random baseline, three tabular deep-learning models (TabTransformer, TabNet, FT-Transformer), and the proposed **BRIDGE** model. Each cell reports mean accuracy ± standard deviation. The data flow is straightforward: methods are evaluated head-to-head on identical datasets.

**Key technical takeaway:** BRIDGE achieves state-of-the-art accuracy on every dataset, but its margin is striking on relational graphs—nearly **3× the best baseline** on TLF2K (0.422 vs. 0.137) and ~2× on TACM12K (0.256 vs. 0.135), suggesting the method's gains come disproportionately from exploiting relational structure rather than from raw tabular modeling power.

**Caption transcribed verbatim:**

*Table 2: Classification accuracy.*

## 技术点深读（DEEP）

![[deep/rllm-relational-table-learning-with-llms]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/rllm-relational-table-learning-with-llms.txt`（31984 字符）供引用检索。