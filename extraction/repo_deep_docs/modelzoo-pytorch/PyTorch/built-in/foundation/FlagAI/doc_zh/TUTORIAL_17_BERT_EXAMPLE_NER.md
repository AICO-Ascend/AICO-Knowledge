# BERT 命名实体识别例子

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_17_BERT_EXAMPLE_NER.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_17_BERT_EXAMPLE_NER.md

# BERT 命名实体识别例子 — 一体化深度解读

---

## 【定位】

这篇文档是 FlagAI 框架下基于 BERT/RoBERTa 模型实现**中文命名实体识别（NER）任务**的端到端实战 guide，描述从数据加载、模型与切词器加载、训练到生成测试的完整流程，作为其文档体系中第 17 篇教程（TUTORIAL_17）的具体实现样例。

---

## 【技术要点】

1. **三种 NER 实现方式**（原文明确列举）：序列标注方法、序列标注+CRF 方法、GlobalPointer 方法；本文以方法 1（纯序列标注）为例。
2. **标签体系（target 列表）**：`["O", "B-LOC", "I-LOC", "B-ORG", "I-ORG", "B-PER", "I-PER"]`，采用 BIO 标注方案，覆盖三类实体：地点（LOC）、组织（ORG）、人名（PER），外加非实体（O），共 7 个类别。
3. **预训练模型选择**：使用 `model_name="RoBERTa-base-ch"`（中文 RoBERTa-base）作为底座，配合 FlagAI 的 `AutoLoader`，通过 `task_name="sequence-labeling"` 触发序列标注任务加载，`class_num=len(target)=7`。
4. **数据格式约定**：每个样本为 `[text, (start, end, label), (start, end, label), ...]` 结构，文本中以 `B-XXX` 表示实体起始、`I-XXX` 表示实体内部，`load_data` 函数据此重建实体 span。
5. **训练超参数**：`batch_size=8`，`gradient_accumulation_steps=1`，`lr=1e-5`，`weight_decay=1e-3`，`epochs=10`，`log_interval=100`，`eval_interval=500`，`save_interval=1`，实验名 `roberta_ner`，保存目录 `checkpoints_ner`。
6. **生成/推理入口**：通过 `model_save_path = "./checkpoints_ner/9000/mp_rank_00_model_states.pt"` 指定 step 9000 的模型权重，运行 `python ./generate.py` 查看输出。

---

## 【关键机制与数据】

**工作原理与数据流**（依据原文梳理）：

1. **数据加载阶段**：原文未给出具体数据量与路径细节，只指出"样例数据在 `/examples/bert_ner/data/`"，并通过 `load_data(filename)` 把字-标签对（每行格式为 `"字符 标签"`，如 `"北 B-LOC"`）按双换行 `\n\n` 分句，按单换行拆字，遇到 `B-` 起新实体、`I-` 扩展前一个实体的右边界 `[1]`，最终产出 `[text, [start,end,label], …]` 形式的样本。

2. **模型加载阶段**：`AutoLoader` 接收 `task_name="sequence-labeling"` 后，从 `./state_dict/` 加载 `RoBERTa-base-ch` 中文权重，并在顶部追加 `class_num=7` 的分类头；`get_model()` 与 `get_tokenizer()` 分别返回模型与切词器。

3. **训练阶段**：使用 `flagai.trainer.Trainer`，device 自适应 `"cuda"` 或 `"cpu"`，每 1 个 epoch 保存一次 checkpoint 到 `checkpoints_ner` 目录。

4. **推理/生成阶段**：加载 step 9000 的 `mp_rank_00_model_states.pt`（从命名看为分布式第 0 rank 的模型状态），调用 `generate.py` 对测试句子做预测。

**性能/规模数据**（仅原文实际出现的）：
- 原文出现训练参数：`batch_size=8`、`epochs=10`、`lr=1e-5`、`weight_decay=1e-3`。
- 原文出现 checkpoint 标识：`9000`（对应 step）和 `mp_rank_00`（对应分布式 rank 0）。
- 原文**未**提供训练时长、F1/Acc 等评测指标、推理耗时等量化性能数据。

**可观察的输出样例**（原文给出的真实运行结果）：

| 输入句子（节选） | 输出实体 |
|---|---|
| "6月15日，河南省文物考古研究所曹操高陵文物队…" | `ORG: ['河南省文物考古研究所', '曹操高陵文物队']` |
| "4月8日，北京冬奥会…习近平总书记…" | `LOC: ['北京','人民大会堂','北京','北京','北京']`; `PER: ['习近平']` |
| "当地时间8日，欧盟委员会表示…" | `ORG: ['欧盟委员会','欧盟']`; `LOC: ['俄罗斯','俄']` |
| "这一盘口状态下英国必发公司亚洲盘交易数据…" | `ORG: ['英国必发公司','博洛尼亚','巴勒莫']` |

---

## 【表格解读】

原文无表格（仅以代码块、列表、文本段落形式给出命令与参数）。原文出现的"表格"型信息是上面我整理的输出样例对照，并非原文自带。

---

## 【公式解读】

原文无公式（含 LaTeX 与伪代码公式均未出现）。

---

## 【关联】

依据文档描述及文末提供的内部链接信息：

- **本文档是《TUTORIAL_17》**，位于 `FlagAI/doc_zh/` 路径下，与 FlagAI 文档体系内其它 tutorial 共同构成 FlagAI 中文使用手册；
- 文中提到的 **"序列标注+CRF 方法"** 与 **"GlobalPointer 方法"** 是同一任务下另外两条路径，本文未展开，需参考 FlagAI 文档体系内的其它专题内容；
- 上游依赖：`flagai.auto_model.auto_loader.AutoLoader`（FlagAI 模型自动加载器）、`flagai.trainer.Trainer`（FlagAI 训练器），均为 FlagAI 框架核心 API；
- 模型资产：`RoBERTa-base-ch` 中文预训练权重位于 `./state_dict/`，训练得到的 NER checkpoint 写入 `./checkpoints_ner/`（由 `Trainer` 的 `save_dir` 决定），推理时取 `./checkpoints_ner/9000/mp_rank_00_model_states.pt`；
- 上下游模块：本文上承 `examples/bert_ner/data/` 下的样例数据，下接 `train.py` 与 `generate.py` 两个可执行脚本；
- 内部链接：原文末尾标注「内部链接: (无)」，故本节内不再补充链接。

---

## 【使用方法】

**启用方式**（按原文给出的步骤）：

1. **数据准备**：样例数据位于 `/examples/bert_ner/data/`，按 `load_data(filename)` 约定的「字+空格+标签」格式组织。
2. **模型与切词器加载**：
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
3. **训练**：在命令行执行 `python ./train.py`，并按需调整以下 Trainer 参数：
   - `env_type="pytorch"`
   - `experiment_name="roberta_ner"`
   - `batch_size=8`
   - `gradient_accumulation_steps=1`
   - `lr=1e-5`
   - `weight_decay=1e-3`
   - `epochs=10`
   - `log_interval=100`
   - `eval_interval=500`
   - `load_dir=None`
   - `pytorch_device=device`（`cuda` 优先，否则 `cpu`）
   - `save_dir="checkpoints_ner"`
   - `save_interval=1`
4. **推理/生成**：将 `model_save_path` 指向 `./checkpoints_ner/9000/mp_rank_00_model_states.pt`，执行 `python ./generate.py` 查看运行结果。

**关于其它两种 NER 方式的启用**：原文未涉及「序列标注+CRF」与「GlobalPointer」方式的具体启用步骤，需参考 FlagAI 文档体系内其它专题（原文未给出内部链接）。
