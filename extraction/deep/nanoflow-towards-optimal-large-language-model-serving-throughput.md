# NanoFlow — 技术点深读（DEEP 2026-08-18）

> 全要素深读笔记：文本技术点提炼 + 跨论文关系。独立文件，extract_phase1 重跑不丢。
> 论文：NanoFlow: Towards Optimal Large Language Model Serving Throughput · arXiv:2408.12757v2 (25 May 2025)

## 核心问题

业界普遍认为 LLM serving 是 memory-bandwidth-bound（模型权重 + KV-cache 每次迭代全量加载，每步只产 1 token/seq）。NanoFlow 首先纠正这一**认知误区**：尽管 self-attention（decode 阶段）单算子 memory-bound，但**端到端 LLM serving 在常见 workload 上整体是 compute-bound**（§3.3，Figure 3）。

但纠正认知后暴露出真正的性能裂缝（§3.6）：现有 serving engine（vLLM / DeepSpeed-FastGen / TensorRT-LLM / SGLang）**单个算子在其瓶颈资源上利用率高（~80%），却因算子顺序执行导致 GPU compute 总利用率仅 ~40%**。机制如下（§3.6 + Figure 4）：
- transformer 一层内 dense GEMM（compute-bound）、decode attention（memory-bound）、AllGather/AllReduce（network-bound）**在单个大 batch 上串行**执行；
- 不同算子瓶颈资源不同，串行执行时其他资源空闲 → 形成 "WASTED" pipeline bubble，compute（最受限资源）被大量浪费。
- 实证后果（§3.6 + §6.2）：vLLM / DeepSpeed-FastGen / TensorRT-LLM 离线吞吐仅达**理论最优的 22.0% / 22.9% / 37.8%**（Figure 7，LLaMA-2-70B 8×A100，最优 = 1857 tokens/s/GPU）。

NanoFlow 攻击的核心问题：**如何在单 GPU 内部把 compute/memory/network 三类异质算子重叠起来，逼近 compute 资源的理论上限吞吐**，而不是跨设备扩容。

## 关键创新点

### 1. Nano-batching + intra-device parallelism（§3.7, §4）
- **机制**：把原 dense batch（如 2048）切成多个 nano-batch（如 0-768、768-2048），对每个 nano-batch 各起一份相同算子（nano-operation），因 nano-batch 间无数据依赖，compute-bound / memory-bound / network-bound nano-op 可**在同一 device 上并行**执行，对每种资源分别占满。代价是模型权重需重复加载多次，但只要整体 compute-bound（TR<1，§3.3），多余 memory I/O 可被 pipeline 隐藏。
- **效果**：相对 vLLM/DeepSpeed-FastGen/TensorRT-LLM 平均 **1.91×** 吞吐（abstract + §6.2），达到理论最优的 **50%-72%**（多模型，§6.6），LLaMA-2-70B 最佳 case 达 **68.5%**（§6.2）。

### 2. 两阶段 auto-search（MILP）自动构造 intra-device pipeline（§4.1）
- **机制**：用 mixed integer linear programming 自动决定 nano-operation 的 (a) 数量、(b) batch size、(c) 执行顺序、(d) GPU 资源分配 R。两阶段逼近降搜索空间：
  - **Stage I（pipeline structure search，§4.1.2）**：忽略 kernel 间干扰，先解出 nano-op 数量/batch size/顺序。从"每算子切 2 份"起步，若仍有 compute bubble 就对 bubble 附近算子增加 nano-op 数，直到 MILP 无法再优化。约束：batch size ∈ [128, dense_batch]（128 为 GEMM tile-friendly）；依赖由父算子依赖 + input batch 交集共同决定；同类瓶颈资源的算子不重叠；探索 AG↔AR 等价网络变换。
  - **Stage II（resource allocation refining，§4.1.3）**：固定 Stage I 的结构，引入 kernel interference 模型，再解一个 MILP 分配各 nano-op 的资源利用率 R，约束**任意时刻并发的 R 之和 ≤ 1.0**，执行时间用 D_best/P 估算（P 由 Table 3 查得）。
- **效果**：约 10 分钟搜出实用 pipeline（§4.1.2 末段），相对部署时长可忽略；仅在模型架构或输入/输出长度显著变化时重搜。

### 3. GEMM-centric kernel interference 建模（§4.1.1）
- **机制**：GPU 不暴露 compute/mem/net 带宽的显式分配接口（R_physical 不可控），用 **GEMM 性能比 R 作为代理**。两两测 GEMM × (GEMV 或 network) kernel 重叠时性能：例如 GEMM 降到 0.8、GEMV 升到 0.3 → 建立非线性的"R→P 交换率"表（Table 3）。只测 pairwise（compute-memory、compute-network），假定三 kernel 重叠时该映射仍成立。剪枝：GEMV/network kernel 的 thread block 数限制在 8-128（步长 8，128 即饱和），剔除"占资源多但更慢"的 GEMM 实现。
- **效果**：对 A100 上 ~100 个 GEMM-GEMV pair profile，sensitivity 分析跨所有 GEMM shape 与 64 个 batch size 组合，R→P 映射标准差 < 5% 均值（§4.1.1 末段）→ Table 3 可泛化用于所有后续 auto-search。

### 4. 异步 request scheduling（§4.2.1）
- **机制**：batch formation（内存预估、新请求 admit、PagedAttention 页表调整、EOS 检测）在 CPU 侧耗时不可忽略。NanoFlow 在 iteration i 的 GPU 执行**同时**为 i+1 形成 batch；i+1 launch 后再为 i+2 形 batch 并处理 i 的 EOS。即检测 EOS 滞后 1 个 iteration。
- **效果**：因平均 decode 长度 >100 tokens（Table 4），多算 1 个 token 的开销 < 1%，换得完全隐藏 batch formation 开销。配合固定 dense batch size，P99 latency 仅是均值的 **1.07×**（§6.3）。

### 5. Batch formation：chunked prefill + 固定 dense batch（§4.2.1）
- **机制**：沿用 Sarathi-Serve 的 chunked prefill 策略，token 粒度切 prefill 以**恰好填满**选定的最佳 dense batch（如 2048）。优先 unfinished decode，再用 prefill chunk 补满。预测未来 peak 内存（按每请求已 decode token 数 + 平均 decode 长度估完成时间），仅在预测内存安全时 admit 新请求；OOM 则把请求 offload 到 CPU 后 reload（不重算）。
- **效果**：dense 算子跨 iteration batch size 恒定 → 降低 tail latency；decode↔prefill 自动稳态平衡（decode 多了 prefill 预算自动减少，反之亦然）。

### 6. 分层 KV-cache offloading + contiguous-then-scatter 加载（§4.2.2）
- **机制**：多轮对话场景下，KQV 生成后立即（不等请求结束）把 KV 向量 offload 到 CPU mem + SSD 层级缓存（LRU 管理）。offload 用 GPU-initiated copy，**藏在 FFN compute-bound 算子执行期间**，只占少量 GPU 资源；NUMA-aware 线程绑定降开销。下一轮对话到达时从 CPU/SSD 取回，因 PagedAttention 的 page 碎片化，先 copy 到 GPU 上连续空间再 scatter 到各 page 目的地。
- **效果**：contiguous-then-scatter 比直接 copy 到碎片化 page 目的地快 **7-10× host-to-device 带宽**（§4.2.2）。开启 offloading 整体仅拖慢 pipeline 3.0%（§6.4），但多轮 LMSYS-Chat workload 节省 **3.02× compute**（§6.4 末段）。

## 表格（原文结构化）

### Table 2：算子级 cost model vs 实测（LLaMA-2-70B，dense batch=2048，8×A100，§3.4）
| Operation | Compute (GFLOP) | Mem Load (GB) | Net (GB) | Est Tcomp (ms) | Est Tmem (ms) | Est Tnet (ms) | Real (ms) |
|---|---|---|---|---|---|---|---|
| KQV | 27487.8 | 19.5 | 0 | 11.01 | 1.22 | 0 | 16.08 |
| O | 21990.2 | 16.1 | 0 | 8.81 | 1.01 | 0 | 16.01 |
| UG (Up+Gate) | 153931.6 | 96.6 | 0 | 61.67 | 6.04 | 0 | 69.92 |
| D (Down) | 76965.8 | 49.7 | 0 | 30.84 | 3.11 | 0 | 34.96 |
| DecAttn | 3665.9 | 462.2 | 0 | 1.47 | 28.89 | 0 | 35.60 |
| PfAttn | 916.3 | 2.1 | 0 | 0.37 | 0.13 | 0 | 4.56 |
| Net | 18.8 | 75.2 | 75.2 | 0.01 | 4.70 | 31.33 | 47.92 |
| **Total** | — | — | — | **114.17** | **45.09** | **31.33** | — |

关键读法：Tcomp (114ms) >> Tmem (45ms) > Tnet (31ms) → 整体 compute-bound，验证 §3.3。PfAttn 实测（4.56ms）远大于估算（0.37ms），因 kernel launch overhead 占大头（§3.4 末段说明）。

### 理论最优吞吐（Equation 5，§3.5）
| Model | Hardware | Compute (FP16) | PModel | Optimal (tokens/s/GPU) |
|---|---|---|---|---|
| LLaMA-2-70B | 8×A100 SXM | 280 TFLOPS (profiled via CUTLASS) | 70B | **1857** |

Throughput_optimal = Compute / (2·PModel)，与 batch size、内存带宽、prefill/decode 长度无关（compute-bound 前提下）。

### Figure 7：离线吞吐对比（LLaMA-2-70B，8 GPU，TP=8，optimal=1857）
| Workload | vLLM | DeepSpeed-FastGen | TensorRT-LLM | NanoFlow |
|---|---|---|---|---|
| In512/Out512 | 494 | 552 | 410 | **1286** |
| In1024/Out512 | 490 | 513 | 372 | **1263** |
| In512/Out1024 | 548 | 293 | 335 | **1212** |
| Splitwise (dataset) | 251 | 255 | 560 | **1259** |
| LMSYS-Chat (dataset) | 293 | 335 | 831 | **1247** |
| ShareGPT (dataset) | 484 | 548 | 639 | **1272** |

相对加速（§6.2）：相对 vLLM 4.18×、DeepSpeed-FastGen 3.45×、TensorRT-LLM 1.91×（dataset workload 平均）；constant-length 下分别 2.62× / 2.78× / 1.73×。最佳 case 达 optimal 的 68.5%。

### Figure 11：跨模型吞吐（input 1024/output 512，§6.6）
| Model | Optimal (tok/s/GPU) | vLLM (% optimal) | NanoFlow (% optimal) |
|---|---|---|---|
| LLaMA-3-70B | 1857 | 32.0% (593) | 70.6% (1306) |
| Qwen2-72B | 1803 | 30.8% (554) | 67.4% (1213) |
| Deepseek-67B | 1944 | 27.4% (532) | 59.1% (1147) |
| Mixtral-8x7B | 19819 | 9.7% (997) | 50.4% (5188, MoE) |
| LLaMA-3-8B | 16236 | 31.9% (5187) | 78.5% (12756) |

NanoFlow vs vLLM 平均 2.66× 吞吐（abstract 末段）。

### Figure 9：消融（§6.4）
| 配置 | In512/Out0 | In512/Out512 | In1024/Out512 | In512/Out1024 |
|---|---|---|---|---|
| Non-overlap | 1273 | 1106 | 1092 | 1048 |
| Nano-batch only | 1171 | 982 | 958 | 952 |
| NanoFlow | 1446 | 1323 | 1291 | 1277 |
| NanoFlow + offload | 1402 | 1290 | 1259 | 1244 |

关键读法：单纯 nano-batch（不重叠）反而比 non-overlap **慢 13.2%**（因重复加载权重无收益）；重叠后才正收益。overlapping network-bound 算子带来 1.07×（prefill-only workload），overlapping network + memory 双双带来 1.17×（decode-heavy workload）。开启 KV offload 拖慢 3.0%。

### Figure 8：延迟 SLO 内最大请求率（200ms normalized latency，§6.3）
| Dataset | 最优 baseline 可承载 req/s | NanoFlow 可承载 req/s | vs TensorRT-LLM |
|---|---|---|---|
| Splitwise | 6.6 | 8.2 | 1.24× |
| LMSYS-Chat-1M | 17.1 | 32.1 | **1.64×** |
| ShareGPT | 10.5 | 16.3 | 1.55× |

低 req rate 下 NanoFlow latency 略高于最佳 baseline（因面向吞吐、固定大 dense batch），高 req rate 下优势拉开。P99 latency = 1.07× 均值。

## 与同类对比

- **vs Sarathi-Serve / Sarathi（chunked prefill）[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]**：Sarathi 在 **iteration/request 调度层**做 chunked prefill + hybrid batching，目标是消除 prefill/decode 间的 generation stall；NanoFlow 在 **算子级 / intra-device 层**做 nano-batch 重叠，目标是消除同一算子序列内 compute/memory/network 的 pipeline bubble。二者正交且互补——NanoFlow 直接**沿用 Sarathi-Serve 的 chunked prefill 策略**做 batch formation（§4.2.1），把其当作上层调度，自己专注下层算子重叠。Sarathi 不做算子级并行，仍串行执行 KQV/Attn/UGD。
- **vs vLLM/PagedAttention [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]]**：vLLM 解决 KV-cache 内存碎片化（page table）+ continuous batching；Figure 4 明确把 vLLM 列为"单大 batch 串行执行"的范式代表，是 NanoFlow 的直接 baseline（被 4.18× 超过，dataset workload）。但 NanoFlow **不取代 PagedAttention**，反而**在其之上构建**（§4.2.2 用 PagedAttention 管理 page，contiguous-then-scatter 加载策略专门为 page 碎片化设计）。即 vLLM 是内存管理层，NanoFlow 是算子调度层。
- **vs SGLang [[sglang-efficient-execution-of-structured-language-models-programs]]**：Figure 4 把 SGLang 列为同样"单大 batch 串行执行"的框架之一；SGLang 强项在 structured generation 的 RadixAttention 与 program-level 优化，与 NanoFlow 的 intra-device 算子重叠正交，理论上可叠加。
- **vs TensorRT-LLM**：NVIDIA 官方高度优化的 engine，已是 Figure 7 中最强 baseline（dataset workload 达 optimal 30-45%）。NanoFlow 仍超 1.91×（§6.2），说明 TensorRT-LLM 即便单算子 kernel 极优，**串行执行**仍浪费 compute → 算子级重叠的收益独立于底层 kernel 库质量。NanoFlow 用 CUTLASS（§3.5）测 peak compute。
- **vs Disaggregated / disagg（Splitwise, DistServe）**：这些方案把 prefill/decode 拆到不同 cluster（phase-level），物理隔离资源以各取所需；NanoFlow **不 disagg**，在单实例内同时跑 prefill+decode（chunked prefill hybrid batch），靠 intra-device overlap 解决资源争用。正交方向，理论上可叠加 disagg + NanoFlow。Splitwise 同时是 NanoFlow 的 baseline 和评测数据集来源。
- **vs 算子级编译器（Rammer, Unity, ASPEN, Welder，§7 operation-level parallelism）**：Rammer 重映射 op 到不同功能单元（intra-op parallelism），Unity 做代数变换 + 并行，ASPEN/Welder 打破 op 边界做 tile-level graph。共同短板：**不考虑算子异质资源需求**（不区分 compute/memory/network-bound），tile 间仍顺序依赖 → 并行度受限；需从零重编译、手工量大。NanoFlow 通过 nano-batching **创造**重叠机会（duplicate op 在不同 nano-batch 上），而非仅在已有算子上重排。
- **vs MoE 专用优化（FasterMoE 等）**：§4.1.4 MoE pipeline——MoE 因 expert 不均衡用 TP，FFN 用 grouped-GEMM，多一个 gate routing 算子，但 auto-search 仍自动产出 pipeline（Figure 11 Mixtral-8x7B 达 optimal 50.4%）。

## 跨论文关系（→ MOC 谱系）

NanoFlow 位于 **LLM serving 系统优化谱系**的"算子级 / intra-device 重叠"分支，是**已修正前提（compute-bound）+ 新机制（intra-device parallelism via nano-batching）**的组合。

- 上游（前提修正）：
  - [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] (vLLM/PagedAttention, 2023) — NanoFlow 的 KV-cache 内存管理层基底，也是直接 baseline。NanoFlow 在 PagedAttention page 之上做 contiguous-then-scatter（§4.2.2）。
  - [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] / [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] (Sarathi/Sarathi-Serve, 2023-2024) — NanoFlow 的 batch formation 策略直接复用 Sarathi-Serve 的 chunked prefill（§4.2.1）。Sarathi 在 iteration 层消 stall，NanoFlow 在算子层消 bubble，两层正交。
- 同层（serving 引擎对比 / 互补）：
  - [[sglang-efficient-execution-of-structured-language-models-programs]] (SGLang) — Figure 4 同列为"串行执行"baseline，强项在 structured generation，与 NanoFlow 算子重叠正交可叠加。
  - DistServe / Splitwise（disagg 范式）— phase-level 物理隔离 vs NanoFlow intra-device 逻辑重叠，正交方向。
- 跨硬件谱系（同类工程思想）：
  - [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]] (CloudMatrix384 SuperPod) — 同样关注 serving throughput 逼近硬件上限，思路是 persistent kernel + overlapping streams 跨 NPU 流水；NanoFlow 是单 device 内算子重叠，SuperPod 是跨 device/流重叠。两者代表"逼近硬件最优"的两种粒度（intra-device vs inter-device），可对比 R（资源利用率）逼近上界的程度。
  - [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] (Mooncake) — KV-cache-centric disagg 架构；与 NanoFlow 的 KV-cache SSD offloading + LRU 层级缓存（§4.2.2）思路呼应但尺度不同：Mooncake 跨节点 disagg KV pool，NanoFlow 单实例内 CPU mem + SSD 分层。NanoFlow 的 offload 思想可视为 Mooncake KV-pool 思想的单机微缩版。
- 下游/可叠加：MoE pipeline（§4.1.4）为后续 MoE serving 优化提供算子重叠基底；auto-search 框架可吸纳新算子（quantization 如 ATOM/QServe，§7）。

## 局限与边界

- **前提强依赖 compute-bound**：整个方法成立的前提是 TR<1（§3.3）。论文 Figure 3 自己承认 **LLaMA-3-8B 上 512-1024（长 decode）workload TR≈1**，此时 compute 不再显著主导，nano-batching 重复加载权重的开销可能无法被 pipeline 隐藏 → 收益打折。MoE Mixtral 仅达 optimal 50.4%（§6.6），是所测模型中最低，反映 MoE 的 expert 不均衡 + grouped-GEMM 特性使算子重叠空间受限。
- **kernel interference 模型为近似**：(1) 仅 profile **pairwise**（compute-memory、compute-network），三 kernel 同时重叠时假设 R→P 映射不变（§4.1.1 末段）；(2) 用 GEMM 性能 R 作为 R_physical 的代理，GPU 不暴露真实资源分配 → 模型本身是经验近似，标准差 <5% 但非零。复杂场景（多算子深重叠）下误差会放大。
- **MILP 搜索非最优**：Stage I/II 都是启发式逼近，"practical pipeline 可在 ~10 分钟内找到"（§4.1.2 末段），但**不保证 provably optimal**。论文明确写"搜索最优解需 hours-days"，故放弃。
- **Nano-batching 本身有开销**：消融（Figure 9）显示，**不重叠**时单纯 nano-batch 比 non-overlap **慢 13.2%**（重复加载权重无收益）。收益完全依赖能否有效重叠；若某算子无可重叠伙伴（如纯 prefill workload 网络重叠收益仅 1.07×，§6.4），增益有限。
- **延迟 trade-off 未完全解决**：低 request rate 下 NanoFlow latency **略高于最佳 baseline**（§6.3），因面向 throughput 用大 dense batch。NanoFlow 明确自我定位为 throughput-oriented（§6.3 首段），低 QPS 场景非其甜区。
- **硬件 / 厂商泛化未实测**：cost model 在 Table 1 跨 11 款 accelerator（NVIDIA/AMD/Intel）分析 compute/mem/net 比值稳定（§3.3 末段），但**实验仅在 NVIDIA A100 80GB SXM 上做**（§6.1）。AMD MI300 / Intel Gaudi 的 kernel interference profile、CUTLASS 等价库、CUDA event 替代品均未验证；实现明确为"NVIDIA GPUs"（§5）。对非 NVIDIA 平台的可移植性是 open question。
- **不解决调度层问题**：auto-scaling、workload balancing、priority-aware routing 全部假设由外部 control plane 处理（§4.2.1 首段），NanoFlow 实例假设请求充裕且等优先级。请求不充裕时需控制面缩减实例数以维持单实例大 batch——但论文未给出该协同机制的设计。
- **auto-search 触发条件模糊**：仅在"模型架构或 workload（input/output 长度）显著变化"时重搜（§4.1.3 末段），但"显著"未量化，实际部署可能需人工阈值。
- **评估场景偏静态**：主评估为离线吞吐 + 固定 5 分钟 exponential 间隔 trace（§6.3），未覆盖 bursty 流量、长尾 prompt、动态模型切换等真实生产场景。SLO 仅用单一 normalized latency 200ms（按人类阅读速度定，§6.3），未考虑首 token 延迟（TTFT）与 TBT 分别约束。
