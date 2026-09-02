# Mooncake Architecture

> 仓 `mooncake` · 路径 `doc/en/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mooncake/doc/en/architecture.md

# Mooncake Architecture 文档深度解读

## 【定位】
本文档是 Mooncake 存储子系统的架构总览, 阐述其如何通过 DRAM/SSD 多级缓存池与 (GPUDirect) RDMA 零拷贝传输, 提升大语言模型在慢速对象存储环境下的推理效率, 并给出组件拓扑与职责划分.

## 【技术要点】
1. **多级缓存池构建**: 在高速互连的 DRAM/SSD 资源上搭建多级缓存池, 应对慢速对象存储环境的 LLM 推理瓶颈.
2. **零拷贝传输**: 利用 (GPUDirect) RDMA 技术, 将数据从发起端的 DRAM/VRAM 直接搬运至目标端 DRAM/VRAM, 全程零拷贝; 同时最大化利用单机的多 NIC 资源.
3. **对象级存储与副本策略**: 提供对象级数据存储服务; 缓存层支持数据复制, 采用 slice 级 placement 保证 + best-effort 分配, 属轻量化设计 (不保证高可用).
4. **写操作原子性**: 保证 `Put` 写入的原子性, 即 `Get` 永远读到一致版本, 但不保证读到最新版本.
5. **大对象并行 I/O**: 支持 striping 与并行 I/O 传输, 利用多网卡聚合带宽.
6. **动态与多模式刷盘**: 支持多种向慢速对象存储刷盘 (flush) 的模式; 支持缓存资源的动态增删.

## 【关键机制与数据】
- **组件分工 (拓扑)**:
  - **Master 节点**: 集中管理 object → VRAM/DRAM/NVM buffer 的映射关系; 并通过调用 Transfer Engine 的 API 驱动 **managed pool buffer 节点**完成数据搬运. (原文: "The master node centrally manages the mappings of objects to VRAM/DRAM/NVM buffers. The master node also drives managed pool buffer nodes to achieve data transfer by calling Transfer Engine's APIs")
  - **Managed pool buffer 节点**: 主要提供 DRAM 空间用于存放对象. (原文: "Managed pool buffer nodes mainly provide DRAM space for storing objects")
- **传输引擎**: Transfer Engine 作为已开源子模块, 支撑跨机器 VRAM/DRAM/NVMe SSD 的零拷贝与多 NIC 数据传输. (原文: "This feature is supported by Transfer Engine, which has been open-sourced")
- **数据流抽象**: 文档以职责说明方式描述数据流 (Master 调度 → Transfer Engine API → managed pool buffer 节点执行), 未给出具体的数据包格式/时序图.
- **接口面**: 对象级操作 `Get / Put / List / Del`; 副本策略可通过 `Replicate` 操作动态配置. (原文: "Mooncake provides object-level operations, i.e. `Get/Put/List/Del`, and also supports dynamically configurating replication strategies (`Replicate` operations)")
- **性能数据**: 原文未给出具体性能数字 / 基准测试结果 / 量化指标, 仅以特性描述形式呈现.
- **架构图**: 文档引用一张 `architecture` 图片 (`../../image/mooncake-store.png`), 文中未对图内组件做进一步展开描述.

## 【表格解读】
原文无表格 (文档仅包含一张架构示意图 `mooncake-store.png`, 无任何参数表/对比表/配置项表).

## 【公式解读】
原文无公式 (文档以自然语言 + 架构图描述系统, 未出现任何 LaTeX 公式或伪代码公式).

## 【关联】
- **核心依赖 — Transfer Engine**: 文档明确将零拷贝、多 NIC、跨 VRAM/DRAM/NVMe SSD 传输能力归属到 Transfer Engine, 并声明其已开源, 但同时注明 "updates are forthcoming", 表明 Transfer Engine 是 Mooncake 存储层的数据搬运底座, 但不是本次文档展开的重点.
- **节点关系**:
  - Master 节点 → Managed pool buffer 节点: 通过 Transfer Engine API 驱动数据搬运, 形成"控制面 (Master) + 数据面 (buffer 节点)" 的解耦关系.
  - Managed pool buffer 节点 → Transfer Engine: 作为数据面承载方, 将自身 DRAM 空间暴露给 Transfer Engine 完成 RDMA 收发.
- **存储分层关联**: 文档将存储分为三层视角 — 慢速对象存储 (后端) / DRAM (managed pool buffer 节点) / VRAM·NVMe SSD (经 Transfer Engine 访问的端侧介质), 三者通过刷盘模式、多级缓存池耦合.
- **内部链接**: 文末标注 "内部链接: (无)", 因此本节无法引用同仓其他文档; 关联信息均来自本文档内部叙述.

## 【使用方法】
原文未涉及 (文档聚焦架构与能力描述, 未给出启用步骤、配置项、命令行示例或 API 调用样例; 具体使用方法需参考其他文档或 Transfer Engine 仓库).

## 图文联合解读

- `mooncake-store.png`: **图示内容**：左侧Mooncake Managed Store Master统一调度Get/Put/Replicate/List/Del对象操作；多个推理服务器并列，每台含Store Client→Transfer Engine操控RAM段（VRAM/DRAM分页KVCache与Managed Pool Buffer），各服务器Buffer间**双向箭头直连**（零拷贝对等RDMA）；下方Other Cache Pool含NVMeof/RPC段，最底层回写Object Store/PFS，并标注BatchTransfer Read/Write/Flush。

**技术结论**：① 分层多级缓存池（内存池→SSD/远端段→慢对象存储）；② 中心化元数据 + 去中心化高速数据通路；③ 多NIC聚合带宽的分片并行I/O。

**对应文档**：直观验证"DRAM/SSD多级缓存池""GPUDirect RDMA零拷贝""分片并行I/O""多模式刷新慢存储""对象级存储与原子写"等核心论点。
