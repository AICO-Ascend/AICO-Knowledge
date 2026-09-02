# 环境变量列表

> 来源 https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0001.html
> 抓取路由 hiascend-source · 2026-09-02 17:37 · 原文 20896 字符 · 1 图
> MiniMax-M3 七节深读 · ver=v1 · 原文: extraction/web_docs/ascend-cann-commercial-envvars.md

# CANN 900 环境变量参考页面深度解读

## 【定位】

本文档是 **CANN 商用版 900** 在"环境变量"模块的总索引页（入口），按功能大类罗列开发者基于 CANN 构建 AI 应用与业务过程中**全部可使用的环境变量名与简要说明**，并以表格形式分组指向各环境变量的详细子页面，供开发者在安装配置、图编译/执行、算子编译/执行、集合通信、性能调优、日志与故障采集等场景中按需查阅。

---

## 【技术要点】

1. **环境变量设置方式**：原文列出 4 类机制 — `export` 命令、`putenv/getenv/setenv/unsetenv/clearenv` 函数、`os.environ`、`os.getenv` 等。
2. **设置时机约束**：原文明确"建议用户在应用进程拉起前设置环境变量，否则可能引起环境变量访问冲突，导致程序异常"。
3. **范围声明**：原文明确"本手册不包含 Ascend Extension for PyTorch 的环境变量"，指向独立文档。
4. **算子编译缓存默认保留比例**：`ASCEND_REMAIN_CACHE_SIZE_RATIO` 默认值为 **50**，单位为百分比。
5. **集合通信共享数据缓存区**：`HCCL_BUFFSIZE` 取值整数，**≥1**，默认值 **200**，单位 **MB**。
6. **RDMA 重传次数**：`HCCL_RDMA_RETRY_CNT` 取值整数，范围 **[1, 7]**，默认值 **7**。
7. **Trace 日志老化规格**：`ASCEND_TRACE_RECORD_NUM` 取值范围 **[10, 1000]**。
8. **Host 网卡端口占用数**：原文写"配置后系统默认占用以该端口起始的 **32 个端口**"用于集群信息收集（`HCCL_IF_BASE_PORT`）。
9. **TensorFlow 控制流版本差异**（原文写出 V1/V2 控制流算子对照清单）：
   - V1：`Switch、Merge、Enter、LoopCond、NextIteration、Exit、ControlTrigger` — 不支持动态 shape。
   - V2：`If、Case、While、For、PartitionedCall` — 支持动态 shape。
10. **HF32 覆盖范围**：`ENABLE_HF32_EXECUTION` 当前版本**仅针对 Conv 类算子与 Matmul 类算子**生效。

---

## 【关键机制与数据】

- **配置语义（原文）**：本手册"描述开发者基于 CANN 构建 AI 应用和业务过程中可使用的环境变量"，覆盖从安装落盘、模型/图编译、算子执行、Host 侧缓存、分布式集合通信、性能数据采集到日志与故障 Dump 的全链路。
- **分组语义（原文）：** 按职责归类 — 安装配置、图编译、算子编译、资源配置、算子执行、图执行、TFAdapter、集合通信（再细分功能 / 性能 / 网络 / 调试 / 可靠性 / 安全 6 个子维度）、AOE 调优、AMCT 模型压缩、性能数据采集、日志、故障信息收集、后续版本废弃环境变量。
- **集合通信默认端口占用范围（原文）：** `HCCL_IF_BASE_PORT` 配置后系统默认占用以该端口起始的 32 个端口。
- **网络层可选链路（原文）：** `HCCL_INTRA_PCIE_ENABLE`（Server 内 PCIe）、`HCCL_INTRA_ROCE_ENABLE`（Server 内/超节点内 RoCE）、`HCCL_INTER_HCCS_DISABLE`（超节点内通信链路类型控制）。
- **归约保序概念（原文）：** 文中将"归约保序"定义为"严格的确定性计算，在确定性的基础上保证归约顺序一致"，归约类算子包括 `AllReduce、ReduceScatter、ReduceScatterV、Reduce`。
- **算子重执行粒度（原文）：** `HCCL_OP_RETRY_ENABLE` / `HCCL_OP_RETRY_PARAMS` 重执行以**通信域**为粒度，触发条件为通信算子报 **SDMA 或 RDMA CQE 类型错误**。
- **多流并发默认值（原文）：** `ENABLE_DYNAMIC_SHAPE_MULTI_STREAM` 注明"当前多流并发执行功能默认关闭"，仅动态 shape 图模式下可开。
- **TFAdapter 适用版本（原文）：** 部分变量仅在特定 TF 版本生效，例如 `ENABLE_FORCE_V2_CONTROL`、`ENABLE_HF32_EXECUTION`、`STEP_NOW`、`TOTAL_STEP`、`LOSS_NOW`、`TARGET_LOSS` 标注"TensorFlow 1.15"；`NPU_DEBUG`、`NPU_DUMP_GRAPH`、`NPU_ENABLE_PERF`、`NPU_LOOP_SIZE` 标注"TensorFlow 2.6.5"。
- **A3 超节点（原文）：** `HCCL_LOGIC_SUPERPOD_ID` 注释中点名 "针对 Atlas A3 训练系列产品 / Atlas A3 推理系列产品 的超节点模式组网"，用于将一个物理超节点划分为多个逻辑超节点。
- **昇腾内存复用（原文）：** "计算图在昇腾平台编译的过程中默认采用内存复用形式" — 因此 `OP_NO_REUSE_MEM` 是为"问题定位场景"提供的反向开关。
- **权限与路径自动创建（原文）：** `NPU_COLLECT_PATH`、`ASCEND_DUMP_PATH` 注明"执行用户需对该路径具有读、写、可执行权限，若路径不存在，系统会自动创建该路径中的目录"；`ASCEND_DUMP_PATH` 还给出路径字符集约束（字母、数字、`_`、`-`、`.`、中文字符）。

> 原文未涉及具体的版本演进表或不同 CANN 900 小版本之间的差异说明。

---

## 【表格解读】

下文按原文分组**逐字还原**（变量名、链接锚文本、简介全部原样保留，仅作分组归并说明）。

### 1) 安装配置相关（原文表格逐字还原）

| 环境变量 | 简介 |
| --- | --- |
| [ASCEND_CACHE_PATH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0006.html) | 若开发者期望编译运行过程中产生的文件落盘到归一路径，可通过此环境变量设置**共享文件**的存储路径，各组件编译运行过程中产生的可共享文件会存储到此环境变量定义的路径中。 |
| [ASCEND_WORK_PATH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0007.html) | 若开发者期望编译运行过程中产生的文件落盘到归一路径，可通过此环境变量设置**单机独享文件**的存储路径，各组件编译运行过程中产生的单机独享文件会存储到此环境变量定义的路径中。 |
| [ASCEND_CUSTOM_OPP_PATH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0147.html) | 用户自定义算子包安装路径。开发者编译生成的自定义算子包需要安装到指定路径下时，需要配置该路径。 |

**归类解读**：前两条构成"归一落盘路径"对照 — `ASCEND_CACHE_PATH` 管**跨组件共享文件**，`ASCEND_WORK_PATH` 管**单机独享文件**；第三条是自定义算子包安装路径。

### 2) 图编译（原文表格逐字还原）

| 环境变量 | 简介 |
| --- | --- |
| [DUMP_GE_GRAPH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0011.html) | 把整个流程中各个阶段的图描述信息打印到文件中，此环境变量控制dump图的内容多少。 |
| [DUMP_GRAPH_LEVEL](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0012.html) | 把整个图编译流程中各个阶段的图描述信息打印到文件中。 |
| [DUMP_GRAPH_FORMAT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0155.html) | 控制需要生成的dump文件类型。 |
| [DUMP_GRAPH_PATH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0013.html) | 指定DUMP图文件的保存路径，可配置为绝对路径或脚本执行目录的相对路径。 |
| [OP_NO_REUSE_MEM](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0014.html) | 计算图在昇腾平台编译的过程中默认采用内存复用形式，在问题定位场景中，如果开发者怀疑是内存复用错误导致计算结果异常，可通过此环境变量指定为某算子单独分配内存。 |
| [ASCEND_ENGINE_PATH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0015.html) | 单算子JSON文件转换成离线模型场景，如果希望模型转换时只使用TBE算子（不查找AI CPU算子，找不到TBE算子则报错），则需要使用该环境变量。 |
| [MAX_COMPILE_CORE_NUMBER](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0016.html) | 此环境变量用于指定图编译时可用的CPU核数。 |
| [MULTI_THREAD_COMPILE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0017.html) | 此环境变量用于控制模型转换时是否使用单线程编译。 |
| [ENABLE_NETWORK_ANALYSIS_DEBUG](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0018.html) | TensorFlow训练场景下，计算图编译失败时默认会终止训练流程，不会继续向Device下发剩余的图。若开发者希望图编译失败时，不终止训练流程，允许TF Adapter持续向Device下发计算图，可通过设置该环境变量实现。 |

**归类解读**：
- **Dump 三件套** — `DUMP_GE_GRAPH`（控制 dump 量）/ `DUMP_GRAPH_LEVEL`（阶段图）/ `DUMP_GRAPH_FORMAT`（dump 文件类型）/ `DUMP_GRAPH_PATH`（保存路径）。
- **内存复用关闭开关** — `OP_NO_REUSE_MEM`。
- **算子查找策略** — `ASCEND_ENGINE_PATH` 强制走 TBE，找不到则报错（不兜底 AI CPU）。
- **编译并行控制** — `MAX_COMPILE_CORE_NUMBER` 控制 CPU 核数；`MULTI_THREAD_COMPILE` 控制是否单线程。
- **TF 训练容错** — `ENABLE_NETWORK_ANALYSIS_DEBUG` 仅在 TF 训练下让图编译失败不终止流程。

### 3) 算子编译（原文表格逐字还原）

| 环境变量 | 简介 |
| --- | --- |
| [TE_PARALLEL_COMPILER](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0020.html) | 网络模型较大时，可通过配置此环境变量开启算子的并行编译功能。 |
| [ASCEND_MAX_OP_CACHE_SIZE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0021.html) | 启用算子编译缓存功能时，可通过此环境变量限制某个AI处理器下缓存文件夹的磁盘空间的大小。 |
| [ASCEND_REMAIN_CACHE_SIZE_RATIO](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0022.html) | 启用算子编译缓存功能时，当编译缓存空间大小达到ASCEND_MAX_OP_CACHE_SIZE而需要删除旧的kernel文件时，系统需要保留缓存的空间大小比例，默认为50，单位为百分比。 |
| [IGNORE_INFER_ERROR](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0142.html) | 算子入图时，跳过算子原型交付件校验的开关。交付件包括shape推导等算子入图适配函数的实现。 |

**归类解读**：
- **编译缓存容量控制对** — `ASCEND_MAX_OP_CACHE_SIZE` 定义上限（容量），`ASCEND_REMAIN_CACHE_SIZE_RATIO` 定义回收后保留比例（默认 50%）。
- **编译并行** — `TE_PARALLEL_COMPILER` 针对"网络模型较大"时开启算子级并行。
- **原型交付件校验** — `IGNORE_INFER_ERROR` 是"跳过 shape 推导等入图适配函数实现校验"的开关。

### 4) 资源配置（原文表格逐字还原）

| 环境变量 | 简介 |
| --- | --- |
| [ASCEND_DEVICE_ID](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0027.html) | 指定当前进程所用的AI处理器的逻辑ID。 |
| [ASCEND_RT_VISIBLE_DEVICES](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0028.html) | 指定哪些Device对当前进程可见，支持一次指定一个或多个Device ID。通过该环境变量，可实现不修改应用程序即可调整所用Device的功能。 |
| [AUTO_USE_UC_MEMORY](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0029.html) | 控制系统是否允许算子搬移数据不经过L2 Cache的功能。 |
| [RESOURCE_CONFIG_PATH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0133.html) | 用于设置配置异构资源描述信息文件的存储路径。 |

**归类解读**：
- **Device 选择两层** — `ASCEND_DEVICE_ID`（单卡逻辑 ID）vs `ASCEND_RT_VISIBLE_DEVICES`（可见设备集合，免改应用换卡）。
- **数据通路策略** — `AUTO_USE_UC_MEMORY` 控制是否旁路 L2 Cache。
- **异构资源描述** — `RESOURCE_CONFIG_PATH` 指向异构资源描述信息文件。

### 5) 算子执行（原文表格逐字还原）

| 环境变量 | 简介 |
| --- | --- |
| [ACLNN_CACHE_LIMIT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0031.html) | 此环境变量用于配置aclnn API在Host侧缓存的算子信息条目个数。缓存的算子信息包含workspace大小、算子计算的执行器、Tiling信息等。 |

**归类解读**：通过条目数控制 aclnn API 在 Host 侧的算子信息缓存规模，缓存要素为 workspace 大小、执行器、Tiling 信息三类。

### 6) 图执行（原文表格逐字还原）

| 环境变量 | 简介 |
| --- | --- |
| [ENABLE_DYNAMIC_SHAPE_MULTI_STREAM](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0033.html) | 计算图执行时，开启多流并发执行功能在一定场景下可提升网络性能。当前多流并发执行功能默认关闭，动态shape图模式场景下，若开发者想开启多流并发执行功能，可通过此环境变量开启。 |
| [MAX_RUNTIME_CORE_NUMBER](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0034.html) | 训练与在线推理场景下，针对动态shape图模式执行的网络，可通过设置此环境变量开启图执行器（Host侧）的多线程任务调度。 |

**归类解读**：两者均针对"动态 shape 图模式"运行时 — `ENABLE_DYNAMIC_SHAPE_MULTI_STREAM` 改 Device 多流并发，`MAX_RUNTIME_CORE_NUMBER` 改 Host 侧多线程调度。

### 7) TFAdapter（原文表格逐字还原）

| 环境变量 | 简介 |
| --- | --- |
| [JOB_ID](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0036.html) | TensorFlow训练与在线推理场景下，可通过此环境变量自定义任务ID。 |
| [ENABLE_FORCE_V2_CONTROL](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0037.html) | TensorFlow 1.15训练场景下，如果输入是动态shape，由于tf.case/tf.cond/tf.while_loop这些API对应TensorFlow V1版本的控制流算子（例如Switch、Merge、Enter、LoopCond、NextIteration、Exit、ControlTrigger等）不支持动态shape，仅TensorFlow V2版本的控制流算子（例如If、Case、While、For、PartitionedCall等）支持动态shape，因此，如果用户的训练脚本中使用了这些API，需要将V1版本的控制流算子转换为V2版本，用于支持动态shape功能。另外，如果网络中的分支结构较多，采用V1版本的控制流算子可能导致流数超限，此时也需要将V1版本的控制流算子转换成V2版本算子解决。 |
| [ENABLE_HF32_EXECUTION](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0038.html) | 针对TensorFlow 1.15网络，是否启用HF32自动代替FP32数据类型的功能，当前版本此环境变量仅针对Conv类算子与Matmul类算子生效。 |
| [NPU_DEBUG](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0039.html) | TensorFlow 2.6.5训练与在线推理场景下，用于开启TF Adapter的Debug级别执行日志。 |
| [NPU_DUMP_GRAPH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0040.html) | TensorFlow 2.6.5训练与在线推理场景下，用于开启TF Adapter图Dump功能。 |
| [NPU_ENABLE_PERF](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0041.html) | TensorFlow 2.6.5训练与在线推理场景下，用于开启TF Adapter图耗时打印功能。 |
| [NPU_LOOP_SIZE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0042.html) | TensorFlow 2.6.5训练与在线推理场景下，用于设置NPU上循环下沉的次数。 |
| [STEP_NOW](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0043.html) | TensorFlow 1.15训练场景下，若通过"experimental_accelerate_train_mode"参数或者"accelerate_train_mode"参数触发了训练加速功能，可通过此环境变量设置NPU上当前的执行步数。 |
| [TOTAL_STEP](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0044.html) | TensorFlow 1.15训练场景下，若通过"experimental_accelerate_train_mode"参数或者"accelerate_train_mode"参数触发了训练加速功能，可通过此环境变量设置NPU上总训练步数。 |
| [LOSS_NOW](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0045.html) | TensorFlow 1.15训练场景下，若通过"experimental_accelerate_train_mode"参数或者"accelerate_train_mode"参数触发了训练加速功能，可通过此环境变量设置NPU上当前迭代的loss值。 |
| [TARGET_LOSS](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0046.html) | TensorFlow 1.15训练场景下，若通过"experimental_accelerate_train_mode"参数或者"accelerate_train_mode"参数触发了训练加速功能，可通过此环境变量设置NPU上的目标训练loss值。 |
| [RANK_TABLE_FILE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0047.html) | TensorFlow分布式训练或推理场景下，通过此环境变量指定参与集合通信的AI处理器的rank table资源配置文件，包含rank table文件路径和文件名。 |
| [RANK_ID](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0048.html) | TensorFlow分布式训练或推理场景下，通过此环境变量指定当前进程在集合通信进程组中对应的rank标识。 |
| [RANK_SIZE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0049.html) | TensorFlow分布式训练或推理场景下，通过此环境变量指定当前训练进程对应的Device数量。 |
| [CM_CHIEF_IP](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0050.html) | TensorFlow分布式训练场景下，用户可以选择不使用rank table文件，通过组合使用环境变量的方式自动生成资源信息，完成集合通信初始化。  本环境变量用于配置Master节点的监听Host IP。 |
| [CM_CHIEF_PORT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0051.html) | 本环境变量用于配置Master节点的监听端口。 |
| [CM_CHIEF_DEVICE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0052.html) | 本环境变量用于指定Master节点中统计Server端集群信息的Device逻辑ID。 |
| [CM_WORKER_SIZE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0053.html) | 本环境变量用于配置本次业务通信域Device的数量。 |
| [CM_WORKER_IP](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0054.html) | 本环境变量用于配置当前Device和Master节点进行信息交换时所用的网卡IP。 |

**归类解读**（按 TFAdapter 子主题归并）：
- **任务 ID**：`JOB_ID`。
- **TF 1.15 控制流兼容**：`ENABLE_FORCE_V2_CONTROL`（V1→V2 控制流转换，覆盖动态 shape 与流数超限两类触发条件）。
- **TF 1.15 数据类型替代**：`ENABLE_HF32_EXECUTION`（仅作用于 Conv / Matmul）。
- **TF 1.15 训练加速控制四元组**：`STEP_NOW` / `TOTAL_STEP` / `LOSS_NOW` / `TARGET_LOSS`（前置条件是启用 `experimental_accelerate_train_mode` 或 `accelerate_train_mode`）。
- **TF 2.6.5 调测四件套**：`NPU_DEBUG`（Debug 日志）、`NPU_DUMP_GRAPH`（图 Dump）、`NPU_ENABLE_PERF`（图耗时）、`NPU_LOOP_SIZE`（循环下沉次数）。
- **TF 分布式 rank 三件套**：`RANK_TABLE_FILE` / `RANK_ID` / `RANK_SIZE`。
- **TF 分布式 "无 rank table" CM_* 替代组**：`CM_CHIEF_IP` / `CM_CHIEF_PORT` / `CM_CHIEF_DEVICE`（Master 侧）+ `CM_WORKER_SIZE` / `CM_WORKER_IP`（Worker 侧）— 原文说明"通过组合使用环境变量的方式自动生成资源信息"。

### 8) 集合通信 — 功能相关（原文表格逐字还原）

| 环境变量 | 简介 |
| --- | --- |
| **功能相关** | |
| [HCCL_CONNECT_TIMEOUT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0077.html) | 分布式训练或推理场景下，用于限制不同设备之间socket建链过程的超时等待时间。不同设备进程在集合通信初始化之前由于其他因素会导致执行不同步。该环境变量控制设备间的建链超时等待时间，在该配置时间内各设备进程等待其他设备建链同步。 |
| [HCCL_EXEC_TIMEOUT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0078.html) | 不同设备进程在分布式训练或推理过程中存在卡间执行任务不一致的场景（如仅特定进程会保存checkpoint数据），通过该环境变量可控制设备间执行时同步等待的时间，在该配置时间内各设备进程等待其他设备执行通信同步。 |
| [HCCL_ALGO](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0079.html) | 此环境变量用于配置集合通信Server间通信算法以及超节点间通信算法，支持全局配置算法类型与按算子配置算法类型两种配置方式。 |
| [HCCL_BUFFSIZE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0080.html) | 此环境变量用于控制通信域所使用的共享数据缓存区大小。需要配置为整数，取值大于等于1，默认值为200，单位MB。 |
| [HCCL_INTRA_PCIE_ENABLE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0081.html) | 用于配置Server内是否使用PCIe链路进行通信。 |
| [HCCL_INTRA_ROCE_ENABLE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0082.html) | 用于配置Server内或超节点内是否使用RoCE链路进行通信。 |
| [HCCL_INTER_HCCS_DISABLE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0083.html) | 此环境变量用于配置超节点模式组网中超节点内的通信链路类型，支持如下取值： |
| [HCCL_OP_EXPANSION_MODE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0096.html) | 该环境变量用于配置通信算子的展开模式。 |
| [HCCL_DETERMINISTIC](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0099.html) | 此环境变量用于配置是否开启归约类通信算子的确定性计算或保序功能，其中归约类通信算子包括AllReduce、ReduceScatter、ReduceScatterV、Reduce，归约保序是指严格的确定性计算，在确定性的基础上保证归约顺序一致。 |
| [HCCL_LOGIC_SUPERPOD_ID](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0100.html) | 针对 Atlas A3 训练系列产品 / Atlas A3 推理系列产品 的超节点模式组网，若不使用rank table文件配置集群资源信息，可通过此环境变量指定当前节点运行进程所属的超节点ID，实现将一个物理超节点划分为多个逻辑超节点的功能。 |

### 9) 集合通信 — 性能相关（原文表格逐字还原）

| 环境变量 | 简介 |
| --- | --- |
| **性能相关** | |
| [HCCL_RDMA_PCIE_DIRECT_POST_NOSTRICT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0093.html) | 多机通信且Host操作系统小页内存页表大小非4KB的场景，当通信算子下发性能Host Bound时，开发者可设置此环境变量，通过PCIe Direct的方式提交RDMA任务，提升通信算子下发性能。 |
| [HCCL_RDMA_QPS_PER_CONNECTION](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0094.html) | 两个rank之间RDMA通信时会默认创建1个QP（Queue Pair）进行数据传输，若开发者想让两个rank之间的RDMA通信使用多个QP，可通过此环境变量实现。 |
| [HCCL_RDMA_QP_PORT_CONFIG_PATH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0141.html) | 两个rank之间RDMA通信时会默认创建1个QP（Queue Pair）进行数据传输，若开发者想让两个rank之间的RDMA通信使用多个QP，并指定多QP通信时使用的源端口号，可通过此环境变量实现。 |
| [HCCL_MULTI_QP_THRESHOLD](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0095.html) | rank间RDMA通信使用多QP通信的场景下，开发者可通过本环境变量设置每个QP分担数据量的最小阈值。 |

### 10) 集合通信 — 网络相关（原文表格逐字还原）

| 环境变量 | 简介 |
| --- | --- |
| **网络相关** | |
| [HCCL_IF_IP](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0073.html) | 当通信域的创建方式为"[基于root节点信息创建](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclug_000008.html#ZH-CN_TOPIC_0000002562460885__section1539155710538)"时，可通过此环境变量配置HCCL初始化时Host使用的通信IP地址。此IP地址用于与root节点通信，以完成通信域的创建**。** |
| [HCCL_IF_BASE_PORT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0074.html) | 当通信域的创建方式为"[基于root节点信息创建](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclug_000008.html#ZH-CN_TOPIC_0000002562460885__section1539155710538)"时，可以通过该环境变量指定Host网卡起始端口号，配置后系统默认占用以该端口起始的32个端口进行集群信息收集。 |
| [HCCL_HOST_SOCKET_PORT_RANGE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0143.html) | 当通信域的创建方式为"[基于root节点信息创建](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclug_000008.html#ZH-CN_TOPIC_0000002562460885__section1539155710538)"时，开发者可通过此环境变量配置HCCL在Host侧使用的通信端口。 |
| [HCCL_NPU_SOCKET_PORT_RANGE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0144.html) | 当通信域的创建方式为"[基于root节点信息创建](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclug_000008.html#ZH-CN_TOPIC_0000002562460885__section1539155710538)"时，开发者可通过此环境变量配置HCCL在NPU侧使用的通信端口。 |
| [HCCL_SOCKET_IFNAME](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0075.html) | 配置HCCL初始化时Host使用的通信网卡名，HCCL将通过该网卡名获取Host IP，与root节点通信，以完成通信域的创建**。** |
| [HCCL_SOCKET_FAMILY](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0076.html) | 该环境变量指定通信网卡使用的IP协议。 |
| [HCCL_RDMA_TC](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0089.html) | 用于配置RDMA网
