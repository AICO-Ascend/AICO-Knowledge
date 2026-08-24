---
paper_num: "26"
title: "HYPER-CONNECTIONS"
authors: ""
date: "2026/1/19"
arxiv: "https://arxiv.org/abs/2409.19606"
pdf: "papers/hyper-connections.pdf"
slug: "hyper-connections"
tags: []
---

# HYPER-CONNECTIONS

> [!abstract] 摘要（原文）
> 1\. ✨ 这项研究引入了hyper-connections，作为Residual Connections的一种有效替代方案，旨在解决梯度消失和表示崩溃之间的跷跷板效应。 2. 🧠 理论上，hyper-connections通过可学习的深度和宽度连接，并支持动态调整层间连接强度及实现序列-并行双重性，从而优化网络层排布。 3. 🚀 实验结果表明，hyper-connections在LLMs（包括dense和MoE模型）以及Vision任务中均显著提升了性能，同时仅引入可忽略的计算和参数开销。

## 元信息
- **发表日期**: 2026/1/19
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2409.19606
- **本地 PDF**: `papers/hyper-connections.pdf`
- **页数**: 37

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/hyper-connections-fig01.png]]
*整页渲染: ![[assets/hyper-connections-p01.png]]*
> [!quote] caption
> The performance of the baseline model OLMoE-1B-7B and the model with hyper- connections, OLMoE-1B-7B-DHC×4. (1) and (2) show the training loss (0.99 EMA smoothed) and the C4-en validation loss, respectively. Our method converges 1.8 times faster compared to the baseline and maintains a significant advantage at the 500B tokens. (3) and (4) show the accuracy curves on HellaSwag and ARC-Challenge, de

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图含4个子图，在500B tokens规模上对比基线 OLMoE-1B-7B（红）与加入超连接的 OLMoE-1B-7B-DHC×4（蓝）：(1) 训练损失（0.99 EMA平滑）DHC×4全程低于基线，终点差距0.027；(2) C4-en验证损失差距0.028，并标注 "×1.8" 收敛加速；(3) HellaSwag准确率 DHC×4 约71% 对比基线约69.5%；(4) ARC-Challenge DHC×4 约46% 对比基线约40%。

原文据此论证：DHC（Dynamic Hyper-Connections）显著提升训练收敛效率，并在500B tokens长程训练与下游基准上持续保持优势。作为Introduction开篇核心实验证据，为后续消融实验与机制分析提供量化锚点，奠定论文"超连接作为残差结构替代方案有效"的总体立论。

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/hyper-connections-fig02.png]]
*整页渲染: ![[assets/hyper-connections-p02.png]]*
> [!quote] caption
> Hyper-connections (HC) with an expansion rate of n = 2. (a) Residual connections. (b) Hyper-connections: β1, β2, α0,0, α0,1, α1,0, α1,1, α2,1, and α2,2 are learnable scalars or scalars predicted by the network , depending on the specific HC version. These connections enable lateral information exchange and vertical integration of features across depths. The Transformer with HC is shown in Fig. 17.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图2（n=2）解读**

**结构呈现**：图示对比四种连接方案——(a) 残差连接（基线，单层输出加回h）；(b) HC全量版：h拆为h₁、h₂两个隐向量，以7个标量（α₀,₀、α₀,₁、α₁,₀、α₁,₁、α₂,₁、α₂,₂ 实现层↔隐向量深度路由，β₁、β₂ 控制隐向量至输出的残差缩放，并附带h₁↔h₂横向链路）实现纵深加权与宽度交换；(c) 仅保留α的垂直深度连接；(d) 仅保留β的横向宽度连接。

**技术结论**：HC把单一残差通路拓展为"深度整合+宽度交互"双通路；(c)(d)作为消融对照，证明纵、横向通路缺一不可。

**论文作用**：作为HC整体架构定义图与消融范式，为后续嵌入Transformer（图17）及各类视觉/语言实验提供结构基线。

### Figure 3 (p.2) ⭐深度解读
![[assets/crops/hyper-connections-fig03.png]]
*整页渲染: ![[assets/hyper-connections-p02.png]]*
> [!quote] caption
> Cosine similarity be- tween the input of the current and the previous layers for the OLMo-1B models (Groeneveld et al., 2024). The curve represents the median of similarity, while the shaded area indicates the range be- tween the 5th and 95th percentiles.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**图表内容**：横轴为层索引 i（0~32），纵轴为相邻层输入的余弦相似度 cos(h₀ⁱ, h₀ⁱ⁺¹)。红线（Pre-Norm）从第 1 层约 0.2 迅速攀升至 0.85–0.95 区间，并在整个网络深度上保持稳定的高值；蓝线（Hyper-Connection）同样从低位上升，但中位数仅在 0.60–0.85 之间大幅振荡，且第 5–95 分位带更宽（约 0.35–0.90）。

2）**关键论证**：Pre-Norm 模型中相邻层输入高度相似（≈0.9），表明存在明显的表征坍缩/秩坍缩问题，深层难以获得新信息；而 Hyper-Connection 将相似度显著拉低并放大层间差异，证明其有效缓解了该瓶颈。

3）**论文作用**：作为方法动机图，Figure 3 在引入 Hyper-Connection 前定量揭示 Pre-Norm 的固有缺陷，为后续提出残差宽度扩展（多流残差映射）以恢复层间表征多样性提供实验依据，奠定整篇方法的立论基础。

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/hyper-connections-fig04.png]]
*整页渲染: ![[assets/hyper-connections-p05.png]]*
> [!quote] caption
> Sequential and parallel arrangements of hyper-connections with n = 2.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图(a)展示n=2的**顺序排列**超连接结构：单个输入经展开生成2条并行隐藏流（蓝色与橙色块），依次通过layer 1与layer 2；每层前通过"⊕"汇聚各流，层内由可学习矩阵H^l控制流间混合与残差路径。

**论证结论**：该图直观说明超连接（HC）通过可学习矩阵将传统单残差扩展为多流并行结构，并在顺序堆叠中保持每层的多流聚合能力，证明HC可作为ResNet残差连接的**直接泛化**框架。

**整体作用**：图4(a)(b)共同奠定HC的拓扑自由度——既支持常规顺序堆叠，也支持并行多分支，为后续实验（ResNet、ViT、LLM等任务）验证"多流残差优于单流"提供结构基础，是方法论层的核心可视化支撑。

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/hyper-connections-fig05.png]]
*整页渲染: ![[assets/hyper-connections-p06.png]]*
> [!quote] caption
> Comparison of training loss curves for different expansion rate. The left subfigure includes models with dynamic hyper-connections (DHC) at various expansion rates, while the right subfigure shows the effect of omitting the tanh function. Both subfigures illustrate how increasing the expansion rate leads to improved training loss performance over 500B tokens. Results are smoothed using an exponent

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图5解读**

该图展示OLMo-1B基线与DHC在扩展率x1/x2/x4/x8下、100–500B tokens的训练损失曲线（共2子图，各5条曲线）。

**数据观察**：左图（含tanh）在500B处，DHCx1≈2.47最高，基线≈2.43居中，DHCx4/x8≈2.38最低；右图（去tanh）整体上移但曲线排序一致，DHCx4/x8 W/O tanh仍最优。

**关键结论**：①扩展率越大损失越低，DHC x≥2稳定优于基线，证明超连接结构有效；②tanh的引入进一步压低损失，验证其设计必要性。

**论文作用**：作为方法验证的核心实验，从消融角度同时支撑了"扩展率"与"tanh"两项关键设计选择。

### Figure 6 (p.8) ⭐深度解读
![[assets/crops/hyper-connections-fig06.png]]
*整页渲染: ![[assets/hyper-connections-p08.png]]*
> [!quote] caption
> (1) and (2) Training loss (0.99 EMA smoothed) and C4-en validation loss for OLMo-7B and OLMo-7B-DHC×4 models. (3) and (4) Accuracy curves on hellaswag and sciq, demonstrating the superior performance of the OLMo-7B-DHC×4 model.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图以100–500B训练token的OLMo‑7B（红）与DHC×4（蓝）作1×4对照：0.99 EMA训练损失约由2.45降至2.18，C4‑en由2.74降至2.47，DHC全程略低。HellaSwag最终约70%对69%，SciQ约92%对90%，蓝线更优，阴影表示波动范围。结果证明DHC×4在7B规模兼具优化与泛化优势；该图将消融及静态评测延伸至完整训练曲线，支撑动态超连接可扩展且有效的核心结论。

### Figure 7 (p.9) ⭐深度解读
![[assets/crops/hyper-connections-fig07.png]]
*整页渲染: ![[assets/hyper-connections-p09.png]]*
> [!quote] caption
> Visualization of connection matrices for hyper-connections and various related baseline methods. The attention layers, which have odd ids, are marked with green tick marks.

> [!tip] 技术解读（多模态）
> 【图文联合解读】核心：32×32下三角热力图，对比超连接与Post/Pre-Norm层间权重（色阶−1至+1），奇数层（注意力层）用绿色刻度标记。超连接矩阵呈稀疏非均匀分布，第10–11行附近出现一处标注为"PTB"（预训练偏置）的异常亮斑；Post-Norm表现为对角方向的平滑衰减；Pre-Norm则接近均匀强连接（近似恒等）。

结论：超连接学到了比固定残差更丰富、可学习的跨层路由结构，并保留了来自预训练的偏置特征，突破了Post/Pre-Norm的刚性模式。

作用：作为4.5节可视化分析的核心证据，解释表1中DHC×4在MMLU Var（39.7 vs 38.5）和HellaSwag（70.2 vs 69.5）上优于基线的性能来源。

### Figure 8 (p.14) ⭐深度解读
![[assets/crops/hyper-connections-fig08.png]]
*整页渲染: ![[assets/hyper-connections-p14.png]]*
> [!quote] caption
> Comparison between transformers with hyper-connections and that with residual connec- tions. 14

> [!tip] 技术解读（多模态）
> 【图文联合解读】图左为标准残差Transformer（h⁰→Attention⁺→FFN⁺→…→h^L单流跳连）；右为宽度n=2的Hyper-Connections：h⁰经Repeat得双流h⁰₁、h⁰₂，每层以α^l_{i,k}分配权重（2×3矩阵）将前层多流混合输入Attention/FFN，β^l_j门控缩放输出后再分裂为h^l₁、h^l₂。结论：超连接以可学习权重替代固定残差，将残差函数族从标量加法扩展为多流加权聚合，缓解层间信息瓶颈。作用：为论文核心架构创新提供与残差基线的直观对照，支撑后续消融与扩展性实验。

### Figure 9 (p.17) ⭐深度解读
![[assets/crops/hyper-connections-fig09.png]]
*整页渲染: ![[assets/hyper-connections-p17.png]]*
> [!quote] caption
> Loss curves in V3 validation sets and accuracy curves on downstream tasks for OLMoE-1B7B and OLMoE-1B7B-DHC×4 models. 17

> [!tip] 技术解读（多模态）
> 【图文联合解读】图9由28张子图组成，对比 OLMoE-1B-7B（红）与 OLMoE-1B-7B-DHC×4（蓝）在约100B–500B tokens 训练区间的表现。上12张为训练loss及12个验证集（C4、Dolma六子集 books/cc/pes2o/reddit/stack/wiki、Ice、M2D2-s2orc、Pile、WikiText-103）的loss曲线，蓝色全程稳定低于红色约0.02–0.05；下16张为MMLU四类及平均、HellaSwag、SciQ、ARC-Challenge/Easy、PIQA、WinoGrande、OpenBookQA、BoolQ、COPA、CommonsenseQA、SocialIQA 的下游准确率，蓝色多数高于红色且差距随训练持续或扩大。

论证：DHC×4 在保持 MoE 稀疏激活宽度不变的前提下，同时降低预训练loss并提升下游任务准确率，支撑核心主张——可学习残差连接（DHC）作为静态跳连的可扩展替代优于基线，是论文方法有效性的关键横向验证证据。

### Figure 10 (p.18) ⭐深度解读
![[assets/crops/hyper-connections-fig10.png]]
*整页渲染: ![[assets/hyper-connections-p18.png]]*
> [!quote] caption
> Loss curves in V3 validation set and accuracy curves on downstream tasks for OLMo-7B and OLMo-7B-DHC×4 models. 18

> [!tip] 技术解读（多模态）
> 【图文联合解读】图含15子图：9个V3验证集loss曲线（c4 en、dolma六子集books/cc/pes2o/reddit/stack/wiki、ice、m2d2-s2orc、pile、wikitext103）与6个下游任务准确率（HellaSwag、SciQ、COPA、OpenbookQA、PIQA、WinoGrande、ARC-Easy），对比OLMo-7B基线与OLMo-7B-DHC×4在100B–500B token训练区间表现。

蓝色DHC×4在所有loss子图均稳定低于红色基线（如HellaSwag最终约70% vs 68%、SciQ约92% vs 90%、COPA约83% vs 80%），6个准确率均高于基线。论证DHC宽度扩展（×4）在7B规模上同时改善预训练loss与下游能力，是论文支撑"超连接可扩展优于残差基线"结论的核心实验链路。

### Figure 11 (p.20) ⭐深度解读
![[assets/crops/hyper-connections-fig11.png]]
*整页渲染: ![[assets/hyper-connections-p20.png]]*
> [!quote] caption
> Training loss curves of ViT/16-Large and ViT/16-Large-DHC×2, smoothed using an

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 图示对象与数据：** 图中展示 ViT/16-Large（红线）与 ViT/16-Large-DHC×2（蓝线）在约 60000–95000 步区间的训练 loss 曲线，EMA(0.999) 平滑；纵轴为 loss，横轴为训练步数。蓝线全程位于红线之下，差距随步数推进而逐渐收敛。

**2) 论证的技术结论：** DHC×2 在多 epoch 训练中持续降低训练 loss，证明超连接带来的额外容量确有优化收益；但随同一数据集被反复遍历，HC 的增益递减，暗示存在对训练集的过拟合/记忆效应，容量扩展收益边际递减。

**3) 在论文链路中的作用：** 作为支撑实验，量化验证 HC 的容量增益随训练饱和的边界条件，为后续关于泛化、可扩展性与训练效率的讨论提供实证依据，也解释了在有限 epoch 设置下 DHC 优势更显著的现象。

### Figure 12 (p.21) ⭐深度解读
![[assets/crops/hyper-connections-fig12.png]]
*整页渲染: ![[assets/hyper-connections-p21.png]]*
> [!quote] caption
> Distribution of weights of last DHC in ViT-Base/16-DHC×2 model. F MORE VISUALIZATION AND ANALYSIS

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（图12）**

图12展示ViT-Base/16-DHC×2末层DHC模块权重在两幅不同输入图上的分布直方图：左侧绿色为"capitulum"，右侧橙色为"779:school bus"，共7个参数（β₁≈1.10–1.20、β₂≈1.10–1.20、α₁,₀≈−0.65–−0.35、α₁,₁≈1.1–1.3、α₁,₂≈0.1–0.3、α₂,₀≈2.0–2.4、α₂,₁≈−0.2–0.2）。

关键发现：同一网络面对不同样本时权重分布差异极大——"school bus"在β₁≈1.20、α₁,₁≈0.9、α₁,₂≈−0.1、α₂,₁≈−0.2等极值处高度集中（频次≈50），而"capitulum"分布相对分散。这是论文**"超连接具有输入自适应动态路由"**这一核心命题的直观证据，用以佐证其用可学习动态连接替代静态残差路径的方法论动机。

### Figure 13 (p.22) ⭐深度解读
![[assets/crops/hyper-connections-fig13.png]]
*整页渲染: ![[assets/hyper-connections-p22.png]]*
> [!quote] caption
> Visualization of unfolded connection matrix.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象：** 图中两组（a DHC / b SHC）各展示5个33×33上三角展开连接矩阵 **C⁽⁰⁾~C⁽⁴⁾**（隐状态 h_i^j 中 j=0…32），色阶[−1, 1]，奇数层（注意力层）顶部标绿刻度。

**2) 关键结论：** 两模型学到的连接模式高度一致——主对角线呈深红（≈+1，自连接最强），向上呈近似指数衰减的正连接；C⁽⁰⁾扩散最广，注意力层位置出现竖向蓝条（负抑制）。这说明习得的连接结构以"位置/层依赖"为主，而非输入相关，从而支持 SHC 可作为 DHC 的简化替代。

**3) 链路作用：** 为"去除动态门控、保留静态超连接亦不损性能"提供可视化依据，支撑论文方法简化与推理加速的核心论点。

### Figure 14 (p.23) ⭐深度解读
![[assets/crops/hyper-connections-fig14.png]]
*整页渲染: ![[assets/hyper-connections-p23.png]]*
> [!quote] caption
> Comparison of unfolded connection matrices for OLMo-1B-DHC×1, OLMo-1B-DHC×2 and OLMo-1B-DHC×4 model.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**核心对象**：三幅33×33展开式连接矩阵热力图（值域[-1,1]，红正蓝负），分别对应 OLMo-1B-DHC×1/×2/×4。

**结构对比**：
- (a) ×1：连接高度集中在主对角带，中段约第18列被标注"wasted"，呈现明显的稀疏带状结构，代表性容量未被充分利用；
- (b) ×2：连接沿对角扩展，副对角与跨行条目增多，带状结构弱化；
- (c) ×4：连接近乎弥散至全矩阵，出现显著蓝色（负值）条目，呈现正负交错的多路径路由。

**技术结论**：随宽度从1→4，连接从"窄带冗余"演化为"近全连接"；×1存在显著浪费，而更宽连接可承载更丰富、含正负权重的多路径信息流。

**论文作用**：作为经验证据，支撑"加宽超连接可释放表征容量"的核心论点，与其它实验共同构成 DHC 设计的消融/可解释性链路。

### Figure 15 (p.31) ⭐深度解读
![[assets/crops/hyper-connections-fig15.png]]
*整页渲染: ![[assets/hyper-connections-p31.png]]*
> [!quote] caption
> Training loss curves of related works, smoothed using Exponential Moving Average (EMA) with a decay rate of 0.99. 31

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**核心对象与数据：** 图L展示1B参数规模下5条训练Loss曲线（EMA平滑，衰减率0.99），横轴为token数（0–500B），纵轴Loss范围2.4–2.9。曲线包括基线OLMo-1B（红）、ResiDual（蓝）、Altup×2（绿）、本文DHC×2（紫）、DHC×2 W/O tanh（橙）。起点均约2.88–2.89，训练至500B时收敛到不同终值：Altup最高约2.42，紫/橙两条DHC最低约2.38–2.39，基线与ResiDual居中约2.40；红色基线在约100B、250B处出现明显Loss尖峰。

**关键技术结论：** 在1B规模下，本文DHC×2（含/不含tanh）训练Loss始终低于基线OLMo与ResiDual，全程优于Altup；tanh激活对DHC性能影响极小，验证了所提方法相对相关工作的稳定优势。

**论文链路作用：** 作为附录L的扩展实验，1B规模与正文更小规模的实验形成多尺度互证，强化"DHC在大模型预训练中同样有效且优于ResiDual、Altup"的核心主张，支撑正文方法对比的结论。

### Figure 16 (p.32) ⭐深度解读
![[assets/crops/hyper-connections-fig16.png]]
*整页渲染: ![[assets/hyper-connections-p32.png]]*
> [!quote] caption
> Training loss curves of DHC with tanh over 500 billion tokens, smoothed using

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

1) **核心对象与数据**：图中呈现 5 条训练 loss 曲线，横轴为训练 token 量（0–1000B），纵轴 loss 范围约 2.35–2.60，曲线经 EMA（decay=0.99）平滑。对比对象为基线 OLMo-1B（红）与四个 DHC（带 tanh）变体：x1（蓝）、x2（绿）、x4（紫）、x8（橙）。两条红色竖线标记约 250B 与 350B 处 loss 尖峰事件。训练终止时 loss 由高到低约为：DHCx1≈2.36 > 基线≈2.35 > DHCx2/x4≈2.34 > DHCx8≈2.33（最低）。

2) **关键结论**：DHC 扩展比（×N）越大，训练 loss 越低，证明超连接中**残差流宽度扩展**对模型拟合能力有正向增益；但 x1 因通道数不足略逊于基线，验证了**最小扩展阈值**的存在。该图与 Fig.17（无 tanh）配对，论证 tanh 门控对收敛稳定性的必要性。

3) **实验链路作用**：此图属于超连接消融实验（与 Table 6、Fig.13–15 呼应），为论文核心主张——DHC 通过隐式增加模型深度/宽度且不增显式参数即提升性能——提供了长程训练（1000B tokens 量级）的可复现 loss 证据，构成从组件有效性到端到端训练有效性的关键证据链。

### Figure 17 (p.32) ⭐深度解读
![[assets/crops/hyper-connections-fig17.png]]
*整页渲染: ![[assets/hyper-connections-p32.png]]*
> [!quote] caption
> Training loss curves of DHC without tanh over 500 billion tokens, smoothed using

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 图示内容**：5条EMA(衰减率0.99)平滑的训练loss曲线，横轴0–1000B tokens，纵轴约2.30–2.60；对比OLMo-1B基线（红）与DHC×1/×2/×4/×8无tanh版本（蓝/绿/紫/橙）。紫色DHC×4末值最低≈2.33，橙×8、绿×2次之，红色基线在1000B处≈2.35；蓝色×1全程高于基线表现最差。

**2) 关键技术结论**：去掉tanh约束后，DHC×2/×4/×8仍稳定低于基线且随expansion rate提升loss进一步降低，证明tanh并非DHC发挥作用的必要前提；但×1反劣于基线，表明需足够宽度扩展方能取得增益。

**3) 论文作用**：属DHC消融实验关键证据，验证无tanh简化设计仍保持有效性，为方法选型与训练效率提供支撑。

### Figure 18 (p.33) ⭐深度解读
![[assets/crops/hyper-connections-fig18.png]]
*整页渲染: ![[assets/hyper-connections-p33.png]]*
> [!quote] caption
> Training loss curves comparied with parallel transformer blocks (PTB), smoothed using

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示OLMo-1B四种架构在10B–500B tokens上的训练损失曲线（EMA衰减0.99平滑），含四组：红线基线OLMo-1B、蓝线OLMo-1B-PTB、绿线DHC×4去tanh、紫线DHC×4。500B tokens处收敛损失依次约为2.41、2.43、2.39、2.38——DHC×4最低，PTB反高于基线，tanh带来小幅额外增益。

**论证结论：**
1. 所提Dynamic Hyper-Connections（DHC）在训练收敛性上显著优于串行基线与并行Transformer块（PTB）；
2. PTB虽加速并行却损失更差，证明DHC兼顾效率与质量；
3. tanh门控组件不可或缺，去除即性能回退。

**论文链路作用：** 该图是核心消融/对比证据，回应"并行化是否更优"的潜在质疑，支撑Hyper-Connections作为优于串行、PTB两类baseline的架构选择，为后续下游任务表现提供训练动力学依据。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.6) ⭐深度解读
![[assets/crops/hyper-connections-tab01.png]]
> [!quote] caption
> Ablation study on expansion rates n with training on 500 B tokens.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

Table 1 以 OLMo-1B 为基线，在 500B tokens 上对 DHC 扩展率 n∈{1,2,4,8} 做消融，对比"去 tanh"与"含 tanh"两版本。数据显示：基线 V2/V3 PPL 为 18.023/14.229，下游均准 62.5；扩展率升高后指标单调改善，DHC×8 W/O tanh 取得最低损失（V2 2.777、PPL 17.425，V3 2.514、PPL 13.819），DHC×4 W/O tanh 取得最高下游精度 64.4；含 tanh 版本整体略低但更稳定。

原文借此论证"扩展率 n 越大越好、tanh 提供稳定正则"，支撑 Figure 1 中 OLMoE-1B-7B-DHC×4 收敛速度 1.8× 提升的结论。该表在论文中起核心验证作用：量化 n 与 tanh 的边际收益，为 DHC 模块超参选择与设计合理性提供实验依据。

### Table 2 (p.7) ⭐深度解读
![[assets/crops/hyper-connections-tab02.png]]
> [!quote] caption
> Ablation study on static and dynamic hyper-connections with training on 500 B tokens.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读**

Table 2 在 500B tokens 训练规模上消融 OLMo-1B 基线、SHC×n、DHC×n（n=2/4）及去 tanh 变体，对比 V2/V3 验证集 Loss、PPL 与下游平均准确率。数据上：基线 V2 Loss 2.811、下游 62.5%；DHC×4 去 tanh 以 V2 Loss 2.779、下游 64.4% 双双最优；DHC×4（带 tanh）在 V3 PPL 13.826 最佳。

原文据此论证四点关键技术结论：① 超连接稳定优于残差基线；② 动态路由（β、α 由网络依输入预测）优于静态可学习标量；③ 扩展率 n=4 优于 n=2；④ 去除 tanh 进一步提升。该消融是支撑图 2 架构设计与 HC 整体方法有效性的核心证据，串联从组件动机（Figure 2 残差/深度/宽度连接分解）到性能验证的完整实验链路，确证横向信息交换与纵向特征整合的协同价值。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/hyper-connections-tab03.png]]
> [!quote] caption
> Ablation study on OLMo-1B-DHC × 4. In the B or WC column, the symbol " ✗ " denotes parameters that are not trainable from initialization.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**1) 核心对象与数据**
Table 3 对 OLMo-1B-DHC×4 的三个组件（WC 加权连接、B 偏置、Tanh 激活）做 6 组消融，"✗"=从初始化冻结不训练、"✓"=可训练；指标含 V2/V3 验证 Loss 与 PPL、下游平均准确率。最优配置 WC✓+B✓+Tanh✗：V2 Loss=2.779、PPL=17.773，V3 Loss=2.516、PPL=13.823，Acc=64.4；加 Tanh 后 Acc 略降至 63.8；仅 WC 可训练 Acc=63.6；仅 B 可训练最差（Acc=62.5）。

**2) 关键结论**
WC 与 B 必须同时可训练、缺一不可，单独训练任一项均退化明显；Tanh 几乎无增益甚至略损，验证"加权连接+偏置"即 DHC 的最小有效设计。

**3) 论文作用**
消融验证支撑 DHC 设计简洁性与组件必要性；与 Fig.3 揭示的残差流跨层高余弦相似性形成"为何需引入动态重加权"的动机—方案互补论证。

### Table 4 (p.8) ⭐深度解读
![[assets/crops/hyper-connections-tab04.png]]
> [!quote] caption
> Performance of related methods on OLMo-1B models.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 4 在 OLMo-1B 上对比 DHC×2 与 ResiDual、Altup×2，指标含 V2/V3 Eval Loss、PPL 及下游平均准确率。DHC×2 W/O tanh 全面最优：Loss 2.792/2.529、PPL 17.663/14.033、下游 Acc 63.8%，超越基线 62.5%。论证：(1) ResiDual、Altup 反劣于 vanilla 残差（62.0/62.4）；(2) DHC×2 略胜基线（63.0）；(3) 去 tanh 后增益扩大，表明动态连接矩阵中的非线性门控非必需。此表作 1B 量级消融，与图 4 的 n=2 拓扑示意（顺序/并行）呼应，承接结构设计论证，启下 4.3 节 7B 模型训练曲线验证。

### Table 5 (p.9) ⭐深度解读
![[assets/crops/hyper-connections-tab05.png]]
> [!quote] caption
> Performance of 7B models. FLOPs refers to the computation per token in the forward pass.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 5横向对比 **OLMo-7B** 与 **OLMo-7B-DHC×4**（参数量同为 6.9B）：前向 FLOPs 仅由 13.36G 微增到 13.38G（+0.15%，几乎可忽略）；V2 损失 2.581→**2.559**（PPL 14.316→**14.023**），V3 损失 2.322→**2.304**（PPL 11.324→**11.120**），下游任务平均准确率 70.1→**71.0**，DHC 在每一列指标上均更优（粗体标注）。

**论证结论**：将扩展率 r=4 的动态超连接（DHC）施加到 7B 级别基线时，可同时压低预训练损失/困惑度并提升下游准确率，验证了 hyper-connections 不只是小模型上的"玩具改进"，而是**在规模放大后仍保持"近零额外算力、可见效果增益"**的关键证据。

**在论文链路中的作用**：与 Figure 5（OLMo-1B 训练曲线）构成"小模型看趋势 → 7B 看收益"的递进证据链，为全文"以极低成本改造残差流、可随规模稳定 scaling"的核心主张提供决定性的大模型端实证支撑。

### Table 6 (p.9) ⭐深度解读
![[assets/crops/hyper-connections-tab06.png]]
> [!quote] caption
> Downstream evaluations for MoE models training with 500B tokens under the OLMoE evaluation setting. ARC-C stands for ARC-Challenge, and ARC-E for ARC-Easy. MMLU Var is a modified version of MMLU that includes varying few-shot examples, providing stable feedback during early training, as outlined in 

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）表6对比OLMo-7B与OLMo-7B-DHC×4（n=4）：参数同为6.9B，FLOPs仅由13.36G增至13.38G（+0.02G）；V2 Loss 2.581→2.559（↓0.022），V3 Loss 2.322→2.304（↓0.018），对应PPL分别由14.316/11.324降至14.023/11.120，下游任务平均Acc由70.1升至71.0。注：表内为稠密OLMo-7B，与caption所述"MoE models / OLMoE setting"不符，存在标注疑误。

2）原文据此论证：DHC以n=4替换残差连接后，在近全指标上超越残差基线——训练loss降~0.027、C4-en验证loss降0.028、ARC-Challenge +6分、MMLU Var +1.2分，且仅需基线一半训练token即可达同等性能。

3）作用：与Fig.1、Fig.9互证，确立"近零参/算力代价换取稳定性能增益"这一核心实证支柱，支撑超连接作为残差连接可扩展替代方案的方法论主张。

### Table 7 (p.15) ⭐深度解读
![[assets/crops/hyper-connections-tab07.png]]
> [!quote] caption
> Comparison of number of parameters.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明**：所提供图片实际为论文正文（含公式21–26），仅在末尾出现"Table 7: Comparison of number of parameters."标题，**表格本身的数值未在图像中呈现**；用户附带的讲解文字实为 Figure 7（连接矩阵热力图）的caption，存在张冠李戴。以下仅依据图像中的公式与正文论证解读：

1) **核心对象**：Table 7 用于列出实验中各模型（OLMo-1B/7B、OLMoE 等）在 SHC×{2,4}、DHC×{2,4} 配置下的参数总量与额外参数 $P_\text{extra}$。图像给出的计算式为：SHC 额外参量 $n(n+2)\times 2L$（例 OLMo-1B-SHC×4 = 768）；DHC 额外参量 $(|\theta_\text{norm}|+d_\text{model}(n+2)+n(n+2)+2)\times 2L$（例 OLMo-1B-DHC×4 = 394,048）。

2) **关键结论**：相比基座模型动辄数十亿的参数量，SHC/DHC 引入的额外参数占比极小；SHC 仅含静态矩阵 $n^2$ 量级，DHC 主体来自宽度为 $d_\text{model}$ 的窄投影，与表 8 的 FLOPs 共同支撑"开销可忽略"这一论断。

3) **论文作用**：与 Table 8（FLOPs）配套，为"超连接以极小成本换取残差路径扩展"的整体方法论证提供参数–计算双重证据。

### Table 8 (p.16) ⭐深度解读
![[assets/crops/hyper-connections-tab08.png]]
> [!quote] caption
> FLOPs per token in forward pass.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 图文联合解读**

1) **核心对象与数据**：表 8 展示前向传播中每 token 的 FLOPs，对比 OLMo 基线与四种 HC 变体（SHC×2/×4、DHC×2/×4），覆盖 1B/7B 稠密及 MoE 模型。HC 自身仅新增 0.0010G–0.0197G FLOPs，总 FLOPs 增幅在 **+0.038% 到 +0.208%** 之间（OLMo-1B-DHC×4 最大仅约 0.2%）。

2) **关键结论**：HC（尤其 DHC）引入的计算开销相对原 Transformer 可忽略不计，验证了"以极低算力代价换得残差连接替换"的可行性，与下方 Memory Footprint 段落（n=2 时额外显存 <15%，且隐状态可重计算）共同构成"算力–显存双廉价"的论证链。

3) **整体链路作用**：在 Figure 8（架构对比）定性展示之后，本表以量化 FLOPs 增量排除读者对 HC 复杂度的疑虑，为后续 Table 9 实测显存与下游性能实验铺路，证明 HC 是"即插即用"的轻量残差替代方案。

### Table 9 (p.16) ⭐深度解读
![[assets/crops/hyper-connections-tab09.png]]
> [!quote] caption
> Measured Memory Footprint on 8 GPUs.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**注意**：图片实际呈现的是 FLOPs 对比表（HC FLOPs / Total FLOPs / Δ 率），与所标注的"Measured Memory Footprint"存在出入，以下按可见内容解读。

**1) 核心数据**：对比 OLMo-1B/7B 及 OLMoE-1B-7B 在 SHC×2/×4、DHC×2/×4 变体下的计算开销。HC 引入的额外 FLOPs 极小（OLMo-1B-DHC×4 仅 0.0049G，总 Δ +0.200%；OLMo-7B-DHC×4 仅 0.0197G，Δ +0.147%；OLMoE-1B-7B-DHC×4 为 0.0049G，Δ +0.208%），即 HC 占比 <0.15%。

**2) 关键论证**：结合正文 Memory Footprint 段落（激活额外 2nsbd_modelL，前向丢弃+重算可降至 nsbd_model），共同证明 HC 是"近零开销"的高性价比结构替换，为 DHC×4 等扩展变体在大模型上的可行性提供效率依据。

**3) 链路作用**：与 Figure 9（OLMoE-1B-7B 损失/下游精度曲线）形成"效率—效果"双验证，确保性能增益并非源于算力堆叠，而是结构本身的归纳偏置。

### Table 10 (p.19) ⭐深度解读
![[assets/crops/hyper-connections-tab10.png]]
> [!quote] caption
> Benchmarking class-conditional image generation on ImageNet 256 × 256, with cfg=1.50. NP , P , and R are short for Numerical Precision, Precision, and Recall, respectively.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表对比ImageNet 256×256条件生成（cfg=1.50）下四个DiT变体。核心数据：DiT-XL/2-SHC×2（675M、FP16、QK-Norm）的FID=2.18、sFID=4.52、IS=287.24、R=0.60，较同规模基线DiT-XL/2（FID=2.36）FID降低0.18，并逼近参数量大45%的DiT-1B/2（983M，FID=2.13、IS=288.69）。论文据此论证两点：(1)FP16配合QK-Norm在降低数值精度（NP）下仍保持生成稳定；(2)静态超连接（SHC×2）以更少参数逼近更大模型质量，证明HC模块的扩展有效性。该表属于方法验证实验链路，与下游任务表格共同为"超连接可作为残差连接的drop-in替代"提供生成质量层面的实证支撑。

### Table 11 (p.19) ⭐深度解读
![[assets/crops/hyper-connections-tab11.png]]
> [!quote] caption
> Accuracy on ImageNet. ViT*/16 refers to the results reported by (Dosovitskiy et al., 2020), whereas ViT/16 denotes our re-implemented baseline. SHC and DHC indicate that residual connections are replaced with static and dynamic hyper-connections, respectively.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表中以224×224图像、bfloat16训练ViT/16 300轮，将残差替换为静态(SHC)或动态(DHC)超连接，扩展率n=2。85M Base准确率由76.38%升至SHC 77.60%、DHC 77.26%；307M Large由77.25%升至78.38%、79.94%，相对提升1.13%和2.69%。结果表明DHC在Large上优势最大，HC可在不增模型规模下提精度；该表承担方法在图像分类任务中的验证作用。

### Table 12 (p.20) ⭐深度解读
![[assets/crops/hyper-connections-tab12.png]]
> [!quote] caption
> Training hyperparameters for ViT.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图像无法完整辨认**：所提供图片仅显示了论文 E.3 节"Visualization of DHC"的正文段落（含 Figure 12 的讨论），并未呈现 Table 12 的实际行列超参数数据，仅在页脚处可见"Table 12: Training hyperparameters for ViT"的标题。下列说明以原文段落与标题为依据。

**核心对象**：Table 12 应列出 ViT 系列模型（含 baseline ViT-Base/16 与其 DHC×2 变体）的训练超参数——典型项目包括优化器（如 AdamW / Adam）、batch size、weight decay、learning rate 与 schedule、warmup epochs、总训练 epoch 数、augmentation、label smoothing、drop_path 等。

**技术结论**：该表作为附录表，与 Figure 12（最后一层 DHC 动态权重分布可视化）同页出现，意在以可复现的超参数配置支撑"beta 类内高度集中、alpha 类间差异显著"的结论——即 DHC 学到了输入相关的连接模式。

**论文链路作用**：Table 12 属于"More Visualization and Analysis"附录的实验可复现性模块，确保主文中 ViT 图像分类实验（baseline vs DHC）结果与权重可视化分析可在统一配置下被复现与对比。

### Table 13 (p.0) ⭐深度解读
![[assets/crops/hyper-connections-tab13.png]]
> [!quote] caption
> OLMo’s default configuration was evaluated using multiple metrics. Perplexity (PPL) and loss were used for the V2 and V3 Validation Sets, while zero-shot testing was applied to the Downstream Benchmarks. However, the grey benchmarks were excluded from our analysis due to the instability of their per

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 13 图文联合解读**

该表列出了 OLMo 默认配置下的完整评测体系，分为三大类共34项指标：① **V2 Validation Sets**（12项，如 4chan、C4、Gab、ICE、Manosphere、Pile 等领域验证集）；② **V3 Validation Sets**（11项，涵盖 Dolma 的 books、common-crawl、pes2o、reddit、stack、wiki 等子集）；③ **Downstream Benchmarks**（11项零-shot任务：piqa、hellaswag、winogrande、openbook_qa、sciq、arc_easy、copa、commitment_bank、mrpc、rte、sst2）。验证集用 PPL/loss，下游任务用零-shot 准确率，灰色行因数值不稳定被剔除。原文借此论证：hyper-connections 在**多领域语言建模**（V2/V3 验证集覆盖域内与域外语料）与**多任务下游能力**（涵盖推理、常识、NLI、情感分析）上均需系统性对比，是评估 DHC/SHC 变体有效性的统一基准，在实验链路中充当"多维度可复现评测脚手架"。

### Table 14 (p.31) ⭐深度解读
![[assets/crops/hyper-connections-tab14.png]]
> [!quote] caption
> Downstream Benchmarks for OLMoE.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1）核心对象与结构：** 表左侧仅列出 12 个下游评测基准名称（包括 piqa、hellaswag、winogrande、openbook_qa、sciq、arc_easy、arc_challenge、copa、boolq、commonsense_qa、social_iqa、mmlu）及其文献引用，覆盖常识推理、阅读理解、问答与多任务知识等能力。右侧具体分数列在本截图中未呈现。

**2）论证结论：** 论文将该评测套件作为 OLMoE 模型的标准化下游验证集，对照基线与不同 DHC 扩张倍率（×1/×2/×4），证明 Hyper-Connections 在预训练指标之外，亦能在多样化下游任务上取得一致增益，从而验证方法的可迁移性与稳健性。

**3）在论文链路中的作用：** 与正文 Figure 14（连接矩阵可视化）互补——前者展示"结构层面"的展开模式，后者给出"任务层面"的实证收益，共同支撑"结构改动有效且泛化"的核心论点。

### Table 15 (p.33) ⭐深度解读
![[assets/crops/hyper-connections-tab15.png]]
> [!quote] caption
> Results on downstream benchmarks for 1B models.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 15 图文联合解读**

**1) 核心数据**：表格展示 OLMo-1B 基线与多种 hyper-connection 变体在 7 个下游基准（arc_easy、copa、hellaswag、openbook_qa、piqa、sciq、winogrande）上的平均分。基线为 62.5；DHCx4 W/O tanh 取得最高均分 64.4，DHCx4、DHCx2 W/O tanh 均为 63.8，SHCx4 为 63.6，均高于基线。

**2) 关键结论**：① 增大连接扩展因子 n（DHCx4）效果最佳，过大（x8）反降；② 移除 tanh 在 DHC 上平均更优（64.4 vs 63.8）；③ 非可训练 WC/ℬ 变体（63.4/63.6）与全训练版本相当，说明结构先验本身已贡献增益；④ SHC 同样带来提升，验证稀疏超连接的泛化能力。

**3) 实验链路作用**：作为 1B 规模下游消融，对超参数 n、激活 tanh、可训练性进行系统性扫描，与 7B 实验、训练损失曲线（Figure 15）共同支撑"hyper-connections 改进跨规模稳健有效"的核心论点。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\left|\theta_{\texttt{SHC}}\right|= |\theta_{\mathbf{B}}| + |\theta_{\mathbf{A}}|= n + n \cdot (n+1)=n \cdot (n+2),
$$

$$
P_{\texttt{extra}}=\left|\theta_{\texttt{SHC}}\right| \times 2 \times L,
$$

$$
P_{\texttt{extra}}=\left|\theta_{\texttt{DHC}}\right| \times 2 \times L,
$$

$$
\mathbf{\hat{h}} = \mathcal{T}(\texttt{Norm}(\mathbf{h})) + \mathbf{h}.
$$

$$
\mathbf{\hat{h}} = \mathcal{T}(\mathbf{h}) + \mathbf{h}.
$$

$$
\mathcal{HC}_{PreNorm}=\begin{pmatrix} 0 & 1 \\ 1 & 1 \\ \end{pmatrix}
$$

$$
\begin{aligned} \mathbf{\hat{H}} &= \mathcal{HC}(\mathcal{T}, \mathbf{H}) \\ &=\mathbf{B}^\intercal\mathcal{T}(\mathbf{H}^\intercal\mathbf{A_m})^\intercal + \mathbf{A_r}^\intercal\mathbf{H} \\ &=\mathcal{T}(\mathbf{h})^\intercal + \mathbf{h}^\intercal \\ &=\mathbf{\hat{h}}^\intercal. \end{aligned}
$$

$$
\mathbf{h}' = \mathcal{T}(\mathbf{h})
$$

$$
\mathbf{\hat{h}} = \texttt{Norm}(\mathbf{h} + \mathbf{h}')
$$

$$
\mathcal{T} = \mathcal{C} \circ \mathcal{T} \circ \mathcal{A},
$$

$$
\mathcal{HC}_{PostNorm}=\begin{pmatrix} 0 & \frac{1}{\sqrt{\sigma_{\mathbf{h}}^2 + \sigma_{\mathbf{h}'}^2 + 2\sigma_{\mathbf{h}\mathbf{h}'}}} \\ 1 & \frac{1}{\sqrt{\sigma_{\mathbf{h}}^2 + \sigma_{\mathbf{h}'}^2 + 2\sigma_{\mathbf{h}\mathbf{h}'}}} \\ \end{pmatrix}=\begin{pmatrix} 0 & \mathbf{B} \\ \mathbf{A}_m & \mathbf{A}_r \\ \end{pmatrix}.
$$

$$
\mathbf{\hat{H}}=\mathbf{\hat{h}}^\intercal.
$$

$$
\sigma_{\mathbf{h} + \mathbf{h}'} = \sqrt{\sigma_{\mathbf{h}}^2 + \sigma_{\mathbf{h}'}^2 + 2\sigma_{\mathbf{h}\mathbf{h}'}}.
$$

$$
\begin{aligned} \mathbf{\hat{h}} &= \text{Norm}(\mathbf{h}' + \mathbf{h}) \\ &= \frac{\mathbf{h}' + \mathbf{h} - \mu_{\mathbf{h}' + \mathbf{h}}}{\sigma_{\mathbf{h} + \mathbf{h}'}} \\ &= \frac{1}{\sigma_{\mathbf{h}' + \mathbf{h}}} (\mathbf{h}' + \mathbf{h}) \\ &= \frac{1}{\sqrt{\sigma_{\mathbf{h}}^2 + \sigma_{\mathbf{h}'}^2 + 2\sigma_{\mathbf{h}\mathbf{h}'}}} (\mathbf{h}' + \mathbf{h}) \end{aligned}
$$

$$
\begin{aligned} \mathbf{\hat{H}} &= \mathbf{B}^\intercal \mathbf{h}'^\intercal + \mathbf{H}' \\ &= \mathbf{B}^\intercal \mathbf{h}'^\intercal + \mathbf{A}_r \mathbf{H} \\ &= \mathbf{B}^\intercal \mathbf{h}'^\intercal + \mathbf{A}_r \mathbf{h}^\intercal \\ &= \frac{1}{\sqrt{\sigma_{\mathbf{h}}^2 + \sigma_{\mathbf{h}'}^2 + 2\sigma_{\mathbf{h}\mathbf{h}'}}} \mathbf{h}'^\intercal + \frac{1}{\sqrt{\sigma_{\mathbf{h}}^2 + \sigma_{\mathbf{h}'}^2 + 2\sigma_{\mathbf{h}\mathbf{h}'}}} \mathbf{h}^\intercal &= \mathbf{\hat{h}}^\intercal. \end{aligned}
$$

$$
\mathcal{HC}=\begin{pmatrix} \mathbf{0}_{1 \times 1} & \mathbf{1}_{1 \times n}\\ \mathbf{e}_1 & \mathbf{e}_{n\times n} \end{pmatrix},
$$

$$
\mathbf{h}_i^{k+1} = \mathbf{h}_j^{k+1}
$$

$$
\mathbf{h}^{k+1}=\sum_{i=1}^{n}(\mathcal{T}^{k\times n+i}(\mathbf{h}^{k}) + \mathbf{h}^k).
$$

$$
\mathcal{HC}^{\{ k \mid k-1 \equiv 0 \pmod{n} \}}= \begin{pmatrix} \mathbf{0}_{1\times 1} & \mathbf{e}_1^\intercal \\ \mathbf{1}_{n\times 1} & \mathbf{1}_{n\times n}, \end{pmatrix}
$$

$$
\mathcal{HC}^{\{ k \mid k-1 \equiv i \pmod{n}, i \neq 0 \}}= \begin{pmatrix} \mathbf{0}_{1\times 1} & \mathbf{e}_i^\intercal \\ \mathbf{e}_i & \mathbf{e}_{n\times n}, \end{pmatrix}.
$$

## 技术点深读（DEEP）

![[deep/hyper-connections]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/hyper-connections.txt`（82287 字符）供引用检索。