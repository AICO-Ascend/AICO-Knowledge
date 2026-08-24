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
> 【图文联合解读】## Figure 1 图文联合解读

**1) 核心对象与数据：**
该图为多面板条形图，对比 Kimi K2.5（蓝色 K 标）与 Claude Opus 4.5、Gemini 3 Pro 及另两款模型在四大类基准上的得分：
- **Coding – SWE-bench Verified**：K2.5 = 76.8，其余为 80.0 / 80.9 / 76.2
- **Coding – SWE-bench Multilingual**：K2.5 = 73.0（最高），余为 72.0 / 77.5 / 65.0
- **Video – VideoMMBU**：K2.5 = 86.6（领先），余为 85.9 / 84.4 / 87.6
- **Video – LongVideoBench**：K2.5 = 79.8（大幅领先），余为 76.5 / 67.2 / 77.7
另有 SearchQA（76.1 vs 63.2）与视频类基准（87.7 vs 88.5）的局部对比。

**2) 关键论证结论：**
K2.5 在 **多语言代码修复**与**长/多模态视频理解**任务上取得 SOTA，在 SWE-bench Verified 上接近最优，证明其在视觉-智能体（coding + video）双线均具竞争力。

**3) 在论文中的作用：**
作为首页总览图，定量支撑论文核心卖点——"visual-agentic intelligence"，为后续 Table 1 的联合训练策略消融提供基线锚点。

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig02.png]]
*整页渲染: ![[assets/kimi-k2-5-visual-agentic-intelligence-p04.png]]*
> [!quote] caption
> Vision RL training curves on vision benchmarks starting from minimal zero-vision SFT. By scaling vision RL FLOPs, the performance continues to improve, demonstrating that zero-vision activation paired with long-running RL is sufficient for acquiring robust visual capabilities.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图2联合解读：**

**① 核心数据**：图含两条RL训练曲线。左图MMMU Pro（粉）起点≈0.71–0.72，随RL FLOPs攀升并逼近≈0.76虚线参考；右图（绿）起点≈0.69，最终稳定在≈0.78左右，基线虚线位于≈0.70。两条曲线均呈持续上升趋势并伴随明显振荡收敛。

**② 关键结论**：作者以"minimal zero-vision SFT"为起点，仅靠加大视觉RL算力即在两个基准上获得显著且单调的增益（MMMU Pro +4–5pp，右图 +8–9pp），证明无需预先大量视觉微调，长程RL即可"涌现"出鲁棒的视觉能力。

**③ 方法链路作用**：此图为全文核心证据——支撑"文本能力先于视觉激活、视觉能力由RL后激活获得"的设计哲学，与Table 2的跨模态迁移结果呼应，共同论证MoE+RL的后训练范式无需显式视觉SFT即可获得多模态智能。

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
> 【图文联合解读】**图4 图文联合解读**

图含左右两子图，横轴均为 RL flops。左图（Training Accuracy vs Steps）以散点+红色平滑曲线呈现训练准确率，由初始约 36% 平滑上升至末段约 64%；右图（Average Parallelism vs Steps）显示平均并行度：初期约 8.5、中段长期平稳徘徊于 7.5–9、后期加速攀升至约 14。

该图以双指标共演化论证两点核心结论：① 并行 Agent 强化学习训练过程平稳收敛、无发散崩溃，证明 r_finish 等奖励机制驱动的训练可行性；② 准确率与并行度同向增长，说明模型不仅"答对任务"，还主动学习提升任务分解的并行深度，回应了正文中"避免无意义切分过多子智能体"的设计目标——分解是有效而非冗余的。

在论文方法链中，该图承担 RL 后训练阶段"策略正确性 + 并行分解合理性"的双重实证支撑，为后续 agentic 能力评测提供训练可信度背书。

### Figure 5 (p.10) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig05.png]]
*整页渲染: ![[assets/kimi-k2-5-visual-agentic-intelligence-p10.png]]*
> [!quote] caption
> Comparison of model performance and token usage for Kimi K2 Thinking following token-efficient RL. compromise alleviates memory pressure, it does not fundamentally resolve the load imbalance caused by multimodal input sizes. More critically, it precludes the direct reuse of parallel strategies that have been highly optimized for text-only training.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **图表内容**：左雷达图为"Performance (%)"，覆盖 AIME2025、GPQADIAMOND、HMMT25_Feb/Nov、MMLUPro、LiveCodeBenchV6 及 Overall 共 7 个基准；Toggle 前（灰虚线）vs 后（蓝实线）显示 5 项提升（如 LiveCodeBenchV6 +2.2%、AIME2025 +1.1%）、2 项下降（GPQADIAMOND −1.0%、MMLUPro −2.0%），Overall +0.3%。右雷达图为"Token Usage"，7 项全部减少（绿标 0 增加），幅度 −745 至 −8127 tokens，Overall 节省 4791。

2) **关键结论**：token-efficient RL 在 7 个基准上**全部**显著降低 token 消耗，同时整体性能仅微涨 0.3%，证明"省 token 不损精度"。

3) **论文作用**：作为方法有效性的核心证据，支撑 Kimi K2 Thinking "降本保效"的核心卖点，为后续推理效率与多模态训练优化提供量化锚点。

### Figure 6 (p.14) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig06.png]]
*整页渲染: ![[assets/kimi-k2-5-visual-agentic-intelligence-p14.png]]*
> [!quote] caption
> The word cloud visualizes heterogeneous K2.5-based sub-agents dynamically instantiated by the

> [!tip] 技术解读（多模态）
> 【图文联合解读】**注意**：所提供图片实为一张性能对比表格，与caption所述"词云"不符，以下按图像实际内容解读。

该表横向比较K2.5 Agent Swarm、Kimi K2.5、Claude Opus 4.5、GPT-5.2、GPT-5.2 Pro在三项基准上的得分：BrowseComp为78.4/60.6/37.0/65.8/77.9；WideSearch为79.0/72.7/76.2/—/—；In-house Swarm Bench为58.3/41.6/45.8/—/—。

论证结论：Agent Swarm相对Kimi K2.5基座在BrowseComp提升17.8分、In-house Swarm Bench提升16.7分，且在BrowseComp以78.4超越GPT-5.2 Pro（77.9），证明Orchestrator动态调度多异构子代理的架构有效。

整体作用：作为论文方法链路的终点证据，量化呈现"Orchestrator+子代理群"框架相比单模型基座与同级前沿模型的综合优势。

### Figure 7 (p.14) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig07.png]]
*整页渲染: ![[assets/kimi-k2-5-visual-agentic-intelligence-p14.png]]*
> [!quote] caption
> Comparison of Kimi K2.5 performance un- der Agent Swarm and Discard-all context management in BrowseComp. (60.6%) and surpassing even GPT-5.2 Pro (77.9%). Similarly, WideSearch sees a 6.3% improvement (72.7% → 79.0%) on Item-F1, enabling K2.5 Agent Swarm to outperform Claude Opus 4.5 (76.2%) and establish a new state- of-the-art. The gains are most pronounced on In-house Swarm bench (16.7%), where

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图7实质为一张多基准成绩对比表**（caption仅提BrowseComp，但实际涵盖三项）：列依次为K2.5 Agent Swarm、K2.5 单代理基线（即Discard-all）、Claude Opus 4.5、GPT-5.2、GPT-5.2 Pro；行依次为 BrowseComp（78.4 / 60.6 / 37.0 / 65.8 / 77.9）、WideSearch（79.0 / 72.7 / 76.2 / — / —）、In-house Swarm Bench（58.3 / 41.6 / 45.8 / — / —）。

**技术结论**：Agent Swarm在三项基准上均大幅超越Discard-all基线——BrowseComp +17.8、WideSearch +6.3、Swarm +16.7，并在BrowseComp上反超GPT-5.2 Pro（77.9）、远超Claude Opus 4.5（37.0），印证"Orchestrator主动上下文分片优于被动压缩"。

**在论文中的作用**：作为核心实验证据，验证多代理编排方法相较单代理上下文管理的有效性，并完成K2.5与顶级闭源模型的横向定位。

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
> 【图文联合解读】**图像无法辨认**：裁图仅显示表标题与页眉"Kimi K2.5 Technical Report"，表格的具体行/列与数值未呈现，以下解读仅依据原文 caption。

**1) 核心对象**：该表对比多种"视觉-文本联合训练"策略（即不同的融合时机 early/late fusion 与视觉 token 占比配置），控制变量为"固定视觉-文本总 token 预算"，输出某项任务性能分数。

**2) 关键结论**：在总 token 预算一致时，采用**早融合（early fusion）**并**降低视觉 token 占比**的策略组合取得最佳结果，说明图文信息在浅层即交互、并为视觉让出更多文本容量，比后期拼接或高视觉占比更优。

**3) 论文作用**：作为消融依据，为 K2.5 选定"早融合 + 低视觉比例"的联合训练范式提供经验支撑，是其视觉能力接入主模型训练链路中的关键设计决策证据。

### Table 2 (p.4) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-tab02.png]]
> [!quote] caption
> Cross-Modal Transfer: Vision RL Improves Textual Knowledge Benchmark Before Vision-RL After Vision-RL Improvement

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读**

Table 2 对比 Vision-RL 前后三个文本基准表现：MMLU-Pro 84.7→86.4（+1.7）、GPQA-Diamond 84.3→86.4（+2.1）、LongBench v2 56.7→58.9（+2.2），均升 1.7–2.2 分。

该表论证关键结论：在最小化零视觉 SFT 启动后，长程视觉 RL 不仅获得视觉能力，还通过跨模态正向迁移，同步提升纯文本知识与长上下文理解，证伪"视觉训练损害语言能力"的传统担忧。

论文链路中，本表承接 Figure 2 对视觉能力随 RL FLOPs 持续增长的展示，将结论从单模态延伸到跨模态迁移维度，为作者"零视觉激活 + 长程视觉 RL"训练范式提供文本侧量化支撑，证明视觉与语言能力可协同增益。

### Table 3 (p.7) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-tab03.png]]
> [!quote] caption
> Overview of training stages: data composition, token volumes, sequence lengths, and trainable components.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

⚠️ 图片仅显示页眉"K Kimi K2.5 Technical Report"与 Table 3 的标题行，表格本体（各阶段的 Data、Tokens、Seq Len、Trainable 模块）未在截图中呈现，故具体数值无法从图像读取，以下解读依据标题语义与上下文推断。

**1) 核心对象与结构**
Table 3 以"训练阶段"为行，列出四列量化维度：数据组成（多模态/智能体任务配比）、训练 token 量级、上下文序列长度、可训练参数范围（冻结 vs 解冻）。它本质是一份"训练配方总览表"，把多阶段 pipeline 压缩为可对比的规格清单。

**2) 论证的关键技术结论**
通过对照各阶段 token 量与可训练组件占比，论文据此说明：智能体能力（如 Figure 3 中可训练的 orchestrator + 冻结子代理）并非靠堆通用预训练数据获得，而是依赖后期针对 agentic 轨迹的小规模、组件选择性训练。

**3) 在论文中的作用**
该表位于方法章节，向下衔接数据构造、训练策略与消融实验，是读者快速理解"视觉 + 智能体"能力来源的入口；同时为后续基准评测的能力归因提供训练侧解释依据。

### Table 4 (p.12) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-tab04.png]]
> [!quote] caption
> Performance comparison of Kimi K2.5 against open-source and proprietary models. Bold denotes the global SOTA; Data points marked with * are taken from our internal evaluations. † refers to their scores of text-only subset.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 4 将 Kimi K2.5 与 Claude Opus 4.5、GPT-5.2 (xhigh)、Gemini 3 Pro 等专有模型及 DeepSeek-V3.2、Qwen3-VL-235B-A22B 等开源模型，在推理/编码/智能体/图像四大类共 40 余基准上系统对比。K2.5 在智能体类全面领先：BrowseComp 60.6、BrowseComp (Agent Swarm) 78.4、WideSearch (Agent Swarm) 79.0 均为全球 SOTA；图像类 InfoVQA 92.6、CharXiv 77.5、编码 LiveCodeBench v6 85.0 亦夺冠。原文结合 Figure 4 论证：并行智能体 RL 训练中精度与并行度同步上升，"奖励完成子任务"机制引导策略学会有效任务分解。该表处于论文实验链终端，为"并行 RL→有效子任务分解→代理能力领先"核心论点提供量化证据。

### Table 5 (p.13) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-tab05.png]]
> [!quote] caption
> Performance and token efficiency of some reasoning models. Average output token counts (in thousands) are shown in parentheses.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 图文联合解读**

**1) 核心对象与数据**：Table 5 对比 Kimi K2.5、Kimi K2 Thinking、Gemini-3.0 Pro、DeepSeek-V3.2 Thinking 四款模型在 7 个推理基准（AIME 2025、HMMT Feb/Nov 2025、IMO-AnswerBench、LiveCodeBench、GPQA Diamond、HLE-Text）上的得分与平均输出 token（括号内，千计）。

**2) 关键技术结论**：Kimi K2.5 在全部 7 项任务上得分均高于 Kimi K2 Thinking，同时输出 token 显著更少（AIME：96.1/25k vs 94.5/30k；IMO：81.8/36k vs 78.6/37k；HLE-Text：31.5/24k vs 23.9/29k）。这定量证明 token-efficient RL 可同步实现性能提升与推理成本压缩。

**3) 论文链路作用**：与 Figure 5 互为表里，以数据支撑"K2.5 更高分、更少 token"的核心卖点，是论证 token-efficient RL 方法有效性的关键实验证据。

### Table 6 (p.14) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-tab06.png]]
> [!quote] caption
> Performance comparison of Kimi K2.5 Agent Swarm against single-agent and proprietary baselines on agentic search benchmarks. Bold denotes the best result per benchmark.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表6对比K2.5 Agent Swarm与单agent及专有基线在3项agentic search基准上的表现：BrowseComp 78.4（最高，>GPT-5.2 Pro 77.9）、WideSearch 79.0（最高，>Claude Opus 4.5 76.2）、In-house Swarm Bench 58.3（最高），三项均加粗领先。BrowseComp上较单agent K2.5（60.6）提升17.8分，内部Swarm Bench提升16.7分。该表作为核心实验证据，支撑Orchestrator动态调度异构子agent的Swarm范式同时优于单一推理与闭源强基线，是论文Agent Swarm方法主张的关键验证。

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