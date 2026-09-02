# 综述

> 仓 `parakv` · 路径 `docs/zh/design/index.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/parakv/docs/zh/design/index.md

# ParaKV 设计文档深度解读

## 【定位】

本文档是 ParaKV 高性能 KV 存储引擎的综述性设计文档，系统阐述了存储引擎在**内存型与内存+SSD 混合存储介质**下的整体架构思路，核心聚焦两件事：**内存索引（key/value 分离的 HashMap）**的结构定义，以及 **WAL（Write-Ahead Log）索引日志**如何保证崩溃后可恢复地重建出持久化索引。文档给出了 flag 位编码、记录格式、块大小、快照触发阈值等具体参数，是后续模块（Segment、Compaction、SPDK 接入）共同依赖的索引层设计契约。

---

## 【技术要点】

1. **存储介质双模设计**：引擎需同时支持纯内存型与"内存 + SSD"混合型两种介质，以应对不同存储规模。
2. **内存索引结构（key/value 分离）**：索引条目只存 key 与数据偏移（offset），开放定制法 HashMap；key 为 uint64_t 占 8 字节；value 为 flag + location 复合字段。
3. **Flag 三态编码（原文定义）**：000 = 文件块偏移（兼容 PS 实现）；001 = 裸磁盘架构下的 segment_id + slot_id 编码；002 = 内存地址（热数据缓存）。
4. **地址空间位数约束**：48bit 地址空间约 256TB；20bit 无符号整数范围 0 ~ 1,048,575；28bit 无符号整数范围 0 ~ 268,435,455。
5. **WAL 记录格式（uint64_t key）**：Magic(1) + Type(1) + Key(8) + DiskAddr(8) + OldDiskAddr(8) + Checksum(4) = **30 字节**，可填充至 **32 字节**对齐；若 key 为 uint128_t，总长变为 **38 字节**，填充至 **64 字节**。
6. **块大小与校验**：日志块大小 **4KB**（对齐 NVMe 块），块尾预留 4 字节块校验和（可选）；每条记录带 CRC32 校验。
7. **快照触发策略**：周期触发（**每 10 分钟**）或 WAL 大小超过阈值（**1GB**）时触发；快照后截断 WAL，保留活跃区与旧区构成的循环缓冲区。
8. **写缓冲区优化**：设置约 **128KB** 写缓冲区积累刷盘，配合 SPDK 批量提交接口 `spdk_nvme_ns_cmd_writev` 减少小 I/O。
9. **WAL 与数据分离**：WAL 存于独立 NVMe 命名空间或专用文件，避免与 Segment 数据争抢 IO 带宽。
10. **Compaction-WAL 联动**：Compaction 修改的索引更新（Update 类型，携带 OldDiskAddr）也需写 WAL；旧 Segment 回收无需记录 WAL。

---

## 【关键机制与数据】

### 工作原理

**写路径（原文：先写日志，后更新内存索引）**
1. 构造 WAL 记录（Type + Key + DiskAddr + OldDiskAddr + CRC32）；
2. 维护当前块写入偏移（Block ID + 块内偏移），块满则填充零后追加新块；
3. 通过 SPDK 异步写入（`spdk_nvme_ns_cmd_write` 完成回调）→ 同步等待持久化完成 → 用 CAS 等原子操作更新内存哈希表 → 推进日志位置元数据。

**读/恢复路径**
- 加载最新快照 → 重建内存哈希表 → 从快照记录的日志位置 `snapshot_lba` 起顺序读 WAL 块 → 校验通过后按类型（Insert/Update/Delete）应用到哈希表 → 将当前 WAL 写入位置置为最后一条记录之后。

**并发控制**
- **索引更新锁**：细粒度（Key 互不冲突）；**日志写入锁**：仅保护日志分配与写入，不阻塞索引更新；高并发可设计多日志流并按 Key 哈希分区。

**Compaction 交互**
- Compaction 线程在更新索引前先写 Update 类型 WAL 记录（携带新旧地址），可批量写以降低日志开销；旧 Segment 被标记可回收时无需记录 WAL，因为索引已更新。

### 性能数据（原文明确给出的数值）

| 项目 | 数值 | 来源 |
|---|---|---|
| Key 字节长度（uint64_t） | 8 字节 | 原文 |
| WAL 记录长度（uint64_t key） | 30 字节（可填充至 32） | 原文 |
| WAL 记录长度（uint128_t key） | 38 字节（可填充至 64） | 原文 |
| WAL 块大小 | 4KB（对齐 NVMe 块） | 原文 |
| 块尾校验和 | 4 字节（可选） | 原文 |
| 写缓冲区 | 128KB | 原文 |
| 快照周期触发 | 每 10 分钟 | 原文 |
| WAL 大小触发阈值 | 1GB | 原文 |
| 地址空间 | 48bit ≈ 256TB；20bit 范围 0~1,048,575；28bit 范围 0~268,435,455 | 原文 |

---

## 【表格解读】

### 表 1：Flag 标记位定义

| flag 标记位 | 说明 |
|:------|:-------|
| 000 | 文件块偏移，兼容当前 PS 实现 |
| 001 | 裸磁盘架构，对应的是 segment_id 和 slot_id 编码 |
| 002 | 内存地址（热数据缓存） |

**逐行解读**：
- **000（文件块偏移）**：兼容既有 PS（Parameter Server）实现路径，flag 段解码后 location 即为传统文件内的块偏移，适用于文件存储介质。
- **001（裸磁盘架构）**：用于 SPDK 直接管理的裸盘场景，location 字段按 segment_id（段标识）+ slot_id（槽位标识）编码，支持 NVMe 高性能直访。
- **002（内存地址）**：用于热数据缓存层，location 即为可直接寻址的内存指针，结合 48bit ≈ 256TB 的虚拟地址空间可覆盖极大热数据集。

### 表 2：WAL 文件/Section 单条记录字段

| 字段 | 长度 (字节) | 说明 |
|:--------|:----------|:----------------|
| Magic | 1 | 固定魔数，用于校验记录完整性 |
| Type | 1 | 操作类型：0x01=Insert, 0x02=Update, 0x03=Delete |
| Key | 8 | Key 值（uint64_t） |
| DiskAddr | 8 | 磁盘地址（LBA 或 Segment+Slot 编码），对于 Delete 操作可为 0 |
| OldDiskAddr | 8 | 仅 Update 操作有效，表示更新前的磁盘地址；Insert/Delete 为 0 |
| Checksum | 4 | 对前面字段的 CRC32 校验和 |

**逐行解读**：
- **Magic (1B)**：固定魔数用于完整性边界识别，能在恢复扫描时快速定位有效记录起点。
- **Type (1B)**：以三态编码区分 Insert / Update / Delete，Update 携带 OldDiskAddr 是为幂等恢复与回滚审计服务。
- **Key (8B)**：默认 uint64_t 键值，匹配内存索引条目大小，便于 8 字节对齐访问。
- **DiskAddr (8B)**：8 字节可容纳 LBA（48bit ≈ 256TB）+ 槽位偏移的复合编码；Delete 时该字段无效写 0。
- **OldDiskAddr (8B)**：仅 Update 有效，承载迁移前地址，用于恢复时区分"重复 Update"与冲突写入；Insert/Delete 写 0。
- **Checksum (4B)**：对前述 26 字节做 CRC32，定位部分写入（torn write）；配合块尾 4 字节块校验和形成双重防线，校验失败时按"日志截断"语义丢弃后续记录。

---

## 【公式解读】

**原文公式 1（记录长度计算）**：

$$\text{总长度} = 1 + 1 + 8 + 8 + 8 + 4 = 30 \text{ 字节}$$

- 符号含义：`1`(Magic) + `1`(Type) + `8`(Key) + `8`(DiskAddr) + `8`(OldDiskAddr) + `4`(Checksum)。
- 作用：推导 uint64_t key 场景下单条 WAL 记录的固定长度基线，并据此填充至 32 字节对齐以适配常见缓存行/块写入边界。

**原文公式 2（uint128_t key 扩展）**：

$$\text{总长度}_{\text{uint128}} = 30 + 8 = 38 \text{ 字节（填充到 64 字节）}$$

- 符号含义：在公式 1 基础上 Key 字段由 8 字节扩展为 16 字节（新增 8 字节）。
- 作用：保持记录结构向后兼容的同时支持 128 位键，按 64 字节填充到典型 NVMe 控制器最优写入粒度。

**原文公式 3（地址空间范围）**：

$$48 \text{bit 地址空间} \approx 256 \text{TB}$$

$$20 \text{bit} \in [0,\ 1{,}048{,}575]$$

$$28 \text{bit} \in [0,\ 268{,}435{,}455]$$

- 符号含义：分别对应"全量 LBA 空间"、"slot 索引上限"、"segment 索引上限"三种位宽容量。
- 作用：界定裸磁盘架构下 segment_id / slot_id / LBA 三段位宽的最大承载量，确保编码方案在工程上不会溢出。

> 原文无其他数学公式。

---

## 【关联】

文档虽无文末内部链接，但正文反复交叉引用以下模块/特性，构成完整的引擎依赖图：

1. **Append-Only Segment（数据层）**：WAL **不记录 Value**，Value 由 Append-Only Segment 负责持久化；WAL 与 Segment **存储分离**（独立 NVMe 命名空间或文件），避免 IO 带宽争抢。
2. **内存索引 Dump 能力**：作为"WAL + 快照"的离线镜像旁路，要求索引具备**快速从 dump 文件加载**的能力。
3. **Compaction 模块**：Compaction 触发的 Key 迁移必须以 Update 类型写入 WAL 并携带 OldDiskAddr，旧 Segment 回收无需写 WAL；Compaction 可**批量写 WAL**以摊销日志开销。
4. **SPDK 栈**：WAL 写入依赖 `spdk_nvme_ns_cmd_write`（同步/异步）与 `spdk_nvme_ns_cmd_writev`（批量）；裸磁盘区域由 SPDK 直接管理；WAL 文件/Section 也可降级到普通文件（若使用文件系统）。
5. **快照子系统**：作为 WAL 的"压缩锚点"——快照完成后才能截断 WAL；快照恢复时通过 `snapshot_lba` 锚定增量起点。
6. **PS（Parameter Server）兼容层**：flag=000 即为兼容当前 PS 实现的文件块偏移编码，体现引擎对存量协议/格式的向后兼容策略。

---

## 【使用方法】

原文未涉及完整的启用步骤、配置文件或运维命令，仅以**设计契约**形式给出以下可执行/可配置线索：

- **写入接口（原文提及的 API）**：`spdk_nvme_ns_cmd_write`（单条写入）、`spdk_nvme_ns_cmd_writev`（批量写入）。
- **可调参数（原文明确数值）**：写缓冲区大小 **128KB**、WAL 块大小 **4KB**、快照周期 **10 分钟**、WAL 阈值 **1GB**、记录对齐粒度 **32 / 64 字节**、块尾校验和 **4 字节（可选）**。
- **介质选择**：裸磁盘（SPDK 直管 NVMe 命名空间） / 普通文件系统 文件，二选一。
- **并发模型选择**：单线程全局序列化 或 按 Key 哈希分区的多日志流（高并发场景）。
- **快照一致性策略**：暂停写入 或 Copy-on-Write（生成快照时保证一致性）。

> 关于完整的部署/启动命令、配置文件 schema、监控指标等，原文未涉及；需结合仓库其他设计文档（如 Segment、Compaction、SPDK 接入）补齐。

## 图文联合解读

- `index.jpg`: **图示内容**：左侧展示hashmap中Key(8字节)与Offset(8字节)交替排列的内存条目布局；右上方标注Offset的64bit位域划分（3bit flag + 13bit reserved + 48bit location）；右下方说明裸磁盘模式下location由20bit segment_id与28bit slot_id编码。

**技术结论**：索引采用key-offset分离结构，offset通过3bit flag区分文件块/裸盘/内存三种存储介质，裸盘场景用段号+槽号紧凑编码地址，单条索引仅16字节，空间与寻址效率兼顾。

**文档关系**：直接可视化"内存索引"章节中key与偏移分离的设计，并具体呈现flag-location字段定义表，论证了存储引擎对内存与SSD混合介质的统一寻址能力。
- `wal-section.jpg`: **图文解读：**

1）图示：横向排列的多个等大小矩形块，每块标注"Log Block (4KB)"，末尾"…"表示可无限追加。

2）技术结论：WAL采用4KB固定块大小的Append-Only顺序写入布局，块满即追加新块，结构规整、易于顺序扫描与快速定位。

3）文档呼应：直观印证"WAL追加写、预分配空间"的设计，与文中"每块含若干记录+尾部校验和""块写满时追加"的描述一致，为"先写日志后更新索引"的崩溃恢复机制提供物理存储基础。
