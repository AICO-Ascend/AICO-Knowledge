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

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.11 `J𝑃𝑃𝑂(𝜃) = E[𝑞∼𝑃(𝑄), 𝑜∼𝜋𝜃𝑜𝑙𝑑(𝑂|𝑞)] 1`
- p.13 `𝑟𝑡= 𝑟𝜑(𝑞, 𝑜≤𝑡) −𝛽log 𝜋𝜃(𝑜𝑡|𝑞, 𝑜<𝑡)`
- p.13 `J𝐺𝑅𝑃𝑂(𝜃) = E[𝑞∼𝑃(𝑄), {𝑜𝑖}𝐺`
- p.14 `𝑖=1 ∼𝜋𝜃𝑜𝑙𝑑(· | 𝑞) for each question 𝑞∈D𝑏`
- p.14 `r = {𝑟1, 𝑟2, · · · , 𝑟𝐺} correspondingly. Subsequently, these rewards are normalized by subtracting`
- p.14 `the output as the normalized reward, i.e., ˆ𝐴𝑖,𝑡= e𝑟𝑖= 𝑟𝑖−mean(r)`
- p.18 `∇𝜃JA(𝜃) = E[(𝑞, 𝑜) ∼D`
- p.28 `J𝑆𝐹𝑇(𝜃) = E[𝑞, 𝑜∼𝑃𝑠𝑓𝑡(𝑄, 𝑂)]`
- p.28 `∇𝜃J𝑆𝐹𝑇= E[𝑞, 𝑜∼𝑃𝑠𝑓𝑡(𝑄, 𝑂)]`
- p.28 `J𝑅𝐹𝑇(𝜃) = E[𝑞∼𝑃𝑠𝑓𝑡(𝑄), 𝑜∼𝜋𝑠𝑓𝑡(𝑂|𝑞)]`
- p.28 `∇𝜃J𝑅𝐹𝑇(𝜃) = E[𝑞∼𝑃𝑠𝑓𝑡(𝑄), 𝑜∼𝜋𝑠𝑓𝑡(𝑂|𝑞)]`
- p.28 `∇𝜃J𝑂𝑛𝑅𝐹𝑇(𝜃) = E[𝑞∼𝑃𝑠𝑓𝑡(𝑄), 𝑜∼𝜋𝜃(𝑂|𝑞)]`
- p.29 `J𝐷𝑃𝑂(𝜃) = E[𝑞∼𝑃𝑠𝑓𝑡(𝑄), 𝑜+, 𝑜−∼𝜋𝑠𝑓𝑡(𝑂|𝑞)] log 𝜎©­`
- p.29 `∇𝜃J𝐷𝑃𝑂(𝜃) = E[𝑞∼𝑃𝑠𝑓𝑡(𝑄), 𝑜+, 𝑜−∼𝜋𝑠𝑓𝑡(𝑂|𝑞)] ©­`
- p.29 `J𝑃𝑃𝑂(𝜃) = E[𝑞∼𝑃𝑠𝑓𝑡(𝑄), 𝑜∼𝜋𝜃𝑜𝑙𝑑(𝑂|𝑞)] 1`

## 全文文本
全文已存 `extraction/fulltext/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models.txt`（81353 字符）供引用检索。