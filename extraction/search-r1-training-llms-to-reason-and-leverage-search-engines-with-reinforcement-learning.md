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

### Figure 1 (p.4)
![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p04.png]]
> [!quote] caption
> Demonstration of PPO and GRPO training with the search engine (SEARCH-R1).

### Figure 2 (p.9)
![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p09.png]]
> [!quote] caption
> (a) PPO vs. GRPO: GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO provides more stable optimization but converges at a slower rate. (b) Base vs. Instruct LLM study: Instruction-tuned LLMs converge faster, but the final performance of both modles remains highly similar. (c)

### Figure 3 (p.17)
![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]]
> [!quote] caption
> Retrieved Token Loss Masking Study instruction-tuned models exhibit faster convergence and benefit from higher initial perfor- mance relative to their base counterparts. Despite this early advantage, the final performance of both model types converges to a similar level after training. These results indicate that while instruction tuning facilitates more efficient early-stage learning in reasoning

### Figure 4 (p.17)
![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]]
> [!quote] caption
> Study of SEARCH-R1 on base and instruct LLMs. The instruction model converges faster and starts from a better initial performance. However, the final performance of both models is very similar. F

### Figure 5 (p.18)
![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p18.png]]
> [!quote] caption
> Training dynamics of SEARCH-R1 with PPO and GRPO as the base RL method across four LLMs. GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO provides more stable optimization but converges at a slower rate. PPO and GRPO achieve comparable final reward performance. G

### Figure 6 (p.19)
![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]]
> [!quote] caption
> The training dynamics of SEARCH-R1 with a different number of retrieved pas- sages. (LLM: Qwen2.5-7b-base, RL: PPO)

### Figure 7 (p.19)
![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]]
> [!quote] caption
> We observe that a larger group size generally leads to faster convergence but may also increase the risk of collapse due to the inherent instability of reinforcement learning.

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
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM REINFORCEMENT LEARNING
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEMENT LEARNING
- [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] — AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning

## 全文文本
全文已存 `extraction/fulltext/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning.txt`（100895 字符）供引用检索。