# MoRIIOConnector Usage Guide

> 仓 `vllm` · 路径 `docs/features/moriio_connector_usage.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/moriio_connector_usage.md

# vLLM 文档深度解读:MoRIIOConnector Usage Guide

## 【定位】

这篇文档描述 vLLM 在 ROCm 平台上专用的 KV cache 传输连接器 **MoRIIOConnector** —— 它基于 AMD ROCm 的 [MoRI-IO](https://github.com/rocm/mori) 通信库,提供低开销的点对点 KV cache 传输,服务于 PD 分离部署 (Prefill-Decode disaggregation) 场景下的 prefiller→decoder KV 缓存搬运需求,并给出单主机/多节点两种部署形态的完整启动范式。

---

## 【技术要点】

1. **连接器性质与依赖**:基于 ROCm 的 MoRI-IO 库构建的 KV connector;官方镜像 `vllm/vllm-openai-rocm:nightly` 已自带 MoRI;手动安装可执行 `pip install amd_mori`。
2. **两种工作模式(WRITE/READ)**:
   - **WRITE 模式(默认)**:producer 每完成一层计算就把 KV 块主动推送到 consumer 显存。
   - **READ 模式**:consumer 在收到 KV 块就绪通知后一次性把 KV 块从 producer 端拉取过来;通过 `--kv-transfer-config.kv_connector_extra_config.read_mode true` 启用。
3. **控制面五项关键参数**(均位于 `kv_connector_extra_config` 下):`proxy_ip`、`proxy_ping_port`(默认 `36367`)、`http_port`、`handshake_port`、`notify_port`。
4. **两种传输后端**:
   - **RDMA**(默认,多节点必备);通过 `--kv-transfer-config.kv_connector_extra_config.backend rdma` 显式选择。
   - **xGMI**(同机 prefiller+decoder 时使用,绕开 NIC 直走 AMD GPU fabric);通过 `backend xgmi` 启用。
5. **RDMA 后端核心可调参数**:`qp_per_transfer`(每个 transfer 的 QP 数)、`post_batch_size`(单次 `ibv_post_send` doorbell 内合并的 WR 数,默认 `-1` 表示使用后端默认)、`num_workers`(投递/轮询完成的工作线程数);另外可通过 MoRI 自身的环境变量(如 `MORI_IO_QP_MAX_SEND_WR`、`MORI_IO_QP_MAX_CQE`)做高级调优,与 vLLM 的 `VLLM_MORIIO_*` 设置相互独立。
6. **端口基准与偏移规则**:`notify_port` 是 *基准端口*,每个 `(DP rank, TP rank)` 对使用 `notify_port + offset`,其中 offset 由 rank 决定,因此需保证从 `notify_port` 起的一段端口范围在主机上可用。

---

## 【关键机制与数据】

**工作原理(数据流,按原文梳理)**:

- **握手流程(原文)**:`handshake_port` 用于 prefiller 与 decoder 之间一次性 MoRI engine 握手,双方在 KV 传输开始前交换 RDMA engine descriptors。
- **传输路径(原文)**:"MoRI moves KV bytes over RDMA/xGMI",即数据通路走 RDMA 或 xGMI,而控制通道(proxy 注册/心跳、握手、块 ID 交换、存活检测、完成信号)走 TCP。
- **WRITE 模式数据流(原文)**:
  1. **Block allocation**:decoder 通过 `notify_port` 通道告知 prefiller 自己拥有的 block id。
  2. 之后 prefiller 按层把计算好的 KV 块推送到 decoder 端对应 block。
  3. **Completion**:全部块传输完毕后,prefiller 通知 decoder 可安全使用这些块。
- **READ 模式数据流(原文)**:decoder 在就绪通知后一次性把所有 KV 块从 prefiller 端拉走;完成后通知 prefiller,使其可以释放 KV cache block。
- **代理(proxy)注册与心跳(原文)**:每个 vLLM 实例向 `proxy_ip:proxy_ping_port` 发起注册并发送心跳,代理据此保持路由表鲜活;用户请求由代理根据注册的 `http_port` 转发到具体实例。
- **xGMI vs RDMA(原文)**:xGMI 用于 prefiller/decoder 同主机,跳过 NIC 直接走 AMD GPU 内部 fabric;RDMA 走 NIC,适合跨节点。

**性能/容量数据(仅列举原文明确出现的数字)**:
- 单机示例使用模型 `Qwen/Qwen3-235B-A22B-FP8`,TP=4,`gpu-memory-utilization=0.9`,prefill 占 GPU 0–3,decode 占 GPU 4–7。
- 多节点示例使用 `deepseek-ai/DeepSeek-R1-0528`,TP=8,`gpu-memory-utilization=0.8`,启用 `--enable-expert-parallel`,Docker 资源参数:`--shm-size 256G`、`--ulimit memlock=-1`、`--ulimit stack=67108864`。
- 关于 `post_batch_size`:原文仅给 "-1 表示后端默认"的语义,未给出具体性能数值。

---

## 【表格解读】

**原文无表格。** 文中以 JSON 配置块、shell 命令和环境变量列表形式呈现配置项,未出现 markdown 表格;因此不做表格还原。

---

## 【公式解读】

**原文无公式。** 文中没有 LaTeX 或伪代码形式的数学公式;唯一可视为"参数化表达"的是 `notify_port + offset` 的端口偏移描述,但这是端口号生成规则而非数值/数学公式。

---

## 【关联】

文档与其他模块/特性的耦合关系:

- **与上游镜像/构建**:
  - 引用 [`Dockerfile.rocm_base`](../../docker/Dockerfile.rocm_base):在"Prerequisites → Installation"章节被引用,作为获取 MoRI 安装信息的入口(原文: "Refer to the Dockerfile.rocm_base for more information")。
  - 本提示中提到的 `Dockerfile.rocm`(../../docker/Dockerfile.rocm)在这篇文档可见的正文内**未被引用**,仅出现在题目提示中。
- **与 PD 分离部署框架**:本连接器本身属于 PD disaggregation 体系下的 KV cache 通道;需要配套的 `vllm-router`(代理)和 `--vllm-pd-disaggregation` 模式才能组成完整工作链。
- **与 MoRI-IO 通信库**:作为底层 transport 实现,既消费其 RDMA/xGMI 数据面,又通过 `MORI_IO_*` 环境变量暴露出传输层细粒度调优。
- **与 ROCm 运行时**:依赖 ROCm 的 AITER(`VLLM_ROCM_USE_AITER=1`)以及 `HIP_VISIBLE_DEVICES`、`/dev/kfd`、`/dev/dri`、`/dev/infiniband` 设备与 `--group-add video/render` 的设备权限;并要求 RDMA 场景下安装对应的 NIC userspace 库(原文链接 "Installing NIC userspace libraries",在文末"附录"位置)。
- **与 KV connector 体系**:作为 `kv_connector` 字段的一个可选值(`"MoRIIOConnector"`),与其它 KV 传输实现并列,通过统一的 `--kv-transfer-config` 接口接入 vLLM。
- **与参考实现代理**:除 `vllm-router` 外,文档还给出 vLLM 仓库内的参考 toy 代理 `examples/disaggregated/disaggregated_serving/moriio_toy_proxy_server.py` 作为可选替代。

---

## 【使用方法】

### 安装
- **Docker 方式(原文)**:直接使用 `vllm/vllm-openai-rocm:nightly`,已内置 MoRI。
- **手动安装(原文)**:
  ```bash
  pip install amd_mori
  ```
- **Docker 代理镜像(原文)**:使用 `vllm/vllm-router:nightly`。
- **手动代理安装(原文)**:
  ```bash
  pip install vllm-router
  ```

### 单机部署(原文命令)

**Prefill 实例(GPU 0–3,`port 20005`,TP=4,mem 0.9)**:
```bash
export VLLM_ROCM_USE_AITER=1
export CUDA_VISIBLE_DEVICES=0,1,2,3
export HIP_VISIBLE_DEVICES=0,1,2,3
vllm serve Qwen/Qwen3-235B-A22B-FP8 \
  -tp 4 --port 20005 --gpu-memory-utilization 0.9 \
  --kv-transfer-config '{
    "kv_connector": "MoRIIOConnector",
    "kv_role": "kv_producer",
    "kv_connector_extra_config": {
      "proxy_ip": "127.0.0.1",
      "proxy_ping_port": "36367",
      "http_port": "20005",
      "handshake_port": "6301",
      "notify_port": "6105"
    }
  }'
```

**Decode 实例(GPU 4–7,`port 40005`,TP=4,mem 0.9)**:
- 端口差异:`handshake_port=7301`、`notify_port=7501`、`http_port=40005`;其余与 prefiller 对称。

### 启动代理(原文)
- 关键参数:`--vllm-pd-disaggregation --kv-connector moriio --vllm-discovery-address "0.0.0.0:36367"`(`36367` 即 `proxy_ping_port`)。
- 备选 toy 代理:`python examples/disaggregated/disaggregated_serving/moriio_toy_proxy_server.py`(需先 `pip install quart aiohttp msgpack`)。

### 多节点 1P1D 部署(原文)
- 两节点共需:`export PREFILL_IP=<node1-ip>; export DECODE_IP=<node2-ip>`。
- **Node 1(同时跑 proxy 与 prefill)**:Docker 命令,模型 `deepseek-ai/DeepSeek-R1-0528`,TP=8,`--enable-expert-parallel`,`--gpu-memory-utilization 0.8`,`--port 8100`,`--kv-transfer-config` 内 `kv_role=kv_producer`,`http_port=8100`,`handshake_port=6301`,`notify_port=61005`,`proxy_ip="${PREFILL_IP}"`。
- **Node 2(decode)**:模型同上,TP=8,`--enable-expert-parallel`,`--gpu-memory-utilization 0.8`,`--port 8200`,`kv_role=kv_consumer`,`proxy_ip="${DECODE_IP}"`。
- 关键 Docker flags(原文):`--init --network host --ipc host --privileged --security-opt seccomp=unconfined --ulimit memlock=-1 --ulimit stack=67108864 --shm-size 256G --group-add video --group-add render --device /dev/kfd --device /dev/dri --device /dev/infiniband`。

### 应用层配置(原文摘录)
- `--kv-transfer-config.kv_connector_extra_config.read_mode true` → 切换到 READ 模式。
- `--kv-transfer-config.kv_connector_extra_config.backend rdma|xgmi` → 选择传输后端。

### RDMA 后端参数(原文)
- `qp_per_transfer`:QP 数量,数值越大单次传输并发越高,但 RDMA 资源占用越多。
- `post_batch_size`:一次 doorbell 合并的 WR 数,默认 `-1`(后端默认);增大可降低每次 WR 的下发开销。
- `num_workers`:MoRI 用来提交/轮询 transfer completion 的工作线程数。

### NIC userspace 库
- 原文:参见附录 "Installing NIC userspace libraries"(原文: "For instructions on installing appropriate NIC userspace libraries, see Installing NIC userspace libraries")。

> **说明**:原文"Multi-node deployment → On node 2"的 docker 命令末尾 `--kv-transfer-config '{ "kv_connector": "M` 处被截断,node 2 完整 JSON 配置未在原文给出,故不补全。
