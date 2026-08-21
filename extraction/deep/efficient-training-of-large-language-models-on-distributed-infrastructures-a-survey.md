# Efficient Training on Distributed Infrastructures Survey — 技术点深读（DEEP 2026-08-18；2026-08-21 织入 15 张 M3 图解读）

> 源文献：Duan et al., "Efficient Training of Large Language Models on Distributed Infrastructures: A Survey", arXiv:2407.20018v1 (29 Jul 2024). Shanghai AI Laboratory, CUHK, Fudan, SJTU, NTU, PKU.
> 定位：distributed-training taxonomy 锚点 — 覆盖从基础设施到训练系统全栈的综述，是本仓库"训练系统谱系"的总纲。
> 图注来源：M3 captions（`minimax_captions.json`，15 张，p.02–p.29），按段织入；公式以 `formulas.json` LaTeX 为权威源（该论文仅 1 条，见 §5 支柱）。

## 核心问题

该 survey 直面 LLM 训练在万卡级集群上面临的 **"SER" 三重困境**（§1, §2.3）：

- **Scalability（可扩展性）**：模型规模未饱和（scaling laws 仍未 plateau，§1 引 [8]），训练系统需在数万 GPU/AI 加速器上保持正确性与精度，涉及硬件配置、网络互联、训练框架的协同设计。典型案例：LLaMA-3 在 16K H100 上预训练约 54 天（§1, §8.1）。
- **Efficiency（效率）**：以 **MFU（Model FLOPs Utilization）** 为核心度量。LLaMA3 在 16K GPU 上仅达 38%–41% MFU（§1, §2.3），说明规模化下利用率急剧下降。需在 parallelism / computation / communication / memory 四维联合优化。
- **Reliability（可靠性）**：训练周期长达数周到数月，节点级故障频发——Bloom 384 GPU 每周 1–2 次故障（§8.1）、OPT 175B 两周 40+ 次中断、MegaScale 12,288 GPU 数周内 100+ 次失败、LLaMA3 54 天 466 次中断。单节点 1.5% 日故障率外推到 1,000 GPU 即 84.8% 日故障率（§8.1），synchronous training 让任意节点崩溃拖垮全局。

该 survey 的精确目标是：**给出从 distributed training infrastructure（accelerator/network/storage/scheduling）到 training systems（parallelism/computation/communication/memory/fault tolerance）的端到端技术图谱**（§1, Fig.1），补齐既有 LLM survey 偏算法/资源压缩而忽视 systemic 设计的空白（§2.4 明确对比 Wan [29]/Liu [30]/Xu [31]）。

**综述结构图（Fig. 1, p.02）** 以 2×3 taxonomic grid 把 §3–§8 六章铺成一张总图：§3 Infrastructure（AI Accelerators / Network Infrastructure / Storage）、§4 Parallelism Schemes（Hybrid / Auto / Heterogeneous）、§5 Computation Optimizations（Operator Optimization / Mixed-Precision Training）、§6 Memory Optimizations（Activation Recomputation / Redundancy Reduction / Defragmentation / Offloading）、§7 Communication Optimizations（Collective Communication / Scheduling / In-Network Aggregation）、§8 Fault Tolerance（Failure Analysis / Anomaly Detection / Checkpoint-Based & Checkpoint-Free Recovery）。图的核心信息是：**taxonomy 沿"硬件底座 → 分布式协同 → 微观优化 → 韧性"递进**，即可扩展 LLM 训练需要 compute/memory/network/fault-recovery 四层协同设计——每一层必要但单独不充分。这张图也是本 deep note "关键创新点"六支柱结构的原文依据。

**背景段（§2）图证：Transformer 层结构（Fig. 2, p.03）**——survey 的技术讨论对象。图中一个标准 Transformer 层由两个共享输入 $X$ 的并行子块构成，数据流自下而上：左 **Attention block** 为 $X \to$ Norm $\to$ Linear($W_{qkv}$) 并行投影出 $Q,K,V$ $\to$ MHA/GQA $\to$ Linear($W_o$) $\to$ 残差加（$\oplus$）；右 **FFN block** 为 $X \to$ Norm $\to$ 两路并行 Linear $W_1$ 与 $W_3$ $\to$ $W_1$ 输出经 SiLU 后与 $W_3$ 输出逐元素乘（$\odot$）$\to$ Linear($W_2$) $\to$ 残差加。两图要点：(1) FFN 采用 **SwiGLU 式门控激活**（两路线性投影经 SiLU 门控相乘），即 LLaMA 家族对原始 ReLU 两层 FFN 的现代替换，同等计算量下参数效率更优；(2) 两块均用 pre-norm + residual。该层结构是全文所有优化维度的作用对象：Attention block 的 $Q,K,V$ 投影与 MHA 是 §5.1.1 FlashAttention 融合与 §4.1.2 张量并行列-行切分的靶点，FFN 的双线性结构是 §4.1.5 Expert Parallelism（把 FFN 替换为 MoE）的插入位置，而 Norm/残差处的激活正是 §6.1 activation recomputation 选择 checkpoint 的候选点。

## 关键创新点

该 survey 的 taxonomy 支柱按 §3–§8 六章组织，每一支柱既是分类轴也是技术演进脉络：

1. **Infrastructure 支柱（§3）—— 硬件-网络-存储-调度四元组**

   **基础设施总览（Fig. 3, p.04）** 给出分布式 LLM 训练部署的分层架构：核心是若干 **Compute Nodes**，由 **Backend Network**（高带宽训练流量）互联；下方 **Frontend Network**（管理与存储流量）把计算集群接到 **Training Dataset Storage** 与 **Checkpoint Storage**；右侧两个正交控制子系统——顶部 **Scheduling System**、以及含 **Anomaly Detection** 与 **Failure Recover** 模块的 **Fault Tolerance** 栈。架构刻意把计算流量（backend）与 I/O/管理流量（frontend）**解耦**，并为数据平面配上独立的可靠性与调度平面——支撑数千 GPU 的独立扩展、低争用与快速故障隔离。这张图正是 §3 四元组 + §8 容错在物理部署上的投影。

   **基础设施 taxonomy（Fig. 4, p.05）** 把 §3 全章铺成四分支层级树：AI Accelerators（NVIDIA Ampere/Hopper/Blackwell × AMD GPU/GAUDI/TPU/Graphcore IPU/Cerebras CS-2）、Network Infrastructure（Chip-to-Chip：Cube-Mesh/FC/Torus；Node-to-Node：GPUDirect-RDMA/InfiniBand/RoCE/iWARP；Network Topology：HPC/Training-Optimized/Reconfigurable；Load Balancing & CC：ECMP/packet spraying/PFC/DCQCN/HPCC 等）、Storage Systems（Checkpoint：Tectonic/HDFS/Ceph；Training Data：Lustre/GPFS/BeeGFS/Alluxio/JuiceFS 等）、Scheduling Systems（Workload：Tiresias/Pollux/Sia…；Resource：Cassini/HIRE/Zeus/Perseus…）。图的要点：**通信开销在 LLM 训练中占主导（某些场景 >90% 时间），故 taxonomy 明显向网络栈倾斜**——从物理互联、拓扑设计到拥塞控制全覆盖，反映出带宽与延迟（而非裸算力）才是首要可扩展性瓶颈。

   - **AI Accelerators（§3.1）**：NVIDIA GPU（Ampere/Hopper/Blackwell，含 Transformer Engine 混合 FP8/FP16）、AMD MI250X（Frontier 64GB HBM, 191.5 TFLOPS FP16）、Habana GAUDI、Google TPUv4（4096 chips, ~60% peak FLOPS）、Graphcore Bow Pod64（22 petaFLOPS）、Cerebras CS-2（wafer-scale, 850K cores）。
   - **Network Infrastructure（§3.2）**：Chip-to-Chip（PCIe→NVLink cube-mesh→NVSwitch fully-connected 300/600/900 GB/s→TPU 2D/3D-Torus ICI）× Node-to-Node（GPUDirect-RDMA, InfiniBand EDR/HDR/NDR 100/200/400 Gbps, RoCE-v1/v2）× Network Topology（HPC Clos/Dragonfly+；训练优化 rail-optimized/rail-only/HPN/BiGraph/HammingMesh；可重构 SiP-ML/TopoOpt/TPUv4 OCS）× Load Balancing & Congestion Control（ECMP→packet spraying→Ethereal→HPN；PFC/TIMELY/DCQCN/HPCC/EQDS；MLTCP/CASSINI/MLT 基于 LLM 周期性 elephant-flow 特性）。

     **Chip-to-chip 五种拓扑（Fig. 5, p.06）**：(a) **Tree**——PCIe Switch + Root Complex 构成多级层次；(b) **Cube-Mesh**——规则网格（4 GPU 为平面 mesh，8 GPU 为 cube-mesh），即 NVLink-1.0 形态；(c) **Switch-based Fully-Connected**——GPU 经 NVSwitch 芯片全互联取得 all-to-all 带宽（如 DGX-2 六颗 NVSwitch）；(d) **P2P-based Fully-Connected**——每对芯片直连（Intel/AMD/华为 Ascend 采用）；(e) **2D-Torus**——带 wraparound 边的网格，提供多条最短路径（Google TPUv2/v3）。要点：带宽/延迟/可扩展性的 trade-off 决定选型——torus 提供冗余路径，fully-connected 带宽最大但布线成本随规模陡增，mesh/tree 以成本换性能。

     **GPU 集群四种网络拓扑（Fig. 6, p.07）**：统一由 Core（绿）→ Spine（红）→ Leaf（蓝）→ GPU 端点（紫）三层交换机组网并按 Pod 分组。(a) **Clos** 全 fat-tree：每 leaf 连每 spine、每 spine 连每 core，any-to-any 带宽但交换机成本高；(b) **Dragonfly+** 去掉 core 层、加 Pod 间直连弧；(c) **Rail-Optimized** 保留 Clos 全层级，但把跨机架同序号 GPU 对齐到共享 leaf 交换机上，缩短 collective 流量路径；(d) **Rail-Only** 干脆去掉 core：rail 内流量本地化，rail 间流量卸载到独立的旁路 Clos。要点：**LLM 训练网络拓扑正与并行策略协同设计**——rail-optimized 利用 collective 通信模式的可预测性，rail-only 以灵活性换成本，标志向 workload-aware 精简交换织物的转向。
   - **Storage（§3.3）**：Checkpoint 存储（Tectonic/HDFS/Ceph，70B 模型 ckpt 达 980GB）× 训练数据存储（Lustre/GPFS/BeeGFS 并行文件系统；Alluxio/JuiceFS/Quiver/Fluid 缓存层；LLaMA3 15T tokens≈30TB，原始数据 100× 放大达 PB 级）。
   - **Scheduling（§3.4）**：Workload scheduling（异构感知 Gavel/Gandivafair、job-packing FGD/Lucid、adaptive-scaling Pollux/Sia；LLM 专用 Crius/Hydro/Acme）× Resource scheduling（Cassini 网络、HIRE in-network、SiloD 存储、Synergy CPU、EnvPipe/Zeus/Perseus 能效）。

2. **Parallelism Schemes 支柱（§4）—— Hybrid / Auto / Heterogeneous 三分法**

   **并行策略 taxonomy（Fig. 7, p.10）** 把 §4 铺成三分支层级树：Hybrid Parallelism（Data/Tensor/Pipeline——细分为 Pipeline Bubble 与 Memory Imbalance 缓解/Sequence/Expert Parallelism——细分为 Sparse Activation、Communication Optimization、Load Balancing）、Auto Parallelism（General Frameworks × Transformer-Specific）、Heterogeneous Parallelism（硬件异构 × 模型异构如 RLHF），每个叶节点按引文编号列举代表系统。要点：**高效 LLM 训练早已不是单一维度（如纯数据并行）能解决**——现代系统必须组合多种策略（常靠自动化）来隐藏 pipeline 气泡、平衡 MoE 负载、利用硬件/模型异构性。

   - **Hybrid Parallelism（§4.1）** 5 子维：Data Parallelism（F=1 full replication PyTorch-DDP/Horovod；F=W full sharding ZeRO-3/FSDP；1<F<W hybrid sharding MiCS）→ Tensor Parallelism（1-D Megatron-LM 列-行切分；2-D Optimus；2.5-D Tesseract；3-D）→ Pipeline Parallelism（GPipe fill-drain；1F1B PipeDream；Interleaved 1F1B；Zero Bubble 拆 B/W 梯度；Chimera 双向；TeraPipe token 级；memory 平衡 BPipe/MPress/Chimera/Hanayo/V-Shape/AdaPipe）→ Sequence Parallelism（ring-based Ring Self-Attention/DistFlashAttn/Context Parallel/Striped Attention/BurstAttention/Blockwise Ring/WallFacer；head-dim DeepSpeed-Ulysses；hybrid USP/LoongTrain Double-Ring）→ Expert Parallelism（sparse activation GShard/Switch/Tutel/DeepSpeed-MoE/Megablocks/ScatterMoE；comm 优化 PipeMoE/ScheMoE/Lina/Janus/TA-MoE；load balance FasterMoE/SmartMoE/FlexMoE/Prophet）。

     **3D 并行实例（Fig. 8, p.12）** 展示混合并行的层级嵌套（外→内）：最外 **Data Parallelism**——两个 DP rank 复制全模型、跨节点 AllReduce 同步梯度；其内 **Sequence Parallelism** 沿序列维度协调激活；再内 **Tensor Parallelism** 四路切分（TP-0…TP-3）在节点内分片权重矩阵/激活；最内 **Pipeline Parallelism** 四个串行 stage 分到连续层区间（Stage 0: Layer 0–3 … Stage 3: Layer 12–15），stage 间 Send/Recv 传激活。要点：**3D 并行层级嵌套三种正交策略，把每种匹配到合适带宽的互联**——TP 用节点内 NVLink 快带宽做权重/激活分片；PP 只在层边界换激活、用便宜的跨节点带宽；DP 包在最外复制模型、AllReduce 平均梯度。三个轴各解决不同瓶颈（TP/PP 解显存、DP 解吞吐），单一方案无法独立完成万亿参数训练。

     **Expert Parallelism（Fig. 9, p.14）**：$N$ 台设备上的数据流（每台自下而上）：Input Token Vector → Embedding → Add&Norm → Attention → Add&Norm → **Gating** →（跨设备）→ **Expert-i** →（跨设备）→ Add&Norm → Output Token Vector。Gating 与 Experts 之间夹两个 **All-to-All Dispatch**（橙色椭圆），把 token 路由到远端设备上被指派的 expert、并把结果送回；虚线椭圆圈出 MoE 特有块（Gating + All-to-All + Experts），与标准 Transformer 块区分。要点：**每台设备恰好驻留一个 expert，设备间协作完全经由 gating 层两侧的 All-to-All 通信**而非复制 expert——这正是 §4.1.5 中 comm 优化（Lina/Janus 等）与 load balance 子类的共同作用点。
   - **Auto Parallelism（§4.2）**：General（Mesh-TensorFlow/GSPMD/OneFlow SBP/Alpa/Unity/Aceso/PartIR/nnScaler/AutoDDL；search-based FlexFlow SOAP+MCMC、AutoMap MCTS）+ Transformer-Specific（DeepSpeed-Autotuning/Galvatron/Merak/Colossal-AI/Galvatron-BMW）。
   - **Heterogeneous Parallelism（§4.3）**：异构硬件（HetPipe/Whale/AMP/Pathways/SDPIPE/HAP/PipePar + geo-distributed Yuan/SWARM/FusionAI）× 异构模型（RLHF 四模型 PPO：DeepSpeed-Chat/HuggingFace TRL/OpenRLHF/APP/ReaLHF/PUZZLE）。

     **RLHF 架构与数据流（Fig. 10, p.17）**：Query Dataset 喂给**可训练 Actor Model**（红）生成 response；response 与原 query 一起路由到三个**冻结模型**（蓝）——Critic Model 产 value、Reward Model 产 score、Reference Model 产 KL 估计；训练阶段，推理期收集的 value/score/KL 信号驱动梯度下降，回灌更新 Actor 与 Critic 权重。要点：**RLHF 把推理（冻结模型产训练信号）与训练（actor/critic 梯度更新）解耦**，模型异构性——reference/reward/critic 冻结而仅 actor/critic 更新——是其额外显存与时间开销的核心来源。此即 §4.3.2 模型异构并行的系统化动因。

3. **Computation Optimizations 支柱（§5）**

   **计算优化 taxonomy（Fig. 11, p.19）** 把 §5 铺成两分支：Operator Optimizations → Manual（FlashAttention 家族、BPT、SWattention、ByteTransformer）× Automatic（Kernel-level：Halide/TVM/Roller/Triton/ALCOP；Graph-level 编译器：Chimera/Welder/Slapo/TorchDynamo+TorchInductor/JIT-Q）；Mixed-precision Training → 16-Bit Floating Point（FP16/BF16、Campo、THC）× Sub-8-Bit Floating Point（Wang et al./Sun et al./FP8-LM/Rouhani et al.）× Low-Bit Fixed Point（INT8 Jetfire；INT4 Xi et al.；1-Bit BitNet/BitNet b1.58）。要点：优化策略横跨一条**粒度谱**——从细粒度 kernel tiling 的访存/计算效率到粗粒度图融合，并伴以激进降精度直至二值表示。

   - **Operator Optimizations（§5.1）**：Manual（FlashAttention 系列 IO-aware tiling + online softmax；FlashAttention-3 H100 WGMMA/TMA warp-specialized pipeline；BPT 扩展 tiling 到 FFN；SWattention Sunway；ByteTransformer padding-free variable-length）+ Automatic（kernel-level Halide/TVM/Roller/Triton/ALCOP；graph-level Chimera/Welder/Slapo/TorchDynamo+TorchInductor/JIT-Q）。

     该支柱的算法基元即标准 scaled dot-product attention（§5.1.1，fulltext L205-211 原文公式；LaTeX 权威源 `extraction/formulas.json` 该 slug 条目[0]，双源校验一致）：

     $$
     \text{Attention}(Q, K, V) = \texttt{softmax}\left(\frac{QK^T}{\sqrt{d}}\right)V
     $$

     其中 $Q,K,V$ 为输入 token 向量 $X=[x_1,\dots,x_n]$ 经线性变换得到的 query/key/value 张量，$d$ 为 head 维度，$\sqrt{d}$ 缩放因子稳定 softmax 数值。FlashAttention 系列的核心机制在于：把上式中 $QK^T$、softmax、$\cdot V$ 的多次 HBM 往返融合为单个 CUDA kernel 内的分块（tiling）+ online softmax（lazy 除法延迟到末端），从而把 attention 的 HBM 访问复杂度从 $O(n^2)$ 降到 $O(n^2 d / M)$（$M$ 为 SRAM 容量），而数学输出与原式严格等价——这是 §5.1.1 所有 manual 算子优化的共同不变式。FlashAttention-3 进一步在 H100 上用 WGMMA/TMA warp-specialized pipeline 把非-GEMM 操作（softmax 等）隐藏到异步 GEMM 后面。
   - **Mixed-Precision Training（§5.2）**：16-Bit（FP16/BF16 + loss scaling；Campo casting 优化；THC 同态压缩）→ Sub-8-Bit（FP8 Wang/Sun hybrid/FP8-LM/Rouhani microscaled）→ Low-Bit Fixed Point（INT8 Jetfire；INT4 Xi et al. Hadamard；1-Bit BitNet/b1.58 ternary {-1,0,1}）。

4. **Memory Optimizations 支柱（§6）** —— 四类 memory 占用（Model States 16Φ / Activations / Temp Buffers / Fragmentation，Φ 为模型参数量；该 16Φ=4Φ 参数+4Φ 梯度+12Φ Adam 一/二阶矩 的 memory 推导见 fulltext L2250-2255，**未收录 formulas.json，按 .txt 引用不渲染 $$**）对应四类技术

   **内存优化 taxonomy（Fig. 12, p.21）** 把 §6 铺成四分支层级树：Activation Recomputation → Dynamic Evicting（DTR/MegTaiChi/Coop）× Static Evicting（Checkmate/LoongTrain/Yuan et al./Selective Checkpointing/DistFlashAttn）；Redundancy Reduction → Fully Sharding（ZeRO/FSDP）× Partially Sharding（ZeRO++/MiCS/PaRO/RTP/AMSP）；Defragmentation → Tensor-based（ROAM/ZeRO-R/Imanishi et al./MegTaiChi/Coop）× VMM-based（GMLake/Expandable Segments）；Offloading → CPU（Static：L2L/ZeRO-Offload/Elixir/Yuan et al.；Dynamic：TSPLIT/PatrickStar/Mobius/Harmony/TMOF/STRONGHOLD）× SSD（ZeRO-Infinity/Angel-PTM/Smart-Infinity/Fuyou/MoESys）。要点：**没有单一技术独大**——每类解决不同瓶颈（算换存 / 参数冗余 / 碎片分配 / 容量扩展），实用系统通常跨分支组合多种策略以塞进 GPU 显存预算。

   - **Activation Recomputation（§6.1）**：Static evicting（Checkmate MILP；Selective-checkpointing Megatron-SP；DistFlashAttn 在 FlashAttention 输出设 ckpt；LoongTrain selective-checkpoint++；Yuan et al. Pareto frontier）+ Dynamic evicting（DTR/MegTaiChi/Coop contiguous eviction）。
   - **Redundancy Reduction（§6.2）**：Fully sharding（ZeRO-1/2/3 把 16Φ 降到 16Φ/N，N 为数据并行度；推导见 fulltext L2399-2411，**未收录 formulas.json，按 .txt 引用不渲染 $$**）+ Partially sharding（ZeRO++ 二级 shard+量化；MiCS；AMSP/PaRO 三策略 Full-Replica/Full-Sharding/Partial-Sharding；RTP rotated tensor）。
   - **Defragmentation（§6.3）**：Tensor-based（ROAM 树搜索；Imanishi 2D bin-packing + simulated annealing；MegTaiChi/Coop）+ VMM-based（GMLake virtual memory stitching；PyTorch expandable segments v2.1 集成）。
   - **Offloading（§6.4）**：CPU 静态（L2L/ZeRO-Offload 70B@16×V100/Elixir/Yuan 激活粒度）+ CPU 动态（TSPLIT micro-tensor/PatrickStar chunk/Mobius/Harmony/TMOF/STRONGHOLD/MPipeMoE）+ SSD（ZeRO-Infinity 32T@512×V100/Smart-Infinity near-storage/Fuyou activation-to-SSD/MoESys 2D prefetch）。

5. **Communication Optimizations 支柱（§7）**

   **通信流量热图（Fig. 13, p.25）** 是全书最具实证分量的图：128×128 GPU 对热图，可视化 InternLM-2 102B 预训练在 128 GPU 上单 iteration 的通信流量，混合并行配置 TP=8 / PP=4 / DP=4 / ZeRO-1=4，色标 256 MB（黄）→ 12 GB（深紫）。按拓扑排布优先级 TP > DP/ZeRO-1 > PP，可分解出四类流量图样：① **TP 的 AllReduce**——16 个对角致密 8×8 方块，对应 NVSwitch 全互联的节点内拓扑；②③ **DP/ZeRO-1 的 ReduceScatter/AllGather**——四个 32×32 矩形子网格内六条对称对角条纹（且 DP/ZeRO-1 节点内流量与 TP 累进同格）；④ **PP 的 Send/Recv**——((32,0),(128,96)) 与 ((0,32),(96,128)) 处两条细黄线。要点：**TP 流量（节点内 NVSwitch）单对流量最大，故把 TP 组共置同节点的混合并行布局主导带宽压力；PP 流量可忽略，是最便宜的可跨节点扩展维度**——这为 §3.2.3 rail-optimized 拓扑与 §4 混合并行的协同设计提供了量化依据。

   **通信优化 taxonomy（Fig. 14, p.26）** 把 §7 铺成三分支：Collective Communication → Pre-Defined Algorithms（库：MPI/NCCL/RCCL；模式：Ring/Tree/Hybrid）× Synthesized Algorithms（GC3/SCCL/TACCL/Blink/P²）；Communication Scheduling → FIFO-based（Poseidon/GradientFlow/PyTorch DDP）× Priority-based（P3/TicTac/ByteScheduler/PACE/Lina）× Decomposition-based（Pipeline/Communication/Computation decomposition + out-of-order backprop）；In-Network Aggregation → Ethernet-based（SwitchML/FPISA/NetReduce/AllReduce-Switch/PANAMA/ATP）× InfiniBand-based（NVIDIA Mellanox SHARP v1/v2/v3）。要点：三层互补——**定制 collective 算法（降延迟）、智能调度重叠算/通（FIFO/优先级/分解的依赖感知重排）、交换机内硬件加速聚合（把 AllReduce 卸载进网络）**——共同对付分布式 LLM 训练的主导通信瓶颈。

   - **Collective Communication（§7.1）**：Pre-Defined（MPI/NCCL/RCCL；Ring/Double Binary Tree/Hybrid Two-level AllReduce/BlueConnect/Plink）+ Synthesized（GC3 DSL；SCCL SMT；TACCL MILP；Blink topology probing；P² parallel matrix simulation）。
   - **Communication Scheduling（§7.2）**：FIFO（Poseidon/GradientFlow/PyTorch-DDP bucket fusion）+ Priority（P3 slice；TicTac critical path；ByteScheduler Bayesian tuning；PACE preemptive；Lina MoE All-to-All 优先）+ Decomposition（pipeline stage Breadth-First/Fold3D/TriRace；comm primitive Wang/SYNDICATE MCMC/Centauri/DeAR；computation CoCoNet/T3/Oases；ooo-backprop；Lynx recomputation overlap）。
   - **In-Network Aggregation（§7.3）**：Ethernet-based（SwitchML DPDK/FPISA P4 FP16/NetReduce RoCE+FPGA/AllReduce-Switch/PANAMA/ATP multi-tenant）+ InfiniBand-based（NVIDIA SHARP v1/v2/v3 on EDR/HDR/NDR + NVSwitch-v3）。

6. **Fault Tolerance 支柱（§8）** —— 检测 + 恢复双层

   **容错 taxonomy（Fig. 15, p.29）** 把 §8 铺成三分支层级树：Anomaly Detection → Statistical Monitoring（Healthd/MegaScale/C4/Vela/Unicorn/Transom/NCCLX/NCCL flight recorder）× Proactive Validation（MegaScale lightweight tests/SuperBench/Vela/TPUv4 Preflight Check）；Checkpointing-Based Recovery → Persistent Checkpointing（**Synchronous**：DeepSpeed/Varuna/JIT-Checkpointing/Flash-Checkpoint/Universal Checkpointing；**Snapshot-Stall**：Check-N-Run/TorchSnapshot；**Asynchronous**：DeepFreeze/CheckFreq/LightCheck/DataStates-LLM/FastPersist）× In-Memory Checkpointing（Gemini/REFT）；Checkpointing-Free Recovery → Live Migration（Parcae/Oobleck）× Module Redundancy（Bamboo/SlipStream/SWARM）。要点：清晰的**设计谱系**——检测先行（统计监控 + 主动校验）尽早抓故障；恢复策略在**持久性 vs 开销**间取捨（persistent ckpt 以存储/IO 成本换故障存活，in-memory 以持久性换速度，checkpoint-free 彻底消除 IO 瓶颈但要冗余资源）；且 persistent checkpointing 已分化为同步（强一致、高停顿）与异步（低停顿、弱保证）两派，反映领域向"checkpoint IO 与计算重叠"的转向；无单一技术独大，现代系统（MegaScale/Vela）多支柱组合。

   - **Failure Analysis（§8.1）**：硬件故障为主（Acme 硬件最严重；C4 82.5% 故障局限单节点；LLaMA3 78% 硬件问题；A100/H100 高故障率）；OPT 175B 实际 57 天 vs 理想 25 天，**56% 时间浪费于故障处理**（§8.1 标志性数字）。
   - **Anomaly Detection（§8.2）**：Statistical monitoring（DCGM SM/NVLink 指标 + heartbeat；MegaScale RDMA metric；C4 transport-layer；NCCLX PyTorch 共设计；Vela Multi-NIC health；TPUv4 healthd；Transom ML 异常检测）+ Proactive validation（MegaScale lightweight test；Vela two-tier；TPUv4 preflight；SuperBench）。
   - **Checkpoint-Based Recovery（§8.3）**：Persistent（Synchronous DeepSpeed/Varuna；JIT-Checkpointing 失败后即时 ckpt 最多损失 1 mini-batch；Flash-Checkpoint distributed cache；Universal Checkpointing 跨并行策略）+ Snapshot-Stall（Check-N-Run；TorchSnapshot chunking；MegaScale/InternEvo 单 worker 读+broadcast）+ Asynchronous（DeepFreeze/CheckFreq/LightCheck/DataStates-LLM/FastPersist double-buffer）+ In-Memory（Gemini CPU ckpt placement；REFT Redis+RAIM5 erasure coding）。
   - **Checkpoint-Free Recovery（§8.4）**：Live migration（Parcae 三迁移机制；Oobleck pipeline template）+ Module redundancy（Bamboo bubble 冗余 stage；SlipStream 跨 replica 路由；SWARM 异构不可靠设备）。

## 表格（原文结构化）

### 表 1：基础设施支柱 → 仓库相关论文 / 系统映射（基于 §3, Fig. 3 p.04 / Fig. 4 p.05 / Fig. 5 p.06 / Fig. 6 p.07）

| 子领域 | 代表系统（原文引用） | 与仓库论文关联 |
|---|---|---|
| AI Accelerators | NVIDIA Ampere/Hopper/Blackwell；AMD MI250X；TPUv4；Cerebras CS-2 | [[ascend-950-npu-architecture-whitepaper]]（华为 NPU 硬件对照）；[[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]（CloudMatrix384 SuperPod 算力供给） |
| Chip-to-Chip Topology | NVLink cube-mesh；NVSwitch 900 GB/s；TPU 3D-Torus | [[ascend-950-npu-architecture-whitepaper]]（Ascend HCCS 互联对照） |
| Node-to-Node | InfiniBand NDR 400Gbps；RoCE-v2；GPUDirect-RDMA | [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]（RoCE 组网实践）；[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]（拓扑优化直接对标 rail-optimized/rail-only/TopoOpt） |
| Training-Optimized Topology | rail-optimized；rail-only；HPN(Alibaba)；BiGraph；HammingMesh | [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]（ATop→ZCube 自动拓扑优化管线，对应 §3.2.3 reconfigurable + training-optimized） |
| Storage | Tectonic；HDFS；Ceph；Lustre；Alluxio；JuiceFS | — |
| Workload Scheduling | Crius；Hydro；Acme；Pollux；Sia | — |
| Resource Scheduling | Cassini；SiloD；Synergy；EnvPipe；Zeus；Perseus | — |

### 表 2：并行策略支柱 → 仓库论文映射（基于 §4, Fig. 7 p.10 / Fig. 8 p.12 / Fig. 9 p.14 / Fig. 10 p.17）

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
| Memory | Redundancy Reduction | ZeRO-1/2/3；ZeRO++；MiCS；AMSP；RTP | [[zero-memory-optimizations-toward-training-trillion-parameter-models]]（ZeRO 全系，§6.2.1 16Φ→16Φ/N 数学推导源头；推导见 fulltext L2399-2411，未收录 formulas.json，按 .txt 引用） |
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
- [[zero-memory-optimizations-toward-training-trillion-parameter-models]] — §6.2.1 Redundancy Reduction 的 ZeRO-1/2/3 源头（16Φ→16Φ/N 数学推导，推导见 fulltext L2250-2255 + L2399-2411，未收录 formulas.json，按 .txt 引用），并延伸至 §6.4.1 ZeRO-Offload、§6.4.3 ZeRO-Infinity。
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
