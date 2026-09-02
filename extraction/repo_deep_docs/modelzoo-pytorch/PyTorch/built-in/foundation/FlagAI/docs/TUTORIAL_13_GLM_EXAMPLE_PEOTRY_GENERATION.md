# GLM example: Classical Chinese Poetry Generation

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_13_GLM_EXAMPLE_PEOTRY_GENERATION.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_13_GLM_EXAMPLE_PEOTRY_GENERATION.md

# 一体化深度解读:GLM 古诗生成示例指南

## 【定位】
这篇文档是 FlagAI/modelzoo-pytorch 仓中 GLM (General Language Model) 在**中文古典诗词生成** (Classical Chinese Poetry Generation) 任务上的端到端教程,说明如何基于 `examples/glm_poetry_generation` 下的 `train.py` 与 `generate.py` 完成"标题+格律 → 诗体"的 seq2seq 训练与推理,并给出训练超参、collate_fn 实现、AutoLoader 用法及两种解码方式 (随机采样/Beam Search) 的调用示例。

---

## 【技术要点】

1. **任务范式**:将诗题与体裁拼接为 `title:style`(如 `桃花:七言绝句`)作为 **src**,将整首诗作为 **tgt**,以 seq2seq 形式送入 GLM,对应 `AutoLoader("seq2seq", model_name="GLM-large-ch", ...)`。
2. **诗体四分类**:依据行数 (绝句 4 句 / 律诗 8 句) 与每句字数 (5 字 / 7 字) 划分出 **wujue、wulv、qijue、qilv** 四类,以中文章符 `:` 分隔 title 与 style 写入 src。
3. **数据预处理细节**:title 超过 **20 字符**会被截断 (`title = title[:20]`);`:` 多次出现时取首段为 title、末段为 style;`src` 与 `tgt` 行数必须相等 (有 `assert`)。
4. **Dataset 与动态 Padding**:`GLMPoetryDataset` 调用 `tokenizer.encode_plus(source_text, target_text=target_text)` 得到 `input_ids/target_ids/position_ids/attention_mask/loss_mask`;`GLMPoetryDynamicCollateFN` 以 batch 内最大长度为基准分别 pad 五类张量 (`pad_id` 来自 `tokenizer.get_command_id('pad')`)。
5. **Position ID 的特殊 Padding**:`pad_position_ids` 对 `position_ids[0]` 续接 `len+0..pad_len-1`,对 `position_ids[1]` 续接 `1`,反映 GLM 的二维 block/位置编码 (下文逐行说明)。
6. **训练超参与生成解码**:训练 batch=4、lr=2e-4、weight_decay=2e-8、epochs=100、log_interval=10、save_interval=1、eval_interval=2000000 (即默认关闭评估);生成时随机采样参数 `top_k=10, top_p=0.1, temperature=1.2, repetition_penalty=4.0, out_max_length=66`,Beam Search 参数 `beam_size=10, out_max_length=66`。

---

## 【关键机制与数据】

- **数据流** (原文):
  1. `read_file()` 从两个文本分别读取 `src`(标题+体裁)与 `tgt`(诗正文),过滤并对齐长度;
  2. `GLMPoetryDataset.__getitem__` 把单条 src/tgt 经 `tokenizer.encode_plus(...)` 编码成 GLM 输入字段;
  3. `GLMPoetryDynamicCollateFN.__call__` 在 batch 内取 `max_length` 后对 5 类字段执行右侧 pad,并组装为 `torch.LongTensor`;
  4. `Trainer` 以 `model`、`train_dataset`、`collate_fn=my_collate_fn` 完成训练。
- **二维位置编码填充** (原文):`pad_position_ids` 中 `position_ids[0]` 接续为 `[len+0, len+1, ..., len+pad_len-1]`(主位置递增),`position_ids[1]` 全填 `1`(第二维位置统一标记),与 GLM 在生成式任务里 block 维度为 1 的设定一致。
- **生成解码** (原文):`predict_generate_randomsample` 与 `predict_generate_beamsearch` 共享 `out_max_length=66`(覆盖一首七律 ≤56 字加标点的余量);随机采样引入 **repetition_penalty=4.0** 抑制诗中重复字/词,`temperature=1.2` 抬高分布多样性,`top_k=10 & top_p=0.1` 实现截断式核采样。
- **原文样例输出** (原文):输入 `"桃花:七言绝句"` → 输出 `"可怜含笑向春风,刚种桃花欲待红。今日流莺来旧处,百般言语是墙东。"`(4 句七言,与 qijue 体裁对应)。
- **性能数据**:原文未涉及训练耗时/资源/指标数字,仅以 `tb summary` 形式建议可视化路径 (`tensorboard_dir="tbsummary"`)。

---

## 【表格解读】

|          | Jueju (绝句) | Lvshi (律诗) |
|----------|--------------|--------------|
| five characters (五字) | wujue (五绝) | wulv (五律) |
| seven characters (七字) | qijue (七绝) | qilv (七律) |

**逐行解读**:
- **表头**:行 = 每句字数 (5 / 7),列 = 全诗行数 (绝句 4 句 / 律诗 8 句),交叉单元格即古诗的四种标准体裁名。
- **第一行 five characters × Jueju = wujue**:五言绝句,共 4 句 × 5 字 = 20 字。
- **第一行 five characters × Lvshi = wulv**:五言律诗,共 8 句 × 5 字 = 40 字。
- **第二行 seven characters × Jueju = qijue**:七言绝句,共 4 句 × 7 字 = 28 字。
- **第二行 seven characters × Lvshi = qilv**:七言律诗,共 8 句 × 7 字 = 56 字 (对应生成参数 `out_max_length=66` 留出标点冗余)。

---

## 【公式解读】

原文无公式。

(说明:文档内出现的仅为 Python 代码片段中的赋值表达式与超参数字,无 LaTeX 或伪代码形式的公式。)

---

## 【关联】

- **上游模型**:通过 `flagai.auto_model.auto_loader.AutoLoader` 加载 `GLM-large-ch`,沿用仓内 GLM 系列预训练权重 (`config.json / pytorch_model.bin / vocab.txt`),属于 FlagAI "foundation" 目录中通用语言模型的下游应用分支。
- **下游组件**:
  - `tokenizer.encode_plus(...)`:与 FlagAI 通用 tokenizer 体系对接,提供 GLM 任务所需的 `input_ids/target_ids/position_ids/attention_mask/loss_mask` 五元组;
  - `flagai.trainer.Trainer`:与文档中其它教程 (`train.py`) 共享同一训练入口,通过 `env_type="pytorch"` 接入 PyTorch 后端;
  - 生成侧 `predict_generate_randomsample / predict_generate_beamsearch` 与仓内其它 GLM 推理示例共享同一 `predictor` 抽象。
- **数据来源**:`FlagAI/examples/glm_poetry_generation/data/` 下的样本语料,标题/体裁以中文冒号 `:` 分隔(注意是全角`：`而非半角`:`),是后续 `train.py`/`generate.py` 默认输入格式。
- **内部链接**:原文无内部链接引用。

---

## 【使用方法】

**1. 训练入口** (原文):
```commandline
cd ./examples/glm_poetry_generation
python ./train.py
```

**2. 关键配置项** (原文 `Trainer(...)` 字段):
| 配置项 | 值 | 说明 |
|---|---|---|
| env_type | "pytorch" | 后端 |
| experiment_name | "glm_poetry" | 实验名 |
| batch_size | 4 | 批大小 |
| gradient_accumulation_steps | 1 | 梯度累积 |
| lr | 2e-4 | 学习率 |
| weight_decay | 2e-8 | 权重衰减 |
| epochs | 100 | 总 epoch |
| log_interval | 10 | 日志间隔 |
| tensorboard_dir | "tbsummary" | TB 路径 |
| eval_interval | 2000000 | 评估间隔(原文设定值,实际基本禁用评估) |
| load_dir | None | 断点续训目录(默认从零) |
| save_dir | "checkpoints_poetry" | 权重保存目录 |
| save_interval | 1 | 保存间隔 |

**3. 生成入口** (原文):需先在 `generate.py` 中修改 `model_dir` (权重目录) 与 `model_save_path` (训练后权重路径),然后:
```commandline
cd ./examples/glm_poetry_generation
python ./generate.py
```
两种解码调用 (原文):
```python
predictor.predict_generate_randomsample(
    text, out_max_length=66, top_k=10, top_p=.1,
    repetition_penalty=4.0, temperature=1.2)

predictor.predict_generate_beamsearch(
    text, out_max_length=66, beam_size=10)
```

**4. 输入约定** (原文):推理 `text` 应形如 `"桃花:七言绝句"`(中文全角冒号 `：` 分隔 title 与 style),与 `read_file()` 中 `line.split("：")` 的解析逻辑保持一致。
