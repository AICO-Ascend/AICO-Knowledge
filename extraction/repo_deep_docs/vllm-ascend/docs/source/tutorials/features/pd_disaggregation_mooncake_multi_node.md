# Prefill-Decode Disaggregation (DeepSeek)

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/features/pd_disaggregation_mooncake_multi_node.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/features/pd_disaggregation_mooncake_multi_node.md

# vllm-ascend 文档深度解读

## 【定位】

本文档面向受限资源场景,系统阐述 vLLM-Ascend 在多节点环境下基于 Mooncake(由 Moonshot AI 提供的 Kimi 推理服务后端)实现 Prefill-Decode (PD) 分离 + Expert Parallel (EP) 部署的端到端实践指南,以 DeepSeek-r1-w8a8 模型和 "2P1D" 架构为示例,覆盖物理网络验证、Docker 容器准备、Mooncake 安装编译以及 Prefiller/Decoder 节点启动全流程。

---

## 【技术要点】

1. **目标模型与硬件拓扑**:以 DeepSeek-r1-w8a8 为示例模型,使用 4 台 Atlas 800T A3 服务器构建 "2P1D"(2 Prefiller + 2 Decoder)架构;每台服务器 8 NPUs 与 16 chips 部署一个服务实例(原文: "use 8 NPUs and 16 chips to deploy one service instance")。

2. **节点 IP 与互联要求**:Prefiller 为 192.0.0.1、192.0.0.2,Decoder 为 192.0.0.3、192.0.0.4;物理机需在同一 LAN,节点内 NPU 互联通过 HCCS,跨节点通过 RDMA。

3. **Mooncake 传输机制**:在 Ascend NPU 上,Mooncake 使用 **AscendDirectTransport** 进行 RDMA 数据传输,其端口在 `[20000, 20000 + npu_per_node × 1000)` 区间内随机分配,需与 `kv_port` 错开以避免端口冲突。

4. **Mooncake 版本**:克隆 `https://github.com/kvcache-ai/Mooncake.git` 的 **`v0.3.9`** 分支(`--depth 1`);编译时通过 `cmake .. -DUSE_ASCEND_DIRECT=ON` 启用昇腾直传支持,并安装 `mpich` / `libmpich-dev`。

5. **网络验证命令矩阵**:A3 系列 NPU 编号循环为 `{0..15}`(16 个 NPU),使用 `hccn_tool` 的 `-lldp / -link / -net_health / -netdetect / -gateway / -hccs_ping / -tls` 等子命令;同时通过 `npu-smi info -t spod-info` 获取 `superpodid` 与 `SDID`。

6. **DP 启动脚本**:通过 `examples/external_online_dp/launch_online_dp.py` 启动 `dp-size-local` 个 vLLM 实例,并向 `run_dp_template.sh` 传递 **七个位置参数**;`kv_port` 占用范围 `[kv_port, kv_port + num_chips)`,每个节点需分配唯一 `engine_id` 避免冲突。

---

## 【关键机制与数据】

### 工作原理

**原文 (机制描述):**

> "vLLM-Ascend now supports prefill-decode (PD) disaggregation with EP (Expert Parallel) options."

> "On Ascend NPU, Mooncake uses AscendDirectTransport for RDMA data transfer, which randomly allocates ports within range `[20000, 20000 + npu_per_node × 1000)`."

> "Each P/D node will occupy ports ranging from `kv_port` to `kv_port + num_chips` to initialize socket listeners."

**数据流推断 (基于原文证据):**

- **Prefill 阶段**:Prefiller 节点(192.0.0.1、192.0.0.2)执行 prompt prefill 计算。
- **KV Cache 传输**:通过 Mooncake + AscendDirectTransport (RDMA) 将 KV cache 从 Prefiller 跨节点传输至 Decoder。
- **Decode 阶段**:Decoder 节点(192.0.0.3、192.0.0.4)执行自回归 token 生成。
- **并行维度**:同时支持 DP (Data Parallel) 与 EP (Expert Parallel),通过 `launch_online_dp.py` 启动多个 DP rank。

### 性能数据

原文未涉及具体的吞吐量 (throughput)、首 token 时延 (TTFT)、token 间时延 (TPOT) 或其他 benchmark 数字。所有可量化信息仅为端口范围、循环索引和 DP 规模示例(如 `P: 2; D: 32`)。

---

## 【表格解读】

### 表格 1:kv_port 配置推荐表 (原文逐字还原)

| NPUs per Node | Reserved Port Range | Recommended kv_port |
|---------------|---------------------|---------------------|
| 8             | 20000 - 27999       | >= 28000            |
| 16            | 20000 - 35999       | >= 36000            |

**逐行解读:**

- **8 NPUs 行**:当单节点 NPU 数为 8 时,AscendDirectTransport 随机占用端口区间 `[20000, 20000+8×1000) = [20000, 28000)`,即 20000–27999;因此建议 `kv_port` ≥ 28000,以彻底避开该区间。
- **16 NPUs 行**:当单节点 NPU 数为 16 时,随机占用区间扩展为 `[20000, 20000+16×1000) = [20000, 36000)`,即 20000–35999;建议 `kv_port` ≥ 36000。
- **设计意图**:由于每个 P/D 节点会监听 `[kv_port, kv_port+num_chips)` 范围的 socket,若 `kv_port` 落入 AscendDirectTransport 的随机端口池,会出现启动期 `zmq.error.ZMQError: Address already in use` 间歇性故障——原文以 warning 形式提示该冲突风险。

---

### 表格 2:`launch_online_dp.py` 启动选项表 (原文已截断,逐字还原可见部分)

| Launcher option | Template value | Meaning | Example value | Constraints |
| --- | --- | --- | --- | --- |
| `--dp-size` | `$3` / `--data-parallel-size` | Total DP ranks in the group. | P: `2`; D: `32` | Positive integer; identical within the same group. Total ranks must cover `[0, dp-size)` without overlap. |
| `--tp-size` | `$7` / `--tensor-parallel-si` | _(原文此处被截断)_ | _(未提供)_ | _(未提供)_ |

**已可见行的解读:**

- **`--dp-size` 行**:`launch_online_dp.py` 通过位置参数 `$3` 将总 DP rank 数传递给 `run_dp_template.sh`,后者以 `--data-parallel-size` 形式传给底层 vLLM 实例。示例值 P=`2` 对应 2 个 Prefiller,D=`32` 对应 2 个 Decoder × 每个 16 NPU(= DP 16 × 2 = 32);约束条件要求同一 group 内数值一致,且所有 rank 必须连续无重叠地覆盖 `[0, dp-size)`。
- **`--tp-size` 行**:原文表格在此处被截断,仅露出 `$7 / --tensor-parallel-si` 字段名,无法完整还原后续语义,但可推断 `$7` 是 `run_dp_template.sh` 接收的第七个位置参数,映射为 vLLM 的 `--tensor-parallel-size` 参数。

---

## 【公式解读】

### 公式 1:AscendDirectTransport 端口随机分配区间

**原文逐字保留:**

```
[20000, 20000 + npu_per_node × 1000)
```

**符号含义:**

- **`20000`**:端口区间下界(常数,单位为端口号)。
- **`npu_per_node`**:每节点 NPU 数量(变量),影响区间宽度。
- **`× 1000`**:每个 NPU 预留的端口空间步长,保证 16 个 NPU 的总随机池为 16000 个端口。
- **`)` (右开区间)**:右端开区间,表示上界 `20000 + npu_per_node × 1000` 本身不被包含在随机分配池内,但正好是 `kv_port` 的推荐起点。

**作用:** 告知用户根据 NPU 数量计算 AscendDirectTransport 占用的端口池,并据此设置 `kv_port` 起点以避免冲突——这是与表格 1 中 "Recommended kv_port" 数值直接对应的数学依据。

---

## 【关联】

- **Mooncake(Kimi / Moonshot AI)**:作为 PD 分离的核心 KV cache 传输引擎,通过 AscendDirectTransport 在昇腾 NPU 上提供 RDMA 级 KV 缓存交换能力;上游仓库为 `https://github.com/kvcache-ai/Mooncake`,版本锁定 `v0.3.9`。
- **Expert Parallel (EP)**:DeepSeek-r1-w8a8 这类 MoE 架构的核心并行维度,被本文档明确列入"PD disaggregation with EP options"特性范畴。
- **Data Parallel (DP)**:由 `launch_online_dp.py` 启动器驱动,通过 `examples/external_online_dp/` 目录下的脚本实现多实例协同,与本文档的"2P1D" 多节点架构直接耦合。
- **Atlas 800T A3 / A2 系列**:本文档针对两类硬件分别给出 `{0..15}` 与 `{0..7}` 的 NPU 索引循环(对应 16 NPU vs 8 NPU),表明 PD 分离能力覆盖多代昇腾硬件。
- **HCCS / RDMA 互联**:HCCS(片内高速总线)负责节点内 NPU 互联,RDMA 负责跨节点数据传输,二者共同构成 Mooncake 传输链路的物理承载。
- **下游 vLLM 参数体系**:`--data-parallel-size`、`--tensor-parallel-size` 等参数被封装在 `run_dp_template.sh` 中,体现"启动器 → 模板脚本 → vLLM 实例"的层级化调用关系。

---

## 【使用方法】

### 1. 多节点网络环境验证 (原文提供完整命令集)

- **物理层要求**:同 LAN、节点内 HCCS、节点间 RDMA(原文)。
- **A3 节点验证序列(6 步)**:①`hccn_tool -i $i -lldp -g`(循环 `{0..15}`);②`-link -g`;③`-net_health -g`;④`-netdetect -g`;⑤`-gateway -g`;⑥`-tls -g | grep switch` 确保各节点 TLS 一致。
- **附加步骤**:`cat /etc/hccn.conf` 检查 HCCN 配置;`hccn_tool -i $i -vnic -g` 获取虚拟 NPU IP;`npu-smi info -t spod-info -i $i -c {0,1}` 获取 superpodid 与 SDID;`hccn_tool -i $i -hccs_ping -g address x.x.x.x` 跨节点 PING 测试。
- **A2 节点**:循环索引改为 `{0..7}`,IP 获取改用 `hccn_tool -i $i -ip -g`,跨节点 PING 改用 `-ping`。

### 2. Docker 容器启动 (原文提供完整脚本)

```bash
export IMAGE=m.daocloud.io/quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}
export NAME=vllm-ascend
docker run --rm --name $NAME --net=host --shm-size=1g \
  --device /dev/davinci0 ... --device /dev/davinci15 \
  --device /dev/davinci_manager --device /dev/devmm_svm --device /dev/hisi_hdc \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool \
  -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
  -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
  -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  -v /etc/hccn.conf:/etc/hccn.conf \
  -v /mnt/sfs_turbo/.cache:/root/.cache \
  -it $IMAGE bash
```

**关键配置项:**

- `--net=host`:桥接网络下需额外暴露端口用于多节点通信(原文注释提示)。
- `--device /dev/davinci{0..15}`:挂载 16 个 NPU 设备节点。
- `/etc/hccn.conf` 必须挂载进入容器。

### 3. Mooncake 安装与编译 (原文提供完整命令)

```bash
git clone -b v0.3.9 --depth 1 https://github.com/kvcache-ai/Mooncake.git
cd Mooncake
# 可选: sed -i 's|https://go.dev/dl/|https://golang.google.cn/dl/|g' dependencies.sh
apt-get install mpich libmpich-dev -y
bash dependencies.sh -y
mkdir build && cd build
cmake .. -DUSE_ASCEND_DIRECT=ON
make -j && make install
export LD_LIBRARY_PATH=/usr/local/lib64/python3.12/site-packages/mooncake:$LD_LIBRARY_PATH
```

### 4. Prefiller/Decoder 服务启动 (原文提供脚本链接)

- **入口脚本**:`examples/external_online_dp/launch_online_dp.py`(主仓库 GitHub)。
- **节点模板**:`examples/external_online_dp/run_dp_template.sh`,需在每个节点上修改。
- **参数传递**:启动器传 7 个位置参数至模板脚本(详见表格 2;后 5 个参数因原文截断未完全列出)。
- **端口约束**:每个 P/D 节点监听 `[kv_port, kv_port + num_chips)`;按表格 1 推荐配置,16 NPU 节点 `kv_port` ≥ 36000,8 NPU 节点 `kv_port` ≥ 28000。
- **唯一性要求**:每节点 `engine_id` 必须唯一(原文明确约束)。

> **说明**:原文"Launcher option"表格在 `--tp-size` 行中部截断(`--tensor-parallel-si` 之后的内容缺失),完整 `run_dp_template.sh` 的 `$1–$7` 参数语义需以仓库实际文件为准。
