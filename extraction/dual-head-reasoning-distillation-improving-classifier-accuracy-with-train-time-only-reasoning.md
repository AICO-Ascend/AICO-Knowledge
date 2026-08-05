---
paper_num: "28"
title: "Dual-Head Reasoning Distillation: Improving Classifier Accuracy with Train-Time-Only Reasoning"
authors: "Classifier Accuracy with Train-Time-Only Reasoning Jillian Xu∗ University of Waterloo j23xu@uwaterloo.ca Dylan Zhou Google dylanzhou@google.com Vinay Shukla Google vinayshukla@google.com Yang Yang Google lizyang@google.c"
date: "2026/1/19"
arxiv: "https://arxiv.org/abs/2509.21487"
pdf: "papers/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning.pdf"
slug: "dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning"
tags: []
---

# Dual-Head Reasoning Distillation: Improving Classifier Accuracy with Train-Time-Only Reasoning

> [!abstract] 摘要（原文）
> 1\. 💡 Dual-Head Reasoning Distillation (DHRD) 提出了一种训练时推理 (train-time reasoning) 的新方法，通过在训练时使用推理头 (reasoning head) 和教师推理 (teacher rationales) 来提升分类准确率，同时避免了推理时的吞吐量 (throughput) 惩罚。 2. 🛠️ 该方法对 decoder-only LM 施加了一个加权联合目标，该目标结合了标签交叉熵 (label cross-entropy) 和 token 级别的 LM loss，用于在包含原始输入和教师（如 Gemini 2.5 Flash）生成推理的序列上进行训练。 3. 📈 在七项 SuperGLUE 任务上，DHRD 比 pooled baselines 提高了 0.65–5.47% 的准确率，尤其在 entailment/causal tasks 上增益显著，且推理时由于不生成推理，其 QPS 比 CoT decoding 快 96–142 倍。

## 元信息
- **发表日期**: 2026/1/19
- **作者**: Classifier Accuracy with Train-Time-Only Reasoning Jillian Xu∗ University of Waterloo j23xu@uwaterloo.ca Dylan Zhou Google dylanzhou@google.com Vinay Shukla Google vinayshukla@google.com Yang Yang Google lizyang@google.c
- **arXiv**: https://arxiv.org/abs/2509.21487
- **本地 PDF**: `papers/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning.pdf`
- **页数**: 12

## 图表（原文 caption + 页码）

### Figure 1 (p.2)
![[assets/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-p02.png]]
> [!quote] caption
> SuperGLUE per-task scores for four backbones. DHRD (train-time reasoning) consistently beats the pooled-classifier baseline and rivals teacher model Gemini 2.5 Flash, with the largest gains on CB/COPA/RTE. ‘Avg’ is the macro-average, tabulated results can be found in Table 1. improvements are attributable to alignment of input–rationale–label triplets rather than to generic LM regularization; inte

### Figure 2 (p.3)
![[assets/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-p03.png]]
> [!quote] caption
> Dual-head fine-tuning on a shared decoder. The classification head pools hidden states over the input span (blue) to produce K class logits. The train-only reasoning head applies a causal LM loss over the full sequence, covering both classification input tokens (blue) and teacher rationale tokens (orange). During training, inputs concatenate task text with teacher rationales. At inference, only th

## 全文文本
全文已存 `extraction/fulltext/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning.txt`（40047 字符）供引用检索。