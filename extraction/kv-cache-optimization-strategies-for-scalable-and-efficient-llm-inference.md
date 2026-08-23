---
paper_num: "62"
title: "KV Cache Optimization Strategies for Scalable and Efficient LLM Inference"
authors: ""
date: "2026/3/20"
arxiv: "https://arxiv.org/abs/2603.20397"
pdf: "papers/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference.pdf"
slug: "kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference"
tags: [kv-cache]
---

# KV Cache Optimization Strategies for Scalable and Efficient LLM Inference

> [!abstract] 摘要（原文）
> The key-value (KV) cache is a foundational optimization in Transformer-based large language models (LLMs), eliminating redundant recomputation of past token representations during autoregressive generation. However, its memory footprint scales linearly with context length, imposing critical bottlenecks on GPU memory capacity, memory bandwidth, and inference throughput as production LLMs push context windows from thousands to millions of tokens. Efficient KV cache management has thus become a first-order challenge for scalable LLM deployment. This paper provides a systematic review of recent KV cache optimization techniques, organizing them into five principal directions: cache eviction, cache compression, hybrid memory solutions, novel attention mechanisms, and combination strategies. For each category we analyze the underlying mechanisms, deployment trade-offs, and empirical performance across memory reduction, throughput, and model accuracy metrics. We further map techniques to seven practical deployment scenarios, including long-context single requests, high-throughput datacenter serving, edge devices, multi-turn conversations, and accuracy-critical reasoning, providing actionable guidance for practitioners selecting among competing approaches. Our analysis reveals that no single technique dominates across all settings; instead, the optimal strategy depends on context length, hardware constraints, and workload characteristics, pointing toward adaptive, multi-stage optimization pipelines as a promising direction for future research.

## 元信息
- **发表日期**: 2026/3/20
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2603.20397
- **本地 PDF**: `papers/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference.pdf`
- **页数**: 24

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig01.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p02.png]]*
> [!quote] caption
> Autoregressive generation, at each step the new token (orange) attends to all prior tokens (cyan). Without caching, keys and values for every past token would be recomputed from scratch at each step. The KV cache avoids this by storing and reusing them.

> [!tip] 技术解读（多模态）
> ## Figure Description

The figure illustrates **autoregressive token generation** across two decoding steps. In Step 1, three context tokens ("The", "apple", "tastes") feed into a query position (orange "?"), which attends to all prior tokens (cyan) and predicts "sweet". In Step 2, the sequence extends to four tokens and predicts the next character ("."). Arrows from every prior token converge on the current query position, depicting full causal self-attention. A callout box highlights the **KV Cache**, which stores key/value vectors for previously processed tokens so they are not recomputed at each step.

**Key takeaway:** The KV cache eliminates redundant projection recomputation across decoding steps, reducing per-step cost from O(n²) to O(n) per new token, at the expense of memory that grows linearly with context length.

## Caption (verbatim)

> Figure 1: Autoregressive generation, at each step the new token (orange) attends to all prior tokens (cyan). Without caching, keys and values for every past token would be recomputed from scratch at each step. The KV cache avoids this by storing and reusing them.

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig02.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p03.png]]*
> [!quote] caption
> Data-flow of the KV cache within a single transformer layer. Input token xt fans into three projections; Kt and Vt are appended to their respective caches (teal); Qt attends over the full caches to produce output ot. Cache size grows as O(T) per head per layer.

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 2)

**Architecture / Data Flow:** Inside a single transformer layer, the current input token x_t is linearly projected through three learned matrices (W_K, W_Q, W_V) into a key K_t, query Q_t, and value V_t. K_t and V_t are *appended* to their growing per-layer caches K_c = [K_1, …, K_t] and V_c = [V_1, …, V_t] (each of size t × d_k and t × d_v per head), while Q_t is used ephemerally. Output is computed via scaled dot-product attention over the full accumulated caches:

$$o_t = \text{softmax}\!\left(\tfrac{Q_t \mathbf{K}_c^{\top}}{\sqrt{d_k}}\right)\mathbf{V}_c.$$

**Key takeaway:** The KV cache grows *linearly* in sequence length (O(T) per head per layer), which is the fundamental memory bottleneck for long-context LLM inference and the motivation for all subsequent cache-optimization techniques.

## Caption (verbatim)

**Figure 2:** Data-flow of the KV cache within a single transformer layer. Input token x_t fans into three projections; K_t and V_t are appended to their respective caches (teal); Q_t attends over the full caches to produce output o_t. Cache size grows as O(T) per head per layer.

### Figure 3 (p.3) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig03.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p03.png]]*
> [!quote] caption
> KV cache memory as a function of context length for three LLaMA-2 model variants under fp16 precision.

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 2)

**Architecture / Data Flow:** Inside a single transformer layer, the current input token x_t is linearly projected through three learned matrices (W_K, W_Q, W_V) into a key K_t, query Q_t, and value V_t. K_t and V_t are *appended* to their growing per-layer caches K_c = [K_1, …, K_t] and V_c = [V_1, …, V_t] (each of size t × d_k and t × d_v per head), while Q_t is used ephemerally. Output is computed via scaled dot-product attention over the full accumulated caches:

$$o_t = \text{softmax}\!\left(\tfrac{Q_t \mathbf{K}_c^{\top}}{\sqrt{d_k}}\right)\mathbf{V}_c.$$

**Key takeaway:** The KV cache grows *linearly* in sequence length (O(T) per head per layer), which is the fundamental memory bottleneck for long-context LLM inference and the motivation for all subsequent cache-optimization techniques.

## Caption (verbatim)

**Figure 2:** Data-flow of the KV cache within a single transformer layer. Input token x_t fans into three projections; K_t and V_t are appended to their respective caches (teal); Q_t attends over the full caches to produce output o_t. Cache size grows as O(T) per head per layer.

### Figure 4 (p.4) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig04.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p04.png]]*
> [!quote] caption
> Causal self-attention weight matrix for “The apple tastes sweet.” visualised with the Viridis colormap (dark purple = low, yellow = high). Gray cells are causally masked future tokens. Each row sums to 1 (post-softmax).

> [!tip] 技术解读（多模态）
> **Figure description**

The figure is a 4×4 causal self-attention weight matrix for the sentence "The apple tastes sweet." Rows correspond to Queries (Q): "The", "apple", "tastes", "sweet"; columns correspond to Keys (K) with the same tokens. Cell values are post-softmax attention weights (each row sums to 1). The upper-triangular cells are grayed out, indicating causal masking that forbids attending to future tokens. Colors follow the Viridis colormap — dark purple for low weight, yellow for high. The bottom row ("sweet" query) is outlined in orange to highlight that it concentrates 65% of its attention on "apple" (0.65), while "The" receives only 0.05. An annotation calls out that low-weight KV pairs become eviction candidates.

**Key takeaway (≤120 words):** Attention distributions are highly skewed — a single token ("apple") absorbs 0.65 of "sweet"'s attention mass — so KV entries contribute very non-uniformly to inference. This non-uniformity is the empirical justification for *attention-score-driven eviction* methods (e.g., H₂O, SnapKV), which discard low-weight KV pairs to shrink memory and accelerate decoding without retraining.

**Verbatim caption:**

Figure 4: Causal self-attention weight matrix for "The apple tastes sweet." visualised with the Viridis colormap (dark purple = low, yellow = high). Gray cells are causally masked future tokens. Each row sums to 1 (post-softmax). Query "sweet" concentrates 65% of its attention on "apple", demonstrating that KV entries carry highly non-uniform importance, the core premise of attention-score-driven eviction methods such as H₂O and SnapKV.

### Figure 5 (p.5) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig05.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p05.png]]*
> [!quote] caption
> Taxonomy of KV cache optimization techniques surveyed in this paper, organized into five major categories.

> [!tip] 技术解读（多模态）
> ## Description of Main Figure

**Architecture/Components:** The figure is a hierarchical taxonomy diagram with a single root node "KV Cache Optimization" branching into five parallel categories, each accompanied by representative methods:

1. **Cache Eviction** — H₂O, SnapKV, NACL, Ada-KV
2. **Cache Compression** — KIVI, PALU, MiniCache, KVQuant
3. **Hybrid Memory** — PagedAttention, InfiniGen, LayerKV
4. **New Attention Mechanism** — Linear, Log-Linear, KIMI Linear
5. **Combination Methods** — FlexGen, ShadowKV, TailorKV

**Key Technical Takeaway:** KV cache optimization is best understood as a five-pronged design space — each category attacks a distinct bottleneck (memory footprint, decoding latency, TTFT, throughput, or attention complexity), so practitioners select methods based on their target workload rather than seeking a universal solution.

## Caption (Verbatim)

**Figure 5:** Taxonomy of KV cache optimization techniques surveyed in this paper, organized into five major categories.

### Figure 6 (p.6) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig06.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p06.png]]*
> [!quote] caption
> Upper plots illustrate symbolic plots of an attention map deploying different KV cache policies in LLM generation. Lower right: contrasts their accuracy-memory trade-off. Left: the overview of H2O framework [1]. A key challenge in eviction-based methods is identifying which tokens carry long-range importance. One approach tracks accumulated attention scores and treats high-scoring tokens as essent

> [!tip] 技术解读（多模态）
> **Description of Figure 6:**

The figure combines three components to illustrate KV cache optimization strategies:

1. **Top row** — Four symbolic attention-map matrices comparing sparsity patterns: *Dynamic Sparsity*, *Static Sparsity (Strided)*, *Static Sparsity (Local)*, and *Static Sparsity w. H₂O*. Each grid shows which token positions are retained (blue) versus evicted (gray); H₂O retains a hybrid pattern mixing heavy-hitter columns with local bands.

2. **Bottom-left** — H₂O framework diagram: token sequence ("Children laughed and played in the sunny park...") with Key/Value caches scored as 0.2, 0.1, 0.1, 0.6. A Query vector computes accumulated attention scores (1, 1.4, 1.5, ✗, 0.6), discarding the lowest-scoring token to keep the cache budget fixed.

3. **Bottom-right** — Accuracy vs. Memory Reduction (%) plot showing H₂O and Dynamic Sparsity maintain >75% accuracy even at ~80% memory reduction, while Static Strided/Local collapse sharply beyond 60–80% reduction.

**Key Technical Takeaway:** H₂O's hybrid retention policy (heavy-hitters + recent tokens) outperforms static strided/local patterns, preserving accuracy at high compression ratios where purely static schemes fail.

### Figure 7 (p.7) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig07.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p07.png]]*
> [!quote] caption
> The graph shows the simplified workflow of SnapKV, where the orange area represents the cluster of features per head selected by SnapKV. These features are then used to form new Key-Value pairs concatenated with the features in the observation window. Together, the selected prefix and observation windows constitute the new KV cache utilized for the generation. [2].

> [!tip] 技术解读（多模态）
> ## Figure 7: SnapKV Workflow — Description

**Architecture & Data Flow:**
- **Input (left):** A user submits a multi-turn conversational prompt (e.g., Q4 report, rephrasing email, gift, KV-cache explanation, R&D expense query).
- **Processing (center, blue box):** SnapKV operates across stacked **Layers** of *Input Sequence KVs*, each split into a **Prefix** (orange region) and an **Obs. window** (green region).
  1. **Voting & Selecting Important Features** → clusters features per attention head via **Attention Weight Calc.**
  2. **Clustering & Concatenating Features** → merges selected per-head features across layers, producing **Compressed KVs**.
- **Output (right):** A compressed KV cache feeds the LLM, which responds (e.g., "R&D expenses… xxx.xx billion").

**Key Technical Takeaway:** SnapKV compresses the KV cache by *head-wise feature voting* on attention scores, concatenating only critical prefix features with the observation window—preserving context fidelity while drastically shrinking memory for long-context inference.

## Caption (Verbatim)

**Figure 7:** The graph shows the simplified workflow of SnapKV, where the orange area represents the cluster of features per head selected by SnapKV. These features are then used to form new Key-Value pairs concatenated with the features in the observation window. Together, the selected prefix and observation windows constitute the new KV cache utilized for the generation. [2].

### Figure 8 (p.9) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig08.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p09.png]]*
> [!quote] caption
> Definition of per-token and per-channel quantization. X ∈Rlprompt×d is the key/value cache, where lprompt is the number of tokens and d is the number of channels. zX is the zero-point, and sX is the scaling factor.. [5]. whose magnitudes are very large”; whereas for value cache, “there is no obvious outlier pattern”. Based on this insight, KIVI applies per-channel quantization for keys and per-tok

> [!tip] 技术解读（多模态）
> ## Figure 9 — Palu's Low-Rank KV-Cache Projection

**Architecture & Data Flow:**
- **X** (input) is normally projected through full weight matrix **W** → **Y** (Original KV cache).
- **W** is *offline-decomposed* into two low-rank factors: **A** (down-projection) and **B** (up-projection), such that **A · B ≈ W**.
- Runtime path: **X → A → H** (latent bottleneck, cached) → **B → Ỹ** (reconstructed KV).
- The red annotation marks the storage swap: **"Cache H instead of Y"** — only the smaller latent **H** is retained in memory.

**Key Technical Takeaway:**
By replacing the full-rank projection **W** with a low-rank factorization **A·B**, the KV cache stores the compact latent **H** rather than the full **Y**, drastically reducing memory footprint while **Y** can be approximately reconstructed on demand via **B** — yielding high compression ratios with minimal reconstruction error since **W**'s decomposition is precomputed offline. (87 words)

## Caption (Verbatim)

**Figure 9:** Palu's low-rank projection method for KV-cache reduction. A weight matrix **W** of linear projection is decomposed into two low-rank matrices. Input **X** is down-projected to a latent representation **H**, which is cached. **Y** can be reconstructed from **H** using the up-projection matrix **B**. [19].

### Figure 9 (p.9) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig09.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p09.png]]*
> [!quote] caption
> Palu’s low-rank projection method for KV-cache reduction. A weight matrix W of linear projection is decomposed into two low-rank matrices. Input X is down-projected to a latent representation H, which is cached. Y can be reconstructed from H using the up-projection matrix B. [19]. 9

> [!tip] 技术解读（多模态）
> ## Figure 9 — Palu's Low-Rank KV-Cache Projection

**Architecture & Data Flow:**
- **X** (input) is normally projected through full weight matrix **W** → **Y** (Original KV cache).
- **W** is *offline-decomposed* into two low-rank factors: **A** (down-projection) and **B** (up-projection), such that **A · B ≈ W**.
- Runtime path: **X → A → H** (latent bottleneck, cached) → **B → Ỹ** (reconstructed KV).
- The red annotation marks the storage swap: **"Cache H instead of Y"** — only the smaller latent **H** is retained in memory.

**Key Technical Takeaway:**
By replacing the full-rank projection **W** with a low-rank factorization **A·B**, the KV cache stores the compact latent **H** rather than the full **Y**, drastically reducing memory footprint while **Y** can be approximately reconstructed on demand via **B** — yielding high compression ratios with minimal reconstruction error since **W**'s decomposition is precomputed offline. (87 words)

## Caption (Verbatim)

**Figure 9:** Palu's low-rank projection method for KV-cache reduction. A weight matrix **W** of linear projection is decomposed into two low-rank matrices. Input **X** is down-projected to a latent representation **H**, which is cached. **Y** can be reconstructed from **H** using the up-projection matrix **B**. [19].

### Figure 10 (p.11) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig10.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p11.png]]*
> [!quote] caption
> vLLM system overview [22]. 11

> [!tip] 技术解读（多模态）
> **Architecture & Data Flow:** Figure 10 depicts vLLM's distributed inference architecture centered around a **Scheduler** (green) that dispatches work to N parallel **Workers** (Worker 0 through Worker N−1), each hosting a **Cache Engine** and a **Model Shard** on a GPU. The Scheduler also interfaces with a **KV Cache Manager**, which maintains **Block tables** (analogous to OS page tables) and coordinates two specialized allocators — a **CPU Block Allocator** and a **GPU Block Allocator** — to manage KV cache placement across memory tiers.

**Key Technical Takeaway:** The system decouples centralized scheduling/orchestration from decentralized cache management, using paged virtual-memory abstractions to enable non-contiguous, block-level KV storage and efficient sharing across workers.

**Caption (verbatim):**
> Figure 10: vLLM system overview [22].

### Figure 11 (p.12) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig11.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p12.png]]*
> [!quote] caption
> Operation flow of the prefetching module of InfiniGen. [23]. A layer-wise KV cache management strategy is proposed in LayerKV [24]. The core concept is to split KV cache by layers, keeping only a subset of layers on the GPU during the prefill stage while offloading some layers to CPU memory to reduce Time to First Token (TTFT). Prefill time refers to the time for the GPU to compute the first token

> [!tip] 技术解读（多模态）
> **Architecture / Data Flow**

The figure depicts InfiniGen's prefetching pipeline across three phases. **Offline Skewing** pre-computes a skewness profile of attention weights. During **Prefill** (GPU), a Partial Weight Index Generation step identifies which token IDs are statistically important. In the **Decoding** stage (shown for Layer *i*−1 and Layer *i*), the GPU runs a lightweight KV selector → Attention → FFN sequence, while the CPU concurrently issues **Prefetching** commands. Selected Token IDs (orange) flow CPU→GPU; Selected Keys/Values (blue) feed into the next layer's KV selector.

**Key Takeaway**

Decoupling "which tokens matter" (offline skewing + on-GPU partial index generation) from "fetching only those tokens" allows InfiniGen to overlap CPU-side KV transfer with GPU attention computation, shrinking the working set transferred per step.

**Caption (verbatim):**

Figure 11: Operation flow of the prefetching module of InfiniGen. [23].

### Figure 12 (p.15) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig12.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p15.png]]*
> [!quote] caption
> Standard linear attention (top) vs. loglinear attention (bottom). The input consists of query, key, and value vectors [30]. at nearby keys and averages their value; while Linear Attention is alike global linear regression because it fits a global straight line for all data. Based on such observation, the authors proposed Local Linear Attention, which is similar to local linear regression. This ena

> [!tip] 技术解读（多模态）
> ## Description of Figure 12

**Architecture/Components:**
- **Top panel – Linear Attention:** A flat, sequential row of identical processing blocks, each consuming the local value vectors (orange circles below) and emitting an output (red circles above). Dashed auxiliary lines feed key/query signals across the sequence; outputs pass strictly left-to-right with no hierarchical aggregation.
- **Bottom panel – Log-Linear Attention:** Same input/output column structure, but the internal blocks form a **hierarchical/tree-like aggregation** — darker inner blocks (denoted by ⊕ addition nodes) accumulate neighboring values, then are progressively consolidated into lighter blocks above, finally projecting to the top output column. This creates a logarithmic-depth reduction rather than a flat chain.

**Data flow:** Value vectors enter at the bottom → are combined locally (⊕) and propagated upward through aggregation stages → final attended representations emitted at top.

**Key technical takeaway (≤120 words):**
Log-Linear Attention replaces linear attention's flat, single-path recurrence with a logarithmic-depth hierarchical aggregation tree. By locally pooling key-value pairs into intermediate "summary" nodes (shown by the ⊕ merges and stacked dark→light blocks) before propagating to the output, it reduces the effective path length between distant tokens from O(n) to O(log n). This preserves linear-time efficiency while improving representational capacity, since each query can attend to a richer, multi-resolution context rather than only a single linearly-propagated state. The design trades strict simplicity for hierarchical expressiveness.

## Caption (verbatim)

**Figure 12:** Standard linear attention (top) vs. loglinear attention (bottom). The input consists of query, key, and value vectors [30].

### Figure 13 (p.17) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig13.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p17.png]]*
> [!quote] caption
> During Pre-filling, ShadowKV offloads the value cache to the CPU while maintaining a low-rank key cache, landmarks, and outliers on the GPU. During decoding, it employs landmarks for sparse attention. [35].

> [!tip] 技术解读（多模态）
> # Figure 13: ShadowKV Architecture

**Architecture / Components / Data Flow:**
Figure 13 depicts ShadowKV's GPU–CPU hybrid design, split into two phases across a horizontal GPU/CPU boundary.

- **Pre-filling (GPU):** The **Pre-RoPE Key Cache** branches three ways: (1) **SVD** → compressed **Low-rank Key Cache**; (2) **RoPE & Reduce** → **Landmarks**; (3) **Find Outliers** → **Outliers**. The **Value Cache** is *offloaded* to the **CPU**.
- **Decoding (GPU):** **KV Selection** consults Landmarks, the Low-rank Key Cache, and Outliers; a **Cache Hit/Miss** check triggers **Low-rank Key Cache Reconstruction + RoPE**, feeding **Sparse Attention**.
- **Decoding (CPU):** *Selected Missed Chunk IDs* trigger **Value Cache Fetching**, returning values to the GPU for sparse attention.

**Key Technical Takeaway:**
ShadowKV exploits the **low-rank structure of pre-RoPE keys** to keep compressed keys and landmarks on the GPU while offloading values to the CPU; at decoding, landmark-based chunk selection + outlier retention enables **sparse attention without accuracy loss**, drastically cutting GPU memory.

**Caption (verbatim):**
"Figure 13: During Pre-filling, ShadowKV offloads the value cache to the CPU while maintaining a low-rank key cache, landmarks, and outliers on the GPU. During decoding, it employs landmarks for sparse attention. [35]."

### Figure 14 (p.17) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig14.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p17.png]]*
> [!quote] caption
> System overview of TailorKV. Offline identification categorizes the layers into quantization-friendly and sparsity-friendly. For quantization-friendly layers, we employ aggressive static quantization. For sparsity-friendly layers, we dynamically retrieve Top-K tokens. Critical current query and critical key cache represent the outliers in the query and key cache, respectively. [36]. A sparsity-awa

> [!tip] 技术解读（多模态）
> # Figure 13: ShadowKV Architecture

**Architecture / Components / Data Flow:**
Figure 13 depicts ShadowKV's GPU–CPU hybrid design, split into two phases across a horizontal GPU/CPU boundary.

- **Pre-filling (GPU):** The **Pre-RoPE Key Cache** branches three ways: (1) **SVD** → compressed **Low-rank Key Cache**; (2) **RoPE & Reduce** → **Landmarks**; (3) **Find Outliers** → **Outliers**. The **Value Cache** is *offloaded* to the **CPU**.
- **Decoding (GPU):** **KV Selection** consults Landmarks, the Low-rank Key Cache, and Outliers; a **Cache Hit/Miss** check triggers **Low-rank Key Cache Reconstruction + RoPE**, feeding **Sparse Attention**.
- **Decoding (CPU):** *Selected Missed Chunk IDs* trigger **Value Cache Fetching**, returning values to the GPU for sparse attention.

**Key Technical Takeaway:**
ShadowKV exploits the **low-rank structure of pre-RoPE keys** to keep compressed keys and landmarks on the GPU while offloading values to the CPU; at decoding, landmark-based chunk selection + outlier retention enables **sparse attention without accuracy loss**, drastically cutting GPU memory.

**Caption (verbatim):**
"Figure 13: During Pre-filling, ShadowKV offloads the value cache to the CPU while maintaining a low-rank key cache, landmarks, and outliers on the GPU. During decoding, it employs landmarks for sparse attention. [35]."

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.8) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-tab02.png]]
> [!quote] caption
> Summary of KV Cache eviction techniques

> [!tip] 表格解读（多模态）
> **Note:** The image presents a *table* (Table 2), not a figure with architecture/data flow.

**Description:**
This table summarizes KV Cache eviction techniques used in LLM inference optimization. It is organized into four columns — Method, Mechanism, Phase, and Overview — and contains a single entry for the H₂O method. The Method column names the technique (H₂O); the Mechanism column specifies its eviction strategy (removing the top-K noncritical tokens); the Phase column indicates when it operates (during decoding); and the Overview column provides a high-level summary of its design goal (balancing retention of Heavy-Hitter tokens with recent tokens).

**Key Technical Takeaway:**
H₂O is a decoding-phase eviction policy that selectively drops the top-K least-important tokens from the KV cache, preserving only Heavy-Hitter (frequently-attended) tokens plus recent context — exploiting the observation that attention mass concentrates on a small subset of tokens.

**Caption (verbatim):**
> Table 2: Summary of KV Cache eviction techniques

### Table 3 (p.10) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-tab03.png]]
> [!quote] caption
> Cache Compression Methods Comparison Table

> [!tip] 表格解读（多模态）
> **Main Figure / Table Description (Table 3 — Cache Compression Methods Comparison)**

The table compares two families of KV-cache compression techniques for LLM inference:

- **PALU (Low-Rank Projection)**: Decomposes projection matrix *W* via SVD into *A* (4096×r) and *B* (r×128). Input *X* is multiplied by *A* to produce a compact latent *H* (cached in place of KV); *H* is later reconstructed into the full KV by multiplying with *B*. Reconstruction matrix *B* is fused into other weight matrices offline (Matrix Fusion) to avoid runtime overhead; RoPE-based keys bypass fusion and are reconstructed via a custom GPU kernel. Group-Head Low-Rank Decomposition (G-LRD) balances joint vs. per-head decomposition for accuracy/cost.
- **KVQuant (Ultra-Low-Bit Quantization)**: Combines (1) Per-Channel Key Quantization, (2) Pre-RoPE Quantization, (3) Sensitivity-Weighted Non-Uniform Quantization (tailored levels for outliers), and (4) Per-Vector Dense-and-Sparse Quantization (≈1% outliers stored in higher precision).
- *Data flow*: Token *X* → projection/quantization → compressed cache (*H* or quantized KV) → on-demand reconstruction → attention.

**Key Technical Takeaway:** KV-cache compression splits into *projection-based* (PALU: train-free, offline fusion, RoPE handled by a custom GPU kernel) and *quantization-based* (KVQuant: aggressive bit reduction via per-channel, pre-RoPE, non-uniform, and outlier-aware schemes), enabling million-token context inference.

**Caption (verbatim):** *Table 3: Cache Compression Methods Comparison Table*

### Table 4 (p.13) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-tab04.png]]
> [!quote] caption
> Hybrid Memory Solutions Comparison Table

> [!tip] 表格解读（多模态）
> **Description:** The main figure is a comparison table (no architectural diagram is present) structured as a four-column matrix evaluating seven hybrid memory solutions for LLM KV-cache offloading (Paged Attention, InfiniGen, LayerKV, INF2, KVPR, Oneiros, CLO). Columns capture: *Method*, *Offload destination* (mostly CPU DRAM; INF2 uniquely targets Host Memory + NVMe CSDs), *Mechanism* (e.g., paging, speculation, layer-wise scheduling, parameter remapping, head-wise approximate caching), and *Key optimization* (fragmentation reduction, PCIe bandwidth utilization, TTFT minimization, multi-tenant reclaim). The accompanying prose details Oneiros's parameter-remapping flow and CLO's query-similarity–guided KV reuse pipeline.

**Key technical takeaway:** GPU memory pressure in autoregressive LLM inference is mitigated by offloading KV caches—and even remapped inactive-model parameters—to CPU memory, hiding PCIe transfer latency behind ongoing layer-by-layer compute via prefetching, similarity-based reuse, or asynchronous overlap. (118 words)

**Caption (verbatim):** "Table 4: Hybrid Memory Solutions Comparison Table"

### Table 5 (p.16) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-tab05.png]]
> [!quote] caption
> Attention Variants – Mechanisms, Complexities, and Features

> [!tip] 表格解读（多模态）
> **Note:** The provided content contains only the paper title and a table caption — no actual figure image or detailed figure description is included. Below I transcribe what's available and offer a brief inference based on the caption title.

**Description (inferred from "Table 5: Attention Variants – Mechanisms, Complexities, and Features"):**

The table likely compares multiple attention mechanisms used in LLM inference — including variants such as Multi-Head Attention (MHA), Multi-Query Attention (MQA), and Grouped-Query Attention (GQA). Columns would typically detail each variant's structural mechanism (shared vs. separate key/value projections), computational/memory complexity (e.g., KV cache size relative to hidden dimension and number of heads), and qualitative features such as quality trade-offs, inference speedup, and compatibility with KV cache optimization.

**Key technical takeaway:** Attention variants trade off KV cache memory against model quality — reducing distinct KV heads (MQA/GQA) shrinks cache footprint and improves inference throughput with minimal quality loss, making them core enablers for scalable KV cache optimization.

**Caption (verbatim transcription):**

> Table 5: Attention Variants – Mechanisms, Complexities, and Features

If you can share the actual figure or the full table contents, I can produce a more precise description and detailed technical analysis.

### Table 6 (p.18) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-tab06.png]]
> [!quote] caption
> Comparison of KV Cache Optimization Techniques

> [!tip] 表格解读（多模态）
> **Description:**

The table compares two KV cache optimization techniques for large language model inference, structured with four columns—Technique, Memory, Speedups, and Accuracy loss—against two rows of methods (H₂O and SnapKV). Each cell quantifies the efficiency gains and the resulting accuracy trade-offs, where reductions in memory correspond to throughput/latency improvements while accuracy loss remains comparable to a baseline.

**Key takeaway:** Both H₂O and SnapKV compress the KV cache to free memory and accelerate decoding, but H₂O delivers a stronger throughput boost (up to 29× vs. SnapKV's 3.6×) at the cost of more aggressive eviction, while SnapKV offers a steadier trade-off with smaller accuracy loss.

**Caption (verbatim):** Table 6: Comparison of KV Cache Optimization Techniques

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
KV_{per\ token} = 2 \times H\times D \times B \times L
$$

$$
KV_{cache\ size} = KV_{per\ token} \times \mathrm{Context Length}
$$

$$
\mathrm{Score}\left( Q_i, K_j\right) = \frac{Q_i \cdot K_j^{T}}{\sqrt{d_k}}
$$

$$
\alpha_{ij} = \mathrm{softmax}\!\left( \frac{Q_i \cdot K_j^{T}}{\sqrt{d_k}} \right)
$$

$$
\mathrm{output}_i = \sum_{j} \alpha_{ij} V_j
$$

$$
\tilde Q^{(\text{layer}+1)} = X^{(\text{layer})} \cdot M \cdot W_Q^{(\text{layer}+1)}
$$

$$
V_i' = \frac{\phi(Q_i)^T \sum_{j=1}^{i} \phi(K_j) V_j^T} {\phi(Q_i)^T \sum_{j=1}^{i} \phi(K_j)}
$$

$$
V_i' = \frac{\phi(Q_i)^T S_i}{\phi(Q_i)^T Z_i}
$$

$$
S_i = \sum_{j=1}^{i} \phi(K_j) V_j^T
$$

$$
Z_i = \sum_{j=1}^{i} \phi(K_j)
$$

$$
o_t = \sum_{\ell=0}^{L-1} \lambda_t^{(\ell)} q_t^T \left(\sum_{s \in B_t^{(\ell)}} v_s k_s^T \right) = \sum_{\ell=0}^{L-1} \lambda_t^{(\ell)} q_t^T S_t^{(\ell)}
$$

$$
S_t = (I - \beta_t k_t k_t^T)\,\mathrm{Diag}(\alpha_t)S_{t-1} + \beta_t k_t v_t^T \in \mathbb{R}^{d_k \times d_v}
$$

$$
o_t = S_t^T q_t \in \mathbb{R}^{d_v}
$$

## 相关论文

- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] — A Survey on Large Language Model Acceleration based on KV Cache Management
- [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] — CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion
- [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] — IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse
- [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] — Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter

## 技术点深读（DEEP）

![[deep/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference.txt`（91318 字符）供引用检索。