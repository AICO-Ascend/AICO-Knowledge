# DeepSeek-V3.2

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/DeepSeek-V3.2.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/DeepSeek-V3.2.md

# DeepSeek-V3.2 部署文档深度解读

## 【定位】

本文档解决的是 **DeepSeek-V3.2（一种带稀疏注意力机制的大模型）在 vllm-ascend 上的端到端部署与验证问题**，给出了从支持的特性矩阵、模型权重准备、单机/多节点在线服务部署、到 PD 分离与评测的完整操作指引。

## 【技术要点】

1. **稀疏注意力（Sparse Attention）架构**：DeepSeek-V3.2 主体结构与 DeepSeek-V3.1 类似，但新增了**稀疏注意力机制**，目标是针对长上下文场景优化训练与推理效率（原文："a sparse attention model … designed to explore and validate optimizations for training and inference efficiency in long-context scenarios"）。
2. **量化版本与硬件要求**：提供两种 W8A8 量化权重：
   - `DeepSeek-V3.2-Exp-W8A8` 与 `DeepSeek-V3.2-w8a8`
   - 硬件需求：**1 节点 Atlas 800 A3（64GB × 16）** 或 **2 节点 Atlas 800 A2（64GB × 8）**
   - 推荐将权重下载到多节点共享目录 `/root/.cache/`
3. **Docker 镜像两套**：
   - A3：`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3`，需挂载 16 个 `/dev/davinci*` 设备
   - A2：`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`，需挂载 8 个 `/dev/davinci*` 设备
   - 两者均挂载 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`，并 `-v /root/.cache:/root/.cache` 共享权重
4. **单机在线推理关键参数**（A3 单节点，量化模型）：
   - `--tensor-parallel-size 8` `--data-parallel-size 2`（共 16 卡 = 8 卡 TP × 2 副本 DP）
   - `--quantization ascend` `--enable-expert-parallel`
   - `--max-num-seqs 16` `--max-model-len 8192` `--max-num-batched-tokens 4096`
   - `--gpu-memory-utilization 0.92` `--no-enable-prefix-caching`
   - `--additional-config '{"enable_mlapo":true}'`
   - `--compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}'`
   - `--speculative-config '{"num_speculative_tokens": 3, "method": "deepseek_mtp"}'`（MTP 投机解码，3 个 draft token）
   - 端口 `--port 8000`，服务名 `--served-model-name deepseek_v3_2`
5. **多节点在线推理（A3 双节点，TP=16、DP=2 各节点 1 副本）**：
   - 通信：两节点均设置 `HCCL_IF_IP=$local_ip`、`GLOO_SOCKET_IFNAME=$nic_name`、`TP_SOCKET_IFNAME=$nic_name`、`HCCL_SOCKET_IFNAME=$nic_name`
   - Node0 作为 master：`--data-parallel-size 2 --data-parallel-size-local 1 --data-parallel-address $node0_ip --data-parallel-rpc-port 12890`
   - Node1 作为从属：额外加 `--headless` 与 `--data-parallel-start-rank 1`，端口 `--port 8077`
   - 其余推理参数与单机一致
6. **关键环境变量集合**（单/多节点通用）：
   - `HCCL_OP_EXPANSION_MODE="AIV"`（HCCL 算子展开模式 AIV）
   - `OMP_PROC_BIND=false`、`OMP_NUM_THREADS=10`
   - `VLLM_USE_V1=1`
   - `HCCL_BUFFSIZE=200`
   - `PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`（NPU 内存分配采用可扩展段）

## 【关键机制与数据】

- **稀疏注意力**：原文表明 V3.2 = V3.1 架构 + 稀疏注意力，目标是长上下文场景的训练/推理效率优化。
- **W8A8 量化**：权重与激活均 8-bit 量化，使用 `--quantization ascend` 调用 Ascend 量化后端。
- **MLA + PO（enable_mlapo）**：`--additional-config '{"enable_mlapo":true}'` 启用 MLA-PO 优化路径（Multi-head Latent Attention – 一种降低 KV cache 显存占用的 MLA 变体）。
- **专家并行（Expert Parallelism）**：`--enable-expert-parallel` 配合 MoE 架构使用。
- **投机解码（MTP）**：`method: "deepseek_mtp"` + `num_speculative_tokens: 3`，每轮草拟 3 个 token，可显著降低 decode 时延。
- **CUDA Graph 解码优化**：`cudagraph_mode: "FULL_DECODE_ONLY"` 表示仅在纯 decode 阶段捕获 CUDA Graph，prefill 不捕获。
- **多节点并行拓扑**：A3 双节点 = TP=16（跨节点张量并行）× DP=2（每节点各 1 个 DP 副本），共 32 卡规模。
- **数据流与角色分工**（原文）：
  - Node0：master/rank 0，负责 `--data-parallel-address` 与 `--data-parallel-rpc-port 12890` 的协调
  - Node1：通过 `--headless` + `--data-parallel-start-rank 1` 加入同一 data-parallel 域
  - 两者共享 `--tensor-parallel-size 16` 形成跨节点 TP 环
- **性能数据**：原文未给出具体吞吐量/时延数字（性能测试入口见文档第 7 节链接 `using_ais_bench.md#execute-performance-evaluation` 与 `using_lm_eval.md`）。

## 【表格解读】

**原文无表格。** 全文以命令/脚本块（`=== "A3 series"` / `=== "A2 series"`）以及参数列表形式组织，未出现任何 markdown 表格。

## 【公式解读】

**原文无公式。** 文档仅含 shell 命令、JSON 配置片段与步骤文字，未涉及 LaTeX 公式或伪代码公式。

## 【关联】

依据文末及正文链接，文档与其他模块/特性存在如下关联：

- **支持矩阵** → [`../../user_guide/support_matrix/supported_models.md`](../../user_guide/support_matrix/supported_models.md)：用于查询 DeepSeek-V3.2 在 vllm-ascend 上的完整支持特性矩阵。
- **特性配置** → [`../../user_guide/feature_guide/index.md`](../../user_guide/feature_guide/index.md)：解释所使用特性（如 MTP、Expert Parallel、CUDA Graph）的具体配置方法。
- **多节点互联安装** → [`../../getting_started/installation.md#installation-multi-node-interconnect`](../../getting_started/installation.md#installation-multi-node-interconnect)：第 3.2 节引用，用于在多节点部署前验证 HCCL 网络互通。
- **源码安装** → [`../../getting_started/installation.md`](../../getting_started/installation.md)：第 4.2 节引用，对应非 Docker 方式从源码安装 vllm-ascend。
- **PD 分离（Mooncake 多节点）** → [`../features/pd_disaggregation_mooncake_multi_node.md`](../features/pd_disaggregation_mooncake_multi_node.md)：第 6 节关联内容，演示将 DeepSeek-V3.2 部署为 Prefill/Decode 分离形态。
- **FAQ** → [`../../faqs.md`](../../faqs.md)：与 DeepSeek-V3.2 部署/运行相关的常见问题与排错。
- **性能评测（ais_bench）** → [`../../developer_guide/evaluation/using_ais_bench.md`](../../developer_guide/evaluation/using_ais_bench.md) 以及其中 [`#execute-performance-evaluation`](../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation) 锚点：第 7 节性能评测入口。
- **精度评测（lm_eval）** → [`../../developer_guide/evaluation/using_lm_eval.md`](../../developer_guide/evaluation/using_lm_eval.md)：第 7 节精度评测入口。

## 【使用方法】

### 启用方式（按部署形态分类）

**(a) Docker 方式（推荐）**

- 拉取并启动 A3 或 A2 镜像，按第 4.1 节 `docker run` 命令在每个节点启动容器；A3 暴露 16 个 davinci 设备，A2 暴露 8 个 davinci 设备，并挂载驱动与 `/root/.cache`。
- 镜像名通过环境变量 `IMAGE` 注入，版本占位符为 `{{ vllm_ascend_version }}`。

**(b) 源码方式**

- 按 [`../../getting_started/installation.md`](../../getting_started/installation.md) 从源码编译 `vllm-ascend`；多节点场景需在**每个节点**分别完成源码部署。

### 单机在线服务启动命令

```shell
export HCCL_OP_EXPANSION_MODE="AIV"
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=10
export VLLM_USE_V1=1
export HCCL_BUFFSIZE=200
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True

vllm serve /root/.cache/modelscope/hub/models/vllm-ascend/DeepSeek-V3.2-W8A8 \
  --additional-config '{"enable_mlapo":true}' \
  --host 0.0.0.0 --port 8000 \
  --data-parallel-size 2 --tensor-parallel-size 8 \
  --quantization ascend --seed 1024 \
  --served-model-name deepseek_v3_2 \
  --enable-expert-parallel \
  --max-num-seqs 16 --max-model-len 8192 --max-num-batched-tokens 4096 \
  --trust-remote-code --no-enable-prefix-caching \
  --gpu-memory-utilization 0.92 \
  --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
  --speculative-config '{"num_speculative_tokens": 3, "method": "deepseek_mtp"}'
```

### 多节点在线服务启动（A3 双节点示例，节选）

- **Node0（master）**：`--tensor-parallel-size 16 --data-parallel-size 2 --data-parallel-size-local 1 --data-parallel-address $node0_ip --data-parallel-rpc-port 12890`，端口 8077。
- **Node1**：`--headless --data-parallel-start-rank 1`，其他并行与推理参数与 Node0 完全一致；通过 `HCCL_IF_IP` / `HCCL_SOCKET_IFNAME` / `TP_SOCKET_IFNAME` / `GLOO_SOCKET_IFNAME` 绑定本节点网卡。
- 注：原文 Node1 的 A3 命令块在 `speculative-config` 行被截断，实际使用时应保持 `num_speculative_tokens=3, method=deepseek_mtp` 与 Node0 一致。

### 主要配置项说明（按参数归类，原文有则写）

| 类别 | 参数 / 环境变量 | 作用 | 原文值 |
|---|---|---|---|
| 并行策略 | `--tensor-parallel-size` | 张量并行度 | 单机 8；多节点 16 |
| 并行策略 | `--data-parallel-size` | 数据并行副本数 | 单机 2；多节点 2 |
| 并行策略 | `--data-parallel-size-local` | 每节点本地 DP 副本数 | 多节点 1 |
| 并行策略 | `--data-parallel-start-rank` | 本节点起始 DP rank | Node1 为 1 |
| 并行策略 | `--enable-expert-parallel` | 启用专家并行（MoE） | true |
| 量化 | `--quantization ascend` | 调用 Ascend 量化后端（W8A8） | ascend |
| 投机解码 | `--speculative-config` | MTP 草拟 token 数与方法 | `num_speculative_tokens=3, method=deepseek_mtp` |
| MLA-PO | `--additional-config '{"enable_mlapo":true}'` | 启用 MLA-PO 优化 | true |
| 编译 | `--compilation-config` | CUDA Graph 模式 | `cudagraph_mode: "FULL_DECODE_ONLY"` |
| 容量 | `--max-num-seqs` | 最大并发序列数 | 16 |
| 容量 | `--max-model-len` | 最大上下文长度 | 8192 |
| 容量 | `--max-num-batched-tokens` | 单批最大 token 数 | 4096 |
| 容量 | `--gpu-memory-utilization` | NPU 显存利用率上限 | 0.92 |
| 缓存 | `--no-enable-prefix-caching` | 关闭前缀 KV 缓存 | true |
| HCCL | `HCCL_OP_EXPANSION_MODE` | HCCL 算子展开模式 | `AIV` |
| HCCL | `HCCL_BUFFSIZE` | HCCL 通信缓冲（MB） | 200 |
| HCCL | `HCCL_IF_IP` / `HCCL_SOCKET_IFNAME` | 绑定的本节点网卡 IP 与接口名 | `$local_ip` / `$nic_name` |
| 调度 | `OMP_PROC_BIND` / `OMP_NUM_THREADS` | CPU/OpenMP 绑定 | false / 10 |
| 运行时 | `VLLM_USE_V1` | 强制使用 vLLM V1 引擎 | 1 |
| 内存 | `PYTORCH_NPU_ALLOC_CONF` | NPU 显存分配策略 | `expandable_segments:True` |
| 命名 | `--served-model-name` | 对外暴露的模型名 | `deepseek_v3_2` |
| 安全 | `--trust-remote-code` | 信任远端自定义代码 | true |

### 后续步骤（文档链接中提及，命令原文未完全给出）

- **PD 分离部署**：参见 [`../features/pd_disaggregation_mooncake_multi_node.md`](../features/pd_disaggregation_mooncake_multi_node.md)。
- **性能评测**：使用 ais_bench，按 [`using_ais_bench.md#execute-performance-evaluation`](../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation) 执行。
- **精度评测**：使用 lm_eval，按 [`using_lm_eval.md`](../../developer_guide/evaluation/using_lm_eval.md) 执行。
- **FAQ**：部署/运行问题排查见 [`../../faqs.md`](../../faqs.md)。
