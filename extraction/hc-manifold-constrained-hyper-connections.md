---
paper_num: "36"
title: "HC: Manifold-Constrained Hyper-Connections"
authors: "Zhenda Xie*†, Yixuan Wei*, Huanqi Cao*, Chenggang Zhao, Chengqi Deng, Jiashi Li, Damai Dai, Huazuo Gao, Jiang Chang, Kuai Yu, Liang Zhao, Shangyan Zhou, Zhean Xu, Zhengyan Zhang, Wangding Zeng, Shengding Hu, Yuqing Wang,"
date: "2026/1/5"
arxiv: "https://arxiv.org/abs/2512.24880"
pdf: "papers/hc-manifold-constrained-hyper-connections.pdf"
slug: "hc-manifold-constrained-hyper-connections"
tags: []
---

# HC: Manifold-Constrained Hyper-Connections

> [!abstract] 摘要（原文）
> 1\. 💡 针对Hyper-Connections (HC) 在扩展残差流宽度时面临的训练不稳定性和可扩展性受限问题，本文提出了Manifold-Constrained Hyper-Connections (mHC)。 2. 🛠️ mHC通过将HC的残差连接空间投影到由双随机矩阵构成的特定流形上，并结合如Sinkhorn-Knopp算法进行约束，从而恢复了恒等映射特性，同时通过基础设施优化（如内核融合和重计算）提升了效率。 3. 🚀 实验证明，mHC显著增强了大规模训练的稳定性，提供了实质性的性能提升和优越的可扩展性，且仅引入了微不足道的额外计算开销。

## 元信息
- **发表日期**: 2026/1/5
- **作者**: Zhenda Xie*†, Yixuan Wei*, Huanqi Cao*, Chenggang Zhao, Chengqi Deng, Jiashi Li, Damai Dai, Huazuo Gao, Jiang Chang, Kuai Yu, Liang Zhao, Shangyan Zhou, Zhean Xu, Zhengyan Zhang, Wangding Zeng, Shengding Hu, Yuqing Wang,
- **arXiv**: https://arxiv.org/abs/2512.24880
- **本地 PDF**: `papers/hc-manifold-constrained-hyper-connections.pdf`
- **页数**: 19

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-fig01.png]]
*整页渲染: ![[assets/hc-manifold-constrained-hyper-connections-p01.png]]*
> [!quote] caption
> Illustrations of Residual Connection Paradigms. This figure compares the structural

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图对比三种残差连接结构：(a) 标准残差——单条恒等旁路，x_l 经 Layer F 后与 x_l 简单相加得 x_{l+1}；(b) Hyper-Connections (HC)——引入三个可学习映射（橙色 H_l^pre、H_l^post、H_l^res），将单流扩展为多流并通过 Pre/Post/Res Mapping 混合；(c) mHC——在 HC 基础上对三个映射分别施加流形投影算子 P_M（绿色框），即 P_M^pre(H_l^pre)、P_M^post(H_l^post)、P_M^res(H_l^res)。

原文借此论证关键技术结论：HC 的 Res Mapping 矩阵若不加约束，其行和可能偏离 1、破坏残差流的尺度稳定性，导致训练振荡；mHC 将映射投影到（如双随机矩阵）流形上，从而稳定残差信号幅度。

在论文中的作用：作为开篇 Figure 1，它奠定全文方法框架，使后续 Table 1 的消融实验与正文中关于"流形约束带来收敛稳定性与性能增益"的论证得以直观对照。

### Figure 2 (p.7) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-fig02.png]]
*整页渲染: ![[assets/hc-manifold-constrained-hyper-connections-p07.png]]*
> [!quote] caption
> Training Instability of Hyper-Connections (HC). This figure illustrates (a) the absolute

> [!tip] 技术解读（多模态）
> 【图文联合解读】图(a)显示HC相对mHC的绝对损失差在5k步内从~0.012骤降至近0，但15k步后又反弹至~0.005；图(b)显示HC梯度范数在0.10–0.18间剧烈震荡，而mHC从0.25单调降至~0.05。原文据此论证HC存在训练不稳定（梯度范数不收敛、损失差回升），从而引出对残差流施加流形约束的mHC，作为全文核心方法改进的动机与实验起点。

### Figure 3 (p.7) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-fig03.png]]
*整页渲染: ![[assets/hc-manifold-constrained-hyper-connections-p07.png]]*
> [!quote] caption
> Propagation Instability of Hyper-Connections (HC). This figure illustrates the

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图(a)展示单层映射 𝓗^res 的逐层前向信号增益（灰）与反向梯度增益（蓝）：在 60 层内二者大多围绕 1 波动（数量级 ≈10⁰），仅在边界 *l*≈0、*l*≈60 处出现尖峰（前向 ≈30，反向 ≈15）。图(b)展示累积乘积 ∏𝓗^res 的复合映射：前向信号末端骤升至 ≈500（10^2.7），反向梯度在中间层累积放大至 ≈3000（10^3.5），整体呈 2–3 个数量级的指数级爆炸。

原文借此论证 **HC 的传播不稳定性**：单层增益看似平稳，但跨深层逐层相乘后信号/梯度会发生数量级级别的发散。该图是论文提出"流形约束（manifold-constrained）"方案以稳定 HC 残差传播的核心动机图，直接驱动后续实验设计与消融验证。

### Figure 4 (p.12) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-fig04.png]]
*整页渲染: ![[assets/hc-manifold-constrained-hyper-connections-p12.png]]*
> [!quote] caption
> Communication-Computation Overlapping for mHC. We extend the DualPipe

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图4 图文联合解读：**

**1) 核心对象与结构：** 图示三流并行时间轴——Normal Compute Stream（含 MLP(B/W/F)、ATTN(B/W/F) 及 Whole Stage Recompute(B)）、Communication Stream（含 DISPATCH(F/B)、COMBINE(F/B)、PP Send/Recv(F/B)）、High Priority Compute Stream（仅承载 ℱₚₒₛₜ,ᵣₑₛᴹ）。小操作 ℱᵖʳᵉᴹ、ℱᵖᵒˢₜ,ᵣₑₛᴬ 等以斜纹小矩形穿插于各流衔接处，体现 Dense 交互开销被嵌入 DualPipe 调度。

**2) 关键结论：** mHC 引入的预聚合/残差聚合额外开销（m 路分发-合并）可与 PP 通信及主流计算完全重叠；高优先级流使小算子不被 stall，证明 mHC 在不牺牲通信-计算重叠效率前提下可扩展至多头架构。

**3) 论文作用：** 该图落在文末 Efficiency/Systems 章节，是支撑"mHC 实际可部署"的核心工程证据，承接前文算法推导，为实践落地与训练成本对比提供调度层依据。

### Figure 5 (p.12) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-fig05.png]]
*整页渲染: ![[assets/hc-manifold-constrained-hyper-connections-p12.png]]*
> [!quote] caption
> Training Stability of Manifold-Constrained Hyper-Connections (mHC). This figure

> [!tip] 技术解读（多模态）
> 【图文联合解读】图5在27B模型、5万步内比较Baseline、HC与mHC。左图以Baseline损失差为0；mHC由约−0.06回升至−0.021，HC回升更快、约至−0.015。右图mHC梯度范数由约0.13缓降至0.04，明显低于在0.09–0.18间剧烈波动并多次触及0.20的HC，且后期趋近Baseline。说明流形约束可抑制梯度爆炸、提升训练稳定性，同时维持更低损失；该图是mHC稳定性设计与后续性能实验之间的关键验证。

### Figure 6 (p.13) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-fig06.png]]
*整页渲染: ![[assets/hc-manifold-constrained-hyper-connections-p13.png]]*
> [!quote] caption
> Scaling properties of mHC compared to the Baseline. (a) Compute Scaling Curve.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图6(b) Token Scaling Curve 解读**

**对象与数据**：图(b)为双面板折线图，横轴为FLOPs（≈1–5×10²¹）。左面板"Absolute Loss Gap"以Baseline归零为参考，mHC曲线从约-0.024单调上升至-0.015；右面板"Relative Loss Ratio"中Baseline锁定100%，mHC由98.8%升至99.15%，两者均表明mHC在各token预算下Loss始终更低。

**技术结论**：mHC的增益在数据规模维度上**持续存在但略有收敛**，说明Baseline仅能通过更多token部分追赶，无法反超，验证了mHC改进的稳健性。

**论文作用**：与(a) Compute Scaling Curve互为补充，从**参数量（3B→27B）**与**数据量**两轴联合证明mHC在全规模上可扩展，是支撑其"适用于生产级预训练"主张的核心缩放性证据。

### Figure 7 (p.14) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-fig07.png]]
*整页渲染: ![[assets/hc-manifold-constrained-hyper-connections-p14.png]]*
> [!quote] caption
> Propagation Stability of Manifold-Constrained Hyper-Connections (mHC). This

> [!tip] 技术解读（多模态）
> 【图文联合解读】**(1) 核心对象与数据**
(a) 单层映射（0–60层）：前向信号增益 $\mathcal{P}_{M^{res}}(\mathcal{H}_l^{res})$ 严格为 1.0（灰线平直）；反向梯度增益 ≈1.03–1.05（蓝线），全程近乎水平。
(b) 复合映射：前向乘积 $\prod_{i=1}^{l}\mathcal{P}_{M^{res}}(\mathcal{H}_i^{res})$ 仍恒为 1.0；反向梯度乘积自 ≈1.1 上升，在第 20–25 层达峰值 ≈1.65，再缓降至 ≈1.0。

**(2) 技术结论**
流形约束保证前向信号幅度逐层精确归一，无衰减也无爆炸；但反向梯度经多层累积可放大约 65%，存在明显爆炸隐患——证明 mHC 对前向与反向路径并非对称稳定。

**(3) 在论文中的作用**
以可量化的传播曲线诊断 mHC 的稳定性边界，揭示反向链路缺乏对偶约束，从而为后续讨论残差式梯度修正、双向流形约束或初始化策略提供实证依据。

### Figure 8 (p.14) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-fig08.png]]
*整页渲染: ![[assets/hc-manifold-constrained-hyper-connections-p14.png]]*
> [!quote] caption
> Visualizations of Learnable Mappings. This figure displays representative single-

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图8图文联合解读**

图8对比HC（上行）与mHC（下行）在27B模型中的单层映射$\mathcal{H}^{res}$与复合映射$\prod$。**HC**的$\mathcal{H}_{60}^{res}$内部元素达±6.77，复合映射$\prod_{i=1}^{60}\mathcal{H}_{61-i}^{res}$元素飙至±142与±509，传播严重失稳；而**mHC**各层值稳定于[0,1]区间，行列和均≈1.0。原文据此论证流形约束显著提升信号/梯度传播稳定性，是验证mHC缓解深层网络表征爆炸/坍塌核心动机的关键可视化实证。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.6) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-tab01.png]]
> [!quote] caption
> | Ablation Study of HC Components. When a specific mapping ( H pre

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 表的核心结构与数据**
该表为HC（Hyper-Connections）三组件的消融实验，纵列为三种可学习映射：$\mathcal{H}_l^{\text{res}}$（残差映射）、$\mathcal{H}_l^{\text{pre}}$（前置映射）、$\mathcal{H}_l^{\text{post}}$（后置映射），横列为绝对损失差（Absolute Loss Gap）。具体量化结果：基线无任何映射为 **0.0**；单独加入 $\mathcal{H}_l^{\text{res}}$ 为 **−0.022**；再叠加 $\mathcal{H}_l^{\text{pre}}$ 为 **−0.025**；三者全部启用为 **−0.027**。

**2) 原文论证的关键结论**
残差映射贡献最显著（−0.022），前置与后置映射虽增益较小但持续有效，说明HC框架中三个映射呈协同互补关系，任一组件不可被固定替代（统一权重或恒等矩阵）所取代，验证了联合可学习设计的必要性。

**3) 在论文整体中的作用**
作为方法可信度的组件级证据，承接前文方法定义，向下游ImageNet等大规模实验延伸——证明HC的增益并非源于单一组件，而是源自三映射的端到端联合优化。

### Table 2 (p.8) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-tab02.png]]
> [!quote] caption
> | Comparison of Memory Access Costs Per Token. This analysis accounts for the overhead introduced by the residual stream maintenance in the forward pass, excluding the internal I/O of the layer function F .

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表量化对比 Residual Connection 与 Hyper-Connections 的逐 token 内存读写开销（不含层函数 F 内部 I/O）。Residual 总 I/O 仅 Read 2C、Write C；HC 经 5 步操作（H^pre/H^post/H^res 计算与 Residual Merge）后总 I/O 达 Read (5n+1)C+n²+2n、Write (3n+1)C+n²+2n，额外开销与残差流数 n 成正比。原文借此论证 HC 多残差流维护带来可控但显著的内存成本，为 Manifold-Constrained 优化提供动机；它衔接 Fig 2 的训练不稳定性分析，支撑"HC 有效但需工程改进"的核心论证链。

### Table 3 (p.11) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-tab03.png]]
> [!quote] caption
> | Stored and Recomputed Intermediate Activations We list per token activation pre- served for the backward pass and the transient activation recomputed in 𝐿 𝑟 consecutive layers. Layer 𝑙 0 represents the first layer in 𝐿 𝑟 layers and layer 𝑙 is in [ 𝑙 0 , 𝑙 0 + 𝐿 𝑟 − 1 ] .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读：**

表3列出 mHC 反向传播中需存储与重算的中间激活（每 token）：① **x_{l₀}**，大小 nC，**每 L_r 层常驻一次**；② **F(𝓗_l^pre x_l, 𝒲_l)**，大小 C，**逐层存储**；③ **x_l、𝓗_l^pre x_l、RMSNorm(𝓗_l^pre x_l)**，大小依次为 nC、C、C，**仅在 L_r 块内临时重算**。

由此推得：重算块引入瞬时显存 (n+2)C·L_r（峰值），常驻部分为 nC·⌈L/L_r⌉；最小化二者之和得 **L_r* ≈ √(nL/(n+2))**，在重算粒度与常驻存储间取得最优。

该式为 mHC 工程实现中块长 L_r 的选取提供量化依据，是连接算法设计与显存高效部署的关键桥梁。

### Table 4 (p.13) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-tab04.png]]
> [!quote] caption
> | System-level Benchmark Results for 27B Models. This table compares the zero- shot and few-shot performance of the Baseline, HC, and m HC across 8 diverse downstream benchmarks. m HC consistently outperforms the Baseline and surpasses HC on the majority of benchmarks, demonstrating its effectivenes

> [!tip] 表格解读（多模态）
> 【图文联合解读】**1) 核心对象与数据**
Table 4对比27B规模下Baseline、HC、mHC三种方案在8项下游任务(BBH/DROP/GSM8K/HellaSwag/MATH/MMLU/PIQA/TriviaQA)的零/少样本表现。mHC在7/8项上同时超越Baseline与HC,如BBH 51.0 vs 48.9/43.8、DROP 53.9 vs 51.6/47.0、TriviaQA 57.6 vs 56.3/54.3;仅MATH上HC以26.4略胜mHC的26.0。

**2) 关键结论**
原文据此论证:在大规模预训练场景下,将超连接约束到双随机流形(mHC)相较原始HC能持续带来更优的下游性能,验证流形约束在大模型上的有效性。

**3) 在论文中的作用**
该表作为"大规模预训练实际增益"的系统级证据,承接架构消融(Table 3)与训练开销分析(通信-计算重叠),共同支撑mHC"以极低额外成本换取一致性能提升"的核心论断。

### Table 5 (p.19) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-tab05.png]]
> [!quote] caption
> | Detailed Model Specifications and Hyper-parameters. This table presents the architec- tural configurations for the 3B, 9B, and 27B models based on the DeepSeek-V3 (Liu et al., 2024b) architecture. It outlines the specific hyper-parameters for m HC and HC, including the residual stream expansion an

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图联合解读（Table 5）**

表5列出3B/9B/27B三组及3B@1T对照组（均基于DeepSeek-V3架构）的详细配置：总参量2.97B/9.18B/27.0B，层数12/18/30，路由专家64/64/72（激活6+共享2），隐藏维1280/1920/2560；统一采用MLA注意力、RoPE(θ=10000)、Loss-Free负载均衡、RMSNorm(ε=1e-20)。

该表支撑mHC与HC的多规模对比实验——通过锁定架构基线排除结构差异，证明mHC的残差流扩展与Sinkhorn-Knopp约束在不同参数量级下均稳定有效（即"方法增益可归因于设计本身而非规模"）。在论文链路中，它是从理论创新过渡到3B→9B→27B实证验证的**统一配置对照表**，是Figure 5训练稳定性曲线得以成立的前置条件。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf{x}_{l+1} = \mathbf{x}_l + \mathcal{F}(\mathbf{x}_l, \mathcal{W}_l),
$$

$$
\mathbf{x}_L = \mathbf{x}_l + \sum_{i=l}^{L-1} \mathcal{F}(\mathbf{x}_i, \mathcal{W}_i),
$$

$$
\mathbf{x}_{l+1} = \mathcal{H}_{l}^{\mathrm{res}}\mathbf{x}_l + \mathcal{H}_{l}^{\mathrm{post}\, \top}\mathcal{F}(\mathcal{H}_{l}^{\mathrm{pre}}\mathbf{x}_l, \mathcal{W}_l),
$$

$$
\mathbf{x}_{L} = \left(\prod_{i=1}^{L-l}\mathcal{H}_{L-i}^{\mathrm{res}}\right)\mathbf{x}_l + \sum_{i=l}^{L-1}\left(\prod_{j=1}^{L-1-i}\mathcal{H}_{L-j}^{\mathrm{res}}\right)\mathcal{H}_{i}^{\mathrm{post}\, \top}\mathcal{F}(\mathcal{H}_{i}^{\mathrm{pre}}\mathbf{x}_i, \mathcal{W}_i),
$$

$$
\begin{cases} \tilde{\mathbf{x}}_l = \text{RMSNorm}(\mathbf{x}_l) \\ \hpre{l} = \alpha_l^\mathrm{pre} \cdot \tanh(\theta^\mathrm{pre}_l \tilde{\mathbf{x}}^\top_l) + \mathbf{b}_l^\mathrm{pre} \\ \hpost{l} = \alpha_l^\mathrm{post} \cdot \tanh(\theta^\mathrm{post}_l \tilde{\mathbf{x}}^\top_l) + \mathbf{b}_l^\mathrm{post} \\ \hres{l} = \alpha_l^\mathrm{res} \cdot \tanh(\theta^\mathrm{res}_l \tilde{\mathbf{x}}^\top_l) + \mathbf{b}_l^\mathrm{res}, \\ \end{cases}
$$

$$
\mathcal{P}_{\mathcal{M}^\mathrm{res}}(\hres{l}) \coloneq \left\{ \hres{l} \in \mathbb{R}^{n \times n} \mid \hres{l}\mathbf{1}_n = \mathbf{1}_n, \ \mathbf{1}^\top_n\hres{l} = \mathbf{1}^\top_n, \ \hres{l} \geq 0 \right\},
$$

$$
\begin{cases} \vec{\mathbf{x}}'_l = \text{RMSNorm}(\vec{\mathbf{x}}_l) \\ \tlhpre{l} = \alpha_l^\mathrm{pre} \cdot (\vec{\mathbf{x}}'_l\phi^\mathrm{pre}_l) + \mathbf{b}_l^\mathrm{pre} \\ \tlhpost{l} = \alpha_l^\mathrm{post} \cdot (\vec{\mathbf{x}}'_l\phi^\mathrm{post}_l) + \mathbf{b}_l^\mathrm{post} \\ \tlhres{l} = \alpha_l^\mathrm{res} \cdot \text{mat}(\vec{\mathbf{x}}'_l\phi^\mathrm{res}_l) + \mathbf{b}_l^\mathrm{res}, \\ \end{cases}
$$

$$
\begin{cases} \hpre{l} = \sigma(\tlhpre{l}) \\ \hpost{l} = 2\sigma(\tlhpost{l}) \\ \hres{l} = \text{Sinkhorn-Knopp}(\tlhres{l}), \end{cases}
$$

$$
\mathbf{M}^{(t)} = \mathcal{T}_r\left(\mathcal{T}_c(\mathbf{M}^{(t-1)})\right),
$$

$$
L_r^* = \arg\min_{L_r} \left[ nC\times \left\lceil\frac{L}{L_r}\right\rceil + (n+2)C\times L_r \right] \approx \sqrt{\frac{nL}{n+2}}.
$$

## 技术点深读（DEEP）

![[deep/hc-manifold-constrained-hyper-connections]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/hc-manifold-constrained-hyper-connections.txt`（55403 字符）供引用检索。