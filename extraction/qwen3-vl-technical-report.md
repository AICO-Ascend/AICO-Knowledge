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
![[assets/crops/qwen3-vl-technical-report-fig01.png]]
*整页渲染: ![[assets/qwen3-vl-technical-report-p03.png]]*
> [!quote] caption
> The Qwen3-VL framework integrates a vision encoder and a language model decoder to process multimodal inputs, including text, images, and video. The vision encoder is specifically designed to handle dynamic, native-resolution visual inputs, mapping them to visual tokens of variable length.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The diagram illustrates the **Qwen3-VL** architecture and its multimodal data flow. Three native-resolution inputs are shown at the bottom: a tall webpage screenshot (Picture 1, 1248×9376), a tiny logo (Picture 2, 256×32), a cat photo (Picture 3, 1440×800), and a multi-frame kitten video (Video 1, 736×448). These feed into a **Vision Encoder** (SigLIP-2) that produces **variable-length visual tokens** — Picture 1 generates 11,427 tokens, Picture 2 only 8, Picture 3 produces 1,125, and the video yields per-frame tokens plus `<0.5 second>` timestamp text tokens. Tokens are interleaved with text tokens and passed to a **Qwen3 LM Dense/MoE Decoder**. The **DeepStack** mechanism injects vision tokens from multiple encoder layers into corresponding LLM Blocks (1, 5, 7, 9, …, N).

**Key takeaway:** Token count scales with native resolution (small images get few tokens, dense screenshots get many), enabling efficient variable-length visual encoding.

## Caption (verbatim)

**Figure 1:** The Qwen3-VL framework integrates a vision encoder and a language model decoder to process multimodal inputs, including text, images, and video. The vision encoder is specifically designed to handle dynamic, native-resolution visual inputs, mapping them to visual tokens of variable length. To enhance perceptual capability and preserve rich visual information, we incorporate the pioneering DeepStack mechanism, which injects visual tokens from multiple layers of the vision encoder into corresponding layers of the LLM. Furthermore, we adopt Interleaved MRoPE to encode positional information for multimodal inputs with a balanced frequency spectrum, and introduce text-based timestamp tokens to more effectively capture the temporal structure of video sequences.

### Figure 2 (p.17) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-fig02.png]]
*整页渲染: ![[assets/qwen3-vl-technical-report-p17.png]]*
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
![[assets/crops/qwen3-vl-technical-report-fig03.png]]
*整页渲染: ![[assets/qwen3-vl-technical-report-p25.png]]*
> [!quote] caption
> Needle-in-a-Haystack performance heatmap for Qwen3-VL-235B-A22B-Instruct across varying video durations and needle positions. Each cell shows accuracy (%) for locating and answering questions about the inserted “needle” frame.

> [!tip] 技术解读（多模态）
> **Figure Description (≤120 words):**

Figure 3 is a 2D heatmap evaluating the Needle-in-a-Haystack (NIAH) retrieval capability of Qwen3-VL-235B-A22B-Instruct on long videos. The X-axis encodes **Context Length** (0 → 120 min, with token equivalents up to 1024K), split into "Within Training Context (0–30 min)" and "Extrapolation Context (40–120 min)." The Y-axis encodes **needle Depth (%)** from 0–100%. Each cell's color (red→yellow→green) maps to the Accuracy Score (0.0–1.0) for locating/answering a question about an inserted salient frame. The matrix appears uniformly deep-green.

**Key takeaway:** Qwen3-VL achieves ~100% accuracy across all depths within training context (≤256K tokens) and retains 99.5% accuracy when extrapolated to ~1M tokens (~2h video) via YaRN positional extension—demonstrating robust long-sequence multimodal modeling.

**Caption (verbatim):**

"Figure 3: Needle-in-a-Haystack performance heatmap for Qwen3-VL-235B-A22B-Instruct across varying video durations and needle positions. Each cell shows accuracy (%) for locating and answering questions about the inserted "needle" frame."

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.4) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab01.png]]
> [!quote] caption
> Training setup and hyperparameters across different stages for Qwen3-VL.

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**
Table 1 outlines Qwen3-VL's four-stage training pipeline with five columns (Stage, Objective, Training, Token Budget, Sequence Length). Stage S0 trains *only* the MLP merger (vision encoder and LLM frozen) on 67B tokens of captions/OCR at seq-len 8,192 to bridge the modality gap. S1–S3 unfreeze the full stack (vision encoder + merger + LLM) for joint end-to-end training. Token budgets escalate to ~1T for S1/S2 (seq-len 8K→32K) and 100B for S3 (seq-len 262,144). **Key takeaway:** The pipeline uses *progressive unfreezing*—starting with a lightweight cross-modal adapter, then scaling to full joint training while extending context length 32× (8K→262K)—enabling alignment-first stability and billion-token-scale long-context adaptation without destabilizing the LLM.

**Caption verbatim:**
Table 1: Training setup and hyperparameters across different stages for Qwen3-VL.

### Table 2 (p.15) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab02.png]]
> [!quote] caption
> Performance of Qwen3-VL-235B-A22B and top-tier models on visual benchmarks. The highest scores of the reasoning and non-reasoning models are shown in bold and underlined , respectively. Results marked with an ∗ are sourced from the technical report. + denotes results with tool use.

> [!tip] 表格解读（多模态）
> The image you've provided is actually a **table** (Table 2), not a figure. It contains no diagrams, architectures, or data-flow illustrations — only numerical benchmark results comparing language model performance.

**Description of what is shown:**
- A multi-column table titled "Performance of Qwen3-VL-235B-A22B and top-tier models on visual benchmarks."
- Columns include: Benchmark, Qwen3-VL 235B-A22B, Gemini 2.5 Pro, OpenAI GPT-5, and Claude Opus 4.1.
- Rows list various visual benchmarks, with numerical scores.
- Bold indicates highest scores among reasoning models; underlining indicates highest scores among non-reasoning models.
- Asterisks (*) denote results sourced from technical reports; plus signs (+) denote results with tool use.
- Only partial rows are visible at the bottom (mostly cut-off numbers).

**Key technical takeaway:** Qwen3-VL-235B-A22B is being benchmarked against closed-weight frontier models (Gemini 2.5 Pro, GPT-5, Claude Opus 4.1) on multimodal/visual tasks, with a specific focus on distinguishing reasoning vs. non-reasoning performance ceilings.

**Verbatim caption transcription:**

> Table 2: Performance of Qwen3-VL-235B-A22B and top-tier models on visual benchmarks. The highest scores of the reasoning and non-reasoning models are shown in bold and underlined, respectively. Results marked with an * are sourced from the technical report. + denotes results with tool use.

### Table 5 (p.21) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab05.png]]
> [!quote] caption
> Comparison among Qwen3-VL-235B-A22B (Instruct) and other baselines. The highest and second-best scores are shown in bold and underlined respectively.

> [!tip] 表格解读（多模态）
> ## Description

The figure is **Table 5** — a benchmark comparison matrix rather than an architecture diagram. It contrasts **Qwen3-VL-235B-A22B (Instruct)** against three baselines: the prior **Qwen3-VL 235B-A22B**, the text-only **Qwen3 235B-A22B Instruct-2507**, **Deepseek V3 0324**, and **Claude-Opus-4 (Without thinking)**. The rows group benchmarks into five capability buckets — **Knowledge** (MMLU-Pro/Redux, GPQA, SuperGPQA), **Reasoning** (AIME-25, HMMT-25, LiveBench), **Alignment Tasks** (IFEval, Arena-Hard V2, Creative Writing v3, WritingBench), **Coding & Agent** (LiveCodeBench v6, BFCL-v3), and **Multilingualism** (MultiIF, MMLU-ProX, INCLUDE, PolyMATH). Bold marks the top score per row, underline marks the runner-up.

**Key takeaway:** The vision-language **Qwen3-VL-235B-A22B (Instruct) dominates the multimodal "agentic" axes — taking #1 on every Reasoning benchmark (e.g., AIME-25 = 74.7, HMMT-25 = 57.4), edging Claude Opus-4 and Deepseek V3 on LiveCodeBench v6 (54.3), and topping PolyMATH multilingual math (45.1)** — while the text-only Qwen3-Instruct-2507 retains parity on most knowledge/alignment tests, suggesting vision training preserved (rather than hurt) core reasoning ability.

## Caption (verbatim)

**Table 5: Comparison among Qwen3-VL-235B-A22B (Instruct) and other baselines. The highest and second-best scores are shown in bold and underlined respectively.**

### Table 6 (p.22) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab06.png]]
> [!quote] caption
> Comparison among Qwen3-VL-235B-A22B (Thinking) and other reasoning baselines. The highest and second-best scores are shown in bold and underlined respectively.

> [!tip] 表格解读（多模态）
> **Main Figure Description**

The image shows a comparison table (Table 6) with the following structure:

- **Caption block**: Header text explaining the comparison scope and formatting conventions (bold = highest, underlined = second-best).
- **Header row** (four model columns + one benchmark column):
  1. Benchmark (row labels, not visible)
  2. Qwen3-VL 235B-A22B
  3. Qwen3 235B-A22B
  4. OpenAI o3 (medium)
  5. Claude-Opus-4 (With thinking)
- **Data rows**: Not visible in the cropped image — only the column headers are shown.
- **Key technical takeaway**: Qwen3-VL-235B-A22B in "Thinking" mode is benchmarked against a closed-source vision-reasoning stack (OpenAI o3 medium) and a strong reasoning-enabled LLM (Claude-Opus-4 with thinking), enabling direct comparison between an open-weight vision-language MoE and proprietary chain-of-thought baselines. Within ≤120 words, no data rows are exposed in this crop, so numerical takeaways cannot be inferred — only the comparative scope is conveyed.

**Caption Verbatim**

"Table 6: Comparison among Qwen3-VL-235B-A22B (Thinking) and other reasoning baselines. The highest and second-best scores are shown in **bold** and <u>underlined</u> respectively."

### Table 7 (p.22) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab07.png]]
> [!quote] caption
> Comparison among Qwen3-VL-32B-Instruct, Qwen3-VL-30B-A3B-Instruct, and corresponding baselines.

> [!tip] 表格解读（多模态）
> There is no figure (architecture diagram / data-flow schematic) in the provided content. What you supplied is the caption and the header row of **Table 7**, which is a benchmark-comparison table — not a system architecture.

The visible content is limited to:

**Caption (verbatim transcription):**
> Table 7: Comparison among Qwen3-VL-32B-Instruct, Qwen3-VL-30B-A3B-Instruct, and corresponding baselines.

**Table header row (verbatim):**
> | Benchmark | Qwen3-VL 32B | Qwen3 32B | Qwen3-VL 30B-A3B | Qwen3 30B-A3B | Qwen3 30B-A3B |

No body rows, values, diagram, or architecture description are present in the input. If you intended to share a figure (e.g., a model diagram of Qwen3-VL's vision-language architecture), please re-upload the image — I cannot describe components or data flow that aren't shown.

Caption verbatim once more for clarity:
> **Table 7: Comparison among Qwen3-VL-32B-Instruct, Qwen3-VL-30B-A3B-Instruct, and corresponding baselines.**

### Table 8 (p.23) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab08.png]]
> [!quote] caption
> Comparison among Qwen3-VL-32B (Thinking), Qwen3-VL-30B-A3B (Thinking), and corre- sponding baselines.

> [!tip] 表格解读（多模态）
> # Clarification on the Provided Image

The image does **not** contain a figure with architecture, components, or data flow. Instead, it shows the **top portion of Table 8** — only the caption and the header row are visible. No data rows or diagrams are present.

## What is visible

- **Caption:** A table header comparing vision-language (VL) and text-only variants of Qwen3 in 32B and 30B-A3B sizes.
- **Header row columns:** `Benchmark | Qwen3-VL 32B | Qwen3 32B | Qwen3-VL 30B-A3B | Qwen3 30B-A3B | Qwen3 30B-A3B`
- **Data rows:** Not shown.

## Key takeaway from the framing (≤120 words)

The table is structured to contrast **vision-language models** (`Qwen3-VL 32B`, `Qwen3-VL 30B-A3B`) against **text-only baselines** of matched parameter budgets (dense 32B and MoE 30B-A3B). This side-by-side design isolates the contribution of multimodal training from raw model scale, and compares a dense 32B against an MoE 30B-A3B (3B active) configuration — testing whether an MoE vision-language model can match a dense counterpart. Without the numeric rows, however, no quantitative conclusion can be drawn.

## Caption transcribed verbatim

> **Table 8:** Comparison among Qwen3-VL-32B (Thinking), Qwen3-VL-30B-A3B (Thinking), and corresponding baselines.

### Table 11 (p.24) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab11.png]]
> [!quote] caption
> Ablation on Qwen3-ViT. We compare the performance metrics of Qwen3-ViT and SigLIP-2 during the CLIP pre-training stage, and further evaluate their downstream performance in the vision- language modeling (VLM) stage when paired with the same 1.7B Qwen3 language model.

> [!tip] 表格解读（多模态）
> ## Description

**Structure/Components:** This is a comparative ablation **Table 11** benchmarking two vision encoders—**SigLIP-2** (baseline) and **Qwen3-ViT** (proposed)—organized into two evaluation tiers paired with a shared 1.7B Qwen3 LM:

- **Clip Bench tier (7 metrics):** ImageNet-1K, ImageNet-V2, ImageNet-A, ImageNet-R, ImageNet-S, ObjectNet, and a CLIP-Omni aggregate.
- **VLM Bench tier (5 metrics):** OCRB, AI2D, RLWKDQA, InfoVQA, and a VLM-Omni aggregate.
- **Data flow:** Image-text pairs → CLIP pre-training → frozen ViT weights paired with Qwen3-1.7B → downstream VLM evaluation.

**Key Takeaway:** Qwen3-ViT surpasses SigLIP-2 broadly, with the largest gains in **VLM-stage downstream tasks** (e.g., InfoVQA +1.7, AI2D +2.1, Omni +2.9), while staying competitive on CLIP pre-training ImageNet variants—indicating the encoder's improvements transfer more strongly to multimodal reasoning than to contrastive alignment alone.

## Caption (verbatim)

**Table 11: Ablation on Qwen3-ViT.** We compare the performance metrics of Qwen3-ViT and SigLIP-2 during the CLIP pre-training stage, and further evaluate their downstream performance in the vision-language modeling (VLM) stage when paired with the same 1.7B Qwen3 language model.

### Table 12 (p.24) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab12.png]]
> [!quote] caption
> Ablation on DeepStack. We conduct the ablation study on the DeepStack using an internal 15B- A2B LLM, with all experiments pretrained on 200 billion tokens. We directly evaluate these pretrained models on the validation sets, without any post-training.

> [!tip] 表格解读（多模态）
> ## Main Figure Description

**Architecture/Components/Data Flow:** Table 12 presents an ablation study comparing two model variants — "Baseline" and "DeepStack" — built on an internal 15B-A2B LLM, both pretrained on 200B tokens and evaluated zero-shot (no post-training) across 11 multimodal/knowledge benchmarks (AVG, AI2D, OCRB, TVQA, InfoVQA, ChartQA, DocVQA, MMMU, MMStar, RLWDQA, MMB_EN, MMB_CN).

**Key Technical Takeaway:** DeepStack consistently outperforms the Baseline across nearly all benchmarks, with an average gain of +1.3 points (74.7→76.0). Notable improvements occur on OCRB (+2.6), InfoVQA (+2.3), ChartQA (+1.8), and DocVQA (+1.6), while TVQA shows a marginal regression (−0.1), suggesting DeepStack particularly strengthens OCR/document understanding and general visual reasoning at large LLM scale.

## Caption (Transcribed Verbatim)

**Table 12: Ablation on DeepStack.** We conduct the ablation study on the DeepStack using an internal 15B-A2B LLM, with all experiments pretrained on 200 billion tokens. We directly evaluate these pretrained models on the validation sets, without any post-training.

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