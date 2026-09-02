# Bert example: Title Generation

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_15_BERT_EXAMPLE_TITLE_GENERATION.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_15_BERT_EXAMPLE_TITLE_GENERATION.md

# 一体化深度解读:Bert 标题生成示例

## 【定位】
这篇文档解决「给定一段长文本,用 BERT(seq2seq 模式)自动生成对应中文标题」的任务,展示了基于 FlagAI 框架的端到端工作流(数据加载 → 模型加载 → 训练 → 生成)。

---

## 【技术要点】

1. **任务类型**:Seq2Seq 文本生成任务,输入一段文章,模型输出标题。
2. **模型选型**:通过 `AutoLoader("seq2seq", model_name="RoBERTa-base-ch")` 加载中文 RoBERTa-base 用作 seq2seq 编解码器;模型目录包含 `config.json`、`pytorch_model.bin`、`vocab.txt`。
3. **数据准备**:从 `/examples/bert_title_generation/data/` 读取,自定义 `read_file()` 函数分别读取源文 `src` 与目标 `tgt` 两个文件,并统一做 `.lower()` 处理。
4. **训练配置**(`Trainer` 关键参数,原文):
   - `env_type="pytorch"`
   - `batch_size=8`,`gradient_accumulation_steps=1`
   - `lr=2e-4`,`weight_decay=1e-3`
   - `epochs=10`,`log_interval=10`,`eval_interval=10000`
   - `save_dir="checkpoints"`,`save_interval=1`
5. **数据集切分**:按 `data_len * 0.8` 划分训练/验证集,使用 `BertSeq2seqDataset(tokenizer=tokenizer, maxlen=maxlen)` 包装。
6. **推理入口**:单独运行 `generate.py`,需将保存的模型路径指向 `./checkpoints/1001/mp_rank_00_model_states.pt`(1001 为示例编号)。

---

## 【关键机制与数据】

**工作原理/数据流**:
- 数据流:`read_file()` → `src/tgt` 列表 → 按 8:2 切分为 `train_src/train_tgt` 与 `val_src/val_tgt` → 包装为 `BertSeq2seqDataset` → `Trainer` 训练 → 保存至 `checkpoints/{step}/mp_rank_00_model_states.pt` → `generate.py` 加载并解码生成。
- 设备自动检测:`torch.device("cuda" if torch.cuda.is_available() else "cpu")`。
- 任务标识:`task_name="seq2seq"`、`experiment_name="roberta_seq2seq"`。
- 启动命令:`python ./train.py`(训练)、`python ./generate.py`(生成)。

**示例数据(原文展示的真实输入输出)**:
| 输入文本主题 | 模型生成标题 |
|---|---|
| 十个可穿戴产品设计原则 | 可 穿 戴 产 品 设 计 原 则 十 大 原 则 |
| 乔布斯展示 iPhone | 乔 布 斯 宣 布 iphone 8 年 后 将 成 为 个 人 电 脑 |
| 雅虎剥离阿里股权 | 雅 虎 拟 剥 离 阿 里 巴 巴 15 ％ 股 权 |

(原文:从中文长文中抽取「行业要点 / 时间节点 / 关键事件」等核心要素并压缩为短标题,标题中保留数字与专有名词。)

---

## 【表格解读】
**原文无表格**(原文中仅有 3 组 Input/Output 文本对照示例与一段代码示例,未给出正式的参数表或性能对比表)。

---

## 【公式解读】
**原文无公式**(全文未出现任何 LaTeX 数学公式或伪代码公式)。

---

## 【关联】
本示例涉及 FlagAI 框架下以下组件/模块的协同使用:
- **`flagai.auto_model.auto_loader.AutoLoader`**:负责根据 `task_name` 与 `model_name` 自动构建模型与 tokenizer,并支持从本地目录或模型 hub 下载权重。
- **`flagai.trainer.Trainer`**:统一的训练循环封装,负责分布式/单卡环境下的梯度累积、日志、保存等。
- **`BertSeq2seqDataset`**(FlagAI 内置数据集类):负责把 `src/tgt` 列表用 tokenizer 编码并构造监督数据。
- **`/examples/bert_title_generation/data/`**:训练用样本数据所在目录。
- 配套脚本:`train.py`(训练入口)、`generate.py`(推理入口)。

文档提示修改 `train.py` 中的 `read_file()` 以适配自有数据,说明 `BertSeq2seqDataset` 与数据加载层是可替换的接口。

---

## 【使用方法】

**原文有,原文如下配置/命令**:

**1. 数据加载**(在 `train.py` 中定义 `read_file()`,从两文件分别读入 `src`、`tgt`,并做 `lower()`):
```python
def read_file():
    src = []
    tgt = []
    with open(src_dir, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            src.append(line.strip('\n').lower())
    with open(tgt_dir, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            tgt.append(line.strip('\n').lower())
    return src, tgt
```

**2. 加载模型与 tokenizer**:
```python
from flagai.auto_model.auto_loader import AutoLoader
auto_loader = AutoLoader("seq2seq",
                         model_dir="./state_dict/",
                         model_name="RoBERTa-base-ch")
model = auto_loader.get_model()
tokenizer = auto_loader.get_tokenizer()
```

**3. 启动训练**:
```commandline
python ./train.py
```

**4. 训练超参(原文)**:
```python
trainer = Trainer(env_type="pytorch",
                  experiment_name="roberta_seq2seq",
                  batch_size=8, gradient_accumulation_steps=1,
                  lr=2e-4, weight_decay=1e-3,
                  epochs=10, log_interval=10, eval_interval=10000,
                  load_dir=None, pytorch_device=device,
                  save_dir="checkpoints", save_interval=1)
```

**5. 数据集构建(原文 8:2 切分)**:
```python
sents_src, sents_tgt = read_file()
data_len = len(sents_tgt)
train_size = int(data_len * 0.8)
train_src, train_tgt = sents_src[:train_size], sents_tgt[:train_size]
val_src, val_tgt     = sents_src[train_size:], sents_tgt[train_size:]
train_dataset = BertSeq2seqDataset(train_src, train_tgt, tokenizer=tokenizer, maxlen=maxlen)
val_dataset   = BertSeq2seqDataset(val_src,   val_tgt,   tokenizer=tokenizer, maxlen=maxlen)
```

**6. 推理(修改路径后运行)**:
```python
model_save_path = "./checkpoints/1001/mp_rank_00_model_states.pt"
```
```commandline
python ./generate.py
```
