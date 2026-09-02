# MindStudio Insight 支持 NUMA分析特性设计说明书

> 仓 `msinsight` · 路径 `docs/zh/development_guide/design/numa_analysis.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msinsight/docs/zh/development_guide/design/numa_analysis.md

# 「msInsight NUMA分析」设计文档深度解读

## 【定位】
这篇文档是 MindStudio Insight(msInsight) 在 A+K 场景（CPU 侧采用鲲鹏）下，针对大模型训练/推理场景中 **NUMA(Non-Uniform Memory Access) 相关性能问题定位** 的特性设计说明书，目标是提供平台级与 Socket 级的 NUMA 时序数据可视化、架构拓扑展示以及 CPU 侧 NUMA 数据与 NPU 侧 MindStudio 数据的关联分析能力。

---

## 【技术要点】

1. **场景与目标硬件**：聚焦 A+K 场景，CPU 端为鲲鹏，覆盖 Uncore 与 NUMA 指标的时序采集，将 CPU 侧 NUMA 性能数据与 MindStudio NPU 数据关联分析以协同定位瓶颈。
2. **NUMA 架构图能力**：可展示节点（Node）、链路信息详情，点击 NUMA 元素、Socket 元素及各链接在扩展区域呈现对应统计信息。
3. **Platform Metric 可视化（10 项指标）**：DRAM Write Bandwidth、Cross Socket Read Bandwidth、Cross SCCL、Total Read BandWidth、Total Read BandWidth（原文重复列出）、LLC BandWidth、Inner Read BandWidth、Total External Traffic Impact、External Traffic Impact(Socket level)、External Traffic Impact(Node level)。包含 DDR 读写监测、基于 HHA 数据的 NUMA 节点带宽监测、NUMA 流量占比计算及时序数据追踪。
4. **线程分析能力**：以时序图展示线程的 3 种状态统计——active、sync wait、preemption。
5. **命中率分析能力**：支持 LLC 缺失率/命中率（每线程）分析。
6. **数据源与导入流程**：数据来源为 msProf 采集的 `.db` 文件，导入后经后端解析建库/数据结构，前端通过交互发起查询并渲染架构图与 Timeline 泳道。

---

## 【关键机制与数据】

**工作原理（原文 3.2 处理流程）**：
1. 用户采集 NUMA 数据，生成 db 格式数据。
2. 用户在 MindStudio Insight 中导入数据文件。
3. 后端解析数据并建立查询所需的数据结构或数据库连接。
4. 前端按页面交互发起查询请求。
5. 后端返回 NUMA 架构信息、指标变化信息查询结果。
6. 前端展示 NUMA 架构图、Timeline 中分泳道呈现 Platform Metric、线程、命中率等信息。

**典型使用场景（原文 2.2 PyTorch Snapshot 场景）**：
1. 通过 msprof 采集 NUMA 数据，采集数据合入 db 库中。
2. 在 MindStudio Insight 中导入采集数据，参考 NUMA 架构及各指标变化情况分析问题瓶颈。

**性能与安全相关原文约束**：
- 建议运行环境内存超过 **16GB**（原文 2.3.2）。
- 建议内存数据文件不超过 **1GB**（原文 2.3.2）。
- Linux 建议 `glibc > 2.30`（原文 2.3.2）。
- Windows 10+、macOS 13.0+（原文 2.3.2）。
- 不在本文中承诺具体响应时间；具体指标需以性能测试结果为准（原文 6.1）。

---

## 【表格解读】

### 表 1：特性需求列表（原文 1.2）

| 需求编号 | 需求名称 | 特性描述 | 可验证资料 |
| --- | --- | --- | --- |
| 1 | NUMA相关问题分析 | 支持 NUMA架构图展示、Platform Metric可视化、线程分析及命中率分析 | （空） |

**逐行解读**：
- **需求编号 1**：当前唯一明确编号的需求条目。
- **需求名称「NUMA相关问题分析」**：将 NUMA 相关定位能力聚合为一个总需求。
- **特性描述**：把能力拆为四块——架构图、Platform Metric 可视化、线程分析、命中率分析，对应 1.1 范围章节中的 4 项子能力。
- **可验证资料**：原文未填具体内容，留待后续补充（与第 4、5 章的待确认事项一致）。

### 表 2：数据来源（原文 3.1）

| 数据源 | 数据格式 | 主要展示内容 | 说明 |
| --- | --- | --- | --- |
| msProf | .db | NUMA架构图、Platform Metric的10个指标内容、线程分析数据、命中率分析数据 | （空） |

**逐行解读**：
- **数据源 msProf**：唯一数据来源工具，明确不依赖其他采集器。
- **数据格式 `.db`**：与 msInsight 既有导入通路一致，复用既有数据库解析能力。
- **主要展示内容**：四项分别对应架构图、10 项 Platform Metric、线程分析（active/sync wait/preemption）、LLC 命中率/缺失率（每线程）。
- **说明**：原文未填，文档未列出具体采集命令或参数细节（4.2 节用户入口处采集示例原文标注「待补充」）。

> 注：原文还存在「改版记录」「缩略语清单」两张表，但属于元数据/术语说明，与功能设计无直接关联，故此处聚焦于设计内容相关的两张表。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **与其他特性的协同**：NUMA 分析被定位为与 MindStudio **NPU 数据**关联分析的协同手段（原文 1：「CPU侧NUMA性能数据与MindStudio NPU数据关联分析，提升协同定位性能瓶颈的效率」），即 NUMA 数据用于补充 NPU 视角之外的 host 侧瓶颈。
- **页面跳转关系**：Timeline 页面可选择分析时间区域，并可**跳转到 NUMA 页面**，NUMA 页面统计分析该时间区域内的数据（原文 4.3）。
- **数据采集侧依赖**：依赖 msProf/msprof 完成 .db 采集（原文 2.2、3.1），用户指南侧的采集示例「待补充」（原文 4.2）。
- **DFX 模块自洽**：性能、异常、安全、可测试性四节（第 6 章）均围绕同一数据通路——.db 导入 → 后端解析 → 前端展示——做风险与验证设计。
- **下游文档/章节**：第 4 章（NUMA 分析）、第 5 章（Platform Metric/线程/命中率）两个 Use Case 是同一特性的两个并列呈现视图，共享同一 .db 数据源与后端解析通路。
- **内部链接**：原文标注「(无)内部链接」。

---

## 【使用方法】

- **数据采集入口**：通过 msprof 采集 NUMA 数据，采集数据合入 db 库中（原文 2.2）。具体的采集命令示例原文标注「待补充」（原文 4.2）。
- **数据导入**：在 MindStudio Insight 中导入 msProf 生成的 `.db` 文件（原文 3.2 步骤 1–2）。
- **分析页面**：
  - NUMA 页面：展示 NUMA 架构图，点击 NUMA 元素、Socket 元素及各链接在扩展区域展示统计信息（原文 4.1、4.3）。
  - Timeline 页面：分泳道呈现 Platform Metric（10 项指标）、线程分析（active / sync wait / preemption）、命中率分析（LLC 缺失率/命中率，每线程）（原文 5.3）。
- **环境与硬件约束（原文 2.3）**：
  - 硬件支持范围以 MindStudio Insight 发布说明和对应数据采集工具说明为准（原文 2.3.1）。
  - 操作系统：Windows 10+、Linux（建议 `glibc > 2.30`）、macOS 13.0+。
  - 设备内存建议 > 16GB，内存数据文件建议 ≤ 1GB。
- **DFX/安全约束（原文 2.3.3、6.3）**：导入文件需做路径、类型、大小合法性校验；日志避免打印敏感路径与完整调用栈；不新增对外监听端口与认证方式。

## 图文联合解读

- `numa_high_level_diagram.png`: 图示4 Socket（含NUMA 0-7节点）、DDR直连及跨Socket互连链路，右侧呈现跨Socket读7.3 GOps、DRAM 34 GB总指标，印证§1.1"NUMA架构图+Platform Metric可视化"需求设计，支撑A+K场景协同定位NUMA瓶颈。
- `thread_analysis.png`: **图示解读：**

1）**画面结构**：左侧为进程/线程层级树（Process 455984 → Thread 456062 → PyTorch/acl/node），右侧为时序条带。蓝色=Active(CPU)、橙色=Sync Wait、红色=Preemption，悬浮框显示13.32s-13.50s区间聚合：Active 44.5%、Sync Wait 14.3%、Preemption 41.2%，采样间隔0.18s。

2）**技术结论**：证明msInsight具备按子调用栈逐帧聚合线程运行时态的能力，可量化CPU有效执行与等待/抢占开销比例，定位性能瓶颈（如本例Preemption占比偏高，暗示调度干扰）。

3）**与文档关系**：直接对应§1.1需求3"线程分析——支持active、sync wait、preemption三种状态统计"，是NUMA特性中线程维度可视化的实证截图。
- `miss_hit_analysis.png`: **图文联合解读：**

图示展示了**每线程LLC命中率分析**的可视化效果：左侧为层级导航树（Host→Process→Thread→PyTorch→acl/node/LLC Cache Miss/Hit），选中线程456062的acl模块；右侧呈现时序彩色条带（红=Miss、蓝/绿=Hit），并通过悬浮提示框标注0.03s聚合粒度下Miss:15% / Hit:85%。底部堆叠柱图汇总显示缓存命中/缺失占比。

该图论证了msInsight能够**在线程粒度上对LLC命中率进行时序追踪与聚合统计**，为NUMA跨Socket访问瓶颈定位提供量化依据，**直接对应文档1.1节"命中率分析：支持LLC缺失率/命中率（每线程）分析"需求**。
