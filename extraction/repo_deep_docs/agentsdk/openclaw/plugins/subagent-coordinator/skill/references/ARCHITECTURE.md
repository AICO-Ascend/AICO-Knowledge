# Subagent Coordinator — Architecture

> 仓 `agentsdk` · 路径 `openclaw/plugins/subagent-coordinator/skill/references/ARCHITECTURE.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agentsdk/openclaw/plugins/subagent-coordinator/skill/references/ARCHITECTURE.md

# Subagent Coordinator 架构文档深度解读

---

## 【定位】

这篇文档描述 **Subagent Coordinator (v4.0.0)** ——一个**事件驱动的任务分解与委派系统**，采用 "Skill + 3 Plugins" 架构,为 OpenClaw 主代理提供任务分析、复杂度评分、路由决策、委派执行以及跨插件的横切关注点(可观测性/任务规划/执行监控)能力。

---

## 【技术要点】

1. **Skill + 3 Plugins 架构**:一个 Skill(`subagent-coordinator`)作为编排核心,搭配三个 Plugins(`observability` / `taskr` / `exec-monitor`)提供横切能力。

2. **事件驱动松耦合**:Skill 通过 7 个事件向 Plugins 广播状态变更,Plugins 可选参与,主流程不依赖插件是否就绪。
   - 7 个事件依次为:`TASK_ANALYZED → DECOMPOSITION_REQUESTED → ROUTE_DECISION → QUALITY_GATE → BEFORE_DELEGATION → DELEGATE → AFTER_EXECUTION`。

3. **5 级算子分级(L1–L5)**:`operatorLevel: "L1" | "L2" | "L3" | "L4" | "L5"`,委派阶段按级别选择执行体——**worker (L1–L3) 或 ACP (L4–L5)**。

4. **复杂度评分 1–10**:`complexity.total` 范围 `1-10`,分解维度包括 `steps / files / dependency / determinism` 四项,并伴随 `keywords: string[]` 用于后续分析。

5. **三种分解策略**:`suggestedStrategy?: "by_file" | "by_step" | "by_domain"` 三选一,由 `taskr` Plugin 在 `DECOMPOSITION_REQUESTED` 阶段提供。

6. **委派双运行时路由**:`routingDecision.runtime: "subagent" | "acp"`,并携带 `agentId: string` 与人类可读的 `reason: string` 说明路由理由。

7. **质量门作为前置校验**:`QUALITY_GATE` 是 pre-execution validation 关口,通过则进入 `BEFORE_DELEGATION` 与 `DELEGATE`,不通过则返回错误给主代理。

---

## 【关键机制与数据】

工作原理与数据流(均原文标注):

- **原文**:核心数据流以**事件链**形式自上而下传递,每个事件都是一个 `interface` 契约,各插件订阅自己关心的事件点。
  - **TASK_ANALYZED** → 由 Analyzer + Complexity Scorer 产出,载荷包含 `task{ id, description, steps?, files?, estimatedDuration?, priority: "low"|"normal"|"high"|"urgent" }`、`complexity{ total: 1-10, breakdown: {steps, files, dependency, determinism}, keywords }`、`operatorLevel (L1-L5)`、`decompositionTriggered: boolean`、`timestamp: number`。
  - **DECOMPOSITION_REQUESTED** → 载荷 `{ task, complexity, suggestedStrategy?: "by_file"|"by_step"|"by_domain", timestamp }`,`taskr` 在此提供"战略性分解方案"。
  - **ROUTE_DECISION** → `exec-monitor` 在此"建议最优运行时选择"。
  - **QUALITY_GATE** → pre-execution validation,失败则直接 `Return error to main agent`,成功才放行。
  - **BEFORE_DELEGATION** → `observability` 在此"记录委派指标(delegation metrics)"。
  - **DELEGATE** → 分发到 `worker (L1–L3)` 或 `ACP (L4–L5)`。
  - **AFTER_EXECUTION** → `observability` 记录"性能指标 & 执行轨迹",`exec-monitor` 对"长时间任务保存检查点(checkpoint)"。

- **原文**:执行结果度量在 `AFTER_EXECUTION.result` 中,字段包括 `taskId / success: boolean / output?: unknown / error?: string / duration: number (毫秒) / tokensUsed?: number`。
  - ⚠ 原文此处的 TypeScript interface 被截断(原文以 `opera` 结尾),后续内容原文未给出,无法补全。

- **原文**:复杂度评分由两个数据源加权得到 —— `observability` 用 ML 模型"增强"复杂度评分,`exec-monitor` 也独立计算一个 `Complexity score`,原文未给出具体加权公式或阈值。

- **原文**:文档未提供性能基准(如 TPS、平均延迟、token 成本)数字,因此本文档不报告性能数据。

---

## 【表格解读】

### 表 1:组件职责表(Component Responsibilities)

| Component | Type | Responsibility |
|-----------|------|---------------|
| **subagent-coordinator** | Skill | Core orchestration: task analysis, complexity scoring, routing decisions, delegation |
| **observability** | Plugin | Metrics collection, token usage tracking, rate limiting, data sanitisation, execution trace recording, cost breakdown, trend analysis |
| **taskr** | Plugin | Hierarchical task planning, persistence, cross-session continuity, task notes |
| **exec-monitor** | Plugin | Quality gates, checkpoint management, retry strategies, task decomposition |

**逐行解读**:

- **subagent-coordinator (Skill)**:唯一的 Skill 实体,承担**核心编排**职责 —— 任务分析、复杂度评分、路由决策、委派。是事件流的"生产者"与决策中枢。
- **observability (Plugin)**:横向可观测性插件,提供 7 项能力 —— 指标采集、token 使用追踪、限流、数据脱敏、执行轨迹记录、成本分解、趋势分析。在 `TASK_ANALYZED`、`BEFORE_DELEGATION`、`AFTER_EXECUTION` 三个事件点介入。
- **taskr (Plugin)**:任务规划插件,专司"**分层任务规划 + 持久化 + 跨会话连续性 + 任务备注**"四项职责,在 `DECOMPOSITION_REQUESTED` 事件提供战略性分解方案。
- **exec-monitor (Plugin)**:执行监控插件,负责"**质量门 + 检查点管理 + 重试策略 + 任务分解**",在 `ROUTE_DECISION` 给出最优运行时建议,在 `AFTER_EXECUTION` 阶段为长任务保存 checkpoint。

> **补充说明**:原文组件框图(图 1.1)额外显式列出 Skill 内部的 7 个子流程模块 —— Task Input → Analyzer → Decomposer ←→ Complexity Scorer → Quality Gate → Router → Delegator(质量门与 Router 之间为闭环反馈,其他按线性推进)。这与表格中 Skill 文字描述的"核心编排"语义一一对应。

---

## 【公式解读】

**原文无公式**(无 LaTeX、无伪代码形式数学公式)。仅出现 TypeScript interface 类型契约(已在【关键机制与数据】中逐字段还原),不构成数值公式。

---

## 【关联】

文档内未提供文末链接列表,因此"内部链接"信息原文缺失。但根据原文文字与图表,可识别以下**模块间关系链**:

- **Skill ↔ observability (Plugin)**:在 `TASK_ANALYZED`、`BEFORE_DELEGATION`、`AFTER_EXECUTION` 三处耦合 —— observability 用 ML 模型增强复杂度评分,并在委派前后及执行后记录指标/轨迹/成本。
- **Skill ↔ taskr (Plugin)**:在 `DECOMPOSITION_REQUESTED` 处耦合 —— taskr 提供战略级(by_file / by_step / by_domain)的分解方案,支持跨会话任务连续性。
- **Skill ↔ exec-monitor (Plugin)**:在 `ROUTE_DECISION` 和 `AFTER_EXECUTION` 处耦合 —— 推荐运行时(subagent vs acp),并在长任务执行后写入 checkpoint;同时 exec-monitor 与 taskr 在"任务分解"职责上有交叉(原文 Component 表将 decomposition 同时归二者,体现职责重叠设计)。
- **技能内部闭环**:Router ⇄ Quality Gate(图 1.1 中 `◀─ Quality Gate ─▶ Router`)形成决策反馈环,质量门未过则回流至路由或回退错误,Router 也消费 Gate 的判定结果。
- **下游执行体**:`DELEGATE` 事件按 operatorLevel 落地到两类执行体 —— `worker (L1–L3)`(轻量本地)或 `ACP (L4–L5)`(高级异步控制协议),是 Skill 委派链的最末端。

---

## 【使用方法】

**原文未涉及** —— 文档仅声明:
- **Project path**: `/Users/chad/workspace/agent-skills/subagent-coordinator/`
- **Version**: `4.0.0`

未提供 CLI 启用命令、配置文件路径、初始化脚本、API key 或运行时参数(如并发数、超时、重试次数)等内容。文档本身定位为**架构总览**,使用方法/启用细节应位于其他参考文档(如本文路径所属的 `references/` 目录下的姊妹文档)中。
