# 综述

> 仓 `parakv` · 路径 `docs/zh/design/segment.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/parakv/docs/zh/design/segment.md

# ParaKV Segment 文档深度解读

---

## 【定位】

本文档系统阐述 ParaKV 如何将持久化数据按 **segment 数据块**（典型大小 256MB）组织与管理的完整设计，覆盖存储布局、KV 增删改、compaction 流程，以及基于"热/冷数据分离"的高级优化策略，是理解 ParaKV 磁盘层数据生命周期的核心参考。

---

## 【技术要点】

1. **Segment 粒度划分**：将文件或裸磁盘（块设备）切分为固定大小的 segment 数据块（典型 256MB），作为数据回收与版本管理的基本单位。

2. **Segment 两区结构**：每个 segment 由 **bitmap 区**（标记 slot 空闲/占用，0=空闲或已删，1=被占用）与 **slot 数据区**（存放 key+value，key 做冗余以支持恢复与校验）组成；偏移可通过固定参数计算，无需额外索引结构。

3. **Append-only + 批量写入**：ParaKV 不支持原地修改，仅支持 append-only 操作；要求 **batch 写入**（对齐 SSD 页单位，避免读-改-写放大）与 **顺序约束**——先写 slot 数据 → 改 bitmap → 最后更新内存索引。

4. **删除轻量化**：删除只需改内存索引与 bitmap，**不擦除 slot 数据**，原值原地遗留，由 compaction 回收。

5. **Segment 三态机与 Compaction**：状态为 IDLE / APPENDING / FULL；当 FULL 段中已删除 slot 数量超过指定阈值（如 75%）时触发 compaction——申请空闲 segment、迁移有效数据、重置 bitmap、回置 IDLE。

6. **热/冷数据分层优化**：基于"20% 的 Key 贡献 80% 访问"的二八分布，将热 segment 整体缓存到内存（约 10% 系统内存，上限 20%），结合 LFU + Segment 聚合热度（如平均 > 1000 次/分钟）+ 滑动窗口/指数衰减，按 30 秒周期在 SPDK 用户态内存池中实现热段升降级与崩溃恢复。

---

## 【关键机制与数据】

### 数据组织与计算定位
- bitmap 区负责 slot 级空间管理；slot 数据区中每个 slot 由 key + value 组成，**key 做了冗余处理**（便于数据恢复与校验）。
- 数据在 segment 内的偏移可基于上述固定信息推算（原文给出 layout 示意图 `figures/segment_layout.jpg`）。

### 业务场景的固定大小假设
- **Key**：参数服务器场景为 `uint64_t` 无符号长整数；LLM KVCache 场景为 Prefix Cache Block 的散列值，固定 **64 或 128 字节**（取决于 Hash 算法）。
- **Value**：固定大小，取决于模型参数维度与数据类型大小，或 KVCache 块的维度与数据类型大小。
- 该固定性是 segment 能按偏移直接寻址的根基。

### KV 添加流程（原文约束）
- 顺序：先写数据到指定 segment 数据区 → 修改该 segment 的 bitmap 区标记 slot 占用 → 最后更新内存索引。
- 强调 batch 写入是为了对齐 SSD 页单位（读整页→修改→整页写），以**减少 IO 操作、提升性能**。

### KV 删除流程
- 顺序：先删除内存索引 → 再修改 bitmap 区。
- 不擦除 slot 物理数据，依赖 compaction 回收。

### Compaction 触发条件
- 当 segment 处于 FULL 状态且**已删除 slot ID 数量超过指定阈值，如 75%** 时可触发 compaction。
- 流程：申请空闲 segment → 整理待 compaction 数据到新 segment + 修改内存索引 → 完成后将 bitmap 初始化为 0 + segment 置 IDLE。

### Segment 元数据持久化
- 每个 segment 的 bitmap、空闲 segment 列表、当前活动 segment 等元数据同样需要持久化，以确保崩溃后可正确恢复磁盘布局，避免数据错乱或空间泄漏；具体实现可参考**索引 WAL 预写日志部分**（原文未展开具体实现，标注跨模块关联）。

### 热/冷分层优化机制
- **热度识别**：不可依赖人工配置，需自动识别。推荐：
  - 基于内存索引的访问计数（需高效 LFU 统计，PS 场景可离线提供数据文件）；
  - 按 Segment 聚合热度（所有有效 Key 的访问计数求和或平均）；
  - 阈值触发——如 **平均每分钟访问次数 > 1000** 标记为"热 Segment"；
  - 用滑动窗口（如过去 5 分钟访问计数）或指数衰减避免抖动。
- **存储方式**：ParaKV 用 SPDK 裸磁盘架构，**只能使用显式缓存**（mmap 与 SPDK 冲突）。做法：分配固定大小内存池（如 10% 系统内存）→ SPDK 异步读入 Segment 全部 Slot → 维护 *segment_id → 内存指针* 映射 → 热 Segment 的 Slot 读写直接走内存，不经 SPDK。
- **写入流程**：更新内存中 Slot 数据 → 追加写 WAL（**必须记录完整 Slot 数据**，因为热 Segment 在内存中可能已覆盖旧值）→ 异步刷盘（周期如每 1 秒）。
- **崩溃恢复**：加载快照后重放 WAL，将热 Segment 重新加载到内存。
- **升降级触发**：后台线程周期扫描（如 **每 30 秒**）Segment 热度。
- **Compaction 调整**：热 Segment 豁免，只对冷 Segment 执行空间回收；热降冷后若无效 Slot 比例高，可立即加入 Compaction 队列。
- **内存控制**：上限约为总内存 20%；达上限时禁止新冷 Segment 升级并触发 LRU 淘汰；预留 DMA 缓冲区（`spdk_dma_malloc`）保证零拷贝。
- **一致性**：Key 唯一则同一 Slot 同时只有一个写者，无需额外锁；**刷盘周期可配 100ms~1s**，PS 场景允许少量丢失（可上游重算）。

### 核心收益（原文列出）
- 读加速：热 Segment 常驻内存，读操作完全不走磁盘。
- 写加速：热 Segment 更新直接写内存 + WAL，后台异步刷盘，降低写延迟。
- 减少 Compaction 开销：热 Segment 不参与（或频率极低），避免数据频繁迁移导致写放大。
- 提升 SSD 寿命：减少对热数据的随机写与重写，降低 NAND 磨损。

---

## 【表格解读】

### 表 1：Segment 数据块状态表

| 状态 | 说明 |
|:----|:------|
| IDLE | 空闲 |
| APPENDING | 使用中，但有 slot 空闲，可以用来追加新数据 |
| FULL | 使用中，但无 slot 空闲，处于只读状态 |

**逐行解读：**
- **IDLE**：segment 未被任何 segment manager 持有或刚完成 compaction（bitmap 已被初始化为 0），可被分配为承载新写入的工作段或作为 compaction 目标段；
- **APPENDING**：当前活跃段，仍有可用 slot，新 KV 可继续 append 写入；该状态下写入不触发 compaction；
- **FULL**：所有 slot 已被占用（含有效与"已删除但未回收"两种），segment 进入只读，**新写入需另寻 APPENDING 段**，且当无效 slot 比例超过阈值（如 75%）时可触发 compaction 以回收空间。

### 表 2：热 Segment 存储与内存映射方式对比

| 方式 | 优点 | 缺点 | 适用场景 |
|:------|:-------|:------|:------|
| 显式缓存（用户态内存池）| 完全控制内存布局；支持零拷贝 RDMA；与 SPDK 无缝集成 | 需要额外管理内存 | 裸磁盘方案 |
| mmap | 编程简单，OS 自动管理页缓存 | 无法绕过内核；与 SPDK 冲突（SPDK 使用用户态驱动，mmap 不可用）| 传统文件块 |

**逐行解读：**
- **显式缓存（用户态内存池）**：ParaKV 在裸磁盘 + SPDK 架构下唯一可选路径——可直接管理内存布局、与 RDMA 零拷贝、与 SPDK 用户态驱动无缝衔接；代价是需要自行处理内存分配、淘汰与同步；
- **mmap**：依赖内核页缓存，编程简单但需经内核路径；在 SPDK 用户态驱动架构中 **不可用**，因此传统文件块方案才能用，不适用于 ParaKV 当前路线。

---

## 【公式解读】

原文无公式。

> 说明：原文仅给出 segment 数据组织的**示意图**（`figures/segment_layout.jpg`），未提供定位 slot 偏移的显式数学公式，但段落中暗示偏移可"基于上述固定信息计算"——即由 bitmap 大小 + slot 编号 × (key 冗余大小 + value 大小) 等固定参数推导得来，原文未给出具体闭式表达。

---

## 【关联】

- **WAL 预写日志（索引部分）**：原文明确指出"Segment 的元数据持久化实现可参考索引 WAL 预写日志部分"，属于文档内部跨模块引用，但**文末未提供具体链接地址**（原文标注内部链接无）。意味着 segment 元数据的变更（包括 bitmap、空闲列表、活动段切换）应当复用同一套 WAL 通道以保证崩溃一致性。

- **内存索引层**：
  - KV 添加的顺序约束中"最后更新内存索引"——segment 的 slot 物理位置与内存索引条目存在映射关系；
  - 热数据识别依赖"内存索引中的访问计数"（LFU 统计）；
  - 冷→热升级流程中"内存索引中的地址保持不变（仍指向磁盘 LBA）"——表明 segment 设计支持灵活的"地址"语义切换（指向内存或磁盘）。

- **SPDK 用户态驱动栈**：热 Segment 的存储/写入/内存控制（`spdk_dma_malloc`、异步读取、零拷贝）均依赖 SPDK 提供能力，是 segment 优化方案的物理基础。

- **Compaction 子系统**：热 Segment 豁免策略需要 Compaction 线程感知"热段集合"，并与升降级模块协调（如热降冷后加入 Compaction 队列）。

- **上游业务场景（参数服务器 / LLM KVCache）**：Key 与 Value 的固定大小假设直接来源于这两种业务形态，segment 的偏移可计算性正是基于此假设。

---

## 【使用方法】

原文未涉及具体的启用命令、配置文件项或 API 调用方式。

> 原文仅给出**设计层指引**，包括：
> - 可调节的硬编码参数：segment 大小典型值（256MB）、compaction 触发阈值（如 75%）、热段识别阈值（每分钟 > 1000 次）、热段滑动窗口（5 分钟）、扫描周期（30 秒）、热段缓存内存占比（约 10%，上限 20%）、刷盘周期（100ms~1s）；
> - 跨模块引用：WAL 预写日志部分（用于 segment 元数据持久化）；
> - 兼容性约束：裸磁盘方案下必须用显式用户态内存池，不能用 mmap。

具体的配置文件路径、配置项名称、启用开关或 CLI 命令需参考 ParaKV 项目其他文档（如配置说明或 API 参考），本文档未给出。

## 图文联合解读

- `segment_layout.jpg`: **图文联合解读：**

1）图示：Segment 由左侧 bitmap 区（位图）和右侧 kv 区组成；kv 区按 slot 顺序排列，每个 slot 含 key 与 value（Slot 0=k0+v0, Slot 1=k1+v1），key 做冗余存储。

2）技术结论：slot 偏移可由公式 `slot_offset = bitmap_size + slot_size × slot_id` 直接算出（slot_size = key_size + value_size），无需额外索引即可 O(1) 定位数据，且因 Key/Value 固定大小，存储可预测、回收可批量。

3）与文档关系：呼应"固定大小 Key/Value 场景"，支撑 append-only 写入、bitmap 标记占用以及 compaction（按 slot_id 整体搬迁）的设计，实现高效空间管理与快速恢复。
