---
paper_num: "32"
title: "Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with Large-Scale Asynchronous RL"
authors: "Search with Large-Scale Asynchronous RL Jiaxuan Gao1, Wei Fu12, Minyang Xie1, Shusheng Xu2, Chuyi He2, Zhiyu Mei2, Banghua Zhu3, Yi Wu1∗ 1 IIIS, Tsinghua University, 2 Ant Group 3 University of Washington samjia2000@gmai"
date: "2026/1/17"
arxiv: "https://arxiv.org/abs/2508.07976"
pdf: "papers/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl.pdf"
slug: "beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl"
tags: []
---

# Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with Large-Scale Asynchronous RL

> [!abstract] 摘要（原文）
> 

## 元信息
- **发表日期**: 2026/1/17
- **作者**: Search with Large-Scale Asynchronous RL Jiaxuan Gao1, Wei Fu12, Minyang Xie1, Shusheng Xu2, Chuyi He2, Zhiyu Mei2, Banghua Zhu3, Yi Wu1∗ 1 IIIS, Tsinghua University, 2 Ant Group 3 University of Washington samjia2000@gmai
- **arXiv**: https://arxiv.org/abs/2508.07976
- **本地 PDF**: `papers/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl.pdf`
- **页数**: 21

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig01.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p01.png]]*
> [!quote] caption
> (Left) Asynchronous RL brings substantial improvements: Through RL training, our agent, ASearcher-Web-QwQ, obtains +15.0, +22.4, and +15.6 improvements on GAIA, xBench, and

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（中文）**

**1）核心对象与结构/数据：**
图分三栏。左栏为Avg@4准确率柱状图，在GAIA/xBench-DeepSearch/Frames三基准上，Before RL（43.7/28.7/58.9）→ASearcher-v1（52.8/42.1/70.9）→ASearcher-v2（58.7/51.1/74.5），v2相对RL前分别提升+15.0/+22.4/+15.6。中栏显示训练步0–450中每轨迹工具调用次数，阶段2（>200步）后MAX约从5增至100+，AVG从~2升至20+。右栏（log刻度）显示生成tokens从~10⁴升至~10⁵。

**2）原文论证的关键技术结论：**
异步RL带来显著增益，验证训练有效性；随训练推进，模型自发学习更长程的搜索行为（工具调用与生成长度均上升），证明大尺度异步RL可"解锁"十回合以上的长时搜索能力。

**3）在论文中的作用：**
开篇Figure 1统领全文，主图三栏共同支撑"异步RL既提精度、又增长horizon"的两大核心论点，为后续方法与消融提供动机与可视化依据。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig02.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p03.png]]*
> [!quote] caption
> Comparison between ASearcher and Search-R1. (Left) Search-R1 is only equipped with search tools and lacks web browsing capability. (Right) ASearcher utilizes a simple agent design with two basic tools including search and browsing tools, without relying on any external LLM. ASearcher is a comprehensive agent capable of both reasoning and summarizing lengthy web contents. Notably, both reasoning an

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图2对比Search-R1与ASearcher两种智能体架构。左侧Search-R1仅配备搜索工具，单轮最大≤10 turns，仅返回Top-K条目；右侧ASearcher集成搜索+浏览双工具，最大支持≤128 turns长程交互，且能将约100K长度的网页内容摘要压缩至约100长度。图例区分可训练组件（LLM Gen、Tool Calling）、外部工具与外部信息四类。

原文借此论证关键结论：ASearcher以单一LLM即可同时完成推理与长网页总结，无需依赖外部LLM，突破Search-R1的10轮瓶颈。

作用：作为方法核心框架图，为后续大规模异步RL训练及Table 2本地知识库实验提供架构基础。

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig03.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p04.png]]*
> [!quote] caption
> A case study on a complex query from GAIA. Search-R1-32B is unable to break down the complex question and has severe hallucinations. Search-o1 (QwQ) can identify the corrects articles through extensive tool calls, but easily misses key information and fails to verify wrong conclusions. Our end-to-end RL agent, ASearcher-Web-QwQ, exhibits key behaviors featuring

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图3以GAIA复杂问答"Mice"为题，对比三列方法推理轨迹：Search-R1-32B 3次搜索即给出错误"Pigs"且无验证；Search-o1(QwQ)经多轮检索定位文献，但漏关键信息并误判为"Goats"；ASearcher-Web-QwQ通过四阶段——聚焦搜索定位Hafnia alvei→识别Wikipedia及相关2021临床文献→跨文档关联Olga Tapia小鼠研究→基于二次检索的*Grounded Verification*——得出正确答案"Mice"。

该案例支撑论文核心结论：端到端异步RL赋予智能体**长程分解、不确定性感知与自我验证**能力，使其在超过10轮的复杂任务上优于无验证搜索式RL及已有Search-o1基线，是正文论证ASearcher长视野搜索优势的**关键定性证据**。

### Figure 4 (p.7) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig04.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p07.png]]*
> [!quote] caption
> Data Synthesis Agent. Starting from a seed QA, the data synthesis agent iteratively modifies the question through two actions, Injection and Fuzz. Through injection, the agent enriches the question by adding some external facts. Through Fuzz, the agent blurs certain information to increase uncertainty and difficulty. The related fact to the question are tracked during the synthesis process.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图4展示数据合成Agent的三阶段闭环管线：①**左：种子输入**——以QA对（Q："Daniel Charbonell 2014签约旧金山巨人合同几年？" A：四年）及支撑事实为起点；②**中：双动作迭代修改**——**Injection**通过搜索引擎+浏览器抽取外事实（如"古巴外野手，曾效力San Jose Giants"）注入问题增加线索；**Fuzz**模糊关键信息（如将"2014"改为"early 2010s"）提高不确定性；③**右：质量验证三步**——基本可解性与清晰度检查、多答案生成测难度（仅"四年"✓）、答案唯一性校验；通过后回流更新QA与事实库。

**论文作用**：此管线为大规模异步RL训练提供高质量、可解、唯一、具长程推理难度的事实型QA数据，是Agentic Search模型在GAIA/xBench等基准（表4）取得SOTA的数据基础。

### Figure 5 (p.7) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig05.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p07.png]]*
> [!quote] caption
> Statistics from our data synthesis process. (Left) The distribution of the number of supporting facts. (Middle) The distribution of the number of fuzz actions and injection actions. (Right) The accuracy distribution of QwQ-32B in answering the generated questions without using any tools. • The model finds a correct answer with only a few search turns (i.e., ≤1 turns).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心数据**：左图支撑事实数主要分布在7–9之间（占比~0.18–0.19），呈长程检索特征；中图fuzz动作集中在5–6次（峰~0.33），injection动作更分散、向10–11次偏移，整体动作链跨度大；右图QwQ-32B无工具直接答题准确率呈双峰分布，约60%集中于0附近，约15%接近1。

2) **关键结论**：合成问题普遍依赖多条事实链与多轮检索动作，远超单跳查询；模型无工具时绝大多数无法作答，双峰说明问题要么完全无法直接推理、要么模型"碰巧"记住，真正考验搜索与多轮整合能力。

3) **论文作用**：作为数据合成管线的统计验证，为后续ASearcher的大规模异步RL训练提供难度合理、长度足够的长程搜索任务基线。

### Figure 6 (p.9) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig06.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p09.png]]*
> [!quote] caption
> (Left) Test scaling of ASearcher-Web-QwQ. Data points are obtained by enforcing different minimum turns.The accuracy is averaged over GAIA, xBench-DeepSearch, and Frames. (Middle)

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1. **核心对象与数据**：左图显示ASearcher-Web-QwQ测试时平均工具调用数（5→12）与平均准确率（≈52%→55%）呈单调上升关系；中图显示训练过程中每条轨迹的工具调用数：MAX从约5增长至峰值60–70，AVG稳定在3–7，MIN接近0–1；右图log尺度下生成tokens同步增长（MAX由≈5×10⁴升至≈2×10⁵，AVG由10⁴升至≈2×10⁴）。

2. **关键技术结论**：测试时强制更多回合显著提升准确率，验证了长程搜索的scaling有效性；训练中模型自发涌现出远超常规的长轨迹行为，突破了"ten-turn"限制。

3. **论文中的作用**：以训练动力学（工具调用与token长度自然增长）+ 测试时scaling实证共同支撑"大规模异步RL可解锁长程agentic搜索"这一核心论点，衔接方法设计与下游性能收益。

### Figure 7 (p.10) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig07.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p10.png]]*
> [!quote] caption
> One-Step-off RL v.s. Fully Asynchronous RL. In batch generation systems, a batch should wait for the longest trajectory, leading to significant GPU idle time. In contrast, fully asynchronous RL achieves faster training than batch generation RL by fully decoupling training and trajectory generation, achieving near-full resource utilization for trajectory generation. example for batch generation RL 

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示横向对比两种RL训练流水线。**One-Step-Off RL**：轨迹1–12并行生成，但批次须等待最长轨迹（如横跨多步的Traj 7）才能启动Train Step N，期间已完成的Traj 8–12被迫"Idle Time"；训练步内mini-batch顺序为(1,2,3,4)→(6,5,8,7)，存在乱序与浪费。**Fully Async RL**：轨迹持续异步产出，训练步N/N+1/N+2以更短周期无缝触发，分别消费(1,2,3,4)、(5,6,8,9)、(10,7,11,13)，GPU近满载。该图论证：完全解耦训练与轨迹生成可消除长尾阻塞、显著加速训练，是论文支撑大规模长周期智能体搜索RL训练的核心基础设施依据。

### Figure 8 (p.14) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig08.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p14.png]]*
> [!quote] caption
> Comparison of the performance of QwQ-32B agent before and after RL Training. training pipeline trains the agent to learn complex search strategies to perform precise searches, extract key information, and resolve conflict information.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图以双柱状图（左 Avg@4、右 Pass@4）在 GAIA、xBench-DeepSearch、Frames 三大基准上对比 QwQ-32B 基座 RL 训练前后的表现。**具体数据**：Avg@4 三基准分别由 43.7/28.7/58.9 提升至 58.7/51.1/74.5（ASearcher-v2）；Pass@4 由 62.1/51.0/77.1 提升至 74.7/75.0/85.5，且 v1→v2 仍持续单调上升。

**关键论证**：原文借此佐证所提出的异步大规模 RL 训练流程，使 agent 习得复杂检索、关键信息抽取与冲突信息消解能力——尤其 xBench-DeepSearch 增幅最显著（Avg@4 +22.4、Pass@4 +24.0），说明 RL 对长程深度搜索类任务增益最大。

**论文作用**：作为核心主结果图，量化证明方法在多基准上对开源基座 QwQ-32B 的稳定提升，支撑整体异步 RL 训练范式有效性的实验结论。

### Figure 9 (p.15) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig09.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p15.png]]*
> [!quote] caption
> Training Dynamics of ASearcher-Local-7B.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图9展示ASearcher-Local-7B在约300个训练步内三项均值指标的变化曲线：(a) **生成Tokens**从~1000于~50步骤降至~150低谷，后回升至~900；(b) **搜索次数**由~1于~80步后稳步攀升至~5.5；(c) **URL直访**由~0.4于~50步内归零并长期维持近0。

**技术结论**：训练初期模型快速抑制冗余URL直访并精简生成；随后轨迹逐步延长、检索轮次自然增加，验证"长程多轮检索行为由RL自主涌现"而非依赖设计。

**论文作用**：作为ASearcher异步RL方法在长视野agentic搜索中有效性的一手演化证据，支撑全文关于模型自学深度检索、突破十轮瓶颈的核心论点。

### Figure 10 (p.15) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig10.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p15.png]]*
> [!quote] caption
> Training Dynamics of ASearcher-Local-14B. 15

> [!tip] 技术解读（多模态）
> 【图文联合解读】**Figure 10 联合解读**

Figure 10 展示 ASearcher-Local-14B 在约 220 训练步内三个行为指标演变：
- (a) 单轨迹生成 token：由 ~400 降至 ~200（step 25），step 60 跃至峰值 ~720，后续于 500–650 震荡；
- (b) 单轨迹搜索次数：由 ~1.5 在 step 35 后跃升，峰值 ~5.8（step 60），稳定于 4–5；
- (c) 单轨迹 URL 访问：长期近 0，step 130 后跃升至 ~1.8–2.0 并维持。

三图共同证明：随异步 RL 推进，模型自发涌现更长推理链、更频繁的多轮搜索与网页访问，验证方法有效激励长程智能体搜索行为。该图在论文中作为训练动态的关键实证，支撑"异步大规模 RL 可解锁超十轮搜索"的核心论点。

### Figure 11 (p.16) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig11.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p16.png]]*
> [!quote] caption
> Left: Word count of reflective keywords during training time. Right: Word count of keywords indicating explicit reference of external information. sophisticated prompt-based agents powered by Large Reasoning Models through offline RL [19], SFT on simulated trajectories with real-world web data [32, 17], and constructing challenging QAs for RL training. [34].

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图11联合解读**

**核心数据**：左图展示训练step 0–400内6个反思关键词（search/alternatively/wait/check/confirm/however）的每轨迹词频，"search"峰值约8k+、"alternatively"约7k；右图展示5个外部信息显式引用词（doc/mention/source/earlier/previous）频次，"doc"峰值约2.5k、"previous"约1.5k。两组曲线在step ≈250后均出现陡升拐点并持续上行。

**关键结论**：随着RL训练推进，智能体自发地、显著地增加了反思性措辞与显式回溯外部文档的频率，证明"自我校验＋信息溯源"这一核心agentic行为模式是奖励驱动的涌现结果，而非依赖prompt工程或SFT的先验注入。

**整体作用**：作为行为层面（behavioral）的诊断证据，支撑论文主张——大规模异步RL能自然解锁长视野智能体搜索能力，反思-引用循环是性能增益的关键机制。

### Figure 12 (p.20)
![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p20.png]]
> [!quote] caption
> A case study on a complex query from GAIA. Search-R1-32B is unable to break down the complex question and has severe hallucinations. Search-o1 (QwQ) can identify the corrects articles through extensive tool calls, but easily misses key information and fails to verify wrong conclusions. Our end-to-end RL agent, ASearcher-Web-QwQ, exhibits key behaviors featuring

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.7) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-tab01.png]]
> [!quote] caption
> Examples of the synthetic questions, where red indicates injected facts and cyan represents fuzzed content.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表1 联合解读：**

表1展示合成长程搜索问题的多轮构造流程，结构为 Round / Action / Question 三列。两组示例均从简短 Seed QA 出发：Round 1–2 执行"注入"（Injection）逐步叠加新事实（如"Eckerd College 校友""Ulster County County Executive"等），Round 3 执行"模糊化"（Fuzzing），将具体实体替换为通用指代（如 *Catskill Mountain Railroad* → *a historic mountain railway*、*American Legion Post* → *veterans' organization's building*、*1934* → *early 1930s*），切断直接检索路径。

该表论证的技术结论：通过注入与模糊化的多轮迭代，可构造需10+轮搜索推理才能解答的长程合成问题，从而缓解真实长程 QA 数据稀缺的瓶颈。

在论文链路中，此表所展示的合成机制是 ASearcher 训练数据的生成核心——为大规模异步 RL 提供高难度监督信号，使智能体学会在多跳、模糊、远距离事实间反复检索与整合。

### Table 2 (p.12) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-tab02.png]]
> [!quote] caption
> Results with Local Knowledge Base.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 2对比ASearcher-Local与基线在7B/14B两组、4多跳+3单跳QA上的F1/LasJ结果：ASearcher-Local-7B均值58.0/61.0、14B版59.7/63.6，均为各规模SOTA；多跳显著领先(2WikiMQA-F1=72.3/72.2、Musique-F1=34.4/35.6)，单跳与Search-R1-32B持平。论文借此论证：仅靠search+browsing双工具、无外部LLM的简洁agent经长程异步RL训练即可超越所有搜索增强基线，且7B即逼近32B对手(58.0 vs 58.7)。该表与Figure 2架构图呼应，作为封闭KB实验的核心性能基线，为后续开放Web实验奠基。

### Table 3 (p.12) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-tab03.png]]
> [!quote] caption
> Results with Web-based Search and Browsing.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读：**

表3对比Web搜索/浏览方法在7个QA基准（多跳：2WikiMQA、HotpotQA、Bamboogle、Musique；单跳：NQ、TriviaQA、PopQA）的F1与LasJ指标，按7B与14B/32B两组划分。ASearcher-Web-7B平均58.6/61.7，超越DeepResearcher-7B(54.9/58.3)、Simple-DS-7B(53.5/60.3)与Search-R1-7B(56.9/59.0)；ASearcher-Web-14B达61.5/64.5，亦胜Search-R1-32B(60.4/62.5)，并在多跳任务（如2WikiMQA 76.1）全面领先。该表证明异步RL框架由本地检索迁移到真实Web浏览后仍保持SOTA，验证方法在开放环境下的长程搜索泛化能力，构成论文"local→web"完整实验链路的收官。

### Table 4 (p.13) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-tab04.png]]
> [!quote] caption
> Results on GAIA, xBench-DeepSearch, and Frames. The results are evaluated with LLM- as-Judge. For baselines, we run the corresponding official codes for 4 seeds and report Avg@4 and Pass@4.

> [!tip] 表格解读（多模态）
> 【图文联合解读】观察到**图片表头列名实际为2WikiMQA/HotpotQA/Bamboogle/Musique（多跳QA）与NQ/TriviaQA/PopQA（单跳QA），与caption所述"GAIA/xBench-DeepSearch/Frames"不一致**，现按图片实际内容解读：

**1）结构**：对比7B与14B/32B规模下Search-R1、R1-Searcher、DeepResearcher、SimpleDS等基线及ASearcher-Local/Web系列在7个标准QA基准上的F1与LasJ及均值。

**2）关键结论**：ASearcher-Local-7B在2WikiMQA F1 69.1、TriviaQA F1 75.2等多列居首；ASearcher-Web-14B于2WikiMQA达76.1/80.7；14B级ASearcher均值F1 60.0/61.5、LasJ 65.6/64.5均超越Search-o1（55.8/64.9）等强基线，证实大规模异步RL+长程搜索训练在通用检索QA上的稳定增益。

**3）作用**：与GAIA/xBench长程agentic评测互补，证明ASearcher方法在标准QA检索任务中同样具SOTA竞争力，体现泛化性。

### Table 5 (p.14) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-tab05.png]]
> [!quote] caption
> Pass@1 results of ASearcher-Web-QwQ-v2 and baselines, evaluated on GAIA [ 24 ], xBench- DeepSearch [ 41 ], Frames [ 14 ], and HLE-500 [ 19 ]. † indicates results are obtained from official reports.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 解读**

**结构与数据**：该表按三类方法（Commercial Deep Research Agents、General LLMs using Tools、本文 ASearcher-Web-QwQ）在 GAIA、xBench-DeepSearch、Frames、HLE-500 四个基准上的 Pass@1 结果。本文 ASearcher-Web-QwQ-v2 基线为 58.7/51.1/74.5/21.5；叠加 Summary=DeepSeek-V3 提升至 60.3/56.4/76.6/23.4；进一步加入 Test-time Search (K=16) 跃升至 **71.8/75.0/83.4/24.6**。

**关键技术结论**：K=16 时本文方法在 GAIA 上超越 OpenAI-o3 (70.5) 与 OpenAI DeepResearch (67.0)，在 xBench 上达到 75.0 的 SOTA；Frames (83.4) 与 HLE-500 (24.6) 也极具竞争力，验证了"异步 RL + 测试时搜索扩展"的有效性。

**论文作用**：作为主结果表，是论证方法 SOTA 性能的最终实验证据，支撑全文异步大规模 RL 框架的核心贡献。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
J(\pi) = \mathbb{E}\left[\sum_{t=0}^{\infty} \gamma^t R(s_t, a_t) \bigg| a_t \sim \pi(s_t)\right]
$$

$$
\mathcal J_{GRPO}(\theta)=\mathbb E_{x\sim \mathcal D,\{\tau_i\}_{i=1}^G\sim\pi_{\theta_{old}}(\cdot|x)}\Bigg[&\frac{1}{G}\sum_{i=1}^G\frac{1}{\sum_{t=0}^{T_i-1}|a^i_t|}\sum_{t=0}^{T_i-1}\sum_{j=1}^{|a_t^i|}\min\Bigg( \frac{\pi_\theta(a_{t,j}^i|s_t,a_{t,<j}^i)}{\pi_{\theta_{old}}(a_{t,j}^i|s_t,a_{t,<j}^i)}\hat A_{i},\nonumber \\ &\text{clip}\Bigg(\frac{\pi_\theta(a_{t,j}^i|s_t,a_{t,<j}^i)}{\pi_{\theta_{old}}(a_{t,j}^i|s_t,a_{t,<j}^i)},1-\epsilon,1+\epsilon\Bigg)\hat A_{i}\Bigg) \Bigg]
$$

## 技术点深读（DEEP）

![[deep/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl.txt`（66936 字符）供引用检索。