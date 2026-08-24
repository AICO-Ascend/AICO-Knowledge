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
> 【图文联合解读】**图文联合解读：**

图2展示DFlash推理流程的三个阶段：(1) 左侧目标模型编码上下文（含`-./&01`等前缀token），提取**隐藏上下文特征**（顶部阴影方块）并向中间虚线框注入；(2) 中间虚线框为草稿模型，融合目标特征后以**块扩散**方式并行生成约**278个token候选**（如"45%5/0$*5…"），左下虚线框示意已确认/待确认/待生成三类token状态；(3) 右侧目标模型一次性并行验证候选块，部分token被拒绝（"!!!"），其余被接受并继续生成下一块。

**论证结论**：目标模型的隐藏特征可直接作为草稿模型各层的条件输入，无需从头预测；块级扩散+并行验证使每步解码一次前向即可生成数百token。

**论文作用**：作为方法核心示意图，配合Table 2的**speedup/acceptance**数据，直观证明DFlash相较传统自回归推测解码的加速机理与收益来源。

### Figure 3 (p.3) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig03.png]]
*整页渲染: ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p03.png]]*
> [!quote] caption
> Draft cost of 1, 3, 5-layer DFlash and 1-layer EAGLE-3.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1）核心对象与数据：** 分组柱状图，横轴为 draft token 数（4/8/16），纵轴为生成延迟（ms）。EAGLE-3（1层）随 token 数线性增长：约 6.5→12→26 ms；而 DFlash 三种配置几乎平坦——DFlash(1) 始终 ≈2 ms，DFlash(3) 约 3.5–4 ms，DFlash(5) 约 5–6 ms。在 16 token 处，EAGLE-3 比最快 DFlash(1) 慢约 13 倍。

**2）关键结论：** DFlash 因采用 Block Diffusion 并行生成全部 draft token，延迟与草稿长度几乎解耦；而 EAGLE-3 因自回归逐 token 生成，成本随长度线性放大。这验证了 DFlash 作为 draft model 在效率上对自回归方案的数量级优势。

**3）在论文中的作用：** 该图是论文核心卖点之一的实验支撑——证明 DFlash 不仅在生成质量/接受率上可竞争，更以"恒定低延迟"显著降低 speculative decoding 的单步开销，为其在在线推理/树形解码场景中的实用性提供量化证据。

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig04.png]]
*整页渲染: ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p05.png]]*
> [!quote] caption
> DFlash training attention. The target model provides context features (blue) that condition the draft model. The input consists of clean prompt tokens p and clean response tokens r.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图4 联合解读**

图分两栏。左栏"From Target Model"为6列（p1–p4, r1, r2）因果三角掩码，目标模型对prompt与干净response自回归编码，输出蓝色上下文特征；右栏"Mask Blocks"为12列×12行的块注意力矩阵，按r1/m/m/m、r2/m/m/m、r3/m/m/m划分为3块，每块4行中仅允许同块clean token（橙）及前块mask token（绿）相互可见，白色为不可见token。

**核心结论**：draft模型以左侧蓝色目标特征为cross-attention条件，在每个clean response token之后并行预测3个mask token，从而形成"块扩散"式训练目标；条件注入被严格限定在clean token位置，避免未来信息泄露。

**论文作用**：该图即DFlash核心训练范式的示意图，是后文Table 4中Qwen3-27B取得较长接受长度与加速比的方法论基础。

### Figure 5 (p.13) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig05.png]]
*整页渲染: ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p13.png]]*
> [!quote] caption
> The loss decay makes training converge faster and better. A.5.2. RANDOM SAMPLING OF MASKED BLOCKS

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图5图文联合解读：**

图示Math500数据集上Acceptance Length随训练epoch（1–9）的演化，对比有/无loss decay两条曲线。蓝色（有loss decay）epoch 1即达~4.4，epoch 2快速跃升至~5.4；橙色（无）epoch 1仅~4.2，需至epoch 4方追至~6.0。两者在epoch 6–7同步收敛至峰值~6.45（蓝色略高），epoch 9趋于一致~6.35。

原文据此论证：**loss decay策略使dFlash训练"收敛更快、效果更好"**——尤其在前3个epoch显著拉开差距。在论文整体链路中，该消融实验作为附录A.5.2随机掩码采样方案的支撑，验证了损失衰减对投机解码头快速稳定收敛、高接受率（最终~6.35）的必要性，是模型实现高效推测的关键训练技巧之一。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.7) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab02.png]]
> [!quote] caption
> Decoding speedup over baseline and average acceptance

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

表2在"思考模式"下，对Q3-4B/8B两个模型、温度0与1，在GPQA、MATH-500、AIME25三个推理基准上各报告两组配对数据——加速比与平均接受长度。结果显示加速比稳定在3.64×–4.64×之间，接受长度4.55–5.82个token/步；温度0显著优于温度1（确定性更易预测），8B与4B表现接近，MATH-500整体最优。

该表用以论证DFlash在链式思考推理场景下仍能获得约4倍解码加速，且接受长度足够长，证明块扩散式投机解码对推理模型具有普适的高效性。

在论文链路中，它承接Figure 2的推理架构设计，以量化实验闭环回答"该方案在强推理负载下是否真正实用"这一核心问题，构成方法可行性的关键验证。

### Table 3 (p.7) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab03.png]]
> [!quote] caption
> Throughput (tok/s), speedup over baseline, and average

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心内容**：Table 3 在 SGLang（FA4 后端）上对比 Baseline 与 DFlash，涵盖 Qwen3-4B/8B/Coder-30B-A3B 三个模型、4–6 个任务、并发档位 1/4/8/16/32，逐行给出吞吐量（tok/s）、相对加速比与平均接受长度。

**关键结论**：所有配置下 DFlash 加速 2.2×–5.1×；低并发加速最大（如 Qwen3-8B Math500 c=1：1175 vs 230，5.1×），随并发上升收敛至 2.3–3.1×；平均接受长度 6.42–8.09。

**论文作用**：与 Fig.3（draft 成本）互补，构成"draft 廉价 → 端到端服务吞吐显著提升"的完整证据链，支撑 DFlash 作为实用投机解码方案的论断。

### Table 5 (p.8) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab05.png]]
> [!quote] caption
> Speedup over baseline and average acceptance length

> [!tip] 表格解读（多模态）
> 【图文联合解读】图中并非所引 Figure 5，而是比较 Base/Long drafter 在 LongBench 的 hotpotqa、qasper、gov_report 上、1K–32K 上下文的任务得分。1K 时 Long 略优；16K 时分别由 3.61→6.05、3.57→6.00、2.67→3.81；32K 仅 gov_report 可测，得分 2.09→3.56。结果支持长上下文微调可提升 drafter 的长程建模，为推测解码加速奠基。表题称“加速比/平均接受长度”，却与可见数据不符，且无法核验 loss decay 消融。

### Table 7 (p.8) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab07.png]]
> [!quote] caption
> More hidden features from target model increases the

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表7图文联合解读**

表7对比dFlash草稿模型采用3-H与5-H两种目标隐藏特征数配置（统一3草稿层、block size=16）在三基准的加速比：Math500（4.49/5.38→4.69/5.64）、HumanEval（3.80/4.47→3.90/4.61）、MT-Bench（2.32/3.07→2.38/3.18），5-H均稳定小幅领先。

原文据此论证：抽取更多目标层隐藏特征能提供更丰富语义与未来token信息，提升草稿质量、接受长度及端到端加速；但离线训练时缓存目标隐藏态的存储开销随特征数线性增长，构成"速度—训练成本"权衡。

该表在实验链路中作为关键设计超参（隐藏特征数量）的消融证据，支撑最终方案选型。

### Table 9 (p.9) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab09.png]]
> [!quote] caption
> Ablation of target-feature conditioning for Qwen3-4B with 5-layer draft models and draft block size 8. Each task column reports τ / speedup.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表9对Qwen3-4B+5层draft（块大小8），在三任务（GSM8K/HumanEval/MT-Bench）上比较Input与KV两种目标特征注入方式（每格报告τ/加速比）。

**数据**：KV注入全面优于Input注入。在DFlash内，KV将τ从3.5/3.5/2.6提至4.2/4.0/3.0，加速比从2.9/2.9/2.0提至**3.3/3.2/2.2**；DFlash-AR(KV)也稳定胜出EAGLE-3-5L(Input)，如MT-Bench 3.4/1.5 vs 3.1/1.4。

**结论**：用目标模型KV缓存（而非输入embedding）做条件注入是DFlash的核心设计。值得注意的是，DFlash(KV)块扩散版的τ虽略低于自回归DFlash-AR(KV)，但加速比反更高（2.2 vs 1.5），体现块并行解码的优势。

**作用**：作为消融实验，证实"块扩散+深度特征条件化"两个设计选择的有效性，支撑全文方法主张。

### Table 10 (p.12) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab10.png]]
> [!quote] caption
> A 5-layer block diffusion draft model without target

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 10 联合解读**

该表展示的是 **5 层 block diffusion draft model 去除 target context features 后的消融结果**，在 GSM8K、Math500、AIME24、AIME25 四个数学基准上，以 Temp=0/1 报告 (接受长度/加速比)。Temp=0 时数据为 2.83/3.38、3.73/4.61、3.43/4.12、3.35/4.07；Temp=1 时为 2.76/3.29、3.31/4.12、2.66/3.23、2.65/3.24，相较主表完整 dFlash 模型显著下降。

原文借此论证：dFlash 之所以获得高接受长度与显著加速，**关键在于 target 模型的 hidden context 作为 draft 输入**；一旦移除该特征，draft 模型性能急剧退化，验证了**双向跨模型上下文注入是该方法的核心设计**，而非单纯依赖 block diffusion 自身结构。该表作为消融实验支撑，与 Table 8/9 共同证明各组件不可替代。

### Table 11 (p.12) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab11.png]]
> [!quote] caption
> Results across more models on SGLang. Each cell

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 11 联合解读**

**核心对象与数据**：表 11 在 SGLang 推理框架下，对 7 个模型（Qwen3.5-4B/9B/35B-A3B/27B、Qwen3-Coder-Next、GPT-OSS-20B/120B）比较 MTP 与 DFlash，每格报告 acceptance length / speedup，跨 Math500、HumanEval、MT-Bench 三基准。

**关键技术结论**：DFlash 在所有可比模型上同时超越 MTP 的接受长度与加速比——例如 Qwen3.5-4B 在 Math500 上从 6.5/1.5× 提升到 7.1/3.0×，加速比翻倍；Qwen3.5-9B 在 HumanEval 达到 7.9/3.4×；Qwen3.5-27B 取得全表最高的 9.1/3.9×；同时在稠密、MoE、异构（GPT-OSS）架构上均有效，证实方法的**架构无关可迁移性**。

**在论文中的作用**：作为补充实验，扩展主表结论，强化"DFlash 通用且显著优于 MTP"的核心主张，支撑论文方法有效性的普适论证。

### Table 12 (p.12) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab12.png]]
> [!quote] caption
> vLLM results for Qwen3.5-9B. Each cell reports DFlash

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 12 图文联合解读**

1) **核心对象与结构**：表展示 Qwen3.5-9B 模型在 vLLM 推理框架下，DFlash 在 4 个并发等级（1、8、16、32）和 3 个基准（Math500、HumanEval、MT-Bench）上的吞吐量（tok/s）及相对于自回归（AR）解码的加速比（括号内）。数据示例：C=1 时 HumanEval 达 969 tok/s（4.6×）；C=32 时 HumanEval 达 10258 tok/s（2.1×）；MT-Bench 在 C=1/32 下为 627/6787 tok/s（3.0×→1.3×）。

2) **关键技术结论**：① DFlash 在所有并发与基准上均显著优于 AR 解码（最低 1.3×，最高 4.6×）；② 加速比随并发提升而下降，因 AR 解码在高并发下已受内存带宽瓶颈缓解，DFlash 优势被摊薄；③ HumanEval 加速比始终最高，MT-Bench 最低，反映代码生成任务确定性更强、DFlash 草稿接受率更高。

3) **论文作用**：此表补足 vLLM 实际部署视角，证明 DFlash 不仅在自研框架有效，在主流工业推理引擎中同样带来稳定吞吐增益，强化"即插即用、广泛适用"的实验结论。

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