---
paper_num: "67"
title: "CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion"
authors: "RAG with Cached Knowledge Fusion Jiayi Yao University of Chicago/CUHK Shenzhen Hanchen Li University of Chicago Yuhan Liu University of Chicago Siddhant Ray University of Chicago Yihua Cheng University of Chicago Qizheng"
date: "2024/5/26"
arxiv: "https://arxiv.org/abs/2405.16444"
pdf: "papers/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion.pdf"
slug: "cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion"
tags: [kv-cache]
---

# CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion

> [!abstract] 摘要（原文）
> Large language models (LLMs) often incorporate multiple text chunks in their inputs to provide the necessary contexts. To speed up the prefill of the long LLM inputs, one can pre-compute the KV cache of a text and re-use the KV cache when the context is reused as the prefix of another LLM input. However, the reused text chunks are not always the input prefix, which makes precomputed KV caches not directly usable since they ignore the text's cross-attention with the preceding texts. Thus, the benefits of reusing KV caches remain largely unrealized. This paper tackles just one challenge: when an LLM input contains multiple text chunks, how to quickly combine their precomputed KV caches in order to achieve the same generation quality as the expensive full prefill (i.e., without reusing KV cache)? This challenge naturally arises in retrieval-augmented generation (RAG) where the input is supplemented with multiple retrieved texts as the context. We present CacheBlend, a scheme that reuses the precomputed KV caches, regardless prefix or not, and selectively recomputes the KV values of a small subset of tokens to partially update each reused KV cache. In the meantime, the small extra delay for recomputing some tokens can be pipelined with the retrieval of KV caches within the same job, allowing CacheBlend to store KV caches in slower devices with more storage capacity while retrieving them without increasing the inference delay. By comparing CacheBlend with the state-of-the-art KV cache reusing schemes on three open-source LLMs of various sizes and four popular benchmark datasets of different tasks, we show that CacheBlend reduces time-to-first-token (TTFT) by 2.2-3.3x and increases the inference throughput by 2.8-5x from full KV recompute without compromising generation quality. The code is available at this https URL.

## 元信息
- **发表日期**: 2024/5/26
- **作者**: RAG with Cached Knowledge Fusion Jiayi Yao University of Chicago/CUHK Shenzhen Hanchen Li University of Chicago Yuhan Liu University of Chicago Siddhant Ray University of Chicago Yihua Cheng University of Chicago Qizheng
- **arXiv**: https://arxiv.org/abs/2405.16444
- **本地 PDF**: `papers/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion.pdf`
- **页数**: 16

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig01.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p02.png]]*
> [!quote] caption
> Contrasting full KV recompute, prefix caching, full KV reuse, and CacheBlend’s selective KV recompute. full KV recompute (Figure 1(a)). Despite many optimizations, the delay and computation of prefill grow super-linearly with the input length, and can easily slow down the service, especially on long LLM inputs (e.g., in RAG) [11, 53, 60].

> [!tip] 技术解读（多模态）
> **Architecture / Data flow (Figure 1):**
Four side-by-side panels contrast how an LLM processes a multi-chunk input ("Chunk 1 + Chunk 2 + Chunk 3") and produces the KV cache of [1, 2, 3]:
- **(a) Default Full KV recompute:** Prefills the entire input end-to-end → slowest, good quality.
- **(b) Prefix caching:** Reuses only the KV cache of Chunk 1 (the prefix); Chunks 2–3 still require prefill → marginally faster, good quality.
- **(c) Full KV reuse:** Concatenates all three stored KV caches and ignores cross-attention → much faster, low quality.
- **(d) CacheBlend (ours):** Reuses all three stored KV caches but selectively recomputes a small fraction to restore cross-attention → much faster, good quality.

**Key takeaway:** CacheBlend matches the speed of full KV reuse with the quality of full recompute by updating <15% of KV per layer, exploiting attention-matrix sparsity to recover cross-chunk attention cheaply.

**Caption (verbatim):**
*"Figure 1. Contrasting full KV recompute, prefix caching, full KV reuse, and CacheBlend's selective KV recompute."*

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig02.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p04.png]]*
> [!quote] caption
> Generation quality improves as more text chunks are retrieved. and fetch top-k relevant chunks from the database, based on the least L2 distance between the embeddings of the query and the chunk respectively. Figure 2 shows the generation quality, measured using a standard F1-score metric, with an increasing number of selected text chunks. We can see that the quality improves significantly as more

> [!tip] 技术解读（多模态）
> **Figure 3 — Architecture/Components/Data Flow:**

The figure is a three-panel illustration of an RAG-style LLM pipeline with two retrieved text chunks (Chunk 1: Messi's stats; Chunk 2: Ronaldo's stats) prepended to a user query.

- **(a) Setup:** Defines the inputs — two relevant chunks plus a comparative query ("Who scored more goals at FIFA World Cups, Messi or Ronaldo?").
- **(b) Full KV recompute:** Chunks 1 and 2 are concatenated raw → fed into the LLM alongside the query → produces the *correct* answer (green check).
- **(c) Full KV reuse:** Each chunk's KV cache is precomputed *independently* and then concatenated → LLM produces a *wrong*, generic response (red X).

**Key technical takeaway:** Precomputing KV caches per chunk destroys cross-attention between chunks, so when a query requires reasoning across multiple retrieved passages, modular KV reuse degrades to a rambling, incorrect answer despite saving prefill cost.

**Caption (verbatim):**

*Figure 3. An illustrative example of an LLM input with two text chunks prepended to a query. Full KV recompute (b), without reusing KV cache, is slow but gives the correct answer. Full KV reuse (c), however, gives the wrong answer as it neglects cross-attention between the chunks (Figure 4).*

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig03.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p04.png]]*
> [!quote] caption
> An illustrative example of an LLM input with two text chunks prepended to a query. Full KV recompute (b), with- out reusing KV cache, is slow but gives the correct answer. Full KV reuse (c), however, gives the wrong answer as it neglects cross-attention between the chunks (Figure 4). uses this KV cache to generate the answer, it will start to ramble and not produce the right answer.

> [!tip] 技术解读（多模态）
> **Figure 3 — Architecture/Components/Data Flow:**

The figure is a three-panel illustration of an RAG-style LLM pipeline with two retrieved text chunks (Chunk 1: Messi's stats; Chunk 2: Ronaldo's stats) prepended to a user query.

- **(a) Setup:** Defines the inputs — two relevant chunks plus a comparative query ("Who scored more goals at FIFA World Cups, Messi or Ronaldo?").
- **(b) Full KV recompute:** Chunks 1 and 2 are concatenated raw → fed into the LLM alongside the query → produces the *correct* answer (green check).
- **(c) Full KV reuse:** Each chunk's KV cache is precomputed *independently* and then concatenated → LLM produces a *wrong*, generic response (red X).

**Key technical takeaway:** Precomputing KV caches per chunk destroys cross-attention between chunks, so when a query requires reasoning across multiple retrieved passages, modular KV reuse degrades to a rambling, incorrect answer despite saving prefill cost.

**Caption (verbatim):**

*Figure 3. An illustrative example of an LLM input with two text chunks prepended to a query. Full KV recompute (b), without reusing KV cache, is slow but gives the correct answer. Full KV reuse (c), however, gives the wrong answer as it neglects cross-attention between the chunks (Figure 4).*

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig04.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p05.png]]*
> [!quote] caption
> Contrasting the attention matrices of (a) full KV recompute and (b) full KV reuse. The yellow boxes highlight the cross-attention. The right-hand side plots show the resulting forward attention matrices whose discrepancies are a result of the different cross-attention between the two methods. 4

> [!tip] 技术解读（多模态）
> **Figure Description:**

Figure 4 presents two rows comparing attention matrix behavior under two KV cache strategies, each row showing a left heatmap ("Attention matrix" with a yellow-boxed "Cross-attention" region, ~tokens 0–25) and a right heatmap ("Forward-attention", ~tokens 0–45).

- **(a) Full KV recompute:** The cross-attention box shows scattered activations, producing a forward-attention matrix with distributed bright spots across token positions.
- **(b) Full KV reuse:** The cross-attention box is essentially empty (cross-attention is ignored), causing prominent vertical bright stripes in the forward-attention—indicating tokens attending uniformly to a few positions.

**Key Takeaway:** Skipping cross-attention (full KV reuse) corrupts the forward-attention pattern with spurious vertical bands, while full recompute preserves correct token-to-token attention—motivating selective KV updates (CACHEBLEND).

**Caption (verbatim):**
*"Figure 4. Contrasting the attention matrices of (a) full KV recompute and (b) full KV reuse. The yellow boxes highlight the cross-attention. The right-hand side plots show the resulting forward attention matrices whose discrepancies are a result of the different cross-attention between the two methods."*

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig05.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p06.png]]*
> [!quote] caption
> Illustrated contrast between (a) full KV recompute and (b) selective KV recompute on one layer. 0 10 20 30 40 50

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 5) Description:**

The figure contrasts two KV-cache recomputation strategies in a transformer layer. Panel (a) shows *full KV recompute* (reference): layer-*i* input produces Q_i, which is multiplied by K_i to form the Attention Matrix, then multiplied by V_i to produce the next layer's input. Panel (b) shows *selective KV recompute* on two chosen tokens: Q_i is applied to K_i and V_i, but the legend distinguishes "Re-used" (light) versus "Re-computed" (dark) tokens. Only the selected two tokens are recomputed; the rest are reused from the cached values, feeding into the same attention computation and producing the next-layer input. The pipeline (Q×K → Attn Matrix → ×V) is identical in both cases—only the recomputation scope differs.

**Key Takeaway:** Compute overhead scales with the *number* of selected tokens; recomputing only r% of tokens costs r% of full prefill, making selective recomputation a controllable accuracy–efficiency knob.

**Caption (verbatim):**
*Figure 5. Illustrated contrast between (a) full KV recompute and (b) selective KV recompute on one layer.*

### Figure 6 (p.6) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig06.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p06.png]]*
> [!quote] caption
> Attention deviation reduces as we recompute the KV of more tokens on each layer. Importantly, the biggest drop in attention deviation results from recomputing the KV of the tokens with the highest KV deviation (i.e., HKVD tokens). on layer 𝑖, so that the attention matrix includes attention between selected tokens and all other tokens. • Finally, it runs the same attention module to produce the inp

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 5) Description:**

The figure contrasts two KV-cache recomputation strategies in a transformer layer. Panel (a) shows *full KV recompute* (reference): layer-*i* input produces Q_i, which is multiplied by K_i to form the Attention Matrix, then multiplied by V_i to produce the next layer's input. Panel (b) shows *selective KV recompute* on two chosen tokens: Q_i is applied to K_i and V_i, but the legend distinguishes "Re-used" (light) versus "Re-computed" (dark) tokens. Only the selected two tokens are recomputed; the rest are reused from the cached values, feeding into the same attention computation and producing the next-layer input. The pipeline (Q×K → Attn Matrix → ×V) is identical in both cases—only the recomputation scope differs.

**Key Takeaway:** Compute overhead scales with the *number* of selected tokens; recomputing only r% of tokens costs r% of full prefill, making selective recomputation a controllable accuracy–efficiency knob.

**Caption (verbatim):**
*Figure 5. Illustrated contrast between (a) full KV recompute and (b) selective KV recompute on one layer.*

### Figure 7 (p.7) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig07.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p07.png]]*
> [!quote] caption
> Distribution of KV deviation of different tokens on one layer. 5 vs. 6 12 vs. 13 21 vs. 22 31 vs. 32

> [!tip] 技术解读（多模态）
> **Description of Figure 9 (CacheBlend architecture):**

The diagram depicts a layer-wise pipeline (Layer 1 → Layer 2 → Layer 3 → …) where each layer maintains two KV-cache stores: an *Updated KV* and a *Precomputed KV*. At Layer 1, all tokens are recomputed. For subsequent layers, only a small subset of "HKVD" (High KV Deviation) tokens is selectively recomputed, while the rest are re-used. The selection process is cascading: each layer's KV deviation is computed only over the HKVD tokens inherited from the previous layer, then the top few with the highest deviation are passed forward as the new HKVD set. A legend distinguishes *Re-used* vs *Re-computed* tokens.

**Key technical takeaway:** A gradual, layer-to-layer filtering scheme (with decreasing token counts r₁ > r₂ > …) yields more statistically reliable HKVD identification than single-layer attention deviation, while keeping recompute costs minimal.

**Caption (verbatim):**
"Figure 9. CACHEBLEND selects the HKVD (high KV deviation) tokens of one layer by computing KV deviation of only the HKVD tokens selected from the previous layer and selecting the tokens among them with high KV deviation."

### Figure 8 (p.7) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig08.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p07.png]]*
> [!quote] caption
> Rank correlation of the KV deviation per token be- tween two consecutive layers. expensive and defeats the purpose of selective KV recom- pute. Instead, we observe that the HKVD tokens on different layers are not independent:

> [!tip] 技术解读（多模态）
> **Description of Figure 9 (CacheBlend architecture):**

The diagram depicts a layer-wise pipeline (Layer 1 → Layer 2 → Layer 3 → …) where each layer maintains two KV-cache stores: an *Updated KV* and a *Precomputed KV*. At Layer 1, all tokens are recomputed. For subsequent layers, only a small subset of "HKVD" (High KV Deviation) tokens is selectively recomputed, while the rest are re-used. The selection process is cascading: each layer's KV deviation is computed only over the HKVD tokens inherited from the previous layer, then the top few with the highest deviation are passed forward as the new HKVD set. A legend distinguishes *Re-used* vs *Re-computed* tokens.

**Key technical takeaway:** A gradual, layer-to-layer filtering scheme (with decreasing token counts r₁ > r₂ > …) yields more statistically reliable HKVD identification than single-layer attention deviation, while keeping recompute costs minimal.

**Caption (verbatim):**
"Figure 9. CACHEBLEND selects the HKVD (high KV deviation) tokens of one layer by computing KV deviation of only the HKVD tokens selected from the previous layer and selecting the tokens among them with high KV deviation."

### Figure 9 (p.7) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig09.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p07.png]]*
> [!quote] caption
> CacheBlend selects the HKVD (high KV deviation) tokens of one layer by computing KV deviation of only the HKVD tokens selected from the previous layer and selecting the tokens among them with high KV deviation.

> [!tip] 技术解读（多模态）
> **Description of Figure 9 (CacheBlend architecture):**

The diagram depicts a layer-wise pipeline (Layer 1 → Layer 2 → Layer 3 → …) where each layer maintains two KV-cache stores: an *Updated KV* and a *Precomputed KV*. At Layer 1, all tokens are recomputed. For subsequent layers, only a small subset of "HKVD" (High KV Deviation) tokens is selectively recomputed, while the rest are re-used. The selection process is cascading: each layer's KV deviation is computed only over the HKVD tokens inherited from the previous layer, then the top few with the highest deviation are passed forward as the new HKVD set. A legend distinguishes *Re-used* vs *Re-computed* tokens.

**Key technical takeaway:** A gradual, layer-to-layer filtering scheme (with decreasing token counts r₁ > r₂ > …) yields more statistically reliable HKVD identification than single-layer attention deviation, while keeping recompute costs minimal.

**Caption (verbatim):**
"Figure 9. CACHEBLEND selects the HKVD (high KV deviation) tokens of one layer by computing KV deviation of only the HKVD tokens selected from the previous layer and selecting the tokens among them with high KV deviation."

### Figure 10 (p.8) ⭐深度解读
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p08.png]]
> [!quote] caption
> (a) Smartly picking the recompute ratio will not incur an extra delay. (b) Smartly picking storage device(s) to store KVs saves cost while not increasing delay. recompute of one layer, the KV-loading delay should be able to hide the selective recompute delay, i.e., without incurring any extra delay on time-to-first-token (TTFT).

> [!tip] 技术解读（多模态）
> ## Figure 10 Description

**Figure 10** illustrates two design choices in CacheBlend's loading controller, presented as two panels:

**Panel (a) – Recompute ratio:** Line plot of Prefill delay (TTFT, y-axis) vs. Re-compute ratio %, x-axis 0–50). A dashed line ("w/o pipelining") rises steeply from ~1 to ~3.5s; a solid line ("w. pipelining") stays nearly flat, rising only slightly from ~1 to ~2s. An annotation marks 26.8% as the optimal ratio for a 1 GB/s SSD where no extra delay is introduced.

**Panel (b) – Storage device choice:** Bar chart comparing Prefill delay across GPU, CPU RAM, SSD (32 Gbps), and SSD (4 Gbps), with hatched bars for w/o pipelining and solid bars for w. pipelining. The annotation identifies the cheapest device (CPU RAM) that introduces no extra delay under a 15% recompute ratio.

## Key Technical Takeaway (≤120 words)

CacheBlend exploits **pipelining of KV loading and selective recomputation** so that, as long as the recompute delay T_recompute remains ≤ the KV-loading delay T_load, the recomputation is "hidden" and TTFT is not penalized. This lets the controller decouple quality from latency: (1) pick the smallest recompute ratio r* whose quality drop is negligible (empirically ~15%), then (2) select the cheapest storage device whose T_load ≥ T_recompute. Result: KV caches can be stored on slower, cheaper media (e.g., CPU RAM or 32 Gbps SSD instead of GPU HBM) without increasing TTFT, cutting cost while preserving inference quality.

## Caption (verbatim)

**Figure 10.** *(a) Smartly picking the recompute ratio will not incur an extra delay. (b) Smartly picking storage device(s) to store KVs saves cost while not increasing delay.*

### Figure 11 (p.9) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig11.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p09.png]]*
> [!quote] caption
> CacheBlend system (green stared) in light of LLM context augmented generation for a single request. CacheBlend uses text provided by the retriever, interacts with the storage device(s), and provides KV cache on top of LLM inference engines.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Figure 11** illustrates the **CacheBlend system** workflow for LLM context-augmented generation:

**Components:**
- **User** (left) submits a query (e.g., *"Can we use drones in agriculture?"*)
- **CacheBlend System** (green-stared, dotted box): contains *Loading Controller* and *KV Cache Fuser*, producing a *Fused KV Cache*
- **KV Cache Store** (right): hierarchical storage — CPU (fastest) → SSD → Slower Disks
- **Text chunks**: Drone #1/#2, Agri #1/#2

**Data Flow (numbered ①–⑥):**
1. User query → Loading Controller
2. Controller queries relevant text chunks
3. Cache Store locates corresponding KV entries
4. KV Caches #1–4 + recompute ratio → Fuser; Controller signals potential new caches
5. Fuser merges them → Fused KV Cache
6. Fused cache fed to LLM → answer returned to user

**Key Technical Takeaway:** CacheBlend accelerates LLM inference on long retrieved contexts by loading pre-computed KV caches from storage and performing only **selective recomputation** of high-deviation tokens (HKVD) layer-by-layer—dramatically reducing prefill cost while preserving output quality. This layer-wise pipeline overlaps KV loading with recompute via parallel threads.

---

## Caption (Verbatim)

**Figure 11.** *CacheBlend system (green stared) in light of LLM context augmented generation for a single request. CacheBlend uses text provided by the retriever, interacts with the storage device(s), and provides KV cache on top of LLM inference engines.*

### Figure 12 (p.10) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig12.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p10.png]]*
> [!quote] caption
> CacheBlend reduces TTFT by 2.2-3.3× compared to full KV recompute with negligible quality drop across four datasets and three models.

> [!tip] 技术解读（多模态）
> **Description of Figure 12 (Main Figure):**

The figure is a **4×3 grid of scatter plots** comparing four caching/decoding strategies across three LLMs and four long-context datasets.

- **Columns (models):** Mistral-7B, Yi-34B, Llama-70B
- **Rows (datasets):** 2WikiMQA, Musique (F1-score); SAMSum, MultiNews (RougeL-score)
- **X-axis:** TTFT (s) — time to first token (lower = faster)
- **Y-axis:** Generation quality (higher = better)
- **Markers:** CacheBlend (red square, "ours"), Full KV reuse (orange ×), Prefix Caching (blue ●), Full KV recompute (blue ▲)
- **"Better" arrow** points toward the upper-left (low latency + high quality)

**Data flow:** Each method independently processes the long prompt; the plot maps latency vs. output quality so the Pareto frontier is read directly from marker positions.

**Key takeaway:** CacheBlend sits in the optimal upper-left region of every subplot — delivering 2.2–3.3× TTFT reduction over full KV recompute while matching or exceeding its quality, consistently dominating Full KV reuse (which is fast but low quality) and Prefix Caching.

**Caption (verbatim):** *CacheBlend reduces TTFT by 2.2-3.3× compared to full KV recompute with negligible quality drop across four datasets and three models.*

### Figure 13 (p.10) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig13.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p10.png]]*
> [!quote] caption
> Generation quality of CacheBlend with Yi-34B vs MapReduce and MapRerank. 7

> [!tip] 技术解读（多模态）
> **Description of Figure 12 (Main Figure):**

The figure is a **4×3 grid of scatter plots** comparing four caching/decoding strategies across three LLMs and four long-context datasets.

- **Columns (models):** Mistral-7B, Yi-34B, Llama-70B
- **Rows (datasets):** 2WikiMQA, Musique (F1-score); SAMSum, MultiNews (RougeL-score)
- **X-axis:** TTFT (s) — time to first token (lower = faster)
- **Y-axis:** Generation quality (higher = better)
- **Markers:** CacheBlend (red square, "ours"), Full KV reuse (orange ×), Prefix Caching (blue ●), Full KV recompute (blue ▲)
- **"Better" arrow** points toward the upper-left (low latency + high quality)

**Data flow:** Each method independently processes the long prompt; the plot maps latency vs. output quality so the Pareto frontier is read directly from marker positions.

**Key takeaway:** CacheBlend sits in the optimal upper-left region of every subplot — delivering 2.2–3.3× TTFT reduction over full KV recompute while matching or exceeding its quality, consistently dominating Full KV reuse (which is fast but low quality) and Prefix Caching.

**Caption (verbatim):** *CacheBlend reduces TTFT by 2.2-3.3× compared to full KV recompute with negligible quality drop across four datasets and three models.*

### Figure 14 (p.11) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig14.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p11.png]]*
> [!quote] caption
> CacheBlend achieves lower TTFT with higher throughput in RAG scenarios compared with baselines of similar quality. 3 6 9 12 (a) Number of chunks

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 14) — Description**

Figure 14 is a 2×3 grid of line plots benchmarking TTFT (Time-To-First-Token, y-axis, seconds) against Average Request Rate per Second (x-axis). Columns correspond to three LLMs (Mistral-7B, Yi-34B, Llama-70B); rows correspond to two RAG datasets (2WikiMQA Extended, Musique Extended). Four methods are compared via colored lines: **CacheFuse** (red, ours), **Full KV recompute** (dark blue), **Prefix Caching – RAM** (light blue), and **Prefix Caching – RAM+SSD** (green). Figure 15 supplements this with three ablations varying (a) number of chunks, (b) chunk length, and (c) batch size, again contrasting CacheFuse vs. Full KV recompute.

**Key technical takeaway:** CacheFuse sustains dramatically lower TTFT under high request rates across all three model scales and both datasets, with the advantage widening for larger LLMs (Llama-70B), demonstrating its ability to reuse blended KV caches to decouple throughput from context length.

**Captions (verbatim):**

- **Figure 14.** *CACHEBLEND* achieves lower TTFT with higher throughput in RAG scenarios compared with baselines of similar quality.
- **Figure 15.** *CACHEBLEND* outperforms baseline with varying chunk numbers, chunk lengths, and batch sizes.

### Figure 15 (p.11) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig15.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p11.png]]*
> [!quote] caption
> CacheBlend outperforms baseline with varying chunk numbers, chunk lengths, and batch sizes. • SAMSum [25]: This dataset comprises multiple pairs of dialogues and summaries, and requires the LLM to output a summary to a new dialogue. It is intended to test the few-shot learning ability of language models and contains 200 test cases. • MultiNews [20]: This dataset consists of news articles and human

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 14) — Description**

Figure 14 is a 2×3 grid of line plots benchmarking TTFT (Time-To-First-Token, y-axis, seconds) against Average Request Rate per Second (x-axis). Columns correspond to three LLMs (Mistral-7B, Yi-34B, Llama-70B); rows correspond to two RAG datasets (2WikiMQA Extended, Musique Extended). Four methods are compared via colored lines: **CacheFuse** (red, ours), **Full KV recompute** (dark blue), **Prefix Caching – RAM** (light blue), and **Prefix Caching – RAM+SSD** (green). Figure 15 supplements this with three ablations varying (a) number of chunks, (b) chunk length, and (c) batch size, again contrasting CacheFuse vs. Full KV recompute.

**Key technical takeaway:** CacheFuse sustains dramatically lower TTFT under high request rates across all three model scales and both datasets, with the advantage widening for larger LLMs (Llama-70B), demonstrating its ability to reuse blended KV caches to decouple throughput from context length.

**Captions (verbatim):**

- **Figure 14.** *CACHEBLEND* achieves lower TTFT with higher throughput in RAG scenarios compared with baselines of similar quality.
- **Figure 15.** *CACHEBLEND* outperforms baseline with varying chunk numbers, chunk lengths, and batch sizes.

### Figure 16 (p.8) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig16.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p08.png]]*
> [!quote] caption
> This means that even if the storage device is a fast device (ex. CPU RAM), the delay will be lower-bounded by the minimal recomputation to guarantee quality.

> [!tip] 技术解读（多模态）
> ## Figure 10 Description

**Figure 10** illustrates two design choices in CacheBlend's loading controller, presented as two panels:

**Panel (a) – Recompute ratio:** Line plot of Prefill delay (TTFT, y-axis) vs. Re-compute ratio %, x-axis 0–50). A dashed line ("w/o pipelining") rises steeply from ~1 to ~3.5s; a solid line ("w. pipelining") stays nearly flat, rising only slightly from ~1 to ~2s. An annotation marks 26.8% as the optimal ratio for a 1 GB/s SSD where no extra delay is introduced.

**Panel (b) – Storage device choice:** Bar chart comparing Prefill delay across GPU, CPU RAM, SSD (32 Gbps), and SSD (4 Gbps), with hatched bars for w/o pipelining and solid bars for w. pipelining. The annotation identifies the cheapest device (CPU RAM) that introduces no extra delay under a 15% recompute ratio.

## Key Technical Takeaway (≤120 words)

CacheBlend exploits **pipelining of KV loading and selective recomputation** so that, as long as the recompute delay T_recompute remains ≤ the KV-loading delay T_load, the recomputation is "hidden" and TTFT is not penalized. This lets the controller decouple quality from latency: (1) pick the smallest recompute ratio r* whose quality drop is negligible (empirically ~15%), then (2) select the cheapest storage device whose T_load ≥ T_recompute. Result: KV caches can be stored on slower, cheaper media (e.g., CPU RAM or 32 Gbps SSD instead of GPU HBM) without increasing TTFT, cutting cost while preserving inference quality.

## Caption (verbatim)

**Figure 10.** *(a) Smartly picking the recompute ratio will not incur an extra delay. (b) Smartly picking storage device(s) to store KVs saves cost while not increasing delay.*

### Figure 17 (p.12) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig17.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p12.png]]*
> [!quote] caption
> CacheBlend’s outperforms baselines when using RAM and slower disks

> [!tip] 技术解读（多模态）
> **Figure 16 — Description**

Four side-by-side scatter plots compare quality score (F1-Score for 2WikiMQA/Musique; RougeL-Score for SAMSum/MultiNews, y-axis, 0–0.4) against Re-compute Ratio (%, x-axis, 0–100). Four methods are plotted: CacheBlend (red squares), Full KV reuse (orange ×), Prefix Caching (blue circles), and Full KV recompute (blue triangles). Arrows in each subplot point toward the upper-left "Better" corner (low recompute, high quality).

**Key takeaway:** CacheBlend clusters in the low-recompute, high-quality sweet spot (5–18% recompute, near-maximum scores), while full KV recompute and prefix caching sit at ~90–100% recompute, and full KV reuse shows low quality—demonstrating CacheBlend's Pareto-dominant quality/efficiency trade-off.

**Caption (verbatim):**
Figure 16. *CACHEBLEND* has minimal loss in quality compared with full KV recompute, with 5%–18% selective recompute ratio, with Yi-34B.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\begin{aligned} {q}_{m+l} {k}_{m} &={(\mathbb{R}^{d}_{\Theta, m+l}q)}^{T}{(\mathbb{R}^{d}_{\Theta, m}k)}\\ &= \sum_{i=0}^{d/2-1}({q_{[2i]}k_{[2i]}\cos (m+l-m)\theta_{i}}\\ & \quad +{q_{[2i+1]}k_{[2i+1]}\cos (m+l-m)\theta_{i}}) \\ &= \sum_{i=0}^{d/2-1}({q_{[2i]}k_{[2i]}+ {q_{[2i+1]}k_{[2i+1]}})\cos l\theta_{i}} \\ \end{aligned}
$$

$$
q_{m}, k_{m}= \begin{pmatrix} \cos m\theta & -\sin m\theta\\ \sin m\theta & \cos m\theta\\ \end{pmatrix} \{ \begin{pmatrix} q_{[0]}\\ q_{[1]}\\ \end{pmatrix}, \begin{pmatrix} k_{[0]}\\ k_{[1]}\\ \end{pmatrix} \}
$$

$$
\begin{aligned} {q}_{im} {k}_{j(m-n)} &= q_{[0]i}k_{[0]j}\cos (m-m+n)\theta\\ & \quad +q_{[1]i}k_{[1]j}\cos (m-m+n)\theta \\ &= (q_{[0]i}k_{[0]j}+q_{[1]i}k_{[1]j})\cos n\theta \\ \end{aligned}
$$

## 相关论文

- [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] — A Survey on Large Language Model Acceleration based on KV Cache Management
- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] — KV Cache Optimization Strategies for Scalable and Efficient LLM Inference
- [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] — IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse
- [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] — Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter

## 技术点深读（DEEP）

![[deep/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion.txt`（75206 字符）供引用检索。