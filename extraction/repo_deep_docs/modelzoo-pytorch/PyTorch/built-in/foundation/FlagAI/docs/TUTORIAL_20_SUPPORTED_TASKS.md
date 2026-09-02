# All supported tasks

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_20_SUPPORTED_TASKS.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_20_SUPPORTED_TASKS.md

# 深度解读: FlagAI 支持的任务与模型

## 【定位】

这篇文档说明 FlagAI 框架中 **AutoLoader** 通过 `task_name` 参数支持的全部下游任务类型,以及不同模型架构与任务的适配关系,作为用户选用预训练模型完成分类/序列标注/Seq2Seq 等任务的快速参考。

---

## 【技术要点】

1. **统一加载入口 AutoLoader**: 通过 `from flagai.auto_model.auto_loader import AutoLoader` 导入,根据 `task_name` 自动构建对应任务的模型。
2. **五大支持任务**:
   - `task_name="classification"` — 文本分类、语义匹配、情感分析等
   - `task_name="seq2seq"` — 自动摘要、对联生成、对话生成等
   - `task_name="sequence_labeling"` — NER、词性标注、中文分词等
   - `task_name="sequence_labeling_crf"` — 在序列标注模型上添加 **条件随机场(CRF)** 层
   - `task_name="sequence_labeling_gp"` — 在序列标注模型上添加 **全局指针(Global Pointer)** 层
3. **三类模型架构与任务的对应关系**:
   - **Transformer 编码器**(如 `BERT-base-ch`、`RoBERTa-base-ch`)— 支持上述全部任务
   - **Transformer 解码器**(如 `GPT2-base-ch`)— 仅支持 `seq2seq`
   - **编码器+解码器**(如 `T5-base-ch`)— 支持 `seq2seq`
4. **加载关键参数**:
   - `task_name="seq2seq"`
   - `model_name="RoBERTa-base-ch"`
   - `load_pretrain_params=True`
5. **获取组件**: `auto_loader.get_model()` 获取模型对象,`auto_loader.get_tokenizer()` 获取 tokenizer。

---

## 【关键机制与数据】

**工作原理(原文机制)**:
- 原文: *"You can input the different 'task_name' parameters in AutoLoader to load model to perform different task."*
- 原文: *"We construct a roberta seq2seq model by the AutoLoader class."*
- 用户通过实例化 `AutoLoader` 类,传入 `task_name`(决定任务类型,如 `seq2seq`)与 `model_name`(决定模型架构,如 `RoBERTa-base-ch`),框架据此自动构建匹配的模型结构与加载预训练权重。
- **CRF 层与 Global Pointer 层**仅作为 `sequence_labeling` 基础结构之上的可选输出层变体,用于提升序列标注任务性能(原文未给出具体性能数字,仅描述其作用)。

**数据流(原文)**:
1. 实例化 `AutoLoader("seq2seq", model_name="RoBERTa-base-ch", load_pretrain_params=True)`
2. 调用 `get_model()` → 返回针对 `seq2seq` 任务构造的 RoBERTa 模型
3. 调用 `get_tokenizer()` → 返回对应 tokenizer

**性能数据**: 原文未提供任何 benchmark 数字、训练吞吐量或推理延迟。

---

## 【表格解读】

**原文无表格**。文档以编号列表和分段文字形式枚举任务与模型,未出现参数表、性能对比表或配置项表格。

---

## 【公式解读】

**原文无公式**。全文为 API 用法说明与任务/模型枚举,未涉及任何数学表达式或伪代码算法。

---

## 【关联】

- **模型库 (model hub)**: 原文 *"All supported models is can be found in **model hub**."* — 文档将所有可用模型的完整列表指向外部"模型中心",本文档只给出代表性示例(`BERT-base-ch`、`RoBERTa-base-ch`、`GPT2-base-ch`、`T5-base-ch`)。
- **任务↔模型映射**: 同一 `task_name` 在不同 `model_name` 下表现能力不同——例如 `seq2seq` 在 `RoBERTa-base-ch`(编码器)下可行,在 `GPT2-base-ch`(解码器)下以"续写"形式实现,在 `T5-base-ch`(编解码)下以"文本到文本"形式实现。
- **变体关系**: `sequence_labeling_crf` 与 `sequence_labeling_gp` 均为 `sequence_labeling` 基础任务的输出层增强变体,属于上下游扩展关系。
- 原文未提供其他内部章节/链接(文末"内部链接: 无")。

---

## 【使用方法】

**原文涉及的启用方式**:

```python
from flagai.auto_model.auto_loader import AutoLoader

auto_loader = AutoLoader(
    "seq2seq",                          # task_name
    model_name="RoBERTa-base-ch",       # 模型名
    load_pretrain_params=True,          # 是否加载预训练参数
)
model = auto_loader.get_model()
tokenizer = auto_loader.get_tokenizer()
```

**配置项(原文枚举)**:
| 任务类型 | 适用场景示例 | 适配模型类型 |
|---|---|---|
| `classification` | 文本分类、语义匹配、情感分析 | Transformer 编码器 |
| `seq2seq` | 摘要生成、对联、对话 | 编码器 / 解码器 / 编解码器 |
| `sequence_labeling` | NER、词性标注、中文分词 | Transformer 编码器 |
| `sequence_labeling_crf` | 同上 + CRF 输出层 | Transformer 编码器 |
| `sequence_labeling_gp` | 同上 + Global Pointer 输出层 | Transformer 编码器 |

**具体命令**: 原文未给出命令行 CLI 形式的启动指令,仅以 Python API 形式示例。详细模型清单需查阅"model hub"(原文未列出)。
