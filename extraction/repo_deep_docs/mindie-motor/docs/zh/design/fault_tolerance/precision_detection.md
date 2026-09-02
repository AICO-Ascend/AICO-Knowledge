# 精度检测故障恢复特性

> 仓 `mindie-motor` · 路径 `docs/zh/design/fault_tolerance/precision_detection.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/design/fault_tolerance/precision_detection.md

# 「精度检测故障恢复」Design 文档深度解读

## 【定位】

本篇文档系统描述 mindie-motor 在 Coordinator 侧对 Decode 推理输出进行**在线采样 → msprobe 质量检测 → 固定问答拨测确认 → 告警上报 → Controller 自动终止实例**的完整精度异常检测与故障恢复链路设计,跨 Coordinator Inference Worker、Coordinator Scheduler、Controller 三类进程协同,最终通过 `alarm_id=0xFC001009` 将异常 PD 实例组从调度池中隔离并替换。

---

## 【技术要点】

1. **三层进程协同架构**:  Worker 跑"采集 + 检测 + 拨测 + 告警"重逻辑;Scheduler 仅维护跨 Worker 一致的轻量状态(门控 / 连续计数 / probing 标志 / action_token);Controller 接收告警后做实例终止决策。

2. **核心配置参数(原文 `PrecisionDetectionConfig`)**:
   - `precision_check_enabled` 默认 `false` —— 总开关,关闭时不修改 Decode 请求
   - `interval_seconds = 30.0` —— 实例组级采样送检间隔
   - `logprobs_count = 1`(默认)—— top-k 宽度;`1` 支持重复检测,`>=3` 支持乱码,`>=5` 支持生僻字
   - `precision_issue_threshold = 10` —— 连续异常触发拨测/告警的阈值
   - `precision_clear_threshold = 10` —— 活动告警下连续**有效正常**样本触发清除的阈值
   - `probe_max_attempts = 3` —— 拨测次数
   - `probe_timeout_seconds = 600.0` —— 单次拨测超时

3. **采样门控 `CONFIRM_SAMPLE`**: 通过 Scheduler 在 per-key lock 内为每个实例组每个采样窗口(由 `interval_seconds` 控制)最多放行一条完整样本,实现"全局唯一、跨 Worker 一致"的采样出口。

4. **检测 + 连续计数**: `PrecisionReporter.handle()` 在 per-key lock 内调用 `MsprobeChecker.check()`,通过 `AsyncSchedulerClient.record_precision_result()` 将 `has_issue` 上报 Scheduler 更新 `_precision_streak_counts`;若已经处于 `_precision_probing` 则返回 `skip=true`,Worker 释放锁后通过 `asyncio.create_task()` 异步执行拨测与告警。

5. **拨测设计 `InternalRouterProbe`**: 经完整 Router 管线对**目标实例组 pin** 发 `v1/chat/completions`,固定问题 `相对论的发明人是谁`,通过条件为响应文本包含 `爱因斯坦`;为防止递归采样,构造 Router 时显式传入 `sampling_manager=None`。

6. **告警 + 自动恢复**:  `PrecisionAlarm` 通过 `build_precision_issue_alarm()` + `ControllerApiClient.report_alarms()` 上报 `0xFC001009`;Controller `_maybe_precision_auto_recover()` 据 `precision_auto_recovery_enabled` 开关调用 `terminate_instance_for_recovery(d_id, "precision_alarm")` 与可选 P 实例终止;`terminate_instance_for_recovery()` 先 `InstanceManager.separate_instance()` 隔离再遍历 `NodeManagerApiClient.stop()`。

---

## 【关键机制与数据】

### 数据流(原文,精简):

```
Client → Router(inject logprobs) → Decode Engine
      → Router(cache token/logprob, strip client response)
      → SampleController(CONFIRM_SAMPLE)
      → PrecisionReporter(check + RECORD_PRECISION_RESULT)
      → PrecisionAlarm(InternalRouterProbe + report_alarms)
      → Controller(_maybe_precision_auto_recover)
      → terminate_instance_for_recovery
```

### 工作原理要点(均为原文):

- **采样生成**: Router 在流式 chunk 级用 `_collect_logprobs_from_stream_chunk()` 缓存 token id 与 logprob,非流式 body 级用 `_collect_logprob_from_nonstream_body()`,最后 `_submit_token_sample()` 构造 `DecodeSample` 提交给 `SampleController.submit_sample()`。
- **路由策略与实例组 key**:  `unified_pd.py` 用 `(p_instance_id, d_instance_id)`;`pd_hybrid.py` 用 `(None, union_id)`。
- **拨测后必上报告警**: 原文"无论拨测成功或失败,都会上报告警;拨测失败次数写入 `additional_information`"。
- **告警清除三条路径(原文)**:
  1. **auto-recovery 清除**: Controller 终止原 P/D 全部成功,原实例已不存在,立即清除。
  2. **CCAE 手动清除**: CCAE 下发 precision control 且 Controller 终止 P/D 全部成功,与 auto-recovery 共用 `complete_precision_pd_group_recovery`。
  3. **连续正常清除**: 未开启 auto-recovery 或告警仍活动时,同 PD Group 累计 `precision_clear_threshold` 次**有效正常**检测后,Coordinator 上报 CLEAR。
- **moi 一致性约束**: 原文"清除告警必须与产生告警使用完全相同的 `moi`;Scheduler 在产生告警成功后保存原始 `moi`,后续清除直接复用,禁止重新拼接"。
- **CCAE 北向上报窗口(原文)**: 从首次收到 `controlCode` 起算,最多持续上报 **10 分钟(600 秒)**;`Completed`/`Failed` 累计成功上报 **10 次**后删除 task;相同 `controlCode` 抑制忽略,不同 `controlCode` 重启计时;CCAE 返回 `controlStatusRespond=true` 不提前删除 task;HTTP 失败不计入次数,下一周期继续上报。
- **Controller 同步资源清理**: Controller 通知 Coordinator 删除 Scheduler 活动告警状态后,返回字段 `scheduler_state_cleared`(原文:"用于暴露状态清理是否成功,不改变实例终止成功的判定")。

### 性能 / 数值数据:

- **采样频率**:  实例组级每 `30.0` 秒最多送检一次样本。
- **检测灵敏度门槛**:  连续 `10` 次异常触发拨测;连续 `10` 次有效正常清除告警。
- **拨测容忍**:  最多 `3` 次尝试,每次超时 `600.0` 秒。
- **CCAE 终态退出**:  10 次成功上报 **或** 距首次 600 秒,二者先到即删除 task。
- **告警 ID**:  `0xFC001009`(精度异常)。

> 注: 原文未提供 msprobe 模型自身指标(准确率、误报率等)、采样对推理吞吐的实测影响、告警上报端到端延迟等性能基准数据。

---

## 【表格解读】

### 表 1 · 章节入口导航(原文逐字还原)

| 项 | 说明 |
|----|------|
| 用户指南 | [精度检测功能](../../user_guide/features/precision_detection.md) |
| Coordinator 数据采集 | `motor/coordinator/router/precision_sample/` |
| Coordinator 检测编排 | `motor/coordinator/fault_tolerance/precision/` |
| Coordinator 拨测告警 | `motor/coordinator/fault_tolerance/probe/`、`motor/coordinator/fault_tolerance/alarm/` |
| Scheduler 全局状态 | `motor/coordinator/scheduler/` |
| Controller 自动恢复 | `motor/controller/api_server/controller_api.py`、`motor/controller/core/recovery_service.py` |

**解读**: 表格把整条精度检测链路按代码仓目录做了角色切分——`precision_sample/` 负责 Router 层的请求注入与响应缓存;`fault_tolerance/precision/` 是检测编排主体;`fault_tolerance/probe/` 与 `alarm/` 负责拨测与告警;`scheduler/` 保存跨进程一致的轻状态;Controller 的两个文件则实现 API 接入与恢复服务。用户指南通过相对路径指向 `user_guide/features/precision_detection.md`。

---

### 表 2 · 模块分层职责(原文逐字还原)

| 层次 | 组件 | 职责 |
|------|------|------|
| 数据采集 | `inject_logprobs`、`update_logprob_cache`、`build_decode_sample` | 对 Decode 请求注入采样参数,并从响应中缓存 token/logprob |
| 出口门控 | `SampleController` + Scheduler `CONFIRM_SAMPLE` | 每个实例组每个采样窗口最多放行一条完整样本 |
| 检测编排 | `PrecisionReporter` + `MsprobeChecker` | 执行 msprobe 检测,并记录跨 Worker 连续异常次数 |
| 拨测告警 | `InternalRouterProbe` + `PrecisionAlarm` | pin 目标实例组进行固定问答拨测,构造并上报告警 |
| 自动恢复 | Controller `_maybe_precision_auto_recover` | 根据精度告警终止 D 实例及可选 P 实例 |

**解读**: 把模块按"职责域"抽象成五层流水线。每一层的关键组件都用代码实体(类/函数)直接列出;流水线从下往上读,可清晰看出"采 → 门控 → 检 → 报 → 恢"五个阶段的强顺序依赖关系。"出口门控"层是跨进程一致性的关键设计——把"窗口期内是否放行"决策交给 Scheduler,Worker 只负责请求与执行,避免多个 Inference Worker 重复采样。

---

### 表 3 · `PrecisionDetectionConfig` 字段表(原文逐字还原)

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `precision_check_enabled` | `false` | 总开关,关闭时不修改 Decode 请求 |
| `interval_seconds` | `30.0` | 实例组级采样送检间隔 |
| `logprobs_count` | `1` | 注入 top-k 宽度;1 支持重复,>=3 支持乱码,>=5 支持生僻字 |
| `precision_issue_threshold` | `10` | 连续异常触发拨测/告警的阈值 |
| `precision_clear_threshold` | `10` | 活动告警下连续有效正常样本触发清除的阈值 |
| `probe_max_attempts` | `3` | 拨测次数 |
| `probe_timeout_seconds` | `600.0` | 单次拨测超时时间 |

**解读**:
- 总开关默认 `false`,部署启用是显式 opt-in;关闭后 Router 不再注入采样参数,对在线 Decode 业务**无副作用**。
- `interval_seconds=30.0` 与 `precision_issue_threshold=10` 共同决定了"理论最快告警时延 ≈ 30s × 10 = 5 分钟"级别的反应窗口。
- `logprobs_count` 是**检测能力开关**:值越大能从模型获取越多候选 token 概率分布,所支持的异常类型越多,但对推理引擎开销也随之增大;默认 `1` 仅能支撑重复检测。
- `precision_issue_threshold` 与 `precision_clear_threshold` 都设为 `10`,说明设计意图是**对称**——异常累积与正常累积速度一致,避免告警易进难出。
- 拨测侧 `probe_max_attempts=3` 与 `probe_timeout_seconds=600.0` 给单次拨测最多 30 分钟的总预算(3 × 600s)。

---

### 表 4 · Router 基类日志概率采集方法(原文逐字还原)

| 方法 | 说明 |
|------|------|
| `_collect_logprobs_from_stream_chunk()` | 流式 chunk 级缓存 token id、logprob,并按客户端原始请求决定是否剥离 logprobs |
| `_collect_logprobs_from_nonstream_body()` | 非流式响应 body 级缓存 token id、logprob |
| `_submit_token_sample()` | 构造 `DecodeSample` 并交给 `SampleController.submit_sample()` |

**解读**: 三方法覆盖了 Router 的两种响应形态(流式 chunk / 非流式 body),并统一以 `DecodeSample` 提交给 `SampleController`。"按客户端原始请求决定是否剥离 logprobs"说明对客户端响应做了**透明采样**——注入 logprob 不影响最终用户响应内容,仅在 Router 内部消费。

---

### 表 5 · 路由策略与实例组 key(原文逐字还原)

| 路由策略 | 实例组 key |
|----------|------------|
| `unified_pd.py` | `(p_instance_id, d_instance_id)` |
| `pd_hybrid.py` | `(None, union_id)` |

**解读**: 两种部署拓扑对应的采样聚合粒度不同——`unified_pd` 是 P+D 双实例配对,key 用 `p_instance_id` 与 `d_instance_id`;`pd_hybrid` 是混合拓扑,用 `union_id` 标识同一聚合单元,且 `p_instance_id` 留 `None`(与下文告警 `moi` 格式的"有 P/无 P 实例"分支相对应)。

---

### 表 6 · `InternalRouterProbe` 拨测规格(原文逐字还原)

| 项 | 说明 |
|----|------|
| 请求 API | `v1/chat/completions` |
| 问题 | `相对论的发明人是谁` |
| 通过条件 | 响应文本包含 `爱因斯坦` |
| 路由约束 | `SchedulingConstraint.for_precision_probe(p_instance_id, d_instance_id)` |
| 采样防递归 | 构造 Router 时传入 `sampling_manager=None` |

**解读**: 拨测用 `SchedulingConstraint.for_precision_probe(...)` 把请求**强制 pin**到待检测的 `(p, d)` 实例组,避免被路由调度到其他正常实例组导致"假阳性通过"。`sampling_manager=None` 是防止拨测请求本身又被精度采样链路捕获形成递归调用。问题与答案都是固定的常识类问答,目的是快速低成本地检验"模型基础语言生成能力是否完整"。

---

### 表 7 · Scheduler 状态字段(原文逐字还原)

| 字段 | key | 含义 |
|------|-----|------|
| `_sample_exit_last_time` | `(p_instance_id, d_instance_id)` | 上次放行样本的时间戳 |
| `_precision_streak_counts` | 同上 | 当前连续异常次数 |
| `_precision_probing` | 同上 | 是否正在执行拨测/告警 |
| `_precision_action_tokens` | 同上 | 本轮 action 的 UUID,用于 FINISH 校验 |

**解读**: 四个字段共享同一 per-key 索引(`(p_instance_id, d_instance_id)`,对 `pd_hybrid` 则为 `(None, union_id)`),共同支撑**门控 + 计数 + 状态机一致性**:`_sample_exit_last_time` 实现采样间隔节流;`_precision_streak_counts` 累加/衰减连续异常;`_precision_probing` 防止重复进入拨测;`_precision_action_tokens` 用 UUID 校验 `FINISH_PRECISION_ACTION` 属于哪一轮,避免过期回调污染状态。原文"均**在同一个 per-key lock 内**更新状态"——这是并发正确性的关键设计。

---

### 表 8 · 告警清除路径(原文逐字还原)

| 路径 | 触发时机 | 说明 |
|------|----------|------|
| auto-recovery 清除 | Controller 终止原 P/D 全部成功 | 原实例已不存在,立即清除对应告警;新实例按新 PD Group 重新检测 |
| CCAE 手动清除 | CCAE 下发 precision control 且 Controller 终止 P/D 全部成功 | 与 auto-recovery 共用 `complete_precision_pd_group_recovery`:清除 OM 告警并通知 Coordinator 删除 Scheduler 活动状态 |
| 连续正常清除 | 未开启 auto-recovery,或告警仍活动 | 同一 PD Group 累计 `precision_clear_threshold` 次**有效正常**检测后,Coordinator 上报 CLEAR |

**解读**: 告警清除被显式拆成三条互斥路径,关键区分点是"Controller 是否真的把目标 P/D 干掉"。**auto-recovery / CCAE** 两条都是"实体已灭,告警同步撤销",**连续正常清除**则是"实体仍在,只是模型恢复健康,需要可信的连续正常计数才能撤"。这意味着若不开启 `precision_auto_recovery_enabled`,告警只能靠第三条路径自然消除——清除速度受 `precision_clear_threshold × interval_seconds` 影响,默认 30s × 10 = 5 分钟级别的恢复滞后。

---

### 表 9 · `moi` 格式(原文逐字还原)

| 场景 | `moi` 格式 |
|------|------------|
| 有 P 实例 | `service name=Coordinator, service ip=..., pId={p_id}, instanceId={d_id}` |
| 无 P 实例 | `service name=Coordinator, service ip=..., instanceId={d_id}` |

**解读**: OM 平台告警身份字段 `moi` 的拼装要区分 Prefill-Decode 拓扑。**有 P 时必须把 `pId` 写进 `moi`** 才能让 CCAE / OM 后续能精准定位 Prefill 实例。"Scheduler 在产生告警成功后保存原始 `moi`,后续清除直接复用,禁止重新拼接"说明设计上把 `moi` 当成不可变身份标识,避免产生/清除两端的 `moi` 不一致导致 OM 平台匹配失败。

---

### 表 10 · CCAE 北向 Completed 上报规则(原文逐字还原)

| 规则 | 说明 |
|------|------|
| 上报窗口 | 从首次收到 `controlCode` 起算,最多持续上报 **10 分钟**(600 秒);窗口内按周期继续上报 `controlStatus` |
| 窗口到期 | 10 分钟内未进入终态或终态上报未结束时,删除 task 并恢复普通裸心跳(不再携带 `controlCode/controlStatus`) |
| 同码抑制 | task 因窗口到期或终态成功上报 10 次而结束后,后续重复下发的**相同** `controlCode` 一律忽略,不再重启计时 |
| 新码重启 | 收到**不同** `controlCode` 时解除抑制,重新创建 task 并从零开始 10 分钟计时 |
| 成功上报计数 | 仅统计 HTTP POST 成功且 body 携带 `controlStatus=Completed` 或 `Failed` 的周期上报 |
| 停止条件 | `Completed`/`Failed` 累计成功上报 10 次后删除 task;或距首次收到 `controlCode` 已满 10 分钟 |
| 提前 ack | CCAE 返回 `controlStatusRespond=true` 不提前删除 task |
| 失败重试 | HTTP 失败不计入次数,下一周期继续上报 |

**解读**: 这是 Controller 与北向 CCAE 之间的状态上报协议,把"上报→终态→退出"封装成一个**有状态 task**,用 10 分钟硬窗口 + 10 次成功上报双保险退出;用 `controlCode` 内容做去重/重启——只有**不同的 `controlCode`** 才能让已结束的 task 重启,相同 `controlCode` 重复下发不再复活。这是一种典型的"task 生命周期管控 + 防抖"设计,避免外部系统重复触发造成资源抖动。HTTP 失败不计入成功次数,体现了"确认送达"原则而非"尝试次数"。

---

## 【公式解读】

原文无公式。

(原文给出的 sequenceDiagram / classDiagram / 目录树均属结构图,非数学公式或伪代码公式;唯一可视为"伪代码形式"的逻辑是状态机,但原文中以"在同一个 per-key lock 内更新状态"等自然语言描述,未给出形如 `S_t+1 = f(S_t, ...)` 的显式表达式,故此处不引入未在原文出现的内容。)

---

## 【关联】

### 模块上下游

- **Router 子模块**:  `motor/coordinator/router/precision_sample/`(request.py / response.py / sample_builder.py)是入口数据源;由 Router 基类 `_collect_logprobs_from_stream_chunk()` / `_collect_logprob_from_nonstream_body()` / `_submit_token_sample()` 提供能力,依赖 `unified_pd.py` / `pd_hybrid.py` 等路由策略提供实例组 key。
- **Coordinator Scheduler**:  `motor/coordinator/scheduler/` 及其 runtime 子模块(`scheduler_client.py` / `scheduler_server.py` / `zmq_protocol.py`)承载全局状态与三组操作 `CONFIRM_SAMPLE` / `RECORD_PRECISION_RESULT` / `FINISH_PRECISION_ACTION`,三者均在 per-key lock 内执行,保证多 Worker 一致性。
- **Coordinator 检测编排**:  `motor/coordinator/fault_tolerance/precision/`(sample_controller.py / reporter.py / checker.py / streak_result.py)是检测主体,`MsprobeChecker` 是当前生产装配实现。
- **Coordinator 拨测/告警**:  `motor/coordinator/fault_tolerance/probe/`(chat_probe.py / router_probe.py)与 `motor/coordinator/fault_tolerance/alarm/`(base.py / precision_alarm.py)负责 pin 目标实例组、固定问答拨测、构造告警并通过 `ControllerApiClient.report_alarms()` 上报。
- **Controller**:  `motor/controller/api_server/controller_api.py` 接收告警;`motor/controller/core/recovery_service.py` 提供 `terminate_instance_for_recovery()` 与 `complete_precision_pd_group_recovery()` 两个核心服务;`_maybe_precision_auto_recover()` 是入口决策函数。

### 上游依赖

- **msprobe**:  作为检测算法后端,封装在 `MsprobeChecker.check()` 中。文档未展开其内部检测规则,仅说明支持"大段重复、乱码、生僻字"等输出质量异常,且 `logprobs_count` 大小与可检测异常类型相关(`1` 支持重复 / `>=3` 支持乱码 / `>=5` 支持生僻字)。
- **Decode Engine**:  Router 把注入 logprob 的请求发到 Decode Engine,期望其支持 `logprobs` 字段输出。

### 下游 / 北向集成

- **OM 告警平台**:  `moi` 字段作为精度告警的唯一标识;CLEAR 与 RAISE 必须使用完全相同的 `moi`。
- **CCAE 北向**:  Controller 通过 CCAE Reporter(`examples/features/observability/ccae_reporter/reporters/ccae_reporter.py`)消费 CCAE 下发的 precision control,把 task 状态按 10 分钟窗口 + 10 次成功上报规则回写 `controlStatus`。

### 内部链接

- 用户指南:[精度检测功能](../../user_guide/features/precision_detection.md)—— 本 design 文档与其配套,该用户文档提供面向使用方的功能说明与配置指引。

### 与其他故障恢复特性的关系

- 告警 ID `0xFC001009` 是该特性的独立 ID,Controller 用 `record.alarm_id != 0xFC001009` 直接 return 来把精度告警与其他类别告警(实例心跳 / 网络 / OOM 等)区分处理。
- `terminate_instance_for_recovery()` 是精度告警与其他故障恢复通路共享的终止服务入口,体现了"统一恢复原语,差异化告警判定"的设计原则。
- `_precision_probing` 标志位的存在,意味着同一 PD Group 在拨测未完成期间新的异常会上报 `skip=true`,避免重复触发拨测任务堆积。

---

## 【使用方法】

### Coordinator 侧(检测与告警上报)

- **总开关**: `precision_check_enabled`,默认 `false`,关闭时不修改 Decode 请求;设为 `true` 才进入完整精度检测链路。
- **采样参数**:
  - `interval_seconds`(默认 `30.0`):实例组级采样送检间隔。
  - `logprobs_count`(默认 `1`):注入 top-k 宽度;依据业务异常类型需求上调(`>=3` 支持乱码,`>=5` 支持生僻字)。
- **告警阈值**: `precision_issue_threshold`(默认 `10`)控制连续异常触发拨测/告警的门限;`precision_clear_threshold`(默认 `10`)控制活动告警下连续**有效正常**样本清除告警的门限。
- **拨测参数**: `probe_max_attempts`(默认 `3`)与 `probe_timeout_seconds`(默认 `600.0`),合计单 PD Group 单次告警拨测的最长总预算 ≈ 30 分钟。
- **启动装配**: `InferenceServer._lifespan()` 在 Coordinator 启动时自动装配;若 `precision_check_enabled=false` 或 Scheduler client 不可用,则 `app.state.sampling_manager=None`,本进程 **fail-open**(不采集不检测);其余情况调用 `build_precision_reporter()` 装配 `MsprobeChecker`、`InternalRouterProbe`、`PrecisionAlarm`、`PrecisionReporter`、`SampleController`。

### Controller 侧(自动恢复)

- **`precision_auto_recovery_enabled`**: 默认关闭,**独立于** Coordinator 侧总开关;只影响 Controller 收到精度告警后的动作,**不影响** Coordinator 是否检测和上报告警。开启后,Controller 在 `_maybe_precision_auto_recover()` 中自动终止 D 实例与可选 P 实例。

### 北向 CCAE 集成

- Controller 暴露 `POST /controller/terminate_instance`,请求体携带 `instance_id={d_id}`、`p_instance_id={p_id}` 和 `precision_alarm_clear=true`,用于 CCAE 下发 precision control 时触发 `complete_precision_pd_group_recovery`。

> 备注: 原文未涉及具体 CLI 命令、YAML 配置示例、环境变量名或 Helm values 等部署细节;这些内容预期由用户指南 `precision_detection.md` 与运维配置文档给出。
