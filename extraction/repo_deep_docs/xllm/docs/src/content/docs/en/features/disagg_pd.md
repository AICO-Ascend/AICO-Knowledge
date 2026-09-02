# disagg_pd

> 仓 `xllm` · 路径 `docs/src/content/docs/en/features/disagg_pd.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/en/features/disagg_pd.md

# xLLM Disaggregated PD 文档深度解读

## 【定位】

本文档系统阐述了 xLLM 的**Prefill-Decode 解耦 (Disaggregated PD)** 能力,描述如何将传统推理中耦合的 Prefill 与 Decode 两个阶段拆分到独立计算资源上并行执行,从而同时优化 **TTFT** 与 **TPOT** 两大在线推理性能指标,并给出基于 etcd + xLLM Service + xLLM 三组件架构的端到端部署与启动流程。

---

## 【技术要点】

1. **核心问题**:传统 Contiguous Batching 调度将 Prefill 与 Decode 请求混合,两者在算力资源上产生竞争,导致资源利用率不充分,TTFT 与 TPOT 难以同时优化。

2. **解决方案**:将 Prefill 与 Decode 阶段拆分到**独立的计算资源**上并行运行,从根本上消除两阶段之间的算力争抢,实现"降低 TTFT + 降低 TPOT + 提升吞吐"的三重目标。

3. **三组件架构**:
   - **etcd**:存储实例信息等元数据
   - **xLLM Service**:负责请求调度并管理所有计算实例
   - **xLLM**:负责具体的请求计算

4. **环境依赖**:依赖 `/etc/hccn.conf` 文件获取 AI Server 的 Device IP,用于创建通信资源;在容器化部署时需将该文件映射进容器。

5. **实例角色区分**:通过 `--instance_role=PREFILL` 与 `--instance_role=DECODE` 启动不同角色的 xLLM 实例,Prefill 与 Decode 各使用不同的 ASCEND 设备 (示例中分别使用 `ASCEND_RT_VISIBLE_DEVICES=0` 与 `=1`)、不同的 `--port`、`--master_node_addr`、`--transfer_listen_port`、`--disagg_pd_port`。

6. **chunked-prefill + prefix cache 联动**:在 chunked-prefill PD 调度器下,Prefill 实例支持 prefix cache——调度器在计算当前 chunk 预算之前会优先匹配已缓存的 prefix-cache 块,避免重复计算已缓存的 prompt 块。

---

## 【关键机制与数据】

- **工作原理 (原文:Background)**:
  - 在线推理服务的两大性能指标为 **TTFT** 与 **TPOT**
  - 传统 Contiguous Batching 把 Prefill 与 Decode 请求混排 → 资源竞争 → 资源利用无法最大化 → 性能指标受损
  - 解耦后:Prefill 与 Decode 在**独立算力**上**并行执行**,同时降低 TTFT 和 TPOT 并提升吞吐

- **三模块职责 (原文:Introduction)**:
  - etcd ← 元数据 / 实例信息存储
  - xLLM Service ← 请求调度 + 计算实例管理
  - xLLM ← 请求计算

- **架构图**:`![xLLM PD Separation Architecture](figures/pd_architecture.jpg)` 文档引用该图说明整体架构。

- **关键端口与地址 (原文:Usage)**:
  - Device IP 获取命令:`cat /etc/hccn.conf | grep address`,输出格式 `address_0=xx.xx.xx.xx`、`address_1=xx.xx.xx.xx`
  - etcd 默认地址示例:`127.0.0.1:12389`
  - xLLM Service HTTP 端口:28888,RPC 端口:28889,tokenizer 配置目录需指定
  - Prefill / Decode 实例使用各自独立的 `transfer_listen_port` (26000 / 26100) 与 `disagg_pd_port` (7777 / 7787)

- **性能数据**:原文未给出具体的 TTFT、TPOT 或吞吐数字,仅定性描述"同时降低 TTFT 和 TPOT,同时提升吞吐"。

---

## 【表格解读】

原文未包含任何 markdown 表格。但配置项以代码块形式列出,以下**按原文逐字还原为表格**以便解读:

### 表 1: xLLM Service 启动参数

| 参数 | 取值 (原文) | 含义解读 |
|---|---|---|
| 环境变量 `ENABLE_DECODE_RESPONSE_TO_SERVICE` | `true` | 控制 Decode 响应是否回流到 xLLM Service |
| `--etcd_addr` | `"127.0.0.1:12389"` | etcd 服务地址,与后续 xLLM 实例必须一致 |
| `--http_server_port` | `28888` | xLLM Service HTTP 服务端口 |
| `--rpc_server_port` | `28889` | xLLM Service RPC 服务端口 |
| `--tokenizer_path` | `/path/to/tokenizer_config_dir/` | tokenizer 配置文件所在目录 |

### 表 2: Prefill 实例启动参数 (Qwen2-7B-Instruct 示例)

| 参数 | 取值 (原文) | 含义解读 |
|---|---|---|
| `ASCEND_RT_VISIBLE_DEVICES` | `0` | 限定 Prefill 进程使用的 Ascend NPU 卡号 |
| `--model` | `Qwen2-7B-Instruct` | 模型标识 |
| `--port` | `8010` | Prefill 实例 HTTP 端口 |
| `--master_node_addr` | `"127.0.0.1:18888"` | Prefill 实例 master 地址 |
| `--enable_prefix_cache` | `false` | Prefill 阶段关闭 prefix cache(本配置) |
| `--enable_chunked_prefill` | `false` | 关闭 chunked prefill(本配置) |
| `--enable_disagg_pd` | `true` | 启用 PD 解耦 |
| `--instance_role` | `PREFILL` | 标识当前实例为 Prefill 角色 |
| `--etcd_addr` | `"127.0.0.1:12389"` | 必须与 xllm_service 的 etcd_addr 一致 |
| `--transfer_listen_port` | `26000` | Prefill→Decode 的 KV 传输监听端口 |
| `--disagg_pd_port` | `7777` | PD 解耦通信端口 |
| `--node_rank` | `0` | 当前节点 rank |
| `--nnodes` | `1` | 总节点数 |

### 表 3: Decode 实例启动参数 (Qwen2-7B-Instruct 示例)

| 参数 | 取值 (原文) | 含义解读 |
|---|---|---|
| `ASCEND_RT_VISIBLE_DEVICES` | `1` | 限定 Decode 进程使用另一张 Ascend NPU |
| `--model` | `Qwen2-7B-Instruct` | 同 Prefill,模型保持一致 |
| `--port` | `8020` | Decode 实例 HTTP 端口,与 Prefill 不同 |
| `--master_node_addr` | `"127.0.0.1:18898"` | Decode 实例 master 地址,与 Prefill 不同 |
| `--enable_prefix_cache` | `false` | 本配置关闭 prefix cache |
| `--enable_chunked_prefill` | `false` | 本配置关闭 chunked prefill |
| `--enable_disagg_pd` | `true` | 启用 PD 解耦 |
| `--instance_role` | `DECODE` | 标识当前实例为 Decode 角色 |
| `--etcd_addr` | `"127.0.0.1:12389"` | 必须与 xllm_service 的 etcd_addr 一致 |
| `--transfer_listen_port` | `26100` | Decode 端接收 KV 传输的端口,与 Prefill 不同 |
| `--disagg_pd_port` | `7787` | Decode 端 PD 解耦通信端口 |
| `--node_rank` | `0` | 当前节点 rank |
| `--nnodes` | `1` | 总节点数 |

### 表 4: chunked-prefill + prefix cache 启用配置 (Notice)

| 参数 | 取值 (原文) | 含义解读 |
|---|---|---|
| `--enable_chunked_prefill` | `true` | 启用 chunked prefill |
| `--enable_prefix_cache` | `true` | 启用 prefix cache;调度器会在 chunk 预算计算前先匹配已缓存的 prefix-cache 块,避免重算 |

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游安装依赖**:本文档在 Preparation 阶段指向 xLLM 自身的编译安装文档,链接为 **`/en/getting_started/quick_start/`**(即内部链接目标);以及指向外部仓库的 **[xLLM Service](https://github.com/xLLM-AI/xllm-service)** 文档,表明 PD 解耦功能**必须**与 xLLM Service 配套部署。
- **etcd 组件**:作为三方依赖,在本文档"Start Disaggregated PD Service"第一步被引入(`./etcd`),与 xLLM Service、xLLM 形成三模块协同架构,实例信息通过 `--etcd_addr` 在三者之间共享。
- **架构示意**:文档引用 `figures/pd_architecture.jpg` 说明 etcd / xLLM Service / xLLM 之间的整体关系。
- **特性互补**:Notice 章节中,`--enable_chunked_prefill=true` 与 `--enable_prefix_cache=true` 是与 PD 解耦联动的两个开关,共同构成 chunked-prefill PD 调度器的完整能力。
- **硬件依赖**:与 Ascend NPU 强相关(`ASCEND_RT_VISIBLE_DEVICES`、`/etc/hccn.conf` 表明底层走 HCCN 通信),反映 xLLM 对昇腾生态的适配。

---

## 【使用方法】

### 1. 前置准备
- 安装 **xLLM** (参见 [`/en/getting_started/quick_start/`](/en/getting_started/quick_start/))
- 安装 **xLLM Service** (参见 [xLLM Service](https://github.com/xLLM-AI/xllm-service))
- 获取 Device IP:在 AI Server 上执行 `cat /etc/hccn.conf | grep address`,得到形如 `address_0=xx.xx.xx.xx`、`address_1=xx.xx.xx.xx` 的输出

### 2. 启动顺序 (按依赖关系)
1. **启动 etcd**
   ```bash
   ./etcd
   ```
2. **启动 xLLM Service**
   ```bash
   ENABLE_DECODE_RESPONSE_TO_SERVICE=true ./xllm_master_serving --etcd_addr="127.0.0.1:12389" --http_server_port 28888 --rpc_server_port 28889 --tokenizer_path=/path/to/tokenizer_config_dir/
   ```
3. **启动 xLLM Prefill 实例** (Qwen2-7B 示例)
   ```bash
   ASCEND_RT_VISIBLE_DEVICES=0 /path/to/xllm --model=Qwen2-7B-Instruct \
          --port=8010 \
          --master_node_addr="127.0.0.1:18888" \
          --enable_prefix_cache=false \
          --enable_chunked_prefill=false \
          --enable_disagg_pd=true \
          --instance_role=PREFILL \
          --etcd_addr="127.0.0.1:12389" \
          --transfer_listen_port=26000 \
          --disagg_pd_port=7777 \
          --node_rank=0 \
          --nnodes=1
   ```
4. **启动 xLLM Decode 实例** (Qwen2-7B 示例)
   ```bash
   ASCEND_RT_VISIBLE_DEVICES=1 /path/to/xllm --model=Qwen2-7B-Instruct \
          --port=8020 \
          --master_node_addr="127.0.0.1:18898" \
          --enable_prefix_cache=false \
          --enable_chunked_prefill=false \
          --enable_disagg_pd=true \
          --instance_role=DECODE \
          --etcd_addr="127.0.0.1:12389" \
          --transfer_listen_port=26100 \
          --disagg_pd_port=7787 \
          --node_rank=0 \
          --nnodes=1
   ```

### 3. 重要注意事项
- PD 解耦依赖读取 `/etc/hccn.conf` 文件;若在容器中部署,需将该文件从物理机映射进容器。
- xLLM 实例的 `--etcd_addr` 必须与 `xllm_service` 的 `--etcd_addr` **保持一致**。
- 若需启用 chunked-prefill + prefix cache 联动特性,使用:
  ```shell
  --enable_chunked_prefill=true
  --enable_prefix_cache=true
  ```

## 图文联合解读

- `pd_architecture.jpg`: **图示解读：**

1. **结构与数据流**：请求经 API Server 进入 xLLM Service（含 Fault Tolerance、Global Scheduler、Global KV Cache Mgr [HBM/mem/ssd]、Instance Mgr、Event Plane、Node Mgr、Planner），由 ETCD Cluster 存储元数据；xLLM 层分为 2 个 Prefill Instance 与 2 个 Decode Instance，各含 Engine、kv cache、KVCacheTransfer 模块，预解码间通过 KVCacheTransfer 迁移缓存。

2. **技术结论**：通过 Global Scheduler 与 Instance Mgr 实现 Prefill/Decode 独立调度，Global KV Cache Mgr 借助多级存储（HBM/mem/ssd）保障 KV 跨实例流转，KVCacheTransfer 完成 Prefill→Decode 的状态接力。

3. **与文档关系**：图直观落地文档所述"三模块"（etcd / xLLM Service / xLLM）架构，并以 Prefill/Decode 解耦印证"独立算力并行执行"的论点，服务于同时压低 TTFT 与 TPOT、提升吞吐的目标。
