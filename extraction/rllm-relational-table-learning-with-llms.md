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

### Figure 1 (p.1)
![[assets/rllm-relational-table-learning-with-llms-p01.png]]
> [!quote] caption
> Trends in global data volume and in LLM token costs by data type

### Figure 2 (p.2)
![[assets/rllm-relational-table-learning-with-llms-p02.png]]
> [!quote] caption
> The architecture of rLLM analyzed using GNNs. This design efficiently captures inter-table dependencies with minimal architectural complexity.

### Figure 3 (p.2)
![[assets/rllm-relational-table-learning-with-llms-p02.png]]
> [!quote] caption
> Base data structure in rLLM. Arrows indicate inher- itance relationships and parentheses indicate containment relationships. data, respectively. Overall, this design meets the familiar storage and processing requirements of relational table data consist of table data and foreign key relationships.

### Figure 4 (p.3)
![[assets/rllm-relational-table-learning-with-llms-p03.png]]
> [!quote] caption
> The architecture of BRIDGE columns, which can vary greatly in nature. Due to the diverse types of features and the often limited information provided by tables with fewer columns, it is crucial to map or transform some columns into higher-dimensional feature spaces to enhance the sample in- formation. The TableConv module facilitates multi-layer interactive learning among feature columns to extrac

## 全文文本
全文已存 `extraction/fulltext/rllm-relational-table-learning-with-llms.txt`（31984 字符）供引用检索。