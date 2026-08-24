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
> 【图文联合解读】**图文联合解读**

图1展示Mooncake的整体架构，核心由左侧"KVCache-centric Conductor"（含Cache-aware Prefill、KVCache Balance、Load-balance Decoding三个调度器）和右侧三类资源池构成：Prefill Pool（GPU/VRAM内含Local Chunked Prefill Scheduler+Paged KVCache，CPU/DRAM/SSD为Distributed KVCache Pool）、KVCache Pool（Inter-node RDMA跨节点传输）、Decoding Pool（同构分页KVCache）。Prefill实例间通过PP/SP流水线并行，两阶段资源解耦。

原文借此论证两点关键结论：(1)远程位置拉长TTFT、大batch增大TBT，吞吐优化与延迟SLO天然冲突；(2)必须分阶段建模——Prefill阶段以"最大化Cache复用"为目标并约束TTFT SLO、最低MFU及KVCache<DRAM；Decoding阶段以"最大化吞吐"为目标并约束TBT SLO、KVCache<VRAM。

该图是论文方法论的骨架总图，将后续Chunked Prefill、分页KVCache、RDMA传输、负载均衡等具体机制统一在该解耦架构框架下，为后续实验提供结构基础。

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig02.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p04.png]]*
> [!quote] caption
> Normalized throughput and latency of prefill and decoding stages with different sequence lengths or batch sizes for the dummy LLaMA2-70B model. the computational complexity of attention networks scales quadratically with input length while the complexity of MLP scales linearly, computation time in the prefill stage generally increases superlinearly with input length, as shown in the left part of F

> [!tip] 技术解读（多模态）
> 【图文联合解读】左图（batch=1，seq 8k→128k）：prefill延迟由约0.03s超线性升至1.0s，归一化吞吐量由1.0降至0.54；右图（seq=8k，batch 1→16）：decode吞吐量由0.08升至1.0，延迟由0.80缓升至约1.0。原文据此论证：attention计算量随序列长度二次方增长，导致prefill耗时超线性攀升；而decode阶段可依靠增大batch显著提升吞吐，延迟增幅却相对有限。

该图为Mooncake将prefill与decode解耦的双层架构提供了量化依据：因二者计算/访存特性差异悬殊（长序列下prefill为延迟敏感型，decode为吞吐敏感型），必须采用差异化调度与资源分配，正是后续解耦架构设计及端到端实验验证的基础前提。

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig03.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p05.png]]*
> [!quote] caption
> The KVCache pool in CPU memory. Each block is attached with a hash value determined by both its own hash and its prefix for deduplication.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心对象与结构**：图示CPU内存中的KVCache池，由9个Token Blocks（a–i）组成，每块附带链式哈希值（A=Hash(a)、B=Hash(A+b)…F=Hash(E+f)），融合自身与前缀哈希。三类缓存块以颜色区分：黄色为前缀缓存块，粉色为增量缓存块，灰色为未分配块。

2) **关键技术结论**：前缀哈希A–E匹配✅，F处失配❌，触发新增增量块F–I写入；证明链式哈希机制可有效识别公共前缀并去重，仅复用命中部分、新增增量部分，避免全量重算。

3) **方法链路作用**：支撑Mooncake"KVCache-centric"解耦架构——Prefill实例通过Messenger读/写KVCache至池中，Decoding实例加载复用，实现预填充与解码解耦下的高效缓存共享。

### Figure 4 (p.6) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig04.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]]*
> [!quote] caption
> Workflow of inference instances. ( ) For prefill instances, the load and store operations of the KVCache layer are performed layer-by-layer and in parallel with the prefill computation to mitigate transmission overhead (see §5.2). (y ) For decoding instances, asynchronous loading is performed concurrently with GPU decoding to prevent GPU idle time. 4) Decoding: After all the KVCache is received i

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示 Prefill 与 Decoding 两实例工作流。左 Prefill 端：GPU 经 s2 做增量 Prefill，CPU↔GPU 通过"逐层 Load and Store*"(∗)并行传输 Prefix+Incremental KVCache；右 Decoding 端：CPU 异步加载 Full KVCache†(†)至 GPU，GPU 并行执行 s4 解码；两端 CPU 内存间由 s3 完成 KVCache Transfer。该图论证：在 prefill/decoding 解耦架构下，通过分层 Load/Store 与异步加载，使 KVCache I/O 与 GPU 计算重叠，可掩盖传输开销、避免 GPU 空闲，是 Mooncake 围绕 KVCache 中心化设计以降低 TTFT、提升吞吐的核心机制。

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig05.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]]*
> [!quote] caption
> Input and output length distributions in the request trace. 4

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图5展示请求trace中输入长度（左蓝）与输出长度（右绿）频率分布，均采用对数纵轴。

**核心数据：**
- **输入长度**：严重右偏长尾，峰值在<5K处（~10⁴），但分布延伸至128K，部分请求极长。
- **输出长度**：双峰分布，首峰在<50处（~1.5×10⁴），次峰约300–500区间，长尾至2048处有明显截断尖峰。

**论证的技术结论：** 输入长度跨度极大且长尾显著，说明存在大量长prefill与可复用prefix场景，验证了prefill-decode解耦与KVCache中心化存储的必要性；输出以短生成为主但存在长输出长尾，表明解码阶段需灵活调度以避免长尾请求阻塞。

**论文链路作用：** 作为实验trace特征刻画，为后续基于真实负载的调度策略（如early rejection、prefix caching命中率分析）提供量化依据，支撑解耦架构相对传统架构的收益论证。

### Figure 6 (p.7) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig06.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p07.png]]*
> [!quote] caption
> CDF (Cumulative Distribution

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1）核心对象与数据：** 图示为请求trace中KV cache block命中次数的CDF（X轴对数刻度1~10⁴）。曲线迅速攀升：约55%的block仅命中1次，约77%命中≤2–3次，约90%命中≤4–5次，在命中次数≈30处已逼近1.0，呈极重长尾分布。

**2）原文论证结论：** block命中高度集中于少量低频/单次复用块，说明上下文前缀复用极不均匀、热点极其集中，从而印证"以KV cache为中心"的Mooncake架构设计前提——离散的prefix cache池即便容量不大也能捕获绝大部分重复前缀。

**3）论文链路作用：** 该CDF为后续cache容量规划与eviction策略（优先淘汰低命中冷块、按命中次数而非LRU调度）提供量化实证支撑，是连接"真实负载复用特性"与"解耦式KV cache架构设计"的关键依据。

### Figure 7 (p.9) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig07.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p09.png]]*
> [!quote] caption
> Latency of storing KVCache of different request lengths (Layer-wise latency refers to the difference in latency between Layer-wise Prefill and Prefill without storing KVCache).

> [!tip] 技术解读（多模态）
> 【图文联合解读】# 图7 联合解读

**核心数据**：横轴为请求长度（8K–128K tokens），纵轴为存储KVCache的延迟（秒）。蓝色"Serialized"随序列长度从约0.11s线性增长至约0.87s；橙色"Layer-wise"全程稳定在约0.10s，几乎不随长度变化。

**关键结论**：Layer-wise方案（边预fill计算边传输KVCache）通过将存储开销与计算流水重叠，成功将存储延迟从随长度线性增长压缩为常数。序列越长，优势越显著——128K时差距达近9倍。

**论文作用**：此图直接支撑Mooncake架构的核心设计——Prefix Caching必须采用"层粒度调度"而非"序列化等待"，否则长上下文场景下KVCache传输将成瓶颈；为后续Transfer Engine与Instance间的流水线协作提供了量化依据。

### Figure 8 (p.11) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig08.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p11.png]]*
> [!quote] caption
> The prefill scheduling experiment in the Mooncake cluster.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图中以盒须图比较 Mooncake 集群四种 prefill 调度的 TTFT（30 s SLO）：KVCache-centric、cache-aware、load-balancing、random 的均值约为4.2、12.4、57.4、89.2 s，上须最高约12、63、220、290 s，后两者大量请求超时。结果表明，按 KVCache 亲和性放置可提高缓存复用率并显著降低均值与尾延迟；该实验验证了 KVCache-centric 调度器是分离式推理架构低延迟服务的重要保障。

### Figure 9 (p.13) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig09.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p13.png]]*
> [!quote] caption
> The load of prefill and decoding instances over 20 minutes, before using the prediction- based early rejection.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**核心数据**：图示20分钟内（0:00–20:00）prefill（绿）与decoding（橙）两类实例的负载百分比曲线。绿线波动剧烈，多次跌至3%–8%的近空闲状态，又冲至90%–95%的满载；橙线整体偏高但仍起伏于约35%–95%。两条曲线在多个时间点呈明显反向波动——prefill高峰时decoding走低，反之亦然，反映两类节点负载严重错配。

2）**技术结论**：在未启用基于预测的早期拒绝机制前，prefill与decoding实例负载无法被均衡调度，存在严重的"此忙彼闲"现象，部分节点长期空转而另一些节点接近饱和，说明仅靠被动调度难以解决分离架构下的负载失衡。

3）**论文链路作用**：此图作为**动机证据**（motivation），引出论文提出的预测式早期拒绝策略——通过预先识别可被截断的请求并提前rejection，削峰填谷，从而在后续实验（图10/11）中展示该机制对负载均衡与整体吞吐的改善效果。

### Figure 10 (p.14) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig10.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p14.png]]*
> [!quote] caption
> Instance load when applying Early Rejection and Early Rejection Based on Prediction. conditions where resources are scarce and accurate predictions are necessary, making request-level predictions particularly difficult.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图10联合解读**

**核心内容**：图含两子图——(a) Early Rejection 与 (b) Early Rejection Based on Prediction，均为 2×4 箱线图阵列：横轴为 4 个时间点（黑色箭头推进），纵轴双行分别对应两类实例；底行深色箱体表征预测负载，☆号标记早拒发生节点。

**技术结论**：在资源稀缺场景下，仅做 Early Rejection 易造成实例间负载集中与失衡；而引入预测后仍受请求级预测精度制约，凸显单点拒绝策略的局限。

**论证作用**：作为对比基线，与后续启用 Mooncake 完整调度后的负载曲线串联，形成"暴露问题→提出方案→实验验证"论证链，是调度策略章节的关键支撑。

### Figure 11 (p.16) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig11.png]]
*整页渲染: ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]]*
> [!quote] caption
> End-to-end experiments of Mooncake and vLLM on the ArXiv Summarization and L-Eval datasets instances. In real-world clusters, the demand for prefill and decoding instances generally remains stable over certain periods, with only minor temporary imbalances. Thus, the proportion of prefill and decoding instances can be preset. Future research will explore more flexible deployment and conversion meth

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示2×2网格，对比Mooncake-[3P+1D]（蓝）与两基线在ArXiv、L-Eval长文本数据集上的归一化P90 TTFT/TBT-请求速率曲线。量化：TTFT图中Mooncake于~3.5/2.0 req/s才达SLO，基线在1.5-2.5/0.75-1.25即饱和；TBT图中Mooncake在ArXiv稳定~0.48、L-Eval于~0.9触阈。结论：Mooncake解耦架构在高负载下TTFT/TBT均显著优于vLLM基线，证明prefill-decoding分离及KVCache中心化设计有效提升长上下文吞吐与延迟；该端到端实验验证核心架构对vLLM方案的实际优越性。

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
> 【图文联合解读】**图文联合解读：**

1) 表展示 LRUCache、LFUCache、LengthAwareCache 三种策略在 Inf、100000、50000、30000、10000、1000 六档块容量下的命中率：均自 0.51 阶梯式降至 0.30；策略间差距极小（≤0.06），容量 1000 时三者完全收敛于 0.30。

2) 论文借此论证：替换策略对命中率影响有限，故 Mooncake 不再纠结于淘汰算法选型，而是把优化重心转向 prefix caching 提前存储部分 KV 块，以及 prefill–decoding 解耦架构本身。

3) 在论文链路中的作用：作为动机铺垫，排除"策略优化"路径，从而引出"KVCache-centric 解构 + 早期存储"这一核心架构贡献。

### Table 2 (p.15) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-tab02.png]]
> [!quote] caption
> Datasets used in the end-to-end experiment.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表列出端到端实验所用4个数据集的关键特征：ArXiv Summarization（输入8088、缓存命中率~0%）、L-Eval（输入19019、命中率>80%）、Simulated Data（输入16k/32k/64k/128k、命中率50%）、Real Data（输入7955、命中率~50%），到达模式为Poisson Process与Timestamp-based。

该表支撑了论文的实验多样性论证：通过覆盖8k–128k不同输入长度、0%到>80%的命中率梯度，以及合成与真实流量多种模式，全面验证Mooncake的KVCache-centric分离架构在长上下文、高缓存复用及真实业务场景下的有效性，是其方法落地验证的关键基础。

### Table 3 (p.17) ⭐深度解读
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-tab03.png]]
> [!quote] caption
> Number of requests rejected by the system under the overloaded-scenario experiment.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读：**

**1) 核心数据：** 该表展示过载场景（overloaded-scenario）下系统拒绝请求数。三列对比：Baseline（基线）=4183、Early Rejection（早期拒绝）=3771、Early Rejection based on Prediction（基于预测的早期拒绝）=3589。即在相同过载压力下，加入早期拒绝机制较基线减少约 412 条（≈9.8%）；进一步引入预测机制后，再减少约 182 条（相对 Early Rejection 再降 ≈4.8%）。

**2) 关键论证结论：** 论文借此证明 Mooncake 的"过分配 + 早期拒绝"策略有效——通过预测未来负载提前腾挪 KVCache 资源，可显著降低系统对请求的硬拒绝率；基于预测的早期拒绝优于静态早期拒绝，体现负载预测模块的实际价值。

**3) 在论文中的作用：** 该表属于过载鲁棒性实验的一环，与吞吐量、TTFT 等主指标互为补充，共同支撑"以 KVCache 为中心 + 预测式调度"在真实高并发场景下提升服务可用性的核心论点。

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