# bert4torch使用教程

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/nlp/Bert-CRF_for_PyTorch/examples/tutorials/Tutorials.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/nlp/Bert-CRF_for_PyTorch/examples/tutorials/Tutorials.md

# bert4torch 使用教程 · 一体化深度解读

## 【定位】

这篇文档是 **bert4torch** 框架（一个基于 PyTorch 的 BERT/Transformer 训练框架）的**官方入门使用教程**，通过一个完整的"文本二分类"建模流程示例，系统讲解该框架的**数据处理、模型定义、训练/评估、模型保存与加载、以及单机多卡训练**等核心使用方式，旨在让用户快速上手基于 bert4torch 进行各类 Transformer 任务的定制化训练。

---

## 【技术要点】

1. **建模流程一站式**：通过 `Tokenizer` + `build_transformer_model` + `BaseModel` 派生 + `model.compile` + `model.fit` 五步组合完成一个文本二分类任务的训练闭环，示例中 `dropout=0.1`、分类头维度 `Linear(768, 2)`、`optim.Adam(lr=2e-5)`、`epochs=20`、`steps_per_epoch=100`、`grad_accumulation_steps=2`。
2. **数据处理工具集**：`load_vocab()` 支持精简词表，`Tokenizer` 支持 `encode/decode`，`text_segmentate()` 用于按 maxlen 截断（每次截断最长句），`sequence_padding` 用于批内 padding 对齐，`parallel_apply` 支持多进程/多线程，`seed_everything` 固定全局随机种子。
3. **`build_transformer_model` 灵活构建**：`model` 参数切换模型结构，`application` 支持 `encoder` / `lm` / `unilm` 三种应用模式，`with_pool` / `with_nsp` / `with_mlm` 三类输出头独立开关，`segment_vocab_size=2` 为默认 type_token 数量，不传 segment_ids 时需置 0；支持 `layer_add_embs` 注入额外 `nn.Embedding`。
4. **编译与对抗训练**：`model.compile(loss, optimizer, scheduler, metrics)` 接受自定义函数；`metrics` 支持 `'accuracy'` 字符串、自定义函数、字典 `{'f1': f1}` 三种形式；`adversarial_train={'name': 'fgm'}` 内置 `fgm` / `pgd` / `gradient_penalty` / `vat` 四种对抗/正则训练 trick。
5. **评估与回调机制**：通过 `Callback` 子类化实现，按 `on_train_begin` / `on_train_end` / `on_batch_begin` / `on_batch_end` / `on_epoch_begin` / `on_epoch_end` / `on_dataloader_end` 等钩子插桩；示例中仅在 `on_epoch_end` 计算 `val_acc` 并保存最优权重 `best_model.pt`。
6. **断点续训与跨框架兼容**：提供 `save_steps_params` / `load_steps_params` 保存/恢复 `epoch` 和 `step`；`save_weights` 的 `prefix` 参数控制保存 key 前缀（兼容其他训练框架加载）；支持直接 `from_pretrained` 加载 HuggingFace `transformers` 模型。

---

## 【关键机制与数据】

**工作原理/数据流：**

- **数据流**：`Tokenizer(dict_path, do_lower_case=True)` → `MyDataset.load_data(filenames)` 返回 list → `DataLoader(..., collate_fn=collate_fn)` → `collate_fn` 把样本整理成 `(features, labels)`，其中 features 为 `[token_ids, segment_ids]` 的 list/tuple（**原文注**："返回值分为 feature 和 label，feature 可整理成 list 或 tuple"）。
- **模型前向**：`self.bert([token_ids, segment_ids])` —— 原文特别说明 `build_transformer_model` 得到的模型**仅接受 list/tuple 传参**，因此即使只有一个入参也要包装成 `[token_ids]`；返回 `hidden_states` 与 `pooled_output`，分类任务取 `pooled_output` 经 `Dropout(0.1)` 后送入 `Linear(768, 2)`。
- **训练闭环**：`model.fit(train_dataloader, epochs=20, steps_per_epoch=100, grad_accumulation_steps=2, callbacks=[...])` —— `steps_per_epoch=100` 表示每个 epoch 跑 100 个 batch，`grad_accumulation_steps=2` 表示梯度累积步数。
- **返回值结构**：原文说明：若同时设置 `with_pool, with_nsp, with_mlm`，则返回值依次为 `[hidden_states, pool_emb/nsp_emb, mlm_scores]`，否则只返回 `hidden_states`。
- **`prefix` 机制**：原文说明 `save_weights` 的 `prefix` 默认 `None` 不启用；若基于 `BaseModel` 自定义模型，需指定为 bert 模型对应的成员变量名（如 `bert`），直接使用则设为 `''`，"主要是为了别的训练框架容易加载"。
- **对抗训练开关**：原文：`adversarial_train={'name': 'fgm'}`，支持 `fgm`、`pgd`、`gradient_penalty`、`vat` 四种。

**性能数据：** 原文**未给出**任何训练时长、吞吐、显存占用等基准数字，仅示例性写出 `lr=2e-5`、`epochs=20`、`steps_per_epoch=100` 等超参与 `val_acc: {val_acc:.5f}` 这类占位格式。

---

## 【表格解读】

**原文无表格**（除代码块中以注释形式列出的参数列表）。为方便参考，将代码注释中两处关键参数项整理如下（**内容完全来自原文**，仅排版为表格形式）：

### 表 1：`build_transformer_model` 关键参数（源自原文代码注释）

| 参数 | 默认/示例值 | 作用 |
|---|---|---|
| `config_path` | — | 模型的 config 文件地址 |
| `checkpoint_path` | `None` | 模型文件地址，默认 `None` 表示不加载预训练模型 |
| `model` | `'bert'` | 加载的模型结构；`Model` 也可以基于 `nn.Module` 自定义后传入 |
| `application` | `'encoder'` | 模型应用，支持 `encoder`、`lm`、`unilm` 格式 |
| `segment_vocab_size` | `2` | type_token_ids 数量；不传入 segment_ids 时需设置为 `0` |
| `with_pool` | `False` | 是否包含 Pool 部分 |
| `with_nsp` | `False` | 是否包含 NSP 部分 |
| `with_mlm` | `False` | 是否包含 MLM 部分 |
| `return_model_config` | `False` | 是否返回模型配置参数 |
| `output_all_encoded_layers` | `False` | 是否返回所有 hidden_state 层 |
| `layer_add_embs` | `nn.Embedding(2, 768)` | 自定义额外的 embedding 输入 |

### 表 2：`model.compile` 关键参数（源自原文代码注释）

| 参数 | 示例值 | 说明 |
|---|---|---|
| `loss` | `nn.CrossEntropyLoss()` | 可自定义 Loss |
| `optimizer` | `optim.Adam(model.parameters(), lr=2e-5)` | 可自定义优化器 |
| `scheduler` | `None` | 可自定义 scheduler |
| `adversarial_train` | `{'name': 'fgm'}` | 训练 trick 方案，支持 `fgm`、`pgd`、`gradient_penalty`、`vat` |
| `metrics` | `['accuracy', eval, {'f1': f1}]` | loss 等默认打印字段无需设置；支持字符串、自定义函数、字典三种自定义方式 |

### 表 3：`Callback` 钩子时机（源自原文代码注释）

| 钩子 | 触发时机 | 原文注释要点 |
|---|---|---|
| `on_dataloader_end` | dataloader 结束 | 可用于重新生成 dataloader（如多文件预训练场景） |
| `on_train_begin` | 训练开始 | — |
| `on_train_end` | 训练结束 | — |
| `on_batch_begin` | batch 开始 | — |
| `on_batch_end` | batch 结束 | 可用于后台记录 log、写 tensorboard；**原文提示**："尽量不要在 batch_begin 和 batch_end 中 print，防止打断进度条功能" |
| `on_epoch_begin` | epoch 开始 | — |
| `on_epoch_end` | epoch 结束 | 示例中用于计算 val_acc 并保存最优权重 |

---

## 【公式解读】

**原文无公式**（无 LaTeX 或伪代码形式的数学公式）。仅有占位性指标示例（如 `rouge-1`、`rouge-2`、`rouge-l`、`bleu` 与 `random.random()` 伪返回值），不构成可解析的数学式。

---

## 【关联】

文档通过外链与文末内部链接，建立了与框架其他示例模块的横向关系：

1. **`tutorials_custom_fit_progress.py`**（外链：https://github.com/Tongjilibo/bert4torch/blob/master/examples/tutorials/tutorials_custom_fit_progress.py）
   对应文档中"自定义训练过程"小节，演示当内置 `fit()` 不满足需求时，如何在 `BaseModel` 子类中重写 `fit(self, train_dataloader, steps_per_epoch, epochs)`，使用 `cycle(train_dataloader)` 循环取数并手动 `loss.backward()` / `optimizer.step()` / `optimizer.zero_grad()`。**它是 `model.fit()` 的可替换实现示例。**

2. **`tutorials_load_transformers_model.py`**（外链：https://github.com/Tongjilibo/bert4torch/blob/master/examples/tutorials/tutorials_load_transformers_model.py）
   对应"加载 transformers 模型进行训练"小节，演示从 `transformers` 库 `from_pretrained("file_path", num_labels=2)` 加载 `AutoModelForSequenceClassification`，并在 `BaseModel` 子类中以 `input_ids` / `attention_mask` / `token_type_ids` 三参调用，最后返回 `output.logits`。**它是与 HuggingFace 生态互操作的桥接模块。**

3. **上下游关系**：
   - 上游：`bert4torch.tokenizers`（分词器） → `bert4torch.models`（`build_transformer_model`、`BaseModel`、`BaseModelDP`） → `bert4torch.snippets`（`Callback`、`Logger`、`Tensorboard`、`ListDataset`）。
   - 文档中"单机多卡训练"小节开头引入 `from bert4torch.models import BaseModelDP`，是 `BaseModel` 的 DP 封装子类，属于 `models` 模块的下游用法。

4. **本文件在仓库中的位置**：位于 `PyTorch/built-in/nlp/Bert-CRF_for_PyTorch/examples/tutorials/Tutorials.md`，作为 Bert-CRF_for_PyTorch 仓内引入 bert4torch 框架后的使用教程，属于**外部框架教程文档**（非 Bert-CRF 模型自身实现）。

---

## 【使用方法】

### 启用方式（原文有的全部列示）

**1) 最小可运行流程的启用步骤：**

```python
# Step1: 建立分词器
tokenizer = Tokenizer(dict_path, do_lower_case=True)

# Step2: 自定义 Dataset（继承 ListDataset）
class MyDataset(ListDataset):
    @staticmethod
    def load_data(filenames):
        D = []
        return D

# Step3: 自定义 collate_fn（返回 [features], label 形式）
def collate_fn(batch):
    batch_token_ids, batch_segment_ids, batch_labels = [], [], []
    return [batch_token_ids, batch_segment_ids], batch_labels.flatten()

# Step4: DataLoader
train_dataloader = DataLoader(MyDataset('file_path'), batch_size=batch_size, shuffle=True, collate_fn=collate_fn)

# Step5: 定义 Model（继承 BaseModel）
class Model(BaseModel):
    def __init__(self):
        super().__init__()
        self.bert = build_transformer_model(config_path, checkpoint_path, with_pool=True)
        self.dropout = nn.Dropout(0.1)
        self.dense = nn.Linear(768, 2)
    def forward(self, token_ids, segment_ids):
        hidden_states, pooled_output = self.bert([token_ids, segment_ids])
        return self.dense(self.dropout(pooled_output))
model = Model().to(device)

# Step6: compile
model.compile(loss=nn.CrossEntropyLoss(),
              optimizer=optim.Adam(model.parameters(), lr=2e-5),
              scheduler=None,
              metrics=['accuracy'])

# Step7: 定义 Evaluator（Callback 子类）

# Step8: fit
model.fit(train_dataloader, epochs=20, steps_per_epoch=100, grad_accumulation_steps=2,
          callbacks=[evaluator, Logger('./test/test.log'), Tensorboard('./test/')])
```

**2) 配置项速查（按原文出现顺序）：**

| 配置项 | 取值/示例 | 出处 |
|---|---|---|
| 精简词表 | `load_vocab(dict_path, simplified=True, startswith=['[PAD]','[UNK]','[CLS]','[SEP]'])` | §2.1.a |
| 模型 application 模式 | `'encoder'` / `'lm'` / `'unilm'` | §2.2 build_transformer_model |
| 对抗训练 | `adversarial_train={'name': 'fgm'}`，可选 `fgm` / `pgd` / `gradient_penalty` / `vat` | §2.2 model.compile |
| metrics 写法 | 字符串 / 函数 / `{'f1': f1}` 字典三种 | §2.2 model.compile |
| 保存权重前缀 | `model.save_weights(save_path, prefix=None)`；基于 `BaseModel` 自定义时按成员变量名指定 | §2.2 模型保存和加载 |
| DP 多卡 | `model = BaseModelDP(model)`；loss 需 `lambda x, _: x.mean()` | §3.1.a |
| 加载 transformers | `AutoModelForSequenceClassification.from_pretrained("file_path", num_labels=2)` | §2.2 加载 transformers |

**3) 训练命令（原文未涉及命令行/Shell 启动方式）**：原文示例以 `if __name__ == '__main__':` 直接 `model.fit(...)` 启动，未给出独立 CLI 命令或 torchrun / accelerate 等启动脚本。
