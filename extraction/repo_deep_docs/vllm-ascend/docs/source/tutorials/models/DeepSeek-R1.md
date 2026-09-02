# DeepSeek-R1

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/DeepSeek-R1.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/DeepSeek-R1.md

# DeepSeek-R1 部署文档深度解读

---

## 【定位】

这篇文档解决 **如何在 vLLM-Ascend 平台上部署 DeepSeek-R1（特别是 INT8 全量化版本 DeepSeek-R1-W8A8）的完整工程化问题**，涵盖支持的特性矩阵、环境准备、单节点/多节点部署、推理服务启动与服务验证等端到端流程。

---

## 【技术要点】

1. **模型与量化形态**
   - 基础模型：DeepSeek-R1，是 DeepSeek 公司开发的 MoE（Mixture-of-Experts）架构 LLM，擅长复杂逻辑推理、数学问题求解与代码生成。
   - 量化版本：`DeepSeek-R1-W8A8` —— 对权重（weights）和激活值（activations）均采用 **8-bit 整数（INT8）量化**，降低显存占用与算力需求。
   - 文档基于 **vLLM-Ascend v0.13.0** 验证编写，DeepSeek-R1 在该版本首次得到支持。

2. **硬件与拓扑要求**
   - 单节点即可运行：`1 × Atlas 800 A3 (64GB × 16)`，或 `2 × Atlas 800 A2 (64GB × 8)`。
   - 推荐数据并行/张量并行拓扑：**dp4tp4**（而非 `dp2tp8`）。
   - 模型权重下载至多节点共享目录（推荐 ModelScope：`vllm-ascend/DeepSeek-R1-W8A8`）。

3. **核心运行时参数（原文 vllm serve 命令中）**
   - `--data-parallel-size 4`
   - `--tensor-parallel-size 4`
   - `--quantization ascend`
   - `--enable-expert-parallel`
   - `--max-num-seqs 16`
   - `--max-model-len 16384`（性能测试）/ 精度测试建议 **≥35000**
   - `--max-num-batched-tokens 4096`
   - `--gpu-memory-utilization 0.92`
   - `--seed 1024`
   - `--served-model-name deepseek_r1`
   - `--trust-remote-code`

4. **关键调度/编译/推测解码开关**
   - `additional_config.scheduler_config.enable_balance_scheduling=true` —— 开启均衡调度。
   - `--speculative-config '{"num_speculative_tokens":3,"method":"mtp"}'` —— 启用 MTP（Multi-Token Prediction）推测解码，3 个推测 token。
   - `--compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}'` —— 仅 Decode 阶段启用 CUDA Graph。

5. **集合通信环境变量（原文脚本）**
   - `HCCL_OP_EXPANSION_MODE="AIV"` —— 使用 AIV 通信模式。
   - `HCCL_IF_IP`、`GLOO_SOCKET_IFNAME`、`TP_SOCKET_IFNAME`、`HCCL_SOCKET_IFNAME` 指向本节点 `local_ip` 对应的 `nic_name`。
   - `PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`。

6. **安装路径**
   - 方式 A：官方 Docker 镜像（`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3` 用于 A3 系列；同仓库镜像用于 A2 系列）。
   - 方式 B：从源码构建 `vllm-ascend`（多节点需在每个节点上分别搭建环境）。

---

## 【关键机制与数据】

> 原文未提供具体的吞吐量/延迟/Tokens/s 等性能数值。原文仅给出与启动配置相关的"机制性描述"，可整理如下：

- **均衡调度（Balance Scheduling）**—— 原文："Setting `additional_config.scheduler_config.enable_balance_scheduling=true` enables balance scheduling. This may help increase output throughput and reduce TPOT in v1 scheduler. However, TTFT may degrade in some scenarios. Furthermore, enabling this feature is not recommended in scenarios where PD is separated."
  - 作用：提升出参吞吐、降低 TPOT（每 token 时间）。
  - 副作用：可能使 TTFT（首个 token 时间）在某些场景退化。
  - 限制：PD（Prefill-Decode）分离场景不建议启用。

- **MTP 推测解码**—— 原文通过 `--speculative-config '{"num_speculative_tokens":3,"method":"mtp"}'` 启用，每次推测 3 个 token。
- **CUDA Graph 范围**—— 原文：`'{"cudagraph_mode": "FULL_DECODE_ONLY"}'`，仅在 Decode 阶段捕获/复用图，降低 Prefill 阶段的编译开销。
- **AIV 通信模式**—— 原文：`export HCCL_OP_EXPANSION_MODE="AIV"`，在 HCCL 集合通信中使用 AIV（Ascend Inter-V）通道。
- **上下文长度选择**—— 原文："For performance testing with an input length of 3.5k and output length of 1.5k, a value of `16384` is sufficient, however, for precision testing, please set it to at least `35000`." 即输入 3.5k + 输出 1.5k 的性能测试场景下 `max-model-len=16384` 已足够，精度测试至少 35000。
- **w4a8 权重的额外提示**—— 原文："If you use the w4a8 weight, more memory will be allocated to kvcache, and you can try to increase system throughput to achieve greater throughput." 使用 w4a8 权重时，KV Cache 获得更多显存，可通过提高系统吞吐换取更大吞吐。
- **前缀缓存**—— 原文：未显式出现 `--no-enable-prefix-caching` 字段，但参数说明中提到"`--no-enable-prefix-caching` indicates that prefix caching is disabled. To enable it, remove this option."，暗示默认开启、需主动关闭。

> 性能数字、benchmark 数据、tokens/s、TTFT/TPOT 实测值：**原文未涉及**。

---

## 【表格解读】

**原文无表格。** 文档以 shell 命令块、参数说明列表形式承载配置，未出现 markdown 表格结构（如 `|...|...|`）。若将"Key Parameter Descriptions"部分视为参数对照表，其字段为 *参数名 / 取值 / 作用说明*，但原文采用项目符号列表呈现，非表格语法，故按规则不强行转写。

---

## 【公式解读】

**原文无公式。** 文档不包含任何 LaTeX 数学公式或伪代码形式的算式表达。

---

## 【关联】

文档通过以下内部链接与仓库其他模块形成上下游关系：

| 文档内提及的链接 | 关系性质 |
|---|---|
| `../../user_guide/support_matrix/supported_models.md` | 上游参考：DeepSeek-R1 在 vLLM-Ascend 上的"支持特性矩阵"（Supported Features List）。 |
| `../../user_guide/feature_guide/index.md` | 上游参考：各项 feature 的详细配置说明（Feature Guide）。 |
| `../../getting_started/installation.md#installation-multi-node-interconnect` | 依赖前置：多节点部署前的多节点通信验证步骤（§3.2）。 |
| `../../getting_started/installation.md#installation-prebuilt-image` | 依赖前置：Docker 镜像拉取与启动方法（§4.1）。 |
| `../../getting_started/installation.md` | 依赖前置：源码安装 `vllm-ascend` 的总入口（§4.2）。 |
| `../../faqs.md` | 故障排查出口：单/多节点启动命令末尾均指向 Public FAQs。 |
| `./DeepSeek-V3.1.md` | 同系列姊妹文档：DeepSeek-V3.1 的部署指南。 |
| `../../developer_guide/evaluation/using_ais_bench.md` | 配套下游：使用 AIS-Bench 进行精度/性能评估。 |
| `../../developer_guide/evaluation/using_lm_eval.md` | 配套下游：使用 lm-eval 进行精度/性能评估。 |

由此看出本教程在仓库中的角色：**是 DeepSeek-R1 系列模型部署的"主线文档"**，向下挂接评估工具（ais_bench / lm_eval），向上引用支持矩阵与 feature guide，并与姊妹模型 DeepSeek-V3.1 文档并列。

---

## 【使用方法】

### 1. 模型权重获取
原文：下载 `DeepSeek-R1-W8A8` 至多节点共享目录。
```
https://www.modelscope.cn/models/vllm-ascend/DeepSeek-R1-W8A8
```

### 2. 安装方式

**(a) Docker 镜像方式**（原文 §4.1）

A3 系列启动脚本（关键片段，**逐字保留**）：
```shell
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3
docker run --rm \
    --name vllm-ascend \
    --shm-size=1g \
    --net=host \
    --privileged=true \
    --device /dev/davinci0 ... --device /dev/davinci15 \
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

A2 系列使用 `export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`（无 `-a3` 后缀），并暴露 `davinci0`～`davinci7` 共 8 个 device。

**(b) 源码方式**（原文 §4.2）—— 参考 `../../getting_started/installation.md`。

### 3. 单节点 Online Deployment（原文 §5.1）
**关键启动命令（已逐字保留主要参数）：**
```shell
vllm serve vllm-ascend/DeepSeek-R1-W8A8 \
  --additional-config '{"scheduler_config":{"enable_balance_scheduling":true}}' \
  --host 0.0.0.0 --port 8000 \
  --data-parallel-size 4 --tensor-parallel-size 4 \
  --quantization ascend --seed 1024 \
  --served-model-name deepseek_r1 \
  --enable-expert-parallel \
  --max-num-seqs 16 --max-model-len 16384 --max-num-batched-tokens 4096 \
  --trust-remote-code --gpu-memory-utilization 0.92 \
  --speculative-config '{"num_speculative_tokens":3,"method":"mtp"}' \
  --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}'
```
（前置环境变量：`HCCL_OP_EXPANSION_MODE="AIV"`、`HCCL_IF_IP=$local_ip`、`GLOO_SOCKET_IFNAME=$nic_name`、`TP_SOCKET_IFNAME=$nic_name`、`HCCL_SOCKET_IFNAME=$nic_name`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`。）

### 4. 服务验证（原文 §5.1 末尾）
原文使用 `curl` 调用 `http://<node_ip>:8000/v1/chat/completions`，输入 `messages` 角色为 user、内容为 `"The future of AI is"`，期望返回 HTTP 200 且 JSON 中含 `choices` 字段。原文给出一个示例响应片段：`"id": "chatcmpl-xxxxxxxxxxxxx"`，`usage.prompt_tokens=8, completion_tokens=1024, total_tokens=1032`，`finish_reason="length"`。

### 5. 多节点 Data Parallel 部署（原文 §5.2）
**原文该节在用户提供的快照中于 "Node 0" 标题后被截断**，后续命令未完整给出；按上下文推断需在两个节点上分别运行类似脚本，并通过多节点通信前置（§3.2 链接）保证 HCCL/GLOO 互通。**该部分具体命令原文未完整展示。**

### 6. 精度/性能评估（原文文档目的之一）
未在本片段给出具体命令，需跳转至：
- `../../developer_guide/evaluation/using_ais_bench.md`
- `../../developer_guide/evaluation/using_lm_eval.md`

> **故障排查入口**：启动命令末尾的 `Common Issues Tip` 指引至 `../../faqs.md`。
