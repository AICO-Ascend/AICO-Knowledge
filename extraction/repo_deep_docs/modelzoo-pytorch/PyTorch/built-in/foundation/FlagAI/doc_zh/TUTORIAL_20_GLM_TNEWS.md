# 所有支持的任务

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_20_GLM_TNEWS.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_20_GLM_TNEWS.md

# 一体化深度解读: FlagAI 「所有支持的任务」Guide

## 【定位】
本篇文档解决"在 FlagAI 中如何通过 AutoLoader 的 task_name 参数, 按任务类型加载对应模型"的问题, 即描述 FlagAI 框架所支持的全部 NLP 任务类别及其适配模型结构的总览能力。

## 【技术要点】

1. **统一入口 AutoLoader**: 通过 `flagai.auto_model.auto_loader.AutoLoader` 类, 以 `"task_name"` 字符串作为任务分发开关, 同入口完成模型与分词器加载。
2. **五种任务类型 (task_name 取值)**:
   - `classification`: 文本分类、语义匹配、情感分析等
   - `seq2seq`: 标题自动生成、对联自动生成、自动对话
   - `sequence_labeling`: 实体检测、词性标注、中文分词
   - `sequence_labeling_crf`: 在序列标注上叠加条件随机场 (CRF) 层
   - `sequence_labeling_gp`: 在序列标注上叠加全局指针 (Global Pointer) 层
3. **三族模型架构与任务适配关系**:
   - Transformer 编码器类 (如 `BERT-base-ch`、`RoBERTa-base-ch`): 支持上述全部任务
   - Transformer 解码器类 (如 `GPT2-base-ch`): 仅支持 `seq2seq`
   - 编码器+解码器类 (如 `T5-base-ch`): 仅支持 `seq2seq`
4. **预训练参数开关**: `load_pretrain_params=True` 控制是否载入预训练权重。
5. **Predictor 配套**: 除 AutoLoader 外, 还需 `from flagai.model.predictor.predictor import Predictor` 用于推理, 文档以导入语句出现但未展开用法。
6. **示例任务组合**: 文档示例展示 `task_name="seq2seq"` + `model_name="RoBERTa-base-ch"` 的组合 (注: 此处与下文"RoBERTa 编码器仅与所有任务兼容"声明在原文层面同时存在, 未做冲突说明)。

## 【关键机制与数据】

- **工作原理 (原文)**: 文档原文描述的机制为——"您可以在 AutoLoader 中输入不同的'task_name'参数来加载模型以执行不同的任务", 即通过 task_name 字符串驱动 AutoLoader 完成模型分支选择与权重装配。
- **数据流 (原文)**: 实例代码链路为 `AutoLoader("seq2seq", model_name="RoBERTa-base-ch", load_pretrain_params=True)` → `get_model()` 获得 model 对象 → `get_tokenizer()` 获得 tokenizer 对象; Predictor 与 model/tokenizer 共同构成下游使用链路 (Predictor 的具体调用在原文中未展开)。
- **性能数据**: 原文未涉及任何训练/推理性能指标、参数量、吞吐或基准数字。
- **关键开关 (原文)**: `task_name`、`model_name`、`load_pretrain_params=True`, 三者共同决定最终载入的模型形态。

## 【表格解读】

原文无表格 (任务清单以编号列表形式给出, 未使用 markdown 表格)。

## 【公式解读】

原文无公式。

## 【关联】

- **与「模型仓 (model hub)」的关联**: 原文末尾明确"所有支持的模型都可以在 model hub 中找到", 即 task/model 矩阵的"模型"维度由 model hub 提供, 本文档承担"任务维度"的总览角色, 二者构成 task×model 笛卡尔矩阵的两个轴。
- **任务-模型适配链 (原文)**: 
  - `classification` / `seq2seq` / `sequence_labeling` / `sequence_labeling_crf` / `sequence_labeling_gp` ↔ Transformer 编码器族 (BERT-base-ch、RoBERTa-base-ch)
  - `seq2seq` ↔ Transformer 解码器族 (GPT2-base-ch) 与编解码族 (T5-base-ch)
- **下游组件**: `Predictor` 作为推理入口被同一示例段引入, 与 AutoLoader 输出的 model/tokenizer 配对使用 (原文未给出具体调用方式)。
- **内部链接**: 原文无内部链接。

## 【使用方法】

**启用方式 (原文示例, 逐字保留命令)**:

```python
from flagai.auto_model.auto_loader import AutoLoader
from flagai.model.predictor.predictor import Predictor

auto_loader = AutoLoader(
    "seq2seq",
    model_name="RoBERTa-base-ch",
    load_pretrain_params=True,
)
model = auto_loader.get_model()
tokenizer = auto_loader.get_tokenizer()
```

**配置项 (原文)**:
- `task_name` ∈ {`classification`, `seq2seq`, `sequence_labeling`, `sequence_labeling_crf`, `sequence_labeling_gp`}
- `model_name` ∈ {`BERT-base-ch`, `RoBERTa-base-ch`, `GPT2-base-ch`, `T5-base-ch`, …} (以 model hub 中可获取的为准)
- `load_pretrain_params`: 布尔值, 示例中为 `True`

**任务→模型选用准则 (原文)**:
- 任意任务: 选编码器族模型 (`BERT-base-ch` / `RoBERTa-base-ch`)
- 仅做 seq2seq: 选编码器族、解码器族 (`GPT2-base-ch`) 或编解码族 (`T5-base-ch`)

**未涉及项**: 原文未提供训练/推理完整 pipeline 命令、超参、batch size、学习率等配置; Predictor 的具体调用、`task_name` 与 `model_name` 的组合校验逻辑亦未展开。
