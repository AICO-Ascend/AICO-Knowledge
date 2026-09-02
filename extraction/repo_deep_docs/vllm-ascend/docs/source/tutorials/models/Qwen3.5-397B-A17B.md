# Qwen3.5-397B-A17B

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3.5-397B-A17B.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3.5-397B-A17B.md

# Qwen3.5-397B-A17B 部署文档深度解读

## 【定位】
这篇文档是 vllm-ascend 项目中针对 **Qwen3.5-397B-A17B** 大规模 MoE 模型在 Ascend 硬件上生产级部署的完整 guide，覆盖模型权重选型、硬件拓扑、容器安装、单/多节点部署、PD 分离、功能验证、精度与性能评估、调优及 FAQ，旨在为用户提供从环境准备到上线服务的端到端操作指引。

---

## 【技术要点】

1. **模型定位与首发版本**：Qwen3.5-397B-A17B 是大规模 Qwen3.5 MoE 模型，集成多模态、长上下文、MTP 推测解码、W8A8 量化能力；首次支持版本为 `vllm-ascend:v0.17.0rc1`，Ascend 950DT 需从 `v0.23.0rc1` 起使用。
2. **五种权重形态与硬件拓扑**：
   - BF16 原生版：需 2 × Ascend 950DT(96GB×8) / 2 × Atlas 800 A3(64GB×16) / 4 × Atlas 800 A2(64GB×8)
   - `w8a8` / `w4a8`：1 × A3(64GB×16) 或 2 × A2(64GB×8)
   - `w8a8-mxfp8` / `w4a4-mxfp4`：单节点 Ascend 950DT(96GB×8) 即可（需 `--quantization ascend`）
3. **支持特性矩阵**（原文指向 supported_features.md）：BF16、W8A8 量化、chunked prefill、自动前缀缓存、推测解码、异步调度、张量并行、专家并行、数据并行、PD 分离、ACLGraph。
4. **环境变量调优关键参数**（950DT 单节点部署示例）：
   - `PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`（减少碎片、避免 OOM）
   - `HCCL_OP_EXPANSION_MODE="AIV"`、`HCCL_BUFFSIZE=400`、`HCCL_INTRA_PCIE_ENABLE=1`、`HCCL_INTRA_ROCE_ENABLE=0`
   - `OMP_PROC_BIND=false`、`OMP_NUM_THREADS=100`、`TASK_QUEUE_ENABLE=1`、`VLLM_ASCEND_ENABLE_PREFETCH_MLP=1`
5. **三种硬件的 Docker 启动差异**：
   - 950DT：暴露 `/dev/davinci0`–`/dev/davinci7`（8 卡）+ `davinci_manager` + `hisi_hdc` + `ummu` + `uburma`，挂载 `hixlep/`、`/usr/lib64`
   - A3：暴露 16 卡（davinci0–15），挂载 `hccn_tool`、`driver/lib64/`、`version.info`
   - A2：8 卡，挂载项与 A3 类似但数量减半
6. **部署模式分级**：单节点（Prefill+Decode 同机）适合功能验证与长上下文单集群；多节点适合大模型/多并发；PD 分离用于 Prefill/Decode 解耦的高吞吐场景。

---

## 【关键机制与数据】

### 原文工作机制
- **MTP 推测解码（Multi-Token Prediction）**：文档标题与权重名称（`-mtp` 后缀）均表明该模型在 Ascend 上启用 MTP 推测解码以提升推理吞吐；具体算法参数（草稿 token 数、接受率等）**原文未涉及**。
- **量化路径**：BF16 → W8A8（per-channel/per-tensor 整型量化）→ W4A8 → W8A8-mxfp8 → W4A4-mxfp4，对显存需求依次降低，从 BF16 需 2 节点 950DT 缩减至单节点 950DT 即可承载 w4a4-mxfp4。
- **专家并行（Expert Parallelism）+ 张量并行（Tensor Parallelism）+ 数据并行（Data Parallelism）**：MoE 397B-A17B 必须依赖 EP 才可拆分 17B 激活专家路由，配合 TP/DP 跨节点扩展；具体并行度设置（如 `--tensor-parallel-size`、`--expert-parallel-size` 数值）**原文未给出完整命令**（文档截断）。
- **PD 分离（Prefill-Decode Disaggregation）**：将 Prefill 与 Decode 计算分别调度到不同节点，通过 Mooncake 等传输 KV cache，配合文档链接 `../features/pd_disaggregation_mooncake_multi_node.md` 实现跨节点扩展。

### 原文可观察到的数据点
- 文档发布对应 vllm-ascend 版本基线：v0.17.0rc1 起通用支持，v0.23.0rc1 起支持 Ascend 950DT。
- 硬件显存档位：Ascend 950DT 单卡 96GB；Atlas 800 A3 单卡 64GB；Atlas 800 A2 单卡 64GB。
- 单节点性能参数典型配置项（原文已点名但未给具体推荐值，需用户自调）：`--max-model-len`、`--max-num-seqs`、`--max-num-batched-tokens`。

> 注：原文末尾被截断（`vllm serve` 命令未完整给出后续参数与多节点/PD 章节），具体并行度数值、性能基准 (tokens/s)、精度指标 (e.g. MMLU/GSM8K) 等数据在所提供的片段中**不可见**，本解读严格不臆造。

---

## 【表格解读】

### 原文硬件拓扑对照（按原文 3.1 节内容重构）

| 权重版本 | 量化精度 | 节点数 × 类型 | 单卡显存 | ModelScope 下载链接（原文） |
|---|---|---|---|---|
| Qwen3.5-397B-A17B | BF16 | 2 × Ascend 950DT | 96GB × 8 | modelscope.cn/models/Qwen/Qwen3.5-397B-A17B |
| Qwen3.5-397B-A17B | BF16 | 2 × Atlas 800 A3 | 64GB × 16 | 同上 |
| Qwen3.5-397B-A17B | BF16 | 4 × Atlas 800 A2 | 64GB × 8 | 同上 |
| Qwen3.5-397B-A17B-w8a8 | W8A8 | 1 × Atlas 800 A3 | 64GB × 16 | modelscope.cn/models/Eco-Tech/Qwen3.5-397B-A17B-w8a8-mtp |
| Qwen3.5-397B-A17B-w8a8 | W8A8 | 2 × Atlas 800 A2 | 64GB × 8 | 同上 |
| Qwen3.5-397B-A17B-w4a8 | W4A8 | 1 × Atlas 800 A3 | 64GB × 16 | modelscope.cn/models/Eco-Tech/Qwen3.5-397B-A17B-w4a8-mtp |
| Qwen3.5-397B-A17B-w4a8 | W4A8 | 2 × Atlas 800 A2 | 64GB × 8 | 同上 |
| Qwen3.5-397B-A17B-w8a8-mxfp8 | W8A8 (MXFP8) | 1 × Ascend 950DT | 96GB × 8 | modelscope.cn/models/Eco-Tech/Qwen3.5-397B-A17B-w8a8-mxfp8 |
| Qwen3.5-397B-A17B-w4a4-mxfp4 | W4A4 (MXFP4) | 1 × Ascend 950DT | 96GB × 8 | modelscope.cn/models/Eco-Tech/Qwen3.5-397B-A17B-w4a4-mxfp4 |

**逐行解读**：
- **BF16 行**：397B-A17B 全精度权重需 ~800GB 级显存（粗算 BF16 ≈ 2B/参数 × 397B ≈ 794GB），因此必须跨 2 个 A3 节点（2×16×64GB=2048GB）或 4 个 A2 节点（4×8×64GB=2048GB），留出 KV cache 与激活余量。
- **W8A8 / W4A8 行**：整型量化使权重体积缩为 1/2 或 1/2（w8a8 仍 8bit 权重 + 8bit 激活，体积接近 BF16，但实际部署文中给出节点数减少，说明激活/权重共享优化与 Ascend 量化算子库节省了实际开销），A3 单节点即可部署。
- **w8a8-mxfp8 / w4a4-mxfp4 行**：借助 Ascend 950DT 的 MXFP8/MXFP4 微缩浮点原生支持，单卡 96GB × 8 = 768GB 即可容纳，说明 MX 格式相对 BF16 显著降低显存占用（理论上 MXFP8 ≈ 1/2 BF16，MXFP4 ≈ 1/4），同时保留动态范围，更适合生产级吞吐。

> 说明：上表是**按原文 3.1 节文本逐条复刻**，非新增数据；"量化精度"列按原文权重的 `-w8a8`/`-w4a8`/`-mxfp8`/`-mxfp4` 命名直译，未引入原文未声明的额外位宽换算。

---

## 【公式解读】

**原文无公式**。整篇文档是部署操作型 guide，未出现任何 LaTeX 数学表达式或伪代码公式块；性能/精度数字（如 tps、p99 延迟、loss 等）亦未在所提供的片段中给出。

---

## 【关联】

依据文档内嵌及文末内部链接：

- **特性矩阵源** → [`../../user_guide/support_matrix/supported_features.md`](../../user_guide/support_matrix/supported_features.md)：提供 BF16/W8A8/chunked prefill/自动前缀缓存/推测解码/异步调度/TP/EP/DP/PD 分离/ACLGraph 的支持矩阵，是本文"支持特性"声明的唯一权威依据。
- **特性配置详解** → [`../../user_guide/feature_guide/index.md`](../../user_guide/feature_guide/index.md)：对上述特性的开启/调优做参数级说明，是单节点命令中 `--quantization ascend`、并行度、scheduler 等开关的官方解释页。
- **多节点通信验证** → [`../../getting_started/installation.md#installation-multi-node-interconnect`](../../getting_started/installation.md#installation-multi-node-interconnect)：3.2 节要求部署前按该页验证 HCCL 互联（涉及 `hccl_rootinfo.json` 挂载、AIV/PCIE/ROCE 模式选择）。
- **预置镜像** → [`../../getting_started/installation.md#installation-prebuilt-image`](../../getting_started/installation.md#installation-prebuilt-image)：4.1 节 Docker 启动命令依赖此页基础镜像标签规范（`{{ vllm_ascend_version }}-950DT / -a3 / 默认`）。
- **源码/CANN 安装** → [`../../getting_started/installation.md#installation-existing-cann-install`](../../getting_started/installation.md#installation-existing-cann-install)：4.2 节从源码构建 vllm-ascend 的备选路径。
- **FAQ** → [`../../faqs.md`](../../faqs.md)：覆盖部署常见问题（如版本匹配、HCCL 异常、MTP 启用限制等）。
- **Ray 分布式** → [`../features/ray.md`](../features/ray.md)：多节点部署通常使用 Ray 作为 vllm `distributed-executor-backend`（文档截断的命令行中即出现 `--distributed-executor-ba...`，强烈暗示 Ray 后端）。
- **Mooncake PD 分离** → [`../features/pd_disaggregation_mooncake_multi_node.md`](../features/pd_disaggregation_mooncake_multi_node.md)：跨节点 Prefill-Decode 解耦方案，与本文"PD 分离"章节直接对应。

---

## 【使用方法】

以下命令/配置均**逐字来自原文**（仅截取文档片段中已给出的部分）：

### 1) Docker 启动容器（三选一，按硬件）

**Ascend 950DT：**
```bash
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-950DT
export NAME=vllm-ascend

docker run --rm \
  --name $NAME --net=host --shm-size=1g \
  --device /dev/davinci0 --device /dev/davinci1 --device /dev/davinci2 --device /dev/davinci3 \
  --device /dev/davinci4 --device /dev/davinci5 --device /dev/davinci6 --device /dev/davinci7 \
  --device /dev/davinci_manager --device /dev/hisi_hdc --device /dev/ummu --device /dev/uburma \
  -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  -v /etc/hccl_rootinfo.json:/etc/hccl_rootinfo.json \
  -v /etc/hixlep/:/etc/hixlep/ \
  -v /root/.cache:/root/.cache \
  -v /usr/local/sbin:/usr/local/sbin \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
  -v /usr/local/sbin/npu-smi:/usr/local/sbin/npu-smi \
  -v /usr/lib64:/usr/lib64 \
  -itd $IMAGE bash
```

**Atlas 800 A3：** 暴露 `/dev/davinci0`–`/dev/davinci15`（16 卡）+ `davinci_manager` + `devmm_svm` + `hisi_hdc`，挂载 `hccn_tool`/`driver/lib64/`/`version.info`，镜像 tag 为 `{{ vllm_ascend_version }}-a3`。

**Atlas 800 A2：** 暴露 `/dev/davinci0`–`/dev/davinci7`（8 卡）+ `davinci_manager` + `devmm_svm` + `hisi_hdc`，挂载项同 A3，镜像 tag 为 `{{ vllm_ascend_version }}`（无后缀）。

### 2) 容器内校验
```shell
python -c "import vllm, vllm_ascend; print('vllm and vllm_ascend are ready')"
```

### 3) 950DT 单节点量化部署（原文已给出环境变量+启动模板）
```shell
export VLLM_USE_MODELSCOPE=True
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export HCCL_OP_EXPANSION_MODE="AIV"
export HCCL_BUFFSIZE=400
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=100
export TASK_QUEUE_ENABLE=1
export VLLM_ASCEND_ENABLE_PREFETCH_MLP=1
export HCCL_INTRA_PCIE_ENABLE=1
export HCCL_INTRA_ROCE_ENABLE=0

vllm serve Eco-Tech/Qwen3.5-397B-A17B-w4a4-mxfp4 \
  --host 0.0.0.0 --port 8000 --distributed-executor-ba...
```
（文档在此处被截断，后续 `--tensor-parallel-size`、`--expert-parallel-size`、量化声明 `--quantization ascend`、多节点 head/worker 地址等参数**原文片段未给出**。）

### 4) 权重路径推荐
- 下载到共享目录 `/root/.cache/`，保证所有节点读到同一路径。
- 各版本 ModelScope 链接见上方"表格解读"中列出的官方 URL。

### 5) 调优提示（原文 note）
> "Adjust `--max-model-len`, `--max-num-seqs`, and `--max-num-batched-tokens` based on your service workload and available KV cache."

### 原文未涉及
- 完整的 `vllm serve` 命令行参数（多节点、PD 分离章节的命令）；
- 精度评估脚本（e.g. `lm_eval` 任务、benchmark 分数）；
- 性能压测命令（如 `vllm bench serve` 流量模型与目标 QPS）；
- 健康检查/curl 示例；
- MTP 草稿深度等推测解码参数；
- 故障排查案例（仅留 FAQ 链接指向 `../../faqs.md`）。

> 备注：用户提供的原文片段止于"5.1 Single-Node Online Deployment"中 `vllm serve` 命令行中途，第 6–10 节（多节点部署、PD 分离、功能验证、精度/性能评估、调优、FAQ）正文内容在本次输入中**不可见**，故以上解读严格基于可获得的文字，未对其余章节作任何外推。
