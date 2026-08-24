---
paper_num: "15"
title: "昇腾 950 NPU 架构白皮书"
authors: ""
date: "2026/1/1"
arxiv: "—"
pdf: "papers/ascend-950-npu-architecture-whitepaper.pdf"
slug: "ascend-950-npu-architecture-whitepaper"
tags: []
---

# 昇腾 950 NPU 架构白皮书

> [!abstract] 摘要（原文）
> 1\. ✨ 华为昇腾950系列芯片（昇腾950PR和昇腾950DT）是面向下一代人工智能应用的旗舰计算芯片，搭载自研第三代达芬奇架构，旨在赋能大模型全生命周期及AIGC、智能推荐等多元化场景。 2. ⚡️ 该系列芯片在算力密度、存储带宽和互联拓扑上实现跨越式升级，通过引入NDDMA、SIMD/SIMT混合编程和原生支持MXFP4/MXFP8/HiF8等格式（MXFP4张量浮点峰值算力提升高达4倍），显著提升了Transformer类模型的训练与推理效率。 3. 💾 昇腾950系列配备大容量高速片上内存（PR最高128GB/1.6TB/s，DT最高144GB/4TB/s）和128MB L2 Cache，并采用灵衢（Unified Bus）互联总线，支持URMA、UB Memory、PCIe 5.0及UBoE等先进协议，可构建超128K卡大规模集群。

## 元信息
- **发表日期**: 2026/1/1
- **作者**: —
- **arXiv**: —
- **本地 PDF**: `papers/ascend-950-npu-architecture-whitepaper.pdf`
- **页数**: 40

## 图表（原文 caption + 页码）

### Figure 301 (p.12) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig301.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p12.png]]*
> [!quote] caption
> 昇腾950 芯片架构示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示展示昇腾950双Die对称架构：每Die包含AI Core、128MB统一L2 Cache、2颗Linx816 CPU与DVPP，4组Memory Interface对接Global Memory（HBM），中央STARS2.0模块经D2D互联双Die，两侧通过PCIe5.0 CTRL、Security Core、UB CTRL外接72×HiLink端口。

原文借此论证"算-存-网"协同的硬件基底：L2 Cache与片上HBM（PR 1.6TB/s/128GB、DT 4TB/s/144GB）保障高吞吐访存；STARS2.0承担片内任务调度；UB 2.0（72×HiLink 112Gbps拆18 Port）+ PCIe GEN5 + 2×400Gbps UBoE支撑多芯片扩展与URMA语义访存。该图为后续算子映射、多卡互联与集群性能分析提供架构锚点。

### Figure 401 (p.17) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig401.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p17.png]]*
> [!quote] caption
> AI Core 架构及各层级SRAM 示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示AI Core结构：含3个Scalar核（Scalar 0/1/2）、2个Vector Core（各支持64×FP32或128×FP16）、1个Cube Core（16×16×16 FP16矩阵乘单元）；分层SRAM为L0A/L0B各64KB、L0C 256KB紧邻Cube，L1 512KB居中共享，UB0/UB1各256KB供向量/标量使用，底层为Register File，顶端接Bus Interface。

原文以此论证：异构计算（Cube+Vector+Scalar）与L0/L1/UB多级近数据SRAM紧耦合，使矩阵乘、通用算术与控制调度在单Core内协同，减少数据搬运，从而实现高吞吐、低访存的AI计算流水线，是白皮书阐述Ascend 950算力与能效优势的硬件基础图。

### Figure 402 (p.18) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig402.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p18.png]]*
> [!quote] caption
> Cube Core 处理架构示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示Cube Core两级处理结构：顶部一维脉动链依次接收k组正交输入向量——X₀~X_{k-1}（横向，灰色箭头）与Y₀~Y_{k-1}（纵向，绿色箭头），各节点完成MAC后汇入Σ求和单元；下方展开为4×4=16个PE_S构成的二维脉动阵列，承担主体矩阵乘运算。 

（原文未显式引用本图，依图自释）该图论证的关键结论：Cube Core采用"正交广播→局部累加→2D PE阵列"的层级化微架构，通过脉动数据复用降低访存开销，以高吞吐、低延迟完成GEMM/卷积类张量运算。它在全文方法链路中充当算子物理执行的计算核心，是Ascend 950面向AI工作负载峰值算力论证的硬件基石。

### Figure 403 (p.18) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig403.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p18.png]]*
> [!quote] caption
> Cube Core 支持的数值精度示意

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图以"符号(1 bit)+指数+尾数"三段堆叠条形，量化展示 Cube Core 支持的 9 种数值精度：32-bit 组 FP32(1/8/23)、TF32(1/8/10)；16-bit 组 BF16(1/8/7)、FP16(1/5/10)；8-bit 组 HiF8(动态指/阶)、FP8-E5M2(1/5/2)、FP8-E4M3(1/4/3)；4-bit 组 FP4(1/2/1)。

该图论证的关键结论：Cube Core 原生覆盖 4-bit 至 32-bit 全谱精度，特别是同时支持 HiF8 动态分配、两种 FP8 子格式及 TF32、FP4，体现 Ascend 950 在 AI 训练/推理各阶段对精度–吞吐–能效的可分级取舍能力。

在论文中，它作为算子精度契约的可视化基线，向下衔接量化编译栈与算子映射章节，向上支撑混合精度训练与低比特推理方案选型。

### Figure 404 (p.19) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig404.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p19.png]]*
> [!quote] caption
> HiF8 数值精度

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图以8比特位级表格展示HiF8浮点格式的两种编码模式。**Normal编码**采用变长前导码Dot（0–4）划分5档指数区间：Dot=0时E=0（4位尾码M），Dot=1为E=±1（3位M+SE），Dot=2为E=±[2,3]（3位M），Dot=3为E=±[4,7]（2位M），Dot=4为E=±[8,15]（1位M），格式遵循X=(-1)^S·2^E·1.M；**Denormal编码**为S+0000+MMM，使E覆盖[-22,-16]。SE为指数隐含符号位（红色，1-bit不存储），尾码首"1"隐含。

该图论证的核心结论：HiF8通过前导码自适应分配8比特，在保持FP8紧凑性的同时提供分级动态范围与精度折中，以支持AI推理中数值分布的差异化需求，是Ascend NPU精度体系的关键底层格式之一。

### Figure 405 (p.21) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig405.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p21.png]]*
> [!quote] caption
> Vector Core 架构示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示 Vector Core 的双模式架构。左侧顶层含 Scalar Unit、两组 Async Function Queue（各 6 个 Func 槽位并标注 SIMT/SIMD/NULL）、DMA Unit、Vector Unit、Vector Cache/Buffer、Bus Interface、Global Memory。右侧展开两条执行路径：

- **SIMD 模式**：I Cache → Program Sequence → OoO Dispatch，驱动 VL 条 Lane 共享 Vector Register File；
- **SIMT 模式**：I Cache → 多组 Program Sequence 经 Warp Scheduler 调度后 In-order Dispatch，驱动 warp_size 条 Lane 配 SIMT Register File。

两模式共用 Bank 0…N-1、Cache Controller、Coalescing Unit、Load/Store Unit 与 Vector Execution Unit。

**关键结论与链路作用**：该图论证 Vector Core 以统一微架构同时支撑向量级与线程级并行，可按负载动态切换模式，避免两套独立硬件开销。在 AI 计算流水线中，它承接通用向量算子、归约与激活等并行任务，配合 Scalar Unit 指令调度与 DMA 数据搬运，为上层矩阵/张量单元持续供给就绪数据流。

### Figure 406 (p.22) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig406.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p22.png]]*
> [!quote] caption
> AI Core Cube-Vector 融合示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示AI Core内Cube-Vector融合架构：左右对称布置2个Vector Core（各配Register File），经UB0/UB1统一缓冲与中央Cube Core双向互连；Cube Core旁置L1高速缓存及L0A/L0B输入、L0C累加本地存储；上下两端为Bus Interface对外通信。

论证结论：Cube（矩阵乘）与Vector（向量/标量）单元在同一核内紧耦合，通过共享UB实现低延迟数据交换——L0A/L0B喂入Cube、L0C结果回送Vector后处理，形成"矩阵–向量"级流水线，支撑高吞吐与高能效。

在论文中的作用：为后续阐述Ascend 950片上异构融合、内存层级、算力密度及编程模型提供硬件结构基线。

### Figure 407 (p.23) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig407.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p23.png]]*
> [!quote] caption
> NDDMA 指令

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图407 NDDMA指令 联合解读**

1）**核心结构与数据**：左侧Global Memory为32行（0–31）的稀疏存储，编号1–24的数据按不同色块（青、蓝、橙等）散布于非连续行号上，每组在源端间隔约2行；右侧UnifiedBuffer为24格的连续紧凑布局，NDDMA箭头将源端多色分组（含4/8/12/16/20/24等独立散列值）整体映射至目标端紧凑序列。

2）**论证的技术结论**：NDDMA指令可一次性完成"非连续源地址→连续目的地址"的稀疏—稠密转换，并在搬移过程中按预设分色保持批次/通道归属不变，省去显式重排指令。

3）**在论文中的作用**：作为NPU片内外数据通路的关键原语，NDDMA服务于算子前置的数据准备阶段，为后续Cube/Vector单元提供对齐、连续、可直接消费的张量片，是体现Ascend 950内存子系统高效带宽利用与编程灵活性的代表性机制。

### Figure 408 (p.24) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig408.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p24.png]]*
> [!quote] caption
> 昇腾950 新同步机制代码示例

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示对比两种同步伪代码：左侧`set_flag/wait_flag`机制在`i=0:100`循环中需4次显式标志操作（wait_flag/ set_flag/ wait_flag/ set_flag），并配`if i>0`与`if i<99`边界判断；右侧`BufferID`机制用`get_buf/rel_buf`获取/释放缓冲区替代标志位，循环体结构扁平、无分支。

**关键结论：** BufferID机制隐式表达MTE2与Vector单元间的数据就绪与依赖关系，免去显式flag编排与边界处理，编程模型更简洁，依赖硬件对缓冲区生命周期的支持。

**在论文中的作用：** 作为昇腾950新同步机制的编程范式示例，展示同步原语从"显式标志"向"隐式buffer"的演进路径，配合硬件降低多流水级（MTE2↔Vector）编排负担，提升开发效率。

### Figure 409 (p.25) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig409.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p25.png]]*
> [!quote] caption
> 昇腾950 内存层次示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】# 图文联合解读：昇腾950内存层次示意图

## 1) 图示核心结构

该图呈现昇腾950双Die（Die 0 / Die 1）对称的存储层次：
- **片内层级**：每个Die含多组AI Core，每核由AIC（标量/矩阵单元，配L1、L0A、L0B、L0C四级小缓存）与AIV（向量单元，配L1和UB统一缓冲区）组成；另含AI CPU（CPU L1+L2）。
- **跨核层级**：每Die共享L2 Cache与L3 Cache。
- **全局层**：双Die通过Directory（Cache Coherence）目录维护一致性，下接Global Memory全局内存。

## 2) 关键技术结论

图示论证了"**多级近存+Die间目录一致**"的架构取向：
- AI Core内部通过L0A/B/C细化矩阵数据复用，UB承载AIV大块数据搬运，降低访存次数；
- L2/L3分层减小跨核带宽压力；
- Die 0与Die 1经目录而非广播式嗅探保持一致性，可扩展到多Die封装场景。

## 3) 在论文方法/实验链路中的作用

作为架构白皮书的结构总图之一，此图为后续章节的算子流水线、数据搬运优化、并行切分与一致性协议论述提供**统一的存储参照系**，是理解性能瓶颈与带宽分配论证的基线示意图。

### Figure 410 (p.27) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig410.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p27.png]]*
> [!quote] caption
> Non-allocate（L2 hint）典型应用场景示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**核心对象与结构**：图示两个并发任务Task0与Task1。Task0的data A沿蓝色"non-allocate"通路**直写Global Memory**，绕过L2 Cache；data B则经绿色箭头**写入L2 Cache**并由Task1读取复用。

2）**关键结论**：non-allocate提示用于声明该数据**无需驻留L2**（如一次性流式数据），可避免污染缓存、节省L2空间；而具有复用价值的数据仍正常进入L2，在任务间共享，二者策略互补。

3）**论文作用**：作为L2 hint中"非分配"模式的典型用例，说明编程接口如何通过语义提示指导缓存分配，与prefetch/allocate等hint共同构成缓存行为可控的编程模型支撑。

### Figure 411 (p.27) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig411.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p27.png]]*
> [!quote] caption
> STARS2.0 架构示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】# 图文联合解读：STARS2.0 架构示意图

## 1. 核心对象与结构
该图呈现 Ascend 950 NPU 的 **STARS2.0 任务调度运行时**架构，由三层组成：
- **任务队列层**：多个并行的 Task 栈（图中绘出 4 列，"…" 表示可扩展），每栈含 5 级深度槽位；
- **辅助机制层**：右侧 4 个蓝色功能模块——**Notify/Sync（同步通知）、Conds（条件等待）、Profiling（性能采集）、Fusion（指令融合）**，与 Task 栈并列放置；
- **下发层**：底部 **Sched（调度器）** 通过两条总线向硬件单元分发任务——左侧 **HSCB** 连接 **AIV（向量核）**与 **AIC（Cube 核）**等多实例计算簇；右侧 **NoC** 连接 **UBDMA、SDMA、CCU、CPU、DVPP** 共 5 类非计算单元（每类亦为多实例）。

## 2. 关键技术结论
该图论证 STARS2.0 通过统一 **Task 抽象 + 调度器 + HSCB/NoC 双通道**，将 AI 算力（AIV/AIC）与通用算力（DMA/CCU/CPU/DVPP）以**同构任务队列**方式管理，配合 Notify/Conds 实现任务同步、Profiling 采集性能、Fusion 完成指令合并，实现**异构多硬件的统一任务调度与协同执行**。

## 3. 在论文中的作用
作为软件栈承上启下的核心：向上承接编译/调度层的任务流，向下统一驱动 Ascend 950 全套计算与传输硬件，是论文阐述"软硬件协同 + 异构融合"设计理念的关键架构证据。

### Figure 412 (p.31) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig412.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p31.png]]*
> [!quote] caption
> URMA 异步访存通信的过程示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）图中展示两个NPU节点间的URMA异步访存链路。左节点包含Core、URMA、本地UMMU及多个Port；右节点包含对端Port和远端UMMU，两端各挂接Memory。流程为：Core通过Doorbell触发URMA，URMA经本地UMMU读取本地Memory，再经Port-to-Port跨片将数据发往远端UMMU，最终写入远端Memory，全程由硬件接管，无需Core参与传输。

2）该图论证的核心结论：URMA通过硬件自主搬运+Doorbell通知机制实现异步远程访存；双侧UMMU完成地址翻译，使Core可使用虚地址透明访问远端Memory，CPU开销与网络延迟被显著掩盖。

3）在论文方法链中，该图是URMA通信原语的可视化基线，为后续讨论跨Die一致性、内存语义与互联带宽利用率提供架构依据。

### Figure 413 (p.32) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig413.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p32.png]]*
> [!quote] caption
> UB Memory 同步访存语义地址通信过程示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1）核心对象与结构：**
图示左侧模块含 Core、UB Mem Decoder 与 4 个 Port，右侧模块含多个 Port、UMMU 及 Memory。橙色箭头完整勾勒一条同步访存路径：Core → UB Mem Decoder → 左 Port → 跨 NoC → 右 Port → UMMU → Memory，即一次同步地址通信需经"译码—端口—总线—MMU—目标存储"五段链路。

**2）论证的关键结论：**
UB Memory 的同步访存语义依赖地址穿越本地 Decoder 译码后经端口跨片，再由 UMMU 完成地址映射与访问控制落到外部 Memory，体现了"核内 UB ↔ 片外 Memory"同步访问在硬件上必经 UMMU 转换的设计约束。

**3）在论文中的作用：**
作为同步访存语义章节的可视化依据，阐明 UB 同步读写与异步路径的硬件差异，为后续 Cache 一致性、地址映射及访存性能分析提供结构基础。

### Figure 414 (p.33) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig414.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p33.png]]*
> [!quote] caption
> CCU 架构示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**说明**：论文正文未给出该图的显式引用段落，故解读以图示信息为主，结合CCU作为片上集合通信单元的常见定位展开。

**图文联合解读**：

图示CCU采用"CCUM管理层 + CCUA执行层"两级架构。上层CCUM包含Mission Call Interface入口、多路并行Mission Commander及Instruction Implementation Unit，向下分发两条解耦路径：Reduce Call Interface（红色箭头，指向各CCUA的Reduce Unit）与URMA Call Interface（蓝色箭头，下接URMA模块再汇接多Port）；下层由多个并列CCUA组成，每个CCUA内置多个Memory Slice与一个Reduce Unit，以"..."表示可扩展。

**技术结论**：通过Reduce与URMA双路径解耦、Memory Slice切分及多CCUA并行，使规约计算与跨片数据搬运重叠执行，显著降低AllReduce同步开销。

**链路作用**：CCU作为片上集合通信加速引擎，将AllReduce等操作硬件卸载并与AI Core解耦，是Ascend 950多卡互联拓扑与训练/推理通信栈的关键硬件层。

### Figure 415 (p.34) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig415.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p34.png]]*
> [!quote] caption
> UB On Chip Switch 转发示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）核心对象与结构：该图展示UB片上交换（On Chip Switch）的三级转发架构——底部为多个并行**Port**（端口，含"…"示意多端口扩展），中部为绿色**Routing Table**（路由表），顶部为蓝色**Network On Chip**（片上网络）。端口通过实线连接到路由表，路由表再与NoC互联；端口下方虚线箭头表示数据转发出口路径。

2）关键技术结论：交换采用**查表转发**机制，由Routing Table作为枢纽，按目的端口查表后选择从指定Port进出NoC，实现多端口并行、低延迟的片上数据路由。

3）整体作用：该图揭示了Ascend 950 NPU UB模块与片上网络间的数据通路转发原理，是论文阐述NPU存储子系统互联与数据搬运机制的关键支撑图示。

### Figure 416 (p.35) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig416.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p35.png]]*
> [!quote] caption
> PCIe 5.0 架构示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示Ascend 950 NPU的PCIe 5.0主机接口架构，自顶向下分层：顶层PCIe Gen5×16经双向箭头连接System Bus（系统总线）；其下依次为应用层（含MCTP管理组件与DMA引擎）、事务层（Transaction Layer）、数据链路层（DataLink Layer）、物理层（Physical Layer, x16通道），底层为Serdes串行收发器。

该图论证了Ascend 950采用PCIe Gen5×16作为主机互联接口：x16通道配合Serdes提供高带宽串行链路，MCTP支持带外设备管理，DMA引擎实现主机内存与片上存储间的高效数据搬运。

在论文整体架构论述中，本图作为I/O子系统架构证据，与HCCS、HBM等子模块图共同支撑全片对外互联能力论证，是CPU—NPU—外部存储数据通路的关键环节。

### Figure 417 (p.36) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig417.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p36.png]]*
> [!quote] caption
> 昇腾950 的一种超节点示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图解：**

图中展示昇腾950超节点采用**两层交换的层次化拓扑**：底层为若干Ascend 950 NPU（蓝色），同组内底部以多条曲线互联（组内高带宽直连）；每组中部部署Switch收束组内NPU上行流量；各组的Switch再上联至顶层多台Switch（绿色），顶Switch跨组全互联，构成统一的超节点交换域。"…"表示机柜/交换机数量可横向扩展。

**作用：**作为白皮书超节点架构示意，论证通过二层Switch级联将大量950芯片聚合为单一扩展域，支撑万卡级大模型并行训练的带宽与通信扩展性，是衔接芯片微架构与集群系统方案的关键参考图。

### Figure 418 (p.36) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig418.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p36.png]]*
> [!quote] caption
> 昇腾950 访问CPU 超大内存池示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构：** 图中顶部为一台多层交换机（Switch），向下以多条链路连接左右两个机柜（Rack）。左机柜内为两层计算节点组，每组含若干 CPU 与多颗 Ascend950 NPU 交错排布；右机柜内为三层结构，每层由一行 CPU 与一块横贯整层的 Memory Pool（内存池）组成，整体形成"超大内存池"。

**2) 关键结论：** 该图论证了 Ascend950 采用了"算存分离、解耦池化"架构——NPU 集中在左侧计算柜，CPU 大容量内存集中在右侧内存柜，二者通过高速交换网络互通，使 NPU 可跨机柜远程访问 CPU 超大内存池，实现内存资源的池化共享与弹性扩展。

**3) 论文中的作用：** 作为算存解耦设计的核心示意图，支撑白皮书关于超大规模模型训练/推理中内存容量扩展、跨节点内存共享及资源利用率提升的方法论述。

### Figure 419 (p.37) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig419.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p37.png]]*
> [!quote] caption
> 昇腾950 直接访问超大存储资源池示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图中展示了基于解耦架构的存储直访拓扑：顶部为多层堆叠的 Switch（聚合交换），其下分两侧 Rack：左侧为计算 Rack，内含 2 组服务器单元，每组配置 2+ 个 CPU 与 3 个 Ascend950 NPU；右侧为存储 Rack，由 3 列 × 5 行的 Storage 节点组成超大资源池，两者通过同一交换网络对称互联。

该图论证了关键技术结论：昇腾 950 通过统一交换面直接访问外部解耦的存储资源池，实现"算存分离、横向扩展"的池化能力，使 NPU 在不依赖本地 HBM 的前提下支持 PB 级模型/检查点加载。

在论文整体架构链路中，此图用于支撑"内存语义扩展 / 超大模型训练推理"章节，强调 Ascend 950 借助 fabric 直访打破单机存储容量上限。

### Figure 420 (p.38) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig420.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p38.png]]*
> [!quote] caption
> 昇腾超节点基于UB Switch 转换为以太网与以太世界互通示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构：** 图示为一个昇腾超节点对外以太互联拓扑。外部有 **2 个 Ethernet Switch**；超节点内部包含 **2 台 UB Switch**（每台上行端口为 ETH、下行端口为 UB，呈双端口异构形态），通过 ETH 链路与外部交换机**交叉互联**。下行经 UB 总线连接到 **多个 Ascend950 NPU**（图中示意 4 个，中间以"…"省略），NPU 之间另有 UB 直连形成 Mesh。结合 caption，UB Switch 在此处充当"UB↔ETH"协议转换网关。

**2) 关键技术结论：** UB Switch 不仅承载超节点内部 UB 域交换，还作为**协议/链路转换锚点**，将超节点内部高性能 UB 域"延伸"为标准以太网，使其**无缝接入以太生态**，验证了 UB 架构对外的开放性与互操作性。

**3) 在论文中的作用：** 该图用于收束"超节点—域外互联"章节，把前文阐述的 UB Switch 内部 UB 交换功能，**外延为对外以太对接方案**，是论证"超节点可平滑扩展到数据中心级以太网络"的关键架构证据。

### Figure 421 (p.39) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig421.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p39.png]]*
> [!quote] caption
> 昇腾芯片支持以太网与以太世界互通示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示展示了Ascend950芯片与以太网世界的互通架构：顶层2台外部以太网交换机经ETH链路交叉连接至框内2台内部以太网交换机（各含2个ETH端口），后者再以ETH全交叉方式下连4+颗Ascend950芯片（每芯片含1个ETH端口），芯片之间通过底部UB总线（绿色弧线）互联。

**关键结论：** Ascend950内置标准ETH接口，可直接对接通用以太网交换机；芯片间走UB平面，芯片与外部走ETH平面，二者解耦共存。

**方法链作用：** 该图论证昇腾具备"UB域内高速互联 + ETH域外以太网互通"的双平面组网能力，证明其既能通过UB扩展片间高带宽域，又能无缝接入标准以太网基础设施，是大规模AI集群异构组网与弹性扩展的网络基础。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 101 (p.5) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-tab101.png]]
> [!quote] caption
> 关键术语

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表1-1「关键术语」图文解读**

表1-1为两列结构的术语词表（术语/描述），按字母序收录AIC、AIGC、AIV、AI CPU、AI Die、CANN、Clos、CMO、CTP、Device、Die、DVPP共12条，每条均含具体量化定义：AIC/AIV明确AI Core分离架构下Cube Core与Vector Core组合的角色分工；AI CPU特指自研Linx816 ARM核；AI Die对应昇腾950PR/950DT芯片中的计算Die；CANN为异构计算架构软件栈；Clos为多级无阻塞数据中心网络；CMO经SDMA实现L2 Cache管理；CTP为Unified Bus轻量级传输；Device对应Host-Device架构的设备侧；DVPP含JPEG（JPEGD/JPEGE）与Video编解码模块。

正文无显式引用。本表作全篇术语基线，统一了AI Core分离结构、Host-Device架构、异构软件栈、芯片型号等后续高频概念的定口径，是阅读架构详情、软件栈与编号规则的必备前置参照，保障全文表述一致性。

### Table 301 (p.13) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-tab301.png]]
> [!quote] caption
> 昇腾 950 系列芯片支持的主要规格

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表3-1图文联合解读：**

该表呈现昇腾950PR与950DT两款芯片AI子系统的量化规格：Cube Core（32/28 vs 36/32/28）、Vector Core（64/56 vs 72/64/56），并按MXFP4（1784/1561 vs 2007/1784/1561 TFLOPS）、HiF8/MXFP8/FP8（919/804 vs 1034/919/804）、INT8（919/804 vs 1034/919/804 TOPS）、BF16/FP16、TF32等多精度给出Cube+Vector总算力及Cube算力。原文以本表为锚点，论证950DT在算力规模、片上HBM带宽（4TB/s）及Unified Bus 2.0互联（72×HiLink 112Gbps拆分18 Port、PCIe GEN5、2×400Gbps UBoE）方面全面优于950PR，支撑"算力-存储-互联"三位一体扩展的设计结论，是全文硬件能力基线与后续性能实验的参考依据。

### Table 401 (p.20) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-tab401.png]]
> [!quote] caption
> HiF8 特殊值编码

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表4-1 HiF8特殊值编码 图文解读**

**1) 核心对象与结构**：该表给出HiF8（8位浮点）格式中4类特殊值的位级编码。字段按颜色分段——红色为符号位（1bit）、橙色为指数位、紫色为尾数位。ZERO为`00000000`（全零）；NAN为`10000000`（仅符号位为1）；+INF为`01101111`、-INF为`11101111`（指数=`1101`、尾数=`1111`，仅符号位区分）。

**2) 关键技术结论**：HiF8采用紧凑的位模式区分特殊值——ZERO/NAN共用零指数和零尾数，仅靠符号位与全零组合区分；±INF则共享最大指数与满尾数，仅符号位翻转即可互转，便于硬件以少量比较逻辑快速识别异常值。

**3) 在论文中的作用**：作为HiF8数值格式规范的定义表，为后续张量计算单元、数据通路及异常处理电路的设计提供编码基准，支撑NPU对低精度AI计算的可靠性保障。

### Table 402 (p.25) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-tab402.png]]
> [!quote] caption
> 昇腾 950 Memory 层次中主要 Memory 及其大小

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读**

该表量化呈现昇腾950存储层级：AI核侧含L1 Buffer 512KB、L0A/L0B各64KB、L0C 256KB、UB 512KB；CPU侧L1 64KB、L2 1MB/核、L3 4MB/Cluster；片上L2 Cache可达128MB；950PR片上内存最高128GB，950DT为96/144GB。

作为关键结论，它论证了AI核与CPU核各自具备独立多级Cache，并以大容量片上内存支撑大模型驻留，缓解带宽瓶颈。

在论文方法链中，该表是后续算子切分、数据流水编排、性能调优的硬件容量基线，为tiling策略与片上/片外访存比分析提供量化依据。

## 技术点深读（DEEP）

![[deep/ascend-950-npu-architecture-whitepaper]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/ascend-950-npu-architecture-whitepaper.txt`（28777 字符）供引用检索。