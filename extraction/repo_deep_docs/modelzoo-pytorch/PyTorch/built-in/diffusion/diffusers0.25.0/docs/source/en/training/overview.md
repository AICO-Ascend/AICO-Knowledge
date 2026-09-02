# Overview

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/diffusion/diffusers0.25.0/docs/source/en/training/overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/diffusion/diffusers0.25.0/docs/source/en/training/overview.md

# 一体化深度解读:🤗 Diffusers 训练脚本总览

## 【定位】

本篇文档是 🤗 Diffusers 库**训练脚本( training scripts )的入口总览页**,回答"库内置了哪些扩散模型训练示例、各自支持哪些能力( SDXL / LoRA / Flax )、如何安装运行"这三个问题,为后续每一类具体训练任务(unconditional / text-to-image / DreamBooth / ControlNet 等)的单独文档提供索引与统一的安装前置说明。

## 【技术要点】

1. **训练脚本设计四原则**(原文标注于列表):① **Self-contained**——不依赖本地文件,所有依赖从 `requirements.txt` 安装;② **Easy-to-tweak**——数据预处理与训练循环完全暴露,允许用户按场景修改;③ **Beginner-friendly**——为可读性牺牲部分 SOTA 性能,过于复杂的方法被刻意略去;④ **Single-purpose**——一个脚本只做一件事,保持可读。
2. **训练脚本集合**(原文表格共 10 项):unconditional image generation、text-to-image、textual inversion、DreamBooth、ControlNet、InstructPix2Pix、Custom Diffusion、T2I-Adapters、Kandinsky 2.2、Wuerstchen;其中 text-to-image、DreamBooth、textual inversion、ControlNet、InstructPix2Pix、T2I-Adapters **支持 SDXL**,text-to-image、DreamBooth、textual inversion、Kandinsky 2.2、Wuerstchen **支持 LoRA**,text-to-image、textual inversion、DreamBooth、ControlNet **支持 Flax**。
3. **安装方式**(原文 bash 块):从源码安装主库 → `git clone https://github.com/huggingface/diffusers` → `cd diffusers` → `pip install .`;进入具体脚本目录后再 `pip install -r requirements.txt`,SDXL 变体使用 `requirements_sdxl.txt`。
4. **训练加速推荐**(原文末两条 bullet):① 使用 **PyTorch 2.0 或更高版本**,可在训练中自动启用 [scaled dot product attention](../optimization/torch2.0#scaled-dot-product-attention) 而**无需修改训练代码**;② 安装 [xFormers](../optimization/xformers) 启用 memory-efficient attention。
5. **示例维护承诺**(原文):所有示例处于**活跃维护(active)**状态,如行为异常欢迎提 issue;新增训练示例需满足四原则方可加入。

## 【关键机制与数据】

- **数据流/工作原理(原文):** 文档本身不展开单条训练流水线,而是把"数据预处理代码 + 训练循环"作为可改写入口暴露给用户——这意味着用户面对的不是"黑盒训练器",而是可直接 fork 的参考实现。原文:"we've fully exposed the data preprocessing code and the training loop so you can modify it for your own use."
- **性能数据(原文):** 文档**未给出**具体的训练时长、显存占用、batch size、步数等数值,仅在优化层面提供两条**定性建议**(PyTorch 2.0 的 SDPA 与 xFormers 的 memory-efficient attention),具体收益需跳转至各自优化章节。
- **机制联动(原文):** 加速项为"训练代码无侵入"——PyTorch 2.0 的 scaled dot product attention 在新版 SDPA backend 命中时自动启用,无需 `attn_implementation` 之类的额外开关;xFormers 则需要先 `pip install xformers`,Diffusers 会按既有注意力后端调度逻辑使用之。

## 【表格解读】

原文唯一表格为"训练脚本支持矩阵",**逐字还原**如下:

| Training | SDXL-support | LoRA-support | Flax-support |
|---|---|---|---|
| [unconditional image generation](https://github.com/huggingface/diffusers/tree/main/examples/unconditional_image_generation) |  |  |  |
| [text-to-image](https://github.com/huggingface/diffusers/tree/main/examples/text_to_image) | 👍 | 👍 | 👍 |
| [textual inversion](https://github.com/huggingface/diffusers/tree/main/examples/textual_inversion) |  |  | 👍 |
| [DreamBooth](https://github.com/huggingface/diffusers/tree/main/examples/dreambooth) | 👍 | 👍 | 👍 |
| [ControlNet](https://github.com/huggingface/diffusers/tree/main/examples/controlnet) | 👍 |  | 👍 |
| [InstructPix2Pix](https://github.com/huggingface/diffusers/tree/main/examples/instruct_pix2pix) | 👍 |  |  |
| [Custom Diffusion](https://github.com/huggingface/diffusers/tree/main/examples/custom_diffusion) |  |  |  |
| [T2I-Adapters](https://github.com/huggingface/diffusers/tree/main/examples/t2i_adapter) | 👍 |  |  |
| [Kandinsky 2.2](https://github.com/huggingface/diffusers/tree/main/examples/kandinsky2_2/text_to_image) |  | 👍 |  |
| [Wuerstchen](https://github.com/huggingface/diffusers/tree/main/examples/wuerstchen/text_to_image) |  | 👍 |  |

逐行解读(横轴维度对比):
- **unconditional image generation**:三列均为空,即仅支持 PyTorch + 原始 UNet,**不支持** SDXL、LoRA、Flax。
- **text-to-image**:**唯一三项全勾(👍👍👍)**的脚本,SDXL + LoRA + Flax 均支持,定位为"全特性覆盖的旗舰训练示例"。
- **textual inversion**:仅 **Flax**(👍),不支持 SDXL/LoRA——与"textual inversion 学习的是 embedding 概念,参数体量小,通常无需 SDXL/LoRA 路线"的常见实践一致。
- **DreamBooth**:三项全勾,与 text-to-image 并列;SDXL 路径通常配合 LoRA 以控制大模型微调成本。
- **ControlNet**:仅 **SDXL + Flax**(👍👍),不支持 LoRA——因为 ControlNet 训练的是独立的 control 分支,参数相对独立,与 LoRA 的"低秩适配"定位重叠较少。
- **InstructPix2Pix**:仅 **SDXL**(👍),不支持 LoRA 与 Flax。
- **Custom Diffusion**:三列均空,沿用基础 PyTorch 路径。
- **T2I-Adapters**:仅 **SDXL**(👍),与 ControlNet 类似但更轻量,无 LoRA/Flax 支持。
- **Kandinsky 2.2**:仅 **LoRA**(👍),结合其原生潜在表征 + adapter 结构,不直接走 SDXL 路线。
- **Wuerstchen**:仅 **LoRA**(👍),同 Kandinsky,作为新型 cascaded 架构示例不与 SDXL/Flax 重叠。

整体规律(由表格纵向比较得出):**"三项全勾"集中于 text-to-image 与 DreamBooth 两条主线**;**LoRA 列**覆盖了"主流文生图 + Kandinsky + Wuerstchen"等需要控制参数量的训练;**Flax 列**覆盖了偏研究向的脚本(text-to-image / textual inversion / DreamBooth / ControlNet);**SDXL 列**则横跨文生图、个性化(DreamBooth)、指令编辑(InstructPix2Pix)、条件控制(ControlNet/T2I-Adapters)。

## 【公式解读】

原文无公式(无 LaTeX 或伪代码形式数学表达)。

## 【关联】

- **上游依赖(优化层)**:末尾两条加速建议直接指向本仓的优化专题页——[scaled dot product attention](../optimization/torch2.0#scaled-dot-product-attention)(PyTorch 2.0 原生 SDPA)与 [xFormers](../optimization/xformers)(第三方 memory-efficient attention)。这两个优化项是"所有训练脚本"共享的性能底座,无需按脚本单独配置。
- **横向——同类训练专题**:表格中每一行都链向 `examples/<task>/` 子仓库下的独立 README,本概览页是其**目录索引**而非教程本身。
- **下游——各 task README**:unconditional_image_generation、text_to_image、textual_inversion、dreambooth、controlnet、instruct_pix2pix、custom_diffusion、t2i_adapter、kandinsky2_2/text_to_image、wuerstchen/text_to_image 各自由独立训练指南展开。
- **仓库级入口**:开篇链接 `diffusers/examples` 是整个训练示例集合的根目录。
- **未在文末出现的内部链接**(本任务给出的链接清单仅含上述两条优化页);其余链接均为 GitHub 仓库外部或 Colab 跳转。

## 【使用方法】

原文给出三类启用手段,均无脚本内"开关/配置项",而是环境与依赖层面的命令:

1. **从源码安装主库(原文 bash):**
   ```bash
   git clone https://github.com/huggingface/diffusers
   cd diffusers
   pip install .
   ```
   建议在**新的虚拟环境**中执行(原文:"in a new virtual environment")。
2. **安装具体训练脚本依赖(原文 bash):**
   ```bash
   cd examples/dreambooth     # 进入目标脚本目录
   pip install -r requirements.txt
   # SDXL 变体使用专属 requirements
   pip install -r requirements_sdxl.txt
   ```
   原文提示:"Some training scripts have a specific requirement file for SDXL, LoRA or Flax. If you're using one of these scripts, make sure you install its corresponding requirements file."
3. **训练加速(原文两条 bullet):**
   - 升级到 **PyTorch 2.0+**,自动启用 [scaled dot product attention](../optimization/torch2.0#scaled-dot-product-attention),**无需改训练代码**。
   - 安装 [xFormers](../optimization/xformers) 以启用 memory-efficient attention。
4. **具体训练参数/命令行调用方式(原文未涉及):** 本概览页**不列出**各脚本的命令行参数(如 `--train_batch_size`、`--learning_rate`、`--num_train_epochs` 等),需跳转至各 task 的独立 README 查看。
