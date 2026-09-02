# KV Cache 亲和性调度

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/features/kvcache_affinity.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/features/kvcache_affinity.md

# KV Cache 亲和性调度 — 深度解读

## 【定位】

在 PD 分离推理服务基础上，通过自研 Rust 组件 **kv-conductor** 维护全局 KV Cache 前缀树索引，将请求路由到**已缓存最长 token 前缀**的 Worker，从而减少跨实例 KV Cache 传输开销、提升推理吞吐。

---

## 【技术要点】

1. **kv-conductor 组件定位**：Rust 实现、维护全局 KV Cache 前缀树索引三层介质（NPU HBM / CPU / Disk），返回各 DP 的**互斥命中块** `npu_blocks` / `cpu_blocks` / `disk_blocks` 与**未加权覆盖长度** `matched_tokens`（互斥块之和 × `block_size`）。
2. **Coordinator 调度器加权融合**：按 `*_blocks` 与 `scheduler_config.kv_affinity` 中 `w_npu` / `w_cpu` / `w_disk` 等介质权重加权得到亲和匹配长度，再与 endpoint 实时负载 `workload_score` 融合后选路。
3. **两种评分子策略**：
   - `unified`（默认）：单一评分公式，**越低越好**。
   - `load_gated`：先按 `load_gate_topn` 保留负载最低的 N 个 endpoint，再从中选 `matched_tokens` 最大者（并列取负载更低）。
4. **端口注册制 + DP 偏移**：`kv_conductor_config.endpoint` / `replay_endpoint` **无需手工配置**，Coordinator 自动从引擎 `kv-events-config.endpoint`（如 `tcp://*:5557`）推导，启动时按 `dp_rank` 偏移（如 DP0 → 5557、DP1 → 5558）。
5. **构建与打包**：kv-conductor 已集成在 motor Python 包内，随 `build.sh` 条件编译进 wheel；二种获取方式——`KV_CONDUCTOR_PREBUILT=/path/to/kv-conductor` 走预编译，或依赖 cargo 自动 `cargo build --release` 编译；两者皆无则仅输出 `[WARNING]`。
6. **典型参数**：默认 `block_size=128`、DeepSeek V4 / 混合 KV Cache 模型须设为 `512`（与引擎 `--block-size` 一致）；`http_server_port` 默认 `13333`；`w_disk` 默认 `0.0`（不计 Disk）。

---

## 【关键机制与数据】

### 工作原理与数据流

**数据流（原文）**：

> kv-conductor：索引三层介质（NPU HBM / CPU / Disk），查询时返回各 DP 的互斥命中 `npu_blocks` / `cpu_blocks` / `disk_blocks`，以及未加权覆盖长度 `matched_tokens`（互斥块之和 × `block_size`）。
>
> Coordinator 调度器：按 `*_blocks` 与 `scheduler_config.kv_affinity` 中的介质权重加权得到亲和匹配长度，再与 endpoint 实时负载融合后选路。

**推理部署前提（原文）**：必须**已使用 MindIE Motor 部署 PD 分离推理服务**，亲和性调度在该服务之上开启。镜像需包含 kv-conductor 二进制；不部署 Controller / Node Manager 时，详见 [Coordinator 独立部署](../deployment/standalone.md)。

**构建优先级（原文）**：预编译二进制（`KV_CONDUCTOR_PREBUILT`）> cargo 自动编译 > 跳过（仅 `[WARNING]`，kv-conductor 不在 wheel 中，其他功能不受影响）。

**DP 端口偏移机制（原文）**：vLLM 内部按 `data_parallel_rank` 对端口做偏移（DP0 → `tcp://*:5557`、DP1 → `tcp://*:5558`）；Coordinator 注册时按**同样的 DP 秩**将 `*` 替换为 endpoint IP、端口加 `dp_rank`，与 vLLM 实际监听端口一致。

### 性能/数据说明

> **原文未提供具体性能数字（如 TPS 提升幅度、缓存命中率基线等）**，仅定性描述"减少跨实例 KV Cache 传输开销，提升推理吞吐"。

---

## 【表格解读】

### 表 1：子策略行为（原文逐字还原）

| 模式 | 行为 |
|------|------|
| `unified`（默认） | 单一评分（越低越好）= `prefill_load_scale × max(0, isl − overlap_credit × matched_tokens) + load_weight × workload_score` |
| `load_gated` | 先保留负载最低的 N 个 endpoint，再从中选择缓存前缀最长的（`matched_tokens` 最大；并列取负载更低） |

**逐行解读**：
- **unified（默认）**：单一评分，**分越低越优**；公式显式含 `prefill_load_scale`、`overlap_credit`、`matched_tokens`、`load_weight`、`workload_score` 五个变量，是后续调度选路的核心。
- **load_gated**：两阶段选路——第一阶段按 `load_gate_topn` 过滤 Top-N 低负载 endpoint，第二阶段按 `matched_tokens` 倒序、并列时取负载更低者。

### 表 2：`kv_conductor_config`（全局配置，原文逐字还原）

| 配置项 | 类型 | 取值范围 | 说明 |
|--------|------|----------|------|
| **block_size** | uint | ≥ 1 | 事件广播的 hash 粒度（token 数）。须与引擎 `--block-size` / `hash_block_size` 一致。标准模型默认 128；**DeepSeek V4 的取值见 [DeepSeek V4 / 混合 KV Cache 模型](#deepseek-v4)** |
| **http_server_port** | int | 1024–65535 | kv-conductor HTTP API 端口，Coordinator 通过此端口查询缓存命中，默认 `13333` |
| **re_register_interval_sec** | int | ≥ 0 | 周期性重注册间隔（秒），0 或负数禁用（默认 0） |
| **conductor_service** | string | hostname / IP | kv-conductor 服务地址；空则禁用。部署时也可由环境变量注入 |
| **engine_type** | string | 如 `vLLM` | 注册时上报的引擎类型，默认 `vLLM` |
| **model_path** | string | 路径 / 名称 | 注册时的 `modelname` |
| **endpoint** | string | `tcp://*:<port>` | 默认端口模式：`*` 替换为 endpoint IP，端口加 `dp_rank`；注册时写入 `medium_endpoints.npu`。**自动从引擎 `kv-events-config.endpoint` 推导，无需配置** |
| **replay_endpoint** | string | `tcp://*:<port>` | Per-DP replay 端口，conductor 重启恢复时回放缓冲的 KV 事件（可选）。**自动从引擎 `kv-events-config.replay_endpoint` 推导，无需配置** |
| **npu_endpoint** | string | `tcp://*:<port>` | Per-DP HBM（NPU）端口模式的显式覆盖项。**一般无需配置**（见下方端口推导说明），仅在需要覆盖自动推导的默认端口时使用 |

**逐行解读**：
- **block_size**：是 hash 粒度（按 token 数计），**必须**与引擎 `--block-size` / `hash_block_size` 一致；标准模型默认 128，DeepSeek V4 须为 512。
- **http_server_port**：Coordinator 主动查询 kv-conductor 使用的 HTTP API 端口，默认 `13333`。
- **re_register_interval_sec**：周期性重注册间隔；0 或负数即禁用，默认 0。
- **conductor_service**：kv-conductor 服务地址；空字符串表示禁用该参数。
- **engine_type**：注册时上报给 kv-conductor 的引擎类型标签，默认 `vLLM`。
- **model_path**：注册时的 `modelname` 字段值。
- **endpoint**：NPU 介质端口；`*` 在注册时被替换为 endpoint IP，并按 `dp_rank` 加偏移；**由 Coordinator 自动推导**，一般不必手填。
- **replay_endpoint**：Per-DP replay 端口，conductor 重启恢复时用于回放 KV 事件；**亦自动推导**。
- **npu_endpoint**：仅在需要覆盖上述自动推导默认端口时手动指定。

### 表 3：`kv_conductor_config`（L2 二级缓存，原文逐字还原）

| 配置项 | 类型 | 取值范围 | 说明 |
|--------|------|----------|------|
| **pool_endpoint** | string | `tcp://<host>:<port>` | 中心化后端（Mooncake/Memcache）的池服务地址 |
| **cpu_endpoint** | string | `tcp://*:<port>` | Per-DP CPU/DDR 端口 |
| **disk_endpoint** | string | `tcp://*:<port>` | Per-DP DISK/SSD 端口 |
| **store_backend** | string | `Mooncake` / `Memcache` / `YuanRong` | 池化后端类型。Mooncake/Memcache：先注册 pool，再按 DP 注册 `npu`；YuanRong：按 DP 注册 `npu`/`cpu`/`disk` |

**逐行解读**：
- **pool_endpoint**：中心化池服务地址，仅对 Mooncake/Memcache 模式有效。
- **cpu_endpoint** / **disk_endpoint**：Per-DP CPU/DDR 与 DISK/SSD 端口，启用 CPU/Disk 二级缓存时使用。
- **store_backend**：选 `Mooncake` / `Memcache` 时按"先注册 pool，再按 DP 注册 `npu`"；选 `YuanRong` 时直接按 DP 注册 `npu`/`cpu`/`disk` 三层。

### 表 4：`scheduler_config` 调度器亲和性参数（原文逐字还原）

| 配置项 | 类型 | 取值范围 | 说明 |
|--------|------|----------|------|
| **scheduler_type** | string | `kv_cache_affinity` | 启用 KV Cache 亲和性调度 |
| **kv_affinity.mode** | string | `unified` / `load_gated` | 评分子策略，默认 `unified` |
| **kv_affinity.load_weight** | float | `[0, +∞)` | `unified` 下 endpoint 实时负载权重。`1.0`（默认）与亲和折扣后的 prefill 成本同等重要；`0` 表示纯亲和性 |
| **kv_affinity.overlap_credit** | float | `[0, +∞)` | 缓存前缀对 prefill 成本的折扣系数。值越大，已缓存前缀折扣越高。默认 `1.0` |
| **kv_affinity.prefill_load_scale** | float | `[0, +∞)` | `unified` 下亲和折扣后的 prefill 成本权重。默认 `1.0` |
| **kv_affinity.load_gate_topn** | int | `[0, +∞)` | `load_gated` 下保留负载最低的 N 个 endpoint。`0` 时回退为 `2`（默认 `0`） |
| **kv_affinity.w_npu** | float | `[0, +∞)` | 互斥 NPU 命中块权重。默认 `1.0` |
| **kv_affinity.w_cpu** | float | `[0, +∞)` | 互斥 CPU 命中块权重。默认 `1.0` |
| **kv_affinity.w_disk** | float | `[0, +∞)` | 互斥 Disk 命中块权重。默认 `0.0`（默认不计 Disk） |

**逐行解读**：
- **scheduler_type**：固定为 `kv_cache_affinity`，作为开关。
- **kv_affinity.mode**：选 `unified`（单评分）或 `load_gated`（两阶段过滤），默认 `unified`。
- **kv_affinity.load_weight**：仅在 `unified` 下生效；`1.0` 时负载与折扣后 prefill 成本等权，`0` 退化为纯亲和。
- **kv_affinity.overlap_credit**：值越大，已缓存前缀对 prefill 成本折扣越多，默认 `1.0`。
- **kv_affinity.prefill_load_scale**：仅在 `unified` 下生效；折扣后 prefill 成本项的权重，默认 `1.0`。
- **kv_affinity.load_gate_topn**：仅在 `load_gated` 下生效；`0` 自动回退为 `2`。
- **kv_affinity.w_npu/w_cpu**：NPU / CPU 介质命中块权重，默认均为 `1.0`。
- **kv_affinity.w_disk**：Disk 命中块权重，**默认 `0.0`**——即默认不计 Disk 命中。

### 表 5：`kv-events-config`（引擎侧，原文逐字还原）

| 配置项 | 类型 | 取值范围 | 说明 |
|--------|------|----------|------|
| **publisher** | string | `zmq` | 事件发布后端，当前仅支持 `zmq` |
| **enable_kv_cache_events** | bool | `true` / `false` | 是否启用 KV Cache 事件，设为 `true` |
| **endpoint** | string | `tcp://*:<port>` | P 实例发布 KV 事件的 ZMQ 端点 |
| **topic** | string | 自定义 | 事件 ZMQ 主题 |
| **replay_endpoint** | string | `tcp://*:<port>` | 事件回放端点，供 conductor 重启后恢复索引（可选） |

**逐行解读**：
- **publisher**：当前仅支持 ZMQ。
- **enable_kv_cache_events**：开启后 P 实例才会向 kv-conductor 推送事件。
- **endpoint**：P 实例发布 KV 事件的 ZMQ 端点，Coordinator 自动据此推导 `kv_conductor_config.endpoint`。
- **topic**：自定义事件主题，区分不同业务流。
- **replay_endpoint**：可选事件回放端点，conductor 重启后用其回放缓冲事件以恢复索引。

---

## 【公式解读】

### 公式 1：`unified` 子策略评分（**原文逐字保留**）

```text
prefill_load_scale × max(0, isl − overlap_credit × matched_tokens) + load_weight × workload_score
```

**符号含义与解读**：

| 符号 | 含义与作用 |
|------|-------------|
| `prefill_load_scale` | `unified` 下亲和折扣后的 prefill 成本权重（`scheduler_config.kv_affinity.prefill_load_scale`，默认 `1.0`）。值越大，最终评分越偏向亲和折扣后的 prefill 成本。 |
| `max(0, …)` | 下界截断——若折扣后 prefill 成本已无剩余（即 `isl ≤ overlap_credit × matched_tokens`），该项退化为 0，避免负分。 |
| `isl` | 输入序列长度（input sequence length），即本次请求的 prompt token 总数（原文未明确定义，按公式语义推断为请求 token 总量）。 |
| `overlap_credit` | 已缓存前缀对 prefill 成本的折扣系数（`scheduler_config.kv_affinity.overlap_credit`，默认 `1.0`）。值越大，缓存命中贡献的"减免"越多。 |
| `matched_tokens` | 未加权覆盖长度，由 `npu_blocks` / `cpu_blocks` / `disk_blocks`（互斥命中块）× `block_size` 计算得到（原文明确：互斥块之和 × `block_size`）。 |
| `load_weight` | endpoint 实时负载权重（`scheduler_config.kv_affinity.load_weight`，默认 `1.0`）。`0` 表示纯亲和性（无视负载）。 |
| `workload_score` | endpoint 实时负载评分（原文未给出具体形式，由 Coordinator 端实时统计推断，越高表示越忙）。 |

**整体语义**：评分越低越优；前半段表示"扣除缓存命中后的有效 prefill 成本"，后半段表示"endpoint 负载惩罚"。`load_weight=0` 即纯亲和，`prefill_load_scale=0` 即只看负载。

### 公式 2：`load_gated` 子策略选路（**原文逐字保留**）

```text
先保留负载最低的 N 个 endpoint，再从中选择缓存前缀最长的（matched_tokens 最大；并列取负载更低）
```

**符号含义与解读**：

| 符号 | 含义与作用 |
|------|-------------|
| `N` | `scheduler_config.kv_affinity.load_gate_topn`，保留的负载最低 endpoint 数；`0` 自动回退为 `2`。 |
| 排序键 1 | `matched_tokens`（= 互斥命中块 × `block_size`），倒序取最大。 |
| 排序键 2（并列时） | endpoint 实时负载，更低者优先。 |

**整体语义**：两阶段硬过滤；候选集与亲和度的解耦，避免负载高的 endpoint 被命中缓存前缀但被压垮。

> 注：原文示例块 `block_size: 128`、`http_server_port: 13333` 在 PD 分离配置与 PD 混部配置两段 JSON 中均出现；`kv-events-config` 的端口默认 `5557`（事件）/ `6667`（replay）。

---

## 【关联】

| 关联项 | 关系说明 |
|--------|----------|
| [Coordinator 独立部署](../deployment/standalone.md) | 当不部署 Controller / Node Manager 时，kv-conductor 通过 `python -m motor.kv_conductor` 启动，参考该独立部署文档。 |
| [MindIE Motor 快速开始](../quick_start.md) | 亲和性调度需在 PD 分离推理服务之上开启，前置要求为基础服务已正常部署，文中"PD 分离配置"即以该文档为基线。 |
| [KV Cache Store](kv_cache_store/README.md) | KV Cache Store **池化**功能单独通过 `kv_cache_store_config` 开启；本文中 `pool_endpoint` / `cpu_endpoint` / `disk_endpoint` / `store_backend` 等 L2 二级缓存参数即为该池化后端的接入点。 |
| [PD 混部服务部署](../deployment/k8s/pd_aggregation_deployment.md) | PD 混部（`motor_engine_union_config`）启用亲和性的部署细节详见该文档，本文只展示 union 段增量。 |
| DeepSeek V4 / 混合 KV Cache 模型 | 要求 `--block-size` 与 `kv_conductor_config.block_size` **均为 512**；二者任一不一致将导致 conductor 查询命中率始终为 0。 |
| `max_tokens_adaptation.md` | 列在内部链接清单，但本文档正文未引用该文档。 |

---

## 【使用方法】

### 1. 启用基础服务
- 已使用 motor 部署 PD 分离推理服务且正常运行（详见 [快速开始](../quick_start.md)）。
- K8s 集群管理节点（master 节点）执行后续操作。

### 2. 构建 kv-conductor（二选一 / 三优先级）

```bash
# 方式 1：使用预编译二进制（推荐，无需 Rust 工具链）
KV_CONDUCTOR_PREBUILT=/path/to/kv-conductor bash build.sh

# 方式 2：有 cargo 环境
bash build.sh   # 自动 cargo build --release 并打包

# 方式 3：两者皆无 → 仅 [WARNING]，kv-conductor 不在 wheel 中
```

> 使用官方发布镜像时，二进制已随 wheel 打包，上述均无需关心。

### 3. 修改 `user_config.json`

在 `examples/infer_engines/vllm/user_config.json` 中：

- `motor_coordinator_config.scheduler_config.scheduler_type` → `"kv_cache_affinity"`
- `motor_engine_prefill_config.engine_config` → 增加 `kv-events-config`
- 新增顶层 `kv_conductor_config`

完整 PD 分离 / PD 混部示例 JSON 见原文「典型配置」节；`kv_affinity` 子参数（`mode` / `load_weight` / `overlap_credit` / `prefill_load_scale` / `w_npu` / `w_cpu` / `w_disk` 等）**均有默认值**，示例中无需配置。

### 4. 部署服务

```bash
cd examples/deployer
# 方式一：指定配置目录（推荐）
python deploy.py --config_dir ../infer_engines/vllm

# 方式二：单独指定配置文件
python deploy.py --user_config_path ../infer_engines/vllm/user_config.json \
                 --env_config_path     ../infer_engines/vllm/env.json
```

### 5. 验证

```bash
kubectl get pod -A -o wide
```

预期 P/D 实例与 kv-conductor 均启动成功；**Coordinator 日志中可见 "KV Conductor registered" 字样**。

### 6. DeepSeek V4 / 混合 KV Cache 模型

```json
"kv_conductor_config": { "block_size": 512 }
```

```bash
vllm serve ... --block-size 512
```

> 必须**两端一致**，否则 conductor 查询命中率始终为 0；引擎启动日志会打印实际 `hash_block_size` 可用于确认。
