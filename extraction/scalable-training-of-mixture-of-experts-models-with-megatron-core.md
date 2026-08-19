---
paper_num: "12"
title: "Scalable Training of Mixture-of-Experts Models with Megatron Core"
authors: "Scalable Training of Mixture-of-Experts Models with Megatron Core Technical Report NVIDIA1"
date: "2026/3/8"
arxiv: "https://arxiv.org/abs/2603.07685"
pdf: "papers/scalable-training-of-mixture-of-experts-models-with-megatron-core.pdf"
slug: "scalable-training-of-mixture-of-experts-models-with-megatron-core"
tags: [moe, training]
---

# Scalable Training of Mixture-of-Experts Models with Megatron Core

> [!abstract] 摘要（原文）
> 1\. 🚀 本报告介绍了 NVIDIA Megatron-Core 框架中用于大规模混合专家模型（MoE）训练的系统级优化方案，旨在解决参数-计算不匹配带来的内存、通信和计算效率瓶颈。 2. 🛠️ 该框架通过 MoE Parallel Folding 实现多维度并行，解耦了注意力机制与 MoE 层的并行映射，并引入了 FP8/FP4 低精度训练、细粒度激活重计算及卸载等技术来应对存储压力。 3. 📈 为了提升性能，系统集成 DeepEP 和 HybridEP 优化了 Token 分发通信，并结合分组 GEMM 与算子融合等计算优化手段，显著提升了在 NVIDIA GB200 及 H100 集群上大规模 MoE 模型训练的吞吐量。

## 元信息
- **发表日期**: 2026/3/8
- **作者**: Scalable Training of Mixture-of-Experts Models with Megatron Core Technical Report NVIDIA1
- **arXiv**: https://arxiv.org/abs/2603.07685
- **本地 PDF**: `papers/scalable-training-of-mixture-of-experts-models-with-megatron-core.pdf`
- **页数**: 88

## 图表（原文 caption + 页码）

### Figure 1 (p.9)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p09.png]]
> [!quote] caption
> Data flow through an MoE layer: Route, Dispatch, Compute, and Combine stages.

### Figure 2 (p.10)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p10.png]]
> [!quote] caption
> Router architecture: linear projection, score function, top-𝑘selection, and load balancing. combine_postprocess (backward).

### Figure 3 (p.13)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p13.png]]
> [!quote] caption
> Dense Model vs MoE Model parameter/compute scaling.

### Figure 4 (p.15)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p15.png]]
> [!quote] caption
> Expert Parallelism (EP) distributes experts across GPUs. The all-to-all communication dispatches tokens to their assigned experts and combines results.

### Figure 5 (p.17)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p17.png]]
> [!quote] caption
> Parallelism mappings: traditional constraints vs. MoE Parallel Folding decoupling.

### Figure 6 (p.18)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p18.png]]
> [!quote] caption
> Parallel Folding: decoupled attention and MoE parallelism mappings.

### Figure 7 (p.22)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p22.png]]
> [!quote] caption
> Memory-Efficient Permutation.

### Figure 8 (p.23)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p23.png]]
> [!quote] caption
> Selective Recomputation.

### Figure 9 (p.24)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p24.png]]
> [!quote] caption
> Fine-grained activation offloading: stream overlap for forward and backward passes.

### Figure 10 (p.26)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p26.png]]
> [!quote] caption
> Fine-grained offloading and recomputation: complementary memory optimization strategies. optimization target. Megatron-Core provides two techniques: precision-aware optimization that reduces storage requirements, and CPU offloading that moves inactive state off-GPU.

### Figure 11 (p.28)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p28.png]]
> [!quote] caption
> Comparison of sharding strategies: (a) FSDP2 shards each parameter uniformly; (b) Megatron-FSDP flattens per-module and shards non-uniformly, aligning with communication buffers.

### Figure 12 (p.28)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p28.png]]
> [!quote] caption
> Persistent double-buffer design: two pre-allocated buffers are cycled across FSDP collectives, eliminating allocation overhead and enabling NCCL User Buffer Registration.

### Figure 13 (p.30)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p30.png]]
> [!quote] caption
> Expert parallelism across 4 GPUs with 4 experts.

### Figure 14 (p.31)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p31.png]]
> [!quote] caption
> The dispatch kernel design of HybridEP.

### Figure 15 (p.31)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p31.png]]
> [!quote] caption
> The combine kernel design of HybridEP.

### Figure 16 (p.32)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p32.png]]
> [!quote] caption
> Merged FWD-FWD Timeline with all-to-all Overlapping.

### Figure 17 (p.33)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p33.png]]
> [!quote] caption
> Merged FWD-BWD Timeline with all-to-all Overlapping.

### Figure 18 (p.34)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p34.png]]
> [!quote] caption
> EP all-to-all communication overlap strategies: baseline vs. 1F1B with W/D split.

### Figure 19 (p.35)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p35.png]]
> [!quote] caption
> Interleaved PP Timeline with all-to-all Overlapping.

### Figure 20 (p.37)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p37.png]]
> [!quote] caption
> The pipeline for permute fusion in the training process. • Preprocessing: Permutation is fundamentally a data transfer process that requires tokens to be stored consecutively in the buffer corresponding to each expert. The purpose of the preprocessing step is to generate an offset map (Row ID map in figure 20), which indicates the offset of each token in the input and output buffers. This ensures 

### Figure 21 (p.38)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p38.png]]
> [!quote] caption
> The workflow of the router fusion. • Computation of MoE auxiliary loss: Building on step 2, the auxiliary loss computation is fused into a single kernel.

### Figure 22 (p.39)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p39.png]]
> [!quote] caption
> Traditional execution (top) versus CUDA Graph execution (bottom).

### Figure 23 (p.39)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p39.png]]
> [!quote] caption
> Full versus layer-wise CUDA Graphs in one training iteration (three layers, two microbatches).

### Figure 24 (p.40)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p40.png]]
> [!quote] caption
> Partial CUDA Graphs capture static components (attention, shared experts, router, preprocessing) while leaving dynamic expert computation outside the graph.

### Figure 25 (p.41)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p41.png]]
> [!quote] caption
> Transformer layer forward pass: without (upper) and with (lower) partial CUDA Graphs. CPU overhead is largely eliminated for static components.

### Figure 26 (p.42)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p42.png]]
> [!quote] caption
> Why Pipeline Parallelism prevents CUDA Graphs from being shared across microbatches. With PP (top): Execution is interleaved—multiple forward passes run before any backward pass. If microbatches share a graph, F_mb1 overwrites saved context of F_mb0 before B_mb0 uses it, causing memory corruption. Each microbatch needs its own graph (𝐿× 𝑀× 2 graphs total). Without PP (bottom): Execution is sequent

### Figure 27 (p.45)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p45.png]]
> [!quote] caption
> ECHO workflow for forward and backward passes. The planner generates routing and hot expert maps. Expert Dispatch clones hot expert weights to spare slots; Expert Gradient Dispatch reduces gradients back to home experts.

### Figure 28 (p.46)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p46.png]]
> [!quote] caption
> Memory layout comparison across three execution modes. Left: Eager mode allocates memory dynamically based on actual usage. Middle: Baseline static shape requires worst-case sized buffers for each layer independently, causing severe fragmentation when actual usage is lower. Right: Paged Stashing uses a single worst-case tmp buffer shared across layers for computation, while a paged stashing buffer

### Figure 29 (p.46)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p46.png]]
> [!quote] caption
> Paged Stashing stream overlap. Forward pass: After Layer N computes, its activations are stashed (copied from tmp buffer to paged stashing buffer) on a dedicated Pack stream while Layer N+1 computes on the main Compute stream—the stash is completely overlapped. Backward pass: Activations for Layer N are pre-fetched (reloaded from stashing buffer to tmp buffer) on the Unpack stream before Layer N b

### Figure 30 (p.50)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p50.png]]
> [!quote] caption
> FP8 training recipes: Per-Tensor Scaling, Blockwise FP8, and MXFP8. A reduced-precision training recipe consists of: • Data format. There are two types of FP8 format: E4M3 and E5M2 [71, 74]. Usually there are two combinations used in training: ∘E4M3: Inputs, weights, and gradients are all quantized in the E4M3 format. ∘Hybrid: Inputs and weights are quantized in E4M3, while gradients are quantized

### Figure 31 (p.52)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p52.png]]
> [!quote] caption
> The computation of a linear layer with various FP8 recipes. Note the differences in quantization granularity and tensor layout requirements across platforms. precise due to the finer-grained scaling granularity, and has better performance due to the native support of MXFP8 in the Tensor Core. Therefore, MXFP8 is the default FP8 recipe on the Blackwell platform.

### Figure 32 (p.53)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p53.png]]
> [!quote] caption
> FP8 primary weight quantization scheme for blockwise scaling.

### Figure 33 (p.54)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p54.png]]
> [!quote] caption
> FP8 primary weight quantization scheme for delayed scaling and per-tensor current scaling.

### Figure 34 (p.57)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p57.png]]
> [!quote] caption
> SDPA exhibits 𝑂(𝑠2) complexity, while MoE and the remaining attention operations exhibit 𝑂(𝑠) complexity. Therefore, SDPA dominates the computation at longer sequence lengths.

### Figure 35 (p.59)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p59.png]]
> [!quote] caption
> Communication and computation patterns of TP and two types of CP.

### Figure 36 (p.61)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p61.png]]
> [!quote] caption
> Unpacked vs. Packed sequences.

### Figure 37 (p.61)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p61.png]]
> [!quote] caption
> Compute imbalance in causal attention over packed sequences. are partitioned and which CP communication group is used by attention operators, without requiring any parameter redistribution or optimizer-state migration. Therefore, Dynamic-CP provides a practical form of dynamic parallelism for variable-length training with minimal framework overhead. Related work, including

### Figure 38 (p.61)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p61.png]]
> [!quote] caption
> Dynamic Context Parallelism for Packed Sequences.

### Figure 39 (p.64)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p64.png]]
> [!quote] caption
> Load balancing strategies in Megatron-Core MoE.

### Figure 40 (p.65)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p65.png]]
> [!quote] caption
> Shared expert architecture in Megatron-Core MoE. The shared expert processes all tokens while routed experts process only their assigned tokens. When overlap is enabled, shared expert computation runs in parallel with the token dispatch/combine communication, hiding its latency. FLOP and per parameter. The architecture has been adopted by NVIDIA’s Nemotron-3 Super and Ultra models.

### Figure 41 (p.66)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p66.png]]
> [!quote] caption
> Flexible Pipeline Parallel Placement. 66

### Figure 42 (p.67)
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p67.png]]
> [!quote] caption
> An example of granular upcycling a dense layer into E2G2T2 fine-grained MoE. E2G2T2 denotes 4 experts, top 2, with half intermediate size. (1) We shard MLP weights in the intermediate dimension (4ℎ→2ℎ) then duplicate the shards. (2) We initialize half the router weights then duplicate them. This ensures Top2 always selects one of each MLP shard so MoE output is the same as the dense model at the s

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.9 `(𝑝𝑖= 𝜎(𝑙𝑖)/ ∑︀`
- p.16 `World Size = TP × CP × PP × DP,`
- p.16 `at minimum. Since EP ⊆DP, requesting EP=8 forces DP ≥8. Combined with CP=8 for long sequences, the`
- p.17 `• Traditional: EP ≤DP = 8, so maximum EP is 8.`
- p.42 `results in 𝐿×𝑀×2 graphs in total (where 𝐿= layers per GPU, 𝑀= microbatches, ×2 for forward/backward).`
- p.64 `output(x) = 𝑊↑·`

## 相关论文

- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey
- [[muon-is-scalable-for-llm-training]] — Muon is Scalable for LLM Training
- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[zero-memory-optimizations-toward-training-trillion-parameter-models]] — ZeRO: Memory Optimizations Toward Training Trillion Parameter Models
- [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] — GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints

## 技术点深读（DEEP）

![[deep/scalable-training-of-mixture-of-experts-models-with-megatron-core]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/scalable-training-of-mixture-of-experts-models-with-megatron-core.txt`（265930 字符）供引用检索。