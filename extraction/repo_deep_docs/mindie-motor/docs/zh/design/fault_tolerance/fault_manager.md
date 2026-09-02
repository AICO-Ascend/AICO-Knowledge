# FaultManager 故障管理器设计文档

> 仓 `mindie-motor` · 路径 `docs/zh/design/fault_tolerance/fault_manager.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/design/fault_tolerance/fault_manager.md

# FaultManager 故障管理器设计文档 — 一体化深度解读

## 【定位】

这篇文档系统描述了 MindIE Motor Controller 中 FaultManager 故障容错管理器的架构设计、数据模型、故障上报链路、等级映射与节点所有权交换机制，作为 Controller 端硬件/软件故障统一处理与跨实例节点迁移的权威参考。

## 【技术要点】

- **架构模式**：FaultManager 采用 Mixin 模式将功能拆分为 `_ResourceManagerMixin`（节点同步/资源监控）与 `_PersistenceMixin`（ETCD 持久化），主类继承自 `ThreadSafeSingleton` 与 `Observer`，所有 Mixin 不声明 `__init__`，成员属性由 `FaultManager.__init__` 统一初始化。
- **能力边界**：Engine Server 已删除；NodeManager **直接轮询**原生引擎的 `/fault_tolerance/status` HTTP 接口（vLLM FT API），启用 FaultReporter 时**必须由目标引擎版本提供该接口**。
- **故障等级分层**：`FaultLevel` 分 L1～L6（HEALTHY=0 表示无故障），对应从「不处理」「可自愈」「业务级重启」「空闲重启 NPU」「立即重启 NPU」到「隔离 NPU（致命）」的递进处理。
- **软件故障上报**：FaultReporter 周期性 GET `/fault_tolerance/status`（间隔 `poll_interval_sec`），仅上报 dead/unhealthy 状态变更；连续 `max_poll_failures` 次失败按 dead 上报；引擎重拉期间由 Daemon 暂停/恢复并清空轮询状态。
- **动态等级调整**：`PreSeparateNPU` 不做静态映射——若节点上有 INITIAL/ACTIVE 实例则降为 L2（可自愈、正常参与等级计算）；若节点无活跃实例则保持 L6（不参与实例级故障计算、不触发 `separate_instance()` 与 `scale_p2d`）。
- **节点所有权交换**：物理节点（`node_name`）是稳定标识，`INSTANCE_REMOVED` 时仅删 `InstanceMetadata` 而保留 `NodeMetadata`；`_swap_node_ownership` 等量配对外来源节点与孤儿节点，实现故障记录随物理节点迁移到新实例。

## 【关键机制与数据】

- **工作原理**：硬件故障由 ResourceMonitor 监听 ConfigMap 上报，触发 `_handle_fault_info_update`；软件故障由 NodeManager/FaultReporter 经 HTTP API 上报，触发 `report_software_fault(pod_ip)` → 累加至 `NodeMetadata.software_fault_infos` → 调用 `_refresh_instance_fault_level()` 综合硬件+软件故障 → 更新 `InstanceMetadata.fault_level` → 策略中心按等级生成/升级恢复策略。
- **端到端上报链路**：`vllm EngineCore 异常 → 引擎状态 unhealthy/dead → FaultReporter HTTP GET /fault_tolerance/status → 去重 → _send_fault_to_controller() 注入 pod_ip → ControllerApiClient.report_software_fault() → POST /controller/report_software_fault → FaultManager.report_software_fault(pod_ip)`。
- **状态去重**：仅上报 dead/unhealthy 变更；轮询成功 → 状态正常则不上报；连续失败 → 按 dead 上报，避免抖动。
- **故障分类与存储**：`NodeMetadata` 中硬件故障按 `fault_code` 做 key 覆盖刷新，软件故障按 `fault_code` 写入且不受硬件刷新影响；`_refresh_instance_fault_level` 综合两类故障评估。
- **策略降级保护**：`strategy_fault_level` 用于"新故障等级 < 当前策略等级时忽略""同级不切换策略""策略完成后清除所有软件故障"。
- **2P1D 部署示例数据**：5 个 Prefill（各 1 节点）+ 2 个 Decode（各 4 节点），共 13 个物理节点；D1 故障 2 节点、D2 故障 1 节点均触发 L6 → `scale_p2d`，D1 选中 P1/P2、D2 选中 P3 进行节点交换。
- **软件故障等级映射（原文）**：`DEAD(1) → L2 (ENGINE_DEAD)`, `UNHEALTHY(2) → L2 (ENGINE_UNHEALTHY)`；软件故障更新实例 fault_level 但**目前不触发自动恢复策略**。
- **Job_name 语义**：`job_name` 是每个实例的**唯一标识**而非角色分类，只在同实例重启时保持不变；`instance_id` 在每次重启时更新；二者组合是区分"同实例重启"与"节点跨实例迁移"的关键。

## 【表格解读】

### 表 1 — Mixin 模块职责拆分

| Mixin | 职责 | 主要方法 |
|-------|------|---------|
| `_ResourceManagerMixin` | 节点同步、所有权交换、资源监控 | `_sync_instance_nodes`, `_add_new_instance_with_nodes`, `_swap_node_ownership`, `_create_resource_monitor_for_node`, `_handle_fault_info_update`, `_handle_node_status_update` |
| `_PersistenceMixin` | ETCD 持久化与恢复 | `persist_data`, `restore_data`, `_get_next_version` |
| FaultManager 自身 | 生命周期、配置、故障评估、策略处理 | `start`, `stop`, `_refresh_instance_fault_level`, `_process_instance_strategy`, `report_software_fault` |

**逐行解读**：第一行负责所有与物理节点（node）打交道的事务——把 ConfigMap/资源/节点状态变更接入实例层，以及核心的等量交换逻辑；第二行负责 ETCD 上的状态持久化与版本号生成，确保 Controller 重启后能恢复故障上下文；第三行是主类自身职责——启停控制、配置加载、故障等级综合评估、策略匹配分发，以及暴露给上游的故障上报入口。

### 表 2 — 故障能力分层

| 层级 | 来源 | 目标态要求 |
|---|---|---|
| 通用基线 | 原生进程状态、`/health`、请求 transport/5xx/协议异常、Coordinator 熔断、ConfigMap、Node Watch | 所有原生引擎部署必须保留 |
| 引擎扩展 | vLLM `/fault_tolerance/status` | 启用 FaultReporter 时，目标引擎必须提供该 HTTP 接口 |

**逐行解读**：第一行"通用基线"是任何原生引擎部署都必备的能力，包括进程存活检查、健康检查接口、请求层异常、Coordinator 熔断、硬件故障 ConfigMap 与节点 Watch，是跨引擎兼容的兜底能力；第二行"引擎扩展"是 FaultReporter 启用时的额外依赖——目标引擎必须实现 `/fault_tolerance/status` 接口才能上报 dead/unhealthy 状态，否则只能依赖通用基线。

### 表 3 — OriginFaultLevel → FaultLevel 静态映射

| OriginFaultLevel | FaultLevel | 语义 |
|---|---|---|
| `NotHandleFault` | **L1** | 不处理 |
| `SubHealthFault` | **L1** | 亚健康通知（新增） |
| `RestartRequest` | **L2** | 请求重启 / 可自愈 |
| `RestartBusiness` | **L3** | 业务级重启 |
| `FreeRestartNPU` | **L4** | 空闲时重启 NPU |
| `RestartNPU` | **L5** | 立即重启 NPU → 触发实例隔离 |
| `SeparateNPU` | **L6** | 隔离 NPU（致命）→ 触发实例隔离 |
| `PreSeparateNPU` | **L6** (静态) | 预隔离 NPU，**运行时动态降级**（见下文） |

**逐行解读**：前 7 项均做静态映射，从"不处理（L1）"逐步递进到"致命隔离（L6）"；其中 `RestartNPU` 与 `SeparateNPU` 会触发实例隔离——意味着实例必须被踢出服务范围；`PreSeparateNPU` 在静态映射中是 L6 但**运行时动态调整**（见下一节），不能直接按静态表处理。

### 表 4 — FaultInfo 字段（统一故障模型）

| 字段 | 类型 | 含义 |
|------|------|------|
| `fault_category` | `FaultCategory` | HARDWARE / SOFTWARE |
| `fault_level` | `FaultLevel` | L1～L6（HEALTHY=0） |
| `fault_code` | `int` | 硬件故障码 或 SpecialFaultCode |
| `fault_type` | `HardwareFaultType \| None` | CARD_UNHEALTHY / CARD_NETWORK_UNHEALTHY / NODE_UNHEALTHY |
| `npu_name` | `str` | NPU 名称 |
| `origin_fault_level` | `OriginFaultLevel \| None` | 上游 ConfigMap 原始等级 |
| `exception_type` | `str \| None` | 软件异常类型（from_exception 工厂填充） |
| `exception_message` | `str \| None` | 软件异常消息 |
| `engine_id` | `int \| None` | → instance_id |
| `engine_status` | `int \| None` | EngineStatusType: 0=HEALTHY, 1=DEAD, 2=UNHEALTHY |
| `timestamp` | `str \| None` | 时间戳 |
| `additional_info` | `dict \| None` | 附加信息 |

**逐行解读**：前 6 项为公共与硬件专用字段——`fault_category` 区分软硬、`fault_level` 是评估结果、`fault_code` 作为存储与去重 key、`fault_type` 描述硬件故障大类、`npu_name` 定位到具体芯片、`origin_fault_level` 保留上游原始策略用于追溯；后 6 项为软件专用字段，由 `from_exception` 工厂方法自动填充——`exception_type/message` 描述软件异常、`engine_id` 映射回 instance_id、`engine_status` 严格遵循 0/1/2 三态枚举、`timestamp` 与 `additional_info` 提供调试信息。

### 表 5 — NodeMetadata 字段

| 字段 | 类型 | 含义 |
|------|------|------|
| `node_name` | `str` | Kubernetes 节点名（稳定标识） |
| `instance_ids` | `set[int]` | 运行在此节点的实例 ID 集合 |
| `instance_pod_ips` | `dict[int, str]` | instance_id → pod_ip |
| `instance_job_names` | `dict[int, str]` | instance_id → job_name |
| `node_status` | `NodeStatus` | READY / NOT_READY |
| `hardware_fault_infos` | `dict[int, FaultInfo]` | 硬件故障，key=fault_code |
| `software_fault_infos` | `dict[int, FaultInfo]` | 软件故障，key=fault_code |

**逐行解读**：`node_name` 是节点跨实例迁移的稳定锚点；`instance_ids`/`instance_pod_ips`/`instance_job_names` 三个集合/字典结构支持**一节点多实例**的 2P1D 部署形态；`instance_job_names` 在节点创建时设置、swap 时同步更新，文档明确指出"通过直接读 `node.instance_job_names[instance_id]` 替代频繁的 `InstanceManager.get_instance()` 查询"，体现 O(1) 字段访问的优化意图；硬件与软件故障以 `fault_code` 为 key，但硬件故障覆盖刷新而软件故障追加不覆盖，体现两类故障的处理差异。

### 表 6 — InstanceMetadata 字段

| 字段 | 类型 | 含义 |
|------|------|------|
| `instance_id` | `int` | 实例 ID |
| `fault_level` | `FaultLevel` | 当前最高故障等级（评估结果） |
| `fault_code` | `int` | 触发该等级的故障码 |
| `strategy_fault_level` | `FaultLevel` | 当前运行中策略对应的故障等级 |
| `strategy` | `Any` | 策略实例（不可序列化） |
| `lock` | `threading.Lock` | 互斥锁（不可序列化） |

**逐行解读**：`fault_level` 是评估快照、`strategy_fault_level` 是策略快照，二者解耦以实现三类行为——(1) **策略降级保护**——新等级 < 策略等级时忽略，避免低优先级故障打断高优先级恢复；(2) **同级去重**——同等级不切换策略，避免 L2 内多策略抖动；(3) **清理范围**——策略完成后清除所有软件故障；`strategy` 与 `lock` 标注不可序列化，避免 ETCD 持久化时尝试写入线程对象。

### 表 7 — 节点交换场景的物理分配

| 实例 | 旧 ID → 新 ID | job_name | 节点组成 |
|------|---------------|----------|----------|
| P1 | 1 → 10 | prefill-1 | d1_3(L6) |
| P2 | 2 → 11 | prefill-2 | d1_4(L6) |
| P3 | 3 → 12 | prefill-3 | d2_3(L6) |
| P4 | 4 → 13 | prefill-4 | p_4（未参与交换） |
| P5 | 5 → 14 | prefill-5 | p_5（未参与交换） |
| D1' | 6 → 8 | decode-1 | d1_1, d1_2, p_1, p_2 |
| D2' | 7 → 9 | decode-2 | d2_1, d2_2, d2_4, p_3 |

**逐行解读**：D1' 与 D2' 各继承了原健康节点 + 从 Prefill 换入的 P 节点（满足 4 节点规模），而 P1'/P2'/P3' 则获得了原本 D 实例的 L6 故障节点（`d1_3`、`d1_4`、`d2_3`）——这正是**故障节点随物理节点迁移**而非随实例迁移的设计：故障记录跟节点走，被换入到 P 实例后才会触发后续隔离策略；P4/P5 未参与交换保持原状。`job_name` 在新实例中保持不变（`decode-1`/`prefill-1` 等），但 `instance_id` 由旧值（1～7）变更为新值（8～14），这就是文档强调"`job_name` 不变 + `instance_id` 变化"的语义组合。

## 【公式解读】

原文无公式。

## 【关联】

- **ResourceMonitor**（`fault_manager.py` 上游）：节点级资源/故障观察者，把硬件故障通过 ConfigMap 经 `_handle_fault_info_update()` 注入 FaultManager；其创建由 `_create_resource_monitor_for_node` 完成。
- **InstanceManager**（横向协作）：故障评估结果会更新 `InstanceMetadata.fault_level`，并由策略中心驱动 `separate_instance()` 等实例级动作；早期版本需频繁 `InstanceManager.get_instance()` 查询，新版改用 `NodeMetadata.instance_job_names` 直接字段访问以解耦与提速。
- **NodeManager**（同侧跨组件）：Daemon 持有 `FaultReporter`，负责原生进程状态、`/health`、Pod 级恢复；并通过 HTTP API 把软件故障上报到 FaultManager。
- **FaultReporter**（NodeManager 持有）：周期性 HTTP 轮询 `{endpoint.business_port}/fault_tolerance/status`，去重后调用 `_send_fault_to_controller()` → `ControllerApiClient.report_software_fault()` → `POST /controller/report_software_fault`；引擎重拉期间由 Daemon 暂停/恢复。
- **Coordinator**（跨组件通用基线）：负责请求异常、熔断、实例隔离与恢复探测，与 FaultManager 在"通用基线"层级形成互补——FaultManager 偏节点/实例故障域，Coordinator 偏请求/流量域。
- **ETCD Client**：通过 `_PersistenceMixin.persist_data` / `restore_data` / `_get_next_version` 持久化故障与节点/实例元数据，支撑 Controller 重启后状态恢复。
- **vLLM EngineCore**（上游引擎）：故障源头之一，状态变化由 FaultReporter 间接观测；启用 FaultReporter 时目标引擎必须实现 `/fault_tolerance/status` HTTP 接口。
- **mind-cluster（上游集群）**：ConfigMap 上报硬件故障策略（`OriginFaultLevel`），FaultManager 通过 `map_fault_level()` 将其映射为内部 `FaultLevel`，其中 `PreSeparateNPU` 在 mind-cluster 侧表示"节点状态 `PreSeparate`，不给该 NPU 调度新任务但现有任务可继续"。
- **策略中心（`_ft_strategy_center`）**：按 `fault_level` 生成/管理恢复策略（如 `scale_p2d`）；策略完成后清除软件故障。
- **`scale_p2d` 策略**：触发节点跨实例迁移，是 `_swap_node_ownership` 的核心调用方。

## 【使用方法】

- **上报接口（Controller 侧 HTTP 端点）**：原文：`POST /controller/report_software_fault`（由 FaultReporter 经 `ControllerApiClient` 调用），入口对应 `FaultManager.report_software_fault(pod_ip)`。
- **轮询接口（引擎侧 HTTP 端点）**：原文：`GET {endpoint.business_port}/fault_tolerance/status`（vLLM FT API），目标引擎必须提供。
- **轮询参数**：原文：`poll_interval_sec`（轮询周期）、`max_poll_failures`（连续失败次数阈值，达此阈值按 dead 上报）。
- **故障等级配置映射**：通过 `map_fault_level()` 在 `OriginFaultLevel`（`NotHandleFault`/`SubHealthFault`/`RestartRequest`/`RestartBusiness`/`FreeRestartNPU`/`RestartNPU`/`SeparateNPU`/`PreSeparateNPU`）与 `FaultLevel`（L1～L6）之间建立映射，详见表 3。
- **模块依赖约束**：启用 FaultReporter 时，目标引擎必须实现 `/fault_tolerance/status` HTTP 接口，否则只能依赖通用基线（进程状态、`/health`、请求层异常、Coordinator 熔断、ConfigMap、Node Watch）。
- **配置/启用命令**：原文未涉及具体配置文件路径或 CLI 命令，仅描述类继承（`FaultManager(_PersistenceMixin, _ResourceManagerMixin, ThreadSafeSingleton, Observer)`）与单例约束。
