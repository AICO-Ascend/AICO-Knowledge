# Release Notes

> 仓 `model-agent` · 路径 `Release_notes/RELEASE_NOTES_v1.0.0.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/model-agent/Release_notes/RELEASE_NOTES_v1.0.0.md

```markdown
# Release Notes v1.0.0 — 一体化深度解读

## 【定位】
本文档记录 model-agent v1.0.0 (2026.06.30) 一次**重大架构升级**的变更清单: 后端从一个"OpenAI 兼容的聊天代理"重塑为"具备动态工作流编排、自进化经验引擎与 MCP 集成的全功能模型优化框架", 并将底层 LLM 提供方由 MiniMax/MoonShot 切到 Anthropic Claude。

---

## 【技术要点】

1. **静态→动态工作流引擎**: 替换旧的"关键字 intent resolver", 引入 DAG 式的 `DynamicPlanner` + `WorkflowExecutor`, 支持 LLM 生成的执行计划、并行步骤、可配置 retry、checkpoint/restore (基于 LangGraph `MemorySaver`) 以及基于 `asyncio.Queue` + `progress_callback` 的 SSE 实时进度流。
2. **Hermes 自进化经验引擎** (`app/tools/experience/`): 由 `ExperienceStore` (基于 `memory.jsonl`、`skills.json`、`insights.jsonl` 持久化, 含原子写与版本化) + `MemoryEngine` (语义检索) + `SkillEngine` (抽取/版本化/应用技能) + `NudgeEngine` (主动提示) + 可插拔 `layers/` (错误恢复、MCP 优化、模型适配、用户偏好) 构成, 并暴露 `/experience` (状态自省) 与 `/learn` (用户教学) 两个新命令。
3. **MCP (Model Context Protocol) 集成**: `app/tools/workflow/mcp_integration.py` 提供 MCP server 生命周期管理, 在应用启动时 auto-startup, 关闭时 graceful shutdown; 服务器实现包含 `cannbot_server.py` (stdio transport, **316 行**实现) 与 `ms_agent_server.py`/`ms_agent_runner.py`; 工作流步骤可直接调用 MCP 工具。
4. **LLM 提供方迁移 + 运行时热更新**: 从 MiniMax/MoonShot (OpenAI 兼容) 切换到 Anthropic Claude; 新增 `/v1/chat/config` 接口用于运行时更新模型配置, 配合 runtime LLM key rotation, **无需重启服务**即可注入新的 Anthropic access token。
5. **PTA Agent** (`/pta`): 专用于 `torch_npu` 开发的 PyTorch-Ascend 代理, 基于 `thread_id` 的多轮对话记忆, 含历史上下文组装与每轮持久化。
6. **可观测性与工程化增强**: 新增 `trace_id` 在请求生命周期内的端到端透传、Claude Code 工具调用 tracing、heartbeat monitoring; `.github/workflows/ci.yml` CI 含 lint + unit + integration 三阶段; `requirements-dev.txt` 引入 `pytest`、`pytest-asyncio`、`pytest-cov`、`ruff`; 默认模型下载路径配置面向 Ascend NPU。

---

## 【关键机制与数据】

### 工作流调度机制 (原文)
- **DAG 计划生成**: `DynamicPlanner` 基于 LLM 输出多步计划, 含**依赖解析**、**并行路径的交叉验证**、**自适应目标分解**。
- **执行机制**: `WorkflowExecutor` 含**并行步骤执行**、**可配置 retry**、**通过 LangGraph `MemorySaver` 做 checkpoint/restore**、**最大并发度控制**。
- **进度流**: 通过 `asyncio.Queue` + `progress_callback` 提供**每步骤状态更新**的 SSE 实时进度。
- **Brainstorming** (`brainstorming.py`): 多轮意图澄清, 含**渐进式问题生成**、**歧义评估**、**proposal 跟踪**、**design-doc 输出**, 并修复了"LLM 可能陷入无限澄清循环"的缺陷 (新增 max-round guard + 收敛检测)。

### 经验引擎机制 (原文)
- **存储**: `memory.jsonl`、`skills.json`、`insights.jsonl`, 采用**原子写**与**版本化**。
- **检索**: `MemoryEngine` 提供**基于当前上下文的语义检索**找到相关历史经验。
- **触发**: `NudgeEngine` 通过**模式匹配历史经验**给出主动优化建议。
- **可插拔层**: `layers/` 涵盖 **error recovery**、**MCP optimization**、**model adaptation**、**user preferences** 四类适配能力。

### MCP 集成机制 (原文)
- **生命周期**: 由 `app/tools/workflow/mcp_integration.py` 中的 MCP server 生命周期管理器统一管理, 在**应用启动时 auto-startup**, **关闭时 graceful shutdown**。
- **传输/集成**: Cannbot Server 使用 **stdio transport**; MS Agent Server 用于外部 agent 工具调用; **工作流步骤可调用 MCP server 完成领域特定操作**。
- **关键数据 (原文)**: Cannbot Server 实现为 **316 行**。

### 启动生命周期 (原文)
- 在 `app/main.py` 的应用 lifespan 阶段依次初始化: **eval logging patching**、**MCP manager**、**Hermes engine**、**Claude Code history watcher**。
- 外部 agent (search-agent、pta-agent) **改为启动时 clone**, 不再随仓库持久化, 以保证部署清洁。

### 流式输出与超时保护 (原文)
- **新增 `_aiter_with_timeout` 辅助函数**: 原因是 `asyncio.wait_for` **不能直接包 async generator**, 故自行实现对流式生成器的超时包装。
- **新增 `_CLAUDE_SKILL_TIMEOUT` 默认值**, 用于防止 skill 调用挂起。
- Claude Code 响应流经**分块与进度报告**优化。

### 代码清理数据 (原文)
- 移除 **96 个** `kernel_meta/` 文件 (Ascend 编译缓存);
- 移除 **40+ 个** `__pycache__/` 目录与编译 `.pyc`;
- `tmp/` 目录中有 **20 个**未被应用代码引用的测试/演示脚本;
- `server.log` 体积 **7MB+**;
- 修复 **9 个 SKILL.md** 文件中硬编码的个人 home 目录路径, 替换为 `~` (Unix home) 与相对路径, 同时**保留标准昇腾 NPU 工具链路径** (`/home/Ascend/ascend-toolkit/`、`/usr/local/Ascend/`)。

### 可观测性 (原文)
- **请求生命周期内透传 `trace_id`**, 实现端到端可观测;
- LTS (Log/Trace/Span) 上报增强: 新增 **Claude Code 工具调用 tracing**、**heartbeat monitoring**;
- Claude Code 会话历史监控 (`app/services/claude_history_uploader.py`): 后台 `HistoryWatcher` 监视并上传历史会话;
- Claude Code 会话历史提取 (`app/services/claude_history_extractor.py`): 从原始 session log 提炼**结构化洞察**。

---

## 【表格解读】

### Commands 表 (原文逐字还原)

| Command | Trigger | Description |
|---------|---------|-------------|
| `/claude` | User / LLM / Auto | Invoke Claude Code skills |
| `/verify` | User / LLM / Auto | Model deployment verification |
| `/adapt` | User / LLM / Auto | Model adaptation to Ascend NPU |
| `/optimize` | User / LLM / Auto | vLLM-Ascend performance optimization |
| `/quantify` | User / LLM / Auto | Model quantization |
| `/commit` | User / LLM / Auto | Code commit and push |
| `/search` | User / LLM / Auto | Ascend model search |
| `/ai4s` | User / LLM / Auto | AI for Science model migration |
| `/deploy` | User / LLM / Auto | Model deployment |
| `/doc` | User / LLM / Auto | Documentation generation |
| `/pta` | User / LLM / Auto | **PyTorch-Ascend agent (new)** |
| `/experience` | User only | **Hermes engine introspection (new)** |
| `/learn` | User only | **Store adaptation experience (new)** |
| `/workflow` | User / LLM / Auto | Dynamic workflow orchestration **(rewritten)** |

#### 逐行解读
| 行 | 解读 |
|---|---|
| `/claude` | 调用 Claude Code skills, 三方均可触发 (用户 / LLM / 自动)。 |
| `/verify` | 模型部署验证。 |
| `/adapt` | 模型到 Ascend NPU 的适配。 |
| `/optimize` | 基于 vLLM-Ascend 的性能优化。 |
| `/quantify` | 模型量化。 |
| `/commit` | 代码提交与推送。 |
| `/search` | Ascend 模型搜索。 |
| `/ai4s` | AI for Science 模型迁移。 |
| `/deploy` | 模型部署。 |
| `/doc` | 文档生成。 |
| `/pta` | **本版本新增** PyTorch-Ascend 代理, 三方均可触发。 |
| `/experience` | **本版本新增** Hermes 引擎自省, 仅用户可触发 — 不开放给 LLM/自动通道, 体现"主动控制权在用户侧"的设计取向。 |
| `/learn` | **本版本新增** 用户教学, 用于把适配经验存入 Hermes, 同上仅用户可触发。 |
| `/workflow` | **本次重写** 的动态工作流编排, 接替原来的静态 intent resolver。 |

**Trigger 取值含义观察**: `User only` 仅出现于两个 Hermes 相关命令, 其余 12 个均允许 `User / LLM / Auto` 三方触发 — 表示这两个与"经验存储/自省"相关的命令被有意限制以避免 LLM/自动路径误改长期记忆。

> 此外原文无"参数表/性能对比/配置项"等其它表格, 此处为唯一一张表格, 已逐字还原并逐行解读。

---

## 【公式解读】

**原文无公式**。本文档是一篇版本变更说明, 不包含任何数学公式或伪代码表达式。

---

## 【关联】

> **内部链接**: 原文文末标注 **(无)**。以下关联均基于文档正文中各模块/特性之间互相提及的语义推导。

| 关联对象 | 关系与依赖 |
|---|---|
| **DynamicPlanner / WorkflowExecutor** (`app/tools/workflow/`) | `DynamicPlanner` 负责**生成计划**, `WorkflowExecutor` 负责**执行计划**并产出**端到端执行报告**; 二者通过 LangGraph `MemorySaver` 共用 checkpoint/restore 通道。 |
| **Brainstorming** (`brainstorming.py`) | 作为 `WorkflowExecutor` 的前置澄清环节, 受 `/workflow` 命令调度, 与 SSE 进度流共用 `progress_callback` (修复了 brainstorm 阻塞 SSE 的 bug)。 |
| **MCP Integration** (`mcp_integration.py`) | 是 `WorkflowExecutor` 调用外部工具的**桥接器**: 工作流步骤通过它调用 MCP server (Cannbot、MS Agent)。同时接受 `ExperienceStore.layers/` 中的 MCP optimization layer 反向优化建议。 |
| **Hermes Experience Engine** (`app/tools/experience/`) | 通过 `/experience` (自省) 与 `/learn` (用户教学) 命令暴露; 其 `MemoryEngine` 在 `DynamicPlanner` 决策与 `WorkflowExecutor` 错误恢复时被查询; `NudgeEngine` 主动给出优化建议。 |
| **MCP Servers** (`app/tools/mcp_servers/`) | Cannbot (stdio, 316 行)、MS Agent 由 `mcp_integration.py` 生命周期管理器在 `app/main.py` lifespan 中统一启动/关闭。 |
| **PTA Agent** (`/pta` 命令) | 基于 `MemorySaver` (`app/core/memory.py`) 的 `thread_id` 多轮记忆; 启动时从外部 clone 而非随仓库持久化。 |
| **`/v1/chat/config` endpoint** | 与 Hermes、PTA 工作流共用 LLM 运行时; 提供 **runtime config hot-reload** 与 **runtime LLM key rotation**, 上层 Workflow/PTA/`/claude` 等命令无须重启即可切换 Anthropic 凭据/模型。 |
| **Claude Code 历史监控/提取** (`claude_history_uploader.py` + `claude_history_extractor.py`) | 由 `HistoryWatcher` 后台线程驱动, 是 Hermes 引擎"洞察"来源之一; 与 LTS (Log/Trace/Span) 中的心跳与 `trace_id` 透传共同支撑可观测性。 |
| **CI Pipeline** (`.github/workflows/ci.yml`) | 含 lint / unit / integration 三阶段; 依赖 `requirements-dev.txt` 中的 `pytest`、`pytest-asyncio`、`pytest-cov`、`ruff`, 为以上所有新模块提供质量门禁。 |

---

## 【使用方法】

> 以下均来自原文 Commands 表、Highlights、Features 等章节。

### 命令触发 (聊天内命令)
- 触发方式分为三类: `User` (用户直接输入)、`LLM` (模型自动调用)、`Auto` (系统自动)。
- 通用流程 (User / LLM / Auto 均可触发): `/claude`、`/verify`、`/adapt`、`/optimize`、`/quantify`、`/commit`、`/search`、`/ai4s`、`/deploy`、`/doc`、`/pta`、`/workflow`。
- 仅用户可用 (原文标注 `User only`): `/experience`、`/learn` — 用于读写 Hermes 引擎的长期记忆与技能, 防止 LLM/自动通道意外污染。
- `/workflow` 已在本次**重写**, 内部走 DAG 式 `DynamicPlanner` + `WorkflowExecutor`, 支持 SSE 实时进度流。

### HTTP 端点 (用于运行时配置热更新)
- **`/v1/chat/config`**: 运行时更新 Anthropic 模型配置, **无需重启服务**;
- **`/pta`**: PyTorch-Ascend 代理入口, 基于 `thread_id` 维护多轮对话记忆 (含历史上下文组装 + 每轮持久化);
- 配合 **runtime LLM key rotation**, 可在不重启的情况下注入新的 Anthropic access token。

### 环境/部署相关配置项 (原文)
- **默认模型下载路径配置**面向 Ascend NPU 环境;
- **保留的标准昇腾 NPU 工具链路径**: `/home/Ascend/ascend-toolkit/`、`/usr/local/Ascend/` (在 SKILL.md 路径修正中显式保留);
- **`_CLAUDE_SKILL_TIMEOUT`** 默认值用于防止 skill 调用挂起;
- **`_aiter_with_timeout`** 辅助函数用于给流式生成器加超时 (因 `asyncio.wait_for` 无法直接包 async generator)。

### 外部 Agent 获取方式 (原文)
- search-agent、pta-agent 在启动时**自外部 clone**, 不再随仓库持久化, 借此保证部署清洁。

### 可观测性开关 (原文)
- 全链路 `trace_id` 透传默认开启;
- LTS (Log/Trace/Span) 上报已包含 Claude Code 工具调用 tracing + heartbeat monitoring。

> 其余更深层的内部参数 (如 `MemorySaver` 配置项、最大并发度、retry 参数、`progress_callback` 协议细节) **原文未涉及**, 需结合源码 `app/tools/workflow/`、`app/tools/experience/`、`app/core/memory.py` 等文件进一步查阅。
```
