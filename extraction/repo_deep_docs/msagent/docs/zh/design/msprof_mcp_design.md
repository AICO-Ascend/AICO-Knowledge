# msprof-mcp 设计文档

> 仓 `msagent` · 路径 `docs/zh/design/msprof_mcp_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msagent/docs/zh/design/msprof_mcp_design.md

# msprof-mcp 设计文档 一体化深度解读

## 【定位】

msprof-mcp 是基于 Model Context Protocol (MCP) 的 stdio 服务器，将 Ascend PyTorch Profiler 产出的六大类数据载体（trace_view.json、kernel_details.csv、op_statistic.csv、communication_matrix.json、communication.json、profiler_info.json、ascend_pytorch_profiler.db）整合为统一的 MCP 工具面，使 LLM（msAgent Profiler / Cherry Studio / Claude Desktop）能够通过自然语言调用完成 Profiling 总体分析、TimeLine 重叠分析、算子统计、通信瓶颈识别与只读 DB 查询等性能诊断任务。

---

## 【技术要点】

1. **MCP stdio + FastMCP 框架**：`create_server()` 作为唯一工具注册入口，通过 `mcp.tool()` 把所有 Analyzer 方法注册为 MCP 工具；启动入口为 `main()` 调用 `mcp.run(transport="stdio")`。
2. **六大数据载体 × 独立 Analyzer 类**：TraceViewAnalyzeTool、KernelDetailsAnalyzer / OpStatisticAnalyzer / GenericCsvAnalyzer、ProfilerInfoAnalyzer / CommunicationMatrixAnalyzer / CommunicationAnalyzer、DBQueryTool、MsProfAnalyzer、ProfilerViewTools 各自封装一类数据载体，模块间不交叉耦合。
3. **大结果治理三层机制**：Trace 工具通过阈值计数截断、CSV/DB 工具通过 `MAX_RESULT_CHARS` 限制、DB 工具提供 `execute_sql_to_csv` 大结果外置，并使用 `RESULT_TOO_LARGE` 错误引导收敛，防止返回给 LLM 的 JSON 撑爆上下文。
4. **跨版本 CSV 字段兼容**：通过 `FIELD_MAPPINGS` 字典映射不同 Profiler 版本字段名差异（如 `Device_id` vs `Device ID` vs `device_id`），不将字段名写死在业务逻辑中。
5. **SQL 安全只读边界**：`_FORBIDDEN_PREFIXES` 禁止 INSERT/UPDATE/DELETE 等写操作，SQL 预览强制限制结果大小（`MAX_RESULT_CHARS`）。
6. **msprof-analyze 安全封装**：`MsProfAnalyzer` 使用 `stdin=subprocess.DEVNULL` 防止交互阻塞，通过 `_sanitize_success_output` 净化外部命令的噪音日志；`ConnectionManager` 自动检测 glibc 版本选择兼容的 Perfetto TraceProcessor Shell 二进制。

---

## 【关键机制与数据】

**工作原理（基于架构图与时序图）：**

- **注册流程（原文: 4.1 启动时序图）**：`Host → main() → configure_logging()（解析 MSPROF_MCP_LOG_LEVEL）→ create_server() → 实例化所有 Analyzer → mcp.tool() 注册 → mcp.run(transport="stdio")`。
- **Trace 分析数据流（原文: 2.1 分层架构图）**：`TraceViewAnalyzeTool` 内部通过 `ConnectionManager` 管理 Perfetto TraceProcessor Shell 进程；`FlowDataTool` / `SliceFinderTool` / `SliceInfoTool` / `SqlQueryTool` 基于 Perfetto Python API 与 Shell 进程交互，支持多 Trace 文件并发分析。
- **CSV/DB 数据流**：`CSV_* → pandas DataFrame`；`DB / ProfilerViewTools → sqlite3 Connection`；`MsProfAnalyzer → msprof-analyze advisor` 外部进程。
- **结果治理策略（原文: 2.2 架构解读）**：Trace 工具通过"阈值计数截断"、CSV/DB 工具通过 `MAX_RESULT_CHARS`、DB 工具通过 `execute_sql_to_csv` 大结果外置。
- **版本兼容（原文: 2 业务痛点 / 3 核心价值）**：通过 `FIELD_MAPPINGS` 灵活映射字段名，兼容 `Device_id` vs `Device ID` vs `device_id` 等不同 Profiler 版本的 CSV schema 差异。

**性能与数据规模描述（原文有的才写）：**
- 原文: trace_view.json 文件"通常达到数百 MB 甚至数 GB，直接加载到上下文不可行"。
- 原文: 日志级别默认 WARNING，受 `MSPROF_MCP_LOG_LEVEL` 环境变量控制。
- 原文（缺失数据）: 文档未提供具体性能数据（如启动延迟、查询吞吐量、Tool 调用耗时），也未提供 `MAX_RESULT_CHARS` 与结果外置阈值的具体数值。

---

## 【表格解读】

### 表格 1：修订记录

| 日期 | 修订版本 | 修改描述 | 作者 | RFC文档 |
| -- | -- | -- | -- | -- |
| 2026-06-03 | 1.0 | 补充 msprof-mcp 详细设计文档，覆盖架构、工具体系、数据流与测试设计 | kali20gakki1 |  |

**逐行解读**：仅一行有效记录，版本 1.0 由作者 kali20gakki1 于 2026-06-03 完成首次发布，文档定位为"详细设计文档，覆盖架构、工具体系、数据流与测试设计"；RFC 文档列为空表示尚未关联 RFC 编号。

---

### 表格 2：核心价值

| 价值点 | 说明 |
| -- | -- |
| 统一工具面 | 通过 MCP 协议将 6 大分析维度统一暴露为工具，LLM 可以用自然语言调用。 |
| 数据载体全覆盖 | 覆盖 JSON/CSV/SQLite DB 三大类 Profiling 数据载体，不遗漏关键分析维度。 |
| 大结果治理 | 通过阈值截断、CSV 外置、JSON 大小上限等机制，防止大结果撑爆上下文。 |
| 版本兼容 | 通过 `FIELD_MAPPINGS` 灵活映射字段名，兼容不同 Profiler 版本的 CSV schema 差异。 |
| 安全只读 | SQL 查询严格只读（禁止 INSERT/UPDATE/DELETE 等），SQL 预览强制限制结果大小。 |
| 可集成性 | 通过 `uvx msprof-mcp` 或本地源码方式运行，支持 Cherry Studio / Claude Desktop / msAgent 集成。 |

**逐行解读**：
- **统一工具面**：对应架构设计中"FastMCP 统一注册"原则，将 6 大分析维度（Trace/CSV×3/JSON×3/DB×2/msprof-analyze/View）合并为单一协议入口。
- **数据载体全覆盖**：对应业务痛点中"数据格式多样"，通过三类 Analyzer（CSV/JSON/DB）+ Perfetto Shell 覆盖所有 Profiling 输出。
- **大结果治理**：对应业务痛点"Trace 数据巨大（数百 MB 甚至数 GB）"，通过三层机制（阈值截断/CSV 外置/JSON 上限）保证 LLM 上下文安全。
- **版本兼容**：对应业务痛点"版本兼容性"，通过 `FIELD_MAPPINGS` 字典映射而非硬编码字段名。
- **安全只读**：对应非目标中"不支持写入性 SQL 操作"，通过 `_FORBIDDEN_PREFIXES` 与 `MAX_RESULT_CHARS` 双重约束。
- **可集成性**：给出三种部署形态：`uvx msprof-mcp`、本地源码运行、msAgent 集成。

---

### 表格 3：模块职责拆解

| 模块 | 代表路径 | 主要职责 | 设计要点 |
| -- | -- | -- | -- |
| 服务入口层 | `src/msprof_mcp/server.py` | 创建 FastMCP 实例、注册所有工具方法、配置日志、启动 stdio 服务 | `create_server()` 是唯一注册入口，`main()` 启动 stdio 传输。 |
| Trace 分析层 | `src/msprof_mcp/tools/trace_view/` | 分析 trace_view.json，提供重叠分析、Slice 搜索、Flow 数据查询与 SQL 执行 | 通过 ConnectionManager 管理 TraceProcessor Shell 进程，支持多文件连接复用。 |
| CSV 分析层 | `src/msprof_mcp/tools/csv_analyze.py` | 分析 kernel_details.csv、op_statistic.csv 及通用 CSV 文件 | 三个 Analyzer 类分别覆盖不同 CSV 场景，`FIELD_MAPPINGS` 处理版本兼容。 |
| JSON 分析层 | `src/msprof_mcp/tools/json_analyze.py` | 分析 profiler_info.json、communication_matrix.json、communication.json | 两个 Analyzer 类分别覆盖配置查询与通信分析。 |
| DB 查询层 | `src/msprof_mcp/tools/db_query.py` | 对 ascend_pytorch_profiler.db 执行只读 SQL，支持预览与 CSV 导出 | `_FORBIDDEN_PREFIXES` 禁止写操作，`MAX_RESULT_CHARS` 限制预览大小。 |
| msprof-analyze 层 | `src/msprof_mcp/tools/msprof_analyze_cmd.py` | 封装 `msprof-analyze advisor` 命令，净化日志输出 | `stdin=subprocess.DEVNULL` 防止交互阻塞，`_sanitize_success_output` 净化噪音日志。 |
| 视图创建层 | `src/msprof_mcp/tools/profiler_view_tools.py` | 在 profiler SQLite DB 上创建持久视图（如 dispatch_view） | 检查必需表是否存在，支持 `replace_existing` 选项。 |
| Perfetto 工具层 | `src/msprof_mcp/tools/trace_view/perfetto_tool.py` | FlowDataTool、SliceFinderTool、SliceInfoTool、SqlQueryTool 的具体实现 | 基于 Perfetto Python API 与 TraceProcessor Shell 进程交互。 |
| 连接管理层 | `src/msprof_mcp/tools/trace_view/connection_manager.py` | 管理 TraceProcessor Shell 进程的启动、连接与 glibc 兼容检测 | 自动检测 glibc 版本，选择兼容的 Shell 二进制。 |
| 日志配置层 | `src/msprof_mcp/server.py: configure_logging()` | 配置包级日志，抑制 stdio 场景下的噪音日志 | `MSPROF_MCP_LOG_LEVEL` 环境变量控制级别，默认 WARNING。 |

**逐行解读**：
- **服务入口层**：是 FastMCP 实例化与 `mcp.tool()` 注册的唯一场所，决定了协议与传输方式。
- **Trace 分析层**：是最大、最复杂的分析模块，通过子模块拆分（ConnectionManager、Perfetto Tool）实现多文件复用。
- **CSV 分析层**：三个 Analyzer 类（KernelDetails / OpStatistic / Generic）共享同一文件 `csv_analyze.py`，通过 `FIELD_MAPPINGS` 处理版本差异。
- **JSON 分析层**：从命名上看，模块名为单数 `json_analyze.py`，但表内描述为"两个 Analyzer 类"（ProfilerInfoAnalyzer、CommunicationMatrixAnalyzer/CommunicationAnalyzer 三个类），原文描述可能存在口径偏差。
- **DB 查询层**：通过只读约束与结果大小限制保证 LLM 调用安全；`execute_sql_to_csv` 与 `execute_sql` 形成预览/导出两级工具。
- **msprof-analyze 层**：是唯一调用外部二进制（`msprof-analyze advisor`）的模块，需要专门处理超时、卡死、日志噪音等问题。
- **视图创建层**：与 DB 查询层不同，专注于一次性视图创建（dispatch_view），而非交互式查询。
- **Perfetto 工具层**：是 Trace 分析层的内部实现层，封装 Perfetto Python API 与 Shell 进程的交互细节。
- **连接管理层**：负责 Perfetto Shell 进程生命周期管理，特别处理 glibc 版本兼容性。
- **日志配置层**：std io 协议对日志输出敏感（任何 stdout 噪音都可能破坏协议帧），因此日志级别默认 WARNING 并支持环境变量覆盖。

---

### 表格 4：工具注册全景

| 工具名称 | 注册来源 | 数据载体 | 核心能力 |
| -- | -- | -- | -- |
| `get_flow_data` | TraceViewAnalyzeTool | trace_view.json | 按 Flow 关联 CPU/NPU 算子明细查询 |
| `find_slices` | TraceViewAnalyzeTool | trace_view.json | 搜索 Trace 中的特定 Slice |
| `execute_sql_query` | TraceViewAnalyzeTool | trace_view.json | 执行 PerfettoSQL 自定义查询 |
| `analyze_overlap` | TraceViewAnalyzeTool | trace_view.json | 分析计算/通信/调度重叠占比 |
| `analyze_kernel_details` | KernelDetailsAnalyzer | kernel_details.csv | 算子耗时分布、Top N、设备分布 |
| `get_operator_details` | KernelDetailsAnalyzer | kernel_details.csv | 查询特定算子执行明细 |
| `analyze_op_statistic` | OpStatisticAnalyzer | op_statistic.csv | 算子调用次数、总耗时、Core 类型分布 |
| `get_op_type_details` | OpStatisticAnalyzer | op_statistic.csv | 查询特定类型/Core 类型算子统计 |
| `get_csv_info` | GenericCsvAnalyzer | 任意 CSV | 通用 CSV 结构探索与样本数据 |
| `search_csv_by_field` | GenericCsvAnalyzer | 任意 CSV | 通用 CSV 字段搜索与过滤 |
| `get_profiler_config` | ProfilerInfoAnalyzer | profiler_info.json | 获取 Profiler 配置与环境信息 |
| `analyze_communication` | CommunicationMatrixAnalyzer | communication_matrix.json | P2P/集合通信瓶颈与带宽分析 |
| `analyze_communication_trace` | CommunicationAnalyzer | communication.json | 通信操作时间分解与带宽详情 |
| `execute_sql` | DBQueryTool | ascend_pytorch_profiler.db | 只读 SQL 预览查询 |
| `execute_sql_to_csv` | DBQueryTool | ascend_pytorch_profiler.db | 只读 SQL + CSV 外置导出 |
| `msprof_analyze_advisor` | MsProfAnalyzer | Profiling 数据目录 | msprof-analyze 总体分析命令封装 |
| `create_dispatch_view` | ProfilerViewTools | ascend_pytorch_profiler.db | 创建 dispatch 持久视图 |

**逐行解读**（按模块分组）：

**TraceViewAnalyzeTool（4 个工具）**：
- `get_flow_data`：面向 Flow 关联分析，用于跨设备 CPU/NPU 算子对账。
- `find_slices`：面向 Slice 搜索定位。
- `execute_sql_query`：暴露 PerfettoSQL 给 LLM 自定义分析（关键能力，区别于 DB 的 sqlite SQL）。
- `analyze_overlap`：计算/通信/调度三维重叠分析是 TimeLine 性能定位的核心抓手。

**KernelDetailsAnalyzer（2 个工具）**：从算子级（kernel-level）CSV 提供"分布 + 明细"两类查询（`analyze_kernel_details` 聚合分布 + `get_operator_details` 单点明细）。

**OpStatisticAnalyzer（2 个工具）**：从算子统计 CSV 提供"次数/耗时/Core 类型"维度（`analyze_op_statistic` 概览 + `get_op_type_details` 聚焦查询）。

**GenericCsvAnalyzer（2 个工具）**：兜底工具，覆盖 `kernel_details.csv` / `op_statistic.csv` 之外的任意 CSV（如自定义 Profiling 产物），通过 `get_csv_info` 探索 schema、`search_csv_by_field` 做字段过滤。

**JSON 分析层（3 个工具）**：
- `get_profiler_config`：读 `profiler_info.json`，提供环境/参数基线。
- `analyze_communication`：基于 `communication_matrix.json`（矩阵视图）做 P2P/集合通信瓶颈。
- `analyze_communication_trace`：基于 `communication.json`（时间序列表）做带宽详情与时间分解。两者输入不同，分析粒度互补。

**DBQueryTool（2 个工具）**：`execute_sql` 是小结果预览，`execute_sql_to_csv` 是大结果外置，构成"查询大小自适应"两级入口。

**MsProfAnalyzer（1 个工具）**：`msprof_analyze_advisor` 是唯一的"外部命令封装"工具，承担总体性 Advisor 分析输出。

**ProfilerViewTools（1 个工具）**：`create_dispatch_view` 是视图物化工具，与查询类工具正交。

**整体工具特征**：共 17 个工具，按"Trace(4) + CSV(6) + JSON(3) + DB(2) + Advisor(1) + View(1)"分布，与"六大分析维度"对齐——Profiling 总体（msprof_analyze_advisor）、TimeLine（4 个）、算子（4 个 KernelDetails/OpStatistic）、通信（2 个）、配置（1 个）、DB（2 个 + 1 个 View 物化）。

---

## 【公式解读】

**原文无公式。**

文档未包含 LaTeX 数学公式或伪代码形式公式。架构与流程信息通过 mermaid 图（flowchart 分层架构图、sequenceDiagram 启动时序图、flowchart 工具分层）承载，而非公式表达。

---

## 【关联】

**与文中提到的其他模块 / 上下游关系：**

- **msAgent 智能体集成**（内部链接 `msagent_design.md`）：`msprof-mcp` 是 msAgent 智能体的 Profiling 数据分析后端，通过 stdio MCP 协议与 msAgent 通信，构成"msAgent（自然语言入口）→ msprof-mcp（性能分析执行）→ msprof-analyze / Perfetto Shell（外部分析引擎）"的三层调用链。
- **msprof-analyze advisor**（外部命令）：通过 `MsProfAnalyzer` 工具封装，是 msprof-mcp 唯一直接调用的外部二进制，承担 Profiling 总体分析。
- **Perfetto TraceProcessor Shell**（`resources/perfetto/trace_processor_shell`）：通过 `ConnectionManager` 管理进程生命周期，承担 TimeLine 分析底座。
- **Ascend PyTorch Profiler 数据产出**：trace_view.json、kernel_details.csv、op_statistic.csv、communication_matrix.json、communication.json、profiler_info.json、ascend_pytorch_profiler.db 共 7 类数据载体，是 msprof-mcp 全部工具的输入。
- **Cherry Studio / Claude Desktop**：通过 stdio MCP 协议集成，验证 msprof-mcp 的协议兼容性与可移植性。
- **测试 / 打包 / PyPI 发布**（设计目标之一）：构成 msprof-mcp 的工程化下游，为模块提供稳定边界，但本文档未展开测试与发布细节（推断源自"修订描述"中"覆盖架构、工具体系、数据流与测试设计"，但测试章节在所提供片段内未出现）。

**内部链接**：
- [msagent_design.md](msagent_design.md) — msAgent 智能体整体设计文档，msprof-mcp 是其 Profiling 分析能力的后端实现。

---

## 【使用方法】

**启用方式（原文: 3 核心价值 可集成性 / 4.1 设计目标）**：

1. **通过 `uvx` 运行**：`uvx msprof-mcp`（PyPI 安装后一键启动）。
2. **本地源码运行**：直接以本地源码方式启动 stdio 服务（具体命令原文未给出，文档仅描述"通过 uvx msprof-mcp 或本地源码方式运行"）。
3. **集成到 MCP Host**：支持 Cherry Studio / Claude Desktop / msAgent 集成，配置 stdio 传输协议即可。

**配置项 / 环境变量（原文: 日志配置层 / 5.1 工具分层）**：

| 配置项 | 默认值 | 说明 |
| -- | -- | -- |
| `MSPROF_MCP_LOG_LEVEL` | `WARNING` | 包级日志级别控制；考虑到 stdio 协议对 stdout 敏感，默认抑制 DEBUG/INFO 噪音。 |

**工具参数 / 阈值（原文有的）**：
- `MAX_RESULT_CHARS`：DB 查询层 SQL 预览结果大小上限（具体数值原文未给出）。
- `RESULT_TOO_LARGE` 错误：当结果超过阈值时返回该错误引导收敛。
- `replace_existing`：`create_dispatch_view` 工具的可选参数，控制是否替换已存在的同名视图。
- `_FORBIDDEN_PREFIXES`：DB 查询层内部维护的 SQL 关键字黑名单前缀（原文未列出具体前缀集合）。

**原文未涉及**：
- msprof-mcp 的具体安装命令（如 `pip install msprof-mcp` 或 `uv tool install`）原文未给出。
- MCP Host（Cherry Studio / Claude Desktop / msAgent）侧的 stdio 配置 JSON 片段原文未给出。
- `MAX_RESULT_CHARS` 与 `RESULT_TOO_LARGE` 的具体数值原文未给出。
- `_FORBIDDEN_PREFIXES` 的具体前缀列表原文未给出。
- 文档在第 5.1 节"工具分层与能力面"处被截断，后续章节（包括测试设计、配置项细节）未在所提供文本中呈现。
