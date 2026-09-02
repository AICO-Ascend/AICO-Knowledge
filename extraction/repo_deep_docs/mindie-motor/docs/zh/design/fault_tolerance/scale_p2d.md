# ScaleP2D 故障恢复特性

> 仓 `mindie-motor` · 路径 `docs/zh/design/fault_tolerance/scale_p2d.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/design/fault_tolerance/scale_p2d.md

# ScaleP2D 故障恢复特性 — 一体化深度解读

---

## 【定位】

本文档描述 MindIE Motor 在 **PD 分离（Prefill / Decode 解耦）** 推理集群场景下,当 **Decode 实例遭遇 L4–L6 级硬件故障** 时,通过 **主动停掉部分 Prefill 实例** 来释放算力与节点资源、为故障 D 实例恢复或替换腾出容量的一种 **故障自愈（Scale Prefill to Decode, ScaleP2D）** 策略的设计与实现。

---

## 【技术要点】

1. **故障级别触发与策略委托**:ScaleP2D 由 `FaultManager` 在 L4/L5/L6 故障级别下触发(由 `strategy.py` 中的 `level4_strategy` / `level5_strategy` / `level6_strategy` 工厂函数返回策略类);`level5` 与 `level6` 当前直接 **委托** `level4_strategy`,行为一致。

2. **策略工厂条件返回**:仅当配置项 `enable_scale_p2d == true` 且 `get_instance(instance_id).role == "decode"` 时,工厂才返回 `ScaleP2DStrategy` 类(注意是 **类而非实例**),其余情况返回 `None`,由业务方不能直接 `new`。

3. **四步恢复流水线**:`_execute_recovery_flow()` 顺序编排:
   - Step 1 `_get_d_instance()`:加载 D 实例并计算 `num_required_node`;
   - Step 2 `_check_d_instance_status()`:D 状态门禁(确认已隔离/非活跃才放行);
   - Step 3 `_select_p_instances_to_kill()`:容量校验 + 调用可插拔的 `_select_instances_algorithm()`;
   - Step 4 `_kill_and_release_p_instances()`:逐节点调用 `NodeManagerApiClient.stop`。

4. **关键计时与状态参数**:`CHECK_D_INSTANCE_STATUS_INTERVAL = 3`(秒,轮询间隔)、`CHECK_D_INSTANCE_STATUS_TIMEOUT = 30`(秒,轮询超时);状态机枚举为 `INIT / CHECKING / SELECTING / KILLING / SUCCESS / FAILED`。

5. **线程与并发模型**:单次 `execute()` 在 `ThreadPoolExecutor` 独立线程中运行;`RecoveryContext` 仅在策略线程内读写;`StrategyBase._lock` 保护 `_is_finished`;`stop()` 通过 `threading.Event` 通知 `_check_d_instance_status()` 退出轮询;`FaultManager` 在 `InstanceMetadata.lock` 内更新 `strategy` 引用,与策略线程解耦。

6. **解耦依赖避免循环引用**:`FaultManager` 在 `_get_faulty_node_count()` 内 **局部导入**(局部 import),避免与 `scale_p2d` 模块级产生循环引用。

---

## 【关键机制与数据】

### 1. 工作原理 — 四步流水线

ScaleP2D 的核心思想是 **"安全抢占 + 容量可计算"**:先把已故障的 D 实例 **隔离且确认非活跃**(避免在业务流量未切断时误杀 P),然后基于 D 侧 L3+ 故障节点数推算需要腾出多少节点(`num_required_node`),再与 P 池可用容量比对,选出若干 P 实例 stop 掉。

**安全门禁(Step 2)**:`_check_d_instance_status()` 轮询 D 实例的 `InsStatus`,等待其进入非活跃状态后放行;轮询使用 `CHECK_D_INSTANCE_STATUS_INTERVAL = 3s` 间隔、`CHECK_D_INSTANCE_STATUS_TIMEOUT = 30s` 超时,期间 `stop()` 通过 `threading.Event` 可随时打断。

**容量计算(Step 1 子逻辑)**:`_get_faulty_node_count(d_instance)` 统计 D 实例上 L3+ 故障节点 + 元数据缺失节点数;通过 `_lookup_node_metadata(fm, instance_id, node_mgr)` 先尝试 `pod_ip` 匹配,失败时再用 K8s 反查 `node_name`(`FaultManager._lookup`);`num_required_node` 即为该值。

**P 实例选择(Step 3)**:`_select_instances_algorithm(available)` 是 **可插拔** 的策略点(原文档明示"便于替换为代价模型"),目前按容量匹配从候选 P 实例中筛选 `selected_p_instances`;`num_node_per_instance_P` 取首个 P 实例的节点数。

**执行释放(Step 4)**:对每个待停止 P 实例,逐节点调用 `NodeManagerApiClient.stop(node_mgr)`;成功与否影响最终 `RecoveryState`。

### 2. 数据流(原文时序要点)

```
FaultManager._refresh_instance_fault_level()   → 检测 L4+
FaultManager._process_instance_strategy(ins_id)
level4_strategy()                              → 返回 ScaleP2DStrategy 类
FaultManager → ThreadPoolExecutor.submit(execute, ins_id)
FaultManager: ins_metadata.strategy = instance  (在 InstanceMetadata.lock 内)
Pool 线程:
  SP.execute(ins_id):
    IM.get_instance(ins_id)                    → 校验可解析
    IM.get_instance(d_id) + get_instances_by_role(P)
    FM.nodes (局部 import FaultManager)        → 统计 faulty 节点
    IM 轮询 D status (event 可打断)
    NM.stop(node_mgr) × N                      → 释放 P 节点
    self._is_finished = True
FaultManager.is_finished()                     → 重置 HEALTHY / 清空 strategy
```

### 3. 性能/规模数据

原文未给出量化性能指标或基准测试数字;仅给出两个与时间相关的硬编码常量:`CHECK_D_INSTANCE_STATUS_INTERVAL = 3` 秒、`CHECK_D_INSTANCE_STATUS_TIMEOUT = 30` 秒。

---

## 【表格解读】

### 表 1:概述信息表(原文)

| 项 | 说明 |
|----|------|
| 实现文件 | `motor/controller/fault_tolerance/strategy/scale_p2d.py` |
| 调度方 | `FaultManager` 策略中心(线程池异步执行) |
| 策略注册 | `strategy.py` 中 `level4_strategy` / L5 / L6 |

**解读**:这张表点明了 ScaleP2D 的代码落点、调度入口与触发级别。`FaultManager` 作为策略中心,以 **异步** 方式(线程池)执行 `execute`,注册点在 `strategy.py` 的三个故障级别工厂函数中——L5/L6 当前委托 L4,意味着 L4–L6 共用同一条恢复路径。

---

### 表 2:分层与职责表(原文)

| 层次 | 组件 | 职责 |
|------|------|------|
| 调度层 | `FaultManager` | 故障定级、策略选型、线程池提交 `execute`、生命周期与 ETCD 持久化 |
| 策略层 | `ScaleP2DStrategy` | 恢复流水线、上下文维护、日志与错误语义 |
| 数据层 | `InstanceManager` | D/P 实例查询、实例状态(`InsStatus`) |
| 故障数据层 | `FaultManager.nodes` | 节点级 ConfigMap 故障(由 ResourceMonitor 同步) |
| 执行层 | `NodeManagerApiClient` | 对 P 节点下发 HTTP `stop` |

**解读**:五层划分清晰体现了"**谁决策—谁编排—谁查数据—谁执行**"的链式分工。`InstanceManager` 负责运行时实例真相,`FaultManager.nodes` 负责节点级故障真相(由 ResourceMonitor 从 ConfigMap 同步而来);策略层不直接执行停机,而是把动作下发给 `NodeManagerApiClient`,保持策略与执行解耦。

---

### 表 3:`level4_strategy` 参数表(原文)

| 参数 | 类型 | 说明 |
|------|------|------|
| `fault_code` | `int` | 当前实例最高故障码(ScaleP2D 内未使用,预留) |
| `instance_id` | `int` | 故障实例 ID |
| `config` | `ControllerConfig` | Controller 配置 |

**返回值条件(原文)**:
- `ScaleP2DStrategy`:`enable_scale_p2d == true` 且 `get_instance(instance_id).role == "decode"`
- `None`:开关关闭、实例不存在或 role 非 decode

**解读**:工厂函数不接收完整故障上下文——`fault_code` 在 ScaleP2D 内部 **并未使用**(预留扩展);真正的判别仅靠两个条件:**全局开关** `enable_scale_p2d` 和 **实例角色** 必须是 decode。返回的是 **类(类型)** 而非实例,实例化由 `FaultManager` 线程池统一完成。

---

### 表 4:`execute(instance_id)` 公共接口表(原文)

| 项 | 说明 |
|----|------|
| **作用** | 启动一次完整 ScaleP2D 恢复;结束时置 `_is_finished = True` |
| **参数** | `instance_id`:故障 Decode 实例 ID |
| **前置** | `InstanceManager` 中可解析该实例(否则记录错误并返回,不创建 context) |
| **副作用** | 写入 `self.context`;可能 stop 多个 P 实例的 NodeManager |
| **成功判定** | `_execute_recovery_flow()` 四步均返回 `True` → `RecoveryState.SUCCESS` |
| **失败判定** | 任一步返回 `False` 或顶层异常 → `RecoveryState.FAILED`,`last_error` 记录原因 |

**解读**:`execute` 是策略的"生命周期入口";若前置解析失败,**不创建 context**——这是一种 **fail-fast + 无副作用** 的保护设计。四步全 True 才算 SUCCESS,任一失败都把状态机推到 FAILED 并保留 `last_error` 供上层诊断。

---

### 表 5:`stop()` 公共接口表(原文)

| 项 | 说明 |
|----|------|
| **作用** | 请求策略线程尽快退出(设置 `event`);并标记 `_is_finished = True` |
| **调用方** | `FaultManager` 在策略升级/实例移除时停止旧策略 |
| **影响** | 正在执行的 `_check_d_instance_status()` 轮询会检测 `event` 并返回 `False` |

**解读**:`stop()` 兼具"通知中断"和"终结标记"两重作用;`_is_finished` 在 stop 路径也会被置位,因此即便轮询在等待 D 状态时被打断,`FaultManager` 也能正确进入收尾流程(清 strategy / 重置 HEALTHY)。

---

### 表 6:`is_finished()` 公共接口表(原文)

| 项 | 说明 |
|----|------|
| **作用** | 供 `FaultManager` 判断可否清空 `strategy` 并重置实例故障级别 |
| **线程安全** | 使用 `_lock` 读取 |

**解读**:这是策略与调度层之间的 **握手点**——`FaultManager` 通过轮询 `is_finished()` 决定何时进入收尾动作(清空 `ins_metadata.strategy`、将实例故障级别重置为 HEALTHY);读取走 `_lock`,与执行线程的 `_is_finished = True` 写入形成同步。

---

### 表 7:`RecoveryContext` 数据契约(原文)

| 字段 | 类型 | 写入阶段 | 说明 |
|------|------|----------|------|
| `d_instance_id` | `int` | 构造 | 故障 D 实例 ID |
| `d_instance_job_name` | `str` | 构造 | D 实例 job 名(日志) |
| `d_instance` | `Instance \| None` | `_get_d_instance` | D 实例对象引用 |
| `num_node_per_instance_D` | `int` | `_get_d_instance` | D 单实例节点数 |
| `num_node_per_instance_P` | `int` | `_select_p_instances_to_kill` | P 单实例节点数(取首个 P) |
| `num_required_node` | `int` | `_get_d_instance` | 需由 P 侧腾出的节点数 |
| `selected_p_instances` | `list[Instance]` | `_select_p_instances_to_kill` | 待停止的 P 实例列表 |
| `current_state` | `RecoveryState` | 各步骤 | 流程状态 |
| `last_error` | `str \| None` | 失败路径 | 人类可读错误摘要 |
| `start_time` | `float` | 构造 | 用于统计 `elapsed_s` |

**解读**:这是一份"流水线上下文快照",可以清晰看到每一步产生哪些字段:Step 1 同时填好 D 实例引用与 `num_required_node`(容量推算);Step 3 才产生 P 侧两个数字;`start_time` 在构造时写入,结合 `last_error` 便于事后回溯"恢复跑了多久、为什么失败"。

---

### 表 8:内部方法表(原文)

| 方法 | 入参 | 返回值 | 说明 |
|------|------|--------|------|
| `_execute_recovery_flow()` | — | `bool` | 顺序调用 Step 1–4 |
| `_get_d_instance()` | — | `bool` | 加载 D 实例并计算 `num_required_node` |
| `_get_faulty_node_count(d_instance)` | `Instance` | `int` | 统计 L3+ / 缺失元数据节点数 |
| `_lookup_node_metadata(fm, instance_id, node_mgr)` | FM、ID、`NodeManagerInfo` | `NodeMetadata \| None` | pod_ip 匹配或 K8s 反查 node_name |
| `_check_d_instance_status()` | — | `bool` | D 状态门禁与轮询 |
| `_select_p_instances_to_kill()` | — | `bool` | 容量校验 + 调用选择算法 |
| `_select_instances_algorithm(available)` | `list[Instance]` | `list[Instance]` | **可替换** 的 P 选择实现 |
| `_kill_and_release_p_instances()` | — | `bool` | 逐节点 `NodeManagerApiClient.stop` |
| `_node_has_high_level_fault(node_metadata)` | `NodeMetadata` | `bool` | 静态方法,是否存在 L3+ 故障 |

**解读**:注意 `_select_instances_algorithm` 被原文明确标注 **可替换**——这是 ScaleP2D 的扩展点,未来可以替换为代价模型/启发式算法。`_get_faulty_node_count` 与 `_node_has_high_level_fault` 共同支撑"只统计高等级故障节点"这一容量口径(L3+ 作为需要腾位的门槛)。

---

### 表 9:`InstanceManager` 外部依赖表(原文,被截断)

原文提供了该表的开头:

| 方法 | ScaleP2D 用途 |
|------|----------------|
| `get_instance(ins_id: int) -> Instance \| None` | 加载 D 实例、状态轮询 |
| `get_instances_by_role( | (后续内容在原文被截断,未提供完整定义) |

**解读**:仅能确认 `InstanceManager` 提供 **按 ID 取实例** 与 **按角色批量取实例** 两个能力;后者的完整签名和用途原文未给出(文档在表格中断尾)。

---

## 【公式解读】

原文无数学公式。设计意图中出现的"容量推算"逻辑为伪代码式描述:

> D 侧 L3+ 故障节点数  →  `num_required_node`
> `num_required_node` 与 P 池可用容量比对  →  选出若干 P 实例 stop

这一推算在文档中以方法名 `_get_faulty_node_count(d_instance) -> int` 表达,并未给出具体的算式或常量系数;`num_node_per_instance_P` 取首个 P 实例的节点数。**严格按原文,无 LaTeX 公式可还原,此处仅复述原文语义**。

---

## 【关联】

文档通过以下方式与其他模块/特性建立联系:

- **用户侧使用文档**:`使用与配置说明见 [ScaleP2D 用户指南](../../user_guide/features/fault_tolerance/scale_p2d.md)` —— 上游配套的用户指南,描述开关、配置与操作步骤。
- **调度方文档**:`fault_manager.md` —— `FaultManager` 作为 ScaleP2D 的调度层,负责故障定级、策略选型、线程池提交、生命周期与 ETCD 持久化;ScaleP2D 是其下属的众多故障级别策略之一(`level4_strategy` / L5 / L6 工厂的返回目标)。
- **上下游模块**(文档内部交叉引用,无独立链接):
  - 上游数据源:`ResourceMonitor`(同步节点级 ConfigMap 故障到 `FaultManager.nodes`)、`InstanceManager`(D/P 实例与 `InsStatus` 真相);
  - 下游执行器:`NodeManagerApiClient.stop(node_mgr)` —— 对 P 节点下发 HTTP stop;
  - 旁路依赖:K8s Client(在 `_lookup_node_metadata` 走 pod_ip 失败时反查 `node_name`)。
- **设计上的扩展点**:`_select_instances_algorithm()` 被文档明确标注为 **可插拔**,未来可替换为代价模型——这意味着该策略与未来的"P 选择优化算法"特性存在天然接续关系。

---

## 【使用方法】

**原文未在本 design 文档中给出具体启用步骤**;文档在概述部分仅以单行说明指向用户指南:

> 使用与配置说明见 [ScaleP2D 用户指南](../../user_guide/features/fault_tolerance/scale_p2d.md)。

原文中能确认的 **最小启用条件**(从策略工厂推导):
- 全局开关:`enable_scale_p2d == true`
- 实例角色:`get_instance(instance_id).role == "decode"`
- 故障级别:L4 / L5 / L6(由 `strategy.py` 中 `level4_strategy` / `level5_strategy` / `level6_strategy` 触发,后两级委托 `level4_strategy`)
- 实例可解析:`InstanceManager.get_instance(ins_id)` 必须能返回实例,否则 `execute` 直接记录错误并返回

详细的配置文件位置、参数示例、命令行启用方式,请参照内部链接指向的用户指南 `../../user_guide/features/fault_tolerance/scale_p2d.md`。
