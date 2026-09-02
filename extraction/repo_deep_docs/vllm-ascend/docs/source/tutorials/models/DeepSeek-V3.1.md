# DeepSeek-V3 & 3.1

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/DeepSeek-V3.1.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/DeepSeek-V3.1.md

# DeepSeek-V3 & 3.1 文档深度解读

## 【定位】

这篇文档是 vLLM-Ascend 镜像项目中针对 **DeepSeek-V3 / V3.1** 模型的端到端部署与验证指南，描述如何在 Ascend NPU 硬件（950DT / A3 / A2 系列）上完成该混合推理模型的特性矩阵查阅、环境准备、Docker 或源码安装、单/多节点在线服务部署以及精度与性能评测的全流程。

---

## 【技术要点】

1. **混合思考模式 (Hybrid thinking mode)**：一个模型通过切换 chat template 即可同时支持 thinking 与 non-thinking 两种推理模式，相比前代版本在工具调用、Agent 任务上经过 post-training 优化后性能显著提升；DeepSeek-V3.1-Think 在保持与 DeepSeek-R1-0528 相当答案质量的同时响应更快。

2. **多版本量化权重**：文档列出 6 类可用权重——BF16 原版（DeepSeek-V3.1）、w8a8-mtp-QuaRot、w4a8-mtp-QuaRot (Terminus)、w4a4c8-mxfp4、w8a8c8-mxfp8，均来自 ModelScope；统一推荐使用 `msmodelslim` 量化方法。

3. **多节点可选验证**：部署多节点前需按 `installation.md#installation-multi-node-interconnect` 校验互联环境；权重建议放入共享目录如 `/root/.cache/`。

4. **三套硬件的差异化 Docker 启动模板**：
   - Ascend 950DT：使用基础镜像 `quay.io/ascend/vllm-ascend:{{vllm_ascend_version}}`，挂载 `/dev/davinci0`–`davinci7` 共 8 卡；
   - A3 系列：使用后缀 `-a3` 镜像，挂载 0–15 号 davinci 设备；
   - A2 系列：与 A3 类似但仅挂载 0–7 号 davinci 设备；均通过 `--privileged=true`、`--net=host`、`--shm-size=1g` 与 `hccn_tool` 等驱动路径映射。

5. **单节点部署关键参数（原文以 Ascend 950DT 示例给出）**：环境变量 `HCCL_BUFFSIZE=512`、`HCCL_CONNECT_TIMEOUT=600`、`HCCL_EXEC_TIMEOUT=600`、`OMP_PROC_BIND=false`、`OMP_NUM_THREADS=10`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`、`TASK_QUEUE_ENABLE=1`；vLLM 启动参数包含 `--max_model_len 135168`、`--max-num-batched-tokens 16384`、`--gpu-memory-utilization 0.9`、`--tensor-parallel-size 8`、`--data-parallel-size 1`、`--enable-expert-parallel`、`--async-scheduling`、`--max-num-seqs 96`、`--no-enable-prefix-caching`、`--quantization ascend`，以及 `compilation-config={"cudagraph_mode": "FULL_DECODE_ONLY"}` 与 `speculative-config={"num_speculative_tokens": 3, "method": "deepseek_mtp"}`，并通过 `--additional_config` 启用 `enable_cpu_binding` / `multistream_overlap_shared_expert` / `enable_balance_scheduling` / `enable_mlapo`。

6. **A3 系列附加 HCCL 配置**：使用 `HCCL_OP_EXPANSION_MODE="AIV"`、`HCCL_IF_IP=$local_ip`、`GLOO_SOCKET_IFNAME=$nic_name`；可选 `LD_PRELOAD` 加载 `libjemalloc.so.2` 提升性能。

---

## 【关键机制与数据】

- **版本基线**：原文明确写明本文档基于 **vLLM-Ascend v0.9.1rc3** 验证；DeepSeek-V3.1 模型在该版本中首次被支持，**Ascend 950DT** 上需从 `vllm-ascend:v0.23.0rc1` 起。
- **部署规模**：原文给出量化模型 `DeepSeek-V3.1-w8a8-mtp-QuaRot` 可在 **1 台 Atlas 800 A3（64GB × 16）** 上完成单节点 Prefill + Decode 部署。
- **投机解码机制**：通过 `deepseek_mtp` 方法（MTP 即 Multi-Token Prediction）一次性产出 `num_speculative_tokens=3` 个候选 token，配合 `cudagraph_mode: FULL_DECODE_ONLY` 在 Decode 阶段使用 CUDA Graph 加速。
- **专家并行**：DeepSeek-V3/V3.1 属 MoE 架构，启用 `--enable-expert-parallel` 后配合 `--tensor-parallel-size 8` 在 8 卡上分配专家；`multistream_overlap_shared_expert` 用于共享专家多流重叠计算。
- **关于数据流、性能数据、benchmark 数字**：原文此节在本次提供的截断片段中未出现具体吞吐/精度数字，故不臆造。

---

## 【表格解读】

**原文无表格**。该文档以代码块（shell 命令）、列表与内嵌选项卡（`===` 分支）形式组织，未提供任何 markdown 表格形式的参数表、性能对比或配置矩阵。

---

## 【公式解读】

**原文无公式**。文档全文未出现 LaTeX 或伪代码形式的数学公式，所有推理机制均通过自然语言与命令行参数描述。

---

## 【关联】

- **支持特性矩阵** → 指向 `../../user_guide/support_matrix/supported_models.md`，用于查询该模型具体支持的 feature 列表。
- **特性配置指南** → 指向 `../../user_guide/feature_guide/index.md`，进一步说明各 feature 如何启用。
- **安装总入口** → `../../getting_started/installation.md` 涵盖源码安装流程；其子锚点 `installation-multi-node-interconnect` 对应本文 3.2 节的"多节点通信验证"；`installation-prebuilt-image` 对应本文 4.1 节的"Docker 镜像安装"。
- **PD 分离多节点特性** → `../features/pd_disaggregation_mooncake_multi_node.md`，与 DeepSeek-V3.1 在多节点 Prefill-Decode 分离部署场景相关（由内部链接推断）。
- **常见问题** → `../../faqs.md`（文中多次引用），用于排查部署中的典型问题。
- **精度/性能评测** → `../../developer_guide/evaluation/using_ais_bench.md`，与文档开篇承诺的"accuracy and performance evaluation"章节对接（截断片段未给出该章节正文）。

---

## 【使用方法】

**原文给出的启用方式与配置项如下**（截断片段范围内）：

### A. 镜像选择

| 硬件 | 镜像 | 镜像 tag |
|------|------|----------|
| Ascend 950DT | `quay.io/ascend/vllm-ascend` | `{{vllm_ascend_version}}` |
| A3 系列 | `quay.io/ascend/vllm-ascend` | `{{ vllm_ascend_version }}-a3` |
| A2 系列 | `quay.io/ascend/vllm-ascend` | `{{ vllm_ascend_version }}` |

### B. 容器启动关键选项（原文逐字保留示例，详见 §技术要点 4）

- `--shm-size=1g`、`--net=host`、`--privileged=true`（A3/A2）；
- `--device /dev/davinci{0..N}` 视系列挂载 8 或 16 卡；
- 关键卷映射：`/root/.cache:/root/.cache`（权重共享）、`/usr/local/Ascend/driver` 等驱动路径、`/usr/local/dcmi`、`/usr/local/bin/npu-smi`。

### C. 在线服务部署关键参数（以 950DT 单节点为例）

| 参数 | 取值（原文） | 作用 |
|------|-------------|------|
| `--max_model_len` | `135168` | 最大序列长度 |
| `--max-num-batched-tokens` | `16384` | 每 batch token 数上限 |
| `--served-model-name` | `deepseek_v3` | 服务化模型名 |
| `--gpu-memory-utilization` | `0.9` | NPU 显存利用率 |
| `--tensor-parallel-size` | `8` | TP=8 |
| `--data-parallel-size` | `1` | DP=1 |
| `--enable-expert-parallel` | 启用 | 专家并行 |
| `--max-num-seqs` | `96` | 并发序列数上限 |
| `--no-enable-prefix-caching` | 禁用 | 关闭前缀缓存 |
| `--quantization` | `ascend` | 使用 Ascend 量化方案 |
| `compilation-config` | `{"cudagraph_mode": "FULL_DECODE_ONLY"}` | Decode 阶段 CUDA Graph |
| `speculative-config` | `{"num_speculative_tokens": 3, "method": "deepseek_mtp"}` | MTP 投机解码 |
| `additional_config` | `enable_cpu_binding / multistream_overlap_shared_expert / enable_balance_scheduling / enable_mlapo` | CPU 绑核、共享专家重叠、负载均衡调度、MLAPO 优化 |

### D. 环境变量

`HCCL_BUFFSIZE=512`、`HCCL_CONNECT_TIMEOUT=600`、`HCCL_EXEC_TIMEOUT=600`、`OMP_PROC_BIND=false`、`OMP_NUM_THREADS=10`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`、`TASK_QUEUE_ENABLE=1`；A3 系列额外 `HCCL_OP_EXPANSION_MODE="AIV"`、`HCCL_IF_IP=$local_ip`、`GLOO_SOCKET_IFNAME=$nic_name`。

### E. 未涉及部分

> ⚠️ **原文截断说明**：本文给出的原文片段在"A3 系列 Startup Command"块的 `exp` 处被截断，因此 A3 / A2 系列完整的 `vllm serve` 启动命令、多节点部署（`#5-online-service-deployment` 锚点暗示的多节点章节）、离线推理、精度与性能评测（`using_ais_bench`）章节的具体步骤 **在本次输入中未提供**。如需完整使用方法，请以仓库源文件或上游文档为准。
