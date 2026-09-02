# TUTORIAL_5_INSTRUCTIONS_FOR_AutoLoader

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_5_INSTRUCTIONS_FOR_AutoLoader.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_5_INSTRUCTIONS_FOR_AutoLoader.md

# 一体化深度解读:AutoLoader 使用指南

---

## 【定位】
**这篇文档介绍 FlagAI 中 AutoLoader 组件的能力与用法——只需传入 `task_name` 与 `model_name` 两个参数,即可自动从 model hub 下载对应的预训练模型、配置文件(config)与词表(vocab),并按下游任务类型(classification/seq2seq/sequence-labeling 等)快速构建出可直接使用的模型与分词器。**

---

## 【技术要点】

1. **两参数入口机制**:AutoLoader 通过 `task_name`(任务类型,如 `"title-generation"`、`"ner"`)与 `model_name`(模型标识,如 `"RoBERTa-base-ch"`)两个字符串即可完成模型查找与加载,核心导入路径为 `flagai.auto_model.auto_loader.AutoLoader`。

2. **方法分两步**:实例化 `AutoLoader` 后,分别调用 `auto_loader.get_model()` 与 `auto_loader.get_tokenizer()` 获取 PyTorch 模型对象与分词器,二者解耦,可单独使用。

3. **分类任务必须传 `class_num`**:在 `ner` 这类分类/序列标注任务中,必须额外传入 `class_num` 参数(等于标签集合长度),用于告知模型分类/标注的类别数。文档给出的中文 NER 标签集合共 7 类:
   ```python
   target = ["O", "B-LOC", "I-LOC", "B-ORG", "I-ORG", "B-PER", "I-PER"]
   ```
   故示例中 `class_num=len(target)` 即 7。

4. **下载落盘路径固定**:从 model hub 下载的预训练权重、config、vocab 一律存入本地目录 `./state_dict/RoBERTa-base-ch`(以 `RoBERTa-base-ch` 为例),即以 `model_name` 命名子目录。

5. **已训练下游模型直调**:除基础预训练模型外,`model_name` 还可以直接传入已微调好的下游任务模型,例如 `Roberta-base-ch-ner`、`Roberta-base-ch-title-generation`,跳过自行微调步骤,开箱即用。

6. **三大模型族对应不同任务族**(按架构划分):
   - **Transformer encoder**(如 `GLM-large-ch`、`RoBERTa-base-ch`):支持文档前列出的全部任务(包括 classification、seq2seq、sequence labeling)。
   - **Transformer decoder**(如 `GPT2-base-ch`):仅支持 seq2seq 类任务。
   - **Transformer encoder + decoder**(如 `t5-base-ch`):仅支持 seq2seq 类任务。

---

## 【关键机制与数据】

**工作原理(原文描述层面)**:

- AutoLoader 在内部维护一份从 `(task_name, model_name)` 到 model hub 资源的映射,用户传入这两个参数后,AutoLoader 据此在 hub 中定位对应的预训练模型、config 与 vocab 文件。
- 资源首次拉取后会缓存到本地 `./state_dict/{model_name}` 目录,后续调用命中本地缓存。
- `class_num` 作为分类头(原文未给出实现细节,但从上下文可知用于重塑模型的输出维度)的关键参数,仅在分类/序列标注类任务中强制要求。

**任务枚举与状态**(原文):

- classification: ① `classification` ② `semantic-matching` ③ `emotion-analysis`(**todo**) ④ `text-classification`(**todo**) …
- seq2seq: ① `seq2seq` ② `title-generation` ③ `writing` ④ `poetry-generation` ⑤ `couplets-generation`(**todo**) …
- sequence labeling: ① `sequence-labeling` ② `ner` ③ `ner-crf` ④ `ner-gp` ⑤ `part-speech-tagging`(**todo**) ⑥ `chinese-word-segmentation`(**todo**) …

**性能/吞吐数据**:原文未涉及任何训练速度、推理时延、显存占用、参数量等量化指标。

---

## 【表格解读】

**原文无表格。** 文档中虽然有两张图片(`./img/autoloader_en_map.png` 与 `./img/model_task_table.png`),但它们分别是 AutoLoader 的概念示意图与"模型-任务对应表"的截图(原文以 `![model_and_task_table](./img/model_task_table.png)` 形式嵌入),不是 markdown 表格,无法逐字还原成文字表格内容,因此按要求标注为"原文无表格"。模型-任务的对应关系在文档正文中通过三级标题枚举给出(见上文【技术要点】与【关键机制与数据】)。

---

## 【公式解读】

**原文无公式。** 全文未出现任何 LaTeX 公式或伪代码形式的数学表达式,故无公式可解读。

---

## 【关联】

文末提供的内部链接信息为"(无)",但文档正文与图片内嵌了两个**外部参考**:

- **`https://github.com/FlagAI-Open/FlagAI/blob/master/quickstart/ner_ch.py`**:中文 NER 的完整 quickstart 示例脚本,展示 `AutoLoader(task_name="ner", ...)` 之外的下游流程(数据加载、训练/评估循环等),可视为 AutoLoader 在 ner 任务上的端到端参考实现。

文档中图片指向的两张示意图分别承担不同信息密度:
- `autoloader_en_map.png`:**机制层**——展示 AutoLoader 在用户、model hub、磁盘缓存(`./state_dict/`)三者之间的数据流。
- `model_task_table.png`:**枚举层**——即"模型-任务对应表",直观给出每种 `model_name` 可绑定哪些 `task_name`,与正文三级枚举互为补充。

从上下文关系看:
- `AutoLoader` 与 `flagai.auto_model` 包同模块(`auto_loader.py`)绑定,是 FlagAI 上层 `quickstart` 示例脚本(ner_ch.py、title-generation 等)的统一前置依赖。
- `AutoLoader` 下游调用的是 model hub 中的具体 checkpoint,与仓库"All supported models"节中所列的 GLM/RoBERTa/GPT2/T5 等模型族直接挂钩——任务(task)与模型(model)的合法性取决于 hub 中是否已发布对应 checkpoint。

---

## 【使用方法】

### 启用方式
通过导入 `flagai.auto_model.auto_loader` 模块中的 `AutoLoader` 类启用。

### 命令模板(原文给出)
**1. 标题生成任务(seq2seq 类,无 `class_num`):**
```python
from flagai.auto_model.auto_loader import AutoLoader
auto_loader = AutoLoader(
    task_name="title-generation",
    model_name="RoBERTa-base-ch",
)
model    = auto_loader.get_model()
tokenizer = auto_loader.get_tokenizer()
```

**2. NER 任务(序列标注类,必须传 `class_num`):**
```python
target = ["O", "B-LOC", "I-LOC", "B-ORG", "I-ORG", "B-PER", "I-PER"]
from flagai.auto_model.auto_loader import AutoLoader
auto_loader = AutoLoader(
    task_name="ner",
    model_name="RoBERTa-base-ch",
    class_num=len(target),
)
model    = auto_loader.get_model()
tokenizer = auto_loader.get_tokenizer()
```

**3. 直接调用已微调的下游 NER 模型(跳过自行训练):**
```python
target = ["O", "B-LOC", "I-LOC", "B-ORG", "I-ORG", "B-PER", "I-PER"]
from flagai.auto_model.auto_loader import AutoLoader
auto_loader = AutoLoader(
    task_name="ner",
    model_name="RoBERTa-base-ch-ner",   # 注意:已带 -ner 后缀,表示下游已微调版本
    class_num=len(target),
)
model    = auto_loader.get_model()
tokenizer = auto_loader.get_tokenizer()
```

### 配置项
- **`task_name`**(必填,str):取值见【技术要点】中的任务枚举,亦可参考 `model_task_table.png`。
- **`model_name`**(必填,str):取值见 model hub 文档,如 `"RoBERTa-base-ch"`、`"GLM-large-ch"`、`"GPT2-base-ch"`、`"t5-base-ch"` 或带任务后缀的下游模型名。
- **`class_num`**(分类/序列标注任务必填,int):标签类别数,典型取值如 NER 的 7。

### 落盘路径
下载物默认缓存至 `./state_dict/{model_name}` 目录下,可通过切换工作目录或自行重定向模型 hub 的下载路径来调整(原文未涉及具体环境变量或配置项写法)。
