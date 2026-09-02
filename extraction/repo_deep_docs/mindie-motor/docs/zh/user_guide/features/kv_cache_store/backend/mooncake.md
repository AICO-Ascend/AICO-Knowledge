# Mooncake 后端

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/features/kv_cache_store/backend/mooncake.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/features/kv_cache_store/backend/mooncake.md

# Mooncake 后端文档深度解读

## 【定位】

这篇文档描述 **Mooncake 作为 KV Cache 池化后端**在 mindie-motor 中的两种部署模式（embedded 共享模式与 standalone 独立 store 进程模式）、完整的 `kv_cache_store_config` / `kv_transfer_config` 字段语义、不同昇腾硬件（A2/A3/A5）的环境变量依赖、调优建议，以及在 Atlas 850 超节点上使用 Mooncake 的特殊配置（host 网络 / UB 网卡访问），目的是指导用户在 P/D 分离场景下把 KV Cache 接入由 vllm-ascend 天然集成的 Mooncake 池。

---

## 【技术要点】

1. **后端集成方式**：Mooncake 由 vllm-ascend 天然集成，**无需额外安装任何组件**；仅需在 `kv_cache_store_config` 中设 `"backend": "mooncake"`。
2. **两种 `store_mode`**：
   - `embedded`（默认，`store_mode` 为空或 `"embedded"`）：引擎进程自身贡献 `global_segment_size` 池化内存，引擎挂掉则其贡献的内存失效，适合小规模验证。
   - `standalone`（`store_mode="standalone"`）：由独立 `mooncake_store_service` 进程贡献内存，与引擎生命周期解耦，适合生产部署。
3. **必填参数**：`eviction_high_watermark_ratio` 与 `eviction_ratio` 为 Mooncake 专属参数，会传给 `mooncake_master`；**deploy.py 对 mooncake 后端强制校验这两项，缺失会直接报错**（建议值 0.9 / 0.1）。
4. **standalone 模式架构**：每个 PD 实例 Pod 内由 NodeManager 拉起一个独立的 `mooncake_store_service` 进程；引擎进程 `global_segment_size=0`，仅作为请求方；`mooncake_master` 仍跑在独立 kv-store Pod；store 进程故障由 NodeManager 原地重拉（受 `MOTOR_RESTART_LOCAL_SERVICE` 控制，默认开启）。
5. **双 Connector 链路**：`MultiConnector` 组合 `MooncakeConnectorV1`（P2P 直传，prefill→decode 不落池）+ `AscendStoreConnector`（存池，prefill 入池/decode 出池，`backend="mooncake"`），prefill = `kv_producer`，decode = `kv_consumer`。
6. **入池门槛**：block 入池的前提是**请求 prompt 长度 ≥ 128 token**；`AscendStoreConnector` 按 128 token 的 chunk 粒度判定 `can_save`，短请求不产生 put 流量。
7. **硬件环境变量（CANN ≥ 9.1.0）**：所有硬件必须配 `HCCL_INTRA_ROCE_ENABLE=1` 和 `ASCEND_LOCAL_COMM_RES={"version":"1.3"}`；A3 推荐 `ASCEND_ENABLE_USE_FABRIC_MEM=1`，依赖不满足时回退 `ASCEND_BUFFER_POOL=4:8`；Ascend 950 系列按协议二选一：`ASCEND_GLOBAL_RESOURCE_CONFIG={"comm_resource_config.protocol_desc":["uboe:device"]}`（UBOE）或 `ASCEND_LOCAL_COMM_RES={"version":"1.3"}`（UB）。
8. **端口与通信隔离**：store 独占 HIXL `comm_resource_config.listen_port=26666`；HCCL socket 端口段相对引擎偏移（A2：`HCCL_NPU_SOCKET_PORT_RANGE=16700-16800`；A5：host socket 段 +2000），避免 `EI0014`/`EI0020`。

---

## 【关键机制与数据】

### 工作原理与数据流

- **embedded 模式**：引擎进程自身贡献 `global_segment_size`（例：`"2GB"`）内存给 Mooncake 池，请求侧的 `enable=true`、`backend=mooncake`，eviction 参数由 `deploy.py` 强制校验；引擎挂则其贡献的池化内存失效。
- **standalone 模式**：NodeManager 先于引擎在 Pod 内拉起 `mooncake_store_service`（独占大段 `global_segment_size`，如 `"200GB"`），避免与引擎权重/KV 内存竞争；引擎 `global_segment_size=0`，仅作请求方；master 仍在独立 kv-store Pod；store 故障由 NodeManager 原地重拉，重新注册回 master。
- **数据流**：prefill 通过 `MooncakeConnectorV1` 做 P2P 直传（不经池），同时通过 `AscendStoreConnector` 把 KV 写入 Mooncake 池；decode 既可通过 `MooncakeConnectorV1` 接收直传 KV，也通过 `AscendStoreConnector` 从池中读取。`kv_port="30001"` 用于标识域内节点；`engine_id` 在 P/D 间保持一致作为池化域标识。
- **入池判定**：prompt ≥ 128 token 才进入 128 token chunk 粒度的 `can_save` 判定，凑齐整 chunk 才触发 put。

### 性能/参数数据（原文标注）

- **推荐 eviction 值**（原文）：`eviction_high_watermark_ratio=0.9`、`eviction_ratio=0.1`。
- **embedded 示例段大小**（原文）：`"global_segment_size": "2GB"`。
- **standalone 示例段大小**（原文）：`"global_segment_size": "200GB"`。
- **端口示例**（原文）：`kv_port="30001"`；HIXL store `listen_port=26666`；A2 HCCL socket 偏移 `16700-16800`；A5 host socket 偏移 `+2000`。
- **入池 chunk**（原文）：128 token；建议验证 prompt ≥ 500 token。
- **`global_segment_size` 调优比例**（原文）：建议设为模型 KV Cache 预估大小的 **1.5~2 倍**。
- **`default_kv_lease_ttl` 约束**（原文）：需大于 `ASCEND_CONNECT_TIMEOUT` / `ASCEND_TRANSFER_TIMEOUT`。
- **硬件依赖版本门槛**（原文）：CANN ≥ 9.1.0；A5（Ascend 950 系列）HDK ≥ 25.6 且 mooncake ≥ v0.3.11；A3 推荐 HDK ≥ 26.0 或 HDK ≥ 25.5 + mooncake ≥ v0.3.11 + 灵衢算力网络 ≥ 1.5；A2 HDK ≥ 25.5。
- **A3 SSD offload 对齐**（原文）：开启 `ASCEND_ENABLE_USE_FABRIC_MEM=1` 后，相关内存大小需按 **1GB 对齐**。

---

## 【表格解读】

### 表 1：`kv_cache_store_config` 字段表

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `enable` | `false` | 池化总开关，需配 `true` |
| `backend` | `memcache` | 需配 `"mooncake"` |
| `store_mode` | `embedded` | standalone 模式需配 `"standalone"` |
| `global_segment_size` | 无 | standalone 下为 store 进程贡献的池化内存（如 `"200GB"`） |
| `eviction_high_watermark_ratio` / `eviction_ratio` | 无（**必填**） | 驱逐水位与单次驱逐比例，传递给 `mooncake_master`；deploy.py 强制校验，缺失报错（建议 0.9 / 0.1） |

逐行解读：
- **`enable`**：池化总开关，原文默认 `false`，用 Mooncake 时必须显式打开。
- **`backend`**：选择池化后端实现，默认 `memcache`，使用 Mooncake 时配 `"mooncake"`。
- **`store_mode`**：内存贡献者模式选择，默认 `embedded`（引擎自身贡献），生产部署要配 `"standalone"` 改为独立 store 进程。
- **`global_segment_size`**：池化内存段大小，无默认；embedded 下由引擎贡献（如 `"2GB"`），standalone 下由 store 进程贡献（如 `"200GB"`）。
- **`eviction_high_watermark_ratio` / `eviction_ratio`**：驱逐触发水位与单次驱逐比例，**强制必填**，`deploy.py` 缺一即报错，传给 `mooncake_master`，原文推荐 0.9 / 0.1。

### 表 2：`engine_config.kv_transfer_config` 字段表

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `kv_connector` | — | 需配 `"MultiConnector"` |
| `kv_role` | — | 需配：prefill = `kv_producer`，decode = `kv_consumer` |
| `engine_id` | — | 池化域标识，需配且 P/D 保持一致 |
| `connectors[].MooncakeConnectorV1` | — | P2P 直传（prefill → decode 直接传 KV，不落池）；`prefill`/`decode` 拓扑需与部署一致 |
| `connectors[].AscendStoreConnector` | — | 存池（prefill 入池 / decode 出池）；`backend` 需配 `"mooncake"` |
| `kv_port` | — | 建议显式指定（如 `"30001"`），避免多服务端口冲突 |

逐行解读：
- **`kv_connector`**：外层连接器必须为 `"MultiConnector"`，以便同时承载直传与存池两条链路。
- **`kv_role`**：prefill 端为 `kv_producer`（KV 生产者），decode 端为 `kv_consumer`（KV 消费者）。
- **`engine_id`**：作为池化域标识，P/D 必须保持一致，否则会跨域错配。
- **`connectors[].MooncakeConnectorV1`**：P2P 直传通道，KV 不落池；其 `prefill`/`decode` 的并行度（dp/tp/pp）需与实际部署拓扑一致。
- **`connectors[].AscendStoreConnector`**：池化通道，`backend` 必须配 `"mooncake"`；prefill 端负责入池，decode 端负责出池。
- **`kv_port`**：节点通信端口，建议显式指定（如 `"30001"`）避免多服务端口冲突。

### 表 3：所有硬件必配环境变量

| 环境变量（写入 `env.json`） | 说明 |
|------|------|
| `HCCL_INTRA_ROCE_ENABLE=1` | **必须**。HIXL 底层直连传输走 RoCE 协议，需显式使能才能建连，未配置会导致 KV 传输失败。注意该变量需配在 `motor_engine_prefill_env` / `motor_engine_decode_env` 中并随部署下发到引擎 Pod，仅在部署节点 shell 中 export 不生效 |
| `ASCEND_LOCAL_COMM_RES={"version":"1.3"}` | **必须**。使 ascend_transport 按 v1.3 格式生成本地通信资源，走 client-server 单边通信，ranktable 携带 `device_port`。所有硬件（A2/A5 等）均需配置；standalone 模式下缺失时，store 进程与引擎 worker 共用同一 NPU 会因合并 ranktable 出现重复 device_ip 报 `EI0014: IP is used repeatedly`，与 store 同卡的 worker（如 TP rank 0）block 入池失败 |

逐行解读：
- **`HCCL_INTRA_ROCE_ENABLE=1`**：必须开启，使 HIXL 底层直连传输走 RoCE；必须写入 `env.json` 随部署下发，仅 shell export 不会随 Pod 注入。
- **`ASCEND_LOCAL_COMM_RES={"version":"1.3"}`**：使 ascend_transport 按 v1.3 格式生成本地通信资源（client-server 单边通信），ranktable 携带 `device_port`；缺失时 standalone 模式下 store 与同卡 worker 会因 ranktable 重复 device_ip 触发 `EI0014`，导致 worker 入池失败。

### 表 4：各硬件依赖与差异化环境变量

| 硬件 | 依赖 | 环境变量（写入 `env.json`） | 说明 |
|------|------|------------------------------|------|
| Ascend 950 系列产品 | HDK >= 25.6 且 mooncake >= v0.3.11<br>CANN >= 9.1.0 | **UBOE**：`ASCEND_GLOBAL_RESOURCE_CONFIG={"comm_resource_config.protocol_desc":["uboe:device"]}`<br>**UB**：`ASCEND_LOCAL_COMM_RES={"version":"1.3"}` | 按实际使用的通信协议配置对应环境变量（UBOE / UB 二选一） |
| Atlas 800I/T A3 超节点服务器 | HDK >= 26.0<br>或 HDK >= 25.5 且 mooncake >= v0.3.11<br>CANN >= 9.1.0<br>灵衢算力网络 >= 1.5 | `ASCEND_ENABLE_USE_FABRIC_MEM=1` | **推荐**。启用统一内存地址直传方案。若开启 SSD offload，相关内存大小需按 1GB 对齐，详见 vllm-ascend 文档 [Fabric memory size alignment](https://docs.vllm.ai/projects/ascend/en/latest/user_guide/feature_guide/kv_pool.html#fabric-memory-size-alignment-a3-ascend-enable-use-fabric-mem-1) |
| Atlas 800I/T A3 超节点服务器 | 上述依赖不满足时 | `ASCEND_BUFFER_POOL=4:8` | 配置 NPU Device 上用于聚合与 KV 传输的 buffer 个数与大小（例如 `4:8` 表示 4 个 8MB buffer） |
| Atlas 800I/T A2 推理服务器 | HDK >= 25.5<br>CANN >= 9.1.0 | — | 无需额外环境变量，通用必配项即可 |

逐行解读：
- **Ascend 950 系列**：在通用必配项基础上，按所用通信协议二选一配 `ASCEND_GLOBAL_RESOURCE_CONFIG`（UBOE）或 `ASCEND_LOCAL_COMM_RES`（UB）；前置依赖 HDK ≥ 25.6、mooncake ≥ v0.3.11、CANN ≥ 9.1.0。
- **Atlas 800I/T A3（推荐路径）**：依赖满足时配 `ASCEND_ENABLE_USE_FABRIC_MEM=1`，启用统一内存地址直传；开启 SSD offload 时相关内存大小需按 1GB 对齐。
- **Atlas 800I/T A3（回退路径）**：依赖不满足时配 `ASCEND_BUFFER_POOL=4:8`（4 个 8MB buffer），用于聚合与 KV 传输。
- **Atlas 800I/T A2**：无额外环境变量，依赖 HDK ≥ 25.5、CANN ≥ 9.1.0，仅通用必配项即可。

---

## 【公式解读】

原文无公式（无 LaTeX 或伪代码形式的数学表达式；仅有配置项 JSON/YAML 与 shell 片段）。

---

## 【关联】

- **多套服务共享 KV Store**：通过 `kv_cache_store_config.target_job_id` 复用其他推理服务的 kv_store，行为说明见 [KV 池化 README — 多套服务共享 kv_store](../README.md#多套服务共享-kv_store)。
- **standalone 模式独立 store 进程**：本节与其上一节 embedded 模式互为对照，standalone 章节末尾通过锚点 `#standalone-模式独立-store-进程` 反向链接。
- **vllm-ascend KV Pool 文档（外部）**：原理与排障深入参考，链接 https://docs.vllm.ai/projects/ascend/zh-cn/main/user_guide/feature_guide/kv_pool.html；其中 A3 fabric memory size alignment 子节 https://docs.vllm.ai/projects/ascend/en/latest/user_guide/feature_guide/kv_pool.html#fabric-memory-size-alignment-a3-ascend-enable-use-fabric-mem-1 直接关联到 `ASCEND_ENABLE_USE_FABRIC_MEM=1` 的 SSD offload 对齐约束。
- **双 Connector 链路**：本仓库内 `MooncakeConnectorV1`（P2P 直传）与 `AscendStoreConnector`（存池）共同由 `MultiConnector` 编排，构成 P/D 分离下 KV Cache 流动的完整通道。
- **NodeManager 与 NodeManager 重拉**：`MOTOR_RESTART_LOCAL_SERVICE` 控制 store 进程故障后的原地重拉逻辑，是 standalone 模式下可用性的关键依赖。
- **Atlas 850 超节点特殊配置**：与 `examples/deployer/yaml_template/infer_service_template.yaml`、`examples/deployer/yaml_template/engine_template.yaml`、`examples/deployer/startup/common.sh` 中 `set_a5_engine_env` 直接绑定；后续章节原文截断处预期还有「方式二」等其他 host 网络替代方案。
- **P/D 分离部署**：本文档 standalone 示例以 P/D 分离 + standalone 为典型场景，关联 `motor_engine_prefill_config` / `motor_engine_decode_config` 的 `kv_role` 区分（`kv_producer` / `kv_consumer`）。

---

## 【使用方法】

### 1. embedded 模式（小规模验证）

在 `user_config.json` 中启用（原文示例）：

```json
"kv_cache_store_config": {
  "enable": true,
  "backend": "mooncake",
  "global_segment_size": "2GB",
  "eviction_high_watermark_ratio": 0.9,
  "eviction_ratio": 0.1
}
```

要点：必须显式配 `enable=true`、`backend="mooncake"`、`global_segment_size`（无默认），以及两个 eviction 参数（`deploy.py` 强制校验，缺失报错）。

### 2. standalone 模式（生产部署）

在 `user_config.json` 中启用（原文示例）：

```json
"kv_cache_store_config": {
  "enable": true,
  "backend": "mooncake",
  "store_mode": "standalone",
  "global_segment_size": "200GB",
  "eviction_high_watermark_ratio": 0.9,
  "eviction_ratio": 0.1
}
```

并配置 `motor_engine_prefill_config` / `motor_engine_decode_config`：

```json
"kv_transfer_config": {
  "kv_connector": "MultiConnector",
  "kv_role": "kv_producer",
  "kv_port": "30001",
  "engine_id": "0",
  "kv_connector_extra_config": {
    "connectors": [
      {
        "kv_connector": "MooncakeConnectorV1",
        "kv_role": "kv_producer",
        "kv_port": "30001",
        "kv_connector_extra_config": {
          "prefill": {"dp_size": 1, "tp_size": 2, "pp_size": 1},
          "decode": {"dp_size": 1, "tp_size": 2, "pp_size": 1}
        }
      },
      {
        "kv_connector": "AscendStoreConnector",
        "kv_role": "kv_producer",
        "kv_connector_extra_config": {"backend": "mooncake"}
      }
    ]
  }
}
```

> decode 端结构相同，`kv_role` 改为 `"kv_consumer"`，两个 connector 的 `kv_role` 也均为 `"kv_consumer"`。

### 3. 环境变量（`env.json`，Prefill 与 Decode 保持一致）

通用必配（所有硬件）：

```json
"motor_engine_prefill_env": {
  "HCCL_INTRA_ROCE_ENABLE": "1",
  "ASCEND_LOCAL_COMM_RES": "{\"version\":\"1.3\"}"
}
```

按硬件叠加：
- **Ascend 950 系列**：UBOE 用 `ASCEND_GLOBAL_RESOURCE_CONFIG={"comm_resource_config.protocol_desc":["uboe:device"]}`；UB 用 `ASCEND_LOCAL_COMM_RES={"version":"1.3"}`（二选一）。
- **Atlas 800I/T A3（推荐路径）**：加 `ASCEND_ENABLE_USE_FABRIC_MEM=1`，开启 SSD offload 时内存按 1GB 对齐。
- **Atlas 800I/T A3（回退路径）**：上述依赖不满足时加 `ASCEND_BUFFER_POOL=4:8`。
- **Atlas 800I/T A2**：无需额外环境变量。

> 环境变量须写入 `env.json` 的 `motor_engine_prefill_env` / `motor_engine_decode_env`，随部署下发到引擎 Pod，**仅 shell export 不生效**。

### 4. Atlas 850 超节点 host 网络配置（方式一）

- 默认 `deploy_mode=infer_service_set`：编辑 `examples/deployer/yaml_template/infer_service_template.yaml`，在 `roles` 的 `prefill` 与 `decode` 两段 `spec.template.spec` 下均增加：

  ```yaml
  hostNetwork: true
  dnsPolicy: ClusterFirstWithHostNet
  schedulerName: volcano
  ```

- 若 `motor_deploy_config.deploy_mode=multi_deployment`：改为编辑 `examples/deployer/yaml_template/engine_template.yaml` 中引擎 Pod 的 `spec.template.spec`，加上同样的三个字段。
- 同时编辑 `examples/deployer/startup/common.sh` 中的 `set_a5_engine_env`（由 `roles/engine.sh` 在 Atlas 850 场景调用），补齐对 `GLOO_SOCKET_IFNAME` / `TP_SOCKET_IFNAME` / `HCCL_SOCKET_IFNAME`（按 `/proc/net/route` 自动探测默认网卡）、`HCCL_IF_IP`（取 `HOST_IP` 或 `POD_IP`），以及 `PATH`/`LD_LIBRARY_PATH` 的导出逻辑（原文给出的片段在 `export LD_LIBRARY_PATH="/usr/local/lib:/usr/lib` 处截断，文档未提供完整命令，需以仓库原文为准）。

### 5. 验证与调优

- **验证入池**：用长 prompt（≥ 128 token，建议 500+ token）发起请求，通过 master 侧 `PutStart`/`Keys` 指标确认 block 入池。
- **`global_segment_size`**：建议设为模型 KV Cache 预估大小的 **1.5~2 倍**。
- **`eviction_high_watermark_ratio` / `eviction_ratio`**：高并发场景可适度降低驱逐比例以减少抖动。
- **`default_kv_lease_ttl`**：需大于 `ASCEND_CONNECT_TIMEOUT` / `ASCEND_TRANSFER_TIMEOUT`，避免租约在传输完成前过期。

> **原文未涉及**：standalone 模式下 `mooncake_master` 的独立 Pod 配置细节（仅提及仍运行在独立 kv-store Pod）、`MOTOR_RESTART_LOCAL_SERVICE` 的具体取值与重拉退避策略、`target_job_id` 复用场景的具体 `job_id` 来源。
