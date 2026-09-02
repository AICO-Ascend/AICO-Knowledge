# MindStudio Kernel Performance Prediction Architecture Design Specifications

> 仓 `mskpp` · 路径 `docs/en/development_guide/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mskpp/docs/en/development_guide/architecture.md

# mskpp 架构文档深度解读

## 【定位】
本文档是 MindStudio Kernel Performance Prediction (msKPP) 的架构设计总览,描述 msKPP 作为算子峰值性能预测工具的能力清单、建模/自动调优两大功能模块以及软件设计的三大核心目标(易扩展、数据一致性、低调度延迟)。

## 【技术要点】
- **核心定位**:基于算子表达式输入预测算子在算法实现中的峰值性能(peak performance),无需实际计算即可在数秒内返回结果。
- **仿真速度优势**:相对 cycle-level 仿真器提供**一个数量级**(order-of-magnitude)的仿真速度提升,原因是性能预测只需基于输入/输出规模计算对应算法的执行时间。
- **建模能力(2.1)**:涵盖传输通道建模、通道格式转换建模、Cache 命中率建模、Tensor 拆分、与 msprof 理论/实测值对比、指令级传输量/操作数/耗时统计、指令流水线 trace 可视化、指令耗时占比饼图。
- **DFX 能力**:包含 DSL 调试模式(用于排查指令入队/出队问题)和用户自定义指令的 profile 数据补充。
- **Auto Tuning 能力(2.2)**:通过 Python 接口自动生成算子交付 C++ 代码、自动编译模板库与交付代码、采集算子耗时指标、支持 KV 格式可调参数自动替换、支持 msOpGen 项目轻量级调度。
- **三大设计目标**:①易扩展(支持百量级 Ascend 基础指令的开放注册);②数据一致性(统一传输/计算指令耗时计算机制);③低调度延迟(外部 DSL 模拟下大量指令的跨语言调度要快)。

## 【关键机制与数据】

### 工作原理(原文:第 1 节 Overview)
- **输入**:用户输入算子表达式(operator expressions)。
- **处理**:基于输入输出规模(input and output sizes)计算对应算法的执行时间,**不进行实际计算**(not actual computation)。
- **输出**:算子在算法实现中的峰值性能数据。
- **性能基线**:原文描述"within seconds"级别出结果,且相对 cycle-level 仿真器达**一个数量级**提速。

### 数据流(原文:第 3.1 节 Overall Objectives)
- 算子性能建模**依赖**(relies on)现有指令 profile 数据 → 因此建模路径 = 输入算子表达 → 指令级耗时查表/计算 → 流水线调度 → 输出耗时与吞吐。
- 涉及**百种**(hundreds of)基础 Ascend 指令的注册与扩展。
- 数据一致性要求:**不同传输与计算指令的耗时计算保持一致**,指令扩展时数据流需规范化。

### 性能与规模数据(原文有的)
| 项目 | 数据 | 原文出处 |
|---|---|---|
| 仿真速度提升 | 一个数量级(order-of-magnitude)相对 cycle-level 仿真器 | §1 Overview |
| 结果产出时间 | 数秒内(within seconds) | §1 Overview |
| 支持的基础指令规模 | 数百种(hundreds of basic Ascend instructions) | §3.1 Easy code extension |

## 【表格解读】

### 表 2.1:Modeling 功能清单(原文逐字还原)

| Type    | Function                              | Description                                                       | Supported System Feature                                      |
| -------- | -------------------------------------- | --------------------------------------------------------------- | ---------------------------------------------------- |
| Service function| Operator transfer channel modeling                      | Models the data transfer channels for each memory unit of the operator.                       | Operator performance modeling -> Operator computing and transferring specification analysis -> Operator transfer instruction modeling|
| Service function| Operator channel conversion modeling                      | Automatically converts the special computing data format to the specific data format of the target storage unit.         | Operator performance modeling -> Operator computing and transferring specification analysis -> Operator transfer instruction modeling|
| Service function| Cache hit rate modeling                       | Models the hit rate of the high-bandwidth transfer channel between the operator GM space and the Vector Core/Cube Core.| Operator performance modeling -> Operator computing and transferring specification analysis -> Operator transfer instruction modeling|
| Service function| Tensor splitting                        | Splits tensors and simulates conversion of a large tensor into smaller tensors.                     | Operator performance modeling -> Operator computing and transferring specification analysis -> Operator transfer instruction modeling|
| Service function| Comparison between theoretical values of pipeline information and values measured by msprof| Compares the modeling data with the theoretical and measured values.                                     | Operator performance modeling -> Operator computing and transferring specification analysis -> Operator transfer pipeline statistics|
| Service function| Instruction statistics                          | Collects statistics on the total amount of transferred data, number of operations, and time consumption across different instruction dimensions.       | Operator performance modeling -> Operator computing and transferring specification analysis -> Operator instruction statistics|
| Service function| Instruction pipeline chart                            | Uses trace to visualize the pipeline arrangement of instructions executed by an operator.                  | Operator performance modeling -> Operator computing and transferring specification analysis -> Operator instruction pipeline    |
| Service function| Instruction Proportion Pie Chart                          | Uses a pie chart to visualize the proportion of time consumed by each instruction executed by an operator.               | Operator performance modeling -> Operator computing and transferring specification analysis -> Operator instruction proportion    |
| DFX      | Debug mode                             | Provides a debugging tool to help users quickly identify the instruction enqueue and dequeue issues in the DSL language, improving the tool's fault identification efficiency.  | Operator performance modeling -> Instruction pipeline -> Instruction scheduling analysis                |
| DFX      | Profile data supplementation                          | Supplements profile data for user-defined instructions.                               | Operator performance modeling -> Instruction pipeline -> Instruction supplementation                    |

**逐行解读**:
- **传输通道建模(Operator transfer channel modeling)**:为算子的每个 memory unit 建模其数据传输通道,对应"transfer instruction modeling"特性层级,是后续所有传输相关建模的基础。
- **通道转换建模(Operator channel conversion modeling)**:把算子特殊的计算数据格式自动转成目标存储单元的特定数据格式,与上行同属 transfer instruction modeling 层级,处理格式对齐问题。
- **Cache 命中率建模(Cache hit rate modeling)**:专门建模 GM 空间 ↔ Vector Core / Cube Core 间高带宽传输通道的命中率,这是影响算子性能的关键瓶颈参数。
- **Tensor 拆分(Tensor splitting)**:把大 tensor 拆成小 tensor 来模拟转换,是大 shape 场景下必备的工程化手段。
- **msprof 理论/实测值对比(Comparison between theoretical values of pipeline information and values measured by msprof)**:把建模输出与 msprof 理论值与实测值进行三方比对,对应"transfer pipeline statistics"特性层级,用于校验模型精度。
- **指令统计(Instruction statistics)**:从不同指令维度统计总传输量、操作数、耗时,是核心度量输出,对应 instruction statistics 特性。
- **指令流水线图(Instruction pipeline chart)**:用 trace 可视化算子执行指令的流水线排布,对应 instruction pipeline 特性,定位调度瓶颈。
- **指令占比饼图(Instruction Proportion Pie Chart)**:饼图可视化各指令耗时占比,对应 instruction proportion 特性,直观展示热点指令。
- **DFX-Debug mode**:DSL 语言的排障工具,定位指令入队/出队问题,提升故障识别效率,挂接在"Instruction scheduling analysis"特性下。
- **DFX-Profile data supplementation**:对用户自定义指令补充 profile 数据,挂接在"Instruction supplementation"特性,保证扩展指令也可被建模。

### 表 2.2:Auto Tuning 功能清单(原文逐字还原)

| Type    | Function                                  | Description                                                                                                            | Supported System Feature                       |
| -------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| Service function| Automatic generation of operator delivery code with Python interface support| Provides Python interfaces to generate C++ code for delivering operators in the template library. The generated code can be imported and extended by Python, allowing developers to deliver operators in Python. | msKPP supports automatic compilation and running of the template library.      |
| Service function| Automatic compilation of the template library                  | Provides Python interfaces to compile operators in the template library using the built-in compile option template or custom compile options entered by developers.                                | msKPP supports automatic compilation and running of the template library.      |
| Service function| Automatic compilation of delivered code                      | Provides Python APIs to compile the automatically generated operator delivery code to implement the operator delivery function.                                                | msKPP supports automatic compilation and running of the template library.      |
| Service function| Kernel metrics support              | Allows the use of the tuning tool's APIs to collect time consumption data of operators delivered by msKPP.                                                     | msKPP supports automatic compilation and running of the template library.      |
| Service function| Operator tool access and collaborative use                | Allows other operator tools to start the msKPP operator running script normally.                                                                         | msKPP supports automatic compilation and running of the template library.      |
| Service function| Automatic replacement of specified tunable parameters                | Supports automatic change of template code and collaborates with the compilation module to instantiate the code; supports inputs in KV format and correctly matches the tunable variables identified in the template library.| msKPP operates in conjunction with the template library to enable automatic change of template parameters.|
| Service function| Lightweight scheduling of msOpGen projects                | Supports code generation, compilation, and execution for the tiling function of msOpGen projects, as well as code generation, compilation, and execution for kernel functions.| msKPP supports automatic compilation and running of msOpGen projects.|

**逐行解读**:
- **Python 接口自动生成算子交付 C++ 代码**:用 Python 接口为模板库中算子生成 C++ 交付代码,生成的代码可被 Python 反向 import 与扩展,实现"用 Python 交付算子",特性挂接"模板库自动编译与运行"。
- **模板库自动编译(Automatic compilation of the template library)**:用内置编译选项模板或开发者自定义选项编译模板库算子,同上挂接"模板库自动编译与运行"。
- **交付代码自动编译(Automatic compilation of delivered code)**:把上一步自动生成的算子交付代码再编译,完成交付闭环。
- **Kernel 指标支持(Kernel metrics support)**:开放 tuning 工具的 API 供 msKPP 交付的算子采集耗时数据,形成"编译 → 部署 → 采集"链路。
- **算子工具访问与协同使用(Operator tool access and collaborative use)**:支持其它算子工具正常拉起 msKPP 算子运行脚本,体现 msKPP 作为子模块被编排的开放性。
- **可调参数自动替换(Automatic replacement of specified tunable parameters)**:配合编译模块对模板代码做参数实例化,接受 **KV 格式输入**并自动匹配模板库中已识别的可调变量,特性挂接"模板库自动参数变更"。
- **msOpGen 项目轻量级调度(Lightweight scheduling of msOpGen projects)**:为 msOpGen 项目的 tiling 函数及 kernel 函数提供"代码生成 → 编译 → 执行"全链路,挂接"msOpGen 项目自动编译与运行"。

### 表 3.2:Key Element Design(原文截断,仅保留首行)

| Key Element| Design Objective                                                                                                                                           |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Implementation model| Easy code extension: Operator modeling on different chip platforms relies on a large number o...(原文此处被截断) |

**解读**:该表用于列出关键设计要素及其目标,首行指出 "Implementation model" 的设计目标是"易扩展(Easy code extension)",并提示不同芯片平台上的算子建模依赖大量(后续被截断的)指令/实现。原文在此处被截断,后续 Key Element 行(如数据一致性机制、调度延迟优化等)未提供。

## 【公式解读】

原文无公式。

## 【关联】

### 上下游模块关系
- **输入侧 — 算子表达式与 profile 数据**:依赖"现有指令 profile 数据"作为建模输入,涉及**数百种基础 Ascend 指令**的注册机制(对应 §3.1 目标 ①)。
- **协同模块 — 模板库(template library)与 msOpGen 项目**:Auto Tuning 功能清单(§2.2)中所有功能几乎都挂接在"template library"或"msOpGen projects"特性下,表明 msKPP 与模板库/msOpGen 形成**编译-运行-采集闭环**。
- **对比基准 — msprof 工具**:§2.1 第五行的"Comparison between theoretical values of pipeline information and values measured by msprof"显示 msKPP 的建模结果需与 msprof 的理论值和实测值三方对照,msprof 是精度验证方。
- **DSL 层**:Debug mode 中提到"DSL language"用于排查指令入队/出队问题,说明 msKPP 对外提供 DSL 作为建模描述层,且需要跨语言调度支持(对应 §3.1 目标 ③)。
- **底层硬件 — Ascend 芯片**:建模明确指向 Ascend 平台的 GM / Vector Core / Cube Core 间的传输通道,说明 msKPP 是 Ascend 软件栈的性能仿真组件。

### 内部链接关联
文档末附的内部链接锚点参数:`arg1, arg2, ..., arg1, arg2, ..., x, y, z, a, b, c, problem_shape, a, layout_a, b, layout_b, c, layout_c`。从命名特征看,这些是**模板参数/调优变量**(如 `problem_shape`、`layout_a/b/c` 显然是大张量 shape 与 layout 的占位符),与表 2.2 第六行"Automatic replacement of specified tunable parameters"功能形成对应——即 KV 格式输入的可调参数在模板库中被识别为这些命名变量并完成实例化,具体变量值由用户输入决定,本文档未给出具体取值范围或枚举。

## 【使用方法】

原文未涉及。文档为架构总览,**未给出具体的启用方式、配置项或命令**(如 Python API 调用名、CLI 命令、配置文件路径等均未出现)。具体使用方法需参阅 msKPP 的用户手册/API 参考或 §2.2 中提到的 Python interfaces/tuning tool APIs 配套文档。

## 图文联合解读

- `3aaa6dee2c7d6ea527eaa3dae5f60cef_3197x1388.png`: 图示Developer经mskpp.launch接口触发CANN包内的mskpp组件，后者通过acl、runtime、mspti、bisheng接口分别调用AscendCL、Runtime、profiler、compiler四大组件，实现算子性能预测。论证mskpp作为CANN内的轻量仿真层，复用现有算子库与运行时能力完成执行时间估算，与文档"秒级输出、无需实际计算"的性能预测定位一致。
- `6e93a35427501292e4f17d7f2de9382d_2466x1697.png`: **图示内容**：UML组件图描绘msKPP架构——外层绿色Component包含Code generation（输入ActlassConfig）、Context、Compilation、Auto tuning及底部执行组件。数据流沿流水线推进：Code generation产出代码→Context接口→Compilation生成CompiledKernel→Auto tuning调优→launch发射，Context作为共享接口贯穿全局。

**技术结论**：msKPP采用模块化解耦的分层架构，将代码生成、编译、自动调优拆分为可组合组件，依托context共享接口流转数据，体现"无需真实计算、秒级输出"的轻量化性能预测设计目标。

**与文档关系**：印证第1节"性能模拟工具"定位及第2节Modeling服务功能列表——流水线即"建模→编译→调优→发射"的核心实现路径。
- `c3c78f4d6300e662e23871fcd79afa78_3213x1360.png`: 1) **图示内容**：UML组件图展示Code generation组件（含Launcher、Template、ActclassConfig三个类）与Context组件的关系。Launcher通过组合（实心菱形）持有Template和ActclassConfig，对外实现code_gen和ActclassConfig接口；Context实现kernel_name/kernel_src_file接口，Launcher通过Usage依赖该接口。

2) **技术结论**：代码生成采用"启动器+模板+配置"分层架构，Launcher负责初始化、参数解析和代码生成，Template提供渲染模板，ActclassConfig管理源码目录与kernel命名，实现关注点分离。

3) **文档关系**：对应文档第2章中"建模"服务功能的实现层设计，体现msKPP通过可配置代码生成管线产出预测所需kernel的工程化方案。
- `fb438072c2aec562011154c22a6caef1_3157x2450.png`: ## 图文联合解读

**1) 图示内容**：UML组件图，含两大组件——**Compilation**（Compiler、ActlassConfig、KernelInterface、CompiledKernel）与**Run**（NPULauncher、Driver），以及外部接口 *compile*、*launch*、*Context* 和 *set_device/create_stream/memcpy* 等。数据流为：Compiler 接收 ActlassConfig 生成 CompiledKernel（继承KernelInterface），运行时 NPULauncher 调用 CompiledKernel 的 `__run__`，通过 Driver 操作设备流完成执行。

**2) 技术结论**：msKPP 采用**编译/运行解耦**的两阶段架构——编译期产出可复用的 `CompiledKernel` 对象，运行期通过 `NPULauncher` 在 Context 与 Driver 协同下完成 kernel 调度，模块化清晰、职责分离。

**3) 与文档关系**：该图为"msKPP 功能列表与架构"提供结构化视角，印证"仅需算子输入输出即可秒级预测峰值性能"——通过抽象出 launch/Context/Driver 接口，使预测器只需模拟执行时间而无需真实计算，从而实现相较周期级仿真器数量级加速。
- `ee09dc2b587c3deef1d8575fed8e9864_1703x1267.png`: **图文联合解读**

**1) 图示内容：** UML组件图，划分四个红色虚线子模块——Code generation、Compilation、Run、Auto tuning，配色区分外部（紫）参数（如 launch_src_file_path、output_so_path、build_script、profiling、搜索空间定义）与内部（青）参数（如 kernel_name、kernel_src_file）。中心 Context 组件（kernel_name、kernel_src_file、build_script、launch_src_file_path）为四者共享状态，通过实线 Context update 与 <<Usage>> 依赖箭头实现数据流转：Codegen→Compil→Run 形成主链，Auto tuning 复用 Context 中代码与运行模块遍历搜索节点。

**2) 技术结论：** msKPP 采用"中央上下文+模块化组件"架构，算子源代码、编译产物、算子对象等中间产物通过 Context 集中管理，实现代码生成、编译、运行、自动调优四阶段解耦与流水线式串联。

**3) 与文档关系：** 图示对应第 2 章"建模"与"仿真"功能，直观呈现"秒级性能预测"所依赖的轻量化管线——无需 cycle 级模拟，只需算法执行时间即可输出最优配置与性能报告。
- `0e6fab0c918e34303ce4e77d445c8344_1239x1003.png`: **图文联合解读：**

图示代码展示了msKPP算子调用的五步流水线：①`Config`初始化、②`Launcher.code_gen()`生成交付代码、③`compile`产出可执行文件（构建阶段）；④`kernel[blockdim](a,b,c)`调用算子；⑤`@autotune`装饰器对tiling参数自动寻优（actclass与Shape组合）。

论证了msKPP通过"配置—生成—编译—调优—调用"闭环完成端到端性能仿真，对应文档§2.1建模服务函数，印证其"无需实际计算、秒级返回峰值性能"的核心论点。
- `171173b8b170d56a4559b663545b5603_1553x1097.png`: 图示为mskpp矩阵乘性能预测的Python代码示例，三个红色框标注关键API：
① `@mskpp.jit(src_dir, kernel_name)` 加载kernel源并生成算子代理；
② `do_my_matmul[blockdim](c, a, b)` 通过代理调用底层算子；
③ `@mskpp.autotune` 配置tiling_param1、alias1等多组可调参数组合。

**技术结论**：mskpp采用"JIT编译+代理调用+自动调优"三段式接口，用户无需真实计算即可枚举不同参数配置下kernel的执行时间。

**与文档关系**：直观印证"仅基于输入输出尺寸估算执行时间、数秒内输出结果"的快速性能仿真核心论点，体现其相比周期级仿真器的数量级加速优势。
- `d167a1df00f01576fb2cadc30fb35bd6_3097x3847.png`: **图文联合解读：**

1) **图示内容**：UML时序图，五个泳道（Developer/Auto tuning/Code generation/Compilation/Run/Ascend）。流程为：autotune触发 → 获取动态参数、修改kernel、实例化Launcher → code_gen（解析参数、生成胶水代码）→ 编译循环（按search node并行执行编译脚本，返回CompiledKernel）→ profiling（含warmup）→ 设备级并行循环（acl.init、参数下发、kernel下发与执行、流同步、回拷）→ 显示性能。

2) **技术结论**：自动调优是"参数收集→代码生成→并行编译→带预热的性能采样→多设备并行kernel执行"的多阶段流水线，通过两个并行维度（编译时按搜索节点、运行时按可用设备）实现高吞吐调优。

3) **与文档论点呼应**：文档称msKPP较周期级仿真器提速一个数量级，该图揭示其机制：跳过真实计算周期，借助编译缓存与并行设备采样在秒级完成算子峰值性能预测。
- `8fc9562a698616b7dd89cd087f5dc589_2571x1247.png`: **图文联合解读：**

图示采用"分解—分发—并行执行"三层架构：左侧Tuning task经Breakdown拆分为多组"编译任务+下发任务"对，由中央Dispatcher分发至两类资源池——编译任务进入Thread Pool中的并发队列，调度CPU Cores执行；下发任务进入Device Pool中的并发队列，调度Ascend Devices执行。

该图论证了msKPP通过任务解耦与CPU/NPU异构并行调度实现秒级预测的技术路线，与文档"较周期级仿真器提速一个数量级"的论点互为支撑：编译与下发流水化分工是性能预测快速性的架构基础。
