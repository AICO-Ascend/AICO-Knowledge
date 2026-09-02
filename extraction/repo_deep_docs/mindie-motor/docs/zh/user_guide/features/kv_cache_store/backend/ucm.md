# 在 MindIE Motor 中部署 UCM

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/features/kv_cache_store/backend/ucm.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/features/kv_cache_store/backend/ucm.md

# 「在 MindIE Motor 中部署 UCM」文档深度解读

---

## 【定位】

本文档描述在 MindIE Motor 分布式 PD（Prefill-Decode 分离）推理集群中部署 **UCM (Unified Cache Manager) Prefix Cache** 的完整流程，通过持久化与复用 KVCache 来消除跨请求相同前缀的重复 Prefill 计算，从而降低首字延迟与算力开销。

---

## 【技术要点】

1. **角色分工与 Connector 拓扑**：Prefill 使用 `MultiConnector[Mooncake 传输 Connector, UCMConnector]`——`connectors[0]` 是 Mooncake 传输 Connector（负责 P/D 实时 KV 传输），`connectors[1]` 是 `UCMConnector`（负责跨请求前缀复用）。Decode 仅使用与 Prefill 匹配的 Mooncake Connector，不加载 UCM。
2. **UCM 安装位置**：仅在 Prefill Engine Pod 安装 UCM wheel（`uc_manager-*.whl`），通过在 `boot.sh` 中判断 `ROLE = "prefill"` 后执行 `python3 -m pip install` 完成；Decode 不安装。
3. **存储挂载方案**：提供 4 种挂载方式——StorageClass 动态创建 PVC（`storage_class_name` + `access_mode: ReadWriteMany` + `size: "512Gi"`）、已有 PVC（`claim_name`）、NFS（`server: 192.168.10.100` + `path: /export/ucm`）、HostPath（`host_path_type: DirectoryOrCreate`），挂载目标统一为 `/mnt/ucm`。
4. **dshm_size 与 Cache Buffer 关系**：`dshm_size: "128Gi"`（`/dev/shm`）必须**大于** Cache Store 的 `cache_buffer_capacity_gb` 并预留运行余量；UCM 的 `storage_backends` 路径必须与 Pod 挂载的 `mount_path` **完全一致**。
5. **Mooncake master 配置**：`kv_cache_store_config.backend: "mooncake"`，`port: 50088`，`eviction_high_watermark_ratio: 0.9`，`eviction_ratio: 0.1`——为 P/D 传输提供配套服务，**不是** UCM 的持久化 Store。
6. **UCMConnector 内联配置**：`store_pipeline: "Cache|Posix"`、`storage_backends: "/mnt/ucm"`、`cache_buffer_capacity_gb: 64`、`posix_capacity_gb: 400`，并启用 `enable_event_sync: true` 与 `use_layerwise: true`。

---

## 【关键机制与数据】

**UCM 工作原理**：UCM 通过持久化已计算的 KVCache 到后端存储（Posix + Cache 双层 Pipeline），下次请求到来时若前缀命中已存储的 KVCache，则跳过对应 token 段的 Prefill 计算，显著降低 TTFT。在 PD 分离架构中，UCM 与 Mooncake 各司其职：Mooncake 处理"同一请求在 P/D 不同实例间"的实时 KV 传输；UCM 处理"不同请求之间"的前缀复用。

**数据流（基于文档架构图与命中验证流程）**：

```
请求1（首次） → Prefill Pod → UCMConnector → 写入 Posix(/mnt/ucm) + Cache(/dev/shm)
                                ↓
                          Mooncake Connector → Decode Pod
请求2（相同前缀）→ Prefill Pod → UCMConnector → 命中(hit hbm / hit external) → 跳过重复 Prefill
                                              ↓
                                        Mooncake Connector → Decode Pod
```

**关键性能/容量参数（原文摘录）**：

| 参数 | 原文值 | 作用 |
|------|--------|------|
| `cache_buffer_capacity_gb` | 64 | Cache 层（/dev/shm）容量上限 |
| `posix_capacity_gb` | 400 | Posix 层（/mnt/ucm）容量上限 |
| `dshm_size` | 128Gi | Pod 内 /dev/shm 大小，需 > 64 |
| `storage.size` | 512Gi | 动态 PVC 大小，需 > 400 |
| `eviction_high_watermark_ratio` | 0.9 | Mooncake master 高水位驱逐阈值 |
| `eviction_ratio` | 0.1 | Mooncake master 淘汰比例 |
| `Mooncake port` | 50088 | Mooncake master 端口 |
| `kv_port` | 20001 | Prefill/Decode 传输端口 |
| `dp_size` / `tp_size` | 1 / 2 | Prefill 与 Decode 必须保持一致 |

**验证命中**：连续发送两次相同前缀请求，Prefill Pod 日志中应出现 `hit hbm`（命中 Cache 层）或 `hit external`（命中 Posix 层）的非零计数（原文："第二次请求对应日志中的 `hit hbm` 或 `hit external` 应为非零"）。

---

## 【表格解读】

原文包含 1 张关键表格，位于"常见问题"章节：

| 现象 | 检查项 |
| --- | --- |
| Prefill 无法导入 `ucm` | 检查 `boot.sh` 中的 wheel 路径，以及 wheel 与 Python/CANN/硬件版本是否匹配 |
| `UCMConnector must be connectors[1]` | 保持 Mooncake 传输 Connector 为 `connectors[0]`、UCM 为 `connectors[1]` |
| `/mnt/ucm` 不可写 | 检查 `storage[].mount_path`、PVC/NFS 权限和 `storage_backends` |
| 第二次请求仍未命中 | 确认两次请求前缀完全一致，并检查所有 Prefill Pod 日志 |

**逐行解读**：

- **第 1 行**：`ucm` 模块导入失败通常发生在 Prefill Pod 启动时未正确安装 wheel 文件。检查项指向两个维度——一是 `boot.sh` 中 `pip install` 路径是否正确（原文示例为 `/mnt/weight/packages/uc_manager-*.whl`），二是 wheel 与运行时环境（Python 版本、CANN 版本、硬件平台）的版本兼容性。
- **第 2 行**：该错误信息由 UCMConnector 主动抛出，强制要求 UCM 必须放在 `MultiConnector` 列表的第 1 个索引位置（即 `connectors[1]`）。检查项明确禁止用户把 UCM 错放为 `connectors[0]`，即不得让 UCM 充当 P/D 实时传输角色。
- **第 3 行**：`/mnt/ucm` 是 Pod 内 UCM 写入 KVCache 的目标路径。不可写意味着 Pod 内的 `storage[].mount_path` 与 UCM 配置的 `storage_backends` 路径不一致，或底层 PVC/NFS 权限不足。文档强调二者"完全一致"是写入成功的前提。
- **第 4 行**：第二次请求未命中 KVCache 可能由两种原因导致——请求层面（两次请求的前缀字符串不完全相同，导致哈希不匹配）和部署层面（分布式部署下多个 Prefill Pod 各持有部分 KVCache 切片，需要逐一检查所有 Prefill Pod 日志中的 `hit hbm`/`hit external` 计数）。

---

## 【公式解读】

**原文无公式**。文档中仅包含 JSON 配置片段、Shell 命令与一张 Markdown 表格，未出现任何 LaTeX 公式或伪代码形式的数据表达式。

---

## 【关联】

本文档作为 MindIE Motor 的 PD 分离特性与 Cache Store 子能力的交集文档，与以下模块/特性存在显式或隐式关联：

1. **PD 分离特性（上游/核心依赖）**：通过内部链接 `../../../../design/pd_disaggregation.md#connector-驱动执行计划` 指向 PD 分离设计文档。文档明确指出 `connectors[0]` 可选用 `MooncakeConnectorV1`、`MooncakeHybridConnector` 或 `MooncakeLayerwiseConnector`，不同 Connector 的"执行模式和参数并不相同"，必须参照该设计文档配置，并保证 Prefill 与 Decode 端传输配置相互匹配。这是 UCM 部署的前置条件。
2. **AscendStoreConnector（明确否定关系）**：文档以 IMPORTANT 提示明确"UCM **不是** `AscendStoreConnector` 的 backend"，并警告用户**不要**配置 `"backend": "ucm"`。这表明 `AscendStoreConnector` 是另一条独立的 Cache Store 后端通道，与 UCM 是平行而非包含关系。
3. **Mooncake 传输 Connector（协同依赖）**：UCM 在 PD 场景下必须与 Mooncake 传输 Connector 配合使用——Mooncake 承担 P/D 实例间的实时 KV 传输，UCM 承担跨请求的前缀复用。Decode 端必须使用与 Prefill 端"完全匹配"的 Mooncake Connector（包括 `kv_port`、`dp_size`、`tp_size`）。
4. **Cache Store / 存储基础设施（资源依赖）**：文档为 Cache Store 配置 `/dev/shm`（通过 `dshm_size`）与持久化目录（通过 `storage`），依赖 Kubernetes 的 PVC、NFS、HostPath 等存储机制。
5. **外部依赖 UCM 上游项目**：通过文末链接指向 `https://github.com/ModelEngine-Group/unified-cache-management`、`https://ucm.readthedocs.io/en/latest/getting-started/quickstart_vllm_ascend.html` 与 UCM PipelineStore 文档，表明 UCM 本身是 ModelEngine-Group 维护的独立开源项目，MindIE Motor 仅作集成与适配。

---

## 【使用方法】

**启用方式（UCM 部署完整流程，原文步骤提炼）**：

1. **安装 UCM wheel**：在 `examples/deployer/startup/boot.sh` 中，于 `source "$SCRIPT_DIR/common.sh"` 之后加入：
   ```bash
   if [ "$ROLE" = "prefill" ]; then
       python3 -m pip install /mnt/weight/packages/uc_manager-*.whl
   fi
   ```

2. **配置存储**（在 `motor_deploy_config.storage` 中任选其一）：
   - StorageClass 动态 PVC：`storage_class_name` + `access_mode: "ReadWriteMany"` + `size: "512Gi"` + `mount_path: "/mnt/ucm"`
   - 已有 PVC：`claim_name` + `mount_path: "/mnt/ucm"`
   - NFS：`server: "192.168.10.100"` + `path: "/export/ucm"` + `mount_path: "/mnt/ucm"` + `read_only: false`
   - HostPath：`path` + `mount_path: "/mnt/ucm"` + `host_path_type: "DirectoryOrCreate"`
   - 同时设置 `"dshm_size": "128Gi"`

3. **配置 Mooncake master**（根节点 `kv_cache_store_config`）：
   ```json
   "backend": "mooncake", "port": 50088,
   "eviction_high_watermark_ratio": 0.9, "eviction_ratio": 0.1
   ```

4. **配置 Prefill**（`kv_transfer_config`）：
   - `kv_connector: "MultiConnector"`、`kv_role: "kv_producer"`
   - `connectors[0]`：Mooncake 传输 Connector（如 `MooncakeConnectorV1`，`kv_port: "20001"`，`prefill`/`decode` 各 `dp_size: 1, tp_size: 2`）
   - `connectors[1]`：`UCMConnector`，`kv_role: "kv_both"`，`kv_connector_module_path: "ucm.integration.vllm.ucm_connector"`
   - `ucm_connectors` 内联：`store_pipeline: "Cache|Posix"`、`storage_backends: "/mnt/ucm"`、`cache_buffer_capacity_gb: 64`、`posix_capacity_gb: 400`
   - `enable_event_sync: true`、`use_layerwise: true`

5. **配置 Decode**：直接使用 `kv_connector: "MooncakeConnectorV1"`（或与 Prefill 匹配的其他 Mooncake Connector），`kv_role: "kv_consumer"`，`kv_port: "20001"`，`prefill`/`decode` 段的 `dp_size`、`tp_size` 与 Prefill **保持一致**。

**部署与删除命令**：
```bash
# 部署（在 examples/deployer 目录执行）
python3 deploy.py --config_dir ../infer_engines/vllm/ucm_pd

# 删除（以 user_config.json 中的 job_id 作为命名空间）
bash delete.sh mindie-motor
```

**验证命中命令**：
```bash
# 连续两次发送相同请求
curl -sS http://<节点 IP>:31015/v1/chat/completions \
  -H 'Content-Type: application/json' -d @long-request.json
curl -sS http://<节点 IP>:31015/v1/chat/completions \
  -H 'Content-Type: application/json' -d @long-request.json

# 筛 Prefill Pod 并 grep 命中日志
PREFILL_POD=$(kubectl -n mindie-motor get pods -o name | grep '/vllm-p' | head -n 1)
kubectl -n mindie-motor logs "$PREFILL_POD" --since=10m | \
  grep -E 'hit hbm|hit external'
```

**完整样例路径**：`examples/infer_engines/vllm/ucm_pd/`（原文："完整样例位于 `examples/infer_engines/vllm/ucm_pd/`"）。

## 图文联合解读

- `ucm-motor-architecture.svg`: (图解读失败: HTTP Error 400: Bad Request)
- `ucm-cache-hit-flow.svg`: (图解读失败: HTTP Error 400: Bad Request)
