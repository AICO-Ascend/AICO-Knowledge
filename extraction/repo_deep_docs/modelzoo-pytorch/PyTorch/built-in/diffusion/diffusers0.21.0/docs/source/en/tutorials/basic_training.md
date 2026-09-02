# Train a diffusion model

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/diffusion/diffusers0.21.0/docs/source/en/tutorials/basic_training.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/diffusion/diffusers0.21.0/docs/source/en/tutorials/basic_training.md

# 一体化深度解读：Train a diffusion model

---

## 【定位】

这篇文档是 🧨 Diffusers 库中面向 **完全无条件图像生成（unconditional image generation）** 的入门级实操教程, 演示如何从零训练一个 `UNet2DModel`, 在 Smithsonian Butterflies 子集数据集上生成蝴蝶图像 —— 解决"在找不到合适的预训练 checkpoint 时, 如何用 Diffusers 自行训练/微调一个无条件扩散模型"这一问题。

---

## 【技术要点】

1. **数据集与依赖**: 使用 🤗 `datasets` 加载 `huggan/smithsonian_butterflies_subset` (Smithsonian Butterflies 子集), 配合 🤗 `Accelerate` (多 GPU 训练) 和 TensorBoard (可视化训练指标; 也可替换为 Weights & Biases)。
2. **安装与认证**:
   - 库安装: `pip install diffusers[training]` (原文以 Colab 安装注释形式给出)。
   - Hugging Face 登录: 笔记本内 `notebook_login()` 或终端 `huggingface-cli login`; 配合 `apt -qq install git-lfs` 与 `git config --global credential.helper store` 处理大文件上传。
3. **训练超参 `TrainingConfig` dataclass** (原文逐字段保留):
   - `image_size = 128`
   - `train_batch_size = 16`, `eval_batch_size = 16`
   - `num_epochs = 50`, `gradient_accumulation_steps = 1`
   - `learning_rate = 1e-4`, `lr_warmup_steps = 500`
   - `save_image_epochs = 10`, `save_model_epochs = 30`
   - `mixed_precision = "fp16"` (注释: `no` 为 float32, `fp16` 为自动混合精度)
   - `output_dir = "ddpm-butterflies-128"`
   - `push_to_hub = True`, `hub_private_repo = False`, `overwrite_output_dir = True`, `seed = 0`
4. **数据预处理流水线 (`torchvision.transforms.Compose`)**: `Resize((128, 128))` → `RandomHorizontalFlip()` → `ToTensor()` → `Normalize([0.5], [0.5])`, 将像素归一化到 `[-1, 1]` 以匹配模型期望; 通过 `dataset.set_transform(transform)` 训练时按需应用; 最终用 `torch.utils.data.DataLoader` 封装 (batch_size=16, `shuffle=True`)。
5. **`UNet2DModel` 结构构造** (关键参数原文):
   - `sample_size=128`, `in_channels=3`, `out_channels=3`
   - `layers_per_block=2`
   - `block_out_channels=(128, 128, 256, 256, 512, 512)` (共 6 个 UNet 块)
   - `down_block_types` 6 个, 其中第 5 个为 `AttnDownBlock2D` (带空间自注意力的 ResNet 下采样块), 其余为 `DownBlock2D`
   - `up_block_types` 6 个, 第 2 个为 `AttnUpBlock2D` (带空间自注意力的 ResNet 上采样块), 其余为 `UpBlock2D`
6. **`DDPMScheduler` 加噪调用**:
   - `DDPMScheduler(num_train_timesteps=1000)`
   - `noise = torch.randn(sample_image.shape)` 采样与输入同形状的高斯噪声
   - `timesteps = torch.LongTensor([50])` 取一个具体时刻
   - `noisy_image = noise_scheduler.add_noise(sample_image, noise, timesteps)` 按 noise schedule 在指定时刻注入噪声。

---

## 【关键机制与数据】

- **扩散模型角色分工** (原文): "During inference, the scheduler generates image from the noise. During training, the scheduler takes a model output - or a sample - from a specific point in the diffusion process and applies noise to the image according to a *noise schedule* and an *update rule*." 即 scheduler 在推理时从噪声生成图像, 在训练时按 noise schedule 与 update rule 对模型输出/样本施加噪声。
- **数据流** (原文):
  1. `load_dataset("huggan/smithsonian_butterflies_subset", split="train")` → 原始蝴蝶图像 (`PIL.Image`)
  2. `transform` 函数将每张图 `.convert("RGB")` 后经 preprocess 转张量并写入 `{"images": images}`, 通过 `set_transform` 挂载为懒变换
  3. `DataLoader` 按 `train_batch_size=16` 打乱采样
  4. 取出 `sample_image` 形状验证: 原文实测 `Input shape: torch.Size([1, 3, 128, 128])`, 模型 `model(sample_image, timestep=0).sample` 输出 `Output shape: torch.Size([1, 3, 128, 128])` —— 输入输出维度一致。
  5. 训练循环中, `DDPMScheduler.add_noise(image, noise, timesteps)` 产生 `noisy_image` 作为扩散过程的训练样本 (原文代码片段在该步骤后被截断)。
- **归一化的原因** (原文): `Normalize([0.5], [0.5])` "is important to rescale the pixel values into a `[-1, 1]` range, which is what the model expects."
- **数据增强**: `RandomHorizontalFlip()` "augments the dataset by randomly mirroring the images".
- **典型 epoch/保存节奏** (原文 `TrainingConfig`): 每 10 个 epoch 保存一次采样图像 (`save_image_epochs=10`), 每 30 个 epoch 保存一次模型 (`save_model_epochs=30`)。
- **注**: 原文未提供训练 loss 曲线、最终 FID/IS 等性能指标, 也未给出 wall-clock 训练时长 —— 性能/精度数据原文中不存在。

---

## 【表格解读】

原文无表格。

(整篇文档以 markdown 文本 + Python 代码块为主, 没有出现 `| 列 | 列 |` 形式的 markdown 表格, 也没有 ASCII 表; `TrainingConfig` 与 `UNet2DModel` 构造均以 Python dataclass / 关键字参数呈现, 而非表格化定义。)

---

## 【公式解读】

原文无公式。

(文档不包含 LaTeX 数学公式或伪代码形式的方程; 唯一的"算法步骤"是 `noise_scheduler.add_noise(sample_image, noise, timesteps)` 这一 API 调用, 没有显式的扩散过程数学表达, 例如前向过程 $q(x_t \mid x_{t-1})$ 或反向过程 $\epsilon_\theta$ 损失等都未在原文中展开。)

---

## 【关联】

根据文末内部链接信息, 本教程处于 diffusion 训练系列的 **入门级 (basic_training)** 位置, 与以下训练指南形成上下游/并列关系:

| 链接路径 | 关系定位 |
|---|---|
| `../training/overview` | 训练总览 —— 提供整个训练体系的入口与分类索引 |
| `../training/text_inversion` | 个性化文本引导: 通过学习新的 text embedding, 而非修改模型权重 |
| `../training/dreambooth` | 主题驱动微调: 用少量参考图将特定主体绑定到 token |
| `../training/text2image` | 文生图模型 (如 Stable Diffusion) 的训练范式 |
| `../training/lora` | 参数高效微调 (LoRA): 用低秩适配器替代全量微调 |

**逻辑关系**:
- 本教程 (`basic_training`) 是 **无条件图像生成** 的最小可运行示例, 用 `UNet2DModel` + `DDPMScheduler` 演示从数据、模型、scheduler 到训练循环的完整链路。
- `../training/overview` 是上层索引, 该教程可能从其中进入。
- `../training/text2image` 是其"条件化"升级版, 引入文本条件 (例如 CLIP text encoder), 而本教程完全无任何条件输入。
- `../training/dreambooth` / `../training/text_inversion` / `../training/lora` 则是 **在预训练 text2image 模型上做主体/概念注入或参数高效适配** 的路径, 与本教程"从零训练 UNet2DModel"形成两种相反方向的范式 (from-scratch vs. finetune/personalization)。

---

## 【使用方法】

### 启用方式 (按原文步骤)

1. **安装依赖** (原文 Colab 注释):
   ```bash
   pip install diffusers[training]
   ```
2. **登录 Hugging Face Hub** (任选其一):
   - 笔记本: `from huggingface_hub import notebook_login; notebook_login()`
   - 终端: `huggingface-cli login`
3. **配置 Git-LFS** (模型权重较大):
   ```bash
   sudo apt -qq install git-lfs
   git config --global credential.helper store
   ```

### 配置项 (`TrainingConfig` 字段, 原文逐字段)

```python
@dataclass
class TrainingConfig:
    image_size = 128
    train_batch_size = 16
    eval_batch_size = 16
    num_epochs = 50
    gradient_accumulation_steps = 1
    learning_rate = 1e-4
    lr_warmup_steps = 500
    save_image_epochs = 10
    save_model_epochs = 30
    mixed_precision = "fp16"   # "no"=float32, "fp16"=自动混合精度
    output_dir = "ddpm-butterflies-128"
    push_to_hub = True
    hub_private_repo = False
    overwrite_output_dir = True
    seed = 0
```

### 关键命令/调用

- 加载数据集: `dataset = load_dataset("huggan/smithsonian_butterflies_subset", split="train")`
- 自定义数据集: `config.dataset_name = "imagefolder"` (使用本地 `ImageFolder`)
- 预处理流水线: `Resize((image_size, image_size))` → `RandomHorizontalFlip()` → `ToTensor()` → `Normalize([0.5], [0.5])`
- 模型创建: `UNet2DModel(sample_size, in_channels=3, out_channels=3, layers_per_block=2, block_out_channels=(128,128,256,256,512,512), down_block_types=..., up_block_types=...)`
- 噪声调度: `DDPMScheduler(num_train_timesteps=1000)` + `add_noise(sample_image, noise, timesteps)`

### 原文未涉及的内容

- 训练循环主代码 (optimizer、loss、backward、scheduler.step) **在原文中被截断**, 原文仅保留到 `Image.fromarray(((noisy_image.permute(0, 2, 3, 1)` 处即中止; 因此"完整训练步骤 / sampling loop / 评估指标"等具体命令本节无法从原文逐字给出。
- Accelerate launch 命令 (`accelerate launch ...`)、`lr_scheduler`、`AdamW` 优化器、`noise_pred = model(noisy_image, timesteps).sample` / MSE 损失等训练循环细节: **原文未涉及**, 应在文末链接的 "Training with 🧨 Diffusers" Colab notebook 中查阅。
