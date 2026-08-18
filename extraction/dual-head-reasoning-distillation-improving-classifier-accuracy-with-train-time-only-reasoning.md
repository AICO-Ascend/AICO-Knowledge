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

### Figure 1 (p.2) ⭐深度解读
![[assets/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-p02.png]]
> [!quote] caption
> SuperGLUE per-task scores for four backbones. DHRD (train-time reasoning) consistently beats the pooled-classifier baseline and rivals teacher model Gemini 2.5 Flash, with the largest gains on CB/COPA/RTE. ‘Avg’ is the macro-average, tabulated results can be found in Table 1. improvements are attributable to alignment of input–rationale–label triplets rather than to generic LM regularization; inte

> [!tip] 技术解读（多模态）
> ## Figure Description (≤120 words)

The figure presents **four radar (spider) charts**, one per decoder-only backbone (Llama-3.1-8B, Qwen-3-8B, Llama-3.2-3B, Qwen-3-4B), comparing three methods across eight SuperGLUE tasks (BoolQ, CB, COPA, MultiRC, RTE, WiC, WSC, Avg):

- **DHRD** (solid red) — train-time reasoning
- **Gemini 2.5 Flash** (dotted purple) — CoT zero-shot teacher
- **Baseline** (dashed blue) — pooled classifier

DHRD's polygon consistently encloses the baseline's and closely tracks or exceeds Gemini's, with the largest gaps on CB, COPA, and RTE. Architecture-wise, DHRD augments a shared causal transformer with two heads (reasoning LM head at train time, pooled classifier head at test time), enabling one forward pass to serve both objectives without CoT decoding at inference.

**Key takeaway:** Teacher-rationale supervision *at training only* transfers CoT-quality gains to a CoT-free classifier, preserving baseline latency.

## Caption (verbatim)

**Figure 1:** SuperGLUE per-task scores for four backbones. DHRD (train-time reasoning) consistently beats the pooled-classifier baseline and rivals teacher model *Gemini 2.5 Flash*, with the largest gains on CB/COPA/RTE. 'Avg' is the macro-average, tabulated results can be found in Table 1.

### Figure 2 (p.3) ⭐深度解读
![[assets/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-p03.png]]
> [!quote] caption
> Dual-head fine-tuning on a shared decoder. The classification head pools hidden states over the input span (blue) to produce K class logits. The train-only reasoning head applies a causal LM loss over the full sequence, covering both classification input tokens (blue) and teacher rationale tokens (orange). During training, inputs concatenate task text with teacher rationales. At inference, only th

> [!tip] 技术解读（多模态）
> ## Description of Figure 2

**Architecture & Components:** A decoder-only language model serves as a shared backbone, producing hidden embedding tokens (ℝ^(L×D)). Two heads branch off this shared representation:
- **Classification Head:** A Pooler aggregates hidden states over the input span (blue tokens), followed by a 2-layer MLP that outputs K class logits (ℝ^K). This head is used at inference.
- **Reasoning Head (training-only):** Reuses the base model's LM head to compute next-token distributions over the full sequence, producing reasoning logits (ℝ^(L×V)).

**Data Flow:** During training, inputs concatenate the classification sequence (blue) with teacher-generated rationale tokens (orange). The reasoning head applies causal LM loss across both segments, while the classification head operates only on the blue span. At inference, rationales are discarded and only the classification path is used.

**Key Technical Takeaway:** This design distills teacher rationales into the shared decoder's representations during training, transferring reasoning knowledge without adding any inference-time latency — the LM head and rationales are dropped entirely at test time.

## Caption (verbatim)

**Figure 2:** Dual-head fine-tuning on a shared decoder. The *classification head* pools hidden states over the input span (blue) to produce *K* class logits. The train-only *reasoning head* applies a causal LM loss over the full sequence, covering both classification input tokens (blue) and teacher rationale tokens (orange). During training, inputs concatenate task text with teacher rationales. At inference, only the classification head is used.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\begin{aligned} s_i &= [\,x_i,\ \text{\texttt{<REASON>}},\ r_i,\ \text{\texttt{<ANS>}},\ y_i\,],\qquad L_i = |s_i|, \qquad L^{(x)}_i = |x_i|. \end{aligned}
$$

$$
\mathcal{L}_{\mathrm{cls}} = -\frac{1}{B}\sum_{i=1}^B \Big( \mathbf{z}_i[y_i] - \log\!\sum_{k=1}^K e^{\mathbf{z}_i[k]} \Big).
$$

$$
\mathcal{L}_{\mathrm{reason}} = -\,\frac{1}{N}\sum_{i=1}^{B}\sum_{t=1}^{L_i-1} m_{i,t+1}\, \log\!\left( \frac{\exp\{\ell_{i,t}[\,v_{i,t+1}\,]\}} {\sum_{w=1}^{V}\exp\{\ell_{i,t}[w]\}} \right), \qquad N=\sum_{i=1}^{B}\sum_{t=1}^{L_i-1} m_{i,t+1}.
$$

$$
\mathcal{L}_{\mathrm{total}} = \beta\,\mathcal{L}_{\mathrm{cls}} + \alpha\,\mathcal{L}_{\mathrm{reason}}, \quad \alpha,\beta \ge 0.
$$

## 技术点深读（DEEP）

![[deep/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning.txt`（40047 字符）供引用检索。