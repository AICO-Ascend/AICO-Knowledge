# Prefill-Decode Disaggregation (Qwen2.5-VL)

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/features/pd_disaggregation_mooncake_single_node.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/features/pd_disaggregation_mooncake_single_node.md

# 深度解读：vLLM-Ascend Prefill-Decode Disaggregation (Qwen2.5-VL) 单节点部署文档

## 【定位】

本文档面向资源受限的 Atlas 800T A2 单机环境，提供使用 vLLM-Ascend + Mooncake 在 **1P1D（单 Prefiller + 单 Decoder）架构**下部署 **Qwen2.5-VL-7B-Instruct** 的端到端操作指引，涵盖通信环境验证、Docker 容器准备、Mooncake 安装、Prefiller/Decoder 启动、代理服务以及在线验证调用。

---

## 【技术要点】

1. **架构形态**：在 **1 台 Atlas 800T A2 服务器**上，使用 NPU 0 运行 Prefiller、NPU 1 运行 Decoder，二者通过 Mooncake Transfer Engine 交换 KV Cache，构建 "1P1D" PD 分离拓扑；文中提及 "2P1D" 仅作为 ASEND_RT_VISIBLE_DEVICES 与端口差异化扩展思路（原文未展开步骤）。

2. **NPU 通信预检**：使用 `hccn_tool -i $i -lldp -g / -link -g / -net_health -g / -netdetect -g / -gateway -g / -ip -g / -tls -g` 检查设备 0..7 的链路状态（要求 `success` 且 `UP`）、网络健康、IP、网关、TLS（要求跨节点一致）等；同时确认 `/etc/hccn.conf` 在容器内可访问。

3. **跨节点连通性**：以 `hccn_tool -i $i -ping -g address x.x.x.x` 在设备 0..7 上对目标 NPU IP 做 PING 测试（原文用 `x.x.x.x` 作占位）。

4. **运行容器镜像**：`m.daocloud.io/quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`，采用 `--net=host`、`--shm-size=1g`，依次 `--device /dev/davinci0` 至 `/dev/davinci7` + `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`，并挂载 `/usr/local/dcmi`、`/usr/local/Ascend/driver/tools/hccn_tool`、`/usr/local/bin/npu-smi`、Ascend driver lib64/version.info、`/etc/ascend_install.info`、`/etc/hccn.conf`、`/mnt/sfs_turbo/.cache` 等。

5. **Mooncake 0.3.9 安装**：`git clone -b v0.3.9 --depth 1 https://github.com/kvcache-ai/Mooncake.git` → 替换 `dependencies.sh` 中的 `go.dev` URL 为 `golang.google.cn` → `apt-get install mpich libmpich-dev -y` → `bash dependencies.sh -y`（Go 可不装）→ `cmake .. -DUSE_ASCEND_DIRECT=ON` 后 `make -j && make install`，最后将 `/usr/local/lib64/python3.12/site-packages/mooncake` 加入 `LD_LIBRARY_PATH`。

6. **Prefiller/Decoder 角色差异**：两端均用 `vllm serve /model/Qwen2.5-VL-7B-Instruct`，监听端口分别为 **13700**（P）和 **13701**（D），`ASCEND_RT_VISIBLE_DEVICES` 分别为 **0** 与 **1**，并通过 `--kv-transfer-config` 中的 `kv_role` 区分 `kv_producer`（P，端口 **30000**）与 `kv_consumer`（D，端口 **30100**），`kv_connector` 为 `MooncakeConnectorV1`；`prefill`/`decode` 两侧 dp_size、tp_size 均为 1；公共参数：`--tensor-parallel-size 1`、`--seed 1024`、`--served-model-name qwen25vl`、`--max-model-len 40000`、`--max-num-batched-tokens 40000`、`--no-enable-prefix-caching`、`--trust-remote-code`、`--gpu-memory-utilization 0.9`；环境变量统一设 `HCCL_IF_IP=192.0.0.1`、`GLOO_SOCKET_IFNAME=eth0`、`TP_SOCKET_IFNAME=eth0`、`HCCL_SOCKET_IFNAME=eth0`、`OMP_PROC_BIND=false`、`OMP_NUM_THREADS=10`。

---

## 【关键机制与数据】

* **原文工作原理（KV Transfer 视角）**：Prefiller（`kv_producer`）完成 prefill 后将其产生的 KV Cache 经 Mooncake Transfer Engine 推送给 Decoder（`kv_consumer`），两端通过预设的 IP+`kv_port` 协商建立传输通道，文档并未给出 Mooncake 内部 buffer size、segment size 等具体参数。
* **原文数据流**：`vllm serve /model/Qwen2.5-VL-7B-Instruct` 启动 vLLM OpenAI 兼容 API → 客户端请求经 `load_balance_proxy_server_example.py`（监听 `192.0.0.1:8080`，配置 prefiller-hosts=`192.0.0.1:13700`、decoder-hosts=`192.0.0.1:13701`）路由 → Prefiller 完成 prefill → 通过 `MooncakeConnectorV1` 把 KV 推到 Decoder → Decoder 完成后续生成 → 响应回客户端。
* **原文性能数据**：本文档仅含最终 curl 验证片段（`max_completion_tokens: 100`，`temperature: 0`），并未给出 TPS / TTFT / 吞吐基准数（原文无可量化的性能指标）。

---

## 【表格解读】

下表逐字还原原文"Example Proxy for Deployment"中的参数说明表：

| Parameter            | Meaning            |
|----------------------|--------------------|
| `--port`             | Proxy port          |
| `--prefiller-port`   | All prefiller ports |
| `--decoder-ports`    | All decoder ports   |

* `--port：代理服务器自身对外监听端口，示例值为 `8080`，用于后续 `curl http://192.0.0.1:8080/v1/chat/completions` 验证。
* `--prefiller-port：所有 prefiller 实例的端口集合，原文示例只列出 `13700`（单 Prefiller）。
* `--decoder-ports：所有 decoder 实例的端口集合，原文示例只列出 `13701`（单 Decoder）；多实例下需以列表/空格分隔多个端口（原文未给出具体语法）。

---

## 【公式解读】

原文无公式。

---

## 【关联】

* **上游组件**：vLLM-Ascend（`vllm serve`）、Ascend CANN/HCCL 驱动（`hccn_tool`、`/dev/davinci*`）、Mooncake v0.3.9（含 `MooncakeConnectorV1`、Transfer Engine）。
* **下游链路**：通过仓库 `examples/disaggregated_prefill_v1/load_balance_proxy_server_example.py` 提供的代理脚本实现 Prefiller/Decoder 间的请求级负载均衡，使客户端无需感知内部拓扑。
* **外部参考**：原文中"Installation and Compilation Guide"指向 `https://github.com/kvcache-ai/Mooncake?tab=readme-ov-file#build-and-use-binaries`。
* **内部交叉**：文中未给出其他内部特性链接，仅在 2P1D 增量部署中提示需根据需要调整 `ASCEND_RT_VISIBLE_DEVICES` 与端口（无具体引用页面）。

---

## 【使用方法】

* **通信验证**：依次执行 `hccn_tool` 链路/IP/PING/TLS 检查 + `cat /etc/hccn.conf`（容器需挂载）。
* **Docker 启动**：按前述 `--device`/`-v` 参数启动容器并进入 bash。
* **Mooncake 安装**：git v0.3.9 → 替换 go URL → 装 mpich → `dependencies.sh -y` → `cmake -DUSE_ASCEND_DIRECT=ON` → `make -j && make install` → 设 `LD_LIBRARY_PATH`。
* **服务启动**：分别用 `ASCEND_RT_VISIBLE_DEVICES=0/1` 启动 Prefiller（端口 13700，`kv_port=30000`，`kv_role=kv_producer`）与 Decoder（端口 13701，`kv_port=30100`，`kv_role=kv_consumer`）。
* **代理启动**：`python load_balance_proxy_server_example.py --host 192.0.0.1 --port 8080 --prefiller-hosts 192.0.0.1 --prefiller-port 13700 --decoder-hosts 192.0.0.1 --decoder-ports 13701`。
* **业务验证**：`curl http://192.0.0.1:8080/v1/chat/completions` 调用 `qwen25vl`，发送 image_url+text 多模态消息，`max_completion_tokens=100`，`temperature=0`。
* **2P1D 扩展**：按官方文档未单独列步骤，仅"需为每个 P 实例设置不同的 `ASCEND_RT_VISIBLE_DEVICES` 与端口"。
