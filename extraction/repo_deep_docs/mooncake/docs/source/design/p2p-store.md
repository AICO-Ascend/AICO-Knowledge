# P2P Store

> 仓 `mooncake` · 路径 `docs/source/design/p2p-store.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mooncake/docs/source/design/p2p-store.md

# P2P Store 设计文档深度解读

## 【定位】
P2P Store 是构建在 Transfer Engine 之上的客户端分布式对象共享机制，专为训练节点向大量推理节点分发大体积检查点等场景设计，通过无中心化的 etcd 元数据 + 对等节点互为数据源的 BitTorrent 风格传输，解决单点出口带宽饱和问题。

---

## 【技术要点】

1. **架构定位**：基于 Transfer Engine 构建的**纯客户端架构（client-only architecture）**，无中心化 master 节点，全局元数据由 etcd 元数据服务维护，目标是节点间**临时**共享对象。
2. **两大核心接口的语义**：
   - `Register` 等价于 BitTorrent 中的 seeding（做种），**仅向 etcd 注册元数据，不发生任何数据传输**。
   - `GetReplica` 通过元数据搜索，从已调用 `Register` 或 `Get` 的其他机器拉取数据；拉取到本地后，本节点自动成为后续其他节点的数据源（peer-to-peer 链式扩散）。
3. **生命周期对偶**：`Register` ↔ `Unregister`，`GetReplica` ↔ `DeleteReplica`，调用前者后内存区域不可修改/解映射，直到调用对应解除接口。
4. **内存型传输**：数据用 `(addrList, sizeList)` 二元数组描述本地内存区，文件内容按数组顺序逻辑对应；分片粒度由 `maxShardSize` 控制，**推荐值为 64MB**。
5. **当前传输协议限制**：示例程序与示例流程中明确指出 **"currently it only supports the RDMA protocol"**。
6. **Golang API 唯一性约束**：注册名（`name`）必须集群内唯一；`localSegmentName`（hostname/IP:port）也必须集群内唯一；**同一个 `P2PStore` 实例对同一个文件只能 `GetReplica` 一次**。

---

## 【关键机制与数据】

### 数据流与工作机制

1. **元数据平面与数据平面分离**
   - 元数据平面：etcd（地址形如 `10.0.0.1:2379`，即 etcd 默认端口 2379）。`Register` 仅写元数据；`GetReplica` 先查元数据，再发起数据传输。
   - 数据平面：基于 Transfer Engine + RDMA 协议进行节点间内存直传。

2. **BitTorrent 风格链式分发**
   - 原文："A `GetReplica` searches metadata and clones data from other machines that have called Register or Get (unless explicitly calling `Unregister` or `DeleteReplica` to stop pulling files from the local machine), and it can also act as a data source to improve the efficiency of data transfer for other nodes."
   - 含义：拉取完成的节点自动成为新数据源（除非显式调用 `Unregister`/`DeleteReplica` 撤销），形成 P2P 树状扩散，**避免训练节点出口带宽饱和**（"avoid the outbound bandwidth saturation"）。
   - 调用方**不需要知道数据源 IP**：`List`/`GetReplica` 由 P2P Store 自动搜索；但仍要求"other nodes can access this machine using the local machine's hostname or the `--local_server_name` filled in during the creation of the node"——即可达性以 hostname 或 `--local_server_name` 为锚点。

3. **示例工作流（trainer → inferencer）**
   - trainer（`--cmd=trainer`）创建模拟模型文件并对外发布；
   - inferencer（`--cmd=inferencer`）自动从 trainer 或其他已拉取完成的 inferencer 节点拉取；
   - 结束标志：终端打印 "ALL DONE"。

4. **分片粒度**：`maxShardSize` 控制内部数据分片粒度，原文推荐 64MB；`PayloadInfo` 中的 `MaxShardSize`/`TotalSize`/`SizeList` 均由 `Register` 入参派生而来，便于接收端按相同结构拼回。

> 备注：原文中未给出实测带宽、延迟、并发上限等性能数据，因此本节不含性能数字。

---

## 【表格解读】

**原文无表格**（文档中所有参数以代码注释/参数说明形式呈现，未使用 markdown 表格）。

为方便参考，下面将 `Register` 接口的入参逐项还原（仅复述原文，未发明新字段）：

| 参数名 | 原文类型/含义 | 是否必填 | 关键约束（原文） |
|---|---|---|---|
| `ctx` | Golang Context 引用 | 是 | 上下文传递 |
| `name` | 文件注册名 | 是 | 集群内唯一 |
| `addrList` | `[]uintptr`，每段内存起始地址 | 是 | 与 `sizeList` 按数组顺序一一对应，文件内容按此顺序逻辑拼接 |
| `sizeList` | `[]uint64`，每段内存长度 | 是 | 与 `addrList` 一一对应 |
| `maxShardSize` | `uint64`，内部数据分片粒度 | 是 | 推荐值 **64MB** |
| `location` | 该内存段对应的设备名 | 是 | — |

`PayloadInfo` 结构（原文逐字）：

| 字段 | 类型 | 原文含义 |
|---|---|---|
| `Name` | `string` | Full name of the Checkpoint file |
| `MaxShardSize` | `uint64` | The `maxShardSize` passed into `Register` |
| `TotalSize` | `uint64` | The total length of the `sizeList` passed into `Register` |
| `SizeList` | `[]uint64` | The `sizeList` passed into `Register` |

---

## 【公式解读】

**原文无公式**（文档未给出任何 LaTeX 或伪代码形式的数学表达式）。

---

## 【关联】

1. **上游/底座依赖**：[Transfer Engine](transfer-engine.md)
   - 原文开篇即声明 "P2P Store is built on Transfer Engine"；
   - 体现在代码上：`NewP2PStore` 内部会启动一个 Transfer Engine 服务（原文："internally starts a Transfer Engine service"）；
   - 传输协议方面当前随 Transfer Engine 受限于 RDMA（"currently it only supports the RDMA protocol"）。
   - 详细传输机制、缓冲区管理、RDMA 拓扑等需参阅 `docs/source/design/transfer-engine.md`。

2. **与元数据服务（etcd）的关系**：
   - P2P Store 自身不持久化元数据，所有 `Register`/`GetReplica`/`List` 的发现都依赖外部 etcd；
   - 配置锚点：`--metadata_server=<etcd addr:port>`（示例为 `10.0.0.1:2379`），与 Transfer Engine Bench 共享同一 etcd 启动方式（原文："This is consistent with the method described in Transfer Engine Bench"）。

3. **与上层业务的关系**：
   - 文档明确"P2P Store is now used in Moonshot AI's checkpoint transfer service"，是其在大模型检查点分发场景的生产承载。

4. **示例程序定位**：`p2p-store-example` 是位于 `build/mooncake-p2p-store/` 下的演示程序，与 Moonshot 训练→推理迁移流程同构，可作为最小可跑通参考实现。

---

## 【使用方法】

### 1. 编译（原文有）

```bash
# 需参考通用编译指南，并打开 P2P Store 开关
cmake .. -DWITH_P2P_STORE=ON && make -j
```
产物路径：`build/mooncake-p2p-store/p2p-store-example`。

### 2. 启动 etcd 元数据服务

原文："Start the `etcd` service. This is consistent with the method described in Transfer Engine Bench."（具体命令需参见 Transfer Engine Bench 文档，**原文未给出 etcd 启动命令**）。

### 3. 启动训练节点（模拟数据源）

```bash
export MC_GID_INDEX=n   # n 为整数
./p2p-store-example --cmd=trainer \
                    --metadata_server=10.0.0.1:2379 \
                    --local_server_name=10.0.0.2:12345
```

### 4. 启动推理节点（拉取端，可启多个）

```bash
export MC_GID_INDEX=n
./p2p-store-example --cmd=inferencer \
                    --metadata_server=10.0.0.1:2379 \
                    --local_server_name=10.0.0.3:12346
```
结束标志：终端打印 `ALL DONE`。要求其他节点可通过本机 hostname 或 `--local_server_name` 访问本机。

### 5. Golang API 使用流程（按原文接口顺序）

1. **创建实例**：`NewP2PStore(metadataUri, localSegmentName)` —— 内部启动 Transfer Engine。
   - `metadataUri`：etcd 的 hostname 或 IP（示例 `10.0.0.1:2379`）；
   - `localSegmentName`：本机唯一标识，形如 `host:port`（示例 `10.0.0.2:12345`）。
2. **数据源侧**：
   - `Register(ctx, name, addrList, sizeList, maxShardSize, location)` —— 元数据写入等。在调用 `Unregister` 前对应内存区不可改/解映射。
   - `Unregister(ctx, name)` —— 解注册，之后可安全修改/删除该文件占用的内存区。
3. **拉取侧**：
   - `List(ctx, namePrefix)`（`namePrefix` 空字符串表示枚举全部）→ 获取 `[]PayloadInfo`。
   - `GetReplica(ctx, name, addrList, sizeList)` —— 将文件副本拉取到指定内存区；拉取后自动充当后续节点的数据源。在调用 `DeleteReplica` 前对应内存区不可改/解映射。同一 `P2PStore` 实例对同一 `name` 只能 `GetReplica` 一次。
   - `DeleteReplica(ctx, name)` —— 停止对外提供该文件副本，之后可安全修改/删除对应内存区。
4. **关闭**：`Close()`。

### 6. 关键配置项汇总（仅原文出现项）

| 配置项 | 出现位置 | 原文取值/约束 |
|---|---|---|
| `MC_GID_INDEX` | 示例程序环境变量 | 整数 `n`（用于 RDMA GID 索引选择） |
| `--metadata_server` | 示例程序命令行 | `10.0.0.1:2379`（etcd 默认端口） |
| `--local_server_name` | 示例程序命令行 | `host:port`，集群内唯一 |
| `--cmd` | 示例程序命令行 | `trainer` / `inferencer` |
| `maxShardSize`（API 入参） | `Register` | **推荐 64MB** |
| 协议支持 | 全文 | **当前仅支持 RDMA** |
