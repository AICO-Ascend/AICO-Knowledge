# Ray Distributed (Qwen3-235B-A22B)

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/features/ray.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/features/ray.md

# vllm-ascend Ray 分布式 (Qwen3-235B-A22B) 文档深度解读

## 【定位】

本文档是 vllm-ascend 在华为昇腾 (Ascend) NPU 上使用 Ray 分布式框架进行 **多节点推理部署** 的完整操作指南,针对 Qwen3-235B-A22B 大模型这类单机无法容纳的模型场景,详细阐述从多节点通信环境验证、Ray 集群搭建,到最终启动在线推理服务的全流程。

---

## 【技术要点】

1. **三步部署流程**:多节点推理需依次完成——验证多节点通信环境、搭建并启动 Ray 集群、在多节点上启动在线推理服务。

2. **NPU 物理层要求**:节点需处于同一局域网,所有 NPU 通过光模块互联且连接状态正常。

3. **网络验证命令序列**(每个节点执行):
   - `hccn_tool -i $i -lldp -g` 检查远程交换机端口
   - `hccn_tool -i $i -link -g` 获取以太网端口状态 (UP/DOWN)
   - `hccn_tool -i $i -net_health -g` 检查网络健康状态
   - `hccn_tool -i $i -netdetect -g` 查看网络检测的 IP 配置
   - `hccn_tool -i $i -gateway -g` 查看网关配置
   - `cat /etc/hccn.conf` 查看 NPU 网络配置
   - 其中 `$i` 遍历 `{0..7}`,即 **8 个 NPU 设备**

4. **容器化部署核心参数**:
   - `--net=host` 网络模式
   - `--shm-size=1g` 共享内存 1GB
   - 挂载 `/root/.cache` 作为**所有节点共享目录**(关键)
   - 暴露 8 个 `/dev/davinci0-7` 设备 + `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`
   - 挂载驱动路径:`/usr/local/dcmi`、`hccn_tool`、`npu-smi`、Ascend driver lib64 等

5. **Ray 集群启动关键环境变量**:
   - `HCCL_IF_IP={local_ip}` (HCCL 通信 IP)
   - `GLOO_SOCKET_IFNAME={nic_name}` 与 `TP_SOCKET_IFNAME={nic_name}` (通信网卡名)
   - `RAY_EXPERIMENTAL_NOSET_ASCEND_RT_VISIBLE_DEVICES=1` (Ray 2.1+ 避免设备识别问题)
   - `ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7` (指定使用全部 8 张 NPU)
   - **关键约束**:环境变量必须在启动 Ray 集群**之前**设置,更新需重启 Ray

6. **两种并行策略**:
   - **张量并行 + 流水线并行**:`tensor-parallel-size=NPU/节点数`,`pipeline-parallel-size=节点数` (例如 2 节点 × 8 NPU → TP=8, PP=2)
   - **纯张量并行**:`tensor-parallel-size=集群总 NPU 数` (例如 2 节点 × 8 NPU → TP=16)
   - 均配合 `--enable-expert-parallel` 启用专家并行 (MoE 模型特性)

---

## 【关键机制与数据】

### 工作原理与数据流

- **分布式执行器后端**:通过 `--distributed-executor-backend ray` 将 vLLM 的推理任务调度交给 Ray 集群,Ray 将 NPU 资源视为统一资源池,屏蔽节点差异 (原文:"In the container, you can use vLLM as if all NPUs were on a single node. vLLM will utilize NPU resources across all nodes in the Ray cluster.")。

- **节点发现机制**:Worker 节点通过 `ray start --address='{head_node_ip}:6379'` 加入 Head 节点,默认端口 **6379**;Ray Dashboard 默认地址为 `http://localhost:8265`。

- **集群验证命令**:启动后执行 `ray status` 与 `ray list nodes` 验证节点数量与 NPU 数量是否正确。

- **推理启动位置**:原文强调"You only need to run the vllm command on one node."——只需在单一节点执行 `vllm serve`,Ray 会自动分发至所有节点。

### 性能相关数据(原文明确出现的)

| 参数 | 数值 | 来源 |
|---|---|---|
| Qwen3-235B-A22B max-model-len | 8192 | 原文 `--max-model-len 8192` |
| max-num-seqs | 25 | 原文 `--max-num-seqs 25` |
| gpu-memory-utilization | 0.9 | 原文 `--gpu-memory-utilization 0.9` |
| seed | 1024 | 原文 `--seed 1024` |
| 示例节点规模 | 2 节点 × 8 NPU = 16 NPU | 原文 "16 NPUs across 2 nodes (8 NPUs per node)" |
| curl max_completion_tokens | 100 | 原文请求示例 |
| 容器 shm-size | 1g | 原文 `--shm-size=1g` |

---

## 【表格解读】

**原文无表格** (文档以命令块、列表、说明文字形式组织内容,未使用 markdown 表格)。

---

## 【公式解读】

**原文无公式** (文档为操作指南性质,未包含数学公式或伪代码算法)。

---

## 【关联】

由于本文件为独立 feature 文档且**原文未包含内部链接**,无法依据文末链接信息建立与其他特性的直接关联。但从文档描述的工作流与命令可推断以下关联点:

- **Qwen3-235B-A22B 模型**:文档标题明示针对该模型,配合 `--enable-expert-parallel` 标志说明其依赖 **MoE (Mixture of Experts) 专家并行** 机制。
- **vLLM 框架**:核心使用 `vllm serve` 命令,作为推理服务入口;`--trust-remote-code` 表明依赖远程代码加载机制。
- **Ray 集群框架**:作为分布式执行器后端,版本需 ≥ 2.1 (由 `RAY_EXPERIMENTAL_NOSET_ASCEND_RT_VISIBLE_DEVICES` 提示推断)。
- **HCCL 集合通信库**:`HCCL_IF_IP` 环境变量表明底层依赖华为 HCCL (类似 NCCL) 进行 NPU 间高性能通信。
- **Ascend 驱动栈**:`hccn_tool`、`npu-smi`、`dcmi` 等命令属于昇腾驱动工具链,容器需挂载相应路径。
- **多节点并行策略**:文档开篇提到"张量并行或流水线并行",后续章节以具体示例展开,与 vLLM 上游的并行特性保持一致。

---

## 【使用方法】

### 1. 通信环境验证(每节点执行)
```bash
for i in {0..7}; do hccn_tool -i $i -lldp -g | grep Ifname; done
for i in {0..7}; do hccn_tool -i $i -link -g; done
for i in {0..7}; do hccn_tool -i $i -net_health -g; done
for i in {0..7}; do hccn_tool -i $i -netdetect -g; done
for i in {0..7}; do hccn_tool -i $i -gateway -g; done
cat /etc/hccn.conf
```
所有结果必须为 `success` 且状态为 `UP`。

### 2. NPU 互联验证
- 获取 NPU IP:`for i in {0..7}; do hccn_tool -i $i -ip -g | grep ipaddr; done`
- 跨节点 PING 测试:`hccn_tool -i 0 -ping -g address 10.20.0.20`

### 3. 容器启动(全部节点)
```bash
export IMAGE=quay.nju.edu.cn/ascend/vllm-ascend:{{ vllm_ascend_version }}
docker run --rm --name vllm-ascend --net=host --shm-size=1g \
  --device /dev/davinci0 ... --device /dev/davinci7 \
  --device /dev/davinci_manager --device /dev/devmm_svm --device /dev/hisi_hdc \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /path/to/shared/cache:/root/.cache \
  -it $IMAGE bash
```
注意:`/root/.cache` 必须为**所有节点可访问的共享目录**。

### 4. 启动 Ray 集群
**Head 节点**:
```shell
export HCCL_IF_IP={local_ip}
export GLOO_SOCKET_IFNAME={nic_name}
export TP_SOCKET_IFNAME={nic_name}
export RAY_EXPERIMENTAL_NOSET_ASCEND_RT_VISIBLE_DEVICES=1
export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
ray start --head
```

**Worker 节点**:
```shell
# 同样设置上述环境变量
ray start --address='{head_node_ip}:6379' --node-ip-address={local_ip}
```

验证命令:`ray status`、`ray list nodes`

### 5. 启动推理服务(任一节点执行)
**方案 A:张量并行 + 流水线并行** (2 节点 × 8 NPU 示例)
```shell
vllm serve Qwen/Qwen3-235B-A22B \
  --distributed-executor-backend ray \
  --pipeline-parallel-size 2 \
  --tensor-parallel-size 8 \
  --enable-expert-parallel \
  --seed 1024 \
  --max-model-len 8192 \
  --max-num-seqs 25 \
  --served-model-name qwen \
  --trust-remote-code \
  --gpu-memory-utilization 0.9
```

**方案 B:纯张量并行** (2 节点 × 8 NPU 示例)
```shell
vllm serve Qwen/Qwen3-235B-A22B \
  --distributed-executor-backend ray \
  --tensor-parallel-size 16 \
  --enable-expert-parallel \
  --seed 1024 \
  --max-model-len 8192 \
  --max-num-seqs 25 \
  --served-model-name qwen \
  --trust-remote-code \
  --gpu-memory-utilization 0.9
```

### 6. 测试推理
```bash
curl http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "qwen",
        "prompt": "tell me how to sleep well",
        "max_completion_tokens": 100,
        "temperature": 0
    }'
```
