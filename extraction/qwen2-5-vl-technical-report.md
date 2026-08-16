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

### Figure 1 (p.3)
![[assets/qwen2-5-vl-technical-report-p03.png]]
> [!quote] caption
> The Qwen2.5-VL framework demonstrates the integration of a vision encoder and a language model decoder to process multimodal inputs, including images and videos. The vision encoder is designed to handle inputs at their native resolution and supports dynamic FPS sampling. Images of varying sizes and video frames with different FPS rates are dynamically mapped to token sequences of varying lengths. 

## 相关论文

- [[qwen3-vl-technical-report]] — Qwen3-VL Technical Report
- [[kimi-vl-technical-report]] — KIMI-VL TECHNICAL REPORT
- [[kimi-k2-5-visual-agentic-intelligence]] — KIMI K2.5: VISUAL AGENTIC INTELLIGENCE
- [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] — DeepStack: Deeply Stacking Visual Tokens is Surprisingly Simple and Effective for LMMs
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation

## 全文文本
全文已存 `extraction/fulltext/qwen2-5-vl-technical-report.txt`（91584 字符）供引用检索。