# Qwen3-VL-235B-A22B-Instruct

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3-VL-235B-A22B-Instruct.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-VL-235B-A22B-Instruct.md

# Qwen3-VL-235B-A22B-Instruct 文档深度解读

## 【定位】

本文档是 vLLM-Ascend 在 `v0.12.0` 引入的对 Qwen3-VL-235B-A22B-Instruct（Qwen3-VL 系列大规模稀疏 MoE 视觉语言模型）的端到端部署与验证指南，覆盖单/多节点部署、PD 分离、功能与精度验证、性能调优及 FAQ 章节。

---

## 【技术要点】

1. **模型家族定位**：原文标注为「large-scale sparse MoE vision-language model in the Qwen3-VL family」，面向多模态对话、图像理解、多图像推理、OCR 类视觉问答及长上下文生成。
2. **三套权重与硬件映射**（关键数字原文）：
   - BF16 版本：1 台 Atlas 800 A3（64G × 16）或 2 台 Atlas 800 A2（64G × 8）
   - w8a8-QuaRot 量化版本：1 台 Atlas 800 A3（64G × 16）（单节点验证主用）
   - w8a8-mxfp8 量化版本：1 台 Ascend 950DT（96G × 8）
3. **Docker 镜像差异**（按系列）：
   - Ascend 950DT：`--shm-size=1g`，暴露 8 个 davinci 设备（davinci0–7）+ davinci_manager/hisi_hdc/ummu/uburma，挂在 `/etc/hixlep/`
   - A3 系列：`--shm-size=512g`，暴露 16 个 davinci 设备（davinci0–15）
   - A2 系列：`--shm-size=512g`，暴露 8 个 davinci 设备（davinci0–7）
4. **单节点 950DT 在线部署核心参数**（原文）：
   - 模型：`Eco-Tech/Qwen3-VL-235B-A22B-Instruct-w8a8-mxfp8`，`--quantization ascend`
   - 并行：`--tensor-parallel-size 8`、`--data-parallel-size 1`、`--enable-expert-parallel`、`--distributed-executor-backend mp`
   - 容量：`--max-num-seqs 32`、`--max-model-len 32768`、`--max-num-batched-tokens 8192`、`--gpu-memory-utilization 0.9`
   - 多模态闸门：`--limit-mm-per-prompt.image 1`、`--limit-mm-per-prompt.video 0`、`--mm-processor-cache-gb 0`、`--no-enable-prefix-caching`
   - 编译：`--compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}'`
5. **关键运行时环境变量**（原文）：
   - `VLLM_USE_MODELSCOPE=True`（从 ModelScope 加速下载）
   - `PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`（降低 NPU 显存碎片）
   - `HCCL_OP_EXPANSION_MODE="AIV"`、`HCCL_BUFFSIZE=400`
   - `OMP_PROC_BIND=false`、`OMP_NUM_THREADS=100`
   - `TASK_QUEUE_ENABLE=1`
6. **W8A8 量化约束**：原文注明「The W8A8 version needs `--quantization ascend`」——所有 w8a8 路径必须在 vLLM 启动命令中显式声明 `ascend` 后端量化器。
7. **源码安装流程**（原文命令链）：先 `git clone vllm && pip install -e .`，再 `git clone vllm-ascend && pip install -e .`；多节点场景下需在每个节点重复执行。
8. **文档完整性与截断**：原文第 5.1 节 A3 分支在「Run the following script」后中断，第 5 节其余小节（多节点、PD 分离、验证、调优、FAQ）均未在所提供原文片段中给出。

---

## 【关键机制与数据】

- **工作机制**：单节点部署中 Prefill 与 Decode 共置（原文：「Single-node deployment runs both Prefill and Decode on the same node」），通过 TP=8 + DP=1 + Expert Parallel 把 235B 参数（含专家子集）切分到 8 张 NPU 卡。
- **显存管理机制**：利用 `expandable_segments` 分配策略与 `gpu-memory-utilization=0.9` 预留 KV 缓冲；通过 `--mm-processor-cache-gb 0` 与 `--no-enable-prefix-caching` 主动关闭多模态处理器缓存与前缀缓存，避免长视觉序列占用稀缺显存。
- **算子/通信路径**：使用 HCCL 的 `AIV` 扩展模式（`HCCL_OP_EXPANSION_MODE="AIV"`）与 400 字节通信缓冲，提示在多机 RDMA 路径上启用向量加速通信。
- **性能数据**：原文**未提供**任何吞吐量、时延、tokens/s、TTFT 等数值指标，亦无 benchmark 表格。
- **数据流**：原文仅给出 vllm serve 命令行入口，未展示 client→prefill→decode→token-out 的完整数据流图。
- **功能/精度验证**：原文提及「functional verification」「accuracy and performance evaluation」「performance tuning」等章节标题，但未在所提供片段中给出实际脚本或指标。

---

## 【表格解读】

原文无显式表格，下表为依据原文 §3.1 整理的「模型权重-硬件需求」对应关系（非原文表格，仅作结构化呈现）：

| 权重版本 | 量化方式 | 适用硬件需求 | 用途 | 权重链接 |
|---|---|---|---|---|
| `Qwen3-VL-235B-A22B-Instruct`（BF16） | 无（BF16） | 1 节点 Atlas 800 A3（64G × 16） 或 2 节点 Atlas 800 A2（64G × 8） | 原始精度推理 | modelscope.cn/models/Qwen/Qwen3-VL-235B-A22B-Instruct/ |
| `Qwen3-VL-235B-A22B-Instruct-w8a8-QuaRot` | W8A8（QuaRot 旋转量化） | 1 节点 Atlas 800 A3（64G × 16） | 单节点验证（原文：quantized version used by single-node validation） | modelscope.cn/models/Eco-Tech/Qwen3-VL-235B-A22B-Instruct-w8a8-QuaRot |
| `Qwen3-VL-235B-A22B-Instruct-w8a8-mxfp8` | W8A8（mxfp8 微缩浮点） | 1 节点 Ascend 950DT（96G × 8） | 950DT 单节点部署 | modelscope.cn/models/Eco-Tech/Qwen3-VL-235B-A22B-Instruct-w8a8-mxfp8 |

**逐行解读**：
- 第 1 行：BF16 是模型官方原始权重，对显存压力最大，因此 A2 节点必须**两节点**协同才能容纳，A3 单节点即够。
- 第 2 行：QuaRot 量化后模型体积压缩，落在 A3 单节点 64G × 16 的容量内，并被原文明确指定为「单节点验证」的默认版本。
- 第 3 行：mxfp8 版本适配较新的 950DT 平台（96G × 8），意味着新一代卡可在单节点内承载 W8A8 量化后的完整模型。
- 原文建议：多节点场景下「download the model weight to a shared directory across multiple nodes」，避免重复下载。

下表为依据原文 §4.1 整理的「Docker 启动关键差异」：

| 系列 | IMAGE tag | --shm-size | davinci 设备数 | 关键挂载 |
|---|---|---|---|---|
| Ascend 950DT | `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-950DT` | 1g | 8（davinci0–7） | 含 `/etc/hixlep/`、`/usr/local/sbin`、`/usr/lib64`、`/dev/ummu`、`/dev/uburma` |
| A3 | `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3` | 512g | 16（davinci0–15） | 含 `/dev/devmm_svm`、`/usr/local/Ascend/driver/tools/hccn_tool`、`/etc/hccn.conf` |
| A2 | `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}` | 512g | 8（davinci0–7） | 同 A3（不含 a3 后缀） |

**逐行解读**：
- shm-size 差异：950DT 用 1g，A3/A2 用 512g，反映共享内存用于 Ascend 集合通信缓冲时，A 系列需要更大空间以承载 16/8 卡 HCCL 数据。
- 950DT 多挂 `/etc/hixlep/`、`/dev/ummu`、`/dev/uburma` 等新增虚拟化/管理设备，是 950DT 平台独有的运维通道。
- A3 比 A2 多暴露 8 个 davinci 设备，正好对应 A3 单节点 16 卡硬件拓扑。

---

## 【公式解读】

原文无公式。

---

## 【关联】

依据文末及行间内部链接，本文与其上游/兄弟模块的关系如下：

- **`../../user_guide/support_matrix/supported_features.md`** — Qwen3-VL-235B-A22B-Instruct 的特性兼容矩阵（如是否支持 V1、chunked prefill、LoRA、Speculative decoding 等）的统一查询入口，本文 §2 直接引用。
- **`../../user_guide/feature_guide/index.md`** — 各项功能的配置细节总览，对应 §2 中特性启用开关的详细文档。
- **`../../getting_started/installation.md#installation-multi-node-interconnect`** — 多节点互联（HCCL/RDMA）验证步骤；本文 §3.2 要求部署前参考该链接校验环境。
- **`../../getting_started/installation.md#installation-prebuilt-image`** — 预构建 Docker 镜像的官方用法说明；§4.1 中三套 docker run 脚本继承自此文档的设备挂载范式。
- **`../../getting_started/installation.md`** — 安装总入口；§4.2 源码安装与 §4.1 容器安装均最终回链至此。
- **`../../faqs.md`** — 常见问题排查手册；§1 末尾把 FAQ 作为文档组成部分之一列出。
- **`../features/pd_disaggregation_mooncake_multi_node.md`** — PD 分离（Prefill-Decode disaggregation）在 Mooncake 引擎、多节点拓扑下的特性文档；本文 §1 把「PD disaggregation」列为必述章节之一（推测与该文档对接）。
- 上下游关系总结：本 tutorial 文档是 vllm-ascend 文档树中**模型级落地页**，向上接 feature guide 与 support matrix（描述模型能跑哪些特性）、向下接安装/网络/FAQ（描述怎么跑起来），横向接 PD 分离特性（描述如何把单节点部署拆为多节点 prefill/decode）。

---

## 【使用方法】

**启用方式/配置项/命令**（均来自原文）：

1. **选权重**：依据 §3.1 表对应关系下载 BF16 / w8a8-QuaRot / w8a8-mxfp8 中的一种；多节点时下载到共享目录。
2. **多节点环境预检（可选）**：按 [installation-multi-node-interconnect](../../getting_started/installation.md#installation-multi-node-interconnect) 验证。
3. **容器启动（按系列三选一）**：
   - 950DT：`IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-950DT` 后执行 §4.1 中 950DT 段 docker run。
   - A3：`IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3` 后执行 A3 段 docker run。
   - A2：`IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}` 后执行 A2 段 docker run。
   - 校验：`docker ps | grep vllm-ascend`（应 `Up`）；`pip show vllm-ascend`（应显示版本）。
4. **源码安装（替代方案）**：
   ```bash
   git clone https://github.com/vllm-project/vllm.git && cd vllm && pip install -e .
   git clone https://github.com/vllm-project/vllm-ascend.git && cd vllm-ascend && pip install -e .
   pip show vllm vllm-ascend
   ```
   多节点时在每个节点重复执行。
5. **单节点在线部署（950DT + w8a8-mxfp8 范例，原文 §5.1）**：
   ```bash
   export VLLM_USE_MODELSCOPE=True
   export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
   export HCCL_OP_EXPANSION_MODE="AIV"
   export HCCL_BUFFSIZE=400
   export OMP_PROC_BIND=false
   export OMP_NUM_THREADS=100
   export TASK_QUEUE_ENABLE=1

   vllm serve Eco-Tech/Qwen3-VL-235B-A22B-Instruct-w8a8-mxfp8 \
     --host 0.0.0.0 --port 8000 \
     --distributed-executor-backend mp \
     --data-parallel-size 1 \
     --tensor-parallel-size 8 \
     --enable-expert-parallel \
     --seed 1024 \
     --quantization ascend \
     --served-model-name qwen3-vl-235b \
     --max-num-seqs 32 \
     --max-model-len 32768 \
     --max-num-batched-tokens 8192 \
     --trust-remote-code \
     --no-enable-prefix-caching \
     --mm-processor-cache-gb 0 \
     --limit-mm-per-prompt.image 1 \
     --limit-mm-per-prompt.video 0 \
     --gpu-memory-utilization 0.9 \
     --compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}'
   ```
6. **A3 系列单节点部署命令**：原文 §5.1 A3 分支被截断，原文未涉及具体脚本。
7. **多节点部署、PD 分离、functional verification、accuracy/perf eval、performance tuning、FAQs**：原文 §1 预告为文档后续章节，但在所提供片段中均未给出具体步骤，原文未涉及。
