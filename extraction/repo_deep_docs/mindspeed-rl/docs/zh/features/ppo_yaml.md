# PPO配置参数简介

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/ppo_yaml.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/ppo_yaml.md

# PPO 配置参数文档深度解读

---

## 【定位】

本文档系统性地介绍了 MindSpeed RL（昇腾强化学习加速库）中 PPO 训练的层级化参数配置体系，解决的是「如何将 PPO 强化学习训练中模型结构、训练引擎、PPO 算法特有参数、推理生成配置四类异构配置解耦并以层级化 YAML 文件管理」这一问题，让用户能够基于 `configs/` 目录下的标准化 YAML 配置文件快速启动 PPO 训练。

---

## 【技术要点】

1. **配置文件命名与存放规范**：RLXF 训练的全部配置文件存放于 `configs/` 路径下，模型结构相关配置置于 `model/` 子目录，PPO 训练相关配置文件采用 `ppo_trainer_<模型名>_<模型大小>_<机器型号>.yaml` 命名方式（如 `ppo_qwen25_32b_A3.yaml`）。

2. **五大必含字段**：每个 `ppo_trainer` 配置文件必须包含 `defaults`、`megatron_training`、`actor_config`、`rl_config`、`generate_config` 五个字段，分别承担模型引用、训练引擎默认参数、Actor/Reference 模型训练参数、PPO 特有参数与资源分配、推理生成与采样配置。

3. **全量重计算机制**：`recompute_granularity` 选择仅保存 Transformer 层或层组的输入激活值以降低显存；`recompute_method` 提供两种划分方式——`uniform`（按 `recompute_num_layers` 均匀分组）与 `block`（仅对前 `recompute_num_layers` 层重计算，剩余层不做重计算）。

4. **PPO 剪裁与优势估计关键参数**：`clip_ratio`（Actor 损失函数剪裁比例，一般取值 `[0.1, 0.3]`，最大 `[0, 1]`，数值越大策略更新幅度越大）、`cliprange_value`（Critic 损失函数剪裁比例，取值规律相同）、`adv_estimator`（优势计算方法选择）、`kl_ctrl_type` 与 `init_kl_coef`（KL 散度损失权重控制）。

5. **批处理与同步策略**：通过 `global_batch_size` 控制 actor-train 与 rollout 权重同步的样本数；`mini_batch_size` 控制 Actor 每过多少 mini batch 更新一次；`n_samples_per_prompt` 控制每条 prompt 重复采样生成 response 的次数（如启用 reuse 机制）。

6. **资源与共卡模式**：`use_integrated_worker` 控制是否开启全共卡模式；`blocking` 控制是否开启异步；`actor_resource`/`critic_resource` 中通过 `num_npus` 显式分配 Actor/Reference 与 Critic 各自的 NPU 卡数（示例中为各 4 卡）。

---

## 【关键机制与数据】

**工作原理 / 数据流**：

1. **配置加载链**：`defaults` 字段首先列举出本文件需要引用的全部模型配置文件（如 `model: qwen25_7b`），这些模型配置位于 `model/` 目录下的 YAML 文件中，被定义为网络结构。随后在 `megatron_training`、`actor_config` 等具体配置中，通过 `model` 字段选择实际的模型网络结构。
2. **训练角色分层**：PPO 训练涉及的角色包括 Actor（策略模型）、Reference（参考模型，用于计算 KL 散度基线）、Critic（价值模型）、Reward（奖励模型）。文档明确指出当前支持不开启 Reward 模型，改用 `rl_config` 中的 `rule_reward` 开启规则奖励进行打分。
3. **推理与训练桥接**：`generate_config` 中包含推理并行配置（`infer_tensor_parallel_size`、`infer_pipeline_parallel_size`、`infer_expert_parallel_size`）、vLLM 引擎参数、采样参数以及 `resharding` 相关配置（`offload_train_optimizer`、`offload_train_grad`、`offload_train_param` 用于将训练节点的优化器/梯度/权重卸载以腾出显存给推理）。`gpu_memory_utilization` 控制 vLLM 推理时的 GPU 内存分配比例。
4. **同步保序**：通过 `guarantee_order` 控制是否开启 TransferDock 保序，确保跨节点数据传输的一致性。
5. **日志互斥策略**：`use_tensorboard` 与 `use_wandb` 同时为 True 时，tensorboard 不生效（两者存在互斥逻辑）。

**性能数据**：原文未提供任何性能测试数据、benchmark 结果或量化指标。

---

## 【表格解读】

### 表 1：五大字段概览（顶层字段说明）

| 参数名 | 说明 |
|--------|------|
| `defaults` | 负责引入模型配置文件，在 defaults 中应列举本配置文件中所需要用到的所有模型配置，模型配置可以在 megatron_training、actor_config 具体配置中通过 model 字段进行选择 |
| `megatron_training` | 训练引擎通用的默认参数配置 |
| `actor_config` | Actor 模型和 Reference 模型的训练配置参数 |
| `rl_config` | PPO 训练中的特有参数，以及相关模型的资源配置 |
| `generate_config` | 包含分词器设置、推理并行配置、vLLM 引擎参数及生成采样参数等 |

**解读**：该表是配置文件骨架的导航表，五个字段覆盖了从模型定义到训练引擎、再到 PPO 算法特有逻辑、最后到推理生成全链路的配置。其中 `defaults` 是入口机制，其余四个是四大功能模块；`generate_config` 内部又承载了推理并行与 vLLM 引擎两条子链路。

---

### 表 2：`megatron_training` 核心参数

| 参数名 | 说明 |
|--------|------|
| `stage` | 用于指定训练算法，使用 Ray PPO 训练须设置为 `ray_ppo` |
| `global_batch_size` | 经过多少样本后 actor-train 和 rollout 权重同步 |
| `data_path` | 数据集路径配置，例如 `/dataset/data`，注意带前缀 |
| `tokenizer_name_or_path` | 分词器路径配置，可以配置为 HuggingFace 权重文件的文件夹路径，例如 `/ckpt/qwen2.5_7b_hf/` |
| `其余参数` | 其余参数为 Megatron 训练中的特性配置 |

**解读**：`stage: ray_ppo` 是启用 Ray-based PPO 训练的硬性开关；`global_batch_size` 不仅控制梯度累积的批次大小，还兼任 actor-train 与 rollout 间权重同步的频率控制；`data_path` 必须带前缀（指 `/dataset/data` 开头的绝对路径形式）；`tokenizer_name_or_path` 直接指向 HuggingFace 权重文件夹，这一点将训练与 HF 生态打通。

---

### 表 3：全量重计算参数

| 参数名 | 说明 |
|--------|------|
| `recompute_granularity` | 对于内存非常有限的情况，全量重计算只保存 Transformer 层或层组的输入激活值，其他部分全部重新计算 |
| `recompute_num_layers` | 指定重计算分组层数或重计算层数 |
| `recompute_method` | 全量重计算的方法选择：<br>• `uniform`：将 Transformer 层均匀划分组（每组大小由 `recompute_num_layers` 指定），按组存储输入和激活值<br>• `block`：将前 `recompute_num_layers` 个 Transformer 层重计算，剩余层不进行重计算 |

**解读**：该机制通过时间换空间缓解显存压力。`uniform` 适合层与层之间显存占用均匀的场景；`block` 则适合前若干层显存压力突出（例如首层 embedding）、后续层相对轻量的非均匀分布场景，需要配合 `recompute_granularity` 一起使用。

---

### 表 4：`actor_config` 参数（同时适用于 actor、reference、reward 模型）

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

**解读**：该表与 `critic_config` 参数列表结构完全一致（见下表），表明 Actor/Reference 与 Critic 在并行策略（TP/PP）、学习率调度（Lr/Lr decay/Min lr/Warmup）、梯度/优化器/RNG 的加载保存策略上是同一套参数体系。区别仅在于这些参数在两个 YAML 段中分别作用于不同角色。

---

### 表 5：`critic_config` 参数

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

**解读**：与表 4 完全相同的 14 项参数表，仅承载角色由 Actor/Reference/Reward 变为 Critic，证实了 MindSpeed RL 在训练角色配置上的对称设计。

---

### 表 6：`rl_config` PPO 特有参数

| 参数名 | 说明 |
|--------|------|
| `use_integrated_worker` | 是否开启全共卡模式 |
| `blocking` | 是否开启异步 |
| `actor_forward_micro_batch_size` | actor model 前向计算 logp 的 mbs 大小 |
| `ref_forward_micro_batch_size` | ref model 前向计算 logp 的 mbs 大小 |
| `adv_estimator` | 优势计算方法 |
| `kl_ctrl_type` | kl loss 计算方法 |
| `init_kl_coef` | kl loss 所占权重 |
| `mini_batch_size` | 每 mini batch size 之后 actor 会更新一次 |
| `max_prompt_length` | PPO 训练中最大 prompt 长度 |
| `clip_ratio` | Actor 模型训练计算损失函数时的 clip 比例，一般取值范围 [0.1，0.3] 最大取值范围[0，1]，该数值越大允许策略更新的幅度越大 |
| `cliprange_value` | Critic 模型训练计算损失函数时的 clip 比例，一般取值范围 [0.1，0.3] 最大取值范围[0，1]，该数值越大允许策略更新的幅度越大 |
| `entropy_coeff` | entropy loss 所占权重 |
| `n_samples_per_prompt` | 每条prompt的重用次数，一条 prompt 输入能输出 n 条 response |
| `guarantee_order` | 是否开启TransferDock保序 |
| `shuffle_mini_batch` | Actor 训练时是否对 minibatch 进行 shuffle |
| `actor_resource` | 分配给 Actor 、Reference模型的显卡数量 |

**解读**：这是 PPO 算法逻辑的核心配置层。`actor_forward_micro_batch_size` 与 `ref_forward_micro_batch_size` 分别独立控制 Actor 与 Reference 前向（计算 logp）时的微批次大小，这是因为两者计算量不同需要解耦。`clip_ratio` 与 `cliprange_value` 严格遵循 PPO 原论文的双 clip 机制（策略剪裁与价值剪裁）。`n_samples_per_prompt` 的存在暗示系统支持 best-of-n、critic 多次评分等样本复用策略。

---

### 表 7：规则奖励配置

| 参数名 | 说明 |
|--------|------|
| `rule_reward` | 开启后，使用规则奖励进行打分 |
| `verifier_function` | 选择使用的规则奖励模型方法，例如 `["acc", "strict_format"]` |
| `verifier_weight` | 配置规则奖励模型权重，例如 `[1.0, 1.0]` |

**解读**：这是文档明确给出的「不开启 Reward 模型时的替代方案」，通过规则函数（如准确性、严格格式约束）打分。`verifier_function` 与 `verifier_weight` 是按列表顺序一一对应的，意味着可同时启用多个规则奖励并按权重融合。

---

### 表 8：日志配置（tensorboard 与 wandb）

| 参数名 | 说明 |
|--------|------|
| `use_tensorboard` | 配置为 True 时打开 tensorboard（若 `use_tensorboard` 和 `use_wandb` 同时为 True，则 tensorboard 不生效） |
| `use_wandb` | 配置为 True 时打开 wandb |
| `wandb_project` | wandb project 名称配置 |
| `wandb_exp_name` | wandb 实验名称配置 |
| `wandb_save_dir` | 本地存储 wandb 数据的路径 |

**解读**：两套日志后端存在显式互斥逻辑——wandb 优先级高于 tensorboard。该表格也说明 wandb 配置项更丰富（项目名、实验名、本地存储路径），tensorboard 仅一个开关。

---

### 表 9：`generate_config` 推理时并行配置

| 参数名 | 说明 |
|--------|------|
| `infer_tensor_parallel_size` | TP并行策略数 |
| `infer_pipeline_parallel_size` | PP并行策略数，当前未支持该功能，设置为 '1' |
| `infer_expert_parallel_size` | EP并行策略数 |

**解读**：推理端的并行度独立于训练端配置，可以根据 rollout 节点的实际算力单独调整。文档显式标注 `infer_pipeline_parallel_size` 当前未支持须置 1，是已知功能边界声明。

---

### 表 10：resharding 与显存卸载配置

| 参数名 | 说明 |
|--------|------|
| `trust_remote_code` | 是否信任远程代码执行 |
| `offload_train_optimizer` | 卸载训练节点优化器 |
| `offload_train_grad` | 卸载训练节点梯度 |
| `offload_train_param` | 卸载模型权重 |

**解读**：四个参数共同解决「训练与推理争抢显存」的问题。推理端启动 rollout 时，通过 `offload_train_*` 系列将训练侧的优化器状态、梯度、参数卸载到 CPU/Host 内存，腾出显存给 vLLM；rollout 完成后可重新加载继续训练。

---

### 表 11：vLLM 模型参数

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

**解读**：该表直接透传 vLLM 引擎参数。`enforce_eager` 默认开启意味着默认走 PyTorch eager 路径，仅在 DeepSeek V3 开启 `torchair_graph` 时关闭以兼容图模式编译；`enable_expert_parallel` 是 MOE 模型专用开关。

---

### 表 12：采样配置

| 参数名 | 说明 |
|--------|------|
| `logprobs` | 是否生成logprobs |
| `max_tokens` | 单条response最大生成token数量 |
| `top_p` | vllm 筛选出概率累积和达到top_p的token集合，随后只在这个集合里进行采样 |
| `top_k` | vllm 会先选出概率最高的 top_k 个 token，然后在这 top_k 个 token 范围内进行采样 |
| `min_p` | vllm 过滤掉概率低于 min_p 的token，不参与后续的采样过程 |
| `temperature` | 采样时的随机性参数 |
| `detokenize` | 是否将输出token重新转为文本 |

**解读**：标准的 vLLM 采样超参数集合。其中 `logprobs` 是 PPO 训练必需（需用其计算重要性采样比），`max_tokens` 控制 response 长度上限与 `max_prompt_length` 共同决定 `max_model_len = prompt + response`。

---

## 【公式解读】

**原文无公式**。文档为参数说明性质，仅列出参数名与自然语言说明，未涉及 PPO 损失函数、优势估计公式、KL 散度计算公式等数学表达。

---

## 【关联】

本文档处于 MindSpeed RL 配置体系的最顶层导航位置，向下涉及以下关联节点：

1. **直接引用的示例配置文件**：[`ppo_qwen25_32b_A3.yaml`](../../../configs/ppo_qwen25_32b_A3.yaml)（文末内部链接，是 Qwen2.5-32B 在 A3 机器上 PPO 训练的最完整示例）。
2. **模型结构定义层**：`configs/model/` 子目录下的 YAML 文件（如 `qwen25_7b.yaml`），通过 `defaults.model` 字段被各 `ppo_trainer` 文件引用——这是层级化配置解耦设计的核心连接点。
3. **训练引擎层**：所有 `megatron_training` 中标注「其余参数为 Megatron 训练中的特性配置」项，与 Megatron-LM 训练引擎的原生配置体系一一对应，可参考 Megatron 官方文档查阅（本文档未提供直接链接）。
4. **vLLM 推理引擎层**：`generate_config` 中的 vLLM 参数直接调用 [vllm官网参数介绍](https://docs.vllm.ai/en/stable/configuration/engine_args) 文档，原文明确给出该链接。
5. **上游特性模块**：
   - 「全共卡模式」对应 `use_integrated_worker` 开关；
   - 「TransferDock 保序」对应 `guarantee_order` 开关，可能与集合通信库 TransferDock 的相关特性文档关联；
   - 「规则奖励」对应 `rule_reward`，涉及 `configs/` 下规则奖励函数（verifier）的注册机制。
6. **下游训练流程**：本文档定义的五大字段共同作用，最终驱动 Ray-based PPO 主控、actor-train rollout 同步、critic 训练、advantage 计算、KL 惩罚等完整 RLHF 训练流程。

---

## 【使用方法】

原文未涉及启动命令、环境变量或 CLI 入口形式的「启用方式」说明。可获取的有效配置引导信息为：

1. **参考完整示例**：所有字段的具体取值请参照 [`ppo_qwen25_32b_A3.yaml`](../../../configs/ppo_qwen25_32b_A3.yaml)（原文：「具体的参数配置格式请参照示例 [配置文件](../../../configs/ppo_qwen25_32b_A3.yaml)」）。
2. **模型选择占位**：`defaults` 中以 `model: qwen25_7b`（举例）形式指定要引入的模型配置文件名，路径位于 `configs/model/` 目录下。
3. **训练算法选择占位**：`megatron_training.stage` 须设为 `ray_ppo` 方可启用 Ray PPO 训练。
4. **资源分配占位**：在 `rl_config` 下以如下结构显式声明 Actor 与 Critic 各自使用的 NPU 卡数：
   ```yaml
   actor_resource:
       num_npus: 4
   critic_resource:
       num_npus: 4
   ```
5. **互斥日志开启**：`use_tensorboard` 与 `use_wandb` 中任选一项为 True，避免同时开启导致 tensorboard 失效。

> 备注：原文未提供具体的训练启动命令（如 `python -m megatron ...` 或 `bash run_ppo.sh` 之类），如需了解完整启动流程应进一步阅读 MindSpeed RL 主仓的快速入门或训练启动相关文档（本文档未链接）。
