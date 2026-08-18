---
paper_num: "60"
title: "SpecExtend: A Drop-in Enhancement for Speculative Decoding of Long Sequences"
authors: "Speculative Decoding of Long Sequences Jungyoub Cha Hyunjong Kim Sungzoon Cho Seoul National University {jungyoub.cha, hjkim0811, zoon}@snu.ac.kr"
date: "2025/5/27"
arxiv: "https://arxiv.org/abs/2505.20776"
pdf: "papers/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences.pdf"
slug: "specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences"
tags: [speculative]
---

# SpecExtend: A Drop-in Enhancement for Speculative Decoding of Long Sequences

> [!abstract] 摘要（原文）
> Speculative decoding is a widely used technique for accelerating inference in large language models (LLMs), but its performance degrades as input length grows, with significant drops even at moderate lengths. Yet, this early degradation has remained largely underexplored. We introduce SpecExtend, a drop-in enhancement that improves speculative decoding on long sequences without additional training. SpecExtend integrates efficient attention mechanisms such as FlashAttention and Hybrid Tree Attention to accelerate prefill and verification steps. To improve both draft accuracy and speed on long inputs without retraining, we propose Cross-model Retrieval, a novel KV cache eviction strategy that leverages the target model's attention scores to dynamically select relevant context for the smaller draft model. Extensive evaluations show that SpecExtend accelerates speculative decoding by up to 2.84x on 16K-token long document summarization and up to 3.86x on long-form reasoning, while preserving the short-input performance of state-of-the-art frameworks. Our code is available at this https URL .

## 元信息
- **发表日期**: 2025/5/27
- **作者**: Speculative Decoding of Long Sequences Jungyoub Cha Hyunjong Kim Sungzoon Cho Seoul National University {jungyoub.cha, hjkim0811, zoon}@snu.ac.kr
- **arXiv**: https://arxiv.org/abs/2505.20776
- **本地 PDF**: `papers/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences.pdf`
- **页数**: 12

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p01.png]]
> [!quote] caption
> Performance and memory usage of speculative decoding with Llama-3.1-8B-Instruct and EAGLE-3 across varying input lengths. Performance significantly declines well before the shift of memory bottleneck.

> [!tip] 技术解读（多模态）
> **Figure Description:**

The figure is a dual-axis chart benchmarking speculative decoding (EAGLE-3) with Llama-3.1-8B-Instruct across input lengths from 1K to 128K tokens.
- **Left axis (green line, tokens/s):** Throughput drops steeply from ~150 tokens/s at 1K to near-zero by 64K–128K.
- **Right axis (stacked bars, memory in GiB):** Blue = Model Weights (~16 GiB, constant); Orange = KV Cache (grows with sequence length, dominant only at ≥64K).

**Key takeaway:** The performance collapse happens well *before* the KV-cache memory bottleneck emerges, indicating that quadratic attention latency in the target/draft prefill—not memory—is the true cause of speculative decoding degradation on long inputs.

**Caption (verbatim):**
> Figure 1: Performance and memory usage of speculative decoding with Llama-3.1-8B-Instruct and EAGLE-3 across varying input lengths. Performance significantly declines well before the shift of memory bottleneck.

### Figure 2 (p.2) ⭐深度解读
![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p02.png]]
> [!quote] caption
> Overview of SpecExtend. FlashAttention accelerates the prefill phases of both target and draft models, and Hybrid Tree Attention accelerates the verification phase. We use the target model’s attention scores obtained from verification to select the most relevant input chunks to retain in the draft model’s KV cache, enhancing both draft speed and accuracy on long inputs without additional training.

> [!tip] 技术解读（多模态）
> SpecExtend 总览：长输入分 chunk，target/draft 双模型 prefill 用 FlashAttention、verify 用 Hybrid Tree Attention 加速；核心 Cross-model Retrieval——用 target 模型 verify 阶段产出的 attention score 选出最相关 chunk（图中 1/3/7/8）动态保留进 draft KV cache，免训练同时提升 draft 速度与精度（平均接受长度最高 +2.55×；16K 摘要 2.84×、AIME-24 长推理 3.86× 加速）。training-free drop-in，可直接套 EAGLE-3 等短上下文优化的 draft。

### Figure 3 (p.4) ⭐深度解读
![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p04.png]]
> [!quote] caption
> Left figure shows acceptance rates for hard and easy tokens, where CMR enables more accurate drafting in both cases compared to StreamingLLM.

> [!tip] 技术解读（多模态）
> ## Figure 3 Description

**Architecture/Components:**
The figure contains two side-by-side bar charts comparing **StreamingLLM** (orange) against **Cross-Model Retrieval (CMR)** (blue):

- **Left subplot — Acceptance Rate (%) vs. Token Type:** Bar pairs for "Hard" tokens (StreamingLLM ≈59%, CMR ≈61%) and "Easy" tokens (StreamingLLM ≈71%, CMR ≈75%).
- **Right subplot — Natural Divergence (D_KL) vs. Token Position:** Bar groups across four positions (1st, 2nd, 3rd accepted tokens, plus Resampled). D_KL stays low for accepted positions (0.25–0.40) but spikes at the Resampled position (StreamingLLM ≈0.83, CMR ≈0.73).

**Data flow:** Acceptance rates quantify drafting success on hard vs. easy needles, while KL divergence measures target–draft alignment at each verification step.

**Key Technical Takeaway:** CMR simultaneously raises draft acceptance rates *and* reduces target-draft distribution divergence at every position, demonstrating that alignment-driven cache curation yields a more faithful (not just faster) draft model.

## Caption (verbatim)

**Figure 3:** Left figure shows acceptance rates for hard and easy tokens, where CMR enables more accurate drafting in both cases compared to StreamingLLM. Right figure shows the natural divergence between the target and draft models at the first three accepted tokens and the resampled token. CMR consistently yields lower divergence across all positions.

### Figure 4 (p.5) ⭐深度解读
![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p05.png]]
> [!quote] caption
> (a) Average accepted length of Vicuna-7B/68M across different draft model cache settings. (b) End-to-end latency breakdown of speculative decoding on 16K-token inputs. retrieved context to identify and generate tokens corresponding to a planted “needle” in long inputs (Li et al., 2024a; Contributors, 2023). We com- pare its accuracy against three draft model cache strategies: (1) Full KV Cache whi

> [!tip] 技术解读（多模态）
> **Description:**

The figure contains two subplots evaluating SpecExtend for speculative decoding on long inputs. **Subplot (a)** is a line plot comparing the *Average Accepted Length* (y-axis, 1.5–3.5) versus *Input Length* (x-axis, 1K–16K) across three draft-cache strategies—Standard (green), StreamingLLM (orange), and SpecExtend (blue). Standard's accepted length collapses from ~3.7 at 1K to ~1.7 at 16K, StreamingLLM degrades to ~2.5, while SpecExtend stays near ~2.8–3.0. **Subplot (b)** is a stacked horizontal bar chart of *end-to-end latency* (Target Prefill + Draft Prefill + Verification + Drafting) on 16K-token inputs. The Standard configuration totals ~17s (dominated by verification/drafting), whereas SpecExtend reduces total latency to ~7s by shrinking every component.

**Key takeaway:** SpecExtend sustains draft-model acceptance on long contexts and cuts end-to-end speculative-decoding latency by ~2.5×, primarily by reducing verification and drafting costs.

**Caption (verbatim):**

Figure 4: (a) Average accepted length of Vicuna-7B/68M across different draft model cache settings. (b) End-to-end latency breakdown of speculative decoding on 16K-token inputs.

### Figure 5 (p.6) ⭐深度解读
![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p06.png]]
> [!quote] caption
> Speedup comparison of standard speculative decoding and SpecExtend across varying input lengths on

> [!tip] 技术解读（多模态）
> ## Figure 5 Description

**Figure 5** is a grouped bar-chart figure composed of **four side-by-side panels**, each plotting **speedup (y-axis, 0.0–3.5)** against **input length (x-axis: 1K, 2K, 4K, 8K, 16K)** on the GovReport dataset. Each panel pairs two model configurations:

| Panel | Base Model | Draft Model |
|-------|------------|-------------|
| 1 | V-7B | V-68M |
| 2 | V-7B | EAGLE |
| 3 | LC-7B | LC-68M |
| 4 | LC-7B | EAGLE |

Within every panel, two bars per input length are compared: **light-blue "Standard"** speculative decoding vs. **dark-blue "With SpecExtend"**. Numeric speedup labels (e.g., 1.78× vs. 2.28×) sit atop each bar.

**Key takeaway:** SpecExtend delivers consistent speedup gains over standard speculative decoding across *all* model pairs, and the **advantage widens as input length grows**—e.g., on V-7B/V-68M, the gap nearly triples from +0.50× at 1K to +1.44× at 16K—showing its strength scales with long contexts.

## Caption (verbatim)

> Figure 5: Speedup comparison of standard speculative decoding and SpecExtend across varying input lengths on GovReport.

### Figure 6 (p.7) ⭐深度解读
![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p07.png]]
> [!quote] caption
> Decoding speed (left) and average ac- cepted length (right) of the DeepSeek-R1-Distill-Llama- 8B/EAGLE-3 setup on the long reasoning task with the AIME-24 benchmark.

> [!tip] 技术解读（多模态）
> **Description of Figure 6:**

The figure presents two side-by-side bar charts comparing three inference configurations on the AIME-24 long-reasoning benchmark using DeepSeek-R1-Distill-Llama-8B with EAGLE-3:

- **Left chart (Tok/s, decoding speed):**
  - Naive AR: 31.42
  - EAGLE-3: 30.34
  - EAGLE-3 + SpecExtend: **117.21**
- **Right chart (Avg Accepted Length):**
  - Naive AR: 1.00
  - EAGLE-3: 1.89
  - EAGLE-3 + SpecExtend: **5.95**

**Key takeaway:** SpecExtend rescues EAGLE-3 on long-input reasoning — where standard EAGLE-3 collapses to near-naïve throughput — by raising accepted draft length ~3.15× and yielding ~3.86× decoding speedup, while requiring no retraining.

**Caption verbatim:**
> Figure 6: Decoding speed (left) and average accepted length (right) of the DeepSeek-R1-Distill-Llama-8B/EAGLE-3 setup on the long reasoning task with the AIME-24 benchmark.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\frac{T_{avg}^{sd}}{T_t} = \frac{1}{\tau(n,d)} \left( \frac{d \cdot T_d}{T_t} + \frac{T_v(n)}{T_t} \right)
$$

## 相关论文

- [[dflash-block-diffusion-for-flash-speculative-decoding]] — DFlash: Block Diffusion for Flash Speculative Decoding
- [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] — LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and Verification
- [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] — JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting
- [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] — DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation
- [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] — EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty
- [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] — MEDUSA: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads

## 技术点深读（DEEP）

![[deep/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences.txt`（44368 字符）供引用检索。