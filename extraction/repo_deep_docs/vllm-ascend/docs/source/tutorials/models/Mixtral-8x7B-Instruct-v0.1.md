# Mixtral-8x7B-Instruct-v0.1

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Mixtral-8x7B-Instruct-v0.1.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Mixtral-8x7B-Instruct-v0.1.md

# Mixtral-8x7B-Instruct-v0.1 部署指南 — 深度解读

---

## 【定位】

本文档解决"如何在昇腾 (Ascend) Atlas A2/A3 硬件上,通过 vllm-ascend 部署并验证 Mixtral-8x7B-Instruct-v0.1 这一稀疏激活 MoE 模型"的问题,涵盖模型权重准备、容器化环境搭建、单节点部署、在线推理调用、功能验证以及精度/性能评估的完整流程。

---

## 【技术要点】

1. **模型架构特征**:Mixtral-8x7B-Instruct-v0.1 由 Mistral AI 提出的 MoE (Mixture-of-Experts) 模型,具备 **8 个专家、每个 7B 参数**,但**每个 token 仅激活 2 个专家**(稀疏激活),并针对指令跟随任务做了微调。
2. **硬件要求**:单节点部署支持 **1 台 Atlas 800 A3(64GB × 16)** 或 **1 台 Atlas 800 A2(64GB × 8)**;tensor-parallel-size 设置为 **4**。
3. **环境变量配置**:部署前需设置 `HCCL_OP_EXPANSION_MODE="AIV"`、`OMP_PROC_BIND=false`、`OMP_NUM_THREADS=10`、`VLLM_USE_V1=1`、`HCCL_BUFFSIZE=200`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`。
4. **关键启动参数**:`--max-model-len 4096`(测试)/ `512`(benchmark)、`--dtype bfloat16`/`float16`、`--trust-remote-code`、`--enforce-eager`、`--block-size 128`、`--gpu-memory-utilization 0.7`,并通过 `--additional-config '{"enable_mlapo":true}'` 开启 MLAPO。
5. **容器与设备挂载**:通过 docker run 启动官方镜像,Atlas A2 挂载 `/dev/davinci[0-7]`、Atlas A3 挂载 `/dev/davinci[0-15]`,并挂载 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 等驱动设备,以及 dcmi/hccn_tool/npu-smi 等工具路径。
6. **可选平衡调度**:可设置 `additional_config.scheduler_config.enable_balance_scheduling=true` 提升吞吐与 TPOT,但可能在某些场景下劣化 TTFT。
7. **三种 Benchmark 子命令**:`vllm bench` 提供 `latency`(单批延迟)、`serve`(在线服务吞吐)、`throughput`(离线吞吐)三种模式;`serve` 示例使用 `--max-model-len 512`。

---

## 【关键机制与数据】

### 工作原理与数据流

- **模型加载**:从 HuggingFace 下载 BF16 版本权重至本地(如 `/data/models/` 或容器 `/root/.cache`),通过 vllm-ascend 镜像内置的 vLLM 引擎加载,模型标识符为 `mistralai/Mixtral-8x7B-Instruct-v0.1`。
- **推理入口**:启动 `vllm serve`(或 `python -m vllm.entrypoints.openai.api_server`)后,服务监听 `0.0.0.0:8000`,对外暴露 OpenAI 兼容的 `/v1/chat/completions` HTTP 接口。
- **稀疏激活路径**:原文强调"only 2 experts activated per token",这是 Mixtral 的核心稀疏性特征,降低了单 token 实际计算量,使得 8×7B 总参数模型可以在受限显存下运行(结合 TP=4 切分到 4 张 NPU)。
- **设备与驱动链路**:容器需挂载驱动层设备与工具(`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`、dcmi、hccn_tool、npu-smi),保证 CANN/HCCL 通信栈与 NPU 设备正常交互。
- **HCCL 通信调优**:`HCCL_OP_EXPANSION_MODE="AIV"` 走 HCCL 的 AIV(Ascend Inter-Vector)算子扩展模式;`HCCL_BUFFSIZE=200` 调整集合通信 buffer 容量。
- **内存管理**:`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True` 启用 NPU 上分段可扩展分配,降低碎片;`--gpu-memory-utilization 0.7` 限制模型占用显存/NPU 内存比例为 70%。
- **v1 调度器**:通过 `VLLM_USE_V1=1` 强制使用 v1 调度器,可配合 `enable_balance_scheduling` 实现专家负载均衡。

### 性能/精度数据

- 原文未给出具体吞吐量、TPS、TTFT、TPOT、tokens/s 或 accuracy 数值,仅在结论中表述"high throughput and low latency",并指出"performs well on various benchmarks including reasoning, comprehension, and instruction following tasks"(无具体分数)。原文:**未提供量化性能/精度数字**。

---

## 【表格解读】

**原文无表格**。

(注:原文中所有结构化信息均以代码块、有序/无序列表、Notice 解释段落形式呈现,未使用 markdown 表格。)

---

## 【公式解读】

**原文无公式**。

(注:文档中未出现 LaTeX 公式或伪代码公式,所有数值参数均以命令行 flag 或环境变量的形式给出。)

---

## 【关联】

- **运行环境入口**(`../../getting_started/installation.md#installation-prebuilt-image`):本文档的"Installation"小节明确引用此链接说明如何根据机型选择 docker 镜像并启动容器,属于本文档的前置依赖。
- **精度评估**(`../../developer_guide/evaluation/using_ais_bench.md`):"Accuracy Evaluation → Using AISBench"小节指向该文档描述 AISBench 的使用方式,用于评估 Mixtral-8x7B-Instruct-v0.1 在各类基准上的表现。
- **性能评估 — AISBench 部分**(`../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation`):"Performance Evaluation → Using AISBench"小节指向该锚点,说明 AISBench 性能评估执行流程。
- **vLLM Benchmark**(`https://docs.vllm.ai/en/latest/benchmarking/`):外部官方文档,提供 `latency`/`serve`/`throughput` 三个子命令的详细说明,本文档的 `serve` 示例直接引用其模式。
- **上游**:Mistral AI 官方模型卡(`https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1`)提供权重与原始模型定义。
- **下游**:OpenAI 兼容 HTTP 客户端(curl/vllm bench serve)调用 `/v1/chat/completions`,作为人机交互或自动化评估入口。

---

## 【使用方法】

### 1. 权重下载

- BF16 版本:从 `https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1` 下载到本地,建议路径 `/data/models/` 或容器内 `/root/.cache`。
- 也可使用第三方量化版本。

### 2. 启动 Docker 容器(原文命令,保留关键 flag)

```bash
export IMAGE=m.daocloud.io/quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}
export NAME=vllm-ascend

docker run --rm \
    --name $NAME \
    --net=host \
    --shm-size=1g \
    --device /dev/davinci0 --device /dev/davinci1 \
    --device /dev/davinci2 --device /dev/davinci3 \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v /root/.cache:/root/.cache \
    -it $IMAGE bash
```

- Atlas A2:将 `--device /dev/davinci[0-3]` 改为 `/dev/davinci[0-7]`。
- Atlas A3:改为 `/dev/davinci[0-15]`。

### 3. 设置环境变量(部署前)

```bash
export HCCL_OP_EXPANSION_MODE="AIV"
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=10
export VLLM_USE_V1=1
export HCCL_BUFFSIZE=200
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
```

### 4. 启动在线推理服务

```bash
vllm serve "mistralai/Mixtral-8x7B-Instruct-v0.1" \
  --additional-config '{"enable_mlapo":true}' \
  --tensor-parallel-size 4 \
  --max-model-len 4096 \
  --dtype bfloat16 \
  --trust-remote-code \
  --enforce-eager \
  --block-size 128 \
  --gpu-memory-utilization 0.7
```

### 5. 功能验证(curl 调用,三条样例)

- 自我介绍请求(`max_tokens=100, temperature=0.7`)
- 指令跟随请求(中文架构师角色扮演,同上参数)
- MoE 相关问答请求(同上参数)

均通过 `http://localhost:8000/v1/chat/completions` 发送 OpenAI 格式 JSON。

### 6. 精度评估

- 使用 AISBench,详见 `../../developer_guide/evaluation/using_ais_bench.md`。

### 7. 性能评估

- AISBench:详见 `../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation`。
- vLLM Benchmark:`vllm bench {latency|serve|throughput}`;`serve` 模式示例启动命令使用 `--max-model-len 512`(区别于部署时的 4096)、`--dtype float16`,其余与 vllm serve 相同。

> 原文未涉及:多节点分布式部署具体步骤(仅硬件规格提到支持机型)、量化版本具体型号与对比、官方推荐 batch size、典型 TTFT/TPOT 数值指标。
