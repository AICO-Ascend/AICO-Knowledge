# 昇腾硬件架构与 SHMEM 约束

> 仓 `agent-skills` · 路径 `community/Op/shmem-ops-design/references/hardware-architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/community/Op/shmem-ops-design/references/hardware-architecture.md

# 昇腾硬件架构与 SHMEM 约束 — 一体化深度解读

---

## 【定位】

本文档是 SHMEM 算子设计与性能优化的**硬件参数基线参考**：在昇腾 910B/910C 系列 AI 处理器上做 SHMEM 通信/计算融合算子设计时, 必须以本文给出的核数、容量、带宽、链路拓扑、引擎选型为依据,**不得套用错误的硬件参数**(如把 AIC 数错置为 64), 并据此判断算子的 `block_dim` 上限、DMA 单次搬运大小、对称堆容量与集合通信的 `peak_bandwidth` 选取策略。

---

## 【技术要点】

1. **AI Core 分离架构 (910B/910C)**: AIC (Cube) 与 AIV (Vector) 分离, **不存在直连数据通道**, 全部交互经 L2; 区别于 910A 的耦合模式。每个 AIC 含 1 个 Cube + 2 个 Vector 单元。
2. **MTE 三级 DMA 模型**: MTE2 (GM → UB/L0)、MTE3 (UB/L0 → GM)、MTE1 (内部存储间)。SHMEM 的 MTE 路径 `aclshmemx_mte_put/get_nbi` 必须有 UB 中转, **单次最优搬运 190 KB (`190*1024` B), 最小 16 KB**。
3. **核数与算力硬约束**: 910B2 AIV 上限 **48**、AIC 上限 **24**; 910B3 AIV 上限 **40**、AIC 上限 **20**; 910B1 AIV 50/AIC 25; 910C 双 die 约 80–96 AIV / 40–48 AIC。**`block_dim` 不得超过目标 SoC 的 AIV 核数**。
4. **HCCS 链路与拓扑**: 单链路单向 **~28 GB/s**、双向 **~56 GB/s**, 每 NPU/Die 7 根 HCCS。910B 单机 8 卡为 full-mesh (任意两卡 28 GB/s 单向); 910C 双 die 经交换机, **同卡两 die 间 270 GB/s (SIO), 跨卡 die 间 196 GB/s**。
5. **`peak_bandwidth` 必须按通信模式选取**: P2P put/get → 28 GB/s (单链路); AllReduce/AllGather 等集合通信 → `N_links × 28 GB/s` (聚合带宽, mesh 算法同时占用 N-1 条)。报告中须注明所用值、SoC 型号、链路来源。
6. **同步分两层**: 核内用 `AscendC::SyncAll` / `PipeBarrier`; 跨 PE 用 `aclshmemx_signal_op` + `aclshmem_signal_wait_until` / `aclshmem_barrier_all` / `aclshmem_team_sync`。**`aclshmem_quiet` 等全局 quiet 等所有引擎完成**, 而 `aclshmemx_mte_quiet` / `sdma_quiet` / `udma_quiet` / `roce_quiet` 为单引擎 quiet, **MTE put/get 时必须用 `aclshmemx_mte_quiet`, 不可误用全局 quiet**。
7. **RDMA/RoCE 路径**: `aclshmemx_rdma_put/get_nbi` 直接 GM↔GM, 无 UB 中转, 适合跨节点或 P2P 不可达, **需 `-enable_rdma` 编译选项**。
8. **典型分核模式**: 前 N 个 core 负责通信 (comm core)、后 M 个 core 负责计算 (compute core), 用 `GetBlockIdx()` 分支分流; 动态 block_dim, 小数据用少量 core (如 8), 大数据用更多 (如 `2*n_pes`)。

---

## 【关键机制与数据】

### AI Core 工作原理 (原文 §1)
- **Cube 单元**执行 MatMul, 支持 fp16/bf16 输入 + fp32 累加; 原文: "单个 Cube 在 max 配置(16x16x16)下, 一个时钟周期完成 **4096 个 FP16 MACs**"。
- **Vector 单元**支持 fp16/bf16/fp32/int32 向量运算; **Scalar 单元**做标量计算与指令分发。
- **AIC 与 AIV 之间不具备直连数据通道, 所有交互经由 L2 完成** (原文 §1, 这是 SHMEM 在 910B/910C 上设计 comm/core 分离分核的物理基础)。

### 数据搬运机制 (原文 §3)
- **MTE 路径** (原文 §3.1): SHMEM 通过 MTE 实现 `GM ↔ UB` 与 `GM ↔ GM`; 节点内 P2P 可达场景首选, 延迟低, 但需 UB buffer 中转; 单次最优 **190 KB**, 最小 **16 KB**。
- **RDMA/RoCE 路径** (原文 §3.2): 跨节点或 P2P 不可达时使用; 不需 UB 中转, 直接 GM↔GM; **需 `-enable_rdma` 编译选项**。
- **SDMA** (原文 §3.3): Host 侧发起, 主要用于 Host↔Device 拷贝, 部分场景可用于 Device 间大块搬运。

### 同步机制 (原文 §4)
- **核间同步** (原文 §4.1): `AscendC::SyncAll` 用于同一 PE 内多 AIV 核间同步; `AscendC::PipeBarrier<PIPE_*>` 用于单 AIV 内流水线阶段同步。**禁止** custom-ops 新代码调用 internal `aclshmemi_barrier_core_soft`(无公开 API)。
- **跨 PE 同步** (原文 §4.2): `aclshmem_quiet` 等待本 PE 已发出的**全引擎** RMA 完成(MTE+SDMA+UDMA+RDMA); `aclshmem_fence` "保证本 PE 后续读取看到之前收到的写入(**当前实现等价于 `aclshmem_quiet`**)"(原文 §4.2)。
- **FFTS** (原文 §4.3): "`util_get_ffts_config()` 获取 FFTS 配置地址, 通过 launch 参数传入 kernel", 用于配置 kernel launch 参数与同步基址。

### 拓扑与算法匹配 (原文 §2.5)
- **full-mesh (910B 8 卡)** → HCCL **mesh 算法**: 所有 peer 链路并发, 充分利用 N-1 条 HCCS, 适用单机 AllReduce/AllGather/ReduceScatter。
- **switch (910C 双 die)** → 视 switch 带宽选择算法: Die 间经 switch 转发, 非直连, 跨 Die 带宽受限。
- **ring** → HCCL ring 算法: 沿环逐跳, 每跳只一条链路, 适用跨节点 / ring 拓扑。
- 原文明确原则: **"如果当前实现的通信模式(如 peer 串行 get)与硬件拓扑不匹配(如 full-mesh 下只用了 1 条链路), 应优先做算法级重构而非细粒度调参"** (原文 §2.5)。

### 分核模型 (原文 §5)
- 前 N core 通信、后 M core 计算, 按 `GetBlockIdx()` 分支; 动态 block_dim。
- `block_dim` 总数不得超过目标 SoC AIV 核数 (910B2 ≤ 48, 910B3 ≤ 40)。

---

## 【表格解读】

### 表 2.1 — 核数与算力 (原文逐字还原)

| 参数 | 910B1 | 910B2 | 910B3/B4 | 910C |
| --- | --- | --- | --- | --- |
| AIC (Cube Core) 数量 | 25 | **24** | **20** | ~40-48 (双 die) |
| AIV (Vector Core) 数量 | 50 | **48** | **40** | ~80-96 (双 die) |
| 每 AIC 含 Cube 单元 | 1 | 1 | 1 | 1 |
| 每 AIC 含 Vector 单元 | 2 | 2 | 2 | 2 |
| FP16 算力 (TFLOPS) | ~414 | ~376 | ~320 | ~800 |
| INT8 算力 (TOPS) | ~828 | ~752 | ~640 | ~1600 |

**逐行解读**:
- **AIC 数量行**: 910B2 严格为 24, 910B3/B4 严格为 20; 910C 因双 die 给出范围 ~40-48, 含不确定性。原文标注 **"将 AIC 数量错设为 64 是常见错误"**。
- **AIV 数量行**: 是 **`block_dim` 上限的直接依据** — 910B2 = 48, 910B3 = 40。910C 因双 die 给出 ~80-96。
- **每 AIC 单元构成**: Cube:Vector = 1:2, 这是 SHMEM 分核中 "1 个 AIC + 2 个 AIV" 物理配比的来源。
- **FP16/INT8 算力**: 910B1 > 910B2 > 910B3 (注: 910B1 AIC 数反而最多), 910C 大致为 910B1 的两倍。原文数值带 `~` 表近似, 来源为公开资料综合。

### 表 2.2 — 存储层次与容量 (原文逐字还原)

| 存储 | 缩写 | 容量 | 特性 | SHMEM 用途 |
| --- | --- | --- | --- | --- |
| Global Memory (HBM) | GM | 64 GB (910B) / 96 GB (910C) | 大容量、高带宽、所有 core 可见 | 对称堆、输入输出 buffer、signal/state |
| Unified Buffer | UB | **192 KB** (per core) | 每 core 私有、低延迟 | DMA 中转、本地计算中间结果 |
| L1 Buffer | L1 | 512 KB | Cube 单元输入缓存 | MatMul 数据加载 |
| L0A/L0B | L0 | 各 64 KB | Cube 单元寄存器级缓存 | MatMul 操作数 |
| L0C | L0C | 128 KB | Cube 单元累加器 | MatMul 累加结果 |

**逐行解读**:
- **GM**: 是 SHMEM 对称堆所在层, 原文: "GM(HBM)容量决定对称内存最大 `local_mem_size`; SHMEM 默认对称堆上限 `100*1024*1024` 字节"。
- **UB**: 关键中转层, 192 KB/core; 原文: "UB 总容量 192 KB/core; SHMEM examples 常用 `190*1024` 字节作为单次 DMA 搬运上限" — 即预留 2 KB 给元数据/对齐。
- **L1 / L0A / L0B / L0C**: 均为 Cube 单元专属, 决定单次 MatMul 的 tile size 上限 (L0C 128 KB 限累加结果)。

### 表 2.3 — 带宽参数 (原文逐字还原)

| 参数 | 910B1/B2 | 910B3 | 910C(双 Die) |
| --- | --- | --- | --- |
| HBM 带宽 | ~1.2 TB/s | ~1.2 TB/s | ~1.8-3.2 TB/s |
| **HCCS P2P 单链路带宽(单向)** | **~28 GB/s** | **~28 GB/s** | **~28 GB/s** |
| **HCCS P2P 单链路带宽(双向)** | **~56 GB/s** | **~56 GB/s** | **~56 GB/s** |
| HCCS 链路数 (per NPU / per Die) | 7 (full-mesh 直连其余 7 卡) | 7 | 7 (per Die, 连接到交换机) |
| P2P带宽 | 28GB/s(单向) | 28GB/s(单向) | 196GB/s(单向/单die) |
| L2 Cache 片上访问带宽 | ~4 TB/s | ~4 TB/s | - |

**逐行解读**:
- **HBM 带宽**: 910B 三档均约 1.2 TB/s; 910C 因双 die 翻倍到 1.8-3.2 TB/s。
- **HCCS 单链路单向/双向**: 三档 SoC 均为 28/56 GB/s, 这是 P2P put/get 的基准带宽。
- **HCCS 链路数**: 都是 7, 但拓扑不同 — 910B 直连其余 7 卡 (full-mesh), 910C 是 per Die 连交换机。
- **P2P带宽 (末行)**: 910B 单向 28 GB/s (单链路); **910C 196 GB/s 是单向/单 die** = 7 × 28, 即满链路聚合。
- **L2 带宽**: 910B 约 4 TB/s (AIC↔AIV 走 L2, 这是为什么 "所有交互经 L2" 仍是高性能设计的关键); 910C 原文留空。
- 原文下方有"注意": **"910C 中同一卡上两个 DIE 通过 SIO 链路, P2P 带宽为 270 GB/s。196 GB/s 是不同卡上的 DIE 之间的带宽"** — 这两条 P2P 值不要混淆。

### 表 2.4 — 服务器拓扑 (原文逐字还原)

| 服务器型号 | 芯片 | 卡数 | 节点内互联 | 节点间互联 |
| --- | --- | --- | --- | --- |
| Atlas 800T A2 | 910B | 8 | HCCS **full-mesh** (每 NPU 7 根 HCCS 直连其余 7 卡, 任意两卡 28 GB/s 单向) | RoCE v2 (200 Gbps) |
| Atlas 800T A3 | 910B3 | 8 | HCCS **full-mesh** | RoCE v2 (200 Gbps) |
| 910C 集群 | 910C | 多卡 | HCCS **交换机组网** (每 Die 7 根 HCCS 连交换机, Die 间 ~196 GB/s) | RoCE v2 |

**逐行解读**:
- **Atlas 800T A2/A3**: 都是 8 卡 910B 系列, full-mesh 拓扑决定单机集合通信应优先用 mesh 算法 (而非 ring)。
- **910C 集群**: Die 通过交换机转发, "跨 Die 带宽受限", 集合通信算法选择与 full-mesh 不同。
- **节点间互联**统一为 RoCE v2 (200 Gbps), 跨节点必须走 RDMA 路径, 故需 `-enable_rdma`。

### 表 2.5 — 拓扑与集合通信算法 (原文逐字还原)

| 拓扑 | HCCL 典型算法 | 特征 | 适用场景 |
| --- | --- | --- | --- |
| full-mesh (910B 单机 8 卡) | **mesh 算法** | 所有 peer 链路并发收发, 充分利用 N-1 条 HCCS | 单机 AllReduce/AllGather/ReduceScatter |
| switch (910C 双 Die) | 视 switch 带宽选择 | Die 间经 switch 转发, 非直连, 跨 Die 带宽受限 | 910C 节点内集合通信 |
| ring | ring 算法 | 沿环逐跳传递, 每跳只用一条链路 | 跨节点 / ring 拓扑场景 |

**逐行解读**:
- 性能优化核心准则 (原文 §2.5): "通信模式与硬件拓扑不匹配…应优先做**算法级重构**而非细粒度调参" — 例如 full-mesh 下用 ring 会浪费 N-1 倍带宽。

### 表 2.6 — peak_bandwidth 选取 (原文逐字还原)

| 通信模式 | peak_bandwidth | 说明 |
| --- | --- | --- |
| P2P 点对点 (put/get 到单个 peer) | 28 GB/s | 单条 HCCS 链路单向 |
| 集合通信 (AllReduce/AllGather 等) | N_links × 28 GB/s (如 910B3 8 卡: 7 × 28 = 196 GB/s) | 聚合带宽, 因为 mesh 算法同时使用多条链路 |

**逐行解读**:
- P2P put/get 是单链路通信, 即便物理上有 7 条 HCCS, 一次通信只占用 1 条 → peak = 28 GB/s。
- 集合通信在 mesh 算法下并发占用 N-1 条 → peak = 7 × 28 = 196 GB/s (910B3 8 卡)。
- 原文硬性要求: "报告中必须注明 `peak_bandwidth` 使用的值、SoC 型号和链路来源"。

### 表 5.1 — 分核上限约束 (原文逐字还原)

| SoC | AIV (Vector) 核数上限 | AIC (Cube) 核数上限 |
| --- | --- | --- |
| 910B2 | 48 | 24 |
| 910B3 | 40 | 20 |

**逐行解读**: 这是 `block_dim` 取值的硬上限表, 与表 2.1 互为印证。

---

## 【公式解读】

**原文无公式**。文档中出现的所有量化约束 (`190*1024` 字节、`100*1024*1024` 字节、`7 × 28 = 196 GB/s`、`N-1 × 28 GB/s`) 均为算术表达式而非公式定义, 未使用 LaTeX 或伪代码形式给出。

---

## 【关联】

### 文档内部模块互引
- **§1 AI Core 架构** ↔ **§2.1 核数与算力**: AIC/AIV 数量与算力来源于 AI Core 分离架构。
- **§2.2 存储层次** ↔ **§3.1 MTE**: UB 192 KB 决定 DMA 单次搬运上限 `190*1024`; GM 容量决定对称堆上限 `100*1024*1024`。
- **§2.3 带宽** ↔ **§2.4 服务器拓扑** ↔ **§2.5 算法** ↔ **§2.6 peak_bandwidth**: 四节构成完整链路: 物理带宽 → 拓扑连接 → 算法选择 → 报告口径, 不可割裂使用。
- **§3 DMA 引擎** ↔ **§4 同步**: 不同引擎 (MTE / SDMA / UDMA / RDMA / RoCE) 对应不同的 quiet API (`aclshmemx_mte_quiet` / `sdma_quiet` / `udma_quiet` / `roce_quiet`) 与全局 `aclshmem_quiet`。
- **§4.1 核间同步** ↔ **§5 分核模型**: `SyncAll` 与 `GetBlockIdx()` 分支是 comm/core 分离分核模式的两个执行手段。

### 上下游模块
- **CANN 工具包 `platform_config`** (原文 §6): 硬件参数的官方来源, 用于解析芯片子产品参数。
- **HAMi 虚拟化配置** (原文 §6): 提供 aiCore / aiCPU 数量的虚拟化层视角。
- **HCCL 集合通信库** (原文 §2.5): 上游, 提供 mesh / ring 等算法; SHMEM 在集合通信场景下需与 HCCL 算法协同。
- **`npu-smi info` 命令** (原文 §6): 运行时查询实际硬件配置。
- **AscendC 编程框架 (`AscendC::SyncAll` / `PipeBarrier`)** (原文 §4.1): 上游 API, 链接到 asc-devkit 的 `SyncAll.md` 文档 (这是文档中**唯一出现的内部链接**)。
- **SHMEM API 层 (`aclshmemx_*` 系列)** (原文 §3-4): 下游, 本文为该层提供硬件参数依据。
- **`-enable_rdma` 编译选项** (原文 §3.2): 控制 RDMA/RoCE 路径是否启用。

---

## 【使用方法】

### 核数与 block_dim 设置 (原文 §2.1, §5.1)
```text
910B1: AIV ≤ 50, AIC ≤ 25
910B2: AIV ≤ 48, AIC ≤ 24   ← 原文加粗强调
910B3/B4: AIV ≤ 40, AIC ≤ 20  ← 原文加粗强调
910C (双 die): AIV ~80-96, AIC ~40-48
```
原文强制约束: **`block_dim` 不得超过目标 SoC 的 AIV 核数**; **"将 AIC 数量错设为 64 是常见错误"**。

### DMA 搬运配置 (原文 §3.1)
- **API**: `aclshmemx_mte_put_nbi` / `aclshmemx_mte_get_nbi`
- **单次最优大小**: `190 * 1024` 字节 (≈ 190 KB)
- **单次最小大小**: 16 KB
- **中转要求**: 必须使用 UB buffer 作为中转

### RDMA 路径启用 (原文 §3.2)
- **API**: `aclshmemx_rdma_put_nbi` / `aclshmemx_rdma_get_nbi`
- **特性**: 直接 GM↔GM, 无 UB 中转
- **编译选项**: `-enable_rdma`

### 同步 API 选用 (原文 §4.1-4.2)
| 场景 | API |
| --- | --- |
| 同 PE 内多 AIV 核间同步 | `AscendC::SyncAll` |
| 单 AIV 内流水线阶段同步 | `AscendC::PipeBarrier<PIPE_*>` |
| 跨 PE 信号写入 | `aclshmemx_signal_op` |
| 跨 PE 信号等待 | `aclshmem_signal_wait_until` |
| 全 PE 集合同步 | `aclshmem_barrier_all` / `aclshmem_team_sync` |
| 全引擎 RMA 完成等待 | `aclshmem_quiet` (MTE+SDMA+UDMA+RDMA) |
| MTE put/get 完成等待 | `aclshmemx_mte_quiet` (原文强调: "勿误用全局 `aclshmem_quiet`") |
| 写后读一致性 | `aclshmem_fence` (当前实现等价于 `aclshmem_quiet`) |
| FFTS 配置获取 | `util_get_ffts_config()` |

### 对称堆容量配置 (原文 §2.2)
- **默认对称堆上限**: `100 * 1024 * 1024` 字节 (≈ 100 MB)
- 上限由 GM (HBM) 实际容量决定 (910B: 64 GB / 910C: 96 GB)

### 性能报告口径 (原文 §2.6)
报告中必须注明 `peak_bandwidth`:
- **P2P put/get**: 28 GB/s (单条 HCCS 单向)
- **集合通信**: `N_links × 28 GB/s` (例: 910B3 8 卡 mesh = 7 × 28 = 196 GB/s)
- 同时注明 SoC 型号与链路来源。

### 硬件参数查询 (原文 §6)
- 运行时: `npu-smi info`
- 静态配置: 解析 CANN 工具包 `platform_config` 目录
- 虚拟化层: HAMi 配置 (aiCore / aiCPU 数量)

### 分核模式实现 (原文 §5)
- 前 N core (comm core) + 后 M core (compute core)
- 通过 `GetBlockIdx()` 获取当前 core 编号分支
- `GetBlockNum()` 获取总核数
- 动态 block_dim: 小数据用少量 core (例: 8), 大数据用更多 core (例: `2 * n_pes`)
