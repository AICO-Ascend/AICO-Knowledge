# Kimi-K3

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Kimi-K3.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Kimi-K3.md

# Kimi-K3 部署指南深度解读

## 【定位】
本文是 vLLM-Ascend 在 Atlas A3 硬件上部署 Kimi-K3 多模态 MoE 模型（W4A8 量化检查点）的端到端教程，覆盖权重准备、多节点镜像安装、四节点在线服务启动以及（原文未完整给出）准确性与性能评估流程。

---

## 【技术要点】

1. **模型架构特征**：Kimi-K3 是多模态混合专家模型，原文列出其核心组件——Kimi Delta Attention (KDA)、gated Multi-head Latent Attention (MLA)、attention residuals、SiTU activations、latent MoE layers。
2. **量化与规模**：目标为 **W4A8 全量化检查点**，**93 层、896 专家**，权重存储约 **1.49 TB**，参数量与规模显著大于常规 7B–70B 级 MoE。
3. **并行拓扑**：**4 台 Atlas 800 A3 节点，每节点 16 个逻辑 NPU**，组成 **DP4 / TP16 / EP64** 混合并行；每节点对应 1 个全局 DP rank，TP 使用本地全部 16 个 NPU，EP 将专家分布在 64 维 EP 组中。
4. **执行图与缓存**：启用 `FULL_DECODE_ONLY` ACL Graph、`--enable-prefix-caching`、`--max-model-len 133120`、`--max-num-batched-tokens 8192`、`--max-num-seqs 16`、`--gpu-memory-utilization 0.85`。
5. **DSpark 投机解码**：可选三种 draft 检查点——GQA draft（`num_speculative_tokens=7`）、MLA draft（`num_speculative_tokens=7`）、MLA 五 token 块 draft（`num_speculative_tokens=5`）。
6. **多节点通信与启动**：先启 Node 0，Node 1–3 以 `--headless` 模式通过 `--data-parallel-address $NODE0_IP --data-parallel-rpc-port $RPC_PORT` 加入；环境变量控制 HCCL/通信接口与超时（`VLLM_ENGINE_READY_TIMEOUT_S=7200`、`VLLM_EXECUTE_MODEL_TIMEOUT_SECONDS=3000`）。

---

## 【关键机制与数据】

**工作原理 / 数据流**（基于原文可推导部分）：

- **节点角色与启动顺序**：原文："Start Node 0 first. Each worker owns one global DP rank and joins Node 0 through the DP RPC address." 即 Node 0 暴露 RPC（`$RPC_PORT=13345`），其余节点通过 `--data-parallel-rpc-port` 接入；worker 节点使用 `--headless` 不另起 HTTP。
- **并行组与显存预算**：原文："`--data-parallel-size 4` and `--data-parallel-size-local 1` create one DP rank per node. `--tensor-parallel-size 16` uses all 16 local logical NPUs; `--enable-expert-parallel` distributes experts across the 64-rank EP group." 即 4 节点 × 16 NPU = 64 维 EP，TP 在节点内 16 路切分。
- **推理配置语义**：原文："`--max-model-len` bounds input plus output tokens; `--max-num-batched-tokens` bounds tokens scheduled per iteration, and `--max-num-seqs` bounds concurrent sequences per engine." 上下文窗口上限 133120，单次迭代调度 token 数 8192，单引擎并发序列 16。
- **ACL Graph 模式**：原文 `--compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}'`，表明仅对 decode 阶段捕获计算图。
- **HCCL 与内存分配**：`HCCL_BUFFSIZE=1024`、`HCCL_BUFFSIZE_EP=2048`、`HCCL_INTRA_PCIE_ENABLE=1`、`HCCL_INTRA_ROCE_ENABLE=0`、`HCCL_OP_EXPANSION_MODE=AIV`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True` 共同控制集合通信走 PCIe/AIV、显存按段可扩展分配。
- **权重与运行时显存分离**：原文："The weight size is a storage requirement, not an estimate of runtime NPU memory; KV cache, activations, communication buffers, and the optional draft also need memory." 即 1.49 TB 仅指存储，运行时还须预算 KV cache / 激活 / 通信缓冲 / draft 模型。
- **多镜像一致性要求**：原文："All nodes must use the same model revision and compatible software stack." 并且 base 镜像 pin digest 以保证可复现部署。

**关键数据（原文标注）**：
- 权重存储：约 **1.49 TB**
- 层数：**93**；专家数：**896**
- 拓扑：**DP4 / TP16 / EP64**
- 上下文长度：**133120**
- 单次迭代 token 上限：**8192**
- 单引擎并发序列：**16**
- GPU 内存利用率：**0.85**
- HCCL 缓冲：普通 **1024**，EP 通道 **2048**
- `num_speculative_tokens`：GQA/MLA draft 为 **7**，Block5 为 **5**
- 引擎就绪超时：**7200 s**；执行模型超时：**3000 s**

---

## 【表格解读】

原文表格（3.1 Model Weights and Hardware）逐字还原：

| Model | Download | Purpose | Requirements |
| --- | --- | --- | --- |
| Eco-Tech/Kimi-K3-w4a8 | [ModelScope](https://www.modelscope.cn/models/Eco-Tech/Kimi-K3-w4a8) | Full 93-layer, 896-expert W4A8 target | About 1.49 TB of weight storage; the reference deployment uses four Atlas 800 A3 nodes with 16 logical NPUs per node (DP4/TP16/EP64) |
| RadixArk/Kimi-K3-DSpark | [ModelScope](https://www.modelscope.cn/models/RadixArk/Kimi-K3-DSpark) / [Hugging Face](https://huggingface.co/RadixArk/Kimi-K3-DSpark) | Optional GQA draft | Set `num_speculative_tokens` to `7` |
| Inferact/Kimi-K3-DSpark | [ModelScope](https://www.modelscope.cn/models/Inferact/Kimi-K3-DSpark) / [Hugging Face](https://huggingface.co/Inferact/Kimi-K3-DSpark) | Optional MLA draft | Set `num_speculative_tokens` to `7` |
| Inferact/Kimi-K3-DSpark-Block5 | [ModelScope](https://www.modelscope.cn/models/Inferact/Kimi-K3-DSpark-Block5) / [Hugging Face](https://huggingface.co/Inferact/Kimi-K3-DSpark-Block5) | Optional MLA draft with five-token blocks | Set `num_speculative_tokens` to `5` |

**逐行解读**：

- **第 1 行（主模型）**：唯一必装的"主"权重，**93 层、896 专家**、W4A8 量化；存储需求约 **1.49 TB**；参考部署形态锁定为 **4 × Atlas 800 A3（每节点 16 逻辑 NPU）**，并行方式 **DP4/TP16/EP64**。该行定义了整篇教程的硬件与并行基线。
- **第 2 行（RadixArk GQA draft）**：可选 GQA（Grouped-Query Attention）形式 draft 模型，用于 DSpark 投机解码；使用时应将 `num_speculative_tokens` 设为 **7**，提示每步草拟 7 个 token。
- **第 3 行（Inferact MLA draft）**：可选 MLA 形式 draft，与主模型注意力机制对齐；同样设 `num_speculative_tokens=7`，与上一行数值一致但内部实现是 MLA 而非 GQA。
- **第 4 行（Inferact MLA Block5 draft）**：MLA draft 的变体，以"五 token 块"组织草拟序列，`num_speculative_tokens=5`——其值不同于上两行，提示该变体每步草拟 5 token，可能在某些工作负载下命中率与延迟更平衡。

原文还指出这些权重、tokenizer、processor 文件需提前下载，并在每个节点上以**相同路径**挂载（例如 `/path/to/models`）。

---

## 【公式解读】

**原文无公式**（文档中仅出现命令行参数、JSON 配置片段与变量赋值，未给出任何 LaTeX/伪代码形式的数学公式）。

---

## 【关联】

- **上游特性支持矩阵** → `../../user_guide/support_matrix/supported_models.md`：用于核对 Kimi-K3 在 vllm-ascend 当前 main 分支中的官方支持状态（功能/精度/平台列）。
- **特性配置入口** → `../../user_guide/feature_guide/index.md`：与本文"支持的特性"一节对应，覆盖 TP/DP/EP、Prefix Cache、ACL Graph、DSpark 等开关的总览。
- **多节点互联前置** → `../../getting_started/installation.md#installation-multi-node-interconnect`：3.2 节明确要求在启动四节点服务前先做互联校验，对应此章节锚点。
- **宿主机驱动/固件要求** → `../../getting_started/installation.md#installation-requirements`：4.1 节引用此章节作为 Atlas A3 宿主环境基线。
- **已有 CANN 环境下的源码安装** → `../../getting_started/installation.md#installation-existing-cann-install`：4.2 节指出非 Docker 安装时使用此指南，但需替换为 main checkout + 验证过的 vLLM commit，而非通用示例里的旧版本。
- **常见问题** → `../../faqs.md`：本文未在正文引用，但作为部署 Kimi-K3 时的兜底排查入口。
- **准确性与性能评估** → `../../developer_guide/evaluation/using_ais_bench.md`、`../../developer_guide/evaluation/using_lm_eval.md`、`../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation`：原文第 1 节明确提到涵盖"accuracy and performance evaluation"，但第 6、7 节的评估命令被截断（见下文【使用方法】），因此这些链接是预期的下游引用对象。
- **性能调优** → `../../developer_guide/performance_and_debug/optimization_and_tuning.md`：与本文大上下文长度（133120）、FULL_DECODE_ONLY、EP 通信优化（`HCCL_BUFFSIZE_EP=2048`）等调优手段形成上下游关系。

---

## 【使用方法】

> 注：原文在第 5 节末尾被截断（"...Check capacity with the actual checkpoi"），第 6 节"Accuracy Evaluation"、第 7 节"Performance Evaluation"、以及 DSpark 启动的完整命令未给出，故以下仅整理原文**已出现**的可执行内容。

**1. 镜像拉取与启动容器（每个节点）**

原文给定的 nightly 镜像为 `quay.io/ascend/vllm-ascend:nightly-main-a3`；容器挂载 16 个 `/dev/davinci*`、davinci_manager、devmm_svm、hisi_hdc，以及 `/usr/local/dcmi`、`/usr/local/Ascend/driver`、`/usr/local/bin/npu-smi`、`/etc/ascend_install.info` 和 `$MODEL_ROOT` 路径；网络模式 `--net=host`，共享内存 `--shm-size=1g`。

**2. 验证版本**

```shell
python -m pip show vllm vllm-ascend
```

**3. 源码构建（可选，替代 nightly）**

```shell
git clone --branch main https://github.com/vllm-project/vllm-ascend.git
cd vllm-ascend
git submodule update --init --recursive
docker build -f Dockerfile.a3 \
  --build-arg VLLM_COMMIT="$(cat .github/vllm-main-verified.commit)" \
  -t vllm-ascend-kimi-k3:main .
export IMAGE=vllm-ascend-kimi-k3:main
```

构建后用相同的容器启动命令（4.1 节），仅替换 `IMAGE` 值。

**4. 四节点服务公共环境变量（每节点设置）**

```
MODEL_PATH, TOKENIZER_PATH, LOCAL_IP, NODE0_IP, NIC_NAME
SERVICE_PORT=8000, RPC_PORT=13345
DP_SIZE=4, TP_SIZE=16
HCCL_IF_IP=$LOCAL_IP
GLOO_SOCKET_IFNAME=$NIC_NAME
TP_SOCKET_IFNAME=$NIC_NAME
HCCL_SOCKET_IFNAME=$NIC_NAME
VLLM_ENGINE_READY_TIMEOUT_S=7200
VLLM_EXECUTE_MODEL_TIMEOUT_SECONDS=3000
PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
HCCL_BUFFSIZE=1024
HCCL_BUFFSIZE_EP=2048
HCCL_INTRA_PCIE_ENABLE=1
HCCL_INTRA_ROCE_ENABLE=0
HCCL_OP_EXPANSION_MODE=AIV
OMP_PROC_BIND=false
OPENBLAS_NUM_THREADS=1
ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
```

**5. Node 0 启动命令**

```shell
vllm serve "$MODEL_PATH" \
  --host 0.0.0.0 --port $SERVICE_PORT \
  --served-model-name kimi-k3 \
  --tokenizer "$TOKENIZER_PATH" --tokenizer-mode kimi_k3 \
  --quantization ascend --safetensors-load-strategy lazy \
  --tensor-parallel-size $TP_SIZE --data-parallel-size $DP_SIZE \
  --data-parallel-size-local 1 \
  --data-parallel-address $LOCAL_IP --data-parallel-rpc-port $RPC_PORT \
  --enable-expert-parallel --enable-prefix-caching \
  --max-model-len 133120 --max-num-seqs 16 --max-num-batched-tokens 8192 \
  --gpu-memory-utilization 0.85 \
  --reasoning-parser kimi_k3 --tool-call-parser kimi_k3 --enable-auto-tool-choice \
  --compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}'
```

**6. Node 1–3 启动命令**

与 Node 0 相同，但需：
- 在命令前 `export DP_START_RANK="<1_OR_2_OR_3>"`
- 增加 `--headless`
- 将 `--data-parallel-start-rank $DP_START_RANK` 加入参数
- 将 `--data-parallel-address` 指向 `$NODE0_IP`（而非本节点的 `$LOCAL_IP`）

**7. DSpark draft 模型启用方式**

原文仅说明"DSpark with a matching draft checkpoint"作为支持特性，并指出：
- 选用 `RadixArk/Kimi-K3-DSpark`（GQA）→ `num_speculative_tokens=7`
- 选用 `Inferact/Kimi-K3-DSpark`（MLA）→ `num_speculative_tokens=7`
- 选用 `Inferact/Kimi-K3-DSpark-Block5`（MLA 五 token 块）→ `num_speculative_tokens=5`

**具体的 `vllm serve` 中如何挂载 draft 模型（如 `--speculative-model` 等参数）原文未给出完整命令，属于截断部分。**

**8. 评估命令**

原文第 1 节声明涵盖"accuracy and performance evaluation"，但**对应的第 6、7 节正文未包含在本文档片段内**，故**具体的 AIS Bench / lm_eval 启动命令、评估数据集与吞吐/时延指标均原文未涉及**。
