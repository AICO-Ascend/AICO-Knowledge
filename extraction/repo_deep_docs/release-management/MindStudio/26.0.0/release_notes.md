# MindStudio 26.0.0 版本说明

> 仓 `release-management` · 路径 `MindStudio/26.0.0/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/release-management/MindStudio/26.0.0/release_notes.md

# MindStudio 26.0.0 版本说明 深度解读

## 【定位】
本篇文档是 MindStudio 26.0.0 版本（昇腾 AI 全流程开发工具链）的官方 changelog，聚焦"大模型训练调优/诊断、推理优化落地、算子开发与可视化诊断"三大核心场景，系统性记录本版本新增特性、变更特性与漏洞修复，并明确与 CANN 9.0.0、PyTorch ≥2.3 等上下游软件的配套关系。

---

## 【技术要点】

1. **配套基线锁定**：MindStudio 26.0.0 必须搭配 CANN 9.0.0，Ascend HDK 跟随 CANN 部署要求；PyTorch ≥2.3；且**不支持从 MindStudio 8.3.0 直接升级到 26.0.0**，需全新安装。
2. **工具独立化运维**：msProf、msPTI、msMemScope、msServiceProfiler、msKPP、msOpGen、msKL、msSanitizer、msDebug、msOpProf、msTX 共 11 个工具均支持独立安装/卸载/升级。
3. **量化算法栈扩展**：msModelSlim 新增 AWQ（含离群值抑制）、Rotation Tune/AdaptRotation、GPTQ；量化精度自动调优基于 vLLM-Ascend + AisBench；多模态覆盖 Qwen2.5-Omni/Qwen3-Omni/Qwen3-VL；LLM 适配 GLM-4.7、GLM-5、Qwen3-Coder、Qwen3.5、DeepSeek-V3.2；并新增 `pack fp4 to uint8` 权重打包能力。
4. **推理服务 Profiling 全链路**：msServiceProfiler 对接 Prometheus、OpenTelemetry、Torch Profiler；支持 vLLM DPLB、SGLang、MindIE TorchProfiler；引入自动 TraceID 生成以做 Trace 关联分析；NPU OOM 异常后等待 30 秒继续调优；配置文件 `config.toml` 支持 JSON 格式与 JSON 内嵌调优脚本。
5. **Profiling 跨平台与可视化**：msprof-analyze 新增 `calibrate_npu_gpu`（NPU/GPU 拆解比对）、`free_analysis`/`communication_bottleneck`/慢节点启动自动分析、Recipe 文本导出（CSV/JSON/Excel）；msProf 新增 Python GIL Tracer、HostToDevice wait/record event 关联连线、A5 代际（含 chip 2/3/4）ACLGraph 解析增强。
6. **可观测性下沉到 Python 脚本层**：msMonitor 新增 Python 轻量采集接口 `from msmonitor import Monitor, ActivityKind`，并把 Python 包重命名为 `mindstudio_monitor-{version}-xxx.whl`；npu-monitor 新增 `--filter`（按 Kernel/Marker 筛选）、`--duration`（按时长自动结束）、`--async-mode`（异步解析）三个命令行参数。

---

## 【关键机制与数据】

> 注：本文档为特性清单型 changelog，原文未给出具体的吞吐/时延/精度数字，以下为原文中明文写出的**机制级**关键参数与流程要点（无原文不臆造）：

- **原文（OOM 处理）**："在检测到 OOM 返回值时，自动捕获并落盘当前显存使用快照，同时记录本次申请的完整函数调用栈"——msMemScope 的 OOM 现场保全机制。
- **原文（vLLM 显存拆解）**："vllm框架下，可以使用本工具进行一键显存拆解，分析模块、阶段的显存占用情况"——msMemScope 与 vLLM 框架集成。
- **原文（run 包命名变更）**：
  - msProf：`Ascend-mindstudio-msprof_version_linux-archxx.run` → `ascend-mindstudio-msprof_version_archxx.run`
  - msPTI：最终统一为 `mindstudio-profiler-tools-interface_version_archxx.run`
  - msMonitor Python 包：`msmonitor_plugin-{version}-xxx.whl` → `mindstudio_monitor-{version}-xxx.whl`
- **原文（时间单位归一）**：`communication_bottleneck` 输出时间统一换算为**微秒**；`blockDim` 表头重命名为 `block Num`。
- **原文（量化优先级）**：`V1 权重描述文件中 model_quant_type 优先级调整（W8A8_DYNAMIC 高于 W8A8）`。
- **原文（snapshot 规模）**：PyTorch snapshot 支持处理"更大（数十 GB 级）"的文件（msInsight）。
- **原文（关键词同步触发）**：ACLGraph JSONPrint 输出要求 "相关的 Record 事件和 Wait 事件能同时结束，且 Wait 事件的起始时间应该小于 Record 时间的起始时间"。
- **原文（敏感层分析）**：msModelSlim 敏感层分析新增 `mse_layer_wise` 指标，并支持 Attention 结构。

---

## 【表格解读】

### 表1：配套关系（参数/版本表）

| 软件/硬件 | 版本要求 |
| ---- | ---- |
| MindStudio | 26.0.0 |
| Ascend HDK版本 | 跟随CANN部署要求 |
| CANN版本 | 9.0.0 |
| PyTorch版本 | >=2.3 |

解读：明确锁定 CANN 9.0.0 与 PyTorch ≥2.3 的下限；HDK 不单独指定版本，而是"跟随 CANN 部署要求"，意味着只要 CANN 部署合规，HDK 自动满足。

---

### 表2：4.1 算子开发工具链 — 新增特性

| 序号 | 特性名称 | 特性描述 |
| ---- | ---- | ---- |
| 1 | msDebug支持Atlas 350core dump文件解析 | 支持展示Atlas 350相关寄存器和变量打印 |
| 2 | msOpprof支持shmem算子库 | 支持通过msopprof获取shmem算子性能数据 |
| 3 | msSanitizer支持shmem算子库 | 支持通过msSanitizer扫描shmem算子 |
| 4 | 算子调优以及异常检测支持triton算子 | 支持通过算子工具进行triton性能调优以及异常检测 |
| 5 | msOpprof支持Scalar性能数据分析 | msopprof支持Scalar数据展示 |
| 6 | msSanitizer支持对AscendC API执行过程的检测 | 支持LocalTensor越界场景的算子检测 |

解读：
- #1 把崩溃现场解析能力扩展到 Atlas 350 硬件平台。
- #2/#3 形成"shmem 算子"的 profiling + sanitizer 闭环（一个看性能、一个扫内存/正确性）。
- #4 把 Triton 算子纳入 msSanitizer/msOpprof 的能力圈，对国产生态兼容 Triton 至关重要。
- #5 补足 Scalar 这一细粒度数据维度。
- #6 重点是 LocalTensor 越界——典型 AscendC UB 内存越界检测。

---

### 表3：4.2 msProbe — 新增特性

| 序号 | 特性名称 | 特性描述 |
| ---- | ---- | ---- |
| 1 | verl训推一致性比对 | msprobe支持verl训推一致性场景下的训练和推理数据比对 |
| 2 | vllm支持动态启停dump | msprobe支持vllm动态启停dump |
| 3 | 随机行为检查和固定 | msprobe支持工程随机行为检查和随机固定 |

解读：msProbe 把比对能力下沉到 RL 框架 verl，把动态 dump 能力下沉到推理框架 vllm，并把"随机性可复现"作为一等公民引入（检查 + 固定）。

---

### 表4：4.3 msProf — 新增特性

| 序号 | 特性名称 | 特性描述 |
| ---- | ---- | ---- |
| 1 | Python GIL 锁检测 | 新增 GIL Tracer 采集与转换能力，可辅助定位 Python 线程锁竞争导致的性能瓶颈 |
| 2 | wait/record 事件 HostToDevice 连线 | 在 HostToDevice 视图中增加 wait/record event 与 memcpyAsync event 的关联连线，便于从 Host 侧调用追踪到 Device 侧执行 |
| 3 | A5与新芯片场景解析增强 | 增强A5代际继承硬件级 timeline 的 C 化适配，补齐 BIU/UB/CCU 等数据解析，并新增 chip 2/3/4 的 ACLGraph 场景解析支持 |
| 4 | PMU 解析能力增强 | 解除 PMU 解析限制，支持更多 PMU 指标与自定义 PMU 场景解析 |

解读：四件事——(a) GIL 竞争可观测；(b) Host↔Device 调用链可视化；(c) A5 代际硬件 timeline C 语言实现并补齐 BIU/UB/CCU 模块及 chip 2/3/4 的 ACLGraph；(d) PMU 自由扩展。

---

### 表5：4.4 msprof-analyze — 新增特性

| 序号 | 特性名称 | 特性描述 |
| ---- | ---- | ---- |
| 1 | 融合算子前后性能对比 | 新增对 GE 自动融合及 inductor+triton 自动生成融合算子的前后性能对比能力，可直接识别融合后耗时占比与性能收益，帮助评估自动融合策略效果 |
| 2 | Host 与集群瓶颈自动分析 | 新增 free_analysis、communication_bottleneck、慢节点启动等分析能力，可识别 Device 大块空闲、Host Bound/Device Bound 原因、通信慢卡及慢节点启动异常，帮助快速定界集群性能瓶颈 |
| 3 | NPU/GPU 模型拆解比对 | 新增 calibrate_npu_gpu 能力，支持对 NPU 与 GPU profiling 数据进行自动拆解、Module 层级对齐和耗时差异分析，用于跨平台性能校准与瓶颈定位 |
| 4 | Recipe 文本交付件导出 | 新增 Recipe 分析能力的 text 类型导出，支持将细粒度分析结果直接导出为 CSV/JSON/Excel 等文本交付件，降低对数据库工具的依赖，便于结果共享与快速查看 |
| 5 | 计算与通信掩盖分析增强 | 新增计算通信算子覆盖线性度分析能力，帮助识别计算算子对通信算子的掩盖程度，辅助定位训练链路中的真实瓶颈 |

解读：构成"融合收益评估 → 集群瓶颈定位 → 跨平台校准 → 文本化交付 → 真实瓶颈挖掘"的完整分析闭环。第 5 项"计算通信算子覆盖线性度"是判断"是否真的被通信掩盖"的关键指标。

---

### 表6：4.5 msMemScope — 新增特性

| 序号 | 特性名称 | 特性描述 |
| ---- | ---- | ---- |
| 1 | 支持OOM场景保留必要信息 | 在检测到 OOM 返回值时，自动捕获并落盘当前显存使用快照，同时记录本次申请的完整函数调用栈 |
| 2 | 新增vllm框架下一键开启msmemscope显存拆解/显存快照功能 | vllm框架下，可以使用本工具进行一键显存拆解，分析模块、阶段的显存占用情况 |

解读：解决"复现 OOM 现场"这一长期痛点，且与 vllm 推理框架做了一键接入。

---

### 表7：4.6 msInsight — 新增特性（10 项）

| 序号 | 特性名称 | 特性描述 |
| ---- | ---- | ---- |
| 1 | MindStudio Insight支持ftrace数据联合分析 | 提供一个简单易用的trace-cmd采集控制工具，能够指定CPU控制和采集时长，并将采集到的ftrace数据转换为MindStudio Insight可直接解析的格式，以便于查看Timeline并自动分析CPU调度、中断及进程/线程打断等统计信息 |
| 2 | 支持展示CPU与运行进程间关系 | 实现在粗粒度绑核脚本中增加查询CPU和运行进程的可视化能力，辅助验证绑核是否生效 |
| 3 | 支持展示CPU/NPU/NUMA拓扑关系 | 增加可视化能力，实现CPU/NPU/NUMA拓扑关系 |
| 4 | 支持展示容器与宿主机之间的 pid 映射关系 | 支持容器内使用绑核分析场景 |
| 5 | MindStudio Insight支持PyTorch框架snapshot分析 | msInsight能够导入和分析PyTorch Profiler生成的snapshot文件，提供类似于memory_viz的内存使用细节查看功能，并且能够处理更大（数十GB级）的snapshot文件，支持强化学习场景下的内存问题定位 |
| 6 | 支持Triton片上内存使用过程可视化 | MSInsight支持展示Triton算子开发过程中UB移除问题的内存情况 |
| 7 | 支持Host-Device间内存拷贝专项分析 | 内存拷贝按流按类型统计、内存拷贝该流按类型查询详细算子信息、算子点击跳转timeline位置 |
| 8 | 支持ACLGraph的JSONPrint输出展示 | 保证相关的Record事件和Wait事件能同时结束，且Wait事件的起始时间应该小于Record时间的起始时间，展现从 Record 事件发向 Wait 事件的唤醒信息 |
| 9 | 支持aclgraph场景下Stream合并 | 实现自动合并 Stream 泳道的功能，从而减少前端需要显示的泳道数量 |
| 10 | 集成Python代替PyInstaller | Python解释器+集群分析工具使用的三方库+集群分析Python脚本 |

解读：本表是本次版本最重的可视化能力增量，10 项特性构成"调度/拓扑/绑核/容器/PyTorch 内存/Triton UB/H2D 拷贝/ACLGraph 序列化"的全栈视图。其中 #10 是工程层面的打包方式切换（PyInstaller → Python 解释器）。

---

### 表8：4.7 msPTI — 新增特性

| 序号 | 特性名称 | 特性描述 |
| ---- | ---- | ---- |
| 1 | Runtime API 采集适配 | 新增对 CANN Runtime API 的采集适配，便于分析 Runtime 层接口耗时与调用链路 |
| 2 | 降低 LD_PRELOAD 依赖 | 改进 device 数据源获取方式，减少 callback 和采集场景对 LD_PRELOAD 环境变量的依赖，提升接入易用性 |
| 3 | stepTraceV6 解析适配 | 新增 stepTraceV6 数据解析适配，补齐新格式 step trace 场景下的采集与分析支持 |

解读：第 2 项降低 LD_PRELOAD 依赖意味着 msPTI 接入门槛显著降低；第 3 项为新版 step trace 数据格式预留适配。

---

### 表9：4.8 msMonitor — 新增特性

| 序号 | 特性名称 | 特性描述 |
| ---- | ---- | ---- |
| 1 | npu-monitor 按算子名称筛选 | 支持通过 --filter 按 Kernel、Marker 等数据类型和关键字筛选采集结果，减少无关数据干扰，便于用户聚焦关键算子或打点信息 |
| 2 | npu-monitor 按时长自动采集 | 新增 --duration 参数，可按指定时长自动结束采集并完成消费、落盘与资源释放，适合定时观测和自动化任务 |
| 3 | nputrace 异步解析 | 新增 --async-mode 参数，在完成采集后由独立流程异步执行解析，降低在线解析对训练或推理主流程的阻塞 |
| 4 | 轻量化 Monitor API 采集接口 | 新增 Monitor Python 接口，支持 start、stop、get_result、save 等调用方式，可采集 API、RuntimeAPI、AclAPI、NodeAPI、Kernel、Communication、Marker 等数据并导出 Excel，便于在脚本中集成轻量性能观测能力 |

解读：4 项全部围绕"采集过程可控、可嵌入、可无人值守"：--filter 降噪、--duration 自动结束、--async-mode 降低主流程阻塞、Python API 嵌入脚本。

---

### 表10：4.9 msModelSlim — 新增特性

| 序号 | 特性名称 | 特性描述 |
| ---- | ---- | ---- |
| 1 | AWQ算法支持与离群值抑制能力增强 | 支持 AWQ 及相关离群值抑制场景，帮助用户在精度与效率之间取得更优平衡 |
| 2 | Rotation Tune/AdaptRotation支持 | 支持 Rotation Tune/AdaptRotation 量化能力，提升高难模型量化稳定性 |
| 3 | GPTQ算法能力完善 | 提供 GPTQ 算法支持及相关资料/参数完善，便于用户按目标场景选择权重量化策略 |
| 4 | 量化精度自动调优能力 | 支持基于 vLLM-Ascend 与 AisBench 的量化精度自动调优，减少手工试参成本 |
| 5 | 一键量化推荐场景优化 | 优化一键量化推荐场景，提升开箱体验与配置命中率 |
| 6 | 敏感层分析能力增强 | 敏感层分析支持 Attention 结构，并补齐 mse_layer_wise 指标实现与说明 |
| 7 | 多模态模型量化扩展 | 支持多模态理解模型量化接入，并覆盖 Qwen2.5-Omni、Qwen3-Omni、Qwen3-VL 等模型 |
| 8 | GLM/Qwen/DeepSeek系列适配扩展 | 持续补齐 GLM-4.7、GLM-5、Qwen3-Coder、Qwen3.5、DeepSeek-V3.2 等模型量化支持 |
| 9 | FP4权重打包能力 | 增加 pack fp4 to uint8 能力，帮助用户在模型交付与部署前进行更高效的权重封装 |

解读：本表是量化能力的全面扩展，覆盖算法（AWQ/Rotation/GPTQ）、自动化（基于 vLLM-Ascend+AisBench）、敏感层（Attention + mse_layer_wise）、模型矩阵（多模态/GLM/Qwen/DeepSeek）、交付（FP4→uint8 打包）五大维度。

---

### 表11：4.10 msServiceProfiler — 新增特性（15 项）

| 序号 | 特性名称 | 特性描述 |
| ---- | ---- | ---- |
| 1 | vLLM 推理服务 Prometheus 监测集成 | 支持对接 Prometheus 监测系统，实现 vLLM 推理服务运行原生的 metrics 数据采集与扩展推理关键指标监测 |
| 2 | 自定义执行时间作为 metric 指标 | 支持将关键执行时间作为 metric 指标自动配置与汇总 |
| 3 | metric 数据动态暂停与标签自动分配 | 支持 metric 数据动态暂停、标签自动分配、同一服务多次采集等灵活配置 |
| 4 | vLLM DPLB 指标数据采集 | 支持 vLLM 推理服务 DPLB（请求分发）指标数据采集与展示 |
| 5 | OpenTelemetry 动态对接 Trace 统一追踪 | 支持对接 OpenTelemetry 动态追踪，实现推理服务进程全链路 Trace 统一追踪能力，支持对单 EP 进程 Trace 信息汇总 |
| 6 | 自动生成 TraceID | 支持自动生成 TraceID，便于跨进程推理服务的 Trace 关联分析 |
| 7 | Torch Profiler 数据采集与解析 | 支持 Torch Profiler 数据采集与解析，增强对框架执行热点、调用栈等细节的分析能力 |
| 8 | vLLM 推理服务自动插桩采集 | 支持对 vLLM 推理服务进行自动插桩采集，实现关键性能数据的无侵入式采集与解析 |
| 9 | SGLang 推理服务采集支持 | 增强对 SGLang 推理框架的采集与解析支持 |
| 10 | MindIE TorchProfiler 支持 | 支持对 MindIE 推理框架的 TorchProfiler 指标采集与解析 |
| 11 | Profiling 数据对比 | 支持 Profiling 数据对比功能，实现关键指标对比、版本对比、趋势对比 |
| 12 | config.toml 支持 JSON 格式 | 自动调优配置文件 config.toml 支持使用 JSON 格式配置，支持 JSON 格式内嵌调优脚本配置 |
| 13 | 结果输出参数约束调优 | 支持将结果输出参数如对比长度等进行压缩约束，限定调优范围 |
| 14 | NPU OOM 异常等待处理 | 支持调优流程中遇到 NPU out of memory 异常后等待 30 秒继续处理 |
| 15 | 推理服务异常状态数据保留 | 支持检测到推理服务进入异常状态后数据保留 |

解读：本表是推理服务侧可观测性的旗舰特性集合。围绕三大标准对接——Prometheus（指标）、OpenTelemetry（Trace）、Torch Profiler（框架热点），覆盖 vLLM/SGLang/MindIE 三大推理框架，并通过 DPLB（请求分发）指标下沉到负载均衡层；#11 提供跨版本/跨指标的趋势对比，#14/#15 强化调优容错。

---

### 表12：4.11 msTX — 新增特性

| 序号 | 特性名称 | 特性描述 |
| ---- | ---- | ---- |
| 1 | 所有仓统一新的优化下载机制 | 优化mstx下载机制 |

解读：仅 1 项，统一所有仓的 mstx 下载机制（具体技术细节原文未展开）。

---

### 表13：5.1 msProbe — 变更特性

| 序号 | 变更内容 | 变更影响 |
| ---- | ---- | ---- |
| 1 | 优化趋势可视化图表 tooltip 样式和数据展示 | 改善 tb_graph_ascend 趋势可视化的数据阅读体验 |
| 2 | dump修改risk_level的默认等级为focus | 减少默认dump的API数量，方便数据分析 |

解读：可视化与默认行为调整；risk_level 默认改为 focus 后默认 dump 量更收敛，便于聚焦关键数据。

---

### 表14：5.2 msProf — 变更特性

| 序号 | 变更内容 | 变更影响 |
| ---- | ---- | ---- |
| 1 | run 包安装与卸载流程调整 | run 包适配安装到 CANN 整包目录，新增 --uninstall 卸载参数，并要求 --install-path 直接指向实际 cann 目录 |
| 2 | run 包命名统一 | **不兼容变更**：run 包文件名由 `Ascend-mindstudio-msprof_version_linux-archxx.run` 调整为 `ascend-mindstudio-msprof_version_archxx.run` |
| 3 | 性能结果展示字段与表头调整 | task_time 支持展示 kernel_name；UB summary 删减冗余字段并调整表头；block Dim 重命名为 block Num |

解读：#2 是显式标注的"不兼容变更"，依赖旧文件名的自动化脚本必须同步修改；#3 也涉及表头/字段名变更，依赖旧字段名的解析脚本需同步更新。

---

### 表15：5.3 msprof-analyze — 变更特性

| 序号 | 变更内容 | 变更影响 |
| ---- | ---- | ---- |
| 1 | export_type 参数语义统一为 text | cluster/recipe 文本交付件统一归类为 text；module_statistic 的导出类型由 excel 调整为 text |
| 2 | 分析结果字段与单位兼容性调整 | communication_bottleneck 输出时间统一换算为微秒；Advisor 适配 blockDim → block Num |

解读：参数语义收敛（excel→text），时间单位归一化为微秒；同样属于需要同步更新解析脚本的兼容性变更。

---

### 表16：5.4 msPTI — 变更特性

| 序号 | 变更内容 | 变更影响 |
| ---- | ---- | ---- |
| 1 | run 包安装与卸载流程调整 | run 包新增 --uninstall 参数，安装脚本适配 CANN 整包构建场景，并补充卸载时删除安装脚本与 whl 包的处理逻辑 |
| 2 | run 包命名规范调整 | **不兼容变更**：run 包名称最终统一为 `mindstudio-profiler-tools-interface_version_archxx.run` |
| 3 | 安装兼容性增强 | 非 root 用户安装场景增加目录权限处理逻辑 |

解读：与 msProf 的 run 包变更对齐思路一致（命名规范 + 安装/卸载流程），#2 同样为不兼容变更。

---

### 表17：5.5 msMonitor — 变更特性

| 序号 | 变更内容 | 变更影响 |
| ---- | ---- | ---- |
| 1 | Python 分发包命名调整 | `msmonitor_plugin-{version}-xxx.whl` → `mindstudio_monitor-{version}-xxx.whl` |
| 2 | 新增脚本内轻量采集使用方式 | 除 dyno 命令行方式外，支持 `from msmonitor import Monitor, ActivityKind` 启停采集、获取结果、导出文件 |

解读：#1 是包名破坏性变更，依赖旧包名的脚本需同步适配；#2 引入 Python API 形态，把 msMonitor 从 CLI 工具扩展为可嵌入脚本的库。

---

### 表18：5.6 msModelSlim — 变更特性

| 序号 | 变更内容 | 变更影响 |
| ---- | ---- | ---- |
| 1 | 移除重复且未经验证的 Qwen3 W8A8 配置（含 pd_mix 相关项） | 配置来源更单一，降低误用风险 |
| 2 | 文档链接与托管路径规范化（相对路径、错误链接修复） | 用户查阅资料时的跳转成功率与定位效率提升 |
| 3 | 敏感层分析相关指标与文档说明完善 | 用户在敏感层分析结果解读和参数选择时更清晰 |
| 4 | V1 权重描述文件中 model_quant_type 优先级调整（W8A8_DYNAMIC 高于 W8A8） | 输出描述信息与真实策略更一致 |

解读：清理 + 文档修复 + 优先级语义修正；#4 的语义调整直接影响用户对量化结果的判读。

---

### 表19：5.7 msServiceProfiler — 变更特性

| 序号 | 变更内容 | 变更影响 |
| ---- | ---- | ---- |
| 1 | 监测模块 metric 采集支持关键指标采集与展示 | 文档使用方式同之前版本，用户无需更新指示即可直接使用 |
| 2 | 推理服务使用方式变更 | README与安装说明文档使用方式进行了部分修订，首次使用请参考最新版本 |
| 3 | MindIE 新版本配套适配 | 对最新 MindIE 版本配套判断逻辑进行调整 |
| 4 | 日志显示优化 | Trace 相关日志显示模块、版本标识等进行了优化 |

解读：#2 是显式的"使用方式变更"提示，首次使用者需查阅最新文档。

---

### 表20：第 6 节 修复漏洞（原文在 "A3上tr" 处截断，不完整）

| 序号 | 问题描述 | 影响范围 |
| ---- | ---- | ---- |
| 1 | 修复某些场景下，finish命令导致工具挂掉问题 | msdebug工具异常退出 |
| 2 | 检测main scalar的非对齐时，LD_LO指令发生漏报 | mssanitizer功能问题 |
| 3 | matmulleakyrelu_kernellaunch算子寄存器设置归零后，用工具拉起后核名称打印错误 | mssanitizer功能问题 |
| 4 | A3上tr...（原文截断） | （原文截断） |

解读：#1 解决 msdebug 偶发挂死；#2/#3 属于 mssanitizer 对 AscendC 算子/Scalar 检测的漏报与核名打印错误；第 4 条及之后原文被截断，无法解读。

---

## 【公式解读】
**原文无公式。**

---

## 【关联】

依据文中内容，可梳理出以下模块/特性间的依赖与上下游关系：

- **配套与升级路径**：MindStudio 26.0.0 ↔ CANN 9.0.0（强配套，HDK 跟随 CANN）↔ PyTorch ≥2.3；不支持从 8.3.0 跨版本升级。
- **算子开发 → 训练/推理 → 可观测性 的闭环**：
  - **算子层**：msDebug（crash 解析）+ msSanitizer（UB/Scalar/AscendC API 检测）+ msOpprof（性能数据 + Scalar + shmem）+ msOpGen（独立安装）→ 输出给训练与推理。
  - **训练侧**：msProf（采集：GIL、HostToDevice、A5 timeline、PMU）→ msprof-analyze（分析：融合算子对比、Host/集群瓶颈、calibrate_npu_gpu、Recipe 文本交付、计算通信掩盖）→ msInsight（可视化：ftrace、CPU/NPU/NUMA 拓扑、ACLGraph、PyTorch snapshot、Triton UB、Host-Device 拷贝）。
  - **推理侧**：msServiceProfiler 对接 vLLM/SGLang/MindIE + Prometheus + OpenTelemetry + Torch Profiler；msMemScope 一键 vLLM 显存拆解 + OOM 现场落盘；msProbe 在 verl/vLLM 中做数据比对与随机行为固定。
  - **量化交付**：msModelSlim（AWQ/Rotation/GPTQ + 敏感层 + FP4 打包）→ 交付给推理服务。
- **msPTI ↔ msProf 的 run 包改造同步**：两者都做了 run 包命名不兼容变更（msProf：`ascend-mindstudio-msprof_version_archxx.run`；msPTI：`mindstudio-profiler-tools-interface_version_archxx.run`），并都新增 `--uninstall` 参数、要求 `--install-path` 直接指向实际 CANN 目录，对齐 CANN 整包构建流程。
- **msMonitor ↔ msPTI/msProf 的采集协同**：msPTI（Runtime API、stepTraceV6、降 LD_PRELOAD）采集底层数据，msProf timeline 解析消费，msMonitor（--filter / --duration / --async-mode + Python API）做在线/嵌入式监测，三者形成"采集 → 解析 → 在线监测"分层。
- **ACLGraph 改进在多处协同**：msProf（chip 2/3/4 ACLGraph 解析）→ msInsight（ACLGraph JSONPrint 展示 + Stream 自动合并）→ msServiceProfiler（vLLM 自动插桩 + OpenTelemetry Trace 关联）。
- **量化与推理联动**：msModelSlim 的量化精度自动调优基于 vLLM-Ascend + AisBench；敏感层分析补齐 `mse_layer_wise` 指标；FP4 打包能力面向推理部署交付。

> 备注：原文未提供内部链接（即文中无 `[link]` 形式的跳转引用）。

---

## 【使用方法】

> 本文档为版本说明/特性清单，**原文未涉及**具体的"启用方式/配置项/命令行参数使用步骤"。仅在新特性/变更特性的描述中**显式提及**了以下可用的命令或 API（属于描述性提及，非教程）：

- **msMonitor 命令行**：
  - `npu-monitor --filter`（按 Kernel/Marker 等数据类型与关键字筛选）
  - `npu-monitor --duration`（按指定时长自动结束采集）
  - `nputrace --async-mode`（异步解析）
- **msMonitor Python API**：
  - `from msmonitor import Monitor, ActivityKind`
  - 调用：`start` / `stop` / `get_result` / `save`；可采集 API、RuntimeAPI、AclAPI、NodeAPI、Kernel、Communication、Marker；导出 Excel。
- **msProf / msPTI run 包**：
  - 新增 `--uninstall` 参数；`--install-path` 需直接指向实际 CANN 目录以对齐 CANN 整包构建流程。
- **msInsight**：
  - 使用 `trace-cmd` 采集 ftrace 并转换为 MindStudio Insight 可解析格式（CPU/时长可控）。
- **msServiceProfiler**：
  - 配置文件 `config.toml` 支持 JSON 格式，并支持 JSON 内嵌调优脚本。
- **msMemScope**：
  - vLLM 框架下一键开启显存拆解/显存快照。

> 原文在第 6 节 修复漏洞 处出现明显截断（以 "A3上tr" 结束），未能给出后续漏洞条目与详细描述；具体启用步骤、版本回滚路径、配置文件位置等**原文未涉及**。
