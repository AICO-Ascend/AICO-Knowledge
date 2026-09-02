# BERT NER

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_17_BERT_EXAMPLE_NER.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_17_BERT_EXAMPLE_NER.md

# BERT NER 教程文档深度解读

## 【定位】

本文档描述如何在 FlagAI 框架下使用 **BERT（本文档实际采用的是 RoBERTa-base-ch）** 模型完成**中文命名实体识别（NER）**任务，以「序列标注」方式为示例，涵盖数据加载、模型装载、训练与生成推理的全流程示例代码与命令。

---

## 【技术要点】

1. **支持的三种 NER 实现方式**：原文明确指出 BERT 模型支持 (1) 序列标注、(2) 序列标注 + CRF、(3) GlobalPointer；本教程采用方法 1（序列标注）。
2. **标注体系（target/标签集）**：`target = ["O", "B-LOC", "I-LOC", "B-ORG", "I-ORG", "B-PER", "I-PER"]`，即标准的 BIO 体系，覆盖 3 类实体：**LOC（地点）、ORG（机构）、PER（人物）**，共 7 个标签。
3. **预训练模型**：`model_name="RoBERTa-base-ch"`（中文 RoBERTa-base），通过 `AutoLoader` 自动装载，模型权重目录为 `./state_dict/`，`class_num=len(target)=7`。
4. **数据格式与解析**：单条样本形如 `[text, (start, end, label), (start, end, label), ...]`；原始文件采用「逐字符 + 标签」两列（以空格分隔、句子间空行分隔）的 BMES-like 格式（原文使用 B/I 标志）；加载时按字符拼接成完整文本，并依据 `B`/`I` 标志生成实体区间。
5. **训练超参（Trainer 配置）**：`env_type="pytorch"`、`experiment_name="roberta_ner"`、`batch_size=8`、`gradient_accumulation_steps=1`、`lr=1e-5`、`weight_decay=1e-3`、`epochs=10`、`log_interval=100`、`eval_interval=500`、`load_dir=None`、`save_dir="checkpoints_ner"`、`save_interval=1`；训练入口命令为 `python ./train.py`。
6. **推理与可视化**：通过 `generate.py` 调用，指定训练后权重路径 `model_save_path = "./checkpoints_ner/9000/mp_rank_00_model_states.pt"`，运行命令为 `python ./generate.py`。

---

## 【关键机制与数据】

- **数据流**：原始样本文件（位于 `/examples/bert_ner/data/`）→ `load_data(filename)` 解析 → 转为 `[text, (start, end, label), ...]` 列表 → 经 `AutoLoader` 装载的 `tokenizer` 编码 → `model` 前向得到序列标注 → 后处理得到实体（区间 + 类型）。
- **BIO 解析逻辑**（原文代码语义）：
  - `flag[0]=='B'`：开启新实体，记录 `(start=i, end=i, label=flag[2:])`；
  - `flag[0]=='I'`：将当前最后一个实体的 `end` 更新为 `i`；
  - 由此**连续 I 标签会扩展同一实体的 end 索引**，实现 BIO 合并。
- **示例输入**：4 条中文测试语句（新闻文本，涉及人物、地点、机构名）。
- **示例输出（原文标注）**：
  - 第 1 条 → `{'ORG': ['河南省文物考古研究所', '曹操高陵文物队']}`
  - 第 2 条 → `{'LOC': ['北京', '人民大会堂', '北京', '北京', '北京'], 'PER': ['习近平']}`
  - 第 3 条 → `{'ORG': ['欧盟委员会', '欧盟'], 'LOC': ['俄罗斯', '俄']}`
  - 第 4 条 → `{'ORG': ['英国必发公司', '博洛尼亚', '巴勒莫']}`
- **性能数据**：原文未给出 F1、准确率、loss 曲线等任何性能指标，仅展示定性样例。

---

## 【表格解读】

**原文无表格**。原文中出现的最接近表格的结构是 `target` 标签列表，可视为标签定义：

| 标签 | 含义 |
|---|---|
| `O` | 非实体（Outside） |
| `B-LOC` | 地点类实体起始（Begin-Location） |
| `I-LOC` | 地点类实体内部/结束（Inside-Location） |
| `B-ORG` | 机构类实体起始（Begin-Organization） |
| `I-ORG` | 机构类实体内部/结束（Inside-Organization） |
| `B-PER` | 人物类实体起始（Begin-Person） |
| `I-PER` | 人物类实体内部/结束（Inside-Person） |

该列表定义了 3 类实体共 7 个标签，序列标注任务的解码与后处理均以此集合为闭域。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

原文未提供内部链接或上下游章节指引，可推断的关联关系（基于仓库命名与代码引用）：

- **数据目录依赖**：`/examples/bert_ner/data/`，与训练入口 `train.py`、推理入口 `generate.py` 同属 `bert_ner` 示例目录。
- **预训练权重依赖**：`./state_dict/` 需事先存在 `RoBERTa-base-ch` 的模型权重（由 FlagAI 模型仓库提供）；`class_num=len(target)` 与 `target` 列表强耦合。
- **Trainer 依赖**：使用 `flagai.trainer.Trainer`，属于 FlagAI 通用训练器，与其他任务（如分类、问答）的训练脚本共享同一套 Trainer 配置语义。
- **未在本教程中涉及**：方法 2（CRF）与方法 3（GlobalPointer）的实现细节，原文仅在 Background 中提及，未给出对应脚本路径或链接。

---

## 【使用方法】

**1. 数据加载**
- 数据位置：`/examples/bert_ner/data/`
- 自定义 `load_data(filename)` 函数，文件按「字符 标签」逐行书写、句子间空行分隔；函数返回 `[[text, [start,end,label], ...], ...]` 形式。

**2. 模型与分词器装载**
```python
from flagai.auto_model.auto_loader import AutoLoader
task_name = "sequence-labeling"
model_dir = "./state_dict/"
target = ["O", "B-LOC", "I-LOC", "B-ORG", "I-ORG", "B-PER", "I-PER"]
auto_loader = AutoLoader(task_name,
                         model_name="RoBERTa-base-ch",
                         model_dir=model_dir,
                         class_num=len(target))
model = auto_loader.get_model()
tokenizer = auto_loader.get_tokenizer()
```

**3. 训练**
- 命令行：`python ./train.py`
- Trainer 关键配置：`batch_size=8`、`gradient_accumulation_steps=1`、`lr=1e-5`、`weight_decay=1e-3`、`epochs=10`、`log_interval=100`、`eval_interval=500`、`load_dir=None`、`save_dir="checkpoints_ner"`、`save_interval=1`。

**4. 推理（生成）**
- 修改权重路径：`model_save_path = "./checkpoints_ner/9000/mp_rank_00_model_states.pt"`
- 命令行：`python ./generate.py`
- 输出格式为字典：`{实体类型: [实体文本列表]}`，例如 `{'ORG': ['欧盟委员会', '欧盟'], 'LOC': ['俄罗斯', '俄']}`。
