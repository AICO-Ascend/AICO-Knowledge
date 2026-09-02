# 如何构建和应用分词器

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_1_TOKENIZER.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_1_TOKENIZER.md

# 一体化深度解读：FlagAI 分词器构建与应用指南

---

## 【定位】

这篇文档系统介绍了 FlagAI 框架中**分词器（Tokenizer）的核心概念、加载方式、基本用法以及基于 Hugging Face 扩展自定义分词器的完整流程**，目标是帮助开发者将原始自然语言文本高效转换为模型可处理的数字序列，并支持在框架内灵活扩展新分词器。

---

## 【技术要点】

1. **分词的两阶段核心流程**：先将自然语言文本拆分为子词（token），再通过词表文件（vocabulary）将子词映射为对应的数字序号（id），最终原始文本被转换为"规整的数字序列"。
2. **Tokenizer 加载接口**：通过 `flagai.data.tokenizer.Tokenizer.from_pretrained(model_name)` 一行式加载，示例中使用 `model_name = "GLM-large-ch"`。
3. **词表文件自动缓存机制**：模型仓库中的词表文件会自动下载到 `cache_dir` 参数指定的路径，**默认目录为 `./checkpoints/{model_name}`**。
4. **编码与解码双方法**：
   - 编码：`tokenizer.EncodeAsIds(text)` → 返回 token id 列表；
   - 解码：`tokenizer.DecodeIds(encoded_ids)` → 恢复为原始字符串。
5. **自定义分词器扩展机制**：需先在 `/flagai/tokenizer` 目录下新建子目录，再继承基类 `Tokenizer`，可借助 Hugging Face `transformers` 库中的现成分词器（如 `T5Tokenizer`）进行封装。
6. **关键参数 `max_len`**：在自定义 `T5BPETokenizer` 中将 `self.text_tokenizer.max_len` 显式设置为 `int(1e12)`，以解除 Hugging Face 默认长度限制。

---

## 【关键机制与数据】

### 工作原理（原文串联还原）

1. **分词阶段（Tokenization）**：分词器调用其内置的文本分割算法（原文未指定具体算法），按语义单元切分原始文本；
2. **查表阶段（Lookup）**：分割得到的每个子词在词表文件中查找其对应的索引序号；
3. **编码阶段（Encoding）**：所有子词的序号按原始顺序拼接为数字序列（即 `EncodeAsIds` 的输出）；
4. **解码阶段（Decoding）**：通过 `DecodeIds` 将数字序列反向查表并还原为字符串。

### 数据流示例（原文给出）

> **原文**：`text = "Jack is walking a dog."` 经 `EncodeAsIds` 后得到 `encoded_ids = [2990, 2003, 3788, 1037, 3899, 1012]`，再经 `DecodeIds` 后 `recovered_text` 与 `text` 相同。

| 步骤 | 输入 | 输出 |
|------|------|------|
| 编码前 | `"Jack is walking a dog."` | 字符串 |
| 编码后 | — | `[2990, 2003, 3788, 1037, 3899, 1012]` |
| 解码后 | `[2990, 2003, 3788, 1037, 3899, 1012]` | `"Jack is walking a dog."`（与原文一致） |

### 性能数据

原文**未提供**任何性能基准、速度或精度数据。

---

## 【表格解读】

**原文无表格**。

文档中唯一的结构化信息载体是一张示例图（`img/tokenizer_example_1.png`，原文未对其内容做进一步文字描述）和若干代码片段，均不属于表格形式。

---

## 【公式解读】

**原文无公式**。

文档中既未出现 LaTeX 数学公式，也未出现伪代码形式的算法描述。`EncodeAsIds` 和 `DecodeIds` 的实现细节在原文中以代码示例呈现而非公式表达。

---

## 【关联】

### 与文中提及的其他特性/模块的关联

1. **`tokenization.md`（内部链接）**：文档在分词概念介绍部分明确指出"不同分词器可以有不同的文本分割方式，并且有不同的词表文件，**相关算法的介绍可以在 [这里](tokenization.md) 查看**"。这是本文档在算法理论层面的唯一外延链接，分词的具体算法细节（如字节对编码 BPE、WordPiece 等）需跳转至该文阅读。
2. **`flagai.data.tokenizer` 模块**：`Tokenizer` 类的加载入口与默认缓存机制均由此模块提供。
3. **`/flagai/tokenizer` 目录**：是用户自定义分词器扩展的标准注册位置，与 `flagai.data.tokenizer` 形成"运行时接口 + 注册目录"的对应关系。
4. **Hugging Face `transformers` 库**：通过继承 `Tokenizer` 并封装 `T5Tokenizer` 等现成分词器，FlagAI 实现了与上游开源生态的分词器兼容。
5. **`./checkpoints/{model_name}` 目录**：是词表文件下载的默认 `cache_dir`，与模型权重的缓存目录共用同一路径。

### 上下游关系

- **上游（依赖）**：Hugging Face `transformers`（自定义分词器的基础设施）；
- **下游（被消费）**：FlagAI 各类预训练模型（如示例中的 GLM-large-ch），训练和推理阶段都需要先通过本文档介绍的分词器将文本数字化。

---

## 【使用方法】

### 1. 加载预训练分词器（原文给出）

```python
from flagai.data.tokenizer import Tokenizer
model_name = "GLM-large-ch"
tokenizer = Tokenizer.from_pretrained(model_name)
```

### 2. 编码与解码（原文给出）

```python
text = "Jack is walking a dog."                  # 输入文本
encoded_ids = tokenizer.EncodeAsIds(text)        # 数字序列
recoverd_text = tokenizer.DecodeIds(encoded_ids) # 将数字序列恢复为文本
```

### 3. 创建自定义分词器（原文给出）

**步骤 1**：在 `/flagai/tokenizer` 目录下建立一个新的目录。

**步骤 2**：基于 Hugging Face `transformers` 库的分词器编写子类，以 `T5BPETokenizer` 为例：

```python
from transformers import T5Tokenizer
from ..tokenizer import Tokenizer

class T5BPETokenizer(Tokenizer):
    def __init__(self, model_type_or_path="t5-base", cache_dir=None):
        self.text_tokenizer = T5Tokenizer.from_pretrained(model_type_or_path,
                                                            cache_dir=cache_dir)
        self.text_tokenizer.max_len = int(1e12)
```

### 4. 关键配置项说明（原文涉及）

| 配置项 | 默认值/示例值 | 说明 |
|--------|--------------|------|
| `model_name`（`from_pretrained` 参数） | `"GLM-large-ch"` | 指定从哪个模型仓库加载对应词表 |
| `cache_dir`（`from_pretrained` 参数） | `./checkpoints/{model_name}` | 词表文件下载与缓存根目录 |
| `model_type_or_path`（自定义类参数） | `"t5-base"` | 自定义分词器底层调用的 Hugging Face 模型 |
| `max_len` | `int(1e12)` | 自定义 `T5BPETokenizer` 中显式覆盖 Hugging Face 的默认最大长度限制 |

> 备注：原文未涉及命令行启用方式、配置文件格式或环境变量设置，相关启用手段**原文未涉及**。
