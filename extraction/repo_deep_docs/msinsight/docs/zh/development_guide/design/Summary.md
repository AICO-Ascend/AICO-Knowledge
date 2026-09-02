# Summary 设计文档

> 仓 `msinsight` · 路径 `docs/zh/development_guide/design/Summary.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msinsight/docs/zh/development_guide/design/Summary.md

# Summary 设计文档深度解读

## 【定位】
本文档是 msinsight 系统中 `cluster/summary` 页面（集群概览页）的端到端设计说明，覆盖集群数据导入（TEXT/DB 两种场景）、mstt 集群分析工具调用、各子区域（基本信息、并行策略、通信耗时、单卡详情）的前后端接口与数据来源、代码入口与变更流程，面向该页面的维护与扩展开发者。

## 【技术要点】

1. **两种数据场景并行支持**：
   - TEXT 场景依赖 `communication.json`、`communication_matrix.json`，需配置 `experimental_config.profiler_level = torch_npu.profiler.ProfilerLevel.Level1` 或 `Level2`。
   - DB 场景依赖 `analysis.db`，需设置 `export_type = torch_npu.profiler.ExportType.Db`，此时通常不再生成 JSON/CSV 文件。

2. **mstt 集群分析工具跨平台启动命令**：
   - Windows：`cluster_analysis.exe -d . -m mode`
   - Linux：`python3 cluster_analysis.py -d . -m mode`（多数 Linux 发行版自带 Python）
   - macOS：`cluster_analysis -d . -m mode`（与 Windows 类似使用 PyInstaller 打包）
   - DB 模式需附加 `--data_simplification` 参数。
   - `mode` 三种取值：`all`（全部）、`communication_time`（通信耗时）、`communication_matrix`（通信矩阵）。

3. **mstt 输出的两类产物结构**：
   - TEXT：`cluster_step_trace_time.csv`、`cluster_communication_matrix.json`、`cluster_communication.json`、`communication_group.json`，分别对应 `communication_matrix` 与 `communication_time` 两种 mode。
   - DB：单一 `cluster_analysis.db`。

4. **Summary 页面五大子区域对应五个 REST 接口命令**：
   - `summary/queryTopData`（基本信息）
   - `summary/set/parallelStrategy`（并行策略生成）
   - `parallelism/arrangement/all`（并行策略展示）
   - `parallelism/performance/data`（通信域内卡时间占比）
   - `summary/statistic`（单卡详情，文档未展开字段）

5. **并行策略分组算法（以 16 卡、`Algorithm = TP-CP-EP-DP-PP` 为例）**：按 `TP=2 → CP=2 → EP=1 → DP=2 → PP=2` 顺序分组，最终 16 卡归并为 1 组。其中 TP/PP 在显示上"用一个框包围"，CP/DP 在显示上"用两个框分开"。

6. **TEXT 与 DB 表名映射**（关键维护点）：
   - `cluster_base_info` ↔ `ClusterBaseInfo`（基本信息）
   - `step_statistic_info`（底层 `cluster_step_trace_time.csv`）↔ `ClusterStepTraceTime`（通信耗时）

## 【关键机制与数据】

**工作原理与数据流**：

1. **采集链路**：PyTorch 训练时开启 Profiler → 生成 `profiler_info.json`、`profiler_metadata.json` 以及 `ASCEND_PROFILER_OUTPUT` 目录（含通信 JSON 或 analysis.db） → 调用 mstt `cluster_analysis` 工具处理（原文：TEXT 场景需 `profiler_level` 为 `Level1`/`Level2`；DB 场景需 `export_type=Db`） → 输出 `cluster_analysis_output` 目录（TEXT 为 CSV/JSON 集合，DB 为 `cluster_analysis.db`） → 前端 Summary 页面通过后端 handler 读取这些产物渲染。

2. **并行策略生成的参数链路**：前端输入 TP/CP/EP/DP/PP 参数 → 调用 `summary/set/parallelStrategy` 设置策略 → 前端再调用 `parallelism/arrangement/all` 计算并展示卡组关系 → 通信耗时区域通过 `parallelism/performance/data` 从 `step_statistic_info`/`ClusterStepTraceTime` 读取耗时占比。

3. **性能数据**：原文未给出具体性能数字，仅约定"验证通信域内卡时间占比在不同 rank、step 或 iteration 条件下是否符合预期"。

4. **示例数据（原文）**：16 卡场景下 TP=2、CP=2、EP=1、DP=2、PP=2，初始 0~15 各一组，经 5 步分组最终变为 1 组。

5. **DB 模式额外约束**：原文"DB 格式数据通常还会附加 `--data_simplification`"。

## 【表格解读】

### 表格 1：mstt 集群分析工具启动方式（原文 §2.2）

| 平台 | 启动方式 |
| --- | --- |
| Windows | `cluster_analysis.exe -d . -m mode` |
| Linux | `python3 cluster_analysis.py -d . -m mode` |
| macOS | `cluster_analysis -d . -m mode` |

**逐行解读**：
- Windows 行：使用 `.exe` 可执行文件，直接执行即可，无需 Python 环境。
- Linux 行：使用 Python 脚本直接调用，依赖系统已安装的 Python 解释器（原文："多数 Linux 发行版默认带 Python 解释器"）。
- macOS 行：与 Windows 类似，使用打包后的二进制 `cluster_analysis`（无扩展名），通过 PyInstaller 打包以规避 macOS 用户可能未装 Python 的问题。
- 三种命令的 `-d .` 指定当前目录为分析输入目录，`-m mode` 指定分析模式。

### 表格 2：mstt 工具 mode 选项（原文 §2.2）

| mode | 说明 |
| --- | --- |
| `all` | 处理全部集群分析数据 |
| `communication_time` | 处理通信耗时相关数据 |
| `communication_matrix` | 处理通信矩阵相关数据 |

**逐行解读**：
- `all` 行：覆盖 TEXT/DB 所有集群分析的完整输出，性能开销最大。
- `communication_time` 行：仅生成通信耗时相关文件（对应 TEXT 下 `cluster_communication.json`）。
- `communication_matrix` 行：仅生成通信矩阵相关文件（对应 TEXT 下 `cluster_communication_matrix.json`、`cluster_step_trace_time.csv`、`communication_group.json`）。

### 表格 3：Summary 页面能力总览（原文 §3.1）

| 页面区域 | 接口命令 | TEXT 数据来源 | DB 数据来源 | 说明 |
| --- | --- | --- | --- | --- |
| 基本信息 | `summary/queryTopData` | `cluster_base_info` 表 | `ClusterBaseInfo` 表 | 展示集群任务、卡数、通信等顶部概要信息。 |
| 并行策略生成 | `summary/set/parallelStrategy` | 用户配置或文件读取的并行策略参数 | 用户配置或文件读取的并行策略参数 | 根据 TP/CP/EP/DP/PP 等参数生成并行策略。 |
| 并行策略展示 | `parallelism/arrangement/all` | 无固定数据表 | 无固定数据表 | 根据并行策略参数计算并展示卡组关系。 |
| 通信域内卡时间占比 | `parallelism/performance/data` | `step_statistic_info` 表，数据来自 `cluster_step_trace_time.csv` | `ClusterStepTraceTime` 表 | 展示通信域内不同卡的耗时占比。 |
| 详情 | `summary/statistic` | 单卡信息 | 单卡信息 | 展示单卡维度统计详情。 |

**逐行解读**：
- 基本信息行：唯一的差异在数据表名（TEXT 是蛇形 `cluster_base_info`，DB 是 PascalCase `ClusterBaseInfo`），均通过 `summary/queryTopData` 拉取集群任务、卡数、通信概要。
- 并行策略生成行：数据来源不是分析产物，而是用户在前端输入或从文件读取的并行策略参数；接口是写操作（`/set/`），用于"生成"策略。
- 并行策略展示行：标注"无固定数据表"，说明该区域是纯计算结果，由前端根据并行策略参数实时计算卡组关系。
- 通信耗时行：TEXT 数据来自 `step_statistic_info` 表，底层是 `cluster_step_trace_time.csv`；DB 对应 `ClusterStepTraceTime` 表。两者均用于展示通信域内慢卡或不均衡问题。
- 详情行：原文标注"单卡信息"，未明确具体表名；接口 `summary/statistic` 的字段本文档未展开。

### 表格 4：并行策略缩写含义（原文 §3.4）

| 缩写 | 含义 |
| --- | --- |
| TP | tensor parallel |
| CP | context parallel |
| EP | expert parallel |
| DP | data parallel |
| PP | pipeline parallel |

**逐行解读**：
- TP：张量并行，将单层矩阵运算切分到多卡。
- CP：上下文并行，长序列维度切分，多见于 Transformer 长上下文场景。
- EP：专家并行，MoE（Mixture of Experts）架构下不同专家分布到不同卡。
- DP：数据并行，同一模型在不同 batch 数据上并行训练。
- PP：流水线并行，将模型层切分到不同卡形成流水线。

### 表格 5：代码入口（原文 §4）

| 方向 | 代码入口 | 说明 |
| --- | --- | --- |
| 前端模块 | `modules/cluster` | Summary 与 Communication 同属 cluster 前端模块。 |
| 前端请求封装 | `modules/cluster/src/utils/RequestUtils.ts` | 可确认 Summary、Communication、parallelism 相关请求命令。 |
| 后端命令常量 | `server/src/modules/defs/ProtocolDefs.h` | 可确认请求命令字符串。 |
| 后端 Summary 模块 | `server/src/modules/summary` | 可确认 Summary handler、protocol、database/process 逻辑。 |
| 后端插件注册 | `server/src/modules/Plugins.cpp` | 可确认 Summary 插件是否注册。 |
| Communication 关联文档 | `Communication.md` | Summary 与 Communication 均依赖集群分析结果，数据来源存在关联。 |

**逐行解读**：
- 前端模块行：Summary 与 Communication 共享同一前端目录，维护时需注意相互影响。
- 请求封装行：所有 Summary/Communication/parallelism 的请求命令字符串（如 `summary/queryTopData`）应在该 TypeScript 文件中可追溯。
- 命令常量行：C++ 头文件 `ProtocolDefs.h` 是后端命令字符串的唯一权威定义，前后端命令一致性需以此为准。
- Summary 模块行：后端模块目录 `server/src/modules/summary` 包含 handler（路由）、protocol（协议序列化）、database/process（数据访问与处理）三层逻辑。
- 插件注册行：Summary 必须在此 `.cpp` 中注册插件，否则后端不会响应请求。
- Communication 文档行：明示 Summary 与 Communication 共用集群分析产物（`cluster_analysis_output`），任一变更需同步评估对另一页面的影响。

## 【公式解读】

原文无公式。

但文档中描述了一个**伪代码式的并行分组算法**，可形式化如下（按 Algorithm = `TP-CP-EP-DP-PP` 顺序）：

```
设 cards = [0, 1, ..., 15]
groups = [{c} for c in cards]        # 初始每卡一组，共 16 组

# TP=2: 相邻两组两两合并
groups = chunk_and_merge(groups, n=2, axis="TP")   # → 8 组，用一框包围

# CP=2: 相邻两组两两合并
groups = chunk_and_merge(groups, n=2, axis="CP")   # → 4 组，用两框分开

# EP=1: 不变化
groups = unchanged(groups)                         # → 4 组

# DP=2: 相邻两组两两合并
groups = chunk_and_merge(groups, n=2, axis="DP")   # → 2 组，用两框分开

# PP=2: 相邻两组两两合并
groups = chunk_and_merge(groups, n=2, axis="PP")   # → 1 组，用一框包围
```

**符号含义**：
- `cards`：参与并行计算的物理卡编号列表，原文示例为 0~15 共 16 卡。
- `groups`：当前层并行后的卡组集合，初始每卡一组。
- `chunk_and_merge(groups, n, axis)`：将当前 groups 按相邻顺序每 `n` 个合并为一组，`axis` 决定显示样式（TP/PP 一框包围，CP/DP 两框分开，原文未明确 EP 的样式）。
- 各步 `n` 即用户配置的 TP/CP/EP/DP/PP 取值，原文示例为 TP=2、CP=2、EP=1、DP=2、PP=2。

## 【关联】

1. **与 Communication 页面共享数据底层**：原文 §4 明确 Summary 与 Communication 同属 `modules/cluster` 前端模块，且都依赖 mstt `cluster_analysis` 输出的 `cluster_analysis_output` 目录；§3.5 维护提示中要求"慢卡、慢链路专家建议如依赖该数据，应同步验证 Summary 和 Communication 两侧展示"，说明两者数据存在共享与校验关系（详见关联文档 `Communication.md`）。

2. **与 mstt 集群分析工具（msprof-analyze）的依赖关系**：Summary 页面所有展示数据均来源于 mstt 工具的输出。TEXT 场景通过 `communication_matrix`/`communication_time` mode 产生 CSV/JSON；DB 场景需附加 `--data_simplification`。原文提供外部链接：`https://gitcode.com/Ascend/msprof-analyze/blob/master/README.md`。

3. **与 Profiler 采集层的依赖**：原文 §2.1 显式列出 Profiler 采集所需的 `profiler_level`（Level1/Level2）与 `export_type`（Db）配置项，并提供昇腾 Profiling 采集文档外部链接 `https://www.hiascend.com/document/detail/zh/mindstudio/82RC1/T&ITools/Profiling/atlasprofiling_16_0090.html`，说明 Summary 上游是昇腾 Profiler 数据采集层。

4. **TEXT 与 DB 双路径的内部映射关系**：`cluster_base_info` ↔ `ClusterBaseInfo`、`step_statistic_info` ↔ `ClusterStepTraceTime`，这是 Summary 页面最关键的双场景数据一致性约束，原文 §5 步骤 1、6 与 §6.2 都要求保证两类数据字段含义、单位、排序一致。

5. **并行策略参数上下游**：`summary/set/parallelStrategy`（写）→ `parallelism/arrangement/all`（读+计算）→ `parallelism/performance/data`（基于分组结果查询耗时占比），三者构成一条完整的策略配置链路。

## 【使用方法】

**启用方式/配置项/命令**（原文均有涉及）：

1. **Profiler 采集配置**（原文 §2.1）：
   - TEXT 场景：`experimental_config.profiler_level = torch_npu.profiler.ProfilerLevel.Level1` 或 `Level2`。
   - DB 场景：`export_type = torch_npu.profiler.ExportType.Db`。

2. **mstt 工具启动**（原文 §2.2）：
   - Linux：`python3 cluster_analysis.py -d . -m <mode>`
   - Windows：`cluster_analysis.exe -d . -m <mode>`
   - macOS：`cluster_analysis -d . -m <mode>`
   - DB 场景附加：`--data_simplification`
   - `<mode>` 取值：`all` / `communication_time` / `communication_matrix`

3. **Summary 页面后端接口命令**（原文 §3.1）：
   - `summary/queryTopData`
   - `summary/set/parallelStrategy`
   - `parallelism/arrangement/all`
   - `parallelism/performance/data`
   - `summary/statistic`

4. **代码入口定位**（原文 §4）：
   - 前端请求封装：`modules/cluster/src/utils/RequestUtils.ts`
   - 后端命令常量：`server/src/modules/defs/ProtocolDefs.h`
   - 后端 Summary 实现：`server/src/modules/summary`
   - 后端插件注册：`server/src/modules/Plugins.cpp`

5. **新增/修改能力的开发步骤**（原文 §5）：按顺序为 ①确认数据场景（TEXT/DB）→ ②确认数据来源（`cluster_analysis_output` CSV/JSON、`cluster_analysis.db` 或用户输入）→ ③补充后端查询/计算逻辑 → ④更新协议字段与命令常量 → ⑤同步前端展示、i18n 文案 → ⑥验证 TEXT/DB 一致性 → ⑦同步本文档。

6. **验证方法**（原文 §6）：静态验证（图片路径、接口命令、表名、外部链接）+ 功能验证（导入 TEXT/DB 数据、修改 TP/CP/EP/DP/PP 参数、不同 rank/step/iteration 筛选、缺少产物/关键表/空数据/字段缺失等异常场景）。

## 图文联合解读

- `ff203f07-5738-41e8-9432-fade7bf2bd90.png`: **图文联合解读：**

图中描绘 Summary 页面数据处理流程：导入集群数据后判断 `cluster_analysis_output` 是否存在。存在则直接解析，不存在则调用 mstt 工具分两步生成 `cluster_communication_matrix.json` 等中间文件。两路径均经异步 step1（解析矩阵）和 step2（解析耗时），最终汇聚到「展示通信矩阵」和「展示通信耗时」节点，论证了页面采用"已缓存则复用、未生成则 mstt 两步处理"的并行化数据流策略，与文档"Summary 与 Communication 依赖 mstt 集群分析结果"及"step1 输出矩阵、step2 输出耗时"的技术路径完全一致。
- `9d03b22e-a128-4255-b4ea-25f31eb1b79b.png`: **图文联合解读：**

1) **图示内容**：流程图描述 Summary 页面的预处理逻辑。从"导入集群数据"出发，经菱形判断节点"cluster_analysis_output 已存在"——若"否"，进入 mstt 工具进行"解析集群数据"，再流向"展示"；若"是"，则跳过解析直接"展示"，最终"结束"。

2) **技术结论**：mstt 解析结果（cluster_analysis_output）具备缓存复用机制；首次导入需经 mstt 处理，后续导入直接消费缓存产物。

3) **与文档关系**：图示与文档 §2.2 "Summary 和 Communication 页面依赖 mstt 集群分析工具的处理结果"相印证，将文本中"依赖"的抽象描述具象化为带分支条件的数据预处理管道。
- `c9371099-f385-47ae-be4c-d48fc09c943b.png`: **图文联合解读：**

1) **图示内容**：图为 `cluster_base_info` 数据库表配置视图，列字段涵盖 `id`、`file_path`、`ranks`（0-3，4卡）、`steps`、`collect_start_time`、`collect_duration`、`data_size`、`stages`、`pp_stages`、并行维度（`dp/pp/tp/cp/ep_size`）及 `algorithm`。数据行显示一次 `megatron-lm` 训练 profile（tp/dp/pp=2，cp/ep=1，stages 编号 0–7）的元信息入库。

2) **技术结论**：Summary 页面的"集群概览/并行策略"读自该 SQLite 表，TEXT 与 DB 场景需先经 mstt `cluster_analysis.py` 落库，才能在 Web 端呈现并行度、卡号与时长。

3) **与文档关系**：对应文档 §2 数据来源与 §1 范围——证明 DB 场景下原始 `.db` 经 mstt 抽取为结构化元表，是 Summary 渲染的事实依据。
- `e4e29247-0f8e-4029-9f5e-81692fcd9727.png`: **图文联合解读：**

1. **图中所画**：数据库工具（如 DBeaver）打开的 `cluster_base_info` 表结构与首行样例。列包括 `id/ranks/steps/collect_start_time/collect_duration/algorithm/dp_size/pp_size/tp_size/cp_size/ep_size/level`，首行记录 algorithm=Megatron-LM(t)，dp/pp/tp_size 均为 1，cp/ep_size 与时间字段为 Null，level=undefined。

2. **论证的技术结论**：DB 场景下 Summary 页面集群级元数据（含并行维度和算法信息）以关系表形式持久化在 `analysis.db` 中，是页面展示"集群概览"与"并行策略"的数据底座；空值字段说明尚未启用 CP/EP 切分且采集时间未填充。

3. **与文档论点关系**：印证 §2.1 "DB 场景"所述 `analysis.db` 文件即为 Summary 数据的最终承载形式，并为后续集群分析工具（mstt）提供结构化输入。
- `43c5975a-cdfe-4b5f-81fe-81b3fff26b61.png`: 1) **图示内容**：Parallel Strategy Analysis 配置面板，含 Algorithm 下拉（Megatron-LM(tp-cp-ep-dp-p...)）、PP=2、TP=2、CP=1、DP=2、EP=1 输入框及 Generate 按钮。

2) **技术结论**：该组件用于基于 mstt 集群分析结果，手动指定并行维度规模后生成分布式策略视图，验证通信开销与并行切分匹配度。

3) **与文档关系**：对应文档中"集群概览与并行策略"展示逻辑，PP/TP/CP/DP/EP 参数即通信域性能分析的前置输入，呼应 2.1 节通信数据（communication.json）所依赖的并行拓扑。
- `ead77096-c3fb-44e3-b45f-98a3e76526ed.png`: ## 图文联合解读

**1) 图中内容**
顶部 Tab 展示并行维度逐级展开流程（DP → DP+PP → DP+PP+CP → DP+PP+CP+TP，当前选中最后一级）；下方提供 PP/TP/CP/DP/EP 五种并行策略勾选与 Data Type 下拉。本例仅勾选 **Data Parallel**，主区域以 8 张卡（0–7）展示，紫色边框圈出 **两个 DP 组**：`{0,1,4,5}` 与 `{2,3,6,7}`，底部图例对应五种颜色编码。

**2) 技术结论**
即使维度 Tab 已推进到"DP+PP+CP+TP"全维度，实际可视化仍按用户勾选的并行策略进行分组——即 **Tab 决定可选维度范围，Checkbox 决定实际渲染**。此处 DP=2，每组内含 4 卡，验证 Summary 支持多级并行组合下的卡归属还原。

**3) 与文档关系**
呼应文档第 1 节"展示逻辑"与并行策略维护说明：图表直观印证了 Summary 对**并行维度逐级叠加、策略可任意勾选**的设计，便于开发者快速核验集群拓扑与卡分组正确性。
- `b35ef53b-6299-4f9b-bb7e-f6515bcdf522.png`: **图示内容**：悬浮卡片（Index 0，名称 `dp0-pp0-tp0`）展开的详情面板，呈现单卡汇总指标：通信占比 21.67%、计算占比 57.19%、Bubble/Stage 为 0、通信(未重叠) 184175.94us、计算通信重叠 66888.93us、计算 662770.03us、空闲 311903.13us。

**技术结论**：每张卡片对应一个并行 rank（dp/pp/tp 维度），通过计算与通信的重叠/未重叠分解，量化流水并行效率。

**与文档关系**：对应文档"单卡详情"展示逻辑，说明 Summary 页面如何以 rank 为粒度呈现通信域性能与并行策略。
- `67a348ed-3187-4580-a756-3134896d0c59.png`: **1) 图中内容**：双轴组合图，X 轴为 Rank0–7 共 8 个并行卡；左 Y 轴为 Time(μs) 0–1.2M，右 Y 轴为 Ratio 0–60%。堆叠柱含 Computing(未重叠/深蓝)、Computing_Communication Overlap(绿)、Communication(未重叠/青)、Free(紫)、Preparing(橙)；两条折线为 Communication Ratio(红≈20%)与 Computing Ratio(蓝≈58%)。顶部含 Step/Rank Group/Order By/Top 筛选器。

**2) 技术结论**：各 Rank 时间构成高度一致，Computing 占比稳定约 58%，Communication 约 20%，空闲约 15%，说明集群负载均衡，并行策略未现明显瓶颈。

**3) 与文档关系**：呼应文档"集群概览、并行策略、通信域性能"展示逻辑，以可视证据印证 mstt 集群分析后 Summary 页面的核心展示维度。
- `0bbea588-d08d-4b4d-96ee-5e14cfac295f.png`: 1) 图示 DB 场景下 `step_statistic_info` 表的字段结构，列包含 rank_id/step_id/stage_id 及 compute_time、pure_communic、overlap_comm、bubble_time、free_time 等聚簇性能指标，多 rank 多 step 行展示了并行维度的统计聚合。

2) 论证 Summary 页所呈现的并行策略、通信域与计算耗时等聚合数据，均来自该数据库表，按 (rank, step) 维度逐行落库，为可视化提供量化基础。

3) 对应文档 2.1 节 DB 场景：当 `export_type=Db` 时，分析结果入库而非生成 JSON，Summary/Communication 页直接读取此表驱动展示。
- `049e4e63-f3b5-42fd-9afb-68dabd723059.png`: **图文联合解读：**

1）图示内容：Summary 页面顶部给出 Advice 告警（提示 "Communication(Not Overlapped)" 最大差值达 62787.4μs，提示通信存在异常）；下方分别呈现 "Computing Detail (Rank 0)" 和 "Communication Detail (Rank 0)" 两张表格，分别按 Accelerator Core（AI_CORE/AI_VECTOR_CORE/MIX_AIC/MIX_AIV）列出计算耗时，并按 HCCL 列出通信 Not Overlapped 与 Overlapped 耗时，每行可展开 Details。

2）技术结论：Summary 页具备自动诊断与分级下钻能力——既能在跨 Rank 通信失衡时主动告警，又能按核类型拆解计算与通信耗时（含 Overlap 拆分），定位性能瓶颈。

3）与文档关系：印证 §2.1 中 communication.json 作为通信耗时可视化数据来源的论点，直观体现 Summary 页面"集群概览 + 通信域性能 + 单卡详情"的展示逻辑。
