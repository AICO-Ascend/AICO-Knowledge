# Memory部分设计文档

> 仓 `msinsight` · 路径 `docs/zh/development_guide/design/Memory.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msinsight/docs/zh/development_guide/design/Memory.md

# Memory 模块设计文档深度解读

## 【定位】

本文档面向需要维护内存调优、对比和筛选能力的开发者，系统说明 MindStudio Insight 中 **Memory 页面的前后端数据流、主要视图、数据来源和查询能力**，覆盖 TEXT 与 DB 两类数据场景下的动态图、静态图、组件级视图全链路。

---

## 【技术要点】

1. **三类视图与两类数据场景**
   - 视图维度：动态图、静态图、组件视图
   - 数据维度：TEXT、DB

2. **文件解析入口**
   - 统一入口：`ImportActionHandler`
   - TEXT 解析：`Memory::MemoryParse::Instance().Parse()`，解析后会**写入数据库**
   - DB 解析：`FullDb::FullDbParser::Instance().Parse()`，解析**基本保持原样**

3. **后端三层目录结构（路径前缀 `server/src/modules/memory/`）**
   - `protocol`：JSON 与 request/response 结构体转换
   - `database`：查询 `TextMemoryDataBase` 与 `DbMemoryDataBase`
   - `handler`：具体业务查询与比对逻辑

4. **已确认的 5 个 handler（查询职责）**
   - `QueryMemoryOperatorHandler`：动态图表格
   - `QueryMemoryStaticOperatorListHandler`：静态图表格
   - `QueryMemoryViewHandler`：动态图折线图
   - `QueryMemoryStaticOperatorGraphHandler`：静态图折线图
   - `QueryMemoryComponentHandler`：组件级表格

5. **视图选择与分组**
   - 通用：`rankId`、分组方式
   - DB 额外：`hostName`（与 `rankId` 组合可定位单卡）
   - 分组方式三类：全局、流、组件

6. **三类视图的数据来源映射**
   - 动态图：折线图 → `memory_record.csv`；表格 → `operator_memory.csv`
   - 静态图：折线图 → `memory_record.csv` + `static_op_mem.csv`；表格 → `static_op_mem.csv`
   - 组件视图：折线图 → `memory_record.csv`；表格 → `npu_module_mem.csv`

7. **折线图数据组织（C++ 标准容器）**
   - 图例：`std::vector<std::string> legends`
   - 折线：`std::vector<std::vector<std::string>> lines`
   - 关系：`lines[index]` 对应一条横坐标位置的完整数据，与 `legends` 顺序一一对应

8. **表格筛选能力**：名称模糊查询、size 上下界筛选、时间范围框选联动、排序；"Only show allocated or released within the selected interval" 勾选项仅显示选中区间内申请/释放相关算子；**组件视图不支持查询**

---

## 【关键机制与数据】

### 工作原理（数据流）

- **解析路径**：前端导入文件 → `ImportActionHandler` → 按格式分派到 TEXT 或 DB parser → TEXT 落库 / DB 保留原样
- **查询路径**：前端 → handler（业务逻辑）→ database（`TextMemoryDataBase` / `DbMemoryDataBase`）→ protocol（JSON 序列化）→ 前端

### 框选语义差异

- 原文：动态图框选后展示 **时间范围**；静态图对应 **node index 范围**
- 原文：静态图与动态图折线图**数量不同**，但使用相同的**数据组织方式**（即上文 `legends` / `lines` 结构）

### 对比功能

- 原文仅保留截图参考，原文：*"具体比对算法、字段语义与异常处理，以 `QueryMemory*Handler` 的源码和测试为准"*

### Mock 工具

- 原文：`TinyMock` 仅作为内部接口查看工具的补充，不应作为文档唯一来源

> 注：原文未提供性能数据（如查询时延、内存占用、并发量等），本文档不臆造。

---

## 【表格解读】

**原文无表格**。原文中所有数据呈现均为按视图逐项的文本说明（如分组方式三项、数据来源按动态/静态/组件列举），未出现任何 markdown 或文本表格结构。

---

## 【公式解读】

**原文无公式**。文档未包含任何 LaTeX 公式或伪代码表达式，仅有的类 C++ 容器声明（`std::vector<std::string> legends`、`std::vector<std::vector<std::string>> lines`）属于数据结构描述而非数学公式。

---

## 【关联】

### 后端模块内聚关系（上下游分三层）

- **protocol 层** → **database 层** → **handler 层**
- protocol 负责协议转换（JSON ↔ 结构体）
- database 层封装 `TextMemoryDataBase` / `DbMemoryDataBase` 两种数据源
- handler 层承载全部业务查询与对比逻辑（5 个具名 handler + 通配的 `QueryMemory*Handler` 族）

### 与导入管线的关联

- `ImportActionHandler` 是 Memory 数据的**唯一入口**，下游分派给 `MemoryParse`（TEXT）或 `FullDbParser`（DB）

### 视图间数据复用

- `memory_record.csv` 是**三类视图折线图的公共数据源**
- DB 场景引入 `hostName` 维度（TEXT 场景无此选项），与 `rankId` 组合实现**单卡定位**

### 文档约定的真理源

- 原文：**关键数据来源与 handler 以正文和源码为准**；截图仅辅助说明
- 原文：对比算法、字段语义、异常处理 → 以 `QueryMemory*Handler` 源码 + 测试为准
- 原文：新增字段应同步更新 **parser / database / handler / 前端列配置与文案**

### 内部链接

- 文末标注：内部链接 **（无）**

---

## 【使用方法】

### 启用方式 / 前端交互项（原文给出的可操作项）

- **视图选择下拉框**
  - `rankId`（通用）
  - 分组方式：全局 / 流 / 组件
  - `hostName`（仅 DB 场景）

- **折线图查看**
  - 动态图、静态图、组件视图均使用同一数据结构（`legends` + `lines`）渲染

- **表格筛选**
  - 名称模糊查询
  - size 上下界筛选
  - 时间范围框选联动
  - 排序
  - 勾选 *"Only show allocated or released within the selected interval"* 仅显示区间内申请/释放相关算子
  - 注：**组件视图不支持查询**

- **对比功能**：UI 层提供入口（截图参考），具体算法以源码为准

### 验证清单（来自原文第 5 节）

- 导入 TEXT 和 DB 数据，检查视图选择、折线图、表格可用性
- 验证名称 / size / 框选 / 排序 / 对比功能是否符合预期
- 验证动态图、静态图、组件视图是否使用对应数据源（`memory_record.csv` / `operator_memory.csv` / `static_op_mem.csv` / `npu_module_mem.csv`）
- 对新增字段或筛选项，按 **parser → database → handler → 前端列配置与文案** 的顺序同步更新

### 配置项 / 命令

- 原文未涉及任何 CLI 命令、配置文件、环境变量、API 端点 URL 或配置参数。原文也未涉及 `QueryMemory*Handler` 的具体请求/响应字段——明确指示以 `server/src/modules/memory/protocol` 的源码和测试样例为准。

## 图文联合解读

- `memory_interface_optimization.png`: **图文联合解读**

图示将Memory界面纵向划分为**Header（视图选择）、Chart（折线图）、Table（明细表）**三大组件：Header承载Host Name/Rank ID/Group By筛选；Chart区组合Dynamic Chart、Statistic Chart等多视图；Table区封装Name/Size/Query/Reset等过滤条件与Detail Table。标题点明采用**组件拆分+策略/模板方法/组合模式+数据状态管理**的设计思路。论证了前端架构通过职责解耦、模式复用与状态统一，提升Memory视图的可扩展性与维护性，与文档§2"前端由视图选择、折线图、表格三部分组成"的论点一一对应，是其设计理念的可视化体现。
- `memory_main_structure.png`: **图文联合解读：**

图示呈现 Memory 模块的组件架构：根节点 Memory 下设 MemorySession（数据状态管理）、MemoryHeader（Host/RankId/GroupBy 选择器，采用策略+模板方法）、MemoryLineChart（含 DynamicLineChart 与 StaticLineChart，采用组合模式）及 MemoryDetailTable（含 Name/MinSize/MaxSize 筛选与 AntTableChart）。论证了 Memory 界面三段式（视图选择/折线图/表格）分层实现，并标注设计模式（策略模板、组合）。与文档论点对应：①验证"视图选择、折线图、表格"三大组成；②折线图区分为动态/静态两子组件，与"图表数量不同但数据组织方式相同"一致；③表格筛选项 Name/MinSize/MaxSize 对应文档"支持名称、size 条件筛选"；④Host 选项印证"DB 场景下还可选择 hostName"。
- `memory_header.png`: **图文联合解读**

1) **图中内容**：UML类图，父类`MemoryHeader(Template)`含`Host Name/Rank ID/Group By`字段；四个继承子类（FullDisplay/Normal/HostCompare/SingleDisplayStrategy）按场景暴露不同控件组合——FullDisplay和HostCompare含Host Name，SingleDisplay仅含Rank ID。

2) **技术结论**：采用**模板方法+策略模式**，Header按视图场景动态切换子类，DB场景才暴露Host Name，组件视图最简化。

3) **与文档关系**：直接支撑"视图选择"章节——`rankId`、分组方式、DB专属`hostName`的可选逻辑通过四种Strategy解耦实现，印证"组件视图不支持查询"的简化设计。
- `memory_line_graph.png`: **图文联合解读：**

1) **图示内容**：UML组件图，顶部为`<<MemoryLineChart>>`组件（含组件图标），下方通过空心菱形聚合关系连接`DynamicLineChart`和`StaticLineChart`两个子组件。

2) **技术结论**：`MemoryLineChart`作为父级聚合容器，统一封装动态图与静态图两类折线图实现，二者作为其聚合部件被组合使用。

3) **与文档论点对应**：呼应文档"动态图与静态图……使用相同的数据组织方式"——通过聚合同一父组件，证明二者共享统一架构与数据接口，仅渲染形态不同，符合Memory折线图模块化设计。
- `memory_bottom_table.png`: **图示解读：**

1. **结构内容**：UML组件图展示 `MemoryDetailTable`（接口/容器，标 `<<>>` 立体构造型）通过聚合关系（空心菱形）组合两个子组件——`MemoryDetailTableFilter`（筛选器）与 `AntTableChart`（表格渲染器），二者各有 2 个对外接口端口（lollipop），供上层调用。

2. **技术结论**：底部表格采用"组合 + 接口隔离"设计，筛选逻辑与渲染逻辑解耦，分别由独立组件实现，通过标准化接口与外部交互，便于复用与替换 AntTable 实现。

3. **与文档对应**：直接印证文档 §2"Memory界面底部表格具体实现"——表格承担明细数据展示与名称/size 等条件筛选能力，此图明确了其内部组件拆分与依赖关系，支撑"组件视图不支持查询"的论点。
- `memory_text_sequence_diagram.png`: **图示内容**：前后端时序图，前端发起请求→`MemoryParse::Instance()`递归查找record/operator/static op/component四类文件→`GetProfilerFileId()`→校验版本与上次解析状态→`CheckCsvFileList`校验四类CSV→Operator/Record/StaticOp/Component四个Parse按行转为结构体并入库→返回成功消息。

**技术结论**：TEXT解析是线性流水线，核心环节为文件发现→版本与完成性判重→CSV校验→四类并行解析落库，写入`TextMemoryDataBase`。

**与文档关系**：印证§3.1"TEXT 文件解析顺序"，说明`Memory::MemoryParse::Instance().Parse()`内部调用链，并呼应"TEXT解析后会写入数据库"的结论。
- `memory_request_sequence_diagram.png`: 1) **图示内容**：UML时序图，含5条泳道（WsSessionImpl→ModuleManager→MemoryModule→Handler→VirtualMemoryDataBase），展示请求从JSON解析→Module分发→MemoryModule按command名路由Handler→alt分支查询Text/DB两种DataBase→可选比对算法→响应回传并ToJson的完整链路。

2) **技术结论**：Memory查询遵循"入口解析→模块分发→命令路由→分库查询→按需比对→序列化返回"的分层架构，对TEXT/DB两种数据源做alt分支隔离，比对为可选后置步骤。

3) **与文档关系**：佐证3.1节"查询请求经handler和database层返回"的论断，明确`protocol`(JSON转换)、`handler`(command分发与比对)、`database`(Text/Db分库查询)三目录的职责边界。
- `memory.png`: **图示解读：**

1. **画面内容**：截图展示了 MindStudio Insight 的 Memory 主界面，用红框+红色中文标注（视图选择、折线图、表格）将页面纵向切分为三个区域：顶部为 Rank ID/Group By 选择器（当前 Rank 0、Overall）；中部为 Memory Analysis 折线图，含 4 条曲线（Operators Allocated/Activated/Reserved、App Reserved）及峰值数据（约 25143–26742MB）；底部为 Memory Allocation/Release Details 表格，提供 Name、Size 区间与时间区间筛选条件。

2. **技术结论**：界面采用"筛选器—趋势图—明细表"的经典三段式布局，折线图共享同一数据组织即可承载动态/静态多图渲染，表格与图通过同一组参数联动。

3. **与文档关系**：直观佐证第 2 章"Memory 界面由视图选择、折线图、表格三部分组成"及"组件视图不支持查询"的论点。
- `comparison_function.png`: # 图文联合解读

**1) 图内容**：流程图展示"发送比对请求"后，按 handler 类型分叉为**表格**与**折线图**两条并行路径。两条路径均经历两段蓝色高亮公共方法：`GetRespectiveData()`（获取 baseline/compare 数据库全量数据）和 `ExecuteComparisonAlgorithm()`（执行比对）。表格路径额外做 set/map 合并与筛选排序；折线图路径则做标签与数据点合并，最终汇合返回结果。

**2) 技术结论**：表格与折线图两类 handler 的比对流程**主干同构**，差异仅在于比对后的数据组织方式（明细 vs 趋势点），故应将"取数"与"比对算法"两段抽取为公共方法复用，避免重复实现。

**3) 与文档关系**：呼应文档 2.2 节"折线图与表格使用相同数据组织方式"及 3.2 节 handler 业务逻辑描述，论证了 Memory 模块比对能力的**复用性设计**结论。
