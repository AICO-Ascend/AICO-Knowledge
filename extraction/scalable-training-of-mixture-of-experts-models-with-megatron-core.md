---
paper_num: "12"
title: "Scalable Training of Mixture-of-Experts Models with Megatron Core"
authors: "Scalable Training of Mixture-of-Experts Models with Megatron Core Technical Report NVIDIA"
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
- **作者**: Scalable Training of Mixture-of-Experts Models with Megatron Core Technical Report NVIDIA
- **arXiv**: https://arxiv.org/abs/2603.07685
- **本地 PDF**: `papers/scalable-training-of-mixture-of-experts-models-with-megatron-core.pdf`
- **页数**: 88

## 图表（原文 caption + 页码）
_未检测到带 caption 的 figure_

## 相关论文

- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey
- [[muon-is-scalable-for-llm-training]] — Muon is Scalable for LLM Training
- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[zero-memory-optimizations-toward-training-trillion-parameter-models]] — ZeRO: Memory Optimizations Toward Training Trillion Parameter Models
- [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] — GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints

## 全文文本
全文已存 `extraction/fulltext/scalable-training-of-mixture-of-experts-models-with-megatron-core.txt`（8903 字符）供引用检索。