---
paper_num: "18"
title: "Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve"
authors: "Amey Agrawal*2, Nitin Kedia1, Ashish Panwar1, Jayashree Mohan1, Nipun Kwatra1, Bhargav S. Gulavani1, Alexey Tumanov2, and Ramachandran Ramjee1 1Microsoft Research India 2Georgia Institute of Technology"
date: "2024/3/4"
arxiv: "https://arxiv.org/abs/2403.02310"
pdf: "papers/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve.pdf"
slug: "taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve"
tags: [disaggregated-serving]
---

# Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve

> [!abstract] 摘要（原文）
> 1\. 💡 针对大型语言模型（LLM）推理中吞吐量与延迟的权衡问题，现有调度器因预填充和解码阶段的特性差异，常导致生成停顿和流水线气泡。 2. 🧠 Sarathi-Serve通过引入“分块预填充”将大型预填充请求拆分为计算量相等的块，并采用“无停顿调度”将新请求的预填充块与现有解码操作合并，以确保批处理计算均匀。 3. 🚀 实验结果显示，Sarathi-Serve在维持低尾延迟的同时显著提高了LLM服务容量，例如在不同模型和硬件上实现高达5.6倍的端到端服务容量增益。

## 元信息
- **发表日期**: 2024/3/4
- **作者**: Amey Agrawal*2, Nitin Kedia1, Ashish Panwar1, Jayashree Mohan1, Nipun Kwatra1, Bhargav S. Gulavani1, Alexey Tumanov2, and Ramachandran Ramjee1 1Microsoft Research India 2Georgia Institute of Technology
- **arXiv**: https://arxiv.org/abs/2403.02310
- **本地 PDF**: `papers/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve.pdf`
- **页数**: 18

## 图表（原文 caption + 页码）

### Figure 1 (p.1)
![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p01.png]]
> [!quote] caption
> Yi-34B running on two A100 GPUs serving 128 requests from arxiv-summarisation trace. 1a highlights one of the many generation stalls lasting over several seconds in vLLM [53]. 1b shows the impact of increasing load on tail latency. Sarathi-Serve improves throughput while eliminating generation stalls. 1

### Figure 2 (p.2)
![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p02.png]]
> [!quote] caption
> Current LLM serving systems involve a tradeoff be- tween throughput and latency depending on their scheduling policy. Prioritizing prefills optimizes throughput but sacrifices TBT (time-between-tokens) tail latency whereas prioritizing decodes has the opposite effect. Sarathi-Serve serves high throughput with low TBT latency via stall-free batching. (The figure is illustrative and actual values wi

### Figure 3 (p.5)
![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p05.png]]
> [!quote] caption
> Throughput of the prefill and decode phases with different batch sizes for Mistral-7B running on a single A100 GPU. We use prompt length of 1024 for both prefill and decode experiments. Note that different y-axis, showing pre- fills are much more efficient than decode. Further, note that batching boosts decode throughput almost linearly but has a marginal effect on prefill throughput.

### Figure 4 (p.5)
![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p05.png]]
> [!quote] caption
> Prefill and decode time with different input sizes for Mistral-7B running on single A100 GPU. Linear layers contribute to the majority of runtime in both prefill and decode phases. Due to the low arithmetic intensity in decode batches, the cost of linear operation for 1 decode token is nearly same as 128 prefill tokens. into linear, attention and others, and shows their individual contributions. F

### Figure 5 (p.6)
![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]]
> [!quote] caption
> Arithmetic intensity trend for LLaMA2-70B lin- ear operations with different number of token running on four A100s. Decode batches have low arithmetic intensity i.e., they are bottlenecked by memory fetch time, leading to low compute utilization. Prefill batches are compute bound with sub-optimal bandwidth utilization. Sarathi-Serve forms balanced batches by combining decodes and prefill chunks to

### Figure 6 (p.6)
![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]]
> [!quote] caption
> Linear layer execution time as function of number of tokens in a batch for LLaMA2-70B on A100(s) with different tensor parallel degrees. When the number of tokens is small, execution time is dictated by the cost of fetching weights from HBM memory. Hence, execution time is largely stagnant in the 128-512 tokens range, especially for higher tensor parallel degrees. Once the number of tokens in the 

### Figure 7 (p.6)
![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]]
> [!quote] caption
> A generation stall occurs when one or more prefills are scheduled in between consecutive decode iterations of a request. A, B, C and D represent different requests. Sub- script d represents a decode iteration, p represents a full prefill and p0, p1 represent two chunked prefills of a given prompt. vLLM induces generation stalls by scheduling as many pre- fills as possible before resuming ongoing d

### Figure 8 (p.7)
![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p07.png]]
> [!quote] caption
> A 2-way pipeline parallel iteration-level schedule in Orca across 4 requests (A,B,C,D) shows the existence of pipeline bubbles due to non-uniform batch execution times.

### Figure 9 (p.8)
![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p08.png]]
> [!quote] caption
> The incremental cost of coalescing prefills with decode batches. We consider two batching schemes – (i) Decode +

### Figure 10 (p.11)
![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p11.png]]
> [!quote] caption
> Capacity (in queries per second) of Mistral-7B and

### Figure 11 (p.11)
![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p11.png]]
> [!quote] caption
> Capacity of LLaMA2-70B and Falcon-180B (mod- els with pipeline parallelism) with different schedulers under strict (SLO-S) and relaxed (SLO-R) latency SLOs.

### Figure 12 (p.12)
![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p12.png]]
> [!quote] caption
> Latency – Throughput tradeoff in vLLM and

### Figure 13 (p.12)
![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p12.png]]
> [!quote] caption
> TP scales poorly across nodes. (a) Median TBT for decode-only batches: cross node TP increases median TBT by more than 2× compared to a 4-way TP within node and PP across nodes. (b) Capacity under strict (SLO-S) and re- laxed (SLO-R) latency SLOs: Sarathi-Serve increases Falcon- 180B’s serving capacity by 4.3× and 3.6× over vLLM’s TP- only and hybrid-parallel configurations under strict SLOs.

### Figure 14 (p.13)
![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p13.png]]
> [!quote] caption
> Overhead of chunked-prefills in prefill computation for Yi-34B (TP-2) normalized to the cost of no-chunking, shown for various prompt lengths using chunk lengths of 512, 1024 and 2048.

## 全文文本
全文已存 `extraction/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve.txt`（82501 字符）供引用检索。