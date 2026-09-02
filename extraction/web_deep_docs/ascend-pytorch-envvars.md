# 环境变量列表

> 来源 https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/env_variable_list.md
> 抓取路由 hiascend-source · 2026-09-02 17:37 · 原文 9034 字符 · 0 图
> MiniMax-M3 七节深读 · ver=v1 · 原文: extraction/web_docs/ascend-pytorch-envvars.md

# 一体化深度解读：Ascend Extension for PyTorch 环境变量清单

## 【定位】

本页面是 **Ascend Extension for PyTorch（PyTorch 2600 版本）** 开发者在训练和在线推理过程中可使用的全部环境变量的总索引/参考目录页面，用于在调优、调试、问题定位等场景下按类别检索相关环境变量并跳转到具体说明页。

## 【技术要点】

- **页面性质**：纯索引式清单页（`.md` 直出），核心内容为「表 1 环境变量列表」一张大表，按"环境变量类型 / 环境变量名称 / 简介"三列组织，共覆盖 **10 个分类、40 条**环境变量。
- **分类覆盖**：算子执行（7 条）、算子编译（2 条）、内存管理（6 条）、集合通信（6 条）、告警信息打印（4 条）、同步超时（1 条）、特征值检测（4 条）、性能优化（3 条）、设备管理（3 条）、图模式（2 条）。
- **硬件差异点（原文）**：`INF_NAN_MODE_FORCE_DISABLE` 仅适用于 "Atlas A2 训练系列产品 / Atlas A3 训练系列产品"，用以强制关闭 INF_NAN 模式。
- **版本差异点（原文）**：
  - `NPU_ASD_ENABLE`、`NPU_ASD_UPPER_THRESH`、`NPU_ASD_SIGMA_THRESH` —— 适用于 **Ascend Extension for PyTorch 7.0.0 及之前版本** 的特征值检测（绝对阈值 / 相对阈值）；
  - `NPU_ASD_CONFIG` —— 适用于 **Ascend Extension for PyTorch 7.1.0 及之后版本** 的特征值检测开关。
- **Beta 实验特性（原文）**：`(beta) TORCH_HCCL_ZERO_COPY`（集合通信片内零拷贝）、`(beta) INDUCTOR_ASCEND_CHECK_ACCURACY`（Inductor-Triton 模式下的融合算子精度校验）。
- **后端耦合**：集合通信类条目（`HCCL_ASYNC_ERROR_HANDLING`、`HCCL_DESYNC_DEBUG`、`HCCL_EVENT_TIMEOUT` 等）以 **HCCL 作为通信后端** 为前提；告警/调试类条目（`TORCH_NPU_DISABLED_WARNING`、`TORCH_NPU_COMPACT_ERROR_OUTPUT`、`TORCH_NPU_LOGS`、`TORCH_NPU_LOGS_FILTER`）的行为载体为 **Ascend Extension for PyTorch** 新增模块，而非 PyTorch 社区原生模块。
- **作用域与边界**：明确指出"基于 CANN 构建 AI 应用和业务过程中使用的环境变量请参考《CANN 环境变量参考》"，即本表只覆盖 Torch 适配层，CANN 底层环境变量不在本表范围。

## 【关键机制与数据】

> 以下均严格基于原文逐字复述，不引入原文之外的具体数值。

- **`PYTORCH_NPU_ALLOC_CONF`**：原文称"通过此环境变量可控制缓存分配器行为。配置此环境变量会改变内存占用量，可能造成性能波动。" —— 即影响 NPU 缓存分配器，可能带来性能波动。
- **`PYTORCH_NO_NPU_MEMORY_CACHING`**：原文称"可配置是否关闭内存复用机制"。
- **`OOM_SNAPSHOT_ENABLE` / `OOM_SNAPSHOT_PATH`**：原文称"在内存不足报错时是否保存内存数据，以供分析内存不足原因" 以及其保存路径配置。
- **`MULTI_STREAM_MEMORY_REUSE`**：原文称"可配置多流内存复用是否开启"。
- **`TORCH_NPUGRAPH_GC`**：原文称"可控制图捕获模式（NPUGraph Capture）过程中是否主动触发 Python GC（Garbage Collection）"。
- **`INF_NAN_MODE_ENABLE`**：原文称"控制 AI 处理器对输入数据为 Inf/NaN 的处理能力，即控制 AI 处理器使用饱和模式还是 INF_NAN 模式"。
- **`INF_NAN_MODE_FORCE_DISABLE`**：原文限定 "Atlas A2 训练系列产品 / Atlas A3 训练系列产品"，强制关闭 INF_NAN 模式。
- **`COMBINED_ENABLE`**：原文称"可设置 combined 标志"。
- **`ASCEND_LAUNCH_BLOCKING`**：原文称"可控制算子执行时是否启动同步模式"。
- **`TASK_QUEUE_ENABLE`**：原文称"可配置 task_queue 算子下发队列是否开启和优化等级" —— 含"是否开启 + 优化等级"两维开关。
- **`PER_STREAM_QUEUE`**：原文称"可配置是否开启一个 stream 一个 task_queue 算子下发队列" —— 即 per-stream 队列策略。
- **`TORCH_NPU_USE_COMPATIBLE_IMPL`**：原文称"用于控制 API 的实现是否与 PyTorch 原生社区完全对齐"。
- **`ACL_OP_COMPILER_CACHE_DIR` / `ACL_OP_COMPILER_CACHE_MODE`**：原文称分别"配置算子编译磁盘缓存的目录 / 磁盘缓存模式"。
- **`HCCL_ASYNC_ERROR_HANDLING`**：原文称"控制是否开启异步错误处理"。
- **`HCCL_DESYNC_DEBUG`**：原文称"控制是否进行通信超时分析"。
- **`HCCL_EVENT_TIMEOUT`**：原文称"设置等待 Event 完成的超时时间"。
- **`P2P_HCCL_BUFFSIZE`**：原文称"可配置是否开启点对点通信（`torch.distributed.isend`、`torch.distributed.irecv` 和 `torch.distributed.batch_isend_irecv`），并使用独立通信域功能"。
- **`RANK_TABLE_FILE`**：原文称"可配置是否通过 RANK_TABLE_FILE 进行集合通信域建链"。
- **`(beta) TORCH_HCCL_ZERO_COPY`**：原文称在"训练或在线推理场景下，可通过此环境变量开启集合通信片内零拷贝功能，减少通信算子在通信过程中片内拷贝次数，提升集合通信效率，降低通信耗时。同时在计算通信并行场景下，降低通信过程中对显存带宽的抢占"。
- **`TORCH_NPU_DISABLED_WARNING`**：原文称"可配置是否打印 Ascend Extension for PyTorch 的告警信息"。
- **`TORCH_NPU_COMPACT_ERROR_OUTPUT`**：原文称"可精简打印错误信息，开启后会将 CANN 内部调用栈、Ascend Extension for PyTorch 错误码等自定义报错信息转移到 plog 中，仅保留有效的错误说明，提高异常信息的可读性"。
- **`TORCH_NPU_LOGS`**：原文称"用于配置 Ascend Extension for PyTorch 新增模块的日志打印功能，为开发者在 Debugging 场景下提供精准的调试定位能力"。
- **`TORCH_NPU_LOGS_FILTER`**：原文称"用于过滤 Ascend Extension for PyTorch 日志输出内容，通过黑白名单机制筛选需要显示的日志信息" —— 黑白名单过滤机制。
- **`ACL_DEVICE_SYNC_TIMEOUT`**：原文称"可配置设备同步的超时时间"。
- **`CPU_AFFINITY_CONF`**：原文称"可以开启粗/细粒度绑核。该配置能够避免线程间抢占，提高缓存命中，避免跨 NUMA（非统一内存访问架构）节点的内存访问，减少任务调度开销，优化任务执行效率"。
- **`PROF_CONFIG_PATH`**：原文称"在 PyTorch 训练场景中，通过此环境变量可指定 Ascend PyTorch Profiler 接口的 dynamic_profile 采集功能的 profiler_config.json 配置文件路径"。
- **`KINETO_USE_DAEMON`**：原文称"PyTorch 训练场景用于设置是否通过 msMonitor nputrace 方式开启 dynamic_profile 采集功能"（原文措辞含 "nputrace"，疑似笔误，未做改写）。
- **`STREAMS_PER_DEVICE`**：原文称"可配置 stream pool 的最大流数"。
- **`TORCH_NPU_DEVICE_CAPABILITY`**：原文称"可配置 `torch_npu.npu.get_device_capability()` 的返回值"。
- **`TORCH_TRANSFER_TO_NPU`**：原文称"可配置是否自动启用 transfer_to_npu 功能，将 PyTorch 的 CUDA 相关 API 自动替换为 NPU 对应 API"。
- **`TORCHINDUCTOR_NPU_BACKEND`**：原文称"可配置图模式下的优化模式，支持 Triton、MLIR、DVM 等优化模式"。
- **`(beta) INDUCTOR_ASCEND_CHECK_ACCURACY`**：原文称"是 Ascend Extension for PyTorch 提供的精度校验工具，仅在 torch.compile 图编译后端为 'Inductor' 且模式为 'Triton' 时自动检测融合算子的数值精度"。

## 【表格解读】

原文唯一核心表为"表 1 环境变量列表"，**逐字还原**如下：

**表 1 环境变量列表**

| 环境变量类型 | 环境变量名称 | 简介 |
| --- | --- | --- |
| 算子执行 | [INF_NAN_MODE_ENABLE](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/INF_NAN_MODE_ENABLE.md) | 通过此环境变量可控制 AI 处理器对输入数据为 Inf/NaN 的处理能力，即控制 AI 处理器使用饱和模式还是 INF_NAN 模式。 |
| 算子执行 | [INF_NAN_MODE_FORCE_DISABLE](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/INF_NAN_MODE_FORCE_DISABLE.md) | Atlas A2 训练系列产品/Atlas A3 训练系列产品，通过此环境变量可强制关闭 INF_NAN 模式。 |
| 算子执行 | [COMBINED_ENABLE](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/COMBINED_ENABLE.md) | 通过此环境变量可设置 combined 标志。 |
| 算子执行 | [ASCEND_LAUNCH_BLOCKING](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/ASCEND_LAUNCH_BLOCKING.md) | 通过此环境变量可控制算子执行时是否启动同步模式。 |
| 算子执行 | [TASK_QUEUE_ENABLE](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/TASK_QUEUE_ENABLE.md) | 通过此环境变量可配置 task_queue 算子下发队列是否开启和优化等级。 |
| 算子执行 | [PER_STREAM_QUEUE](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/PER_STREAM_QUEUE.md) | 通过此环境变量可配置是否开启一个 stream 一个 task_queue 算子下发队列。 |
| 算子执行 | [TORCH_NPU_USE_COMPATIBLE_IMPL](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/TORCH_NPU_USE_COMPATIBLE_IMPL.md) | 该环境变量用于控制 API 的实现是否与 PyTorch 原生社区完全对齐。 |
| 算子编译 | [ACL_OP_COMPILER_CACHE_DIR](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/ACL_OP_COMPILER_CACHE_DIR.md) | 通过此环境变量可配置算子编译磁盘缓存的目录。 |
| 算子编译 | [ACL_OP_COMPILER_CACHE_MODE](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/ACL_OP_COMPILER_CACHE_MODE.md) | 通过此环境变量可配置算子编译磁盘缓存模式。 |
| 内存管理 | [PYTORCH_NPU_ALLOC_CONF](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/PYTORCH_NPU_ALLOC_CONF.md) | 通过此环境变量可控制缓存分配器行为。配置此环境变量会改变内存占用量，可能造成性能波动。 |
| 内存管理 | [PYTORCH_NO_NPU_MEMORY_CACHING](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/PYTORCH_NO_NPU_MEMORY_CACHING.md) | 通过此环境变量可配置是否关闭内存复用机制。 |
| 内存管理 | [OOM_SNAPSHOT_ENABLE](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/OOM_SNAPSHOT_ENABLE.md) | 通过此环境变量可配置在内存不足报错时是否保存内存数据，以供分析内存不足原因。 |
| 内存管理 | [OOM_SNAPSHOT_PATH](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/OOM_SNAPSHOT_PATH.md) | 通过此环境变量可配置在内存不足报错时内存数据的保存路径。 |
| 内存管理 | [MULTI_STREAM_MEMORY_REUSE](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/MULTI_STREAM_MEMORY_REUSE.md) | 通过此环境变量可配置多流内存复用是否开启。 |
| 内存管理 | [TORCH_NPUGRAPH_GC](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/TORCH_NPUGRAPH_GC.md) | 通过此环境变量可控制图捕获模式（NPUGraph Capture）过程中是否主动触发 Python GC（Garbage Collection）。 |
| 集合通信 | [HCCL_ASYNC_ERROR_HANDLING](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/HCCL_ASYNC_ERROR_HANDLING.md) | 当使用 HCCL 作为通信后端时，通过此环境变量可控制是否开启异步错误处理。 |
| 集合通信 | [HCCL_DESYNC_DEBUG](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/HCCL_DESYNC_DEBUG.md) | 当使用 HCCL 作为通信后端时，通过此环境变量可控制是否进行通信超时分析。 |
| 集合通信 | [HCCL_EVENT_TIMEOUT](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/HCCL_EVENT_TIMEOUT.md) | 当使用 HCCL 作为通信后端时，通过此环境变量可设置等待 Event 完成的超时时间。 |
| 集合通信 | [P2P_HCCL_BUFFSIZE](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/P2P_HCCL_BUFFSIZE.md) | 通过此环境变量可配置是否开启点对点通信（`torch.distributed.isend`、`torch.distributed.irecv` 和 `torch.distributed.batch_isend_irecv`），并使用独立通信域功能。 |
| 集合通信 | [RANK_TABLE_FILE](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/RANK_TABLE_FILE.md) | 通过此环境变量可配置是否通过 RANK_TABLE_FILE 进行集合通信域建链。 |
| 集合通信 | [(beta) TORCH_HCCL_ZERO_COPY](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/（beta）TORCH_HCCL_ZERO_COPY.md) | 训练或在线推理场景下，可通过此环境变量开启集合通信片内零拷贝功能，减少通信算子在通信过程中片内拷贝次数，提升集合通信效率，降低通信耗时。同时在计算通信并行场景下，降低通信过程中对显存带宽的抢占。 |
| 告警信息打印 | [TORCH_NPU_DISABLED_WARNING](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/TORCH_NPU_DISABLED_WARNING.md) | 通过此环境变量可配置是否打印 Ascend Extension for PyTorch 的告警信息。 |
| 告警信息打印 | [TORCH_NPU_COMPACT_ERROR_OUTPUT](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/TORCH_NPU_COMPACT_ERROR_OUTPUT.md) | 通过此环境变量可精简打印错误信息，开启后会将 CANN 内部调用栈、Ascend Extension for PyTorch 错误码等自定义报错信息转移到 plog 中，仅保留有效的错误说明，提高异常信息的可读性。 |
| 告警信息打印 | [TORCH_NPU_LOGS](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/TORCH_NPU_LOGS.md) | 此环境变量用于配置 Ascend Extension for PyTorch 新增模块的日志打印功能，为开发者在 Debugging 场景下提供精准的调试定位能力。 |
| 告警信息打印 | [TORCH_NPU_LOGS_FILTER](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/TORCH_NPU_LOGS_FILTER.md) | 此环境变量用于过滤 Ascend Extension for PyTorch 日志输出内容，通过黑白名单机制筛选需要显示的日志信息，帮助开发者在大量日志中快速定位关键信息。 |
| 同步超时 | [ACL_DEVICE_SYNC_TIMEOUT](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/ACL_DEVICE_SYNC_TIMEOUT.md) | 通过此环境变量可配置设备同步的超时时间。 |
| 特征值检测 | [NPU_ASD_ENABLE](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/NPU_ASD_ENABLE.md) | Ascend Extension for PyTorch 7.0.0 及之前版本，通过此环境变量可控制是否开启 Ascend Extension for PyTorch 的特征值检测功能。 |
| 特征值检测 | [NPU_ASD_UPPER_THRESH](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/NPU_ASD_UPPER_THRESH.md) | Ascend Extension for PyTorch 7.0.0 及之前版本，通过此环境变量可配置特征值检测功能的绝对阈值。 |
| 特征值检测 | [NPU_ASD_SIGMA_THRESH](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/NPU_ASD_SIGMA_THRESH.md) | Ascend Extension for PyTorch 7.0.0 及之前版本，通过此环境变量可配置特征值检测功能的相对阈值。 |
| 特征值检测 | [NPU_ASD_CONFIG](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/NPU_ASD_CONFIG.md) | Ascend Extension for PyTorch 7.1.0 及之后版本，通过此环境变量可控制是否开启 Ascend Extension for PyTorch 的特征值检测功能。 |
| 性能优化 | [CPU_AFFINITY_CONF](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/CPU_AFFINITY_CONF.md) | Ascend Extension for PyTorch 可以通过设置环境变量 CPU_AFFINITY_CONF 来开启粗/细粒度绑核。该配置能够避免线程间抢占，提高缓存命中，避免跨 NUMA（非统一内存访问架构）节点的内存访问，减少任务调度开销，优化任务执行效率。 |
| 性能优化 | [PROF_CONFIG_PATH](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/PROF_CONFIG_PATH.md) | 在 PyTorch 训练场景中，通过此环境变量可指定 Ascend PyTorch Profiler 接口的 dynamic_profile 采集功能的 profiler_config.json 配置文件路径。 |
| 性能优化 | [KINETO_USE_DAEMON](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/KINETO_USE_DAEMON.md) | PyTorch 训练场景用于设置是否通过 msMonitor nputrace 方式开启 dynamic_profile 采集功能。 |
| 设备管理 | [STREAMS_PER_DEVICE](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/STREAMS_PER_DEVICE.md) | 通过此环境变量可配置 stream pool 的最大流数。 |
| 设备管理 | [TORCH_NPU_DEVICE_CAPABILITY](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/TORCH_NPU_DEVICE_CAPABILITY.md) | 通过此环境变量可配置 `torch_npu.npu.get_device_capability()` 的返回值。 |
| 设备管理 | [TORCH_TRANSFER_TO_NPU](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/TORCH_TRANSFER_TO_NPU.md) | 通过此环境变量可配置是否自动启用 transfer_to_npu 功能，将 PyTorch 的 CUDA 相关 API 自动替换为 NPU 对应 API。 |
| 图模式 | [TORCHINDUCTOR_NPU_BACKEND](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/TORCHINDUCTOR_NPU_BACKEND.md) | 通过该环境变量可配置图模式下的优化模式，支持 Triton、MLIR、DVM 等优化模式。 |
| 图模式 | [（beta）INDUCTOR_ASCEND_CHECK_ACCURACY](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/INDUCTOR_ASCEND_CHECK_ACCURACY.md) | INDUCTOR_ASCEND_CHECK_ACCURACY 是 Ascend Extension for PyTorch 提供的精度校验工具，仅在 torch.compile 图编译后端为 "Inductor" 且模式为 "Triton" 时自动检测融合算子的数值精度。 |

**逐类解读（条目归并与共性说明）：**

- **算子执行（7 条）**：覆盖 AI 处理器数值处理模式（`INF_NAN_MODE_ENABLE` / `INF_NAN_MODE_FORCE_DISABLE`，后者仅 Atlas A2/A3 训练系列产品）、combined 标志位（`COMBINED_ENABLE`）、算子下发同步/异步切换（`ASCEND_LAUNCH_BLOCKING`）以及 task_queue 下发策略（`TASK_QUEUE_ENABLE` 含开关+优化等级、`PER_STREAM_QUEUE` 对应 per-stream 队列）、社区一致性（`TORCH_NPU_USE_COMPATIBLE_IMPL`）。本类是算子下发"通道层"的控制面。
- **算子编译（2 条）**：`ACL_OP_COMPILER_CACHE_DIR`（目录）与 `ACL_OP_COMPILER_CACHE_MODE`（模式）成对管理算子磁盘缓存。
- **内存管理（6 条）**：`PYTORCH_NPU_ALLOC_CONF`（缓存分配器行为，性能敏感，原文提示可能造成波动）、`PYTORCH_NO_NPU_MEMORY_CACHING`（关闭内存复用）、`OOM_SNAPSHOT_ENABLE` / `OOM_SNAPSHOT_PATH`（OOM 现场 dump 开关与路径，成对使用）、`MULTI_STREAM_MEMORY_REUSE`（多流复用）、`TORCH_NPUGRAPH_GC`（NPUGraph Capture 中的 Python GC 主动触发开关）。
- **集合通信（6 条）**：依托 HCCL 后端，含异步错误处理（`HCCL_ASYNC_ERROR_HANDLING`）、超时分析（`HCCL_DESYNC_DEBUG`）、Event 超时（`HCCL_EVENT_TIMEOUT`）、P2P + 独立通信域（`P2P_HCCL_BUFFSIZE`）、RANK_TABLE_FILE 建链（`RANK_TABLE_FILE`）、片内零拷贝（`(beta) TORCH_HCCL_ZERO_COPY`，目标为降低片内拷贝次数、降低通信对显存带宽的抢占）。
- **告警信息打印（4 条）**：`TORCH_NPU_DISABLED_WARNING`（告警是否打印）、`TORCH_NPU_COMPACT_ERROR_OUTPUT`（精简错误输出，将自定义栈转移到 plog）、`TORCH_NPU_LOGS`（新增模块日志功能）、`TORCH_NPU_LOGS_FILTER`（通过黑白名单筛选日志）。
- **同步超时（1 条）**：`ACL_DEVICE_SYNC_TIMEOUT`，独立成类，控制设备同步超时。
- **特征值检测（4 条，版本分界明显）**：
  - 7.0.0 及之前：`NPU_ASD_ENABLE` + `NPU_ASD_UPPER_THRESH`（绝对阈值） + `NPU_ASD_SIGMA_THRESH`（相对阈值）；
  - 7.1.0 及之后：`NPU_ASD_CONFIG`（统一开关与配置，替代表述）。
  - 即 7.1.0 起 3 个旧变量被收敛为一个 `NPU_ASD_CONFIG`。
- **性能优化（3 条）**：`CPU_AFFINITY_CONF`（粗/细粒度绑核，优化跨 NUMA 与缓存命中）、`PROF_CONFIG_PATH`（dynamic_profile 的 profiler_config.json 路径）、`KINETO_USE_DAEMON`（通过 msMonitor 开启 dynamic_profile，原文含 "nputrace" 字样，疑为输入笔误，照原文保留）。
- **设备管理（3 条）**：`STREAMS_PER_DEVICE`（stream pool 最大流数）、`TORCH_NPU_DEVICE_CAPABILITY`（覆盖 `torch_npu.npu.get_device_capability()` 返回值）、`TORCH_TRANSFER_TO_NPU`（CUDA API → NPU API 的自动迁移开关，方便基于 CUDA 的脚本迁移）。
- **图模式（2 条）**：`TORCHINDUCTOR_NPU_BACKEND`（后端支持 Triton / MLIR / DVM）、`（beta）INDUCTOR_ASCEND_CHECK_ACCURACY`（仅在 torch.compile 后端 "Inductor" + 模式 "Triton" 时生效）。

## 【公式解读】

原文无公式。

## 【关联】

- 本页首部正文段中提到的外部手册链接（用于环境变量职责划分）：《[CANN 环境变量参考](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0001.html)》——处理"基于 CANN 构建 AI 应用和业务"的环境变量，与本页（Ascend Extension for PyTorch 层）形成上下游分层关系。
- 表 1 中 **每一条环境变量** 都附有指向其明细页的链接，全部位于 `https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/<VAR>.md` 这一固定路径模板下，构成"索引页 → 单变量详情页"的二级知识结构。
- 按功能拓扑，可将 40 条变量归并为四条主线：
  1. **算子下发与缓存**（算子执行 7 + 算子编译 2）；
  2. **资源生命周期**（内存管理 6 + 设备管理 3 + 同步超时 1）；
  3. **分布式训练栈**（集合通信 6）；
  4. **可观测性与优化**（告警信息打印 4 + 特征值检测 4 + 性能优化 3 + 图模式 2）。

## 【使用方法】

原文未涉及可直接照抄的命令/配置/环境变量用法示例（本页仅为索引式清单页，所有具体取值与命令需跳转至各变量独立说明页查阅）。
