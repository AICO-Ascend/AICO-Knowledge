---
paper_num: "69"
title: "Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning"
authors: "Reinforcement Learning Zhenyu Hou∗ Yujiang Li∗ Jie Tang Yuxiao Dong Tsinghua University"
date: "2026/7/8"
arxiv: "https://arxiv.org/abs/2607.07508"
pdf: "papers/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning.pdf"
slug: "single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning"
tags: [rl]
---

# Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning

> [!abstract] 摘要（原文）
> Reinforcement learning (RL) is becoming increasingly important for post-training large language models (LLMs). Previous RL pipelines for LLMs were mostly synchronous and batch-interleaved, which is inefficient for long-horizon agentic tasks. Recently, asynchronous RL has emerged as a more efficient alternative by updating the model as rollouts arrive. However, existing asynchronous RL systems often emphasize throughput, while leaving training stability and task effectiveness largely underexplored. For example, a key challenge is that group-wise sampling in the widely-used GRPO framework does not naturally fit asynchronous agentic training. In this paper, we present Single-rollout Asynchronous Optimization (SAO) to address the stability and off-policy challenges in asynchronous RL. To reduce off-policy effects and improve generalization, we replace group-wise sampling with single-rollout sampling, that is, using one rollout per prompt. We further improve this single-rollout strategy with practical value-model training designs. To improve optimization stability, we introduce a strict double-side token-level clipping strategy. SAO is able to train stably for one thousand steps and consistently outperform GRPO and its variants on agentic coding and reasoning benchmarks, such as SWE-Bench Verified, BeyondAIME, and IMOAnswerBench. We also demonstrate that single-rollout RL is particularly effective in a simulated online learning setting, where the model must adapt to changing evolving environments. To this end, SAO is successfully deployed in the agentic RL pipeline for training the open GLM-5.2 model (750B-A40B).

## 元信息
- **发表日期**: 2026/7/8
- **作者**: Reinforcement Learning Zhenyu Hou∗ Yujiang Li∗ Jie Tang Yuxiao Dong Tsinghua University
- **arXiv**: https://arxiv.org/abs/2607.07508
- **本地 PDF**: `papers/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning.pdf`
- **页数**: 14

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p01.png]]
> [!quote] caption
> The performance of SAO on reasoning and coding benchmarks. The four reasoning benchmarks are evaluated in a reasoning-with-Python-tool setting, where the baseline is the Qwen3- 30B-A3B SFT model; SWE-Bench Verified evaluates coding with the Qwen3-30B-A3B baseline. SAO outperforms the corresponding baseline and GRPO across all five benchmarks. ∗Equal Contribution. Work done while ZH and YL interned

> [!tip] 技术解读（多模态）
> ## Figure Description

**Type:** Grouped bar chart comparing three methods across five benchmarks.

**Components:**
- **Y-axis:** Accuracy (%) from 0 to 100
- **X-axis:** Five benchmarks — AIME2025, BeyondAIME, HMMT Nov 2025, IMOAnswerBench, SWE-Bench Verified
- **Three series per benchmark:** Baseline (white), GRPO (light blue), SAO/ours (dark blue)

**Data flow:** Each benchmark group shows three adjacent bars, with SAO consistently as the tallest, GRPO in the middle, and Baseline lowest. Notable values: AIME2025 (Baseline 80.4 → GRPO 84.2 → SAO 97.3), BeyondAIME (53.3 → 54.8 → 74.8), SWE-Bench Verified (23.0 → 27.0 → 29.8).

**Key technical takeaway:** SAO delivers the largest gains on reasoning benchmarks (e.g., +19.9 points on BeyondAIME) while also winning on coding, demonstrating that single-rollout asynchronous optimization surpasses group-wise GRPO sampling without sacrificing throughput.

## Caption (verbatim)

**Figure 1: The performance of SAO on reasoning and coding benchmarks.** The four reasoning benchmarks are evaluated in a reasoning-with-Python-tool setting, where the baseline is the Qwen3-30B-A3B SFT model; SWE-Bench Verified evaluates coding with the Qwen3-30B-A3B baseline. SAO outperforms the corresponding baseline and GRPO across all five benchmarks.

### Figure 2 (p.3) ⭐深度解读
![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p03.png]]
> [!quote] caption
> Overview of SAO with single rollout design. The numbers denote the generation order of trajectories. For SAO, each trajectory becomes available for training immediately upon completion.

> [!tip] 技术解读（多模态）
> ## Figure Description

**Architecture & Data Flow:**

The figure compares two asynchronous RL training pipelines side-by-side:

**Top — GRPO (baseline):** A rollout stage generates trajectories in batches (numbered 4, 6, 8 → 1, 2, 7, 9 → 3, 5). Trajectories must accumulate into a complete **Group** before the Training stage can begin ("waiting for Group"). The trust-region constraint compares π_θ against π_rollout, clipped to [1−ε, 1+ε].

**Bottom — SAO (proposed):** Rollout generates trajectories sequentially (9, 8, …, 3, 2, 1). Each trajectory is fed immediately into Training as soon as it completes ("Single-Rollout Ready for training"), with the same clipping trust region but now using π_θ as the reference.

**Key Technical Takeaway:** SAO removes the group-level synchronization barrier of GRPO by adopting single-rollout training, eliminating idle "waiting" time and enabling asynchronous, streaming updates while still preserving PPO-style importance-ratio clipping for stability. (88 words)

## Caption (verbatim)

> Figure 2: Overview of SAO with single rollout design. The numbers denote the generation order of trajectories. For SAO, each trajectory becomes available for training immediately upon completion. In contrast, GRPO must wait until all trajectories in a group are generated before training can begin.

### Figure 3 (p.6) ⭐深度解读
![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p06.png]]
> [!quote] caption
> Performance comparison between SAO and GRPO (w/ DIS) during training. It can be observed that SAO almost consistently outperforms the optimized GRPO during the training process on different benchmarks. 4

> [!tip] 技术解读（多模态）
> **Figure 3 Description**

**Components:** Three side-by-side line plots tracking training dynamics across math reasoning tasks — AIME 2025, BeyondAIME, and HMMT-Nov-2025 — each plotting Accuracy (%) versus Training Step (0–1000). Three curves are compared per subplot:
- **SAO** (light purple) — proposed method
- **GRPO (w/ DIS)** (dark blue) — optimized baseline with Dual Importance Sampling
- **Vanilla GRPO** (cyan) — standard GRPO with clip-higher

**Data flow:** Each subplot shows validation accuracy sampled periodically during RL fine-tuning of the Qwen3-30B-A3B policy.

**Key takeaway:** Vanilla GRPO suffers a sharp performance collapse around ~160 steps across all benchmarks, while GRPO (w/ DIS) stabilizes training and climbs steadily. SAO consistently sits at or above the GRPO (w/ DIS) curve throughout training, with the gap widening in later steps.

**Caption (verbatim):**
"Figure 3: Performance comparison between SAO and GRPO (w/ DIS) during training. It can be observed that SAO almost consistently outperforms the optimized GRPO during the training process on different benchmarks."

### Figure 4 (p.7) ⭐深度解读
![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p07.png]]
> [!quote] caption
> Training dynamics of asynchronous single-rollout RL. (a) Explained Variance for SAO and a single-critic-update baseline. (b) Critic gradient norm during value training under full-parameter optimization and frozen-attention optimization used in SAO. (c) Token-level clip ratio during training for SAO with the proposed DIS and the VAPO baseline.

> [!tip] 技术解读（多模态）
> **Main Figure Description (≤120 words):**

Figure 4 presents training-dynamics diagnostics for the SAO (Single-Rollout Asynchronous) reinforcement learning framework through three line plots tracking metrics over training steps. Panel (a) compares Explained Variance between SAO and a single-critic-update baseline ("SAO w/o Faster value"), showing SAO achieves higher explained variance after ~400 steps, indicating better value-prediction alignment with returns. Panel (b) plots Critic Gradient Norm, comparing full-parameter value training ("SAO w/o Frozen attention") against SAO's frozen-attention variant — full optimization produces unboundedly growing gradients (~10) while frozen attention keeps them stable (~4–5), demonstrating regularization. Panel (c) tracks Token-level Clip Ratio, where SAO with DIS shows a controlled spike while vanilla VAPO (w/o DIS) remains near zero, indicating more conservative policy updates.

**Key takeaway:** Frozen-attention value updates and divergence-immune stable clipping are jointly necessary for stable async single-rollout RL training.

**Caption (verbatim):**

Figure 4: Training dynamics of asynchronous single-rollout RL. (a) Explained Variance for SAO and a single-critic-update baseline. (b) Critic gradient norm during value training under full-parameter optimization and frozen-attention optimization used in SAO. (c) Token-level clip ratio during training for SAO with the proposed DIS and the VAPO baseline.

### Figure 5 (p.9) ⭐深度解读
![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p09.png]]
> [!quote] caption
> Online learning simulation under changing writing-style preferences. 5

> [!tip] 技术解读（多模态）
> **Figure Description:**

Figure 5 consists of two side-by-side line plots depicting an online learning simulation under non-stationary writing-style preferences.

- **Left (a):** Tracks accuracy (%) over training steps (0–400+) for three writing styles — Academic, Cute, Classical, Chuunibyou. Shaded regions mark phase transitions where the rewarded style switches; curves show one style rising as the previously dominant one collapses, demonstrating rapid policy re-alignment.
- **Right (b):** Compares reward trajectories of SAO versus a Running Mean Advantage baseline across the same training horizon. Both curves dip at style shifts, but SAO recovers faster and sustains higher steady-state reward.

**Key Takeaway:** SAO's state-dependent baseline adapts to reward distribution shifts with substantially less adaptation lag than the inertia-bound Running Mean baseline, confirming its suitability for non-stationary online RL.

**Caption (verbatim):**

Figure 5: Online learning simulation under changing writing-style preferences.

### Figure 6 (p.13) ⭐深度解读
![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p13.png]]
> [!quote] caption
> Training reward for token-level SAO training and step-level variants, where token-level shows better training rewards.

> [!tip] 技术解读（多模态）
> ## Figure 6 Description

**Main Figure — Training Reward Curve**

- **Plot type:** Line graph, Reward (y-axis, 0.42–0.54) vs. Training Step (x-axis, 0–400).
- **Components / Data flow:** Three curves are tracked over training steps:
  - **SAO (token-level)** — light blue line, climbs steadily from ~0.42 to ~0.54.
  - **Step-level (Average)** — purple line, fluctuates and plateaus around 0.48–0.49.
  - **Step-level (Last-Token)** — darker blue line, tracks closely with the Average variant, ending near 0.49.
- **Trend:** Token-level SAO consistently sits above both step-level variants after ~step 150, with a widening gap.

**Key Technical Takeaway (≤120 words):**
Token-level advantage/value estimation provides finer-grained supervision than step-level aggregation (Average or Last-Token), yielding a substantially higher training reward (≈0.54 vs. ≈0.49). This indicates that aggregating value signals across an entire conversation turn—whether by mean or by terminal-token prediction—blurs the local credit-assignment signal. Token-wise critic targets preserve step-internal logical transitions, which is critical for complex reasoning trajectories where credit must be assigned to sub-step actions rather than coarse turns. **Implication:** retain token-level granularity for both the value model and GAE advantage computation rather than collapsing to step-level actions.

---

## Caption (verbatim)

**Figure 6:** Training reward for token-level SAO training and step-level variants, where token-level shows better training rewards.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbb{E}\left[ \frac{1}{|y|} \sum_{t=1}^{|y|} \min \left( r_t(\theta) \hat{A}_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon) \hat{A}_t \right) \right]
$$

$$
\hat{A}_t^{\text{GAE}} = \sum_{l=0}^{|y|-t-1} (\gamma \lambda)^l \delta_{t+l}
$$

$$
\hat{A}_{i,t} = \frac{R_i - \mu_R}{\sigma_R}, \quad \text{with} \quad \mu_R = \frac{1}{G}\sum_{j=1}^G R_j
$$

$$
L(\theta) = \hat{\mathbb{E}}_t \left[ f(r_t(\theta), \epsilon_l, \epsilon_h) \hat{A}_t \log \pi_{\theta}(a_t|s_t) \right]
$$

$$
r_t(\theta) = \exp\left( \log \pi_\theta(a_t|s_t) - \log \pi_{\text{rollout}}(a_t|s_t) \right)
$$

$$
f(x; \epsilon_\ell, \epsilon_h) = \begin{cases} x, & \text{if } 1-\epsilon_\ell < x < 1+\epsilon_h \\ 0, & \text{otherwise} \end{cases}
$$

$$
\hat{A}(a_{i, N}) = \delta + \gamma \lambda \hat{A}(a_{i+1, 0})
$$

$$
\delta = r_t + \gamma V(a_{i+1, 0}) - V(a_{i, N})
$$

## 相关论文

- [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] — AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM REINFORCEMENT LEARNING
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEMENT LEARNING
- [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] — DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
- [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] — Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning
- [[hybridflow-a-flexible-and-efficient-rlhf-framework]] — HybridFlow: A Flexible and Efficient RLHF Framework

## 技术点深读（DEEP）

![[deep/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning.txt`（45212 字符）供引用检索。