# Coordinator 自熔断需求设计文档

> 仓 `mindie-motor` · 路径 `docs/zh/design/circuit_breaker_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/design/circuit_breaker_design.md

# Coordinator 自熔断需求设计文档 — 一体化深度解读

## 【定位】

本文档针对 MindIE-Motor 的 Coordinator 在生产环境中依赖 Controller 推送故障事件而存在感知滞后、PD 分离场景下请求直接丢失的问题，定义了一套 **Coordinator 内部自熔断 + PD 分离降级** 的能力：使 Coordinator 能基于自身请求观测主动隔离故障实例，并在 D 池耗尽时降级到 P/U 实例以保全请求。

## 【技术要点】

1. **两角色熔断架构**：`SchedulerServer` 作为熔断中枢维护状态机；`InferenceWorker`（经 `SchedulerClient`）作为执行者，异步上报 + 本地缓存熔断状态，路由时直接跳过被熔断实例。
2. **触发条件**：对一个实例**连续失败达到阈值（默认 3 次）**即进入 OPEN 状态；阈值通过连续计数，确保偶发抖动不会误熔断。
3. **指数退避熔断时长**：`min(2^(熔断次数-1) × 30s, 300s)`，即依次为 30s → 60s → 120s → 240s → 300s（封顶），反复故障逐步延长探测间隔。
4. **三种恢复路径**：① 熔断计时器到期自动恢复；② OPEN 期间收到 success 上报（如探针请求成功）立即提前恢复；③ Controller 推送 SET 事件时**强制清除所有熔断状态**（视为已做健康校验）。
5. **状态同步机制**：状态权威在 `SchedulerServer`，Worker 以 **fire-and-forget + asyncio.create_task** 异步上报（非阻塞请求路径），状态变更通过 **ZMQ PUB/SUB 广播 `{instance_id, open/closed}`**，Worker 写入本地 `_cb_blocked_instances` 集合，路由仅读本地，无额外 RPC。
6. **PD 分离三种降级形态**：① 非流式降级：完整 prompt 重发 P/U 实例；② 流式 restart：HTTP 200 未提交、客户端未收 token 时重发并重新流式输出；③ 流式 resume：已向客户端返回部分 token 时由 `Rescheduler` 缓存 token 构造续推请求，对客户端透明。

## 【关键机制与数据】

- **阈值**（原文）：连续失败"默认 3 次"触发熔断。
- **熔断时长公式**（原文）：`min(2^(熔断次数-1) × 30s, 300s)`，上限 300s。
- **数据流闭环**（原文综合）：
  1. 请求失败 → Worker 用 `asyncio.create_task` fire-and-forget 上报 failure；
  2. `SchedulerServer` 计数 +1，达到 3 则置 OPEN 并启动计时器；
  3. 经 ZMQ PUB/SUB 广播 `{instance_id, open}`；
  4. Worker 更新本地 `_cb_blocked_instances`；
  5. 后续路由直接跳过 OPEN 实例，不再产生远程查询开销。
- **PD 降级触发**（原文）：D 池中所有 D 都被熔断后，`UnifiedPDRouter` 检测无可用 D，将请求降级到 `PDHybridRouter`，由单个 P 或 U 完成完整推理。
- **Controller 独立性**（原文）：Controller 故障期间，Coordinator 仅靠自身观测即可规避坏实例；SET 事件全量到来时强制清除熔断，避免历史熔断污染新实例视图。
- 原文未给出具体时延、QPS、内存占用等性能数据。

## 【表格解读】

**表 1：熔断功能角色与职责（原文 §2.1）**

| 角色 | 组件 | 职责 |
|---|---|---|
| 熔断中枢 | `SchedulerServer` | 维护各实例的熔断状态机，接收上报，广播熔断变更 |
| 熔断执行者 | `InferenceWorker`（`SchedulerClient`） | 上报请求成败，本地缓存熔断状态，路由时跳过被熔断实例 |

逐行解读：
- 第一行明确**状态权威归属**：`SchedulerServer` 持有状态机、接收上报、广播变更，是唯一真源；这决定了任何恢复/熔断判定都集中于此，避免 Worker 间状态不一致。
- 第二行明确**执行侧职责**：`InferenceWorker`/`SchedulerClient` 既上报（写）又读本地集合（读），路由路径上**只访问本地集合**，避免把熔断判定放到热路径上，确保不增加请求延迟。
- 文末附注 Controller 仅推送 **SET/ADD/DEL** 事件，其中 SET 会触发全量熔断清除；Inference Instances（P/D/U）在降级时可由 P 或 U 承担完整推理。

**表 2：PD 分离降级三情形（原文 §2.4）**

| 情形 | 触发条件 | 处理方式 |
|---|---|---|
| 非流式降级 | 非流式请求，D 池耗尽 | 将原始 prompt 重新发送到 P/U 实例，等待完整响应 |
| 流式重启（restart） | 流式请求，HTTP 200 尚未提交，客户端未收到任何 token | 将原始 prompt 重新发送到 P/U 实例，重新开始流式输出 |
| 流式续推（resume） | 流式请求，已向客户端返回部分 token | 利用已生成的 token 构造续推请求，在 P/U 实例上继续流式输出，对客户端透明 |

逐行解读：
- 情形 1（restart）适用于**客户端尚未建立流式感知**的场景：HTTP 200 仍未提交意味着连接在协议层面尚未对客户端"生效"，因此重新发起流式对客户端是等价的。
- 情形 2（resume）针对**已部分流式输出**的场景：此时中断会让客户端察觉连接重置，因此由 `Rescheduler` 复用已生成 token 构造续推，保证上下文延续与连接不中断，对客户端完全透明。
- 三情形层层递进，覆盖"还没流 / 流了一部分 / 流了很多"三种不同程度的推进状态，确保 D 池耗尽时任意推进点都能继续完成推理，不丢请求。

> §2.2 中的状态机以文本图（非表格）形式给出，原文如下，**逐字保留**：

```text
正常（CLOSED）
    │
    │  连续 failure 达到阈值（默认 3 次）
    ▼
熔断（OPEN）──── 超时自动恢复 ────► 正常（CLOSED）
    │                                      ▲
    │  收到 success 上报                    │
    └──────────────────────────────────────┘
```

解读：状态机只有 CLOSED / OPEN 两态，无 HALF-OPEN 中间态；恢复来自三条路径——计时器超时、OPEN 期间收到 success、Controller 推送 SET 强制清除。

## 【公式解读】

**熔断时长公式（原文 §2.2 / §3.1）**：

$$
\text{timeout} = \min\!\left(2^{(\text{熔断次数}-1)} \times 30\text{s},\ 300\text{s}\right)
$$

符号含义与作用：
- `2^(熔断次数-1)`：第 1 次熔断为 $2^0=1$，第 2 次为 $2^1=2$，第 3 次为 $2^2=4$ ……实现指数级递增。
- `30s`：基础时间单元，第 1 次熔断的恢复探测间隔即为 30s。
- `300s`：恢复间隔的上限；到达上限后不再继续增长，避免对持续故障实例过久停止探测。
- 序列举例（第 k 次熔断后的探测间隔）：30s → 60s → 120s → 240s → 300s → 300s ……

作用：对**反复故障实例**逐步延长恢复窗口，降低无效探测对故障后端的压力；对**偶发故障实例**则较快（30s）恢复可用性。

> 原文无其它数学公式或伪代码公式。

## 【关联】

文档中提到了以下上下游/模块关系：
- **Controller（上游）**：推送 SET/ADD/DEL 事件；SET 事件触发 `SchedulerServer` 全量清除熔断状态，是熔断清理的"硬重置"信号。
- **`SchedulerServer`（核心中枢）**：熔断状态权威来源；与 `SchedulerClient`/`InferenceWorker` 通过 ZMQ PUB/SUB 维持最终一致；与 Controller 通过事件通道对接。
- **`InferenceWorker` + `SchedulerClient`（下游执行）**：维护 `_cb_blocked_instances` 本地缓存；路由路径读取本地集合；通过 `asyncio.create_task` 异步上报。
- **`UnifiedPDRouter` ↔ `PDHybridRouter`（PD 路由层）**：在 D 池耗尽时由 `UnifiedPDRouter` 触发降级，将请求转交 `PDHybridRouter`，由单个 P 或 U 实例承担完整推理。
- **`Rescheduler`（流式续推组件）**：在流式 resume 场景下缓存已生成 token，构造续推请求以保证客户端无感知续推。
- **推理实例（P / D / U）**：D 实例故障是熔断主要对象；P 或 U 在降级时承担完整推理。
- 注：原文末尾标记"内部链接: (无)"，故未提供更多跨文档链接。

## 【使用方法】

原文**仅给出默认值与派生公式**，未提供完整启用方式/配置文件项/CLI 命令：

- **触发阈值**：默认 3 次连续失败（原文明确表述为"默认 3 次"，未给出修改入口）。
- **熔断时长**：由 `min(2^(熔断次数-1) × 30s, 300s)` 推导，无显式配置项说明。
- **Controller SET 清除**：`SchedulerServer` 接收 Controller 的 SET 事件后自动清除熔断，无需手工操作。
- **降级路径启用条件**：在 1P1D 部署下 D 实例全部熔断时**自动**触发。

原文未涉及：完整的配置文件路径、CLI/UI 启用开关、阈值与时长的修改方式、监控/告警指标项、日志字段说明。**原文未涉及**

## 图文联合解读

- `circuit_breaker_arch.png`: **图文联合解读**

1) 图示：左 Controller 经 instance events(SET/ADD/DEL) 推送给 Coordinator；其内 SchedulerServer（熔断中枢）维护 CircuitBreaker State Machine 与 Instance Pool，InferenceWorker×N（含 UnifiedPDRouter / PDHybridRouter / SchedulerClient）通过 PUB open/closed 与 report success/failure 与中枢双向通信，再经 HTTP 路由到 P Instance、D Instance、P or U Instance，并标注"D-pool circuit-broken → hybrid fallback"。

2) 技术结论：熔断构成 Coordinator 内部的闭环观测–决策–执行回路，不依赖 Controller；PD 分离下 D 池熔断时自动降级至 Hybrid 实例。

3) 与文档关系：印证 2.1 架构表的两类角色分工与 SET 全量清除、PD 降级保全请求的核心论点。
- `circuit_base_seq.jpg`: # 图文联合解读

**1) 图中内容**：UML时序图，含5个角色（外部client、workers、instances、scheduler_server、controller）。流程：客户端请求→workers选实例→instance故障返回→workers上报第1/3次故障→scheduler累加计数→第3次触发熔断、开启指数退避计时器（min(2^(n-1)*30s, 300s)）→Pub熔断开启→workers更新状态并跳过熔断实例→超时后Pub熔断关闭→controller恢复后发SET→scheduler清除熔断并Pub关闭。

**2) 技术结论**：论证自熔断闭环的完整性——通过"累计失败→OPEN→指数退避自动恢复→SET全量清除"机制，Coordinator（workers+scheduler_server）可独立完成故障隔离与恢复，不依赖Controller可用性。

**3) 与文档关系**：直观印证文档"Controller独立性"与"自动恢复"两大目标，尤其用controller先故障后恢复的标注，凸显SchedulerServer承担熔断中枢的必要性。
- `circuit_fallback_seq.jpg`: **1) 图中内容**：时序图含4条生命线（外部client、workers、instances、scheduler_server）。流程：client发推理请求→workers选PD分离路由→选D实例时遇故障（红×标注"d实例故障"）→返回故障→workers连续上报故障×3→scheduler_server触发熔断并Pub广播→workers更新本地熔断状态→重试发现D池无可用→触发降级混部（列出三条分支：非流式→单P重推；流式未返token→单P重推流式；流式已返token→单P续推）→改选P实例→请求返回。

**2) 技术结论**：论证当D实例全部熔断时，系统能自动从PD分离路由无缝降级到单P实例续推（含流式/非流式三种情形），请求不丢失。

**3) 与文档关系**：图解§1.2"PD分离降级保全请求"目标，可视化降级混部的三种具体分支策略。
