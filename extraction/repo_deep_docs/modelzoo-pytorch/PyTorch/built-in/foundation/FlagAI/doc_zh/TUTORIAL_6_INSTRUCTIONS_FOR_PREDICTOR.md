# TUTORIAL_6_INSTRUCTIONS_FOR_PREDICTOR

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_6_INSTRUCTIONS_FOR_PREDICTOR.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_6_INSTRUCTIONS_FOR_PREDICTOR.md

# 《将现成的推理算法与 Predictor 结合使用》深度解读

## 【定位】
这篇文档解决的是 **FlagAI 中不同任务（标题生成、命名实体识别、文本分类、文本续写等）和不同模型架构（encoder / decoder / encoder-decoder）下，推理调用方式碎片化、接口不统一的问题**——通过 `Predictor` 这一统一封装，让用户以 "一行代码" 形式自动识别模型类型并调用对应预测逻辑。

---

## 【技术要点】

1. **统一入口 `Predictor(model, tokenizer)`**：将模型与 tokenizer 一并传入，由 Predictor 内部自动判断模型类型（encoder / decoder / encoder-decoder），再分发到对应的预测分支，免去用户根据任务手工选择调用栈。

2. **AutoLoader 任务-模型映射**：
   - 文章续写：`task_name="writing"`，`model_name="GPT2-base-ch"`
   - 命名实体识别：`task_name="ner"`，`model_name="RoBERTa-base-ch-ner"`，另需传入 `class_num=len(target)`
   - 任务标签集合 `target = ["O", "B-LOC", "I-LOC", "B-ORG", "I-ORG", "B-PER", "I-PER"]`（7 类 BIO 标注）

3. **生成任务采样超参**（以 GPT2 文章续写为例）：
   - `input_max_length=512`（最大输入长度）
   - `out_max_length=100`（最大输出长度）
   - `repetition_penalty=1.5`（避免重复输出，论文 https://arxiv.org/pdf/1909.05858.pdf）
   - `top_k=20`（仅保留概率最大的 20 个 token）
   - `top_p=0.8`（累计概率 ≥ 0.8 的 token 被保留，论文 http://arxiv.org/abs/1904.09751）

4. **NER 接口 `predict_ner(text, target, maxlen=256)`**：返回实体列表，每个元素为 `(start_idx, end_idx, label)` 元组；适配 BERT、RoBERTa、BERT-CRF、BERT-GlobalPointer、RoBERTa-CRF、RoBERTa-GlobalPointer 等多种 backbone + 解码头组合。

5. **Predictor 支持的方法全集**（原文枚举）：
   - 文本表征：`predict_embedding`（支持 bert、roberta）
   - 文本分类 / 语义匹配：`predict_cls_classifier`（支持 bert、roberta 等 transformer 编码器）
   - Mask 语言模型：`predict_masklm`（支持 bert、roberta）
   - 命名实体识别：`predict_ner`（支持 bert、roberta 等编码器）
   - 生成（seq2seq）：`predict_generate_beamsearch` 与 `predict_generate_randomsample`（支持 bert、roberta、gpt2、t5、glm）

6. **方法可用性约束**：GLM、T5、GPT2 等 decoder 主导模型只能调用生成类方法；Bert、Roberta 编码器类模型则覆盖全部上述方法。

---

## 【关键机制与数据】

**工作原理（Pipeline 化推理）：**
- 用户先通过 `AutoLoader` 根据 `task_name + model_name` 从 Modelhub（model.baai.ac.cn/models）拉取权重并装配 tokenizer；
- 构造 `Predictor(model, tokenizer)` 后，Predictor 内部依据 `model` 实例的类别（而不是用户手工指定）解析其属于 encoder-only / decoder-only / encoder-decoder，从而选择 `predict_generate_*`、`predict_ner`、`predict_cls_classifier` 等对应代码路径；
- 对 NER 任务，输出为 `(start_offset, end_offset, label)` 三元组列表，再由用户侧代码按 `e[2]`（label）聚合、按 `t[e[0]:e[1]+1]` 切片还原原文字符串。

**数据流示意（GPT2 文章续写）：**
`"今天天气不错，"` → tokenizer 编码到 `input_max_length=512` → 模型 forward → 随机采样循环（受 `repetition_penalty / top_k / top_p` 约束），直至生成 `out_max_length=100` 个 token 或遇到 EOS → 解码回中文文本。

**原文数据样例（原文）：**
- GPT2 续写输入 `"今天天气不错，"` → 输出 `"到这里来看了一下，很是兴奋，就和朋友一起来这里来了……"`（原文直接给出该真实生成结果）。
- NER 测试样本共 4 条，覆盖体育（冬奥会）、时政（欧盟冻结资产）、娱乐评论（博洛尼亚/巴勒莫赔率）等多领域，长短不一；标签集合固定为 7 类 BIO。

**生成解码论文锚点（原文）：**
- `repetition_penalty` → arXiv:1909.05858
- `top_p`（nucleus sampling） → arXiv:1904.09751

---

## 【表格解读】

**原文无表格。** 文档仅引用两张图片资源：`./img/predictor_map.png`（Predictor 总体调用架构图）与 `../docs/img/predictor_table.png`（方法-模型支持对照表），二者在原文 Markdown 中均以图片形式嵌入，未给出可解析的表格文本或结构化对照数据，故此处不进行表格还原，仅在【关键机制与数据】中以文字形式概括其表达的能力-模型对应关系。

---

## 【公式解读】

**原文无公式。** 文档中所有解码策略均以 Python 函数参数形式给出（`repetition_penalty / top_k / top_p`），并未在正文中写出任何 LaTeX 数学公式或伪代码表达式，因此无法逐式还原。

---

## 【关联】

- **上游模块：`AutoLoader`**（`flagai.auto_model.auto_loader`）—— 负责按 `task_name + model_name` 装载权重与 tokenizer，是 Predictor 工作的前置条件；NER 场景还需显式传入 `class_num`。
- **下游模块：`flagai.model.predictor.predictor.Predictor`** —— 文档主角，对外屏蔽任务与模型差异。
- **配套任务池**：`writing`、`title-generation`、`ner`、`semantic-matching`（原文明确列出后三者作为 "除 writing 之外" 的可支持任务）。
- **模型仓库**：Modelhub（model.baai.ac.cn/models），`RoBERTa-base-ch-ner` 即从此处获取。
- **底层模型谱系**：
  - 编码器侧：BERT、RoBERTa → 全部方法；
  - 解码器侧：GPT2、GLM、T5 → 仅生成方法；
  - 解码头扩展：BERT-CRF、BERT-GlobalPointer、RoBERTa-CRF、RoBERTa-GlobalPointer → 复用 `predict_ner`。
- **采样解码论文**：arXiv:1909.05858（repetition penalty）、arXiv:1904.09751（nucleus / top-p sampling），文档以 URL 形式内联引用。

> 文档末尾未给出任何内部链接信息（无交叉引用、无目录条目），故此节仅基于文中显式提到的模块与任务展开。

---

## 【使用方法】

**1. 通用导入与设备初始化（原文）：**
```python
import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
```

**2. 文章续写（GPT2，随机采样）（原文）：**
```python
from flagai.auto_model.auto_loader import AutoLoader
from flagai.model.predictor.predictor import Predictor

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
    top_p=0.8,
)
```

**3. 命名实体识别（RoBERTa-base-ch-ner）（原文）：**
```python
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
```

**4. 其它方法调用模式（原文按用途列出，无示例代码）：**
- `predict_embedding(text)` — 文本表征
- `predict_cls_classifier(text)` — 分类 / 语义匹配
- `predict_masklm(text_with_[MASK])` — 掩码填充
- `predict_generate_beamsearch(text, ...)` — 束搜索生成（seq2seq）

**5. 调用限制（原文）：**
- GLM、T5、GPT2 类模型仅可调用 `predict_generate_*` 系列；
- BERT、RoBERTa 类编码器模型可调用上文 6 大方法中的全部 5 类（含两种生成方式）。
- 入口脚本建议置于 `if __name__ == '__main__':` 保护块下（原文 GPT2 示例使用此写法）。
