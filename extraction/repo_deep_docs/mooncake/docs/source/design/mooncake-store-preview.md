# Mooncake Store Preview

> 仓 `mooncake` · 路径 `docs/source/design/mooncake-store-preview.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mooncake/docs/source/design/mooncake-store-preview.md

# Mooncake Store Preview 深度解读

## 【定位】

本文档系统性描述 **Mooncake Store** —— 一个为 LLM 推理场景量身定制的高性能分布式 KV 缓存存储引擎，阐述其能力边界、组件架构、客户端 API 与部署模式，对外提供面向 LLM 推理的低层对象存储与缓存管理能力。

---

## 【技术要点】

- **精确定位**：明确定义 Mooncake Store 为「distributed KV cache」而非通用缓存系统；与传统 Redis/Memcached 的关键差异在于「key 不由 value 哈希派生」，因此 value 在插入后是可变的（但单条 K-V 整体仍可能被淘汰）。
- **对象级 API**：仅提供三种核心操作 —— `Put`、`Get`、`Remove`，保持接口精简。
- **多副本机制**：同一对象的多个副本可缓解热点。每个对象内部的各 slice 一定落在**不同的 segment** 上；不同对象的 slice 可以共享 segment；副本放置是 **best-effort** 的，存储空间不足时按尽可能多的副本写入。
- **强一致性 + 零拷贝传输**：由底层 Transfer Engine 提供 RDMA 多网卡聚合带宽，使数据能以线速在节点间流动，CPU 开销极低；通过对大对象做 striping / 并行 I/O 充分利用多 NIC 聚合带宽。
- **双角色 Client**：同一个 `Client` 类身兼两职——**客户端**（发起 Put/Get 请求）和**存储服务端**（把本机一段连续内存注册为 segment 提供给其他 Client 读取）；数据传输发生在 Client ↔ Client 之间，**绕过 Master**。
  - `global_segment_size = 0` → 纯客户端（不发存储）。
  - `local_buffer_size = 0` → 纯服务端（不接收请求）。
- **两种部署模式**：
  - **Default mode**：单 master，存在单点故障风险。
  - **High availability mode（标注 unstable）**：多 master + etcd 集群协调，leader 选举接管，定期 heartbeat 监控 client 健康。
- **容错底线**：「任意数量的 master 与 client 节点失效都不会读到错误数据」，只要至少保留 **1 个 master + 1 个 client** 即能继续提供服务（fail-stop 模型，非脑裂容忍）。
- **多级存储**：支持将缓存数据从 RAM offload 到 SSD，平衡成本与性能。
- **Get TTL 副作用**：当前实现中，Get 首次命中某 key 后，对应 entry 会在一定时间（**默认 1 秒**）后自动删除。
- **动态扩缩容**：支持运行时增删节点，无需停服。

---

## 【关键机制与数据】

### 工作原理 / 数据流

**架构层面（原文）：** Mooncake Store 由两类组件构成：
1. **Master Service**：独立进程，对外暴露 RPC；管理整集群逻辑存储空间池、节点 join/leave、对象空间分配与元数据；其内存分配与淘汰策略针对 LLM 推理负载优化。**注意**：Transfer Engine 所需的 `metadata service`（etcd / Redis / HTTP 等）**不属于** Master Service 范畴，需独立部署。
2. **Client**：唯一客户端类，承担双重角色（client + store server）；既可作为**嵌入式共享库**与 LLM 推理进程（如 vLLM 实例）同进程运行，也可作为**独立进程（standalone）**运行。

**Get 数据流（原文）：** 上层应用调用 Client → 通过 Transfer Engine 从对端 Client 的 segment 把数据搬运到本地**预先注册**的 DRAM/VRAM 内存区域（`registerLocalMemory(addr, len)`）——该本地内存**不是** Master 管理的 Logical Memory Pool，而是用户自管的临时接收缓冲。开启持久化时，内存层 miss 会回退到 SSD 查找并加载。

**Put 数据流（原文）：** 上层应用通过 `Put(key, slices, config)` 提交写入；按 `ReplicateConfig` 申请若干副本；Master 负责为各 slice 挑选 placement（保证 slice 间跨 segment），数据实际从源 Client 直接发往目标 segment 所在 Client，**不经 Master 中转**。开启持久化时，Put 在写入内存池后**异步**触发 SSD 持久化。

### 性能相关数据（原文）

- Get TTL 默认值：**1 秒**（原文: `1s by default`）。
- `ReplicateConfig.replica_num` 默认值：**1**（原文: `replica_num{1}`）。
- Transfer Engine 协议：**RDMA**、**TCP**（原文明确列出）。
- 高可用 leader 监控机制：原文仅提到「periodic heartbeats」，未给出具体频率等数值。

> 原文未提供吞吐量、延迟、benchmark 等具体性能数字，亦未给出 SSD/RAM 容量比例或多层存储的具体策略参数。

---

## 【表格解读】

**原文无表格。**

> 说明：原文中仅包含 `ReplicateConfig` 的 C++ 结构体片段（且该片段在原文末尾被截断），结构体属于代码定义而非表格范畴。已逐字保留其可见部分如下：

```C++
struct ReplicateConfig {
    size_t replica_num{1};                    // Total number of replicas for the object
    bool with_soft_pin{false};               // Whether to enable soft pin mecha
```

——该结构体在原文中尚未展示完毕（文档在末尾被截断），后续字段（如 soft pin 的具体语义、是否还有 `preffered_segment` 等）**原文未给出**，不在此臆造。

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

- **Transfer Engine（./transfer-engine.md）**：Mooncake Store 的数据传输完全依赖 Transfer Engine 实现零拷贝、多 NIC RDMA 聚合带宽与 striping 并行 I/O。两者关系是「上层存储语义 + 下层传输能力」的纵向分层。原文明确强调：
  - Transfer Engine 自身的 **metadata service（etcd / Redis / HTTP 等）需独立部署**，不属于 Master Service；
  - `metadata_connstring`、`protocol`、`protocol_args` 等参数都是 Init 时透传给 Transfer Engine 的；
  - 文档结尾的内部链接 `./transfer-engine.md` 也直接指向该模块。
- **上层 LLM 推理框架（如 vLLM）**：通过**嵌入式模式**把 Client 以共享库形式加载到推理进程内部，复用推理侧已注册的 GPU/DRAM 内存做 Get 接收区。
- **持久化层（SSD）**：在 Put/Get 路径上以异步旁路方式介入，与内存层并行存在，是「Multi-layer storage」能力在数据流上的具体落点。
- **部署侧的 etcd 集群**：仅在高可用模式下被 Master Service 用于 leader 选举，与 Transfer Engine 的 metadata service 是**两个用途不同的 etcd 实例**（原文措辞未强制复用，但实际部署可能合并）。

---

## 【使用方法】

### 启用 / 初始化（原文）

通过 `Client::Init` 启动一个客户端实例，原型与参数含义如下（原文逐字）：

```C++
ErrorCode Init(const std::string& local_hostname,
               const std::string& metadata_connstring,
               const std::string& protocol,
               void** protocol_args,
               const std::string& master_server_entry);
```

| 参数 | 含义（原文） |
| --- | --- |
| `local_hostname` | 本机 `IP:Port`，或可访问的域名（端口缺省时使用默认值） |
| `metadata_connstring` | Transfer Engine 所需 metadata 服务地址（etcd / Redis 等） |
| `protocol` | Transfer Engine 支持的协议（原文列举 **RDMA** 与 **TCP**） |
| `protocol_args` | 对应协议所需参数 |
| `master_server_entry` | Master 地址信息；default 模式为 `IP:Port`，HA 模式为 `etcd://IP:Port;IP:Port;...;IP:Port` |

### 角色切换（原文）

- 想让本实例**只做客户端**（不贡献存储）：将 `global_segment_size` 设为 **0**。
- 想让本实例**只做存储服务端**（不允许处理 Get/Put 请求）：将 `local_buffer_size` 设为 **0**。

### 部署模式选择（原文）

- **Default mode**：master 服务为单节点，部署简单但存在 SPOF。
- **High availability mode（unstable）**：多 master 节点 + etcd 集群选举 leader；leader 通过 heartbeat 监控 client 健康；client 节点恢复后可自动重新加入集群。

### 读写 API（原文）

```C++
tl::expected<void, ErrorCode> Get(const std::string& object_key, 
                                  std::vector<Slice>& slices);
tl::expected<void, ErrorCode> Put(const ObjectKey& key,
                                  std::vector<Slice>& slices,
                                  const ReplicateConfig& config);
```

- `Get`：读取结果由 Transfer Engine 写入用户通过 `registerLocalMemory(addr, len)` 预先注册的本地内存；保证数据完整正确；首次命中后默认 **1 秒** 自动失效。
- `Put`：通过 `ReplicateConfig.replica_num` 指定副本数；副本放置 best-effort；开启持久化时会**异步**落 SSD。

### 客户端接入模式（原文）

- **Embedded mode**：以共享库形式导入到 LLM 推理进程（如 vLLM 实例）。
- **Standalone mode**：作为独立进程运行。

> **未涉及部分**：原文未给出 `make` / CMake / pip 等具体安装命令、未提供 docker compose / k8s manifest 等部署样例、未提供 `Client` 析构/资源回收的具体 API（如 `Unmount`、`Close`）、未提供端到端 example code；Get/Put 之外的 `Remove` 接口原文仅在 features 列表中以一句带过，未给出 API 签名或示例。

## 图文联合解读

- `mooncake-store-preview.png`: **图示内容**：左侧 Master Service（独立进程）通过紫色"控制面"连接 4 个 Mooncake Store 实例；每个 Prefill/Decode vLLM 引擎与本地 Mooncake Store 共进程，通过 put(k,t)/get(k) 交互；底部绿色"逻辑内存池"由黑箭头标注"Transfer Engine 零拷贝传输"互联。

**技术结论**：体现"控制面与数据面分离"——元数据由 Master 集中管理，数据通过共享内存池在节点间零拷贝流转；vLLM 与 Store 同进程避免 RPC 序列化开销，跨节点经 Transfer Engine 直传。

**与文档呼应**：直接佐证"零拷贝"、"对象级 Put/Get"、"强一致性（Master 保障）"及"为 LLM 推理加速"的核心论点，同时体现 Prefill-Decode 分离架构下 KV Cache 的高效复用路径。
- `mooncake-store-simple-get.png`: **图示解读：**

1) **结构与数据流**：时序图展示Client、Master Service、Server三方交互。Client先向Master发起`getObjectInfo(bucket_id)`元数据查询；Master返回`ObjectMapping`；Client自循环选取合适replica并分配本地buffer；最后Client经`TransferEngine Read`直接与Server传输数据，Master不参与数据通路。

2) **技术结论**：数据路径采用零拷贝直连架构——元数据集中寻址（Master），数据平面旁路（Client↔Server直连TransferEngine），避免经Master转发造成的带宽瓶颈与延迟。

3) **与文档关系**：印证文档论断——印证"Multi-replica support"（选replica步骤）和"Zero-copy"特性，体现KV缓存面向LLM推理的高性能设计。
- `mooncake-store-simple-put.png`: 1) **图示内容**：Put 操作时序图。Client 向 Master Service 发 PutStartRequest(key, slices, config)；Master 按 ReplicateConfig 选 Server1/Server2（自环）、标 Object 为 Processing、回写 buffer 元数据；Client 经 TransferEngine（虚线）绕过 Master 直连两 Server 完成零拷贝数据写入；再发 PutEndRequest，Master 标 Object 为 Ready for Read，回 RPC finish。

2) **技术结论**：控制面（Master Service 调度+元数据）与数据面（TransferEngine 直写）解耦；多副本由 ReplicateConfig 驱动放置；Processing→Ready 两阶段状态机保障写后一致性。

3) **文档呼应**：分别印证文档所述"对象级 Put API、多副本支持、零拷贝、强一致性"四大核心特性。
