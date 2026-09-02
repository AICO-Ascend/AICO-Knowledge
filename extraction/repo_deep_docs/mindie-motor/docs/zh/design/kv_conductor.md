# KV Conductor 设计文档

> 仓 `mindie-motor` · 路径 `docs/zh/design/kv_conductor.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/design/kv_conductor.md

# KV Conductor 设计文档深度解读

## 【定位】

KV Conductor 是昇腾推理集群中面向分布式 KV Cache 的**多级缓存索引与查询聚合层**,通过将 HBM (NPU) / CPU / Disk 三层介质上的 cache 块以统一身份模型 (`WorkerKey`) 注册到 RadixTree + continuation-edge 图结构中,向 Coordinator 提供跨介质前缀匹配能力,以支撑 `kv_cache_affinity` 调度器实现 prefix-cache 亲和调度。

---

## 【技术要点】

1. **三层索引结构**:
   - HBM 使用 `ConcurrentRadixTree` (前缀链 Radix Tree),以 `LocalBlockHash` (XXH3 token-content hash) 为键,根路径直接走查;
   - CPU/Disk 使用 `LowerTierIndexer` (continuation-edge 图),以 `(parent_seq_hash, local_hash) → child_seq_hash` 双键边存储,内存高效 (应对千万级块数量);
   - 每条边 `Single` / `Multi` 双形态存储,共享时自动升级为 `Multi`,查询时要求走查路径上每块由该 Worker 持有。

2. **身份模型 `WorkerKey` 四元组**: `(instance_id, backend_id, dp_rank, medium)`。同一实例同 DP 的 HBM / CPU / Disk 块是三个不同 WorkerKey;查询时按 `(instance_id, dp_rank)` 聚合跨介质命中。`backend_id` 用于事件路由 (Mooncake/Memcache = 节点 IP,YuanRong = DP 端口号)。

3. **匹配语义**: 查询先收集每 DP 各介质绝对覆盖终点,再按优先级 NPU > CPU > Disk 互斥切分为 `npu_blocks` / `cpu_blocks` / `disk_blocks` (同前缀副本只归最高优先级介质)。`matched_tokens = (npu + cpu + disk) × block_size` (未加权真实覆盖)。亲和性评分由 Coordinator 调度器按 `scheduler_config.kv_affinity.w_npu/w_cpu/w_disk` (默认 `1.0/1.0/0.0`) 加权。

4. **续查双路径并行**: 上层介质命中后,下层介质**从上层断点续查**;同时对拥有首边 `(None, H₀)` 的 worker **无条件 root 走查**,与续接链并列,取绝对终点最远者 (如实报告更长副本,旧 `skip_root` 语义已弃用)。

5. **并发与一致性模型**:
   - HBM 查询路径 (`:find_matches_detailed`) 仅持读锁,多查询互不阻塞;
   - 变更路径 (`apply_store`/`apply_remove`) hand-over-hand 写锁,先锁父再锁子;
   - `workers` 使用 `Arc<FxHashSet>` 写时复制 (CoW),`Arc::make_mut` 变更;
   - `WorkerLookup` 反向索引 `SequenceBlockHash → tree node` 提供 O(1) 定位;
   - active Worker 集合收缩到 1 个后改用单 Worker 成员检查,避免集合差集开销;
   - 不是 MVCC 结构,属弱一致性。

6. **维护机制**:
   - HBM `Removed` / `Cleared` 只做精确索引删除,不在事件热路径扫描整棵树;
   - 后台 `sweep_stale_nodes()` 按周期回收无 Worker 且无子节点的空节点;
   - `Cleared` 同时删除清空后的外层 `WorkerLookup` key;
   - Worker 注销走 `remove_worker_all_media` 清除该实例/DP 在所有介质上的索引;
   - 避免删除事件周期性出现全树扫描延迟尖峰,同时保证停 ingest 后孤儿节点仍被回收。

7. **后端适配抽象**: `StoreBackend` 枚举支持 Mooncake / Memcache / YuanRong 三种后端;每种后端对应一种 `MatchMode` (`IpOnly` / `None`,另有 `IpAndDpRank` 保留作扩展)。
   - HBM 事件来自引擎 Worker,**不经过 Pool**;Worker 身份 = `(instance_id, dp_rank)`,后端无关;
   - CPU/Disk 事件来自 Pool Master/Daemon,携带 `backend_id`;
   - `MatchMode::None` (YuanRong) 下事件内 `backend_id` 被忽略,改用订阅者注册时的 `backend_id` (即引擎 `instance_id`),以避免 pool daemon 的 IP:port 产生与 HBM 块不同的实例标识,破坏跨介质聚合。

---

## 【关键机制与数据】

### 工作原理与数据流

**Engine Worker 接入路径**: Engine Worker (vLLM/SGLang) 通过两条通道与 KV Conductor 交互:
1. `register` — 注册端点;
2. `ZMQ / HTTP KV events` — 上报 KV 事件。

**Coordinator 查询路径**: Coordinator 发送 `query`,KV Conductor 返回 `200 OK` 响应。

**查询内部数据流**: 查询进入后,通过 `Indexer` 维护的 `DashMap<(model, tenant) -> Entry>` 路由到对应条目,再分别查询:
- `HBM Tree (RadixTree)` — 做 prefix chain matched block counts (从 root 走);
- `CPU/Disk (LowerTier)` — 做 continuation edges matched block counts (断点续查 + root 走查)。

三层命中在响应中聚合为 `npu_blocks` / `cpu_blocks` / `disk_blocks` + `matched_tokens`。

### HBM RadixTree 结构示例 (原文)

```
root
 |
 +-[H0]-- Block { workers: {W1, W2}, block_hash: seq100 }
 |    |
 |    +-[H1]-- Block { workers: {W1, W2}, block_hash: seq200 }
 |    |    |
 |    |    +-[H2]-- Block { workers: {W1}, block_hash: seq300 }
 |    |
 |    +-[H3]-- Block { workers: {W2}, block_hash: seq400 }
 |
 +-[H4]-- Block { workers: {W3} }
```

### CPU/Disk Continuation-Edge 示例 (原文)

```
TransitionKey: (parent_seq_hash, local_hash) -> child_seq_hash

Example:
  (None,    H0)  --> seq100    <- from root
  (seq100,  H1)  --> seq200    <- continue
  (seq200,  H2)  --> seq300    <- continue
```

### 续查流程示例 (原文)

```
query: [H0, H1, H2, H3, H4]
HBM tree returns: W1 depth=2, last_seq=seq200

Candidate a) breakpoint resume from (seq200, H2):
  edge(seq200, H2) -> seq300  OK
  edge(seq300, H3) -> seq400  OK
  edge(seq400, H4) -> ???     MISSING -> stop
  -> absolute end = 4

Candidate b) root walk (always, if W1 owns edge (None, H0)):
  edge(None, H0) -> ... walk until first missing edge
  -> compare with a); keep farther absolute end

Absolute ends: npu_end=2, cpu_end=<farthest absolute end>
Exclusive: npu_blocks=npu_end, cpu_blocks=max(0, cpu_end-npu_end)
```

### 后端 Pool 拓扑 (原文)

```
                    ┌────────────────┐
                    │  StoreBackend  │  (enum)
                    └────────┬───────┘
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌───────────┐  ┌───────────┐  ┌───────────┐
        │  Mooncake │  │  Memcache │  │  YuanRong │
        │  Central  │  │  Central  │  │   Per-DP  │
        │    Pool   │  │    Pool   │  │   Ports   │
        └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
              ▼              ▼              ▼
        ┌───────────┐  ┌───────────┐  ┌───────────┐
        │   IpOnly  │  │   IpOnly  │  │    None   │
        │  IP->DPs  │  │  IP->DPs  │  │ port = DP │
        └───────────┘  └───────────┘  └───────────┘
```

### 性能/参数相关数字 (原文)

- 默认亲和性权重 `w_npu/w_cpu/w_disk = 1.0/1.0/0.0` (磁盘默认不计分);
- CPU/Disk 块数量级: **可能千万级**;
- 块大小 `block_size` (在 `matched_tokens` 公式中出现,作为统一换算系数);
- 边存储双形态: `Single` / `Multi` (共享时升级);
- 边双键定位: `(parent_seq_hash, tokens_hash)` (commit 29157f9);
- 关键 commit 引用: `29157f9` (双键定位语义)。

---

## 【表格解读】

### 表 1: 模块职责

| 模块 | 文件 | 职责 |
|------|------|------|
| HTTP Server | `server.rs` | Axum 路由,CORS,TraceLayer |
| Worker Registry | `registry.rs` | 注册/注销,事件/查询路由,ZMQ 订阅管理 |
| Indexer | `indexer/mod.rs` | Per-(model, tenant) 索引生命周期、两阶段缓存、三层匹配聚合与维护 |
| HBM Tree | `concurrent_tree.rs` | 并发 Radix Tree,前缀链匹配 |
| CPU/Disk Index | `lower_tier.rs` | Continuation-edge 图,断点续查 + root 走查 |
| Hashing | `hashing.rs` | XXH3 token → LocalBlockHash |
| Backend | `backend.rs` | 多后端适配(Mooncake/Memcache/YuanRong) |
| ZMQ | `zmq_subscriber.rs` | ZMQ SUB 事件接入 |
| Events | `events/` | vLLM/Pool 事件解析与规范化 |
| Protocols | `protocols.rs` | API 类型定义,wire format |
| Error | `error.rs` | `KvConductorError` 错误类型 |

**逐行解读**:
- **HTTP Server** (`server.rs`): 采用 Rust 生态的 Axum 框架提供 HTTP 入口,内置 CORS 跨域支持与 `TraceLayer` 链路追踪;
- **Worker Registry** (`registry.rs`): 中心注册中心,负责 Worker 的 register/deregister 生命周期、事件分发路由以及查询请求路由,同时管理 ZMQ 订阅关系;
- **Indexer** (`indexer/mod.rs`): 顶层调度,以 `(model, tenant)` 为键做 per-租户索引隔离,管理两阶段缓存 (likely hot/cold tier),聚合三层匹配结果并维护索引一致性;
- **HBM Tree** (`concurrent_tree.rs`): 实现 `ConcurrentRadixTree` 并发数据结构,负责 HBM 上块的前缀链匹配;
- **CPU/Disk Index** (`lower_tier.rs`): 实现 `LowerTierIndexer`,以 continuation-edge 图替代完整 RadixTree,以应对 CPU/Disk 千万级块的内存压力;
- **Hashing** (`hashing.rs`): 将 token 序列经 XXH3 算法生成 `LocalBlockHash`,作为 RadixTree 的键;
- **Backend** (`backend.rs`): 适配层,封装 Mooncake / Memcache / YuanRong 三种后端的差异;
- **ZMQ** (`zmq_subscriber.rs`): ZeroMQ SUB 模式的事件订阅接入点,接收引擎与 Pool 的 KV 事件流;
- **Events** (`events/`): 解析和规范化来自 vLLM 和 Pool 的异构事件格式,统一为内部事件类型;
- **Protocols** (`protocols.rs`): 定义对外 API 的 wire format 类型,负责序列化/反序列化;
- **Error** (`error.rs`): 定义 `KvConductorError` 统一错误类型,覆盖注册、查询、解析、后端通信等错误场景。

### 表 2: MatchMode 策略

| Backend | MatchMode | Pool `backend_id` | 事件如何关联 Worker |
|---------|-----------|-------------------|-------------------|
| Mooncake | `IpOnly` | 节点 IP(如 `10.0.0.1`) | `hbm_ip_index[IP]` → 该节点所有 DP |
| Memcache | `IpOnly` | 节点 IP | 同 Mooncake |
| YuanRong | `None` | 端口号(如 `15558`) | ZMQ 订阅端口 → 唯一 DP |

**逐行解读**:
- **Mooncake / IpOnly**: CPU/Disk 事件中 `backend_id` 为节点 IP。Worker 关联通过内存中的 `hbm_ip_index` 反向索引把 IP 展开为该节点上所有 DP WorkerKey,即"一个 IP 对应多个 DP"的多对多关系;
- **Memcache / IpOnly**: 同 Mooncake 语义,因为二者都使用 Central Pool 拓扑;
- **YuanRong / None**: YuanRong 采用 Per-DP 独立端口,`backend_id` 即端口号 (示例 `15558`),与 ZMQ 订阅端口一一对应,**直接绑定到唯一 DP**;此模式下事件内 `backend_id` 被忽略,改用订阅者注册时的 `backend_id` (即引擎 `instance_id`),避免 IP:port 形式的 pool daemon 标识破坏与 HBM 块的实例一致性。枚举另有 `IpAndDpRank` 模式 (按 IP + DP 精确匹配),当前后端未选用,保留作扩展。

---

## 【公式解读】

### 公式 1: matched_tokens (未加权真实覆盖)

$$matched\_tokens = (npu + cpu + disk) \times block\_size$$

**符号含义**:
- `npu`: NPU (HBM) 介质上的有效块数 (经过互斥切分后的 `npu_blocks`);
- `cpu`: CPU 介质上的有效块数 (`cpu_blocks`,等于 `max(0, cpu_end - npu_end)`,即扣除已被 NPU 覆盖后的延伸部分);
- `disk`: DISK 介质上的有效块数 (`disk_blocks`,扣除已被 NPU+CPU 覆盖后的延伸部分);
- `block_size`: 单个 KV cache 块的 token 数(块大小常量)。

**作用**: 报告**未加权**的绝对覆盖 token 数,即"同一前缀的副本再长也不重复计分",如实反映可复用 token 总量;此值不经亲和性权重,用于调度器侧的真实覆盖度评估。

### 公式 2: Coordinator 亲和性评分

$$\text{affinity} = \text{round}\left(\left(npu \times w_{npu} + cpu \times w_{cpu} + disk \times w_{disk}\right) \times block\_size\right)$$

**符号含义**:
- `npu` / `cpu` / `disk`: 同公式 1 中的互斥切分块数;
- `w_npu` / `w_cpu` / `w_disk`: 介质亲和性权重,默认 `1.0 / 1.0 / 0.0`,由 `scheduler_config.kv_affinity` 配置;
- `block_size`: 同公式 1;
- `round()`: 四舍五入取整(输出整数 token 数)。

**作用**: Coordinator 调度器按各介质命中数加权求和,得到最终的 `kv_cache_affinity` 评分;`w_disk = 0.0` 默认值意味着 Disk 命中仅计入真实覆盖但不参与亲和性调度评分,体现"Disk 复用代价高、不作为优先调度依据"的设计取舍。Coordinator 调度器负责完成此加权,KV Conductor 仅提供原始块数。

### 公式 3: WorkerKey 身份模型

$$WorkerKey = (instance\_id, backend\_id, dp\_rank, medium)$$

**符号含义**:
- `instance_id`: 推理引擎实例标识(跨介质聚合键);
- `backend_id`: 块的来源后端标识,引擎实例或 pool daemon(Mooncake/Memcache = 节点 IP,YuanRong = DP 端口号);
- `dp_rank`: Data Parallel 副本序号,用于同一实例内的 DP 区分;
- `medium`: 存储介质枚举(HBM / CPU / Disk),区分同一实例同 DP 的不同介质副本。

**作用**: 四元组精确定位一个缓存持有者。同一 `(instance_id, dp_rank)` 下 HBM / CPU / Disk 是**三个**不同 WorkerKey;查询响应中将该三元 (去掉 medium 后) 相同的三个 WorkerKey 命中**聚合**到同一个 DP 条目,实现跨介质命中聚合。

### 公式 4: 互斥切分

$$npu\_blocks = npu\_end$$
$$cpu\_blocks = \max(0,\ cpu\_end - npu\_end)$$
$$disk\_blocks = \max(0,\ disk\_end - npu\_end - cpu\_blocks)$$

**符号含义**:
- `npu_end`: NPU 介质绝对覆盖终点(块序号);
- `cpu_end`: CPU 介质绝对覆盖终点(取断点续查与 root 走查的更远者);
- `disk_end`: Disk 介质绝对覆盖终点(同上)。

**作用**: 按 NPU > CPU > Disk 优先级做**互斥**切分,确保同一前缀副本只归到最高优先级介质,避免重复计数(同前缀的 NPU 命中优先于 CPU 命中优先于 Disk 命中)。

---

## 【关联】

### 模块内上下游关系

- **HTTP Server** ← Coordinator: 接收 query 请求,返回 200 OK;
- **HTTP Server** → **Worker Registry**: Worker 通过 HTTP 注册端点接入;
- **Worker Registry** ← **ZMQ Subscriber** ← **Events** ← Engine Worker / Pool Daemon: 事件通过 ZMQ SUB 进入后经 Events 解析规范化;
- **Worker Registry** → **Indexer**: 事件路由到对应 `(model, tenant)` 索引;
- **Indexer** → **HBM Tree (ConcurrentRadixTree)**: HBM 块索引与查询;
- **Indexer** → **CPU/Disk Index (LowerTierIndexer)**: CPU/Disk 块索引与查询;
- **Indexer** → **Hashing**: token 序列经 XXH3 哈希为 `LocalBlockHash` 后才能在 Tree/Edge 中定位;
- **Indexer** → **Backend**: 通过 `Backend` 适配层识别 Mooncake/Memcache/YuanRong 不同 `MatchMode`,决定 `backend_id` → Worker 关联路径;
- **Indexer** → **Protocols**: wire format 序列化(查询响应 `npu_blocks` / `cpu_blocks` / `disk_blocks` + `matched_tokens`);
- **Indexer** → **Error**: 错误经 `KvConductorError` 统一封装后返回。

### 与调度系统上下游

- **上游 (Producer)**: Engine Worker (vLLM/SGLang) 的 HBM 事件 + Pool Master/Daemon 的 CPU/Disk 事件;
- **下游 (Consumer)**: Coordinator 调度器,消费查询响应,通过 `kv_cache_affinity` 加权 (默认 `w_npu=1.0, w_cpu=1.0, w_disk=0.0`) 完成调度决策;
- **配置耦合点**: `scheduler_config.kv_affinity.w_npu/w_cpu/w_disk` — Coordinator 侧配置但语义上描述 KV Conductor 的输出,因此 KV Conductor 设计需要明确报告"未加权"块数,由 Coordinator 自行加权。

### 跨后端依赖

- **Mooncake / Memcache**: 同 `IpOnly` 语义,共享 `hbm_ip_index` 反向索引路径;
- **YuanRong**: 独立 `None` 模式,端口号即 DP 标识,不走 `hbm_ip_index`,经 ZMQ 订阅端口直接映射到唯一 DP。

### 维护与回收路径

- `Removed` / `Cleared` 事件 → 精确索引删除 → 不扫描整树;
- 后台 `sweep_stale_nodes()` → 统一回收空节点;
- `remove_worker_all_media` → Worker 注销时跨介质清除该实例/DP 在所有介质上的索引。

### 文档内部关联 (原文涉及的子机制)

- 「多级存储介质设计」— 描述三层介质关系;
- 「HBM 索引:ConcurrentRadixTree」— 详述 RadixTree 并发与一致性;
- 「CPU/Disk 索引:LowerTierIndexer」— 详述 continuation-edge 图;
- 「后端适配抽象」— 详述 Mooncake/Memcache/YuanRong 适配差异;
- 「匹配逻辑与查询流程」— 文中预告的章节(原文末尾 cut off,但提及"旧 `skip_root` 语义已弃用"在此节展开)。

> 注: 原文末尾被截断于 "Mooncake/Memcache registration: HBM: medi...",「匹配逻辑与查询流程」节及「注册流程差异」节后续内容**原文未提供**,本文不做臆测。

---

## 【使用方法】

### 启用方式

- **Worker 接入**: Engine Worker (vLLM/SGLang) 启动后通过 HTTP `register` 调用向 KV Conductor 注册;
- **事件上报**: 注册后通过 ZMQ SUB 或 HTTP 上报 KV events (HBM 事件不经过 Pool,CPU/Disk 事件来自 Pool Master/Daemon);
- **Coordinator 查询**: Coordinator 通过 HTTP `query` 调用发起前缀匹配查询,KV Conductor 返回 200 OK 含 `npu/cpu/disk_blocks` + `matched_tokens`。

### 配置项

| 配置项 | 默认值 | 作用 |
|--------|--------|------|
| `scheduler_config.kv_affinity.w_npu` | `1.0` | NPU 命中亲和性权重 |
| `scheduler_config.kv_affinity.w_cpu` | `1.0` | CPU 命中亲和性权重 |
| `scheduler_config.kv_affinity.w_disk` | `0.0` | DISK 命中亲和性权重(默认不计分) |
| 后端选择 (`StoreBackend`) | Mooncake / Memcache / YuanRong | 决定 `MatchMode` 与 `backend_id` 语义 |
| `MatchMode` | `IpOnly` (Mooncake/Memcache) / `None` (YuanRong) / `IpAndDpRank` (保留扩展) | 决定事件 `backend_id` → Worker 关联路径 |

### 命令/调用

- `find_matches_detailed` — HBM RadixTree 查询入口(仅读锁);
- `apply_store` / `apply_remove` — RadixTree 变更入口(hand-over-hand 写锁);
- `remove_worker` — 单介质 Worker 移除,清空该节点 `children` map 回收内存;
- `remove_worker_all_media` — Worker 注销时跨介质清除;
- `sweep_stale_nodes()` — 后台周期调用,回收无 Worker 且无子节点的空节点;
- ZMQ SUB 端口注册 — YuanRong 模式下每个 DP 独立端口(如 `15558`),直接绑定唯一 DP。

### 使用约束 (原文隐含)

- `LocalBlockHash` 是**独立** XXH3 内容哈希(不含前缀信息),前缀链由 RadixTree 显式编码;
- 查询要求走查路径上**每个 block 都由该 Worker 持有**(与 HBM 树 "Worker 集合逐层求交" 语义一致);
- `MatchMode::None` 下事件内 `backend_id` 被忽略,必须使用订阅者注册时的 `backend_id` (即 `instance_id`),否则破坏跨介质聚合;
- 旧 `skip_root` 语义已弃用,新实现**无条件**对拥有首边的 worker 做 root 走查(并与断点续查并列取最远)。

> 注: 原文被截断于「注册流程差异」节内的 Mooncake/Memcache 注册流程,后续 YuanRong 注册差异、完整命令清单、配置文件示例、版本要求等**原文未涉及**,本文不做臆测。
