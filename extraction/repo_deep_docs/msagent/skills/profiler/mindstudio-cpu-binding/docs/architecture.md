# 架构设计

> 仓 `msagent` · 路径 `skills/profiler/mindstudio-cpu-binding/docs/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msagent/skills/profiler/mindstudio-cpu-binding/docs/architecture.md

# `mindstudio-cpu-binding` 架构设计文档一体化深度解读

## 【定位】

本文档解决"如何为 MindStudio 智能体的 CPU 绑核诊断能力设计一套可演进的分层架构"的问题，描述从 MVP 阶段（脚本+快照+Agent 提示词）到最终形态（独立 Agent/Plugin）的四阶段形态演进路径与各层组件职责。

## 【技术要点】

1. **四层分层架构**：自顶向下分为 Agent 交互与编排层、专家规则层、Snapshot 数据层、采集层；明确"第一阶段建议采用分层架构，不直接绑定某一种最终形态"。
2. **MVP 交付五件套**：可运行采集脚本 + Snapshot JSON + Agent 分析提示词/Skill + 报告模板 + 示例报告，强调"不需要一开始搭建完整 MCP 或 Plugin"。
3. **采集源限定为只读、低侵入**：列出 `/proc/<pid>/status`、`/proc/<pid>/task/*/status`、`/proc/<pid>/task/*/stat`、`/proc/<pid>/task/*/comm`、`lscpu`、`numactl -H`、cgroup cpuset/cpu quota 文件、NPU 拓扑命令或平台适配器、PyTorch 相关环境变量、轻量 CPU 采样工具。
4. **Agent 最小必要询问字段**：训练/推理、PID、NPU 设备、rank 映射、环境类型、优化目标。
5. **专家规则八大类**：未绑核判断、跨 NUMA 判断、Rank/NPU/NUMA 不匹配判断、可用 CPU 数与线程数不匹配判断、PyTorch DataLoader/intra-op/inter-op/OpenMP 线程配置建议、多 rank/多实例 CPU range 冲突判断、latency 与 throughput 目标下的 SMT 使用策略。
6. **四阶段演进路线**：阶段 1（脚本+文档+Agent Prompt，3-5 个真实/脱敏案例）→ 阶段 2（Skill 化，固定问题分类与报告结构）→ 阶段 3（MCP 化，7 个工具函数）→ 阶段 4（独立 Agent/Plugin，含一键采集与对比）。

## 【关键机制与数据】

- **原文工作机制**：Agent 层通过询问"训练/推理、PID、NPU 设备、rank 映射、环境类型、优化目标"这一组最小必要信息触发采集流程；采集层产出只读的 Snapshot，Snapshot 数据层对 Agent 屏蔽命令差异并承接采集结果；专家规则层基于 Snapshot 进行诊断并生成保守方案与进阶方案；Agent 层同时输出风险、回滚方式和验证计划。
- **原文数据流约束**：Snapshot 必须覆盖系统拓扑、NPU 拓扑、进程线程信息、cgroup/cpuset 限制、PyTorch 环境变量与运行配置、CPU 使用率和线程 TopN 采样——这六个数据域是 Agent 屏蔽命令差异后直接消费的契约字段。
- **原文性能/数值数据**：文档未提供任何具体的性能基准数字、延迟/吞吐数值或绑核前后对比指标（原文未涉及）。

## 【表格解读】

原文第 6 节"文档映射"表格逐字还原如下：

| 架构部分 | 对应文档 | 说明 |
|----------|----------|------|
| Agent 交互与编排层 | `agent-workflow.md` | 定义端到端交互、采集、诊断、报告、验证和状态机。 |
| 自动绑核与回滚 | `binding-rollback-design.md` | 定义执行后端、rollback-state、回滚流程和实验计划。 |
| HTML 报告输出 | `html-report-design.md` | 定义 HTML 页面结构、CPU/NPU/NUMA 拓扑关系可视化和跨平台查看要求。 |
| 专家规则层 | `diagnosis-rules.md` | 定义问题 Taxonomy、证据字段、判断逻辑和建议策略。 |
| Agent 报告模板 | `../templates/report-template.md` | 约束诊断报告内容结构和证据表达方式。 |
| Snapshot 数据层 | `snapshot-schema.md` | 定义采集器、Agent、MCP 之间的结构化数据契约。 |
| 采集层 | `collector-design.md` | 定义 MVP 采集器 CLI、模块、安全边界和失败策略。 |

逐行解读：
- **Agent 交互与编排层 → agent-workflow.md**：将第 2.1 节所述"询问→采集→诊断→报告→验证"的端到端流程落到状态机定义，是交互层的可执行规约。
- **自动绑核与回滚 → binding-rollback-design.md**：架构总览未独立列"绑核执行"层，但该映射行说明执行后端与 rollback-state 是与四层并列存在的横切能力，对应阶段 4 的"可选的安全应用与回滚"。
- **HTML 报告输出 → html-report-design.md**：将"生成诊断报告"进一步细化为 HTML 形态，并要求 CPU/NPU/NUMA 拓扑关系可视化与跨平台查看，属于报告层的呈现约束。
- **专家规则层 → diagnosis-rules.md**：对应第 2.2 节八大类专家经验，将"未绑核/跨 NUMA/Rank 冲突/线程配置/SMT 策略"等经验抽象为问题 Taxonomy、证据字段、判断逻辑、建议策略四要素。
- **Agent 报告模板 → ../templates/report-template.md**：在第 3 节 MVP 五件套中明确要求"报告模板固定后，专家可以快速 review 输出质量"，此处给出模板文件位置以约束证据表达方式。
- **Snapshot 数据层 → snapshot-schema.md**：对应第 2.3 节六大数据域，将系统拓扑/NPU 拓扑/进程线程/cgroup/PyTorch 配置/CPU 采样固化为采集器、Agent、MCP 之间的结构化契约，是阶段 3 MCP 化（第 4 节列出的 7 个工具函数）能平滑替换的前提。
- **采集层 → collector-design.md**：对应第 2.4 节只读、低侵入的采集源清单，给出 MVP 采集器 CLI、模块、安全边界和失败策略，呼应"采集结果结构化后，后续可以平滑替换成 MCP"的演进诉求。

## 【公式解读】

原文无公式。

## 【关联】

文档通过第 6 节"文档映射"表与同目录下的 6 份姊妹文档建立强耦合：

- **横向（层内细化）**：四层架构中的每一层都对应一份独立的设计文档——Agent 交互层→`agent-workflow.md`、专家规则层→`diagnosis-rules.md`、Snapshot 数据层→`snapshot-schema.md`、采集层→`collector-design.md`，架构文档仅描述职责边界，具体交互、规则、契约、采集细节下沉到对应文档。
- **纵向（能力扩展）**：`binding-rollback-design.md` 与 `html-report-design.md` 是四层架构之外的横切能力，分别承担"执行后端+回滚"与"HTML 报告可视化"，与第 2.1 节中"明确风险、回滚方式和验证计划"以及"生成诊断报告"的能力相对应。
- **演进闭环**：阶段 1（脚本+Prompt）依赖 `collector-design.md`、`snapshot-schema.md`、`report-template.md` 三者作为脚手架；阶段 3（MCP 化）将采集层升级为 `collect_cpu_topology` / `collect_npu_topology` / `collect_process_affinity` / `collect_cgroup_limits` / `collect_runtime_config` / `collect_cpu_runtime_sample` / `generate_affinity_plan` 七个工具，对应采集层与 Snapshot 数据层的契约扩展。
- **外部资产**：第 1、5 节分别引用 `../assets/architecture-overview.mmd`、`../assets/component-class-diagram.mmd`、`../assets/use-case-diagram.mmd`、`../assets/data-flow-diagram.mmd` 四份 Mermaid 源文件，分别承担总体架构图、核心组件类图、用户用例图、数据流图的图形化呈现，与正文的层级与组件叙述互为补充。
- **报告模板**：通过 `../templates/report-template.md` 与第 3 节 MVP 五件套中的"报告模板"形成引用闭环，确保阶段 2 Skill 化与阶段 4 Agent 化沿用同一证据表达规范。

## 【使用方法】

原文未提供具体的启用命令、配置项或 API 调用示例。文档以架构选型、组件职责与演进路线为主，仅在第 3 节以代码块形式给出 MVP 的交付物清单：

```text
可运行采集脚本 + Snapshot JSON + Agent 分析提示词/Skill + 报告模板 + 示例报告
```

阶段 3 提及的 MCP 工具函数名（`collect_cpu_topology`、`collect_npu_topology`、`collect_process_affinity`、`collect_cgroup_limits`、`collect_runtime_config`、`collect_cpu_runtime_sample`、`generate_affinity_plan`）属于交付物名称而非启用方式，原文未涉及具体调用命令或参数。
