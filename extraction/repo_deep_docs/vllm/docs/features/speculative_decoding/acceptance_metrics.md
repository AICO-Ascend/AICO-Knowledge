# Per-Request Acceptance Metrics

> 仓 `vllm` · 路径 `docs/features/speculative_decoding/acceptance_metrics.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/speculative_decoding/acceptance_metrics.md

# vLLM Per-Request Acceptance Metrics 文档深度解读

---

## 【定位】

这篇文档定义并描述了 vLLM 在启用 speculative decoding（推测解码）时，针对**单次请求级别**返回的 acceptance metrics（接受度指标）的能力——使客户端能够在 OpenAI 兼容的响应体 `metrics.speculative_decoding` 字段中获取本次请求的 mean acceptance length 与 accepted-draft-length 分布，作为对 `/metrics` 端点服务器聚合指标的单请求细粒度补充。

---

## 【技术要点】

1. **三级采样开关 `--per-request-spec-decode-metrics`**：`none`（默认，不采集）、`summary`（采集汇总指标）、`detailed`（汇总 + 每步有序数组）。原文明确 "Collection is gated at the source: with `none`, nothing is accumulated." 即在源头处分流避免无谓开销。
2. **指标载体位置**：与 timing 字段同级，挂载在响应体顶层 `metrics.speculative_decoding` 对象下；仅在 `n == 1`（单序列请求）时返回，`n > 1` 时为 `null`，因为指标语义是"描述一条生成流"。
3. **核心字段定义（summary）**：包含 7 个字段——`mean_acceptance_length`、`draft_acceptance_rate`、`acceptance_histogram`、`num_spec_steps`、`num_accepted_draft_tokens`、`num_draft_tokens`、`num_spec_tokens`，其中 `num_spec_tokens` 即配置的 `num_speculative_tokens` (k)。
4. **直方图（dense histogram）约定**：`acceptance_histogram` 长度为 `num_spec_tokens + 1`，索引 `j` 表示"恰好接受 j 个 draft tokens 的步数"，**显式排除总是被接受的 bonus token**，且原文明示 "the sum of the histogram" 即等于 `num_spec_steps`。
5. **detailed 模式的扩展字段**：`per_step_accepted` 与 `per_step_drafted` 是两个有序数组，每步一条记录；`per_step_drafted` 记录"有效提议长度"以支持自适应推测（adaptive speculation）等可变长度 draft，无需 schema 变更。
6. **与流式响应 / Prometheus 的关系**：流式场景下 `metrics` 随最终 usage chunk 一起返回（需启用 `stream_options.include_usage: true` 或 `--enable-force-include-usage`）；按请求求和后可与 Prometheus 端 `vllm:spec_decode_*_total` 系列计数器对账，但 Prometheus 聚合包含 `n > 1` 请求，因此只有"all-`n == 1`"工作负载下两者才完全一致。
7. **实验性 API 警告**：原文带 Experimental 标记，shape 可能在未来版本变更，依赖此接口应 pin vLLM 版本。

---

## 【关键机制与数据】

**工作原理（基于原文可推导的内容）**：

- **采集时机**：服务端在 speculative decoding 流程中，每完成一次 verification step（验证步）就累加相关计数器；`none` 级别下这些累加被源码级屏蔽（"gated at the source"）。
- **bonus token 的处理**：每次 verification step 都额外产生一个被保证接受的 bonus token（这是 speculative decoding 的标准语义），它被显式纳入 `mean_acceptance_length` 的 "+1" 项，但**不计入** `acceptance_histogram` 与 `num_accepted_draft_tokens`，文档在多处字段定义中重复强调 "excluding the bonus token(s)" / "Excludes the always-accepted bonus token"。
- **结构化输出对 draft 的影响**：原文 `num_draft_tokens` 字段注明 "after subtracting drafts invalidated by structured-output constraints"——即被 structured-output 约束作废的 draft 不计入分母，避免拉低真实命中率。
- **空 draft 请求的回退行为**：当请求完全没有 draft 时（"drafted nothing"），`metrics.speculative_decoding` 仍会出现，但 histogram 为 all-zero。
- **请求示例数据（原文样例 JSON）**：当配置 `num_speculative_tokens=3` 时，观测到的样本为 `num_spec_steps=43, num_accepted_draft_tokens=10, num_draft_tokens=129, mean_acceptance_length≈1.2326, draft_acceptance_rate≈0.0775, acceptance_histogram=[39,1,0,3]`，可验算 `mean = 1 + 10/43 ≈ 1.2326`、`rate = 10/129 ≈ 0.0775`、`histogram sum = 39+1+0+3 = 43 = num_spec_steps`，与原文数学定义一致。
- **性能数据**：原文未提供吞吐/延迟基准数字（无可写的"性能数据"）。

---

## 【表格解读】

### 表 1：Level × Behavior（采集级别表）

| Level | Behavior |
| --- | --- |
| `none` (default) | No collection; responses are unchanged. |
| `summary` | Acceptance metrics per request. |
| `detailed` | `summary` plus ordered per-step arrays. |

**逐行解读**：
- `none` 是默认且零开销档位，响应体不被修改，源码层即屏蔽累加；适合不需要观测或关心开销的生产环境。
- `summary` 开启后，每次请求在 `metrics.speculative_decoding` 中输出 7 个汇总字段，是面向"想知道本次请求接受度"的典型用例。
- `detailed` 在 summary 之上额外追加 `per_step_accepted` / `per_step_drafted` 两个有序数组，能定位每一步的表现，是分析/调优阶段使用的"细粒度"档位；文档特别强调它能兼容可变长 draft 场景而无需改 schema。

### 表 2：Summary 字段说明

| Field | Description |
| --- | --- |
| `mean_acceptance_length` | Mean tokens emitted per verification step, including the bonus token: `1 + num_accepted_draft_tokens / num_spec_steps`. Ranges from `1.0` (nothing accepted) to `num_spec_tokens + 1`. |
| `draft_acceptance_rate` | Fraction of proposed draft tokens accepted: `num_accepted_draft_tokens / num_draft_tokens`. |
| `acceptance_histogram` | Dense list of length `num_spec_tokens + 1`; index `j` is the number of steps that accepted exactly `j` draft tokens. Excludes the always-accepted bonus token. |
| `num_spec_steps` | Number of verification steps for this request (the sum of the histogram). |
| `num_accepted_draft_tokens` | Total accepted draft tokens, excluding bonus tokens. |
| `num_draft_tokens` | Total proposed draft tokens, after subtracting drafts invalidated by structured-output constraints. |
| `num_spec_tokens` | Configured `num_speculative_tokens` (`k`), i.e. the maximum draft length per step. |

**逐行解读**：
- `mean_acceptance_length`：每次 verification 步平均产出的 token 数（含 bonus）。值域 `[1.0, num_spec_tokens + 1]`，下界对应"全部 draft 被拒"，上界对应"每步 draft 全部接受 + 1 个 bonus"，是衡量 speculative decoding 实际加速效果的最直观指标。
- `draft_acceptance_rate`：被接受的 draft 占提议 draft 的比例，用于评估 draft 模型/策略的质量。
- `acceptance_histogram`：定长（`num_spec_tokens + 1`）稠密直方图；索引 `j` 语义即"接受 j 个 draft 的步数"，长度受 `num_spec_tokens` 配置约束；总和等于 `num_spec_steps`（下一行）。
- `num_spec_steps`：本次请求的验证步总数，等于直方图各项之和。
- `num_accepted_draft_tokens`：累加器，仅累加被实际接受的 draft token，不含 bonus。
- `num_draft_tokens`：提议的 draft token 累计，已扣减被结构化输出约束作废的部分，是 `draft_acceptance_rate` 的分母。
- `num_spec_tokens`：写回配置常量 `k`（即 `num_speculative_tokens`），方便客户端无需结合服务配置即可解释其他字段。

### 表 3：Detailed 字段说明

| Field | Description |
| --- | --- |
| `per_step_accepted` | Accepted draft count at each step. |
| `per_step_drafted` | Proposed draft count at each step. Records the effective proposal length per step, so variable-length drafting (e.g. adaptive speculation) is represented without a schema change. |

**逐行解读**：
- `per_step_accepted`：每一步接受 draft 数的有序序列，长度等于 `num_spec_steps`。
- `per_step_drafted`：每一步**实际提议**长度（effective proposal length）的有序序列；特别为自适应推测等"每步 draft 长度可变"的场景预留，避免因 draft 长度变化而引入 schema 升级——这是该字段设计的核心动机。

### 表 4：Per-request 字段 ↔ Prometheus 计数器对账表

| Per-request field (summed) | Prometheus counter |
| --- | --- |
| `num_spec_steps` | `vllm:spec_decode_num_drafts_total` |
| `num_draft_tokens` | `vllm:spec_decode_num_draft_tokens_total` |
| `num_accepted_draft_tokens` | `vllm:spec_decode_num_accepted_tokens_total` |

**逐行解读**：
- 第一行：将所有 `n == 1` 请求的 `num_spec_steps` 求和，应等于 Prometheus 中的 `vllm:spec_decode_num_drafts_total`——但 Prometheus 端同时统计了 `n > 1` 请求，因此只在 all-`n == 1` 工作负载下两边一致。
- 第二行：`num_draft_tokens` 求和 ↔ `vllm:spec_decode_num_draft_tokens_total`，对应"提议 draft token 总数"语义。
- 第三行：`num_accepted_draft_tokens` 求和 ↔ `vllm:spec_decode_num_accepted_tokens_total`，对应"被接受 draft token 总数"语义。
- 注：`mean_acceptance_length`、`acceptance_histogram`、`num_spec_tokens`、`draft_acceptance_rate` 在 Prometheus 端**没有**直接对应计数器；`draft_acceptance_rate` 可由后两行 Prometheus 计数器相除得到。

---

## 【公式解读】

原文出现的公式/等价定义（保留原式）：

$$
\text{mean\_acceptance\_length} \;=\; 1 \;+\; \frac{\text{num\_accepted\_draft\_tokens}}{\text{num\_spec\_steps}}
$$

- 符号说明：
  - `num_accepted_draft_tokens`：本次请求中被实际接受的 draft token 总数（**不含** bonus token）。
  - `num_spec_steps`：本次请求的 verification step 总数。
  - `+1`：表示每步必中的 bonus token，因此即便 0 个 draft 被接受，mean 仍为 `1.0`。
- 作用：是 speculative decoding 实际"等效每步产出 token 数"的最直观指标，值越大说明 draft 模型越准、加速效果越好。
- 值域：`1.0 ≤ mean_acceptance_length ≤ num_spec_tokens + 1`。

$$
\text{draft\_acceptance\_rate} \;=\; \frac{\text{num\_accepted\_draft\_tokens}}{\text{num\_draft\_tokens}}
$$

- 符号说明：
  - `num_draft_tokens`：本次请求提议的 draft token 总数，已扣除被 structured-output 约束作废的部分。
  - 分子同上一个公式的定义。
- 作用：衡量 draft 模型（或 n-gram 提示策略）"被打中"的频率；越接近 1.0 说明 draft 越贴合目标分布。

**直方图恒等式**（由原文 "the sum of the histogram" 推导）：

$$
\sum_{j=0}^{\text{num\_spec\_tokens}} \text{acceptance\_histogram}[j] \;=\; \text{num\_spec\_steps}
$$

- 符号说明：`acceptance_histogram[j]` 表示"接受恰好 j 个 draft tokens 的步数"。
- 作用：用于客户端一致性校验——直方图总和必须等于 `num_spec_steps`，否则说明服务端数据异常或版本不匹配。

---

## 【关联】

- **`metrics.speculative_decoding` 与 `metrics` 下 timing 字段的关系**：原文明确二者"share the top-level `metrics` object"，通过文末内部链接 `../per_request_metrics.md` 指向 timing 指标的独立文档；二者都仅在 `n == 1` 时返回。
- **Prometheus 端聚合指标**（`/metrics`）：作为服务器聚合视图，文档通过表 4 给出字段对账关系，构成"per-request（单请求明细）↔ aggregated（聚合计数）"的双视角观测体系。
- **Speculative decoding 自身配置**：所有指标的有效性前提是"speculative decoding 已启用"，文档启用示例中显式给出 `--speculative-config '{"method": "ngram", "num_speculative_tokens": 3, "prompt_lookup_min": 1, "prompt_lookup_max": 3}'`，说明该特性与 n-gram、medusa、eagle 等推测方法兼容（detailed 模式下更对 adaptive speculation 做了 schema 预留）。
- **流式响应 / usage chunk**：与 `stream_options.include_usage` 或 `--enable-force-include-usage` 联动；`metrics` 跟随 usage chunk 在流末尾下发，客户端若想流式获得 spec-decode 指标必须开启 usage 上报。
- **Structured-output 约束**：原文在 `num_draft_tokens` 字段中显式提到 "subtracting drafts invalidated by structured-output constraints"，说明此特性与 vLLM 的 structured outputs（guided decoding / JSON schema / tool 调用等）子系统存在交互：被约束作废的 draft token 不计入命中率分母，以避免误导。

---

## 【使用方法】

**启用方式（原文有）**：

```bash
vllm serve <target-model> \
  --speculative-config '{"method": "ngram", "num_speculative_tokens": 3, "prompt_lookup_min": 1, "prompt_lookup_max": 3}' \
  --per-request-spec-decode-metrics summary
```

**配置项**：
- `--per-request-spec-decode-metrics`：取值 `none`（默认）/ `summary` / `detailed`，决定指标采集粒度。

**响应中读取路径**：
- 响应体顶层 → `metrics.speculative_decoding` → 各字段（summary 含 7 项；detailed 在此基础上多 `per_step_accepted`、`per_step_drafted`）。

**流式读取**：
- 需启用 `stream_options.include_usage: true`（客户端侧）或 `--enable-force-include-usage`（服务端侧），`metrics` 才会在最终 usage chunk 中出现。

**返回条件**：
- `--per-request-spec-decode-metrics ∈ {summary, detailed}` **且** speculative decoding 已启用 **且** `n == 1`；否则 `metrics.speculative_decoding` 为 `null`。
