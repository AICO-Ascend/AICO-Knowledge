# MooncakeStoreConnector Usage Guide

> 仓 `vllm` · 路径 `docs/features/mooncake_store_connector_usage.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/mooncake_store_connector_usage.md

# MooncakeStoreConnector Usage Guide —— 深度解读

## 【定位】

这篇文档解决"如何在 vLLM 中通过 Mooncake 的分布式 KV 缓存池实现跨实例 KV 共享与 CPU/磁盘卸载"的问题,描述的是 `MooncakeStoreConnector` 这一 KV cache connector 能力,以及它与 `MooncakeConnector` 在 disaggregated prefill-decode 场景中的协同使用方法。

---

## 【技术要点】

1. **三类核心能力**:CPU/磁盘 offloading(通过 Mooncake transfer engine 扩展有效 KV 容量)、跨实例 prefix caching(基于哈希去重共享 KV block)、单机与多节点部署(standalone KV cache 扩展 + 分离式 prefill-decode)。

2. **两种拓扑模式**:`"embedded"`(默认)——每个 vLLM rank 在进程内贡献 `global_segment_size` 大小的内存到共享池;`"standalone-store"`——vLLM rank 仅为 requester,外部 `mooncake_client` 进程独占 CPU pool 与(可选)SSD tier,避免每 rank 重复 SSD pool。

3. **Mooncake 主控(Master)**:通过 `mooncake_master --port 50051` 启动,默认 RPC 端口 50051,管理元数据并协调分布式存储,多个 vLLM 实例可共享同一 master。

4. **传输协议**:`"rdma"` 性能最佳,`"tcp"` 作为兜底回退。

5. **Disaggregated Prefill-Decode(XpYd)集成**:通过 `MultiConnector` 同时挂载 `MooncakeConnector`(点对点 KV 传输)与 `MooncakeStoreConnector`(共享 KV 池)——prefill 端用 `MultiConnector` + `kv_producer`,decode 端用 `MultiConnector` + `kv_both`/`kv_consumer`;需配合 disaggregation proxy 设置 `do_remote_prefill=True`/`do_remote_decode=True`。

6. **租户隔离(Tenant Isolation)**:通过 `tenant_id` 划分 Mooncake 命名空间,严格隔离需 master 启用 `--enable_multi_tenants=true` 并注册 tenant 配额策略;非默认 `tenant_id` 要求 Mooncake 版本的 `MooncakeDistributedStore.setup()` 接受 `tenant_id` 参数;`standalone-store` 模式下外部 `mooncake_client` 也需匹配同一 tenant id。

---

## 【关键机制与数据】

- **运行时数据流(Single-node KV cache offloading)**:原文展示通过 `MOONCAKE_CONFIG_PATH=mooncake_config.json` + `--kv-transfer-config '{"kv_connector":"MooncakeStoreConnector","kv_role":"kv_both"}'` 即可将 KV cache offload 到 CPU 内存,扩展有效缓存容量。

- **磁盘 Offloading 三方对齐**(原文明确要求):
  1. `mooncake_master` 启动时带 `--enable_offload=true`;
  2. `mooncake_client`(作为 owner)启动时带 `--enable_offload=true` 并设置 `MOONCAKE_OFFLOAD_FILE_STORAGE_PATH` 指向 SSD 路径;
  3. vLLM 侧在 JSON 配置中设置 `"enable_offload": true`(由 connector 读取,**非环境变量**)。

- **Decode 端前缀回填机制**(原文):decode 启动时,consumer 检查 block-aligned 的 prompt prefix,从 Store 补齐缺失的 block;后续 save 阶段追加新完成的 decode block;以此维持一个完整、可复用的 prefix,同时覆盖 prompt KV 由 `MooncakeConnector` 直接投递(而非经 Store)的部署场景。

- **Decode 端缓存持久化扩展**:在 decoder 的 `MooncakeStoreConnector` entry 中加入 `{"save_decode_cache": true}`,可将新完成的 decode KV block 一并持久化;前置条件是 prefill/decode 实例使用相同的 tensor-parallel size 与兼容的 KV-cache topology。

- **Standalone-store 路由**(原文):通过 `export MOONCAKE_PREFERRED_SEGMENT=127.0.0.1:50053` 将该 rank 的副本固定到本地 owner segment;SSD 目录、磁盘淘汰策略、DirectIO staging buffer 大小由 `mooncake_client` 侧通过 `MOONCAKE_OFFLOAD_FILE_STORAGE_PATH`、`MOONCAKE_BUCKET_EVICTION_POLICY`、`MOONCAKE_USE_URING`、`MOONCAKE_OFFLOAD_LOCAL_BUFFER_SIZE_BYTES`、`MOONCAKE_OFFLOAD_TOTAL_SIZE_LIMIT_BYTES` 等标准环境变量控制,与 vLLM JSON config 独立。

- **配置示例参数(原文 embedded 模式)**: `global_segment_size`: "80GB"(每 GPU),`local_buffer_size`: "4GB"(每 GPU),`protocol`: "rdma",`master_server_address`: "127.0.0.1:50051"。

---

## 【表格解读】

原文无独立的"参数表/性能对比表",仅有一个 **Environment Variables 表**,逐字还原如下:

| Variable | Description | Default |
| --- | --- | --- |
| `MOONCAKE_CONFIG_PATH` | Path to Mooncake JSON config file | (required) |
| `VLLM_MOONCAKE_BOOTSTRAP_PORT` | Bootstrap port for MooncakeConnector P2P transfer (disagg mode only) | 8998 |
| `MOONCAKE_PREFERRED_SEGMENT` | Pin this rank's replicas to a specific owner segment (`host:port`); used in `standalone-store` mode | — |
| `MOONCAKE_REQUESTER_LOCAL_HOSTNAME` | Override the hostname the vLLM rank registers with Mooncake as a requester. Defaults to the rank's resolved IP. | — |
| `VLLM_MOONCAKE_STORE_TIER_LOG` | When `1`, logs a per-batch tier summary (memory vs disk hits) for observability | disabled |

逐行解读:
- **`MOONCAKE_CONFIG_PATH`(必填)**:指向 Mooncake JSON 配置文件路径;vLLM 启动时通过该环境变量加载 Mooncake 拓扑/协议/容量等配置,文档所有示例命令均以该变量前置。
- **`VLLM_MOONCAKE_BOOTSTRAP_PORT`(默认 8998)**:专用于 disagg 模式下的 `MooncakeConnector` 点对点握手端口;与配置中 `kv_connector_extra_config` 的 bootstrap 行为配合(原文 Prefiller 用 50052、Decoder 用 50053 为覆写示例)。
- **`MOONCAKE_PREFERRED_SEGMENT`(默认无)**:在 `standalone-store` 模式下将本 rank 的副本固定到特定 owner 的 `host:port`,避免副本被路由到非预期的 owner 段,典型用法见 `127.0.0.1:50053`。
- **`MOONCAKE_REQUESTER_LOCAL_HOSTNAME`(默认无,fallback 为 rank 解析 IP)**:当 vLLM rank 向 Mooncake 注册自身为 requester 时,可手动覆盖其声明的主机名,以避免多网卡/DNS 解析异常带来的注册失败。
- **`VLLM_MOONCAKE_STORE_TIER_LOG`(默认 disabled)**:开启为 `1` 时,每 batch 输出一行 tier summary(memory 命中 vs disk 命中),用于在 CPU/磁盘分层存储中观测命中率。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **`MooncakeConnector`**(内部链接 `mooncake_connector_usage.md`):负责 prefiller ↔ decoder 之间的**点对点** KV 传输;与 `MooncakeStoreConnector` 通过 `MultiConnector` 组合使用,在 disagg 场景下由 proxy 设置 `do_remote_prefill=True` / `do_remote_decode=True` 协同调度。
- **`MultiConnector`**:vLLM 中允许多个 KV connector 共存的容器,在 XpYd 中同时挂载 `MooncakeConnector`(`kv_producer`/`kv_consumer`)与 `MooncakeStoreConnector`(`kv_both`/`kv_consumer`)。
- **`MooncakeDistributedStore`**(外部 [kvcache-ai/Mooncake](https://github.com/kvcache-ai/Mooncake)):作为共享 KV cache pool 的底层存储引擎,提供哈希去重的 prefix 共享与 transfer engine;`setup()` 需接受 `tenant_id` 参数(在非默认租户场景)。
- **`mooncake_master`**(独立进程):管理元数据、协调分布式存储;启用 `--enable_offload=true` 以支持磁盘 offload;严格租户隔离需 `--enable_multi_tenants=true`。
- **`mooncake_client`**(独立进程):`standalone-store` 模式下的 store owner,独占 CPU pool 与(可选)SSD tier,通过 `MOONCAKE_OFFLOAD_FILE_STORAGE_PATH` 等环境变量控制 SSD 目录、淘汰策略、DirectIO staging buffer。
- **Disaggregation proxy**:负责在 prefiller/decoder 之间路由请求,设置 `do_remote_prefill=True`/`do_remote_decode=True` 来触发 P2P KV 传输;详细 setup 见 `mooncake_connector_usage.md`(文末内部链接)。

---

## 【使用方法】

**1. 安装与启动 Master**

```bash
uv pip install mooncake-transfer-engine
mooncake_master --port 50051
```

**2. JSON 配置示例(embedded 模式,纯 CPU 卸载)**

```json
{
  "mode": "embedded",
  "metadata_server": "P2PHANDSHAKE",
  "master_server_address": "127.0.0.1:50051",
  "global_segment_size": "80GB",
  "local_buffer_size": "4GB",
  "protocol": "rdma",
  "device_name": "",
  "enable_offload": false
}
```

导出配置路径:`export MOONCAKE_CONFIG_PATH=/path/to/mooncake_config.json`。

**3. 单节点 KV 卸载**

```bash
MOONCAKE_CONFIG_PATH=mooncake_config.json \
vllm serve meta-llama/Llama-3.1-8B-Instruct \
    --kv-transfer-config '{"kv_connector":"MooncakeStoreConnector","kv_role":"kv_both"}'
```

**4. Disaggregated Prefill-Decode(XpYd)**

Prefiller(端口 8100,bootstrap 50052,`kv_producer`,组合 P2P + Store):

```bash
MOONCAKE_CONFIG_PATH=mooncake_config.json \
VLLM_MOONCAKE_BOOTSTRAP_PORT=50052 \
vllm serve meta-llama/Llama-3.1-8B-Instruct \
    --port 8100 \
    --kv-transfer-config '{
        "kv_connector": "MultiConnector",
        "kv_role": "kv_producer",
        "kv_connector_extra_config": {
            "connectors": [
                {"kv_connector": "MooncakeConnector",      "kv_role": "kv_producer"},
                {"kv_connector": "MooncakeStoreConnector", "kv_role": "kv_both"}
            ]
        }
    }'
```

Decoder(端口 8200,bootstrap 50053,`kv_consumer`,并可启用 `save_decode_cache`):

```bash
MOONCAKE_CONFIG_PATH=mooncake_config.json \
VLLM_MOONCAKE_BOOTSTRAP_PORT=50053 \
vllm serve meta-llama/Llama-3.1-8B-Instruct \
    --port 8200 \
    --kv-transfer-config '{
        "kv_connector": "MultiConnector",
        "kv_role": "kv_consumer",
        "kv_connector_extra_config": {
            "connectors": [
                {"kv_connector": "MooncakeConnector",      "kv_role": "kv_consumer"},
                {"kv_connector": "MooncakeStoreConnector", "kv_role": "kv_consumer"}
            ],
            "save_decode_cache": true
        }
    }'
```

**5. 磁盘 Offloading(standalone-store 模式)**

- vLLM 侧配置:`"mode": "standalone-store"`,`"global_segment_size": 0`,`"enable_offload": true`,`"device_name": "mlx5_0"`;
- 路由固定:`export MOONCAKE_PREFERRED_SEGMENT=127.0.0.1:50053`;
- 外部对齐:`mooncake_master --enable_offload=true`;`mooncake_client` 启动时带 `--enable_offload=true` 与 `MOONCAKE_OFFLOAD_FILE_STORAGE_PATH`(SSD 目录、淘汰策略、DirectIO staging buffer 大小均在 `mooncake_client` 侧通过 `MOONCAKE_BUCKET_EVICTION_POLICY`、`MOONCAKE_USE_URING`、`MOONCAKE_OFFLOAD_LOCAL_BUFFER_SIZE_BYTES`、`MOONCAKE_OFFLOAD_TOTAL_SIZE_LIMIT_BYTES` 等设置)。

**6. 租户隔离**

在 JSON 中追加 `"tenant_id": "tenant-a"`;严格隔离需 `mooncake_master --enable_multi_tenants=true` 并注册 tenant 配额策略;`standalone-store` 模式下外部 `mooncake_client` 需以匹配的 tenant id 启动。

**7. 可观测性**

设置 `export VLLM_MOONCAKE_STORE_TIER_LOG=1` 启用每 batch memory vs disk 命中汇总日志(默认 disabled)。
