---
paper_num: "31"
title: "Let It Flow: Agentic Crafting on Rock and Roll"
authors: "Building the ROME Model within an Open Agentic Learning Ecosystem ROCK & ROLL & IFLOW & DT Joint Team  ROCK  ROLL  iFlow CLI  Terminal Bench Pro  iFlow-ROME"
date: "2026/1/17"
arxiv: "https://arxiv.org/abs/2512.24873"
pdf: "papers/let-it-flow-agentic-crafting-on-rock-and-roll.pdf"
slug: "let-it-flow-agentic-crafting-on-rock-and-roll"
tags: []
---

# Let It Flow: Agentic Crafting on Rock and Roll

> [!abstract] 摘要（原文）
> 1\. 🏗️ 本文介绍了Agentic Learning Ecosystem (ALE)，这是一个为Agent LLM端到端生产管线优化的基础架构，由RL训练框架ROLL、环境执行引擎ROCK和Agent框架iFlow CLI组成。 2. 📚 基于ALE，研究团队构建了开源Agent模型ROME，该模型通过精心策划的数据组成协议和端到端训练管线，并在超过一百万条轨迹上进行训练，特别提出新颖的IPA策略优化算法以提高训练稳定性。 3. 🚀 ROME在主流Agentic基准测试中取得了显著成果，包括Terminal-Bench 2.0和SWE-bench Verified，性能超越同等规模模型并接近大型模型，且已成功部署于生产环境，证明了ALE的实际有效性。

## 元信息
- **发表日期**: 2026/1/17
- **作者**: Building the ROME Model within an Open Agentic Learning Ecosystem ROCK & ROLL & IFLOW & DT Joint Team  ROCK  ROLL  iFlow CLI  Terminal Bench Pro  iFlow-ROME
- **arXiv**: https://arxiv.org/abs/2512.24873
- **本地 PDF**: `papers/let-it-flow-agentic-crafting-on-rock-and-roll.pdf`
- **页数**: 41

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig01.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p01.png]]*
> [!quote] caption
> Overview of the Agentic Learning Ecosystem (ALE) and ROME Performance. 1[cs.AI] 12 Mar 2026

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示ALE三件套（ROCK沙盒+iFlow智能体+ROLL训练）通过ROME实现"任务→动作→执行→反馈→学习"闭环。Terminal-Bench 2.0上ROME(30B-A3B)24.72分、SWE-bench Verified 57.40分，均超同体量Qwen3(13.48/46.33)；训练曲线准确率由41.60%升至89.83%（相对增益+113.16%）。此为开篇门面图，确立"ROME闭环RL训练范式"核心叙事，证明30B-A3B经iFlow闭环训练即可逼近480B大模型水平(26.97/65.20)。

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig02.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p04.png]]*
> [!quote] caption
> The overview of agentic RL ecosystem (a) and its training pipeline (b). technical stack, ALE is also a call to reframe the community’s priorities. In complex agentic settings, the central challenge is no longer merely data scale or curation quality, but the co-design of training infrastructure, executable environments, and evaluation protocols. We hope this work catalyzes collaborative efforts tow

> [!tip] 技术解读（多模态）
> 【图文联合解读】图(b)展示Agentic RL训练流水线两阶段闭环：Rollout阶段由Agentic LLM向环境输出Action（Tokens），回收Observation（State）；积累的Trajectory Data送入Training阶段完成Weight Update，再经Weight Synchronization回传LLM，形成自循环。图(a)展示ALE生态（含RK Sandbox、CLI、Agent Framework、LLM、Proxy Service、Response Queue、Execution Engine等模块），为流水线提供可执行环境与工程支撑。原文据此论证：智能体RL的核心挑战已从单纯的数据规模与质量，转向训练基础设施、可执行环境与评估协议的协同设计——ALE即作为该一体化技术栈，催化社区协作。

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig03.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p05.png]]*
> [!quote] caption
> ROLL Architecture. (a) ROLL pipelines LLM generation, environment interaction, and reward phases at trajectory-level granularity. Training is also decoupled via a sample buffer using an asyn- chronous ratio to manage staleness. (b) ROLL multiplexes a dynamic GPU pool by shrinking rollout resources for bursty training and expanding them back during demand peaks. coordinates heterogeneous workers an

> [!tip] 技术解读（多模态）
> 【图文联合解读】图3展示ROLL核心架构。

**(a)细粒度Rollout与异步训练**：上侧Rollout系统含Queue Scheduler→LLM Proxy→Environment三段流水线，下侧Training System以容量4条轨迹的Sample Buffer解耦Train Worker；Async Control Logic经Suspend/Update/Resume调度Rollout、KV Cache Recompute与Train step。LLM Engine时序显示4块GPU并行跑traj1–8，GPU D嵌入"Training i"，余卡于Vacant窗口待命，验证轨迹级流水线重叠。

**(b)Train-Rollout多路复用**：在同Async工作流上叠加shrink/expand机制——训练突发期GPU D让位运行Training i，原负责的traj5经Vacant触发KV Cache重算；高峰期再扩展恢复，证实动态GPU池可弹性伸缩。

论文借此论证：轨迹级异步流水线+弹性GPU复用是ROLL支撑大规模agentic RL高吞吐训练的系统基石，为后文实验规模扩展提供架构基础。

### Figure 4 (p.6) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig04.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p06.png]]*
> [!quote] caption
> ROCK System Architecture.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示ROCK系统架构：右侧聚焦两大核心技能——Skill 4"海量调度"（含10,000+并发Sandbox，节点标注Running/Succeed/Failed/Pending四态，由Docker鲸鱼统一编排）与Skill 5"鲁棒容错隔离"（展示鲸鱼容器RUNNING/CRASHED状态自动恢复）；左侧揭示Worker–Sandbox–Env Hub执行栈，并通过Agent Bridging模块实现Model Server与RL Frame间经GEM传递Action/Observation的闭环交互。

**技术论断：** 该图直观论证ROCK具备万级并发沙箱编排与节点级故障自愈两大能力，是智能体强化学习训练得以规模化落地的工程基石。

**论文作用：** 作为Figure 4居于系统设计章节，为后续Table 4（大模型工具调用基准）等实验提供基础设施可行性背书，贯穿"craft on rock and roll"的核心叙事。

### Figure 5 (p.8) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig05.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p08.png]]*
> [!quote] caption
> The overview of iFlow CLI architecture and execution. these requests already contain the complete historical context, fully orchestrated by the iFlow CLI. The proxy then forwards these requests to the appropriate inference service — be it ROLL inference workers during training or an external API (e.g., GPT, Gemini) during deployment. The native mode achieves a clean separation. ROLL is simplified 

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示iFlow CLI四大模块：用户界面（CLI Client/IDE Plugins/Web/SDK 4项）、Main Agent（含Compress/Reminder/Detection/Env. Mgmt 4种运行时扩展）、Tool Suits（File/MCP/System/Task/Network/Other 6类）、Context Management（Compression/Retrieval/Enhancement/Isolation/Persistent Memory 5项），通过Tool Call与Context Interaction双向联动，并叠加Hooks、Skill-Based Workflows、多级记忆三项增强能力。原文以此论证iFlow CLI可独立编排完整历史上下文，由代理统一转发至ROLL推理worker（训练）或外部API（部署），实现原生模式与ROLL的清晰解耦，简化训练-部署全链路。

### Figure 6 (p.10) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig06.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p10.png]]*
> [!quote] caption
> Overview of data sources and composition pipelines for training agentic models, spanning code centric basic data and agentic data. 3

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

**1) 核心对象与结构**：图分左右两区。左侧 *Code Centric Data*——从 High-Quality Repo&PR 爬取 Repo/Issue/Test/Code Patch/Discussion，加工为 Localization、Repair、Unit Test Generation、Multi-turn Interaction、Code Reasoning 五类任务感知数据。右侧 *Agentic Data* 四个子模块：①Programming-Centric（Explore→Build→Review→Behavior 四 Agent 协作，产出 Instance 与 Trajectory）；②General Tool Use（Dialogue&API、Web 交互）；③Safety（Risk Knowledge→Inject Attack→Tiered Validation→Red Team）；④Data Filtering（Heuristic Filter→LLM-based Judge→Execution Simulator→Expert Inspection 四级流水线）。

**2) 关键技术结论**：训练数据由代码基本数据与 agentic 数据双轨合成，多 Agent 协作 + 四级过滤保障数据质量与安全，是 ROME 性能优异的底层支撑。

**3) 论文作用**：该图为 ROME 提供完整数据蓝图，支撑 Table 5/6 中 ROME 在多数基准上可比肩/超越更强开源 agentic 模型的实验结论，构成"数据→训练→评测"链路的关键上游环节。

### Figure 7 (p.16) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig07.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p16.png]]*
> [!quote] caption
> Overview of ROME’s Training Pipeline. incidents. Finally, we generated corresponding golden trajectories devoid of general-security issues for subsequent post-training (e.g., SFT and RL). Our overarching objective was to instill robust security awareness such that, when confronted with tasks containing latent security pitfalls, the agent reliably selected safe action paths and proactively avoided 

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 7：ROME 训练管线）**

图示 ROME 三阶段训练架构：**Stage 1 连续预训练**共 800B tokens——500B 语料（代码+推理/工具调用数据）→300B 轨迹（文件系统、网页购物等）建立"原子能力→智能体求解器"，统一用 Next-Token Prediction 目标；**Stage 2 SFT** 按 70%智能体 / 15%推理 / 15%通用指令数据配比，经启发式过滤（冗余工具调用、过度思考、假阳性）+ LLM-as-Judge 排序，再以 Error/Context Masking 对失败/无关 token 零损失，完成"自适应数据回访"；**Stage 3** 基于 Chunked MDP（sᵢ,aᵢ,rτᵢ 序列）的 IPA 策略优化，融合 TOPR-TIS off-policy 增强、token 级重要性采样与动态轨迹过滤。原文借此论证"先预训练打基础→SFT 注入安全演示→RL 强化安全决策"的链式后训练路径，是全文方法论的骨架图。

### Figure 8 (p.20) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig08.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p20.png]]*
> [!quote] caption
> Overview of the Proposed Interaction-Perceptive Agentic Policy Optimization (IPA) training pipeline. sample efficiency(§3.2.4.4). An overview of our framework, including its key components and data flow, is depicted in Figure 8.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

IPA流水线核心：专家轨迹T*切分为t个chunk（c*₁…c*ₜ），每chunk含状态sᵢ及token序列（τᵢ、τₜ₁ᵢ…τₜₕᵢ、τ⁺ᵢ、τ⁻ᵢ）。经重采样生成两条rollout T⁽¹⁾、T⁽²⁾：早期chunk（绿框）走模仿学习，后续chunk（蓝框）走策略优化，分别输出折扣chunk级回报R(T⁽¹⁾)、R(T⁽²⁾)（γ折扣）。两关键机制：①chunk级重要性采样 ρ_cᵢ=(∏ π_θ^megatron/π_θold^megatron)^(1/|cₜ|) 修正策略偏移；②推理–训练失配掩码 m_cᵢ，当 SGLang 与 megatron 几何似然比 >H 即屏蔽该chunk。

**论证结论：**支撑§3.2.4.4样本效率——通过chunk级重采样+IS+掩码复用专家片段，避免冷启动探索。

**链路作用：**IPA是RL微调阶段的核心算法，与SFT互补，构成两阶段训练pipeline。

### Figure 9 (p.22) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig09.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p22.png]]*
> [!quote] caption
> Comparison of importance sampling strategies across token-level, chunk-level, and sentence- level granularities, where chunk-level aligns with the natural granularity of interactions.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示横向三行对比同一智能体轨迹上三种重要性采样粒度。顶行（token级）将众多τ_token打包入chunk c₂…cₜ，两处"Interaction"箭头落入chunk内部，与chunk边界错位；中行（chunk级，橙色高亮并标✓）每条Interaction箭头恰好落在chunk边界上，τ_{2h}/r₂ 与 s_t/τ_{t1} 等位置严格对齐；底行（sentence级）一个粗粒度句子横跨多条Interaction，混叠多个交互事件。结构上量化呈现了"chunk数↔token数↔interaction次数"的三种对应关系。

原文据此论证：**chunk级粒度与环境中agentic交互的天然边界完全对齐**，既避免token级的子chunk内切分失配，又避免sentence级的跨交互混叠，因而是重要性采样的最优选择。

在论文方法链路中，该图为后续"采样策略—交互步对齐—策略梯度更新"模块提供粒度选择的实证依据，是连接环境交互建模与训练目标设计的关键前提。

### Figure 10 (p.23) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig10.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p23.png]]*
> [!quote] caption
> Comparison of Chunk-Level Optimization and baseline on a mini-set of the training data. Left:

> [!tip] 技术解读（多模态）
> 【图文联合解读】图10以三联子图对比Chunk-Level Optimization与baseline。左图（对数纵轴10⁻²–10²）显示Chunk梯度范数稳定于~10⁻²，baseline在步骤35附近异常飙至~10²并剧烈震荡；中图训练成功率由51%升至峰值70%（稳定于65–68%），baseline仅~60–63%；右图测试成功率由48%升至峰值57.5%，baseline仅~52%。论文据此论证：分块级优化凭借稳定梯度与有效信用分配，在训练测试两端均显著优于baseline并具备泛化性，为整体"流式智能体"优化框架的稳健性与有效性提供关键实验支撑。

### Figure 11 (p.24) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig11.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p24.png]]*
> [!quote] caption
> Illustration of the Chunk-Level Initialized Resampling Strategy (Sequential Rollback). Left: In challenging tasks, sampling high-quality trajectories from the beginning is difficult, severely limiting policy learning efficiency. Right: Sequential Rollback sampling strategy initiates rollouts from critical chunks, dramatically reducing the exploration burden and enabling the policy to rapidly acqui

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构：**
左图为"Sampling From Beginning"示意。一条轨迹被切分为多个 chunk（s₁→c₁→r₁→⋯→s*ₜ→c*ₜ→r*ₜ→⋯→s*ₗ），星号 s* 标识"关键岔路口"（Crucial Fork）状态。在每个 chunk 上并行展开 III 次 rollout（标注 ⁽ⁱ⁾、⁽ⁱⁱ⁾、⁽ⁱⁱⁱ⁾），结果全部以 ❌ 失败告终（"All Failures"、"Uninformative Rollouts"），右端仅露出"Expert-Like"轨迹示意，暗示需回溯到 s*ₗ 关键节点才可获得专家级轨迹。

**2) 关键技术结论：**
原文论证：从头开始的 rollout 难以抵达关键岔路口 s*ₗ，导致大量无效探索，严重限制策略学习效率；而 Sequential Rollback 从关键 chunk 初始化，可大幅降低探索负担，使模型沿关键节点逐步回溯，实现 chunk 级课程学习。

**3) 在论文中的作用：**
该图作为动机图，揭示了传统"从初始状态采样"在长程困难任务中的低效性，为后文提出的 Chunk-Level Initialized Resampling（Sequential Rollback）提供必要性依据，是 AgentFlow 训练管线中关键的数据采样加速机制之一。

### Figure 12 (p.25) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig12.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p25.png]]*
> [!quote] caption
> Performance of Sequential Rollback and baseline (naive sampling) on a challenging training task. Left: Average success rate during training, which reflects the percentage of positive signals in training batch. Sequential Rollback obviously brings more valuable rollouts compared to baseline (all failures). The drop of success rate indicates that the model has rolled back across a crucial chunk to t

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图含三子图，对比Seq-Rollback（绿）与Baseline（灰）约175步训练。左图"训练时平均成功率"：绿线在10%–100%剧烈波动、均值约60–80%，两橙色圈标记骤降点（≈20%和≈40%）；灰线恒为0%。中图"Expert Chunks数量"：绿线由~45递减至~20，标注"Rollback"箭头；灰线恒为0%。

原文用此论证：顺序回退机制能产出大量有价值正样本，而朴素采样基线完全失败；成功率骤降恰反映模型跨关键chunk回退重试的机制行为。作为论文核心贡献Sequential Rollback在难训练任务上的关键经验证据，支撑回退策略的必要性、有效性与可解释性。

### Figure 13 (p.26) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig13.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p26.png]]*
> [!quote] caption
> Comparison of IPA with & without Chunk-Level Initialized Resampling (Parallelized Initial- ization) on a mini-set of the training data. Left: Average success rate on training tasks. The gap between curves in the early stage of training shows that the Chunk-Level Initialized Resampling brings much more diverse reward signals in training batches. Middle: Minimum success rate across train-tasks with 

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图13对比"块级初始化重采样"（Parallelized Initialization, 橙线）与无该机制（灰线）下的IPA训练表现。可见右侧测试时成功率曲线：训练100步时橙线达约90%，灰线仅约52%，差距近40个百分点；左侧训练任务平均成功率在早期阶段橙线也明显领先。原文借此论证两点关键技术结论：(1) 块级重采样在训练初期即提供更多样化的奖励信号；(2) 使模型能以课程式方式攻克最难任务（Middle面板最低成功率亦显著提升）。在论文整体链路中，该图作为消融证据支撑"Parallelized Initialization"是IPA方法中提升rollout价值与最终泛化性能的关键组件。

### Figure 14 (p.27) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig14.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p27.png]]*
> [!quote] caption
> Benchmark characterization and cross-benchmark comparison of Terminal Bench Pro against other benchmarks.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（≤220字）**

该图为Figure 14的部分视图，展示Terminal Bench Pro的基准特征与跨基准对比。

**(a) 环形图**：呈现Terminal Bench Pro在8个任务类别（Scientific Computing、Debugging、Games、System Administration、Security、Machine Learning、Data Processing、Software Engineering）上的分布，各扇区面积接近，表明**类目分布均衡**（每类约12.5%）。

**(c) 热力图**：三列对比Terminal Bench 1.0/2.0/Pro Public在Security、SE、System Admin、Debugging四类上的pass@1标准差。Pro Public在所有四类均最低（如SE: 0.02 vs 1.0的0.09；Debugging: 0.04 vs 2.0的0.18），验证其**评估方差更低、更稳定可靠**。

**论证结论**：通过"均衡覆盖 + 低方差"双重证据，支撑Terminal Bench Pro作为**更严谨基准**的主张——避免类别偏斜与结果波动，使模型能力评估更具区分力。

**链路作用**：作为§3.3.2小节核心可视化，为后文实验（如评测新模型时统一在该基准上的可比性）提供方法论基础。

### Figure 15 (p.28) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig15.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p28.png]]*
> [!quote] caption
> Performance-parameter trade-offs in agentic tasks. Scores represent averages on general agentic and code agent benchmarks. Models with known parameters are shown as circles, while proprietary models with unknown parameters are depicted as diamonds (right side). Left: Total parameters versus overall performance. Right: Activated parameters versus overall performance. 2https://github.com/alibaba/ter

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 15 · 激活参数量 vs 准确率）：**

图示为各模型在 agentic 基准上的平均准确率（纵轴 10–40%）与激活参数量（横轴 0–40B+）的散点对比。核心发现：**iFlow-ROME（30B-A3B）在仅 ~3B 激活参数下达约 30% 准确率**，逼近 GLM-4.6（~28B 激活、~36%）、Kimi-K2-0905（~30B、~32%）等大模型，并显著优于同激活量级的 GPT-OSS-120B（~25%）与 Qwen3-Coder 30B-A3B（~21%）；右上方为参数未知的闭源模型（Claude-Haiku-4.5、GPT-5 Mini 等）。图中斜向"Performance-Parameter Trade-off"箭头印证：在极低激活成本下，iFlow-ROME 凭借路由机制实现了极具竞争力的 agent 性能，凸显 MoE 架构的效率优势，为论文"小激活、大能力"的核心主张提供量化支撑。

### Figure 16 (p.34) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig16.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p34.png]]*
> [!quote] caption
> Pairwise win-rate matrix (%) on the 100-task real-world benchmark under 30-expert blinded majority voting. Each cell reports the percentage of tasks where the row model is judged better than the col- umn model; higher values (green) indicate stronger performance.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图16解读**

**1) 核心对象与数据**：5×5 配对胜率热力图（去除平局），基于 100 个真实任务、30 位专家盲评多数投票，行模型相对列模型的胜率（绿高红低）。ROME 对 Qwen3-Coder 30B 与 Devstral Small 2 取得 **100%** 全胜；对 Qwen3-Coder Plus 与 GLM-4.6 达 **58.8%**；GLM-4.6 对 Plus 仅 44.4%；30B 对 Small 2 为 61.1%。ROME 在各列向上颜色均最绿。

**2) 关键论证结论**：ROME 不仅碾压开源小模型（30B、Small 2），对当前最强商用编码模型（Plus、GLM-4.6）仍保持多数头对头胜率，证明其在真实复杂任务上的全面领先。

**3) 论文整体作用**：作为主实验人评证据，与自动化榜单互补，支撑"RFlow/ROME 优于 SOTA 商用与开源 agent"这一核心论点，是论文方法有效性的关键验证环节。

### Figure 17 (p.36) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig17.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p36.png]]*
> [!quote] caption
> Case study 1 screenshot examples: Sleep Management System Generation. 36

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图17图文联合解读：**

该图呈5×3网格，对比5个AI系统生成"睡眠管理系统"App的截图，各3张：

- **ROME (a-c)**：粉紫渐变欢迎页（含环形进度）、深色数据分析页（指标卡 7h30m/82%/23:15/12 + 折线/柱状图）、带头像设置页，UI最完整美观。
- **Qwen3-Coder-Plus (d-f)**：周报、睡眠记录（进度条）、数据分析柱状图，结构简单。
- **GLM-4.6 (g-i)**：折线+环形图仪表盘，但三张截图几乎雷同，多样性差。
- **Qwen3-coder-30B (j-l)**：饼图+数据表（100%/22:45/82%/62%），信息密度低。
- **Devstral-Small-2 (m-o)**：任务清单、记录页（42h30m/7h15m/85%/12）、图表页，导航不连贯。

**原文论证结论**：ROME 能产出多页面、含导航与丰富可视化、视觉风格统一的完整Web应用；基线模型普遍存在页面单调、组件缺失或生成重复等问题。

**作用**：作为Case study 1的定性证据，与定量评测互补，共同支撑ROME在端到端全栈Web生成上的优越性。

### Figure 18 (p.37) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig18.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p37.png]]*
> [!quote] caption
> Case study 2 screenshot examples: Solar System Modeling. 37

> [!tip] 技术解读（多模态）
> 【图文联合解读】图18以5×2网格对比ROME、Qwen3-Coder-Plus、GLM-4.6、Qwen3-coder-30B、Devstral-Small-2五款代理在"太阳系建模"任务第2、3次截图：ROME呈现完整恒星＋多颗行星分布在同心轨道环上，UI控件齐全；Qwen3-Plus行星排成水平直线，几何失真；GLM-4.6背景转为蓝色渐变且太阳退化为黄色矩形，未完成渲染；Qwen3-30B行星稀少；Devstral-Small-2两屏几乎全黑，仅留椭圆描边。图中用以论证ROME在多轮迭代式可视化生成中，物体完备性、布局合理性与稳定性显著优于开源基线模型，支撑论文"agentic crafting"框架能显著提升大模型创意编码与复杂动态场景构建能力这一核心结论。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.29) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-tab01.png]]
> [!quote] caption
> Performance on Terminal-Based Benchmarks (Normal Models).

> [!tip] 表格解读（多模态）
> 【图文联合解读】表1对比ROME（MoE，30B总参/3B激活）与6个主流模型在6个终端类基准（Terminal-Bench 1.0/2.0、SWE-Bench Verified/Multilingual、Terminal-Bench-Pro Public/Private）的得分。ROME平均分37.60，仅以0.39分之差低于GPT-5 Mini（37.99），却激活参数远少于后者；在Terminal-Bench 1.0（41.50）、Terminal-Bench-Pro-Public（40.50）、SWE-Bench Multilingual（40.00）等项均领先同/近量级对手。原文借此论证：经ALE训练的ROME以极低激活参数量逼近超大闭源模型的agentic编码能力，是论文"以高效架构实现agentic能力"主张的关键实证支撑，配合Figure 1共同构成ROME性能展示的核心。

### Table 2 (p.29) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-tab02.png]]
> [!quote] caption
> Performance on Terminal-Based Benchmarks (Large Models).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 联合解读**

**核心对象与数据**：表2对比ROME（仅3B激活参数的MoE）与Qwen3-Coder Plus/480B-A35B、DeepSeek V3.1(671B/37B激活)、GLM-4.6(355B/32B)、Kimi-K2(1043B/32B)、Claude-Haiku-4在6个终端与SWE基准（Terminal-Bench 1.0/2.0、SWE-Bench Verified/Multilingual、Terminal-Bench-Pro Public/Private）及平均分上的成绩。

**关键结论**：ROME以3B激活取得37.60平均分，逼近40B级激活的Qwen3-Plus(43.36)、GLM-4.6(42.45)、Kimi-K2(42.19)；在Terminal-Bench 1.0上以41.50反超GLM-4.6(41.25)与Qwen3-480B(37.92)。Claude-Haiku-4以48.84居首，但ROME以小近10倍激活参数即进入第一梯队，体现极高参数效率。

**论文链路作用**：作为Figure 2所示"agentic RL生态—训练—评估闭环"中的终端代理能力评测节点，为ROME在代码/终端代理场景下"小而强"的论点提供量化佐证。

### Table 3 (p.30) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-tab03.png]]
> [!quote] caption
> Performance on Tool-Use Benchmarks (Normal Models).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 联合解读：**

**1）核心对象与数据**：ROME（30B总参/3B激活的MoE）与6个基线在6项工具使用基准上的得分对比。ROME以**平均49.46**居中游，超过同架构同规模的Qwen3-Coder（40.87）、24B密集模型Devstral Small 2（39.35）和Gemini-2.5 Flash（43.82），仅落后于GLM-4.5 Air（58.78）、GPT-5 Mini（58.38）与5.1B激活的GPT-OSS-120B（56.47）。Tau2-Bench Retail上ROME达62.28，MTU-Bench Single-Turn达62.45。

**2）关键技术结论**：原文结合图3的ROLL解耦架构（生成—环境交互—奖励流水线+动态GPU池）论证——**仅3B激活参数即可产出具有竞争力的工具调用智能体**，在Tau2-Bench、BFCL-v3等真实API场景上逼近参数规模数十倍于己的模型，证明ROLL训练范式的高效性。

**3）实验链路作用**：作为ROLL方法的核心主结果表，承接图3架构设计，落脚于下游工具使用任务的性能收益，支撑"小激活、强智能体"的整体论点。

### Table 4 (p.30) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-tab04.png]]
> [!quote] caption
> Performance on Tool-Use Benchmarks (Large Models).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读**

该表对比ROME与6款主流大型MoE模型在6项工具调用基准上的表现。ROME仅3B激活参数，平均分**49.46**，与激活37B的DeepSeek V3.1（49.94）持平，并高于Qwen3-Coder Plus（47.41）和Claude-Haiku-4（53.56）；其在MTU-Bench单轮（62.45，第二高）和Tau2-Bench Retail（62.28）尤为突出。GLM-4.6（61.12）与Kimi-K2（60.52）整体领先，ROME与Qwen3-Coder 480B（51.11）也展现强竞争力。

论文借此支撑核心论点：**agentic能力更多源于高质量agentic craft轨迹与RL训练，而非单纯堆参数**——激活参数规模差一个数量级，ROME仍可比肩头部大模型。该表在实验链路中是"参数效率"论证的关键证据，与Figure 4的ROCK架构呼应，共同完成"小模型+精训练≈大模型agentic能力"的论证闭环。

### Table 5 (p.31) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-tab05.png]]
> [!quote] caption
> Performance on General-Agent Benchmarks (Normal Models).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表对比ROME（30B总参/3B激活MoE）与Qwen3-Coder-30B-A3B、Devstral Small 2、GPT-OSS-120B、Gemini-2.5 Flash、GLM-4.5 Air、GPT-5 Mini在GAIA、BrowseComp-ZH、ShopAgent单/多轮四项基准上的表现。ROME平均分25.64，居开源模型之首（Qwen3-Coder仅15.69、Devstral 16.30），超越参数量数倍于自身的GPT-OSS-120B(23.40)与GLM-4.5 Air(24.78)，仅次于闭源GPT-5 Mini(35.59)。ROME在ShopAgent上以34.53/29.61领先多数对手，验证其agentic核心能力。该表处于论文"通用Agent能力评测"环节，与Hard Models表互补，共同支撑"小激活参数亦可达到强agent性能"的关键结论。

> 注：所引文字段落实为Figure 5（iFlow CLI架构图）的讲解，与Table 5主题不直接对应；以上解读基于表格内容及论文主线推断。

### Table 6 (p.31) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-tab06.png]]
> [!quote] caption
> Performance on General-Agent Benchmarks (Large Models).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 联合解读**

**1）对象与数据**：对比 7 个大模型在 4 个通用 Agent 基准上的表现。ROME 仅 30B 总参/3B 激活（MoE），远小于 DeepSeek-V3.1(671B)、Kimi-K2(1043B)、GLM-4.6(355B)、Qwen3-Coder 480B-A35B 等。量化结果：ROME 平均 25.64，高于 Qwen3-Coder-Plus (23.99) 与 Qwen3-480B (23.88)；在 ShopAgent 单轮 (34.53) / 多轮 (29.61) 双双领先，但 GAIA (24.24)、BrowseComp-ZH (14.19) 偏低。

**2）关键结论**：原文以此佐证 ROME"以极少激活参数取得与大型开源 agent 模型相当性能"的核心论断。

**3）链路作用**：作为 Table 5 的大型模型分支补充，与 Figure 6 的数据/训练流水线呼应，从实验端闭环支撑方法有效性。

### Table 8 (p.35) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-tab08.png]]
> [!quote] caption
> Case-study evaluation scores, reported as the average ratings across 30 experts.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 8为30位专家对**ROME**及4个基线（Qwen-Coder-30B、Qwen3-Coder-Plus、Devstral-Small、GLM-4.6）在"睡眠管理系统"与"太阳系建模"两案例下五维度（功能/布局/代码质量/结构/创新）子项评分（满分约100）的平均得分。

**核心数据**：睡眠管理任务中GLM-4.6居首93，ROME与Qwen3-Coder-Plus并列92，Devstral-Small最低86；太阳系建模中Qwen3-Coder-Plus 96居首，ROME 94次之，Devstral-Small仅30分（交互子项仅10）。

**关键结论**：作者方法ROME在两项任务中均位列前列（92/94），与最强商业模型持平并显著领先Devstral-Small，验证其在专业领域生成高质量HTML交互应用的优势，尤其在交互性与代码健壮性上。

**论文作用**：作为IPA框架的专家案例研究补充，与自动化定量评测共同支撑"Agentic工作流+交互感知训练"在交互式代码生成中的有效性论证。

（注：所引正文段落讲解的是Figure 8 IPA训练流水线，与本表无直接对应，故解读以表格自身数据为主。）

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\nabla J_{\text{REINFORCE}}(\pi) = \mathbb{E}_{\tau \sim \pi} \left[ R(\tau)\, \nabla \log \pi(\tau) \right],
$$

$$
G_k = \gamma^{\Delta(j,k)} \times R_{\text{final}},
$$

$$
\mathcal{L}_{\text{\texttt{\textcolor{orange}{IPA}}}} = \lambda_{\text{IL}} \cdot \underbrace{ \sum_{{c}^{*}_{k}\in{\tau}^{*}_{\leq c^*_{f}}} \pi^{megatron}_\theta({c}^{*}_{k}) G_{c^*_k} \nabla \log \pi^{megatron}_\theta({c}^{*}_{k} \mid {\tau}^{*}_{\leq {c}^{*}_{k-1}}) }_{\text{Imitation learning style update}} + \lambda_{\text{RL}} \cdot \mathcal{L}^{c \in \tau_{\geq {{c}_{f}}}}_{\text{\textcolor{orange}{Chunk-RL}}}.
$$

$$
\mathcal{L}_{\mathrm{SFT}}(\theta) = - \frac{1}{\sum_{k=1}^{K} m_k\,|c_{k}| + \epsilon} \sum_{k=1}^{K} m_k\log \pi_\theta\left(c_{k} \mid s_{k}\right),
$$

$$
m_k = m_k^{\mathrm{err}} \cdot m_k^{\mathrm{task}}, \quad m_k^{\mathrm{err}} = \mathbf{1}\big[\neg \mathrm{Err}(k)\big], \quad m_k^{\mathrm{task}} = \mathbf{1}\big[\mathrm{Rel}(k)\big],
$$

$$
\nabla J_{\text{RL}}(\pi) = \mathbb{E}_{\tau \sim \mu^{\text{SGLang}}_{\theta_{old}}} [\underbrace{\left[ {\rho(\tau)}\right]_{0}^{1}}_{TIS} R(\tau) \nabla \log \pi^{\text{megatron}}_{\theta}(\tau)],\quad\rho(\tau) = \big(\prod_{t \in \tau} \frac{\pi^{\text{megatron}}_\theta(\tau_t \mid \tau_{<t})}{\pi^{\text{megatron}}_{\theta_{\text{old}}}(\tau_t \mid \tau_{<t})}\big)^{\frac{1}{|\tau|}}
$$

$$
\nabla J_{\text{RL}}(\pi) &= \underbrace{\sum_{\tau \in \mathcal{T}^+} \mu^{\text{SGLang}}_{\theta_{old}}(\tau) R(\tau)\nabla \log \pi^{\text{megatron}}_{\theta}(\tau)}_{\textrm{Weighted SL update for positive examples}} + \underbrace{\sum_{\tau \in \mathcal{T}^-} \mu^{\text{SGLang}}_{\theta_{old}}(\tau)\left[\rho(\tau) \right]_{0}^{1} R(\tau)\nabla \log \pi^{\text{megatron}}_{\theta}(\tau)}_{\textrm{Clipped IS update for negative examples}} \;,
$$

$$
\nabla J_{\text{RL}}(\pi) = &\underbrace{ \sum_{\tau \in \mathcal{T}^+} \mu^{\text{SGLang}}_{\theta_{old}}(\tau) R(\tau) \sum_{k=1}^{|\tau|} m_k \nabla \log \pi^{\text{megatron}}_\theta(\tau_k \mid \tau_{<k}) }_{\text{Weighted SL update with token-level masking}} \nonumber\\&+\underbrace{ \sum_{\tau \in \mathcal{T}^-} \mu^{\text{SGLang}}_{\theta_{old}}(\tau) \left[\rho(\tau)\right]_0^1 R(\tau) \sum_{k=1}^{|\tau|} m_k \nabla \log \pi^{\text{megatron}}_\theta(\tau_k \mid \tau_{<k}) }_{\text{Clipped IS update with token-level masking}} .
$$

$$
\rho_c (c) = \bigg(\prod_{t \in c} \frac{\pi^{\text{megatron}}_\theta(\tau_t \mid \tau_{<t})}{\pi^{\text{megatron}}_{\theta_{\text{old}}}(\tau_t \mid \tau_{<t})}\bigg)^{\frac{1}{|c|}}.
$$

## 技术点深读（DEEP）

![[deep/let-it-flow-agentic-crafting-on-rock-and-roll]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/let-it-flow-agentic-crafting-on-rock-and-roll.txt`（160353 字符）供引用检索。