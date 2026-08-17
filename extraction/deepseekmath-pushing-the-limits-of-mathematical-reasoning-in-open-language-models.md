---
paper_num: "22"
title: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models"
authors: "Reasoning in Open Language Models Zhihong Shao1,2∗†, Peiyi Wang1,3∗†, Qihao Zhu1,3∗†, Runxin Xu1, Junxiao Song1 Xiao Bi1, Haowei Zhang1, Mingchuan Zhang1, Y.K. Li1, Y. Wu1, Daya Guo1∗ 1DeepSeek-AI, 2Tsinghua University, "
date: "2026/1/19"
arxiv: "https://arxiv.org/abs/2402.03300"
pdf: "papers/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models.pdf"
slug: "deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models"
tags: []
---

# DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models

> [!abstract] 摘要（原文）
> 1\. 💡 DeepSeekMath 7B 是一个开放语言模型，通过在DeepSeek-Coder-Base-v1.5 7B基础上进行120B数学相关token的预训练，在MATH benchmark上实现了51.7%的Top1准确率，接近GPT-4和Gemini-Ultra的性能。 2. 🛠️ 模型的出色表现归因于从Common Crawl中精心筛选的120B高质量DeepSeekMath Corpus，以及引入了Group Relative Policy Optimization (GRPO)——一种无需critic模型的PPO变体，显著优化了强化学习资源消耗。 3. 🔬 论文还探讨了Code训练对数学推理的积极作用，并提出了一个统一的RL范式来分析不同算法，指出强化学习主要通过提升Maj@K来增强模型性能，而非直接提升其基础能力。

## 元信息
- **发表日期**: 2026/1/19
- **作者**: Reasoning in Open Language Models Zhihong Shao1,2∗†, Peiyi Wang1,3∗†, Qihao Zhu1,3∗†, Runxin Xu1, Junxiao Song1 Xiao Bi1, Haowei Zhang1, Mingchuan Zhang1, Y.K. Li1, Y. Wu1, Daya Guo1∗ 1DeepSeek-AI, 2Tsinghua University, 
- **arXiv**: https://arxiv.org/abs/2402.03300
- **本地 PDF**: `papers/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models.pdf`
- **页数**: 30

## 图表（原文 caption + 页码）
_未检测到带 caption 的 figure_

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\footnotesize \mathcal{J}_{PPO}(\theta) = \mathbb{E}{[q \sim P(Q), o \sim \pi_{\theta_{old}}(O|q)]} \frac{1}{|o|} \sum_{t=1}^{|o|} \min \left[ \frac{\pi_\theta(o_{t} | q, o_{<t})}{\pi_{\theta_{old}}(o_{t} | q, o_{<t})} A_{t}, \text{clip} \left( \frac{\pi_\theta(o_{t} | q, o_{<t})}{\pi_{\theta_{old}}(o_{t} | q, o_{<t})}, 1 - \epsilon, 1 + \epsilon \right) A_{t} \right] ,
$$

$$
r_{t} = r_\phi(q, o_{\le t}) - \beta \log\frac{\pi_{\theta}(o_{t}|q, o_{<t})}{\pi_{ref}(o_{t}|q, o_{<t})},
$$

$$
\footnotesize \begin{split} \mathcal{J}_{GRPO}(\theta) &= \mathbb{E}{[q \sim P(Q), \{o_i\}_{i=1}^G \sim \pi_{\theta_{old}}(O|q)]} \\ & \frac{1}{G}\sum_{i=1}^G\frac{1}{|o_i|} \sum_{t=1}^{|o_i|} \left\{ \min \left[ \frac{\pi_\theta(o_{i,t} | q, o_{i,<t})}{\pi_{\theta_{old}}(o_{i,t} | q, o_{i,<t})} \hat{A}_{i,t}, \text{clip} \left( \frac{\pi_\theta(o_{i,t} | q, o_{i,<t})}{\pi_{\theta_{old}}(o_{i,t} | q, o_{i,<t})}, 1 - \epsilon, 1 + \epsilon \right) \hat{A}_{i,t} \right] - \beta \mathbb{D}_{KL}\left[\pi_{\theta} || \pi_{ref}\right]\right\} , \end{split}
$$

$$
\small \mathbb{D}_{KL}\left[\pi_{\theta} || \pi_{ref}\right] = \frac{\pi_{ref}(o_{i,t}|q,o_{i,<t})}{\pi_{\theta}(o_{i,t}|q,o_{i,<t})}- \log\frac{\pi_{ref}(o_{i,t}|q,o_{i,<t})}{\pi_{\theta}(o_{i,t}|q,o_{i,<t})} - 1,
$$

$$
\nabla_{\theta}\mathcal{J}_{\textcolor{red}{\mathcal{A}}}(\theta) = \mathbb{E}[\underbrace{(q,o) \sim \textcolor{red}{\mathcal{D}}}_{Data \ Source}]\left( \frac{1}{|o|} \sum_{t=1}^{|o|} \underbrace{GC_{{\mathcal{A}}}(q, o, t, \textcolor{red}{\pi_{{rf}}})}_{Gradient \ Coefficient} \nabla_{\theta}\log \pi_{\theta}(o_t | q, o_{<t})\right).
$$

$$
\mathcal{J}_{SFT}(\theta)=\mathbb{E}[q, o \sim P_{sft}(Q, O)]\left(\frac{1}{|o|}\sum_{t=1}^{|o|} \log \pi_\theta(o_t | q, o_{<t})\right).
$$

$$
\nabla_{\theta}\mathcal{J}_{SFT} = \mathbb{E}[q, o \sim P_{sft}(Q, O)]\left(\frac{1}{|o|}\sum_{t=1}^{|o|} \nabla_{\theta} \log \pi_\theta(o_{t} | q, o_{<t})\right).
$$

$$
\mathcal{J}_{RFT}(\theta)= \mathbb{E}[q \sim P_{sft}(Q), o \sim \pi_{sft}(O|q)]\left( \frac{1}{|o|}\sum_{t=1}^{|o|} \mathbb{I}(o) \log \pi_\theta(o_{t} | q, o_{<t})\right).
$$

$$
\nabla_{\theta}\mathcal{J}_{RFT}(\theta)= \mathbb{E}[{q \sim P_{sft}(Q), o \sim \pi_{sft}(O|q)}]\left( \frac{1}{|o|}\sum_{t=1}^{|o|} {\mathbb{I}(o)} \nabla_{\theta}\log \pi_\theta(o_{t} | q, o_{<t})\right).
$$

$$
GC_{RFT}(q, o, t) = \mathbb{I}(o)=\left\{ \begin{aligned} 1 & & {\rm the \ answer \ of \ o \ is \ correct} \\ 0 & & {\rm the \ answer \ of \ o \ is \ incorrect} \\ \end{aligned} \right.
$$

$$
\nabla_{\theta}\mathcal{J}_{OnRFT}(\theta)= \mathbb{E}[{q \sim P_{sft}(Q), o \sim \pi_{\theta}(O|q)}]\left( \frac{1}{|o|}\sum_{t=1}^{|o|} {\mathbb{I}(o)} \nabla_{\theta}\log \pi_\theta(o_{t} | q, o_{<t})\right).
$$

$$
\footnotesize \begin{split} \mathcal{J}_{DPO}(\theta) = \mathbb{E}{[q \sim P_{sft}(Q), o^+, o^- \sim \pi_{sft}(O|q)]} \log \sigma \left( \beta \frac{1}{|o^+|}\sum_{t=1}^{|o^+|} \log \frac{\pi_{\theta}(o^+_t | q, o^+_{<t})}{\pi_{\text{ref}}(o^+_t | q, o^+_{<t})} - \beta \frac{1}{|o^-|}\sum_{t=1}^{|o^-|} \log \frac{\pi_{\theta}(o^-_{<t} | q, o^-_{<t})}{\pi_{\text{ref}}(o^-_{<t} | q,o^-_{<t})} \right) \end{split}
$$

$$
\footnotesize \begin{split} \nabla_{\theta}\mathcal{J}_{DPO}(\theta) = \mathbb{E}{[q \sim P_{sft}(Q), o^+, o^- \sim \pi_{sft}(O|q)]} & \left( \frac{1}{|o^+|}\sum_{t=1}^{|o^+|} GC_{DPO} (q,o,t) \nabla_{\theta}\log\pi_{\theta}(o^+_t | q, o^+_{<t}) \right. \\ - & \left. \frac{1}{|o^-|}\sum_{t=1}^{|o^-|} GC_{DPO} (q,o,t) \nabla_{\theta}\log\pi_{\theta}(o^-_t | q, o^-_{<t}) \right) \end{split}
$$

$$
\footnotesize GC_{DPO}(q,o,t) = \sigma\left(\beta\log \frac{\pi_{\theta}(o^-_t | q, o^-_{<t})}{\pi_{\text{ref}}(o^-_t | q, o^-_{<t})} - \beta\log \frac{\pi_{\theta}(o^+_t | q, o^+_{<t})}{\pi_{\text{ref}}(o^+_t | q, o^+_{<t})}\right)
$$

$$
\footnotesize \mathcal{J}_{PPO}(\theta) = \mathbb{E}{[q \sim P_{sft}(Q), o \sim \pi_{\theta_{old}}(O|q)]} \frac{1}{|o|} \sum_{t=1}^{|o|} \min \left[ \frac{\pi_\theta(o_{t} | q, o_{<t})}{\pi_{\theta_{old}}(o_{t} | q, o_{<t})} A_{t}, \text{clip} \left( \frac{\pi_\theta(o_{t} | q, o_{<t})}{\pi_{\theta_{old}}(o_{t} | q, o_{<t})}, 1 - \epsilon, 1 + \epsilon \right) A_{t} \right].
$$

$$
\footnotesize \begin{split} \nabla_{\theta}\mathcal{J}_{PPO}(\theta) = \mathbb{E}{[q \sim P_{sft}(Q), o \sim \pi_{\theta_{old}}(O|q)]} \frac{1}{|o|} \sum_{t=1}^{|o|} A_t \nabla_{\theta}\log \pi_\theta(o_{t} | q, o_{<t}) \end{split}
$$

$$
GC_{PPO}(q, o, t, \pi_{\theta_{rm}}) = A_t,
$$

$$
\footnotesize \begin{split} \mathcal{J}_{GRPO}(\theta) &= \mathbb{E}{[q \sim P_{sft}(Q), \{o_i\}_{i=1}^G \sim \pi_{\theta_{old}}(O|q)]} \\ & \frac{1}{G}\sum_{i=1}^G\frac{1}{|o_i|} \sum_{t=1}^{|o_i|} \left[\frac{\pi_\theta(o_{i,t} | q, o_{i,<t})}{\pi_{\theta_{old}}(o_{i,t} | q, o_{i,<t})} \hat{A}_{i,t} - \beta (\frac{\pi_{ref}(o_{i,t}|q,o_{i,<t})}{\pi_{\theta}(o_{i,t}|q,o_{i,<t})}- \log\frac{\pi_{ref}(o_{i,t}|q,o_{i,<t})}{\pi_{\theta}(o_{i,t}|q,o_{i,<t})} - 1)\right]. \end{split}
$$

$$
\footnotesize \begin{split} \nabla_{\theta}\mathcal{J}_{GRPO}(\theta) & = \mathbb{E}{[q \sim P_{sft}(Q), \{o_i\}_{i=1}^G \sim \pi_{\theta_{old}}(O|q)]} \\ & \frac{1}{G}\sum_{i=1}^G\frac{1}{|o_i|} \sum_{t=1}^{|o_i|} \left[\hat{A}_{i,t} + \beta \left(\frac{\pi_{ref}(o_{i,t}|o_{i,<t})}{\pi_{\theta}(o_{i,t}|o_{i,<t})} - 1\right)\right] \nabla_{\theta}\log \pi_\theta(o_{i,t} | q, o_{i,<t}). \end{split}
$$

$$
\footnotesize GC_{GRPO}(q, o, t, \pi_{\theta_{rm}}) = \hat{A}_{i,t} + \beta \left(\frac{\pi_{ref}(o_{i,t}|o_{i,<t})}{\pi_{\theta}(o_{i,t}|o_{i,<t})} - 1\right),
$$

## 全文文本
全文已存 `extraction/fulltext/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models.txt`（81353 字符）供引用检索。