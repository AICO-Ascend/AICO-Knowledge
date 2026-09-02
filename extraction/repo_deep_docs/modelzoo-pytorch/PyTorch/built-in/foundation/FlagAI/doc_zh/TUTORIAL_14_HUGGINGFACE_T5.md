# 支持 Huggingface t5

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_14_HUGGINGFACE_T5.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_14_HUGGINGFACE_T5.md

# 一体化深度解读: 支持 Huggingface T5

## 【定位】

这篇文档解决"在 modelzoo-pytorch 框架下, 如何把 Huggingface `transformers` 的 T5(seq2seq)模型接入到 `easybigmodel.trainer.Trainer` 中进行训练/微调, 以及当受限于 V100 32G 显存的硬件时, 如何通过 5 个递进的技巧(fp16 → 梯度重计算 → DDP → DeepSpeed → DeepSpeed+Megatron-LM)逐步提升 t5-11b 的可训练 batch size 和吞吐"的问题。

---

## 【技术要点】

1. **Trainer 继承 + `forward_step` 重写**: 自定义 `MyTrainer(Trainer)`, 重写 `forward_step(self, data, model, mems)`, 在内部调用 `model(**data)` 拿到 Huggingface `T5ForConditionalGeneration` 的输出, 然后把 `model_outputs.loss / logits / decoder_hidden_states` 重新打包成 `{loss, logits, hidden_states}` 的 dict 返回, 以匹配 `easybigmodel` 训练器对 step 输出的约定。
2. **数据加载与切分**: 源/目标分别从 `train_inputs.txt` 与 `train_targets.txt` 读入, 行级 `strip('\n').lower()`; 按 80/20 切分训练集/验证集; 使用 `BertSeq2seqDataset`(`maxlen=1024`)以及 `seq2seq_collate_fn`(对 `input_ids` 和 `labels` 分别按当前 batch 最大长度补 0)。
3. **Tokenizer 双上下文**: 源端 `tokenizer(src)`; 目标端必须用 `with tokenizer.as_target_tokenizer():` 包裹后 `tokenizer(tgt)`, 把 `labels.input_ids` 单独保存, 与 encoder 输入解耦。
4. **加速阶梯(原文明确的 5 步)**:
   - **第一步 fp16**: `fp16=True`, `batch_size` 从 `4` 降到 `1`。
   - **第二步 梯度重计算(checkpoint)**: `model.gradient_checkpointing = True`, 在 forward 阶段不保存中间激活; 配合 `gradient_accumulation_steps` 维持等效 batch size; 此时可在 batch_size=1 下跑 t5-11b。
   - **第三步 DDP**: `env_type="pytorchDDP"`, 多卡并行, `num_gpus=2`, 通过 `master_ip / master_port / hostfile / training_script / num_nodes` 启多机多卡。
   - **第四步 DeepSpeed 数据并行**: `env_type="deepspeed"`, 引入 `deepspeed_config='deepspeed.json'`, 配合 `cpuoffload` 与 `stage2`, 将单 GPU 上 batch size 由 1 提升到 4。
   - **第五步 DeepSpeed + Megatron-LM 模型并行**: 在第四步基础上额外指定 `model_paralle_size = 2`, 把模型参数/计算切到多卡。
5. **实验命名与日志节流**: 所有阶段均设置 `experiment_name='t5-11b'`、`eval_interval=10`、`log_interval=10`, 便于横向对比。
6. **学习率与精度**: 全文统一 `lr=1e-4`, 步骤三到五统一 `fp16=True`、`checkpoint_activations=False`(DeepSpeed 自管的 activation checkpoint)。

---

## 【关键机制与数据】

- **工作原理 / 数据流**(原文叙述):
    - 训练循环中, `trainer.train(model, train_dataset, collate_fn=seq2seq_collate_fn)` 触发数据采样 → `BertSeq2seqDataset.__getitem__` 产生单条 `{input_ids, labels}` → `seq2seq_collate_fn` 把当前 batch 的 `input_ids` 和 `labels` 分别按 batch 内最大长度做右侧补 0(原文: `item + [pad_idx] * max(0, max_length - len(item))`, `pad_idx=0`)→ 把 padding 后的 tensor 喂入 `MyTrainer.forward_step` → 调用 `T5ForConditionalGeneration`, 取出 `loss / logits / decoder_hidden_states` 装入 `output` 字典返回。
    - 源/目标两段文本各自先小写化(原文: `line.strip('\n').lower()`),再走 tokenizer, 保证训练-推理文本分布一致。
- **显存/性能数据**(原文明确给出的事实):
    - 原文: "我们可能不会在 V100 32G 上运行 t5-11b" — 即默认硬件是 V100 32G, t5-11b 默认配置不可直接跑。
    - 原文: 配合 fp16 + gradient checkpointing 后, "可以运行 `batch size`=1 的 t5-11b"。
    - 原文: 通过 DeepSpeed `cpuoffload` + `stage2`, "将单个 gpu 上的 `batch size` 增加到 `4`"。
    - 原文(关于阶梯二): "现在, 我们可以用 `gradient_accumulation_steps` train/finetune 一个 t5-11b" — 即用梯度累积弥补单卡 batch=1 的有效 batch 不足。
    - 原文(关于阶梯三/四/五): DDP、DeepSpeed、DeepSpeed+Megatron 三档都设置 `num_gpus=2`, 表明示例以 2 卡为基准。
- **Trainer 关键输出字段**(原文 docstring 明确):
    - `output['loss']`: 训练 loss。
    - `output['logits']`: 模型 logits。
    - `output['hidden_states']`: 解码器各层隐藏状态(`model_outputs.decoder_hidden_states`)。
- **特殊上下文** `tokenizer.as_target_tokenizer()`: 原文显式指出目标文本 tokenization 必须进入 "as_target_tokenizer" 上下文, 以避免源端特殊 token(如 T5 的额外 prefix)污染 labels。

> 性能数字除上述"batch=1 / batch=4 / V100 32G"外, 原文未给出吞吐量/时延/TFLOPs 等具体数值, 因此本节不做引申。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

(可视为"伪代码/算法式"的只有 `seq2seq_collate_fn.padding` 内的列表拼接式:
`pad_indice = [item + [pad_idx] * max(0, max_length - len(item)) for item in indice]`,
其中 `item` 为单样本 token 序列, `max_length` 为当前 batch 内最大长度, `pad_idx=0`, 含义是"若样本短于 batch 内最大长度则右侧补 0 至等长"。原文并未以公式形式给出。)

---

## 【关联】

- **与文末内部链接的关系**: 文末无内部链接信息(题目给定"(无)"), 因此无可直接引用的同仓其他文档 URL。
- **与本仓上下游特性的关系**(基于文档内文可推断):
    - `easybigmodel.trainer.Trainer` 是本指南的核心基类, `MyTrainer.forward_step` 沿用其 step 输出契约(`loss`/`logits`/`hidden_states`), 因此本指南仅示范了 seq2seq 一类 T5 用法, 同框架下的纯 encoder/decoder/多模态可按相同契约继承扩展。
    - **加速阶梯 5 步之间是叠加/替代关系**: 第一步 fp16 是所有后续步骤的精度前置条件(步骤三、四、五均设 `fp16=True`); 第二步 `gradient_checkpointing=True` 在步骤三(DDP)中关闭(`checkpoint_activations=False`)交给 PyTorch/DeepSpeed 自管; 步骤三→四是"PyTorch DDP → DeepSpeed DDP"的并行后端替换; 步骤四→五是"DeepSpeed 数据并行 → DeepSpeed 数据并行 + Megatron-LM 张量并行"的并行维度升级。
    - **`deepspeed.json` / `hostfile`**: 文档以占位符形式引用(`deepspeed_config='deepspeed.json'`, `hostfile='hostfile'`), 实际参数(cpuoffload 范围、ZeRO stage、hostfile 节点/GPU 列表)需由用户在自己环境配置, 与本指南解耦。
    - **`training_script=__file__`**: 表示该 Trainer 的入口即为当前脚本, 表明指南期望用户把示例脚本作为完整可执行入口直接运行。
- **与外部生态的关系**: `T5ForConditionalGeneration` / `T5Tokenizer` 均直接来自 Huggingface `transformers`, 因此模型/分词器层与原生 HF 完全兼容, 仅训练循环被替换为 `easybigmodel` Trainer。

---

## 【使用方法】

**1. 准备数据文件**(原文): `train_inputs.txt` 与 `train_targets.txt`, 一行一个样本, 行内为已归一化的字符串; 脚本读取时会再做 `strip('\n').lower()`。

**2. 下载/加载模型与分词器**(原文命令):
```python
model_name = 't5-11b'
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)
```

**3. 基础训练(基线配置, 原文)**:
```python
trainer = MyTrainer(
    env_type='pytorch',
    epochs=1,
    batch_size=4,
    eval_interval=10,
    log_interval=10,
    experiment_name='t5-11b',
    pytorch_device='cuda:0',
    load_dir=None,
    lr=1e-4,
    fp16=False)

trainer.train(model,
              train_dataset=train_dataset,
              collate_fn=seq2seq_collate_fn)
```
(`maxlen=1024`, 80/20 切分训练/验证集)

**4. 加速阶梯(原文)**:

| 阶梯 | 关键开关 | 关键数值/命令 |
|---|---|---|
| Step 1 fp16 | `fp16=True` | `batch_size=1` |
| Step 2 梯度重计算 | `model.gradient_checkpointing = True` | `batch_size=1`, 配合 `gradient_accumulation_steps` |
| Step 3 DDP | `env_type="pytorchDDP"`, `checkpoint_activations=False` | `master_ip='127.0.0.1'`, `master_port=17750`, `num_nodes=1`, `num_gpus=2`, `hostfile='hostfile'`, `training_script=__file__` |
| Step 4 DeepSpeed | `env_type="deepspeed"`, `deepspeed_config='deepspeed.json'` | `cpuoffload` + `stage2`, `num_gpus=2`, 单 GPU `batch_size` 增至 `4` |
| Step 5 模型并行 | 同 Step 4 + `model_paralle_size=2` | DeepSpeed + Megatron-LM, `num_gpus=2` |

**5. 数据流约定**: `BertSeq2seqDataset.__getitem__` 返回 `{input_ids, labels}`(均为 list[int]); `seq2seq_collate_fn` 在 batch 维度按 `input_ids` 与 `labels` 分别动态 padding(`pad_idx=0`)后转 `torch.Tensor`。

**6. 复用约定**: 自定义 Trainer 必须重写 `forward_step(self, data, model, mems)`, 并返回 `output['loss']`(必需), `output['logits']`、`output['hidden_states']`(原文示例一并给出, 用于日志/可视化)。
