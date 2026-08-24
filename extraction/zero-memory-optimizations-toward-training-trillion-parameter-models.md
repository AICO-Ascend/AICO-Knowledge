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
> 【图文联合解读】**图4（左半）联合解读**

**核心内容**：横轴为模型规模1.5B–13B参数，纵轴为单卡吞吐（Tflops）。绿圆点为ZeRO-DP，橙三角为Baseline-DP，蓝虚线标示4.5 Pflops聚合吞吐（≈35 Tflops）。ZeRO-DP在1.5B–8B规模维持40–47 Tflops峰值；10B起降至约35、21 Tflops。Baseline-DP仅在≤1.5B处出现约39与约18 Tflops两点。

**技术结论**：① ZeRO-DP在≤8B规模下单卡效率逼近理论峰值，并显著高于Baseline-DP；② 模型规模超过8B后，受显存限制batch size被迫减小，吞吐随之下降；③ 但即便降速，ZeRO-DP仍可训练Baseline-DP根本装不下的13B模型，验证其规模可扩展性。

**论文作用**：与Fig2、3及Table 4共同构成ZeRO吞吐量分析链，为"训练万亿参数模型"的核心主张提供效率与规模双重证据。

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
> 【图文联合解读】**图文联合解读：**

图7由三个子图组成，对比ZeRO阶段1–5：
1) **左图**（固定batch=16）：阶段1–3最大模型约40–60B，阶段4–5跃升至140B/150B。
2) **中图**（缓存分配）：40B模型阶段1约29GB，阶段4–5降至约20GB；100B模型阶段4–5约26–29GB，说明缓存与模型规模解耦。
3) **右图**（单卡吞吐）：60B模型阶段4达约35 Tflops峰值；170B模型仅阶段5可行（约21 Tflops）。

**技术结论**：ZeRO阶段4–5在保持缓存恒定（≤30GB）的前提下，将可训练模型规模提升约3倍、吞吐提升近3倍，验证"内存优化可换来模型规模与算力效率的双重扩展"。

**论文作用**：作为支撑ZeRO可训练万亿参数模型的核心实证，连接内存优化理论与大规模训练可行性。

### Figure 8 (p.16) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig08.png]]
*整页渲染: ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]]*
> [!quote] caption
> Throughput per GPU. a Bert-Large model for a data sample. Even if we assume the same sequence length and the total number of samples required to train the model, training a 1T model would take 140 days, assuming the same hardware and similar computational eﬃciency.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**【核心对象与数据】** 图分两栏。左栏"Cache Allocated"显示40B模型缓存随ZeRO Config 1–5从30GB→20GB递减，100B仅Config 4–5可行（30/27GB）；右栏"Throughput per GPU"显示60B吞吐12→36→32 TFlops递增，170B仅Config 5达约20 TFlops，其余均OOM（×）。

**【关键结论】** Config 5同时实现缓存最小化与吞吐峰值，使170B模型从不可行变为可训练，验证"内存切分不损计算效率"的ZeRO核心命题。

**【论文作用】** 与表8显存分配互证，共同支撑"内存优化推动可训练规模跃升至T级"的整体技术叙事，奠定方法验证阶段的关键实验证据。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.11) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab01.png]]
> [!quote] caption
> Per-device memory consumption of diﬀerent optimizations in ZeRO -DP as a function of DP degree . Bold-faced text are the combinations for which the model can ﬁt into a cluster of 32GB V100 GPUs.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文解读：**

1）**核心对象与结构**：表格量化展示 7.5B、128B、1T 三档模型在 DP 度为 1/4/16/64/256/1024 时，ZeRO-DP 三种分区粒度（仅优化器状态 P_os、+梯度 P_os+g、+参数 P_os+g+p）下的单卡显存占用（GB）。粗体标注 32GB V100 可容纳组合：7.5B 在 DP=4 的 P_os+g+p（30GB）、DP=16 的 P_os+g（21.6GB）、DP=64 的 P_os（31.4GB）；128B 仅在 DP=64 的 P_os+g+p（32GB）；1T 仅在 DP=1024 的 P_os+g+p（15.6GB）可行。

2）**关键结论**：分区粒度越细，可行 DP 度越低即可装入显存——证明 ZeRO-DP 通过分片 P+g+os，可将万亿参数模型的单卡显存压至 15.6GB，论证"商用 GPU 集群训练万亿模型"的可行性。

3）**论文作用**：为 ZeRO 方法论提供量化可行性证据，与图1（显存组成分解）形成"为什么能省→省后结果"完整论证链，是支撑全文核心主张的关键数据表。

### Table 2 (p.13) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab02.png]]
> [!quote] caption
> Maximum model size through memory analysis (left) and the measured model size when running with ZeRO-OS (right). The measured model size with Po​s matches the theoretical maximum, demonstrating that our memory analysis provides realistic upper bounds on model sizes.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**核心数据**：表格展示不同MP(1–16)、GPU数(64–1024)下的最大理论模型规模与实测规模。左侧理论值：Pos从2B增至32B，Pos+g增至121.6B，Pos+g+p增至230.4B；右侧ZeRO-DP实测Pos从1.3B增至20B，PoS实测从6.2B增至100B。

**技术结论**：PoS实测值（如64卡时6.2B）与其理论上限（7.6B）接近匹配，证明论文提出的内存分析模型给出了现实可达的上界，而非仅理论推测。

**论文作用**：该表与图2的吞吐量数据互补——图2强调性能加速，本表则验证**可扩展性边界**，即ZeRO-OS通过切分优化器状态(Pos)、梯度(PoS)、参数(PoS+p)，可在千卡级GPU上训练达万亿参数模型，支撑全文"突破万亿参数训练"的核心主张。

### Table 3 (p.18) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab03.png]]
> [!quote] caption
> ZeRO conﬁgurations

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明：图像中 Table 3 仅显示标题"ZeRO configurations"，具体表格内容未在可见区域内呈现，以下结合论文文本与已有认知进行解读。**

**1) 核心对象与结构**：该表对比 ZeRO 不同阶段（P_os 仅切分优化器状态、P_os+g 切分优化器状态+梯度、P_os+g+p 三者全切分）在不同 DP 度（如 64、128、256、1024…）下，单 GPU 的模型状态（优化器状态、梯度、参数）、残差状态（激活、缓冲）及总显存占用，量化展示显存压缩倍数（约 4×→8×→线性可至 N 倍）。

**2) 关键结论**：论证 ZeRO 通过逐步切分三类模型状态，可在固定显存下支撑的参数量随 DP 度线性扩展，文中进一步指出 ZeRO-100B 可在 128 GPU 上训练 13B 模型无需 MP，每 GPU 吞吐 >40 TFlops，比纯 DP（最大 1.4B，<20 TFlops）显著提升。

**3) 在论文中的作用**：Table 3 是 ZeRO 方法部分的内存分析基石，为 Figure 3（60B 模型超线性扩展、15 PFlops 聚合性能）与 Figure 4（民主化训练）提供量化依据，是从理论显存推导走向大规模实验验证的关键桥梁。

### Table 4 (p.19) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab04.png]]
> [!quote] caption
> Configurations for different model sizes, number of layers, and hidden dimensions (HD) across Figures 2, 3, 5.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表4给出Figure 2与Figures 3、5中各模型规模的（层数, HD）对照表。Figure 2：1.5B(48,1600)、8B(72,3072)、40B-60B(88/132,4096)、80B-170B(100/125/150,8192)、140B-170B(175/212,8192)；Figures 3/5：1.16B-2.5B(24/34/54,1920)、4B(64,2304)、6B-8B(52/72,3072)、10B-13B(50/54/58/62,4096)、60B(75,8192)。该表统一了从1.16B到170B九个量级实验的模型规格，使ZeRO-DP等吞吐量对比具备可比性，是论文大规模训练实验设计的配置基线，保障了Figure 2/3/4/5结论的一致性与可复现性。

### Table 8 (p.23) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab08.png]]
> [!quote] caption
> Model configurations for Figure 5 related to memory allocated with different ZeRO configurations.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 图文联合解读**

该表列出 Figure 5 所用模型的配置：均为 ZeRO 模式，规模涵盖 40B（400 卡、MP=16、50 层、hidden=8192、32 头、batch=16/总 batch=400）与 100B（同硬件、125 层、64 头、batch=32/总 800），统一 8192 隐层维度，便于纯显存分配对比。

表 8 与 Figure 5 互证：在相同硬件与并行设置下，**ZeRO 仅靠切分优化器状态/梯度/参数即可显著压低每卡显存**，从而将可训练模型从 8.3B 抬升至 17B（Turing-NLG）甚至 100B 级别，且模型质量（困惑度）不降反升。

在论文论证链中，表 8 是"ZeRO 方法有效性"的**配置基座**，支撑吞吐与万亿级可行性论证，与正文 SOTA 结果、表 7 共同完成"内存优化→规模跃升→质量无损"的闭环证明。

### Table 10 (p.24) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab10.png]]
> [!quote] caption
> Model conﬁgurations for Figure 7 related to evaluating maximum model sizes vs throughput while using only data-parallelism.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表为Figure 7（纯数据并行下最大模型规模 vs 吞吐量实验）提供具体配置：列出隐藏维度（256–3072）、层数、注意力头数及对应模型规模（约1.4B–13B参数），作为扫描吞吐量曲线的输入点。

原文借此论证：（1）硬件约束为400 GPU，GPU数须为MP整数倍；（2）基线选用能容纳模型的最小2的幂次GPU数（如170B模型用256卡），使其通信开销更低，反衬ZeRO优势；（3）实验比较"每GPU性能"而非聚合吞吐，确保公平对比。

该表在论文链路中起**实验设定基准**作用，奠定Figure 7吞吐量-规模曲线的数据基础，是支撑ZeRO相对基线在纯DP场景下仍可训练更大模型这一结论的实证支柱。

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