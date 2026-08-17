---
paper_num: "58"
title: "Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter"
authors: "Models Could Go Cross-Datacenter Ruoyu Qin1,2 Weiran He1 Yaoyu Wang1 Zheming Li1 Xinran Xu1 Yongwei Wu2 Weimin Zheng2 Mingxing Zhang2∗ 1Moonshot AI 2Tsinghua University"
date: "2026/4/16"
arxiv: "https://arxiv.org/abs/2604.15039"
pdf: "papers/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter.pdf"
slug: "prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter"
tags: [kv-cache]
---

# Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter

> [!abstract] 摘要（原文）
> Prefill-decode (PD) disaggregation has become the standard architecture for large-scale LLM serving, but in practice its deployment boundary is still determined by KVCache transfer. In conventional dense-attention models, prefill generates huge KVCache traffics that keep prefill and decode tightly coupled within a single high-bandwidth network domain, limiting heterogeneous deployment and resource elasticity. Recent hybrid-attention architectures substantially reduce KVCache size, making cross-cluster KVCache transport increasingly plausible. However, smaller KVCache alone does not make heterogeneous cross-datacenter PD serving practical: real workloads remain bursty, request lengths are highly skewed, prefix caches are unevenly distributed, and inter-cluster bandwidth fluctuates. A naive design that fully externalizes prefill can therefore still suffer from congestion, unstable queueing, and poor utilization. We present Prefill-as-a-Service (PrfaaS), a cross-datacenter serving architecture that selectively offloads long-context prefill to standalone, compute-dense prefill clusters and transfers the resulting KVCache over commodity Ethernet to local PD clusters for decode. Rather than treating reduced KVCache as sufficient, PrfaaS combines model-side KV efficiency with system-side selective offloading, bandwidth-aware scheduling, and cache-aware request placement. This design removes the requirement that heterogeneous accelerators share the same low-latency RDMA fabric, enabling independent scaling of prefill and decode capacity across loosely coupled clusters. In a case study using an internal 1T-parameter hybrid model, a PrfaaS-augmented heterogeneous deployment achieves 54% higher serving throughput and 64% lower P90 TTFT than a homogeneous PD baseline, with approximately 15% throughput gain at equal cost, while consuming only modest cross-datacenter bandwidth.

## 元信息
- **发表日期**: 2026/4/16
- **作者**: Models Could Go Cross-Datacenter Ruoyu Qin1,2 Weiran He1 Yaoyu Wang1 Zheming Li1 Xinran Xu1 Yongwei Wu2 Weimin Zheng2 Mingxing Zhang2∗ 1Moonshot AI 2Tsinghua University
- **arXiv**: https://arxiv.org/abs/2604.15039
- **本地 PDF**: `papers/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter.pdf`
- **页数**: 16

## 图表（原文 caption + 页码）

### Figure 1 (p.2)
![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p02.png]]
> [!quote] caption
> Comparison of two deployment paradigms for PD-disaggregated LLM serving.

### Figure 2 (p.4)
![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p04.png]]
> [!quote] caption
> KV throughput of MiniMax-M2.5 on an 8×H200 instance at various input lengths.

### Figure 3 (p.6) ⭐深度解读
![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p06.png]]
> [!quote] caption
> Deployment topology of the PrfaaS-PD architecture.

> [!tip] 技术解读（多模态）
> PrfaaS-PD 部署拓扑：Request Router 按长度阈值 t 分流——长请求 (l>t) 送独立 PrfaaS 集群（高算力 prefill 节点+集群内 RDMA），短请求留本地 PD 集群（高显存带宽）。PrfaaS 产出的 KVCache 经普通跨集群以太网传到本地 PD 集群 decode；两侧各挂 Hybrid Prefix Cache Pool（linear state 与 full-attention KV 分组、统一 block pool），Global KVCache Manager 全局协调。核心洞察：hybrid-attention 模型 KV 流量降一个数量级后（1T 模型 ~170Gbps、万卡总出口 ~1.8Tbps），跨数据中心 prefill 卸载在物理链路上首次可行。

### Figure 4 (p.7)
![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p07.png]]
> [!quote] caption
> Hybrid prefix cache pool. Linear states and full-attention KVCache are managed by separate groups backed by a unified block pool. Blocks are categorized as prefix-cache (intra-cluster only, block-aligned) or transfer-cache (cross-cluster, discarded after transfer). categories. Local PD clusters perform PD-disaggregated serving and can complete inference for a request end to end. PrfaaS clusters pr

### Figure 5 (p.11)
![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p11.png]]
> [!quote] caption
> Illustration of the grid search process for the two optimization variables. (a) fixes t at the optimum and searches over the prefill/decode instance split within the local PD cluster. (b) fixes

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\Phi_{\text{kv}}(l)=\frac{S_{\text{kv}}(l)}{T_{\text{prefill}}(l)},
$$

$$
B_{\text{out}} =\frac{N}{P}\cdot\frac{\mathbb{E}[S_{\text{kv}}]}{\mathbb{E}[T_{\text{prefill}}]} \approx\frac{N}{P}\cdot\Phi_{\text{kv}}(L_{\text{avg}}),
$$

$$
\Theta_{\text{\systemnamelowercase}} = \min\!\left(\frac{N_{\text{\systemnamelowercase}}}{T_{\text{prefill}}(l_{\text{long}})},\; \frac{B_{\text{out}}}{S_{\text{kv}}(l_{\text{long}})}\right).
$$

$$
\Theta_{\text{pd-p}} = \frac{N_p}{T_{\text{prefill}}(l_{\text{short}})}.
$$

$$
\Theta_{\text{pd-d}} = \frac{N_d \cdot \mathit{BS}_{\max}}{T_{\text{decode}} \cdot L_{\text{out}}},
$$

$$
\Lambda_{\max} = \min\!\left(\frac{\Theta_{\text{\systemnamelowercase}}}{p},\; \frac{\Theta_{\text{pd-p}}}{1 - p},\; \Theta_{\text{pd-d}}\right).
$$

$$
\frac{\Theta_{\text{\systemnamelowercase}}}{p} = \frac{\Theta_{\text{pd-p}}}{1 - p}.
$$

$$
\Theta_{\text{\systemnamelowercase}} + \Theta_{\text{pd-p}} = \Theta_{\text{pd-d}}.
$$

## 相关论文

- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] — IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse
- [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] — A Survey on Large Language Model Acceleration based on KV Cache Management

## 全文文本
全文已存 `extraction/fulltext/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter.txt`（58766 字符）供引用检索。