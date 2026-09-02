# Tutorial 7: Finetuning Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/FCOS/docs/tutorials/finetune.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/FCOS/docs/tutorials/finetune.md

# Tutorial 7: Finetuning Models —— 一体化深度解读

## 【定位】

本教程是 MMDetection V2.0 框架下"模型微调（Finetune）"专题的入门指引,解决的核心问题是: **如何把在 COCO 数据集上预训练好的检测器,迁移到 Cityscapes、KITTI 等其他新数据集上,以获得更好的性能**;整体能力描述为:提供从数据集注册、模型结构继承、检测头改造、训练调度调整到预训练权重加载的一整套"五步式"微调工作流。

---

## 【技术要点】

1. **两阶段微调流程**:①按 [Tutorial 2: Customize Datasets](customize_dataset.md) 添加新数据集支持;②按本教程修改配置(原文:"There are two steps to finetune a model on a new dataset")。
2. **多配置继承(MMDetection V2.0 特性)**:通过 `_base_` 列表同时继承模型、数据集、运行时三类基础配置,避免重写整份配置(原文:"MMDetection V2.0 support inheriting configs from multiple existing configs")。
3. **检测头仅修改 `num_classes`**:将预训练权重 `pretrained=None`(重新加载预训练),但只对 `roi_head.bbox_head` 与 `roi_head.mask_head` 替换类别数(`num_classes=8`),其它权重大部分复用(原文:"By only changing `num_classes` in the roi_head, the weights of the pre-trained models are mostly reused except the final prediction head")。
4. **数据集基线支持范围**:原文明确列出的内置支持数据集为 **VOC、WIDER FACE、COCO、Cityscapes**(原文:"MMDetection V2.0 already support VOC, WIDER FACE, COCO and Cityscapes Dataset")。
5. **微调专用训练调度**:相比默认调度,微调要求**更小的学习率**与**更少的训练轮次**(原文:"the finetuning hyperparameters vary from the default schedule. It usually requires smaller learning rate and less training epochs")。
6. **预训练权重通过 `load_from` 加载**:为避免训练中下载浪费时间,需事先下载 `.pth` 文件(原文:"The users might need to download the model weights before training to avoid the download time during training")。

---

## 【关键机制与数据】

### 工作原理(原文有的部分)

* **继承机制**:新配置文件通过 `_base_` 列表从已有配置里导入子模块。本例(Cityscapes + Mask R-CNN 50 FPN)继承三份配置:
  - `../_base_/models/mask_rcnn_r50_fpn.py` —— 提供模型基本结构;
  - `../_base_/datasets/cityscapes_instance.py` —— 提供 Cityscapes 实例分割数据集配置;
  - `../_base_/default_runtime.py` —— 提供训练调度、日志、checkpoint 等运行时默认。
  上述配置位于 `configs` 目录下;用户也可不用继承,而直接完整编写(原文:"This configs are in the `configs` directory and the users can also choose to write the whole contents rather than use inheritance")。

* **检测头改造的数据流**:在 Mask R-CNN + Cityscapes 场景中:
  - `bbox_head` 改为 `Shared2FCBBoxHead`,`in_channels=256`、`fc_out_channels=1024`、`roi_feat_size=7`、`num_classes=8`,`reg_class_agnostic=False`,损失为 `CrossEntropyLoss`(`use_sigmoid=False`,`loss_weight=1.0`)与 `SmoothL1Loss`(`beta=1.0`,`loss_weight=1.0`);
  - `mask_head` 改为 `FCNMaskHead`,`num_convs=4`、`in_channels=256`、`conv_out_channels=256`、`num_classes=8`,损失为 `CrossEntropyLoss`(`use_mask=True`,`loss_weight=1.0`);
  - BBox 编码采用 `DeltaXYWHBBoxCoder`,`target_means=[0., 0., 0., 0.]`,`target_stds=[0.1, 0.1, 0.2, 0.2]`。
  上述配置把分类输出维度从 COCO 的 80 类改为 Cityscapes 的 **8 类**,其余权重由 `load_from` 加载的预训练 `.pth` 填充(原文:"By only changing `num_classes` in the roi_head...")。

* **训练调度机制**:原文给出针对 batch size = 8 的设定:
  - 优化器 `SGD`,`lr=0.01`、`momentum=0.9`、`weight_decay=0.0001`,`grad_clip=None`;
  - 学习率策略 `step`,warmup 为线性,`warmup_iters=500`,`warmup_ratio=0.001`,学习率衰减点 `step=[7]`;
  - 总训练 `total_epochs = 8`,原文提示实际 epoch 折算为 **8 × 8 = 64**(8 卡 batch size 折算);
  - 日志间隔 `log_config = dict(interval=100)`。
  原文同时注释:`# [7] yields higher performance than [6]`,说明选 `step=[7]` 是基于性能比较的实验结论(原文:"[7] yields higher performance than [6]")。

* **预训练权重加载**:通过 `load_from` 字段直接指向 S3 上的 Mask R-CNN R50 FPN 2x 预训练权重:`https://s3.ap-northeast-2.amazonaws.com/open-mmlab/mmdetection/models/mask_rcnn_r50_fpn_2x_20181010-41d35c05.pth`(原文逐字给出该 URL)。

### 性能/数据点

* 原文未给出 Cityscapes 复现指标,仅就学习率衰减点 `[7]` 与 `[6]` 给出相对结论:**`[7]` 性能高于 `[6]`**(原文:"[7] yields higher performance than [6]")。
* 实际 epoch 折算:**8 × 8 = 64**(原文:"total_epochs = 8  # actual epoch = 8 * 8 = 64")。

---

## 【表格解读】

**原文无表格。**(全文未出现任何 markdown 表格或 ASCII 表格结构。)

---

## 【公式解读】

**原文无公式。**(全文未出现 LaTeX 数学公式或伪代码公式;仅有的算术式为注释 `actual epoch = 8 * 8 = 64`,已在上文训练调度部分保留。)

---

## 【关联】

* **上游数据来源**:本教程是 [Tutorial 2: Customize Datasets](customize_dataset.md) 的下游步骤,用户必须先按该教程让 MMDetection 识别新数据集(如 Cityscapes),才能进行本教程的五步改造(原文:"Add support for the new dataset following [Tutorial 2: Customize Datasets](customize_dataset.md)")。
* **预训练权重来源**:本文反复强调"pre-trained model"指向 [Model Zoo](../model_zoo.md),即预训练模型列表位于 Model Zoo 页面;`load_from` 字段指定的 Mask R-CNN R50 FPN 2x 权重即是 Model Zoo 中提供的模型之一(原文:"use the models provided in the [Model Zoo]...for other datasets to obtain better performance")。
* **与 `_base_` 配置体系的关系**:本文演示了 MMDetection V2.0 的多配置继承机制——同一文件同时继承模型、数据集、运行时三份基础配置,是 MMDetection 配置系统的基础能力;若不使用继承,需要手动拼装 mask_rcnn_r50_fpn / cityscapes_instance / default_runtime 的全部字段(原文:"the users can also choose to write the whole contents rather than use inheritance")。
* **与其它教程的相对位置**:在原始 MMDetection 教程序列中,本文是 **Tutorial 7**(Tutorial 2 是 Customize Datasets),整体位于"自定义数据集 → 微调预训练模型"这一链条之中。

---

## 【使用方法】

> 以下命令/配置均**逐字取自原文**,未做扩展。

### Step 1: 新建配置文件并继承基础配置(原文)

```python
_base_ = [
    '../_base_/models/mask_rcnn_r50_fpn.py',
    '../_base_/datasets/cityscapes_instance.py', '../_base_/default_runtime.py'
]
```

### Step 2: 改造检测头(原文)

```python
model = dict(
    pretrained=None,
    roi_head=dict(
        bbox_head=dict(
            type='Shared2FCBBoxHead',
            in_channels=256,
            fc_out_channels=1024,
            roi_feat_size=7,
            num_classes=8,
            bbox_coder=dict(
                type='DeltaXYWHBBoxCoder',
                target_means=[0., 0., 0., 0.],
                target_stds=[0.1, 0.1, 0.2, 0.2]),
            reg_class_agnostic=False,
            loss_cls=dict(
                type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0),
            loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=1.0)),
        mask_head=dict(
            type='FCNMaskHead',
            num_convs=4,
            in_channels=256,
            conv_out_channels=256,
            num_classes=8,
            loss_mask=dict(
                type='CrossEntropyLoss', use_mask=True, loss_weight=1.0))))
```

> 关键参数说明:`num_classes=8` 来自 Cityscapes 实例分割的类别数;`pretrained=None` 是为了让 `load_from` 中的预训练权重生效。

### Step 3: 数据集准备(原文)

原文仅声明需要"准备数据集并写 dataset 相关配置",未给出具体命令;支持的内置数据集为 **VOC / WIDER FACE / COCO / Cityscapes**。

### Step 4: 训练调度(原文,按 batch size = 8 设定)

```python
# optimizer
# lr is set for a batch size of 8
optimizer = dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0001)
optimizer_config = dict(grad_clip=None)
# learning policy
lr_config = dict(
    policy='step',
    warmup='linear',
    warmup_iters=500,
    warmup_ratio=0.001,
    # [7] yields higher performance than [6]
    step=[7])
total_epochs = 8  # actual epoch = 8 * 8 = 64
log_config = dict(interval=100)
```

### Step 5: 加载预训练权重(原文)

```python
load_from = 'https://s3.ap-northeast-2.amazonaws.com/open-mmlab/mmdetection/models/mask_rcnn_r50_fpn_2x_20181010-41d35c05.pth'  # noqa
```

> 原文建议:**训练前先下载该 `.pth` 文件**,避免训练过程中实时下载造成中断(原文:"The users might need to download the model weights before training to avoid the download time during training")。

### 命令行启动(原文未涉及)

原文未给出 `python tools/train.py ...` 之类的启动命令,仅停留在"修改配置文件"层面;具体训练命令需参考 MMDetection 通用流程。
