---
paper_num: "45"
title: "Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving"
authors: "Architecture for LLM Serving Ruoyu Qin♠♡1 Zheming Li♠1 Weiran He♠ Mingxing Zhang♡2 Yongwei Wu♡ Weimin Zheng♡ Xinran Xu♠2 ♠Moonshot AI ♡Tsinghua University"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2407.00079"
pdf: "papers/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving.pdf"
slug: "mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving"
tags: [kv-cache, disaggregated-serving]
---

# Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving

> [!abstract] 摘要（原文）
> 1\. 🚀 Mooncake 是一种 KVCache-centric 的解耦架构，通过分离 Prefill 和 Decoding 集群并利用 GPU 集群中未充分利用的 CPU、DRAM 和 SSD 资源实现 KVCache 的分层缓存，旨在最大化有效吞吐量并满足服务水平目标 (SLO)。 2. 🧠 其核心在于 KVCache-centric 调度器，该调度器结合了 Chunked Pipeline Parallelism (CPP) 和分层 Prefill 等优化，以高效处理长上下文请求并实现 KVCache 热点迁移，同时采用预测驱动的早期拒绝策略以应对过载场景。 3. 📊 实验表明，Mooncake 在长上下文场景中性能卓越，相比基线方法可实现高达 525% 的吞吐量提升，在实际工作负载下能处理多 75% 的请求，同时严格遵守 TTFT 和 TBT 等性能 SLOs。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Architecture for LLM Serving Ruoyu Qin♠♡1 Zheming Li♠1 Weiran He♠ Mingxing Zhang♡2 Yongwei Wu♡ Weimin Zheng♡ Xinran Xu♠2 ♠Moonshot AI ♡Tsinghua University
- **arXiv**: https://arxiv.org/abs/2407.00079
- **本地 PDF**: `papers/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving.pdf`
- **页数**: 23

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p02.png]]
> [!quote] caption
> Mooncake Architecture. remote location will prolong the TTFT, and a large batch size will lead to a larger TBT. Thus, the utilization of both these throughput-oriented optimizations may lead to violations of latency-related SLOs.

> [!tip] 技术解读（多模态）
> # 论文核心架构图分析

## 1) 主要架构/组件/数据流描述

该图为 **Mooncake 架构图**，展示了一种以 KVCache 为中心的 LLM 服务解耦架构：

- **组件**：左侧为输入请求队列；中间区域包含多个 GPU 实例节点，分为 **prefill（预填充）节点**（上半部，含 KVCache 池 "3.450678"）和 **decoding（解码）节点**（下半部，含 KVCache 池）；中央为全局调度器（Conductor），负责调度决策。
- **数据流**：请求首先被路由到 prefill 节点；prefill 计算产生的 KVCache（图中上方柱状图表示）通过高速互联被流式传输到对应的 decoding 节点；decoding 节点加载 KVCache 后进行连续批处理生成输出（右侧生成的文本序列 "!\"#$%..."）。箭头与乘号 ⊗ 标示预填充与解码节点间的 KVCache 流转与匹配关系。

## 2) 关键技术要点

**基于 KVCache 的预填充-解码解耦（Disaggregation）：** 预填充（compute-bound）与解码（memory-bound）两种异构负载被分离到不同实例，KVCache 作为"一等公民"在实例间显式流转，全局 Conductor 综合考虑 TTFT/TBT SLO、KVCache 命中率、DRAM 容量与网络拥塞进行实例配对与调度优化，从而实现吞吐与时延的联合优化。

## 3) 图注逐字转录

> **Figure 1: Mooncake Architecture.**

### Figure 2 (p.4) ⭐深度解读
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p04.png]]
> [!quote] caption
> Normalized throughput and latency of prefill and decoding stages with different sequence lengths or batch sizes for the dummy LLaMA2-70B model. the computational complexity of attention networks scales quadratically with input length while the complexity of MLP scales linearly, computation time in the prefill stage generally increases superlinearly with input length, as shown in the left part of F

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】Mooncake 解耦式 KVCache 服务架构：prefill（compute-bound，注意力二次复杂度）与 decode（memory-bound，自回归批处理）分到独立节点池。核心是 disaggregated KVCache 层，池化 CPU/DRAM/SSD/RDMA 资源→跨节点 cache 复用、减冗余计算；调度器做 early rejection + SLO 准入(TTFT/TBT)+负载均衡。把计算阶段与 KVCache 存储解耦→弹性扩展、严 SLO 下更高吞吐。架构核心图。

### Figure 3 (p.5)
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p05.png]]
> [!quote] caption
> The KVCache pool in CPU memory. Each block is attached with a hash value determined by both its own hash and its prefix for deduplication.

### Figure 4 (p.6)
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]]
> [!quote] caption
> Workflow of inference instances. ( ) For prefill instances, the load and store operations of the KVCache layer are performed layer-by-layer and in parallel with the prefill computation to mitigate transmission overhead (see §5.2). (y ) For decoding instances, asynchronous loading is performed concurrently with GPU decoding to prevent GPU idle time. 4) Decoding: After all the KVCache is received i

### Figure 5 (p.6)
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]]
> [!quote] caption
> Input and output length distributions in the request trace. 4

### Figure 6 (p.7)
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p07.png]]
> [!quote] caption
> CDF (Cumulative Distribution

### Figure 7 (p.9)
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p09.png]]
> [!quote] caption
> Latency of storing KVCache of different request lengths (Layer-wise latency refers to the difference in latency between Layer-wise Prefill and Prefill without storing KVCache).

### Figure 8 (p.11)
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p11.png]]
> [!quote] caption
> The prefill scheduling experiment in the Mooncake cluster.

### Figure 9 (p.13)
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p13.png]]
> [!quote] caption
> The load of prefill and decoding instances over 20 minutes, before using the prediction- based early rejection.

### Figure 10 (p.14)
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p14.png]]
> [!quote] caption
> Instance load when applying Early Rejection and Early Rejection Based on Prediction. conditions where resources are scarce and accurate predictions are necessary, making request-level predictions particularly difficult.

### Figure 11 (p.16)
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]]
> [!quote] caption
> End-to-end experiments of Mooncake and vLLM on the ArXiv Summarization and L-Eval datasets instances. In real-world clusters, the demand for prefill and decoding instances generally remains stable over certain periods, with only minor temporary imbalances. Thus, the proportion of prefill and decoding instances can be preset. Future research will explore more flexible deployment and conversion meth

### Figure 12 (p.16)
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]]
> [!quote] caption
> End-to-end experiments of Mooncake and vLLM on simulated data.

### Figure 13 (p.17)
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p17.png]]
> [!quote] caption
> Request TTFT and TBT distributions of Mooncake and vLLM under real workloads

## 相关论文

- [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] — Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation
- [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] — SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills
- [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] — Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve
- [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] — A Survey on Large Language Model Acceleration based on KV Cache Management
- [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] — IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse

## 全文文本
全文已存 `extraction/fulltext/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving.txt`（81350 字符）供引用检索。