# MindStudio Debugger Architecture Design Specifications

> 仓 `msdebug` · 路径 `docs/en/development_guide/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/docs/en/development_guide/architecture.md

## 【定位】

本文面向编码与测试人员，给出 `msDebug` 在 CANN 与现有 LLDB 代码体系中的总体设计，重点说明 coredump 分析、应用调试启用、关键数据结构、接口调用链及软硬件协作约束。

## 【技术要点】

1. **能力范围存在两层划分**：项目概览将算子调试能力划分为 **异常检测、功能调试、性能调优三类**；但功能清单及后续详细设计主要覆盖 **coredump 文件分析、启用调试两类功能**，并未分别展开异常检测与性能调优的完整实现。

2. **msDebug 基于现有 LLDB 增量实现**：保留 LLDB 原

## 图文联合解读

- `context_view_1.png`: **图文联合解读：**

图示为UML组件图，展示msDebug调试工具与系统的交互流程：用户调用msDebug加载coredump文件；coredump文件由adump在runtime运行时生成；runtime与driver、ts协同工作，ts将任务调度至sqcp执行。

**论证结论**：msDebug作为独立离线分析工具，仅读取已有coredump文件，不介入实时调试链路，体现"数据一致性"与"易扩展"的设计目标——分析功能与生成路径解耦。

**与文档关系**：印证第2节"加载coredump文件"功能，呼应3.1节"数据依赖驱动/RTS/编译器提供数据"及模块解耦、易扩展的总体目标。
- `logical_view_1.png`: **图文联合解读：**

图示msDebug采用命令模式+分层架构：User经CommandObjectTarget/Memory/Ascend/Register四个命令对象调用DoLoadCore、DoReadMemory、GetSummaryInfo、ReadRegister接口，统一委派给ProcessElfCoreDevice处理coredump文件；该组件聚合RegisterContextCorePOSIX_ascend完成寄存器读取，并通过Generalization关系使RegisterInfoPOSIX_ascend派生出ascend310P/910B/910D等芯片特化子类。

该图论证了**"易扩展"**的核心设计目标：新增芯片仅需继承RegisterInfoPOSIX_ascend基类即可接入，命令对象与处理逻辑解耦。这正契合文档§3.1关于"寄存器表与内存类型随芯片变化，寄存器维护代码须易扩展"的论点，体现数据一致性前提下分层抽象的设计思路。
- `static_structure_diagram.png`: **图文联合解读：**

1) **图示内容**：UML类图，呈现两套层次化结构。
   - 左侧：核心加载链 `ProcessElfCore`（抽象）→ `ProcessElfCoreDevice`（含 LoadCore/DoReadMemory/GetSummaryInfo 等方法），通过聚合持有右侧对象。
   - 右侧：寄存器上下文链 `RegisterContext`→`RegisterContextPOSIXCore_ascend`（组合持有 `RegisterInfoPOSIX_ascend`），后者派生三个芯片子类 **910B / 310P / 910D**，并进一步下沉为 POSIXCore 版本。

2) **技术结论**：采用**模板方法 + 策略模式**，将"核心加载"与"寄存器/内存操作"解耦；芯片差异封装在叶子子类（GetRegisterAddr/GetRegisterExtractor），新芯片只需继承并覆写对应方法。

3) **与文档呼应**：直接佐证文档 §3.1 第 1 条"**Easy code extension**"——寄存器表/内存类型随芯片变化的设计目标，通过多级 Generalization 自然达成，新增芯片扩展无需改动基类框架。
- `context_view_2.png`: ## 图文联合解读

**1) 图中内容**
UML组件图展示msdebug的部署架构,划分为Host与Device两大节点。Host端包含CANN(编译器、msdebug、运行时)与driver(ts_drv.ko、ts_debug.ko);Device端为TSFW的DEBUGGER_API。二者通过`sq.cq`接口连接,Host侧对外暴露`/dev/drv_debug`字符设备。依赖关系标注明确:`msdebug`依赖compiler与runtime,并通过`/dev/drv_debug`调用`ts_debug.ko`;`ts_debug.ko`与`TSFW`均实现`sq.cq`接口,完成Host-Device通信。

**2) 技术结论**
该架构呈"分层隔离+接口对接"模式:上层(msdebug)与底层芯片固件(TSFW)通过标准队列接口解耦,便于不同芯片扩展;调试通道复用现有驱动框架,集成成本低。

**3) 与文档论点关系**
印证文档§3.1所述"易扩展性"与"数据一致性"目标——`sq.cq`抽象屏蔽芯片差异,`/dev/drv_debug`统一调试入口,支撑多算子集成场景下的功能调试落地。
- `logical_view_2.jpg`: 图示为msdebug包内UML组件图，包含三个组件：`lldb`（调试器前端）、`lldb-server`（远程调试代理）、`runtime_stub`（运行时桩），通过两个`socket`接口连接。

论证结论：msdebug采用**C/S架构**，lldb与lldb-server通过socket通信，runtime_stub为lldb-server提供运行时支持，实现远端调试能力。

与文档论点关系：体现"易代码扩展"目标——通过解耦的组件与标准化socket接口，使调试功能可在不同算子集成场景中灵活扩展。
- `software_implementation_unit_design.jpg`: **图文联合解读：**

1）图示为UML组件图，呈现msDebug三大组件：lldb（含CommandObjectAscend、GDBRemote Client等）、lldb-server（含LLGS、Ascend910/310 DeviceContext等）、runtime_stub（含KernelInfo、SHA265等），通过socket和runtime接口相互连接，runtime经hijack挂载。

2）论证了msDebug采用客户端-服务端-运行时桩的分布式调试架构，通过socket通信实现异构芯片（910/310）扩展。

3）支撑文档"易扩展"与"数据一致性"目标——DeviceContext按芯片分类便于新增扩展，runtime_stub劫持保证驱动/RTS/编译器数据一致。
- `coredump_file_structure.png`: # 图文联合解读

**1) 图中内容**（结构/数据流/关键标注）：
- **根节点**：`ELF Header`，通过 `.ascend.devtbl/.global/.local/.reg/.auxinfo.global/.auxinfo.local` 节派生数据。
- **派生结构**：`DevInfo`（含 `chip_type`、`aic/aiv_bitmap`）、`GlobalMemory`/`LocalMemory`（`uint8_t`）、`RegInfo`（结构体数组）、`GlobalMemInfo`/`LocalMemInfo`（含 `section_index、addr、size、GlobalDataType/MemType`）、`Section Header` 数组。
- **关键枚举**：`CHIP_BEGIN…CHIP_END`（覆盖 CLOUD/MDC/MINI_V3/NANO_V1/KUNPENG920 等 16 种芯片）、`GlobalDataType`（输入/输出/Workspace/Tiling 等 Tensor 类型）、`MemType`（LOA/LOB/LOC/UB/L1/DCACHE/ICACHE/REGISTER）、`coreInfo/shape`（`coreId`、`dim_size[25]`）。

**2) 论证的技术结论**：以 ELF 节为核心的 coredump 元数据组织方案，按"芯片→内存域→张量/存储类型"分层抽象；结构数组支持 per-core/per-section 索引，类型化枚举保证解析一致性。

**3) 与文档论点关系**：直接支撑 §3.1 两条目标——`CHIP_*` 枚举与 `chip_type` 字段体现"代码易扩展（新芯片）"，统一类型枚举与中心化 ELF Schema 保障"数据一致性（driver/RTS/compiler）"。
- `analyzing_coredump_files.png`: **图文联合解读:**

1. **图示内容**：UML时序图，展示msdebug处理coredump文件的流程。用户（Actor1）通过Command发起`msdebug --core coredump.file`，Command创建`ProcessElfCoreDevice`实例并调用`DoLoadCore`解析coredump文件，进而创建`RegisterContextPOSIXCore_ascend`实例保存/恢复上下文。随后分四个交互帧：**Summary**（GetSummaryInfo）、**Read memory**（DoReadMemory）、**Read register**（ReadRegister）、**Switch cores**（SetAIC/SetAIV OnFocus），均从已解析的coredump数据中读取并切换core。

2. **论证结论**：模块采用**职责分层**设计——Command为入口、ProcessElfCoreDevice负责核心加载与内存读取、RegisterContextPOSIXCore_ascend负责寄存器上下文，符合理器调试中"芯片可扩展"的解耦架构。

3. **与文档关系**：图直接对应"功能列表"中**分析coredump文件**的四大能力（加载、打印概要、读内存、读寄存器、切换core、显示栈），验证了文档第3.1节"易扩展、数据一致性"的设计目标。
- `debugging_enablement_interaction_process.jpg`: **图示内容**：UML时序图，含Actor、msdebug、lldb-server、debuggee（含runtime_stub）、driver五角色，按"kernel加载场景"分两支——显式加载（经fatbin的GetChildModuleSpec）与动态加载（经共享库）。关键流：lldb-server发送kernel hash → debuggee经fork/execve起driver → driver注册rtDevBinaryRegister并生成hash → debuggee比对hash → 命中则覆写指令（插入断点），未命中则忽略；随后rtKernelLaunch、rtSynchronizeStream、上报中断事件。

**论证结论**：以kernel hash比对机制实现driver侧真实kernel与调试器断点的精确匹配，统一支持显式/动态两种算子集成场景。

**与文档关系**：对应第2节"Enabling debugging"在不同集成场景下的基础调试能力，以及3.1节"易扩展"与"数据一致性"两大总体目标。
- `interaction_process_of_enabling_debugging_for_a_specified_device.jpg`: **图文联合解读：**

1) **图示内容**：序列图描绘 Actor→msdebug→lldb-server→debuggee(runtime_stub)→driver 的交互流程，涵盖设断点(b allgather.cpp:50)、设备ID保存与传递(run/vRun)、fork+execve 启动、rtSetDevice/rtKernelLaunch 调用、按 `opt opt1` 分支设置匹配设备断点、中断事件上报、断点命中提示及多设备查询，最后验证设备2因不匹配返回错误。

2) **技术结论**：调试链路需在全过程中保持**目标设备ID一致性**；断点仅在启动设备匹配时才下发，否则跳过；驱动侧以中断事件反向通知。

3) **与文档对应**：佐证"数据一致性"目标——ID 跨层贯穿而不丢失；体现"易扩展"——以 opt 分支隔离匹配/非匹配逻辑，便于适配多算子集成场景。
