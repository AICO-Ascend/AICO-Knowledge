---
paper_num: "51"
title: "Efficient Training of Large Language Models on Distributed Infrastructures: A Survey"
authors: "Efficient Training of Large Language Models on Distributed Infrastructures: A Survey Jiangfei Duan∗, Shuo Zhang∗, Zerui Wang∗, Lijuan Jiang, Wenwen Qu, Qinghao Hu, Guoteng Wang, Qizhen Weng, Hang Yan, Xingcheng Zhang, Xi"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2407.20018"
pdf: "papers/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey.pdf"
slug: "efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey"
tags: [training]
---

# Efficient Training of Large Language Models on Distributed Infrastructures: A Survey

> [!abstract] 摘要（原文）
> 1\. ✨ 本文全面综述了分布式 LLM 训练系统的最新进展，旨在解决大规模 LLM 训练在 Scalability, Efficiency 和 Reliability (SER) 方面的核心挑战。 2. ⚡️ 论文详细探讨了包括 Data, Tensor, Pipeline, Sequence 和 Expert 等多种 Hybrid Parallelism 策略，以及 Operator Optimization、Mixed-Precision Training、Memory Optimization 和 Communication Optimization 等关键技术，以提升训练效率。 3. 💾 此外，文章还深入分析了 LLM 训练的 Infrastructure (包括 AI Accelerators, Network 和 Storage) 设计、Job Scheduling 方法，并介绍了 Anomaly Detection 和 Checkpoint-based/Checkpoint-free Recovery 等 Fault Tolerance 机制以确保系统可靠性。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Efficient Training of Large Language Models on Distributed Infrastructures: A Survey Jiangfei Duan∗, Shuo Zhang∗, Zerui Wang∗, Lijuan Jiang, Wenwen Qu, Qinghao Hu, Guoteng Wang, Qizhen Weng, Hang Yan, Xingcheng Zhang, Xi
- **arXiv**: https://arxiv.org/abs/2407.20018
- **本地 PDF**: `papers/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey.pdf`
- **页数**: 42

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig01.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p02.png]]*
> [!quote] caption
> Overall structure of this survey.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图1以2×3虚线网格将全文结构化为**6大主题、共19个子节**：
- §3 基础设施（AI加速器/网络/存储，3子节）
- §4 并行方案（混合/自动/异构并行，3子节）
- §5 计算优化（算子优化/混合精度训练，2子节）
- §6 内存优化（激活重计算/冗余消除/碎片整理/卸载，4子节）
- §7 通信优化（集合通信/通信调度/网内聚合，3子节）
- §8 容错（故障分析/异常检测/检查点恢复/无检查点恢复，4子节）

**技术结论：** 该总纲论证高效LLM分布式训练需在"硬件基础→并行策略→算子/内存/通信优化→容错"全栈协同推进，单一层级优化无法独立解决问题，揭示多维度交织的优化空间。

**作用：** 作为论文路线图，统领后续章节从各维度系统综述与对比各类优化技术。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig02.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p03.png]]*
> [!quote] caption
> A typical Transformer layer contains an Attention

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

图2将典型Transformer层拆为两大块：左侧Attention块含Norm、融合投影Linear(Wqkv)、Q/K/V三路送入MHA/GQA、再经Linear(Wo)输出，最后残差相加⊕；右侧FFN块为SwiGLU结构——Norm后Linear(W1)经SiLU与Linear(W3)逐元素相乘⊙，再由Linear(W2)映射回原维度并残差相连。全层共6个权重矩阵、2次Norm、2处残差。

论文借此论证：Transformer层是分布式训练（TP/PP/DP）的基本切分与调度单元，Attention（GEMM+集合通信）与FFN（纯GEMM）的计算/通信特性差异决定了不同的并行与重计算策略。该图为后续混合精度、激活检查点、序列并行等优化讨论提供了统一的计算图参考。

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig03.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p04.png]]*
> [!quote] caption
> Infrastructure overview for distributed LLM training.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图以分层架构呈现分布式LLM训练基础设施：顶层为"Backend Network (Training Traffic)"，下挂4个并行Compute Node；底层为"Frontend Network (Management & Storage Traffic)"，接入Training Dataset Storage与Checkpoint Storage；右侧独立列出Scheduling System与Fault Tolerance（含Anomaly Detection、Failure Recover两个子模块）。

**关键论证：** 原文借此说明训练流量与存储/管理流量须在网络上分离，避免I/O抢占梯度同步带宽；同时表明调度与容错（检测+恢复）作为横切子系统与计算集群解耦，构成独立保障层。

**论文作用：** 作为统一参照拓扑，为后续并行策略、通信优化、容错与调度等章节提供共享的组件边界与术语基准。

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig04.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p05.png]]*
> [!quote] caption
> Studies on infrastructure optimizations for distributed LLM training.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图4以三级树状结构系统梳理LLM分布式训练基础设施研究：根节点分四大类——①AI加速器（NVIDIA Ampere/Hopper/Blackwell GPU，及AMD、GAUDI、TPU、Graphcore IPU、Cerebras CS-2等异构芯片）；②网络基础设施（Chip-to-Chip NVLink/NVSwitch/TPU、Node-to-Node RDMA InfiniBand/RoCE、网络拓扑Clos/Dragonfly/HPN、负载均衡与拥塞控制PFC/DCQCN/HPCC等）；③存储系统（检查点Tectonic/HDFS/Ceph与训练数据Lustre/GPFS/Alluxio）；④调度系统（工作负载调度Tiresias/Pollux与资源调度Zeus/Perseus）。该图支撑"算力–网络–存储–调度全栈协同优化"核心论断，是论文基础设施优化分类章节的骨架图，为后续并行策略与资源管理讨论提供分类依据。

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig05.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p06.png]]*
> [!quote] caption
> Five chip-to-chip topologies: tree topology, cube-mesh topology, switch-based fully-connected topology, P2P-based

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示五种片间(chip-to-chip)拓扑结构：(a)树形以Root Complex为根，经PCIe Switch分级连接8个叶节点；(b)Cube-Mesh由8节点构成三维立方网格；(c)Switch全连通过2个NVSwitch各连接4个芯片；(d)P2P全连8节点两两直连；(e)2D-Torus为4×4网格，红/蓝绕回边实现行与列首尾相连。

原文借此论证各拓扑在带宽、可扩展性与延迟上的权衡——树形存在根节点瓶颈，Mesh/Torus利于扩展，全连带宽最优但连线数达O(N²)。

该图作为硬件层基础，支撑后续分布式并行训练策略(数据/流水线/张量并行)与通信效率优化的分析。

### Figure 6 (p.7) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig06.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p07.png]]*
> [!quote] caption
> Four typical network topologies in large-scale GPU clusters: Clos topology, Dragonfly+ topology, rail-optimization

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

图示展示四类大规模GPU集群网络拓扑：(a) **Clos** 为标准Fat-Tree四层结构（2 Core → 各Pod内2 Spine → 2 Leaf → 约8 GPU），全连接带宽均衡；(b) **Dragonfly+** 去除Core层，Pod间通过Spine交换机直接弧形互联，降低跨Pod跳数与时延；(c) **Rail-Optimized** 保留Clos骨干，但同rank GPU跨Leaf交换机交叉互联，专为张量并行AllReduce优化；(d) **Rail-Only** 进一步精简，跨Pod仅靠Core，Pod内仅Leaf-GPU Rail直连。

论文借此论证：**网络拓扑直接决定LLM分布式训练集合通信的带宽、跳数与成本**，是基础设施选型核心权衡点。该图为后续并行策略（TP/PP/DP）与通信优化（overlap、压缩、调度）章节提供物理层前提。

### Figure 7 (p.10) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig07.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p10.png]]*
> [!quote] caption
> Studies on parallelism schemes for distributed LLM training.

> [!tip] 技术解读（多模态）
> 【图文联合解读】## 图文联合解读

**核心结构**：该图以树状分类法系统梳理分布式LLM训练的并行方案，根节点"Parallelism Schemes"下分三大支系：(1) **混合并行**（5子类，含数据/张量/流水线/序列/专家并行，约60+项工作，细分子问题如流水线气泡、内存不均衡、通信优化、负载均衡）；(2) **自动并行**（通用框架与Transformer专用，约25项）；(3) **异构并行**（硬件与模型两类，约18项）。量化地映射了约100余篇文献。

**关键结论**：论证了单一并行策略已难以应对大规模LLM训练，研究呈两大趋势——其一是**方案融合化**（DP/TP/PP/SP/EP混合），其二是**自动化与异构化**（自动搜索最优切分策略、利用异构硬件/模型资源提升效率）。

**论文作用**：作为第III节并行方案的**全局索引图**，为后续章节（流水线气泡优化、内存均衡、MoE通信、异构调度等）的方法分类与对比提供统一框架，是读者快速定位具体优化技术的导航图。

### Figure 8 (p.12) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig08.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p12.png]]*
> [!quote] caption
> An example of 3D-parallelism with data parallelism, tensor parallelism, and pipeline parallelism.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**图示结构**：展示2个DP副本（Rank 0/1）经AllReduce跨副本同步；每副本内含4级流水线（Stage 0-3），各级嵌入4路TP（TP-0~3），共16层Transformer按"L0-3/4-7/8-11/12-15"四段分配，Stage间以Send/Recv衔接，每层沿TP维度四色分块表示权重切片。

**技术结论**：3D并行可正交叠加——PP切分网络深度、TP切分单层宽度、DP扩展样本量；三类通信（AllReduce / Send-Recv / TP组内集合）沿独立网域并行，互不抢占带宽，规避瓶颈重叠。

**论文作用**：作为全文"DP×TP×PP×SP"四维资源拓扑基准图，为后续章节讨论通信优化（如梯度压缩）、显存调度与流水线气泡消解提供统一参照框架。

### Figure 9 (p.14) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig09.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p14.png]]*
> [!quote] caption
> Expert parallelism. The dotted line highlights the

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示N设备专家并行架构：每个设备独占一个Expert（图示Expert-1与Expert-N），Embedding/Attention/Add&Norm层跨设备复制；Token经Gating路由后，由All-to-All Dispatch分发至各设备Expert，再经All-to-All回传汇合，经Add&Norm生成输出Token。

论证结论：Expert分片部署配合两次All-to-All通信实现跨设备协作，可在显存受限下扩展MoE参数容量并保持负载均衡，是大规模MoE分布式训练的核心并行策略。

论文作用：与数据并行、张量并行、流水线并行并列，作为综述中支撑"参数与稀疏容量扩展"章节的关键配图。

### Figure 10 (p.17) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig10.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p17.png]]*
> [!quote] caption
> An example of RLHF. Inference process: 1 The

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

该图以**RLHF 流程**为对象，展示"推理—训练"两阶段闭环：①Actor 模型（可训练）以 Query Dataset 输出的 x₁…xₙ 为输入，生成 y₁…yₙ 响应；②Critic（可训练）、Reward、Reference（冻结）三模型并行推理，分别产出 value、score 与 KL 估计，用于③回灌 Actor 进行策略更新。图中通过"Trainable/Freezed"颜色标注明确区分各角色角色属性，揭示了 RLHF 四模型协同 + 三类监督信号（value/score/KL）的核心结构。

**技术结论**：RLHF 的高效训练需同时承载多个异构模型（其中仅 Actor、Critic 可训练），并融合三类不同来源信号，是 LLM 分布式训练中最复杂的范式之一，因此论文将其单列为代表性案例进行讨论。

**论文作用**：作为综述中典型 RL 训练范式的可视化锚点，为后续展开 RLHF 分布式优化挑战（多模型同步、显存压力、通信开销）提供统一参照框架。

### Figure 11 (p.19) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig11.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p19.png]]*
> [!quote] caption
> Studies on computation optimizations for distributed LLM training.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（≤220字）：**

该图以树形分类展示"LLM训练计算优化"的两大主线：

- **算子优化**：分*手写类*（FlashAttention/2/3、BPT、ByteTransformer 等6项）与*自动类*——Kernel 级（Halide、TVM、Triton、ALCOP 等5项）+ Graph 级（Chimera、TorchDynamo、TorchInductor、JIT-Q 等5项）；
- **混合精度训练**：*16位*（FP16、BF16 等4项）、*亚8位浮点*（FP8-LM 等4项）、*低位定点*（INT8 Jetfire、INT4、1-Bit BitNet/b1.58，共4项）。

论文借此论证：计算优化呈"**手写算子 + 编译自动化**"双轨并行，并沿精度持续下探。它在论文方法学链路中与并行策略、内存优化并列，构成"**算法—系统—硬件**"三位一体高效训练框架的核心环节。

### Figure 12 (p.21) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig12.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p21.png]]*
> [!quote] caption
> Studies on memory optimizations for distributed LLM training.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图示对象与结构**
该图为三级树状分类法：根节点"LLM训练内存优化"分4大类、8子类，覆盖约42篇代表工作——
①激活重计算：动态逐出3篇（DTR、MegTaiChi、Coop）+静态逐出5篇（Checkmate、LoongTrain、DistFlashAttn等）；
②冗余削减：全分片2篇（ZeRO、FSDP）+部分分片5篇（ZeRO++、MiCS、PaRO、RTP、AMSP）；
③碎片整理：张量基5篇（ROAM、ZeRO-R等）+VMM基2篇（GMLake、Expandable Segments）；
④卸载：CPU静态4篇+CPU动态6篇（TSPLIT、PatrickStar等）+SSD 6篇（ZeRO-Infinity、Angel-PTM等）。

**关键技术结论**
优化路径沿"重算→分片→整理→外存卸载"递进，从静态策略（ZeRO/FSDP/Checkmate）演进至动态策略（TSPLIT/ZeRO-Infinity），分别缓解激活值、参数、优化器状态及显存碎片化四大瓶颈。

**文中作用**
作为分布式LLM训练内存优化的全景总图，承接前文并行策略章节，奠定"算法—系统协同"的整体优化框架。

### Figure 13 (p.25) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig13.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p25.png]]*
> [!quote] caption
> Communication traffic heatmap for InternLM-2

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**核心对象**：128×128 GPU 对通信流量热力图，颜色由黄（256MB）到深紫（12GB）。对角线上呈现 16 个 8×8 深紫块，对应 16 个 TP 组（128/8），单组通信约 12GB（最高带宽）；黄色对角线代表 PP 通信（量最小）；蓝色散布点为 DP×ZeRO-1 的跨节点梯度同步（量中等）。

2）**关键结论**：TP 组被紧凑地排在同一节点内（深紫块集中且规则），充分利用节点内 NVLink 高带宽；而 DP/ZeRO-1 跨节点通信走 IB。这直观验证了"拓扑感知布局优先级 TP>DP"的设计原则——将通信量最大的并行维度映射到最快链路。

3）**论文作用**：作为实验链路中的可视化证据，为"如何将多维并行（TP/PP/DP/ZeRO）映射到层级化集群拓扑"这一调度方法提供定量依据，支撑后续通信开销分析与拓扑优化策略。

### Figure 14 (p.26) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig14.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p26.png]]*
> [!quote] caption
> Studies on communication optimizations for distributed LLM training.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图14 联合解读**

图14以三级树状分类系统梳理LLM分布式训练的通信优化技术，沿三大维度展开：**① 集体通信**——预定义算法（MPI/NCCL/RCCL库，Ring/Tree/Hybrid拓扑）与合成算法（GC3、SCCL、TACCL、Blink、P²共5种）；**② 通信调度**——FIFO（Poseidon、GradientFlow、PyTorch DDP）、优先级调度（P3、TicTac、ByteScheduler、PACE、Lina）及分解式调度（流水线/通信/计算三类分解，附ooBP）；**③ 网络内聚合**——以太网方案（SwitchML、FPISA、NetReduce、AllReduce-Switch、PANAMA、ATP共6种）与InfiniBand方案（NVIDIA Mellanox SHARP v1/v2/v3）。

该图为论文通信优化章节提供结构化分类基座，明确各子方向代表性工作，是后续方法对比、瓶颈分析与优化策略选型的统一索引框架。

### Figure 15 (p.29) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig15.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p29.png]]*
> [!quote] caption
> Studies on fault tolerance techniques for distributed LLM training.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**核心对象与结构**：图为"LLM分布式训练容错"三级分类树，根节点展开为三类：① Anomaly Detection，含 Statistical Monitoring（TPUv4 Healthd、MegaScale 等8项）与 Proactive Validation（SuperBench、Preflight Check 等4项）；② Checkpointing-Based Recovery，其中 Persistent Checkpointing 按范式进一步细分 Synchronous（DeepSpeed、Varuna 等5项）、Snapshot-Stall（Check-N-Run、TorchSnapshot 共2项）、Asynchronous（DeepFreeze、CheckFreq、LightCheck 等5项），另含 In-Memory（Gemini、REFT 2项）；③ Checkpointing-Free Recovery，含 Live Migration（Parcae、Oobleck）与 Module Redundancy（Bamboo、SlipStream、SWARM）。整图归类约 32 个系统/方法。

**关键技术结论**：揭示容错体系按"检测—恢复—无检查点恢复"分层递进；持久化检查点因同步、一致性、停顿开销的权衡而分化出同步/快照停顿/异步三档；无检查点路径以活迁移与模块冗余提供轻量替代。

**论文作用**：作为综述"分布式基础设施可靠性"章节的分类地图，串联异常检测与恢复策略，为读者建立容错研究全景并支撑后续对比与选型。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\text{Attention}(Q, K, V) = \texttt{softmax}\left(\frac{QK^T}{\sqrt{d}}\right)V
$$

## 相关论文

- [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] — Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core
- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] — MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs
- [[zero-memory-optimizations-toward-training-trillion-parameter-models]] — ZeRO: Memory Optimizations Toward Training Trillion Parameter Models

## 技术点深读（DEEP）

![[deep/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey.txt`（271696 字符）供引用检索。