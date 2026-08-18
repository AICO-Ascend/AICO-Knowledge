---
paper_num: "1"
title: "IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse"
authors: "IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse Yushi Bai1†, Qian Dong1†, Ting Jiang2, Xin Lv2 Zhengxiao Du2, Aohan Zeng12, Jie Tang1, Juanzi Li1 1Tsinghua University 2Z.ai"
date: "2026/3/12"
arxiv: "https://arxiv.org/abs/2603.12201"
pdf: "papers/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse.pdf"
slug: "indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse"
tags: [sparse-attention, kv-cache]
---

# IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse

> [!abstract] 摘要（原文）
> 1\. 🚀 IndexCache 提出了一种针对 DeepSeek Sparse Attention (DSA) 的高效策略，通过将 Transformer 层分为保留索引器的 Full 层和复用邻近 Full 层索引的 Shared 层，大幅降低了计算开销。 2. 💡 该研究提供了训练前贪心搜索和训练中多层蒸馏两种优化方案，前者无需微调模型即可优化索引器层配置，后者通过联合训练使模型适配跨层索引复用。 3. 📈 在 30B 规模的 DSA 模型上实验表明，IndexCache 可去除 75% 的索引器计算，在保持模型性能的同时，实现了最高 1.82× 的预填充速度提升和 1.48× 的解码速度提升。

## 元信息
- **发表日期**: 2026/3/12
- **作者**: IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse Yushi Bai1†, Qian Dong1†, Ting Jiang2, Xin Lv2 Zhengxiao Du2, Aohan Zeng12, Jie Tang1, Juanzi Li1 1Tsinghua University 2Z.ai
- **arXiv**: https://arxiv.org/abs/2603.12201
- **本地 PDF**: `papers/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse.pdf`
- **页数**: 18

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p01.png]]
> [!quote] caption
> Benchmark comparison between GLM-5 and GLM-5 + IndexCache. IndexCache removes 50% of indexer computations while maintaining comparable performance across both long-context and reasoning tasks, delivering ∼1.2× end-to-end speedup.ai. 1[cs.CL] 12 Mar 2026

> [!tip] 技术解读（多模态）
> # Figure 1 — Benchmark Comparison Chart (not an architecture diagram)

**Description:** Figure 1 is a grouped bar chart, not a system architecture. It compares two configurations across 10 benchmarks split into two categories:

- **Series:** GLM-5 (light bars) vs. GLM-5 + IndexCache (1/2) (dark bars), labeled with a "1.2× E2E Speedup" tag in the legend.
- **Long-Context group:** MRCR v2 (71.1/72.3), Graph Walks (92.7/90.8), LongBench v2 (64.5/66.0), RULER (97.7/97.3), AA-LCR (66.2/67.2).
- **General & Reasoning group:** HLE (30.4/30.4), HLE w/ tools (50.4/50.3), SciCode (45.0/47.0), AIME25 (95.9/95.9), IFBench (71.0/70.0).
- **Data flow (conceptual):** baseline GLM-5 evaluation vs. GLM-5 with cross-layer index reuse → scores per benchmark → side-by-side visual comparison.

**Key takeaway:** Cutting the indexer workload in half (1 Full layer per 2 layers) yields ~1.2× end-to-end speedup with negligible accuracy loss across both retrieval-style and reasoning-style tasks.

# Caption (verbatim)

> Figure 1: Benchmark comparison between GLM-5 and GLM-5 + IndexCache. IndexCache removes 50% of indexer computations while maintaining comparable performance across both long-context and reasoning tasks, delivering ∼ 1.2× end-to-end speedup.

### Figure 2 (p.3) ⭐深度解读
![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p03.png]]
> [!quote] caption
> Side-by-side comparison of inference loops. (a) Standard DSA runs the lightning indexer at every layer. (b) IndexCache adds a single conditional branch (red lines): F layers compute and cache fresh indices; S layers reuse the cached indices. Note that Tcache is a temporary buffer holding only the current index tensor; it is overwritten at each F layer and requires no additional GPU memory beyond w

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】IndexCache 架构图(Fig.2)：对比 (a) 标准 DSA（每层跑 lightning indexer）与 (b) IndexCache（加条件分支：F 层算并缓存索引到临时 buffer T_cache，S 层直接复用 T_cache 跳过 indexer）。T_cache 仅存当前索引张量、每 F 层覆写、无额外显存。利用 token 选择跨层冗余消除稳定层 indexer 计算。架构核心图。

### Figure 3 (p.8) ⭐深度解读
![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p08.png]]
> [!quote] caption
> Relative speedup of IndexCache over the DSA baseline across three inference settings on the 30B model. DSA baseline is normalized to 100%.

> [!tip] 技术解读（多模态）
> ## Figure 3 Description

**Architecture/Components:** The figure consists of three side-by-side grouped bar charts sharing the same x-axis (Context Length: 10K, 60K, 120K, 200K) and y-axis (Relative Speedup %, baseline = 100%). Each chart compares three configurations: DSA baseline (gray dotted), IndexCache with 1/2 indexer retention (blue), and IndexCache with 1/4 indexer retention (red). Subplot (a) measures prefill time, (b) per-request decode throughput, and (c) full-batch decode throughput.

**Key Technical Takeaway:** IndexCache at 1/4 indexer retention delivers a substantial 185% speedup in prefill at 200K tokens, with the benefit scaling monotonically with context length — confirming that eliminating redundant indexer computations is increasingly valuable as sequences grow.

## Caption (verbatim)

Figure 3: Relative speedup of IndexCache over the DSA baseline across three inference settings on the 30B model. DSA baseline is normalized to 100%.

### Figure 4 (p.16) ⭐深度解读
![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p16.png]]
> [!quote] caption
> Pairwise top-k index overlap ratio between all layer pairs of the 30B DSA model.

> [!tip] 技术解读（多模态）
> **Main figure description:**

The figure is a 47×47 heatmap visualizing the pairwise top-k index overlap ratio (|T⁽ⁱ⁾ ∩ T⁽ʲ⁾|/k, with k=2048) between every pair of transformer layers in a 30B DSA (DeepSeek Sparse Attention) model. Both axes span Layer 0–46, and the viridis colormap encodes overlap from 0.0 (dark purple) to 1.0 (yellow). A bright diagonal band (overlap ≈ 0.7–1.0) shows that adjacent layers select nearly identical top-k token sets. Distinct yellow clusters (e.g., layers 3–5, 6–8, 17–30, 31–36) reveal functional blocks of internally consistent token selection. Red rectangles overlay the greedily-searched 1/4 IndexCache sharing blocks along the diagonal. Off-diagonal corners (early vs. late layers) appear notably darker (overlap ≤ 0.4).

**Key technical takeaway:** Cross-layer top-k index overlap is highly clustered into contiguous blocks, empirically justifying the IndexCache strategy of sharing indexer computations across groups of consecutive layers.

**Caption verbatim:**

Figure 4: Pairwise top-k index overlap ratio between all layer pairs of the 30B DSA model. Shared blocks according to the greedily-searched 1/4 IndexCache pattern are marked.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathcal{L}^{\mathrm{I}}_{\mathrm{multi}} = \sum_{j=0}^{m} \frac{1}{m+1}\sum_{t} D_{\mathrm{KL}}\!\left( \mathbf{p}^{(\ell+j)}_{t} \,\big\|\, \mathbf{q}^{(\ell)}_t \right),
$$

$$
\mathcal{L}^{\mathrm{I}}_{\mathrm{avg}} = \sum_{t} D_{\mathrm{KL}}\!\left( \bar{\mathbf{p}}_{t} \,\big\|\, \mathbf{q}^{(\ell)}_t \right).
$$

$$
\nabla_\theta \, \mathcal{L}^{\mathrm{I}}_{\mathrm{multi}} &= -\sum_{j=0}^{m} \frac{1}{m+1} \sum_{t} \nabla_\theta \sum_{s} \mathbf{p}^{(\ell+j)}_{t}(s) \log \mathbf{q}^{(\ell)}_t(s) \notag \\ &= -\sum_{t} \nabla_\theta \sum_{s} \underbrace{\Bigl(\textstyle\sum_{j=0}^{m} \frac{1}{m+1} \mathbf{p}^{(\ell+j)}_{t}(s)\Bigr)}_{\bar{\mathbf{p}}_{t}(s)} \log \mathbf{q}^{(\ell)}_t(s) \;=\; \nabla_\theta \, \mathcal{L}^{\mathrm{I}}_{\mathrm{avg}}.
$$

## 相关论文

- [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] — Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter
- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] — A Survey on Large Language Model Acceleration based on KV Cache Management
- [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] — KV Cache Optimization Strategies for Scalable and Efficient LLM Inference
- [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] — CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion

## 技术点深读（DEEP）

![[deep/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse.txt`（58028 字符）供引用检索。