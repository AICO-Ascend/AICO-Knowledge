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
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig01.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p02.png]]*
> [!quote] caption
> Mooncake Architecture. remote location will prolong the TTFT, and a large batch size will lead to a larger TBT. Thus, the utilization of both these throughput-oriented optimizations may lead to violations of latency-related SLOs.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示Mooncake架构：左侧KVCache-centric Conductor含三调度器（Cache-aware Prefill Scheduler、KVCache Balance Scheduler、Load-balance Decoding Scheduler）；纵向分三层资源池——Prefill Pool（GPU/VRAM+本地分块预fill+分页KVCache）、KVCache Pool（CPU/DRAM/SSD分布式KVCache）、Decoding Pool（GPU/VRAM+分页KVCache），节点间以RDMA传输KVCache、Prefill节点间用PP/SP通信。右侧明示两阶段优化目标：Prefill max Cache Reuse受TTFT SLO、最低MFU、KVCache<DRAM约束；Decoding max Throughput受TBT SLO、KVCache<VRAM约束。

技术结论：解耦prefill/decoding并将KVCache显式提升为一等公民资源，通过分布式RDMA池化跨节点复用cache，从而兼顾延迟SLO与吞吐。

作用：全文方法总览图，奠定后续调度器设计与Table 1缓存命中率实验的分析框架。

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig02.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p04.png]]*
> [!quote] caption
> Normalized throughput and latency of prefill and decoding stages with different sequence lengths or batch sizes for the dummy LLaMA2-70B model. the computational complexity of attention networks scales quadratically with input length while the complexity of MLP scales linearly, computation time in the prefill stage generally increases superlinearly with input length, as shown in the left part of F

> [!tip] 技术解读（多模态）
> 【图文联合解读】## 图2（右半·解码阶段）联合解读

**核心数据**：横轴为 Batch Size 1–16（序列长度固定 8k）。绿色柱（归一化吞吐量）从约 0.07 近似线性增长至 1.0；红色折线（解码延迟）几乎平稳，仅在 Batch 15–16 处轻微上扬至 1.0。

**论证结论**：解码阶段吞吐随 batch 近似线性放大，而延迟几乎不增长——这是「**解码高 batch 友好**」的关键实测证据。结合左半图 prefill 阶段计算量随序列长度超线性增长的事实，作者论证 prefill 与 decode 具有截然不同的扩缩特性。

**论文作用**：作为 Mooncake 提出 **prefill/decode 分离架构（disaggregation）** 的核心动机支撑——将计算密集、低延迟敏感的 prefill 与可大批并行、可吞吐优先的 decode 解耦部署，由 KVCache-centric 调度器协同，才能同时兼顾吞吐与 SLO。

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig03.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p05.png]]*
> [!quote] caption
> The KVCache pool in CPU memory. Each block is attached with a hash value determined by both its own hash and its prefix for deduplication.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图3联合解读（≤220字）**

① **核心对象与结构**：展示CPU内存中的KVCache池，含9个Token块(a–i)。每个块采用**链式哈希**：A=Hash(a)、B=Hash(A+b)、…、F=Hash(E+f)，哈希值由自身内容与前缀哈希共同决定。三色分类：黄色=前缀缓存块、粉色=增量缓存块、灰色=未分配块。

② **关键技术结论**：示例中a–e五个前缀块全部Match✓复用，f处Mismatch✗触发失配；增量块F–I(粉色)被新计算并写入新位置。证明链式哈希+块粒度可实现**精确前缀去重**，避免整请求重复计算前缀KVCache。

③ **论文整体作用**：该池是Mooncake解耦架构的存储底层，通过Prefill Instance→Messenger→Decoding Instance间的Load/Store/Transfer/Write/Read五路径实现跨实例KVCache流转，为后续Prefix Caching复用与Early Rejection（表3所示过载场景拒请求）提供基础设施支撑。

### Figure 4 (p.6) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig04.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]]*
> [!quote] caption
> Workflow of inference instances. ( ) For prefill instances, the load and store operations of the KVCache layer are performed layer-by-layer and in parallel with the prefill computation to mitigate transmission overhead (see §5.2). (y ) For decoding instances, asynchronous loading is performed concurrently with GPU decoding to prevent GPU idle time. 4) Decoding: After all the KVCache is received i

> [!tip] 技术解读（多模态）
> 【图文联合解读】图分两栏：左为Prefill实例，含CPU/GPU双层，按Prefix与Incremental KVCache分块；右为Decoding实例，含Full KVCache。流程含s1前缀复用、s2增量prefill、s3跨实例KVCache传输、s4解码四个步骤。Prefill侧(∗)逐层Load/Store与计算并行，隐藏传输开销；Decoding侧(†)异步加载与GPU解码重叠，避免GPU空泡。该图论证Mooncake分离架构"计算与传输并发"的核心优化设计，是KVCache中心化方法论的关键图示。

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig05.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]]*
> [!quote] caption
> Input and output length distributions in the request trace. 4

> [!tip] 技术解读（多模态）
> 【图文联合解读】图5展示请求trace的输入（蓝）与输出（绿）长度分布，频率为log刻度。**输入高度右偏**：峰值集中于0–5k tokens（~10⁴），但长尾延伸至120k+，跨度达4个数量级；**输出近似双峰**：主峰在300–500 tokens（~10³），次峰近2000，最大约2100。

**关键论证**：实际负载中输入长度极端异构——长输入使prefill阶段产生巨大KV cache却仅生成少量token，与decode阶段轻量增量KV形成严重的内存–计算失衡；而输出相对短且有界，prefill/decode资源需求极不对称。

**论文作用**：此图为后续"以KVCache为中心的prefill–decode解耦架构"提供数据驱动的动机支撑，是Mooncake分离式设计合理性的关键实证基础，也为调度策略与cache复用讨论奠定前提。

### Figure 6 (p.7) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig06.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p07.png]]*
> [!quote] caption
> CDF (Cumulative Distribution

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 6）**

1) **图示数据**：横轴 Block Hit Count（对数刻度 1–10⁴），纵轴 CDF。约 55% 的块命中次数=1，约 77% ≤2 次，约 95% ≤10 次；命中≥10² 的块占比可忽略，最大值延伸至 ~10⁴ 但概率极小。整体呈极度长尾分布。

2) **关键结论**：少量"热门"块承担绝大多数重用请求，证实 LLM 请求间 KV cache 复用潜力大、冗余重计算成本高，从而为"以 KV cache 为中心"的设计提供量化依据。

3) **论文作用**：支撑 Mooncake 的核心动机——将 prefill 计算与 KV cache 存储解耦、池化共享，使小部分热块可被多次复用，显著降低 prefix 重算开销。

### Figure 7 (p.9) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig07.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p09.png]]*
> [!quote] caption
> Latency of storing KVCache of different request lengths (Layer-wise latency refers to the difference in latency between Layer-wise Prefill and Prefill without storing KVCache).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图7联合解读**

图7对比两种KVCache存储策略（Serialized序列化 vs Layer-wise分层）在不同请求长度（8K–128K）下的存储延迟。量化数据：Serialized延迟近似线性增长（8K约0.11s→128K约0.86s）；Layer-wise全程稳定在约0.10s，128K时仅为Serialized的~1/8.6。

**关键结论**：原文借此论证"分层并发存储KVCache"可消除长序列下存储开销的线性放大，是Mooncake采用Transformer层间流水线调度、并把prefill计算与KVCache写入重叠的核心实验依据，支撑其长上下文场景下的高吞吐设计。

### Figure 8 (p.11) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig08.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p11.png]]*
> [!quote] caption
> The prefill scheduling experiment in the Mooncake cluster.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图为箱线图，纵轴为TTFT（秒），含一条约30秒的SLO虚线。横轴对比四种调度策略：

1. **核心数据**：KVCache-centric中位数约7–8s，分布极紧凑，远低于SLO；cache-aware中位数约18s，仅少量离群点；load-balancing均值89.41s、箱体伸至~105s，须线达~220s；random均值92.92s、箱体最高~150s、须线逼近285s。

2. **关键结论**：论文提出的KVCache-centric调度策略TTFT最低且稳定，证明以KVCache为中心的调度远优于负载均衡与随机策略，能稳定满足SLO；而load-balancing和random因忽略cache局部性，导致大量长尾延迟。

3. **链路作用**：作为消融/对比实验，量化验证核心调度设计（KVCache-centric）的有效性，支撑论文"以KVCache为中心"这一核心架构主张。

### Figure 9 (p.13) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig09.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p13.png]]*
> [!quote] caption
> The load of prefill and decoding instances over 20 minutes, before using the prediction- based early rejection.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) 图示20分钟窗口内 prefill（绿线）与 decoding（黄线）实例的负载率随时间变化曲线，y 轴负载范围约 10%–95%。两条曲线呈明显**反相位**：prefill 飙升时 decoding 多处低位，反之亦然，且 prefill 振幅显著更大，深谷多次逼近底部。

2) 原文借此论证：在未启用基于预测的 early rejection 机制之前，解耦架构下 prefill 与 decoding 节点负载严重不均衡、波动剧烈，暴露出传统调度难以稳定 SLO 的缺陷，从而为引入**预测式早拒**以均衡负载提供动机。

3) 该图作为**对比基线**，与后续启用 early rejection 后的负载曲线（图10/11）形成对照，串联起"暴露问题 → 提出方案 → 实验验证"的完整论证链，是 Mooncake 调度策略章节的关键支撑。

### Figure 10 (p.14) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig10.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p14.png]]*
> [!quote] caption
> Instance load when applying Early Rejection and Early Rejection Based on Prediction. conditions where resources are scarce and accurate predictions are necessary, making request-level predictions particularly difficult.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**核心对象与数据**：图分上下两行4个Stage，沿时间轴展示实例**解码负载（上，橙）与预填充负载（下，蓝）**的动态变化。Stage1解码≈0.15（低）/预填充≈0.95（高，新请求密）→Accept；Stage2解码≈0.8（高）/预填充≈0.15（低）→Reject；Stage3再次解码≈0.15/预填充≈0.8→Accept；Stage4解码≈0.6/预填充≈0.3→Reject。曲线连接呈现"高-低"振荡。

2）**关键结论**：早期拒绝依据预测的解码负载阈值（≈0.6，橙色虚线）切换Accept/Reject，避免预填充过载溢出，同时印证原文"资源稀缺、需精确预测时，请求级预测尤为困难"——单纯看当前预填充会误判（Stage2本应Reject时预填充低），必须预测解码端未来负载。

3）**方法链作用**：该图为Mooncake**过载预测与早期拒绝策略**提供可视化依据，是调度器在Prefill/Decode解耦架构中保护KVCache节点不被预填冲击的关键决策环节。

### Figure 11 (p.16) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig11.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]]*
> [!quote] caption
> End-to-end experiments of Mooncake and vLLM on the ArXiv Summarization and L-Eval datasets instances. In real-world clusters, the demand for prefill and decoding instances generally remains stable over certain periods, with only minor temporary imbalances. Thus, the proportion of prefill and decoding instances can be preset. Future research will explore more flexible deployment and conversion meth

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图呈现2×2网格中的L-Eval列（ArXiv列未显示）：横轴为请求速率（0.25–2.0 req/s），纵轴为归一化P90 TTFT（上）与P90 TBT（下），虚线1.0为SLO阈值；蓝、红、橙三曲线分别对应Mooncake与两种vLLM基线。TTFT图中，Mooncake在1.5 req/s前维持在0.1–0.3，至~2.0才破线；基线分别在1.25与1.5处即触线。TBT图中，Mooncake与红色基线先后在~1.0与~0.75 req/s突破SLO，而橙色基线始终平坦于~0.2–0.3。

原文借此论证：解耦架构在端到端长文本场景中显著提升SLO吞吐上限，TTFT增益尤为突出；该图为论文整体方法链路的"系统级压测"收尾，呼应§3.2调度与KV缓存传输设计，并以真实基准数据支撑"以KV Cache为中心"的可行性结论。

### Figure 12 (p.16) ⭐深度解读
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]]
> [!quote] caption
> End-to-end experiments of Mooncake and vLLM on simulated data.

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

Figure 11 presents a 2×2 grid of end-to-end performance benchmarks comparing Mooncake against vLLM variants on two long-context datasets (ArXiv Summarization, L-Eval). The top row plots normalized P90 TTFT (Time To First Token) versus request rate, while the bottom row plots normalized P90 TBT (Time Between Tokens). Three series are compared: Mooncake-[3P+1D] (blue) plus two baseline configurations (red, orange). Across all four panels, Mooncake's disaggregated architecture sustains lower latency values at substantially higher request rates before saturating the SLO thresholds (dashed lines at 1.0). The bottom-row TBT curves particularly show Mooncake flattening near ~0.5 while baselines climb toward violation.

**Key takeaway:** Mooncake's prefill–decode disaggregation decouples TTFT from TBT bottlenecks, enabling 2–3× higher sustainable request rates under identical SLOs.

**Verbatim caption:**

Figure 11: End-to-end experiments of Mooncake and vLLM on the ArXiv Summarization and L-Eval datasets

### Figure 13 (p.17) ⭐深度解读
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p17.png]]
> [!quote] caption
> Request TTFT and TBT distributions of Mooncake and vLLM under real workloads

> [!tip] 技术解读（多模态）
> # Figure 13 Description

**Note:** The figure itself (CDF plots) is not visible in the rendered page — only its caption appears. The description below is reconstructed from the caption and accompanying text in §8.1.3.

## Architecture / Components / Data Flow

Figure 13 is a **two-panel CDF plot** comparing request-level latency distributions between two serving stacks on identical real-world traces:

- **Mooncake-[10P+10D]** — 10 prefill instances + 10 decoding instances (disaggregated prefill/decode).
- **vLLM-[20M]** — 20 monolithic instances.
- **Left panel:** TTFT (Time To First Token) CDF, with an SLO threshold at **30 s**.
- **Right panel:** per-token TBT (Time Between Tokens) CDF, capped at **0.1 s/token**.
- **Data flow:** replayed production request traces → dispatched to either Mooncake's prefill→decode pipeline or vLLM's integrated engine → per-request TTFT and TBT samples → empirical CDF curves.

## Key Technical Takeaway

TTFT compliance is near-identical (~100%) for both systems, but **TBT SLO adherence diverges sharply**: Mooncake satisfies it for ~100% of requests vs. **only 57% for vLLM**, allowing Mooncake to serve ~75% more requests under the same SLOs.

## Caption (verbatim)

> Figure 13: Request TTFT and TBT distributions of Mooncake and vLLM under real workloads

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.8) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-tab01.png]]
> [!quote] caption
> Cache hit rates under different cache policies and capacities.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文联合解读：**

表1对比LRUCache、LFUCache、LengthAwareCache三种策略在6种block容量（Inf、100000、50000、30000、10000、1000）下的命中率。数据量化显示：无限容量时三者均仅约0.51；容量缩至1000时统一跌至0.30；LRU在中段容量（30000/10000）略优于LFU（0.48/0.40 vs 0.43/0.35）与LengthAware（0.42/0.35），其余容量下三者差距均≤0.03。

论文借此论证关键结论：LLM真实负载下，KVCache命中率天然存在约51%的上限，传统淘汰策略收益微弱且差异不显著，说明**单实例缓存远远不足以复用prefix token**。因此必须借助跨实例共享来突破容量瓶颈，这直接支撑了Mooncake"以KVCache为中心、prefill与decode解耦"的核心架构：全局Store层汇聚多实例缓存、Early-rejection调度器挑选高复用价值请求，使得长上下文请求能复用远端prefix KVCache、显著降低TTFT，构成其区别于传统vLLM/Tensor Parallel-Serve的差异化设计基础。

### Table 2 (p.15) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-tab02.png]]
> [!quote] caption
> Datasets used in the end-to-end experiment.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表列出4类端到端实验数据集的量化参数：ArXiv Summarization（输入8088/输出229，缓存命中率~0%）、L-Eval（19019/72，>80%）、Simulated Data（输入16k–128k/输出512，50%）和Real Data（7955/194，~50%），到达模式分别为泊松过程或时间戳驱动。

该表用以论证Mooncake架构需适配**多样化负载**：覆盖长输入（最长128k）、长输出（512）、近零与高命中率（0%→>80%）以及不同请求到达模式，体现KVCache-centric解耦架构对上下文缓存复用与吞吐优化的普适性。

在论文链路中，它是端到端实验前的**场景定义**，为后续吞吐、延迟、SLO达成率等性能评估提供可对比、可复现的测试基准。

### Table 3 (p.17) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-tab03.png]]
> [!quote] caption
> Number of requests rejected by the system under the overloaded-scenario experiment.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 解读**

1) **对象与数据**：该表量化过载场景下三种策略的拒绝量——Baseline 4183、Early Rejection 3771、Early Rejection based on Prediction 3589，呈单调递减。

2) **论证结论**：表说明仅靠早期拒绝已降低约10%被拒请求；叠加负载预测后进一步降至3589（较Baseline降幅≈14%），证明早拒绝+负载预测策略能显著减少过载下被系统拒之门外的高负载请求。

3) **链路作用**：作为Mooncake"预测–早拒绝–调度"前端机制的实验锚点，与吞吐/时延指标互补，量化验证了KVCache-centric架构在高压负载下的鲁棒性与请求接纳能力。

## 相关论文

- [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] — KV Cache Optimization Strategies for Scalable and Efficient LLM Inference
- [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] — CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion
- [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] — Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation
- [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] — SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills
- [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] — Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve

## 技术点深读（DEEP）

![[deep/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving.txt`（81350 字符）供引用检索。