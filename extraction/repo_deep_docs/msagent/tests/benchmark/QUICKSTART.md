# Benchmark Quickstart

> 仓 `msagent` · 路径 `tests/benchmark/QUICKSTART.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msagent/tests/benchmark/QUICKSTART.md

# msagent · tests/benchmark/QUICKSTART.md 深度解读

---

## 【定位】

这篇文档是 benchmark 子模块的"速查手册"，只收录最常用命令，专为第一次跑 benchmark 或调试环境的人员设计，覆盖 smoke 验证、单 case 跑、整目录批量跑、结果查看和故障排查五类高频场景。

---

## 【技术要点】

1. **依赖安装双路径**：推荐 `python3 -m pip install -e .` 安装为本地可执行命令 `benchmark-builder`；若不想安装，所有命令统一加 `PYTHONPATH=src python3 -m run_benchmark` 也能等价运行。
2. **Smoke 测试链路验证**：`benchmark-builder` + `benchmarks/mock_agent_smoke.yaml` + `--agent heuristic --judge heuristic` 的组合是"不调用真实模型、只验证管线"的最小闭环，成功标志为 `Ran 1 cases from mock_agent_smoke; average_score=1.0000`。
3. **msAgent CLI 调用三要素**：`--agent msagent-cli --judge msagent-cli` + `--msagent-agent Hermes`，CLI 路径可通过 `MSAGENT_CLI="uv --project /path/to/msagent run msagent"` 注入，模型可通过 `--model deepseek-chat` 覆盖。
4. **Codex/Claude CLI 模型切换开关**：`export BENCHMARK_DEEPSEEK=1` 临时把 Codex CLI 和 Claude CLI adapter 切到 DeepSeek；Codex 默认连本地 Responses proxy `http://127.0.0.1:8787/v1`（Codex 自定义 provider 要求 Responses API），Claude CLI 直接连 Anthropic-compatible 端点；该开关**只影响 benchmark 子进程**。
5. **结果产物双形态**：人读的汇总在 `runs/<run_id>/report.md`，机器可读的全量结果在 `runs/<run_id>/scores.json`，需用 `jq` 提取字段（`token_usage`、`duration_ms`、`tool_calls`、`must_include_results`、`must_tool_use_results`、`weaknesses`）。
6. **CLI 路径缺失通用修法**：`msAgent CLI was not found` → `export MSAGENT_CLI="uv --project /path/to/msagent run msagent"`；`Codex CLI was not found` → `export CODEX_CLI=/path/to/codex`；`Claude CLI was not found` → `export CLAUDE_CLI=/path/to/claude`。

---

## 【关键机制与数据】

**原文：smoke 验证机制**
- 配置文件：`benchmarks/mock_agent_smoke.yaml`
- agent / judge 都指定为 `heuristic`（不调用真实模型）
- 输出位置：`runs/smoke/`
- 验证成功的原文证据：`Ran 1 cases from mock_agent_smoke; average_score=1.0000`

**原文：CLI 路径注入机制**
- 通过环境变量 `MSAGENT_CLI` 指定源码版或虚拟环境里的 msAgent
- 原文示例：`MSAGENT_CLI="uv --project /path/to/msagent run msagent"`
- 这条路径会被 benchmark 子进程作为外部命令调用，而不是 Python import

**原文：Codex CLI 与 Responses proxy 的绑定关系**
- Codex CLI 默认连接本地 Responses proxy `http://127.0.0.1:8787/v1`
- 原因：原文明确写"Codex 自定义 provider 需要 Responses API"
- 这意味着跑 Codex 之前必须先在本地 8787 端口起好 Responses proxy

**原文：DeepSeek 切换作用域**
- `BENCHMARK_DEEPSEEK=1` 是"只影响 benchmark 子进程"的局部开关
- Claude CLI 还需要额外 `export DEEPSEEK_API_KEY=<your-deepseek-api-key>`

**原文：超时与产出参数**
- 真实 case 跑时设置 `--timeout-seconds 1800`（30 分钟）
- 整目录跑同样使用 1800 秒超时
- 输出：`runs/real-case1-codex-deepseek/` 与 `runs/real-case1-claude-deepseek/`

**原文：scores.json 关键字段（从 jq 表达式逆推）**
- `scores[]` 数组元素包含：`case_id`、`score`、`judge_score`、`must_include_pass`、`must_tool_use_pass`
- 顶层包含：`token_usage`、`duration_ms`、`tool_calls`
- 元素内还含：`must_include_results`、`must_tool_use_results`、`weaknesses`、`must_tool_use_results`（数组/对象）

**原文：case 失败（score=0）时的三大排查线索**
- `Missing Items`：答案未命中 `must_include` 或 `must_include_regex`
- `Missing Tools`：trace 中未命中 `must_tool_use`
- `runtime/*/*.stderr.txt`：底层 CLI 报错日志

---

## 【表格解读】

**原文无表格。** 全文以 bash 代码块、JSON 路径、配置项列表为主，所有"配置/对比/参数"都嵌入在命令行或 jq 表达式里。下表为**对原文参数隐含信息的归纳式重构**（非原文表格），仅作参考：

| 场景 | agent | judge | 配置文件 | 输出目录 | 关键环境变量/参数 |
|---|---|---|---|---|---|
| Smoke | heuristic | heuristic | `benchmarks/mock_agent_smoke.yaml` | `runs/smoke` | — |
| 单 msAgent case | msagent-cli | msagent-cli | `benchmarks/agent_list.yaml` | `runs/msagent-agent-list` | `--msagent-agent Hermes` |
| 单 msAgent case + 自定义模型 | msagent-cli | msagent-cli | `benchmarks/agent_list.yaml` | `runs/msagent-agent-list-deepseek` | `--msagent-agent Hermes --model deepseek-chat` |
| 单 msAgent case + 指定源码 CLI | msagent-cli | msagent-cli | `benchmarks/agent_list.yaml` | `runs/msagent-agent-list` | `MSAGENT_CLI="uv --project /path/to/msagent run msagent"` |
| Codex + DeepSeek | codex-cli | codex-cli | `benchmarks/real_case1.yaml` | `runs/real-case1-codex-deepseek` | `BENCHMARK_DEEPSEEK=1`、`--timeout-seconds 1800` |
| Claude + DeepSeek | claude-cli | claude-cli | `benchmarks/real_case1.yaml` | `runs/real-case1-claude-deepseek` | `BENCHMARK_DEEPSEEK=1`、`DEEPSEEK_API_KEY`、`--timeout-seconds 1800` |
| 整目录批量 | msagent-cli | msagent-cli | `benchmarks`（目录） | `runs/all-msagent` | `--msagent-agent Hermes --timeout-seconds 1800` |

> 注：上表是**对原文命令行的结构化重组**，原文本身以节（§3–§7）形式分散呈现，并非表格。

---

## 【公式解读】

**原文无公式。** 全文不包含任何 LaTeX 或伪代码形式的数学公式。

---

## 【关联】

由于原文未提供文末内部链接（用户标注"内部链接: (无)"），以下关联仅基于**文档本身出现的命名实体**之间的隐含关系：

- **配置文件族**：`benchmarks/mock_agent_smoke.yaml`、`benchmarks/agent_list.yaml`、`benchmarks/real_case1.yaml` 是三份被反复引用的 benchmark 配置；前两者属于 mock/agent-list 范畴，后者属于"real case"（真实模型调用）范畴，文档没有给出它们的字段说明，但根据上下文可推断：
  - `mock_agent_smoke.yaml` 含 1 个 case，用于管线验证（"Ran 1 cases"）。
  - `agent_list.yaml` 用于单 case / 整目录跑 msAgent CLI。
  - `real_case1.yaml` 是真实 case，配套 Codex / Claude CLI + DeepSeek 使用。

- **CLI adapter 层**：`msagent-cli`、`codex-cli`、`claude-cli` 是同层的 `--agent` / `--judge` 选项值，对应三个外部命令分别由 `MSAGENT_CLI`、`CODEX_CLI`、`CLAUDE_CLI` 三个环境变量指定路径。

- **模型层**：`deepseek-chat` 是贯穿文档的默认模型；`Hermes` 是 `--msagent-agent` 的具体取值，指向 msAgent 内置的某个 agent profile。

- **运行器**：`benchmark-builder`（安装后命令）与 `python3 -m run_benchmark`（等价不安装版本）是同一入口的两种调用方式，二者参数完全一致。

- **结果消费侧**：`report.md`（人读）与 `scores.json`（机器读）共享同一个 run_id；jq 命令揭示 scores.json 的 schema 是 benchmark 报告系统的下游契约。

- **上下游关系**：smoke（§3）→ 单 case（§4）→ 多 CLI 真实 case（§5）→ 整目录（§7）是文档推荐的"由浅入深"递进路径；任何一步失败都对应 §9 的故障排查分支。

---

## 【使用方法】

下列命令均**逐字摘自原文**：

**1. 进入 benchmark 目录**
```bash
cd tests/benchmark
```

**2. 安装依赖（二选一）**
```bash
python3 -m pip install -e .
```
或跳过安装，所有后续命令加 `PYTHONPATH=src python3 -m run_benchmark`。

**3. 跑本地 smoke**
```bash
benchmark-builder \
  --config benchmarks/mock_agent_smoke.yaml \
  --out runs/smoke \
  --agent heuristic \
  --judge heuristic
```
等价不安装版：
```bash
PYTHONPATH=src python3 -m run_benchmark \
  --config benchmarks/mock_agent_smoke.yaml \
  --out runs/smoke \
  --agent heuristic \
  --judge heuristic
```
成功后查看报告：
```bash
cat runs/smoke/report.md
```

**4. 跑单个 msAgent case**
```bash
PYTHONPATH=src python3 -m run_benchmark \
  --config benchmarks/agent_list.yaml \
  --out runs/msagent-agent-list \
  --agent msagent-cli \
  --judge msagent-cli \
  --msagent-agent Hermes
```
指定源码版 CLI：
```bash
MSAGENT_CLI="uv --project /path/to/msagent run msagent" \
PYTHONPATH=src python3 -m run_benchmark \
  --config benchmarks/agent_list.yaml \
  --out runs/msagent-agent-list \
  --agent msagent-cli \
  --judge msagent-cli \
  --msagent-agent Hermes
```
指定模型：
```bash
PYTHONPATH=src python3 -m run_benchmark \
  --config benchmarks/agent_list.yaml \
  --out runs/msagent-agent-list-deepseek \
  --agent msagent-cli \
  --judge msagent-cli \
  --msagent-agent Hermes \
  --model deepseek-chat
```

**5. 跑 Codex / Claude + DeepSeek**
```bash
export BENCHMARK_DEEPSEEK=1
# export DEEPSEEK_API_KEY=<your-deepseek-api-key>   # 仅 Claude 需要

PYTHONPATH=src python3 -m run_benchmark \
  --config benchmarks/real_case1.yaml \
  --out runs/real-case1-codex-deepseek \
  --agent codex-cli \
  --judge codex-cli \
  --model deepseek-chat \
  --judge-model deepseek-chat \
  --timeout-seconds 1800

PYTHONPATH=src python3 -m run_benchmark \
  --config benchmarks/real_case1.yaml \
  --out runs/real-case1-claude-deepseek \
  --agent claude-cli \
  --judge claude-cli \
  --model deepseek-chat \
  --judge-model deepseek-chat \
  --timeout-seconds 1800
```

**7. 跑整个目录**（注意原文跳过了 §6 编号）
```bash
PYTHONPATH=src python3 -m run_benchmark \
  --config benchmarks \
  --out runs/all-msagent \
  --agent msagent-cli \
  --judge msagent-cli \
  --msagent-agent Hermes \
  --timeout-seconds 1800
```

**8. 看结果**
```bash
cat runs/msagent-agent-list/report.md
jq '.' runs/msagent-agent-list/scores.json
jq '.scores[] | {case_id, score, judge_score, must_include_pass, must_tool_use_pass}' \
  runs/msagent-agent-list/scores.json
jq '.scores[] | {case_id, must_tool_use_results}' runs/msagent-agent-list/scores.json
jq '{token_usage, duration_ms, tool_calls}' runs/msagent-agent-list/scores.json
```

**9. 常见失败排查**
```bash
export MSAGENT_CLI="uv --project /path/to/msagent run msagent"
export CODEX_CLI=/path/to/codex
export CLAUDE_CLI=/path/to/claude
```
case score=0 时：
```bash
cat runs/<run_id>/report.md
jq '.scores[] | {case_id, must_include_results, must_tool_use_results, weaknesses}' \
  runs/<run_id>/scores.json
```
重点字段：`Missing Items`、`Missing Tools`、`runtime/*/*.stderr.txt`。
