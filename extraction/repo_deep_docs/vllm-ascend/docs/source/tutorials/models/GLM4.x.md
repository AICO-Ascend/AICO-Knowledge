# GLM-4.5/4.6/4.7

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/GLM4.x.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/GLM4.x.md

# GLM-4.5/4.6/4.7 文档深度解读

> 说明：原文在 "Node 1" 多节点部署脚本处被截断（以 `export VLLM` 结尾，未给出完整命令与后续章节如 "Accuracy Evaluation" / "Performance Evaluation" 等内容）。以下解读仅基于原文实际出现的字段。

---

## 【定位】

这篇文档是 vllm-ascend 针对 GLM-4.5/4.6/4.7（MoE 架构、面向 agent 场景的基础模型）在 Ascend NPU 平台上从环境准备、镜像/源码安装，到单节点/多节点 vLLM 在线服务部署（quantization + MTP speculative decoding + expert parallel + data parallel）的端到端部署验证指南。

---

## 【技术要点】

1. **首次支持版本**：`vllm-ascend:v0.10.0rc1` 是首个引入 GLM-4.5 支持的镜像版本。
2. **支持的三类模型权重**：
   - **BF16 全精度版**：`GLM-4.5`、`GLM-4.6`、`GLM-4.7`（来自 ModelScope 的 ZhipuAI 仓库）。
   - **W8A8 量化 + float MTP（多 token 预测）版**：`GLM-4.5-w8a8-with-float-mtp`、`GLM-4.7-w8a8-with-float-mtp`。
   - **W8A8 量化（不带 MTP）版**：`GLM-4.6-w8a8`——文档原文解释："Because vllm does not support GLM4.6 mtp in October, we do not provide an mtp version. Since it is now supported, you can use the following quantization scheme to add mtp weights to the quantized weights."。
3. **硬件最小部署单元**：量化版 `glm4.7_w8a8_with_float_mtp` 可部署于 **1 台 Atlas 800 A3 (64GB × 16) 或 1 台 Atlas 800 A2 (64GB × 8)**；低延迟场景推荐单机部署。
4. **并行策略组合**：单节点使用 `--data-parallel-size 2 --tensor-parallel-size 8 --enable-expert-parallel`（DP×TP×EP 三轴并行）。
5. **推测解码（MTP）配置**：`--speculative-config '{"num_speculative_tokens": 3, "method":"mtp", "enforce_eager":true}'`（每步猜 3 个 token，强制 eager 模式）。
7. **CUDA Graph 与编译配置**：`--compilation-config '{"cudagraph_capture_sizes": [1,2,4,8,16,32,64,128,256,512], "cudagraph_mode": "FULL_DECODE_ONLY"}'`——只在 decode 阶段捕获 CUDA Graph。
6. **关键 NPU/HCCL 环境变量**：`HCCL_BUFFSIZE=512`、`HCCL_OP_EXPANSION_MODE=AIV`、`VLLM_ASCEND_ENABLE_TOPK_OPTIMIZE=1`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`、`OMP_PROC_BIND=false`、`OMP_NUM_THREADS=1`。
8. **多节点扩展点（相对单节点多出）**：双节点各起一份 vllm serve，使用 `--data-parallel-size 2 --data-parallel-size-local 1 --data-parallel-start-rank {0,1} --data-parallel-address $local_ip --data-parallel-rpc-port 13389 --host 0.0.0.0 --port 8004`，并启用 `--enable-auto-tool-choice --reasoning-parser glm45 --tool-call-parser glm47`（用于 agent 工具调用与 GLM-4.5 风格的 reasoning 解析）；`--max-model-len 140000`（多节点略高于单节点的 133000）。
9. **Ascend 特有融合算子开关**：`--additional-config '{"enable_shared_expert_dp":true,"ascend_fusion_config":{"fusion_ops_gmmswigluquant":false},"scheduler_config":{"enable_balance_scheduling":true}}'`；文档明确指出 `fusion_ops_gmmswigluquant` 算子在 NPU 总数 ≤ 16 时性能会退化，因此默认关闭。

---

## 【关键机制与数据】

### 数据流 / 部署拓扑（原文有的才写）

- **模型加载路径**：文档示例命令 `vllm serve Eco-Tech/GLM-4.7-W8A8-floatmtp` 表明模型从 HuggingFace Hub 或镜像仓库直接拉取；推荐将权重缓存到共享目录 `/root/.cache/`（原文："It is recommended to download the model weight to the shared directory of multiple nodes, such as `/root/.cache/`."），以便多节点共享。
- **Docker 设备映射**：
  - **A3 系列**：显式 `--device /dev/davinci0` … `/dev/davinci15`（即 16 张 NPU），再加 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`。
  - **A2 系列**：显式 `--device /dev/davinci0` … `/dev/davinci7`（即 8 张 NPU），管理/驱动设备相同。
  - 两个镜像都挂载 `/usr/local/dcmi`、`/usr/local/Ascend/driver/...`、`/usr/local/bin/npu-smi`、`/etc/ascend_install.info` 与 `/root/.cache`，以保证驱动、工具链与权重可见。
- **多节点通信**：通过 `HCCL_IF_IP=$local_ip`、`GLOO_SOCKET_IFNAME`、`TP_SOCKET_IFNAME`、`HCCL_SOCKET_IFNAME` 四个环境变量绑定本节点 IP 与网卡，`nic_name` 由 `ifconfig` 获取；Node 1 的 `node0_ip` 与 Node 0 的 `local_ip` 相同（原文："same as the local_IP address in node 0"），用于跨节点汇聚。
- **DP-RPC 端口**：多节点使用 `--data-parallel-rpc-port 13389`。
- **关键参数**：
  - 单节点 `--max-model-len 133000`；多节点 `--max-model-len 140000`；二者均 `--max-num-batched-tokens 8192`、`--max-num-seqs 16`、`--gpu-memory-utilization 0.9`、`--seed 1024`。

### 性能 / 限制说明（原文）

- **量化算子经验法则（原文）**："`fusion_ops_gmmswigluquant` The performance of the GmmSwigluQuant fusion operator tends to degrade when the total number of NPUs is ≤ 16."
- **多节点提示（原文）**："While the previous documentation advises against multi-node deployment on the Atlas 800 A2 (64GB × 8) platform, this configuration can still be implemented for the GLM-4.x model if required." 即双节点仍可用，但作者建议在 A2 上单机部署。

> 原文未给出吞吐量、时延、token/s、显存占用等具体数字性能表格，本节不杜撰。

---

## 【表格解读】

**原文无表格**。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

文档通过以下内部链接将 GLM-4.x 接入到 vllm-ascend 的整体生态：

| 链接 | 在文档中出现的位置 | 关系 / 上下游 |
|------|------------------|--------------|
| `../../user_guide/support_matrix/supported_models.md` | Section 2 "Supported Features" | 上游：**模型支持矩阵**——明确 GLM-4.5/4.6/4.7 在特性维度（如 MTP、量化、expert parallel）是否受支持。 |
| `../../user_guide/feature_guide/index.md` | Section 2 "Supported Features" | 配套：**特性配置指南**——给出各特性（如 expert parallel、MTP、Ascend 融合算子、CUDA Graph）的开启/调优方式。 |
| `../../getting_started/installation.md` | Section 4.2 "Source Code Installation" | 替代路径：**源码安装 vllm-ascend**——在不想用 Docker 镜像时的依赖与构建流程。 |
| `../../developer_guide/evaluation/using_ais_bench.md` | 文末元信息列出，文档 Section 1 已声明会讲 "accuracy and performance evaluation"，但正文被截断未展开 | 下游：**精度评测**——使用 AIS Benchmark 评估 GLM-4.x 部署的精度。 |
| `../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation` | 文末元信息列出，同上 | 下游：**性能评测**——AIS Benchmark 下的吞吐/时延性能测试入口。 |

另含两条**外部权重/工具链接**（原文 Section 3.1）：
- ModelScope 上的 ZhipuAI/GLM-4.5、ZhipuAI/GLM-4.6、ZhipuAI/GLM-4.7（BF16）。
- Modelers 上的 Modelers_Park/GLM-4.5-w8a8、Modelers_Park/GLM-4.6-w8a8；ModelScope 上的 Eco-Tech/GLM-4.7-W8A8-floatmtp（量化版）。
- GitCode 上的 Ascend-SACT/GLM-4.5-w8a8（量化方案）。

---

## 【使用方法】

> 启用步骤汇总自原文 Section 3–5。

### 1. 下载权重
```text
# 任选一种，建议放入 /root/.cache/ 作为多节点共享目录
GLM-4.5 (BF16):     https://www.modelscope.cn/models/ZhipuAI/GLM-4.5
GLM-4.6 (BF16):     https://www.modelscope.cn/models/ZhipuAI/GLM-4.6
GLM-4.7 (BF16):     https://www.modelscope.cn/models/ZhipuAI/GLM-4.7
GLM-4.5-w8a8-mtp:   https://modelers.cn/models/Modelers_Park/GLM-4.5-w8a8
GLM-4.6-w8a8:       https://modelers.cn/models/Modelers_Park/GLM-4.6-w8a8
GLM-4.7-w8a8-mtp:   https://www.modelscope.cn/models/Eco-Tech/GLM-4.7-W8A8-floatmtp
量化方案:           https://ai.gitcode.com/Ascend-SACT/GLM-4.5-w8a8
```

### 2. 启动 Docker 镜像（A2 / A3 二选一）
- **A3 (16 卡)**：`export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3`，按原文 docker run 模板映射 `/dev/davinci0`…`/dev/davinci15` 及管理设备。
- **A2 (8 卡)**：`export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`，映射 `/dev/davinci0`…`/dev/davinci7`。
- **源码安装替代**：参考 `../../getting_started/installation.md`，多节点需在每台机器上各做一遍。

### 3. 单节点启动 vLLM 在线服务（原文 Section 5.1）
```shell
export HCCL_BUFFSIZE=512
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=1
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export HCCL_OP_EXPANSION_MODE=AIV
export VLLM_ASCEND_ENABLE_TOPK_OPTIMIZE=1

vllm serve Eco-Tech/GLM-4.7-W8A8-floatmtp \
  --data-parallel-size 2 \
  --tensor-parallel-size 8 \
  --enable-expert-parallel \
  --seed 1024 \
  --served-model-name glm \
  --max-model-len 133000 \
  --max-num-batched-tokens 8192 \
  --max-num-seqs 16 \
  --quantization ascend \
  --trust-remote-code \
  --gpu-memory-utilization 0.9 \
  --speculative-config '{"num_speculative_tokens": 3, "method":"mtp", "enforce_eager":true}' \
  --compilation-config '{"cudagraph_capture_sizes": [1,2,4,8,16,32,64,128,256,512], "cudagraph_mode": "FULL_DECODE_ONLY"}' \
  --additional-config '{"enable_shared_expert_dp":true,"ascend_fusion_config":{"fusion_ops_gmmswigluquant":false},"scheduler_config":{"enable_balance_scheduling":true}}'
```

### 4. 多节点（双节点）启动（原文 Section 5.2，Node 0 脚本已给出完整版；Node 1 脚本被截断，仅给出以下公共变量与差异项）
**两节点共同设置的环境变量**（`local_ip` / `nic_name` 通过 ifconfig 获取）：
```shell
export HCCL_IF_IP=$local_ip
export GLOO_SOCKET_IFNAME=$nic_name
export TP_SOCKET_IFNAME=$nic_name
export HCCL_SOCKET_IFNAME=$nic_name
export HCCL_BUFFSIZE=512
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=1
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export HCCL_OP_EXPANSION_MODE=AIV
export VLLM_ASCEND_ENABLE_TOPK_OPTIMIZE=1
```

**Node 0 关键参数**（原文给出）：
- `--host 0.0.0.0 --port 8004`
- `--data-parallel-size 2 --data-parallel-size-local 1 --data-parallel-start-rank 0`
- `--data-parallel-address $local_ip --data-parallel-rpc-port 13389`
- `--tensor-parallel-size 8 --enable-expert-parallel`
- `--max-model-len 140000 --max-num-batched-tokens 8192 --max-num-seqs 16`
- `--quantization ascend --trust-remote-code --gpu-memory-utilization 0.9`
- `--enable-auto-tool-choice --reasoning-parser glm45 --tool-call-parser glm47`
- `--served-model-name glm47`
- MTP / compilation / additional-config 三项与单节点相同。

**Node 1 的差异项（原文被截断，未给出 `--data-parallel-start-rank`、端口等具体取值；建议以镜像对称结构补全）**：Node 1 需额外设置 `node0_ip="xxxx"` 并与 Node 0 的 `local_ip` 一致。

### 5. 后续步骤（原文声明但因截断未展开）
- **精度评估** → 见 `../../developer_guide/evaluation/using_ais_bench.md`。
- **性能评估** → 见 `../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation`。

> **配置项小结**：模型选择（HuggingFace/ModelScope 仓库名）、`--quantization ascend`（W8A8）、`--enable-expert-parallel`、`--speculative-config.method=mtp`、`--additional-config.enable_shared_expert_dp`、`--additional-config.ascend_fusion_config.fusion_ops_gmmswigluquant`（NPU ≤16 时置 `false`）、`--additional-config.scheduler_config.enable_balance_scheduling`、`--compilation-config.cudagraph_mode=FULL_DECODE_ONLY`、环境变量 `HCCL_OP_EXPANSION_MODE=AIV` 与 `VLLM_ASCEND_ENABLE_TOPK_OPTIMIZE=1` 是与 Ascend NPU + GLM MoE 强相关的开关。
