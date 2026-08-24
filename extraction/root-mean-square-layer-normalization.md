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
> 【图文联合解读】**图文联合解读：**

图(b)横轴为训练时间(0–160分钟)，纵轴为Loss(4–10)，展示GRU-RNNSearch前10k步的两条曲线：蓝色Baseline最终约6.0，橙色LayerNorm约4.5；在约35分钟同一训练步处，Baseline=7.0，LayerNorm=5.9，损失差1.1。

原文借此论证：LayerNorm带来的加速收敛主要来自**缩放不变性**而非均值中心化（re-centering invariance），因为均值归一化并不降低隐藏状态或梯度方差。作者据此提出RMSNorm仅保留缩放项即可达到相近甚至更优效果。

该图作为论文动机起点，连接Table 1的不变性分析，推动RMSNorm作为更轻量替代方案的提出与后续实验验证。

### Figure 2 (p.6) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-fig02.png]]
*整页渲染: ![[assets/root-mean-square-layer-normalization-p06.png]]*
> [!quote] caption
> SacreBLEU score on newstest2013 for the RNNSearch. Models are implemented accord- ing to Nematus [25] in Tensorﬂow.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**核心对象与结构**：Figure 2 为 RNNSearch 模型在 newstest2013 上的验证集 SacreBLEU 收敛曲线，横轴为训练步数（×30k，0–50），纵轴为 Valid BLEU（0–25），共五条曲线。L2-Norm（红）起步最低、收敛最慢，最终约 22；Baseline（蓝）起步约 15，收敛缓慢；LayerNorm（橙）、RMSNorm（绿）、pRMSNorm（紫）均在 ~5 步内快速攀升至 23–24 平台。

2）**关键结论**：RMSNorm/pRMSNorm 在保持与 LayerNorm 相当收敛速度的同时，达到最高的终端 BLEU，验证其在 NMT 任务中作为轻量归一化方案的有效性。

3）**论文作用**：作为支撑实验，与 Table 1 等 WMT 测试集结果互证，强化"RMSNorm = 可去均值重中心化的 LayerNorm"这一核心论点。

### Figure 3 (p.7) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-fig03.png]]
*整页渲染: ![[assets/root-mean-square-layer-normalization-p07.png]]*
> [!quote] caption
> SacreBLEU score on new- stest2013 (devset) for the RNNSearch with pRMSNorm. We use Tensorﬂow-version Ne- matus, and change p by a step size of 10%.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 3）：**

**1) 核心对象与数据：** 单线折线图，x 轴为 pRMSNorm 的标量超参数 p（%），在约 10%–100% 区间以 10% 步长扫参；y 轴为 RNNSearch（TF 版 Nematus）在 newstest2013 验证集上的 SacreBLEU，刻度 22–25。

**2) 关键结论：** 蓝色曲线整体近似水平，全 p 区间 BLEU 集中在 23.9–24.1 之间，最大波幅约 0.5 分，仅在 p≈90% 处出现一次浅凹（≈23.6），其余波动 ≤0.1 分。这直接说明 pRMSNorm 对 p 取值**极不敏感**，基本"免调参"。

**3) 在论文中的作用：** 作为超参数鲁棒性消融，与正文中 RMSNorm 与 LayerNorm 的精度/速度对比互为补充，支撑核心主张——pRMSNorm 是一种**即插即用、性能无损、对超参宽容**的轻量化归一化替代方案。

### Figure 4 (p.7) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-fig04.png]]
*整页渲染: ![[assets/root-mean-square-layer-normalization-p07.png]]*
> [!quote] caption
> SacreBLEU score curve of Layer-

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**核心对象与数据：** 图示newstest2013验证集上SacreBLEU随训练步数（0–30×30k）的变化曲线。对比两条曲线——LayerNorm（蓝）从约1缓慢爬升至约4，几乎持平；RMSNorm（橙）从约4稳步上升至约16，全程领先且差距持续扩大。

**关键论证结论：** 当初始化中心为0.2（非零偏移）时，RMSNorm显著优于LayerNorm。这是因为RMSNorm去掉了LayerNorm中的re-centering（均值中心化）步骤，不强制将输入拉回零均值，因此对初始化偏移具有更强的鲁棒性，避免了训练塌陷。

**在论文中的作用：** 该图作为"初始化敏感性"实验的关键证据，与Figure 2/3共同支撑论文核心主张——RMSNorm在保留re-scaling的同时简化re-centering，不仅计算更高效，还在非标准初始化下保持稳定性能，是LayerNorm的可行替代方案。

### Figure 5 (p.8) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-fig05.png]]
*整页渲染: ![[assets/root-mean-square-layer-normalization-p08.png]]*
> [!quote] caption
> Error rate on validation set for the attentive reader model.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图5展示了Attentive Reader模型上六种归一化方法的验证错误率收敛曲线（约300k训练步）：Baseline（蓝）收敛缓慢，300k步后错误率仍约0.48；BatchNorm-LSTM（绿）较慢；LayerNorm（红）、BatchNorm-Everywhere（橙）、RMSNorm（紫）、pRMSNorm（棕）在约50k步即收敛至≈0.5。结合表6，各方法每0.1k步耗时为：LayerNorm 392s、RMSNorm 333s（节省15.1%）、pRMSNorm 330s（节省15.8%）。

论文以此论证关键结论：**RMSNorm与LayerNorm收敛性能相当，但计算开销显著降低**——通过省略均值中心化、重计算缩放不变性，简化了归一化计算。该实验在整体方法链中起核心验证作用：证明RMSNorm在保持训练稳定性的同时，实现了效率与精度的最佳平衡，为后续在Transformer、机器翻译等大规模任务中的推广提供了实证依据。

### Figure 6 (p.8) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-fig06.png]]
*整页渲染: ![[assets/root-mean-square-layer-normalization-p08.png]]*
> [!quote] caption
> Recall@K values on validation set for the order-embedding models. worse than RMSNorm. Although in Figure 5 the performance of RMSNorm and LayerNorm is comparable, RMSNorm is around 15% faster than LayerNorm as shown in Table 6.3

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

Figure 6 以三幅子图（R@1、R@5、R@10）展示 Order-Embedding 模型在 COCO 跨模态检索任务中验证集 Recall@K 随训练步数（×0.3k，0–250）的演化。蓝色 Baseline 曲线在三项指标上均明显落后（R@1≈39 vs. 归一化组≈41；R@10≈87 vs. ≈89），收敛更慢且终值更低；RMSNorm（绿）与 pRMSNorm（红）自训练早期即领先 LayerNorm（橙），三者最终趋于相近，但 RMSNorm/pRMSNorm 峰值与稳定性略优。

原文借此论证：**在 OE 跨模态场景下，RMSNorm 收敛速度与最终性能均不逊于 LayerNorm，且远胜无归一化基线**，呼应 Figure 5 的"精度可比"与 Table 6 的"RMSNorm 比 LayerNorm 快约 15%"。

在论文整体实验链路中，该图与 §6.3 的 Image-Caption Retrieval 共同构成"质量—效率"双重证据链：既证明 RMSNorm 在跨模态检索中提供与 LayerNorm 同等收敛质量，又凸显其计算效率优势，从而支撑全文核心主张——RMSNorm 是 LayerNorm 的有效替代。

### Figure 7 (p.13) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-fig07.png]]
*整页渲染: ![[assets/root-mean-square-layer-normalization-p13.png]]*
> [!quote] caption
> SacreBLEU score curve over train- ing steps on newstest2013 (devset) for the RNNSearch. Models are trained with Nema- tus in Theano.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

图7对比RNNSearch在newstest2013上50×30k步内的SacreBLEU收敛曲线：Baseline（蓝）起点最低（~5 BLEU）且缓慢爬升至~22；LayerNorm（橙）起步即达~17，快速收敛至~23；RMSNorm（绿）、pRMSNorm（红）、WeightNorm（紫）均从~10–12起步，最终收敛于~22–23，性能与LayerNorm基本持平。

该图用于论证：**RMSNorm及其参数化版本pRMSNorm能达到与LayerNorm相当的翻译质量**，而无需计算均值与再平移，从而以更低的计算开销获得相近效果。这为论文核心主张——RMSNorm可作为LayerNorm的简洁替代——提供了在NMT任务上的直接实验支撑，是方法验证链路中的关键证据之一。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.6) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-tab02.png]]
> [!quote] caption
> SacreBLEU score on newstest2014 (Test14) and newstest2017 (Test17) for RNNSearch using Tensorﬂow- version Nematus. “ Time ”: the time in second per 1k training steps. We set p to 6.25%. We highlight the best results in bold, and show the speedup of RMSNorm against Layer- Norm in bracket.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 表格核心内容：**
Table 2对比五种RNNSearch模型在Test14/17的SacreBLEU与训练耗时（每1k步秒数）：Baseline (21.7/23.4, 399s)、LayerNorm (22.6/23.6, 665s)、L2-Norm (20.7/22.0, 482s)、RMSNorm (22.4/**23.7**, 501s)、pRMSNorm (**22.6**/23.1, 493s)；括号标注RMSNorm、pRMSNorm相对LayerNorm分别提速24.7%与25.9%。

**2) 关键论证结论：**
RMSNorm/pRMSNorm在Test17/14取得与LayerNorm相当甚至更优的BLEU（差距≤0.2），但训练时间减少约25%，证实RMSNorm以更少计算即可替代LayerNorm；L2-Norm质量最差，排除其作为替代方案。

**3) 在论文中的作用：**
与Figure 2（收敛曲线，证趋势）形成"质量+效率"互补证据链——曲线证明收敛行为可比，Table 2以量化数字坐实最终得分与加速比，共同支撑论文核心主张：RMSNorm是LayerNorm的轻量高效替代。

### Table 3 (p.7) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-tab03.png]]
> [!quote] caption
> SacreBLEU score on newstest2014 (Test14) and new- stest2017 (Test17) for RNNSearch. “ Th ”: Theano-version Nema- tus, “ Py ”: an in-house PyTorch-based RNNSearch.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1）表格核心对象与数据：** Table 3 对比 RNNSearch 在 Test14/Test17 上 Baseline 与 LayerNorm 两种配置的 SacreBLEU 表现，按列 1–4（四个分组条件）及 ALL（整体）给出均值 M 与标准差 S。Baseline 的 M 介于 −1.19 至 −2.60，S 高达 2.33–7.35；LayerNorm 的 M 收敛至 −0.43 至 −0.51，S 压缩至 1.19–1.51。

**2）关键技术结论：** 加入 LayerNorm 后，M 的绝对值从约 2 缩小至约 0.5，S 的最大值由 7.35 降至 1.51。数据定量证明层归一化显著降低跨条件/跨语对的方差，使训练结果更稳定、更可复现。

**3）在论文中的作用：** 作为引入 RMSNorm 的前导实验证据——先证"归一化对 RNN 翻译模型必要且有效"，再顺势提出更轻量的 RMSNorm 替代方案，形成"动机→替代→验证"的完整方法论证链。

### Table 8 (p.8) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-tab08.png]]
> [!quote] caption
> Time in seconds per 0.1k training steps for the order-embedding model.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表量化展示OE模型每0.1k步训练耗时：Baseline 2.11s、LayerNorm 12.02s、RMSNorm 7.12s（加速40.8%）、pRMSNorm 4.34s（加速63.9%）。原文据此论证RMSNorm较LayerNorm提速40%–64%，凸显*p*RMSNorm的效率优势。在论文链路中，该表与Table 7（精度指标）形成"精度-效率"互补双表：Table 7证RMSNorm泛化更优，Table 8证其训练开销更低；二者合力支撑"RMSNorm可在保持精度的同时显著提升效率、可作为LayerNorm高效替代"这一核心结论。

### Table 9 (p.9) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-tab09.png]]
> [!quote] caption
> Training error rate for the ConvPool- CNN-C model.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 9 图文联合解读**

**1) 核心对象与结构数据**
Table 9 以**训练误差曲线图**形式呈现 ConvPool-CNN-C 模型在 0–200 epoch 区间内的误差率（0–0.08）变化，共 6 条曲线：Baseline、BatchNorm、LayerNorm、WeightNorm、RMSNorm、pRMSNorm。量化观察：Baseline（蓝）收敛最慢，前 50 epoch 误差居高，200 epoch 时仍残留约 0.005；其余 5 种归一化方法在约 100 epoch 后误差趋近 0，其中 RMSNorm 与 pRMSNorm 曲线几乎与 LayerNorm 重合。

**2) 关键论证结论**
该曲线配合 Table 10（测试误差：RMSNorm 8.83% / pRMSNorm 10.37% vs LayerNorm 10.49%；单 epoch 时间：RMSNorm 31s（节省 20.5%）、pRMSNorm 30s（节省 23.1%）），共同论证：**RMSNorm 在训练收敛速度上与 LayerNorm 相当，但测试精度更高、计算开销显著更低**，证明其可作为 LayerNorm 的高效替代。

**3) 在论文链路中的作用**
该表位于实验章末，与 Table 7（跨模态检索 R@K）、Table 8（ImageNet）、Table 10 构成"训练动态 → 训练时间 → 测试性能"完整证据链，从**视觉收敛过程**维度直观支撑论文核心主张：RMSNorm 以更低成本获得等效甚至更优的归一化效果。

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