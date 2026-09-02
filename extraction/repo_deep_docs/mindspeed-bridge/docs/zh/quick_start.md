# MindSpeed Bridge 快速入门：Qwen3.5-VL-9B 模型指令微调

> 仓 `mindspeed-bridge` · 路径 `docs/zh/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-bridge/docs/zh/quick_start.md

# MindSpeed Bridge 快速入门（Qwen3.5-VL-9B）深度解读

## 【定位】

这篇文档是「mindspeed-bridge」仓库面向初次接触该框架的开发者，提供的一份**在昇腾 NPU 上完成 Qwen3.5-VL-9B 多模态视觉语言模型（VLM）指令微调（SFT）任务的端到端快速入门指引**，涵盖环境搭建、权重与数据集准备、微调启动三个环节。

---

## 【技术要点】

1. **框架定位与接入方式**：MindSpeed Bridge 是 Megatron-Bridge 在昇腾平台上的**非侵入式适配层**，训练通过 `mindspeed_bridge.scripts.training.run_recipe` 入口**委托**上游 Megatron-Bridge 的 `run_recipe.py` 启动，无需修改上游源码。
2. **硬件适配范围**：支持 Ascend 950 系列产品、Atlas A3 训练系列产品、Atlas A2 训练系列产品（详见 install_guide.md）。
3. **默认并行配置（以 A3 为例）**：`NPUS_PER_NODE=16`、`TP=1`、`PP=16`、`CP=1`、`NNODES=1`、`NODE_RANK=0`、`MASTER_PORT=6015`；Qwen3.5-VL-9B 为 9B 参数**稠密**多模态模型，单卡显存占用较小。
4. **训练超参默认值**：`SEQ_LENGTH=4096`、`TRAIN_ITERS=2000`、`GLOBAL_BATCH_SIZE=16`、`MICRO_BATCH_SIZE=1`、`NUM_LAYERS=32`、`MTP_LAYERS=null`（9B 稠密模型默认关闭 MTP）。
5. **Recipe 与 step_func**：`RECIPE="qwen35_vl_9b_sft_config"`（定义于 `mindspeed_bridge/recipes/qwen_vl/qwen35_vl_9B_sft.py`），`step_func=qwen3_vl_step`。
6. **数据集 provider**：使用 `PreloadedVLMConversationProvider`，加载预加载的多模态对话数据；JSONL 每条数据采用 HuggingFace 多模态 conversation 格式，`content` 中通过 `image` 类型引用图片（路径相对于 `dataset.image_folder`）。
7. **并行约束公式**：`NPUS_PER_NODE × NNODES = TP × PP × DP`；MoE 模型还需满足 `EP ≤ DP`。
8. **环境变量固化**：`HF_PATH`（权重目录绝对路径）、`TRAIN_JSON`（JSONL 数据路径）、`TRAIN_IMAGES`（图片目录）；并需 source `cann/set_env.sh` 与 `nnal/atb/set_env.sh`。

---

## 【关键机制与数据】

**工作原理（训练启动链）**：

1. **入口委托**：用户在节点上执行示例脚本 `qwen35_vl_9b_sft_4k_A3.sh`，脚本内部用 `torchrun --module mindspeed_bridge.scripts.training.run_recipe` 启动，将分布式参数与 CLI 覆盖参数透传至 MindSpeed-Bridge 入口；该入口**再委托**给上游 Megatron-Bridge 的 `run_recipe.py`，从而实现非侵入式接入。
2. **recipe 配置解析**：通过 `--recipe qwen35_vl_9b_sft_config` 选择模型/优化器/数据集/并行策略的预设组合；通过 `--hf_path $HF_PATH` 同时加载 Qwen3.5-VL-9B 的**模型权重 + 文本/视觉 processor**；通过 `--step_func qwen3_vl_step` 指定 Qwen3.5-VL 系列的前向 step 实现。
3. **数据流**：JSONL（多模态对话） → `PreloadedVLMConversationProvider` 解析 `conversation`（或 `{"messages": [...], "images": [...]}` 传统格式，文本中以 `<image>` 占位）→ 按 `dataset.image_folder` 加载图像 → 进入 VLM 训练管线。
4. **多机机制**：各终端分别启动同一脚本，区别仅在 `NODE_RANK`（取值 0 ~ NNODES-1，不能重复），`MASTER_ADDR` 统一指向主节点 IP；多机场景下每个节点都需准备相同权重与数据（或通过 NFS 共享）。
5. **日志与产出**：训练日志写入 `./logs/qwen35_vl_9b_sft_TP${TP}_PP${PP}_CP${CP}_NUM_LAYERS${NUM_LAYERS}.log`，可通过观察 `lm loss` 随迭代次数稳步下降判断训练是否正常；权重默认保存至 `checkpoint.save` 指定路径（示例为 `${WORKSPACE}/results/qwen35_vl_9b_sft_config_sft`）。

**性能与约束（原文给出的明确数据/警告）**：

- 原文：`NPUS_PER_NODE=16` 表示需要 16 个 NPU 参与训练，如果实际低于此配置，可能遇到 OOM 问题。
- 原文：Qwen3.5-VL-9B 为 9B 参数稠密多模态模型，单卡显存占用较小，可适当减小 `NUM_LAYERS`/`TRAIN_ITERS` 或调整 `TP/PP` 先验证环境与流程。
- 原文：`MICRO_BATCH_SIZE` 过大可能导致 OOM。
- 原文：上下文并行算法示例使用 `kvallgather_cp_algo`（参数 `model.context_parallel_algo`）。
- 原文：是否启用 Ascend GDN（Gated Delta Net）AscendC 亲和实现由 `model.use_ascend_gdn` 控制。

---

## 【表格解读】

**表 1：微调脚本参数说明（原文逐字还原）**

| 参数名 | 说明 |
| --- | --- |
| `--hf_path` | HuggingFace 模型 ID 或本地权重路径，同时用于加载模型权重与文本/视觉处理器。 |
| `--recipe` | 指定训练使用的 recipe 配置函数，示例脚本为 `qwen35_vl_9b_sft_config`（定义在 `mindspeed_bridge/recipes/qwen_vl/qwen35_vl_9B_sft.py`）。 |
| `--step_func` | 指定前向 step 函数，Qwen3.5-VL 系列模型使用 `qwen3_vl_step`。 |
| `model.tensor_model_parallel_size` | 张量并行大小。 |
| `model.pipeline_model_parallel_size` | 流水线并行大小。 |
| `model.context_parallel_size` | 上下文并行大小。 |
| `model.context_parallel_algo` | 上下文并行算法，示例脚本使用 `kvallgather_cp_algo`。 |
| `model.num_layers` | 训练的 Transformer 层数，功能验证时建议调小。 |
| `model.mtp_num_layers` | MTP（Multi-Token Prediction）多 token 预测层数。 |
| `model.use_ascend_gdn` | 是否启用 Ascend GDN（Gated Delta Net）AscendC 亲和实现。 |
| `model.seq_length` | 序列长度，需与数据集保持一致。 |
| `dataset.train_data_path` | 多模态对话数据集路径（JSONL）。 |
| `dataset.image_folder` | 多模态数据中的图片目录。 |
| `train.train_iters` | 总训练迭代数。 |
| `train.global_batch_size` | 全局 batch size。 |
| `train.micro_batch_size` | 每个微批次 batch size，过大可能导致 OOM。 |
| `checkpoint.save` | 训练权重保存路径。 |

**逐行解读**：

- **CLI 主入口三参数（`--hf_path` / `--recipe` / `--step_func`）**：构成"权重来源 + 训练配方 + 前向实现"的最小三元组；`--hf_path` 同时承担权重与 processor 加载，使视觉/文本预处理与训练在同一目录可达。
- **并行三件套（TP / PP / CP）**：分别对应 `model.tensor_model_parallel_size`、`model.pipeline_model_parallel_size`、`model.context_parallel_size`；`model.context_parallel_algo=kvallgather_cp_algo` 指明上下文并行采用 KV 全量收集算法。
- **结构与超参（`model.num_layers` / `model.mtp_num_layers` / `model.seq_length`）**：`num_layers` 支持功能验证时调小以快速跑通；`mtp_num_layers` 对稠密模型默认关闭；`seq_length` 需与数据集保持一致（示例为 4096）。
- **昇腾亲和开关（`model.use_ascend_gdn`）**：启用 Ascend GDN（Gated Delta Net）的 AscendC 亲和实现，是 MindSpeed-Bridge 在昇腾侧的性能优化点。
- **数据集三件套（`dataset.train_data_path` / `dataset.image_folder`）**：前者指向 JSONL 路径，后者作为 `content.image` 字段的相对基准目录，二者协同解析多模态样本。
- **训练循环（`train.train_iters` / `train.global_batch_size` / `train.micro_batch_size`）**：示例默认 2000/16/1；`micro_batch_size` 与显存直接相关，过大易 OOM。
- **持久化（`checkpoint.save`）**：决定训练产出权重落盘路径，示例默认写入 `${WORKSPACE}/results/qwen35_vl_9b_sft_config_sft`。

---

## 【公式解读】

原文无数学公式。但文档给出一个**并行卡数约束（伪代码式）**：

```
NPUS_PER_NODE × NNODES = TP × PP × DP
```

- `NPUS_PER_NODE`：单节点使用的 NPU 卡数（示例 16）。
- `NNODES`：参与训练的节点数量（示例单机为 1）。
- `TP`：张量并行大小（示例 1）。
- `PP`：流水线并行大小（示例 16）。
- `DP`：数据并行大小（由上式反推，示例 DP=1）。

附加约束（原文）：MoE 模型还需满足 `EP ≤ DP`（Qwen3.5-VL-9B 为稠密模型，不涉及 EP）。这两个式子是启动微调前**校验硬件与并行配置是否匹配**的依据。

---

## 【关联】

- **上游依赖**：Megatron-Bridge（`run_recipe.py`）与 Megatron-LM（基础知识）；MindSpeed-Bridge 作为非侵入适配层委托给上游 `run_recipe.py`。
- **同仓库特性/模块引用**：
  - **recipe 模块**：`mindspeed_bridge/recipes/qwen_vl/qwen35_vl_9B_sft.py`（定义 `qwen35_vl_9b_sft_config`）—— 是该 quick start 的训练配方来源。
  - **示例脚本**：`mindspeed_bridge/examples/models/vlm/qwen35_vl/qwen35_vl_9b_sft_4k_A3.sh`—— 是用户实际编辑、执行的入口脚本。
  - **训练入口模块**：`mindspeed_bridge.scripts.training.run_recipe` —— 由 `torchrun --module` 触发。
  - **数据集 provider**：`PreloadedVLMConversationProvider` —— 多模态对话数据预加载组件。
  - **昇腾亲和特性**：`use_ascend_gdn`（Gated Delta Net 的 AscendC 亲和实现）、`kvallgather_cp_algo`（上下文并行算法）。
- **文档上下游**：本文反复链接 `install_guide.md`（出现 2 次），作为"环境准备"环节的前置文档；同时为后续可能涉及的并行配置调优、MoE 模型训练等留出扩展空间（GLM5/GLM5.2、Qwen3.5-VL-35B-A3B 等被作为 MoE 案例提及，但未在本 quick start 中展开）。

---

## 【使用方法】

**1. 环境准备**
- 按 `install_guide.md` 完成软件安装。
- 设置昇腾 CANN 与 ATB 环境变量（root 默认路径为例，需按实际替换）：
  ```shell
  source /usr/local/Ascend/cann/set_env.sh
  source /usr/local/Ascend/nnal/atb/set_env.sh
  ```

**2. 权重准备**
- 创建权重目录并下载 Qwen3.5-VL-9B 开源权重（HuggingFace 或 ModelScope 二选一）：
  ```shell
  mkdir -p ./model_from_hf/qwen35_vl_9b_hf
  cd ./model_from_hf/qwen35_vl_9b_hf
  huggingface-cli download Qwen/Qwen3.5-9B --local-dir .   # 方式一
  # 或
  git clone https://www.modelscope.cn/Qwen/Qwen3.5-9B.git .   # 方式二
  cd ../..
  ```
- 固化权重路径：
  ```shell
  export HF_PATH=/model_from_hf/qwen35_vl_9b_hf
  ```

**3. 数据集准备**
- 准备多模态对话 JSONL（`content` 中 `image` 类型引用图片）与图片目录：
  ```shell
  TRAIN_JSON="/path_to_dataset/train.jsonl"
  TRAIN_IMAGES="/path_to_dataset/images"
  ```
- 兼容格式：`{"conversation": [...]}` 主推 / `{"messages": [...], "images": [...]}` + `<image>` 占位（次选）。

**4. 启动微调**
- 编辑示例脚本（在 Megatron-Bridge 源码根目录下）：
  ```shell
  cd Megatron-Bridge
  vi ../MindSpeed-Bridge/mindspeed_bridge/examples/models/vlm/qwen35_vl/qwen35_vl_9b_sft_4k_A3.sh
  ```
- **关键配置项默认值**（原文给出）：
  - `WORKSPACE="$(pwd)"`
  - `NPUS_PER_NODE=16`、`MASTER_ADDR=localhost`、`MASTER_PORT=6015`、`NNODES=1`、`NODE_RANK=0`
  - `TP=1`、`PP=16`、`CP=1`、`NUM_LAYERS=32`、`MTP_LAYERS=null`
  - `RECIPE="qwen35_vl_9b_sft_config"`、`SEQ_LENGTH=4096`、`TRAIN_ITERS=2000`、`GLOBAL_BATCH_SIZE=16`、`MICRO_BATCH_SIZE=1`
  - `TRAIN_JSON="/path/to/dataset/train.jsonl"`、`TRAIN_IMAGES="/path/to/dataset/images"`
- 执行：
  ```shell
  bash ../MindSpeed-Bridge/mindspeed_bridge/examples/models/vlm/qwen35_vl/qwen35_vl_9b_sft_4k_A3.sh
  ```
- 内部启动命令（原文）：
  ```shell
  torchrun $DISTRIBUTED_ARGS --module mindspeed_bridge.scripts.training.run_recipe \
     --hf_path $HF_PATH \
     --recipe $RECIPE \
     --step_func qwen3_vl_step \
     $CLI_OVERRIDES 2>&1 | tee ./logs/qwen35_vl_9b_sft_TP${TP}_PP${PP}_CP${CP}_NUM_LAYERS${NUM_LAYERS}.log
  ```

**5. 资源不足时的应急手段（原文提示）**
- 降低 `NPUS_PER_NODE` 不足带来的 OOM 风险：适当减小 `NUM_LAYERS`、`TRAIN_ITERS`，或按"启动微调"章节调整 `TP/PP` 先验证环境与流程；并行配置须满足 `NPUS_PER_NODE × NNODES = TP × PP × DP`。

**6. 多机训练**
- 多终端各自执行同一脚本，仅 `NODE_RANK` 不同；`MASTER_ADDR` 均指向主节点 IP；其余参数保持一致；每节点需具备相同权重与数据（或共享存储）。
