---
paper_num: "11"
title: "KIMI K2.5: VISUAL AGENTIC INTELLIGENCE"
authors: ""
date: "2026/2/1"
arxiv: "https://arxiv.org/abs/2602.02276"
pdf: "papers/kimi-k2-5-visual-agentic-intelligence.pdf"
slug: "kimi-k2-5-visual-agentic-intelligence"
tags: [multimodal]
---

# KIMI K2.5: VISUAL AGENTIC INTELLIGENCE

> [!abstract] 摘要（原文）
> 1\. 🚀 Kimi K2.5 是一款开源多模态智能体模型，通过联合优化文本与视觉预训练以及强化学习，实现了跨模态能力的双向增强与对齐。 2. 🤖 该模型引入了 Agent Swarm 框架，通过动态任务分解和并行子智能体调度，在保持高推理精度的同时，显著降低了处理复杂任务的延迟。 3. 📈 大量评测结果表明，Kimi K2.5 在编程、多模态视觉推理、长视频理解及复杂智能体任务中均达到了行业领先水平，为通用智能体智能的发展提供了有力支持。

## 元信息
- **发表日期**: 2026/2/1
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2602.02276
- **本地 PDF**: `papers/kimi-k2-5-visual-agentic-intelligence.pdf`
- **页数**: 30

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig01.png]]
*整页渲染: ![[assets/kimi-k2-5-visual-agentic-intelligence-p01.png]]*
> [!quote] caption
> Kimi K2.5 main results. 1

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图1以四组共10项基准对比 Kimi K2.5 与 GPT-5.2 (xhigh)、Claude Opus 4.5、Gemini 3 Pro：**Agents** 三项（Humanity's Last Exam 50.2、BrowseComp 74.9、DeepSearchQA 77.1）、**Coding** 两项（SWE-bench Verified 76.8、Multilingual 73.0）、**Image** 三项（MMMU Pro 78.5、MathVision 84.2、OmniDocBench 1.5 88.8）、**Video** 两项（VideoMMMU 86.6、LongVideoBench 79.8）。

关键论证：Kimi K2.5 在 **Agents 类别 3/3 全胜**（BrowseComp 超第二名 9.1 分），Video 与 Image 多项夺冠，量化支撑其"visual-agentic intelligence"核心卖点；在 SWE-bench Verified（76.8 vs Claude 80.9）上略弱，提示 Coding 仍有提升空间。

论文作用：作为首页总览图，锚定 Table 1 联合训练消融基线，并以横向对标建立"全能型 agentic 模型"定位。

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig02.png]]
*整页渲染: ![[assets/kimi-k2-5-visual-agentic-intelligence-p04.png]]*
> [!quote] caption
> Vision RL training curves on vision benchmarks starting from minimal zero-vision SFT. By scaling vision RL FLOPs, the performance continues to improve, demonstrating that zero-vision activation paired with long-running RL is sufficient for acquiring robust visual capabilities.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**核心数据**：图含两条以 RL FLOPs 为横轴、Accuracy 为纵轴的训练曲线。左图（MMMU Pro，粉线）从基线 ~0.713 持续爬升至 ~0.755–0.760；右图（绿色，另一视觉基准）从 ~0.698 攀升至 ~0.78，两条虚线分别标注起止水平。两条曲线均呈单调上升趋势，验证随 RL 计算量扩展性能持续改善。

2）**关键结论**：在仅经过极少量"zero-vision SFT"的起点上，仅依靠长程视觉 RL 即可获得稳健视觉能力——视觉涌现无需依赖大规模视觉 SFT，RL FLOPs 本身是性能提升的关键杠杆。

3）**论文作用**：作为核心实证证据，支撑全文"zero-vision activation + 长程 RL" 的方法论主张，并与 Table 2 的跨模态迁移结果形成"视觉能力—文本能力同源提升"的互补论证，构成 K2.5 视觉智能后训练范式的关键一环。

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig03.png]]
*整页渲染: ![[assets/kimi-k2-5-visual-agentic-intelligence-p05.png]]*
> [!quote] caption
> An agent swarm has a trainable orchestrator that dynamically creates specialized frozen subagents and decomposes complex tasks into parallelizable subtasks for efficient distributed execution.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示 Agent Swarm 系统架构。**核心对象**：左侧为可训练 Orchestrator，配备 create_subagent、assign_task、search、browser 等工具；右侧为动态生成的约 6 类冻结子智能体（AI / Physics / Life Sciences / Anthropology Researcher、Fact Checker、Web Developer），每个内置搜索与浏览工具。**结构与数据**：Orchestrator 先执行"create subagents"并收到 success 回执，再分两批"Assign Tasks"——首批拆为 100 个子任务（4×AI Researcher + 1×Physics + 4×Life Sciences + 1×Anthropology），次批 25 个（2×Fact Checker + 1×File Downloader + ... + Web Developer），各子智能体并行完成后逐一回传 task N result，最终聚合为 Final Results。**论证结论**：可训练 Orchestrator 通过"动态创建专用子智能体 + 任务并行分解 + 结果汇聚"实现复杂任务的分布式高效执行。**论文作用**：该图是 Kimi K2.5 方法链路的架构骨架，定义了"一个训练中枢 + 多个冻结专家"的协同范式，为后续能力扩展与实验评测提供框架基础。

### Figure 4 (p.6) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig04.png]]
*整页渲染: ![[assets/kimi-k2-5-visual-agentic-intelligence-p06.png]]*
> [!quote] caption
> In our parallel-agent reinforcement learning environment, the training accuracy increases smoothly as train- ing progresses. At the same time, the level of parallelism during training also gradually increases. many subagents without meaningful task decomposition. By rewarding completed subtasks, r finish enforces feasibility and guides the policy toward valid and effective decompositions.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图4联合解读**

该图由左右两幅散点+平滑曲线图构成，横轴均为 RL flops。左图"Training Accuracy vs Steps"显示训练准确率从约 36% 单调平稳上升至约 63%；右图"Average parallelism vs Steps"显示平均并行度先在 8 附近小幅波动、中段保持平稳，后期急剧攀升至约 14。

原文借此论证：在并行智能体 RL 环境中，对已完成子任务施加 r_finish 奖励，既能持续提升任务完成准确率，又能驱动策略学到更深入、有意义的任务分解（并行度上升），从而避免"无意义切分多个子代理"的退化解。

在论文整体链路中，该图作为方法有效性证据，支撑第6页关于"奖励机制引导有效分解"的核心论点，为后续 Table 4 的 SOTA 结果提供训练动态层面的合理化解释。

### Figure 5 (p.10) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig05.png]]
*整页渲染: ![[assets/kimi-k2-5-visual-agentic-intelligence-p10.png]]*
> [!quote] caption
> Comparison of model performance and token usage for Kimi K2 Thinking following token-efficient RL. compromise alleviates memory pressure, it does not fundamentally resolve the load imbalance caused by multimodal input sizes. More critically, it precludes the direct reuse of parallel strategies that have been highly optimized for text-only training.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（≤220字）：**

图示双雷达图对比Kimi K2 Thinking在token-efficient RL前后于7项基准（含HMMT25系列、AIME2025、GPQADIAMOND、LiveCodeBenchV6、MMLUPro及Overall）上的表现。

**左图（性能）**：5升2降——LiveCodeBenchV6 +2.2%、AIME2025 +1.1%、HMMT25_Nov +0.8%、Overall +0.3%为正向；MMLUPro −2.0%、GPQADIAMOND −1.0%为退化。**右图（token消耗）**：7项全部下降，幅度−817至−8127，Overall削减−4791，无任何一项增长。

论文据此论证：token-efficient RL可在几乎不损伤（仅2项小幅退化）的前提下系统压缩输出token，实现推理效率与能力兼得。该图是支撑K2 Thinking"可控思考预算"训练范式的核心定量实证，并为Table 5的横向对比提供方法学锚点。

### Figure 6 (p.14) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig06.png]]
*整页渲染: ![[assets/kimi-k2-5-visual-agentic-intelligence-p14.png]]*
> [!quote] caption
> The word cloud visualizes heterogeneous K2.5-based sub-agents dynamically instantiated by the

> [!tip] 技术解读（多模态）
> 【图文联合解读】**说明**：所给图片实为 **Table 6（性能对比表）**，而非 Figure 6 的词云。图 6 词云本身未呈现，以下基于表格内容做联合解读。

**核心数据**：在三个 agentic 搜索基准上，K2.5 Agent Swarm 均居首位——BrowseComp 78.4（vs Kimi K2.5 60.6、Claude Opus 4.5 37.0、GPT-5.2 65.8、GPT-5.2 Pro 77.9）、WideSearch 79.0（vs 72.7/76.2）、自建 Swarm Bench 58.3（vs 41.6/45.8）；其中在 Swarm 专用基准上领先优势最大（+16.7 vs K2.5）。

**论证结论**：Orchestrator 动态实例化的异构子代理（即图 6 词云所可视化的能力分布）确实转化为可量化的检索增益；多代理编排显著优于单模型，验证了 Swarm 架构的有效性。

**论文作用**：作为方法链路下游的关键实验证据，证明 K2.5 Agent Swarm 在 agentic 任务上同时超越开源单模型与闭源商业基线，支撑"动态编排+异构子代理"的核心贡献。

### Figure 7 (p.14) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig07.png]]
*整页渲染: ![[assets/kimi-k2-5-visual-agentic-intelligence-p14.png]]*
> [!quote] caption
> Comparison of Kimi K2.5 performance un- der Agent Swarm and Discard-all context management in BrowseComp. (60.6%) and surpassing even GPT-5.2 Pro (77.9%). Similarly, WideSearch sees a 6.3% improvement (72.7% → 79.0%) on Item-F1, enabling K2.5 Agent Swarm to outperform Claude Opus 4.5 (76.2%) and establish a new state- of-the-art. The gains are most pronounced on In-house Swarm bench (16.7%), where

> [!tip] 技术解读（多模态）
> 【图文联合解读】图7以三行三基准对比K2.5 Agent Swarm与Discard-all版K2.5及主流闭源模型得分：BrowseComp 78.4 vs 60.6（+17.8），超GPT-5.2 Pro（77.9）；WideSearch 79.0 vs 72.7（+6.3），超Claude Opus 4.5（76.2）；自研Swarm Bench 58.3 vs 41.6（+16.7），亦超Claude（45.8）。核心结论为Agent Swarm上下文管理相对Discard-all带来稳定且显著的全面增益，使其在三项任务上均超越顶级闭源对手。在论文链路中，该图作为关键消融/对比证据，定量证明Swarm多智能体架构与上下文管理是K2.5刷新SOTA的核心机制驱动。

### Figure 8 (p.15) ⭐深度解读
![[assets/kimi-k2-5-visual-agentic-intelligence-p15.png]]
> [!quote] caption
> Agent Swarm achieves 3×–4.5× faster execution time compared to single-agent baselines as target Item-F1 increases from 30% to 70% in WideSearch testing. rather than context truncation, allowing the system to scale effective context length along an additional architectural dimension while preserving modularity, information locality, and reasoning integrity.

> [!tip] 技术解读（多模态）
> # Figure Description

**Note:** The figure graphic itself is not rendered on this page — only the caption and surrounding text are visible. The following description is inferred from the caption and page context.

**Architecture/Components/Data Flow (inferred from caption):**
- **X-axis:** Target Item-F1 (information coverage/quality metric), ranging from 30% → 70%
- **Y-axis:** Execution time (latency)
- **Two curves compared:**
  - Agent Swarm (multi-agent parallel orchestration)
  - Single-agent baseline (sequential execution)
- **Benchmark:** WideSearch — a wide-scope search/retrieval task

**Key Technical Takeaway (≤120 words):**
The figure demonstrates that Kimi K2.5's Agent Swarm delivers a **3×–4.5× latency reduction** over single-agent baselines on the WideSearch benchmark, with the speedup *widening* as task complexity (target Item-F1) increases from 30% to 70%. This means parallel sub-agent orchestration scales favorably with task difficulty — the harder and broader the search, the more Agent Swarm outperforms sequential execution. The result validates the system's design choice of concurrent execution of heterogeneous sub-tasks with selective context persistence, enabling lower inference latency without sacrificing answer completeness on complex agentic workloads.

---

# Caption Verbatim Transcription

> **Figure 8:** Agent Swarm achieves 3 –4.5 faster execution time compared to single-agent baselines as target Item-F1 increases from 30% to 70% in WideSearch testing.

### Figure 9 (p.21) ⭐深度解读
![[assets/kimi-k2-5-visual-agentic-intelligence-p21.png]]
> [!quote] caption
> Learning curves comparing vision-to-text ratios (10:90, 20:80, 50:50) under fixed vision-text token budget across vision and language tasks. Early fusion with lower vision ratios tend to yield better results. B

> [!tip] 技术解读（多模态）
> # Figure 9 Description

**Architecture/Components/Data Flow:**
The figure displays learning curves (loss/accuracy vs. training steps) plotted on a Cartesian grid for three vision-to-text token ratio configurations—**10:90, 20:80, and 50:50**—under a *fixed* overall vision-text token budget. The x-axis represents training progression (steps/tokens consumed), while the y-axis tracks task performance, with separate curves likely shown for vision tasks, language tasks, and joint bi-modal benchmarks. Three colored lines distinguish the ratios, enabling visual comparison of convergence speed, asymptotic performance, and training stability across ratios.

**Key Technical Takeaway (≤120 words):**
Early fusion combined with **lower vision ratios (e.g., 10:90 or 20:80)** yields superior convergence and bi-modal competence compared to the 50:50 configuration. Higher vision ratios cause a "dip-and-recover" pattern, where text capability degrades mid-training before recovering, indicating a modality domain shift. Co-optimizing vision and language from the outset enables smoother gradient landscapes and prevents representation collapse, reinforcing that native multimodal pre-training with moderate vision weight achieves more robust cross-modal alignment under fixed token budgets.

---

**Caption (verbatim):**
> Figure 9: Learning curves comparing vision-to-text ratios (10:90, 20:80, 50:50) under **fixed** vision-text token budget across vision and language tasks. Early fusion with lower vision ratios tend to yield better results.

### Figure 10 (p.23) ⭐深度解读
![[assets/kimi-k2-5-visual-agentic-intelligence-p23.png]]
> [!quote] caption
> Overview of our agentic RL framework. environments with minimal overhead. Our design prioritizes compositional modularity by integrating a suite of plug- gable components, such as a Tolset module for supporting various tools with sandboxes, a Judge module for multi- faceted reward signals, and specialized modules for prompt diversification and instruction-following enhancement.

> [!tip] 技术解读（多模态）
> # Figure 10: Overview of Agentic RL Framework

**Architecture/Components & Data Flow:**

The figure depicts a modular agentic RL training framework organized around a central **Rollout Manager** that orchestrates up to ~100,000 concurrent agent tasks as independent asynchronous coroutines. Each task acquires an environment instance from a managed pool (equipped with sandbox and specialized tools) and recursively triggers sub-task rollouts, enabling multi-agent paradigms and partial rollouts.

The framework is built from composable, pluggable modules wrapping the core agent loop:
- **Tool/Sandbox module** — heterogeneous tool execution with sandboxing
- **Reward module** — multi-faceted reward signal composition
- **Prompt diversification module** — prompt variation
- **Instruction-following module** — instruction adherence enhancement

Inference engine outputs flow back through a **train-inference co-design** layer that records log-probabilities for mismatch correction, with a proxy service bridging black-box LLM-API environments into the custom protocol.

**Key Technical Takeaway:**
The core innovation is treating every agent task as an independent async coroutine with a **dedicated Rollout Manager**, enabling 100,000-way concurrency, recursive sub-task rollouts, and partial rollout control — making complex multi-agent training tractable while keeping sandboxing, reward composition, and prompt diversification as orthogonal, pluggable modules.

---

**Caption (verbatim):**

> Figure 10: Overview of our agentic RL framework.

### Figure 11 (p.28) ⭐深度解读
![[assets/kimi-k2-5-visual-agentic-intelligence-p28.png]]
> [!quote] caption
> Qualitative example of Kimi K2.5 analyzing a complete playthrough of Black Myth: Wukong (24 hours of continuous gameplay across 32 videos at 1080p) using parallel visual agents. See generated webpage and source videos (all rights reserved by source authors). 28

> [!tip] 技术解读（多模态）
> **Description of the figure area:**

The figure content itself is not rendered/visible in this image — the main body of the page appears as blank white space, suggesting the qualitative example (likely screenshots/frames of a gameplay playthrough) failed to load or is missing. No architecture, components, or data flow diagrams are visible to describe.

**Key takeaway from caption:** Kimi K2.5 uses parallel visual agents to analyze long-form, high-resolution video (32 videos at 1080p) — demonstrating multi-hour video understanding via parallelization rather than sequential frame processing.

**Caption (verbatim):**

> Figure 11: Qualitative example of Kimi K2.5 analyzing a complete playthrough of [overlapping/unreadable characters] 24 hours of continuous gameplay across 32 videos at 1080p using parallel visual agents. See generated webpage and source videos (all rights reserved by source authors).

*Note: There is visible text-overlap/garbling near "playthrough of " in the original PDF rendering (e.g., characters resembling "𝒢𝒰𝒱𝓏𝓊") where an inline object/image collides with the caption text, making one word illegible.*

### Figure 12 (p.29) ⭐深度解读
![[assets/kimi-k2-5-visual-agentic-intelligence-p29.png]]
> [!quote] caption
> Qualitative examples of Kimi K2.5 solving visual reasoning tasks via tool use. 29

> [!tip] 技术解读（多模态）
> # Figure Description

**Note:** The figure body on this page appears blank/unrendered — only the caption is visible at the bottom. The page is otherwise empty white space.

**What should be present (based on caption):**
- **Type:** Qualitative examples (presumably a multi-panel figure)
- **Subject:** Kimi K2.5 performing visual reasoning tasks
- **Mechanism:** "via tool use" — implying the model invokes external tools (e.g., code execution, image manipulation, object detection, geometric calculators) rather than answering purely from internal perception
- **Implied data flow:** Visual input → model perception → tool selection → tool execution → result integration → reasoning output

**Key technical takeaway (≤120 words):**
Kimi K2.5 augments its native visual perception with **external tool calls** to solve visual reasoning tasks. Rather than relying solely on a vision encoder's internal representation, the model decomposes problems, invokes specialized tools (code, analysis modules, etc.), and integrates the results into its chain of thought. This agentic vision approach extends the model's capabilities beyond what fixed-resolution visual tokens alone can support, enabling more accurate, verifiable, and compositional visual reasoning.

---

**Caption (verbatim):**
> Figure 12: Qualitative examples of Kimi K2.5 solving visual reasoning tasks via tool use.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.3) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-tab01.png]]
> [!quote] caption
> Performance comparison across different vision-text joint-training strategies. Early fusion with a lower vision ratio yields better results given a fixed total vision-text token budget.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表比较固定视觉—文本总 token 预算下早期、中期、晚期视觉注入：注入点为0%、50%、80%，视觉/文本比为10/90%、20/80%、50/50%。早期方案在视觉知识、视觉推理、OCR、文本知识、代码上分别得25.8、43.8、65.7、45.5、24.8，除文本推理外整体优于中晚期（文本推理中期58.6，略高早期58.5）。该表作为训练策略消融，验证尽早、较低视觉占比融合更优，并为后续主模型确定训练配置。

### Table 2 (p.4) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-tab02.png]]
> [!quote] caption
> Cross-Modal Transfer: Vision RL Improves Textual Knowledge Benchmark Before Vision-RL After Vision-RL Improvement

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表对比三个纯文本基准在视觉RL前后的表现：MMLU-Pro 84.7→86.4（+1.7），GPQA-Diamond 84.3→86.4（+2.1），LongBench v2 56.7→58.9（+2.2）。核心结论：在视觉任务上做RL反向提升了文本知识能力，揭示视觉—语言间的正向跨模态迁移效应。与Figure 2（视觉能力随RL FLOPs增长）互补，共同支撑"零视觉SFT叠加长程视觉RL"的有效性——收益不仅体现于视觉基准，亦外溢至纯文本知识。

### Table 3 (p.6) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-tab03.png]]
> [!quote] caption
> Overview of training stages: data composition, token volumes, sequence lengths, and trainable components.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明：所提供图片实际为论文第6页正文（含"Prompt Construction for Parallel-agent Capability Induction"段落及§4.1 "Foundation: Kimi K2 Base Model"），并非Table 3本体。Table 3实际位于第7页。以下仅依据caption与上下文推断解读。**

**Table 3 联合解读：**

1）**核心对象与结构**：表格纵列四个维度——训练阶段、数据组成、token总量、序列长度、可训练组件；横向对照SFT/RL等阶段，体现由基础模型（Kimi K2：1.04T总参/32B激活，15T预训练token）到后训练的演进。

2）**关键技术结论**：原文据其论证——基础能力来自万亿级MoE预训练，后训练阶段通过可控token量级与序列长度配置，对orchestrator进行视觉-智能体能力的渐进注入，同时冻结sub-agent以稳定分布式执行。

3）**论文链路作用**：承接§4.1基础模型说明，向下衔接"parallel-agent capability induction"的提示构造与训练流水线，是方法章中连接foundation与agent swarm训练的关键资源配置总览表。

### Table 4 (p.12) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-tab04.png]]
> [!quote] caption
> Performance comparison of Kimi K2.5 against open-source and proprietary models. Bold denotes the global SOTA; Data points marked with * are taken from our internal evaluations. † refers to their scores of text-only subset.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**1) 表格结构与数据**
该表横向对比 K2.5 与 5 个模型（Claude Opus 4.5、GPT-5.2 xhigh、Gemini 3 Pro、DeepSeek-V3.2、Qwen3-VL-235B）在 4 类 30 余项基准的成绩，加粗为全球 SOTA。K2.5 多项领先：数学 AIME 96.1、HMMT 95.4、GPQA-Diamond 87.6；Agentic BrowseComp 60.6→(w/ctx)74.9→(Swarm)78.4、WideSearch(Swarm) 79.0、Seal-0 57.4；图像 OCRBench 92.3、InfoVQA 92.6、WorldVQA 46.3、MathVista 90.1。

**2) 原文论证的关键结论**
(1) K2.5 与头部闭源持平或领先；(2) 仅 K2.5 报告的 Agent Swarm 列（BrowseComp 78.4、WideSearch 79.0）直接验证"并行智能体 RL"对长程浏览/搜索的提升；(3) 图像多任务领先证明多模态联合训练有效。

**3) 在论文中的作用**
作为主实验表，承接 Figure 4 的并行 RL 设计，在通用/智能体/视觉三维度系统验证方法有效性，支撑 K2.5 为全面型 agentic-visual 模型的最终结论。

### Table 5 (p.13) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-tab05.png]]
> [!quote] caption
> Performance and token efficiency of some reasoning models. Average output token counts (in thousands) are shown in parentheses.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表5核心对象**：横向对比 Kimi K2.5（token-efficient RL 后）、Kimi K2 Thinking、Gemini-3.0 Pro、DeepSeek-V3.2 Thinking 在 7 项推理基准（AIME 2025、HMMT Feb/Nov 2025、IMO-AnswerBench、LiveCodeBench、GPQA Diamond、HLE-Text）上的得分与括号内平均输出 token 数（千）。

**关键数据**：K2.5 在 AIME 2025（96.1,25k）、HMMT Feb 2025（95.4,27k）、HLE-Text（31.5,24k）等 6/7 项以更少 tokens 击败原版 K2 Thinking（如 94.5,30k）；相较 Gemini-3.0 Pro，token 略多 2–10k，但在 AIME 2025、HLE-Text 准确率反超；同时全面领先 DeepSeek-V3.2 Thinking。

**技术结论**：token-efficient RL 在不损失甚至提升准确率前提下压缩 15–30% 输出长度，实现性能—效率兼得。

**论文作用**：作为 Figure 5 的姊妹实证，在方法链末端验证 token 经济性主张，回应"长 CoT 部署成本高"的隐忧。

### Table 6 (p.14) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-tab06.png]]
> [!quote] caption
> Performance comparison of Kimi K2.5 Agent Swarm against single-agent and proprietary baselines on agentic search benchmarks. Bold denotes the best result per benchmark.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读（Table 6）**

**核心数据**：在三个智能体搜索基准上对比 K2.5 Agent Swarm 与单智能体基线（Kimi K2.5）及专有模型（Claude Opus 4.5、GPT-5.2、GPT-5.2 Pro）：BrowseComp 78.4 vs 60.6 / 37.0 / 65.8 / 77.9；WideSearch 79.0 vs 72.7 / 76.2（GPT 列缺测）；In-house Swarm Bench 58.3 vs 41.6 / 45.8（GPT 列缺测）。三个最高分（粗体）全部归于 K2.5 Agent Swarm。

**关键结论**：Agent Swarm 在所有基准上同时超越单智能体 K2.5 与最强专有基线（BrowseComp 略胜 GPT-5.2 Pro，WideSearch/In-house 大幅领先 Claude Opus 4.5），论证了多智能体协同相对单体推理与闭源前沿模型的结构性优势。

**论文作用**：作为第 14 页核心定量证据，与 Figure 6（异构子智能体词云）共同支撑"K2.5 通过动态多智能体编排获得 agentic intelligence"的方法论主张，闭环全文"视觉智能体"主题。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathrm{budget}(x) = \text{Percentile}\left(\{ |y_j| \mid r(x, y_i) = 1, i=1,\dots, K \}, \rho \right) \,.
$$

$$
r_{\mathrm{PARL}}(x, y) = \lambda_1 \cdot \mspace{-26mu} \underbrace{r_{\text{parallel}}}_{\text{instantiation reward}} \mspace{-9mu} + \mspace{18mu}\lambda_2 \cdot \mspace{-32mu}\underbrace{r_{\text{finish}}}_{\text{sub-agent finish rate}} + \underbrace{r_{\text{perf}}(x, y)}_{\text{task-level outcome}} \, .
$$

$$
\text{CriticalSteps} = \sum_{t=1}^{T} \left( S_{\mathrm{main}}^{(t)} + \max_i S_{\mathrm{sub}, i}^{(t)} \right).
$$

$$
L_{\mathrm{RL}}(\theta) = \mathbb{E}_{x \sim\mathcal{D}} \left[ \frac{1}{N} \sum_{j=1}^K \sum_{i=1}^{|y_j|} \mathrm{Clip} \left( \frac{\pi_{\theta}(y_j^i | x, y_j^{0:i})}{\pi_{\mathrm{old}}(y_j^i | x, y_j^{0:i}) }, \alpha, \beta \right) ({r}(x, y_j) - \bar{r}(x))- \tau \left( \log \frac{\pi_{\theta}(y_j^i | x, y_j^{0:i})}{\pi_{\mathrm{old}}(y_j^i | x, y_j^{0:i}) } \right)^2 \right] \, .
$$

$$
\tilde{r}(x,y) = \begin{cases} r(x, y) \cdot \mathbb{I}\left\{ \frac{1}{K} \sum_{i=1}^K r(x, y_i) < \lambda\ \mathrm{or}\ |y_i| \leq \mathrm{budget(x)} \right\} & \text{if } \lfloor t/m \rfloor \pmod 2 = 0\ (\mathrm{{Phase 0}}) \\ r(x, y) & \text{if } \lfloor t/m \rfloor \pmod 2 = 1\ (\mathrm{{Phase 1}}) \end{cases} \, .
$$

## 相关论文

- [[kimi-vl-technical-report]] — KIMI-VL TECHNICAL REPORT
- [[qwen2-5-vl-technical-report]] — Qwen2.5-VL Technical Report
- [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] — DeepStack: Deeply Stacking Visual Tokens is Surprisingly Simple and Effective for LMMs
- [[qwen3-vl-technical-report]] — Qwen3-VL Technical Report
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation

## 技术点深读（DEEP）

![[deep/kimi-k2-5-visual-agentic-intelligence]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/kimi-k2-5-visual-agentic-intelligence.txt`（95693 字符）供引用检索。