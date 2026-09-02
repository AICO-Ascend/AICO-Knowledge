# disagg_pd

> 仓 `xllm` · 路径 `docs/src/content/docs/zh/features/disagg_pd.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/zh/features/disagg_pd.md

# xLLM「PD分离」feature 文档深度解读

---

## 【定位】

这篇文档介绍 xLLM 推理引擎如何通过 **Prefill-Decode 分离（PD Disaggregation）** 的部署架构，将 Prefill（预填充）和 Decode（解码）两个推理阶段拆分到独立计算资源上并行执行，以同时降低 TTFT（首 token 时延）和 TPOT（每 token 生成时延）并提升整体吞吐量。

---

## 【技术要点】

1. **问题动机**：传统 Contiguous Batching 将 P 与 D 请求混合调度，二者会互相抢占计算资源，导致 TTFT 和 TPOT 无法同时最大化。
2. **三模块协作架构**：以 etcd（存储实例元数据）+ xLLM Service（请求调度 + 实例管理）+ xLLM（计算实例执行）三层组合实现 P/D 分离。
3. **三进程启动序列**：依次为 etcd → xllm_master_serving（Service）→ xLLM 计算实例；其中 Service 需设置 `ENABLE_DECODE_RESPONSE_TO_SERVICE=true` 并监听 `etcd_addr="127.0.0.1:12389"`、HTTP 端口 `28888`、RPC 端口 `28889`。
4. **角色化实例启动**：通过 `--instance_role=PREFILL` 与 `--instance_role=DECODE` 区分两种实例，二者各自绑定一张 Ascend NPU 卡（`ASCEND_RT_VISIBLE_DEVICES=0/1`）、不同 service 端口（`8010`/`8020`）、不同 master 节点地址（`127.0.0.1:18888`/`18898`）、不同 transfer 端口（`26000`/`26100`）、不同 PD 通信端口（`7777`/`7787`）。
5. **必关与必开参数**：PD 分离模式下 `--enable_disagg_pd=true`，并显式关闭 `--enable_prefix_cache=false` 与 `--enable_chunked_prefill=false`（即默认模式下禁前缀缓存与分块预填充）；如需开启 chunked-prefill 调度器的 prefix cache，需同时置两个开关为 `true`。
6. **关键环境约束**：容器内必须能读到宿主机的 `/etc/hccn.conf`（用于 NPU 通信），且 P/D 实例的 `--etcd_addr` 必须与 xllm_service 的 `--etcd_addr` 保持一致。

---

## 【关键机制与数据】

- **工作原理（原文）**：
  - 「传统的 Contiguous Batching 调度策略将 Prefill 和 Decode 请求混合在一起调度，导致 P 和 D 会互相抢占计算资源，影响性能指标无法最大程度的利用计算资源」。PD 分离通过「将 Prefill 和 Decode 两阶段拆分到独立的计算资源并行执行」来解决该矛盾。
  - **数据流（原文）**：实例元数据由 etcd 存储；xLLM Service 负责"调度请求和管理所有计算实例"；xLLM 计算实例承担实际的 Prefill 或 Decode 计算；Service 与实例之间通过 etcd（实例注册发现）+ HTTP/RPC（`http_server_port 28888`、`rpc_server_port 28889`）+ 跨实例传输端口（`transfer_listen_port`、`disagg_pd_port`）完成元数据同步与 KV/请求传递。
  - **Chunked-prefill + Prefix cache 调度机制（原文）**：「使用 chunked-prefill PD 调度器时，Prefill 实例已支持 prefix cache。开启后，调度器会先匹配已有 prefix cache block，再计算当前 chunk budget，避免重复计算已缓存的 prompt block」。
- **性能数据**：原文未给出具体的 TTFT / TPOT / 吞吐数字或基准测试数据。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **依赖/前置**：
  - **xLLM 安装编译**：通过内部链接 `/zh/getting_started/quick_start/` 指向（这是文档唯一出现的内部链接）。
  - **xLLM Service**：通过外部 GitHub 链接 `https://github.com/xLLM-AI/xllm-service` 引用，为 PD 分离的调度与管控组件。
  - **etcd**：作为 Service 与 xLLM 实例之间的共享元数据存储，Service 与 P/D 实例必须使用相同的 `--etcd_addr` 才能互通。
- **同/邻接特性**：
  - **Chunked Prefill（分块预填充）**：默认 PD 分离实例关闭（`--enable_chunked_prefill=false`），但开启后可与 Prefix Cache 共存于 Prefill 实例。
  - **Prefix Cache（前缀缓存）**：默认 PD 分离实例关闭（`--enable_prefix_cache=false`），启用 chunked-prefill 时可同时启用并享受调度器层面的去重收益。
  - **KV 传输层**：依赖 `transfer_listen_port`（实例间 KV/中间结果传输的监听端口）与 `disagg_pd_port`（PD 通信端口）完成跨实例数据通路。
- **上下游关系**：客户端请求 → xLLM Service（调度）→ etcd（发现 P/D 实例）→ Prefill 实例（计算 prompt 特征/KV）→ 传输到 Decode 实例（自回归生成）→ 结果经 Service 返回客户端（其中 decode 响应需 `ENABLE_DECODE_RESPONSE_TO_SERVICE=true`）。

---

## 【使用方法】

### 1. 安装
- **xLLM**：参见 [`/zh/getting_started/quick_start/`](/zh/getting_started/quick_start/)
- **xLLM Service**：参见外部仓库 `https://github.com/xLLM-AI/xllm-service`

### 2. 启动顺序与命令

**(a) 启动 etcd**
```bash
./etcd
```

**(b) 启动 xLLM Service**
```bash
ENABLE_DECODE_RESPONSE_TO_SERVICE=true ./xllm_master_serving \
    --etcd_addr="127.0.0.1:12389" \
    --http_server_port 28888 \
    --rpc_server_port 28889 \
    --tokenizer_path=/path/to/tokenizer_config_dir/
```

**(c) 启动 Prefill 实例（以 Qwen2-7B 为例，NPU 0）**
```bash
ASCEND_RT_VISIBLE_DEVICES=0 /path/to/xllm --model=Qwen2-7B-Instruct \
       --port=8010 \
       --master_node_addr="127.0.0.1:18888" \
       --enable_prefix_cache=false \
       --enable_chunked_prefill=false \
       --enable_disagg_pd=true \
       --instance_role=PREFILL \
       --etcd_addr=127.0.0.1:12389 \
       --transfer_listen_port=26000 \
       --disagg_pd_port=7777 \
       --node_rank=0 \
       --nnodes=1
```

**(d) 启动 Decode 实例（以 Qwen2-7B 为例，NPU 1）**
```bash
ASCEND_RT_VISIBLE_DEVICES=1 /path/to/xllm --model=Qwen2-7B-Instruct \
       --port=8020 \
       --master_node_addr="127.0.0.1:18898" \
       --enable_prefix_cache=false \
       --enable_chunked_prefill=false \
       --enable_disagg_pd=true \
       --instance_role=DECODE \
       --etcd_addr=127.0.0.1:12389 \
       --transfer_listen_port=26100 \
       --disagg_pd_port=7787 \
       --node_rank=0 \
       --nnodes=1
```

### 3. 关键开关说明（原文）

| 开关 | 默认（PD 模式下） | 作用 |
|---|---|---|
| `--enable_disagg_pd` | 显式置 `true` | 启用 PD 分离 |
| `--instance_role` | `PREFILL` / `DECODE` | 指定实例角色 |
| `--enable_prefix_cache` | `false` | 默认关闭前缀缓存 |
| `--enable_chunked_prefill` | `false` | 默认关闭分块预填充；置 `true` 后可与 prefix cache 共存 |
| `--enable_prefix_cache=true` + `--enable_chunked_prefill=true` | — | 启用 chunked-prefill 调度器，Prefill 实例支持 prefix cache，先匹配 cache block 再算 chunk budget |

### 4. 部署约束（原文）
- 容器内需挂载宿主机 `/etc/hccn.conf`（NPU 通信配置）。
- xllm 实例的 `--etcd_addr` 必须与 `xllm_service` 的 `--etcd_addr` 保持一致。

## 图文联合解读

- `pd_architecture.jpg`: **1) 图示内容**：请求经API Server进入xLLM Service，由Fault Tolerance、Global Scheduler、Global KV Cache Mgr、Instance Mgr、Planner等模块调度；ETCD集群存储元数据并与Service及xLLM互通；底层xLLM含多个Prefill/Decode实例（Engine+kv cache+KVCacheTransfer），Prefill与Decode通过KVCacheTransfer互联。

**2) 技术结论**：PD分离通过Service集中调度+实例间KVCache直传+ETCD元数据共享，实现Prefill/Decode独立扩缩与资源解耦。

**3) 与文档关系**：图示完整印证文档"三模块协同"论点，可视化了etcd元数据、xLLM Service调度、xLLM Prefill/Decode实例（`--instance_role=PREFILL`）的执行链路与`--transfer_listen_port`对应的KV传输通道。
