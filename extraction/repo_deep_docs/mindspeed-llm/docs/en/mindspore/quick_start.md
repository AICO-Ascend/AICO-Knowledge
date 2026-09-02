# Quick Start: Qwen3-0.6B Model Pretraining and Fine-Tuning

> 仓 `mindspeed-llm` · 路径 `docs/en/mindspore/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/mindspore/quick_start.md

# 一体化深度解读：mindspeed-llm MindSpore Qwen3-0.6B Quick Start

## 【定位】

本文是 MindSpeed LLM（昇思版）面向新开发者的「Qwen3-0.6B 预训练与微调快速上手」Guide，给出从环境准备、Hugging Face 权重下载、HF→MCore 权重转换、到 Alpaca 数据预处理与启动预训练任务的端到端最小化示例，覆盖单卡（TP=1, PP=1）MindSpore Ascend NPU 上的语言模型二次预训练与指令微调完整链路。

---

## 【技术要点】

1. **MindSpore Ascend NPU 单机训练最小化路径**：以 Qwen3-0.6B 为例，覆盖「环境准备 → 权重获取 → HF→MCore 转换 → 数据预处理（`.bin`/`.idx`）→ 启动预训练/微调」四个主步骤；推荐分片配置为 `tp1pp1`（即 TP=1, PP=1）。

2. **权重格式硬性要求**：Ascend MindSpeed LLM **只接受 MCore (`mg`) 格式权重**作为输入；原始 Hugging Face 权重须通过 `convert_ckpt.py` 转换。MindSpore 端默认在 Device 侧做权重转换，**对 LLM 存在 OOM 风险**，文档建议在 `convert_ckpt.py` 顶部手工加入 CPU 上下文代码（`ms.set_context(device_target="CPU", ...)` + `torch.configs.set_pyboost(False)`）以走 CPU 侧转换。

3. **关键转换命令参数组合**：`--use-mcore-models`、`--load-model-type hf`、`--save-model-type mg`、`--model-type-hf qwen3`、`--spec mindspeed_llm.tasks.models.spec.qwen3_spec layer_spec`、`--ai-framework mindspore`、权重精度 `--params-dtype bf16`（与源 Qwen3 权重保持一致）。

4. **预训练数据预处理统一格式**：通过 `preprocess_data.py` 把 `.parquet/.csv/.json/.jsonl/.txt/.arrow` 多种原始格式统一预处理成 `.bin` + `.idx` 双文件，避免训练时重复加载；示例采用 Alpaca 数据集（`train-00000-of-00001-...parquet`），列名用 `--json-keys text`。

5. **Tokenizer 与 Handler 解耦**：使用 HF 来源 tokenizer（`--tokenizer-type PretrainedFromHF` + `--tokenizer-name-or-path`）配合通用预训练 handler（`--handler-name GeneralPretrainHandler`），多进程 `--workers 4`，进度 `--log-interval 1000`。

6. **关键约束**：
   - "MindSpore performs weight conversion on the Device side by default ... OOM risk"（原文 NOTE）。
   - "Model weights converted by MindSpore cannot be used directly for PyTorch training or inference."（MindSpore 转换出的权重**不能**直接给 PyTorch 训练/推理用，反之亦然，两条栈互不通用）。
   - 同一目录下的原始文件**必须为同一格式**。

---

## 【关键机制与数据】

- **预训练数据预处理工作流（原文）**：通过 `preprocess_data.py` 在训练前把多格式原始数据（`.parquet/.csv/.json/.jsonl/.txt/.arrow`）一次性预处理成 **两个统一文件 `.bin` + `.idx`**；Handler（`GeneralPretrainHandler`）负责解析、tokenizer（`PretrainedFromHF`）负责切分 token，最终产物以 `--output-prefix` 为前缀（如 `alpaca`），生成 `alpaca_text_document.bin` 和 `alpaca_text_document.idx`。

- **权重链路工作流（原文）**：HF `Qwen3-0.6B` 全量权重（`config.json` / `model.safetensors` / `tokenizer.json` / `vocab.json` / `merges.txt` / `generation_config.json` / `tokenizer_config.json`） → 校验 SHA-256 → `convert_ckpt.py`（HF→MCore, bf16, TP=1/PP=1, `qwen3_spec layer_spec`） → 落到 `./model_weights/qwen3_mcore/`，并以 `successfully saved checkpoint from iteration 1 to ./model_weights/qwen3_mcore/` + `INFO:root:Done!` 作为成功标志。

- **设备侧 vs CPU 侧权重转换（原文）**：默认走 Device 侧，对 LLM 易 OOM；推荐手工改 `convert_ckpt.py` 顶部加入 `import mindspore as ms; ms.set_context(device_target="CPU", pynative_synchronize=True); import torch; torch.configs.set_pyboost(False)`，强制 CPU 侧转换以规避显存不足。

- **性能数据**：原文未给出吞吐、训练步数、loss 数值、训练时长等任何性能/精度数据。

---

## 【表格解读】

### Table 1 权重转换参数（原文逐字还原）

| Parameter | Description | Required |
|---|---|---|
| `--use-mcore-models` | Convert to the MCore format. | ✅ |
| `--model-type GPT` | Specify the model type as the GPT series. | ✅ |
| `--target-tensor-parallel-size` | Tensor parallel size. Recommended value: `1`. | ✅ |
| `--target-pipeline-parallel-size` | Pipeline parallel size. Recommended value: `1`. | ✅ |
| `--load-model-type` | The type of the loaded weights. It can be `hf` or `mg`. | ✅ |
| `--save-model-type` | The type of the saved weights. It can be `hf` or `mg`. | ✅ |
| `--load-dir` | Weight file load path. | ✅ |
| `--save-dir` | Weight file save path. | ✅ |
| `--model-type-hf` | Hugging Face model type. | ✅ |
| `--params-dtype` | Weight precision after conversion. The default is `fp16`. If the source files use `bf16`, set this option to `bf16`. | ✅ |
| `--spec` | Transformer layer structure configuration. | ✅ |
| `--tokenizer-model` | Tokenizer model file path. | ✅ |
| `--ai-framework` | Training framework. Supported values are `pytorch` and `mindspore`. The default is `pytorch`. Set this option to `mindspore`. | ✅ |

**逐行解读**：
- `--use-mcore-models` 是 MCore 格式开关，不开启则不会落 mg 格式。
- `--model-type GPT` 说明 MindSpeed LLM MindSpore 端是按 GPT 类 Decoder-only 模型规范实现的，Qwen3 走的是该骨架（通过 `--spec` 替换层结构）。
- `--target-tensor-parallel-size` / `--target-pipeline-parallel-size` 均为转换后权重的目标并行度，原文**明确推荐 `1`**，与 Qwen3-0.6B 的 `tp1pp1` 建议分片配置一致。
- `--load-model-type` / `--save-model-type` 限定为 `hf`/`mg` 二选一，本场景是 `hf → mg`。
- `--load-dir` / `--save-dir` 即 HF 源权重目录（`./model_from_hf/qwen3_hf/`）和 MCore 目标目录（`./model_weights/qwen3_mcore/`）。
- `--model-type-hf` 取 `qwen3`，与 `--spec mindspeed_llm.tasks.models.spec.qwen3_spec layer_spec` 一起用于正确解析 Qwen3 的 HF 命名空间与 MindSpore 端层结构。
- `--params-dtype` 默认 `fp16`，但因 Qwen3-0.6B 源权为 `bf16`，**必须显式设为 `bf16`** 才能保精度一致。
- `--spec` 指向 Qwen3 的 MindSpore 端 Transformer 层规格文件，是 MindSpeed 把 HF 模型映射到 Megatron-LM 风格层定义的关键。
- `--tokenizer-model` 单独指向 `tokenizer.json`，转换阶段就需要 tokenizer 信息以校验词表大小等匹配。
- `--ai-framework` 默认 `pytorch`，**本指南必须显式设为 `mindspore`**，否则会进入 PyTorch 分支。

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

**逐行解读**：
- `--input` 支持目录或单文件，覆盖 6 种常见数据格式；但**同目录内格式必须统一**（隐性要求）。
- `--tokenizer-type PretrainedFromHF` + `--tokenizer-name-or-path` 配合使用，只要指 HF 模型目录即可自动加载其内嵌 tokenizer。
- `--handler-name` 决定如何把原始字段映射成 token 序列；`GeneralPretrainHandler` 是 Alpaca 这类纯文本预训练场景的通用处理器。
- `--output-prefix` 即产物前缀，**会同时生成 `.bin` 与 `.idx`**（如 `alpaca_text_document.bin/idx`）。
- `--workers 4` 启用 4 个进程并行预处理，加速 Alpaca 这种小到中等规模数据集。
- `--log-interval 1000` 控制预处理阶段每 1000 步打印一次进度。
- `--json-keys` 默认 `text`，可指定多列（如 `text,input,title`），从原始 schema 中抽取多字段拼接训练。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **前置依赖**：[`install_guide.md`](install_guide.md) — MindSpore 框架的 MindSpeed LLM 安装指南，本文"环境准备"小节直接 link 过去，作为跑通 Quick Start 的前提。
- **权重转换细节**：[`../pytorch/tools/checkpoint_convert_hf_mcore_large_params.md#21-converting-hugging-face-weights-to-the-mcore-format`](../pytorch/tools/checkpoint_convert_hf_mcore_large_params.md#21-converting-hugging-face-weights-to-the-mcore-format) — 跨 MindSpore/PyTorch 链路通用的 HF→MCore 大参数量权重转换原理，本文 Weight Conversion 段指向其「21-Converting Hugging Face weights to the MCore format」锚点；尽管它位于 pytorch 路径下，但 MindSpore 端复用同一 MCore 权重规范。
- **预训练数据处理细节**：[`../pytorch/tools/data_process_pretrain.md`](../pytorch/tools/data_process_pretrain.md) — `preprocess_data.py` 把任意格式数据统一预处理为 `.bin`/`.idx` 双文件机制的官方说明，本文 Data Preprocessing 段引用，作为 `.bin`/`.idx` 输出规范的权威出处。
- **MindSpore ↔ PyTorch 互斥关系**：原文 NOTE 强调「MindSpore 转换的权重不能直接用于 PyTorch 训练/推理」，意味着同一 repo 下的 MindSpore 文档与 PyTorch 文档共享相同的 MCore 中间格式与脚本入口，但**最终权重栈互不通用**；本文与 PyTorch 系列文档（如上文两个 pytorch 路径下的工具文档）是「同源不同栈」关系。
- **上下游关系**：上游依赖 Hugging Face `Qwen/Qwen3-0.6B` 仓库提供原始权重 + tokenizer；下游（本文未展示部分，按目录推断）应接 pretrain 启动脚本与 fine-tune 启动脚本（同一 `examples/mindspore/qwen3/` 目录下）。

---

## 【使用方法】

**1. 环境准备**
- 装 MindSpore 框架 + Ascend NPU CANN，按 `install_guide.md` 走；并 `source /usr/local/Ascend/cann/set_env.sh`。

**2. 下载 Qwen3-0.6B HF 权重**
```shell
mkdir -p ./model_from_hf/qwen3_hf
cd ./model_from_hf/qwen3_hf
wget https://huggingface.co/Qwen/Qwen3-0.6B/resolve/main/{config.json,generation_config.json,merges.txt,model.safetensors,tokenizer.json,tokenizer_config.json,vocab.json}
sha256sum model.safetensors   # 对照 HF 网页上的 SHA-256
```

**3. HF → MCore 权重转换（推荐先改 CPU 上下文规避 OOM）**
```shell
cd MindSpeed-LLM
# 在 convert_ckpt.py 顶部加入：
#   import mindspore as ms
#   ms.set_context(device_target="CPU", pynative_synchronize=True)
#   import torch
#   torch.configs.set_pyboost(False)
vi examples/mindspore/qwen3/ckpt_convert_qwen3_hf2mcore.sh   # 按上文示例修改
bash examples/mindspore/qwen3/ckpt_convert_qwen3_hf2mcore.sh
# 成功标志：successfully saved checkpoint from iteration 1 to ./model_weights/qwen3_mcore/
#           INFO:root:Done!
```

**4. 预训练数据预处理（Alpaca 示例）**
```shell
mkdir dataset && cd dataset
wget https://huggingface.co/datasets/tatsu-lab/alpaca/resolve/main/data/train-00000-of-00001-a09b74b3ef9c3b56.parquet
# 或：https://www.modelscope.cn/datasets/angelala00/tatsu-lab-alpaca/resolve/master/train-00000-of-00001-a09b74b3ef9c3b56.parquet
cd ..
vi examples/mindspore/qwen3/data_convert_qwen3_pretrain.sh    # 按上文示例修改
bash examples/mindspore/qwen3/data_convert_qwen3_pretrain.sh
# 产物：./dataset/alpaca_text_document.bin + .idx
```

**关键配置项汇总**（仅就原文给出的）：
- 并行度：`tp1pp1`（Qwen3-0.6B 官方推荐）
- 精度：源/目标均为 `bf16`
- 框架：`--ai-framework mindspore`
- 模型规格：`--spec mindspeed_llm.tasks.models.spec.qwen3_spec layer_spec`
- Tokenizer：`--tokenizer-type PretrainedFromHF`
- 处理器：`--handler-name GeneralPretrainHandler`
- 预处理并发：`--workers 4`，`--log-interval 1000`

**注意**：原文在 "4. Run the pretraining data processing script." 处被截断，**预训练任务启动脚本、微调任务启动脚本**等内容原文未涉及；具体 pretrain/finetune 启动命令需参照同仓 `examples/mindspore/qwen3/` 下的其他脚本文件。

## 图文联合解读

- `running_log.png`: **图示内容**:终端日志展示Qwen3-0.6B模型在Ascend NPU上的训练启动信息，含参数分布(总7.62B)、理论显存(37360.75 MB)、Rank级显存占用，以及前4个iteration的耗时、吞吐(25.1→152 TFLOP/s/GPU)、学习率(6.25e-7→2.5e-6)、loss(21.5→12.14)。

**技术结论**:模型成功加载并进入warmup阶段，loss快速下降、吞吐稳定在~152 TFLOP/s/GPU，多卡显存分配均衡(约37–42 GB)，验证了训练流程正常启动。

**与文档关系**:作为"启动训练任务"步骤的实证截图,印证开发者在按文档配置后可在NPU上顺利跑通Qwen3-0.6B的预训练/微调。
