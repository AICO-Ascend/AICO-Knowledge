# Major Function of Model Module

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_3_MODEL.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_3_MODEL.md

# FlagAI Model 模块教程深度解读

## 【定位】

本文档系统讲解 FlagAI 中 `model` 模块的核心能力——如何通过统一的 `BaseModel` 接口加载预训练/微调模型（涵盖 encoder、decoder、encoder-decoder 三类典型结构），并介绍了模型的分层构建逻辑（`layer → block → model`）、`forward` 输入输出契约以及基于 JSON 配置的实例化方法，为模型层的使用与扩展提供权威指引。

---

## 【技术要点】

1. **统一基类与三类架构支持**：所有模型继承自 `BaseModel`，当前全面支持 **encoder、decoder、encoder-decoder** 三种主流结构；GLM 系列模型可加载 THUDM/GLM 全系权重。
2. **`from_pretrain` 双模式加载**：
   - **modelhub 模式**（在线）：自动下载 `config.json`、`pytorch_model.bin`、`vocab.txt`。
   - **本地模式**（离线）：从 `download_path/model_name/` 目录加载。
   - 优化了数据并行/模型并行场景的下载，避免重复下载造成的资源浪费。
3. **同结构模型共用类加载**：结构相同的模型共用同一类，例如 `BERT-base` 与 `RoBERTa-base` 都使用 `BertModel` 类。
4. **任务无关的 `AutoLoader`**：以"任务与模型无关"为设计原则，可自由组合任务与模型。
5. **分层构造范式**：`flagai.model.layer`（mlp、layernorm、activation、attention 等基础层）→ `flagai.model.block`（如 BERT block，由 layer 组合而成的 Transformer 块）→ `flagai.model`（embedding + 堆叠 block 构成完整模型）。
6. **`forward` 输入输出契约**：输入为**关键字参数**（如 `input_ids`、`position_ids`、`attention_mask`），多余参数自动忽略；输出为包含 `logits` 与 `hidden_states` 的 **dict**。
7. **`init_from_json` 配置驱动实例化**：通过 JSON 配置文件初始化模型，并支持新增参数（如 `checkpoint_activations=True` 用于控制是否执行**梯度重计算**）。

---

## 【关键机制与数据】

- **加载机制**：`from_pretrain` 通过 `ClassName.from_pretrain()` 调用，参数为 `download_path` 与 `model_name`，会自动识别本地或远端源。
- **任务适配机制**：通过专门的子类（如 `GLMForSeq2Seq`、`BertForSequenceLabeling`）承载微调后的任务能力，仍使用 `from_pretrain` 加载。
- **AutoLoader 机制**：以任务名（如 `"title-generation"`）+ 模型名（如 `"GLM-large-ch"`）+ 模型目录 `model_dir` 三元组加载模型实例 `auto_loader.get_model()`。
- **`forward` 输入**：GLM 的 `forward` 关键字参数包括 `input_ids=None`、`position_ids=None`、`attention_mask=None`、`mems=None`、`return_memory=False`、`detach_memory=True`、`prompt_pos=None` 以及 `**kwargs`（多余自动忽略）。
- **`forward` 输出**：GLM 返回 `{'loss': loss, 'logits': logits, 'hidden_states': mems}`，其中 `logits` 与 `hidden_states` 是必需字段。
- **`init_from_json`**：`GLMModel.init_from_json(config_file="./config.json", checkpoint_activations=True)`，其中 `checkpoint_activations=True` 是用于**控制是否执行梯度重计算**的新增参数；输出为 GLM 模型的实例。
- **性能数据**：原文未涉及具体性能数据（无训练/推理吞吐、参数量、benchmark 等数字）。

---

## 【表格解读】

### 表 1：All supported models（原文逐字还原）

| ClassName | ModelName | Language | Model Type |
|---|---|---|---|
| flagai.model.glm_model.GLMModel | **GLM-10b-ch** | chinese | encoder |
| flagai.model.glm_model.GLMModel | **GLM-large-ch** | chinese | encoder |
| flagai.model.bert_model.BertModel | **RoBERTa-base-ch** | chinese | encoder |
| flagai.model.gpt2_model.GPT2Model | **GPT2-base-ch** | chinese | decoder |
| flagai.model.t5_model.T5Model | **T5-base-ch** | chinese | enc2dec |
| flagai.model.t5_model.T5Model | **T5-base-en** | chinese | enc2dec |
| flagai.model.bert_model.BertModel | **BERT-base-en** | english | encoder |
| flagai.model.glm_model.GLMModel | **GLM-large-en** | english | encoder |

**逐行解读**：
- 第 1–2 行：GLM 系列（中文），使用同一 `GLMModel` 类覆盖两个规模（10B 与 large），均为 encoder 类型。
- 第 3 行：`RoBERTa-base-ch` 通过 `BertModel` 类加载，说明该类兼容 RoBERTa 与 BERT 同一结构族。
- 第 4 行：唯一的中文 decoder 模型 `GPT2-base-ch`，由 `GPT2Model` 加载。
- 第 5–6 行：T5 系列（注意：原文标 T5-base-en 的 Language 字段为 `chinese`，原文如此，未做修正），由 `T5Model` 加载，类型为 `enc2dec`（encoder-decoder）。
- 第 7 行：英文 encoder 模型 `BERT-base-en`，由 `BertModel` 加载。
- 第 8 行：`GLM-large-en` 英文版，仍由 `GLMModel` 加载，体现 GLM 类对中英双语模型的支持。

> 注：原表中"T5-base-en"的 Language 列显示为 `chinese`，系原文内容，按用户要求不做修改地保留。

### 表 2：Supported models + tasks（原文逐字还原）

| ClassName | Model Name | language | Task |
|---|---|---|---|
| flagai.model.glm_model.GLMForSeq2Seq | GLM-large-ch | chinese | **title generation** |
| flagai.model.glm_model.GLMForSeq2Seq | GLM-large-ch | chinese | **poetry generation** |
| flagai.model.bert_model.BertForSequenceLabeling | RoBERTa-base-ch | chinese | **title generation** |
| flagai.model.bert_model.BertForSequenceLabeling | RoBERTa-base-ch | chinese | **NER** |
| flagai.model.bert_model.BertForSequenceLabeling | RoBERTa-base-ch | chinese | **semantic matching** |
| flagai.model.t5_model.T5Model | T5-base-ch | chinese | **title generation** |
| flagai.model.bert_model.BertForSequenceLabeling | BERT-base-en | english | **title gneration** |

> 注：原文末行"title gneration"为原文拼写（typo），按用户要求保留。

**逐行解读**：
- 第 1–2 行：同一 `GLM-large-ch` 模型 + `GLMForSeq2Seq` 类，可同时承载两个生成类任务（标题生成、诗歌生成）。
- 第 3–5 行：`RoBERTa-base-ch` + `BertForSequenceLabeling` 类，同时支持**标题生成**、**NER（命名实体识别）**、**语义匹配**三类任务，体现同一类多任务覆盖能力。
- 第 6 行：`T5-base-ch` 通过原生 `T5Model` 类直接承载标题生成任务。
- 第 7 行：`BERT-base-en` + `BertForSequenceLabeling` 类支持英文标题生成（原文拼为 `title gneration`）。

---

## 【公式解读】

原文无数学公式（LaTeX 或符号化公式）；仅包含若干代码片段（函数签名、返回值字典、调用示例），均已在【关键机制与数据】与【使用方法】节内逐字引用。

---

## 【关联】

本文档属于 FlagAI 模型层的 tutorial 文档，章节标题自身揭示了文档的内部目录结构（`from_pretrain` → `All supported models` → `Supported models + tasks` → `Model design` → `forward function` → `init_from_json`），章节之间形成如下上下游关系：

- `BaseModel` 是所有模型类的根基，提供通用加载/保存能力，被 `GLMModel`/`BertModel`/`GPT2Model`/`T5Model`/`GLMForSeq2Seq`/`BertForSequenceLabeling` 等子类继承。
- `from_pretrain` 是用户层入口，其下分两条子路径：**从 modelhub 加载**与**加载本地模型权重**，两者调用方式相同，仅路径解析不同。
- `All supported models` 列出 `from_pretrain` 可直接加载的预训练权重；`Supported models + tasks` 则在其基础上进一步列出已微调、绑定到特定任务的模型权重。
- `AutoLoader` 位于 `flagai.auto_model.auto_loader`，是任务-模型无关的高阶封装，依赖本模块的 `ClassName.from_pretrain()` 来获取底层模型。
- `Model design`（`layer → block → model`）是模型结构层面的自底向上构造路径，与上层的加载/任务化机制相互独立：前者定义"模型长什么样"，后者定义"怎么把模型拿出来用"。
- `forward function` 是模型被训练/推理时实际被调用的方法；其输入约定与下游 loss 计算、metric 评估直接挂钩。
- `init_from_json` 是模型实例化的另一条路径（区别于 `from_pretrain`），适合需要自定义初始化参数（如 `checkpoint_activations=True`）的场景，与配置文件 `config.json` 配合使用。
- 关于 GLM 系列与上游仓库 THUDM/GLM 的关系：本文档链接了 `https://github.com/THUDM/GLM`，说明 GLM 系列权重与上游开源项目保持兼容。

---

## 【使用方法】

### 1. 从 modelhub 在线加载模型

```python
>>> from flagai.model.glm_model import GLMModel
>>> model = GLMModel.from_pretrain(download_path="./state_dict", model_name="GLM-large-ch")
```
会自动下载 `config.json`、`pytorch_model.bin`、`vocab.txt` 到 `download_path/model_name/` 下。

### 2. 从本地加载模型权重

```python
>>> from flagai.model.glm_model import GLMModel
>>> model = GLMModel.from_pretrain(download_path="./state_dict", model_name="GLM-large-ch")
```
当 `./state_dict/GLM-large-ch/` 下已存在 `pytorch_model.bin` 与 `config.json` 时，从本地直接读取。

### 3. 加载任务化（已微调）模型

```python
>>> from flagai.model.glm_model import GLMForSeq2Seq
>>> model = GLMForSeq2Seq.from_pretrain(model_name='GLM-large-ch')
```
适用于如 `title-generation`、`poetry generation`、`NER`、`semantic matching` 等任务场景（见任务表）。

### 4. 使用 AutoLoader（任务-模型无关）

```python
>>> from flagai.auto_model.auto_loader import AutoLoader
>>> auto_loader = AutoLoader("title-generation",
>>>                          model_name="GLM-large-ch",
>>>                          model_dir="./state_dict")
>>> model = auto_loader.get_model()
```

### 5. 通过 JSON 配置文件实例化（支持自定义初始化参数）

```python
>>> GLMModel.init_from_json(config_file="./config.json", checkpoint_activations=True)
```
其中 `checkpoint_activations=True` 用于控制是否执行**梯度重计算**。

### 6. 调用 `forward` 函数

```python
>>> def forward(self,
>>>             input_ids=None,
>>>             position_ids=None,
>>>             attention_mask=None,
>>>             mems=None,
>>>             return_memory=False,
>>>             detach_memory=True,
>>>             prompt_pos=None,
>>>             **kwargs)
>>> return {'loss': loss, 'logits': logits, 'hidden_states': mems}
```
- 输入采用**关键字参数**，多余参数会被自动忽略。
- 输出为字典，必需字段为 `logits` 与 `hidden_states`，并附带 `loss`。

> 配置项（如学习率、batch size 等训练超参数）：原文未涉及，仅涉及模型初始化/加载相关参数（`download_path`、`model_name`、`model_dir`、`config_file`、`checkpoint_activations`）。
