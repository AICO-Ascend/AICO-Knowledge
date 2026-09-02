# 背景

> 仓 `parakv` · 路径 `docs/zh/design/introduction.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/parakv/docs/zh/design/introduction.md

# ParaKV 设计引言文档深度解读

## 【定位】
本文档是 ParaKV（Parallel KV for LLM & Recommendation at Storage Speed）KV 存储引擎的**总纲/引言级设计文档**，系统阐述了在 LLM KVCache 与推荐稀疏参数两大场景下，存储规模向 TB/PB 演进所面临的传输与容量瓶颈，并明确给出基于 **RDMA（RoCEv2）+ NVMe SSD + SPDK** 的全栈技术选型依据与四大设计目标，为后续子系统详细设计奠定基调。

---

## 【技术要点】

1. **两大应用场景与瓶颈定位**：在线推理（推荐/广告）从十亿级参数演进至万亿级，Worker↔PS 数据交换成传输瓶颈；LLM KVCache 需要 TB～PB 级存储 + 高性能传输。
2. **ParaKV 四大设计目标**：
   - **高性能**：微秒级延迟、单机千万级 QPS、支持高吞吐批量读取
   - **高可用**：99.99% 服务可用性、容忍单点故障与网络分区、无缝切换、版本回滚
   - **可扩展**：10TB 级模型参数（DRAM+SSD 分层突破内存限制）、PB 级 KVCache
   - **易集成**：兼容主流 RoCE 网卡，无缝融入现有 **brpc** 微服务框架
3. **传输层选型 RoCEv2**：基于标准以太网 + IP 网络部署成本低；硬件要求 Mellanox ConnectX 系列、Broadcom NetXtreme-E、华为 HNS 等支持 RoCE 的网卡，交换机需支持 **PFC/ECN**。
4. **RDMA 核心概念封装**：原生 Verbs API 复杂，本方案设计 **Opt-PS-RDMA** 通信库，对外提供类似 RPC 的 **pull/push** 接口，并集成**连接池、内存池、故障切换**等能力；内部核心资源为 MR（l_key/r_key 保护）、QP（发送/接收队列）、CQ（完成队列）。
5. **存储介质选型 NVMe SSD**：速度通常超过 3000 MB/s、最快可达 7000 MB/s 以上；常见容量 3.84 TB、7.68 TB、15.36 TB；与 NVMe-oF 结合可实现基于 RDMA 的 CPU 卸载访问。
6. **NVMe 全栈协同优化**：硬件层 NVMe 协议（65,535 队列 × 65,535 深度 vs SATA 单队列 × 32）+ 驱动层 SPDK 用户态轮询 + 应用层 Segment/Slot 对齐（4 KB/16 KB 页、2 MB/4 MB 块）+ 写入策略 Append-Only + Compaction + TRIM + NVMe-oF 卸载到 DPU（NVIDIA BlueField）。

---

## 【关键机制与数据】

### RDMA 工作原理（原文）
- **单边操作**：RDMA Read/Write——目标端 CPU **不参与**；适合本场景的"读 KVCache / 推 PS 参数"高吞吐路径。
- **双边操作**：Send/Recv——目标端 CPU 需参与，类似传统消息传递。
- **核心优势数据**：现代 RDMA 网卡带宽**可达 200 Gbps**，延迟**低至 1 μs**。
- **数据流**：应用 ↔ 注册内存区域 MR（l_key 本地用 / r_key 远端用）↔ QP 发送/接收队列 ↔ 网卡硬件处理协议 ↔ 远端网卡 ↔ 远端 MR；CPU 几乎零参与。

### NVMe SSD 性能数据（原文）
- **协议并行度**：NVMe 支持 **65,535 个 I/O 队列**，**每队列深度 65,535**；SATA 仅支持单队列，深度 32。
- **速度**：通常超过 **3000 MB/s**，最快 **7000 MB/s 以上**。
- **容量**：3.84 TB / 7.68 TB / 15.36 TB 常见。
- **页/块尺寸**：SSD 读写以页为单位（**4 KB / 16 KB**），擦除以块为单位（**2 MB / 4 MB**）。

### ParaKV 写入与生命周期流程（原文）
1. **Append-Only 日志写**：利用 NVMe "顺序写 > 随机写"特性，写入 Segment。
2. **对齐 I/O**：Segment / Slot 严格对齐到 SSD 页边界，确保原子读写，避免读-修改-写。
3. **Compaction（压实）**：后台将随机写回收为顺序写，降低写放大；同时配合主控的**磨损均衡**算法延长 SSD 寿命。
4. **TRIM 指令**：删除 Key 或 Compaction 释放 Segment 时主动下发，提前告知 SSD 主控失效地址，加速垃圾回收。
5. **分布式卸载**：通过 NVMe-oF + DPU（如 NVIDIA BlueField），将 NVMe 传输路径完全卸载到硬件，绕过 Arm 核心，实现 GPU/CPU 内存 ↔ 远端 NVMe SSD 的**零 CPU 参与**数据通路。

### SPDK 优化机制（原文）
- **用户态驱动**：绕过内核，直接 MMIO 与 NVMe 设备通信，消除系统调用与上下文切换。
- **轮询模式**：CPU 主动"忙等"在设备队列上，**牺牲功耗换取极致低延迟与吞吐**。
- **零拷贝**：DMA 直接在 NVMe 设备与应用内存间传输。

---

## 【表格解读】
**原文无表格**。

---

## 【公式解读】
**原文无公式**。

---

## 【关联】

原文标注的内部链接为 **(无)**，即本文档未提供具体内部超链接路径。但文中**点名引用了若干配套子系统与外部技术**，构成如下上下游关系：

| 文中提及的特性/模块 | 在 ParaKV 中的角色 | 上下游关系 |
|---|---|---|
| **Opt-PS-RDMA 通信库** | 封装原生 RDMA Verbs API，提供 pull/push 接口 | 上承 ParaKV 业务层，下接 RDMA 网卡硬件（RoCEv2） |
| **SPDK** | NVMe 用户态驱动 + 轮询 + 零拷贝 | 上承 ParaKV Segment/Compaction 逻辑，下接 NVMe SSD 硬件 |
| **NVMe-oF** | 基于网络的 NVMe 远程访问 | 与 RDMA 协同，构建分布式存储底层 |
| **NVIDIA BlueField DPU** | 智能网卡，硬件卸载 NVMe 数据通路 | 旁路 Arm 核心，连接 GPU/CPU 内存与远端 NVMe SSD |
| **brpc 微服务框架** | ParaKV 集成的目标 RPC 框架 | 部署形态依赖，需 ParaKV 提供兼容接口 |
| **RoCEv2 + PFC/ECN 交换机** | 传输网络底座 | 机房网络部署前置条件 |

> 注：原文中这些模块以**文字描述**形式出现，未提供内部 markdown 链接，因此无法映射到仓库具体路径。

---

## 【使用方法】
**原文未涉及**。

本文档为**引言级总纲**，聚焦于"为什么选型"与"设计目标"，未涉及具体的启用方式、配置文件项、启动命令、API 调用示例或运维步骤。这些内容预计在后续的设计子文档（如 RDMA 通信库设计、Segment 存储引擎设计、Compaction 调度设计等）中给出。
