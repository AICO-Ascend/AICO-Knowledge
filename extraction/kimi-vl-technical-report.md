---
paper_num: "21"
title: "KIMI-VL TECHNICAL REPORT"
authors: ""
date: "2025/4/10"
arxiv: "https://arxiv.org/abs/2504.07491"
pdf: "papers/kimi-vl-technical-report.pdf"
slug: "kimi-vl-technical-report"
tags: [multimodal]
---

# KIMI-VL TECHNICAL REPORT

> [!abstract] 摘要（原文）
> 1\. 🚀 Kimi-VL 是一个高效的开源 MoE VLM，具备先进的多模态推理、长上下文理解和强大的 agent 能力，其语言解码器（Kimi-VL-A3B）仅激活2.8B参数，并结合了原生分辨率的 MoonViT 视觉编码器。 2. 🏆 该模型在 OSWorld、大学级图像/视频理解、OCR 和数学推理等挑战性任务上表现出色，有效竞争并超越了 GPT-4o-mini、Qwen2.5-VL-7B 等前沿模型，且支持128K长上下文和超高分辨率视觉输入。 3. 💡 基于 Kimi-VL，Kimi-VL-Thinking-2506 通过长 CoT SFT 和 RL 进一步提升了长程推理能力，在 MMMU、MathVision 等基准测试中取得了突破性表现，以约3B激活参数重新定义了高效多模态思维模型的标准。

## 元信息
- **发表日期**: 2025/4/10
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2504.07491
- **本地 PDF**: `papers/kimi-vl-technical-report.pdf`
- **页数**: 24

## 图表（原文 caption + 页码）

### Figure 1 (p.1)
![[assets/kimi-vl-technical-report-p01.png]]
> [!quote] caption
> Comparison between Kimi-VL-Thinking-2506 and frontier open-source VLMs, including short-thinking VLMs (e.g. Gemma-3 series, Qwen2.5-VL series) and long-thinking VLMs (QVQ-72B/Max-Preview), on MathVision benchmark. Our model achieves strong multimodal reasoning with just 2.8B LLM activated parameters.

### Figure 2 (p.2)
![[assets/kimi-vl-technical-report-p02.png]]
> [!quote] caption
> Highlights of Kimi-VL performance for a wide range of benchmarks like, general benchmarks (MMMU, MMBench), OCR (InfoVQA), multi-image (BLINK), long video (LongVideoBench, Video-MME), long document (MMLongBench-Doc), and agent (ScreenSpot-Pro and OSWorld). Detailed results are presented in Table 3. 1

### Figure 3 (p.3)
![[assets/kimi-vl-technical-report-p03.png]]
> [!quote] caption
> The model architecture of Kimi-VL and Kimi-VL-Thinking, consisting of a MoonViT that allows native- resolution images, an MLP projector, and a Mixture-of-Experts (MoE) language decoder. 1) Kimi-VL is smart: it has comparable text ability against efficient pure-text LLMs; without long thinking, Kimi-VL is already competitive in multimodal reasoning and multi-turn agent benchmarks, e.g., MMMU, MathV

### Figure 4 (p.4)
![[assets/kimi-vl-technical-report-p04.png]]
> [!quote] caption
> The pre-training stages of Kimi-VL consume a total of 4.4T tokens after text-only pre-training of its language model. To preserve text abilities, all stages that update the language model are joint training stages. preprocessing operations enable MoonViT to share the same core computation operators and optimization as a language model, such as the variable-length sequence attention mechanism suppo

### Figure 5 (p.6)
![[assets/kimi-vl-technical-report-p06.png]]
> [!quote] caption
> The post-training stages of Kimi-VL and Kimi-VL-Thinking, including two stages of joint SFT in 32K and 128K context, and further long-CoT SFT and RL stages to activate and enhance long thinking abilities. to 800,000. The joint long-context stage is conducted in two sub-stages, where each one extends the model’s context length by four times. For data composition, we filter and upsample the ratio of

### Figure 6 (p.8)
![[assets/kimi-vl-technical-report-p08.png]]
> [!quote] caption
> Manuscript reasoning visualization. Kimi-VL-Thinking demonstrates the ability to perform historical and scientific inference by analyzing handwritten manuscripts step by step. In this example, our model identifies the author as Albert Einstein based on handwriting style, content analysis, and language cues. It reasons that the manuscripts relate to gravitational field equations, consistent with Ei

### Figure 7 (p.12)
![[assets/kimi-vl-technical-report-p12.png]]
> [!quote] caption
> Kimi-VL exhibits strong visual reasoning capabilities by grounding visual content in spatial, contextual, and cultural knowledge. It accurately identifies matching urban locations based on structural and layout features, interprets scenes from video games like Cyberpunk 2077 using stylistic cues, and recognizes real-world landmarks such as the

### Figure 8 (p.13)
![[assets/kimi-vl-technical-report-p13.png]]
> [!quote] caption
> Kimi-VL demonstrates its capability to perform symbolic reasoning and geometric inference by solving a circle geometry problem step by step. The model analyzes given conditions, applies geometric theorems such as the inscribed angle theorem and properties of triangle angles, and accurately derives the target angle. presented in visual contexts. On the more challenging MathVision benchmark, due to 

### Figure 9 (p.14)
![[assets/kimi-vl-technical-report-p14.png]]
> [!quote] caption
> Diverse OCR visualization. Kimi-VL demonstrates strong OCR capabilities across varied content types, including structured financial tables, complex mathematical formulas, and handwritten Chinese text. The model accurately parses tabular data into markdown, converts formulas to LaTeX, and transcribes handwritten paragraphs with contextual understanding, showcasing its versatility in multimodal text

### Figure 10 (p.15)
![[assets/kimi-vl-technical-report-p15.png]]
> [!quote] caption
> Kimi-VL is capable of following multi-step reasoning processes to complete complex GUI tasks. In this example, it successfully enables the “Do Not Track” feature in the Chrome browser to enhance online privacy. The agent interprets each screen, identifies relevant UI elements, and performs the appropriate actions sequentially with clear thoughts, actions, and API calls. 15

### Figure 11 (p.16)
![[assets/kimi-vl-technical-report-p16.png]]
> [!quote] caption
> Video scene splitting. Kimi-VL processes a long-form video by segmenting it into coherent scenes and providing detailed start/end timestamps along with fine-grained natural language descriptions for each scene.†

### Figure 12 (p.17)
![[assets/kimi-vl-technical-report-p17.png]]
> [!quote] caption
> Catching and understanding key details from an hour-long video course. Kimi-VL demonstrates its ability to comprehend and interpret instructional video content by analyzing frame sequences and extracting conceptual progression over time. In this case, the model identifies a deepening of the traditional saying “Teach a man to fish, and you feed him for a lifetime” into a more nuanced idea: “Teach h

### Figure 13 (p.16)
![[assets/kimi-vl-technical-report-p16.png]]
> [!quote] caption
> Specifically, increasing the max thinking token length at inference time consistently improves test-time accuracy across all three 16

## 相关论文

- [[qwen3-vl-technical-report]] — Qwen3-VL Technical Report
- [[qwen2-5-vl-technical-report]] — Qwen2.5-VL Technical Report
- [[kimi-k2-5-visual-agentic-intelligence]] — KIMI K2.5: VISUAL AGENTIC INTELLIGENCE
- [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] — DeepStack: Deeply Stacking Visual Tokens is Surprisingly Simple and Effective for LMMs
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation

## 全文文本
全文已存 `extraction/fulltext/kimi-vl-technical-report.txt`（122024 字符）供引用检索。