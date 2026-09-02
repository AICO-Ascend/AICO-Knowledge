# MindStudio 26.0.0 Release Notes

> 仓 `release-management` · 路径 `MindStudio/26.0.0/release_notes_en.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/release-management/MindStudio/26.0.0/release_notes_en.md

# MindStudio 26.0.0 Release Notes 一体化深度解读

## 【定位】

本文档是 MindStudio 26.0.0 版本的官方 Release Notes，描述面向 Ascend AI 开发者的全场景一体化开发工具链的版本变更、能力更新与兼容性约束，重点解决 LLM 训练阶段的多核调度低效、RL 失败难以定位、长时训练异常难以感知，以及推理部署阶段的量化适配周期长、在线服务调优困难、算子开发调试周期长、内存问题排查难等核心痛点。

---

## 【技术要点】

1. **工具独立安装/卸载/升级机制** —— MindStudio 26.0.0 的工具链软件不支持从 8.3.0 直接升级到 26.0.0；msProf、msPTI、msMemScope、msServiceProfiler、msKPP、msOpGen、msKL、msSanitizer、msDebug、msOpProf、msTX 共 11 个工具均支持独立安装、卸载、升级。
2. **算子开发工具链扩展** —— msDebug 支持解析 Atlas 350 core dump 文件；msOpprof 与 msSanitizer 支持 shmem 算子库（性能剖析与扫描）；算子调优与异常检测支持 triton 算子；msOpprof 支持 Scalar profile 数据分析；msSanitizer 支持 AscendC API 执行过程检测（LocalTensor 越界场景）。
3. **msProf 采集与解析增强** —— 新增 Python GIL 锁检测（GIL Tracer）；HostToDevice 视图下新增 wait/record event 与 memcpyAsync event 关联；增强 A5 代际硬件级时间线 C 适配，补齐 BIU/UB/CCU 数据解析，新增 chip 2/3/4 的 ACLGraph 场景解析；解除 PMU 解析限制，支持更多 PMU 指标和自定义 PMU 解析。
4. **msprof-analyze 分析能力新增 5 项** —— 算子融合前后性能对比（GE 自动融合与 inductor+triton 自动生成融合算子）、Host 与集群瓶颈自动分析（`free_analysis`、`communication_bottleneck`、慢节点启动检测）、NPU/GPU 跨平台模型分解对比（`calibrate_npu_gpu`）、Recipe 文本化交付物导出（CSV/JSON/Excel）、计算通信重叠线性分析。
5. **msInsight 可视化诊断能力新增 10 项** —— 涵盖 ftrace 数据采集转换、CPU-进程关系可视化、CPU/NPU/NUMA 拓扑可视化、容器-PID 映射可视化、PyTorch snapshot 分析（支持 tens of GB 大快照，用于 RL 场景）、Triton 片上内存使用可视化（UB 移除问题诊断）、Host-Device 内存拷贝分析（按 stream/type 统计）、ACLGraph JSONPrint 可视化（Record/Wait 事件对齐）、Stream 自动合并、用打包 Python 解释器+三方库+集群分析脚本替换 PyInstaller。
6. **msPTI 与 msMonitor 采集轻量化** —— msPTI 新增 CANN Runtime API 采集与 stepTraceV6 解析，降低 `LD_PRELOAD` 依赖；msMonitor 的 npu-monitor 新增 `--filter`（按数据类型/关键字过滤，如 `Kernel`、`Marker`）与 `--duration`（定时自动停止），nputrace 新增 `--async-mode` 异步解析。

---

## 【关键机制与数据】

- **版本配套关系（原文）**：MindStudio 26.0.0 ↔ Ascend HDK 跟随 CANN 部署要求 ↔ CANN 9.0.0 ↔ PyTorch >=2.3。
- **升级约束（原文）**：MindStudio 8.3.0 不支持直接升级到 26.0.0，需直接安装 26.0.0 对应版本。
- **msProf 多核调度与异常检测机制（原文）**：通过 GIL Tracer 采集与转换识别 Python 线程锁竞争导致的性能瓶颈；通过 wait/record event ↔ memcpyAsync event 关联，实现 Host 端调用到 Device 端执行的可追踪链路。
- **msprof-analyze 三类瓶颈定位能力（原文）**：
  - `free_analysis` —— 识别设备上的大空闲块；
  - `communication_bottleneck` —— 识别 Host Bound/Device Bound 成因、慢通信链路、异常慢节点启动；
  - `calibrate_npu_gpu` —— 自动分解 NPU/GPU profile 数据，按模块对齐时间，分析执行时间差异，支撑跨平台性能校准与瓶颈定位。
- **msMemScope OOM 处置机制（原文）**：在 OOM 触发时自动捕获并持久化显存快照，同时保存内存分配请求的完整调用栈；针对 vLLM 提供单命令一键内存分解与按模块/阶段使用分析。
- **msInsight 大规模数据处理能力（原文）**：可处理 tens of GB 级别的 PyTorch Profiler snapshot，并支持 RL 场景下的内存问题诊断。
- **msInsight ACLGraph JSONPrint 显示约束（原文）**：相关 Record 与 Wait 事件同时结束，Wait 事件先于 Record 事件开始，并展示 Record→Wait 的唤醒信息；Stream 合并用于减少前端展示单元数。
- **msPTI 集成轻量化（原文）**：通过改进设备数据源获取方式，最小化对 `LD_PRELOAD` 环境变量的依赖，简化集成。
- **msMonitor 采集控制参数（原文）**：npu-monitor 提供 `--filter`（按数据类型/关键字过滤）与 `--duration`（指定时长后自动停止采集、保存数据并释放资源）；nputrace 提供 `--async-mode` 异步解析（原文该条目说明在文档末尾被截断）。

---

## 【表格解读】

### 表格 1：Software/Hardware Compatibility

| Software/Hardware | Version Requirement |
| ---- | ---- |
| MindStudio | 26.0.0 |
| Ascend HDK Version | Follow CANN deployment requirements |
| CANN Version | 9.0.0 |
| PyTorch Version | >=2.3 |

**解读**：明确本次发布的工具链版本为 MindStudio 26.0.0，配套的 CANN 软件栈版本固定为 9.0.0，PyTorch 仅声明最低版本门槛（>=2.3），Ascend HDK 不在本工具链约束范围内而需跟随 CANN 的部署要求。该表是其他子工具能力生效的前置环境基线。

---

### 表格 2：4.1 Operator Development Toolchain

| No. | Feature | Description |
| ---- | ---- | ---- |
| 1 | msDebug supports parsing Atlas 350 core dump files. | Supports displaying Atlas 350 related registers and variable printing. |
| 2 | msOpprof supports shmem operator library. | Supports obtaining shmem operator profile data. |
| 3 | msSanitizer supports shmem operator library. | Supports scanning shmem operators. |
| 4 | Operator tuning and anomaly detection support triton operators. | Supports triton performance tuning and anomaly detection through operator tools. |
| 5 | msOpprof supports Scalar profile data analysis. | Supports Scalar data display. |
| 6 | msSanitizer supports detection of AscendC API execution process. | Supports operator detection for LocalTensor out-of-bounds scenarios. |

**逐行解读**：
- 第 1 行：msDebug 扩展到 Atlas 350 平台，能解析其 core dump 并展示相关寄存器与变量值，提升事后调试可见性。
- 第 2 行：msOpprof 引入 shmem 算子库的 profile 数据采集，补齐 shared memory 路径算子的性能可视化能力。
- 第 3 行：msSanitizer 在算子扫描维度同步支持 shmem 算子，与第 2 行的 msOpprof 构成"剖析+静态/动态扫描"双能力闭环。
- 第 4 行：算子调优与异常检测从 AscendC 扩展到 triton 算子，性能调优与异常检测能力随算子开发语言生态外延。
- 第 5 行：msOpprof 新增 Scalar 数据类型的 profile 展示，丰富数据类型维度的剖析覆盖。
- 第 6 行：msSanitizer 新增 AscendC API 执行过程检测，专门覆盖 LocalTensor 越界场景，针对性提升算子内存越界排查效率。

---

### 表格 3：4.2 msProbe

| No. | Feature | Description |
| ---- | ---- | ---- |
| 1 | verl training-inference consistency comparison | msProbe supports training and inference data comparison in verl training-inference consistency scenarios. |
| 2 | Dynamic vLLM dump start/stop | msProbe supports dynamic vLLM dump start/stop. |
| 3 | Random behavior check and fixation | msProbe supports engineering random behavior check and random fixation. |

**逐行解读**：
- 第 1 行：在 verl 训练-推理一致性场景下，msProbe 提供训练数据与推理数据的对比能力，支撑 RL 训练链路中训推一致性验证。
- 第 2 行：vLLM 的 dump 行为由静态转为运行时可控，可在运行过程中按需启停 dump，避免一次性大 dump 干扰在线推理。
- 第 3 行：面向工程中的随机性来源，msProbe 支持随机行为检查与随机性固化（fixation），提升调试可复现性。

---

### 表格 4：4.3 msProf

| No. | Feature | Description |
| ---- | ---- | ---- |
| 1 | Python GIL lock detection | Added GIL Tracer collection and conversion support to help identify performance bottlenecks caused by Python thread lock contention. |
| 2 | HostToDevice connection for a wait/record event | Added association connections between wait/record events and memcpyAsync events in the HostToDevice view, facilitating tracking from Host-side calls to Device-side execution. |
| 3 | Enhanced A5 and new chip scenario parsing | Enhanced C-based adaptation of A5 generation inherited hardware-level timeline, supplemented BIU/UB/CCU data parsing, and added ACLGraph scenario parsing support for chip 2/3/4. |
| 4 | Enhanced PMU parsing capability | Removed PMU parsing restrictions, supporting more PMU metrics and custom PMU parsing. |

**逐行解读**：
- 第 1 行：通过新增 GIL Tracer 采集与转换，定位 Python 全局解释器锁竞争导致的性能瓶颈，弥补原 profile 工具在 Python 层线程竞争分析上的盲区。
- 第 2 行：在 HostToDevice 视图中建立 wait/record event 与 memcpyAsync event 之间的关联，把 Host 侧 API 调用与 Device 侧执行连成可追踪链路。
- 第 3 行：补强 A5 代际硬件级时间线的 C 适配层，并补齐 BIU/UB/CCU 三大硬件单元的数据解析；额外新增 chip 2/3/4 上 ACLGraph 场景的解析支持，覆盖更广泛的新代际芯片。
- 第 4 行：解除原有 PMU 解析限制，支持更多 PMU 指标以及用户自定义 PMU 解析，提升硬件微架构级事件的可观察性。

---

### 表格 5：4.4 msprof-analyze

| No. | Feature | Description |
| ---- | ---- | ---- |
| 1 | Performance comparison before and after operator fusion | Added support for comparing performance before and after GE auto-fusion and inductor+triton auto-generated fused operators to directly identify post-fusion time consumption and performance gains to help evaluate auto-fusion strategies. |
| 2 | Automatic analysis of Host and cluster bottlenecks | Added analysis capabilities: `free_analysis`, `communication_bottleneck`, and slow node startup detection. These identify large free blocks on devices, Host Bound/Device Bound causes, slow communication links, and abnormal slow node startup, helping quickly pinpoint cluster performance bottlenecks. |
| 3 | NPU/GPU model breakdown comparison | Added `calibrate_npu_gpu` capability to automatically decompose NPU and GPU profile data, align module-level timings, and analyze exaecution time differences, enabling cross-platform performance calibration and bottleneck localization. |
| 4 | Recipe text deliverable export | Added support for exporting fine-grained analysis results as text-based deliverables (CSV/JSON/Excel). This reduces reliance on database tools and makes it easier to share and view results. |
| 5 | Enhanced computation and communication overlap analysis | Added linearity analysis for compute-communication operator coverage to identify how much compute operators mask communication overhead, helping pinpoint true bottlenecks in training pipelines. |

**逐行解读**：
- 第 1 行：提供 GE 自动融合、induct+triton 自动生成融合算子前后的性能对比能力，量化融合策略带来的耗时收益，辅助融合策略评估。
- 第 2 行：内置三类集群瓶颈分析能力 —— `free_analysis`（大空闲块定位）、`communication_bottleneck`（Host Bound/Device Bound 成因、慢通信链路）、慢节点启动检测，用于快速收敛集群性能问题定位范围。
- 第 3 行：`calibrate_npu_gpu` 自动分解 NPU/GPU profile 并按模块对齐时间，给出执行时间差分析，使跨平台性能校准与瓶颈定位成为内置能力。
- 第 4 行：把细粒度分析结果以 CSV/JSON/Excel 文本形式导出，降低对数据库工具的依赖，方便分发与查看。
- 第 5 行：在原有计算-通信重叠分析基础上引入"线性分析"，量化计算算子掩盖通信开销的程度，定位训练流水线中真正的瓶颈。

---

### 表格 6：4.5 msMemScope

| No. | Feature | Description |
| ---- | ---- | ---- |
| 1 | Out-of-Memory (OOM) information retention | Automatically captures and persists graphics memory snapshots upon OOM detection, along with the full call stack of the memory allocation request. |
| 2 | One-click memory breakdown & snapshot for vLLM | Enables seamless memory decomposition and per-module/phase usage analysis in vLLM with a single command using msMemScope. |

**逐行解读**：
- 第 1 行：在 OOM 触发瞬间自动捕获并持久化显存快照，连同内存分配请求的完整调用栈一并保留，使 OOM 现场可事后追溯，避免因服务崩溃导致现场丢失。
- 第 2 行：针对 vLLM 场景提供 msMemScope 单命令入口，完成内存分解与按模块/阶段的使用分析，简化在线推理服务的内存画像流程。

---

### 表格 7：4.6 msInsight

| No. | Feature Name | Feature Description |
| ---- | ---- | ---- |
| 1 | ftrace data analysis | Provides a simple and easy-to-use trace-cmd collection control tool that can specify CPU control and collection duration, and converts the collected ftrace data into a format directly parsable by MindStudio Insight, facilitating Timeline viewing and automatic analysis of statistical information such as CPU scheduling, interrupts, and process/thread preemption |
| 2 | CPU–process relationship visualization | Enables querying and visualizing the mapping between CPUs and running processes in coarse-grained CPU binding scripts, helping verify the effectiveness of CPU pinning. |
| 3 | CPU/NPU/NUMA 拓扑可视化 | Adds visualization support for displaying CPU, NPU, and NUMA topology relationships. |
| 4 | Container–host PID mapping visualization | Supports core binding analysis scenarios within containers. |
| 5 | msInsight: PyTorch snapshot analysis | Imports and analyzes snapshot files from PyTorch Profiler, offers memory usage details similar to memory_viz, handles large snapshots (tens of GB), and supports memory issue diagnosis in RL scenarios. |
| 6 | Triton on-chip memory usage visualization | Visualizes memory usage during Triton operator development, specifically for diagnosing UB removal issues. |
| 7 | Host–Device memory copy analysis | Provides per-stream, per-type memory copy statistics, detailed operator info per stream/type, and click-to-jump navigation to the corresponding timeline position. |
| 8 | ACLGraph JSONPrint output visualization | Ensures related Record and Wait events end simultaneously, with Wait events starting earlier than Record events, and displays wake-up information from Record to Wait events. |
| 9 | Stream merging for ACLGraph | Automatically merges Stream units to reduce the number of units displayed in the frontend. |
| 10 | Python integration replacing PyInstaller | Replaces PyInstaller with a packaged Python interpreter, third-party libraries used by cluster analysis tools, and the cluster analysis Python script. |

**逐行解读**：
- 第 1 行：提供 trace-cmd 风格的 ftrace 采集控制工具，可指定 CPU 与采集时长，并将采集数据转换为 MindStudio Insight 直接可解析格式，支撑 Timeline 查看与 CPU 调度/中断/进程线程抢占的统计自动分析。
- 第 2 行：在粗粒度 CPU 绑定脚本场景下，提供 CPU 与运行进程的映射查询与可视化，验证 CPU 绑核效果。
- 第 3 行：新增 CPU、NPU、NUMA 三者的拓扑关系可视化，构建异构系统的全局拓扑视图。
- 第 4 行：补充容器内 PID 与宿主机 PID 的映射可视化，补全容器化场景下的核绑定分析链路。
- 第 5 行：导入并分析 PyTorch Profiler 的 snapshot 文件，提供类似 memory_viz 的内存使用细节，支持 tens of GB 级大快照，并支撑 RL 场景下的内存问题诊断。
- 第 6 行：在 Triton 算子开发过程中可视化片上内存使用情况，专门用于诊断 UB 移除类问题。
- 第 7 行：按 stream、type 维度提供 Host-Device 内存拷贝统计及算子级详细信息，支持点击跳转到对应时间线位置。
- 第 8 行：保证相关 Record 与 Wait 事件同时结束，且 Wait 事件先于 Record 事件开始，并显示 Record→Wait 的唤醒信息，强化 ACLGraph 同步关系的可视化表达。
- 第 9 行：自动合并 Stream 单元，减少前端展示单元数量，提升大规模 ACLGraph 场景下的可读性。
- 第 10 行：用打包的 Python 解释器+三方库+集群分析脚本替代 PyInstaller 打包方式，简化集群分析工具的分发与运行依赖。

---

### 表格 8：4.7 msPTI

| No. | Feature | Description |
| ---- | ---- | ---- |
| 1 | Runtime API collection | Added support for CANN Runtime API collection to analyze interface latency and call paths at the Runtime layer. |
| 2 | Reduced `LD_PRELOAD` dependency | Improved device data源 retrieval, minimizing reliance on the `LD_PRELOAD` environment variable for callbacks and collection scenarios, and simplifying integration. |
| 3 | stepTraceV6 parsing | Added support for stepTraceV6 data parsing, enabling collection and analysis for the new step trace format. |

**逐行解读**：
- 第 1 行：新增 CANN Runtime 层 API 的采集能力，用于分析 Runtime 层接口耗时与调用路径，向上补足 API 级性能画像。
- 第 2 行：通过改进设备端数据源获取方式，减少对 `LD_PRELOAD` 环境变量的依赖，简化回调与采集场景的集成。
- 第 3 行：支持 stepTraceV6 新版 step trace 格式的解析，使新版 step trace 数据可被采集与分析。

---

### 表格 9：4.8 msMonitor（原文截断，仅列出已呈现条目）

| No. | Feature | Description |
| ---- | ---- | ---- |
| 1 | npu-monitor: filter by operator name | Added `--filter` to filter collected results by data types and keywords (e.g., `Kernel`, `Marker`), reducing noise and helping users focus on key operators or tracepoints. |
| 2 | npu-monitor: automatic collection by duration | Added `--duration` to automatically stop collection after a specified period, completing data saving and resource release — ideal for timed observation and automated tasks. |
| 3 | nputrace: asynchronous parsing | Added `--async-mode` to ...（原文于此处被截断，未给出完整描述） |

**逐行解读**：
- 第 1 行：npu-monitor 新增 `--filter`，按数据类型与关键字（举例 `Kernel`、`Marker`）过滤采集结果，减少噪声、聚焦关键算子或 tracepoint。
- 第 2 行：npu-monitor 新增 `--duration`，到达预设时长后自动停止采集、保存数据并释放资源，适用于定时观测与自动化任务。
- 第 3 行：nputrace 新增 `--async-mode`（异步解析），但原文关于该特性的完整描述在文档末尾被截断，本节无法基于原文给出完整解读。

---

## 【公式解读】

原文无公式。

---

## 【关联】

原文未提供内部链接（`内部链接: (无)`）。基于文中各章节的命名与功能描述，可识别出的子模块间关系如下：

- **算子开发工具链（第 4.1 节）**：msDebug、msOpprof、msSanitizer 共同服务于"shmem 算子库 + triton 算子 + AscendC API"三类算子场景，构成"剖析 + 静态/动态扫描 + 异常检测"的能力三角。
- **msProbe ↔ msMemScope**：第 4.2 节的"动态 vLLM dump 启停"与第 4.5 节的"vLLM 一键内存分解"共同面向 vLLM 推理服务的可观测性，msProbe 负责行为采样、msMemScope 负责内存画像。
- **msProf ↔ msprof-analyze**：第 4.3 节的采集/解析能力（A5/chip 2/3/4 ACLGraph、PMU、HostToDevice 关联）是第 4.4 节 `free_analysis`、`communication_bottleneck`、`calibrate_npu_gpu`、算子融合对比等分析能力的数据上游。
- **msInsight 与 msProf 数据消费关系**：第 4.6 节 PyTorch snapshot 分析、Host-Device 内存拷贝分析、ACLGraph JSONPrint/Stream 合并均依赖 msProf/上游 profile 采集器提供的数据源。
- **msPTI 与 msProf**：msPTI 在第 4.7 节新增 CANN Runtime API 采集并支持新版 stepTraceV6，与 msProf 共同构成"Runtime API + step trace"的运行时可观测栈。
- **msMonitor 与 msProf**：msMonitor 的 npu-monitor、nputrace 在第 4.8 节提供带过滤与时长的轻量采集能力，与 msProf 形成互补的轻量/重量两级采集路径。

---

## 【使用方法】

- **msMemScope 一键内存分解（vLLM）**：使用 msMemScope 提供的单条命令即可完成 vLLM 内存分解与按模块/阶段使用分析（原文未列出具体命令字面量）。
- **msInsight ftrace 采集**：使用内置的 trace-cmd 风格控制工具，指定 CPU 与采集时长进行 ftrace 采集，并将结果转换为 MindStudio Insight 直接可解析格式（原文未列出具体命令字面量）。
- **npu-monitor 过滤采集**：`--filter` 按数据类型与关键字（如 `Kernel`、`Marker`）过滤采集结果。
- **npu-monitor 定时采集**：`--duration` 在指定时长后自动停止采集、保存数据并释放资源。
- **nputrace 异步解析**：`--async-mode` 启用异步解析（原文该条目说明被截断，具体行为以官方文档为准）。
- **msprof-analyze 内置能力调用**：`free_analysis`、`communication_bottleneck`、`calibrate_npu_gpu` 作为内置分析能力直接调用，支撑大空闲块定位、Host/Device Bound 与慢通信链路诊断、NPU/GPU 跨平台模型分解对比（原文未列出具体 CLI 写法）。
- **版本兼容基线**：使用本版本前需确认环境满足 CANN 9.0.0、PyTorch >=2.3，Ascend HDK 跟随 CANN 部署要求；若当前为 MindStudio 8.3.0，需直接安装 26.0.0 对应版本，不可直接升级。
