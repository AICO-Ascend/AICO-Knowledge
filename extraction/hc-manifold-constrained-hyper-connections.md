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
> 【图文联合解读】图1对比三种残差连接结构：(a)标准残差——$x_l$经Layer $\mathcal{F}$后与自身相加得$x_{l+1}$；(b)HC引入Res/Pre/Post三个可学习映射$\mathcal{H}_l^{\text{res}}$、$\mathcal{H}_l^{\text{pre}}$、$\mathcal{H}_l^{\text{post}}$，作用于多流隐层$\mathbf{h}$；(c)mHC对上述三映射施加流形投影约束$\mathcal{P}_{\mathcal{M}^{\text{res}}}$、$\mathcal{P}_{\mathcal{M}^{\text{pre}}}$、$\mathcal{P}_{\mathcal{M}^{\text{post}}}$。

该图直观论证：mHC通过投影约束使残差路径趋近恒等、Pre/Post映射近似正交，从而稳定收敛、提升性能；作为开篇框架图，为Table 1消融实验与"流形约束带来性能增益"的核心论点建立结构基线。

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
> 【图文联合解读】图5基于27B模型、训练5万步，对比Baseline、HC与mHC。（a）相对基线的损失差由约−0.06逐渐收敛，末步mHC约−0.02，HC约−0.017。（b）梯度范数初值约0.20；mHC末段约0.04–0.05，较贴近基线，HC约0.10且波动更大，末步升至约0.14。说明mHC训练更稳定，并从优化层面验证流形约束可改善HC扩展残差流的训练性质，为后续性能实验奠基。

### Figure 6 (p.13) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-fig06.png]]
*整页渲染: ![[assets/hc-manifold-constrained-hyper-connections-p13.png]]*
> [!quote] caption
> Scaling properties of mHC compared to the Baseline. (a) Compute Scaling Curve.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图6(b) Token Scaling Curve 图文联合解读**

**1) 核心对象与量化结构**
横轴为FLOPs（≈1×10²¹ ~ 4.5×10²¹），含两个子图：Absolute Loss Gap（−0.03~0.01）与 Relative Loss Ratio（98%~101%）。Baseline恒为0/100%；mHC绝对损失差由约 −0.024 单调回升至约 −0.014，相对损失比由约 98.7% 提升至约 99.3%，共5个采样点。

**2) 关键技术结论**
mHC在所有token预算下均稳定优于Baseline（loss gap始终为负），证明数据量扩展时mHC不失效；但绝对/相对优势随FLOPs增大略有收窄（从≈1.3% → ~0.7%），表明mHC增益在大规模下虽略减但持续存在。

**3) 论文链路作用**
与图6(a) Compute Scaling互补，共同验证mHC在两个正交维度（模型/数据规模）上的可扩展性（scaling law compatibility），排除"小模型收益、大模型失效"的疑虑，为mHC用于大规模预训练提供实证支撑。

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
> 【图文联合解读】**核心对象与数据**：Table 1 展示 HC（流形约束超连接）三个可学习映射 $\mathcal{H}_l^{\text{res}}$、$\mathcal{H}_l^{\text{pre}}$、$\mathcal{H}_l^{\text{post}}$ 的消融实验，以"绝对损失差距"为度量。基线（全禁用）为 0.0；仅启用 $\mathcal{H}_l^{\text{res}}$ 降至 −0.022；叠加 $\mathcal{H}_l^{\text{pre}}$ 达 −0.025；再叠加 $\mathcal{H}_l^{\text{post}}$ 达 −0.027。固定映射分别为均匀 1/n、全 1、恒等矩阵。

**关键技术结论**：三个分量均带来稳定增益且单调叠加——$\mathcal{H}_l^{\text{res}}$ 贡献最大（−0.022），$\mathcal{H}_l^{\text{pre}}$、$\mathcal{H}_l^{\text{post}}$ 各贡献 −0.003、−0.002，验证三者缺一不可、"全量启用"为最优设计。

**论文链路作用**：作为方法组件级消融证据，支撑完整 HC 设计的合理性，为后续主实验提供因果层面的设计合法性背书。

### Table 2 (p.8) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-tab02.png]]
> [!quote] caption
> | Comparison of Memory Access Costs Per Token. This analysis accounts for the overhead introduced by the residual stream maintenance in the forward pass, excluding the internal I/O of the layer function F .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表2图文联合解读**

表2按操作步骤拆解Residual与HC每token的内存读写。Residual仅"Residual Merge"一步：读2C、写C。HC含5步——计算三映射(读nC/写n²+2n)、𝓗^pre(读nC+n/写C)、𝓗^post(读C+n/写nC)、𝓗^res(读nC+n²/写nC)、Merge(读2nC/写nC)——总计读(5n+1)C+n²+2n、写(3n+1)C+n²+2n（n为残差流数）。

**关键结论**：HC引入n路并行残差流，前向内存I/O随n近似线性放大，开销可控且不含反向梯度。**作用**：作为理论分析，量化证明mHC以多项式级内存代价换取多流残差表达力，为其在大型Transformer中实际部署提供可扩展性依据。

### Table 3 (p.11) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-tab03.png]]
> [!quote] caption
> | Stored and Recomputed Intermediate Activations We list per token activation pre- served for the backward pass and the transient activation recomputed in 𝐿 𝑟 consecutive layers. Layer 𝑙 0 represents the first layer in 𝐿 𝑟 layers and layer 𝑙 is in [ 𝑙 0 , 𝑙 0 + 𝐿 𝑟 − 1 ] .

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 3 列出 mHC 反向传播两类激活的存储策略：①持久存储——仅每 L_r 层首个块输入 **x_{l₀}**（nC/token）常驻显存；②块内瞬时重算——F(H_l^{pre}x_l, W_l)、x_l、H_l^{pre}x_l、RMSNorm(·) 输出均在 L_r 连续层内重算，共 (n+2)C/token。

原文据此论证总显存≈nC·⌈L/L_r⌉+(n+2)C·L_r，对 L_r 求导得最优块长 L_r*≈√(nL/(n+2))（式 20），在持久与瞬时开销间取得最优。

该表为 mHC 块级重算设计提供显存账本，是推导 Eq.20 最优块长的依据，证明该策略既保证可微反向又将峰值显存压至 O(√nL)，是论文工程落地的关键支撑。

### Table 4 (p.13) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-tab04.png]]
> [!quote] caption
> | System-level Benchmark Results for 27B Models. This table compares the zero- shot and few-shot performance of the Baseline, HC, and m HC across 8 diverse downstream benchmarks. m HC consistently outperforms the Baseline and surpasses HC on the majority of benchmarks, demonstrating its effectivenes

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表展示27B规模下Baseline、HC、mHC三种配置在8项下游基准的zero/few-shot得分（BBH 3-shot:43.8→48.9→51.0；DROP 3-shot:47.0→51.6→53.9；GSM8K 8-shot:46.7→53.2→53.8；HellaSwag 10-shot:73.7→74.3→74.7；MATH 4-shot:22.0→26.4→26.0；MMLU 5-shot:59.0→63.0→63.4；PIQA 0-shot:78.5→79.9→80.5；TriviaQA 5-shot:54.3→56.3→57.6）。mHC在8项中有7项同时优于Baseline与HC，仅MATH略低0.4。

论文借此论证：mHC在大规模预训练中带来系统性增益，流形约束相对HC具备可观测的实用优势。

该表与Figure 4的DualPipe通信-计算重叠方案配套——前者证明mHC可高效训练，本表则将方法改进落实到真实大模型下游能力，构成mHC有效性最直接的实证闭环。

### Table 5 (p.19) ⭐深度解读
![[assets/crops/hc-manifold-constrained-hyper-connections-tab05.png]]
> [!quote] caption
> | Detailed Model Specifications and Hyper-parameters. This table presents the architec- tural configurations for the 3B, 9B, and 27B models based on the DeepSeek-V3 (Liu et al., 2024b) architecture. It outlines the specific hyper-parameters for m HC and HC, including the residual stream expansion an

> [!tip] 表格解读（多模态）
> 【图文联合解读】表5列出3B/9B/27B模型基于DeepSeek-V3的完整架构：层数12/18/30、隐藏维1280/1920/2560、FFN维896/1280/1536、路由专家64/64/72（激活6、共享2）、注意力头16/24/32，统一采用MLA(KV秩512)、RoPE(θ=10000, dim=64)、RMSNorm(ε=1e-20)，Loss-Free负载均衡；总参2.97B/9.18B/27.0B，并增设3B-1T Tokens列用于长程训练验证。该表为mHC与HC对比提供统一基线，证明mHC（含残差流扩展与Sinkhorn-Knopp约束）在三档规模上均可即插即用，支撑缩放性与消融实验的可复现性，是论文"架构无关性"结论的关键实证。

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