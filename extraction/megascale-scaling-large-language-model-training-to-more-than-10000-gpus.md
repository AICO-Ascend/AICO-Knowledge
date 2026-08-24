---
paper_num: "46"
title: "MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs"
authors: "Ziheng Jiang1,∗Haibin Lin1,∗Yinmin Zhong2,∗Qi Huang1 Yangrui Chen1 Zhi Zhang1 Yanghua Peng1 Xiang Li1 Cong Xie1 Shibiao Nong1 Yulu Jia1 Sun He1 Hongmin Chen1 Zhihao Bai1 Qi Hou1 Shipeng Yan1 Ding Zhou1 Yiyao Sheng1 Zhuo "
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2402.15627"
pdf: "papers/megascale-scaling-large-language-model-training-to-more-than-10000-gpus.pdf"
slug: "megascale-scaling-large-language-model-training-to-more-than-10000-gpus"
tags: [training]
---

# MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs

> [!abstract] 摘要（原文）
> 1\. 🚀 MegaScale是一个用于在超过10,000个GPU上训练大型语言模型(LLM)的生产系统，旨在解决大规模训练中的效率和稳定性挑战。 2. ⚙️ MegaScale通过算法-系统协同设计，整合了模型优化、计算与通信重叠、算子优化、数据管道及网络调优，并利用深度可观测性和鲁棒训练框架实现故障容忍。 3. 💥 该系统在12,288个GPU上训练175B LLM时实现了55.2%的Model FLOPs Utilization (MFU)，比Megatron-LM提升1.34倍，并在数周的实际生产运行中自主修复和恢复了100多次。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Ziheng Jiang1,∗Haibin Lin1,∗Yinmin Zhong2,∗Qi Huang1 Yangrui Chen1 Zhi Zhang1 Yanghua Peng1 Xiang Li1 Cong Xie1 Shibiao Nong1 Yulu Jia1 Sun He1 Hongmin Chen1 Zhihao Bai1 Qi Hou1 Shipeng Yan1 Ding Zhou1 Yiyao Sheng1 Zhuo 
- **arXiv**: https://arxiv.org/abs/2402.15627
- **本地 PDF**: `papers/megascale-scaling-large-language-model-training-to-more-than-10000-gpus.pdf`
- **页数**: 16

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig01.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p02.png]]*
> [!quote] caption
> Data parallel training with ZeRO2. dependencies that contribute to stability issues. We develop a robust training framework to automate fault localization and recovery. We design heartbeat messages encapsulating various forms of information to facilitate real-time anomaly detection and provide early warnings. We implement a suite of diagnostic tests to identify nodes causing disruptions. We optimi

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示 **ZeRO-2 数据并行的计算流水**：两个 Model Replica（GPU）分别输入 Data 0 / Data 1，各自执行 **Forward → Backward → Reduce-Scatter → Update Params → All-Gather**。两副本在 Reduce-Scatter 阶段通过 *"sync grads"* 同步分片梯度，在 All-Gather 阶段通过 *"gather params"* 拉取完整参数。

**论证的关键结论**：相比传统 All-Reduce，ZeRO-2 将**梯度与优化器状态按数据并行维度切分存储**，消除每卡冗余，显著降低单卡显存占用，使超大模型可在数据并行规模上线性扩展。

**在论文中的作用**：该图给出 MegaScale 的**基础并行范式**，作为后续万卡级扩展框架（通信优化、流水线编排、故障定位与心跳检测等）的算子级前提，支撑"超过 10,000 GPU 训练 LLM"的可行性论证。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig02.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p03.png]]*
> [!quote] caption
> Interleaved 1F1B pipeline. update the model. Instead of duplicating model states (like the optimizer states, gradients, and parameters), Zero Redun- dancy Optimizer (ZeRO) [11] shards these states across every data-parallel process. As a result, the traditional all-reduce operations that aggregate gradients are decomposed into sep- arate reduce-scatter and all-gather operations. This is because ev

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示为**3级Interleaved 1F1B流水线调度时序图**：横轴为时间步，每行对应一个stage，方块内数字为微批次ID，**粉红色代表前向（warm-up段）**、**蓝色代表后向（稳态1F1B段）**、灰色为bubble/空闲；两条红虚线将调度切分为**warm-up → 稳态交替执行F/B → cooldown**三阶段，每stage内含多个模型分片（chunk）交叉调度，使前/后向在不同分片上交错进行。

原文借此论证：**交错调度将pipeline bubble率压缩至传统1F1B的1/v**，从而提升吞吐、降低端到端训练时延；该调度是Megatron在万卡级千亿模型（175B）扩展中的核心并行组件，与ZeRO分片策略协同，支撑Table 2所示的强可扩展性实验结论。

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig03.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p04.png]]*
> [!quote] caption
> Overlapping communication in tensor parallelism (TP) and sequence parallelism (SP) with parallel transformer block (PTB). with a large receptive field created by stacking layers of such windowed attention. This enables faster training without com- promising the accuracy. LAMB optimizer. Efficient training at a large scale is often hindered by batch size constraints. Particularly, increasing the ba

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图分三子图：(a) 标准PTB含SP区LayerNorm+All-Gather/Reduce-Scatter与TP区QKV ColParaLinear→Self Attention→RowParaLinear；(b) 将AG融合进ColParaLinear、RS融合进RowParaLinear，消除独立通信节点；(c) 双CUDA流S0(GEMM)与S1(comm)并行，使A×W与all-gather Copy交错、B×W与reduce-scatter交错执行。

**技术结论**：算子级融合＋流级重叠，使TP的集合通信与GEMM计算时间线重合，隐藏通信时延。

**整体作用**：作为Megascale万卡训练系统栈的算子层关键改造，为后续大规模扩展实验提供PTB结构级通信优化基础。

### Figure 4 (p.4) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig04.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p04.png]]*
> [!quote] caption
> The cool-down phase can be viewed as the inverse of the warm-up phase, allowing for the inverse application of the same technique. As for the steady phase, both the forward and backward computation are independent of adjacent communication operations. Taking the backward as an example, as shown in the right part of

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示流水线并行中 stage i 与 stage i+1 的 S/R（Send/Receive）与 FWD/BWD（Forward/Backward）任务调度。顶部为原始序列，S/R 与计算紧邻串行；底部经"Communication Overlap"变换后，**Send 前移至 FWD 之前**、**Receive 后移至 FWD/BWD 之后**，分 Warm-up 与 Steady 两阶段展示。

原文据此论证关键结论：通信可与计算流水重叠，稳态时前向与反向计算均独立于相邻通信操作，cool-down 阶段为 warm-up 的逆过程，可复用同一技术。

该图是 MegaScale 流水线通信重叠优化（与张量并行融合通信共同支撑）的核心图示，构成其在 10K+ GPU 上维持高 MFU 训练效率的基础组件之一。

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig05.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p06.png]]*
> [!quote] caption
> Robust training workflow. interval and help recover the transmission more quickly when the link flapping period is short. 4

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示大规模训练鲁棒性工作流的三层架构：①**Kubernetes层**（含Training Job Info、Evicted Pods、Blocked IPs状态表）；②**Driver控制层**（User API提交作业，Checker周期性发起stop&&check巡检，Log Analysor通过心跳信号触发Checker）；③**Executors执行层**（Executor 0…N，受Kubernetes调度并向Checker回传心跳与检查结果）。

**论证结论**：在万卡级训练中，故障（链路抖动flapping、节点异常）不可避免；该工作流通过"心跳感知→日志分析→Checker巡检→驱逐异常Pod/屏蔽故障IP"的闭环，使Kubernetes快速重建资源，实现训练不中断的自动恢复。

**论文作用**：作为可靠性保障模块的核心架构说明，为后续关于"千卡故障可秒级恢复、万卡训练可连续运行多周"的实验结论提供机制依据，是论文系统设计章节的关键配图。

### Figure 6 (p.8) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig06.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p08.png]]*
> [!quote] caption
> Inconsistent MFU observed in large-scale training. Differ- ent colors denote distinct executions of the same training job. mitigates the bandwidth constraints of HDFS, leading to a substantial reduction in the recovery time. 5

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图6横轴为训练步数（0–30000），纵轴为MFU（0–0.6）。多色折线代表同一训练任务的多次独立执行，MFU整体落在0.35–0.45区间，但波动显著：红色线段（约7000–17000步）MFU仅0.35–0.38，低于蓝/橙/粉/紫/绿等其余执行（约0.40–0.43），同一任务不同run间MFU差异可达5–10%。

论文借此论证：**大规模训练中性能不一致是常态而非异常**——即便软硬件配置相同，跨次执行的MFU仍存在系统性偏差，单次观测无法代表真实训练效率，必须建立可重复、可量化的可靠性度量。

该图在论文链路中作为**现象驱动的开篇实证**，支撑后文提出的全栈诊断工具与故障恢复机制（如HDFS带宽缓解），说明仅靠扩大GPU规模并不能保证稳定高效训练，必须配套工程化可靠性保障。

### Figure 7 (p.8) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig07.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p08.png]]*
> [!quote] caption
> We gather latency data of the computation phase (forward and backward) across devices and average the latency across steps. The aggregated data is visualized host 0 0 1 2 3 host 3 12 13 14 15 host 6 24 25 26 27 host 9 36 37 38 39 host 4 16 17 18 19 host 7 28 29 30 31 host 10 40 41 42 43 host 5 20 21 22 23 host 8 32 33 34 35 host 11 44 45 46 47 host 1 4 5 6 7 host 2 8 9 10 11 DP Comm TP Comm PP Com

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构：** 12台host（0–11）按4×3排列，每台含4个rank，共48个rank；颜色映射计算耗时（浅粉≈2.0s → 深红≈2.5s）。Rank 20以斜纹标注，作为选中示例，通过绿/橙/紫三条虚线箭头分别连接TP、PP、DP三维通信的邻居rank。

**2) 论证的关键结论：** 大多数rank耗时均匀，但host 8的rank 32与host 10的rank 40–41明显偏慢，构成"computational stragglers"；沿PP链路的虚线箭头揭示耗时沿流水线阶段累积传播，3D视图直观暴露三维并行（TP/DP/PP）耦合下的跨维度延迟依赖。

**3) 在论文中的作用：** 作为Megascale诊断工具的可视化证据，证明万卡级训练中存在跨节点、跨并行维度的性能失衡，为后续straggler识别与负载重平衡优化提供分析依据。

### Figure 8 (p.9) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig08.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p09.png]]*
> [!quote] caption
> The trace shows events collected in a pipeline group on a unified timeline. Dependencies become visible when an event is selected.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**核心对象与结构**：该图呈现 Megascale 调试框架的流水线并行轨迹视图。横向为统一时间轴，纵向为同一 pipeline group 内的 4 个 stage（rank[0]、rank[4]、rank[8]、rank[12]，共 16 个 stage 中的子集）。事件块按类型着色：绿色为 forward（f...），橙色为 backward（bac...），灰色为前/反向大块（forwar.../bac...），短箭头显示跨 rank 的数据依赖（选中事件后高亮）。

**论证结论**：图中清晰呈现 1F1B 调度模式——各 stage 交错启动形成流水气泡，forward 波从 rank[0] 向右传播、backward 波回传，可视化工具将这种跨 stage 时序与显式依赖关系一并暴露，便于在大规模训练中定位流水线停顿与通信瓶颈。

**论文作用**：支撑文中 Nezha 大规模分布式调试系统章节，作为"能在万卡规模下对复杂流水线 schedule 做细粒度可视化"的实证。

### Figure 9 (p.10) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig09.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p10.png]]*
> [!quote] caption
> Weak-scaling training performance of Megatron-LM and

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图9解读：**

**1) 图示数据：** 该柱状图展示530B模型在弱扩展设置下（batch size随GPU数同比放大）的MFU对比，横轴为GPU规模（2240/4480/11200），纵轴为MFU(%)。MegaScale在三种规模下MFU分别为54.30%、54.10%、54.30%，几乎水平；Megatron-LM则为49.20%、48.80%、48.20%，两者存在约5–6个百分点的稳定差距，且两条序列随规模扩大均无明显下降。

**2) 关键结论：** 论文以此证明MegaScale相对Megatron-LM具有**规模无关的持续效率增益**——其全栈优化（通信overlap、并行策略、可靠性机制等）在大规模下仍稳定保持约54% MFU，弱扩展性良好。

**3) 论文作用：** 该图是论文"万卡级高效训练"主张的核心量化证据之一，与强扩展、收敛性、故障恢复等实验共同构成对MegaScale系统级性能的完整论证链。

### Figure 10 (p.11) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig10.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p11.png]]*
> [!quote] caption
> The training loss curves in microbenchmark experiments.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图10解读：ADAM与LAMB优化器训练损失对比**

**1) 核心对象与数据**
图(b)展示两条训练loss曲线：蓝色为1×batch_size下的ADAM，橙色为4×batch_size下的LAMB。横轴为已消费tokens（B，0–270B+），纵轴为loss（2–8）。ADAM起点约4.5，LAMB起点近8且在~90B处出现尖峰；两条曲线在~150B tokens后基本重合，最终loss稳定在≈2.2。

**2) 关键技术结论**
证明在batch_size扩大4倍的情况下，LAMB优化器能达到与ADAM（1×batch_size）几乎一致的收敛loss，说明大batch训练不会损失模型质量，验证了LAMB优化器在大batch场景下的有效性。

**3) 在论文中的作用**
此图属于微基准实验（microbenchmark），为整篇论文万卡级训练提供优化器选型依据：在大规模集群中必须使用大batch以摊销通信开销，而本实验证明LAMB可在保持loss不退化的前提下支撑4×batch扩展，是后续端到端万卡训练可扩展性论证的关键支撑。

### Figure 11 (p.11) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig11.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p11.png]]*
> [!quote] caption
> The normalized training loss curve of a real production run on more than 10,000 GPUs for several weeks. This run trains a model with hundreds of billions of parameters on multi-trillion tokens. Different colors indicate training restarts. MegaScale repairs and recovers the training process for over 100 times in presence of failures.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图11联合解读：**

图示万卡规模（10 000+ GPU）训练千亿参数、多token模型的归一化loss曲线：X轴为已消费token比例(0–1)，Y轴为loss。曲线初始≈0.85骤降至~0.2，再缓降至≈0.15；多色段对应100+次故障重启，loss衔接平滑无明显跳变。

**关键结论**：MegaScale的故障检测与恢复机制可在万卡、跨周长周期训练中保持收敛稳定性，多次重启不影响loss趋势。

**论文作用**：作为production-scale端到端验证，证明系统在真实超大规模长周期训练中的鲁棒性与可落地性，是整套方法从单点优化走向规模化可靠训练的最终佐证。

### Figure 12 (p.12) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig12.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p12.png]]*
> [!quote] caption
> The MFU becomes stable after addressing the stragglers and problematic code segments. Different colors represent different training trials with the same setup. executing diagnostic tests is less than 10 minutes. Moreover, the system can catch up to the training progress prior to the crash within 15 minutes from the latest checkpoints, maintain- ing over 90% effective training time rate, which is c

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图12横轴为训练步数（0–30000），纵轴为MFU（0–0.6）。橙色线对应前约1万步，蓝色线对应1万–3万步，两条同配置试验曲线MFU均稳定在约0.48–0.50，仅偶现向下尖刺（落后节点瞬时拖累）。橙色段尖刺稍频，蓝色段更平直，说明排查straggler与问题代码段后MFU趋于平稳。

原文借此图论证：万卡级规模下，经诊断与代码优化，训练利用率可长期保持稳定，支撑"有效训练时间率>90%"的可靠性声明；在论文链路中，它是衔接"问题诊断→针对性优化→长期稳定性验证"实验闭环的关键实证证据。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.9) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-tab01.png]]
> [!quote] caption
> Model configurations.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 表内核心数据：** Table 1 给出两个模型的并行配置——175B（96 层 / 128 头 / hidden=12288 / TP=8 / PP=8）与 530B（105 层 / 160 头 / hidden=20480 / TP=8 / PP=35）。两模型张量并行度 TP 恒为 8，而流水线并行度 PP 由 8 跃升至 35，层数与 hidden 同步放大。

**2) 论证的技术结论：** TP 固定表明节点内 8 路张量并行已是单节点上限；规模扩张时必须通过加深 PP（8→35）将模型切片分摊至更多节点，体现"TP 饱和、PP 扛规模"的万卡并行拓扑设计。

**3) 在论文中的作用：** 该表是后续 MegaScale 框架实验的统一模型基线，所有 MFU、吞吐、容错恢复等万卡级评测均以此配置为输入，是连接并行策略设计与大规模训练实证的关键参数表。

### Table 2 (p.10) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-tab02.png]]
> [!quote] caption
> Strong-scaling training performance for the 175B model. We set the batch size to 6144 when training with 3072 to 12288 GPUs. For 256 to 1024 GPUs, we decrease the batch size to 768 due to GPU memory limit. We report the training time required for training 300B tokens here. The number in parentheses 

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构**：表格对比 MegaScale 与基线 Megatron-LM 在 175B 模型上的强扩展性能。两组批次大小：768（256–1024 GPU，受显存限制）、6144（3072–12288 GPU）。关键数据：12288 GPU 下 MegaScale 单次迭代 6.34 s、吞吐 1984.0k tokens/s、训练 300B tokens 仅 1.75 天、Aggregate 2166.3 PFlops/s、MFU 55.2%；小规模（1024 GPU）MFU 达 59.0%、加速 1.32×。

**2) 关键结论**：MegaScale 在全规模区间均稳定优于 Megatron-LM，MFU 提升幅度 1.19×–1.34×，单次迭代时间与训练总时同步下降，验证其通信/调度优化对万卡强扩展的有效性。

**3) 论文作用**：与 Figure 2（Interleaved 1F1B 流水线）一脉相承，本表以量化数据落地"万卡稳定训练"这一中心主张，构成方法-系统-性能闭环的关键实验证据，支撑 MegaScale 整体论证框架。

### Table 3 (p.11) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-tab03.png]]
> [!quote] caption
> MFU improvement breakdown when training the 175B model with 256 GPUs and batch size 256.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读**

1) **核心数据**：表格以175B模型在256 GPU、BS=256下，逐项累加9个优化对MFU的影响。基线47.7%→最终65.3%，累计提升+17.6pp；其中通信重叠类（TP/PP/DP overlap）合计贡献约+7.2pp，LAMB+BS×3单项贡献最大（+3.0pp），PTB、efficient operators、SWA各贡献1–4.6pp。

2) **关键结论**：证明论文所提各项优化均非冗余——从并行结构（PTB）、注意力（SWA）、三轴通信重叠、算子融合到LAMB，均能独立带来可量化增益，且可叠加。

3) **链路作用**：作为消融式证据，支撑后文"高效优化使千卡级扩展可行"的核心论点，为Figure 3的通信重叠设计与万卡级扩展实验提供量化基础。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\begin{aligned} y = x + \text{MLP}(\text{LN}(x + \text{Attention}(\text{LN}(x)))) \end{aligned}
$$

$$
\begin{aligned} y = x + \text{MLP}(\text{LN}(x)) + \text{Attention}(\text{LN}(x)) \end{aligned}
$$

## 相关论文

- [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] — Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] — From ATOP to ZCube: Automated Topology Optimization Pipeline and A Highly Cost-Effective Network Topology for Large Model Training
- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey
- [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] — Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning

## 技术点深读（DEEP）

![[deep/megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/megascale-scaling-large-language-model-training-to-more-than-10000-gpus.txt`（77210 字符）供引用检索。