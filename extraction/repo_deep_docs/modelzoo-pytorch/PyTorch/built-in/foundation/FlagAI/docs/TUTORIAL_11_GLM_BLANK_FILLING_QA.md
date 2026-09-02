# GLM Blank Filling Generation

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_11_GLM_BLANK_FILLING_QA.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_11_GLM_BLANK_FILLING_QA.md

# GLM Blank Filling Generation 文档深度解读

---

## 【定位】

这篇文档介绍了 GLM（General Language Model）模型的核心能力——**变长空白填充（variable-length blank filling）生成**，并说明了如何基于 FlagAI 框架调用预训练 GLM 模型完成三类不同粒度的填空/问答生成任务（token 级、句子级、文档级）。

---

## 【技术要点】

1. **预训练范式**：GLM 采用自回归空白填充（autoregressive blank-filling）预训练，结合自编码思想随机遮蔽连续 token 片段、再以自回归方式重建，从而让模型在预训练阶段就学到生成能力。
2. **下游任务统一为完形填空**：GLM 把分类等下游任务改写为 cloze question（如情感分类改写为 "[SENTENCE]. It's really ___"），预训练与微调目标一致（均为给定上下文生成文本）。
3. **三种 MASK 粒度**：
   - `[MASK]`：Token 级，遮蔽随机 token，遮蔽比例最小，适合短答案。
   - `[sMASK]`：Entity/Sentence 级，多个完整句子片段，**覆盖原 token 约 15%**，适合 seq2seq 任务。
   - `[gMASK]`：Document 级，**单个片段、长度服从原长 50%–100% 的均匀分布**，适合长文本生成。
4. **调用组件**：FlagAI 提供 `GLMModel`、`Tokenizer`、`Predictor` 三件套；加载模型名 `GLM-large-ch`，推理入口为 `predictor.predict_generate_randomsample(text)`。
5. **多任务预训练扩展**：GLM 在预训练中**联合训练** masked span 重建与较长文本生成，使模型更好地适配文本生成任务。
6. **特殊控制符**：生成示例中可见 `<|endoftext|>` 与 `<|startofpiece|>` 作为 GLM 的分段/起始控制标记，用于分隔输入与生成内容。

---

## 【关键机制与数据】

- **原文：预训练–微调一致性**——"both pretraining and finetuning involves training the model to generate text given context"，因此下游任务以 cloze 形式构造（如情感分类填空 "It's really ___"）。
- **原文：`[sMASK]` 比例**——"Multiple spans (sentences) are sampled to cover **15% of the original tokens**"，且被遮蔽的 span 必须是完整句子。
- **原文：`[gMASK]` 长度采样**——"length is sampled from a **uniform distribution over 50%–100%** of the original length"，仅采一个 span。
- **原文：示例输入/输出对比**（数据流示意）：
  - `[MASK]` 例：`[CLS]北京故宫是中国[MASK]非物质文化遗产。` → `现存最大的古代宫殿建筑, 也是`
  - `[sMASK]` 例：`[CLS]人工智能是一个以计算机科学为基础,…,[sMASK],具有非常巨大的前景。` → 一整段多句解释
  - `[gMASK]` 例：`[CLS]问题:啤酒伤胃吗?回答:[gMASK]` → 包含多个 `<n>` 段落的超长回答
- **原文：模型名**——示例中均使用 `GLM-large-ch`（中文大模型）；`download_path="./state_dict/"` 用于下载/加载权重。
- **原文：推理控制符**——生成以 `<|startofpiece|>` 作为生成内容起始标志，`<|endoftext|>` 作为结束标志。

> 注：原文档未给出训练 epoch、batch size、学习率、推理延迟、参数量、显存占用等性能数字，本文不臆造。

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**

（文档中仅以自然语言伪模板描述 MASK 行为，例如 "[SENTENCE]. It's really ___"、`[CLS]...[MASK]...<|endofpiece|>...` 等，没有 LaTeX 数学表达式或伪代码公式。）

---

## 【关联】

- **三种 MASK 方法之间的递进关系**：token → sentence → document，遮蔽粒度与生成长度依次增大，对应不同下游任务类型（短填空 → seq2seq 句子生成 → 长文本/问答生成）。三者共享同一推理入口 `predict_generate_randomsample`，仅通过输入 prompt 中的 MASK 类型标记切换。
- **预训练与微调的关联**：文档强调 `[sMASK]` 对应"seq2seq tasks whose predictions are often complete sentences or paragraphs"、`[gMASK]` 对应"long text generation"，体现预训练的多任务设定直接服务于下游任务设计。
- **FlagAI 框架组件关联**：`GLMModel`（模型） + `Tokenizer`（分词与下载配置） + `Predictor`（推理封装）三者协同，`Predictor.predict_generate_randomsample` 是统一生成接口。
- **与文档内无内部链接**（用户在任务中明确标注"内部链接: (无)"），但文档本身以教程形式暗示其位于 FlagAI 模型库的 GLM 系列教程中（编号 TUTORIAL_11），可视为 GLM 系列教程的一部分。

---

## 【使用方法】

文档给出了**三段可直接运行的 Python 示例**，分别对应 `[MASK]` / `[sMASK]` / `[gMASK]`，核心启用流程一致：

```python
import torch
from flagai.model.glm_model import GLMModel
from flagai.data.tokenizer import Tokenizer
from flagai.model.predictor.predictor import Predictor

model_name = 'GLM-large-ch'

# 加载分词器与模型（download_path 指定权重下载/缓存目录）
model = GLMModel.from_pretrain(model_name=model_name, download_path="./state_dict/")
tokenizer = Tokenizer.from_pretrained(model_name)

# 部署到 GPU
model.cuda(torch.cuda.current_device())

# 构造推理器
predictor = Predictor(model, tokenizer)

# 填空生成（按需替换 text 中的 MASK 类型）
text = '问题：啤酒伤胃吗？回答：[gMASK]'
output = predictor.predict_generate_randomsample(text)
print(text, '\n', output)
```

**关键配置项（原文出现的）**：
- `model_name`：取值为 `'GLM-large-ch'`。
- `download_path="./state_dict/"`：仅在第一段示例中出现，用于下载预训练权重到本地。
- `tokenizer = Tokenizer.from_pretrained("GLM-large-ch", only_download_config=False)`：第二、三段示例中传入 `only_download_config=False`，表示除配置外也下载必要文件。

**三种 MASK 的对应输入模板**（原文给出）：
1. `[MASK]`（token 级）：`'北京故宫是中国[MASK]非物质文化遗产。'`
2. `[sMASK]`（sentence 级）：`'人工智能是一个以计算机科学为基础，由计算机、数学、哲学等多学科交叉融合的交叉学科，[sMASK]，具有非常巨大的前景。'`
3. `[gMASK]`（document 级）：`'问题：啤酒伤胃吗？回答：[gMASK]'`

**原文未涉及**：训练脚本入口、学习率、batch size、GPU 卡数、推理超参（temperature、top-k/top-p、最大生成长度等）均未在文档中给出。
