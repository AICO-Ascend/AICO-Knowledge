# Tutorial 7: Finetuning Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/finetune.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/finetune.md

# 一体化深度解读:Tutorial 7: Finetuning Models

## 【定位】

这篇文档解决**如何将 MMDetection 在 COCO 上预训练的检测器迁移到新数据集(如 Cityscapes)以获得更好性能**的问题,系统阐述在新数据集上对预训练模型进行 finetune 的完整 config 配置流程。

## 【技术要点】

1. **两步法迁移流程**(原文):先按 Tutorial 2 增加新数据集支持,再修改 config;整个 config 需改动 5 个部分——继承 base config、修改 head、修改 dataset、修改训练 schedule、加载预训练权重。

2. **多继承 config 机制**(原文):`_base_` 列表同时继承 `_base_/models/mask_rcnn_r50_fpn.py`(模型结构)、`_base_/datasets/cityscapes_instance.py`(数据集)和 `_base_/default_runtime.py`(运行时),避免重写并减少 bug;用户也可选择完全重写而非继承。

3. **头部仅改 num_classes**(原文):只修改 `roi_head` 中 `bbox_head.num_classes=8` 和 `mask_head.num_classes=8`,即可使预训练权重除最终预测头外大部分被复用(`pretrained=None`),其余超参如 `Shared2FCBBoxHead(in_channels=256, fc_out_channels=1024, roi_feat_size=7)`、`DeltaXYWHBBoxCoder(target_means=[0.,0.,0.,0.], target_stds=[0.1,0.1,0.2,0.2])`、`reg_class_agnostic=False`、`FCNMaskHead(num_convs=4, in_channels=256, conv_out_channels=256)` 均沿用。

4. **finetune 专用训练 schedule**(原文):相比默认 schedule,需要**更小学习率与更少 epoch**——`optimizer=dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0001)`(lr 是为 batch size 8 设置),`optimizer_config=dict(grad_clip=None)`,`lr_config=dict(policy='step', warmup='linear', warmup_iters=500, warmup_ratio=0.001, step=[7])`,`total_epochs=8`(原文标注 actual epoch = 8 × 8 = 64),`log_config=dict(interval=100)`。

5. **预训练权重加载**(原文):通过 `load_from` 指定 URL 加载 `mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco` 在 COCO 上的 checkpoint,原文指标为 **bbox_mAP=0.408、segm_mAP=0.37**;建议提前下载权重以避免训练中下载。

6. **数据集内置支持范围**(原文):MMDetection V2.0 已支持 **VOC、WIDER FACE、COCO、Cityscapes** 四种数据集,其他数据集需按 Tutorial 2 自定义。

## 【关键机制与数据】

- **工作原理(原文):** 预训练检测器在新数据集上 finetune 时,模型大部分权重(backbone、FPN、neck、head 主体)均可复用,仅最终分类/分割预测头因 `num_classes` 变化而需要重新学习,因此配置中设置 `pretrained=None`(避免在 backbone 上重复下载 ImageNet 权重,因 ImageNet 权重已隐含在 load_from 的 COCO checkpoint 中)并通过 `load_from` 加载完整预训练检测器。

- **数据流(原文):** 训练流是 `coco 预训练 Mask R-CNN → 继承 model/dataset/runtime 三个 base config → 改 num_classes=8 → 改 optimizer/lr_config → load_from 加载 COCO 权重 → 在 Cityscapes 上训练 8 个 epoch(以 batch size 8 等效 64 epoch 视角)→ 得到 Cityscapes 上的 finetuned 模型`。

- **性能数据(原文):** 给出的预训练参考 checkpoint 指标为 **`bbox_mAP=0.408`、`segm_mAP=0.37`**(基于 `mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco`),并提及 `step=[7]` 注释 "yields higher performance than [6]",即第 7 epoch 处 step decay 比第 6 epoch 处性能更高。

- **lr 与 batch size 的耦合(原文):** `lr=0.01` 是**显式针对 batch size 8** 设置的(`# lr is set for a batch size of 8`),因此 `total_epochs=8` 经 8 倍换算得到 `actual epoch = 8 × 8 = 64`,提示线性 scaling 关系。

## 【表格解读】

**原文无表格。**(整篇文档以 Python config 代码块形式呈现,无 markdown 表格;但其内部结构等价于一张"配置项 → 关键参数 → 作用"映射,可参照上文【技术要点】第 2、3、4 条整理的参数列表。)

## 【公式解读】

**原文无公式。**(全文未出现 LaTeX 数学式或伪代码公式;唯一的算术表达式为注释中的 `actual epoch = 8 * 8 = 64`,表示 `total_epochs(8)` 与 batch size 等效系数(8)相乘得到线性 scaling 后的等效训练轮数 64。)

## 【关联】

- **上游/前置依赖(链接 `customize_dataset.md`):** 文档明确指出 finetune 第一步必须**先完成 Tutorial 2: Customize Datasets** 的工作——即新增数据集的 `dataset_type`、`data_root`、`train/val/test pipeline` 与 `train_dataloader/val_dataloader` 等配置(若非 Cityscapes/VOC/WIDER FACE/COCO 之内置支持集);本教程的 Cityscapes 示例之所以简化为继承 `_base_/datasets/cityscapes_instance.py`,正是依赖了 Tutorial 2 已建立的自定义机制。

- **下游/模型来源(链接 `../model_zoo.md`):** 文档明示使用 [Model Zoo](../model_zoo.md) 中提供的预训练检测器作为迁移起点,因此本教程是 **Model Zoo(预训练模型池) → Customize Dataset(数据集接入) → Finetune(迁移学习)** 三段流水中的最后一段,典型链为 `_base_` 列表中 `_base_/models/mask_rcnn_r50_fpn.py` 的结构定义 ↔ `load_from` 指向的 Model Zoo checkpoint ↔ `customize_dataset.md` 定义的新数据集。

- **同 config 体系内的横向关联:** `_base_/default_runtime.py` 控制日志、checkpoint、evaluation 等运行时行为,与本文中改动的 `log_config.interval=100` 形成"继承 + 局部覆盖"的关系;`_base_/datasets/cityscapes_instance.py` 中的类别数与本文 `num_classes=8` 需保持一致,否则 head 输出维度会与 dataset label 空间不匹配。

## 【使用方法】

启用方式与命令(原文):

1. **新建 finetune config 文件**,在 `configs/` 下创建(如 `configs/mask_rcnn/mask_rcnn_r50_fpn_cityscapes_finetune.py`),首行通过 `_base_` 列表继承三个 base config:
   ```python
   _base_ = [
       '../_base_/models/mask_rcnn_r50_fpn.py',
       '../_base_/datasets/cityscapes_instance.py', '../_base_/default_runtime.py'
   ]
   ```

2. **修改 head**(将 `num_classes` 改为新数据集类别数,示例为 Cityscapes 的 8 类):
   ```python
   model = dict(
       pretrained=None,
       roi_head=dict(
           bbox_head=dict(type='Shared2FCBBoxHead', in_channels=256,
                          fc_out_channels=1024, roi_feat_size=7,
                          num_classes=8,
                          bbox_coder=dict(type='DeltaXYWHBBoxCoder',
                                          target_means=[0.,0.,0.,0.],
                                          target_stds=[0.1,0.1,0.2,0.2]),
                          reg_class_agnostic=False,
                          loss_cls=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0),
                          loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=1.0)),
           mask_head=dict(type='FCNMaskHead', num_convs=4, in_channels=256,
                          conv_out_channels=256, num_classes=8,
                          loss_mask=dict(type='CrossEntropyLoss', use_mask=True, loss_weight=1.0))))
   ```

3. **修改训练 schedule**(更小 lr + 更少 epoch + linear warmup + step decay):
   ```python
   optimizer = dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0001)
   optimizer_config = dict(grad_clip=None)
   lr_config = dict(policy='step', warmup='linear', warmup_iters=500,
                    warmup_ratio=0.001, step=[7])
   total_epochs = 8
   log_config = dict(interval=100)
   ```

4. **加载预训练权重**(原文建议提前手动下载以避开训练中下载):
   ```python
   load_from = 'http://download.openmmlab.com/mmdetection/v2.0/mask_rcnn/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco_bbox_mAP-0.408__segm_mAP-0.37_20200504_163245-42aa3d00.pth'
   ```

5. **关键约束(原文):** `lr=0.01` 锚定 batch size 8,若实际 batch size 不同需按线性 scaling 规则重新设置;`num_classes` 必须与 `_base_/datasets/cityscapes_instance.py`(或自定义 dataset 配置)中 `classes` 元组长度一致;若新数据集不在 `{VOC, WIDER FACE, COCO, Cityscapes}` 之内,需先按 [Tutorial 2: Customize Datasets](customize_dataset.md) 接入。

(原文未涉及具体 `python tools/train.py ...` 启动命令,仅给出 config 写法,实际训练命令需结合项目 `tools/train.py` 使用,文档本身未明示。)
