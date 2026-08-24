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
> 【图文联合解读】**图文联合解读：**

该图实为正文段落而非架构示意图，仅依据文字与上下文解读。所述昇腾950为多Die合封Chiplet：含2个AI Die、2个IO Die，950PR配8个、950DT配4个HBM片上内存模组，通过D2D Clink与Memory Interface互联，构成UMA整体。结合原文论证：①Chiplet封装实现内存统一访问与扩展性；②Cube Core数量32/28/36、Vector Core 64/56/72，算力梯度按精度逐级递减，MXFP4下Cube算力最高达1946 TFLOPS；③支撑LLM算子加速（FlashAttention单核提升1.5~2倍）与CCU通信-计算融合，软硬协同支撑Super Node从384卡扩展至8K卡，是大模型训练推理全流程加速的硬件基石。

### Figure 401 (p.17)
![[assets/ascend-950-npu-architecture-whitepaper-p17.png]]
> [!quote] caption
> AI Core 架构及各层级SRAM 示意图

### Figure 402 (p.18)
![[assets/ascend-950-npu-architecture-whitepaper-p18.png]]
> [!quote] caption
> Cube Core 处理架构示意图

### Figure 403 (p.18) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig403.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p18.png]]*
> [!quote] caption
> Cube Core 支持的数值精度示意

> [!tip] 技术解读（多模态）
> 【图文联合解读】**注意：图与所给caption存在冲突**——题目称图为"数值精度示意"，但实际图像标题为「图4-2 Cube Core 处理架构示意图」。以下按图像真实内容解读：

**1) 核心对象与结构**：图像展示Cube Core的脉动式PE阵列微架构。上半部示意k个输入流（x₀…x_{k-1} 与 y₀…y_{k-1}）沿正交方向注入一排PE单元；下半部展开为 4×4 PEs 网格，所有PE输出汇聚至 Σ 累加单元，完成矩阵乘累加（MAC）运算。

**2) 关键技术结论**：Cube Core 通过二维 PE 阵列实现大规模乘加并行，是 Ascend 950 张量算力的硬件载体；Σ 树形归约支持高吞吐、低延迟的矩阵乘法，是后续混合精度、稀疏加速等功能扩展的物理基础。

**3) 论文整体作用**：作为第四章计算引擎微架构的图示锚点，为后续章节（算力峰值推算、精度支持、数据流优化等）提供结构化依据。

### Figure 404 (p.19)
![[assets/ascend-950-npu-architecture-whitepaper-p19.png]]
> [!quote] caption
> HiF8 数值精度

### Figure 405 (p.21)
![[assets/ascend-950-npu-architecture-whitepaper-p21.png]]
> [!quote] caption
> Vector Core 架构示意图

### Figure 406 (p.22) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig406.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p22.png]]*
> [!quote] caption
> AI Core Cube-Vector 融合示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**说明**：所提供内容仅为论文正文文字段落，未呈现实际的 Cube-Vector 融合架构示意图，故仅依据 4.1.4 节文本进行解读。

---

**图文联合解读**：

1) **核心对象与结构**：图示应展示 AI Core 内 Cube 核（含 L1 Buffer）与 Vector 核（含 Unified Buffer）通过一条**直连 CV 数据传输通道**相连，绕过 L2 层进行核内数据交换，体现 SIMD 为主、SIMT 为辅的新异构融合编程架构。

2) **关键技术结论**：Cube L1 Buffer 与 Vector Unified Buffer 间的直连通道免去了 L2 中转，显著**提高核内数据复用率**，减少 L2 层数据搬移开销，从而提升 CV 融合算子的执行效率。

3) **论文整体作用**：作为硬件级证据，支撑新架构在端到端吞吐、时延与开发效率三者之间取得更优平衡这一核心论点，是"CV 融合"特性论证的关键图示。

### Figure 407 (p.23)
![[assets/ascend-950-npu-architecture-whitepaper-p23.png]]
> [!quote] caption
> NDDMA 指令

### Figure 408 (p.24)
![[assets/ascend-950-npu-architecture-whitepaper-p24.png]]
> [!quote] caption
> 昇腾950 新同步机制代码示例

### Figure 409 (p.25) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig409.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p25.png]]*
> [!quote] caption
> 昇腾950 内存层次示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**核心对象与结构：** 该图展示昇腾 950（950PR/950DT）的内存三级层次——底层为高速片上 DRAM（缓存全局数据，两型号配置不同），中层为 L2 Cache（服务 AIC/AIV 的 AI 计算，与片上内存双向搬运），上层为 L3 Cache（服务 AI CPU 通用计算），三级间以高带宽低延迟链路连通。

**关键技术结论：** 原文以此论证，分层存储将 AI 加速器与 CPU 的数据访问局部化——L2 以"片上 DRAM↔AIC/AIV"双向通路承担高吞吐 AI 数据流，L3 服务 CPU 通用任务，分工明确，整体提升 Memory 子系统效率。

**论文作用：** 该图作为硬件架构总览的关键图示，与执行单元、数据流等章节联动，为读者建立"存储-计算"协同的整体认知框架，是论文方法论证的视觉锚点。

### Figure 410 (p.27)
![[assets/ascend-950-npu-architecture-whitepaper-p27.png]]
> [!quote] caption
> Non-allocate（L2 hint）典型应用场景示意图

### Figure 411 (p.27) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig411.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p27.png]]*
> [!quote] caption
> STARS2.0 架构示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**：

需说明：图片实际为**图4-10 "Non-allocate (L2 hint) 典型应用场景示意图"**，而非所提示的 Figure 4-11 STARS2.0 架构图。以下按图实内容解读：

1. **核心对象与结构**：图中两个并行任务 Task0、Task1。其中 Task0 输出的 **data A** 沿 `non-allocate` 属性路径直接写入 Global Memory（绕过 L2 Cache）；而 Task0 与 Task1 共用的 **data B** 则经由 L2 Cache 中转复用，体现"绕过 vs. 复用"的差异化分配。

2. **论证的技术结论**：佐证正文所述——异腾 950 针对 SDMA 提供 L2 Cache 驻留策略（CMO），涵盖 Prefetch、Writeback、Flush 三类操作，程序员可通过配置参数控制 CMO 触发时机与作用域，从而按需决定数据是否驻留 L2。

3. **链路作用**：该图位于 4.4 节"软硬协同高效调度：STARS2.0"之前，承担**承上启下**作用——以存储层级访存优化收束，随后转入 STARS2.0 硬件调度器在任务/资源/数据流层面的协同调度论述。

### Figure 412 (p.31)
![[assets/ascend-950-npu-architecture-whitepaper-p31.png]]
> [!quote] caption
> URMA 异步访存通信的过程示意图

### Figure 413 (p.32)
![[assets/ascend-950-npu-architecture-whitepaper-p32.png]]
> [!quote] caption
> UB Memory 同步访存语义地址通信过程示意图

### Figure 414 (p.33)
![[assets/ascend-950-npu-architecture-whitepaper-p33.png]]
> [!quote] caption
> CCU 架构示意图

### Figure 415 (p.34)
![[assets/ascend-950-npu-architecture-whitepaper-p34.png]]
> [!quote] caption
> UB On Chip Switch 转发示意图

### Figure 416 (p.35)
![[assets/ascend-950-npu-architecture-whitepaper-p35.png]]
> [!quote] caption
> PCIe 5.0 架构示意图

### Figure 417 (p.36) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig417.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p36.png]]*
> [!quote] caption
> 昇腾950 的一种超节点示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】图像无法辨认，仅依据原文解读。

**图文联合解读：**

1. **核心对象**：图 417 的标题为"昇腾 950 的一种超节点示意图"，按 caption 应展示昇腾 950NPU 超节点（Super-Node）的拓扑结构，包括多颗 NPU 芯片经高带宽互连（如 HCCS/UB 或自研总线）组成的紧耦合域，可能涉及片间/机框级互联、共享内存或拓扑编排示意。但实际图片仅显示章节标题"4.7 超节点能力 / 4.7.1 异腾超节点"，并无具体拓扑图。

2. **关键技术结论**：原文将其置于 4.7 节，作为昇腾 950 区别于单芯片能力的关键论据——通过超节点互联扩展算力规模与通信带宽，支撑大模型训练/推理中的跨芯片并行与协同。

3. **论文作用**：承接前文单芯片微架构、Cache/HBM、计算单元等设计，论证昇腾 950 由"单 NPU"扩展到"超节点"的系统级扩展能力，是性能规模化叙事的关键支撑图。

### Figure 418 (p.36) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig418.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p36.png]]*
> [!quote] caption
> 昇腾950 访问CPU 超大内存池示意图

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示呈现昇腾950超节点的三层交换拓扑：底层多颗Ascend 950芯片以曲线互联呈Full Mesh；中层各集群内Switch汇聚芯片间通信；顶层Switch跨集群互联，构成Clos/混合组网。原文据此论证：基于UB（Unified Bus）互连协议配合UB Switch，可组建K级别规模的超节点，芯片间通过UB实现高效通信，并支持Full Mesh、Clos、灵活混合等多种拓扑。该图位于4.7.2节"超节点与超大内存池组网"开篇，确立横向扩展架构框架，为后续引入CPU超大内存池共享与池化组网方案铺垫技术前提。

### Figure 419 (p.37)
![[assets/ascend-950-npu-architecture-whitepaper-p37.png]]
> [!quote] caption
> 昇腾950 直接访问超大存储资源池示意图

### Figure 420 (p.38)
![[assets/ascend-950-npu-architecture-whitepaper-p38.png]]
> [!quote] caption
> 昇腾超节点基于UB Switch 转换为以太网与以太世界互通示意图

### Figure 421 (p.39)
![[assets/ascend-950-npu-architecture-whitepaper-p39.png]]
> [!quote] caption
> 昇腾芯片支持以太网与以太世界互通示意图

## 表格（裁剪图 + caption，可直接插入报告）

### Table 101 (p.5) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-tab101.png]]
> [!quote] caption
> 关键术语

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表为表1-1"关键术语"，含11条术语分两列（术语/描述），具体为：AIC/AIV（AI Cube Core与Vector Core分离架构下的两类核心）、AI CPU（自研Linx816 ARM内核）、AI Die（昇腾950PR/950DT的计算Die）、CANN（异构计算架构软件栈）、CMO（SDMA实现的L2 Cache管理机制）、CTP（Unified Bus轻量级传输层）、Clos（多级无阻塞交换网络）、AIGC、Dice、Device等。

原文以此论证昇腾950的五大技术维度：①计算核心分离架构（AIC+AIV）、②自研CPU内核（Linx816）、③异构软件栈（CANN）、④片上存储与传输（SDMA/CMO、CTP）、⑤芯片与多级组网（AI Die、Clos）。

该表是论文开篇的术语约定层，为后续架构细节、章节展开及读者理解提供统一语义基准，起到铺垫与锁定关键概念的作用。

### Table 301 (p.13) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-tab301.png]]
> [!quote] caption
> 昇腾 950 系列芯片支持的主要规格

> [!tip] 表格解读（多模态）
> 【图文联合解读】表3-1量化呈现昇腾950PR与950DT两款芯片AI子系统的核心规格：Cube Core数量32/28 vs 36/32/28，Vector Core 64/56 vs 72/64/56；Cube+Vector总算力在MXFP4下达1784/1561与2007/1784/1561 TFLOPS，HiF8/MXFP8/FP8与INT8分别为919/804与1034/919/804，BF16/FP16为486/425与547/486/425，TF32为243/212与273/243/212；Cube算力MXFP4为1730/1513与1946/1730/1513 TFLOPS。斜杠区分不同功耗档位。

原文借此论证：①950DT规格全面领先950PR，核心数与算力更高；②覆盖MXFP4至TF32多精度，算力随位宽逐级递减；③Cube单元承担矩阵运算主体。

作用：作为白皮书的硬件算力基线表，为后续微架构、指令集及软件栈的设计分析提供量化参考。

### Table 401 (p.20) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-tab401.png]]
> [!quote] caption
> HiF8 特殊值编码

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心内容**：表4-1列出HiF8浮点格式对四类特殊值的8位编码——ZERO=00000000、NAN=10000000、+INF=01101111、-INF=11101111。颜色区分了符号位（红色高位）与数值位（绿色低位），清晰展示各特殊值在8比特空间中的排布。

2) **论证结论**：该表证明HiF8在仅8比特的紧凑表示下，仍完整保留了IEEE风格特殊值语义——零、正负无穷、NaN互不冲突且可被硬件/软件直接判别，体现了HiF8作为Ascend 950 NPU低精度张量计算核心数据类型的完备性。

3) **作用定位**：在论文整体方法链路中，HiF8特殊值编码表是"精度定义"章节的基础规范表，为后续矩阵引擎（Cube）、向量单元在低精度训练/推理中处理边界值（除零、上溢/下溢、异常标记）提供硬件判别依据，是连接"格式定义"与"微架构实现"的关键参考。

### Table 402 (p.25) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-tab402.png]]
> [!quote] caption
> 昇腾 950 Memory 层次中主要 Memory 及其大小

> [!tip] 表格解读（多模态）
> 【图文联合解读】表4-2量化昇腾950的11级Memory容量：AI Core内L0A/B各64KB（输入/权）、L0C 256KB（累加）、L1与UB各512KB；CPU侧L1 64KB、L2 1MB、L3 4MB/Cluster；共享L2 Cache≤128MB；片上内存PR型≤128GB、DT型96/144GB。

**关键结论**：L0A/B/C分离为Cube Core的乘累加数据流（x、y经Σ部分和）提供专用高速缓冲，配合UB与大容量片上内存，形成"近核高带宽—远端大容量"的存储层次，支撑矩阵复用，缓解访存对Cube算力的制约。

**作用**：为论文后续算力利用率推导、tiling切分策略与软件栈优化提供基础存储参数。

## 技术点深读（DEEP）

![[deep/ascend-950-npu-architecture-whitepaper]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/ascend-950-npu-architecture-whitepaper.txt`（28777 字符）供引用检索。