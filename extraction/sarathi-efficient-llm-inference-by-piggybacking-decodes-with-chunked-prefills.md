---
paper_num: "17"
title: "SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills"
authors: "Amey Agrawal*2, Ashish Panwar1, Jayashree Mohan1, Nipun Kwatra1, Bhargav S. Gulavani1, and Ramachandran Ramjee1 1Microsoft Research India 2Georgia Institute of Technology"
date: "2023/8/31"
arxiv: "https://arxiv.org/abs/2308.16369"
pdf: "papers/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills.pdf"
slug: "sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills"
tags: [disaggregated-serving]
---

# SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills

> [!abstract] 摘要（原文）
> 1\. 💡 SARATHI通过引入\`chunked-prefills\`和\`decode-maximal batching\`技术，解决了\`LLM\`推理中\`decode\`阶段\`GPU\`利用率低以及\`pipeline parallelism\`中由于\`prefill\`和\`decode\`时间差异导致的\`pipeline bubbles\`问题。 2. 🚀 \`decode-maximal batching\`使\`decode\`请求能够“\`piggyback\`”于\`prefill\`块，将内存密集型\`decode\`操作转变为计算密集型，并创建了计算负载均匀的\`hybrid batches\`，显著减少了\`pipeline bubbles\`。 3. 📈 SARATHI在\`LLaMA-13B\`模型上将\`decode throughput\`提高了高达10倍，\`end-to-end throughput\`提高了1.33倍；在\`GPT-3\`的\`pipeline parallelism\`中，它将\`bubbles\`减少了6.29倍，实现了1.91倍的\`end-to-end throughput\`提升。

## 元信息
- **发表日期**: 2023/8/31
- **作者**: Amey Agrawal*2, Ashish Panwar1, Jayashree Mohan1, Nipun Kwatra1, Bhargav S. Gulavani1, and Ramachandran Ramjee1 1Microsoft Research India 2Georgia Institute of Technology
- **arXiv**: https://arxiv.org/abs/2308.16369
- **本地 PDF**: `papers/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills.pdf`
- **页数**: 16

## 图表（原文 caption + 页码）

### Figure 1 (p.1)
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p01.png]]
> [!quote] caption
> Example two-stage pipeline parallel schedule. (a)

### Figure 2 (p.3) ⭐深度解读
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p03.png]]
> [!quote] caption
> High-level architecture of a decoder block. sequence length of each request (i.e., the number of input tokens in the given query), and H is the model’s embedding size (e.g., 5120 for LLaMA-13B).

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】SARATHI chunked-prefill：把 prompt 切成等长 prefill chunk（匹配流水级算力），在途 decode 请求 piggyback 到每个 prefill chunk 上→单次前向混合 prefill+decode token。解耦长 prefill 与 decode 延迟：每个流水级跑统一 hybrid-phase 步、消除 prefill-decode bubble、打满 GPU。更高单卡利用率+decode 吞吐+更大 batch。架构核心图。

### Figure 3 (p.4)
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p04.png]]
> [!quote] caption
> Per-token prefill and decode time with different batch sizes (sequence length = 1024) for LLaMa-13B on A6000 GPU. Prefill saturates GPU compute even at batch size of 1 and results in almost constant per-token time across batch sizes. Decode under-utilizes GPU compute and costs as much as 200× prefill for batch size 1. The incremental cost of linear operators for decode is almost zero as batch size

### Figure 4 (p.4)
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p04.png]]
> [!quote] caption
> Impact of the arithmetic intensity (bottom) on the throughput (top) of prefills and decodes for LLaMA-13B on A6000 GPU. operations. Figure 4b shows the arithmetic intensity of each operation separately for prefill (left) and decode phases (right).

### Figure 5 (p.5)
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p05.png]]
> [!quote] caption
> Pipeline bubbles in LLM inference A 2-way PP iteration-level schedule [48] across 4 requests (A,B,C,D) shows the existence of pipeline bubbles due to non-uniform batch execution times. set of layers; compared to TP which shards each layer across the participating GPUs. As discussed in §2.3, compared to TP, PP has a much better compute-communication ratio and does not require expensive interconnect

### Figure 6 (p.6)
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p06.png]]
> [!quote] caption
> Example of how attention mask is set across dif- ferent chunk prefill iterations in SARATHI (q and k represent “query" and “key" tokens, respectively). The attention mask for v (“values") is set similarly.

### Figure 7 (p.7)
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p07.png]]
> [!quote] caption
> The effect of tile quantization on the runtime of one iteration of LLaMA-13B on A6000 GPU. maximal batching with that of the baseline scheme that com- putes prefill and decode iterations separately. With baseline batching, a decode-only iteration spends 12.49 milliseconds per token. In contrast, per-token decode time is only 1.2 mil- liseconds with decode-maximal batching. This shows that pig- gyb

### Figure 8 (p.9)
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p09.png]]
> [!quote] caption
> Decode-only speedup with SARATHI on an A6000 GPU with LLaMA-13B (chunk size = 256).

### Figure 9 (p.10)
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p10.png]]
> [!quote] caption
> Normalized throughput (tokens/ms) for LLaMa 13B on A6000 GPU with different sequence lengths, P:D ratios, and chunk sizes. 2 4 6 8 10 12 14 16 18

### Figure 10 (p.10)
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p10.png]]
> [!quote] caption
> Breakdown of total time spent on different operations for LLaMa 13B on A6000 GPU with varying sequence lengths and batch sizes, using prefill chunk sizes of 256 (top half) and 512 (bottom half). Orange and blue bars represent baseline and SARATHI, respectively. for sequence length of 1K as shown in Figure 9a. Using the chunk size of 512 for sequence length=1K at batch size of 18 also provides sign

### Figure 11 (p.11)
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p11.png]]
> [!quote] caption
> Comparison with iteration-level scheduler Orca for LLaMa 13B on A6000 GPU. configuration of sequence length and chunk size, we show the effect of varying batch sizes. Further, for each run, we also show the runtime across different operations i.e., preproj, attention, postproj, and ffn.

### Figure 12 (p.12)
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p12.png]]
> [!quote] caption
> Impact of SARATHI on pipeline bubbles (top) and request completion times (bottom) for GPT-3 deployed on DGX A100(s) in simulation. the effect of variable sequence lengths on request latencies.

### Figure 13 (p.13)
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p13.png]]
> [!quote] caption
> Ablation study: Effect of varying the chunk size on different components of the system for LLaMa 13B on A6000 GPU. measure the time to compute the prefill phase for various se- quence lengths using the full sequence at once - this represents our baseline prefill performance. For each long sequence, we then compute the prefill with chunked-prefills and compare its end-to-end runtime with the baseli

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
B = \lfloor \left(\frac{M_G - M_S}{L*m_{kv}}\right) \rfloor
$$

## 相关论文

- [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] — Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve
- [[sglang-efficient-execution-of-structured-language-model-programs]] — SGLang: Efficient Execution of Structured Language Model Programs
- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation

## 技术点深读（DEEP）

![[deep/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills.txt`（76688 字符）供引用检索。