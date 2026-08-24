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

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig01.png]]
*整页渲染: ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p01.png]]*
> [!quote] caption
> Left: Conventional large multimodal models (LMMs) string all visual tokens into a sequence for high- and low-resolution images. Middle: Our DeepStack LMMs stack the tokens into a grid and infuse them into the first and middle transformer layers from bottom to top (■↑■↑■↑) simply using a residual connection. With no architecture modification and context length increasing, our model can handle multi

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 1）**

该图分两部分：左为架构示意，将视觉token分4组（标注1–4）通过残差连接沿Transformer由浅至深（层l_a…l_d）分层注入，而非一次性串入序列；右为七维雷达图，对比7个基准（VQAv2 78.5/80.9/87.6、GQA 62.0/64.4、TextVQA 58.2/61.9、DocVQA 28.1/46.0、InfoVQA 25.8/31.6、SEED 58.6/62.9、POPE 85.9/87.6），四曲线分别为Sequence-576ctx、Sequence-2880ctx、DeepStack-V与DeepStack-L（均2880token/576ctx）。

原文借此论证：仅靠"分层堆叠+残差注入"，在不增上下文长度前提下，DeepStack-L即可全面碾压同ctx的串接基线，并逼近5×ctx的串接模型。

论文作用：以一张图同时完成"动机（高分辨率需更多token）→方法（分层注入）→收益（4× token且不增ctx）"的全链路论证，作为后续Vicuna-7B/CLIP ViT-L实验的可视化总纲。

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig02.png]]
*整页渲染: ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p04.png]]*
> [!quote] caption
> Architecture of DeepStack. The main innovation lies in the DeepStack strategy that infuses visual tokens into different layers. Left: DeepStack for LLMs. Given an input image, we feed the tokens extracted from the low-resolution version to the input layer of LLM. Considering the 2D nature of images, we extra the neighbors from the high-resolution version and reorganize them into DeepStack, which a

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

图示 **DeepStack-V**（视觉编码器侧架构）：高分辨率图像被切分为多块网格（如编号 1–5 的彩色区域），低分辨率版本对应 1 块；经 Patch Embed 与首层 ViT Block 处理后，串接多层 ViT Block，每层间分别注入 4 个来自不同图像区域/分辨率的视觉 token 组（图中红/橙/绿/紫标号的 1-1-1-1、2-2-2-2、5-5-5-5），最终经 Connector 接入 LLM 与文本 token 融合。

**技术结论**：DeepStack 将视觉 token 分散堆叠至 ViT 多个中间层（而非仅输入层），借助高分辨率邻域块在不同深度强化细粒度视觉表征。

**方法作用**：作为论文核心架构图，证明"多层视觉 token 注入"在视觉编码器和 LLM 两侧均通用，是后续消融与基准实验的方法基石。

### Figure 3 (p.8) ⭐深度解读
![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig03.png]]
*整页渲染: ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p08.png]]*
> [!quote] caption
> Analysis on using LLM layers to process visual tokens. (a) We insert the visual tokens into different starting layers and initialize the correspondence input embeddings as zero; (b) We fix the first layer to insert global visual tokens and ablation on the interval s for stacking high-resolution tokens; (c) We ablation number of layers for token stacking. 8

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图3核心内容**：左图(b)展示插入全局token后，高分辨率token堆叠间隔*s*∈{3,4,5}对性能的影响——平均得分稳定在49.7–49.9，几乎无变化；右图(c)展示堆叠层数N∈{0,2,4,6,9}的影响——0层约49.5，4层达到峰值约50.7，9层回落至约49.5。

**关键结论**：间隔*s*鲁棒（间隔1–2即可覆盖所有层），无需精细调参；层数需折中，过少无法充分融合、过多反而引入干扰，4层为最优。

**论文作用**：为DeepStack"深层堆叠"策略提供超参依据，证明该设计轻量且对堆叠密度不敏感，仅需选好堆叠次数即可稳定获益，是方法实用性的关键验证。

### Figure 4 (p.10) ⭐深度解读
![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig04.png]]
*整页渲染: ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p10.png]]*
> [!quote] caption
> Visualization. Both LLaVA-1.5 and DeepStack use 576 visual context length for a fair comparison.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图像无法有效辨认**——所展示的图片内容为循环图表（VOQA/POP/GAQA 等标注）与 DeepStack Figure 4（视觉问答对比示例）无关，疑似加载错误，故仅依据原文进行解读：

1) **核心对象与结构**：图分两栏对比 LLaVA-1.5 与 DeepStack，两者均使用 576 视觉 token 的同等上下文长度；上方样本在图像中以**红圈**标注问题对应区域，下方样本展示细粒度图像描述任务。

2) **关键技术结论**：在 token 数严格公平的前提下，DeepStack 通过多层叠加（stacking）策略，在需要**高分辨率与细粒度视觉理解**的 VQA（上方示例）以及**细节图像描述**（下方示例）上显著优于 LLaVA-1.5，验证视觉表征的层级堆叠优于单层扩张。

3) **整体链路作用**：作为定性可视化（qualitative visualization），与论文中量化的 LLaVA-Bench、MMBench、MM-Vet、TextVQA、POPE、MMMU 等基准结果相互印证，支撑"深度堆叠视觉 token 而非简单增加 token 数"这一核心方法论主张。

### Figure 5 (p.9) ⭐深度解读
![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig05.png]]
*整页渲染: ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p09.png]]*
> [!quote] caption
> Visualization of three sam- pling methods for DeepStack.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图5展示DeepStack对4×4视觉token的三种采样分组方案：2D Spatial（行内交替"1,2,1,2 / 3,4,3,4"，行列均交替）、1D Sequential（按行同色，"1,1,1,1 → 4,4,4,4"纵向排列）、2D Grid（2×2块同色，"1,1,2,2 / 3,3,4,4"分块均匀）。相同编号token在同一层被堆叠送入LMM。论文借此论证分组策略的多样性与鲁棒性——2D Spatial细粒度空间交替、1D Sequential保持序列连续性、2D Grid强化局部块一致性，三者均支撑多层视觉token整合。作为消融可视化，它验证了"深度堆叠视觉token"对采样方式不敏感的核心结论，是证明DeepStack通用性的关键图示。

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

## 技术点深读（DEEP）

![[deep/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms.txt`（62336 字符）供引用检索。