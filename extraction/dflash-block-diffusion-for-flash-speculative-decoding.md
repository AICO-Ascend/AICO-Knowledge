---
paper_num: "7"
title: "DFlash: Block Diffusion for Flash Speculative Decoding"
authors: "Jian Chen 1 Yesheng Liang 1 Zhijian Liu 1"
date: "2026/2/4"
arxiv: "https://arxiv.org/abs/2602.06036"
pdf: "papers/dflash-block-diffusion-for-flash-speculative-decoding.pdf"
slug: "dflash-block-diffusion-for-flash-speculative-decoding"
tags: [speculative]
---

# DFlash: Block Diffusion for Flash Speculative Decoding

> [!abstract] 摘要（原文）
> 1\. 🚀 DFlash 提出了一种利用轻量级块扩散（block diffusion）模型进行并行草稿生成的投机解码框架，有效解决了 autoregressive LLM 序列化解码导致的推理延迟瓶颈。 2. 🧠 该方法通过将 target LLM 的隐藏层特征注入 draft model 的 KV cache 中，实现了对未来 token 块的精确条件建模，从而显著提升了草稿的预测质量与接受率。 3. 📈 实验表明，DFlash 在多种主流模型和任务上实现了超过 6 倍的无损加速，其性能相较于目前最先进的投机解码方法 EAGLE-3 提升了约 2.5 倍。

## 元信息
- **发表日期**: 2026/2/4
- **作者**: Jian Chen 1 Yesheng Liang 1 Zhijian Liu 1
- **arXiv**: https://arxiv.org/abs/2602.06036
- **本地 PDF**: `papers/dflash-block-diffusion-for-flash-speculative-decoding.pdf`
- **页数**: 13

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig01.png]]
*整页渲染: ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p02.png]]*
> [!quote] caption
> Speedup comparison between DFlash, EAGLE-3 against Autoregressive Decoding on Qwen3-8B (Yang et al., 2025) with the

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

图1以分组柱状图形式展示DFlash、EAGLE-3相对自回归基线（均归一为1.00）在Qwen3-8B+Transformers后端、7个基准上的加速比：GSM8K（5.15 vs 2.23）、Math500（6.08 vs 2.05）、AIME25（5.62 vs 2.05）、HumanEval（5.14 vs 2.17）、MBPP（4.65 vs 1.93）、LiveCodeBench（5.51 vs 1.81）、MT-Bench（2.75 vs 1.90）。DFlash在所有任务上均显著领先，平均超EAGLE-3约2.5倍以上，最高比值出现在LiveCodeBench（约3.0×），最低也在MT-Bench（约1.45×）。原文借此直接论证"块扩散式投机解码"在精度无损前提下，可大幅超越主流自回归投机方法（EAGLE-3），作为开篇核心实验，奠定全文方法优势与实用价值。

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig02.png]]
*整页渲染: ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p04.png]]*
> [!quote] caption
> DFlash Inference Design. Hidden context features extracted from the target model are fused and injected into each draft layer’s

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图示DFlash推理架构：**目标模型从提示词抽取hidden context特征（蓝方块），融合后注入每层Draft Layer的KV Cache；Target Embedding并入Target Decode Token（黄）与多个Mask Token（绿），序列经Bidirectional Attention+MLP多层堆叠，最终由Target LM Head并行解码至`<eos>`。

**图文论证结论：**把目标模型上下文特征融合注入草案层KV Cache，使草案模型可借助双向注意力并行填补掩码位置，实现条件式块级推测解码，区别于传统自回归逐token草案。

**论文整体作用：**作为DFlash核心推理机制设计，与表2解码加速比及平均接受率实验直接对应，为"扩散式块生成+Flash推测解码"提供方法学基础。

### Figure 3 (p.3) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig03.png]]
*整页渲染: ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p03.png]]*
> [!quote] caption
> Draft cost of 1, 3, 5-layer DFlash and 1-layer EAGLE-3.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**核心对象与数据**：横轴为 draft token 数（4/8/16），纵轴为 Latency（ms）。EAGLE-3 自≈6.5ms（4 tok）线性增至≈26ms（16 tok）；三档 DFlash 几乎不随长度变化——DFlash(1)≈1.8–2ms、DFlash(3)≈3.8–4ms、DFlash(5)≈5.5–5.8ms；16 tok 时 EAGLE-3 比 DFlash(1) 慢≈14×。

**关键结论**：DFlash 因块扩散并行生成，draft 成本与生成长度近似解耦；EAGLE-3 受自回归限制成本随长度线性放大，在长 block 下 DFlash 显著更廉价。

**论文作用**：量化支撑 DFlash"draft cost 可被并行摊销"的核心优势，为 Table 3 中更长 block 带来更高整体吞吐与加速比提供前置实验依据。

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig04.png]]
*整页渲染: ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p05.png]]*
> [!quote] caption
> DFlash training attention. The target model provides context features (blue) that condition the draft model. The input consists of clean prompt tokens p and clean response tokens r.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图以矩阵可视化DFlash的训练注意力模式。左侧"From Target Model"为12×6网格，蓝格表示目标模型对prompt p1–p4与响应r1–r2提取的上下文特征（共4+2=6列）；右侧"Mask Blocks"为12×12网格，划分3个4×4块，每块含1个clean anchor（黄，如r1/r2/r3）+3个mask token（绿，<m>），其余为invisible（白）。每块4行体现块内并行解码结构。

该图论证的核心结论是：DFlash采用块扩散训练范式，以clean token作锚点条件化mask token预测，使草稿模型在单次前向中并行生成整块draft token，避免自回归串行依赖。

在论文链路中，此图为方法核心图，明确阐释了"目标特征条件化+块扩散掩码训练"的整体机制，是后续消融实验与投机解码加速比论证的可视化基础。

### Figure 5 (p.13) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig05.png]]
*整页渲染: ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p13.png]]*
> [!quote] caption
> The loss decay makes training converge faster and better. A.5.2. RANDOM SAMPLING OF MASKED BLOCKS

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图5为折线图，横轴为训练Epoch(1-9)，纵轴为Math500上的Acceptance Length（约4.2–6.5），对比"with loss decay"（蓝）与"without loss decay"（橙）两条曲线。前3个epoch蓝线明显高于橙线（如epoch 2蓝≈5.4 vs 橙≈5.2，差距约0.2），约epoch 5后两者趋于重合，并在epoch 7达峰值≈6.45，epoch 9轻微回落至≈6.35。

原文以此论证：加入loss decay训练策略可使模型**收敛更快**（前期epoch差距明显）且**最终性能更优**（峰值略高），验证该技巧在dFlash推测解码框架中的有效性。

该图属于附录A.5消融实验，与表5的加速比实验形成补充，从训练动力学角度独立支撑论文对loss decay机制的选择，增强方法设计的可信度。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.6) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab01.png]]
> [!quote] caption
> Decoding speedup over baseline and average acceptance length ( τ ) on Qwen3 models with thinking mode disabled and a

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**核心对象与数据**：表1给出Qwen3-4B/8B在T=0与T=1下，DFlash(块大小16)与EAGLE-3(树大小16/60)在7个基准(MATH/Code/Chat)上的加速比与平均接受长度τ，每格两值(加速比/τ)。以Q3-4B T=0为例：DFlash均加速4.91×、τ=6.54，全面碾压EAGLE-3(16)的1.81×/3.05与EAGLE-3(60)的2.08×/3.48；Q3-8B DFlash达4.86×/6.49，T=1场景同样领先(4.03×/5.48 vs 1.88×/3.26)。

**关键结论**：DFlash仅用块大小16即比EAGLE-3最大树(60)快约2.4倍、τ更长，跨任务、模型、温度稳健。

**论文作用**：作为主结果表，为"块扩散草稿取代树状自回归草稿"的中心论点提供量化证据链，与Fig.1可视化共同构成核心实验支撑。

### Table 2 (p.7) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab02.png]]
> [!quote] caption
> Decoding speedup over baseline and average acceptance

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读**

**核心内容**：表格对比 Q3-4B 与 Q3-8B 两个模型在 GPQA、MATH-500、AIME25 三个推理基准、Temp=0/1 两个采样温度下启用 thinking mode 后的解码加速比（括号内为平均接受长度）。Q3-4B 在 Temp=0 下加速 4.23×–4.59×，接受长度 5.23–5.74；Temp=1 降至 3.64×–3.93×。Q3-8B 表现接近且更稳定（MATH-500 Temp=0 达 4.64×/5.82）。

**关键结论**：dFlash 在数学/科学推理任务上实现 3.6×–4.6× 的端到端加速，且规模放大（4B→8B）几乎不损失加速比，验证了 block diffusion draft 对大型 target 模型的兼容性与泛化性；高温采样因接受长度下降导致加速回落，符合 speculative decoding 预期。

**实验链路作用**：该表是论文主实验的核心定量证据，支撑"dFlash 作为通用投机解码方案在推理类工作负载下实用性强"的总体结论。

### Table 3 (p.7) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab03.png]]
> [!quote] caption
> Throughput (tok/s), speedup over baseline, and average

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读：**

表格展示 DFlash 在 SGLang (FA4 backend) 上针对 Qwen3-4B/8B 与 Qwen3-Coder-30B-A3B (MoE) 三类模型，在 Math500、HumanEval、LCB、MBPP 任务上的吞吐量 (tok/s)、加速比与平均接受长度随并发度 1→32 的变化。

**核心数据**：Qwen3-4B Math500 并发=1 时吞吐量 316→1531 tok/s（4.8×），并发=32 时达 7136→20417（2.9×），平均接受长度 8.01；MoE 30B-A3B 上加速比稳定在 2.3–3.5×。

**论证结论**：DFlash 在低并发下达 4–5× 加速，高并发仍保持 ≥2.2×；对 MoE 大模型加速更稳定，体现块扩散草稿的兼容性。

**作用**：作为端到端部署层证据，与 Figure 3（草稿成本）互补，证明 DFlash 在真实推理框架中的吞吐优势。

### Table 5 (p.8) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab05.png]]
> [!quote] caption
> Speedup over baseline and average acceptance length

> [!tip] 表格解读（多模态）
> 【图文联合解读】图中列出 LongBench 上 Base 与长上下文微调（Long）drafter 在 hotpotqa、qasper、gov_report、1K–32K上下文下的结果；32K仅测 gov_report。随上下文增长，数值总体下降，但 Long 始终优于 Base：16K分别为3.61→6.05、3.57→6.00、2.67→3.81，32K时 gov_report 为2.09→3.56。这验证了长上下文微调对 drafter 质量及推测解码效率的提升，是连接长上下文建模与 speculative decoding 加速的关键实验；不过表内为单值，与“加速比和平均接受长度”的图注并不完全一致。

### Table 6 (p.8) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab06.png]]
> [!quote] caption
> 5-layer draft model has the best average speedup. All

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 图文联合解读**

**核心数据**：该表对比 3/5/8 层 DFlash 草稿模型（均以 block size 16、目标模型 5 层隐特征训练）在 Math500、HumanEval、MT-Bench 三个基准上的加速比，每基准给出两组数值。5-L 表现：4.71/5.99、3.96/4.94、2.35/3.37；8-L 表现：4.64/6.33、3.96/5.29、2.23/3.50。可见 8-L 在右列略高（如 Math500 的 6.33），但左列与 3-L 接近甚至略低。

**关键结论**：caption 明确指出 5 层草稿模型取得最佳**平均**加速比，说明在模型容量与推理开销间存在最优平衡点，盲目加深草稿模型并不能单调提升加速效果。

**实验链作用**：该表属于 DFlash 的**架构消融/超参验证实验**，用于确定草稿模型层数这一关键设计选择，为后续主实验的最优配置提供依据。

### Table 7 (p.8) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab07.png]]
> [!quote] caption
> More hidden features from target model increases the

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 7 解读**

1) **结构与数据**：表比较3/5/8层（从目标模型提取的隐特征层数）三种设置在Math500、HumanEval、MT-Bench三个基准上的加速比，每个基准有两列Speedup值。随层数增加，第二列加速比持续上升（如Math500: 5.64→5.99→6.33；HumanEval: 4.61→4.94→5.29；MT-Bench: 3.18→3.37→3.50），而第一列基本持平甚至略降（MT-Bench: 2.38→2.35→2.23）。

2) **关键结论**：更多隐特征层提高draft接受长度（对应第二列提升），却增加draft延迟（第一列边际下降）；存在draft质量与开销的权衡。

3) **论文作用**：作为消融实验，支撑5.5.3节"目标隐特征数量"超参选择，为DFlash默认5层提供依据，衔接Table 6的draft层数权衡讨论。

### Table 8 (p.8) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab08.png]]
> [!quote] caption
> Ablation study of training–inference block size (BS)

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

需先指出：图片下方正文明确引用为 "Table 7" 并讨论 **target hidden features 数量（3 vs 5）**，而非 block size；用户所给 caption（"Training–Inference Block Size"）与图中文本不符，本解读以图内实际内容为准。

**1) 核心对象与数据：**
表格展示两个 Setting（3-H、5-H）在 Math500、HumanEval、MT-Bench 三基准上的 Speedup（每基准两列）。3-H：4.49/5.38、3.80/4.47、2.32/3.07；5-H：4.69/5.64、3.90/4.61、2.38/3.18。5-H 在所有指标上稳定优于 3-H。

**2) 关键技术结论：**
提取越多 target 层 hidden features，draft 模型获得的语义与未来 token 信息越丰富，接受长度与端到端加速越高；但收益伴随离线训练存储线性增长。

**3) 在论文中的位置：**
该表与 Table 8/9 一同构成消融证据链，证明 **target hidden context 注入是 dFlash 性能核心**，而非 block diffusion 结构本身——移除该特征则性能急剧退化。

### Table 9 (p.9) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab09.png]]
> [!quote] caption
> Ablation of target-feature conditioning for Qwen3-4B with 5-layer draft models and draft block size 8. Each task column reports τ / speedup.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表9以Qwen3-4B为target、5层draft、块大小8，消融target-feature的两种注入方式（Input vs KV），在GSM8K/HumanEval/MT-Bench上报告τ/速度加速。

**结构与数据**：自回归侧DFlash-AR(KV) τ为4.8/4.6/3.4，全面优于Input(4.2/4.3/3.1)；块扩散侧DFlash(KV) τ为4.2/4.0/3.0，速度加速达3.3/3.2/2.2，为全表最高。

**关键结论**：KV注入全面优于Input注入——验证目标特征经KV缓存传递比拼接到输入更有效，是dFlash的核心设计选择；且KV条件下DFlash块扩散取得最大加速，凸显块扩散并行采样优势。

**论文作用**：作为第9号消融表，支撑dFlash"target-feature通过KV注入"和"块扩散draft"两大设计主张，强化方法可信度。

### Table 10 (p.12) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab10.png]]
> [!quote] caption
> A 5-layer block diffusion draft model without target

> [!tip] 表格解读（多模态）
> 【图文联合解读】## Table 10 解读

**1. 核心数据**：5层 block diffusion 草案模型在**移除 target 上下文特征**后的表现。温度0下：GSM8K 加速2.83/接受长3.38、Math500 3.73/4.61、AIME24 3.43/4.12、AIME25 3.35/4.07；温度1下加速与接受长普遍下降（如 AIME25 降至 2.65/3.24）。速度均≤4.6×。

**2. 关键结论**：原文据此论证——若草案模型不接收目标模型的上下文特征，其接受长度与加速比仅达"modest"水平，远低于完整 dFlash，证明**target context features 是草案模型质量的关键依赖**。

**3. 论文作用**：作为消融实验，剥离 dFlash 核心设计（target 特征融合），反证该模块对 block diffusion 推测解码有效性的必要性。

### Table 11 (p.12) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab11.png]]
> [!quote] caption
> Results across more models on SGLang. Each cell

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心对象与数据**：表11在SGLang框架下测试7个模型（Qwen3.5-4B/9B/35B-A3B/27B、Qwen3-Coder-Next、GPT-OSS-20B/120B），每格报告 acceptance length / speedup，跨 Math500、HumanEval、MT-Bench 三基准；前三组含 MTP 对照，后四组仅 DFlash。

**关键结论**：DFlash 在所有模型上 acceptance length 略胜或近似 MTP（如 4B：7.1 vs 6.5），但 speedup 优势更显著——9B 达 3.5×、27B 高达 3.9×，约为 MTP（1.3–1.7×）的 2 倍，表明 acceptance length 与 speedup 并非线性耦合。

**论文作用**：作为主表外的扩展泛化实验，覆盖 4B–120B 不同规模、dense/MoE 不同架构及代码/对话任务，证明 DFlash 相对 MTP 的稳定优势，强化方法普适性与稳健性主张。

### Table 12 (p.12) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab12.png]]
> [!quote] caption
> vLLM results for Qwen3.5-9B. Each cell reports DFlash

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 12 图文联合解读**

该表展示Qwen3.5-9B在vLLM推理框架下，DFlash吞吐量(tok/s)与相对AR解码的加速比，维度为并发度(1/8/16/32)×任务(Math500/HumanEval/MT-Bench)。

**核心数据**：吞吐量随并发度近似线性增长，HumanEval由969→10258 tok/s；但加速比却随并发度衰减——Math500由4.0×降至1.9×，MT-Bench由3.0×降至1.3×；HumanEval加速效果最优(1.9–4.6×)。

**技术结论**：DFlash在真实服务系统vLLM中仍可获得1.3–4.6×端到端加速，验证其工程实用性；同时揭示推测解码在高并发场景下加速比递减的固有特性（批处理均摊降低解码边际增益）。

**论文作用**：作为部署层实证，与离线基准互补，支撑DFlash从算法到工业推理服务的有效性论证，强化论文"落地可用"的核心主张。

### Table 13 (p.13) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab13.png]]
> [!quote] caption
> Randomly sample anchor tokens to construct masked

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 13 图文联合解读：**

该表对比"Standard"与"Sample"（随机采样锚点构造掩码块）两种训练策略，在 Math500、HumanEval、MT-Bench 三个基准上各列出两组 speedup 数据。Sample 行在所有基准与指标上均加粗优于 Standard：Math500 为 4.69x / 5.64x 对比 4.13x / 4.94x；HumanEval 为 3.90x / 4.61x 对比 3.29x / 3.86x；MT-Bench 为 2.38x / 3.18x 对比 2.13x / 2.80x。

原文据此论证：随机采样锚点构建掩码块能有效扩充训练数据多样性，提升草稿模型的接受长度与端到端加速比。在论文整体链路中，该消融实验为 dFlash 训练阶段的掩码构造方式选择提供经验依据，巩固了块扩散草稿模型相对标准训练的优越性。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf{H}_{t} = \mathrm{RMSNorm} \left( W_c[\mathbf{H}^{(l_1)};\ldots;\mathbf{H}^{(l_5)}] \right).
$$

$$
\begin{aligned} \mathbf{Q}_i &= W_i^Q \mathbf{H}_d, \\ \mathbf{K}_i &= [W_i^K \mathbf{H}_t;\, W_i^K \mathbf{H}_d]_{\mathrm{seq}}, \\ \mathbf{V}_i &= [W_i^V \mathbf{H}_t;\, W_i^V \mathbf{H}_d]_{\mathrm{seq}}. \end{aligned}
$$

$$
5 \times 2048 \times 2048 \times 2 \approx 42\text{ MB},
$$

## 相关论文

- [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] — SpecExtend: A Drop-in Enhancement for Speculative Decoding of Long Sequences
- [[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]] — BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DIFFUSION LANGUAGE MODELS
- [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] — DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation
- [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] — LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and Verification
- [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] — JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting
- [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] — EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty

## 技术点深读（DEEP）

![[deep/dflash-block-diffusion-for-flash-speculative-decoding]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/dflash-block-diffusion-for-flash-speculative-decoding.txt`（54200 字符）供引用检索。