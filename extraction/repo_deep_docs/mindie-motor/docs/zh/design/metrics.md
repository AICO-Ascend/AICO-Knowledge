# Metrics 可观测性指标设计文档

> 仓 `mindie-motor` · 路径 `docs/zh/design/metrics.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/design/metrics.md

# 一体化深度解读：MindIE Motor Metrics 可观测性指标设计文档

## 【定位】

本文档定义了 MindIE Motor 在 Coordinator 侧的 Metrics 子系统设计，统一从 vLLM 引擎 Pod 采集 Prometheus 指标，通过语义感知聚合 + Motor 自有计算指标层 + 引擎重启无偏差的 counter rate 机制，最终以 `full / instance / role / dp / node` 五种视图重新暴露给 Prometheus / OpenTelemetry Collector，解决"如何让上层监控在不耦合 vLLM 内部指标命名的情况下获得稳定、可聚合、可对比的集群观测数据"这一问题。

---

## 【技术要点】

1. **语义感知聚合（Semantic-aware Aggregation）**：每个已知 vLLM 指标被映射到 `MetricSemantic`（10 类），由 `SemanticAggregationEngine` 按语义分发到 5 种聚合策略（Sum / Max / Mean / Histogram Merge / Passthrough），不再按指标名硬编码聚合方式。

2. **Motor 计算指标层（`MotorMetricComputer` + `ComputedMetricDef`）**：Motor 自有计算指标（如 TPS、Worker 计数）通过声明式 `ComputedMetricDef` 注册，集中管理；通过 `pre_aggregation`（DP 级，注入 endpoint metrics 列表）和 `post_aggregation`（Service 级，追加 aggregate 列表）两阶段注入，无需修改 `MetricsCollector`。

3. **Counter Rate 重启容错**：以 `(job_name, dp_rank)` 作为稳定标识（跨重启不变），配合 `instance_id` 变化 + `raw_counter` 显著下降（drop > 10%）的双重检测做重启识别，通过 baseline 偏移机制继承上一轮 effective counter 值，确保引擎重启后速率计算不出现负值或尖峰。

4. **DP 级与 Service 级指标差异化注入时机**：DP 级（counter rate，如 `motor:prompt_tokens_per_second`）在 `_parse_metrics()` 之后、`pre_aggregation` 阶段注入 endpoint，使自然参与后续 DP → Instance → Service 聚合流水线；Service 级（worker 计数，如 `motor:active_prefill_workers`）在 `_generate_full_metrics()` 聚合完成后追加。

5. **五视图输出**：同一份数据支持 `full`（SERVICE 级，默认 Prometheus 抓取）、`instance`（注入 `instance_id`、`role`）、`role`（Prefill vs Decode 对比）、`dp`（per-endpoint，注入 `dp_rank`、`role`、`instance_id`、`pod_ip`）、`node`（注入 `pod_ip`、`role`）五种聚合视图。

6. **角色感知 + 派生指标**：聚合引擎在 SERVICE 级聚合时按 `role_scope`（如 TTFT 为 `decode` 范围）过滤；`post_process` 阶段从合并后的直方图计算 p50/p95/p99 与均值，并派生比率指标（如 `prefix_cache_hit_rate = hits / queries`）。

---

## 【关键机制与数据】

### 工作原理（四层流水线）

整个系统由四层协同工作：

- **Layer 1（`metric_types.py`）**：定义通用数据结构 `Metric`（含 `name/help/type/label/value`）、`MetricType`（`GAUGE/COUNTER/HISTOGRAM/SUMMARY`）、`AggregationScope`（`INSTANCE/ROLE/NODE/SERVICE`）、`AggregationContext`（scope + instance_roles + deploy_mode + ins_ids）。
- **Layer 2（`metric_registry.py`）**：每个已知 vLLM 指标名 → `MetricSemantic` → 决定聚合策略与是否做角色过滤。
- **Layer 3（`aggregation_engine.py`）**：`SemanticAggregationEngine` 两阶段处理（`aggregate` + `post_process`）。
- **Layer 4（`metrics_collector.py`）**：后台 daemon 线程跑完整流水线 `采集 → 解析 → 计算 → 聚合 → 缓存 → 格式化`。

### 数据流（主编排器流水线）

```
各 Engine /metrics 端点 (HTTP)
  → _fetch_instance_metrics()        拉取原始 Prometheus 文本
  → _parse_metric_text()             解析为 list[Metric]
  → _motor_computer.compute_pre_aggregation()
  │   └── 注入 DP 级计算指标（如 TPS）到 endpoint metrics 列表
  → 存入 _last_collects

get_metrics("full")
  → _aggregate_collects_by_instance()   INSTANCE 级聚合
  → _aggregate_metrics_all_instance()   SERVICE 级聚合（含 role 过滤）
  → post_process()                      直方图分位数 + 比率派生
  → _motor_computer.compute_post_aggregation()
  │   └── 追加 Service 级计算指标（如 worker 计数）
  → _format_prometheus()              输出 Prometheus 文本
```

### Counter Rate 重启容错的状态转移（原文时间线示例）

- **T0**：job=decoder-0, dp_rank=0, ins_id=5, raw_counter=10000 → baseline=0, effective=10000, TPS=0（首次无历史）
- **T1**：job=decoder-0, dp_rank=0, ins_id=5, raw_counter=11000 → effective=11000, TPS=1000/dt ✓
- **T2（重启后）**：job=decoder-0, dp_rank=0, ins_id=12, raw_counter=50 → 检测到 ins_id 12 ≠ 5，baseline 继承为 11000，effective=50+11000=11050，TPS=(11050-11000)/dt ≈ 0 ✓
- **T3**：effective=500+11000=11500，TPS=(11500-11050)/dt=450/dt ✓

**重启双重判定条件**（原文）：
- `instance_id` 发生变化
- `raw_counter` 显著下降（drop > 10%）

> 注：原文未给出 Prometheus 抓取频率、指标总量、聚合吞吐量等性能数据。

---

## 【表格解读】

### 表 1：Layer 1 基础类型（`metric_types.py`）

| 类型 | 说明 |
|------|------|
| `Metric` | 通用指标表示：`name`、`help`、`type`、`label`（列表）、`value`（列表） |
| `MetricType` | Prometheus 标准类型：`GAUGE`、`COUNTER`、`HISTOGRAM`、`SUMMARY` |
| `AggregationScope` | 聚合范围：`INSTANCE`、`ROLE`、`NODE`、`SERVICE` |
| `AggregationContext` | 聚合上下文：scope + instance_roles + deploy_mode + ins_ids |

**解读**：这是整个子系统的数据基座。`Metric` 用"标签列表+值列表"而非 dict，适配 Prometheus 文本格式的多 label 同名指标；`AggregationScope` 枚举对应 5 种视图中的 4 类聚合粒度（`dp` 视图本身为 per-endpoint 无聚合）；`AggregationContext` 把聚合时需要的"做什么范围聚合、哪些角色参与、是什么部署模式、目标实例集合"打包传递，避免聚合函数签名臃肿。

### 表 2：Layer 2 语义注册表（`metric_registry.py`）

| 语义类别 | 聚合方式 | 典型指标 |
|---------|---------|---------|
| `COUNTER` | Sum | `request_success_total` |
| `THROUGHPUT_COUNTER` | Sum | `prompt_tokens_total`、`generation_tokens_total` |
| `STATE_GAUGE` | Sum | `num_requests_running`、`process_open_fds` |
| `QUEUE_GAUGE` | Sum | `num_requests_waiting` |
| `CACHE_METRIC` | Mean | `kv_cache_usage_perc` |
| `HOTSPOT_RESOURCE_GAUGE` | Max | `kv_cache_usage_perc_max` |
| `METADATA_GAUGE` | Passthrough | `process_max_fds`、所有 `motor:*` 指标 |
| `HISTOGRAM_LATENCY` | Histogram Merge | `e2e_request_latency_seconds` 等 |
| `SLA_METRIC` | Histogram Merge + 分位数 | `time_to_first_token_seconds` 等 |
| `RATIO_NUMERATOR` / `RATIO_DENOMINATOR` | Sum | `prefix_cache_hits_total` / `queries_total` |

**解读**：这是整个子系统最具巧思的部分——把"指标语义"显式建模，取代散落的 if/else。例如 `STATE_GAUGE` 与 `HOTSPOT_RESOURCE_GAUGE` 表面都是 gauge，但前者（请求运行数）跨实例累加才有意义，后者（KV cache 使用率最大值）取 max 才能反映系统瓶颈；`CACHE_METRIC` 用 Mean 是因为各实例 KV 占用率取均值才反映集群平均水位。`RATIO_NUMERATOR/RATIO_DENOMINATOR` 的拆分设计让派生比率（如 `prefix_cache_hit_rate = hits / queries`）只需在 `post_process` 阶段做一次除法，避免在每个采集周期重新扫描 metric 名。

### 表 3：五种指标视图

| 视图 | `type=` 参数 | 聚合范围 | 注入标签 | 用途 |
|------|-------------|---------|---------|------|
| `full` | 默认 | SERVICE（集群级） | — | Prometheus 抓取 |
| `instance` | `instance` | INSTANCE | `instance_id`、`role` | 单实例排障 |
| `role` | `role` | ROLE | `role` | Prefill vs Decode 对比 |
| `dp` | `dp` | 无聚合（per-endpoint） | `dp_rank`、`role`、`instance_id`、`pod_ip` | 细粒度排障 |
| `node` | `node` | NODE | `pod_ip`、`role` | 节点级监控 |

**解读**：五视图设计服务于不同监控主体——`full` 给全局告警/大盘；`role` 给 PD 分离架构下两类引擎的性能对比（这是 LLM 推理常见分析维度）；`dp` 给 SRE 定位具体数据并行 rank 的问题；`node` 给硬件层（结合 pod_ip 对应物理节点）。值得注意的是 `dp` 视图"无聚合（per-endpoint）"——意味着它绕过聚合引擎直接透出原始样本，这是细粒度排障所必需；其余 4 个视图则都进入聚合流水线。

### 表 4：内置计算指标注册表（节选，原文标注共 6 个）

| name | phase | compute_type | source_counters / role_filter |
|------|-------|--------------|------------------------------|
| `motor:prompt_tokens_per_second` | `pre_aggregation` | `counter_rate` | source_counters=`["vllm:prompt_tokens_total"]`, role_filter=None |
| `motor:generation_tokens_per_second` | `pre_aggregation` | `counter_rate` | source_counters=`["vllm:generation_tokens_total"]`, role_filter=None |
| `motor:active_prefill_workers` | `post_aggregation` | `worker_count` | role_filter=`["prefill"]` |
| …其余省略 | … | … | … |

**解读**：所有 `counter_rate` 类型指标统一在 DP 级注入，是为了确保 TPS 反映"单个 DP rank 的真实产出速率"（否则跨 rank 求和后再算速率就失去意义）；`worker_count` 类型则在 Service 级注入，是集群级统计。`role_filter` 字段的出现意味着同一个 `compute_type` 可以按角色复用——例如可能存在 `motor:active_decode_workers` 与 `motor:active_prefill_workers` 共享同一计算逻辑。

---

## 【公式解读】

原文未出现标准 LaTeX 数学公式，但存在以下两类核心计算式 / 伪代码表达式，逐字保留并解读如下：

### 表达式 1：基础聚合策略（`aggregation_engine.py`）

```
Sum:       lambda a, b: a + b
Max:       lambda a, b: max(a, b)
Mean:      Sum → 除以源数量
Passthrough: 取第一个值
Histogram Merge: 合并 bucket、累加 _count / _sum，按 le 排序
```

**符号含义**：
- `a, b`：被聚合的两个样本值（来自不同 instance / endpoint）；
- `Sum` 用于累加型量（counter、状态计数），语义上"总量相加"；
- `Max` 用于热点资源（如 KV cache 占用率峰值），语义上"集群最坏情况"；
- `Mean` 中的"源数量"指参与聚合的 endpoint 个数，公式上为 `(Σ sample_i) / N`；
- `Passthrough` 保留单一权威值，避免被多实例平均稀释（如 `process_max_fds` 是进程元数据）；
- `Histogram Merge` 的 `le` 是 Prometheus bucket 的"小于等于"阈值，需排序后逐 bucket 累加。

### 表达式 2：Counter Rate 与 Baseline 偏移（TPS 计算）

```
TPS_t = (effective_counter_t − effective_counter_{t-1}) / dt

effective_counter_t = raw_counter_t + baseline_t

baseline_t = {
    0,                                      首次采集（无历史）
    effective_counter_{t-1},                检测到引擎重启（ins_id 变化 + drop > 10%）
    baseline_{t-1},                         正常运行
}

restart_detected = (instance_id_t ≠ instance_id_{t-1})  AND  (drop > 10%)
```

**符号含义**：
- `effective_counter_t`：第 t 次采集的"等效累计值"，即在重启后把 raw_counter 抬高到上一轮水平，避免 delta 出现负值；
- `raw_counter_t`：vLLM 实际暴露的原始 counter 值（引擎进程级累计）；
- `baseline_t`：偏移量，用于把"新引擎的 raw_counter"映射到"旧引擎的等效水位"；
- `dt`：相邻两次采集的时间间隔；
- `drop > 10%`：restart 检测阈值（原文明确给出 10%）；
- `(job_name, dp_rank)`：作为稳定标识贯穿重启（`job_name` 跨重启不变，`instance_id` 跨重启变化）。

**作用**：保证 vLLM 引擎重启窗口内的 TPS 计算既不出负值（避免 Prometheus rate() 函数告警），也不出虚高尖峰（避免"重启后第一帧 delta 巨大导致 TPS 跳变"）。

### 表达式 3：派生比率（`post_process` 阶段）

```
prefix_cache_hit_rate = prefix_cache_hits_total / queries_total
```

**符号含义**：
- 分子分母均来自 `RATIO_NUMERATOR` / `RATIO_DENOMINATOR` 语义类别（已在聚合阶段完成 Sum）；
- 该公式在 `post_process` 阶段执行，对每条 SERVICE 级聚合结果重算一次。

### 表达式 4：分位数派生

```
p50 / p95 / p99 = quantile(merged_histogram, [0.5, 0.95, 0.99])
mean = merged_histogram._sum / merged_histogram._count
```

**符号含义**：从 `HISTOGRAM_LATENCY` / `SLA_METRIC` 语义类别合并后的直方图直接派生分位数与均值，无需重新打点。

---

## 【关联】

文档本身未提供显式内部链接（"内部链接: (无)"），但从模块拆分、四层架构和设计动机可以推断出以下上下游关系：

1. **上游数据源**：vLLM 引擎 Pod 的 `/metrics` HTTP 端点（Prometheus 文本格式）—— `_fetch_instance_metrics()` 负责拉取。这是整个 Metrics 子系统的唯一外部数据来源。

2. **下游消费方**：
   - **Prometheus**：默认抓取 `full` 视图（SERVICE 级聚合）；
   - **OpenTelemetry Collector**：可消费 `full` 视图或按需调用其他视图；
   - **运维/SRE**：通过 `instance` / `dp` / `node` 视图做排障，通过 `role` 视图做 Prefill vs Decode 对比。

3. **横向模块耦合**：
   - **`MotorMetricComputer` 解耦 `MetricsCollector`**：原文动机明确指出，原先 `_append_coordinator_metrics()` 与新需求"DP 级 counter rate 指标"两处插入逻辑散落在 `MetricsCollector` 中，抽象出 `MotorMetricComputer` 后，新指标只需在 `_MOTOR_COMPUTED_METRICS` 列表追加 `ComputedMetricDef`，无需修改 `MetricsCollector` 任何代码——这是典型的"开闭原则"应用。
   - **`metric_registry` 驱动 `aggregation_engine`**：语义注册表是声明式配置层，聚合引擎是执行层，二者通过 `MetricSemantic` 解耦——新增 vLLM 指标只需在注册表映射，无需改聚合策略。

4. **上下文依赖**：`AggregationContext` 字段中的 `deploy_mode`（部署模式）与 `instance_roles`（实例角色）表明本子系统依赖更上层的部署配置/服务发现模块来确定实例角色（prefill / decode / mixed），这与 PD 分离（Prefill-Decode Disaggregation）架构强相关。

5. **PD 分离架构的隐性体现**：文档多处提到 prefill / decode 角色（如 `motor:active_prefill_workers` 的 `role_filter=["prefill"]`、TTFT 的 `role_scope="decode"`），说明该 Metrics 设计与 MindIE Motor 的 PD 分离推理部署模式深度耦合。

---

## 【使用方法】

> 原文末尾"How to add a custom Motor computed metric"小节被截断（停在 "**Step 2：在 `metric_registry.py"），因此新增指标的完整配置步骤仅有 Step 1 可见。

### 启用方式

- **默认抓取**：Prometheus 抓取 Coordinator 的 `full` 视图端点即可，无需指定 `type=` 参数（默认即 SERVICE 级聚合）。
- **视图切换**：通过 HTTP 查询参数 `type=instance|role|dp|node` 切换不同聚合视图，详见上文"五种指标视图"表格。

### 配置项（系统级，源自 `AggregationContext`）

- **`scope`**：决定聚合范围（`INSTANCE` / `ROLE` / `NODE` / `SERVICE`）。
- **`instance_roles`**：限定参与聚合的角色集合（prefill / decode / mixed）。
- **`deploy_mode`**：当前部署模式，影响聚合策略。
- **`ins_ids`**：目标实例 ID 列表。

### 新增 Motor 计算指标的步骤（原文 Step 1 + Step 2 截断）

**Step 1：在 `_MOTOR_COMPUTED_METRICS` 注册表中添加定义**

编辑 `motor/coordinator/metrics/metric_computer.py`，在 `_MOTOR_COMPUTED_METRICS` 列表中添加一条 `ComputedMetricDef`：

```python
ComputedMetricDef(
    name="motor:new_tokens_per_second",
    help="New tokens per second computed from vllm:new_tokens_total counter deltas",
    phase="pre_aggregation",
    compute_type="counter_rate",
    source_counters=["vllm:new_tokens_total"],
    role_filter=None,
),
```

**Step 2：在 `metric_registry.py…`** —— 原文在此处被截断，未涉及。

### 原文中明确给出的关键参数 / 阈值

| 参数 / 阈值 | 值 | 出处 |
|------------|-----|------|
| 重启检测 — `instance_id` 变化 | 必要条件 | "重启检测双重判断" |
| 重启检测 — `raw_counter` 下降比例 | `> 10%` | "drop > 10%" |
| DP 级 counter rate 稳定标识 | `(job_name, dp_rank)` | "Counter Rate 重启容错设计" |
| 视图数量 | 5 种（`full / instance / role / dp / node`） | "五种指标视图" |
| 语义类别数量 | 10 类 | "metric_registry.py" 表 |
| 内置计算指标数量 | 共 6 个（原文明确写"共 6 个"，仅展示 3 个） | `_MOTOR_COMPUTED_METRICS` 注册表说明 |
| 直方图派生分位数 | `p50 / p95 / p99` | `post_process` 阶段 |
| 派生比率示例 | `prefix_cache_hit_rate = hits / queries` | `post_process` 阶段 |
