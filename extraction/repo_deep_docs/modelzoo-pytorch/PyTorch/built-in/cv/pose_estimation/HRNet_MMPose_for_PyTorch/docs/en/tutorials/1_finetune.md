# Tutorial 1: Finetuning Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/en/tutorials/1_finetune.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/en/tutorials/1_finetune.md

# 一体化深度解读：HRNet_MMPose_for_PyTorch — Tutorial 1: Finetuning Models

---

## 【定位】

这篇文档指导用户如何将在 COCO 上预训练的 MMPose 姿态估计模型（Model Zoo 中的 HRNet 等）作为"起点"，迁移并微调（finetune）到新的数据集（如 COCO-WholeBody Dataset）上，以获得更好的性能。

---

## 【技术要点】

1. **两阶段流程**：微调分为两步 — 先按照 Tutorial 2: Adding New Dataset 增加对新数据集的支持，再按本教程修改 config（修改四个部分）。
2. **修改输出头（Modify Head）**：仅修改 `keypoint_head` 中的 `out_channels`，由原 COCO 的 17 个关键点改为新数据集的关键点数；本文示例的 COCO-WholeBody 改为 **133 个**。需同步修改 `num_output_channels`、`dataset_joints`、`dataset_channel`、`inference_channel` 四个字段。
3. **修改数据集配置（Modify Dataset）**：将 dataset 类型切换为 `TopDownCocoWholeBodyDataset`；分别指定 train/val/test 的 `ann_file` 与 `img_prefix`；`samples_per_gpu=32`，`workers_per_gpu=2`。
4. **修改训练调度（Modify Training Schedule）**：相比默认 schedule，finetune 需要"更小的学习率、更少的训练轮次"；示例采用 Adam 优化器 `lr=5e-4`，`lr_config` 采用 step 策略 + linear warmup（500 iters，ratio=0.001，step=[170, 200]），`total_epochs=210`。
5. **加载预训练权重（Use Pre-trained Model）**：在 config 中设置 `load_from` 字段为预训练模型的路径或下载链接（URL），可提前下载以避免训练时的下载延迟。
6. **关于 `pretrained` 字段的区分**：模型 config 中的 `pretrained='https://download.openmmlab.com/mmpose/pretrain_models/hrnet_w48-8ef0771d.pth'` 用于**初始化 backbone**（来自 ImageNet 预训练），与本任务的微调无关；真正加载姿态估计预训练权重要使用 `load_from`。

---

## 【关键机制与数据】

- **工作原理**：以 MMPose 的 config 继承机制为基础，复制一份基线 config 后，仅覆盖差异字段。整体可视为"**模型头按新数据集关键点数改造 + 数据集类与标注路径替换 + 训练调度收紧 + 加载 COCO 预训练姿态估计权重**"四件套。
- **数据流**（原文体现）：
  1. backbone 使用 HRNet-W48（4 个 stage，多分支结构，输入 in_channels=3）。
  2. `keypoint_head` 为 `TopdownHeatmapSimpleHead`，`in_channels=48`，输出通道数为 `channel_cfg['num_output_channels']`（原文示例 133）。
  3. 训练样本经 `train_pipeline`，验证/测试经 `val_pipeline` / `test_pipeline`，最终在 `test_cfg` 中以 `flip_test=True, post_process='unbiased', shift_heatmap=True, modulate_kernel=17` 进行推理后处理。
- **原文未提供**：未给出性能数据（如 AP、mAP 等指标），未给出 batch size 的硬件依赖说明，未给出 train_pipeline / val_pipeline / data_cfg 内部细节；这些均未在本文档中出现。

---

## 【表格解读】

**原文无表格。**

本文档仅以 Python config 代码块形式给出配置示例，未包含任何 markdown 表格或对比表。

---

## 【公式解读】

**原文无公式。**

本文档全部为配置文件（dict）形式与自然语言说明，未出现任何数学公式或 LaTeX 表达式。

---

## 【关联】

- **上游/前置教程**：文档开篇与"Outline"小节均显式引用 [Tutorial 2: Adding New Dataset](tutorials/../2_new_dataset.md)（内部链接 `tutorials/../2_new_dataset.md`），声明"增加对新数据集的支持"是微调的前置步骤，本教程负责后续的 config 修改。
- **外部资源依赖**：
  - [Model Zoo](https://mmpose.readthedocs.io/en/0.x/modelzoo.html) — 提供可供下载与对比的预训练模型库，本教程中的 `load_from` URL 指向其中。
  - ImageNet 预训练 backbone `hrnet_w48-8ef0771d.pth`（OpenMMLab mmpose pretrain_models）— 用于 backbone 初始化。
  - COCO 全身体姿态估计预训练 `hrnet_w48_coco_384x288_dark-741844ba_20200812.pth` — 用于本次微调任务的 `load_from`。
- **下游/配套**：与 MMPose 中其他数据集适配器（如 COCO、MPII-TRB 等"10+"种 dataset wrapper）形成横向选择；与 `TopdownHeatmapSimpleHead`、`JointsMSELoss(use_target_weight=True)` 等模块构成微调目标的实际计算路径。

---

## 【使用方法】

启用方式与配置项（均来自原文）：

1. **新增数据集支持**：先按 Tutorial 2: Adding New Dataset 增加新数据集。
2. **修改 `channel_cfg`**：将 `num_output_channels`、`dataset_joints`、`dataset_channel`、`inference_channel` 由 `17` 改为新数据集关键点数（示例 133）。
3. **修改 `model.keypoint_head`**：仅将 `out_channels=channel_cfg['num_output_channels']` 同步；其余 backbone / head 结构基本沿用 HRNet-W48 + `TopdownHeatmapSimpleHead`。
4. **修改 `data` 字典**：将 `train/val/test` 三段的 `type` 改为新数据集类（如 `TopDownCocoWholeBodyDataset`），并填入对应 `ann_file` 与 `img_prefix`；`samples_per_gpu=32`，`workers_per_gpu=2`，val/test dataloader `samples_per_gpu=32`。
5. **修改训练调度**：
   ```python
   optimizer = dict(type='Adam', lr=5e-4)
   optimizer_config = dict(grad_clip=None)
   lr_config = dict(policy='step', warmup='linear',
                    warmup_iters=500, warmup_ratio=0.001,
                    step=[170, 200])
   total_epochs = 210
   ```
6. **设置 `load_from`**：将其指向 Model Zoo 中目标预训练模型（URL 或本地路径），建议训练前预先下载。
7. **启动训练**：原文未涉及具体启动命令（如 `python tools/train.py ...`），故启动方式"原文未涉及"。
