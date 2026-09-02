# Communication部分设计文档

> 仓 `msinsight` · 路径 `docs/zh/development_guide/design/Communication.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msinsight/docs/zh/development_guide/design/Communication.md

# 文档深度解读：Communication 部分设计文档

## 【定位】

本文档描述 `cluster/communication` 页面的**数据来源（TEXT / DB 双场景）、接口命令（URL 路由）以及前后端代码入口**，面向需要维护通信矩阵、通信耗时、算子列表、带宽和分布图的开发者，是 Communication 模块的接口-数据-代码映射参考手册。

---

## 【技术要点】

1. **双数据场景支持**：页面同时支持 **TEXT**（原始文本文件，由 ATT 处理后输出）与 **DB**（处理后的结构化数据）两种数据来源，但页面能力和接口命名保持一致。
2. **10 个核心 URL 接口**：包括 `communication/matrix/bandwidthInfo`、`communication/duration/iterations`、`communication/matrix/group`、`communication/matrix/sortOpNames`、`communication/duration/operatorNames`、`communication/operatorLists`、`communication/duration/list`、`communication/operatorDetails`、`communication/distribution`、`communication/bandwidth`，分别对应矩阵带宽、矩阵分组、算子排序、算子名列表、算子列表、耗时明细、算子详情、分布图、带宽分析等视图。
3. **前后端分层代码入口**：前端请求封装在 `modules/cluster/src/utils/RequestUtils.ts`；后端命令常量定义于 `server/src/modules/defs/ProtocolDefs.h`，插件实现位于 `server/src/modules/communication/CommunicationPlugin.h`，插件注册在 `server/src/modules/Plugins.cpp`。
4. **测试支撑链**：协议测试入口为 `server/src/test/modules/communication/protocol/CommunicationProtocolUtilTest.cpp`，请求样例文件为 `server/src/test/test_data/request.csv`。
5. **未完全实现项**：原文指出 `sortOpNames` 的 **DB 场景支持情况需以源码实现为准**；每个接口的完整响应字段同样以源码和测试结果为准；通信耗时明细列表中的**专家建议由数据计算得到**（具体算法未在文档中说明）。

---

## 【关键机制与数据】

**工作原理/数据流：**

1. **原始数据阶段**（ATT 处理后文件）：
   - text 场景：参见原文图片 `figures/communication_text_data.png`（原文：原文以图片形式呈现，未提供具体字段）。
   - db 场景：参见原文图片 `figures/communication_db_data.png`。

2. **处理后 DB 数据阶段**：
   - text 场景处理后：参见原文图片 `figures/communication_processed_text_data.png`。
   - db 场景处理后：参见原文图片 `figures/communication_processed_db_data.png`。

3. **页面-接口-数据三级映射**：每个页面 UI 元素（图片）对应一个 URL 请求，对应一种 db 数据类型与一种 text 数据类型，最终形成"页面 → 接口 → 数据"的查找表。

4. **矩阵分组底层数据**：原文明确指出 `communication/matrix/group` 在 text 场景下底层数据来源于图片 `figures/communication_matrix_group_4.png`。

5. **算子名排序底层数据**：`communication/matrix/sortOpNames` 的 text 场景底层数据来源于 `figures/communication_sortOpNames_3.png`，DB 场景是否支持需以源码为准。

6. **算子名列表多数据源**：`communication/duration/operatorNames` 的 text 场景数据来源于三张图片（`figures/communication_operatorNames_4.png`、`_5.png`、`_6.png`）。

7. **耗时明细多数据源**：`communication/duration/list` 的 text 场景数据来源于两张图片（`figures/communication_duration_list_3.png`、`_4.png`）。

**性能数据**：原文未提供任何具体的性能指标、响应时间、带宽数值。

---

## 【表格解读】

### 表格：页面接口总览（逐字还原）

| 页面数据 | URL 请求 | db 数据类型 | text 数据类型 | 说明 |
| --- | --- | --- | --- | --- |
| ![communication_page_data_1](figures/communication_page_data_1.png) | `communication/matrix/bandwidthInfo` | ![communication_db_data_1](figures/communication_db_data_1.png) | ![communication_text_data_1_1](figures/communication_text_data_1_1.png) ![communication_text_data_1_2](figures/communication_text_data_1_2.png) | 矩阵带宽详情。 |
| ![communication_duration_iterations_1](figures/communication_duration_iterations_1.png) | `communication/duration/iterations` | ![communication_duration_iterations_2](figures/communication_duration_iterations_2.png) | ![communication_duration_iterations_3](figures/communication_duration_iterations_3.png) | 迭代列表与通信耗时范围。 |
| ![communication_matrix_group_1](figures/communication_matrix_group_1.png) | `communication/matrix/group` | ![communication_matrix_group_2](figures/communication_matrix_group_2.png) | ![communication_matrix_group_3](figures/communication_matrix_group_3.png) 底层数据来源于：![communication_matrix_group_4](figures/communication_matrix_group_4.png) | 通信矩阵分组信息。 |
| ![communication_sortOpNames_1](figures/communication_sortOpNames_1.png) | `communication/matrix/sortOpNames` |  | ![communication_sortOpNames_2](figures/communication_sortOpNames_2.png) 底层数据：![communication_sortOpNames_3](figures/communication_sortOpNames_3.png) | 算子名排序与聚合结果；DB 场景是否支持需以源码实现为准。 |
| ![communication_operatorNames_1](figures/communication_operatorNames_1.png) | `communication/duration/operatorNames` | ![communication_operatorNames_2](figures/communication_operatorNames_2.png) | ![communication_operatorNames_3](figures/communication_operatorNames_3.png) 数据：![communication_operatorNames_4](figures/communication_operatorNames_4.png) ![communication_operatorNames_5](figures/communication_operatorNames_5.png) ![communication_operatorNames_6](figures/communication_operatorNames_6.png) | 通信耗时视图中的算子名列表。 |
| ![communication_operatorLists_1](figures/communication_operatorLists_1.png) | `communication/operatorLists` | ![communication_operatorLists_2](figures/communication_operatorLists_2.png) | ![communication_operatorLists_3](figures/communication_operatorLists_3.png) 数据：![communication_operatorLists_4](figures/communication_operatorLists_4.png) | 算子列表视图。 |
| ![communication_duration_list_1](figures/communication_duration_list_1.png) | `communication/duration/list` | ![communication_duration_list_2](figures/communication_duration_list_2.png) | ![communication_duration_list_3](figures/communication_duration_list_3.png) ![communication_duration_list_4](figures/communication_duration_list_4.png) | 通信耗时明细列表，专家建议由数据计算得到。 |
| ![communication_operatorDetails_1](figures/communication_operatorDetails_1.png) | `communication/operatorDetails` | ![communication_operatorDetails_2](figures/communication_operatorDetails_2.png) | ![communication_operatorDetails_3](figures/communication_operatorDetails_3.png) | 算子详情。 |
| ![communication_distribution_1](figures/communication_distribution_1.png) | `communication/distribution` | ![communication_distribution_2](figures/communication_distribution_2.png) | ![communication_distribution_3](figures/communication_distribution_3.png) | 通信分布图。 |
| ![communication_bandwidth_1](figures/communication_bandwidth_1.png) | `communication/bandwidth` | ![communication_bandwidth_2](figures/communication_bandwidth_2.png) | ![communication_bandwidth_3](figures/communication_bandwidth_3.png) | 带宽分析。 |

### 表格逐行说明

1. **`bandwidthInfo`**：路径 `communication/matrix/bandwidthInfo`，负责**矩阵带宽详情**，text 场景关联两张子图（`_1_1`、`_1_2`）。
2. **`iterations`**：路径 `communication/duration/iterations`，输出**迭代列表与通信耗时范围**。
3. **`group`**：路径 `communication/matrix/group`，输出**通信矩阵分组信息**，text 场景额外标注"底层数据来源于"第 4 张子图。
4. **`sortOpNames`**：路径 `communication/matrix/sortOpNames`，用于**算子名排序与聚合结果**；**DB 数据类型列为空**，原文明确"DB 场景是否支持需以源码实现为准"。
5. **`operatorNames`**：路径 `communication/duration/operatorNames`，提供**通信耗时视图中的算子名列表**，text 场景标注 3 张子图为数据来源。
6. **`operatorLists`**：路径 `communication/operatorLists`，输出**算子列表视图**。
7. **`duration/list`**：路径 `communication/duration/list`，输出**通信耗时明细列表**，原文注明"专家建议由数据计算得到"（具体算法未给出）。
8. **`operatorDetails`**：路径 `communication/operatorDetails`，输出**算子详情**。
9. **`distribution`**：路径 `communication/distribution`，输出**通信分布图**。
10. **`bandwidth`**：路径 `communication/bandwidth`，输出**带宽分析**。

---

## 【公式解读】

原文无公式。

---

## 【关联】

原文未提供文末的内部链接信息（标记为"无"）。但根据文档内容可推断以下关联关系：

- **数据来源关联**：文档引用了 `figures/communication_text_data.png`、`figures/communication_db_data.png` 等多张原始数据图，依赖 **ATT 工具**对原始采集数据的预处理产物（"ATT 处理后文件"）。
- **协议层关联**：后端插件 `CommunicationPlugin.h` 与 `ProtocolDefs.h`（命令常量）共同构成协议实现层，调用契约由 `CommunicationProtocolUtilTest.cpp` 进行验证。
- **插件注册关联**：`CommunicationPlugin.h` 通过 `server/src/modules/Plugins.cpp` 进行注册，纳入插件体系。
- **前端封装关联**：`RequestUtils.ts` 是前端调用所有 10 个 URL 接口的统一入口。
- **测试样例关联**：`request.csv` 作为请求样例，与协议测试共同支撑接口正确性验证。
- **与 msinsight 主仓关系**：本文属于 `msinsight` 的 `cluster/communication` 子模块，文档路径为 `docs/zh/development_guide/design/Communication.md`。

---

## 【使用方法】

- **页面访问入口**：路径 `cluster/communication`。
- **接口 URL 调用清单**（10 个接口）：
  - `communication/matrix/bandwidthInfo`
  - `communication/duration/iterations`
  - `communication/matrix/group`
  - `communication/matrix/sortOpNames`
  - `communication/duration/operatorNames`
  - `communication/operatorLists`
  - `communication/duration/list`
  - `communication/operatorDetails`
  - `communication/distribution`
  - `communication/bandwidth`
- **数据场景选择**：支持 `text` 与 `db` 两种数据来源，切换不影响接口命名。
- **代码定位**：
  - 前端请求封装 → `modules/cluster/src/utils/RequestUtils.ts`
  - 后端命令常量 → `server/src/modules/defs/ProtocolDefs.h`
  - 后端插件实现 → `server/src/modules/communication/CommunicationPlugin.h`
  - 插件注册 → `server/src/modules/Plugins.cpp`
  - 协议测试 → `server/src/test/modules/communication/protocol/CommunicationProtocolUtilTest.cpp`
  - 请求样例 → `server/src/test/test_data/request.csv`
- **未明确事项**（需查阅源码确认）：
  - `sortOpNames` 的 DB 场景支持情况；
  - 专家建议的具体计算算法；
  - 每个接口的完整响应字段。
- **配置项 / 启用命令**：原文未涉及具体的启用配置项、启动命令或环境变量。

## 图文联合解读

- `communication_text_data.png`: # 图文联合解读

**1) 图的内容**
该图为 Windows 文件资源管理器截图，展示了 4 个数据文件：
- `cluster_communication.json` (8,025 KB，2024/2/22)
- `cluster_communication_matrix.json` (7,127 KB，2023/9/14)
- `cluster_step_trace_time.csv` (3 KB，2023/9/14)
- `communication_group.json` (1 KB，2023/9/14)

均为 ATT 处理后的原始/中间产物，3 个 JSON + 1 个 CSV 结构。

**2) 技术结论**
这些文件构成 `cluster/communication` 页面"原始数据层"的物理载体：JSON 文件承担结构化通信记录（矩阵、群组信息），CSV 承载时序步长追踪数据，覆盖了矩阵带宽、迭代耗时、群组聚合三类接口所需的输入。

**3) 与文档论点关系**
该图对应文档 §2.1「原始数据（ATT 处理后文件）」章节，是对 TEXT/DB 双场景数据来源的可视化佐证，印证了页面接口背后的多源异构数据依赖。
- `communication_db_data.png`: **图文联合解读：**

1) **图中内容**：展示了一个 SQLite 数据库文件 `cluster_analysis.db` 的属性信息——修改日期 `2024/10/30 12:32`、类型 `Data Base File`、大小 `1,892 KB`。

2) **技术结论**：ATT 处理后的集群通信数据已被持久化到本地 SQLite 数据库中，文件体积约 1.8 MB，结构化为可被前端直接查询的关系型存储。

3) **与文档论点的关系**：该图对应文档 2.2 节"处理后 DB 数据内容"中的 **db 场景**示意图，印证了 `cluster/communication` 页面采用 DB 而非 TEXT 作为数据底座的设计结论，并佐证 2.3 节接口通过 SQLite 文件向后端暴露的工程实现方式。
- `communication_processed_text_data.png`: **1) 图示内容**：DB管理工具的表列表界面，含工具栏（打开表、设计表、新建表等）和6张表（step_statistic_info、group_id、communication_time_info、communication_matrix、communication_bandwidth_info、cluster_base_info），标注「有索引」「有触发器」「根据页面」三列信息。

**2) 技术结论**：communication 业务相关 3 张表（time_info、matrix、bandwidth_info）均建索引优化查询，其余 3 张无索引；全表无触发器；「根据页面」列表明这些表服务于不同前端页面（页号 2、4、5、6、7、8）。

**3) 与文档关系**：印证文档 2.2 节「处理后 DB 数据内容」的 db 场景表结构，揭示通信模块数据按"矩阵/耗时/带宽"三类分表存储并加索引的设计依据。
- `communication_processed_db_data.png`: **图示内容**：DB集合（表）清单，含 ClusterBaseInfo(3373)、ClusterCommunicationBandwidth(35)、Matrix(6)、Time(34)、StepTraceTime(3)、CommunicationGroupMapping(2)、HostInfo(4)、RankDeviceMap(5)、status_info(3375) 共9张表，列出索引、触发器与文档数。

**技术结论**：ATT 输出经处理后按维度拆分入库——带宽、矩阵、耗时、群组映射分表承载，BaseInfo/status_info 记录量级最大，反映从原始 rank 级数据到通信多维指标的归集路径。

**文档关系**：对应"2.2 处理后 DB 数据内容（db 场景）"，佐证通信模块采用"分维度分表"存储设计，为 `communication/matrix/*` 等页面接口提供数据底座。
- `communication_page_data_1.png`: **1) 图中内容**：Communication页面Matrix Model视图。顶部导航栏切换至Communication；控件含Step(1)、Communication Group(0-7)、Operator Name(allgather-bottom1)、矩阵类型(Bandwidth GB/s)、可见范围(4.5132–17.6246)。主体为8×8(Dst×Src Rank)带宽热力矩阵，红色低带宽、蓝色高带宽，悬浮tooltip展示算子名hcom_allGather__565_27_1及srcRank→dstRank(3→2)对应6.214 GB/s。

**2) 技术结论**：矩阵以Rank对为粒度呈现算子级通信带宽，支持范围筛选与hover下钻至单次通信事件，前端通过颜色映射直观区分带宽差异。

**3) 与文档关系**：对应文档2.3节`communication/matrix/bandwidthInfo`接口的可视化展示，印证"矩阵带宽详情"的数据映射关系。
- `communication_db_data_1.png`: **1) 图中内容**：数据库客户端（类似 Navicat）界面，左侧树形结构展开 `main` 库，选中表 `ClusterCommunicationMatrix`；右侧表格展示字段 step、hccl_op_name、group_name、src_rank、dst_rank、transit_size、transit_time、bandwidth、trans_type、op_name，样本数据为 alltoall-top1、allreduce-bottom3 等算子在 6032/6044 等 rank 间的 RDMA/HCCS/LOCAL 通信记录。

**2) 技术结论**：经 ATT 处理后，通信矩阵被结构化存入 `ClusterCommunicationMatrix` 表，每行即一条 rank-to-rank 通信事件，携带传输类型、耗时、大小与带宽，是页面矩阵与带宽图的直接数据源。

**3) 与文档关系**：对应 2.2 节"处理后 DB 数据内容"中 db 场景下 `ClusterCommunicationMatrix` 的字段定义，支撑 `communication/matrix/bandwidthInfo` 等接口取数。
- `communication_text_data_1_1.png`: **图解读：**

1) **画面内容**：数据库客户端左侧树形结构显示 `cluster_9` 库下的 `communication_matrix` 表（红框标出），右侧为该表数据，列包含 id、group_id、iteration_id、op_name、op_sort、group_name、src_rank、dst_rank、transport_type、transit_size、transit_time、bandwidth。四列（transport_type/transit_size/transit_time/bandwidth）以红框圈出。`op_sort` 列亦被红框标注，包含 allreduce-top1、middle、bottom1、bottom2、total 等分类。

2) **技术结论**：通信矩阵以"算子类型+传输类型（HCCS/LOCAL）+ src/dst rank"为最小记录单元，每条记录独立存储传输大小、耗时与带宽，支撑按 group 与 op_sort 的聚合分析。

3) **与文档关系**：对应文档 2.3 节 `communication/matrix/bandwidthInfo` 接口的数据源，验证 DB 场景下带宽矩阵的存储结构与红框列即为页面带宽详情字段映射。
- `communication_text_data_1_2.png`: **图文解读：**

1) **图中内容**：展示一个文件条目——`cluster_communication_matrix.json`，类型为 JSON File，大小 507 KB，时间戳 2024/11/21 18:22，无内部结构展示。

2) **论证结论**：该图作为原始数据（ATT 处理后文件）的产物佐证，说明通信矩阵相关元数据以结构化 JSON 形式落地，单文件量级约百 KB 至 MB 级，属于轻量级持久化产物。

3) **与文档关系**：对应文档第 2.1 节"原始数据"中 text 场景 `communication_text_data` 引用图，作为 ATT 流程输出文件清单的可视化例证，支撑"前后端以 JSON 文件作为数据载体"的设计论点。
- `communication_duration_iterations_1.png`: # 图文联合解读

## 1) 图中内容
展示"通信矩阵"页面 UI：顶部为筛选区（迭代ID=1、通信域={0~7}、算子=Total Op Info、模式切换），中部为矩阵配置面板（类型=带宽 GB/s、范围 14.315~16.9618、显示卡内通信开关、确认按钮）。下方为 Dst Rank Id 热力矩阵，第 6/7 行展示各格带宽数值（15.3261、14.4173、16.9618 等），颜色由蓝→红渐变映射带宽强度。

## 2) 技术结论
该页面对应 `communication/matrix/bandwidthInfo` 接口，呈现源/目的 rank 间的带宽热力分布；支持范围筛选与卡内通信开关联动，颜色编码直观区分高低带宽单元（蓝低/红高）。

## 3) 与文档关系
印证文档 2.3 节"通信矩阵带宽详情"条目——前端通过矩阵类型下拉、范围输入和开关控件向后端请求相应 db/text 数据，渲染为热力矩阵视图。
- `communication_duration_iterations_2.png`: **图示内容：** 左侧为数据库表结构树，`main` 模式下罗列通信相关表（ClusterCommunicationBandwidth/Matrix/Time、CommunicationGroupMapping 等），高亮选中 `ClusterStepTraceTime`；右侧展示该表数据，含 step、type（rank/stage）、index、computing、communication 字段，记录每步按 rank 与 stage 维度的计算与通信耗时。

**技术结论：** 通信模块以多张专用表支撑，其中 `ClusterStepTraceTime` 是 ATT 落库后按 step 粒度拆分计算与通信耗时的核心源表，rank 与 stage 两类索引分别支撑矩阵带宽与迭代耗时的统计。

**与文档关系：** 对应 §2.1 db 场景的"原始数据（ATT 处理后文件）"，即页面接口（matrix/group、duration/iterations 等）所读取的底层 DB 数据来源。
- `communication_duration_iterations_3.png`: **图示解读：**

1) **画面内容**：数据库管理工具截图，左侧树形结构展开 `cluster_33 → main → task`，其中 `step_statistic_info` 表被红框标注；右侧表格展示该表字段：`id`、`rank_id`、`step_id`（红框高亮，全部为 16）、`stage_id`、`compute_time`、`pure_communication…`（截断）。

2) **技术结论**：所有 rank（1–24）共享同一个 `step_id=16`，表明该 step 在多卡并行中具有一致的阶段标识；`compute_time` 与 `pure_communication` 字段按 rank 分行存储，支撑通信矩阵与耗时聚合的原始数据粒度。

3) **与文档关系**：对应 2.2 节"处理后 DB 数据内容"db 场景，说明 `step_statistic_info` 是通信耗时与带宽矩阵计算的数据源，页面通过 `communication/duration/iterations` 等接口聚合此表实现"迭代列表与通信耗时范围"功能。
- `communication_matrix_group_1.png`: 图示内容：Communication页面顶部筛选栏，包含"迭代ID=1"、"通信域=(0,1,2,3,4,5,6,7)"（红框标注）、"算子名称=Total Op Info"等下拉选项，以及"通信矩阵/通信耗时分析"切换；下方矩阵区含"通信矩阵类型=带宽(GB/s)"、卡内通信开关、筛选范围14.315~16.9618，显示Dst Rank Id热力图。

技术结论：该界面通过多维筛选（迭代/域/算子）+数值范围过滤，实现对通信带宽矩阵的可视化查询，支持卡内通信显隐切换。

与文档关系：对应"2.3 页面接口总览"中 `communication/matrix/bandwidthInfo` 的前端入口，论证通信矩阵带宽详情页的数据过滤与展示机制。
- `communication_matrix_group_2.png`: # 图文联合解读

## 1) 图中内容
数据库管理工具截图：左侧对象树定位到 `cluster_analysis_23.main` 下的 **`CommunicationGroupMapping`** 表（高亮选中）；右侧查询结果展示该表数据，含 `type`（collective/p2p）、`group_name`（通信组ID）、`rank_set`（如 {6032}、{6032,6044}、{6044}）三列，红框圈出关键列。

## 2) 技术结论
每条记录映射一个通信算子实例：type 区分集合通信与点对点通信，rank_set 明确参与该通信的 rank 编号集合，体现通信域（group_name）与物理 rank 的绑定关系。

## 3) 与文档论点关系
对应文档 2.3 节 `communication/matrix/group` 接口的 DB 数据来源，作为通信矩阵分组查询的原始数据基础，与 text 场景数据并列支撑页面通信分组渲染。
- `communication_matrix_group_3.png`: **图文解读：**

1) **图中内容**：左侧为数据库schema树，红色框标注`group_id`表；右侧展示该表数据，`id`列从1自增，`group_id`列存为元组格式`(32,)`、`(33,)`等，每行对应一个独立分组ID。

2) **技术结论**：`group_id`表作为通信矩阵分组的索引映射表，主键`id`与业务分组号一一对应，结构简洁，采用自增主键+单字段元组存储，便于按序号快速检索分组。

3) **与文档关系**：对应文档`communication/matrix/group`接口的db数据类型，印证了"处理后DB数据"中矩阵分组的存储设计——通过独立`group_id`表解耦分组维度，支持页面按分组聚合展示通信矩阵数据。
- `communication_matrix_group_4.png`: ## 图文联合解读

**1) 图中内容：** 该图为 `cluster_communication_matrix.json` 原始数据片段，展示了 step1 步骤下 allreduce 通信的拓扑信息。结构为 JSON 数组，包含字段：`Transport Type`（LOCAL/HCCS）、`Transit Time(ms)`、`Bandwidth(GB/s)`、`Transit Size`、`Op Name`（如 `hcom_broadcast`）。关键标注包括传输类型分类（HCCS 为高速互联协议）、耗时（0.00484 ms）和带宽（3.84 GB/s）等数值。

**2) 技术结论：** 论证了通信矩阵数据经 ATT 处理后按"传输类型 + 操作名"组织，每条记录明确分离耗时、带宽、传输量三类指标，可直接支撑后续聚合统计与可视化。

**3) 与文档关系：** 对应文档 2.1 节"原始数据（ATT 处理后文件）"中 text 场景的 `communication_text_data` 配图，是说明 `cluster/communication` 页面通信矩阵数据源头与字段映射的依据。
- `communication_sortOpNames_1.png`: **1) 图示内容**：Communication页面顶部控制区，红色框标注「算子名称」下拉框（选项Total Op Info），含迭代ID、通信域、矩阵类型（带宽GB/s）、筛选范围14.315–16.9618等筛选控件，右上为"通信矩阵/通信耗时分析"单选切换。

**2) 技术结论**：算子名称作为矩阵下拉的关键筛选维度，与迭代ID、通信域构成三段式查询入参，决定后端`communication/matrix/bandwidthInfo`接口返回的矩阵数据范围。

**3) 与文档关系**：对应文档2.3节页面接口总览表第一行，验证「矩阵带宽详情」页面的前端参数组装逻辑与DB/text双数据场景共用入口设计。
- `communication_sortOpNames_2.png`: **1) 图示内容**：左侧为数据库对象树，展开通信相关表（`communication_bandwidth_info`、`communication_matrix` 高亮选中、`communication_time_info` 等）；右侧为 `communication_matrix` 表数据，字段含 `id`、`group_id`、`iteration_id`、`op_name`、`op_soft`，红色框标注 `op_name` 列，呈现 `hcom_allGather_`、`hcom_reduceScatter_`、`hcom_allReduce_` 等通信算子。

**2) 技术结论**：DB 场景下，通信矩阵原始数据以「group_id + iteration_id + op_name」三元组组织，按 group 分组、同一 iteration 内顺序记录算子类型，构成 `communication/matrix/group` 接口的底层结构。

**3) 与文档关系**：对应文档第 2.2 节"处理后 DB 数据内容"中 `communication_matrix` 表的字段与样例，作为前端矩阵带宽页面的数据来源说明。
- `communication_sortOpNames_3.png`: **图示解读：**

1) **画面内容**：展示 ATT 处理后的原始通信数据，含 `Transport Type`(LOCAL/HCCS)、`Transit Time(ms)`、`Transit Size(MB)`、`Op Name`(hcom_allreduce、hcom_broadcast)、`Bandwidth(GB/s)` 等字段，以 JSON 数组形式按步(step)组织矩阵。

2) **技术结论**：通信矩阵的最小数据单元即"算子×链路×步"三元组，含传输类型、耗时、带宽、Op 名称，可直接映射到矩阵带宽详情接口 `communication/matrix/bandwidthInfo`。

3) **与文档关系**：作为 §2.1 text 场景的原始数据样本，佐证前端无需二次解析即可消费该结构，证明通信模块数据源的扁平化与字段标准化设计。
- `communication_operatorNames_1.png`: ## 图文联合解读

**1) 图中内容**：截图展示 `cluster/communication` 页面的筛选控件区。顶部导航栏中「通信」Tab 高亮激活。下方含三个下拉框：迭代ID（值为1）、通信域（值为 `(0,1,2,3,4,5,6,7)`）、算子名称（红框标注，当前为 `Total Op Info`）。右侧单选按钮切换「通信矩阵 / 通信耗时分析」（后者选中）。下方为 HCCL 通信域下 Rank 0/1 的通信耗时甘特条带，按算子着色（粉、紫、蓝等）。

**2) 技术结论**：页面通过「迭代ID × 通信域 × 算子名称」三段式过滤控制通信耗时分析视图；`Total Op Info` 模式下聚合展示各 Rank 全部算子的通信耗时分布，体现多算子、多 Rank 并行通信特性。

**3) 与文档论点关系**：对应文档 §2.3 表格中 `communication/duration/iterations` 接口（`communication_duration_iterations_1` 截图），印证"通信耗时分析"视图的数据维度（迭代列表+耗时范围）及前端过滤交互设计。
- `communication_operatorNames_2.png`: **图示解读**：

1) **画面内容**：左侧为数据库表结构树，展示了cluster_analysis_23下的通信相关表（ClusterCommunicationTime、ClusterCommunicationBandwidth、ClusterCommunicationMatrix等）；右侧为`ClusterCommunicationTime`表的数据预览，含`step`、`rank_id`、`hccl_op_name`、`group_name`四列，其中`hccl_op_name`列用红框标注，显示`hcom_send/receive_397_x_1`等HCCL算子命名。

2) **技术结论**：通信耗时数据按step粒度存储，rank_id=6032下每个通信算子（send/receive）独立成行，编号397对应特定group_name，证明通信算子与集合通信组一一映射，可按算子聚合统计耗时。

3) **与文档关系**：对应"2.2 处理后DB数据内容"的text场景截图，论证CommunicationTime表是页面通信耗时接口（`communication/duration/iterations`）的数据来源。
- `communication_operatorNames_3.png`: **1) 图内容**：Navicat数据库界面。左侧展示 `main` 库下的通信相关表（`communication_matrix`、`communication_bandwidth_info`、`communication_time_info` 等），右侧打开某张表，红框标注 `op_name`（如 `hcom_allGather_479_0…`）与 `op_suffix`（如 `13944853901003…`）两列；其余列为 `id`、`iteration_id`、`stage_id`、`rank_id`。

**2) 技术结论**：DB场景下通信算子数据以结构化表存储，每条记录对应一次集合通信操作，通过 `op_name` 标识算子类型、`op_suffix` 标识唯一实例，结合迭代/阶段/rank维度索引。

**3) 与文档关系**：对应文档 §2.2 "处理后DB数据内容 db场景" 的配图，证明 `communication/matrix/bandwidthInfo` 等接口的 db 数据来源为 `communication_matrix` 表，字段 `op_name`、`op_suffix` 是关键映射键。
- `communication_operatorNames_4.png`: **图文联合解读：**

1. **图示内容**：图中仅展示一个高亮选中的文件名标签 `cluster_communication.json`，右侧带数字"2"（疑似页码或索引），蓝色背景表示当前选中状态。

2. **技术结论**：该文件即为 Communication 页面 ATT 处理后的原始 JSON 数据载体，是 text/db 两类场景下通信数据的统一落盘形式。

3. **与文档关系**：对应文档 2.1 节"原始数据（ATT 处理后文件）"的引用图，证明前端/后端通信矩阵、耗时等数据均源自此 JSON 文件，经处理后入库供页面接口调用，印证了"原始数据→DB→页面"的数据流映射关系。
- `communication_operatorNames_5.png`: **图解：**

1) **图中所画**：展示了 ATT 处理后的原始通信数据（JSON 格式），按迭代/分组维度组织，每条记录包含三大传输通道（RDMA、SDMA、HCCS）的带宽统计与耗时统计。带宽字段含 Transit Size、Transit Time、Bandwidth(GB/s)、Large Packet Ratio、Size Distribution；耗时字段含 Elapse Time、Synchronization Time、Wait Time、Idle Time。

2) **论证结论**：通信指标按"带宽维度（带宽矩阵）"和"耗时维度（时间矩阵）"双视角拆分，RDMA/SDMA/HCCS 三种链路独立采集，Size Distribution 支持大包识别，耗时细分为同步/等待/空闲子项——为前端通信矩阵、通信耗时图提供完整结构化数据底座。

3) **与文档关系**：对应文档 §2.1"DB 场景原始数据"图，是 `communication/matrix/bandwidthInfo` 与 `communication/duration/iterations` 接口读取的源数据形态说明。
- `communication_operatorNames_6.png`: **图说：** JSON 数组承载通信算子（allreduce、reduceScatter）处理后数据，每条目按通信域 RDMA/HCCS 分组，内含 Transit Time(ms)、Bandwidth(GB/s)、Size Distribution、Large Packet Ratio、Start Timestamp(us)、Elapse Time、Wait/Synchronization/Idle Time Ratio 等字段，支撑矩阵带宽、耗时分布与算子列表三类页面。

**结论：** ATT 原始数据经聚合后，按「算子×通信域」维度结构化输出，统一了 text/db 两场景字段命名，供前端矩阵图、耗时图、散点图直接消费。

**与文档关系：** 印证 §2.2「处理后 DB 数据内容」——即前端接口所消费的标准化中台数据。
- `communication_operatorLists_1.png`: **图示解读：**

1) **画面内容**：横轴为时间(ms)，范围约655–6833ms，以1000ms为刻度；纵轴为Rank ID(0–7)。每行用不同颜色（粉、紫、蓝、橙）矩形条呈现各rank上的通信操作片段，按时间分簇分布；底部含时间轴缩略条，右侧带滚动条与颜色图例（Time/ms）。

2) **技术结论**：展示一个iteration内8个rank的**通信耗时甘特图**，不同颜色对应不同集合通信算子（如AllReduce/ReduceScatter/AllGather等）；各rank间操作存在时间错位与重叠，可直观对比算子耗时与并行调度关系。

3) **与文档论点对应**：该图即文档2.3节接口`communication/duration/iterations`对应的"通信耗时分布"前端可视化，印证"迭代列表与通信耗时范围"的数据映射，说明页面通过此图呈现算子耗时与rank间调度时序，是通信瓶颈分析的核心视图。
- `communication_operatorLists_2.png`: ## 图文联合解读

**1) 图中内容**
图为数据库表`ClusterCommunicationTime`的数据视图，左侧树形结构展示了通信相关表族（ClusterCommunicationBandwidth/Matrix/BaseInfo等）。主表记录了同一group（group_name相同，rank_id=6032）下send/receive算子的逐次调用，关键字段**start_timestamp**与**elapsed_time**被红框标注，覆盖transit_time、wait_time、synchronization_time、idle_time等多维耗时。

**2) 技术结论**
通信耗时被分解为多个阶段粒度存储，每条hcom算子（含_397_X_1后缀）对应一行原语级记录，时间戳为ns级精度（1e15量级），形成可聚合迭代序列。

**3) 与文档关系**
对应文档 §2.3 中 `communication/duration/iterations` 接口的 **db 数据类型**（即表格中 `communication_duration_iterations_2` 那张图），证明"迭代列表与通信耗时范围"的数据源即来自此表，TEXT与DB两路数据并存。
- `communication_operatorLists_3.png`: 1) **图中内容**：左侧为数据库客户端树形结构，`main`库下展示 `cluster_base_info`、`communication_bandwidth_info`、`communication_matrix`、`communication_time_info` 等表（高亮选中）；右侧为 `communication_time_info` 表数据，含 `id/iteration_id/stage_id/rank_id/op_name/op_suffix/start_time/elapse_time/synchronization` 字段，红色虚线框突出 `start_time` 与 `elapse_time` 列，记录全部属于 iteration_id=16、stage_id=0 的 `hcom_allGather_479_0` 操作。

2) **技术结论**：证明通信耗时数据按 (iteration, stage, rank, op_name, op_suffix) 五元组细粒度存储，时间戳与耗时构成耗时范围统计的原始依据。

3) **与文档关系**：对应文档 2.3 节 `communication/duration/iterations` 接口的 db 数据来源，支撑"通信耗时范围"页面的展示。
- `communication_operatorLists_4.png`: **1）图示内容**：截图显示一个文件条目标签，标注文件名 `cluster_communication.json`，右侧数字"2"（被截断），图标为页面侧边栏的文档样式，背景为浅蓝色。

**2）技术结论**：该图为文档 2.1 节"原始数据（ATT 处理后文件）"的占位配图，说明 `cluster_communication.json` 是经过昇腾分析工具（Ascend Tensor Compiler Tool）处理后的输出文件，且与通信耗时图各出现两次——分别对应 **text** 与 **db** 两个数据场景，证实两种场景共享同一份原始数据源。

**3）与文档关系**：支撑"支持 TEXT 与 DB 两种数据场景"的设计论点，体现原始数据源唯一、处理路径并行的数据流结构。
- `communication_duration_list_1.png`: **图文联合解读：**

**1) 图示内容：** 上半部分为"通信时长"组合图，按卡序号（1/4/7/0/3/2/5/6）展示总时间（蓝柱）、传输时间（绿柱）、同步时间（青柱）、等待时间（紫柱）四组柱状图，并叠加同步/等待时间占比双折线（左Y轴ms，右Y轴Ratio 0-1）；下半部分为"通信时长数据分析"表格，列出8张卡的详细数值（含SDMA/RDMA带宽、通信算子详情链接）。

**2) 技术结论：** 卡0是显著异常点——同步时间仅0.354ms、占比0.024，远低于其他卡（占比0.73-0.99），但空闲时间高达1007ms；其余7卡均存在严重的同步/等待开销瓶颈，总时间主要由等待时间主导。

**3) 与文档关系：** 该图为`communication/duration/iterations`接口的可视化呈现，印证文档"迭代列表与通信耗时范围"的设计——通过图表与表格联动，既能宏观识别瓶颈卡（如卡0空闲异常），也能下钻查看具体算子。
- `communication_duration_list_2.png`: **图文联合解读：**

1）图为DB客户端左侧对象树及右侧表数据。左侧框出 `ClusterCommunicationBandwidth`、`ClusterCommunicationTime` 两张通信相关表；右侧展示带宽明细表，列含 id/iteration_id/stage_id/rank_id/op_name/op_suffix/transport_type/bandwidth_size/bandwidth_utilization/large_package_ratio/size_distribution/transit_size/transit_time，行数据按 rank_id(32/40/48/56/160/168) 展开 hcom_allGather_479_0_ 算子的 RDMA/HCCS/PCIE/SDMA/SIO 五种传输通道记录。

2）论证同一算子在一次 iteration 内按 rank 与 transport_type 维度被切分为多条记录，DB 中所有数值型字段暂为 0，说明 ATT 原始数据未携带带宽/时延指标，需经后处理计算填入。

3）对应文档 §2.1 中「DB 场景」原始数据结构，并支撑 §2.3 接口表「communication/matrix/bandwidthInfo」返回的 db 数据类型即来源于此表的字段映射关系。
- `communication_duration_list_3.png`: ## 图文联合解读

**1) 图中内容**：数据库管理工具界面，左侧树形结构展示 `cluster_*` 库与表（红框标注 `communication_bandwidth_info` 和 `communication_time_info`），右侧为 `communication_bandwidth_info` 表的数据网格，列含 `id/iteration_id/stage_id/rank_id/op_name/op_suffix/transport_type/bandwidth_size/utilization/large_package_ratio/size_distribution/transit_size/transit_time`。

**2) 技术结论**：每条记录按 rank × transport_type（RDMA/HCCS/PCIE/SDMA/SIO 循环）展开，体现通信带宽的"算子-传输通道"二维建模；数值均置 0，印证这是 **DB 场景下处理后的表结构样例**。

**3) 与文档关系**：对应"2.2 处理后 DB 数据内容—db 场景"截图，论证带宽字段在 DB 中以宽表形式持久化，为后续 `communication/matrix/bandwidthInfo` 等接口提供查询底座。
- `communication_duration_list_4.png`: **图示解读：**

1) **画面内容**：编辑器打开 `cluster_communication_matrix.json`（红框标注文件名），内容为 ATT 处理后的原始 JSON 数据。结构按通信域分组，每条记录包含 `SDMA/RDMA/PCIE/HCCS` 四类通道的 `Transit Size(MB)`、`Transit Time(ms)`、`Bandwidth(GB/s)`、`Large Packet Ratio`、`Size Distribution`，以及 `Communication Time Info`（时间戳、占比）和 `Wait/Synchronization/Idle Time`。绿框多处标注重复出现的 `Communication Bandwidth Info` 字符串，体现同一字段在数组中被反复序列化。

2) **技术结论**：矩阵带宽数据采用「通道级 + 时间戳」的扁平数组结构落地，单次迭代产生一条完整记录，跨通道指标可平行比较。

3) **文档关联**：对应文档第 2.1 节「原始数据（ATT 处理后文件）」text 场景，是后续 `communication/matrix/bandwidthInfo` 接口读取的源数据，验证了带宽矩阵的字段约定与数据流向。
- `communication_operatorDetails_1.png`: **图文联合解读：**

1) **图中内容**：标题为"通信后的关联算子分析"，表格列出8行算子数据，列含序号、开始时间、总时间、传输时间、同步时间、占比、等待时间、空闲时间、SDMA/RDMA带宽、带宽分析、通信算子详情。红框标注首行"通信算子详情"列的"查看更多"链接。

2) **技术结论**：通信耗时主要由同步与等待构成（占比普遍>95%），传输时间仅约14ms；不同算子SDMA带宽在15.79~16.82GB间波动，RDMA带宽为0；空闲时间与同步时间此消彼长。

3) **与文档论点关系**：对应文档"通信耗时"与"算子列表"维度，验证"页面接口总览"中通信耗时统计的结构化字段，并指示用户通过"查看更多"跳转至通信算子详情子页面。
- `communication_operatorDetails_2.png`: **图文联合解读：**

1) **画面内容**：DB客户端截图。左侧schema树中红色框高亮`ClusterCommunicationBandwidth`表，与`ClusterCommunicationMatrix`、`ClusterCommunicationTime`等同属`main`库。右侧展示该表数据：列含`step`、`rank_id`(6032)、`hcom_op_name`（hcom_allGather/hcom_reduceScatter）、`group_name`、HCCS、`transit_size/time`、`bandwidth`、`large_packet_ratio`、`package_size`、`count`、`total_duration`，每行为一次通信算子记录。

2) **技术结论**：该表为通信带宽详情的持久化存储，每行对应一次HCC集合通信事件，transit_size与transit_time共同支撑bandwidth字段计算，是`bandwidthInfo`接口的DB数据源。

3) **与文档关系**：对应§2.3表格第1行db数据类型列（`communication_db_data_1`），印证DB场景下带宽接口直接读取此表，与text场景的原始文件形成数据来源对照。
- `communication_operatorDetails_3.png`: **1) 图中内容**：DB客户端左侧表树选中 `communication_bandwidth_info`（红框），右侧展示其表结构与数据：列含 id、iteration_id、stage_id、rank_id、op_name、op_suffix、transport_type、bandwidth_size、bandwidth_utilization、large_package_ratio、size_distribution、transit_size、transit_time；数据行以 `hcom_allGather_479_0` 为例，同一算子在 rank_id 32/40/48/56/160 下分别记录 RDMA、HCCS、PCIE、SDMA、SIO 五种传输类型。

**2) 技术结论**：带宽信息以"算子 × rank × 传输介质"为粒度持久化，每个通信算子在DB中按 transport_type 拆分为多条记录，对应矩阵带宽详情。

**3) 与文档关系**：即文档表 2.3 中 `communication/matrix/bandwidthInfo` 接口对应的 `communication_db_data_1`，支撑页面通信矩阵带宽展示的数据底表。
- `communication_distribution_1.png`: **图示解读**

1) **画面内容**：双轴组合图，标题"HCCS"。蓝色柱状表示包数量（左轴0-400），绿色折线表示带宽GB/s（右轴0-18）。X轴为包大小(MB)：0、0.0032、0.0042、0.0164、0.0492、0.0164。含两条参考线（336.00包、15.12 GB/s）以及tooltip（0.0164 MB时6包、9.1361 GB/s）。

2) **技术结论**：包大小与带宽/包数量呈强正相关；在0.0164 MB附近性能达到峰值并触顶，带宽约15 GB/s、包量≈336，存在传输上限阈值，符合HCCS高速链路典型吞吐曲线。

3) **与文档关系**：对应 `communication/matrix/bandwidthInfo` 接口返回的矩阵带宽详情可视化，论证了通信矩阵页面"包大小—带宽—包数量"三维映射的设计合理性，为带宽分布与算子通信耗时分析提供数据支撑。
- `communication_distribution_2.png`: **1. 图中内容**
数据库管理工具截图，左侧树形结构中"ClusterCommunicationBandwidth"表被红框高亮选中；右侧数据表列出 HCCL 通信算子（hcom_allGather_383_X、hcom_reduceScatter_38），字段包括 step、rank_id、band_type(HCCS)、transit_size、bandwidth、**package_size**（红框标注）、count、**total_duration**（红框标注）。

**2. 技术结论**
通信带宽表由 ATT 原始数据归并生成；package_size 与 total_duration 是关键派生聚合指标，每行对应一次集合通信操作在指定 rank、group 下的包大小与总耗时，二者结合 transit_size、bandwidth 可还原带宽详情。

**3. 与文档论点关系**
对应文档 2.3 节"矩阵带宽详情"接口 `communication/matrix/bandwidthInfo`，红框精准指明前端页面展示所依赖的核心列，印证该表是 TEXT/DB 双场景下带宽矩阵的数据源。
- `communication_distribution_3.png`: # 图文联合解读

**1) 图中内容**
数据库客户端截图。左侧对象树以红框标注 `communication_bandwidth_info` 表；右侧数据表列出该表字段：id、iteration_id、stage_id、rank_id、op_name、op_suffix、transport_type、bandwidth_size、bandwidth_utilization、large_package_ratio、**size_distribution**（红框重点标注）、transit_size、transit_time。样本数据为 `hcom_allGather_479_0…` 算子，按 RDMA / HCCS / PCIE / SDMA / SIO 五种传输类型分行记录，size_distribution 当前为空 `{}`。

**2) 技术结论**
`communication_bandwidth_info` 表采用"算子 × 传输类型"展开式存储，size_distribution 为后续带宽分布图预留 JSON 字段，前端 `communication/matrix/bandwidthInfo` 接口直接读取该表渲染矩阵带宽详情。

**3) 与文档论点关系**
对应文档 §2.3 表格中 `communication/matrix/bandwidthInfo` 的 db 数据类型截图，佐证"页面接口 ↔ DB 表 ↔ 字段"一一映射的设计主张。
- `communication_bandwidth_1.png`: **图文联合解读：**

图示为"带宽分析"表格，呈现通信矩阵页面的链路带宽详情，字段包括链路方式（SDMA、HCCS、PCIE、SIO、RDMA）、传输大小(MB)、传输时长(ms)、带宽(GB/s)、大通通信包占比。该图对应文档 2.3 节接口表中 `communication/matrix/bandwidthInfo` 的页面展示（`communication_db_data_1` / `communication_text_data_1_1/1_2` 截图）。

技术结论：当前通信流量集中在 SDMA 与 HCCS 两条链路上，二者传输大小(1644.99MB)、时长(104.15ms)、带宽(15.7951 GB/s)完全一致，说明本次迭代的跨片通信主要走 HCCS 经 SDMA 等价路径；而 PCIE、SIO、RDMA 均为 0，表明该算子未触发跨主机/跨设备通信，大通包占比可忽略。

文档关系：印证正文所述"通信带宽按链路聚合、原始 ATT 数据与处理后 DB/Text 数据字段映射一致"的设计，并佐证 HCCS 在片间通信中的主导地位。
- `communication_bandwidth_2.png`: **图文解读：**

1) **图示内容**：数据库表视图，左侧列出 `ClusterCommunicationBandwidth/Matrix/Time` 等业务表；右侧表格字段含 `step、rank_id、hcom_op_name、band_type(HCCS)、transit_size、transit_time、bandwidth、large_packet_ratio、package_size、count、total_duration`，红框突出带宽计算关键五列。

2) **技术结论**：HCCS 链路上 allGather/reduceScatter 算子的 transit_size 稳定为 100.66、包大小 33.55，但带宽在 14–19 GB/s 区间波动，说明耗时与带宽并非线性相关，需依此字段做带宽详情展示。

3) **与文档关系**：对应文档 §2.3 表中 `communication/matrix/bandwidthInfo` 接口的 DB 数据源，红框字段即为页面矩阵带宽详情的前端取数映射。
- `communication_bandwidth_3.png`: **图解说明：**

1. **图示内容**：数据库管理工具（Navicat）视图，左侧树形结构展示 `communication_bandwidth_info` 表所在位置（main 库下通信相关表组），右侧显示该表数据。表包含 `id/iteration_id/stage_id/rank_id/op_name/op_suffix/transport_type` 及 `bandwidth_size/utilization/large_package_ratio/size_distribution/transit_size/transit_time` 等字段。**红框标注**三个关键列：`bandwidth_size`、`bandwidth_utilization`、`large_package_ratio`。数据按 `transport_type` 拆分为 RDMA/HCCS/PCIE/SDMA/SIO 五种传输通道记录。

2. **技术结论**：通信带宽详情按"算子+rank+传输类型"粒度拆分存储，覆盖 HCCL 五种硬件传输通道；三个红框字段是带宽矩阵页面的核心展示指标。

3. **与文档关系**：对应文档第 2.3 节"页面接口总览"中 `communication/matrix/bandwidthInfo` 接口对应的 DB 数据结构示意图，论证带宽详情页数据来源于 `communication_bandwidth_info` 表的这三列字段。
