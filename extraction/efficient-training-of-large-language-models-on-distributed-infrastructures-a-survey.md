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
> 【图文联合解读】**图文联合解读**

**1) 图示内容**：该图呈现论文的整体结构框架，展示了4个并列的技术维度章节及子节：§4并行策略（4.1混合并行、4.2自动并行、4.3异构并行，各1子节）、§5计算优化（5.1算子优化、5.2混合精度训练）、§7集合通信（7.1集合通信、7.2通信调度、7.3网内聚合）、§8容错（8.1故障分析、8.2异常检测、8.3检查点恢复、8.4无检查点恢复，共4子节最多）。

**2) 论证结论**：原文用此图论证分布式大模型训练效率可沿"并行—计算—通信—容错"四层栈式分解，每层含具体子技术（如并行3类、通信3类、容错4类）。

**3) 论文作用**：作为综述的导航图，为读者提供分类索引，明确各优化技术在整个训练流水线中的层级定位与覆盖范围。

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
> 【图文联合解读】**图3图文联合解读**

图示将分布式LLM训练基础设施划分为左右两平面：左侧**数据面**自上而下依次为Backend Network（承载训练流量）→4个Compute Node→Frontend Network（管理与存储流量）→Training Dataset Storage与Checkpoint Storage；右侧**控制面**包含Scheduling System，以及Fault Tolerance子系统（细分Anomaly Detection与Failure Recover）。

**论证结论**：分布式LLM高效训练不仅依赖算力横向扩展，更需前后端网络解耦（分离训练流量与管控/存储流量）、存储分层（数据集与检查点独立），并通过调度与容错子系统协同保障大规模训练的稳定性与可恢复性。

**论文作用**：作为综述的总览架构图，统摄后续对并行计算、网络拓扑、存储优化、调度策略与容错机制等章节的系统化论述，构成全篇方法学的整体框架。

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig04.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p05.png]]*
> [!quote] caption
> Studies on infrastructure optimizations for distributed LLM training.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图中将分布式LLM训练的基础设施优化研究分为两大类别（可视为按优化主题的分类表）：

**第一类（资源调度与分配类，12项）**：Tiresias、THEMIS、ElasticFlow、Gavel、Gandiva_fair、FGD、Lucid、Pollux、Sia、Crius、Hydro、Acme，主要聚焦GPU/作业调度与公平性。

**第二类（系统效率与弹性类，7项）**：Cassini、HIRE、SiloD、Synergy、EnvPipe、Zeus、Perseus，侧重流水线、弹性伸缩、能效与容错。

**原文论证结论**：作者通过该分类表系统梳理了"基础设施优化"这一维度的代表性工作，凸显调度、弹性、效率三大研究主线，为后续讨论并行策略与算法优化奠定对比基线。

**论文作用**：作为综述的方法学骨架之一，与算法层优化形成"算法×基础设施"双维度分类图谱，帮助读者快速定位研究坐标。

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig05.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p06.png]]*
> [!quote] caption
> Five chip-to-chip topologies: tree topology, cube-mesh topology, switch-based fully-connected topology, P2P-based

> [!tip] 技术解读（多模态）
> 【图文联合解读】图5展示五种芯片间互连拓扑：(a)树形——1个Root Complex经PCIe Switch分层挂接16片芯片；(b)Cube-Mesh——8节点构成3D立方体邻接；(c)交换全连接——2个NVSwitch各自将上下两组芯片全连；(d)P2P全连接——8节点两两直连，呈完全图；(e)2D-Torus——4×4网格，含红色行向与蓝色列向环绕边。

论文据此论证：各拓扑在带宽、延迟、可扩展性与成本间存在显著权衡——树形廉价但根节点处易成瓶颈；Cube-Mesh结构平衡；NVSwitch全连（如NVLink）提供高带宽；P2P延迟最低但N²连线难以扩展；2D-Torus（如TPU Pod）利于大规模部署但AllReduce需特殊映射。

作用：作为后续讨论3D并行（TP/PP/DP）通信模式与节点内拓扑选型匹配的硬件基础铺垫。

### Figure 6 (p.7) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig06.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p07.png]]*
> [!quote] caption
> Four typical network topologies in large-scale GPU clusters: Clos topology, Dragonfly+ topology, rail-optimization

> [!tip] 技术解读（多模态）
> 【图文联合解读】图6展示大规模GPU集群四种典型网络拓扑（2 Pod 并列，每Pod含2 Spine + 2 Leaf + 每Leaf下挂8 GPU节点）：(a) Clos——Core(2)-Spine(4)-Leaf(4)三级直连，叶仅连本Pod；(b) Dragonfly+——省去Core层，两Pod Spine间以弧形长线直接跨Pod互连；(c) Rail-Optimized——保留Core-Spine层，但每Leaf横向扇出至对Pod GPU（底部大量交叉连线），带宽局部优化；(d) Rail-Only——仅本Pod内Leaf-GPU链路，无跨Pod底层通路。原文借此论证：拓扑决定All-Reduce等集合通信的对分带宽与最短路径，直接影响DP/TP/PP并行切分及计算-通信重叠效率。该图为后续章节搭建"硬件拓扑→并行策略→训练效率"的物理前提，是连接基础设施与算法优化的枢纽图示。

### Figure 7 (p.10) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig07.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p10.png]]*
> [!quote] caption
> Studies on parallelism schemes for distributed LLM training.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图7联合解读：**

**核心对象与结构**：图7将分布式LLM训练的并行方案研究分为两类列表呈现——上框列举12项并行方案研究（HetPipe [221]、AccPar [222]、Whale [223]、AMP [224]、Pathways [225]、HPH [226]、SDPipe [227]、HAP [228]、PipePar [229]、Yuan et al. [230]、SWARM [231]、FusionAI [232]），涵盖异构流水线、自动并行等系统级方案；下框列举6项RLHF训练系统（DeepSpeed-Chat [233]、HuggingFace TRL [234]、OpenRLHF [235]、Adaptive Placement and Parallelism [236]、ReaLHF [237]、PUZZLE [238]），聚焦强化学习微调场景。

**技术结论**：通过分类列举，揭示分布式LLM训练并行技术已从单一流水线/数据并行拓展到异构资源调度、自动并行搜索及RLHF专用框架等多元路径，技术生态丰富且针对不同训练阶段（预训练、对齐）有专门优化。

**论文作用**：作为综述章节的分类总览图，为后续深入讨论各类并行策略提供文献索引框架，便于读者快速定位相关工作。

### Figure 8 (p.12) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig08.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p12.png]]*
> [!quote] caption
> An example of 3D-parallelism with data parallelism, tensor parallelism, and pipeline parallelism.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 8）：**

该图以一个16层LLM为例，展示三层并行嵌套结构：外层为2个Data Parallel副本（Rank 0/1），通过AllReduce同步梯度；内层包含4个Pipeline Stage（0/1/2/4，跳号编排），分别承载Layers 0-3、4-7、8-11、12-15，Stage间以Send/Recv传递激活值；每个Stage内部进一步切分为4个Tensor Parallel分片（TP-0至TP-3）。原图还嵌入Sequence Parallel层。

原文借此论证：**DP解决数据扩展、PP分摊层间计算与内存、TP分摊单层显存**，三者正交可叠加，是支撑千亿级LLM在分布式集群上训练的核心组合范式。在全文方法链中，该图为"并行策略分类与组合"章节的实例化说明，为后续ZeRO、激活重计算等内存优化技术的讨论奠定拓扑基础。

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
> 【图文联合解读】**核心对象与结构**：该图为 RLHF 四模型协作数据流图。包含 2 个可训练模型（Actor Model、Critic Model，红色）与 2 个冻结模型（Reference Model、Reward Model，蓝色），并标注三步流程：① Actor 由 query 集 x₁…xₙ 生成 response y₁…yₙ；② Critic/Reference/Reward 推理产出 value、score、KL 估计；③ 训练信号回传 Actor 与 Critic。

**关键结论**：RLHF 需协同 4 个异构模型并交替执行"推理—评分—训练"，其中 2 个冻结、2 个可训练，证明 RLHF 对分布式显存、通信与调度均提出高于普通 SFT 的资源需求。

**论文作用**：作为 RLHF 训练范式章节的结构锚点，为后文分布式优化策略（模型并行、显存管理等）提供动机与需求基线。

### Figure 11 (p.19) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig11.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p19.png]]*
> [!quote] caption
> Studies on computation optimizations for distributed LLM training.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**核心对象**：分类树状结构，列出分布式LLM训练中4类计算优化研究及约22项代表性工作：
① **编译优化**（左侧标签 "…tions"）：Kernel级（Halide[267]、TVM[252]、Roller[268]、Triton[269]、ALCOP[270]）；Graph级（Chimera[271]、Welder[272]、Slapo[203]、TorchDynamo&TorchInductor[273]、JIT-Q[274]）。
② **混合精度**（标签 "…int"）：FP16 [275]、Campgo[276]、BF16 [277]、THC[278]。
③ **亚字节精度**（标签 "…oint"）：Wang et al.[279]、Sun et al.[280]、FP8-LM[281]、Rouhani[282]。
④ **量化**（标签 "…nt"）：INT8-Jetfire[283]、INT4-Xi[284]、1-Bit-BitNet[285]/b1.58[286]。

**关键论证**：计算优化从**编译器层级**（kernel、graph）到**数值精度层级**（mixed precision、sub-byte、quantization）逐级压降算力与显存，是分布式训练效率提升的关键技术支柱。

**论文作用**：作为综述对"计算优化"子领域的系统分类索引，与通信优化、并行策略、内存优化等并列，构成完整分布式LLM训练优化全景图。

### Figure 12 (p.21) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig12.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p21.png]]*
> [!quote] caption
> Studies on memory optimizations for distributed LLM training.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图12展示分布式LLM训练内存优化研究的分类树（局部）。顶部框为"卸载（Offloading）"，细分为静态卸载（L2L、ZeRO-Offload、Elixir、Yuan et al.，共4项）与动态卸载（TSPLIT、PatrickStar、Mobius、Harmony、TMOF、STRONGHOLD，共6项）；下方框列举另一类共6项工作（ZeRO-Infinity、Angel-PTM、Smart-Infinity、Fuyou、MoESys等），对应异构存储扩展显存方案。原文据此论证：内存优化研究沿"卸载"与"异构显存扩展"两条路径展开，均通过CPU/NVMe分担GPU显存压力。该图为论文方法综述章节的子分类支撑，系统梳理分布式训练栈，缓解大模型训练的内存瓶颈。

### Figure 13 (p.25) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig13.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p25.png]]*
> [!quote] caption
> Communication traffic heatmap for InternLM-2

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 13）：**

该图为128×128 GPU对通信热力图，量化展示InternLM-2 102B单次迭代在TP=8/PP=4/DP=4/ZeRO-1=4配置下的通信量（256MB–12GB）。

**结构特征**：
- 对角线有16个8×8深紫方块（16组TP群组），单次AllReduce峰值达12GB，为最重通信；
- 蓝色点状散点对应DP/ZeRO群组内通信，强度次之；
- 黄色对角线代表PP点对点通信，仅256MB量级，最轻。

**关键结论**：通信强度呈 TP > DP/ZeRO > PP 的明确层次，验证了"按通信强度优先级排布拓扑"的设计原则——需将高带宽TP通信约束在NVLink域内。

**论文作用**：作为实验证据支撑第7章集体通信优化讨论，证明分层并行中不同维度通信开销差异巨大，是拓扑感知调度与集合通信算法选择的核心依据。

### Figure 14 (p.26) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig14.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p26.png]]*
> [!quote] caption
> Studies on communication optimizations for distributed LLM training.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图14以三层分层结构（左标签被截断，依内容可还原为**Scheduling/ Aggregation/ Delegation**）梳理分布式LLM训练的通信优化研究：

- **上层（调度）**：分四子类——流水线阶段分解（Breadth-First[159]、Fold3D[351]、TriRace[352]）、通信分解（SYNDICATE[354]等4项）、计算分解（CoCoNet[357]等4项）、乱序反向传播[361]，共12篇。
- **中层（聚合）**：SwitchML[362]、FPISA[363]等6种可编程交换机方案。
- **下层（委派）**：仅NVIDIA Mellanox SHARP v1/v2/v3[368]一项，指向硬件卸载。

**论证结论**：通信优化呈"软→硬"分层谱系，从算法调度到网络设备卸载，互补共存。

**论文作用**：作为综述通信优化章节的方法学分类地图，为读者快速定位各层代表工作与选型权衡提供索引。

### Figure 15 (p.29) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig15.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p29.png]]*
> [!quote] caption
> Studies on fault tolerance techniques for distributed LLM training.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（图15）**

该图以分类树形式系统梳理分布式LLM训练容错技术，左侧为四类主干（Checkpointing、Recomputing、Parcae/Oobleck类、Elasticity），右侧罗列代表性工作，共19项：Checkpointing下细分**同步**（DeepSpeed、Varuna、JIT-/Flash-/Universal Checkpointing，5项）、**Snapshot-Stall**（Check-N-Run、TorchSnapshot，2项）、**异步**（DeepFreeze、CheckFreq、LightCheck、DataStates-LLM、FastPersist，5项）；其余三行各列2–3项。

原文借此论证：容错设计存在**同步开销、快照粒度与弹性恢复**间的权衡——主流方案由同步快照逐步演进到异步检查点与弹性冗余。图中各子类的划分与文献编号直接支撑全文"训练效率优化"谱系中的**可靠性分支**，与并行、通信、内存优化并列，是综述方法分类的重要组成部分。

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