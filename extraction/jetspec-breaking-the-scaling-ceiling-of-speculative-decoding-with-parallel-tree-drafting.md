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
> 【图文联合解读】**图文联合解读**

该图为分组柱状图，在 H100、tree budget=256 条件下，对 DFlash（蓝）、DDTree（橙）、JetSpec（绿）三种方法在 7 个基准（数学 GSM8K/MATH-500/AIME25、代码 HumanEval/MBPP/LCB、对话 MT-Bench）上对比标准 AR 解码的端到端加速比。

**量化结果**：JetSpec 在所有基准均最优——GSM8K 7.82×、MATH-500 9.64×（全图峰值）、AIME25 8.78×、HumanEval 7.12×、MBPP 6.73×、LCB 7.67×、MT-Bench 4.58×；DDTree 次之，DFlash 最弱（如 MATH-500 仅 6.12×）。

**论证结论**：相较 DFlash 块并行草案，树结构带来大幅提升（DDTree 普遍多 2–3×），而 JetSpec 在树草案之上再叠加 JetLinear 等优化，相对 DDTree 仍稳定再增约 0.3–1×，证明其打破了缩放天花板。

**论文作用**：作为开篇 headline 实验图，确立 JetSpec 跨领域通用且最优的性能定位，为后续方法与低预算分析提供高预算下的对照基线。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig02.png]]
*整页渲染: ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p03.png]]*
> [!quote] caption
> Expected speculative decoding speedup scales as a function of draft length γ, under different per-token drafting costs c and acceptance rates α. Comparing the two panels shows that reducing c substantially improves the scalability of speculative decoding with respect to γ, and increasing α further amplifies this effect. The results highlight that pushing per-token drafting cost c low and acceptanc

> [!tip] 技术解读（多模态）
> 【图文联合解读】The user wants me to analyze Figure 2 from the JetSpec paper, combining the image content with the paper's text. Let me carefully read the chart.

Figure 2 shows two panels comparing expected speculative decoding speedup as a function of draft length γ (x-axis, from 2 to 256), with different acceptance rates α (0.70 to 0.95) and different per-token drafting costs c.

Left panel (a): Typical SD with c = 0.05
- Y-axis: Expected speedup from ~0 to 7
- Acceptance rates: 0.70, 0.75, 0.80, 0.85, 0.90, 0.95
- All curves peak around γ = 16, then decline
- Peak values: α=0.95 peaks at ~6.5, α=0.90 at ~4.6, α=0.85 at ~3.7, α=0.80 at ~3.1, α=0.75 at ~2.7, α=0.70 at ~2.3
- At γ=256, most curves drop below 1

Right panel (b): Ultra low-cost SD with c = 0.0005
- Y-axis: Expected speedup from 0 to ~20
- Same acceptance rates
- Curves continue to grow longer, peaking around γ = 64-128
- Peak values: α=0.95 reaches ~18-19, α=0.90 at ~9.5, α=0.85 at ~6.5, α=0.80 at ~5.5, α=0.75 at ~4, α=0.70 at ~3.3
- At γ=256, curves still remain high

The key insight: reducing c (drafting cost) extends the scalability ceiling of γ significantly, and higher α amplifies this effect.

Now I need to write a Chinese interpretation in ≤220 characters covering:
1) Core object/structure of the figure (specific, quantified)
2) Key technical conclusion from the paper
3) Role in the overall paper

Let me count characters carefully. I need to be concise.

Let me draft:

图2展示期望推测解码加速比随草稿长度γ（2–256）的变化，分两面板对比草稿成本c=0.05（典型）与c=0.0005（超低）下的表现，每条曲线对应不同接受率α（0.70–0.95）。左图加速比在γ≈16处达峰后骤降（最高≈6.5，α=0.95），右图则持续增长至γ≈64–128（最高≈18）。论文借此论证：降低每token草稿成本c可大幅提升γ的可扩展性，提高α进一步放大该效应，从而引出JetSpec通过并行树状草拟实现超低c的动机。

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig03.png]]
*整页渲染: ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p04.png]]*
> [!quote] caption
> JetSpec design overview. JetSpec extracts fused hidden features from the frozen target model and conditions a causal-parallel draft head to generate high-quality candidate trees in one forward pass.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**核心对象与结构**：JetSpec 三步流水线架构图。①**特征提取**：从冻结目标模型 M_p 的 M~N 层隐藏态，经 Feature Fusion 生成融合特征向量；②**并行树状草稿生成**：融合特征与 Anchor 令牌（return）+ 3 个 Draft Slots 输入 m 层因果并行 Draft Head M_q，单次前向生成候选树——根节点 s=-0.51，分叉至 a(+)、b、+、B 等子节点，每个带独立置信分（如 s=-0.87、-1.56、-2.48）；③**树验证**：冻结 M_p（L~N 层冻结，❄标识）配合 tree-causal attention mask，对候选树打分并产出 step i+1 的已验证 token（return, a, +, b）。

**论证的技术结论**：通过提取并融合目标模型多层隐藏态作为条件，配合因果并行头，可在一轮前向中产出多分支候选树（含具体得分），从而打破传统串行 speculative decoding 的缩放上限。

**论文链路作用**：作为方法总览图，串联"特征融合—并行草稿—树验证"三阶段，是 JetSpec 区别于 EAGLE/Medusa 等序列式草案方法的核心理论框架支撑，后续 Table 3 的消融即在该流水线上验证学习率等训练超参影响。

### Figure 4 (p.15) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig04.png]]
*整页渲染: ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p15.png]]*
> [!quote] caption
> Tree-quality failure mode at MATH-500 prompt #0, decode step 0. Both heads draft from the same prefix (last token “We”). The causal head’s rank-1 branch (“ are told that”) is faithful: target joint Σ log p ≈Σ log r, so tree verification walks 6 tokens along it. The diffusion head’s rank-1 branch (“ given told that”) is incoherent (target joint Σ log p = −63.32 nats, i.e. probability ≈e−63) because

> [!tip] 技术解读（多模态）
> 【图文联合解读】图(a)因果头 γ=0：rank-1 分支"are told that" gap=−0.34 忠实→验证接受 6 tokens；rank-3 分支 gap=+42.50 被拒。图(b)扩散头 γ=0：rank-1"given told that"联合概率≈e⁻⁶³、gap=+59.56 不连贯，仅接受 4 tokens；忠实分支"are given that the"反居 rank-3（gap=−3.69）。该图揭示扩散头的"排序错位"失败模式——高保真草稿被埋没、验证沿错置的 rank-1 路径短走，直接论证 JetSpec 引入 γ>0、以 Gumbel 噪声重排使优质分支升至 rank-1 的核心设计动机，是论文并行树草稿方法链路中说明 γ 参数必要性的关键定性证据。

### Figure 5 (p.18) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig05.png]]
*整页渲染: ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p18.png]]*
> [!quote] caption
> Figure 5: Causal attention mask used for training with multiple sampled blocks. Each query can attend to the full verified prefix and to the anchor plus earlier positions within its own block, but cannot attend to future positions or positions from other sampled blocks. JETSPEC reuses intermediate representations from the frozen target model as draft-head context. For

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图5展示JetSpec训练多采样块的因果注意力掩码（3×3块状矩阵）：键值序列为4 token已验证前缀(x₀₋₃) + 3个采样块（每块1锚点a+5草稿b，总长18）；查询按6+6+6排列。黄色=可关注，紫色=屏蔽。规则为：所有查询可全访前缀；块内q_{i,j}仅见a_i及b_{i,≤j}（因果下三角）；跨块完全隔离。该设计保证每块独立自回归预测，避免相互"偷看"，并复用目标模型中间表征作为草稿头上下文，从而支撑Table 5中JetSpec相对DDTree在Qwen3-30B-A3B（MoE）上τ加速比的优越性，验证并行树起草的可扩展性。

### Figure 6 (p.19) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig06.png]]
*整页渲染: ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p19.png]]*
> [!quote] caption
> Each sampled block includes an anchor position and multiple future token positions. The anchor is retained as block context and excluded from the loss, while loss is applied only to future token positions within each block. allowing the causal draft head to condition on rich target-model features while keeping the target model frozen.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心对象与结构**：图示"Block-wise supervision for sampled training blocks"，共 3 个块（Block 1–3），每块由 1 个 anchor（a_i，白色，标注"no loss"）与 5 个未来 token 位置（b_{i,1}–b_{i,5}，橙色，标注"loss"）构成，即 1:5 的锚点-预测配比；监督仅施加于橙色位置。

2) **关键技术结论**：该 block-wise 监督机制使因果 draft head 能以 anchor 携带的目标模型特征作为上下文条件进行预测，同时保持目标模型冻结不变，从而支撑"并行树状草稿 + 冻结目标"的训练范式。

3) **论文整体作用**：作为 JetSpec 训练链路的核心监督方案，为后续 Table 6 中 JetSpec 与 JetSpec-Corpus 的消融对比、以及整体 speedup / accept-rate 增益提供训练侧的算法基础。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.7) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab01.png]]
> [!quote] caption
> Low-budget regime comparison of JetSpec and baselines trained with the same Qwen3-8B model and data recipe. We report results on math, coding, and chat benchmarks using non-thinking mode with a 3072 max tokens. We report end-to-end decoding speedup over standard AR decoding and average accepted leng

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表在Qwen3-8B低预算（budget=16/32）下对比JetSpec、DFlash、EAGLE-3于7个基准（GSM8K、MATH-500、AIME25、HumanEval、MBPP、LCB、MT-Bench）的AR端到端加速比与平均接受长度τ。JetSpec（budget=32）近乎全线最优：GSM8K 4.89×、MATH-500 6.35×（τ=8.23）、HumanEval 4.29×、LCB 4.86×。对比DFlash，随预算增大反而退化（GSM8K 4.80→4.21、MATH-500 6.12→5.39），而JetSpec持续提升。该表直接验证JetSpec突破了DFlash式并行树草稿的"缩放天花板"，是论文核心主张的主要实证支撑。

### Table 2 (p.7) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab02.png]]
> [!quote] caption
> High-budget comparison on Qwen3-8B with at least 64 draft tokens. EAGLE-3 uses tree mode with max depth 8; larger budgets give minimal or worse gains due to training mismatch.

> [!tip] 表格解读（多模态）
> 【图文联合解读】# Table 2 图文联合解读

**1) 核心对象与数据：** 该表在 Qwen3-8B 上对比 EAGLE-3、DFlash、JetSpec 三种推测解码方法在 **≥64 draft tokens 高预算**下的加速比，分为 Temperature=0 与 Temperature=1 两块，每行覆盖预算分支因子（16/32）下的 12 项数据。EAGLE-3 加速比多在 **1.8–4.0×** 区间封顶（budget 32 仅 2.04–4.03）；DFlash 中位 ~4–6×；**JetSpec（32）则多项达到 6.14、6.35、6.48、8.23×**，且 budget 由 16→32 普遍进一步提升。

**2) 关键技术结论：** EAGLE-3 因训练与部署预算不匹配（max depth=8）存在"训练失配"，增大预算收益停滞甚至下降；JetSpec 通过**并行树形草稿**在训练时即匹配高预算树结构，从而**打破缩放天花板**，在高预算下显著超越 EAGLE-3 与 DFlash，呼应 Figure 2 所揭示的"低 drafting cost c + 高接受率 α 才可随 γ 持续放大"的规律。

**3) 在论文中的位置：** 该表是论文的高预算消融/对照实验，**实证支撑 Figure 2 的理论分析**，并与全文论证链路呼应——从图 2 的 scaling 理论 → 表 2 的高预算实测 → 证明 JetSpec 的并行树草稿真正消除了先前方法（EAGLE-3/DFlash）的可扩展性瓶颈。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab03.png]]
> [!quote] caption
> Learning-rate ablation with J ET S PEC and without loss weighting training ( γ = 0 ). See Section 3.4.2 for γ ’s definition and ablations. We report speedup and average accepted length τ .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 联合解读：**

1) **结构与数据**：表展示 JetSpec 在 γ=0（无 loss weighting）下，5 个学习率（5e-5、1e-4、3e-4、6e-4、1e-3）× 2 个训练目标（SFT 与 Forward KL）× 2 个基准（GSM8K、MATH-500）的消融，报告 Speedup 与平均接受长度 τ。峰值集中于 LR=3e-4：GSM8K SFT 5.79/τ=6.78、Forward KL 5.92/τ=6.87；MATH-500 SFT 8.30/τ=9.80、Forward KL 8.29/τ=9.81。LR 过小（5e-5）效果最差（MATH-500 仅 7.27），过大（1e-3）略有回落。

2) **关键结论**：①最优 LR 约为 3e-4，呈非单调钟形曲线；②在多数 LR 与基准上，Forward KL 训练目标均稳定优于 SFT，证明其作为目标函数选择的合理性；③τ 与 Speedup 高度一致，表明接受长度是加速的核心驱动量。

3) **作用**：为正文中 JetSpec 主实验的 LR（3e-4）与训练目标（Forward KL）超参选择提供消融依据，验证其在不同基准上的稳健性。

### Table 4 (p.9) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab04.png]]
> [!quote] caption
> Loss-objective ablation with J ET S PEC at LR 6 × 10 − 4 and γ = 0 . We report speedup and average accepted length τ . All cells use checkpoints from a single training pipeline trained on math-only data ( ∼ 3 epochs); we report on math benchmarks to keep the comparison in-distribution.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读：**

**1) 核心对象与结构数据：** 表 4 对比 JetSpec 在固定学习率 6×10⁻⁴、γ=0 条件下，三种损失目标（SFT、Forward-KL Distill、Reverse-KL Distill）在四个数学基准（GSM8K、MATH-500、AIME25、AIME24）上的 speedup 和平均接受长度 τ。Forward-KL 在 GSM8K 上达 6.11/7.09，MATH-500 上 8.46/10.01，AIME25 上 7.56/9.40，AIME24 上 8.00/9.70，与 SFT 基本持平或略优；Reverse-KL 则全面崩塌（GSM8K 仅 3.29/3.78，MATH-500 仅 5.25/6.59）。

**2) 关键结论：** 模式覆盖型 Forward-KL 蒸馏是 JetSpec 树形 draft 训练的正确选择，能保留目标联合分布的 mass；模式收敛型 Reverse-KL 因过度集中于单一分支导致 draft 树质量骤降，速度比近乎腰斩。

**3) 在论文中的作用：** 该表属于消融实验环节，与 Figure 4 的失败案例互为佐证，共同锁定 JetSpec 训练损失必须采用 Forward-KL，排除 Reverse-KL，为后续主实验提供损失函数设计依据。

### Table 5 (p.9) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab05.png]]
> [!quote] caption
> Model generalizability: JetSpec vs. DDTree on Qwen3-30B-A3B (MoE target), both trained with SFT on the same 800K-example data mixture as our Qwen3-8B main results. Each cell reports speedup / average accepted length τ at temperature 0 with tree budget 256 .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读**

1) **表格结构与数据**：表5以Qwen3-30B-A3B（MoE目标模型）为评测对象，对比JetSpec与DDTree在GSM8K、MATH-500、AIME25、AIME24四个数学基准上的表现（温度0，树预算256，每格报告speedup/τ）。可见三列数据中，JetSpec速度提升达5.96–8.46×、τ达6.93–9.98；DDTree仅3.29–5.25×、τ 3.78–6.59；中间列在MATH-500上τ高达10.01，整体性能最佳。

2) **关键技术结论**：在MoE目标上JetSpec相较DDTree实现约1.6–2×的speedup优势与近2倍τ提升，验证了并行树草稿机制对稀疏激活MoE同样有效，且加速比从稠密模型扩展到MoE并未衰减。

3) **论文整体作用**：此表是"模型泛化性"实验核心证据，证明JetSpec并非仅适配稠密Qwen3-8B，而是具备跨架构（dense→MoE）、跨规模的可迁移性，强化了方法作为通用投机解码方案的论证。

### Table 6 (p.9) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab06.png]]
> [!quote] caption
> Training-data ablation: J ET S PEC vs. J ET S PEC -Corpus, both trained with SFT on the same 800K-example data mixture (Qwen3-8B target). JetSpec uses model-regenerated continuations as supervision targets; JetSpec -Corpus uses the original training corpus. Each cell reports speedup / average accept

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表对比 JetSpec 与 JetSpec-Corpus 在 Qwen3-8B、6 基准、3 预算（16/64/256）下的 speedup/平均接受长度τ。JetSpec 全面领先：budget=16 时 2.68–5.78 vs 1.54–2.75；budget=256 时 4.58–8.78 vs 2.63–4.42，加速比提升约 2–3 倍。

原文论证：用目标模型再生续写作监督目标至关重要，原始语料造成分布失配，再生样本使草稿贴合目标分布，显著提升接受率与加速比，验证数据策略对 speculative decoding 的决定性。

该表是训练数据消融核心证据，与 Figure 6 块采样损失共同支撑"训练侧决定 speculative decoding 上限"的主张，闭环验证 JetSpec 有效性。

### Table 7 (p.9) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab07.png]]
> [!quote] caption
> compares causal and diffusion heads under different choices of γ , the parameter that controls how aggressively the DFlash training objective downweights per-position loss at positions far from each anchor token. Specifically, position i within a block contributes to the training loss with weight w 

> [!tip] 表格解读（多模态）
> 【图文联合解读】图中上方为JetSpec/JetSpec-Corpus的另一表，Table 7本体未呈现，仅有其正文说明：它比较不同γ下的causal与diffusion head；块内位置i的权重为 \(w_i=\exp[-\max(i-i_{anchor},0)/γ]\)，γ=0表示均匀加权。扩散头对γ敏感：γ=0、7、15时加速分别为5.46×、8.36×、6.17×，γ=7最佳；causal头则较稳定。该消融说明衰减强度需折中，并为扩散头训练及后续树状草稿扩展提供参数依据。

### Table 8 (p.15) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab08.png]]
> [!quote] caption
> extends Figure 4 to the full top- 5 branches of each head’s tree at MATH-500 prompt #0 , decode step 0 (root token “We” ). The pattern reported in the main text repeats throughout the tree. For the diffusion head, top- 2 and top- 4 both combine “ given ” at depth 1 and “ told ” at depth 2 with targe

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 图文联合解读**

**① 核心对象与数据**：列出 MATH-500 prompt #0、step 0 处 Causal 与 Diffusion 两 head 各 top-5 分支的 token 序列、Σlog r（surrogate）、Σlog p（target）、Δ（nats）。surrogate 高度聚集（causal -3.88~-4.01，diffusion -3.76~-3.87），而 target 跨度极大（causal -3.54~-49.71；diffusion -0.08~-96.44）；diffusion 端 Δ 多在 +47~+92.57，唯 rank 3（"are given that the"）Δ=-3.69 与 target 吻合最佳，causal rank 1 Δ=-0.34 几乎贴合，但 rank 2-5 仍 +7~+45 偏离。

**② 关键结论**：两 head 的 surrogate log-r 都不能精确复现 target joint；diffusion head 失真更严重，整体呈系统性高估，仅个别分支碰巧接近 target。

**③ 论文作用**：作为 Figure 4 的全分支扩展，定量印证"现有 head surrogate 不足以驱动并行树 drafting"，论证 JetSpec 须显式对齐 target 并设计新校正机制的必要性。

### Table 9 (p.15) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab09.png]]
> [!quote] caption
> reports the rank- 1 gap distribution across MATH-500 prompts 0 – 49 for both heads at γ = 0 and at γ = 7 (DFlash’s best macroscopic loss-weighting setting, Table 7). At γ = 0 , the diffusion

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图像无法呈现表格具体数值（仅显示 caption 与小节标题），以下基于原文论述解读：**

1) **核心对象**：Table 9 展示在 MATH-500 提示 0–49 上，对扩散头在 γ=0 与 γ=7（DFlash 最佳宏观损失加权）两种设置下的 rank-1 gap 分布，用于逐题刻画并行树形草稿与目标模型 top-1 token 的偏差。

2) **关键结论**：γ=0 时扩散头 gap 偏大/分布不均，削弱并行潜力；γ=7 的适度衰减使 rank-1 gap 分布更紧凑，验证扩散头需配合合适衰减才能释放并行树形草稿的吞吐优势，是突破线性 scaling 上限的前提。

3) **链路作用**：作为 3.4.2 节"Tree Drafting with Diffusion Head"的消融实证，与 Table 7 的宏观加权搜索、Section 3 的并行树形草稿设计形成"宏观调参→逐题分布验证"的闭环，支撑 JetSpec 整体方法论。

### Table 10 (p.18) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab10.png]]
> [!quote] caption
> Tree-construction algorithm ablation on MATH-500 ( n = 500 ) with JetSpec at the pro- duction setting (causal head, LR 3 × 10 − 4 , Forward-KL distillation, γ = 0 ). Hybrid scoring is P

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表10图文联合解读**

表10在MATH-500(n=500)上对JetSpec的树构建算法做消融，对比三种策略的两项指标：①累积log-prob（默认）取得加速**8.15×**、平均接受长度τ=9.81；②纯熵引导严重退化至**4.76×**/5.52；③混合评分Σᵢlog rᵢ+α·Hᵢ扫描α∈{0.25,0.5,1,2,4,8}，α=0.25时达最优**8.27×**/9.81，随后随α增大单调劣化，α=8.0降至**7.42×**/9.00。

论文借此论证：累积log-prob评分已接近最优，小权重熵正则带来边际增益，熵主导则显著损害接受长度。该消融验证了默认树构造策略的合理性，为生产配置中的组件选择提供实证支撑，是"推理时并行树结构设计"实验链路中关键的设计依据。

### Table 11 (p.20) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab11.png]]
> [!quote] caption
> vLLM serving performance of J ET S PEC on Math-500 with Qwen3-8B on a single H100 GPU, evaluated across batch sizes and tree budgets (in parentheses). Each setting reports end-to-end throughput over AR decoding in tokens per second (TPS).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 11 图文联合解读**

该表以 AR 为基线，对比 JetSpec 在不同 batch size（1/2/4/8/16）与 tree budget（16/32/64/128）下的端到端 TPS 加速比。

关键发现：① 低 batch 下树预算越大收益越高，batch=1、tree=128 达 4.33×（553.3 TPS）；② 高 batch 时出现拐点，batch=16、tree=32 取得全局最优 3.81×（1094.6 TPS），而 tree=128 反而回降至 2.80×，因树过大造成 overhead；③ 所有配置均稳定超越 AR（≥1.63×），证明并行树形 draft 能有效突破线性 draft chain 的吞吐天花板。

作用：在 vLLM 真实部署层面验证 JetSpec 的工程价值，呼应标题"打破 scaling ceiling"，并揭示 batch 与 tree budget 需联合调优的实践规律。

### Table 12 (p.21) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab12.png]]
> [!quote] caption
> Per-draft-token drafting cost ratio c = T draft / ( N T verify ) (%) on a single H200 NVL GPU, sweeping context length L and draft depth N . This is the cost coefficient used in Eq. equation 2 and Fig. 2. Lower is better.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心对象与结构**：单H200 NVL GPU上草稿开销占比 c = T_draft/(N·T_verify)（%），行为上下文长度 L∈{128,256,…,4096}，列为草稿深度 N∈{1,2,4,…,512}。

**数据规律**：(1) c 随 N 近似每翻倍减半——N=1 时约 15%，N=512 时仅 0.034–0.037%；(2) L≤2048 时 c 与 L 几乎无关，L=4096 时整体上抬（N=1:15%→18.3%）。

**论证结论**：c 随 N 急剧衰减，证明并行树形草稿的边际开销可被摊销至近乎零，从而打破传统推测解码"深 N 不划算"的扩展天花板。

**论文作用**：作为 Eq.2 与 Fig.2 加速模型的实测成本系数，为 JetSpec "大 N 并行草稿"策略提供量化标定，使理论加速比上限趋近接受率倒数 τ⁻¹。

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