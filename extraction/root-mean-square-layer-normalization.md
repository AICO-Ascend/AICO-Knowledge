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

1) **核心对象与数据**：该图展示了基于 GRU 的 RNNSearch 模型在前 10k 训练步内 Baseline（无归一化，蓝线）与 LayerNorm（橙线）的训练损失曲线。子图(a)按训练步数（×100）绘制，在约 3000 步时 Baseline loss=7.0，LayerNorm loss=5.4，相差 1.6；子图(b)按训练时间（分钟）绘制，同等时长约 30 分钟时 Baseline=7.0，LayerNorm=5.9，相差 1.1。两条 LayerNorm 曲线全程显著低于 Baseline，且收敛更快、更平稳。

2) **论证的关键结论**：作者借此说明 LayerNorm 带来的训练稳定性提升主要来源于**缩放不变性（scale invariance）**而非重中心化（re-centering），从而为后续提出"可移除均值项、仅保留 RMS 缩放归一化"即 RMSNorm 提供实验铺垫。

3) **在论文中的作用**：作为支撑性预实验，与 Table 1 的 WMT 翻译结果互证，强化"RMSNorm ≈ 去均值 LayerNorm"的核心论点，构成从 LayerNorm → RMSNorm 简化论证链条的关键一环。

### Figure 2 (p.6) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-fig02.png]]
*整页渲染: ![[assets/root-mean-square-layer-normalization-p06.png]]*
> [!quote] caption
> SacreBLEU score on newstest2013 for the RNNSearch. Models are implemented accord- ing to Nematus [25] in Tensorﬂow.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图2展示RNNSearch在newstest2013上五条SacreBLEU收敛曲线（横轴0–50×30k步，纵轴0–25）：RMSNorm（绿）、pRMSNorm（紫）、LayerNorm（橙）约5步内快速升至23–24平台；Baseline（蓝）缓升至~22；L2-Norm（红）起步近0、收敛最慢。它论证了RMSNorm/pRMSNorm收敛速度与LayerNorm相当、显著快于基线、且BLEU持平或更优。该图为论文核心主张——"无trick的RMSNorm在训练效率与翻译质量上等价甚至优于LayerNorm"——提供收敛行为的可视化证据，铺垫后文Table 2在Test14/Test17上的最终质量与耗时对比，形成"收敛速度→最终质量→计算开销"的完整实验论证链。

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
> 【图文联合解读】图示6种归一化方法在attentive reader上的验证误差随训练步数（×1k, 最长≈300k）的收敛曲线：RMSNorm、pRMSNorm与LayerNorm均稳定收敛至约0.47，BatchNorm-LSTM约0.50，Baseline下降最慢且最终仅≈0.48。配套Table 6记录每0.1k步训练耗时——Baseline 315s、LayerNorm 392s、RMSNorm 333s（较LayerNorm快15.1%）、pRMSNorm 330s（快15.8%）。原文据此论证：RMSNorm与LayerNorm在收敛误差上相当，但训练速度领先约15%，以"精度持平、效率更优"的实证支撑全文核心结论，构成RMSNorm消融对比实验中关键的速度–精度权衡证据。

### Figure 6 (p.8) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-fig06.png]]
*整页渲染: ![[assets/root-mean-square-layer-normalization-p08.png]]*
> [!quote] caption
> Recall@K values on validation set for the order-embedding models. worse than RMSNorm. Although in Figure 5 the performance of RMSNorm and LayerNorm is comparable, RMSNorm is around 15% faster than LayerNorm as shown in Table 6.3

> [!tip] 技术解读（多模态）
> 【图文联合解读】图6比较Order-embedding模型在验证集上的Mean Recall@1/5/10，对比Baseline、LayerNorm、RMSNorm、pRMSNorm；每0.3k步取样，训练约0–75k步。Recall约由34/71/84升至40–41/76–77/88，三种归一化更早收敛，R@K整体优于Baseline，RMSNorm与LayerNorm相当。它承接图5的收敛结果及表6效率数据：RMSNorm性能不降，训练时间较LayerNorm快约15%，再由表7测试结果完成验证。

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
> 【图文联合解读】**Table 2 图文联合解读：**

1) **核心数据**：5行RNNSearch（Nematus）模型在Test14/17的SacreBLEU与每1k步训练耗时。Baseline（21.7/23.4，399s）< L2-Norm（20.7/22.0，482s，最差）；LayerNorm（22.6/23.6，665s）vs RMSNorm（22.4/**23.7**，501s，加速24.7%）vs pRMSNorm（**22.6**/23.1，493s，加速25.9%）。

2) **关键结论**：RMSNorm/pRMSNorm在BLEU上与LayerNorm持平或更优（Test17 23.7 vs 23.6），同时训练时间降低约25%，验证"去均值中心化+可学习缩放"既保持质量又显著提速；而L2-Norm无缩放参数则性能退化，证明缩放项不可缺。

3) **论文作用**：与Figure 2收敛曲线互证——前者证"质量不减"，本表证"效率增益"，共同构成RMSNorm替代LayerNorm的核心实证支撑，主导第三/四节的效率论证主线。

### Table 3 (p.7) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-tab03.png]]
> [!quote] caption
> SacreBLEU score on newstest2014 (Test14) and new- stest2017 (Test17) for RNNSearch. “ Th ”: Theano-version Nema- tus, “ Py ”: an in-house PyTorch-based RNNSearch.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表3 图文联合解读**：

① **核心数据**：表3报告RNNSearch在Test14与Test17（Theano/PyTorch两版Nematus）上不同归一化方案相对参考的Δ SacreBLEU，分列1–4及ALL均值。Baseline M=-2.60→ALL=-1.60（掉点严重）；LayerNorm M≈-0.50（恢复≈1 BLEU）；pRMSNorm行M≈-0.40至-0.74，整体表现略优于或持平LayerNorm。

② **论证结论**：pRMSNorm以极简的单一缩放因子完全替代LayerNorm，在两种框架、两个测试集上均不损失性能且略优，有力支持"RMSNorm即可，无需均值重中心化"的核心主张。

③ **论文作用**：与Figure 3（单数据集调p曲线）互补，是pRMSNorm在真实NMT场景、跨框架的稳健性验证实验，支撑其作为通用归一化模块的结论。

### Table 8 (p.8) ⭐深度解读
![[assets/crops/root-mean-square-layer-normalization-tab08.png]]
> [!quote] caption
> Time in seconds per 0.1k training steps for the order-embedding model.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表量化展示 order-embedding 模型在 COCO 跨模态检索任务中，每 0.1k 训练步的耗时：Baseline 2.11±0.047s、LayerNorm 12.02±0.191s、RMSNorm 7.12±0.207s（较 LayerNorm 省 40.8%）、pRMSNorm 4.34±0.168s（省 63.9%）。可见 LayerNorm 代价约为 Baseline 的 5.7 倍，而 RMSNorm 显著压缩该开销，pRMSNorm 更接近 Baseline 速度。

论文借此论证核心结论：**RMSNorm 在维持与 LayerNorm 相当甚至更优检索性能（Table 7、Figure 6）的同时，大幅降低训练时间成本**，pRMSNorm 进一步逼近无归一化基线效率。

在实验链路中，该表与 Figure 6（收敛曲线）、Table 7（R@K）共同构成"收敛行为→训练成本→测试精度"的完整证据链，**从计算开销维度**直观支撑 RMSNorm 以更低代价实现等效归一化的主张。

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