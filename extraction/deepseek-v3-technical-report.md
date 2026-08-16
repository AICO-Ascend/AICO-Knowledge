---
paper_num: "41"
title: "DeepSeek-V3 Technical Report"
authors: "DeepSeek-AI research@deepseek.com"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2412.19437"
pdf: "papers/deepseek-v3-technical-report.pdf"
slug: "deepseek-v3-technical-report"
tags: []
---

# DeepSeek-V3 Technical Report

> [!abstract] 摘要（原文）
> 1\. 🤖 DeepSeek-V3是一个拥有671B总参数和37B激活参数的强大MoE语言模型，其核心创新包括无辅助损失的负载均衡策略和Multi-Token Prediction训练目标。 2. 🚀 该模型通过高效的FP8混合精度训练框架和DualPipe算法，实现了近乎完全的计算-通信重叠，并以仅2.788M H800 GPU小时的经济成本完成了14.8T tokens的预训练。 3. 🏆 综合评估表明，DeepSeek-V3在知识、代码和数学等多个基准测试中超越了其他开源模型，并达到了与GPT-4o和Claude-3.5-Sonnet等领先闭源模型相当的性能。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: DeepSeek-AI research@deepseek.com
- **arXiv**: https://arxiv.org/abs/2412.19437
- **本地 PDF**: `papers/deepseek-v3-technical-report.pdf`
- **页数**: 53

## 图表（原文 caption + 页码）

### Figure 5 (p.12)
![[assets/deepseek-v3-technical-report-p12.png]]
> [!quote] caption
> It employs a bidirectional pipeline scheduling, which feeds micro-batches from both ends of the pipeline simultaneously and a significant portion of communications can be fully overlapped. This overlap also ensures that, as the model further scales up, as long as we maintain a constant computation-to-communication ratio, we can still employ fine-grained experts across nodes while achieving a near-

### Figure 6 (p.15)
![[assets/deepseek-v3-technical-report-p15.png]]
> [!quote] caption
> Firstly, in order to accelerate model training, the majority of core computation kernels, i.e., GEMM operations, are implemented in FP8 precision. These GEMM operations accept FP8 tensors as inputs and produce outputs in BF16 or FP32. As depicted in Figure 6, all three GEMMs associated with the Linear operator, namely Fprop (forward pass), Dgrad (activation backward pass), and Wgrad (weight backwa

### Figure 10 (p.48)
![[assets/deepseek-v3-technical-report-p48.png]]
> [!quote] caption
> 48

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.11 `where [·; ·] denotes concatenation. Especially, when 𝑘= 1, h𝑘−1`
- p.23 `scale 𝑠= 40, 𝛼= 1, 𝛽= 32, and the scaling factor √`
- p.30 `J𝐺𝑅𝑃𝑂(𝜃) = E[𝑞∼𝑃(𝑄), {𝑜𝑖}𝐺`
- p.30 `𝐴𝑖= 𝑟𝑖−mean({𝑟1, 𝑟2, · · · , 𝑟𝐺})`

## 全文文本
全文已存 `extraction/fulltext/deepseek-v3-technical-report.txt`（150416 字符）供引用检索。