# GLM 例子：标题生成

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_12_GLM_EXAMPLE_TITLE_GENERATION.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_12_GLM_EXAMPLE_TITLE_GENERATION.md

# 一体化深度解读：GLM 例子：标题生成

## 【定位】
本文档是 FlagAI/modelzoo 中针对中文长文本摘要（标题生成）任务的端到端教程：演示如何以 `GLM-large-ch` 为基座模型，从数据加载、模型与分词器加载、训练到推理生成，完成一个"输入正文 → 输出标题"的完整 Pipeline；并提示可替换为更大的 `GLM-10b-ch`（百亿参数）以提升效果。

---

## 【技术要点】
1. **任务定义**：序列到序列生成，输入一段正文文本，模型输出对应标题；属于条件文本生成任务。
2. **基座模型**：默认使用 `GLM-large-ch`；支持替换为 `GLM-10b-ch`（百亿参数，需在外部 BAAI 模型详情页 100001 获取）。
3. **数据组织**：`/examples/glm_title_generation/data/` 下放置 `train.src`（正文）与 `train.tgt`（目标标题），按行一一对应。
4. **数据处理**：`read_file()` 用 `.lower()` 归一化文本并按 `\n` 切分；自定义 `GLMTitleGenerationDataset` 调用 `tokenizer.encode_plus(source_text, target_text=target_text)` 同时编码源与目标；`GLMTitleGenerationCollateFN` 在 batch 内对 `input_ids / target_ids / position_ids / loss_mask / attention_mask` 按本批最大长度 `max_length` 填充（`pad_id` 取自 `tokenizer.get_command_id('pad')`）。
5. **模型与分词器加载**：通过 `flagai.auto_model.auto_loader.AutoLoader("title-generation", model_name="GLM-large-ch", model_dir="./state_dict/glm/")` 自动构建；要求目录内含 `1.config.json / 2.pytorch_model.bin / 3.vocab.txt`，缺失时自动从 modelhub 拉取。
6. **训练超参（Trainer）**：`batch_size=1, gradient_accumulation_steps=1, lr=2e-4, weight_decay=1e-3, epochs=10, log_interval=10, eval_interval=10000, load_dir=None, save_dir="checkpoints", save_interval=1, num_checkpoints=1`。
7. **推理（generate.py）**：提供两种解码方式 —— 随机抽样 `predict_generate_randomsample`（`out_max_length=66, top_k=10, top_p=0.1, repetition_penalty=4.0, temperature=1.2`）与集束搜索 `predict_generate_beamsearch`（`out_max_length=66, beam_size=10`）。

---

## 【关键机制与数据流】

### 工作原理与数据流（原文语义）
1. **数据加载**：`read_file()` 逐行读取 `train.src` / `train.tgt`，去除换行并 `.lower()`，分别构造源列表 `src` 与目标列表 `tgt`；原文注释明确"换为其他数据时只需修改处理方式，构造好 src 与对应 tgt 列表即可"。
2. **样本编码**：`GLMTitleGenerationDataset.__getitem__` 中 `tokenizer.encode_plus(source_text, target_text=target_text)` 一次性产出包含 `input_ids / target_ids / position_ids / attention_mask / loss_mask` 的字典。
3. **批内对齐（collate_fn）**：
   - `pad_token`：用 `pad_id` 在尾部填充到本批 `max_length`；
   - `pad_position_ids`：第一段位置 id 用 `[len+0, len+1, ..., len+pad_len-1]` 续接，第二段用 `[1]*pad_len`（块状相对位置标记的占位）；
   - `pad_loss_mask`：用 `0` 填充，使填充部分不参与 loss 计算。
4. **训练驱动**：`Trainer(env_type="pytorch", pytorch_device=device, ...)` 接收 `model / train_dataset / collate_fn=my_collate_fn` 启动训练，按 `save_interval` 与 `num_checkpoints=1` 保留检查点。
5. **推理生成**：`predictor` 提供两种解码器 —— `predict_generate_randomsample`（带 `top_k / top_p / temperature / repetition_penalty` 的截断采样）与 `predict_generate_beamsearch`（固定束宽的集束搜索），输出最大长度均为 `66`。

### 原文：示例结果（Input / Output 对照）
输入三段中文长文本，输出均为简短标题，且原文示例输出的字与字之间均带**空格分隔**：

| 输入主题 | 原文输出标题 |
|---|---|
| 可穿戴产品设计十原则 | `可 穿 戴 产 品 设 计 原 则 十 大 原 则` |
| 乔布斯与 iPhone 改变世界 | `乔 布 斯 宣 布 iphone 8 年 后 将 成 为 个 人 电 脑` |
| 雅虎剥离阿里巴巴股权 | `雅 虎 拟 剥 离 阿 里 巴 巴 15 ％ 股 权` |

> 原文仅展示该三组样例，未给出评测指标（BLEU/ROUGE 等）与训练耗时/吞吐等性能数据。

---

## 【表格解读】
原文无表格（无参数表、无性能对比表、无配置表）。可结构化信息均以代码片段形式呈现，关键参数已在【技术要点】中逐条列出。

---

## 【公式解读】
原文无公式。

> 涉及数学/算法过程的描述仅为 `pad_position_ids` 中的列表生成式：
> - `position_ids[0] += [len(position_ids[0]) + x for x in range(pad_len)]`：对第一段位置 id 在原长度 `len` 之上从 `0` 递增补齐到 `max_length`；
> - `position_ids[1] += [1] * pad_len`：对第二段位置 id 全部填 `1`（即 GLM 块状相对位置中"段内相对位置"的占位约定）。
>
> 上述为**实现细节**，不是公式，未在原文中以数学形式给出。

---

## 【关联】
- **依赖上游/工具链**：
  - `flagai.auto_model.auto_loader.AutoLoader`：根据 `task_name="title-generation"` 与 `model_name="GLM-large-ch"` 自动装配模型与分词器；
  - `flagai.trainer.Trainer`：通用训练驱动器，屏蔽 env_type / device / 梯度累积 / checkpoint 等细节；
  - 分词器需提供 `encode_plus(source, target=...)` 与 `get_command_id('pad')` 接口（FlagAI GLM 套件特性）。
- **模型入口与切换**：原文给出从 `GLM-large-ch` 切换到 `GLM-10b-ch` 的外链入口（`https://model.baai.ac.cn/model-detail/100001`），指向 BAAI ModelHub 中 ID 为 100001 的资源页；该链接为本节唯一的外部引用。
- **目录定位**：训练与生成脚本均位于仓内 `./examples/glm_title_generation/` 路径下；模型权重位于 `./state_dict/glm/`，checkpoint 输出至 `save_dir="checkpoints"`。
- **任务类比**：与同仓内的 BERT 标题生成（文档配图 `./img/bert_title_generation_model.png`）共享"输入正文 → 输出标题"的范式，但底层实现采用 GLM 的自回归空白填充预训练范式。

---

## 【使用方法】

### 训练
```commandline
cd ./examples/glm_title_generation
python ./train.py
```
前置准备：
1. 将训练数据放入 `/examples/glm_title_generation/data/`：正文行写入 `train.src`，对应标题行写入 `train.tgt`（一行一条，`src[i]` 与 `tgt[i]` 对齐）；
2. 准备 `model_dir`（默认 `./state_dict/glm/`），确保含 `config.json / pytorch_model.bin / vocab.txt`；缺失时 `AutoLoader` 会自动从 modelhub 下载；
3. 训练参数默认：`batch_size=1, gradient_accumulation_steps=1, lr=2e-4, weight_decay=1e-3, epochs=10, log_interval=10, eval_interval=10000, save_interval=1, num_checkpoints=1`，可在 `Trainer(...)` 实例化处调整。

### 推理（生成）
运行前需修改 `generate.py` 中的两个路径：
- `model_dir`：模型配置所在目录；
- `model_save_path`：训练后得到的 checkpoint 路径。

```commandline
cd ./examples/glm_title_generation
python ./generate.py
```

解码方式（二选一）：
```python
# 随机抽样 + 截断采样
predictor.predict_generate_randomsample(
    text,
    out_max_length=66,
    top_k=10,
    top_p=0.1,
    repetition_penalty=4.0,
    temperature=1.2
)

# 集束搜索
predictor.predict_generate_beamsearch(
    text,
    out_max_length=66,
    beam_size=10
)
```

> 注：`out_max_length / top_k / top_p / repetition_penalty / temperature / beam_size` 等参数为 FlagAI GLM 推理接口内置，文档中给出的是示例值，可按需调整。文档原文未给出推荐 GPU 型号、显存需求、推理时延、吞吐或评测分数等基准数据。
