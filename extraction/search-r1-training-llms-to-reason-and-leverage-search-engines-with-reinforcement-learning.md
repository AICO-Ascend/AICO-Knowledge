---
paper_num: "25"
title: "Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning"
authors: "Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning Bowen Jin1, Hansi Zeng2, Zhenrui Yue1, Jinsung Yoon3, Sercan ¨O. Arık3, Dong Wang1, Hamed Zamani2, Jiawei Han1 1 Department of Co"
date: "—"
arxiv: "https://arxiv.org/abs/2503.09516"
pdf: "papers/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning.pdf"
slug: "search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning"
tags: [training, rl]
---

# Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning

> [!abstract] 摘要（原文）
> 1\. 💡 SEARCH-R1 提出了一种新颖的强化学习 (RL) 框架，使大型语言模型 (LLMs) 能够学习自主生成搜索查询，并将推理与实时检索交错进行，以有效获取外部知识。 2. ⚙️ 该框架将搜索引擎建模为 RL 环境的一部分，通过检索令牌掩蔽 (retrieved token masking) 确保训练稳定性，并支持多轮推理与检索交互，使用 \<search>、\<information> 和 \<think> 等特定令牌进行结构化决策。 3. 📈 在七个问答数据集上的实验表明，SEARCH-R1 在相同设置下比 RAG 基线表现出显著的性能提升，并提供了关于 RL 优化方法、LLM 选择及响应长度动力学的宝贵见解。

## 元信息
- **发表日期**: —
- **作者**: Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning Bowen Jin1, Hansi Zeng2, Zhenrui Yue1, Jinsung Yoon3, Sercan ¨O. Arık3, Dong Wang1, Hamed Zamani2, Jiawei Han1 1 Department of Co
- **arXiv**: https://arxiv.org/abs/2503.09516
- **本地 PDF**: `papers/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning.pdf`
- **页数**: 31

## 图表（原文 caption + 页码）

### Figure 1 (p.4) ⭐深度解读
![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p04.png]]
> [!quote] caption
> Demonstration of PPO and GRPO training with the search engine (SEARCH-R1).

> [!tip] 技术解读（多模态）
> **Figure 1 — Architecture / Components / Data Flow**

Two parallel pipelines (top: PPO; bottom: GRPO) start with query *q* entering a **Rollout Module** that couples a trained **Policy LLM** (yellow) with a **Search Engine** (blue), enabling multi-turn retrieval-and-reasoning. Rollout output(s) *o* are scored by frozen **Reward** and **Reference LLMs** (green) producing reward *r*. In PPO, a trained **Value LLM** also produces *v*; (*v*, *r*) feeds **GAE** → per-token advantage *A*. GRPO skips the value model: it samples *G* rollouts (*o₁…o_G*), scores each (*r₁…r_G*), and uses **Group Computation** to derive group-relative advantages (*A₁…A_G*), with a KL constraint (vs. reference) back to the policy.

**Key takeaway:** Unlike prior RL that rollout solely from π_θ(·|x), this framework makes the policy explicitly retrieval-aware via π_θ(·|x;ℛ), and uses **loss masking** so gradients update only LLM-generated tokens, not retrieved content — stabilizing training while preserving search-augmented reasoning.

**Caption (verbatim):** "Figure 1: Demonstration of PPO and GRPO training with the search engine (SEARCH-R1). During the rollout, LLMs can conduct multi-turn interactions with the search engine."

### Figure 2 (p.9) ⭐深度解读
![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p09.png]]
> [!quote] caption
> (a) PPO vs. GRPO: GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO provides more stable optimization but converges at a slower rate. (b) Base vs. Instruct LLM study: Instruction-tuned LLMs converge faster, but the final performance of both modles remains highly similar. (c)

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 2):**

The figure presents four training-dynamics subplots for Search-R1 (a reinforcement-learning framework combining LLM reasoning with search engine retrieval):

- **(a) PPO vs. GRPO**: Compares two RL algorithms on Train Reward vs. Step curves (0–500 steps). GRPO (orange) converges faster but shows instability spikes, while PPO (blue) converges more slowly yet stably.
- **(b) Base vs. Instruct**: Compares Qwen2.5 base vs. instruction-tuned LLMs over 0–200 steps. Instruct (orange) starts higher and rises faster; Base (blue) climbs more slowly but converges to similar reward (~0.40).
- **(c) Response Length**: Dual-axis plot showing Response Length (blue, 900–1150 tokens) and Train Reward (red) over 0–200 steps. Length decreases initially, then increases alongside reward.
- **(d) # Valid Search**: Dual-axis plot tracking valid search-call count (blue, ~1.4–2.0) and reward (red) over steps — both grow together as training proceeds.

**Key Technical Takeaway:** Search-R1 exhibits a two-phase learning dynamic — early-stage response compression followed by reward-driven expansion through increased retrieval calls — and retrieved-token loss masking yields consistently superior QA performance (NQ 0.480 vs. 0.388; avg. 0.431 vs. 0.343).

**Verbatim Caption:**

"Figure 2: (a) PPO vs. GRPO: GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO provides more stable optimization but converges at a slower rate. (b) Base vs. Instruct LLM study: Instruction-tuned LLMs converge faster, but the final performance of both modles remains highly similar. (c) Response length study: The response length exhibits a decrease-increase-stabilize trend throughout training, aligning with the overall performance trajectory of the LLM. (d) # Valid search study: As the training proceeds, the LLM learns to call search more."

### Figure 3 (p.17) ⭐深度解读
![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]]
> [!quote] caption
> Retrieved Token Loss Masking Study instruction-tuned models exhibit faster convergence and benefit from higher initial perfor- mance relative to their base counterparts. Despite this early advantage, the final performance of both model types converges to a similar level after training. These results indicate that while instruction tuning facilitates more efficient early-stage learning in reasoning

> [!tip] 技术解读（多模态）
> **Figure 3 — Retrieved Token Loss Masking Study**

The figure presents two side-by-side line plots comparing training reward trajectories across RL steps. Each subplot shows two curves: "w. mask" (blue, with error bars) versus "w.o. mask" (orange, with error bars). Subplot (a) tracks Qwen-2.5-3b-base over ~400 steps with reward range 0.0–0.4; subplot (b) tracks Qwen-2.5-7b-base over ~250 steps with reward 0.10–0.50. Both curves rise together initially, but the unmasked (orange) curve collapses to near-zero reward at the end of training in both models, while the masked (blue) curve remains stable.

**Key takeaway:** Masking the loss on retrieved tokens is essential — without it, training reward collapses late in optimization, whereas masking preserves stable convergence across model scales.

**Caption (verbatim):** "Figure 3: Retrieved Token Loss Masking Study"

### Figure 4 (p.17) ⭐深度解读
![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]]
> [!quote] caption
> Study of SEARCH-R1 on base and instruct LLMs. The instruction model converges faster and starts from a better initial performance. However, the final performance of both models is very similar. F

> [!tip] 技术解读（多模态）
> **Figure 3 — Retrieved Token Loss Masking Study**

The figure presents two side-by-side line plots comparing training reward trajectories across RL steps. Each subplot shows two curves: "w. mask" (blue, with error bars) versus "w.o. mask" (orange, with error bars). Subplot (a) tracks Qwen-2.5-3b-base over ~400 steps with reward range 0.0–0.4; subplot (b) tracks Qwen-2.5-7b-base over ~250 steps with reward 0.10–0.50. Both curves rise together initially, but the unmasked (orange) curve collapses to near-zero reward at the end of training in both models, while the masked (blue) curve remains stable.

**Key takeaway:** Masking the loss on retrieved tokens is essential — without it, training reward collapses late in optimization, whereas masking preserves stable convergence across model scales.

**Caption (verbatim):** "Figure 3: Retrieved Token Loss Masking Study"

### Figure 5 (p.18) ⭐深度解读
![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p18.png]]
> [!quote] caption
> Training dynamics of SEARCH-R1 with PPO and GRPO as the base RL method across four LLMs. GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO provides more stable optimization but converges at a slower rate. PPO and GRPO achieve comparable final reward performance. G

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 5):**

**Architecture/Components:** Four-panel grid of training-reward line plots (x = Step, y = Train Reward), each comparing two RL methods—**PPO** (blue) vs. **GRPO** (orange)—across four LLMs: (a) Qwen2.5-3b-base, (b) Qwen2.5-3b-it, (c) Qwen2.5-7b-base, (d) Qwen2.5-7b-it. Steps range 0–500 for base models and 0–300 for instruction-tuned variants; reward ranges ~0.1–0.5.

**Data flow:** Training-step progression → policy updates via PPO (with critic/value function) vs. GRPO (critic-free, group-relative) → logged reward trajectories.

**Key takeaway (≤120 words):** GRPO climbs faster but suffers *reward collapse* mid-training in every panel, dropping sharply before partially recovering. PPO rises more slowly yet stays monotonically stable. Both converge to comparable terminal rewards (~0.35–0.45), demonstrating that PPO's stability comes at the cost of sample efficiency, while GRPO trades reliability for faster early progress—an important consideration when selecting an RL backbone for Search-R1.

**Caption (verbatim):**
"Figure 5: Training dynamics of SEARCH-R1 with PPO and GRPO as the base RL method across four LLMs. GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO provides more stable optimization but converges at a slower rate. PPO and GRPO achieve comparable final reward performance."

### Figure 6 (p.19) ⭐深度解读
![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]]
> [!quote] caption
> The training dynamics of SEARCH-R1 with a different number of retrieved pas- sages. (LLM: Qwen2.5-7b-base, RL: PPO)

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Figure 6** plots **training reward (y-axis, 0.1–0.5) vs. optimization step (x-axis, 0–500)** for the SEARCH-R1 pipeline (LLM: Qwen2.5-7b-base, RL: PPO). Three curves compare retrieval depths — `topk=1` (blue), `topk=3` (orange), `topk=5` (green). All settings start near 0.1, rise steeply until ~step 200, and plateau around 0.45–0.5 with mild oscillation.

**Key takeaway:** Retrieval depth (1 vs. 3 vs. 5 passages) yields nearly identical reward trajectories, suggesting top-k is not the dominant driver of PPO convergence in SEARCH-R1 — corroborated by Table 7, where topk=3 modestly wins on average (0.431) over topk=1 (0.375) and topk=5 (0.400).

---

## Caption (verbatim)

**Figure 6:** The training dynamics of SEARCH-R1 with a different number of retrieved passages. (LLM: Qwen2.5-7b-base, RL: PPO)

**Figure 7:** The training dynamics of SEARCH-R1 (GRPO) with different group size. (LLM: Qwen2.5-7b-base)

### Figure 7 (p.19) ⭐深度解读
![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]]
> [!quote] caption
> We observe that a larger group size generally leads to faster convergence but may also increase the risk of collapse due to the inherent instability of reinforcement learning.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Figure 6** plots **training reward (y-axis, 0.1–0.5) vs. optimization step (x-axis, 0–500)** for the SEARCH-R1 pipeline (LLM: Qwen2.5-7b-base, RL: PPO). Three curves compare retrieval depths — `topk=1` (blue), `topk=3` (orange), `topk=5` (green). All settings start near 0.1, rise steeply until ~step 200, and plateau around 0.45–0.5 with mild oscillation.

**Key takeaway:** Retrieval depth (1 vs. 3 vs. 5 passages) yields nearly identical reward trajectories, suggesting top-k is not the dominant driver of PPO convergence in SEARCH-R1 — corroborated by Table 7, where topk=3 modestly wins on average (0.431) over topk=1 (0.375) and topk=5 (0.400).

---

## Caption (verbatim)

**Figure 6:** The training dynamics of SEARCH-R1 with a different number of retrieved passages. (LLM: Qwen2.5-7b-base, RL: PPO)

**Figure 7:** The training dynamics of SEARCH-R1 (GRPO) with different group size. (LLM: Qwen2.5-7b-base)

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathcal{J}_{GRPO}(\theta) = \, & \mathbb{E}_{x \sim \mathcal{D}, \{ y_i \}_{i=1}^{G} \sim \pi_{\text{old}}( \cdot| x; \se)} \Bigg[ \frac{1}{G} \sum_{i=1}^{G} \frac{1}{\sum_{t=1}^{|y_i|} I(y_{i,t})} \sum_{t=1: I(y_{i,t})=1}^{|y_i|} \min \Bigg( \frac{\pi_{\theta}(y_{i,t} | x, y_{i,<t}; \se)}{\pi_{\text{old}}(y_{i,t} | x, y_{i,<t}; \se)} \hat{A}_{i,t}, \nonumber \\[8pt] & \hspace{120pt} \text{clip} \Bigg( \frac{\pi_{\theta}(y_{i,t} | x, y_{i,<t}; \se)}{\pi_{\text{old}}(y_{i,t} | x, y_{i,<t}; \se)}, 1 - \epsilon, 1 + \epsilon \Bigg) \hat{A}_{i,t} \Bigg) - \beta \mathbb{D}_{KL} \left[ \pi_{\theta} || \pi_{\text{ref}} \right] \Bigg],
$$

$$
\max_{\pi_\theta} \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi_{\theta}(\cdot \mid x; \se)} \left[ r_{\phi}(x, y) \right] - \beta \mathbb{D}_{\text{KL}} \left[ \pi_{\theta}(y \mid x; \se) \,||\, \pi_{\text{ref}}(y \mid x; \se) \right],
$$

$$
\mathcal{J}_{PPO}(\theta) = \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi_{\text{old}}( \cdot| x; \se)} \left[ \frac{1}{\sum_{t=1}^{|y|} I(y_t)} \sum_{t=1: I(y_t)=1}^{|y|} \min \left( \frac{\pi_{\theta}(y_t | x, y_{<t}; \se)}{\pi_{\text{old}}(y_t | x, y_{<t}; \se)} A_t, \text{clip} \left( \frac{\pi_{\theta}(y_t | x, y_{<t}; \se)}{\pi_{\text{old}}(y_t | x, y_{<t}; \se)}, 1 - \epsilon, 1 + \epsilon \right) A_t \right) \right],
$$

$$
r_{\phi}(x, y) = \text{EM}(a_\text{pred}, a_\text{gold}),
$$

## 相关论文

- [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] — DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
- [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] — From ATOP to ZCube: Automated Topology Optimization Pipeline and A Highly Cost-Effective Network Topology for Large Model Training
- [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] — Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEMENT LEARNING
- [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] — AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning

## 技术点深读（DEEP）

![[deep/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning.txt`（100895 字符）供引用检索。