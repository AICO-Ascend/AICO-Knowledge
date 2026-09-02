# 技能设计原理

> 仓 `agent-skills` · 路径 `official/PyTorch/npu-graph-skill/graph-mode-expert/references/skill-design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/PyTorch/npu-graph-skill/graph-mode-expert/references/skill-design.md

# 一体化深度解读：NPUGRAPH_SKILL 技能设计原理

---

## 【定位】

本文档系统阐述了 NPUGRAPH_SKILL（即 npu-graph-skill）中各技能的设计原则、关键决策、与已有 `.npugraphs/` 体系的差异以及尚未敲定的待办事项，本质是一份**"为什么这样设计"的设计权衡记录**，用于约束后续技能开发保持架构一致性。

---

## 【技术要点】

1. **不重复原则（PR-001）**：`.npugraphs/` 已有的能力（如 `implementation` TDD 编码、`code-analysis` 源码分析、`requirements` 需求设计），NPUGRAPH_SKILL 一律不重复建设，仅做 `.npugraphs/` 未覆盖的"图模式"专项能力。

2. **单文件核心 + 参考资料分离（PR-002）**：每个技能的**核心逻辑必须自包含在 `SKILL.md`** 中，可被 Claude Code 直接加载进上下文；详细参考资料放在 `references/` 子目录按需读取。

3. **脚本优先于手动操作（PR-003）**：能用 Python 脚本自动化完成的操作，必须以 `python scripts/xxx.py` 形式标注，禁止使用 `grep | awk | sort` 这类 Bash 管道拼接；脚本须满足可测试、可复用、可被 MCP 包装三个条件。

4. **结构化输出（PR-004）**：技能输出必须携带明确字段（Phase、时间线、错误码），且支持 JSON 序列化，为后续 MCP 集成和跨技能数据传递预留接口。

5. **5 阶段诊断流程**：`graph-mode-diagnostics` 采用「分类 → 定位 → 模式 → 追踪 → 报告」5 阶段，阶段划分严格对标图执行生命周期（Capture / Replay / Memory / Update / Compile），诊断**不含修复**，修复一律 handoff 到 `implementation`（遵循 Iron Law：先定位再修复）。

6. **P99 指标 + 10 次 warmup**：`graph-performance-profiling` 采用 P50/P99 而非 mean/std 进行性能对比，且对比基准强制采用"同脚本两次运行再对比"以规避跨环境差异（CANN 版本等），warmup 默认 **10 次**以消除首次编译开销。

---

## 【关键机制与数据】

**诊断 5 阶段工作流**（原文：分类→定位→模式→追踪→报告）：第一阶段做问题分类，第二阶段定位到具体模块，第三阶段匹配已知模式，第四阶段追踪数据流，第五阶段产出报告。这 5 个阶段一一对应图执行的 5 个生命周期（Capture / Replay / Memory / Update / Compile），形成"问题域 ↔ 执行域"的双向映射。

**异常检测演进路径**（原文：v0.1.0 用正则足够，v2.0 可升级 ML）：`graph-log-analyzer` 当前以正则匹配为核心进行异常检测，预留 ML 升级通道；模式命名采用 E-/T-/M- 三系列前缀——E 代表 Error（错误）、T 代表 Timeline（时间线）、M 代表 Memory（内存），三系列可独立无限扩展。

**MCP 启用优先级**（原文：Context7 → NPU-Log-Parser → Playwright → 其他）：先接入速度最快的文档查询 MCP（Context7），再自建核心工具（NPU-Log-Parser），最后接入浏览器自动化（Playwright），其余 MCP 排到最后；自建 MCP 采用 **Python stdio 协议**，与 Claude Code MCP 客户端兼容。

**资源规模统计**（原文：4 个 MCP 推荐 + 3 个自建；`scripts/` 含 3 个 Python 脚本）：NPUGRAPH_SKILL 在 MCP 集成和脚本化程度上均显著多于 `.npugraphs/` 体系。

---

## 【表格解读】

### 表 1：graph-mode-diagnostics 决策表

| 决策点 | 选择 | 原因 |
|--------|------|------|
| 诊断流程 | 5 阶段（分类→定位→模式→追踪→报告） | 继承自 `.npugraphs/debugging`，保持一致 |
| 阶段划分 | Capture / Replay / Memory / Update / Compile | 对标图执行生命周期 |
| 是否含修复 | 否（handoff 到 implementation） | 遵循 Iron Law：先定位再修复 |

**逐行解读：**
- **诊断流程行**：明确"分类→定位→模式→追踪→报告"为线性 5 步流程，且该流程是**直接继承**自已有的 `.npugraphs/debugging`，避免在体系内出现两套互不兼容的诊断范式。
- **阶段划分行**：将图执行生命周期拆为 Capture / Replay / Memory / Update / Compile 五个对象，每个诊断阶段对应一个生命周期切片，便于问题归属判定。
- **是否含修复行**：明确"诊断 ≠ 修复"，一旦定位到根因即交棒给 `implementation` 技能处理，体现"先定位再修复"的工程纪律（Iron Law）。

### 表 2：graph-performance-profiling 决策表

| 决策点 | 选择 | 原因 |
|--------|------|------|
| 指标选用 | P50/P99 而非 mean/std | 性能分析的标准实践，P99 更反映长尾 |
| 对比方式 | 同脚本两次运行再对比 | 避免跨环境差异（CANN 版本等） |
| warmup 次数 | 默认 10 次 | 足够消除首次编译开销 |

**逐行解读：**
- **指标选用行**：选用 P50（中位数）和 P99（99 分位数）替代传统的均值与标准差，是因为性能问题常常被均值掩盖，而 P99 才是真实长尾瓶颈的反映。
- **对比方式行**：性能对比必须"同脚本两次运行"——即在**同一环境**中跑两次取差值，规避硬件差异、CANN 版本差异、驱动差异等外部干扰。
- **warmup 次数行**：warmup 默认 10 次，依据是"足够消除首次编译开销"，既不过度（避免浪费）也不不足（避免误判）。

### 表 3：graph-log-analyzer 决策表

| 决策点 | 选择 | 原因 |
|--------|------|------|
| 模式命名 | E-/T-/M- 三系列 | E=错误, T=时间线, M=内存，可以无限扩展 |
| 解析器实现 | Python 而非 Bash | 支持流式处理、JSON 输出、可 MCP 化 |
| 异常检测 | 正则匹配 + 后续 ML | v0.1.0 用正则足够，v2.0 可升级 ML |

**逐行解读：**
- **模式命名行**：E-/T-/M- 三前缀构成一个**可水平扩展**的命名空间，E 表示错误类模式、T 表示时间线相关、M 表示内存相关，新增模式只需在同一前缀下追加，不破坏既有命名。
- **解析器实现行**：选 Python 而非 Bash 的核心理由是**流式处理**（Bash 难以做到）、**JSON 输出**（为 MCP 集成铺路）、**可 MCP 化**（Bash 进程难以包装为 MCP server）。
- **异常检测行**：明确分阶段演进策略——v0.1.0 阶段正则匹配已足够覆盖常见错误日志，待日志规模和模式复杂度提升后再升级到 ML 模型，避免过度设计。

### 表 4：graph-mcp-integration 决策表

| 决策点 | 选择 | 原因 |
|--------|------|------|
| MCP 启用顺序 | Context7 → NPU-Log-Parser → Playwright → 其他 | 先启用最快的（文档查询），再自建核心工具 |
| 自建 MCP | Python stdio 协议 | 开发简单，与 Claude Code MCP 客户端兼容 |

**逐行解读：**
- **MCP 启用顺序行**：四个 MCP 按"价值-成本"递进——Context7 用于文档查询（接入最快、即时见效），NPU-Log-Parser 是核心工具（需自建但价值最高），Playwright 提供浏览器自动化（复杂度更高），其他 MCP 放在最后。
- **自建 MCP 行**：采用 Python stdio 协议实现自建 MCP，理由是"开发简单"和"与 Claude Code MCP 客户端兼容"，避免引入额外网络协议栈。

### 表 5：NPUGRAPH_SKILL 与 `.npugraphs/` 差异对比表

| 维度 | .npugraphs/ | NPUGRAPH_SKILL |
|------|------------|----------------|
| 语言 | 英文为主 | 中文为主（面向中文团队） |
| 触发方式 | `/command` slash 命令 | 关键词 + 上下文匹配 |
| MCP 集成 | 无 | 4 个 MCP 推荐 + 3 个自建 |
| 脚本 | 无独立脚本目录 | `scripts/` 含 3 个 Python 脚本 |
| 分发方式 | 复制 `.npugraphs/` 目录 | 需额外复制 `NPUGRAPH_SKILL/` 和 `NPUGRAPH_SKILL_DOC.md` |

**逐行解读：**
- **语言行**：`.npugraphs/` 面向英文团队，NPUGRAPH_SKILL 主语言切换为中文，体现对中文研发团队的本地化适配。
- **触发方式行**：`.npugraphs/` 采用显式 `/command` slash 命令触发，NPUGRAPH_SKILL 改用关键词 + 上下文匹配触发，降低了用户记忆成本。
- **MCP 集成行**：NPUGRAPH_SKILL 显著强化了 MCP 集成（4 推荐 + 3 自建 = 7 个 MCP），而 `.npugraphs/` 此项为"无"，这是两个体系最大的能力差异。
- **脚本行**：NPUGRAPH_SKILL 专设 `scripts/` 目录存放 3 个 Python 脚本，与 PR-003"脚本优先"原则相呼应；`.npugraphs/` 则无独立脚本目录。
- **分发方式行**：`.npugraphs/` 只需复制单一目录，NPUGRAPH_SKILL 需要同时复制 `NPUGRAPH_SKILL/` 和 `NPUGRAPH_SKILL_DOC.md` 两部分，部署门槛更高。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档作为 NPUGRAPH_SKILL 的设计元文档，与体系中其他组件存在如下关联：

1. **与 `.npugraphs/` 体系的关系**：NPUGRAPH_SKILL 是 `.npugraphs/` 的**增量补充**而非替代——所有 `.npugraphs/` 已覆盖能力（`implementation`、`code-analysis`、`requirements`、`debugging` 等）NPUGRAPH_SKILL 均不再重复建设，并通过"诊断流程继承自 `.npugraphs/debugging`"明确继承关系。

2. **`graph-mode-diagnostics` ↔ `implementation`**：诊断技能严格遵循"只诊断、不修复"的边界，定位完成后必须通过 handoff 机制将修复任务移交 `implementation`（位于 `.npugraphs/` 中），形成"诊断  修复"的上下游串联。

3. **`graph-log-analyzer` ↔ `graph-mcp-integration`**：日志分析技能与 MCP 集成技能存在**演进关系**——日志解析器在 PR-003/PR-004 指导下使用 Python 实现并输出 JSON，正是为了后续被包装为 MCP 服务；MCP 启用顺序中"先自建核心工具 NPU-Log-Parser"正指向此处的解析器。

4. **`graph-mode-diagnostics` 5 阶段 ↔ 图执行生命周期**：诊断的 5 个阶段（分类→定位→模式→追踪→报告）与图执行的 5 个生命周期（Capture / Replay / Memory / Update / Compile）形成**双向映射**，任何诊断输出都可在执行生命周期中精准定位。

5. **NPUGRAPH_SKILL_DOC.md**：与本设计文档并列的随仓库分发的文档，与 `NPUGRAPH_SKILL/` 目录共同构成分发单元（见表格第 5 行）。

6. **`.npugraphs/install.sh`**：作为待决策事项中的参考模式，NPUGRAPH_SKILL 未来若引入 Cursor rule 安装需求，将沿用 `.npugraphs/install.sh` 的脚本化安装范式。

---

## 【使用方法】

原文未涉及启用方式、配置项或命令。本文档为**设计元文档**（meta-document），其作用是为后续技能开发者提供决策依据与约束规则，本身不可作为技能被调用，也未提供任何运行时开关、配置参数或 CLI 命令。
