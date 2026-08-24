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
> 【图文联合解读】图(a)展示ALE双层架构：左侧ROLL训练框架含Actor Train/Infer（Sync Weight同步权重）与Env.Manager调度多Env.Worker（运行Rock SDK）；右侧ROCK执行引擎以iFlow CLI为Agent，通过ModelProxy的Request/Response Queue与LLM四步轮询（①送②收③查④回）。图(b)RL管线：Rollout阶段Agentic LLM与Environment以Action Tokens、Observation State循环生成Trajectory Data；Training阶段据此Weight Update，再经Weight Synchronization回灌Rollout。原文据此论证智能体强化学习的核心挑战已从"数据规模"转向"训练基础设施、可执行环境与评估协议的协同设计"，ALE构成后续Terminal-Based Benchmark（Table 2）等实验的系统底座，并通过rollout与训练解耦支撑大规模端到端训练。

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

图4以"ROCK SERVICE"为核心架构，展示了五大核心技能：①Skill 1精简SDK控制（make/reset/step/close四操作）；②Skill 2无缝Agent扩缩，统一纳管Openhands、iFlow CLI、Mini Agent、SWE Agent等多类异构Agent；③Skill 3原生Agent桥接，通过OpenAI协议对接Agent Frame、GEM协议对接RL Frame（传输LLM Request/Response与Action/Observation）；④Skill 4大规模调度，支持10,000+并发Sandbox（Running/Succeed/Failed/Pending多状态共存）；⑤Skill 5鲁棒故障隔离，单Sandbox崩溃不影响其他Running节点。

该图论证了ROCK通过"控制平面SDK化+执行平面Sandbox池化+协议层兼容化"的设计，同时支撑训练与推理链路。在论文整体链路中，它奠定了Table 4工具使用基准测评的工程基础——正是凭借10K+并发环境与多Agent兼容能力，论文才能在R²-Harness、τ²-Bench等基准上跑通大规模强化学习训练流，从而得出"工具调用SOTA"的结论。

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

该图对比了三种重要性采样粒度：每个 chunk 由 system prompt sₜ、h 个 token (τₜ₁–τₜₕ) 与 response rₜ 构成。Token 级将交互点落在 chunk c₂ 的 token 序列内部（最细粒度）；Chunk 级让交互点严格对齐 chunk 边界（即 c₁→c₂ 或 cₜ 末尾，✓ 标记处），与一次完整 agent 交互天然对应；Sentence 级则将多个 chunk 聚合为一个交互单位（粒度最粗）。

**关键结论**：Chunk 级采样与交互的自然粒度一致，能获得更稳定、低方差的重要性权重估计，是论文 method 设计的基础选择。**链路作用**：作为消融性图示，为后续实验中选择 chunk 级策略提供直觉与一致性论据。

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

左图：从 s₁ 全程采样至关键分叉 s*ᵢ 再至 s*ⱼ，多条 rollout 全部失败（✗），标注 "Costly Search from the Beginning""All Failures""Uninformative Rollouts"，凸显从零探索的低效。

右图：在专家轨迹引导下 "Rollback" 回滚至 Crucial Fork s*ᵢ，从该 chunk 重采样 c(i)⁽ⁱ⁾r(i)⁽ⁱ⁾ 三条并行分支，得到成功（✓）与失败（✗）混合的 "Valuable Rollouts"，Success Rate 显著提升。

**技术结论**：Sequential Rollback 将搜索负担从全程前推压缩到 chunk 级重采，大幅释放有效样本；**论文作用**：与 Resampling 模块协同，是 FlowRL 在长程 agentic 任务中解决"前期探索瘫痪"的关键采样加速器，直接决定策略收敛效率。

### Figure 12 (p.25) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig12.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p25.png]]*
> [!quote] caption
> Performance of Sequential Rollback and baseline (naive sampling) on a challenging training task. Left: Average success rate during training, which reflects the percentage of positive signals in training batch. Sequential Rollback obviously brings more valuable rollouts compared to baseline (all failures). The drop of success rate indicates that the model has rolled back across a crucial chunk to t

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图12以三联子图展示Sequential Rollback与Baseline在困难训练任务上的对比。**左图**（训练成功率）：Seq-Rollback成功率在10%–100%剧烈波动，基线始终为0；图中橙色圆圈标出两处"成功率骤降"点，暗示模型跨越关键chunk回退重试。**中图**（专家chunk使用量）：随训练步数从约42单调降至0，标注"沿专家轨迹回退"，说明模型逐步摆脱对专家的依赖。**右图**（测试成功率）：前75步两者均失败，约75步后Seq-Rollback陡升至近100%，基线恒为0。

该图作为论文核心实验证据，定量证明：顺序回退机制可产生富含正信号的rollout，且随训练自收敛——专家介入渐少、测试成功率跃升，完整支撑了"agentic crafting需回退式探索"这一方法论主张。

### Figure 13 (p.26) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig13.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p26.png]]*
> [!quote] caption
> Comparison of IPA with & without Chunk-Level Initialized Resampling (Parallelized Initial- ization) on a mini-set of the training data. Left: Average success rate on training tasks. The gap between curves in the early stage of training shows that the Chunk-Level Initialized Resampling brings much more diverse reward signals in training batches. Middle: Minimum success rate across train-tasks with 

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图由三个子图对比IPA算法有无Chunk-Level初始化重采样（并行初始化）的效果。左图（训练平均成功率）：加该模块（橙）由约35%稳步升至~95%，基线（灰）峰值仅~75%且后期回落至~40%；中图（训练最低任务成功率）：加模块约40步后陡升至~70%，基线恒为0，蓝色箭头标注"学习困难任务能力"；右图（测试平均成功率）：加模块达~90%，基线仅~53%。

原文以此论证Chunk-Level初始化重采样在训练早期为batch注入更丰富的奖励信号，使智能体能攻克困难任务并显著提升测试泛化，是IPA流程中关键的样本多样性增强组件，支撑整体训练稳定性与泛化性能。

### Figure 14 (p.27) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig14.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p27.png]]*
> [!quote] caption
> Benchmark characterization and cross-benchmark comparison of Terminal Bench Pro against other benchmarks.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图14以四联图刻画Terminal Bench Pro：8类任务各25例，共200例、每类占12.5%，较1.0/2.0更均衡。Pro Public每题测试数最小/中位/均值为10/19/28.3（1.0：1/3/5；2.0：1/3/8）；安全、软件、运维、调试的跨基准pass@1标准差为0.04/0.02/0.05/0.04。说明新版测试更充分、性能波动更低；该图在主评测前审计基准，为后续能力与泛化比较提供统一标尺。

### Figure 15 (p.28) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig15.png]]
*整页渲染: ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p28.png]]*
> [!quote] caption
> Performance-parameter trade-offs in agentic tasks. Scores represent averages on general agentic and code agent benchmarks. Models with known parameters are shown as circles, while proprietary models with unknown parameters are depicted as diamonds (right side). Left: Total parameters versus overall performance. Right: Activated parameters versus overall performance. 2https://github.com/alibaba/ter

> [!tip] 技术解读（多模态）
> 【图文联合解读】**核心对象与数据**：双子图散点图。左图横轴为总参数量（15B–Unknown，对数刻度），右图为激活参数量（0–Unknown），纵轴均为智能体任务平均准确率（10–40%）。圆点=开源已知参数模型，菱形=闭源模型。关键数据：IFlow-ROME（30B-A3B，紫色星标）以仅3B激活参获约30%准确率；同尺寸Qwen3-Coder 30B-A3B仅约20%；480B级Qwen3-Coder 480B、Kimi-K2-0905约32–34%；闭源Claude-Haiku-4.5达约40%。

**技术结论**：右图中IFlow-ROME显著领先Pareto前沿——以约1/10的激活参量匹配甚至超越480B级开源模型，证明MoE在智能体任务上的高参数效率；左图同步显示其30B总参亦优于多数同体量模型。

**论文作用**：作为模型发布的核心效率证据，呼应"小激活、强能力"主张，与训练流程、通用/代码智能体基准评测章节形成完整论证闭环。

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
> 【图文联合解读】## 图18图文联合解读

**核心对象**：5×2网格对比ROME、Qwen3-Coder-Plus、GLM-4.6、Qwen3-coder-30B、Devstral-Small-2共5个模型对"太阳系建模"任务的两帧渲染截图。ROME产出最完整——黑底同心椭圆轨道+中心太阳+多颗异色行星按真实尺度分布；Qwen3-Coder-Plus行星在帧2呈初始共线；GLM-4.6含星空蓝底与左右UI信息面板；Qwen3-coder-30B带中文行星标签；Devstral-Small-2近乎空场，仅余中心亮点与单轨道，未渲染行星。

**论证结论**：作为定性证据，支撑ROME在agentic创意编码中场景完整度、物理合理性与元素丰富度全面优于基线模型。

**论文作用**：实验章节"案例研究"的视觉佐证，与定量评估互补，共同验证"agentic crafting"框架在多类创意生成任务上的普适优势。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.29) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-tab01.png]]
> [!quote] caption
> Performance on Terminal-Based Benchmarks (Normal Models).

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 1对比7个模型在6项终端编码基准的得分。ROME（MoE，30B总参/3B激活）在Terminal-Bench 1.0（41.50）、2.0（24.72）、Pro-Public（40.50）三项居首，均值37.60第一；SWE-Bench Verified（57.40）与Multilingual（40.00）仅次于GPT-5 Mini。

论文借此论证：仅3B激活的ROME均值全面领先——超GPT-OSS-120B（31.83）、GLM-4.5 Air（31.75）、Devstral Small 2（29.10）、Qwen3-Coder（25.94）、Gemini-2.5 Flash（19.87），并略胜GPT-5 Mini（37.99），印证MoE架构与ALE训练实现"小模型高性能"的有效性。

该表是支撑ROME开源SOTA主张的核心量化证据，串联Figure 1的ALE方法概述与后续消融/规模化分析，构成实验链路关键节点。

### Table 2 (p.29) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-tab02.png]]
> [!quote] caption
> Performance on Terminal-Based Benchmarks (Large Models).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读**

表2对比ROME（30B总参/3B激活）与Qwen3-Coder Plus、Qwen3-Coder 480B-A35B、DeepSeek V3.1（671B/37B激活）、GLM-4.6（355B/32B）、Kimi-K2（1043B/32B）、Claude-Haiku-4共7个模型在Terminal-Bench 1.0/2.0、SWE-Bench Verified/Multilingual及Terminal-Bench-Pro-Public/Private六项基准上的表现。

ROME均分37.60，虽低于Claude-Haiku-4（48.84），但在Terminal-Bench 1.0以41.50反超DeepSeek（38.75）、Kimi-K2（39.25），与GLM-4.6（41.25）持平；Pro-Public得40.50，与Kimi-K2并列。SWE-Bench Verified 57.40亦领先DeepSeek（62.20以外的多数MoE对手）。

该表是论文"小激活、强agent"主张的关键实证——仅3B激活参数即可在agentic终端任务上与千亿级MoE模型正面竞争，验证其训练栈与RL策略的效率优势。

### Table 3 (p.30) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-tab03.png]]
> [!quote] caption
> Performance on Tool-Use Benchmarks (Normal Models).

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 3对比7个模型在6项Tool-Use基准上的表现。ROME为30B MoE架构、仅激活3B参数，平均得49.46，大幅领先同规模Qwen3-Coder（40.87）与Devstral Small 2（39.35），并在Tau2-Bench三域（Retail 62.28、Airline 50.50、Telecom 30.92）、BFCL-v3（43.00）、MTU-Bench多轮（47.63）上全面压制同量级对手；与参数量大数倍的GPT-OSS-120B（56.47）、GLM-4.5 Air（58.78）、GPT-5 Mini（58.38）仅小幅落后。论文借此论证：ROLL框架以极少激活参数量即可训练出强工具调用与多轮交互能力的agentic模型，是方法有效性论证的关键实验支撑。

### Table 4 (p.30) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-tab04.png]]
> [!quote] caption
> Performance on Tool-Use Benchmarks (Large Models).

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 4展示ROME与Qwen3-Coder Plus/480B-A35B、DeepSeek V3.1、GLM-4.6、Kimi-K2、Claude-Haiku-4在Tau2-Bench(Retail/Airline/Telecom)、BFCL-v3、MTU-Bench(单/多轮)六项工具调用基准上的得分。ROME为MoE架构，总参30B、激活仅3B，平均分49.46，介于GLM-4.6(61.12)、Kimi-K2(60.52)与DeepSeek V3.1(49.94)之间；其以3B激活参数即逼近Qwen3-Coder 480B-A35B(51.11)、超过Qwen3-Coder Plus(47.41)，并在Tau2-Retail并列最高62.28、MTU单轮62.45位列第二。该表用以论证ROME在激活参数仅为对手1/10量级下仍保持可比工具调用性能，是论文Agentic实验链路中"高效小型激活MoE"的关键支撑证据。

### Table 5 (p.31) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-tab05.png]]
> [!quote] caption
> Performance on General-Agent Benchmarks (Normal Models).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 图文联合解读**

Table 5 对比 ROME（30B MoE、激活 3B）与 Qwen3-Coder 30B-A3B、Devstral Small 2（24B Dense）、GPT-OSS-120B、Gemini-2.5 Flash、GLM-4.5 Air、GPT-5 Mini 共 7 个模型在 GAIA、BrowseComp-ZH、ShopAgent（单/多轮）4 项通用 Agent 基准上的成绩。ROME 平均 **25.64**，超过 Qwen3-Coder（15.69）、Devstral（16.30）、GPT-OSS-120B（23.40）、Gemini-2.5 Flash（22.66）、GLM-4.5 Air（24.78）等所有开源/闭源对手，仅次于 GPT-5 Mini（35.59）；ShopAgent 单轮 34.53、多轮 29.61 均居开源模型首位。

该表用以印证"ROME 以仅 3B 激活参数即在多数基准上比肩/超越更强开源 Agent 模型"这一关键技术结论，是 ROME 训练完成后在通用 Agent 能力维度上的关键评测证据，与 Figure 5 的 iFlow CLI 数据/训练链路上下游呼应，共同构成"数据→训练→评测"的闭环验证。

### Table 6 (p.31) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-tab06.png]]
> [!quote] caption
> Performance on General-Agent Benchmarks (Large Models).

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 6对比ROME（MoE，30B总参/3B激活）与6个大型基线在GAIA、BrowseComp-ZH、ShopAgent（单/多轮）4项基准的成绩。ROME均值25.64，超过Qwen3-Coder Plus（23.99）与Qwen3-Coder 480B-A35B（23.88），ShopAgent双轮34.53/29.61均高于Kimi-K2（30.97/26.26），仅次于DeepSeek V3.1（32.16）与Claude-Haiku-4（32.51）。

原文据此论证：ROME以仅3B激活参数（远小于同类32–37B）即取得有竞争力的通用Agent能力，证明其agentic数据合成与训练流水线在效率与泛化上的优势，构成论文"通用Agent能力外推验证"环节的核心证据，为前文数据构造（图6）→ 训练 → 评测闭环提供横向性能对标支撑。

### Table 8 (p.35) ⭐深度解读
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-tab08.png]]
> [!quote] caption
> Case-study evaluation scores, reported as the average ratings across 30 experts.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 图文联合解读**

**核心数据**：该表对比 ROME 与 Qwen-Coder-30B、Qwen3-Coder-Plus、Devstral-Small、GLM-4.6 共 5 个模型，在「睡眠管理系统」与「太阳系建模」两个案例、5 个子维度（功能/布局/代码质量/结构/创新）上的 30 位专家打分。

**关键结论**：ROME 在两个案例总分分别达 92 与 94，整体领先或并列最优（Sleep 仅次于 GLM-4.6 的 93，Solar 超过 Qwen3-Coder-Plus 的 96 仅 2 分但功能交互项 34 vs 36 接近）；Devstral-Small 在 Solar 案例骤降至 30，暴露其复杂交互任务短板。

**作用**：作为自动评测的补充，以专家主观评分印证 ROME 在真实 GUI 智能体案例中的实用性与稳健性，强化主实验结论。

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