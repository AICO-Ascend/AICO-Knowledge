# msSanitizer Architecture Design Specifications

> 仓 `mssanitizer` · 路径 `docs/en/development_guide/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mssanitizer/docs/en/development_guide/architecture.md

# msSanitizer 架构设计文档 一体化深度解读

---

## 【定位】

这篇文档描述了 msSanitizer（昇腾 AI 处理器专用异常检测工具）的整体架构设计：它通过**编译器插桩 + 运行时钩子**的协同机制，自动采集算子执行过程中的行为信息并分析异常，覆盖内存越界、对齐错误、未初始化访问、流水线竞争等多种昇腾芯片开发中难以调试的问题。

---

## 【技术要点】

1. **三大异常类别覆盖**：文档将异常划分为「Memory check（内存检查）」、「Race check（竞争检查）」、「Uninitialization check（未初始化检查）」三大类。其中内存检查细分为 7 项（illegal read/write、alignment、multi-core corruption、memory leak、illegal release、unused memory、CANN software stack），竞争检查细分为 3 项（inter-pipeline、intra-pipeline、inter-core race）。

2. **四大核心模块**：系统由 **Framework 进程模块**（命令行解析与 IPC）、**Runtime 运行时模块**（Hook 运行时接口采集行为数据）、**Processor 信息处理模块**（运行检查算法生成报告）、**Check plugin 检查插件模块**（与编译器协作插入检查桩函数）四部分组成。模块间通过 **IPC**（Framework ↔ Runtime）和调用关系（Framework → Processor、Runtime → Plugin）连接。

3. **插件化算法扩展**：设计上采用 **plugin-based architecture** 插件化架构管理检查算法，便于未来支持更多异常类型；并支持 **multi-instance running**——多工具实例在同一主机上并发独立运行互不冲突。

4. **三类并行加速检查时长**：在「Check duration（检查耗时）」维度上设计了三种并行性——**multi-card parallelism**（多卡并行）、**inter-algorithm parallelism**（算法间并行）、**intra-algorithm parallelism**（算法内并行）。

5. **静态 + 动态双插桩机制**：编译器在编译阶段通过 check plugin 插入**静态插桩（static instrumentation）**；运行时模块调用编译器的**动态插桩（dynamic instrumentation）**能力。文档图示中明确这两条调用路径：`kernel -.->|Call the static instrumentation capability.| compile_cli` 和 `sanitizer -.->|Call the dynamic instrumentation capability.| dbi_cli`。

6. **明确的命令行选项控制**：可指定 `--kernel-name` 指定要检查的 kernel、`--block-id` 指定要检查的 block ID、`--cache-size` 指定 GM 内存大小、`--log-file`/`--log-level` 控制报告输出、`--max-debuglog-size` 设置 debug log 大小。

---

## 【关键机制与数据】

**工作原理 / 核心交互过程**（原文第 4 节 "Core interaction process"）：

1. 用户通过命令行调用 msSanitizer 并传入待检查的算子程序。
2. msSanitizer 启动算子程序并 **hook** 运行时接口。
3. 编译器在**编译阶段**通过 check plugin 插入静态插桩。
4. 运行时模块在**执行阶段**采集行为数据并上报。
5. 信息处理模块分析数据、检测异常、向用户报告结果。

**模块数据流（原文表 "Module functions"，表格逐字复现见下节）**：
- **Framework**：输入 = 用户命令行选项；输出 = 检查配置与进程控制
- **Runtime**：输入 = 运行时 API 调用；输出 = 操作信息（operation information）
- **Processor**：输入 = 运行时信息（runtime information）；输出 = 异常检查结果（exception check result）
- **Check plugin**：输入 = 插桩策略查询（instrumentation policy query）；输出 = 桩函数实现（stub function implementation）

**性能数据**：原文未给出具体的耗时数字、内存占用数字或加速比数字，仅在设计目标层面提出「Minimize the check duration」（最小化检查时长）的定性要求。**性能数据原文未涉及**。

---

## 【表格解读】

### 表 1：Functions（1.3 节，原文 13 项 Service + 1 项 Runtime configuration + 1 项 DFX）

| Type | Function | Description | Supported System Feature |
|------|----------|-------------|--------------------------|
| Service | Illegal read/write check | Check for out-of-bounds memory reads/writes on host and kernel. | Memory check → Illegal read/write check |
| Service | Alignment check | Check for alignment of memory reads/writes on kernel. | Memory check → Alignment check |
| Service | Multi-core corruption check | Check for overlapped memory writes from multiple blocks on the device. | Memory check → Multi-core corruption check |
| Service | Memory leak check | Check for memory leaks on the host. | Memory check → Memory leak check |
| Service | Illegal release check | Check for illegal memory release on the host. | Memory check → Illegal release check |
| Service | Unused memory check | Collect statistics on the memory that is allocated but not used. | Memory check → Unused memory check |
| Service | CANN software stack memory check | Check the memory behavior of the CANN software stack. | Memory check → CANN software stack check |
| Service | Inter-pipeline race check | Check the race behavior between pipelines. | Race check → Inter-pipeline race check |
| Service | Intra-pipeline race check | Check the race behavior of instructions in a pipeline. | Race check → Intra-pipeline race check |
| Service | Inter-core race check | Check the instruction race behavior between cores. | Race check → Inter-core race check |
| Service | Uninitialization check | Check the read events on uninitialized memory. | Uninitialization check |
| Service | Exception location information | Display the exception location based on the file name, line number, or call stack. | Exception location |
| Service | Kernel check | Specify the kernel to be checked using `--kernel-name`. | Command line → Runtime options |
| Service | Block check | Specify the ID of the block to be checked using `--block-id`. | Command line → Runtime options |
| Runtime configuration | GM cache resource allocation | Specify the GM memory size using `--cache-size`. | Command line → Runtime options |
| Service | Check report output | Control report output using `--log-file`/`--log-level`. | Command line → Exception report settings |
| DFX | Debug log | Set the debug log size using `--max-debuglog-size`. | Tool debugging → Log settings |

**逐行解读**：
- 表头三列分别表达「功能大类」「具体功能」「功能描述」，第四列「Supported System Feature」对应工具的子系统特性归属。
- 前 7 行属于 **Memory check** 类：覆盖 host 与 kernel 双端的越界读写、kernel 内存对齐、多 block 重叠写、host 内存泄漏、host 非法释放、已分配未使用内存统计，以及 CANN 软件栈自身行为检查。
- 接下来 3 行属于 **Race check** 类：分别针对流水线间、流水线内指令间、core 间指令三种粒度的竞争行为。
- 第 11 行 Uninitialization check 单列一类，检查未初始化内存的读事件。
- 第 12 行 Exception location 提供基于文件名、行号或调用栈的异常定位。
- 第 13–14 行 Kernel/Block check 通过 `--kernel-name` / `--block-id` 让用户**精确选择**被检查对象，从而控制检查范围、避免对所有 kernel/block 全量插桩带来的开销。
- 第 15 行（Runtime configuration）通过 `--cache-size` 控制 GM 缓存资源，体现"运行时分配资源"的配置维度。
- 第 16 行 Check report output 通过 `--log-file`/`--log-level` 控制输出。
- 第 17 行 DFX（Design For X，可调试性）维度仅 1 项 debug log 控制。

---

### 表 2：Overall Design Objectives（2.1 节）

| Design Objective | Description |
|------------------|-------------|
| **Check accuracy** | Prioritize the control of false negative and false positive by analyzing their respective occurrence scenarios. |
| **Operator integration mode** | Cover the runtime interface differences in different operator integration modes to ensure availability. |
| **Easy extension of check algorithms** | Use a plugin-based architecture for check algorithm management to support more exception types in the future. |
| **Check duration** | Minimize the check duration to ensure availability in large-operator, network-wide, and multi-device check scenarios. |
| **Usability of command-line options** | Design options clearly and intuitively to ensure good human-machine interaction experience. |
| **Multi-instance running of tools** | Enable multiple tool instances to run concurrently and independently on a single host without conflicts. |

**逐行解读**：
- **Check accuracy**：优先控制**漏报（false negative）**和**误报（false positive）**，通过分析各自的发生场景实现——这是工具最核心的可用性前提。
- **Operator integration mode**：覆盖 AscendC 单算子、直接算子调用、ACLNN 单算子调用、PyTorch 集成（见 1.2 节）等多种集成方式下运行时接口的差异。
- **Easy extension of check algorithms**：通过 plugin-based 架构管理算法，便于新增异常类型。
- **Check duration**：明确点名三类场景——**大算子（large-operator）**、**网络级（network-wide）**、**多设备（multi-device）**，这些场景都要求检查耗时最小化。
- **Usability of command-line options**：强调命令行选项设计的清晰直观。
- **Multi-instance running**：同一主机上多实例并发且相互独立。

---

### 表 3：Key Element Design（2.2 节）

| Key Element | Design Objectives Involved |
|-------------|---------------------------|
| **Implementation model** | Check accuracy: Ensure accuracy in instruction behavior abstraction and algorithm implementation.<br>Algorithm scalability: Algorithm modules need to be properly abstracted.<br>Algorithm parallelism: multi-card parallelism, inter-algorithm parallelism, and intra-algorithm parallelism |
| **Interaction model** | Operator integration mode: Access different memory information through different integration methods.<br>Command line usability: Clear and intuitive option design |
| **Concurrency model** | Multi-instance running: Ensure that functions of different tools are independent and do not conflict with each other. |

**逐行解读**：
- **Implementation model（实现模型）** 对应三项设计目标：检查精度（指令行为抽象和算法实现的准确性）、算法可扩展性（模块适当抽象）、算法并行性（多卡 / 算法间 / 算法内）。
- **Interaction model（交互模型）** 对应两项：通过不同集成方式访问不同的内存信息（呼应 Operator integration mode）、命令行可用性（清晰直观的选项设计）。
- **Concurrency model（并发模型）** 仅对应 Multi-instance running：保证不同工具实例功能独立、互不冲突。

---

### 表 4：Module functions（3.2 节）

| Module | Function | Key Input/Output |
|--------|----------|------------------|
| **Framework module** | Process control: command line parsing, process startup, and inter-process communication | Input: user command line options; output: check configuration and process control |
| **Runtime module** | Information collection: Hook runtime interfaces to collect user process behavior data. | Input: runtime API calls; output: operation information |
| **Processor module** | Exception analysis: Run the check algorithm to generate a check report. | Input: runtime information; output: exception check result |
| **Check plugin module** | Compilation instrumentation: Collaborate with the compiler to insert check stub functions. | Input: instrumentation policy query; output: stub function implementation |

**逐行解读**：
- Framework 模块承担**进程控制**——命令行解析、进程启动、进程间通信（IPC），对应图 3.1 中 "Framework <-- IPC --> Runtime"。
- Runtime 模块通过 **hook（钩子）** 运行时接口采集用户进程行为数据，是运行时信息采集层。
- Processor 模块运行**检查算法**生成**检查报告**，是离线/在线的分析层。
- Check plugin 模块与编译器协作插入**桩函数（stub function）**，对应静态 + 动态插桩两条路径。
- 四模块的 I/O 链条：用户命令行 → Framework → 启动并控制 Runtime → Runtime 采集行为 → 上报 Framework 转发 Processor → Processor 生成报告 → 返回用户；Check plugin 则在编译阶段被编译器查询插桩策略并提供桩函数实现。

---

### 表 5：Software Units（3.3 节）

| Software Unit | Description | External Interface | Internal Interface | Relationship |
|---------------|-------------|---------------------|---------------------|--------------|
| Framework module | Overall tool process control | Tool command line | Communication server | Provide command lines for users to invoke; transfer data between the communication server and the runtime module; use the information input interface of the information processing module. |
| Runtime module | Collect and upload runtime data. | None | Communication client | Transfer data between the communication client and the framework module; use the dynamic instrumentation plugin to complete the dynamic instrumentation process. |
| Processor module | Perform exception check and output the result. | Exception output | Information input interface | Implement the exception output and information input interfaces to receive data transferred by the framework. |
| Check plugin module | Collaborate with the compiler to complete instrumentation. | Instrumentation query interface and instruction stub implementation | Dynamic instrumentation plugin | Implement the instrumentation query interface for the compiler to query, implement the instruction stub to link to static instrumentation, and implement the dynamic instrumentation plugin for the runtime module to invoke. |

**逐行解读**：
- **Framework** 对外暴露 **Tool command line**，对内提供 **Communication server**，负责与通信客户端（Runtime）以及信息处理模块（Processor）的数据转发。
- **Runtime** 没有外部接口（"None"），仅通过内部 **Communication client** 与 Framework 通信，并使用 check plugin 的 **dynamic instrumentation plugin** 完成动态插桩。
- **Processor** 对外暴露 **Exception output**，对内提供 **Information input interface**，接收 Framework 转发的数据。
- **Check plugin** 对外暴露**两个接口**——**Instrumentation query interface**（供编译器调用）和 **instruction stub implementation**（链接到静态插桩），对内则实现 **dynamic instrumentation plugin** 供 Runtime 调用。这清晰地映射了"静态插桩在编译期完成，动态插桩在运行期被 Runtime 调用"的双轨设计。
- "Relationship" 一列本质上把每个单元承担的协作义务明确写出，便于模块边界划分。

---

## 【公式解读】

原文无公式（无 LaTeX 公式、无伪代码公式形式表达）。**原文无公式**。

---

## 【关联】

由于文档结构较为完整且为 overview 性质，**文末未列出内部链接**（系统提示也确认 "(无)"）。但从文档内容本身可以梳理以下内部关联：

1. **应用场景 ↔ 检查能力映射**：
   - 「AscendC Single-Operator Scenario」（1.2 节）对应 Kernel/Block 级细粒度检查（`--kernel-name`、`--block-id`，表 1 第 13–14 行）。
   - 「ACLNN / PyTorch 集成场景」（1.2 节）对应 Operator integration mode（表 2），通过 Interaction model 抽象多接入方式的内存信息差异。

2. **三大异常类别 ↔ 模块归属**：
   - Memory check → Runtime 模块采集内存行为 → Processor 模块分析（表 4 数据流）。
   - Race check（inter/intra-pipeline、inter-core）→ 与 on-chip memory、core 调度相关（1.1 节背景），需 Runtime 在执行阶段采集指令事件后由 Processor 分析。
   - Uninitialization check → 单独一类，需结合静态/动态插桩记录初始化事件。

3. **设计目标 ↔ 关键要素 ↔ 架构形态**：
   - Check accuracy → Implementation model（指令行为抽象准确性）
   - Algorithm scalability → plugin-based architecture → Check plugin 模块
   - Check duration → multi-card / inter-algorithm / intra-algorithm parallelism → 在 Implementation model 中定义
   - Multi-instance running → Concurrency model → Framework ↔ Runtime 通过 IPC 隔离

4. **静态 vs 动态插桩双轨**：
   - 静态插桩：编译器 + check plugin 的 **instruction stub implementation**（Software Units 表第 4 行 External Interface）
   - 动态插桩：Runtime 通过 check plugin 的 **dynamic instrumentation plugin**（同表 Internal Interface）在执行期调用
   - 二者最终都把采集到的数据汇入 Processor 进行分析。

5. **CANN 软件栈 ↔ 单独检查项**：表 1 中 "CANN software stack memory check" 独立成项（1.2 节应用场景也单独列出 "CANN software stack memory check"），表明该工具不仅检算子，也检 CANN 自身的内存行为。

---

## 【使用方法】

原文在表 1、表 2 中**明确给出了可用的命令行选项**，汇总如下：

| 选项 | 用途 | 原文条目 |
|------|------|----------|
| `--kernel-name` | 指定要检查的 kernel（Service: Kernel check） | "Specify the kernel to be checked using `--kernel-name`" |
| `--block-id` | 指定要检查的 block ID（Service: Block check） | "Specify the ID of the block to be checked using `--block-id`" |
| `--cache-size` | 指定 GM 内存大小（Runtime configuration: GM cache resource allocation） | "Specify the GM memory size using `--cache-size`" |
| `--log-file` / `--log-level` | 控制报告输出（Service: Check report output） | "Control report output using `--log-file`/`--log-level`" |
| `--max-debuglog-size` | 设置 debug log 大小（DFX: Debug log） | "Set the debug log size using `--max-debuglog-size`" |

**调用流程（原文第 4 节 Core interaction process）**：
1. 用户通过命令行调用 msSanitizer 并**传入待检查的算子程序**；
2. msSanitizer 启动算子程序并 hook 运行时接口；
3. 编译器在编译阶段通过 check plugin 插入静态插桩；
4. Runtime 模块在执行阶段采集行为数据并上报；
5. Processor 模块分析数据、检测异常、向用户返回检查结果。

**关于配置文件、环境变量、API 调用形式的启用方式**：**原文未涉及**——文档仅说明工具通过命令行调用并以命令行选项控制行为，未描述其他启用方式。

## 图文联合解读

- `mssanitizer_system_architecture.png`: **图文联合解读：**

**1）图示内容：** 架构图分三层。底层为Ascend芯片及BiSheng编译器（DWARF增强lineinfo）和Runtime；中间层为Check Tool（User Program遍历→Check Module：语言层/公共Stub/信息协同）和Operator Check（命令解析→应用流控→算法管理：Memory/Race/Synchronization）；顶层为Check plugins与信息展示（DWARF/Summary解析）。

**2）技术结论：** 系统通过"编译器插桩+运行时Stub接管"双引擎，在Host侧插桩用户程序、在Device侧通过API Stub拦截核内调用，配合DWARF行号定位异常，覆盖越界、对齐、多核竞争等检测。

**3）与文档关系：** 图印证了"compile instrumentation + runtime hooking"的设计论点，结构化的Check Module与Algorithm Management对应文档列出的非法读写、对齐、多核冲突三类服务功能。
