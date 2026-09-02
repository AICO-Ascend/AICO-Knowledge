# Operator部分设计文档

> 仓 `msinsight` · 路径 `docs/zh/development_guide/design/Operator.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msinsight/docs/zh/development_guide/design/Operator.md

# 「Operator 部分设计文档」一体化深度解读

## 【定位】
本篇文档面向开发者，说明 msinsight 中 **Operator（算子）详情页**的前后端请求链路、TEXT 与 DB 两种数据查询场景及表格/饼图展示逻辑，用于维护算子详情、筛选与比对能力。

## 【技术要点】

1. **前后端三段式 UI 结构**：Operator 页面由上方过滤条件、中间饼图、下方详情表格三部分组成，分别对应前端代码块 `Filter.tsx`（过滤）、`DetailChart.tsx`（饼图）、`DetailTable.tsx`（详情表）以及基础表格组件 `BaseTable`。
2. **请求-处理-响应六步闭环**，原文逐字为：
   - ① 前端发送 `operator/details` 请求；
   - ② `ProtocolDefs.h` 中定义 `REQ_RES_OPERATOR_DETAIL_INFO = "operator/details"`；
   - ③ `OperatorModule.cpp` 根据请求字符串注册并分发到对应 handler；
   - ④ `QueryOpDetailInfoHandler` 负责查询数据库并组装结果；
   - ⑤ `OperatorProtocol.cpp` 负责请求/响应结构与 JSON 的转换；
   - ⑥ 返回前端后，详情表和饼图根据响应数据刷新。
3. **TEXT 与 DB 双数据场景**：
   - `type=TEXT` 时，数据存储在 `kernelTable` 中，查询通常可直接通过 SQL 完成；`pmuColumnNames` 作为表头，主要承载寄存器相关信息。
   - `type=DB` 时，需要进行多表联查。
4. **数据库入口统一收口**，原文逐字为：`auto database = Timeline::DataBaseManager::Instance().GetSummaryDatabase(rankId);`，依赖周边 `KernelParser`、`dbManager` 与全量 DB 结构支撑。
5. **辅助关注文件**：`modules/operator/src/connection/handler.ts`、`modules/operator/src/components/RequestUtils.ts`、`modules/operator/src/components/TableColumnConfig.tsx`。
6. **开发约束**：新增接口或筛选项需先后端补查询逻辑再补 protocol 字段，前端同步表格列配置与 i18n 文案；如涉及排序、分页或比对须同步补测试；验证环节需校验 TEXT/DB 两场景下前端后端字段名一致性。

## 【关键机制与数据】

- **数据流/请求链路（原文 §3）**：前端 `RequestUtils` 发起 `operator/details` → `ProtocolDefs.h` 中定义的请求字符串常量 `REQ_RES_OPERATOR_DETAIL_INFO` 标识该路由 → `OperatorModule.cpp` 按字符串匹配分发至 `QueryOpDetailInfoHandler` → handler 通过 `Timeline::DataBaseManager::Instance().GetSummaryDatabase(rankId)` 获取数据库对象并执行 SQL/多表联查 → 命中结果经 `OperatorProtocol.cpp` 序列化/反序列化为 JSON → 前端 `DetailChart.tsx` 与 `DetailTable.tsx` 消费响应刷新饼图与详情表。
- **双场景分流依据**：入口参数 `type` 字段取值为 `TEXT` 或 `DB`，决定走 `kernelTable` 单表 SQL 还是多表联查路径。原文未给出具体表名、字段数、查询性能或容量数据。
- **响应数据形态**：原文 §3.3 明确"返回数据会在后端转换为 JSON 再回传前端"，但未给出具体 JSON schema、字段定义或样本。
- **周边支撑范围**：原文 §3.1 仅可确认数据库管理入口一项支撑；`KernelParser`、`dbManager` 和"全量 DB 结构"的完整说明需以源码为准（原文标注"若后续确认，可补充到此处"）。

> 说明：原文未给出任何性能数据（QPS、延迟、吞吐）、容量上限、字段数量、采样率或硬编码数字；如需上述数据，应回到 `QueryOpDetailInfoHandler`、SQL 表结构源码或 `pmuColumnNames` 定义处查证。

## 【表格解读】
原文无表格（文档内仅含示意图 `figures/*.png` 与代码片段，未出现参数表/性能对比/配置项表）。

## 【公式解读】
原文无公式（未出现 LaTeX 或伪代码形式的算式）。

## 【关联】

- **与可视化主流程的关联**：Operator 页面属于 msinsight 的可视化调优前端能力一环，其依赖的 `BaseTable` 为通用基础表格组件，与文档所属「development_guide/design」目录下其他设计文档（同属 msinsight 调优可视化能力集）共享前端基础设施。
- **与数据库/解析层的关联**：依赖 `Timeline::DataBaseManager`（数据库管理入口）、`KernelParser`（kernel/算子解析器）、`dbManager`，构成"解析→入库→查询→展示"的链路上下游。原文明确这些周边组件的完整说明需以源码为准。
- **与协议层的关联**：通过 `ProtocolDefs.h` 中的常量 `REQ_RES_OPERATOR_DETAIL_INFO` 与 `OperatorProtocol.cpp` 协同，构成 msinsight 前后端 RPC/消息协议体系的一部分。
- **与 i18n/前端配置的关联**：新增列或筛选项时需同步 `TableColumnConfig.tsx` 列配置与 i18n 文案，意味着 Operator 页面与 msinsight 国际化能力紧耦合。
- 文档末尾标注「内部链接: (无)」，因此无内部锚点链接可解析。

## 【使用方法】

原文未提供用户侧的启用方式、配置项或命令行（如 URL 入口、开关参数、查询参数名/示例值等）；文档定位为开发者设计说明，仅给出新增接口/筛选项的工程建议（先确认数据来源是 TEXT 还是 DB；后端先补查询逻辑再补 protocol；前端同步表格列配置与 i18n；涉及排序/分页/比对须同步补测试）以及验证方法（导入算子调优数据 → 检查过滤/饼图/详情表 → 验证 TEXT 与 DB 一致性 → 校验前后端字段名一致）。

> 注：若需具体启用步骤（如访问路径 `/operator`、查询参数 `type=TEXT|DB`、`rankId` 传值方式等），原文未涉及，应结合 `modules/operator/src/connection/handler.ts`、`RequestUtils.ts` 与 `OperatorModule.cpp` 源码确认。

## 图文联合解读

- `operator.png`: # 图文联合解读

## 1) 图中内容
展示Operator页面前端界面，自上而下分为三部分：
- **顶部过滤区**：分组方式（下拉"计算算子类型"）、卡序号（0）、师（15）
- **中间饼图区**：左图为"按算子类型分组总耗时(μs)"，含Conv2D(29.88%)、BNTrainingUpdate(10.86%)等十余种算子占比；右图为"按加速器核分组总耗时(μs)"，AI_CORE占100%
- **底部详情表格**：列含类型/加速器核/数量/总耗时/平均耗时/最大耗时/最小耗时/详情，共15条分页数据

## 2) 技术结论
证明Operator页面采用"过滤-聚合-明细"三层布局：过滤条件驱动后端聚合查询，结果同时以饼图（占比可视化）和表格（指标明细）双视图呈现，支持分页与详情下钻。

## 3) 与文档论点关系
直接对应文档§2所述"上方过滤条件、中间饼图、下方详情表格"三大组件结构（Filter.tsx/DetailChart.tsx/DetailTable.tsx），印证前端三段式布局与双饼图对比展示的设计。
- `operator_main_structure.png`: **图解说明：**

**1) 图的内容：** 该图为「主体逻辑结构图」，呈树状层级结构。自顶向下为：App → Operator → 三个并列子模块（Filter、DetailChart、DetailTable），其中 DetailTable 进一步派生出 OperatorTable、OperatorTypeTable 和 BaseTable（BaseTable 用灰色填充，区别于其他绿色框，暗示其为复用基础组件）。

**2) 技术结论：** 该图印证了 Operator 前端采用"容器—子组件—基础组件"三层分层架构。Filter、DetailChart、DetailTable 三者解耦并行，由 Operator 统一调度；表格展示层通过继承/组合 BaseTable 复用渲染能力，避免重复开发。

**3) 与文档的关系：** 与文档第 2 节"前端代码逻辑"中列出的四个关键代码块（`Filter.tsx`、`DetailChart.tsx`、`DetailTable.tsx`、`BaseTable`）一一对应，直观展示了组件依赖与调用关系。
- `operator_QueryOpDetailInfoHandler.png`: **图文联合解读：**

1）图示为`QueryOpDetailInfoHandler::HandleRequest`函数代码，含请求转换、参数校验（红框`CommonCheck`）及分支处理（对比/非对比场景，红色标注），最后封装响应并发送。

2）论证Handler通过`isCompare`标志位实现请求分流，对应文档第3节步骤4中"组装结果"的入口设计。

3）该图是文档"QueryOpDetailInfoHandler处理逻辑"配图的代码层佐证，将抽象处理链路落实到具体实现：参数校验→场景分支→响应返回，与文档描述的处理流程一一对应。
- `operator_query_db.png`: 图示：`HandleDetailDataRequest` 函数代码片段。先通过 `VirtualSummaryDataBase::GetFileIdFromCombinationId` 由 rankId 取文件ID，再经 `DataBaseManager::GetSummaryDatabase` 拿到 database 实例，核心调用 `QueryOperatorDetailInfo(request.params, response)` 查算子详情（红框标注），失败则 `ServerLog::Error` 记录。

论证：印证文档第3节所述"`QueryOpDetailInfoHandler` 负责查询数据库并组装结果"，明确了查询调用的具体代码位置。

关系：与第3.1节"前置信息"中 `database = Timeline::DataBaseManager::Instance().GetSummaryDatabase(rankId)` 一一对应，是其后续调用落点。
- `operator_db_management.png`: **图文联合解读：**

图示为`DataBaseManager::GetSummaryDatabase`函数源码，核心标注两处：①参数`inputId`（红框）作为查询键；②红字注释"所有数据库对象都存储在Map里，如果之前有就直接返回，没有就新建"。数据流依次为：recursive_mutex加锁 → `BaselineManager`判断isBaseline → 选取`summaryBaselineDatabaseMap`或`summaryDatabaseMap` → lambda按`DataType`（TEXT创建`TextSummaryDataBase`，DB创建`DbSummaryDataBase`）懒加载 → 遍历`host2DbPath`匹配host后返回。

**技术结论：** 数据库对象采用map缓存+懒加载策略，并按baseline/普通、TEXT/DB双维度分类管理。

**与文档关系：** 直接印证3.1节"database管理"前置入口实现，支撑3.2节TEXT与DB双场景的数据库获取链路。
- `operator_text.png`: **图示解读：**

1）**图内容**：代码展示 `TextSummaryDataBase::GetQueryDetailBaseSql` 函数，针对 TEXT 场景构造 SQL。三段 SQL（`conditionalQuerySql`/`allQuerySql`/`baseAllQuerySql`）在 WHERE 条件和 ORDER BY 上存在差异，红色批注指出"非对比与对比场景的区分，可优化"。

2）**技术结论**：不同场景通过拼接差异化 SQL 片段实现（`isHccl`、`isLimit`、`rankId` 三维条件组合），代码逻辑冗余可合并。`TABLE_KERNEL` 表名支持后续灵活替换为 DB 表，体现 TEXT/DB 共用同一查询接口的设计。

3）**文档关系**：对应文档 §3.2 "TEXT 场景——数据存储在 kernelTable 中"的实现细节，是 `operator_query_db.png` 的源码级补充，揭示了 TEXT 场景 SQL 构造的可优化点。
- `operator_db.png`: **图示内容**：函数 `DbSummaryDataBase::GenerateQueryDetailsSqlForOperator()` 通过 PMU 列名动态拼接 SQL：内层子查询从 `TABLE_COMPUTE_TASK_INFO` 出发，与 `TASK` 及多张 `STRING_IDS`（NAME、OPTYPE、TASKTYPE、INPUTSHAPES 等）做 JOIN，过滤 `accelerator_core <> 'HCCL'` 并按 duration 降序 LIMIT，外层再拼接 `JoinExtraColName`、`CreatePMUTmpTableSql` 输出完整查询语句。

**技术结论**：DB 场景下，Operator 详情查询通过多表 JOIN 完成算子元数据补全，并排除通信类算子，按耗时排序取 Top-N。

**与文档关系**：对应第 3 节"查询数据库拿到参数"配图，印证 DB 类型查询链路以 SQL 组装为核心实现。
- `operator_return_data.png`: **1) 图示内容**：展示 `ToResponseJson<OperatorDetailInfoResponse>` 模板函数实现，使用 RapidJSON 将响应对象序列化为 JSON。流程为：先调用 `ProtocolUtil::SetResponseJsonBaseInfo` 写入基础信息，向 body 添加 `total`、`level` 标量字段；再遍历 `res.pmuHeaders` 向量构建 `pmuHeaders` JSON 数组；最后循环 `res.datas`，为每个元素生成含 `diff`、`baseline`、`compare` 三个字段的对象并推入 `data` 数组。红色注释标注此处编码 JSON 返回前端。

**2) 技术结论**：Operator 详情响应的 JSON 协议结构固定，包含 `pmuHeaders`（列名）和 `data`（含 diff/baseline/compare 的比对行），是 TEXT/DB 双场景共用的下行结构。

**3) 与文档关系**：对应文档第 3 节第 5 步——`OperatorProtocol.cpp` 负责请求/响应结构与 JSON 转换，是后端→前端链路的关键收口。
