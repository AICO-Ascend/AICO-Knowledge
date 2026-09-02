# Support Huggingface t5

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_14_HUGGINGFACE_T5.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_14_HUGGINGFACE_T5.md

# 一体化深度解读:Support Huggingface t5

---

## 【定位】

本教程展示如何在 FlagAI 的 `Trainer` 训练框架内接入 HuggingFace 的 **T5 (本文具体示例为 `t5-11b`) 模型与分词器** 完成 seq2seq 任务的训练/微调,并在显存紧张时给出 **从 FP16 → gradient checkpointing → DDP → DeepSpeed → Megatron-LM** 五级递进的显存/吞吐优化方案。

---

## 【技术要点】

1. **继承重写 `forward_step`**:自定义 `MyTrainer(Trainer)`,实现 `forward_step(self, data, model, mems)` 直接调用 HuggingFace `T5ForConditionalGeneration` 的前向 (`model(**data)`),返回字典中包含 `loss`、`logits`、`decoder_hidden_states` 三个键,符合 FlagAI `Trainer` 的输出约定。
2. **数据管线**:`read_file()` 读取 `train_inputs.txt`/`train_targets.txt`(原文均使用 `.lower()` 归一化);`BertSeq2seqDataset.__getitem__` 用 `tokenizer(src)` 编码源端,在 `tokenizer.as_target_tokenizer()` 上下文内编码目标端,产出 `input_ids` 与 `labels`。
3. **批内 padding**:`seq2seq_collate_fn` 内部 `padding()` 以 batch 内最大长度对齐,`pad_idx=0`;最终返回 `{"input_ids": token_ids_padded, "labels": labels_padded}`。
4. **切分与训练入口**:按 `0.8` 比例切分训练/验证集,调用 `trainer.train(model, train_dataset=..., collate_fn=seq2seq_collate_fn)`。
5. **五级加速/降显存技巧链**:
   - FP16:`fp16=False → fp16=True`
   - Gradient Recomputation:`model.gradient_checkpointing = True`(原文称可使 `t5-11b` 以 `batch_size=1` 跑通,再叠加 `gradient_accumulation_steps`)
   - 数据并行 DDP:`env_type='pytorchDDP'`,`num_gpus=2`,新增 `master_ip/master_port/num_nodes/hostfile/training_script`
   - DeepSpeed 数据并行:`env_type='deepspeed'`,配 `deepspeed_config='deepspeed.json'`,原文称使用 `cpuoffload` + `stage2` 可在 **单卡将 batch size 提升到 4**
   - 模型并行:`model_paralle_size = 2`(原文注 "Open your imagenation",即面向更大规模想象空间)

---

## 【关键机制与数据】

- **输入数据约定**(原文):源端文件 `src_dir = 'train_inputs.txt'`,目标端文件 `tgt_dir = 'train_targets.txt'`,模型保存/加载位置 `model_dir = "./t5-11b"`(原文中文注释 "模型位置"),`maxlen = 1024`。
- **`__getitem__` 数据流**(原文):`src` → `tokenizer(src)` → `inputs.input_ids`;`tgt` → `with tokenizer.as_target_tokenizer(): labels = tokenizer(tgt)` → `labels.input_ids`;返回字典同时承载两路。
- **训练超参默认**(原文):`epochs=1`,`batch_size=4`(基础示例)/ `batch_size=1`(加速步骤中),`eval_interval=10`,`log_interval=10`,`experiment_name='t5-11b'`,`pytorch_device='cuda:0'`,`load_dir=None`,`lr=1e-4`,`fp16=False`(示例)/ `fp16=True`(加速步骤)。
- **显存/吞吐结论**(原文):FP16 + gradient_checkpointing 后原文判断 `t5-11b` 可在 `batch_size=1` 上运行;叠加 DeepSpeed `cpuoffload` + `stage2` 后,原文称 **单卡 batch size 可提升至 4**;进一步叠加模型并行(`model_paralle_size=2`)。
- **并行通信参数**(原文,加速步骤 3-5 重复出现):`master_ip='127.0.0.1'`,`master_port=17750`,`num_nodes=1`,`num_gpus=2`,`hostfile='hostfile'`,`training_script=__file__`。

---

## 【表格解读】

原文无表格(纯代码与文字说明)。

---

## 【公式解读】

原文无显式公式;核心数据形态学表述如下(伪代码,忠实于原文 `padding` 函数):

```
pad_indice[i] = item_i  ⊕  [pad_idx] · max(0, max_length − len(item_i))
```

符号说明(均出自原文):
- `item_i`:第 `i` 个 token 序列(`input_ids` 或 `labels`)
- `max_length`:该 batch 内最大序列长度(`max_length_tk` 或 `max_length_lb`)
- `pad_idx=0`:填充索引(原文默认 0)
- `max(0, max_length − len(item_i))`:需补零数,短序列右对齐补齐到 batch 内最长
- `⊕`:在序列末尾拼接pad token
- 整体最终用 `torch.tensor(pad_indice)` 转 tensor

---

## 【关联】

- 本指南直接复用 FlagAI `flagai.trainer.Trainer` 的扩展点 `forward_step`,与 `modelzoo-pytorch` 内 **其他教程(继承 Trainer 重写前向)** 属于同一使用范式(本路径属于 `PyTorch/built-in/foundation/FlagAI/docs/`,与同级 docs 共享 `Trainer` API)。
- 加速步骤 3-5 涉及的 `pytorchDDP` / `deepspeed` / `megatron-lm` 三类 `env_type` 是 FlagAI Trainer 的并行后端,与仓库内 **分布式训练相关模块** 共享 `master_ip、master_port、num_nodes、num_gpus、hostfile、training_script` 这一标准并行参数集。
- step5 的 `deepspeed + megatron-lm` 模型并行路径与 FlagAI 仓库中 **Megatron-LM 模型并行后端** 对应。
- 模型侧 `T5ForConditionalGeneration` / `T5Tokenizer` 来自 HuggingFace `transformers`,与 `flagai.trainer` 解耦,本教程本质是 **"以 FlagAI Trainer 为控制流、HuggingFace 模型/分词器为载荷"** 的桥接示例。
- 文末给出的内部链接信息为 **(无)**,即本文档未在尾部声明关联跳转。

---

## 【使用方法】

**启用方式与配置项**(按原文汇总):

- **依赖导入**(原文):
  ```python
  from flagai.trainer import Trainer
  from transformers import T5ForConditionalGeneration, T5Tokenizer
  from torch.utils.data import Dataset
  ```
- **替换模型名**(原文):`model_name = 't5-11b'` 一处既用于 `T5Tokenizer.from_pretrained(model_name)`,也用于 `T5ForConditionalGeneration.from_pretrained(model_name)`,以及 `experiment_name='t5-11b'`。
- **训练/验证切分**(原文):`train_size = int(data_len * 0.8)`,前段训练、后段验证。
- **加速开关切换**(原文):
  - FP16:`fp16=False → fp16=True`
  - Gradient checkpointing:`model.gradient_checkpointing = True`
  - DDP:`env_type='pytorchDDP'`,新增 `master_ip='127.0.0.1'`、`master_port=17750`、`num_nodes=1`、`num_gpus=2`、`hostfile='hostfile'`、`training_script=__file__`、`checkpoint_activations=False`
  - DeepSpeed:`env_type='deepspeed'`,新增 `deepspeed_config='deepspeed.json'`(原文配套声称使用 `cpuoffload` + `stage2`)
  - Megatron-LM 模型并行:在 DeepSpeed 基础上新增 `model_paralle_size = 2`(注意原文拼写为 `model_paralle_size`,非 `model_parallel_size`)
- **训练入口调用**(原文):`trainer.train(model, train_dataset=train_dataset, collate_fn=seq2seq_collate_fn)`。

原文未涉及命令行(如 `torchrun`、`deepspeed` 启动器)调用方式,仅给出 Python API 式配置。
