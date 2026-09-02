# global_kvcache

> 仓 `xllm` · 路径 `docs/src/content/docs/zh/features/global_kvcache.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/zh/features/global_kvcache.md

# xLLM 全局多级 KV Cache 深度解读

## 【定位】

这篇文档描述 xLLM 如何将传统的"单级 Device Prefix Cache"扩展为 **Device HBM + Host Cache + Mooncake Store** 三级缓存体系,用于解决长上下文推理中"相同前缀被其他请求或 xLLM 实例重复 Prefill 计算"的浪费问题,从而在多进程、多实例乃至进程重启之间复用 KV Cache。

---

## 【技术要点】

1. **三级缓存层次**:
   - **Device HBM**:Forward 计算使用的最低延迟 KV,设备本地,生命周期为设备本地;
   - **Host Cache**:Pinned CPU 内存中的 G2H/D2H 传输缓冲区 + 可复用 Host Prefix Cache,生命周期为 xLLM 进程;
   - **Mooncake Store**:分布式 KV 对象存储,跨 xLLM 进程和重启共享,生命周期为 Store 集群。

2. **三层部署组件**:etcd(注册计算实例 + 同步服务元数据)、xLLM Service(请求路由 + Fused/PD 分离实例管理)、xLLM(持有 Device/Host KV + 执行推理)、Mooncake Store(分布式可跨进程复用 KV 对象存储层)。

3. **Block 三阶段流转**:
   - **阶段一**:Scheduler→BlockMgr.prefetch_from_storage → Host Prefix Cache 探测 → 为 hole 分配 G2H 目标 block → 所有 TP Rank 并行 `BatchIsExist` + 命中后 `BatchGet` → 所有 TP bitmap 逻辑 AND(只有所有 TP Rank 都命中才能发布该 block);
   - **阶段二**:BlockMgr.allocate → 合并 Device Prefix 与已 mount 的 Host Prefix → 分配缺失 Device blocks + best-effort 预留 D2H 目标 Host blocks → 构建按层 H2D plan → Worker 异步调度 H2D copy 并在每层用 event 等待 → 物理 H2D 未完成即先发布元数据;
   - **阶段三**:BlockMgr.deallocate → 收集 HBM→预留 Host block pairs → D2H2G 异步 → `BatchPut`(失败仅记日志,不改变 D2H 成功状态) → 仅当所有 TP Rank 的 D2H/RPC 都成功才发布 Host Prefix Cache。

4. **TP bitmap 一致性**:PrefetchResult 在所有 TP Rank 上做**逻辑 AND**——任一 Rank 缺失即视为 miss,保证跨 Rank 数据一致性;Worker 不直接回调 Scheduler,全部经 BlockManager 解耦。

5. **Fused vs Decode 角色差异**:
   - Fused 实例 + PD 分离的 **Prefill**:完整使用 Mooncake 准入 + Host 恢复 + 写回流程;
   - **Decode**:Store 保持开启用于自身 Host/Mooncake 写回,但**请求准入只探测 Device Prefix Cache**,**不** mount Host alias、**不**从 Mooncake 获取 prefix、**不**调度 Host→Device 恢复。

6. **PD 分离特殊流程**:
   - Prefill 负责 Mooncake 准入 + Host→HBM 恢复;
   - **Decode 在 Prefill 开始前即预分配目标 Device Block**,通过 `AddNewRequests(prompt metadata)` 提前 reserve;
   - transfer cursor 会**跳过 D-side shared prefix**,避免重复传输;
   - Decode 仍需开启 Store + 配置 Host Cache 容量以供自身写回使用。

---

## 【关键机制与数据】

**(原文未提供任何性能数字、benchmark、TPS/QPS 等量化数据;以下仅为文档中描述的工作原理与数据流)**

**核心工作原理**(原文描述):

- **冷启动问题**:仅使用 Device Cache 时,即使相同前缀已被其他请求或其他 xLLM 实例计算过,冷请求仍然需要重新执行 Prefill → 这是文档明确指出的瓶颈。
- **命中路径**:请求首先探测 Host Prefix Cache;若 Host 已覆盖全部 prefix 则跳过 Store RPC;缺失的完整 Block 从 Mooncake Store 读取到预分配的 Host Block,再**按层**(layer-by-layer)恢复到 HBM,跳过已命中前缀的重复计算。
- **写回路径**:已完成的 HBM Block **异步**写回 Host,随后写入 Mooncake Store。
- **H2D 同步机制**:Worker 通过 `LayerSynchronizer(batch_id)` 挂载,每个 layer copy range 触发异步 H2D copy 并记录 event,当前计算层等待 event 完成后才读取 KV Cache——实现 H2D copy 与 Forward 计算的层间流水。
- **元数据发布与物理拷贝解耦**:H2D 元数据发布受 token cursor 限制,但**发生在物理 H2D copy 完成之前**——即 Scheduler 不等待 H2D 完成即可继续调度。
- **D2H2G 容错语义**:`BatchPut` 部分失败**仅记录日志,不改变 D2H 成功状态**;但 BlockManager 校验所有 TP 返回的 expected block count,**任一 TP Rank 的 D2H/RPC 失败则不发布 Host Prefix** 并释放预留 Host blocks;**无论 copy_ok 与否都释放 offload 持有的 Device blocks**。
- **PD 共享前缀跳过**:Prefill 通过 transfer cursor 跳过 D-side shared prefix,避免 P→D 传输已存在于 Decode 端的 KV。

**性能数据**(原文):**原文未涉及任何性能数据、benchmark、吞吐/延迟数字。**

---

## 【表格解读】

**原文表格**(逐字还原):

| 层级 | 用途 | 生命周期 |
|---|---|---|
| Device HBM | 当前 Forward 使用的最低延迟 KV | 设备本地 |
| Host Cache | Pinned CPU 内存中的传输缓冲区和可复用 Host Prefix Cache | xLLM 进程 |
| Mooncake Store | 在多个 xLLM 进程以及进程重启之间共享的分布式 KV 对象 | Store 集群 |

**逐行解读**:

| 行 | 解读 |
|---|---|
| Device HBM | **最低延迟**层,服务于正在执行的 Forward 计算——这是热路径 KV,容量受设备显存限制;生命周期"设备本地"意味着进程退出或设备重置即失效,故不能跨进程复用。|
| Host Cache | 兼具**两个用途**:① 作为 HBM↔Store 之间的 G2H/D2H **传输缓冲区**;② 作为**可复用 Host Prefix Cache**,提供进程内 prefix 命中。生命周期为 xLLM 进程——进程重启即失效,无法跨实例共享。|
| Mooncake Store | **跨 xLLM 进程 + 跨进程重启**的共享层,生命周期延续至整个 Store 集群;是实现"全局"多级 Cache 的关键,使多实例协同命中相同前缀成为可能。|

表格整体揭示了**延迟-容量-共享范围**的递进关系:HBM(快/小/私有)→ Host(中/中/进程内)→ Store(慢/大/全局)。任何命中路径都遵循"先本层、再外层"的探测顺序,且每一级同时承担**复用**与**传输中转**双重角色。

---

## 【公式解读】

**原文无公式。** 文档中没有出现 LaTeX 数学公式、伪代码数学表达式或性能公式。仅有 mermaid sequence 图描述控制流与时序。

---

## 【关联】

文档与其他特性的关联如下(基于文中提及与文末内部链接):

1. **PD 分离(Disaggregated Prefill-Decode)** `/zh/features/disagg_pd/`:
   - 文档专设"PD 分离"章节,描述 Prefill/Decode 在三级 KV Cache 中的**角色分工**——Prefill 负责 Mooncake 准入 + Host→HBM 恢复,Decode 仅负责自身写回 + 预分配目标 block;
   - 通过 `AddNewRequests(prompt metadata)` 提前在 Decode 端 reserve,`TransferKVInfo` 协调 P→D 的 KV 传输(Mooncake KVTransfer);
   - shared prefix 通过 transfer cursor 跳过,避免冗余传输——这是 PD 分离与全局 KV Cache 的深度耦合点。

2. **xLLM Service 路由层**:作为"Client / xLLM Service"出现在两个 sequence 图首部,负责请求路由与 Fused/PD 分离实例管理,是调用方进入三级 Cache 体系的入口。

3. **Mooncake Store**:作为分布式 KV 对象存储层,既是 xLLM 的外部依赖,也是整个全局 Cache 体系的**最外层共享层**,文档中以独立架构组件出现。

4. **etcd**:用于注册计算实例 + 同步服务元数据,与 xLLM Service 配合实现实例发现与调度,是部署侧的依赖组件。

5. **快速开始(Quick Start)** `/zh/getting_started/quick_start/` 与 **CLI 参考** `/zh/cli_reference/`:
   - 文档未给出具体配置项,但要在实践中启用全局多级 KV Cache,需通过 quick start 部署 etcd + xLLM Service + Mooncake Store 集群,并参照 CLI reference 启用 Host Cache 与 Store;
   - 文档本身的"使用方法"章节未展开,需结合这两个链接补全配置细节(参见下节)。

6. **TP(张量并行)**:文档中多次提及"所有 TP Rank 并行"、"TP bitmap 逻辑 AND",说明全局 KV Cache 在 TP 拓扑下的**一致性约束**——一个 block 必须所有 TP Rank 都命中才能被发布使用。

---

## 【使用方法】

**原文未涉及具体启用方式、配置项或 CLI 命令。** 文档聚焦于工作机制与数据流描述,未给出:

- 启动 xLLM 时启用 Host Cache 的配置项;
- 启用/连接 Mooncake Store 的 endpoint 配置;
- etcd 集群的部署与连接方式;
- CLI 命令(尽管文末链接指向 `/zh/cli_reference/`,文档本身未引用具体命令);
- Host Cache 容量、Block 大小、G2H/D2H 并发度等调优参数。

要在实践中启用全局多级 KV Cache,需结合文末链接的 **Quick Start**(`/zh/getting_started/quick_start/`)按其步骤部署 etcd + xLLM Service + Mooncake Store 组件拓扑,并参照 **CLI Reference**(`/zh/cli_reference/`)配置 Store endpoint 与 Host Cache 容量;**PD 分离**场景还需参考 `/zh/features/disagg_pd/` 文档。

> **注意**:本文档结尾处 PD 分离章节的 sequence 图(阶段三 PREFILL Forward 与 P→D KV 传输)被截断(`Note over PWorker,PHBM: Forward 按 batch_id 挂载 Laye...`),完整流程需结合 `/zh/features/disagg_pd/` 文档补充。

## 图文联合解读

- `globalkvcache_architecture.png`: 图示包含三大模块：左侧 ETCD 提供主选举、缓存/负载同步与服务发现；右上方 Global KVCache Manager 由 Master（含 Global Scheduler 与 KVCache Mgr）与多 Slave 构成，负责跨实例调度与 KV 元数据管理；右下方为 PD 分离的 Prefill/Decode 实例，各自持有 Xllm Engine、KV Cache 与传输模块，通过 Master 接入 Store。  

论证结论：xLLM 通过 ETCD 注册发现 + 全局调度器 + PD 分离实例，使 KV Cache 能在进程/集群级跨请求复用。  

与文档论点呼应：图中 ETCD↔Master↔实例的三方协同，正是文档"将 Device Prefix Cache 扩展为 HBM/Host/Mooncake 三级，并在多 xLLM 进程及重启间共享"这一架构落地的可视化体现。
