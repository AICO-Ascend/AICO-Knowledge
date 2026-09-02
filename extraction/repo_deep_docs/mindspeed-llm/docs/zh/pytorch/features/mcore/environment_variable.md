# 模型脚本环境变量介绍

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/mcore/environment_variable.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/mcore/environment_variable.md

# mindspeed-llm 模型脚本环境变量文档深度解读

## 【定位】

本文档是昇腾 LLM 分布式训练框架 mindspeed-llm 中,针对模型训练脚本所依赖的环境变量的速查参考表,系统罗列了 15 个常用环境变量(同步模式、HCCL 通信、内存管理、算子优化、绑核、可见设备等)的作用、取值含义与官方文档链接,用于让用户在不阅读全部源码的前提下理解各脚本启动/运行参数的语义与影响。

---

## 【技术要点】

1. **算子下发与同步控制**:`ASCEND_LAUNCH_BLOCKING`(1 强制同步、0 关闭),与 `TASK_QUEUE_ENABLE`(0 关闭 / 1 Level 1 / 2 Level 2)共同构成算子下发模式与任务队列优化的两轴控制。
2. **HCCL 分布式通信配置**:包括 `HCCL_WHITELIST_DISABLE`(白名单开关 1-关闭/0-开启)、`HCCL_CONNECT_TIMEOUT`(超时,默认 **120**)、`HCCL_SOCKET_IFNAME`(网卡)、`HCCL_LOGIC_SUPERPOD_ID`(ROCE 多机超节点 ID,范围 0~N)、`HCCL_ASYNC_ERROR_HANDLING`(默认 **1**,即开启异步错误处理)。
3. **NPU 设备与拓扑可见性**:`ASCEND_RT_VISIBLE_DEVICES` 限制进程可见的 Device ID;`NPUS_PER_NODE` 指定每计算节点使用的 NPU 数量。
4. **内存与硬件队列**:`PYTORCH_NPU_ALLOC_CONF` 通过 `expandable_segments:True/False` 开关进行内存碎片回收;`CUDA_DEVICE_MAX_CONNECTIONS` 定义任务流可映射到的硬件队列数量。
5. **算子组合优化**:`COMBINED_ENABLE`(0/1)用于优化**非连续两个算子组合类**场景。
6. **CPU 亲和性与检测**:`CPU_AFFINITY_CONF` 控制粗/细粒度绑核,降低跨 NUMA 访问与调度开销;`NPU_ASD_ENABLE` 提供四级(0/1/2/3)异常检测与告警策略。

---

## 【关键机制与数据】

- **任务队列与同步的耦合约束(原文)**:`ASCEND_LAUNCH_BLOCKING=1` 会"屏蔽 task_queue 队列优化功能"——意味着 `TASK_QUEUE_ENABLE` 会在同步模式下被强制失效;反之 `=0` 在异步路径下"会增加内存消耗,有 OOM 的风险"。
- **日志输出开关(原文)**:`ASCEND_SLOG_PRINT_TO_STDOUT=1` 时日志不再落盘、直接打屏(可能造成日志丢失);`=0` 时日志落到 log 文件。
- **HCCL 默认值(原文)**:`HCCL_CONNECT_TIMEOUT` 默认 **120**;`HCCL_ASYNC_ERROR_HANDLING` 默认 **1**(开启)。
- **内存碎片优化(原文)**:`PYTORCH_NPU_ALLOC_CONF` 默认 `expandable_segments:False`,开启时设为 `expandable_segments:True`,用于"内存管理和碎片回收"。
- **算子组合优化目标(原文)**:`COMBINED_ENABLE=1` 用于"优化**非连续两个算子组合类**场景"。
- **检测策略分级(原文)**:`NPU_ASD_ENABLE` 四级——0 关闭 / 1 仅打印异常日志不告警 / 2 告警 / 3 告警并在 Device 侧 info 日志记录过程数据。
- **CPU 绑核收益(原文)**:可避免线程抢占、提高缓存命中、避免跨 NUMA 内存访问、减少任务调度开销,从而"优化任务执行效率"。
- **多机拓扑(原文)**:`HCCL_LOGIC_SUPERPOD_ID` 在走 ROCE 时,"不同多机超节点 ID 不同,范围 0~N"。

---

## 【表格解读】

下表为**原文表格的逐字还原**(精简链接列以保持可读性):

| 环境变量名称 | 环境变量描述 |
|---|---|
| ASCEND_LAUNCH_BLOCKING | 1:强制算子采用同步模式运行会导致性能下降,会屏蔽 task_queue 队列优化功能;0:会增加内存消耗,有 OOM 的风险。 |
| ASCEND_SLOG_PRINT_TO_STDOUT | 0:关闭日志打屏,日志采用默认输出方式,将日志保存在 log 文件中;1:开启日志打屏,日志将不会保存在 log 文件中,直接打屏显示。 |
| HCCL_WHITELIST_DISABLE | HCCL 白名单开关,1-关闭/0-开启。 |
| HCCL_CONNECT_TIMEOUT | 设置 HCCL 超时时间,默认值为 120。 |
| CUDA_DEVICE_MAX_CONNECTIONS | 定义了任务流能够利用或映射到的硬件队列的数量。 |
| TASK_QUEUE_ENABLE | 用于控制开启 task_queue 算子下发队列优化的等级:0:关闭;1:开启 Level 1 优化;2:开启 Level 2 优化。 |
| COMBINED_ENABLE | 设置 combined 标志。0:表示关闭此功能;1:表示开启此功能,用于优化非连续两个算子组合类场景。 |
| PYTORCH_NPU_ALLOC_CONF | 内存碎片优化开关,默认是 `expandable_segments:False`,使能时配置为 `expandable_segments:True`,用于内存管理和碎片回收。 |
| ASCEND_RT_VISIBLE_DEVICES | 指定哪些 Device 对当前进程可见,支持一次指定一个或多个 Device ID。通过该环境变量,可实现不修改应用程序即可调整所用 Device 的功能。 |
| NPUS_PER_NODE | 配置一个计算节点上使用的 NPU 数量。 |
| HCCL_SOCKET_IFNAME | 指定 HCCL Socket 通讯走的网卡配置。 |
| GLOO_SOCKET_IFNAME | 指定 Gloo Socket 通讯走的网卡配置。 |
| HCCL_LOGIC_SUPERPOD_ID | 指定当前设备的逻辑超节点 ID,如果走 ROCE,不同多机超节点 ID 不同,0~N。 |
| CPU_AFFINITY_CONF | 开启粗/细粒度绑核。该配置能够避免线程间抢占,提高缓存命中,避免跨 NUMA 节点的内存访问,减少任务调度开销,优化任务执行效率。 |
| NPU_ASD_ENABLE | 0:关闭检测功能;1:开启特征值检测功能,打印异常日志,不告警;2:开启,并告警;3:开启,告警,并在 Device 侧 info 级别日志中记录过程数据。 |
| HCCL_ASYNC_ERROR_HANDLING | 当使用 HCCL 作为通信后端时,通过此环境变量可控制是否开启异步错误处理,默认值为 1。0:不开启异步错误处理;1:开启异步错误处理。 |

### 逐行解读

- **ASCEND_LAUNCH_BLOCKING**:同步调试专用开关,取 1 会强制算子同步并**禁用** `TASK_QUEUE_ENABLE` 的队列优化;取 0 则回到异步执行,但有 OOM 风险——属于"调试-性能-稳定性"三角取舍。
- **ASCEND_SLOG_PRINT_TO_STDOUT**:日志去向二选一开关,1 打屏(便于实时观察)但**不落盘**;0 走默认落盘路径。
- **HCCL_WHITELIST_DISABLE**:反向语义开关(1-关闭/0-开启),用于控制 HCCL 算子白名单是否生效,常用于兼容未入库的新算子。
- **HCCL_CONNECT_TIMEOUT**:通信建链超时,单位为秒,默认 120——在大规模集群网络抖动场景可调大。
- **CUDA_DEVICE_MAX_CONNECTIONS**:任务流到硬件队列的映射容量,影响流水线并行度。
- **TASK_QUEUE_ENABLE**:算子下发队列优化的**三档**等级,Level 2 优化通常更深(包含算子融合/合并类增强),但与同步模式互斥。
- **COMBINED_ENABLE**:针对"非连续两个算子组合"场景的合并优化,适合 reduce-broadcast、cast+gemm 等相邻算子场景。
- **PYTORCH_NPU_ALLOC_CONF**:`expandable_segments` 内存分配器开关,True 启用段扩展策略以缓解碎片,适合长稳训练。
- **ASCEND_RT_VISIBLE_DEVICES**:运行时层级的设备可见性裁剪,与代码层 `torch.npu.set_device` 不同——它作用于**进程级** Device 列表。
- **NPUS_PER_NODE**:声明单节点 NPU 数,与分布式 launcher 的 rank 分配配合使用。
- **HCCL_SOCKET_IFNAME** / **GLOO_SOCKET_IFNAME**:通信库(Socket 层)所走网卡配置,通常指向 RDMA/高速网卡。
- **HCCL_LOGIC_SUPERPOD_ID**:逻辑超节点 ID,ROCE 多机场景下用于将不同物理机划入不同 SuperPod 域,影响集合通信拓扑。
- **CPU_AFFINITY_CONF**:CPU 绑核,降低跨核/跨 NUMA 抖动,直接提升数据加载与算子调度效率。
- **NPU_ASD_ENABLE**:异常自检测(Anomaly Self Detection)开关,1 仅记录、2 告警、3 告警 + 记录过程数据,排障逐级打开。
- **HCCL_ASYNC_ERROR_HANDLING**:通信后端异步错误处理,默认 1 开启,排障时可设 0 强制同步报错以精确定位。

---

## 【公式解读】

**原文无公式。**(本文档为环境变量参考表,无数学公式或伪代码。)

---

## 【关联】

- **与算子下发/同步链路的关系**:`ASCEND_LAUNCH_BLOCKING` 与 `TASK_QUEUE_ENABLE` 在行为上互斥(同步模式会屏蔽队列优化),二者属于同一控制面的两个旋钮。
- **与 HCCL 分布式通信栈的关系**:`HCCL_WHITELIST_DISABLE`、`HCCL_CONNECT_TIMEOUT`、`HCCL_SOCKET_IFNAME`、`HCCL_LOGIC_SUPERPOD_ID`、`HCCL_ASYNC_ERROR_HANDLING` 共同覆盖了 HCCL 通信库的**白名单/超时/网卡/拓扑/错误处理**五个维度。
- **与进程级设备管理的关系**:`ASCEND_RT_VISIBLE_DEVICES`(运行时)与 `NPUS_PER_NODE`(节点容量声明)分别从"哪些设备可用"和"每个节点声明多少设备"两个角度参与拓扑装配。
- **与内存/性能调优链的关系**:`PYTORCH_NPU_ALLOC_CONF`(内存) ↔ `CUDA_DEVICE_MAX_CONNECTIONS`(队列) ↔ `CPU_AFFINITY_CONF`(CPU)构成 host-device 端到端的资源与调度协同。
- **与可观测性/可调试性的关系**:`ASCEND_SLOG_PRINT_TO_STDOUT`(日志去向)+ `NPU_ASD_ENABLE`(异常检测)+ `HCCL_ASYNC_ERROR_HANDLING`(通信错误处理)共同构成可观测与可调试的最小工具集。
- **文档内部链接**:原文未提供本文档与其他特性文档之间的内部链接(标注"无");文中的所有链接均指向外部 HiAscend 官方环境变量参考。

---

## 【使用方法】

**启用方式/配置项/命令**(全部基于原文表格内容,无额外信息添加):

1. **同步调试**:`export ASCEND_LAUNCH_BLOCKING=1`(注意会屏蔽 `TASK_QUEUE_ENABLE` 的队列优化)。
2. **算子队列优化(异步路径)**:`export TASK_QUEUE_ENABLE=1`(Level 1)或 `=2`(Level 2)。
3. **算子合并**:`export COMBINED_ENABLE=1`,用于优化非连续两个算子组合场景。
4. **内存碎片回收**:`export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`(默认 `False`)。
5. **进程级 Device 裁剪**:`export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3`(支持多 ID);配合 `export NPUS_PER_NODE=N` 声明每节点 NPU 数。
6. **HCCL 通信调优**:
   - `export HCCL_WHITELIST_DISABLE=1`(关闭白名单);
   - `export HCCL_CONNECT_TIMEOUT=<秒>`(默认 120);
   - `export HCCL_SOCKET_IFNAME=<网卡名>`;若使用 Gloo 通信则 `export GLOO_SOCKET_IFNAME=<网卡名>`;
   - ROCE 多机下 `export HCCL_LOGIC_SUPERPOD_ID=<0~N>`;
   - `export HCCL_ASYNC_ERROR_HANDLING=0` 可关闭异步错误处理以便精确定位(默认 1)。
7. **CPU 绑核**:`export CPU_AFFINITY_CONF=...(开启粗/细粒度绑核)`。
8. **硬件队列数量**:`export CUDA_DEVICE_MAX_CONNECTIONS=<N>`。
9. **日志打屏**:`export ASCEND_SLOG_PRINT_TO_STDOUT=1`(注意此时**不会**保存到 log 文件)。
10. **NPU 异常检测**:`export NPU_ASD_ENABLE=1`(仅日志)/ `=2`(告警)/ `=3`(告警 + Device 侧 info 过程日志)。

> 注:除 `ASCEND_LAUNCH_BLOCKING`、`ASCEND_SLOG_PRINT_TO_STDOUT`、`HCCL_WHITELIST_DISABLE`、`CUDA_DEVICE_MAX_CONNECTIONS`、`NPUS_PER_NODE`、`GLOO_SOCKET_IFNAME` 外,其余变量原文均提供了 HiAscend 官方详细文档链接,可作为深度调优时进一步参考的依据。
