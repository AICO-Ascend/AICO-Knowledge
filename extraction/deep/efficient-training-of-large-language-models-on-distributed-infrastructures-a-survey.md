# Efficient Training on Distributed Infrastructures Survey — 技术点深读（DEEP 2026-08-18）

> 源文献：Duan et al., "Efficient Training of Large Language Models on Distributed Infrastructures: A Survey", arXiv:2407.20018v1 (29 Jul 2024). Shanghai AI Laboratory, CUHK, Fudan, SJTU, NTU, PKU.
> 定位：distributed-training taxonomy 锚点 — 覆盖从基础设施到训练系统全栈的综述，是本仓库"训练系统谱系"的总纲。

## 核心问题

该 survey 直面 LLM 训练在万卡级集群上面临的 **"SER" 三重困境**（§1, §2.3）：

- **Scalability（可扩展性）**：模型规模未饱和（scaling laws 仍未 plateau，§1 引 [8]），训练系统需在数万 GPU/AI 加速器上保持正确性与精度，涉及硬件配置、网络互联、训练框架的协同设计。典型案例：LLaMA-3 在 16K H100 上预训练约 54 天（§1, §8.1）。
- **Efficiency（效率）**：以 **MFU（Model FLOPs Utilization）** 为核心度量。LLaMA3 在 16K GPU 上仅达 38%–41% MFU（§1, §2.3），说明规模化下利用率急剧下降。需在 parallelism / computation / communication / memory 四维联合优化。
- **Reliability（可靠性）**：训练周期长达数周到数月，节点级故障频发——Bloom 384 GPU 每周 1–2 次故障（§8.1）、OPT 175B 两周 40+ 次中断、MegaScale 12,288 GPU 数周内 100+ 次失败、LLaMA3 54 天 466 次中断。单节点 1.5% 日故障率外推到 1,000 GPU 即 84.8% 日故障率（§8.1），synchronous training 让任意节点崩溃拖垮全局。

该 survey 的精确目标是：**给出从 distributed training infrastructure（accelerator/network/storage/scheduling）到 training systems（parallelism/computation/communication/memory/fault tolerance）的端到端技术图谱**（§1, Fig.1），补齐既有 LLM survey 偏算法/资源压缩而忽视 systemic 设计的空白（§2.4 明确对比 Wan [29]/Liu [30]/Xu [31]）。

## 关键创新点

该 survey 的 taxonomy 支柱按 §3–§8 六章组织，每一支柱既是分类轴也是技术演进脉络：

1. **Infrastructure 支柱（§3）—— 硬件-网络-存储-调度四元组**
   - **AI Accelerators（§3.1）**：NVIDIA GPU（Ampere/Hopper/Blackwell，含 Transformer Engine 混合 FP8/FP16）、AMD MI250X（Frontier 64GB HBM, 191.5 TFLOPS FP16）、Habana GAUDI、Google TPUv4（4096 chips, ~60% peak FLOPS）、Graphcore Bow Pod64（22 petaFLOPS）、Cerebras CS-2（wafer-scale, 850K cores）。
   - **Network Infrastructure（§3.2）**：Chip-to-Chip（PCIe→NVLink cube-mesh→NVSwitch fully-connected 300/600/900 GB/s→TPU 2D/3D-Torus ICI）× Node-to-Node（GPUDirect-RDMA, InfiniBand EDR/HDR/NDR 100/200/400 Gbps, RoCE-v1/v2）× Network Topology（HPC Clos/Dragonfly+；训练优化 rail-optimized/rail-only/HPN/BiGraph/HammingMesh；可重构 SiP-ML/TopoOpt/TPUv4 OCS）× Load Balancing & Congestion Control（ECMP→packet spraying→Ethereal→HPN；PFC/TIMELY/DCQCN/HPCC/EQDS；MLTCP/CASSINI/MLT 基于 LLM 周期性 elephant-flow 特性）。
   - **Storage（§3.3）**：Checkpoint 存储（Tectonic/HDFS/Ceph，70B 模型 ckpt 达 980GB）× 训练数据存储（Lustre/GPFS/BeeGFS 并行文件系统；Alluxio/JuiceFS/Quiver/Fluid 缓存层；LLaMA3 15T tokens≈30TB，原始数据 100× 放大达 PB 级）。
   - **Scheduling（§3.4）**：Workload scheduling（异构感知 Gavel/Gandivafair、job-packing FGD/Lucid、adaptive-scaling Pollux/Sia；LLM 专用 Crius/Hydro/Acme）× Resource scheduling（Cassini 网络、HIRE in-network、SiloD 存储、Synergy CPU、EnvPipe/Zeus/Perseus 能效）。

2. **Parallelism Schemes 支柱（§4）—— Hybrid / Auto / Heterogeneous 三分法**
   - **Hybrid Parallelism（§4.1）** 5 子维：Data Parallelism（F=1 full replication PyTorch-DDP/Horovod；F=W full sharding ZeRO-3/FSDP；1<F<W hybrid sharding MiCS）→ Tensor Parallelism（1-D Megatron-LM 列-行切分；2-D Optimus；2.5-D Tesseract；3-D）→ Pipeline Parallelism（GPipe fill-drain；1F1B PipeDream；Interleaved 1F1B；Zero Bubble 拆 B/W 梯度；Chimera 双向；TeraPipe token 级；memory 平衡 BPipe/MPress/Chimera/Hanayo/V-Shape/AdaPipe）→ Sequence Parallelism（ring-based Ring Self-Attention/DistFlashAttn/Context Parallel/Striped Attention/BurstAttention/Blockwise Ring/WallFacer；head-dim DeepSpeed-Ulysses；hybrid USP/LoongTrain Double-Ring）→ Expert Parallelism（sparse activation GShard/Switch/Tutel/DeepSpeed-MoE/Megablocks/ScatterMoE；comm 优化 PipeMoE/ScheMoE/Lina/Janus/TA-MoE；load balance FasterMoE/SmartMoE/FlexMoE/Prophet）。
   - **Auto Parallelism（§4.2）**：General（Mesh-TensorFlow/GSPMD/OneFlow SBP/Alpa/Unity/Aceso/PartIR/nnScaler/AutoDDL；search-based FlexFlow SOAP+MCMC、AutoMap MCTS）+ Transformer-Specific（DeepSpeed-Autotuning/Galvatron/Merak/Colossal-AI/Galvatron-BMW）。
   - **Heterogeneous Parallelism（§4.3）**：异构硬件（HetPipe/Whale/AMP/Pathways/SDPIPE/HAP/PipePar + geo-distributed Yuan/SWARM/FusionAI）× 异构模型（RLHF 四模型 PPO：DeepSpeed-Chat/HuggingFace TRL/OpenRLHF/APP/ReaLHF/PUZZLE）。

3. **Computation Optimizations 支柱（§5）**
   - **Operator Optimizations（§5.1）**：Manual（FlashAttention 系列 IO-aware tiling + online softmax；FlashAttention-3 H100 WGMMA/TMA warp-specialized pipeline；BPT 扩展 tiling 到 FFN；SWattention Sunway；ByteTransformer padding-free variable-length）+ Automatic（kernel-level Halide/TVM/Roller/Triton/ALCOP；graph-level Chimera/Welder/Slapo/TorchDynamo+TorchInductor/JIT-Q）。
   - **Mixed-Precision Training（§5.2）**：16-Bit（FP16/BF16 + loss scaling；Campo casting 优化；THC 同态压缩）→ Sub-8-Bit（FP8 Wang/Sun hybrid/FP8-LM/Rouhani microscaled）→ Low-Bit Fixed Point（INT8 Jetfire；INT4 Xi et al. Hadamard；1-Bit BitNet/b1.58 ternary {-1,0,1}）。

4. **Memory Optimizations 支柱（§6）** —— 四类 memory 占用（Model States 16Φ / Activations / Temp Buffers / Fragmentation）对应四类技术
   - **Activation Recomputation（§6.1）**：Static evicting（Checkmate MILP；Selective-checkpointing Megatron-SP；DistFlashAttn 在 FlashAttention 输出设 ckpt；LoongTrain selective-checkpoint++；Yuan et al. Pareto frontier）+ Dynamic evicting（DTR/MegTaiChi/Coop contiguous eviction）。
   - **Redundancy Reduction（§6.2）**：Fully sharding（ZeRO-1/2/3 把 16Φ 降到 16Φ/N）+ Partially sharding（ZeRO++ 二级 shard+量化；MiCS；AMSP/PaRO 三策略 Full-Replica/Full-Sharding/Partial-Sharding；RTP rotated tensor）。
   - **Defragmentation（§6.3）**：Tensor-based（ROAM 树搜索；Imanishi 2D bin-packing + simulated annealing；MegTaiChi/Coop）+ VMM-based（GMLake virtual memory stitching；PyTorch expandable segments v2.1 集成）。
   - **Offloading（§6.4）**：CPU 静态（L2L/ZeRO-Offload 70B@16×V100/Elixir/Yuan 激活粒度）+ CPU 动态（TSPLIT micro-tensor/PatrickStar chunk/Mobius/Harmony/TMOF/STRONGHOLD/MPipeMoE）+ SSD（ZeRO-Infinity 32T@512×V100/Smart-Infinity near-storage/Fuyou activation-to-SSD/MoESys 2D prefetch）。

5. **Communication Optimizations 支柱（§7）**
   - **Collective Communication（§7.1）**：Pre-Defined（MPI/NCCL/RCCL；Ring/Double Binary Tree/Hybrid Two-level AllReduce/BlueConnect/Plink）+ Synthesized（GC3 DSL；SCCL SMT；TACCL MILP；Blink topology probing；P² parallel matrix simulation）。
   - **Communication Scheduling（§7.2）**：FIFO（Poseidon/GradientFlow/PyTorch-DDP bucket fusion）+ Priority（P3 slice；TicTac critical path；ByteScheduler Bayesian tuning；PACE preemptive；Lina MoE All-to-All 优先）+ Decomposition（pipeline stage Breadth-First/Fold3D/TriRace；comm primitive Wang/SYNDICATE MCMC/Centauri/DeAR；computation CoCoNet/T3/Oases；ooo-backprop；Lynx recomputation overlap）。
   - **In-Network Aggregation（§7.3）**：Ethernet-based（SwitchML DPDK/FPISA P4 FP16/NetReduce RoCE+FPGA/AllReduce-Switch/PANAMA/ATP multi-tenant）+ InfiniBand-based（NVIDIA SHARP v1/v2/v3 on EDR/HDR/NDR + NVSwitch-v3）。

6. **Fault Tolerance 支柱（§8）** —— 检测 + 恢复双层
   - **Failure Analysis（§8.1）**：硬件故障为主（Acme 硬件最严重；C4 82.5% 故障局限单节点；LLaMA3 78% 硬件问题；A100/H100 高故障率）；OPT 175B 实际 57 天 vs 理想 25 天，**56% 时间浪费于故障处理**（§8.1 标志性数字）。
   - **Anomaly Detection（§8.2）**：Statistical monitoring（DCGM SM/NVLink 指标 + heartbeat；MegaScale RDMA metric；C4 transport-layer；NCCLX PyTorch 共设计；Vela Multi-NIC health；TPUv4 healthd；Transom ML 异常检测）+ Proactive validation（MegaScale lightweight test；Vela two-tier；TPUv4 preflight；SuperBench）。
   - **Checkpoint-Based Recovery（§8.3）**：Persistent（Synchronous DeepSpeed/Varuna；JIT-Checkpointing 失败后即时 ckpt 最多损失 1 mini-batch；Flash-Checkpoint distributed cache；Universal Checkpointing 跨并行策略）+ Snapshot-Stall（Check-N-Run；TorchSnapshot chunking；MegaScale/InternEvo 单 worker 读+broadcast）+ Asynchronous（DeepFreeze/CheckFreq/LightCheck/DataStates-LLM/FastPersist double-buffer）+ In-Memory（Gemini CPU ckpt placement；REFT Redis+RAIM5 erasure coding）。
   - **Checkpoint-Free Recovery（§8.4）**：Live migration（Parcae 三迁移机制；Oobleck pipeline template）+ Module redundancy（Bamboo bubble 冗余 stage；SlipStream 跨 replica 路由；SWARM 异构不可靠设备）。

## 表格（原文结构化）

### 表 1：基础设施支柱 → 仓库相关论文 / 系统映射（基于 §3, Fig.4）

| 子领域 | 代表系统（原文引用） | 与仓库论文关联 |
|---|---|---|
| AI Accelerators | NVIDIA Ampere/Hopper/Blackwell；AMD MI250X；TPUv4；Cerebras CS-2 | [[ascend-950-npu-architecture-whitepaper]]（华为 NPU 硬件对照）；[[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]（CloudMatrix384 SuperPod 算力供给） |
| Chip-to-Chip Topology | NVLink cube-mesh；NVSwitch 900 GB/s；TPU 3D-Torus | [[ascend-950-npu-architecture-whitepaper]]（Ascend HCCS 互联对照） |
| Node-to-Node | InfiniBand NDR 400Gbps；RoCE-v2；GPUDirect-RDMA | [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]（RoCE 组网实践）；[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]（拓扑优化直接对标 rail-optimized/rail-only/TopoOpt） |
| Training-Optimized Topology | rail-optimized；rail-only；HPN(Alibaba)；BiGraph；HammingMesh | [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]（ATop→ZCube 自动拓扑优化管线，对应 §3.2.3 reconfigurable + training-optimized） |
| Storage | Tectonic；HDFS；Ceph；Lustre；Alluxio；JuiceFS | — |
| Workload Scheduling | Crius；Hydro；Acme；Pollux；Sia | — |
| Resource Scheduling | Cassini；SiloD；Synergy；EnvPipe；Zeus；Perseus | — |

### 表 2：并行策略支柱 → 仓库论文映射（基于 §4, Fig.7/Fig.8/Fig.9）

| 并行维度 | 代表方法（原文） | 与仓库论文关联 |
|---|---|---|
| Data Parallelism (F=1/W/hybrid) | PyTorch-DDP；Horovod；ZeRO-3；FSDP；MiCS | [[zero-memory-optimizations-toward-training-trillion-parameter-models]]（ZeRO 系列，§4.1.1 + §6.2.1 核心源头） |
| Tensor Parallelism 1-D/2-D/2.5-D/3-D | Megatron-TP；Optimus；Tesseract；3-D TP | [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]（1-D TP 列-行切分开山之作，§4.1.2）；[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]（Interleaved 1F1B + 3D 并行，§4.1.3）；[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]（10K+ GPU 实践，§3.2 + §8.1 + §8.3 多处引证）；[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]（Megatron-Core MoE，§4.1.5 expert parallelism） |
| Pipeline Parallelism (bubble/memory) | GPipe；1F1B；Interleaved 1F1B；Zero Bubble；Chimera；TeraPipe；BPipe；AdaPipe | [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]（Interleaved 1F1B 原始出处）；[[muon-is-scalable-for-llm-training]]（Muon 优化器与 pipeline 协同的可扩展性参照） |
| Sequence Parallelism (ring/ulysses/hybrid) | Ring Self-Attention；Megatron-SP；DeepSpeed-Ulysses；Context Parallel；LoongTrain；USP；WallFacer | — |
| Expert Parallelism (MoE) | GShard；Switch Transformer；Tutel；DeepSpeed-MoE；Megablocks；Lina；SmartMoE；Prophet | [[scalable-training-of-mixture-of-experts-models-with-megatron-core]]（§4.1.5 sparse activation + comm optimization + load balance 三子类直接对应） |
| Auto Parallelism | Alpa；FlexFlow；GSPMD；Unity；Galvatron；Colossal-Auto | — |
| Heterogeneous Parallelism | Pathways；Whale；DeepSpeed-Chat；OpenRLHF；ReaLHF；PUZZLE | — |

### 表 3：通信/内存/容错支柱 → 仓库论文映射（基于 §6/§7/§8）

| 支柱 | 子类 | 代表方法 | 仓库关联 |
|---|---|---|---|
| Memory | Activation Recomputation | Checkmate；Selective-checkpointing；DistFlashAttn；LoongTrain selective++ | — |
| Memory | Redundancy Reduction | ZeRO-1/2/3；ZeRO++；MiCS；AMSP；RTP | [[zero-memory-optimizations-toward-training-trillion-parameter-models]]（ZeRO 全系，§6.2.1 16Φ→16Φ/N 数学推导源头） |
| Memory | Offloading | ZeRO-Offload；ZeRO-Infinity；PatrickStar；Fuyou；MoESys | [[zero-memory-optimizations-toward-training-trillion-parameter-models]]（ZeRO-Offload/Infinity 同源延伸） |
| Communication | Collective Comm | NCCL；RCCL；Ring/Tree/Hybrid；SCCL；TACCL；Blink | [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]（大规模 collective 实践 + ECMP/Enhanced-ECMP） |
| Communication | Comm Scheduling | ByteScheduler；PACE；Lina；CoCoNet；ooo-backprop；Lynx | — |
| Communication | In-Network Aggregation | SHARP v1/v2/v3；SwitchML；FPISA；NetReduce | [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]（CloudMatrix 网络聚合对照 SHARP） |
| Fault Tolerance | Anomaly Detection | MegaScale monitoring；C4；NCCLX；Vela；TPUv4 healthd | [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]（§8.2 lightweight test + RDMA 监控） |
| Fault Tolerance | Checkpoint Recovery | JIT-Checkpointing；Flash-Checkpoint；Universal Checkpointing；DeepFreeze；Gemini；REFT | — |
| Fault Tolerance | Checkpoint-Free | Parcae；Oobleck；Bamboo；SlipStream；SWARM | — |

## 与同类对比

与 [[a-survey-of-large-language-models]]（Zhao et al., [26]）对比：该 Zhao survey 是 **LLM 算法/模型全景综述**（预训练架构、训练算法、指令微调、对齐），而本 survey 在 §2.4 明确将其归入 "algorithms for training / instruction tuning / alignment" 的 **不在本文讨论范围** 之列。两者互补：Zhao 回答"训练什么模型/用什么算法"，本 survey 回答"在什么硬件/系统上、用哪种并行/通信/内存策略把模型训出来"。本 survey 的 systemic 视角（infra→parallelism→comm→memory→fault）是 Zhao survey 完全不涉及的维度。

与 [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] 对比：后者聚焦 **推理阶段 KV cache 管理**（serving 侧加速），而本 survey 聚焦 **训练阶段** 全栈。两者在 sequence parallelism（§4.1.4）和 attention 优化（§5.1.1 FlashAttention）有技术交叉点——长上下文训练的 ring-attention/Ulysses 思想与 KV cache 管理共享 attention 分块/通信原理，但目标函数不同（训练吞吐 vs 推理延迟）。

与其他既有 LLM survey（§2.4）的差异定位：
- Wan et al. [29]：model-centric + data-centric efficient 方法，非 systemic。
- Liu et al. [30]：训练 + 推理部署，覆盖广但不深入训练系统内部。
- Xu et al. [31]：resource-efficient，算法+系统混合，但量化/微调偏算法。
- Zhu [32] / Han [33]：压缩 + PEFT，算法侧。
- Liang et al. [36]：auto-parallelism 综述，但面向 general DNN 非 LLM 特化。
- Mayer [35]：distributed DNN 系统，非 LLM 时代。

本 survey 的独特点：**唯一以 SER 框架贯穿、以 distributed infra→training system 全栈为 scope、且明确包含 LLM 时代新兴 workload（MoE §4.1.5、RLHF §4.3.2）的 systemic 综述**。

## 跨论文关系（→ MOC 谱系）

本 survey 是 **distributed-training taxonomy 锚点**，置于"训练系统谱系"根节点，向下辐射：

- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — §4.1.2 Tensor Parallelism 1-D 列-行切分的开山原论文，本 survey §4.1.2 + §5.2.1 多处引用为 baseline。
- [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] — §4.1.3 Interleaved 1F1B + 3D 并行（DP×TP×PP）的工业级落地，本 survey §4.1.3 pipeline bubble 与 §4.1 hybrid parallelism 的核心引证。
- [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] — §3.2.3 rail-optimized topology + §8.1 failure analysis + §8.3 snapshot-stall checkpoint 的 10K+ GPU 实践范本，本 survey 多章节直接引用。
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — §4.1.5 Expert Parallelism 三子类（sparse activation / comm optimization / load balance）的 Megatron-Core 实现。
- [[zero-memory-optimizations-toward-training-trillion-parameter-models]] — §6.2.1 Redundancy Reduction 的 ZeRO-1/2/3 源头（16Φ→16Φ/N 数学推导），并延伸至 §6.4.1 ZeRO-Offload、§6.4.3 ZeRO-Infinity。
- [[muon-is-scalable-for-llm-training]] — 优化器侧可扩展性参照，与本 survey §5 computation optimization + §4.1.3 pipeline 协同的设计空间互补（本 survey §2.4 明确声明"advanced optimization algorithms [34] 不在 scope"，Muon 类正落在该边界）。
- [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] — §3.2.3 Training-Optimized Topology + Reconfigurable Topology 的工业自动化对应（ATop→ZCube 直接对标 rail-optimized/rail-only/TopoOpt/SiP-ML 谱系）。
- [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]] — §3.1 AI Accelerators + §3.2 Network + §7.3 In-Network Aggregation 的华为侧 infra 对照（CloudMatrix384 vs NVIDIA SuperPod/TPUv4）。
- [[ascend-950-npu-architecture-whitepaper]] — §3.1.2 Other AI Accelerators + §3.2.1 Chip-to-Chip 的华为 NPU 硬件侧参照（vs NVIDIA GPU / AMD MI250X / TPU）。
- [[a-survey-of-large-language-models]] — sibling survey，算法侧 complement（见"与同类对比"）。
- [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] — sibling survey，推理侧 complement，attention 优化技术交叉。

## 局限与边界

1. **时间窗截断（arXiv v1, 2024-07-29）**：未覆盖 2024 下半年以来的关键进展——DeepSeek-V3 的 FP8 训练日志、Muon 优化器大规模验证、Blackwell B200/GB200 量产、1-bit LLM（BitNet b1.58 之后）的下游评估。§5.2.3 对 1-bit 的讨论止于 BitNet b1.58，未涉及其训练稳定性在大规模上的实证。
2. **光计算展望偏 speculative（§9）**：结论章提出 silicon photonics 范式转移（Taichi 160 TOPS/W、TopoOpt/TPUv4 OCS），但缺乏大规模训练实证，停留在 "may necessitate" 推测层面。
3. **RLHF 系统侧覆盖偏浅（§4.3.2）**：仅列举 DeepSpeed-Chat/OpenRLHF/ReaLHF/PUZZLE 框架，未深入 PPO 训练中 actor/critic/reward/reference 四模型的显存-通信-调度联合优化的量化模型，也未涉及 DPO 类免 reward model 范式的系统含义。
4. **量化训练的精度-效率权衡缺实证表（§5.2）**：罗列 FP8/INT8/INT4/1-bit 方法，但未给出"精度损失 vs 训练加速比"的统一基准对比表，实践者难以直接选型。
5. **MoE 系统侧未覆盖 expert routing 的算法-系统联合（§4.1.5）**：TA-MoE 提了 topology-aware routing，但缺 DeepSeek-V2 MLA + MoE 这类架构-系统协同设计的深度讨论。
6. **Auto Parallelism 搜索成本未充分量化（§4.2）**：Alpa/Unity/Aceso 的搜索时间常数被提及但未横向对比，实践可落地性评估不足。
7. **Fault Tolerance 的"故障预测"缺位（§8.2）**：仅 reactive monitoring + proactive validation，未涉及基于 ML 的故障预测（时序模型预测 GPU 退化），而 Transom 仅一笔带过。
8. **非 NVIDIA 生态覆盖不均（§3.1.2）**：AMD ROCm / 华为 Ascend / 国产加速器的内容浅，主要因公开系统性资料少；[[ascend-950-npu-architecture-whitepaper]] 类一手资料在 survey 截稿时尚未充分流通。
9. **网络拥塞控制（§3.2.4）未与训练调度（§3.4）联合建模**：CASSINI/MLT 做了初步 traffic-aware 调度，但 congestion control 与 collective comm scheduling 的端到端协同优化仍是开放问题。
10. **明确排除项（§2.4）**：LLM 架构演进 [24][25]、训练算法 [26]、指令微调 [27]、对齐 [28]、模型压缩 [32]、PEFT [33]、advanced optimization algorithms [34]、general distributed DNN systems [35]、general DNN auto-parallelism [36]——这些边界使本 survey 高度聚焦 systemic，但也意味着算法-系统协同的设计空间（如 Muon+pipeline、量化感知并行）留白。
