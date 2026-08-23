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
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig01.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p02.png]]*
> [!quote] caption
> Mooncake Architecture. remote location will prolong the TTFT, and a large batch size will lead to a larger TBT. Thus, the utilization of both these throughput-oriented optimizations may lead to violations of latency-related SLOs.

> [!tip] 技术解读（多模态）
> ## Description

**Architecture & Data Flow:**
The figure depicts a **KVCache-centric Conductor** system with three coordinated schedulers (left) managing four GPU instances arranged in a 2×2 layout. The top row holds **Prefill Instances** (GPU/VRAM with Local Chunked Prefill Scheduler + Paged KVCache) connected via PP/SP, while the bottom row holds **Decoding Instances** (GPU/VRAM with Paged KVCache + Local Scheduler). A shared middle layer — the **KVCache Pool** (CPU/DRAM/SSD-based Distributed KVCache Pools) — bridges prefill and decoding, with **RDMA-based Inter-node KVCache Transfer** (⊗) enabling cross-node cache movement. Three pools govern flow: **Prefill Pool** (Cache-aware Prefill Scheduler → maximize cache reuse), **KVCache Pool** (Balance Scheduler), and **Decoding Pool** (Load-balance Decoding Scheduler).

**Key Technical Takeaway:**
The system separates stage-specific optimization goals — **Prefill maximizes cache reuse** (subject to TTFT SLO, minimum MFU, KVCache < DRAM), while **Decoding maximizes throughput** (subject to TBT SLO, KVCache < VRAM) — by decoupling scheduling across the prefill/decode boundary through a unified, RDMA-shared distributed KVCache pool.

## Caption (verbatim transcription)

There is no separate numbered figure caption in the image. The in-figure annotations read verbatim:

> **KVCache-centric Conductor**
> 
> Prefill Pool / KVCache Pool / Decoding Pool
> Cache-aware Prefill Scheduler → Prefill Instance → GPU/VRAM (Local Chunked Prefill Scheduler | Paged KVCache) ↕ CPU/DRAM/SSD (Distributed KVCache Pool) ↔ RDMA ⊗ Inter-node KVCache Transfer
> KVCache Balance Scheduler ↔ Decoding Instance → GPU/VRAM (Paged KVCache | Local Scheduler) ↕ CPU/DRAM/SSD (Distributed KVCache Pool)
> Load-balance Decoding Scheduler
> 
> **Prefill Stage Optimization Goal:** max Cache Reuse s.t. TTFT SLO, Minimum MFU, KVCache < DRAM
> 
> **Decoding Stage Optimization Goal:** max Throughput s.t. TBT SLO, KVCache < VRAM

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig02.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p04.png]]*
> [!quote] caption
> Normalized throughput and latency of prefill and decoding stages with different sequence lengths or batch sizes for the dummy LLaMA2-70B model. the computational complexity of attention networks scales quadratically with input length while the complexity of MLP scales linearly, computation time in the prefill stage generally increases superlinearly with input length, as shown in the left part of F

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】Mooncake 解耦式 KVCache 服务架构：prefill（compute-bound，注意力二次复杂度）与 decode（memory-bound，自回归批处理）分到独立节点池。核心是 disaggregated KVCache 层，池化 CPU/DRAM/SSD/RDMA 资源→跨节点 cache 复用、减冗余计算；调度器做 early rejection + SLO 准入(TTFT/TBT)+负载均衡。把计算阶段与 KVCache 存储解耦→弹性扩展、严 SLO 下更高吞吐。架构核心图。

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig03.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p05.png]]*
> [!quote] caption
> The KVCache pool in CPU memory. Each block is attached with a hash value determined by both its own hash and its prefix for deduplication.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The figure illustrates a **prefix-cache-aware KV cache transfer** workflow across distributed LLM serving instances.

**Components & data flow:**
- **Token blocks** (a–i) are hashed cumulatively (A=Hash(a), B=Hash(A+b), …, F=Hash(E+f)) to produce compact identifiers.
- The hashed signatures are compared against an existing **Prefix Cache**; five blocks match (A–E) while the sixth mismatches (F).
- A **Prefill Instance** initially loads/stores the full cache.
- A **Messenger** reads the matched prefix cache and transfers only the **incremental cache blocks** (F–I) to another Messenger.
- The receiving Messenger **writes** the prefix plus incremental blocks, and the **Decoding Instance** loads them — avoiding recomputation.

**Key takeaway:** By hashing chained token blocks for prefix matching, only the divergent suffix (incremental blocks) is shipped over the network, slashing redundant prefill compute and inter-instance bandwidth for shared contexts.

## Caption Transcription

No caption / figure number text is visible in the provided image — only in-figure labels (e.g., "Token Blocks," "Prefix Cache Blocks," "Incremental Cache Blocks," "Unallocated Cache Blocks," and the action arrows "Load/Store/Read/Write/Transfer KVCache") are present.

### Figure 4 (p.6) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig04.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]]*
> [!quote] caption
> Workflow of inference instances. ( ) For prefill instances, the load and store operations of the KVCache layer are performed layer-by-layer and in parallel with the prefill computation to mitigate transmission overhead (see §5.2). (y ) For decoding instances, asynchronous loading is performed concurrently with GPU decoding to prevent GPU idle time. 4) Decoding: After all the KVCache is received i

> [!tip] 技术解读（多模态）
> ## Figure Description

The diagram illustrates a **disaggregated LLM inference architecture** with two instances:

**Prefill Instance (left, blue):**
- **CPU side:** holds *Prefix KVCache* and *Incremental KVCache* in host memory
- **GPU side:** mirrors both caches in device memory
- *Layer-wise Load and Store* moves tensors between CPU↔GPU
- (s1) Reuses prefix cache; (s2) runs incremental prefill on the GPU; (s3) transfers the full/updated KVCache to the decoder

**Decoding Instance (right, orange):**
- Receives the transferred cache via *Async Load* (CPU→GPU)
- (s4) Performs token decoding on the GPU using the assembled **Full KVCache**

**Key takeaway:** Splitting prefill and decoding, combined with *layer-wise pipelined* CPU↔GPU cache movement and *asynchronous* transfer, overlaps data movement with compute, maximizing hardware utilization and throughput.

## Caption Transcription (verbatim, as shown in figure)

*(No standalone caption text is present; the in-figure labels read as follows)*

- "**Prefill Instance**" / "**Decoding Instance**"
- "GPU", "CPU"
- "Prefix KVCache", "Incremental KVCache", "Full KVCache"
- "(s1) KVCache Reuse", "s2: Incremental Prefill", "s3: KVCache Transfer", "s4: Decoding"
- "Layer-wise Load and Store*", "Async Load†"

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig05.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]]*
> [!quote] caption
> Input and output length distributions in the request trace. 4

> [!tip] 技术解读（多模态）
> **Figure description (≤120 words):**

The figure consists of two side-by-side log-scale histograms characterizing sequence length distributions in a dataset.

- **Left panel (blue):** *Input Length* on the x-axis (~0 to 120,000 tokens) versus *Frequency* on a log y-axis (~10⁰ to 10⁴). The distribution is heavily right-skewed, peaking near 5,000–10,000 tokens (~10⁴ samples) and decaying roughly monotonically across three orders of magnitude, with a sparse long tail extending to ~125,000.
- **Right panel (green):** *Output Length* on the x-axis (~0 to 2,000 tokens) versus *Frequency* on a log y-axis (~10⁰ to 10⁴). It shows a bimodal pattern: a large spike at very short outputs (~1,000 tokens, ~1.5×10⁴ samples), a broad mode centered around 400–500 tokens (~10³), and an outlier spike near 2,000 tokens.

**Key technical takeaway:** Inputs are ~10–50× longer than outputs, and output length is effectively bounded near 2,048 — suggesting a context-window truncation at the maximum generation length.

**Caption (verbatim):** No caption text is rendered in the image; only axis labels ("Input Length", "Output Length", "Frequency") and tick values are present.

### Figure 6 (p.7) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig06.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p07.png]]*
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
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig07.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p09.png]]*
> [!quote] caption
> Latency of storing KVCache of different request lengths (Layer-wise latency refers to the difference in latency between Layer-wise Prefill and Prefill without storing KVCache).

> [!tip] 技术解读（多模态）
> **Figure 7 — Description (≤120 words):**

The figure is a grouped bar chart comparing two KVCache-storing strategies across five input lengths. The **x-axis** lists Sequence Lengths (8k, 16k, 32k, 64k, 128k); the **y-axis** is Latency (seconds, 0 – ~0.85). Two series are plotted per length: **Serialized** (blue) and **Layer-wise** (orange). Data flow: each request's prefill executes layer-by-layer, with the KVCache for layer *i* stored asynchronously while layer *i+1* computes — overlapping memory writes with attention. The blue bars grow steeply (~0.10 s → ~0.85 s) while the orange bars stay nearly flat (~0.10 s) at all lengths.

**Key takeaway:** Overlapping KVCache storage with the next layer's attention keeps prefill latency roughly constant regardless of sequence length, eliminating VRAM-induced TTFT growth.

**Caption (verbatim):**
Figure 7: Latency of storing KVCache of different request lengths (Layer-wise latency refers to the difference in latency between Layer-wise Prefill and Prefill without storing KVCache).

### Figure 8 (p.11) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig08.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p11.png]]*
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
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig09.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p13.png]]*
> [!quote] caption
> The load of prefill and decoding instances over 20 minutes, before using the prediction- based early rejection.

> [!tip] 技术解读（多模态）
> **Figure Description & Key Takeaway:**

Figure 9 is a time-series line chart spanning a 20-minute window (x-axis: 0:00 → 20:00) with load percentage on the y-axis (0–100%). Two curves are plotted: a **green line** representing the load on **prefill instances** and a **yellow line** representing the load on **decoding instances**. Both oscillate roughly between 10% and 95%, exhibiting pronounced anti-phase behavior—when one peaks, the other tends to dip, and vice versa.

**Key takeaway:** The chart empirically demonstrates the load-coupling instability introduced by naive early rejection: scheduling decisions lag behind actual decoding load, causing phase-staggered oscillation between prefill and decoding pools and resulting in poor cluster utilization. This motivates the prediction-based early rejection framework introduced in §7.4.

**Caption (verbatim):**

Figure 9: The load of prefill and decoding instances over 20 minutes, before using the prediction-based early rejection.

### Figure 10 (p.14) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig10.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p14.png]]*
> [!quote] caption
> Instance load when applying Early Rejection and Early Rejection Based on Prediction. conditions where resources are scarce and accurate predictions are necessary, making request-level predictions particularly difficult.

> [!tip] 技术解读（多模态）
> ## Figure Description

The figure illustrates a four-stage scheduling/load-balancing process along a time axis, organized into two stacked rows tracking system loads.

**Components & Layout:**
- **Top row (Decoding Load):** Orange horizontal bars whose *width = request length* and *height = utilization* (0–1). A yellow dashed threshold line and a smooth yellow curve track utilization over time.
- **Bottom row (Prefill Load):** Light-blue bars represent prefill requests; darker blue bars represent *newly added* prefill requests. A green dashed threshold and green curve track prefill utilization.
- **Connectors:** Black arrows flow horizontally across each row (load evolution between stages); red arrows point vertically from decoding to prefill rows (cross-stage influence).
- **Decisions:** Pink stars = "Accept," purple stars = "Reject."

**Data Flow:** Stage 1 (low decode, high prefill → Accept) → Stage 2 (decode surges, prefill drops → Reject) → Stage 3 (decode drops, prefill rises → Accept) → Stage 4 (decode moderate, prefill low → Reject).

**Key Technical Takeaway:** Accept/reject decisions are jointly driven by **both** decoding and prefill utilization thresholds; the scheduler must account for **cross-stage coupling** (vertical red arrows) where decoding load from a prior stage suppresses prefill acceptance in the next stage, preventing resource overcommitment.

## Caption (Verbatim Transcription)

> "Length [bracket]; Utilization [bracket] — Legend: Prefill Request | Prefill Request (New Added) | Decoding Request — Y-axes: Decoding Load, Prefill Load — X-axis: Stage 1, Stage 2, Stage 3, Stage 4 — Time — Outcomes: Accept, Reject"

### Figure 11 (p.16) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig11.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]]*
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

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.8) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-tab01.png]]
> [!quote] caption
> Cache hit rates under different cache policies and capacities.

> [!tip] 表格解读（多模态）
> **Description of the Main Figure (Table 1):**

**Architecture/Components/Data Flow:** Table 1 presents a comparative evaluation matrix of cache hit rate performance across two dimensions:
- **Rows (Cache Policies):** Three eviction strategies — LRUCache (Least Recently Used), LFUCache (Least Frequently Used), and LengthAwareCache (length-aware eviction).
- **Columns (Block Capacity):** A descending capacity gradient from Inf (unbounded) → 100000 → 50000 → 30000 → 10000 → 1000, simulating cache pressure scenarios.

**Key Technical Takeaway:** All three policies yield near-identical hit rates (~0.51) at unbounded capacity, but diverge under tight capacity (1000 blocks), where LRUCache outperforms LFUCache and LengthAwareCache (0.30 vs. 0.30, with intermediate advantages at 10000 blocks: 0.40 vs. 0.35). This indicates eviction strategy becomes critical only under memory pressure, with recency-based heuristics holding a slight edge at extreme constraints.

**Caption (verbatim):** "Table 1: Cache hit rates under different cache policies and capacities."

### Table 2 (p.15) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-tab02.png]]
> [!quote] caption
> Datasets used in the end-to-end experiment.

> [!tip] 表格解读（多模态）
> **Description:**
This table (Table 2) is a comparison matrix summarizing four datasets used in an end-to-end experiment for LLM inference/serving. Its **components** are the dataset names plus four evaluation dimensions: Avg Input Length, Avg Output Length, Cache Ratio, and Arrival Pattern. The **data flow** is implicitly a workload characterization—each row profiles a distinct request distribution, ranging from short-output summarization (ArXiv, L-Eval) to synthetic multi-length sweeps (Simulated Data) and timestamp-driven production traces (Real Data).

**Key technical takeaway:** The benchmark deliberately spans divergent regimes—input lengths from ~8K to 128K tokens, cache hit-ratios from ~0% to >80%, and both stochastic (Poisson) and bursty (timestamp-based) arrivals—to stress-test the system across compute-, memory-, and I/O-bound regimes within a single evaluation harness.

**Caption (verbatim):**
Table 2: Datasets used in the end-to-end experiment.

### Table 3 (p.17) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-tab03.png]]
> [!quote] caption
> Number of requests rejected by the system under the overloaded-scenario experiment.

> [!tip] 表格解读（多模态）
> ## Figure Description

**Architecture/Components:** The figure is a comparative data table (Table 3) presenting experimental results across three request-handling strategies evaluated under an overloaded-scenario workload. The columns represent distinct system configurations: a **Baseline** (no early-rejection mechanism), an **Early Rejection** policy (rules-based admission control), and an **Early Rejection based on Prediction** (ML/forecasting-driven admission control). The single metric row quantifies the absolute count of requests rejected by each approach.

**Data Flow:** Workload → system admission controller (variant-specific) → rejection counter → tabular aggregation.

**Key Technical Takeaway:** Predictive early rejection achieves the lowest rejection count (3589 vs. Baseline's 4183, ~14% reduction) while outperforming naive early rejection (3771), demonstrating that forecasting-driven admission control is more selective than rule-based gating.

## Caption (Verbatim)

> **Table 3:** Number of requests rejected by the system under the overloaded-scenario experiment.

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