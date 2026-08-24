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
> 【图文联合解读】**图文联合解读**

**1) 图示核心结构：**
该图展示昇腾950 双 Die 对称架构。两侧各含 1 个 AI Core（中央计算阵列），被上下两道 L2 Cache 环绕；每 Die 配备 2 个 Linx816 CPU、1 个 DVPP（视频预处理）模块与 1 个 STARS 加速器；外侧通过 2 个 Memory Interface 连接 Global Memory，并通过 D2D（Die-to-Die）接口实现片内互连。两侧封装端集成 PCIe5.0 CTRL、Security Core、UB CTRL，并外接 Hilink 总线接口。

**3) 论证结论：**
该图用以论证昇腾950 通过"双 Die + D2D 高速互连"扩展算力与显存容量，依托 L2 Cache 上下包夹 AI Core 的布局降低数据访问延迟，并借由 DVPP/STARS/Linx816 CPU 与 AI Core 协处理，构建"通用+专用"异构计算体系。

**3) 在论文中的作用：**
作为白皮书架构总览图，是后续各章节（计算、存储、互连、I/O）论述的结构基础，定位各子模块的功能边界与连接关系。

### Figure 401 (p.17) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig401.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p17.png]]*
> [!quote] caption
> AI Core 架构及各层级SRAM 示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图展示Ascend 950 AI Core架构：
①**计算单元**：1个Cube Core（16×16×16 FP16矩阵乘引擎）、2个Vector Core（各含双64×64 FP32 / 128×128 FP16 SIMD）、3个Scalar Core（Scalar 0/1/2）；
②**分层SRAM**：L1 512KB顶层缓存、L0A/L0B各64KB直连Cube作为矩阵操作数缓冲、L0C 256KB存放累加结果、UB0/UB1各256KB作为Vector/Scalar共享缓存；
③顶部Bus Interface对外连接。

**关键技术结论**：通过Cube（张量）+Vector（向量）+Scalar（控制）三类异构单元与L1→L0A/B→L0C→UB四级紧耦合SRAM，将数据复用尽量留在片内，显著降低外部HBM带宽压力，为不同精度算子（FP32/FP16）提供差异化高吞吐通路。

**论文作用**：作为AI Core基础结构图，奠定后续计算密度、片上存储层次、带宽模型与算子映射（matmul/conv）论述的硬件基础。

### Figure 402 (p.18) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig402.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p18.png]]*
> [!quote] caption
> Cube Core 处理架构示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构：** 图示上半部为K组(x_i, y_i)输入对，分别进入独立Cube单元执行乘加；中间通过Σ单元完成部分和汇聚；下方为4×4共16个PE_S阵列承接结果并并行完成累加/写回。整体呈现"分组MAC → 局部Σ → PE_S并行处理"的三级脉动流水结构。

**2) 关键技术结论：** Cube Core通过脉动阵列实现高并行矩阵乘加，每PE_S独立承担部分和的计算与存储，大幅降低片内数据搬运开销，体现Cube算力核心的并行性与能效优势。

**3) 论文作用：** 作为Ascend 950 NPU中Cube Core的微架构示意，为后续算子映射、数值精度支持及峰值算力分析提供硬件结构依据，是整篇架构白皮书算力底座的图示基础。

### Figure 403 (p.18) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig403.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p18.png]]*
> [!quote] caption
> Cube Core 支持的数值精度示意

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示Cube Core支持的8种数值精度格式及其位宽分配（符号/指数/尾数）：FP32(1+8+23)、TF32(1+8+10)、BF16(1+8+7)、FP16(1+5+10)、HiF8（动态分配）、FP8-E5M2(1+5+2)、FP8-E4M3(1+4+3)、FP4(1+2+1)，覆盖32/16/8/4-bit四档。

该图论证Cube Core具备从FP32高精度训练到FP4/FP8低比特推理的完整精度谱系，硬件原生支持混合精度与量化工作负载；在论文中作为算子精度能力的核心佐证，支撑后续关于算力、能效与AI全栈适配性的论述。

### Figure 404 (p.19) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig404.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p19.png]]*
> [!quote] caption
> HiF8 数值精度

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**核心对象与结构：**
该图定义 HiF8 这一8位浮点格式。Normal 子类采用变长前缀码 Dot（0–4，共5档）自适应分配阶码位宽：Dot=0 隐含阶 E=0、Dot=1(E=±1)、Dot=2(E=±[2,3])、Dot=3(E=±[4,7])、Dot=4(E=±[8,15])，每升一档阶码增加1位、尾数 M 由3位递减至1位，总位宽恒为8（红色数字代表不存储的隐藏位）。Denormal 子类用"0000"前缀 + 3位 M 表示 E∈[-22,-16]。阶码额外含1位 SE（Sign of Exponent）。

**关键结论：** HiF8 以变长前缀在8位内同时覆盖大动态范围（最高 ±2^15）与小数（denormal 至 2^-22），按数值大小自适应精度与范围。

**论文作用：** 作为 Ascend 950 NPU 数值体系中的低精度浮点格式，为 AI 推理/训练提供高动态、低存储开销的运算支持。

### Figure 405 (p.21) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig405.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p21.png]]*
> [!quote] caption
> Vector Core 架构示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**1) 核心对象与结构**

图示Vector Core整体架构。左侧顶层由Scalar Unit、Async Function Queue（含Func0–Func6共6个槽位，分别标注SIMT/SIMD/NULL）、DMA Unit、Vector Unit SIMD/SIMT、Vector Cache/Buffer、Bus Interface、Global Memory自上而下串联。右侧细化两条执行路径：①**SIMD模式**——I Cache→Program Sequence→**OoO Dispatch**→Vector Cache/Unified Buffer（N个Bank+Cache Controller+Coalescing Unit）→Vector Load/Store Unit→**Vector Register File（Lane 0…Lane VL-1）**→Vector Execution Unit；②**SIMT模式**——I Cache→Program Sequence→**Warp Scheduler**→**In-order Dispatch**→共用N-bank Vector Cache/Unified Buffer→**SIMT Load/Store Unit**→**SIMT Register File（Lane 0…Lane warp_size-1）**→Vector Execution Unit。

**2) 关键结论**

论证同一Vector Core通过共享数据通路与执行单元，仅前端调度（OoO vs. Warp Scheduler+In-order）与寄存器宽度（VL vs. warp_size）差异，即可同时支撑SIMD高效向量计算与SIMT线程级并行。

**3) 论文作用**

作为Ascend 950异构并行架构的核心运算单元，向上衔接Scalar调度与指令派发，向下贯通Global Memory存储体系，是全篇并行编程模型与硬件承载论述的基础图示。

### Figure 406 (p.22) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig406.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p22.png]]*
> [!quote] caption
> AI Core Cube-Vector 融合示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心对象与结构**：展示单 AI Core 内 Cube-Vector 异构融合微架构。两侧对称布置 Vector Core 0/1，各配独立 Register File 与统一缓冲区 UB0/UB1；中央为 Cube Core，配三级片上存储——L1（顶部共享）、L0A/L0B（矩阵乘双输入）、L0C（累加输出）；上下 Bus Interface 对接 HSM/HBM。4 组橙色双向箭头标识 UB↔L1、UB↔L0C 的数据通路。

2) **关键结论**：Cube 与 Vector 通过 L1 与 UB 紧耦合共享存储，矩阵乘结果经 L0C→UB 直供 Vector 完成 activation、归一化等逐元素算子，省去 HBM 往返与显式数据拷贝，支撑 Cube-Vector 流水线式融合执行。

3) **论文作用**：作为 AI Core 微架构蓝图，奠定后续片上存储层次、并行扩展、带宽/性能分析的参照，体现 Ascend 950 "异构融合+共享存储" 的核心设计思路。

### Figure 407 (p.23) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig407.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p23.png]]*
> [!quote] caption
> NDDMA 指令

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示 **NDDMA（非连续直接内存访问）指令** 的数据搬运行为。左为 Global Memory（共32行），24个数据元素（1–24）按 2元素/组×9组 + 6个单元素的非连续模式散布，行间存在空隙（如第6、11、12行空缺）；右为 UnifiedBuffer，经 NDDMA 搬运后，数据被紧凑地重新排列为连续序列 1,2,3,5,6,7,9,10,11,13,14,15,17,18,19,21,22,23…，消除了原布局中的步进间隔。

原文借此论证的关键结论：**单条 NDDMA 指令即可完成"跨步/非连续 Global Memory → 连续 UnifiedBuffer"的重组**，无需软件介入做地址计算或中间缓存拷贝。

在论文整体链路中，该图属于 NPU 数据通路章节，用以说明 DMA 子系统为 Cube/Vector 计算单元提供就绪数据布局的能力，是片上存储与计算流水线高效衔接的关键支撑机制。

### Figure 408 (p.24) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig408.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p24.png]]*
> [!quote] caption
> 昇腾950 新同步机制代码示例

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心对象与结构**：图示对比两种 MTE2→Vector 流水同步写法。左侧"set_flag/wait_flag"机制在 100 次循环中每轮插入 4 个同步原语（wait_flag、set_flag×2）并需 `if i>0`、`if i<99` 条件判断；右侧"BufferID"机制用 `get_buf(MTE2,#id)` 与 `rel_buf(V,#id)` 将同步隐式绑定到缓冲区生命周期，仅 4 个调用、无条件分支。

2) **关键技术结论**：BufferID 新机制以"获取—释放"对替代显式 flag 握手，逻辑步骤由 8 行压减为 7 行，省去边界条件判断，证明同步可被缓冲区生命周期吸收，降低编程复杂度与出错面。

3) **论文作用**：作为昇腾 950 新同步机制的代码级佐证，与架构层论述相互印证，体现"硬件能力下沉为编程原语"的设计思路。

### Figure 409 (p.25) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig409.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p25.png]]*
> [!quote] caption
> 昇腾950 内存层次示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示昇腾950双Die（Die 0/Die 1）内存层次拓扑：每Die内含多个AI Core与AI CPU。AI Core内部分为AIC（含L1、L0A/L0B/L0C缓存）与AIV（含L1、UB统一缓冲）；AI CPU独立配置CPU L1/L2。Die内AI Core共享L2 Cache、CPU侧接L3 Cache，跨Die通过Directory维持缓存一致性，底层统一对接Global Memory。

原文借此论证三点：①AIC/AIV异构分区使标量与向量访存解耦，L0A/B/C三级缓存降低指令重复访问开销，UB作为片上数据中转提升数据复用；②多Die通过Directory实现全局一致地址空间，支撑大模型跨Die张量并行；③L2/L3/GM分层提供容量与带宽的逐级放大。

该图位于硬件架构章节，为后续片上存储容量、带宽指标及一致性协议设计提供拓扑基础。

### Figure 410 (p.27) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig410.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p27.png]]*
> [!quote] caption
> Non-allocate（L2 hint）典型应用场景示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】【核心对象】图示展示两条差异化数据通路：data A经"non-allocate"标记由Task0直接穿透至Global Memory，不进L2；data B则由Task0写入L2 Cache，再被Task1命中复用。

【技术结论】原文论证：non-allocate hint允许软件声明一次性数据绕过L2，避免污染并节约缓存容量；可复用数据驻留L2供后续任务命中，减少对Global Memory的重复访问，体现软硬协同的片上缓存精细管控。

【链路作用】位于存储层级与缓存管理软件接口章节，作为L2 hint机制的典型场景示例，为后续prefetch、cache hint等优化手段提供动机铺垫。

### Figure 411 (p.27) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig411.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p27.png]]*
> [!quote] caption
> STARS2.0 架构示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图示联合解读（基于图片实际内容"STARS2.0 架构示意图"）：**

**1) 核心对象与结构：** 图示分两层——上层为STARS调度框，内含4列Task堆叠队列、4个能力模块（Notify Sync / Conds / Profiling / Fusion）及底部Sched调度器；下层经两条总线外联——左侧HSCB总线挂接AIV、AIC计算簇，右侧NoC总线挂接UB DMA、SDMA、CCU、CPU、DVPP共5类异构IP，每类以多实例堆叠呈现。

**2) 关键技术结论：** STARS2.0通过Task队列抽象+Fission/Notify/Profile/Conds/Fusion五大机制，将计算簇（AIV/AIC）与非计算IP（DMA/SDMA/CCU/CPU/DVPP）统一封装在同一调度接口下，实现"软硬件协同解耦"——上层框架只需关注Task依赖与编排，无须感知底层异构拓扑。

**3) 在论文链路中的作用：** 作为全篇硬件架构总览图，奠定后续算子并行切分、L2 hint内存管理、SDMA/DVPP协同等章节的调度底层依据，凸显Ascend 950"软件定义硬件、统一任务抽象"的设计理念。

### Figure 412 (p.31) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig412.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p31.png]]*
> [!quote] caption
> URMA 异步访存通信的过程示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）该图刻画URMA异步访存通信的两端结构：发起端包含Core、URMA模块与本地UMMU，并配有4个Port（带省略号表示可扩展）；接收端由对等Port、本地UMMU构成。数据流（橙色箭头）经本地Memory→UMMU→URMA→多Port→对端UMMU→远端Memory，全程由Core通过"Doorbell"门铃信号异步触发URMA执行，无需CPU参与搬运。

2）该图论证的关键结论：URMA通过硬件Doorbell机制与双端UMMU地址翻译，实现绕过处理器核的直接Memory-to-Memory异步传输；地址翻译由硬件卸载，Core仅发触发信号即可释放计算资源。

3）在论文方法链路中，此图为URMA通信模型提供架构示意，是昇腾950 NPU片间/卡间高效访存与解耦通信能力论述的支撑图，奠定后续带宽、延迟优化的讨论基础。

### Figure 413 (p.32) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig413.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p32.png]]*
> [!quote] caption
> UB Memory 同步访存语义地址通信过程示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示UB Memory同步访存语义下跨域地址通信链路：Core发出访存请求→UB Mem Decoder解析并扇出至多个并行Port（左域）→经Port-Port对穿通道传输至右域Port→汇聚送入UMMU（统一内存管理单元）进行地址翻译→落达目标Memory；底部两域各挂独立Memory，体现源/目的端分离。

技术结论：Ascend 950通过"多Port并行分发+UMMU统一地址映射"机制，实现UB同步访存语义的跨核/跨簇透明地址通信，在保证一致性的同时提升访存吞吐与并行度。

作用：作为片上互联与内存子系统的核心证据，为论文论证NPU多核协同、统一地址空间与高性能访存模型提供硬件流程支撑。

### Figure 414 (p.33) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig414.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p33.png]]*
> [!quote] caption
> CCU 架构示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示了CCU的层次化架构，顶层为CCUM（含Mission Call Interface、多个Mission Commander、Instruction Implementation Unit），其下分出Reduce Call Interface与URMA Call Interface两条调度通道。中间层为多个CCUA实例，每实例含Memory Slice组与Reduce Unit，承接Reduce任务。最底层URMA模块通过URMA Call Interface获取指令，底部连接多个Port用于外部互联。

该图论证的关键结论是：CCU采用"中央调度（CCUM）+分布式执行（CCUA）"的两级架构，将集合归约与远程内存访问解耦为独立通路（红/蓝线分别下发给Reduce Unit与URMA），并通过多Mission Commander、多Memory Slice实现任务并行、内存切片化处理，从而支撑高效集合通信与跨设备数据搬运。

在论文整体方法链中，本图为Ascend NPU通信子系统的核心架构说明，为后续集合通信性能、带宽利用率分析提供硬件拓扑基础。

### Figure 415 (p.34) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig415.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p34.png]]*
> [!quote] caption
> UB On Chip Switch 转发示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）图中呈现三层结构：底层为多个 **Port**（端口），中间层为 **Routing Table**（路由表），顶层为 **Network On Chip**（片上网络）；实线表示各 Port 与 Routing Table、NoC 的常规连接，虚线及向下箭头标注了一条具体转发路径，形象展示包从 Port 经查表后送往 NoC 的过程。

2）该图佐证了 **UB On-Chip Switch 通过集中式路由表实现端口间转发** 的结论：每个 Port 接收的数据依据 Routing Table 决策下一跳/出口，再注入 NoC，端口—路由表—网络三级解耦保证了转发确定性与可扩展性。

3）在论文中，此图属于 UB 互连子系统的微结构说明，配合整体 NoC 拓扑章节，支撑 Ascend 950 片内高带宽、低延迟数据通路的设计论证，是架构层级"结构图"链路的关键一环。

### Figure 416 (p.35) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig416.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p35.png]]*
> [!quote] caption
> PCIe 5.0 架构示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示展示了 Ascend 950 NPU 中 **PCIe 5.0 子系统的分层架构**：自上而下依次为连接片内 System Bus 的**应用层**（含 MCTP 管理协议与 DMA 数据搬运引擎，以深蓝高亮标示）、**事务层**、**数据链路层**、**物理层（×16 通道宽度）**，最底层为浅青色标注的 **SerDes** 收发器。

该图论证 Ascend 950 采用 **PCIe Gen5 ×16 接口**（理论单向带宽约 64 GB/s、双向约 128 GB/s），通过 MCTP+DMA 协同实现片外主机侧的设备管理与高效数据搬运，并以 ×16 物理通道 + SerDes 保障高带宽低延迟的板级 I/O。

在论文整体链路中，本图位于 **I/O 互连子系统章节**，承接前文片上互连（L2C/HCCS/NLINK）的论述，呈现"**片内—封装内—板级**"三尺度完整数据通路，支撑后续训练/推理场景中模型与张量的主机侧供给及多卡横向扩展能力。

### Figure 417 (p.36) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig417.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p36.png]]*
> [!quote] caption
> 昇腾950 的一种超节点示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示昇腾 950 超节点的三层 Clos 式交换拓扑：底层为多颗 Ascend 950 芯片（蓝框，下方曲线表示芯片间高速全互连），中层为机柜/域内若干 Switch，最上层为跨域顶层 Switch 组（用"…"表示可扩展）。芯片→域内 Switch→顶层 Switch 形成多级交换树，体现大规模高带宽域内/域间互连。

该图论证的关键结论：超节点通过多级交换拓扑将数百至数千颗 Ascend 950 统一为单一算力域，兼顾域内高带宽与域间可扩展性，实现"scale-out 而非仅 scale-up"。

其作用：作为芯片→整机柜→超节点的体系结构证据，支撑论文阐述昇腾 950 在系统层级（而非裸片层级）实现大模型训练/推理集群协同的设计主张，是超节点章节的拓扑总览图。

### Figure 418 (p.36) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig418.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p36.png]]*
> [!quote] caption
> 昇腾950 访问CPU 超大内存池示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示了**两个机柜（Rack）**通过顶部**交换机（Switch，多节点堆叠）**互联的拓扑：

- **左侧机柜**：承载两组昇腾950 NPU集群，每组上方配CPU，NPU（Ascend950方块）作为计算主体；
- **右侧机柜**：三层结构，每层由CPU行配**Memory Pool（深蓝色大容量内存块）**组成，作为被访问的"超大内存池"。

**论证结论**：昇腾950 NPU无需自带超大HBM，可通过交换网络远程透明访问CPU侧大内存池，实现**存算解耦（disaggregated memory）**，突破NPU本地存储容量上限。

**论文作用**：该图作为关键架构证据，支撑昇腾950"超大内存寻址"设计主张，体现其在大模型训练/推理场景中利用分布式CPU内存扩展可用存储空间、提升单卡/集群有效容量的整体方法论。

### Figure 419 (p.37) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig419.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p37.png]]*
> [!quote] caption
> 昇腾950 直接访问超大存储资源池示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图中展示了基于**交换机的计算-存储分离架构**：左侧为计算Rack，包含2组（每组2+ CPU与3+ Ascend950），右侧为存储Rack，部署5行×3列以上的Storage节点池，两者通过顶部交换机多链路互联。

**核心结论**：Ascend 950 通过交换机**绕过CPU**，直接访问远端超大规模共享存储资源池，实现计算资源与存储资源的解耦与池化。

**论文作用**：该图作为架构示意图，佐证昇腾950面向大模型训练/推理场景中"存算分离、存储共享"的设计思路，强调NPU对外部存储的高带宽、低延迟直访能力，为后续容量与带宽扩展性论证提供拓扑依据。

### Figure 420 (p.38) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig420.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p38.png]]*
> [!quote] caption
> 昇腾超节点基于UB Switch 转换为以太网与以太世界互通示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**核心对象与结构**：图示一个昇腾超节点，包含2个外部 Ethernet Switch、2个 UB Switch（每个均配1个 ETH 上行口+1个 UB 下行口）以及若干 Ascend950 NPU。呈现三级互联：①底部 NPU 之间以 UB 曲线直连（对等链路）；②UB Switch 经 UB 绿色线与全部 NPU 全互联 Mesh；③UB Switch 经 ETH 蓝色线交叉上联两台外部以太网交换机。

**关键技术结论**：UB Switch 作为 UB 协议 ↔ 以太协议转换枢纽，凭借双 ETH 上联实现跨超节点扩展；超节点内部 UB 全互联 Mesh 保证 NPU 高带宽近距通信，与外部以太网共同构成"近距 UB + 远距 ETH"的分级互联体系。

**论文作用**：该图论证了 Ascend950 超节点仅凭 UB Switch 即可无感接入标准以太网基础设施，是其"超节点 + 通用以太网"可扩展架构的核心证据，为全篇大规模集群组网论述提供硬件可行性支撑。

### Figure 421 (p.39) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig421.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p39.png]]*
> [!quote] caption
> 昇腾芯片支持以太网与以太世界互通示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示Ascend950芯片的双模混合互联拓扑：底层4颗（省略号示更多）Ascend950 NPU各集成ETH端口，通过蓝色ETH链路全交叉上联至同一机箱内的2个以太网交换机；后者再交叉对接机箱外2个外部以太网交换机，实现与外部"以太世界"互通；NPU之间另通过绿色UB总线两两直连，形成片间Mesh互联。

原文以此论证关键技术结论：Ascend950原生集成以太网MAC/接口，可无缝接入标准以太网生态，同时保留片间专用UB高速总线，二者并行兼顾开放兼容与高带宽低延迟通信。

该图在论文整体方法/实验链路中的作用：作为Ascend950互联架构的示意证据，支撑其在数据中心集群中"标准以太网+专用互联"双通道部署的可行性与扩展性论述。

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
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与数据**
该表（表3-1）汇总昇腾 950PR 与 950DT 两款芯片的关键规格，涵盖：128MB 统一 L2 Cache、STARS2.0 任务调度、片上 HBM（PR：1.6TB/s + 128GB；DT：4TB/s + 144GB）、Unified Bus 2.0 互联（72×HiLink 112Gbps 拆分为 18 Port，支持 URMA/UB Memory 语义，PCIe GEN5 x16 兼容 GEN4/3/2/1 的 EP/RC 模式，以及 2×400Gbps UBoE 以太接入，可拆分为 1×400/200/100/50/25Gbps 或 2×200/100/50/25Gbps）。

**2) 关键技术结论**
两款芯片同源于 950 平台设计，DT 版在内存带宽（4TB/s）和容量（144GB）上较 PR 版分别提升约 2.5× 和 12.5%，而 L2、调度器与 UB2.0 互联子层保持一致，体现"统一架构、按规格衍生"的策略。

**3) 在论文中的作用**
该表是 950 系列整体规格的"对照基线"，承接前文架构介绍，并为后文 PR/DT 衍生版本及不同产品形态的应用提供量化依据。

### Table 401 (p.20) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-tab401.png]]
> [!quote] caption
> HiF8 特殊值编码

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示 HiF8、E4M3、E5M2 三种 8 位浮点格式的"有效精度(bit)—阶码"映射锥形图。

**1）核心数据：** HiF8 阶码覆盖 [-22, 15] 共 38 个 2 的幂次（接近 FP16 的 [-24, 15]），有效位含 1.M 隐位比尾数多 1 bit；精度呈锥形渐变、无跳变——E∈[-22,-16] 为 1 bit（DML 区，橙圈标注）、[-15,-8] 为 2 bit、[-7,-5] 为 3 bit、[-4,4] 达 4 bit、[5,15] 回落 2 bit。E4M3 仅覆盖 -7~8 且右端掉至 2 bit，E5M2 几乎全段恒为 3 bit。

**2）关键结论：** 相比 E4M3 范围窄、E5M2 中段精度低，HiF8 同时兼顾宽动态范围与近 1 处高密度精度，并额外编码 4 个特殊值（不区分 ±0）。

**3）论文作用：** 作为表 401"HiF8 特殊值编码"的可视化佐证，论证 HiF8 格式在精度分布上的设计优势，为 Ascend 950 NPU 推理计算数值方案的选型提供量化依据。

### Table 402 (p.25) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-tab402.png]]
> [!quote] caption
> 昇腾 950 Memory 层次中主要 Memory 及其大小

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心对象与结构**：图示昇腾950双Die（Die0/Die1）内存层次。每Die含多AI Core与AI CPU；AI Core内AIC子单元含L1、L0A、L0B、L0C、UB缓冲区，AIV子单元含UB；AI CPU含CPU L1/L2。Die级设统一L2 Cache与L3 Cache，底层为Directory（Cache Coherence）与Global Memory，形成"核内→Die级→全局"三级存储体系。

2) **关键技术结论**：UB作为AIC/AIV共享数据通路衔接矩阵运算；L0A/L0B/L0C分级缓冲降低片内搬运开销；Die间经Directory维护Cache一致性；L2/L3 Cache有效缓解对Global Memory的访问压力，提升带宽利用率与能效比。

3) **论文作用**：作为硬件架构章节核心拓扑图，为后续Cube计算单元、算力指标、访存带宽与并行调度等性能分析提供内存层次基础。

## 技术点深读（DEEP）

![[deep/ascend-950-npu-architecture-whitepaper]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/ascend-950-npu-architecture-whitepaper.txt`（28777 字符）供引用检索。