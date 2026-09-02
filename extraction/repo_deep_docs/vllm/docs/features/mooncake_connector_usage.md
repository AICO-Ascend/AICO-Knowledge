# MooncakeConnector Usage Guide

> 仓 `vllm` · 路径 `docs/features/mooncake_connector_usage.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/mooncake_connector_usage.md

```markdown
# MooncakeConnector Usage Guide — 一体化深度解读

## 【定位】

这篇文档是 vLLM 推理引擎中 **MooncakeConnector**（基于 Mooncake Transfer Engine 的 KV 缓存传输连接器）的部署与使用手册，目标是指导用户在 **prefill-decode 解耦架构（disaggregated inference）** 下，通过 Mooncake 的 RDMA 零拷贝通路在 prefiller 节点和 decoder 节点之间高效搬运 KV cache，从而把 vLLM 的 KV cache 从 prefiller 实例转移到 decoder 实例。

---

## 【技术要点】

- **核心定位**：Mooncake 通过在高速互联的 DRAM/SSD 资源上构建多层缓存池来提升 LLM 推理效率，专注于慢对象存储场景，并通过 (GPUDirect) RDMA 实现零拷贝数据传输，最大化单机多 NIC 资源利用率。
- **安装约束（CUDA 主版本敏感）**：vLLM 默认 CUDA 13，对应 pip 包为 `mooncake-transfer-engine-cuda13`；CUDA 12 环境必须改装 `mooncake-transfer-engine`，两者为同版本不同 CUDA 主版本的构建，错误安装会以 `libcudart.so.<major>: cannot open shared object file` 报错。
- **三组件拓扑**：prefill 实例（`kv_role: kv_producer`，端口 8010）+ decode 实例（`kv_role: kv_consumer`，端口 8020）+ 一个轻量级 proxy（默认监听端口 8000，转发请求到 prefill/decode）。
- **角色模式**：`kv_producer` / `kv_consumer` / `kv_both`，其中 `kv_both` 用于角色未预先确定的实验性对称部署。
- **关键环境变量**：
  - `VLLM_MOONCAKE_BOOTSTRAP_PORT`，默认 `8998`，仅 prefiller 需要；headless 实例必须与 master 实例一致；同一主机不同实例需要不同端口，跨主机端口号可相同。
  - `WITH_NVIDIA_PEERMEM`，默认 `1`（走 `ibv_reg_mr()` + `nvidia-peermem` 内核模块路径），设为 `0` 则走 DMA-BUF 路径，是 GB200 等无 peermem 模块主机的必需选项；未正确设置会在 `rdma_context.cpp` 中抛出 `Failed to register memory <addr>: Bad address [14]`，导致 KV 传输失败。
  - `VLLM_MOONCAKE_ABORT_REQUEST_TIMEOUT`，默认 `480` 秒，用于在请求被 abort 但尚未告知 prefiller 时，超时回收 prefiller 端的 KV cache 块，避免无限占用。
- **连接器扩展配置（`kv_connector_extra_config`）**：
  - `num_workers`：每个 prefiller worker 用于 Mooncake 传输 KV cache 的线程池大小，默认 `10`。
  - `mooncake_protocol`：传输协议，默认 `"rdma"`。
  - `device_name`：RDMA 设备白名单（逗号分隔，如 `"mlx5_0,mlx5_1"`），空字符串代表自动发现全部设备；在 InfiniBand 与 RoCE 混部主机上用于强制两端走同一类链路层。

---

## 【关键机制与数据】

**工作原理（按原文梳理）**：
1. Mooncake 在 LLM 推理系统中提供 KV cache 多级缓存池，数据通路基于 GPUDirect RDMA 实现零拷贝，单机多 NIC 可并发利用以提升带宽。
2. 在 vLLM 的解耦推理（disaggregated）场景里，MooncakeConnector 作为 `KVTransferConfig` 中的 `kv_connector`，分别以 `kv_producer` 和 `kv_consumer` 两端运行：prefill 完成后把 KV cache 通过 Mooncake 传输给 decode 端做继续生成。
3. proxy 进程是 HTTP 入口：客户端请求打到 proxy（默认 8000），proxy 把请求路由到 prefiller（8010），然后把 decode 端（8020）接上后续生成步骤；整个 KV cache 通路在 Mooncake 内部完成。
4. GPU 内存注册走两条路径：`ibv_reg_mr()`（peermem 模块，需要 root 权限加载）或 DMA-BUF（无需 peermem，适合 GB200 等新硬件）；错误路径会在 `rdma_context.cpp` 中以 `Failed to register memory <addr>: Bad address [14]` 报错，最终导致 KV transfer 失败。
5. abort 兜底：若请求被取消且 decoder 没来得及通知 prefiller，prefiller 端在 `VLLM_MOONCAKE_ABORT_REQUEST_TIMEOUT`（默认 480 秒）后自动释放该请求对应的 KV cache 块。

**数据/参数（原文给出的具体数字与默认值）**：

- 默认端口：prefiller bootstrap = `8998`，HTTP prefill = `8010`，HTTP decode = `8020`，proxy = `8000`。
- `VLLM_MOONCAKE_ABORT_REQUEST_TIMEOUT` 默认 = `480` 秒。
- `num_workers` 默认 = `10`。
- `WITH_NVIDIA_PEERMEM` 默认 = `1`。
- `mooncake_protocol` 默认 = `"rdma"`。
- 示例模型：`Qwen/Qwen2.5-7B-Instruct`。

---

## 【表格解读】

原文无表格。

原文中的 KV role / 环境变量 / extra_config 都是以 markdown 列表形式给出，没有结构化表格。为方便对照，下面以 markdown 表格**逐字**还原三组关键配置（内容完全取自原文，未新增字段）：

### 表 1：KV Role 选项（原文）

| 选项 | 含义 |
|---|---|
| `kv_producer` | For prefiller instances that generate KV caches |
| `kv_consumer` | For decoder instances that consume KV caches from prefiller |
| `kv_both` | Enables symmetric functionality where the connector can act as both producer and consumer. This provides flexibility for experimental setups and scenarios where the role distinction is not predetermined. |

逐行解读：
- `kv_producer`：运行在 prefiller 上，负责生成 KV cache 并通过 Mooncake 推送出去。
- `kv_consumer`：运行在 decoder 上，负责接收并装载 prefiller 端推送过来的 KV cache。
- `kv_both`：同一个 connector 进程既能产又能消费，主要面向对称部署与实验场景，便于把角色解耦。

### 表 2：环境变量（原文）

| 变量名 | 默认值 | 是否必填 / 适用对象 | 关键行为 |
|---|---|---|---|
| `VLLM_MOONCAKE_BOOTSTRAP_PORT` | `8998` | 仅 prefiller 实例必填；headless 实例须与 master 一致 | Mooncake bootstrap 服务端口 |
| `WITH_NVIDIA_PEERMEM` | `1` | 在没加载 `nvidia-peermem` 的主机（如 GB200）需设为 `0` | `1`→`ibv_reg_mr()` 需 peermem 模块；`0`→DMA-BUF |
| `VLLM_MOONCAKE_ABORT_REQUEST_TIMEOUT` | `480` 秒 | 可选 | abort 请求且 decoder 未通知 prefiller 时，超时回收 prefiller 端 KV cache 块 |

逐行解读：
- `VLLM_MOONCAKE_BOOTSTRAP_PORT`：Mooncake 的 bootstrap 服务用于 prefiller 与 proxy/decoder 之间建链。仅 prefiller 必须显式选择端口；headless（即无 master 角色）实例要保持与同集群 master 一致；同一主机上的多个实例必须端口不同，但跨主机可以复用同一端口号（语义上由 IP 区分）。
- `WITH_NVIDIA_PEERMEM`：由 Mooncake 读取而非 vLLM 读取，决定 GPU 内存如何注册到 RDMA。默认走 `ibv_reg_mr()`，依赖 `nvidia-peermem` 内核模块；在 GB200 等无法加载该模块的平台上必须设 `0` 改走 DMA-BUF。容器化场景通过 `docker run -e WITH_NVIDIA_PEERMEM=0 ...` 注入。未正确设置时会触发 `rdma_context.cpp` 中的 `Failed to register memory <addr>: Bad address [14]` 错误。
- `VLLM_MOONCAKE_ABORT_REQUEST_TIMEOUT`：以秒为单位的 abort 兜底超时。当请求被取消且 decoder 还没把释放消息送达 prefiller 时，prefiller 端在该超时到期后主动释放该请求的 KV cache 块，避免长时占用。

### 表 3：`kv_connector_extra_config`（原文）

| 参数 | 默认值 | 含义 |
|---|---|---|
| `num_workers` | `10` | 单个 prefiller worker 用于通过 Mooncake 传输 KV cache 的线程池大小 |
| `mooncake_protocol` | `"rdma"` | Mooncake 连接器传输协议 |
| `device_name` | 空（自动发现） | RDMA 设备白名单（逗号分隔，如 `"mlx5_0,mlx5_1"`），用于限制拓扑发现范围；InfiniBand/RoCE 混部时强制两端走同一链路层 |

逐行解读：
- `num_workers`：并发传输 KV cache 的线程数；值越大并发度越高，但也会消耗 prefiller worker 的 CPU/线程资源。
- `mooncake_protocol`：底层传输协议选择，默认 RDMA，原文未列出其它可选值。
- `device_name`：用来锁定 RDMA NIC 子集；在 IB 与 RoCE 混布且两端必须使用同一链路层时尤其有用；空值 = 全量发现。

---

## 【公式解读】

原文无公式。

---

## 【关联】

**与 Mooncake 上游项目**：
- 本文档多次引导用户回到 [Mooncake project](https://github.com/kvcache-ai/Mooncake) 和 [Mooncake documents](https://kvcache-ai.github.io/Mooncake/)，表明 vLLM 中的 MooncakeConnector 是对 Mooncake Transfer Engine 的**适配层**：vLLM 负责 KV cache 的生成/消费与生命周期管理，Mooncake 负责跨节点 RDMA 通路。

**与 vLLM 解耦推理（disaggregated inference）框架**：
- 文档中的 `kv_role`、`kv_connector`、`kv-transfer-config` 字段是 vLLM 解耦推理的标准接口；MooncakeConnector 在该接口下扮演具体的 `kv_connector` 实现，与其它可能的 connector（如基于 TCP/NCCL 等）并存。
- proxy（`mooncake_connector_proxy.py`）是 vLLM disaggregated 模式中典型的请求路由层，接收客户端 HTTP 请求后把预填请求转发给 prefiller、再交给 decoder。

**与硬件 / 内核模块**：
- `WITH_NVIDIA_PEERMEM=1` 依赖 `nvidia-peermem` 内核模块，把 GPU 显存注册为 IBV MR；这与 NVIDIA GPUDirect RDMA 内核栈紧耦合。
- `WITH_NVIDIA_PEERMEM=0` 走 DMA-BUF 路径，是 GB200 等新一代平台上规避 peermem 缺失的替代方案。

**与请求生命周期管理**：
- `VLLM_MOONCAKE_ABORT_REQUEST_TIMEOUT` 与 vLLM 的请求 abort 流程耦合：负责在 decoder 异常退出/未送达释放消息时防止 prefiller 端 KV cache 块被无限占用。

**文末内部链接**：
- [run_mooncake_connector.sh](../../examples/disaggregated/mooncake_connector/run_mooncake_connector.sh)：一键启动脚本，把 prefiller、decoder、proxy 三者在一个脚本里拉起。
- [mooncake_connector_proxy.py](../../examples/disaggregated/mooncake_connector/mooncake_connector_proxy.py)：独立 Python proxy，监听端口 8000，把客户端请求按需路由到 prefiller/decode。

---

## 【使用方法】

**1. 安装**：
- CUDA 13 环境（vLLM 默认）：`uv pip install mooncake-transfer-engine-cuda13`
- CUDA 12 环境：`uv pip install mooncake-transfer-engine`

**2. 启动 Prefiller（示例 IP `192.168.0.2`）**：

```bash
vllm serve Qwen/Qwen2.5-7B-Instruct \
  --port 8010 \
  --kv-transfer-config '{"kv_connector":"MooncakeConnector","kv_role":"kv_producer"}'
```

**3. 启动 Decoder（示例 IP `192.168.0.3`）**：

```bash
vllm serve Qwen/Qwen2.5-7B-Instruct \
  --port 8020 \
  --kv-transfer-config '{"kv_connector":"MooncakeConnector","kv_role":"kv_consumer"}'
```

**4. 启动 Proxy**：

```bash
python examples/disaggregated/mooncake_connector/mooncake_connector_proxy.py \
  --prefill http://192.168.0.2:8010 \
  --decode http://192.168.0.3:8020
```

之后通过端口 `8000` 向 proxy 发送请求。

**5. 关键环境变量（启动前可选配置）**：
- `VLLM_MOONCAKE_BOOTSTRAP_PORT`：默认 `8998`，仅 prefiller 需要；headless 实例必须与 master 一致；同主机不同实例端口必须不同，跨主机端口号可相同。
- `WITH_NVIDIA_PEERMEM`：默认 `1`（需 `nvidia-peermem` 内核模块）；在 GB200 等无该模块的主机上设 `0`；容器场景通过 `docker run -e WITH_NVIDIA_PEERMEM=0 ...` 注入。
- `VLLM_MOONCAKE_ABORT_REQUEST_TIMEOUT`：默认 `480` 秒，abort 兜底超时。

**6. `kv_connector_extra_config`（在 `--kv-transfer-config` JSON 中追加）**：
- `num_workers`（默认 `10`）：每个 prefiller worker 的 Mooncake 传输线程池大小。
- `mooncake_protocol`（默认 `"rdma"`）：底层传输协议。
- `device_name`（默认空 = 自动发现）：RDMA 设备白名单，如 `"mlx5_0,mlx5_1"`。
```

---
*以上解读严格基于原文，未引入文档未给出的数值或机制；环境变量与配置项的默认值、命令、错误现象均逐字摘自原文。*
