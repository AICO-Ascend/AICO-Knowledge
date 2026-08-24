---
paper_num: "47"
title: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models"
authors: "Parameter Models Samyam Rajbhandari∗, JeﬀRasley∗, Olatunji Ruwase, Yuxiong He {samyamr, jerasley, olruwase, yuxhe}@microsoft.com"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/1910.02054"
pdf: "papers/zero-memory-optimizations-toward-training-trillion-parameter-models.pdf"
slug: "zero-memory-optimizations-toward-training-trillion-parameter-models"
tags: [training]
---

# ZeRO: Memory Optimizations Toward Training Trillion Parameter Models

> [!abstract] 摘要（原文）
> 1\. 针对训练万亿参数深度学习模型面临的内存限制，该论文提出了 ZeRO (Zero Redundancy Optimizer)，一种通过消除现有数据并行 (DP) 和模型并行 (MP) 冗余来优化内存的新方法。 2. ZeRO 核心包括 ZeRO-DP（数据并行内存优化）分阶段分区优化器状态、梯度和参数，以及 ZeRO-R（残余内存优化）管理激活、临时缓冲区和内存碎片。 3. ZeRO-100B 的实现使在 400 个 GPU 上高效训练 170B 参数的模型成为可能，相比最先进技术，模型大小增加 8 倍，吞吐量提升 10 倍，并简化了大型模型的训练应用。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Parameter Models Samyam Rajbhandari∗, JeﬀRasley∗, Olatunji Ruwase, Yuxiong He {samyamr, jerasley, olruwase, yuxhe}@microsoft.com
- **arXiv**: https://arxiv.org/abs/1910.02054
- **本地 PDF**: `papers/zero-memory-optimizations-toward-training-trillion-parameter-models.pdf`
- **页数**: 24

## 图表（原文 caption + 页码）

### Figure 1 (p.3) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig01.png]]
*整页渲染: ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p03.png]]*
> [!quote] caption
> Comparing the per-device memory consumption of model states, with three stages of

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

图1以 Ψ=7.5B、K=12、N_d=64 为具体参数，量化对比 Baseline 与 ZeRO-DP 三阶段（P_os、P_os+g、P_os+g+p）的**每卡显存**：参数（蓝）、梯度（橙）、优化器状态（绿）三色块由满载依次被切分，单卡占用从 Baseline 的 (2+2+K)Ψ=**120GB** 降至 31.4GB → 16.6GB → **1.9GB**，约 **60×** 压缩。

**关键结论**：依次分片优化器状态、梯度、参数可逐级消除数据并行冗余，且通信开销可控。

**作用**：作为全文方法论的开篇动机图，为后续 P_os / P_g / P_p 的形式化定义及万亿参数训练可行性论证奠定量化基础。

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig02.png]]
*整页渲染: ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p04.png]]*
> [!quote] caption
> ZeRO training throughput and speedup w.r.t SOTA baseline for varying model sizes.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图2以双轴柱状/散点复合图，对比1.5B–170B共9档模型规模下ZeRO（绿点）与基线MP（橙/红三角）的单GPU吞吐量（实线为10/15 Pflops参考线，灰柱为加速比）。数据上：ZeRO吞吐量稳定在30–38 Tflops，1.5/8B时基线仅23–26 Tflops、加速比≈1×；100B时ZeRO达~38 Tflops、基线骤降至~3.5 Tflops、加速比峰值~10×；170B仍保持~10×加速。

**技术结论**：验证ZeRO通过消除MP冗余存储，使MP始终限于单节点即可训练百亿–千亿级模型；相比>40B必须跨节点MP的基线，吞吐量与可扩展性均显著领先。

**论文作用**：作为Stage-1实验的核心证据，量化支撑"在标准数据并行集群上高效训练万亿参数模型"这一核心主张。

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig03.png]]
*整页渲染: ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p05.png]]*
> [!quote] caption
> Superlinear scalability and per GPU training throughput of a 60B parameter model using ZeRO-100B. 38 TFlops per GPU, and aggregate performance over 15 Petaﬂops. This is more than 10x improvement in training speed compared to SOTA for the same model size.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图3图文联合解读：**

1) **核心对象与数据**：横轴为GPU数（64→400），左轴为总性能Tflops（对数），右轴为单卡Tflops。灰柱=单卡吞吐，绿线=实测总性能，蓝线=理想线性参考。64卡时实测与线性线重合（约1500 Tflops，单卡~6 Tflops）；随规模扩展，实测曲线（绿）全程高于理想线性线（蓝），且灰柱同步增长（6→36 Tflops/GPU）；400卡时实测约15000 Tflops（15 PFlops），单卡~38 Tflops/GPU。

2) **关键结论**：ZeRO-100B在60B模型上呈现超线性扩展，单卡吞吐亦随规模提升，证实分片化显存优化缓解了内存-计算比瓶颈，训练速度较SOTA提升超10×。

3) **论文作用**：作为方法核心实证，衔接"显存瓶颈分析→ZeRO分片策略→超大规模可行性论证"链路，为后续ZeRO-100B乃至万亿参数训练提供性能保证。

### Figure 4 (p.16) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig04.png]]
*整页渲染: ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]]*
> [!quote] caption
> Max model throughput with ZeRO-DP.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图4散点图联合解读：**

左图为散点图，横轴为模型规模(1–13B参数)，纵轴为单卡吞吐量(0–50 Tflops)。绿色圆点(ZeRO-DP)从1.5B约40 Tflops上升，6–8B时达峰约47 Tflops，超过35 Tflops虚线(对应集群聚合4.5 Pflops)；橙色三角(Baseline-DP)在同等规模仅约18 Tflops，较ZeRO低约55%。右图(Figure 5)补充Model-ZeRO-17B验证困惑度全程低于Megatron-LM-8.3B。

**技术结论：** ZeRO-DP仅靠分片数据并行即可将单卡吞吐提升约2倍，并在10B级仍维持近峰值，验证其可扩展性。**论文作用：** 该图作为吞吐可行性证据，支撑后续Figure 5中17B模型训练实验及向万亿参数扩展的论证链。

### Figure 5 (p.16) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig05.png]]
*整页渲染: ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]]*
> [!quote] caption
> SOTA Turing-NLG enabled by ZeRO.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图5横轴为迭代步数（0–300K），纵轴为验证困惑度（8–14），对比两条曲线：橙色Megatron-LM-8.3B与绿色Model-ZeRO-17B。两者起点均接近14，但绿色ZeRO-17B曲线全程位于橙色之下，迭代至30万步时，ZeRO-17B收敛至约8.8，而Megatron-LM-8.3B稳定在约9.3附近。

原文据此论证：ZeRO使可训练参数规模从8.3B跃升至17B（Turing-NLG），同时困惑度反而更低，证明内存优化未以模型质量为代价。该图作为论文方法验证阶段的核心实验证据，与表8（不同ZeRO配置下的显存分配）相互呼应，共同支撑"ZeRO赋能SOTA大规模模型训练"的整体技术叙事。

### Figure 6 (p.16) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig06.png]]
*整页渲染: ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]]*
> [!quote] caption
> Max model size .

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

**1）核心对象与数据**：图分两子图。左图在固定 batch size=16 下，测试 ZeRO Config 1–5 可训练的最大模型规模：Config 1≈40B、2≈60B、3≈50B、4≈140B、5≈150B；右图展示对应缓存占用（GB），Config 1–3 仅含 40B 模型（约 24–30 GB），Config 4–5 同时给出 40B（≈20 GB）与 100B（≈27–30 GB）模型的内存开销。

**2）关键技术结论**：Config 3→4 之间出现数量级跃升（50B→140B），而缓存占用几乎不增反降，证明突破 GPU 显存瓶颈的关键在于 Config 3/4 引入的 ZeRO-Infinity 思想——将优化器状态等卸载至 CPU/NVMe 内存，使超大规模模型训练成为可能，且单卡内存代价受控。

**3）论文链路作用**：该图作为 ZeRO 三阶段（Pos/G/Pa）→ Infinity 演进路线的量化证据，回答了"为何需要 Stage 3 之后的优化"，支撑后文对万亿参数训练的可行性论证。

### Figure 7 (p.16) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig07.png]]
*整页渲染: ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]]*
> [!quote] caption
> Max cache allo- cated.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图含三子图，量化展示ZeRO五种配置：①固定batch=16时最大模型规模由Config 1–3的40–60B跃升至Config 4–5的140–150B；②40B/100B模型各配置下缓存占用稳定在20–30GB；③170B模型在Config 1–4下无法训练（×标记），仅Config 5达约20Tflops，60B模型单卡吞吐由约12升至约31Tflops。

原文结论：ZeRO-3+（Config 4/5）在缓存相近的前提下将可训练模型规模提升约3倍，并首次实现纯数据并行下的170B级训练，验证零冗余存储可突破显存瓶颈。

论文作用：作为核心定量证据，支撑ZeRO将数据并行扩展至万亿参数规模的方法链路。

### Figure 8 (p.16) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig08.png]]
*整页渲染: ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]]*
> [!quote] caption
> Throughput per GPU. a Bert-Large model for a data sample. Even if we assume the same sequence length and the total number of samples required to train the model, training a 1T model would take 140 days, assuming the same hardware and similar computational eﬃciency.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图以ZeRO配置1–5为横轴：左图显示40B/100B模型缓存由约30/29 GB降至20/26 GB；右图显示60B模型在配置4达约35 Tflops，170B仅配置5可运行，约21 Tflops。说明深层配置可兼顾内存与吞吐，使超大模型训练可行；据此估算1T BERT-Large训练约需140天，为ZeRO方案选择和万亿参数扩展提供量化依据。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.11) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab01.png]]
> [!quote] caption
> Per-device memory consumption of diﬀerent optimizations in ZeRO -DP as a function of DP degree . Bold-faced text are the combinations for which the model can ﬁt into a cluster of 32GB V100 GPUs.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心数据**：表1展示 7.5B/128B/1T 三种模型，在 P_os、P_{os+g}、P_{os+g+p} 三种 ZeRO-DP 优化阶段下，每设备显存随 DP 度（1→1024）的变化。如 7.5B 模型：P_os 阶段 DP=1 需 120GB；引入 P_{os+g+p} 后，DP=64 降至 31.4GB（加粗，<32GB）；1T 模型仅在 P_{os+g+p}、DP=1024 时降至 15.6GB 才可装入。

2) **关键技术结论**：随 DP 度和优化阶段递进，每设备显存近似线性下降；加粗单元格表明，通过逐阶段切分 optimizer states → gradients → parameters，大模型可在 32GB V100 集群上训练，验证 ZeRO-DP 三阶段切分的必要性与可扩展性。

3) **论文作用**：定量支撑 ZeRO"分而治之"核心思路，为后文图1（内存分解）与万亿参数训练可行性论证提供数据基石。

### Table 2 (p.13) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab02.png]]
> [!quote] caption
> Maximum model size through memory analysis (left) and the measured model size when running with ZeRO-OS (right). The measured model size with Po​s matches the theoretical maximum, demonstrating that our memory analysis provides realistic upper bounds on model sizes.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表2对比"理论最大模型容量"（内存分析）与"实际测量容量"（ZeRO-OS运行）。随MP从1增至16、GPU从64扩至1024：Baseline理论容量由2B→32B，实测1.3B→20B；ZeRO-DP(Pos)理论7.6B→121.6B，实测6.2B→100B；Pos+g+p理论上限可达128B→2T。论文据此论证两点：①实测值贴近理论上限，证明内存分析给出的容量边界现实可达；②仅Pos分片即可将可训规模提升约5倍，1024卡可实测训练100B模型。该表为ZeRO方法提供量化锚点，支撑"突破万亿参数训练瓶颈"的核心主张，并衔接Figure 2中吞吐量与加速比的对比实验。

### Table 3 (p.18) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab03.png]]
> [!quote] caption
> ZeRO conﬁgurations

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**说明：** 图片仅显示表格标题"Table 3: ZeRO configurations"及其下方的正文片段，未见具体行列数据，故结合上下文推断。

1）**核心对象与结构**：Table 3 应列出 ZeRO 各阶段配置（ZeRO-DP、ZeRO-OS、ZeRO-P、ZeRO-Pos+g、ZeRO-100B）的并行度与所分片的状态（优化器状态/梯度/参数），并标注 100B 模型下每 GPU 的 batch size 与可扩展的 DP degree。

2）**关键结论**：随着 DP degree 提升，ZeRO-100B 单卡可容纳更大 batch，提升算术强度（arithmetic intensity），从而驱动 Figure 3 中 60B 模型实现 38 TFlops/GPU、聚合 15 PFlops 的超线性扩展与 10× 加速。

3）**论文作用**：作为方法配置表，与 Figure 3 的扩展性实验直接对应，是"技术配置→性能收益"论证链的桥梁，并衔接 §10.4"民主化大模型训练"的推广讨论。

### Table 4 (p.19) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab04.png]]
> [!quote] caption
> Conﬁgurations for diﬀerent model sizes, number of layers, and hidden dimensions (HD) across Figures 2, 3, 4.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明**：图像仅显示了 Table 4 的标题与下方正文段落，**表格的列与数据行并未呈现在该裁图中**，因此具体数值依据缺失。以下结合标题与原文 Figure 4 论述做联合解读：

**1) 核心对象与结构**：Table 4 列出 Figure 2/3/4 中所用各规模模型的**参数量（L）、层数（Layers）、隐藏维度（HD）、注意力头数**等配置，构成横轴变量，使读者能复现 throughput/memory 曲线。

**2) 关键结论**：配合 Figure 4（ZeRO-DP 数据并行吞吐量散点图），该表说明 ZeRO-DP 通信开销随模型规模**次线性增长**——从 1.5B 到 100B+ 模型仍能保持高吞吐，论证 ZeRO 对万亿参数训练的可行性。

**3) 链路作用**：Table 4 是实验的**配置基线表**，贯穿 Figures 2–4，为 memory reduction、billion-scale throughput、trillion-scale projection 三组实验提供统一参数锚点，支撑后续 P_a+cpu、混合精度等章节的横向比较。

### Table 8 (p.23) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab08.png]]
> [!quote] caption
> Model configurations for Figure 5 related to memory allocated with different ZeRO configurations.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 图文联合解读**

Table 8 列出 Figure 5 中各 ZeRO 配置对应的模型参数，共 7 行：
- **40B（5 行重复）**：ZeRO、400 GPU、MP=16、50 层、隐藏 8192、32 头、batch 16、总 batch 400；
- **100B（2 行重复）**：同硬件配置，125 层、64 头、batch 32、总 batch 800。

固定硬件（400 GPU、MP=16、hidden=8192），规模扩展通过加层（50→125）、增注意力头（32→64）和翻倍 batch 实现，论证 ZeRO 配合张量并行即可支撑 100B 量级训练。该表为 Figure 5 内存分配柱状图提供统一配置基准，与 Figure 8 吞吐量分析互补，共同支撑 ZeRO 训练万亿参数模型的核心结论。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\frac{batch \times seq\_length \times n \times h}{B_{gpu}} \leq \frac{24 \times n \times h^2}{B_{data}}
$$

## 相关论文

- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core
- [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] — GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey
- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[muon-is-scalable-for-llm-training]] — Muon is Scalable for LLM Training

## 技术点深读（DEEP）

![[deep/zero-memory-optimizations-toward-training-trillion-parameter-models]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/zero-memory-optimizations-toward-training-trillion-parameter-models.txt`（67057 字符）供引用检索。