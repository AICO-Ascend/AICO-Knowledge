# Inference-Model-Optimize-Agent 架构文档

> 仓 `mindspeed-agent` · 路径 `docs/ARCHITECTURE.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-agent/docs/ARCHITECTURE.md

# mindspeed-agent `docs/ARCHITECTURE.md` 深度解读

---

## 【定位】

本文档系统描述了 MindSpeed-Agent 仓库中 `inference-model-optimize` 插件的**三层架构（Plugin → Agent → Skill）**与**四阶段推理优化流水线（architect → developer → tester → reviewer）**的完整设计,是该插件的状态机引擎、Agent 角色定义、Skill 能力映射及跨平台适配的**架构级单一真相源**。

---

## 【技术要点】

1. **三层架构模型**:Plugin 层（应用编排,通过 `.claude-plugin/plugin.json` 注册入口）、Agent 层（角色执行,负责状态机推进与 Skill 调用链）、Skill 层（最小知识单元,通过 `SKILL.md` 定义领域知识与工程模板,可被多 Agent 复用）。

2. **四阶段严格顺序流水线**:architect (Phase 1 方案设计) → developer (Phase 2 环境部署) → tester (Phase 3 自动寻优) → reviewer (Phase 4 性能诊断),所有路径最终汇聚到 `finalize → done` 或异常退出到 `abort`。

3. **迭代上限分级**:
   - architect: **iter_cap=3**
   - developer: **iter_cap=4**
   - tester: **iter_cap=8**
   - reviewer: **iter_cap=5**
   - 整体 tester ↔ reviewer 闭环:最多 **3 轮**

4. **Orchestrator 单点调度**:唯一入口 Agent,亲自充当状态机引擎,**每次状态转移调用 `engine.state_machine next`** 而非凭记忆决定;门禁校验 + 重试最多 **2 次**;收集 **17 个**用户参数字段(`model_path`、`scenario`、`npu_cards` 等);单点任务（仅显存计算、仅 benchmark）直接委派对应 Agent,不走流水线。

5. **Handoff Token 协议**:每个 Agent 输出结构化 JSON + handoff token,具体为:
   - architect → `ARCHITECT_READY` / `ARCHITECT_FAILED`
   - developer → `SERVICE_READY` / `SERVICE_FAILED`
   - tester → `NEED_RESTART`(回 developer)/ `OPTIMIZATION_READY`(进 reviewer 或 finalize)
   - reviewer → `REVIEWER_CONTINUE`(回 tester)/ `REVIEWER_DONE`(进 finalize)

6. **跨平台适配**:同一套 Agent 定义通过 `agent.yaml` 中的 `claude_code:` / `codex:` 平台字段差异化配置（model、context 等）,由 `engine/agent_registry.py` 在运行时解析;Claude Code 用 Workflow JS 状态机内嵌引擎,Codex 用 Python CLI 直调,DSH 复用 Python 引擎 + subagent + 双加载(`AGENTS.md` + `CLAUDE.md`)。

7. **Plugin 版本与依赖**:`inference-model-optimize` 插件 version **0.5.0**,声明依赖三个 skill:`./skills/model-analysis`、`./skills/deployment`、`./skills/performance-optimization`;Claude Code 加载插件时自动将 `skills/` 下 symlink 目标注册为可用 skill。

---

## 【关键机制与数据】

### 流水线状态转移机制

工作原理（原文摘录核心机制）:

- **流水线入口**:`init` 状态启动,进入 `architect`（方案设计 Agent,iter_cap=3）
- **架构师产出**:`ARCHITECT_READY` 进入 `developer`（环境部署）;`FAILED` 走 always 分支;`always` 路径直达 finalize
- **部署产出**:`SERVICE_READY` 进入 `tester`（自动寻优）;`FAILED` 走 always 分支
- **寻优产出**（tester iter_cap=8）:
  - `NEED_RESTART` → 回 developer 重启服务（携带 `candidate_restart_params`）
  - `OPTIMIZATION_READY + iter_below_cap` → 进入 reviewer
  - `OPTIMIZATION_READY`（at cap）→ 直接进 finalize
- **诊断闭环**（reviewer iter_cap=5）:
  - `CONTINUE + tester_below_cap` → 回 tester 继续迭代
  - `REVIEWER_DONE / CONTINUE（tester at cap）` → 进 finalize
- **终态**:`finalize` → `done`（正常完成）;异常路径 → `abort`

### 关键性能数据

原文:**无具体性能数据**（如吞吐量数值、加速比等）。本文档属于架构描述,未提供实测性能指标。

### Agent 输出 Schema 关键字段

- **architect (ARCHITECT_SCHEMA)**: `model_profile`（架构类型、层数、hidden_size、参数量）、`memory_budget`（权重/KV Cache/激活/引擎开销,单位 GB）、`recommended_strategy`（TP × DP × EP × PP、总卡数、rationale）、`hardware_requirements`（最少 NPU 卡数、推荐配置）、`risk_warnings`
- **developer (DEVELOPER_SCHEMA)**: `service_url`、`port`、`model_name`、`tp`、`dp`、`health_check_passed`、`models_endpoint_ok`、`service_status`
- **tester (TESTER_SCHEMA)**: `baseline_metrics`（基线吞吐、TTFT、TPOT、P50/P99 延迟）、`optimized_metrics`、`comparison`（各维度变化百分比）、`optimal_params`、`candidate_restart_params`、`target_achieved`、`comparison_report`
- **reviewer (REVIEWER_SCHEMA)**: `profiling_data_path`、`profiling_collected`、`diagnosis`（E2E 耗时、compute/communication/idle 占比）、`bottleneck_classification`（compute / communication / dispatch / memory）、`operator_top_n`（耗时 Top-N 算子及占比）、`optimization_suggestions`（id、priority、executable_by、verification_method）、`evidence_list`（数据来源、表名/字段名、原始数值）、`diagnosis_report`

---

## 【表格解读】

### 表 1:跨平台支持（原文逐字还原）

| 平台 | 插件清单 | 指令文件 | Workflow 引擎 |
|------|---------|---------|--------------|
| Claude Code | `.claude-plugin/plugin.json` | `CLAUDE.md` | Workflow JS（内嵌 JS 状态机） |
| Codex | `.codex-plugin/plugin.json` | `AGENTS.md` | Python CLI 直调 |
| DSH（DeepSeek Harness） | `.dsh/skills/`（投影） | `AGENTS.md` + `CLAUDE.md`（双加载） | 复用 Python 引擎 + subagent |

**逐行解读**:
- **Claude Code 行**:Claude Code 平台使用 `.claude-plugin/plugin.json` 作为插件清单,平台级指令文件为 `CLAUDE.md`,工作流引擎为内嵌的 Workflow JS 状态机（即 `optimize-pipeline.workflow.js`）。
- **Codex 行**:Codex 平台使用 `.codex-plugin/plugin.json` 作为插件清单,指令文件为 `AGENTS.md`,工作流引擎为 Python CLI 直调（绕过 JS 状态机）。
- **DSH 行**:DSH（DeepSeek Harness）平台将 skill 投影到 `.dsh/skills/` 目录,指令文件**双加载** `AGENTS.md` + `CLAUDE.md`,复用 Python 引擎并通过 subagent 调度。

### 表 2:Agent 角色定义文件（原文逐字还原）

| 文件 | 用途 |
|------|------|
| `agent.yaml` | 跨平台元数据 — name、description、skills、tools、schema，以及 `claude_code:` / `codex:` 平台配置 |
| `AGENT.md` | Claude Code 原生 Agent 指令 — YAML frontmatter + 详细的中文执行指引 |

**逐行解读**:
- **`agent.yaml` 行**:承载跨平台可复用的元数据,包括 Agent 名称、描述、依赖 skill、可用工具、输出 schema,以及 `claude_code:` / `codex:` 两个平台专属配置块（模型选择、上下文模式等）。由 `engine/agent_registry.py` 在运行时解析平台差异。
- **`AGENT.md` 行**:Claude Code 原生 Agent 指令载体,采用 YAML frontmatter + 详细中文执行指引格式,是 Claude Code 平台加载时实际阅读的 prompt 来源。

### 表 3:Agent-Skill 映射（原文逐字还原,原文截断处标注）

| Agent | Skills | 说明 |
|-------|--------|------|
| architect | `vllm-memory-calculator` | 显存计算器，分析模型结构与显存预算 |
| developer | `environment-install` | 深度学习环境（Conda、CANN、vLLM）安装 |
| developer | `vllm-ascend-serving` | vLLM Ascen（原文此处截断） |

**逐行解读**:
- **architect 行**:architect Agent 依赖 `vllm-memory-calculator` skill,用于分析模型结构并产出显存预算（输入 model_path、scenario、npu_cards、precision 等参数）。
- **developer (environment-install) 行**:developer Agent 依赖 `environment-install` skill,负责 Conda、CANN、vLLM 等深度学习环境的安装部署。
- **developer (vllm-ascend-serving) 行**:developer Agent 还依赖 `vllm-ascend-serving` skill,用于在 Ascend NPU 平台上启动 vLLM 推理服务。原文该单元格内容被截断（"...vLLM Ascen"）,后续说明缺失。

> **补充说明**（基于原文 Agent 章节推导）:tester Agent 依赖 `vllm-ascend-benchmark` 与 `vllm-ascend-autotune-zh`;reviewer Agent 依赖 `ascend-profiling-collection`、`ascend-msprof-analyze-cli`、`ascend-perf-tuning`。

---

## 【公式解读】

**原文无公式**。

文档中虽包含状态转移图与目录树（伪 ASCII 图形）,但未出现 LaTeX 数学公式或形式化伪代码公式。流水线阶段关系以文本箭头表示（如 `architect (Phase 1) → developer (Phase 2) → tester (Phase 3) → reviewer (Phase 4)`）,不构成公式形式。

---

## 【关联】

### 与仓库其他模块的关联

- **根目录 `.claude-plugin/marketplace.json`**:定义了 marketplace 中可安装的插件列表,包括 `mindspeed-agent`、`inference-model-optimize`、`ops`、`doc-agent` 四个插件;`inference-model-optimize` 是其中之一,与其他三个插件并列部署。

- **Plugin 目录结构关联**:
  - `plugins/inference-model-optimize/skills/` 为 symlink → `../../skills/...`,即实际指向仓库根 `skills/` 目录下的 `model-analysis`、`deployment`、`performance-optimization` 三类 skill。
  - `skills/inference-model-skills/SKILL.md` 作为推理领域的**路由索引**,按用户意图分发到 `deployment/`（部署和服务管理）、`model-analysis/`（模型与显存分析）、`performance-optimization/`（benchmark、寻优和 profiling）。

- **Workflow 文件协作链**:
  - `optimize-pipeline.yaml`:状态机 YAML（**单一真相源**）
  - `optimize-pipeline.workflow.js`:Claude Code Workflow JS 运行时
  - `state-machine-config.js`:YAML 编译出的 JS 状态机
  - `schemas.js`:结构化输出 JSON Schema（对应 ARCHITECT/DEVELOPER/TESTER/REVIEWER_SCHEMA）
  - `gates.js`:门禁校验函数（orchestrator 调用,最多重试 2 次）
  - `briefs.js`:Prompt 模板

### 与上下游特性的关联

- **上游**:根 `MindSpeed / Ascend NPU` 平台的 Claude Code 插件集合——`mindspeed-agent` 本身是上位概念,`inference-model-optimize` 是其下的子插件。
- **下游**:依赖的 skill 知识库（model-analysis、deployment、performance-optimization）以及具体的工程模板（如 `vllm-memory-calculator` 显存计算器、`vllm-ascend-benchmark` 压测工具、`ascend-profiling-collection` profiling 采集工具）。
- **横向**:与 `ops`、`doc-agent` 同为 marketplace 可安装插件,通过 `marketplace.json` 统一分发。

> 注:原文未提供内部链接 URL（标注为"内部链接: (无)"）。

---

## 【使用方法】

原文**部分涉及**,以下从原文摘录的启用方式/配置项:

### 插件清单声明（plugin.json）

```json
{
  "name": "inference-model-optimize",
  "version": "0.5.0",
  "skills": [
    "./skills/model-analysis",
    "./skills/deployment",
    "./skills/performance-optimization"
  ]
}
```

### Agent 平台配置示例（agent.yaml）

```yaml
name: architect
description: ...
skills: [vllm-memory-calculator]
tools: [read, bash, skill]
schema: architect_schema

claude_code:
  model: sonnet
  extra_tools: [Read, Bash, Skill]

codex:
  model: claude-sonnet-5
  context: fork
```

### Orchestrator 入口调用

- 用户参数入口:收集 **17 个字段**（如 `model_path`、`scenario`、`npu_cards` 等）
- 状态机推进:每次状态转移调用 `engine.state_machine next`(而非凭记忆决定)
- 门禁重试上限:**2 次**
- 单点任务入口:仅显存计算、仅 benchmark 等单点任务直接委派对应 Agent,不走完整流水线

### 加载机制

- **Claude Code**:通过 `.claude-plugin/plugin.json` 注册,自动将 `skills/` 下 symlink 目标注册为可用 skill
- **Codex**:通过 `.codex-plugin/plugin.json` 注册
- **DSH**:通过 `.dsh/skills/` 投影,`AGENTS.md` + `CLAUDE.md` 双加载

> **原文未涉及**:具体 CLI 启动命令、运行时环境变量、用户面向的端到端调用示例。本文为架构设计文档,使用方法章节以"架构描述"为主,完整的用户面向使用手册需参考其他文档（原文未列出具体路径）。
