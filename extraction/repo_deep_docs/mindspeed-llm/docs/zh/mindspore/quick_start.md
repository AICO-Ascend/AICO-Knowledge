# 快速入门：Qwen3-0.6B 模型预训练及微调

> 仓 `mindspeed-llm` · 路径 `docs/zh/mindspore/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/mindspore/quick_start.md

# 深度解读：Qwen3-0.6B 模型预训练及微调快速入门（MindSpore）

> 说明：原文在"微调 → 数据预处理 → 第 3 步"处出现截断（脚本仅展示到 `--input` 一行就被截断，未展示后续 `--tokenizer-*` / `--handler-name` / `--output-prefix` 等参数及后续启动微调章节），下面解读以原文实际呈现内容为准，对缺失部分予以如实标注。

---

## 【定位】

这篇文档是 MindSpeed-LLM（昇腾 + MindSpore 框架）面向初次接触者的"零起步"教程，以 Qwen3-0.6B 为具体样例，端到端串起「环境搭建 → HuggingFace 权重获取 → HF→Megatron-Mcore 权重转换 → 预训练数据预处理 → 启动预训练 → 微调数据预处理（脚本被截断）」完整流程，让开发者能在 Ascend NPU 上以单样本 Alpaca 数据快速跑通指令微调任务。

---

## 【技术要点】

1. **训练框架栈**：MindSpore + Megatron-LM（Mcore 分支）+ Ascend NPU（`source /usr/local/Ascend/cann/set_env.sh` + `atb/set_env.sh`），权重必须先转成 Megatron-Mcore 格式才能跑训练。
2. **模型示例**：Qwen3-0.6B（Qwen 系列），示例脚本路径 `examples/mindspore/qwen3/` 下 `ckpt_convert_qwen3_hf2mcore.sh`、`data_convert_qwen3_pretrain.sh`、`pretrain_qwen3_0point6b_4K_ms.sh`、`data_convert_qwen3_instruction.sh`。
3. **预训练并行/规模配置（原文给出的示例值）**：`NPUS_PER_NODE=8`、`NNODES=1`、`TP=1`、`PP=1`、`SEQ_LEN=4096`、`MBS=1`、`GBS=8`、`TRAIN_ITERS=2000`，对应分布式通信端口 `MASTER_PORT=6011`。
4. **关键模型结构开关**：`--use-mcore-models`、`--disable-bias-linear`（与 Qwen 原模型一致）、`--group-query-attention` + `--num-query-groups 8`（GQA）、`--position-embedding-type rope`（RoPE）、`--bf16`、`--ai-framework mindspore`。
5. **数据预处理统一格式**：所有原始数据（.parquet/.csv/.json/.jsonl/.txt/.arrow）经 `preprocess_data.py` 统一产出 `.bin` + `.idx` 双文件，预训练例产生 `alpaca_text_document.bin/.idx`，使用 `PretrainedFromHF` tokenizer + `GeneralPretrainHandler`，`--workers 4`、`--log-interval 1000`。
6. **MindSpore 特殊约束（原文 NOTE 强调）**：
   - 默认在 Device 侧做权重转换，大模型易 OOM，建议在 `convert_ckpt.py` 包导入时加入 `ms.set_context(device_target="CPU", pynative_synchronize=True)` + `torch.configs.set_pyboost(False)` 强制 CPU 侧转换；
   - MindSpore 转换出的权重**不可直接用于 PyTorch 训练/推理**；
   - 多机训练需各终端分别启动脚本、仅 `NODE_RANK` 不同，无共享存储时需追加 `--no-shared-storage`。

---

## 【关键机制与数据】

### 工作流（数据流 + 权重流，对应原文步骤）

**原文主线**：环境搭建 → 下载 HF 权重（`config.json / generation_config.json / merges.txt / model.safetensors / tokenizer.json / tokenizer_config.json / vocab.json`）→ `sha256sum` 校验 `model.safetensors` → `convert_ckpt.py` 以 `--use-mcore-models --load-model-type hf --save-model-type mg --target-tensor-parallel-size 1 --target-pipeline-parallel-size 1 --model-type-hf qwen3 --params-dtype bf16 --spec mindspeed_llm.tasks.models.spec.qwen3_spec layer_spec --ai-framework mindspore` 切分为 mg 权重 → `preprocess_data.py`（`--tokenizer-type PretrainedFromHF --handler-name GeneralPretrainHandler --workers 4 --log-interval 1000`）产出 `alpaca_text_document.bin/.idx` → 启动 `pretrain_qwen3_0point6b_4K_ms.sh` 完成 2000 步预训练 → 微调阶段同样走 `preprocess_data.py` 产出 `.bin/.idx`（原文脚本截断）。

**原文给出的成功标志日志**（权重转换成功后）：
```
successfully saved checkpoint from iteration 1 to ./model_weights/qwen3_mcore/
INFO:root:Done!
```

**原文给出的训练规模常量（示例脚本）**：

| 维度 | 数值（原文） |
|---|---|
| NPUS_PER_NODE | 8 |
| NNODES | 1 |
| WORLD_SIZE | `NPUS_PER_NODE * NNODES` |
| MASTER_PORT | 6011 |
| TP × PP | 1 × 1 |
| SEQ_LEN | 4096 |
| MBS / GBS | 1 / 8 |
| TRAIN_ITERS | 2000 |
| 预训练 GQA groups | 8 |
| 精度 | bf16 |

**性能/资源类数字**：原文未给出吞吐量、训练耗时、NPU 利用率、显存占用等性能数据，仅指定了上述配置值；微调章节未给出并行度、batch size、iter 数（因原文截断）。

---

## 【表格解读】

### 表 1：权重转换参数解析（逐字还原）

|参数|说明|必填|
|---|---|---|
|`--use-mcore-models`|转换为Megatron-Mcore格式| ✅ |
|`--model-type GPT`|指定模型类型为GPT系列| ✅ |
|`--target-tensor-parallel-size`|张量并行度设置（建议配置1）| ✅ |
|`--target-pipeline-parallel-size`|流水线并行度设置（建议保持1）| ✅ |
|`--load-model-type`|加载权重的类别（可以是hf、mg）| ✅ |
|`--save-model-type`|存储权重的类别（可以是hf、mg）| ✅ |
|`--load-dir`|权重文件加载路径| ✅ |
|`--save-dir`|权重文件保存路径| ✅ |
|`--model-type-hf`|HuggingFace模型类别| ✅ |
|`--params-dtype`|指定权重转换后的权重精度模式，默认为fp16，如果源文件格式为bf16，则需要设置为bf16 | ✅ |
|`--spec`| 指定Transformer层的结构配置| ✅ |
|`--tokenizer-model`|指定分词器模型文件路径 | ✅ |
|`--ai-framework`|指定使用的训练框架，支持`pytorch`和`mindspore`，默认为`pytorch`，需要设置为`mindspore` | ✅ |

**逐行解读**：
- `--use-mcore-models`：开启 Megatron-Mcore（新版）权重/模型分支，与 Mcore 训练配套。
- `--model-type GPT`：MindSpeed 内部将 Qwen3 视作 GPT 家族成员（Decoder-only），便于复用 GPT 类切分逻辑。
- `--target-tensor-parallel-size` / `--target-pipeline-parallel-size`：Qwen3-0.6B 推荐 `tp=1, pp=1`（原文 NOTE 强调），即单卡单进程承载整模型，避免小模型被强行切分。
- `--load-model-type` / `--save-model-type`：原文限定 `hf → mg` 方向。
- `--load-dir` / `--save-dir`：原文示例为 `./model_from_hf/qwen3_hf/` → `./model_weights/qwen3_mcore/`。
- `--model-type-hf qwen3`：指明 HF 模型类别以选择对应的加载器。
- `--params-dtype`：Qwen3-0.6B 原权重为 bf16，因此必须设为 `bf16`，否则精度不匹配。
- `--spec mindspeed_llm.tasks.models.spec.qwen3_spec layer_spec`：注入 Qwen3 的层结构规范（含 GQA、RoPE、归一化等）。
- `--tokenizer-model`：原文指向 `./model_from_hf/qwen3_hf/tokenizer.json`，转换时一并加载以保证词表一致。
- `--ai-framework mindspore`：MindSpore 训练前的必填项；默认 `pytorch`，必须显式覆盖。

### 表 2：数据预处理参数解析（逐字还原）

|参数|说明|必填|
|---|---|---|
|`--input`|支持输入数据集目录或文件，目录则处理全部文件, 支持.parquet、.csv、.json、.jsonl、.txt、.arrow格式，同一目录要求数据格式保持一致| ✅ |
|`--tokenizer-type`|说明使用tokenizer类别，参数值为PretrainedFromHF时，词表路径填写模型目录即可| ✅ |
|`--tokenizer-name-or-path`|配合tokenizer-type，目标模型的tokenizer原数据文件夹，用于数据集的转换| ✅ |
|`--handler-name`|指定数据集的处理类| ✅ |
|`--output-prefix`|转换后输出的数据集文件的文件名前缀 | ✅ |
|`--workers`|多进程数据集处理| ✅ |
|`--log-interval`|处理进度更新的间隔步数| ✅ |
|`--json-keys`|从文件中提取的列名列表，默认为`text`，可以为`text`、`input`及`title`等多个输入，结合实际情况及数据集内容使用| ✅ |

**逐行解读**：
- `--input`：原文示例 `./dataset/train-00000-of-00001-a09b74b3ef9c3b56.parquet`（Alpaca 数据集）。
- `--tokenizer-type PretrainedFromHF`：从 HF 模型目录直接加载 tokenizer，避免单独再下词表。
- `--tokenizer-name-or-path`：原文示例 `./model_from_hf/qwen3_hf/`（即下载的 Qwen3-0.6B 目录）。
- `--handler-name GeneralPretrainHandler`：对应预训练范式（与下游微调 `AlpacaStyle*Handler` 区分）。
- `--output-prefix ./dataset/alpaca`：最终文件为 `alpaca_text_document.bin` + `.idx`。
- `--workers 4`：4 进程并行 tokenize。
- `--log-interval 1000`：每处理 1000 条打印一次进度。
- `--json-keys text`：从 Alpaca parquet 中抽取 `text` 列作为训练语料。

### 表 3：训练脚本参数说明（逐字还原）

|参数名|说明|
|----|----|
|`--use-mcore-models`|使用Mcore分支运行模型|
|`--disable-bias-linear`|去掉linear的偏移值，与Qwen原模型一致|
|`--group-query-attention`|开启GQA注意力处理机制|
|`--num-query-groups 8`|配合GQA使用，设置groups为8|
|`--position-embedding-type rope`|位置编码采用RoPE方案|
|`--bf16`|昇腾芯片对bf16精度支持良好，可显著提升训练速度|
|`--ai-framework`|指定使用的训练框架|

**逐行解读**：
- `--use-mcore-models`：训练侧与权重转换侧保持同一分支。
- `--disable-bias-linear`：Qwen 系列原模型在 attention/MLP 的 Linear 层均无 bias，训练侧需对齐以避免数值偏移。
- `--group-query-attention` + `--num-query-groups 8`：Qwen3-0.6B 使用 GQA（Q 多、K/V 少），groups=8 与模型结构一致。
- `--position-embedding-type rope`：Qwen3 默认使用 RoPE 旋转位置编码。
- `--bf16`：昇腾对 bf16 支持良好（原文原话），兼顾速度与数值范围。
- `--ai-framework`：在 MindSpore 分支下必须显式指定为 `mindspore`（原文 NOTE 第 3 条）。

---

## 【公式解读】

**原文无公式**（全文未出现任何数学公式或伪代码形式的方程；仅有 shell 命令、参数表与变量赋值）。

---

## 【关联】

### 与文中提到的其他特性/模块的上下游关系

| 文档/模块 | 在本文中的角色 | 关系方向 |
|---|---|---|
| `install_guide.md`（MindSpeed LLM软件安装） | "环境搭建"小节的唯一外链 | **前置依赖**：不安装就跑不起来任何后续步骤 |
| `../pytorch/tools/checkpoint_convert_hf_mcore_large_params.md#huggingface权重转换至megatron-mcore格式` | "权重转换"小节的外链 | **前置依赖**：提供 HF→Mcore 转换的通用参数说明，本文脚本是其具体实例化 |
| `../pytorch/tools/data_process_pretrain.md` | "启动预训练 → 数据预处理"小节的外链 | **前置依赖**：本文 `data_convert_qwen3_pretrain.sh` 是该通用文档的样例化 |
| `../pytorch/tools/data_process_sft_alpaca_style.md` | "启动微调 → 数据预处理"小节的外链（注意：路径以 `pytorch` 标注） | **前置依赖**：定义 Alpaca 风格指令微调数据格式与 handler |
| `../../../configs/finetune/templates.json`（文末内部链接清单列出，但原文正文**未实际引用**该文件） | 在该 guide 的姊妹/下游文档中作为 prompt template 模板 | **下游引用**：本文未直接涉及，仅出现在链接清单中 |

### 横向关系
- **与 Megatron-LM 仓库**：MindSpeed-LM 复用 Megatron-LM 的并行/优化机制（如 TP/PP、GQA、RoPE、bf16），因此要求开发者"具备对 Megatron-LM 仓库的基本了解"。
- **与 HuggingFace 生态**：所有原始权重与 Alpaca 数据均来自 HF，转换链路是"HF → Mcore"，训练/推理端不再依赖 HF 格式。
- **与 PyTorch 框架**：因 hf2mcore 转换脚本中包含 `import torch`（CPU 旁路 NOTE 中），MindSpore 与 PyTorch 共享同一份转换工具；但原文明确"**MindSpore 框架转换出的模型权重无法直接用于 PyTorch 框架训练或推理**"，两者权重不互通。
- **与 Ascend CANN/ATB**：通过 `source /usr/local/Ascend/cann/set_env.sh` 与 `source /usr/local/Ascend/nnal/atb/set_env.sh` 引入底层算子库，是 NPU 训练栈的关键环境变量。

---

## 【使用方法】

> 以下命令/配置均严格取自原文。

### 1. 获取 HuggingFace 权重
```shell
mkdir -p ./model_from_hf/qwen3_hf
cd ./model_from_hf/qwen3_hf
wget https://huggingface.co/Qwen/Qwen3-0.6B/resolve/main/{config.json,generation_config.json,merges.txt,model.safetensors,tokenizer.json,tokenizer_config.json,vocab.json}
sha256sum model.safetensors   # 与 HF 网页公布值比对
```

### 2. HF → Mcore 权重转换
```bash
export CUDA_DEVICE_MAX_CONNECTIONS=1
source /usr/local/Ascend/cann/set_env.sh
python ./mindspeed_llm/mindspore/convert_ckpt.py \
  --use-mcore-models \
  --model-type GPT \
  --load-model-type hf --save-model-type mg \
  --target-tensor-parallel-size 1 --target-pipeline-parallel-size 1 \
  --spec mindspeed_llm.tasks.models.spec.qwen3_spec layer_spec \
  --load-dir ./model_from_hf/qwen3_hf/ \
  --save-dir ./model_weights/qwen3_mcore/ \
  --tokenizer-model ./model_from_hf/qwen3_hf/tokenizer.json \
  --params-dtype bf16 \
  --model-type-hf qwen3 \
  --ai-framework mindspore
bash examples/mindspore/qwen3/ckpt_convert_qwen3_hf2mcore.sh
```
（CPU 侧转换旁路：在 `convert_ckpt.py` 包导入处加 `ms.set_context(device_target="CPU", pynative_synchronize=True)` 与 `torch.configs.set_pyboost(False)`）

### 3. 预训练数据预处理（Alpaca）
```bash
source /usr/local/Ascend/cann/set_env.sh
python ./preprocess_data.py \
  --input ./dataset/train-00000-of-00001-a09b74b3ef9c3b56.parquet \
  --tokenizer-name-or-path ./model_from_hf/qwen3_hf/ \
  --tokenizer-type PretrainedFromHF \
  --handler-name GeneralPretrainHandler \
  --output-prefix ./dataset/alpaca \
  --json-keys text --workers 4 --log-interval 1000
bash examples/mindspore/qwen3/data_convert_qwen3_pretrain.sh
# 产物：./dataset/alpaca_text_document.bin / .idx
```

### 4. 启动预训练
```bash
source /usr/local/Ascend/cann/set_env.sh
source /usr/local/Ascend/nnal/atb/set_env.sh
bash examples/mindspore/qwen3/pretrain_qwen3_0point6b_4K_ms.sh
```
脚本内关键配置：`NPUS_PER_NODE=8 / NNODES=1 / TP=1 / PP=1 / SEQ_LEN=4096 / MBS=1 / GBS=8 / TRAIN_ITERS=2000`，并启用 `--use-mcore-models --disable-bias-linear --group-query-attention --num-query-groups 8 --position-embedding-type rope --bf16 --ai-framework mindspore`。
多机训练：每终端独立启动，仅 `NODE_RANK` 不同；无共享存储时追加 `--no-shared-storage`。

### 5. 微调数据预处理（**原文脚本被截断**）
原文在此处给出脚本编辑路径 `examples/mindspore/qwen3/data_convert_qwen3_instruction.sh`，并已开始展示 bash 片段（含 `mkdir ./finetune_dataset` 与 `--input ./dataset/train-00000-of-00001-a09b74b3ef9c3b56.parquet`），但剩余参数、`Handler` 类型、`.bin/.idx` 产物路径及后续启动微调小节均**未在原文呈现**。按姊妹文档 `data_process_sft_alpaca_style.md` 与"configs/finetune/templates.json"内部链接的提示，可推断应使用 Alpaca 风格 SFT Handler 与对应 prompt 模板，但具体配置项**原文未涉及**，需读者自行参考对应外部文档补齐。

## 图文联合解读

- `running_log.png`: **图文解读：**

图：训练日志显示Qwen3-0.6B在昇腾NPU上成功加载npu_rotary_position_embedding模块，总参数量7.62B（前缀相关性已加载），理论显存约37GB；4次迭代中吞吐量从25.1 TFLOP/s/GPU（warmup）稳定升至约152 TFLOP/s/GPU，loss平稳下降，各rank显存分配正常。

**结论**：Megatron-Mcore格式权重转换正确，NPU预训练流水线可正常收敛并达到稳定算力。

**与文档关系**：印证"权重转换"步骤有效，为"启动训练任务"提供运行验证证据。
