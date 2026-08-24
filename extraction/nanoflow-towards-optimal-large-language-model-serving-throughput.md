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

图4展示单层Transformer在现有LLM服务框架（如vLLM）下的串行执行流水线，水平轴为时间，包含6类操作：KQV、DecAttn、Prefill Attention (PF)、O、Attn.AG/O.AG、Up-Gate-Down (UGD)，分别用黄（计算受限）、绿（访存受限）、蓝（网络受限）三色标注。

关键发现：计算受限的KQV/O/UGD与访存/网络受限的DecAttn/PF/AG之间存在4段"WASTED"空泡——短小的访存/网络操作耗时远低于紧邻的长计算操作，使昂贵的GPU计算单元在流水过渡期处于空闲，严重拉低整体吞吐。

此图作为NanoFlow的核心动机图，揭示现有pipeline的算力浪费瓶颈，从而引出其解决方案：在节点内将小操作与对应计算操作**融合**（如DecAttn+PF融合），消除空泡，最大化紧致瓶颈资源的利用率，为后续NanoFlow的分块交错调度设计奠定基础。

### Figure 5 (p.8) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig05.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p08.png]]*
> [!quote] caption
> Interference characteristics between GEMM and GEMV kernels. The points on the x-axis correspond unique GEMM-GEMV implementation pairs. The y-axis denotes the GEMM and GEMV kernels’ normalized performance P. ferent implementations of overlapping kernels exponentially expand the profiling space, resulting in millions of possible configurations. This immense complexity makes exhaustive exploration in

> [!tip] 技术解读（多模态）
> 【图文联合解读】## 图文联合解读

**1) 核心对象与结构：**
Figure 5 以横轴为不同 GEMM-GEMV 实现对（共约 18 个配对），纵轴为归一化性能 P∈[0,1.2]，绘制三条曲线：蓝色圆点实线（GEMM）从 ~1.0 单调下降至 ~0.45；橙色圆点实线（GEMV）由近 0 上升至 ~1.0；灰色×虚线（非最优 GEMV）则在两曲线间剧烈震荡。图中以红色虚线标出 0.3 与 0.8 两个阈值，分别对应"GEMM 优先"（左）与"GEMV 优先"（右）两个分区。

**2) 关键论证结论：**
两曲线呈典型此消彼长——优先 GEMM 时 GEMV 跌至 0.3，反之 GEMM 降至 0.45；而非最优 GEMV 实现性能完全不可预测（0.2–0.7 间抖动）。这印证了 GPU 上计算、内存、缓存资源竞争导致的 kernel interference 不可显式控制，且实现选择对干扰程度有数量级影响。

**3) 在论文中的作用：**
为 NanoFlow 必须采用"逐实现穷举 profiling + R_physical 测量"的方法论提供直接依据——既然干扰不可预测且依赖实现，就必须靠实测建模来分配 SM/带宽，是后文搜索空间指数膨胀论证的实验支撑。

### Figure 6 (p.11) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig06.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p11.png]]*
> [!quote] caption
> Execution pipeline of LLaMA-2 70B, automatically generated by NanoFlow. The solid background and shaded background represents input batch 0-768 and 768-2048, respectively. R stands for resource utilization. By overlapping the compute-, memory-, and network-intensive operations, NanoFlow increases compute utilization and improves the serving throughput. data size of the offload is balanced across i

> [!tip] 技术解读（多模态）
> 【图文联合解读】图6为NanoFlow为LLaMA-2 70B自动生成的层内执行流水线，横向分三行：绿色行DecAttn1-4（R=0.4）、黄色行KQV1-4/O1-2/UGD1-2（R=0.4-0.9，主计算）、蓝色网格行Attn.AG/O.AG/UGD.AR（R=0.1-0.2，内存与网络传输）。实色与阴影底分别对应batch 0-768与768-2048。原文借此论证：NanoFlow将计算、内存、网络三类操作在纳秒级时间轴上交错（如Prefill Attention与AG→AR转换并行），使各类资源利用率同时抬升（UGD达R=0.9），消除单类资源瓶颈、提升吞吐。该图是NanoFlow自动调度器的可视化核心证据，承上启下，支撑后续与vLLM等基线的吞吐对比实验。

### Figure 7 (p.11) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig07.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p11.png]]*
> [!quote] caption
> Offline throughput comparison. NanoFlow outper- forms all baselines for all the workload settings. TP stands for the number of GPUs used with tensor parallelism. • How do the various techniques proposed in NanoFlow contribute to the end-to-end throughput? (§6.4) • What is the compute, memory and network resource usage pattern of NanoFlow? (§6.5) • How does NanoFlow improve performance when ap- pli

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图7图文联合解读**

图7展示LLaMA-2-70B（8 GPU, TP=8）下NanoFlow与vLLM、DeepSpeed-FastGen、TensorRT-LLM的离线吞吐对比。(a)定长场景（输入/输出512–1024）：NanoFlow达1212–1286 tokens/s；(b)真实数据集（Splitwise/LMSYS-Chat/ShareGPT）：NanoFlow达1247–1272 tokens/s，均逼近理论最优1857；最强基线TensorRT-LLM仅560–817 tokens/s，NanoFlow全面领先约2.5×。

原文论证：所有工作负载下NanoFlow均显著优于现有系统，证明其跨场景的通用性与领先地位。

该图在论文中承担端到端性能验证的角色，作为§6.4各技术贡献（拆分注意力、AG转换、跨batch交错等）消融分析与§6.5资源利用模式讨论之外的最终效果收口，佐证NanoFlow设计的整体有效性。

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
> 【图文联合解读】表1列2017–2024共13款加速器(NVIDIA V100→B200、AMD MI250/300/325X、Intel Gaudi2/3) 的显存容量、MemBW、NetBW、FP16算力及三项比值。数据显示：算力从125K→2.25M GFLOPS，但MemSize/MemBW仅0.015–0.05，NetBW/MemBW仅0.067–0.39。

论证结论：相对算力增长，显存与网络带宽严重不足，LLM推理的attention/KV cache访存操作成为瓶颈，且卡间通信难以掩盖计算。

论文作用：为NanoFlow将prefill(compute-bound)与decode(memory-bound)解耦、采用nanobatch填满带宽并与通信重叠的设计方案，提供量化硬件动机。

### Table 2 (p.7) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-tab02.png]]
> [!quote] caption
> Comparison of operation runtimes between cost model estimation and real-world measurements.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心对象与结构**：覆盖 7 类 LLM serving 操作（KQV、O、UG、D、DecAttn、PfAttn、Net），横向给出算力（GFLOP）、显存/网络占用（GB）三组资源量，以及估计的 T_comp / T_mem / T_net 与实测 Real Time。

**关键数据**：
- **Compute-bound**：KQV（11.01ms vs 16.08）、O（8.81 vs 16.01）、UG（61.67 vs 69.92）、D（30.84 vs 34.96）、PfAttn（0.37 vs 4.56），估计与实测同量级；
- **Memory-bound**：DecAttn 需加载 462.2GB，T_mem=28.89 主导，实测 35.60ms；
- **Network-bound**：Net 传输 75.2GB，T_net=31.33 主导，实测 47.92ms。

**关键结论**：成本模型可正确辨识各 op 的瓶颈类型（compute / memory / network），系统实际各项开销使估计略低于实测，但瓶颈归属与实测一致。

**论文作用**：该模型是 NanoFlow 调度策略的前提——只有准确判定各 op 的瓶颈资源，才能将异构 bottleneck 的操作共置同一 NanoFlow 实例内，实现计算、显存与网络的重叠，提升整体吞吐。

### Table 3 (p.9) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-tab03.png]]
> [!quote] caption
> Performance P of GEMV and network kernels with different resource utilization R .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**联合解读：**

**1) 表内容：** Table 3 对比三类算子在资源利用率 R∈{0,0.1,…,1} 下的性能 P。GEMM 严格线性（P≡R）；GEMV 在 R=0.2 时 P=0.3（红字），R=0.9 才达 0.95；Network 在 R=0.2 时 P=0.5（红字），R=0.9 即饱和为 1。GEMV 与 Network 在低/中 R 区间均呈超线性（P > R）。

**2) 关键论证：** 证明 GEMM 是算力受限（P 与 R 等比），而 GEMV（访存）和 Network（通信）属于时延受限/未占满资源，故同等 R 下可获得超额 P，为 NanoFlow 的核心理论基础——GEMV/Network 能隐藏延迟。

**3) 链路作用：** 为 §3 将 LLM 推理拆为 GEMM-prefill、GEMV-decode、Network 三流并在同一 SM 上共调度提供量化依据，是 Figure 3 算时/存时曲线和后续调度策略的实验支撑。

### Table 4 (p.12) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-tab04.png]]
> [!quote] caption
> The average and standard deviation of input and output lengths in the sampled datasets.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读**

该表展示三个真实对话数据集的长度统计：Splitwise 输入极长（1155±1109）而输出短（211±163）；LMSYS-Chat 输入短（102±169）、输出中等（222±210）；ShareGPT 输入中等（246±547）、输出最长（322±244）。**核心特征是各数据集标准差普遍接近甚至超过均值**，表明请求长度高度偏斜、波动剧烈，长短请求混杂是真实负载常态。

原文借此论证：①不同应用场景输入/输出比例差异显著，传统按请求级批处理难以同时兼顾；②高方差要求 NanoFlow 采用比请求更细的算子级调度，在 microbatch 间重叠 memory/compute/network 操作，以吸收长度不均带来的气泡。该表作为实验 baseline 的现实依据，支撑了后续对 NanoFlow 在三类典型 workload 上吞吐提升的评测结论。

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