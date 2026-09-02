# GLM 例子：古诗生成

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_13_GLM_EXAMPLE_PEOTRY_GENERATION.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_13_GLM_EXAMPLE_PEOTRY_GENERATION.md

# 一体化深度解读：GLM 古诗生成教程

## 【定位】
这篇文档解决"如何基于 FlagAI/GLM 大模型在 `examples/glm_poetry_generation` 路径下完成古诗（绝句/律诗）生成任务"的问题，描述了从背景知识、数据准备、模型加载、训练到随机采样/集束搜索生成的端到端能力。

## 【技术要点】

1. **古诗体裁规范**：绝句 = 4 句，律诗 = 8 句；每句五或七字；共四种类型（五言绝句、五言律诗、七言绝句、七言律诗），原文以表格形式给出。
2. **输入数据格式约定**：`src` 形如 `"春晓：五言绝句"`、`"标题：五言律诗"`，按中文冒号 `：` 切分，标题超过 20 字时截断保留前 20 字；`tgt` 为对应的完整诗句。
3. **数据加载三件套**：`GLMPoetryDataset.__getitem__` 调用 `tokenizer.encode_plus(source_text, target_text=target_text)` 得到 `input_ids / target_ids / position_ids / attention_mask / loss_mask`；`GLMPoetryDynamicCollateFN` 在 batch 内取 `max_length` 后做动态 padding（其中 `position_ids[0]` 续增、`position_ids[1]` 用 1 填充、`loss_mask` 用 0 填充）。
4. **模型加载（AutoLoader）**：从 `model_dir`（含 `config.json / pytorch_model.bin / vocab.txt`）自动构建模型与分词器，task_name=`"poetry"`，model_name=`"GLM-large-ch"`；如需更大规模可换 `GLM-10b-ch`。
5. **训练超参数（Trainer）**：`env_type="pytorch"`，`batch_size=4`，`gradient_accumulation_steps=1`，`lr=2e-4`，`weight_decay=2e-8`，`epochs=100`，`log_interval=10`，`eval_interval=2000000`，`save_interval=1`，checkpoint 写到 `checkpoints_poetry`，tensorboard 写入 `tbsummary`。
6. **两种生成方式**：`predict_generate_randomsample(text, out_max_length=66, top_k=10, top_p=0.1, repetition_penalty=4.0, temperature=1.2)` 与 `predict_generate_beamsearch(text, out_max_length=66, beam_size=10)`。

## 【关键机制与数据】

- **数据流（训练侧）**：`read_file()` 同步读取 `train.src` 与 `train.tgt`，按行解析成对齐的 src/tgt 列表，并通过 `assert len(src) == len(tgt)` 校验对齐；随后被 `GLMPoetryDataset` 包装，逐样本调用 `tokenizer.encode_plus`；最后由 `GLMPoetryDynamicCollateFN`（原文标注："将一批（batch）数据填充（padding）成统一大小"）将每条样本的 `input_ids / target_ids / position_ids / attention_mask / loss_mask` 在 batch 维度上对齐到 `max_length`，并封装成 `torch.LongTensor`。
- **位置编码 padding 策略（原文）**：`position_ids[0]` 填充位置采用 `[len(position_ids[0])+x for x in range(pad_len)]` 递增序列，`position_ids[1]` 填充位用 1 填充；`loss_mask` 填充位用 0 填充以避免 padding 位置参与损失计算。
- **示例输入输出（原文）**：输入 `"桃花：七言绝句"`，输出 `"可怜含笑向春风,刚种桃花欲待红。今日流莺来旧处,百般言语是墙东。"`。
- **示例诗（原文）**：《静夜思》李白 —— "床前明月光，疑是地上霜。举头望明月，低头思故乡。"
- **生成方式选择（原文）**：可选择基于概率筛选的随机抽样（random sample）或集束搜索（beamsearch）两种生成方式。

## 【表格解读】

原文表格逐字还原：

|       | 绝句 | 律诗 |
| :---: | :--- | :--- |
| 五言  | 五言绝句 | 五言律诗 |
| 七言  | 七言绝句 | 七言律诗 |

逐行解读：
- 表头行：列维度为体裁（绝句 / 律诗），行维度为每句字数（五言 / 七言），交叉处为四类古诗命名。
- 第一行（五言 × 绝句 / 律诗）：五言绝句、五言律诗——即每句五字的四句或八句近体诗。
- 第二行（七言 × 绝句 / 律诗）：七言绝句、七言律诗——即每句七字的四句或八句近体诗。
- 表格意义：作为训练/生成任务的"体裁标签"字典，配合 `src` 中的"标题：体裁"格式（如 `"桃花：七言绝句"`）约束模型输出长度与节奏。

## 【公式解读】

原文无公式。

## 【关联】

- **模型与规模**：教程主样例使用 `GLM-large-ch`；文档给出外链 https://model.baai.ac.cn/model-detail/100001 指向更大的 `GLM-10b-ch` 百亿参数模型，并提示"如果想要使用更大规模的百亿参数模型`GLM-10b-ch`请点这里"——即同一脚本可通过替换 model_name 升级到 10B 规模。
- **FlagAI 内部依赖**：`flagai.auto_model.auto_loader.AutoLoader`（自动构建模型与分词器）、`flagai.trainer.Trainer`（封装 env_type、batch_size、lr、epochs、save_dir 等训练参数）。
- **目录与文件**：训练入口 `./examples/glm_poetry_generation/train.py`、生成入口 `./examples/glm_poetry_generation/generate.py`；训练样例数据在 `./examples/glm_poetry_generation/data/` 下的 `train.src` 与 `train.tgt`；模型本地目录 `./state_dict/`。
- **可视化资源**：生成结果示例图 `../docs/img/poetry_generation.png`（以 `![result]` 形式嵌入文档）。

## 【使用方法】

1. **进入示例目录并训练**：
   ```commandline
   cd ./examples/glm_poetry_generation
   python ./train.py
   ```
2. **运行生成脚本**：
   ```commandline
   cd ./examples/glm_poetry_generation
   python ./generate.py
   ```
3. **生成参数**：
   - 随机采样：`predict_generate_randomsample(text, out_max_length=66, top_k=10, top_p=.1, repetition_penalty=4.0, temperature=1.2)`
   - 集束搜索：`predict_generate_beamsearch(text, out_max_length=66, beam_size=10)`
4. **更换数据**：原文提示"如果换为其他数据，修改处理方式即可，只需要构造好 src 以及对应 tgt 列表"。
5. **更换更大模型**：原文未涉及具体配置项切换操作，仅以外链指向 `GLM-10b-ch` 模型下载页。
