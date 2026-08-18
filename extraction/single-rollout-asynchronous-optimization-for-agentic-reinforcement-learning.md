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

### Figure 1 (p.1)
![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p01.png]]
> [!quote] caption
> The performance of SAO on reasoning and coding benchmarks. The four reasoning benchmarks are evaluated in a reasoning-with-Python-tool setting, where the baseline is the Qwen3- 30B-A3B SFT model; SWE-Bench Verified evaluates coding with the Qwen3-30B-A3B baseline. SAO outperforms the corresponding baseline and GRPO across all five benchmarks. ∗Equal Contribution. Work done while ZH and YL interned

### Figure 2 (p.3)
![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p03.png]]
> [!quote] caption
> Overview of SAO with single rollout design. The numbers denote the generation order of trajectories. For SAO, each trajectory becomes available for training immediately upon completion.

### Figure 3 (p.6)
![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p06.png]]
> [!quote] caption
> Performance comparison between SAO and GRPO (w/ DIS) during training. It can be observed that SAO almost consistently outperforms the optimized GRPO during the training process on different benchmarks. 4

### Figure 4 (p.7)
![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p07.png]]
> [!quote] caption
> Training dynamics of asynchronous single-rollout RL. (a) Explained Variance for SAO and a single-critic-update baseline. (b) Critic gradient norm during value training under full-parameter optimization and frozen-attention optimization used in SAO. (c) Token-level clip ratio during training for SAO with the proposed DIS and the VAPO baseline.

### Figure 5 (p.9)
![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p09.png]]
> [!quote] caption
> Online learning simulation under changing writing-style preferences. 5

### Figure 6 (p.13)
![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p13.png]]
> [!quote] caption
> Training reward for token-level SAO training and step-level variants, where token-level shows better training rewards.

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.2 `πθ(y|q), which generates a response sequence y = [y1, . . . , y|y|] given a query q from dataset D.`
- p.3 `where rt(θ) =`
- p.3 `ϕ = E[(Vϕ(q, y<t) −R)2], where R denotes the cumulative reward. To balance`
- p.3 `where δt = rt + γVϕ(st+1) −Vϕ(st). While effective, this approach necessitates maintaining a copy`
- p.4 `i.e., rt(θ) =`
- p.4 `L(θ) = ˆEt`
- p.4 `rt(θ) = exp (log πθ(at|st) −log πrollout(at|st))`
- p.5 `ˆA(ai,N) = δ + γλ ˆA(ai+1,0)`
- p.5 `δ = rt + γV (ai+1,0) −V (ai,N)`
- p.6 `ϵlow = 0.3, ϵhigh = 5.0. We adopt a length-adaptive GAE [Yue et al., 2025] with λpolicy = 1 −1`
- p.6 `and α = 1.5. The value model is trained with a learning rate of 5 × 10−6, λcritic = 1, and a 10-step`
- p.9 `recent rewards, thereby facilitating advantage computation as ˆA = r −E[rwindow]. By decoupling`
- p.13 `λpolicy = 1 −`

## 相关论文

- [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] — AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM REINFORCEMENT LEARNING
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEMENT LEARNING
- [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] — DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
- [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] — Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning
- [[hybridflow-a-flexible-and-efficient-rlhf-framework]] — HybridFlow: A Flexible and Efficient RLHF Framework

## 全文文本
全文已存 `extraction/fulltext/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning.txt`（45212 字符）供引用检索。