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
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p01.png]]
> [!quote] caption
> Overview of the Agentic Learning Ecosystem (ALE) and ROME Performance. 1[cs.AI] 12 Mar 2026

> [!tip] 技术解读（多模态）
> **Architecture & Data Flow**
The figure presents the Agentic Learning Ecosystem (ALE) as a closed-loop, full-stack infrastructure. Three components interlock: **ROCK** (sandbox environment manager that generates executable trajectories), **iFlow CLI** (agent framework handling context engineering and environment interaction), and **ROLL** (scalable RL framework for multi-environment policy optimization). Data flows circularly: Instructions → iFlow → trajectories generated inside ROCK → consumed by ROLL → ROME model update → context/policy feedback returns to iFlow. A linear Task→Action→Execution→Feedback→Learning workflow underlies the loop.

**Key Technical Takeaway**
Empirical scaling is striking: ROME's accuracy climbs from 41.80% (initial) to 89.83% (peak) over training — a +47.07 absolute / +113.16% relative gain — while achieving 57.40% on SWE-bench Verified and 24.72% on Terminal-Bench 2.0, outperforming similarly-sized open models (100B parameters).

**Caption (verbatim):**
Figure 1: Overview of the Agentic Learning Ecosystem (ALE) and ROME Performance.

### Figure 2 (p.4) ⭐深度解读
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p04.png]]
> [!quote] caption
> The overview of agentic RL ecosystem (a) and its training pipeline (b). technical stack, ALE is also a call to reframe the community’s priorities. In complex agentic settings, the central challenge is no longer merely data scale or curation quality, but the co-design of training infrastructure, executable environments, and evaluation protocols. We hope this work catalyzes collaborative efforts tow

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The figure has two panels illustrating the **Agentic Learning Ecosystem (ALE)**:

**(a) Ecosystem architecture** — Two coupled subsystems. The left block, *ROLL* (RL training framework), contains an Actor-Train model whose weights are synced to an Actor-Infer model; an Env. Manager dispatches LLM Requests to multiple Env. Workers (each backed by Rock SDK) and collects LLM Responses/Training Data. The right block, *ROCK Sandbox* (execution engine), hosts the *iFlow CLI* agent framework and a ModelProxy Service that mediates Poll Request / LLM Request / Deliver Response traffic via Request and Response Queues. The two subsystems communicate over the Rock SDK interface.

**(b) RL training pipeline** — A closed loop: the *Rollout Stage* cycles Agentic LLM ↔ Environment through Action tokens and Observations, emitting Trajectory Data that drives the *Training Stage* (Weight Update), whose updated weights are synchronized back to rollout.

**Key takeaway:** Decoupling rollout environment execution (ROCK) from model training/inference (ROLL) — connected via queued ModelProxy RPCs — enables scalable, fault-tolerant, closed-loop agentic RL.

## Caption (verbatim)

Figure 2: The overview of agentic RL ecosystem (a) and its training pipeline (b).

(a) The overview of **A**gentic **L**earning **E**cosystem (**ALE**).
(b) Agentic RL training pipeline.

### Figure 3 (p.5) ⭐深度解读
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p05.png]]
> [!quote] caption
> ROLL Architecture. (a) ROLL pipelines LLM generation, environment interaction, and reward phases at trajectory-level granularity. Training is also decoupled via a sample buffer using an asyn- chronous ratio to manage staleness. (b) ROLL multiplexes a dynamic GPU pool by shrinking rollout resources for bursty training and expanding them back during demand peaks. coordinates heterogeneous workers an

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 3: ROLL Architecture):**

Figure 3 shows two complementary views of ROLL. **Panel (a)** illustrates fine-grained rollout and asynchronous training: a *Rollout System* (Queue Scheduler → LLM Proxy → Environment) produces training data that flows into a *Training System* (Sample Buffer → GPU/Train Worker). The *Async Control Logic* orchestrates Suspend→Update→Resume cycles for both rollout and training steps, with KV Cache Recompute. The LLM Engine diagram shows sample-level pipelining across GPU A/B, where trajectories (traj1–traj8) overlap generation with recompute. **Panel (b)** depicts Train–Rollout Multiplexing: GPUs (A–D) are dynamically Shrunk or Expanded between rollout and training stages based on the critical path, with KV Cache Recompute managing state.

**Key Technical Takeaway:** ROLL decouples generation/environment interaction/reward from training via a sample buffer and an *asynchronous ratio* (max allowable policy-version gap per sample), and dynamically reallocates GPUs to whichever stage (rollout vs. training) is the current bottleneck—minimizing idle time while bounding staleness.

**Caption (verbatim):**

Figure 3: ROLL Architecture. (a) ROLL pipelines LLM generation, environment interaction, and reward phases at trajectory-level granularity. Training is also decoupled via a sample buffer using an asynchronous ratio to manage staleness. (b) ROLL multiplexes a dynamic GPU pool by shrinking rollout resources for bursty training and expanding them back during demand peaks.

### Figure 4 (p.6) ⭐深度解读
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p06.png]]
> [!quote] caption
> ROCK System Architecture.

> [!tip] 技术解读（多模态）
> # Figure 4 Description

## Architecture / Components / Data Flow

**Central ROCK Service** is built around a client–server architecture with four core components:
- **Admin** (control plane): orchestrates sandboxes, admission control, cluster-wide scheduling
- **Worker** nodes: run sandbox runtimes and manage local hardware
- **Rocket** (lightweight proxy): mediates agent SDK ↔ sandbox traffic, governs egress policies
- **EnvHub** (central registry): stores environment images for reproducible provisioning

The figure highlights five supporting **Skills** arranged around the core:
1. **Streamlined SDK Control** — primitives (make/reset/step/close) mimic a local RL env
2. **Seamless Agent Scaling** — bridges to N heterogeneous agents (OpenHands, iFlow CLI, Mini Agent, SWE Agent)
3. **Native Agent Bridging** — `Agent Frame ↔ ROCK Model Server ↔ RL Frame` exchanging LLM Requests/Responses and Action/Observation
4. **Massive-Scale Scheduling** — manages 10,000+ concurrent sandbox environments (Success/Pending/Running states)
5. **Robust Fault Isolation** — quarantines failing containers without disrupting running ones

Data flows from external agent SDK → Rocket → Worker sandboxes → back as observations/rewards; Admin issues lifecycle and scheduling commands; EnvHub serves cached images to workers.

## Key Technical Takeaway

ROCK's central design insight is **decoupling sandbox execution from orchestration**: the lightweight Rocket proxy + Admin control plane lets thousands of heterogeneous agent environments be provisioned, scheduled, and fault-isolated independently, so concurrent rollouts remain stable and resource-efficient while exposing a simple `reset/step/close` API to any RL training framework.

## Caption (Verbatim)

> Figure 4: ROCK System Architecture.

### Figure 5 (p.8) ⭐深度解读
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p08.png]]
> [!quote] caption
> The overview of iFlow CLI architecture and execution. these requests already contain the complete historical context, fully orchestrated by the iFlow CLI. The proxy then forwards these requests to the appropriate inference service — be it ROLL inference workers during training or an external API (e.g., GPT, Gemini) during deployment. The native mode achieves a clean separation. ROLL is simplified 

> [!tip] 技术解读（多模态）
> **Figure Description (Architecture/Data Flow):**

The diagram illustrates iFlow CLI as an orchestrator-worker agent framework centered on a **Main Agent** that coordinates tools and context to plan/execute actions. Four peripheral modules surround it:

- **User Interface** (top-left): CLI Client, IDE Plugins, Web, SDK
- **Tool Suites** (top-right): File/System/Network/MCP/Task/Other Tools
- **Enhanced Capabilities** (bottom-left): Hooks (session-level interception), Skill-Based Workflows (reusable automation chains), Multi-Tiered Memory (user/project/global)
- **Context Management** (bottom-right): Compression, Retrieval, Enhancement, Isolation, Persistent Memory
- **Runtime Extensions**: Compress, Reminder, Detection, Env. Mgmt

**Data Flow:** The Main Agent invokes tools via a *Tool Call* and exchanges with Context Management via *Context Interaction*. Sub-agents are exposed as specialized tools with bounded context, eliminating inter-agent handoffs.

**Key Takeaway:** iFlow CLI achieves *separation of concerns* by isolating context management from the generation engine, ensuring perfect consistency between training and deployment while supporting multi-framework integration.

**Caption (verbatim):**
"Figure 5: The overview of iFlow CLI architecture and execution."

### Figure 6 (p.10) ⭐深度解读
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p10.png]]
> [!quote] caption
> Overview of data sources and composition pipelines for training agentic models, spanning code centric basic data and agentic data. 3

> [!tip] 技术解读（多模态）
> ## Figure 6 Description

The figure presents a **two-pillar data pipeline** for training agentic models:

**🟦 Code Centric Data (left, blue):**
- Source: *High-Quality Repo & PR* → *Crawl All Information* (Repo, Issue, Test, Code Patch, Discussion)
- Output: *Task-aware Data* — Localization, Repair, Unit Test Generation, Multi-turn Interaction, Code Reasoning

**🟨 Agentic Data (right, yellow) — four parallel streams:**
1. **Programming-Centric Data:** multi-agent loop (Explore → Task → Build Agent → Instance → Review → Quality → Behavior → Trajectory)
2. **General Tool Use Data:** Dialogue & API → Basic Data; Web → Interactive Data
3. **Safety Data:** Risk Knowledge → Inject Attack → Tiered Validation → Red Team Data
4. **Data Filtering pipeline:** Heuristic Filter → LLM-based Judge → Execution Simulator → Expert Inspection

**Data flow:** Both pillars converge into a unified training corpus, with filtering applied to ensure quality.

### Key Technical Takeaway
The architecture decouples **code-centric reasoning signals** (task-aware supervision from real repos/PRs) from **agentic interaction signals** (multi-agent trajectories, tool use, safety red-teaming). A multi-stage filter (heuristic + LLM judge + execution simulator + expert inspection) gates both streams, ensuring trajectory-quality alignment. This dual-pillar composition enables the ROME model to jointly master static code reasoning and dynamic workflow-driven agency.

### Figure 7 (p.16) ⭐深度解读
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p16.png]]
> [!quote] caption
> Overview of ROME’s Training Pipeline. incidents. Finally, we generated corresponding golden trajectories devoid of general-security issues for subsequent post-training (e.g., SFT and RL). Our overarching objective was to instill robust security awareness such that, when confronted with tasks containing latent security pitfalls, the agent reliably selected safe action paths and proactively avoided 

> [!tip] 技术解读（多模态）
> ## Description of Figure 7: ROME's Training Pipeline

The figure depicts a three-stage, left-to-right training pipeline:

**Stage 1 – Continuous Pre-Training (yellow):** A two-sub-stage curriculum trains on raw text and software-engineering traces. Sub-Stage I uses ~500B tokens of code/reasoning/tool-use data to instill atomic coding and reasoning skills; Sub-Stage II consumes ~300B tokens of agentic trajectories (File System, Web Shopping) to cultivate goal-maintenance and interaction capabilities, all optimized via next-token prediction.

**Stage 2 – Supervised Fine-Tuning (orange):** A 15/15/70 general/reasoning/agentic SFT mix is filtered through heuristic rules (overthinking, redundant tool calls, incomplete interactions, fake positives) and an LLM-as-Judge ranker (Sub-Stage I). Sub-Stage II refines the high-quality set using **error masking** (zero-out loss on failed/unrelated turns) and **context masking**, with adaptive data revisiting.

**Stage 3 – Agentic Reinforcement Learning (red):** Filtered instances (difficulty, environment stability, task misalignment) enter a Policy–Action–Environment loop optimized via **Interaction-Perceptive Agentic Policy Optimization (IPA)**. IPA extends REINFORCE with TOPR + token-level importance sampling, dynamic trajectory filtering, and a **Chunked MDP** formulation that rebuilds the objective (discounted chunk-level return, aligned importance sampling) and refines the rollout paradigm via crucial-chunk-initialized sampling.

**Key Takeaway:** ROME's pipeline is unified around *granularity-aware, failure-robust learning* — CPT bootstraps atomic→agentic skills, SFT suppresses noisy failure gradients through error/context masking, and IPA reframes RL over interaction chunks (rather than tokens) so credit assignment and importance sampling align with the agent's natural decision units.

## Caption (verbatim)

**Figure 7:** Overview of ROME's Training Pipeline.

### Figure 8 (p.20) ⭐深度解读
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p20.png]]
> [!quote] caption
> Overview of the Proposed Interaction-Perceptive Agentic Policy Optimization (IPA) training pipeline. sample efficiency(§3.2.4.4). An overview of our framework, including its key components and data flow, is depicted in Figure 8.

> [!tip] 技术解读（多模态）
> ## Figure Description

The figure (three panels) depicts the **IPA training pipeline**:

**Left panel — Chunk-Level Initialized Resampling:** A expert-like trajectory T* (chunks c*₁…c*ₜ) is split into multiple rollouts T⁽¹⁾ and T⁽²⁾ at the chunk level. Cross-rollout "Re-Sampling" arrows swap chunks, feeding **Imitation Learning** (early) and **Chunk-Level Optimization** (later) signals.

**Right-top panel — Chunk-Level Importance Sampling:** Computes a geometric-mean ratio ρ_c(c_i) comparing the Megatron training policy π_θ^megatron against the old Megatron policy μ_θ_old^megatron over a chunk, used to weight off-policy updates.

**Right-bottom panel — Inference-Training Mismatch Masking:** Builds a binary mask m_ε on the ratio against the SGLang inference policy μ_θ_old^SGLang, applied with the discounted chunk-level return γ to produce R(T⁽¹⁾) and R(T⁽²⁾).

**Key takeaway:** Realigning policy optimization at the **chunk level** — via resampling, geometric-mean IS, and inference-vs-training masking — corrects distributional drift in industrial off-policy agentic RL while preserving trajectory credit assignment.

## Caption (verbatim)

> Figure 8: Overview of the Proposed **Interaction-Perceptive Agentic Policy Optimization** (**IPA**) training pipeline.

### Figure 9 (p.22) ⭐深度解读
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p22.png]]
> [!quote] caption
> Comparison of importance sampling strategies across token-level, chunk-level, and sentence- level granularities, where chunk-level aligns with the natural granularity of interactions.

> [!tip] 技术解读（多模态）
> ## Figure Description

**Architecture/Components:**
The figure (Figure 9) displays three horizontal rows comparing importance sampling granularities along the same agent trajectory:
- **Token-Level (top):** Fine-grained partitioning — chunks contain many tokens; "Interaction" arrows appear at sub-chunk positions (misaligned).
- **Chunk-Level (middle, highlighted in orange):** Each chunk (c₁, c₂, …, cₜ) coincides with an environmental interaction; green checkmarks (✓) confirm alignment between chunk boundaries and interaction events.
- **Sentence-Level (bottom):** Coarse partitioning where one sentence spans multiple interactions.

Each chunk contains the sequence sᵢ, τᵢ₁, …, τᵢₕ, rᵢ, with "Interaction" markers indicating agent–environment boundaries.

**Key Technical Takeaway:** Chunk-level sampling is the natural granularity for multi-turn agentic RL — token-level mismatches decision/transition resolution (most tokens cause no external effect), while sentence-level is too coarse, conflating multiple decisions; chunks (e.g., *reason → API call → trigger execution*) align the optimization horizon with causal environmental transitions.

## Caption (verbatim)

**Figure 9:** Comparison of importance sampling strategies across token-level, chunk-level, and sentence-level granularities, where chunk-level aligns with the natural granularity of interactions.

### Figure 10 (p.23) ⭐深度解读
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p23.png]]
> [!quote] caption
> Comparison of Chunk-Level Optimization and baseline on a mini-set of the training data. Left:

> [!tip] 技术解读（多模态）
> ## Figure Description

**Layout:** Three side-by-side line plots comparing **Chunk-Level Optimization (orange)** vs **Baseline (gray)** over training steps (0–90).

| Panel | Metric | Y-axis | Orange (Chunk-Level) | Gray (Baseline) |
|-------|--------|--------|----------------------|-----------------|
| **Left** | Unclipped Gradient Norm | log scale, 10⁻²–10² | Stable near 10⁻² | Spikes up to ~10² |
| **Middle** | Train-Time Success Rate (%) | 50–75 | Climbs to ~68–70% | Plateau ~62–65% |
| **Right** | Test-Time Success Rate (%) | 48–58 | Climbs to ~57% | Plateau ~50–52% |

**Data flow:** Training-step index → metric measurement → per-step series point → comparison between two optimization methods.

### Key Technical Takeaway
Aligning temporal discounting to semantic chunk boundaries (rather than individual tokens) yields **~3 orders of magnitude lower gradient variance** at training time, which translates directly into a **+6% absolute gain in test-time success rate**, demonstrating that chunk-level credit assignment improves both stability and generalization in agentic RL. *(110 words)*

### Caption (Verbatim Transcription)

> Figure 10: Comparison of Chunk-Level Optimization and baseline on a mini-set of the training data. **Left:** Unclipped gradient norm for updates that reflects the stability of training. Our Chunk-Level Optimization exhibits more stable gradient norms, while baseline induces anomalous gradient fluctuations. **Middle:** Performance on training tasks. Owing to stable gradient updates and effective credit assignment, Chunk-Level Optimization consistently shows better performance than baseline. **Right:** Test-time success rate on validation tasks. Chunk-Level Optimization retain its superiority over baseline, demonstrating the generalization of our method.

### Figure 11 (p.24) ⭐深度解读
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p24.png]]
> [!quote] caption
> Illustration of the Chunk-Level Initialized Resampling Strategy (Sequential Rollback). Left: In challenging tasks, sampling high-quality trajectories from the beginning is difficult, severely limiting policy learning efficiency. Right: Sequential Rollback sampling strategy initiates rollouts from critical chunks, dramatically reducing the exploration burden and enabling the policy to rapidly acqui

> [!tip] 技术解读（多模态）
> ## Figure Description

The figure compares two rollout paradigms side-by-side, both sharing the same trajectory structure (state s¹ᵢ followed by chunks (c¹ᵢ, r¹ᵢ) … (sⁿᵢ …) anchored at a **Crucial Fork**).

**Left — Sampling From Beginning:** Standard rollouts start from s¹ᵢ and must traverse every chunk. In difficult tasks, *all* continuations collapse (✗), producing **Uninformative Rollouts for Optimization**.

**Right — Chunk-Level Initialized Resampling:** Once the early chunks are mastered, a **Sequential Rollback** re-anchors the rollout at progressively earlier crucial forks. The pre-filled prefix is an **Expert-Like Trajectory**; only the suffix is resampled. Success rate rises as forks are mastered, yielding **Valuable Rollouts for Optimization** (✓ on critical-chunk branches).

**Key takeaway:** By re-initializing rollouts at identified crucial forks instead of the start, IPA slashes the effective horizon, stabilizes reward signals, and converts long-horizon agentic tasks into a chunk-level curriculum. (≈70 words)

## Caption (verbatim)

**Figure 11:** Illustration of the Chunk-Level Initialized Resampling Strategy (Sequential Rollback). **Left:** In challenging tasks, sampling high-quality trajectories from the beginning is difficult, severely limiting policy learning efficiency. **Right:** Sequential Rollback sampling strategy initiates rollouts from critical chunks, dramatically reducing the exploration burden and enabling the policy to rapidly acquire the key skills embedded in these crucial chunks. By progressively rolling back along the crucial chunks, it enables chunk-level curriculum learning for model to finally solve these challenging tasks.

### Figure 12 (p.25) ⭐深度解读
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p25.png]]
> [!quote] caption
> Performance of Sequential Rollback and baseline (naive sampling) on a challenging training task. Left: Average success rate during training, which reflects the percentage of positive signals in training batch. Sequential Rollback obviously brings more valuable rollouts compared to baseline (all failures). The drop of success rate indicates that the model has rolled back across a crucial chunk to t

> [!tip] 技术解读（多模态）
> ## Figure Description

The figure (Figure 12) consists of **three side-by-side line plots** comparing Sequential Rollback (green) vs. Baseline/naive sampling (gray) over ~175 training steps:

- **Left** — *Average Success Rate (Train-Time)*: Seq-Rollback yields ~30–100% success with fluctuating "Success Rate Drops"; Baseline stays at 0%.
- **Middle** — *Expert Chunks Used (Train-Time)*: Number of expert chunks shrinks progressively from ~42 to ~1, showing "Rollback along the Expert Trajectory" / "Sample from the Beginning."
- **Right** — *Average Success Rate (Test-Time)*: Two regimes separated at step 75 — "All Attempts Failed" vs. "Learn to Succeed with Rollback" (rising to 100%).

**Data flow:** expert trajectory chunks → backward resampling initialization → policy rollouts → success-rate feedback driving iterative refinement.

**Key takeaway:** Sequential rollback anchors sampling near the decisive fork states of expert trajectories, dramatically reducing exploration cost and enabling the policy to learn skills that naive from-scratch sampling cannot acquire on hard tasks.

## Caption (verbatim)

**Figure 12:** Performance of Sequential Rollback and baseline (naive sampling) on a challenging training task. **Left:** Average success rate during training, which reflects the percentage of positive signals in training batch. Sequential Rollback obviously brings more valuable rollouts compared to baseline (all failures). The drop of success rate indicates that the model has rolled back across a crucial chunk of the crucial fork. **Middle:** Expert chunks used during training, which visually displays the progress of rolling back along the expert trajectory. **Right:** Average success rate on the challenging task during testing. In test-time, all trajectories are sampled from the initial state. The gap between two curves after step 75 indicates that sequential rollback enables effective learning on extremely hard tasks.

### Figure 13 (p.26) ⭐深度解读
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p26.png]]
> [!quote] caption
> Comparison of IPA with & without Chunk-Level Initialized Resampling (Parallelized Initial- ization) on a mini-set of the training data. Left: Average success rate on training tasks. The gap between curves in the early stage of training shows that the Chunk-Level Initialized Resampling brings much more diverse reward signals in training batches. Middle: Minimum success rate across train-tasks with 

> [!tip] 技术解读（多模态）
> **Figure Description (≤120 words):**

The main figure consists of **three side-by-side line plots**, all sharing the x-axis (Training Steps, 0–100). Two curves appear in each: an orange line "IPA (w/ Chunk-Level Init.)" and a gray dashed "Baseline."

- **Left plot** — *Average Success Rate (Train-Time, %)*: IPA climbs rapidly to ~95% by step 100; baseline plateaus near ~45%.
- **Middle plot** — *Minimum Train-Task Success Rate (%)*: IPA starts at 0% and rises to ~70% (annotated "Ability to Learn Challenging Tasks"); baseline stays at 0%, showing IPA unlocks hard tasks.
- **Right plot** — *Average Success Rate (Test-Time, %)*: IPA reaches ~90%, versus ~55% for baseline.

**Key takeaway:** Chunk-Level Initialized Resampling provides diverse reward signals early in training, enabling curriculum-like progression from easy to hard agentic tasks and yielding large generalization gains at test time.

**Caption (verbatim):**

Figure 13: Comparison of IPA with & without Chunk-Level Initialized Resampling (Parallelized Initialization) on a mini-set of the training data. **Left:** Average success rate on training tasks. The gap between curves in the early stage of training shows that the Chunk-Level Initialized Resampling brings much more diverse reward signals in training batches. **Middle:** Minimum success rate across train-tasks with test-time setting (sampled from beginning). With Chunk-Level Resampling, IPA enables the train model to solve extremely hard tasks by learning in a chunk-level curriculum-like manner. **Right:** Average success rate at test-time. Benefiting from more valuable rollouts, Parallelized Initialization substantially improves the performance of IPA.

### Figure 14 (p.27) ⭐深度解读
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p27.png]]
> [!quote] caption
> Benchmark characterization and cross-benchmark comparison of Terminal Bench Pro against other benchmarks.

> [!tip] 技术解读（多模态）
> **Description:**

Figure 14 is a four-panel characterization comparing Terminal Bench Pro against Terminal-Bench 1.0 and 2.0. Panel (a) is a donut chart showing Terminal Bench Pro's balanced task category distribution across 8 domains (Scientific Computing, Debugging, Games, System Administration, Security, Machine Learning, Data Processing, Software Engineering). Panel (b) is a stacked horizontal bar chart juxtaposing category proportions across the three benchmarks, revealing Terminal Bench Pro's balanced coverage vs. the skewed distributions of 1.0 and 2.0. Panel (c) is a heatmap of category-wise pass@1 standard deviations, showing lower variance for Terminal Bench Pro Public. Panel (d) is a grouped bar chart (Min/Median/Mean test cases) showing Terminal Bench Pro Public averaging ~28.3 test cases per task versus ~5 for the others.

**Key takeaway:** Terminal Bench Pro delivers balanced domain coverage and ~5–6× more test cases per task than prior benchmarks, yielding more statistically reliable agent evaluations.

**Caption (verbatim):**

"Figure 14: Benchmark characterization and cross-benchmark comparison of Terminal Bench Pro against other benchmarks."

### Figure 15 (p.28) ⭐深度解读
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p28.png]]
> [!quote] caption
> Performance-parameter trade-offs in agentic tasks. Scores represent averages on general agentic and code agent benchmarks. Models with known parameters are shown as circles, while proprietary models with unknown parameters are depicted as diamonds (right side). Left: Total parameters versus overall performance. Right: Activated parameters versus overall performance. 2https://github.com/alibaba/ter

> [!tip] 技术解读（多模态）
> # Figure 15 Description

**Architecture/Components/Data Flow:** The figure consists of two side-by-side scatter plots comparing model accuracy (%) against model size. The **left panel** plots Accuracy vs. **Total Parameters** (Billions, log scale), while the **right panel** plots Accuracy vs. **Activated Parameters** (Billions, log scale). Both panels include an annotation for the "Performance Pareto-Front" curve. Models are encoded by shape: **blue circles** for known-parameter open-source models (e.g., GLM-4.6, DeepSeek v3.1, Qwen3-Coder Plus, Kimi-K2-0905, GLM-4.5 Air, GPT-OSS-120B) and **orange diamonds** for proprietary unknown-parameter models (Claude-Haiku-4.5, GPT-5 Mini, Gemini-2.5 Flash). The highlighted **purple circle marks iFlow-ROME (30B–A3B)**, the proposed model. A shaded region on the right side denotes the "Unknown Parameters" regime.

**Key Technical Takeaway:** iFlow-ROME (30B–A3B) sits on the Pareto frontier, achieving ~31% accuracy with only 3B activated parameters—matching or exceeding much larger models like GPT-OSS-120B and GLM-4.5 Air, demonstrating superior parameter efficiency.

**Caption (verbatim):**
"Figure 15: Performance-parameter trade-offs in agentic tasks. Scores represent averages on general agentic and code agent benchmarks. Models with known parameters are shown as circles, while proprietary models with unknown parameters are depicted as diamonds (right side). **Left**: Total parameters versus overall performance. **Right**: Activated parameters versus overall performance."

### Figure 16 (p.34) ⭐深度解读
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p34.png]]
> [!quote] caption
> Pairwise win-rate matrix (%) on the 100-task real-world benchmark under 30-expert blinded majority voting. Each cell reports the percentage of tasks where the row model is judged better than the col- umn model; higher values (green) indicate stronger performance.

> [!tip] 技术解读（多模态）
> **Figure 16 — Description:**

The main figure is a 5×5 pairwise win-rate heatmap comparing five models: ROME, Qwen3-Coder Plus, GLM-4.6, Qwen3-Coder 30B, and Devstral Small 2, evaluated on a 100-task real-world benchmark (ties excluded). Each cell encodes the percentage of tasks where the row model outperformed the column model, color-coded via a divergent red→yellow→green gradient (0–100% Win Rate scale shown on the right). The diagonal is blank/self-comparison. ROME's row reads 58.8, 58.8, 100.0, 100.0 — uniformly green and saturating against the two smaller baselines — while weaker models (Qwen3-Coder 30B, Devstral Small 2) yield deep red cells (0.0, 5.6, 10.5) when facing ROME.

**Key takeaway:** ROME achieves near-saturated win rates (100%) against smaller same-family baselines and a consistent ~58% edge over the larger Qwen3-Coder Plus and GLM-4.6, evidencing "scale-breaking" agentic capability rather than mere parameter scaling.

**Caption (verbatim):**

Figure 16: Pairwise win-rate matrix (%) on the 100-task real-world benchmark under 30-expert blinded majority voting. Each cell reports the percentage of tasks where the row model is judged better than the column model; higher values (green) indicate stronger performance.

### Figure 17 (p.36) ⭐深度解读
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p36.png]]
> [!quote] caption
> Case study 1 screenshot examples: Sleep Management System Generation. 36

> [!tip] 技术解读（多模态）
> **Description:**

The figure is a comparative grid of UI screenshots (5 rows × 3 columns) generated by different code-generating AI models for a "Sleep Management System." It compares outputs from five models—ROME (a, b, c), Qwen3-Coder-Plus (d, e, f), GLM-4.6 (g, h, i), Qwen3-coder-30B (j, k, l), and Devstral-Small-2 (m, n, o)—with each row showing three sequential screenshots illustrating how the rendered dashboard evolves (e.g., analytics panels, KPI cards, charts, user tables).

**Key technical takeaway:**
ROME produces a visually rich, themed dashboard with gradient backgrounds, KPI tiles, line/bar charts, and toggle controls—outperforming the baselines, which yield more uniform, sparse, or partially rendered layouts.

**Caption (verbatim):**
Figure 17: Case study 1 screenshot examples: Sleep Management System Generation.

### Figure 18 (p.37) ⭐深度解读
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p37.png]]
> [!quote] caption
> Case study 2 screenshot examples: Solar System Modeling. 37

> [!tip] 技术解读（多模态）
> ## Figure Description

The figure is a **5×3 comparative grid** (15 panels total) showing rendered output screenshots from five different LLM-based code generation systems attempting the same prompt: produce a Solar System visualization.

**Layout (model → row):**
- **Row 1 (a–c):** ROME — black background, bright yellow central sun, concentric orbital rings, several small orbiting planets visible.
- **Row 2 (d–f):** Qwen3-Coder-Plus — similar layout with sun + planets; (e) shows planets in a near-linear arrangement.
- **Row 3 (g–i):** GLM-4.6 — dark **blue** background, HUD overlays in corners, sun + planets rendered with engine-style graphics.
- **Row 4 (j–l):** Qwen3-coder-30B — black background, faint orbital grid, only a couple of planets visible per frame.
- **Row 5 (m–o):** Devstral-Small-2 — nearly empty black canvases with only tiny dots, no readable structure.

**Key technical takeaway:** Even with identical prompts, only ROME and GLM-4.6 produce complete, visually correct solar-system simulations; smaller/local code models (Devstral-Small-2, Qwen3-coder-30B) yield partially rendered or near-empty scenes, demonstrating that **spatial-physics visualization fidelity scales strongly with model reasoning capability**, not just code-compilation success.

## Caption (verbatim)

**Figure 18: Case study 2 screenshot examples: Solar System Modeling.**

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