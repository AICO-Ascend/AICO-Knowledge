# Tutorial 7: Finetuning Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/NasFPN/docs/tutorials/finetune.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/NasFPN/docs/tutorials/finetune.md

# 文档深度解读:NasFPN · Tutorial 7 — Finetuning Models

---

## 【定位】

这篇文档是 MMDetection 中**教程 7**,指导用户如何将在 COCO 数据集上预训练好的检测模型(如 Mask R-CNN)**迁移微调(finetune)到新的数据集**(如 CityScapes、KITTI),通过复用预训练权重并只调整少量配置,在新数据集上获得比从零训练更好的性能。

---

## 【技术要点】

1. **两步式微调流程**:① 按 Tutorial 2 为新数据集添加支持;② 修改 configs(继承基础 config、修改 head、修改数据集、修改训练调度、使用预训练权重)。
2. **配置继承机制**:MMDetection V2.0 支持从多个已有 config 继承,新 config 通过 `_base_` 列表同时继承模型结构、数据集配置和运行时设置(如 `_base_/models/mask_rcnn_r50_fpn.py`、`_base_/datasets/cityscapes_instance.py`、`_base_/default_runtime.py`)。
3. **Head 修改策略**:仅修改 `roi_head` 中的 `num_classes`(示例中 bbox_head 和 mask_head 都设为 **8**),其余权重从预训练模型继承,最终预测头会被替换。
4. **微调训练调度特征**:相比默认调度,**更小的学习率**(示例 `lr=0.01`,针对 batch size=8)和**更少的训练 epoch**(示例 total_epochs=8,实际 8×8=64 epoch),并配合 warmup(`warmup='linear'`、`warmup_iters=500`、`warmup_ratio=0.001`)与 step 策略(`step=[7]`,且注释说明 `[7] yields higher performance than [6]`)。
5. **预训练权重加载**:通过 `load_from` 指定预训练模型 URL;文档建议提前下载权重以避免训练过程中下载。
6. **数据集支持范围**:MMDetection V2.0 已支持 VOC、WIDER FACE、COCO、Cityscapes 四类数据集。

---

## 【关键机制与数据】

**工作原理(以 Cityscapes 为例的 Mask R-CNN 微调)**:

1. **基础结构继承**:新 config 同时继承模型骨架(`mask_rcnn_r50_fpn.py`)、数据集定义(`cityscapes_instance.py`)、运行时默认设置(`default_runtime.py`),免去重写。
2. **Head 复用与替换**:bbox_head 保留 `Shared2FCBBoxHead` 结构(`in_channels=256`、`fc_out_channels=1024`、`roi_feat_size=7`)、bbox 编解码(`DeltaXYWHBBoxCoder`,`target_means=[0., 0., 0., 0.]`,`target_stds=[0.1, 0.1, 0.2, 0.2]`)、`reg_class_agnostic=False` 及三类损失(`CrossEntropyLoss`、`SmoothL1Loss(beta=1.0)`、`CrossEntropyLoss(use_mask=True)`),仅把 `num_classes=8` 替换以适配 Cityscapes 的类别数;mask_head 同样使用 `FCNMaskHead`,`num_convs=4`、`in_channels=256`、`conv_out_channels=256`、`num_classes=8`。
3. **优化器配置**:SGD(`lr=0.01, momentum=0.9, weight_decay=0.0001`),针对 batch size=8 设置;`grad_clip=None`。
4. **学习率调度**:`policy='step'` + linear warmup(`iters=500`,`ratio=0.001`);`step=[7]`(在第 7 个 epoch 处衰减);`total_epochs=8`;注释 `# actual epoch = 8 * 8 = 64` 表明存在 8× 系数,实际训练 64 epoch。
5. **日志间隔**:`log_config = dict(interval=100)`,每 100 iter 记录一次。
6. **预训练权重源 URL**(原文给出):
   - `http://download.openmmlab.com/mmdetection/v2.0/mask_rcnn/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco_bbox_mAP-0.408__segm_mAP-0.37_20200504_163245-42aa3d00.pth`

**性能数据(原文)**:仅在预训练权重文件名中体现 `bbox_mAP-0.408`、`segm_mAP-0.37`(COCO 上的指标),文档正文未提供在 Cityscapes 微调后的具体性能数字。

---

## 【表格解读】

**原文无表格**。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

根据文末提供的内部链接与文中引用,本文档与以下文档/模块存在上下游关系:

1. **[`../model_zoo.md`](../model_zoo.md)** — 文档开篇即声明 "use the models provided in the Model Zoo",微调依赖 Model Zoo 中已发布的预训练权重;链接路径 `../model_zoo.md` 表示与 NasFPN 同目录的父级文档(涉及各检测模型的性能与 checkpoint 列表)。
2. **[`customize_dataset.md`](customize_dataset.md)** — 文档第一步 "Add support for the new dataset following Tutorial 2: Customize Datasets" 显式链接到该教程,即在执行本文档的 config 改动之前,需先阅读该教程完成新数据集的注册与配置。
3. **MMDetection V2.0 配置体系**:涉及 `configs/_base_/models/`、`configs/_base_/datasets/`、`configs/_base_/default_runtime.py` 三类基础配置,以及 `roi_head.bbox_head`、`roi_head.mask_head` 等子模块。
4. **COCO 预训练生态**:本文档的微调起点全部建立在 COCO 预训练权重之上,与 Cityscapes、KITTI、VOC、WIDER FACE 等下游数据集形成 "上游预训练 → 下游微调" 的依赖关系。

---

## 【使用方法】

**启用方式与配置项(原文)**:

1. **创建新 config 文件**,在文件首部声明 `_base_` 列表:
   ```python
   _base_ = [
       '../_base_/models/mask_rcnn_r50_fpn.py',
       '../_base_/datasets/cityscapes_instance.py', '../_base_/default_runtime.py'
   ]
   ```
2. **重写 `model` 字段**:将 `pretrained=None`,并在内层 `roi_head.bbox_head` 与 `roi_head.mask_head` 中把 `num_classes` 改为新数据集类别数(示例为 8);其余结构、损失、BBox 编解码参数沿用继承值。
3. **重写优化器与训练调度**:
   ```python
   optimizer = dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0001)  # lr for batch size 8
   optimizer_config = dict(grad_clip=None)
   lr_config = dict(
       policy='step', warmup='linear', warmup_iters=500, warmup_ratio=0.001,
       step=[7])
   total_epochs = 8  # actual epoch = 8 * 8 = 64
   log_config = dict(interval=100)
   ```
4. **指定预训练权重**:在 config 中设置 `load_from` 为完整 URL(见原文链接),并建议提前下载到本地以避免训练中下载。
5. **数据集准备**:在训练前完成新数据集的准备与 config 注册(详见 `customize_dataset.md`);VOCO/WIDER FACE/COCO/Cityscapes 已内置支持。
6. **命令**:原文未涉及具体的训练启动命令(如 `tools/train.py` 的调用方式)。
