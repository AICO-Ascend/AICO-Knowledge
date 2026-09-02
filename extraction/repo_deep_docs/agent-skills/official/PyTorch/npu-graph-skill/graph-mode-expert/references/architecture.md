# NPUGRAPH_SKILL 架构设计

> 仓 `agent-skills` · 路径 `official/PyTorch/npu-graph-skill/graph-mode-expert/references/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/PyTorch/npu-graph-skill/graph-mode-expert/references/architecture.md

# NPUGRAPH_SKILL 架构设计 ── 一体化深度解读

---

## 【定位】

**一句话：本文档描述 NPUGRAPH_SKILL 这一在现有 `.npugraphs/` 技能体系之上叠加的"图模式问题诊断增强层"的架构总览——它的目标是把面向图模式（Graph Mode）的细粒度诊断（捕获/重放/内存/性能）从原有粗粒度通用能力中切分出来，并通过 MCP 自动化工具链与结构化日志/性能分析手段形成闭环。**

---

## 【技术要点】

1. **差异化定位（6 维度）**：NPUGRAPH_SKILL 与现有 `.npugraphs/` 在定位、粒度、工具链、日志、性能、输出六个维度上各有侧重——前者是"图模式问题诊断专项"，后者是"通用 NPUGraph 开发全流程"。
2. **四技能拆分体系**：将图模式问题进一步细分为四条独立技能——`graph-mode-diagnostics`（核心）、`graph-performance-profiling`、`graph-log-analyzer`、`graph-mcp-integration`，各技能下含 `SKILL.md` + `references/` 或 `patterns/` 子库。
3. **关键词驱动的技能路由**：通过中英文关键词 + ACL API 名称（如 `aclmdlRICaptureBegin`、`aclmdlRIExecuteAsync failed`）将用户问题直接路由到对应技能阶段（捕获阶段 / 重放阶段 / 内存阶段 / 性能 / 日志 / MCP 配置）。
4. **MCP 自动化 + Python 脚本双链路**：日志解析走 `scripts/parse_npu_logs.py`，图 dump 分析走 `scripts/analyze_graph_dump.py`，图健康检查走 `scripts/check_graph_health.py`；MCP 侧预定引入 `Context7`（文档查询）与 `Playwright`（Profiler 截图）、`NPU-Log-Parser`、`Graph-Dump-Analyzer` 等服务。
5. **与 `.npugraphs/` 的"互补而非替代"原则**：技能映射严格按"已有则增强、不已则独立"——`debugging`↔`graph-mode-diagnostics`、`verification`↔`graph-performance-profiling`、`torch-npu-logs-registration`↔`graph-log-analyzer`、`graph-issue-solver`↔`graph-mode-diagnostics`；`requirements/` 与 `implementation/` 明确划在 scope 之外。
6. **四阶段交付路线图**：v0.1.0 = 核心技能 + MCP 评估 + 脚本原型；v0.2.0 = MCP 实际接入（Context7 + NPU-Log-Parser）；v0.3.0 = Graph-Dump-Analyzer MCP + 性能分析脚本完善；v1.0.0 = 全量测试覆盖 + 与 `.npugraphs/` 无缝集成。

---

## 【关键机制与数据】

### 1. 设计阶段与版本基线

> 原文: "版本: v0.1.0 | 日期: 2026-06-10 | 状态: **设计阶段**"

当前文档明确处于"设计阶段"，并非可运行实现——因此文中描述的是待建系统的能力图谱与目录骨架，而不是已上线的实测数据。

### 2. 路由机制（基于关键词 + ACL API 名的硬匹配）

工作原理：**用户问题 → 关键词匹配 → 路由到对应技能**，匹配粒度精确到 ACL Runtime API 名称级别。原文给出的六组分流规则，覆盖了用户最常见的六类痛点：

- **捕获阶段**：`"图捕获失败"` / `"capture failed"` / `aclmdlRICaptureBegin` → `graph-mode-diagnostics`
- **重放阶段**：`"重放出错"` / `"replay error"` / `aclmdlRIExecuteAsync failed` → `graph-mode-diagnostics`
- **内存阶段**：`"OOM"` / `"内存泄漏"` / `"memory"` / `"allocator"` → `graph-mode-diagnostics`
- **性能**：`"慢"` / `"性能下降"` / `"regression"` / `"profile"` / `"耗时"` → `graph-performance-profiling`
- **日志分析**：`"日志分析"` / `"parse log"` / `TORCH_NPU_LOGS` → `graph-log-analyzer`
- **MCP 配置**：`"配置MCP"` / `"setup mcp"` / `"mcp工具"` → `graph-mcp-integration`
- **兜底**：模糊/综合问题统一回落到 `graph-mode-diagnostics`（全流程）。

> 原文: "模糊/综合问题 → graph-mode-diagnostics (全流程)"。

### 3. 三阶段级联数据流

> 原文给出如下数据流：
> - 用户报告问题 → `graph-mode-diagnostics`
> - 需要日志分析 → `graph-log-analyzer` → `scripts/parse_npu_logs.py` → **结构化日志报告**
> - 需要性能分析 → `graph-performance-profiling` → MCP: Playwright → **Profiler 截图** → **性能分析报告**
> - 终点：输出 **综合诊断报告 + 修复建议 + 验证步骤**

文档还指出诊断主技能可走 `MCP: Context7` 查询 CANN/PyTorch 文档，形成"代码上下文 + 日志 + 性能"三源汇流。

### 4. 性能数据

> 原文: **无任何运行时性能数字**（如时延、吞吐、加速比等）。原文仅出现与"性能"相关的概念性术语（"性能下降"、"耗时"、"baseline-metrics"）。

### 5. 关键 API / 环境变量锚点

> 原文出现的 ACL Runtime API：`aclmdlRICaptureBegin`、`aclmdlRIExecuteAsync`（用于路由匹配）。
> 环境变量锚点：`TORCH_NPU_LOGS`（用于触发日志分析技能）。

---

## 【表格解读】

### 表 1｜设计目标差异化矩阵（6 维度 × 2 系统）

| 维度 | .npugraphs/ (现有) | NPUGRAPH_SKILL (本系统) |
|------|-------------------|------------------------|
| **定位** | 通用 NPUGraph 开发全流程 | 图模式**问题诊断**专项 |
| **粒度** | 粗粒度（debugging/requirements 覆盖所有） | 细粒度（捕获/重放/内存/性能 分技能） |
| **工具链** | 依赖 Bash 手动执行 | MCP 自动化 + Python 脚本 |
| **日志** | 手动 grep | 结构化解析 + 模式匹配 |
| **性能** | 不在 scope 内 | 独立性能分析技能 |
| **输出** | Markdown 报告 | 结构化报告 + Timeline 可视化 |

**逐行解读：**

- **定位行**：明确两者不是取代关系，而是"全流程 vs 专项"——`.npugraphs/` 仍负责端到端开发，本系统专攻"图模式问题"这一窄域。
- **粒度行**：核心创新点——把单一 `debugging/` 技能按"捕获/重放/内存/性能"四象限拆细，每个技能有独立 `SKILL.md`，并配套 `references/` 或 `patterns/` 子库。
- **工具链行**：从"依赖 Bash 手动执行"升级为"MCP 自动化 + Python 脚本"双轨——意味着技能可调用 MCP 工具，而非纯文本指令。
- **日志行**：从"手动 grep"升级为"结构化解析 + 模式匹配"——即 `scripts/parse_npu_logs.py` 输出的"结构化日志报告"。
- **性能行**：`.npugraphs/` 明确将"性能"排除在外，本系统设独立 `graph-performance-profiling` 技能填补缺口，并通过 `baseline-metrics.md` 沉淀指标基线。
- **输出行**：从纯 Markdown 升级到"结构化报告 + Timeline 可视化"——Timeline 是新增能力，对应 `graph-log-analyzer/patterns/timeline-patterns.md`。

### 表 2｜扩展计划路线图（v0.1.0 → v1.0.0）

| 版本 | 内容 |
|------|------|
| v0.1.0 | 核心技能定义 + MCP 评估 + 脚本原型 |
| v0.2.0 | MCP 实际集成（Context7 + NPU-Log-Parser） |
| v0.3.0 | Graph-Dump-Analyzer MCP + 性能分析脚本完善 |
| v1.0.0 | 全量测试覆盖 + 与 .npugraphs/ 无缝集成 |

**逐行解读：**

- **v0.1.0**（当前文档所处的版本）：聚焦"设计"，产出"核心技能定义 + MCP 评估 + 脚本原型"三件套——这与目录结构中 `DOC/` 与 `scripts/` 的存在呼应。
- **v0.2.0**：从"评估"切换到"实际集成"，明确点名 MCP 工具——`Context7`（用于查阅 CANN/PyTorch 文档，与数据流图一致）与 `NPU-Log-Parser`（用于替代/补充本地的 `parse_npu_logs.py`）。
- **v0.3.0**：进一步引入 `Graph-Dump-Analyzer MCP`，与目录中 `scripts/analyze_graph_dump.py` 形成 MCP+脚本双形态；同时"性能分析脚本完善"对应 `graph-performance-profiling/references/profiling-methodology.md` 与 `baseline-metrics.md` 的细化。
- **v1.0.0**：终态——"全量测试覆盖"意味着从原型转生产，"与 .npugraphs/ 无缝集成"则把第 4 节的"互补关系"变成运行时可协同的交付。

### 表 3｜.npugraphs/ 与 NPUGRAPH_SKILL 技能映射（6 组）

| .npugraphs/skills/ | NPUGRAPH_SKILL/SKILL/ | 关系 |
|---|---|---|
| debugging/ | graph-mode-diagnostics/ | 互补增强（←→） |
| requirements/ | （独立） | 独立（需求分析不在此系统 scope） |
| implementation/ | （独立） | 独立（编码实现不在此系统 scope） |
| verification/ | graph-performance-profiling/ | 验证阶段增强（←→） |
| torch-npu-logs-registration/ | graph-log-analyzer/ | 日志分析互补（←→） |
| graph-issue-solver/ | graph-mode-diagnostics/ | 问题单求解互补（←→） |

**逐行解读：**

- `debugging/` 与 `graph-mode-diagnostics/` 是最核心的"双向增强"对——前者覆盖开发期通用 debug，后者覆盖运行期 graph-mode 专项诊断，避免重复造轮子。
- `requirements/` 与 `implementation/` **明确不在本系统 scope**——这条边界很重要，意味着用户做需求/编码时不会被错误路由到本系统的四个技能。
- `verification/` ↔ `graph-performance-profiling/` 是另一条关键增强——`.npugraphs/` 做功能验证，本系统做性能验证。
- `torch-npu-logs-registration/` ↔ `graph-log-analyzer/` 把"日志注册配置"与"日志内容分析"切开，前者在 `.npugraphs/`，后者在本系统。
- `graph-issue-solver/` ↔ `graph-mode-diagnostics/` 表明：广义 issue solver 留在 `.npugraphs/`，图模式专项求解转交本系统。

---

## 【公式解读】

**原文无公式**。文中 `parse_npu_logs.py` 等脚本虽可能涉及统计/聚合逻辑，但原文未给出任何数学表达式、LaTeX 公式或伪代码推导。

---

## 【关联】

文档内部明确给出 3 类关联，且内部链接清单为"（无）"。以下关联全部基于原文目录与第 4 节原文映射重构：

### 1. 技能内部关联（4 条技能 + 共享资产）

- **共享文档**：`NPUGRAPH_SKILL_DOC.md`（同级总入口）、`DOC/architecture.md`（本文件）、`DOC/mcp-evaluation.md`、`DOC/skill-design.md` 为全部四条技能的设计公共层。
- **`graph-mode-diagnostics`** 下含三个 references：`known-patterns.md`（已知问题模式扩展版）、`error-code-map.md`（ACL 错误码 → 根因映射）、`diagnostic-checklist.md`（诊断检查清单）。
- **`graph-performance-profiling`** 下含两个 references：`profiling-methodology.md`、`baseline-metrics.md`——后者承担"性能基线"职能，配合 v0.3.0 的脚本完善。
- **`graph-log-analyzer`** 下含三个 patterns：`error-patterns.md`、`timeline-patterns.md`、`memory-patterns.md`——三套模式与第 3 节"捕获/重放/内存"三阶段一一映射。
- **`graph-mcp-integration`** 仅一个 `SKILL.md`，被 `MCP/setup-guide.md` 与 `MCP/mcp-configs.json` 引用。

### 2. 上下游关联（与 `.npugraphs/` 的双向增强）

见上"表 3 解读"——`debugging/`、`verification/`、`torch-npu-logs-registration/`、`graph-issue-solver/` 四条 `.npugraphs/` 技能与本系统的对应技能形成"互补增强"；`requirements/`、`implementation/` 划在 scope 之外。

### 3. 工具/数据源关联

- **`MCP/mcp-configs.json` + `MCP/setup-guide.md`**：作为 MCP 集成的配置入口，被 `graph-mcp-integration/SKILL.md` 引用，并支撑数据流图中 `Context7` 与 `Playwright` 两种 MCP server。
- **`scripts/parse_npu_logs.py`**：被 `graph-log-analyzer` 调用，输入为 `TORCH_NPU_LOGS` 触发的 NPU 日志，输出为"结构化日志报告"。
- **`scripts/analyze_graph_dump.py`**：对应 v0.3.0 的 `Graph-Dump-Analyzer MCP`，承担图 dump 分析职责。
- **`scripts/check_graph_health.py`**：作为图健康检查通用入口，可能被 `graph-mode-diagnostics` 调用以给出"全流程"兜底诊断。

---

## 【使用方法】

> 原文未提供具体启用命令或客户端配置示例。以下仅整理**原文出现**的启用信号与配置项：

### 1. 触发技能——通过用户提问中的关键词（原文第 3 节）

| 用户输入关键词（节选） | 目标技能 |
|---|---|
| "图捕获失败" / "capture failed" / `aclmdlRICaptureBegin` | graph-mode-diagnostics（捕获阶段） |
| "重放出错" / "replay error" / `aclmdlRIExecuteAsync failed` | graph-mode-diagnostics（重放阶段） |
| "OOM" / "内存泄漏" / "memory" / "allocator" | graph-mode-diagnostics（内存阶段） |
| "慢" / "性能下降" / "regression" / "profile" / "耗时" | graph-performance-profiling |
| "日志分析" / "parse log" / `TORCH_NPU_LOGS` | graph-log-analyzer |
| "配置MCP" / "setup mcp" / "mcp工具" | graph-mcp-integration |
| 模糊/综合问题 | graph-mode-diagnostics（全流程，兜底） |

### 2. 启用 MCP 集成（原文仅提及未给配置示例）

> 原文: "MCP: Context7"（数据流图）、"MCP: Playwright"（数据流图）、v0.2.0 计划 "MCP 实际集成（Context7 + NPU-Log-Parser）"、v0.3.0 "Graph-Dump-Analyzer MCP"。

**具体 MCP server 端口、URL、鉴权字段原文未涉及**——配置入口集中在 `MCP/mcp-configs.json` 与 `MCP/setup-guide.md`，当前未在文档中展开。

### 3. 调用脚本（原文给出的命令入口）

| 脚本路径 | 用途 |
|---|---|
| `scripts/parse_npu_logs.py` | NPU 日志解析器，输出结构化日志报告 |
| `scripts/analyze_graph_dump.py` | 图 dump 分析器 |
| `scripts/check_graph_health.py` | 图健康检查 |

> 原文未给出 `python scripts/parse_npu_logs.py --xxx` 形式的命令行参数样板。

### 4. 版本/启用状态校验

> 原文: 文档版本 **v0.1.0**、日期 **2026-06-10**、状态 **设计阶段**——意味着当前不建议在生产环境启用，应以 v1.0.0（"全量测试覆盖 + 与 .npugraphs/ 无缝集成"）为最终启用标志。

---

> **解读约束声明**：本文中所有时间/数字/名词均来自原文，未自行补充任何数据；文档处于"设计阶段"且原文给出无内部链接，故"关联"与"使用方法"两节仅在原文信息边界内还原。
