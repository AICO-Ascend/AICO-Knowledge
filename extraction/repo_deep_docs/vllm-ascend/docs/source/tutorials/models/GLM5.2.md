# GLM-5.2

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/GLM5.2.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/GLM5.2.md

# 深度解读: docs/source/tutorials/models/GLM5.2.md

---

## 【定位】

本篇文档是 vllm-ascend 项目针对 **GLM-5.2 (MoE 架构大模型)** 在华为 Atlas 800 A2/A3 昇腾 NPU 上的端到端部署与验证指南,完整覆盖**模型权重获取 → 环境准备 (Docker/源码安装) → 单节点/多节点部署 → 精度与性能评估**全链路,并按"context 长度 (1M 以下 / 1M)、硬件 (A3/A2)、部署模式 (单节点/多节点共部署/Prefill-Decode 分离)"三个维度组织验证场景。

---

## 【技术要点】

1. **模型架构**: GLM-5.2 采用 Mixture-of-Experts (MoE) 架构,面向复杂系统工程与长时序 agentic 任务。原文链接指向 HuggingFace `zai-org/GLM-5.2`,权重托管在 ModelScope `ZhipuAI/GLM-5.2`。

2. **三种权重的硬件需求矩阵** (原文 3.1):
   - `GLM-5.2` (BF16): 需 **2 节点 Atlas 800 A3 (128GB × 8)** 或 **4 节点 Atlas 800 A2 (64GB × 8)**
   - `GLM-5.2-w8a8` (W8A8 量化): 需 **1 节点 Atlas 800 A3 (128GB × 8)** 或 **2 节点 Atlas 800 A2 (64GB × 8)**
   - `GLM-5.2-w4a8c8` (W4A8C8 量化): 需 **1 节点 Atlas 800 A3 (128GB × 8)** 或 **2 节点 Atlas 800 A2 (64GB × 8)**;可在 **1 节点 Atlas 800 A3 (64GB × 16)** 部署
   - 量化工具: `msmodelslim` (Ascend 开源, gitcode.com/Ascend/msmodelslim)

3. **Docker 镜像**: `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3` (A3 系列) 与无 `-a3` 后缀版本 (A2 系列)。A3 启动脚本暴露 **16 个 `/dev/davinci0`-`davinci15` 设备**,A2 启动脚本仅暴露 **0-7 共 8 个 davinci 设备**。

4. **单节点 A3 部署核心命令参数** (5.1.1.1, `GLM-5.2-w4a8c8`):
   - `--tensor-parallel-size 8` + `--data-parallel-size 2` (DP2 TP8)
   - `--enable-expert-parallel`(MoE 必须)
   - `--quantization ascend`
   - `--max-model-len 135000`,`--max-num-seqs 12`,`--max-num-batched-tokens 8192`
   - `--gpu-memory-utilization 0.92`
   - `--compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}'`
   - `--speculative-config '{"num_speculative_tokens": 3, "method": "deepseek_mtp", "enforce_eager": true}'`
   - `--tool-call-parser glm47` + `--reasoning-parser glm45` + `--enable-auto-tool-choice`

5. **Ascend 特有 `--additional-config` 字段** (原文逐一解释):
   - `enable_dsa_cp: true` — DSA 上下文并行,加速长上下文 prefill
   - `enable_sparse_li_c8: true` — C8 量化模型的稀疏注意力优化
   - `enable_balance_scheduling: true` — v1 调度器负载均衡,提升吞吐、降低 TPOT
   - `multistream_overlap_shared_expert: true`
   - `enable_fused_mc2: 0` — 此场景关闭融合算子,与上述多流共享专家冲突

6. **HCCL 与运行环境变量** (A3 单节点启动脚本前):
   - `HCCL_OP_EXPANSION_MODE="AIV"`
   - `HCCL_TRANSFER_TIMEOUT=600`、`HCCL_EXEC_TIMEOUT=3600`、`HCCL_CONNECT_TIMEOUT=3600`
   - `HCCL_BUFFSIZE=200`
   - `OMP_PROC_BIND=false`、`OMP_NUM_THREADS=1`
   - `PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`

---

## 【关键机制与数据】

**工作原理 / 数据流**:

- **专家并行 (Expert Parallel)**: GLM-5.2 是 MoE 模型,`--enable-expert-parallel` 必开;不同 DP/TP 组合对应不同吞吐/延迟权衡 (DP2 TP8 平衡容量与计算;`dp1tp16` + 关 EP 可换更低延迟但牺牲吞吐,原文 5.1.1.1)。
- **MTP (Multi-Token Prediction) 推测解码**: 使用 DeepSeek 风格的 MTP 草稿头;`num_speculative_tokens: 3`(3-5 范围内可调);`enforce_eager: true` 是因为 GLM-5.2 不支持 graph-mode 推测解码 (原文参数说明)。
- **CUDA Graph**: 仅在 decode 阶段捕获 (`FULL_DECODE_ONLY`),用于减少 kernel 启动开销。
- **DSA-CP 上下文并行**: 长上下文 prefill 加速;开启后 `layer_sharding` 不能包含 `o_proj`(原文)。
- **多流共享专家 overlap** (`multistream_overlap_shared_expert`): 与 `enable_fused_mc2` 在该场景下互斥;多节点场景则可开启融合算子获益 (原文)。
- **共享目录建议**: 多节点部署时权重放在共享目录,如 `/root/.cache/`。

**性能 / 数据**: **原文未给出具体数值**(如 tokens/s、TTFT、TPOT 等 benchmark 数据);仅在参数说明中提及"低延迟场景用 `dp1tp16` 但吞吐更低""某些场景 TTFT 可能下降"等定性描述。性能评估方法指向 `using_ais_bench.md` (内部链接)。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

| 内部链接 | 关联关系 |
|---|---|
| `../../user_guide/support_matrix/supported_models.md` | GLM-5.2 在 vllm-ascend 中的**功能支持矩阵**(第 2 节指向,用于查 GLM-5.2 启用了哪些 vLLM 特性) |
| `../../user_guide/feature_guide/index.md` | **功能配置指南**(第 2 节指向,用于详细功能开关) |
| `../../getting_started/installation.md#installation-multi-node-interconnect` | **多节点互联互通验证**(第 3.2 节指向,多节点部署前置) |
| `../../getting_started/installation.md` | **源码安装 vllm-ascend**(第 4.2 节指向) |
| `../../developer_guide/evaluation/using_ais_bench.md` | **使用 ais_bench 做精度评估**;其中 `#execute-performance-evaluation` 锚点对应**性能评估执行**步骤 |
| `../../developer_guide/performance_and_debug/optimization_and_tuning.md` | **性能调优与优化指南**(文档结构暗示的下游: `additional_config` 各字段的深度调优方法在此) |
| `../../user_guide/support_matrix/feature_matrix.md` | **功能矩阵**(与 `supported_models.md` 对应,但粒度为"功能×模型") |

**模块上下游关系**: 本教程是 GLM-5.2 专用"最佳实践汇编",其上游依赖安装文档 (installation) 与功能支持矩阵 (supported_models / feature_matrix);下游衔接**评估流程** (ais_bench 精度 + 性能) 与**调优指南** (optimization_and_tuning)。

---

## 【使用方法】

**启用方式 / 配置项 (原文摘录)**:

1. **Docker 镜像启动 (A3)**:
   ```shell
   export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3
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
     -v /root/.cache:/root/.cache \
     -it $IMAGE bash
   ```

2. **Docker 镜像启动 (A2)**: 同样的 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}` 镜像,只挂载 `davinci0`-`davinci7` (8 卡)。

3. **vLLM 在线服务启动 (A3 单节点 w4a8c8)**:
   ```shell
   export HCCL_OP_EXPANSION_MODE="AIV"
   export HCCL_TRANSFER_TIMEOUT=600
   export HCCL_EXEC_TIMEOUT=3600
   export HCCL_CONNECT_TIMEOUT=3600
   export OMP_PROC_BIND=false
   export OMP_NUM_THREADS=1
   export HCCL_BUFFSIZE=200
   export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
   vllm serve /root/.cache/modelscope/hub/models/vllm-ascend/GLM-5.2-w4a8c8 \
     --host 0.0.0.0 --port 8077 \
     --safetensors-load-strategy prefetch \
     --api-server-count 1 \
     --data-parallel-size 2 --enable-expert-parallel --tensor-parallel-size 8 \
     --seed 1024 --served-model-name glm-5 \
     --tool-call-parser glm47 --reasoning-parser glm45 --enable-auto-tool-choice \
     --max-num-seqs 12 --max-model-len 135000 --max-num-batched-tokens 8192 \
     --trust-remote-code --gpu-memory-utilization 0.92 \
     --quantization ascend \
     --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
     --additional-config '{"enable_dsa_cp": true, "enable_sparse_li_c8": true, "enable_balance_scheduling": true, "multistream_overlap_shared_expert": true, "enable_fused_mc2": 0}' \
     --speculative-config '{"num_speculative_tokens": 3, "method": "deepseek_mtp", "enforce_eager": true}'
   ```

4. **多节点部署前置**: 需先按 `installation.md#installation-multi-node-interconnect` 验证多节点通信;每个节点都要执行相同的容器启动与环境变量设置。

5. **精度 / 性能评估**: 参考 `using_ais_bench.md`(整体流程)与 `#execute-performance-evaluation` 锚点(执行性能评估)。

> **注**: 原文在 5.1.1.1 节末尾 "**`--additional-config` fields**" 子节对 `multistream_overlap_shared_expert` 的解释行未完整呈现(`true` 后无后续说明文字),且 5.1 之后的小节 (5.1.1.2 单节点 A3、其他场景如多节点 A3、A2 单节点/多节点、Prefill-Decode 分离) 在提供的原文片段中**未给出**,属文档后续章节内容。
