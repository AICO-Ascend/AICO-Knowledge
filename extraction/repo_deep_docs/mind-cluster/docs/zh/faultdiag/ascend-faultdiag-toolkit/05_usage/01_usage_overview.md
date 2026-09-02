# 特性概览

> 仓 `mind-cluster` · 路径 `docs/zh/faultdiag/ascend-faultdiag-toolkit/05_usage/01_usage_overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docs/zh/faultdiag/ascend-faultdiag-toolkit/05_usage/01_usage_overview.md

# 文档深度解读：ascend-fd-tk 特性概览

## 【定位】

本篇是 ascend-fd-tk（昇腾故障诊断工具套件）"使用方式"章节的总览文档，旨在以一张"全景图"的形式说明该工具提供了哪些能力、如何调用、产物落在哪里、不同场景下该走哪条命令链路——即解决**"用户拿到工具后不知道该用哪种模式、产物放哪里、按什么顺序敲命令"**的问题。

---

## 【技术要点】

1. **两种使用模式**：交互式（`>>>` 提示符逐步输入） vs 非交互式（一行命令全流程），分别面向"临时调试/问题排查"与"自动化运维/定时任务/脚本集成"两类场景。
2. **平台相关的家目录**：Linux 平台 `~/.ascend-faultdiag-toolkit/`（基于用户主目录 `~`）；Windows 平台为**当前工作目录**下的 `.ascend-faultdiag-toolkit/`，这一点是与 Linux 行为不同的地方。
3. **日志轮转策略**：工具运行日志单文件上限 **10MB**；达到阈值自动触发日志切分；归档命名 `ascend-fd-tk.log.1 / .2 / …`，**编号越小代表日志越新**；最多保留 **5 份**归档日志。
4. **三类子路径**：① `cache/` 清洗结果缓存（按 host/bmc/switch 分类落盘为 JSON）；② `logs/ascend-fd-tk.log` 运行日志；③ `report/` 诊断 / 巡检报告输出目录；外加 `encrypted_conn_config` 用于在线连接配置 `conn.ini` 的加密存放。
5. **四类典型场景命令流程**：在线诊断、离线诊断、分批诊断、客户定制化巡检——共享"清理缓存 → （可选）配置目录 → 配置连接/日志 → 采集 → 诊断/巡检"的五段式骨架。
6. **报告文件命名规范**：诊断报告为 `diag_report_{YYYYMMDD_HHMMSS}.xlsx`，巡检报告为 `inspection_errors.csv`——前者按时间戳组织，后者为巡检问题条目列表。

---

## 【关键机制与数据】

- **数据流概览（原文）**：原文将流程抽象为"采集 → 清洗 → 诊断 / 巡检"三级管道：
  - 在线模式：`auto_collect_diag` / `auto_collect` 一步完成采集；离线模式需先用 `set_host_dump_log` / `set_bmc_dump_log` / `set_switch_dump_log` 把已落盘的 dump 日志喂入工具。
  - 采集/清洗产物进入 `家目录/cache/`（按设备 IP 或目录名落盘的 JSON 文件），作为后续 `auto_diag` / `auto_inspection` 的输入。
  - 报告产物进入 `家目录/report/`，形态为 `diag_report_{YYYYMMDD_HHMMSS}.xlsx`（诊断）或 `inspection_errors.csv`（巡检）。
- **采集源分类（原文）**：三类——**host**、**bmc**、**switch**，对应三类 `set_*_dump_log` 命令和 `cache/` 下的三种子分类。
- **核心命令清单（原文）**：`clear_cache`、`set_config_dir`（可选）、`set_conn_config`、`set_host_dump_log` / `set_bmc_dump_log` / `set_switch_dump_log`、`auto_collect_diag`、`auto_collect`、`auto_diag`、`auto_inspection`。
- **性能 / 容量数据（原文）**：日志单文件 **10MB** 阈值、归档文件最多 **5 份**——其余性能数字原文未给出。

---

## 【表格解读】

### 表格 ①：工具使用方式

| 使用方式 | 适用场景 | 特点 |
|------|----------|------|
| 交互式  | 临时调试、问题排查、逐步操作 | 进入 `>>>` 提示符，逐条输入命令 |
| 非交互式 | 自动化运维、定时任务、脚本集成 | 一行命令完成全流程 |

逐行解读：
- **交互式**：用户进入 REPL 风格的 `>>>` 提示符后逐条敲命令；适合"一步一看结果"的临时调试与逐步排查。
- **非交互式**：将全部流程收敛为单行命令，便于嵌入运维脚本、定时任务与 CI/CD 自动化场景。

---

### 表格 ②：家目录目录结构

| 路径 | 用途 |
|------|------|
| `家目录/cache/` | 清洗结果缓存信息（host / bmc / switch 分类，按照设备 IP 或目录名落盘的 JSON 文件） |
| `家目录/logs/ascend-fd-tk.log` | 工具运行日志 |
| `家目录/report/` | 诊断 / 巡检报告输出目录（`diag_report_{YYYYMMDD_HHMMSS}.xlsx` / `inspection_errors.csv`） |
| `家目录/encrypted_conn_config` | 在线连接配置文件 `conn.ini` 加密后的文件 |

逐行解读：
- **`cache/`**：清洗阶段产出的结构化数据，按 host / bmc / switch 三大类再按"设备 IP 或目录名"细分子目录，文件形态为 JSON——是后续 `auto_diag` / `auto_inspection` 的数据底座。
- **`logs/ascend-fd-tk.log`**：工具自身的运行日志；受 10MB 上限 + 5 份归档的轮转策略约束（见原文 NOTE）。
- **`report/`**：用户最终可见的报告落地处；诊断结果为带时间戳的 Excel，巡检问题为 CSV。
- **`encrypted_conn_config`**：将在线模式必需的 `conn.ini`（含 IP、凭据等敏感信息）加密后存放，避免明文落盘。

---

### 表格 ③：特性列表

| 特性 | 说明 |
|------|------|
| [日志采集](02_log_collection.md)与[日志清洗](03_log_parse.md) | 在线模式自动收集并清洗；离线模式提前收集日志再清洗 |
| [故障诊断](04_fault_diagnosis.md) | 对清洗后的数据进行故障检测和根因分析，生成 Excel 诊断报告 |
| [故障巡检](05_fault_inspection.md) | 按不同客户类型预定义规则批量健康检查，生成 CSV 巡检报告 |

逐行解读：
- **日志采集 + 日志清洗**：构成"采—洗"基础能力；在线模式由工具自动完成采+洗，离线模式则是"用户预先采 + 工具只负责洗"，适配无法远程访问设备的场景。
- **故障诊断**：以清洗后的 JSON 为输入，做故障检测 + 根因分析，输出 `diag_report_{YYYYMMDD_HHMMSS}.xlsx`。
- **故障巡检**：与诊断不同之处在于"按客户类型预定义规则"做批量健康检查，更偏向周期性预防；输出 `inspection_errors.csv`（仅记录异常条目，而非全量报告）。

---

### 表格 ④：场景命令流程

| 流程              | 适用场景 | 核心步骤 |
|-----------------|----------|----------|
| [在线诊断流程](07_online_diagnosis.md) | 设备可访问（IP / 凭据齐备） | `clear_cache` → `set_config_dir`（可选）→ `set_conn_config` → `auto_collect_diag` 或 `auto_collect` + `auto_diag` |
| [离线诊断流程](08_offline_diagnosis.md)      | 仅日志可获取 | `clear_cache` → `set_config_dir`（可选）→ `set_host_dump_log` / `set_bmc_dump_log` / `set_switch_dump_log`（任选）→ `auto_collect_diag` 或 `auto_collect` + `auto_diag` |
| [分批诊断流程](09_batch_diagnosis.md)      | 多网络平面、设备数量大 | `clear_cache` → `set_config_dir`（可选）→ 重复 N 次[`set_conn_config` + `auto_collect` 或 `set_host_dump_log` / `set_bmc_dump_log` / `set_switch_dump_log`（任选）+ `auto_collect`] → `auto_diag` |
| [客户定制化巡检](10_customized_inspection.md)     | 按不同客户类型预定义规则批量健康检查 | `clear_cache` → `set_config_dir`（可选）→ `set_conn_config` 或 `set_host_dump_log` / `set_bmc_dump_log` / `set_switch_dump_log`（任选）→ `auto_collect` + `auto_inspection` |

逐行解读：
- **在线诊断**：典型前置是 `clear_cache` 清旧缓存、`set_conn_config` 写入在线连接配置（凭据加密后落 `encrypted_conn_config`）；核心差异命令是 `auto_collect_diag`（采+诊合一）或 `auto_collect + auto_diag`（拆开执行，便于人工介入中间环节）。
- **离线诊断**：与在线流程的差异点是**没有 `set_conn_config`**，改用三类 `set_*_dump_log` 把已存在的 dump 日志喂入；后续"采+诊"步骤形态一致。
- **分批诊断**：面向"多网络平面 + 设备数量大"场景，将"配连接 + 采集"循环执行 N 次（每次可对应不同网络平面 / 设备子集），最后统一调用一次 `auto_diag`——即将"采"和"诊"解耦以应对大批量场景。
- **客户定制化巡检**：流程骨架与诊断一致，但末端是 `auto_inspection`（而非 `auto_diag`），输出的是 `inspection_errors.csv`；输入源既可来自在线连接，也可来自离线 dump 日志——即巡检与诊断在命令链路上复用同一套"采"环节，仅末端动作不同。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文作为"使用方式"章节的总览页，本身**不展开**具体步骤，而是通过链接把读者分发到下游各专项文档：

- **特性 ↔ 命令流程**：
  - "[日志采集](02_log_collection.md)与[日志清洗](03_log_parse.md)" → 是四条流程（在线/离线/分批/巡检）中"采集阶段"的实现细节页面。
  - "[故障诊断](04_fault_diagnosis.md)" → 对应"在线诊断流程 / 离线诊断流程 / 分批诊断流程"末端 `auto_diag` 的内部逻辑。
  - "[故障巡检](05_fault_inspection.md)" → 对应"客户定制化巡检"流程末端 `auto_inspection` 的内部逻辑。
- **流程间关系**：四条场景流程共享同一个五段式骨架（`clear_cache` → `set_config_dir` 可选 → 配连接/日志 → 采集 → 诊断/巡检），差异仅在第 3、4、5 步的命令选型——本文相当于给出了一张"流程族谱"，把"输入可达性"（在线 vs 离线）、"规模"（单批 vs 分批）、"目的"（诊断 vs 巡检）三个维度串起来。
- **上下游数据贯通**：`cache/`（清洗结果）→ `auto_diag` / `auto_inspection` → `report/`（诊断 Excel / 巡检 CSV）；`encrypted_conn_config` 又是 `set_conn_config` 的输出与后续采集命令的输入凭据来源。

---

## 【使用方法】

### 启用方式（原文）
- 工具以 **交互式（`>>>` 提示符）** 或 **非交互式（一行命令）** 两种方式运行；家目录在 Linux 为 `~/.ascend-faultdiag-toolkit/`，在 Windows 为**当前工作目录**下的 `.ascend-faultdiag-toolkit/`。

### 通用命令骨架（原文）
任意场景的入口均为 `clear_cache`（清理 `cache/` 旧数据），其后按场景选择：

| 场景 | 关键命令链 |
|------|------|
| 在线诊断 | `clear_cache` → `set_config_dir`（可选）→ `set_conn_config` → `auto_collect_diag` 或 `auto_collect + auto_diag` |
| 离线诊断 | `clear_cache` → `set_config_dir`（可选）→ `set_host_dump_log` / `set_bmc_dump_log` / `set_switch_dump_log`（任选）→ `auto_collect_diag` 或 `auto_collect + auto_diag` |
| 分批诊断 | `clear_cache` → `set_config_dir`（可选）→ 重复 N 次 `set_conn_config`/`set_*_dump_log` + `auto_collect` → `auto_diag` |
| 客户定制化巡检 | `clear_cache` → `set_config_dir`（可选）→ `set_conn_config` 或 `set_*_dump_log`（任选）→ `auto_collect + auto_inspection` |

### 配置项与产物（原文）
- **配置目录**：`set_config_dir` 设置（可选步骤，原文未给出具体配置项内容）。
- **运行日志**：`家目录/logs/ascend-fd-tk.log`，单文件 10MB 上限，最多 5 份归档（命名 `ascend-fd-tk.log.1`…`ascend-fd-tk.log.5`，编号越小越新）。
- **报告产物**：
  - 诊断：`家目录/report/diag_report_{YYYYMMDD_HHMMSS}.xlsx`
  - 巡检：`家目录/report/inspection_errors.csv`

> 注：原文未涉及具体配置项字段（如 `conn.ini` 内的 IP/凭据格式、`set_config_dir` 接受的参数等），这些细节需进入对应专项文档（02_log_collection.md / 04_fault_diagnosis.md / 07_online_diagnosis.md 等）查阅。
