# Mooncake — 技术点深读（DEEP 2026-08-18）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving · arXiv:2407.00079v4 (3 Sep 2025)
> 作者：Ruoyu Qin, Zheming Li, Weiran He, Mingxing Zhang, Yongwei Wu, Weimin Zheng, Xinran Xu — Moonshot AI ♠ × Tsinghua Univ. ♡。Moonshot AI 的 Kimi 生产级服务平台的实际支撑架构。

## 核心问题

Mooncake 解决的不是单点优化，而是一个**多约束下的商业 MaaS 优化问题**（§1.1）：

1. **目标函数**：最大化 overall effective throughput（直接对应 revenue）；且只有**完整跑完的请求**才计入 goodput，中途被拒的资源全部浪费（§2）——这点比 DistServe/Splitwise 的 goodput 定义更严格。
2. **硬约束**：两类 latency SLO——TTFT（time to first token，预填充阶段指标）与 TBT（time between tokens，解码阶段指标）。实验中 §8.1 设 `TTFT_P90 = 10×`、`TBT_P90 = 5×`（单请求无干扰基线的倍数），实际部署用固定阈值（§2）。
3. **资源约束的现实性**：GPU 供给受限、无法弹性扩容，导致 **overload 是常态而非边缘情况**——这是 Mooncake 区别于以往所有"假设资源充足"的研究（vLLM/Splitwise/DistServe/TetriInfer）的根本前提（§1.1, §7）。
4. **负载异构性**：prefill 是 compute-bound（attention 二次复杂度、MLP 线性，故 prefill 延迟随 input length **超线性**增长，§2 Figure 2 左）；decode 是 memory-bound（每次只处理 1 token，随 batch size **次线性**增长，§2 Figure 2 右）。两者 SLO 不同、资源需求不同，耦合调度互相干扰。

## 关键创新点

1. **KVCache-centric disaggregated 架构（§1, §3）**：不仅 prefill/decode 节点池分离，更将 GPU 节点中**未被充分利用的 CPU/DRAM/SSD/RDMA 资源**聚合成 disaggregated KVCache 层——以零额外硬件成本提供近 GPU 的 prefix caching 容量与带宽。KVCache 被当作"一等公民"在实例间显式流转：global scheduler **Conductor** 为每个请求选择一对 prefill + decoding 实例，按 4 步执行（§3）：(1) KVCache Reuse——把可复用 prefix block 从远端 CPU DRAM 加载进 GPU；(2) Incremental Prefill——若未缓存 token 数超过 `prefill_chunk` 阈值（>1000 tokens，§3 步骤 2），按 chunk 流水线执行；(3) KVCache Transfer——逐层 KVCache 流式传输到 decoding 节点 CPU 内存，与 prefill 计算重叠；(4) Decoding——KVCache 全部到齐后加入 continuous batching，decoding 节点本地调度器**二次校验** TBT SLO（因为 prefill 期间负载已变化），不满足则拒——此时 prefill 成本被浪费，这正是 §7 Early Rejection 的动机。

2. **Paged KVCache + 全局 hash 去重（§3 Figure 3）**：CPU 内存中 KVCache 以 paged block 存储，每个 block 的 hash = `hash(本 block tokens) ∥ 前一 block 的 hash`（前缀链式哈希），从而**等价的前缀产生等价的 hash 链**——可直接做全局 prefix 去重与跨请求复用。block size 在 trace 中为 **512 tokens**（§4.1）。这与 vLLM 单机 PagedAttention 的 block 概念一致，但 Mooncake 把 block 提升为**跨节点迁移/复制/swap 的全局调度单位**。

3. **Chunked Pipeline Parallelism (CPP) for long-context prefill（§5.1）**：长上下文（8k→1M，§5.1）下 input 可达 output 的 10–100 倍，TTFT 是关键瓶颈。三种多节点并行方案对比：
   - 跨节点 TP：每层 2 次 RDMA all-reduce，MFU 大降。
   - Sequence Parallelism (SP, Ring/Striped Attention)：每层至少 1 次跨节点通信，MFU 仍劣于单节点 TP；且需 elastic SP 动态调整 partition，复杂化 Conductor 决策（与 KVCache 复用率、SLO 违反联合调度冲突）。
   - **CPP**：将 prefill 节点按 X 个一组组成 pipeline group，请求 token 切成 ≤`prefill_chunk` 的 chunk，不同 chunk 在不同节点**同时处理**——只需在 pipeline stage **边界**通信（类训练中的 PP），可被计算 overlap，网络资源与 KVCache 跨节点传输不争用；天然适配短/长上下文，无需频繁动态重分区。论文称这是 **inference 阶段 CPP 的首次应用**（训练阶段已有 TeraPipe [24]）。

4. **Layer-wise Prefill + 异步 KVCache 流式 overlap（§5.2）**：prefill 逐层计算（compute-bound），KVCache 的 load/store 经 `launch`/`wait` 异步执行——每层 attention 前等待本层 KVCache 异步加载完成并触发下一层异步加载；attention 完成后启动本层异步存储；全部计算完成后等待所有存储完成。效果（Figure 7）：layer-wise prefill 的存 KVCache 额外延迟**几乎为零**（serialized 存储随 seq len 线性上升，layer-wise 与"不存储"曲线几乎重合）；且使 prefill 调度**可忽略 VRAM 容量约束**（只需装得下一个请求），调度器只看 KVCache 分布 + DRAM 可用量。

5. **KVCache-centric 调度算法 (Algorithm 1, §6.1)**：Conductor 为每个 prefill 实例估计 `TFT = T_transfer + T_queue + T_prefill`（依赖该实例上 prefix_len 命中长度），选最小 TFT 实例；若 >SLO 直接返回 **HTTP 429**。关键设计：定义 `kvcache_balancing_threshold`——若当前实例本地 prefix_len 与全局最优 best_prefix_len 差距小于阈值，走 **cache-aware** 分支（直接本地算，不跨机拉）；若差距大于阈值，走 **cache-balancing** 分支（从 best_matched_instance 远端拉 KVCache 到本地）。prefill 时间预测用离线数据训练的预测模型（Transformer 计算模式规律，误差小）；queue 时间 = 队列中所有请求 prefill 时间之和；TTFT 各实例**并行计算**，开销可忽略。

6. **启发式自动 hot-spot migration（§6.2）**：不去预测未来 block 使用（workloads 高度动态、不可预测），而是用**两个简单启发式**实现隐式复制：(a) 当最优远端 prefix 不在本地、但额外 prefill 时间 < 传输时间时，请求转发到本地实例并**主动拉取 KVCache 本地化**；(b) 当 `best_remote_prefix_len ≤ local_prefix × threshold` 时宁可重算不拉。两条规则自然使**热点 block 被复制到多机**、冷 block 被 swap out。实验（§6.2 Figure 8，8 prefill + 8 decode，重放 23k 请求）：平均 TTFT 分别为 random=92.07s、load-balancing=60.41s、cache-aware=14.36s、**KVCache-centric=6.26s**——cache-aware 比 load-balancing 降 4×，再加 cache load balancing 再降 2.3×。

7. **Early Rejection + Prediction-based Early Rejection（§7）**——overload 场景的核心创新：
   - **load 定义**：disaggregated 架构下，prefill 与 decode 独立处理，故直接用 **SLO 满足度**作为 load——比较实例预测的最大 TTFT/TBT 与 `l_tft`/`l_tbt`（§7.1），而非传统的"请求数/容量比"。
   - **Early Rejection（§7.2）**：把 decoding 实例的 load 评估**提前到 prefill 开始前**，取 prefill pool 与 decoding pool 中较大 load 决定是否接收——避免"prefill 做完才发现 decode 满载被拒、prefill 算力白费"。
   - **load fluctuation 病态（§7.3, Figure 9/10a）**：直接 Early Rejection 会导致 prefill 与 decoding 负载**反相震荡**——Stage 1 双低大量接收→prefill 满；Stage 2 decode 满拒、prefill 闲；Stage 3 decode 完成降、prefill 又满……根因是 decode load 预测相对实际执行有**时滞**。
   - **Prediction-based Early Rejection（§7.4）**：预测"prefill 结束后" 的 decode load 来消震荡。两层预测：(1) **Request-level**——预测单请求 output length 反推 TBT/TTFT，但成本高/精度低，特别是 overload 下；(2) **System-level**（Mooncake 当前采用）——假设每个请求 decode 阶段耗时统一 `t_d`，t 时刻把 prefill 能完成的请求加入、把 t 前完成的移出，算所有 decode 实例平均 TBT/`l_tbt` 比。精度要求低、更适合 overload。

8. **trace 开源（§4）**：首个可用于真实复用分析的 1 小时采样 trace，**23,608 条**请求，字段 timestamp(0–3,600,000 ms)、input_length、output_length、hash_ids（remapped block hash，block size 512）。统计：平均 input **7,590 tokens**、平均 output **182 tokens**、input/output 比约 **720**（反映 Kimi 长上下文特性）。cache hit ratio 随容量 1k→50k blocks 从 30% 升到 50%（再增收益递减）；**超 50% 的 block 从未被使用**而少数 block 被访问数万次（Figure 6）——热点复制是刚需。

## 表格（原文结构化）

### Table 1 — Cache hit rates under different policies/capacities (§4.2)
| Block capacity | Inf | 100000 | 50000 | 30000 | 10000 | 1000 |
|---|---|---|---|---|---|---|
| LRUCache | 0.51 | 0.51 | 0.50 | 0.48 | 0.40 | 0.30 |
| LFUCache | 0.51 | 0.51 | 0.49 | 0.43 | 0.35 | 0.30 |
| LengthAwareCache | 0.51 | 0.50 | 0.48 | 0.42 | 0.35 | 0.30 |

结论：本 trace 下 LRUCache 最优（temporal proximity），50% 命中率是当前 workload 的实际上限。

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

### 端到端关键结果汇总
| 场景 | 配置 | 结果 |
|---|---|---|
| ArXiv Summ. | Mooncake-[3P+1D] vs vLLM-[4M] | +20% throughput（满足 SLO） |
| L-Eval | Mooncake-[3P+1D] vs vLLM-[4M] | +40% throughput（prefix caching 加成） |
| Simulated (16k–128k) | Mooncake vs vLLM | +50% ~ +525% throughput（vLLM 长 ctx 下解码被打断、被迫单条处理） |
| Real Workload | Mooncake-[10P+10D] vs vLLM-[20M] | TTFT 两者近 100% 满足；TBT Mooncake ~100%、vLLM 仅 57%；Mooncake 处理多 75% 请求。TTFT 上限 30s，TBT 上限 0.1s/token |
| 调度实验 | KVCache-centric vs random/load-balancing | TTFT 6.26s vs 92.07s/60.41s（Figure 8） |

## 与同类对比

| 系统 | 架构 | KVCache 池范围 | Overload 处理 | 区别 |
|---|---|---|---|---|
| **Mooncake** | prefill/decode disaggregated + 分层 KVCache 池 (GPU/CPU/DRAM/SSD) | **跨节点全局** | Early Rejection + Prediction（核心创新） | 商业生产级（Kimi），KVCache 是调度一等公民 |
| [[efficient-memory-management-for-large-language-model-serving-with-pagedattention\|vLLM]] | coupled prefill+decode，continuous batching | 单节点 PagedAttention | 无（假设资源充足） | block 概念根——Mooncake 把 block 推广为跨节点迁移单位；Mooncake 的 prefix match 逻辑与 vLLM 类似但 vLLM 只支持本地 cache |
| DistServe [8] | disaggregated | 主要单节点阶段分离 | goodput 优化但无 reject 策略 | Mooncake 共享 disagg 直觉，但 DistServe 专注资源分配+并行策略，不做跨节点 KVCache 池与 overload 拒绝 |
| Splitwise [7] | disaggregated phase splitting | — | 无 | Mooncake 早期开发同期出现，启发 Mooncake；未做 KVCache-centric 全局调度 |
| TetriInfer [9] | chunked prefill + 两阶段 disagg | — | 两阶段预测调度 | 与 Mooncake 思路接近，但无 overload-oriented rejection 与全局 hot-spot migration |
| [[sglang-efficient-execution-of-structured-language-model-programs\|SGLang]] | coupled | 单请求 RadixAttention (LRU radix tree) | 无 | SGLang 做的是**单实例内** per-request prefix 复用；Mooncake 做的是**跨节点全局池**复用 + 热点复制；可视为 SGLang 的本地版推广到分布式 |
| [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve\|Sarathi-Serve]] | **collocated** chunked prefill inline 到 decode batch | 单节点 | 无 | 与 Mooncake 的 disagg 选择**正反**：Sarathi-Serve 认为 chunked prefill 可消除 disagg 必要性；Mooncake §5 反驳——理由：(1) prefill 需要不同 cross-node 并行设置（CPP/SP），(2) disagg 独立 prefill 节点才有机会 layer-wise overlap 释放 VRAM。Mooncake 仅在"无需 chunking 且不破 TBT SLO"时才 inline prefill |
| AttentionStore [35] | 分层 KVCache（多 turn） | 跨请求 | — | 与 Mooncake 设计相近，但 AttentionStore 是**独立 cache service**；Mooncake = cache 存储 + cache-aware 调度一体化；Mooncake 强调长上下文下 KVCache 极大、需高带宽传输 + KVCache-centric 全局调度 |
| Prompt Cache [33] | 预计算常用 prompt KVCache | 单服务器 | — | 静态预存，非动态全局调度 |
| Preble [36] | distributed prompt scheduling | 分布式 | — | 同属 KVCache-centric 调度思路，Mooncake 与之 corroborate；但 Mooncake 报告**线上真实复用率只有 ≤50%**（远低于开源 benchmark），特定场景（chat-to-paper papers.col）可达 90% |
| LoongServe [14] | elastic sequence parallelism | 跨节点 SP | — | Mooncake §5.1 明确比较：ESP 需全局通信组、调整时复杂化 Conductor、频繁 SP 通信与 KVCache 跨节点传输争用网络——故 Mooncake 选 CPP 而非 ESP |
| [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod\|Huawei CloudMatrix MaaS]] | Ascend + UB 架构 disagg | — | — | GPU/RoCE vs Ascend/UB 的 disagg 对照（硬件栈不同，但 disagg 思路共鸣） |
| [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter\|Prefill-as-a-Service]] | 跨 DC prefill/decode 进一步 disagg | 跨 DC | — | Mooncake 的跨节点 disagg 在**数据中心内**，PaasS 推到**跨 DC**——Mooncake 是其前置锚点 |

## 跨论文关系（→ MOC 谱系）

- **[[efficient-memory-management-for-large-language-model-serving-with-pagedattention]]** — 单节点 paging 根。Mooncake 的 paged block + 前缀链式 hash 直接继承自 vLLM，但把 block 从"单机内存管理单位"推广为"跨节点调度/迁移/复制/swap 单位"。Mooncake §6.1 明确指出 reuse 逻辑与 vLLM 类似但 vLLM 仅本地。
- **[[sglang-efficient-execution-of-structured-language-model-programs]]** — 单请求 prefix reuse vs Mooncake 全局池。SGLang 的 RadixAttention 在单实例内做 LRU radix tree 自动共享多种 reuse pattern；Mooncake 是该思路的**分布式全局化**，并新增 hot-spot migration 启发式。
- **[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]** — collocated hybrid vs Mooncake disagg 的核心 tradeoff。Mooncake §5 直接反驳 Sarathi-Serve"chunked prefill 消除 disagg 必要性"的论点，给出两条保留 disagg 的理由（多节点并行需求 + VRAM 释放）。
- **[[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]** — GPU/RoCE vs Ascend/UB disagg 对照。
- **[[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]** — Mooncake 是其前置锚点。Mooncake 把 KVCache 跨节点池化在单 DC 内；PaasS 进一步推到跨 DC，把 prefill 当独立服务。
- **[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]**（SARATHI 原版）— chunked prefill 概念源头，Mooncake `prefill_chunk` 阈值机制即基于此，但用于 disagg prefill 节点内部而非 inline decode batch。
- **[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]** — RAG 场景下 KVCache 复用，与 Mooncake 的 prefix cache reuse 互补（Mooncake 做机制/调度，CacheBlend 做 RAG 融合）。
- **[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]** — EPD disagg 在多模态上的推广；Mooncake 是文本 LLM 的 disagg 锚点。
- **Mooncake 在谱系中的定位**：**跨节点 disagg 锚点**。它是 vLLM (block 概念) → Sarathi (chunked prefill) → DistServe/Splitwise (prefill/decode 分离) 这条线在**生产级、overload 场景、跨节点全局 KVCache 池**方向的集大成，并是 Prefill-as-a-Service (跨 DC) 的直接前置。

## 局限与边界

1. **请求级 output length 预测未做**（§7.4, §10）：当前 system-level prediction 假设统一 `t_d`，是粗近似；request-level 预测留作 future work。这限制 overload 下精度上限。
2. **prefill/decode 实例比例预设**（§8.1.1）：Mooncake-[2P+2D] 在 ArXiv 上 TTFT 不如 [3P+1D]——因负载失衡；论文承认"proportion 可预设但 future 需灵活转换"，未实现动态调整。
3. **trace 复用率上限 ~50%**（§9）：当前 Kimi workload 真实 KVCache 复用率理论上限仅 50%（即使容量与 TTFT SLO 无限），远低于开源 benchmark；cache 收益被高估。仅特定场景（papers.col chat-to-paper）达 90%。
4. **VRAM 释放假设强依赖 layer-wise overlap**（§5.2）：layer-wise prefill 有效性依赖 prefill 是 compute-bound 且逐层可异步——对极短请求或非标准模型架构（如 MLA、hybrid SSM）未必成立。
5. **CPP 仅适配 decoder-only autoregressive**（§5.1）：利用自回归特性做 pipeline，对 encoder/encoder-decoder 模型不直接适用。
6. **dummy model 评估**（§1.2, §8）：所有实验用 LLaMA2-70B 架构 dummy model + 重放 trace，**非真实模型权重**；绝对数字需在生产部署上重新校准。
7. **未实现请求优先级与异质 SLO**（§10）：调度策略当前不考虑请求优先级与不同 TTFT/TBT SLO 等级，留作 future work。
8. **热点阈值人工调参**（§6.2 脚注 1）：`kvcache_balancing_threshold` 当前手动调整，未来需自适应算法。
9. **跨 DC 未覆盖**：Mooncake disagg 止于单 DC（含跨节点 RDMA），跨 DC 场景由后续 Prefill-as-a-Service 工作（[[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]）承接。
10. **KVCache 压缩/选择/跨层共享/无 KVCache 架构正交**（§10）：Mooncake 不压缩 KVCache，但会从中受益（更大 batch + 更高 hit ratio）；与 SnapKV/H2O/MLKV/Mamba/YOCO 等方向正交互补。
