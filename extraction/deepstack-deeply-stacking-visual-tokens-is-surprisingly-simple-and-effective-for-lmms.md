---
paper_num: "14"
title: "DeepStack: Deeply Stacking Visual Tokens is Surprisingly Simple and Effective for LMMs"
authors: "is Surprisingly Simple and Effective for LMMs Lingchen Meng 1,2∗ Jianwei Yang 3∗ Rui Tian1,2 Xiyang Dai3 Zuxuan Wu1,2† Jianfeng Gao3† Yu-Gang Jiang1,2 1Shanghai Key Lab of Intell. Info. Processing, School of CS, Fudan Un"
date: "2026/6/10"
arxiv: "https://arxiv.org/abs/2406.04334"
pdf: "papers/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms.pdf"
slug: "deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms"
tags: [multimodal]
---

# DeepStack: Deeply Stacking Visual Tokens is Surprisingly Simple and Effective for LMMs

> [!abstract] 摘要（原文）
> 1\. 💡 针对现有大型多模态模型（LMMs）将所有视觉token作为序列输入第一层导致的高昂计算和内存成本，DeepStack提出了一种创新策略，通过分层堆叠视觉token并从底部到顶部将其注入Transformer层，以有效处理高分辨率图像。 2. ⚙️ 该方法利用简单的残差连接，在不改变架构和不增加上下文长度的前提下，使LMMs能够处理多倍视觉token，并可应用于语言Transformer（DeepStack-L）和视觉Transformer（DeepStack-V）。 3. ✨ 实验结果表明，DeepStack在保持相同上下文长度的情况下，在VQA和文本导向型任务（如TextVQA、DocVQA、InfoVQA）上取得了显著性能提升，有效缓解了视觉幻觉，并实现了性能与效率之间的更优平衡。

## 元信息
- **发表日期**: 2026/6/10
- **作者**: is Surprisingly Simple and Effective for LMMs Lingchen Meng 1,2∗ Jianwei Yang 3∗ Rui Tian1,2 Xiyang Dai3 Zuxuan Wu1,2† Jianfeng Gao3† Yu-Gang Jiang1,2 1Shanghai Key Lab of Intell. Info. Processing, School of CS, Fudan Un
- **arXiv**: https://arxiv.org/abs/2406.04334
- **本地 PDF**: `papers/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms.pdf`
- **页数**: 17

## 图表（原文 caption + 页码）

### Figure 1 (p.1)
![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p01.png]]
> [!quote] caption
> Left: Conventional large multimodal models (LMMs) string all visual tokens into a sequence for high- and low-resolution images. Middle: Our DeepStack LMMs stack the tokens into a grid and infuse them into the first and middle transformer layers from bottom to top (■↑■↑■↑) simply using a residual connection. With no architecture modification and context length increasing, our model can handle multi

### Figure 2 (p.4)
![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p04.png]]
> [!quote] caption
> Architecture of DeepStack. The main innovation lies in the DeepStack strategy that infuses visual tokens into different layers. Left: DeepStack for LLMs. Given an input image, we feed the tokens extracted from the low-resolution version to the input layer of LLM. Considering the 2D nature of images, we extra the neighbors from the high-resolution version and reorganize them into DeepStack, which a

### Figure 3 (p.8)
![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p08.png]]
> [!quote] caption
> Analysis on using LLM layers to process visual tokens. (a) We insert the visual tokens into different starting layers and initialize the correspondence input embeddings as zero; (b) We fix the first layer to insert global visual tokens and ablation on the interval s for stacking high-resolution tokens; (c) We ablation number of layers for token stacking. 8

### Figure 4 (p.10)
![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p10.png]]
> [!quote] caption
> Visualization. Both LLaVA-1.5 and DeepStack use 576 visual context length for a fair comparison.

### Figure 5 (p.9)
![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p09.png]]
> [!quote] caption
> Visualization of three sam- pling methods for DeepStack.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\begin{split} \mathcal{L} & = \sum_{t=1}^N \log \mathcal{P}_{\theta}(x_{t+1} \mid x_{1:t}) \end{split}
$$

$$
\mathcal{L} = \sum_{t=1}^N \log \mathcal{P}_{\theta}(x_{t+1} \mid x_{1:t}, \mathbf{X})
$$

$$
\begin{split} \mathbf{X} &= \mathcal{M}(\mathbf{f^v}); \hspace{2mm}\mathbf{f^v} = \mathcal{F}^v(\mathbf{I}) \\ \end{split}
$$

$$
\begin{split} \mathbf{X^{stack}} &= \{\mathbf{{X^{stack}}^{1}, {X^{stack}}^{2}, ..., {X^{stack}}^{s}} \} \\ &= \mathrm{Sampling2D}\left(\mathcal{M}(\mathcal{F}^v(\mathbf{I^{hires}}))\right) \end{split}
$$

$$
\begin{split} &\mathbf{H}^{V^1} = \mathcal{P}^{V^1}\big ( \mathbf{X}\big ) + \mathbf{X^{stack}}^{1}\\ &\mathbf{H}^{V^2} = \mathcal{P}^{V^2}\big (\mathbf{H}^{V^1}\big ) + \mathbf{X^{stack}}^{2} \\ &\mathbf{H}^{L} = \mathcal{P}^{\mathbb{L}}\big (\mathbf{H}^{V^n}\big ) \\ \end{split}
$$

$$
\begin{split} &\mathbf{H}^{L} = \mathcal{P}\big (\mathrm{SeqCat}[ \mathbf{X}, \mathbf{X^{stack}} ]\big ) \\ \end{split}
$$

$$
\begin{split} \mathbf{H}^{L} & = \mathcal{P}\big (\mathcal{M}(\mathrm{DimCat}[ \mathbf{f}, \mathbf{f^{hires}} ]) \big ) \\ &\approx \mathcal{P}\big ( \mathcal{M}^{1}(\mathbf{f}) + \mathcal{M}^{2}(\mathbf{f^{hires}}) \big ) \end{split}
$$

$$
\vspace{\baselineskip} \mathbf{H}^{L} = \tikzmarknode{x}{\highlight{red}{$\mathcal{P}^{\mathbb{L}}$}}\Bigg( \tikzmarknode{s}{\highlight{blue}{$\mathcal{P}^{V^n}\bigg( ...\Big(\mathcal{P}^{V1}\big (\mathbf{X}+ \mathbf{X^{stack}}^1\big ) + \mathbf{X^{stack}}^2 \Big) ... \bigg) + \mathbf{X^{stack}}^{n}$}} \Bigg)
$$

## 相关论文

- [[kimi-k2-5-visual-agentic-intelligence]] — KIMI K2.5: VISUAL AGENTIC INTELLIGENCE
- [[qwen3-vl-technical-report]] — Qwen3-VL Technical Report
- [[kimi-vl-technical-report]] — KIMI-VL TECHNICAL REPORT
- [[qwen2-5-vl-technical-report]] — Qwen2.5-VL Technical Report
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation

## 全文文本
全文已存 `extraction/fulltext/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms.txt`（62336 字符）供引用检索。