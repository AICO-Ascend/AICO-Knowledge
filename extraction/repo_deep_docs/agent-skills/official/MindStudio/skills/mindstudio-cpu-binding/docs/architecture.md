# 架构设计

> 仓 `agent-skills` · 路径 `official/MindStudio/skills/mindstudio-cpu-binding/docs/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/MindStudio/skills/mindstudio-cpu-binding/docs/architecture.md

# 架构设计文档深度解读

## 【定位】
本文档定义了 `mindstudio-cpu-binding` 技能的分层架构总览，明确各层职责边界、采集机制、专家规则沉淀方式、MVP 交付形态以及四阶段演进路径，为后续诊断流程、采集器、报告模板、回滚机制等子模块提供统一的架构约束与协作框架。

---

## 【技术要点】

1. **四层分层架构**：文档明确划分为 Agent 交互与编排层、专家规则层、Snapshot 数据层、采集层，强调"第一阶段建议采用分层架构，不直接绑定某一种最终形态"。

2. **采集层只读低侵入原则**：MVP 采集脚本仅通过 `/proc/<pid>/status`、`/proc/<pid>/task/*/status|stat|comm`、`lscpu`、`numactl -H`、cgroup cpuset/cpu quota 文件、NPU 拓扑命令、PyTorch 环境变量、轻量 CPU 采样工具进行只读采集。

3. **MVP 交付五件套**：原文代码块明示为「可运行采集脚本 + Snapshot JSON + Agent 分析提示词/Skill + 报告模板 + 示例报告」，强调"不需要一开始搭建完整 MCP 或 Plugin"。

4. **四阶段演进路径**：
   - 阶段 1（脚本 + 文档 + Agent Prompt）：交付 3-5 个真实/脱敏案例
   - 阶段 2（Skill 化）：固化专家流程
   - 阶段 3（MCP 化）：固化 7 个工具函数（`collect_cpu_topology`/`collect_npu_topology`/`collect_process_affinity`/`collect_cgroup_limits`/`collect_runtime_config`/`collect_cpu_runtime_sample`/`generate_affinity_plan`）
   - 阶段 4（独立 Agent / Plugin）：面向规模化使用

5. **Agent 编排层最小询问集**：训练/推理、PID、NPU 设备、rank 映射、环境类型、优化目标六项；输出"保守方案 + 进阶方案"，并明示风险、回滚方式和验证计划。

6. **专家规则覆盖范围**：未绑核判断、跨 NUMA 判断、Rank/NPU/NUMA 不匹配判断、可用 CPU 数与线程数不匹配判断、PyTorch DataLoader/intra-op/inter-op/OpenMP 线程配置建议、多 rank/多实例 CPU range 冲突判断、latency 与 throughput 目标下的 SMT 使用策略。

---

## 【关键机制与数据】

**整体工作机制（数据流路径）**：用户通过 Agent 交互层发起诊断请求 → Agent 询问最少必要信息后触发采集层 → 采集层通过只读系统接口收集数据 → 采集结果写入 Snapshot 数据层（结构化 JSON）→ 专家规则层基于 Snapshot 进行问题分类与诊断 → Agent 编排层整合诊断结果 → 输出包含保守方案与进阶方案的报告。

**采集层数据来源（原文逐项列出）**：
- 系统拓扑：`lscpu`、`numactl -H`
- NPU 拓扑：NPU 拓扑命令或平台适配器
- 进程线程信息：`/proc/<pid>/status`、`/proc/<pid>/task/*/status|stat|comm`
- 资源约束：cgroup cpuset/cpu quota 文件
- 运行时配置：PyTorch 相关环境变量
- 运行时采样：轻量 CPU 采样工具（用于 CPU 使用率和线程 TopN 采样）

**MCP 化阶段固化的工具函数清单（原文 7 项）**：`collect_cpu_topology`、`collect_npu_topology`、`collect_process_affinity`、`collect_cgroup_limits`、`collect_runtime_config`、`collect_cpu_runtime_sample`、`generate_affinity_plan`。

**性能数据**：原文未涉及任何性能基准、时延或吞吐数字。

---

## 【表格解读】

原文第 6 节「文档映射」表格逐字还原如下：

| 架构部分 | 对应文档 | 说明 |
|----------|----------|------|
| Agent 交互与编排层 | `agent-workflow.md` | 定义端到端交互、采集、诊断、报告、验证和状态机。 |
| 自动绑核与回滚 | `binding-rollback-design.md` | 定义执行后端、rollback-state、回滚流程和实验计划。 |
| HTML 报告输出 | `html-report-design.md` | 定义 HTML 页面结构、CPU/NPU/NUMA 拓扑关系可视化和跨平台查看要求。 |
| 专家规则层 | `diagnosis-rules.md` | 定义问题 Taxonomy、证据字段、判断逻辑和建议策略。 |
| Agent 报告模板 | `../templates/report-template.md` | 约束诊断报告内容结构和证据表达方式。 |
| Snapshot 数据层 | `snapshot-schema.md` | 定义采集器、Agent、MCP 之间的结构化数据契约。 |
| 采集层 | `collector-design.md` | 定义 MVP 采集器 CLI、模块、安全边界和失败策略。 |

**逐行解读**：

1. **Agent 交互与编排层 → `agent-workflow.md`**：编排层覆盖端到端交互、采集触发、诊断执行、报告生成、验证步骤与状态机管理，是整个诊断流程的控制中枢。

2. **自动绑核与回滚 → `binding-rollback-design.md`**：该模块虽未在四大分层中单列，但其重要性体现在"回滚流程和实验计划"，配合编排层"明确风险、回滚方式和验证计划"的输出要求。

3. **HTML 报告输出 → `html-report-design.md`**：与编排层的"生成诊断报告"对应，强调 CPU/NPU/NUMA 拓扑关系的可视化能力与跨平台查看兼容性。

4. **专家规则层 → `diagnosis-rules.md`**：文档对应专家规则层的全部职责——问题 Taxonomy（分类体系）、证据字段（输入契约）、判断逻辑（推理规则）、建议策略（输出动作）。

5. **Agent 报告模板 → `../templates/report-template.md`**：模板位于上级目录的 `templates` 子目录，约束报告内容结构与证据表达方式，是编排层输出报告的格式约束。

6. **Snapshot 数据层 → `snapshot-schema.md`**：定义采集器、Agent、MCP 三者之间的结构化数据契约，是跨层数据流通的格式约束。

7. **采集层 → `collector-design.md`**：定义 MVP 采集器的 CLI 入口、模块划分、安全边界（只读低侵入）和失败策略，与第 2.4 节采集层的只读原则呼应。

---

## 【公式解读】

原文无公式。

---

## 【关联】

根据原文表格第 6 节「文档映射」与第 4 节「形态演进建议」建立如下关联关系：

- **上游/输入契约**：`snapshot-schema.md`（Snapshot 数据层）定义了采集器、Agent、MCP 之间的结构化数据契约，是采集层向专家规则层传递数据的格式约束。
- **横向依赖**：`diagnosis-rules.md`（专家规则层）与 `agent-workflow.md`（编排层）紧耦合——专家规则提供问题 Taxonomy 与判断逻辑，编排层负责触发与状态机推进。
- **下游输出**：`html-report-design.md` 与 `../templates/report-template.md` 共同约束编排层的报告输出，前者负责可视化结构，后者负责内容结构。
- **执行闭环**：`binding-rollback-design.md` 与编排层"明确风险、回滚方式和验证计划"形成闭环，文档映射中将其单列，表明自动绑核作为执行动作与诊断分析相对独立。
- **演进关联**：阶段 3（MCP 化）所列 7 个工具函数（`collect_cpu_topology` 等）将逐步替换阶段 1 的 MVP 脚本；阶段 4 的一键采集/分析/报告生成能力则依赖前序阶段的工具函数与 Snapshot 契约。
- **图表资产**：原文第 5 节引用三份 Mermaid 源文件——`architecture-overview.mmd`（总体架构）、`component-class-diagram.mmd`（核心组件类图）、`use-case-diagram.mmd`（用户用例图）、`data-flow-diagram.mmd`（数据流图），分别对应总体视图、静态结构、用户视角与数据流视角。

---

## 【使用方法】

原文未涉及具体的启用命令、配置项或 CLI 调用方式。仅在第 2.4 节采集层提及 MVP 采集脚本会读取 `/proc/<pid>/status`、`/proc/<pid>/task/*/status|stat|comm`、`lscpu`、`numactl -H`、cgroup cpuset/cpu quota 文件、NPU 拓扑命令、PyTorch 相关环境变量、轻量 CPU 采样工具——这些为采集层的数据来源清单而非启用方式。具体启用步骤需查阅 `collector-design.md`（采集器 CLI 定义）与 `agent-workflow.md`（端到端交互流程）。
