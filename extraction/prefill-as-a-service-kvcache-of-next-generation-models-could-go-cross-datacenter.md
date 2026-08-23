---
paper_num: "58"
title: "Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter"
authors: "Models Could Go Cross-Datacenter Ruoyu Qin1,2 Weiran He1 Yaoyu Wang1 Zheming Li1 Xinran Xu1 Yongwei Wu2 Weimin Zheng2 Mingxing Zhang2∗ 1Moonshot AI 2Tsinghua University"
date: "2026/4/16"
arxiv: "https://arxiv.org/abs/2604.15039"
pdf: "papers/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter.pdf"
slug: "prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter"
tags: [kv-cache]
---

# Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter

> [!abstract] 摘要（原文）
> Prefill-decode (PD) disaggregation has become the standard architecture for large-scale LLM serving, but in practice its deployment boundary is still determined by KVCache transfer. In conventional dense-attention models, prefill generates huge KVCache traffics that keep prefill and decode tightly coupled within a single high-bandwidth network domain, limiting heterogeneous deployment and resource elasticity. Recent hybrid-attention architectures substantially reduce KVCache size, making cross-cluster KVCache transport increasingly plausible. However, smaller KVCache alone does not make heterogeneous cross-datacenter PD serving practical: real workloads remain bursty, request lengths are highly skewed, prefix caches are unevenly distributed, and inter-cluster bandwidth fluctuates. A naive design that fully externalizes prefill can therefore still suffer from congestion, unstable queueing, and poor utilization. We present Prefill-as-a-Service (PrfaaS), a cross-datacenter serving architecture that selectively offloads long-context prefill to standalone, compute-dense prefill clusters and transfers the resulting KVCache over commodity Ethernet to local PD clusters for decode. Rather than treating reduced KVCache as sufficient, PrfaaS combines model-side KV efficiency with system-side selective offloading, bandwidth-aware scheduling, and cache-aware request placement. This design removes the requirement that heterogeneous accelerators share the same low-latency RDMA fabric, enabling independent scaling of prefill and decode capacity across loosely coupled clusters. In a case study using an internal 1T-parameter hybrid model, a PrfaaS-augmented heterogeneous deployment achieves 54% higher serving throughput and 64% lower P90 TTFT than a homogeneous PD baseline, with approximately 15% throughput gain at equal cost, while consuming only modest cross-datacenter bandwidth.

## 元信息
- **发表日期**: 2026/4/16
- **作者**: Models Could Go Cross-Datacenter Ruoyu Qin1,2 Weiran He1 Yaoyu Wang1 Zheming Li1 Xinran Xu1 Yongwei Wu2 Weimin Zheng2 Mingxing Zhang2∗ 1Moonshot AI 2Tsinghua University
- **arXiv**: https://arxiv.org/abs/2604.15039
- **本地 PDF**: `papers/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter.pdf`
- **页数**: 16

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig01.png]]
*整页渲染: ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p02.png]]*
> [!quote] caption
> Comparison of two deployment paradigms for PD-disaggregated LLM serving.

> [!tip] 技术解读（多模态）
> **Figure 1 Description**

The figure contrasts two PD-disaggregated LLM serving architectures:

**(a) Status quo** — a Single Homogeneous Cluster containing co-located Prefill and Decode phases, each backed by local KV Stores. Tightly-coupled KV transfer over an **RDMA-based Single-Cluster KV Store** keeps phases within one high-bandwidth fabric.

**(b) PrfaaS** — splits phases across two clusters (PrfaaS Cluster with Prefill-specific GPUs; Local PD Cluster with Decode GPUs), connected by a Cross-Datacenter KVCache Transfer Layer over **Ethernet**. The middle annotation distinguishes Dense (network-bound ❌) vs. Hybrid (prefill-bound ✔) loosely-coupled KV transfer.

**Key Takeaway:** PrfaaS offloads only long-uncached prefills to a dedicated compute-rich cluster, transferring KVCache over commodity Ethernet to local PD clusters — enabling heterogeneous, cross-datacenter disaggregation without requiring a unified RDMA fabric.

**Caption (verbatim):** Figure 1: Comparison of two deployment paradigms for PD-disaggregated LLM serving.

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig02.png]]
*整页渲染: ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p04.png]]*
> [!quote] caption
> KV throughput of MiniMax-M2.5 on an 8×H200 instance at various input lengths.

> [!tip] 技术解读（多模态）
> **Description of Figure 2 (≤120 words):**

The figure is a dual-axis bar+line chart plotting MiniMax-M2.5's behavior across prompt lengths (1K → 128K tokens).

- **X-axis:** Prompt Length (log scale: 1K, 2K, 4K, 8K, 16K, 32K, 64K, 128K).
- **Left Y-axis (blue bars):** KV Throughput in Gbps — grows roughly from ~5 Gbps (1K) up to ~62 Gbps (64K), then *drops* to ~48 Gbps at 128K.
- **Right Y-axis (red line):** Prefill Latency in seconds — stays near 0 through 8K, rises to ~2 s at 32K, and explodes to ~5.5 s at 128K.

**Key takeaway:** KV-cache transport demand scales with context length, but throughput saturates/degrades at very long contexts while prefill latency balloons — the "bandwidth bottleneck" that couples prefill and decode into a single tightly-integrated cluster.

**Caption (verbatim):**

> Figure 2: KV throughput of MiniMax-M2.5 on an 8×H200 instance at various input lengths.

### Figure 3 (p.6) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig03.png]]
*整页渲染: ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p06.png]]*
> [!quote] caption
> Deployment topology of the PrfaaS-PD architecture.

> [!tip] 技术解读（多模态）
> PrfaaS-PD 部署拓扑：Request Router 按长度阈值 t 分流——长请求 (l>t) 送独立 PrfaaS 集群（高算力 prefill 节点+集群内 RDMA），短请求留本地 PD 集群（高显存带宽）。PrfaaS 产出的 KVCache 经普通跨集群以太网传到本地 PD 集群 decode；两侧各挂 Hybrid Prefix Cache Pool（linear state 与 full-attention KV 分组、统一 block pool），Global KVCache Manager 全局协调。核心洞察：hybrid-attention 模型 KV 流量降一个数量级后（1T 模型 ~170Gbps、万卡总出口 ~1.8Tbps），跨数据中心 prefill 卸载在物理链路上首次可行。

### Figure 4 (p.7) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig04.png]]
*整页渲染: ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p07.png]]*
> [!quote] caption
> Hybrid prefix cache pool. Linear states and full-attention KVCache are managed by separate groups backed by a unified block pool. Blocks are categorized as prefix-cache (intra-cluster only, block-aligned) or transfer-cache (cross-cluster, discarded after transfer). categories. Local PD clusters perform PD-disaggregated serving and can complete inference for a request end to end. PrfaaS clusters pr

> [!tip] 技术解读（多模态）
> **Figure Description (≤120 words):**

The diagram depicts a **hybrid prefix cache pool** architecture with two source groups feeding into a single shared pool. The **Linear Attention Group** (top-left) manages request-level recurrent states across Groups 0, 1, 2, while the **Full Attention Group** (top-right) manages block-level KVCaches (Group 3). Arrows labeled "Allocate/Free" show both groups drawing/releasing blocks from the **Unified Hybrid Cache Pool** (bottom). The pool is partitioned into three block types: **Prefix-Cache Blocks** (purple, reusable, aligned block size), **Transfer-Cache Blocks** (pink, cross-cluster, any length), and **Free Blocks** (gray).

**Key Technical Takeaway:** A single shared block pool unifies heterogeneous KV storage—reusable aligned prefix blocks for intra-cluster serving versus flexible transfer blocks for cross-cluster PD-disaggregated prefill transfer.

**Caption (verbatim):**

Figure 4: Hybrid prefix cache pool. Linear states and full-attention KVCache are managed by separate groups backed by a unified block pool. Blocks are categorized as prefix-cache (intra-cluster only, block-aligned) or transfer-cache (cross-cluster, discarded after transfer).

### Figure 5 (p.11) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig05.png]]
*整页渲染: ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p11.png]]*
> [!quote] caption
> Illustration of the grid search process for the two optimization variables. (a) fixes t at the optimum and searches over the prefill/decode instance split within the local PD cluster. (b) fixes

> [!tip] 技术解读（多模态）
> **Description**

Figure 5 is a two-panel grid-search visualization for a two-variable optimization problem.

- **Panel (a) — Prefill/Decode allocation:** X-axis shows N_p (prefill instances, 1–7, bottom) and N_d (decode instances, 1–7, top). Y-axis is throughput Λ_max (req/s). A red "Prefill bound" curve (monotonically rising, then falling) and a green "Decode bound" curve intersect at a marked star: Λ_max = 3.24 at N_p = 3, N_d = 5.
- **Panel (b) — Routing threshold:** X-axis is threshold t in tokens (0K–60K); Y-axis is Λ_max (req/s). A red "PrfaaS bound" (rising then leveling near 20K) intersects a decaying blue "PD-Prefill bound" curve at a star: Λ_max = 3.24, t = 19.4K.
- **Data flow:** Profiling data → PrfaaS-PD throughput model → 2-D grid search over (N_p, N_d, t) → optimal operating point.

**Key takeaway:** System throughput peaks at the *intersection* of prefill and decode bounds, and overall Λ_max is set by the minimum of PrfaaS-bound and PD-bound curves — decoupling cluster sizing from routing policy.

**Caption (verbatim):**
"Figure 5: Illustration of the grid search process for the two optimization variables. (a) fixes t at the optimum and searches over the prefill/decode instance split within the local PD cluster. (b) fixes N_p = 3, N_d = 5 and searches over t."

## 表格（裁剪图 + caption，可直接插入报告）

### Table 3 (p.4) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-tab03.png]]
> [!quote] caption
> KV throughput Φ kv (Gbps) at various input lengths. All models are benchmarked on 8 × H200 with SGLang v0.5.9 [7].

> [!tip] 表格解读（多模态）
> **Figure Description (Table 3):**

The table presents KV cache throughput (Φ_kv, in Gbps) measured across two model architecture families — **Hybrid** (Kimi Linear, MiMo-V2-Flash, Qwen3.5-397B, Ring-2.5-1T) and **Dense** (MiniMax-M2.5, Qwen3-235B) — at four input sequence lengths (1K, 8K, 32K, 128K). Each row reports the throughput a single model instance produces when generating KV Cache during prefill, providing a side-by-side comparison of how architectural sparsity affects network demand. Dense attention models exhibit throughput that grows steeply with context length (e.g., MiniMax-M2.5: 4.94 → 59.93 Gbps from 1K to 32K), whereas hybrid architectures remain compressed across the same range.

**Key Technical Takeaway (98 words):**
Dense transformers generate KV cache at rates that far exceed cross-datacenter Ethernet capacity — MiniMax-M2.5 reaches ~60 Gbps at 32K context, roughly 30× higher than hybrid counterparts. This single-instance egress bandwidth is the dominant systems constraint binding conventional PD disaggregation to tightly integrated network domains. Hybrid/linear-attention architectures alleviate this bottleneck by compressing transport demand, making disaggregated prefill–decode serving across looser interconnects operationally feasible and enabling heterogeneous hardware scaling without bespoke networking.

**Caption (verbatim):**
Table 3: KV throughput Φ_kv (Gbps) at various input lengths. All models are benchmarked on 8×H200 with SGLang v0.5.9 [7].

### Table 4 (p.8) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-tab04.png]]
> [!quote] caption
> Notation used in the PrfaaS-PD throughput model. Traffic System

> [!tip] 表格解读（多模态）
> ## Description

**Architecture/Components/Data Flow:** The table defines the notation for a **PrfaaS-PD throughput model** that splits incoming requests by length. On the **Traffic** side, requests of random input length $L$ arrive at rate $\Lambda$ and are partitioned by a routing threshold $t$: long requests ($L > t$, mean $l_{\text{long}}$) are sent to **PrfaaS** (prefill-only) with probability $p$, while short requests go to **PD-P** (prefill-and-decode, mean $l_{\text{short}}$). The **System** side models PrfaaS egress bandwidth $B_{\text{out}}$, KVCache size $S_{\text{kv}}(l)$, batch limits $BS_{\max}$, and per-step decode time $T_{\text{decode}}$, producing throughputs $\Theta_{\text{prfaas}}$, $\Theta_{\text{pd-p}}$, and $\Theta_{\text{pd-d}}$.

**Key Technical Takeaway:** A single routing threshold $t$ balances uncached-token prefill cost against decode-side reuse, decoupling long-input prefill from variable-length generation to maximize aggregate throughput.

## Caption (verbatim)

**Table 4:** Notation used in the PrfaaS-PD throughput model.

### Table 5 (p.11) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-tab05.png]]
> [!quote] caption
> KVCache size S kv , prefill latency T prefill , and KV throughput Φ kv of the internal 1T hybrid model at various input lengths. Prefill latency is benchmarked on 8 × H200 with in-house vLLM [ 28 ].

> [!tip] 表格解读（多模态）
> **Description of the main figure:**

The figure presents a two-stage hyperparameter search for a Prefill/Decode disaggregated LLM serving system. **(a)** Sweeps instance allocation N_p (prefill, bottom axis) and N_d (decode, top axis, complementary). The achievable throughput is bounded below by the Prefill-bound (red, increasing in N_p) and the Decode-bound (green, decreasing in N_p); the intersection pins the optimum at **Λ_max=3.24 req/s** at N_p=3, N_d=5 (★). **(b)** Sweeps the routing threshold t (tokens) that decides whether a request is handled by PrfaaS vs. PD-Prefill. The PrfaaS bound (red) rises then crosses the PD-Prefill bound (blue) at **t=19.4K**, again yielding Λ_max=3.24. **Key takeaway:** the two optimization dimensions (instance split, routing threshold) are coupled, each converging on the same optimum throughput of 3.24 req/s, indicating a global sweet-spot for the hybrid serving configuration.

**Caption verbatim:**

Table 5: KVCache size 𝒮_kv, prefill latency 𝒯_prefill, and KV throughput Φ_kv of the internal 1T hybrid model at various input lengths. Prefill latency is benchmarked on 8×H200 with in-house vLLM [28].
Seq Len | KVCache Size | Prefill Latency | KV Throughput
1K | 190.8 MiB | 0.44 s | 3.61 Gbps
8K | 308.9 MiB | 0.72 s | 3.59 Gbps
32K | 701.3 MiB | 1.84 s | 3.19 Gbps
128K | 2316.3 MiB | 7.40 s | 2.62 Gbps

(a) Search over prefill/decode allocation. (b) Search over routing threshold t.

### Table 6 (p.12) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-tab06.png]]
> [!quote] caption
> Comparison of optimal configurations across PrfaaS-PD, homogeneous PD, and naive heterogeneous PD deployments.

> [!tip] 表格解读（多模态）
> **Note:** No figure is provided in the prompt — the content is a comparison **table**, so I will describe it as such.

---

**Description (Table 6):**
The table benchmarks three deployment strategies — **PrfaaS-PD**, **Homogeneous PD**, and **Naive Heterogeneous PD** — across six rows of configuration and performance metrics. Columns compare: (1) the inference threshold *t* (only defined for PrfaaS-PD at 19.4K), (2) instance-pool counts *N_prfaas / N_p / N_d*, (3) **Time-To-First-Token** latency (mean / P90 in seconds), (4) per-stage service rates **Θ** (req/s) for prefilling, prefill-decoder, and decoder stages, (5) peak sustainable arrival rate **Λ_max**, and (6) a normalized throughput **Ratio**. PrfaaS-PD configures 4/3/5 instances across three role groups, achieving the highest Λ_max (3.24 req/s) and best P90 TTFT (3.51 s) — matching the naive heterogeneous deployment's tail latency while substantially exceeding homogeneous PD (9.73 s).

**Key takeaway (≤120 words):**
PrfaaS-PD delivers **1.54× higher peak throughput** (3.24 req/s vs. 2.11 req/s) over homogeneous PD while cutting P90 TTFT by ~64% (3.51 s vs. 9.73 s). Crucially, it outperforms the **naive heterogeneous** alternative (1.16×, 2.45 req/s), demonstrating that combining a *threshold-gated PrfaaS router* with three differentiated role pools (N_prfaas = 4, N_p = 3, N_d = 5) — rather than merely splitting prefix/decoder capacity — is what unlocks the latency–throughput Pareto improvement. The dash-marked cells indicate that strict prefix–decoder and pure-PrfaaS tiers do not exist in the homogeneous and naive setups, respectively.

---

**Verbatim caption (transcribed):**

> **Table 6:** Comparison of optimal configurations across PrfaaS-PD, homogeneous PD, and naive heterogeneous PD deployments.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\Phi_{\text{kv}}(l)=\frac{S_{\text{kv}}(l)}{T_{\text{prefill}}(l)},
$$

$$
B_{\text{out}} =\frac{N}{P}\cdot\frac{\mathbb{E}[S_{\text{kv}}]}{\mathbb{E}[T_{\text{prefill}}]} \approx\frac{N}{P}\cdot\Phi_{\text{kv}}(L_{\text{avg}}),
$$

$$
\Theta_{\text{\systemnamelowercase}} = \min\!\left(\frac{N_{\text{\systemnamelowercase}}}{T_{\text{prefill}}(l_{\text{long}})},\; \frac{B_{\text{out}}}{S_{\text{kv}}(l_{\text{long}})}\right).
$$

$$
\Theta_{\text{pd-p}} = \frac{N_p}{T_{\text{prefill}}(l_{\text{short}})}.
$$

$$
\Theta_{\text{pd-d}} = \frac{N_d \cdot \mathit{BS}_{\max}}{T_{\text{decode}} \cdot L_{\text{out}}},
$$

$$
\Lambda_{\max} = \min\!\left(\frac{\Theta_{\text{\systemnamelowercase}}}{p},\; \frac{\Theta_{\text{pd-p}}}{1 - p},\; \Theta_{\text{pd-d}}\right).
$$

$$
\frac{\Theta_{\text{\systemnamelowercase}}}{p} = \frac{\Theta_{\text{pd-p}}}{1 - p}.
$$

$$
\Theta_{\text{\systemnamelowercase}} + \Theta_{\text{pd-p}} = \Theta_{\text{pd-d}}.
$$

## 相关论文

- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] — IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse
- [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] — A Survey on Large Language Model Acceleration based on KV Cache Management
- [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] — KV Cache Optimization Strategies for Scalable and Efficient LLM Inference
- [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] — CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion

## 技术点深读（DEEP）

![[deep/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter.txt`（58766 字符）供引用检索。