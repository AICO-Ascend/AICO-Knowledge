---
paper_num: "38"
title: "Root Mean Square Layer Normalization"
authors: "Biao Zhang1 Rico Sennrich2,1 1School of Informatics, University of Edinburgh 2Institute of Computational Linguistics, University of Zurich B.Zhang@ed.ac.uk, sennrich@cl.uzh.ch"
date: "2026/1/7"
arxiv: "https://arxiv.org/abs/1910.07467"
pdf: "papers/root-mean-square-layer-normalization.pdf"
slug: "root-mean-square-layer-normalization"
tags: []
---

# Root Mean Square Layer Normalization

> [!abstract] 摘要（原文）
> 1\. 🤔 本文提出了一种名为 Root Mean Square Layer Normalization (RMSNorm) 的新型归一化方法，通过仅使用均方根（RMS）统计量来正则化输入，旨在提高 LayerNorm 的计算效率并保持其重缩放不变性。 2. 💡 RMSNorm 假设 LayerNorm 的重定中心不变性是可有可无的，并证明仅依赖重缩放不变性已足以稳定激活并加速模型收敛；此外，文章还引入了 Partial RMSNorm (pRMSNorm) 以进一步提升效率。 3. ⚡️ 在机器翻译、图像分类等任务上的广泛实验表明，RMSNorm 在保持与 LayerNorm 相当性能的同时，可将运行时间缩短 7% 至 64%，证明了其在不同模型和实现上的效率优势。

## 元信息
- **发表日期**: 2026/1/7
- **作者**: Biao Zhang1 Rico Sennrich2,1 1School of Informatics, University of Edinburgh 2Institute of Computational Linguistics, University of Zurich B.Zhang@ed.ac.uk, sennrich@cl.uzh.ch
- **arXiv**: https://arxiv.org/abs/1910.07467
- **本地 PDF**: `papers/root-mean-square-layer-normalization.pdf`
- **页数**: 14

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/root-mean-square-layer-normalization-p01.png]]
> [!quote] caption
> One major feature of LayerNorm that is widely regarded as contributions to the stabilization is its re-centering invariance property: the summed inputs after LayerNorm remain intact when the inputs or weight matrix is shifted by some amount of noise. We argue that this mean normalization does not reduce the variance of hidden states or model gradients, and hypothesize that it has little impact on 

> [!tip] 技术解读（多模态）
> # Description

**No figure is visible on the provided page.** The image shows only the first page (title page) of the paper "Root Mean Square Layer Normalization" (Zhang & Sennrich, NeurIPS 2019, arXiv:1910.07467v1), containing the title, authors (Biao Zhang¹, Rico Sennrich²·¹), affiliations (University of Edinburgh; University of Zurich), abstract, and the opening paragraphs of Section 1 (Introduction). No diagram, plot, or figure is rendered in the supplied image.

The only in-text reference to a figure in this page is:
> "…the efficiency gain from faster and more stable training (in terms of number of training steps) is counter-balanced by an increased computational cost per training step, which diminishes the net efficiency, as shown in **Figure 1**."

# Caption Transcription

There is **no figure caption to transcribe**, as no figure appears on this page. The caption for Figure 1 is not present in the provided excerpt.

### Figure 2 (p.6) ⭐深度解读
![[assets/root-mean-square-layer-normalization-p06.png]]
> [!quote] caption
> SacreBLEU score on newstest2013 for the RNNSearch. Models are implemented accord- ing to Nematus [25] in Tensorﬂow.

> [!tip] 技术解读（多模态）
> **Figure Description:**

Figure 2 is a line plot comparing validation BLEU score convergence across five RNNSearch model variants over training. The x-axis shows training steps (×30k, ranging 0–50) and the y-axis shows Valid BLEU score (0–25). Five curves are plotted:
- **Baseline** (blue) — no normalization, slowest to converge
- **L2-Norm** (red) — slowest startup, lowest final score
- **LayerNorm** (orange) — rapid convergence, high plateau
- **RMSNorm** (green) — best final BLEU
- **pRMSNorm** (purple) — comparable to RMSNorm, slightly slower

Companion Table 2 reports final test BLEU on Test14/Test17 plus wall-clock time per 1k steps (Baseline 399s, LayerNorm 665s, RMSNorm 501s, pRMSNorm 493s — a ~25% speedup over LayerNorm).

**Key Technical Takeaway:** RMSNorm matches LayerNorm's re-scaling invariance while reducing compute by ~25% over LayerNorm in TensorFlow, making it an effective drop-in replacement that accelerates RNN convergence by ~50% without sacrificing translation quality.

**Caption (verbatim):** Figure 2: SacreBLEU score on newstest2013 for the RNNSearch. Models are implemented according to Nematus [25] in Tensorflow.

### Figure 3 (p.7) ⭐深度解读
![[assets/root-mean-square-layer-normalization-p07.png]]
> [!quote] caption
> SacreBLEU score on new- stest2013 (devset) for the RNNSearch with pRMSNorm. We use Tensorﬂow-version Ne- matus, and change p by a step size of 10%.

> [!tip] 技术解读（多模态）
> **Figure 3 Description (architecture/components/data flow):**
A single-line plot where the x-axis is the hyperparameter *p* (%) swept from ~20 to 100 in 10% steps, and the y-axis is the **Valid SacreBLEU score** (range ~22–25) on newstest2013. The blue curve (RNNSearch + pRMSNorm, Tensorflow Nematus) remains nearly flat around 24 BLEU with small dips, showing how the single scalar hyperparameter *p* flows into pRMSNorm and is evaluated end-to-end on a translation task.

**Key technical takeaway (≤120 words):**
pRMSNorm's SacreBLEU on the RNNSearch devset is largely insensitive to *p* across the entire 20–100% sweep, with all points landing within roughly ±1 BLEU of ~24. This indicates that practitioners do not need to carefully tune *p* to obtain strong translation quality; pRMSNorm delivers stable performance across a wide range of values, making it a drop-in alternative to LayerNorm/RMSNorm without sensitive hyperparameter selection.

**Caption (verbatim):**
*"Figure 3: SacreBLEU score on newstest2013 (devset) for the RNNSearch with pRMSNorm. We use Tensorflow-version Nematus, and change p by a step size of 10%."*

### Figure 4 (p.7) ⭐深度解读
![[assets/root-mean-square-layer-normalization-p07.png]]
> [!quote] caption
> SacreBLEU score curve of Layer-

> [!tip] 技术解读（多模态）
> **Figure 3 Description (architecture/components/data flow):**
A single-line plot where the x-axis is the hyperparameter *p* (%) swept from ~20 to 100 in 10% steps, and the y-axis is the **Valid SacreBLEU score** (range ~22–25) on newstest2013. The blue curve (RNNSearch + pRMSNorm, Tensorflow Nematus) remains nearly flat around 24 BLEU with small dips, showing how the single scalar hyperparameter *p* flows into pRMSNorm and is evaluated end-to-end on a translation task.

**Key technical takeaway (≤120 words):**
pRMSNorm's SacreBLEU on the RNNSearch devset is largely insensitive to *p* across the entire 20–100% sweep, with all points landing within roughly ±1 BLEU of ~24. This indicates that practitioners do not need to carefully tune *p* to obtain strong translation quality; pRMSNorm delivers stable performance across a wide range of values, making it a drop-in alternative to LayerNorm/RMSNorm without sensitive hyperparameter selection.

**Caption (verbatim):**
*"Figure 3: SacreBLEU score on newstest2013 (devset) for the RNNSearch with pRMSNorm. We use Tensorflow-version Nematus, and change p by a step size of 10%."*

### Figure 5 (p.8) ⭐深度解读
![[assets/root-mean-square-layer-normalization-p08.png]]
> [!quote] caption
> Error rate on validation set for the attentive reader model.

> [!tip] 技术解读（多模态）
> # Main Figure Description (Figure 5)

**Components:** Six normalization methods compared — Baseline, BatchNorm-Everywhere, BatchNorm-LSTM, LayerNorm, RMSNorm, and pRMSNorm — evaluated on an attentive reader model.

**Data flow:** Plot of *valid error rate* (y-axis, 0.4–1.0) vs. *training steps in thousands* (x-axis, 0–300k). Curves descend from ~1.0 and converge; BatchNorm-LSTM drops sharply by ~25k steps, LayerNorm/RMSNorm/pRMSNorm settle near 0.45 by ~50k steps, while Baseline converges slowest to ~0.48.

**Key takeaway:** RMSNorm matches LayerNorm's final accuracy but converges substantially faster, achieving comparable error rates with roughly 15% lower wall-clock time, demonstrating that reparameterized RMSNorm offers an attractive speed–performance trade-off.

---

**Caption (verbatim):**
Figure 5: Error rate on validation set for the attentive reader model.

### Figure 6 (p.8) ⭐深度解读
![[assets/root-mean-square-layer-normalization-p08.png]]
> [!quote] caption
> Recall@K values on validation set for the order-embedding models. worse than RMSNorm. Although in Figure 5 the performance of RMSNorm and LayerNorm is comparable, RMSNorm is around 15% faster than LayerNorm as shown in Table 6.3

> [!tip] 技术解读（多模态）
> # Main Figure Description (Figure 5)

**Components:** Six normalization methods compared — Baseline, BatchNorm-Everywhere, BatchNorm-LSTM, LayerNorm, RMSNorm, and pRMSNorm — evaluated on an attentive reader model.

**Data flow:** Plot of *valid error rate* (y-axis, 0.4–1.0) vs. *training steps in thousands* (x-axis, 0–300k). Curves descend from ~1.0 and converge; BatchNorm-LSTM drops sharply by ~25k steps, LayerNorm/RMSNorm/pRMSNorm settle near 0.45 by ~50k steps, while Baseline converges slowest to ~0.48.

**Key takeaway:** RMSNorm matches LayerNorm's final accuracy but converges substantially faster, achieving comparable error rates with roughly 15% lower wall-clock time, demonstrating that reparameterized RMSNorm offers an attractive speed–performance trade-off.

---

**Caption (verbatim):**
Figure 5: Error rate on validation set for the attentive reader model.

### Figure 7 (p.13) ⭐深度解读
![[assets/root-mean-square-layer-normalization-p13.png]]
> [!quote] caption
> SacreBLEU score curve over train- ing steps on newstest2013 (devset) for the RNNSearch. Models are trained with Nema- tus in Theano.

> [!tip] 技术解读（多模态）
> **Figure 7 Description:**

The figure is a line chart comparing five normalization methods' training dynamics for RNNSearch on WMT14 En-De. Five curves are plotted: Baseline (blue), LayerNorm (orange), RMSNorm (green), pRMSNorm (red), and WeightNorm (purple). The y-axis is "Valid BLEU score" (≈5–25), and the x-axis is "Training steps (×30k)" from 0 to 50. All methods start near 5–10 BLEU and rise sharply within the first ~10 steps before plateauing in the 21–23 range.

**Key Takeaway:** WeightNorm converges noticeably slower and converges to a lower final BLEU than LayerNorm, RMSNorm, and pRMSNorm, demonstrating that the proposed reparameterized RMS-based variants match LayerNorm's translation quality while (as argued earlier) being more efficient. (96 words)

**Caption (verbatim):**
Figure 7: SacreBLEU score curve over training steps on newstest2013 (devset) for the RNNSearch. Models are trained with *Nematatus* in Theano.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
a_i = \sum_{j=1}^m{w_{ij} x_j},\quad y_i = f\left(a_i + b_i\right),
$$

$$
\bar{a}_i = \frac{a_i - \mu}{\sigma} g_i, \quad y_i = f\left(\bar{a}_i + b_i\right),
$$

$$
\mu = \frac{1}{n}\sum_{i=1}^{n} a_i, \quad \sigma = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(a_i - \mu)^2}.
$$

$$
\mathbf{y} = f\left(\frac{\mathbf{Wx}}{\text{RMS}(\mathbf{a})} \odot \mathbf{g} + \mathbf{b}\right),
$$

$$
\text{RMS}(\alpha\mathbf{x}) = \alpha \text{RMS}(\mathbf{x}),
$$

$$
\small \begin{split} \mathbf{y}^\prime = f\left(\frac{\mathbf{W^{\prime}x}}{\text{RMS}(\mathbf{a}^\prime)} \odot \mathbf{g} + \mathbf{b}\right) = f\left(\frac{\delta\mathbf{Wx}}{\delta\text{RMS}(\mathbf{a})} \odot \mathbf{g} + \mathbf{b}\right) = \mathbf{y}. \end{split}
$$

$$
\small \begin{split} \mathbf{R}^\prime & = \frac{1}{{\delta \text{RMS}(\mathbf{a})}} \left(\mathbf{I}-\frac{\left(\mathbf{\delta Wx}\right)\left(\mathbf{\delta Wx}\right)^T}{n\delta^2 \text{RMS}(\mathbf{a})^2}\right) = \frac{1}{\delta}\mathbf{R}. \\ \end{split}
$$

$$
\begin{split} & \bar{a}_i = \frac{a_i}{\text{RMS}(\mathbf{a})} g_i, \quad \text{where}~~ \text{RMS}(\mathbf{a}) = \sqrt{\frac{1}{n} \sum_{i=1}^{n} a_i^2}. \end{split}
$$

$$
\small & \frac{\partial \mathcal{L}}{\partial \mathbf{b}} = \frac{\partial \mathcal{L}}{\partial \mathbf{v}}, \quad \frac{\partial \mathcal{L}}{\partial \mathbf{g}} = \frac{\partial \mathcal{L}}{\partial \mathbf{v}} \odot \frac{\mathbf{Wx}}{\text{RMS}(\mathbf{a})},
$$

$$
\small \begin{split} & \frac{\partial \mathcal{L}}{\partial \mathbf{W}} = \sum_{i=1}^n \left[\mathbf{x}^T \otimes \left(\text{diag}\left(\mathbf{g} \odot \frac{\partial \mathcal{L}}{\partial \mathbf{v}} \right) \times \mathbf{R}\right)\right]_{i}, \text{where}~~ \mathbf{R} = \frac{1}{{\text{RMS}(\mathbf{a})}} \left(\mathbf{I}-\frac{\left(\mathbf{Wx}\right)\left(\mathbf{Wx}\right)^T}{n\text{RMS}(\mathbf{a})^2}\right), \end{split}
$$

## 技术点深读（DEEP）

![[deep/root-mean-square-layer-normalization]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/root-mean-square-layer-normalization.txt`（46403 字符）供引用检索。