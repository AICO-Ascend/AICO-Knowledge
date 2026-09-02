# 主备倒换特性设计文档

> 仓 `mindie-motor` · 路径 `docs/zh/design/fault_tolerance/standby.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/design/fault_tolerance/standby.md

# 《主备倒换特性设计文档》深度解读

## 【定位】

本文档描述 mindie-motor 中 Controller 与 Coordinator 组件通过 ETCD 分布式锁实现主备自动倒换的高可用能力，解决单实例部署下 Pod 或进程故障导致整个推理服务不可用的问题。

---

## 【技术要点】

1. **ETCD 分布式锁统一选举框架**：Controller 与 Coordinator 共用 `StandbyManager`（`motor/common/standby/standby_manager.py`），单例模式 + 后台线程，以 `master_standby_check_interval` 为周期轮询——Master 续租、Standby 抢锁，连续失败次数达到 `master_lock_max_failures` 才放弃本轮。

2. **锁键隔离原则**：两个组件的 ETCD 锁键分别自动加上 `/controller/` 与 `/coordinator/` 前缀，**两套选举完全独立、互不干扰**，可分别在不同时间发生倒换。

3. **Controller 单进程流量隔离**：StandbyManager 角色直接决定业务模块启停（Master 启 InstanceManager/EventPusher/FaultManager；Standby 仅保留 ControllerAPI），通过 `/readiness`（直接查 `is_master()`）+ HTTP 中间件**双重**拒绝 standby Pod 接收业务流量。

4. **Coordinator 跨进程角色传递**：锁持有者（Daemon 线程）与探针响应者（Mgmt 进程）解耦，通过 `RoleShmHolder` 管理的共享内存作为桥梁——byte0 存角色标识，byte1-8 存心跳时间戳。

5. **Coordinator `/readiness` 四维判断**：综合 Daemon 存活（孤儿检测）、心跳新鲜度、角色状态、所需实例就绪情况，任一不满足即返回 503。

6. **`/liveness` 与角色解耦**：standby 状态下 Coordinator 的 liveness 只要 Daemon 活着即返回 200，**不会**触发 Pod 不必要重启；只有 Mgmt 父进程不再是 Daemon（孤儿）时才返回 503 触发重启。

---

## 【关键机制与数据】

**选举工作原理（原文）**：StandbyManager 主循环以 `master_standby_check_interval` 为周期。当前 Master 调用 `_renew_master_lock()` 续租 ETCD Lease，**续租失败则降级为 Standby 并回调 `on_become_standby()`**；当前 Standby 调用 `_try_become_master()` 抢锁，**成功则升级为 Master 并回调 `on_become_master()`**。线程退出时若持有锁则主动释放（加速切换，不依赖 TTL 超时）。

**角色变更数据流（Controller，原文）**：
```
ETCD 锁状态 → StandbyManager 回调 → on_become_master()/on_become_standby()
→ 启停 InstanceManager/EventPusher/FaultManager 等业务模块
→ ControllerAPI 中间件切换拒绝/放行业务请求
→ /readiness 返回 200/503（直接查 StandbyManager().is_master()）
```

**角色变更数据流（Coordinator，原文）**：
```
ETCD 锁状态（StandbyManager 线程）→ 回调通知 → Daemon 写共享内存 byte0
→ Mgmt 进程 ReadinessProbe 读共享内存 → /readiness 响应 200/503
```
原文明确指出：「**锁持有者（Daemon 内的 StandbyManager 线程）和探针响应者（Mgmt 进程）不在同一个进程中，共享内存是它们之间的桥梁。**」

**告警去重机制（原文）**：升主时从 ETCD 读 `should_report_event` 键判断是否需要上报 `MasterToSlaveEvent`，随后将该键置为 `true`，**确保同一次故障只上报一次**。

**倒换时序（原文六步）**：① 初始选主（Pod B 抢锁成功）→ ② K8s Readiness 探测（Master 返回 200，Standby 返回 503，Kube Proxy 仅路由到 Master）→ ③ Master 故障（HTTP 不可达，K8s 移出 Service Endpoint）→ ④ ETCD Lease TTL 超时释放锁，Standby 抢锁升主 → ⑤ K8s 探测新 Master 就绪，加入 Endpoint，流量切换 → ⑥ 原 Master 重启后以 Standby 身份加入等待。

**原文未给出具体数值**：`master_standby_check_interval`、ETCD Lease TTL、`master_lock_max_failures` 的实际取值文档均未列明，仅作为可配置参数提及。

---

## 【表格解读】

**`/readiness` 多维判断表（逐字还原）**：

| 检查项 | 检测方式 | 不满足时 |
|---|---|---|
| Daemon 是否存活 | 共享内存中检查父进程是否为 Daemon（孤儿检测） | 503 `DAEMON_EXITED` |
| Daemon 心跳是否新鲜 | 共享内存 byte1-8 的时间戳是否在阈值内 | 503 `HEARTBEAT_STALE` |
| 角色是否为 master | 共享内存 byte0 的角色标识 | 503 `NOT_MASTER` |
| 所需实例是否就绪 | `InstanceManager.get_required_instances_status()` | ready 字段为 `false` |

**逐行解读**：

- **第 1 行（Daemon 存活 / 孤儿检测）**：通过检查 Mgmt 进程的父进程 PID 是否仍为 Daemon 来判断 Daemon 是否异常退出——一旦 Daemon 崩溃但 Mgmt 被 init 接管成为孤儿，本项立即失败。这是 Coordinator 特有的检测，因为 Controller 是单进程模型不存在该问题。

- **第 2 行（心跳新鲜度）**：Daemon 的心跳线程定期刷新共享内存 byte1-8 的时间戳；Mgmt 读取后若超过阈值即判定心跳过期。该机制让 Mgmt 能间接感知 Daemon 是否"卡死"（即使进程还在但已停止工作）。

- **第 3 行（角色判定）**：直接读取 byte0 的 master/standby 标识，与 Controller 通过 `StandbyManager().is_master()` 直接查询的机制相比，这里走的是共享内存通道，因为角色判定方（Mgmt）与角色持有方（Daemon）跨进程。

- **第 4 行（实例就绪）**：调用 `InstanceManager.get_required_instances_status()`，原文表述为"ready 字段为 `false`"即不满足——这表明 Coordinator 在角色为 master 的前提下，还需要业务侧的推理实例真正就绪才会接受流量，是比角色判定更高一层的"真业务就绪"语义。

---

## 【公式解读】

**原文无公式**。

（注：原文出现的 `master_standby_check_interval`、`master_lock_max_failures` 属于配置参数名称，并非数学公式；共享内存 byte0/byte1-8 属于内存布局描述而非公式。）

---

## 【关联】

本文档与以下组件/特性形成上下游协作关系（基于原文提及，未引入外部链接）：

- **ETCD 基础设施层**：项目本身已依赖 ETCD 作为服务发现与配置存储，主备选举**复用同一套 ETCD 集群**——这是文档第 4 节明确的设计决策依据（避免引入 K8s Leader Election 这条额外依赖路径）。

- **K8s 原生机制**：Readiness Probe、Liveness Probe、Service Endpoint、Kube Proxy——文档多次强调"双重流量隔离"既依赖 K8s 探测结果移出 Endpoint，也依赖应用层 HTTP 中间件直接拒绝，二者协同而非互斥。

- **Controller 业务模块**：`InstanceManager`、`EventPusher`、`FaultManager` 在 Master 时启动、Standby 时停用——主备倒换直接决定这些模块的进程内生命周期。

- **ControllerAPI**（`controller_api.py`）：作为唯一在 Standby 状态仍持续运行的 Controller 组件，承担 `/readiness`、`/liveness` 探针响应与中间件流量拦截。

- **Coordinator 多进程体系**：`coordinator_daemon.py`（持锁与业务调度）、`management_server.py`（Mgmt，承载探针与 HTTP 入口）、`Infer 进程`（仅 master 时运行）——三进程模型倒逼共享内存机制的引入。

- **共享内存辅助组件**：`RoleShmHolder`（`role_shm_holder.py`，写入角色与心跳）、`probe.py`（Mgmt 内 ReadnessProbe / LivenessProbe 实现）——构成跨进程角色传递的完整链路。

- **`should_report_event` ETCD 键**：与告警事件系统联动，倒换时配合 `MasterToSlaveEvent` 上报，并利用 ETCD 键值做告警去重（"同一次故障只上报一次"）。

- **`StandbyManager` 单例基础库**（`motor/common/standby/standby_manager.py`）：被 Controller 与 Coordinator 共用，是该特性的核心复用点；其回调钩子 `on_become_master()` / `on_become_standby()` 是两个组件差异化的扩展点。

---

## 【使用方法】

**原文未涉及**具体的启用配置项、YAML 片段、命令行开关或 Helm values。

文档仅以设计视角描述了机制与流程，提到以下**可配置项名称**（但未给出取值范围、默认值或启用开关）：
- `master_standby_check_interval`（主循环检查周期）
- `master_lock_max_failures`（连续抢锁失败放弃阈值）
- ETCD Lease TTL（决定锁自动释放时间窗口，文档未列具体值）

如需在生产环境中启用或调优主备倒换行为，需结合 `motor/common/standby/standby_manager.py` 的源码及部署侧 ETCD 配置进一步查阅，原文未提供操作指引。
