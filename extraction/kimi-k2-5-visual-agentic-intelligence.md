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
> ## Description of Figure 1

The figure is a grouped bar chart comparing Kimi K2.5 (blue) against three baselines — GPT‑5.2 (xhigh), Claude Opus 4.5, and Gemini 3 Pro (gray) — across ten benchmarks organized into four panels: **Agents** (Humanity's Last Exam, BrowseComp, DeepSearchQA), **Coding** (SWE‑bench Verified, SWE‑bench Multilingual), **Image** (MMMU Pro, MathVision, OmniDocBench 1.5), and **Video** (VideoMMMU, LongVideoBench). Each panel shows four bars per benchmark with numeric scores labeled above and model logos embedded in the bar tops. The y‑axis is percentile (%) accuracy, except OmniDocBench which uses a normalized Lévenshtein‑distance metric (higher = better).

**Key takeaway:** Kimi K2.5 dominates agentic benchmarks (e.g., 74.5 on BrowseComp vs. ≤60.6 for others) and achieves top scores in 7/10 tasks, with its largest margins in multi‑step agentic search — supporting the claim of joint text‑vision RL optimization and Agent Swarm's concurrent task decomposition.

## Caption (verbatim)

**Figure 1: Kimi K2.5 main results.**

### Figure 2 (p.4) ⭐深度解读
![[assets/kimi-k2-5-visual-agentic-intelligence-p04.png]]
> [!quote] caption
> Vision RL training curves on vision benchmarks starting from minimal zero-vision SFT. By scaling vision RL FLOPs, the performance continues to improve, demonstrating that zero-vision activation paired with long-running RL is sufficient for acquiring robust visual capabilities.

> [!tip] 技术解读（多模态）
> **Description (≈95 words):**

The figure presents two side-by-side line plots tracking vision RL training performance. The left panel (pink curve) shows MMMU Pro benchmark accuracy rising from ~0.71 to ~0.76 as RL flops scale up. The right panel (green curve) shows a second benchmark accuracy climbing from ~0.68 to ~0.78 with a similar upward trajectory. Both curves feature horizontal dashed baselines (likely upper-bound reference targets) and shaded confidence bands beneath the trajectories. The x-axis denotes RL FLOPs (compute scaling) while the y-axis shows accuracy.

**Key technical takeaway:** Visual capabilities can emerge from a minimal zero-vision SFT checkpoint purely through extended RL compute scaling—suggesting that RL FLOPs, not extensive vision pre-training, are the critical driver of robust visual acquisition.

**Caption (verbatim):**

> Figure 2: Vision RL training curves on vision benchmarks starting from minimal zero-vision SFT. By scaling vision RL FLOPs, the performance continues to improve, demonstrating that zero-vision activation paired with long-running RL is sufficient for acquiring robust visual capabilities.

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig03.png]]
*整页渲染: ![[assets/kimi-k2-5-visual-agentic-intelligence-p05.png]]*
> [!quote] caption
> An agent swarm has a trainable orchestrator that dynamically creates specialized frozen subagents and decomposes complex tasks into parallelizable subtasks for efficient distributed execution.

> [!tip] 技术解读（多模态）
> ## Figure Description

**Architecture/Components:** The diagram depicts a centralized **Orchestrator** (left, trainable) with tool access (`create_subagent`, `assign_task`, `search`, `browser`, …) that manages a swarm of **frozen subagents** (right), including AI Researcher, Physics Researcher, Life Sciences Researcher, Anthropology Researcher, Fact Checker, and Web Developer.

**Data Flow (three stages):**
1. **Create subagents** — Orchestrator instantiates specialized agents (each equipped with search/python/browser icons); a `success` signal returns.
2. **Assign Tasks** — Tasks are dispatched in parallel batches (e.g., AI Researcher Tasks 1–4, Physics Task 5, then Tasks 96–100 in a second wave; Fact Checker/File Downloader/Web Developer in another pool), with `task N result` streams flowing back.
3. **Final Results** — Aggregated output returned to caller.

**Key Technical Takeaway:** The orchestrator is **trainable while subagents remain frozen**, decoupling high-level coordination logic from low-level execution—this avoids end-to-end credit-assignment ambiguity and stabilizes RL training.

## Caption (verbatim)

> **Figure 3:** An agent swarm has a trainable orchestrator that dynamically creates specialized frozen subagents and decomposes complex tasks into parallelizable subtasks for efficient distributed execution.

### Figure 4 (p.6) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig04.png]]
*整页渲染: ![[assets/kimi-k2-5-visual-agentic-intelligence-p06.png]]*
> [!quote] caption
> In our parallel-agent reinforcement learning environment, the training accuracy increases smoothly as train- ing progresses. At the same time, the level of parallelism during training also gradually increases. many subagents without meaningful task decomposition. By rewarding completed subtasks, r finish enforces feasibility and guides the policy toward valid and effective decompositions.

> [!tip] 技术解读（多模态）
> **Figure Description & Technical Takeaway**

The figure (Figure 4) visualizes two co-evolving training metrics over the course of parallel-agent reinforcement learning: (1) **training accuracy** as the primary performance signal, and (2) the **level of parallelism** within the agent environment. Both curves trend upward together, plotted against training progress (likely steps/epochs on the x-axis, with accuracy and a parallelism measure as dual y-axes, or as overlaid normalized curves).

**Key takeaway:** Parallelism is not a fixed hyperparameter but an *emergent property* induced by training—accuracy and concurrency scale jointly, suggesting the orchestrator learns to decompose tasks into parallel subagents as a side effect of reward shaping rather than explicit instruction.

**Caption (verbatim):**

> Figure 4: In our parallel-agent reinforcement learning environment, the training accuracy increases smoothly as training progresses. At the same time, the level of parallelism during training also gradually increases.

### Figure 5 (p.10) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig05.png]]
*整页渲染: ![[assets/kimi-k2-5-visual-agentic-intelligence-p10.png]]*
> [!quote] caption
> Comparison of model performance and token usage for Kimi K2 Thinking following token-efficient RL. compromise alleviates memory pressure, it does not fundamentally resolve the load imbalance caused by multimodal input sizes. More critically, it precludes the direct reuse of parallel strategies that have been highly optimized for text-only training.

> [!tip] 技术解读（多模态）
> ## Figure Description

**Architecture/Components/Data Flow:** The figure is a two-panel comparative visualization titled "Token Efficiency before and after Toggle across Benchmarks." The left panel plots **Performance (%)** and the right panel plots **Token Usage**, each listing multiple benchmarks (e.g., AIME, GPQA, MMLU-Pro) along the x-axis. Data points are color-coded — gray for **Before Toggle** and orange/blue for **After Toggle** — allowing side-by-side comparison of model accuracy and compute cost.

**Key Technical Takeaway:** Despite the figure being redacted in this rendering, the surrounding text reveals that toggling **token-efficient RL** on Kimi K2 Thinking preserves (and in some cases slightly improves) benchmark performance while substantially reducing token usage — demonstrating that reasoning length can be compressed without sacrificing capability.

**Caption (verbatim):**
> Figure 5: Comparison of model performance and token usage for Kimi K2 Thinking following token-efficient RL.

### Figure 6 (p.14) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig06.png]]
*整页渲染: ![[assets/kimi-k2-5-visual-agentic-intelligence-p14.png]]*
> [!quote] caption
> The word cloud visualizes heterogeneous K2.5-based sub-agents dynamically instantiated by the

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

The main figure (Figure 7) is a performance comparison chart on the **BrowseComp** benchmark contrasting Kimi K2.5 under two context-handling regimes. Architecture/components depicted: (1) **Agent Swarm** pathway — central Orchestrator decomposes the query and dynamically instantiates specialized K2.5 sub-agents, each operating on a bounded local context, with only task-relevant outputs routed back; (2) **Discard-all** pathway — a reactive, single-agent baseline that periodically compresses/discards accumulated history. Data flow: query → orchestrator (or single agent) → sub-agent invocations → aggregated answer. **Key takeaway:** proactive context sharding via orchestrated sub-agents outperforms reactive history compression, indicating that explicit decomposition preserves task-relevant reasoning signal better than truncating the trajectory.

**Captions (verbatim):**

- *Figure 6:* "The word cloud visualizes heterogeneous K2.5-based sub-agents dynamically instantiated by the Orchestrator across tests."
- *Figure 7:* "Comparison of Kimi K2.5 performance under Agent Swarm and Discard-all context management in BrowseComp."

### Figure 7 (p.14) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig07.png]]
*整页渲染: ![[assets/kimi-k2-5-visual-agentic-intelligence-p14.png]]*
> [!quote] caption
> Comparison of Kimi K2.5 performance un- der Agent Swarm and Discard-all context management in BrowseComp. (60.6%) and surpassing even GPT-5.2 Pro (77.9%). Similarly, WideSearch sees a 6.3% improvement (72.7% → 79.0%) on Item-F1, enabling K2.5 Agent Swarm to outperform Claude Opus 4.5 (76.2%) and establish a new state- of-the-art. The gains are most pronounced on In-house Swarm bench (16.7%), where

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

The main figure (Figure 7) is a performance comparison chart on the **BrowseComp** benchmark contrasting Kimi K2.5 under two context-handling regimes. Architecture/components depicted: (1) **Agent Swarm** pathway — central Orchestrator decomposes the query and dynamically instantiates specialized K2.5 sub-agents, each operating on a bounded local context, with only task-relevant outputs routed back; (2) **Discard-all** pathway — a reactive, single-agent baseline that periodically compresses/discards accumulated history. Data flow: query → orchestrator (or single agent) → sub-agent invocations → aggregated answer. **Key takeaway:** proactive context sharding via orchestrated sub-agents outperforms reactive history compression, indicating that explicit decomposition preserves task-relevant reasoning signal better than truncating the trajectory.

**Captions (verbatim):**

- *Figure 6:* "The word cloud visualizes heterogeneous K2.5-based sub-agents dynamically instantiated by the Orchestrator across tests."
- *Figure 7:* "Comparison of Kimi K2.5 performance under Agent Swarm and Discard-all context management in BrowseComp."

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
> I'm unable to complete this request because **no figure is present in the image you provided**. The image only contains:

- A page header: "Kimi K2.5 — Technical Report"
- A caption labeled "Table 1" (text only — no chart, diagram, or visual element)

Without an actual architecture diagram, components, or data-flow illustration to examine, I cannot describe figures, modules, or data flow. If you intended to share a specific figure (e.g., the Moonshot Kimi K2.5 system architecture diagram), please re-upload that image.

---

### Verbatim transcription of the visible caption:

> **Table 1:** Performance comparison across different vision-text joint-training strategies. Early fusion with a lower vision ratio yields better results given a fixed total vision-text token budget.

If you can share the intended figure, I'll happily provide the requested description and key technical takeaway within the 120-word limit.

### Table 2 (p.4) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-tab02.png]]
> [!quote] caption
> Cross-Modal Transfer: Vision RL Improves Textual Knowledge Benchmark Before Vision-RL After Vision-RL Improvement

> [!tip] 表格解读（多模态）
> There is **no figure** on this page — it contains only Table 2 and body text. I cannot describe architecture, components, or data flow that aren't shown. Here is what the page actually contains, with the table title transcribed verbatim:

**Table title (verbatim):** "Table 2: Cross-Modal Transfer: Vision RL Improves Textual Knowledge"

**Table contents:**
| Benchmark | Before Vision-RL | After Vision-RL | Improvement |
|---|---|---|---|
| MMLU-Pro | 84.7 | 86.4 | +1.7 |
| GPQA-Diamond | 84.3 | 86.4 | +2.1 |
| LongBench v2 | 56.7 | 58.9 | +2.2 |

**Key technical takeaway (from the surrounding text, ≤120 words):** Outcome-based visual RL unexpectedly improves *text-only* benchmarks (MMLU-Pro +1.7, GPQA-Diamond +2.1, LongBench v2 +2.2), suggesting visual RL enhances calibration on queries resembling visually grounded reasoning (counting, OCR). Motivated by this, Kimi K2.5's post-training abandons modality-specific expert routing in favor of a **Joint Multimodal RL** paradigm: RL domains are organized by *ability* (knowledge, reasoning, coding, agentic) rather than input modality, and a shared Generative Reward Model (GRM) judges traces across both text and vision — enabling cross-modal transfer without capability degradation.

If you intended a different page containing an architecture/flow figure, please re-upload it.

### Table 3 (p.7) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-tab03.png]]
> [!quote] caption
> Overview of training stages: data composition, token volumes, sequence lengths, and trainable components.

> [!tip] 表格解读（多模态）
> I only have access to the header and a single caption from the document — not the underlying figure or table content itself. The page shared shows:

- **Header:** "K Kimi K2.5 — TECHNICAL REPORT"
- **Visible caption:** Table 3's caption

Since the actual table body (training stages, data composition, token volumes, sequence lengths, trainable components) and any architecture/data-flow figure are not included in the input, I cannot describe their structure, components, or flow.

**Transcribed caption verbatim:**

> **Table 3:** Overview of training stages: data composition, token volumes, sequence lengths, and trainable components.

If you can share the figure image or the table rows, I can produce the architecture/components/data-flow description plus the ≤120-word technical takeaway you asked for.

### Table 4 (p.12) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-tab04.png]]
> [!quote] caption
> Performance comparison of Kimi K2.5 against open-source and proprietary models. Bold denotes the global SOTA; Data points marked with * are taken from our internal evaluations. † refers to their scores of text-only subset.

> [!tip] 表格解读（多模态）
> **No figure provided.** The submitted content contains only a table caption (Table 4) from the Kimi K2.5 Technical Report, not a figure or diagram. Therefore, I cannot describe architecture, components, or data flow, as no architectural figure has been shared.

If you intended to attach a figure (e.g., a diagram of model architecture, training pipeline, or system components), please re-upload the image, and I will provide the requested description and verbatim caption transcription.

**What is present — caption of Table 4 (verbatim):**

> "Table 4: Performance comparison of Kimi K2.5 against open-source and proprietary models. Bold denotes the global SOTA; Data points marked with * are taken from our internal evaluations. ^† refers to their scores of text-only subset."

Please share the figure you would like analyzed, and I'll deliver a ≤120-word technical summary plus an exact caption transcription.

### Table 5 (p.13) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-tab05.png]]
> [!quote] caption
> Performance and token efficiency of some reasoning models. Average output token counts (in thousands) are shown in parentheses.

> [!tip] 表格解读（多模态）
> Looking at the provided image, I can only see a header banner and a table caption — **no main figure is present** in this image. The image contains text only:

**Header:** "Kimi K2.5 — TECHNICAL REPORT"

**Caption text (transcribed verbatim):**
> "Table 5: Performance and token efficiency of some reasoning models. Average output token counts (in thousands) are shown in parentheses."

**Technical takeaway (inferred from caption context, ≤120 words):**

Since no figure/table data is visible, the key insight derivable from the caption itself is:

> The figure compares reasoning models on **two axes** — task performance and **token efficiency** (output token count, reported in thousands in parentheses). The key takeaway for reasoning models is that **higher accuracy does not necessarily imply better efficiency**: a model can achieve competitive performance while generating substantially fewer output tokens, making token cost a critical second axis for evaluating reasoning systems alongside raw benchmarks. This dual metric helps identify Pareto-optimal reasoning models that balance capability with inference cost.

If you can share the actual Table 5 contents or the main figure you'd like analyzed, I can provide a more specific architecture/components/data-flow description.

### Table 6 (p.14) ⭐深度解读
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-tab06.png]]
> [!quote] caption
> Performance comparison of Kimi K2.5 Agent Swarm against single-agent and proprietary baselines on agentic search benchmarks. Bold denotes the best result per benchmark.

> [!tip] 表格解读（多模态）
> **Figure description (Table 6):**

*Structure & components:* A 5-column × 4-row benchmark table comparing five agentic search systems — **K2.5 Agent Swarm** (multi-agent), single-agent **Kimi K2.5**, **Claude Opus 4.5**, **GPT-5.2**, and **GPT-5.2 Pro** — evaluated on three benchmarks: BrowseComp, WideSearch, and In-house Swarm Bench. Bold entries mark per-benchmark winners.

*Data flow logic:* Each row reports a single accuracy score per system, enabling vertical comparison of swarm coordination gains vs. monolithic single-agent/proprietary baselines.

*Key technical takeaway:* Coordinated agent swarms dominate on challenging, broad-scope search (e.g., +17.8 over Claude Opus 4.5 on BrowseComp, 78.4), while matched-cost single-agent models remain competitive on narrow retrieval (WideSearch). Multi-agent decomposition appears to pay off most when queries exceed a single model's effective search horizon.

**Caption (verbatim):** *Table 6: Performance comparison of Kimi K2.5 Agent Swarm against single-agent and proprietary baselines on agentic search benchmarks. Bold denotes the best result per benchmark.*

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