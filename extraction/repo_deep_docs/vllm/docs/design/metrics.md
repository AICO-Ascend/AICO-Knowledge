# Metrics

> 仓 `vllm` · 路径 `docs/design/metrics.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/metrics.md

# 设计文档深度解读：vLLM Metrics 设计

## 【定位】

这篇文档系统性地阐述了 vLLM V1 引擎的可观测性指标（Metrics）体系：从指标分类、`/metrics` 端点规范、Grafana 仪表盘参考、Prometheus 客户端演进、多进程采集模式权衡，到 V1 引擎中指标采集点的架构重定位（从 EngineCore 迁至前端 API Server），为生产监控、SLO 跟踪与容量规划提供统一、可落地的设计契约。

---

## 【技术要点】

1. **指标按粒度分层（Server-level vs Request-level）**：Server-level 用 Gauge/Counter 表征引擎全局状态（如 `num_requests_running` Gauge、`prefix_cache_hits` Counter）；Request-level 用 Histogram 表征单个请求的延迟与规模分布，二者关系是"server-level 解释 request-level 的取值范围"。
2. **`/metrics` 端点 + `vllm:` 命名空间前缀**：V1 通过 Prometheus 兼容端点暴露 14 类核心指标，覆盖请求计数（`num_requests_running`、`request_success_total`）、KV 缓存水位（`kv_cache_usage_perc` 取值 0–1）、前缀缓存命中（`prefix_cache_queries` / `prefix_cache_hits`）、token 处理总量（`prompt_tokens_total` / `generation_tokens_total`）以及 5 类延迟直方图（`time_to_first_token_seconds`、`inter_token_latency_seconds`、`e2e_request_latency_seconds`、`request_prefill_time_seconds`、`request_decode_time_seconds`）。
3. **Grafana 仪表盘是"指标重要性"的隐式优先级清单**：文档明确指出，"Grafana 仪表盘中暴露的指标子集"代表特别重要的核心 SLO，包括 TTFT、TPOT、E2E 延迟、prompt/generation token 长度、请求各阶段耗时（队列/prefill/decode）以及最大生成长度 `request_max_num_generation_tokens`。
4. **HTTP 层指标通过 `prometheus_fastapi_instrumentator` 接入**：示例 `curl http://0.0.0.0:8000/metrics` 输出 `http_requests_total{handler="/v1/completions",method="POST",status="2xx"} 201.0`，对应 handler `/v1/completions`，含请求/响应字节计数与高分辨率延迟桶，弥补早期 `MetricsMiddleware` 迁移过程中的能力空缺。
5. **多进程模式与采集点演进的两次重大重构**：
   - 历史方案：引擎核心进程采集 + 多进程模式聚合到 API server；
   - 当前方案：API Server 进程内直接采集，仅当 `--api-server-count > 1` 时使用多进程模式；
   - 副作用：`--api-server-count > 1` 时，`prometheus_client` 内置的 10 个 Python/进程级指标（`python_gc_objects_collected_total`、`process_virtual_memory_bytes`、`process_cpu_seconds_total` 等）不可用，因它们无法跨进程聚合。
6. **V1 指标采集架构原则——把开销从 EngineCore 移出**：EngineCore 是性能关键的内层循环，前向计算间不容许额外开销；AsyncLLM.outer loop 与 GPU 执行重叠，是容纳度量的理想位置。基于 `EngineCoreOutputs` 在前端 API Server 端做指标簿记是 V1 的具体落点。

---

## 【关键机制与数据】

### 数据流与采集原理

- **V1 双进程架构下的指标采集路径**（原文：Metrics Collection 章节）：EngineCore 内层循环专注于前向推理；AsyncLLM 作为外层循环与 GPU 执行重叠，是承担"开销"的最佳位置；`AsyncLLM.output_handler_loop` 是指标簿记（metrics bookkeeping）的理想投放点。最终实现在前端 API server 中采集，依赖从 `EngineCoreOutputs` 中可推断的状态信息作为数据源。

- **时间间隔计算的正确性约束**（原文：Interval Calculations 章节）：
  - 必须用 `time.monotonic()` 而非 `time.time()`，因为单调时钟不受 NTP 等系统时钟跳变影响；
  - 关键陷阱：单调时钟**每个进程有独立参考点**，跨进程比较单调时间戳是无意义的；
  - 因此，**计算一个时间间隔，必须使用同一进程采集的两个时间戳**——这是 API Server 进程内采集模型成立的正确性前提之一。

### 性能/规模数据

- 原文未给出独立的性能基准数字；
- HTTP 指标样例值（原文 Prometheus Client Library 章节）：以 `http_requests_total{handler="/v1/completions",method="POST",status="2xx"} 201.0` 为代表，"201.0"代表已完成的 2xx 状态请求计数，并非性能数据。

### 关键约束

- 原文（Multi-process Mode 章节）：`--api-server-count > 1` 时，`prometheus_client` 内置的 Python/进程级指标无法对外暴露，"对这些指标是否能代表 vLLM 实例的整体状态存疑"，原文表述为 "It's questionable how relevant these are since they do not aggregate these stats for all processes that make up a vLLM instance."

---

## 【表格解读】

**原文无表格。**

原文中所有指标均以项目符号列表形式呈现，未提供参数表、性能对比表或配置矩阵。但 V1 Metrics 章节与 Grafana Dashboard 章节实质上是两个并列的"指标清单"——前者给出完整端点暴露集合（含类型标签 Gauge/Counter/Histogram），后者是仪表盘优先子集。如下是基于原文逐字保留的两个清单（**非原文表格**，仅为忠实归集解读）：

**清单 A — V1 Metrics（按 Prometheus 类型分组，逐字保留）**

| 类型 | 指标名 | 原文语义 |
|---|---|---|
| Gauge | `vllm:num_requests_running` | Number of requests currently running. |
| Gauge | `vllm:kv_cache_usage_perc` | Fraction of used KV cache blocks (0–1). |
| Counter | `vllm:prefix_cache_queries` | Number of prefix cache queries. |
| Counter | `vllm:prefix_cache_hits` | Number of prefix cache hits. |
| Counter | `vllm:prompt_tokens_total` | Total number of prompt tokens processed. |
| Counter | `vllm:generation_tokens_total` | Total number of generated tokens. |
| Counter | `vllm:request_success_total` | Number of finished requests (by finish reason). |
| Histogram | `vllm:request_prompt_tokens` | Histogram of input prompt token counts. |
| Histogram | `vllm:request_generation_tokens` | Histogram of generation token counts. |
| Histogram | `vllm:time_to_first_token_seconds` | Time to first token (TTFT). |
| Histogram | `vllm:inter_token_latency_seconds` | Inter-token latency. |
| Histogram | `vllm:e2e_request_latency_seconds` | End-to-end request latency. |
| Histogram | `vllm:request_prefill_time_seconds` | Request prefill time. |
| Histogram | `vllm:request_decode_time_seconds` | Request decode time. |

**解读**：14 个核心指标分两类用途——6 个**系统状态面**指标（运行中请求数、KV 利用率、前缀缓存命中率、token 吞吐、请求成功率）覆盖容量规划核心信号；8 个**延迟与规模分布面**指标（5 个延迟直方图 + 2 个 token 长度直方图 + 1 个请求成功计数）则是 SRE 直接用于 SLO 跟踪的对象。

**清单 B — Grafana Dashboard 强调指标（原文为项目符号，未指定类型，含义原文照录）**

| 指标名 | 原文语义 |
|---|---|
| `vllm:e2e_request_latency_seconds_bucket` | End to end request latency measured in seconds. |
| `vllm:prompt_tokens` | Prompt tokens. |
| `vllm:generation_tokens` | Generation tokens. |
| `vllm:inter_token_latency_seconds` | Inter-token latency (Time Per Output Token, TPOT) in seconds. |
| `vllm:time_to_first_token_seconds` | Time to First Token (TTFT) latency in seconds. |
| `vllm:num_requests_running`（含 `_swapped` 与 `_waiting`） | Number of requests in the RUNNING, WAITING, and SWAPPED states. |
| `vllm:kv_cache_usage_perc` | Percentage of used cache blocks by vLLM. |
| `vllm:request_prompt_tokens` | Request prompt length. |
| `vllm:request_generation_tokens` | Request generation length. |
| `vllm:request_success` | Number of finished requests by their finish reason: either an EOS token was generated or the max sequence length was reached. |
| `vllm:request_queue_time_seconds` | Queue time. |
| `vllm:request_prefill_time_seconds` | Requests prefill time. |
| `vllm:request_decode_time_seconds` | Requests decode time. |
| `vllm:request_max_num_generation_tokens` | Max generation tokens in a sequence group. |

**解读**：相比清单 A，清单 B 多了**队列时间**（`request_queue_time_seconds`）和**单 sequence group 最大生成 token 数**（`request_max_num_generation_tokens`）两个未在 V1 Metrics 章节显式列出的指标；同时 `num_requests_running` 扩展出 `_swapped` / `_waiting` 两个标签维度对应调度器三态，反映仪表盘视角下对**调度器内部状态**的关注；`request_success` 进一步定性说明 finish reason 为 EOS 或达到 max sequence length。

---

## 【公式解读】

**原文无公式。**

文档未呈现数学公式或伪代码形式的时间/吞吐计算式。仅有**与时间相关的文字性约束**值得作为"准公式"保留并解读：

- **间隔计算正确性原则**（原文逐字保留）：
  > "It is best practice to use timestamps based on 'monotonic time' (`time.monotonic()`) rather than 'wall-clock time' (`time.time()`) to calculate intervals as the former is unaffected by system clock changes (e.g. from NTP)."

  含义：设 $\Delta t = t_{\text{end}} - t_{\text{start}}$，其中 $t$ 必须采自同一进程的 `time.monotonic()`，不可与 `time.time()` 混用，亦不可跨进程比较。文档明确说明"monotonic clocks differ between processes - each process has its own reference point. So it is meaningless to compare monotonic timestamps from different processes."

- **单进程约束的工程后果**：该原则**反推**了 V1 选型——指标必须采集自同一进程才能计算延迟，从而支撑了"指标簿记放在前端 API Server 进程内"的架构决定。

---

## 【关联】

文档通过文末链接与仓库内多个上下游模块建立关系：

- **[Inferencing and Serving → Production Metrics](../usage/metrics.md)**：用户侧文档，给出 V1 指标对外的正式解释与使用说明，是本文档"理论性 Metrics 设计"的落地视图。
- **Grafana 参考示例 ([prometheus_grafana/README.md](../../examples/observability/prometheus_grafana/README.md))**：本文档定义的指标子集在仪表盘中的渲染范例，链接至此示例以演示如何采集、存储与可视化。
- **OpenTelemetry 示例 ([opentelemetry/README.md](../../examples/observability/opentelemetry/README.md))**：与 Prometheus 并行的另一类可观测性后端集成示例，体现 vLLM 的多后端兼容性。
- **API server scale-out ([data_parallel_deployment.md#internal-load-balancing](../serving/data_parallel_deployment.md#internal-load-balancing))**：直接对应"多进程模式"章节中"metrics are collected in the API server process and multiprocess mode is only used when `--api-server-count > 1`"的部署场景；数据并行部署涉及多 API Server 实例的负载均衡，与多进程指标聚合的可行性紧密耦合。
- **PR #7279 讨论 ([gh-pr:7279#discussion_r1710417152](gh-pr:7279#discussion_r1710417152))**：历史上"engine core 进程 + 多进程聚合到 API server"的旧采集模型出处，文档明确"See <https://github.com/vllm-project/vllm/pull/7279>"；关联讨论可解释旧模型的设计动机与局限。
- **Deprecation policy ([../contributing/deprecation_policy.md](../contributing/deprecation_policy.md))**：为 Metrics Design → Legacy PRs 章节铺垫——原 metrics 体系经历多次迭代（PR #1890 → PR #2316 → PR #2730 → PR #4464 → PR #7279），旧指标若标记为 deprecated，其移除路径由该政策约束。
- **V1 实施的 11 个 PR**（[Metrics Implementation PRs](https://github.com/vllm-project/vllm/issues/10582) 下列出的 #11962、#11973、#10907、#12416、#12478、#12516、#12530、#12561、#12579、#12592、#12644）：与文档的 "Metrics Collection / Interval Calculations / Scheduler Stats" 等技术章节一一对应，是 V1 指标架构的代码层实现索引。

整体上，文档是 V1 Metrics 体系的**"设计宪法"**，向上指引用户文档与监控样例，向下追溯到实现 PR 与历史演进。

---

## 【使用方法】

**启用方式 / 命令**（原文直接给出）：

1. **指标端点查询**：
   ```bash
   $ curl http://0.0.0.0:8000/metrics 2>/dev/null  | grep -P '^http_(?!.*(_bucket|_created|_sum)).*'
   ```
   该命令抓取所有 `http_` 前缀、非桶/非 created/非 sum 的聚合指标（如 `http_requests_total`、`http_request_size_bytes_count`、`http_request_duration_highr_seconds_count` 等）。

2. **V1 指标默认通过 Prometheus 兼容 `/metrics` 端点暴露，使用 `vllm:` 命名空间前缀**。

3. **多进程采集相关的运行选项**：当使用 `--api-server-count > 1` 时启用多进程模式；此时 `prometheus_client` 内置的 10 个 Python/进程级指标（`python_gc_objects_collected_total`、`python_gc_objects_uncollectable_total`、`python_gc_collections_total`、`python_info`、`process_virtual_memory_bytes`、`process_resident_memory_bytes`、`process_start_time_seconds`、`process_cpu_seconds_total`、`process_open_fds`、`process_max_fds`）不可用，原文明确将其标为"unavailable when `--api-server-count > 1`"。

4. **部署参考**：API Server 横向扩展场景参见 [data_parallel_deployment.md#internal-load-balancing](../serving/data_parallel_deployment.md#internal-load-balancing)；监控栈搭建参考 [prometheus_grafana/README.md](../../examples/observability/prometheus_grafana/README.md)；其他后端集成参见 [opentelemetry/README.md](../../examples/observability/opentelemetry/README.md)。

**关于"启用/禁用具体某指标"的开关、采集粒度配置、采样频率等参数**：**原文未涉及**。文档未出现显式的 metrics 启用/禁用配置项或采集周期参数。

> **注**：原文档末尾在 "Scheduler Stats" 一节以 "The engine core process will" 截断，本解读严格基于已存在的原文内容，未对未给出的机制（如 Scheduler Stats 的具体形态、Stats 字段含义）做任何臆测或补充。

## 图文联合解读

- `intervals-1.png`: 1) 图示请求在 API Server（橙）与 Engine Core（红）间的时序事件，右侧大括号划分 Queue→Prefill→Inference/Decode 三阶段；左侧标 TTFT，token 间标 ITL。

2) 无抢占下请求生命周期分三阶段；TTFT 涵盖排队+Prefill，ITL 刻画 Decode 节奏，二者构成核心请求级 SLO。

3) 文档强调请求级 Histogram 是 SRE 追踪的 SLO，本图给出 TTFT/ITL 的物理定义，支撑"server-level 解释 request-level"的心智模型。
- `intervals-2.png`: **图示解读：**

**1）图的内容：** 标题为"Intervals - preempted decode"的时序图，分两列展示一个请求的全生命周期——左列API Server（橙色）：ARRIVED → ITERATION（含TTFT首token时延区间）；右列Engine Core（红色）：QUEUED→SCHEDULED→FIRST_TOKEN→NEW_TOKEN→**PREEMPTED**→SCHEDULED→NEW_TOKEN→LAST_TOKEN。右侧括号标注阶段分组：Queue、Prefill、ITL、ITL Decode、Inference。

**2）技术结论：** 该图刻画了请求被抢占解码场景下各关键时间区间的起止边界，证明TTFT（首token时延）和ITL（token间隔时延）作为直方图指标可跨越"被抢占+重新调度"事件被持续、正确地分段度量。

**3）与文档关系：** 支撑文档论点"Server-level metrics解释request-level metrics"中的请求级直方图指标（Histogram型SLO）能在异常调度路径下仍保持可观测性，从而服务生产监控与容量规划。
- `intervals-3.png`: 1) 图示"被抢占的 prefill"间隔：左侧 API Server(ARRIVED→ITERATION)与右侧 Engine Core(QUEUED→SCHEDULED→PREEMPTED→SCHEDULED→FIRST_TOKEN→NEW_TOKEN→LAST_TOKEN)的双轨状态流，标注 TTFT(贯穿整个排队/抢占/重调度)与 ITL(各 decode 迭代)。

2) 论证：请求级时延指标 TTFT/ITL 跨越多个调度周期，被抢占后仍重计，反映 vLLM 请求级 Histogram 指标的真实计时语义。

3) 呼应文档论点：解释为何请求级直方图是关键 SLO，且 TTFT 含排队与抢占开销，需配合 server-level 指标共同观测。
