# MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs — 技术点深读（DEEP 2026-08-18）
> 独立深读文件，extract_phase1 重跑不丢失。M3 figure caption（9 张）已织入分析；图 4（PP overlap 调度）与图 10（microbenchmark loss 曲线）无 M3 caption，仅按全文叙述引用。
> 论文：MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs · arXiv:2402.15627 · ByteDance & Peking University · NSDI '24

## 核心问题

在 10,000+ GPU 的生产规模下训练 LLM 带来两类前所未有的系统性挑战（§1）：

1. **训练效率（training efficiency）**：MFU（Model FLOPs Utilization，观测吞吐 / 假设 100% 峰值 FLOPs 的理论上限）随规模急剧下降。LLM 训练非 embarrassingly parallel，3D parallelism 下 GPU 间通信、算子优化、数据预处理、GPU 显存均显著拉低 MFU。如 Figure 6（p.8，M3 解读：相同配置下不同 run 的 MFU 在 0–0.6 区间剧烈波动，颜色编码不同 execution）所示，10k 规模下 MFU 不一致是常态而非偶发。
2. **训练稳定性（training stability）**：训练 trillion tokens 需数周，failure 与 straggler 是常态而非例外；单 straggler 拖慢整个 10k-GPU 作业，单次 failure 代价巨大、recovery 必须极快。

MegaScale 用两条系统原则回应：**algorithm-system co-design**（针对 LLM 训练的专用系统全栈协同设计）与 **in-depth observability**（穿透表层指标、跨栈收集粒度数据以定位 root cause）。这两条原则贯穿算法（§3.1）、通信重叠（§3.2）、算子/数据/网络（§3.3–3.6）、容错（§4）、排障（§5）与生产验证（§6）。

## 关键创新点

1. **算法层优化（§3.1）**——在不损失精度前提下压低单步计算与流水气泡：
   - **Parallel Transformer Block (PTB)**：将标准串行式 `y = x + MLP(LN(x+Attention(LN(x))))` 重写为并行式 `y = x + MLP(LN(x)) + Attention(LN(x))`（式 1→2），Attention 与 MLP 并行执行，缩短关键路径。引用 PaLM [5] 表明数百亿参数规模下不降质。Figure 3（p.4，M3：PTB 将 All-Gather/Reduce-Scatter 与 QKV/Self-Attention/MLP 的 ColParaLinear/RowParaLinear 并列编排，SP 与 TP 区域显式切分）即以 PTB 为底座展示通信融合方案。
   - **Sliding Window Attention (SWA)**：固定窗口 w 的稀疏注意力，复杂度 O(s·w) vs full self-attention 的 O(s·s)（w≪s）；通过堆叠层获得大 receptive field 保留全局信息。
   - **LAMB optimizer** [9]：将 LLM batch size 放大 4× 而不损失精度（microbenchmark Figure 10b，4× BS LAMB 在 ~250B tokens 时与 ADAM 1× BS 同 loss）。结合 interleaved pipeline，4 步 1× batch 的气泡 `4((p-1)/v)` 转化为 1 步 4× batch 的气泡 `(p-1)/(4v)`，**直接削减 87.5% pipeline bubble**（§3.1）。Ablation 中 LAMB BS×3 贡献 +3.0% MFU（Table 3 第 9 行）。

2. **3D Parallelism 中的通信-计算重叠（§3.2）**——按并行策略逐一拆解 critical path 之外的通信，整体在 ablation 中贡献 TP/PP/DP overlap 共 +6.2% MFU（Table 3 第 4–6 行，分别为 +2.2%/+2.5%/+1.5%）：
   - **DP overlap**：all-gather（前向取最新参数）与 reduce-scatter（反向收梯度）按 model chunk 粒度触发；首个 all-gather 借鉴 PyTorch FSDP [15] 在迭代起始 prefetch，与 data loading 重叠，通信时间减少 `1/(2·vpp_size)`；并按依赖计算算子的顺序赋予通信算子优先级。通信底图见 Figure 1（p.2，M3：两个 model replica 并行，Reduce-Scatter sync grads → Update Params → All-Gather gather params 的环形流水）。
   - **PP overlap**：interleaved 1F1B（Figure 2，p.3，M3：3 stage × 2 virtual stage 的交错调度，同色块表同一 micro-batch 的前/反向，红色虚线标交错切换点，靠虚拟子阶段 doubling in-flight micro-batch 来压气泡）中，warm-up 前向只依赖前一次 receive，故解耦 send/recv（原本合并实现会被慢者阻塞），让 send 与计算重叠（Figure 4 左，p.5）；cool-down 为 warm-up 之逆；steady phase 的 forward/backward 与相邻通信互不依赖，send/recv 异步发起（Figure 4 右，p.5）。
   - **TP/SP overlap**：TP 分权重、SP 沿 sequence 分 LayerNorm/Dropout，故需 all-gather/reduce-scatter 重分布（Figure 3a 在 critical path，p.4）。MegaScale 将 all-gather 与 reduce-scatter **fuse 进 FFN 路径的 parallel Linear**（Figure 3b，M3：standalone comm node 消失，AG 折入 ColParaLinear-with-AG、RS 折入 RowParaLinear-with-RS），因 FFN 路径 GEMM kernel 更大、通信更易隐藏；进一步将 GEMM kernel 切成小 chunk，在双 CUDA stream（S0 kernel / S1 comm）上 pipeline 执行（Figure 3c，M3：A0…AN 输入 chunk 在 S1 copy 与 S0 A×W GEMM 并行、输出 C0…CN 在 S1 RS 与 S0 B×W GEMM 并行），反向同理。

3. **高效算子（§3.3）**：采用 **FlashAttention-2** [16] 改进 thread block/warp 间 work partitioning；将 LayerNorm、GeLU 的细粒度 kernel 融合，减少 kernel launch 开销并优化访存。Ablation 贡献 +1.7% MFU（Table 3 第 7 行）。

4. **数据流水线（§3.4）**：
   - **异步数据预处理**：预处理非关键路径，在 step 末尾 gradient 同步时并行启动下一步预处理。
   - **冗余 dataloader 消除**：同机 TP group 内所有 GPU 输入完全相同，采用**两层 tree-based** 方案——每机一台专用 loader 读入 shared memory，各 GPU worker 仅负责从 shared memory 复制到自己显存，消除冗余磁盘读。

5. **Collective 通信组初始化（§3.5）**：Megatron-LM 在 2,048 NVIDIA Ampere GPU 上初始化耗时 **1047 秒**（严重阻碍快速 restart/recovery 与迭代开发）。两点根因与修复：
   - TCPStore 单线程阻塞 → 替换为 **Redis**（非阻塞异步），初始化降至 361 秒；
   - 每个通信组初始化后做 global barrier，复杂度 O(n²) → **精心设计组初始化顺序**最小化 global barrier，复杂度 O(n)；最终 **2048 GPU < 5 秒、10,000+ GPU < 30 秒**。

6. **网络性能调优（§3.6）**：
   - **拓扑**：Broadcom Tomahawk 4 芯片，每片 25.6 Tbps / 64×400 Gbps；三层 CLOS-like 拓扑连 10,000+ GPU，downlink:uplink = 1:1（各 32 端口），小直径。
   - **降低 ECMP 哈希冲突**：ToR 将一个 400G downlink 拆为两个 200G downlink（AOC），使 uplink 带宽两倍于 downlink，冲突概率下降；服务器 8 张 200G NIC 以 multi-rail 接 8 台不同 switch；同一组 ToR 下可达 64 台 GPU server，调度数据密集节点置于同一 ToR 减少跳数。
   - **拥塞控制**：默认 DCQCN [19] 在 all-to-all 下产生大量 PFC、HoL blocking；自研算法融合 **Swift [20] 的精确 RTT 测量**与 **DCQCN 的 ECN 快速响应**，显著提升吞吐、减少 PFC 相关拥塞。
   - **重传超时**：调 NCCL 的 retransmit timer 与 retry count；NIC 启用 **adap_retrans** 以更短间隔重传，应对短周期 link flapping（直接服务于 §6.3 的 flapping 案例）。

7. **容错 Robust Training Workflow（§4）**：Driver 接 Kubernetes 分配 Pod、每 executor 管一节点、起训练进程并启动 robust training daemon 周期性 heartbeat（Figure 5，p.6，M3：Driver 内含 User API / Checker / Log Analyser 与 Training Job Info / Evicted Pods / Blocked IPs 三个状态表，Checker 向 Executor 触发 "stop && check" 并收 "check results"，Log Analyser 消费 heartbeat 异常时触发 Checker）。
   - **数据采集与分析（§4.2）**：heartbeat 含 executor 基本信息与训练进程状态；聚合 stdout/stderr，按 warning/error keyword 实时报错；**RDMA traffic metrics 作为隐性异常指示**——训练周期性使每步流量相似，流量显著下降或异常波动即告警、完全停止则自动触发恢复。监控分级：秒级（整体健康、ECN/PFC/QoS、link flapping、NIC 问题）与**毫秒级**（是否拥塞、DP/PP 数据传输是否到物理极限）。
   - **诊断测试（§4.3）**：在执行时间与误报率间权衡的轻量 suite。**Intra-host 网络测试**——Loopback 测所有 RNIC 到内存节点/GPU 的 loopback 带宽（全 mesh），推断链路带宽退化与 PCIe 配置异常；RNIC-to-RNIC 测同机 RNIC 间连通与带宽。**NCCL tests**——机内 all-to-all 比对带宽基准；通过后每节点与同 ToR 邻居做 all-reduce。
   - **快速 checkpoint 与恢复（§4.4）**：两阶段 checkpoint——GPU 将 on-chip state 写入 host memory（优化 PyTorch 序列化 + pinned memory，借高 PCIe 带宽**数秒**完成）后立即继续训练；后台进程异步把状态从 host memory 落到 HDFS。恢复阶段在 critical path 上：同 DP group 多 worker 共享同一 state partition，**指定组内单一 worker 从 HDFS 读，再 broadcast 给其他**，线性降低 HDFS 读负载，显著缩短恢复时间。

8. **训练排障工具（§5）**：
   - **CUDA Event Monitor（§5.1）**：在 10k GPU 规模下观察到不同 run 的 MFU 不一致（Figure 6，p.8，M3：同配置不同 execution 的 MFU 在 0–0.6 间散落），且 MFU 随时间下降；单 GPU GEMM 微基准看不出差异。开发基于 **CUDA event**（非 torch profiler / Megatron timer）的计时工具，最小化 CUDA 同步以避免性能退化，可常驻生产。两模式：**heat-map**（Figure 7，p.8，M3：12 host × 4 rank = 48 rank 网格，色条 2.0s→2.5s 映射，TP/DP/PP Comm 用绿/紫/橙虚线，rank 20 选中揭示 3D 依赖；揭示约 0.5% 机器显著偏慢如 host 10 的 rank 40/41、host 8 的 rank 32 为深红，剔除后各 run 峰值 MFU 一致）；**distributed trace**（Figure 8，p.9，M3：rank[0/4/8/12] 沿时间轴排成横栈，forward 绿 / backward 粉 / L 灰 + 粉色 all-reduce 尖刺，粉色曲线箭头表 producer→consumer 跨 rank 依赖，选中事件高亮其因果链）。数据本地写文件→streamer 实时同步到 Kafka→analytical database，on-the-fly 分析不中断训练。
   - **3D Parallel Training Visualization（§5.2）**：3D parallelism 下数据流与任务序列极复杂；单 GPU 故障会让整个 cluster stall 在 NCCL 通信，外部表现为泛化阻塞而根因淹没在 timeout 洪流。每 GPU worker 在通信 timeout 时 log 自身 ongoing event，据此在逻辑拓扑上可视化数据依赖（Figure 7 的 3D 视图，p.8）；故障 GPU 所在节点 hang 而不写 log，被 timeout 等待者反而会写 log，借此快速锁定问题节点，手动隔离后再经 robust framework 标记维护。

9. **Problems Discovered and Fixed（§6.3）**：数周生产记录中 **>90% 异常被 robust framework 自动检测/定位/恢复**（如 CUDA error、segmentation fault），检测+诊断 **<10 分钟**，从最近 checkpoint 追回 crash 前进度 **<15 分钟**，**维持 >90% effective training time rate**（=iterations × iter time / total time）。生产期内训练自动恢复 **>100 次**，loss 曲线（Figure 11，p.11，M3：x 轴 normalized consumed tokens rate 0→1，y 轴 loss 0.2–0.8，每段不同色表一次 restart，连续无 visible regression）证明恢复 pipeline 不引入 loss 回归。三个典型案例：
   - **Computational stragglers**：特定 host 同一前向比其他 rank 慢约 10%，多实验一致→判定为机器固有而非软件；隔离后 MFU 提升约 0.7%。
   - **MFU decreasing**：随 step 推进单步时间增加，但 forward/backward/optimizer 稳定→归因 collective communication；逐步定位到最后一个 reduce-scatter（DP）。网络带宽稳定→排除慢速通信；依同步特性判定为**部分 rank 晚发起 reduce-scatter**。两-rank 缩放实验发现 launch time 交替波动、gap 随 step 增大。追溯到 forward 计算阶段——**不规则 garbage collection**与某些 PyTorch 操作扰动 critical path；修改/移除后不再出现 MFU 显著下降（Figure 12，p.12，M3：早期 0–~10k step 多 trial 在 <0.5 处抖动，后期 ~10k–30k 收敛至 0.48–0.50 紧带）。
   - **Frequent network interface flapping**：接口先 down 后 up，间隔数秒、传输中包全丢。教训一：timeout 阈值须显式调大，否则默认值在 NIC up 之前就触发 NCCL completion error；教训二：根因是 NIC-AOC cable-switch 间链路质量差，通过下控 NIC 信号强度、AOC 线缆质量、switch 端信号强度降到可接受频率。

## 表格（原文结构化）

### Table 1：模型配置（§6）
| Model Size | Heads | Hidden Size | Layers | TP | PP |
|---|---|---|---|---|---|
| 175B | 128 | 12288 | 96 | 8 | 8 |
| 530B | 160 | 20480 | 105 | 8 | 35 |

### Table 2：175B 模型 strong-scaling 训练性能（§6.1，训练 300B tokens）
| Batch | Method | GPUs | Iter Time (s) | Throughput (tok/s) | Train Time (days) | MFU | Aggregate PFlops/s |
|---|---|---|---|---|---|---|---|
| 768 | Megatron-LM | 256 | 40.0 | 39.3k | 88.35 | 53.0% | 43.3 |
| 768 | Megatron-LM | 512 | 21.2 | 74.1k | 46.86 | 49.9% | 77.6 |
| 768 | Megatron-LM | 768 | 15.2 | 103.8k | 33.45 | 46.7% | 111.9 |
| 768 | Megatron-LM | 1024 | 11.9 | 132.7k | 26.17 | 44.7% | 131.9 |
| 768 | MegaScale | 256 | 32.0 | 49.0k | 70.86 | 65.3% (1.23×) | 52.2 |
| 768 | MegaScale | 512 | 16.5 | 95.1k | 36.51 | 63.5% (1.27×) | 101.4 |
| 768 | MegaScale | 768 | 11.5 | 136.7k | 25.40 | 61.3% (1.31×) | 146.9 |
| 768 | MegaScale | 1024 | 8.9 | 176.9k | 19.62 | 59.0% (1.32×) | 188.5 |
| 6144 | Megatron-LM | 3072 | 29.02 | 433.6k | 8.01 | 48.7% | 466.8 |
| 6144 | Megatron-LM | 6144 | 14.78 | 851.6k | 4.08 | 47.8% | 916.3 |
| 6144 | Megatron-LM | 8192 | 12.24 | 1027.9k | 3.38 | 43.3% | 1106.7 |
| 6144 | Megatron-LM | 12288 | 8.57 | 1466.8k | 2.37 | 41.2% | 1579.5 |
| 6144 | MegaScale | 3072 | 23.66 | 531.9k | 6.53 | 59.1% (1.21×) | 566.5 |
| 6144 | MegaScale | 6144 | 12.21 | 1030.9k | 3.37 | 57.3% (1.19×) | 1098.4 |
| 6144 | MegaScale | 8192 | 9.56 | 1315.6k | 2.64 | 54.9% (1.26×) | 1400.6 |
| 6144 | MegaScale | 12288 | 6.34 | 1984.0k | 1.75 | **55.2% (1.34×)** | 2166.3 |

> 备注：256–1024 GPU 因显存限制 batch=768；3072–12288 GPU batch=6144。括号为相对 Megatron-LM 加速比。12,288 GPU 为论文头条指标：55.2% MFU、1.34×、2166.3 aggregate PFlops/s。strong-scaling 下 MegaScale MFU 随 GPU 数从 59.1% 降到 55.2%（computation-to-communication ratio 下降，预期行为）。

### Table 3：175B / 256 GPU / batch 256 的 MFU 提升拆解（§6.1 Ablation）
| Idx | Method | MFU (∆MFU) |
|---|---|---|
| 1 | baseline (Megatron-LM，含网络优化) | 47.7% |
| 2 | (1) with PTB | 52.3% (4.6%) |
| 3 | (2) with SWA | 53.3% (5.6%) |
| 4 | (3) with TP overlap | 55.5% (7.8%) |
| 5 | (4) with PP overlap | 58.0% (10.3%) |
| 6 | (5) with DP overlap | 59.5% (11.8%) |
| 7 | (6) with efficient operators | 61.2% (13.5%) |
| 8 | (7) with misc optimizations | 62.3% (14.6%) |
| 9 | (8) with LAMB (BS×3) | 65.3% (17.6%) |

> 合计较 baseline +17.6% MFU。网络优化对 baseline 与 MegaScale 均开启以公平对比。3D comm overlap（TP+PP+DP，第 4–6 行）合计 +6.2%，是单类最大贡献块；算法（PTB+SWA）+5.6% 次之；LAMB BS×3 +3.0%。

### Figure 9 数据（530B weak-scaling，§6.1）
| #GPUs | Megatron-LM MFU (%) | MegaScale MFU (%) |
|---|---|---|
| 2240 | 49.20 | 54.30 |
| 4480 | 48.80 | 54.10 |
| 11200 | 48.20 | 54.30 |

> Figure 9（p.10，M3：分组柱状图，灰色 Megatron-LM vs 红色 hatched MegaScale，三个 GPU 规模）。MegaScale 较 Megatron-LM 高达 +6.1%；规模增大 5× 时 Megatron-LM MFU 下降 1.6%，MegaScale 凭 3D-parallel comm overlap 维持 ~54% 近线性可扩展。

### 关键运维数字（§6.3）
| 指标 | 数值 |
|---|---|
| 自动处理异常比例 | >90% |
| 检测+诊断耗时 | <10 min |
| 从 checkpoint 恢复耗时 | <15 min |
| Effective training time rate | >90% |
| 生产运行期内自动修复次数 | >100 次 |
| Computational straggler 剔除后 MFU 提升 | ~0.7% |
| Straggler 机器占比（heat-map） | ~0.5% |
| 通信组初始化（2048 GPU / 10k+ GPU） | <5 s / <30 s |

## 与同类对比

- **vs Megatron-LM [10, 7]**：MegaScale 建立在 Megatron-LM 之上（commit 285068c8），继承其 3D parallelism 与 interleaved 1F1B（Figure 2，p.3）；在 12,288 GPU / 175B 上达 55.2% MFU vs Megatron-LM 的 41.2%（1.34×）。差异来源按 Table 3 拆解：算法（PTB+SWA）+5.6%、3D comm overlap（TP/PP/DP）+6.2%、efficient ops +1.7%、misc +1.1%、LAMB BS×3 +3.0%。weak-scaling 530B 上（Figure 9，p.10）MegaScale 在 11,200 GPU 仍 54.3%（近线性），Megatron-LM 降至 48.2%。注意 175B 用 12,288 GPU、530B 用 11,200 GPU 是因 3D 配置不同。
- **vs PyTorch FSDP [15]**：DP overlap 的首 all-gather prefetch 思路借鉴 FSDP，但 MegaScale 在 3D parallelism 上下文按 model chunk 粒度调度、并赋予通信优先级，比 FSDP 的纯 DP 场景更复杂。
- **vs DCQCN [19] / Swift [20]**：默认 DCQCN 在大规模 all-to-all 下 PFC 过多、HoL blocking；MegaScale 融合 Swift 的 RTT 精测与 DCQCN 的 ECN 快响应，自研拥塞控制算法，而非纯端到端或纯交换机侧方案。
- **vs torch.distributed [17]**：用 Redis 替换 TCPStore、重排通信组初始化顺序降 global barrier 复杂度 O(n²)→O(n)，将 2048 GPU 初始化从 1047s 降到 <5s（209× 加速），这是 restart-and-recovery 与迭代开发能成立的前提。
- **vs PyTorch Profiler / Megatron timer**：基于 CUDA event 的轻量计时，最小化同步、可常驻生产；提供分布式 trace（Figure 8，p.9，跨 rank 统一 timeline + 依赖边）与 heat-map（Figure 7，p.8，跨机各维度耗时差异），弥补 PyTorch Profiler 单节点视角局限。
- **vs Pingmesh/NetBouncer/Hostping [58,61,62]**：诊断工具聚焦 LLM 训练特有场景（intra-host RNIC/NCCL 全 mesh loopback、3D parallel topology 上的 timeout 反推故障节点——靠"未写 log 的 hang 节点即为根因"这一反直觉信号），而非通用数据中心网络探测。

## 跨论文关系（→ MOC 谱系）

- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] —— **谱系根**。MegaScale 直接建于 Megatron-LM 之上，沿用 TP/PP/DP+SP 与 interleaved 1F1B；MegaScale 是把 Megatron 的算法骨架推到 10k-GPU 生产规模的后继。
- [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] —— **直接前置**（Megatron-LM 的 distributed follow-up，也是 MegaScale 的 commit 285068c8 基线）。MegaScale 的 interleaved pipeline、序列并行、3D 并行组合直接来自此工作；MegaScale 在其之上增加 comm/compute overlap、LAMB、PTB/SWA、容错与可观测性。
- [[zero-memory-optimizations-toward-training-trillion-parameter-models]] —— **正交互补**。ZeRO2（§2, Figure 1，p.2）是 MegaScale DP 的基础：将 optimizer states+gradients shard 跨 DP 进程，all-reduce 拆成 reduce-scatter+all-gather，MegaScale 据此设计 overlap。
- [[muon-is-scalable-for-llm-training]] —— **哲学同源**。Muon 的 gather/compute overlap（把通信藏进 GEMM/计算）与 MegaScale 的 TP/SP overlap（GEMM kernel 切 chunk 与通信 pipeline，Figure 3c，p.4）共享同一"通信-计算重叠"内核，尽管分别作用于 optimizer 内通信与 TP 通信。
- 谱系定位：MegaScale 是 training-system 基因树在 **10k-GPU 规模**的 apex——Megatron-LM（根，TP/PP/DP 原语）→ Efficient Large-Scale LLM Training（distributed 落地 + interleaved）→ MegaScale（生产级 10k-GPU：算法-系统协同 + 容错 + 深可观测）。

## 局限与边界

1. **算法假设受规模约束**：PTB 的"不降质"依据 PaLM 在数百亿参数的结论（§3.1 引 [5]）；LAMB 的 4× batch 无损精度为 13B 模型 microbenchmark 观察（§6.2，Figure 10b，p.11，资源所限未在更大模型做），未在万亿参数级严格验证。
2. **MFU 随规模下降**：strong-scaling 下 batch 固定、computation-to-communication ratio 随 GPU 数增加而下降，12,288 GPU 时 MFU 从 256 GPU 的 65.3% 降到 55.2%（§6.1）——非完全解决，而是受控下降。
3. **容错非完全自动化**：~90% 异常自动处理，余 ~10% 仍需 §5 的手动分析与人工隔离节点（§5.2、§6.3）；straggler 诊断依赖 CUDA event 工具与人工判读。
4. **硬件与拓扑绑定**：Tomahawk 4 + 8×200G NIC multi-rail + 特定 AOC 拆分，网络优化强耦合具体硬件；通用性有限。ECMP 拓扑调度的"数据密集节点置于同 ToR"依赖训练任务调度配合，跨作业共享集群时调度自由度受限。
5. **基线时效**：对比基线为 Megatron-LM commit 285068c8（实验启动时选定，§6.1），后续版本可能已合入部分优化，1.34× 的相对优势具时点性。
6. **可观测性开销**：CUDA event 监控与 Kafka 流水线"overhead 可忽略"为论文自述（§5.1 末），未给量化数据；常驻生产下对极小步时间敏感场景仍需谨慎。
7. **恢复 RTO 依赖 checkpoint 频率与 HDFS 带宽**：两阶段 checkpoint 把 HDFS I/O 移出 critical path，但恢复阶段仍受 HDFS 带宽限制（仅靠 group 内单读 + broadcast 缓解）；<15 min 恢复是生产观测值而非硬上限。
8. **集群规模陈述时点性**：">10,000 NVIDIA Ampere GPU"为 September 2023 快照（§6），Hopper 集群在建；论文结论是否外推到 Hopper + 更大规模未验证。
