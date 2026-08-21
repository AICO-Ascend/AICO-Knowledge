---
paper_num: "33"
title: "AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning"
authors: "Learning System for Language Reasoning Wei Fu12∗, Jiaxuan Gao1, Xujie Shen2, Chen Zhu2, Zhiyu Mei12, Chuyi He2, Shusheng Xu12, Guo Wei2, Jun Mei2, Jiashu Wang3, Tongkai Yang2, Binhang Yuan3, Yi Wu1 1 IIIS, Tsinghua Unive"
date: "2026/1/17"
arxiv: "https://arxiv.org/abs/2505.24298"
pdf: "papers/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning.pdf"
slug: "areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning"
tags: [rl]
---

# AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning

> [!abstract] 摘要（原文）
> 1\. 🏆 AReaL 提出了一个完全异步的强化学习系统，通过彻底解耦 LLM 的生成和训练过程，解决了同步 RL 系统在处理长推理任务时 GPU 利用率低和扩展性差的问题。 2. 🌟 为了在异步环境下保持 RL 训练的稳定性，AReaL 引入了对数据时效性的控制，并采用了一种解耦的 PPO 目标函数，使其能够有效利用来自不同策略版本的数据。 3. 🚀 实验结果表明，与同步系统相比，AReaL 在数学和代码推理基准测试中实现了高达 2.77 倍的训练加速，同时保持或提升了最终模型性能，并展示了良好的可扩展性。

## 元信息
- **发表日期**: 2026/1/17
- **作者**: Learning System for Language Reasoning Wei Fu12∗, Jiaxuan Gao1, Xujie Shen2, Chen Zhu2, Zhiyu Mei12, Chuyi He2, Shusheng Xu12, Guo Wei2, Jun Mei2, Jiashu Wang3, Tongkai Yang2, Binhang Yuan3, Yi Wu1 1 IIIS, Tsinghua Unive
- **arXiv**: https://arxiv.org/abs/2505.24298
- **本地 PDF**: `papers/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning.pdf`
- **页数**: 27

## 图表（原文 caption + 页码）

### Figure 1 (p.4) ⭐深度解读
![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]]
> [!quote] caption
> Execution timeline of a synchronous (left) and a one-step overlap (right) RL system showing underutilized inference devices. … Rollout Controller Reward Service

> [!tip] 技术解读（多模态）
> **Figure 2 — AREAL Architecture**

**Components & Data Flow:** Two decoupled GPU clusters. The *Generation* side hosts multiple Interruptible Rollout Workers (GPU) that send prompts (green) and trajectories (blue) through a Rollout Coordinator to a Replay Buffer. A Reward Service (CPU) returns rewards via the coordinator. The Replay Buffer sends aggregated batches through a Replay Buffer to Trainer Workers (GPU, Training cluster), which feed a Parameter Service. The Parameter Service emits interrupt signals (red) and parameter save/load updates (purple) back to the rollout workers, closing the async loop.

**Key takeaway (≤120 words):** AREAL fully decouples generation and training across separate GPU clusters coordinated via a Replay Buffer and Parameter Service. Rollout workers are *interruptible*: upon receiving new weights they discard stale KV state and continue decoding—enabling continuous, weight-updated trajectory generation without waiting for synchronized training steps. This eliminates the GPU underutilization and memory-IO bottleneck of synchronous RL.

**Caption (verbatim):**
*"Figure 2: The AREAL architecture featuring asynchronous generation and training components."*

### Figure 2 (p.4) ⭐深度解读
![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]]
> [!quote] caption
> The AREAL architecture featuring asynchronous generation and training components.

> [!tip] 技术解读（多模态）
> **Figure 2 — AREAL Architecture**

**Components & Data Flow:** Two decoupled GPU clusters. The *Generation* side hosts multiple Interruptible Rollout Workers (GPU) that send prompts (green) and trajectories (blue) through a Rollout Coordinator to a Replay Buffer. A Reward Service (CPU) returns rewards via the coordinator. The Replay Buffer sends aggregated batches through a Replay Buffer to Trainer Workers (GPU, Training cluster), which feed a Parameter Service. The Parameter Service emits interrupt signals (red) and parameter save/load updates (purple) back to the rollout workers, closing the async loop.

**Key takeaway (≤120 words):** AREAL fully decouples generation and training across separate GPU clusters coordinated via a Replay Buffer and Parameter Service. Rollout workers are *interruptible*: upon receiving new weights they discard stale KV state and continue decoding—enabling continuous, weight-updated trajectory generation without waiting for synchronized training steps. This eliminates the GPU underutilization and memory-IO bottleneck of synchronous RL.

**Caption (verbatim):**
*"Figure 2: The AREAL architecture featuring asynchronous generation and training components."*

### Figure 3 (p.4) ⭐深度解读
![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]]
> [!quote] caption
> Illustration of generation management in AREAL. Vertical lines show the ready time for the next step training. Blue crosses show the interrupted requests when new parameters arrive. 4

> [!tip] 技术解读（多模态）
> **Figure 2 — AREAL Architecture**

**Components & Data Flow:** Two decoupled GPU clusters. The *Generation* side hosts multiple Interruptible Rollout Workers (GPU) that send prompts (green) and trajectories (blue) through a Rollout Coordinator to a Replay Buffer. A Reward Service (CPU) returns rewards via the coordinator. The Replay Buffer sends aggregated batches through a Replay Buffer to Trainer Workers (GPU, Training cluster), which feed a Parameter Service. The Parameter Service emits interrupt signals (red) and parameter save/load updates (purple) back to the rollout workers, closing the async loop.

**Key takeaway (≤120 words):** AREAL fully decouples generation and training across separate GPU clusters coordinated via a Replay Buffer and Parameter Service. Rollout workers are *interruptible*: upon receiving new weights they discard stale KV state and continue decoding—enabling continuous, weight-updated trajectory generation without waiting for synchronized training steps. This eliminates the GPU underutilization and memory-IO bottleneck of synchronous RL.

**Caption (verbatim):**
*"Figure 2: The AREAL architecture featuring asynchronous generation and training components."*

### Figure 4 (p.8) ⭐深度解读
![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p08.png]]
> [!quote] caption
> The strong scaling trend. Dotted lines indicate ideal linear scaling. verl consistently encounters OOM with 32k context length and the 32B model so the data points are missing. 8

> [!tip] 技术解读（多模态）
> **Description of Figure 4 (Strong Scaling Trend):**

The figure is a 2×3 grid of line plots comparing training throughput across model size and context length. Rows distinguish context length (ctx=16384 top, ctx=32768 bottom); columns distinguish model size (1.5B, 7B, 32B left-to-right). The y-axis shows throughput in tokens/second; the x-axis shows the number of GPUs (ranging 32–512 depending on model size). Three series are plotted: AReaL (blue solid), verl (orange dashed), and ideal linear scaling (black dotted).

**Key Takeaway:** AReaL tracks the ideal linear scaling line closely across all six configurations, while verl falls progressively further below it as the number of GPUs grows — confirming AReaL's superior multi-node scaling efficiency for RL training.

**Caption (verbatim):**

Figure 4: The strong scaling trend. Dotted lines indicate ideal linear scaling. verl consistently encounters OOM with 32k context length and the 32B model so the data points are missing.

### Figure 5 (p.9) ⭐深度解读
![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p09.png]]
> [!quote] caption
> Ablation studies of the decoupled PPO objective and staleness control with a 1.5B model on math reasoning tasks. Both algorithmic choices are essential. With a moderate staleness value and the decoupled objective, training progress can be accelerated by over 2× while maintaining final evaluation performance.

> [!tip] 技术解读（多模态）
> ## Figure 5 Description

**Components/Data flow:** Figure 5 is a three-panel ablation study on a 1.5B model for math reasoning. Panel (a) plots training-reward learning curves under naive PPO across MaxStaleness values {0, 1, 2, 4, 8, 16, ∞}; panel (b) reproduces the same experiment with the decoupled PPO objective (eq. 5), where curves cluster tightly near the oracle (η=0). Panel (c) is a horizontal bar chart of effective training throughput (k tokens/s) vs. MaxStaleness, rising monotonically from 128.7 (η=0) to 396.8 (η=∞).

**Key technical takeaway:** The decoupled PPO objective stabilizes training against stale data, enabling moderate staleness (η ≤ 8) to more than triple throughput (≈3.1×) with negligible loss in final accuracy, whereas naive PPO collapses as staleness grows.

## Caption (verbatim)

**Figure 5:** Ablation studies of the decoupled PPO objective and staleness control with a 1.5B model on math reasoning tasks. Both algorithmic choices are essential. With a moderate staleness value and the decoupled objective, training progress can be accelerated by over 2× while maintaining final evaluation performance.

### Figure 6 (p.10) ⭐深度解读
![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p10.png]]
> [!quote] caption
> Ablation studies on system optimizations. experimental setup, we configured 32 micro-batches for the standard setting and established a token budget of 32,768 per micro-batch for the dynamic batching approach. As demonstrated in Figure 6a, dynamic batching yields an average of 30% throughput improvements across various model sizes.

> [!tip] 技术解读（多模态）
> **Figure description (≤120 words):**

Figure 6 presents two ablation bar charts rather than an architecture diagram. **Left (6a) — Dynamic vs. Normal Batching:** Compares throughput (TFLOPs/GPU) across model scales (1B/1 node, 7B/2 nodes, 32B/8 nodes). Dynamic batching consistently outperforms normal batching: 427.4 vs 404.4 (1B), 454.7 vs 303.1 (7B), and 387.7 vs 283.0 (32B), with the largest gap (~50%) at 7B. **Right (6b) — Interruptible Generation:** Compares average throughput (tokens/s) at 1.5B and 7B on 4 nodes. Interruptible generation yields 231k vs 207k (1.5B) and 130k vs 111k (7B). **Key takeaway:** Both optimizations are validated quantitatively—dynamic micro-batch allocation delivers ~30% throughput gains, and interruptible generation adds 12–17%, confirming their inclusion in the AREAL system design.

**Caption (verbatim):**

Figure 6: Ablation studies on system optimizations.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\pibehav(\cdot|s) = \begin{cases} \pi_{\theta+j}(\cdot|s) & \text{if } t_j\leq t\leq t_{j+1} \text{ and } s\in \mathcal{S}_t(q) \\ \text{arbitrary} & \text{otherwise} \end{cases}
$$

$$
J(\theta)= \mathbb{E}_{q\sim\mathcal{D}, a_t\sim\pi_\theta\left(\cdot|q,a_{<t}\right)} \left[ \sum_{t=1}^H \gamma^{t-1}r(s_t,a_t) \right].
$$

$$
J_\mathrm{PPO}(\theta)= \mathbb{E}_{q\sim\mathcal{D}, a_t\sim\pi_{\mathrm{old}}\left(\cdot|q,a_{<t}\right)} \left[ \sum_{t=1}^H \min\left( u_t(\theta)\hat{A}(s_t,a_t),\mathrm{clip}\left(u_t(\theta),1-\epsilon,1+\epsilon\right)\hat{A}(s_t,a_t)\right) \right],
$$

$$
\lfloor (N_r-1) /B \rfloor \leq i + \eta.
$$

$$
J(\theta)&= \mathbb{E}_{q\sim\mathcal{D}, a_t\sim\pibehav} \left[ \sum_{t=1}^H \min( \underset {{\text{Importance Ratio}}} { \boxed{ \frac{\pi_\theta}{\pibehav} } } \hat{A}_t,\quad \overbrace{ \frac{\piprox}{\pibehav} \mathrm{clip}( \underset{\text{Trust Region Center}}{ \boxed{ \frac{\pi_\theta}{\piprox} } } ,1-\epsilon,1+\epsilon )\hat{A}_t }^\text{Importance Ratio} ) \right] \\ &= \mathbb{E}_{q\sim\mathcal{D}, a_t\sim\pibehav} \left[ \sum_{t=1}^H \frac{\piprox}{\pibehav} \min\left( u_t^\mathrm{prox}(\theta)\hat{A}_t, \mathrm{clip}\left( u_t^\mathrm{prox}(\theta),1-\epsilon,1+\epsilon \right)\hat{A}_t) \right) \right],
$$

## 相关论文

- [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] — Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning
- [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] — DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEMENT LEARNING
- [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] — Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning
- [[hybridflow-a-flexible-and-efficient-rlhf-framework]] — HybridFlow: A Flexible and Efficient RLHF Framework

## 技术点深读（DEEP）

![[deep/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning.txt`（88470 字符）供引用检索。