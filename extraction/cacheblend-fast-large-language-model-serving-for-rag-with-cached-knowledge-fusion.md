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

### Figure 1 (p.2)
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p02.png]]
> [!quote] caption
> Contrasting full KV recompute, prefix caching, full KV reuse, and CacheBlend’s selective KV recompute. full KV recompute (Figure 1(a)). Despite many optimizations, the delay and computation of prefill grow super-linearly with the input length, and can easily slow down the service, especially on long LLM inputs (e.g., in RAG) [11, 53, 60].

### Figure 2 (p.4)
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p04.png]]
> [!quote] caption
> Generation quality improves as more text chunks are retrieved. and fetch top-k relevant chunks from the database, based on the least L2 distance between the embeddings of the query and the chunk respectively. Figure 2 shows the generation quality, measured using a standard F1-score metric, with an increasing number of selected text chunks. We can see that the quality improves significantly as more

### Figure 3 (p.4)
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p04.png]]
> [!quote] caption
> An illustrative example of an LLM input with two text chunks prepended to a query. Full KV recompute (b), with- out reusing KV cache, is slow but gives the correct answer. Full KV reuse (c), however, gives the wrong answer as it neglects cross-attention between the chunks (Figure 4). uses this KV cache to generate the answer, it will start to ramble and not produce the right answer.

### Figure 4 (p.5)
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p05.png]]
> [!quote] caption
> Contrasting the attention matrices of (a) full KV recompute and (b) full KV reuse. The yellow boxes highlight the cross-attention. The right-hand side plots show the resulting forward attention matrices whose discrepancies are a result of the different cross-attention between the two methods. 4

### Figure 5 (p.6)
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p06.png]]
> [!quote] caption
> Illustrated contrast between (a) full KV recompute and (b) selective KV recompute on one layer. 0 10 20 30 40 50

### Figure 6 (p.6)
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p06.png]]
> [!quote] caption
> Attention deviation reduces as we recompute the KV of more tokens on each layer. Importantly, the biggest drop in attention deviation results from recomputing the KV of the tokens with the highest KV deviation (i.e., HKVD tokens). on layer 𝑖, so that the attention matrix includes attention between selected tokens and all other tokens. • Finally, it runs the same attention module to produce the inp

### Figure 7 (p.7)
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p07.png]]
> [!quote] caption
> Distribution of KV deviation of different tokens on one layer. 5 vs. 6 12 vs. 13 21 vs. 22 31 vs. 32

### Figure 8 (p.7)
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p07.png]]
> [!quote] caption
> Rank correlation of the KV deviation per token be- tween two consecutive layers. expensive and defeats the purpose of selective KV recom- pute. Instead, we observe that the HKVD tokens on different layers are not independent:

### Figure 9 (p.7)
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p07.png]]
> [!quote] caption
> CacheBlend selects the HKVD (high KV deviation) tokens of one layer by computing KV deviation of only the HKVD tokens selected from the previous layer and selecting the tokens among them with high KV deviation.

### Figure 10 (p.8)
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p08.png]]
> [!quote] caption
> (a) Smartly picking the recompute ratio will not incur an extra delay. (b) Smartly picking storage device(s) to store KVs saves cost while not increasing delay. recompute of one layer, the KV-loading delay should be able to hide the selective recompute delay, i.e., without incurring any extra delay on time-to-first-token (TTFT).

### Figure 11 (p.9)
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p09.png]]
> [!quote] caption
> CacheBlend system (green stared) in light of LLM context augmented generation for a single request. CacheBlend uses text provided by the retriever, interacts with the storage device(s), and provides KV cache on top of LLM inference engines.

### Figure 12 (p.10)
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p10.png]]
> [!quote] caption
> CacheBlend reduces TTFT by 2.2-3.3× compared to full KV recompute with negligible quality drop across four datasets and three models.

### Figure 13 (p.10)
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p10.png]]
> [!quote] caption
> Generation quality of CacheBlend with Yi-34B vs MapReduce and MapRerank. 7

### Figure 14 (p.11)
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p11.png]]
> [!quote] caption
> CacheBlend achieves lower TTFT with higher throughput in RAG scenarios compared with baselines of similar quality. 3 6 9 12 (a) Number of chunks

### Figure 15 (p.11)
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p11.png]]
> [!quote] caption
> CacheBlend outperforms baseline with varying chunk numbers, chunk lengths, and batch sizes. • SAMSum [25]: This dataset comprises multiple pairs of dialogues and summaries, and requires the LLM to output a summary to a new dialogue. It is intended to test the few-shot learning ability of language models and contains 200 test cases. • MultiNews [20]: This dataset consists of news articles and human

### Figure 16 (p.8)
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p08.png]]
> [!quote] caption
> This means that even if the storage device is a fast device (ex. CPU RAM), the delay will be lower-bounded by the minimal recomputation to guarantee quality.

### Figure 17 (p.12)
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p12.png]]
> [!quote] caption
> CacheBlend’s outperforms baselines when using RAM and slower disks

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.8 `5𝑇𝑟𝑒𝑐𝑜𝑚𝑝𝑢𝑡𝑒(𝑟%, 𝐿𝐿𝑀, 𝐿) = 𝑟% × 𝑃𝑟𝑒𝑓𝑖𝑙𝑙(𝐿𝐿𝑀, 𝐿). 𝑃𝑟𝑒𝑓𝑖𝑙𝑙(𝐿𝐿𝑀, 𝐿) is`
- p.16 `is the rotary matrix with hyperparameter Θ ∈{𝜃𝑖= 10000−2𝑖𝑑,𝑖∈`

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