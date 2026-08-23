---
paper_num: "40"
title: "Qwen2.5-VL Technical Report"
authors: "Qwen2.5-VL Technical Report Qwen Team, Alibaba Group"
date: "2026/1/5"
arxiv: "https://arxiv.org/abs/2502.13923"
pdf: "papers/qwen2-5-vl-technical-report.pdf"
slug: "qwen2-5-vl-technical-report"
tags: [multimodal]
---

# Qwen2.5-VL Technical Report

> [!abstract] 摘要（原文）
> 1\. ✨ Qwen2.5-VL 是 Qwen 视觉语言系列的最新旗舰模型，通过原生动态分辨率处理和基于绝对时间编码的多模态旋转位置嵌入（MRoPE），显著提升了对图像和超长视频的理解能力。 2. ⚙️ 该模型重新设计了 Vision Transformer (ViT) 架构，引入窗口注意力以优化计算效率，并将其预训练语料库扩展至 4.1 万亿 tokens，以增强性能。 3. 🏆 Qwen2.5-VL 在文档解析、精确对象定位、超长视频理解及代理功能方面表现出色，其旗舰 72B 模型在多项基准测试中与 GPT-4o 和 Claude 3.5 Sonnet 等顶尖模型媲美甚至超越。

## 元信息
- **发表日期**: 2026/1/5
- **作者**: Qwen2.5-VL Technical Report Qwen Team, Alibaba Group
- **arXiv**: https://arxiv.org/abs/2502.13923
- **本地 PDF**: `papers/qwen2-5-vl-technical-report.pdf`
- **页数**: 23

## 图表（原文 caption + 页码）

### Figure 1 (p.3) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-fig01.png]]
*整页渲染: ![[assets/qwen2-5-vl-technical-report-p03.png]]*
> [!quote] caption
> The Qwen2.5-VL framework demonstrates the integration of a vision encoder and a language model decoder to process multimodal inputs, including images and videos. The vision encoder is designed to handle inputs at their native resolution and supports dynamic FPS sampling. Images of varying sizes and video frames with different FPS rates are dynamically mapped to token sequences of varying lengths. 

> [!tip] 技术解读（多模态）
> ## Figure Description

**Inputs (bottom):** Images (Picture 1: 9204×1092, Picture 2: 28×224, Picture 3: 700×1260) and videos (Video 1: 392×644, sampled at dynamic FPS 0.5–10) enter at **native resolution**, bypassing resize.

**Vision Encoder:** A redesigned ViT first applies a **Conv3D (2×14×14)** over window-partitioned video frames. The transformer stack runs one **Full Attention** block followed by **M Window Attention** blocks, each sandwiched by **RMSNorm** and an **FFN with SwiGLU**. MRoPE injects spatial + absolute-temporal position IDs.

**Tokenization:** Variable token counts emerge (Picture 1: 11,427; Picture 2: 8; Picture 3: 1,125; Video 1: 644/1,288/2,576 depending on FPS).

**Decoder:** Visual tokens + text tokens ("and videos here.", "Picture 1 is an image from a blog") feed the **Qwen2.5 LM Decoder**, which produces autoregressive text output.

### Key Technical Takeaway (≤120 words)
Qwen2.5-VL's core innovation is **native-resolution vision encoding combined with Multimodal RoPE (MRoPE) aligned to absolute time**. By avoiding image resizing, preserving aspect ratios, and pairing spatial 2D-RoPE with a temporal axis, the model handles arbitrary image sizes and variable-FPS videos as token sequences of differing lengths. A redesigned ViT (SwiGLU FFN, RMSNorm, window attention with one full-attention block) balances compute efficiency against global context. The MLP-based vision-language merger compresses long feature sequences before the LLM. This design enables precise temporal grounding (pace of events, moment localization) while scaling efficiently across multimodal inputs.

### Caption (verbatim)
"Figure 1: The Qwen2.5-VL framework demonstrates the integration of a vision encoder and a language model decoder to process multimodal inputs, including images and videos. The vision encoder is designed to handle inputs at their native resolution and supports dynamic FPS sampling. Images of varying sizes and video frames with different FPS rates are dynamically mapped to token sequences of varying lengths. Notably, MRoPE aligns time IDs with absolute time along the temporal dimension, enabling the model to better comprehend temporal dynamics, such as the pace of events and precise moment localization. The processed visual data is subsequently fed into the Qwen2.5 LM Decoder. We have re-engineered the vision transformer (ViT) architecture, incorporating advanced components such as FFN with SwiGLU activation, RMSNorm for normalization, and window-based attention mechanisms to enhance performance and efficiency."

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.8) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab02.png]]
> [!quote] caption
> Training data volume and composition across different stages.

> [!tip] 表格解读（多模态）
> **Note:** No architecture/figure with components or data flow is provided in the image — only **Table 2**, which is a three-row hyperparameter table comparing training stages. I cannot describe a figure that isn't there, so I'll summarize what's actually present.

**Description of Table 2 (~110 words):**
The table has three columns representing progressive training stages and three rows of hyperparameters. Row 1 (Tokens): 1.5T, 2T, 0.6T — increasing then shrinking. Row 2 (Sequence length): 8192, 8192, 32768 — fixed then quadrupled in stage 3. Row 3 (Training): ViT, ViT & LLM, ViT & LLM — vision-only warm-up, then joint vision–language. **Key takeaway:** The pipeline follows a *vision-first → joint multimodal → long-context refinement* curriculum: start with a pure ViT on 1.5T tokens at length 8192, then add an LLM head with another 2T tokens, and finally finetune on a smaller 0.6T-token corpus extended to 32,768-token context length to teach long-context multimodal reasoning.

**Caption (verbatim):**
"Table 2: Training data volume and composition across different stages."

### Table 3 (p.11) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab03.png]]
> [!quote] caption
> Performance of Qwen2.5-VL and State-of-the-art.

> [!tip] 表格解读（多模态）
> **Description (≈115 words):**

**Structure.** This is a benchmark comparison matrix (Table 3), not an architectural diagram. **Columns (components/models):** Previous Open-source SoTA, Claude-3.5-Sonnet-0620, GPT-4o-0513, InternVL2.5-78B, Qwen2-VL-72B, Qwen2.5-VL-72B, Qwen2.5-VL-7B, Qwen2.5-VL-3B. **Rows (data flow / evaluation axes):** grouped into three task families — College-level Problems (MMMU, MMMU-Pro), Math (MathVista, MATH-Vision, MathVerse), and General Visual Question Answering (15+ benchmarks including MMBench variants, MMStar, MuirBench, BLINK, MTVQA, MMVet). **Cells:** numeric scores per dataset/model pair. **Key takeaway:** Qwen2.5-VL-72B matches or surpasses GPT-4o-0513 on several multimodal reasoning benchmarks (e.g., MuirBench 70.7, MMVet 76.2) and decisively beats its open-source predecessor Qwen2-VL-72B, demonstrating that scaling and dataset curation, not only size, drive multimodal gains.

**Caption (verbatim):**

Table 3: **Performance of Qwen2.5-VL and State-of-the-art.**

### Table 4 (p.12) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab04.png]]
> [!quote] caption
> Performance on pure text tasks of the 70B+ Instruct models and Qwen2.5-VL.

> [!tip] 表格解读（多模态）
> **Description:**

This is a performance comparison table (not an architectural figure) titled *Table 4*. It benchmarks five large language models — Llama-3.1-70B, Llama-3.1-405B, Qwen2-72B, Qwen2.5-72B, and Qwen2.5-VL-72B — across 10 datasets grouped into four task categories: General (MMLU-Pro, MMLU-redux, LiveBench-0831), Mathematics & Science (GPQA, MATH, GSM8K), Coding (HumanEval, MultiPL-E), and Alignment (IFEval). Bold cells indicate best-in-column results.

**Key takeaway:** Qwen2.5-VL-72B — a vision-language model — matches or rivals text-only Qwen2.5-72B on most benchmarks while competing closely with the much larger Llama-3.1-405B, and it tops the table on LiveBench-0831 (57.0), MultiPL-E (79.5), and IFEval (86.3), demonstrating that multimodal training need not sacrifice pure-text reasoning capability. *(119 words)*

**Caption (verbatim):**

"Table 4: Performance on pure text tasks of the 70B+ Instruct models and Qwen2.5-VL."

### Table 5 (p.13) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab05.png]]
> [!quote] caption
> Performance of Qwen2.5-VL and other models on OCR, chart, and document understanding benchmarks.

> [!tip] 表格解读（多模态）
> **Description (treating as a table-typed visualization):**

The image shows the header of Table 5 — a benchmark comparison matrix rather than an architecture figure. **Components**: (1) a "Datasets" column on the left (data rows are cut off in the crop, so individual benchmark names are not visible), and (2) seven model-column headers comparing proprietary frontier VLMs — Claude-3.5 Sonnet, Gemini 1.5 Pro, GPT-4o — alongside the open-source InternVL2.5-78B baseline and Qwen2.5-VL family at three parameter scales (72B, 7B, 3B). **Data flow (intended)**: each cell would carry one model's accuracy/score on one benchmark, enabling cross-model and cross-scale diffing. **Key takeaway**: the table spans a full capability ladder — closed SOTA, open 78B class, and small/medium Qwen variants — so readers can directly judge how Qwen2.5-VL trades size against OCR/chart/document SOTA. (≈115 words)

**Caption verbatim:**

> Table 5: Performance of Qwen2.5-VL and other models on OCR, chart, and document understanding benchmarks.

### Table 7 (p.14) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab07.png]]
> [!quote] caption
> Performance of Qwen2.5-VL and other models on counting.

> [!tip] 表格解读（多模态）
> **Main Figure Description**

This is **Table 7**, a performance comparison table evaluating object counting accuracy on the CountBench dataset across six vision-language models. The data flow is simple: a single benchmark row (CountBench) maps to accuracy scores per model. Columns include the proposed Qwen2.5-VL-72B alongside five competing baselines (Gemini 1.5-Pro, GPT-4o, Claude-3.5 Sonnet, Molmo-72b, InternVL2.5-78B).

**Key Technical Takeaway:**
Qwen2.5-VL-72B achieves the highest counting accuracy at **93.6**, beating GPT-4o (87.9) and Claude-3.5 Sonnet (89.7), while InternVL2.5-78B surprisingly trails at 72.1 — demonstrating that Qwen2.5-VL's visual grounding excels on dense object-counting tasks despite competitive VLMs varying widely in performance.

**Caption (verbatim):**
Table 7: Performance of Qwen2.5-VL and other models on counting.

### Table 8 (p.14) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab08.png]]
> [!quote] caption
> Performance of Qwen2.5-VL and other models on video benchmarks.

> [!tip] 表格解读（多模态）
> **Description**

The figure is a benchmark comparison **Table 8** structured as a matrix. **Columns** list five evaluated models: Gemini 1.5-Pro, GPT-4o, Qwen2.5-VL-72B, Qwen2.5-VL-7B, and Qwen2.5-VL-3B. **Rows** are split into two task sections—*Video Understanding Tasks* (Video-MME, Video-MMMU, MMVU, MVBench, MMBench-Video, LongVideoBench, LVBench, EgoSchema, PerceptionTest, MLVU, TempCompass) and *Video Grounding Tasks* (Charades-STA mIoU). **Data flow** reads left→right: each cell reports that model's score on the dataset, with the highest in each row bolded; dashes indicate unreported results. **Key takeaway:** Qwen2.5-VL-72B posts the best scores on long-video/grounding-heavy sets (LVBench 47.3, EgoSchema 76.2, MLVU 74.6, Charades-STA 50.9 mIoU) and remains competitive across the board, while the 7B/3B variants scale gracefully down to lightweight inference.

**Caption (verbatim)**

Table 8: Performance of Qwen2.5-VL and other models on video benchmarks.

### Table 9 (p.15) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab09.png]]
> [!quote] caption
> Performance of Qwen2.5-VL and other models on GUI Agent benchmarks.

> [!tip] 表格解读（多模态）
> **Description (≈115 words):**
Table 9 is a comparative benchmark matrix evaluating six vision–language models (GPT-4o, Gemini 2.0, Claude, Aguvis-72B, Qwen2-VL-72B, Qwen2.5-VL-72B) across seven GUI-agent tasks. The benchmarks split into two regimes: offline GUI grounding (ScreenSpot, ScreenSpot Pro, Android Control High/Low_EM) measuring click-coordinate prediction accuracy, and online agent success-rate evaluations (AndroidWorld_SR, MobileMiniWob++_SR, OSWorld) — the latter requiring Set-of-Mark (SoM) overlays for some baselines. Qwen2.5-VL-72B (column-rightmost, bolded) dominates grounding tasks and matches or exceeds baselines online *without* SoM, indicating robust native screen understanding.

**Key takeaway:** Qwen2.5-VL-72B sets a new ScreenSpot-Pro record (43.6% vs. 23.6% prior best) and reaches 93.7% on Android Control Low_EM — resolving UI elements without auxiliary marks.

**Caption (verbatim):**
*Table 9: Performance of Qwen2.5-VL and other models on GUI Agent benchmarks.*

## 相关论文

- [[qwen3-vl-technical-report]] — Qwen3-VL Technical Report
- [[kimi-vl-technical-report]] — KIMI-VL TECHNICAL REPORT
- [[kimi-k2-5-visual-agentic-intelligence]] — KIMI K2.5: VISUAL AGENTIC INTELLIGENCE
- [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] — DeepStack: Deeply Stacking Visual Tokens is Surprisingly Simple and Effective for LMMs
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation

## 技术点深读（DEEP）

![[deep/qwen2-5-vl-technical-report]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/qwen2-5-vl-technical-report.txt`（91584 字符）供引用检索。