# memscope组件实现设计说明书

> 仓 `msmemscope` · 路径 `docs/zh/design/msmemscope组件实现设计说明书.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmemscope/docs/zh/design/msmemscope组件实现设计说明书.md

# msmemscope 组件实现设计说明书 — 一体化深度解读

## 【定位】
本设计说明书阐述 MindStudio-MemScope（msmemscope）作为整网内存调试调优工具的**整体软件架构与模块接口设计**，描述其如何在 AI 框架、CANN、driver 三层完成内存数据采集、辅助分析与自动诊断，并规划配套的 DFX 能力。

---

## 【技术要点】

1. **三层采集范围**：工具采集覆盖 AI 框架层（PyTorch、MindSpore）、CANN 层（runtime kernellaunch、acl 状态、atb op/kernel）、driver 层（hal 显存分配），并通过 `LD_PRELOAD` 劫持、MSTX 打点、runtime/driver hook 三条路径上报。
2. **三大模块解耦架构**：系统划分为数据采集模块、数据分析模块、框架模块；采集与分析运行在不同进程下，借助 EventTraceManager 类判断是否采集（含影子采集模式），通过 EventReport 接口上报，统一由框架模块串联。
3. **无状态事件路由 + 三阶段处理**：`EventRouter::Route` 作为无状态事件路由单例，CLI 与 Python API 模式共用；内部委托给 `EventHandler` 按 UpdateMemoryState→DispatchToAnalyzers→CleanupMemoryState 三阶段顺序处理，并支持影子事件跳过分发清理。
4. **订阅式分发替代硬编码**：所有分析器（Dump、DecomposeAnalyzer、InefficientAnalyzer、HalAnalyzer、StepInnerAnalyzer、OpExecuteWatch）通过 `EventDispatcher::Subscribe` 注册回调，`EventDispatcher::DispatchEvent` 根据订阅的 `EventBaseType` 与 `Priority` 进行反向注册式弱耦合分发，替代原 `Process::SendEvent` 中 switch-case 硬编码分发以及 MstxAnalyzer/PyStepManager 自建订阅。
5. **共享内存 IPC 通信**：`ServerProcess::Notify/Wait` 利用共享内存发送/接收数据包，返回值为实际字节数（>=0 成功，<0 失败），并要求具备维测或重发机制；多 client 并发场景下各管道解包缓冲带独立。
6. **进程拉起与配置解析**：框架通过 `UserCommand Parse(int32_t argc, char **argv)` 解析命令行（违规返回 help 打印并终止），通过 `Process::Launch`（先设置 `LD_PRELOAD`）`fork + execvpe` 子进程拉起客户脚本，主进程进入等待直到子进程自然或异常结束；分析器注册端口预留 `EventDispatcher::UnSubscribe` 支持动态增删。

---

## 【关键机制与数据】

### 数据流（原文工作原理）

> 原文 §4.1.3 逻辑视图：
> "和大多数内存分析工具类似，主要由三个模块组成……数据采集模块、数据分析模块以及框架模块，考虑到数据采集和数据处理的高效并行，将二者运行在不同进程下，数据采集和数据分析解耦，通过框架模块进行串联。"

采集端通过 hook（`Report_xx_hooks`）→ `Process::SendEvent`（内部委托 `EventRouter::Route`）→ `EventHandler` 三阶段（UpdateMemoryState / DispatchToAnalyzers / CleanupMemoryState）→ `EventDispatcher::DispatchEvent` → 分析器回调。原文显式声明这是替代原有的 `Process::SendEvent` 中 switch-case 硬编码分发与 MstxAnalyzer/PyStepManager 的自建订阅机制，说明设计属于"以统一订阅模型收敛历史上分散的事件分发路径"的演进。

### 上下文依赖（原文 §4.1.2）
- **AI 框架**：依赖 PyTorch、MindSpore，用于获取其内部内存池的内存行为（仅看整体用量不足）。
- **CANN**：感知 runtime 中 kernellaunch 与 acl 状态。
- **Driver**：获取上层所有应用的显存分配情况与 kernel 真实执行情况。
- **Insight**：可视化采集到的数据，呈现显存变化趋势与详情。

### 性能/容量数据
原文未提供具体数字（例如接口耗时、吞吐量、显存占用上限等），仅有"返回值 >=0 表示实际字节数"等语义化描述，未见性能基准数据。

---

## 【表格解读】

### 表 1：功能特性与 DFX 能力清单（原文 §开头表格，逐字还原）

| 类型     | 功能清单         | 功能描述                                                     | 支撑的系统功能         |
| -------- | ---------------- | ------------------------------------------------------------ | ---------------------- |
| 业务功能 | 数据采集         | 支持AI框架、CANN、driver层显存使用相关数据采集                | 数据采集               |
| 业务功能 | 自定义数据采集   | 支持客户自定义采集范围和采集项                                | 数据采集               |
| 业务功能 | 泄漏分析         | 支持PyTorch、mindspore框架内存池泄漏分析、CANN组件显存泄漏分析 | 显存调试               |
| 业务功能 | 显存比对         | 对不同软件版本采集到的内存数据进行比对，找到差异点            | 显存调试               |
| 业务功能 | 显存块监测       | 以算子为监测事件，在事件运行前后对指定显存值进行落盘          | 显存调试               |
| 业务功能 | 显存拆解         | 对显存使用情况进行分解，以可视化形式展示各个模块的显存使用情况 | 显存调优               |
| 业务功能 | 低效显存识别     | 对显存低效模式进行识别，包括过早申请、过迟释放、临时闲置      | 显存调优               |
| DFX功能  | 日志系统         | C++和python模块共用一个日志系统且支持分级控制                 | 系统可维护性           |
| DFX功能  | DT系统           | 通过UT、FUZZ工程白盒看护程序整体功能                          | 程序功能白盒看护       |
| DFX功能  | 数据采集插件化   | 针对采集项容易变化和增加的特点，对hook组件进行隔离，方便扩展  | 系统扩展性             |
| DFX功能  | 冒烟框架         | 对整个工具的所有主路径功能进行100%覆盖，在版本发布和代码上库前运行 | 系统可靠性          |

**逐行解读**：
- **业务功能（前 7 行）**：每行描述一项用户面能力并对应一类系统能力，"数据采集/自定义采集"为入口；泄漏分析、显存比对、显存块监测归为**显存调试**路径（侧重问题定位与差异比较）；显存拆解、低效显存识别归为**显存调优**路径（侧重结构化展示与模式识别）。
- **DFX 功能（后 4 行）**：用于工程保障而非用户业务面——"日志系统"统一 C++/Python 日志并支持分级（对应"数据采集插件化"的扩展性、"DT 系统"的测试保障、"冒烟框架"的发布门禁覆盖率 100%）。
- "**冒烟框架……100% 覆盖**"是原文中明确的覆盖率量化指标。

### 表 2：关键要素设计（原文 §3.2，逐字还原）

| 关键要素   | 设计目标                                                                                                  |
| ---------- | --------------------------------------------------------------------------------------------------------- |
| 上下文视图 | 给出组件的上下文，说明组件外部的交互和依赖关系                                                            |
| 逻辑视图   | 阐述组件的各个功能模块的静态关系，通过组件图来表示                                                       |
| 开发视图   | 表达完成各个功能模块所需要的子模块，以UML类图的形式展示                                                  |
| 交互视图   | 展示各个模块之间的动态交互关系，阐述其并发、同步等逻辑，主要以时序图进行表示                              |

**逐行解读**：这是经典的 "4+1" 视图的工程化简化版本——上下文（黑盒外联）、逻辑（模块静态关系）、开发（UML 类图）、交互（时序/并发同步）。原文中仅给出了前三个视图的章节展开（第 4 章"开发视图"实际包含了上下文、逻辑、类图），未单独列出交互视图章节（即未提供时序图）。

### 表 3：软件单元清单（原文 §4.1.3，逐字还原）

| 软件单元     | 描述                                                                                                  | 外部接口                                              | 内部接口                       | 关系描述                                                                                                |
| ------------ | ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------- |
| 数据采集模块 | 通过hook等方式采集内存相关数据，并发送给框架模块                                                       | Process::SendEvent（内部委托给EventRouter::Route）    | Report_xx_hooks                | 整个模块通过hook，注册回调方式等采集数据，经过一定处理后将数据发送给框架侧                              |
| 数据分析模块 | 向框架模块注册回调，对采集模块发来的数据进行接收和分析                                                  | EventDispatcher::Subscribe                            | EventHandle                    | 所有分析器统一通过EventDispatcher订阅模式注册回调，包括HalAnalyzer、StepInnerAnalyzer、DecomposeAnalyzer、InefficientAnalyzer、Dump |
| 框架模块     | 作为系统的入口，负责解析命令行，串联数据采集和分析模块以及插桩                                          | CommandParser、EventRouter                            | DoLaunch、SetPreloadEnv        | 解析客户命令行配置，EventRouter::Route统一将事件路由至EventHandler三阶段处理（UpdateMemoryState→DispatchToAnalyzers→CleanupMemoryState） |

**逐行解读**：
- **数据采集模块**：接口名为 `Process::SendEvent`，但原文明确指出"内部委托给 `EventRouter::Route`"，即对外语义不变但内部已改经无状态路由器；其内部子接口为 `Report_xx_hooks`（以 `xx` 占位表示多种采集项 hook）。
- **数据分析模块**：枚举了原文 4.1.4 中确认存在的 5 个分析器 + Dump，与"取代 switch-case 与自建订阅机制"的演进叙事一致。
- **框架模块**：内含三阶段处理管线，将事件生命周期拆为**状态更新→分发→清理**，影子事件具有单独的跳过逻辑（见 EventHandler 注意事项）。

---

## 【公式解读】

原文无公式。文档中出现的为接口签名（伪代码形式）与代码符号（如 `EventBase`、`std::shared_ptr<EventBase>`、`MemoryState*`、`SubscriberId`、`EventBaseType`、`Priority`、`HandlerFunc`），并非数值或解析公式。

---

## 【关联】

文档给出的模块与组件关系如下（原文 §4.1.2 – §4.1.4 抽取）：

- **上游依赖**：
  - **AI 框架**（PyTorch、MindSpore）→ 通过 hook 提供数据采集入口，承载内存池内部行为的可观测性。
  - **CANN（runtime + atb）**→ 工具劫持 `_ZN3atb6Runner7ExecuteE` 与 `_ZN3atb9StoreUtil15SaveLaunchParamE`（原文符号格式）等接口，获取算子/kennel 执行事件。
  - **driver（hal 层）**→ 通过 `halMemAlloc / halMemFree` 劫持获取显存分配释放原语。
  - **`LD_PRELOAD` 注入**：框架 `Process::Launch` 通过 `SetPreloadEnv` 设置 `LD_PRELOAD` 变量以劫持用户态符号。

- **下游消费**：
  - **Insight 可视化工具**：原文 §4.1.2 指出"工具采集到的数据通过可视化工具进行展示，可以看到显存变化趋势、显存使用详情等"，作为结果展示链路。

- **模块间上下游**：
  - **数据采集 ↔ 框架**：通过 `Report_xx_hooks` → `Process::SendEvent` → `EventRouter::Route` 单向流。
  - **分析器 ↔ 框架**：通过 `EventDispatcher::Subscribe / UnSubscribe` 反向注册，构成回调扇出。
  - **框架 ↔ 分析**：通过 `EventDispatcher::DispatchEvent(event, MemoryState* state)` 将事件与内存状态快照一同下发。

- **DFX 配套对工程能力的支撑**（表 1 后 4 行）：日志、DT、插件化采集、冒烟框架分别对应**可维护性 / 白盒看护 / 扩展性 / 可靠性**，与 §4.1.4 中"工具模块（LOG、字符串处理、数值计算、文件读写）"呼应。

---

## 【使用方法】

原文未提供完整的命令行示例或 Python 接口调用范式，但涉及以下启用机制（原文 §4.2.5.1 接口清单抽取）：

- **命令行入口**：调用 `UserCommand Parse(int32_t argc, char **argv)` 解析；输入需符合预先设置的规则，否则解析失败、流程终止并返回 help 信息打印（原文表述）。
- **子进程拉起**：调用 `Process::Launch(const std::vector<std::string>& execParams)`，由框架 `fork` 并通过 `execvpe` 拉起客户脚本；调用前需先设置 `LD_PRELOAD` 变量（原文明确说明）。
- **分析器启用**：通过 `EventDispatcher::Subscribe(const SubscriberId& id, const std::vector<EventBaseType>& eventTypes, const Priority& priority, const HandlerFunc& func)` 注册；可通过 `EventDispatcher::UnSubscribe(const SubscriberId& id)` 解注册。
- **采集范围控制**：通过 `msmemscope_python` 模块设置采集范围和采集项（原文 §4.1.4 采集段表述）。
- **影子采集模式**：通过 `EventTraceManager` 类判断数据是否需要采集，影子事件在 `EventHandler` 的 UpdateMemoryState 阶段处理完毕后跳过后续分发与清理（原文 §4.2.5.1 EventHandler 注意事项）。
- **通信建立**：`ServerProcess::Notify(std::size_t clientId, const std::string& msg)` / `ServerProcess::Wait(std::size_t clientId, std::string& msg)` 基于共享内存，返回值为字节数（>=0 成功、<0 失败，需具备维测或重发机制，原文表述）。

具体的完整命令行清单、参数开关、环境变量名、Python API 函数签名原文未详列，本文不臆造。

## 图文联合解读

- `1a451d58-83b5-4f4d-a09a-0c033012bb18.png`: **图文联合解读：**

图示采用UML用例图，描绘Actor1（用户）驱动**数据采集**与**数据分析**两大核心用例。采集侧按AI框架、CANN、驱动层三类源解耦；分析侧细化为泄漏分析、比对、块监测、拆解、低效识别五个子用例。

该图论证了"采-析分离、模块解耦"的架构结论，与文档"采集插件化、各采集项独立解耦、分析模块支持快速迭代"的设计目标及功能清单一一对应，直观呈现了memscope的功能拓扑。
- `ce97d227-4c20-47bc-b40d-0ca124cc5e7d.png`: **图文联合解读：**

1) **图中内容**：UML组件图，左侧三个绿色组件（Pytorch/CANN/Driver）通过虚线依赖箭头指向中央粉色核心组件 **msleaks**，msleaks 再以 `<<Usage>>` 关系连接右侧黄色 **Insight** 分析组件。

2) **技术结论**：呈现"采集层—聚合层—分析层"三层架构，采集源解耦、msleaks 作为统一数据汇聚枢纽、Insight 承担可视化分析，体现插件化隔离思想。

3) **与文档关系**：直接印证 §3.2 "各采集项独立解耦、便于快速增删扩展"的关键设计目标，呼应"数据采集插件化"DFX 特性。
- `3c7e7422-39ee-430c-a732-b973454702ed.png`: **1) 图内容**：UML组件图，展示三大封装组件——**Tracer**（含hal_mem_hook、memory_pool_hook、kernel_hook、acl_hook、op_hook五个采集Hook）、**Analyzer**（含leak、compare、watch、decompose、inefficient五个分析模块）、**Framework**（cfg_parser与communication）。通过`report`和`analyzer`两个接口实现解耦：Tracer暴露report，Framework调用analyzer。

**2) 技术结论**：采用"采集-框架-分析"三层解耦架构，Hook插件化隔离支撑快速增删采集项；Framework作为中间层统一配置与通信；各分析子模块独立，便于客户自定义逻辑与并行迭代。

**3) 与文档关系**：直接印证文档"数据采集各采集项独立解耦""分析模块支持快速迭代""hook组件隔离便于扩展"的整体设计目标，与DFX中"数据采集插件化"特性严格对应。
- `96abcebd-f98d-4594-9856-17ea7aac212c.png`: # 图文联合解读

## 1) 图中内容
该图为UML类图，左右分两区呈现：
- **左区（绿色，数据采集端）**：`Hooks`（HalMemAlloc/Free、AcInit/Finalize、rtKernelLaunch、AtbHook、AtenHook）→ `EventTraceManager`（IsNeedTrace）→ `EventReport` 单例（各Report方法）；辅以`OpExecuteWatch`+`TensorDumper`（算子级监测）和`MstxManager`（range标注）。
- **右区（粉色，数据分析端）**：`ClientParser`→`Command`→`Process`（含Protocol、EventDispatcher订阅分发）→抽象基类`AnalyzerBase`，派生三具体分析器：`DecomposeAnalyzer`/`InefficientAnalyzer`（含EarlyAllocation、LateDeallocation、TemporarilyIdleness）/`LeakAnalyzer`。
- 中央箭头"内存事件上报工具进程"连接采集与分析两端。

## 2) 技术结论
架构采用**"采集—上报—分析"解耦设计**：采集侧按"Hook→Trace管理→Report"分层，每类事件独立接口；分析侧采用**订阅-分发器+策略模式**（AnalyzerBase为抽象基类），新增分析器只需继承实现EventHandle，体现插件化扩展。

## 3) 与文档论点呼应
- 表格"采集项独立解耦、快速增删"对应各Report方法与Hooks隔离；
- "数据分析支持快速迭代、客户自定义"对应AnalyzerBase派生体系；
- "泄漏分析/显存拆解/低效识别"三大功能分别由三个具体分析器实现，方法名直接对应业务特征（如TemporarilyIdleness对应"临时闲置"）。
- `71dcaade-e055-40e4-901c-ad2e4d5766a3.png`: **图文联合解读：**

1) **图示内容**：流程图描绘"显存比对"完整链路——msleaks拉起命令→client_parser解析→校验命令有效性→双CSV读取与表头校验→按时间排序→Myers算法比对→构建最优图路径与回溯→依kernelLaunch索引回查PTA内存事件→计算内核间内存变化→保存结果文件。

2) **技术结论**：比对模块采用Myers差异算法+最优图路径实现事件对齐，并通过kernelLaunch索引回溯PTA事件，确保内存差异追踪的精准性，失败校验形成闭环。

3) **与文档关系**：该图印证了"显存比对"业务功能的实现路径，支撑文档"数据采集项独立解耦、分析模块快速迭代"的设计目标，体现DFX能力中冒烟框架对主路径的覆盖要求。
- `cbdaa896-d55d-45d3-9b4a-f3b0ec895e52.png`: **图文联合解读：**

**1) 图中内容**：该流程图描述了基于网格的蛇形路径搜索算法。从"开始"初始化最大步数与最优路径数组后，进入循环：遍历第i步可达的K线，判断最优条件决定路径走向（上→下 / 左→右），更新坐标与前驱并创建diff节点；继而判断两kernel name是否一致（是则横纵坐标+1）、是否对角线节点（是则创建snake节点），最终更新最优路径数组并判断是否抵达终点。

**2) 技术结论**：该算法通过分支决策（最优条件判定+节点类型判定）实现了显存差异数据的二维蛇形可视化路径生成，diff节点与snake节点分层构建，体现"显存比对/拆解"的可视化渲染策略。

**3) 与文档关系**：对应文档"显存比对"（多版本差异比对）与"显存拆解"（模块显存可视化）业务功能，印证"数据分析支持快速迭代、可视化展示各模块显存使用情况"的设计目标。
- `a208c7b1-ef2d-4361-aa6e-f46e956f5d8e.png`: **图文联合解读：**

图示呈现memscope工具的UML时序图，主体为用户→命令行→框架→用户程序→信息记录→dump→信息分析七大对象的协作流：①命令行传入参数，框架解析后可选[compare]触发内存比对，或进入主流程创建用户进程；②用户程序进出host/device钩子时由event_trace完成信息回传与记录；③可选[watch_dump]将记录落盘；④分析模块统一执行泄漏/拆解/低效识别，并将告警信息打印至命令行。

**论证结论：** 各模块（采集、记录、dump、分析）解耦独立，通过参数opt分支按需组合调用，验证了文档"采集项独立解耦、分析模块支持快速迭代"的整体设计目标。
- `511a0c05-0460-4695-95cb-d5841afb00c2.png`: **图文联合解读：**

1) **图示内容**：顶部三个绿色框（npu1/2/3 data report）通过实线箭头汇聚至蓝色"share memory(unlock queue)"共享无锁队列，再经实线下达橙色"server(analysis)"分析服务器；右侧虚线引出队列内部结构——水平条带划分为S2C、Head/tail、C2S区段，由"head/tail"指针标注读写位置，底部箭头标注"Flag+PacketHead+RecordBuffer"数据组成。

2) **技术结论**：多NPU端采用无锁共享内存队列并发上报数据，服务端以S2C/C2S双通道+Head/Tail指针机制实现高效异步通信，避免锁竞争开销。

3) **与文档关系**：印证"数据采集项独立解耦、支持快速增删"的整体设计目标——各NPU采集端解耦，经统一队列汇总至分析模块，体现插件化采集与集中式分析的可扩展架构。
