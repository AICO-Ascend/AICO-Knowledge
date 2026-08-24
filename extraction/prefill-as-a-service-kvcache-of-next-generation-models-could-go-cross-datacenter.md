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

### Figure 1 (p.2) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig01.png]]
*整页渲染: ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p02.png]]*
> [!quote] caption
> Comparison of two deployment paradigms for PD-disaggregated LLM serving.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

图1对比PD分离LLM推理的两种部署范式。**(a)现状**：单同构集群内Prefill与Decode经各自KV Store，通过"Tightly Coupled KV Transfer"紧耦合传输，底层为RDMA单集群KV存储。**(b)PrfaaS**：PrfaaS集群（Prefill专用+本地KV）与本地PD集群（Decode+本地KV）通过以太网跨集群KV存储松耦合传输；传输层给出两种策略——**Dense**（全量KV、Network Bound、✗不可行）与**Hybrid**（按Prefill块粒度、Prefill Bound、✓可行）。

**论证结论**：随下一代模型KV Cache规模爆炸，RDMA紧耦合方案难以扩展；PrfaaS利用Hybrid策略将传输受限于计算侧（Prefill-bound）而非网络带宽，使跨数据中心KVCache复用成为可能。

**作用**：作为全文核心动机图，奠定"为何需跨数据中心PrfaaS"前提，并衔接Table 1模型配置与后续PrfaaS系统设计/实验链路。

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig02.png]]
*整页渲染: ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p04.png]]*
> [!quote] caption
> KV throughput of MiniMax-M2.5 on an 8×H200 instance at various input lengths.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图左半部展示MiniMax-M2.5在8×H200上、prompt长度1K–128K时的KV吞吐（蓝柱）与prefill延迟（红折线）：吞吐由约5 Gbps升至64K峰值约61 Gbps，128K回落至约48 Gbps；延迟由约0.3 s超线性增长至约5.5 s。右表对比GQA/MLA/Sparse/SWA/Linear Attention五类注意力机制的prefill延迟与KV吞吐高低。

原文据此论证：长上下文prefill产生的KV cache传输已达数十Gbps量级，延迟随长度急剧放大，且不同注意力机制在吞吐/延迟上取舍各异——从而支撑"跨数据中心传输KV cache将成为下一代模型prefill服务瓶颈"这一核心论点，为Prefill-as-a-Service方案提供量化依据与机制选型参考。

### Figure 3 (p.6) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig03.png]]
*整页渲染: ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p06.png]]*
> [!quote] caption
> Deployment topology of the PrfaaS-PD architecture.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示PrfaaS-PD双集群部署拓扑：Request Router按阈值t分流请求——长请求(l>t)送PrfaaS集群的Prefill节点（标"高计算吞吐"），短请求(l≤t)送Local PD集群的Decode节点（标"高内存带宽"）。两集群各含三层子系统：Compute层为PD节点、Network层为Intra-Cluster RDMA Network、Storage层为Hybrid Prefix Cache Pool；二者经Cross-Cluster Ethernet互联，并由Global KVCache Manager跨集群统一调度。原文借此论证：PD分离+RDMA/Ethernet分层网络+混合前缀缓存池三层协同，可支撑跨数据中心KVCache传输。该图作为后文跨机房KV吞吐实验（表3，8×H200，SGLang v0.5.9）的系统部署前提与方法框架。

### Figure 4 (p.7) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig04.png]]
*整页渲染: ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p07.png]]*
> [!quote] caption
> Hybrid prefix cache pool. Linear states and full-attention KVCache are managed by separate groups backed by a unified block pool. Blocks are categorized as prefix-cache (intra-cluster only, block-aligned) or transfer-cache (cross-cluster, discarded after transfer). categories. Local PD clusters perform PD-disaggregated serving and can complete inference for a request end to end. PrfaaS clusters pr

> [!tip] 技术解读（多模态）
> 【图文联合解读】**1) 核心对象与结构**：图示统一混合缓存池（Unified Hybrid Cache Pool），Linear Attention Group（请求级循环态，3对块）与Full Attention Group（块级KVCache，约7–8个半填块）通过Group 0–3四条通道向池子Allocate/Free；池内块按用途分三类——Prefix-Cache（紫色，可复用、块对齐）、Transfer-Cache（红色，跨簇、任意长度）、Free（灰色），全注意力侧可见明显的半填碎片块。

**2) 论证结论**：异构注意力模型的两类状态可在同一存储后端上共存，并通过"簇内复用 vs 跨簇一次性传输"语义分类隔离，从而统一管理。

**3) 论文链路作用**：该池是PrfaaS调度框架的基础设施抽象层，使本地PD集群与跨集群预填池能在同一资源池内协同分配，为跨数据中心KVCache调度提供底层支撑。

### Figure 5 (p.11) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig05.png]]
*整页渲染: ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p11.png]]*
> [!quote] caption
> Illustration of the grid search process for the two optimization variables. (a) fixes t at the optimum and searches over the prefill/decode instance split within the local PD cluster. (b) fixes

> [!tip] 技术解读（多模态）
> 【图文联合解读】图及实测表：1K/8K/32K/128K序列的KVCache为190.8/308.9/701.3/2316.3 MiB，预填充0.44/0.72/1.84/7.40 s，KV吞吐3.61/3.59/3.19/2.62 Gbps。固定最优t≈19.4K，在Nₚ+N_d=8下搜索，得Nₚ=3、N_d=5时Λmax=3.24 req/s；固定配比扫描t，峰值不变。该实测驱动两阶段网格搜索，连接PD资源分配与跨机房/本地路由优化，确定PaaS配置。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.3) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-tab01.png]]
> [!quote] caption
> Configurations of representative models. Type A denotes the linear-complexity block, and Type B denotes the quadratic-complexity full attention block.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 解读**

1) **核心数据**：表格列出 6 个代表性模型的两类注意力配置——Type A（线性复杂度块）与 Type B（二次复杂度全注意力），并给出混合比 A:B 及参数规模。关键数据点：Kimi Linear (KDA+MLA, 3:1, 48B)、MiMo-V2-Flash (SWA+GQA, 5:1, 309B)、Qwen3.5-397B (GDN+GQA, 3:1, 397B)、Ring-2.5-1T (Lightning+MLA, 7:1, 1T)；MiniMax-M2.5 与 Qwen3-235B 为纯 GQA 全注意力。

2) **论证结论**：下一代大模型（48B–1T）普遍采用"线性注意力+全注意力"混合架构，且混合比集中于 3:1–7:1，混合已成主流趋势，纯二次全注意力只在较小旧模型中出现。

3) **在论文中的作用**：作为问题动机的现实依据，支撑后续"prefill-as-a-service 跨数据中心"的论证——混合注意力带来线性 KV 局部化与全注意力全局 KV 截然不同的访问/传输模式，使跨数据中心 KV cache 复用成为新瓶颈，从而引出对混合模型 PD 解聚服务的设计需求。

### Table 3 (p.4) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-tab03.png]]
> [!quote] caption
> KV throughput Φ kv (Gbps) at various input lengths. All models are benchmarked on 8 × H200 with SGLang v0.5.9 [7].

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读**

该表展示8×H200+SGLang v0.5.9环境下，Hybrid（Kimi Linear、MiMo-V2-Flash、Qwen3.5-397B、Ring-2.5-1T）与Dense（MiniMax-M2.5、Qwen3-235B）共6个模型在1K/8K/32K/128K四种输入长度下的KV吞吐Φ_kv（Gbps）。

**核心数据对比**：Dense模型吞吐显著高于Hybrid，MiniMax-M2.5在32K达峰值59.93 Gbps、Qwen3-235B达33.35 Gbps；而Hybrid模型多停留在1–8 Gbps区间，Ring-2.5-1T更随序列增长从7.27降至1.46 Gbps，呈反相关趋势。

**技术结论**：该表定量证明下一代大模型（尤其Hybrid MoE）单卡/单实例KVCache吞吐有限，跨数据中心传输将成瓶颈。

**论文作用**：与Figure 3部署拓扑呼应，为PrfaaS-PD提出"Prefill/Decode分离+RDMA与Ethernet分层互联+混合前缀缓存池"提供关键带宽实测依据，支撑全文"跨机房KVCache调度"的核心理论与系统设计。

### Table 5 (p.11) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-tab05.png]]
> [!quote] caption
> KVCache size S kv , prefill latency T prefill , and KV throughput Φ kv of the internal 1T hybrid model at various input lengths. Prefill latency is benchmarked on 8 × H200 with in-house vLLM [ 28 ].

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心对象与数据**：表给出 1T 混合模型在 1K/8K/32K/128K 输入下的三项实测——KVCache 大小 S_kv 从 190.8 MiB 单调升至 2316.3 MiB（约 12×）；prefill 延迟 T_prefill 由 0.44 s 升至 7.40 s，呈超线性增长（≈17×）；KV 吞吐 Φ_kv 由 3.61 Gbps 降至 2.62 Gbps，长序列下传输效率明显下滑。

**论证结论**：长序列 KVCache 体积庞大、prefill 计算昂贵，使跨数据中心传输 KV 比本地重算更划算；Φ_kv 随序列增长下降进一步表明，长上下文场景正是跨 DC 方案的优势区间。

**论文链路作用**：为后续成本模型提供 S_kv、Φ_kv 的硬件基线输入，直接决定跨 DC vs. 本地 prefill 的临界距离 t*，是支撑"prefill-as-a-service"经济性论证的关键实测依据。

### Table 6 (p.12) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-tab06.png]]
> [!quote] caption
> Comparison of optimal configurations across PrfaaS-PD, homogeneous PD, and naive heterogeneous PD deployments.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表横向对比三种部署的最优配置：PrfaaS-PD（4/3/5拆分）、同构PD（0/9/3）、朴素异构PD（4/—/8）。关键数据：PrfaaS-PD以阈值 t=19.4K 划分跨域流量，最大吞吐量 Λ_max=3.24 req/s，达同构PD（2.11）的1.54×、朴素异构PD（2.45）的1.32×；TTFT均值2.22s、P90为3.51s，均显著优于同构PD（4.44/9.73s）。

原文借此论证：跨数据中心承载prefill-as-a-service能更精细地拆分prefill与decode节点配比，使受限资源（prefill）利用率提升，从而突破单DC内的负载均衡瓶颈；且相对仅做节点角色分离的朴素异构PD仍多获32%吞吐增益，证明**跨域KV cache传输**是增益的关键来源，而非单纯的PD解耦。

该表作为论文核心实验结论，量化支撑了"下一代模型KV cache须跨DC"的主张，是PrfaaS-PD调度策略有效性的最终验证节点。

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
- [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] — KV Cache Optimization Strategies for Scalable and Efficient LLM Inference
- [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] — CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion

## 技术点深读（DEEP）

![[deep/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter.txt`（58766 字符）供引用检索。