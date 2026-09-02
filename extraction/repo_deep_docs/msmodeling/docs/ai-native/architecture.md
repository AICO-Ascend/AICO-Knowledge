# AI Native 架构

> 仓 `msmodeling` · 路径 `docs/ai-native/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/ai-native/architecture.md

# 一体化深度解读：AI Native 架构

## 【定位】

本篇文档定义 `msmodeling` 仓库的「AI Native 架构」分层、能力边界与协作规则，明确开发者意图如何经统一入口、授权与工作流编排落到 GitCode CLI / `openLiBing` 上，并形成可审计的 Issue / PR 记录，从而取代或绕开对 Superpowers / OpenSpec 等外部运行时的依赖。

## 【技术要点】

1. **五层意图落地位**（原文）：开发者自然语言 → `AGENTS.md` 统一入口 → `spec/`（授权、远端边界、审计、状态机）→ 工作流 Skills / 领域 Skills / GitCode Skills / 本地工具 → `GitCode CLI + openLiBing analyzer` → 可审计 Issue / PR。
2. **端到端可拆分 + 人机共治**（原文）：工作流负责编排，原子 Skill 仍可单独调用；默认逐阶段确认，明确授权后可连续推进；人可随时暂停、改计划或接管。
3. **事实优先与证据驱动**（原文）：远端状态来自 CLI、`PR` 变更来自 `gitcode pr diff`、代码事实来自正确工作树或基线；测试 / 构建 / CI / 评审结论必须关联证据，未知项不写成通过。
4. **最小权限边界**（原文）：AI 不自动审批、合并、强推、关闭 Issue，也不绕过门禁。
5. **三类仓库身份区分**（原文）：canonical = `Ascend/msmodeling`（正式 Issue / PR / Review / CI 目标）；source = 当前可写 Git remote（动态识别，可为个人 Fork 或主仓开发分支）；operation target = 每次 `GitCode CLI` 操作实际所用仓库，写操作必须显式选择和确认。
6. **不引入运行时依赖**（原文）：不引入 Superpowers，也不引入 OpenSpec；仓库内已有 `spec/`、RFC、design 三层事实源，沿用仓库原生格式以避免双写和冲突；结构化需求、验收条件与方案文档仍采用仓库原生格式输出。
7. **Staging 与 canonical 隔离**（原文）：Fork 内部 PR 只用于 staging，不能替代 canonical PR 的 `openLiBing` 结果。

## 【关键机制与数据】

- **意图传递通道**（原文）：开发者的自然语言（意图、确认、暂停、接管）自顶向下流动，逐层被沉淀为：`AGENTS.md` 中的任务路由 → `spec/` 中的授权与边界 → 工作流 Skills 中的具体编排 → 工具调用 → 远端 / 本地代码事实与 Issue / PR 记录。
- **Skill 编排粒度**（原文）：同时给出三类 Skill —— 工作流 Skills（Issue / Delivery / PR Review / CI / Feedback）、领域 Skills（DeviceProfile / op mapping / 模型适配 / OptiX / 性能优化）、GitCode Skills（Issue / PR / inline review / pipeline），并以「本地工具（Git / pytest / pre-commit / build）」做收口。
- **事实源分层**（原文）：远端事实 = `GitCode CLI`；PR 变更 = `gitcode pr diff`；代码事实 = 工作树或基线。证据未对齐的结论不被视为通过。
- **人机协作状态机**（原文）：默认每阶段需人确认；明确授权后切换为连续推进；任意阶段人可暂停、修改计划或接管，整个状态机由 `spec/` 中的状态机定义承载。
- **审计落地形态**（原文）：所有动作的最终副产物是可审计的 Issue / PR 记录，canonical 仓库 `Ascend/msmodeling` 为正式归档目标。
- **性能 / 量化数据**：原文无任何性能指标、吞吐、延迟或量化基准。

## 【表格解读】

原文无表格。

唯一结构化的「分层图」以 `text` 代码块给出（见下，逐字还原）：

```text
开发者
  │ 自然语言意图、确认、暂停、接管
  ▼
AGENTS.md ── 统一入口与任务路由
  ▼
spec/ ── 授权、远端边界、审计、状态机
  ▼
工作流 Skills ── Issue / Delivery / PR Review / CI / Feedback
  ├── 领域 Skills ── DeviceProfile / op mapping / 模型适配 / OptiX / 性能优化
  ├── GitCode Skills ── Issue / PR / inline review / pipeline
  └── 本地工具 ── Git / pytest / pre-commit / build
  ▼
GitCode CLI + openLiBing analyzer
  ▼
Issue / PR 可审计记录
```

逐层解读：

| 层级 | 原文措辞 | 在架构中的作用 |
|---|---|---|
| 开发者 | 「自然语言意图、确认、暂停、接管」 | 唯一既可发起又可中断流程的角色，对应「人机共治」中的人侧。 |
| `AGENTS.md` | 「统一入口与任务路由」 | 把自然语言意图路由到对应的工作流 / 领域 / GitCode Skill，是 AI 侧的入口契约。 |
| `spec/` | 「授权、远端边界、审计、状态机」 | 决定本次会话能调哪些 Skill / 工具、写到哪个仓库、何时暂停、为状态机提供事实源。 |
| 工作流 Skills | 「Issue / Delivery / PR Review / CI / Feedback」 | 端到端编排步骤，对应 Issue 生命周期到 PR 评审 + CI + 反馈闭环。 |
| 领域 Skills | 「DeviceProfile / op mapping / 模型适配 / OptiX / 性能优化」 | 与 `msmodeling` 业务强绑定的原子能力：`DeviceProfile`、算子映射、模型适配、OptiX、性能优化。 |
| GitCode Skills | 「Issue / PR / inline review / pipeline」 | 把工作流操作落地到 GitCode 平台的对象与流程。 |
| 本地工具 | 「Git / pytest / pre-commit / build」 | 代码事实与本地证据的产生器，支撑「证据驱动」原则。 |
| `GitCode CLI + openLiBing analyzer` | 图中最末端执行层 | 真实的远端副作用执行与结果分析：`GitCode CLI` 写远端，`openLiBing analyzer` 给出审查 / 分析结果。 |
| Issue / PR 可审计记录 | 图中最末端归档层 | 架构的「事实沉淀」，保证每一步都可回放与追责。 |

## 【公式解读】

原文无公式。

## 【关联】

- **与领域 Skills 的耦合**（原文）：架构把 `DeviceProfile / op mapping / 模型适配 / OptiX / 性能优化` 作为领域 Skill 挂在工作流之下，意味着 AI Native 流程必须能调用这些 msmodeling 业务原子能力，而非仅做通用 Git 操作。
- **与 `spec/` 的耦合**（原文）：`spec/` 同时承担「授权、远端边界、审计、状态机」四种职能，是 AI 自主性的总开关，也是「最小权限」的落地点。
- **与 GitCode 平台的耦合**（原文）：通过 `GitCode CLI`（写操作）与 `openLiBing analyzer`（分析）形成双向通路；canonical 仓库 `Ascend/msmodeling` 为正式归档目标，Fork 内部 PR 仅服务于 staging。
- **与文档体系 `spec/、RFC、design` 三层事实源**（原文）：架构明确继续沿用仓库原生 `spec/`、RFC、design 三层事实源，避免引入 OpenSpec 后的双写与冲突。
- **与上下游模块**（原文）：外部链接信息中标注为 (无)，本文档自身未挂出其他文档链接；本架构未引用 Superpowers 与 OpenSpec 的运行时能力，相关替代由执行规范与工作流 Skills 提供。

## 【使用方法】

原文未给出具体的「启用步骤 / 配置项 / 命令」清单。可从原文中直接读出的可执行抓手仅有：

- **入口文件**（原文）：在仓库根目录维护 `AGENTS.md` 作为统一入口与任务路由。
- **事实 / 授权 / 状态机载体**（原文）：使用仓库内已有的 `spec/`、`RFC`、`design` 三层文档承载授权、远端边界、审计与状态机；结构化需求 / 验收条件 / 方案文档也以仓库原生格式产出。
- **写操作的强制确认**（原文）：每次 `GitCode CLI` 操作必须显式选择并确认 operation target；不得对 `Ascend/msmodeling` canonical 仓做自动审批 / 合并 / 强推 / 关闭 Issue / 绕过门禁。
- **审计证据抓手**（原文）：以 `gitcode pr diff` 拉取 PR 变更，以本地 Git / pytest / pre-commit / build 产出的工作树或基线作为代码事实，由 `openLiBing analyzer` 产出分析结果，三者共同作为证据驱动结论的依据。
- **不在范围内**（原文）：不安装 / 不引入 Superpowers、不引入 OpenSpec 运行时依赖。

如需具体启用命令（如 `gitcode` CLI 的安装与登录、`openLiBing` 的调用方式、`AGENTS.md` 的契约模板等），原文未涉及。
