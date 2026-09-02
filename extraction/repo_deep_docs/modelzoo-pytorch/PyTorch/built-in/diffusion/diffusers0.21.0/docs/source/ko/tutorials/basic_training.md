# Diffusion 모델을 학습하기

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/diffusion/diffusers0.21.0/docs/source/ko/tutorials/basic_training.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/diffusion/diffusers0.21.0/docs/source/ko/tutorials/basic_training.md

# 一体化深度解读:Diffusers「Basic Training」教程

---

## 【定位】

这篇文档是 🤗 Diffusers 库的**入门级训练教程**,指导用户基于 `UNet2DModel` 与 `DDPMScheduler` 在 [Smithsonian Butterflies](https://huggingface.co/datasets/huggan/smithsonian_butterflies_subset) 数据子集上从零训练一个**无条件图像生成 (unconditional image generation)** 的扩散模型,并串联了配置、数据、模型、调度器、优化器、评估流水线的完整最小闭环。

---

## 【技术要点】

1. **统一配置 dataclass `TrainingConfig`**:`image_size=128`、`train_batch_size=16`、`eval_batch_size=16`、`num_epochs=50`、`gradient_accumulation_steps=1`、`learning_rate=1e-4`、`lr_warmup_steps=500`、`save_image_epochs=10`、`save_model_epochs=30`、`mixed_precision="fp16"`(原文:"`no`는 float32, 자동 혼합 정밀도를 위한 `fp16`"),`output_dir="ddpm-butterflies-128"`,并支持 `push_to_hub=True`、`hub_private_repo=False`、`overwrite_output_dir=True`。

2. **数据预处理流水线**:`Resize((128,128)) → RandomHorizontalFlip → ToTensor → Normalize([0.5],[0.5])` 把像素值映射到 `[-1, 1]`(原文:"모델이 예상하는 [-1, 1] 범위로 픽셀 값을 재조정 하는데 중요합니다");使用 `dataset.set_transform(transform)` 把 transform 绑定到训练时取样,并通过 `torch.utils.data.DataLoader` 启用 `shuffle=True`。

3. **`UNet2DModel` 结构参数**:`in_channels=3`、`out_channels=3`、`layers_per_block=2`、`block_out_channels=(128, 128, 256, 256, 512, 512)`,下采样由 5 个 `DownBlock2D` + 1 个 `AttnDownBlock2D`(含 spatial self-attention)组成,上采样对称由 `UpBlock2D` 与 `AttnUpBlock2D` 组成;输入/输出 shape 一致为 `torch.Size([1, 3, 128, 128])`。

4. **噪声调度 `DDPMScheduler`**:`num_train_timesteps=1000`,使用 `add_noise(sample_image, noise, timesteps)` 给图像加噪,`timesteps=torch.LongTensor([50])` 作为示例时间步;训练目标是**预测噪声**,损失为 `loss = F.mse_loss(noise_pred, noise)`。

5. **优化器与学习率调度**:`optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)`;`lr_scheduler = get_cosine_schedule_with_warmup(optimizer, num_warmup_steps=500, num_training_steps=len(train_dataloader)*num_epochs)`。

6. **评估与产物**:`DDPMPipeline` 从随机噪声反推图像,`make_grid` 拼成 4×4 网格,每 `save_image_epochs=10` 个 epoch 保存样本网格,每 `save_model_epochs=30` 个 epoch 保存模型 checkpoint,并可选 `push_to_hub=True` 上传 Hugging Face Hub。

---

## 【关键机制与数据】

- **工作原理**:训练阶段,scheduler 在 `num_train_timesteps=1000` 上随机采样时间步,对真实图像 `x_0` 加噪得到 `x_t`;UNet 以 `(x_t, t)` 为输入预测噪声 `ε_θ(x_t, t)`,损失为预测噪声与真实高斯噪声的 MSE。
- **数据流**:`Smithsonian Butterflies (HugGan)` → `load_dataset(split="train")` → `preprocess` (含 `convert("RGB")`) → `set_transform` → `DataLoader(shuffle=True)` → `(noisy_image, timesteps)` 输入 `model` → `mse_loss(noise_pred, noise)` → `AdamW` + cosine warmup → 反向传播。
- **推理/评估原理**(原文):"추론시에, 스케줄러는 노이즈로부터 이미지를 생성합니다. 학습시 스케줄러는 diffusion 과정에서의 특정 포인트로부터 모델의 출력 또는 샘플을 가져와 *노이즈 스케줄* 과 *업데이트 규칙*에 따라 이미지에 노이즈를 적용합니다." —— 训练与推理共用 scheduler 但角色相反:训练用 `add_noise`,评估用 `DDPMPipeline` 反向去噪,`generator=torch.manual_seed(config.seed)` 保证可复现。
- **样本输入输出 shape**(原文):`Input shape: torch.Size([1, 3, 128, 128])` / `Output shape: torch.Size([1, 3, 128, 128])`。
- **性能数据**:原文未提供训练耗时、GPU 利用率、收敛曲线等性能指标(原文文档在此处被截断,训练循环主体 `evaluate` / `train_loop` 后半段未给出,故无法引用具体性能数字)。

---

## 【表格解读】

**原文无表格。** 全部结构化参数均以 `@dataclass` 形式(`TrainingConfig`)和 `UNet2DModel(...)` 构造参数的形式呈现,而非 markdown 表格。

---

## 【公式解读】

原文未使用 LaTeX 数学公式,但给出了一段**噪声预测损失**的伪代码式定义(原文逐字保留):

```
noise_pred = model(noisy_image, timesteps).sample
loss = F.mse_loss(noise_pred, noise)
```

符号含义:

| 符号 | 含义 |
|---|---|
| `noisy_image` | 由 `noise_scheduler.add_noise(sample_image, noise, timesteps)` 产生的加噪图像(在时刻 `t`) |
| `timesteps` | 采样的扩散时间步(`torch.LongTensor([50])` 为示例),决定噪声强度 |
| `model(...)` | `UNet2DModel`,接受 `(noisy_image, t)` 作为输入 |
| `.sample` | UNet 输出的 `UNet2DOutput` 中代表预测噪声的张量 |
| `noise` | 与 `sample_image` 同形状的标准高斯噪声 `torch.randn(sample_image.shape)` |
| `F.mse_loss` | PyTorch 均方误差损失函数 |
| `loss` | 标量损失,优化目标即最小化该 MSE |

作用:让 UNet 学会由 `(x_t, t)` 反推加入图像中的真实噪声 `ε`,这是 DDPM 系列模型最常用的 ε-prediction 参数化形式。

---

## 【关联】

**内部链接(文末列出的相关教程)**:

- `../training/overview` —— 训练功能总览,本教程是其基础入门篇。
- `../training/text_inversion` —— Textual Inversion,通过学习新文本嵌入来个性化文本到图像模型;与本教程相反,不需要重训 UNet 全量参数。
- `../training/dreambooth` —— DreamBooth,使用少量参考图像微调扩散模型来学习特定主体/风格;本教程提供的数据加载与训练循环可作为其底座。
- `../training/text2image` —— Stable Diffusion 等条件扩散模型的文本到图像训练,引入了文本编码器与 Cross-Attention,与本教程的纯 UNet + scheduler 路线形成扩展。
- `../training/lora` —— LoRA,只训练低秩适配器参数,显著降低显存;与本教程的全参数 AdamW 微调形成对比。

**外部上下游组件**(原文提及):

- 上游数据:`huggan/smithsonian_butterflies_subset`、HugGan Community Event、社区/自建 `ImageFolder`。
- 配套工具:`🤗 Datasets`(含 `Image`、`set_transform`)、`🤗 Accelerate`(多 GPU 简化,原文:"다수 GPU에서 학습을 간소화하기 위해")、`TensorBoard`、`Weights & Biases`。
- 模型组件:`UNet2DModel`、`DDPMScheduler`、`DDPMPipeline`、`diffusers.optimization.get_cosine_schedule_with_warmup`。
- 模型分享:`huggingface-cli login` / `notebook_login()` + `git-lfs` → `push_to_hub`。

---

## 【使用方法】

1. **环境安装**(原文):
   ```bash
   !pip install diffusers[training]
   ```
   并确认 🤗 Datasets、🤗 Accelerate、TensorBoard 已安装(原文:"🤗 Datasets을 불러오고 전처리하기 위해 … 다수 GPU에서 학습을 간소화하기 위해 🤗 Accelerate … 학습 메트릭을 시각화하기 위해 TensorBoard").

2. **登录 Hub 以便上传**(原文,二选一):
   ```py
   >>> from huggingface_hub import notebook_login
   >>> notebook_login()
   ```
   或终端:
   ```bash
   huggingface-cli login
   ```

3. **大文件支持**(原文):
   ```bash
   !sudo apt -qq install git-lfs
   !git config --global credential.helper store
   ```

4. **配置训练参数**:实例化 `TrainingConfig()`,可调 `image_size / train_batch_size / num_epochs / learning_rate / lr_warmup_steps / mixed_precision / output_dir / push_to_hub`。

5. **加载与预处理数据**:
   ```py
   config.dataset_name = "huggan/smithsonian_butterflies_subset"
   dataset = load_dataset(config.dataset_name, split="train")
   ```
   再以 `torchvision.transforms.Compose([Resize, RandomHorizontalFlip, ToTensor, Normalize([0.5],[0.5])])` 包装成 `preprocess`,通过 `dataset.set_transform(transform)` 绑定,并构造 `DataLoader(dataset, batch_size=config.train_batch_size, shuffle=True)`。

6. **构建模型**(原文示例):
   ```py
   model = UNet2DModel(
       sample_size=config.image_size,
       in_channels=3, out_channels=3,
       layers_per_block=2,
       block_out_channels=(128, 128, 256, 256, 512, 512),
       down_block_types=("DownBlock2D","DownBlock2D","DownBlock2D","DownBlock2D","AttnDownBlock2D","DownBlock2D"),
       up_block_types=("UpBlock2D","AttnUpBlock2D","UpBlock2D","UpBlock2D","UpBlock2D","UpBlock2D"),
   )
   ```

7. **构造噪声调度器**(原文):
   ```py
   noise_scheduler = DDPMScheduler(num_train_timesteps=1000)
   ```

8. **构建优化器与 LR 调度**(原文):
   ```py
   optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
   lr_scheduler = get_cosine_schedule_with_warmup(
       optimizer=optimizer,
       num_warmup_steps=config.lr_warmup_steps,
       num_training_steps=(len(train_dataloader) * config.num_epochs),
   )
   ```

9. **配置评估函数**(原文给出片段 `evaluate(config, epoch, pipeline)`,使用 `DDPMPipeline(batch_size=config.eval_batch_size, generator=torch.manual_seed(config.seed))` 反向生成 16 张样本并通过 `make_grid(..., rows=4, cols=4)` 拼图后写入 `output_dir/samples`)。

> **说明**:原文在 `evaluate` 函数体内 `os.makedirs(test_dir, exist_ok=True)` 处截断,**主训练循环(`train_loop`)、accelerate 包装、模型 `save_model` / `push_to_hub` 调用、混合精度 `accelerator.autocast` 段落未在提供的原文中给出**,因此训练主循环的具体写法此处标注为"原文未涉及(原文于 evaluate 中途截断)"。
