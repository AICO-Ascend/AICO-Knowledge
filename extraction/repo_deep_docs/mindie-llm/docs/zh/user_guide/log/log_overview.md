# 日志简介

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/log/log_overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/log/log_overview.md

# 昇腾 MindIE 日志简介文档 · 一体化深度解读

---

## 【定位】

本文档是 MindIE 大模型推理引擎日志体系的概览性文档，**解决两个问题**：一是界定 MindIE 日志的两大分类（安全审计日志 / 运行调试日志）的语义边界；二是统一定义 MindIE 全组件（motor、server、llm、llmmodels、sd）的日志记录格式与字段含义，为后续日志级别配置（setting_log_level.md）和日志内容配置（configuring_log_content.md）提供前置约定。

---

## 【技术要点】

1. **日志二分法**：MindIE 日志按内容分为 **安全审计日志**（登录认证、账户管理、访问控制、网络攻击等安全事件相关）和 **运行调试日志**（业务与调试过程中产生的其他日志），二者语义互斥、归属明确。
2. **统一日志格式**：所有组件日志遵循同一模板 —— `[date time] [pid] [tid] [组件名称] [大写日志级别] [file:line] : [error code] [*] log message`，其中加粗的 `date time`、`组件名称`、`大写日志级别`、`log message` 为**必选字段**。
3. **组件白名单**：组件名称的可选枚举为 **`[motor, server, llm, llmmodels, sd]`** 共 5 个值，对应 MindIE 引擎的五大功能模块。
4. **子模块前缀机制**：格式中的 `*` 是一个条件占位符 —— **仅当组件内部存在子组件或更小功能模块时**，才在日志信息前呈现子模块信息，原文以 NOTE 说明（`*：` 表示如果组件内有子组件或者更小的功能模块，会在日志信息前进行呈现）。
5. **可选字段开关**：非必选字段的输出受环境变量 **`MINDIE_LOG_VERBOSE`** 控制，通过该变量可控制可选信息是否落盘，具体配置入口在 configuring_log_content.md。
6. **错误码外联**：Critical 级别及部分 Error 级别日志会携带 error code，错误码的查询入口为昇腾官网的《MindIE 错误码参考》（`mindie_log_0072.html`）。

---

## 【关键机制与数据】

- **日志格式模板（原文）：** 
  ```
  [date time] [pid] [tid] [组件名称] [大写日志级别] [file:line] : [error code] [*] log message
  ```
  该模板是 MindIE 全组件统一遵循的串行输出规范，字段以空格或冒号分隔，`error code` 前用冒号 `:` 与前段隔开，`log message` 前保留一个空格。

- **必选/可选字段切分机制（原文）：** 原文明确指出"**加粗内容为日志的必选内容**，其余字段为日志的可选信息"——即 `date time`、`组件名称`、`大写日志级别`、`log message` 四者**始终输出**；`pid`、`tid`、`file:line`、`error code`、`*` 这五项受 `MINDIE_LOG_VERBOSE` 调控。

- **子模块前缀条件（原文）：** `*` 占位符是**条件渲染**的，并非无条件输出 —— 当且仅当组件内嵌套有子组件时才会触发该段前缀。

- **日志级别体系（原文）：** 文档未给出具体级别集合，仅通过内部链接指向 `setting_log_level.md#table1`；该表存储日志级别的具体定义（如 DEBUG / INFO / WARNING / ERROR / CRITICAL 等，需参考链接文档），原文未直接列出级别数量。

- **错误码来源（原文）：** 仅 Critical 级别**全部**携带错误码；Error 级别为**部分**携带，故 error code 的出现频率与日志级别强相关。

- 性能数据 / 吞吐数据 / 容量限制：原文**未涉及**。

---

## 【表格解读】

原文包含 1 张表（表 1：日志字段说明），逐字还原如下：

| 字段 | 说明 |
|---|---|
| **date time** | 日期时间。 |
| pid | 进程号。 |
| tid | 线程号。 |
| 组件名称 | MindIE 的组件名称，有以下选项：[motor，server，llm，llmmodels，sd]。 |
| **大写日志级别** | 日志级别的大写形式，日志级别请参见[表 1 日志级别](setting_log_level.md#table1)。 |
| file:line | 文件名:代码行号。 |
| error code | Critical 级别和部分 Error 级别日志的错误码，错误码请参见《[MindIE 错误码参考](https://www.hiascend.com/document/detail/zh/mindie/300/ref/errorcodereference/mindie_log_0072.html)》。 |
| **log message** | 具体错误信息。 |

**逐行解读：**

- **date time**（加粗 / 必选）：时间戳，是日志可追溯性的基础，无此字段则日志不可排序、不可定位事件顺序。
- **pid**（可选）：进程号，用于多进程场景下区分不同推理实例或 worker 进程。
- **tid**（可选）：线程号，辅助定位同一进程内多线程并发时的日志来源。
- **组件名称**（加粗 / 必选）：取值限定为 `[motor, server, llm, llmmodels, sd]` 五选一，对应 MindIE 引擎内部的固定模块命名空间，是日志过滤与路由的关键维度。
- **大写日志级别**（加粗 / 必选）：必须为大写形式（如 `INFO` 而非 `info`），级别集合未在本表列出，通过内部链接跳转到 `setting_log_level.md#table1` 查看。
- **file:line**（可选）：源代码文件名与行号，便于从日志反查代码位置；其中冒号是字段内分隔符（`file:line`），与日志主格式中 `:` 的角色不同。
- **error code**（可选）：仅 Critical 和部分 Error 级别才有，是结构化的错误分类标识，查询入口为昇腾官网外链。
- **log message**（加粗 / 必选）：人类可读的具体描述，是日志语义的主要载体。

加粗行（date time、组件名称、大写日志级别、log message）即原文标注的必选字段集合。

---

## 【公式解读】

原文未使用 LaTeX 或严格伪代码公式，但给出**日志格式模板**，本质是一条**输出格式规约**，逐字保留并解释如下：

$$
\texttt{[date time]\; [pid]\; [tid]\; [组件名称]\; [大写日志级别]\; [file:line]\; : \; [error code]\; [*]\; log message}
$$

| 符号 / 占位符 | 含义与作用 |
|---|---|
| `[date time]` | 日期时间，必选 |
| `[pid]` | 进程号，可选，受 `MINDIE_LOG_VERBOSE` 控制 |
| `[tid]` | 线程号，可选 |
| `[组件名称]` | 取值 ∈ {motor, server, llm, llmmodels, sd}，必选 |
| `[大写日志级别]` | 必选，级别定义见 `setting_log_level.md#table1` |
| `[file:line]` | 源码定位，可选 |
| `:` | 固定分隔符，把错误码区段与前段隔开 |
| `[error code]` | 错误码，仅 Critical 和部分 Error 出现 |
| `[*]` | 条件占位符：仅当组件存在子模块时，才渲染子模块前缀 |
| `log message` | 必选的具体消息文本 |

注：原文无独立的数学公式或算法伪代码。

---

## 【关联】

本文档处于 MindIE 日志文档体系的**入口层（Overview）**，与其他模块的关系如下：

- **下游 1 — 日志级别配置**：`setting_log_level.md#table1`。本文档将"大写日志级别"字段的取值集合外联到该文档的"表 1 日志级别"，构成"格式定义 → 级别枚举"的依赖链。
- **下游 2 — 日志内容配置**：`configuring_log_content.md`。本文档将"必选/可选字段切换"的具体配置方法外联到该文档，依赖变量为 `MINDIE_LOG_VERBOSE`，形成"字段定义 → 字段开关"的依赖链。
- **外联 — 错误码体系**：通过《MindIE 错误码参考》（昇腾官网 `mindie_log_0072.html`）提供 error code 的查询入口，建立 MindIE 日志与昇腾全域错误码体系的映射。
- **横向 — 五大组件**：组件字段将 motor / server / llm / llmmodels / sd 五个组件模块在同一格式下统一，意味着任何一个组件的日志落盘都要遵循本文档定义的串行格式。

简言之，本文档是 MindIE 日志体系的**总纲**，本身不提供配置细节，仅作为其他三份配套文档的"前置约定"存在。

---

## 【使用方法】

本文档为概览性文档，不直接提供启用命令。其涉及的可配置项与入口如下：

- **环境变量**：`MINDIE_LOG_VERBOSE` —— 用于控制日志中的**可选字段**（pid、tid、file:line、error code、* 子模块前缀）是否输出。具体取值与生效方式请参见 [configuring_log_content.md](configuring_log_content.md)。
- **日志级别设置**：通过 [setting_log_level.md](setting_log_level.md) 中的"表 1 日志级别"定义具体级别集合与切换方式。
- **错误码查询**：通过昇腾官网《MindIE 错误码参考》查阅 Critical / Error 级别日志对应的 error code。
- **如何区分日志类型**：登录认证、账户管理、访问控制、网络攻击等安全事件归入**安全审计日志**；其他业务与调试日志归入**运行调试日志**——文档仅给出语义划分原则，未给出开关命令（原文未涉及）。

原文未涉及的项：日志落盘路径、滚动策略、保留时长、采样率、远程发送等运维细节均**不在本文档范围内**，需查阅 MindIE 其他配套文档。
