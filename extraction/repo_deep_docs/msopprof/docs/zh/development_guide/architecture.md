# MindStudio Ops Profiler 架构设计说明书

> 仓 `msopprof` · 路径 `docs/zh/development_guide/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msopprof/docs/zh/development_guide/architecture.md

# 一体化深度解读: msopprof 架构设计说明书

---

## 【定位】

**一句话**: 这篇文档是「MindStudio Ops Profiler (msopprof)」算子调优组件的架构设计说明书,面向昇腾算子开发人员,目的是对算子开发工具进行模块设计,明确主要数据结构和主要处理过程,为后续编码和测试提供指导输入。

---

## 【技术要点】

1. **两类性能数据划分**:算子性能数据分为"算子仿真"(昇腾仿真器,指令级仿真,输出流水图与代码热点图)和"算子上板"(真实昇腾设备,反映硬件真实性能)两类。

2. **四大劫持接口**:基础组件通过劫持 `runtime`、`ascendcl_impl`、`adump`、`msprof` 四个接口实现性能数据采集与上下文获取;其中 `runtime` 与 `aclrt` 两种启动方式当前并存,`rt` 接口下线后可删除对 `runtime` 的劫持。

3. **动态插桩机制**:借助 **bisheng 编译器** 的能力,在算子运行时动态替换 `.o` 文件,实现自定义桩、BBCount 桩等打桩能力。

4. **采集方式分场景**:
   - **上板调优**:从硬件接口采集,通过 `KernelReplay` 进行重放,并使用 `ProTask` 开启通道采集数据(不同芯片对应不同类)。
   - **仿真调优**:利用仿真器直接获取性能数据,生成后存储到指定算子目录下。
   - **MC2 算子**:通过劫持 `msprof` 获取打点信息以展示通算流水图。

5. **解析架构演进**:原有结构上板解析与仿真解析独立,当前版本将两端共用能力(如算子代码行映射 `pc2code` 功能)抽离至「基础解析类」,后续数据量展示等相关类都不局限于仿真或上板。

6. **整体设计目标**:包括性能数据准确性(严格按芯片手册解析 PMU 采集顺序与搬运类接口)、易扩展性(采集/解析/新增交付件/算子接入四方面)、多算子调用/多进程/多卡并行支持、采集阶段减少落盘改通信传输、解析阶段多线程并行处理等。

---

## 【关键机制与数据】

**工作原理(采集路径)**:
- 用户算子启动 → 调用被劫持接口 → 基础组件劫持逻辑触发 → 创建 `Hijackedxxx` 对象 → 主动调用 `ProfInit` 与 `ProfData` → 根据场景路由到 `KernelReplay`(上板)或 `SaveBasicInfo`/`HandleDumpLogAfterLaunch`(其他路径)→ 启动相应采集 `Task`(FftsTask / StarsTask / AiCoreTask) → 由 `ProTask` 开通道采集。

**打桩接口分工**(原文):
- `runtime` 接口:运行时相关;
- `msprof` 接口:用于获取 MC2 算子的打点信息以展示流水图;
- `adump` 接口:用于获取算子输入信息(如 workspace 长度)。

**性能数据指标**(原文):展示指令耗时情况、L2cache 命中率、内存带宽读写速率、L0 读写带宽率、UB 读写带宽速率、算子基础信息、计算/搬运单元耗时占比、资源冲突占比;搬运带宽图覆盖 `GM<->L1`、`GM<->UB`、`GM<->other` 三类数据搬运。

**关于具体性能数字**:原文未给出具体性能数据(如带宽数值、命中率阈值等)。

---

## 【表格解读】

### 表 1:第 2 节 功能清单(业务/dfx 全部条目)

| 类型 | 功能清单 | 功能描述 | 支撑的调优类型 |
| --- | --- | --- | --- |
| 业务功能 | 计算内存热力图 | 以资源维度展示算子基础信息、计算负载分析和内存负载分析的数据 | 上板调优 |
| 业务功能 | Roofline 瓶颈分析图 | 构建出性能模型,然后利用该性能模型快速评估出算子的理论性能极限 | 上板调优 |
| 业务功能 | Cache 热力图 | 可视化呈现 Cache 热力图,可显示对应指令信息,以便用户优化 L2Cache 命中率 | 上板调优 |
| 业务功能 | 通算流水图(MC2 算子) | 直观看到 MC2 算子的通算运行情况、指令耗时等信息,协助开发者识别通算瓶颈 | 上板调优 |
| 业务功能 | 指令流水图 | 以指令维度展示时序关系并关联调用栈快速追踪瓶颈位置 | 仿真调优 |
| 业务功能 | 算子代码热点图 | 支持查看算子源码与指令集的映射关系、耗时情况等功能,可协助开发者识别热点代码分布,并分析热点函数优化的可行性 | 上板调优/仿真调优 |
| 业务功能 | 性能数据文件 | 展示指令耗时情况、L2cache 命中率、内存带宽读写速率、L0 读写带宽率、UB 读写带宽速率、算子基础信息、计算/搬运单元耗时占比、资源冲突占比 | 上板调优 |
| 业务功能 | 搬运带宽图 | 展示 GM<->L1,GM<->UB,GM<->other 间数据搬运的带宽图 | 仿真调优 |
| dfx 功能 | Ctrl+C 功能 | 提前终止算子进程,工具可根据当前已采集的数据解析结果 | 上板调优/仿真调优 |
| dfx 功能 | 提前终止进程 | 用户可定时结束算子进程 | 上板调优 |
| dfx 功能 | 指定仿真器版本 | 用户可直接设置仿真器版本 | 仿真调优 |

**逐行解读**:
- 8 项业务功能 + 3 项 dfx 功能,共 11 条;其中 1 项跨模式共享(算子代码热点图)、1 项跨模式共享(Ctrl+C),其余业务功能明确锁定单一调优模式。
- 上板调优功能以"性能数据指标型"(Roofline、Cache 热力、内存热力、性能数据文件)和"瓶颈识别"(通算流水 MC2)为主;仿真调优功能以"指令级视角"(指令流水图、搬运带宽图)为主——这反映了两种调优模式的根本差异:上板看真实设备吞吐/命中率,仿真看指令级时序与数据搬运。
- dfx 三项聚焦"可中断性"与"环境配置灵活性",仿真专属项为「指定仿真器版本」。

### 表 2:第 2 节 代码热点图详细功能(msopprof vs msopprof simulator)

| 特性名称 | msopprof | msopprof simulator |
| --- | --- | --- |
| 查看寄存器使用情况(Gpr Count) | 不支持 | 支持 |
| 模拟代码行和指令维度的 L2Cache 命中率 | 支持 | 不支持 |
| 查看与 GM 有关的数据搬运量(Process Bytes) | 支持 | 支持 |
| Vector 计算类指令在 UB Bank 上读和写的冲突情况 | 不支持 | 支持 |
| Vector 计算单元利用率 | 不支持 | 支持 |
| 查看算子源码与指令的耗时情况(cycles) | 不支持 | 支持 |
| 查看算子源码与指令的执行次数 | 支持 | 支持 |
| 查看算子源码与指令集的映射关系 | 支持 | 支持 |
| 查看源码、指令 PC 地址、Pipe、Source | 支持 | 支持 |
| 查看 core 信息 | 不支持 | 支持 |

**逐行解读**:
- 共 10 条特性对比,2 项为两端共有(Process Bytes、执行次数),6 项仅 simulator 支持(Gpr Count、UB Bank 冲突、Vector 利用率、cycles、core 信息等),2 项仅 msopprof 支持(L2Cache 命中率)。
- **互补关系**:msopprof(实板)擅长"命中率"统计与基础映射关系展示;simulator 擅长"细粒度耗时、向量单元利用率、冲突分析"——二者结合形成完整调优能力。
- msopprof simulator 在 Vector 流水线微观分析层完全领先,在寄存器与 bank 冲突分析层独占,这是因为仿真器能拿到指令级 retire 数据,板上采集则受限。

### 表 3:第 3.2 节 关键要素设计目标

| 关键要素 | 设计目标 |
| --- | --- |
| 实现模型 | 1. 性能数据准确性:PMU 数据采集顺序、搬运类接口(动态插桩和仿真器指令解析)解析的准确性,同时需要严格按照芯片手册解析<br/>2. 解析、采集易于扩展:解析、采集模块需要做合适的抽象,保证以后功能的扩展和芯片信号的扩展 |
| 交互模型 | 工具侧需要正确地将用户输入的参数传输给基础组件侧,实现相应的采集功能。 |
| 并发模型 | 解析高并发:实现解析并行处理。 |

**逐行解读**:
- 实现模型强调「准确性(对照芯片手册)」与「可扩展性(模块抽象)」两条主线,与 §3.1 的整体目标对应。
- 交互模型仅从"参数传输"角度描述工具侧↔基础组件侧链路,未涉及 UI 层。
- 并发模型只覆盖解析侧,采集侧的并发策略在原文未单独列出(仅在 §3.1 提"多线程并行解析")。

### 表 4:第 4.1.1.3 节 采集模块软件单元清单

| 软件单元 | 描述 | 外部接口 | 内部接口 | 关系描述 |
| --- | --- | --- | --- | --- |
| 劫持 | 包括 runtime\adump\msprof 接口 | 相应组件接口 | Hijackedxxx | 对外暴露相应组件接口,当调用该接口时会创造 Hijackedxxx 对象进行劫持逻辑。 |
| 数据采集 | 串联所有数据采集的逻辑包括上板的重放、仿真的采集 | ProfInit\ProfData | KernelReplay\SaveBasicInfo\HandleDumpLogAfterLaunch | 进入劫持后会主动调用 profInit,ProfData,不同的场景会调用内部不同的逻辑,例如上板会调用 KernelReplay 函数 |
| 算子上下文模块 | 记录算子的上下文,.o 信息 | Save, ParseMetaDataFromBinary | GetMetaSection、ParseKernelArgs | 算子运行时会记录、分析算子上下文,在全部记录完成时可以调用 Save 函数保存上下文 |
| config 模块 | 记录由工具侧传来的配置信息 | Get/Set |  | 会记录由工具侧传来的配置信息,运行时会调用获取该信息选择性采集性能数据 |
| task 管理 | 创建、控制上板采集 task | Start、Stop | FftsTask, StarsTask, AiCoreTask | 采集模块会根据当前不同的场景机器启动、停止相应的 task |
| 动态插桩模块 | 控制动态插桩流程的模块,包括自定义桩、BBCount 桩 | RunDBITask | GetOrCreate, Run | 首先外部调用 RunDBITask 函数,该函数中会根据类型建立相应对象,之后会调用 Run 接口与编译器交互,进行 .o 替换 |

**逐行解读**:
- 6 大软件单元构成采集侧的全部能力:`劫持`(入口)→`config`(配置源)→`数据采集`(主线)→`算子上下文`/`task 管理`(`数据采集`的左右翼) →`动态插桩`(独立能力)。
- `数据采集`单元是枢纽,上板路由到 `KernelReplay`(对应 `ProTask` 开通道),仿真路由到 `SaveBasicInfo` 等路径;这印证 §4.1.1.2 的两类采集分支描述。
- `task 管理`内部三类子任务 `FftsTask/StarsTask/AiCoreTask`,暗示采集覆盖多类硬件单元(原文未拆细,推测对应不同硬件 IP 块)。
- `动态插桩模块`与 bisheng 编译器耦合,通过 `Run` 触发 `.o` 替换——这是性能数据补充来源(原文 §4.1.1.2 第 3 条)。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档为架构视角,其内部模块、特性间存在如下依赖与互补关系(基于原文表述):

1. **采集 → 解析 数据下游**:§4.1.2.1 明确"单个算子数据按照用户指定目录划分文件夹写入磁盘","从计算内存热力图、Roofline、指令流水图、代码热点图、性能数据文件等不同指标维度计算并呈现交付件"——即采集侧产出原始数据(Roofline 模型、PMU 原始数据、代码行映射关系等中间数据),由解析侧按指标维度加工为功能清单(表 1)中的 8 个业务交付件。
2. **代码热点图的"两端共用"耦合**:表 2 中"msopprof simulator + msopprof"功能差异,正是 §4.1.2.2 提到的「基础解析类」要独立化的来源——`pc2code`(源码-指令映射)、L2Cache 命中率、Process Bytes 等在两种模式都用到,所以抽出公共基类。
3. **MC2 算子专属链路**:功能清单中的「通算流水图(MC2 算子)」依赖 §4.1.1.2 中劫持 `msprof` 获取打点信息,这是 MC2 通算场景专有通路(与普通算子的采集-解析链不同)。
4. **dfx 与主流程的耦合**:`Ctrl+C` 与「提前终止进程」均属于 §4.1.1.3 `task 管理` 的 `Stop` 接口能力面,允许用户在采集未完成时基于已采集数据解析结果;原文明确"工具可根据当前已采集的数据解析结果",印证此能力与解析侧的协作关系。
5. **芯片差异扩展点**:§4.1.1.4 第 5 条指出 `ProTask`「不同芯片对应不同类」;§3.2 实现模型也要求"解析、采集模块需要做合适的抽象,保证以后功能的扩展和芯片信号的扩展"——这两处呼应提示:同一业务功能在不同昇腾芯片上由不同 `ProTask` 子类承载。
6. **关于文末内部链接信息**:题目提供的「内部链接: (无)」,即原文档在本次输入中未提供可点击的章节/特性锚点链接。

---

## 【使用方法】

原文未涉及具体启用方式、配置项或命令。文档定位为架构设计说明书,仅从模块、数据结构、处理过程层面定义组件设计,不直接给出 CLI/SDK 调用样例。如需获取具体命令用法或配置项,需另行查阅 msopprof 仓内其他文档(如用户指南、安装/部署文档等)。

## 图文联合解读

- `c0a326b0db9a4090093b24cb8172eb8c_559x304.png`: 1) 图示为UML组件图：Actor1通过<<Use>>调用msOpProf（含Basic component子模块），后者经<<Use>>依赖hccl、msprof、adump、dcmi、runtime、ascend_cl、camodel、ascend_hal等八个外部组件。

2) 论证了msopProf采用"高内聚-低耦合"模块化设计，通过单一Basic component聚合调用底层硬件/运行时接口。

3) 与文档呼应：作为算子调优组件架构总览，可视化呈现"算子上板/仿真"调优能力（如Roofline、Cache热力图）所依赖的底层支撑组件体系。
- `045770052e13e209fbd1c08d7f823b4f_796x564.png`: **1) 图中内容**：UML组件图。Actor1（用户）通过 `<<Use>>` 调用 `msprof` 与 `adump` 两个接口；中央节点 `prof` 向上提供 `Basic component` 子系统（含 `msprof`、`adump`、`runtime` 接口以及 `Data collection`、`Dynamic instrumentation` 两个组件），向下以 `<<Realization>>` 实现 `JobTask` 接口；`Data collection` `<<Use>>` 外部组件 `ascend_hal`（硬件抽象层），`Dynamic instrumentation` `<<Use>>` 外部组件 `bisheng`（毕昇编译器），共同再经 `prof` 回连用户。

**2) 技术结论**：Profiler 采用分层架构——用户通过统一接口接入，数据采集与动态插桩解耦，硬件层（ascend_hal）与编译器层（bisheng）作为外部依赖，便于扩展仿真与上板两类调优路径。

**3) 与文档关系**：印证文档"算子仿真/算子上板"双路径划分，以及面向算子开发者的模块化工具链设计目标。
- `65735dda83950e7537ac39b9b5814ca6_676x330.png`: **图示解读：**

1）**结构与数据流**：UML组件图展示分层架构——上层"Hijacking"接口通过"prof"接口接入"Data collection"组件，后者经"Interface1"连接"Task management"；下层三个模块（Operator context module、Config module、Dynamic instrumentation module）分别实现context、Get、dbiTask接口，被Data collection以Use方式调用。

2）**技术结论**：Data collection是核心枢纽，采用接口解耦设计，统一对接劫持、任务调度与三大数据采集模块，实现采集层与业务层的关注点分离。

3）**与文档关系**：印证文档所述"算子上板/仿真性能数据采集"模块化设计理念，支撑功能清单中Roofline、Cache热力图等调优业务的数据来源闭环。
- `588feb02ee9770a998f2f3efa89053db_827x609.png`: **1) 图示内容**：Profiler UML类图，分四层：劫持接口层（HijackedrtRegister/HijackedKernelLaunch/HijackedFuncOfMsprof/HijackedFuncOfAddumpGetDFXInfoAddrForDynamic），由ProfInjectHelper驱动；数据汇集层（ProfDataCollect：ProfData/PostProcess/SaveObject）；采集抽象层（DataCollect派生DataCollectInDevice与DataCollectWithSimulator两个子类）；任务执行层（ProfTask派生ProfTaskOf310P与ProfTaskOf910B），辅以KernelContext、MemoryContext、DBITask、ProfConfig等上下文与配置类。

**2) 技术结论**：①"上板"与"仿真"两条调优路径共享同一采集抽象，通过子类化实现差异化，统一"采集-后处理-落盘"流程；②ProfInjectHelper经劫持接口完成无侵入式数据注入；③多芯片平台通过继承ProfTask解耦，便于硬件扩展。

**3) 与文档对应**：DataCollect两子类直接对应文档§1所述"算子仿真"与"算子上板"两类性能数据的采集分工，支撑功能清单中的上板调优项。
- `a0d7778dc45c84bd7ea9ec128dc12c64_606x534.png`: **1) 图示内容：** UML组件图，边界"Parsing module"内含三个组件——`simulator paser`、`basic parser`、`On-board data parser`，三者通过"Parsing interface"装配连接；各组件均向外提供`Execute`接口；`Visualization module`通过"Provided interface1"被前两者以`<<Usage>>`虚线依赖。

**2) 技术结论：** 系统采用"解析与可视化解耦"的分层架构，解析模块按数据源分仿真/上板两条路径，并共享基础解析器，统一封装后供可视化层消费，体现接口标准化与职责单一。

**3) 与文档关系：** 印证文档"算子仿真"与"算子上板"两类性能数据的并行处理设计，组件图即功能清单中"上板调优"（Roofline、Cache热力图等）的底层模块映射。
- `8dd1dc24b25bf85bbcf95909f0596fe9_491x499.png`: **1) 图中内容**：UML组件图，含`ProfilingRun`接口、`Tuning task module`组件；核心为并行的`On-board data parsing module`与`Simulation data parsing module`，二者均实现`Execute`接口，并分别通过`WriteBin`接口对接`Data visualization module`、通过`RunAllPlugins`接口对接`Parsing plugin module`。

**2) 技术结论**：算子调优组件采用"任务调度—双路径解析—下游扩展"的分层架构；上板与仿真解析路径对称并行、互不耦合，解析结果统一汇聚至可视化和插件层，具备良好扩展性。

**3) 与文档关系**：图中双解析路径精确对应文档"算子仿真"与"算子上板"两类性能数据的并行处理设计，印证架构对两类调优场景的均衡支撑。
- `8a89fbabc5733e1a7aac5a054dcb2020_951x890.png`: # 图文联合解读

**1) 图中内容**：自上而下的分层类图——DeviceDataParse 解析原始数据，通过 `<<Usage>>` 依赖交付 DataHandler；DataHandler 派生 DataHandlerOf910B / DataHandlerOf310P 两版本，分别生成 Fft/Acsq/AiCore/L2Cache/Hwts 等 Bean，被 OpBasicInfo、BasicPmu、PmuCalculator 共用；底层的 CachelineHeatMap、MC2TimelineParser、StorageAccess 等特性类最终通过聚合关系汇入 DataVisualize 输出可视化数据。

**2) 技术结论**：采用"解析→模型→特性→可视化"的四层流水线，按芯片版本（910B/310P）分离数据处理，并按业务特性横向扩展。

**3) 与文档论点的关系**：直接对应文档"上板调优"功能清单——Cache 热力图、计算内存热力图、Roofline（BasicPmu/PmuCalculator）、MC2 通算流水图等均由图中对应类生成，验证了模块化、按特性聚合可视化输出的架构设计主张。
- `3abb8bd5fbcd5ab405175535888d270a_865x509.png`: **图文联合解读：**

图示单算子"解析—计算—可视化"三级流水线架构：左侧Parse阶段含两级ThreadPool，按DataCenter并行分发解析任务（ParseByCoreCore/calByCore）并生成pc2Code；右侧明细展示PluginManager驱动的InstParse、CacheParse、ProcessBasedCalculator、Pc2Code等可插拔模块，以及Visualise阶段输出的SplitCoreTimeLine、WholeCoreTimeLine与HotSpotMap。

该图论证了**多线程+插件化的分层解耦技术结论**：通过DataCenter统一数据底座、PluginManager扩展点、ThreadPool并行调度，实现解析/计算/可视化职责分离——与文档"明确模块设计、主要数据结构与处理过程，作为编码输入"的架构设计目的直接对应，支撑算子上板调优的指令级性能分析能力。
- `d56db36d46d521390d256af71d135b82_714x738.png`: # 图文联合解读

**1) 图中内容（UML类图）：**
自上而下展示「MteParser → MtePlugin → DataCenter → DataStream<T>」四层结构，采用组合（实心菱形）依赖。MteParser通过SetMtelog/Start/Stop控制MTE日志采集；MtePlugin以Entry()作为处理入口；DataCenter管理dataStreamPtrMap_/dataTablePtrMap_，对外提供Register与Get接口；DataStream<T>是基于std::queue<T>的泛型容器，提供Push/Pop/TryPop。

**2) 技术结论：**
采用"控制—插件—数据中心—数据流"分层解耦架构，结合模板泛型与队列，实现生产者-消费者式的高性能、类型安全的数据通路，支持多路数据并行注册与异步处理。

**3) 与文档论点的关系：**
为后续"计算内存热力图、Roofline、Cache热力图、通算流水图"等业务功能提供统一的性能数据采集与分发底座，是算子上板调优特征数据的来源基础设施。
- `50769b9f211c0b12606cdfc20451937e_755x247.png`: **图文联合解读（≤150字）：**

图示UML组件图：Parsing模块通过ToJson接口<<Use>>驱动上板数据可视化模块，后者经Interface1<<Use>>调用Calculation模块，三者共同封装于Visualization module容器内，形成"解析→可视化→计算"单向数据流。论证采用分层解耦架构，依托标准化接口（ToJson、Interface1）实现模块独立演进与复用。契合文档"算子上板调优"的模块化设计论点，为热力图、Roofline、Cache热力图等业务功能提供可扩展的支撑框架。
- `aa18e26188739b739a336b9f02b81b93_741x620.png`: ## 图文联合解读

**1) 图中内容：** UML类图展示插件式架构，顶层 `IPluginInterface` 定义 `Run()` 入口；`SimDataVisualizer` 作为编排器，统一调度 `HotSpotMapVisualizer`（热点图）、`SimPcToCode`（PC→代码映射）、`SimCodeToPc`（代码→PC反向映射），三者双向协作并共享 `SimVisualizerConfig`（chipType/outputPath等）配置。

**2) 技术结论：** 采用"接口—编排—专项可视化器—配置中心"分层设计，热点、流水、Code↔PC双向映射解耦，支持线程安全数据共享（`ThreadSafeUnorderedMap`），体现高内聚低耦合、可插拔扩展的微插件架构。

**3) 与文档关系：** 直接落地文档§1"算子仿真"能力，对应功能清单中的"代码热点图"业务功能，验证仿真器侧通过指令级仿真产出热点数据的可实现性。
- `42ce072b0176e22468f44988463b9602_634x732.png`: **1) 图中内容**：UML类图，展示仿真可视化模块的继承与组合关系。`SimDataVisualizer`继承`PluginInterface`（提供`Run()`入口），并组合`SimVisualizerConfig`（含芯片型号、Core名、输出路径、PC2代码行映射）；`SubcoreTimelineVisualizer`继承`SimDataVisualizer`，持有`waitFlag/setFlag`、多类Record集合、`pidMap/flagMap`等数据结构，并提供事件收集（指令/UserMark/Flag/Flow）、线程调度（`FindAvailableThread`）、元数据写入及JSON落盘等方法。

**2) 技术结论**：该模块采用"插件接口—配置—可视化器"三层架构，通过Record流式收集仿真指令与Flag事件，按线程调度重建时序，最终输出用于流水渲染的JSON数据。

**3) 与文档关系**：对应文档"通算流水图（MC2算子）"业务功能，论证了仿真调优中MC2算子通算瓶颈识别的数据通路与处理流程实现。
- `0445179afe113aca20d9c881bb2e7971_599x563.png`: **图文联合解读：**

1）**图示内容**：UML类图展示三组继承/关联关系。`PluginInterface`为顶层接口（含`Run()`）；`SimDataVisualizer`继承之；`CoreTimeLineVisualizer`继承`SimDataVisualizer`，封装`waitFlagName`、`setFlagName`、`pc2codeMap_`等私有字段及`ParseByCore`、`CollectInstEvents`、`DependencyRegister`等事件解析与流水线构建方法；`SimVisualizerConfig`作为配置数据类（含`chipType`、`coreName`、`outputPath`、`pc2Code`映射表），通过实线箭头被`CoreTimeLineVisualizer`聚合使用。

2）**技术结论**：证明系统采用**插件化分层架构**——以统一接口解耦可视化模块，通过配置对象注入硬件拓扑（chip/core）与码流映射（Pc2Code），实现流水线类可视分析能力的可插拔扩展。

3）**与文档论点关系**：呼应文档"算子仿真"调优场景——上板/仿真数据经解析后，由可视化插件（如Core时间线）统一呈现，支撑流水图、热点图等业务功能的模块化交付。
- `edeab66075d8586d74141cb17b2c783e_440x245.png`: **图文联合解读：**

图示为UML组件图，包含三个组件：**Plugin module**（插件模块）、**msbit**、**Basic module**（基础模块）。Plugin module通过**MSBitAInit**接口（<<Realization>>，实现关系）暴露给msbit；Basic module以<<Use>>依赖方式使用Plugin module的**stub逻辑**（桩逻辑）。

**论证结论：** 采用**接口解耦+桩逻辑注入**模式，插件模块通过标准化接口MSBitAInit向msbit提供服务，基础模块独立调用桩逻辑，三者分层隔离，便于解耦、测试与扩展。

**与文档关系：** 印证文档所述"算子调优组件作为算子开发工具链关键一环"的模块化设计思想，体现组件间松耦合架构原则，为编码阶段的接口定义与模块划分提供设计依据。
- `718f6c588384db46683f20bf40a856bb_496x374.png`: 图示为UML组件图：Plugin module（插件模块）容器内含Transfer stub interface（传输桩接口）及其Interface implementation（实现关系，`<<Realization>>`），后者通过`<<Use>>`调用Data recording（数据记录）组件；外部Basic component提供MSProfAtInit接口被插件模块依赖使用。

论证结论：采用**插件化、低耦合**架构——算子调优业务功能（如计算内存热力图、Roofline、Cache热力图等）通过统一桩接口由独立Basic组件注入，性能数据采集与记录可插拔加载。

与文档关系：印证了第1、2章所述"算子开发工具模块设计"的核心理念，即通过标准化接口解耦基础能力与业务功能，支撑算子仿真与上板两类调优场景的灵活扩展。
- `c1018e879215315155a838be67be24af_887x556.png`: **图文联合解读：**

1) 图为UML类图，展示InjectionEvent事件注入模块的架构：Task通过<<Usage>>触发；InjectionEvent提供Start/Stop/RegisterFunc；通过Association关联packet（含Payload，含profDataPathConfig/processCtrlReq），通过<<Usage>>使用communication（RemoteProcess、sendMsgQueue、SendMsgAsync/ReceiveMsg）实现消息收发，并使用DataParser（MteParser、InstrParser、iCacheParser三类解析器及对应日志接口）和DBIParser进行数据解析。

2) 论证了算子上板性能采集采用"事件注入→消息通信→多类型并行解析"的分层架构，解析模块按MTE、指令、iCache、DBI分类处理，支撑多样化性能数据输出。

3) 对应文档"算子上板"调优场景，为功能清单中Roofline、Cache热力图等提供底层采集解析链路支撑。
- `f02a02a67847d793c2ca85ddeebd034b_971x438.png`: 1) **图示内容**：描述了算子Profiler持久化数据的二进制文件结构。多个block（block1~block100）顺序排列，每block由BlockHeader（Record count/offset/nd_para configuration，均为uint64）、RecordHeader+xxxRecord（type+record1/2/3）以及512B padding组成，block间通过偏移量串联。

2) **技术结论**：采用"定长块+变长记录+页尾对齐"的混合布局，兼顾随机访问效率与缓存/页对齐写入性能，是大规模算子性能数据落盘的标准设计。

3) **文档关联**：作为"算子上板"调优的数据基座，该结构承载Roofline、Cache热力图、通算流水图等业务功能所需的原始性能记录，是上板调优链路的关键存储层。
- `cf1aff15b08bb3fe4b7634e5202de28e_606x467.png`: **图文联合解读：**

1) **图示内容**：展示了二进制数据文件的块结构。文件由若干数据块组成，每块包含两段——**块头**（8B内容长度uint64 + 1B类型uint8 + 1B零填充长度uint8 + 2B Reserved）和**块体**（按bin类型组织的任意长度内容），总大小为4字节倍数，可依次排列至第n块。

2) **技术结论**：采用"通用块头+类型化块体"的可变长TLV-like结构，便于按数据类型（如Roofline、Cache热力图、流水图）灵活扩展；同时通过4字节对齐保证跨平台解析安全。

3) **与文档关系**：该图支撑"算子调优组件"功能清单的多样化数据需求——不同调优图（内存热力图、Roofline、Cache、MC2流水）可对应不同block type，统一在同一bin文件中序列化存储，印证了文档所述"模块化、可扩展"的架构设计思路。
- `e798b43938a390ec8513f21c4c077819_639x840.png`: # 图文联合解读

## 1) 图中内容
该流程图描述了**寄存器占用统计算法**：
- **数据存储**：左侧"Historical occupied registers (DST) map"作为持久化数据结构参与每轮迭代
- **主流程**：取指令寄存器 → 区分DST/SRC → 双重判断（DST是否在SRC中？否则DST是否在历史表中？）→ 计数一次 → 更新历史表 → 判断是否为最后一条指令
- **关键收敛步骤**：处理完所有指令后，将所有历史占用寄存器视为DST再次执行算法，并明确要求**时间复杂度 < O(n)**

## 2) 技术结论
通过"历史占用DST映射表"做记忆化缓存，避免每条指令两两比较，将朴素O(n²)复杂度降至接近O(n)；同时通过"是否在SRC/历史表中"的去重逻辑，防止DST被重复计入占用数。

## 3) 与文档论点的关系
该算法支撑算子调优组件中**上板调优**功能（如计算内存热力图、Roofline瓶颈分析）的底层数据采集——寄存器占用率是评估算子在昇腾硬件上资源压力的关键指标，本图展示了Profiler架构设计中资源分析模块的核心处理过程。
- `1a12bc5385fc2d2751bf3684dc8ef711_606x314.png`: **图文联合解读：**

1) **图示内容**：左侧为 aclnn dynamic 调用流程（rtRegisterAllKernel→Malloc/MapMem→Launch→Free/UnMapMem→UnRegister）；右侧 msOpProf(on-board) 虚线框内四个蓝色模块通过"Hijack"分别劫持对应运行时 API，注入二进制加载、内存备份、性能采集、内存释放的自定义实现。

2) **技术结论**：on-board 调优采用**运行时 API 劫持机制**，在算子真实硬件执行的关键节点透明插入插桩，无需修改 aclnn 动态库即可获取上板真实性能数据。

3) **文档对应**：印证文档"算子上板"调优场景——即通过劫持 Runtime 接口，实现 Roofline、内存热力、Cache 热力等上板性能分析功能的底层采集路径。
- `428ea3fa9e3357494c0695c49c79c5e5_756x348.png`: **图文联合解读：**

图示为UML时序图，描述算子仿真场景下数据采集流程：用户进程初始化后，依次通过Runtime interface调用`rtSregister`→`ProfDataCollect.SaveObj`记录对象信息至`DataCollectWithSimulator`；再调用`rtKernelLaunch`→创建ProfDataCollect→向服务器请求outputPath→`ProfInit`→执行→`ProfData`。论证了仿真器采集需经"注册对象→创建采集器→请求路径→初始化→执行→归档"六阶段闭环，体现了Runtime、ProfDataCollect与DataCollectWithSimulator三者分层协作的架构设计，对应文档"算子仿真"调优路径。
- `33e097268e3e2fec3e00bf7d3f11943b_802x293.png`: **图文联合解读**

1）**图示内容**：左侧GM含data/backup；右侧三级流水线，每级data→kernel→backup，"Execution"驱动kernel执行，"Restoration"将结果回写backup；级间data/backup通过实线箭头串联，形成"执行-恢复"循环机制。

2）**技术结论**：算子采用**checkpointing机制**，将输入数据与备份分离存储，通过多级流水线实现可恢复、可复现的迭代式执行，确保每次kernel运行的数据状态可追溯。

3）**与文档关系**：该图为算子上板调优提供数据采集底层支撑，使Roofline分析、通算流水图等功能能在真实硬件上获得可靠、可重复的性能数据，呼应"算子上板反映真实性能"的核心论点。
- `cee27f22cc2250ad3a5581dd027d64ec_705x586.png`: ## 图文联合解读

**1) 图示内容：** 时序图刻画5条生命周期线（msOpProf / AscendCL / Basic module / mstx / User operator）的调用流程。用户算子经mstx埋点（RangeStartA/End）→ Basic module转发至 AscendCL 的 `IRICaptureBegin`/`End` → `loop3` 中循环 `IRIExecuteAsync` 并执行Data saving → 最终 `IRIDestroy`，由Basic module退出后回传msOpProf做Parse。

**2) 技术结论：** 论证"算子上板"性能采集采用分层调用链——用户算子通过mstx轻量埋点，Basic module适配层封装AscendCL的RIC捕获接口完成指令级数据落盘，msOpProf离线解析，全程闭环支撑Roofline、Cache热力图等调优功能。

**3) 与文档论点呼应：** 印证了文档功能清单所列"上板调优"类业务（Roofline瓶颈分析、Cache热力图、计算内存热力图、通算流水图）的数据来源链路，明确了模块间接口契约。
- `1f3babf8f320f45808062c10f4829f0c_676x393.png`: **图示内容**：左侧灰色框"aclnn dynamic"展示运行时调用链（rtRegisterAllKernel→rtSetDevice→rtGetDeviceCount→rtGetDeviceInfo→rtGetSocVersion→rtKernelLaunchWithHandle→rtDevBinaryUnRegister）；右侧蓝色框"msOpProf (on-board)"列出六个挂钩模块（.o信息记录、模拟器适配×2、正确信息返回、SoC版本替换、Profile数据采集），通过"Hijack"箭头劫持左侧对应acirt接口。

**技术结论**：msOpProf采用Hijack机制无侵入拦截runtime的acirt调用，在不修改aclnn动态库的前提下注入仿真适配与性能采集能力。

**与文档关系**：印证文档"算子仿真"与"算子上板"两类调优数据的采集实现路径，支撑功能清单中上板调优相关的性能可视化需求。
- `4f2aa7604d013cd8200e9d3dec0e0cb3_554x139.png`: 1) **图示内容**：四个蓝色矩形框从左至右依次为 `aclrt`、`aclrtImpl`、`aclrtImpl`、`rts`，对应底层动态库 `libascend.so`、`injection.so`、`libascend_impl.so`、`libruntime_camodel.so`。框间通过三条带标签的弧形箭头连接：`aclrt→injection.so` 为"Dependency order modification"（依赖顺序修改），`injection.so→libascend_impl.so` 为"dlopen and call"（动态加载调用），`libascend_impl.so→libruntime_camodel.so` 为"call"（直接调用）。

2) **技术结论**：展示了算子运行时库的**分层加载与调用链**——上层通过修改依赖顺序触发注入层，注入层以 `dlopen` 懒加载实现层，最终直达底层 RTS 模型库，形成可拦截、可观测的运行时插桩通路。

3) **文档关系**：印证了架构设计中"模块化、按层插桩"的设计理念，为算子性能数据采集与调优功能（如内存热力图、流水图）提供运行时拦截基础。
- `bde468e9c0c6b148a76c2a4dba5f4957_590x188.png`: **图文联合解读：**

1）图示内容：上方蓝色方块横向排列表示算子执行序列（Operator1 → Target → Operator3 → Operator4），对应一个绿色椭圆标注"Parse profile data of the target operator."（解析目标算子profile数据）；下方通过"Modification"箭头连接到第二轮同样的执行序列，再次解析profile；底部"times"箭头表示该流程沿时间轴多次循环迭代。

2）技术结论：阐明Ops Profiler采用**迭代式调优工作流**——每次执行后解析目标算子性能数据，依据结果修改算子实现，再重复执行剖析，循环优化直至性能达标。

3）与文档关系：此图对应文档"算子上板调优"流程的可视化，体现了调优组件作为"获取性能数据和优化方向"工具的核心机制：通过多轮profile解析→修改→重执行的闭环，支撑内存热力图、Roofline、Cache热力图等业务功能的迭代分析。
- `c05e7daabb8ce6bfefaf9d7f981b3510_616x909.png`: **1) 图示内容：** 三方时序图（msOpProf / Basic component / Simulator），展示算子调优仿真流程：msOpProf 启动算子→Basic 注册仿真器接口→执行目标算子 A/B→循环内仿真器传输数据、msOpProf 处理数据→回送完成通知→生成解析可视化文件→执行非目标算子→算子退出。

**2) 技术结论：** 采用"Basic 中介、仿真器回灌、Profiler 采集"分层架构；目标算子需逐次仿真-解析循环以产出可视化数据，非目标算子仅作执行占位。

**3) 与文档论点关系：** 印证文档"算子仿真"场景——通过仿真器指令级仿真输出性能数据，对应功能清单中流水图/代码热点等上板调优所需可视化能力。
- `0a88cded14362a8b1296f411041af697_281x511.png`: **图文联合解读：**

1）图示为DBi任务执行流程图：从start出发，依次经过`DbiTaskConfig::Init`→`RunDBiTask`判断→`InitMemory`判断→`ExpandArgs`→`KernelLaunch+Synchronize`→`WriteMemInfo`，任一判断节点失败均直达End。

2）论证了算子上板调优的数据采集链路具有严格的顺序约束与短路容错机制。

3）对应文档中"算子上板"性能采集的真实硬件执行流程，是上板调优类业务功能（Roofline、Cache热力图等）的底层数据生产通路。
- `c6dde60847f0fc6d376b5c21cbda745e_471x370.png`: 图示为kernelLaunch、DBITask、ProfDataCollectt三对象的UML时序：kernelLaunch依次插入BBCount stub、自同步、记录信息至ProfDataCollectt，再refreshParam、插入自定义stub、同步、再记录。论证上板调优通过stub注入+kernel同步机制采集性能数据，与文档"算子上板"性能数据获取流程对应。
- `ee49ee40ab6421501678387083daf5bd_1010x619.png`: **图文联合解读：**

1) **图示内容**：UML时序图，含Actor、AscendC、Operator tuning tool、Basic component module、Profiling API五条泳道。流程为：用户用AscendC编译MC2算子→启动程序→调优工具向基础模块传参→模块劫持MsprofRegisterCallback与MsprofReportAdditionalInfo接口→回放算子并同步等待MC2线程，分别采集HCCL通信任务、AI CPU任务、AI Core任务流水→落盘并回传分析结果。

2) **技术结论**：上板调优采用"接口劫持+算子回放"非侵入式机制，通过拦截Profiling API回调获取三类任务流水，实现MC2算子通算性能数据的透明采集。

3) **与文档论点关系**：直接支撑功能清单中"通算流水图（MC2算子）"业务功能的设计实现，验证其上板调优的数据采集通路。
- `97bc6c3118b9d9963b644bf344bc47a9_1190x591.png`: **图文联合解读：**

图示为UML时序图，呈现四模块流水线：算子调优工具→数据提取→数据计算→数据可视化。数据依次传递"原始调优数据→指令数据结构→可视化数据结构"，各模块通过自调用完成内部细化（提取指令细节、分析UB地址bank冲突、写入InstrParseInfo、保存可视化数据）。该图论证了**模块解耦、单核单次调用闭环**的架构结论，与文档"上板调优"功能清单（如Cache热力图需分析UB冲突以优化命中率）一一对应，明确了模块职责划分与数据契约。
- `4d3d83b9ba3452f568ca875a6fba0f22_600x543.png`: **图文联合解读：**

1）图为UML时序图，含Actor、Operator tuning tool、Basic component module三条泳道：用户启动MC2算子→调优工具传递参数至基础组件→基础组件保存数据→多卡解析含三步（基础/可视化数据分析、通算流水分析、visualize_data.bin增强与trace保存）→返回分析结果。

2）论证：调优工具与基础组件解耦，多卡解析作为核心中间环节串起数据采集与可视化输出。

3）契合文档"上板调优"中MC2通算流水图功能的设计实现路径。
- `3cb0ff74e5f415ca79f81475417e9b8c_549x424.png`: **图文联合解读：**

图示为msopprof启动时序图，包含msopprof启动、DataCenter、MtePlugin、MteParser、InjectEvent五条泳道。

**1）画面内容**：msopprof先构造MteParser，再依次构造DataCenter和MtePlugin；InjectEvent调Start()触发MtePlugin，Plugin调Run()进行数据预处理；橙色loop2框内循环执行Push→trigger→SetMteLog→reply→数据处理；最后Clear、Shutdown、关闭插件并做后处理（merge、时序化）。

**2）技术结论**：插件采用"事件驱动+循环回调"架构，DataCenter负责数据中枢，MtePlugin负责指令注入与日志采集，MteParser为解析入口，三者解耦协作。

**3）与文档关系**：印证"算子上板调优"需多模块协同采集性能流水数据的架构设计，支撑Cache热力图、通算流水图等功能清单的实现。
- `c25a835f49bbef90ca85052b158dcc94_543x598.png`: # 图文联合解读

## 1) 图中内容
本图为**仿真调优时序图（Simulation Tuning Sequence Diagram）**，展示 4 个参与方：User、Operator tuning tool、Parsing、Calculation、Visualization。
数据流：
- User 导出已解析的 dump 数据 → 调优工具校验输入；
- 进入 **Multi-card parsing** 循环框：Parsing 按核插件化解析指令/Cache 信息 → 各核 datacenter 暂存 → Calculation 计算 gpr/ubread 等指令数据 → 回填并合并核间 datacenter → Visualization 生成流水图/热力图 → 数据落盘；
- 最终将算子解析结果回传 User。

## 2) 技术结论
论证了仿真调优采用**"插件化按核解析 + 分布式 datacenter + 多阶段流水线"**的分层架构：解析、计算、可视化解耦，支持多卡并行，并以 datacenter 为数据中枢贯穿全流程。

## 3) 与文档论点的关系
对应文档"算子仿真"场景——通过仿真器输出流水图、代码热点图等详细性能数据，支撑上板调优前的指令级深度分析。
- `949ac9f03680c24e723b9c6db7daf0cd_710x346.png`: **图文联合解读：**

1) 图示结构：左侧"process"框内嵌套"device 0"和"device 1"，每设备含"launch1/launch2"，右侧连接ProfConfig、MemoryContext、KernelContext、DataCollect四个外部模块，呈典型层级树+引用关系。

2) 技术结论：刻画了Profiler的多进程—多设备—多launch三级嵌套数据模型，配置/上下文对象按launch粒度挂载，采集结果汇总至进程级DataCollect。

3) 与文档关系：为上板调优功能（内存热力图、Roofline、Cache热力图、通算流水图）提供底层数据结构基础，体现"按launch采、按device组织、归口process"的数据流设计。
- `c8f24f9a8445ecaa4bf74839170d83a0_1105x705.png`: **图文联合解读：**

图示为「Data」类处理流程思维树：从获取relocObjectPath与.o路径起步，主线为`ParseMergedDumpData`，依次完成按socVersion分支控制、按核解析dump（含指令/Icache解析）、合并dump信息、指令地址反查码、序列化对象、生成JSON流水图（Trace/SepTrace）及统计序列化（含pcStatistic、codeStatistic、CoreStatistic等），圆圈数字标识子项数量。

**论证结论：** 上板调优数据处理是"解析→合并→序列化→可视化"的多阶段流水线，需结合soc版本分流并产出流水图与统计结果。

**与文档关系：** 印证文档所述算子上板调优功能（如通算流水图、性能统计）由底层Data模块的多步处理链路支撑。
