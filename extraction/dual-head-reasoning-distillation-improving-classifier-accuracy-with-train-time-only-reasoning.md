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
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-fig01.png]]
*整页渲染: ![[assets/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-p02.png]]*
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
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-fig02.png]]
*整页渲染: ![[assets/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-p03.png]]*
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

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.4) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-tab01.png]]
> [!quote] caption
> SuperGLUE results (higher is better). Rel. ∆ (%) is the relative percentage change versus the pooled baseline for the same backbone ( α =0 , β =1 ). All DHRD rows use the optimal weights selected on the validation split: α = β =1 for Llama-3.1-8B, Llama-3.2-3B, and Qwen-3-8B; α =0 . 5 , β =1 for Qwe

> [!tip] 表格解读（多模态）
> ## Description (≤120 words)

**Architecture/Components/Data Flow:** The table benchmarks four open-weight backbones (Llama-3.1-8B, Qwen-3-8B, Llama-3.2-3B, Qwen-3-4B) under two settings — a *Baseline (pooled classifier)* and *DHRD (train-time reasoning)* — against a Gemini 2.5 Flash CoT zero-shot reference. Each row reports per-task scores across seven SuperGLUE subtasks (BoolQ, CB, COPA, MultiRC, RTE, WiC, WSC), an averaged score, and the relative Δ (%) vs. baseline. Per-task values use "F1/EM" or "acc/F1" notation where applicable.

**Key Technical Takeaway:** DHRD train-time reasoning consistently beats pooled classifier baselines; Llama-3.2-3B sees the largest relative lift (+5.47%), and both 8B DHRD configurations surpass the Gemini 2.5 Flash teacher's SuperGLUE average (86.40).

## Caption (Verbatim)

**Table 1:** SuperGLUE results (higher is better). Rel. Δ (%) is the relative percentage change versus the pooled baseline for the same backbone (α=0, β=1). All DHRD rows use the optimal weights selected on the validation split: α=β=1 for Llama-3.1-8B, Llama-3.2-3B, and Qwen-3-8B; α=0.5, β=1 for Qwen-3-4B. Full α/β ablations can be found in Appendix B.

### Table 2 (p.4) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-tab02.png]]
> [!quote] caption
> Ablations on rationale/label alignment (SuperGLUE). ConsistentReasoningLabel (aligned <REASON> and <ANS> ), OnlyLabel (aligned <ANS> ), ShuffleReasoning (misaligned <REASON> ,

> [!tip] 表格解读（多模态）
> ## Caption (verbatim)

**Table 2:** Ablations on rationale/label alignment (SuperGLUE). ConsistentReasoningLabel (aligned ⟨REASON⟩ and ⟨ANS⟩), OnlyLabel (aligned ⟨ANS⟩), ShuffleReasoning (misaligned ⟨REASON⟩, aligned ⟨ANS⟩), ShuffleReasoningLabel (misaligned ⟨REASON⟩ and ⟨ANS⟩). In all settings, the LM loss is applied to the input tokens and present ⟨REASON⟩/⟨ANS⟩ segments. All rows use α=β=1.

## Description

**Architecture/components/data flow:** The table is an ablation study comparing four DHRD training configurations across two Llama backbones (Llama-3.1-8B and Llama-3.2-3B), evaluated on seven SuperGLUE tasks (BoolQ, CB, COPA, MultiRC, RTE, WiC, WSC). Each row reports per-task scores, the average, and the relative change versus the ConsistentReasoningLabel baseline. The four settings differ only in how the ⟨REASON⟩ and ⟨ANS⟩ tokens are paired with the gold label during LM-loss computation (aligned vs. misaligned), while all rows share identical α=β=1 loss weights applied to input tokens and to whichever reasoning/answer segments are present.

**Key technical takeaway:** Aligned reasoning is essential—misaligning both ⟨REASON⟩ and ⟨ANS⟩ causes a catastrophic ~45–48% relative drop, while aligning only the answer recovers most of the performance (within ~2–4%).

### Table 3 (p.9) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-tab03.png]]
> [!quote] caption
> SuperGLUE results (higher is better). Rel. ∆ (%) is the relative percentage change compared to each model’s pooled baseline ( α =0 , β =1 ). Reasoning / CoT fine-tuned models follows ( α =1 , β =0 ) with CoT at inference using the Reasoning Head (refer to Appendix E.6).

> [!tip] 表格解读（多模态）
> The provided content is **not a figure** but rather a **results table (Table 3)**. There is no architecture diagram, model components, or data flow to describe. Below I describe the table's content and provide the verbatim caption.

---

## Description of Table 3

**Structure:** The table reports SuperGLUE benchmark scores across 7 tasks (BoolQ, CB, COPA, MultiRC, RTE, WiC, WSC) plus an average and relative Δ (%) — higher is better.

**Components (rows):**
- **Reference models:** Gemini 2.5 Flash (CoT zero-shot) and Reasoning/CoT variants of Llama-3.1-8B and Qwen3-8B.
- **Model families evaluated:** Llama-3.1-8B, Qwen3-8B, Llama-3.2-3B, Qwen3-4B — each with a Baseline plus three DHRD configurations (β=1,α=0.5), (β=1,α=1), (β=0.5,α=1).

**Key takeaway:** The **DHRD (β=1, α=1)** setting consistently yields the largest gains on the larger 8B backbones (Llama-3.1-8B +1.43%, Qwen3-8B +1.32%) and the strongest improvement on Llama-3.2-3B (+5.47%), demonstrating that balanced distractor/reward weighting is the optimal DHRD hyperparameter regime.

---

## Caption (verbatim transcription)

> **Table 3:** SuperGLUE results (higher is better). Rel. Δ (%) is the relative percentage change compared to each model's pooled baseline (α=0, β=1). Reasoning / CoT fine-tuned models follows (α=1, β=0) with CoT at inference using the Reasoning Head (refer to Appendix E.6).

### Table 4 (p.10) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-tab04.png]]
> [!quote] caption
> SuperGLUE benchmark overview with task type, train, validation, and test dataset sizes

> [!tip] 表格解读（多模态）
> **Main Figure Description**

The figure displays Table 4, a tabular overview of the SuperGLUE benchmark suite rather than an architectural diagram. Its components are a five-column header (Benchmark, Task, Metric, Train, Validation, Test) followed by seven task rows — BoolQ, CB, COPA, MultiRC, RTE, WiC, and WSC — each annotated with task type (QA, NLI, WSD, Coref.), evaluation metric, and dataset split sizes. Below the table, a section header "D" introduces supplementary QPS (queries-per-second) results comparing Chain-of-Thought versus non-CoT inference on identical decoder backbones, though its body content is not shown.

**Key Technical Takeaway:** SuperGLUE's tasks vary drastically in scale (CB has only 250 train examples vs. MultiRC's 27,243), and metric choice depends on task type — Accuracy for most, F1/EM for MultiRC, and F1/Accuracy for CB — reflecting heterogeneous evaluation demands.

**Caption (verbatim):**
"Table 4: SuperGLUE benchmark overview with task type, train, validation, and test dataset sizes"

### Table 5 (p.10) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-tab05.png]]
> [!quote] caption
> Throughput (queries per second, higher is better). Classification uses a pooled head at inference (no decoding). Reasoning uses CoT-style decoding (train-time only in DHRD). The rightmost column shows the speedup of our deployed path over CoT decoding on the same backbone.

> [!tip] 表格解读（多模态）
> **Description (architecture / components / data flow + key takeaway):**

This is a benchmark results table rather than an architecture diagram. It compares throughput (queries per second) across four LLM backbones — **Llama-3.1-8B**, **Llama-3.2-3B**, **Qwen3-8B**, **Qwen3-4B** — measured under two inference paths on identical backbones: (1) a **Pooled Classifier** path (classification head, no autoregressive decoding) and (2) a **Reasoning / CoT** path (autoregressive chain-of-thought generation, train-time only in DHRD). A third column reports the **Speedup = QPS(no-CoT) / QPS(CoT)**, i.e., the factor by which the deployed (no-decoding) path outpaces CoT decoding on the same model.

**Key technical takeaway:** Bypassing autoregressive decoding in favor of a pooled classification head yields a **~96×–142× throughput speedup**, with the 3B-class backbones (Llama-3.2-3B → ~142×, Qwen3-4B → ~117×) showing larger relative gains than their 8B counterparts.

**Caption (verbatim):**

*Table 5: Throughput (queries per second, higher is better). Classification uses a pooled head at inference (no decoding). Reasoning uses CoT-style decoding (train-time only in DHRD). The rightmost column shows the speedup of our deployed path over CoT decoding on the same backbone.*

### Table 6 (p.12) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-tab06.png]]
> [!quote] caption
> Third-party assets and licenses.

> [!tip] 表格解读（多模态）
> I don't see a main figure in the provided content. The image shows only text from a research paper's appendix, specifically:

- **E.7** — Throughput (QPS) Measurement Protocol
- **F** — Future Work
- **G** — Assets & Licenses

The only labeled visual element referenced is "Table 6," but the actual table contents are not included in this excerpt — only its caption appears at the bottom.

**Verbatim caption transcription:**

> Table 6: Third-party assets and licenses.

If you intended to share a different figure (e.g., the DHRD architecture diagram or a results plot from the main paper), please re-upload it and I'll provide the architecture/components/data-flow description plus a key technical takeaway within 120 words.

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