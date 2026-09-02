# Quick Start: Qwen3-8B Model Pretraining and Fine-Tuning

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/training/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/training/quick_start.md

# 深度解读：Qwen3-8B 模型预训练与微调 Quick Start 文档

## 【定位】

本文档是 MindSpeed LLM 框架面向新手的入门级 Quick Start 指南，以 Qwen3-8B 模型为示例，完整描述了"环境准备 → 开源权重获取 → 权重格式转换（HF → MCore） → 数据预处理 → 启动预训练"的全链路最小可执行流程，旨在帮助开发者快速跑通一次基于昇腾 NPU 的大模型预训练任务。

---

## 【技术要点】

1. **完整流程闭环**：本文档覆盖了从 Hugging Face 原始权重到 MCore 训练格式的转换、原始数据到 `.bin/.idx` 二进制索引格式的预处理，再到 NPU 集群训练启动的完整链路，是端到端最小可行示例。

2. **Qwen3-8B 模型权重下载**：需从 Hugging Face 下载 `config.json`、`generation_config.json`、`merges.txt`、5 个分片权重文件 `model-00001-of-00005.safetensors` 至 `model-00005-of-00005.safetensors`、`model.safetensors.index.json`、`tokenizer.json`、`tokenizer_config.json`、`vocab.json` 共 11 类文件，并通过 `sha256sum` 校验完整性。

3. **权重格式转换（HF → MCore）**：使用 `convert_ckpt_v2.py`，关键参数为 `--target-tensor-parallel-size 1`（TP=1，推荐值 1）、`--target-pipeline-parallel-size 2`（PP=2，推荐值 2），对应 Qwen3-8B 的推荐分片配置 `tp1pp2`。

4. **预训练数据预处理**：以 Alpaca 数据集为例，使用 `preprocess_data.py` 脚本将 `.parquet` 原始数据转换为 `alpaca_text_document.bin` 与 `alpaca_text_document.idx` 索引文件；使用 `PretrainedFromHF` tokenizer 类型 + `GeneralPretrainHandler` 数据集处理器。

5. **环境与硬件配置**：基于 Ascend NPU（PyTorch 框架），需 `source /usr/local/Ascend/cann/set_env.sh`，并设置 `CUDA_DEVICE_MAX_CONNECTIONS=1`；单节点配置 `NPUS_PER_NODE=8`、`MASTER_ADDR=localhost`。

6. **开发者前置条件**：要求具备 PyTorch 基本经验、Python 开发经验及 Megatron-LM 仓库基本熟悉度。

---

## 【关键机制与数据】

### 工作原理与数据流

**整体数据流（原文隐含链路）：**

```
Hugging Face 原始权重（11 类文件）
    ↓ sha256sum 完整性校验
    ↓ convert_ckpt_v2.py (HF → MCore, tp1pp2)
MCore 分片权重（iter_0000001/mp_rank_00_001/model_optim_rng.pt）
    ↓ 配合 tokenizer 目录
Hugging Face 原始数据（Alpaca .parquet）
    ↓ preprocess_data.py (PretrainedFromHF + GeneralPretrainHandler)
二进制索引数据（alpaca_text_document.bin / .idx）
    ↓
NPU 预训练任务启动（pretrain_qwen3_8b_4K_ptd.sh）
```

**关键运行日志（原文给出的转换成功标志）：**
```
INFO:root:Saving to ./model_weights/qwen3_mcore/iter_0000001/mp_rank_00_001/model_optim_rng.pt
INFO:root:Done!
```

**关键配置数字（原文标注的推荐值）：**

| 配置项 | 推荐值 | 说明 |
|---|---|---|
| Tensor Parallel Size | `1` | Qwen3-8B 推荐配置 |
| Pipeline Parallel Size | `2` | Qwen3-8B 推荐配置 |
| 综合分片配置 | `tp1pp2` | 与脚本一致 |
| 数据预处理 workers | `4` | 多进程并行 |
| 日志间隔 log-interval | `1000` | 进度更新步数 |
| 单节点 NPUs | `8` | NPUS_PER_NODE |

> **性能数据**：原文未涉及训练吞吐量、loss 曲线、TPS、MFU 等性能指标。

---

## 【表格解读】

### Table 1 权重转换参数（原文逐字还原）

| Parameter | Description | Required |
|---|---|---|
| `--target-tensor-parallel-size` | Tensor parallel size. Recommended value: `1`. | ✅ |
| `--target-pipeline-parallel-size` | Pipeline parallel size. Recommended value: `2`. | ✅ |
| `--load-model-type` | Type of the loaded weights. It can be `hf` or `mg`. | ✅ |
| `--save-model-type` | Type of the saved weights. It can be `hf` or `mg`. | ✅ |
| `--load-dir` | Weight file load path. | ✅ |
| `--save-dir` | Weight file save path. | ✅ |
| `--model-type-hf` | Hugging Face model type. | ✅ |

**逐行解读：**

- **`--target-tensor-parallel-size`（必填）**：目标张量并行度，将单层 Qwen3-8B 的 Attention/MLP 权重切分到多张 NPU 上做张量并行；推荐值 `1`，即不做 TP 切分。
- **`--target-pipeline-parallel-size`（必填）**：目标流水线并行度，将 Transformer 的不同层段放到不同 NPU 上以流水线方式执行；推荐值 `2`，即拆成 2 个 stage。
- **`--load-model-type`（必填）**：源端权重格式，`hf` 表示 Hugging Face 原生格式，`mg` 表示 MCore 格式；本流程取 `hf`。
- **`--save-model-type`（必填）**：目标端权重格式，本流程取 `mg`（即 Megatron-Core）。
- **`--load-dir`（必填）**：源端权重目录，本示例为 `./model_from_hf/qwen3_hf/`。
- **`--save-dir`（必填）**：目标端权重输出目录，本示例为 `./model_weights/qwen3_mcore/`，最终落盘路径为 `iter_0000001/mp_rank_00_001/model_optim_rng.pt`。
- **`--model-type-hf`（必填）**：指定 Hugging Face 端的模型类型字符串，本示例为 `qwen3`，脚本据此识别模型结构与层映射。

---

### Table 2 数据预处理参数（原文逐字还原）

| Parameter | Description | Required |
|---|---|---|
| `--input` | Supported input formats include dataset directories or files. If you specify a directory, the script processes all files in it. Supported formats are `.parquet`, `.csv`, `.json`, `.jsonl`, `.txt`, and `.arrow`. All files in the same directory must use the same format. | ✅ |
| `--tokenizer-type` | Specifies the tokenizer type. When the value is `PretrainedFromHF`, you only need to fill in the model directory for the vocabulary path. | ✅ |
| `--tokenizer-name-or-path` | Works with `tokenizer-type`. This is the tokenizer source directory of the target model and is used for dataset conversion. | ✅ |
| `--handler-name` | Specifies the dataset handler class. | ✅ |
| `--output-prefix` | File name prefix of the converted dataset output. | ✅ |
| `--workers` | Multi-process dataset processing. | ✅ |
| `--log-interval` | Number of steps between progress updates. | ✅ |
| `--json-keys` | List of column names extracted from the file. The default is `text`, and you can use multiple inputs such as `text`, `input`, and `title` according to the actual data. | ✅ |

**逐行解读：**

- **`--input`（必填）**：输入路径，可为单文件或目录；支持 `.parquet`、`.csv`、`.json`、`.jsonl`、`.txt`、`.arrow` 六种格式；同一目录下文件格式必须一致。本示例使用 Alpaca 单文件 `.parquet`。
- **`--tokenizer-type`（必填）**：tokenizer 类型；`PretrainedFromHF` 表示直接复用 Hugging Face 模型目录里的 tokenizer，无需单独指定 vocab 文件。
- **`--tokenizer-name-or-path`（必填）**：与 `--tokenizer-type` 配合，指向目标模型的 tokenizer 源目录；本示例为 `./model_from_hf/qwen3_hf/`。
- **`--handler-name`（必填）**：数据集处理器类名，决定如何把原始数据拼接成训练样本；本示例用通用预训练处理器 `GeneralPretrainHandler`。
- **`--output-prefix`（必填）**：输出文件名前缀；本示例为 `./dataset/alpaca`，生成 `alpaca_text_document.bin` 和 `alpaca_text_document.idx` 两个文件。
- **`--workers`（必填）**：数据预处理的并行进程数；本示例设为 `4`，用于加速大规模数据 tokenize。
- **`--log-interval`（必填）**：进度日志输出间隔（按处理步数计）；本示例为 `1000`。
- **`--json-keys`（必填）**：从输入文件中抽取的列名列表；默认为 `text`，可根据实际数据多选（如 `text`、`input`、`title`）；本示例使用 `text`。

---

## 【公式解读】

**原文无公式。**

（注：原文中所有命令均为 shell/Python 调用形式，未出现 LaTeX 数学公式或伪代码形式的算式表达。）

---

## 【关联】

本文档处于 Quick Start 链路的最上游，作为"任务启动入口"，与以下上下游模块/文档存在明确引用关系：

### 上游（前置依赖）
1. **[install_guide.md](install_guide.md)**：环境准备阶段指引用户查阅此文档以完成 PyTorch 框架在 Ascend NPU 上的安装；属于 Quick Start 的**前置条件**。
2. **[checkpoint_convert_hf_mcore_large_params.md](../tools/checkpoint_convert_hf_mcore_large_params.md)**：权重转换章节（"Weight Conversion"）指引用户查阅此文档以获取 HF → MCore 转换的细节；属于 Quick Start 的**工具层依赖**。

### 下游（后续步骤）
3. **[data_process_pretrain.md](../tools/data_process_pretrain.md)**：数据预处理章节明确指引用户查阅此文档以获取预训练数据集处理的详细说明；属于 Quick Start 的**数据侧延伸**。
4. **[data_process_sft_alpaca_style.md](../tools/data_process_sft_alpaca_style.md)**：文末虽未在正文中显式展开，但属于"指令微调"阶段（Alpaca 风格数据处理）的工具文档，与本指南描述的"基于预训练模型的单样本格式指令微调"目标直接对应。
5. **[templates.json](../../../../configs/finetune/templates.json)**：配置文件，承载微调（finetune）阶段使用的提示词模板 / 数据格式模板，与指令微调任务模板配置直接相关。

### 模块关系总结
本 Quick Start 串联了 **「安装」→「权重获取」→「权重转换」→「数据预处理」→「预训练启动」→「微调」** 的完整链路，前两条为前置环境与工具准备，后两条为下游训练侧扩展。

---

## 【使用方法】

### 启用方式（按原文步骤）

#### Step 1：环境准备
```shell
# 参考 install_guide.md 完成 PyTorch + Ascend NPU 环境搭建
source /usr/local/Ascend/cann/set_env.sh
export CUDA_DEVICE_MAX_CONNECTIONS=1
```

#### Step 2：下载 Qwen3-8B 权重
```shell
mkdir -p ./model_from_hf/qwen3_hf
cd ./model_from_hf/qwen3_hf
wget https://huggingface.co/Qwen/Qwen3-8B/resolve/main/{config,generation_config}.json
wget https://huggingface.co/Qwen/Qwen3-8B/resolve/main/merges.txt
wget https://huggingface.co/Qwen/Qwen3-8B/resolve/main/model-0000{1..5}-of-00005.safetensors
wget https://huggingface.co/Qwen/Qwen3-8B/resolve/main/{model.safetensors.index.json,tokenizer.json,tokenizer_config.json,vocab.json}
```

#### Step 3：SHA-256 校验
```shell
sha256sum model-0000{1..5}-of-00005.safetensors
```
对比 Hugging Face 文件详情页给出的哈希值。

#### Step 4：HF → MCore 权重转换
```shell
vi examples/mcore/qwen3/ckpt_convert_qwen3_hf2mcore.sh
# 按 Table 1 配置：TP=1, PP=2
bash examples/mcore/qwen3/ckpt_convert_qwen3_hf2mcore.sh
```

#### Step 5：预训练数据预处理
```shell
mkdir dataset && cd dataset
wget https://huggingface.co/datasets/tatsu-lab/alpaca/resolve/main/data/train-00000-of-00001-a09b74b3ef9c3b56.parquet
cd ..
vi examples/mcore/qwen3/data_convert_qwen3_pretrain.sh
# 按 Table 2 配置参数
bash examples/mcore/qwen3/data_convert_qwen3_pretrain.sh
# 产物：./dataset/alpaca_text_document.{bin,idx}
```

#### Step 6：启动预训练任务
```shell
vi examples/mcore/qwen3/pretrain_qwen3_8b_4K_ptd.sh
# 已给出片段：
# NPUS_PER_NODE=8
# MASTER_ADDR=localhost
```
**⚠ 原文截断提示**：本文档在 Step 6 处文本截断（`MASTER_ADDR=localhost     # On a single node, use the IP address o...`），后续预训练脚本完整参数、`bash` 启动命令、训练日志样例、SFT（指令微调）章节以及对应命令均**原文未涉及**，需结合仓库实际脚本 `examples/mcore/qwen3/pretrain_qwen3_8b_4K_ptd.sh` 或后续文档（如 `data_process_sft_alpaca_style.md`、`configs/finetune/templates.json`）补全。

### 配置项汇总

| 类别 | 关键参数 | 原文推荐值 |
|---|---|---|
| 硬件 | NPUS_PER_NODE | 8 |
| 网络 | MASTER_ADDR（单机） | localhost |
| 训练并行 | TP size | 1 |
| 训练并行 | PP size | 2 |
| 综合分片 | 推荐配置 | tp1pp2 |
| 数据预处理 | workers | 4 |
| 数据预处理 | log-interval | 1000 |
| 数据预处理 | tokenizer-type | PretrainedFromHF |
| 数据预处理 | handler-name | GeneralPretrainHandler |
| 数据预处理 | json-keys | text |

## 图文联合解读

- `running_log.png`: # 图文联合解读

**1) 图中内容：** 终端日志展示Qwen3-8B训练运行记录，包含模型参数规模（总参7.62B，embedding层1.09B），显存预算约36.7GB；多Rank内存分配数据（allocated/reserved/max allocated）；迭代训练指标（iter 1/2000→4/2000，吞吐量25.1→151.7 TFLOPs/s/GPU，lm loss≈12.14，学习率6.25→2.5，grad norm≈56）。

**2) 技术结论：** Qwen3-8B在Ascend NPU上成功启动并稳定训练，多Rank显存分配均衡（各卡占用约29–39GB），无nan/skipped异常，吞吐量稳步提升至151 TFLOPs/s/GPU，loss缓慢下降，验证了训练流程可行性。

**3) 与文档关联：** 作为"启动训练任务"步骤的可视化佐证，定量呈现Qwen3-8B在MindSpeed LLM上的真实运行状态，降低新手对训练效果的感知门槛。
- `tune_log.png`: ## 图文联合解读

**1）图中内容**：终端训练日志，包含两部分：  
- **参数统计**：transformer block 6.95B + embedding 1.24B = 总参数量 8.19B；权重+优化器理论内存约 35GB；各 rank 已分配/预留显存明细。  
- **迭代指标**（iter 1–5）：每步耗时、学习率、global batch size=16、lm loss（3.05→5.26→4.44→3.93→3.54）、grad norm 及跳过迭代计数。

**2）技术结论**：loss 总体收敛下降且无 NaN、显存分配稳定（~35GB），证明 MindSpeed LLM 已在昇腾 NPU 上成功完成 Qwen3-8B 的预训练/微调前向与反向传播。

**3）与文档关系**：直观佐证文档"在 Ascend NPU 上启动预训练与微调任务"论点，为开发者提供可复现的运行预期。

（约 148 字）
