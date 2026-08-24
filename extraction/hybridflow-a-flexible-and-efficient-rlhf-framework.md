---
paper_num: "30"
title: "HybridFlow: A Flexible and Efficient RLHF Framework"
authors: "Guangming Sheng The University of Hong Kong gmsheng@connect.hku.hk Chi Zhang ByteDance zhangchi.usc1992@bytedance.com Zilingfeng Ye ByteDance yezilingfeng@bytedance.com Xibin Wu ByteDance wuxibin@bytedance.com Wang Zhang"
date: "2026/1/17"
arxiv: "https://arxiv.org/abs/2409.19256"
pdf: "papers/hybridflow-a-flexible-and-efficient-rlhf-framework.pdf"
slug: "hybridflow-a-flexible-and-efficient-rlhf-framework"
tags: [rl]
---

# HybridFlow: A Flexible and Efficient RLHF Framework

> [!abstract] 摘要（原文）
> 1\. 🤔 HybridFlow 提出了一种混合编程模型，巧妙地结合了单控制器（用于节点间数据流协调）和多控制器（用于高效执行节点内分布式 LLM 计算）范式，旨在解决 RLHF 在 LLM 对齐中面临的复杂性和效率挑战。 2. ⚙️ 该框架设计了分层 API 以实现灵活的 RLHF 算法表达和高效操作编排，并引入了 3D-HybridEngine 用于 Actor 模型在训练和生成阶段之间的高效参数重分片，实现了零内存冗余和显著降低的通信开销。 3. 🚀 实验结果表明，HybridFlow 在运行各种 RLHF 算法时，吞吐量比现有最先进的基线系统（如 DeepSpeed-Chat、OpenRLHF 和 NeMo-Aligner）提高了 1.53 倍至 20.57 倍，验证了其灵活性和高效率。

## 元信息
- **发表日期**: 2026/1/17
- **作者**: Guangming Sheng The University of Hong Kong gmsheng@connect.hku.hk Chi Zhang ByteDance zhangchi.usc1992@bytedance.com Zilingfeng Ye ByteDance yezilingfeng@bytedance.com Xibin Wu ByteDance wuxibin@bytedance.com Wang Zhang
- **arXiv**: https://arxiv.org/abs/2409.19256
- **本地 PDF**: `papers/hybridflow-a-flexible-and-efficient-rlhf-framework.pdf`
- **页数**: 19

## 图表（原文 caption + 页码）

### Figure 1 (p.3) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig01.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p03.png]]*
> [!quote] caption
> Dataflow graph of 3 RLHF algorithms [19, 43, 55].

> [!tip] 技术解读（多模态）
> 【图文联合解读】图展示(a) PPO、(b) Safe-RLHF、(c) ReMax 三种 RLHF 算法的三阶段数据流图，含 actor、critic、reference policy、reward model、cost model 五类模型节点：①生成(Actor Gen)、②准备(Ref/RM/Critic/Cost Fwd 等前向)、③训练(Actor/Critic Training)。Safe-RLHF 引入 cost model 与 L_ptx，ReMax 采用双 actor+双 RM+双 Ref 结构。该图论证：不同 RLHF 算法共享"生成—准备—训练"骨架，但模型组合与依赖各异，故 HybridFlow 须以灵活的多控制器架构统一调度异构数据流，为其模块化设计提供关键动机，并衔接后文对现有框架灵活性差、效率低两类缺陷的剖析。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig02.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p03.png]]*
> [!quote] caption
> Programming model used in RLHF systems. (a)

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（≤220字）：**

图2对比两种RLHF编程模型。(a)现有框架采用纯多控制器：Actor、Critic、Reward各worker独立调度，代码层嵌套`recv_actor()`/`broadcast()`递归调用，由此产生两大缺陷——**Inflexible**（计算与数据依赖深度耦合、难以适配多种LLM系统）与**Inefficient**（训推切换开销大、模型放置策略僵化）。(b) HybridFlow提出混合模型：**Inter-Node**用单控制器统一编排`actor.gen → critic.comp_value → reward.compute_reward`；**Intra-Node**仍保留多控制器并行`gen`/`comp_reward`（含`all_gather_weights`）。由此获得**Flexible**（解耦数据与计算依赖、无缝集成任意LLM）与**Efficient**（零冗余切换、支持灵活模型放置）。该图是论文方法动机的核心可视化，与Table 2实测的训推切换开销直接呼应，奠定后文HybridFlow编程抽象与性能优势的设计基础。

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig03.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p04.png]]*
> [!quote] caption
> Dataflow execution given a model placement plan.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图左侧展示数据流图𝒟，包含Gen、Ref、RM、Value及Actor/Critic Training六个节点；中间为Placement方案，将四类模型分别映射至3台机器的6块GPU：Actor→机器A(GPU0-1)、Critic→机器B(GPU2-3)、Ref与RM共置→机器C(GPU4-5)；右侧Execution Pattern展示时序：Gen与Value分别在A、B上并行执行，Ref与RM在C上串行执行。

该图论证的核心结论是：HybridFlow通过解耦**模型放置**与**计算调度**，使各模型可独立并行于不同设备（如Gen与Value跨机并发），同时允许无依赖的子模型（如Ref、RM）共置以节省显存和资源，从而在3机6卡上灵活组织RLHF多阶段流水线。

此图在论文中起承上启下作用：它是3D并行的具体实例，用以说明所提抽象如何将RLHF复杂依赖关系转化为高效可执行的分布式调度方案，支撑后续吞吐量与可扩展性的实验论证。

### Figure 4 (p.6) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig04.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p06.png]]*
> [!quote] caption
> Architecture of HybridFlow. 3D-HybridEngine and Auto-Mapping algorithm. The hybrid programming model includes a set of hierarchical APIs to enable flexible expression of the RLHF dataflow and effi- cient computation of models in the dataflow (§4). The 3D-

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图自顶向下分5层：①用户输入层（RLHF数据流图、模型/设备配置）；②ParallelWorker层，包含Transfer Protocol、3D-HybridEngine、训练/生成双引擎；③Auto Mapping层（模型放置+设备分配）；④Resource Pool层；⑤底层Physical Devices。

原文借此论证：通过层次化API将RLHF数据流描述与底层分布式执行解耦——上层用数据流图灵活表达算法逻辑，Auto Mapping自动完成模型-设备映射，3D-HybridEngine在统一显存下交错训练与生成，从而避免传统RLHF框架在显存/控制流层面的低效。

该图是整篇论文方法总纲，统领§4-§6各模块定位，并在实验部分支撑其端到端吞吐与显存利用率优势。

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig05.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p06.png]]*
> [!quote] caption
> An illustration of hierarchical APIs. (a) Model with 3D parallel configuration, resource allocation, and 3DParallelWorker initialization. (b) Asynchronous data re- sharding between two models with collect and distribute functions in 3D_PROTO. devices, it facilitates distributed model weight initialization and establishes 3D parallel groups for each model. A parallel group includes a set of GPUs to

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图(a)展示`ActorWorker`继承`3DParallelWorker`，通过`ResourcePool(n_gpus_per_machine × n_machines)`分配GPU，按DP/TP/PP三维配置初始化模型；图(b)展示单控制器调度Actor(p,t,d=1,2,3，3个DP组)与Critic(p,t,d=2,1,2，2个DP组)间的5步异步数据reshard（①调用 ②返回future ③收集 ④分发 ⑤传输）。该图论证：分层API支持异构并行配置模型间的灵活数据重分片，是HybridFlow单控制器多Worker范式实现RLHF灵活训练的核心机制。

### Figure 6 (p.7) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig06.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p07.png]]*
> [!quote] caption
> Implementation of PPO [55], ReMax [43], and Safe- RLHF [19]. Users can adapt to different RLHF algorithms by simply adding or deleting a few lines of code. our programming model, HybridFlow is flexible in support- ing diverse distributed execution patterns without any code change of the RLHF algorithm (Figure 6).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**核心对象与结构**：图右代码展示同一HybridFlow框架下PPO、ReMax、Safe-RLHF三算法的统一编排，分三阶段：①生成响应（`actor.generate_sequences`）；②准备经验（critic/values、reference log_prob、reward、cost、advantages）；③actor-critic训练。蓝色标注ReMax差异（`do_sample=False`、删除critic），红色标注Safe-RLHF差异（复用RewardWorker初始化cost模型、新增`compute_cost`与`pretrain_loss`）。

**关键技术结论**：原文据此论证HybridFlow编程模型无需修改RLHF算法代码即可切换算法，**仅需增删数行**即可适配不同分布式执行模式与损失函数（`algo_type`参数化）。

**方法链路作用**：作为论文"算法灵活性（flexibility）"主张的代码级实证，与吞吐量/可扩展性实验互补，证明框架对多种RLHF范式（单/双/多奖励模型）的低门槛支持是其相对已有系统（Megatron-LM、ColossalAI等）的关键差异化优势。

### Figure 7 (p.8) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig07.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p08.png]]*
> [!quote] caption
> 3D-HybridEngine workflow in one RLHF iteration. 4 GPUs are used for actor training and generation. 1-2-2 (𝑝-𝑡-𝑑) parallel groups are used in training and 1-1-2-2 (𝑝𝑔- 𝑡𝑔-𝑑𝑔-𝑑) parallel groups are used in generation. 5 3D-HybridEngine

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图7解读：3D-HybridEngine工作流**

**核心结构**：展示单次RLHF迭代中4块GPU的完整流程，分为5步：①All Gather模型权重→②加载P1-P4提示词→③生成R1-R4响应并跨TP组AllGather→④将权重重新分片切回训练模式→⑤训练。训练采用1-2-2（p-t-d）并行，生成采用1-1-2-2（pg-tg-dg-d）并行，含2个Micro-DP组、TP组（红虚线）。

**技术结论**：通过权重resharding与并行组重配置，实现同一套4 GPU在生成（低显存、需长序列）与训练（高吞吐）两种模式间零冗余切换，避免传统方案中生成与训练资源割裂的问题。

**论文作用**：作为HybridEngine的核心证据图，支撑"灵活3D并行+零冗余权重转换"这一关键设计，证明RLHF训练在有限GPU资源下仍可高效完成生成—训练循环。

### Figure 8 (p.8) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig08.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p08.png]]*
> [!quote] caption
> Model weights resharding. 2 machines each with 4 GPUs are used for actor training and generation. model parameters updated in iteration 𝑖(step 1○in Figure 7), for generation within each micro DP group. Then, the batch of prompts are loaded to each model replica (step 2○), which generates responses (Generation stage of RLHF). Following this, 3D-HybridEngine performs an all-gather operation on the g

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图8展示RLHF中actor训练→生成阶段的**模型权重重分片**机制，硬件为2机×4卡（G1–G8）。训练时单机内4卡构成TP组、跨机为DP组，每卡持有模型权重分片（橙）与冗余训练权重（灰）。

**(a) HybridFlow-V**：沿用相同TP/DP分组，生成阶段需在TP组内All-Gather完整权重再丢弃未用分片，冗余通信开销大。

**(b) HybridFlow**：采用**Micro-DP组**重新分组，缩小All-Gather范围，每份权重仅在更少卡间共享（如G1+G3互传），显著降低跨阶段通信与显存冗余。

**论证结论**：由于RLHF三阶段（训练/生成/推理）所需并行模式各异，权重分布必然重分配；通过差异化分组设计，HybridFlow可大幅压缩resharding成本。

**论文作用**：该图是3DHybridEngine**自动并行映射与权重重分片**优化的核心可视化证据，直接支撑其对RLHF端到端效率的提升主张。

### Figure 9 (p.11) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig09.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]]*
> [!quote] caption
> PPO throughput. Numbers in parentheses are HybridFlow speedups compared with baselines. 8 16 32 64 128 # of GPUs 0 1 2 3

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图9图文联合解读**

**① 核心对象与数据**：四个子图分别呈现 7B/13B/34B/70B 四种模型规模下 PPO 训练吞吐量（tokens/s）随 GPU 数（8→128）变化的柱状对比，被对比对象为 NeMo-Aligner、DS-Chat、OpenRLHF 三个基线。典型读数：在 128 GPU 下，HybridFlow 在 7B 上达约 3.8×10⁴、70B 上约 0.82×10⁴ tokens/s，对应最高加速比从 7B 的 8.63× 攀升到 70B 的 17.98×。

**② 关键结论**：HybridFlow 在所有规模与 GPU 配置下均稳定领先，且模型越大、可调度资源越多，优势越显著——证明其 3D 混合引擎在大模型 RLHF 训练中具备优越的吞吐量与可扩展性。

**③ 论文作用**：作为方法部分的旗舰实验，与图8的端到端时延图共同支撑"灵活+高效"的核心主张，是全文系统级性能优势的关键实证依据。

### Figure 10 (p.11) ⭐深度解读
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]]
> [!quote] caption
> ReMax throughput. Numbers in parentheses are HybridFlow speedups compared with baselines 8 16 32 64 128 # of GPUs 0 1 2 3

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Architecture/Components**: The figure consists of three rows of grouped bar charts (Figures 9, 10, 11), each containing four subfigures corresponding to Llama model sizes: 7B, 13B, 34B, and 70B. Each subfigure plots **throughput (tokens/s)** on the y-axis against the **number of GPUs** (8/16/32/64/128, varying by model size) on the x-axis. Four systems are compared via colored bars: NeMo-Aligner (blue), DS-Chat (orange), OpenRLHF (red), and HybridFlow (green).

**Data Flow**: The rows correspond to three RLHF algorithms — PPO (top), ReMax (middle), and Safe-RLHF (bottom) — illustrating end-to-end RLHF training throughput scaling.

**Key Technical Takeaway**: HybridFlow consistently and substantially outperforms all baselines across every model size and algorithm, achieving **1.5×–19.8× speedups**, with the largest gains at 70B scale where competing systems fail to scale efficiently.

## Verbatim Captions

**Figure 9.** PPO throughput. Numbers in parentheses are HybridFlow speedups compared with baselines.

**Figure 10.** ReMax throughput. Numbers in parentheses are HybridFlow speedups compared with baselines

**Figure 11.** Safe-RLHF throughput. Numbers in the parentheses are HybridFlow speedups compared with the baselines

### Figure 11 (p.11) ⭐深度解读
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]]
> [!quote] caption
> Safe-RLHF throughput. Numbers in the parentheses are HybridFlow speedups compared with the baselines reward models. Each model is a Llama [73] model with sizes ranging from 7B to 70B. Safe-RLHF has an additional cost model whose architecture and size are the same as the re- ward model and ReMax eliminates the critic model. We use mixed precision for actor and critic training, i.e., BF16 for model 

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Architecture/Components**: The figure consists of three rows of grouped bar charts (Figures 9, 10, 11), each containing four subfigures corresponding to Llama model sizes: 7B, 13B, 34B, and 70B. Each subfigure plots **throughput (tokens/s)** on the y-axis against the **number of GPUs** (8/16/32/64/128, varying by model size) on the x-axis. Four systems are compared via colored bars: NeMo-Aligner (blue), DS-Chat (orange), OpenRLHF (red), and HybridFlow (green).

**Data Flow**: The rows correspond to three RLHF algorithms — PPO (top), ReMax (middle), and Safe-RLHF (bottom) — illustrating end-to-end RLHF training throughput scaling.

**Key Technical Takeaway**: HybridFlow consistently and substantially outperforms all baselines across every model size and algorithm, achieving **1.5×–19.8× speedups**, with the largest gains at 70B scale where competing systems fail to scale efficiently.

## Verbatim Captions

**Figure 9.** PPO throughput. Numbers in parentheses are HybridFlow speedups compared with baselines.

**Figure 10.** ReMax throughput. Numbers in parentheses are HybridFlow speedups compared with baselines

**Figure 11.** Safe-RLHF throughput. Numbers in the parentheses are HybridFlow speedups compared with the baselines

### Figure 12 (p.12) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig12.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p12.png]]*
> [!quote] caption
> Throughput of HybridFlow under different placements 32 64 96 128 # of GPUs

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图示内容**：三组子图（a）13B、（b）34B、（c）70B（部分截断），横轴为 GPU 数量（16–128），纵轴为吞吐量 tokens/s（量级 1e4），每个 GPU 配置下并排比较 Colocate（蓝）、Split（橙）、Standalone（红）、HybridFlow（绿）四种放置方案。

**关键结论**：随着 GPU 规模扩大，吞吐量单调上升，128 卡时 13B 场景接近 2.5–3×10⁴ tokens/s、34B 与 70B 约 1.2–1.5×10⁴ tokens/s；HybridFlow 在各模型规模与 GPU 配置下均达到与最优方案相当或更优的水平，尤其在中小规模/大模型场景下相对 Standalone 优势明显，说明其放置策略对模型与集群规模均具良好扩展性。

**论文作用**：作为 placement 消融实验，与 Fig.11（67B actor）共同支撑方法章节关于"flexible 3D hybrid engine"可适配多种模型与硬件拓扑的核心主张。

> 注：图中右下角可见 "Figure 13" 标注，与原题所述 Figure 12 编号存在偏差。

### Figure 13 (p.12) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig13.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p12.png]]*
> [!quote] caption
> Placement comparison under 13B actor and reference policy & 70B critic and reward model.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 13）**

1) **核心对象**：三幅柱状图，横轴为 GPU 数（16–128），纵轴为吞吐量（tokens/s，量级 10⁴），对比 Colocate、Split、Standalone、HybridFlow 四种模型放置策略，场景为 13B Actor/Reference 与 70B Critic/Reward 的非对称 RLHF 配置。左图覆盖最广 GPU 规模，中、右图聚焦特定区间。

2) **关键技术结论**：在小规模（≤32 GPU）下 Colocate 与 HybridFlow 接近，但随 GPU 增至 96–128，HybridFlow 凭借灵活放置策略实现最高吞吐，验证其在异构模型尺寸（13B+70B）下通过细粒度调度获得显著性能优势。

3) **论文作用**：支撑 HybridFlow "单控制器多角色 3D 并行 + 自动放置" 的核心主张，回应 RLHF 流水线中模型规模异构带来的调度挑战，为系统设计提供量化依据。

### Figure 14 (p.13) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig14.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p13.png]]*
> [!quote] caption
> Transition time between actor training and generation.

> [!tip] 技术解读（多模态）
> 【图文联合解读】## 图文联合解读

**核心数据**：图14比较了四种系统（OpenRLHF、DS-Chat、HybridFlow-V、HybridFlow）在四种模型规模（7B/13B/34B/70B）下，Actor训练→生成阶段的转换耗时。

- **7B（128 GPU）**：OpenRLHF约11s，HybridFlow约3.5s；
- **34B（128 GPU）**：OpenRLHF飙升至约50s，HybridFlow稳定在约5s；
- **70B（128 GPU）**：OpenRLHF/DS-Chat/HybridFlow-V分别约90s/28s/28s，HybridFlow仅约9s，差距达约10倍。

**关键论证**：HybridFlow在训练与生成阶段**复用同一并行策略**（同构并行），无需重组张量/流水/数据并行组；HybridFlow-V（生成用3D、训练用1D）则需重新分片，代价随模型与集群规模剧增。实验证明：正是这一设计抉择带来了近乎一个数量级的转换加速。

**论文作用**：支撑HybridFlow"统一并行抽象"的核心架构贡献，是其端到端RLHF训练效率优于现有系统（端到端加速1.53×–20.44×）的关键微结构证据。

### Figure 15 (p.13) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig15.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p13.png]]*
> [!quote] caption
> Time breakdown on different generation parallel sizes of the actor model on 16 GPUs. various model scales, which is the time to reshard model weights from training to generation, under the same settings in §8.2. OpenRLHF’s transition time includes weight syn- chronization time between two copies of the actor model on different devices. HybridFlow reduces the transition time by 55.2% (11.7s) on ave

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图15展示了7B与13B模型在不同生成并行配置（T_g张量并行/D_g数据并行，固定16 GPU）下，单步generation time与transition time的分解对比。

**数据要点：** 7B模型generation time从T_g=8时的~88s降至T_g=1时的~33s，但transition time从几乎可忽略升至~10s；13B模型同样在T_g=4时generation最优（~145s），T_g=1时反而回升至~225s。

**论证结论：** 生成并行策略存在明显权衡——降低张量并行度虽压缩生成耗时，却显著抬升权重reshard与同步开销；HybridFlow通过解耦与高效迁移，将transition time平均降低55.2%（11.7s），有效缓解该权衡。

**论文作用：** 该图为§8.2实验提供并行配置敏感性证据，支撑"3D-HybridEngine"的调度合理性——需动态选择生成并行度，使端到端RLHF迭代时间最小化。

### Figure 16 (p.13) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig16.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p13.png]]*
> [!quote] caption
> Runtime of device mapping algorithm. The model size and # of GPUs are simultaneously scaled.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 16 设备映射算法运行时间）：**

1）**核心对象与数据**：该图为对数纵轴柱状图，横轴为同时放大的"模型规模+GPU数"配置，依次为 (7B,8)、(7B,16)、(13B,24)、(13B,32)、(34B,48)、(34B,64)、(70B,96)、(70B,128)；运行时间从约 10s 单调增长至 ~10³s（近千秒），呈近似指数级上升趋势。

2）**关键结论**：HybridFlow 的设备映射算法在大模型+大集群下仍可在分钟级完成规划（最大 ~1500s），开销可控，避免成为流水线瓶颈。

3）**链路作用**：与 Figure 14 互证——前者证明训练-生成切换极短，本图证明前期规划代价可接受，共同支撑"HybridFlow 单控制器 3D 混合调度低开销、可扩展至 70B/128GPU"的方法论结论。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.9) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-tab02.png]]
> [!quote] caption
> Transition overhead between training & generation

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 解读：**

该表量化训练→生成切换阶段的**通信量**(Comm.Vol)、**峰值显存**(Peak Mem.)、**冗余**(Redundancy)，对比DS-Chat、HybridFlow-V、HybridFlow三者，以模型大小M、分片数t_p/t_pd/t_g及参数ρ_g表达。核心结论：HybridFlow**冗余为0**（优于DS-Chat的M/t_pd与HybridFlow-V的M/t_p），**峰值显存降至**M/(t_g ρ_g)（其余两者均为完整M），通信量分子亦最小。该表与Figure 2编程模型共同支撑3D-HybridEngine设计——证明HybridFlow在RLHF训练-生成高频交替场景下显著降低显存与通信开销，是论文论证框架高效性的核心理论证据。

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.7 `critic_metrics = critic.update_critic(batch, loss_func=algo_type)`
- p.7 `pretrain_loss = actor.compute_loss(pretrain_batch)`
- p.7 `batch[“pretrain_loss”] = pretrain_loss`
- p.7 `actor_metrics = actor.update_actor(batch, loss_func=algo_type)`
- p.8 `𝑁𝑎=𝑝×𝑡×𝑑=𝑝𝑔×𝑡𝑔×𝑑𝑔×𝑑such that 𝑑𝑔=`

## 相关论文

- [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] — AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning
- [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] — Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEMENT LEARNING
- [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] — DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
- [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] — Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning

## 技术点深读（DEEP）

![[deep/hybridflow-a-flexible-and-efficient-rlhf-framework]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/hybridflow-a-flexible-and-efficient-rlhf-framework.txt`（109820 字符）供引用检索。