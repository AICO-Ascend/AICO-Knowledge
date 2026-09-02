# Hy4-preview (Experimental)

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Hy4-preview.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Hy4-preview.md

# Hy4-preview 部署指南 一体化深度解读

## 【定位】

这篇文档解决"如何在华为昇腾 NPU（仅 Atlas 800I A3）上,通过 vLLM-Ascend 的官方 Docker 镜像 `quay.io/ascend/vllm-ascend:hy4-a3`,完成腾讯混元 Hy4-preview（770B MoE 模型,W8A8 量化权重）的快速推理部署"这一问题,描述的是该模型在 A3 硬件上的开箱即用实验性部署能力。

---

## 【技术要点】

1. **模型规模与架构**:总参数量 **770B**,每个 token 激活约 **49B**;骨干由 **78 层**组成(第 1 层为标准 Dense FFN,其余 **77 层**为 MoE);每 MoE 层含 **256 个 Routed Experts + 1 个 Shared Expert**,每 token 通过 **Top-8** 路由选择专家,共享专家始终激活。

2. **原生 MTP(Speculative Decoding)**:除骨干外还内置 **1 层 native MTP**,MTP 层总参数约 **10B**,每个 token 激活约 **0.7B**,通过 `--speculative-config '{"method": "mtp", "num_speculative_tokens": 3}'` 启用,推测步数为 3。

3. **硬件与软件栈强绑定**:仅支持 **Atlas 800I A3(A3)** 16 卡节点;推荐 **HDK 25.5.0 / CANN 9.0.1 / torch_npu 2.10.0.post2**,vLLM 与 vLLM-Ascend 均基于 **v0.23.0**。

4. **并行拓扑**:节点内 **TP=16**(`--tensor-parallel-size 16`)全卡拆分 + **EP**(`--enable-expert-parallel`,将 256 routed + 1 shared 专家分布到各 NPU);跨节点 **DP=2**(`--data-parallel-size 2`)可将上下文扩展到 **96K**。

5. **量化与图优化**:采用 Ascend **W8A8 量化**(`--quantization ascend`,权重约 **762 GB**);Decode 阶段使用 `--compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}'` 捕获图,并通过 `--additional-config '{"ascend_compilation_config": {"enable_npugraph_ex": true}}'` 启用 NPUGraph EX 优化。

6. **运行时关键环境变量**:`HCCL_BUFFSIZE=128`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`、`ASCEND_LAUNCH_BLOCKING=0`、`VLLM_USE_V1=1`、`VLLM_ASCEND_ENABLE_MLAPO=1`、`VLLM_ASCEND_ENABLE_FUSED_MC2=1`、`VLLM_ENGINE_READY_TIMEOUT_S=1800`。

7. **交付形态限制**:配套代码**尚未合入** vLLM-Ascend 主仓,**不支持** `pip install` 或源码构建,只能使用 `quay.io/ascend/vllm-ascend:hy4-a3` Docker 镜像。

---

## 【关键机制与数据】

- **路由机制(原文)**:"the model selects the **Top-8** experts from the 256 routed experts for computation, while always activating the shared expert"——每 token 仅激活 8/256 个 routed 专家,加上恒激活的 shared expert,实现稀疏激活以降低单 token 计算量。

- **MTP 投机解码(原文)**:"1 native MTP (Multi-Token Prediction) layer built in to support speculative decoding. The MTP layer has a total of about **10B** parameters, with about **0.7B** parameters activated per token."——MTP 作为草稿模型,主模型每步验证其产出,`num_speculative_tokens=3` 即每步最多投机 3 个 token。

- **上下文长度与节点数的关系(原文)**:"a single A3 node only supports about 1K context. If you need to test long sequences such as 32K, it is recommended to use 2 A3 nodes"——单节点仅 ~1K 上下文;双节点 DP=2 可扩到 **96K**。

- **单节点部署限参(原文)**:`--max-num-seqs 8`、`--max-model-len 512`、`--max-num-batched-tokens 512`、`--gpu-memory-utilization 0.92`,定位是"validation and low-concurrency short-sequence scenarios"。

- **NPUGraph EX(原文)**:"Ascend-specific graph execution optimization",与 `FULL_DECODE_ONLY` 联合使用以降低 decode 阶段 kernel launch 开销。

- **Fused MC2 / MLAPO(原文)**:`VLLM_ASCEND_ENABLE_FUSED_MC2=1` 与 `VLLM_ASCEND_ENABLE_MLAPO=1` 为 Ascend 侧开启融合 MC2 通信与 MLAPO 优化的开关,具体语义文档未展开。

- **Automatic Prefix Caching(原文)**:`--enable-prefix-caching`,复用共享前缀的 KV cache。

- **容器挂载点(原文)**:A3 为 16 卡设备,需挂载 `/dev/davinci[0-15]`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`,以及驱动库 `/usr/local/Ascend/driver/lib64/`、`npu-smi`、`hccn_tool` 与 `version.info`、`/etc/ascend_install.info`,并将宿主机 `/mnt/weight` 映射至容器同路径。

- **多节点网络(原文)**:节点使用 `--net=host`,Node1(`192.168.1.1`)承担 DP rank 0 与 API,Node2(`192.168.1.2`)为 headless worker,启动顺序"Node1 先执行"(原文在此处被截断)。

---

## 【表格解读】

### 表 1:Supported Features(已验证命令中启用的特性)

| Feature | Description | Configuration |
| --- | --- | --- |
| Tensor Parallel (TP) | Splits the model across all 16 NPUs within a node. | `--tensor-parallel-size 16` |
| Expert Parallel (EP) | Distributes the MoE experts (256 routed + 1 shared per layer) across NPUs. | `--enable-expert-parallel` |
| Data Parallel (DP) | Multi-node DP across 2 nodes, extending the context to 96K. | `--data-parallel-size 2` |
| W8A8 Quantization | Loads the W8A8 quantized weights (Ascend quantization). | `--quantization ascend` |
| Automatic Prefix Caching | Reuses the KV cache for shared prompt prefixes. | `--enable-prefix-caching` |
| Speculative Decoding (MTP) | Uses the native MTP layer for Multi-Token Prediction. | `--speculative-config '{"method": "mtp", "num_speculative_tokens": 3}'` |
| Decode Graph Capture | Captures the decode phase into a graph to reduce kernel launch overhead. | `--compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}'` |
| NPUGraph EX | Ascend-specific graph execution optimization. | `--additional-config '{"ascend_compilation_config": {"enable_npugraph_ex": true}}'` |

**逐行解读**:
- **TP=16**:与 A3 节点物理 16 卡对应,模型层参数在该节点 16 张 NPU 上切分。
- **EP**:将每层 256 个 routed 专家 + 1 个 shared 专家分布到多卡,MoE 经典做法,通常与 TP 正交。
- **DP=2(仅多节点)**:两个节点各跑一份 TP=16 的模型副本,数据并行;能扩展到 96K 上下文,弥补单节点 1K 的局限。
- **W8A8 量化**:`ascend` 量化后端,与 ModelScope 上的 `Hy4-preview-w8a8` 权重配套。
- **Prefix Caching**:共享 prompt 前缀复用 KV,降低重复 prefill 开销。
- **MTP 投机**:`num_speculative_tokens=3` 表示每主模型步最多投机 3 个 draft token,需主模型一次性 verify。
- **FULL_DECODE_ONLY cudagraph**:只对 decode 阶段做图捕获,prefill 仍走原路径,可减少 decode 阶段 CPU launch overhead。
- **NPUGraph EX**:Ascend 私有图执行优化,与上一项协同降低 kernel launch 成本。

> 注:原文明确指出 LoRA、Pipeline Parallel、Prefill-Decode Disaggregation 在本文档中**未经验证**。

### 表 2:Model Weight

| Model | Weight |
| --- | --- |
| Hy4-preview | https://huggingface.co/tencent/Hy4-preview |
| Hy4-preview-w8a8 | https://www.modelscope.cn/models/Eco-Tech/Hy4-preview-w8a8 |

**逐行解读**:第一行为官方原版权重(HF);第二行为本教程实际使用的 **W8A8 量化版**,体量约 **762 GB**,需下载到本地磁盘(建议 `/mnt/weight`)。

### 表 3:Hardware and Software Preparation

| Hardware | Ascend HDK | CANN version | torch_npu version | vLLM | vLLM-Ascend version |
| --- | --- | --- | --- | --- | --- |
| Atlas 800I A3 (A3) | 25.5.0 (recommended) | CANN 9.0.1 | 2.10.0.post2 | Based on v0.23.0 | Based on v0.23.0 |

**逐行解读**:硬件仅 A3 一行,说明本模型在该硬件族外**不支持**;HDK 25.5.0 为推荐(非强制);CANN、torch_npu、vLLM、vLLM-Ascend 给出唯一一组基线版本(v0.23.0),用于锁定可复现性。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **../../user_guide/support_matrix/supported_models.md**:被 §2 引用,用于给出 Hy4-preview 的**完整**支持矩阵(本文档中列出的只是已验证命令中启用的特性,并非"全支持")。
- **../../user_guide/feature_guide/index.md**:被 §2 引用,作为各项特性(TP/EP/DP/Prefix Caching/MTP/cudagraph/NPUGraph EX 等)**配置项语义**的权威说明来源。
- **../../getting_started/installation.md#installation-multi-node-interconnect**:被 §3.3 引用,描述多节点 HCCN 互联的验证步骤,与本文 DP=2 多节点部署直接对应。
- **../../developer_guide/evaluation/using_ais_bench.md** 与 **#execute-performance-evaluation**:文末提供的内部链接(虽文档本体在此处被截断未直接展示),对应使用 **ais_bench** 工具对该部署进行性能评估的章节,属于性能验证下游。

模型本体层面:Hy4-preview = DeepSeek 类 MoE 架构(Dense 1 层 + 77 层 MoE,256 routed / 1 shared,Top-8 路由) + MTP 投机解码;在 vLLM-Ascend 上以 `ascend` W8A8 后端、`FULL_DECODE_ONLY` cudagraph + `enable_npugraph_ex` 作为 Ascend 侧图栈;并行拓扑是 **TP×EP(节点内) + DP(节点间)**。

---

## 【使用方法】

1. **拉取镜像**(原文 §4.1):
   ```bash
   docker pull quay.io/ascend/vllm-ascend:hy4-a3
   ```

2. **创建容器**(原文 §4.1):挂载 16 张 NPU(`/dev/davinci[0-15]`)、管理设备、驱动库、权重目录(`/mnt/weight`),并设置 `--shm-size=1000g`。

3. **进入容器**:`docker exec -it ${CONTAINER_NAME} bash`。

4. **单节点部署命令**(原文 §5.1):
   ```bash
   export HCCL_BUFFSIZE=128
   export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
   export ASCEND_LAUNCH_BLOCKING=0
   export VLLM_LOGGING_LEVEL=INFO
   export VLLM_USE_V1=1
   export VLLM_ASCEND_ENABLE_MLAPO=1
   export VLLM_ASCEND_ENABLE_FUSED_MC2=1
   export VLLM_ENGINE_READY_TIMEOUT_S=1800

   vllm serve /path/to/Hy4-preview-w8a8 \
     --host 127.0.0.1 --port 8000 \
     --tensor-parallel-size 16 \
     --served-model-name hy4 \
     --max-num-seqs 8 \
     --max-model-len 512 \
     --max-num-batched-tokens 512 \
     --enable-expert-parallel \
     --trust-remote-code \
     --quantization ascend \
     --gpu-memory-utilization 0.92 \
     --seed 1024 \
     --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
     --speculative-config '{"method": "mtp","num_speculative_tokens": 3}' \
     --additional-config '{"ascend_compilation_config": {"enable_npugraph_ex": true}}'
   ```

5. **多节点 DP=2 部署**(原文 §5.2,文本被截断):原文明确——两节点使用 `--net=host`、复用与单节点相同的 `vllm serve` 命令,Node1(`192.168.1.1`)承担 DP rank 0 + API,Node2(`192.168.1.2`)为 headless worker,启动顺序"先 Node1"。**具体的 headless worker 命令、环境变量差异、对外 API 入口选择等细节在所提供原文中未出现**(原文在 "1. First execute th" 处被截断,后续章节 §6 及以后也未给出)。

6. **前置验证命令**(原文 §3.2):`npu-smi info`(确认 HDK/驱动);多节点通信验证见 `../../getting_started/installation.md#installation-multi-node-interconnect`。

7. **源码安装**(原文 §4.2):**不支持**,仅可通过 §4.1 的 Docker 镜像使用。
