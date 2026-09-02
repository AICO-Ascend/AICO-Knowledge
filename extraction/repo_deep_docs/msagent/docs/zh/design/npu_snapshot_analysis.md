# NPU平台内存快照分析设计文档

> 仓 `msagent` · 路径 `docs/zh/design/npu_snapshot_analysis.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msagent/docs/zh/design/npu_snapshot_analysis.md

# NPU 平台内存快照分析设计文档 — 一体化深度解读

---

## 【定位】

本文档定义了 `ascend-npu-snapshot-analyzer`（Ascend NPU Memory Snapshot 分析 Agent Skill）的完整设计——它是面向昇腾 NPU 的 PyTorch `torch_npu.npu.memory._dump_snapshot()` 内存快照数据的**离线自动化分析能力**，通过「pickle → SQLite → SQL/Python 分析 → 自包含 HTML 报告」四阶段流水线，为 LLM Agent 提供五大分析模式（峰值 / 碎片 / 泄漏 / OOM / 跨快照对比）的可驱动工作流。

---

## 【技术要点】

1. **数据格式转换**：将 `torch_npu.npu.memory._dump_snapshot()` 导出的 pickle（dict 格式）与 `_snapshot()` 导出的 list 格式反序列化后，转为 SQLite DB，遵循「一次转换、多次查询」原则。
2. **一文件一 DB**：DB 文件名 = pickle 文件名（仅换后缀 `.db`），避免多份数据混杂；跨快照对比通过 `ATTACH DATABASE` 机制实现，不合并到同一物理文件。
3. **延迟索引创建**：导入流程严格遵循「先建表 → 批量 INSERT → 最后建索引」，将 **1GB 文件的导入速度提升 10 倍以上**。
4. **分层工作流（Track A / Track B）**：简单查询由 SKILL.md 中的 **CTE 宏**承载（LLM 直接拼 SQL），复杂分析（峰值时序重建、泄漏检测算法等）由 `scripts/` 下 Python 脚本封装。
5. **五维分析模式**：`snapshot_analyze.py --mode` 支持 `peak` / `fragment` / `leak` / `oom` / `compare`；泄漏检测算法采用「**单调增长 + 长生命周期 + 堆栈归因**」三重判定。
6. **自包含 HTML 报告**：通过 ECharts 实现折线图、柱状图、内存布局图、堆栈归因图等交互式可视化；纯 CLI + HTML，**不提供 Web 服务或 API**。

---

## 【关键机制与数据】

### 工作原理（四阶段流水线）

1. **① 数据准备阶段**：Agent 调用 `python snapshot_to_db.py snapshot.pkl`，脚本经 `pickle.load()` 反序列化后，执行 `CREATE TABLE` + 批量 `INSERT`，最后才延迟创建索引，输出 `snapshot.db`。
2. **② 工作流决策阶段**：Agent 读取 SKILL.md，根据用户诉求匹配分析模式（如「分析 snapshot.pkl 有没有内存泄漏」→ 匹配到 `leak` 模式，对应 Track B 脚本调用路径）。
3. **③ 分析执行阶段**：Agent 调用 `python snapshot_analyze.py snapshot.db --mode leak`；`snapshot_analyze.py` 通过 `snapshot_queries.py` 封装的 CTE 函数（如 `get_device_overview(db_path)`）发起 `SELECT ... FROM segments/blocks/traces`，在内存中执行泄漏检测算法后返回 JSON。
4. **④ 报告生成阶段**：将 JSON 分析结果经模板渲染为 ECharts 交互式图表，输出 `snapshot_report.html` 返回给用户。

### 性能数据（原文明确给出）

| 优化项 | 数据 |
| -- | -- |
| 延迟索引创建的导入加速比 | **1GB 文件导入速度提升 10 倍以上** |

### 数据流核心实体

- **5 张表**：`devices`、`call_stacks`、`segments`、`blocks`、`traces`
- **call_stacks 去重**：相同堆栈只存一份（通过 `stack_hash` = MD5(frames_json) 做 `UNIQUE` 约束），节省存储
- **segments 段类型分类**：`large`（>1MB） / `small`
- **blocks 状态三态**：`active_allocated` / `active_pending_free` / `inactive`
- **traces 事件类型**：`alloc` / `free_requested` / `free_completed` / `segment_alloc` / `segment_free` / `segment_map` / `segment_unmap` / `snapshot` / `oom`（OOM 时 `addr=NULL`，`device_free` 记录 OOM 时可用内存）

---

## 【表格解读】

### 表 1：修订记录

| 日期 | 修订版本 | 修改描述 | 作者 | RFC 文档 |
| -- | -- | -- | -- | -- |
| 2026-06-11 | 1.0 | 初始版本，覆盖 ASCEND NPU Memory Snapshot 分析 Agent 的架构、DB 设计、分析能力、可视化方案与测试设计 | @msagent | npu_snapshot_analysis.md |

**解读**：v1.0 一次性覆盖五大设计维度（架构 / DB / 分析 / 可视化 / 测试），无后续版本，说明当前仍处于初始完整设计阶段，尚未进入迭代修订。

### 表 2：核心价值

| 价值点 | 说明 |
| -- | -- |
| NPU 原生支持 | 针对 `torch_npu` 的 snapshot 格式设计，兼容 CUDA snapshot 格式 |
| 一键分析 | pickle → SQLite DB → 分析报告，全流程自动化 |
| 多维度分析 | 覆盖峰值、碎片、扩容、泄漏、OOM 五大分析场景 |
| 交互式可视化 | 自包含 HTML 报告，含折线图、柱状图、内存布局图、堆栈归因图 |
| 跨快照对比 | 支持 ATTACH DATABASE 机制对比两份快照的差异 |
| Agent 可集成 | 通过 SKILL.md + scripts 的标准模式，LLM 可直接调用 |

**解读**：六条价值点对应六大产品差异化卖点；其中「跨快照对比」明确依赖 SQLite 原生 `ATTACH DATABASE` 语法（非应用层合并），是技术亮点。

### 表 3：设计目标与非目标

| 维度 | 目标 / 非目标 |
| -- | -- |
| 目标 1 | 支持 `_dump_snapshot()`（dict）和 `_snapshot()`（list）两种导出格式的解析 |
| 目标 2 | 将 pickle 转换为 SQLite DB，支持高效查询和跨快照对比 |
| 目标 3 | 提供总体概览、峰值、碎片、泄漏、OOM 五种分析模式 |
| 目标 4 | 支持跨快照对比模式（ATTACH DATABASE） |
| 目标 5 | 生成自包含 HTML 报告，含 ECharts 交互式图表 |
| 目标 6 | 通过 SKILL.md 的 CTE 宏（Track A）+ 脚本调用（Track B）实现 Agent 驱动工作流 |
| 非目标 1 | 不实现实时采集功能（仅离线 pickle） |
| 非目标 2 | 不实现 CUDA 特有的硬件细节分析（如 CUDA stream 调度） |
| 非目标 3 | 不实现 device_traces 的 GPU 侧执行时序分析（Phase 1 仅解析 traces 表） |
| 非目标 4 | 不实现 Web 服务或 API（纯 CLI + HTML 报告） |
| 非目标 5 | 不实现多进程/分布式训练的内存协调分析 |

**解读**：注意目标 3 中列出的五种模式与表 2「多维度分析」中的五场景不完全一致——目标 3 用「**总体概览**」替代了「**扩容**」，说明「扩容统计」实际上是「峰值分析」的子能力，而「总体概览」作为独立基础模式存在。

### 表 4：devices 表

| 字段 | 类型 | 约束 | 说明 |
| -- | -- | -- | -- |
| `id` | INTEGER | PK, AUTOINCREMENT | 主键 |
| `device_index` | INTEGER | UNIQUE, NOT NULL | NPU 设备编号，对应 snapshot 中的 device 值 |
| `device_type` | TEXT | DEFAULT 'Ascend-NPU' | 设备类型标识 |

**解读**：轻量设备字典表，`device_index` 唯一约束避免重复入库，`device_type` 默认值硬编码为 `Ascend-NPU`，体现对昇腾生态的强绑定。

### 表 5：call_stacks（调用栈字典表）

| 字段 | 类型 | 约束 | 说明 |
| -- | -- | -- | -- |
| `id` | INTEGER | PK, AUTOINCREMENT | 主键 |
| `stack_hash` | TEXT | UNIQUE | 堆栈帧列表的 MD5 哈希，用于去重 |
| `frames_json` | TEXT | - | JSON 数组格式的完整堆栈帧列表 |

**解读**：去重字典表是节省存储的关键设计——通过 `stack_hash` MD5 做 UNIQUE 约束，使 segments/blocks/traces 三张表仅以 `stack_id` 外键引用即可，避免堆栈帧字符串的重复冗余。

### 表 6：segments（内存段表）

| 字段 | 类型 | 约束 | 说明 |
| -- | -- | -- | -- |
| `id` | INTEGER | PK, AUTOINCREMENT | 主键 |
| `device_id` | INTEGER | NOT NULL, FK→devices | 所属设备 |
| `address` | INTEGER | - | Segment 起始虚拟地址 |
| `total_size` | INTEGER | - | aclrtMalloc 分配的段总大小 (Reserved) |
| `allocated_size` | INTEGER | - | 已分配使用的内存大小 |
| `active_size` | INTEGER | - | 正在使用或等待释放的内存大小 |
| `requested_size` | INTEGER | - | 用户请求的内存大小 |
| `stream` | INTEGER | - | 关联的 NPU stream |
| `segment_type` | TEXT | - | 段类型：`large` (>1MB) 或 `small` |
| `pool_id_0` | INTEGER | - | segment_pool_id 元组第 1 元素 |
| `pool_id_1` | INTEGER | - | segment_pool_id 元组第 2 元素 |
| `is_expandable` | INTEGER | - | 是否可扩容 (0/1) |
| `stack_id` | INTEGER | FK→call_stacks | 分配时的堆栈引用 |

**解读**：四层 Size 维度（`total_size` / `allocated_size` / `active_size` / `requested_size`）是计算碎片率的核心数据源；`segment_type` 以 1MB 为分界划分 large/small，与 PyTorch 缓存分配器策略一致；`pool_id_0/1` 将元组扁平化为两列，适配 SQLite 单值字段约束。

### 表 7：blocks（内存块表）

| 字段 | 类型 | 约束 | 说明 |
| -- | -- | -- | -- |
| `id` | INTEGER | PK, AUTOINCREMENT | 主键 |
| `segment_id` | INTEGER | NOT NULL, FK→segments, CASCADE | 所属 segment |
| `address` | INTEGER | - | Block 起始地址 |
| `size` | INTEGER | - | 实际占用大小（含对齐） |
| `requested_size` | INTEGER | - | malloc 请求大小（可能小于 size） |
| `state` | TEXT | - | 状态：`active_allocated` / `active_pending_free` / `inactive` |
| `stack_id` | INTEGER | FK→call_stacks | 分配时的堆栈引用 |

**解读**：`requested_size` ≤ `size`（含对齐填充）的差值即为块级碎片；`state` 三态可推算 `inactive` 块占比即为 segment 内部空闲率；`CASCADE` 级联删除保证 segment 删除时子 block 同步清理。

### 表 8：traces（时序事件表）

| 字段 | 类型 | 约束 | 说明 |
| -- | -- | -- | -- |
| `id` | INTEGER | PK, AUTOINCREMENT | 主键 |
| `device_id` | INTEGER | NOT NULL, FK→devices | 所属设备 |
| `trace_index` | INTEGER | - | 设备内事件序号，用于还原时序 |
| `action` | TEXT | - | 事件类型：`alloc` / `free_requested` / `free_completed` / `segment_alloc` / `segment_free` / `segment_map` / `segment_unmap` / `snapshot` / `oom` |
| `addr` | INTEGER | - | 关联内存地址（OOM 时为 NULL） |
| `device_free` | INTEGER | - | 仅 OOM 事件存在，OOM 时可用内存 |
| `size` | INTEGER | - | 操作的内存大小 |
| `stream` | INTEGER | - | 关联的 NPU stream |
| `stack_id` | INTEGER | FK→call_stacks | 事件关联的堆栈引用 |

**解读**：九种 `action` 类型覆盖完整生命周期（alloc/free_requested/free_completed 三段式，加上段级与快照事件、OOM 异常事件）；`trace_index` 是设备内单调递增序号，配合 `(device_id, trace_index)` 联合索引可高效还原时序；`device_free` 字段专为 OOM 根因分析设计，仅 OOM 行有值。

### 表 9：索引策略

| 索引名 | 表 | 字段 | 用途 |
| -- | -- | -- | -- |
| `idx_blocks_state` | blocks | `state` | 全局碎片率计算 |
| `idx_blocks_stack` | blocks | `stack_id` | 堆栈归因查询 |
| `idx_blocks_segment` | blocks | `segment_id` | segment 关联查询 |
| `idx_blocks_segment_state` | blocks | `segment_id, state` | 按 segment 分析碎片 |
| `idx_traces_stack` | traces | `stack_id` | 堆栈归因查询 |
| `idx_traces_device_action` | traces | `device_id, action` | OOM 事件快速定位 |
| `idx_traces_device_index` | traces | `device_id, trace_index` | 时序范围遍历 |
| `idx_segments_stack` | segments | `stack_id` | 堆栈归因查询 |
| `idx_segments_device` | segments | `device_id` | 设备过滤 |
| `idx_segments_device_type` | segments | `device_id, segment_type` | large/small 分类统计 |

**解读**：10 个索引全部为非主键的二级索引，集中服务于三类查询——**碎片统计**（state / segment_state）、**堆栈归因**（三张表的 stack_id）、**OOM/时序检索**（device_action / device_index）。`idx_blocks_segment_state` 是唯一复合索引，体现「按段分析碎片」这一高频组合查询的优先级。

### 表 10：数据映射关系（原文已截断）

| pickle 字段 | DB 表 | DB 字段 | 说明 |
| -- | -- | -- | -- |
| `segments[].device` | `segments` | `device_id` | 外键关联 devices.id |
| `segments[].address` | `segments` | `address` | 保存原始 in…（原文截断） |

**解读**：文档此处被截断，仅可见前两行映射规则；其余 `segments[].total_size` / `allocated_size` / `active_size` / `requested_size` / `stream` / `segment_type` / `segment_pool_id` / `is_expandable` / `stack_id` 等字段的映射未在原文完整展示。

---

## 【公式解读】

**原文无公式**（无 LaTeX 数学式或伪代码算法公式）。

文档中仅以自然语言描述算法行为，例如泄漏检测为「**单调增长 + 长生命周期 + 堆栈归因**」三重判定，但未给出带符号的判定公式或数学表达。具体阈值参数定义在 `references/analysis_methodology.md`（本文档内未展开）。

---

## 【关联】

文档通过目录结构图与架构图明确了下游模块依赖与上下游关系：

| 关联对象 | 关系性质 | 说明 |
| -- | -- | -- |
| `SKILL.md` | **上游入口** | 定义主工作流 + CTE 宏 + 输出规范，LLM Agent 首先读取此文件 |
| `scripts/snapshot_to_db.py` | **下层基础设施** | pickle → SQLite 转换器，DB 的唯一生产者 |
| `scripts/snapshot_queries.py` | **中层查询库** | 封装 CTE 函数，被 `snapshot_analyze.py` 调用 |
| `scripts/snapshot_analyze.py` | **上层业务入口** | 五种分析模式（peak/fragment/leak/oom/compare）的统一调用入口 |
| `references/snapshot_schema.md` | **横向参考** | Segment/Block/TraceEntry 字段定义，作为 schema 文档来源 |
| `references/analysis_methodology.md` | **横向参考** | 检测算法、判定规则、阈值定义（具体数值未在本设计文档展开） |
| `references/analysis_templates.md` | **横向参考** | 典型分析套路：模板触发条件、决策树、输出字段清单 |
| `tests/test_snapshot_to_db.py` | **测试覆盖** | 转换工具单元测试 |
| `tests/test_snapshot_analyze.py` | **测试覆盖** | 分析逻辑单元测试 |
| `SQLite ATTACH DATABASE` | **跨快照机制** | 跨 DB 物理连接，但每个 pickle 仍独立成库 |
| `ECharts` | **可视化引擎** | 自包含 HTML 报告的图表渲染框架（折线/柱状/内存布局/堆栈归因） |
| `torch_npu` | **上游数据源** | `_dump_snapshot()`（dict）与 `_snapshot()`（list）两种导出 API |
| `PyTorch memory_viz` | **替代关系** | 官方工具仅支持 CUDA 单份浏览，本 Skill 补齐 NPU + 对比能力 |

**Phase 1 演进路径**：`traces` 表当前仅做解析与索引，**不做 device_traces 的 GPU 侧执行时序关联分析**——预留为后续 Phase 扩展点。

---

## 【使用方法】

**原文涉及**：

### 命令行调用方式

1. **pickle → SQLite 转换**（数据准备阶段）：
   ```text
   python snapshot_to_db.py snapshot.pkl
   ```
   输出：`snapshot.db`（与 pickle 同名，后缀替换）

2. **执行分析**（分析执行阶段，模式二选一示例）：
   ```text
   python snapshot_analyze.py snapshot.db --mode leak
   ```
   `--mode` 支持五个值：`peak` / `fragment` / `leak` / `oom` / `compare`

3. **报告生成**：由 `snapshot_analyze.py` 自动调用 HTML 报告生成器，输出 `snapshot_report.html`

### Agent 驱动工作流

- **Track A（CTE 宏直查）**：LLM 直接读取 SKILL.md 中预置的 SQL CTE 宏，拼装后查询 SQLite DB
- **Track B（脚本封装）**：LLM 路由匹配到分析模板后，调用 `scripts/snapshot_analyze.py` 对应模式

### 输出物

- `snapshot.db`（SQLite 数据库）
- `snapshot_report.html`（自包含，含 ECharts 交互式图表）

### 非目标（明确不支持）

- 实时内存采集
- Web 服务 / API 接口
- CUDA stream 调度 / device_traces GPU 执行时序关联（Phase 1 不做）
- 多进程/分布式训练的内存协调分析
