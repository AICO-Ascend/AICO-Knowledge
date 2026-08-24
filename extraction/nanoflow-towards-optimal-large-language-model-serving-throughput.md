---
paper_num: "54"
title: "NanoFlow: Towards Optimal Large Language Model Serving Throughput"
authors: "Kan Zhu University of Washington Yufei Gao University of Washington Tsinghua University Yilong Zhao University of Washington UC Berkeley Liangyu Zhao University of Washington Gefei Zuo University of Michigan Yile Gu Univ"
date: "2024/8/23"
arxiv: "https://arxiv.org/abs/2408.12757"
pdf: "papers/nanoflow-towards-optimal-large-language-model-serving-throughput.pdf"
slug: "nanoflow-towards-optimal-large-language-model-serving-throughput"
tags: []
---

# NanoFlow: Towards Optimal Large Language Model Serving Throughput

> [!abstract] 摘要（原文）
> 1. Large Language Models (LLMs) have resulted in a surging demand for planet-scale serving systems, where tens of thou- sands of GPUs continuously serve hundreds of millions of users. Consequently, throughput has emerged as a key met- ric that determines serving systems’ performance. Due to large model sizes and memory-intensive self-attention, LLM serving has been commonly assume

## 元信息
- **发表日期**: 2024/8/23
- **作者**: Kan Zhu University of Washington Yufei Gao University of Washington Tsinghua University Yilong Zhao University of Washington UC Berkeley Liangyu Zhao University of Washington Gefei Zuo University of Michigan Yile Gu Univ
- **arXiv**: https://arxiv.org/abs/2408.12757
- **本地 PDF**: `papers/nanoflow-towards-optimal-large-language-model-serving-throughput.pdf`
- **页数**: 17

## 图表（原文 caption + 页码）

### Figure 1 (p.3) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig01.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p03.png]]*
> [!quote] caption
> Transformer architecture. The operations in the yellow boxes have large batch sizes and share model weight parameters across requests; hence, they are compute-bound. Operations in green boxes require loading a unique KV cache for each request; hence, they are memory-bound. The blue box represents network operations that perform synchronization between operations. • A comprehensive evaluation of Na

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示Transformer按算子瓶颈三色分类：黄色compute-bound（W_Q/K/V/O、Up、Down、Gate 共7类权重共享算子，大batch摊销权重加载）；绿色memory-bound（prefill/decode attention，每请求独享KV cache，小batch避压）；蓝色network-bound（AllGather/AllReduce通信同步）。原文据此论证NanoFlow核心：异构batch+device-stream级算子融合，跨CUDA stream注入micro-batch将串行依赖转并行，实现1.91×吞吐、达理论峰68.5%。此图奠定全文方法论基石——先分类、再调度融合，后续流水设计与实验评估均依托此分类展开。

### Figure 2 (p.5) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig02.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p05.png]]*
> [!quote] caption
> Comparison of network time and compute time. The closer to yellow, the more compute-bound the workload is, whereas the closer to blue indicates the workload is more network-bound. LMSYS-Chat Splitwise

> [!tip] 技术解读（多模态）
> 【图文联合解读】## 图文联合解读

**1. 核心对象与结构**
该热力图以 6 个 LLM（行：LLaMA-3 8B、Mistral 8x7B、LLaMA-2/3 70B、Qwen2 72B、LLaMA-3 405B）×13 种 GPU + Compute Bound 参考列（V100→Ada6000 PCIe）共 78 格，单元格数值为"网络通信时间/计算时间"比值（范围 0.119–2.609）。色编码：黄色(<1)表示计算受限，蓝色(>1)表示通信受限。

**2. 关键结论**
数据显示两条清晰趋势：①**模型越大越偏黄**（如 LLaMA-3 405B 在多数 GPU 上仅 0.119–0.812，呈深黄），说明大模型被 GEMM 主导；②**GPU 越快越偏蓝**（如 LLaMA-3 8B 在 H100/B100/B200/Gaudi 上达 1.008–1.529，Ada6000 上高达 2.609），意味着当算力足够强时，allreduce 等集合通信反成瓶颈。

**3. 在论文方法链中的作用**
该图为 NanoFlow 提出**nano-batch + 通信-计算重叠**提供动机：传统大 batch 在通信受限场景下吞吐不再随 batch 线性增长（因被 allreduce 阻塞），故需将大 batch 拆成 nano-batch 并流水化通信与计算，以榨干通信受限区间的吞吐。

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig03.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p05.png]]*
> [!quote] caption
> Comparison of compute time and memory time.

> [!tip] 技术解读（多模态）
> 【图文联合解读】热力图以5种LLM部署配置（行为LLaMA-3 8B×1、Mistral 8×7B×8、LLaMA-2/3 70B×8、Qwen2 72B×8）×6类负载（列为LMSYS-Chat/Splitwise/ShareGPT及512-512、1024-512、512-1024）为轴，单元值为计算时间与访存时间之比。绝大多数单元格呈黄色（计算受限，0.07–0.68），仅单卡LLaMA-3 8B在512-1024长输出负载下升至1.09、进入浅绿访存受限区；多GPU的大模型比值最低（0.07–0.32），纯计算受限。

图证：LLM推理在模型、部署与负载维度上瓶颈位置显著分散——同一时刻系统内同时存在计算、访存、网络三类受限算子。NanoFlow据此提出按算子类型（GEMM/GEMV/AllReduce）分别流水编排的调度方案，以同时缓解三类瓶颈、提升整体吞吐。

### Figure 4 (p.8) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig04.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p08.png]]*
> [!quote] caption
> Execution pipeline of existing systems. The green, yellow, and blue operations correspond to memory-, compute-, and network-bound operations. Operations in the previous and next layer are denoted by dotted borders. "WASTED" shows the stages in the pipeline where the most constrained resource, compute, is underutilized. Small operations (i.e. layernorm, activation, etc.) are omitted for simplicity.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图以时间轴展示现有LLM推理系统单层执行流水线，依次包含：KQV投影（黄/计算）、DecAttn（绿/访存）、PF Prefill（黄）、Attn.AG（蓝/网络）、O投影、O.AG、UGD大块计算（黄，主导项）、UGD.AR全归约（蓝）；首尾虚线框表示邻层KQV。

**关键结论：** 在KQV-DecAttn、PF-AG、AG-UGD、UGD-AR四段交界均出现"WASTED"空隙，因短小的访存/网络操作（DecAttn、AG/AR）与超长UGD计算（占主导）无法流水填充，导致计算核心在等访存/通信时空转，吞吐受限。

**论文作用：** 此图作为动机图，定量揭示"算力被访存/网络气泡浪费"的结构性瓶颈，直接引出NanoFlow将多层小操作聚合以消除WASTED、提升throughput的核心方案。

### Figure 5 (p.8) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig05.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p08.png]]*
> [!quote] caption
> Interference characteristics between GEMM and GEMV kernels. The points on the x-axis correspond unique GEMM-GEMV implementation pairs. The y-axis denotes the GEMM and GEMV kernels’ normalized performance P. ferent implementations of overlapping kernels exponentially expand the profiling space, resulting in millions of possible configurations. This immense complexity makes exhaustive exploration in

> [!tip] 技术解读（多模态）
> 【图文联合解读】图5展示不同GEMM-GEMV实现配对下的归一化性能P：最优GEMM（蓝线）由左侧~1.0单调降至~0.45，最优GEMV（橙线）由近0升至~1.0，二者呈明显此消彼长；非最优GEMV（灰虚线）在0.1–0.9间剧烈波动。红色参考线标出P≈0.8与P≈0.3两个临界点。

论证两点关键结论：(1) GEMM与GEMV性能存在显著权衡，错配将使GEMV性能跌至非最优路径的~0.1；(2) 不同实现组合形成"数百万种配置"，穷举profile不可行。

作用上，此图作为NanoFlow的motivation，支撑其设计高效性能模型与搜索策略，在不遍历全空间的前提下为硬件选择最优GEMM-GEMV重叠组合，是LLM推理跨核重叠调度的基础实验依据。

### Figure 6 (p.11) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig06.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p11.png]]*
> [!quote] caption
> Execution pipeline of LLaMA-2 70B, automatically generated by NanoFlow. The solid background and shaded background represents input batch 0-768 and 768-2048, respectively. R stands for resource utilization. By overlapping the compute-, memory-, and network-intensive operations, NanoFlow increases compute utilization and improves the serving throughput. data size of the offload is balanced across i

> [!tip] 技术解读（多模态）
> 【图文联合解读】图6展示NanoFlow为LLaMA-2 70B单层自动生成的执行流水线：沿"Layer"时间轴，将KQV计算、Prefill（PF1）、Q/O投影、Up·Gate·Down（UGD1/UGD2 R=0.9）、DecAttn1–4（R=0.4）及AG·AR（R=0.1–0.2）等算子分置计算/内存/网络三条轨道并行排布；实色与格纹背景分别对应batch 0–768与768–2048。原文借此论证NanoFlow通过Prefill Attention、AG→AR Transform等机制，使计算密集（UGD R=0.9）与访存/网络密集（KQV、AR R=0.1–0.4）算子互补重叠，提升整体资源利用率，从而提高服务吞吐。该图是把NanoFlow自动调度能力与端到端吞吐实验相连的核心可视化证据。

### Figure 7 (p.11) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig07.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p11.png]]*
> [!quote] caption
> Offline throughput comparison. NanoFlow outper- forms all baselines for all the workload settings. TP stands for the number of GPUs used with tensor parallelism. • How do the various techniques proposed in NanoFlow contribute to the end-to-end throughput? (§6.4) • What is the compute, memory and network resource usage pattern of NanoFlow? (§6.5) • How does NanoFlow improve performance when ap- pli

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（≤220字）：**

该图以LLaMA-2-70B、8 GPU、TP=8为固定配置，在Splitwise、LMSYS-Chat、ShareGPT三组真实负载下对比每GPU吞吐量（tokens/s）。四个柱形（由低到高约251→1259、293→1247、335→1272）显示NanoFlow（橙色）达到1259/1247/1272 tokens/s，约为理论最优线1857（红色虚线）的67%，相对最优基线提升约1.5–2倍，并全面优于其余三种方法。该图是§6.4消融实验的收口，以端到端量化证据证明NanoFlow所提协同优化在所有真实负载上均稳定逼近最优，构成论文"近最优LLM服务"核心论点的关键支撑。

### Figure 8 (p.13) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig08.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p13.png]]*
> [!quote] caption
> Latency comparison. The x-axis shows the number of incoming requests per second and the y-axis shows the normalized latency. NanoFlow handles higher request within 200ms SLO constraints.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图含三面板延迟-请求率曲线（Splitwise/LMSYS-Chat-1M/ShareGPT），对比 vLLM、DeepSpeed-FastGen、TensorRT-LLM 与 NanoFlow 在 200 ms/token SLO 阈值（红色虚线）下随 req/s 变化的归一化延迟。各基线分别在 Splitwise 约 6.6–8.2、LMSYS ≈17.1、ShareGPT ≈10.5 req/s 处越过红线陡升，而 NanoFlow（红色）推迟至 15–32 req/s 才显著上升。原文借此论证 NanoFlow 在严苛 SLO 下能维持更高请求吞吐；该图作为方法有效性的端到端压测证据，与正文的 micro-benchmark 组件分析互为印证，构成"组件→系统→SLO 吞吐"完整实验链路的最后一环。

### Figure 9 (p.13) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig09.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p13.png]]*
> [!quote] caption
> Ablation study results for NanoFlow. Nano-batching and overlapping improves NanoFlow’s performance.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图9为NanoFlow消融实验，纵轴为单GPU Token吞吐量(tokens/s)，横轴在四种I/O配置(512/0、512/512、1024/512、512/1024)下对比四种方案。量化数据：NanoFlow依次为1446/1323/1291/1277 tokens/s，全面优于Non-overlap基线(1273/1106/1092/1048)与Nanobatch-only(1171/982/958/952)；关键发现是Nanobatch-only反而低于Non-overlap，说明单独纳米批划分会引入额外开销。

技术结论：仅做nano-batching并不能提升性能，必须与overlapping结合才能发挥优势；offload版(1402/1290/1259/1244)略有下降但仍优于两基线。

论文作用：以消融证据支撑NanoFlow两大核心技术——nano-batching与overlap缺一不可，是验证方法有效性的关键依据。

### Figure 10 (p.13) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig10.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p13.png]]*
> [!quote] caption
> While the non-overlapping baseline sequentially executes operations, which mostly uses only one resource at a given time, the NanoFlow instance can concurrently utilize multiple resources and achieves 68.5% average compute utilization. Due to kernel interfer- ence, NanoFlow provides lower than optimal compute usage.

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图以Compute/Memory/Network三层堆叠时序（0–3000μs）对比单层推理资源占用。(a)非重叠基线串行：Compute在1300–2700μs维持~88%峰值，Memory在300–700μs达80%，Network仅短暂脉冲达58–75%，三类资源时间上近乎互斥。(b)NanoFlow三类资源交错并发，Compute呈多段阶梯（25%–88%），Memory与Network同步起伏，整体Compute利用率均值达68.5%。论文借此论证NanoFlow通过算子级细粒度融合实现跨资源并发是其相对非重叠流水线提升吞吐的关键机制证据，也提示内核干扰下仍存优化空间。

### Figure 11 (p.13) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig11.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p13.png]]*
> [!quote] caption
> We find that

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图示对象与数据**：柱状图对比 vLLM（蓝）与 NanoFlow（橙）在 5 个模型上的归一化单卡吞吐（%），红虚线标示 100% 最优基准，柱内数字为绝对 tokens/s/GPU。具体：Llama-3-70B 32.0%(593)→70.6%(1306)；Qwen2-72B 30.8%(554)→67.4%(1213)；Deepseek-67B 27.4%(532)→59.1%(1147)；Mixtral-8x7B 9.7%(997)→50.4%(5188)；Llama-3-8B 31.9%(5187)→78.5%(12756)。

**关键结论**：NanoFlow 在全部模型上均显著优于 vLLM，最高达最优吞吐的 78.5%（Llama-3-8B），相对 vLLM 提升约 2.2–5.2 倍。

**论文作用**：作为通用性验证，证明 NanoFlow 在 dense 与 MoE、不同参数规模模型上均稳定逼近最优，支撑"跨架构实现近最优服务吞吐"的核心主张。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.6) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-tab01.png]]
> [!quote] caption
> Characteristics of accelerator models across various vendors and release years.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文联合解读**

1) **对象与数据**：表格对比 NVIDIA（V100→B200, 2017–2024）、AMD（MI250/300/325X）、Intel（Gaudi 2/3）及 NVIDIA Ada 6000 共 11 款加速器。量化趋势：MemSize 从 16GB 升至 256GB（AMD MI325X），MemBW 从 900 增至 8000 GB/s（B100/B200），NetBW 从 64 增至 1800 GB/s，FP16 算力从 125K 跃至 2.25M GFLOP/s（B200）。三个比值揭示结构性瓶颈：MemSize/MemBW 仅 0.015–0.050、NetBW/MemBW 仅 0.067–0.39，而 **Compute/MemBW 高达 107–486**，说明算力与带宽增速严重失衡。

2) **论证结论**：内存带宽是 LLM 推理的关键瓶颈；算力相对内存富余（compute-bound 算子易被喂饱），而网络相对内存并不稀缺 → 必须通过设备内**算子重叠**（compute/memory/network 三类流并行）来隐藏内存延迟，而非单纯堆叠规模或网络。

3) **论文作用**：作为 NanoFlow 方法动机的硬件画像依据，支撑其"device-stream 级 micro-batch 调度、异构 batch 融合"的核心理念，是 Fig.1 Transformer 算子分类与流水线设计的现实硬件前提。

### Table 2 (p.7) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-tab02.png]]
> [!quote] caption
> Comparison of operation runtimes between cost model estimation and real-world measurements.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读**

Table 2 列出7个推理操作（KQV、O、UG、D、DecAttn、PfAttn、Net）的GFLOP、内存/网络用量与三类估计时间（T_comp/T_mem/T_net）及实测时间。粗体标出每行主导瓶颈：计算密集型操作（KQV、O、UG、D、PfAttn）的 Est T_comp 分别为 11.01/8.81/61.67/30.84/0.37 ms，对应实测 16.08/16.01/69.92/34.96/4.56 ms；DecAttn 为内存密集型（Est T_mem 28.89 ms vs 实测 35.60 ms）；Net 为网络密集型（Est T_net 31.33 ms vs 实测 47.92 ms）。

**技术结论**：模型估计的主导瓶颈类型与实测瓶颈属性一致，验证了 NanoFlow 成本模型对算子运行时间的预测准确性。

**论文作用**：为调度器依据各操作瓶颈选择最优并行策略（TP/CP/EP/PP）提供量化依据，是 Figure 2 网络-计算比热力图分析的前置基础。

### Table 4 (p.12) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-tab04.png]]
> [!quote] caption
> The average and standard deviation of input and output lengths in the sampled datasets.

> [!tip] 表格解读（多模态）
> 【图文联合解读】## 图文联合解读

**Table 4 核心数据**：展示三个真实采样数据集的输入/输出 token 长度的均值与标准差。
- **Splitwise**：输入 1155（±1109），输出 211（±163）——超长输入，高方差；
- **LMSYS-Chat**：输入 102（±169），输出 222（±210）——短输入、聊天气泡；
- **ShareGPT**：输入 246（±547），输出 322（±244）——中等长度但方差极大。

**关键论证结论**：三个数据集的"标准差接近甚至超过均值"，说明请求长度分布高度异构（heavy-tailed），单一 batch 策略会因 padding 或 bubble 导致计算/显存资源严重浪费，印证了 NanoFlow 需要细粒度 pipeline 调度（如阶段分解、张量并行子流水线）的必要性。

**论文链路作用**：作为评估部分的 workload characterization，为后续实验吞吐对比提供多样化、贴近真实场景的负载基准，证明 NanoFlow 在不同长度模式（长输入型 / 短输入长输出 / 中长混合）下均能稳定优于 vLLM 等基线。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
T_{mem} = \frac{MemSize}{MemBW}
$$

$$
T_{Compute} &\approx \frac{2B_{Dense} \cdot P_{Model}}{Compute}
$$

$$
T_{net} \approx 4\cdot\frac{N_{GPU}B_{Dense}D_{model} S_{type} L }{NetBW}
$$

$$
T_R &= \frac{T_{Mem}}{T_{Compute}} \approx \frac{Compute}{MemBW} \frac{MemSize}{P_{model}} \frac{1}{2B_{dense}}
$$

$$
\mathrm{Throughput_{optimal}} &= \frac{B_{Dense}}{T_{Compute}} = \frac{Compute}{2 P_{Model}}
$$

## 技术点深读（DEEP）

![[deep/nanoflow-towards-optimal-large-language-model-serving-throughput]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/nanoflow-towards-optimal-large-language-model-serving-throughput.txt`（78749 字符）供引用检索。