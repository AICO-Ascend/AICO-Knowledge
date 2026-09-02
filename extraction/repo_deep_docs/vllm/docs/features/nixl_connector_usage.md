# NixlConnector Usage Guide

> 仓 `vllm` · 路径 `docs/features/nixl_connector_usage.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/nixl_connector_usage.md

# NixlConnector Usage Guide 一体化深度解读

---

## 【定位】

这篇文档描述了 vLLm 的 **NixlConnector**：基于 NIXL 库的 KV cache 跨进程传输连接器,用于支撑 vLLM 的**分离式预填充 (disaggregated prefilling)** 架构,涵盖基础 P/D (Prefill/Decode) 部署、双向 KV 传输 (multi-turn)、传输后端选择、握手端口与租约/TTL 等关键运维参数。

---

## 【技术要点】

1. **底层传输库**:基于 [NIXL](https://github.com/ai-dynamo/nixl) 库实现**完全异步**的 send/receive KV cache 传输;NIXL 默认 transport 后端是 **UCX**,可通过 `kv_connector_extra_config.backends` 切换其他 plugin(如 LIBFABRIC)。
2. **角色模型**:分为 **kv_producer (Prefill)** 与 **kv_consumer (Decode)** 两种角色,通过 `--kv-transfer-config` 中的 `kv_role` 指定;典型部署使用 `CUDA_VISIBLE_DEVICES=0/1` 在同一节点划分两张 GPU。
3. **Side-channel 握手**:Prefill 与 Decode 通过 `VLLM_NIXL_SIDE_CHANNEL_PORT`/`VLLM_NIXL_SIDE_CHANNEL_HOST` 建立初始握手,Prefill 把连接信息 (`engine ID`、host/port) 通过 `KVTransferParams` 传给 Decode 用于握手。
4. **租约与 TTL 机制**:`kv_lease_duration`(默认 **30** 秒)在 Prefill 端持有已生成的 KV blocks 等待 Decode 读取,期间由心跳自动续期;`decoder_kv_blocks_ttl`(默认 **480** 秒)控制 Decoder 在双向传输模式下缓存的 KV 存活时间,**不通过心跳续期**。
5. **DP/TP 端口推导公式**:每个 worker 的 side-channel 端口为 `base_port + dp_rank`,例如 `--data-parallel-size=2`、base_port=5600 → dp_rank 0/1 分别使用 5600/5601;同端口号在不同 host 上可复用。
6. **双向 KV 传输 (Multi-turn)**:在多轮对话场景下,通过**有状态代理 (stateful proxy)** 缓存 `kv_transfer_params`,使 Prefill 在后续轮次可通过 **RDMA read 从 Decode 拉取**已有 KV blocks,只计算新增 token,从而显著降低 TTFT。

---

## 【关键机制与数据】

### 工作原理(数据流)
- **Turn 1 (cache miss)**:Client→Proxy→P(full prefill)→Proxy 收到 P 的 `kv_transfer_params`→转发给 D,D **通过 RDMA 从 P 拉取** KV→D 流式回包并附带自己的 `kv_transfer_params`→Proxy 按 `conversation_id` 缓存 D 的传输参数。
- **Turn 2+ (cache hit, bidirectional)**:Proxy 命中缓存→请求附带 D 的 `remote_block_ids`→P **通过 RDMA 从 D 拉取**已有 KV→P 仅 prefill 新 token→之后 D 再通过 RDMA 从 P 拉取新生成 token 的 KV。
- **传输机制**:全程 P2P 拉取 (RDMA read),由 Proxy 维护 `conversation_id` ↔ `kv_transfer_params` 的映射。

### 关键性能/配置参数(原文)
| 参数 | 默认值 | 说明 |
|---|---|---|
| `VLLM_NIXL_SIDE_CHANNEL_PORT` | 5600 | Prefill/Decode 实例均需;NIXL 初始握手端口 |
| `VLLM_NIXL_SIDE_CHANNEL_HOST` | localhost | Prefill/Decode 跨机时设置 |
| `kv_lease_duration` | **30 秒** | Prefill 端 KV blocks 持有时间,带心跳续期 |
| `decoder_kv_blocks_ttl` | **480 秒** | Decoder 双向模式下缓存 KV 存活时间,不带心跳续期 |

> 原文未提供具体的 TTFT/吞吐性能数字,只定性描述"significantly reducing TTFT for long-prefill such as multi-turn heavy scenarios"。

### Mermaid 时序图
原文中包含一张 `sequenceDiagram`,完整标注了 Turn 1 与 Turn 2+ 的双向 RDMA 交互细节(`Client/Proxy/P/D` 四方参与者,缓存命中/未命中两个 rect 块)。

---

## 【表格解读】

**原文无表格**。

(原文以代码块、嵌套列表与 mermaid 序列图为主要表达形式,环境变量部分以分层 bullet 形式呈现,不存在 markdown 表格结构。)

---

## 【公式解读】

**原文无数学公式**,但包含一个**端口推导表达式**:

$$\text{worker\_port} = \text{base\_port} + \text{dp\_rank}$$

**符号含义**:
- `base_port`:由 `VLLM_NIXL_SIDE_CHANNEL_PORT` 设置的基准端口(默认 5600)。
- `dp_rank`:数据并行的 worker 编号,取值范围 `[0, data_parallel_size)`。
- `worker_port`:该 DP worker 实际使用的 side-channel 监听端口。

**作用**:用于 TP/DP 部署下自动为同一节点上的多个 vLLM worker 分配**唯一**的 NIXL 握手端口;同一端口号在不同 host 上可重复使用,因为握手信息中还会携带 host/engine ID 用于区分。

---

## 【关联】

### 配套文档
- **[NixlConnector Compatibility Matrix](nixl_connector_compatibility.md)**:描述支持的模型架构、TP 配置与特性交互(原文明确指引)。
- **[NIXL 官方仓库](https://github.com/ai-dynamo/nixl)**:底层传输库,提供 backend plugin 列表与构建说明。

### 构建/依赖
- **[requirements/kv_connectors.txt](../../requirements/kv_connectors.txt)**:指定所需 NIXL 版本。
- **[docker/Dockerfile.rocm](../../docker/Dockerfile.rocm)**:ROCm 平台下从源码构建 NIXL + UCX(ROCm 支持)。
- **`tools/install_nixl_from_source_ubuntu.py`**:非 CUDA 平台从源码安装 NIXL + UCX 的脚本。

### 测试与基准
- **[tests/v1/kv_connector/nixl_integration/toy_proxy_server.py](../../tests/v1/kv_connector/nixl_integration/toy_proxy_server.py)**:基础 P/D 部署使用的演示代理服务器(原文 Basic Usage 章节直接引用其启动命令)。
- **[tests/v1/kv_connector/nixl_integration/run_accuracy_test.sh](../../tests/v1/kv_connector/nixl_integration/run_accuracy_test.sh)** + **[test_accuracy.py](../../tests/v1/kv_connector/nixl_integration/test_accuracy.py)**:NixlConnector 的精度集成测试。
- **[benchmarks/multi_turn/benchmark_serving_multi_turn.py](../../benchmarks/multi_turn/benchmark_serving_multi_turn.py)**:多轮场景基准测试,与本文档双向 KV 传输章节对应。

### 上游
- **NIXL (ai-dynamo/nixl)**:本文档核心依赖。
- **UCX**:默认 transport 后端;相关环境变量 `UCX_TLS`、`UCX_NET_DEVICES` 与 NCCL 的 `NCCL_IB_HCA`/`NCCL_SOCKET_IFNAME` **不可混用**(原文 tip 明确指出)。

---

## 【使用方法】

### 安装
```bash
# Nvidia 平台快速开始
uv pip install nixl
# 非 CUDA 平台从源码构建
python tools/install_nixl_from_source_ubuntu.py
```

### UCX Transport 配置
```bash
export UCX_TLS=all   # 或 "rc,ud,sm,^cuda_ipc" 等具体组合
export UCX_NET_DEVICES=all  # 或 "mlx5_0:1,mlx5_1:1"
```

### 切换 Backend (例: LIBFABRIC)
```bash
vllm serve <MODEL> \
  --kv-transfer-config '{
    "kv_connector":"NixlConnector",
    "kv_role":"kv_producer",
    "kv_connector_extra_config":{"backends":["LIBFABRIC"]}
  }'
```
或以 dotted 形式:
```bash
vllm serve <MODEL> \
  --kv-transfer-config.kv_connector NixlConnector \
  --kv-transfer-config.kv_role kv_producer \
  --kv-transfer-config.kv_connector_extra_config.backends+ LIBFABRIC
```

### Prefiller (Producer) 启动
```bash
CUDA_VISIBLE_DEVICES=0 \
UCX_NET_DEVICES=all \
VLLM_NIXL_SIDE_CHANNEL_PORT=5600 \
vllm serve Qwen/Qwen3-0.6B \
  --port 8100 \
  --enforce-eager \
  --kv-transfer-config '{"kv_connector":"NixlConnector","kv_role":"kv_producer","kv_load_failure_policy":"fail"}'
```

### Decoder (Consumer) 启动
```bash
CUDA_VISIBLE_DEVICES=1 \
UCX_NET_DEVICES=all \
VLLM_NIXL_SIDE_CHANNEL_PORT=5601 \
vllm serve Qwen/Qwen3-0.6B \
  --port 8200 \
  --enforce-eager \
  --kv-transfer-config '{"kv_connector":"NixlConnector","kv_role":"kv_consumer","kv_load_failure_policy":"fail"}'
```

### Proxy 启动
```bash
python tests/v1/kv_connector/nixl_integration/toy_proxy_server.py \
  --port 8192 \
  --prefiller-hosts localhost \
  --prefiller-ports 8100 \
  --decoder-hosts localhost \
  --decoder-ports 8200
```

### 租约 / TTL 调优示例
```bash
# Prefill 端 lease 延长到 60 秒
--kv-transfer-config '{"kv_connector_extra_config": {"kv_lease_duration": 60}}'
# Decoder 端双向缓存 TTL 延长到 600 秒
--kv-transfer-config '{"kv_connector_extra_config": {"decoder_kv_blocks_ttl": 600}}'
```

> 注:原文在 Turn 2+ (cache hit) 步骤详解处**于 "Proxy looks up cached `kv_transfer_params` f" 处截断**,如需完整双向流程第 2 步之后的内容,需查阅后续原文补全。
