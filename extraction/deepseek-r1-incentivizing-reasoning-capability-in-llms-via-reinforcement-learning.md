---
paper_num: "34"
title: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning"
authors: "Reinforcement Learning DeepSeek-AI research@deepseek.com"
date: "2026/1/17"
arxiv: "https://arxiv.org/abs/2501.12948"
pdf: "papers/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning.pdf"
slug: "deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning"
tags: [rl]
---

# DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning

> [!abstract] 摘要（原文）
> 1\. 🤖 DeepSeek-R1-Zero展示了大型语言模型可以通过纯强化学习（RL）在没有监督微调的情况下发展出强大的推理能力，并涌现出如自我验证等有趣行为。 2. ✨ 为解决DeepSeek-R1-Zero的局限并进一步提升性能，DeepSeek-R1采用了多阶段训练流程，结合冷启动数据和迭代强化学习，使其推理能力达到与OpenAI-o1-1217相当的水平。 3. 🚀 研究还表明，将DeepSeek-R1的推理模式蒸馏到小型模型中比直接在小模型上进行大规模RL训练更有效，并开源了多个稠密模型。

## 元信息
- **发表日期**: 2026/1/17
- **作者**: Reinforcement Learning DeepSeek-AI research@deepseek.com
- **arXiv**: https://arxiv.org/abs/2501.12948
- **本地 PDF**: `papers/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning.pdf`
- **页数**: 86

## 图表（原文 caption + 页码）

### Figure 2 (p.6)
![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p06.png]]
> [!quote] caption
> In the initial stage, we collect thousands of cold-start data that exhibits a conversational, human-aligned thinking process. RL training is then applied to improve the model perfor- mance with the conversational thinking process and language consistency. Subsequently, we apply rejection sampling and SFT once more. This stage incorporates both reasoning and non- reasoning datasets into the SFT pro

### Figure 3 (p.14)
![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p14.png]]
> [!quote] caption
> For each question ? , GRPO samples a group of outputs f= 1, = 2,    , = g from the old policy 14

### Figure 6 (p.35)
![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p35.png]]
> [!quote] caption
> B.6. Ablation Study of Language Consistency Reward

### Figure 7 (p.37)
![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p37.png]]
> [!quote] caption
> As can be seen, without the LC reward, language consistency gradually deteriorates as train- ing steps increase. However, when the LC reward is applied, stable language consistency is maintained throughout the training process. For benchmark performance, the model main- tains comparable performance on the mathematical benchmark, while a slight degradation is observed on the coding benchmark. Altho

### Figure 13 (p.48)
![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p48.png]]
> [!quote] caption
> We have categorized potential content safety challenges faced by language models into 4 major categories and 28 subcategories.

### Figure 14 (p.53)
![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p53.png]]
> [!quote] caption
> For DeepSeek-V3 and DeepSeek-R1, we evaluated safety scores for models with and without the risk control system (introduced in D.3.1). Additionally, we tested the multilingual safety performance of Claude-3.7-Sonnet and GPT-4o(2024-05-13). From Figure 14, we can draw the following conclusions: • With risk control system in place, DeepSeek-V3 (86.5%) and DeepSeek-R1 (85.9%) achieve total safety sco

## 全文文本
全文已存 `extraction/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning.txt`（223572 字符）供引用检索。