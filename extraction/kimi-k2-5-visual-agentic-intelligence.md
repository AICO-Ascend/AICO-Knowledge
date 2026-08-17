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

### Figure 1 (p.1)
![[assets/kimi-k2-5-visual-agentic-intelligence-p01.png]]
> [!quote] caption
> Kimi K2.5 main results. 1

### Figure 2 (p.4)
![[assets/kimi-k2-5-visual-agentic-intelligence-p04.png]]
> [!quote] caption
> Vision RL training curves on vision benchmarks starting from minimal zero-vision SFT. By scaling vision RL FLOPs, the performance continues to improve, demonstrating that zero-vision activation paired with long-running RL is sufficient for acquiring robust visual capabilities.

### Figure 3 (p.5)
![[assets/kimi-k2-5-visual-agentic-intelligence-p05.png]]
> [!quote] caption
> An agent swarm has a trainable orchestrator that dynamically creates specialized frozen subagents and decomposes complex tasks into parallelizable subtasks for efficient distributed execution.

### Figure 4 (p.6)
![[assets/kimi-k2-5-visual-agentic-intelligence-p06.png]]
> [!quote] caption
> In our parallel-agent reinforcement learning environment, the training accuracy increases smoothly as train- ing progresses. At the same time, the level of parallelism during training also gradually increases. many subagents without meaningful task decomposition. By rewarding completed subtasks, r finish enforces feasibility and guides the policy toward valid and effective decompositions.

### Figure 5 (p.10)
![[assets/kimi-k2-5-visual-agentic-intelligence-p10.png]]
> [!quote] caption
> Comparison of model performance and token usage for Kimi K2 Thinking following token-efficient RL. compromise alleviates memory pressure, it does not fundamentally resolve the load imbalance caused by multimodal input sizes. More critically, it precludes the direct reuse of parallel strategies that have been highly optimized for text-only training.

### Figure 6 (p.14)
![[assets/kimi-k2-5-visual-agentic-intelligence-p14.png]]
> [!quote] caption
> The word cloud visualizes heterogeneous K2.5-based sub-agents dynamically instantiated by the

### Figure 7 (p.14)
![[assets/kimi-k2-5-visual-agentic-intelligence-p14.png]]
> [!quote] caption
> Comparison of Kimi K2.5 performance un- der Agent Swarm and Discard-all context management in BrowseComp. (60.6%) and surpassing even GPT-5.2 Pro (77.9%). Similarly, WideSearch sees a 6.3% improvement (72.7% → 79.0%) on Item-F1, enabling K2.5 Agent Swarm to outperform Claude Opus 4.5 (76.2%) and establish a new state- of-the-art. The gains are most pronounced on In-house Swarm bench (16.7%), where

### Figure 8 (p.15)
![[assets/kimi-k2-5-visual-agentic-intelligence-p15.png]]
> [!quote] caption
> Agent Swarm achieves 3×–4.5× faster execution time compared to single-agent baselines as target Item-F1 increases from 30% to 70% in WideSearch testing. rather than context truncation, allowing the system to scale effective context length along an additional architectural dimension while preserving modularity, information locality, and reasoning integrity.

### Figure 9 (p.21)
![[assets/kimi-k2-5-visual-agentic-intelligence-p21.png]]
> [!quote] caption
> Learning curves comparing vision-to-text ratios (10:90, 20:80, 50:50) under fixed vision-text token budget across vision and language tasks. Early fusion with lower vision ratios tend to yield better results. B

### Figure 10 (p.23)
![[assets/kimi-k2-5-visual-agentic-intelligence-p23.png]]
> [!quote] caption
> Overview of our agentic RL framework. environments with minimal overhead. Our design prioritizes compositional modularity by integrating a suite of plug- gable components, such as a Tolset module for supporting various tools with sandboxes, a Judge module for multi- faceted reward signals, and specialized modules for prompt diversification and instruction-following enhancement.

### Figure 11 (p.28)
![[assets/kimi-k2-5-visual-agentic-intelligence-p28.png]]
> [!quote] caption
> Qualitative example of Kimi K2.5 analyzing a complete playthrough of Black Myth: Wukong (24 hours of continuous gameplay across 32 videos at 1080p) using parallel visual agents. See generated webpage and source videos (all rights reserved by source authors). 28

### Figure 12 (p.29)
![[assets/kimi-k2-5-visual-agentic-intelligence-p29.png]]
> [!quote] caption
> Qualitative examples of Kimi K2.5 solving visual reasoning tasks via tool use. 29

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

## 全文文本
全文已存 `extraction/fulltext/kimi-k2-5-visual-agentic-intelligence.txt`（95693 字符）供引用检索。