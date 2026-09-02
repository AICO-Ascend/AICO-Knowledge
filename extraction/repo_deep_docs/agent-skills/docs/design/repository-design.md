# Agent-Skills 代码仓设计文档

> 仓 `agent-skills` · 路径 `docs/design/repository-design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/docs/design/repository-design.md

【定位】一句话: 本文档定义 agent-skills（昇腾社区 AI 辅助研发核心管理仓库）的整体仓库结构、技能分层架构与 SKILL.md 标准化规范，并配套验证/测试机制以保障技能的可互操作与跨平台兼容。

【技术要点】
1. 仓库顶层结构（原文 §2.1）：skills/（扁平化技能目录）、docs/（含 design/、guides/、examples/）、tests/（含 test-data/、validators/、expected-results/）、scripts/validate/validate_skills.py、template/SKILL.md、README.md、.gitignore、AGENTS.md。
2. 技能目录采用"扁平化、自包含"结构（原文 §3.2）：每个 skill-name/ 下包含 SKILL.md（必需）、README.md（可选）、references/（可选，含 commands.md、examples.md）、scripts/（可选）、resources/（可选）。
3. 技能遵循外部 Agent Skills 标准（原文 §3.1）：链接为 https://agentskills.io，用于确保互操作性与跨平台兼容。
4. SKILL.md 规范（原文 §3.3）：采用 YAML frontmatter + Markdown 主体；frontmatter 至少包含 `name`（技能名）和 `description`（功能/使用场景的详细描述）两个字段。
5. 四层架构（原文 §2.2 PlantUML）：Agent Application Layer → Skill Composition Layer → Skills Layer → Foundation Layer，上层对下层为单向调用关系（app → composition，composition → skills，skills → foundation）。
6. 配套验证（原文 §2.1）：scripts/validate/validate_skills.py 作为技能验证脚本入口；tests/ 三个子目录（test-data、validators、expected-results）共同支撑技能测试闭环。

【关键机制与数据】
- 架构工作原理（原文 §2.2）：自上而下的分层调用链——应用层（app）调用组合层（composition），组合层调用技能层（skills），技能层调用基础层（foundation），形成"应用-组合-技能-基础"四级依赖。
- 标准化工作原理（原文 §3.1, §3.3）：通过统一 SKILL.md（YAML frontmatter + Markdown）作为技能的元数据与文档入口，使外部 Agent 解析器可按 agentskills.io 规范加载与发现技能。
- 验证/测试数据流（原文 §2.1）：test-data/ 作为输入 → validators/ 中的脚本执行比对 → expected-results/ 中的预期结果作为基线，三者结合 validate_skills.py 完成技能正确性校验。
- 性能数据：原文未涉及。

【表格解读】原文无表格（原文 §2.1 与 §3.2 以 ASCII 代码块形式给出"仓库目录树"和"技能目录树"两类结构示意，并非 markdown 表格，故此处按要求记为"原文无表格"，相关结构信息已在【技术要点】中逐项还原）。

【公式解读】原文无公式（全文未出现任何 LaTeX 或伪代码形式的数学/逻辑表达式；唯一出现的形式化片段是 §3.3 的 YAML frontmatter 代码块，已作为配置规范在【技术要点】与【使用方法】中说明）。

【关联】
- 模板与实例：template/SKILL.md 是新技能创建的"标准技能模板"，与 skills/*/SKILL.md 构成"模板 → 实例"关系（原文 §2.1）。
- 验证链路：scripts/validate/validate_skills.py 调用 tests/test-data/ 中的测试数据，并对照 tests/expected-results/ 中的预期结果完成验证；tests/validators/ 提供验证脚本支持（原文 §2.1）。
- 文档体系：docs/design/repository-design.md（本文件）定义总架构，docs/guides/ 提供开发指南，docs/examples/ 提供示例文档，三者形成 design → guides → examples 的文档链路（原文 §2.1）。
- 外部标准：skills/ 下所有技能的 SKILL.md 规范与外部 agentskills.io 标准保持一致（原文 §3.1），这是与昇腾社区外部生态对接的接口。
- AI 编程助手：根目录的 AGENTS.md 作为 AI 编程助手指南，与 skills/ 共同服务于"AI 辅助研发"的项目目标（原文 §2.1、§1.1）。

【使用方法】
- 技能创建：复制 template/SKILL.md 为 skills/<skill-name>/SKILL.md，并按 §3.3 填写 frontmatter 的 `name`（技能名）与 `description`（功能与使用场景的详细描述），其余可选目录（README.md、references/、scripts/、resources/）按需添加（原文 §2.1、§3.2、§3.3）。
- 技能验证：执行 scripts/validate/validate_skills.py（原文 §2.1 给出脚本路径；原文未给出具体 CLI 参数、调用方式与返回码定义）。
- 测试流程：tests/test-data/ 作为输入，运行 tests/validators/ 中的验证脚本，输出与 tests/expected-results/ 中的基线对比（原文 §2.1；原文未涉及 CI 接入方式、定时任务或触发条件）。
- 外部兼容：遵循 https://agentskills.io 标准，使技能可在遵循同一标准的外部 Agent 平台加载与发现（原文 §3.1）。
- 配置项：仅明确给出 SKILL.md frontmatter 的两个字段——`name`、`description`；原文未涉及环境变量、配置文件、开关参数等其他配置项。
