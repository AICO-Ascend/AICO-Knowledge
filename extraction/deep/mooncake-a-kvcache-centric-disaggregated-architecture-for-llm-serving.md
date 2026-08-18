# Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving — 技术点深读（DEEP 2026-08-18）
> 独立文件，extract_phase1 重跑不丢。本笔记在原 deep note 基础上把 11 张 figure 的 M3 解读织进各节，前后文一致。
> 论文：Mooncake · arXiv:2407.00079v4 (3 Sep 2025)
> 作者：Ruoyu Qin, Zheming Li, Weiran He, Mingxing Zhang, Yongwei Wu, Weimin Zheng, Xinran Xu — Moonshot AI ♠ × Tsinghua Univ. ♡。Moonshot AI 的 Kimi 生产级服务平台的实际支撑架构。

## 核心问题

Mooncake 解决的不是单点优化，而是一个**多约束下的商业 MaaS 优化问题**（§1.1）：

1. **目标函数**：最大化 overall effective throughput（直接对应 revenue）；且只有**完整跑完的请求**才计入 goodput，中途被拒的资源全部浪费（§2）——这点比 DistServe/Splitwise 的 goodput 定义更严格。
2. **硬约束**：两类 latency SLO——TTFT（time to first token，预填充阶段指标）与 TBT（time between tokens，解码阶段指标）。实验中 §8.1 设 `TTFT_P90 = 10×`、`TBT_P90 = 5×`（单请求无干扰基线的倍数），实际部署用固定阈值（§2）；real workload 实验中 TTFT 上限 30 s、TBT 上限 0.1 s/token（§8.1.3）。
3. **资源约束的现实性**：GPU 供给受限、无法弹性扩容，导致 **overload 是常态而非边缘情况**——这是 Mooncake 区别于以往所有"假设资源充足"的研究（vLLM/Splitwise/DistServe/TetriInfer）的根本前提（§1.1, §7）。
4. **负载异构性**：prefill 是 compute-bound（attention 二次复杂度、MLP 线性，故 prefill 延迟随 input length **超线性**增长，§2 Figure 2 左）；decode 是 memory-bound（每次只处理 1 token，随 batch size **次线性**增长，§2 Figure 2 右）。两者 SLO 不同、资源需求不同，耦合调度互相干扰。Figure 2（p.3，M3：prefill 延迟曲线随 seq len 从 8k→128k 陡升、throughput 反向下降；decode 阶段 throughput 随 batch size 上升先线性后趋平）正是 §1.1 选择 disagg 的实证依据。
5. **架构总览对照 Figure 1（p.2，M3）**：左侧输入请求队列→中央 Conductor 把请求分派到 prefill 节点池（上）与 decoding 节点池（下），两池各自挂载 CPU/DRAM 中的 KVCache 池；prefill 产出的 KVCache 通过高速互联流式输送到 decoding 节点，最终在右侧生成输出 token。M3 强调"KVCache 作为一等公民在实例间显式流转、Conductor 综合考虑 TTFT/TBT SLO + KVCache 命中率 + DRAM 容量 + 网络拥塞联合调度"——这一全局视图贯穿后文所有调度算法。

## 关键创新点

1. **KVCache-centric disaggregated 架构（§1, §3；Figure 1 p.2, Figure 4 p.6）**：不仅 prefill/decode 节点池分离，更将 GPU 节点中**未被充分利用的 CPU/DRAM/SSD/RDMA 资源**聚合成 disaggregated KVCache 层——以零额外硬件成本提供近 GPU 的 prefix caching 容量与带宽。KVCache 被当作"一等公民"在实例间显式流转：global scheduler **Conductor** 为每个请求选择一对 prefill + decoding 实例，按 4 步执行（§3）：(1) KVCache Reuse——把可复用 prefix block 从远端 CPU DRAM 加载进 GPU；(2) Incremental Prefill——若未缓存 token 数超过 `prefill_chunk` 阈值（>1000 tokens，§3 步骤 2），按 chunk 流水线执行；(3) KVCache Transfer——逐层 KVCache 流式传输到 decoding 节点 CPU 内存，与 prefill 计算重叠；(4) Decoding——KVCache 全部到齐后加入 continuous batching，decoding 节点本地调度器**二次校验** TBT SLO（因为 prefill 期间负载已变化），不满足则拒——此时 prefill 成本被浪费，这正是 §7 Early Rejection 的动机。**Figure 4（p.6，M3）** 逐层展开此 4 步：左侧 prefill 实例上排"KVCache load/store 层层并行"、下排"prefill 计算 layer-by-layer"；右侧 decoding 实例上排"async load buffer"、下排"GPU decoding"；底部箭头表示 prefill→decoding 的 KVCache handoff。M3 要点："两种 overlap 策略针对不同瓶颈——prefill 用 layer-by-layer 隐藏传输、decode 用 async loading 防止 GPU 空等"。

2. **Paged KVCache + 全局 hash 去重（§3 Figure 3 p.5）**：CPU 内存中 KVCache 以 paged block 存储，每个 block 的 hash = `hash(本 block tokens) ∥ 前一 block 的 hash`（前缀链式哈希），从而**等价的前缀产生等价的 hash 链**——可直接做全局 prefix 去重与跨请求复用。block size 在 trace 中为 **512 tokens**（§4.1）。**Figure 3（p.5，M3）** 画出 tokens→hash 分组→链式去重块（prefix hash chain）→prefix/full KVCache 分页（按 block ID 索引）的链路；M3 强调"复合 hash = 内容 + 前缀上下文，去重同时保留上下文局部性"。这与 vLLM 单机 PagedAttention 的 block 概念一致，但 Mooncake 把 block 提升为**跨节点迁移/复制/swap 的全局调度单位**。

3. **Chunked Pipeline Parallelism (CPP) for long-context prefill（§5.1；8k→1M，§5.1）**：长上下文下 input 可达 output 的 10–100 倍，TTFT 是关键瓶颈。三种多节点并行方案对比：
   - 跨节点 TP：每层 2 次 RDMA all-reduce，MFU 大降。
   - Sequence Parallelism (SP, Ring/Striped Attention)：每层至少 1 次跨节点通信，MFU 仍劣于单节点 TP；且需 elastic SP 动态调整 partition，复杂化 Conductor 决策（与 KVCache 复用率、SLO 违反联合调度冲突）。
   - **CPP**：将 prefill 节点按 X 个一组组成 pipeline group，请求 token 切成 ≤`prefill_chunk` 的 chunk，不同 chunk 在不同节点**同时处理**——只需在 pipeline stage **边界**通信（类训练中的 PP），可被计算 overlap，网络资源与 KVCache 跨节点传输不争用；天然适配短/长上下文，无需频繁动态重分区。论文称这是 **inference 阶段 CPP 的首次应用**（训练阶段已有 TeraPipe [24]）。

4. **Layer-wise Prefill + 异步 KVCache 流式 overlap（§5.2；Figure 7 p.9）**：prefill 逐层计算（compute-bound），KVCache 的 load/store 经 `launch`/`wait` 异步执行——每层 attention 前等待本层 KVCache 异步加载完成并触发下一层异步加载；attention 完成后启动本层异步存储；全部计算完成后等待所有存储完成。**Figure 7（p.9，M3）**：分组柱状图对比 Serialized vs Layer-wise 在 8k/16k/32k/64k/128k 五种 seq len 下的 store 延迟——Serialized 蓝柱从 ~0.10 s 陡升至 ~0.85 s（随 seq len 线性增长），Layer-wise 橙柱在所有长度上几乎平直（~0.10 s）。M3 要点："overlap 让 store 延迟与 seq length 解耦，消除 VRAM-induced TTFT 增长"。效果：layer-wise prefill 的存 KVCache 额外延迟**几乎为零**；且使 prefill 调度**可忽略 VRAM 容量约束**（只需装得下一个请求），调度器只看 KVCache 分布 + DRAM 可用量（Figure 1 中 prefill 调度框只依赖 KVCache 分布与 DRAM size，正是此理）。

5. **KVCache-centric 调度算法 (Algorithm 1, §6.1)**：Conductor 为每个 prefill 实例估计 `TFT = T_transfer + T_queue + T_prefill`（依赖该实例上 prefix_len 命中长度），选最小 TFT 实例；若 >SLO 直接返回 **HTTP 429**。关键设计：定义 `kvcache_balancing_threshold`——若当前实例本地 prefix_len 与全局最优 best_prefix_len 差距小于阈值，走 **cache-aware** 分支（直接本地算，不跨机拉，Algorithm 1 行 8–13）；若差距大于阈值，走 **cache-balancing** 分支（从 best_matched_instance 远端拉 KVCache 到本地，行 14–22）。prefill 时间预测用离线数据训练的预测模型（Transformer 计算模式规律，误差小）；queue 时间 = 队列中所有请求 prefill 时间之和；TTFT 各实例**并行计算**，开销可忽略。

6. **启发式自动 hot-spot migration（§6.2；Figure 6 p.7 + Figure 8 p.11）**：不去预测未来 block 使用（workloads 高度动态、不可预测），而是用**两个简单启发式**实现隐式复制：(a) 当最优远端 prefix 不在本地、但额外 prefill 时间 < 传输时间时，请求转发到本地实例并**主动拉取 KVCache 本地化**；(b) 当 `best_remote_prefix_len ≤ local_prefix × threshold` 时宁可重算不拉。两条规则自然使**热点 block 被复制到多机**、冷 block 被 swap out。**理论支撑来自 Figure 6（p.7，M3）**：CDF 显示 ~60% 的 block 只被命中 1 次、~90% 命中 < 10 次，只有极少数"hot tail"达 10⁴ 命中——M3 要点："cache 命中高度集中在少数 prefix block，eviction 策略应优先捕获高频 tail 而非均匀缓存"。**实验 Figure 8（p.11，M3）**：箱线图对比四种调度在 8 prefill + 8 decode、23k 请求重放下 TTFT 中位数与方差。M3 给出数值：KVCache-centric median ≈ 0 s、cache-aware median ≈ 2 s、load-balancing IQR ~30–100 s（median ~60 s）、random median ~100 s 且极端 outlier 上至 ~270 s。原文正文给出的平均值（§6.2）为 random=92.07 s、load-balancing=60.41 s、cache-aware=14.36 s、**KVCache-centric=6.26 s**——cache-aware 比 load-balancing 降 4×，再加 cache load balancing 再降 2.3×。M3 进一步点出："pure load-balancing 忽视 cache locality，TTFT 分布频繁越线"——这正是 cache-aware 必要性的实证。

7. **Early Rejection + Prediction-based Early Rejection（§7；Figure 9 p.13, Figure 10 p.14）**——overload 场景的核心创新：
   - **load 定义**：disaggregated 架构下，prefill 与 decode 独立处理，故直接用 **SLO 满足度**作为 load——比较实例预测的最大 TTFT/TBT 与 `l_tft`/`l_tbt`（§7.1），而非传统的"请求数/容量比"。
   - **Early Rejection（§7.2）**：把 decoding 实例的 load 评估**提前到 prefill 开始前**，取 prefill pool 与 decoding pool 中较大 load 决定是否接收——避免"prefill 做完才发现 decode 满载被拒、prefill 算力白费"。
   - **load fluctuation 病态（§7.3；Figure 9 p.13 M3, Figure 10a p.14 M3）**：直接 Early Rejection 会导致 prefill 与 decoding 负载**反相震荡**。**Figure 9（p.13，M3）** 给出真实生产集群 20 min 时间序列：绿线 prefill、黄线 decode 在 10%–95% 间反相震荡；M3："scheduling lag 实测导致 phase-staggered oscillation，集群利用率差，motivates §7.4 的 prediction-based ER"。**Figure 10a（p.14，M3）** 进一步给出理论化的 4-stage 反相图：Stage 1 双低→大量接收→prefill 满；Stage 2 decode 满、prefill 闲被拒；Stage 3 decode 完成降、prefill 又满；Stage 4 循环——根因是 decode load 预测相对实际执行有**时滞**。
   - **Prediction-based Early Rejection（§7.4；Figure 10b p.14 M3）**：预测"prefill 结束后"的 decode load 来消震荡。两层预测：(1) **Request-level**——预测单请求 output length 反推 TBT/TTFT，但成本高/精度低，特别是 overload 下；(2) **System-level**（Mooncake 当前采用）——假设每个请求 decode 阶段耗时统一 `t_d`，t 时刻把 prefill 能完成的请求加入、把 t 前完成的移出，算所有 decode 实例平均 TBT/`l_tbt` 比。**Figure 10b（p.14，M3）**：基于预测的 ER 在 8 个时间步里几乎没有 reject（多为空星），decoding 实例数稳定——M3 要点："system-level 预测（uniform t_d + 提前过滤掉会在 t 前完成的请求）避免了 reactive 策略的过早 evict"。精度要求低、更适合 overload。

8. **trace 开源（§4；Figure 5 p.6, Figure 6 p.7, Table 1）**：首个可用于真实复用分析的 1 小时采样 trace，**23,608 条**请求，字段 timestamp(0–3,600,000 ms)、input_length、output_length、hash_ids（remapped block hash，block size 512）。统计：平均 input **7,590 tokens**、平均 output **182 tokens**、input/output 比约 **720**（反映 Kimi 长上下文特性）。**Figure 5（p.6）** 画 input/output 长尾分布，input 主峰在数千但拖至 100k+，output 高度集中于 < 500。**cache hit ratio 随容量**（Table 1）1k→50k blocks 从 30% 升到 50%（再增收益递减）；LRU 最优（temporal proximity）。**超 50% 的 block 从未被使用**而少数 block 被访问数万次（Figure 6）——热点复制是刚需。

## 表格（原文结构化）

### Table 1 — Cache hit rates under different policies/capacities (§4.2)
| Block capacity | Inf | 100000 | 50000 | 30000 | 10000 | 1000 |
|---|---|---|---|---|---|---|
| LRUCache | 0.51 | 0.51 | 0.50 | 0.48 | 0.40 | 0.30 |
| LFUCache | 0.51 | 0.51 | 0.49 | 0.43 | 0.35 | 0.30 |
| LengthAwareCache | 0.51 | 0.50 | 0.48 | 0.42 | 0.35 | 0.30 |

结论：本 trace 下 LRUCache 最优（temporal proximity），50% 命中率是当前 workload 的实际上限；与 Figure 6 M3 解读一致——CDF 显示命中高度集中在尾部少数 block，容量超过 ~10 hits/block 收益递减。

### Table 2 — End-to-end experiment datasets (§8.1)
| Dataset | Avg Input | Avg Output | Cache Ratio | Arrival |
|---|---|---|---|---|
| ArXiv Summarization | 8088 | 229 | ~0% | Poisson |
| L-Eval | 19019 | 72 | >80% | Poisson |
| Simulated Data | 16k/32k/64k/128k | 512 | 50% | Poisson |
| Real Data | 7955 | 194 | ~50% | Timestamp-based |

### Table 3 — Overload-scenario rejection counts (§8.2, 8P+8D, 23k trace, 2× replay)
| Strategy | Rejected requests |
|---|---|
| Baseline | 4183 |
| Early Rejection | 3771 |
| Early Rejection based on Prediction | **3589** |

### 实验硬件配置 (§8.1 Testbed)
- 节点：8× NVIDIA A800-SXM4-80GB（80GB HBM/卡），NVLink 互联，节点间 RDMA 800 Gbps；每节点部署一个 prefill 或 decoding 实例。
- dummy model：LLaMA2-70B 架构。

### 端到端关键结果汇总（含图对照）
| 场景 | 配置 | 结果 | 图对照 |
|---|---|---|---|
| ArXiv Summ. | Mooncake-[3P+1D] vs vLLM-[4M] | +20% throughput（满足 SLO） | Figure 11（p.16，M3：2×2 网格，TBT 下行 Mooncake 平在 ~0.5 而基线冲向 1.0） |
| L-Eval | Mooncake-[3P+1D] vs vLLM-[4M] | +40% throughput（prefix caching 加成） | Figure 11 |
| Simulated (16k–128k) | Mooncake vs vLLM | +50% ~ +525% throughput（vLLM 长 ctx 下解码被打断、被迫单条处理） | Figure 12 |
| Real Workload | Mooncake-[10P+10D] vs vLLM-[20M] | TTFT 两者近 100% 满足；TBT Mooncake ~100%、vLLM 仅 57%；Mooncake 处理多 75% 请求。TTFT 上限 30s，TBT 上限 0.1s/token | Figure 13（p.17，M3：左 panel TTFT CDF 两线几乎重合；右 panel TBT CDF Mooncake 平 100%、vLLM 在 57% 处骤升——TBT SLO divergence 是核心增益来源） |
| 调度实验 | KVCache-centric vs random/load-balancing | TTFT 6.26s vs 92.07s/60.41s | Figure 8（p.11） |

## 与同类对比

| 系统 | 架构 | KVCache 池范围 | Overload 处理 | 区别 |
|---|---|---|---|---|
| **Mooncake** | prefill/decode disaggregated + 分层 KVCache 池 (GPU/CPU/DRAM/SSD) | **跨节点全局** | Early Rejection + Prediction（核心创新，Figure 9/10 实证） | 商业生产级（Kimi），KVCache 是调度一等公民 |
| [[efficient-memory-management-for-large-language-model-serving-with-pagedattention\|vLLM]] | coupled prefill+decode，continuous batching | 单节点 PagedAttention | 无（假设资源充足） | block 概念根——Mooncake 把 block 推广为跨节点迁移单位；Mooncake 的 prefix match 逻辑与 vLLM 类似但 vLLM 只支持本地 cache（§6.1 明示） |
| DistServe [8] | disaggregated | 主要单节点阶段分离 | goodput 优化但无 reject 策略 | Mooncake 共享 disagg 直觉，但 DistServe 专注资源分配+并行策略，不做跨节点 KVCache 池与 overload 拒绝 |
| Splitwise [7] | disaggregated phase splitting | — | 无 | Mooncake 早期开发同期出现，启发 Mooncake；未做 KVCache-centric 全局调度 |
| TetriInfer [9] | chunked prefill + 两阶段 disagg | — | 两阶段预测调度 | 与 Mooncake 思路接近，但无 overload-oriented rejection 与全局 hot-spot migration |
| [[sglang-efficient-execution-of-structured-language-model-programs\|SGLang]] | coupled | 单请求 RadixAttention (LRU radix tree) | 无 | SGLang 做的是**单实例内** per-request prefix 复用；Mooncake 做的是**跨节点全局池**复用 + 热点复制；可视为 SGLang 的本地版推广到分布式 |
| [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve\|Sarathi-Serve]] | **collocated** chunked prefill inline 到 decode batch | 单节点 | 无 | 与 Mooncake 的 disagg 选择**正反**：Sarathi-Serve 认为 chunked prefill 可消除 disagg 必要性；Mooncake §5 反驳——理由：(1) prefill 需要不同 cross-node 并行设置（CPP/SP），(2) disagg 独立 prefill 节点才有机会 layer-wise overlap 释放 VRAM（Figure 7 实证）。Mooncake 仅在"无需 chunking 且不破 TBT SLO"时才 inline prefill |
| AttentionStore [35] | 分层 KVCache（多 turn） | 跨请求 | — | 与 Mooncake 设计相近，但 AttentionStore 是**独立 cache service**；Mooncake = cache 存储 + cache-aware 调度一体化；Mooncake 强调长上下文下 KVCache 极大、需高带宽传输 + KVCache-centric 全局调度 |
| Prompt Cache [33] | 预计算常用 prompt KVCache | 单服务器 | — | 静态预存，非动态全局调度 |
| Preble [36] | distributed prompt scheduling | 分布式 | — | 同属 KVCache-centric 调度思路，Mooncake 与之 corroborate；但 Mooncake 报告**线上真实复用率只有 ≤50%**（远低于开源 benchmark），特定场景（papers.col chat-to-paper）可达 90% |
| LoongServe [14] | elastic sequence parallelism | 跨节点 SP | — | Mooncake §5.1 明确比较：ESP 需全局通信组、调整时复杂化 Conductor、频繁 SP 通信与 KVCache 跨节点传输争用网络——故 Mooncake 选 CPP 而非 ESP |
| [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod\|Huawei CloudMatrix MaaS]] | Ascend + UB 架构 disagg | — | — | GPU/RoCE vs Ascend/UB 的 disagg 对照（硬件栈不同，但 disagg 思路共鸣） |
| [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter\|Prefill-as-a-Service]] | 跨 DC prefill/decode 进一步 disagg | 跨 DC | — | Mooncake 的跨节点 disagg 在**数据中心内**，PaasS 推到**跨 DC**——Mooncake 是其前置锚点 |

## 跨论文关系（→ MOC 谱系）

- **[[efficient-memory-management-for-large-language-model-serving-with-pagedattention]]** — 单节点 paging 根。Mooncake 的 paged block + 前缀链式 hash（Figure 3）直接继承自 vLLM，但把 block 从"单机内存管理单位"推广为"跨节点调度/迁移/复制/swap 单位"。Mooncake §6.1 明确指出 reuse 逻辑与 vLLM 类似但 vLLM 仅本地。
- **[[sglang-efficient-execution-of-structured-language-model-programs]]** — 单请求 prefix reuse vs Mooncake 全局池。SGLang 的 RadixAttention 在单实例内做 LRU radix tree 自动共享多种 reuse pattern；Mooncake 是该思路的**分布式全局化**，并新增 hot-spot migration 启发式（Figure 6/8 实证必要性）。
- **[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]** — collocated hybrid vs Mooncake disagg 的核心 tradeoff。Mooncake §5 直接反驳 Sarathi-Serve"chunked prefill 消除 disagg 必要性"的论点，给出两条保留 disagg 的理由（多节点并行需求 + VRAM 释放，后者由 Figure 7 layer-wise overlap 实证）。
- **[[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]** — GPU/RoCE vs Ascend/UB disagg 对照。
- **[[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]** — Mooncake 是其前置锚点。Mooncake 把 KVCache 跨节点池化在单 DC 内；PaasS 进一步推到跨 DC，把 prefill 当独立服务。
- **[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]**（SARATHI 原版）— chunked prefill 概念源头，Mooncake `prefill_chunk` 阈值机制即基于此，但用于 disagg prefill 节点内部而非 inline decode batch。
- **[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]** — RAG 场景下 KVCache 复用，与 Mooncake 的 prefix cache reuse 互补（Mooncake 做机制/调度，CacheBlend 做 RAG 融合）。
- **[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]** — EPD disagg 在多模态上的推广；Mooncake 是文本 LLM 的 disagg 锚点。
- **Mooncake 在谱系中的定位**：**跨节点 disagg 锚点**。它是 vLLM (block 概念) → Sarathi (chunked prefill) → DistServe/Splitwise (prefill/decode 分离) 这条线在**生产级、overload 场景、跨节点全局 KVCache 池**方向的集大成，并是 Prefill-as-a-Service (跨 DC) 的直接前置。

## 局限与边界

1. **请求级 output length 预测未做**（§7.4, §10）：当前 system-level prediction 假设统一 `t_d`（Figure 10b 即此假设的实证），是粗近似；request-level 预测留作 future work。这限制 overload 下精度上限。
2. **prefill/decode 实例比例预设**（§8.1.1）：Mooncake-[2P+2D] 在 ArXiv 上 TTFT 不如 [3P+1D]（Figure 11 红橙线）——因负载失衡；论文承认"proportion 可预设但 future 需灵活转换"，未实现动态调整。
3. **trace 复用率上限 ~50%**（§9）：当前 Kimi workload 真实 KVCache 复用率理论上限仅 50%（即使容量与 TTFT SLO 无限），与 Table 1 的 0.51 上限、Figure 6 长尾分布互证；远低于开源 benchmark；cache 收益被高估。仅特定场景（papers.col chat-to-paper）达 90%。
4. **VRAM 释放假设强依赖 layer-wise overlap**（§5.2）：layer-wise prefill 有效性依赖 prefill 是 compute-bound 且逐层可异步——对极短请求或非标准模型架构（如 MLA、hybrid SSM）未必成立。
5. **CPP 仅适配 decoder-only autoregressive**（§5.1）：利用自回归特性做 pipeline，对 encoder/encoder-decoder 模型不直接适用。
6. **dummy model 评估**（§1.2, §8）：所有实验用 LLaMA2-70B 架构 dummy model + 重放 trace，**非真实模型权重**；绝对数字需在生产部署上重新校准。Figure 11/12/13 的对比曲线虽反映趋势，但绝对 RPS 阈值不可直接外推。
7. **未实现请求优先级与异质 SLO**（§10）：调度策略当前不考虑请求优先级与不同 TTFT/TBT SLO 等级，留作 future work。
8. **热点阈值人工调参**（§6.2 脚注 1）：`kvcache_balancing_threshold` 当前手动调整，未来需自适应算法。
9. **跨 DC 未覆盖**：Mooncake disagg 止于单 DC（含跨节点 RDMA），跨 DC 场景由后续 Prefill-as-a-Service 工作（[[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]）承接。
10. **KVCache 压缩/选择/跨层共享/无 KVCache 架构正交**（§10）：Mooncake 不压缩 KVCache，但会从中受益（更大 batch + 更高 hit ratio）；与 SnapKV/H2O/MLKV/Mamba/YOCO 等方向正交互补。
