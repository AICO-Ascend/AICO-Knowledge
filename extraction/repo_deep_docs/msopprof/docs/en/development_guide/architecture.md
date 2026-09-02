# MindStudio Ops Profiler Architecture Design Specifications

> 仓 `msopprof` · 路径 `docs/en/development_guide/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msopprof/docs/en/development_guide/architecture.md

```markdown
# MindStudio Ops Profiler 架构设计规范 — 深度解读

## 【定位】
本文档为 Ascend 算子调优工具（msopprof）的**架构设计输入文档**，定义算子开发工具链中算子调优组件的功能模块、主数据结构与关键处理流程，作为编码阶段的输入与开发/测试人员的指导。

---

## 【技术要点】
1. **两类算子性能数据来源**：算子仿真（在 Ascend 模拟器上通过指令级仿真产出 pipeline 图、代码热点图等细节数据）与**板上 Profiling**（在真实 Ascend 设备上运行得到的真实性能数据，是最可信的数据源）。
2. **功能分类**：分为 Service function（服务功能，含 8 项）和 DFX function（DFX 功能，含 3 项）。
3. **板上调优（On-board tuning）专用功能**：计算内存热力图、Roofline 瓶颈分析图、Cache 热力图、MC2 算子的通信计算 pipeline 图、Profile 数据文件展示、早期进程终止。
4. **仿真调优（Simulation tuning）专用功能**：指令 pipeline 图、传输带宽图（GM↔L1、GM↔UB、GM↔others）、指定模拟器版本。
5. **共同支持功能**：算子代码热点图（On-board/Simulation 均支持）；Ctrl+C 终止（On-board/Simulation 均支持）。
6. **关键设计要素**：
   - **数据采集方式**：通过 **hijacking runtime interfaces（劫持运行时接口）** 进行 Profile 数据采集。
   - **解析方式**：利用**多线程并行解析**。
   - **传输优化**：采集阶段利用通信传输减少驱动写入（reduce drive writing）。
   - **调用模式**：支持多算子、多进程、多卡并行调用。
   - **准确性约束**：PMU 数据采集顺序与传输接口解析（动态插桩与模拟器指令解析）必须**严格遵循芯片手册**。
   - **扩展性**：覆盖数据采集、解析方式、新交付件、算子接入方式。

---

## 【关键机制与数据】
**Profile 数据流机制（原文）**：
- **算子接入路径**：不同算子接入方式可能需要被调用，Profile 数据采集通过劫持运行时接口（runtime interfaces）完成。
- **PMU 数据采集顺序**：必须严格遵循芯片手册（chip manual），涉及动态插桩（dynamic instrumentation）和模拟器指令解析（simulator instruction parsing）两条解析路径。
- **传输层**：采集侧利用通信传输降低驱动写入开销；解析侧采用多线程并行解析提升吞吐。
- **可信度差异**：On-board profiling 反映算子在硬件上的真实性能，被原文定位为"the most reliable source of operator performance data"。

性能数值/带宽数据：原文未给出具体数字，仅描述指标类别（如 L2 cache hit rate、内存读/写带宽、L0 读/写带宽、UB 读/写带宽、计算/MTE 单元时延比、资源冲突比等指标名称）。

---

## 【表格解读】

### 表 1：Service/Component Function List（服务/组件功能清单）

| Type             | Function                                                   | Description                                                                                                                                                                                                                             | Supported Tuning Type             |
| ---------------- | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| Service function | Computing memory heatmap                                   | Displays basic operator information, compute workload analysis, and memory workload analysis data by resource.                                                                                                                          | On-board tuning                   |
| Service function | Roofline bottleneck analysis chart                         | Constructs a performance model to quickly evaluate the theoretical performance limit of an operator.                                                                                                                                    | On-board tuning                   |
| Service function | Cache heatmap                                              | Visualizes the cache heatmap and displays corresponding instruction information to help optimize L2 cache hit rates.                                                                                                                    | On-board tuning                   |
| Service function | Communication and computing pipeline chart (MC2 operators) | Visually presents the communication-computing execution and instruction latency of MC2 operators to help identify bottlenecks.                                                                                                          | On-board tuning                   |
| Service function | Instruction pipeline chart                                 | Displays timing relationship by instruction and associates with the call stack to quickly trace bottlenecks.                                                                                                                            | Simulation tuning                 |
| Service function | Operator code hot spot map                                 | Displays the mapping between operator source code and instructions, as well as the time consumption. This helps developers identify hot spot code distribution and analyze the feasibility of hot spot function optimization.           | On-board tuning/Simulation tuning |
| Service function | Profile data files                                         | Displays instruction latency, L2 cache hit rate, memory read/write bandwidth rate, L0 read/write bandwidth rate, UB read/write bandwidth rate, basic operator information, compute/MTE unit latency ratio, and resource conflict ratio. | On-board tuning                   |
| Service function | Transfer bandwidth chart                                   | Displays bandwidth charts for data transfers between GM↔L1, GM↔UB, and GM↔others.                                                                                                                                                        | Simulation tuning                 |
| DFX function     | Ctrl+C support                                             | Terminates the operator process early. The tool can parse results based on currently collected data.                                                                                                                                    | On-board tuning/Simulation tuning |
| DFX function     | Early process termination                                  | Allows users to end the operator process at a scheduled time.                                                                                                                                                                           | On-board tuning                   |
| DFX function     | Specified simulator version                                | Allows users to set the simulator version directly.                                                                                                                                                                                     | Simulation tuning                 |

**逐行解读**：
- **Computing memory heatmap**：按资源维度展示算子基本信息、计算负载分析与内存负载分析数据，专属于板上调优。
- **Roofline bottleneck analysis chart**：构造性能模型，用于快速评估算子的理论性能上限，板上调优专用。
- **Cache heatmap**：可视化 Cache 热力图并展示对应指令信息，用于优化 L2 cache 命中率，板上调优专用。
- **Communication and computing pipeline chart (MC2 operators)**：可视化 MC2 算子的通信-计算执行过程与指令时延，专用于识别瓶颈，板上调优专用。
- **Instruction pipeline chart**：按指令维度展示时序关系并关联调用栈以快速定位瓶颈，仿真调优专用。
- **Operator code hot spot map**：展示算子源码与指令的映射及时延，帮助识别热点代码分布并分析热点函数优化的可行性，是**唯一同时支持 On-board 与 Simulation** 的服务功能。
- **Profile data files**：汇总多维度性能指标（指令时延、L2 命中率、内存/L0/UB 读/写带宽、计算/MTE 时延比、资源冲突比），板上调优专用，是数据展示的"基底层"。
- **Transfer bandwidth chart**：仅在 Simulation 调优下展示 GM↔L1、GM↔UB、GM↔others 之间的数据传输带宽。
- **Ctrl+C support**：DFX 类功能，在已采集数据基础上支持用户通过 Ctrl+C 提前终止算子进程并完成部分结果解析，**双调优均支持**。
- **Early process termination**：允许用户在预定时间结束算子进程，仅板上调优支持。
- **Specified simulator version**：允许用户直接指定模拟器版本，仅仿真调优支持。

### 表 2：Detailed features of the code hot spot map（代码热点图特性差异对比）

| Feature                                                                            | msOpProf      | msOpProf Simulator |
| ---------------------------------------------------------------------------------- | ------------- | ------------------ |
| Displaying the register usage (Gpr Count)                                          | Not supported | Supported          |
| Simulating the L2 cache hit ratio in the code line and instruction dimensions      | Supported     | Not supported      |
| Displaying the data transfer volume related to GM (Process Bytes)                  | Supported     | Supported          |
| Read and write conflicts of vector instructions on the UB Bank                     | Not supported | Supported          |
| Vector unit utilization                                                            | Not supported | Supported          |
| Displaying the time consumed by the operator source code and instructions (cycles) | Not supported | Supported          |
| Displaying the execution count of operator source code and instructions            | Supported     | Supported          |
| Displaying the mapping between the operator source code and instruction set        | Supported     | Supported          |
| Displaying source code, instruction program counter (PC) address, pipe, and source | Supported     | Supported          |
| Displaying core information                                                        | Not supported | Supported          |

**逐行解读**（msOpProf 与 msOpProf Simulator 互补/差异）：
- **Gpr Count（寄存器使用情况）**：仅 Simulator 支持，板上版本缺失。
- **L2 cache hit ratio（代码行/指令维度）**：仅 msOpProf（板上）支持——Simulator 不支持，意味着板上版的 Cache 分析能力反而更强。
- **GM Process Bytes**：两者均支持，为共有能力。
- **UB Bank 读写冲突**：仅 Simulator 支持。
- **Vector unit 利用率**：仅 Simulator 支持（板上缺失此维度）。
- **源码/指令耗时（cycles）**：仅 Simulator 支持，**板上版无法直接展示耗时**——这是显著的能力差异。
- **执行次数**：两者均支持。
- **源码↔指令集映射**：两者均支持。
- **源码 + 指令 PC + Pipe + Source 展示**：两者均支持。
- **Core 信息**：仅 Simulator 支持，板上版缺失。

**对比结论**：Simulator 版覆盖了**耗时、寄存器、向量单元利用率、UB Bank 冲突、核心信息**等更细粒度的指令级数据；而 msOpProf 板上版独占了 **L2 cache 命中率（代码行/指令维度）** 的能力。两者形成互补。

---

## 【公式解读】
原文无公式。

---

## 【关联】
- **与算子开发工具链（operator development toolchain）的关系**：算子调优组件是算子开发工具链中的关键组成部分，定位为算子开发者（客户算子开发工程师与内部算子开发工程师）获取性能数据与优化方向的主要工具。
- **上游/下游链路**：
  - **下游数据源**：算子执行环境（Ascend simulator 模拟器 / 真实 Ascend 设备）。
  - **下游产物**：8 项 Service function + 3 项 DFX function，覆盖热力图、Roofline、Pipeline、带宽、热点图、Profile 数据文件等可视化与分析能力。
- **与 Ascend 模拟器的关系**：指定模拟器版本（DFX function）以及指令 pipeline 图、传输带宽图均需依赖模拟器仿真。
- **与 MC2 算子的关系**：MC2 算子（通信-计算融合算子）拥有专属的"Communication and computing pipeline chart"。
- **与运行时（Runtime）的关系**：Profile 数据采集通过**劫持 runtime 接口**完成，表明本工具与算子运行时存在紧耦合拦截关系。
- **与芯片手册的关系**：PMU 数据采集顺序与传输接口解析（动态插桩 + 模拟器指令解析）必须**严格遵循芯片手册**，构成设计的强约束。
- **注**：原文标注"内部链接: (无)"，且第 3.2 节"Key Element Design"的表格内容在原文中被截断（仅显示表头"Key Element | Design Objective"无内容），故无法提供该表内的进一步模块关联信息。

---

## 【使用方法】
原文未涉及具体的启用方式、配置项或命令。
（原文仅说明"本文档目的是为算子开发工具设计模块、定义主数据结构与关键处理流程，作为编码阶段输入"，尚未进入 API/CLI 启动方式章节；相关具体命令需参考编码阶段或配套文档。）
```

## 图文联合解读

- `c0a326b0db9a4090093b24cb8172eb8c_559x304.png`: **图示解读：** UML组件图，Actor1（开发者）通过顶层组件 **msOpProf**（内含 Basic component）使用外部组件群，均为 <<Use>> 虚线依赖：右侧 hccl/msprof/adump（高层能力），下方 dcmi/runtime/ascend_cl/camodel/ascend_hal（运行时与硬件抽象）。

**技术结论：** msOpProf 采用**外观/委派模式**，自身不实现性能采集，而是汇聚调度昇腾栈中通信（hccl）、profile（msprof）、dump、设备管理、运行时、CL/Model/HAL 等子模块，对外屏蔽底层细节。

**与文档关系：** 图直接落实文档"**定义算子开发工具的模块组成**"这一设计目标，描绘"板上 profile"路径所依赖的完整组件拓扑，为编码与测试提供组件清单与依赖边界。
- `045770052e13e209fbd1c08d7f823b4f_796x564.png`: **图文联合解读：**

1）**图示内容**：UML组件图，外部Actor1通过<<Use>>调用绿色"Basic component"包内的msprof、adump、runtime三个接口与prof端口；包内Data collection组件依赖adump、runtime、Dynamic instrumentation（实现obiTask接口），并向上对接runtime、外部对接ascend-hal、向下对接bisheng。

2）**技术结论**：msopprof采用分层解耦架构——以prof端口为核心枢纽，Data collection向上对接runtime采集运行时数据，向下通过Dynamic instrumentation+obiTask插入到bisheng编译器插桩，外部通过ascend-hal获取硬件真实profile，体现"板级profiling"的端到端数据流。

3）**文档呼应**：图与文档"算子仿真与板上profiling"两类性能数据的来源论点对应，证实板上profiling的真实可靠性来源于runtime+hal+bisheng插桩的协同采集链路。
- `65735dda83950e7537ac39b9b5814ca6_676x330.png`: **图文联合解读：**

1) **图示内容**：UML组件图。核心组件「Data collection」居中，通过`prof`接口接收上游`Hijacking`接口输入，通过`Interface1`对接下游`Task management`组件；同时通过`context`、`Get`、`dbiTask`三个接口分别依赖`Operator context module`、`Config module`、`Dynamic instrumentation module`三个子模块。

2) **技术结论**：Data collection是枢纽级核心模块，采用"接口-实现"分离（Realization）与"使用"（Use）关系，实现采集层与上下层解耦，分层清晰、职责单一。

3) **与文档关系**：对应文档"算子调优组件需设计模块、定义主数据结构与关键流程"的设计目标，图为该架构的模块分解视图，支撑"模拟仿真+板端 profiling"两类数据流落地。
- `588feb02ee9770a998f2f3efa89053db_827x609.png`: **图文联合解读：**

图示为Profiler架构UML类图，以ProfDataCollect为核心，通过`DataCollect`抽象基类派生出`DataCollectInDevice`（板卡采集，含KernelReplay/Backup/Restore）与`DataCollectWithSimulator`（仿真采集）；ProfTask按芯片进一步细分为`ProfTaskOf310P`与`ProfTaskOf910B`。左侧Hijacked*接口及ProfInjectHelper体现"劫持注入式"采集机制。

该图论证了采集层与芯片/模式解耦的插件化设计：同一控制流通过不同实现分别支持实板与仿真两种profile场景，呼应文档"算子仿真与上板profiling两类性能数据"的双轨分类，为后续编码与测试提供模块边界依据。
- `a0d7778dc45c84bd7ea9ec128dc12c64_606x534.png`: **图文联合解读：**

**1) 图中内容：** UML组件图，展示"Parsing module"边界内含simulator paser、basic parser、On-board data parser三个组件，通过Parsing interface串联；左侧两个Execute接口分别触发模拟器与板上数据解析；右侧Visualization module通过"Provided interface1"被两个解析器以Usage依赖。

**2) 技术结论：** 系统采用"解析-可视化"分层架构，simulator与on-board两条解析路径共享基础解析器，并统一向可视化模块输出，体现模块解耦与接口复用。

**3) 与文档关系：** 图示印证文档所述算子性能数据的两大来源（仿真模拟与板上剖析），并通过模块化设计支撑其作为算子调优工具的职责划分。
- `8dd1dc24b25bf85bbcf95909f0596fe9_491x499.png`: **图文联合解读：**

图示Profiler组件架构：Tuning task模块通过RunDataParse/Execute接口，调度On-board与Simulation两条解析链路，统一汇聚至WriteBin（→可视化模块）和RunAllPlugins（→解析插件）。论证"模拟+在板"两类性能数据复用同一调度框架、并与插件化可视化解耦的结论，印证文档对算子调优工具模块化拆分与扩展性设计的目标。
- `8a89fbabc5733e1a7aac5a054dcb2020_951x890.png`: **1) 图中内容**：UML类图，分四层——顶层`DeviceDataParse`触发解析；核心`DataHandler`含`ParseDeviceData/Bin/L2CacheBin`等方法，抽象出`DataHandlerOf910B`与`DataHandlerOf310P`两个芯片特化实现，分别产出Ffts/Aicsq/AiCore/L2Cache/Hwts等Bean；中层`OpBasicInfo/BasicPmu/PmuCalculator`聚合性能特征；最终由`CacheLineHeatMap/MC2TimelineParser/StorageAccess`等汇聚至`DataVisualize`输出。

**2) 技术结论**：采用"解析-聚合-特征-可视化"分层架构，通过Realization模式适配910B/310P异构芯片，模块解耦、可扩展。

**3) 与文档关系**：契合文档"算子调优工具"模块化设计主张，为on-board profiling的多芯片数据采集与呈现提供结构基础。
- `3abb8bd5fbcd5ab405175535888d270a_865x509.png`: **图文联合解读：**

1）图示内容：以"单算子"为根，自顶向下分**Parse→Parse(带ThreadPool)→Visualize**三层主流程。Parse层含两个ThreadPool，分别调度DataCenter0/F的core/veccore解析与PCI代码生成；中段以PluginManager1（InstParse/CacheParse，处理ms/ppinfo/dma日志与Cache/Used汇总）、PluginManager2（ProcessBase/VectorUtil/UnConflict/GFLOPS&Register计算）、Pci2Code（解析PCI二代代码并Symbolize）三模块支撑"解析—计算—PCI分析"；末端Visualize经PluginManager1/2输出SplitCoreTimeLine、WholeCoreTimeLine与HotSpotMap。

2）技术结论：算子调优工具采用**并行解析+插件化解算+多视图可视化**的分层架构，实现"指令/Cache→指标→热视图"的完整数据流。

3）关联论点：呼应文档"为算子开发者提供仿真与上板性能数据"的定位，架构将日志解析、性能计算与可视化解耦，便于扩展分析维度。
- `d56db36d46d521390d256af71d135b82_714x738.png`: **图示内容：** UML类图展示MTE解析模块的四层结构——MteParser（含SetMtelog/Start/Stop）组合MtePlugin（含DataCenter_对象与Entry入口），DataCenter（dataStreamPtrMap_/dataTablePtrMap_）通过组合关系管理DataStream<T>模板类（std::queue<T>，支持Push/Pop/TryPop）。

**技术结论：** 解析器采用"入口插件→数据中心→流式队列"三层解耦架构，DataCenter作为注册中心管理多路数据流，实现数据采集与解析解耦。

**与文档关系：** 支撑"算子调优工具模块化设计"论点，定义了on-board profiling场景下的MTE日志解析、注册、缓存子模块的关键类与处理流程，为编码提供架构输入。
- `50769b9f211c0b12606cdfc20451937e_755x247.png`: **图文联合解读：**

1) **图示内容**：UML组件图，绿色包"Visualization module"内含Calculation module和On-board data visualization module，外部Parsing module通过两条虚线接口（<<Use>>）依赖：解析模块↔ToJson接口↔板内可视化模块↔Interface1接口↔计算模块，体现计算→可视化→解析的分层调用链。

2) **技术结论**：采用分层+接口隔离架构，三模块职责解耦，Parsing负责数据解析、Visualization负责呈现、Calculation负责运算，接口（ToJson、Interface1）保证扩展性与替换性。

3) **与文档关系**：该组件图对应文档中"On-board profiling"（板上真实性能剖析）的可视化子系统设计，印证文档"为算子开发者提供性能数据与优化方向"的工具链定位，是模块划分架构设计的具体落地。
- `aa18e26188739b739a336b9f02b81b93_741x620.png`: ## 图文联合解读

**1) 图中内容**
UML类图，展示了模拟数据可视化的插件架构：
- **PluginInterface**（顶层接口）：提供 `Run()` 方法
- **SimDataVisualizer**（抽象基类）：继承自 PluginInterface
- **HotSpotMapVisualizer**（核心插件）：继承 SimDataVisualizer，通过 `PluginErrorCode Entry()` 入口，内含 `MergeInfo` 数据结构
- **SimPcToCode / SimCodeToPc**（双向映射器）：分别实现 PC↔源码行号的正向/反向映射（标记为关键类©）
- **SimVisualizerConfig**（配置类）：被两个映射器共享，定义 chipType、输出路径等
- 红色■标注关键方法如 `CalCulate()`、`UpdateInstInfo()`

**2) 技术结论**
采用"插件接口 + 双向PC映射 + 统一配置"的分层设计，实现热力图可视化与指令级源码定位的解耦。

**3) 与文档关系**
对应文档概述中"模拟器输出 pipeline 图与代码热点图"的功能设计，是 on-board profiling 之外 simulation 路径的可视化模块架构落地。
- `42ce072b0176e22468f44988463b9602_634x732.png`: **图文联合解读：**

**图示内容：** UML类图，展示三层继承结构——`PluginInterface`（顶层接口，含`Run()`）→ `SimDataVisualizer`（中间抽象类，关联`SimVisualizerConfig`配置类，封装芯片型号、核名、输出路径等）→ `SubcoreTimelineVisualizer`（具体子类，提供事件/标志位/流水事件采集、用户标记解析、SepTrace生成、JSON输出等方法）。

**技术结论：** 采用**插件化+模板方法**架构，模拟数据可视化以插件形式注册，配置与渲染解耦，子核时间线分析为可扩展的具体实现。

**与文档关系：** 支撑文档"算子模拟"模块的设计——通过插件接口统一调度，由配置类驱动不同芯片的时序数据解析与可视化输出，落地"工具链模块化设计"论点。
- `0445179afe113aca20d9c881bb2e7971_599x563.png`: **图文联合解读：**

该UML类图展示了Simulator可视化子模块的架构：PluginInterface定义统一入口`Run()`，SimDataVisualizer实现该接口并依赖SimVisualizerConfig（封装芯片/核/输出路径配置），CoreTimelineVisualizer继承SimDataVisualizer并扩展流水时序采集与绘制方法（ParseByCore、CollectInstEvents/GetFlowEvents、WriteFile等）。

**论证结论：** 系统采用"接口—配置—子类实现"的可插拔分层架构，便于新增可视化类型。

**与文档关系：** 对应文档"算子仿真"场景，实现指令级仿真后流水线时序图等性能数据的呈现，支撑开发者获取优化方向。
- `edeab66075d8586d74141cb17b2c783e_440x245.png`: **图文联合解读：**

图示为UML组件图，含三个组件：Plugin module、msbit、Basic module。Plugin module通过MSBitAInit接口以<<Realization>>关系实现msbit；Basic module以<<Use>>依赖Plugin module，标注"Use the stub logic"。这论证了**分层解耦、插件可热替换**的技术结论：Basic模块通过桩逻辑调用插件，插件实现统一MSBitAInit接口对接msbit，呈现清晰的模块化分层。该设计呼应文档"算子调优工具面向Ascend算子开发者、支持功能模块独立演进"的架构目标，体现可扩展性与可维护性。
- `718f6c588384db46683f20bf40a856bb_496x374.png`: **图文联合解读：**

图示采用UML组件图，描绘「Plugin module」包内结构：含「Transfer stub interface」接口、由「Interface implementation」实现（Realization），后者依赖「Data recording」（Use）；包对外通过「MSBIInit」接口与「Basic component」相连。

**技术结论：** 插件模块采用"接口-实现-数据"分层解耦设计，stub接口隔离传输细节，实现层负责业务编排，数据记录独立为可替换子模块，便于扩展。

**与文档关系：** 体现调优工具链的模块化架构原则，即算子性能数据通过标准化接口采集与记录，支持模拟器仿真与板上profiling两种场景的灵活适配。
- `c1018e879215315155a838be67be24af_887x556.png`: **图文联合解读：**

1）图为UML类图，展示Task→InjectionEvent（注入事件，含Start/Stop/RegisterFunc）通过<<Usage>>依赖communication（异步消息队列）、packet（载荷Payload）、DataParser（MTE/Instr/ICache三类解析器）及DBIParser四大模块，模块间松耦合。

2）论证了**模块化解耦设计**：事件注入、跨进程通信、数据包封装、按数据类型分类解析（流水线/指令/缓存）、DBI硬件解析职责分离，消息通过SendMsgAsync异步队列传递。

3）与文档呼应：直接对应"算子调优组件的模块设计"论点——为模拟器指令级仿真（流水线图、热点图）与板端真实性能剖析提供可扩展、可替换的解析器架构基础。
- `f02a02a67847d793c2ca85ddeebd034b_971x438.png`: ## 图文联合解读

**1) 图中内容**：展示**Profiler二进制数据块的链式存储结构**。每个block由BlockHeader（Record count/offset/set_nd_para配置，uint64）+ RecordHeader + 三条Record(type+record1/2/3) + 512B padding组成。共100个block通过右侧箭头**顺序串联**。

**2) 技术结论**：论证了Profiling数据采用**定长块+链式索引**的二进制布局——块头记录条目数和偏移量以实现随机访问，padding保证块大小对齐便于内存映射/顺序读写。

**3) 与文档关系**：支撑文档"算子调优工具需输出详细性能数据"的设计目标，该结构是为板上Profiling（on-board profiling）功能服务的底层数据组织方案，定义了性能数据的物理存储格式。
- `cf1aff15b08bb3fe4b7634e5202de28e_606x467.png`: ## 图文联合解读

**1) 图中内容**：展示了一种**自描述型二进制数据块格式**。每块由12字节固定头部（内容长度8B+类型1B+零填充长度1B+保留2B，需4字节对齐）和可变长内容组成，按块序列排列（Data block … n）。

**2) 技术结论**：该格式采用"长度+类型"自描述设计，支持零填充对齐与未知字段预留，具备良好的可扩展性与类型可识别性，适合存储结构化的profiling原始数据流。

**3) 与文档关系**：对应文档中"算子仿真"与"板上profiling"两类性能数据的底层bin文件存储结构，是Operator Tuning组件持久化指令级模拟结果与真实硬件性能数据的格式定义基础。
- `e798b43938a390ec8513f21c4c077819_639x840.png`: **1) 图示内容**：流程图展示寄存器占用统计算法。先取当前指令寄存器，区分DST/SRC；判断DST是否在SRC中，是则占用计数+1；否则查询历史占用映射表，更新历史指令数据；将新DST加入历史占用集；遍历至末条指令后，将全部历史占用寄存器作为DST重复算法，要求时间复杂度<O(n)。

**2) 技术结论**：通过DST与SRC、历史占用的双重判别去重，将寄存器活跃性分析的复杂度控制在亚O(n²)，避免指令数增长导致性能爆炸。

**3) 与文档关系**：对应"算子仿真"指令级模拟环节中的寄存器占用分析模块，为流水线图、热点图等性能数据提供底层寄存器活跃性统计支撑。
- `1a12bc5385fc2d2751bf3684dc8ef711_606x314.png`: **图文解读：**

1) **图示内容**：左侧灰色框为标准 `aclnn dynamic` 调用链（Register→Malloc→Launch→Free→UnRegister），右侧蓝色虚线框为 msOpProf 通过 "Hijack" 劫持机制，将每个RT接口分别重定向至带 profiling 能力的实现函数（算子信息记录、内存备份、性能数据采集、内存释放）。

2) **技术结论**：msOpProf 采用**非侵入式运行时API劫持**方案，在不修改用户算子代码的前提下，于 RT 层透明插入采集逻辑，实现真实板卡上的 profile 数据获取。

3) **与文档关系**：图示论证了文档所述"on-board profiling 反映真实硬件性能"的实现路径——通过劫持四个关键RT调用完成全生命周期数据采集，是"模拟与上板两种性能数据"分类中"上板"路径的具体落地设计。
- `428ea3fa9e3357494c0695c49c79c5e5_756x348.png`: 1) 图为UML时序图，描绘四个对象（User process、Runtime interface、ProfDataCollect、DataCollectWithSimulator）的交互：用户初始化后调用rtSregister→SaveObj→记录对象信息；再调用rtKernelLaunch，创建ProfDataCollect、请求输出路径、ProfInit、moveObjToOutPutPath，最后由Runtime执行并调用ProfData。

2) 论证了"算子模拟"模式的数据采集闭环：Runtime拦截kernel调用，ProfDataCollect负责对象登记与持久化，DataCollectWithSimulator作为模拟器后端完成对象归档。

3) 对应文档"Operator simulation"章节，佐证了模拟器路径通过Runtime插桩+独立采集服务生成性能数据的设计论点。
- `33e097268e3e2fec3e00bf7d3f11943b_802x293.png`: **图文联合解读：**

**图示内容：** 左侧GM（全局内存）含"data"与"backup"两块，由"Input backup"箭头连接。三级流水线串联，每级含蓝色"data"、绿色"kernel"、蓝色"backup"。data→kernel为"Execution"；前级backup→后级data为"Restoration"；同级data与backup之间以虚线贯穿保持流式传递。

**技术结论：** 该图为算子级流水线数据流示意图，论证了"数据-备份双轨并行"机制——kernel执行读取data，同时backup预存快照；若当前kernel出错，可通过前级backup逐级回溯（Restoration），实现fail-safe容错恢复。

**与文档关系：** 对应文档§1中"板上profiling采集真实硬件执行数据"的设计诉求，阐释on-board profiling如何在真实Ascend设备上通过备份-恢复机制保障性能数据采集的完整性与可重放性，是算子调优组件可靠性的关键保障。
- `cee27f22cc2250ad3a5581dd027d64ec_705x586.png`: 1) **图示内容**：UML时序图，五个对象（msOpProf、AscendCL、Basic module、mstx、User operator）的纵向生命线。流程为：User operator调用mstxRangeStartA→Basic module调用aclmdlIRICaptureBegin；进入loop3，执行aclmdlIRIExecuteAsync与Data saving循环；mstxRangeEnd→aclmdlIRICaptureEnd→aclmdlIRIDestroy→Destruct and exit；最后msOpProf Parse the operator。

2) **技术结论**：板上Profiling采用"用户打桩+mstx转发+AscendCL IRI接口采集+离线解析"分层架构；用户算子通过mstx范围标签界定采集区间，Basic module桥接运行时IRT采集，loop3体现多次执行异步采样，msOpProf负责事后解析。

3) **与论点关系**：对应文档Overview中"On-board profiling：算子在真实Ascend设备上运行的性能数据"，图示论证了该路径的关键处理流程与模块职责划分。
- `1f3babf8f320f45808062c10f4829f0c_676x393.png`: ## 图文联合解读

**1) 图中内容**：左侧灰色框为 `acinn dynamic` 中的运行时RT API调用流（Start→rtRegisterAllKernel→rtSetDevice→rtGetDeviceCount→rtGetDeviceInfo→rtGetSocVersion→rtKernelLaunchWithHandle→rtDevBinaryUnRegister→End）；右侧虚线框 `msOpProf (on-board)` 通过"Hijack"箭头对每个RT API注入对应实现（.o信息记录、模拟器适配、正确信息返回、SoC版本替换、性能数据采集）。

**2) 技术结论**：板载Profiler采用**API劫持（Hook）机制**，无需修改acnn源码即可透明接管RT调用，实现二进制加载、设备管理、版本伪装和性能采集五大功能。

**3) 与文档关系**：印证第1节"on-board profiling（板载真实性能数据采集）"的设计思想——通过劫持RT层而非侵入算子，支撑"可靠反映硬件真实性能"的论点。
- `4f2aa7604d013cd8200e9d3dec0e0cb3_554x139.png`: ## 图文联合解读

**1) 图中内容**：四个蓝色方框表示昇腾运行时库的调用链——`libascend.so`（aclrt）→ `injection.so`（aclrtImpl）→ `libascend_impl.so`（aclrtImpl）→ `libruntime_camodel.so`（rts）。箭头标注三种关系：aclrt→aclrtImpl 为"依赖顺序调整"，两 aclrtImpl 之间为"dlopen 动态加载并调用"，最后为普通"call"调用。

**2) 技术结论**：算子调优工具通过 **依赖顺序修改 + 动态库注入（injection.so）** 的方式，将自身插入用户态 API 与底层实现库之间，从而拦截 aclrt 调用并附加 profiling 逻辑，实现无侵入式的算子性能数据采集。

**3) 与文档关系**：该图直接支撑文档关于"板上 profiling 反映真实硬件性能"的论点——说明采集通路嵌于 aclrt↔rts 真实调用链中，确保采集到的是硬件真实执行数据，而非仿真结果。
- `bde468e9c0c6b148a76c2a4dba5f4957_590x188.png`: **1) 图示内容：** 两行蓝色方块分别表示连续算子序列（Operator 1 → Target operator → Operator 3 → Operator 4）的两次执行；绿色胶囊框标注"Parse profile data of the target operator"，在两次执行后各出现一次；中间箭头"Modification"指向 Target operator，底部时间轴标注"times"表示循环往复。

**2) 技术结论：** 板载 profiling 采用"执行→解析目标算子 profile→修改→再执行"的迭代循环流程，多轮重复以逐步逼近性能最优。

**3) 与文档关系：** 对应文档"on-board profiling"获取真实硬件性能数据的环节，体现该工具通过解析目标算子 profile 数据定位瓶颈、辅助开发者进行修改与优化的核心理念。
- `c05e7daabb8ce6bfefaf9d7f981b3510_616x909.png`: **图文联合解读：**

1) 图示：UML时序图，三条泳道（msOpProf / Basic component / Simulator），展示算子启动→仿真器注册→执行目标算子A→Loop1数据迁移与处理→完成通知→解析→执行算子B→Loop1→退出流程，含"生成可视化文件""等待解析"等关键标注。

2) 论证：msOpProf通过Basic component中转，按"传输-处理-通知"循环采集数据，目标算子全程插桩、非目标算子跳过，体现分层解耦与目标选择性剖析。

3) 与文档关系：对应"算子仿真"场景（涉及Simulator），呈现指令级模拟下性能数据的采集闭环，为文档中"流水线图/代码热点图"等可视化输出提供执行流程依据。
- `0a88cded14362a8b1296f411041af697_281x511.png`: 图示为算子仿真/在板剖析任务的控制流图：start → DBlTaskConfig::Init → RunDBlTask判定 → InitMemory判定（任一失败则End）→ ExpandArgs → KernelLaunch+Synchronize → WriteMemInfo。

技术结论：算子性能采集流程遵循"配置→条件守卫→参数展开→核函数执行同步→内存信息落盘"的顺序固化流程，异常分支直接终止。

与文档关系：直接对应第1章论及的"算子模拟与在板剖析两类性能数据采集"中的核心处理管线，定义了调优组件的标准化执行骨架。
- `c6dde60847f0fc6d376b5c21cbda745e_471x370.png`: **图文联合解读：**

1) **图示内容**：这是一张UML时序图，含三条泳道——`kernelLaunch`（内核启动）、`DBITask`（动态二进制插桩任务）、`ProfDataCollectt`（性能数据采集）。数据流依次为：插入BBCount桩→kernelLaunch同步→向ProfDataCollectt记录信息→refreshParam→插入自定义桩→再次kernelLaunch同步→再次记录信息。

2) **技术结论**：on-board profiling通过DBI机制实现非侵入式插桩（BBCount+自定义桩），利用二次kernelLaunch前后分别记录baseline与优化后数据，从而对比出算子真实性能差异；ProfDataCollectt作为统一汇聚点保证数据完整性。

3) **与文档关系**：图示具体实现了文档所述"板上profiling"与"operator tuning"流程，是"算子开发工具模块设计、关键处理流程"在profile阶段的实例化呈现。
- `ee49ee40ab6421501678387083daf5bd_1010x619.png`: **图文联合解读：**

图示UML时序：Actor编译带标记参数MC2算子后启动，工具经基础组件劫持MsprofRegisterCallback与MsprofReportAdditionalInfo接口，重放算子同步捕获通信、AI CPU、AI Core三条流水线，落盘后回传分析结果。

论证：通过劫持Profiling API并算子重放，可非侵入地获取完整硬件流水线数据。

关系：图解文档"板上剖析反映最真实性能"的技术实现路径，支撑调优工具作为算子开发者获取性能数据主工具的论点。
- `97bc6c3118b9d9963b644bf344bc47a9_1190x591.png`: **图文联合解读：**

1. **图中内容**：UML时序图，展示算子调优工具与三个模块（数据抽取、计算、可视化）间的交互流程。工具下发"单kernel单次调用的原始调优数据"，抽取模块解析为指令数据结构；计算模块依UB地址分析bank conflict、写入InstrParseInfo，封装为可视化数据结构；可视化模块存储数据后回传"分析完成"消息。

2. **技术结论**：采用三段式流水线架构（抽取→计算→可视化），按"单kernel单次调用"粒度分析，模块解耦、数据结构分级传递，bank conflict是基于UB地址的关键分析点。

3. **与文档关系**：印证文档所述"算子调优是获取性能数据与优化方向的核心工具"，通过分层模块化设计支撑指令级模拟与上板profiling两类性能数据的产出。
- `4d3d83b9ba3452f568ca875a6fba0f22_600x543.png`: 1) 图含Actor、调优工具、基础组件三条UML时序线：用户发起MC2算子程序启动→工具下发执行参数至基础组件→基础组件回传数据保存→进入"Multi-card parsing"交互框，依次完成基本/可视化数据分析、通信与计算流水线分析、visualize_data.bin增强与pipeline/trace保存→工具返回分析结果给用户。

2) 论证：调优工具作为用户与基础组件的中介承担参数下发与结果回收，"多卡解析"是板上调测的核心处理阶段，承载多卡场景下的数据聚合与可视化增强。

3) 与文档对应：落实文档"算子调优是算子开发工具链核心组件"的定位，具体化"板上调测"的数据采集—解析—可视化闭环流程。
- `3cb0ff74e5f415ca79f81475417e9b8c_549x424.png`: **图文联合解读：**

1) **图示内容**：UML时序图，包含msop启动、DataCenter、MtePlugin、MteParser、InjectEvent五条生命周期线。流程为：构造Parser/datacenter/Plugin→Start→loop2循环（Run采集→SetMteLog→Push→trigger→数据处理）→Stop→关闭插件→Shutdown→后处理(merge、可视化)。

2) **技术结论**：采用事件驱动+采集循环架构，MteParser作为调度中枢，DataCenter负责数据汇聚，InjectEvent负责事件注入，核心数据采集通过loop2循环持续运行，体现"插件化、按需触发、循环采集"的设计模式。

3) **与文档关系**：图示对应文档所述算子调优工具的板端profiling实现，展示了从启动、数据采集到后处理可视化的完整闭环，是文档"模块设计"与"关键处理流程"论点的具体可视化支撑。
- `c25a835f49bbef90ca85052b158dcc94_543x598.png`: **图文联合解读：**

图示为"模拟调优时序图"，描绘用户向算子调优工具导出dump数据，经校验后进入**多卡解析循环**：逐核解析指令/缓存信息→每核datacenter暂存→计算gpr/ubread等指令数据→合并各核datacenter→生成流水线图与热力图→落盘，最终回传用户。论证了**仿真调优采用"解析→计算→可视化"三阶段流水线**，且通过per-core datacenter与插件式计算实现并行扩展。该图为文档第1节"算子仿真"分支（运行于模拟器，产出流水线图与代码热点图）的架构具象化，展示了从原始数据到可视化产物的完整处理流程。
- `949ac9f03680c24e723b9c6db7daf0cd_710x346.png`: **图示解读：**

1) **结构/数据流**：左侧"process"容器内含device0、device1两个设备，每设备各有两个launch。右侧为四个独立模块——ProfConfig、MemoryContext、KerneContext、DataCollect。device0的launch分别连线至MemoryContext、KerneContext；device1的launch1连线至DataCollect；device整体连线至ProfConfig。

2) **技术结论**：算子调优工具采用"进程—设备—launch"三级分层架构，配置管理（ProfConfig）、上下文（Memory/KerneContext）与数据采集（DataCollect）模块并行解耦，支持多设备多launch的并发性能剖析。

3) **与文档关系**：呼应文档第1节"模块设计、数据结构与关键处理流程"的设计目标，为模拟器仿真与板端profiling两条性能数据采集路径提供模块划分与依赖关系的实现依据。
- `c8f24f9a8445ecaa4bf74839170d83a0_1105x705.png`: **图文联合解读：**

图示`Data`模块的函数调用树：入口获取`relocObjectPath`与`.o`路径后，调用`ParseMergedDumpData`，按`socVersion`分支，依次执行`ParseDumpByCore`（含startPc/instrPopped/instr/Icache四类Dump解析）、`MergeDumpInfo`、`GetPc2code`、序列化Trace（输出JSON流水线图）和SerializeStatistic（PC/code/Core统计）。绿色框为函数节点，红色数字标注调用次数。

**论证结论：** Profiler数据处理采用"分层解析→合并→序列化"的模块化管道架构，dump按Core维度拆分解析后合并，最终通过JSON序列化输出流水线图与统计数据。

**与文档关系：** 呼应文档"定义主要数据结构与关键处理流程"的目标，Data模块即on-board profiling原始数据的标准化处理入口，是后续可视化与调优的数据底座。
