# 精度检测功能

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/features/precision_detection.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/features/precision_detection.md

# 精度检测功能 — 一体化深度解读

---

## 【定位】

这篇文档描述 mindie-motor 中**精度检测（Precision Detection）**这一容错特性：在 Decode 实例推理过程中通过采样 token 与 logprob 识别"大段重复/乱码/生僻字"类输出质量异常，按 PD 实例组粒度上报告警，并由 Controller 可选地自动终止异常实例，实现推理精度的在线监控与闭环恢复。

---

## 【技术要点】

1. **采样注入机制**：Coordinator Router 在 Decode 请求中注入 `logprobs`、`top_logprobs`、`return_token_ids` 三个字段，从响应缓存 `prompt_token_ids`、`output_token_ids`、`logprobs`、`topk_logprobs`，每实例组每 `interval_seconds`（默认 30.0 秒）最多送检一条完整样本。
2. **多档异常检测能力**：`logprobs_count=1` 仅支持大段重复；`>=3` 额外支持乱码；`>=5` 额外支持生僻字。值越大引擎侧开销越高。
3. **阈值告警与拨测联动**：同一实例组连续异常达 `precision_issue_threshold=10` 次后，先由 `InternalRouterProbe` 用固定问答（问题"相对论的发明人是谁"，响应需包含"爱因斯坦"）做拨测，拨测仍异常则上报精度告警 `alarm_id=0xFC001009` 至 Controller。
4. **Controller 侧自动恢复（可选）**：通过 `precision_auto_recovery_enabled=true` 启用，Controller 调用 `/controller/terminate_instance` 终止 D 实例，请求体可携带 `p_instance_id` 同步终止 P 实例；终止成功后 Controller 会向 CCAE Reporter 连续上报 `controlStatus=Completed` 共 **10 次** 后停止该 precision task 上报，并附加 `precision_alarm_clear=true` 清除精度告警。
5. **fail-open 设计**：msprobe 执行失败、top-k 与 token 数量不对齐、Scheduler ZMQ 失败等场景不会中断用户请求，也不会误触发恢复。Scheduler 客户端不可用时 `sampling_manager` 置为 `None`，本轮进程不启用完整采样链路。
6. **告警清除双路径**：依赖 Controller 终止后回调清除，或在活动告警下由 Coordinator 自身连续 `precision_clear_threshold=10` 次**有效正常**检测后自动上报 CLEAR（不依赖 auto-recovery）。

---

## 【关键机制与数据】

**工作原理（请求生命周期内）**：
Router → 注入采样参数 → 缓存响应字段 → Scheduler ZMQ 出口门控（每实例组按 `interval_seconds` 节流） → `MsprobeChecker` 调用 `msprobe.response_anomaly.detector.ILLDetector` 检测 → Scheduler 跨 Worker 记录连续异常计数 → 达阈值后 `InternalRouterProbe` 拨测 → `PrecisionAlarm` 上报 → Controller 决策恢复。

**数据流关键数字（原文）**：
- `interval_seconds` 默认 30.0 秒，节流粒度
- 异常累积阈值 `precision_issue_threshold=10`
- 清除阈值 `precision_clear_threshold=10`
- `probe_max_attempts=3`，`probe_timeout_seconds=600.0`
- CCAE 上报次数 = **10 次** `controlStatus=Completed`
- 告警标识 `alarm_id=0xFC001009`
- 日志关键字：`Precision check (token sampling)`、`inject_logprobs`、`SampleController: confirmed (scheduler)`、`submit`、`result`、`threshold reached`、`reporting alarm_id=0xFC001009`、`terminating D instance_id=`

---

## 【表格解读】

### 表 1：适用场景

| 维度 | 说明 |
|------|------|
| 部署形态 | PD 分离、CDP/Hybrid 等经过 Coordinator Router 转发 Decode 请求的部署形态 |
| 检测对象 | Decode 输出 token 序列及对应 logprob |
| 检测粒度 | PD 实例组；PD 分离使用 `(p_instance_id, d_instance_id)`，Hybrid 场景使用 `(None, union_id)` |
| 异常类型 | `logprobs_count=1` 支持大段重复；`>=3` 额外支持乱码；`>=5` 额外支持生僻字 |
| 处置方式 | Coordinator 上报告警；Controller 可选自动终止 D/P 实例 |

**逐行解读**：
- **部署形态**：仅适用于请求经 Coordinator Router 转发的部署架构，因此直连推理不适用。
- **检测粒度**：以"实例组"为单位，PD 分离用 `(p,d)` 二元组定位，Hybrid 用 `(None, union_id)`——这决定了"只终止 D 未终止 P"故障对应 P 实例 ID 缺失场景。
- **异常类型**：与 `logprobs_count` 强耦合，运维需根据需要识别的异常种类调整该参数。
- **处置方式**：报警与恢复解耦——Coordinator 始终上报，是否自动恢复由 Controller 侧独立开关控制。

### 表 2：Coordinator 侧 `precision_detection_config`

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `precision_check_enabled` | `false` | 精度检测总开关。关闭时不注入 logprobs、不采样、不检测，性能零额外开销 |
| `interval_seconds` | `30.0` | 每个实例组允许送检一条完整请求样本的最小间隔，单位秒 |
| `logprobs_count` | `1` | 注入到 Decode 请求的 top-k 宽度；值越大检测能力越强，引擎侧开销也越高 |
| `precision_issue_threshold` | `10` | 同一实例组连续检测异常达到该次数后触发拨测与告警 |
| `precision_clear_threshold` | `10` | 活动告警下连续有效正常样本达到该次数后上报清除告警 |
| `probe_max_attempts` | `3` | 精度拨测请求次数 |
| `probe_timeout_seconds` | `600.0` | 单次拨测超时时间，单位秒 |

**逐行解读**：
- **总开关默认关闭**意味着该特性在生产中按需开启，关闭时对 Decode 链路零侵入（关键运维承诺）。
- **`interval_seconds` 控制的是检测节流**，不是请求注入频率——所有 Decode 请求都会被注入，但真正送检的样本按此间隔限流。
- **`logprobs_count` 是能力-开销权衡旋钮**：需识别生僻字必须 `>=5`。
- **两个阈值对称设置**（均为 10），分别用于触发与清除，避免抖动。
- **拨测参数**定义了二次确认机制，避免单次误判直接告警/恢复。

### 表 3：Controller 侧配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `precision_auto_recovery_enabled` | `false` | Controller 收到 `alarm_id=0xFC001009` 的精度告警后，是否自动终止告警中的 D/P 实例 |

**逐行解读**：默认关闭体现"宁可不恢复也不误杀"的保守策略；启用后才会进入终止实例 + 向 CCAE 上报 Completed 流程。

### 表 4：验证日志关键词

| 日志关键词 | 含义 |
|------------|------|
| `Precision check (token sampling): interval=...` | 链路已启用（启动阶段） |
| `exit_gate=scheduler_zmq streak=scheduler_zmq probe=internal_router` | 出口门控、跨 Worker 计数、拨测组件三段均挂载 |
| `PrecisionSample: inject_logprobs` | Router 已向 Decode 请求注入采样参数 |
| `SampleController: confirmed (scheduler)` | Scheduler 放行了本实例组的一条样本 |
| `PrecisionSample: submit` | 样本已构造并提交给检测链路 |
| `MsprobeChecker: result` | msprobe 已返回检测结果 |
| `PrecisionReporter: threshold reached` | 连续异常达到阈值，开始拨测与告警 |
| `PrecisionAlarm: reporting alarm_id=0xFC001009` | 精度告警已上报 Controller |
| `Precision auto-recover: terminating D instance_id=` | Controller 已触发自动恢复 |

**逐行解读**：表中日志构成一条**完整调用链检查清单**，运维可按顺序核对——从启动挂载 → 注入 → 节流放行 → 提交 → 检测 → 阈值 → 告警 → 恢复——任一关键字缺失即可定位故障环节。

### 表 5：日志与排查

| 现象 | 可能原因 | 建议 |
|------|----------|------|
| 启动后没有 `Precision check` 日志 | `precision_check_enabled=false` 或配置未加载 | 检查 `motor_coordinator_config.precision_detection_config` |
| 日志提示 Scheduler client unavailable | Coordinator 未连接 Scheduler | 检查 Scheduler 进程和 ZMQ 连接 |
| `sample incomplete` | 引擎返回 token_ids 但未返回 logprobs | 检查引擎是否支持 logprobs 参数 |
| `MsprobeChecker: msprobe not installed` | 环境缺少 msprobe | 安装 msprobe 或在测试中显式注入 mock checker |
| 一直检测不到生僻字 | `logprobs_count < 5` 或 token2category 映射缺失 | 调大 `logprobs_count`，检查 msprobe 映射文件 |
| 告警有但未终止实例 | Controller 未开启自动恢复 | 检查 `precision_auto_recovery_enabled` |
| 只终止 D 未终止 P | 告警中 `p_instance_id` 为空 | 检查部署模式和实例组 key 是否能解析 P 实例 |

**逐行解读**：每条都对应一个**因果链**，运维根据现象定位到配置/依赖/数据三类原因之一。其中"Scheduler client unavailable"会触发 sampling_manager 置 None，整条检测链路停摆；"msprobe not installed"则会触发 fail-open，检测静默失败但请求不受影响——这两点是非侵入性设计带来的可观测性盲区，需要主动巡检。

---

## 【公式解读】

**原文无公式。** 文档以配置项和日志关键字驱动，无数学公式或伪代码形式表达。

---

## 【关联】

文档明确给出唯一内部链接：[精度检测设计文档](../../design/fault_tolerance/precision_detection.md)，属于 `docs/zh/design/fault_tolerance/` 路径下的设计文档。这表明：

- **上下游关系**：本篇 user_guide 文档面向"如何启用与验证"，设计文档面向"内部实现原理"——两者构成 user ↔ design 的标准双层文档结构。
- **所属特性域**：归类为**容错（fault_tolerance）**模块，与 mindie-motor 的实例恢复、告警体系同处一个能力簇。
- **协同模块**：
  - **Coordinator Router**：作为采样注入的执行点；
  - **Scheduler（ZMQ）**：作为实例组节流门控与跨 Worker 异常计数载体；
  - **msprobe（外部依赖）**：作为实际异常检测引擎；
  - **Controller** + **CCAE Reporter**：作为告警接收、自动终止、上报闭环的下游链路。

---

## 【使用方法】

**启用方式（原文）**：

1. 确认推理引擎支持 `return_token_ids` 和 `logprobs` 返回字段。
2. 确认运行环境已安装 `msprobe`，且 `msprobe.response_anomaly.detector.ILLDetector` 可导入。
3. 在 Coordinator `user_config.json` 的 `motor_coordinator_config.precision_detection_config` 中设置 `precision_check_enabled: true`，并按需调整 `interval_seconds`、`logprobs_count`、`precision_issue_threshold`、`precision_clear_threshold`、`probe_max_attempts`、`probe_timeout_seconds`。
4. （可选）在 Controller 配置 `motor_controller_config.precision_auto_recovery_enabled: true` 启用自动终止。
5. 使用现有 deploy 脚本重新部署：

```bash
cd examples/deployer
python deploy.py --config-dir ../infer_engines/vllm
```

**验证**：服务启动后观察 Coordinator 日志是否出现 `Precision check (token sampling): interval=... exit_gate=scheduler_zmq streak=scheduler_zmq probe=internal_router`，再发送普通推理请求并按"验证方法"日志关键词清单逐环节核对。
