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
> 【图文联合解读】**核心对象与结构**：左图为ZeRO-DP（绿圆）与Baseline-DP（橙三角）的"单卡吞吐(Tflops)–模型规模(B)"散点对比，蓝虚线标示4.5 Pflops聚合基准；ZeRO-DP在6–8B参数时达峰值约47 Tflops，并可扩展至13B，Baseline-DP仅在1.5B处达约39/18 Tflops。右图为Model-ZeRO-17B（绿）与Megatron-LM-8.3B（橙）的"验证困惑度–迭代次数"曲线，30万次迭代后前者降至~8.8，低于后者~9.3。

**技术结论**：ZeRO-DP在削减显存的同时不牺牲计算吞吐，并使训练规模突破Baseline瓶颈；更大模型带来更优收敛质量。

**论文作用**：与Fig.3（超线性扩展）互补，以吞吐与精度双重实验指标，支撑ZeRO"民主化训练"主张，是Table 3理论分析走向实证落地的关键一环。

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
> 【图文联合解读】**1) 核心对象与结构**：表2对比 MP=1–16（对应 64–1024 GPU）下的**最大理论模型规模**（Baseline / Pos / Pos+g / Pos+g+p 四档）与**实测规模**（Baseline / ZeRO-DP 等）。例如 64 卡时 Baseline=2B、Pos+g+p=14.4B、ZeRO-DP 实测=1.3B；512 卡时 Pos+g+p 理论 115.2B；1024 卡时 Pos+g+p 理论 230.4B / Baseline 仅 32B。

**2) 关键结论**：ZeRO-DP（Pos）实测值与理论上限吻合，证明内存分析给出的上界是**现实可达**的，Pos 阶段即可显著放大单卡可承载参数量（64 卡即从 2B→7.6B）。

**3) 在论文中的作用**：作为 ZeRO 内存建模的**实证验证锚点**，为后文 Pos+g（优化器状态+梯度分片）至 Pos+g+p（参数分片）及 ZeRO-Os 的扩展分析提供正确性依据，构成"理论建模 → 实测校验 → 分阶段扩展"的实验链路起点。

### Table 3 (p.18) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab03.png]]
> [!quote] caption
> ZeRO configurations

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 3 列出5种ZeRO组合配置：左列为ZeRO-DP分区策略（P_os或P_os+g），右列为ZeRO-R残差内存分区（C_B+M_D、+P_a、+P_a+cpu）。每行自上而下逐步叠加分区组件，形成由浅入深的内存优化梯度。

论文借此论证：ZeRO并非单一方案，而是可在DP维度（优化器状态/梯度分区）与R维度（激活检查点、模型、激活分区、CPU卸载）之间灵活组合，形成内存—通信—计算的多阶段权衡策略。

该表是后续实验（如图3的60B吞吐测试、向万亿参数模型扩展）的配置输入矩阵，承担方法栈"配置枚举"的角色，为分级评估不同内存收益提供基础。

### Table 4 (p.19) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab04.png]]
> [!quote] caption
> Configurations for different model sizes, number of layers, and hidden dimensions (HD) across Figures 2, 3, 5.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 解读**

Table 4 罗列 ZeRO-DP 在 Figures 2–4 实验中的模型规模–层数–隐藏维度（HD）配置：1.5B/48层/1600、8B/72/3072、40–60B/88,132/4096、80–170B/100–150/8192、140–170B/175,212/8192；及 1.16–2.5B/1920、4B/2304、6–8B/3072、10–13B/4096、60B/8192。

作者借此论证：随模型从 1.5B 扩至 170B，HD 由 1600 升至 8192、层数最高达 212，ZeRO-DP 仍保持吞吐与显存线性扩展能力。

该表是 Figure 2–4 的"实验参数清单"，为定量论证 ZeRO 在百亿至千亿参数模型上的有效性提供可复现配置声明，是实验章节的支撑性数据底座。

### Table 8 (p.23) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab08.png]]
> [!quote] caption
> Model configurations for Figure 5 related to memory allocated with different ZeRO configurations.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**联合解读（≤220字）：**

表格为Figure 5显存实验的模型配置：均采用ZeRO（共7行），固定400 GPU、MP=16；含40B组（50层、hidden 8192、32头、batch 16、总batch 400，5行对应各分片阶段）与100B组（125层、hidden 8192、64头、batch 32、总batch 800，2行）。

支撑的核心结论：ZeRO通过分片优化器状态、梯度与参数，使单卡显存不再随模型线性扩张，从而在400卡规模下即可训练40B乃至100B模型，为图5中各阶段显存消长曲线提供统一、可比的超参基准。

在论文链路中，本表衔接表7的内存节省量化数据，支撑图5的可视化论证，并与Figure 8（吞吐量/可训练时间估算）共同构成"内存优化→算力可行→质量无损"的完整证据链，是ZeRO赋能SOTA大规模训练叙事的关键实验脚手架。

### Table 10 (p.24) ⭐深度解读
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-tab10.png]]
> [!quote] caption
> Model configurations for Figure 7 related to evaluating maximum model sizes vs throughput while using only data-parallelism.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表10为Figure 7实验的模型配置：128 GPU、MP=1纯数据并行条件下，ZeRO组覆盖1.5B–13B共8档（hidden 1920→4096、layers 34→72、heads 16→32、单卡batch 24→2随模型增大递减）；Baseline组仅1.6B与3.8B两档。对比论证：纯DP无张量并行时，ZeRO可训模型上限（~13B）较Baseline（~3.8B）提升超3倍，说明ZeRO通过分片优化器状态与梯度显著释放显存，使万亿参数训练不必依赖TP即可扩大模型规模，为Fig 7吞吐量-容量曲线提供配置支撑，凸显其内存效率的核心优势。

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