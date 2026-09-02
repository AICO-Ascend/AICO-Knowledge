# global_kvcache

> 仓 `xllm` · 路径 `docs/src/content/docs/en/features/global_kvcache.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/en/features/global_kvcache.md

# 一体化深度解读:Global Multi-Level KV Cache

## 【定位】

本文档系统阐述 xLLM 如何将原本仅驻留在设备 HBM 的 KV 前缀缓存,扩展为「Device HBM / Host pinned memory / Mooncake Store」三级层次化体系,以解决长上下文推理中设备显存容量与带宽瓶颈,以及冷请求重复计算前缀的问题,并描述该机制在融合 (Fused) 实例与 Prefill/Decode 解耦 (Disaggregated PD) 两种部署形态下的运行时行为差异。

## 【技术要点】

1. **三级存储层次**:Device HBM(当前前向所用,最低延迟,Device-local 生命周期)→ Host cache(锁页 CPU 内存,可复用主机前缀缓存,xLLM 进程生命周期)→ Mooncake Store(跨 xLLM 进程/重启共享的分布式 KV 对象,Store 集群生命周期)。
2. **冷请求命中路径**:请求首先查 Host prefix cache;缺失的整块可从 Mooncake Store 预取到 Host 预分配块,再逐层恢复到 HBM,匹配前缀无需重算;前向完成后 HBM 块被异步拷回 Host,再写回 Mooncake Store。
3. **TP rank 间发布判定**:`PrefetchResult` 对所有 TP rank 的命中位图做 Logical AND,只有当**每一个 TP rank 都命中**时,对应块才可发布 (publishable)。
4. **元数据发布先于物理 H2D**:`BlockManager` 在 token-cursor 范围内发布 Device Prefix 元数据,但该发布发生在 H2D 物理拷贝完成之前,Forward 必须显式按层等待事件 (event)。
5. **层间同步器**:`Worker` 为每个 batch 创建 `LayerSynchronizer(batch_id)`,在每段 layer-copy 范围内:Copy 流先读 Host KV → 发起异步 H2D copy 并记录 event → 当前计算层等待该 event → event 完成后才读取 HBM KV。
6. **Scheduler 不接收完成回调**:`Scheduler` 在 `transfer_blocks` 后立即返回,**不等待 H2D 完成**;Offload 完成由 `BlockManager` 的 future 回调处理,而不是 Scheduler。
7. **D2H2G 部分失败语义**:BatchPut 部分失败仅被记录,**不改变 D2H 的成功标志**;但若任一 TP rank 的 D2H/RPC 失败,则不发布 Host Prefix Cache 并释放保留的 Host 块。
8. **PD 解耦下的职责切分**:Prefill 走完整的 Mooncake admission + Host restore + write-back 路径;Decode 仍启用 Store 和 Host cache(供 write-back 使用),但其请求 admission 路径**只探测 Device Prefix Cache**,不挂载 Host aliases、不从 Mooncake 拉前缀、不调度 H2D 恢复。

## 【关键机制与数据】

工作原理按 Block Lifecycle 的三个阶段描述(原文 Mermaid sequenceDiagram 已给出完整交互),摘要如下:

- **Phase 1:请求 admission 与 Mooncake 预取**(蓝色分组)
  - `Scheduler.add_request` → `BlockManager.prefetch_from_storage` → 先探 Host Prefix Cache,得到已有块与空洞 (holes);
  - 为空洞在 Host 上分配 G2H (Global-to-Host) 目的块;
  - 若 Host 已覆盖前缀,跳过对 Store 的 RPC;否则通过 `Engine` 创建 worker-by-block 的结果矩阵,并行下发到所有 TP rank;
  - 各 rank 调用 `BatchIsExist(keys)` 得到存在位图 → 仅对存在 key 执行 `BatchGet(existing keys, Host tensors)` 填充 Host 张量;
  - Scheduler 通过 `update_prefetch_result(timeout)` 轮询 `PrefetchResult.completed()`,最终取 `merged_hits()`(跨 TP rank 逻辑与);
  - 释放 Store 未命中的目的块 → 缓存 Store 命中块 → 计算可达前缀并挂载 Host 状态 → 标记 `AdmissionReady / enqueue_ready_request`。
  - **原文:"Workers do not directly callback the Scheduler"**。

- **Phase 2:Host → HBM 恢复与前向**(绿色分组)
  - `Scheduler.allocate(sequence, num_tokens)` → `BlockManager` 合并 Device 与已挂载 Host 前缀 → 在 HBM 分配缺失的 Device 块,并 best-effort 为未来 D2H 预留 Host 目的块;
  - 发布 Device Prefix 元数据(token-cursor bounded,**先于物理 H2D 完成**,原文如此);
  - 构建逐层 H2D 计划,`transfer_blocks(batches)` 入队后**立即返回**;
  - 各 rank 注册 H2D 传输,创建 `LayerSynchronizer(batch_id)`,异步调度 `load_from_host`,Forward 按 batch_id 顺序执行并挂载同步器,逐层读 Host KV → 发起异步 H2D + record event → 当前层 wait event → event 完成后读 HBM KV。
  - **原文:"There is no H2D-complete callback to the Scheduler"**。

- **Phase 3:HBM → Host → Mooncake 写回**(橙色分组)
  - `Scheduler.deallocate(completed sequence)` → 发布已完成的 Device Prefix 元数据 → 收集 HBM-到-已保留-Host 块配对 → 复位序列(offload 对保留块引用);
  - `transfer_offload_blocks()` 提交异步 D2H2G 计划;
  - Copy 流等待 Compute 流 → 读 Device KV → D2H 拷贝并流同步 → `BatchIsExist(keys)` → key 不存在则 `BatchPut`,已存在则跳过(原文:"Skip overwrite and count it as present");
  - **原文:"Partial BatchPut failure is logged only and does not change D2H success"**;
  - Engine 收集 TP futures,`PrefetchResult` 校验每个 TP 结果是否达到期望块数;
  - future 回调 `copy_ok` 触发:始终释放 offload 持有的 Device 块;若**每个 TP D2H/RPC 都成功**则发布 Host Prefix Cache,否则不发布并释放预留 Host 块。
  - **原文:"Offload completion is handled by the BlockManager callback, not the Scheduler"**。

- **部署组件**(原文:Architecture 段):`etcd`(注册计算实例、同步服务元数据)→ `xLLM Service`(路由请求、管理 Fused 或 Disaggregated PD 实例)→ `xLLM`(持有 Device 与 Host KV 缓存并执行推理)→ `Mooncake Store`(提供分布式、与进程独立的 KV 对象层)。

性能数据:**原文未涉及具体数字**(无 QPS/吞吐/延迟/显存占用等量化指标)。

## 【表格解读】

**原文表格(逐字还原)**:

| Tier | Purpose | Lifetime |
|---|---|---|
| Device HBM | Lowest-latency KV used by the current forward pass | Device-local |
| Host cache | Pinned CPU-memory staging and reusable host prefix cache | xLLM process |
| Mooncake Store | Distributed KV objects shared across xLLM processes and restarts | Store cluster |

**逐行解读**:

- **Device HBM**:**Purpose** 是「当前前向所用的最低延迟 KV」,**Lifetime** 是「Device-local」——即生命周期与设备绑定,这是常规推理路径上的工作集,容量受设备显存上限约束。
- **Host cache**:**Purpose** 是「Pinned CPU-memory staging and reusable host prefix cache」——既是锁页主机内存的暂存区,又是可复用的主机前缀缓存;**Lifetime** 为「xLLM process」,随 xLLM 进程终止而失效,因此承担的是同进程内的跨请求复用。
- **Mooncake Store**:**Purpose** 是「Distributed KV objects shared across xLLM processes and restarts」——分布式 KV 对象层,可在多个 xLLM 实例/重启之间共享;**Lifetime** 为「Store cluster」,独立于 xLLM 进程存在,因此承担跨实例/跨重启的复用。

整张表呈现的是**自下而上容量递增、延迟递增、生命周期跨度递增**的层次结构,对应文档中描述的「先查 Host → 缺块从 Mooncake Store 拉 → 命中前缀免重算 → 完成后再异步写回 Host 与 Store」的数据流。

## 【公式解读】

**原文无公式**。文档以架构图、Mermaid 序列图与文字描述形式说明流程,未出现 LaTeX 数学公式或伪代码公式。

## 【关联】

- **/en/getting_started/quick_start/**:本文是特性文档,描述能力如何工作;`quick_start` 提供部署/启动 xLLM 的入门流程,是阅读本特性前所需的运行环境与基本使用说明。
- **/en/features/disagg_pd/**:本文中「Disaggregated PD」一节明确指出 Prefill 与 Decode 实例在此特性下的职责切分(只有 Prefill 走完整 Mooncake admission + Host-to-HBM restore 路径;Decode admission 仅探测 Device Prefix Cache),该页面应进一步给出 PD 解耦的部署/调度细节,与本文形成「总体机制 + PD 模式特化」的互补关系。
- **/en/cli_reference/**:本文未直接列出 CLI 参数,但所提及的 `etcd`、`xLLM Service`、`xLLM`、`Mooncake Store` 组件及 Store/Host cache 启用行为通常由 CLI 开关控制;`cli_reference` 承载这些配置项的精确字段说明与启用方式。

## 【使用方法】

**原文未涉及**。本文档仅描述三级 KV Cache 的架构、Block Lifecycle 阶段(Mooncake 预取、Host→HBM 恢复、HBM→Host→Mooncake 写回)与 Disaggregated PD 模式下的行为切分,未提供启用该特性的 CLI 命令、环境变量、配置文件字段或 API 调用示例。具体的启用方式与配置项应参考相关链接 `/en/getting_started/quick_start/` 与 `/en/cli_reference/`。

## 图文联合解读

- `globalkvcache_architecture.png`: **图文解读(≤150字):**

图示分三块:左侧**ETCD**承担主选举、缓存/负载指标同步、服务发现;右上方**Global Multi-Level KV Cache Management**采用Master(Slave架构,含Global Scheduler与KVCache Mgr)+多Slave;右下方**Disaggregated Serving**部署Prefill与Decode实例,各含Xllm Engine、KV Cache与KV Cache Transfer,Prefill→Decode传递请求。红色箭头表示ETCD↔Master控制面,黑色箭头表示Master→实例下发与实例间调度。  
该图论证:**控制面(ETCD+Master)与执行面(Prefill/Decode实例)解耦**,通过Slave节点支撑分布式缓存对象管理,与文档论点呼应——xLLM在设备HBM之外新增Host缓存与Mooncake Store两级,实现跨进程/跨实例前缀复用,缓解长上下文推理对显存容量与带宽的压力。
