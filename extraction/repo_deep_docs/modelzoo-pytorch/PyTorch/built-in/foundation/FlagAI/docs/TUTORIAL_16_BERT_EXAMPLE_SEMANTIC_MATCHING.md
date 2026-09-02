# Bert example: Semantic matching

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_16_BERT_EXAMPLE_SEMANTIC_MATCHING.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_16_BERT_EXAMPLE_SEMANTIC_MATCHING.md

# 一体化深度解读:Bert example: Semantic Matching

---

## 【定位】

这篇文档解决的是**基于预训练语言模型(如 RoBERTa-base-ch)对两个输入句子进行语义等价性判断的二分类任务**,即判断"句子 A 与句子 B 是否表达相同含义",输出 0/1 两类分类结果,并给出了从数据加载、模型构建、训练到推理生成的完整示例流程。

---

## 【技术要点】

1. **任务定义**:语义匹配(Semantic Matching)属于句子对二分类,输入为两个句子,输出 2 分类结果(同义/异义),标签集合为 {0, 1}。
2. **模型选型**:采用 `RoBERTa-base-ch` 中文 RoBERTa 基座模型,通过 `AutoLoader` 以 `"classification"` 任务名自动加载;模型目录需包含 `config.json`、`pytorch_model.bin`、`vocab.txt` 三个文件。
3. **数据格式**:每行用 `\t` 分隔的 3 列形式 — `sentence_a \t sentence_b \t label`(整数 0/1);`src` 形如 `[[s1, s2], [s3, s4], ...]`,`tgt` 为 `[1, 0, ...]`。
4. **训练超参**:批量大小 `batch_size=8`,梯度累积 `gradient_accumulation_steps=1`,学习率 `lr=1e-5`,权重衰减 `weight_decay=1e-3`,训练轮数 `epochs=10`,日志间隔 `log_interval=100`,评估间隔 `eval_interval=500`,保存间隔 `save_interval=1`,实验名 `roberta-base-ch-semantic-matching`。
5. **数据集划分**:按 `data_len * 0.9` 切分训练集与验证集(9:1),训练封装到 `BertClsDataset`。
6. **推理入口**:训练完成后通过修改 `model_save_path` 指向 `./checkpoints_semantic_matching/9000/mp_rank_00_model_states.pt`,运行 `python ./generate.py` 即可观察生成结果。

---

## 【关键机制与数据】

**任务机理(原文)**:
文档开篇给出架构示意 `semantic_model.png`,语义匹配在底层逻辑上即句子对的二分类问题 — 编码器同时接收两个句子,经过交互式建模后输出一个二分类标签。

**示例数据流(原文)**:
```
test_data = [["后悔了吗","你有没有后悔"],
             ["打开自动横屏","开启移动数据"],
             ["我觉得你很聪明","你聪明我是这么觉得"]]
classification out: 1 / 0 / 1
```
即「后悔了吗」与「你有没有后悔」同义(1);「打开自动横屏」与「开启移动数据」不同义(0);「我觉得你很聪明」与「你聪明我是这么觉得」同义(1)。

**训练流程(原文)**:
数据加载 → `AutoLoader("classification", model_name="RoBERTa-base-ch", model_dir="./state_dict/")` 装载模型与 tokenizer → 9:1 划分 → 封装为 `BertClsDataset` → `Trainer(env_type="pytorch", ...)` 配置训练 → 命令行 `python ./train.py` 启动训练。

**训练后推理路径(原文)**:
```python
model_save_path = "./checkpoints_semantic_matching/9000/mp_rank_00_model_states.pt"
```
保存路径中包含训练步数 `9000` 与并行 rank 编号 `mp_rank_00`,暗示该训练框架使用分布式模型状态保存方式(deepspeed/mp 风格)。

**设备选择(原文)**:`torch.device("cuda" if torch.cuda.is_available() else "cpu")` — 优先 GPU,回退 CPU。

> 注:原文未给出准确率、F1、loss 曲线等性能指标数据,仅以 3 条样例展示定性结果。

---

## 【表格解读】

**原文无表格**。文档中存在的视觉元素为一张模型架构示意图 `semantic_matching_model.png`(仅以 `![](./img/semantic_matching_model.png)` 形式引用,无内部文字表格);另有 3 组输入—输出对列表,但均以代码块形式呈现,而非结构化表格。

---

## 【公式解读】

**原文无公式**。文档未出现任何 LaTeX 数学公式或伪代码算法,任务本质上是基于已有二分类模型的端到端微调,不涉及额外数学定义。

---

## 【关联】

文档作为 FlagAI(FlagAI/PyTorch)框架下的 **Tutorial 16** 案例,与以下特性/模块存在上下游关联:

- **`flagai.auto_model.auto_loader.AutoLoader`**:框架级自动化加载器,根据 `model_name` 与任务类型 `"classification"` 自动构建模型与分词器;模型文件本地不存在时,会从 model hub 下载到 `model_dir`。
- **`flagai.trainer.Trainer`**:框架级训练器,封装了分布式/单机训练、checkpoint 周期保存、`save_interval`、`eval_interval` 等机制。`save_dir="checkpoints_semantic_matching"` 与推理时 `model_save_path` 中的子目录 `9000` 形成训练—推理闭环。
- **`BertClsDataset`**:FlagAI 自带的分类数据集类,与 `src`(句子对列表)/`tgt`(标签列表)配套使用。
- **配套脚本**:`train.py`(实现 `read_file` 与训练入口)、`generate.py`(加载 `mp_rank_00_model_states.pt` 做推理);样例数据位于 `/examples/bert_semantic_matching/data/`。
- **预训练基座**:`RoBERTa-base-ch`(中文 RoBERTa 基座),属于 FlagAI/ModelHub 收录模型,与文档中其他使用 BERT/RoBERTa 的 tutorial 共享相同的 AutoLoader 调用范式。

(原文文末无内部超链接,关联信息均来自文档正文中提到的类名/路径/模块名。)

---

## 【使用方法】

**1. 数据准备(原文)**:
在 `train.py` 中定义 `read_file(data_path)`,从每行 `\t` 分隔的 3 列文件读取 `src = [[sent_a, sent_b], ...]` 与 `tgt = [label, ...]`;样例数据位于 `/examples/bert_semantic_matching/data/`。

**2. 模型与分词器加载(原文)**:
```python
from flagai.auto_model.auto_loader import AutoLoader
model_dir = "./state_dict/"
auto_loader = AutoLoader("classification",
                         model_name="RoBERTa-base-ch",
                         model_dir=model_dir)
model = auto_loader.get_model()
tokenizer = auto_loader.get_tokenizer()
```

**3. 训练器配置(原文)**:
```python
from flagai.trainer import Trainer
import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
trainer = Trainer(env_type="pytorch",
                  experiment_name="roberta-base-ch-semantic-matching",
                  batch_size=8, gradient_accumulation_steps=1,
                  lr=1e-5,
                  weight_decay=1e-3,
                  epochs=10, log_interval=100, eval_interval=500,
                  load_dir=None, pytorch_device=device,
                  save_dir="checkpoints_semantic_matching",
                  save_interval=1)
```

**4. 启动训练(原文)**:
```commandline
python ./train.py
```

**5. 推理生成(原文)**:
修改 `generate.py` 中的模型路径:
```python
model_save_path = "./checkpoints_semantic_matching/9000/mp_rank_00_model_states.pt"
```
然后执行:
```commandline
python ./generate.py
```
即可看到分类结果输出(0/1)。
