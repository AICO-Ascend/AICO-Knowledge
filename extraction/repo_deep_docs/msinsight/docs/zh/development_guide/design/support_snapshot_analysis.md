# 支持内存快照展示和分析

> 仓 `msinsight` · 路径 `docs/zh/development_guide/design/support_snapshot_analysis.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msinsight/docs/zh/development_guide/design/support_snapshot_analysis.md

# 一体化深度解读：msinsight 内存快照分析设计文档

---

## 【定位】

本文档提出 MindStudio Insight（msinsight）在昇腾（Ascend）平台上**面向大模型训练与推理场景的内存快照（snapshot）离线分析能力**的整体设计方案，旨在解决大文件内存数据难以高效分析、可视化展示与问题定位的痛点。

---

## 【技术要点】

1. **三层前后端分离架构**：前端 React + TypeScript（含 MobX Stores、ECharts 渲染），后端 C++，数据层 SQLite 存储，通过 WebSocket 与前端通信。
2. **SQLite 三表数据模型**：核心表为 `block` 表（内存块）、`trace_entry` 表（事件流水）、`dictionary` 表（字典），并按 device 维度分表（如 `block_<deviceId>`）。
3. **三类核心内存曲线指标**：支持 `allocated` / `reserved` / `active` 三个维度的时间序列展示，十万级数据点渲染时间 < 10 秒。
4. **三个专项分析器**：分别针对内存泄漏（`MemoryLeakAnalyzer`，分析时间 < 5 秒）、Segment 申请统计（`SegmentAllocAnalyzer`，< 10 秒）、申请前碎片评估（`FragmentationAnalyzer`，< 10 秒）。
5. **多维查询能力**：所有查询接口支持分页、过滤、排序，且统一要求响应时间 < 10 秒（仅泄漏分析要求 < 5 秒）。
6. **跨平台兼容性**：支持 Ubuntu 20.04+、CentOS 8+、Windows 10+，并兼容多 device 场景。

---

## 【关键机制与数据】

### 工作原理与数据流

**整体架构（原文 §3.1.1）**：系统分为前端层、后端层、数据层。前端 Memory 页面通过 WebSocket 发起请求，C++ 后端的 Request Handlers 接收后调用服务层（Service/SegmentService/三个 Analyzer），最终由 `MemSnapshotDatabase` 封装层访问 SQLite 物理表。

**数据加载流程（原文 §3.1.3 序列图 1）**：
1. 用户选择快照文件 → 页面更新 session 状态
2. 后端调用 `OpenDbReadOnly(dbPath)` 打开只读数据库
3. `CheckAllTableExist()` 校验表结构
4. 查询 device 列表返回前端供用户选择

**内存曲线查询流程（原文 §3.1.3 序列图 2）**：
`QueryMemoryRecords(params)` → `SELECT FROM trace_entry` → 返回 `MemoryRecord` 列表 → 前端 `MemoryLineChart`（ECharts）渲染 allocated/reserved/active 三条曲线。

**内存块查询流程（原文 §3.1.3 序列图 3）**：
`QueryBlocksTable(queryParams)` → `SELECT FROM block_<deviceId>` → 返回 `BlockTableItemDTO` 列表 → `MemoryDetailTable` 渲染分页表格。

### 性能数据（原文用例章节）

| 用例 | 性能要求 | 原文位置 |
|---|---|---|
| 内存总量曲线渲染（十万级数据点） | < 10 秒 | 用例 1 |
| 内存块详情分页查询 | < 10 秒 | 用例 2 |
| 内存事件分页查询 | < 10 秒 | 用例 3 |
| device 切换响应 | < 10 秒 | 用例 4 |
| 时间点内存状态查询 | < 10 秒 | 用例 5 |
| 内存泄漏分析 | **< 5 秒** | 用例 6 |
| Segment 申请事件统计 | < 10 秒 | 用例 7 |
| Segment 申请前碎片评估 | < 10 秒 | 用例 8 |

> **关键差异**：所有查询类操作时间预算为 10 秒，唯独"内存泄漏分析"为更严格的 5 秒——因为它需要在用户交互过程中实时完成，而其他多为分页懒加载。

### 核心数据结构（原文 §3.1.2）

- **TraceEntry**：内存事件，类型包括 `alloc` / `free` / `segment_alloc`
- **Block**：内存块，含地址、大小、状态、alloc/free event_id
- **Segment**：由多个 Block 组成的大内存段
- **MemoryRecord**：单时间点的 allocated/reserved/active 快照
- **MemoryLeakCandidate**：泄漏候选（地址、大小、类型、分配时间）
- **SegmentAllocEvent**：新申请 Segment 事件（排除已申请/预留内存的再分配）
- **FragmentationInfo**：碎片率、碎片分布、最大连续空闲块三项指标

---

## 【表格解读】

**原文无表格**（markdown 数据表格）。

文档中存在两种可视化图表，但均非参数表/性能对比表：
- **ASCII 架构图**（§3.1.1）：展示前端层 / 后端层 / 数据层的逻辑划分与组件归属；
- **PlantUML 组件图**（§3.1.2）：展示 8 个前端组件、8 个后端组件、3 个数据表的依赖关系；
- **Mermaid 序列图**（§3.1.3）：分别描绘数据加载、曲线查询、内存块查询、时间点状态查询（最后一个被截断）四个流程。

如需将上述信息结构化为对照表，可整理如下（仅基于原文组件描述，非原文直接提供）：

| 层 | 组件 | 职责（原文） | 对应主要 Handler/接口 |
|---|---|---|---|
| 前端 | MemoryPage | 主入口，集成所有内存分析功能 | — |
| 前端 | MemoryLineChart | ECharts 渲染 allocated/reserved/active 三曲线 | — |
| 前端 | MemoryDetailTable | 分页/过滤/排序展示 block 或 event | — |
| 前端 | MemoryLeakPanel | 展示泄漏点和统计信息 | — |
| 前端 | SegmentAllocStatsPanel | 展示 Segment 申请统计 | — |
| 前端 | FragmentationPanel | 展示申请前碎片率/分布/最大空闲块 | — |
| 后端 | MemSnapshotParser | 解析原始快照并导入 SQLite | — |
| 后端 | MemSnapshotDatabase | 封装所有 SQLite 操作 | — |
| 后端 | MemSnapshotService | 高级查询（如时间点 segments 状态） | 部分接口 |
| 后端 | MemSnapshotSegmentService | 继承自 Service，处理 Segment 构建查询 | 部分接口 |
| 后端 | MemoryLeakAnalyzer | 泄漏分析 | QueryMemoryLeakHandler |
| 后端 | SegmentAllocAnalyzer | Segment 申请统计 | — |
| 后端 | FragmentationAnalyzer | 申请前碎片评估 | — |
| 后端 | Request Handlers | HTTP 处理 | QueryMemSnapshotAllocationHandler、QueryMemSnapshotBlockHandler、QueryMemSnapshotStateHandler 等 |
| 数据 | SQLite 三表 | 持久化存储 | block表、trace_entry表、dictionary表 |

---

## 【公式解读】

**原文无公式**（无 LaTeX 数学公式，也无伪代码形式的算法式）。

文档中出现的"伪代码式"内容仅为 ASCII 架构图、PlantUML 组件依赖图、Mermaid 时序图，均为结构/流程表达，不含数值计算公式。

---

## 【关联】

> **注：原文未在文末提供内部链接清单（"内部链接: (无)"）**，以下关联基于文档自身对上下游的描述整理。

### 显式声明的非目标（边界关系）

- **不改变数据采集方式**：本设计仅消费已采集的快照文件，不涉及 Ascend 平台采集端（`MemSnapshotParser` 是消费侧，不替代采集器）。
- **不提供实时监控**：本设计为**离线分析**，与 msinsight 中可能存在的实时 profiling 模块无功能重叠。
- **不支持 PyTorch 原生 snapshot 格式**：明确排除了与 PyTorch Profiler 的 `.pytorch_snapshot` 兼容路径，意味着仅服务于昇腾自有快照格式。
- **不提供自动优化建议**：分析层只输出诊断数据，优化策略由用户/上层决策。

### 上下游模块推测（基于原文命名）

- **上游（数据来源）**：昇腾平台 `msprof`/`mstx` 等内存采集工具生成的原始快照 → 经 `MemSnapshotParser` 导入 SQLite。
- **下游（消费方）**：前端 `MemoryPage` 集成于 msinsight 主 UI；MobX Stores 中的 `memoryStore`、`sessionStore` 与 msinsight 全局 session/路由管理耦合；WebSocket 通道与 msinsight 后端整体通信协议一致。
- **横向（同领域模块）**：与 timeline（事件时间线）、operator（算子分析）、communication（集合通信分析）等其他 msinsight 子模块共享同一前端壳与后端 C++ 框架。

### 内部组件依赖链（原文 §3.1.2 UML）

```
MemoryPage → LineChart / DetailTable / Header / LeakPanel / AllocStatsPanel / FragPanel
MemoryPage → MobX Stores
Request Handlers → {Service, SegmentService, LeakAnalyzer, AllocAnalyzer, FragAnalyzer}
所有服务/分析器 → MemSnapshotDatabase → {block表, trace_entry表, dictionary表}
MemSnapshotParser → MemSnapshotDatabase （一次性导入）
```

---

## 【使用方法】

**原文未涉及具体的启用方式、配置项或命令**。文档当前定位为 Draft 状态（§0 状态字段），仅完成 §1 概述、§2 用例分析、§3.1 总体方案与核心流程设计，尚未提供：

- 编译/构建命令
- SQLite schema DDL
- HTTP/WebSocket API 端点签名
- 配置文件项（如"大 Segment 阈值"——用例 7 提到"支持配置'大 Segment'的阈值"，但未给出参数名/默认值）
- 用户操作手册或截图

可从文档推断的**接口命名约定**（仅作参考，非完整配置）：
- 后端 Handler 命名遵循 `QueryMemSnapshot{Allocation|Block|State}Handler` 前缀 + `QueryMemoryLeakHandler`（见 §3.1.2 组件描述第 7 点）。
- 数据库访问入口为 `OpenDbReadOnly(dbPath)`（原文数据加载流程序列图）。
- 数据表命名按 device 分表：`block_<deviceId>`（原文内存块查询流程序列图）。

如需获取完整启用方式，需等待文档后续章节（推测为 §4 接口设计、§5 部署/配置、§6 测试）补齐，或参考仓库其他已落地模块的接入文档。
