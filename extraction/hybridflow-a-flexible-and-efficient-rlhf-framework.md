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
> 【图文联合解读】该图展示3种RLHF算法（PPO/Safe-RLHF/ReMax）的三阶段数据流：①Generation（Actor Gen，ReMax含2个）；②Preparation（Ref/RM/Critic/Cost模型的Forward）；③Training（Actor Training，PPO与Safe-RLHF另有Critic Training，Safe-RLHF还引入L_ptx损失与Actor Fwd）。各算法模型组合与拓扑各异——PPO需4模型，Safe-RLHF额外引入Cost模型，ReMax仅3模型且无critic。

**论证结论**：HybridFlow以统一的Stage抽象即可灵活承载不同模型数量与执行顺序，验证其作为通用RLHF框架的表达力与可扩展性。

**论文作用**：作为方法论开篇的"能力示例"，证明单一系统可统一支持多样RLHF流程，为后续灵活的Actor/Colocation调度与高效分布式实现奠定设计动机。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig02.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p03.png]]*
> [!quote] caption
> Programming model used in RLHF systems. (a)

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图(b)展示HybridFlow混合编程模型：顶层单控制器协调Actor、Critic、Reward、Reference四类模型；每个模型内部采用多控制器实现（图中以`gen(prompts)`、`comp_values(res)`、`comp_reward(res)`三段伪代码为例，共享`all_gather_weights()`同步与`model()`调用），灰色节点表示当前未激活。

原文借此论证两个关键技术结论：**灵活**——解耦数据与计算依赖、无缝集成任意LLM系统；**高效**——阶段转换零冗余（避免权重重复广播）、支持不同模型放置策略。

在论文整体链路中，该图是"混合控制器"设计的核心证据，与(a)纯多控制器范式形成对照，支撑后续吞吐量、显存占用与分布式扩展性实验的设计假设，是方法论章节的奠基性技术图。

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
> 【图文联合解读】**图文联合解读：**

图6展示一份**单一Python控制脚本**，按"生成响应→准备经验→更新actor/critic"三阶段编排，涵盖PPO/ReMax/Safe-RLHF三种RLHF算法；其中**蓝色虚框**标注ReMax特有行（`do_sample=False`、蓝叉标记`critic.compute_values`在ReMax中可省），**红色虚框**标注Safe-RLHF特有行（`cost.compute_cost`与`pretrain_loss`）。

原文借此论证**HybridFlow在不改算法代码的前提下，仅增删若干行即可切换不同RLHF算法**，体现其编程模型的灵活性。该图作为方法部分的关键示例，与第3节"单控制器抽象+分布式执行解耦"的设计形成呼应，为后文性能与易用性实验提供代码级证据。

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
> 【图文联合解读】**图文联合解读：**

图9以四个子图(a–d)对比7B/13B/34B/70B模型在8–128 GPU上的PPO吞吐量(tokens/s)，四种系统（NeMo-Aligner、DS-Chat、OpenRLHF、HybridFlow）同列对照。绿色HybridFlow条形在各规模下均最高：7B/128 GPU达约3.7×10⁴ tok/s，70B/128 GPU达约0.8×10⁴ tok/s；加速比随模型增大而扩大（7B: 1.68–8.63×，70B: 5.17–17.98×，34B峰值达20.57×）。

论文借此定量论证：HybridFlow通过灵活组合3D混合并行与RLHF阶段解耦编排，在端到端训练吞吐上系统性优于现有框架。该图是全文"高效RLHF"主张的核心实验支撑，证明其架构优势随模型与集群规模同步放大。

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
> 【图文联合解读】## 图文联合解读

**1) 核心对象与数据**：图(a)为13B模型下四种放置策略（Colocate蓝、Split橙、Standalone红、HybridFlow绿）在16/24/32/64/96/128 GPU下的吞吐量（tokens/s，单位1e4）。小规模时Colocate≈HybridFlow≈0.7–1.0e4，Standalone仅0.4–0.7e4；128 GPU时四者收敛至约2.6e4。

**2) 关键技术结论**：HybridFlow在不同GPU规模下吞吐均≥Standalone，尤其在16–64 GPU区间显著领先（最大提升约30–40%），且在小规模时与Colocate持平；说明其灵活映射并不以吞吐为代价，突破了"非Colocate则慢"的固有代价。

**3) 在论文中的作用**：作为可扩展性实验的核心证据，证明HybridFlow的placement解耦设计兼具灵活性与高效性，为"统一多策略RLHF训练"主张提供关键性能背书。

### Figure 13 (p.12) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig13.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p12.png]]*
> [!quote] caption
> Placement comparison under 13B actor and reference policy & 70B critic and reward model.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**核心对象与数据**：图13展示13B actor/ref + 70B critic/reward配置下，Colocate、Split、Standalone、HybridFlow四种放置策略在32/64/96/128块GPU上的吞吐量（tokens/s，量级1e4）。32 GPU时HybridFlow约5500，与Colocate持平但远高于Split(~2000)与Standalone(~2500)；64 GPU时HybridFlow升至约8500，居首；96–128 GPU时四种策略差距收窄至约9000–12000，HybridFlow仍领先约10%。

**关键结论**：异构模型规模下，固定放置策略（Colocate/Split/Standalone）顾此失彼，HybridFlow的灵活放置在中小规模GPU集群上提升最显著（最高近2×），验证其自适应布局优势。

**论文作用**：作为placement消融实验，与图12（67B actor场景）共同支撑方法章节关于"flexible 3D hybrid engine"可扩展性的主张。

### Figure 14 (p.13) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig14.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p13.png]]*
> [!quote] caption
> Transition time between actor training and generation.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（图14）：**

图14以双子图形式，在7B(T_g=2)与13B(T_g=4)两种配置下，对比四种框架在不同GPU规模下的"actor训练↔生成"模式切换耗时。

- **7B子图**：OpenRLHF从8卡约4s线性增至128卡约11s；DS-Chat约3-5s；HybridFlow-V约3-4s；HybridFlow始终稳定在2.5-3.5s（最低）。
- **13B子图**：差距进一步放大——OpenRLHF从10s升至17s，DS-Chat从5s升至12s，而HybridFlow几乎保持在3-4s，几乎不随GPU数增长。

**论证结论**：HybridFlow通过将训练与生成统一在同一调度器内（而非控制器分离式架构），将切换开销压到最低且具备良好扩展性。这正是其端到端RLHF训练吞吐量优于同类框架的关键工程支撑。

### Figure 15 (p.13) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig15.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p13.png]]*
> [!quote] caption
> Time breakdown on different generation parallel sizes of the actor model on 16 GPUs. various model scales, which is the time to reshard model weights from training to generation, under the same settings in §8.2. OpenRLHF’s transition time includes weight syn- chronization time between two copies of the actor model on different devices. HybridFlow reduces the transition time by 55.2% (11.7s) on ave

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示了 **7B 与 13B actor 模型在 16 GPU 上**于四种生成并行配置（T_g/D_g = 8/1、4/2、2/4、1/8）下的时间分解，包含 **generation time（蓝色）** 与 **transition time（橙色）** 两部分。量化来看：7B 生成时间随 T_g 减小从约 85s 降至 30s 左右；13B 则在 T_g=8/D_g=1 与 T_g=1/D_g=8 时均出现约 220s 的高值，呈现非单调 U 形。transition time 占比相对较小（7B 约 3–5s，13B 约 5–10s），但不可忽略。

原文借此论证：HybridFlow 通过解耦训练/生成资源并采用统一调度，将 actor 模型的 **reshard 过渡时间平均减少 55.2%（11.7s）**，凸显其在 RLHF 流水线中显著降低模式切换开销的关键优势。该图在实验链路中服务于"RLHF 训练—生成频繁交替场景下的端到端效率"这一核心主张，为 HybridFlow 的灵活并行设计提供了直接量化支撑。

### Figure 16 (p.13) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig16.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p13.png]]*
> [!quote] caption
> Runtime of device mapping algorithm. The model size and # of GPUs are simultaneously scaled.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图以对数纵轴柱状图展示8组（模型规模, GPU数）配置下的设备映射算法耗时：(7B,8)≈10s、(7B,16)≈30s、(13B,24)≈65s、(13B,32)≈110s、(34B,48)≈220s、(34B,64)≈370s、(70B,96)≈800s、(70B,128)≈1400s。

原文借此论证：当模型与GPU同步放大时，Auto Device Mapping的求解时间呈近似指数增长，但在最大规模70B/128 GPU下仍控制在约25分钟以内，处于工程可接受范围，证明该算法在千亿级RLHF训练中具备可扩展性，避免了映射本身成为系统瓶颈，从而支撑HybridFlow整体"灵活高效"的实验结论。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.9) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-tab02.png]]
> [!quote] caption
> Transition overhead between training & generation

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 联合解读**

**1) 核心对象与数据：** 表2对比三种方案在训练⇄生成模式切换时的三项开销。其中 *Comm. Vol.*（通信量）：DS-Chat 为 $\frac{tpd-1}{tpd}M$，HybridFlow-V 为 $\frac{tp-1}{tp}M$，HybridFlow 为 $\frac{tp-t_g p_g}{t_g p_g tp}M$；*Peak Mem.*（峰值显存）：DS-Chat、HybridFlow-V 均为 $M$，HybridFlow 降至 $\frac{1}{t_g p_g}M$；*Redundancy*（参数冗余）：DS-Chat、HybridFlow-V 分别有 $\frac{1}{tpd}M$、$\frac{1}{tp}M$ 的冗余，HybridFlow 为 0。

**2) 关键结论：** HybridFlow 通过同一组显存复用 actor/critic/ref/reward 四模型并使训练/生成各采用独立并行配置 $(tp)$ 与 $(t_g p_g)$，在切换时实现了 **零参数冗余**、通信量近似线性降低、显存峰值缩减 $t_g p_g$ 倍，相对 DS-Chat 与 HybridFlow-V 均显著更优。

**3) 在论文中的作用：** 该表量化支撑了 HybridFlow 混合编程模型（图2）相对于纯多控制器方案的核心收益——消除模式切换开销，是其端到端高吞吐实验结论的理论依据。

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