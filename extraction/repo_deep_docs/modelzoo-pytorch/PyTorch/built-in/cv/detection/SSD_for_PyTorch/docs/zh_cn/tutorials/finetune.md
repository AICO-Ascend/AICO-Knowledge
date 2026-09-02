# 教程 7: 模型微调

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/zh_cn/tutorials/finetune.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/zh_cn/tutorials/finetune.md

# 一体化深度解读：SSD_for_PyTorch · 模型微调教程（教程 7）

---

## 【定位】

这篇文档解决的是**"如何把 MMDetection V2.0 ModelZoo 中提供的、在 COCO 上预训练的检测模型迁移到新数据集（如 Cityscapes、KITTI）上并获得更好性能"**的问题——即模型微调（finetune）的工程方法与配置改写指南。

---

## 【技术要点】

1. **基础配置继承机制（`_base_`）**：通过 `_base_ = [...]` 列表同时继承模型结构、数据集和运行时三份基础配置，以 Cityscapes + Mask R-CNN 为例，分别从 `../_base_/models/mask_rcnn_r50_fpn.py`、`../_base_/datasets/cityscapes_instance.py`、`../_base_/default_runtime.py` 继承，避免全量重写并减少配置漏洞。

2. **Head 改造（只改类别数）**：保留 `roi_head.bbox_head` 与 `roi_head.mask_head` 的全部结构（`Shared2FCBBoxHead`、`FCNMaskHead`、`DeltaXYWHBBoxCoder` 等），仅把 `num_classes` 改为新数据集的类别数（Cityscapes 示例为 **8**），其余预训练权重可被重用；`pretrained=None` 防止从 backbone 重复加载默认权重。

3. **训练策略差异（finetune ≠ from scratch）**：原文强调微调"通常需要更小的学习率和更少的训练回合"——具体落地为 SGD `lr=0.01`、`max_epochs=8`（远小于 3x schedule）、`warmup_iters=500`、`warmup_ratio=0.001`、`step=[7]`（在第 7 epoch 衰减 lr）。

4. **预训练权重接入（`load_from`）**：通过 `load_from` 指向远程 .pth 文件，在训练开始前下载好权重；示例为 `mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco`，原 COCO 指标 `bbox_mAP-0.408`、`segm_mAP-0.37`。

5. **数据集支持现状**：原文明确说明截至 MMDetection V2.0，配置文件已支持 **VOC、WIDER FACE、COCO、Cityscapes** 四种数据集，其余数据集需自行准备并写配置（衔接教程 2）。

6. **日志与梯度裁剪配置**：`optimizer_config = dict(grad_clip=None)`、`log_config = dict(interval=100)`，表明该微调示例未启用梯度裁剪、日志每 100 iter 输出一次。

---

## 【关键机制与数据】

**整体工作流（数据流/原理）**：
1. 用户从 ModelZoo 选定 COCO 预训练检测器；
2. 按教程 2 为新数据集（如 Cityscapes）添加 dataset wrapper；
3. 新建配置文件，通过 `_base_` 三继承拼出"模型结构 + 数据集 + 运行时"骨架；
4. 改 `roi_head` 中的 `num_classes`（其余结构与权重兼容）；
5. 改 optimizer / lr_config / runner，使用更小的 lr 和更少的 epoch；
6. 通过 `load_from` 拉取预训练 .pth，训练时除 head 末层外其余权重复用。

**性能数据（原文）：**
- 原预训练模型在 COCO 上的精度：`bbox_mAP-0.408`、`segm_mAP-0.37`（来源：文件名后缀 `20200504_163245-42aa3d00.pth`）。
- 微调优化器基准 `batch size = 8`，对应 `lr = 0.01`、`max_epochs = 8`。

**bbox 编解码关键参数（原文）：**
- `target_means = [0., 0., 0., 0.]`、`target_stds = [0.1, 0.1, 0.2, 0.2]`（注意 w/h 维度 std 更大，匹配 COCO 框的尺度特性）。

---

## 【表格解读】

**原文无表格。** 文档以代码块形式给出配置示例（5 段 Python 配置），未出现 markdown 表格、参数表或性能对比表。

---

## 【公式解读】

**原文无公式。** 全文未出现 LaTeX 公式或伪代码形式的目标函数/优化公式。涉及数值关系的均为代码中的列表/字典字面量（如 `step=[7]`、`max_epochs=8`），不构成独立公式。

---

## 【关联】

- **上游/前置 → [教程 2：自定义数据集的方法](customize_dataset.md)**：原文将"为新数据集添加支持"明确指向教程 2，构成本教程的前置依赖。
- **上游资源 → [ModelZoo](../model_zoo.md)**：原文开篇即说明"在 COCO 数据集上预训练的检测器"来自 ModelZoo，本教程是 ModelZoo 模型在新数据集上落地的"使用说明书"，二者构成"模型库 + 微调用法"关系。
- **横向关联**：`_base_/models/mask_rcnn_r50_fpn.py`、`_base_/datasets/cityscapes_instance.py`、`_base_/default_runtime.py` 三份基础配置文件是本教程配置继承的实际来源；本教程未涉及教程 8+（如半监督、蒸馏等），文档自身体系止于"finetune 五步"。

---

## 【使用方法】

**启用方式**：新建一个 python 配置文件，按以下顺序填入五块内容（原文示例）：

1. **基础配置继承**：
   ```python
   _base_ = [
       '../_base_/models/mask_rcnn_r50_fpn.py',
       '../_base_/datasets/cityscapes_instance.py', '../_base_/default_runtime.py'
   ]
   ```

2. **Head 修改（将类别数改为新数据集类别数，Cityscapes 示例 = 8）**：
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
               loss_cls=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0),
               loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=1.0)),
           mask_head=dict(
               type='FCNMaskHead',
               num_convs=4,
               in_channels=256,
               conv_out_channels=256,
               num_classes=8,
               loss_mask=dict(type='CrossEntropyLoss', use_mask=True, loss_weight=1.0))))
   ```

3. **数据集**：直接复用 `_base_` 中已支持的 cityscapes_instance 配置；非 VOC/WIDER FACE/COCO/Cityscapes 数据集需按教程 2 自定义。

4. **训练策略（batch size = 8 时的 finetune 配置）**：
   ```python
   optimizer = dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0001)
   optimizer_config = dict(grad_clip=None)
   lr_config = dict(
       policy='step',
       warmup='linear',
       warmup_iters=500,
       warmup_ratio=0.001,
       step=[7])
   runner = dict(max_epochs=8)
   log_config = dict(interval=100)
   ```
   *原文注：`lr_config` 中的 `max_epochs` 和 `step` 需针对自定义数据集专门调整。*

5. **加载预训练权重**（训练前需手动下载，避免训练时阻塞）：
   ```python
   load_from = 'https://download.openmmlab.com/mmdetection/v2.0/mask_rcnn/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco_bbox_mAP-0.408__segm_mAP-0.37_20200504_163245-42aa3d00.pth'
   ```

**训练命令**：原文未涉及具体启动命令（如 `tools/train.py` 调用方式）。
