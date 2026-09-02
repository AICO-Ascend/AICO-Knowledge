# Mooncake Architecture

> 仓 `mooncake` · 路径 `doc/zh/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mooncake/doc/zh/architecture.md

# Mooncake Architecture 文档深度解读

---

## 【定位】

**一句话定位**：本文档描述 Mooncake 存储子系统的架构设计，阐述其如何通过 DRAM/SSD 多级缓存池与 (GPUDirect) RDMA 零拷贝传输，提升 LLM 等场景在慢速对象存储环境下的推理效率。

---

## 【技术要点】

核心机制分条：

1. **多级缓存池架构**：在高速互联的 DRAM/SSD 资源上构建多级缓存池，对象（Object）最终按特定规则写入 Managed Pool Buffer 节点所分配的存储空间，覆盖 VRAM/DRAM/NVMe SSD 等多种介质。

2. **(GPUDirect) RDMA 零拷贝传输**：利用 RDMA 技术，实现发起端 DRAM/VRAM 到接收端 DRAM/VRAM 的直接传输，无需数据拷贝；同时聚合单机多网卡资源提升带宽。

3. **对象级接口与原子性保证**：对外提供 Object 级别的 Get/Put/List/Del 操作，以及 Replicate 操作；保证对象写操作的原子性——Get 一定能读到某次 Put 生成的完整数据，但**不保证读到最新版本**。

4. **条带化与并行 I/O**：对较大对象执行条带化（striping）拆分，并通过并行 I/O 传输以利用多网卡聚合带宽。

5. **三级下刷模式（Eager/Lazy/None）**：对慢速对象存储提供三种持久化强度，对应持久化要求从**高到低**的对象分级。

6. **轻量化的多副本策略**：缓存层多副本保存，提供 slice 级别的分布保证和尽力而为（best-effort）的分配策略；因不保证绝对高可用，系统设计更轻量。

7. **动态弹性**：支持运行时动态增删缓存资源；Master 节点集中管理 Object 到 VRAM/DRAM/NVM 缓冲区的映射关系与空间策略。

> 注：Mooncake 当前**仅开源下层的 Transfer Engine 子系统**，"后续更新敬请期待"，因此文档所述完整系统架构尚未全部对外开放。

---

## 【关键机制与数据】

### 工作原理与数据流

**原文：Master 节点集中管理对象（Object）到 VRAM/DRAM/NVM 缓冲区（Buffer）的映射关系及空间管理策略。同时，Master 节点通过调用 Transfer Engine 的相关接口，驱动 Managed Pool Buffer 节点实现数据传输。**

由此可还原数据流路径：

```
用户请求 → Master 节点（解析 Object → Buffer 映射）
       → Transfer Engine（封装 RDMA/零拷贝/多网卡聚合）
       → Managed Pool Buffer 节点（实际数据落地点：VRAM/DRAM/NVMe SSD）
```

### 设计取舍与一致性语义

**原文：保证对象写操作的原子性，即 Get 一定会读到某次 Put 生成的完整的数据，但不一定是最新的。**

这是一条**有界一致性**语义（bounded consistency）：保证读到完整的快照，但不保证线性化的最新性——为换得系统轻量化（无强可用性保证）而做出的取舍。

### 性能与持久化三档

| 下刷模式 | 持久化强度 | 目标场景（按原文对应关系） |
|---|---|---|
| Eager | 高（最高） | 持久化要求最高的对象 |
| Lazy | 中 | 持久化要求居中的对象 |
| None | 低 | 持久化要求最低的对象 |

> 原文用"对应持久化要求从高到低的对象"明确三档覆盖区间；具体量化指标（如延迟/吞吐数字）文档中未给出。

### 子系统开源状态

**原文：Mooncake 目前开源了位于下层的 Transfer Engine 子系统，后续更新敬请期待！**

注意：架构顶层（Master + Managed Pool Buffer 等管理逻辑）的开源状态文档中未说明，按字面"目前"二字推断为**当下未开源**。

---

## 【表格解读】

**原文无表格**（文档正文仅含一段 Markdown 渲染的架构示意图 `mooncake-store.png`，并不包含形式化表格）。

如需将上文"三档下刷模式"以表格形式呈现便于查阅，可参考下表（**仅依据原文措辞整理**，非原文自带的表格）：

| 模式 | 持久化要求 | 原文对应描述 |
|---|---|---|
| Eager | 高 | "对应持久化要求最高的" |
| Lazy | 中 | "对应持久化要求从高到低"的中间档 |
| None | 低 | "对应持久化要求从高到低"的最低档 |

---

## 【公式解读】

**原文无公式**（文档未出现任何 LaTeX 数学表达式或伪代码形式的公式）。

---

## 【关联】

**上游调用方与典型场景**：
- 文档在首段就将应用场景定位为"大型语言模型（LLM）等场景下的推理效率"，并强调"慢速对象存储环境"——即作为慢速后端存储与 LLM 推理请求之间的**加速层**。
- 对照文档开头"Mooncake 是 Kimi 所用的 serving platform"的项目背景，该架构即为 Kimi 推理服务的存储子系统底座。

**子系统层级关系**：
1. **Transfer Engine**——位于**下层**，已被开源，承担"数据传输 + 零拷贝 + 多网卡池化"的实际 I/O 能力。
2. **Master 节点**——上层管理面，持有 Object → Buffer 的元数据映射与空间策略，对 Transfer Engine 的接口进行**驱动调用**。
3. **Managed Pool Buffer 节点**——存储空间的实际承载者（VRAM/DRAM/NVMe SSD），由 Master 驱动并接收/发送对象数据。

**横向特性耦合点**：
- "支持对较大的对象进行条带化和并行 I/O" 与 "聚合单机多网卡资源" 二者在 Transfer Engine 层耦合——条带是分片策略，多网卡聚合是传输策略，二者协同才能真正达到"大对象高吞吐"。
- "动态增删缓存资源" 与 "Master 集中管理映射" 耦合——弹性能力的实现依赖 Master 维护一致的元数据视图。

**目前开源边界**：文档给出的内部链接标注为"(无)"，仅文末提示 Transfer Engine 子系统已开源，**其余模块（Master/Managed Pool Buffer 完整逻辑）的代码与接口的内部链接未提供**。

---

## 【使用方法】

**原文未涉及**具体的启用方式、配置项或命令行指令。文档为架构概述性质，描述的是设计目标、能力范围、子系统角色与开源状态，**未给出**：

- 部署所需的配置项（如副本数、缓存层级比例）；
- 客户端调用示例（如 Get/Put 的 API 用法）；
- Transfer Engine 子系统的安装/编译命令（虽然提到已开源，但具体步骤本文档未列出）；
- 三种下刷模式（Eager/Lazy/None）的切换配置方法；
- 多网卡或 GPUDirect RDMA 的环境要求与启用步骤。

若需上述信息，需参考 Transfer Engine 子系统单独的文档或代码仓库（本文档未提供相应链接）。

## 图文联合解读

- `mooncake-store.png`: **图文联合解读：**

图含 Master、N 个推理服务器（每机有 Store Client+Transfer Engine+含 VRAM/DRAM Paged KVCache 与 Managed Pool Buffer 的 RAM 段，构成 Mem Cache Pool），下方 NVMeof/RPC 段为 Other Cache Pool，连至 Object Store/PFS。控制面：Master↔Store Client 走 Get/Put/List/Del/Replicate，并对 Transfer Engine 发 BatchTransfer Read/Write/Flush；数据面：服务器间 Managed Pool Buffer 经 RDMA 双向零拷贝互通，按 Eager/Lazy/None 模式下刷或回灌慢存。

论证了"控制/数据面解耦、内存池化、跨节点零拷贝聚合带宽"的核心架构设计，与文档关于 Transfer Engine 子系统、Master 集中管理映射并驱动 Managed Pool 传输、多级缓存池及下刷模式的论点一一对应。
