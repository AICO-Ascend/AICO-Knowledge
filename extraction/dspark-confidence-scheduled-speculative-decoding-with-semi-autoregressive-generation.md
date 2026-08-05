---
paper_num: "8"
title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
authors: "Semi-Autoregressive Generation Xin Cheng1,2,∗, Xingkai Yu2,∗, Chenze Shao2,∗, Jiashi Li2,∗, Yunfan Xiong2,∗ Yi Qian2, Jiaqi Zhu2, Shirong Ma2, Xiaokang Zhang2, Jiasheng Ye2, Qinyu Chen2, Chengqi Deng2, Jiping Yu2, Damai "
date: "2024/1/1"
arxiv: "https://arxiv.org/abs/2607.05147"
pdf: "papers/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation.pdf"
slug: "dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation"
tags: [speculative]
---

# DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation

> [!abstract] 摘要（原文）
> 1\. 🚀 DSpark 引入了一种半自回归生成架构，通过在并行主干网络中集成轻量级序列模块，在保持高吞吐生成速度的同时，有效缓解了传统并行 Draft model 常见的后缀准确率衰减问题。 2. 💡 为了优化系统级效率，DSpark 提出了置信度调度验证（Confidence-Scheduled Verification）机制，利用校准后的生存概率和负载感知调度器，根据实时引擎负载动态分配验证预算，从而最大化整体吞吐量。 3. 📈 大规模生产部署实测表明，DSpark 相比现有工业基线显著扩展了交互边界，在满足严格时延约束的前提下，将生成速度提升了 60%–85%，有效突破了 LLM 在高并发 serving 系统中的性能瓶颈。

## 元信息
- **发表日期**: 2024/1/1
- **作者**: Semi-Autoregressive Generation Xin Cheng1,2,∗, Xingkai Yu2,∗, Chenze Shao2,∗, Jiashi Li2,∗, Yunfan Xiong2,∗ Yi Qian2, Jiaqi Zhu2, Shirong Ma2, Xiaokang Zhang2, Jiasheng Ye2, Qinyu Chen2, Chengqi Deng2, Jiping Yu2, Damai 
- **arXiv**: https://arxiv.org/abs/2607.05147
- **本地 PDF**: `papers/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation.pdf`
- **页数**: 33

## 图表（原文 caption + 页码）

### Figure 1 (p.4)
![[assets/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation-p04.png]]
> [!quote] caption
> Recall from Equation 1 that the per-token latency of speculative decoding is 𝐿= (𝑇draft + 𝑇verify)/𝜏. Autoregressive drafters achieve high 𝜏but pay 𝑇draft ∝𝛾; parallel drafters collapse 𝑇draft to a single pass but sacrifice 𝜏because each position is predicted independently. Meanwhile, fixed-length verification wastes 𝑇verify on low-confidence suffix tokens that are almost certain to be rejected. D

## 全文文本
全文已存 `extraction/fulltext/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation.txt`（102452 字符）供引用检索。