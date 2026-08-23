---
paper_num: "3"
title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
authors: "Models via Training-Time Test Yuhui Li1,3, Fangyun Wei2, Chao Zhang1, Hongyang Zhang3,4 1Peking University 2Microsoft Research 3University of Waterloo 4Vector Institute yuhui.li@stu.pku.edu.cn, fawe@microsoft.com c.zhang"
date: "2025/3/3"
arxiv: "https://arxiv.org/abs/2503.01840"
pdf: "papers/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test.pdf"
slug: "eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test"
tags: [speculative, training]
---

# EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test

> [!abstract] 摘要（原文）
> 1\. 🚀 EAGLE-3 通过放弃特征预测约束，直接进行 token 预测并引入 multi-layer feature fusion 技术，显著提升了 draft model 的表达能力与推理效率。 2. 📈 该研究提出了 training-time test 训练方法，使 draft model 能够有效利用规模化训练数据，从而在 LLaMA 等主流模型上实现了高达 6.5 倍的推理速度提升。 3. ⚙️ 实验表明，EAGLE-3 在 SGLang 等工业级推理框架中表现优异，在 batch size 为 64 时仍能保持 1.38 倍的吞吐量提升，优于现有的 speculative sampling 方法。

## 元信息
- **发表日期**: 2025/3/3
- **作者**: Models via Training-Time Test Yuhui Li1,3, Fangyun Wei2, Chao Zhang1, Hongyang Zhang3,4 1Peking University 2Microsoft Research 3University of Waterloo 4Vector Institute yuhui.li@stu.pku.edu.cn, fawe@microsoft.com c.zhang
- **arXiv**: https://arxiv.org/abs/2503.01840
- **本地 PDF**: `papers/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test.pdf`
- **页数**: 12

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig01.png]]
*整页渲染: ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p01.png]]*
> [!quote] caption
> Scaling law evaluated on the MT-bench using LLaMA-Instruct 3.1 8B as the target model, with the x-axis representing the data scale relative to ShareGPT.

> [!tip] 技术解读（多模态）
> ## Figure Description

The figure (Figure 1) contains **two vertically stacked line plots** comparing **EAGLE-2 (red)** and **EAGLE-3 (blue)** across increasing data scales (x-axis: 1, 2, 4, 8 × ShareGPT).

**Top plot — Speedup:**
- Y-axis: Speedup ratio (~3.2–4.4)
- EAGLE-2: flat ≈ 3.2–3.3 (plateaus)
- EAGLE-3: rises from ~3.7 → ~4.4

**Bottom plot — Accept Length:**
- Y-axis: Accept length (~4.0–6.1)
- EAGLE-2: flat ≈ 4.1
- EAGLE-3: rises from ~5.2 → ~6.1

**Key takeaway:** EAGLE-2's feature-prediction design caps its benefit from extra training data (saturation), whereas EAGLE-3's shift to direct token prediction with multi-layer feature fusion unlocks a **monotonically increasing scaling curve** in both speedup and acceptance — enabling draft models to genuinely benefit from larger training corpora.

## Caption (verbatim)

> Figure 1: Scaling law evaluated on the MT-bench using LLaMA-Instruct 3.1 8B as the target model, with the x-axis representing the data scale relative to ShareGPT. The new architectural designs in EAGLE-3 enable an increasing scaling curve, which was never observed in the previous works.

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig02.png]]
*整页渲染: ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]]*
> [!quote] caption
> Speedup ratios of different methods at temperature=0. For the standard speculative sampling, Vicuna-13B uses Vicuna-68M as the draft model. In Table 1, we present comparisons with additional methods, but this figure only showcases a subset. Chat model’s evaluation dataset is MT-bench, and the reasoning model’s evaluation dataset is GSM8K. DeepSeek R1 LLaMA 8B refers to DeepSeek-R1-Distill-LLaMA 8B

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】EAGLE-3 加速比柱状图（temp=0）：在 Vicuna-13B/LLaMA-3.1-8B/3.3-70B/DeepSeek-R1-LLaMA-8B 上对比 Vanilla/SpecDec/Medusa/HASS/EAGLE/EAGLE-2/EAGLE-3，EAGLE-3 分别达 5.6x/4.4x/4.1x/5.0x，全面最优。适合做「EAGLE-3 性能优势」论据。

### Figure 3 (p.3) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig03.png]]
*整页渲染: ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p03.png]]*
> [!quote] caption
> Illustration of training-time test (the bottom part) and its comparison with other draft methods (the upper and middle parts). f denotes the feature, t denotes the token, and a represents the unconstrained vectors.

> [!tip] 技术解读（多模态）
> # Figure 3 Description

**Architecture & Data Flow:**
Figure 3 compares three draft-model architectures vertically:

1. **EAGLE (top):** Predicts next-layer features (f_{t+1}≈f_{t+1}, loss l_fea) plus tokens (t̂_{t+2}≈t_{t+2}, loss l_token) during both training and test.
2. **EAGLE + fea removal (middle):** Removes feature-prediction loss; draft model directly outputs unconstrained vectors â_t_{t+1}, then an LM head produces tokens.
3. **EAGLE-3 (bottom):** Merges training and test into a unified pipeline that simulates multi-step generation. Step 1 takes (f_1…f_t), predicts â_t_{t+1} and t̂_{t+2}. A "training-time test" loop (red dashed arrow) feeds back to Step 2, which predicts t̂_{t+3}, enabling end-to-end multi-step supervision.

**Key Takeaway:** EAGLE-3's training-time test architecture removes the feature-prediction constraint, allowing direct token prediction and richer use of multi-level target features for greater flexibility.

# Caption (Verbatim)

**Figure 3:** Illustration of **training-time test** (the bottom part) and its comparison with other draft methods (the upper and middle parts). *f* denotes the feature, *t* denotes the token, and *α* represents the unconstrained vectors. We use the hat to denote the predictions from models. All the methods shown in the figure use the token sequence from the previous time step, but for simplicity, this is not depicted in the figure. The input to EAGLE-3 is not actually *f*, but it is not shown in this figure. We will provide a detailed explanation in the following section.

### Figure 4 (p.2) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig04.png]]
*整页渲染: ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]]*
> [!quote] caption
> We can address this issue by incorporating Step 1 into the training process (the bottom of Figure 3). Using this method, the benefits of increasing training data become more pronounced. We name this technique as training-time test. EAGLE and speculative sampling methods such as Medusa (Cai et al., 2024) reuse the top-layer fea- tures of the target model, specifically the features immediately befor

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】EAGLE-3 加速比柱状图（temp=0）：在 Vicuna-13B/LLaMA-3.1-8B/3.3-70B/DeepSeek-R1-LLaMA-8B 上对比 Vanilla/SpecDec/Medusa/HASS/EAGLE/EAGLE-2/EAGLE-3，EAGLE-3 分别达 5.6x/4.4x/4.1x/5.0x，全面最优。适合做「EAGLE-3 性能优势」论据。

### Figure 5 (p.4) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig05.png]]
*整页渲染: ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p04.png]]*
> [!quote] caption
> Diagram of the EAGLE-3 inference pipeline, illustrating the three steps of the draft model. l, m, and h represent the low, middle, and high-level features of the target model, respectively. e denotes the embedding. 3 EAGLE-3

> [!tip] 技术解读（多模态）
> **Figure Description (≤120 words):**

Figure 5 depicts the EAGLE-3 inference pipeline, contrasting the frozen Target Model (left, producing a single "|" token) with the three-step Draft Model (right). **Step ①** uses an FC layer + Decoder Layer + LM Head on concatenated low/mid/high features (g) and embeddings (e) of context tokens "can", "I" to draft "do". **Step ②** similarly drafts "it" while re-emitting the fused features g and embeddings for the growing prefix. **Step ③** applies only an LM Head to the features to expand the tree with multiple parallel children ("can"/"I"/"do"/"it"). Arrows route target-model features (l_how, m_how, h_how, l_can, m_can, h_can) into the draft.

**Key Technical Takeaway:**
EAGLE-3 injects low/middle/high-level features (l, m, h) and token embeddings (e) directly into every draft layer via an FC projection into a unified k-dim feature g, enabling feature-level autoregression with a context-aware dynamic tree instead of EAGLE-2's static structure.

**Verbatim Caption:**
Figure 5: Diagram of the EAGLE-3 inference pipeline, illustrating the three steps of the draft model. *l*, *m*, and *h* represent the low, middle, and high-level features of the target model, respectively. *e* denotes the embedding.

### Figure 6 (p.5) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig06.png]]
*整页渲染: ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p05.png]]*
> [!quote] caption
> All attention masks are diagonal, except when the original training data is used as the key. Using matrix multiplication in this case would result in significant computational waste, so we can use vector dot products to calculate the attention score only for the corresponding positions. HASS (Zhang et al., 2024) and EAGLE-3 both make similar modifications to the attention mecha- nism to simulate t

> [!tip] 技术解读（多模态）
> ## Description

The figure depicts a **chunked/segmented causal attention** computation across three stages, flowing left-to-right via a blue arrow:

1. **Stage 1 (top-left):** Queries {How, can, I} attend to Keys {How, can, I} in a 3×3 lower-triangular mask (red ✓ marks).
2. **Branching tree (middle):** The key stream extends downward to {are, we, do}, forming a hierarchical prefix tree.
3. **Stage 2 (top-right):** Queries {are, we, do} attend to the 6-key prefix {How…do} in a 3×6 causal mask.
4. **Stage 3 (bottom-right):** Queries {you, help, it} (yellow) attend to the full 9-key sequence in a 3×9 causal mask, with the expanded tree shown bottom-left.

**Key technical takeaway:** Each query chunk attends only to its own segment plus a bounded prefix of prior tokens, achieving **linear-time causal attention** by avoiding full-sequence key lookups while preserving strict autoregressive masking. (~90 words)

## Caption (verbatim)

The image contains **no textual caption** — only inline axis labels ("Key", "Query") and token cells. No overall title or figure caption is present to transcribe.

### Figure 7 (p.8) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig07.png]]
*整页渲染: ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p08.png]]*
> [!quote] caption
> Acceptance rate of EAGLE and EAGLE-3 on MT-bench, with the target model being LLaMA-

> [!tip] 技术解读（多模态）
> **Figure 7 Description**

The figure is a 2-series line chart plotting **Accept rate** (y-axis, 0.50–0.80) against the estimated-feature count **n-α** (x-axis, from 0-α through 7-α). Two methods are compared on MT-bench with LLaMA-Instruct 3.1 8B as the target model: **EAGLE** (red, square markers) and **EAGLE-3** (blue, circular markers). EAGLE-3 remains flat near ~0.79 across all n, while EAGLE degrades monotonically from ~0.71 at 0-α down to ~0.52 at 6-α before a slight uptick at 7-α.

**Key takeaway (≤120 words):**
EAGLE-3 maintains a near-constant ~79% acceptance rate even as the number of chained estimated features grows, whereas the original EAGLE collapses from 71% → 52%. This indicates EAGLE-3's mixed low/middle/high-level feature fusion and removed feature-prediction constraint enable robust long speculative chains, a prerequisite for the larger speedups (4.40× on MT-bench) reported elsewhere in the paper.

**Caption (verbatim):**
"Figure 7: Acceptance rate of EAGLE and EAGLE-3 on MT-bench, with the target model being LLaMA-Instruct 3.1 8B. Hereby, n-α refers to the acceptance rate when the input contains n estimated features, under the condition that the previous estimated tokens are all accepted by the target model."

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.8) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-tab02.png]]
> [!quote] caption
> Ablation study results with LLaMA-Instruct 3.1 8B as the target model. “Remove fea con” refers to the first improvement of EAGLE-3, which removes the feature prediction constraint. “Fused features” refers to the second improvement of EAGLE-3, where low, middle, and high-level feature fusion replaces

> [!tip] 表格解读（多模态）
> **Figure 7 — Description (≤120 words):**

A line plot comparing the *acceptance rate* of two speculative-decoding models, **EAGLE** (red, circles) and **EAGLE-3** (blue, squares), as a function of speculative step depth `n-α` (0 to 7). Both curves are evaluated on MT-bench with LLaMA-Instruct 3.1 8B as the target model. The x-axis represents the number of previously-accepted estimated features feeding the next draft, while the y-axis shows the proportion of draft tokens the target model verifies positively. Visual flow: the EAGLE curve drops sharply from ~0.71 at step 0 to ~0.51 at step 6–7, whereas EAGLE-3 remains nearly flat at ~0.78–0.81 throughout. **Key takeaway:** combining multi-layer (low/mid/high) fused features with a relaxed prediction constraint in EAGLE-3 decouples acceptance from draft length, sustaining high acceptance (~0.79) even at deep speculation, while EAGLE degrades ~20 percentage points.

**Caption verbatim:**

Figure 7: Acceptance rate of EAGLE and EAGLE-3 on MT-bench, with the target model being LLaMA-Instruct 3.1 8B. Hereby, *n-α* refers to the acceptance rate when the input contains *n* estimated features, under the condition that the previous estimated tokens are all accepted by the target model.

### Table 5 (p.8) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-tab05.png]]
> [!quote] caption
> Throughput improvement under different batch sizes on A100 and LLaMA-Instruct 3.1 8B for the MT- Bench dataset, with vLLM without speculative sampling as the baseline (1.00x).

> [!tip] 表格解读（多模态）
> # Main Figure Description

## Description of Main Figure (Table 5)

**Type**: Table (not a figure with architecture)

**Components**:
- **Rows**: Two methods being evaluated — EAGLE and EAGLE-3
- **Columns**: 8 different batch sizes (2, 4, 8, 16, 24, 32, 48, 56)
- **Cell values**: Throughput improvement multipliers (e.g., 1.30x, 1.75x)
- **Baseline**: vLLM without speculative sampling (1.00x)

**Data flow/Pattern**: As batch size increases, throughput improvement decreases monotonically for both methods. EAGLE peaks at 1.30x (batch=2) and drops below baseline (0.71x) at batch=56. EAGLE-3 peaks at 1.75x and remains above baseline across all tested batch sizes.

**Key Technical Takeaway (≤120 words)**:
EAGLE-3 consistently outperforms vanilla EAGLE across all batch sizes, with the largest gap (0.79x higher) appearing at batch size 2 (1.75x vs. 1.30x). Critically, EAGLE-3 maintains a speedup even at batch size 56 (1.01x), while EAGLE degrades into a slowdown (0.71x). This demonstrates that EAGLE-3's enhanced draft model design is more robust to the diminishing returns of speculative decoding at high batch sizes, where parallel verification costs erode the benefits of single-batch speculation. The crossover point where EAGLE loses its advantage occurs around batch 32, whereas EAGLE-3 extends effective speculative sampling across the full batch-size spectrum.

## Caption Transcription (Verbatim)

"Table 5: Throughput improvement under different batch sizes on A100 and LLaMA-Instruct 3.1 8B for the MT-Bench dataset, with vLLM without speculative sampling as the baseline (1.00x)."

## 相关论文

- [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]] — EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey
- [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] — MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core
- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] — Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM

## 技术点深读（DEEP）

![[deep/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test.txt`（45552 字符）供引用检索。