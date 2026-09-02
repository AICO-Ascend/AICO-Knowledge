# 教程 7: 模型微调

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/zh_cn/tutorials/finetune.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/zh_cn/tutorials/finetune.md

```markdown
# 教程 7: 模型微调 —— 一体化深度解读

## 【定位】
本教程以 Cityscapes 数据集上的 Mask R-CNN 微调为示例，指导用户如何将 COCO 预训练检测器迁移到自定义数据集，并通过修改 MMDetection V2.0 配置文件的五个部分（继承基础配置 / Head 修改 / 数据集 / 训练策略 / 加载预训练权重）来获得更好的下游任务性能。

## 【技术要点】
1. **基于继承机制复用配置**：新配置通过 `_base_` 列表引用三份基础配置——模型结构 `mask_rcnn_r50_fpn.py`、数据集 `cityscapes_instance.py`、运行设置 `default_runtime.py`，避免重复编写并减少疏漏。
2. **Head 类别数适配**：只需改动 `roi_head.bbox_head.num_classes` 与 `mask_head.num_classes`，即可将 COCO 的 80 类扩展到 Cityscapes 的 8 类；除最后预测 Head 外，预训练权重大部分可继续复用（迁移学习核心收益点）。
3. **bbox Coder 保持 DeltaXYWH**：保留 `target_means=[0.,0.,0.,0.]` 和 `target_stds=[0.1,0.1,0.2,0.2]`（归一化到 COCO 统计尺度），保证预训练 Box 回归层权重的可迁移性。
4. **小 batch 微调超参重写**：`optimizer.lr=0.01`（batch size 8 适用）、`momentum=0.9`、`weight_decay=0.0001`；`lr_config` 改为 linear warmup + step 衰减（`warmup_iters=500`、`warmup_ratio=0.001`、`step=[7]`）；`runner.max_epochs=8`，`log_config.interval=100`。
5. **预训练权重外部加载**：通过 `load_from` 字段指明外部 URL，避免重新训练时下载失败阻塞训练；Mask R-CNN R50-FPN 微调示例对应模型在 COCO 上 `bbox_mAP=0.408`、`segm_mAP=0.37`（数字仅出现在权重文件名中）。

## 【关键机制与数据】
**工作原理（按修改逻辑）**：
- 配置继承：MMDetection V2.0 的 `_base_` 多文件继承机制使新配置只需覆盖差异项，用户也可选择不继承、从头重写。
- Head 适配：bbox_head 完整复刻 COCO 训练时 `Shared2FCBBoxHead` 的 `in_channels=256`、`fc_out_channels=1024`、`roi_feat_size=7`、`reg_class_agnostic=False`；mask_head 采用 `FCNMaskHead`（`num_convs=4`、`conv_out_channels=256`）；损失函数为分类 `CrossEntropyLoss`（`use_sigmoid=False`）、回归 `SmoothL1Loss`（`beta=1.0`）、掩码 `CrossEntropyLoss`（`use_mask=True`），三者 `loss_weight` 均为 `1.0`。
- 训练策略：SGD 优化器在 batch size=8 下 `lr=0.01`；先 500 iter linear warmup 至 `lr×0.001`，第 7 epoch 后 step 衰减；总训练 8 epoch、日志每 100 iter 打印一次。
- 权重加载：`load_from` 直接远程加载 COCO 预训练 checkpoint（Mask R-CNN R50-Caffe-FPN mstrain-poly 3x），权重文件名为 `mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco_bbox_mAP-0.408__segm_mAP-0.37_20200504_163245-42aa3d00.pth`。

**性能数据（原文未给出微调前后对比，仅在权重文件名中保留 COCO 上基线 mAP）**：
- 原文：`bbox_mAP-0.408__segm_mAP-0.37`（出现在 `load_from` URL 的权重文件命名中，属 COCO 预训练基线，非本次微调 Cityscapes 的实测结果）。

## 【表格解读】
原文无表格。

## 【公式解读】
原文无公式。

## 【关联】
- **上游基础 — ModelZoo（`../model_zoo.md`）**：微调所需的预训练权重与 `_base_/models/mask_rcnn_r50_fpn.py` 等配置文件均来自 MMDetection ModelZoo，教程开篇即指出「ModelZoo 中提供的模型用于其他数据集中」。
- **上游前置 — 教程 2 自定义数据集（`customize_dataset.md`）**：进行本教程微调的第一步就是按教程 2 的方法对新数据集添加支持（数据标注格式、类别映射、dataset wrapper 等），再进入本教程的配置修改流程；文档以 `customize_dataset.md` 内部链接明确这一前置依赖。
- **下游影响**：配置继承链末端（`_base_/default_runtime.py`）承接训练运行时参数，决定了 `log_config`、`checkpoint_config`、`evaluation` 等行为；修改 `num_classes` 后所有 `dataset_type`、`classes` 元信息必须保持一致，否则类别数错位会触发训练异常。

## 【使用方法】
- **启用方式**：在 `configs/` 目录下新建一个继承式 Python 配置文件（例如 `configs/cityscapes/mask_rcnn_r50_fpn_cityscapes_finetune.py`），顶部声明 `_base_` 三元组列表，再依次覆盖 `model.roi_head`、`optimizer`、`lr_config`、`runner`、`log_config`、`load_from` 字段。
- **关键配置项**：
  - `_base_`：`['../_base_/models/mask_rcnn_r50_fpn.py', '../_base_/datasets/cityscapes_instance.py', '../_base_/default_runtime.py']`
  - `model.pretrained=None`（避免覆盖外部 `load_from`）
  - `num_classes=8`（Cityscapes）/ mask_head `num_classes=8`
  - `optimizer=dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0001)`、`optimizer_config=dict(grad_clip=None)`
  - `lr_config=dict(policy='step', warmup='linear', warmup_iters=500, warmup_ratio=0.001, step=[7])`
  - `runner=dict(max_epochs=8)`
  - `log_config=dict(interval=100)`
  - `load_from='https://download.openmmlab.com/mmdetection/v2.0/mask_rcnn/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco_bbox_mAP-0.408__segm_mAP-0.37_20200504_163245-42aa3d00.pth'`
- **训练前准备**：按 `customize_dataset.md` 准备并注册新数据集；按 `model_zoo.md` 下载或确认 `load_from` 指明的权重可访问；batch size=8 时直接沿用 `lr=0.01`，若更改 batch size 须按线性缩放规则同步调整学习率并相应修改 `step`/`max_epochs`（原文标注「lr_config 中的 max_epochs 和 step 需要针对自定义数据集进行专门调整」）。
- **运行命令**：原文未涉及（微调执行命令一般在分布式训练教程中给出，本文聚焦配置层）。
```
