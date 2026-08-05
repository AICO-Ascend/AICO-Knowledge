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

### Figure 1 (p.1)
![[assets/root-mean-square-layer-normalization-p01.png]]
> [!quote] caption
> One major feature of LayerNorm that is widely regarded as contributions to the stabilization is its re-centering invariance property: the summed inputs after LayerNorm remain intact when the inputs or weight matrix is shifted by some amount of noise. We argue that this mean normalization does not reduce the variance of hidden states or model gradients, and hypothesize that it has little impact on 

### Figure 2 (p.6)
![[assets/root-mean-square-layer-normalization-p06.png]]
> [!quote] caption
> SacreBLEU score on newstest2013 for the RNNSearch. Models are implemented accord- ing to Nematus [25] in Tensorﬂow.

### Figure 3 (p.7)
![[assets/root-mean-square-layer-normalization-p07.png]]
> [!quote] caption
> SacreBLEU score on new- stest2013 (devset) for the RNNSearch with pRMSNorm. We use Tensorﬂow-version Ne- matus, and change p by a step size of 10%.

### Figure 4 (p.7)
![[assets/root-mean-square-layer-normalization-p07.png]]
> [!quote] caption
> SacreBLEU score curve of Layer-

### Figure 5 (p.8)
![[assets/root-mean-square-layer-normalization-p08.png]]
> [!quote] caption
> Error rate on validation set for the attentive reader model.

### Figure 6 (p.8)
![[assets/root-mean-square-layer-normalization-p08.png]]
> [!quote] caption
> Recall@K values on validation set for the order-embedding models. worse than RMSNorm. Although in Figure 5 the performance of RMSNorm and LayerNorm is comparable, RMSNorm is around 15% faster than LayerNorm as shown in Table 6.3

### Figure 7 (p.13)
![[assets/root-mean-square-layer-normalization-p13.png]]
> [!quote] caption
> SacreBLEU score curve over train- ing steps on newstest2013 (devset) for the RNNSearch. Models are trained with Nema- tus in Theano.

## 全文文本
全文已存 `extraction/fulltext/root-mean-square-layer-normalization.txt`（46403 字符）供引用检索。