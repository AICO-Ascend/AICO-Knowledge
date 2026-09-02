# pack模式预训练数据集处理

> 仓 `mindspeed` · 路径 `docs/zh/features/preprocess-eod-data.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/preprocess-eod-data.md

# MindSpeed pack模式预训练数据集处理 深度解读

## 【定位】

这篇文档解决在 pack 模式（多文档拼接）预训练中如何通过 **离线数据预处理** 显式插入 EOD token 并按需 pad 序列长度，从而在训练时实现**文档级 attention 隔离**并加速长序列并行场景下 `megatron_cp_algo` 的运行效率。

---

## 【技术要点】

1. **EOD 边界显式标记**：在每条样本末尾通过 `--append-eod` 显式插入 EOD token，防止模型将不同样本/文档视为连续序列并建立跨文档上下文依赖，为后续 `reset-attention-mask` / `reset-position-ids` 提供边界依据。
2. **离线 pad 加速**：通过 `--pad-to-multiple-of 8` 在预处理阶段把每条数据长度 pad 到指定倍数，可将长序列并行（`megatron_cp_algo` + EOD Reset 场景）原本需在线执行的子序列 padding 提前到离线完成，节约在线 pad 时间。
3. **多格式数据接入**：`preprocess_data.py` 的 `--input` 接受目录或单文件，支持 `.parquet`、`.csv`、`.json`、`.jsonl`、`.txt`、`.arrow` 六种格式，同一目录内格式需一致。
4. **Handler 解耦数据风格**：默认 `GeneralPretrainHandler` 提取 `text` 列，配合 `--json-keys text [input output ...]` 支持多列输入；tokenizer 通过 `--tokenizer-type PretrainedFromHF` + `--tokenizer-name-or-path` 接入 HuggingFace tokenizer。
5. **并行预处理**：`--workers 4` 控制并行进程数，`--log-interval 1000` 控制日志打印频率；输出产物固定为 `<prefix>_text_document.bin` / `<prefix>_text_document.idx` 两个文件，训练时仅需把 `<prefix>` 传入 `--data-path`。
6. **与 EOD Reset 训练的协同**：预处理结果需配合训练侧三个开关联合使用——`--reset-attention-mask`、`--reset-position-ids`、`--attention-mask-type causal|general`，二者共同构成完整的"文档级隔离"链路。

---

## 【关键机制与数据】

### 数据流

```
原始数据 (.parquet/.json/.jsonl/.csv/.txt/.arrow)
    │
    ▼  preprocess_data.py
    ├── GeneralPretrainHandler  解析 text 列
    ├── HF Tokenizer (PretrainedFromHF)  tokenize
    ├── --append-eod  在每条样本末尾追加 EOD token
    ├── --pad-to-multiple-of N  每条数据长度 pad 到 N 的倍数
    ▼
输出: ./dataset/alpaca_llama2_7b_text_document.{bin, idx}
    │
    ▼  训练时 --data-path 传入 prefix
    ├── --reset-attention-mask / --reset-position-ids  在 EOD 处重置
    └── --attention-mask-type causal | general
```

### 关键参数（原文给出）

- `--append-eod`：文档级隔离的基础开关，原文明确其作用为"将文档结束标记 EOD 显式地添加到每条数据的末尾，防止模型学习无意义的关联"。
- `--pad-to-multiple-of`：离线 pad 开关；推荐值 **CP × lcm(2, TP)**（与在线 pad 公式一致）。
- 未设置 `--pad-to-multiple-of` 时（原文）："对于 `--attention-mask-type` 为 causal 的情况，因为内部实现的需求，每个子序列的长度会被**在线 pad 到 CP × lcm(2, TP) 的倍数**，其中 lcm 为最小公倍数"。

### 性能/行为差异（原文明确给出的对照）

| 场景 | 行为 | 性能/精度影响 |
|---|---|---|
| 未设 `--pad-to-multiple-of` | 在线 pad 每个子序列到 CP × lcm(2, TP) 倍数 | 多花在线 pad 时间 |
| 设置 `--pad-to-multiple-of = CP × lcm(2, TP)` | 预处理阶段离线完成等量 pad | 节约在线 pad 时间、加速训练 |
| 两者对比 | 每个 batch 样本构成存在差异 | "二者在精度上并不能完全对齐" |

> 注：原文未给出具体的加速倍率/吞吐数字，故不臆造。

---

## 【表格解读】

**原文无表格。**

文档以命令、参数列表和文字对照形式呈现，未包含 markdown 表格。"参数说明"部分以无序列表形式列出各 flag 的含义，可视为参数清单而非结构化表格。

---

## 【公式解读】

**原文无公式。**

文档中唯一出现的"算式"为 `CP × lcm(2, TP)`，以纯文本形式给出，表示"上下文并行度 × (2 与张量并行度的最小公倍数)"——这是 `--pad-to-multiple-of` 的推荐取值，也是未设该参数时在线 pad 的目标倍数。该表达式已在上节"关键机制与数据"中解释，此处不单列 LaTeX 形式。

---

## 【关联】

文档内部没有提供超链接形式的内部关联（"内部链接: (无)"），但从内容可梳理出以下模块级上下游关系：

1. **上游 — 数据来源**：HuggingFace 社区（如 `tatsu-lab/alpaca`）或 ModelScope 上的 parquet/csv/json 等原始数据 → 作为 `preprocess_data.py` 的输入。
2. **同模块协同 — 训练侧开关**：本文档的预处理产出必须在训练脚本中配合 **EOD Reset 训练场景** 的一组开关使用：
   - `--reset-attention-mask`
   - `--reset-position-ids`
   - `--attention-mask-type causal | general`
   这些开关负责在 EOD 位置重置 attention mask 与 position ids，正是预处理阶段插入 EOD token 的"消费方"。
3. **下游加速 — 长序列并行**：`pad-to-multiple-of` 的取值与 `megatron_cp_algo`（Megatron Context Parallel 算法）的子序列切分强绑定，二者取值需保持 `CP × lcm(2, TP)` 一致，才能避免精度 gap 的同时获得加速收益。
4. **tokenizer 依赖**：依赖 HuggingFace tokenizer（`--tokenizer-type PretrainedFromHF` + `--tokenizer-name-or-path ./model_from_hf/llama-2-7b-hf`），需提前准备好对应 HF 模型目录。
5. **精度取舍提示**：原文"注意事项"明确指出，是否使能 `pad-to-multiple-of` 会导致在线训练时每个批样本存在差异，"二者在精度上并不能完全对齐"——这是与精度敏感评测对齐相关联的注意点。

---

## 【使用方法】

### 1. 环境准备（原文给出）

```shell
source /usr/local/Ascend/ascend-toolkit/set_env.sh
cd Megatron-LM
mv ../MindSpeed/tools/preprocess_data.py .
mv ../MindSpeed/tools/data_handler.py .
```

### 2. 下载数据（原文给出，可替换为 ModelScope 镜像）

```shell
mkdir dataset
cd dataset/
wget https://huggingface.co/datasets/tatsu-lab/alpaca/blob/main/data/train-00000-of-00001-a09b74b3ef9c3b56.parquet
cd ..
```

### 3. 执行 pack 模式预处理（原文给出）

```shell
python ./preprocess_data.py \
    --input ./dataset/train-00000-of-00001-a09b74b3ef9c3b56.parquet \
    --tokenizer-name-or-path ./model_from_hf/llama-2-7b-hf \
    --tokenizer-type PretrainedFromHF \
    --handler-name GeneralPretrainHandler \
    --output-prefix ./dataset/alpaca_llama2_7b \
    --append-eod \
    --pad-to-multiple-of 8 \
    --json-keys text \
    --workers 4 \
    --log-interval 1000
```

### 4. 训练侧配套开关（原文给出，启用 EOD Reset）

```text
--reset-attention-mask
--reset-position-ids
--attention-mask-type causal    # 或 general
--data-path ./dataset/alpaca_llama2_7b_text_document
```

### 5. 配置项速查（原文完整列出）

| 参数 | 含义 / 取值 |
|---|---|
| `--input` | 数据集目录或具体文件，支持 `.parquet/.csv/.json/.jsonl/.txt/.arrow`，同一目录下格式需一致 |
| `--handler-name` | 默认 `GeneralPretrainHandler`，提取 `text` 列 |
| `--json-keys` | 待提取列名列表，默认 `text`，可多列如 `--json-keys text input output` |
| `--append-eod` | 在每条数据末尾追加 EOD token，开启文档级隔离 |
| `--pad-to-multiple-of` | 离线将每条数据长度 pad 到该值的倍数；推荐取 `CP × lcm(2, TP)` 以加速 `megatron_cp_algo` |
| `--tokenizer-name-or-path` | HF tokenizer 路径 |
| `--tokenizer-type` | `PretrainedFromHF` |
| `--output-prefix` | 输出前缀，最终文件为 `<prefix>_text_document.{bin, idx}` |
| `--workers` | 并行进程数，示例 `4` |
| `--log-interval` | 日志间隔，示例 `1000` |

### 6. 精度提示（原文"注意事项"）

> 在构建 pack 模式数据集时，是否使能 `pad-to-multiple-of` 参数会导致在线训练时每个批样本中存在一定差异，因此二者在精度上并不能完全对齐。

如需在精度敏感的评测场景下与未 pad 版本对齐，需谨慎评估或统一两侧配置。

## 图文联合解读

- `append-eod.png`: 图中展示两条流水线：
1) `--append-eod`：在每条样本末尾追加EOD边界符；
2) `--pad-to-multiple-of`：先将样本pad至N的倍数再追加EOD。

**论证**：EOD显式标记样本边界，使模型能在该处重置attention mask与position_ids，实现文档级注意力隔离，提升token利用率。

**与文档关系**：图解"解决方案"中两个核心预处理参数的可视化流程，印证pack+EOD是文档隔离与离线pad加速训练的关键机制。
