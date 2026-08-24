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
> 【图文联合解读】**图1解读**

图1对比PD分离LLM两种部署范式：左侧PrfaaS（Prefill-as-a-Service）专用集群配本地KV Store与Prefill节点，右侧本地PD集群含Standard/Decode节点及本地KV Store，二者经中间"跨数据中心KVCache传输层"（松耦合KV Transfer）连接，层内对比"Dense—Network Bound"（✗，因带宽受限被否）与"Hybrid—Prefill Bound"（✓，以Prefill为瓶颈而被选）两条路径，并由底部"基于以太网的跨集群KV Store"统一封装。

**论证结论**：Hybrid松耦合方案可克服跨数据中心带宽瓶颈，使KVCache可在集群间高效流转，从而实现PrfaaS多集群分离推理。

**全文作用**：作为方法论总图，引出后续对Hybrid传输、KV布局与跨集群调度的具体设计与实验。

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig02.png]]
*整页渲染: ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p04.png]]*
> [!quote] caption
> KV throughput of MiniMax-M2.5 on an 8×H200 instance at various input lengths.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1）核心数据：** 图以 MiniMax-M2.5 在 8×H200 实例上的实测呈现双轴关系——蓝柱为 KV 吞吐量(Gbps)、红线为 Prefill 延迟(s)，横轴为 prompt 长度(1K–128K)。吞吐量从 1K 的 ~5 Gbps 单调升至 64K 峰值 ~61 Gbps，128K 回落至 ~48 Gbps；延迟在 ≤32K 区间保持 <1.2 s，64K 升至 ~2.2 s，128K 陡增至 ~5.5 s。

**2）关键结论：** 长上下文 prefill 产生高达数十 Gbps 级别的 KV 流量，且在 128K 出现明显 **compute-bound 拐点**——吞吐量不升反降、延迟指数级攀升，证明长 prompt 的 prefill 是高算力开销单元，将其剥离至专用实例具备现实必要性。

**3）论文作用：** 为 "prefill-as-a-service / KV cache 跨数据中心传输" 的核心动机提供单实例 KV 带宽量化证据，论证解耦 prefill 与 decode 的工程价值。

### Figure 3 (p.6) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig03.png]]
*整页渲染: ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p06.png]]*
> [!quote] caption
> Deployment topology of the PrfaaS-PD architecture.

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图展示PrfaaS-PD部署拓扑：核心为Local PD Cluster（含Prefill与Decode两类节点，由Intra-Cluster RDMA Network高带宽互联，配套Hybrid Prefix Cache Pool），短请求(l≤t)本地直接处理；Global KVCache Manager经Inter-Cluster Ethernet跨集群统一调度。原文借此论证：PrfaaS-PD通过Prefill/Decode分离、RDMA+Ethernet分层网络与混合前缀缓存池，可支撑跨数据中心的KVCache传输。该图为后文跨机房KV吞吐实验（表3，8×H200，SGLang v0.5.9）提供系统部署前提与方法框架。

### Figure 4 (p.7) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig04.png]]
*整页渲染: ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p07.png]]*
> [!quote] caption
> Hybrid prefix cache pool. Linear states and full-attention KVCache are managed by separate groups backed by a unified block pool. Blocks are categorized as prefix-cache (intra-cluster only, block-aligned) or transfer-cache (cross-cluster, discarded after transfer). categories. Local PD clusters perform PD-disaggregated serving and can complete inference for a request end to end. PrfaaS clusters pr

> [!tip] 技术解读（多模态）
> 【图文联合解读】图4展示统一Hybrid Cache Pool：第3组Full Attention含8个块级KVCache单元；池中可见12块，其中5个粉色跨集群Transfer-Cache块、7个灰色空闲块。论文说明，线性状态与全注意力KVCache虽分组建管，却共享分块资源；前缀缓存仅集群内且按块对齐，传输缓存可跨集群任意长度并在使用后释放。该结构连接各PD集群的prefill/decode链路，为跨数据中心KV传输、资源隔离及统一池调度提供架构基础，并非结果指标图。

### Figure 5 (p.11) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig05.png]]
*整页渲染: ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p11.png]]*
> [!quote] caption
> Illustration of the grid search process for the two optimization variables. (a) fixes t at the optimum and searches over the prefill/decode instance split within the local PD cluster. (b) fixes

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图(a)** 展示本地 PD 集群内 prefill/decode 实例分配（固定 Np+Nd=8）的吞吐量网格扫描：下 x 轴 Np∈[1,7]、上 x 轴 Nd∈[7,1]，纵轴 Λ_max(req/s)。红线 Prefill bound 在 Np=1→3 单调上升至 3.24，绿线 Decode bound 在 Np=4→7 单调下降至 ~0.8，二者在最优点 ★Np=3、Nd=5 交汇。附表量化 1K/8K/32K/128K 序列对应 KVCache 为 190.8/308.9/701.3/2316.3 MiB。

**关键结论**：总实例数受限时，prefill 与 decode 实例存在唯一最优配比——prefill 过多受 prefill 吞吐上界制约，decode 过多受 decode 上界制约，形成"V 形"包络。

**论文作用**：与图(b)固定 Np=3、Nd=5 扫描传输时间 t 配合，构成两变量优化的两阶段网格搜索，为跨数据中心 KVCache 共享方案的实例/带宽联合部署决策提供量化依据。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.3) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-tab01.png]]
> [!quote] caption
> Configurations of representative models. Type A denotes the linear-complexity block, and Type B denotes the quadratic-complexity full attention block.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 1 罗列 6 个代表性 LLM 的注意力结构与参数量：Kimi Linear（48B，KDA+MLA，3:1）、MiMo-V2-Flash（309B，SWA+GQA，5:1）、Qwen3.5-397B（GDN+GQA，3:1）、Ring-2.5-1T（Lightning+MLA，7:1）均采用线性块 A 与二次方块 B 混合，A:B 介于 3:1–7:1；而 MiniMax-M2.5（229B）与 Qwen3-235B（235B）仍为纯 GQA。原文据此论证：下一代大模型正普遍引入线性复杂度注意力块，使 KV cache 访存模式规则化、prefill 计算可批量预测，跨数据中心搬运 cache 因此具备可行性。该表为论文"prefill-as-a-service、KV cache 跨 DC 调度"的核心方案提供了模型结构层面的现实依据。

### Table 3 (p.4) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-tab03.png]]
> [!quote] caption
> KV throughput Φ kv (Gbps) at various input lengths. All models are benchmarked on 8 × H200 with SGLang v0.5.9 [7].

> [!tip] 表格解读（多模态）
> 【图文联合解读】表3量化了6个模型在1K/8K/32K/128K四种序列长度下的KV吞吐Φ_kv（Gbps），分Hybrid（Kimi Linear、MiMo-V2-Flash、Qwen3.5-397B、Ring-2.5-1T）与Dense两组对比。关键发现：（1）Hybrid吞吐整体显著低于Dense——32K时Ring-2.5-1T仅2.59、Qwen3.5-397B为8.25 Gbps，而同长度Dense模型达33–60 Gbps，量级差近一个数量级；（2）Dense吞吐随序列长度呈"先升后降"，32K达峰、128K回落；（3）Ring-2.5-1T呈反常递减趋势（1K的7.27→128K的1.46）。

该表支撑论文核心论点：下一代大模型的KV cache传输吞吐受限、长上下文场景尤甚，凸显Figure 3所示跨数据中心PrfaaS-PD分离架构的必要性，为"KV cache可跨DC传输"的关键论断提供量化依据。

### Table 5 (p.11) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-tab05.png]]
> [!quote] caption
> KVCache size S kv , prefill latency T prefill , and KV throughput Φ kv of the internal 1T hybrid model at various input lengths. Prefill latency is benchmarked on 8 × H200 with in-house vLLM [ 28 ].

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 联合解读**

1) **核心数据**：内部 1T 混合模型在 4 种输入长度（1K/8K/32K/128K）下的 KVCache 体积分别为 190.8/308.9/701.3/2316.3 MiB，预填充时延 0.44/0.72/1.84/7.40 s，KV 吞吐 3.61/3.59/3.19/2.62 Gbps。

2) **关键结论**：随序列长度增长，KVCache 呈超线性膨胀（1K→128K 约 12×），预填充时延近 17× 跃升，而 KV 吞吐反而下降至 2.62 Gbps——单条 KVCache 即逼近甚至超过典型跨数据中心专线带宽，为论文"1T 级模型 KVCache 必须跨 DC 传输"提供量化依据。

3) **方法链作用**：作为后文 Figure 5 网格搜索的输入参数，固定模型侧 KV 体积与生成速率，为 PD 拆分、跨 DC 调度等优化变量提供基准工作负载。

### Table 6 (p.12) ⭐深度解读
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-tab06.png]]
> [!quote] caption
> Comparison of optimal configurations across PrfaaS-PD, homogeneous PD, and naive heterogeneous PD deployments.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 图文联合解读**

**1）核心数据**：对比 PrfaaS-PD、Homogeneous PD、Naive Heterogeneous PD 三种部署的最优配置。PrfaaS-PD 取阈值 t=19.4K，实例池 N=4/3/5，TTFT 均值/P90 为 2.22/3.51 s，三阶段服务率 Θ=1.61/1.64/3.91 req/s，Λ_max=3.24 req/s；Homogeneous PD（9/3 实例）Λ_max 仅 2.11；Naive Heterogeneous（4/—/8）TTFT 最低（1.74 s）但 Λ_max 仅 2.45。归一化吞吐比 1.54× / 1.00× / 1.16×。

**2）关键结论**：PrfaaS-PD 以 1.54× 显著优于传统 Homogeneous PD，且比 Naive Heterogeneous PD（1.16×）多 33% 吞吐，证明显式分离跨数据中心 PrfaaS 实例池的必要性——单靠阶段异构部署增益有限。

**3）论文作用**：作为方法核心实验的"压轴定量证据"，支撑"PrfaaS 跨数据中心共享 KV-cache"主线，论证新架构在 SLO 满足下的容量优势。

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