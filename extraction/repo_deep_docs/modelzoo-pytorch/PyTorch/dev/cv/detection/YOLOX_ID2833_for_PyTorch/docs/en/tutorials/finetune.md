# Tutorial 7: Finetuning Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/finetune.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/finetune.md

# 深度解读: Tutorial 7: Finetuning Models

## 【定位】
本文档面向 MMDetection V2.0 用户,介绍如何将 COCO 数据集上预训练的检测模型(以 Mask R-CNN 为代表)迁移/微调到新数据集(如 CityScapes、KITTI),以获得更好的下游性能,并以 Cityscapes 为实例给出可落地的配置文件修改步骤。

---

## 【技术要点】
1. **两阶段流程**: 在新数据集上微调模型分两步 — ① 按 [Tutorial 2: Customize Datasets](customize_dataset.md) 增加新数据集支持; ② 按本文修改配置文件。
2. **配置继承机制**: 支持从多个已有 base config 组合继承,需在 `_base_` 列表中分别引入 model 结构、数据集和运行时配置,以 Cityscapes+Mask R-CNN 微调为例继承 `_base_/models/mask_rcnn_r50_fpn.py`、`_base_/datasets/cityscapes_instance.py`、`_base_/default_runtime.py`。
3. **Head 改造**: 仅需在 `roi_head` 中将 `num_classes` 由 COCO 的 80 改为 Cityscapes 的 **8**,其余预训练权重(骨干、FPN、head 大部分)可被复用,只重训最终预测层。
4. **数据集配置**: MMDetection V2.0 已内置 VOC、WIDER FACE、COCO、Cityscapes 数据集配置。
5. **训练调度差异**: 微调相比默认 schedule 通常需要更小的学习率与更少的训练轮次,示例采用 SGD (`lr=0.01`, `momentum=0.9`, `weight_decay=0.0001`),`max_epochs=8`,学习率 `step=[7]` 衰减,并启用线性 warmup (`warmup_iters=500`, `warmup_ratio=0.001`)。
6. **加载预训练权重**: 通过配置文件中的 `load_from` 字段指定预训练权重 URL,建议训练前手动下载以避免训练中下载阻塞;`model.pretrained` 置为 `None`,避免重复下载 backbone 权重。

---

## 【关键机制与数据】
- **工作原理 (原文)**: 通过 `_base_` 列表复用现有 model/dataset/runtime 配置,降低用户书写配置负担并减少 bug;之后通过 `model = dict(...)` 覆盖 `roi_head` 中的 `bbox_head` 与 `mask_head`,主要把 `num_classes` 替换为 Cityscapes 的 8 类;最后通过 `load_from` 拉取 COCO 预训练权重,使 backbone、FPN、head 主体被复用,仅重新学习最终分类/回归层。
- **bbox 编码 (原文)**: `DeltaXYWHBBoxCoder`,`target_means=[0., 0., 0., 0.]`,`target_stds=[0.1, 0.1, 0.2, 0.2]`;`reg_class_agnostic=False`。
- **Head 结构 (原文)**: `Shared2FCBBoxHead`(`in_channels=256`, `fc_out_channels=1024`, `roi_feat_size=7`);`FCNMaskHead`(`num_convs=4`, `in_channels=256`, `conv_out_channels=256`)。
- **损失 (原文)**: 分类使用 `CrossEntropyLoss`(`use_sigmoid=False`),回归使用 `SmoothL1Loss`(`beta=1.0`),分割 mask 使用 `CrossEntropyLoss`(`use_mask=True`);三类损失 `loss_weight` 均为 `1.0`。
- **优化器 (原文)**: SGD, `lr=0.01`(基于 batch size 8 设定), `momentum=0.9`, `weight_decay=0.0001`,`grad_clip=None`。
- **学习率策略 (原文)**: `policy='step'`, `warmup='linear'`, `warmup_iters=500`, `warmup_ratio=0.001`, `step=[7]`(即第 7 个 epoch 衰减);`runner.max_epochs=8`, `log_config.interval=100`。
- **预训练权重来源 (原文)**: `https://download.openmmlab.com/mmdetection/v2.0/mask_rcnn/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco_bbox_mAP-0.408__segm_mAP-0.37_20200504_163245-42aa3d00.pth`,对应 `mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco` 模型。
- **性能数据**: 原文中出现的数值仅来自上述权重文件名:`bbox_mAP-0.408`、`segm_mAP-0.37`(源自该 .pth 文件名,原文未额外解释其评测协议)。

---

## 【表格解读】
**原文无表格**。

(原文中并未提供任何参数表/性能对比表/配置项表格,关键参数均以 Python 代码块形式给出,见上方【技术要点】与【关键机制与数据】逐条复述。)

---

## 【公式解读】
**原文无公式**。

(原文未给出 LaTeX 公式或伪代码公式,所有数值参数如 `target_means=[0., 0., 0., 0.]`、`target_stds=[0.1, 0.1, 0.2, 0.2]`、`beta=1.0` 等仅以配置项出现,而非数学公式形式。)

---

## 【关联】
- **[Model Zoo](../model_zoo.md)**: 本文微调起点 — `load_from` 字段所指向的预训练权重来源于 Model Zoo 中的 `mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco` 等条目;Model Zoo 提供可选 backbone / schedule 组合清单,是选择 `pretrained` 来源的依据。
- **[Tutorial 2: Customize Datasets](customize_dataset.md)**: 文中第一步要求添加新数据集支持,需遵循该教程注册 dataset、pipeline、classes;本文的 `num_classes=8` 等参数需与 `customize_dataset.md` 中注册的类别数保持一致,二者构成"先注册数据,再改配置微调"的串行依赖。
- 隐含依赖:本文示例基于 Mask R-CNN(`mask_rcnn_r50_fpn.py`),其 backbone+FPN 的预训练复用依赖 `_base_/models/` 下的对应 base 配置,运行时/日志等则统一继承自 `_base_/default_runtime.py`。

---

## 【使用方法】

### 启用方式(原文)
按以下 5 步修改 config 文件,然后按 MMDetection 标准训练命令启动(原文未列出具体启动命令行):

1. **继承 base configs**(示例):
   ```python
   _base_ = [
       '../_base_/models/mask_rcnn_r50_fpn.py',
       '../_base_/datasets/cityscapes_instance.py', '../_base_/default_runtime.py'
   ]
   ```
2. **修改 head**(将 `num_classes` 改为新数据集类别数,Cityscapes=8,`pretrained=None`,其它字段保持如原示例)。
3. **修改 dataset**:按 [customize_dataset.md](customize_dataset.md) 注册新数据集;如使用 Cityscapes 可直接继承 `_base_/datasets/cityscapes_instance.py`(无需重写)。
4. **修改训练调度**(微调常用设置):
   ```python
   optimizer = dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0001)
   optimizer_config = dict(grad_clip=None)
   lr_config = dict(
       policy='step', warmup='linear',
       warmup_iters=500, warmup_ratio=0.001,
       step=[7])
   runner = dict(max_epochs=8)
   log_config = dict(interval=100)
   ```
   注:`lr=0.01` 是 batch size=8 的设定值;`max_epochs` 与 `step` 需针对自定义数据集**专门调参**(原文原话)。
5. **加载预训练权重**:
   ```python
   load_from = 'https://download.openmmlab.com/mmdetection/v2.0/mask_rcnn/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco_bbox_mAP-0.408__segm_mAP-0.37_20200504_163245-42aa3d00.pth'  # noqa
   ```
   建议训练前手动下载该 `.pth` 到本地,并将 `load_from` 改为本地路径(原文提示:"users might need to download the model weights before training to avoid the download time during training")。

### 配置项汇总(原文)
| 字段 | 取值/含义 |
|---|---|
| `model.pretrained` | `None`(避免重复下载 backbone) |
| `model.roi_head.bbox_head.num_classes` | `8`(Cityscapes) |
| `model.roi_head.bbox_head.type` | `Shared2FCBBoxHead` |
| `model.roi_head.bbox_head.in_channels` | `256` |
| `model.roi_head.bbox_head.fc_out_channels` | `1024` |
| `model.roi_head.bbox_head.roi_feat_size` | `7` |
| `model.roi_head.bbox_head.bbox_coder.target_means` | `[0., 0., 0., 0.]` |
| `model.roi_head.bbox_head.bbox_coder.target_stds` | `[0.1, 0.1, 0.2, 0.2]` |
| `model.roi_head.bbox_head.reg_class_agnostic` | `False` |
| `model.roi_head.mask_head.type` | `FCNMaskHead` |
| `model.roi_head.mask_head.num_convs` | `4` |
| `model.roi_head.mask_head.conv_out_channels` | `256` |
| `optimizer.type` | `SGD` |
| `optimizer.lr` | `0.01`(batch size=8) |
| `optimizer.momentum` | `0.9` |
| `optimizer.weight_decay` | `0.0001` |
| `lr_config.policy` | `step` |
| `lr_config.warmup` | `linear`, `warmup_iters=500`, `warmup_ratio=0.001` |
| `lr_config.step` | `[7]` |
| `runner.max_epochs` | `8` |
| `log_config.interval` | `100` |
| `load_from` | mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco 权重 URL |

### 启动训练命令
**原文未涉及**(未给出 `tools/train.py` 等具体启动命令,读者需按 MMDetection 标准训练流程自行启动)。
