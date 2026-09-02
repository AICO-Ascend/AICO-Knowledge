# 快速入门

> 仓 `mindspeed` · 路径 `docs/zh/user-guide/quickstart.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/user-guide/quickstart.md

# 深度解读：MindSpeed 快速入门文档

## 【定位】

本文档是 MindSpeed（昇腾大模型加速库）的**快速入门指南**，面向已完成安装的用户，指导其如何基于 Megatron-LM 在昇腾设备上完成数据准备与预训练启动，从而无缝启用 MindSpeed 所提供的加速与优化能力。

---

## 【技术要点】

1. **适配器导入机制**：必须在 Megatron-LM 的两个入口文件 `pretrain_gpt.py` 与 `tools/preprocess_data.py` 中，于 `import torch` 之下新增一行 `import mindspeed.megatron_adaptor`，使 MindSpeed 在不改动 Megatron-LM 主体源码的情况下完成与昇腾设备的桥接。

2. **硬件与内存约束**：MindSpeed Core 支持 **Ascend 950 系列产品、Atlas A3 训练系列产品、Atlas A2 训练系列产品**，且要求**单 NPU 片上内存 ≥ 64GB**；示例脚本默认 `NPUS_PER_NODE=8`，低于此规格可能触发 OOM。

3. **数据处理链路**：原始 Parquet（Alpaca） → JSON 文本（每行 `{"text": ...}`） → Megatron 二进制格式（`alpaca_text_document.bin` 与 `.idx`），依赖 `nltk pyarrow pandas` 第三方库。

4. **Tokenizer 准备**：使用 GPT2BPETokenizer，需将 `vocab.json` 与 `merges.txt` 放入 `Megatron-LM/gpt-tokenizer` 目录；如 HuggingFace 不可达建议改用 ModelScope 镜像。

5. **预训练分布式拓扑（示例）**：`NPUS_PER_NODE=8`、`NNODES=1`、`WORLD_SIZE=8`、`TP=2`、`PP=2`、`CP=1`、`EP=1`、`MASTER_PORT=6001`，`CUDA_DEVICE_MAX_CONNECTIONS=1`，`torchrun` 启动并以 `nccl` 作为分布式后端。

6. **示例模型超参**：8 层 Transformer，`hidden-size=4096`，`ffn-hidden-size=14336`，`num-attention-heads=64`，`seq-length=4096`，`micro-batch-size=1`，`global-batch-size=16`，`lr=1.0e-6`，`min-lr=1.0e-7`，`train-iters=1000`，`--fp16` 精度训练，并显式禁用 `--no-masked-softmax-fusion` 与启用 `--attention-softmax-in-fp32`。

---

## 【关键机制与数据】

**工作原理 / 数据流（基于原文描述）：**

1. **适配层注入**：MindSpeed 不直接修改 Megatron-LM，而是通过在训练入口脚本中 `import mindspeed.megatron_adaptor`，把昇腾 NPU 的张量/通信算子替换或代理到 Megatron-LM 的运行时路径上。
2. **数据预处理管线**：
   - 依赖安装 → `pip3 install nltk pyarrow pandas`（原文要求）；
   - `pd.read_parquet` 读取 Alpaca → 逐行 `json.dumps({"text": v})` 序列化 → 写入 `alpaca_json.json`；
   - `preprocess_data.py` 在昇腾侧运行（同样需导入 mindspeed 适配器），参数 `--tokenizer-type GPT2BPETokenizer --vocab-file --merge-file --append-eod --workers 8`，输出 `*.bin` + `*.idx` 二进制预训练数据。
3. **预训练启动链路**：`source /usr/local/Ascend/cann/set_env.sh` 加载 CANN 环境变量 → 通过 `torchrun` 拉起 `pretrain_gpt.py` → `train_distributed.sh` 内置 `DISTRIBUTED_ARGS / GPT_ARGS / DATA_ARGS / OUTPUT_ARGS` 四组配置 → 数据划分 `--split 990,5,5`（训练/校验/测试比例）。
4. **环境变量**：`CUDA_DEVICE_MAX_CONNECTIONS=1`（限制每张设备并发连接数，避免与 Megatron-LM 的张量并行流水线调度冲突）。

**性能数据**：原文未给出任何吞吐/加速比/MFU 等定量性能数据，仅在 NOTE 中以**风险提示**形式给出"NPUS_PER_NODE=8 低于此可能 OOM"以及"参数需根据场景适配避免 OOM"。

---

## 【表格解读】

### 表 1：preprocess_data.py 参数说明（原文逐字还原）

| 参数 | 说明 |
|-|-|
| `--input` | 数据集 |
| `--output-prefix` | 处理后的数据集 |
| `--tokenizer-type` | tokenizer 类型 |
| `--vocab-file` | tokenizer 文件 |
| `--merge-file` | tokenizer 文件 |
| `--append-eod` | 添加 \<eod> 结尾 token |
| `--log-interval` | log 迭代数 |
| `--workers` | 并行数 |

**逐行解读：**
- `--input`：指定上一阶段生成的 JSON 语料路径，原文示例为 `alpaca_json.json`。
- `--output-prefix`：二进制输出前缀，原文示例为 `./gpt_pretrain_data/alpaca`（最终产物为 `alpaca_text_document.bin`/`.idx`）。
- `--tokenizer-type`：分词器类型，原文使用 `GPT2BPETokenizer`，与 `vocab.json`/`merges.txt` 配套。
- `--vocab-file` / `--merge-file`：BPE 词表与合并规则文件路径，对应 `gpt-tokenizer/` 目录下的两个文件。
- `--append-eod`：在每个样本末尾附加文档结束符 `<eod>`，Megatron-LM 用以识别样本边界。
- `--log-interval`：每处理多少条样本输出一次进度日志，原文示例值为 `1000`。
- `--workers`：数据预处理的并行进程数，原文示例值为 `8`。

### 表 2：train_distributed.sh 参数配置（原文逐字还原）

| 参数 | 说明 |
|-|-|
| `CKPT_DIR` | 权重文件路径 |
| `VOCAB_FILE` | tokenizer 文件 |
| `MERGE_FILE` | tokenizer 文件 |
| `DATA_PATH` | 数据集文件 |

**逐行解读：**
- `CKPT_DIR=./ckpt`：预训练过程中 checkpoint 的本地保存路径。
- `VOCAB_FILE=./gpt-tokenizer/vocab.json`：训练侧使用的 BPE 词表，与预处理阶段保持一致。
- `MERGE_FILE=./gpt-tokenizer/merges.txt`：训练侧使用的 BPE merges 文件。
- `DATA_PATH=./gpt_pretrain_data/alpaca_text_document`：对应 `preprocess_data.py` 输出的 `_text_document` 前缀路径（脚本会自动追加 `.bin`/`.idx`）。
- 上述四项均为 **Shell 变量**而非命令行 flag，由脚本内 `$VOCAB_FILE` / `$MERGE_FILE` / `$DATA_PATH` 展开后注入 `DATA_ARGS`。

---

## 【公式解读】

**原文无公式。** 文档仅包含 Shell 变量赋值、Python 引用与命令行参数，未出现任何 LaTeX 公式或伪代码公式。

---

## 【关联】

- **install_guide.md**（文末内部链接）：本文档第一步即要求用户"参考 MindSpeed 安装指导"完成环境准备，定位上是 **install_guide → quickstart** 的下游入口文档，二者构成完整上手路径。
- **Megatron-LM 上游仓库**：MindSpeed 通过 `import mindspeed.megatron_adaptor` 适配器模式挂载到 Megatron-LM（NVIDIA 官方仓库）的 `pretrain_gpt.py` 与 `tools/preprocess_data.py` 之上，因此本文档完全以 Megatron-LM 的脚本结构（`GPT_ARGS / DATA_ARGS / DISTRIBUTED_ARGS / OUTPUT_ARGS`）为骨架。
- **CANN 工具链**：通过 `source /usr/local/Ascend/cann/set_env.sh` 引入 CANN 运行环境，是 MindSpeed 在昇腾侧运行的前置依赖。
- **第三方数据/分词器生态**：HuggingFace（GPT-3.5-turbo tokenizer、Alpaca 数据集）与 ModelScope（文档建议的备选镜像）共同构成数据获取链路。
- **同仓其他未直接引用但隐含相关的模块**：MindSpeed Core 对多种并行策略（TP/PP/CP/EP）的加速能力由 quickstart 中 `TP=2 PP=2 CP=1 EP=1` 的示例配置侧面体现，但具体加速模块（如重计算、FlashAttention、ZeRO 等）本文档未展开。

---

## 【使用方法】

**启用方式（均来自原文）：**

1. **环境准备**
   - 参照 `install_guide.md` 完成 MindSpeed 安装。
   - 在 `Megatron-LM/pretrain_gpt.py` 中，于 `import torch` 之下新增 `import mindspeed.megatron_adaptor`。
   - 在 `Megatron-LM/tools/preprocess_data.py` 中同样注入该导入。

2. **数据准备**
   - 创建 `Megatron-LM/gpt-tokenizer/`，放入 `vocab.json` 与 `merges.txt`。
   - 下载 Alpaca Parquet 数据集。
   - `pip3 install nltk pyarrow pandas`。
   - 运行原文提供的 Pandas 脚本将 Parquet 转 JSON。
   - 运行原文提供的 `python tools/preprocess_data.py ...` 命令（参数含 `--input alpaca_json.json --output-prefix ./gpt_pretrain_data/alpaca --tokenizer-type GPT2BPETokenizer --vocab-file ... --merge-file ... --append-eod --log-interval 1000 --workers 8`），生成 `.bin` / `.idx`。

3. **启动预训练**
   - `source /usr/local/Ascend/cann/set_env.sh` 加载 CANN 环境。
   - 在 `Megatron-LM/` 下创建并按原文示例填充 `train_distributed.sh`（含 `NPUS_PER_NODE=8 / TP=2 / PP=2 / CP=1 / EP=1` 等）。
   - 将 `CKPT_DIR / VOCAB_FILE / MERGE_FILE / DATA_PATH` 替换为本地实际路径。
   - 执行 `bash ./train_distributed.sh` 启动分布式预训练。

**配置项/开关（原文涉及的主要 flag）：**
- `--transformer-impl local`：使用本地 Transformer 实现。
- `--tensor-model-parallel-size / --pipeline-model-parallel-size`：TP/PP 并行度。
- `--num-layers-per-virtual-pipeline-stage 1`：虚拟流水线每段层数。
- `--no-masked-softmax-fusion / --attention-softmax-in-fp32`：注意力数值相关开关。
- `--fp16`：半精度训练。
- `--disable-bias-linear`：去除线性层 bias。
- `--initial-loss-scale 4096.0`、`--clip-grad 1.0`、`--lr-warmup-fraction 0.01`：优化与稳定性相关参数。
- `--log-throughput / --log-interval 1 / --save-interval 10000 / --eval-interval 10000 / --eval-iters 10`：日志、checkpoint、评测节奏参数。
- `--split 990,5,5`：训练/校验/测试样本划分比例。
- `--distributed-backend nccl`：分布式通信后端。

> 原文 NOTE 明确提醒：`NPUS_PER_NODE`、hidden-size、num-layers 等参数需根据实际硬件规格与场景适配，避免 OOM。
