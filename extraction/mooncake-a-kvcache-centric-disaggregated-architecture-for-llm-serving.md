---
paper_num: "45"
title: "Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving"
authors: "Architecture for LLM Serving Ruoyu Qin♠♡1 Zheming Li♠1 Weiran He♠ Mingxing Zhang♡2 Yongwei Wu♡ Weimin Zheng♡ Xinran Xu♠2 ♠Moonshot AI ♡Tsinghua University"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2407.00079"
pdf: "papers/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving.pdf"
slug: "mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving"
tags: [kv-cache, disaggregated-serving]
---

# Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving

> [!abstract] 摘要（原文）
> 1\. 🚀 Mooncake 是一种 KVCache-centric 的解耦架构，通过分离 Prefill 和 Decoding 集群并利用 GPU 集群中未充分利用的 CPU、DRAM 和 SSD 资源实现 KVCache 的分层缓存，旨在最大化有效吞吐量并满足服务水平目标 (SLO)。 2. 🧠 其核心在于 KVCache-centric 调度器，该调度器结合了 Chunked Pipeline Parallelism (CPP) 和分层 Prefill 等优化，以高效处理长上下文请求并实现 KVCache 热点迁移，同时采用预测驱动的早期拒绝策略以应对过载场景。 3. 📊 实验表明，Mooncake 在长上下文场景中性能卓越，相比基线方法可实现高达 525% 的吞吐量提升，在实际工作负载下能处理多 75% 的请求，同时严格遵守 TTFT 和 TBT 等性能 SLOs。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Architecture for LLM Serving Ruoyu Qin♠♡1 Zheming Li♠1 Weiran He♠ Mingxing Zhang♡2 Yongwei Wu♡ Weimin Zheng♡ Xinran Xu♠2 ♠Moonshot AI ♡Tsinghua University
- **arXiv**: https://arxiv.org/abs/2407.00079
- **本地 PDF**: `papers/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving.pdf`
- **页数**: 23

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p02.png]]
> [!quote] caption
> Mooncake Architecture. remote location will prolong the TTFT, and a large batch size will lead to a larger TBT. Thus, the utilization of both these throughput-oriented optimizations may lead to violations of latency-related SLOs.

> [!tip] 技术解读（多模态）
> **论文核心架构图分析**

**1) 主要架构/组件/数据流描述**

该图为 **Mooncake 架构图**，展示了一种以 KVCache 为中心的 LLM 服务解耦架构：

- **组件**：左侧为输入请求队列；中间区域包含多个 GPU 实例节点，分为 **prefill（预填充）节点**（上半部，含 KVCache 池 "3.450678"）和 **decoding（解码）节点**（下半部，含 KVCache 池）；中央为全局调度器（Conductor），负责调度决策。
- **数据流**：请求首先被路由到 prefill 节点；prefill 计算产生的 KVCache（图中上方柱状图表示）通过高速互联被流式传输到对应的 decoding 节点；decoding 节点加载 KVCache 后进行连续批处理生成输出（右侧生成的文本序列 "!\"#$%..."）。箭头与乘号 ⊗ 标示预填充与解码节点间的 KVCache 流转与匹配关系。

**2) 关键技术要点**

**基于 KVCache 的预填充-解码解耦（Disaggregation）：** 预填充（compute-bound）与解码（memory-bound）两种异构负载被分离到不同实例，KVCache 作为"一等公民"在实例间显式流转，全局 Conductor 综合考虑 TTFT/TBT SLO、KVCache 命中率、DRAM 容量与网络拥塞进行实例配对与调度优化，从而实现吞吐与时延的联合优化。**

**3) 图注逐字转录**

> **Figure 1: Mooncake Architecture.**

### Figure 2 (p.4) ⭐深度解读
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p04.png]]
> [!quote] caption
> Normalized throughput and latency of prefill and decoding stages with different sequence lengths or batch sizes for the dummy LLaMA2-70B model. the computational complexity of attention networks scales quadratically with input length while the complexity of MLP scales linearly, computation time in the prefill stage generally increases superlinearly with input length, as shown in the left part of F

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】Mooncake 解耦式 KVCache 服务架构：prefill（compute-bound，注意力二次复杂度）与 decode（memory-bound，自回归批处理）分到独立节点池。核心是 disaggregated KVCache 层，池化 CPU/DRAM/SSD/RDMA 资源→跨节点 cache 复用、减冗余计算；调度器做 early rejection + SLO 准入(TTFT/TBT)+负载均衡。把计算阶段与 KVCache 存储解耦→弹性扩展、严 SLO 下更高吞吐。架构核心图。

### Figure 3 (p.5) ⭐深度解读
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p05.png]]
> [!quote] caption
> The KVCache pool in CPU memory. Each block is attached with a hash value determined by both its own hash and its prefix for deduplication.

> [!tip] 技术解读（多模态）
> ## Description of Figure 3

**Architecture/Components:** Figure 3 depicts the KVCache pool residing in CPU memory. At the top, raw tokens (e.g., `)`, `7`, `*`, `6`, `#`, `$`, `8`, `+`, `%`) are shown being grouped into hash blocks. A dashed intermediate layer represents hash-chained block entries (e.g., `0*#$%&'!$+`, `1*#$%&'!0!2+`) connected via `9)4*+!` link pointers, forming a dedup chain. The lower portion shows paged memory regions (`!"###"$%"&'&`, `0*"/12)$%+,` etc.) storing both **prefix cache blocks** and **full cache blocks**, indexed by block IDs (`=...)6;<()*+#`, `;":20$#";<()*+#`).

**Data Flow:** Tokens → hash grouping → chained dedup blocks → split into prefix/full KVCache pages → distributed across multiple paged CPU memory pools with hash-based addressing.

**Key Technical Takeaway:** KVCache blocks are uniquely addressed by a composite hash of *content + prefix context*, enabling deduplication of identical token sequences across requests while preserving contextual locality for prefix reuse.

---

## Caption (verbatim)

**Figure 3:** The KVCache pool in CPU memory. Each block is attached with a hash value determined by both its own hash and its prefix for deduplication.

### Figure 4 (p.6) ⭐深度解读
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]]
> [!quote] caption
> Workflow of inference instances. ( ) For prefill instances, the load and store operations of the KVCache layer are performed layer-by-layer and in parallel with the prefill computation to mitigate transmission overhead (see §5.2). (y ) For decoding instances, asynchronous loading is performed concurrently with GPU decoding to prevent GPU idle time. 4) Decoding: After all the KVCache is received i

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

Figure 4 depicts two parallel workflow pipelines for LLM inference. The left side shows **prefill instances**, organized into two stacked stages where the upper stage handles KVCache load/store operations (e.g., 56789... entries) and the lower stage runs the prefill computation (e.g., AB+C'/C'FIB computations) concurrently — both progressing layer-by-layer. The right side shows **decoding instances**, similarly split: the upper stage (≤22'*+,-# buffer) receives asynchronously loaded data while the lower stage performs GPU decoding (e.g., ?6@/,'AB+C). A transfer arrow at the bottom (6:9!'"#$%&&'(5.$+3'. ) connects the prefill output to the decoding input, representing KVCache handoff. **Key takeaway:** Prefill uses *layer-by-layer parallelism* between compute and KVCache transfer to hide transmission latency, while decoding uses *async loading* to keep the GPU saturated — both are overlap strategies targeting different bottlenecks.

### Figure 5 (p.6) ⭐深度解读
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]]
> [!quote] caption
> Input and output length distributions in the request trace. 4

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

Figure 4 depicts two parallel workflow pipelines for LLM inference. The left side shows **prefill instances**, organized into two stacked stages where the upper stage handles KVCache load/store operations (e.g., 56789... entries) and the lower stage runs the prefill computation (e.g., AB+C'/C'FIB computations) concurrently — both progressing layer-by-layer. The right side shows **decoding instances**, similarly split: the upper stage (≤22'*+,-# buffer) receives asynchronously loaded data while the lower stage performs GPU decoding (e.g., ?6@/,'AB+C). A transfer arrow at the bottom (6:9!'"#$%&&'(5.$+3'. ) connects the prefill output to the decoding input, representing KVCache handoff. **Key takeaway:** Prefill uses *layer-by-layer parallelism* between compute and KVCache transfer to hide transmission latency, while decoding uses *async loading* to keep the GPU saturated — both are overlap strategies targeting different bottlenecks.

### Figure 6 (p.7) ⭐深度解读
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p07.png]]
> [!quote] caption
> CDF (Cumulative Distribution

> [!tip] 技术解读（多模态）
> **Figure 6 — CDF of Block Hit Count**

**Architecture/Components:**
- **Axes:** X = Block Hit Count (log scale, 10⁰–10⁴); Y = CDF (0.0–1.0)
- **Curve:** A monotonic blue step function rising sharply at the low end and asymptotically saturating near 1.0
- **Inputs:** Aggregated hash-block reuse counts from the request trace dataset

**Data flow:** Block hit counts → sorted empirical distribution → cumulative step function → CDF visualization.

**Key takeaway (≈120 words):** The CDF reveals an extremely skewed, long-tailed reuse pattern: roughly 60% of blocks are reused only once and ~90% fewer than ten times, with only a tiny tail of "hot" blocks reaching 10⁴ hits. This implies that KVCache reuse is highly concentrated in a small minority of prefix blocks, while the vast majority contribute negligibly to hit rate. Consequently, cache-sizing policies and eviction strategies (LRU/LFU/LengthAware) should prioritize capturing the high-frequency prefix tail rather than uniformly caching all blocks — capacity beyond ~10 hits per block yields diminishing returns, consistent with the paper's reported saturation around 50% hit ratio at 50,000 blocks.

**Caption (verbatim):**
*Figure 6: CDF (Cumulative Distribution Function) of the block hit count in the request trace.*

### Figure 7 (p.9) ⭐深度解读
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p09.png]]
> [!quote] caption
> Latency of storing KVCache of different request lengths (Layer-wise latency refers to the difference in latency between Layer-wise Prefill and Prefill without storing KVCache).

> [!tip] 技术解读（多模态）
> **Figure 7 — Description (≤120 words):**

The figure is a grouped bar chart comparing two KVCache-storing strategies across five input lengths. The **x-axis** lists Sequence Lengths (8k, 16k, 32k, 64k, 128k); the **y-axis** is Latency (seconds, 0 – ~0.85). Two series are plotted per length: **Serialized** (blue) and **Layer-wise** (orange). Data flow: each request's prefill executes layer-by-layer, with the KVCache for layer *i* stored asynchronously while layer *i+1* computes — overlapping memory writes with attention. The blue bars grow steeply (~0.10 s → ~0.85 s) while the orange bars stay nearly flat (~0.10 s) at all lengths.

**Key takeaway:** Overlapping KVCache storage with the next layer's attention keeps prefill latency roughly constant regardless of sequence length, eliminating VRAM-induced TTFT growth.

**Caption (verbatim):**
Figure 7: Latency of storing KVCache of different request lengths (Layer-wise latency refers to the difference in latency between Layer-wise Prefill and Prefill without storing KVCache).

### Figure 8 (p.11) ⭐深度解读
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p11.png]]
> [!quote] caption
> The prefill scheduling experiment in the Mooncake cluster.

> [!tip] 技术解读（多模态）
> **Figure 8 Description:**

Figure 8 is a **box plot** comparing Time-To-First-Token (TTFT) distributions across four scheduling strategies evaluated in the Mooncake cluster. The Y-axis measures TTFT in seconds (0–250+), with a dashed horizontal SLO line at ~30s. The four categories on the X-axis are:

- **KVCache-centric** – tightest distribution, median near 0s
- **cache-aware** – compact distribution, median ~2s
- **load-balancing** – wide IQR (~30–100s), median ~60s
- **random** – largest spread, median ~100s with extreme outliers up to ~270s

Triangular markers (▲) denote the mean. The plot clearly shows that cache-aware/KVCache-centric policies achieve both lower medians and tighter tails, while load-only and random strategies violate the SLO frequently.

**Key takeaway:** Pure load-balancing ignores cache locality, producing TTFT distributions that frequently breach the SLO — confirming that cache-hit awareness is essential for prefilling latency guarantees in Mooncake.

**Caption (verbatim):**
> *Figure 8: The prefill scheduling experiment in the Mooncake cluster.*

### Figure 9 (p.13) ⭐深度解读
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p13.png]]
> [!quote] caption
> The load of prefill and decoding instances over 20 minutes, before using the prediction- based early rejection.

> [!tip] 技术解读（多模态）
> **Figure Description & Key Takeaway:**

Figure 9 is a time-series line chart spanning a 20-minute window (x-axis: 0:00 → 20:00) with load percentage on the y-axis (0–100%). Two curves are plotted: a **green line** representing the load on **prefill instances** and a **yellow line** representing the load on **decoding instances**. Both oscillate roughly between 10% and 95%, exhibiting pronounced anti-phase behavior—when one peaks, the other tends to dip, and vice versa.

**Key takeaway:** The chart empirically demonstrates the load-coupling instability introduced by naive early rejection: scheduling decisions lag behind actual decoding load, causing phase-staggered oscillation between prefill and decoding pools and resulting in poor cluster utilization. This motivates the prediction-based early rejection framework introduced in §7.4.

**Caption (verbatim):**

Figure 9: The load of prefill and decoding instances over 20 minutes, before using the prediction-based early rejection.

### Figure 10 (p.14) ⭐深度解读
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p14.png]]
> [!quote] caption
> Instance load when applying Early Rejection and Early Rejection Based on Prediction. conditions where resources are scarce and accurate predictions are necessary, making request-level predictions particularly difficult.

> [!tip] 技术解读（多模态）
> **Figure 10 — Description:**

The figure contrasts two load-management strategies across four sequential time steps, visualized as stacked bar charts of instance load on prefilling (top row) and decoding (bottom row) instances, each annotated with a dashed TBT-threshold line.

**(a) Early Rejection:** As load progresses, instances whose TBT exceeds the threshold are progressively rejected (star markers alternate empty/filled across steps), causing the decoding instance count to drop sharply.

**(b) Early Rejection Based on Prediction:** Load is forecasted ahead of time using the prefill→uniform-decoding pipeline; far fewer rejections occur (mostly empty stars), keeping decoding instances stable.

**Key takeaway:** Prediction-driven rejection retains more decoding instances under overload because the system-level forecast (uniform decoding time *t_d*, prefiltered to remove requests that would already finish before *t*) prevents premature evictions that the reactive policy in (a) cannot avoid.

**Caption (verbatim):** Figure 10: Instance load when applying Early Rejection and Early Rejection Based on Prediction.

### Figure 11 (p.16) ⭐深度解读
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]]
> [!quote] caption
> End-to-end experiments of Mooncake and vLLM on the ArXiv Summarization and L-Eval datasets instances. In real-world clusters, the demand for prefill and decoding instances generally remains stable over certain periods, with only minor temporary imbalances. Thus, the proportion of prefill and decoding instances can be preset. Future research will explore more flexible deployment and conversion meth

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

Figure 11 presents a 2×2 grid of end-to-end performance benchmarks comparing Mooncake against vLLM variants on two long-context datasets (ArXiv Summarization, L-Eval). The top row plots normalized P90 TTFT (Time To First Token) versus request rate, while the bottom row plots normalized P90 TBT (Time Between Tokens). Three series are compared: Mooncake-[3P+1D] (blue) plus two baseline configurations (red, orange). Across all four panels, Mooncake's disaggregated architecture sustains lower latency values at substantially higher request rates before saturating the SLO thresholds (dashed lines at 1.0). The bottom-row TBT curves particularly show Mooncake flattening near ~0.5 while baselines climb toward violation.

**Key takeaway:** Mooncake's prefill–decode disaggregation decouples TTFT from TBT bottlenecks, enabling 2–3× higher sustainable request rates under identical SLOs.

**Verbatim caption:**

Figure 11: End-to-end experiments of Mooncake and vLLM on the ArXiv Summarization and L-Eval datasets

### Figure 12 (p.16) ⭐深度解读
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]]
> [!quote] caption
> End-to-end experiments of Mooncake and vLLM on simulated data.

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

Figure 11 presents a 2×2 grid of end-to-end performance benchmarks comparing Mooncake against vLLM variants on two long-context datasets (ArXiv Summarization, L-Eval). The top row plots normalized P90 TTFT (Time To First Token) versus request rate, while the bottom row plots normalized P90 TBT (Time Between Tokens). Three series are compared: Mooncake-[3P+1D] (blue) plus two baseline configurations (red, orange). Across all four panels, Mooncake's disaggregated architecture sustains lower latency values at substantially higher request rates before saturating the SLO thresholds (dashed lines at 1.0). The bottom-row TBT curves particularly show Mooncake flattening near ~0.5 while baselines climb toward violation.

**Key takeaway:** Mooncake's prefill–decode disaggregation decouples TTFT from TBT bottlenecks, enabling 2–3× higher sustainable request rates under identical SLOs.

**Verbatim caption:**

Figure 11: End-to-end experiments of Mooncake and vLLM on the ArXiv Summarization and L-Eval datasets

### Figure 13 (p.17) ⭐深度解读
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p17.png]]
> [!quote] caption
> Request TTFT and TBT distributions of Mooncake and vLLM under real workloads

> [!tip] 技术解读（多模态）
> # Figure 13 Description

**Note:** The figure itself (CDF plots) is not visible in the rendered page — only its caption appears. The description below is reconstructed from the caption and accompanying text in §8.1.3.

## Architecture / Components / Data Flow

Figure 13 is a **two-panel CDF plot** comparing request-level latency distributions between two serving stacks on identical real-world traces:

- **Mooncake-[10P+10D]** — 10 prefill instances + 10 decoding instances (disaggregated prefill/decode).
- **vLLM-[20M]** — 20 monolithic instances.
- **Left panel:** TTFT (Time To First Token) CDF, with an SLO threshold at **30 s**.
- **Right panel:** per-token TBT (Time Between Tokens) CDF, capped at **0.1 s/token**.
- **Data flow:** replayed production request traces → dispatched to either Mooncake's prefill→decode pipeline or vLLM's integrated engine → per-request TTFT and TBT samples → empirical CDF curves.

## Key Technical Takeaway

TTFT compliance is near-identical (~100%) for both systems, but **TBT SLO adherence diverges sharply**: Mooncake satisfies it for ~100% of requests vs. **only 57% for vLLM**, allowing Mooncake to serve ~75% more requests under the same SLOs.

## Caption (verbatim)

> Figure 13: Request TTFT and TBT distributions of Mooncake and vLLM under real workloads

## 相关论文

- [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] — KV Cache Optimization Strategies for Scalable and Efficient LLM Inference
- [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] — CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion
- [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] — Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation
- [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] — SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills
- [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] — Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve

## 技术点深读（DEEP）

![[deep/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving.txt`（81350 字符）供引用检索。