---
paper_num: "5"
title: "EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees"
authors: "Yuhui Li♠ Fangyun Wei‡ Chao Zhang♠ Hongyang Zhang♣† ♠Peking University ‡Microsoft Research ♣University of Waterloo †Vector Institute hongyang.zhang@uwaterloo.ca"
date: "2024/6/24"
arxiv: "https://arxiv.org/abs/2406.16858"
pdf: "papers/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees.pdf"
slug: "eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees"
tags: [speculative]
---

# EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees

> [!abstract] 摘要（原文）
> 1\. 🚀 EAGLE-2 提出了一种基于上下文的动态草稿树结构，通过利用 draft model 的置信度得分来准确近似标记的接受率，从而突破了静态草稿树的局限性。 2. 💡 该方法在不改变原始 LLM 输出分布的前提下实现了无损加速，无需额外训练即可动态调整草稿树结构，显著提升了推理过程中的 token 接受数量。 3. 📈 在多项生成任务的广泛评估中，EAGLE-2 相比 EAGLE-1 实现了 20%-40% 的进一步提速，在多种主流模型上表现出 3.05x-4.26x 的显著推理加速效果。

## 元信息
- **发表日期**: 2024/6/24
- **作者**: Yuhui Li♠ Fangyun Wei‡ Chao Zhang♠ Hongyang Zhang♣† ♠Peking University ‡Microsoft Research ♣University of Waterloo †Vector Institute hongyang.zhang@uwaterloo.ca
- **arXiv**: https://arxiv.org/abs/2406.16858
- **本地 PDF**: `papers/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees.pdf`
- **页数**: 12

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig01.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p01.png]]*
> [!quote] caption
> Speedup ratios of different methods at tempera- ture=1. For speculative sampling, the Vicuna series uses

> [!tip] 技术解读（多模态）
> **Figure 1 — Speedup bar chart**

Architecture/components: Grouped bar chart with the y-axis showing "Speedup" (0–4) and the x-axis listing four LLMs — Vicuna 7B, Vicuna 13B, LLaMA2-Chat 7B, and LLaMA2-Chat 13B. Each group contains three bars comparing EAGLE-2 (light pink), EAGLE (blue), and Speculative sampling (purple, hatched where N/A). Reported values: Vicuna 7B (3.05x / 2.13x / 1.50x), Vicuna 13B (3.80x / 2.32x / 1.62x), LLaMA2-Chat 7B (3.19x / 2.22x / N/A), LLaMA2-Chat 13B (3.92x / 2.68x / N/A).

Key takeaway: EAGLE-2 consistently delivers 3–4× speedup across models, outperforming EAGLE by ~40–50% and far exceeding plain speculative sampling, with no accuracy loss since it preserves the target model's output distribution.

**Caption (verbatim):**
Figure 1: Speedup ratios of different methods at temperature=1. For speculative sampling, the Vicuna series uses Vicuna-68M as the draft model. LLaMA2-Chat lacks a suitable draft model, and is marked as N/A. Methods like Medusa relax acceptance conditions under non-greedy settings, which do not guarantee lossless acceleration. *In this paper, we only compare with speculative sampling based methods ensuring the output text distribution remains constant.* In Table 1, we present comparisons with additional methods, but this figure only showcases a subset, including the fastest among these methods, EAGLE.

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig02.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p02.png]]*
> [!quote] caption
> Speedup ratios of different methods at temperature=0. For speculative sampling, the Vicuna series uses Vicuna- 68M as the draft model. LLaMA2-Chat 7B, 13B, and LLaMA3-Instruct 8B lack suitable draft models and are marked as N/A. LLaMA2-Chat 70B and LLaMA3-Instruct 70B use LLaMA2-Chat 7B and LLaMA3-Instruct 8B as draft models, respectively. In Table 1, we present comparisons with additional methods

> [!tip] 技术解读（多模态）
> **Figure description**

The figure is a grouped bar chart (no architecture/data flow — it is a benchmark comparison) plotting **Speedup** on the y-axis (0–4.5×) against seven target LLM configurations on the x-axis: Vicuna 7B/13B, LLaMA2-Chat 7B/13B/70B, and LLaMA3-Instruct 8B/70B. For each model, up to five methods are compared via color-coded bars: **EAGLE-2** (light pink), **EAGLE** (blue), **Medusa** (green), **Lookahead** (orange), and **Speculative sampling** (purple, hatched). EAGLE-2 consistently tops every group (3.29×–4.26×), with EAGLE second; "N/A" hatched bars indicate missing draft models for several LLaMA configurations.

**Key takeaway:** EAGLE-2 achieves ~2.5–5× wall-clock speedup over autoregressive decoding and outperforms EAGLE, Medusa, Lookahead, and standard speculative sampling across all tested models — the gain holding even at 70B scale without additional training.

**Caption (verbatim):**

> Figure 2: Speedup ratios of different methods at temperature=0. For speculative sampling, the Vicuna series uses Vicuna-68M as the draft model. LLaMA2-Chat 7B, 13B, and LLaMA3-Instruct 8B lack suitable draft models and are marked as N/A. LLaMA2-Chat 70B and LLaMA3-Instruct 70B use LLaMA2-Chat 7B and LLaMA3-Instruct 8B as draft models, respectively. In Table 1, we present comparisons with additional methods, but this figure only showcases a subset, including the fastest among these methods, EAGLE.

### Figure 3 (p.3) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig03.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]]*
> [!quote] caption
> Comparison of standard speculative sampling and EAGLE. For simplicity, EAGLE’s tree-structured draft is shown only in the verification stage, while the illustration of the drafting stage uses a chain-structured draft. Here, ti denotes the i-th token embedding, and fi denotes the i-th feature vector in the second-to-top-layer of LLM before LM head. the token sequence ta, ta+1, · · · , tb. Speculati

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 3)

**Architecture/Components:**
Figure 3 compares standard speculative sampling with EAGLE across two stages:

- **(a) Drafting Stage:** Speculative sampling uses a *Token Autoregressive* draft model producing chain tokens (t₄, t₅). EAGLE replaces this with a *Feature Autoregressive* draft model that operates on second-to-top-layer feature vectors (f_i) augmented with one-step-ahead token embeddings (t_{j+1}), yielding features that are then mapped to draft tokens via the original LM head.
- **(b) Verification Stage:** Both pipelines feed candidates into the *Original LLM*. Standard speculative sampling uses a chain-structured draft—rejecting all subsequent tokens upon a mismatch. EAGLE uses a *tree-structured* draft, allowing alternative branches to be evaluated in parallel if a token is rejected.

**Key Technical Takeaway:**
EAGLE shifts autoregression from the token space to the feature space and uses a tree-structured draft with the original LM head, enabling multiple candidate continuations to be verified in a single forward pass—substantially boosting acceptance rates over chain-based speculative decoding.

## Caption (Verbatim)

"Figure 3: Comparison of standard speculative sampling and EAGLE. For simplicity, EAGLE's tree-structured draft is shown only in the verification stage, while the illustration of the drafting stage uses a chain-structured draft. Here, t_i denotes the i-th token embedding, and f_i denotes the i-th feature vector in the second-to-top-layer of LLM before LM head."

### Figure 4 (p.3) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig04.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]]*
> [!quote] caption
> Differences between EAGLE and EAGLE-2. EA- GLE always uses a fixed draft shape. When the query is “10+2=”, the next token is very likely to be correctly pre- dicted as “1”. However, with a static draft tree, EAGLE would still add two candidates, even though the probability of the other candidate “3” being correct is very low. EAGLE- 2, on the other hand, adjusts the shape of draft tree based on th

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 3)

**Architecture/Components:**
Figure 3 compares standard speculative sampling with EAGLE across two stages:

- **(a) Drafting Stage:** Speculative sampling uses a *Token Autoregressive* draft model producing chain tokens (t₄, t₅). EAGLE replaces this with a *Feature Autoregressive* draft model that operates on second-to-top-layer feature vectors (f_i) augmented with one-step-ahead token embeddings (t_{j+1}), yielding features that are then mapped to draft tokens via the original LM head.
- **(b) Verification Stage:** Both pipelines feed candidates into the *Original LLM*. Standard speculative sampling uses a chain-structured draft—rejecting all subsequent tokens upon a mismatch. EAGLE uses a *tree-structured* draft, allowing alternative branches to be evaluated in parallel if a token is rejected.

**Key Technical Takeaway:**
EAGLE shifts autoregression from the token space to the feature space and uses a tree-structured draft with the original LM head, enabling multiple candidate continuations to be verified in a single forward pass—substantially boosting acceptance rates over chain-based speculative decoding.

## Caption (Verbatim)

"Figure 3: Comparison of standard speculative sampling and EAGLE. For simplicity, EAGLE's tree-structured draft is shown only in the verification stage, while the illustration of the drafting stage uses a chain-structured draft. Here, t_i denotes the i-th token embedding, and f_i denotes the i-th feature vector in the second-to-top-layer of LLM before LM head."

### Figure 5 (p.3) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig05.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]]*
> [!quote] caption
> Overall, the acceptance rate of draft tokens is position-dependent, with the highest acceptance rate at position P1 and the lowest at position P6. Draft tokens in the upper left side of the draft tree (such as position P1) have higher acceptance rates, while those in the lower 3

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 3)

**Architecture/Components:**
Figure 3 compares standard speculative sampling with EAGLE across two stages:

- **(a) Drafting Stage:** Speculative sampling uses a *Token Autoregressive* draft model producing chain tokens (t₄, t₅). EAGLE replaces this with a *Feature Autoregressive* draft model that operates on second-to-top-layer feature vectors (f_i) augmented with one-step-ahead token embeddings (t_{j+1}), yielding features that are then mapped to draft tokens via the original LM head.
- **(b) Verification Stage:** Both pipelines feed candidates into the *Original LLM*. Standard speculative sampling uses a chain-structured draft—rejecting all subsequent tokens upon a mismatch. EAGLE uses a *tree-structured* draft, allowing alternative branches to be evaluated in parallel if a token is rejected.

**Key Technical Takeaway:**
EAGLE shifts autoregression from the token space to the feature space and uses a tree-structured draft with the original LM head, enabling multiple candidate continuations to be verified in a single forward pass—substantially boosting acceptance rates over chain-based speculative decoding.

## Caption (Verbatim)

"Figure 3: Comparison of standard speculative sampling and EAGLE. For simplicity, EAGLE's tree-structured draft is shown only in the verification stage, while the illustration of the drafting stage uses a chain-structured draft. Here, t_i denotes the i-th token embedding, and f_i denotes the i-th feature vector in the second-to-top-layer of LLM before LM head."

### Figure 6 (p.4) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig06.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p04.png]]*
> [!quote] caption
> Average acceptance rates for different confidence score intervals of the draft model. The red dashed line connects (0,0) and (1,1) to aid in visual assessment. The original LLM is Vicuna 7B. aspects: how to expand the draft tree (Section 4.1) and how to rerank draft tokens (Section 4.2). During the expansion phase, we input the most promising nodes from the latest layer of the draft tree into the 

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 5)**

The main figure depicts a **draft tree structure** used in speculative decoding (Figure 5a) alongside its empirical validation (Figure 5b).

**Architecture / Data Flow:**
- **Root node "Query"** branches into two first-layer children: **P1** and **P2**.
- Each first-layer node further branches into two second-layer tokens: **P3, P4** under P1, and **P5, P6** under P2.
- This binary tree represents candidate continuations generated by the draft model, which are later verified by the original LLM.
- The accompanying scatter plot (Figure 5b) plots each draft token's acceptance rate against its position (1–6) in the tree, showing per-query variance.

**Key Technical Takeaway:**
Acceptance rate decreases with tree depth (e.g., P6 is lowest) *and* varies significantly across queries at the same position—proving acceptance is **context-dependent**, not just position-dependent. This motivates EAGLE-2's **dynamic, context-aware draft tree** over the static trees used by EAGLE/Medusa.

---

**Caption (verbatim):**

> Figure 5: Acceptance rates of draft tokens at different positions. In the left figure, P1-P6 indicate positions in the token tree, corresponding to positions 1-6 on the horizontal axis in the right figure. The right figure shows the acceptance rates of draft tokens at positions P1-P6.

### Figure 7 (p.5) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig07.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p05.png]]*
> [!quote] caption
> Illustration of EAGLE-2. The numbers beside the edges represent the confidence scores of the draft model, and the numbers in brackets within the blocks represent the value of the nodes. During the expansion phase, we select the top 2 nodes with the highest value from the current layer (orange blocks) as inputs to the draft model and connect the generated tokens (green blocks) to the draft tree. In

> [!tip] 技术解读（多模态）
> **Main figure description:**

The figure illustrates EAGLE-2's two-phase speculative decoding pipeline:

1. **Expand (Top-2)**: Starting from root "It" (value 1.0), the top-2 highest-value nodes per layer (orange blocks) are fed into the draft model, which generates children (green blocks) appended as new branches.

2. **Rerank (Top-8)**: Across the entire expanded tree, the top-8 highest-value nodes (blue blocks) are selected — favoring shallower nodes on ties — to keep the draft connected.

3. **Flatten to 1D**: Selected nodes are linearized into the sequence [It, is, has, a, the, to, good, be].

4. **Attention mask**: A triangular tree-structured causal mask ensures each token only attends to its ancestors, enabling parallel verification.

**Key takeaway:** Tree-structured attention masking preserves causal consistency while allowing parallel draft verification, yielding denser, lower-latency acceptance than sequential draft decoding.

**Caption (verbatim):**

Figure 7: Illustration of EAGLE-2. The numbers beside the edges represent the confidence scores of the draft model, and the numbers in brackets within the blocks represent the value of the nodes. During the expansion phase, we select the top 2 nodes with the highest value from the current layer (orange blocks) as inputs to the draft model and connect the generated tokens (green blocks) to the draft tree. In the rerank phase, we select the top 8 nodes with the highest value from all nodes (blue blocks), flatten them into a 1-dimensional sequence to form the final draft. We then construct the attention mask according to the tree structure, ensuring each token can only see its ancestor nodes.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.7) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-tab01.png]]
> [!quote] caption
> Speedup ratios and average acceptance lengths τ of different methods. V represents Vicuna, L2 represents LLaMA2-Chat. SpS denotes standard speculative sampling, with its draft model being Vicuna-68M. Methods like Medusa relax acceptance conditions under non-greedy settings, which do not guarantee lo

> [!tip] 表格解读（多模态）
> **Description of Main Figure (Table 1):**

Table 1 presents a quantitative comparison of inference acceleration methods for LLMs. The table is organized as a matrix with two model backbones (V = Vicuna; L2 = LLaMA2-Chat) on rows and competing methods across columns. The two reported metrics are: (1) **Speedup ratio** (relative wall-clock acceleration over the base model) and (2) **average acceptance length τ** (mean number of drafted tokens verified/accepted per decoding step). Three classes of methods are tabulated: standard autoregressive decoding (baseline = 1.0×), SpS (standard speculative sampling with Vicuna-68M as the static draft model), and EAGLE-2 (dynamic draft trees). Medusa is acknowledged but excluded from head-to-head comparison because its relaxed acceptance criterion under non-greedy sampling is non-lossless.

**Key technical takeaway:** By dynamically expanding the draft tree based on the target model's confidence at each step, EAGLE-2 raises the average accepted-token count τ above static SpS, yielding higher speedup while preserving lossless, greedy-equivalent output. (104 words)

**Caption transcribed verbatim:**

> Table 1: Speedup ratios and average acceptance lengths τ of different methods. V represents Vicuna, L2 represents LLaMA2-Chat. SpS denotes standard speculative sampling, with its draft model being Vicuna-68M. Methods like Medusa relax acceptance conditions under non-greedy settings, which do not guarantee lossless acceleration. Therefore, we do not compare EAGLE-2 with these methods.

### Table 2 (p.8) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-tab02.png]]
> [!quote] caption
> Speedup ratios and average acceptance lengths τ with LLaMA2-Chat 70B, LLaMA3-Instruct 70B, and LLaMA3-Instruct 8B as the original LLMs, with the tem- perature set to 0, on the MT-bench dataset.

> [!tip] 表格解读（多模态）
> **Note:** What you've shared is a **table (Table 2)**, not a figure, so there is no architecture, component diagram, or data-flow diagram to describe. I can summarize the table's content and key takeaway instead.

## Table Summary

The table benchmarks four **speculative decoding** techniques on the MT-bench dataset (temperature = 0):

**Columns:** Model | Method | Speedup | τ (average acceptance length)

**Rows:** Three base LLMs are evaluated:
- **LLaMA2-Chat 70B**: PLD (1.31×, τ=1.39), Lookahead (1.52×, τ=1.64), EAGLE (3.01×, τ=3.81), **EAGLE-2 (3.51×, τ=4.48)** ← best
- **LLaMA3-Instruct 70B**: EAGLE (2.83×, τ=3.62), **EAGLE-2 (3.29×, τ=4.16)** ← best
- **LLaMA3-Instruct 8B**: EAGLE (2.72×, τ=3.65), **EAGLE-2 (3.46×, τ=4.53)** ← best

## Key Technical Takeaway
**EAGLE-2 consistently achieves the highest speedup (≈3.3×–3.5×) and longest average acceptance length (τ ≈ 4.1–4.5) across all three LLMs**, substantially outperforming PLD, Lookahead, and the original EAGLE — demonstrating that its improved draft-model strategy delivers transferable, model-agnostic inference acceleration. (≈89 words)

## Verbatim Caption
> "Table 2: Speedup ratios and average acceptance lengths τ with LLaMA2-Chat 70B, LLaMA3-Instruct 70B, and LLaMA3-Instruct 8B as the original LLMs, with the temperature set to 0, on the MT-bench dataset."

### Table 3 (p.8) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-tab03.png]]
> [!quote] caption
> Ablation experiment results with temperature set to 0 on Vicuna 7B. “w/o value” indicates not using value and directly using confidence, “w/o reranking” indicates not performing reranking, and “w/o both” indicates neither value nor reranking is used.

> [!tip] 表格解读（多模态）
> **Description of Main Figure (Table 2):**

This table (not an architectural figure) compares speculative decoding methods across three target LLMs on MT-bench at temperature 0. Columns: Model, Method, Speedup, τ (average acceptance length). Rows group results by base model — LLaMA2-Chat 70B (PLD, Lookahead, EAGLE, EAGLE-2), LLaMA3-Instruct 70B (EAGLE, EAGLE-2), and LLaMA3-Instruct 8B (EAGLE, EAGLE-2). EAGLE-2 values are bolded, indicating the best results. Data flow: each method proposes draft tokens, the target LLM verifies them, and the speedup is computed relative to standard autoregressive decoding.

**Key technical takeaway:** EAGLE-2 consistently outperforms its predecessor EAGLE and other baselines, achieving up to **3.51× speedup with τ=4.48** on LLaMA2-Chat 70B, and **3.46× speedup with τ=4.53** even on the smaller LLaMA3-Instruct 8B model — demonstrating that dynamic draft trees scale effectively across model sizes.

**Caption (verbatim):**

> Table 2: Speedup ratios and average acceptance lengths τ with LLaMA2-Chat 70B, LLaMA3-Instruct 70B, and LLaMA3-Instruct 8B as the original LLMs, with the temperature set to 0, on the MT-bench dataset.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
V_i=\prod_{t_j \in \text{Path}\left(\text{root}, t_i\right)} p_j \approx \prod_{t_j \in \text{Path}\left(\text{root}, t_i\right)} c_j,
$$

## 相关论文

- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]] — BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DIFFUSION LANGUAGE MODELS
- [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] — MEDUSA: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads
- [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] — JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting
- [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] — EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty
- [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] — DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation

## 技术点深读（DEEP）

![[deep/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees.txt`（46933 字符）供引用检索。