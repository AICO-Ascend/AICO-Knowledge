# 环境变量列表

> 来源 https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0001.html
> 抓取路由 hiascend-source · 2026-09-02 17:37 · 原文 22029 字符 · 1 图
> MiniMax-M3 七节深读 · ver=v1 · 原文: extraction/web_docs/ascend-cann-community-envvars.md

# CANN 社区版 910beta1 环境变量参考 — 一体化深度解读

## 【定位】

该页面是 CANN（Compute Architecture for Neural Networks）社区版 910beta1 的**环境变量索引总览**，按功能大类（安装配置、图编译、算子编译、资源配置、算子/图执行、TFAdapter、集合通信、AOE 调优、AMCT 模型压缩、性能采集、日志、故障信息、已废弃变量）集中列出开发者构建 AI 应用时可调用的环境变量及简介，作为查找入口链接到各变量的子详情页。

---

## 【技术要点】

1. **设置方式覆盖范围广**：原文指出环境变量可通过 `export` 命令、`putenv/getenv/setenv/unsetenv/clearenv` 函数、`os.environ`、`os.getenv` 等多种途径设置；建议在应用进程拉起前完成配置，以避免访问冲突。
2. **安装/落盘归一路径**：通过 `ASCEND_CACHE_PATH`（共享文件）与 `ASCEND_WORK_PATH`（单机独享文件）将各组件编译运行产物统一落盘到指定路径；自定义算子包则通过 `ASCEND_CUSTOM_OPP_PATH` 指定安装路径。
3. **图编译与算子编译可调**：`DUMP_GE_GRAPH`/`DUMP_GRAPH_LEVEL`/`DUMP_GRAPH_FORMAT`/`DUMP_GRAPH_PATH` 控制图描述信息 dump 的内容、级别、文件类型与路径；`OP_NO_REUSE_MEM` 用于关闭某算子的内存复用以辅助问题定位；`MAX_COMPILE_CORE_NUMBER`、`MULTI_THREAD_COMPILE` 控制图编译的 CPU 核数与线程模式；算子并行编译由 `TE_PARALLEL_COMPILER` 开启。
4. **算子编译缓存与回收策略**：算子编译缓存由 `ASCEND_MAX_OP_CACHE_SIZE` 限制磁盘空间大小，`ASCEND_REMAIN_CACHE_SIZE_RATIO` 控制删除旧 kernel 时需保留缓存比例，**原文标注默认为 50（百分比）**。
5. **Device 与集合通信网络参数**：`ASCEND_DEVICE_ID` 指定逻辑 ID；`ASCEND_RT_VISIBLE_DEVICES` 控制进程可见 Device；集合通信子项含超时（`HCCL_CONNECT_TIMEOUT`、`HCCL_EXEC_TIMEOUT`）、算法（`HCCL_ALGO`）、共享缓存（`HCCL_BUFFSIZE`，**原文标注默认 200，单位 MB**）、链路选择（`HCCL_INTRA_PCIE_ENABLE`、`HCCL_INTRA_ROCE_ENABLE`、`HCCL_INTER_HCCS_DISABLE`）、保序（`HCCL_DETERMINISTIC`）、RDMA 性能（`HCCL_RDMA_*` 系列）、网卡（`HCCL_IF_IP`、`HCCL_SOCKET_IFNAME`）、端口（`HCCL_IF_BASE_PORT`、`HCCL_HOST_SOCKET_PORT_RANGE`、`HCCL_NPU_SOCKET_PORT_RANGE`）、重传（`HCCL_RDMA_RETRY_CNT`，**原文标注默认 7，取值范围 [1,7]**）。
6. **TFAdapter 分版本差异**：`ENABLE_FORCE_V2_CONTROL` 仅对应 TensorFlow 1.15 训练场景，用于将 V1 控制流算子（Switch、Merge、Enter、LoopCond、NextIteration、Exit、ControlTrigger 等）转换为 V2 控制流算子（If、Case、While、For、PartitionedCall 等）以支持动态 shape；`ENABLE_HF32_EXECUTION` 仅对 Conv 类与 Matmul 类算子生效；`NPU_DEBUG`/`NPU_DUMP_GRAPH`/`NPU_ENABLE_PERF`/`NPU_LOOP_SIZE` 对应 TF 2.6.5 训练与在线推理；`STEP_NOW`/`TOTAL_STEP`/`LOSS_NOW`/`TARGET_LOSS` 依赖 `experimental_accelerate_train_mode` 或 `accelerate_train_mode` 参数触发。
7. **分布式组网两种方式**：TF 分布式训练或推理支持 `RANK_TABLE_FILE`/`RANK_ID`/`RANK_SIZE` 指定 rank table；也可不依赖 rank table，通过 `CM_CHIEF_IP`/`CM_CHIEF_PORT`/`CM_CHIEF_DEVICE`/`CM_WORKER_SIZE`/`CM_WORKER_IP` 自动生成资源信息完成集合通信初始化。`HCCL_LOGIC_SUPERPOD_ID` 明确针对 **Atlas A3 训练系列产品 / Atlas A3 推理系列产品** 的超节点模式组网，用于将一个物理超节点划分为多个逻辑超节点。
8. **日志/调试/废弃变量分层**：`ASCEND_*_LOG_*` 系列控制日志路径、级别、Event、Device 侧回传延时、`trace` 日志文件老化（**`ASCEND_TRACE_RECORD_NUM` 取值范围 [10, 1000]**）；故障信息收集由 `NPU_COLLECT_PATH`、`ASCEND_DUMP_SCENE`、`ASCEND_DUMP_PATH` 三项承担；末尾列出 `GE_USE_STATIC_MEM_MEMORY`（原文写作 `GE_USE_STATIC_MEM`）、`ENABLE_ACLNN` 为后续版本废弃环境变量。**本手册明确不含 Ascend Extension for PyTorch 的环境变量**。

---

## 【关键机制与数据】

- **归一落盘与算子包管理**（原文："若开发者期望编译运行过程中产生的文件落盘到归一路径，可通过此环境变量设置**共享文件**的存储路径"）：`ASCEND_CACHE_PATH`、`ASCEND_WORK_PATH` 区分共享/单机独享；自定义算子包通过 `ASCEND_CUSTOM_OPP_PATH` 安装到指定路径。
- **图 dump 粒度**（原文）：`DUMP_GE_GRAPH` 控制 dump 图的**内容多少**，`DUMP_GRAPH_LEVEL` 控制**阶段**，`DUMP_GRAPH_FORMAT` 控制**文件类型**，`DUMP_GRAPH_PATH` 控制**保存路径**，可配置为绝对路径或脚本执行目录的相对路径。
- **内存复用关闭粒度**（原文："在问题定位场景中，如果开发者怀疑是内存复用错误导致计算结果异常，可通过此环境变量指定为某算子单独分配内存"）：`OP_NO_REUSE_MEM` 默认采用内存复用形式，可为**某算子**单独分配内存。
- **算子缓存回收策略**（原文）：`ASCEND_REMAIN_CACHE_SIZE_RATIO` "默认为 50，单位为百分比"——在缓存空间达到 `ASCEND_MAX_OP_CACHE_SIZE` 而需删除旧 kernel 时，保留的最小空间比例。
- **算子原型校验跳过**（原文："算子入图时，跳过算子原型交付件校验的开关。交付件包括 shape 推导等算子入图适配函数的实现"）：`IGNORE_INFER_ERROR`。
- **多流并发执行前提**（原文："当前多流并发执行功能默认关闭，动态 shape 图模式场景下"）：`ENABLE_DYNAMIC_SHAPE_MULTI_STREAM` 仅在**动态 shape 图模式**场景有效。
- **TF 控制流算子版本切换原因**（原文）："由于 tf.case/tf.cond/tf.while_loop 这些 API 对应 TensorFlow V1 版本的控制流算子（例如 Switch、Merge、Enter、LoopCond、NextIteration、Exit、ControlTrigger 等）不支持动态 shape，仅 TensorFlow V2 版本的控制流算子（例如 If、Case、While、For、PartitionedCall 等）支持动态 shape"。
- **RDMA QP 与多 QP 调度**（原文）："两个 rank 之间 RDMA 通信时会默认创建 1 个 QP（Queue Pair）进行数据传输"，`HCCL_RDMA_QPS_PER_CONNECTION` 与 `HCCL_RDMA_QP_PORT_CONFIG_PATH` 用于多 QP，`HCCL_MULTI_QP_THRESHOLD` 用于设置每个 QP 分担数据量的最小阈值。
- **HCCL 算子重执行粒度**（原文）："HCCL 算子重执行以**通信域**为粒度，当通信算子执行报 SDMA 或者 RDMA CQE 类型的错误时，HCCL 会尝试重新执行此通信算子"——`HCCL_OP_RETRY_ENABLE` 与 `HCCL_OP_RETRY_PARAMS`。
- **HCCL 调试子模块**（原文）："$HOME/ascend/log/run 目录下的日志"将包含 HCCL 特定子模块的详细运行信息；目前支持 `ALG` 或 `alg`（算法编排模块）、`TASK` 或 `task`（任务编排模块）、`RESOURCE` 或 `resource`（资源管理模块）几个配置项——`HCCL_DEBUG_CONFIG`。
- **版本适配差异**（原文）：本手册显式**不含** Ascend Extension for PyTorch 的环境变量，且 `HCCL_LOGIC_SUPERPOD_ID` 显式仅适用于 **Atlas A3 训练系列产品 / Atlas A3 推理系列产品**。
- **废弃说明**（原文）：本节标题为"后续版本废弃环境变量"，收录 `GE_USE_STATIC_MEM`、`ENABLE_ACLNN`，原文未在本页中展开说明其取代/迁移方式。

---

## 【表格解读】

> 原文按功能大类切分为多个表格，下方逐表**原样还原**并归类解读。所有变量名、简介内容与子详情页链接均原样保留。

### 表 1 · 安装配置相关

| 环境变量 | 简介 |
| --- | --- |
| [ASCEND_CACHE_PATH](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0006.html) | 若开发者期望编译运行过程中产生的文件落盘到归一路径，可通过此环境变量设置**共享文件**的存储路径，各组件编译运行过程中产生的可共享文件会存储到此环境变量定义的路径中。 |
| [ASCEND_WORK_PATH](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0007.html) | 若开发者期望编译运行过程中产生的文件落盘到归一路径，可通过此环境变量设置**单机独享文件**的存储路径，各组件编译运行过程中产生的单机独享文件会存储到此环境变量定义的路径中。 |
| [ASCEND_CUSTOM_OPP_PATH](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0147.html) | 用户自定义算子包安装路径。开发者编译生成的自定义算子包需要安装到指定路径下时，需要配置该路径。 |

**解读**：归类为"产物落盘与算子包管理"。`ASCEND_CACHE_PATH` 与 `ASCEND_WORK_PATH` 形成**共享/单机独享**文件分层设计，便于在多机部署或共享存储场景下隔离；`ASCEND_CUSTOM_OPP_PATH` 是自定义算子（Custom OPP）的注册安装入口。

---

### 表 2 · 图编译

| 环境变量 | 简介 |
| --- | --- |
| [DUMP_GE_GRAPH](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0011.html) | 把整个流程中各个阶段的图描述信息打印到文件中，此环境变量控制 dump 图的内容多少。 |
| [DUMP_GRAPH_LEVEL](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0012.html) | 把整个图编译流程中各个阶段的图描述信息打印到文件中。 |
| [DUMP_GRAPH_FORMAT](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0155.html) | 控制需要生成的 dump 文件类型。 |
| [DUMP_GRAPH_PATH](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0013.html) | 指定 DUMP 图文件的保存路径，可配置为绝对路径或脚本执行目录的相对路径。 |
| [OP_NO_REUSE_MEM](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0014.html) | 计算图在昇腾平台编译的过程中默认采用内存复用形式，在问题定位场景中，如果开发者怀疑是内存复用错误导致计算结果异常，可通过此环境变量指定为某算子单独分配内存。 |
| [ASCEND_ENGINE_PATH](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0015.html) | 单算子 JSON 文件转换成离线模型场景，如果希望模型转换时只使用 TBE 算子（不查找 AI CPU 算子，找不到 TBE 算子则报错），则需要使用该环境变量。 |
| [MAX_COMPILE_CORE_NUMBER](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0016.html) | 此环境变量用于指定图编译时可用的 CPU 核数。 |
| [MULTI_THREAD_COMPILE](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0017.html) | 此环境变量用于控制模型转换时是否使用单线程编译。 |
| [ENABLE_NETWORK_ANALYSIS_DEBUG](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0018.html) | TensorFlow 训练场景下，计算图编译失败时默认会终止训练流程，不会继续向 Device 下发剩余的图。若开发者希望图编译失败时，不终止训练流程，允许 TF Adapter 持续向 Device 下发计算图，可通过设置该环境变量实现。 |

**解读**：归类为"图编译期行为控制"。`DUMP_*` 四件套分别承担"内容多少/阶段/文件类型/保存路径"四个维度——可在不阅读子页的情况下理解 dump 行为由四个变量协作完成。`OP_NO_REUSE_MEM` 默认采用内存复用，关闭粒度为单算子，常用于精度异常归因。`ASCEND_ENGINE_PATH` 是单算子 JSON 转离线模型场景下"只用 TBE 算子、找不到即报错"的开关。`ENABLE_NETWORK_ANALYSIS_DEBUG` 是 TF 场景的容错开关，控制图编译失败后是否继续下发剩余图。

---

### 表 3 · 算子编译

| 环境变量 | 简介 |
| --- | --- |
| [TE_PARALLEL_COMPILER](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0020.html) | 网络模型较大时，可通过配置此环境变量开启算子的并行编译功能。 |
| [ASCEND_MAX_OP_CACHE_SIZE](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0021.html) | 启用算子编译缓存功能时，可通过此环境变量限制某个 AI 处理器下缓存文件夹的磁盘空间的大小。 |
| [ASCEND_REMAIN_CACHE_SIZE_RATIO](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0022.html) | 启用算子编译缓存功能时，当编译缓存空间大小达到 ASCEND_MAX_OP_CACHE_SIZE 而需要删除旧的 kernel 文件时，系统需要保留缓存的空间大小比例，默认为 50，单位为百分比。 |
| [IGNORE_INFER_ERROR](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0142.html) | 算子入图时，跳过算子原型交付件校验的开关。交付件包括 shape 推导等算子入图适配函数的实现。 |

**解读**：归类为"算子编译加速与缓存治理"。`TE_PARALLEL_COMPILER` 是大模型并行编译加速开关；`ASCEND_MAX_OP_CACHE_SIZE` + `ASCEND_REMAIN_CACHE_SIZE_RATIO`（原文：默认 50，百分比）构成"上限+回收保留比例"的缓存治理对；`IGNORE_INFER_ERROR` 是算子入图阶段"跳过原型校验（shape 推导等）"的容错开关。

---

### 表 4 · 资源配置

| 环境变量 | 简介 |
| --- | --- |
| [ASCEND_DEVICE_ID](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0027.html) | 指定当前进程所用的 AI 处理器的逻辑 ID。 |
| [ASCEND_RT_VISIBLE_DEVICES](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0028.html) | 指定哪些 Device 对当前进程可见，支持一次指定一个或多个 Device ID。通过该环境变量，可实现不修改应用程序即可调整所用 Device 的功能。 |
| [AUTO_USE_UC_MEMORY](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0029.html) | 控制系统是否允许算子搬移数据不经过 L2 Cache 的功能。 |
| [RESOURCE_CONFIG_PATH](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0133.html) | 用于设置配置异构资源描述信息文件的存储路径。 |

**解读**：归类为"进程级硬件与异构资源绑定"。`ASCEND_DEVICE_ID`/`ASCEND_RT_VISIBLE_DEVICES` 形成"绑定单卡 vs 暴露多卡"两种用法；`AUTO_USE_UC_MEMORY` 控制数据搬移是否走 L2 Cache，影响带宽/缓存命中；`RESOURCE_CONFIG_PATH` 提供异构资源描述文件的落盘/读取位置。

---

### 表 5 · 算子执行

| 环境变量 | 简介 |
| --- | --- |
| [ACLNN_CACHE_LIMIT](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0031.html) | 此环境变量用于配置 aclnn API 在 Host 侧缓存的算子信息条目个数。缓存的算子信息包含 workspace 大小、算子计算的执行器、Tiling 信息等。 |

**解读**：仅一条——控制 aclnn API 在 Host 侧缓存的条目上限，缓存内容包含 workspace 大小、执行器与 Tiling 信息。该变量是算子执行期唯一列出的环境变量。

---

### 表 6 · 图执行

| 环境变量 | 简介 |
| --- | --- |
| [ENABLE_DYNAMIC_SHAPE_MULTI_STREAM](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0033.html) | 计算图执行时，开启多流并发执行功能在一定场景下可提升网络性能。当前多流并发执行功能默认关闭，动态 shape 图模式场景下，若开发者想开启多流并发执行功能，可通过此环境变量开启。 |
| [MAX_RUNTIME_CORE_NUMBER](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0034.html) | 训练与在线推理场景下，针对动态 shape 图模式执行的网络，可通过设置此环境变量开启图执行器（Host 侧）的多线程任务调度。 |

**解读**：归类为"图执行期并发与调度"。两者均显式标注**仅适用于动态 shape 图模式**：`ENABLE_DYNAMIC_SHAPE_MULTI_STREAM` 默认关闭，用于开启多流并发执行；`MAX_RUNTIME_CORE_NUMBER` 用于开启 Host 侧图执行器的多线程任务调度。

---

### 表 7 · TFAdapter

| 环境变量 | 简介 |
| --- | --- |
| [JOB_ID](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0036.html) | TensorFlow 训练与在线推理场景下，可通过此环境变量自定义任务 ID。 |
| [ENABLE_FORCE_V2_CONTROL](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0037.html) | TensorFlow 1.15 训练场景下，如果输入是动态 shape，由于 tf.case/tf.cond/tf.while_loop 这些 API 对应 TensorFlow V1 版本的控制流算子（例如 Switch、Merge、Enter、LoopCond、NextIteration、Exit、ControlTrigger 等）不支持动态 shape，仅 TensorFlow V2 版本的控制流算子（例如 If、Case、While、For、PartitionedCall 等）支持动态 shape，因此，如果用户的训练脚本中使用了这些 API，需要将 V1 版本的控制流算子转换为 V2 版本，用于支持动态 shape 功能。另外，如果网络中的分支结构较多，采用 V1 版本的控制流算子可能导致流数超限，此时也需要将 V1 版本的控制流算子转换成 V2 版本算子解决。 |
| [ENABLE_HF32_EXECUTION](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0038.html) | 针对 TensorFlow 1.15 网络，是否启用 HF32 自动代替 FP32 数据类型的功能，当前版本此环境变量仅针对 Conv 类算子与 Matmul 类算子生效。 |
| [NPU_DEBUG](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0039.html) | TensorFlow 2.6.5 训练与在线推理场景下，用于开启 TF Adapter 的 Debug 级别执行日志。 |
| [NPU_DUMP_GRAPH](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0040.html) | TensorFlow 2.6.5 训练与在线推理场景下，用于开启 TF Adapter 图 Dump 功能。 |
| [NPU_ENABLE_PERF](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0041.html) | TensorFlow 2.6.5 训练与在线推理场景下，用于开启 TF Adapter 图耗时打印功能。 |
| [NPU_LOOP_SIZE](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0042.html) | TensorFlow 2.6.5 训练与在线推理场景下，用于设置 NPU 上循环下沉的次数。 |
| [STEP_NOW](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0043.html) | TensorFlow 1.15 训练场景下，若通过 "experimental_accelerate_train_mode" 参数或者 "accelerate_train_mode" 参数触发了训练加速功能，可通过此环境变量设置 NPU 上当前的执行步数。 |
| [TOTAL_STEP](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0044.html) | TensorFlow 1.15 训练场景下，若通过 "experimental_accelerate_train_mode" 参数或者 "accelerate_train_mode" 参数触发了训练加速功能，可通过此环境变量设置 NPU 上总训练步数。 |
| [LOSS_NOW](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0045.html) | TensorFlow 1.15 训练场景下，若通过 "experimental_accelerate_train_mode" 参数或者 "accelerate_train_mode" 参数触发了训练加速功能，可通过此环境变量设置 NPU 上当前迭代的 loss 值。 |
| [TARGET_LOSS](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0046.html) | TensorFlow 1.15 训练场景下，若通过 "experimental_accelerate_train_mode" 参数或者 "accelerate_train_mode" 参数触发了训练加速功能，可通过此环境变量设置 NPU 上的目标训练 loss 值。 |
| [RANK_TABLE_FILE](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0047.html) | TensorFlow 分布式训练或推理场景下，通过此环境变量指定参与集合通信的 AI 处理器的 rank table 资源配置文件，包含 rank table 文件路径和文件名。 |
| [RANK_ID](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0048.html) | TensorFlow 分布式训练或推理场景下，通过此环境变量指定当前进程在集合通信进程组中对应的 rank 标识。 |
| [RANK_SIZE](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0049.html) | TensorFlow 分布式训练或推理场景下，通过此环境变量指定当前训练进程对应的 Device 数量。 |
| [CM_CHIEF_IP](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0050.html) | TensorFlow 分布式训练场景下，用户可以选择不使用 rank table 文件，通过组合使用环境变量的方式自动生成资源信息，完成集合通信初始化。  本环境变量用于配置 Master 节点的监听 Host IP。 |
| [CM_CHIEF_PORT](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0051.html) | 本环境变量用于配置 Master 节点的监听端口。 |
| [CM_CHIEF_DEVICE](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0052.html) | 本环境变量用于指定 Master 节点中统计 Server 端集群信息的 Device 逻辑 ID。 |
| [CM_WORKER_SIZE](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0053.html) | 本环境变量用于配置本次业务通信域 Device 的数量。 |
| [CM_WORKER_IP](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0054.html) | 本环境变量用于配置当前 Device 和 Master 节点进行信息交换时所用的网卡 IP。 |

**解读**：归类为"TF Adapter 专用变量"，可细分为三组：
- **通用**：`JOB_ID`（任务 ID）；
- **TF 1.15**：`ENABLE_FORCE_V2_CONTROL`（V1→V2 控制流算子转换）、`ENABLE_HF32_EXECUTION`（HF32 替 FP32，**仅 Conv/Matmul 算子**）、`STEP_NOW`/`TOTAL_STEP`/`LOSS_NOW`/`TARGET_LOSS`（依赖 `experimental_accelerate_train_mode` 或 `accelerate_train_mode` 触发的训练加速功能）；
- **TF 2.6.5**：`NPU_DEBUG`、`NPU_DUMP_GRAPH`、`NPU_ENABLE_PERF`、`NPU_LOOP_SIZE`；
- **分布式**：使用 rank table 文件时配置 `RANK_TABLE_FILE`/`RANK_ID`/`RANK_SIZE`；不使用 rank table 时组合配置 `CM_CHIEF_IP`/`CM_CHIEF_PORT`/`CM_CHIEF_DEVICE`/`CM_WORKER_SIZE`/`CM_WORKER_IP` 以自动生成资源信息。

---

### 表 8 · 集合通信

#### 功能相关

| 环境变量 | 简介 |
| --- | --- |
| [HCCL_CONNECT_TIMEOUT](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0077.html) | 分布式训练或推理场景下，用于限制不同设备之间 socket 建链过程的超时等待时间。不同设备进程在集合通信初始化之前由于其他因素会导致执行不同步。该环境变量控制设备间的建链超时等待时间，在该配置时间内各设备进程等待其他设备建链同步。 |
| [HCCL_EXEC_TIMEOUT](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0078.html) | 不同设备进程在分布式训练或推理过程中存在卡间执行任务不一致的场景（如仅特定进程会保存 checkpoint 数据），通过该环境变量可控制设备间执行时同步等待的时间，在该配置时间内各设备进程等待其他设备执行通信同步。 |
| [HCCL_ALGO](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0079.html) | 此环境变量用于配置集合通信 Server 间通信算法以及超节点间通信算法，支持全局配置算法类型与按算子配置算法类型两种配置方式。 |
| [HCCL_BUFFSIZE](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0080.html) | 此环境变量用于控制通信域所使用的共享数据缓存区大小。需要配置为整数，取值大于等于 1，默认值为 200，单位 MB。 |
| [HCCL_INTRA_PCIE_ENABLE](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0081.html) | 用于配置 Server 内是否使用 PCIe 链路进行通信。 |
| [HCCL_INTRA_ROCE_ENABLE](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0082.html) | 用于配置 Server 内或超节点内是否使用 RoCE 链路进行通信。 |
| [HCCL_INTER_HCCS_DISABLE](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0083.html) | 此环境变量用于配置超节点模式组网中超节点内的通信链路类型，支持如下取值： |
| [HCCL_OP_EXPANSION_MODE](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0096.html) | 该环境变量用于配置通信算子的展开模式。 |
| [HCCL_DETERMINISTIC](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0099.html) | 此环境变量用于配置是否开启归约类通信算子的确定性计算或保序功能，其中归约类通信算子包括 AllReduce、ReduceScatter、ReduceScatterV、Reduce，归约保序是指严格的确定性计算，在确定性的基础上保证归约顺序一致。 |
| [HCCL_LOGIC_SUPERPOD_ID](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0100.html) | 针对 Atlas A3 训练系列产品 / Atlas A3 推理系列产品 的超节点模式组网，若不使用 rank table 文件配置集群资源信息，可通过此环境变量指定当前节点运行进程所属的超节点 ID，实现将一个物理超节点划分为多个逻辑超节点的功能。 |

#### 性能相关

| 环境变量 | 简介 |
| --- | --- |
| [HCCL_RDMA_PCIE_DIRECT_POST_NOSTRICT](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0093.html) | 多机通信且 Host 操作系统小页内存页表大小非 4KB 的场景，当通信算子下发性能 Host Bound 时，开发者可设置此环境变量，通过 PCIe Direct 的方式提交 RDMA 任务，提升通信算子下发性能。 |
| [HCCL_RDMA_QPS_PER_CONNECTION](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0094.html) | 两个 rank 之间 RDMA 通信时会默认创建 1 个 QP（Queue Pair）进行数据传输，若开发者想让两个 rank 之间的 RDMA 通信使用多个 QP，可通过此环境变量实现。 |
| [HCCL_RDMA_QP_PORT_CONFIG_PATH](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0141.html) | 两个 rank 之间 RDMA 通信时会默认创建 1 个 QP（Queue Pair）进行数据传输，若开发者想让两个 rank 之间的 RDMA 通信使用多个 QP，并指定多 QP 通信时使用的源端口号，可通过此环境变量实现。 |
| [HCCL_MULTI_QP_THRESHOLD](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0095.html) | rank 间 RDMA 通信使用多 QP 通信的场景下，开发者可通过本环境变量设置每个 QP 分担数据量的最小阈值。 |

#### 网络相关

| 环境变量 | 简介 |
| --- | --- |
| [HCCL_IF_IP](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0073.html) | 当通信域的创建方式为"[基于 root 节点信息创建](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/API/hcclug/hcclug_000008.html#ZH-CN_TOPIC_0000002586753591__section1539155710538)"时，可通过此环境变量配置 HCCL 初始化时 Host 使用的通信 IP 地址。此 IP 地址用于与 root 节点通信，以完成通信域的创建**。** |
| [HCCL_IF_BASE_PORT](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_0074.html) | 当通信域的创建方式为"[基于 root 节点信息创建](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/API/hcclug/hcclug_000008.html#ZH-CN_TOPIC_0000002586753591__section1539155710538)"时，可以通过该环境变量指定 Host 网卡起始端口号，配置后系统默认占用以该端口起始的 32 个端口进行集群信息收集。 |
| [HCCL_HOST_SOCKET_PORT_RANGE](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/maintenref/envvar/envref_07_
