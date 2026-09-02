# Diffusion 모델을 학습하기

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/diffusion/diffusers0.25.0/docs/source/ko/tutorials/basic_training.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/diffusion/diffusers0.25.0/docs/source/ko/tutorials/basic_training.md

# 一体化深度解读：Diffusion 모델을 학습하기

## 【定位】
这篇文档是 🧨 Diffusers 库的入门级实操教程，旨在手把手教会用户**在自定义图像数据集（以 Smithsonian Butterflies 为例）上从零微调/训练一个无条件图像生成的 `UNet2DModel`**，并把训练好的 checkpoint 推到 Hugging Face Hub。

---

## 【技术要点】

1. **任务定义**：unconditional image generation（在 Smithsonian Butterflies 子集 `huggan/smithsonian_butterflies_subset` 上训练 UNet2DModel，输出 128×128 蝴蝶图像）。原文建议可直接在 Hugging Face Hub 搜索现有 unconditional-image-generation checkpoint，或自行训练。

2. **训练超参（`TrainingConfig` 数据类）**：
   - `image_size = 128`
   - `train_batch_size = 16`，`eval_batch_size = 16`
   - `num_epochs = 50`
   - `gradient_accumulation_steps = 1`
   - `learning_rate = 1e-4`
   - `lr_warmup_steps = 500`
   - `save_image_epochs = 10`，`save_model_epochs = 30`
   - `mixed_precision = "fp16"`（取值 `"no"` 表示 float32，`"fp16"` 表示自动混合精度）
   - `output_dir = "ddpm-butterflies-128"`
   - `push_to_hub = True`，`hub_private_repo = False`，`overwrite_output_dir = True`，`seed = 0`

3. **数据预处理流水线（`torchvision.transforms.Compose`）**：
   - `Resize((config.image_size, config.image_size))`：统一到 128×128
   - `RandomHorizontalFlip()`：镜像增强
   - `ToTensor()`
   - `Normalize([0.5], [0.5])`：把像素缩放到 `[-1, 1]`，与模型期望范围对齐
   - 通过 `dataset.set_transform(transform)` 在训练时按需调用

5. **UNet2DModel 架构关键参数**：
   - `sample_size=128`，`in_channels=3`，`out_channels=3`
   - `layers_per_block=2`
   - `block_out_channels=(128, 128, 256, 256, 512, 512)`（6 个 UNet 块的输出通道）
   - `down_block_types=("DownBlock2D", "DownBlock2D", "DownBlock2D", "DownBlock2D", "AttnDownBlock2D", "DownBlock2D")`
   - `up_block_types=("UpBlock2D", "AttnUpBlock2D", "UpBlock2D", "UpBlock2D", "UpBlock2D", "UpBlock2D")`
   - 输入/输出形状验证：`Input shape: torch.Size([1, 3, 128, 128])` → `Output shape: torch.Size([1, 3, 128, 128])`

6. **噪声调度器 `DDPMScheduler(num_train_timesteps=1000)`**：用 `add_noise(sample_image, noise, timesteps)` 给图像加噪；示例中 `timesteps = torch.LongTensor([50])`。

7. **损失与优化**：
   - 损失：`loss = F.mse_loss(noise_pred, noise)`（模型预测噪声 vs 真实噪声的 MSE）
   - 优化器：`torch.optim.AdamW`，`lr=1e-4`
   - 学习率调度：`get_cosine_schedule_with_warmup`，`num_warmup_steps=500`，`num_training_steps = len(train_dataloader) * num_epochs`

8. **评估与采样**：通过 `DDPMPipeline`（基础输出为 `List[PIL.Image]`）生成 `eval_batch_size=16` 张图，并用 `make_grid(rows=4, cols=4)` 拼成网格后保存到 `output_dir/samples`。

---

## 【关键机制与数据】

原文涉及的数据流与原理（**仅记录原文中出现的内容**）：

- **数据流（原文）**：
  1. `load_dataset("huggan/smithsonian_butterflies_subset", split="train")` → `dataset`（`~datasets.Image` 自动解码为 `PIL.Image`）；
  2. 自定义 `transform(examples)` 把每张图 `convert("RGB")` 后过 `preprocess`，输出 `{"images": images}`，再 `dataset.set_transform(transform)` 注册；
  3. `torch.utils.data.DataLoader(dataset, batch_size=16, shuffle=True)` 构成 `train_dataloader`；
  4. 训练时 `noise = torch.randn(sample_image.shape)` 生成真实噪声，`noise_scheduler.add_noise(sample_image, noise, timesteps)` 得到 `noisy_image`；
  5. `noise_pred = model(noisy_image, timesteps).sample` → `F.mse_loss(noise_pred, noise)` 反向传播。

- **模型行为差异（原文）**：scheduler 在训练时按 *noise schedule* 与 *update rule* 把噪声应用到图像；推理时（`DDPMPipeline`）从随机噪声开始反向扩散生成图像（"이는 역전파 diffusion 과정입니다"）。

- **性能数据**：原文未给出训练耗时、GPU 利用率、显存占用或 FID 等定量指标（这些需要运行 notebook 才能获得，原文不提供）。

- **依赖与登录命令（原文）**：
  - 安装：`!pip install diffusers[training]`
  - Hugging Face Hub 登录：`from huggingface_hub import notebook_login; notebook_login()` 或 `huggingface-cli login`
  - Git-LFS：`!sudo apt -qq install git-lfs` + `!git config --global credential.helper store`
  - 辅助库：🤗 Datasets、🤗 Accelerate、TensorBoard、可选 Weights & Biases。

---

## 【表格解读】

**原文无表格**（`TrainingConfig` 是 Python `@dataclass`，不是 markdown 表格；其他内容均以代码块、列表和段落形式呈现）。

为方便对照，将 `TrainingConfig` 的字段以 markdown 表格形式**逐字还原**如下（来源即原文 dataclass 定义，仅做版式整理，未改字）：

| 字段 | 值 | 注释（原文直译） |
|---|---|---|
| `image_size` | `128` | 생성되는 이미지 해상도 |
| `train_batch_size` | `16` | — |
| `eval_batch_size` | `16` | 평가 동안에 샘플링할 이미지 수 |
| `num_epochs` | `50` | — |
| `gradient_accumulation_steps` | `1` | — |
| `learning_rate` | `1e-4` | — |
| `lr_warmup_steps` | `500` | — |
| `save_image_epochs` | `10` | — |
| `save_model_epochs` | `30` | — |
| `mixed_precision` | `"fp16"` | `no`는 float32, 자동 혼합 정밀도를 위한 `fp16` |
| `output_dir` | `"ddpm-butterflies-128"` | 로컬 및 HF Hub에 저장되는 모델명 |
| `push_to_hub` | `True` | 저장된 모델을 HF Hub에 업로드할지 여부 |
| `hub_private_repo` | `False` | — |
| `overwrite_output_dir` | `True` | 노트북을 다시 실행할 때 이전 모델에 덮어씌울지 |
| `seed` | `0` | — |

逐行解读：
- `image_size=128` 同时决定了 `transforms.Resize` 与 `UNet2DModel(sample_size=...)`，因此两者必须保持一致；
- `train_batch_size` 与 `eval_batch_size` 都为 16，`eval_batch_size` 还必须能被 `make_grid(rows=4, cols=4)=16` 整除；
- `gradient_accumulation_steps=1` 表示当前配置下不做梯度累积；
- `mixed_precision="fp16"` 是训练加速关键开关；
- `push_to_hub=True` + `hub_private_repo=False` 表示默认公开上传到 Hub，因此需要先执行 `notebook_login()`；
- `save_image_epochs=10` 与 `save_model_epochs=30` 分离，意味着每 10 个 epoch 出图评估、每 30 个 epoch 才落盘权重。

---

## 【公式解读】

**原文无标准数学公式**（没有 LaTeX 行内/行间公式，也没有伪代码块描述的更新规则），唯一以代码形式呈现的"损失公式"为：

```py
>>> import torch.nn.functional as F

>>> noise_pred = model(noisy_image, timesteps).sample
>>> loss = F.mse_loss(noise_pred, noise)
```

可写为等价的数学形式（**仅复现原文代码语义，不添加原文未出现的项**）：

$$
\mathcal{L} = \operatorname{MSE}\!\left(\,\hat{\varepsilon}_\theta(x_t, t),\ \varepsilon\,\right) = \left\|\hat{\varepsilon}_\theta(x_t, t) - \varepsilon\right\|_2^2
$$

符号含义（仅采用原文出现的量）：
- $\hat{\varepsilon}_\theta(x_t, t)$：模型 `model(noisy_image, timesteps).sample`，即 UNet2DModel 在第 $t$ 步对 $x_t$ 预测出的噪声，对应代码 `noise_pred`；
- $\varepsilon$：与 $x_t$ 同形状的高斯噪声 `noise = torch.randn(sample_image.shape)`，是 `add_noise` 实际混入图像的真实噪声；
- $x_t$：`noise_scheduler.add_noise(sample_image, noise, timesteps)` 的输出 `noisy_image`；
- $t$：`timesteps`，例子里取 `torch.LongTensor([50])`；
- $\operatorname{MSE}$：逐元素均方误差，对应 `F.mse_loss`。

注意：原文**没有给出**前向扩散公式 $x_t = \sqrt{\bar\alpha_t}\,x_0 + \sqrt{1-\bar\alpha_t}\,\varepsilon$ 或 DDPM 的 KL 推导，因此这里不予补全。

---

## 【关联】

原文正文提到的关联特性/工具：

- **[Smithsonian Butterflies](https://huggingface.co/datasets/huggan/smithsonian_butterflies_subset)**：训练用图像数据集。
- **[HugGan Community Event](https://huggingface.co/huggan)**：可获取更多图像数据集；导入方式有两条规则：
  - HugGan 数据集 → `config.dataset_name = <repo id>`；
  - 本地自定义图像 → `config.dataset_name = "imagefolder"`（对应 `ImageFolder`）。
- **🤗 Datasets**：`load_dataset`、`~datasets.Image`、`~datasets.Dataset.set_transform`。
- **🤗 Accelerate**：原文提到"다수 GPU에서 학습을 간소화하기 위해"安装，但本教程的训练循环并未真正使用 `Accelerator`。
- **TensorBoard / Weights & Biases**：可视化与追踪（原文仅建议安装，未提供集成代码）。
- **`DDPMScheduler`** / **`DDPMPipeline`**：训练加噪与推理采样。
- **`diffusers.optimization.get_cosine_schedule_with_warmup`**：带 warmup 的余弦 LR。
- **`UNet2DModel`** 与各种 block（`DownBlock2D` / `AttnDownBlock2D` / `UpBlock2D` / `AttnUpBlock2D`）。

文末内部链接（你提供的）对应的更高级训练范式（与本文"无条件、单 UNet 从零微调"形成对比）：

| 内部链接 | 与本文的关系 |
|---|---|
| `../training/overview` | 训练总览页，把本文（基础无条件训练）作为入门案例之一。 |
| `../training/text_inversion` | Textual Inversion：在文本条件扩散模型中学习新 token；与本文"无条件 + UNet2DModel"路径不同，需要文本编码器与 text-conditional UNet。 |
| `../training/dreambooth` | DreamBooth：用少量参考图对整模型做个性化微调，比本文"全量训练"更轻量但需要文本条件。 |
| `../training/text2image` | 文本→图像训练（如 Stable Diffusion），建立在 UNet2DModel + text encoder + VAE 的组合之上。 |
| `../training/lora` | LoRA：用低秩适配器只更新少量参数做微调，可与 DreamBooth、text-to-image 等组合使用，比本文的全参数训练更省资源。 |

---

## 【使用方法】

原文给出的启用/配置命令汇总（**仅原文出现过的**）：

**1. 安装依赖**
```bash
!pip install diffusers[training]
```
原文还隐含要求预先安装 🤗 Datasets、🤗 Accelerate、TensorBoard（可选 Weights & Biases）。

**2. 登录 Hugging Face Hub（推送模型用）**
```py
>>> from huggingface_hub import notebook_login
>>> notebook_login()
```
或终端：
```bash
huggingface-cli login
```

**3. Git-LFS（大文件版本管理）**
```bash
!sudo apt -qq install git-lfs
!git config --global credential.helper store
```

**4. 数据集与预处理**
```py
>>> from datasets import load_dataset
>>> config.dataset_name = "huggan/smithsonian_butterflies_subset"
>>> dataset = load_dataset(config.dataset_name, split="train")
```
预处理（`torchvision.transforms.Compose`）：Resize → RandomHorizontalFlip → ToTensor → Normalize([0.5],[0.5])；通过自定义 `transform` + `dataset.set_transform(transform)` 应用。

**5. 构建 UNet2DModel**（按第 3 节给出的 `block_out_channels` 与 `down_block_types` / `up_block_types` 元组实例化）。

**6. 噪声调度器**
```py
>>> noise_scheduler = DDPMScheduler(num_train_timesteps=1000)
```

**7. 优化器与 LR 调度**
```py
>>> optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
>>> lr_scheduler = get_cosine_schedule_with_warmup(
...     optimizer=optimizer,
...     num_warmup_steps=config.lr_warmup_steps,
...     num_training_steps=(len(train_dataloader) * config.num_epochs),
... )
```

**8. 评估**（每 `save_image_epochs` 个 epoch 调用一次）
```py
>>> pipeline = DDPMPipeline(unet=model, scheduler=noise_scheduler)
>>> images = pipeline(batch_size=config.eval_batch_size, generator=torch.manual_seed(config.seed)).images
```
使用 `make_grid(images, rows=4, cols=4)` 拼图并保存到 `config.output_dir/samples`。

**9. 模型推送**
通过 `TrainingConfig.push_to_hub = True`、`hub_private_repo = False` 配合 `notebook_login()` 实现上传；上传目录即为 `config.output_dir = "ddpm-butterflies-128"`。

> ⚠️ 原文 **未涉及**：完整 `for epoch in range(num_epochs)` 训练循环代码（文档在 `evaluate` 函数尾部被截断，原文未给出损失反传、`.backward()`、`optimizer.step()`、`lr_scheduler.step()`、`pipeline.save_model()`/`push_to_hub` 的具体调用语句）。这些步骤需要参考 Colab 原始 notebook（`training_example.ipynb`）或补全。
