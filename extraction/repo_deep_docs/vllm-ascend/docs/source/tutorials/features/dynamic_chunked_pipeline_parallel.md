# Dynamic Chunked Pipeline Parallel (DeepSeek-V3.1)

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/features/dynamic_chunked_pipeline_parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/features/dynamic_chunked_pipeline_parallel.md

# Dynamic Chunked Pipeline Parallel (CPP) 文档深度解读

## 【定位】

本文档介绍 vLLM-Ascend 中 Dynamic Chunked Pipeline Parallel (CPP) 特性在 **Prefill-Decode (PD) 分离部署** 场景下的使用方法，通过基于 profiling 数据动态计算最优 chunk size，降低 Pipeline Parallel 场景下 P 节点处理长序列时的 **Time-To-First-Token (TTFT)**，并以 DeepSeek-V3.1 在 Atlas 800T A3 上的部署为示范案例。

---

## 【技术要点】

1. **适用场景限定**：CPP 仅用于 PD 分离部署中的 P（Prefiller）节点，D（Decoder）节点无需 CPP 配置；自 `v0.19.1rc1` 版本起支持。
2. **硬件与模型**：使用 `DeepSeek-V3.1-W8A8`（量化版），单节点 `1 × Atlas 800T A3 (64GB × 16)`；示范拓扑为 3 台 Atlas 800T A3 服务器（1 个 P 节点 + 2 个 D 节点，D 节点为 DP32 标准配置）。
3. **KV 传输组件**：推荐使用 `MooncakeConnectorV1` 作为 `kv_connector`，并以 `kv_role` 在 P 节点设为 `kv_producer`、D 节点设为 `kv_consumer`。
4. **推荐配置**：建议在 PP 的 P 节点上 **不启用** `async-scheduling`（避免 prefill 阶段性能下降）；启用 `--enable-chunked-prefill` 与 `--enable-prefix-caching`。
5. **CPP 专属 profiling 配置**：通过 `--additional-config` 注入 `scheduler_config.profiling_chunk_config`，核心参数为 `enabled: true`、`smooth_factor: 1.0`、`min_chunk: 4096`。
6. **并行规模参数**：P 节点 `--tensor-parallel-size 8`、`--pipeline-parallel-size 2`、`--enable-expert-parallel`；KV 配置侧 `prefill.pp_size=2, dp_size=1, tp_size=8`，`decode.dp_size=32, tp_size=1`。
7. **网络与运行控制**：通过 `HCCL_IF_IP`/`GLOO_SOCKET_IFNAME`/`TP_SOCKET_IFNAME`/`HCCL_SOCKET_IFNAME` 绑定网卡（原文：`nic_name="eth0"`），并设置 `HCCL_BUFFSIZE=2048`（P 节点）/ `HCCL_BUFFSIZE=600`（D 节点）、`VLLM_USE_V1=1`、`TASK_QUEUE_ENABLE=1`、`HCCL_OP_EXPANSION_MODE="AIV"` 等。
8. **端口与超时**：`vllm serve --port 8003`，`VLLM_RPC_TIMEOUT=3600000`，`VLLM_EXECUTE_MODEL_TIMEOUT_SECONDS=30000`，`HCCL_EXEC_TIMEOUT=204`，`HCCL_CONNECT_TIMEOUT=120`。
9. **D 节点启动方式**：使用 `launch_online_dp.py` + `run_dp_template.sh` 模板，通过 7 个位置参数（`$1`–`$7`）传入可见设备、端口、`data-parallel-size/rank/address/rpc-port` 与 `--tensor-parallel-size`；D 节点 `--max-num-batched-tokens 256`、`--max-num-seqs 40`、`--gpu-memory-utilization 0.94`、`--compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}'`，并启用 `scheduler_config.recompute_scheduler_enable: true`、`multistream_overlap_shared_expert: true`、`finegrained_tp_config.lmhead_tensor_parallel_size: 16`。

---

## 【关键机制与数据】

### 1) 工作机制

- **原文**："By dynamically calculating the optimal chunk size based on profiling data, CPP significantly reduces Time-To-First-Token (TTFT) for long sequences on P nodes."
  - CPP 通过 profiling 数据动态调整 prefill chunk 切分粒度，避免固定切分在长序列下造成的 pipeline 气泡或计算空转，从而压低 TTFT。
- **原文**："CPP is designed to be used on the P (Prefiller) node in Prefill-Decode (PD) disaggregation deployments. The D (Decoder) node does not require CPP configuration."
  - 设计上 CPP 只承担 prefill 阶段调度优化，decode 端做低延迟逐 token 解码，不需要 chunked 调度。

### 2) 数据流

- P 节点完成 prefill → 经 Mooncake 的 KV cache 通道（`kv_port: 36000`）将 KV 传输给 D 节点 → D 节点以 DP32 规模进行 decode。
- P 节点侧 KV 传输上下文：`prefill { pp_size: 2, dp_size: 1, tp_size: 8 }`；D 节点消费侧：`decode { dp_size: 32, tp_size: 1 }`。

### 3) 性能数据

- 文档未给出具体 TTFT 数值或吞吐量对比数据；性能收益仅以 "significantly reduces TTFT for long sequences" 作定性表述。
- 文档**未提供基准测试结果**（评测方式仅在文末关联 `using_ais_bench.md#execute-performance-evaluation` 中，未在本文展示数据）。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档处于 vLLM-Ascend PD 分离部署的特征教程层，与以下文档形成完整闭环：

- **同特性的深度文档**：
  - 配置细节 → [`../../user_guide/feature_guide/dynamic_chunk_pipeline_parallel.md`](../../user_guide/feature_guide/dynamic_chunk_pipeline_parallel.md)
  - 设计原理 → [`../../developer_guide/Design_Documents/dynamic_chunked_pipeline_parallel.md`](../../developer_guide/Design_Documents/dynamic_chunked_pipeline_parallel.md)
- **PD 分离前置准备与对照案例**：
  - 单节点 PD 分离（Qwen2.5-VL）→ [`pd_disaggregation_mooncake_single_node.md`](pd_disaggregation_mooncake_single_node.md)
  - 多节点 PD 分离（DeepSeek）→ [`pd_disaggregation_mooncake_multi_node.md`](pd_disaggregation_mooncake_multi_node.md)
  - Mooncake 安装与编译步骤 → [`pd_disaggregation_mooncake_multi_node.md#install-mooncake`](pd_disaggregation_mooncake_multi_node.md#install-mooncake)
  - `run_dp_template.sh` 参数说明 → [`pd_disaggregation_mooncake_multi_node.md#run_dp_template-sh`](pd_disaggregation_mooncake_multi_node.md#run_dp_template-sh)
- **D 节点启动配套脚本**（来自 `vllm-project/vllm-ascend` 仓库 `examples/external_online_dp/`）：
  - [`launch_online_dp.py`](https://github.com/vllm-project/vllm-ascend/blob/main/examples/external_online_dp/launch_online_dp.py)
  - [`run_dp_template.sh`](https://github.com/vllm-project/vllm-ascend/blob/main/examples/external_online_dp/run_dp_template.sh)
- **性能评估工具**（用于评测 TTFT/吞吐）：
  - [`../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation`](../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation)

整体结构上，本文档以"特性教程（tutorials/features）"为入口，向下接入"用户特性指南（user_guide/feature_guide）"与"开发者设计文档（developer_guide/Design_Documents）"双线展开，并在 PD 分离主线下复用 `pd_disaggregation_mooncake_*` 系列教程的环境与脚本约定。

---

## 【使用方法】

### 1) 启用条件

- 原文："This feature is supported starting from version `v0.19.1rc1`."
- 需在 **P 节点**启用 CPP；D 节点不启用。

### 2) 镜像与容器（原文命令）

```bash
export IMAGE=m.daocloud.io/quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}
export NAME=vllm-ascend

docker run --rm \
  --name $NAME \
  --net=host \
  --shm-size=1g \
  --device /dev/davinci0 ... --device /dev/davinci15 \
  --device /dev/davinci_manager \
  --device /dev/devmm_svm \
  --device /dev/hisi_hdc \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool \
  -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
  -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
  -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  -v /etc/hccn.conf:/etc/hccn.conf \
  -v /mnt/weight:/mnt/weight \
  -it $IMAGE bash
```

### 3) 模型权重

- `DeepSeek-V3.1-W8A8`（量化版），放置于共享目录如 `/mnt/weight/`。

### 4) P 节点启动（带 CPP，原文命令）

关键参数（完整命令见原文）：

| 项 | 值 / 命令 |
|---|---|
| 模型 | `/mnt/weight/DeepSeek-V3.1-w8a8` |
| 端口 | `--port 8003` |
| 服务名 | `--served-model-name model` |
| TP / PP / EP | `--tensor-parallel-size 8` `--pipeline-parallel-size 2` `--enable-expert-parallel` |
| 序列/长度 | `--max-num-seqs 32` `--max-model-len 131072` `--max-num-batched-tokens 32768` |
| 显存 | `--gpu-memory-utilization 0.9` |
| 调度特性 | `--enable-chunked-prefill` `--enable-prefix-caching` `--no-async-scheduling` |
| 量化 | `--quantization ascend` |
| CPP 配置 | `--additional-config '{"scheduler_config":{"profiling_chunk_config":{"enabled":true,"smooth_factor":1.0,"min_chunk":4096}}}'` |
| KV Connector | `MooncakeConnectorV1`，`kv_role: kv_producer`，`kv_port: 36000` |
| KV 并行元数据 | `prefill{pp_size:2, dp_size:1, tp_size:8}`、`decode{dp_size:32, tp_size:1}` |
| 环境变量 | `HCCL_IF_IP=192.0.0.1`、`GLOO/TP/HCCL_SOCKET_IFNAME=eth0`、`OMP_NUM_THREADS=1`、`HCCL_BUFFSIZE=2048`、`HCCL_OP_EXPANSION_MODE=AIV`、`VLLM_USE_V1=1`、`TASK_QUEUE_ENABLE=1`、`VLLM_ALLOW_LONG_MAX_MODEL_LEN=1`、`VLLM_ASCEND_ENABLE_FLASHCOMM1=1`、`VLLM_RPC_TIMEOUT=3600000`、`VLLM_EXECUTE_MODEL_TIMEOUT_SECONDS=30000`、`HCCL_EXEC_TIMEOUT=204`、`HCCL_CONNECT_TIMEOUT=120` |
| 启动成功标志 | `vLLM API server started on 0.0.0.0:8003` |

### 5) D 节点启动（不带 CPP，使用 DP 模板）

- 通过 [`launch_online_dp.py`](https://github.com/vllm-project/vllm-ascend/blob/main/examples/external_online_dp/launch_online_dp.py) + [`run_dp_template.sh`](https://github.com/vllm-project/vllm-ascend/blob/main/examples/external_online_dp/run_dp_template.sh) 在每台 D 节点起多个 DP 实例；模板中按 `$1`–`$7` 接收 `ASCEND_RT_VISIBLE_DEVICES`、`port`、`--data-parallel-size/rank/address/rpc-port`、`--tensor-parallel-size`。
- 关键参数（原文摘要）：
  - `--data-parallel-size/-rank/-address/-rpc-port`：由 launcher 注入；
  - `--tensor-parallel-size 1`（D 节点侧 TP，由 launcher 通过 `$7` 传入）；
  - `--max-model-len 131072`、`--max-num-batched-tokens 256`、`--max-num-seqs 40`、`--gpu-memory-utilization 0.94`；
  - `--no-enable-prefix-caching`、`--compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}'`；
  - `--additional-config '{"scheduler_config":{"recompute_scheduler_enable": true}, "multistream_overlap_shared_expert": true, "finegrained_tp_config":{"lmhead_tensor_parallel_size": 16}}'`；
  - KV 角色：`kv_role: kv_consumer`、`kv_port: 36000`；
  - `OMP_NUM_THREADS=10`、`HCCL_BUFFSIZE=600`、`HCCL_OP_EXPANSION_MODE="AIV"`。

### 6) 注意事项（原文 Important 摘要）

- CPP 仅在 P 节点开启，D 节点不开启；D 节点专注低延迟逐 token 解码。
- 推荐 `MooncakeConnectorV1` 作为 `kv_connector`，对 PP 支持更完备。
- 不推荐在 PP 的 P 节点开启 `async-scheduling`，prefill 阶段可能出现性能下降。

### 7) 性能评估

- 原文未涉及具体的评测执行步骤；评测操作参见 [`../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation`](../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation)。
