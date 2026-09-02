# 步数蒸馏

> 仓 `flashgen` · 路径 `docs/features/step_distill.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/flashgen/docs/features/step_distill.md

# FlashGen · 步数蒸馏 (Step Distill) 文档深度解读

---

## 【定位】

本文档描述 FlashGen 基于 **DMD2** (Improved Distribution Matching Distillation) 实现的 **Wan 2.1 T2V 1.3B 步数蒸馏**能力：将扩散模型原本需要的数十次去噪压缩为 **3 个** 离散蒸馏步，在尽量保持生成质量的同时显著降低推理时延，并给出已在单机 8 卡昇腾 NPU 环境完成端到端验证的训练配置。

---

## 【技术要点】

1. **三角色 DMD2 训练范式**：Teacher（冻结，提供真实分布 score 参考）/ Student（待蒸馏的目标 Generator）/ Critic（学习 Student 当前输出分布，与 Teacher score 共同构造 Student 优化方向）；Student 和 Critic 需要 `trainable: true`，Teacher 必须 `trainable: false`。
2. **3 步离散蒸馏时间步**：`dmd_denoising_steps = [1000, 757, 522]`，列表长度即蒸馏步数；命令中该参数建议加引号避免被 shell 当作模式表达式处理。
3. **两套 Student rollout 模式**：
   - `data_latent`（默认）：真实 VAE latent 加噪后单步有梯度 Student 前向；
   - `simulate`：纯随机噪声模拟少步推理轨迹，3 步配置下执行 **2 次无梯度 + 1 次有梯度** Student 前向，计算量更高但更接近真实推理分布。
4. **非对称更新节奏**：Critic **每次迭代**都更新；Student 按 `generator_update_interval = 5` 的间隔更新。
5. **离线 Negative Prompt 编码**：通过 `scripts/encode_negative_prompt.py` 预先生成 `negative_prompt_embeds.pt` 与 `negative_prompt_attention_mask.pt`，避免多卡训练时在线文本编码触发 collective 通信死锁；Student / Teacher / Critic 三个角色均显式指定同一 `negative_prompt_embeds_path`。
6. **DMD2 方法关键超参**：`real_score_guidance_scale = 3.5`（Teacher 条件/无条件 score 的 CFG 引导强度）、`fake_score_learning_rate = 1e-5`、`fake_score_betas = [0.0, 0.999]`、`fake_score_lr_scheduler = constant`；原文强调**三项 Critic 配置均不可省略**，不会自动回退到 Student 优化器配置。
7. **配置覆盖机制**：以 `flashgen/configs/wan_dmd_npu.yaml` 为默认，支持 `--dotted.key value` 命令行覆盖（如 `--method.rollout_mode simulate`）。
8. **昇腾适配**：使用 NPU 安全的 Torch SDPA attention backend，支持单卡与分布式训练；`training.dit_precision = fp32`、`pipeline.vae_precision = bf16`、`enable_gradient_checkpointing_type = block_skip` 配合控制显存。

---

## 【关键机制与数据】

- **核心机制（原文：「DMD2 通过匹配 Student 与预训练模型的输出分布，使 Student 学会用少量离散时间步完成去噪。」）**：Teacher 提供真实数据分布的 score，Critic 学习 Student 的输出分布，二者的 score 差异构造出 Student 的梯度优化方向，使 Student 收敛到少步去噪即可拟合原分布的能力。
- **Rollout 数据流（原文示例）**：
  - `data_latent`：`真实 latent ──加噪到 522──> Student@522（有梯度）──> 预测结果`
  - `simulate`：`随机噪声 ──> Student@1000（无梯度） ──加噪到 757──> Student@757（无梯度） ──加噪到 522──> Student@522（有梯度）──> 预测结果`
- **有效 Batch Size 公式（原文）**：
  `4（每 rank batch size）× 8（rank 数）× 2（梯度累积）= 64`
- **模型导出**：支持将 DCP checkpoint 中的 Student 转换为 Diffusers 格式（用于下游推理）。
- **质量评估入口**：训练完成后的质量评估请参见[基准验证](benchmark.md)（文档本身未给出蒸馏前后 FID/CLIP/时延等具体数值，所有性能数据均外链至 benchmark 文档）。
- **显存不足策略（原文）**：「优先降低 `train_batch_size`，并相应提高 `gradient_accumulation_steps` 以维持目标有效 batch size。」
- **关于 VALIDATION_DIR**：示例命令刻意**不保留**未使用的 `VALIDATION_DIR` 变量——「仅在 shell 中定义验证集路径变量不会启用验证」。

> 说明：原文未直接给出蒸馏前后的延迟/FID/质量等具体性能数字，本节所有数据均严格来自训练配置本身（batch size、步数、精度、并行维度等），不外推。

---

## 【表格解读】

### 1. 训练三角色表（原文逐字还原）

| 角色 | 是否训练 | 作用 |
|------|----------|------|
| **Teacher** | 否 | 预训练 Wan 模型，提供真实数据分布的 score 参考 |
| **Student** | 是 | 蒸馏目标模型（Generator），训练完成后用于导出和推理 |
| **Critic** | 是 | 学习 Student 当前的输出分布，与 Teacher 的 score 共同构造 Student 的优化方向 |

**逐行解读**：
- **Teacher（冻结）**：以原 Wan 2.1 T2V 1.3B 权重初始化，全程不参与梯度更新；唯一作用是提供「真实数据分布 score」作为 Student 优化的参照信号，并承担 CFG 中无条件分支的计算。
- **Student（可训练）**：本文档的最终交付物；训练完成后用于导出 DCP checkpoint，再转换为 Diffusers 格式供推理。
- **Critic（可训练）**：本质是 Student 的「镜像评分器」，持续拟合 Student 当前输出分布；其与 Teacher 的 score 之差决定 Student 优化方向，因此必须随 Student 一起迭代，但又不能更新得太快导致不稳定——这正是后文 `generator_update_interval=5` 的设计动机。

---

### 2. 视频规格参数表（原文逐字还原）

| 参数 | 已验证值 | 说明 |
|------|----------|------|
| `num_frames` | `77` | 视频帧数 |
| `num_height` | `448` | 视频高度 |
| `num_width` | `832` | 视频宽度 |
| `num_latent_t` | `20` | 77 帧视频经过 VAE 时间压缩后的 latent 长度 |

**逐行解读**：
- 四项参数共同决定了 `data_latent` 模式下读取真实 VAE latent 时张量的形状契约：`num_latent_t = 20` 是由 77 帧经过 VAE 时间维压缩后得到，因此**实际数据规格必须与命令行中这四个数值完全一致**，否则 Student rollout 的张量形状不匹配。

---

### 3. Rollout 模式对比表（原文逐字还原）

| 模式 | Student 输入 | 单次 rollout | 数据集作用 |
|------|---------------|--------------|------------|
| `data_latent` | 真实视频 latent 加噪 | 随机选择一个蒸馏时间步，执行 1 次有梯度 Student 前向 | 提供真实 latent、文本条件和样本元数据 |
| `simulate` | 纯随机噪声 | 模拟少步推理轨迹，前序步骤无梯度，目标步骤有梯度 | 提供文本条件和样本元数据；真实 latent 不作为 Student 起点 |

**逐行解读**：
- `data_latent` 是**计算更轻**的默认路径：直接把训练数据中已经 VAE 编码好的 latent 加噪一步即可；但其 Student 起点分布与真实推理时「纯噪声起步」存在 mismatch。
- `simulate` 是**更贴近真实少步推理**的路径：从纯噪声出发按 `[1000, 757, 522]` 串行 rollout 完整轨迹，前序步骤全部 `torch.no_grad()`，只在最终目标步骤反向传播；缺点是训练计算量更高（3 步配置下 = 2 次无梯度 + 1 次有梯度前向）。
- 文中特别提醒：**即使切换到 `simulate`，DataLoader 仍需读取训练数据目录**，因为需要从中取文本 embedding、attention mask 和批次元数据。

---

### 4. DMD2 方法参数表（原文逐字还原）

| 参数 | 已验证值 | 说明 |
|------|----------|------|
| `method.rollout_mode` | `data_latent` | 从真实 VAE latent 加噪后执行单步 Student rollout |
| `method.generator_update_interval` | `5` | 每 5 次训练迭代更新一次 Student；Critic 仍按每次迭代更新 |
| `method.real_score_guidance_scale` | `3.5` | Teacher 条件/无条件 score 的 CFG 引导强度 |
| `method.dmd_denoising_steps` | `[1000,757,522]` | Student rollout 使用的离散时间步，列表长度对应蒸馏步数 |
| `method.fake_score_learning_rate` | `1e-5` | Critic 优化器学习率，必须为正数 |
| `method.fake_score_betas` | `[0.0,0.999]` | Critic Adam betas；本命令沿用 YAML 值 |
| `method.fake_score_lr_scheduler` | `constant` | Critic 学习率调度器；本命令沿用 YAML 值 |

**逐行解读**：
- `generator_update_interval=5` 与 Critic 每次迭代都更新形成「Critic 追 Student」的 5:1 步频比，是 DMD2 类方法的标准做法，避免 Critic 落后太多导致 score 估计失真。
- `real_score_guidance_scale=3.5` 同时控制 Teacher 自身条件/无条件分支的 CFG 强度，影响 score 估计质量。
- 文档**特别警告**：`fake_score_learning_rate`、`fake_score_betas`、`fake_score_lr_scheduler` 三项必须保留，不允许删除——当前实现不会自动回退到 Student 优化器配置，否则会训练失败。

---

### 5. 数据、并行与有效 Batch Size 表（原文逐字还原）

| 参数 | 已验证值 | 说明 |
|------|----------|------|
| `training.data.train_batch_size` | `4` | 每个 rank 的 batch size |
| `training.data.seed` | `1024` | 数据管线和训练采样使用的随机种子 |
| `training.data.dataloader_num_workers` | `0` | 在训练进程内加载数据，便于规避多进程数据加载问题；可能降低吞吐 |
| `training.data.training_cfg_rate` | `0` | 不对训练条件做随机 CFG dropout |
| `training.loop.gradient_accumulation_steps` | `2` | 梯度累积步数 |
| `training.distributed.num_gpus` | `8` | 参与训练的设备数；参数名沿用上游，昇腾环境中指 NPU 数量 |
| `training.distributed.sp_size` | `1` | sequence parallel 规模，本配置未启用 SP |
| `training.distributed.hsdp_replicate_dim` | `1` | HSDP replicate 维度 |
| `training.distributed.hsdp_shard_dim` | `8` | HSDP shard 维度，与本例的 world size 一致 |

**逐行解读**：
- `dataloader_num_workers=0` 是个有意选择——多进程 DataLoader 在某些昇腾 + 共享存储场景下存在稳定性问题，宁可牺牲吞吐也要在训练进程内加载。
- `training_cfg_rate=0` 表示训练阶段不做条件 dropout（区别于 `real_score_guidance_scale` 的推理期 CFG）。
- `sp_size=1` 明确**未启用** sequence parallel；并行拓扑退化为标准 HSDP（`hsdp_replicate_dim=1, hsdp_shard_dim=8`），等价于 DDP。
- 由本表参数直接代入公式即可得出**有效 batch size = 4 × 8 × 2 = 64**（见后文「公式解读」）。

---

### 6. 优化、精度与检查点表（原文逐字还原，原文此处被截断）

| 参数 | 已验证值 | 说明 |
|------|----------|------|
| `training.optimizer.learning_rate` | `1e-5` | Student 学习率 |
| `training.optimizer.weight_decay` | `0.01` | Student 优化器权重衰减 |
| `training.optimizer.lr_scheduler` | `constant` | Student 使用恒定学习率调度 |
| `training.optimizer.lr_warmup_steps` | `10` | Student 学习率 warmup 步数 |
| `training.loop.max_train_steps` | `4000` | 最大训练迭代数 |
| `training.model.enable_gradient_checkpointing_type` | `block_skip` | 使用 block-skip gradient checkpointing 降低激活显存 |
| `training.dit_precision` | `fp32` | DiT 训练精度 |
| `pipeline.flow_shift` | `8` | Wan FlowMatch 调度器的 shift 参数 |
| `pipeline.vae_precision` | `bf16` | VAE 计算精度 |
| `callbacks.grad_clip.max_grad_norm` | ` （原文此处行未结束，值列与说明列缺失） | — |

**逐行解读**：
- Student 主优化器采用 `lr=1e-5 / weight_decay=0.01 / constant scheduler / 10 步 warmup`，是相当保守的设定，符合蒸馏场景下不希望破坏预训练分布的需求。
- `max_train_steps=4000` 是已验证的训练长度（与 Critic 每步更新、Student 每 5 步更新对应）。
- `block_skip` 形式的 gradient checkpointing 比默认实现更激进地跳过中间激活的保存，配合 `dit_precision=fp32` 在 fp32 主权重下训练仍能放入 8 卡显存。
- DiT 用 fp32、VAE 用 bf16 形成「主模型高数值精度 + 编解码低精度」的混合策略；`flow_shift=8` 是 Wan FlowMatch 调度器专用超参。
- **`callbacks.grad_clip.max_grad_norm` 一行在原文中被截断**（行末仅剩 `| \``），具体已验证值与说明缺失——本解读不臆造。

---

## 【公式解读】

### 原文公式（逐字保留）

```text
4（每 rank batch size）× 8（rank 数）× 2（梯度累积）= 64
```

**符号解释**：
- `4`（每 rank batch size）：即 `training.data.train_batch_size = 4`，每个 NPU rank 在一次 micro-batch 前向中处理的样本数。
- `8`（rank 数）：即 `training.distributed.num_gpus = 8`，单机 8 卡全量参与；`sp_size=1` 表示未启用 sequence parallel，因此「rank 数」=「数据并行度」。
- `2`（梯度累积）：即 `training.loop.gradient_accumulation_steps = 2`，累积 2 个 micro-batch 后再执行一次优化器 step。
- 等号右侧 `64`：表示**一个完整梯度更新周期内被 Student（以及 Critic）实际看到的样本总数**，即业内所说的「effective batch size」。

**作用**：原文用此公式明确单次 `optimizer.step()` 等效 batch 大小；并紧接着给出**显存不足时的调参原则**——优先降低 `train_batch_size`，再按比例上调 `gradient_accumulation_steps` 以保持 64 这一目标值不变。

---

### 采样轨迹伪代码（原文逐字保留）

```text
data_latent:
真实 latent ──加噪到 522──> Student@522（有梯度）──> 预测结果

simulate:
随机噪声 ──> Student@1000（无梯度）
         ──加噪到 757──> Student@757（无梯度）
         ──加噪到 522──> Student@522（有梯度）──> 预测结果
```

**符号解释**：
- `Student@t`：表示在离散时间步 `t` 上调用 Student 前向。原文 `[1000, 757, 522]` 即 `dmd_denoising_steps`，对应 DMD2 默认的 3 步采样轨迹上的三个离散点。
- `（有梯度）` / `（无梯度）`：标识该次 Student 前向是否参与反向传播。`simulate` 模式中只有**最终目标步骤**反传，前序步骤全部 `torch.no_grad()`。
- `加噪到 X`：在 `data_latent` 模式中，对真实 VAE latent 按时间步 `X` 加噪；在 `simulate` 模式中，对前一步 Student 的预测 `x0` 按时间步 `X` 加噪。

**作用**：这是 DMD2 rollout 的**数据流定义**，直观说明两种模式在前向次数、计算量、Student 起点分布上的差异——`data_latent` 走单步直路，`simulate` 走完整 3 步推理模拟。

---

## 【关联】

依据文末及正文中出现的内部链接，文档存在以下上下游关系：

1. **上游 / 训练环境**：[`../quick_start.md`](../quick_start.md)
   - 在「训练前准备 → 环境与预训练模型」一节中明确：用户需先按照「快速开始」完成 **FlashGen 安装** 与 **昇腾训练环境安装**，并准备 **Diffusers 格式的 Wan 2.1 T2V 1.3B 预训练模型**。即步数蒸馏训练强依赖快速开始文档中的环境与基础模型准备流程。

2. **下游 / 质量评估**：[`benchmark.md`](benchmark.md)（文末链接出现 2 次：列表 + 正文引用）
   - 在「启动训练 → 8 卡已验证配置」末尾：示例命令**没有配置训练中验证**，并提示「训练完成后的质量评估请参见[基准验证](benchmark.md)」。
   - 在文末链接列表中再次出现 [`benchmark.md`](benchmark.md)，确认步数蒸馏训练结束后的量化指标（FID / 延迟 / 视觉质量）评估入口在基准验证文档中。

3. **同仓库特性关系**（基于标题与术语推断）：
   - 「量化感知」属于 FlashGen 另一条加速主线，本篇只描述步数蒸馏，二者**正交、可组合**（Student 蒸馏完成后可再施加量化）。
   - 文档多处引用 DMD2 原论文 [arXiv:2405.14867](https://arxiv.org/abs/2405.14867)，表明步数蒸馏实现严格对齐上游公开方法，未做本质改动。

---

## 【使用方法】

### 1. 离线编码 Negative Prompt（训练前必做）

```bash
python scripts/encode_negative_prompt.py \
  --model_path /path/to/Wan2.1-T2V-1.3B-Diffusers \
  --output_dir /path/to/negative_prompt
```
预期产物：
```text
negative_prompt/
├── negative_prompt_embeds.pt
└── negative_prompt_attention_mask.pt
```

### 2. 单机 8 卡端到端训练命令（已验证）

```bash
export TOKENIZERS_PARALLELISM=false

NUM_GPUS=8
DATA_DIR=/path/to/training_dataset
MODEL_PATH=/path/to/Wan2.1-T2V-1.3B-Diffusers
NEG_PROMPT_DIR=/path/to/negative_prompt
OUTPUT_DIR=/path/to/training_outputs

torchrun \
  --nnodes 1 \
  --nproc_per_node "$NUM_GPUS" \
  train.py \
  --config flashgen/configs/wan_dmd_npu.yaml \
  --models.student.init_from "$MODEL_PATH" \
  --models.teacher.init_from "$MODEL_PATH" \
  --models.critic.init_from "$MODEL_PATH" \
  --models.student.negative_prompt_embeds_path "$NEG_PROMPT_DIR" \
  --models.teacher.negative_prompt_embeds_path "$NEG_PROMPT_DIR" \
  --models.critic.negative_prompt_embeds_path "$NEG_PROMPT_DIR" \
  --method.rollout_mode data_latent \
  --training.data.data_path "$DATA_DIR" \
  --training.data.train_batch_size 4 \
  --training.data.num_latent_t 20 \
  --training.data.num_height 448 \
  --training.data.num_width 832 \
  --training.data.num_frames 77 \
  --training.data.seed 1024 \
  --training.data.dataloader_num_workers 0 \
  --training.data.training_cfg_rate 0 \
  --training.distributed.num_gpus "$NUM_GPUS" \
  --training.distributed.sp_size 1 \
  --training.distributed.hsdp_replicate_dim 1 \
  --training.distributed.hsdp_shard_dim "$NUM_GPUS" \
  --training.optimizer.learning_rate 1e-5 \
  --training.optimizer.weight_decay 0.01 \
  --training.optimizer.lr_scheduler constant \
  --training.optimizer.lr_warmup_steps 10 \
  --method.fake_score_learning_rate 1e-5 \
  --method.generator_update_interval 5 \
  --method.real_score_guidance_scale 3.5 \
  --method.dmd_denoising_steps "[1000,757,522]" \
  --training.loop.max_train_steps 4000 \
  --training.loop.gradient_accumulation_steps 2 \
  --training.checkpoint.output_dir "$OUTPUT_DIR" \
  --training.checkpoint.training_state_checkpointing_steps 300 \
  --training.tracker.project_name wan_dmd_distill \
  --training.tracker.run_name wan_dmd_distill \
  --training.model.enable_gradient_checkpointing_type block_skip \
  --training.dit_precision fp32 \
  --pipeline.flow_shift 8 \
  --pipeline.vae_precision bf16 \
  --callbacks.grad_clip.max_grad_norm 1.0
```
**注意**：命令中**刻意不保留** `VALIDATION_DIR` 变量，因为「仅在 shell 中定义不会被 train.py 消费」。

### 3. 切换 `simulate` 模式

在命令中追加：
```bash
--method.rollout_mode simulate
```
或临时单次切换（其余沿用默认 YAML）。

### 4. 单卡调试命令（已验证）

```bash
NUM_GPUS=1

torchrun \
  --nnodes 1 \
  --nproc_per_node "$NUM_GPUS" \
  train.py \
  --config flashgen/configs/wan_dmd_npu.yaml \
  --training.distributed.num_gpus "$NUM_GPUS" \
  --training.distributed.hsdp_replicate_dim 1 \
  --training.distributed.hsdp_shard_dim 1 \
  --training.data.train_batch_size 1 \
  --training.loop.max_train_steps 10
```
> 单卡命令仅展示分布式与调试参数；**模型、数据、negative prompt 路径仍需通过 YAML 或命令行正确设置**。

### 5. 默认 YAML 关键片段（位于 `flashgen/configs/wan_dmd_npu.yaml`）

```yaml
method:
  rollout_mode: data_latent

models:
  student:
    _target_: flashgen.networks.wan.WanModel
    init_from: /path/to/Wan2.1-T2V-1.3B-Diffusers
    trainable: true
    negative_prompt_embeds_path: /path/to/negative_prompt
  teacher:
    _target_: flashgen.networks.wan.WanModel
    init_from: /path/to/Wan2.1-T2V-1.3B-Diffusers
    trainable: false
    disable_custom_init_weights: true
    negative_prompt_embeds_path: /path/to/negative_prompt
  critic:
    _target_: flashgen.networks.wan.WanModel
    init_from: /path/to/Wan2.1-T2V-1.3B-Diffusers
    trainable: true
    disable_custom_init_weights: true
    negative_prompt_embeds_path: /path/to/negative_prompt
```
**使用约束**：三个角色必须从同一套预训练权重初始化；Teacher 必须保持 `trainable: false`，Student / Critic 必须 `trainable: true`。

### 6. 文档截断说明

原文在「优化、精度与检查点」参数表的最后一行 `callbacks.grad_clip.max_grad_norm` 处被截断（已验证值列与说明列缺失）。根据命令行上下文推测该参数已验证值为 `1.0`（来自 8 卡训练命令末尾的显式传参），但**本文严格忠实于原文呈现内容**，不擅自补全缺失说明文字。
