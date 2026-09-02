# ScaleP2D 故障恢复

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/features/fault_tolerance/scale_p2d.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/features/fault_tolerance/scale_p2d.md

# ScaleP2D 故障恢复 —— 一体化深度解读

---

## 【定位】

本文档描述 MindIE Motor 在 **PD 分离（Prefill / Decode 解耦）** 部署形态下,当 **Decode 实例遭遇 L4–L6 级硬件故障** 时,通过主动缩减 Prefill 实例数量来腾出算力与节点资源、从而支撑 D 实例恢复或替换的 **故障自愈策略（ScaleP2D）** 的触发条件、恢复流程、配置方法、日志排查与约束限制。

---

## 【技术要点】

1. **PD 分离场景专属的故障自愈策略**: ScaleP2D 仅在 Prefill / Decode 解耦部署形态下生效,目标对象严格限定为 `role == "decode"` 的 D 实例,故障级别限定为 L4 / L5 / L6,Prefill 实例故障不在策略范围内。
2. **MindCluster 版本依赖**: 该特性依赖 MindCluster 的"优先级调度"与"实例强制删除"能力,**MindCluster 版本必须 ≥ 26.1.0** 才支持。
3. **核心策略动作**: 当 D 实例因硬件故障进入 `inactive` 等可抢占态后,系统在 `scale_p2d_d_instance_reinit_wait_timeout`(默认 **60 秒**) 内轮询等待 D 自恢复,超时后主动从 P 实例中挑选若干个,经由 NodeManager 下发 `stop`,由 CRD Controller 强制回收 Pod 并释放节点。
4. **四步恢复流程**: ①加载 D 实例并统计 L3+ 故障节点数、计算 `num_required_node` → ②等待 D 自恢复 → ③按可用 P 容量选取待停止 P 实例 → ④对选中 P 实例全部 NodeManager 下发 `stop`。
5. **双层配置要求**: 需同时启用 Controller 侧 JSON(`enable_scale_p2d=true` 等)与 InferServiceSet CRD 侧 YAML(`schedulingStrategy.type=Priority`、各 role 设 `priority`、`fault-scheduling=external-force`),二者缺一不可。
6. **P 实例选择策略**: 当前为"按实例 ID 排序"的占位实现,文档明确说明后续可能接入负载/优先级模型,意味着线上行为可能演进。

---

## 【关键机制与数据】

### 触发判定逻辑

FaultManager 异步触发 ScaleP2D 必须**同时**满足三项条件:
- `enable_scale_p2d == true`
- 故障实例 `role == "decode"`
- 实例故障级别为 L4 / L5 / L6

### 节点数计算公式(原文)

可用 P 容量节点数计算如下:

```
可用节点 = nodes_per_P × (P_count - 1)
```

- `nodes_per_P`: 每个 P 实例占用的节点数(原文约束:"默认各 P 实例节点数相同")
- `P_count`: 当前 P 实例总数
- 公式含义: 从 P 实例中保留 1 个、停掉其余所有,得到可用于腾挪的最大节点数(即"可用 P 容量")。原文同时要求"需保留至少 1 个 P 实例",故减 1 是必须的最小保留量。

### 关键参数(原文)

- `scale_p2d_d_instance_reinit_wait_timeout`: 默认 **60 秒**,ScaleP2D 抢占前等待 D 实例自恢复的最长时间。
- `strategy_center_check_interval`: 默认 **1 秒**,策略中心轮询间隔。
- `priority` 字段取值范围: **1–32**(原文),数值越小优先级越高。

### 数据流概览

1. FaultManager 监测到 D 实例达到 L4–L6 → 异步触发 ScaleP2D。
2. ScaleP2D 加载 D 实例上 L3+ 故障节点清单(缺失元数据视同故障)。
3. 进入等待窗口(`scale_p2d_d_instance_reinit_wait_timeout`),轮询 D 实例状态:
   - 若回到 `initial` / `active` → 取消 ScaleP2D。
   - 仍处于 `inactive` 等可抢占态 → 进入 P 选择阶段。
4. 在可用 P 容量(`nodes_per_P × (P_count - 1)`)内选取待停止 P 实例。
5. 对所选 P 实例全部 NodeManager 下发 `stop`。
6. CRD Controller 强制回收 Pod,释放节点供 D 实例恢复/替换。

### 性能数据

**原文未涉及**性能数据(无恢复时延、节点回收耗时等量化指标)。

---

## 【表格解读】

### 表 1:适用场景(原文逐字还原)

| 维度 | 说明 |
|------|------|
| 部署形态 | PD 分离:P 实例负责 Prefill,D 实例负责 Decode |
| 故障对象 | **Decode 实例**(`role == decode`) |
| 故障级别 | 实例级故障达到 **L4、L5 或 L6** |
| 节点故障 | D 实例上存在 **L3 及以上** 设备级硬件故障的节点,或节点元数据缺失 |
| 前置隔离 | D 实例已脱离 `initial` / `active` 等业务活跃态(由 FaultManager 触发隔离后进入 `inactive` 等状态) |

**逐行解读**:
- **部署形态**: 明确该策略仅适用 PD 解耦部署,与混合部署不兼容。
- **故障对象**: 策略的方向性是"以 P 换 D",因此目标对象限定 D 实例;Prefill 实例故障需走其他策略。
- **故障级别**: L4–L6 是严重级别,而 L3 及以下由其他隔离/恢复逻辑处理。
- **节点故障**: 引入"L3+ 节点级"作为 D 实例判定输入,这是因为 D 实例级别的 L4+ 故障可能由其下属节点的 L3+ 设备故障累积导致;元数据缺失视同故障,体现"宁严勿漏"的容错取向。
- **前置隔离**: ScaleP2D 是"补救动作",而非"隔离动作",因此必须先经 FaultManager 隔离,本特性才能生效。

---

### 表 2:恢复流程(原文逐字还原)

| 步骤 | 说明 |
|------|------|
| 1. 加载 D 实例 | 统计 D 实例上 L3+ 故障节点数(缺失元数据视同故障),计算需腾出的节点数 `num_required_node` |
| 2. 等待 D 自恢复 | 在 `scale_p2d_d_instance_reinit_wait_timeout` 内轮询 D 实例状态;若恢复为 `initial` / `active` 则取消 ScaleP2D;超时后若仍为 `inactive` 等可抢占状态则继续 |
| 3. 选择 P 实例 | 在可用 P 容量内选取待停止的 P 实例(可用节点 = `nodes_per_P × (P_count - 1)`) |
| 4. 停止 P 实例 | 对选中 P 实例的所有 NodeManager 下发 `stop`,由 CRD 强制回收 Pod 并释放节点 |

**逐行解读**:
- **步骤 1**: 计算 `num_required_node` 是为后续判断"是否真要触发 P 缩减"提供依据(若 D 自身能容纳,可能跳过),缺失元数据等同故障是为了应对 ResourceMonitor 同步滞后。
- **步骤 2**: 设置 `scale_p2d_d_instance_reinit_wait_timeout`(默认 60 秒)是为了让 D 实例自身具备一定的"自我修复机会",避免不必要的 P 缩减;超时后才进入强干预阶段。
- **步骤 3**: 用 `nodes_per_P × (P_count - 1)` 表达"留 1 砍其余",体现"保留至少 1 个 P 实例"的硬约束;但是否真正砍够 `num_required_node` 个,文档未给出选择算法细节,需结合设计文档。
- **步骤 4**: 下发 `stop` 到 NodeManager,实际 Pod 删除与节点释放依赖 CRD Controller 的强制回收能力(对应 `fault-scheduling=external-force` 标签),Controller 自身并不直接删 Pod。

---

### 表 3:Controller 配置(原文逐字还原)

| 配置项 | 类型 | 说明 |
|--------|------|------|
| `enable_fault_tolerance` | bool | 须 `true` 才启动 FaultManager |
| `enable_scale_p2d` | bool | 是否启用 ScaleP2D(用户侧默认 `false`) |
| `scale_p2d_d_instance_reinit_wait_timeout` | int | ScaleP2D 执行抢占前,等待 D 实例自恢复(重初始化)的最长时间(秒)。等待期间若 D 实例恢复为 `initial` / `active`,则不再执行 ScaleP2D;超时后若 D 实例仍处于 `inactive` 等可抢占状态,则继续后续 P 实例选择流程。默认:`60` |
| `strategy_center_check_interval` | int | 策略中心轮询间隔(秒) |

**逐行解读**:
- **`enable_fault_tolerance`**: 是 FaultManager 总开关,ScaleP2D 必须在其启用前提下才会被加载。
- **`enable_scale_p2d`**: 用户侧默认 `false`,即 ScaleP2D 是 opt-in 而非 opt-out,避免默认开启带来误抢占风险。
- **`scale_p2d_d_instance_reinit_wait_timeout`**: 唯一可直接调优的抢占窗口参数,默认 60 秒;调小意味着更快进入 P 缩减(可能误伤还在自愈的 D 实例),调大意味着更宽容的自愈窗口但占用更久的故障资源。
- **`strategy_center_check_interval`**: 控制器侧轮询节拍,影响 ScaleP2D 对 D 状态变化的响应灵敏度。

---

### 表 4:`priority` 字段(原文逐字还原)

| 字段 | 类型 | 取值范围 | 说明 |
|------|------|----------|------|
| `priority` | int | 1–32 | 数值越小,调度优先级越高 |

**逐行解读**:
- `priority` 是角色级字段,作用于 `prefill`、`decode` role 的 `spec` 同级,**仅当开启 `schedulingStrategy.type=Priority` 时生效**。
- 原文明确建议:**prefill 的 `priority` 数值大于 decode**,即 prefill 优先级最低,更易被抢占,这样在资源紧张或主动缩减时,prefill 实例会被优先让位,与 ScaleP2D"释放 P 算力"的策略方向一致。

---

### 表 5:`fault-scheduling` 标签(原文逐字还原)

| 标签 | 修改前 | 修改后 | 说明 |
|------|--------|--------|------|
| `fault-scheduling` | `grace` | `external-force` | 开启实例级重调度;强制删除原实例并级联删除 Pod,供 ScaleP2D 实现 P 实例的强制释放 |

**逐行解读**:
- `grace` 是默认行为(优雅退出),不强制级联删除 Pod。
- `external-force` 表示由外部(本场景即 ScaleP2D)触发强制删除,使 CRD Controller 必须级联回收 Pod。
- 这是 ScaleP2D "P 实例停止"步骤真正落地的前置条件;不开启此标签,NodeManager 的 `stop` 将无法触发 Pod 回收,资源释放会卡住。

---

### 表 6:日志与排查(原文逐字还原)

| 关键词 | 可能原因 | 建议 |
|--------|----------|------|
| `instance_not_in_instance_manager` | D 实例不存在 | 检查 ETCD / InstanceManager 同步 |
| `ScaleP2D not needed` + `initial/active` | D 未隔离 | 检查 `separate_instance` 流程 |
| `did not become INACTIVE` | 状态检查超时 | 检查隔离与状态上报延迟 |
| `Node metadata missing` | 节点未同步 | 检查 ResourceMonitor / pod_ip 映射 |
| `no_p_instances` | 无 P 实例 | 检查部署与注册 |
| `Insufficient Prefill nodes` | P 容量不足 | 扩容 P 或降低故障节点数 |
| `Failed to stop P instance node` | NodeManager 不可达 | 检查进程、网络、Pod 生命周期 |
| `algorithm_not_implemented` | 选择算法未实现 | 联系开发确认 P 实例选择策略 |

**逐行解读**:
- 该表以日志前缀 `[motor/controller/fault_tolerance/scale_p2d]` 为锚点。
- 前四条(`instance_not_in_instance_manager`、`ScaleP2D not needed` + `initial/active`、`did not become INACTIVE`、`Node metadata missing`)均属 **触发阶段** 异常,反映 ScaleP2D 在加载 D 实例与等待其进入可抢占态时遇到数据缺失或状态不符。
- 后四条(`no_p_instances`、`Insufficient Prefill nodes`、`Failed to stop P instance node`、`algorithm_not_implemented`)属 **执行阶段** 异常,反映 P 实例选取与停止过程中资源、连通性、策略实现层面的问题。

---

## 【公式解读】

原文出现的伪代码公式:

```
可用节点 = nodes_per_P × (P_count - 1)
```

**符号含义**:
- **`可用节点`**: 在 ScaleP2D 阶段 3 "选择 P 实例" 中,可用于腾挪的 P 实例侧节点总容量上界。
- **`nodes_per_P`**: 单个 P 实例占用的节点数;原文约束"默认各 P 实例节点数相同",因此该值即"任一 P 实例的节点数"。
- **`×`**: 乘法算子,代表总节点数等于"单实例节点数 × 可削减实例数"。
- **`P_count`**: 当前 P 实例总数(原文未限定最小值,但限制 3 已说明"需保留至少 1 个 P 实例")。
- **`- 1`**: 减去 1 个 P 实例作为必须保留的最小值,体现硬约束;若 `P_count = 1` 则可用节点为 0,无法触发 P 缩减。

原文无 LaTeX 公式或其他数学表达式。

---

## 【关联】

- **设计文档** [`../../../design/fault_tolerance/scale_p2d.md`](../../../design/fault_tolerance/scale_p2d.md): 本文多处引用其"更完整的设计说明",包括 P 实例选择算法、`num_required_node` 计算细节、以及占位实现向负载/优先级模型演进的路径。
- **配置参考** [`../../configuration/config_reference.md#motor_controller_config`](../../configuration/config_reference.md#motor_controller_config): ScaleP2D 的 Controller 侧 JSON 配置(尤其是 `fault_tolerance_config` 嵌套结构)的官方权威定义与字段全集。
- **FaultManager**: 触发隔离(`separate_instance` 流程)将 D 实例置为 `inactive` 状态,本文多处将 "D 实例是否已隔离" 作为前置条件与触发依据(如 `did not become INACTIVE`、`ScaleP2D not needed` 等日志)。
- **InstanceManager / ETCD**: 提供实例与节点元数据的同步通道(对应日志 `instance_not_in_instance_manager`、`Node metadata missing`)。
- **ResourceMonitor**: 提供节点元数据与 `pod_ip` 映射,故障节点识别依赖其同步结果。
- **NodeManager**: ScaleP2D 阶段 4 的 `stop` 指令下发目标,负责 P 实例停止的落地。
- **InferServiceSet CRD / CRD Controller**: 提供 `schedulingStrategy=Priority` 的优先级调度与 `fault-scheduling=external-force` 的强制 Pod 回收能力,是 ScaleP2D 真正能够"释放 P 节点"的关键依赖。
- **MindCluster**: 版本 ≥ 26.1.0 提供了 ScaleP2D 所依赖的"优先级调度 + 实例强制删除"底层能力。
- **PD 分离部署形态**: 上游约束,ScaleP2D 不适用于 Prefill 实例故障或非 PD 分离场景。

---

## 【使用方法】

### 1. Controller 侧 JSON 配置

在 Controller 配置中开启 FaultManager 总开关与 ScaleP2D 子开关,并显式设定等待窗口(可选):

```json
{
  "fault_tolerance_config": {
    "enable_fault_tolerance": true,
    "enable_scale_p2d": true,
    "scale_p2d_d_instance_reinit_wait_timeout": 60,
    "strategy_center_check_interval": 1
  }
}
```

关键字段(原文):
- `enable_fault_tolerance`: 必须为 `true`(总开关)。
- `enable_scale_p2d`: 必须为 `true`,用户侧默认 `false`。
- `scale_p2d_d_instance_reinit_wait_timeout`: int,秒,默认 `60`。
- `strategy_center_check_interval`: int,秒,默认 `1`(原文示例值)。

### 2. InferServiceSet YAML 配置(CRD 部署场景)

修改 `examples/deployer/yaml_template/infer_service_template.yaml`(CRD 模式下 deploy 脚本据此生成 `output_yamls/infer_service.yaml`),完成三项修改:

**(a) 开启优先级调度**——在 `spec.template` 下增加:

```yaml
spec:
  template:
    schedulingStrategy:
      type: Priority
    roles:
      # ...
```

**(b) 为 prefill / decode 角色配置 priority**(1–32,数值越小优先级越高):

```yaml
    - name: prefill
      replicas: 4
      priority: 2          # 优先级最低
      # ...

    - name: decode
      replicas: 4
      priority: 1
      # ...
```

**(c) 将 Pod 标签 `fault-scheduling` 改为 `external-force`**(原 `grace`):

```yaml
        template:
          metadata:
            labels:
              fault-scheduling: external-force   # 原为 grace
              fault-retry-times: "10000"
              app: mindie-server
              # ...
```

### 3. 版本前置条件

**MindCluster 版本必须 ≥ 26.1.0**(原文:"需要 MindCluster 版本为 26.1.0 及以上才支持")。

### 4. 启用后的日志排查入口

日志前缀:`[motor/controller/fault_tolerance/scale_p2d]`,结合上文"日志与排查"表中的 8 个关键词进行故障定位(原文已逐条给出可能原因与建议)。
