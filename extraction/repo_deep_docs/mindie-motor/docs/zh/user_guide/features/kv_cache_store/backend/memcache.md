# MemCache 后端

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/features/kv_cache_store/backend/memcache.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/features/kv_cache_store/backend/memcache.md

# MemCache 后端 文档深度解读

## 【定位】

这篇文档描述 mindie-motor（昇腾自研推理集群管理框架）的 MemCache 后端，作为默认的 KV 池化（KV pooling）后端在 P/D（Prefill/Decode）分离推理架构下提供跨请求、跨引擎的 KV Cache 共享能力，并涵盖 LocalService 部署模式、KV events 缓存感知调度广播、以及尚处于 WIP 阶段的 UBSIO/SSD 三级缓存接入。

---

## 【技术要点】

1. **默认池化后端与零安装特性**：MemCache 基于 memcache_hybrid 提供 KV 池化能力，已预装在 Motor 镜像中，无需额外安装步骤。

2. **双重配置入口**：`AscendStoreConnector` 中通过 `"backend": "memcache"` 启用；而在 `kv_cache_store_config` 下，还支持设置 `local_service_mode` 与 `target_job_id` 两个可选参数：
   - `local_service_mode` 默认值随硬件变化——Atlas 800I A2 推理服务器 / Atlas 850 超节点服务器为 `inprocess`；Atlas 800I A3 超节点服务器为 `standalone`。
   - `target_job_id` 用于复用其他推理服务的 kv_store（值取自目标服务的 `motor_deploy_config.job_id`）；未配置、与自身 `job_id` 相同、或目标 kv_store 不可用时，退回在本 namespace 新建 kv_store。

3. **LocalService 两进程模式差异**：
   - `inprocess`（同进程）：DRAM 由 vLLM 进程内分配，每个进程的 `dram.size` 在 `mmc-local-inprocess.conf` 中配置；无独立 LocalService 进程，集成在 vLLM 内。
   - `standalone`（独立进程）：使用独立 LocalService，对应 `mmc-local-standalone.conf`；vLLM 侧需设 `dram.size=0GB`；LocalService 由 NodeManager 自动拉起并监控。

4. **KV events ZMQ PUB 广播机制**：MetaService 在 KV 块元数据写入/删除后通过 ZMQ PUB 广播三类事件（`STORED` / `REMOVED` / `CLEARED`），Motor 的 kv-conductor 订阅事件后借助 `backend_id` 计算 KV 亲和度，驱动缓存感知 prefill 调度，使请求优先路由到已缓存前缀的节点，复用 KV、降低 TTFT。默认关闭，开启需三步：解除脚本注释并对齐 `kv_events_model_name` / `kv_events_block_size` 与 `kv_conductor_config` 的 `model_path` / `block_size`；在 `kv_conductor_config.pool_endpoint` 配置广播地址（如 `"tcp://mindie-motor-kvs-master:5557"` 或 `"tcp://*:5557"`，端口须与脚本 `kv_events_endpoint` 一致，`*` 会自动替换为 K8s 注入的 `KVS_MASTER_SERVICE` 域名）；`ock.mmc.local_service.backend_id` 由 deployer 在部署时自动替换为本节点 Pod IP。

5. **MultiConnector 补丁（必装）**：vLLM 上游 `MultiConnector` 缺少 `get_kv_connector_kv_cache_events()` 实现，会静默丢弃 worker 侧 AscendStoreConnector 收集的 KV 事件；vllm-ascend 已替换为 `AscendMultiConnector`，需在部署时应用 `examples/deployer/patch/vllm_ascend_multi_connector_kv_events.patch`（一个补丁适配 v0.20.2 ~ v0.26.0）。前提：memcache_hybrid 需为包含 KvEvent 功能（PR #334 起）的版本，否则 MetaConfig 不识别 `kv_events_*` 字段。

6. **UBSIO/SSD 三级缓存（HBM → DRAM → SSD）**：该特性文档明确标注"尚不成熟，暂不推荐在生产环境中使用"，启用需对生产硬件、负载做针对性配置。使用官方 `partition_disks.sh` 脚本对 NVMe 裸盘分区；分区数 `device_count`：`standalone` 为 1，`inprocess` 为 `endpoints × local_world_size`。启用步骤包括：编辑对应 conf 文件设置 `ock.mmc.local_service.storage.enabled = true`、配置 `ubsio.disk.path`、`ubsio.wcache.evict_water_level`（`standalone` = `85`，`inprocess` = `0`）、`ubsio.standalone.device_count`（`standalone` = `1`，`inprocess` = `endpoints × local_world_size`）。

7. **配置模板同步机制**：所有 memcache 内部配置项（DRAM 池大小、通信协议、SSD 缓存、UBSIO 参数等）均在 `mmc-local-inprocess.conf` 中管理，模板位于 `examples/deployer/startup/roles/kv_store_backends/memcache/`，部署时由 `common.sh` 自动同步到 `$CONFIG_PATH/`。

---

## 【关键机制与数据】

**KV events 事件流**（原文）：
MetaService（ZMQ PUB）→ 广播事件 STORED/REMOVED/CLEARED → kv-conductor 订阅 → 借助 `backend_id` 计算 KV 亲和度 → 缓存感知 prefill 调度 → 请求优先路由到已缓存前缀的节点。Coordinator 启动注册时将订阅地址告知 kv-conductor。K8s Service `mindie-motor-kvs-master` 已默认暴露 `kv-events: 5557` 端口。

**backend_id 注入机制**（原文）：deployer 在部署时自动将每个引擎节点 LocalService 的 `ock.mmc.local_service.backend_id` 替换为本节点 Pod IP，无需用户配置；kv-conductor 据此区分 KV 块所属节点。

**SSD 分区与配置对应关系**（原文）：
- 目标 conf 文件取决于 `local_service_mode`：`inprocess` → `mmc-local-inprocess.conf`；`standalone` → `mmc-local-standalone.conf`。
- `ubsio.wcache.evict_water_level`：`standalone` = `85`，`inprocess` = `0`。
- `ubsio.standalone.device_count`：`standalone` = `1`，`inprocess` = `endpoints × local_world_size`。

**配置同步路径**（原文）：模板目录 `examples/deployer/startup/roles/kv_store_backends/memcache/` → `common.sh` 自动同步 → `$CONFIG_PATH/`。

---

## 【表格解读】

**LocalService 部署模式对比表**（原文逐字还原）：

| 模式 | 值 | DRAM 分配方式 | LocalService 进程 | 适用场景 |
|------|-----|--------------|-------------------|----------|
| **同进程** | `inprocess` | vLLM 进程内分配；每个进程的 `dram.size` 在 `mmc-local-inprocess.conf` 中配置 | 无独立进程，集成在 vLLM 内 | 部署简单，资源占用少 |
| **独立进程** | `standalone` | 独立 LocalService 使用 `mmc-local-standalone.conf`；vLLM 侧 `dram.size=0GB` | NodeManager 自动拉起并监控 | 内存隔离更好，LS 崩溃不影响 vLLM |

**逐行解读**：

- **同进程 / `inprocess` 行**：DRAM 池化内存由 vLLM 进程内分配，每个进程的 DRAM 上限 `dram.size` 在 `mmc-local-inprocess.conf` 中配置；不产生独立 LocalService 进程，LocalService 逻辑被集成进 vLLM；适用场景为追求部署简洁与低资源占用的部署。
- **独立进程 / `standalone` 行**：使用独立的 LocalService 进程，配套 `mmc-local-standalone.conf`，且 vLLM 侧需设 `dram.size=0GB`（DRAM 由 LocalService 独占）；该 LocalService 由 NodeManager 自动拉起并监控；适用场景为对内存隔离要求更高、避免 LS 故障传导到 vLLM 的部署。

---

## 【公式解读】

原文无公式（文档主体为配置说明、部署指引、表格与操作步骤，未引入数学公式或伪代码块）。

---

## 【关联】

- **KV 池化默认入口** — 本文与 `../README.md#多套服务共享-kv_store`（内部链接，文档内引用点）直接关联：`target_job_id` 的语义、跨服务复用回退行为（未配置 / 与自身 `job_id` 相同 / 目标不可用 → 本 namespace 新建）的详细说明均指向该 README 章节。
- **MemCache 分离部署** — `local_service_mode` 二选一机制与硬件默认值的细节差异（含 Atlas 800I A3 超节点服务器场景），通过外部链接 *MemCache 分离部署方案*（https://gitcode.com/Ascend/memcache/wiki/MemCache+vLLM+A3%E5%88%86%E7%A6%BB%E9%83%A8%E7%BD%B2%E6%A1%88%E4%BE%8B.md）给出"两种模式的差异和部署示例"。
- **UBSIO 多级池化** — SSD 三级缓存的分区细节、`ubsio.*` 参数语义与多级池化原理，通过外部链接 *MemCache Wiki — 多级池化 UBSIO 配置指南*（https://gitcode.com/Ascend/memcache/wiki/【WIP】多级池化 UBSIO配置指南.md）展开。
- **下游 vLLM 集成** — 通过 `vllm_ascend_multi_connector_kv_events.patch`（`examples/deployer/patch/`）与 vllm-ascend 的 `AscendMultiConnector` 实现耦合，并以来源仓库 memcache_hybrid 的 KvEvent 能力（PR #334 起）为依赖前置。
- **K8s 部署支撑** — MetaService 广播地址可通过 K8s 注入的 `KVS_MASTER_SERVICE` 域名解析；K8s Service `mindie-motor-kvs-master` 默认暴露 `kv-events: 5557` 端口；NodeManager 在 `standalone` 模式下负责 LocalService 的生命周期。
- **配置模板与部署流程** — 配置模板位于 `examples/deployer/startup/roles/kv_store_backends/memcache/`，分区脚本为官方 `partition_disks.sh`；两者共同构成 memcache 后端的部署前置。

---

## 【使用方法】

**1. 启用 MemCache 后端**（原文）：
- 在 `AscendStoreConnector` 配置：
  ```json
  "backend": "memcache"
  ```
- 在 `kv_cache_store_config` 配置（可选扩展）：
  ```json
  "kv_cache_store_config": {
    "backend": "memcache",
    "local_service_mode": "standalone",
    "target_job_id": "service-a"
  }
  ```
- 如需覆盖硬件默认值，需在 `user_config.json` 中显式配置 `local_service_mode`。

**2. 开启 KV events 广播（缓存感知调度）**（原文，按三步）：
- 解除 `examples/deployer/startup/roles/kv_store_backends/memcache/memcache_meta_service.py` 中「KV events 广播」配置块的注释，按需填写 `kv_events_model_name` / `kv_events_block_size`（须与 `kv_conductor_config` 中 `model_path` / `block_size` 一致），重启 kv_store。
- 在 `kv_conductor_config.pool_endpoint` 配置 MetaService 的广播地址（如 `"tcp://mindie-motor-kvs-master:5557"`，端口须与脚本 `kv_events_endpoint` 一致；可用 `"tcp://*:5557"` 自动替换为 `KVS_MASTER_SERVICE` 域名）。
- `ock.mmc.local_service.backend_id` 由 deployer 自动注入为 Pod IP，无需手配。
- 部署时应用 `examples/deployer/patch/vllm_ascend_multi_connector_kv_events.patch`。

**3. 启用 UBSIO/SSD 三级缓存**（原文，⚠️ 不推荐生产使用）：
- 在所有启用 SSD 缓存的节点执行 `partition_disks.sh`，按 `device_count` 规划分区数（`standalone`=1，`inprocess`=`endpoints × local_world_size`），脚本输出 `ubsio.disk.path`。
- 根据 `local_service_mode` 选择目标 conf 文件：`inprocess` → `mmc-local-inprocess.conf`；`standalone` → `mmc-local-standalone.conf`。
- 编辑对应 conf：`ock.mmc.local_service.storage.enabled = true`、`ubsio.disk.path`、按模式设置 `ubsio.wcache.evict_water_level`（`standalone`=85，`inprocess`=0）与 `ubsio.standalone.device_count`（`standalone`=1，`inprocess`=`endpoints × local_world_size`）。
