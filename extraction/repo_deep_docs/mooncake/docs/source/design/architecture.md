# Mooncake Architecture

> 仓 `mooncake` · 路径 `docs/source/design/architecture.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mooncake/docs/source/design/architecture.md

# Mooncake Architecture 一体化深度解读

---

## 【定位】

这篇文档定义了 **Mooncake 作为 LLM 推理加速基础设施的整体架构形态**——它如何在慢速对象存储 (slow object storage) 的不利前提下, 通过在高速互联的 DRAM/SSD 之上构建多级缓存池, 并借助 (GPUDirect) RDMA 与多网卡资源, 实现对象级存储与零拷贝传输, 从而提升 LLM 推理效率。

---

## 【技术要点】

1. **多级缓存池 (Multi-level caching pool)**: 在"高速互联的 DRAM/SSD 资源"之上构建, 以缓解底层"慢速对象存储环境"对 LLM 推理的制约。
2. **(GPUDirect) RDMA 零拷贝传输**: "利用 (GPUDirect) RDMA technology to transfer data directly from the initiator's DRAM/VRAM to the target's DRAM/VRAM in a zero-copy manner", 即发送端 DRAM/VRAM → 接收端 DRAM/VRAM 直传, 不经额外拷贝。
3. **多网卡带宽聚合 (multi-NIC)**: "maximizing the use of multi-NIC resources on a single machine", 在单台机器内充分利用多张网卡资源, 配合下文 striping/parallel I/O 形成聚合带宽。
4. **对象级存储接口**: 提供 `Get / Put / List / Del` 四类基础对象操作, 另支持 `Replicate` 操作来"dynamically configurating replication strategies" (动态配置副本策略)。
5. **副本与一致性模型 (轻量化设计)**: "supports data replication in the cache layer with slice-level placement guarantees and best-effort allocation, with a lightweight design due to not guaranteeing high availability"; 写操作具有 "atomicity", 即 "a `Get` operation will always read one consistent version, but not necessarily the latest one" (保证读到一致的版本, 但不保证读到最新版本)。
6. **大对象并行传输与分级落盘**: "supports striping and parallel I/O transfer for larger objects to utilize the aggregated bandwidth of multiple network cards"; 同时 "supports multiple modes for flushing slow object storage", 即向慢速对象存储的刷写 (flush) 支持多种模式。
7. **弹性拓扑**: "supports dynamic addition and removal of cache resources", 缓存资源可动态增删。

---

## 【关键机制与数据】

Mooncake 的工作机制可以从 **数据面** 与 **控制面** 两条线索理解:

**控制面 (Master Node)**
- 原文: "The master node centrally manages the mappings of objects to VRAM/DRAM/NVM buffers."
- 作用: 维护 object → buffer (VRAM/DRAM/NVM) 的全局映射, 这是对象级存储能运行的前提。
- 原文: "The master node also drives managed pool buffer nodes to achieve data transfer by calling Transfer Engine's APIs."
- 作用: 数据搬运并非由 buffer 节点自发进行, 而是由 Master 通过调用 Transfer Engine API 来驱动, 这是一种中心化调度的传输模型。

**数据面 (Managed Pool Buffer Nodes + Transfer Engine)**
- 原文: "Managed pool buffer nodes mainly provide DRAM space for storing objects."
- 作用: 池化的 buffer 节点贡献 DRAM 容量作为对象存储介质。
- 原文: "Mooncake supports zero-copy and multi-NIC data transfer over VRAM/DRAM/NVMe SSD. This feature is supported by Transfer Engine, which has been open-sourced."
- 作用: Transfer Engine 是已开源的子系统, 负责跨 VRAM / DRAM / NVMe SSD 的零拷贝、多 NIC 数据传输。
- 原文: "supports striping and parallel I/O transfer for larger objects to utilize the aggregated bandwidth of multiple network cards"
- 作用: 大对象会被切片 (stripe) 并行 I/O, 借此把多块网卡/多设备的带宽聚合成单流的吞吐。

**端到端数据流 (综合原文)**
1. 客户端发起 `Put/Get/List/Del/Replicate` 操作。
2. Master 节点根据自身维护的 object → buffer 映射, 决定对象应落到/取自哪些 VRAM/DRAM/NVM buffer。
3. Master 调用 Transfer Engine 的 API, 驱动 Managed Pool Buffer 节点完成跨节点的零拷贝数据传输 (可走 GPUDirect RDMA, 并使用多 NIC 聚合)。
4. 大对象以 striping + parallel I/O 方式搬运, 充分发挥多网卡聚合带宽。
5. 对于需要持久化或冷数据, 按"多种 flush 模式"刷写到慢速对象存储; 缓存资源可按需动态扩缩。

**关于性能数据**: 原文未提供任何量化性能数字 (如延迟、吞吐、命中率、带宽数值等), 本节不补充臆造数据。

---

## 【表格解读】

**原文无表格**

(原文档中只有一张架构示意图 `figures/mooncake-store.png`, 不存在以参数表/性能对比/配置项形式呈现的表格。)

---

## 【公式解读】

**原文无公式**

(原文档不包含 LaTeX 或伪代码形式的公式。)

---

## 【关联】

文档主要描述了 Mooncake 的 **Store 子系统** 架构, 涉及的内部关系与上下游模块如下:

- **Transfer Engine (已开源)**: 是 Mooncake 的数据搬运子系统, "This feature is supported by Transfer Engine, which has been open-sourced"; "Mooncake has open-sourced the Transfer Engine subsystem, and updates are forthcoming!"。Master 通过调用其 API 驱动 buffer 节点完成传输, 是 Store 架构的关键依赖。
- **Managed Pool Buffer Nodes**: 作为缓存层的物理承载 (主要贡献 DRAM), 与 Master 构成控制/数据分工关系 (Master 管映射并调度, buffer 节点提供空间)。
- **慢速对象存储 (slow object storage)**: 作为 Mooncake 缓存池的下游/后方存储, Mooncake 提供了"多种 flush 模式"与之协同; Mooncake 整个设计的出发点正是 "enhance the inference efficiency ... in slow object storage environments"。
- **LLM 推理 (Kimi serving)**: Mooncake 是 "the serving platform for Kimi" 的组成, 文档中提到的 VRAM、GPUDirect RDMA、striping 等均直接服务于 LLM 推理场景下的 KV cache / 模型权重等大对象存取需求。

注: 用户提供的文档文末注明"内部链接: (无)", 因此不存在可枚举的内部链接列表; 上述关联关系均来自原文中明确提及的组件名称与上下文。

---

## 【使用方法】

原文未涉及。

(原文档为 architecture 设计文档, 只描述系统结构、组件职责与机制, 未给出任何启用方式、配置项或命令行/API 调用样例。如需启用与配置细节, 应参考 Mooncake 仓库中其他文档, 而非本架构说明。)

## 图文联合解读

- `mooncake-store.png`: **图解：**

1）图示左侧为集中式元数据节点"Mooncake Managed Store Master"，通过 `Get/Put/Replicate/List/Del` 与各推理服务器(Inference Server 1…N)的 Store Client 通信，再经 Transfer Engine 发起 `Read/Write/Flush` 的批量传输。每个推理服务器内部 RAM Segment 含 VRAM/DRAM Paged KVCache 与 Managed Pool Buffer，跨服务器缓冲区通过 RDMA 直连；下方"Other Cache Pool"挂载 NVMeof/RPC Segment，并回连至底层 Object Store/PFS。

2）论证了控制面（Master）与数据面（Transfer Engine）解耦、内存级缓存池与异构 SSD/对象存储分层池化、跨节点零拷贝直通的整体拓扑。

3）图示直接对应文档论点：多级缓存池、对象级接口、跨节点复制与多种 Flush 模式、资源可动态增删的架构基础。
