# 实例扩缩容设计文档

> 仓 `mindie-motor` · 路径 `docs/zh/design/scaling.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/design/scaling.md

# MindIE Motor 实例扩缩容设计文档 — 一体化深度解读

---

## 【定位】

本文档阐述 MindIE Motor 推理集群管理框架中 **Prefill / Decode 推理实例的两种扩缩容机制** —— 基于 K8s HPA 的自动弹性扩缩容（负载自适应）与基于 ConfigMap 基线的手动扩缩容（人工决策），解决"如何在 PD 分离推理架构中安全、可预期地调整实例副本数并兼顾 SLA 与资源利用率"的问题。

---

## 【技术要点】

1. **两种互补的扩缩容语义**：自动扩缩容（负载自适应，HPA 驱动） + 手动扩缩容（人工决策，确定性增量变更），共同覆盖波动负载与计划性变更两类运维场景。
2. **指标聚合与决策解耦**：Motor Coordinator 仅负责采集 / 聚合 / 暴露 Prometheus 指标，不参与扩缩容决策；扩缩容完全交由 K8s 标准 HPA 完成，可复用稳定窗口、冷却、最保守决策等成熟语义。
3. **三类指标聚合视图**：`/metrics` 端点支持 `full`（默认全局聚合）/ `instance`（实例级）/ `role`（按 Prefill/Decode 聚合），通过 `type` query 参数切换，匹配不同扩缩容粒度。
4. **PD 分离的差异化指标推荐**：Prefill（计算密集）侧关注 `vllm:num_requests_waiting`、`vllm:kv_cache_usage_perc`、`motor:prompt_tokens_per_second`、`vllm:time_to_first_token_seconds`；Decode（访存密集）侧关注 `motor:generation_tokens_per_second`、`vllm:e2e_request_latency_seconds`、`vllm:time_per_output_token_seconds`。
5. **手动扩缩容六大设计原则**：以集群 ConfigMap `motor-config` 为唯一基线、仅允许修改实例数字段、增量式调整（扩容仅创建高 index 实例 / 缩容逆序删除）、部署模式自适应（InferServiceSet / multi_deployment）、成功即刷新基线、前置校验（整数 + 1~16 范围）。
6. **scalingPolicy 配置约束**：`type` 当前仅支持 `HPA`；`minReplicas` ≥ 1；`maxReplicas` ≥ `minReplicas`；依赖 MindCluster Infer Operator 版本 ≥ 26.1.0 与 External Metrics Adaptor。

---

## 【关键机制与数据】

### 1. 自动扩缩容数据流（原文 1.2 工作原理）

```
HPA (autoscaler) ──> Infer Operator ──> Engine Pods (Prefill/Decode)
   ^                                         │
   │                                         │ /metrics
   │                                         ▼
   └─── External Metrics API <── MindIE Motor Coordinator (aggregation/TPS)
```

工作步骤（原文逐条）：
1. Coordinator 从所有引擎 Pod 采集 Prometheus 指标，按语义聚合后通过 `:1027/metrics` 端点暴露。
2. External Metrics Adaptor 周期性从 Coordinator 拉取指标，转换为 Kubernetes External Metrics API。
3. HPA 从 External Metrics API 获取负载数据，与用户配置的目标阈值对比。
4. 当指标持续超出阈值时，HPA 通知 Infer Operator 增加副本；低于阈值时减少副本。

### 2. 手动扩缩容核心机制（原文 2.2 设计思路）

- **基线锚点**：每次部署把 `user_config` 持久化为 ConfigMap `motor-config`，扩缩容以集群内基线与当前输入做对比，避免多客户端配置漂移；集群中不存在基线时拒绝扩缩容。
- **单一变更维度**：仅允许修改 `p_instances_num` / `d_instances_num` / `hybrid_instances_num`，其余配置必须与基线完全一致，其余变更走全量重新部署路径。
- **增量式调整**：扩容仅创建高 index 新实例（不重拉存量、不滚动重启）；缩容从最大 index 逆序删除并清理对应部署产物。
- **部署模式自适应**：扩缩容路径的部署模式取自集群基线而非本地输入；`InferServiceSet` 模式直接更新角色 replicas，`multi_deployment` 模式按引擎类型逐个增量 apply / delete。
- **成功即收敛**：每次成功的扩缩容都把 user_config 写回 ConfigMap，成为下一次操作基线。
- **前置校验**：实例数必须为正整数且不超过 16，校验在触碰集群前完成。

### 3. 关键设计考虑（原文 1.5）

- **扩缩容范围**：仅作用于 Prefill / Decode 实例；Router 不参与扩缩容。
- **缩容稳定窗口**：HPA 默认 5 分钟，避免负载短暂波动导致频繁扩缩（原文）。
- **新实例性能预热**：扩容新实例无 KV Cache 缓存，Prefix Cache 逐步重建，存在性能小幅度劣化。
- **Adaptor 依赖链路**：Adaptor 异常会导致 HPA 无法获取指标，扩缩容失效。
- **缩容下限建议**：`minReplicas` 至少为 1，避免缩容到 0 导致服务完全不可用。
- **角色独立扩缩容**：默认 `/metrics` 返回 `full` 全局聚合；按 Prefill/Decode 独立扩缩时 Adaptor 需分别请求 `/metrics?type=role&role=prefill` 与 `/metrics?type=role&role=decode`。

### 4. 性能 / 数据相关（原文无具体性能数字）

原文未给出实测 TPS、扩缩容时延、扩容耗时等具体性能数据，仅给出推荐阈值（如下表解读）。

---

## 【表格解读】

### 表 1 — `/metrics` 端点 `type` 参数聚合视图

| type 值 | 说明 | 适用场景 |
|---------|------|---------|
| `full`（默认） | 全局聚合，所有实例指标聚合为单一值 | Prometheus 抓取、HPA 全局扩缩容 |
| `instance` | 实例级指标，注入 `instance_id`、`role` 标签 | 单实例排障 |
| `role` | 按角色（Prefill / Decode）聚合 | 按角色独立扩缩容 |

**逐行解读**：
- `full`（默认）：所有 Prefill 与 Decode 实例的同指标聚合成单一数值，HPA 用此值做全局决策时简单直接；但无法区分角色负载差异。
- `instance`：每个引擎 Pod 单独暴露指标，附带 `instance_id` 与 `role` 标签，用于单实例问题定位（排障），不适合直接驱动 HPA。
- `role`：按角色分别聚合，适配 PD 分离架构 —— Prefill 与 Decode 选用不同扩缩容指标与阈值时，必须使用此视图。

---

### 表 2 — Prefill 扩缩容推荐指标

| 指标名 | 类型 | 说明 | 推荐阈值建议 |
|--------|------|------|-------------|
| `vllm:num_requests_waiting` | Gauge | 等待调度的请求数 | > 5 触发扩容，< 2 触发缩容 |
| `vllm:num_requests_running` | Gauge | 当前运行中的请求数 | 视 NPU 规格和模型而定 |
| `vllm:kv_cache_usage_perc` | Gauge | KV Cache 使用率（0-1） | > 0.8 触发扩容 |
| `motor:prompt_tokens_per_second` | Gauge | Prompt token 处理速率（Motor 计算） | 按 SLA 目标设定 |
| `vllm:time_to_first_token_seconds` | Histogram | 首 token 延迟（TTFT） | 按 SLA 目标（如 p95 < 500ms） |

**逐行解读**：
- `vllm:num_requests_waiting`：排队请求数是最直接的负载信号，原文给出明确数值阈值（> 5 扩容、< 2 缩容）；Gauge 类型可直接读取。
- `vllm:num_requests_running`：运行中请求数受 NPU 规格与模型差异显著，原文未给出固定阈值，留给用户自行调优。
- `vllm:kv_cache_usage_perc`：0~1 区间的 KV Cache 使用率，0.8 是经验阈值；Gauge 类型可直接用作 HPA External Metric。
- `motor:prompt_tokens_per_second`：由 Coordinator 计算的服务级 Gauge（基于 vLLM counter delta rate），比原始 counter 更准确反映实时吞吐。
- `vllm:time_to_first_token_seconds`：Histogram 类型，需在 Adaptor 侧计算 p50/p95/p99 后作为独立指标暴露，原文示例阈值 p95 < 500ms。

---

### 表 3 — Decode 扩缩容推荐指标

| 指标名 | 类型 | 说明 | 推荐阈值建议 |
|--------|------|------|-------------|
| `vllm:num_requests_waiting` | Gauge | 等待调度的请求数 | > 5 触发扩容 |
| `vllm:num_requests_running` | Gauge | 当前运行中的请求数 | 视 NPU 规格和模型而定 |
| `motor:generation_tokens_per_second` | Gauge | 生成 token 速率（Motor 计算） | 按 SLA 目标设定 |
| `vllm:e2e_request_latency_seconds` | Histogram | 端到端请求延迟 | 按 SLA 目标（如 p95 < 2s） |
| `vllm:time_per_output_token_seconds` | Histogram | 跨 token 延迟（TPOT） | 按 SLA 目标（如 p95 < 50ms） |

**逐行解读**：
- `vllm:num_requests_waiting`：与 Prefill 共用基础排队指标，原文仅给出扩容阈值（> 5），未单独列出缩容阈值。
- `vllm:num_requests_running`：Decode 实例常并发处理多个 decode 请求，运行中请求数与 Prefill 语义不同，仍需按 NPU/模型调优。
- `motor:generation_tokens_per_second`：Decode 侧的核心吞吐指标，由 Coordinator 计算，反映实时生成速率；适用于"按 SLA 目标设吞吐阈值"的扩缩策略。
- `vllm:e2e_request_latency_seconds`：Histogram 类型，原文示例阈值 p95 < 2s，需 Adaptor 侧做分位聚合。
- `vllm:time_per_output_token_seconds`：TPOT（Time Per Output Token），Histogram 类型，原文示例阈值 p95 < 50ms，是衡量 Decode 流式输出流畅度的关键指标。

---

### 表 4 — `scalingPolicy` 参数说明

| 参数 | 说明 | 取值 |
|------|------|------|
| `scalingPolicy.type` | 弹性扩缩容策略类型 | 当前仅支持 `HPA` |
| `scalingPolicy.spec.minReplicas` | 缩容下限，实例数不会低于此值 | 正整数 |
| `scalingPolicy.spec.maxReplicas` | 扩容上限，实例数不会超过此值 | 正整数，且 ≥ minReplicas |
| `scalingPolicy.spec.metrics[].type` | 指标类型 | `External`（由 External Metrics Adaptor 提供） |
| `scalingPolicy.spec.metrics[].external.metric.name` | 外部指标名称 | 需与 Adaptor 暴露的指标名一致 |
| `scalingPolicy.spec.metrics[].external.target.type` | 目标值类型 | `AverageValue`（Pod 平均值） |
| `scalingPolicy.spec.metrics[].external.target.averageValue` | 目标平均值阈值 | 按指标量纲设定 |

**逐行解读**：
- `type`：当前实现仅暴露 HPA 一种扩缩容类型，未预留 Custom 控制器扩展点。
- `minReplicas` / `maxReplicas`：硬性上下界，原文强调建议 `minReplicas ≥ 1`，避免服务完全不可用。
- `metrics[].type`：必须是 `External`，因为 Motor 指标经 Adaptor 转换为 K8s External Metrics API 暴露，不在 Pod 内 Metrics API 范围内。
- `metric.name`：必须与 Adaptor 实际暴露的指标名一致 —— Adaptor 可能对原始 Prometheus 指标名（如 `vllm:num_requests_waiting`）做映射或重命名，需以 `kubectl get --raw /apis/external.metrics.k8s.io/v1beta1` 实际返回为准。
- `target.type`：当前仅支持 `AverageValue`（Pod 平均值），未涉及 Value / Utilization 等其他 target 类型。
- `target.averageValue`：按指标量纲设定，数值含义因指标类型而异（如 `num_requests_waiting` 为请求个数、`kv_cache_usage_perc` 为 0~1 比例）。

---

## 【公式解读】

**原文无公式。**

文档未涉及数学公式或伪代码公式；扩缩容阈值均为经验配置值（> 5、< 2、0.8、p95 < 500ms 等），HPA 内部的副本数计算由 K8s 标准控制器完成，本文未展开。

---

## 【关联】

本文档作为 MindIE Motor 扩缩容机制的 design 入口，与以下模块 / 文档紧密耦合：

- **[`./metrics.md`](./metrics.md)**：自动扩缩容依赖 Coordinator `/metrics` 端点暴露的引擎级聚合指标，metrics 文档定义了指标的语义、命名空间（`vllm:` / `motor:`）、Gauge vs Histogram 区分；扩缩容文档是 metrics 的"消费者"之一，引用了 `motor:prompt_tokens_per_second`、`motor:generation_tokens_per_second` 等 Motor 计算的服务级指标。
- **[`../user_guide/api/metrics_interfaces.md`](../user_guide/api/metrics_interfaces.md)**：用户 / 运维通过该 API 文档了解如何调用 `/metrics` 端点（`?type=full` / `instance` / `role` 参数）、如何解释指标；与扩缩容文档中 §1.3.1 "指标聚合视图"直接对应，是扩缩容落地的接口层参考。
- **[`../user_guide/features/manual_scaling.md`](../user_guide/features/manual_scaling.md)**：本文档 §2 手动扩缩容设计是 user guide 中 manual_scaling 特性的设计侧描述；user guide 提供 CLI 命令、操作步骤、示例，本文提供"集群基线 / 增量式调整 / 成功即收敛"等设计语义；二者构成"设计 ↔ 使用"的闭环。

依赖链路（不在内部链接中但文中明确提及）：
- **Infer Operator**（MindCluster Infer Operator ≥ 26.1.0）：负责创建 / 调整 Engine Pods（Prefill / Decode），是 HPA 调整副本的执行端。
- **External Metrics Adaptor**：将 Motor 的 Prometheus 指标转换为 K8s External Metrics API，是 HPA 与 Motor 之间的桥梁；其部署与配置正确性直接决定扩缩容可用性。
- **Router / Controller / Coordinator**：明确不在扩缩容路径中 —— 自动扩缩容作用于 Prefill / Decode；手动扩缩容只调整 Prefill / Decode 实例数。

---

## 【使用方法】

### 自动扩缩容启用（原文 1.4）

1. **前置部署**：部署 Infer Operator（≥ 26.1.0）与 External Metrics Adaptor；Adaptor 需正确配置 Coordinator 地址。
2. **修改 `infer_service_template.yaml`**：在 Prefill 与 Decode 角色配置块下添加 `scalingPolicy` 字段：

```yaml
roles:
  - name: prefill
    replicas: 4
    workload:
      apiVersion: apps/v1
      kind: StatefulSet
    scalingPolicy:
      type: HPA
      spec:
        minReplicas: 1
        maxReplicas: 4
        metrics:
        - type: External
          external:
            metric:
              name: vllm:num_requests_waiting
            target:
              type: AverageValue
              averageValue: "5"
    metadata:
      labels:
        infer.huawei.com/gang-schedule: 'true'
    spec:
      # ... 其余配置保持不变 ...
  - name: decode
    replicas: 4
    workload:
      apiVersion: apps/v1
      kind: StatefulSet
    scalingPolicy:
      type: HPA
      spec:
        minReplicas: 1
        maxReplicas: 4
        metrics:
        - type: External
          external:
            metric:
              name: motor:generation_tokens_per_second
            target:
              type: AverageValue
              averageValue: "10"
    metadata:
      labels:
        infer.huawei.com/gang-schedule: 'true'
    spec:
      # ... 其余配置保持不变 ...
```

3. **验证 Adaptor 暴露的指标名**：

```bash
kubectl get --raw /apis/external.metrics.k8s.io/v1beta1 | grep -E "vllm:|motor:"
```

若 Adaptor 暴露的指标名与模板示例不同，以实际返回值为准。

### 手动扩缩容启用（原文 §2）

- 原文 §2.2 描述了**设计机制**（基线 ConfigMap `motor-config`、增量调整、前置校验），但**具体的 CLI 命令、操作步骤、调用方式**不在本文档范围内，详见 `../user_guide/features/manual_scaling.md`。
- 实例数约束（原文）：必须为正整数，范围 1~16，超出则在触碰集群前快速失败。

### 指标查询（原文 1.3.1）

```bash
# 全局聚合指标（默认）
curl http://{coordinator-ip}:1027/metrics

# 按角色分别查看
curl http://{coordinator-ip}:1027/metrics?type=role&role=prefill
curl http://{coordinator-ip}:1027/metrics?type=role&role=decode
```

### 多指标组合策略示例（原文 1.3.3）

```yaml
scalingPolicy:
  type: HPA
  spec:
    minReplicas: 1
    maxReplicas: 4
    metrics:
    - type: External
      external:
        metric:
          name: num_requests_waiting
        target:
          type: AverageValue
          averageValue: "5"
    - type: External
      external:
        metric:
          name: kv_cache_usage_perc
        target:
          type: AverageValue
          averageValue: "0.8"
```

HPA 在多指标下取**最保守的扩缩容决策**（当前副本数最接近触发扩容或缩容的指标）。
