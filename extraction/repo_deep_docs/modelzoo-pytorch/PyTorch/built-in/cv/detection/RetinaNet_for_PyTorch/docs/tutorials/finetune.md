# Tutorial 7: Finetuning Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch/docs/tutorials/finetune.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch/docs/tutorials/finetune.md

# 深度解读:Tutorial 7 - Finetuning Models

## 【定位】

这篇文档指导用户如何将 Model Zoo 中在 COCO 数据集上预训练好的检测器(如 Mask R-CNN)迁移到新数据集(如 Cityscapes、KITTI)上进行微调(finetune),以获得更好的性能,核心方法是修改配置文件(config)而非重新训练。

---

## 【技术要点】

1. **Config 继承机制(Inherit base configs)**:通过 `_base_` 列表一次性继承三类基础配置——模型结构、目标数据集、运行时训练设置,避免重复书写整份 config 并减少 bug。原文示例继承自 `mask_rcnn_r50_fpn.py` + `cityscapes_instance.py` + `default_runtime.py`。

2. **检测头适配(Modify head)**:仅修改 `roi_head` 中的 `num_classes`,其余骨干权重基本可复用,仅最终的预测头(`Shared2FCBBoxHead` / `FCNMaskHead`)需要重新训练。原文将类别数设为 `num_classes=8`(Cityscapes 实例数)。

3. **数据集适配(Modify dataset)**:复用 MMDetection V2.0 内置的 `cityscapes_instance.py`(已支持 VOC、WIDER FACE、COCO、Cityscapes 四类数据集的注册),用户只需按 [Tutorial 2: Customize Datasets](customize_dataset.md) 准备新数据。

4. **训练计划调整(Modify training schedule)**:微调阶段需要**更小的学习率**与**更少的训练轮数**——原文示例使用 `lr=0.01`(针对 batch_size=8)、SGD+momentum=0.9+weight_decay=0.0001、step 学习率策略(warmup_iters=500, step=[7], total_epochs=8 即实际 8×8=64 epoch)、log interval=100。

5. **加载预训练权重(Use pre-trained model)**:通过 `load_from` 字段指向预训练权重 URL,原文链接指向 `mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco` 的 COCO 预训练权重(下载链接建议提前手工下载以避免训练中断)。

6. **边界框编解码配置保留**:`DeltaXYWHBBoxCoder` 的 `target_means=[0.,0.,0.,0.]` 与 `target_stds=[0.1,0.1,0.2,0.2]` 沿用 COCO 设置;`reg_class_agnostic=False`(即 per-class regression);损失函数仍为 `CrossEntropyLoss`(loss_weight=1.0)与 `SmoothL1Loss`(beta=1.0, loss_weight=1.0)。

---

## 【关键机制与数据】

**工作流程(原文):** "There are two steps to finetune a model on a new dataset. Add support for the new dataset following Tutorial 2: Customize Datasets. Modify the configs as will be discussed in this tutorial."

**配置修改的五步走(原文,以 Cityscapes 为例):**

| 步骤 | 作用 | 关键数据(原文) |
|------|------|----------------|
| Inherit base configs | 复用模型/数据/运行时基线 | 3 个 `_base_` 文件 |
| Modify head | 仅换 `num_classes`,其余权重复用 | `num_classes=8` |
| Modify dataset | 接入 Cityscapes 实例配置 | VOC/WIDER FACE/COCO/Cityscapes 已支持 |
| Modify training schedule | 降低 lr,缩短 epoch | `lr=0.01`, `total_epochs=8` (实际 64) |
| Use pre-trained model | `load_from` 指向权重 | 原文 URL 对应 COCO mAP 指标见下 |

**权重复用机制(原文):** "By only changing `num_classes` in the roi_head, the weights of the pre-trained models are mostly reused except the final prediction head."

**性能数据(原文):** 预训练权重 `mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco` 在 COCO 上报告 **bbox_mAP=0.408**, **segm_mAP=0.37**(20200504_163245-42aa3d00 版本)。

**训练缩放说明(原文):** "actual epoch = 8 * 8 = 64" —— 表示配置文件中的 `total_epochs=8` 经过 8 倍线性缩放后实际等价于 64 epoch。

**学习率步进(原文):** 注释 "# [7] yields higher performance than [6]" 说明 step=[7] 在 Cityscapes 微调上比 step=[6] 表现更好。

---

## 【表格解读】

**原文无表格**。原文全部以代码块形式给出配置示例,未提供任何 markdown/HTML 表格结构。

---

## 【公式解读】

**原文无公式**(LaTeX 或伪代码形式均无)。仅以纯配置项形式描述了 `DeltaXYWHBBoxCoder` 的 `target_means` / `target_stds` 数值列表,以及 `loss_cls` / `loss_bbox` 的类型与权重,但未给出数学表达。

---

## 【关联】

- **上游依赖 → [Tutorial 2: Customize Datasets](customize_dataset.md)** :微调的第一步骤——添加新数据集支持,直接被本文"两个步骤"的第 1 步引用;若新数据集不在 Cityscapes/VOC/WIDER FACE/COCO 之列,必须先按该教程完成数据集注册。

- **预训练权重的来源 → [Model Zoo](../model_zoo.md)** :本文示例的 `load_from` 权重来自 Model Zoo 中的 `mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco` 模型,用户可查阅 Model Zoo 选取其他 backbone/head 组合用于微调。

- **上下文**:本文是 Tutorial 7,基于 Tutorial 2(数据集定制)+ MMDetection V2.0 的 config 继承体系(`_base_`)实现;后续微调得到的模型可直接用于该新数据集的推理与部署。

- **横向关联**:Cityscapes 微调示例与原始 MMDetection 官方教程一致,代码结构遵循 `configs/` 下 `_base_/` 的模块化分层(models / datasets / default_runtime 等子目录)。

---

## 【使用方法】

原文给出的具体启用/配置方式如下:

**① 创建新 config 文件,顶部写入:**
```python
_base_ = [
    '../_base_/models/mask_rcnn_r50_fpn.py',
    '../_base_/datasets/cityscapes_instance.py', '../_base_/default_runtime.py'
]
```

**② 在 `model` 字段覆盖检测头,把类别数改为新数据集的类别数(原文示例 `num_classes=8`):**
```python
model = dict(
    pretrained=None,
    roi_head=dict(
        bbox_head=dict(type='Shared2FCBBoxHead', num_classes=8, ...),
        mask_head=dict(type='FCNMaskHead', num_classes=8, ...)))
```

**③ 调整训练计划(关键超参):**
- `optimizer = dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0001)`(针对 batch_size=8)
- `optimizer_config = dict(grad_clip=None)`
- `lr_config = dict(policy='step', warmup='linear', warmup_iters=500, warmup_ratio=0.001, step=[7])`
- `total_epochs = 8`(实际 64)
- `log_config = dict(interval=100)`

**④ 指定预训练权重:**
```python
load_from = 'http://download.openmmlab.com/mmdetection/v2.0/mask_rcnn/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco_bbox_mAP-0.408__segm_mAP-0.37_20200504_163245-42aa3d00.pth'
```
原文建议:启动训练前先手工下载该权重,避免训练过程中下载导致中断。

**⑤ 训练命令**:原文未涉及具体 train 命令(可参考 MMDetection 标准的 `tools/train.py` 启动方式)。
