# GRPO配置参数简介

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/grpo_yaml.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/grpo_yaml.md

# mindspeed-rl · GRPO 配置参数文档 深度解读

---

## 【定位】

这篇文档解决的核心问题是：**在 MindSpeed RL 强化学习加速库中，如何使用层级化 YAML 配置（将模型结构与训练参数解耦）来完整定义 GRPO（Group Relative Policy Optimization）训练流程的全部超参与并行/资源设置**，为用户提供一份「字段索引 + 含义注释」式的 GRPO 配置字典。

---

## 【技术要点】

1. **层级化配置解耦**：将「模型结构」与「训练配置」拆为不同 YAML 文件，GRPO 训练专属文件命名遵循 `grpo_trainer_<模型名>_<模型大小>_<机器型号>.yaml` 规则，全部存放在 `configs/` 目录下；模型结构文件存放在 `configs/model/` 子目录中。

2. **五大配置段结构**：根 YAML 包含 `defaults`、`megatron_training`、`actor_config`、`rl_config`、`generate_config` 五个段，分别承担「模型引入 / 训练引擎通用默认 / Actor 与 Reference 训练 / GRPO 特有超参与资源 / 推理与采样配置」的职责。

3. **GRPO 特有训练开关**：训练算法需通过 `megatron_training.stage` 显式指定为 `ray_grpo` 才启用 Ray 驱动的 GRPO 流程；`actor_forward_micro_batch_size` / `ref_forward_micro_batch_size` 分离前向 micro batch，`clip_ratio`（一般 `[0.1, 0.3]`，最大 `[0, 1]`）控制策略更新幅度，`n_samples_per_prompt` 控制一条 prompt 衍生出 n 条 response。

4. **奖励机制可切换**：当前默认不开启 Reward 模型（无独立 reward 模型节点），改用「规则奖励（rule_reward）」打分——通过 `verifier_function`（如 `["acc", "strict_format"]`）与 `verifier_weight`（如 `[1.0, 1.0]`）组合实现；同时支持 GAE 优势估计（`gamma`、`lam`）、KL 惩罚（`kl_penalty`、`kl_ctrl_type`、`init_kl_coef`）与熵正则（`entropy_coeff`）。

5. **推理侧 vLLM 集成**：`generate_config` 内嵌 vLLM 引擎参数与采样参数，覆盖并行（`infer_tensor_parallel_size` / `infer_pipeline_parallel_size` / `infer_expert_parallel_size`，其中 PP 当前必须置 `1`）、资源（`gpu_memory_utilization`、`max_num_seqs`、`max_model_len`、`max_num_batched_tokens`）、MOE（`enable_expert_parallel`）、DeepSeek V3 专属（`torchair_graph` 与 `enforce_eager` 配对关闭）以及采样（`top_p` / `top_k` / `min_p` / `temperature` / `max_tokens` / `logprobs` / `detokenize`）。

6. **显存优化三板斧**：`actor_config` 下的训练侧全量重计算（`recompute_granularity` / `recompute_num_layers` / `recompute_method` 支持 `uniform` 与 `block` 两种切分方式），以及 `generate_config` 下的 resharding（`trust_remote_code`、`offload_train_optimizer` / `offload_train_grad` / `offload_train_param`）共同应对昇腾 NPU 显存压力。

---

## 【关键机制与数据】

- **原文：配置加载流程**——通过根配置 `defaults.model: qwen25_7b` 引入 `configs/model/` 下对应的模型结构 YAML；引入后，`megatron_training` / `actor_config` 等段可选择性地覆盖或引用模型结构中的字段。
- **原文：Ray GRPO 启动条件**——`stage` 必须设为 `ray_grpo` 才进入 Ray 调度的 GRPO 训练流程，`global_batch_size` 描述「多少样本后 actor-train 与 rollout 权重同步」。
- **原文：actor 与 reference 同步粒度**——`global_batch_size` 是 actor-train 与 rollout 端权重同步的样本数门槛，而非梯度累积步长；梯度累积由 `actor_config.micro_batch_size` 控制；每次 `mini_batch_size` 之后 actor 更新一次。
- **原文：n_samples_per_prompt 的作用**——「每条 prompt 输入能输出 n 条 response」，是 GRPO 组内相对优势（group baseline）得以计算的前提。
- **原文：日志系统互斥**——`use_tensorboard` 与 `use_wandb` 同时为 `True` 时，tensorboard 不生效（wandb 优先）。
- **原文：vLLM 推理调度**——`num_scheduler_steps` 控制「调度器将一个完整调度周期内的批处理请求分成多少个子步骤执行」；`gpu_memory_utilization` 指定推理时 GPU 内存利用率上限。
- **原文：资源分配样例**——`actor_resource.num_npus: 4` 表示分配给 Actor 与 Reference 模型的 NPU 数量为 4。
- **原文（性能/吞吐相关）**：`log_max_throughput` 配置 tps（tokens per second）计算时是否使用 max 值；`guarantee_order` 控制是否开启 TransferDock 保序；`shuffle_mini_batch` 控制 Actor 训练时是否对 mini batch 打散。文档未给出具体性能数值与 benchmark 数据。

---

## 【表格解读】

### 表 1：根配置段总览（原文逐字还原）

| 参数名 | 说明 |
|--------|------|
| `defaults` | 引入需要使用的模型配置文件，其下的模型配置（如`model`）<br> 可在 `megatron_training`、`actor_config` 等具体配置中被选择使用 |
| `megatron_training` | 训练引擎的通用默认参数配置 |
| `actor_config` | Actor 模型和 Reference 模型的训练配置参数 |
| `rl_config` | GRPO 训练中的特有参数，以及相关模型的资源配置 |
| `generate_config` | 包含分词器设置、推理并行配置、vLLM 引擎参数及生成采样参数等 |

**逐行解读**：这一表界定了 GRPO YAML 的「配置段协议」。
- `defaults`：是入口点，靠它把模型结构 YAML「拼装」进来；其下的 `model` 键是占位键，会在 `megatron_training` / `actor_config` 等段被引用。
- `megatron_training`：是训练引擎的「通用默认」，与底层 Megatron 训练栈对齐（学习率调度、并行等），GRPO 不独有。
- `actor_config`：聚焦 Actor 与 Reference 模型的本训练超参（学习率、并行、保存/加载等）。
- `rl_config`：GRPO 专属段，包括奖励函数、KL 控制、组采样策略、Ray 资源分配等。
- `generate_config`：把推理侧（vLLM + 分词器 + 采样参数）独立成段，便于与训练侧解耦切换。

---

### 表 2：`megatron_training` 关键参数（原文逐字还原）

| 参数名 | 说明 |
|--------|------|
| `stage` | 用于指定训练算法，使用 Ray GRPO 训练须设置为 `ray_grpo` |
| `global_batch_size` | 经过多少样本后 actor-train 和 rollout 权重同步 |
| `data-path` | 数据集路径配置，例如 `/dataset/data`，注意带前缀 |
| `tokenizer_name_or_path` | 分词器路径配置，可以配置为 HuggingFace 权重文件的文件夹路径，例如 `/ckpt/qwen2.5_7b_hf/` |
| `其余参数` | 其余参数为 Megatron 训练中的特性配置 |

**逐行解读**：
- `stage=ray_grpo`：触发条件式开关，必须显式打开才进入 Ray GRPO 主循环。
- `global_batch_size`：在 GRPO 中含义特殊——它不是普通梯度累积步长，而是 actor-train 与 rollout 之间的「权重同步节拍」。
- `data-path`：原文写为 `data-path`（连字符），注意与下文 `actor_config` 中 `micro_batch_size` 等下划线风格的命名差异，沿用 Megatron 原生命名。
- `tokenizer_name_or_path`：可直接指向 HuggingFace 权重目录复用其 tokenizer。
- `其余参数`：留白说明其余均走 Megatron 原生特性，不在 GRPO 文档中重复展开。

---

### 表 3：全量重计算参数（原文逐字还原）

| 参数名 | 说明 |
|--------|------|
| `recompute_granularity` | 对于内存非常有限的情况，全量重计算只保存 Transformer 层或层组的输入激活值，其他部分全部重新计算 |
| `recompute_num_layers` | 指定重计算分组层数或重计算层数 |
| `recompute_method` | 全量重计算的方法选择：<br>• `uniform`：将 Transformer 层均匀划分组（每组大小由 `recompute_num_layers` 指定），按组存储输入和激活值<br>• `block`：将前 `recompute_num_layers` 个 Transformer 层重计算，剩余层不进行重计算 |

**逐行解读**：
- `recompute_granularity`：以「层 / 层组」为粒度启用 recompute；开启后只保留输入激活，反向时重算其余中间激活。
- `recompute_num_layers`：在两种方法下语义不同——`uniform` 下是「每组大小」，`block` 下是「前 N 层」。
- `recompute_method`：二选一。`uniform` 适合层数多、显存压力大时的均匀切分；`block` 适合「只重算浅层、深层正常缓存」的非均衡策略。两者与 `recompute_num_layers` 共同决定切分拓扑。

---

### 表 4：`actor_config` 参数（原文逐字还原）

| 参数名 | 说明 |
|--------|------|
| `micro_batch_size` | 梯度累积的 mbs 大小 |
| `tensor_model_parallel_size` | TP 并行策略数 |
| `pipeline_model_parallel_size` | PP 并行策略数 |
| `lr` | 学习率 |
| `lr_decay_style` | 学习率衰减配置 |
| `min_lr` | 最小学习率 |
| `weight_decay` | 权重衰减，用于防止模型过拟合 |
| `lr_warmup_fraction` | 学习率预热比例，在训练初期逐渐增大学习率的比例 |
| `clip_grad` | 梯度裁剪系数 |
| `load` | 模型加载的路径 |
| `save` | 模型保存的路径 |
| `no_load_optim` | 续训加载优化器状态 |
| `no_load_rng` | 续训加载数据随机数生成器 |
| `no_save_optim` | 保存优化器状态 |
| `no_save_rng` | 保存数据随机数生成器 |

**逐行解读**：
- 训练并行：`tensor_model_parallel_size` / `pipeline_model_parallel_size` 共同决定训练侧并行拓扑，与推理侧 `infer_*_parallel_size` 需分开设置。
- 学习率三件套：`lr` + `lr_decay_style` + `min_lr` 描述衰减曲线；`lr_warmup_fraction` 描述预热比例。
- 正则化：`weight_decay` 抑制过拟合，`clip_grad` 控制梯度爆炸。
- 续训语义：`no_load_optim` / `no_load_rng` 是「**不**加载」的开关（默认开启续训语义，需显式打开这些开关以禁用加载优化器或 RNG 状态）；`no_save_*` 同理控制「**不**保存」。

---

### 表 5：`rl_config` 关键参数（原文逐字还原）

| 参数名 | 说明 |
|--------|------|
| `use_integrated_worker` | 是否开启全共卡模式 |
| `blocking` | 是否开启异步 |
| `gamma` | 奖励折扣因子 |
| `lam` | GAE参数 |
| `actor_forward_micro_batch_size` | actor model 前向计算 logp 的 mbs 大小 |
| `ref_forward_micro_batch_size` | ref model 前向计算 logp 的 mbs 大小 |
| `adv_estimator` | 优势计算方法 |
| `kl_penalty` | kl 散度惩罚系数 |
| `kl_ctrl_type` | kl loss 计算方法 |
| `init_kl_coef` | kl loss 所占权重 |
| `mini_batch_size` | 每 mini batch size 之后 actor 会更新一次 |
| `max_prompt_length` | GRPO 训练中最大 prompt 长度 ｜
| `clip_ratio` | Actor 模型训练计算损失函数时的 clip 比例，一般取值范围 [0.1，0.3] 最大取值范围[0，1]，该数值越大允许策略更新的幅度越大 |
| `entropy_coeff` | entropy loss 所占权重 |
| `n_samples_per_prompt` | 每条prompt的重用次数，一条 prompt 输入能输出 n 条 response |
| `guarantee_order` | 是否开启TransferDock保序 |
| `shuffle_mini_batch` | Actor 训练时是否对 minibatch 进行 shuffle |
| `log_max_throughput` | 配置tps计算时是否使用max值 |
| `num_cpus_for_local_task` | ray 进程配置的 cpu 数量 |
| `actor_resource` | 分配给 Actor 、Reference模型的显卡数量 |

**逐行解读**：
- 调度模式：`use_integrated_worker` 决定是否「全共卡」（actor、reference、rollout 共享 NPU 拓扑）；`blocking` 控制是否异步——二者共同决定流水线并行度。
- RL 算法要素：`gamma`（折扣因子）+ `lam`（GAE λ）+ `adv_estimator`（优势估计方法选择）是策略梯度类算法的标准三件套。
- 重要性采样与稳定：`clip_ratio` 直接借鉴 PPO 思想，但范围被文档标注为 `[0.1, 0.3]` 一般取值，最大 `[0, 1]`；`kl_penalty` + `kl_ctrl_type` + `init_kl_coef` 实现 KL 约束；`entropy_coeff` 鼓励探索。
- GRPO 专属：`n_samples_per_prompt` 是 GRPO 「组内相对优势」的核心——组越大、估计越稳但算力开销越大；`mini_batch_size` 决定一次 PPO 更新前会切多少个 mini batch。
- 工程细节：`guarantee_order`（TransferDock 保序）与 `shuffle_mini_batch` 关系数据一致性、收敛稳定性；`log_max_thruput` 影响 tps 统计口径。
- Ray 资源：`num_cpus_for_local_task`（Ray 进程 CPU 数）与 `actor_resource`（Actor + Reference 占用 NPU 数）共同决定集群资源划分。

---

### 表 6：显卡资源配置样例（原文逐字还原）

```
actor_resource:
    num_npus: 4
```

**逐行解读**：在 `rl_config` 段下，`actor_resource` 是一个子节点（map 形式），`num_npus: 4` 显式给 Actor 与 Reference 模型分配 4 张 NPU。原文中以缩进 YAML 代码块呈现，属于「资源配置」示例。

---

### 表 7：规则奖励配置（原文逐字还原）

| 参数名 | 说明 |
|--------|------|
| `rule_reward` | 开启后，使用规则奖励进行打分 |
| `verifier_function` | 选择使用的规则奖励模型方法，例如 `["acc", "strict_format"]` |
| `verifier_weight` | 配置规则奖励模型权重，例如 `[1.0, 1.0]` |

**逐行解读**：
- `rule_reward` 是总开关；文档说明当前不依赖独立 Reward 模型，规则奖励替代之。
- `verifier_function` 是一个字符串列表，支持同时挂多套规则（如 `acc` 答对率 + `strict_format` 严格格式）。
- `verifier_weight` 与上者一一对应（`[1.0, 1.0]` 表示两个 verifier 等权叠加），决定各规则的得分权重。

---

### 表 8：tensorboard 日志配置（原文逐字还原）

| 参数名 | 说明 |
|--------|------|
| `use_tensorboard` | 配置为 True 时打开 tensorboard（若 `use_tensorboard` 和 `use_wandb` 同时为 True，则 tensorboard 不生效） |

**逐行解读**：单字段开关；当与 `use_wandb` 同时为 `True` 时被覆盖——wandb 优先。

---

### 表 9：wandb 日志配置（原文逐字还原）

| 参数名 | 说明 |
|--------|------|
| `use_wandb` | 配置为 True 时打开 wandb |
| `wandb_project` | wandb project 名称配置 |
| `wandb_exp_name` | wandb 实验名称配置 |
| `wandb_save_dir` | 本地存储 wandb 数据的路径 |

**逐行解读**：`use_wandb` 为总开关；`wandb_project`（项目名）/ `wandb_exp_name`（实验名）/ `wandb_save_dir`（本地缓存目录）共同配置 wandb 上传通道。

---

### 表 10：推理并行配置（原文逐字还原）

| 参数名 | 说明 |
|--------|------|
| `infer_tensor_parallel_size` | TP并行策略数 |
| `infer_pipeline_parallel_size` | PP并行策略数，当前未支持该功能，设置为 '1' |
| `infer_expert_parallel_size` | EP并行策略数 |

**逐行解读**：
- `infer_tensor_parallel_size`：vLLM 推理端的 TP，与训练侧 TP 解耦。
- `infer_pipeline_parallel_size`：PP 当前**未支持**，硬约束为 `'1'`。
- `infer_expert_parallel_size`：EP，用于 MOE 模型切分专家；与 `enable_expert_parallel` 配合使用。

---

### 表 11：resharding 相关配置（原文逐字还原）

| 参数名 | 说明 |
|--------|------|
| `trust_remote_code` | 是否信任远程代码执行 |
| `offload_train_optimizer` | 卸载训练节点优化器 |
| `offload_train_grad` | 卸载训练节点梯度 |
| `offload_train_param` | 卸载模型权重 |

**逐行解读**：这是训练—推理之间的「权重 resharding + 显存卸载」开关集合。
- `trust_remote_code`：对应 HuggingFace `trust_remote_code=True`，允许加载自定义模型代码。
- `offload_train_optimizer` / `offload_train_grad` / `offload_train_param`：在训练侧将优化器状态、梯度、参数卸载到 host 内存或二级存储，缓解 NPU 显存压力；典型场景是当 rollout 节点需要抢占显存时启用。

---

### 表 12：vllm 模型相关设置（原文逐字还原）

| 参数名 | 说明 |
|--------|------|
| `max_num_seqs` | vllm 推理并发最大样本限制 |
| `max_model_len` | vllm 能够处理的最大输入序列长度(prompt+response) |
| `max_num_batched_tokens` | vllm 单步能处理的最大 token 数量 |
| `enforce_eager` | 使能PyTorch eager模式，默认开启，仅 DeepSeek V3 开启 torchair_graph 时需要关闭 |
| `torchair_graph` | DeepSeek V3 使能 torchair 图模式 |
| `enable_expert_parallel` | MOE 模型使能专家切分，需要 MOE 模型支持 |
| `dtype` | vllm 推理所使用的数据类型 |
| `gpu_memory_utilization` | GPU 内存利用率，指定推理时使用 GPU 内存的比例 |
| `num_scheduler_steps` | 在一个完整的调度周期内，调度器会将批处理请求分成多少个子步骤来执行 |

**逐行解读**：
- 容量上限：`max_num_seqs`（并发路数）、`max_model_len`（prompt+response 上下文上限）、`max_num_batched_tokens`（单步 token 总量）三个维度共同决定 vLLM 容量。
- 模式开关：`enforce_eager=True` 是默认（eager 模式），与 `torchair_graph`（torchair 图编译）互斥——后者专为 DeepSeek V3 设计，开启图编译时必须把 `enforce_eager` 置 `False`。
- MOE 开关：`enable_expert_parallel` 与推理并行的 `infer_expert_parallel_size` 配套；要求底层模型本身支持专家切分。
- 资源与调度：`dtype` 指定推理精度（如 `bfloat16`）；`gpu_memory_utilization` 决定 vLLM 抢占的显存比例上限；`num_scheduler_steps` 决定调度粒度，越大越细、可能越稳但开销越高。

---

### 表 13：采样配置（原文逐字还原）

| 参数名 | 说明 |
|--------|------|
| `logprobs` | 是否生成logprobs |
| `max_tokens` | 单条response最大生成token数量 |
| `top_p` | vllm 筛选出概率累积和达到top_p的token集合，随后只在这个集合里进行采样 |
| `top_k` | vllm 会先选出概率最高的 top_k 个 token，然后在这 top_k 个 token 范围内进行采样 |
| `min_p` | vllm 过滤掉概率低于 min_p 的词元，不参与后续的采样过程 |
| `temperature` | 采样时的随机性参数 |
| `detokenize` | 是否将输出token重新转为文本 |

**逐行解读**：
- `logprobs`：开启后每步返回选中 token 的对数概率，是后续 actor/reference 计算 logp 与 KL 的数据源。
- `max_tokens`：单条 response 硬上限，避免无限生成。
- 采样三件套：`top_p`（核采样）、`top_k`（截断采样）、`min_p`（概率下界过滤）三者可叠加使用；`temperature` 控制分布锐度（越大越随机）。
- `detokenize`：是否将 token id 还原为可读文本，便于日志与规则奖励（`acc`、`strict_format` 等字符串匹配）直接消费。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

- **示例配置文件**：[`grpo_qwen25_7b_A3.yaml`](../../../configs/grpo_qwen25_7b_A3.yaml) ——这是文档钦点的「具体参数配置格式样例」，覆盖 `defaults`、`megatron_training`、`actor_config`、`rl_config`、`generate_config` 五大段的真实取值。
- **模型结构文件目录**：`configs/model/` ——存放被 `defaults.model` 引入的网络结构 YAML（如 `qwen25_7b`），与 GRPO 训练配置文件形成「结构 + 训练」解耦关系。
- **训练引擎底层**：`megatron_training` 段透传至 Megatron 训练栈（TP/PP/重计算/学习率调度等），与 MindSpeed（基于 Megatron 的昇腾加速版）形成上下游依赖。
- **推理引擎**：`generate_config` 中 vLLM 参数与 `https://docs.vllm.ai/en/stable/configuration/engine_args` 保持一致；`enforce_eager` / `torchair_graph` 与 DeepSeek V3 的 torchair 图模式绑定。
- **规则奖励链路**：`rl_config.rule_reward` → `verifier_function` / `verifier_weight` → 在采样后通过 `detokenize` 还原文本进行字符串级规则打分，与 `actor_forward_micro_batch_size` / `ref_forward_micro_batch_size` 计算的 logp 一同进入优势估计（`adv_estimator`、`gamma`、`lam`）。
- **资源/调度协同**：`rl_config.actor_resource`（NPU 分配）+ `num_cpus_for_local_task`（Ray CPU 数）+ `use_integrated_worker`（全共卡）/ `blocking`（异步）共同决定 Ray GRPO 集群布局，与 `infer_*_parallel_size`（推理并行）解耦但需要总资源不超集群上限。
- **显存策略组合**：`actor_config` 的全量重计算（`recompute_granularity` / `recompute_num_layers` / `recompute_method`）与 `generate_config` 的 `offload_train_*` resharding 系列开关互补，共同应对 NPU 显存压力。

---

## 【使用方法】

> 以下启用方式均来自原文。

- **定位配置文件**：所有 GRPO 训练相关 YAML 存放在 `configs/` 目录，模型结构 YAML 在 `configs/model/`，训练配置以 `grpo_trainer_<模型名>_<模型大小>_<机器型号>.yaml` 命名。
- **开启 Ray GRPO 训练**：在 `megatron_training` 段设置 `stage: ray_grpo`。
- **引入模型结构**：在 `defaults` 段设置 `model: <模型名>`，例如 `model: qwen25_7b`。
- **指定分词器**：`megatron_training.tokenizer_name_or_path` 配置为 HuggingFace 权重目录，例如 `/ckpt/qwen2.5_7b_hf/`。
- **指定数据集**：`megatron_training.data-path` 设为数据集路径（如 `/dataset/data`，原文提示「带前缀」）。
- **开启全量重计算**：在 `actor_config` 下设置 `recompute_granularity` / `recompute_num_layers` / `recompute_method`（`uniform` 或 `block`）。
- **配置 Actor / Reference 资源**：`rl_config.actor_resource.num_npus: <数量>`，例如 `actor_resource.num_npus: 4`。
- **开启规则奖励**：`rl_config.rule_reward: True`，并设置 `verifier_function: ["acc", "strict_format"]`、`verifier_weight: [1.0, 1.0]`。
- **开启异步 / 全共卡**：`rl_config.use_integrated_worker` 与 `rl_config.blocking`。
- **配置日志**：`rl_config.use_tensorboard` 与 `rl_config.use_wandb`（二者同时为 True 时 tensorboard 不生效），可选填 `wandb_project` / `wandb_exp_name` / `wandb_save_dir`。
- **配置 vLLM 推理**：`generate_config` 下设置 `infer_tensor_parallel_size` / `infer_expert_parallel_size`（`infer_pipeline_parallel_size` 当前必须为 `'1'`）；`max_num_seqs` / `max_model_len` / `max_num_batched_tokens` / `gpu_memory_utilization` / `num_scheduler_steps`；DeepSeek V3 专用 `torchair_graph: True` 配对 `enforce_eager: False`；MOE 模型配 `enable_expert_parallel: True`。
- **配置采样参数**：`generate_config` 下设置 `top_p` / `top_k` / `min_p` / `temperature` / `max_tokens` / `logprobs` / `detokenize`。
- **配置 resharding/卸载**：`generate_config` 下设置 `trust_remote_code` / `offload_train_optimizer` / `offload_train_grad` / `offload_train_param`。
- **完整示例参考**：参见 [grpo_qwen25_7b_A3.yaml](../../../configs/grpo_qwen25_7b_A3.yaml)。

> 原文未给出具体启动命令（如 `python -m ...` 或 `bash run_grpo.sh` 等 CLI 入口），仅给出 YAML 字段定义与示例文件链接。
