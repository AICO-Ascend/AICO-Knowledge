# Trainer

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_4_TRAINER.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_4_TRAINER.md

# Trainer 文档深度解读

## 【定位】

这篇文档描述 FlagAI 框架中 `Trainer` 类所提供的训练能力接口,说明如何通过统一的 `Trainer` 抽象封装 PyTorch DDP、DeepSpeed、Megatron-LM+DeepSpeed 等多种分布式/并行训练后端,以及 fp16 混合精度、梯度重算等显存优化手段,完成对超大模型(如 GLM-10b-ch、t5-11b)的训练。

---

## 【技术要点】

1. **统一 Trainer 抽象**:Trainer 通过 `env_type` 一个参数切换后端,支持的取值包括 `pytorch`、`pytorchDDP`、`deepspeed`、`deepspeed+mpu`、`bmtrain`,覆盖单机 CPU/GPU、单/多机数据并行、DeepSpeed 数据/流水线并行、BMTrain 数据/流水线并行,以及 DeepSpeed+Megatron-LM 的「数据并行 + 模型并行」混合。
2. **两步用法**:使用 Trainer 只需「初始化 + 执行」两步,参考 `examples/glm_superglue` 目录中的代码。
3. **自定义 Trainer**:当自定义模型的输入/输出与 FlagAI 框架约定的 forward 行为不一致时,需继承 `Trainer` 并覆写 `forward_step(self, data, model, mems)` 方法;**该方法必须返回一个 dict**(原文明确写出此约束),通常包含 `loss`、`logits`、`hidden_states` 等字段。
4. **fp16 混合精度**:在初始化 Trainer 时将 `fp16=True` 即可把 fp32 参数转为 fp16,以缓解大模型显存压力;示例中 `batch_size=1`、`pytorch_device='cuda:0'`、`epochs=1`、`lr=1e-4`。
5. **梯度重算(Gradient recomputation)**:前向阶段不保存中间结果,以亚线性显存开销训练超大模型;FlagAI 中通过 `checkpoint_activations=True`(GLM)或 `model.gradient_checkpointing = True`(HuggingFace T5)开启,论文为 *Training Deep Nets with Sublinear Memory Cost*。
6. **超大规模模型示例**:T5-11b 训练需权重大于 20G+,且单卡需 `gpu >= V100`;示例位于 `examples/t5_huggingface`,完整示例中使用了 `env_type='deepspeed'`、`epochs=1`、`batch_size=1`、`eval_interval=10`、`log_interval=10`、`lr=1e-4`,并附带 pytorchDDP 参数(`master_ip='127.0.0.1'`、`master_port=17750`、`num_nodes=1`、`num_gpus=1`、`training_script=__file__`)以及 `deepspeed_config='deepspeed.json'`。
7. **并行训练模式**:文档在「Parallel training」章节显式列出三种模式——`deepspeed`、`pytorchDDP`、`deepspeed + megatron-lm`;`env_type` 中还显式包含 `bmtrain`(支持数据/流水线并行)与 `deepspeed+mpu`(数据并行 + 模型并行)。

---

## 【关键机制与数据】

- **原文**:`Trainer` 类提供多并行框架训练 API,支持 Pytorch DDP/Deepspeed 多卡分布式训练、Megatron-LM+Deepspeed 混合并行分布式训练,以及 NVIDIA Apex 的混合精度训练。
- **原文**:`env_type` 控制训练是否分布式,默认 `pytorch`;支持 `pytorch`、`pytorchDDP`、`deepspeed`、`deepspeed+mpu`、`bmtrain` 五种取值,分别对应:单机 cpu/gpu、单/多机 gpu 数据并行、单/多机 gpu 数据/流水线并行(DeepSpeed 与 BMTrain 各自一套)、单/多机 gpu 数据并行 + 模型并行。
- **原文**:自定义 Trainer 时,`forward_step` 方法返回值必须是 dict,示例给出 `loss`、`logits`、`hidden_states` 三个 key 的写法。
- **原文**:梯度重算不保存前向中间结果,引用论文 *Training Deep Nets with Sublinear Memory Cost*(arXiv:1604.06174v2);GLM 通过 `checkpoint_activations=True` 开启,HuggingFace T5 通过 `model.gradient_checkpointing = True` 开启。
- **原文**:T5-11b 模型权重大于 **20G+**,单卡需 `gpu >= V100`;t5-11b 论文为 *Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer*(arXiv:1910.10683)。
- **原文**:T5 训练示例中 `maxlen = 1024`,数据集按 80/20 切分训练/验证集,且训练集只取前 200 条(`train_src = sents_src[:train_size][:200]`,`train_tgt = sents_tgt[:train_size][:200]`)。
- **原文**:数据预处理使用 `tokenizer.as_target_tokenizer()` 上下文管理器分别处理源端和目标端文本,collate_fn 内对 `input_ids` 与 `labels` 分别 padding 到当前 batch 内最大长度,pad_idx 默认为 0。

---

## 【表格解读】

原文本身没有使用 markdown 表格语法,但 `env_type` 取值说明结构清晰,这里用 markdown 表格**逐字还原**其语义对照关系(取自原文"env_type in Trainer"小节的代码块):

| env_type 取值 | 适用场景(原文) | 并行维度(原文) |
|---|---|---|
| `pytorch` | single node cpu/gpu | (无并行,默认) |
| `pytorchDDP` | single-/multi- node gpu | data parallel |
| `deepspeed` | single-/multi- node gpu | data/pipeline parallel |
| `bmtrain` | single-/multi- node gpu | data/pipeline parallel |
| `deepspeed+mpu` | single-/multi- node gpu | data parallel + model parallel |

**逐行解读**:
- `pytorch`:最轻量,适用于单机 CPU/GPU 的非分布式训练,作为默认值。
- `pytorchDDP`:PyTorch 原生 DistributedDataParallel,适合标准的单/多机数据并行场景。
- `deepspeed`:DeepSpeed 提供的并行方案,可同时利用数据并行与流水线并行两种模式。
- `bmtrain`:与 DeepSpeed 类似,但属于 BMTrain 后端的实现,同样支持数据/流水线并行。
- `deepspeed+mpu`:DeepSpeed 与 Megatron-LM 的混合,即文档另一处提到的 `deepspeed + megatron-lm` 模式,可同时获得数据并行与模型并行的加速效果。

此外,「Parallel training」一节目录里点名的三种实战方案(deepspeed、pytorchDDP、deepspeed+megatron-lm)与上表中的 `deepspeed`、`pytorchDDP`、`deepspeed+mpu` 相对应;`bmtrain` 仅在 `env_type` 列表里出现,未在目录里单独展开。

---

## 【公式解读】

**原文无公式。**(文档中未出现 LaTeX 或伪代码形式的数学公式;仅以代码块描述配置项与训练流程。)

---

## 【关联】

- **前向函数约定**:自定义 Trainer 的「forward 行为不一致」判断依据来自 [TUTORIAL_3_MODEL.md#forward-function](TUTORIAL_3_MODEL.md#forward-function),即 `forward_step` 必须返回包含 `loss` 等字段的 dict 这一约定,与 FlagAI 模型自身的 forward 函数返回值结构保持一致。
- **GLM 训练样例**:文档提到「Two steps to use a Trainer」时引用目录 `examples/glm_superglue`,为基于 GLM 的 SuperGLUE 任务训练示例,使用 `GLMModel.from_pretrain(..., checkpoint_activations=True)` 开启梯度重算。
- **T5-11b 训练样例**:对应目录 `examples/t5_huggingface`,演示把 HuggingFace `T5ForConditionalGeneration` 与 FlagAI `Trainer`(`env_type='deepspeed'`)结合,加载 20G+ 权重的模型并在 `gpu >= V100` 上训练。
- **混合精度后端**:文档首段说明「mixed precision via NVIDIA Apex」是 Trainer 所封装的训练能力之一,与 `fp16=True` 这一开关相对应(具体实现细节原文未展开)。
- **DeepSpeed 配置**:T5-11b 示例中通过 `deepspeed_config='deepspeed.json'` 引用外部 DeepSpeed 配置文件(原文未给出文件内容),与 `env_type='deepspeed'` 协同生效。
- **并行训练三路线**:目录中并列的 `deepspeed`、`pytorchDDP`、`deepspeed + megatron-lm` 三个子章节,与 `env_type` 取值表中的 `deepspeed`、`pytorchDDP`、`deepspeed+mpu` 一一映射,`bmtrain` 未在子章节中单独展开。

---

## 【使用方法】

- **基础流程(原文)**:`Trainer` 包含上述能力的基础训练循环,使用只需两步——**初始化**与**执行**;参考代码位于目录 `examples/glm_superglue`。
- **env_type 切换**:通过 `MyTrainer(env_type=...)` 设置;可取 `pytorch`(单机 cpu/gpu)、`pytorchDDP`(单/多机数据并行)、`deepspeed`(单/多机数据/流水线并行)、`deepspeed+mpu`(数据并行 + 模型并行,即 DeepSpeed+Megatron-LM)、`bmtrain`(单/多机数据/流水线并行),未指定时默认 `pytorch`。
- **单节点 CPU/GPU 关键配置项**(原文示例 `env_type='pytorch'`):`epochs=1`、`batch_size=4`、`eval_interval=100000`、`log_interval=10`、`experiment_name='t5-11b'`、`pytorch_device='cpu'`(也可写 `'cuda:0'` 等指定具体显卡)、`load_dir=None`、`lr=1e-4`。
- **fp16 开关**:在上述配置基础上追加 `fp16=True`,把 fp32 参数转为 fp16;示例其余参数为 `batch_size=1`、`eval_interval=10`、`log_interval=10`、`pytorch_device='cuda:0'`、`lr=1e-4`。
- **梯度重算**:对 FlagAI GLM,使用 `GLMModel.from_pretrain(download_path="./state_dict", model_name="GLM-large-ch", checkpoint_activations=True)`;对 HuggingFace T5-11b,加载后设置 `model.gradient_checkpointing = True`;两者均依赖底层 `Trainer` 配合生效。
- **T5-11b 端到端示例参数**(原文 `examples/t5_huggingface`):`env_type='deepspeed'`、`epochs=1`、`batch_size=1`、`eval_interval=10`、`log_interval=10`、`experiment_name='t5-11b'`、`load_dir=None`、`lr=1e-4`;pytorchDDP 侧参数 `master_ip='127.0.0.1'`、`master_port=17750`、`num_nodes=1`、`num_gpus=1`、`training_script=__file__`;DeepSpeed 侧 `deepspeed_config='deepspeed.json'`;数据按 80/20 切分,训练集只取前 200 条,`maxlen=1024`。
- **自定义 Trainer 模板**(原文):继承 `flagai.trainer.Trainer` 后覆写 `forward_step(self, data, model, mems)`,内部调用 `model(**data)`,把 `model_outputs.loss`、`model_outputs.logits`、`model_outputs.decoder_hidden_states` 装入 `output` 字典并返回。
- **数据要求**:源/目标文本分别来自 `./data/train.src`、`./data/train.tgt`,文本统一 `.strip('\n').lower()`;`T5Seq2seqDataset.__init__` 接收 `sents_src`、`sents_tgt`、`tokenizer`、`maxlen=512`;`seq2seq_collate_fn` 把 batch 内 `input_ids`、`labels` 分别 pad 到各自最大长度,默认 `pad_idx=0`。
- **硬件下限(原文)**:**模型权重大于 20G+ 时,单卡需 `gpu >= V100`**。
