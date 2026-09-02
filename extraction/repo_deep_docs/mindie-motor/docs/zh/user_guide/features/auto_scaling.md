# 自动弹性扩缩容

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/features/auto_scaling.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/features/auto_scaling.md

# 自动弹性扩缩容文档深度解读

## 【定位】

这篇文档描述 MindIE Motor 在 Kubernetes 上基于 HPA（Horizontal Pod Autoscaler）+ External Metrics Adaptor 的自动弹性扩缩容能力，即根据 Prefill/Decode 推理实例的实时负载指标动态调整副本数，以兼顾服务可用性与资源利用率。

---

## 【技术要点】

1. **核心控制环路**：Infer Operator 为推理实例创建 HPA 资源 → HPA 通过 External Metrics Adaptor 从 MindIE Motor Coordinator 拉取引擎级聚合指标（排队请求数、TPS、KV Cache 使用率等）→ 与用户配置的扩缩容阈值对比 → 超阈值扩容、低于阈值缩容。
2. **Metrics 聚合视图**：`Coordinator /metrics` 端点支持三种 `type` —— `full`（默认，全局聚合）、`instance`（注入 `instance_id`/`role` 标签）、`role`（按 Prefill/Decode 独立聚合）。
3. **配置位置**：在 `examples/deployer/yaml_template/infer_service_template.yaml` 的每个 role 块下新增 `scalingPolicy` 字段，原文示例中 Prefill 副本 1–4、指标 `vllm:num_requests_waiting` 阈值 `5`；Decode 副本 1–4、指标 `motor:generation_tokens_per_second` 阈值 `10`。
4. **缩容稳定窗口**：`--horizontal-pod-autoscaler-downscale-stabilization` 默认 **5 分钟**，原文示例中验证缩容观察数分钟。
5. **多指标策略**：HPA 选取**最保守**的决策（即"当前副本数最接近触发扩/缩容的指标"），原文给出 `vllm:num_requests_waiting=5` + `vllm:kv_cache_usage_perc=0.8` 组合示例。
6. **依赖与版本**：本特性依赖 MindCluster Infer Operator **≥ 26.1.0**；Adaptor 可直接使用 `mindcluster-deploy` 仓库 `infer-operator-metrics-adaptor` 目录示例部署。

---

## 【关键机制与数据】

### 工作原理（原文四步流程）

1. MindIE Motor Coordinator 从所有引擎 Pod 采集 Prometheus 指标，按语义聚合后通过 `/metrics` 端点暴露。
2. External Metrics Adaptor 周期性从 Coordinator 拉取指标，转换为 Kubernetes External Metrics API。
3. HPA 从 External Metrics API 获取负载数据，与用户配置的目标阈值对比。
4. 当指标持续超出阈值时，HPA 通知 Infer Operator 增加副本；低于阈值时减少副本。

### 架构拓扑（原文 ASCII 图要点）

> 原文:`HPA (autoscaler)` → `Infer Operator` → `Engine Pods (Prefill / Decode)`；同时 `Engine Pods` 通过 `/metrics` 上报 → `MindIE Motor Coordinator (aggregation/TPS)` → 由 External Metrics Adaptor 通过 **External Metrics API** 反向喂给 HPA。

### 关键数据/参数（原文显式给出）

- Coordinator metrics 端口：`1027`（原文:`http://{coordinator-ip}:1027/metrics`）。
- 缩容稳定窗口：默认 **5 分钟**（原文:`--horizontal-pod-autoscaler-downscale-stabilization`）。
- HPA 验证回显示例（原文）:`TARGETS` 列形如 `3/5`、`8/10`，含义为"当前值/目标值"。
- SLA 目标示例（推荐阈值列）:TTFT `p95 < 500ms`、E2E `p95 < 2s`、TPOT `p95 < 50ms`、KV Cache 使用率 `> 0.8` 触发扩容、排队请求 `> 5` 扩容 / `< 2` 缩容。
- 服务端口（负载测试示例）:`{service-ip}:31015/v1/chat/completions`。
- 支持型号:Atlas 800I A2 推理服务器、Atlas 800I A3 超节点服务器。

> 注：原文"注意事项"段末尾在 `若使用不带 type 参数的 /metrics` 处截断，最后一条注意事项未给出完整结论。

---

## 【表格解读】

### 表 1：Coordinator `/metrics` 端点 `type` 参数（原文逐字还原）

| type 值 | 说明 | 适用场景 |
|---------|------|---------|
| `full`（默认） | 全局聚合，所有实例指标聚合为单一值 | Prometheus 抓取、HPA 全局扩缩容 |
| `instance` | 实例级指标，注入 `instance_id`、`role` 标签 | 单实例排障 |
| `role` | 按角色（Prefill / Decode）聚合 | 按角色独立扩缩容 |

**逐行解读**：
- `full`（默认）—— 将所有实例的同一指标合并为一个聚合值，最适合作为 HPA 全局扩缩容的输入，因为 HPA 的 `AverageValue` 目标值是"Pod 平均值"，全局聚合避免了多实例分别上报带来的重复计数。
- `instance` —— 每个实例打上 `instance_id` 和 `role` 标签，可用于排查某个具体 Pod 的异常，但不适合直接作为 HPA 指标（HPA 会按 Pod 取平均）。
- `role` —— 仅按 Prefill / Decode 维度聚合，用于"按角色独立扩缩容"场景，对应本文档主推的用法（Prefill 与 Decode 用不同指标、不同阈值）。

### 表 2：scalingPolicy 参数说明（原文逐字还原）

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
- `type` —— 字段为未来扩展留口子，目前实现仅 `HPA`，与 Kubernetes 原生 HPA 语义对齐。
- `minReplicas` / `maxReplicas` —— 上下界构成扩缩容可行域；原文注意事项明确建议 `minReplicas ≥ 1`，避免缩到 0 导致服务不可用。
- `metrics[].type` —— `External` 表示该指标经由 External Metrics Adaptor 接入，需提前部署 Adaptor 并确认其暴露的指标名（可执行 `kubectl get --raw /apis/external.metrics.k8s.io/v1beta1 | grep -E "vllm:|motor:"` 核实）。
- `target.type` —— `AverageValue` 是 K8s HPA 的 Pod 平均值模式，Coordinator `/metrics?type=full` 的全局聚合最贴合此语义。
- `target.averageValue` —— 阈值必须与指标量纲一致：排队请求数用整数（如 `"5"`），KV Cache 使用率用 `[0,1]`（如 `"0.8"`），TPS 用每秒 token 数。

### 表 3：Prefill 扩缩容推荐指标（原文逐字还原）

| 指标名 | 类型 | 说明 | 推荐阈值建议 |
|--------|------|------|-------------|
| `vllm:num_requests_waiting` | Gauge | 等待调度的请求数 | > 5 触发扩容，< 2 触发缩容 |
| `vllm:num_requests_running` | Gauge | 当前运行中的请求数 | 视 NPU 规格和模型而定 |
| `vllm:kv_cache_usage_perc` | Gauge | KV Cache 使用率（0-1） | > 0.8 触发扩容 |
| `motor:prompt_tokens_per_second` | Gauge | Prompt token 处理速率（Motor 计算） | 按 SLA 目标设定 |
| `vllm:time_to_first_token_seconds` | Histogram | 首 token 延迟（TTFT） | 按 SLA 目标（如 p95 < 500ms） |

**逐行解读**：
- 排队请求数最直观反映"积压"，给出扩容/缩容双向阈值避免震荡。
- 运行中请求数受并发上限约束，需结合具体 NPU 规格与模型并发能力评估。
- KV Cache 使用率是 Prefill 显存压力的直接信号，超过 0.8 必须扩容以防止 OOM。
- `motor:prompt_tokens_per_second` 由 Coordinator 基于 vLLM counter 的 delta rate 计算（参见下文 Histogram 说明），比原始 counter 更准确反映吞吐。
- TTFT 是 Prefill 阶段核心 SLA 指标；Histogram 类型需 Adaptor 侧计算分位数后作为独立指标暴露。

### 表 4：Decode 扩缩容推荐指标（原文逐字还原）

| 指标名 | 类型 | 说明 | 推荐阈值建议 |
|--------|------|------|-------------|
| `vllm:num_requests_waiting` | Gauge | 等待调度的请求数 | > 5 触发扩容 |
| `vllm:num_requests_running` | Gauge | 当前运行中的请求数 | 视 NPU 规格和模型而定 |
| `motor:generation_tokens_per_second` | Gauge | 生成 token 速率（Motor 计算） | 按 SLA 目标设定 |
| `vllm:e2e_request_latency_seconds` | Histogram | 端到端请求延迟 | 按 SLA 目标（如 p95 < 2s） |
| `vllm:time_per_output_token_seconds` | Histogram | 跨 token 延迟（TPOT） | 按 SLA 目标（如 p95 < 50ms） |

**逐行解读**：
- 排队与运行中请求数与 Prefill 共享，但语义偏向 Decode 侧请求积压。
- `motor:generation_tokens_per_second` 是 Decode 吞吐代理指标，原文 Prefill/Decode 配置示例均以此指标建阈。
- E2E 延迟体现用户感知，TPOT 体现单 token 流式输出的平稳度，二者构成 Decode 核心 SLA。
- 注意事项明确：Prefill 为计算密集型、Decode 为访存密集型，应分别配置不同指标体系。

---

## 【公式解读】

**原文无公式**。

> 说明：原文档未出现 LaTeX 数学式或伪代码公式。可形式化描述的逻辑关系只有"当前值 > 阈值 → 扩容 / 当前值 < 阈值 → 缩容"这一 HPA 通则，但原文未给出数学表达。

---

## 【关联】

### 文档内显式引用的上下游链接

- **`../../design/metrics.md`**（设计文档，metrics 设计）—— 本特性的指标语义、聚合规则、命名约定（如 `vllm:num_requests_waiting`、`motor:generation_tokens_per_second`）应由该设计文档定义，是 `/metrics` 端点行为的源头。
- **`../api/metrics_interfaces.md`**（API 接口，metrics 接口）—— 提供 Coordinator `/metrics` 端点的接口契约（端口 1027、`type` 参数、`role` 参数），本特性通过该接口与 Adaptor 解耦。

### 与仓内其他特性/模块的关系

- **Infer Operator（MindCluster）**：本特性由其在 K8s 侧拉起 HPA 与 StatefulSet 副本；版本约束 **≥ 26.1.0**，部署示例来自 `mindcluster-deploy/infer-operator-metrics-adaptor`。
- **External Metrics Adaptor**：作为 Prometheus ↔ K8s External Metrics API 的桥梁；Adaptor 异常时 HPA 将无法取数，原文已显式提醒。
- **PD 分离 / PD 混部**：前置条件之一是已部署 Prefill-Decode 模式推理服务；Router **不参与**扩缩容。
- **Prefix Cache**：注意事项指出新扩容实例无 KV Cache，需逐步重建缓存，短期内推理性能可能小幅劣化。
- **推荐指标中 Histogram 处理**：依赖 Adaptor 侧将 p50/p95/p99 分位数独立暴露才能用于扩缩容——这是与 Adaptor 实现的隐含契约。

---

## 【使用方法】

### 1. 前置条件

- 已完成 Infer Operator 安装部署；
- 已完成 MindIE Motor 推理服务部署（PD 分离或 PD 混部）；
- 已部署 External Metrics Adaptor，可使用 [`mindcluster-deploy/infer-operator-metrics-adaptor`](https://gitcode.com/Ascend/mindcluster-deploy/tree/master/infer-operator-metrics-adaptor) 示例。

### 2. 确认 Coordinator 暴露 Metrics

Coordinator 默认通过 `/metrics` 端点暴露聚合指标，**无需额外配置**：

```bash
curl http://{coordinator-ip}:1027/metrics                  # 全局聚合（默认）
curl http://{coordinator-ip}:1027/metrics?type=role&role=prefill
curl http://{coordinator-ip}:1027/metrics?type=role&role=decode
```

### 3. 验证 Adaptor 可用

```bash
kubectl get --raw /apis/external.metrics.k8s.io/v1beta1 | grep -E "num_requests_waiting|motor:generation_tokens_per_second"
```

> 实际指标名以 Adaptor 暴露为准（Adaptor 可能对 Prometheus 名做映射），可通过 `kubectl get --raw /apis/external.metrics.k8s.io/v1beta1 | grep -E "vllm:|motor:"` 列出。

### 4. 在 `infer_service_template.yaml` 中声明 `scalingPolicy`

原文给出 Prefill（指标 `vllm:num_requests_waiting`，阈值 `"5"`）与 Decode（指标 `motor:generation_tokens_per_second`，阈值 `"10"`）两个示例，均为 `minReplicas: 1, maxReplicas: 4`。也支持在 `metrics:` 列表下叠加多条指标，HPA 取最保守决策（如 `vllm:num_requests_waiting=5` + `vllm:kv_cache_usage_perc=0.8`）。

### 5. 验证与压测

```bash
kubectl get hpa -n {namespace}
kubectl get hpa -n {namespace} --watch
kubectl get pod  -n {namespace} | grep -E "prefill|decode"
```

模拟负载：

```bash
for i in {1..100}; do
  curl -X POST "http://{service-ip}:31015/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d '{"model":"your-model","max_tokens":100,"messages":[{"role":"user","content":"Hello"}]}' &
done
```

停负载后观察 **5 分钟**缩容窗口，确认副本回落至 `minReplicas`。

### 6. 关键注意事项（原文摘要）

- HPA 仅作用于 Prefill/Decode；Router 不参与扩缩容。
- 缩容默认 **5 分钟**稳定窗口，避免抖动。
- 新扩容实例**无 KV Cache**，Prefix Cache 需重建，短期性能可能下降。
- `minReplicas ≥ 1`，避免缩到 0。
- 优先使用 Gauge 或 Motor 计算的 TPS 指标；Counter 类指标**不会因 `/metrics` 请求重置**。
- 原文最后一条注意事项（关于"不带 `type` 参数的 `/metrics`"用法）在文档中**被截断**，原文未涉及完整结论。
