# PD-Colocated with Mooncake Multi-Instance

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/features/pd_colocated_mooncake_multi_instance.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/features/pd_colocated_mooncake_multi_instance.md

# PD-Colocated with Mooncake Multi-Instance 文档深度解读

---

## 【定位】

本教程文档解决在 vLLM-Ascend 上部署 **PD 同机部署（PD-Colocated）+ Mooncake 多实例**的问题，演示如何在两台 Atlas 800T A2 节点上各启动一个 vLLM 实例并复用跨节点 KV Cache，验证缓存复用效果与跨节点推理性能。

---

## 【技术要点】

1. **硬件/拓扑前提**：使用 **Qwen2.5-72B-Instruct** 模型，在两台 Atlas 800T A2 节点上各占用 **4 张 NPU 卡**（Instance 1 使用第一节点 NPU [0-3]，Instance 2 使用第二节点 NPU [0-3]），节点间通过 **RoCE 网络**互联，节点内通过 **HCCS** 通信。
2. **多机通信验证流程**：使用 `hccn_tool` 检查端口状态（lldp）、链路状态（link）、健康度（net_health）、IP 配置（netdetect）、网关（gateway）、跨节点 ping、TLS 配置一致性，要求全部 `success` / `UP`，且各节点 tls 设置需一致。
3. **Docker 镜像与设备挂载**：使用 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}` 镜像，`--net=host`、`--shm-size=1g`，挂载 `/dev/davinci0-3`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`，并将宿主机的 `hccn.conf`、`npu-smi`、`Ascend driver tools` 等挂入容器。
4. **Mooncake 安装要点**（可选）：vllm-ascend {{vllm_ascend_version}} 镜像已预装 Mooncake；源码路径 `https://github.com/kvcache-ai/Mooncake.git`，分支 **v0.3.9**，编译选项 `-DUSE_ASCEND_DIRECT=ON`，依赖 `mpich`、`libmpich-dev`，验证输出路径为 `/usr/local/Ascend/ascend-toolkit/latest/python/site-packages/mooncake/__init__.py`。
5. **Mooncake Master 服务参数**：`--port 50088`、`--eviction_high_watermark_ratio 0.95`、`--eviction_ratio 0.05`。
6. **vLLM 启动关键参数**：`--dtype bfloat16`、`--max-model-len 25600`、`--tensor-parallel-size 4`、`--max-num-batched-tokens 4096`、`--gpu-memory-utilization 0.9`，并通过环境变量 `HCCL_INTRA_ROCE_ENABLE=1` 启用 A2 系列的 RoCE 路径。
7. **KV Connector 配置**：`kv_connector=MooncakeConnectorStoreV1`、`kv_role=kv_both`、`use_layerwise=false`、`mooncake_rpc_port=0`、`load_async=true`、`register_buffer=true`；其中 `register_buffer=true` 为 PD-colocated 模式必需项。
8. **Benchmark 配置（AISBench）**：Dataset A（完全随机数据），输入/输出 tokens **1024/10**，总请求数 **100**，并发 **25**，通过 TTFT（Time to First Token）评估缓存复用效果（文档在 Step 2 描述前被截断）。

---

## 【关键机制与数据】

### 工作原理

- **PD 同机部署**：Prefill-Decode 部署在同一实例内部（colocated），区别于 PD 分离部署；通过 `MooncakeConnectorStoreV1` 在 RDMA 链路上以 KV Cache 形式跨节点复用。
- **数据流**：Client 请求 → vLLM 实例（NPU [0-3]）→ 本实例 prefill + decode 同时完成 → 同时把 KV Cache 经 RoCE 写入远端 Mooncake 段（`global_segment_size=107374182400` ≈ 100GB）→ 远端实例下次命中相同前缀时直接从 Mooncake 读取 KV Cache。
- **元数据握手**：metadata_server 设置为 `P2PHANDSHAKE`（点对点握手），绕过集中式元数据服务。
- **协议栈**：`protocol=ascend` 表示走 Ascend 私有协议（非 TCP/socket），结合 `HCCL_INTRA_ROCE_ENABLE=1` 让 HCCL 通信走 RoCE。
- **缓存淘汰策略**：eviction_high_watermark_ratio=0.95 触发后，按 eviction_ratio=0.05（5%）淘汰。
- **传输粒度**：`use_layerwise=false` 表示一次性整段传输（适合跨节点带宽充足场景）；`true` 表示逐层传输（适合单节点内存受限场景）。
- **异步加载**：`load_async=true` 与 `mooncake_rpc_port=0`（自动分配端口）配合，避免 decode 阻塞。

### 性能数据

- 原文仅给出 **Benchmark 测试配置**（Dataset A、1024/10 tokens、100 请求、并发 25），以及 Step 1 的基准变量 **TTFT1**（发送给 Instance 1 的首 token 时延）。
- 文档在 Step 2 描述前被截断，未给出最终的 TTFT 数值或缓存命中率等定量指标 → **原文未提供完整的性能结果**。

---

## 【表格解读】

### 表 1：Mooncake Master Service 启动参数

| Parameter                     | Value | Explanation                           |
| ----------------------------- | ----- | ------------------------------------- |
| port                          | 50088 | Port for the master service           |
| eviction_high_watermark_ratio | 0.95  | High watermark ratio (95% threshold)  |
| eviction_ratio                | 0.05  | Percentage to evict when full (5%)    |

**解读**：这是启动 `mooncake_master` 进程的端口与淘汰策略配置。`port=50088` 为 Mooncake Master 的 RPC 端口，客户端通过 `mooncake.json` 中的 `master_server_address` 连接该端口；`eviction_high_watermark_ratio=0.95` 表示当 KV Cache 占用达到 95% 容量时启动淘汰；`eviction_ratio=0.05` 表示每次淘汰 5% 的条目（5% × 容量），从而保持写放大可控。

### 表 2：mooncake.json 配置参数

| Parameter              | Value                              | Explanation                  |
| ---------------------- | ---------------------------------- | ---------------------------- |
| metadata_server        | P2PHANDSHAKE                       | Point-to-point handshake mode|
| protocol               | ascend                             | Ascend proprietary protocol  |
| master_server_address  | 90.90.100.188:50088 (for example)  | Master server address        |
| global_segment_size    | 107374182400                       | Size per segment (100GB)     |

**解读**：这是每个 vLLM 实例的客户端 Mooncake 配置。`metadata_server=P2PHANDSHAKE` 跳过集中元数据服务，让两端直接握手（适合两节点 PoC）；`protocol=ascend` 选择 Ascend 私有协议，配合 HCCL/RoCE 链路；`master_server_address` 指向 Master 节点 IP:50088；`global_segment_size=107374182400` 即 **100GB**，表示每个 NPU 端预留给 KV Cache 的段大小，决定单实例可缓存的容量上限。

### 表 3：vLLM KV Transfer 配置参数

| Parameter         | Value                     | Explanation                       |
| ----------------- | ------------------------- | --------------------------------- |
| kv_connector      | MooncakeConnectorStoreV1  | Use StoreV1 version               |
| kv_role           | kv_both                   | Enable both produce and consume   |
| use_layerwise     | false                     | Transfer entire cache (see note)  |
| mooncake_rpc_port | 0                         | Automatic port assignment         |
| load_async        | true                      | Enable asynchronous loading       |
| register_buffer   | true                      | Required for PD-colocated mode    |

**解读**：这是 `--kv-transfer-config` JSON 内的关键参数。`kv_connector=MooncakeConnectorStoreV1` 选定 v1 版连接器；`kv_role=kv_both` 让单实例既充当 producer（prefill 后写入 KV）又充当 consumer（命中前缀时读取），契合 PD 同机部署"自产自用+跨节点复用"的需求；`use_layerwise=false` 选择整段传输（跨节点带宽充足时延迟更低）；`mooncake_rpc_port=0` 让系统自动分配端口避免冲突；`load_async=true` 让 KV 加载与 decode 计算流水线重叠；`register_buffer=true` 是 PD-colocated 模式的强制要求，确保 RDMA 缓冲区预先注册以降低握手开销。文档附注说明：`use_layerwise=false` 适合跨节点（带宽充足），`true` 适合单节点内存受限。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档涉及的多模块/上下游关系：

- **Mooncake 项目**（[kvcache-ai/Mooncake](https://github.com/kvcache-ai/Mooncake)）：作为 KV Cache 传输与存储的底层依赖，提供 Master 服务、Transfer Engine；本文档固定使用 `v0.3.9` 分支并以 `-DUSE_ASCEND_DIRECT=ON` 编译以启用对 Ascend 直通 RDMA 的支持。
- **vLLM-Ascend**（镜像 `quay.io/ascend/vllm-ascend`）：将 Mooncake 集成进 vLLM 的 KV Connector 框架，提供 `MooncakeConnectorStoreV1` 连接器。
- **HCCL / RoCE**：A2 系列通过 `HCCL_INTRA_ROCE_ENABLE=1` 启用 RoCE 路径，使跨节点 KV 传输复用 HCCL 通信栈。
- **Atlas 800T A2 硬件层**：NPU 卡通过 HCCS（节点内）+ RoCE（节点间）协同工作，KV Cache 跨节点访问性能依赖此拓扑。
- **AISBench 性能评测**：作为基准测试工具，文中作为推荐引用，但本文档未给出具体链接/版本号（原文未涉及）。
- **PD-colocated vs PD-disaggregated**：`kv_role=kv_both` + `register_buffer=true` 表明本文档聚焦"同机部署"模式，与 P/D 分离部署为并列分支（原文未涉及）。

注：原文未提供文档内部的交叉链接，仅有 Mooncake GitHub 外部链接（已在表格中体现）。

---

## 【使用方法】

### 1. 网络验证

```bash
# 单节点验证（5 类检查：lldp / link / net_health / netdetect / gateway）
for i in {0..7}; do hccn_tool -i $i -lldp -g | grep Ifname; done
for i in {0..7}; do hccn_tool -i $i -link -g ; done
for i in {0..7}; do hccn_tool -i $i -net_health -g ; done
for i in {0..7}; do hccn_tool -i $i -netdetect -g ; done
for i in {0..7}; do hccn_tool -i $i -gateway -g ; done

# 检查 /etc/hccn.conf 必须存在
cat /etc/hccn.conf

# 获取 NPU IP
for i in {0..7}; do hccn_tool -i $i -ip -g; done

# 跨节点 ping
for i in {0..7}; do hccn_tool -i $i -ping -g address x.x.x.x; done

# TLS 一致性检查
for i in {0..7}; do hccn_tool -i $i -tls -g ; done | grep switch
```

### 2. Docker 启动

每节点执行一次，挂载 hccn.conf 与 Ascend driver：

```bash
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}
export NAME=vllm-ascend
docker run --rm --name $NAME --net=host --shm-size=1g \
  --device /dev/davinci0 --device /dev/davinci1 \
  --device /dev/davinci2 --device /dev/davinci3 \
  --device /dev/davinci_manager --device /dev/devmm_svm \
  --device /dev/hisi_hdc \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool \
  -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
  -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
  -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  -v /etc/hccn.conf:/etc/hccn.conf \
  -v /root/.cache:/root/.cache \
  -it $IMAGE bash
```

### 3. （可选）Mooncake 安装

```bash
git clone -b v0.3.9 --depth 1 https://github.com/kvcache-ai/Mooncake.git
cd Mooncake && git submodule update --init --recursive
apt-get install mpich libmpich-dev -y
bash dependencies.sh -y
mkdir build && cd build
cmake .. -DUSE_ASCEND_DIRECT=ON && make -j && make install
# 验证
python -c "import mooncake; print(mooncake.__file__)"
```

### 4. 启动 Mooncake Master（任一节点容器内）

```bash
docker exec -it vllm-ascend bash
cd /vllm-workspace/Mooncake
mooncake_master --port 50088 \
  --eviction_high_watermark_ratio 0.95 \
  --eviction_ratio 0.05
```

### 5. 创建 mooncake.json

```json
{
    "metadata_server": "P2PHANDSHAKE",
    "protocol": "ascend",
    "device_name": "",
    "master_server_address": "<your_server_ip>:50088",
    "global_segment_size": 107374182400
}
```

### 6. 部署 vLLM 实例（两个节点各一份，仅改 `--host`/`--port`）

```bash
export LD_LIBRARY_PATH=/usr/local/Ascend/ascend-toolkit/latest/python/site-packages:$LD_LIBRARY_PATH
export MOONCAKE_CONFIG_PATH="/vllm-workspace/mooncake.json"
export HCCL_INTRA_ROCE_ENABLE=1

vllm serve <path_to_your_model>/Qwen2.5-72B-Instruct/ \
--served-model-name qwen \
--dtype bfloat16 \
--max-model-len 25600 \
--tensor-parallel-size 4 \
--host <your_server_ip> \
--port 8002 \
--max-num-batched-tokens 4096 \
--gpu-memory-utilization 0.9 \
--kv-transfer-config '{
      "kv_connector": "MooncakeConnectorStoreV1",
      "kv_role": "kv_both",
      "kv_connector_extra_config": {
          "use_layerwise": false,
          "mooncake_rpc_port": "0",
          "load_async": true,
          "register_buffer": true
      }
  }'
```

### 7. Benchmark（AISBench + Dataset A）

- 测试集：Dataset A（完全随机数据）
- 输入/输出 tokens：**1024/10**
- 总请求：**100**
- 并发：**25**
- Step 1：发送 Dataset A → Instance 1，记录 TTFT1（无缓存基线）
- Step 2 及后续步骤原文被截断，**原文未涉及**具体如何对比 TTFT1 vs TTFT2 以量化缓存命中收益。
