# TUTORIAL_6_INSTRUCTIONS_FOR_PREDICTOR

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_6_INSTRUCTIONS_FOR_PREDICTOR.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_6_INSTRUCTIONS_FOR_PREDICTOR.md

# 深度解读：FlagAI Predictor 教程文档

## 【定位】

这篇文档解决的是 **FlagAI 框架下不同 NLP 任务（文本生成、命名实体识别、文本分类、语义匹配等）与不同模型架构（encoder、decoder、encoder-decoder）预测接口不统一** 的问题。它介绍了 `Predictor` 这一统一封装层，通过 `Pipeline` 输入文本后自动识别模型类型，调用相应的预测方法，使用户无需关心底层模型差异，即可"一行代码"获取预测结果。

---

## 【技术要点】

1. **统一入口 Predictor**：通过 `Predictor(model, tokenizer)` 实例化，传入 AutoLoader 加载的模型与分词器，自动完成后续的模型类型解析与方法路由。

2. **AutoLoader 任务名与模型名映射**：
   - 写作/续写任务：`task_name="writing"`, `model_name="GPT2-base-ch"`
   - NER 任务：`task_name="ner"`, `model_name="RoBERTa-base-ch-ner"`, 同时需传入 `class_num=len(target)`

3. **GPT2 随机采样生成（核心参数，保留原文数字）**：
   - `input_max_length=512`
   - `out_max_length=100`
   - `repetition_penalty=1.5`（重复惩罚，参考论文 arxiv:1909.05858）
   - `top_k=20`
   - `top_p=0.8`（参考论文 arxiv:1904.09751）

4. **NER 标签体系（7 类）**：`["O", "B-LOC", "I-LOC", "B-ORG", "I-ORG", "B-PER", "I-PER"]`，采用 BIO 标注方案（LOC=地名、ORG=机构、PER=人名）。

5. **NER 结果解析机制**：`predict_ner` 返回的每个实体为 `[start, end, label]` 三元组，通过 `e[0]:e[1]+1` 切片从原文中提取实体字符串，并按标签聚合到 `dict[label] → list[str]`。

6. **设备自动选择**：`torch.device("cuda" if torch.cuda.is_available() else "cpu")`，模型需 `.to(device)` 迁移。

---

## 【关键机制与数据】

### 工作原理
原文描述的 Predictor 工作流程：
1. 用户通过 `Pipeline`（Pipeline 在文档中被提及但代码示例中未直接调用）传入文本；
2. Predictor 接收 `(model, tokenizer)` 后，**自动分析 model 的类（class）**；
3. 根据模型类型自动调用对应的预测分支代码（如检测到 GPT2 → 调用生成方法）。

### 模型能力矩阵（原文叙述）
| 模型类型 | 支持的 Predictor 方法范围 |
|---|---|
| GPT2 / GLM / T5（decoder / encoder-decoder） | 仅支持生成类方法（`predict_generate_beamsearch`、`predict_generate_randomsample`），**不支持**分类、NER 等 |
| BERT / RoBERTa（encoder） | 支持**全部**方法：embedding、分类、MLM、NER、生成 |

### 原文示例输出数据
- **GPT2 写作示例输入**：`"今天天气不错，"`
- **GPT2 写作示例输出**：`"到这里来看了一下，很是兴奋，就和朋友一起来这里来了。我们是周五晚上去的，人不多，所以没有排队，而且这里的环境真的很好，在这里享受美食真的很舒服，我们点了一个套餐，两个人吃刚刚好，味道很好。"`

### NER 示例输入数据（原文测试样本，共 4 条）
1. `"6月15日，河南省文物考古研究所曹操高陵文物队公开发表声明承认：'从来没有说过出土的珠子是墓主人的"`
2. 北京冬奥会总结表彰大会相关报道
3. 欧盟冻结俄罗斯寡头资产的新闻
4. 博洛尼亚/巴勒莫比赛盘口数据

> 原文未提供具体的性能数据（如推理速度、准确率指标）。

---

## 【表格解读】

**原文无表格**。文档中仅包含两张图片：
- `./img/predictor_map.png`（Predictor 工作流程示意图，原文未做文字解读）
- `../docs/img/predictor_table.png`（Predictor 表格示意图，原文未做文字解读）

文档以分条列表形式枚举了 Predictor 支持的全部方法，但**未以表格形式给出**模型与方法的支持映射关系。

---

## 【公式解读】

**原文无公式**。

文档中仅通过注释引用了两篇论文（用于解释 `repetition_penalty` 与 `top_p` 参数的数学原理），但**未在文档内复现任何具体公式**，仅有论文链接：
- `https://arxiv.org/pdf/1909.05858.pdf`（重复惩罚机制）
- `http://arxiv.org/abs/1904.09751`（top-p 核采样）

---

## 【关联】

1. **上游模块 — AutoLoader**：Predictor 不负责模型加载，必须依赖 `flagai.auto_model.auto_loader.AutoLoader` 获取 `model` 和 `tokenizer`，二者是 Predictor 的初始化输入。

2. **配套接口 — Pipeline**：文档开篇指出"文本通过 Pipeline 传入"，Pipeline 是 Predictor 上层的文本输入通道（代码示例中未直接展示调用方式）。

3. **模型仓库 — Modelhub**：NER 示例注释中提到模型检查点来自 `model.baai.ac.cn/models`，这是 FlagAI 的模型仓库。

4. **下游模型适配范围**（原文明确列出）：
   - **NER 任务支持**：`BERT`、`RoBERTa`、`BERT-CRF`、`BERT-GlobalPointer`、`Roberta-CRF`、`Roberta-GlobalPointer`
   - **生成任务支持**：`BERT`、`RoBERTa`、`GPT2`、`T5`、`GLM`

5. **方法间的互斥关系**：decoder 类模型（GPT2/GLM/T5）只能调用生成类方法；encoder 类模型（BERT/RoBERTa）才能调用分类、NER、MLM、embedding 等方法 —— 这一限制是 Predictor 路由机制的逻辑前提。

---

## 【使用方法】

### 1. 启用方式（原文代码示例）

**场景 A：GPT2 中文文章续写（随机采样生成）**
```python
from flagai.auto_model.auto_loader import AutoLoader
from flagai.model.predictor.predictor import Predictor
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

loader = AutoLoader(task_name="writing", model_name="GPT2-base-ch")
model = loader.get_model()
tokenizer = loader.get_tokenizer()
model.to(device)

predictor = Predictor(model, tokenizer)
text = "今天天气不错，"
out = predictor.predict_generate_randomsample(
    text,
    input_max_length=512,
    out_max_length=100,
    repetition_penalty=1.5,
    top_k=20,
    top_p=0.8
)
```

**场景 B：RoBERTa 中文 NER**
```python
import torch
from flagai.auto_model.auto_loader import AutoLoader
from flagai.model.predictor.predictor import Predictor

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

target = ["O", "B-LOC", "I-LOC", "B-ORG", "I-ORG", "B-PER", "I-PER"]
auto_loader = AutoLoader(task_name="ner",
                         model_name="RoBERTa-base-ch-ner",
                         class_num=len(target))
model = auto_loader.get_model()
tokenizer = auto_loader.get_tokenizer()
model.to(device)

predictor = Predictor(model, tokenizer)

for t in test_data:
    entities = predictor.predict_ner(t, target, maxlen=256)
    result = {}
    for e in entities:
        if e[2] not in result:
            result[e[2]] = [t[e[0]:e[1] + 1]]
        else:
            result[e[2]].append(t[e[0]:e[1] + 1])
```

### 2. Predictor 全量方法清单（原文枚举）

| 方法名 | 任务类型 | 适用模型 |
|---|---|---|
| `predict_embedding` | 文本嵌入 | bert, roberta 等 |
| `predict_cls_classifier` | 文本分类 / 语义匹配 | bert, roberta 等 transformer encoder |
| `predict_masklm` | 掩码语言模型 | bert, roberta 等 transformer encoder |
| `predict_ner` | 命名实体识别 | bert, roberta 等 transformer encoder |
| `predict_generate_beamsearch` | 序列生成（beam search） | bert, roberta, gpt2, t5, glm |
| `predict_generate_randomsample` | 序列生成（随机采样） | bert, roberta, gpt2, t5, glm |

### 3. 关键配置项（参数）

| 参数 | 适用方法 | 原文中给出的取值 | 含义 |
|---|---|---|---|
| `input_max_length` | 随机采样生成 | `512` | 输入最大长度 |
| `out_max_length` | 随机采样生成 | `100` | 输出最大长度 |
| `repetition_penalty` | 随机采样生成 | `1.5` | 重复惩罚系数 |
| `top_k` | 随机采样生成 | `20` | 保留概率最高的 k 个 token |
| `top_p` | 随机采样生成 | `0.8` | 累积概率阈值（核采样） |
| `class_num` | NER 的 AutoLoader | `len(target)`（示例中为 7） | 标签类别数 |
| `maxlen` | `predict_ner` | `256` | NER 推理最大文本长度 |

> 原文未提供关于 batch 推理、CPU/GPU 性能调优、模型量化等进阶配置项的说明。
