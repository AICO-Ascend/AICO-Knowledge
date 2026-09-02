# KV Offloading Usage Guide

> 仓 `vllm` · 路径 `docs/features/kv_offloading_usage.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/kv_offloading_usage.md

# KV Offloading Usage Guide — 一体化深度解读

## 【定位】

这篇文档解决的是 **vLLM 中如何将已完成的 KV cache block 从昂贵的 GPU 显存卸载 (offload) 到更大但更慢的存储层级 (CPU 主机内存, 以及可选的次级 tier) 以扩展 prefix cache 容量** 的问题, 同时描述了在命中时如何把数据回迁 (promote) 到 GPU 的完整配置与机制。

---

## 【技术要点】

1. **核心组件**: `OffloadingConnector` 通过在 `kv_connector_extra_config` 中的 `spec_name` 区分两种 spec — `CPUOffloadingSpec` (默认, 单层 CPU) 和 `TieringOffloadingSpec` (多层, CPU 主层 + 一个或多个次级层)。
2. **硬件支持边界 (原文)**:
   > "The `OffloadingConnector` currently supports CUDA, ROCm, and XPU only."
3. **数据传输机制**: GPU ↔ CPU 之间通过 DMA (`cudaMemcpyAsync`) 进行异步传输, 与模型计算重叠, 因此卸载对 CPU/GPU 计算核心的开销极小。次级 tier **没有直接访问 GPU 的能力**, 所有 GPU ↔ 次级 tier 的传输都必须经由 CPU 主层中转 (staged)。
4. **块大小与对齐约束**: `block_size` 必须是 GPU block size 的整数倍, 且与 `blocks_per_chunk` 互斥; `blocks_per_chunk` 默认为 `1`, 必须 > 0, 是为那些 KV cache group 具有不同 block size 的模型提供的替代方案。
5. **淘汰策略**: 内建 `lru`/`arc` (通过 `CachePolicyFactory` 预注册), 也支持通过 `cache_policy_module_path` 指向自定义 `CachePolicy` 类名 (无须 fork vLLM)。`store_threshold` 控制一个 block 被卸载前所需的最小查找次数, 但 `TieringOffloadingSpec` 拒绝 ≥ 2 的值。
6. **KV 事件自描述模式**: `self_describing_kv_events: true` 时, connector 会发出 block 粒度的 `BlockStored`/`BlockRemoved` payload (包含 constituent block hashes、whole-chunk `token_ids`、per-block `block_size`、parent hash、LoRA 与 group/cache-spec 元数据), 但必须同时配合 `--kv-events-config` 启用 KV cache events 才会生效; 否则保持占位回退。

---

## 【关键机制与数据】

### 数据流与拓扑 (原文 mermaid 流程)

```
GPU <--> CPU["CPU primary tier"]
CPU  <--> S0["Secondary tier 0"]
CPU  <--> S1["Secondary tier 1"]
CPU  <--> SN["..."]
```

即 GPU 只与 CPU primary tier 双向直连; 所有次级 tier 都挂在 CPU 主层之下, 形成一条"GPU ↔ CPU ↔ 次级层"的链式拓扑。这意味着在多 tier 配置中, 一次"GPU → 次级 tier 0"的写入实际上是两次中转 (GPU→CPU, CPU→S0), 一次命中回迁也是两次。

### 工作原理 (按原文梳理)

- **写入路径**: 已完成的 GPU block → 通过 `cudaMemcpyAsync` 异步 DMA 到 pinned host memory (CPU primary tier) → 在多 tier 模式下, CPU 主层进一步下沉到所配置的次级 tier (顺序按 `secondary_tiers` 列表中 tier 0 → tier 1 … 依次写入)。
- **读取路径 (回迁)**: 查找顺序同样是 tier 0 先于 tier 1 (原文: "tier 0 is consulted before tier 1"); 命中后再经 CPU 主层中转上 GPU。
- **触发条件**: `store_threshold` (默认 `0`) 控制一个 block 需要被查找多少次后才允许被卸载。
- **追踪容量**: `max_tracker_size` (默认 `64000`) 限制 lookup tracker 的最大条目数。
- **预填/解码区分**: `offload_prompt_only` (默认 `true`) 控制只卸载预填 (prompt/prefill) block, 跳过解码 (decode) block。
- **异步并行**: GPU↔CPU 传输与模型计算 overlap, 这是"最小 CPU/GPU core 开销"的根源。

### 性能相关数字 (仅汇总原文出现的)

- `cpu_bytes_to_use`: CPU 主层跨**所有 worker** (非 per-worker) 预留的字节数。示例: 单 tier `1000000000` (≈1 GB), 多 tier `10737418240` (≈10 GB)。
- 多 tier FS 示例参数: `n_read_threads: 32`, `n_write_threads: 16`。
- FS tier 默认线程数: `n_read_threads: 16`, `n_write_threads: 16`。
- 默认 `eviction_policy: lru`; 默认 `blocks_per_chunk: 1`; 默认 `max_tracker_size: 64000`。

---

## 【表格解读】

### 表 1: `kv_connector_extra_config` 参考表 (逐字还原)

| Key | Required | Default | Scope | Notes |
| --- | --- | --- | --- | --- |
| `spec_name` | no | `CPUOffloadingSpec` | both | Set to `TieringOffloadingSpec` for multi-tier. |
| `cpu_bytes_to_use` | yes | — | both | Total bytes of host memory reserved for the CPU tier across all workers (not per-worker). |
| `block_size` | no | GPU block size | both | Offloaded block size in tokens; must be a multiple of the GPU block size. Mutually exclusive with `blocks_per_chunk`. |
| `blocks_per_chunk` | no | `1` | both | Offloaded chunk size in GPU blocks; must be > 0. Alternative to `block_size` for models whose KV cache groups have different block sizes. |
| `eviction_policy` | no | `lru` | both | Primary tier policy: built-in `lru`/`arc`, or a custom `CachePolicy` name (see [Custom Eviction Policies](#custom-eviction-policies)). |
| `cache_policy_module_path` | no | — | both | Python import path for a custom `CachePolicy` not in the built-in registry. Required only when `eviction_policy` is not built-in and wasn't pre-registered via `CachePolicyFactory` (advanced). |
| `store_threshold` | no | `0` | single-tier | Min lookups before a block is offloaded. Values ≥ 2 are rejected by `TieringOffloadingSpec`. |
| `max_tracker_size` | no | `64000` | single-tier | Max entries in the lookup tracker. |
| `secondary_tiers` | no | `[]` | multi-tier | List of secondary tier configs (see below). |
| `offload_prompt_only` | no | `true` | both | If `true`, only prompt (prefill) blocks are offloaded; decode blocks are skipped. |
| `self_describing_kv_events` | no | `false` | both | Opt-in. When `true` *and* KV cache events are enabled (`--kv-events-config` with `enable_kv_cache_events`), the connector emits self-describing block-granular `BlockStored`/`BlockRemoved` payloads (constituent block hashes, whole-chunk `token_ids`, per-block `block_size`, parent hash, LoRA + group/cache-spec metadata) instead of the placeholder fallback, so external KV-event consumers can index offloaded blocks. Inert unless events are enabled. With `TieringOffloadingSpec`, a CPU promotion is self-describing when a local request observes its primary-tier `HIT` before event translation; otherwise its stored event may retain the placeholder, while a later `HIT` can backfill metadata for removal. Pending-removal/re-promotion races and externally initiated promotions may also produce placeholders, and consumers must ignore removals for unknown hashes. Partial recurrent tails emit the hash-aligned portion from the physical block start through the tail boundary. Other sliding-window/SSM chunks keep the placeholder fallback. In chunk mode (`block_size` > GPU block size, or `blocks_per_chunk` > 1), overlapping chunks re-announce shared per-block hashes, so consumers must reference-count (deduplicate) repeated store/remove announcements. |
| `spec_module_path` | no | — | both | Python import path for a custom `OffloadingSpec` not in the built-in registry. Required only when `spec_name` is not built-in (advanced). |

**逐行解读**:

- **`spec_name`**: 唯一决定走单层还是多层路径的关键开关; 缺省即进入 `CPUOffloadingSpec`。
- **`cpu_bytes_to_use`**: 唯一一个"required = yes"的核心字段, 注意它是**全局跨 worker** 的总额而非单 worker, 部署多 worker 时需要核算总占用。
- **`block_size` / `blocks_per_chunk`**: 二者提供两种粒度表达, 且**互斥**。`block_size` 直接以 token 数表达, 要求整除 GPU block size; `blocks_per_chunk` 以 GPU block 数为单位, 是给"不同 KV group 有不同 block size"的模型留的退路, 必须 > 0, 缺省为 1 (即最小粒度)。
- **`eviction_policy` / `cache_policy_module_path`**: 组成一对扩展点 — 内建名走 `CachePolicyFactory` 注册表, 找不到再回退到 `cache_policy_module_path` 指定的模块里按类名查找。
- **`store_threshold`**: 限制一个 block 必须被命中查找够次数才被允许卸载, 形成"热 block 留 GPU, 冷 block 才下放"的过滤; 但 `TieringOffloadingSpec` 明确**拒绝 ≥ 2** 的值, 说明多 tier 模式只接受 0 或 1。
- **`max_tracker_size`**: 控制 lookup tracker 上限, 防止冷数据长期占用追踪条目; 仅 single-tier scope。
- **`secondary_tiers`**: `Scope` 为 multi-tier, 缺省空列表即退化为单层。
- **`offload_prompt_only`**: 决定卸载范围, 默认仅卸载预填块, 是为了避免把频繁变化的解码块不断搬运而放大开销。
- **`self_describing_kv_events`**: 这是该表里最长的字段, 描述一个非常细粒度的行为契约 — 不仅开关自身要开, 还要配合 `--kv-events-config` 全局启用才会真正发出自描述事件; 并且列举了多种边界情况下的"占位回退"或"参考计数去重"要求 (多 tier 下非本地请求、pending-removal/race、外部发起的 promotion、部分 recurrent tail、SSM/sliding-window、chunk 模式重叠)。
- **`spec_module_path`**: 与 `cache_policy_module_path` 类似的扩展点, 但用于自定义 `OffloadingSpec` 类, 而非 `CachePolicy`。

### 表 2: Filesystem (FS) tier 配置表 (逐字还原)

| Key | Required | Default | Notes |
| --- | --- | --- | --- |
| `type` | yes | — | Must be `fs`. |
| `root_dir` | yes | — | Base directory; vLLM creates subdirectories beneath it (see [On-Disk Layout](#on-disk-layout)). |
| `n_read_threads` | no | `16` | Read-priority I/O threads (load path). |
| `n_write_threads` | no | `16` | Write-priority I/O threads (store path). |
| `enable_kv_events` | no | `false` | Publish `BlockStored` KV events (medium `FS`) for successfully stored blocks. Requires KV cache events to be enabled globally. |
| `locality` | no | unspecified | `LOCAL` or `REMOTE` relative to the publishing vLLM instance. Included in the tier's KV events only when explicitly configured. |

**逐行解读**:

- **`type` / `root_dir`**: FS tier 的两个强制字段, `type` 必须字面量 `fs`; `root_dir` 是基础目录, vLLM 在其下自建子目录 (具体布局由 "On-Disk Layout" 一节说明, 但原文此处被截断)。
- **`n_read_threads` / `n_write_threads`**: 读写分离的 I/O 线程池, 默认各 16, 在多 tier 示例里被调成读 32 / 写 16, 表明读路径 (命中回迁) 在该示例中被认为更需要带宽。
- **`enable_kv_events`**: FS tier 选择性发布 `BlockStored` 事件, `medium` 标记为 `FS`; 同样依赖全局 KV events 启用才生效。
- **`locality`**: 给消费方描述存储位置语义 (`LOCAL`/`REMOTE`/不指定), 注意 vLLM **不会**根据 tier 类型自动推断 — 比如 OBJ tier 不会隐含 `REMOTE`; 该字段只在显式配置时才出现在事件里, 它"只描述 tier 属性, 不代表消费方已经具备路由到这些 block 的能力"。

---

## 【公式解读】

**原文无公式**。文中没有出现 LaTeX 或伪代码形式的数学公式; 唯一接近"量化"的是以字面量形式给出的字节数与线程数配置项, 已在【关键机制与数据】与【表格解读】中按字段语义解读, 这里不再单列。

---

## 【关联】

文中明确给出的内部链接/类路径锚点如下, 据此可梳理文档所处的"特性网络"位置:

1. **同仓库相关 connector**: 顶部链接 [`OffloadingConnector`](disagg_prefill.md) — `disagg_prefill.md` (disaggregated prefill 文档) 是定义 `OffloadingConnector` 形态的上游页面, 说明该 connector 同时属于 prefix-caching 扩展生态, 与 disaggregated prefill 共享 `kv_connector` 注册框架。
2. **NIXL 传输后端选择**: 文末提供的内部链接 `nixl_connector_usage.md#selecting-a-nixl-transport-backend-plugin` (出现两次), 提示存在并行的 `NixlConnector` 用法文档; Offloading 与 NIXL 虽属不同 connector, 但都属于 vLLM 的 KV-cache 跨设备/跨节点传输栈, 消费方通常需要同时了解两者的 backend 选择 (尤其当考虑把 secondary tier 部署到远程节点时)。
3. **可扩展点上下游**:
   - 上游 (策略/spec 注册): `vllm/v1/kv_offload/cpu/policies/factory.py` 的 `CachePolicyFactory` 是 `eviction_policy` 解析入口, 与 `CachePolicyFactory.register_cache_policy(...)` 提供的进程内短名注册互为表里。
   - 下游 (策略实现): `vllm/v1/kv_offload/cpu/policies/base.py` 中的 `CachePolicy` 基类, 是用户实现自定义淘汰策略时必须实现的契约。
   - 同层级 (`OffloadingSpec`): `spec_module_path` 提供与 `cache_policy_module_path` 平行的扩展机制, 但针对的是 `OffloadingSpec` 类 (而不是 `CachePolicy`), 用于完全替换单/多层行为。
4. **KV 事件链路**: `--kv-events-config` 下的 `enable_kv_cache_events` 是**全局开关**, 它与 tier 级的 `enable_kv_events`、`connector` 级的 `self_describing_kv_events` 形成三层叠加 — 任何一层关闭都会让自描述 payload 退化到占位回退, 这一点决定了文档与 vLLM 的 KV-events 子系统的耦合关系。

---

## 【使用方法】

### 启用方式 (原文给出)

#### 1. 单层 (CPU only) 启动命令

```bash
vllm serve <model> \
  --kv-transfer-config '{
    "kv_connector": "OffloadingConnector",
    "kv_role": "kv_both",
    "kv_connector_extra_config": {
      "block_size": 64,
      "cpu_bytes_to_use": 1000000000
    }
  }'
```

#### 2. 多层 (CPU + FS 次级层) 启动命令

```bash
vllm serve <model> \
  --kv-transfer-config '{
    "kv_connector": "OffloadingConnector",
    "kv_role": "kv_both",
    "kv_connector_extra_config": {
      "spec_name": "TieringOffloadingSpec",
      "cpu_bytes_to_use": 10737418240,
      "block_size": 16,
      "eviction_policy": "lru",
      "secondary_tiers": [
        {
          "type": "fs",
          "root_dir": "/mnt/kv_cache",
          "n_read_threads": 32,
          "n_write_threads": 16
        }
      ]
    }
  }'
```

#### 3. 启用自定义淘汰策略 (out-of-tree, 推荐) — JSON 配置

```json
{
  "cpu_bytes_to_use": 10737418240,
  "eviction_policy": "MyCachePolicy",
  "cache_policy_module_path": "my_package.my_module"
}
```

#### 4. 注册自定义策略短名 (进程内)

```python
from vllm.v1.kv_offload.cpu.policies.factory import CachePolicyFactory

CachePolicyFactory.register_cache_policy("my_policy", "my_package.my_module", "MyCachePolicy")
```

注册后即可在 `kv_connector_extra_config` 中用 `"eviction_policy": "my_policy"`。原文强调这种注册**只在执行注册的那个进程内生效**, 若通过 `vllm serve` CLI 启动独立 server 进程, **必须**走第 3 种 `cache_policy_module_path` 方式。

### 关键配置项速查 (摘自原文, 已合并去重)

- 必填 (除 `spec_name` 外几乎所有场景): `cpu_bytes_to_use` (全局跨 worker 总额)。
- 互斥对: `block_size` ↔ `blocks_per_chunk`。
- 多 tier 必填: `secondary_tiers` (类型列表), 每条带 `type`; `TieringOffloadingSpec` 模式下 `store_threshold` 禁止 ≥ 2。
- 启用自描述 KV 事件: `self_describing_kv_events: true` **且** 同时通过 `--kv-events-config` 启用全局 `enable_kv_cache_events`; tier 级 FS/OBJ 也可单独 `enable_kv_events: true` 发布 `medium` 为 `FS`/`OBJ` 的 `BlockStored` 事件。
- FS tier 可选项: `locality: LOCAL|REMOTE` (不设置则 `locality` 字段不会出现在 KV 事件中)。
- 高级扩展点: `cache_policy_module_path` (自定义 `CachePolicy`)、`spec_module_path` (自定义 `OffloadingSpec`), 均要求字符串为可 import 的 Python 模块路径。

### 关于文档完整性

> 注: 原文末尾在 "Filesystem (FS)" 一节中以 `Eac` 截断, 后续的 On-Disk Layout、其他次级 tier (如 object-store) 配置表等小节内容**原文未提供**, 因此本解读中不对这些未出现部分做推断。
