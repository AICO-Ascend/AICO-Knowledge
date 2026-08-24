---
paper_num: "65"
title: "Attention Residuals"
authors: ""
date: "2026/3/16"
arxiv: "https://arxiv.org/abs/2603.15031"
pdf: "papers/attention-residuals.pdf"
slug: "attention-residuals"
tags: []
---

# Attention Residuals

> [!abstract] 摘要（原文）
> Residual connections with PreNorm are standard in modern LLMs, yet they accumulate all layer outputs with fixed unit weights. This uniform aggregation causes uncontrolled hidden-state growth with depth, progressively diluting each layer's contribution. We propose Attention Residuals (AttnRes), which replaces this fixed accumulation with softmax attention over preceding layer outputs, allowing each layer to selectively aggregate earlier representations with learned, input-dependent weights. To address the memory and communication overhead of attending over all preceding layer outputs for large-scale model training, we introduce Block AttnRes, which partitions layers into blocks and attends over block-level representations, reducing the memory footprint while preserving most of the gains of full AttnRes. Combined with cache-based pipeline communication and a two-phase computation strategy, Block AttnRes becomes a practical drop-in replacement for standard residual connections with minimal overhead. Scaling law experiments confirm that the improvement is consistent across model sizes, and ablations validate the benefit of content-dependent depth-wise selection. We further integrate AttnRes into the Kimi Linear architecture (48B total / 3B activated parameters) and pre-train on 1.4T tokens, where AttnRes mitigates PreNorm dilution, yielding more uniform output magnitudes and gradient distribution across depth, and improves downstream performance across all evaluated tasks.

## 元信息
- **发表日期**: 2026/3/16
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2603.15031
- **本地 PDF**: `papers/attention-residuals.pdf`
- **页数**: 21

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/attention-residuals-fig01.png]]
*整页渲染: ![[assets/attention-residuals-p01.png]]*
> [!quote] caption
> Overview of Attention Residuals. (a) Standard Residuals: standard residual connections with uniform additive accumulation. (b) Full AttnRes: each layer selectively aggregates all previous layer outputs via learned attention weights. (c) Block AttnRes: layers are grouped into blocks, reducing memory from O(Ld) to O(Nd).[cs.CL] 16 Mar 2026

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示三种残差架构：(a)标准残差对Attention+MoE层均匀⊕累加；(b)Full AttnRes每层引入Q/K/V矩阵与α权重，选择性聚合全部前层L个输出；(c)Block AttnRes将层分组为N块，将每token内存由O(Ld)降至O(Nd)。该图论证：标准残差"一刀切"聚合存在局限，注意力残差以学到的α权重实现层间选择性信息路由，Block变体以分组粒度换取内存效率；为后续Table 1各方案内存访问成本对比与附录两阶段推理调度建立方法基础框架。

### Figure 2 (p.5)
![[assets/attention-residuals-p05.png]]
> [!quote] caption
> PyTorch-style pseudo code for Block Attention Residuals. block_attn_res computes softmax attention over block representations using a learned pseudo-query wl; forward is a single-layer pass that maintains partial_block (bi n, intra-block residual) and blocks ([b0, . . . , bn−1], inter-block history).

### Figure 3 (p.6) ⭐深度解读
![[assets/crops/attention-residuals-fig03.png]]
*整页渲染: ![[assets/attention-residuals-p06.png]]*
> [!quote] caption
> Cache-based pipeline communication example with 4 physical ranks and 2 virtual stages per rank, where hatched boxes denote end of AttnRes blocks. Numbers indicate micro-batch indices. Each rank caches previously received blocks; stage transitions only transmit incremental blocks (+[b1, b2]) instead of the full history. naïve implementation. During inference, repeated access to accumulated block re

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图3深度解读（≤220字）**

**核心对象与结构**：图示4物理Rank×2虚拟Stage的流水线通信布局。每Rank缓存已收块（`[b₀]`、`[b₀,b₁]`），阶段切换仅传增量块（`+[b₁,b₂]`、`+[b₂,b₃]`），斜纹框标记AttnRes块终点缓存位。

**论证的关键结论**：AttnRes通过缓存机制将跨阶段通信量从"全量历史重传"压缩为"增量块传输"，Rank 0→Rank 3每个Stage仅传递1–2个新增块，而非所有累积块，显著降低推理时流水线并行的通信开销。

**论文整体链路作用**：该图是AttnRes系统效率层面的核心可视化证据，与Table 3（AttnRes vs baseline性能对比）相互印证，共同支撑"块级残差缓存+增量通信=高效流水线推理"的方法论闭环，为后文分布式部署分析提供通信模型基础。

### Figure 4 (p.9) ⭐深度解读
![[assets/crops/attention-residuals-fig04.png]]
*整页渲染: ![[assets/attention-residuals-p09.png]]*
> [!quote] caption
> Scaling law curves for Attention Residuals. Both Full and Block AttnRes consistently outperform the baseline across all scales. Block AttnRes closely tracks Full AttnRes, recovering most of the gain at the largest scale. PFLOP/s-days, Block AttnRes reaches 1.692 versus the Baseline’s 1.714, equivalent to a 1.25× compute advantage.

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图以双对数尺度展示三种模型的缩放定律拟合曲线：Baseline（蓝, 1.891×C⁻⁰·⁰⁵⁷）、Full AttnRes（红, 1.865×C⁻⁰·⁰⁵⁷）、Block AttnRes（橙, 1.870×C⁻⁰·⁰⁵⁸），x轴PFLOP/s-days 0.5–5+，y轴Loss≈1.7–1.95。两条AttnRes曲线全程低于Baseline，且衰减指数几乎一致（-0.057 vs -0.058），说明增益贯穿全尺度。图标注Loss≈1.8处Block AttnRes相对Baseline节省1.25×算力（同算力下Block达1.692 vs Baseline 1.714）。

作为方法核心主实验，该图定量证明AttnRes在任意规模均稳定有效，且Block变体以更低开销逼近Full收益，与表4消融共同支撑"残差路径改造普遍有效"这一论文核心结论。

### Figure 5 (p.10) ⭐深度解读
![[assets/crops/attention-residuals-fig05.png]]
*整页渲染: ![[assets/attention-residuals-p10.png]]*
> [!quote] caption
> Training dynamics of Baseline and Block AttnRes. (a) Validation loss during training. (b) Each transformer block’s output magnitude at the end of training. (c) Each transformer block’s gradient magnitude.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**(a) 验证损失**：Baseline（蓝）与 Block AttnRes（红）起始均约 1.47，训练全程走势一致，但 Block AttnRes 在 ~80k 步后加速下降，最终约 1.15，低于 Baseline 的 ~1.18，验证其优化更充分。

**(b) 块输出幅度**（0–27 层）：Baseline 在前 20 层维持在 ~1，但第 20 层后陡升至 ~12，呈末端激活爆炸；Block AttnRes 全程平稳在 0–2 区间，证明其有效抑制了深层信号膨胀。

**(c) 梯度幅度**（×10⁻⁵）：Baseline 梯度在第 0 层达 ~2.5 后单调衰减至近 0，呈现典型的梯度消失；Block AttnRes 全程维持在 0.1–0.7，分布显著更均衡。

**论证作用**：该图从"损失更低、激活更稳、梯度更匀"三方面，为 Block AttnRes 改善信号传播的理论主张提供直接经验证据；与 Table 5 中多种残差机制的横向梳理互补，构成论文方法验证链中的关键实证支撑。

### Figure 6 (p.11) ⭐深度解读
![[assets/crops/attention-residuals-fig06.png]]
*整页渲染: ![[assets/attention-residuals-p11.png]]*
> [!quote] caption
> Effect of block size on validation loss (16-layer model). • Language understanding and reasoning: MMLU [13], MMLU-Pro Hard [55], GPQA-Diamond [41], BBH [48], ARC-Challenge [6], HellaSwag [65], and TriviaQA [21]. • Reasoning (Code and Math): GSM8K [7], MGSM [44], Math [25], CMath [14], HumanEval [5], and MBPP [1]. • Chinese language understanding: CMMLU [26] and C-Eval [19].

> [!tip] 技术解读（多模态）
> 【图文联合解读】**Figure 6 图文联合解读**

**核心对象与数据**：横轴为块大小 S∈{32,16,8,4,2}，纵轴为16层模型验证损失。红色实线 Block AttnRes 在五个 S 下的取值依次为 1.757、1.753、1.748、1.746、1.746；两条参考线：Baseline（灰虚线，1.766）与 Full AttnRes（红虚线，S=1，1.737）。

**技术结论**：块越小损失越低，S=32→4 单调下降共 0.011；在 S=4 处已收敛至 1.746，与 S=2 完全持平，说明进一步细化块无收益。Block AttnRes 即使在 S=32（1.757）也优于 Baseline（1.766），但始终未追平 Full AttnRes，最优差距约 0.009。

**论文作用**：作为 Table 4 消融的延伸，量化"块大小"这一实用超参的效率–性能权衡——S=4 即可获得 Full AttnRes 近 95% 的增益（1.746 vs 1.737），为部署中的块粗化选择提供实证依据。

### Figure 7 (p.12) ⭐深度解读
![[assets/crops/attention-residuals-fig07.png]]
*整页渲染: ![[assets/attention-residuals-p12.png]]*
> [!quote] caption
> Architecture sweep under fixed compute (≈6.5 × 1019 FLOPs, ≈2.3 × 108 active parameters). Each cell reports validation loss for a (dmodel/Lb, H/Lb) configuration, where Lb = L/2 is the number of Transformer blocks; the star marks the optimum.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图7 联合解读**

图7呈现固定算力（≈6.5×10¹⁹ FLOPs、≈2.3×10⁸活跃参数）下，5×5的(d_model/L_b, H/L_b)架构网格验证损失热力图，分Baseline(a)与Attention Residuals(b)两组。Baseline最优在(60, 0.3)处，损失1.847；Attention Residuals最优在(45, 0.3)处，损失1.802，全网格均更优（最高值1.954→更低）。

论证结论：(1) 算力固定时，注意力残差相对Baseline普遍带来约0.03–0.05的损失下降；(2) 最优共同落于H/L_b=0.3，但AR所需d_model/L_b更小（45<60），说明残差机制提升了参数利用率；(3) 该图在论文中作为架构无关性证据，与主实验互补，支撑"残差设计独立带来增益"的核心论点，并为后续缩放实验的超参选择提供依据。

### Figure 8 (p.13) ⭐深度解读
![[assets/crops/attention-residuals-fig08.png]]
*整页渲染: ![[assets/attention-residuals-p13.png]]*
> [!quote] caption
> Depth-wise attention weight distributions for a 16-head model with full (top) and block (bottom) Attention Residuals, averaged over tokens. The model has 16 attention and 16 MLP layers. Each row shows how the lth attention (left) or MLP (right) layer distributes weight over previous sources. Diagonal dominance indicates locality remains the primary information pathway, while persistent weights on 

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

图8为16层16头模型的逐层注意力权重热力图。上排（Full AttnRes）源空间为32×16、含斜纹屏蔽区，每层权重几乎全集中于最近邻的±1–2行，对角支配明显；下排（Block AttnRes）源压缩为8块索引，呈现清晰的块对角块状结构（块内权重≈0.8–0.9），仅末层向下一块轻微溢出。

作者借此论证：两种 Attention Residuals 均保持强对角/块对角主导，说明**局部路径仍是主通道**，远距离权重稀疏可控且无广泛弥散，从而验证"块级近似即可逼近全连接残差"的假设。

该图为论文方法链中的**经验证据支撑**：从微观权重分布角度解释为何 Block AttnRes 在几乎不损失建模能力的前提下，可大幅压缩通信开销，连接理论分析与后续实验结论。

### Figure 9 (p.15) ⭐深度解读
![[assets/crops/attention-residuals-fig09.png]]
*整页渲染: ![[assets/attention-residuals-p15.png]]*
> [!quote] caption
> Depth mixing matrices M for four residual variants (L=4; Block AttnRes uses block size S=2). Highway is shown with scalar gates for clarity. AttnRes panels show unnormalized ϕ scores; background colors group entries that share the same source (Full AttnRes) or the same source block (Block AttnRes). • Standard residual [12], hl = hl−1 + fl−1(hl−1). Expanding gives hl = Pl−1 i=0 vi, so Mi→l = 1 for 

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心对象**：L=4 的四种残差变体的深度混合矩阵 M。Highway 用标量门（γ、g），(m)HC 用 β⊤Aα 形式的矩阵-向量乘积；Full AttnRes 显示 φ(wₗ, kᵢ) 未归一化打分，按来源节点用蓝/橙/紫/绿背景分组；Block AttnRes(S=2) 将 4 层分两个源块，块内用 φ(w, k₁+k₂) 聚合。

2) **关键结论**：统一视角下，M 的每行表示层 l 对早期各层输出的混合权重；标准残差对应全 1 等权混合，Highway/(m)HC 引入标量或低秩门控，而 AttnRes 用基于当前 token 查询 (w) 与历史键 (k) 的 φ 分数实现**输入依赖、源感知**的深度路由，且 Block 版本在保证表达力的同时显著降低复杂度。

3) **论文作用**：作为方法论桥梁，将 AttnRes 纳入"深度混合矩阵"统一框架，与 Highway、mHC 对照，直观论证其作为**通用残差推广**的合理性与计算效率优势，为后续实验提供理论支撑。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.8) ⭐深度解读
![[assets/crops/attention-residuals-tab01.png]]
> [!quote] caption
> Memory access cost per token per layer incurred by the residual mechanism under each scheme.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表量化比较Standard Residuals、mHC（m流）、AttnRes（Full/Block）四种方案每token每层的访存成本，含Read/Write/Symbolic/Typical列。典型配置（L=128, m=4, S=16）下：Standard=3d，mHC总I/O=34d，AttnRes Full=(S+N)d≈24d，Block=(N/S+5)d≈5.5d。关键结论：Block方案以约5.5d远低于Full的24d，验证图1(c)中"分组将访存从O(Ld)降至O(Nd)"的设计主张；其成本接近Standard，证明注意力残差在分块策略下具备实用可行性，支撑论文"以注意力残差替代均匀累加"的方法论，并成为后续实验对比内存开销的基准依据。

### Table 2 (p.9) ⭐深度解读
![[assets/crops/attention-residuals-tab02.png]]
> [!quote] caption
> Baseline vs Block AttnRes (N=8) vs Full AttnRes vs mHC(-lite): Model configurations, Hyperparameters, and Validation Loss.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心对象与结构**：表对比5档MoE规模（194M–528M激活参数、38.7B–119.0B tokens、L_b=H=12–17、d_model 896–1264、d_ff 400–560、lr≈2×10⁻³、batch 192–432）下Baseline、Block AttnRes(N=8)、Full AttnRes与mHC(-lite)的验证损失。

2) **关键结论**：Full AttnRes在4/5档（194M/296M/436M/528M：1.899/1.804/1.737/1.692，均加粗）取最低损失，mHC(-lite)仅在241M以1.869险胜；Block AttnRes稳定优于Baseline但弱于Full——证明学得的块间注意力残差在多尺度下稳定优于静态标量混合与启发式mHC方案。

3) **论文作用**：作为核心实验表，跨规模量化论证AttnRes相对基线与前沿mHC的一致增益，为"以注意力替代标量残差混合"这一核心主张提供实证支撑。

### Table 3 (p.10) ⭐深度解读
![[assets/crops/attention-residuals-tab03.png]]
> [!quote] caption
> Performance comparison of AttnRes with the baseline, both after the same pre-training recipe. Best per-row results are bolded .

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 3 在相同预训练前提下对比 Baseline 与 AttnRes 在 15 个基准上的表现，分三组：General 7 项（MMLU 73.5→74.6、GPQA-Diamond 36.9→44.4、BBH 76.3→78.0 等）、Math & Code 6 项（HumanEval 59.1→62.2、Math 53.5→57.1、CMath 84.7→85.1 等）、Chinese 2 项（C-Eval 79.6→82.5、CMMLU 82.0→82.9）。AttnRes 在 14 项胜出，仅 MMLU-Pro 以 52.2 与 Baseline 打平（同行加粗）；最大增益出现在 GPQA-Diamond（+7.5）、Math（+3.6）、HumanEval（+3.1）、C-Eval（+2.9）等推理/代码/中文任务。

论证结论：在排除训练差异后，注意力残差结构本身为模型带来跨领域稳定提升，且通信优化未折损质量。

作用：与 Table 1/2 的系统效率数据互补，与 Figure 3 的缓存通信机制呼应，共同支撑 AttnRes"既快又好"的核心主张。

### Table 4 (p.11) ⭐深度解读
![[assets/crops/attention-residuals-tab04.png]]
> [!quote] caption
> Ablation on key components of AttnRes (16-layer model).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**联合解读**

表4对16层AttnRes做组件消融：Baseline为1.766，DenseFormer/mHC为1.767/1.747；Full AttnRes取1.737，"输入相关查询"进一步降至1.731，证实其为关键机制；Block(S=4)得1.746，回收Full近95%增益；而SWA仅1.764、input-independent mixing升至1.749，区分于既有稀疏/静态混合方法。该表衔接Fig 4缩放实验，以块粗化在小模型中验证可行性，为大模型Block AttnRes提供超参依据，支撑论文"机制有效+部署友好"双重论证。

### Table 5 (p.14) ⭐深度解读
![[assets/crops/attention-residuals-tab05.png]]
> [!quote] caption
> Comparison of residual update mechanisms. Weight : whether the mixing coefficients are architecture-fixed, learned-static (fixed after training), or input-dependent (dynamic). Source : which earlier representations layer l can access. Normalization is omitted from most formulas for clarity.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表按"单态/多态/跨层"三组横向对比14种残差更新机制，纵列展示更新公式、权重类型(固定/静态/动态)与信息源范围。AttnRes以φ(q,k)做动态注意力加权，Full版源覆盖全部早层h₁…h_{l-1}，Block版将其限定为块级[b₀,…,b_nʲ]——是表中唯一兼具"动态权重+全源跨层访问"的方法。

论文借此将AttnRes定位于残差机制谱系中"动态权重×全源跨层"的交汇点，凸显其相对Residual/ReZero(单源固定/静态)等方法在表达能力上的差异化优势。

在论文论证链中，Table 5提供理论坐标系，与Figure 5的损失/激活/梯度经验证据互补，共同支撑Block AttnRes改善信号传播的核心主张。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\bm{h}_{l} = \brickred{\alpha_{0 \to l}} \cdot \bm{h}_1 + \sum_{i=1}^{l-1} \brickred{\alpha_{i \to l}} \cdot f_i(\bm{h}_{i})
$$

$$
\brickred{\alpha_{i \to l}} = \frac{\phi\left(\bm{q}_{l}, \bm{k}_{i}\right)}{\sum_{j=0}^{l-1} \phi\left(\bm{q}_{l}, \bm{k}_{j}\right)}
$$

$$
\bm{q}_{l} = \bm{w}_{l}, \quad \quad \bm{k}_{i} = \bm{v}_{i} = \begin{cases} \bm{h}_1 & i = 0 \\ f_i(\bm{h}_{i}) & 1 \leq i \leq l-1 \end{cases}
$$

$$
\bm{h}_{l} = \sum_{i=0}^{l-1} \brickred{\alpha_{i \to l}} \cdot \bm{v}_{i}
$$

$$
\bm{b}_n = \sum_{j \in \mathcal{B}_n} f_j(\bm{h}_j)
$$

$$
\mathbf{V} = \begin{cases} [\bm{b}_0, \bm{b}_1, \ldots, \bm{b}_{n-1}]^\top & \text{if } i = 1 \text{ (first layer of block } n\text{)} \\ [\bm{b}_0, \bm{b}_1, \ldots, \bm{b}_{n-1}, \bm{b}_n^{i-1}]^\top & \text{if } i \geq 2 \text{ (subsequent layers)} \\ \end{cases}
$$

$$
\mathrm{Comm}_{\text{na\"ive}} = \sum_{j=1}^{C-1} jN_p \cdot d = \frac{C(C{-}1)}{2}\,N_p d.
$$

$$
\mathrm{Comm}_{\text{cached}} = \underbrace{\frac{P(P{-}1)}{2}\, N_p d}_{\text{first virtual stage}} + \underbrace{(V{-}1)\, P^2\, N_p d}_{\text{subsequent virtual stages}}.
$$

$$
\mathbf{W}_t = \mathbf{W}_{t-1} - \eta\,\nabla\ell(\mathbf{W}_{t-1};\, \bm{x}_t),
$$

$$
\mathbf{M}_{i \to l} = \bm{\beta}_{i}^\top \, \mathbf{A}_{i+1 \to l}^{\times} \, \bm{\alpha}_{l},
$$

$$
\mathrm{Read}_{\text{inter}}^{(n)} = 2(n-1)Sd,
$$

$$
\mathrm{Read}_{\text{inter}} = \sum_{n=1}^{N} 2(n-1)Sd = 2Sd \cdot \frac{N(N-1)}{2} = dL(N-1).
$$

$$
\mathrm{Write}_{\text{inter}} = Ld
$$

$$
\mathrm{Read}_{\text{intra}}^{(n)} = \sum_{t=1}^{S} 2(t-1)d = S(S-1)d.
$$

$$
\mathrm{Read}_{\text{total}} = dL(N-1) + N \cdot S(S-1)d, \qquad \mathrm{Write}_{\text{total}} = 2Ld.
$$

$$
\text{Read per layer} = (N-1)d + (S-1)d = (S + N - 2)d, \qquad \text{Write per layer} = 2d,
$$

$$
\boxed{\;\text{Total I/O per layer} = (S + N)\,d.\;}
$$

$$
\begin{bmatrix} \bm{h}_1 \\ \bm{h}_2 \\ \vdots \\ \bm{h}_L \end{bmatrix} = \begin{bmatrix} 1 & & & \\ 1 & 1 & & \\ \vdots & \vdots & \ddots & \\ 1 & 1 & \cdots & 1 \end{bmatrix} \begin{bmatrix} \bm{v}_0 \\ \bm{v}_1 \\ \vdots \\ \bm{v}_{L-1} \end{bmatrix}
$$

$$
\mathbf{H}_{l} = \mathbf{H}_{l-1} \mathbf{A}_{l} + f_{l-1}(\mathbf{H}_{l-1} \bm{\alpha}_{l-1})\, \bm{\beta}_{l-1}^\top,
$$

## 技术点深读（DEEP）

![[deep/attention-residuals]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/attention-residuals.txt`（73664 字符）供引用检索。