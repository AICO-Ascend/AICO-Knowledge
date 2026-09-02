# Train a diffusion model

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/diffusion/diffusers0.25.0/docs/source/en/tutorials/basic_training.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/diffusion/diffusers0.25.0/docs/source/en/tutorials/basic_training.md

# 一体化深度解读:Diffusers 基础训练教程 (basic_training.md)

## 【定位】

本教程演示了**在 🧨 Diffusers 框架下,从零开始训练一个无条件图像生成扩散模型 (UNet2DModel) 的完整流程**,采用 Smithsonian Butterflies 子集数据集,产出可推送至 Hugging Face Hub 的蝴蝶图像生成模型。

---

## 【技术要点】

1. **模型架构选择**:使用 [`UNet2DModel`] 类从零构建,无任何预训练权重依赖,属"无条件"扩散模型 (unconditional image generation)。
2. **UNet 拓扑**:6 层 down/up block 通道为 `(128, 128, 256, 256, 512, 512)`,每个 block 内 `layers_per_block=2` 层 ResNet;仅在倒数第二个 down block (`AttnDownBlock2D`) 与对应 up block (`AttnUpBlock2D`) 引入 spatial self-attention。
3. **噪声调度器**:`DDPMScheduler`,`num_train_timesteps=1000`,通过 `add_noise` 方法按 noise schedule 向图像施加噪声。
4. **训练超参 (TrainingConfig dataclass)**:`image_size=128`, `train_batch_size=16`, `eval_batch_size=16`, `num_epochs=50`, `gradient_accumulation_steps=1`, `learning_rate=1e-4`, `lr_warmup_steps=500`, `save_image_epochs=10`, `save_model_epochs=30`, `mixed_precision="fp16"`, `output_dir="ddpm-butterflies-128"`。
5. **数据预处理流水线 (`torchvision.transforms.Compose`)**:Resize → RandomHorizontalFlip → ToTensor → Normalize([0.5], [0.5]) (将像素归一化到 `[-1, 1]`,与模型期望匹配)。
6. **Hub 推送**:`push_to_hub=True` 时,需先 `notebook_login()` 或 `huggingface-cli login`,并用 Git-LFS 承载大文件 checkpoint。

---

## 【关键机制与数据】

**工作原理 (原文视角)**:

- 训练采用前向加噪 + 噪声预测范式:`noise_scheduler.add_noise(...)` 把真实图像 `sample_image` 与随机噪声 `torch.randn(sample_image.shape)` 按 timestep 混合;`UNet2DModel` 学习预测噪声 (后续代码虽被截断,但上下文已明示)。
- 数据流:`datasets.load_dataset("huggan/smithsonian_butterflies_subset")` → `set_transform(transform)` 触发懒加载预处理 → `torch.utils.data.DataLoader` 按 `batch_size=16`、shuffle 输出 batch → 模型前向 → scheduler 反向。
- 形状对齐验证:输入 `torch.Size([1, 3, 128, 128])` → 输出 `torch.Size([1, 3, 128, 128])` (下/上采样保持分辨率,因为模型仅在需要处下采样)。
- 混合精度:`mixed_precision="fp16"` (可改 `"no"` 走 float32) 以加速训练。
- 视觉化:用 `matplotlib.pyplot.subplots(1, 4, figsize=(16, 4))` 展示前 4 张图。

**性能/规模数据 (原文给出的数字)**:
- 图像分辨率:128 × 128
- UNet 通道阶梯:128 → 128 → 256 → 256 → 512 → 512
- 训练 epoch:50;评估 batch 16
- 优化器 warmup:500步
- Diffusion 时间步:1000

(原文未提供训练时长/吞吐/FLOPS 等性能数字。)

---

## 【表格解读】

**原文无表格**。

(教程以代码块 + 配置 dataclass 形式承载超参,未使用表格呈现。)

---

## 【公式解读】

**原文无公式**。

(扩散过程的数学描述 (前向加噪 $x_t = \sqrt{\bar\alpha_t}x_0 + \sqrt{1-\bar\alpha_t}\epsilon$ 等) 在本教程片段中未显式列出;它仅通过 `add_noise` 方法抽象呈现。)

---

## 【关联】

本教程位于 `PyTorch/built-in/diffusion/diffusers0.25.0/docs/source/en/tutorials/`,定位为入门级 (Tutorial) 文档,与以下训练范式上下游链接:

| 关联文档 | 关系定位 |
|---|---|
| `../training/overview` | 训练范式总览,本教程为其中最简单路径 (无条件、UNet2DModel、从零训练) 的具体落地 |
| `../training/text_inversion` | 进阶:文本反演,需结合 text encoder (与本教程纯 UNet2D 不同) |
| `../training/dreambooth` | 进阶:个性化主题微调,与本教程共享 UNet 训练骨架,但引入交叉注意力条件 |
| `../training/text2image` | 进阶:文本→图像,与本教程共享基础训练循环,但叠加 CLIP text conditioning |
| `../training/lora` | 进阶:参数高效微调,可与本教程训练循环结合,降低显存/算力开销 |

简言之,本教程是**最底层、无条件、单 UNet** 的训练范式基线;其余四个链接文档均是"在其训练循环上引入条件信号或高效参数化"的延伸。

---

## 【使用方法】

**原文给出的启用/配置方式**:

1. **依赖安装**:
   ```bash
   #!pip install diffusers[training]
   ```
   (同时需要 🤗 Datasets 加载数据集、🤗 Accelerate 简化多卡、TensorBoard 或 Weights & Biases 可视化。)

2. **Hub 登录 (二选一)**:
   ```py
   from huggingface_hub import notebook_login
   notebook_login()
   ```
   或终端:
   ```bash
   huggingface-cli login
   ```

3. **Git-LFS (承载大 checkpoint)**:
   ```bash
   sudo apt -qq install git-lfs
   git config --global credential.helper store
   ```

4. **训练配置 (dataclass 实例化)**:
   ```py
   config = TrainingConfig()  # 详见前文 TrainingConfig 字段
   ```

5. **数据集加载**:
   ```py
   from datasets import load_dataset
   config.dataset_name = "huggan/smithsonian_butterflies_subset"
   dataset = load_dataset(config.dataset_name, split="train")
   ```
   也可换为本地 `imagefolder` 或其他 Hub 数据集 (来自 HugGan Community Event)。

6. **模型创建**:
   ```py
   from diffusers import UNet2DModel
   model = UNet2DModel(sample_size=128, in_channels=3, out_channels=3, layers_per_block=2, block_out_channels=(128,128,256,256,512,512), down_block_types=(...), up_block_types=(...))
   ```

7. **调度器创建 (原文片段)**:
   ```py
   from diffusers import DDPMScheduler
   noise_scheduler = DDPMScheduler(num_train_timesteps=1000)
   noise = torch.randn(sample_image.shape)
   timesteps = ...   # (原文此行被截断)
   ```

> **备注**:原文片段止于 `timesteps =` 一行,optimizer、训练循环、评估/采样图像保存 (`save_image_epochs=10`)、模型保存 (`save_model_epochs=30`) 及 `push_to_hub` 的具体实现代码未在所提供文本中呈现,故"原文未涉及"其后续命令细节。
