# Qwen3.8-2.4T-A95B

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3.8-2.4T-A95B.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3.8-2.4T-A95B.md

# Qwen3.8-2.4T-A95B 文档深度解读

## 【定位】

这篇文档是 vLLM-Ascend **0.23.0** 中针对 Qwen3.8-2.4T-A95B（2400B 总参 / 95B 激活的 MoE 大模型）在 Atlas A3 / Atlas A2 集群上的端到端验证与部署指南,涵盖权重选型、多节点安装、DP/TP/EP 拓扑部署、功能验证、精度与性能评测、性能调优及 FAQ,并明确指出该模型在该版本中**首发支持**。

---

## 【技术要点】

1. **模型基本属性**(原文):2400B 总参数 / 95B 激活参数的 MoE 模型,基于 Qwen3.5 架构,改进 coding、专业工作、科研、长链路 agent 任务;首发版本为 vLLM-Ascend **0.23.0**。
2. **三种权重格式**(原文):
   - `Qwen3.8-2.4T-A95B` (FP16/BF16):约 **4.89 TB** 存储与权重内存;
   - `Qwen3.8-2.4T-A95B-w8a8`:约 **2.33 TiB**;
   - `Qwen3.8-2.4T-A95B-w4a8`:约 **1.21 TiB**。
3. **两套验证部署拓扑**(原文):
   - A3:`4 × Atlas 800 A3 (64GB × 16)` + W8A8 + Mixed Prefill/Decode,**DP4/TP16/EP64**;
   - A2:`8 × Atlas 800 A2 (64GB × 8)` + W4A8 + Mixed Prefill/Decode,**DP8/TP8/EP64**。
4. **多节点并行策略**(原文):每个节点上运行 1 个 DP rank,节点内 Tensor Parallel,**跨节点 Expert Parallel**(EP64)。
5. **W8A8 加载策略**(原文):使用 **lazy Safetensors** 策略,避免从共享存储预取完整 checkpoint。
6. **vllm serve 关键启动参数**(原文 Node 0):
   - `--quantization ascend`、`--safetensors-load-strategy lazy`
   - `--tensor-parallel-size $TP_SIZE`、`--data-parallel-size $DP_SIZE`、`--data-parallel-size-local 1`、`--data-parallel-address $LOCAL_IP`、`--data-parallel-rpc-port $RPC_PORT`
   - `--enable-prefix-caching`、`--enable-expert-parallel`
   - `--max-model-len 131072`、`--max-num-seqs 8`、`--max-num-batched-tokens 16384`、`--gpu-memory-utilization 0.85`
   - `--speculative-config '{"method":"qwen3_5_mtp","num_speculative_tokens":1}'`(MTP 投机 1 token)
   - `--compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}'`
   - `--additional-config '{"enable_cpu_binding":true,"enable_fused_mc2":1}'`
7. **关键环境变量**(原文):`VLLM_EXECUTE_MODEL_TIMEOUT_SECONDS=3000`、`HCCL_BUFFSIZE=1024`、`HCCL_BUFFSIZE_EP=2048`、`HCCL_INTRA_ROCE_ENABLE=0`、`HCCL_OP_EXPANSION_MODE="AIV"`、`HCCL_IF_IP=$LOCAL_IP`、`HCCL_SOCKET_IFNAME=$NIC_NAME`、`GLOO_SOCKET_IFNAME=$NIC_NAME`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`、`OPENBLAS_NUM_THREADS=1`、`ASCEND_RT_VISIBLE_DEVICES=0..15`。
8. **Docker 镜像**(原文):A3 用 `quay.io/ascend/vllm-ascend:qwen3.8-a3`;A2 用 `quay.io/ascend/vllm-ascend:v0.23.0`,均通过 `--device /dev/davinci*` + `--device /dev/davinci_manager` + `--device /dev/devmm_svm` + `--device /dev/hisi_hdc` 暴露 NPU 设备,并 `-v /root/.cache:/root/.cache` 挂载共享权重目录。

> 注:原文在 Nodes 1-3 启动命令处**被截断**(仅显示到 `export TOKE`),因此 worker 节点的完整命令与 DP_START_RANK 的具体设置**未在原文给出**,下文不做臆造。

---

## 【关键机制与数据】

- **数据流/工作原理(原文)**:
  - 权重以共享目录(推荐 `/root/.cache/`)方式被所有 serving 节点挂载,**checkpoint 与 tokenizer 目录必须在所有节点同路径**。
  - W8A8 部署通过 `lazy` safetensors 策略按需从共享存储读取权重,**避免一次性预取完整 2.33 TiB checkpoint** 造成存储压力。
  - 跨节点通信依赖 HCCL,关键开关包括 `HCCL_IF_IP`、`HCCL_SOCKET_IFNAME`(必须为 `LOCAL_IP` 所属的 `NIC_NAME`)、`HCCL_INTRA_ROCE_ENABLE=0`(关掉节点内 RoCE)、`HCCL_OP_EXPANSION_MODE="AIV"`(使用 AIV 算子扩展)。
  - 节点启动顺序:**Node 0 必须先启动**,所有 worker 的 `NODE0_IP` 必须等于 Node 0 的 `LOCAL_IP`,每个 worker 需分配唯一 `DP_START_RANK`。
  - 计算/通信融合:`enable_fused_mc2:1` 启用 MC2(Matmul + Communication)融合算子,以匹配昇腾 Atlas A3/A2 上的大规模 all-reduce 通信。
  - 投机解码:使用 Qwen3.5 风格的 MTP(`qwen3_5_mtp`),每个 step 投机 1 个 token。
  - CUDA Graph 仅在 Decode 阶段生效(`cudagraph_mode: FULL_DECODE_ONLY`),针对 Decode 阶段 batch 小、形状相对稳定的特性。

- **性能数据**:**原文未涉及**(没有任何吞吐量、时延、tokens/s、显存占用等具体数值)。

---

## 【表格解读】

原文表格 1 个(已逐字还原):

| Platform | Weight | Deployment | Topology |
| --- | --- | --- | --- |
| 4 × Atlas 800 A3 (64GB × 16) | W8A8 | Mixed Prefill/Decode deployment | DP4/TP16/EP64 |
| 8 × Atlas 800 A2 (64GB × 8) | W4A8 | Mixed Prefill/Decode deployment | DP8/TP8/EP64 |

逐行解读:

- **第 1 行(A3 W8A8)**:4 台 Atlas 800 A3 服务器(每台 16 张 64GB NPU,共 64 张卡),使用 W8A8 量化权重,采用 Prefill+Decode 同部署(Mixed)模式,4 个 DP rank(每节点 1 个 DP)各起 TP16,EP 跨节点=64(等于全网专家并行度)。W8A8 量化使得单卡 ~2.33TiB 总量能够装下。
- **第 2 行(A2 W4A8)**:8 台 Atlas 800 A2 服务器(每台 8 张 64GB NPU,共 64 张卡),使用 W4A8 更激进的量化(1.21TiB 总量),同样 Mixed Prefill/Decode,8 个 DP rank(每节点 1 个 DP)各起 TP8,EP 跨节点=64。
- **拓扑对比**:两套拓扑都满足 **DP × TP × 总卡数 = 1 × 16 × 4 = 64** 与 **1 × 8 × 8 = 64**;同时 EP64 = 总卡数,意味着 expert 并行打满全网,适合 2400B 级 MoE 的专家路由分布。
- **量化选择逻辑**:A3 单卡显存充裕(64GB × 16 = 1024 GB/节点)故用 W8A8 保精度;A2 单卡显存有限但卡数更多,故用 W4A8 进一步压低权重内存。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

文档与以下文档/模块存在链接关系(均为原文出现或经由章节交叉引用得出):

- **支持矩阵层**:`../../user_guide/support_matrix/supported_models.md`(Supported Models 矩阵——用于确认 Qwen3.8-2.4T-A95B 的官方支持状态);`../../user_guide/support_matrix/feature_matrix.md`(Feature Matrix——查看前缀缓存、Expert Parallel、投机解码等功能的支持矩阵)。
- **特性指南层**:`../../user_guide/feature_guide/index.md`(Feature Guide 索引——指向每个特性的详细配置页,本篇中的 `enable-prefix-caching`、`enable-expert-parallel`、`quantization ascend`、`speculative-config` 等参数都来自该层)。
- **安装指南层**:`../../getting_started/installation.md#installation-multi-node-interconnect`(多节点互联验证,HCCL 网络前置条件);`../../getting_started/installation.md#installation-prebuilt-image`(预构建镜像,本篇 A3/A2 docker run 即由此页派生);`../../getting_started/installation.md#installation-existing-cann-install`(在已有 CANN 的环境从源码安装 vllm-ascend,用于 4.2 章节)。
- **评估模块**:`../../developer_guide/evaluation/using_ais_bench.md`(使用 AIS-Bench 做功能/精度评测;同链接在原文中重复出现两次,以及 `using_ais_bench.md#execute-performance-evaluation` 锚点指向"执行性能评测"小节——本篇第 5 节之后的精度与性能评估步骤即引用此页)。
- **性能调优模块**:`../../developer_guide/performance_and_debug/optimization_and_tuning.md`(对应文档中"性能调优"章节,补充 `HCCL_BUFFSIZE`、fused_mc2、`PYTORCH_NPU_ALLOC_CONF` 等参数的调优说明)。

上下游关系:**Prerequisites → Installation → Multi-Node Deployment → Functional Verification → Accuracy/Performance Evaluation → Performance Tuning → FAQ**;其中性能调优章节与 optimization_and_tuning.md 双向对照,评估章节与 using_ais_bench.md 双向对照。

---

## 【使用方法】

### 启用方式(原文给出)

1. **Docker 安装(A3 系列)**:
   - 镜像:`quay.io/ascend/vllm-ascend:qwen3.8-a3`
   - 在**每个节点**执行 `docker run --rm --name vllm-ascend --net=host --shm-size=1g --device /dev/davinci0 ... --device /dev/davinci15 --device /dev/davinci_manager --device /dev/devmm_svm --device /dev/hisi_hdc -v /usr/local/dcmi:/usr/local/dcmi -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info -v /etc/ascend_install.info:/etc/ascend_install.info -v /root/.cache:/root/.cache -it $IMAGE bash`
   - 进入容器后:`python -c "import vllm, vllm_ascend; print('vllm and vllm_ascend are ready')"`。

2. **Docker 安装(A2 系列)**:
   - 镜像:`quay.io/ascend/vllm-ascend:v0.23.0`
   - `docker run` 命令同上,仅 `--device /dev/davinci*` 暴露 `0..7`(8 张卡),无需 8~15 号设备,其余挂载参数一致。

3. **源码安装(可选)**:参见 `../../getting_started/installation.md#installation-existing-cann-install`;多节点时所有节点需安装**相同版本**的 vLLM 与 vLLM-Ascend。

### 配置项 / 启动命令(原文 Node 0 部分)

需先设置的环境变量(以 A3 系列 Node 0 为例):

```shell
export MODEL_PATH=<QWEN3_8_MODEL_PATH>
export TOKENIZER_PATH=<QWEN3_8_TOKENIZER_PATH>
export LOCAL_IP=<NODE0_LOCAL_IP>
export NIC_NAME=<NODE0_NIC_NAME>
export PORT=<SERVICE_PORT>
export RPC_PORT=<DP_RPC_PORT>
export DP_SIZE=4
export TP_SIZE=16

export VLLM_EXECUTE_MODEL_TIMEOUT_SECONDS=3000
export HCCL_BUFFSIZE=1024
export HCCL_BUFFSIZE_EP=2048
export HCCL_IF_IP=$LOCAL_IP
export HCCL_INTRA_ROCE_ENABLE=0
export HCCL_OP_EXPANSION_MODE="AIV"
export HCCL_SOCKET_IFNAME=$NIC_NAME
export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
export GLOO_SOCKET_IFNAME=$NIC_NAME
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export OPENBLAS_NUM_THREADS=1
```

启动服务命令:

```shell
vllm serve $MODEL_PATH \
    --host 0.0.0.0 \
    --port $PORT \
    --served-model-name qwen3.8 \
    --tokenizer $TOKENIZER_PATH \
    --trust-remote-code \
    --quantization ascend \
    --safetensors-load-strategy lazy \
    --tensor-parallel-size $TP_SIZE \
    --data-parallel-size $DP_SIZE \
    --data-parallel-size-local 1 \
    --data-parallel-address $LOCAL_IP \
    --data-parallel-rpc-port $RPC_PORT \
    --enable-prefix-caching \
    --enable-expert-parallel \
    --max-model-len 131072 \
    --max-num-seqs 8 \
    --max-num-batched-tokens 16384 \
    --gpu-memory-utilization 0.85 \
    --speculative-config '{"method":"qwen3_5_mtp","num_speculative_tokens":1}' \
    --compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}' \
    --additional-config '{"enable_cpu_binding":true,"enable_fused_mc2":1}'
```

### 其他原文未涉及的内容

- **功能验证、精度/性能评估的具体命令**:**原文未涉及**(章节大纲提及,正文被截断)。
- **性能调优的具体手段**:**原文未涉及**(仅引用 `optimization_and_tuning.md` 链接)。
- **FAQ**:**原文未涉及**(大纲提及,正文被截断)。
- **Nodes 1-3 的完整 worker 启动命令**:**原文未涉及**(在 `export TOKE` 处截断,未给出 `DP_START_RANK`、`DP_RANK_LOCAL`、`HCCL_IF_IP` 等参数在 worker 上的具体用法)。
