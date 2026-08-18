---
paper_num: "66"
title: "Huawei Cloud Model-as-a-Service on the CloudMatrix384 SuperPod"
authors: "SuperPod xDeepServe (XDS) Team @ Huawei"
date: "2025/8/4"
arxiv: "https://arxiv.org/abs/2508.02520"
pdf: "papers/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod.pdf"
slug: "huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod"
tags: []
---

# Huawei Cloud Model-as-a-Service on the CloudMatrix384 SuperPod

> [!abstract] 摘要（原文）
> Scaled-out MoE LLMs and scaled-up SuperPods create new systems challenges for production Model-as-a-Service (MaaS), requiring disaggregation, low-latency communication, and decentralized serving. This report presents xDeepServe, the production serving system behind Huawei Cloud's MaaS offering on CloudMatrix384, a 48-server SuperPod with 384 Ascend 910C chips connected by a high-bandwidth UB fabric and global shared memory. It serves models including DeepSeek, Kimi, GLM, Qwen, and MiniMax, among others. xDeepServe is built around Transformerless, a disaggregated execution architecture that decomposes transformer inference into modular units -- attention, feedforward, and MoE -- and supports disaggregated Prefill-Decode and MoE-Attention deployments. To enable disaggregation, we develop XCCL, a memory-semantic communication layer providing microsecond-level point-to-point and scalable all-to-all primitives, and we extend FlowServe with decentralized DP groups and techniques to mitigate stragglers and synchronization variance. In a peak decoding configuration, xDeepServe reaches 2400 tokens/s per Ascend 910C chip at ~50ms time-per-output-token (TPOT).

## 元信息
- **发表日期**: 2025/8/4
- **作者**: SuperPod xDeepServe (XDS) Team @ Huawei
- **arXiv**: https://arxiv.org/abs/2508.02520
- **本地 PDF**: `papers/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod.pdf`
- **页数**: 32

## 图表（原文 caption + 页码）

### Figure 2 (p.23)
![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p23.png]]
> [!quote] caption
> FlowServe selects the appropriate DistFlow [10] backend based on the network fabric. For MLA models like DeepSeek and Kimi K2, both interconnects satisfy TTFT and TPOT SLAs.

### Figure 4 (p.8)
![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p08.png]]
> [!quote] caption
> Step 1: The sender’s serving engine invokes XCCL’s send, passing the source buffer in the app data area (e.g., KV cache), an eventID (e.g., number of sends), the receiver NPU’s ID, and the number of AIV cores to use. XCCL launches a kernel on the sender NPU. The send kernel uses MTE2 to copy data from the app data area to each AIV’s unified buffer in parallel. Step 2: The send kernel then reads th

### Figure 8 (p.12)
![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p12.png]]
> [!quote] caption
> Trade-off between MTE and DMA. To improve communication efficiency, we employ NPU-Direct Unified Remote Memory Access (URMA), a technique on Ascend NPUs similar to IBGDA on GPUs [15]. NPU-Direct URMA enables AIV cores to issue remote memory access requests directly to the DMA engine, bypassing both the host CPU and AI CPU as shown in §2.2. Although NPU-Direct URMA incurs higher startup latency com

### Figure 10 (p.12)
![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p12.png]]
> [!quote] caption
> This redesign centers on three key components: • First, we introduce the Data Parallel (DP) group abstraction, inspired by SGLang [24].

### Figure 12 (p.16)
![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p16.png]]
> [!quote] caption
> Step 1: Collecting Expert Load Distribution. First, we collect data on expert loads across NPUs. We define expert load as the total number of tokens routed to each expert within a given time interval. Token count directly reflects both communication overhead (MoE-Dispatch and

### Figure 17 (p.22)
![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p22.png]]
> [!quote] caption
> 1. A request first arrives at a randomly selected Job Executor (JE), which assigns it to a prefill

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
h_{\ell,t} = \arg\max_{e} \text{ token\_count}[\ell][e][t].
$$

$$
L_\ell = \sum_{t\in T}\text{token\_count}[\ell][h_{\ell,t}][t].
$$

## 技术点深读（DEEP）

![[deep/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod.txt`（94761 字符）供引用检索。