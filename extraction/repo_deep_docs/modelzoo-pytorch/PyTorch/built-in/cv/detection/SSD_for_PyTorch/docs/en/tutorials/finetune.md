# Tutorial 7: Finetuning Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/finetune.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/finetune.md

# 一体化深度解读:PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/finetune.md

## 【定位】

这篇文档是 MMDetection 系列教程中的第 7 篇 (Tutorial 7: Finetuning Models),核心解决的问题是:**如何把在 COCO 等大型数据集上预训练好的检测器 (如 Mask RCNN) 迁移 (finetune) 到一个新的数据集 (例如 CityScapes、KITTI) 上,以获得比从零训练更好的性能**。文档以 Cityscapes 数据集 + Mask RCNN 为主线,系统性给出了在新数据集上 finetune 预训练模型需要做的配置层修改。

---

## 【技术要点】

文档给出 finetune 一个新数据集的完整流程,核心机制可归纳为以下 5 条:

1. **两步走总体流程**:先按 Tutorial 2 (customize_dataset.md) 让框架支持新数据集;再按本文所述修改配置文件 (config)。这一点是原文明文给出的。
2. **继承式配置 (Config Inheritance)**:新 config 通过 `_base_` 列表继承模型结构、数据集、运行时设置三部分——`_base_/models/mask_rcnn_r50_fpn.py` + `_base_/datasets/cityscapes_instance.py` + `_base_/default_runtime.py`,用户也可选择全部手写而不使用继承。
3. **修改 head 以适配新类别数**:只需修改 `roi_head` 中 `bbox_head.num_classes` 和 `mask_head.num_classes` (Cityscapes 示例中均改为 `8`),其余预训练权重大部分可直接复用,只有最后的预测头会重新训练。
4. **修改训练调度 (Training Schedule)**:finetune 通常需要 **更小的学习率** 和 **更少的训练 epoch**。原文给出的示例是 `lr=0.01`(针对 batch size 8)、`max_epochs=8`、lr 在第 `7` 个 epoch 时 step、`warmup_iters=500`、`warmup_ratio=0.001`、`log_config.interval=100`,并强调 `max_epochs` 和 `lr_config.step` 需要针对具体数据集调优。
5. **加载预训练权重**:通过 `load_from` 指定预训练权重 URL。原文示例指向 `mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco` 在 COCO 上的权重 (bbox_mAP=0.408, segm_mAP=0.37)。文档提示用户最好提前手动下载,以避免训练过程中下载浪费时间。

补充要点 (原文):文档还提到 MMDetection V2.0 已经支持 VOC、WIDER FACE、COCO、Cityscapes 这几种数据集;`Shared2FCBBoxHead` 的关键参数包括 `in_channels=256`、`fc_out_channels=1024`、`roi_feat_size=7`,`bbox_coder` 使用 `DeltaXYWHBBoxCoder`,其 `target_means=[0., 0., 0., 0.]`、`target_stds=[0.1, 0.1, 0.2, 0.2]`、`reg_class_agnostic=False`,`FCNMaskHead` 使用 `num_convs=4`、`conv_out_channels=256`,分类与回归/mask 损失均为 `CrossEntropyLoss`/`SmoothL1Loss` (`beta=1.0`),`loss_weight` 均为 `1.0`。

---

## 【关键机制与数据】

**工作原理/数据流 (以 Cityscapes + Mask RCNN 为例,原文):**

1. **基座结构继承**:新 config 通过 `_base_` 数组加载三段已有配置,得到完整的 Mask RCNN FPN 模型结构 + Cityscapes 实例分割数据集定义 + 默认运行时设置 (日志、checkpoint、评估器等)。
2. **类别对齐**:把 `bbox_head.num_classes` 和 `mask_head.num_classes` 改为 Cityscapes 的 8 类。原文 (原文):"By only changing `num_classes` in the roi_head, the weights of the pre-trained models are mostly reused except the final prediction head." 即除了最后的预测层,backbone/FPN/RoI 特征提取等大部分权重都直接复用 COCO 预训练结果。
3. **损失与回归头配置**:`bbox_coder` 为 `DeltaXYWHBBoxCoder`,对 box 中心与宽高做归一化回归;`reg_class_agnostic=False` 意味着每个类别都有独立的回归参数;`loss_bbox` 使用 `SmoothL1Loss`,`beta=1.0`;`mask_head` 使用 `FCNMaskHead`,`loss_mask` 启用 `use_mask=True`。
4. **训练调度数据流**:
   - 优化器:SGD,`lr=0.01`,`momentum=0.9`,`weight_decay=0.0001`,`grad_clip=None`(原文标注该 lr 对应 batch size 8)。
   - 学习率策略:`policy='step'` + 线性 warmup (warmup_iters=500, warmup_ratio=0.001),在 epoch 7 处 step。
   - Runner:`max_epochs=8`,日志间隔 `interval=100`。
   - 原文强调:`max_epochs` 和 `lr_config.step` 需要"specifically tuned for the customized dataset"。
5. **权重加载**:`load_from` 指向 COCO 预训练权重 URL (mAP 数据已在要点 5 中给出)。训练时框架从该 checkpoint 初始化除最后预测头外的大部分参数,再在 Cityscapes 上继续训练。

**性能数据 (原文):** 预训练权重文件本身携带的指标为 bbox_mAP=0.408、segm_mAP=0.37(在 COCO test-dev 上)。文档本身没有给出在 Cityscapes 上 finetune 后的具体 mAP/segm mAP 数字。

---

## 【表格解读】

**原文无表格。** 文档全部以代码片段 + 文字描述形式呈现,未提供参数表、性能对比表或配置项表。

---

## 【公式解读】

**原文无公式。** 文档没有给出任何 LaTeX 公式或伪代码形式的公式,仅以 Python config 字典形式描述模型、优化器、学习率策略等设置。

---

## 【关联】

文档与文末/文中其他模块的关联:

- **上游/前置教程**:**[Tutorial 2: Customize Datasets](customize_dataset.md)** —— 文档第 2 段明确把"按 Tutorial 2 让框架支持新数据集"列为 finetune 的**第 1 步**,即本文的第 2 步建立在 customize_dataset 的成果之上。
- **权重来源**:**[Model Zoo](../model_zoo.md)** —— 文档开头明确"detectors pre-trained on the COCO dataset can serve as a good pre-trained model for other datasets, e.g., CityScapes and KITTI Dataset... use the models provided in the Model Zoo",`load_from` 中使用的预训练权重链接实际就是从 Model Zoo 中挑选得到的。也就是说,本文是 Model Zoo 的下游"使用说明",而 Model Zoo 是本文的上游"权重仓库"。
- **基座配置依赖**:文中 `_base_` 引用的 `_base_/models/mask_rcnn_r50_fpn.py`、`_base_/datasets/cityscapes_instance.py`、`_base_/default_runtime.py` 是 MMDetection 配置文件体系 (configs 目录) 中的内置 base config,本文展示的是一种"组合式复用"模式。

整体链路:**Model Zoo (权重) → Finetune 教程 (本文) → Customize Datasets (数据集接入) → 训练/推理**。

---

## 【使用方法】

**启用方式 (原文):** 把 5 处配置修改组合起来,得到一个新的 finetune config,再使用 MMDetection 标准的训练命令启动训练。原文给出的关键配置项与命令如下:

1. **继承基座配置** (原文):

```python
_base_ = [
    '../_base_/models/mask_rcnn_r50_fpn.py',
    '../_base_/datasets/cityscapes_instance.py', '../_base_/default_runtime.py'
]
```

2. **修改 head** (原文,只展示需要改动部分):将 `bbox_head.num_classes` 与 `mask_head.num_classes` 改为新数据集类别数 (Cityscapes 为 8),其余参数 (`in_channels=256`、`fc_out_channels=1024`、`roi_feat_size=7`、`num_convs=4`、`conv_out_channels=256` 等) 保留;`bbox_coder` 用 `DeltaXYWHBBoxCoder`、`target_means=[0., 0., 0., 0.]`、`target_stds=[0.1, 0.1, 0.2, 0.2]`、`reg_class_agnostic=False`;`loss_cls` 用 `CrossEntropyLoss` (`use_sigmoid=False`, `loss_weight=1.0`),`loss_bbox` 用 `SmoothL1Loss` (`beta=1.0`, `loss_weight=1.0`),`loss_mask` 用 `CrossEntropyLoss` (`use_mask=True`, `loss_weight=1.0`);并设置 `model.pretrained=None` 以避免重复下载 ImageNet 预训练 (backbone 权重将由 `load_from` 提供)。

3. **数据集 (原文)**:MMDetection V2.0 原生支持 VOC / WIDER FACE / COCO / Cityscapes;若不在此列,需按 [customize_dataset.md](customize_dataset.md) 先注册。

4. **训练调度 (原文):**

```python
# optimizer (lr is set for a batch size of 8)
optimizer = dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0001)
optimizer_config = dict(grad_clip=None)
# learning policy
lr_config = dict(
    policy='step',
    warmup='linear',
    warmup_iters=500,
    warmup_ratio=0.001,
    step=[7])
# max_epochs and step need specifically tuned for the customized dataset
runner = dict(max_epochs=8)
log_config = dict(interval=100)
```

5. **加载预训练权重 (原文):**

```python
load_from = 'https://download.openmmlab.com/mmdetection/v2.0/mask_rcnn/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco_bbox_mAP-0.408__segm_mAP-0.37_20200504_163245-42aa3d00.pth'
```

文档提示:用户最好在训练前手动下载权重到本地,再把 `load_from` 改成本地路径,以避免训练过程中在线下载带来的不稳定。

**配置项小结 (原文有):** `_base_`、`pretrained`、`roi_head.bbox_head.*`、`roi_head.mask_head.*`、`bbox_coder.*`、`loss_cls.*`、`loss_bbox.*`、`loss_mask.*`、`num_classes`、`optimizer`、`optimizer_config`、`lr_config`、`runner.max_epochs`、`log_config.interval`、`load_from`。

**原文未涉及的内容:** 具体的训练启动命令 (如 `tools/train.py` 的调用方式、`work_dir` 设置、分布式启动命令)、验证/测试命令、finetune 后在 Cityscapes 上的具体 mAP 数字、其它数据集 (如 KITTI) 的具体配置示例 —— 这些需要参考其它文档,本文未给出。
