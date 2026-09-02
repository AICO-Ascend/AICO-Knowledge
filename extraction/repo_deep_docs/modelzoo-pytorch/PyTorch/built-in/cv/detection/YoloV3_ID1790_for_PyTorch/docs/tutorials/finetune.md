# Tutorial 7: Finetuning Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/YoloV3_ID1790_for_PyTorch/docs/tutorials/finetune.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/YoloV3_ID1790_for_PyTorch/docs/tutorials/finetune.md

# Tutorial 7: Finetuning Models —— 一体化深度解读

---

## 【定位】

本教程是 MMDetection 文档体系中专门讲解"如何将 Model Zoo 中在 COCO 上预训练的检测模型，迁移/微调到其他数据集（如 Cityscapes、KITTI）以获得更好性能"的官方指南，回答了"换数据集后该如何修改配置"这一具体工程问题。

---

## 【技术要点】

1. **两阶段迁移流程**：原文明确指出"two steps to finetune a model on a new dataset"——第一步按 [Tutorial 2: Customize Datasets](customize_dataset.md) 增加新数据集支持，第二步修改配置（本文重点）。
2. **配置继承机制 (config inheritance)**：MMDetection V2.0 支持从多个已有配置继承，新配置只需 `_base_` 列表即可复用 `mask_rcnn_r50_fpn.py` 模型骨架、`cityscapes_instance.py` 数据集、`default_runtime.py` 运行时设置。
3. **Head 修改的核心技巧**：仅需将 `roi_head.bbox_head.num_classes` 和 `roi_head.mask_head.num_classes` 改为新数据集类别数（Cityscapes 示例 = **8**），其余权重（含预训练 backbone/FPN）几乎都可复用，仅末层预测头被重置。
4. **细粒度 Head 参数（Cityscapes Mask R-CNN 示例）**：
   - BBox Head：`Shared2FCBBoxHead`，`in_channels=256`，`fc_out_channels=1024`，`roi_feat_size=7`，`num_classes=8`
   - BBox Coder：`DeltaXYWHBBoxCoder`，`target_means=[0., 0., 0., 0.]`，`target_stds=[0.1, 0.1, 0.2, 0.2]`，`reg_class_agnostic=False`
   - 损失：`CrossEntropyLoss(use_sigmoid=False, loss_weight=1.0)` + `SmoothL1Loss(beta=1.0, loss_weight=1.0)`
   - Mask Head：`FCNMaskHead`，`num_convs=4`，`in_channels=256`，`conv_out_channels=256`，`num_classes=8`，`loss_mask=CrossEntropyLoss(use_mask=True, loss_weight=1.0)`
5. **微调专属训练超参**（区别于默认 schedule）：使用更小的学习率和更少的训练轮次——SGD `lr=0.01`、`momentum=0.9`、`weight_decay=0.0001`（原文注明"lr is set for a batch size of 8"）；lr 策略为 `step`，配合 `warmup='linear'`、`warmup_iters=500`、`warmup_ratio=0.001`、阶梯节点 `step=[7]`；`total_epochs = 8`，并标注"actual epoch = 8 * 8 = 64"；日志间隔 `log_config.interval=100`。
6. **加载预训练权重**：通过 `load_from` 指定 URL 路径，原文使用 `mask_rcnn_r50_fpn_2x_20181010-41d35c05.pth`（2x schedule 的 Mask R-CNN R50-FPN 权重），并建议训练前手动下载以避免训练中断。

---

## 【关键机制与数据】

- **工作原理（原文表述）**：
  - 原文："Detectors pre-trained on the COCO dataset can serve as a good pre-trained model for other datasets, e.g., CityScapes and KITTI Dataset."——这是迁移学习的动机基础。
  - 原文："By only changing `num_classes` in the roi_head, the weights of the pre-trained models are mostly reused except the final prediction head."——即仅替换最终分类/分割头，其余 backbone/FPN/RoI 特征层沿用 COCO 预训练权重。
  - 原文："The finetuning hyperparameters vary from the default schedule. It usually requires smaller learning rate and less training epochs"——微调须用比默认更小学习率与更短 schedule，避免破坏预训练特征。
  - 原文："The users might need to download the model weights before training to avoid the download time during training."——网络权重文件应预下载，避免训练开始后被下载阻塞。
- **数据流**：模型 backbone/FPN 由 COCO 预训练权重初始化 → 加载到继承自 `_base_/models/mask_rcnn_r50_fpn.py` 的 Mask R-CNN 结构 → 通过 `load_from` URL 拉取完整 checkpoint → 仅 `num_classes` 维度不一致的末层被新数据集类别数（Cityscapes=8）替换重训 → 用 `_base_/datasets/cityscapes_instance.py` 提供的 Cityscapes 数据管线训练 → 8×8=64 epoch（按 batch size 8 标定学习率）后得到微调模型。
- **性能数据**：原文未给出在 Cityscapes 上的具体 mAP/IoU 等性能数字，仅以注释形式提及 "[7] yields higher performance than [6]"（说明 `step=[7]` 比 `step=[6]` 性能更好，但未引用具体数值）。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式（LaTeX 或标准数学形式）。

> 附带说明：原文中以代码注释形式出现过一条算术关系 `actual epoch = 8 * 8 = 64`，可视为配置中的训练轮数换算说明（即 `total_epochs` 字段值 8 与实际总 epoch 64 之间的 8 倍换算关系，原文未明示乘数 8 的具体含义，按 MMDetection 惯例通常与多卡训练下的 epoch 缩放有关），但它并非正式数学公式，故不列入公式节。

---

## 【关联】

- **上游 / 前置教程**：[Tutorial 2: Customize Datasets](customize_dataset.md)——本教程第一步明确要求用户先按该教程添加新数据集支持，是"加载新数据集 → 修改配置 → 微调"链路上的前置环节。
- **上游 / 资源池**：[Model Zoo](../model_zoo.md)——本教程的预训练权重均来源于 Model Zoo，文中使用的 `mask_rcnn_r50_fpn_2x_20181010-41d35c05.pth` 即为 Model Zoo 中的 2x schedule 权重条目，Model Zoo 提供"用什么权重可微调"的候选清单。
- **横向关系**：本教程与 Model Zoo 形成"选模型 → 准备数据集 → 微调配置"的闭环：Model Zoo 提供权重，customize_dataset 提供数据接入，本教程提供配置改写范式。
- **可继承的 `_base_` 配置**：`_base_/models/mask_rcnn_r50_fpn.py`、`_base_/datasets/cityscapes_instance.py`、`_base_/default_runtime.py` 均为相对路径，指向 MMDetection 的 `configs/` 目录中的基础配置模块，构成本教程可复用的"积木式"配置体系。

---

## 【使用方法】

1. **新增数据集支持**：先按 [Tutorial 2: Customize Datasets](customize_dataset.md) 增加目标数据集的 dataset wrapper 与 class 定义。
2. **新建配置 Python 文件**，使用 `_base_` 列表继承骨架：

   ```python
   _base_ = [
       '../_base_/models/mask_rcnn_r50_fpn.py',
       '../_base_/datasets/cityscapes_instance.py',
       '../_base_/default_runtime.py'
   ]
   ```

3. **修改 Head**：在继承配置中将 `model.roi_head.bbox_head.num_classes` 与 `model.roi_head.mask_head.num_classes` 改为新数据集类别数（Cityscapes 示例 = 8）；如需可同时显式覆写 BBox Coder、损失函数等（详见原文 Modify head 段落）。
4. **修改训练 schedule**（微调关键）：

   ```python
   optimizer = dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0001)  # batch size=8
   optimizer_config = dict(grad_clip=None)
   lr_config = dict(
       policy='step',
       warmup='linear',
       warmup_iters=500,
       warmup_ratio=0.001,
       step=[7])
   total_epochs = 8  # actual epoch = 8 * 8 = 64
   log_config = dict(interval=100)
   ```

5. **指定预训练权重**：将 `load_from` 指向 Model Zoo 中的目标权重 URL，例如：

   ```python
   load_from = 'https://s3.ap-northeast-2.amazonaws.com/open-mmlab/mmdetection/models/mask_rcnn_r50_fpn_2x_20181010-41d35c05.pth'
   ```

   建议训练启动前手动 `wget` 该文件到本地，再将 `load_from` 改为本地路径。
6. **启动训练**：使用 MMDetection 标准训练命令（如 `tools/train.py` + 新配置路径）即可开始微调；原文未涉及具体命令行参数与启动命令，详见 MMDetection 主文档。

> 注：原文未涉及数据增强、评估指标、验证流程、混合精度 (AMP) 训练、多卡分布式启动参数等更细粒度开关，这些均不在本教程讨论范围内。
