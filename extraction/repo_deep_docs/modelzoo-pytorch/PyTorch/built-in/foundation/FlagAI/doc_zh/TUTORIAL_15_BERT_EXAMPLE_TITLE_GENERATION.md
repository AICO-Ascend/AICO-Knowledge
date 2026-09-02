# BERT 标题生成例子

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_15_BERT_EXAMPLE_TITLE_GENERATION.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_15_BERT_EXAMPLE_TITLE_GENERATION.md

# 一体化深度解读: BERT 标题生成 (FlagAI)

## 【定位】
本篇文档是 FlagAI 框架下,基于 RoBERTa-base-ch 的中文 seq2seq 微调教程,演示如何用 BERT 改造的序列到序列模型完成"长文本 → 短标题"的生成式摘要任务,给出了从数据加载、模型装载、训练到生成结果的端到端示例流程。

## 【技术要点】
1. **任务形式**: 输入一段中文长文本,模型生成对应的中文短标题,本质是 seq2seq 文本生成任务,在 FlagAI 中通过 `task_name="title-generation"` 注册。
2. **基础模型**: 采用 `RoBERTa-base-ch`(FlagAI 中文 RoBERTa),seq2seq 头通过 BertSeq2seqDataset 适配,即用 BERT 编码器 + 解码器的方式做生成。
3. **数据加载约定**: 样例数据位于 `/examples/bert_title_generation/data/`;`read_file()` 把每个 .strip('\n').lower() 处理后的样本同时放入 `src` 与 `tgt` 两个列表,二者下标一一对应。
4. **模型/切词器装载**: 使用 `flagai.auto_model.auto_loader.AutoLoader`,按 `task_name`、`model_dir`、`model_name` 三参数自动构建模型与切词器;若本地无 `config.json / pytorch_model.bin / vocab.txt` 三件套,会自动从 modelhub 拉取。
5. **训练超参(原文给定的具体数字)**:`batch_size=8`、`gradient_accumulation_steps=1`、`lr=2e-4`、`weight_decay=1e-3`、`epochs=10`、`log_interval=10`、`eval_interval=10000`、`save_interval=1`、实验名 `roberta_seq2seq`,并基于 `torch.cuda.is_available()` 自动选择 device。
6. **数据集与切分**:`BertSeq2seqDataset(src, tgt, tokenizer=tokenizer, maxlen=maxlen)` 构造样本;`train_size = int(data_len * 0.8)`,即按 8:2 比例切分训练集/验证集。
7. **生成阶段**: 显式从 `./checkpoints/<step>/mp_rank_00_model_states.pt` 载入权重后跑 `python ./generate.py`,原文以 `1001` 作为示例 step 编号。

## 【关键机制与数据】
**工作原理(按文档描述顺序还原)**

1. 数据预处理: `read_file()` 同时读取源文本与目标标题两条流,按行写入 `src` 与 `tgt` 列表,要求二者顺序一致。
2. 数据切分: 按 `int(data_len * 0.8)` 切分,前 80% 作为训练、后 20% 作为验证。
3. 模型装载: `AutoLoader(task_name="title-generation", model_dir="./state_dict/", model_name="RoBERTa-base-ch")` 同时返回 `model` 与 `tokenizer`。
4. 训练: 由 `Trainer` 对象统一封装,文档未给出 `train.py` 内部循环细节,只给出超参与调度间隔。
5. 生成: 加载 `model_save_path` 指向的 `pt` 权重文件,再调用 `generate.py`。

**示例输入/输出数据流(原文整段保留,共三对)**

| 原文输入(摘要) | 模型生成(标题) |
|---|---|
| "本文总结了十个可穿戴产品的设计原则而这些原则同样也是笔者认为是这个行业最吸引人的地方1为人们解决重复性问题2从人开始而不是从机器开始3要引起注意但不要刻意4提升用户能力而不是取代人" | "可 穿 戴 产 品 设 计 原 则 十 大 原 则" |
| "2007年乔布斯向人们展示iPhone并宣称它将会改变世界还有人认为他在夸大其词然而在8年后以iPhone为代表的触屏智能手机已经席卷全球各个角落未来智能手机将会成为真正的个人电脑为人类发展做出更大的贡献" | "乔 布 斯 宣 布 iphone 8 年 后 将 成 为 个 人 电 脑" |
| "雅虎发布2014年第四季度财报并推出了免税方式剥离其持有的阿里巴巴集团15％股权的计划打算将这一价值约400亿美元的宝贵投资分配给股东截止发稿前雅虎股价上涨了大约7％至5145美元" | "雅 虎 拟 剥 离 阿 里 巴 巴 15 ％ 股 权" |

(原文:) 性能数据(准确率、loss 曲线等)未在文档中给出。

## 【表格解读】
**原文无表格。** 上方"示例输入/输出数据流"为本人依据"结果展示"原文段归纳,不视为原文表格,故填"原文无表格"。

## 【公式解读】
**原文无公式。** `train_size = int(data_len * 0.8)` 出现在伪代码中,属程序语句而非数学公式,故填"原文无公式"。

## 【关联】
1. **框架归属**: 文档定位为 FlagAI(`flagai.auto_model.auto_loader`、`flagai.trainer`)在 modelzoo-pytorch 中的"built-in/foundation/FlagAI"目录下的中文样例之一,与其它 FlagAI 教程(同样基于 `AutoLoader + Trainer`)处于同一套使用范式之下。
2. **下游依赖**: 依赖 `BertSeq2seqDataset`,该类是 FlagAI 为"seq2seq / 标题生成"提供的 `Dataset` 实现;依赖 `Trainer` 调度机制(`env_type="pytorch"`、step 级保存 `mp_rank_00_model_states.pt`,表明底层配合分布式并行保存约定)。
3. **上下游**: 上游是从 modelhub 拉取或加载本地的 `RoBERTa-base-ch` 三件套 (`config.json`、`pytorch_model.bin`、`vocab.txt`);下游是 `./generate.py` 加载生成的 `pt` 文件做推理。文档未给出其它内部链接,文末注明"(无)"。
4. **同目录同主题**: 路径前缀 `PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_15_…` 表明该教程属于 FlagAI 中文文档序列中的第 15 篇,与其它 FlagAI 中文模型教程并列。

## 【使用方法】

**数据准备**
- 样例数据位置:`/examples/bert_title_generation/data/`
- 自定义数据:在 `trainer.py` 中按 `read_file()` 模式构造 `src` 与 `tgt` 两个等长列表,文本预处理为 `.strip('\n').lower()`。

**模型装载**
```python
from flagai.auto_model.auto_loader import AutoLoader
auto_loader = AutoLoader(task_name="title-generation",
                         model_dir="./state_dict/",
                         model_name="RoBERTa-base-ch")
model = auto_loader.get_model()
tokenizer = auto_loader.get_tokenizer()
```

**训练**
- 命令:`python ./train.py`
- 关键配置:
  | 配置项 | 原文取值 |
  |---|---|
  | env_type | "pytorch" |
  | experiment_name | "roberta_seq2seq" |
  | batch_size | 8 |
  | gradient_accumulation_steps | 1 |
  | lr | 2e-4 |
  | weight_decay | 1e-3 |
  | epochs | 10 |
  | log_interval | 10 |
  | eval_interval | 10000 |
  | load_dir | None |
  | pytorch_device | `torch.device("cuda" if torch.cuda.is_available() else "cpu")` |
  | save_dir | "checkpoints" |
  | save_interval | 1 |

**数据切分与 Dataset**
- 切分比例:`data_len * 0.8` 做训练,余下做验证。
- Dataset:`BertSeq2seqDataset(src, tgt, tokenizer=tokenizer, maxlen=maxlen)`(`maxlen` 的具体数值在原文 `train.py` 中给出,本教程文本未暴露)。

**生成(推理)**
1. 改写权重路径:`model_save_path = "./checkpoints/1001/mp_rank_00_model_states.pt"`(原文标注 `1001` 为示例,需按实际 step 改动)。
2. 执行:`python ./generate.py`,即可看到生成标题。
