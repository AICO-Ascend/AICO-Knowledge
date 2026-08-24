---
paper_num: "39"
title: "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints"
authors: "Multi-Head Checkpoints Joshua Ainslie∗, James Lee-Thorp∗, Michiel de Jong∗† Yury Zemlyanskiy, Federico Lebrón, Sumit Sanghai Google Research"
date: "2026/1/7"
arxiv: "https://arxiv.org/abs/2305.13245"
pdf: "papers/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints.pdf"
slug: "gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints"
tags: [training]
---

# GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints

> [!abstract] 摘要（原文）
> 1\. 🧐 Transformer解码器推理因加载注意力键值而存在内存带宽瓶颈，Multi-Query Attention (MQA) 能缓解此问题但常导致质量下降。 2. 🚀 本文提出一种通过少量计算将现有Multi-Head Attention (MHA) 模型“uptrain”为MQA模型的方案，并引入了Grouped-Query Attention (GQA)，作为MHA和MQA之间的中间形式。 3. ✨ 实验表明，经过“uptrain”的GQA模型在保持接近MHA质量的同时，实现了与MQA相当的推理速度，提供了更优的性能-效率权衡。

## 元信息
- **发表日期**: 2026/1/7
- **作者**: Multi-Head Checkpoints Joshua Ainslie∗, James Lee-Thorp∗, Michiel de Jong∗† Yury Zemlyanskiy, Federico Lebrón, Sumit Sanghai Google Research
- **arXiv**: https://arxiv.org/abs/2305.13245
- **本地 PDF**: `papers/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints.pdf`
- **页数**: 7

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig01.png]]
*整页渲染: ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p01.png]]*
> [!quote] caption
> Overview of conversion from multi-head to multi-query attention. Key and value projection matri- ces from all heads are mean pooled into a single head.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图1展示了从多头注意力（MHA）到多查询注意力（MQA）的参数转换流程。左侧为H个独立的Key投影矩阵（K₁…K_H），每个维度为d_model×d_h；经中间"Mean Pool"操作后，合并为右侧单一的Key投影K_MQ（仍保持d_model×d_h）。

**论证结论**：通过将所有头的K/V投影矩阵逐元素取均值，可将H份独立的K/V头压缩为1份共享参数，且输出维度不变。该操作无额外训练即可完成，实现了从MHA到MQA的参数无缝降维。

**论文作用**：作为全文核心方法"训练式转换"的可视化基础，说明了GQA作为一种通用化形态——只需调整共享头数，即可平滑插值于MHA与MQA之间，是后续初始化策略与实验分析的理论前提。

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig02.png]]
*整页渲染: ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p02.png]]*
> [!quote] caption
> Overview of grouped-query method. Multi-head attention has H query, key, and value heads. Multi-query attention shares single key and value heads across all query heads. Grouped-query attention instead shares single key and value heads for each group of query heads, interpolating between multi-head and multi-query attention. a small proportion α of its original training steps on the same pre-train

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示三种注意力机制的Q/K/V头配置对比：左Multi-head（H=8）每查询头独立配独立K/V头（8个K、8个V）；右Multi-query仅1个K、1个V头被8个查询共享；中间加粗的Grouped-query将8个查询头分为4组，每2查询共享1个K/V头（共4个K/V）。原文借此论证：GQA是MHA与MQA之间的插值方案，在保留多头表征能力的同时显著降低K/V显存与解码计算开销。该图为论文核心方法奠定结构基础——将预训练MHA checkpoint只需少量额外步（比例α）即可转换/微调为GQA模型，从而兼顾质量与推理效率。

### Figure 3 (p.3) ⭐深度解读
![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig03.png]]
*整页渲染: ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p03.png]]*
> [!quote] caption
> Uptrained MQA yields a favorable tradeoff compared to MHA with higher quality and faster speed than MHA-Large, and GQA achieves even better performance with similar speed gains and comparable quality to MHA-XXL. Average perfor- mance on all tasks as a function of average inference time per sample for T5-Large and T5-XXL with multi- head attention, and 5% uptrained T5-XXL with MQA and GQA-8 attenti

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图3图文联合解读：**

图3散点图展示四模型的速度-性能权衡：MHA-Large(≈0.4ms, 46.0)、MQA-XXL(≈0.3ms, 46.6)、GQA-XXL(≈0.3ms, 47.2)、MHA-XXL(≈1.5ms, 47.3)。GQA-XXL以MQA级推理速度取得接近MHA-XXL的质量，且比后者快约5倍，构成Pareto最优折中。

原文借此论证：经5%继续训练的MQA在速度-质量权衡上优于MHA-Large，GQA则同时逼近MHA-XXL的性能并保留显著的速度增益。该图是论文实验链路的核心可视化证据，验证"uptraining"方法将MHA检查点高效转化为GQA的可行性——在不牺牲质量的前提下大幅提升推理效率，支撑GQA作为实用注意力替代方案的核心论点。

### Figure 4 (p.4) ⭐深度解读
![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig04.png]]
*整页渲染: ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]]*
> [!quote] caption
> Performance comparison of different check- point conversion methods for T5-Large uptrained to MQA with proportion α = 0.05. ‘Mean’ mean-pools key and value heads, ‘First’ selects the first head and ‘Random’ initializes heads from scratch. be useful. Both MQA and GQA gain from 5% uptraining with diminishing returns from 10%. 0

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示T5-Large以α=0.05上训练至MQA时，三种checkpoint转换方法的性能对比：Mean池化约55.6、First取首头约55.5、Random随机初始化约55.2。

**技术结论**：Mean池化最优，Random最差但绝对差距仅约0.4，说明仅需5%上训练，从MHA checkpoint转换即可获得接近最优的MQA性能，验证转换策略而非从零训练的有效性。

**论文作用**：为论文核心主张——MHA checkpoint可通过轻量键值头转换快速得到高性能MQA/GQA——提供方法选型依据，支撑后续uptraining实验链路设计与维度消融的合理性。

### Figure 5 (p.4) ⭐深度解读
![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig05.png]]
*整页渲染: ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]]*
> [!quote] caption
> Performance as a function of uptraining pro- portion for T5 XXL models with MQA and GQA-8.

> [!tip] 技术解读（多模态）
> 【图文联合解读】## 图文联合解读

**核心数据**：横轴为 uptraining 比例 α（0/5%/10%），纵轴为模型性能。MHA 基线（粉色虚线）恒定约 57.5；GQA-8（蓝方块）从 α=0 时约 56.7 升至 α=10% 时约 57.4；MQA（橙三角）从约 54.0 急升至 5% 时的约 57.0，随后趋于平缓。

**关键结论**：α=0 时 MQA 落后 MHA 约 3.5 分，而 GQA-8 仅落后约 0.8 分，说明 GQA 在"无重训练"状态下就能很好地逼近 MHA 质量；仅需 5% uptraining，两者即获大幅提升且收益递减，证明极小额外成本即可恢复性能。

**论文作用**：作为 uptraining 有效性的实证核心，支撑"用 GQA 替代 MHA 是推理效率与质量最优折中"的核心主张，使论文方案具备实际部署可行性。

### Figure 6 (p.4) ⭐深度解读
![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig06.png]]
*整页渲染: ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]]*
> [!quote] caption
> Time per sample for GQA-XXL as a function of the number of GQA groups with input length 2048 and output length 512. Going from 1 (MQA) to 8 groups adds modest inference overhead, with increasing cost to adding more groups. is especially helpful for long inputs (Pope et al., 2022; de Jong et al., 2022). Rabe (2023) indepen- dently developed GQA with public implementa- tion. Other works have explore

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图6图文联合解读：**

图6展示GQA-XXL在输入2048、输出512条件下，单样本推理时间（秒）随分组数1–64的变化，对照MHA（≈2.5s）、MQA（≈0.5s）两条基线。GQA在1–8组时与MQA几乎重合（≈0.5s），16组0.6s，32组0.8s，64组陡升至≈2.5s，逼近MHA。

结论：分组≤8几乎无推理开销，≥32则效率优势消失，证实8组是兼顾表达力与速度的最佳折中。该图为论文核心方法——"由MHA检查点转换少量分组GQA"——提供推理成本实证，验证转换后模型在保留多头能力的同时获得近似MQA的推理速度。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.3) ⭐深度解读
![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-tab01.png]]
> [!quote] caption
> Inference time and average dev set performance comparison of T5 Large and XXL models with multi-head attention, and 5% uptrained T5-XXL models with multi-query and grouped-query attention on summarization datasets CNN/Daily Mail, arXiv, PubMed, MediaSum, and MultiNews, translation dataset WMT, and q

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表1核心内容**：对比 T5-Large/XXL（MHA）与仅 5% 额外训练的 MQA-XXL、GQA-8-XXL 在 7 个任务（CNN/DM、arXiv、PubMed、MediaSum、MultiNews 用 R₁，WMT 用 BLEU，TriviaQA 用 F1）的推理时延 T_infer 与平均得分。

**关键数据**：MHA-XXL 为 1.51 s / 47.2；MQA-XXL 降至 0.24 s / 46.6；GQA-8-XXL 为 0.28 s / 47.1。

**论证结论**：MQA 推理提速约 6.3× 但均分仅降 0.6；GQA-8 提速约 5.4× 而质量几近追平 MHA-XXL，证明 GQA 在速度与精度间取得最佳平衡。

**论文作用**：作为核心实证，支撑"MHA checkpoint 经极少 uptraining 即可无损转换为 GQA、服务高效部署"的核心主张。

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.2 `et al., 2020). For α = 0.05, training took approxi-`
- p.3 `proportion α = 0.05. We see that a larger up-`
- p.4 `MQA with proportion α = 0.05. ‘Mean’ mean-pools`

## 相关论文

- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[zero-memory-optimizations-toward-training-trillion-parameter-models]] — ZeRO: Memory Optimizations Toward Training Trillion Parameter Models
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey
- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] — From ATOP to ZCube: Automated Topology Optimization Pipeline and A Highly Cost-Effective Network Topology for Large Model Training

## 技术点深读（DEEP）

![[deep/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints.txt`（23726 字符）供引用检索。