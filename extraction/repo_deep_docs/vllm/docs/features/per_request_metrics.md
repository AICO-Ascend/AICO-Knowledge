# Per-Request Metrics

> 仓 `vllm` · 路径 `docs/features/per_request_metrics.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/per_request_metrics.md

# Per-Request Metrics 文档一体化深度解读

## 【定位】

这篇文档描述 vLLM 在 **API 响应体（per-request 级别）内直接返回单请求时序/吞吐指标** 的能力，作为对 `/metrics` 端点上 Prometheus 服务端聚合指标的补充，用于计费、SLA 监控与延迟分析。

## 【技术要点】

1. **启用开关**：服务端通过 `--enable-per-request-metrics` 启动；例如 `vllm serve meta-llama/Llama-3.1-8B-Instruct --enable-per-request-metrics`。
2. **响应注入位置**：在 OpenAI 兼容响应里追加 `metrics` 对象，与 `usage`（`prompt_tokens`/`completion_tokens`/`total_tokens`）并列。
3. **指标字段集**：`time_to_first_token_ms`（TTFT）、`generation_time_ms`（纯 decode 时间）、`queue_time_ms`（排队等待时间）、`mean_itl_ms`（decode 阶段平均相邻 token 间延迟，单 token 响应为 `null`）、`tokens_per_second`（从调度到最后 token 的端到端吞吐，含 prefill）。
4. **适用性约束**：仅当请求映射到**单一生成流**（`n == 1`）时返回；`n > 1` 或多个 prompt 时 `metrics` 为 `null`，但 token usage 仍准确。
5. **服务端依赖**：需开启 stats 日志（默认开启）；若同时设置 `--disable-log-stats`，vLLM 会**拒绝** `--enable-per-request-metrics`。
6. **Streaming 接收方式**：流式响应中指标附着在最后一个 usage chunk；客户端需设 `stream_options={"include_usage": True}`，或服务端加 `--enable-force-include-usage` 强制下发。
7. **代价提示**：原文 note 提示——在高并发下启用可能引入"non-negligible CPU overhead"，生产部署前需针对具体负载 benchmark。
8. **拓展能力**：启用 `--per-request-spec-decode-metrics` 时，`metrics.speculative_decoding` 子对象返回平均接受长度与 accepted-draft-length 分布，同样仅在 `n == 1` 时上报。

## 【关键机制与数据】

- **工作机制**：服务端在请求被调度、首 token 生成、末 token 生成等节点上埋点计时，汇总后随响应返回；流式场景则延迟到最终 usage chunk 一次性下发。
- **与 Prometheus 关系**：`metrics` 是**单请求粒度**，`/metrics` 端点暴露**服务端聚合**直方图（如 `vllm:time_to_first_token_seconds`）。二者数据来源相同但粒度不同，前者用于精细诊断，后者用于全局监控。
- **时序分段定义（原文语义）**：
  - TTFT = 调度时刻 → 首个输出 token；
  - generation_time = 首个输出 token → 末个输出 token（**不含**排队与 prefill/TTFT）；
  - tokens_per_second 分母为"调度→末 token"的推理全程（**包含** prefill），故反映端到端生成速度而非纯 decode 速度。
- **示例数值（原文 JSON 样本，非实测承诺）**：`time_to_first_token_ms=85.2`、`generation_time_ms=1240.5`、`queue_time_ms=12.3`、`mean_itl_ms=9.1`、`tokens_per_second=103.2`；对应 `prompt_tokens=42`、`completion_tokens=128`、`total_tokens=170`。

## 【表格解读】

逐字还原原文表格：

| Field | Description |
| --- | --- |
| `time_to_first_token_ms` | Time from when the request was scheduled until the first output token was generated (TTFT). |
| `generation_time_ms` | Decode time: time from the first output token to the last output token. Excludes both queue wait and prefill/TTFT. |
| `queue_time_ms` | Time the request spent waiting in the scheduler queue before processing began. |
| `mean_itl_ms` | Mean inter-token latency (average time between successive output tokens) during the decode phase. `null` for single-token responses. |
| `tokens_per_second` | Overall output token throughput: all generated tokens over the inference interval (scheduling to last output token). Unlike `generation_time_ms`, this includes the prefill phase, so it reflects end-to-end generation speed rather than pure decode speed. |

逐行解读：

- **`time_to_first_token_ms`（TTFT）**：从请求被调度器接受处理开始，到生成第一个输出 token 的耗时——衡量"用户感知的首字延迟"，对交互式体验最关键。
- **`generation_time_ms`**：纯 decode 阶段时长（首 token → 末 token），**排除**排队等待和 prefill/TTFT，专门反映解码吞吐；当关注 decode 阶段本身的成本或加速收益（如 speculative decoding）时使用。
- **`queue_time_ms`**：请求在 scheduler 队列中等待处理的时间——用于衡量调度拥塞与 batching 策略对尾延迟的影响。
- **`mean_itl_ms`**：decode 阶段相邻 token 的平均间隔；单 token 响应因没有"相邻对"被置为 `null`，需特别处理避免被误解析为 0。
- **`tokens_per_second`**：端到端吞吐（所有生成 token 数 ÷ 从调度到最后 token 的总推理时间），**包含** prefill；与 `generation_time_ms` 不同之处在于分母是否含 TTFT/prefill，因此更接近"该请求在系统中的整体生成速度"。

## 【公式解读】

原文无公式。

## 【关联】

- **服务端聚合指标 `/metrics`（Prometheus）**：本文 `metrics` 是其单请求粒度的镜像/补充；同源直方图变量如 `vllm:time_to_first_token_seconds` 在文档中明确点名。
- **Speculative Decoding（推测解码）**：通过 `--per-request-spec-decode-metrics` 启用后，在同一 `metrics` 对象下挂载 `speculative_decoding` 子字段（平均接受长度、accepted-draft-length 分布），同样受 `n == 1` 单序列约束。详见文档末尾内部链接 [Per-Request Acceptance Metrics](speculative_decoding/acceptance_metrics.md)。
- **OpenAI 兼容 `/v1/chat/completions` 与 `/v1/completions`**：两个端点都支持 `metrics` 字段；`/v1/completions` 上对"多 prompt 请求"同样抑制 metrics（与 `n > 1` 行为一致）。
- **Streaming usage 链路**：依赖 `stream_options.include_usage`（客户端）或 `--enable-force-include-usage`（服务端）把指标注入最终 usage chunk；与 OpenAI 兼容流的 usage chunk 机制绑定。
- **Server stats logging（默认开启）**：是 per-request metrics 的隐含依赖，与 `--disable-log-stats` 互斥。

## 【使用方法】

- **服务端启用**：
  ```bash
  vllm serve meta-llama/Llama-3.1-8B-Instruct --enable-per-request-metrics
  ```
  - 不要同时使用 `--disable-log-stats`，否则 vLLM 会拒绝启动该组合。
- **非流式请求示例（Python OpenAI 客户端）**：访问 `response.model_extra.get("metrics")` 读取 `metrics` 对象；`response.usage` 读取 token 用量。
- **流式请求示例**：
  - 客户端：调用时设 `stream=True, stream_options={"include_usage": True}`；遍历 chunk，找到 `chunk.usage` 非空的最终 chunk，从中取 `chunk.model_extra.get("metrics")`。
  - 服务端强制（替代客户端配置）：`--enable-force-include-usage`。
- **响应字段读取**：`time_to_first_token_ms`、`generation_time_ms`、`queue_time_ms`、`mean_itl_ms`、`tokens_per_second`；注意 `mean_itl_ms` 对单 token 响应为 `null`，所有字段在底层计时不可用时也为 `null`。
- **推测解码扩展指标**：
  ```bash
  vllm serve ... --enable-per-request-metrics --per-request-spec-decode-metrics
  ```
  启用后从 `metrics.speculative_decoding` 读取平均接受长度与 accepted-draft-length 分布（仅 `n == 1` 请求生效，详见 [Per-Request Acceptance Metrics](speculative_decoding/acceptance_metrics.md)）。
- **生产前评估**：原文 note 建议高并发场景先 benchmark CPU 开销影响再启用。
