---
paper_num: "9"
title: "JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting"
authors: "Decoding with Parallel Tree Drafting Lanxiang Hu1 Zhaoxiang Feng1 Yulun Wu2 Haoran Yuan3 Yujie Zhao1 Yu-Yang Qian4 Bojun Wang5 Peng Zhao4 Daxin Jiang5 Yibo Zhu5 Tajana Rosing1 Hao Zhang1 1UC San Diego 2 Zhejiang Universi"
date: "2026/6/16"
arxiv: "https://arxiv.org/abs/2606.18394"
pdf: "papers/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting.pdf"
slug: "jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting"
tags: [speculative]
---

# JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting

> [!abstract] 摘要（原文）
> 1\. 🚀 JETSPEC 提出了一种创新的因果并行草稿头部架构，通过在单一前向传播中生成具备分支因果依赖的候选树，有效解决了推测解码（Speculative Decoding）中因果性与效率之间的权衡矛盾。 2. 💡 该框架通过利用冻结目标模型的融合隐藏特征进行训练，确保了草稿概率分布与目标模型的自回归因子分解相一致，从而在增加草稿预算时显著提高了树结构的接受率。 3. 📈 实验表明，JETSPEC 在 Qwen3 等模型上能够将草稿预算高效转化为更长的接受前缀，在 MATH-500 等基准测试中实现了高达 9.64 倍的端到端解码加速，并能通过 vLLM 集成在真实服务负载下保持高性能。

## 元信息
- **发表日期**: 2026/6/16
- **作者**: Decoding with Parallel Tree Drafting Lanxiang Hu1 Zhaoxiang Feng1 Yulun Wu2 Haoran Yuan3 Yujie Zhao1 Yu-Yang Qian4 Bojun Wang5 Peng Zhao4 Daxin Jiang5 Yibo Zhu5 Tajana Rosing1 Hao Zhang1 1UC San Diego 2 Zhejiang Universi
- **arXiv**: https://arxiv.org/abs/2606.18394
- **本地 PDF**: `papers/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting.pdf`
- **页数**: 21

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig01.png]]
*整页渲染: ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p02.png]]*
> [!quote] caption
> End-to-end decoding speedup over standard autoregressive decoding on H100 GPUs across math, coding, and chat benchmarks. DFlash denotes the original block-parallel drafting method, DDTree is tree-based variant of DFlash, and JetSpec denotes our method. Both employ a tree budget of 256 tokens using Algorithm 1. acceleration. Despite these advances, head-based SD still faces a causality-efficiency d

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图1解读：**

该图以分组柱状图形式对比三种推测解码方法（DFlash蓝、DDTree橙、JetSpec绿）在四个基准上的端到端加速比。HumanEval：DFlash≈?.4×、DDTree 6.31×、JetSpec **7.12×**；MBPP：3.96/6.09/**6.73×**；LCB：4.70/6.75/**7.67×**；MT-Bench：2.72/4.26/**4.58×**。

原文借此论证两点结论：①树形草稿（DDTree、JetSpec）显著优于块并行草稿（DFlash），证明因果性-效率瓶颈可突破；②JetSpec在所有基准上均取得最高加速，尤其在HumanEval和LCB上较DDTree额外提升约0.6–0.9×。

该图作为开篇主结果图，确立了JetSpec并行树形草稿的SOTA地位，为后续方法详解和消融实验提供总体性能基线。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig02.png]]
*整页渲染: ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p03.png]]*
> [!quote] caption
> Expected speculative decoding speedup scales as a function of draft length γ, under different per-token drafting costs c and acceptance rates α. Comparing the two panels shows that reducing c substantially improves the scalability of speculative decoding with respect to γ, and increasing α further amplifies this effect. The results highlight that pushing per-token drafting cost c low and acceptanc

> [!tip] 技术解读（多模态）
> 【图文联合解读】图(a)横轴为对数刻度γ∈[2,256]，纵轴为加速比，在c=0.05条件下绘制6条曲线对应α=0.70~0.95。数据呈典型"先升后降"形态：α=0.95在γ=16处达~6.5×峰值，α=0.90峰值~4.6×(γ=16)，α=0.85峰值~3.7×(γ=8)，α=0.70仅在γ=2处~2.2×；γ>32后所有曲线骤降至<1.5×，在γ=256收敛至~0.5–1×。

论证结论：即便c已压至0.05，传统推测解码仍存在"加速比天花板"——单纯增大γ收益递减甚至恶化；必须**同时**降低每token起草成本c并提高接受率α才能突破。Table 12给出不同L、N下实测c值，为本图参数标定提供依据。

论文作用：作为Eq.(2)理论预测的可视化锚点，定量揭示传统推测解码γ扩展失效的瓶颈，为JetSpec以**并行树形起草**大幅降低c、从而突破天花板的核心动机提供关键支撑。

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig03.png]]
*整页渲染: ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p04.png]]*
> [!quote] caption
> JetSpec design overview. JetSpec extracts fused hidden features from the frozen target model and conditions a causal-parallel draft head to generate high-quality candidate trees in one forward pass.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**【核心对象】** 图示JetSpec三阶段流水线：①抽取冻结目标模型 $M_p$ 多层（Layer M…N）中间隐藏态，经Feature Fusion压缩为单条Fused Feature；②以"return"为anchor、γ个[init]为草稿槽，输入m层因果并行Draft Head $M_q$，单次前向产出7节点候选树（return为根，a(s=-0.51)/+(s=-2.48)/B(s=-4.05)/sum(s=-1.39)/b(s=-2.91)等分支）并配tree-causal注意力掩码矩阵；④BFS排序后回灌 $M_p$ 做tree-SD验证。

**【技术结论】** 草稿成本c被压至轻量head级，接受率α借中间层融合特征保持高位，破解c/α权衡，使加速比随γ单调上升。

**【链路作用】** 作为方法总览图，串联"特征抽取→并行树生成→tree验证"完整推理链，为后续实验论证加速上限提供架构依据。

### Figure 4 (p.15) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig04.png]]
*整页渲染: ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p15.png]]*
> [!quote] caption
> Tree-quality failure mode at MATH-500 prompt #0, decode step 0. Both heads draft from the same prefix (last token “We”). The causal head’s rank-1 branch (“ are told that”) is faithful: target joint Σ log p ≈Σ log r, so tree verification walks 6 tokens along it. The diffusion head’s rank-1 branch (“ given told that”) is incoherent (target joint Σ log p = −63.32 nats, i.e. probability ≈e−63) because

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图4对比因果头与扩散头从相同前缀"We"出发的草稿树质量。

**核心对象与数据：** 因果头rank-1分支"are told that"忠实（gap=−0.34），验证器接受6 token；扩散头rank-1分支"given told that"不连贯（gap=+42.50，目标联合概率≈e⁻⁶³），仅接受4 token；但扩散头rank-3分支（gap=−3.69）反而忠实。

**关键技术结论：** 扩散头采用分支无关的逐位预测器q_sur，将"given"(depth 1)与"told"(depth 2)独立组合——两者局部合理但全局不相邻，导致rank-1分支虽高概率却全局荒谬。即：树质量而非单一token概率才是speculative decoding扩展的真正瓶颈。

**论文作用：** 揭示并行树草稿在扩散头下的典型失败模式，论证JetSpec需要专门解决"局部合理、全局不连贯"的草稿质量问题，支撑其方法设计的必要性。

### Figure 5 (p.18) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig05.png]]
*整页渲染: ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p18.png]]*
> [!quote] caption
> Figure 5: Causal attention mask used for training with multiple sampled blocks. Each query can attend to the full verified prefix and to the anchor plus earlier positions within its own block, but cannot attend to future positions or positions from other sampled blocks. JETSPEC reuses intermediate representations from the frozen target model as draft-head context. For

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示注意力掩码矩阵，行=3 blocks × 6 query positions（anchor + 5），列=verified prefix（x₀–x₃）+ sampled blocks。**所有 query 对 verified prefix 全 ✓（黄色）**；仅 block 1 内部呈**左上三角因果掩码**——attend anchor a₁ 及更早位；block 2、3 对 block 1 列**全深紫遮蔽**，实现块间隔离。

该掩码直接支撑 JetSpec 的**并行树形 draft 训练机制**：使多个采样块在同一前向中并行计算的同时，仍保留块内自回归约束与块间独立性，避免长串行展开；从而把 draft 规模从线性扩展转为批量扩展，论证其打破 speculative decoding 缩放上限的核心技术结论。

### Figure 6 (p.19) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig06.png]]
*整页渲染: ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p19.png]]*
> [!quote] caption
> Each sampled block includes an anchor position and multiple future token positions. The anchor is retained as block context and excluded from the loss, while loss is applied only to future token positions within each block. allowing the causal draft head to condition on rich target-model features while keeping the target model frozen.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

图中展示 JetSpec 的**训练块采样结构**：每个 block 含 1 个 anchor（隐于上下文、无 loss）与多个 future token（带 loss），具体可见三行共 9 个标注 "loss" 的橙色块，索引形如 b_{i,j}（i=block 行号 1–3，j=块内位置 3–5），对应"predicted token position with loss"。

原文借此论证关键结论：通过 block-wise 采样把 anchor 留作上下文、仅对 future 位置施加 loss，使因果 draft head 能在**冻结目标模型**条件下，以目标模型特征为条件学习多 token 联合预测，从而支撑其并行树状 draft 的可扩展性，缓解传统 speculative decoding 的 scaling ceiling。

在整体链路中，此图属于**训练策略说明**模块，与 §3.3 的 draft head 设计衔接，为后续实验（墙钟加速比）提供方法论基础。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.7) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab01.png]]
> [!quote] caption
> Low-budget regime comparison of JetSpec and baselines trained with the same Qwen3-8B model and data recipe. We report results on math, coding, and chat benchmarks using non-thinking mode with a 3072 max tokens. We report end-to-end decoding speedup over standard AR decoding and average accepted leng

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文联合解读**

1) **核心数据**：基于 Qwen3-8B，在 7 个基准（GSM8K/MATH-500/AIME24/HumanEval/MBPP/LCB/MT-Bench）上对比 EAGLE-3、DFlash、JetSpec 三种方法在 Budget=16/32、温度 T=0 与 T=1 下的端到端加速比与平均接受长度 τ。低预算下 EAGLE-3 仅约 2.0×–2.4×；DFlash 与 JetSpec 普遍达 4×–6×；其中 JetSpec(B=32) 在多数任务上最优——T=0 时 MATH-500 达 6.35×、GSM8K 达 4.89×、HumanEval 达 4.29×，τ 同步最高（6.14、8.23、5.35）。

2) **关键结论**：JetSpec 在低预算（树规模小）条件下显著超越 head-based EAGLE-3，并在多数任务上击败 block-parallel DFlash/DDTree，证明其并行树草稿机制在有限预算下仍能维持高接受率与高加速。

3) **论文作用**：该表是实验链路中"低预算可行性"的核心证据，配合 Figure 1 高预算图，共同论证 JetSpec 打破了 SD 随预算缩放受限的天花板。

### Table 2 (p.7) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab02.png]]
> [!quote] caption
> High-budget comparison on Qwen3-8B with at least 64 draft tokens. EAGLE-3 uses tree mode with max depth 8; larger budgets give minimal or worse gains due to training mismatch.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表在Qwen3-8B上（batch 16/32，T=0/1，≥64 draft tokens）对比三方法加速比：EAGLE-3因训练失配最高仅约4.0×，预算增大几无收益；DFlash峰值7.83×（T=0，bs=16），但bs=32多列明显下滑；JetSpec在bs=32下多列加粗领先，T=0最高达8.23×、6.48×，T=1最高6.44×。结合Fig.2的速度公式（依赖c与α）与Tab.12的低c实测，论证"压低逐token草稿成本c并提升接受率α"可让加速随draft长度γ持续增长，从而打破EAGLE-3的扩展饱和，构成论文高预算场景下方法有效性的关键实证。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab03.png]]
> [!quote] caption
> Learning-rate ablation with J ET S PEC and without loss weighting training ( γ = 0 ). See Section 3.4.2 for γ ’s definition and ablations. We report speedup and average accepted length τ .

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表展示JetSpec在LR∈[5e-5, 1e-3]、γ=0无加权训练下的加速比与平均接受长度τ，分GSM8K/MATH-500两基准、对比SFT与Forward KL两种训练目标。数据呈倒U型：3×10⁻⁴为峰值（GSM8K SFT 5.79×/6.78；MATH-500 FK 8.29×/9.81），两端衰减；SFT与FK差异<0.2×几近重合；MATH-500加速峰值8.30×显著高于GSM8K的5.87×。论文借此论证：γ=0下Fig.3因果并行草稿头已获高接受率与强加速，验证设计有效性，并为后续γ消融与突破scaling ceiling提供训练基线。

### Table 4 (p.9) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab04.png]]
> [!quote] caption
> Loss-objective ablation with J ET S PEC at LR 6 × 10 − 4 and γ = 0 . We report speedup and average accepted length τ . All cells use checkpoints from a single training pipeline trained on math-only data ( ∼ 3 epochs); we report on math benchmarks to keep the comparison in-distribution.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读**

该表对比 JetSpec 在 LR=6×10⁻⁴、γ=0 时三种训练目标（SFT、Forward-KL Distill、Reverse-KL Distill）在四个数学基准（GSM8K/MATH-500/AIME25/AIME24）上的 speedup 与平均接受长度 τ。结果显示：**Forward-KL 与 SFT 持平略优**（如 MATH-500：8.46/10.01 vs 8.42/9.98），**Reverse-KL 全面退化**（如 GSM8K 仅 3.29/3.78，约为前者一半）。论文借此论证：训练 draft 模型应选 **Forward-KL 蒸馏**——其 mass-covering 特性保证高召回率与长接受序列；而 Reverse-KL 的 mode-seeking 易导致草稿早夭。该消融为 JetSpec 整体训练配方中损失函数的选择提供了关键实验依据。

### Table 5 (p.9) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab05.png]]
> [!quote] caption
> Model generalizability: JetSpec vs. DDTree on Qwen3-30B-A3B (MoE target), both trained with SFT on the same 800K-example data mixture as our Qwen3-8B main results. Each cell reports speedup / average accepted length τ at temperature 0 with tree budget 256 .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**1) 核心对象与数据**：表格对比 JetSpec 与 DDTree 在 Qwen3-30B-A3B（MoE）目标上的泛化表现，在 GSM8K / MATH-500 / AIME25 / AIME24 四个数学基准、tree budget 256、T=0 下报告 speedup 与 τ。JetSpec 加速 5.96–8.42×、τ 6.93–9.98；DDTree 加速 6.11–8.46×、τ 7.09–10.01；第三列基线仅 3.29–5.25×、τ 3.78–6.59，明显落后。

**2) 关键技术结论**：以 Qwen3-8B 主实验同款 800K SFT 数据训练，可成功迁移至 30B MoE 目标；JetSpec 与 DDTree 接受长度接近 10、加速达 5–8×，远胜基线，证明并行树状 draft 在 MoE 架构上仍然高效。

**3) 论文整体作用**：作为 generalizability 实验，验证 JetSpec 不仅适用于 dense 主结果模型，也可推广至 MoE 大模型，扩展其部署范围与方法适用边界。

### Table 6 (p.9) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab06.png]]
> [!quote] caption
> Training-data ablation: J ET S PEC vs. J ET S PEC -Corpus, both trained with SFT on the same 800K-example data mixture (Qwen3-8B target). JetSpec uses model-regenerated continuations as supervision targets; JetSpec -Corpus uses the original training corpus. Each cell reports speedup / average accept

> [!tip] 表格解读（多模态）
> 【图文联合解读】【对象与数据】图为 DDTree vs JetSpec 主结果对比表，而非 caption 所述 JetSpec–Corpus 训练数据消融；七列基准覆盖数学（GSM8K / MATH-500 / AIME25）、代码（HumanEval / MBPP / LCB）与对话（MT-Bench），每格 speedup / 平均接受长度 τ。DDTree 在 MATH-500 为 8.61 / 9.49、GSM8K 为 7.26 / 7.93；JetSpec 全面胜出：9.45 / 10.65、7.40 / 8.18，余项亦均略高。

【关键结论】JetSpec 全基准稳定超越当前最强基线 DDTree：数学域增益最显著（MATH-500 speedup +0.84、τ +1.16；AIME25 +0.34 / +0.57），代码与对话域增益较温和（+0.07 ~ +0.33）；τ 多接近甚至超过树深，并行草稿高接受率得到量化验证。

【论文作用】作为主结果表，定量支撑 "打破 speculative decoding scaling ceiling" 的核心论断；与 Figure 6 锚点–未来 token 块采样结构相呼应，共同证明 JetSpec 训练目标与解码策略在多域的有效性。

### Table 7 (p.9) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab07.png]]
> [!quote] caption
> compares causal and diffusion heads under different choices of γ , the parameter that controls how aggressively the DFlash training objective downweights per-position loss at positions far from each anchor token. Specifically, position i within a block contributes to the training loss with weight w 

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明**：所提供图片上方展示的并非 Table 7 本身（实为含 JetSpec/JetSpec-Corpus 的另一表格），Table 7 内容仅以正文段落形式出现于图片下方。以下依据原文段落对 Table 7 进行解读：

**1) 核心对象与结构**
Table 7 在不同 γ 值下比较 **causal head** 与 **diffusion head** 两种草稿头的推测加速比。γ 控制 DFlash 训练损失对远离 anchor token 位置的衰减权重，定义为 $w_i=\exp(-\max(i-i_{\text{anchor}},0)/\gamma)$；γ=0 退化为均匀加权。

**2) 关键技术结论**
- causal head 对 γ 不敏感，全区间表现稳健；
- diffusion head 对 γ 高度敏感，呈倒 U 形：γ=7 达峰值 **8.36×**，端点显著塌缩（γ=0 仅 5.46×，γ=15 为 6.17×）；
- 因此 γ=7 被确立为 DFlash 最优宏观损失加权设置。

**3) 在论文整体方法链路中的作用**
该消融为 3.4.2 节 "Tree Drafting with Diffusion Head" 的核心依据，证明扩散头搭配适度衰减（γ=7）方可释放并行树形草稿的并行潜力，是 JetSpec 突破线性 scaling 上限的关键设计前提，并直接被 Table 9 在 MATH-500 上的 rank-1 gap 分布进一步验证。

### Table 8 (p.15) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab08.png]]
> [!quote] caption
> extends Figure 4 to the full top- 5 branches of each head’s tree at MATH-500 prompt #0 , decode step 0 (root token “We” ). The pattern reported in the main text repeats throughout the tree. For the diffusion head, top- 2 and top- 4 both combine “ given ” at depth 1 and “ told ” at depth 2 with targe

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 表格对象与数据：** Table 8 扩展 Figure 4，展示 MATH-500 prompt #0、decode step 0（根 token "We"）处 diffusion head 与 causal head 各自的 **top-5 完整分支树**，逐 depth 给出 token、target joint（nats）与 gap 值。

**2) 关键技术结论：**
- **扩散头**：仅 rank-3（target joint −0.08）连贯；rank-2/4 共享 off-argmax "given"+"told" 组合，target joint 均 **< −50 nats** → 分布崩溃。
- **因果头**：仅 rank-1（" are told that"，gap **−0.34**）忠实；rank 2–5 一致继承 off-argmax depth-2 token "given"（非 rank-1 的 argmax "told"），depth 4–5 急剧退化（如 rank-3 "the2product" gap **+42.50**）。
- 二者共同印证 §A.4 的 **off-argmax inheritance**：每条分支 depth-*d* 的 marginal 被锚定到上一层的 argmax 延拓，因此非 argmax 分支继承了与其祖先 token **不匹配** 的条件上下文。

**3) 论文中的作用：** 作为案例证据，定量揭示 parallel tree drafting 随树规模扩大时缩放天花板（scaling ceiling）的根因——非 argmax 分支的条件错配累积导致 acceptance rate 衰减，从而支撑 JetSpec 用专用 diffusion-style head 重构 drafting 树的必要性。

### Table 9 (p.15) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab09.png]]
> [!quote] caption
> reports the rank- 1 gap distribution across MATH-500 prompts 0 – 49 for both heads at γ = 0 and at γ = 7 (DFlash’s best macroscopic loss-weighting setting, Table 7). At γ = 0 , the diffusion

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表以 MATH-500 前 50 条 prompt 为样本，逐条列出 draft head 与 target head 的 **rank-1 gap**（top-1 token 不一致度），并对比 γ=0 与 γ=7 两种宏观损失加权设定。

原文据此论证核心结论：**即使采用 DFlash 最优的宏观损失加权（γ=7）**，diffusion-style draft head 在 rank-1 上仍与 target head 存在**显著、普遍**的差距，即单 token 草稿的接受率有结构性瓶颈，仅靠损失加权不足以弥合二者的 top-1 失配。

在论文链路中，该表为 JetSpec 提出 **并行树形草稿（parallel tree drafting）** 提供关键经验依据：既然单点采样难以命中 target，说明必须通过多分支并行生成候选树来提升草稿命中率，从而突破 speculative decoding 的 scaling ceiling。

### Table 10 (p.18) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab10.png]]
> [!quote] caption
> Tree-construction algorithm ablation on MATH-500 ( n = 500 ) with JetSpec at the pro- duction setting (causal head, LR 3 × 10 − 4 , Forward-KL distillation, γ = 0 ). Hybrid scoring is P

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表消融JetSpec在MATH-500上的树构建打分策略，比较Speedup与平均接受长度τ。纯熵引导最差（4.76/5.52）；累积对数概率（默认）达8.15/9.81；混合∑log rᵢ+α·Hᵢ在α=0.25时最优（8.27/9.81），且随α增大单调下降至α=8.0的7.42/9.00。结论：以对数概率为主、熵仅做小幅正则即可，默认配置近似最优，证明JetSpec并行树草稿中token级置信度排序是关键，而非依赖深度级不确定性；该消融为生产配置选择提供了闭环验证。

### Table 11 (p.20) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab11.png]]
> [!quote] caption
> vLLM serving performance of J ET S PEC on Math-500 with Qwen3-8B on a single H100 GPU, evaluated across batch sizes and tree budgets (in parentheses). Each setting reports end-to-end throughput over AR decoding in tokens per second (TPS).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读**

表11测量JetSpec在Qwen3-8B/单H100/Math-500上的端到端TPS，按batch(1–16)与树预算(16/32/64/128)交叉。结果：小batch时预算越大越好（batch=1，预算128达553.3 TPS，4.33×）；batch≥8后预算32最优（batch=16达1094.6 TPS，3.81×），预算128反降至2.80×。原文借此论证：树预算与batch强耦合——低batch靠大预算减少验证轮次降延迟，大batch时验证与显存开销反客为主，相对增益递减。作为"打破扩展天花板"主张的核心实测支撑，该表说明JetSpec在真实vLLM服务中需按负载自适应选择树预算，方获最优吞吐，呼应论文"并行树草稿→按需预算"的设计闭环。

### Table 12 (p.21) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab12.png]]
> [!quote] caption
> Per-draft-token drafting cost ratio c = T draft / ( N T verify ) (%) on a single H200 NVL GPU, sweeping context length L and draft depth N . This is the cost coefficient used in Eq. equation 2 and Fig. 2. Lower is better.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1）核心对象与数据：** 该表为每个 draft token 的成本系数 c = T_draft/(N·T_verify) (%)，行扫描上下文长度 L∈{128,256,512,1024,2048,4096}，列扫描草稿深度 N∈{1,2,4,…,512}。定量看：N=1 时 c≈15.0%；N=512 时 c 仅 ≈0.034%（L=128）。固定 L 后，c 几乎随 N 翻倍而减半，呈近似 1/N 规律；L 从 128 到 2048 各列数值高度稳定，L=4096 整体上浮约 20%（如 N=1 升至 18.295%）。

**2）关键技术结论：** c 随 N 增大而趋近于零，说明并行树形草稿（parallel tree drafting）每额外分支的边际成本几乎可忽略，从硬件层面证实 JetSpec"草稿可并行化、可深可宽"的论断，突破了传统 speculative decoding 因串行草稿开销而限制草稿深度的天花板。

**3）论文中的作用：** 该 c 代入 Eq. 2 推导 JetSpec 理论加速比，并支撑 Fig. 2 的趋势曲线；是连接"草稿算法设计"与"端到端加速效果"的关键实测参数。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbb{E}[\#\mathrm{tokens}] = \frac{1-\alpha^{N+1}}{1-\alpha},
$$

$$
\mathrm{Speedup} = \frac{1-\alpha^{N+1}} {(1-\alpha)(N c + 1)}.
$$

$$
q_{\mathrm{sur}}(y_{1:k}\mid x) \propto \prod_{i=1}^{k} r_i(y_i\mid x),
$$

$$
p(y_{1:k}\mid x) = \prod_{i=1}^{k} p(y_i \mid x, y_{<i}).
$$

$$
M_{v,u} = \begin{cases} 0, & \text{if } u \in \mathrm{Anc}(v)\cup\{v\}, \\ -\infty, & \text{otherwise}, \end{cases}
$$

$$
\mathrm{Attn}(Q_v,K,V) = \mathrm{softmax} \left( \frac{Q_vK^\top}{\sqrt{d}} + M_v \right)V.
$$

$$
q(\pi(v)\mid x) = \prod_{u\in \pi(v)} q(y_u \mid x, h_x^{o}, \pi_{<u}),
$$

$$
\mathcal{L}_{\mathrm{FKL}}^{(m)} = D_{\mathrm{KL}} \left( \tilde{p}^{(m)} \,\middle\|\, \tilde{q}^{(m)} \right).
$$

$$
\mathcal{L}_{\mathrm{train}} = T_{\mathrm{KD}}^2 \frac{ \sum_m w_m \mathcal{L}_{\mathrm{FKL}}^{(m)} }{ \sum_m w_m },
$$

$$
s(\pi(v)) = \sum_{u\in \pi(v)} \log q(y_u \mid x, h_x^o, \pi_{<u}),
$$

$$
A_t \sim \mathrm{Bernoulli}(\alpha_t), \qquad \alpha_t = \alpha\!\left( y_t;\, q(\cdot\mid x,y_{<t}), p(\cdot\mid x,y_{<t}) \right),
$$

$$
\alpha_t = \min\!\left( 1,\, \frac{ p(y_t\mid x,y_{<t}) }{ q(y_t\mid x,y_{<t}) } \right),
$$

$$
c(N,L) = \frac{T_{\mathrm{draft}}(N,L)/N} {T_{\mathrm{verify}}(N,L)} = \frac{T_{\mathrm{draft}}(N,L)} {N\,T_{\mathrm{verify}}(N,L)}.
$$

## 相关论文

- [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] — LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and Verification
- [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] — DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation
- [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] — SpecExtend: A Drop-in Enhancement for Speculative Decoding of Long Sequences
- [[dflash-block-diffusion-for-flash-speculative-decoding]] — DFlash: Block Diffusion for Flash Speculative Decoding
- [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] — MEDUSA: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads
- [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]] — EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees

## 技术点深读（DEEP）

![[deep/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting.txt`（70018 字符）供引用检索。