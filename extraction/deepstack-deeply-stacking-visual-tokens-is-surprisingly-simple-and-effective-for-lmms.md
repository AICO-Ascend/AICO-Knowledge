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
> 【图文联合解读】**图1联合解读：**

图1含三部分：(1)**左**——Sequence LMMs将576或2880视觉token**拼成一条长序列**送入L层Transformer，序列长度随分辨率线性增长；(2)**中**——DeepStack LMMs把2880 token**堆叠为网格并分4组**（每组576），分别在l_a、l_b、l_c、l_d四层通过**残差连接注入**（■↑■↑■↑），ctx_len恒为576；(3)**右**——雷达图显示DeepStack-L（红，2880 tok/576 ctx）在VQAv2（80.9）、GQA（64.4）、TextVQA（71.9）、DocVQA（46.0）、InfoVQA（31.6）、SEED（62.6）、POPE（87.5）7项基准全面超越Sequence（蓝/橙）。

**论证结论**：以"分层堆叠+残差注入"替代"长序列拼接"，无需改动架构即可在**不增加上下文长度**前提下保留高分辨率视觉信息，并在多基准取得最优。该图作为论文开篇总览，奠定了DeepStack方法在整篇方法/实验链路中的核心立论——以最简改动突破高分辨率LMM的上下文瓶颈。

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig02.png]]
*整页渲染: ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p04.png]]*
> [!quote] caption
> Architecture of DeepStack. The main innovation lies in the DeepStack strategy that infuses visual tokens into different layers. Left: DeepStack for LLMs. Given an input image, we feed the tokens extracted from the low-resolution version to the input layer of LLM. Considering the 2D nature of images, we extra the neighbors from the high-resolution version and reorganize them into DeepStack, which a

> [!tip] 技术解读（多模态）
> 【图文联合解读】图以羊图说明两种实现：3×3高分辨率图提取局部邻域，低分辨率图提供整体内容，每组以4个视觉token表示。DeepStack-L将编号1、2、3、5的视觉组依次注入LLM不同块；DeepStack-V在ViT多个中间层堆叠特征，再经Connector与文本token进入LLM。该设计先编码全局信息，再逐层补充高分辨率细节，以简单堆叠深化视觉—语言融合；它是连接视觉编码与语言推理的核心方法，并支撑后续性能与消融实验。

### Figure 3 (p.8) ⭐深度解读
![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig03.png]]
*整页渲染: ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p08.png]]*
> [!quote] caption
> Analysis on using LLM layers to process visual tokens. (a) We insert the visual tokens into different starting layers and initialize the correspondence input embeddings as zero; (b) We fix the first layer to insert global visual tokens and ablation on the interval s for stacking high-resolution tokens; (c) We ablation number of layers for token stacking. 8

> [!tip] 技术解读（多模态）
> 【图文联合解读】将对应输入嵌入置零，并固定首层插入全局词元后，图消融起始层、间隔s与堆叠层数：(a) 起始层0/1/2/4/8/16/24时均分约49.5/49.5/49.4/49.2/48.2/44.2/38.0，越早越好；(b) s=0～5约为49.0/50.8/51.1/50.9/50.8/50.4，s=2最佳；(c) 堆叠0/2/4/6/9层约为49.2/50.3/51.0/50.0/49.5，4层最佳。视觉特征应早期、适度间隔、跨层反复注入LLM；该实验验证DeepStack机制并确定关键超参。

### Figure 4 (p.10) ⭐深度解读
![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig04.png]]
*整页渲染: ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p10.png]]*
> [!quote] caption
> Visualization. Both LLaVA-1.5 and DeepStack use 576 visual context length for a fair comparison.

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图对比 LLaVA-1.5 与 DeepStack（均 576 visual tokens）：上排 4 组细粒度 VQA——角落文字"Postcode"、白板星数 3、Hershey's 糖果条、HTC 手机，DeepStack 全对而 LLaVA-1.5 全错（红圈标注提问区域）；下排 2 组细节描述中，LLaVA-1.5 幻觉虚构餐桌/手袋/"Voice over QAM"，DeepStack 正确识别背景卡车与基准名 VQAv2/Pope/GQA；底部雷达图覆盖 VQAv2、GQA、TextVQA、DocVQA、InfoVQA、SEED、POPE 7 项基准。原文以此定性佐证 DeepStack 在等长视觉上下文下捕获更细粒度信息并抑制幻觉，支撑"少 token 不损精度"的核心结论。

### Figure 5 (p.9) ⭐深度解读
![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig05.png]]
*整页渲染: ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p09.png]]*
> [!quote] caption
> Visualization of three sam- pling methods for DeepStack.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**核心对象：** 图示为 4×4 网格，编号 1–4 代表 4 个 LLM 层堆叠位置，呈现三种视觉 token 分配策略——2d Spatial 采用 2×2 棋盘式交错（每层均匀散布全图）；1d Sequential 按行顺序堆叠（前 1/4 行→层1，后 1/4 行→层4）；2d Grid 按 2×2 块分区（前 1/4 区域→层1，依此类推）。

**关键论证结论：** DeepStack 需将 ViT 视觉 token 分组后送入不同 LLM 层；三种采样对应"空间均匀散布 / 严格时序分段 / 块状区域划分"三种粒度，为后续消融实验提供采样方案的对照基线。

**论文链路作用：** 衔接方法设计与实验章节，作为堆叠机制的可视化定义，明确不同采样如何影响视觉-语言特征在各层的融合方式。

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