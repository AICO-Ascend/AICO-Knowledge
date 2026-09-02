# Tutorial 7: Finetuning Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/tutorials/finetune.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/tutorials/finetune.md

# Tutorial 7: Finetuning Models 深度解读

## 【定位】
本教程解决"如何将 COCO 预训练的目标检测/实例分割模型迁移到其他数据集(如 Cityscapes、KITTI)上进行微调"的问题,通过继承基础配置 + 五项局部修改的标准化流程,降低用户在新数据集上获得高性能检测器的门槛。

---

## 【技术要点】

1. **两阶段微调流程**:第一步按 [Tutorial 2: Customize Datasets](customize_dataset.md) 增加新数据集支持;第二步修改配置(下文以 Cityscapes 为例涉及五个修改点)。

2. **多配置继承机制(MMDetection V2.0)**:通过 `_base_` 列表同时继承模型结构、数据集、训练调度三类基础配置,避免重复编写整份配置;示例继承 `_base_/models/mask_rcnn_r50_fpn.py`、`_base_/datasets/cityscapes_instance.py`、`_base_/default_runtime.py` 三个文件。

3. **头部(Head)按类别数改造**:仅在 `roi_head` 中将 `num_classes` 由 COCO 的 80 改为 Cityscapes 的 **8**(`bbox_head.num_classes=8`,`mask_head.num_classes=8`);其余预训练权重可继续复用,只有最终预测头被重新训练。BBox Head 采用 `Shared2FCBBoxHead`(`in_channels=256`、`fc_out_channels=1024`、`roi_feat_size=7`),Mask Head 采用 `FCNMaskHead`(`num_convs=4`、`in_channels=256`、`conv_out_channels=256`)。

4. **bbox 编码与损失**:使用 `DeltaXYWHBBoxCoder`,`target_means=[0., 0., 0., 0.]`,`target_stds=[0.1, 0.1, 0.2, 0.2]`;`reg_class_agnostic=False`;分类损失 `CrossEntropyLoss`(`use_sigmoid=False, loss_weight=1.0`),回归损失 `SmoothL1Loss`(`beta=1.0, loss_weight=1.0`);Mask 损失 `CrossEntropyLoss`(`use_mask=True, loss_weight=1.0`)。

5. **差异化训练调度(微调专用)**:相比默认调度,**学习率更小、训练轮数更少**。优化器 `SGD`(`lr=0.01, momentum=0.9, weight_decay=0.0001`,该 lr 针对 batch size=8 设置);学习率调度 `policy='step'`、`warmup='linear'`、`warmup_iters=500`、`warmup_ratio=0.001`、`step=[7]`(原文注释:[7] 比 [6] 性能更高);`total_epochs = 8`(实际 epoch = 8 × 8 = 64);`log_config.interval=100`;`grad_clip=None`。

6. **加载预训练权重**:通过 `load_from` 指定已发布的预训练模型 URL,建议提前下载权重以避免训练中下载。示例 URL 对应 `mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco` 模型(原文中以 `bbox_mAP-0.408__segm_mAP-0.37` 性能标注命名)。

---

## 【关键机制与数据】

**工作原理与数据流(原文提炼)**:

- **整体机制**:预训练检测器(COCO)→ 加载至新数据集(Cityscapes)→ 仅重新训练与新类别数耦合的"预测头"参数 → 其余 backbone/FPN/早期 head 复用 COCO 权重,实现知识迁移。
- **类别数变化驱动 head 重训**:Cityscapes 实例任务共 8 类,`bbox_head.num_classes=8` 与 `mask_head.num_classes=8` 是触发 head 重新初始化的关键。
- **学习率与轮数差异化的目的**:避免在已收敛的特征上因大学习率破坏预训练表征;`total_epochs=8` 与 `step=[7]` 配合在第 7 个 epoch 处衰减 lr;`warmup_iters=500` 与 `warmup_ratio=0.001` 给出线性 warmup 起步,降低微调初期震荡。
- **batch size 与 lr 的耦合**:原文明确"lr is set for a batch size of 8",若实际 batch size 改变,需按线性缩放规则相应调整 lr。

**原文性能数据**:
- 原文:`bbox_mAP-0.408__segm_mAP-0.37`(对应 `mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco` 在 COCO 上的报告值,出现在预训练权重 URL 的文件名中)。

---

## 【表格解读】

**原文无表格**。

---

## 【公式解读】

**原文无公式**(原文中未出现 LaTeX 或伪代码形式公式;`step=[7]`、`total_epochs=8`、`actual epoch = 8 * 8 = 64` 属于配置参数而非数学公式)。

---

## 【关联】

- **上游依赖**:[Tutorial 2: Customize Datasets](customize_dataset.md) —— 微调第一步"为新数据集增加支持"必须先完成本教程才能进行。
- **权重来源**:[Model Zoo](../model_zoo.md) —— `load_from` 所指向的预训练模型来自 MMDetection 官方 Model Zoo,本教程是该 Zoo 中模型"二次利用"的入口。
- **配置结构依赖**:继承的 `_base_/models/mask_rcnn_r50_fpn.py`、`_base_/datasets/cityscapes_instance.py`、`_base_/default_runtime.py` 三个文件,均位于 MMDetection V2.0 的 `configs` 目录,是 MMDetection V2.0 起引入的多配置继承特性的具体载体。
- **同类延伸**:Cityscapes 之外,文中提及 KITTI Dataset 也可按相同思路微调(原文表述为 "e.g., CityScapes and KITTI Dataset")。

---

## 【使用方法】

**启用方式与配置命令(原文汇总)**:

1. **新建配置文件**,在文件顶部写入继承语句:
   ```python
   _base_ = [
       '../_base_/models/mask_rcnn_r50_fpn.py',
       '../_base_/datasets/cityscapes_instance.py', '../_base_/default_runtime.py'
   ]
   ```

2. **修改 `model` 配置块**(原文中已给出完整 Python 片段,关键修改点为 `pretrained=None` 以及 `roi_head.bbox_head.num_classes=8`、`roi_head.mask_head.num_classes=8`)。

3. **准备数据集**:按 [Tutorial 2: Customize Datasets](customize_dataset.md) 完成;MMDetection V2.0 已内置 VOC、WIDER FACE、COCO、Cityscapes 的数据集配置。

4. **修改训练调度**(原文完整片段):
   ```python
   # optimizer (lr is set for a batch size of 8)
   optimizer = dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0001)
   optimizer_config = dict(grad_clip=None)
   # learning policy
   lr_config = dict(
       policy='step', warmup='linear', warmup_iters=500,
       warmup_ratio=0.001,
       step=[7])
   total_epochs = 8  # actual epoch = 8 * 8 = 64
   log_config = dict(interval=100)
   ```

5. **指定预训练权重**(原文片段):
   ```python
   load_from = 'http://download.openmmlab.com/mmdetection/v2.0/mask_rcnn/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco_bbox_mAP-0.408__segm_mAP-0.37_20200504_163245-42aa3d00.pth'
   ```
   原文建议"提前下载模型权重"以避免训练中下载耗时。

6. **训练命令**:原文未涉及具体启动命令(属于通用 mmdet 训练流程,本文档不展开)。
