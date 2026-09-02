# 为模型和数据并行训练定制训练器

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_4_TRAINER.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_4_TRAINER.md

# 一体化深度解读：FlagAI Trainer 定制与分布式训练指南

## 【定位】

本文档解决 FlagAI 框架下"如何通过统一的 `Trainer` 类 API 适配多种并行训练框架"的问题，覆盖从单节点 CPU/GPU 训练到多节点 DeepSpeed / Megatron-LM 混合并行的全场景训练能力。

---

## 【技术要点】

1. **统一入口 `env_type` 参数**：通过一个参数切换四种训练环境——`pytorch`（单节点 CPU/GPU）、`pytorchDDP`（单/多节点数据并行）、`deepspeed`（单/多节点数据/流水线并行）、`deepspeed+mpu`（数据并行 + 模型并行）。
2. **自定义 Trainer 子类化机制**：通过继承 `flagai.trainer.Trainer` 并覆盖 `forward_step(self, data, model, mems)` 方法，使其返回包含 `loss`、`logits`、`hidden_states` 等键的 `dict`，从而适配非 FlagAI 原生模型（如 HuggingFace 的 `T5ForConditionalGeneration`）。
3. **fp16 混合精度**：通过在 `Trainer` 构造时设置 `fp16=True` 即可启用，无需用户额外修改代码。
4. **梯度重计算（Gradient Checkpointing）**：在前向过程不保存中间激活以节省显存，引用论文 *Training Deep Nets with Sublinear Memory Cost* (arXiv:1604.06174v2)。FlagAI 模型通过 `checkpoint_activations=True`（如 `GLMModel.from_pretrain`），HuggingFace 模型通过 `model.gradient_checkpointing = True` 启用。
5. **DeepSpeed ZeRO + CPU Offload**：通过 `deepspeed.json` 配置 `zero_optimization.stage` 与 `cpu_offload` 等关键参数实现优化器显存卸载。
6. **Megatron-LM + DeepSpeed 混合并行**：用于 10B+ 级别模型（如 GLM-10b-ch），通过将矩阵按行/列切分实现张量并行，并叠加 DeepSpeed 的数据并行。

---

## 【关键机制与数据】

### 工作原理

- **Trainer 使用分两步**（原文："Trainer使用分成两个步骤，初始化和调用"）：第一步实例化 Trainer 对象并配置超参，第二步调用 `trainer.train(model, train_dataset=..., collate_fn=...)` 启动训练循环。
- **`forward_step` 数据契约**（原文）：方法必须返回一个 `dict`，至少包含 `loss` 字段（用于反向传播），可选 `logits`、`hidden_states` 等用于评估指标。
- **DeepSpeed 优化器机制**（原文）："deepspeed主要在优化器方面做了优化，其提供了cpu-offload的optimizer，可以极大的降低gpu显存的占用"。
- **Megatron-LM 张量切分思想**（原文）："Megatron-LM提供了Tensor的切分方法，主要思想是将矩阵按照行/列进行切分"。

### 数据流（以 T5-11b 完整示例为依据）

```
文件读取 → read_file() 得到 src/tgt 列表 
        → T5Seq2seqDataset 编码 input_ids / labels 
        → seq2seq_collate_fn 进行动态 padding 
        → MyTrainer.forward_step 调用 model(**data) 
        → 返回 {loss, logits, hidden_states} 
        → trainer.train()
```

### 性能/硬件数据（原文）

- **百亿模型权重规模**（原文）："百亿规模以上的模型权重在 20G+，单块显卡需要 V100 及以上的硬件"。
- **pytorchDDP 适用规模**（原文）："在模型的参数规模<1 billion, 比如 `t5-base` 的时候可以使用"。
- **DeepSpeed 适用场景**（原文）："在上述训练 T5-11b 的例子中，只能使用 `deepspeed` 框架的数据并行模式"。

---

## 【表格解读】

### 表 1：`env_type` 参数对照表（原文表格还原）

| env_type 取值 | 适用场景 | 并行维度 |
|---|---|---|
| `pytorch` | single node cpu/gpu | 单机训练 |
| `pytorchDDP` | single-/multi- node gpu | data parallel |
| `deepspeed` | single-/multi- node gpu | data/pipeline parallel |
| `deepspeed+mpu` | single-/multi- node gpu | data parallel + model parallel |

**逐行解读**：
- `pytorch`：最轻量入口，无分布式，仅适用于单机 CPU 或单卡 GPU 调试。
- `pytorchDDP`：原生 PyTorch DDP 数据并行，单机多卡或多机多卡均可，但不适合超大模型。
- `deepspeed`：支持数据并行与流水线并行，并集成 ZeRO 优化器分片与 CPU offload，适合显存吃紧场景。
- `deepspeed+mpu`：在 DeepSpeed 数据并行基础上叠加 Megatron-LM 的张量/流水线模型并行，是百亿级以上模型的标配。

### 表 2：`deepspeed.json` 关键配置项（原文表格还原）

| 配置字段 | 数值/取值 | 作用 |
|---|---|---|
| `train_micro_batch_size_per_gpu` | `2` | 每张 GPU 的微批次大小 |
| `gradient_accumulation_steps` | `1` | 梯度累积步数 |
| `steps_per_print` | `100` | 每多少步打印一次日志 |
| `gradient_clipping` | `1.0` | 梯度裁剪阈值 |
| `zero_optimization.stage` | `3` | ZeRO 第三阶段（参数分片到所有 GPU） |
| `zero_optimization.contiguous_gradients` | `false` | 是否使用连续梯度缓冲 |
| `zero_optimization.overlap_comm` | `true` | 通信与计算重叠 |
| `zero_optimization.reduce_scatter` | `true` | 使用 reduce-scatter 通信 |
| `zero_optimization.reduce_bucket_size` | `5e7` | reduce 通信桶大小 |
| `zero_optimization.allgather_bucket_size` | `5e7` | allgather 通信桶大小 |
| `zero_optimization.cpu_offload` | `true` | 将优化器状态卸载到 CPU |
| `zero_allow_untested_optimizer` | `true` | 允许未在 DeepSpeed 官方测试的优化器 |
| `fp16.enabled` | `true` | 启用 fp16 混合精度 |
| `fp16.loss_scale` | `0` | 动态 loss scaling |
| `fp16.loss_scale_window` | `1000` | loss scale 调整窗口 |
| `fp16.hysteresis` | `2` | loss scale 调整迟滞 |
| `fp16.min_loss_scale` | `1` | loss scale 下限 |
| `optimizer.type` | `Adam` | 优化器类型 |
| `optimizer.params.lr` | `0.0004` | 学习率 |
| `optimizer.params.weight_decay` | `0.01` | 权重衰减 |
| `optimizer.params.betas` | `[0.9, 0.98]` | Adam beta 参数 |
| `optimizer.params.eps` | `1e-6` | Adam epsilon |
| `activation_checkpointing.partition_activations` | `false` | 是否对激活进行分区（Megatron 式） |
| `activation_checkpointing.contiguous_memory_optimization` | `false` | 是否启用连续内存优化 |
| `wall_clock_breakdown` | `false` | 是否输出耗时分解 |

**关键项解读**（原文重点标注）：
- **主要参数**（原文）："`stage` 和 `cpu_offload`" 是 DeepSpeed 配置中最核心的两项，`stage=3` 实现参数、优化器状态、梯度全分片，`cpu_offload=true` 进一步将优化器状态卸载到主机内存。
- **`hostfile` 简化**（原文）："`hostfile` 在单节点时可以省略"。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游/前置文档**：[TUTORIAL_3_MODEL.md#模型的forward-函数](TUTORIAL_3_MODEL.md)（原文链接）：讲解 FlagAI 模型 `forward` 函数的输入输出契约。本文自定义 `Trainer` 时明确指出"模型的输入输出与 `FlagAI` 框架中模型的行为不一致时"需要参考该文档，是直接的前置依赖。
- **代码示例位置**（原文）：
  - `examples/glm_superglue` 目录：用于"入门"章节的参考代码。
  - `examples/t5_huggingface` 目录：用于"完整的用 Trainer 训练 huggingface t5-11b 例子"以及 `deepspeed.json` 配置文件的参考。
- **支持 Megatron-LM 的内部模型**（原文）："飞智内部模型（GLM，T5，BERT【包括 RoBERTa】，GPT2）支持了 Megatron-LM"。
- **关联论文**：
  - 梯度重计算：[Training Deep Nets with Sublinear Memory Cost](https://arxiv.org/abs/1604.06174v2)
  - T5：[Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer](https://arxiv.org/pdf/1910.10683.pdf)

---

## 【使用方法】

### 启用方式（原文代码示例完整保留）

**1. 单节点 CPU 训练**：
```python
trainer = MyTrainer(
    env_type='pytorch',
    epochs=1, batch_size=4,
    eval_interval=10, log_interval=10,
    experiment_name='t5-11b',
    pytorch_device='cpu',
    load_dir=None,
    lr=1e-4)
```

**2. 单节点 GPU + fp16 混合精度**：
```python
trainer = MyTrainer(
    env_type='pytorch',
    epochs=1, batch_size=1,
    eval_interval=10, log_interval=10,
    experiment_name='t5-11b',
    pytorch_device='cuda:0',
    load_dir=None,
    lr=1e-4,
    fp16=True)  # change to `True`
```

**3. 梯度重计算——FlagAI GLM-10b-ch**：
```python
from flagai.model.glm_model import GLMModel
model = GLMModel.from_pretrain(download_path="./state_dict",
                               model_name="GLM-large-ch",
                               checkpoint_activations=True)
```

**4. 梯度重计算——HuggingFace T5-11b**：
```python
from transformers import T5ForConditionalGeneration, T5Tokenizer
tokenizer = T5Tokenizer.from_pretrained('t5-11b')
model = T5ForConditionalGeneration.from_pretrained('t5-11b')
model.gradient_checkpointing = True
```

**5. pytorchDDP 分布式训练**：
```python
trainer = MyTrainer(
    env_type='pytorchDDP',
    epochs=1, batch_size=1,
    eval_interval=10, log_interval=10,
    experiment_name='t5-base',
    load_dir=None, lr=1e-4,
    # parameters for pytorchDDP
    master_ip='127.0.0.1', master_port=17750,
    num_nodes=1, num_gpus=1,
    hostfile='./hostfile',
    training_script=__file__,
)
```

**6. DeepSpeed 分布式训练（T5-11b 完整示例）**：
```python
trainer = MyTrainer(
    env_type='deepspeed',
    epochs=1, batch_size=1,
    eval_interval=10, log_interval=10,
    experiment_name='t5-11b',
    load_dir=None, lr=1e-4,
    # parameters for pytorchDDP
    master_ip='127.0.0.1', master_port=17750,
    num_nodes=1, num_gpus=1,
    training_script=__file__,
    # deepspeed
    deepspeed_config='deepspeed.json'
)
# ...
trainer.train(model,
              train_dataset=train_dataset,
              collate_fn=seq2seq_collate_fn)
```

**关键配置项说明**（原文）：
- `pytorch_device`：取值 `'cpu'`、`'cuda:0'` 等，用于指定单节点训练设备。
- `master_ip` / `master_port`：分布式训练主节点地址与端口，示例为 `'127.0.0.1'` / `17750`。
- `num_nodes` / `num_gpus`：节点数与每节点 GPU 数，示例均为 `1`。
- `hostfile`：pytorchDDP 模式下指定主机列表，单节点时可省略。
- `deepspeed_config`：DeepSpeed 配置文件路径，参考 `examples/t5_huggingface/deepspeed.json`。
- `training_script`：当前训练脚本路径（`__file__`），用于 DDP/DeepSpeed 启动子进程。

> 注：原文未涉及"如何启动 `deepspeed` 启动命令"的具体 shell 命令，也未涉及 `deepspeed+mpu` 模式的完整代码示例（仅说明"只要在配置文件中将环境…"后文截断）。
