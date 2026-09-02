# 发布说明

> 仓 `model-agent` · 路径 `Release_notes/RELEASE_NOTES_v1.0.0_CN.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/model-agent/Release_notes/RELEASE_NOTES_v1.0.0_CN.md

# model-agent v1.0.0 (2026.06.30) 发布说明 — 深度解读

---

## 【定位】

本文档描述 model-agent 项目从"OpenAI 兼容聊天代理"到"功能完备的模型优化框架"的重大架构升级,核心新增 **动态工作流引擎**、**Hermes 自演进经验引擎**、**MCP 集成**、**PTA Agent** 及 **Anthropic Claude 原生接入** 五大能力,并完成 LLM 提供商由 MiniMax/MoonShot 向 Anthropic Claude 的迁移、CI 流水线建设与大量清理/Bug 修复。

---

## 【技术要点】

1. **动态工作流引擎(DAG)**: 由 `DynamicPlanner` (`planner.py`) 替换原静态关键词意图解析器,LLM 生成多步骤计划,支持依赖解析、并行路径交叉验证与自适应目标分解;`WorkflowExecutor` (`executor.py`) 实现并行步骤执行、可配置重试、LangGraph `MemorySaver` 检查点/恢复和最大并发控制;通过 `asyncio.Queue` + `progress_callback` 实现 SSE 实时进度推送。
2. **Hermes 自演进引擎** (`app/tools/experience/`): 由 `ExperienceStore` (持久化层,基于 `memory.jsonl` / `skills.json` / `insights.jsonl`,支持原子写入与版本管理)、`MemoryEngine` (语义记忆检索)、`SkillEngine` (技能提取/版本化/应用)、`NudgeEngine` (基于历史经验的模式匹配主动建议优化) 及 `layers/` 分层架构(错误恢复/MCP 优化/模型适配/用户偏好)组成。
3. **MCP 集成**: 新增生命周期管理器 `app/tools/workflow/mcp_integration.py`,支持应用启动自动拉起、退出优雅关闭;内置 **Cannbot Server** (`cannbot_server.py`,共 **316 行** stdio 传输服务端实现) 与 **MS Agent Server** (`ms_agent_server.py` / `ms_agent_runner.py`)。
4. **PTA Agent** (`/pta`): 面向 `torch_npu` 开发场景的 PyTorch-Ascend Agent,基于 `thread_id` 的多轮对话记忆,支持历史上下文拼装与逐轮持久化;基于 LangGraph `MemorySaver` (`app/core/memory.py`) 实现检查点保存/恢复。
5. **Anthropic Claude 原生接入**: LLM 提供商由 `langchain-openai` 切换至 `langchain-anthropic`;新增 `POST /v1/chat/config` 端点支持运行时配置热更新(需 `access_token` / `base_url` / `model` 三字段);新增 `trace_id` 全链路传播、运行时 LLM 密钥轮换支持(无需重启即可注入新 Anthropic 访问令牌)。
6. **基础设施完善**: 新增 `.github/workflows/ci.yml` 三阶段流水线(代码检查/单元测试/集成测试);新增 `requirements-dev.txt`(`pytest` / `pytest-asyncio` / `pytest-cov` / `ruff`);新增 `app/services/claude_history_uploader.py`(`HistoryWatcher` 后台监控)与 `claude_history_extractor.py`(结构化洞察提取);新增 `app/tools/skills/registry.py` 技能注册中心(跨框架管理/发现/版本化);新增 `_aiter_with_timeout` 异步生成器超时包装器(`asyncio.wait_for` 无法包装异步生成器)与 `_CLAUDE_SKILL_TIMEOUT` 默认值防止技能调用无限挂起。

---

## 【关键机制与数据】

### 工作流引擎工作机制(原文)
- **DynamicPlanner → WorkflowExecutor 闭环**: LLM 生成多步计划 → 执行计划含并行路径 → 通过 `asyncio.Queue` + `progress_callback` SSE 推流 → 端到端执行报告(逐步骤详情/耗时/结果)。
- **Brainstorming 多轮澄清**: 渐进式问题生成 + 模糊度评估 + 提案跟踪 + 设计文档输出。
- **MCP 桥接**: 工作流步骤调用 MCP Server 执行领域特定操作。
- **检查点/恢复**: 通过 LangGraph `MemorySaver` 实现。

### Hermes 经验引擎工作机制(原文)
- **ExperienceStore 持久化**: 三个文件 `memory.jsonl` / `skills.json` / `insights.jsonl`,原子写入 + 版本管理。
- **检索路径**: 当前上下文 → `MemoryEngine` 语义检索相关历史经验 → `SkillEngine` 应用提取的技能 → `NudgeEngine` 主动触发优化建议。
- **分层架构**: `layers/` 提供可插拔适配层(错误恢复/MCP 优化/模型适配/用户偏好)。

### 服务启动生命周期(原文)
`app/main.py` 启动顺序: **eval 日志补丁 → MCP 管理器 → Hermes 引擎 → Claude Code 历史监控器**。

### 部署参数(原文)
- 服务运行端口: **18003**;uvicorn 入口文件: `run.py`(项目根目录)。
- 外部 Agent(search-agent、pta-agent)改为启动时从各自源头克隆,不再本地持久化在仓库中。

### 代码清理量化数据(原文)
- 移除 `kernel_meta/` 文件: **96 个**(Ascend 编译缓存产物)
- 移除 `__pycache__/` 目录: **40+ 个** 及对应 `.pyc` 文件
- 移除 `tmp/` 测试/演示脚本: **20 个**
- 移除 `server.log` 积压日志: **7MB+**
- 修复硬编码个人目录的 SKILL.md: **9 个**
- 综合测试套件当前通过率: **86.2% (160 个测试)**
- Cannbot Server 服务端代码: **316 行**

---

## 【表格解读】

### 表 1: 命令一览(原文逐字还原)

| 命令 | 触发方式 | 说明 |
|---------|---------|-------------|
| `/claude` | 用户 / LLM / 自动 | 调用 Claude Code 技能 |
| `/verify` | 用户 / LLM / 自动 | 模型部署验证 |
| `/adapt` | 用户 / LLM / 自动 | 模型适配至 Ascend NPU |
| `/optimize` | 用户 / LLM / 自动 | vLLM-Ascend 性能优化 |
| `/quantify` | 用户 / LLM / 自动 | 模型量化 |
| `/commit` | 用户 / LLM / 自动 | 代码提交与推送 |
| `/search` | 用户 / LLM / 自动 | Ascend 模型搜索 |
| `/ai4s` | 用户 / LLM / 自动 | AI for Science 模型迁移 |
| `/deploy` | 用户 / LLM / 自动 | 模型部署 |
| `/doc` | 用户 / LLM / 自动 | 文档生成 |
| `/pta` | 用户 / LLM / 自动 | **PyTorch-Ascend Agent(新增)** |
| `/experience` | 仅用户 | **Hermes 引擎内省(新增)** |
| `/learn` | 仅用户 | **存储适配经验(新增)** |
| `/workflow` | 用户 / LLM / 自动 | 动态工作流编排 **(重写)** |

**逐行解读**:
- 14 条命令整体分为三组:**业务命令** (`/claude` ~ `/doc`,10 条)、**新增命令** (`/pta` / `/experience` / `/learn`,3 条,均加粗)、**重写命令** (`/workflow`,1 条,加粗)。
- 触发方式三档:**用户**(显式输入)、**LLM**(模型决策)、**自动**(框架触发),绝大多数命令三种均支持;仅 `/experience` 与 `/learn` 限定"仅用户",体现其内省与主动学习属性。
- `/pta` / `/experience` / `/learn` 三条加粗命令恰好对应本次发布的三大新能力:**PyTorch-Ascend 专用 Agent**、**Hermes 引擎自省**、**Hermes 主动学习入口**。
- `/workflow` 标记"重写",印证了核心亮点"以基于 DAG 的 DynamicPlanner + WorkflowExecutor 替代原有的静态意图解析器"。

### 表 2: 依赖变更(原文逐字还原)

| 依赖 | 原版本 | 当前版本 | 备注 |
|------------|-----------------|-----------------|-------|
| LLM SDK | langchain-openai | langchain-anthropic | Anthropic Claude 原生 |
| HTTP 客户端 | — | httpx>=0.28.0 | MCP 传输 |
| SSE 服务端 | — | sse-starlette>=2.0.0 | MCP 流式 |
| 开发工具 | — | pytest>=7.4.0, ruff | CI 流水线 |

**逐行解读**:
- **LLM SDK** 由 OpenAI 兼容 (`langchain-openai`) 切换至 Anthropic 原生 (`langchain-anthropic`),这是与破坏性变更中环境变量重命名配套的 Provider 切换。
- **httpx>=0.28.0** 与 **sse-starlette>=2.0.0** 是首次引入,均为 MCP(模型上下文协议)功能服务:`httpx` 用于 MCP 传输,`sse-starlette` 用于 MCP 流式响应。
- **pytest>=7.4.0 与 ruff** 共同支撑 `.github/workflows/ci.yml` 三阶段流水线(代码检查/单元测试/集成测试)。
- 表格仅列出 4 项变更,其余依赖(FastAPI、Uvicorn、Pydantic、LangChain、LangGraph、python-dotenv、structlog、huaweicloudsdklts)保持不变。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

本次发布以"**Provider 切换 + 工作流/经验/MCP 三大新引擎 + Agent 扩展 + 工程化**"为主线,模块间关系如下:

1. **LLM Provider 切换(Anthropic) ↔ 工作流引擎**: `DynamicPlanner` 与 `WorkflowExecutor` 内的 LLM 调用均依赖 `langchain-anthropic` SDK;`/v1/chat/config` 端点与运行时密钥轮换均围绕 Anthropic 凭据展开,共同构成"无重启热更新"闭环。
2. **工作流引擎 ↔ Hermes 经验引擎**: 工作流步骤的执行结果经 `ExperienceStore` 持久化(`memory.jsonl` / `skills.json` / `insights.jsonl`),供 `MemoryEngine` 检索并由 `NudgeEngine` 主动触发建议;`/experience` / `/learn` 命令则为用户提供入口。
3. **工作流引擎 ↔ MCP 集成**: `mcp_integration.py` 桥接工作流步骤与 MCP Server,`Cannbot Server`(316 行 stdio)与 `MS Agent Server` 暴露领域工具;`MCP_*` 环境变量控制其行为。
4. **PTA Agent ↔ LangGraph MemorySaver**: `/pta` 多轮对话基于 `app/core/memory.py` 的 `MemorySaver` 与 `thread_id` 实现检查点;与工作流引擎共享同一 LangGraph 基础设施。
5. **Claude Code 工具链 ↔ Hermes**: `claude_history_uploader.py`(`HistoryWatcher` 后台)与 `claude_history_extractor.py` 将 Claude Code 会话摄入 Hermes 的 `insights.jsonl` 流,形成闭环。
6. **服务启动序列 ↔ 上述所有引擎**: `app/main.py` 启动顺序为"eval 日志补丁 → MCP 管理器 → Hermes 引擎 → Claude Code 历史监控器",构成依赖链上的初始化时序约束。
7. **CI 流水线 ↔ 开发工具链**: `.github/workflows/ci.yml` 三阶段(代码检查/单元测试/集成测试)依赖 `requirements-dev.txt`(`pytest` / `pytest-asyncio` / `pytest-cov` / `ruff`);当前通过率 **86.2% (160 个测试)** 即为此流水线的产物。
8. **配置项家族**: `.env` 新增四类可选配置 — `HERMES_*` / `MCP_*` / `WORKFLOW_*` / `CLAUDE_HISTORY_*`,默认值开箱即用,与上述四个子系统一一对应。

---

## 【使用方法】

### 环境变量(破坏性变更,原文)
```
OPENAI_API_KEY   →  ANTHROPIC_AUTH_TOKEN
OPENAI_BASE_URL  →  ANTHROPIC_BASE_URL
OPENAI_MODEL     →  ANTHROPIC_MODEL
```
部署清单与 `.env` 文件必须同步更新。

### API 路由(原文)
- 健康检查: `GET /api/system/health`  →  `GET /_stcore/health`
- 流式聊天 + brainstorm: `/api/chat/stream` + `/api/chat/brainstorm`  → 合并为 `POST /v1/chat/completions`
- 运行时配置热更新(新增): `POST /v1/chat/config`,**必须**包含 `access_token` / `base_url` / `model` 三个字段

### 启动方式(原文)
- 入口文件: `run.py`(uvicorn),**项目根目录**
- 监听端口: **18003**
- 启动时自动行为: eval 日志补丁 → MCP 管理器拉起 → Hermes 引擎初始化 → Claude Code 历史监控器启动;外部 Agent(search-agent、pta-agent)启动时从源头克隆

### `.env` 可选配置(原文)
新增 `HERMES_*` / `MCP_*` / `WORKFLOW_*` / `CLAUDE_HISTORY_*` 四类可选配置,默认值开箱即用,生产环境可按需定制。

### 新增/变更命令(原文)
- `/pta`(用户/LLM/自动)— PyTorch-Ascend Agent 多轮对话
- `/experience`(仅用户)— Hermes 引擎内省(统计/记忆/技能/洞察/遗忘)
- `/learn`(仅用户)— 主动将适配经验存入 Hermes
- `/workflow`(用户/LLM/自动)— 动态工作流编排(DAG 引擎,已重写)

### CI 流水线(原文)
`.github/workflows/ci.yml` 三阶段: 代码检查 → 单元测试 → 集成测试;安装 `requirements-dev.txt` 中的 `pytest` / `pytest-asyncio` / `pytest-cov` / `ruff`。
