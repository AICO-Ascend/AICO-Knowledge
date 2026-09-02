# msprof_mcp_design

> 仓 `agent-skills` · 路径 `official/MindStudio/docs/zh/design/msprof_mcp_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/MindStudio/docs/zh/design/msprof_mcp_design.md

# msprof-mcp 设计文档一体化深度解读

---

## 【定位】

这篇文档系统描述了 `msprof-mcp` —— 一个基于 Model Context Protocol (MCP) 的服务器设计，旨在为大语言模型 (LLM) 提供分析 Ascend PyTorch Profiler 采集性能数据的统一工具面，覆盖架构分层、工具体系、数据流治理与测试设计，解决 Profiling 数据格式多样、Trace 体积巨大、工具链依赖复杂、版本字段差异等业务痛点。

---

## 【技术要点】

1. **统一工具面（17 个 MCP 工具）**：通过 `create_server()` 入口和 FastMCP 的 `mcp.tool()` 注册 17 个分析工具，覆盖 6 大分析维度（总体 / TimeLine / 算子 / 通信 / 配置 / 数据库）。
2. **数据载体解耦**：6 类 Analyzer 分别处理不同载体 —— `trace_view.json` 由 TraceViewAnalyzeTool 分析、`kernel_details.csv`/`op_statistic.csv` 由 CSV 分析层处理、`profiler_info.json`/`communication_matrix.json`/`communication.json` 由 JSON 分析层处理、`ascend_pytorch_profiler.db` 由 DBQueryTool 处理。
3. **大结果治理机制**：分层策略 —— Trace 工具阈值计数截断；CSV/DB 工具通过 `MAX_RESULT_CHARS` 限制返回大小；DB 工具提供 `execute_sql_to_csv` 大结果外置导出；超阈值返回 `RESULT_TOO_LARGE` 错误引导收敛。
4. **版本兼容字段映射**：通过 `FIELD_MAPPINGS` 字典映射不同 Profiler 版本的 CSV 字段名（如 `Device_id` vs `Device ID` vs `device_id`），不将字段名写死在业务逻辑中。
5. **安全只读 SQL**：`DBQueryTool` 通过 `_FORBIDDEN_PREFIXES` 禁止 INSERT/UPDATE/DELETE 等写操作；`msprof-analyze` 命令封装时使用 `stdin=subprocess.DEVNULL` 防止交互阻塞；提供 `_sanitize_success_output` 净化噪音日志。
6. **连接管理与多 Trace 并发**：TraceViewAnalyzeTool 内部通过 `ConnectionManager` 管理 Perfetto TraceProcessor Shell 进程，支持多 Trace 文件并发分析；自动检测 glibc 版本以选择兼容的 Shell 二进制。

---

## 【关键机制与数据】

### 工作原理（三层架构）

- **入口层**：`main()` 解析 `MSPROF_MCP_LOG_LEVEL` 环境变量（默认 WARNING）→ 调用 `configure_logging()` → 调用 `create_server()` → 通过 `mcp.run(transport="stdio")` 启动 stdio 传输。
- **服务层**：`create_server()` 实例化 9 个 Analyzer 对象，逐个调用 `mcp.tool()` 将方法注册为 MCP 工具，最终返回 FastMCP 实例。
- **载体层**：每个 Analyzer 封装特定数据载体的分析逻辑，例如 `CSV_K/KernelDetailsAnalyzer → pandas DataFrame`，`DB/DBQueryTool → sqlite3 Connection`，`MSANALYZE/MsProfAnalyzer → msprof-analyze advisor 外部命令`，`TV/TraceViewAnalyzeTool → Perfetto TraceProcessor Shell`。

### 数据流（启动时序）

> 原文：Host 启动 → Main 解析日志级别 → Server 实例化各 Analyzer → 各 Analyzer 通过 `mcp.tool()` 注册方法 → Server 返回 FastMCP 实例 → Main 启动 stdio 服务。

### 大结果治理策略

> 原文：Trace 工具通过阈值计数截断、CSV/DB 工具通过 `MAX_RESULT_CHARS` 限制、DB 工具提供 `execute_sql_to_csv` 大结果外置。

### 业务痛点量化

> 原文：trace_view.json 文件"通常达到数百 MB 甚至数 GB，直接加载到上下文不可行"。

### 外部命令封装

> 原文：`msprof-analyze advisor` 是外部二进制命令，存在超时、卡死、日志噪音等问题；`MsProfAnalyzer` 通过 `stdin=subprocess.DEVNULL` 防止交互阻塞。

---

## 【表格解读】

### 表格 1：核心价值

| 价值点 | 说明 |
| -- | -- |
| 统一工具面 | 通过 MCP 协议将 6 大分析维度统一暴露为工具，LLM 可以用自然语言调用。 |
| 数据载体全覆盖 | 覆盖 JSON/CSV/SQLite DB 三大类 Profiling 数据载体，不遗漏关键分析维度。 |
| 大结果治理 | 通过阈值截断、CSV 外置、JSON 大小上限等机制，防止大结果撑爆上下文。 |
| 版本兼容 | 通过 `FIELD_MAPPINGS` 灵活映射字段名，兼容不同 Profiler 版本的 CSV schema 差异。 |
| 安全只读 | SQL 查询严格只读（禁止 INSERT/UPDATE/DELETE 等），SQL 预览强制限制结果大小。 |
| 可集成性 | 通过 `uvx msprof-mcp` 或本地源码方式运行，支持 Cherry Studio / Claude Desktop / msAgent 集成。 |

**解读**：此表把方案设计的 6 个核心价值做了顶层抽象 —— 前两条聚焦"能力整合"（统一工具面、载体全覆盖），中间两条聚焦"工程治理"（大结果、版本兼容），后两条聚焦"工程规范"（安全只读、可集成性）。值得注意的是价值点的数量（6 个）恰好与"6 大分析维度"对应。

### 表格 2：模块职责拆解

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

**解读**：此表是 10 个模块的"职责 + 路径 + 设计要点"三栏映射。设计上具有以下特征：(1) 唯一入口性 —— 服务入口层仅含 `create_server()` 一个注册入口；(2) 载体对称性 —— CSV/JSON 分析层各对应具体的文件类型，DB 层对应 SQLite；(3) Trace 工具深度最重 —— Trace 分析层下面嵌套了 Perfetto 工具层和连接管理层两个子模块；(4) 安全纵深防御 —— DB 层与 msprof-analyze 层均含独立的安全机制（前者 `_FORBIDDEN_PREFIXES`，后者 `subprocess.DEVNULL`）。

### 表格 3：工具注册全景

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

**解读**：此表共 17 个工具，可按数据载体聚类：(1) trace_view.json 载体 4 个工具（Flow / Slice / SQL / 重叠）；(2) kernel_details.csv 载体 2 个；(3) op_statistic.csv 载体 2 个；(4) 通用 CSV 载体 2 个；(5) profiler_info.json 载体 1 个；(6) communication_matrix.json 与 communication.json 载体各 1 个；(7) SQLite DB 载体 3 个（预览、外置、视图创建）；(8) 外部命令封装 1 个。命名规范上含 `_details`/`_statistic` 后缀的为聚合分析，含 `_info` 的为元信息查询，含 `_csv` 的为外置导出。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档在"可集成性"与启动时序图中显式提到 msprof-mcp 集成对象与上游协议：

- **msagent_design.md**（文末内部链接）：`msprof-mcp` 在启动时序图中作为"Host / MCP Host"出现，与 msAgent Profiler 形成上下游关系 —— msAgent 作为 MCP Host 端，通过 stdio 协议调用 `msprof-mcp` 提供的工具。该链接文档应描述 msAgent 作为 Profiler Agent 的设计，可与本文档的"工具注册全景"章节对照理解。
- **MCP 协议与 FastMCP 框架**：作为协议层依赖，定义了 `create_server()` 的注册方式与 stdio 传输规范。
- **Perfetto TraceProcessor Shell**（`resources/perfetto/trace_processor_shell`）：作为 Trace 分析的底层执行环境，由 ConnectionManager 调度。
- **msprof-analyze advisor**（外部二进制命令）：作为总体分析能力的实际执行体，被 `MsProfAnalyzer` 工具封装。
- **6 类 Profiling 数据载体**：trace_view.json / kernel_details.csv / op_statistic.csv / communication_matrix.json / communication.json / profiler_info.json / ascend_pytorch_profiler.db，构成本工具面的完整输入域。

---

## 【使用方法】

> 原文涉及：

- **运行方式**：`uvx msprof-mcp` 或本地源码方式运行。
- **集成客户端**：支持 Cherry Studio、Claude Desktop、msAgent 集成。
- **日志配置**：通过 `MSPROF_MCP_LOG_LEVEL` 环境变量控制日志级别，默认 `WARNING`。
- **传输协议**：MCP stdio 传输（`mcp.run(transport="stdio")`）。
- **入口函数**：`create_server()` 是唯一工具注册入口；`main()` 启动 stdio 传输。
- **数据库交互限制**：通过 `_FORBIDDEN_PREFIXES` 禁止 INSERT/UPDATE/DELETE 等写操作，SQL 预览受 `MAX_RESULT_CHARS` 限制。
- **大结果外置**：通过 `execute_sql_to_csv` 工具将超大查询结果导出为 CSV 文件，防止上下文膨胀。
- **视图创建选项**：`create_dispatch_view` 工具支持 `replace_existing` 选项（原文未给出更多细节）。

原文未涉及：CLI 参数列表、配置文件路径、PyPI 包名（仅提及"为测试、打包、PyPI 发布提供稳定边界"作为设计目标之一）。
