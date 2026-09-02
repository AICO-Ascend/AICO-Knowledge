# Qwen3-30B-A3B

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3-30B-A3B.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-30B-A3B.md

# Qwen3-30B-A3B 文档深度解读

## 【定位】

本文是 vllm-ascend 项目中针对 **Qwen3-30B-A3B MoE 模型** 在 Ascend NPU 上的部署与验证指南，覆盖模型特性、权重视化、Docker/源码安装、混合量化策略与单节点在线部署的端到端流程，作为该模型在 vLLM-Ascend 上首版本（v0.8.4rc2）启用、复现与扩展的官方操作手册。

---

## 【技术要点】

1. **模型架构与参数规模**：Qwen3-30B-A3B 为稀疏 MoE 架构，总参数量 **30.5B**，每个 token 激活参数量 **3.3B**；首批支持版本为 **vLLM-Ascend v0.8.4rc2**，本文以 **v0.22.1rc** 验证，**v0.22.1rc 及之后版本均可稳定运行**。
2. **硬件配置与卡数建议**：
   - **Atlas 800I A3**：64GB，**1~2 卡**
   - **Atlas 800I A2**：64GB，**2~4 卡**
   - **Atlas 300I DUO**：W8A8 量化版本走 **TP2**
3. **三种官方 Docker 镜像**（以模板变量 `{{ vllm_ascend_version }}` 占位）：
   - A3：`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3`
   - A2：`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`
   - Atlas 300I DUO：`quay.io:ascend/vllm-ascend:{{ vllm_ascend_version }}-310p`
4. **A3 硬件拓扑**：**8 个 NPU + 双 die 设计，共 16 颗芯片，对应 `/dev/davinci[0-15]`**；共享机器上可只映射所需子集（如 `/dev/davinci[0-7]` 对应 NPU 0-3）。
5. **W8A8 混合量化策略（按模型结构顺序）**：
   - Embedding 层：**BF16**
   - Q/K 归一化（q_norm, k_norm）：**BF16**
   - 注意力投影（q/k/v/o_proj）：**Static W8A8**，采用**预计算的 per-tensor scale**
   - MoE 路由门（mlp.gate）：**BF16**
   - MoE 专家投影（gate/up/down_proj）：**Dynamic W8A8**，**输入 scale 在推理时按需计算**
6. **容器默认工作目录**为 `/workspace`，vLLM 与 vLLM-Ascend 作为 site-packages 中的 Python 包安装；Atlas 300I DUO 源码安装后**必须卸载** `triton-ascend` 与 `triton`，否则与 vLLM-Ascend 冲突。

---

## 【关键机制与数据】

- **稀疏激活原理**（原文）："sparse MoE architecture enables efficient training and inference, delivering strong performance across reasoning, instruction-following, and agent capabilities while maintaining lower computational cost compared to dense models of similar capability." 即以 3.3B 激活参数量达成接近更大 dense 模型的能力，同时降低算力开销。
- **W8A8 量化分层的工程意义**（原文）：Embedding 与归一化层以 BF16 保留以维持数值精度与训练分布一致性；注意力投影使用**静态 per-tensor scale**避免推理中重复计算；MoE 专家层使用**动态 scale**是为适应不同 token 在不同专家上的输入分布差异。
- **版本兼容承诺**（原文）："The Qwen3-30B-A3B model is first supported in v0.8.4rc2. This document is validated and written based on **vLLM-Ascend v0.22.1rc**. All **v0.22.1rc and later versions** can run stably."
- **多节点部署约束**（原文）："If deploying a multi-node environment, set up the environment on each node."（每个节点均需独立准备环境）
- **卡数说明**（原文）："These are the recommended numbers of cards, which can be adjusted according to the actual situation."

> 注：原文第 5 节"Online Service Deployment"在 "For the Qwen3-30B-A3B MoE model, Expe…"处截断，**部署启动命令、性能数据等未在给出片段中呈现**，故下文"使用方法"仅基于已展示部分整理。

---

## 【表格解读】

### 原文表格 1：模型变体清单（Section 3.1）

| Model | Hardware Requirement | Download |
| --- | --- | --- |
| Qwen3-30B-A3B (BF16) | Atlas 800I A3 (64GB, 1~2 cards)<br>Atlas 800I A2 (64GB, 2~4 cards) | [Download](https://www.modelscope.cn/models/Qwen/Qwen3-30B-A3B) |
| Qwen3-30B-A3B-W8A8 | Atlas 800I A3 (64GB, 1~2 cards)<br>Atlas 800I A2 (64GB, 2~4 cards) | [Download](https://www.modelscope.cn/models/Eco-Tech/Qwen3-30B-A3B-w8a8) |
| Eagle3 Draft Model | NA | [Download](https://www.modelscope.cn/models/Eco-Tech/Qwen3-30B-A3B-w8a8-QuaRot-310) |

**逐行解读**：
- **Qwen3-30B-A3B (BF16)**：原生 BF16 精度版，可在 A3（1~2 卡）或 A2（2~4 卡）上运行；用于精度优先场景及量化基线。
- **Qwen3-30B-A3B-W8A8**：W8A8 量化版，硬件需求与 BF16 相同但计算量更低；下载链接指向 Eco-Tech 的 ModelScope 仓库。
- **Eagle3 Draft Model**：作为推测解码（speculative decoding）的 draft 模型存在，原文标注 Hardware Requirement 为 **NA**（即非必要硬件前提），其权重也来自 `Qwen3-30B-A3B-w8a8-QuaRot-310` 仓库。

### 原文表格 2：Atlas 300I DUO 量化版本（Section 3.1）

| Model | Quantization | Hardware Requirement | Download |
| --- | --- | --- | --- |
| Qwen3-30B-A3B-w8a8-QuaRot-310 | W8A8 | Atlas 300I DUO (TP2) | [Download](https://www.modelscope.cn/models/Eco-Tech/Qwen3-30B-A3B-w8a8-QuaRot-310) |

**逐行解读**：
- **Qwen3-30B-A3B-w8a8-QuaRot-310**：专为 Atlas 300I DUO 准备的 W8A8 量化版，**必须以 Tensor Parallel 2（TP2）** 方式部署；该权重同样在 Eagle3 Draft Model 表格中作为 draft 模型来源被引用，体现了量化 + 推测解码联合优化的思路。

---

## 【公式解读】

原文无公式。

（原文仅以自然语言描述了量化策略与硬件拓扑，未出现任何数学表达式或伪代码公式。）

---

## 【关联】

依据文末提供的内部链接，本文处在 vllm-ascend 文档树的以下上下文位置：

- **模型支持矩阵**（`../../user_guide/support_matrix/supported_models.md`）：向上承接"Section 2 Supported Features"，说明 Qwen3-30B-A3B 在整体支持列表中的状态位。
- **特性指南入口**（`../../user_guide/feature_guide/index.md`）：与上同章节指向，作为特性配置的索引页。
- **量化指南**（`../../user_guide/feature_guide/quantization.md`）：直接呼应 Section 3 的 W8A8 混合量化讨论 —— 文中明确"若直接下载不到 W8A8 权重，可基于 BF16 用 **msmodelslim** 自行量化"，故该链接是量化流程的下游操作手册。
- **安装指南**（`../../getting_started/installation.md`）：Section 4 末尾指向，承载 Docker 与源码两种安装路径的更完整说明（本文中仅展示了针对 MoE 的精简版本）。
- **环境变量与额外配置**（`../../user_guide/configuration/env_vars.md`、`../../user_guide/configuration/additional_config.md`）：在 Section 5（截断部分）预计会引用，结合常见 vLLM-Ascend 部署实践，这些文档承载 TP、cache、quantization 等开关的详细定义。
- **四套评测工具**（`../../developer_guide/evaluation/using_ais_bench.md`、`using_lm_eval.md`、`using_opencompass.md`、`using_evalscope.md`）：对应文末"accuracy and performance evaluation"承诺的具体实现路径，分别为 AIS Bench、lm-evaluation-harness、OpenCompass、EvalScope 四种评测框架的使用方式。

整体上下游关系可概括为：**安装（Installation）→ 部署（Online Service Deployment，Section 5）→ 评测（Evaluation，Section 6/7 未在给出片段中呈现）**，并以特性矩阵与配置文档为横向支撑。

---

## 【使用方法】

> 以下仅基于原文 Section 4 安装与 Section 3.1 权重视化部分整理；Section 5 的部署启动命令因原文截断未给出，故启动参数不再臆造。

### 1. 准备模型权重
- 推荐将权重下载到**所有节点可访问的共享目录**。
- 三种变体 / 量化版本按上表选择，链接均指向 ModelScope。
- 若 W8A8 权重无法直接下载，可参考 [Quantization Guide](../../user_guide/feature_guide/quantization.md) 使用 **msmodelslim** 从 BF16 量化得到。

### 2. Docker 镜像安装（官方 all-in-one）
按硬件选择对应镜像与设备映射：

| 硬件 | 镜像 tag 模板 | NPU 设备映射 |
| --- | --- | --- |
| Atlas 800I A3 | `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3` | `/dev/davinci[0-15]`（16 chips） |
| Atlas 800I A2 | `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}` | `/dev/davinci[0-7]` |
| Atlas 300I DUO | `quay.io:ascend/vllm-ascend:{{ vllm_ascend_version }}-310p` | `/dev/davinci0` |

并按原文挂载 `/usr/local/Ascend/driver`、`/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/etc/ascend_install.info`、`/usr/local/sbin`（310P 多了 `hccn_tool`、`lib64/`、`version.info` 与 `/root/.cache`）。

### 3. 源码安装（备选路径）
```bash
git clone https://github.com/vllm-project/vllm.git && cd vllm && pip install -e .
git clone https://github.com/vllm-project/vllm-ascend.git && cd vllm-ascend && pip install -e .
```
并在 **Atlas 300I DUO 上额外执行**：
```bash
pip uninstall -y triton-ascend triton
```

### 4. 安装验证
```bash
docker ps | grep vllm-ascend-env     # Docker 方式
pip show vllm-ascend                 # 容器内版本确认
pip show vllm vllm-ascend            # 源码方式
```
预期：容器状态为 `Up`，或两个包的版本信息正常显示。

### 5. 部署与评测（原文未涉及具体命令）
- **单节点在线部署**：原文 Section 5.1 标题及导语存在，但具体启动命令在给定片段中截断于"For the Qwen3-30B-A3B MoE model, Expe…"，故不在此臆造；按惯例会引用 [env_vars.md](../../user_guide/configuration/env_vars.md) 与 [additional_config.md](../../user_guide/configuration/additional_config.md) 进行 TP/量化等开关配置。
- **评测框架**：原文未在给出片段中给出评测命令，但通过文末链接可对应到 AIS Bench、lm-evaluation-harness、OpenCompass、EvalScope 四个使用指南。
