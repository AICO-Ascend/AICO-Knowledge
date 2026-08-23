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
![[assets/crops/root-mean-square-layer-normalization-fig01.png]]
*整页渲染: ![[assets/root-mean-square-layer-normalization-p01.png]]*
> [!quote] caption
> One major feature of LayerNorm that is widely regarded as contributions to the stabilization is its re-centering invariance property: the summed inputs after LayerNorm remain intact when the inputs or weight matrix is shifted by some amount of noise. We argue that this mean normalization does not reduce the variance of hidden states or model gradients, and hypothesize that it has little impact on 

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

The figure consists of two side-by-side line plots comparing training dynamics of two model variants: a "Baseline" (blue) and "LayerNorm" (orange).

- **Plot (a):** Loss vs. Training Step (×100), x-axis 0–100, y-axis ~4–10. At step ~30 (×100), the Baseline reaches loss 7.0 while LayerNorm reaches 5.4.
- **Plot (b):** Loss vs. Training Time (minutes), x-axis 0–160, y-axis ~4–10. At ~35–40 min, the Baseline is at 7.0 while LayerNorm is at 5.9.

Both curves share the same legend style; dashed vertical guide lines mark the annotated comparison points, and red dots highlight the specific loss values.

**Key technical takeaway:** Applying LayerNorm yields a substantially lower training loss than the Baseline at both the same number of steps and the same wall-clock time, indicating faster convergence per step and improved per-minute throughput.

**Caption (verbatim):**

(a) Training loss vs. training steps. (b) Training loss vs. training time.

### Figure 2 (p.6) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-fig02.png]]
*整页渲染: ![[assets/root-mean-square-layer-normalization-p06.png]]*
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
![[assets/crops/root-mean-square-layer-normalization-fig03.png]]
*整页渲染: ![[assets/root-mean-square-layer-normalization-p07.png]]*
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
![[assets/crops/root-mean-square-layer-normalization-fig04.png]]
*整页渲染: ![[assets/root-mean-square-layer-normalization-p07.png]]*
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
![[assets/crops/root-mean-square-layer-normalization-fig05.png]]
*整页渲染: ![[assets/root-mean-square-layer-normalization-p08.png]]*
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
![[assets/crops/root-mean-square-layer-normalization-fig06.png]]
*整页渲染: ![[assets/root-mean-square-layer-normalization-p08.png]]*
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
![[assets/crops/root-mean-square-layer-normalization-fig07.png]]
*整页渲染: ![[assets/root-mean-square-layer-normalization-p13.png]]*
> [!quote] caption
> SacreBLEU score curve over train- ing steps on newstest2013 (devset) for the RNNSearch. Models are trained with Nema- tus in Theano.

> [!tip] 技术解读（多模态）
> **Figure 7 Description:**

The figure is a line chart comparing five normalization methods' training dynamics for RNNSearch on WMT14 En-De. Five curves are plotted: Baseline (blue), LayerNorm (orange), RMSNorm (green), pRMSNorm (red), and WeightNorm (purple). The y-axis is "Valid BLEU score" (≈5–25), and the x-axis is "Training steps (×30k)" from 0 to 50. All methods start near 5–10 BLEU and rise sharply within the first ~10 steps before plateauing in the 21–23 range.

**Key Takeaway:** WeightNorm converges noticeably slower and converges to a lower final BLEU than LayerNorm, RMSNorm, and pRMSNorm, demonstrating that the proposed reparameterized RMS-based variants match LayerNorm's translation quality while (as argued earlier) being more efficient. (96 words)

**Caption (verbatim):**
Figure 7: SacreBLEU score curve over training steps on newstest2013 (devset) for the RNNSearch. Models are trained with *Nematatus* in Theano.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.4) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-tab01.png]]
> [!quote] caption
> Invariance properties of different normalization methods. “  ” indicates invariant, while “  ” denotes the opposite.

> [!tip] 表格解读（多模态）
> **Note:** The snippet you provided contains the caption for **Table 1**, not a figure with architecture/data flow. Furthermore, the actual table contents (rows/columns/method names) are not included in the text you shared — only the caption and surrounding paragraph. Below I describe what can be inferred from context, and I transcribe the caption verbatim.

---

**Description / Key technical takeaway (~80 words):**
Table 1 compares the invariance properties of competing normalization methods (e.g., BatchNorm, LayerNorm, InstanceNorm, GroupNorm) against RMSNorm across several transformation axes — re-scaling and re-centering of weight vectors, and re-scaling/re-centering of the dataset. Each cell uses ✓ to denote invariance and ✗ to denote lack thereof. **Key takeaway:** RMSNorm preserves the weight- and dataset-rescaling invariances of LayerNorm while dropping the mean-subtraction (re-centering) step, showing that the mean-removal in LayerNorm is *not* essential to its effectiveness and that computing only the root-mean-square is sufficient.

**Caption (transcribed verbatim):**
> Table 1: Invariance properties of different normalization methods. "✓" indicates invariant, while "✗" denotes the opposite.

### Table 2 (p.6) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-tab02.png]]
> [!quote] caption
> SacreBLEU score on newstest2014 (Test14) and newstest2017 (Test17) for RNNSearch using Tensorﬂow- version Nematus. “ Time ”: the time in second per 1k training steps. We set p to 6.25%. We highlight the best results in bold, and show the speedup of RMSNorm against Layer- Norm in bracket.

> [!tip] 表格解读（多模态）
> **Figure 2 Description:**

The figure is a line plot showing the **SacreBLEU score on newstest2013** for the RNNSearch model as a function of training progress. **Components/axes:**
- **X-axis:** Training steps (×30k), ranging from 0 to 50
- **Y-axis:** SacreBLEU score (the upper portion is cut off in the view)
- **Curves:** Multiple training trajectories are overlaid (a red curve and a blue curve are visible at the left edge, with a legend entry for **pRMSNorm** in purple/grey)
- **Context:** Models are implemented using Nematus [25] in Tensorflow, comparing normalization strategies (Baseline, LayerNorm, L2-Norm, pRMSNorm)

**Key technical takeaway:** pRMSNorm is evaluated as a drop-in normalization replacement within the encoder–decoder RNN, demonstrating stable training and competitive BLEU convergence on WMT-style MT benchmarks versus LayerNorm/L2-Norm variants.

**Caption (verbatim):**

> Figure 2: SacreBLEU score on newstest2013 for the RNNSearch. Models are implemented according to Nematus [25] in Tensorflow.

### Table 3 (p.6) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-tab03.png]]
> [!quote] caption
> further lists translation results of different models implemented in Theano and Pytorch. Overall, RMSNorm yields comparable translation quality compared with LayerNorm but incurs less computational overhead, outperforming LayerNorm with speedups ranging from 11% ∼ 34%. In addition, we observe that t

> [!tip] 表格解读（多模态）
> I don't have access to the actual figure image or its caption in the provided text — only the surrounding prose. Based on the text alone, I cannot accurately describe the figure's visual architecture (axes, curves, data points) or transcribe its caption verbatim.

What the text tells us about Figure 7:
- It illustrates the **effect of the partial ratio p** on model performance (for *p*RMSNorm).
- The x-axis is presumably **p** (partial ratio, e.g., 6.25%, other values).
- The y-axis is presumably **BLEU score** (translation quality on RNNSearch).
- It likely plots BLEU vs. p to show that BLEU is fairly stable across different p values.

**Key technical takeaway (from text):**
*"In RNNSearch, the scale of p has little influence on the final translation quality — using a small ratio does not significantly degenerate BLEU score, so we set p = 6.25% for all following experiments."*

This means **partial RMS estimation can be aggressive without hurting accuracy**, enabling meaningful compute savings.

**Caption (verbatim):** *Not present in the provided text excerpt.* The passage only references the figure ("Figure 7 shows the effect of p on model performance") without quoting a caption. If you can share the image or the caption text, I'll transcribe it exactly.

### Table 8 (p.8) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-tab08.png]]
> [!quote] caption
> Time in seconds per 0.1k training steps for the order-embedding model.

> [!tip] 表格解读（多模态）
> There is no figure (image or diagram) present in the input you provided — only text content from what appears to be a research paper, including discussion of Tables 7 and 8 (referenced in the text but not shown) and a "6.4 CIFAR-10 Classification" section. Because no figure is visible, I cannot describe its architecture, components, data flow, or transcribe its caption.

For completeness, here is the text content that **is** present, transcribed verbatim:

---

"the validation set, RMSNorm slightly exceeds LayerNorm with respect to recall value. For the final test results as shown in Table 7, both RMSNorm and LayerNorm improve the model performance, reaching higher recall values (except LayerNorm on R@5) and lower mean rank, though RMSNorm reveals better generalization than LayerNorm. Besides, results in Table 8 show that RMSNorm accelerates training speed by 40%~64% compared with LayerNorm, highlighting better efficiency of *p*RMSNorm.

Table 8: Time in seconds per 0.1k training steps for the order-embedding model.

**6.4 CIFAR-10 Classification**

CIFAR-10 is a supervised image classification task, with 10 different classes. We train a modified version of the ConvPool-CNN-C architecture [15], and follow the same experimental protocol as Salimans and Kingma [22]. BatchNorm, LayerNorm, and WeightNorm are included for comparison. Training details are given in Appendix A.4."

---

If you intended to attach or share an actual figure, please re-upload it and I'll describe its architecture/components and transcribe its caption.

### Table 9 (p.9) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-tab09.png]]
> [!quote] caption
> Training error rate for the ConvPool- CNN-C model.

> [!tip] 表格解读（多模态）
> # Note: No Figure Available

The provided excerpt does **not contain a figure** — it contains text from Sections 7 (Conclusion and Future Work) and Acknowledgments of the RMSNorm paper, along with a **table caption** (Table 9). There is no accompanying architecture diagram, data-flow illustration, or component figure shown.

What I can transcribe verbatim from the visible content:

---

**Caption (verbatim):**

> Table 9: Training error rate for the ConvPool-CNN-C model.

---

**Surrounding table context (partial, cut off at top of excerpt):**

> "…epoch for the ConvPool-CNN-C model. Time is measured [with] GeForce RTX 2080 Ti."

---

If you intended to share a figure (e.g., the RMSNorm architecture diagram showing summed inputs → RMS computation → re-scaling with learnable gain), please re-upload or paste it, and I will provide the architecture/components/data-flow description plus a key technical takeaway. The main conceptual takeaway from the **text** is that **RMSNorm drops LayerNorm's mean-subtraction step while keeping the re-scaling invariance**, yielding 7%–64% empirical speedups as a drop-in LayerNorm replacement.

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