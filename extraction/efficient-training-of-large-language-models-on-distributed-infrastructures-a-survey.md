---
paper_num: "51"
title: "Efficient Training of Large Language Models on Distributed Infrastructures: A Survey"
authors: "Efficient Training of Large Language Models on Distributed Infrastructures: A Survey Jiangfei Duan∗, Shuo Zhang∗, Zerui Wang∗, Lijuan Jiang, Wenwen Qu, Qinghao Hu, Guoteng Wang, Qizhen Weng, Hang Yan, Xingcheng Zhang, Xi"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2407.20018"
pdf: "papers/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey.pdf"
slug: "efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey"
tags: [training]
---

# Efficient Training of Large Language Models on Distributed Infrastructures: A Survey

> [!abstract] 摘要（原文）
> 1\. ✨ 本文全面综述了分布式 LLM 训练系统的最新进展，旨在解决大规模 LLM 训练在 Scalability, Efficiency 和 Reliability (SER) 方面的核心挑战。 2. ⚡️ 论文详细探讨了包括 Data, Tensor, Pipeline, Sequence 和 Expert 等多种 Hybrid Parallelism 策略，以及 Operator Optimization、Mixed-Precision Training、Memory Optimization 和 Communication Optimization 等关键技术，以提升训练效率。 3. 💾 此外，文章还深入分析了 LLM 训练的 Infrastructure (包括 AI Accelerators, Network 和 Storage) 设计、Job Scheduling 方法，并介绍了 Anomaly Detection 和 Checkpoint-based/Checkpoint-free Recovery 等 Fault Tolerance 机制以确保系统可靠性。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Efficient Training of Large Language Models on Distributed Infrastructures: A Survey Jiangfei Duan∗, Shuo Zhang∗, Zerui Wang∗, Lijuan Jiang, Wenwen Qu, Qinghao Hu, Guoteng Wang, Qizhen Weng, Hang Yan, Xingcheng Zhang, Xi
- **arXiv**: https://arxiv.org/abs/2407.20018
- **本地 PDF**: `papers/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey.pdf`
- **页数**: 42

## 图表（原文 caption + 页码）
_未检测到带 caption 的 figure_

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.2 `Suppose the input token vector is X = [x1, x2, · · · , xn].`
- p.2 `Attention(Q, K, V ) = softmax`
- p.18 `i = softmax(si) =`

## 相关论文

- [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] — Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core
- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] — MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs
- [[zero-memory-optimizations-toward-training-trillion-parameter-models]] — ZeRO: Memory Optimizations Toward Training Trillion Parameter Models

## 全文文本
全文已存 `extraction/fulltext/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey.txt`（271696 字符）供引用检索。