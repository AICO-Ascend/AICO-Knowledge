# How to construct and use Tokenizer

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_1_TOKENIZER.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_1_TOKENIZER.md

# 一体化深度解读: FlagAI Tokenizer 教程文档

## 【定位】

这篇文档解决**如何在 FlagAI 中加载、使用 Tokenizer,以及如何基于 HuggingFace tokenizer 二次封装自定义 tokenizer**的问题,使开发者能够完成"自然语言文本 ↔ token ID 序列"的双向转换。

---

## 【技术要点】

1. **Tokenizer 的核心职责**:在 NLP 预处理阶段,将非结构化的符号文本拆分为语义单元 **tokens**,再通过词表 (vocabulary) 查表映射为数字 ID,得到机器学习系统可用的数值矩阵。
2. **加载方式**:通过 `Tokenizer.from_pretrained(model_name)` 从 **Modelhub** 自动下载词表文件;缓存路径由 `cache_dir` 参数指定,**默认值为 `./checkpoints/{model_name}`**。
3. **编码 (Encode)**:调用 `tokenizer.EncodeAsIds(text)` 将字符串转为 token ID 列表;示例 `text = "Jack is walking a dog."` 经编码后得到 `[2990, 2003, 3788, 1037, 3899, 1012]`(原文直接给出的数字序列)。
4. **解码 (Decode)**:调用 `tokenizer.DecodeIds(encoded_ids)` 将 ID 列表还原为字符串;原文明示 `recovered_text` 应与原始 `text` 相同。
5. **自定义 tokenizer 的目录约定**:需在 **`/flagai/tokenizer`** 下新建 package(原文小标题 1)。
6. **基于 HuggingFace 二次封装**:以 `T5Tokenizer` 为例,定义继承自 `Tokenizer` 的子类 `T5BPETokenizer`,并在 `__init__` 中将 `self.text_tokenizer.max_len` 显式设为 **`int(1e12)`**(原文参数原值)。

---

## 【关键机制与数据】

- **工作原理**:Tokenizer 本质上维护一套"分词规则 + 词表文件"。分词规则决定如何把文本切成 tokens(不同 tokenizer 分法不同),词表文件提供 token → ID 的映射表。运行时,文本先按规则切片,再查表得到整数序列,机器学习模型即可消费这一序列。
- **数据流**:
  - 加载阶段:`model_name` → 从 Modelhub 拉取词表 → 写入 `./checkpoints/{model_name}`(可被 `cache_dir` 覆盖)。
  - 编码阶段:`text (str)` → `EncodeAsIds` → `encoded_ids (List[int])`。
  - 解码阶段:`encoded_ids (List[int])` → `DecodeIds` → `recovered_text (str)`。
- **原文给出的具体数据**:对示例句 `"Jack is walking a dog."` 编码后得到的 token ID 列表为 `[2990, 2003, 3788, 1037, 3899, 1012]`(共 6 个 ID,与文本中的 6 个 token 一一对应)。
- **性能数据**:原文未涉及(无训练/推理吞吐量、词表大小、运行时间等数字)。

---

## 【表格解读】

**原文无表格**。原文中虽然列举了 token ID 序列 `[2990, 2003, 3788, 1037, 3899, 1012]`,但它是嵌入在代码注释中的一行列表,而非独立表格;参数(如 `cache_dir`、`max_len = int(1e12)`、`model_type_or_path`)也是以代码/正文形式出现,未形成表格结构。

---

## 【公式解读】

**原文无公式**(无 LaTeX 或伪代码形式公式)。文档所涉及的"运算"仅是方法调用(`EncodeAsIds` / `DecodeIds` / `from_pretrained`)和参数赋值(`max_len = int(1e12)`),没有数学公式。

---

## 【关联】

- **与 Modelhub 的关系**:加载 tokenizer 的词表来源就是 Modelhub;`model_name` 需对应 Modelhub 上可识别的模型(原文示例 `GLM-large-en`)。缓存目录 `./checkpoints/{model_name}` 也是 Modelhub 在 FlagAI 体系内的默认落盘约定,与模型权重加载共享同一套路径规范。
- **与 HuggingFace transformers 库的关系**:自定义 tokenizer 的推荐路径是"包装 HuggingFace 的 tokenizer",原文以 `T5Tokenizer` 为例展示了如何继承 `flagai.data.tokenizer.Tokenizer` 并内嵌一个 `T5Tokenizer` 实例。这表明 FlagAI 的 Tokenizer 在设计上是一个**抽象基类/外观层**,底层委托给 HuggingFace 实现,自身只定义统一接口。
- **与 tokenization.md 的关系**:原文有一行被注释掉的提示 `[//]: # (An introduction to those algorithms can be viewed [here](tokenization.md).)`,说明项目内另有一篇 `tokenization.md` 专门介绍分词算法(BPE、WordPiece 等),本文档定位为**使用教程**,二者是"原理 ↔ 使用"的互补关系。
- **与上下游模块的关系**:Tokenizer 输出 token ID 列表,这些 ID 会被后续的 NLP 模型(例如 GLM)直接消费,因此 Tokenizer 是 FlagAI 数据流中的**最前端预处理环节**;反之,模型产出的 ID 也通过 `DecodeIds` 回到文本侧,可用于生成任务的输出还原。

---

## 【使用方法】

- **加载预训练 tokenizer**:
  ```python
  from flagai.data.tokenizer import Tokenizer
  model_name = "GLM-large-en"
  tokenizer = Tokenizer.from_pretrained(model_name)  # 默认下载到 ./checkpoints/{model_name}
  ```
  可通过 `cache_dir` 参数自定义词表落盘路径(原文仅说明默认值,未给出显式传参示例)。

- **文本编码 → ID 列表**:
  ```python
  text = "Jack is walking a dog."
  encoded_ids = tokenizer.EncodeAsIds(text)  # → [2990, 2003, 3788, 1037, 3899, 1012]
  ```

- **ID 列表 → 文本(还原)**:
  ```python
  recovered_text = tokenizer.DecodeIds(encoded_ids)  # 与原始 text 相同
  ```

- **创建自定义 tokenizer(两步法,原文小标题原话)**:
  1. **第一步**:在 **`/flagai/tokenizer`** 目录下创建一个 package(原文未细化包内部目录结构)。
  2. **第二步**:在该包内编写继承自 `Tokenizer` 的类,以**包装 HuggingFace 的 tokenizer**;原文以 `T5BPETokenizer` 包装 `T5Tokenizer` 为示例,关键参数 `model_type_or_path` 默认 `"t5-base"`,`cache_dir` 默认 `None`;并在初始化时把底层 tokenizer 的 `max_len` 显式置为 `int(1e12)`,以避免 HuggingFace 默认长度上限的截断。

- **配置项/命令汇总**(逐字取自原文):
  - `model_name`:Tokenizer.from_pretrained 的入参,示例 `"GLM-large-en"`。
  - `cache_dir`:词表缓存目录,默认 `./checkpoints/{model_name}`。
  - `model_type_or_path`:自定义 tokenizer 包装时透传给 HuggingFace 的入参,示例 `"t5-base"`。
  - `max_len = int(1e12)`:在自定义 tokenizer 初始化时对底层 HuggingFace tokenizer 设置的长度上限(原文原值)。
