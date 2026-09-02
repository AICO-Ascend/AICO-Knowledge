# Model Script Environment Variables

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/environment_variable.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/environment_variable.md

# Model Script Environment Variables — 深度解读

## 【定位】
这篇文档是 mindspeed-llm（昇腾LLM分布式训练框架）面向 Megatron-Core (mcore) 模型脚本的一站式**环境变量参考手册**，集中罗列并解释其上层模型脚本所依赖的全部可调环境变量，覆盖同步/异步、日志、HCCL 集合通信、内存、算子调度、网卡、CPU 亲和、异常检测等维度，供用户在调参、排障、性能调优时按需设置。

---

## 【技术要点】

1. **同步控制开关 `ASCEND_LAUNCH_BLOCKING`**：`1` 强制算子同步执行（性能下降并关闭 `task_queue` 优化），`0` 则相反（增大显存占用、有 OOM 风险）。
2. **算子调度优化 `TASK_QUEUE_ENABLE`**：三档 `0`/`1`/`2`，分别对应关闭、级别 1、级别 2 的 `task_queue` 算子派发队列优化。
3. **算子融合 `COMBINED_ENABLE`**：`0` 关闭，`1` 启用针对"两个非连续算子组合"的优化场景。
4. **通信层相关 HCCL 变量**：
   - `HCCL_WHITELIST_DISABLE`：`1` 禁用白名单，`0` 启用。
   - `HCCL_CONNECT_TIMEOUT`：默认 `120`（秒）。
   - `HCCL_ASYNC_ERROR_HANDLING`：默认 `1`（启用异步错误处理），`0` 关闭。
   - `HCCL_SOCKET_IFNAME` / `HCCL_LOGIC_SUPERPOD_ID`（ROCE 下从 `0` 到 `N`）：分别配置通信网卡与逻辑 SuperPoD 标识。
5. **显存碎片治理 `PYTORCH_NPU_ALLOC_CONF`**：默认 `expandable_segments:False`；设为 `expandable_segments:True` 启用显存可扩展段与碎片回收。
6. **设备与节点拓扑可见性**：`ASCEND_RT_VISIBLE_DEVICES`（多设备 ID）、`NPUS_PER_NODE`（每节点 NPU 数）、`CUDA_DEVICE_MAX_CONNECTIONS`（任务流可映射的硬件队列数）。
7. **网卡与进程间通信**：`GLOO_SOCKET_IFNAME`（Gloo 通信网卡）。
8. **CPU 亲和 `CPU_AFFINITY_CONF`**：粗/细粒度核心绑定，目的包括避免线程争用、提升缓存命中率、规避跨 NUMA 内存访问、降低调度开销。
9. **异常/告警检测 `NPU_ASD_ENABLE`**：四档 `0`/`1`/`2`/`3`，依次为关闭、仅打日志不上报、上报告警、追加 `info` 级端侧日志记录。
10. **日志输出 `ASCEND_SLOG_PRINT_TO_STDOUT`**：`0` 走默认落盘，`1` 屏幕打印且不再保存为日志文件。

---

## 【关键机制与数据】

- **同步 vs 异步执行的权衡（原文）**：原文指出 `ASCEND_LAUNCH_BLOCKING=1` 会强制同步、降低性能并禁用 `task_queue` 优化；`=0` 则增加显存占用并带来 OOM 风险——即同步性、显存、性能三者之间的取舍。
- **超时与容错默认值（原文）**：`HCCL_CONNECT_TIMEOUT` 默认 `120`；`HCCL_ASYNC_ERROR_HANDLING` 默认 `1`（启用异步错误处理）。
- **多机 SuperPoD 寻址（原文）**：使用 ROCE 时，`HCCL_LOGIC_SUPERPOD_ID` 取值为 `0` 至 `N`，不同多节点 SuperPoD 对应不同 ID。
- **内存优化开关（原文）**：`PYTORCH_NPU_ALLOC_CONF` 默认 `expandable_segments:False`，切换为 `True` 后启用显存管理与碎片回收。
- **算子派发与融合（原文）**：`TASK_QUEUE_ENABLE` 提供 0/1/2 三档派发队列优化；`COMBINED_ENABLE=1` 用于"两个非连续算子组合"的优化场景。
- **异常分级（原文）**：`NPU_ASD_ENABLE` 提供 `0`/`1`/`2`/`3` 四档，分别对应：关闭、仅异常日志不上报、同时上报告警、追加 `info` 级端侧日志。
- **CPU 亲和收益（原文）**：原文列出五项目标——避免线程争用、提升缓存命中率、规避跨 NUMA 内存访问、降低任务调度开销、提升任务执行效率。

> 注：上述均逐字来自原文表格的 Description 列；除表中明确给出的默认值（120、1、expandable_segments:False）与可枚举取值集合外，未给出量化性能数据。

---

## 【表格解读】

> 以下表格**逐字**还原原文：

| Environment Variable | Description |
|-----------------------------|-------------------------------------|
| [ASCEND_LAUNCH_BLOCKING](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/ASCEND_LAUNCH_BLOCKING.md) | `1`: Forces operators to run in synchronous mode. This degrades performance and disables the `task_queue` optimization feature.<br>`0`: This increases memory use and creates an out-of-memory (OOM) risk. |
| [ASCEND_SLOG_PRINT_TO_STDOUT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0121.html) | `0`: Disables log output to the screen. Logs use the default output method and are saved in log files.<br>`1`: Enables log output to the screen. Logs are not saved in log files and are printed directly to the screen. |
| [HCCL_WHITELIST_DISABLE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0156.html) | Enables or disables the HCCL allowlist. `1` disables it, and `0` enables it. |
| [HCCL_CONNECT_TIMEOUT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0077.html) | Sets the HCCL timeout. The default value is `120`. |
| CUDA_DEVICE_MAX_CONNECTIONS | Specifies the number of hardware queues that a task stream can use or map to. |
| [TASK_QUEUE_ENABLE](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/TASK_QUEUE_ENABLE.md) | Controls the optimization level of the `task_queue` operator dispatch queue.<br>`0`: Disables optimization.<br>`1`: Enables level 1 optimization.<br>`2`: Enables level 2 optimization. |
| [COMBINED_ENABLE](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/COMBINED_ENABLE.md) | Sets the `combined` flag.<br>`0`: Disables this feature.<br>`1`: Enables this feature for optimized scenarios that combine two non-contiguous operators. |
| [PYTORCH_NPU_ALLOC_CONF](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/PYTORCH_NPU_ALLOC_CONF.md) | Switch for memory fragmentation optimization. The default value is `expandable_segments:False`. Set the value to `expandable_segments:True` to enable memory management and fragmentation reclamation. |
| [ASCEND_RT_VISIBLE_DEVICES](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0028.html) | Specifies which devices are visible to the current process. You can specify one or more device IDs at a time. This environment variable lets you adjust the devices in use without modifying the application. |
| NPUS_PER_NODE` | Configures the number of NPUs used on a compute node. |
| [HCCL_SOCKET_IFNAME](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0075.html) | Specifies the network interface card configuration used for HCCL Socket communication. |
| GLOO_SOCKET_IFNAME | Specifies the network interface card configuration used for Gloo Socket communication. |
| [HCCL_LOGIC_SUPERPOD_ID](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0100.html) | Specifies the logical SuperPoD ID of the current device. If you use ROCE, different multi-node superpods have different IDs, from `0` to `N`. |
| [CPU_AFFINITY_CONF](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/CPU_AFFINITY_CONF.md) | Enables coarse-grained or fine-grained CPU core binding. This configuration helps avoid thread contention, improve cache hit rates, avoid memory access across NUMA nodes, reduce task scheduling overhead, and improve task execution efficiency. |
| [NPU_ASD_ENABLE](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/NPU_ASD_ENABLE.md) | `0`: Disables detection.<br>`1`: Enables feature detection, prints exception logs, and does not raise alarms.<br>`2`: Enables detection and raises alarms.<br>`3`: Enables detection, raises alarms, and records process data in device-side logs at the `info` level. |
| [HCCL_ASYNC_ERROR_HANDLING](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/HCCL_ASYNC_ERROR_HANDLING.md) | When you use HCCL as the communication backend, this environment variable controls whether asynchronous error handling is enabled. The default value is `1`.<br>`0`: Disables asynchronous error handling.<br>`1`: Enables asynchronous error handling. |

**逐行解读**：
1. `ASCEND_LAUNCH_BLOCKING` — 算子同步开关；`1` 同步（性能降、关 `task_queue`），`0` 异步（显存涨、OOM 风险）。
2. `ASCEND_SLOG_PRINT_TO_STDOUT` — 日志输出目的地；`0` 走默认落盘，`1` 屏幕打印且不落盘。
3. `HCCL_WHITELIST_DISABLE` — HCCL 算子白名单；`1` 关闭、`0` 启用。
4. `HCCL_CONNECT_TIMEOUT` — HCCL 建链超时；默认 `120`。
5. `CUDA_DEVICE_MAX_CONNECTIONS` — 单个任务流可使用/映射的硬件队列数（参数名沿用 CUDA 命名习惯）。
6. `TASK_QUEUE_ENABLE` — `task_queue` 算子派发队列优化级别；三档 `0`/`1`/`2`。
7. `COMBINED_ENABLE` — 两个非连续算子组合优化；`0` 关、`1` 开。
8. `PYTORCH_NPU_ALLOC_CONF` — NPU 显存分配策略；默认 `expandable_segments:False`，`True` 启用碎片回收。
9. `ASCEND_RT_VISIBLE_DEVICES` — 当前进程可见 NPU 设备集合；可运行时调设备无需改代码。
10. `NPUS_PER_NODE` — 单计算节点使用的 NPU 数（原文存在一处额外反引号，此处按原文忠实保留）。
11. `HCCL_SOCKET_IFNAME` — HCCL Socket 通信所用网卡。
12. `GLOO_SOCKET_IFNAME` — Gloo Socket 通信所用网卡。
13. `HCCL_LOGIC_SUPERPOD_ID` — 逻辑 SuperPoD 标识；ROCE 下多机 SuperPoD 各自取 `0`…`N`。
14. `CPU_AFFINITY_CONF` — 粗/细粒度 CPU 绑定；改善争用、缓存、跨 NUMA、调度、执行效率。
15. `NPU_ASD_ENABLE` — 异常/告警检测；四档 `0`/`1`/`2`/`3` 由弱到强逐步加入日志与端侧日志记录。
16. `HCCL_ASYNC_ERROR_HANDLING` — HCCL 异步错误处理；默认 `1` 启用。

---

## 【公式解读】
原文无公式。

---

## 【关联】
- 文档首句提到 "the scripts in the preceding model list"，说明本文是一组**模型脚本（model list）**的共享环境变量参考，与上游的「模型列表」章节是父子文档关系；为避免重复，每个模型页不再逐一列出这些通用变量。
- 涉及的子系统维度与潜在关联：
  - **集合通信**：`HCCL_*` 系列变量 → 对应 HCCL 通信库，配置多节点/多 SuperPoD 拓扑与容错。
  - **算子运行时**：`TASK_QUEUE_ENABLE`、`COMBINED_ENABLE`、`ASCEND_LAUNCH_BLOCKING` → 影响 CANN/PyTorch-NPU 适配层中算子的派发、合并与同步行为。
  - **内存管理**：`PYTORCH_NPU_ALLOC_CONF` → 与 PyTorch-NPU 显存分配器（caching allocator）联动。
  - **设备可见性**：`ASCEND_RT_VISIBLE_DEVICES`、`NPUS_PER_NODE` → 配合 `torch.distributed` 启动器，决定 rank↔device 映射。
  - **CPU 亲和**：`CPU_AFFINITY_CONF` → 与主机 OS 调度器及 NUMA 拓扑交互。
  - **诊断**：`NPU_ASD_ENABLE` → 联动设备侧健康/异常检测与日志通道。
  - **跨通信后端**：`HCCL_SOCKET_IFNAME` 与 `GLOO_SOCKET_IFNAME` 分别面向集合通信与 Gloo 后端，影响分布式启动与控制面。

> 注：原文文末无内部链接列表（标记为"无"）。

---

## 【使用方法】
本文为**环境变量参考表**，未给出具体的启动脚本或命令行示例，原文仅以"取值与含义"形式给出每个变量的使用语义。可归纳为：
- 在运行模型脚本前，通过 shell 直接 `export` 所需变量即可生效。
- 默认值（按原文给出的）：
  - `HCCL_CONNECT_TIMEOUT = 120`
  - `HCCL_ASYNC_ERROR_HANDLING = 1`
  - `PYTORCH_NPU_ALLOC_CONF` 默认 `expandable_segments:False`
- 多档取值（按原文给出的枚举）：
  - `ASCEND_LAUNCH_BLOCKING ∈ {0, 1}`
  - `ASCEND_SLOG_PRINT_TO_STDOUT ∈ {0, 1}`
  - `HCCL_WHITELIST_DISABLE ∈ {0, 1}`
  - `TASK_QUEUE_ENABLE ∈ {0, 1, 2}`
  - `COMBINED_ENABLE ∈ {0, 1}`
  - `NPU_ASD_ENABLE ∈ {0, 1, 2, 3}`
  - `HCCL_ASYNC_ERROR_HANDLING ∈ {0, 1}`

原文未给出具体的 export 命令、torchrun/分布式启动参数或脚本调用样例，因此具体的"启用方式/完整配置项/命令"以原文为准——**原文未涉及**具体的启动命令模板，仅提供各变量取值的语义说明。
