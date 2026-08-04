---
paper_num: "43"
title: "SGLang: Efficient Execution of Structured Language Model Programs"
authors: "Structured Language Model Programs Lianmin Zheng2∗ Liangsheng Yin3 Zhiqiang Xie1 Chuyue Sun1 Jeff Huang4 Cody Hao Yu5 Shiyi Cao2 Christos Kozyrakis1 Ion Stoica2 Joseph E. Gonzalez2 Clark Barrett1 Ying Sheng1∗ 1 Stanford "
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2312.07104"
pdf: "papers/sglang-efficient-execution-of-structured-language-model-programs.pdf"
slug: "sglang-efficient-execution-of-structured-language-model-programs"
tags: [disaggregated-serving]
---

# SGLang: Efficient Execution of Structured Language Model Programs

> [!abstract] 摘要（原文）
> 1\. 🚀 SGLang是一个用于高效编程和执行复杂Language Model Programs (LM Programs) 的系统，其前端语言通过提供生成和并行控制的Primitives简化了多调用结构。 2. ⚡️ 其运行时引入了RadixAttention以自动复用KV cache、Compressed Finite State Machine以加速结构化输出解码，以及API speculative execution以优化API-only模型。 3. 📈 实验结果表明，SGLang在多种LLM应用和模型上实现了高达6.4倍的吞吐量提升和3.7倍的延迟降低，超越了现有的推理系统。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Structured Language Model Programs Lianmin Zheng2∗ Liangsheng Yin3 Zhiqiang Xie1 Chuyue Sun1 Jeff Huang4 Cody Hao Yu5 Shiyi Cao2 Christos Kozyrakis1 Ion Stoica2 Joseph E. Gonzalez2 Clark Barrett1 Ying Sheng1∗ 1 Stanford 
- **arXiv**: https://arxiv.org/abs/2312.07104
- **本地 PDF**: `papers/sglang-efficient-execution-of-structured-language-model-programs.pdf`
- **页数**: 20

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐MiniMax深度解读
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p02.png]]
> [!quote] caption
> System architecture: An interpreter executes language primitives with optimized runtime.

> [!tip] 技术解读（MiniMax 多模态）
> 【MiniMax 解读】SGLang 系统架构(Fig.1)：Python 嵌入式前端+高性能 runtime，流式 interpreter 提交原语(extend/gen/fork)异步执行并保留依赖。RadixAttention 用 LRU 基数树缓存 KV，跨请求共享前缀自动复用中间注意力态。Frontiers&Dependencies 跟踪就绪原语+数据依赖→批独立操作、重叠执行藏延迟。DSL+radix-cache+依赖调度统一，比 vLLM/Guidance/LMQL 快至 6.4x。架构核心图。

### Figure 2 (p.3)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p03.png]]
> [!quote] caption
> The implementation of a multi-dimensional essay judge in SGLang utilizes the branch-solve-merge prompting technique [40]. Primitives provided by SGLang are shown in red. 2

### Figure 3 (p.5)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p05.png]]
> [!quote] caption
> Examples of RadixAttention operations with an LRU eviction policy, illustrated across nine time points. The figure demonstrates the dynamic evolution of the radix tree in response to various requests. These requests include two chat sessions, a batch of few-shot learning inquiries, and a self-consistency sampling. Each tree edge carries a label denoting a substring or a sequence of tokens. The nod

### Figure 4 (p.6)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p06.png]]
> [!quote] caption
> The decoding process of normal and compressed FSMs (the underscore _ means a space). requests by matched prefix length and prioritize requests with longer matched prefixes instead of using a first-come, first-served schedule. Alg. 1 (Appendix) shows the pseudo-code for cache-aware scheduling with contiguous batching. The algorithm uses longest-shared-prefix-first order. In more latency-sensitive s

### Figure 5 (p.7)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p07.png]]
> [!quote] caption
> Normalized throughput on Llama-7B models. Higher is better. pattern: s += context + "name:" + gen("name", stop="\n") + "job:" + gen("job", stop="\n"). Naively, the two gen primitives correspond to two API calls, meaning that the user needs to pay for the input token fee on the context twice. In SGLang, we can enable speculative execution on the first call and let it continue the generation of a fe

### Figure 6 (p.8)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p08.png]]
> [!quote] caption
> Normalized latency on Llama-7B models. Lower is better. MMLU

### Figure 7 (p.8)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p08.png]]
> [!quote] caption
> Normalized throughput on Mixtral-8x7B models with tensor parallelism. Higher is better. result from KV cache reuse, the exploitation of parallelism within a single program, and faster constrained decoding. Next, we explain the reasons for the speedup in each benchmark.

### Figure 8 (p.9)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p09.png]]
> [!quote] caption
> (a)(b) Cache hit rate ablation study. (c) RadixAttention ablation study.

### Figure 9 (p.14)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p14.png]]
> [!quote] caption
> KV cache sharing examples. Blue boxes represent shareable prompt parts, green boxes indicate non-shareable parts and yellow boxes mark non-shareable model outputs. Shareable elements include few-shot learning examples, questions in self-consistency [53], chat history in multi-turn chat, and search history in tree-of-thought [56]. A

### Figure 10 (p.17)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p17.png]]
> [!quote] caption
> Example of how regex is converted into FSM and how FSM guides the decoding process.

### Figure 11 (p.18)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p18.png]]
> [!quote] caption
> Comparison of decoding using Compressed FSM versus normal FSM: The left subfigure depicts the decoding process per forward pass, while the right subfigure explains the origins of various result components. direct partitioning might alter the intended meaning [50]. For example, the compressed text in Fig. 2’s regex is {"summary": ", which can only be tokenized as {", summary, ": and _" according to

### Figure 12 (p.19)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p19.png]]
> [!quote] caption
> Normalized throughput on Llama-2-70B models with tensor parallelism. Higher is better. MMLU

### Figure 13 (p.19)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p19.png]]
> [!quote] caption
> Achieved cache hit rate and optimal cache hit rate on various benchmarks. opportunities for more compilation optimizations, as we can rewrite the graph and perform more static planning. D.1

### Figure 14 (p.20)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p20.png]]
> [!quote] caption
> An SGLang program and its corresponding dataflow graph.

## 全文文本
全文已存 `extraction/sglang-efficient-execution-of-structured-language-model-programs.txt`（79774 字符）供引用检索。