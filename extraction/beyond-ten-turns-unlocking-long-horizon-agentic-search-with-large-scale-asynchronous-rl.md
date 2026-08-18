---
paper_num: "32"
title: "Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with Large-Scale Asynchronous RL"
authors: "Search with Large-Scale Asynchronous RL Jiaxuan Gao 1 , Wei Fu , Minyang Xie 1 , Shusheng Xu Chuyi He 2 , Zhiyu Mei 2 , Banghua Zhu 3 , Yi Wu 1 IS, Tsinghua University, 2 Ant Group 3 University of Washington samjia20@gma"
date: "2026/1/17"
arxiv: "https://arxiv.org/abs/2508.07976"
pdf: "papers/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl.pdf"
slug: "beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl"
tags: []
---

# Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with Large-Scale Asynchronous RL

> [!abstract] 摘要（原文）
> 

## 元信息
- **发表日期**: 2026/1/17
- **作者**: Search with Large-Scale Asynchronous RL Jiaxuan Gao 1 , Wei Fu , Minyang Xie 1 , Shusheng Xu Chuyi He 2 , Zhiyu Mei 2 , Banghua Zhu 3 , Yi Wu 1 IS, Tsinghua University, 2 Ant Group 3 University of Washington samjia20@gma
- **arXiv**: https://arxiv.org/abs/2508.07976
- **本地 PDF**: `papers/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl.pdf`
- **页数**: 21

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p01.png]]
> [!quote] caption
> (Left) Asynchronous RL brings substantial improvements: Through RL training, our agent, ASearcher-Web-QwQ, obtains +15.0, +2.4, and +15.6 improvements on GAIA, xBench, and

> [!tip] 技术解读（多模态）
> # Figure Description

**Architecture/Components/Data Flow:**
The figure depicts a comparative chart for what appears to be a method called **DEPA** (with a variant labeled **DEPA-R**), benchmarking it against several baseline models. The layout shows performance results along a categorical axis (multiple models/tasks listed vertically) against a metric scale (0–2 range). Legend entries distinguish **"Avg@4"** and per-stage breakdowns (**Stage 1** vs **Stage 2**) for two configurations, suggesting a two-stage pipeline evaluation. Data flow appears to compare token-level decoding metrics (e.g., EOS/NLL-related indicators) across competing approaches.

**Key Technical Takeaway:**
DEPA's two-stage variant achieves higher aggregate scores than single-stage baselines, indicating that separating the pipeline into Stage 1 + Stage 2 yields measurable gains in the Avg@4 metric.

# Caption (Verbatim — as rendered; text is heavily overlapping/garbled in the source)

> "Figure : ... DEPA vs ... 1,NLL 2, ... 1,EOS 2, ... 1, ... 2, ... Avg@4 Stage 1 Stage 2 Stage 1 Stage 2 ... (a) ... 2-output ... (b) ..."

**Note:** The page (arXiv:2508.07976v4) has severely overlapping/illegible glyphs in this figure region, so a clean verbatim transcription is not possible from the rendered image alone — most labels appear stacked and unreadable.

## 技术点深读（DEEP）

![[deep/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl.txt`（2528 字符）供引用检索。