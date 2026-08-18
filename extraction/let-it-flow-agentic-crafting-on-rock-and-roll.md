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

### Figure 3 (p.5)
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p05.png]]
> [!quote] caption
> ROLL Architecture. (a) ROLL pipelines LLM generation, environment interaction, and reward phases at trajectory-level granularity. Training is also decoupled via a sample buffer using an asyn- chronous ratio to manage staleness. (b) ROLL multiplexes a dynamic GPU pool by shrinking rollout resources for bursty training and expanding them back during demand peaks. coordinates heterogeneous workers an

### Figure 4 (p.6)
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p06.png]]
> [!quote] caption
> ROCK System Architecture.

### Figure 5 (p.8)
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p08.png]]
> [!quote] caption
> The overview of iFlow CLI architecture and execution. these requests already contain the complete historical context, fully orchestrated by the iFlow CLI. The proxy then forwards these requests to the appropriate inference service — be it ROLL inference workers during training or an external API (e.g., GPT, Gemini) during deployment. The native mode achieves a clean separation. ROLL is simplified 

### Figure 6 (p.10)
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p10.png]]
> [!quote] caption
> Overview of data sources and composition pipelines for training agentic models, spanning code centric basic data and agentic data. 3

### Figure 7 (p.16)
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p16.png]]
> [!quote] caption
> Overview of ROME’s Training Pipeline. incidents. Finally, we generated corresponding golden trajectories devoid of general-security issues for subsequent post-training (e.g., SFT and RL). Our overarching objective was to instill robust security awareness such that, when confronted with tasks containing latent security pitfalls, the agent reliably selected safe action paths and proactively avoided 

### Figure 8 (p.20)
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p20.png]]
> [!quote] caption
> Overview of the Proposed Interaction-Perceptive Agentic Policy Optimization (IPA) training pipeline. sample efficiency(§3.2.4.4). An overview of our framework, including its key components and data flow, is depicted in Figure 8.

### Figure 9 (p.22)
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p22.png]]
> [!quote] caption
> Comparison of importance sampling strategies across token-level, chunk-level, and sentence- level granularities, where chunk-level aligns with the natural granularity of interactions.

### Figure 10 (p.23)
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p23.png]]
> [!quote] caption
> Comparison of Chunk-Level Optimization and baseline on a mini-set of the training data. Left:

### Figure 11 (p.24)
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p24.png]]
> [!quote] caption
> Illustration of the Chunk-Level Initialized Resampling Strategy (Sequential Rollback). Left: In challenging tasks, sampling high-quality trajectories from the beginning is difficult, severely limiting policy learning efficiency. Right: Sequential Rollback sampling strategy initiates rollouts from critical chunks, dramatically reducing the exploration burden and enabling the policy to rapidly acqui

### Figure 12 (p.25)
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p25.png]]
> [!quote] caption
> Performance of Sequential Rollback and baseline (naive sampling) on a challenging training task. Left: Average success rate during training, which reflects the percentage of positive signals in training batch. Sequential Rollback obviously brings more valuable rollouts compared to baseline (all failures). The drop of success rate indicates that the model has rolled back across a crucial chunk to t

### Figure 13 (p.26)
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p26.png]]
> [!quote] caption
> Comparison of IPA with & without Chunk-Level Initialized Resampling (Parallelized Initial- ization) on a mini-set of the training data. Left: Average success rate on training tasks. The gap between curves in the early stage of training shows that the Chunk-Level Initialized Resampling brings much more diverse reward signals in training batches. Middle: Minimum success rate across train-tasks with 

### Figure 14 (p.27)
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p27.png]]
> [!quote] caption
> Benchmark characterization and cross-benchmark comparison of Terminal Bench Pro against other benchmarks.

### Figure 15 (p.28)
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p28.png]]
> [!quote] caption
> Performance-parameter trade-offs in agentic tasks. Scores represent averages on general agentic and code agent benchmarks. Models with known parameters are shown as circles, while proprietary models with unknown parameters are depicted as diamonds (right side). Left: Total parameters versus overall performance. Right: Activated parameters versus overall performance. 2https://github.com/alibaba/ter

### Figure 16 (p.34)
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p34.png]]
> [!quote] caption
> Pairwise win-rate matrix (%) on the 100-task real-world benchmark under 30-expert blinded majority voting. Each cell reports the percentage of tasks where the row model is judged better than the col- umn model; higher values (green) indicate stronger performance.

### Figure 17 (p.36)
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p36.png]]
> [!quote] caption
> Case study 1 screenshot examples: Sleep Management System Generation. 36

### Figure 18 (p.37)
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p37.png]]
> [!quote] caption
> Case study 2 screenshot examples: Solar System Modeling. 37

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.19 `LSFT(θ) = −`
- p.20 `∇JREINFORCE(π) = Eτ∼π [R(τ) ∇log π(τ)] ,`
- p.20 `∇JRL(π) = Eτ∼µSGLang`
- p.21 `∇JRL(π) = ∑`
- p.21 `we define a binary loss mask: mk = I`
- p.23 `Gk = γ∆(j,k) × Rfinal,`
- p.24 `∇JChunk-RL(π) = ∑`
- p.26 `LIPA = λIL · ∑`

## 全文文本
全文已存 `extraction/fulltext/let-it-flow-agentic-crafting-on-rock-and-roll.txt`（160353 字符）供引用检索。