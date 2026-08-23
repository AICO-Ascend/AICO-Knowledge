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
> ## Description (architecture, components, data flow + key takeaway)

The figure contrasts DeepStack with conventional LMMs in three panels.

**Left ("Sequence LMMs")**: Visual tokens from high/low-resolution images are concatenated into a flat sequence fed entirely into one Transformer stack (×L).

**Middle ("DeepStack LMMs")**: Tokens form a grid of groups (1–4) infused into transformer layers from bottom to top via residual connections—1→*l_a*, 2→*l_b*, 3→*l_c*, 4→*l_d*—requiring no architecture modification.

**Right (Radar chart)**: Compares Sequence baselines (vis_tok=576/2880, ctx_len=576/2880) with DeepStack-V (Vicuna-7B) and DeepStack-L (CLIP ViT-L), both using vis_tok=2880, ctx_len=576, across VQAv2, GQA, TextVQA, DocVQA, InfoVQA, SEED, POPE.

**Key takeaway**: Distributing token groups across intermediate layers lets DeepStack process 4× more visual tokens at the same context length, yielding major gains without altering the underlying architecture.

---

## Caption (verbatim)

> Figure 1: Left: Conventional large multimodal models (LMMs) *string* all visual tokens into a sequence for high- and low-resolution images. Middle: Our DeepStack LMMs *stack* the tokens into a grid and infuse them into the first and middle transformer layers from bottom to top (■ ↑ ■ ↑ ■ ↑), simply using a residual connection. With no architecture modification and context length increasing, our model can handle multiple times more visual tokens as inputs. Right: We apply *DeepStack* separately to Vicuna-7B (DeepStack-L) and CLIP ViT-L (DeepStack-V). Our models can take 4× more visual tokens, and significantly outperforms the sequence LMM with same context length and rival the one using a much longer context, over a wide range of benchmarks.

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig02.png]]
*整页渲染: ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p04.png]]*
> [!quote] caption
> Architecture of DeepStack. The main innovation lies in the DeepStack strategy that infuses visual tokens into different layers. Left: DeepStack for LLMs. Given an input image, we feed the tokens extracted from the low-resolution version to the input layer of LLM. Considering the 2D nature of images, we extra the neighbors from the high-resolution version and reorganize them into DeepStack, which a

> [!tip] 技术解读（多模态）
> ## Figure 2 Description

**Architecture & Data Flow:** The figure illustrates two variants of the DeepStack strategy for infusing visual tokens across layers:

- **DeepStack-L (left, for LLMs):** Both a low-resolution image and a high-resolution image are processed through a shared **Vision Encoder** and **Connector**. The low-resolution visual tokens enter the *first* LLM Block, while successive groups of high-resolution neighbor tokens (numbered 2–5) are stacked and progressively injected into *deeper* LLM Blocks alongside text tokens.

- **DeepStack-V (right, for ViTs):** The same dual-resolution idea is applied earlier in the pipeline. Low-res and high-res images pass through a **Patch Embed** and a **ViT Block**, with progressive visual-token groups inserted at successive ViT Blocks before a **Connector** feeds the final representation into the **LLM** along with text tokens.

**Key Technical Takeaway:** DeepStack improves fine-grained visual understanding without expanding the visual context length by *distributing* visual tokens across layers rather than concatenating them at the input — a global-view stream at shallow layers plus stacked high-resolution features at deeper layers.

## Caption (verbatim)

**Figure 2: Architecture of DeepStack.** The main innovation lies in the *DeepStack* strategy that infuses visual tokens into different layers. Left: *DeepStack* for LLMs. Given an input image, we feed the tokens extracted from the low-resolution version to the input layer of LLM. Considering the 2D nature of images, we extra the neighbors from the high-resolution version and reorganize them into *DeepStack*, which are then fed to the consequent layers in LLMs. Right: *DeepStack* for ViTs. We apply similar sampling strategy but feed the visual tokens into the ViT layers of vision encoder.

### Figure 3 (p.8) ⭐深度解读
![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig03.png]]
*整页渲染: ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p08.png]]*
> [!quote] caption
> Analysis on using LLM layers to process visual tokens. (a) We insert the visual tokens into different starting layers and initialize the correspondence input embeddings as zero; (b) We fix the first layer to insert global visual tokens and ablation on the interval s for stacking high-resolution tokens; (c) We ablation number of layers for token stacking. 8

> [!tip] 技术解读（多模态）
> **Figure 3 Description:**

**Components:** Three side-by-side ablation line plots, each plotting "Mean score" (y-axis, ~48–51) against a hyperparameter (x-axis), all comparing DeepStack configurations on a 7-benchmark suite.

**(a) Starting layer to insert visual tokens:** Layer index (0–24). Score remains ~49 for early layers (0–8), then drops sharply at layer 24. ⇒ Earliest insertion is best.

**(b) Layer interval for DeepStack:** Interval *s* (0–5). Score peaks at *s*=1–2 (~51) and gradually declines. ⇒ Moderate spacing optimal.

**(c) Number of layers for DeepStack:** N-Layers (0–9). Score peaks at N=4 (~51). ⇒ ~4 stacking layers optimal.

**Key takeaway (≤120 words):** DeepStack is robust to insertion location at early LLM layers but degrades if visual tokens are injected too late (≥16). Performance is maximized when stacking spans roughly 4 intermediate layers with a small interval (~1–2), confirming that interleaving visual features across multiple mid-layers—not just the input—yields the strongest gains, while too few or too many stacking layers both hurt.

**Caption (verbatim):**
"Figure 3: **Analysis on using LLM layers to process visual tokens.** (a) We insert the visual tokens into different starting layers and initialize the correspondence input embeddings as zero; (b) We fix the first layer to insert global visual tokens and ablation on the interval *s* for stacking high-resolution tokens; (c) We ablation number of layers for token stacking."

### Figure 4 (p.10) ⭐深度解读
![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig04.png]]
*整页渲染: ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p10.png]]*
> [!quote] caption
> Visualization. Both LLaVA-1.5 and DeepStack use 576 visual context length for a fair comparison.

> [!tip] 技术解读（多模态）
> **Figure 4 — Description:**

**Components / Layout:** The figure presents qualitative comparisons between LLaVA-1.5 and DeepStack (both using 576 visual tokens). The **top row** shows four images (a card, a "Welcome to Washington DC" board, candy/wine bottles, and a phone) with question–answer pairs; red circles highlight the queried area. The **middle panel** compares detailed captions on a people/cow scene, with correct facts highlighted in blue and hallucinations in red. The **bottom** is a heptagonal radar chart benchmark across VQAv2, GQA, POPE, SEED, TextVQA, DocVQA, and InfoVQA, with DeepStack (green/red) consistently enclosing LLaVA-1.5 (blue).

**Key takeaway:** DeepStack's multi-layer stacking of high-resolution tokens preserves fine-grained details (small text, brand labels, background objects) that single-layer low-resolution baselines like LLaVA-1.5 hallucinate or miss.

**Caption (verbatim):**
"Figure 4: **Visualization.** Both LLaVA-1.5 and DeepStack use 576 visual context length for a fair comparison. Top: We mark the area corresponding to each question with a **red circle**. DeepStack can well answer the questions which need high-resolution and fine-grained understanding. Bottom: DeepStack demonstrates a more accurate visual understanding in detailed visual captioning."

### Figure 5 (p.9) ⭐深度解读
![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig05.png]]
*整页渲染: ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p09.png]]*
> [!quote] caption
> Visualization of three sam- pling methods for DeepStack.

> [!tip] 技术解读（多模态）
> ## Description

**Main figure (Figure 5): Visualization of three sampling methods for DeepStack**

The figure presents three 4×4 grids of color-coded, numbered cells (1–4) that illustrate how high-resolution visual tokens are sampled and arranged before being stacked across the DeepStack layers.

- **2d Spatial (default):** Each 2×2 block shares the same number/color, reflecting a 4-neighbor spatial sampling that preserves local 2D coherence across layers.
- **1d Sequential:** Numbers progress linearly (1→4) within the grid; tokens are first flattened into a 1D sequence and then uniformly resampled per layer, destroying spatial locality.
- **2d Grid:** Tokens are partitioned into 2D sub-grids that are then stacked per layer, producing a checker-like interleaved pattern.

**Key technical takeaway:** Preserving 2D spatial coherence in how high-resolution tokens are organized before stacking (the *2d Spatial* strategy) is critical — Table 5 shows it achieves the best average score (51.1 AVG) compared to *2d Grid* (49.0) and *1d Sequential* (49.3), confirming that geometry-aware sampling materially improves multimodal performance.

## Caption (verbatim)

**Figure 5:** Visualization of three sampling methods for **DeepStack**.

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