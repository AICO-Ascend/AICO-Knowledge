# 可靠性能力（特性说明）

> 仓 `mindie-motor` · 路径 `docs/zh/design/fault_tolerance/overview.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/design/fault_tolerance/overview.md

# 「可靠性能力（特性说明）」深度解读

---

## 【定位】

本文档系统描述 MindIE Motor 在昇腾自研推理集群管理框架下所提供的**多层可靠性保障能力**：从硬件故障感知、实例隔离、自动重拉起注册，到 PD 分离部署下「缩P保D」的资源回收策略，再到 L2 网络故障下的 token 级重推机制——构成一个完整的"故障检测 → 隔离决策 → 恢复执行"闭环。

---

## 【技术要点】

1. **核心组件三件套**：`FaultManager`（单例观察者，负责故障检测/隔离/恢复决策与策略调度）、`InstanceAssembler`（负责 Pod 重启后的实例组装与 StartCmd 下发）、`InstanceManager`（负责实例生命周期、状态机与心跳）。
2. **双重 Watch 机制**：`ResourceMonitor` 对每个 K8s Node 同时监听 `kube-system` 命名空间下的 `mindx-dl-deviceinfo-{node_name}` ConfigMap（解析 `DeviceInfoCfg` 中的 `CardUnhealthy`、`CardNetworkUnhealthy` 及 `SwitchInfoCfg`）与 K8s Node Ready/NotReady 状态变化；Node NotReady 时注入 `NODE_REBOOT` 故障（fault_code `0x0000001`，等级 L6）。
3. **七级故障体系**：HEALTHY(0) / L1 `NotHandleFault` / L2 `RestartRequest` / L3 `RestartBusiness` / L4 `FreeRestartNPU` / L5 `RestartNPU` / L6 `SeparateNPU` / `PreSeparateNPU`；阈值线为 L2——`fault > L2` 走 `separate_instance()` 强制隔离，`fault ≤ L2`（已隔离）走 `recover_instance()` 解除隔离，HEALTHY 复位。
4. **自动重拉起注册**：NodeManager 启动 → `RegisterManager._register()` 发送 `RegisterMsg`（含 job_name/role/pod_ip/parallel_config/device_num/ranktable，指数退避重试） → `InstanceAssembler.register()` 检查实例 → 轮询 `_instances_assembler_loop`（`_filter_abnormal_endpoints()` + `is_endpoints_enough()`）→ `ASSEMBLED` → `_start_command_sender` 下发 `StartCmdMsg`（job_name, role, instance_id, endpoints, master_dp_ip, ranktable） → NodeManager `parse_start_cmd()` + `Daemon.pull_engine()` + `HeartbeatManager.start()` → 状态机 INITIAL → ACTIVE。
5. **Controller 重启 re-register 场景**：NodeManager 心跳遇 503 响应 → `HeartbeatManager._reregister()` 发送 `ReregisterMsg`（携带已有 `instance_id`/`endpoints`）→ Controller 还原实例身份、**跳过 StartCmdMsg 下发**、直接交还 `InstanceManager`。
6. **ScaleP2DStrategy（缩P保D）**：仅 decode 角色 + L4/L5/L6 故障触发；L5/L6 委托 L4 策略逻辑；通过释放一个 Prefill 实例节点资源用于拉起新 Decode 实例，期间 Coordinator 检测 `readiness == ONLY_PREFILL` 自动将 `deploy_mode` 回退为 `SINGLE_NODE`（业务无感知，仅延迟增加），新 Decode 就绪后恢复 PD 分离路由——**策略方向单向**，Prefill 故障不触发。
7. **TokenReinferenceStrategy（token 级重推）**：仅白名单故障码 `{0x00f1fef5, 0x08520003}` 触发；策略 `stop()` 不执行任何操作（**不可中断**，须等待网络自愈或故障升级）；同时支持 `CardNetworkUnhealthy` 与交换机故障两条检测路径。

---

## 【关键机制与数据】

### 工作原理（故障检测 → 隔离决策 → 恢复闭环）

```
ResourceMonitor ──(ConfigMap/Node Watch)──► FaultManager._refresh_instance_fault_level()
                                                 │
                ┌────────────────────────────────┼───────────────────────────────┐
                ▼                                ▼                               ▼
        fault > L2                          fault ≤ L2 且已隔离                    HEALTHY
   separate_instance()                    recover_instance()                重置 + recover
   加入 forced_separated_instances       从强制隔离集合移除
   标记实例 INACTIVE                      为自动重拉起打开通路
```

**原文:** 隔离与恢复机制由 `FaultManager._refresh_instance_fault_level()` 驱动；`forced_separated_instances` 集合是故障隔离与自动重拉起注册之间的衔接点——只有 `recover_instance()` 解除隔离后，状态机才允许从 `INACTIVE` 恢复为 `ACTIVE`。

### 数据流（自动重拉起注册）

```
K8s Pod 重启 → NodeManager 启动 → RegisterMsg
        ↓
Controller InstanceAssembler.register()
   • NOT_REGISTERED: 创建 Instance，分配 ID
   • 添加 NodeManager 信息与 Endpoints
        ↓
_instances_assembler_loop (轮询)
   • _filter_abnormal_endpoints()  剔除异常 NodeManager
   • is_endpoints_enough()         等待所有 Pod 注册完毕
        ↓
register_status = ASSEMBLED → InstanceManager.add_instance() 接管
   • 通知观察者 INSTANCE_INITIAL
        ↓
_start_command_sender → StartCmdMsg → NodeManager
   • parse_start_cmd() 校验
   • Daemon.pull_engine() 启动原生推理引擎进程
   • HeartbeatManager.start()
        ↓
InstanceManager 收到心跳 → 状态机 INITIAL → ACTIVE
```

### 性能/规模数据

**原文:** 文档未给出具体 QPS、时延、故障恢复耗时等量化性能数据；仅给出故障码枚举（`0x0000001`、`0x00f1fef5`、`0x08520003`）和 7 级故障等级阈值（L2 为自动恢复/隔离的决策分界线）。

### token 级重推数据流

```
链路抖动/瞬断 → 驱动/固件上报 → ConfigMap 更新
        ↓
ResourceMonitor 解析 DeviceInfoCfg/SwitchInfoCfg
        ↓
FaultManager._handle_fault_info_update() → 评估为 L2
        ↓
故障等级 ≤ L2 → separate_instance()（INACTIVE）
        ↓
策略中心按 fault_code 匹配 TokenReinferenceStrategy
        ↓
策略与推理引擎协同 → 受影响 token 重推
        ↓
网络自愈 → FaultManager 感知清除 → recover_instance()
        ↓
心跳自动重注册 → ACTIVE
```

---

## 【表格解读】

### 表 1：能力总览（原文逐字还原）

| 能力 | 说明 | 核心模块 |
|------|------|----------|
| 实例故障隔离 | 硬件故障（NPU/网络）+ 软件故障（节点重启）感知与隔离 | `FaultManager` + `ResourceMonitor` |
| 自动重拉起注册 | Pod 重启后 NodeManager 自动重新注册，Controller 组装实例并拉起引擎 | `InstanceAssembler` + `InstanceManager` |
| 缩P保D（Scale P2D） | Decode 实例故障时，释放 Prefill 节点以恢复 Decode | `ScaleP2DStrategy` |
| token级重推 | L2 级别网络故障检测与token级重推恢复 | `TokenReinferenceStrategy` |

**逐行解读：**
- **实例故障隔离**：覆盖范围最广（硬件 NPU/网络 + 软件节点重启），由 `FaultManager` 决策与 `ResourceMonitor` 感知协同，是其他三项能力的基础。
- **自动重拉起注册**：解决故障隔离后的实例"重建"问题——一旦 Pod 被 K8s 重启（无论是手动还是因 L5/L6 故障触发），通过 NodeManager → Controller → InstanceAssembler → InstanceManager 的链路自动恢复服务，无人工介入。
- **缩P保D（Scale P2D）**：针对 PD 分离部署的资源回收策略，本质是**牺牲 Prefill 能力保 Decode 能力**——通过释放 Prefill 节点资源换取新 Decode 实例的拉起。
- **token 级重推**：最轻量级的恢复策略，仅对受网络瞬时故障（L2）影响的 token 进行重推理，避免整卡重启/节点隔离带来的巨大开销。

---

### 表 2：故障等级（原文逐字还原）

| 等级 | 枚举 | 原始故障类型 | 含义 |
|------|------|-------------|------|
| 0 | `HEALTHY` | — | 无故障 |
| 1 | `L1` | `NotHandleFault` | 无需处理 |
| 2 | `L2` | `RestartRequest` | 可自愈（触发token级重推） |
| 3 | `L3` | `RestartBusiness` | 无法自动处理 |
| 4 | `L4` | `FreeRestartNPU` | 需隔离并触发恢复策略（缩P保D） |
| 5 | `L5` | `RestartNPU` | 需 NPU 重启 |
| 6 | `L6` | `SeparateNPU` / `PreSeparateNPU` | 需 NPU 分离 / 节点重启 |

**逐行解读：**
- **L0 HEALTHY**：终态，所有故障清除后的复位状态。
- **L1 `NotHandleFault`**：记录但不触发任何恢复动作，仅用于观测与日志。
- **L2 `RestartRequest`**：**关键分界线**——既可能触发 `TokenReinferenceStrategy`（白名单故障码），也是 `separate_instance()` 与 `recover_instance()` 的决策阈值（≤ L2 可恢复）。
- **L3 `RestartBusiness`**：业务层面无法自动处理的故障，需人工介入；当前框架未给出自动化恢复路径。
- **L4 `FreeRestartNPU`**：在 PD 分离部署下可触发 `ScaleP2DStrategy`，是非 PD 场景下"需隔离 + 触发恢复策略"的标准等级。
- **L5 `RestartNPU`**：需 NPU 设备级重启，**策略上委托 L4 逻辑**（即走相同的缩P保D/隔离流程）。
- **L6 `SeparateNPU` / `PreSeparateNPU`**：NPU 分离或节点重启级别，对应 `NODE_REBOOT`（fault_code `0x0000001`），**同样委托 L4 策略逻辑**。

---

### 表 3：策略路由映射（原文伪代码逐字还原）

```python
# L4 → ScaleP2DStrategy（仅 decode 角色，非 decode 返回 None）
# L5 → 委托 L4
# L6 → 委托 L4
```

**逐行解读：**
- **L4 → ScaleP2DStrategy**：仅当故障角色为 decode 时返回策略实例，其他角色返回 `None`（即不触发任何自动化策略，仅做隔离）。
- **L5 → 委托 L4**：复用 L4 的 ScaleP2D 逻辑，避免策略代码重复。
- **L6 → 委托 L4**：同上，覆盖节点重启/分离场景。

---

## 【公式解读】

**原文无公式。**

文档中未出现任何 LaTeX 数学公式或伪代码形式的状态转移方程；所有逻辑均通过文字、流程图（`text` 代码块）与伪代码片段描述。

---

## 【关联】

### 与文中其他模块/特性的关系

1. **PD 分离（[../pd_disaggregation.md](../pd_disaggregation.md)）**：
   - 缩P保D 策略的**部署前提**——必须在 PD 分离模式下才有效（`X 个 Prefill 实例 + Y 个 Decode 实例`）。
   - 缩P保D 触发后，Coordinator 通过 `readiness == ONLY_PREFILL` 检测并自动将 `deploy_mode` 回退为 `SINGLE_NODE`，**业务对此无感知**（仅延迟增加）。
   - 新 Decode 实例心跳就绪后，Coordinator 恢复 PD 分离路由（详见原文「关键设计点—模式恢复」）。

2. **FaultManager 详解（[fault_manager.md](fault_manager.md)）**：
   - 本文是 FaultManager 的**功能面总览**，fault_manager.md 应承载其**实现细节**（单例模式、`_refresh_instance_fault_level()` 内部逻辑、策略中心路由算法、`forced_separated_instances` 集合管理等）。
   - 三个核心策略类（`ScaleP2DStrategy`、`TokenReinferenceStrategy` 及隐含的 L1/L3 兜底策略）均注册于 FaultManager 持有的策略中心。

3. **PD 分离（[../pd_disaggregation.md](../pd_disaggregation.md)）— 重复引用**：
   - 与第 1 项同链接，文档末尾仍保留一次引用，说明该链接在缩P保D章节中是**强依赖锚点**。

### 上下游链路

```
[K8s Pod 重启 / 硬件故障 / 网络抖动]
        ↓
ResourceMonitor (ConfigMap + Node Watch)        ← 感知层
        ↓
FaultManager (故障等级判定 + 策略路由)           ← 决策层
        ↓
InstanceManager.separate_instance() / recover_instance()   ← 隔离/恢复层
        ↓
InstanceAssembler (Pod 重新注册 → 实例组装 → StartCmd 下发)  ← 重建层
        ↓
NodeManager → Daemon.pull_engine() → ACTIVE     ← 执行层
```

横向策略维度：FaultManager 还路由至 `ScaleP2DStrategy`（PD 场景的资源回收）与 `TokenReinferenceStrategy`（L2 网络故障的轻量恢复）两个领域特定策略。

---

## 【使用方法】

**原文未涉及。**

本文档为特性说明文档，**未给出任何配置项、启用命令、API 调用示例或 YAML 部署清单**。具体的启用/配置方式（如是否需要开启 `TokenReinferenceStrategy` 白名单、如何调优 `is_endpoints_enough()` 的并行度阈值、`ScaleP2DStrategy` 的节点选择策略参数等）需参考各策略对应源码文件：

- `motor/controller/fault_tolerance/fault_types.py`（故障等级枚举定义）
- `motor/controller/fault_tolerance/strategy/strategy.py`（策略路由中心）
- `motor/controller/fault_tolerance/strategy/scale_p2d.py`（ScaleP2D 实现）
- `motor/controller/fault_tolerance/strategy/token_reinference.py`（TokenReinference 实现）
- `motor/controller/core/instance_assembler.py`（实例组装逻辑）
- `motor/node_manager/core/register_manager.py`（NodeManager 注册逻辑）
