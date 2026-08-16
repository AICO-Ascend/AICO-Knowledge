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

### Figure 1 (p.1)
![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p01.png]]
> [!quote] caption
> Performance and memory usage of speculative decoding with Llama-3.1-8B-Instruct and EAGLE-3 across varying input lengths. Performance significantly declines well before the shift of memory bottleneck.

### Figure 2 (p.2) ⭐深度解读
![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p02.png]]
> [!quote] caption
> Overview of SpecExtend. FlashAttention accelerates the prefill phases of both target and draft models, and Hybrid Tree Attention accelerates the verification phase. We use the target model’s attention scores obtained from verification to select the most relevant input chunks to retain in the draft model’s KV cache, enhancing both draft speed and accuracy on long inputs without additional training.

> [!tip] 技术解读（多模态）
> SpecExtend 总览：长输入分 chunk，target/draft 双模型 prefill 用 FlashAttention、verify 用 Hybrid Tree Attention 加速；核心 Cross-model Retrieval——用 target 模型 verify 阶段产出的 attention score 选出最相关 chunk（图中 1/3/7/8）动态保留进 draft KV cache，免训练同时提升 draft 速度与精度（平均接受长度最高 +2.55×；16K 摘要 2.84×、AIME-24 长推理 3.86× 加速）。training-free drop-in，可直接套 EAGLE-3 等短上下文优化的 draft。

### Figure 3 (p.4)
![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p04.png]]
> [!quote] caption
> Left figure shows acceptance rates for hard and easy tokens, where CMR enables more accurate drafting in both cases compared to StreamingLLM.

### Figure 4 (p.5)
![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p05.png]]
> [!quote] caption
> (a) Average accepted length of Vicuna-7B/68M across different draft model cache settings. (b) End-to-end latency breakdown of speculative decoding on 16K-token inputs. retrieved context to identify and generate tokens corresponding to a planted “needle” in long inputs (Li et al., 2024a; Contributors, 2023). We com- pare its accuracy against three draft model cache strategies: (1) Full KV Cache whi

### Figure 5 (p.6)
![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p06.png]]
> [!quote] caption
> Speedup comparison of standard speculative decoding and SpecExtend across varying input lengths on

### Figure 6 (p.7)
![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p07.png]]
> [!quote] caption
> Decoding speed (left) and average ac- cepted length (right) of the DeepSeek-R1-Distill-Llama- 8B/EAGLE-3 setup on the long reasoning task with the AIME-24 benchmark.

## 相关论文

- [[dflash-block-diffusion-for-flash-speculative-decoding]] — DFlash: Block Diffusion for Flash Speculative Decoding
- [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] — LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and Verification
- [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] — JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting
- [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] — DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation
- [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] — EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty
- [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] — MEDUSA: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads

## 全文文本
全文已存 `extraction/fulltext/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences.txt`（44368 字符）供引用检索。