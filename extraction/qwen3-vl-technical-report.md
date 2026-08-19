---
paper_num: "13"
title: "Qwen3-VL Technical Report"
authors: "Qwen3-VL Technical Report Qwen Team"
date: "2026/6/10"
arxiv: "https://arxiv.org/abs/2511.21631"
pdf: "papers/qwen3-vl-technical-report.pdf"
slug: "qwen3-vl-technical-report"
tags: [multimodal]
---

# Qwen3-VL Technical Report

> [!abstract] 摘要（原文）
> 1\. 🚀 Qwen3-VL是Qwen系列迄今为止最强大的视觉-语言模型，在广泛的多模态基准测试中表现出色，原生支持高达256K tokens的文本、图像和视频交错上下文。 2. 💡 该模型家族包括密集型（2B/4B/8B/32B）和MoE型（30B-A3B/235B-A22B）变体，并通过增强的interleaved-MRoPE、DeepStack集成和基于文本的时间对齐等架构升级，提升了视觉-语言对齐和长上下文理解能力。 3. 📈 Qwen3-VL在通用VQA、多模态推理、文档理解、2D/3D Grounding和视频理解等任务中均实现领先性能，并且在纯文本能力方面超越了部分文本专用模型，同时在多语言OCR支持方面也取得了显著进展。

## 元信息
- **发表日期**: 2026/6/10
- **作者**: Qwen3-VL Technical Report Qwen Team
- **arXiv**: https://arxiv.org/abs/2511.21631
- **本地 PDF**: `papers/qwen3-vl-technical-report.pdf`
- **页数**: 42

## 图表（原文 caption + 页码）

### Figure 1 (p.3) ⭐深度解读
![[assets/qwen3-vl-technical-report-p03.png]]
> [!quote] caption
> The Qwen3-VL framework integrates a vision encoder and a language model decoder to process multimodal inputs, including text, images, and video. The vision encoder is specifically designed to handle dynamic, native-resolution visual inputs, mapping them to visual tokens of variable length.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The diagram illustrates the **Qwen3-VL** architecture and its multimodal data flow. Three native-resolution inputs are shown at the bottom: a tall webpage screenshot (Picture 1, 1248×9376), a tiny logo (Picture 2, 256×32), a cat photo (Picture 3, 1440×800), and a multi-frame kitten video (Video 1, 736×448). These feed into a **Vision Encoder** (SigLIP-2) that produces **variable-length visual tokens** — Picture 1 generates 11,427 tokens, Picture 2 only 8, Picture 3 produces 1,125, and the video yields per-frame tokens plus `<0.5 second>` timestamp text tokens. Tokens are interleaved with text tokens and passed to a **Qwen3 LM Dense/MoE Decoder**. The **DeepStack** mechanism injects vision tokens from multiple encoder layers into corresponding LLM Blocks (1, 5, 7, 9, …, N).

**Key takeaway:** Token count scales with native resolution (small images get few tokens, dense screenshots get many), enabling efficient variable-length visual encoding.

## Caption (verbatim)

**Figure 1:** The Qwen3-VL framework integrates a vision encoder and a language model decoder to process multimodal inputs, including text, images, and video. The vision encoder is specifically designed to handle dynamic, native-resolution visual inputs, mapping them to visual tokens of variable length. To enhance perceptual capability and preserve rich visual information, we incorporate the pioneering DeepStack mechanism, which injects visual tokens from multiple layers of the vision encoder into corresponding layers of the LLM. Furthermore, we adopt Interleaved MRoPE to encode positional information for multimodal inputs with a balanced frequency spectrum, and introduce text-based timestamp tokens to more effectively capture the temporal structure of video sequences.

### Figure 2 (p.17) ⭐深度解读
![[assets/qwen3-vl-technical-report-p17.png]]
> [!quote] caption
> Multilingual OCR performance of our model on a self-built test set. The model achieves over 70% accuracy on 32 out of 39 supported languages, demonstrating strong and usable multilingual capabilities. establishes a new state of the art, marginally outperforming its “thinking” counterpart, Qwen3-VL- 235B-A22B-Thinking. On OCR-related visual question answering (VQA) benchmarks that require both OCR 

> [!tip] 技术解读（多模态）
> ## Figure Description

**Type:** Vertical bar chart, sorted ascending by accuracy.

**Axes:**
- **Y-axis:** Accuracy (%), linear scale 0–100
- **X-axis:** Language (39 categorical entries, ordered low→high)

**Encoding:** Each bar represents a language's OCR accuracy. Bars are color-graded from light purple (low) to dark purple (high), reinforcing the sort order. Values span roughly **71%** (Romanian, lowest) to **~97%** (Swedish, highest).

**Components visible:** 39 discrete language labels (Romanian, Swahili, Russian, Hindi, Hebrew, Polish, Cebuano, Italian, German, Vietnamese, Ukrainian, Uzbek, Spanish, French, Portuguese, Japanese, Turkish, Korean, Arabic, Persian, Urdu, Finnish, Dutch, Norwegian, Czech, Greek, Thai, Indonesian, Danish, Serbian, Swedish, etc.).

**Key takeaway:** 32/39 languages clear the 70% practical-utility threshold, with most non-Latin scripts (Thai, Korean, Arabic, Greek, Hindi) also performing strongly — indicating the OCR is genuinely multilingual rather than Latin-script-biased.

## Caption (Verbatim)

> **Figure 2:** Multilingual OCR performance of our model on a self-built test set. The model achieves over 70% accuracy on 32 out of 39 supported languages, demonstrating strong and usable multilingual capabilities.

### Figure 3 (p.25) ⭐深度解读
![[assets/qwen3-vl-technical-report-p25.png]]
> [!quote] caption
> Needle-in-a-Haystack performance heatmap for Qwen3-VL-235B-A22B-Instruct across varying video durations and needle positions. Each cell shows accuracy (%) for locating and answering questions about the inserted “needle” frame.

> [!tip] 技术解读（多模态）
> **Figure Description (≤120 words):**

Figure 3 is a 2D heatmap evaluating the Needle-in-a-Haystack (NIAH) retrieval capability of Qwen3-VL-235B-A22B-Instruct on long videos. The X-axis encodes **Context Length** (0 → 120 min, with token equivalents up to 1024K), split into "Within Training Context (0–30 min)" and "Extrapolation Context (40–120 min)." The Y-axis encodes **needle Depth (%)** from 0–100%. Each cell's color (red→yellow→green) maps to the Accuracy Score (0.0–1.0) for locating/answering a question about an inserted salient frame. The matrix appears uniformly deep-green.

**Key takeaway:** Qwen3-VL achieves ~100% accuracy across all depths within training context (≤256K tokens) and retains 99.5% accuracy when extrapolated to ~1M tokens (~2h video) via YaRN positional extension—demonstrating robust long-sequence multimodal modeling.

**Caption (verbatim):**

"Figure 3: Needle-in-a-Haystack performance heatmap for Qwen3-VL-235B-A22B-Instruct across varying video durations and needle positions. Each cell shows accuracy (%) for locating and answering questions about the inserted "needle" frame."

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$

## 相关论文

- [[kimi-vl-technical-report]] — KIMI-VL TECHNICAL REPORT
- [[qwen2-5-vl-technical-report]] — Qwen2.5-VL Technical Report
- [[kimi-k2-5-visual-agentic-intelligence]] — KIMI K2.5: VISUAL AGENTIC INTELLIGENCE
- [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] — DeepStack: Deeply Stacking Visual Tokens is Surprisingly Simple and Effective for LMMs
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation

## 技术点深读（DEEP）

![[deep/qwen3-vl-technical-report]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/qwen3-vl-technical-report.txt`（150008 字符）供引用检索。