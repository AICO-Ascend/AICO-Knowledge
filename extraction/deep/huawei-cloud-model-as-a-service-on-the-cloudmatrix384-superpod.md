# Huawei CloudMatrix384 — 技术点深读（DEEP 2026-08-18）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Huawei Cloud Model-as-a-Service on the CloudMatrix384 SuperPod · arXiv:2508.02520

## 核心问题

大规模 MoE LLM（DeepSeek/Kimi K2/Qwen/GLM）与 SuperPod 级硬件（数百 NPU、全局共享内存）相遇时，传统 LLM serving 系统无法利用底层硬件特性，出现三重新挑战（§1）：

1. **MoE 细粒度路由同步**：数百 NPU 上的 expert routing、同步、load balancing，straggler 会放大为系统级延迟（dispatch/combine 占 MoE 执行时间 ≥25%，§3.2）。
2. **SuperPod 硬件未被利用**：CloudMatrix384 提供 global shared memory + uniform low-latency 跨 NPU 访问，但传统 serving 基于 host-centric 网络语义（NCCL/verbs 风格），无法直接暴露内存语义。
3. ** disaggregation 缺失**：prefill（compute-bound）与 decode（memory-bound）争用资源；MoE（stateless，随 batch size scale）与 attention（stateful KV cache，随 seq len scale）资源不对称，colocated 部署造成资源浪费与互相干扰。

生产目标 SLA（§1、§7.2）：TTFT < 2 s，TPOT 35 ms（多数情况），DeepSeek-R1 支持输入至 96K、reasoning 32K、输出 32K（128K context window）。峰值 decode 配置：**2400 tokens/s per Ascend 910C chip @ ~50 ms TPOT**（§Abstract、§7.1）。

## 关键创新点

1. **Transformerless 解耦执行架构**（§1、§5）。将 transformer 拆为 attention / feedforward / MoE 独立模块，跑在专用 NPU 上。三阶段演进（Figure 16）：(a) Disaggregated Prefill-Decode（§5.1），(b) Disaggregated MoE-Attention（§5.2），(c) Vision: dataflow serving（去全局同步，§5.3）。机制：prefill 用 TP=4 + eager graph + sequence parallel + prefix cache；decode 用 TP=1 + static graph。DeepSeek-V3/R1 部署在 768 die：288 die 跑 EP288（256 routed + 32 shared experts），480 die 跑 MLA（§5.2）。

2. **XCCL 内存语义通信库**（§3）。基于 CloudMatrix384 global shared memory 构造 far-memory 风格原语，非传统 network verbs（对照 DeepEP [2]）。
   - **P2P send/recv**（§3.1）：每 NPU on-chip memory 三分区——app data area、metadata area、managed data area（ring buffer）。metadata 32B/field，含 eventID/chunkID/tailPtr；总 fields 数 = 384×2×48×2 ≈ 74K，metadata 总 4 MB。8 步协议：MTE2 读→MTE3 写远端 managed data→更新 tailPtr→poll ack。ping-pong unified buffer 使 MTE2/MTE3 并行。性能：<1 MB 负载 <20 μs（2 AIV cores 即可）；9 MB 用满 48 AIV cores 比 2 cores 快 >2.5×。可扩展到 ~300K NPU pair。
   - **MoE dispatch/combine**（§3.2）：pull-based，两阶段——先广播每 rank 应收 token 数，再 pull 数据。dispatch 内联 FP16/BF16→INT8 量化。EP128 batch-per-die=96 时 global batch=12,288。小 batch dispatch 略慢于 combine（量化开销），batch≥32 后 dispatch 反超（数据量减半）。
   - **A2E/E2A**（§3.3）：disaggregated MoE-Attention 专用，处理 attention NPU 与 expert NPU 数量不对称（如 288 expert vs 160 attention）。

3. **Trampoline Forward 机制**（§3.3、§5.2）。针对 attention/expert NPU 不对称：选与 attention NPU 数量相等的 expert NPU 作 trampoline，先收全部数据再转发给其余 expert NPU。两段式路由（A2E→A2E'、E2A→E2A'）降低 metadata fan-out 与带宽不平衡。实测（§3.3）：3 DP domain × 160 DP group（TP=1）+ 288 expert NPU，per-die batch 96 → global batch 46,080，A2E=172 μs，E2A=193 μs。

4. **NPU-Direct URMA**（§3.3）。类 GPU IBGDA：AIV core 直接向 DMA engine 发 remote memory 请求，绕过 host CPU 与 AI CPU。虽启动延迟高于 MTE2/MTE3，但三优势：(1) 释放 AIV 资源；(2) 适合高吞吐（DMA 支持数 GB，MTE 受 unified buffer 数百 KB 限制）；(3) 避免与 compute stream 抢 MTE2。

5. **FlowServe 去中心化 DP group 抽象**（§4.1、§4.2）。受 SGLang [24] 启发。每 DP group 自含完整 pipeline（tokenizer、API parser、SPMD executor、RTC、DistFlow），跨 DP 无通信。单 FlowServe 实例可跨整 SuperPod（48 server / 768 die）。TE-shell 仅保留三职责：跨 DP 请求分发（§4.3）、触发 expert LB（§4.5）、健康检查协调（§6.1）。**Output shortcutting**：每 DP master fork 子进程专做 detokenization + 流式解析，直连前端，避免中心化输出瓶颈。

6. **DP Load Balancing**（§4.3）。Prefill 用单级协作调度（leader @ DP-0 all-gather 状态，cost model 含 prefix cache hit rate）；decode 用 KV cache 用量最低 + 排除满 batch group 的策略，TE-shell 实时跟踪 pending count 与 KV stats。

7. **Proactive GC 降 jitter**（§4.4）。首 dispatch（DeepSeek 第 4 层 / Kimi K2 第 2 层）全局同步首次发生，jitter 可 >100 ms。三手段：core pinning、PTA caching（bypass guard check）、manual Python GC（每数百 forward 触发）。

8. **EPLB（Expert Placement Load Balancing）**（§4.5）。数据驱动周期性复制 hot expert。四步：(1) Collect kernel（gating 后插）统计每 expert 每 NPU token 数，每分钟上报；(2) EPLB 算法——`h_{ℓ,t}=argmax_e token_count[ℓ][e][t]`，`L_ℓ=Σ_{t∈T} token_count[ℓ][h_{ℓ,t}][t]`，在冗余预算 R 内贪心选使模拟总负载最小的 expert 复制；(3) 四阶段热重配（prefetch→disable slot→async load→restore mapping）；(4) communication-free token rotation：按 token 在 batch 中位置轮转映射到 replica，无需跨 NPU 通信。效果（Figure 11）：20% experts 承载超均值负载，最热 expert 30× 均值；EPLB 使 forward 延迟降 >40%。

9. **MTP（Multi-Token Prediction）**（§4.6）。5 步紧优化循环：(1) MTP forward 生成 k draft；(2) sample；(3) 主模型 verify；(4) sample；(5) 检查 logits 决定接受。单 MTP 层 acceptance 70–90%，固定 batch 下降延迟 ≤40%。训练第二 MTP（冻结主模型+原 MTP，28 万内部样本）使 tokens/step 从复用权重的 2.26 提升到 2.35（+9%）。

10. **INT8 量化**（§4.7）。910C 不原生支持 FP8，DeepSeek-R1/V3 原训练 FP8 → INT8 PTQ，融合 SmoothQuant [22] + GPTQ [4]。MLA/MoE/MLP 全量化；activation token-wise、weight channel-wise；用 hardware-accelerated `npu_quant_matmul` (QMM)。MLA 量化 Wq_a/Wkv_a/Wq_b/Wo；KV cache 非 RoPE 部分 INT8（数值稳定），低敏感 attention 层全 INT8 计算；MoE dispatch 通信 fused 量化，每 expert 校准至少 n=4 样本（典型 40–128）。up_proj/gate_proj fused 成单 kernel。

11. **Disaggregated MoE-Attention 三技术**（§5.2）：(a) A2E/E2A + trampoline；(b) **DP domain 抽象**——多 DP group 封装，任一时刻仅一个 domain 与 MoE NPU 交互；inter-DP 并行（domain 间）+ intra-DP 并行（microbatch，每 domain 2 microbatch × 96）互补，避免过度 microbatch 降有效 batch；(c) **persistent kernel 零开销调度**——MoE NPU 跑 3 concurrent stream（A2E 接收 / MoE 计算 / E2A 发送）的 busy-polling persistent kernel，不回 CPU，因 MoE kernel 微秒级、CPU 交互毫秒级会成瓶颈。

12. **可靠性：三阶段演进**（§6）。Stage 1 Restart-the-World（小集群 4P1D，全引擎重启，decode 优先于 prefill 重启）；Stage 2 P/D Separate Failover（共享集群，"kill-P-to-preserve-D"策略，配合 EP-LB 做 decode 垂直缩容——减 DP group 与 EP rank，每 expert 留至少一 replica）；Stage 3 Fine-Grained（网络抖动→token recomputation：全员 rollback 上一 iteration，专用线程广播 rollback signal；on-chip memory fault→与 CANN 协作重映射虚拟内存、mask 故障区）。检测：multi-tier heartbeat（control plane→TE shell→DP master，单线程 event loop）+ link probing（注入 dummy payload 区分 decode 饱和 vs link 故障）。

## 表格（原文结构化）

### 表1：SuperPod 硬件规格（§2.2）
| 项目 | 规格 |
|---|---|
| SuperPod 组成 | 48 server，384 Ascend 910C chip |
| 单 server | 多 CPU、多 NIC、8 × 910C NPU |
| 三类网络 | VPC（外联）、RoCE（scale-out，跨 SuperPod/910B）、UB（scale-up，全互联，带宽数倍于 RoCE） |
| UB 特性 | global shared memory（CPU DRAM + NPU on-chip 统一寻址）；消除 intra-server NUMA |
| 算力/内存 | 数百 PFLOPs FP16；数 TB on-chip memory；TB/s 级 memory bandwidth |
| 910C chip | 2 die，片内 NoC 互联；DaVinci 架构 |
| 每 die | AIC + AIV core（等数）、若干 AI CPU、多 DMA engine；AIV 含 KB 级 unified buffer + MTE2/MTE3 |

### 表2：XCCL 三类原语（§3）
| 原语 | 用途 | 数据结构 | 关键性能 |
|---|---|---|---|
| send/recv | disaggregated PD KV 迁移、sequence parallel、npu-fork | 74K metadata field × 32B，4 MB metadata；per-pair ring buffer | <1 MB <20 μs（2 AIV）；9 MB 用 48 cores 快 >2.5× |
| dispatch/combine | colocated EP，top-k 路由/聚合 | per-rank 32B metadata（eventID/offset/token_count）；fixed-size per-rank block | 占 MoE 时间 ≥25%；EP128 bsz96→global 12,288 |
| A2E/E2A | disaggregated MoE-Attention | 同 dispatch + trampoline 两段路由 | global 46,080 batch：A2E 172 μs，E2A 193 μs |

### 表3：DeepSeek-R1 decode 单 iteration 延迟分解（§7.1，Figure 20，DP288 EP288，bsz 60/die，~3K seq）
| 算子 | 占比 | 平均 μs | 最小 μs | 最大 μs |
|---|---|---|---|---|
| QuantBatchMatmul | 22.1% | — | — | — |
| MultiLatentAttention | 21.8% | — | — | — |
| MoE-Combine | 20.4% | 312 | 165 | 2939 |
| MoE-Dispatch | 15.3% | 234 | 185 | 1231 |
| Others | 11.7% | — | — | — |
| MlaPreprocess | 8.7% | — | — | — |
| **iteration 合计** | — | ~93 ms（含 MTP forward+sample+主模型+final sample）；调度间隙 ~2 ms；MTP acceptance ~90% → TPOT = (93+2)/1.9 ≈ 50 ms |

### 表4：两种 decode 部署对比（§7.1）
| 配置 | NPU die | 组织 | per-die batch | global batch | tokens/s/chip | TPOT |
|---|---|---|---|---|---|---|
| Colocated PD | 288 | DP288 EP288（256 routed+32 shared，每 die 1 expert+1 redundant） | 60 | 17,280 | 2400 | 50 ms |
| Disaggregated MA | 768 | 3 DP domain × 160 DP group（TP=1）attn + 288 EP288 expert | 96 | 46,080 | 2400 | ~49 ms |

### 表5：生产部署与 SLA（§7.2）
| 项 | 值 |
|---|---|
| 部署 | 16 × 910C server；4 prefill TE（DP8 EP32，每 TE 2 server）+ 1 decode TE（DP128 EP128，8 server） |
| 工作负载 | 输入 0–64K（均 13K），输出均 2.1K |
| TTFT | 900 ms |
| 平均 TPOT | 34.8 ms |
| DeepSeek-R1 长序列上限 | 输入 96K / reasoning 32K / 输出 32K（128K context）；长输入处理可达 30 分钟，独立资源隔离 |

### 表6：可靠性演进（§6.2）
| Stage | 策略 | 局限/特点 |
|---|---|---|
| 1 Restart-the-World | 小集群 4P1D，全引擎重启；decode 优先 | 资源利用率低；单 prefill 故障拖垮关联 decode |
| 2 P/D Separate Failover | 共享集群、独立 failover；kill-P-preserve-D；EP-LB 垂直缩容 | 需 KV cache 处理与 replica 管理 |
| 3 Fine-Grained | 网络抖动→token recomputation（全员 rollback）；mem fault→CANN 虚拟内存重映射 | 系统不中断，仅个别请求失败 |

## 与同类对比

- **vs Mooncake [18] / MemServe [7]**（§5.1）：同为 disaggregated PD，但 Mooncake 是 KVCache-centric、GPU/RoCE 体系；xDeepServe 针对 SuperPod UB fabric + 大 MoE expert parallelism，且做异构 NPU（prefill 跑 910B+910C，decode 仅 910C）。
- **vs Splitwise [17] / TetriServe [8] / DistServe [25]**（§5.1）：同 PD 解耦动机，但本文面向 SuperPod 规模 + 大 MoE，并进一步解耦 MoE-Attention。
- **vs FastDecode [6] / Lamina [1] / InstAttention [16] / MegaScale-Infer [26]**（§5.2）：同 attention-FFN 解耦思想，但前者小模型/小规模；本文在 768 die SuperPod 规模验证 DeepSeek-V3/R1，并补 trampoline/DP domain/persistent kernel 三机制。
- **vs DeepEP [2]**（§3.2）：DeepEP 用传统 network-level verbs；XCCL 用 far-memory 语义 over global shared memory，更贴合 UB fabric。
- **vs SGLang [24]**（§4.1）：DP group 抽象受 SGLang 启发，但 FlowServe 扩展到 SuperPod 规模并去中心化。
- **vs vLLM EAGLE MTP [13]**（§4.6）：EAGLE 默认调度有 stall，FlowServe 用自定义 5 步 pipeline 消除 CPU bubble；并训练专用第二 MTP（2.35 tokens/step）。
- **vs GPU-based 系统（Mooncake/SGLang/vLLM）**：本质差异——Ascend 910C NPU + UB shared memory + 内存语义 XCCL，而非 GPU + RDMA/NCCL。910C 无 FP8，靠 INT8 PTQ 弥补。

## 跨论文关系（→ MOC 谱系）

- → [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]：同为 disaggregated PD 谱系；Mooncake 是 GPU/KVCache-centric 代表，本文是 Ascend/SuperPod 内存语义代表，对照两种 disagg 路线。
- → [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]：本文 prefill 调度讨论 chunk-prefill 的 overhead 与替代（单级协作调度 + cost model），形成对照。
- → [[sglang-efficient-execution-of-structured-language-model-programs]]：DP group 抽象灵感来源 [24]；可对比去中心化扩展策略。
- → [[ascend-950-npu-architecture-whitepaper]]：910C 是 950 的前代，本文提供 910C 在 SuperPod serving 中的实测行为（MTE2/MTE3、DMA、AIV/AIC、URMA），为 950 架构演进提供生产基线。
- → [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]]：本文 KV cache 迁移（P2P）、KV INT8 量化、non-RoPE 量化是 survey 中 disagg + quant 方向的工业实例。
- 谱系定位：**serving-system / NPU-cluster 主题**，Ascend 系（vs Mooncake/SGLang 的 GPU 系）；disaggregation 三阶演进的工业落地。
- 关联参考（论文内引用，非库内）：DeepEP [2]、DaVinci [14]、LegoOS [19]（disaggregation 原则）、FaRM [3]（far-memory 协议原型）、DeepSeek [15]、Kimi K2 [12]、Qwen3 [23]、GLM-5 [5]。

## 局限与边界

- **无 FP8 原生支持**（§4.7）：910C 不支持 FP8，DeepSeek 原 FP8 模型必须 INT8 PTQ，依赖 SmoothQuant+GPTQ 补偿精度损失，论文未给出端到端精度对比数据（仅给量化策略）。
- **全局同步未消除**（§5.3）：disaggregated MoE-Attention 仍依赖 A2E/E2A 同步屏障，单 straggler/故障可级联卡死全系统；dataflow serving 仍是 vision，未落地。
- **dispatch/combine 方差大**（§7.1，Figure 20）：max 可达 min 的 10×（dispatch 185→1231 μs；combine 165→2939 μs），源于吸收 MLA 与 MoE 跨 NPU/Dexpert 不均，仍是尾延迟风险。
- **EPLB 周期性、非实时**（§4.5）：每分钟采样一次，对突发负载倾斜响应滞后；redundancy slot 预算 R 有限，极端 hot expert 可能仍不均。
- **metadata 固定 4 MB、非零拷贝**（§3.1）：当前实现数据需在 app data area 与 managed data area 间拷贝（非零拷贝版本另存但未默认）。
- **第二 MTP 仍需离线训练**（§4.6）：复用权重仅 2.26 tokens/step，专用第二 MTP 需 28 万样本训练，部署成本与泛化性未充分讨论。
- **生产 TPOT 35 ms vs 峰值 50 ms**（§1、§7.1 vs §7.2）：峰值 2400 tokens/s/chip 在 50 ms TPOT 下达成；生产 34.8 ms TPOT 配置的 per-chip 吞吐未公布，难以直接对照。
- **异构 prefill 跨 fabric**（§5.1）：910B→910C 跨 RoCE/VPC 传 KV，SLA 满足但带宽低于 UB，扩展受 fabric 限制。
- **可靠性评估缺失**（§6）：仅给机制，未给 MTTR/可用率数值或故障注入实验。
- **测评模型单一**（§7）：实测以 DeepSeek-R1/V3 为主；Kimi K2 / Qwen / GLM / MiniMax 仅声明支持，未给同口径 benchmark。
