# 【B050】LLM推理监控平台设计文档

> 仓 `msserviceprofiler` · 路径 `docs/design/ms_service_metric_Monitoring_Metrics_Design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msserviceprofiler/docs/design/ms_service_metric_Monitoring_Metrics_Design.md

# 深度解读：ms-service-metric LLM 推理监控指标设计文档

---

## 【定位】

本文档是 msserviceprofiler 中 `ms-service-metric` 组件在 vLLM-Ascend 服务化推理场景下的**监控指标增强设计文档**，对应需求【B050】LLM推理监控平台，目标是在 vLLM 原生 `/metrics` 基础上，补齐细粒度执行阶段拆分、EPLB 特性观测、异常状态统计和多维标签（dp/role/phase）能力，并以 Prometheus 格式对外暴露数据。

---

## 【技术要点】

1. **轻量 hook + Prometheus 暴露架构**：`ms-service-metric` 在 vLLM 启动时初始化适配器，加载 `v1_metrics.yaml`，由 `SymbolHandlerManager` 将 handler 挂载到目标函数，采集结果写入 `MetricsManager`，统一注册到 vLLM 的 Prometheus registry 并加 `vllm_profiling_` 前缀，最终通过 vLLM 自身的 `/metrics` 端口对外暴露。

2. **两类 handler 机制**：
   - `wrap handler`：包裹原函数，适合前后计时和异常捕获。
   - `context handler`：可访问函数局部变量，适合复杂上下文抽取。

3. **三类本轮新增指标**（分别对应三个 PR）：
   - PR `!339` 异常状态监控：3 个 Counter（`running_to_waiting_count_total`、`block_allocate_failures_total`、`rpc_errors_total`）。
   - PR `!345` EPLB 与细粒度时延：EPLB 热度 5 个指标（`current_mean/max`、`update_mean/max`、`imbalance`）+ 4 个搬运耗时指标（`expert_weight_update/map_update/log2phy_map_update/expert_weight_replace:duration`）+ 3 个 NPU 阶段指标（`forward_duration`、`kernel_launch`、`non_forward_duration`）。
   - PR `!353` phase 维度增强：使 Worker/Executor/EngineCore 指标可按 `prefill/decode/mixed` 维度观测。

4. **标签自动注入机制**：`MetricsManager` 自动补齐 `dp`（来自进程 rank）、`role`、`phase`（来自 `meta_state` 或调用栈推断）三个标签，其中 `dp` 来自进程 rank，`role/phase` 来自 `meta_state` 或调用栈推断；`phase` 增强还补充了从 `scheduler_output` 推断 phase 的能力，以降低线程/进程隔离导致的 phase 丢失。

5. **多进程聚合**：通过 `PROMETHEUS_MULTIPROC_DIR` 和 vLLM 的 Prometheus registry 将多进程指标汇聚到同一 `/metrics` 暴露面。

6. **异常监控 hook 点位**：`Scheduler._preempt_request`（统计 running 回退 waiting 同时累计 `scheduler:recompute_events`）、`KVCacheManager.allocate_slots`（既覆盖返回失败对象也覆盖直接抛异常）、`MultiprocExecutor.collective_rpc`（仅记录实际 Python 异常类型，不虚构 reason 字段）。

---

## 【关键机制与数据】

**工作原理**（原文："metrics 的核心原理可以概括为'在运行时找到目标函数，在函数执行前后拿到上下文，再把结果写入 Prometheus 指标对象'"）：

- **配置驱动**：配置文件路径为 `ms_service_metric/adapters/vllm/config/v1_metrics.yaml`，描述要 hook 的 symbol、版本边界、handler 或 metric 配置。
- **启动时序**（原文 sequenceDiagram）：启动阶段完成 hook 挂载 → Runtime Caller 调用目标函数 → 进入 wrap/context handler → 提取 args/locals/duration/exception → 正常路径下 `record_metric(name, value, labels)` 后注入 dp/role/phase 并更新 Histogram/Counter/Gauge → 异常路径下 `record_metric(error_metric, 1, labels)` 后继续抛出原始异常。
- **完整数据链路**（原文 text）：
  ```
  vLLM / vLLM-Ascend Runtime
    -> ms-service-metric adapter initialize
    -> load YAML symbol config
    -> hook target function with handler
    -> record metric into MetricsManager
    -> register into vLLM prometheus registry
    -> expose from /metrics
    -> optional Prometheus scrape
    -> optional visualization / alert tools
  ```

**EPLB 热度与搬运采集点位**（原文 §3.2.2）：
- `EplbWorker.do_update` → 采集 rank0 暴露的热度聚合结果和 layer 级 imbalance。
- `D2DExpertWeightLoader.update_expert_map_and_weight` → 专家权重更新耗时。
- `VllmEplbAdaptor.do_update_expert_map` → expert map 更新耗时。
- `VllmEplbAdaptor.do_update_log2phy_map` → log2phy map 更新耗时。
- `VllmEplbAdaptor.do_update_expert_weight` → 专家权重替换耗时。

**NPU 阶段时延语义**（原文）：
- `forward_duration`："更贴近算子主执行阶段"。
- `kernel_launch`："反映从 forward 到 post process 之间的执行跨度"。
- `non_forward_duration`："用于观察不属于 forward 本体的额外耗时，更适合暴露 CPU 波动、调度衔接、后处理等影响"。

**性能/容量数据**：原文未提供具体的性能数据（如 QPS 提升、延迟下降百分比等），所有数字均以指标名称和分类呈现，无量化基准。

---

## 【表格解读】

原文无显式 markdown 表格。以下按指标族逐字还原**指标清单表**（摘自原文 §3.2 各小节），并逐行解读：

### 表 A：PR !339 异常状态监控指标

| 指标名称 | 标签 | 类型 | 含义 |
|---|---|---|---|
| `vllm_profiling_running_to_waiting_count_total` | dp, role, phase | Counter（累计型 _total） | running 请求回退 waiting 的次数，可视为 pending 请求回退/积压风险观测信号 |
| `vllm_profiling_block_allocate_failures_total` | dp, role, phase | Counter | KV cache block 分配失败次数 |
| `vllm_profiling_rpc_errors_total` | dp, role, phase, exception_type | Counter | driver 到 worker 的 RPC 异常次数，按 Python 异常类型聚合 |

逐行解读：
- **第 1 行** Counter 后缀 `_total` 符合 Prometheus 命名习惯；标签三维度用于按 DP 域/角色/阶段拆分；其语义在 §3.2.1 中明确为"pending 请求回退/积压风险的一类观测信号"，并**同时累计** `scheduler:recompute_events` 反映重计算触发。
- **第 2 行** 仅三标签维度，没有 `exception_type`，因为 block 分配失败的异常类型在原文未细分。
- **第 3 行** 额外 `exception_type` 标签"有助于按异常类别做聚合，但不会引入不受控的高基数字段"——是设计上对基数（cardinality）的明确约束。
- **总体设计取向**（原文）："该类指标优先强调'是否发生'和'发生频率'，而非耗时分布"。

### 表 B：PR !345 EPLB 热度与失衡指标

| 指标名称 | 标签 | 采集点位 |
|---|---|---|
| `eplb:expert_hotness:current_mean` | — | EplbWorker.do_update（rank0） |
| `eplb:expert_hotness:current_max` | — | EplbWorker.do_update（rank0） |
| `eplb:expert_hotness:update_mean` | — | EplbWorker.do_update（rank0） |
| `eplb:expert_hotness:update_max` | — | EplbWorker.do_update（rank0） |
| `eplb:expert_hotness:imbalance` | rank, phase, layer | EplbWorker.do_update |

逐行解读：
- **current_* vs update_***：原文未显式区分二者语义，但从命名推断 current 为当前快照、update 为本轮更新后的结果，原文仅说明"采集 rank0 暴露的热度聚合结果和 layer 级 imbalance"。
- **imbalance 标签含 `layer`**：体现 layer 级细粒度失衡定位能力；`rank` 标签暗示多 rank 部署下的横向对比；`phase` 与全局 phase 标签语义一致。
- **采集约束**：这 5 个指标均仅在 rank0 采集，说明 EPLB 热度本身是全局共享状态，无需每个 rank 重复上报。

### 表 C：PR !345 专家搬运耗时指标

| 指标名称 | 采集函数 |
|---|---|
| `eplb:expert_weight_update:duration` | D2DExpertWeightLoader.update_expert_map_and_weight |
| `eplb:expert_map_update:duration` | VllmEplbAdaptor.do_update_expert_map |
| `eplb:log2phy_map_update:duration` | VllmEplbAdaptor.do_update_log2phy_map |
| `eplb:expert_weight_replace:duration` | VllmEplbAdaptor.do_update_expert_weight |

逐行解读：
- 这 4 个指标均为 `*:duration` 后缀，类型应为 Histogram（原文 §3.1.2 中提到映射到 Prometheus 的 `Histogram/Counter/Gauge`）。
- **逻辑关系**：原文中第 1 个指标（`expert_weight_update`）来自 D2DExpertWeightLoader，第 2/3/4 个指标来自 VllmEplbAdaptor，说明专家搬运链路拆为 D2D 整体 + Adaptor 内三段（map 更新 / log2phy 映射 / 权重替换），可独立观测瓶颈。

### 表 D：PR !345 NPU 细粒度阶段时延指标

| 指标名称 | 语义（原文） |
|---|---|
| `npu:forward_duration` | 更贴近算子主执行阶段 |
| `npu:kernel_launch` | 反映从 forward 到 post process 之间的执行跨度 |
| `npu:non_forward_duration` | 观察不属于 forward 本体的额外耗时（CPU 波动、调度衔接、后处理） |

逐行解读：
- 三个指标构成 forward 阶段的拆分视图：`forward_duration` 是算子主时间，`kernel_launch` 是 forward 到 post process 之间的衔接，`non_forward_duration` 是 forward 之外的额外开销，三者配合可区分"算子慢"还是"调度/后处理慢"。
- 原文 §1.2 中将这一能力的目标描述为"区分算子执行、CPU 抖动、调度等待、sample 阶段等不同耗时来源"。

### 表 E：PR !353 phase 增强可拆分观测的细粒度指标

| 指标名称 | 来源侧 |
|---|---|
| `prepare input` | Worker（record_function hook） |
| `forward` | Worker |
| `post process` | Worker |
| `sample_token` | Worker |
| `draft_token` | Worker |
| `executor:execute_model:duration` | Executor |
| `executor:sample_tokens:duration` | Executor |

逐行解读：
- 原文明确："该增强并不单独创造一批全新业务指标"，即这些指标在 PR !353 之前已存在，本轮主要是补齐 phase 标签的稳定传递能力。
- Worker 侧通过 `record_function_or_nullcontext` 携带 phase 标签；Executor/EngineCore 侧 handler 继承或推断 phase；Adapter 初始化阶段补齐 `pd_role` 设置。

---

## 【公式解读】

原文无公式。所有"指标计算"均通过 Prometheus 内置 Histogram/Counter/Gauge 类型表达（如 `duration` 后缀指标隐含为 Histogram 分桶），但文档未给出具体的桶边界（bucket boundary）、分位点（quantile）或聚合公式。

---

## 【关联】

**与上游/下游模块的关联**：

- **vLLM-Ascend**：作为运行时底座，`ms-service-metric` 通过其原生 `/metrics` 端口暴露指标，文档明确"不重复定义 vLLM 原生已经稳定提供的全部基础指标，仅说明与本平台集成关系"。
- **vLLM 原生 Prometheus registry**：所有平台新增指标共享其 registry，并自动加上 `vllm_profiling_` 前缀。
- **Prometheus**：作为外部 scraper 抓取 `/metrics`（可选）。
- **Grafana / 告警系统**：作为可视化和告警下游（可选）；`mean/max/min/last` 等统计"主要基于 Prometheus 查询和 panel reducer 得到，不要求每个统计值都单独定义一个 metric"。
- **PR 链路**：本文档对应三个 PR 的增量合集——`!339`（异常状态）、`!345`（EPLB + 细粒度时延）、`!353`（phase 维度）。

**内部链接**：原文未提供任何内部链接 URL（"内部链接: (无)"）。

---

## 【使用方法】

原文涉及的启用/配置方式如下：

- **配置文件路径**：`ms_service_metric/adapters/vllm/config/v1_metrics.yaml`，描述要 hook 的 symbol、版本边界、handler 或 metric 配置（原文 §3.1.2）。
- **环境变量**：`PROMETHEUS_MULTIPROC_DIR`，用于多进程指标汇聚到同一 `/metrics` 暴露面（原文 §3.1.2）。
- **适配器初始化**：vLLM 启动时由 `ms-service-metric` 自动初始化适配器，加载 YAML 并完成 hook 挂载，无需业务侧手动介入（原文 §3.1.1）。
- **兼容性约束**：原文 §2 提及"通过 YAML 配置和版本约束适配不同 vLLM / vLLM-Ascend 版本"，但未给出具体的版本号约束。
- **指标端点**：vLLM 自有 `/metrics` 端口（原文 §3.1.1）。
- **指标前缀**：所有平台新增指标统一以 `vllm_profiling_` 为前缀（原文 §3.1.2）。
- **可视化**：可选接入 Prometheus 抓取 + Grafana 展示（原文 §3.1.1）。

**未涉及项**：原文未提供具体的 Grafana dashboard JSON 路径、Prometheus 抓取配置示例、告警规则定义或命令行启动参数。原文 §1.3 中也明确将"Prometheus、Grafana 本身的部署、运维和看板交付"列为非目标。
