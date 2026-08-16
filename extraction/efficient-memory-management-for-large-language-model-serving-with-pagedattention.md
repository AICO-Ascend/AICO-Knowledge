---
paper_num: "52"
title: "Efficient Memory Management for Large Language Model Serving with PagedAttention"
authors: "Model Serving with PagedAttention Woosuk Kwon1,∗Zhuohan Li1,∗Siyuan Zhuang1 Ying Sheng1,2 Lianmin Zheng1 Cody Hao Yu3 Joseph E. Gonzalez1 Hao Zhang4 Ion Stoica1 1UC Berkeley 2Stanford University 3Independent Researcher 4"
date: "2023/9/13"
arxiv: "https://arxiv.org/abs/2309.06180"
pdf: "papers/efficient-memory-management-for-large-language-model-serving-with-pagedattention.pdf"
slug: "efficient-memory-management-for-large-language-model-serving-with-pagedattention"
tags: []
---

# Efficient Memory Management for Large Language Model Serving with PagedAttention

> [!abstract] 摘要（原文）
> 1. High throughput serving of large language models (LLMs) requires batching sufficiently many requests at a time. How- ever, existing systems struggle because the key-value cache (KV cache) memory for each request is huge and grows and shrinks dynamically. When managed inefficiently, this memory can be significantly wasted by fragmentation and redundant duplication, limiting the

## 元信息
- **发表日期**: 2023/9/13
- **作者**: Model Serving with PagedAttention Woosuk Kwon1,∗Zhuohan Li1,∗Siyuan Zhuang1 Ying Sheng1,2 Lianmin Zheng1 Cody Hao Yu3 Joseph E. Gonzalez1 Hao Zhang4 Ion Stoica1 1UC Berkeley 2Stanford University 3Independent Researcher 4
- **arXiv**: https://arxiv.org/abs/2309.06180
- **本地 PDF**: `papers/efficient-memory-management-for-large-language-model-serving-with-pagedattention.pdf`
- **页数**: 16

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p01.png]]
> [!quote] caption
> Left: Memory layout when serving an LLM with 13B parameters on NVIDIA A100. The parameters (gray) persist in GPU memory throughout serving. The memory for the KV cache (red) is (de)allocated per serving request. A small amount of memory (yellow) is used ephemerally for activation. Right: vLLM smooths out the rapid growth curve of KV cache memory seen in existing systems [31, 60], leading to a nota

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】PagedAttention 内存布局(Fig.1)：13B 模型在 A100-40G 上参数占 65%（26GB 常驻）、KV cache >30%（每请求动态）、激活小片。传统系统把每请求 KV 存成单连续张量→内部+外部碎片严重、batch 受限。PagedAttention 借 OS 虚拟内存分页：KV 切成固定块（如 16 token）存非连续物理显存，每请求 block table 映射逻辑→物理（类比页表）；请求间可共享物理块（并行采样/beam search/前缀共享）；碎片仅剩 sub-block 余量（~1 token vs GB 级）→近乎零 KV 浪费、吞吐 2-4x。架构核心图，KV-cache/serving 基石。

### Figure 2 (p.2)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p02.png]]
> [!quote] caption
> Average percentage of memory wastes in different LLM serving systems during the experiment in §6.2. percentage of memory is used for other data, including ac- tivations – the ephemeral tensors created when evaluating the LLM. Since the model weights are constant and the ac- tivations only occupy a small fraction of the GPU memory, the way the KV cache is managed is critical in determining the maxi

### Figure 3 (p.4)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p04.png]]
> [!quote] caption
> KV cache memory management in existing systems. Three types of memory wastes – reserved, internal fragmentation, and external fragmentation – exist that prevent other requests from fitting into the memory. The token in each memory slot represents its KV cache. Note the same tokens can have different KV cache when at different positions. 3

### Figure 4 (p.5)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p05.png]]
> [!quote] caption
> vLLM system overview.

### Figure 5 (p.5)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p05.png]]
> [!quote] caption
> Illustration of the PagedAttention algorithm, where the attention key and values vectors are stored as non-contiguous blocks in the memory. block size (𝐵). Denote the key block 𝐾𝑗= (𝑘(𝑗−1)𝐵+1, . . . ,𝑘𝑗𝐵) and value block 𝑉𝑗= (𝑣(𝑗−1)𝐵+1, . . . , 𝑣𝑗𝐵). The attention com- putation in Eq. 4 can be transformed into the following block- wise computation: 𝐴𝑖𝑗= exp(𝑞⊤ 𝑖𝐾𝑗/ √ 𝑑) Í⌈𝑖/𝐵⌉ 𝑡=1 exp(𝑞⊤ 𝑖𝐾𝑡1/ √ 𝑑

### Figure 6 (p.6)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p06.png]]
> [!quote] caption
> Block table translation in vLLM. divides it into physical KV blocks (this is also done on CPU RAM for swapping; see §4.5). The KV block manager also maintains block tables—the mapping between logical and physical KV blocks of each request. Each block table entry records the corresponding physical blocks of a logical block and the number of filled positions. Separating logical and physical KV block

### Figure 7 (p.6)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p06.png]]
> [!quote] caption
> Storing the KV cache of two requests at the same time in vLLM. requests and the latest tokens for generation phase requests) as one sequence and feeds it into the LLM. During LLM’s computation, vLLM uses the PagedAttention kernel to access the previous KV cache stored in the form of logical KV blocks and saves the newly generated KV cache into the physical KV blocks. Storing multiple tokens within

### Figure 8 (p.7)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p07.png]]
> [!quote] caption
> Parallel sampling example. generates a single sequence. In the remainder of this paper, we assume the more general case in which a request gener- ates multiple sequences. In parallel sampling, one request includes multiple samples sharing the same input prompt, allowing the KV cache of the prompt to be shared as well. Via its PagedAttention and paged memory management, vLLM can realize this sharin

### Figure 9 (p.7)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p07.png]]
> [!quote] caption
> Beam search example. sample space. The algorithm relies on the beam width pa- rameter 𝑘, which determines the number of top candidates retained at every step. During decoding, beam search ex- pands each candidate sequence in the beam by considering all possible tokens, computes their respective probabilities us- ing the LLM, and retains the top-𝑘most probable sequences out of 𝑘· |𝑉| candidates, wh

### Figure 10 (p.8)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p08.png]]
> [!quote] caption
> Shared prompt example for machine translation.

### Figure 11 (p.9)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p09.png]]
> [!quote] caption
> Input and output length distributions of the (a)

### Figure 12 (p.10)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p10.png]]
> [!quote] caption
> Single sequence generation with OPT models on the ShareGPT and Alpaca dataset

### Figure 13 (p.10)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p10.png]]
> [!quote] caption
> Average number of batched requests when serv- ing OPT-13B for the ShareGPT (2 reqs/s) and Alpaca (30 reqs/s) traces.

### Figure 14 (p.11)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p11.png]]
> [!quote] caption
> Parallel generation and beam search with OPT-13B on the Alpaca dataset.

### Figure 15 (p.11)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p11.png]]
> [!quote] caption
> Average amount of memory saving from sharing KV blocks, when serving OPT-13B for the Alpaca trace.

### Figure 16 (p.12)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p12.png]]
> [!quote] caption
> Translation workload where the input prompts share a common prefix. The prefix includes (a) 1 example with 80 tokens or (b) 5 examples with 341 tokens.

### Figure 17 (p.12)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p12.png]]
> [!quote] caption
> Performance on chatbot workload.

### Figure 18 (p.12)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p12.png]]
> [!quote] caption
> Ablation experiments. handle the long prompts, as PagedAttention resolves the problem of memory fragmentation and reservation. 7

### Figure 19 (p.13)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p13.png]]
> [!quote] caption
> (a) Overhead of recomputation and swapping for different block sizes. (b) Performance when serving OPT-13B with the ShareGPT traces at the same request rate.

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.3 `𝑃(𝑥) = 𝑃(𝑥1) · 𝑃(𝑥2 | 𝑥1) · · · 𝑃(𝑥𝑛| 𝑥1, . . . ,𝑥𝑛−1).`
- p.3 `𝑡=1 exp(𝑞⊤`

## 全文文本
全文已存 `extraction/fulltext/efficient-memory-management-for-large-language-model-serving-with-pagedattention.txt`（82023 字符）供引用检索。