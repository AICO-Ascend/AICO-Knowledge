# Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter — 技术点深读（DEEP 2026-08-18）
<!-- 独立深读文件：extract_phase1 重跑不覆盖；内容织进 deep/<slug>.md，MOC 谱系见 moc_relations.md -->
> 论文：Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter · arXiv:2604.15039v2
> 作者：Ruoyu Qin, Weiran He, Yaoyu Wang, Zheming Li, Xinran Xu, Yongwei Wu, Weimin Zheng, Mingxing Zhang（Moonshot AI / 清华大学）· 2026/4/22

## 核心问题

PD disaggregation 已是大规模 LLM serving 的事实架构，但其实际部署边界仍由 **KVCache 跨节点传输**决定（§1, §2.1）。论文用 Figure 1（p.2，M3 解读）一图立论：图 (a) status quo 把 Prefill/Decode 锁在同一个 Single Homogeneous Cluster 内、走 RDMA-based Single-Cluster KV Store、tightly-coupled KV transfer；图 (b) PrfaaS 把两阶段拆到 PrfaaS Cluster（Prefill-specific）与 Local PD Cluster（Decode）两个集群，中间用 Ethernet-based Cross-Datacenter KVCache Transfer Layer 连接，并显式标注 Dense=network-bound ✗、Hybrid=prefill-bound ✓——即"只有 hybrid 模型才让 loosely-coupled KV transfer 成立"。这一图示直接对应论文三个被点名的系统性痛点：

1. **异构硬件无法解耦部署**：compute-oriented（NVIDIA Rubin CPX）与 bandwidth-oriented（Groq LPU）加速器按芯片类型/物理位置分别池化，无法在同一个 tightly coupled RDMA fabric 内共存（§1, §2.1）。一旦强塞进单集群，prefill-to-decode 硬件比固定，无法随流量演化调整，一侧 overprovisioned、另一侧成瓶颈，stranded capacity 严重（§2.1）。
2. **带宽墙量化**：单实例 KV throughput Φ_kv(l)=S_kv(l)/T_prefill(l)（式1, §2.1）。dense 模型 MiniMax-M2.5 在 32K 输入下单实例 KV 产出约 60 Gbps（§2.1），Figure 2（p.4，M3 解读）用双轴 bar+line 直观呈现这一带宽墙：KV throughput（蓝柱）从 1K 的 ~5 Gbps 一路爬到 64K 的 ~62 Gbps，128K 才因 prefill latency（红线）爆炸（~5.5 s）而回落到 ~48 Gbps——prefill latency 在 8K 前近 0，32K 升到 ~2 s，128K 飙到 ~5.5 s。这正好说明 dense 模型 KV 流量随上下文增长而 saturate/degrade，是把 prefill/decode 死锁在紧密集成集群的"带宽耦合"。512×H200 集群在 L_avg=32K 下，MiniMax-M2.5 需 3.8 Tbps、Qwen3 需 2.1 Tbps 出口带宽（式2, §2.3），把部署锁死在紧密集成 fabric。
3. **hybrid 模型"必要不充分"**：hybrid-attention（KDA/SWA/linear 交错少量 full-attention）把 Φ_kv 降一个数量级，使跨 DC 传输"plausible"，但真实负载仍 bursty、请求长度高度倾斜、prefix cache 分布不均、跨集群带宽波动；naive 全量外移 prefill 仍会拥塞、排队、利用率低（§1, §2.2, §2.3）。

核心论断（§1）：**KVCache-friendly 模型架构是 cross-DC 异构 serving 的必要条件但非充分条件；必须与 selective offloading + bandwidth-aware scheduling + cache-aware placement 联合才 practical。**

## 关键创新点

1. **Prefill-as-a-Service (PrfaaS) 跨 DC 架构**（§1, §3.1）：将长上下文 prefill 选择性卸载到独立、compute-dense 的 PrfaaS 集群，KVCache 经 commodity Ethernet 回传给本地 PD 集群 decode；短请求留本地 PD 路径。Figure 1b（p.2，M3 要点）即此架构示意——PrfaaS Cluster 与 Local PD Cluster 由 Cross-Datacenter KVCache Transfer Layer（Ethernet）连接，hybrid 标注为 prefill-bound ✓。Figure 3（p.6，M3 解读）进一步给出部署拓扑：Request Router 按阈值 t 把长请求 (l>t) 送 PrfaaS 集群（高算力 prefill 节点 + intra-cluster RDMA）、短请求 (l≤t) 留本地 PD 集群（高显存带宽 decode 节点）；PrfaaS 产出 KVCache 经跨集群以太网回传；两侧各挂 Hybrid Prefix Cache Pool，Global KVCache Manager 全局协调；M3 点出"1T 模型 ~170 Gbps、万卡总出口 ~1.8 Tbps"使跨 DC prefill 卸载在物理链路上首次可行。去除"异构加速器必须共享低延迟 RDMA fabric"的假设，prefill 与 decode 可在 loosely coupled 集群/数据中心/区域独立扩缩。效果：1T 模型 case study 中吞吐 +54%、P90 TTFT −64%、等成本下吞吐 +15%，仅消耗 modest 跨 DC 带宽（Abstract, §4.4）。

2. **Selective offloading by length threshold**（§1, §3.3, §3.4.2）：只有 incremental uncached 长度 l>t 才外移到 PrfaaS；l≤t 留 PD-P。阈值 t 是系统级优化变量。机制：短 prefill 实际是 memory/communication-bound 而非 compute-bound，算术利用率低，无法吃满 compute-dense 加速器，外移反而亏（§3.3）。t 控制带宽压力——提升 t 把 PrfaaS 限制在更长请求，T_prefill(l) 近二次增长而 S_kv(l) 线性，降低 per-instance KV throughput（§3.4.2）。Figure 5b（p.11，M3 解读）把这一权衡可视化：横轴阈值 t（0K–60K），红曲线 PrfaaS bound 随 t 增大先升后平（~20K 后平台），蓝曲线 PD-Prefill bound 随 t 增大单调下降，最优 Λ_max=3.24 落在两曲线交点 t=19.4K。

3. **Hybrid Prefix Cache Pool**（§3.2, Figure 4 p.7, M3 解读）：基于 vLLM hybrid KVCache manager，把 linear-attention/SWA 的 request-level recurrent state（size 与输入长度无关、仅 exact-length 匹配可复用）与 full-attention 的 block-level KV（随长度线性、支持 partial prefix 匹配）分到不同 group（Linear Attention Group 管 Group 0/1/2 的 request-level recurrent states；Full Attention Group 管 Group 3 的 block-level KVCaches），但共享 Unified Hybrid Cache Pool。block 分两类：**prefix-cache blocks**（intra-cluster、block-aligned、需写满才能跨请求复用）和 **transfer-cache blocks**（cross-cluster、任意长度、传输完即丢弃），另有 Free Blocks。M3 点出核心洞察："单一共享 block pool 统一异构 KV 存储——reusable aligned prefix blocks 用于 intra-cluster serving，flexible transfer blocks 用于 cross-cluster PD-disagg prefill transfer"。解决了 hybrid 模型下"all-layer-uniform KVCache storage"范式失效问题。

4. **Converging-pipeline 吞吐模型**（§3.4.1, 式3-6）：PrfaaS = min(算力瓶颈 N_prfaas/T_prefill(l_long), 网络瓶颈 B_out/S_kv(l_long))；PD-P = N_p/T_prefill(l_short)；PD-D = N_d·BS_max/(T_decode·L_out)。端到端 Λ_max = min(Θ_prfaas/p, Θ_pd-p/(1−p), Θ_pd-d)，其中 p=P(L>t)，对应论文中"PrfaaS Prefill → PD-D Decode"与"PD-P Prefill → PD-D Decode"两路 producer 汇聚到一个 consumer 的 converging pipeline（§3.4.1 文中示意图）。把 compute、bandwidth、routing split 三类约束统一到一个可优化模型。

5. **Throughput-optimal 双变量求解**（§3.4.2, 式7-8, Figure 5 p.11, M3 解读）：两决策变量——阈值 t（定 p、l_long、l_short）与 PD 集群内 N_p/N_d 比。最优 t 使 Θ_prfaas/p = Θ_pd-p/(1−p)（两 prefill 阶段同时饱和）；最优 N_p/N_d 使 Θ_prfaas+Θ_pd-p = Θ_pd-d（producer-consumer 平衡）。因 Θ_prfaas/p 随 p 单调减、Θ_pd-p/(1−p) 随 p 单调增，grid search 高效收敛。Figure 5a（p.11，M3 解读）画出固定 t 下搜 N_p/N_d：红 Prefill bound 曲线随 N_p 增先升后降，绿 Decode bound 曲线与之相交于星号 Λ_max=3.24, N_p=3, N_d=5；Figure 5b 给出 t 的对应交点 t=19.4K。M3 概括"data flow: profiling → throughput model → 2-D grid search → optimal operating point"。Case study 得 t=19.4K、N_p=3、N_d=5、约 50% 请求外移（§4.2）。

6. **Dual-Timescale Scheduling**（§3.4.3）：
   - **短期（bandwidth- & cache-aware routing）**：监控 PrfaaS egress utilization 与 queue depth，接近阈值即触发调整；按 incremental prefill-length 分布（prefix 匹配后）搜最优 t。对 prefix-cache hit 请求分两种约束：带宽稀缺时各集群缓存独立评估（l_total−l_pd≤t 留 PD-P，否则外移）；带宽充足时算力为稀缺资源，取 l_prefix=max(l_prfaas,l_pd)，允许跨集群 cache transfer 减少重复计算。
   - **长期（traffic-driven re-optimization）**：监控各阶段 queue depth 与 utilization，当 Θ_prfaas+Θ_pd-p≪Θ_pd-d（prefill 瓶颈）或≫（decode 瓶颈）时，在 PD 集群内把节点在 prefill/decode 角色间转换，重调 N_p/N_d 与 t（§3.4.3）。

7. **传输层工程化**（§3.3）：layer-wise prefill pipelining 使 KVCache 生成与传输 overlap；multi-connection TCP 充分利用带宽；congestion monitoring 集成进 scheduler，早检测 loss/retransmission 防止拥塞累积——保证即便 Φ_kv 名义低，突发与不均链路利用仍不致拥塞。

## 表格（原文结构化）

### Table 1 — 代表性模型配置（§2.2）
| Model | Attention Type A (linear) | Attention Type B (full) | A:B Ratio | Params |
|---|---|---|---|---|
| Kimi Linear | KDA | MLA | 3:1 | 48B |
| MiMo-V2-Flash | SWA | GQA | 5:1 | 309B |
| Qwen3.5-397B | GDN | GQA | 3:1 | 397B |
| Ring-2.5-1T | Lightning | MLA | 7:1 | 1T |
| MiniMax-M2.5 | – | GQA | – | 229B |
| Qwen3-235B | – | GQA | – | 235B |

### Table 2 — 注意力机制的 prefill latency 与 KV throughput 特性（§2.2，lower is better）
| Mechanism | Prefill Latency | KV Throughput |
|---|---|---|
| GQA | High | High |
| MLA | High | Low |
| Sparse Attention | Low | High |
| SWA | Low | Low |
| Linear Attention | Low | Low |

### Table 3 — KV throughput Φ_kv (Gbps) @ 8×H200, SGLang v0.5.9（§2.2）
| Seq Len | Kimi Linear (H) | MiMo-V2-Flash (H) | Qwen3.5-397B (H) | Ring-2.5-1T (H) | MiniMax-M2.5 (D) | Qwen3-235B (D) |
|---|---|---|---|---|---|---|
| 1K | 1.19 | 0.82 | 4.13 | 7.27 | 4.94 | 4.12 |
| 8K | 2.29 | 2.85 | 6.28 | 4.47 | 32.87 | 22.42 |
| 32K | 3.87 | 4.66 | 8.25 | 2.59 | 59.93 | 33.35 |
| 128K | 4.88 | 4.71 | 7.47 | 1.46 | 47.82 | 21.50 |

关键对比（与 Figure 2 p.4 的 MiniMax-M2.5 单实例曲线互证）：32K 下 MiMo-V2-Flash 4.66 Gbps vs MiniMax-M2.5 59.93 Gbps = 13× 降幅；Qwen3.5-397B 8.25 vs Qwen3-235B 33.35 = 4× 降幅；Ring-2.5-1T MLA 相对 GQA ~4.5× 压缩 + 7:1 hybrid ~8× = 整体 ~36× KV 内存节省（§2.2）。Table 3 的 32K→128K 区间 MiniMax-M2.5 从 59.93 跌到 47.82，正对应 Figure 2 红线 prefill latency 在长上下文爆炸、KV throughput 反降的现象——dense 模型长上下文带宽墙自我 saturate。

### Table 4 — PrfaaS-PD 吞吐模型符号（§3.4.1）
| 符号 | 含义 |
|---|---|
| Λ | 请求到达率（吞吐） |
| N_prfaas | PrfaaS prefill 实例数 |
| L | uncached 输入长度（随机变量） |
| N_p, N_d | PD-P / PD-D 实例数 |
| t | 路由阈值 |
| B_out | PrfaaS 出口带宽 |
| l_long / l_short | E[L\|L>t] / E[L\|L≤t] |
| BS_max | 最大 decode batch size |
| T_prefill(l) | 长度 l 的 prefill 时间 |
| p | P(L>t)，外移到 PrfaaS 的比例 |
| T_decode | 单步 decode 时间 |
| L_out | 平均输出长度 |
| Θ_prfaas / Θ_pd-p / Θ_pd-d | 各阶段吞吐（req/s） |
| S_kv(l) | 长度 l 的 KVCache 大小 |

### Table 5 — 内部 1T hybrid 模型 (Kimi Linear 架构, KDA:MLA=3:1) profiling @ 8×H200（§4.1）
| Seq Len | KVCache Size | Prefill Latency | KV Throughput |
|---|---|---|---|
| 1K | 190.8 MiB | 0.44 s | 3.61 Gbps |
| 8K | 308.9 MiB | 0.72 s | 3.59 Gbps |
| 32K | 701.3 MiB | 1.84 s | 3.19 Gbps |
| 128K | 2316.3 MiB | 7.40 s | 2.62 Gbps |

对比 Table 3 的 dense MiniMax-M2.5：同为 32K，1T hybrid 仅 3.19 Gbps vs 59.93 Gbps，约 19× 降幅——这是 Figure 1b 把 hybrid 标为 prefill-bound ✓、Figure 3 跨 DC 拓扑可行的数字根基。

### Table 6 — 三种部署配置对比（§4.2, §4.3）
| Metric | PrfaaS-PD | Homogeneous PD | Naive Heterogeneous PD |
|---|---|---|---|
| Threshold t | 19.4K | — | — |
| N_prfaas / N_p / N_d | 4 / 3 / 5 | — / 9 / 3 | 4 / — / 8 |
| Mean / P90 TTFT (s) | 2.22 / 3.51 | 4.44 / 9.73 | 1.74 / 3.51 |
| Θ_prfaas / Θ_pd-p / Θ_pd-d (req/s) | 1.61 / 1.64 / 3.91 | — / 2.11 / 2.35 | 2.45 / — / 6.25 |
| Λ_max (req/s) | 3.24 | 2.11 | 2.45 |
| Ratio | 1.54× | 1.00× | 1.16× |

关键数字（与 Figure 5 p.11 的 grid search 交点互证）：PrfaaS-PD 吞吐比 homogeneous 高 54%（3.24 vs 2.11）、比 naive heterogeneous 高 32%（3.24 vs 2.45）；mean TTFT −50%、P90 TTFT −64%；Θ_prfaas/p ≈ 1.61/0.496 ≈ 3.25 与 Θ_pd-p/(1−p) ≈ 1.64/0.504 ≈ 3.25 几乎相等，验证式7"两 prefill 阶段同时饱和"；Θ_prfaas+Θ_pd-p=3.25 ≈ Θ_pd-d=3.91 略低（decode 略有余量），符合式8的 producer-consumer 平衡近似。平均 PrfaaS 出口仅 13 Gbps，占 100 Gbps Ethernet 链路的 13%（§4.3.1, §4.4）。

## 与同类对比

- **vs Mooncake [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]**：Mooncake 把 KVCache 提升为 first-class 系统资源，建全局 KV pool，但池作用域仍是**单 DC 内 RDMA fabric**。PrfaaS 把同一思想外推到跨 DC，KV pool 跨 loosely coupled 集群，传输介质从 RDMA 降到 commodity Ethernet——前提是 hybrid 模型把 Φ_kv 降一个数量级。Mooncake 是 intra-DC KV 池根，PrfaaS 是其跨 DC 延伸。
- **vs Splitwise / DistServe**（§6）：同属 PD disaggregation 谱系，但 Splitwise 从 cost/power、DistServe 从 goodput 角度论证，都默认单集群紧密耦合；PrfaaS 额外引入跨 DC 异构与 bandwidth-aware 调度。
- **vs Helix / Hetis / LLM-PQ**（§6）：这些把异构 GPU/网络纳入优化空间做 phase-specialized 放置，但仍假设硬件可同处一域；PrfaaS 显式去除该假设，允许异构芯片物理分离跨 DC。
- **vs naive heterogeneous PD**（§4.3.3, Table 6）：naive 把所有 prefill 给 H200、所有 decode 给 H20，无长度路由无负载均衡——吞吐仅 1.16×（vs PrfaaS 1.54×），25% 性能损失来自 prefill/decode 严重失衡 + 把异构 prefill 当通用路径而非选择性卸载。这正是"hybrid 模型 + 无脑外移"会失败的实证，也反衬 Figure 1b"selective offload + loosely coupled"设计的必要性。
- **vs KVCache 压缩/复用类**（H2O, KIVI, KVQuant, CacheGen, CacheBlend, FusionRAG, §5, §6）：这些在算法/系统层缩 KV 体积/流量，与 PrfaaS 模型架构侧降 Φ_kv 互补，共同让跨 DC KV 更鲁棒；CacheBlend/FusionRAG 的非前缀 KV 复用甚至可与跨集群 cache transfer 协同。

## 跨论文关系（→ MOC 谱系）

- **[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]** — 同作者群（Moonshot AI）。Mooncake 确立 KVCache-as-first-class-resource、全局 KV pool 的 intra-DC 范式；PrfaaS 是其跨 DC 推广（论文 §1/§6 明确把 Mooncake 作为前作与单 DC KV 池根）。
- **[[efficient-memory-management-for-large-language-model-serving-with-pagedattention]]** — PagedAttention 的 block 抽象是 PrfaaS hybrid prefix cache pool（prefix-cache/transfer-cache block 分类、共享 block pool，Figure 4 p.7）的内存管理根。
- **[[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]** — 另一类大规模部署范式：GPU + RoCE 紧密耦合超 Pod；PrfaaS 走反方向（loosely coupled、Ethernet 跨集群），可作为对照。
- **[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]** — multimodal EPD disagg 兄弟工作；同属 disagg 谱系，PrfaaS 把 disagg 边界从单集群推到跨 DC，未来 multimodal 长 context 亦可能跨 DC 卸载 prefill。
- **[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]** — 论文 §5/§6 显式引用，非前缀 KVCache 融合复用，与 PrfaaS 跨集群 cache transfer 互补。
- **[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]** / **[[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]]** / **[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]** — KVCache 管理谱系上下文，PrfaaS 在系统部署层而非单模型注意力层降 KV 流量。

**MOC 定位**：PrfaaS 是 **cross-DC disagg 的顶点**——它把 PD disagg（Splitwise/DistServe/Mooncake）、异构硬件（Helix/Hetis/LLM-PQ）、KVCache 压缩复用（H2O/KIVI/CacheBlend）三条线收束到"hybrid 模型架构使跨 DC KV 传输 plausible，selective offloading + bandwidth-aware scheduling 使其 practical"这一联合论断上。Figure 1（p.2）的 (a) vs (b) 二分正是这一收束的图示化。

## 局限与边界

1. **强依赖 hybrid-attention 模型**（§2.2, §5）：整套论证建立在 hybrid 模型把 Φ_kv 降一个数量级之上（Table 3: 32K 下 MiMo-V2-Flash 4.66 vs MiniMax-M2.5 59.93 Gbps；Figure 2 p.4 直观展示 dense 模型 ~60 Gbps 带宽墙）。对纯 dense GQA/MLA 模型，单实例 KV 流量远超跨 DC Ethernet，PrfaaS 不适用——仍需 RDMA 紧密耦合。即 PrfaaS 的可行性是"模型架构条件性的"。
2. **case study 规模有限**（§4.1）：仅一个内部 1T 模型、32 H200 + 64 H20、100 Gbps VPC 互联；workload 为 truncated log-normal（µ=9.90, σ=1.00, [128,128K], 均值~27K），输出固定 1024 token。所有吞吐/带宽结论由 profiling 数据（Table 5）喂入吞吐模型得出（§4.1），非端到端线上实测，模型与负载多样性未验证。
3. **仅 H200/H20 一对硬件**（§4.4）：作者承认 H200+H20 只是代表性配对，cost-effective prefill 专用芯片需另行评估；Rubin CPX / LPU / Taalas HC1 等被点名的 phase-specialized 硬件（§5）未被实测。
4. **PrfaaS 集群当前 compute-bound**（§4.4）：带宽有大量 headroom（13 Gbps / 100 Gbps，§4.3.1），意味着若未来 hybrid 模型 Φ_kv 进一步下降或专用线带宽提升，瓶颈会转移到别处；论文只做推论性外推（IDC 级万卡 ~1.8 Tbps 出口，§2.3, Figure 3 M3 要点），未实测大规模。
5. **缓存一致性与全局元数据开销未量化**（§3.2, §3.4.3）：global KVCache manager 跨所有集群维护元数据、做 cache rebalancing，但在集群数/缓存规模放大时的元数据开销、跨集群 cache transfer 一致性窗口、failure 恢复路径未展开。
6. **naive heterogeneous 对比偏弱**（§4.3.3）：naive 配置被刻意设为"无调度无负载均衡"，凸显 PrfaaS 调度价值，但缺乏与"带简单负载均衡的异构部署"的中间基线，难以隔离"selective offloading"与"bandwidth-aware scheduling"各自的贡献。
7. **跨 DC 延迟未深入**：论文聚焦吞吐与 TTFT，但跨集群 KVCache 传输引入的尾延迟、跨区域地理距离下的 RTT 影响（仅 VPC peering/专线，§3.1, Figure 3 拓扑）对交互式/低 SLO 场景的边界未给出量化阈值。
