# MindStudio Debugger 架构设计说明书

> 仓 `msdebug` · 路径 `docs/zh/development_guide/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/docs/zh/development_guide/architecture.md

# msDebug 架构设计文档深度解读

## 【定位】

本文档是 **MindStudio Debugger（msDebug）算子调试工具的架构设计说明书**，旨在解决原有功能调试工具仅具备仿真调试能力所导致的「仿真与真实结果不一致且性能差」的问题，通过明确 msDebug 的模块设计、主要数据结构与处理过程，为后续编码与测试人员提供指导。

---

## 【技术要点】

1. **基座与扩展模式**：基于 lldb 原有代码进行修改，参照原流程补充针对昇腾设备的实现；通过多态机制实现 `RegisterInfoPOSIX_ascend` 寄存器信息类，方便后续芯片类型扩展。
2. **核心能力划分**：包含两大模块——**coredump 文件分析模块**（加载 AIC ERR 崩溃产生的 coredump 文件，提供内存/寄存器/调用栈/切核/汇总信息打印）和**调试使能模块**（支持单算子、PyTorch 多算子、MC2 算子等多种场景下的程序调试启动）。
3. **关键运行时标识**：解析 elf 头时需特判 `e_machine` 字段为 `EM_ASCEND（0x1029）`，用于识别昇腾 coredump 文件。
4. **内存类型分类**：`DeviceAddressClass` 需新增支持 `DCACHE`、`ICACHE` 类型，其中 `DCACHE` 又包含 GM 中的 `STACK`、`TILING DATA`、`ARGS` 三类。
5. **硬件异常管道细分**：`UpdateStopInfo` 通过读取 Error 寄存器判断是 `cube / ccu / mte / vec / fixp` 哪条 pipe 异常。
6. **通信与下发链路**：组件间通信使用 socket 实现；通过 `ts_debug.ko` 驱动接口向 device 侧 TSFW 下发调试命令，或借助 PCIe 接口向 device 侧内存下发断点指令。

---

## 【关键机制与数据】

### 1. AIC ERR → coredump → msDebug 的链路
- **原文**：基于 AIC ERR 崩溃时产生的 coredump 文件，使用 msDebug 工具进行加载文件并分析数据，从而降低用户现场 AIC ERR 压测诉求，提高硬件异常问题定位效率。
- **原文**：驱动、rts 基于 sqcp 调试通道上报的 AIC ERR 崩溃信息，adump 组件产生 coredump 文件。
- **机制要点**：使用 msDebug 调试算子程序和产生 coredump 文件存在冲突（依赖同一 sqcp 调试通道），不能同时开启；adump 使能 coredump 文件生成功能需要开关开启。

### 2. 上板单步调试命令流（标准一次流程）
- **原文**：msDebug → ts_debug.ko（驱动接口） → device 侧 TSFW → 触发 DEBUGGER_API → 完成后向 ts_debug.ko 返回结果 → 返回消息至 msDebug。
- **能力扩展**：通过对 DEBUGGER_API 的扩展，可分别实现断点设置、恢复运行、单步运行、内存读取、寄存器读取等业务功能，并支持对新功能的扩展。

### 3. coredump 信息汇总（来自原文示例输出）
- **示例 chip 标识**：`hiipu64`、`A2/A3`
- **示例字段**：CoreId、CoreType（AIV/AIC）、PC、DeviceId、ChipType；汇总内存表含 Id、DataType、MemType、Addr、Size、CoreId、CoreType、dim 八列。
- **原文示例 PC 值**：`0x12c04120062c`（三条 AIV 核相同）。
- **示例规模**：STACK 大小 32768 字节；OUTPUT_TENSOR 维度 `[8, 2048]`，大小 32768；DEVICE_KERNEL_OBJECT 大小 182944。

### 4. 调试使能的运行场景约束
- **原文**：使能调试功能的成功标志是「在正确的时机下发断点并使算子命中断点」。
- **场景列表**：单算子、PyTorch 多算子、MC2 算子；MC2 算子额外需指定 device。

---

## 【表格解读】

### 表格 1：功能清单（原文 §2）

| 功能清单 | 功能描述 |
|---|---|
| 支持 coredump 文件分析 | 主要用于加载 coredump 文件，并提供打印内存、寄存器、coredump 汇总信息、切核、查看调用栈的功能 |
| 支持调试使能 | 在不同算子接入场景下使能调试基础功能 |

**逐行解读**：
- 第 1 行定义离线分析能力——针对已产生的 coredump 进行被动加载与多维度信息提取（内存/寄存器/汇总/切核/调用栈）。
- 第 2 行定义在线调试能力——按算子接入场景主动开启调试基础设施。
- 两者形成「事后取证（coredump 分析）+ 实时介入（调试使能）」的闭环。

### 表格 2：关键要素设计（原文 §3.2）

| 关键要素 | 设计目标 |
|---|---|
| 实现模型 | 基于 lldb 原有代码进行修改，参照原有流程补充增加针对昇腾设备的实现。由于不同芯片的寄存器表、内存类型等信息有差异，对于新增芯片类型的寄存器操作维护代码、读内存数据相关代码开发易扩展。 |
| 交互模型 | 需要正确处理用户输入的命令行指令和参数，实现相应的调试功能，并回显正常信息或者提示错误信息。 |

**逐行解读**：
- 实现模型强调**继承 + 扩展**：基线是 lldb，扩展点面向昇腾设备；扩展点特别关注「芯片差异」（寄存器表、内存类型）。
- 交互模型关注**输入容错与反馈**：正确处理命令参数、正常回显与错误提示并存，确保人机交互的鲁棒性。

### 表格 3：coredump 文件分析模块软件单元清单（原文 §4.1.1.3）

| 软件单元 | 描述 | 外部接口 | 内部接口 | 关系描述 |
|---|---|---|---|---|
| CommandObjectTarget | core 文件加载命令解析模块 | --core | / | 解析 --core 命令，获取 coredump 文件路径，调用 DoLoadCore 接口执行 coredump 文件加载命令 |
| CommandObjectMemory | 内存读取命令解析模块 | memory read | / | 解析内存读取命令，调用 DoReadMemory 接口执行各类内存信息打印命令 |
| CommandObjectAscend | 信息展示、切核命令解析模块 | ascend info summary、ascend aiv/aic | / | 解析 ascend 命令，调用 GetSummaryInfo 接口执行获取汇总信息命令，以及调用 SetAicOnFocus/SetAivOnFocus 接口执行切核命令 |
| CommandObjectRegister | 寄存器读取命令解析模块 | register read | / | 解析寄存器读取命令，调用 RegisterContextCorePOSIX_ascend 提供的 ReadRegister 接口执行寄存器信息读取命令 |
| ProcessElfCoreDevice | elf core 进程模块 | / | LoadCore、ReadMemory、GetSummaryInfo、GetCoresInfo | 继承 ProcessElfCore 类，提供加载 coredump 文件接口、内存读取接口、coredump 文件信息获取接口、切核接口、获取核信息 |
| RegisterContextCorePOSIX_ascend | 寄存器管理模块 | / | ReadRegister | 在加载 coredump 时被 ProcessElfCoreDevice 创建，提供寄存器读取接口给 CommandObjectRegister 调用，成员变量有 RegisterInfoPOSIX_ascend |
| RegisterInfoPOSIX_ascend | 寄存器信息模块 | / | GetRegisterInfo | 作为 RegisterContextCorePOSIX_ascend 的成员变量，用于存储各种芯片类型的寄存器信息 |

**逐行解读**：
- 前四行是**命令解析层（CommandObject*）**，分别对应加载、内存读、汇总+切核、寄存器读四类 CLI 命令，全部通过内部接口下沉到 ProcessElfCoreDevice。
- `ProcessElfCoreDevice` 是**业务核心**，继承 lldb 原生 `ProcessElfCore`，把通用 ELF core 处理逻辑与昇腾特化能力合二为一。
- `RegisterContextCorePOSIX_ascend` 与 `RegisterInfoPOSIX_ascend` 是**寄存器职责分离的两层**：前者管理寄存器读写上下文，后者存储寄存器表信息；通过组合关系（成员变量）耦合，并以多态支持芯片扩展。

---

## 【公式解读】

**原文无公式**。

（文档中未出现 LaTeX 或伪代码形式表达的数学/逻辑公式；仅出现 C++ 接口签名伪代码，已在「使用方法」中保留。）

---

## 【关联】

文档以模块为单位串联了 msDebug 在 CANN 整体架构中的位置与上下游依赖，主要关系如下：

1. **与「调试器、驱动、RTS、编译器」的横向关系**：msDebug 属于 CANN 架构中的调试器组件；coredump 分析链路依赖驱动、RTS、sqcp 调试通道、adump 组件；调试使能链路依赖编译器（提供调试信息）、runtime 动态库、ts_debug.ko 驱动、TSFW。

2. **与「adump」的下游关系**：adump 组件是 coredump 文件的生产者；msDebug 是其消费者；二者共享同一 sqcp 通道，因此**互斥**。

3. **与「lldb / lldb-server / runtime_stub」的内部组成关系**：调试使能模块内部由三个组件构成，组件间通信使用 socket 实现：
   - **lldb 模块**：新增昇腾算子调试信息解析接口，新增并扩展通信接口传输昇腾设备信息。
   - **lldb-server 模块**：新增昇腾算子进程抽象类，实现调试使能功能；新增通信 server 端接口，接收 lldb、runtime_stub 模块发送的信息。
   - **runtime_stub 模块**：实现算子程序运行时接口劫持功能，为使能调试提供运行时信息。

4. **与「TSFW / DEBUGGER_API」的纵向调用关系**：通过 ts_debug.ko / PCIe 下发命令到 TSFW，TSFW 触发 DEBUGGER_API 完成断点/恢复/单步/内存读/寄存器读等操作，再回传结果。

5. **与「多算子调用方式」的能力兼容关系**：支持多算子调用、多进程调用、多线程调用；通过 runtime 接口的劫持适配多种算子调用方式。

> 注：原文未提供内部超链接信息（"内部链接: (无)"），以上关系均依据文档正文中的文字描述提取。

---

## 【使用方法】

### 1. coredump 文件分析模块（原文 §4.2.1.2）

**加载 coredump 文件**：
```bash
msdebug --core coredump_file [ kernel.o | fatbin格式的可执行文件 ]
```
或进入 msDebug 后：
```bash
(msdebug) target create --core coredump_file [ kernel.o | fatbin格式的可执行文件 ]
```

**打印内存地址信息**：
```bash
(msdebug) memory read
```

**打印寄存器信息**：
```bash
(msdebug) register read
```

**切核查看不同 core id 的崩溃信息（如 stack 数据）**：
```bash
(msdebug) ascend aiv/aic id
```

**打印 coredump 文件汇总信息（含 device id、设备类型、core id、tensor 信息）**：
```bash
(msdebug) ascend info summary
```

**展示 coredump 代码调用栈**：
```bash
(msdebug) bt
```

### 2. 调试使能模块（原文 §4.2.2）

**指定 device 调试使能**（方案 1，已选用）：
```bash
(msdebug) ascend device $dev_id
```

**切核命令（内部命令）**：
```bash
(msdebug) ascend aiv/aic $core_id
```

**场景约束**：
- 多算子场景需指定算子。
- MC2 算子额外需指定 device。

> 注：文档在 §4.3「数据模型」段被截断（"参考 coredump文件，设计适用"后未续），故数据模型的完整定义与潜在配置项**原文未涉及**。

## 图文联合解读

- `上下文视图1.png`: 图示解读：图中展示msDebug上下文视图，含用户、msDebug、coredump file、driver、runtime、adump、rts、sqcp等组件。用户通过msDebug加载coredump文件；adump经runtime、driver通道生成coredump；rts经sqcp调试通道上报AIC ERR。论证了msDebug作为调试器在CANN架构中与驱动、RTS、adump的协作关系，并通过sqcp通道串联。呼应文档4.1.1.1节，说明coredump文件依赖sqcp通道，故msDebug调试与adump生成coredump共用该通道，存在冲突不能同时开启。
- `逻辑视图1.png`: **图文联合解读：**

1）图为msDebug的类图，用户通过Usage关系向四个CommandObject（Target/Memory/Ascend/Register）下达指令；CommandObjectTarget调用ProcessElfCoreDevice（继承自ProcessElfCore）完成DoLoadCore；CommandObjectMemory/Ascend/Register经Aggregation关联ProcessElfCoreDevice和RegisterContextCorePOSIX_ascend（继承自RegisterContext）；RegisterContext通过Composition持有RegisterInfoPOSIX_ascend，其下通过Generalization派生出310P/910B/910D三个芯片子类。

2）论证结论：采用命令模式+模板方法实现"代码易扩展"目标，新增芯片仅需继承RegisterInfoPOSIX_ascend。

3）契合文档3.1节设计目标——基于lldb扩展、对新增芯片寄存器维护代码易扩展的架构承诺。
- `静态结构图.png`: **图解**：UML类图，展示msDebug中coredump分析的寄存器上下文类结构。`ProcessElfCore`泛化出`ProcessElfCoreDevice`；`RegisterContext`泛化出`RegisterContextPOSIXCore_ascend`（聚合关系），后者组合`RegisterInfoPOSIX_ascend`抽象类，该抽象类再泛化出910B/310P/910D三个芯片的具体子类。

**结论**：采用抽象基类+多芯片继承的分层设计，将通用寄存器操作与芯片相关数据（寄存器集、地址提取器）分离。

**与文档关系**：对应文档"易扩展"设计目标——新增芯片只需继承抽象类实现GetRegisterSet/GetRegExtractor，避免改动通用框架代码。
- `上下文视图2.png`: **图文联合解读：**

图示为UML部署上下文图，分Host（CANN含msdebug/compiler/runtime，driver含ts_drv.ko与ts_debug.ko，经`/dev/drv_debug`、`sq cq`接口）与Device（TSFW封装DEBUGGER_API）两侧。

论证msdebug部署于Host端CANN中，通过`sq cq`调试通道与Device侧TSFW通信，经`/dev/drv_debug`调用驱动，并依赖compiler/runtime协作。

呼应文档"msdebug属调试器、基于sqcp调试通道"的论点，为后续模块设计与接口约束提供结构基础。
- `逻辑视图2.jpg`: **图文联合解读：**

图示msdebug内部组件结构：左侧`lldb`与右侧`lldb-server`通过`<<Interface>> socket`连接，`runtime_stub`经另一socket与`lldb-server`通信。

论证结论：①msdebug基于开源lldb改造（前端lldb+后端lldb-server）；②采用socket接口解耦前后端通信；③`runtime_stub`实现对runtime接口的劫持，从而适配多算子/多进程调用方式。

与文档关系：印证"基于lldb原有代码修改"及"runtime接口劫持适配多种算子调用方式"的设计论点。
- `软件实现单元设计.jpg`: **图文联合解读：**

图示展示msDebug三组件架构：**lldb**（含CommandObjectAscend、Target等调试前端）通过**socket**接口连接**lldb-server**（含AscendProcessLinux、Ascend310B/310PDeviceContext等服务端），二者再由**runtime_stub**（含KernelInfo、MemoryObjectParser等）通过**hijack**机制劫持**runtime**接口。

论证结论：①遵循lldb原有C/S架构并扩展昇腾设备类；②通过多芯片DeviceContext实现易扩展；③runtime劫持实现多算子调用适配。

与文档关系：印证§3.1"基于lldb修改"及"runtime接口劫持适配多种算子调用方式"的设计目标。
- `coredump文件结构.png`: **图文联合解读：**

**图示内容：** 该图为msDebug加载coredump文件的ELF数据结构设计图。以ELF Header为根节点，左侧扩展出昇腾专有section（`.ascend.devtbl`、`ascend.global/local/reg/auxinfo`），右侧逐级展开DevInfo、GlobalMemory、LocalMemory、RegInfo、GlobalMemInfo、LocalMemInfo、Section Header等结构体，并列出CHIP类型、Tensor类型、MemType（LOA/L1/UB等）枚举表。

**技术结论：** 论证了msDebug在标准ELF格式基础上扩展昇腾设备专属section的设计方案，将芯片型号、AIC/AIV核位图、内存分区、寄存器信息按核心ID组织，可灵活适配多芯片多核场景。

**与文档关系：** 印证第3.2节"基于lldb代码扩展昇腾实现"及"代码易扩展"设计目标，为"支持coredump文件分析"功能提供具体数据布局依据。
- `coredump文件分析.png`: ## 图文联合解读

**1）图示内容**：UML时序图，描述msdebug加载coredump文件的交互流程。参与者包括Actor1、Command、ProcessElfCoreDevice、RegisterContextPOSIXCore_ascend四大角色，按"初始化→汇总信息→读内存→读寄存器→切核"五个分组（alt/ref框）展开：初始化阶段创建Device实例并解析coredump、构建寄存器上下文；其余阶段分别通过GetSummaryInfo、DoReadMemory、ReadRegister、SetAicOnFocus/SetAivOnFocus从已解析数据中读取。

**2）技术结论**：所有调试功能（内存/寄存器/汇总/切核）均离线读取coredump解析数据，无运行时依赖；Command作为统一入口分发指令，ProcessElfCoreDevice负责数据中枢，RegisterContextPOSIXCore_ascend封装寄存器访问，架构清晰分层。

**3）与文档论点关系**：印证§3.2中"易扩展"设计——寄存器操作独立封装于Context类，新增芯片仅需扩展对应Context即可复用Command/Device主流程，与"开源代码修改"原则一致。
- `调试使能交互流程.jpg`: **图文联合解读**

**1) 图中内容**：UML时序图，描绘 Actor→msdebug→lldb-server→debuggee(含runtime_stub)→driver 五方协作流程，分"kernel load scenarios"两种分支（显式 image add/export KERNEL 与动态加载 shared library）。核心流程为：设断点→生成 kernel hash→vRun→fork/execve→rtDevBinaryRegister→双侧 hash 比对→若一致经 driver 覆写指令触发断点，不一致则忽略该 kernel→rtKernelLaunch→中断事件上报→断点命中。

**2) 技术结论**：以**内核 hash 双侧比对**作为精准断点命中机制，支持显式与动态两种 kernel 加载方式，覆盖多算子、多进程调用场景，体现 runtime 接口劫持与驱动协同的调试使能实现。

**3) 与文档关系**：直接论证 §3.1 中"支持多种算子调用方式""算子接入方式支持""基于 lldb 扩展"等关键设计目标，说明调试使能与 runtime/驱动如何协同工作。
- `指定device调试使能交互流程.jpg`: **1) 图示内容**：UML时序图，展示Actor-msdebug-lldb_server-debuggee(含runtime_stub)-driver五方交互。用户依次发起`b allgather.cpp:50`、`ascend device 1`、`run`等命令；msdebug保存目标设备ID并下发；lldb-server fork debuggee，经rtSetDevice/rtKernelLaunch收集含多设备ID的kernel信息；匹配设备设断点，命中后回显；`ascend device 2`因单设备调试限制返回错误。

**2) 技术结论**：调试受runtime劫持触发，多设备场景需匹配目标设备才设断点；同一会话仅允许调试一个设备。

**3) 与文档关系**：印证§3.1"支持多算子调用方式""runtime接口劫持适配多种调用"及"数据一致性"设计目标，体现断点与设备绑定的实现机制。
