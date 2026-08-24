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

1）**核心对象**：在 OLMo-1B 上，绘制第 *i* 层输入 **h₀ⁱ** 与第 *i+1* 层输入 **h₀ⁱ⁺¹** 之间的余弦相似度（曲线为中位数，阴影为 5–95 分位数），横轴覆盖 1–32 层。Pre-Norm（红）全程维持在 ~0.90–0.95，分布带极窄；Hyper-Connection（蓝）在 ~0.55–0.80 间波动，且 5–95 分位数带明显更宽。

2）**关键结论**：Pre-Norm 相邻层输入高度相似，表明存在表征坍缩/重复，层间缺乏信息增益；扩展残差宽度后层间多样性显著恢复。

3）**链路作用**：作为动机图，定量暴露 Pre-Norm 缺陷，为提出多流 Hyper-Connection 提供立论依据。

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/hyper-connections-fig04.png]]
*整页渲染: ![[assets/hyper-connections-p05.png]]*
> [!quote] caption
> Sequential and parallel arrangements of hyper-connections with n = 2.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**核心对象与结构**：图4展示n=2时HC的两种拓扑。(a)顺序排列：底部输入经加法节点分两流进入layer 1，再堆叠进入layer 2，逐层输出；(b)并行排列：输入分流后分别经layer 1与直接路径，汇聚加和再分流入layer 2，末端带⊕合并输出。两者均含2条残差流与2个⊕聚合节点。

2）**论证的关键结论**：HC不仅兼容传统顺序堆叠（等价于残差网络），还能以并行多分支形式运行——即通过n=2同时维护两条独立残差路径并以加法融合，揭示其结构自由度。

3）**链路作用**：作为方法论核心可视化，奠定"多流残差优于单流"的拓扑基础，为后续ResNet/ViT/LLM实验中对比HC-n=2、4与baseline的增益提供结构层面的支撑。

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
> 【图文联合解读】**Figure 7 图文联合解读：**

1) **核心对象**：5个32×32的连接矩阵热力图（绿刻度标记奇数层即注意力层），色阶−1.0（蓝）至+1.0（红），对比Hyper-Connection、Post-Norm、Pre-Norm、Pre-Norm PTB、Two-hop Residual。Hyper-Connection呈现混合红蓝的非平凡模式（含PTB标记），Post-Norm为平滑红色三角，Pre-Norm/Pre-Norm PTB近乎全饱和深红，Two-hop Residual呈规则竖条状。

2) **论证结论**：Hyper-Connection习得了比四种基线更丰富、可学习、层间异构的连接模式（残差强度可正可负），突破了传统残差恒等约束。

3) **作用**：作为4.5节可视化分析，定性证明所提DHC方法相对基线的结构新颖性，与上方Table 7（DHC×4在MMLU 38.5→39.7、HellaSwag 69.5→70.2等全指标提升）形成"结构多样性→性能增益"的闭环论证。

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
> 【图文联合解读】**图文联合解读（≤220字）：**

图含28子图：12个验证集loss曲线（training、C4 en、dolma各子集、pile、wikitext103等）与16个下游任务accuracy曲线（MMLU 5子类、HellaSwag、SciQ、ARC、PIQA、WinoGrande、BoolQ、COPA等），对比OLMoE-1B-7B（红）与DHC×4（蓝）在500B tokens内的全程演化轨迹。**关键结论**：蓝线在全部12个验证loss上全程低于红线（差距约0.05–0.15），在全部16个下游accuracy上全程高于红线（如MMLU avg. ~1.5pp、HellaSwag ~2pp），一致胜出且差距稳定。**论文作用**：与图8定性架构对比、FLOPs开销表协同，定量证明DHC×4作为残差连接的替代具备跨领域、跨任务的普适增益，无明显退化任务，支撑其"即插即用"的工程定位。

### Figure 10 (p.18) ⭐深度解读
![[assets/crops/hyper-connections-fig10.png]]
*整页渲染: ![[assets/hyper-connections-p18.png]]*
> [!quote] caption
> Loss curves in V3 validation set and accuracy curves on downstream tasks for OLMo-7B and OLMo-7B-DHC×4 models. 18

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心对象与数据**：6×3 共 18 张子图，横轴均为训练 token 量（100–500B），红/蓝线分别代表 OLMo-7B 基线与 OLMo-7B-DHC×4。前 11 张为 V3 验证集（c4-en、dolma 子集 books/cc/pes2o/reddit/stack/wiki、ice、m2d2-s2orc、pile、wikitext-103）上的 loss 曲线，11 个数据集上 DHC×4 的 loss 始终低于基线（如 c4-en 500B 时约 2.47 vs 2.50，pile 约 2.04 vs 2.07）；后 7 张为下游任务准确率（HellaSwag、SciQ、COPA、OpenBookQA、PIQA、WinoGrande、ARC-Easy），DHC×4 在 SciQ 上领先约 2–3 个百分点（~92% vs ~89.5%），其余任务亦有 0.5–1 pp 的稳定优势。

2) **关键结论**：在 7B 规模、长程训练（500B tokens）下，宽度×4 的动态超连接（DHC）相对标准残差连接同时降低预训练 loss 并提升全部 7 项下游准确率，证明方法可扩展性。

3) **论文作用**：作为 DHC×4 扩展性实验的核心证据，支撑"超连接架构在大模型长程训练中仍有效"的主张，与 Table 10 共同构成方法稳健性验证链。

### Figure 11 (p.20) ⭐深度解读
![[assets/crops/hyper-connections-fig11.png]]
*整页渲染: ![[assets/hyper-connections-p20.png]]*
> [!quote] caption
> Training loss curves of ViT/16-Large and ViT/16-Large-DHC×2, smoothed using an

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图对比ViT/16-Large基线（红）与DHC×2（蓝）在约30k–93k训练步的loss曲线（EMA=0.999平滑）。两条曲线均从≈1.8降至≈0.20–0.25，DHC全程略低约0.05–0.10，但差距极小且随训练推进逐渐收敛。论文借此论证：超连接带来稳定但**有限且递减**的loss增益，源于多epoch对同一数据集的反复过拟合。在整体实验链路中，此图作为训练动力学的补充实证，与Table 11的ImageNet精度结论相呼应——说明HC的价值不在于大幅压低训练loss，而体现在精度端与表征质量上。

### Figure 12 (p.21) ⭐深度解读
![[assets/crops/hyper-connections-fig12.png]]
*整页渲染: ![[assets/hyper-connections-p21.png]]*
> [!quote] caption
> Distribution of weights of last DHC in ViT-Base/16-DHC×2 model. F MORE VISUALIZATION AND ANALYSIS

> [!tip] 技术解读（多模态）
> 【图文联合解读】**1) 核心对象**：7×3网格直方图，对应3个ImageNet类（33海龟、998 capitulum、779校车）的末层DHC权重（β₁、β₂及α分量）频次分布。

**2) 关键数据**：β₁、β₂呈双峰（≈0.95与1.20），类别差异显著——校车β₁集中于1.20（频次≈50），capitulum集中于0.95（频次≈45），海龟双峰并存；α₁,₀∈[-0.65,-0.35]、α₂,₀∈[2.0,2.4]。

**3) 结论与作用**：权重随输入类别自适应分化，印证DHC动态加权机制有效（非恒等残差），作为附录可视化支撑"输入依赖超连接"的核心理论主张。

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

1) **结构与数据**：表1以OLMo-1B基线（V2 Loss 2.811、Down Stream 62.5）为对照，比较DHC（Dynamic Hyper-Connections）在扩展率n∈{1,2,4,8}、有/无tanh激活下的表现。W/O tanh组中，n=8取得最优Loss/PPL（V3 PPL 13.819），n=4取得最优下游任务精度64.4；带tanh组n=4的V3 PPL为13.826，精度63.8。

2) **关键结论**：随n增大，困惑度单调下降但下游精度先升后降，n=4为综合最优权衡点；去除tanh普遍优于保留tanh，验证了tanh约束的非必要性。

3) **论文作用**：作为消融实验，为主方法OLMoE-1B-7B-DHC×4中n=4的超参选择提供实证依据，证明DHC扩展在适度规模下即可显著超越基线。

### Table 2 (p.7) ⭐深度解读
![[assets/crops/hyper-connections-tab02.png]]
> [!quote] caption
> Ablation study on static and dynamic hyper-connections with training on 500 B tokens.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心对象**：表 2 在 500B tokens 训练下对比 OLMo-1B 基线与静态超连接（SHC）、动态超连接（DHC）在扩展率 n=2、n=4 时的表现，指标含 V2/V3 Eval Loss、PPL 及下游平均准确率。

**数据要点**：所有 HC 变体均优于基线（62.5→64.4%）；相同 n 下，去除 tanh 的 DHC 反而全面优于原版 DHC；n=4 普遍优于 n=2，最优配置为 **DHC×4 W/O tanh**（V3 PPL 13.844、下游 64.4%）。

**技术结论**：实验验证"去掉 tanh 的动态超连接"为最佳设计。

**论文作用**：在消融实验中为最终动态超连接方案（去 tanh、n=4）的选型提供量化依据，是支撑方法设计的关键证据链。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/hyper-connections-tab03.png]]
> [!quote] caption
> Ablation study on OLMo-1B-DHC × 4. In the B or WC column, the symbol " ✗ " denotes parameters that are not trainable from initialization.

> [!tip] 表格解读（多模态）
> 【图文联合解读】1) 表3对OLMo-1B-DHC×4的WC（宽度连接矩阵）、B（偏置）、Tanh三组件做6组消融，对比V2/V3 Loss/PPL与下游平均准确率。最优配置WC✓+B✓+Tanh✗：V3 PPL 13.823，下游准确率64.4%；三组件全开下游反降为63.8%。

2) 论证：DHC各组件均有效，WC矩阵贡献最大（启WC下游+1.1%），B次之；Tanh非线性非必需，引入反而损害下游精度。

3) 该表作为方法验证的终点环节，承接Figure 3揭示的Pre-Norm层间坍缩动机，通过组件级消融为DHC最终方案（保留WC+B、剔除Tanh）提供定量选型依据。

### Table 4 (p.8) ⭐深度解读
![[assets/crops/hyper-connections-tab04.png]]
> [!quote] caption
> Performance of related methods on OLMo-1B models.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表为OLMo-1B上WC（宽度连接）、B（偏置）、Tanh三组件的消融实验，按V2/V3评测Loss-PPL与下游平均准确率分两区（共6组配置）。数据明确显示：开启WC即可将V2 Loss从2.804降至2.779、下游准确率由62.5跃至64.4；B仅在WC开启后带来微弱增益；引入Tanh反而劣化下游表现（63.8 vs 64.4）。论文借此论证**WC是Hyper-Connections性能的核心模块，B与Tanh为非必要冗余**，印证其"以最少结构换最大增益"的设计哲学，构成消融链路中支撑方法极简性与有效性的关键证据。

### Table 5 (p.9) ⭐深度解读
![[assets/crops/hyper-connections-tab05.png]]
> [!quote] caption
> Performance of 7B models. FLOPs refers to the computation per token in the forward pass.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 图文联合解读**

表5对比OLMo-7B基线与OLMo-7B-DHC×4在7B规模上的表现：两者参数量相同（均6.9B），FLOPs几乎不变（13.36G→13.38G，仅增0.02G），但DHC×4在V2 Loss（2.581→2.559）、V2 PPL（14.316→14.023）、V3 Loss（2.322→2.304）、V3 PPL（11.324→11.120）以及下游任务平均准确率（70.1→71.0）上全面胜出。该表用以证明：动态超连接（DHC）以几乎为零的额外计算开销（约0.15% FLOPs），即可同时改善预训练困惑度与下游任务表现。它是论文"以极小代价换性能"这一核心论点的7B级关键证据，与Figure 5的小规模曲线分析形成互补，从量化和质化两个层面共同支撑DHC的可扩展性与有效性。

### Table 6 (p.9) ⭐深度解读
![[assets/crops/hyper-connections-tab06.png]]
> [!quote] caption
> Downstream evaluations for MoE models training with 500B tokens under the OLMoE evaluation setting. ARC-C stands for ARC-Challenge, and ARC-E for ARC-Easy. MMLU Var is a modified version of MMLU that includes varying few-shot examples, providing stable feedback during early training, as outlined in 

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）Table 6对比OLMo-7B与OLMo-7B-DHC×4（同等6.9B参数、FLOPs≈13.37G）在500B tokens训练后的OLMoE下游评测结果：DHC×4在V2/V3 Loss与PPL上全面降低（V2 Loss 2.581→2.559；V3 PPL 11.324→11.120），任务平均准确率由70.1提升至71.0，参/算量几乎持平。

2）论证以n=4的超连接替换残差连接后，在不增加参数与计算的前提下，下游指标稳定提升（训练损失降约0.027，C4-en验证损失降约0.028）。

3）与Fig.6长程loss曲线、Fig.13–15消融共同构成递进实验证据链，从下游有效性到长程训练稳定性，端到端支撑"DHC隐式增宽/增深模型即提升性能"的核心主张。

### Table 7 (p.15) ⭐深度解读
![[assets/crops/hyper-connections-tab07.png]]
> [!quote] caption
> Comparison of number of parameters.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

表7对照展示了静态超连接(SHC)与动态超连接(DHC)在OLMo系列模型（含1B/7B等不同规模）上的参数开销。依据公式：|θ_SHC|=n(n+2)，|θ_DHC|=|θ_norm|+d_model(n+2)+n(n+2)+2。具体实例：OLMo-1B-SHC×4仅新增768个参数，OLMo-1B-DHC×4新增394,048个。该表与Table 8(FLOPs)互证，支撑"超连接引入的额外参数与计算开销均可忽略"这一核心结论，为方法在大规模预训练中的实用化部署扫除效率顾虑。

### Table 8 (p.16) ⭐深度解读
![[assets/crops/hyper-connections-tab08.png]]
> [!quote] caption
> FLOPs per token in forward pass.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 联合解读**

**① 核心对象与数据**：表展示各模型前向单 token 的 FLOPs，对比基线与加入 SHC/DHC（扩展率 n=2、4）的差异。OLMo-1B 基线 2.3536 G；SHC×2/×4 增量仅 +0.038%/+0.127%，DHC×2/×4 为 +0.076%/+0.200%。OLMo-7B 基线 13.3647 G，DHC×4 增 +0.147%；OLMoE-1B-7B 基线 2.3580 G，DHC×4 增 +0.208%。HC 自身 FLOPs 仅 0.0010–0.0197 G。

**② 论证结论**：相比基座数十亿参数，HC 引入的计算开销最大不足 0.21%，与参数开销（SHC 仅 n² 静态矩阵，DHC 主体为 d_model 窄投影）共同支撑"开销可忽略"论断。

**③ 论文作用**：属效率验证环节，为"以 HC 替换残差连接几乎零成本"提供关键量化证据，铺垫下游大规模实用化主张。

### Table 9 (p.16) ⭐深度解读
![[assets/crops/hyper-connections-tab09.png]]
> [!quote] caption
> Measured Memory Footprint on 8 GPUs.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 9 展示 OLMo-1B/7B/OLMoE-1B-7B 引入 SHC/DHC（×2、×4）后的实测开销：HC FLOPs 增量极小（如 OLMo-1B-DHC×4 仅 0.0049G，OLMo-7B-DHC×4 仅 0.0197G），总 FLOPs 增幅均 ≤0.208%（×2 时仅 +0.038%–+0.076%）。

关键结论：HC 以几乎可忽略的计算代价（<0.3%）即可嵌入模型；结合正文，n=2 时额外激活显存 <15% 标准 Transformer 总量，证实 HC 是轻量、即插即用的残差替代方案。

链路作用：继 Figure 8 架构定性对比后，以量化 FLOPs/显存数据打消读者对复杂度的顾虑，衔接下游任务实验，证明性能提升几乎"零成本"。

### Table 10 (p.19) ⭐深度解读
![[assets/crops/hyper-connections-tab10.png]]
> [!quote] caption
> Benchmarking class-conditional image generation on ImageNet 256 × 256, with cfg=1.50. NP , P , and R are short for Numerical Precision, Precision, and Recall, respectively.

> [!tip] 表格解读（多模态）
> 【图文联合解读】图像可辨。表在ImageNet 256×256、cfg=1.50下比较类条件生成：DiT-XL/2-SHC×2采用FP16、QK-Norm，参数仍为675M，FID/sFID为2.18/4.52，IS=287.24、P=0.82、R=0.60。同规模XL/2为2.36/4.54、269.46、0.83、0.58；983M模型为2.13/4.50、288.69、0.82、0.59。结果表明SHC不增参数即可改善质量与召回率并逼近1B模型；配合Figure 10，证明超连接在大模型跨任务训练中的扩展性与鲁棒性。

### Table 11 (p.19) ⭐深度解读
![[assets/crops/hyper-connections-tab11.png]]
> [!quote] caption
> Accuracy on ImageNet. ViT*/16 refers to the results reported by (Dosovitskiy et al., 2020), whereas ViT/16 denotes our re-implemented baseline. SHC and DHC indicate that residual connections are replaced with static and dynamic hyper-connections, respectively.

> [!tip] 表格解读（多模态）
> 【图文联合解读】注：图片顶部表格含FID/sFID/IS生成指标，属E.1 DiT实验，非Table 11本体。Table 11数据仅以正文叙述呈现：**ViT/16-Base（85M）**：基线76.38%，+SHC达77.60%（+1.22%），+DHC达77.26%（+0.88%）；**ViT/16-Large（307M）**：基线77.25%，+SHC达78.38%（+1.13%），+DHC达79.94%（+2.69%）。关键结论：超连接稳定提升分类精度，且DHC在大模型上增益最显著（+2.69%）。论文作用：与E.1生成实验互补，证明超连接在不同视觉任务与不同模型规模下的通用有效性与可扩展性。

### Table 12 (p.20) ⭐深度解读
![[assets/crops/hyper-connections-tab12.png]]
> [!quote] caption
> Training hyperparameters for ViT.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 12 解读**

1) **核心数据**：ViT 训练超参表，含 lr=0.003、Batch Size=4096、调度器为 Cosine Annealing + 10k 步线性 Warmup、Mixup(α=0.2)、300 epoch、AdamW(β1=0.9, β2=0.999, ε=1e−8)、梯度裁剪 1.0、Weight Decay=0.3、Dropout=0.1、bf16 精度。

2) **论证结论**：ViT 实验沿用成熟 ImageNet 训练配方（大 batch、长 epoch、cosine+warmup、强正则），证明 DHC 带来的增益来源于结构改进而非特殊调参，从而保证与基线 ViT 公平对比。

3) **链路作用**：作为附录的可复现性材料，支撑正文对 DHC 在 ViT-Base/16 等视觉骨干上性能与权重分布（图12）的实验结论，是论文"通用残差替代方案"主张在视觉域验证的实验基础。

### Table 13 (p.0) ⭐深度解读
![[assets/crops/hyper-connections-tab13.png]]
> [!quote] caption
> OLMo’s default configuration was evaluated using multiple metrics. Perplexity (PPL) and loss were used for the V2 and V3 Validation Sets, while zero-shot testing was applied to the Downstream Benchmarks. However, the grey benchmarks were excluded from our analysis due to the instability of their per

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心对象与结构**：Table 13 是 OLMo 默认配置的评测基准清单，分三组：13 个 V2 验证集（覆盖 4chan、c4_en、gab、ice、m2d2_s2orc/wiki、manosphere、pile、ptb、twitterAEE 等）、11 个 V3 验证集（Dolma 子集：books、common-crawl、pes2o、reddit、stack、wiki 及 c4_en、ice、pile、m2d2、wikitext103 等），以及 10 个 Downstream 零样本基准（piqa、hellaswag、winogrande、openbook_qa、sciq、arc_easy、copa、commitment_bank、mrpc、rte、sst2）。V2/V3 用 PPL 与 loss，下游用 zero-shot，灰色行因指标不稳定被剔除。

**技术结论作用**：为 DHC 与基线对比定义统一、多维度评测协议，确保跨语料域与跨推理任务比较的公平性。

**实验链路角色**：作为 Table 6 消融与 Fig.13–15 的配套表，提供"DHC 不增显式参数即可在长程训练下持续降低 loss、提升 zero-shot"的可复现多维证据，连接组件有效性至端到端训练有效性。

### Table 14 (p.31) ⭐深度解读
![[assets/crops/hyper-connections-tab14.png]]
> [!quote] caption
> Downstream Benchmarks for OLMoE.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 14 联合解读**

**1) 核心对象与数据结构**
该表列出 OLMoE（MoE 架构基线）所采用的 12 项下游评测基准，涵盖：常识/物理推理（piqa、hellaswag、winogrande、social_iqa、commonsense_qa）、QA 阅读（openbook_qa、sciq、boolq）、ARC 推理（arc_easy/arc_challenge、copa）及综合知识（mmlu）。当前裁图仅展示基准名称与文献引用列，主体分数列未在图中呈现，故量化结果须结合原文正文。

**2) 论证的技术结论**
论文以此套标准化基准，对应用 Dynamic Hyper-Connection（DHC）后的 OLMoE 进行零样本/小样本下游评测，验证超连接方案在 MoE 架构上的迁移有效性与通用性，与前期 OLMo 稠密模型实验形成互补。

**3) 在论文整体链路中的作用**
Table 14 属实验链路末端的"泛化性验证"环节：先以 OLMo-1B 证明 DHC 在稠密模型上的优势（Fig.14、Table 13 等），再以 OLMoE 证明其同样适用于稀疏专家架构，从而支撑"超连接是一种可即插即用的架构增强"这一核心论断。

### Table 15 (p.33) ⭐深度解读
![[assets/crops/hyper-connections-tab15.png]]
> [!quote] caption
> Results on downstream benchmarks for 1B models.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表15图文联合解读**

**1) 核心对象与数据**：以OLMo-1B（平均62.5）为基线，在7项下游任务（arc_easy/copa/hellaswag/openbook_qa/piqa/sciq/winogrande）上对比DHC/SHC变体在不同倍率n∈{1,2,4,8}及tanh/非trainable消融下的表现。最高分出现于**OLMo-1B-DHCx4 W/O tanh（64.4）**，较基线提升**+1.9**；DHCx4含tanh版本63.8次之。

**2) 关键论证结论**：①DHC普遍优于基线，验证超连接架构的迁移增益；②n=4为性价比最优配置，继续增大n收益不增；③冻结W或B后DHC仍超越基线，证明残差映射的必要性。

**3) 实验链路作用**：作为"下游任务泛化性"验证环节，与训练损失/困惑度分析互补，支撑论文关于超连接可作为残差连接即插即用替代的核心主张。

（注：所附引用段落实为Figure 15训练曲线说明，与本表内容不对应。）

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