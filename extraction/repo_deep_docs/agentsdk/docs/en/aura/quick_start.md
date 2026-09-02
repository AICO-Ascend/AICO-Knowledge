# Quick Start<a name="ZH-CN_TOPIC_0000002459355024"></a>

> 仓 `agentsdk` · 路径 `docs/en/aura/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agentsdk/docs/en/aura/quick_start.md

```markdown
# 深度解读：docs/en/aura/quick_start.md

## 【定位】
本篇是 AgentSDK（Agent SDK）的入门 Quick Start 指南，描述如何通过 `agentic_rl` 命令完成"模型转换 → 数据集准备 → 启动训练"的最小上手路径。

## 【技术要点】
1. **入口命令**：Agent SDK 通过 `agentic_rl` 命令对外暴露训练能力。
2. **模型转换工具**：基于 `/home/third-party/MindSpeed-LLM` 下的 `convert_ckpt.py`，将 HuggingFace 格式的模型权重转为 Megatron-core（mcore）格式。
3. **转换关键参数**（原文命令中字面保留）：`--use-mcore-models`、`--model-type GPT`、`--load-model-type hf`、`--save-model-type mg`、`--target-tensor-parallel-size 4`、`--target-pipeline-parallel-size 1`、`--add-qkv-bias`、`--params-dtype bf16`、`--model-type-hf llama2`；权重输入路径示例 `/home/models/Qwen2.5-7B-Instruct/`，输出路径 `/home/models/Qwen2.5-7B-Instruct-mcore/`，tokenizer 指向该模型目录下的 `tokenizer.json`。
4. **数据集**：下载自 `huggingface.co/datasets/agentica-org/DeepScaleR-Preview-Dataset/resolve/main/deepscaler.json`，解压至 `/home/datasets/deepscalar/`。
5. **训练启动**：在 `/home/work-dir` 下执行 `agentic_rl --config-path /home/agent-7.3.0/configs/agent-parameters.yaml`；配置路径需根据实际安装位置调整。
6. **多节点分布式**：需先启动 Ray 集群——Master 节点形如 `ray start --head --port {ray_port} --dashboard-host={master_ip} --node-ip-address={current_ip} --dashboard-port={dashboard_port} --resources='{"NPU": {npus_per_node}}'`，Worker 节点形如 `ray start --address={master_ip}:{ray_port} --node-ip-address={current_ip} --resources='{"NPU": {npus_per_node}}'`。

> 路径与权限（原文 NOTE 直译要点）：
> - 模型权重路径、Agent SDK 安装路径及其所有文件的属主须与运行用户一致；
> - 路径不得为符号链接；
> - 必须为本地**绝对路径**；
> - 目录权限 `750`，文件权限 `640`；
> - 模型须来自可信源且未被篡改，未经转换/数据未处理即训练可能在 `torch.load` 阶段出现序列化问题。

## 【关键机制与数据】
- **工作原理（原文）**：用户先准备 mcore 格式权重与预处理后的数据集，再以 `agentic_rl` 加载 YAML 配置驱动训练；多节点场景则由 Ray 负责集群编排，NPU 资源通过 `--resources '{"NPU": {npus_per_node}}'` 向 Ray 声明。
- **数据流（原文）**：`Qwen2.5-7B-Instruct` (HF) → `convert_ckpt.py` → `Qwen2.5-7B-Instruct-mcore` (mg, TP=4 / PP=1, bf16, 含 qkv-bias)；同时把 `deepscaler.json` 下载到 `/home/datasets/deepscalar/` 作为训练数据；两者就绪后由 `agentic_rl` 拉起训练任务。
- **性能数据**：原文未给出任何性能/吞吐/精度数值，**无原文性能指标**。

## 【表格解读】
原文无表格（全部以 shell 代码块与说明文字形式给出，故无 markdown 表格可还原）。

## 【公式解读】
原文无公式（无 LaTeX 或伪代码形式的数学表达式，故无公式可还原）。

## 【关联】
- **Environment Preparation →** [`installation_guide.md#installation-and-deployment`](installation_guide.md#installation-and-deployment)：本指南的环境准备小节直接依赖该文档完成 SDK 与依赖安装。
- **Follow-up Procedure → Agent 用法示例：** [`user_guide/user_guide.md`](user_guide/user_guide.md)，用于在完成首次训练后继续查阅 Agent 使用范例。
- **Follow-up Procedure → 后端/模型兼容列表：** 文档中提到的 `[Supported Inference Backends]`、`[Supported Training Backends]`、`[Supported Models]` 三处引用，原文仅给出占位符文本，未提供具体链接。
- **上游组件依赖：** `MindSpeed-LLM` 的 `convert_ckpt.py`（位于 `/home/third-party/MindSpeed-LLM`）以及 Ray（多节点编排）属于隐含调用上游。
- **数据来源：** Hugging Face 上的 `agentica-org/DeepScaleR-Preview-Dataset`。

## 【使用方法】
**启用方式（原文命令层面）**
- 环境准备：依 `installation_guide.md#installation-and-deployment` 安装 Agent SDK。
- 模型转换：cd 至 `/home/third-party/MindSpeed-LLM`，执行 `convert_ckpt.py`，按上文关键参数传入 `--load-dir` / `--save-dir` / `--tokenizer-model`。
- 数据集准备：`mkdir -p /home/datasets/deepscalar/` 后 `wget` 下载 `deepscaler.json`。
- 启动训练：cd `/home/work-dir`，多节点先启 Ray（Master `ray start --head …` + Worker `ray start --address=…`），再运行
  ```bash
  agentic_rl --config-path /home/agent-7.3.0/configs/agent-parameters.yaml
  ```

**配置项（原文明确出现的位置变量，原文未给出 YAML schema）**
- 唯一被显式传入的 CLI 配置：`--config-path /home/agent-7.3.0/configs/agent-parameters.yaml`。
- Ray 端可调占位符：`{ray_port}`、`{master_ip}`、`{current_ip}`、`{dashboard_port}`、`{npus_per_node}`。

**前置/边界约束（原文 NOTE 明示）**
属主一致性 · 禁符号链接 · 必须本地绝对路径 · 目录 `750` / 文件 `640` · 模型可信且已完成转换与数据预处理。
```
