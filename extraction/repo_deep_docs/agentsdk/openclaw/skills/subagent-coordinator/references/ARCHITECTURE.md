# Subagent Coordinator — Architecture

> 仓 `agentsdk` · 路径 `openclaw/skills/subagent-coordinator/references/ARCHITECTURE.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agentsdk/openclaw/skills/subagent-coordinator/references/ARCHITECTURE.md

# Subagent Coordinator — Architecture 深度解读

## 【定位】

这篇文档描述的是 AgentSDK 中 **Subagent Coordinator（子代理协调器）** 这一基于 Skill + 3 Plugins 架构的**事件驱动任务分解与委派系统**的整体架构设计,包括组件构成、事件流走向、各事件载荷的数据结构,以及三个插件的核心职责分工。

---

## 【技术要点】

1. **架构形态**: 采用 **Skill + 3 Plugins** 组合,即核心编排能力由 Skill (`subagent-coordinator`) 承担,三个外部插件 (`observability`、`taskr`、`exec-monitor`) 通过事件总线以松耦合方式扩展行为。

2. **Skill 内部组件管线** (共 7 个内部节点): `Task Input → Analyzer → (Quality Gate) → Decomposer → Complexity Scorer → Router → Delegator`,先质量闸再分解、再评分、再路由、最后委派。

3. **事件驱动的状态推进** (7 个关键事件,按文档出现顺序): `TASK_ANALYZED` → `DECOMPOSITION_REQUESTED` → `ROUTE_DECISION` → `QUALITY_GATE` → `BEFORE_DELEGATION` → `DELEGATE` → `AFTER_EXECUTION`。每个事件在主干之外都会向一个或多个插件派发,形成可观测的旁路。

4. **复杂度评分量化**: `complexity.total` 取值范围 **1–10**,由 `steps`、`files`、`dependency`、`determinism` 四个细分维度加权构成,并附带关键词列表 (`keywords`)。

5. **操作员分级与委派目标**: `operatorLevel` 共 **5 级 (L1–L5)**;委派目标按级别分流——**L1–L3 走 worker (subagent)**,**L4–L5 走 ACP**。

6. **分解策略三选一**: `DECOMPOSITION_REQUESTED` 事件支持 `by_file` / `by_step` / `by_domain` 三种策略 (`suggestedStrategy`),且 `TASK_ANALYZED` 中已有 `decompositionTriggered` 布尔位记录是否触发分解。

---

## 【关键机制与数据】

**工作原理(原文有的部分)**:

- 文档以 ASCII 图明确表达了**两条分层结构**:
  1. 顶层 Skill 内部分为 7 个处理节点,且 **Quality Gate 的判定结果(`Pass?`)** 决定是否进入下游;`No` 分支直接 `Return error to main agent`,**Yes** 才进入 `BEFORE_DELEGATION`。
  2. 底层 Plugin Layer 中 3 个插件按职责横切——`observability` 在 `TASK_ANALYZED`、`BEFORE_DELEGATION`、`AFTER_EXECUTION` 三处介入;`taskr` 在 `DECOMPOSITION_REQUESTED` 介入;`exec-monitor` 在 `ROUTE_DECISION` 介入并提供"suggested optimal runtime selection",在 `AFTER_EXECUTION` 做 "checkpoint save if long-running task"。
- 事件传播机制被明确定义为**单向主路径 + 旁路增强**:`Task Received` 是入口,经过一连串事件逐步细化,最终 `DELEGATE` 调用 worker/ACP,`AFTER_EXECUTION` 收尾。

**性能/数据(原文有的部分)**:

- **优先级枚举** (`TaskAnalyzedEvent.task.priority`): `"low" | "normal" | "high" | "urgent"` 四级。
- **执行时长字段** (`AfterExecutionEvent.result.duration`): 单位为 **毫秒 (milliseconds)**。
- **可选 token 计量字段** (`AfterExecutionEvent.result.tokensUsed`): 类型 `number`,且标记为 `?` 可选。
- **执行结果状态** (`AfterExecutionEvent.result.success`): `boolean`。
- **分解策略枚举** (`DecompositionRequestedEvent.suggestedStrategy`): `"by_file" | "by_step" | "by_domain"`。
- **运行时枚举** (`BeforeDelegationEvent.routingDecision.runtime`): `"subagent" | "acp"`。
- **时间戳**: 全部 4 个事件载荷(已展示完整者)均含 `timestamp: number` 字段。

> 注: `AfterExecutionEvent` 在原文中以 `opera` 截断,后续 `operatorLevel` 字段未给出;`AFTER_EXECUTION` 在事件流图中也出现于最末位置,未呈现下游事件,本文不做臆测填补。

---

## 【表格解读】

原文包含 1 张 Markdown 表格(组件职责表),逐字还原如下:

| Component | Type | Responsibility |
|-----------|------|---------------|
| **subagent-coordinator** | Skill | Core orchestration: task analysis, complexity scoring, routing decisions, delegation |
| **observability** | Plugin | Metrics collection, token usage tracking, rate limiting, data sanitisation, execution trace recording, cost breakdown, trend analysis |
| **taskr** | Plugin | Hierarchical task planning, persistence, cross-session continuity, task notes |
| **exec-monitor** | Plugin | Quality gates, checkpoint management, retry strategies, task decomposition |

**逐行解读**:

- **subagent-coordinator / Skill / "Core orchestration"**: 是整个系统的主编排者,文档 §1.2 与事件流图均把它定位为"中枢",承载**任务分析、复杂度评分、路由决策、委派**四类核心动作;它不持久化、不做监控、不做重试,只决策。
- **observability / Plugin / "Metrics collection…"**: 横切关注点插件,职责最为繁多——**指标采集、token 统计、限流、数据脱敏、执行 trace、成本拆解、趋势分析**共 7 项;事件流图中它在 3 处介入(分析、委派前、执行后),印证了它的"全链路旁路观测"角色。
- **taskr / Plugin / "Hierarchical task planning…"**: 偏**状态与计划管理**,负责**层次化任务规划、持久化、跨会话连续性、任务笔记**;在事件流中只在 `DECOMPOSITION_REQUESTED` 处介入,提供 "strategic decomposition plan",即宏观分解蓝图。
- **exec-monitor / Plugin / "Quality gates…"**: 偏**执行质量与恢复**,负责**质量门、检查点、重试策略、任务分解**;与 `subagent-coordinator` 的 `Quality Gate` 内部节点同名,但作为插件它还在 `ROUTE_DECISION` 阶段提供 runtime 建议,以及在 `AFTER_EXECUTION` 保存 checkpoint,体现"运行时守护"。

> 4 个组件的 Type(Skill/Plugin)直接对应文档标题中的 **"Skill + 3 Plugins"** 数字;表格本身即这一架构主张的最凝练表达。

---

## 【公式解读】

原文无公式。

文档中的"复杂度评分"虽具有公式意味(`total` 由 4 个 `breakdown` 项构成),但并未给出具体加权表达式或数学形式,仅以 TypeScript `interface` 列出字段,因此不构成可逐符号解析的公式。

---

## 【关联】

文档本身的内部链接元信息标注为 **(无)**,没有显式给出指向其他模块/文档的锚点链接。但从文本上下文可以梳理出以下**隐式上下游与模块关系**:

- **上游(主 Agent)**: `MAIN AGENT (OpenClaw)` 是 Skill 的宿主,`Task Received` 入口由主 Agent 触发;委派结果 (`DELEGATE → DELEGATE → worker (L1-L3) or ACP (L4-L5)`) 也回流到主 Agent,质量门失败时 `Return error to main agent`。
- **下游(执行体)**:
  - **L1–L3 worker / subagent**: 由 `routingDecision.runtime = "subagent"` 触发。
  - **L4–L5 ACP**: 由 `routingDecision.runtime = "acp"` 触发,代表比 subagent 更上层的执行能力。
- **横向(插件协同)**:
  - `observability` ↔ `taskr`/`exec-monitor`: 三者在事件流上各自挂载,无相互依赖关系,体现"事件总线 + 可选插件参与"的松耦合。
  - `taskr` (战略分解) 与 `exec-monitor` (执行分解) 同名相关字段 `Decomposition`/`Task decomposition`,前者偏计划、后者偏运行时执行。
- **同宿主项目**: `Project path: /Users/chad/workspace/agent-skills/subagent-coordinator/`(原文),说明本 Skill 与同仓其他 agent-skills 同源,但具体同仓兄弟 Skill 未在文档内列名。
- **与版本管理**: 文档标注 `Version: 4.0.0`,暗示这是一个已有 3 个主版本迭代的成熟组件。

---

## 【使用方法】

原文未涉及。

文档作为 **Architecture / Overview** 类目,仅描述"系统是什么、组件如何组合、事件如何流动、载荷字段如何定义";**未给出任何启用开关、配置项、CLI 命令或调用样例**。涉及启用与配置的具体内容需参考同仓其他文档(本概览未引用具体路径)。
