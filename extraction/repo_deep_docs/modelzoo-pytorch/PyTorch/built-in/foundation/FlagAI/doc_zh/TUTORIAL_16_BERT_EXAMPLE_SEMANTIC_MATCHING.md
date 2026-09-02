# BERT 语义匹配例子

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_16_BERT_EXAMPLE_SEMANTIC_MATCHING.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_16_BERT_EXAMPLE_SEMANTIC_MATCHING.md

# 一体化深度解读:BERT 语义匹配例子

## 【定位】
这篇文档是 FlagAI/modelzoo-pytorch 仓中面向"中文句子对语义匹配"二分类任务的端到端快速上手教程,涵盖数据准备、模型加载、训练与推理生成的完整链路示例。

---

## 【技术要点】

1. **任务定义**:输入两句话,输出二分类(1=语义相同,0=语义不同),对应 FlagAI 中的 `classification` 任务类型。
2. **示例输入输出**:三条测试样本(`["后悔了吗","你有没有后悔"]`、`["打开自动横屏","开启移动数据"]`、`["我觉得你很聪明","你聪明我是这么觉得"]`)对应输出 `1 / 0 / 1`,验证模型对语序变化、否定词匹配、改写表达的语义理解。
3. **模型选择**:使用 `AutoLoader("classification", model_name="RoBERTa-base-ch", ...)`,基于中文 RoBERTa-base 预训练模型做微调;模型目录 `model_dir = "./state_dict/"` 需包含 `config.json / pytorch_model.bin / vocab.txt` 三件套,缺失时自动从 model hub 下载。
4. **训练超参数**:`batch_size=8`、`gradient_accumulation_steps=1`、`lr=1e-5`、`weight_decay=1e-3`、`epochs=10`、`log_interval=100`、`eval_interval=500`、`save_dir="checkpoints_semantic_matching"`、`save_interval=1`。
5. **数据切分**:按 `0.9 : 0.1` 比例将 `src/tgt` 切分为训练集与验证集,封装为 `BertClsDataset`。
7. **推理命令**:训练完成后通过 `python ./generate.py` 加载 `checkpoints_semantic_matching/9000/mp_rank_00_model_states.pt` 权重进行生成测试。

---

## 【关键机制与数据】

**工作原理与数据流(基于原文描述)**

- **原文**:任务流程图 `semantic_model.png` 显示句子对经过编码与匹配后输出二分类概率(图中为示意图)。
- **原文**:数据格式约束——`src` 为 `[[s1_1, s1_2], [s2_1, s2_2], ...]` 的二维列表,`tgt` 为 `[1, 0, ...]` 的一维整数列表;样例数据按行读取并按 `\t` 切分,字段顺序为 `句子1 \t 句子2 \t 标签`,仅保留 `len(line) == 3` 的合法行。
- **原文**:`read_file` 函数返回 `(src, tgt)`,但函数体内变量名存在笔误(同时使用 `sents_tgt/sents_src` 与 `src/tgt`),读者需按外层返回名理解。
- **原文**:训练入口为 `python ./train.py`,推理入口为 `python ./generate.py`;推理时显式指向 `./checkpoints_semantic_matching/9000/mp_rank_00_model_states.pt` 这一具体 step 权重(步骤号 9000)。
- **原文**:设备自适应——`device = torch.device("cuda" if torch.cuda.is_available() else "cpu")`,通过 `Trainer(... pytorch_device=device ...)` 注入。
- **原文**:性能数据(训练耗时、准确率、loss 曲线等):原文未涉及。

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

- **上游/下游模块**:依赖 `flagai.auto_model.auto_loader.AutoLoader`(统一模型/分词器加载入口)、`flagai.trainer.Trainer`(训练管理器)、`BertClsDataset`(句子对分类数据集封装)——这些是 FlagAI 框架的核心 API,文档演示了它们在 `classification` 任务上的协同用法。
- **关联产物**:训练产物落到 `./checkpoints_semantic_matching/` 目录(包含 step 级 `mp_rank_00_model_states.pt`),供后续 `generate.py` 加载,形成"训练—推理"闭环。
- **数据依赖**:样例数据位于仓内 `examples/bert_semantic_matching/data/`,需保证行格式为 `句子1\t句子2\t标签` 以匹配 `read_file` 的切分逻辑。
- **图片引用**:文中引用 `./img/semantic_matching_model.png` 作为任务示意图(路径与仓内结构相对应),为唯一外部资源依赖。
- **内部链接**:原文未提供任何内部链接。

---

## 【使用方法】

**1. 数据准备(原文)**

```python
# 示例:从 examples/bert_semantic_matching/data/ 读取
def read_file(data_path):
    src, tgt = [], []
    with open(data_path) as f:
        lines = f.readlines()
    for line in lines:
        line = line.split("\t")
        if len(line) == 3:
            sents_tgt.append(int(line[2]))      # 注:原文变量名,应理解为 src/tgt
            sents_src.append([line[0], line[1]])
    return src, tgt
```

**2. 模型与分词器加载(原文)**

```python
from flagai.auto_model.auto_loader import AutoLoader

model_dir = "./state_dict/"
auto_loader = AutoLoader("classification",
                         model_name="RoBERTa-base-ch",
                         model_dir=model_dir)
model = auto_loader.get_model()
tokenizer = auto_loader.get_tokenizer()
```

**3. 训练(原文)**

- 命令行启动:`python ./train.py`
- Trainer 配置:`env_type="pytorch"`、`batch_size=8`、`gradient_accumulation_steps=1`、`lr=1e-5`、`weight_decay=1e-3`、`epochs=10`、`log_interval=100`、`eval_interval=500`、`load_dir=None`、`save_dir="checkpoints_semantic_matching"`、`save_interval=1`。
- 数据切分比例:`train_size = int(data_len * 0.9)`,验证集为尾部 `0.1`。

**4. 推理/生成(原文)**

- 权重路径配置:`model_save_path = "./checkpoints_semantic_matching/9000/mp_rank_00_model_states.pt"`
- 命令行启动:`python ./generate.py`,运行后查看输出结果。

**注**:关于 eval 指标(accuracy、F1 等)、最大序列长度、`max_seq_len`、训练总 step 数等配置项,原文未涉及。
