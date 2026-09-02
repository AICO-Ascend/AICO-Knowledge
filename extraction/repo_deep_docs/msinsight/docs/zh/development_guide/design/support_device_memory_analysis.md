# MindStudio Insight 支持 Device 内存分析特性设计说明书

> 仓 `msinsight` · 路径 `docs/zh/development_guide/design/support_device_memory_analysis.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msinsight/docs/zh/development_guide/design/support_device_memory_analysis.md

# MindStudio Insight 支持 Device 内存分析特性设计说明书 —— 一体化深度解读

---

## 【定位】

本文档是 MindStudio Insight 中 **Device 侧内存分析特性**（PyTorch Snapshot + msMemScope 两条采集路径）的开发设计说明书，规定其数据来源、处理流程、页面能力、DFX 设计与验证方法，用于辅助大模型训练/推理场景下 OOM、内存泄漏、内存碎片与低效显存占用问题的图形化定位。

---

## 【技术要点】

1. **两条独立采集路径**：① PyTorch NPU 提供的 `torch_npu.npu.memory._record_memory_history` / `_dump_snapshot` 导出 `pickle` 文件（PyTorch Snapshot）；② msMemScope 工具采集导出 `memscope_dump_{timestamp}.db`（MindStudio Memory Scope）。二者数据格式与展示内容不同，分别对应不同的后端解析与前端视图。
2. **统一的 6 步处理流程**（见 §3.2）：采集 → 导入 → 后端解析并建立查询数据结构/DB 连接 → 前端按页面交互发起查询 → 后端返回图表/表格/详情/筛选结果 → 前端可视化展示（内存生命周期、调用栈、内存池状态、明细）。
3. **PyTorch Snapshot 页面能力**（§4.3）：内存块生命周期图、内存池状态图、内存块视图、内存事件视图、选中详情、自动筛选区间未释放内存块共 6 类视图。
4. **msMemScope 页面能力**（§5.2/§5.3）：调用栈火焰图（按线程和函数查看 Python 调用栈）、内存块生命周期图（申请/释放/访问事件）、内存详情拆解图（按 CANN、PTA 等内存层级）、内存块视图、内存事件视图、低效显存筛选共 6 类视图。
5. **环境约束**（§2.3.2）：Windows 10+；Linux 建议 `glibc > 2.30`；macOS 13.0+；运行 MindStudio Insight 的设备内存建议超过 **16GB**；建议内存数据文件不超过 **1GB**。
6. **DFX 四项要求**（§6）：①性能——不对外承诺具体响应时间，仅建议对大文件（1GB 以内）、长范围查询、缩放/平移做验证；②异常——覆盖格式不匹配、文件损坏/字段缺失、文件过大、空时间范围、缺失调用栈/访问事件、Snapshot 缺申请或释放记录；③安全——不新增端口/认证、对导入路径与类型做合法性校验、示例脱敏（`/home/xxx/demo.py`）、新第三方组件走 license/漏洞检查；④可测试性——覆盖正常导入、空数据、缺失字段、大文件、错误格式、筛选/缩放/拖拽/搜索/复制等交互。

---

## 【关键机制与数据】

### 数据流（原文 §3.2，6 步）

```
用户采集 Snapshot 或 msMemScope 数据
  → 用户在 MindStudio Insight 中导入数据文件
    → 后端解析数据并建立查询所需的数据结构或数据库连接
      → 前端按页面交互发起查询请求
        → 后端返回图表、表格、详情或筛选结果
          → 前端展示内存生命周期、调用栈、内存池状态和明细数据
```

### PyTorch Snapshot 采集侧 API（原文 §4.2）

```python
torch_npu.npu.memory._record_memory_history(stacks='python')
# 运行模型代码
torch_npu.npu.memory._dump_snapshot("model_memory_snapshot.pickle")
```

### 典型场景举例（原文 §2.1）

在强化学习、大模型训练与推理中，不同阶段（如 `generate_sequence`、`actor_update` 等）可能出现不同的内存峰值或碎片特征，开发者据此定位 OOM、内存碎片、内存峰值与低效显存使用问题。

### 安全与敏感信息原则（原文 §2.3.3）

- 示例路径必须脱敏（原文示例：`/home/xxx/demo.py`）。
- 不放置真实用户名、局点信息、密钥、口令或公网地址。
- 导入文件路径、类型、大小需做合法性校验。
- 日志异常信息需避免打印敏感路径和完整调用栈。

---

## 【表格解读】

### 表 1：改版记录（原文逐字还原）

| 日期 | 修订版本 | 修订描述 | 作者 | 审核 |
| --- | --- | --- | --- | --- |
| 2026-01-15 | v1.0 | 初稿 | 刘鹏程 | 廖宴 |
| 2026-06-11 | v1.1 | 清理模板占位，补充可验证的 Device 内存分析范围、数据来源、安全与验证说明 | - | - |

**解读**：v1.1（2026-06-11）相对 v1.0 的核心增量是"清理模板占位 + 补充可验证性"——即把过去无法在仓库源码/用户指南/发布说明中验证的内部 schema、算法细节、性能指标等占位内容剔除，转而只描述可被外部资料佐证的范围、数据来源、安全与验证方法。v1.1 未指定作者/审核人（用 `-` 占位）。

---

### 表 2：缩略语清单（原文逐字还原）

| 缩略语 | 英文全名 | 中文解释 |
| --- | --- | --- |
| msInsight | MindStudio Insight | MindStudio Insight 性能分析工具 |
| Snapshot | PyTorch Memory Snapshot | PyTorch 内存快照数据 |
| msMemScope | MindStudio Memory Scope | Device 内存采集与分析工具 |
| OOM | Out Of Memory | 内存不足 |

**解读**：四组术语分别对应本文的三个主体工具（msInsight 自身、PyTorch 侧 Snapshot 数据源、MindStudio 自研 msMemScope 数据源）和一类问题域（OOM）。值得注意的是，"Snapshot"特指 **PyTorch Memory Snapshot**，与 msMemScope 是并列关系，二者都属于"Device 侧内存分析"的两条采集路径。

---

### 表 3：特性需求列表（原文 §1.2，逐字还原）

| 需求编号 | 需求名称 | 特性描述 | 可验证资料 |
| --- | --- | --- | --- |
| 1 | 支持 PyTorch Snapshot 内存分析 | 支持 snapshot 中内存生命周期展示、内存池状态分析和内存事件详情展示 | `docs/zh/user_guide/memory_tuning.md` |
| 2 | 支持 MindStudio Memory Scope 内存分析 | 支持 msMemScope 数据导入后的调用栈、内存块生命周期、内存分类拆解等功能 | `docs/zh/user_guide/memory_tuning.md` |

**解读**：本文明确划定了 2 条顶层需求，且每条都标注了唯一可验证资料 `docs/zh/user_guide/memory_tuning.md`——表明本设计文档不重复用户指南内容，而是把"用户视角的操作细节"全部下沉到该指南，本设计只覆盖"开发视角"。Snapshot 聚焦"生命周期/内存池/事件详情"三类视图；msMemScope 则多了"调用栈"和"分类拆解"两类视图。

---

### 表 4：数据来源（原文 §3.1，逐字还原）

| 数据源 | 数据格式 | 主要展示内容 | 说明 |
| --- | --- | --- | --- |
| PyTorch Snapshot | `pickle` | 内存块生命周期、内存池状态、内存事件详情 | 由 `torch_npu.npu.memory._dump_snapshot()` 导出 |
| msMemScope | `memscope_dump_{timestamp}.db` | 调用栈火焰图、内存块生命周期图、内存详情拆解图、内存详情表 | 由 msMemScope 工具采集生成 |

**解读**：① 数据格式上，Snapshot 用 Python 原生 `pickle`，msMemScope 用 SQLite 类 `.db` 文件，**两条路径完全异构**，意味着后端需要两套解析器（原文 §8 已明确"待确认"两条解析器路径与数据库结构）。② 展示内容差异：Snapshot 无调用栈视图（仅有内存层信息），msMemScope 无内存池状态图，但多了调用栈火焰图与 CANN/PTA 层级拆解图——这是两条路径在功能上的互补关系。

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

文档自身在 §3.3 与 §4.3 / §5.3 / §1.2 中显式声明了与其他文档/模块的关系：

| 关联对象 | 关系类型 | 出处 |
| --- | --- | --- |
| `support_snapshot_analysis.md` | Snapshot 详细设计（同仓其他 design 文档） | §3.3 |
| `docs/zh/user_guide/memory_tuning.md` | 用户侧采集与使用流程（用户指南）；字段含义与用户操作权威定义（"PyTorch Snapshot 数据内存详情（内存快照）"章节与"MemScope 数据内存详情"章节） | §3.3、§4.3、§5.3、§1.2 全部指向同一份 |
| `Memory.md` | 普通 Memory 模块（非 Device 侧）开发说明 | §3.3 |
| 安装指南 / 发布说明 / 构建脚本 | 实际硬件支持矩阵与环境要求的权威来源 | §2.3.1、§2.3.2 |
| 性能测试结果 | 性能指标（响应时间、错误码、告警格式）的权威来源（本文不作承诺） | §6.1、§8 |

**结构定位**：本文处在 "design 文档层"，向下不暴露数据库 schema/算法细节（§1.1 明确剔除），向上把所有"用户视角字段定义"全部委托给 `memory_tuning.md`。Snapshot 与 msMemScope 两条线在 design 层是并列的，而 msMemScope 的"内存详情拆解图"按 CANN / PTA 等层级展示，暗示其与 CANN 算子层 / PyTorch Adapter 层有间接关联，但本文未给出具体代码路径。

---

## 【使用方法】

**1. 启用 PyTorch Snapshot 内存分析（原文 §2.2 + §4.2）**

```python
# 步骤 1：运行模型前启用历史记录（启用 Python 调用栈采集）
torch_npu.npu.memory._record_memory_history(stacks='python')

# 步骤 2：运行需要分析的训练/推理代码

# 步骤 3：导出 pickle 文件
torch_npu.npu.memory._dump_snapshot("model_memory_snapshot.pickle")

# 步骤 4：在 MindStudio Insight 中导入该 pickle 文件
```

**2. 启用 msMemScope 内存分析（原文 §2.2 + §5.2）**

```
步骤 1：使用 msMemScope 工具采集内存结果文件
步骤 2：导入 memscope_dump_{timestamp}.db 格式的结果文件
步骤 3：在 MindStudio Insight 中查看调用栈火焰图、内存块生命周期图、
        内存详情拆解图（CANN / PTA 等层级）和内存详情表
```

**3. 适用硬件范围（原文 §2.3.1）**

支持昇腾 NPU 相关内存分析场景。具体型号以 MindStudio Insight 发布说明与对应数据采集工具说明为准。

**4. 推荐运行环境（原文 §2.3.2）**

- Windows 10+
- Linux：`glibc > 2.30`
- macOS 13.0+
- 运行 MindStudio Insight 的设备内存 > **16GB**（建议）
- 内存数据文件 ≤ **1GB**（建议）

**5. 待补全/未在本文给出的内容**

原文未涉及：完整接口请求/响应字段、错误码与告警格式、性能指标（响应时间）、后端解析器具体代码路径、数据库表结构。均见 §8"待确认事项"，以"源码或性能测试结果"为准。
