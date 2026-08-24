---
paper_num: "48"
title: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM"
authors: ""
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2104.04473"
pdf: "papers/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm.pdf"
slug: "efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm"
tags: [training, architecture]
---

# Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM

> [!abstract] 摘要（原文）
> 1\. 🎯 针对GPU内存限制和训练时间过长等大规模语言模型挑战，本文提出了PTD-P（Pipeline, Tensor, Data Parallelism）组合并行策略。 2. 🚀 PTD-P通过引入新颖的交错式流水线调度（interleaved pipelining schedule）和Scatter/Gather通信优化，显著提高了吞吐量，同时保持内存效率。 3. 💪 在3072个A100 GPU上，该方法为万亿参数模型实现了502 petaFLOP/s的总吞吐量，达到单GPU理论峰值的52%，使得训练时间可缩短至约3个月。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2104.04473
- **本地 PDF**: `papers/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm.pdf`
- **页数**: 13

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig01.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p01.png]]*
> [!quote] caption
> Trend of sizes of state-of-the-art Natural Language Pro- cessing (NLP) models with time. The number of floating-point op- erations to train these models is increasing at an exponential rate.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图1图文联合解读**

图1位于论文首页右侧，为一张折线图：横轴为年份（2018–2021），纵轴为参数量（对数刻度，单位十亿，范围10⁻²–10³），按时间顺序标注五个代表性NLP模型——ELMo(94M)、BERT-L(340M)、GPT-2(1.5B)、Turing-NLG(8.3B)、GPT-3(175B)，红色虚线拟合显示参数规模近指数增长，约每1–1.5年放大一个数量级。

原文借此为Abstract中两大瓶颈提供量化证据：训练SOTA模型所需FLOPs呈指数增长，而GPU显存有限使大模型难以装入单机/单卡，迫切需要新的模型并行方法。

该图作为引言动机图，引出Megatron-LM提出的**张量并行+流水线并行**方案，并自然衔接后文Table 1对1B–1T参数GPT模型的弱扩展吞吐实验，构成"问题驱动—方案提出—规模验证"的完整逻辑链。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig02.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]]*
> [!quote] caption
> Combination of tensor and pipeline model parallelism (MP) used in this work for transformer-based models.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示 N_t=2、N_p=2 的二维正交并行：每层 Transformer 内含 Self-Attention 与 MLP 模块，被横切为 Tensor MP partition #1/#2，权重/激活经蓝虚线（all-reduce）在 2 张 GPU 间同步；不同层分属 Pipeline MP #1/#2，沿绿色箭头串行。

**论证结论**：层内张量并行平摊权重与激活显存，层间流水线并行扩展深度，二者正交使单卡显存降为 1/(N_t·N_p)，是 Table 2 中 GPT 扩至 530B 参数规模的架构基础。

**论文链作用**：为 Section 3 并行策略推导与 Section 5 弱扩展性实验（N_t=N_p=8 等配置）提供可视化与硬件映射前提，奠定"张量×流水线"正交分解的整体方法框架。

### Figure 3 (p.3) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig03.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]]*
> [!quote] caption
> GPipe pipeline schedule with forward passes (blue) for all microbatches (represented by numbers) followed by backward passes (green). The gray area represents the pipeline bubble. For simplicity, we assume that the backward pass takes twice as long as the forward pass. The efficiency of the pipeline schedule does not depend on this factor. Each batch in this example consists of 8 microbatches, and

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心对象与结构**：图中展示 GPipe 流水调度在 4 个 Device（Device 1–4）上的时间—任务分配。每个 mini-batch 被切分为 8 个 micro-batch（编号 1–8），先依次执行前向（蓝色 1→8）再依次执行反向（绿色 8→1），灰色区域表示设备空闲的"流水线气泡"，右侧"Pipeline flush"分界线后开始下一批（9–16）。

2) **关键技术结论**：气泡（灰色）产生于流水线首尾的填充与排空阶段，其占比随 micro-batch 数 m 与流水级数 p 之比（p−1/m）决定；反向耗时设为前向 2 倍，但调度效率与该比值无关，仅由气泡比例主导——这是 GPipe 的固有瓶颈。

3) **在论文中的作用**：Figure 3 揭示传统 GPipe 的气泡开销，以此作为动机，引出本文提出的 Interleaved 1F1B 调度策略（在后续 Figure 中展示），通过交错前反向显著缩小气泡，从而提升大规模 Transformer 在 GPU 集群上的训练效率，构成方法部分的核心改进点。

### Figure 4 (p.3) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig04.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]]*
> [!quote] caption
> Default and interleaved 1F1B pipeline schedules. The top figure shows the default non-interleaved 1F1B schedule. The bottom figure shows the interleaved 1F1B schedule, where each device is assigned multiple chunks (in this case, 2). Dark colors show the first chunk and light colors show the second chunk. The size of the pipeline bubble is smaller (the pipeline flush happens sooner in the interleav

> [!tip] 技术解读（多模态）
> 【图文联合解读】# Figure 4 图文联合解读

**1) 核心对象与结构**：上图为4设备默认非交错1F1B流水线，每设备单chunk，前向(深蓝)预热4个micro-batch后进入1F1B稳态，尾部灰色气泡含一段空闲；下图为交错1F1B，每设备分配2个chunk（深/浅色区分），micro-batch数翻倍至约24+，同色段对应同一chunk内的前/反向，灰色气泡显著缩短。

**2) 关键技术结论**：通过将多chunk分配给同一设备、虚拟扩大流水线深度P，使稳态期 in-flight micro-batch 数加倍，等效缩小编排/排空阶段气泡占比，从而提高流水线并行利用率、降低单步时间。

**3) 在论文中的作用**：作为Megatron-LM面向GPU集群大模型训练的核心创新之一，与张量并行、序列并行共同构成"TP+PP+DP"三级并行框架，支撑万亿参数级Transformer的高效端到端训练。

### Figure 5 (p.5) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig05.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p05.png]]*
> [!quote] caption
> Blocks of transformer model partitioned with tensor model parallelism (figures borrowed from Megatron [40]). 𝑓and 𝑔 are conjugate. 𝑓is the identity operator in the forward pass and all- reduce in the backward pass, while 𝑔is the reverse. relevant for the pipeline bubble size. We qualitatively describe how communication time behaves and present cost models for amount of communication; however, we d

> [!tip] 技术解读（多模态）
> 【图文联合解读】图(a)将MLP权重按列切分A=[A₁,A₂]与B=[B₁,B₂]至两块GPU：X经f（恒等）复制后分别做XAᵢ→GeLU得Y₁、Y₂，由g全归并为Y=GeLU(XA)，再切分B线性映射输出Z。图(b)沿注意力头切分Q=[Q₁,Q₂]、K、V，各GPU独立完成Q·Kᵀ→Softmax→乘V后由g归并。前向f恒等、g为all-reduce；反向二者互换，保证X梯度仅一次跨GPU通信。论文据此论证：tensor-parallel模块每两次GEMM间各插入一次all-reduce，单次通信量∝隐藏维度h、可与计算重叠，从而在千亿参数规模下维持近线性扩展，支撑PTD-P方案的整体可行性。

### Figure 6 (p.5) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig06.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p05.png]]*
> [!quote] caption
> Fraction of time spent idling due to pipeline flush (pipeline bubble size) versus data-parallel size (𝑑), for different numbers of GPUs (𝑛) and ratio of batch size to microbatch size (𝑏′ = 𝐵/𝑏).

> [!tip] 技术解读（多模态）
> 【图文联合解读】图以对数刻度数据并行规模d（1→64）为横轴、气泡占比（0–1.0）为纵轴，呈现n=32/128、b′=B/b∈{32,128,512}四组曲线。关键数据：①n=32,b′=32时，d=1处气泡≈0.97、d=32降至0；②n=128,b′=512全程仅约0.12–0.25；③n=128,b′=128即便d=64气泡仍≈0.50。结论：b′（每阶段microbatch数）是气泡主导因素——b′越大气泡越低；固定b′时n↑（即流水线深度↑）气泡随之上升。论文借此量化"流水线空泡与并行配置的关系"，为数据并行度与微批规模的选择提供实验依据，支撑整体并行策略与调度优化的论证。

### Figure 7 (p.6) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig07.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p06.png]]*
> [!quote] caption
> Per-GPU throughput versus microbatch size for a GPT model with a billion parameters (128 attention heads, hidden size of 4096, 4 transformer layers).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图7联合解读：**

1) **核心数据**：1B参数GPT模型（128头/h=4096/4层）的单卡吞吐量随microbatch变化曲线。尺寸1→16时，每GPU吞吐量由约68 TFLOP/s单调升至约91 TFLOP/s，但增益递减明显（1→2增约9，8→16仅增约2），呈对数饱和趋势。

2) **关键结论**：增大microbatch可摊薄kernel launch等固定开销、提升GPU利用率；存在明显"甜点区"（约8–16），过小则算力浪费，过大收益饱和。

3) **作用定位**：作为单卡baseline，验证microbatch对计算效率的影响，为后续张量并行与流水线并行的batch配置提供经验依据，是模型并行前确认最优工作负载的关键前置实验。

### Figure 8 (p.6) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig08.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p06.png]]*
> [!quote] caption
> Behavior of normalized estimated throughput (time com- puted as 𝑡= (𝑏′/𝑏+ 𝑝−1) ·  𝑡𝑓(𝑏) + 𝑡𝑏(𝑏)) with respect to the mi- crobatch size 𝑏for the same GPT model from Figure 7.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**Figure 8 图文联合解读**

1) **核心内容**：展示同一GPT模型在总batch size=128（蓝圆）与512（橙菱）下，归一化吞吐随microbatch size *b*∈{1,2,4,8,16} 的曲线。蓝线在 *b*=2–4 达峰≈1.10，*b*=16 骤降至≈0.75；橙线在 *b*=4 达峰≈1.22，*b*=16 仍保持≈1.11，整体更平稳且始终高于蓝线。

2) **关键技术结论**：microbatch 存在最优值——*b* 太小则 GPU kernel 效率低（*t_f*/*t_b* 大），*b* 太大则流水线 bubble 成本（*p*−1 项）激增；更大的总 batch（如512）能更稳定地承受较大 microbatch。

3) **论文中的作用**：与 Fig.7（*t_f*/*t_b* 标度）配套，将"单步时间"与"流水线 bubble"两类代价合成吞吐公式，量化 microbatch 调优权衡，是 Megatron-LM 分布式训练配置准则的核心实验支撑。

### Figure 9 (p.7) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig09.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p07.png]]*
> [!quote] caption
> Scatter/gather communication optimization. Light blue blocks are layers in the first pipeline stage, and dark blue blocks are layers in the second pipeline stage. Without the scatter/gather optimization, the same tensor is sent redundantly over inter-node

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图9解读：**

**1）核心对象与结构：** 图以4块GPU（编号1–4）分属两个节点的流水线阶段（浅蓝块GPUs 1、2为阶段一，深蓝块GPUs 3、4为阶段二）为对象。(a) 中节点内NVLink用于层间通信，跨节点InfiniBand需传输完整红色张量块；(b) 中发送端按头维度将张量切分为若干小块（浅红色）经InfiniBand分发，接收端通过all-gather重新拼合为完整张量（深红色）。

**2）关键技术结论：** scatter/gather优化把InfiniBand链路传输的张量从完整粒度降为分片粒度，等效降低了跨节点带宽占用，同时保持计算结果等价。

**3）在论文中的作用：** 该图是Megatron-LM张量并行–流水线并行跨节点通信优化的核心论据，支撑其在大规模GPU集群上保持高扩展效率的整体方法链。

### Figure 10 (p.8) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig10.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p08.png]]*
> [!quote] caption
> Throughput per GPU of PTD-P and ZeRO-3 for two differ- ent GPT models (the 175B GPT-3 model is shown with dotted lines, and the 530B model is shown with solid lines). Global batch sizes are fixed and ZeRO-3 is used without any model parallelism.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图10核心展示：在固定全局batch size下，175B（虚线）与530B（实线）GPT模型分别用ZeRO-3（蓝）与PTD-P（橙）训练时，单卡吞吐（Achieved teraFLOP/s per GPU）随GPU数（768–1920）的变化。定量看：PTD-P 530B稳定在约170→160，PTD-P 175B约150→143，几无衰减；而ZeRO-3 175B从约143骤降至~45，ZeRO-3 530B从约138降至~50。

原文借此论证：**纯数据并行（ZeRO-3，不含模型并行）随GPU规模增大吞吐严重退化**；PTD-P（张量+流水线并行）保持高且稳定的单卡效率，故千亿级以上模型必须引入模型并行。

该图与Table 1互补，作为"为何需Megatron式TP+PP"的**关键经验依据**，支撑论文弱扩展至1T参数的核心结论。

### Figure 11 (p.9) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig11.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]]*
> [!quote] caption
> Throughput per GPU of pipeline parallelism using two different batch sizes in a weak-scaling experiment setup (model size increases with the pipeline-parallel size). 12 24 36 48 60

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图11 联合解读**

1) **核心数据**：横轴为流水线并行度 P∈{1,2,4,8}，纵轴为单 GPU 吞吐量(TFLOPS/s)。batch=8(蓝)由 P=1 的 ~165 降至 P=8 的 ~88，跌幅近 47%；batch=128(橙)则从 ~178 仅缓降至 ~163(约 8%)，基本水平。

2) **关键结论**：弱扩展(模型随 P 增大)下，pipeline bubble 开销在小 batch 时无法被摊薄，导致每 GPU 吞吐显著下降；而 batch 足够大时，bubble 被掩盖，pipeline parallel 接近线性扩展。

3) **在论文中的作用**：该图支撑"pipeline parallelism 需配合足够大的 micro-batch 才能高效"的核心论点，与文中 1F1B 调度分析互为印证，是论证大规模训练组合策略(tensor+pipeline+data)可行性的关键实验证据。

### Figure 12 (p.9) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig12.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]]*
> [!quote] caption
> Throughput per GPU of interleaved and non-interleaved schedules for a GPT model (175 billion parameters) on 96 GPUs. and a microbatch size of 1. As we increase the number of pipeline stages, we also increase the size of the model by proportionally increasing the number of layers in the model, e.g., with a pipeline- parallel size of 1, we use a model with 3 transformer layers and 15 billion paramet

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图横轴为 batch size（12–60），纵轴为每 GPU 实现的 teraFLOP/s，蓝色圆点为非交错（non-interleaved）调度，橙色菱形为交错（interleaved）调度，对比 175B 参数 GPT 模型在 96 GPU 上的吞吐。可读关键数据：BS=12 时非交错约 82、交替约 119（差距最大 ~37 TFLOP/s）；BS=24 时约 109 vs 134；BS=36 时约 122 vs 141；BS=48 时约 130 vs 143；BS=60 时约 135 vs 146，随 batch 增大差距收窄并趋于饱和。

**技术结论：** 交错调度在各 batch 下均显著优于非交错，且在小 batch 时收益更突出，证明通过将模型层切分为更细的子阶段（虚拟阶段）并交替执行，能有效缓解流水线气泡。

**论文作用：** 该图为本文核心创新——Interleaved 1F1B 流水线并行调度——提供了 175B 大规模模型上的端到端性能证据，是支撑该调度方案有效性的关键实验图。

### Figure 13 (p.9) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig13.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]]*
> [!quote] caption
> Throughput per GPU of various parallel configurations that combine pipeline and tensor model parallelism using a GPT model with 162.2 billion parameters and 64 A100 GPUs.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图13展示64块A100训练162.2B参数GPT模型时，五种(流水线并行度, 张量并行度)=(2,32)/(4,16)/(8,8)/(16,4)/(32,2)配置下的单GPU吞吐量(TFLOPS/s)。两条曲线分别对应batch=32(蓝)与128(橙)：batch=128全程高于batch=32，前者在(8,8)处峰值约165 TFLOPS/s，后者峰约142；在高流水线配置(16,4)与(32,2)处大小batch落差最大(差~50–60 TFLOPS/s)，而小batch在(8,8)两侧迅速衰减。

**论证结论**：两种并行的配比显著影响吞吐，二者不可极端化；大batch可有效掩盖流水线空泡(bubble)，使高流水线配置仍保持高性能。

**论文作用**：作为Figure 12(纯张量并行)的对照，本图直接验证了Megatron-LM"流水线并行+张量并行"联合方案的核心主张——通过合理拆分即可高效训练百亿级以上模型，构成其方法学闭环的关键实验证据。

### Figure 14 (p.10) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig14.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]]*
> [!quote] caption
> Throughput per GPU of various parallel configurations that combine data and pipeline model parallelism using a GPT model with 5.9 billion parameters, three different batch sizes, mi- crobatch size of 1, and 64 A100 GPUs. (2, 32) (4, 16) (8, 8) (16, 4) (32, 2) (Tensor-parallel size, Data-parallel size) 0 50 100 150 200

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示5.9B参数GPT在64块A100上不同(流水线并行度,数据并行度)配置的单GPU吞吐量：批大小=32时，从(2,32)的约62 TFLOP/s单调降至(32,2)的约42 TFLOP/s；批大小=512时，从约148降至约90 TFLOP/s。两条曲线随流水线深度增加均呈下降趋势，原文借此论证：**在该模型规模与GPU数量下，数据并行效率高于管道并行**，pure-data-parallel配置最划算，而增大pipeline会因气泡(bubble)开销显著降低每GPU吞吐。该图为论文并行策略选择（Figure 13/14共同构成扩展性实验）提供了量化依据，是支撑"Megatron在并行配置空间仍具高效率"这一整体结论的关键数据点。

### Figure 15 (p.10) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig15.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]]*
> [!quote] caption
> Throughput per GPU of various parallel configurations that combine data and tensor model parallelism using a GPT model with 5.9 billion parameters, three different batch sizes, microbatch size of 1, and 64 A100 GPUs. 1 2 4 8

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与数据**
该图横轴为五种(TP, DP)组合：(2,32)、(4,16)、(8,8)、(16,4)、(32,2)，纵轴为单 GPU 吞吐量 (tFLOP/s，0–200)。三条曲线对应 BS=32(蓝)、128(橙)、512(绿)。起点：BS=512 约 128、BS=128 约 103、BS=32 约 58；随TP增大均持续下滑，至 (32,2) 时三者收敛至约 22–25 tFLOP/s。

**2) 关键技术结论**
原文用以论证：随 TP 规模由 2 增至 32，三批大小曲线均从 ~125 骤降至 ~25 tFLOP/s，根源是 all-to-all 通信开销主导——一味放大张量并行反成性能瓶颈。

**3) 在论文链路中的作用**
作为"组合并行配置敏感性"实验的关键证据，支撑"TP 不应盲目放大、需与 DP 协同配置"的并行策略准则，与 Figure 14/16 共同构成 Megatron-LM 并行规模选择的方法学依据。

### Figure 16 (p.10) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig16.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]]*
> [!quote] caption
> Throughput per GPU of a (𝑡, 𝑝) = (8, 8) parallel configura- tion for different microbatch sizes on a GPT model with 91 billion parameters, for two different batch sizes using 64 A100 GPUs. importance of using both tensor and pipeline model parallelism in conjunction to train a 161-billion-parameter GPT model (32 trans- former layers to support pipeline-parallel size of 32, 128 attention heads, hid

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图16展示在 **(t,p)=(8,8)** 并行、**64卡 A100** 训练 **91B 参数 GPT** 时，单卡吞吐（纵轴 teraFLOP/s，0–200）随 microbatch（横轴 1/2/4/8，对数刻度）的变化，含 batch=128 与 batch=512 两条曲线。**橙色（512）**：约 163→172→160→155，全程近乎平坦，峰值 ≈172 TF/s；**蓝色（128）**：约 155→158→140→120，microbatch ≥4 后明显下滑。

**关键结论**：batch=512 时对 microbatch 大小极不敏感（强鲁棒），逼近算力峰值；batch=128 较大 microbatch 会因整批 microbatch 数少、流水线气泡占比相对增大而损失吞吐。

**在论文中的作用**：作为扩展性实验的一环，量化验证"张量并行 + 流水线并行"组合在千亿参数规模、用较小 microbatch 仍可保近峰效率，为 Megatron-LM 在大规模训练上的方法论高效性提供直接实证支撑。

### Figure 17 (p.11) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig17.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p11.png]]*
> [!quote] caption
> Throughput (in sequences per second) with and without activation recomputation for a GPT model with 145 billion param- eters using 128 A100 GPUs ((𝑡, 𝑝) = (8, 16)). 12 24 36 48 60

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图17联合解读**

该图刻画145B参数GPT模型在128块A100上的吞吐量（sequences/秒）随batch size（1–256，对数刻度）的变化，对比启用与停用activation recomputation（蓝圆 vs 橙菱）。橙色"W/o act. recomp"曲线仅至batch=8即达约4 seq/s，因显存耗尽（OOM）终止；蓝色曲线则持续爬升至batch=256时约7.8 seq/s。值得注意的是在batch≤8区间，无recomp略高（~4 vs ~3），恰好暴露了重计算的算力开销。

原文据此论证：以算力换显存的重计算可将可用batch从8扩展到256，使吞吐量近似翻倍，是百亿级模型训练的必备技术。

其作用在论文整体方法链中，呼应"张量并行+流水并行+混合精度+重计算"的可扩展训练体系，为大规模模型训练落地提供关键memory-saving抓手。

### Figure 18 (p.11) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig18.png]]
*整页渲染: ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p11.png]]*
> [!quote] caption
> Throughput per GPU with and without the scatter/gather optimization for a GPT model with 175 billion parameters using 96 A100 GPUs and the interleaved schedule.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）图表为折线对比图，横轴为批大小（12/24/36/48/60），纵轴为每GPU达成算力（50–150 teraFLOP/s），含两条曲线：未优化（蓝圈）在各批大小下达约107/120/127/130/131 TFLOPS，散射-收集优化（橙菱）达约119/134/142/144/147 TFLOPS。

2）原文借此论证：在96张A100上训练175B参数GPT-3并采用交错调度时，散射-收集通信优化在所有批大小下均稳定优于未优化基线，批大小60时差距约16 TFLOPS（147 vs 131），验证了该优化对张量并行流水线通信瓶颈的缓解效果。

3）该图属于消融/优化效果验证实验，为Megatron-LM在大规模集群上实现高效训练的工程方案提供量化支撑，是证明所提通信优化必要性与有效性的关键实证。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.8) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-tab01.png]]
> [!quote] caption
> Weak-scaling throughput for GPT models ranging from 1 billion to 1 trillion parameters.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文联合解读**（注：图示区域为正文段落，表格本身未直接渲染，依据 caption 与正文描述重建其内容）

1) **核心对象与结构**：表 1 列出 GPT 系列模型（1B–1T 参数）在 24–3072 块 A100 GPU（384 个 DGX A100 节点）上的**弱扩展吞吐**配置，列含参数量、批大小、张量/流水并行度，以及**单 GPU 与聚合 FLOP/s**；最大模型达峰值设备吞吐的 52%，最小为 44%。

2) **关键技术结论**：跨规模呈**超线性扩展**，因模型越大矩阵乘法越大，GPU 利用率提升而通信相对计算时间未显著增加，验证了 Megatron 的 TP+SP 并行在大规模下无明显通信瓶颈。

3) **作用**：该表为论文实验枢纽——既是**端到端训练框架**（含数据加载、优化器、通信、日志）可行性的实证，也是后续用公式（4） `8TP/(nX)` 估算万亿参数训练时间的 X 值来源，支撑"万卡级高效 LLM 训练"的核心论点。

### Table 2 (p.9) ⭐深度解读
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-tab02.png]]
> [!quote] caption
> Comparison of PTD Parallelism to ZeRO-3 (without model paralllelism). The 530-billion-parameter GPT model did not fit on 560 GPUs when using a microbatch size of 4 with ZeRO-3, so we increased the number of GPUs used to 640 and global batch size to 2560 to provide a throughput estimate (relevant row

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读：**

1）**核心对象与数据**：对比 ZeRO-3 与 PTD 两种并行方案在 174.6B / 529.6B 参数 GPT 模型上的吞吐量。ZeRO-3 仅支持数据并行，174.6B 在 384 GPU、mb=4 时仅 144 TFLOP/s/卡、需 90 天；529.6B 须扩至 640 GPU 才可容纳（mb=4，batch=2560*），仅 138 TFLOP/s/卡、169 天。PTD（TP=96/280）同等规模达 153–171 TFLOP/s/卡，529.6B 在 560 GPU 上 156 天、2240 GPU 缩至 42 天。

2）**论证结论**：呼应 Figure 2——张量并行（层内切分）+ 流水线并行（层间切分）的正交组合，使 PTD 在更少 GPU 上即可装下更大模型，并保持显著高于 ZeRO-3 的每卡算力与训练效率。

3）**论文作用**：以量化对比实证 PTD 方案在大规模训练中的可行性，支撑全文"张量+流水线正交扩展"的核心方法论。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
P = 12lh^2\left(1 + \dfrac{13}{12h}+\dfrac{V+s}{12lh}\right).
$$

$$
F=96Bslh^2\left(1 + \dfrac{s}{6h} + \dfrac{V}{16lh}\right).
$$

$$
\text{End-to-end training time} \approx \dfrac{8TP}{nX}.
$$

$$
[Y_1, Y_2]= [\textrm{GeLU}(XA_1), \textrm{GeLU}(XA_2)]. \nonumber
$$

$$
B=\begin{bmatrix} B_1 \\ B_2 \end{bmatrix}, \ Y = [Y_1, Y_2]. \nonumber
$$

$$
\left(b' / b + p - 1\right) \cdot \left(t_f(b) + t_b(b)\right).
$$

## 相关论文

- [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] — From ATOP to ZCube: Automated Topology Optimization Pipeline and A Highly Cost-Effective Network Topology for Large Model Training
- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey
- [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] — MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs
- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core

## 技术点深读（DEEP）

![[deep/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm.txt`（74320 字符）供引用检索。