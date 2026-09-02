# 教程 11: How to xxx

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/zh_cn/tutorials/how_to.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/zh_cn/tutorials/how_to.md

# 一体化深度解读: MMDetection "How to xxx" 教程

## 【定位】

这篇文档是 MMDetection 在 modelzoo-pytorch 仓 (`SSD_for_PyTorch/docs/zh_cn/tutorials/how_to.md`) 下的一篇**FAQ 汇总型教程**，收集并解答了使用 MMDetection 时最常见的"如何做"类问题，主要涵盖**骨干网络替换（来自 MMClassification 与 TIMM）、马赛克数据增强、骨干网络的冻结与解冻、新骨干网络通道数的探测**等高频操作场景，目的是为用户提供可直接拷贝修改的配置文件与代码模板。

---

## 【技术要点】

1. **跨库骨干网络复用**：MMDet/MMCls/MMSeg 都继承自 MMCV 的根注册表，因此可在 MMDetection 中直接通过 `type='mmcls.MobileNetV3'` 这样的命名使用 MMClassification 中的骨干网络；前提是 `mmcls>=0.20.0`，并通过 `custom_imports = dict(imports=['mmcls.models'], allow_failed_imports=False)` 触发注册。
2. **TIMM 骨干网络二级封装**：MMClassification 提供了 `TIMMBackbone` 包装器，因此可以在 MMDetection 配置中通过 `type='mmcls.TIMMBackbone', model_name='efficientnet_b1', features_only=True, pretrained=True` 直接使用 `timm` 中的 `EfficientNet-B1`。
3. **骨干权重 prefix 修正**：MMCls 预训练权重的参数名前缀为 `backbone.`，在 MMDet 中加载时必须用 `init_cfg=dict(type='Pretrained', checkpoint=pretrained, prefix='backbone.')` 把该 prefix 去掉。
4. **马赛克数据增强三件套**：使用 `Mosaic` 必须配套 `MultiImageMixDataset`；马赛克后图像放大 4 倍，需用 `RandomAffine`（`scaling_ratio_range=(0.1, 2)`、`border=(-img_scale[0] // 2, -img_scale[1] // 2)`）恢复尺寸；`pad_val=114.0` 与 COCO 标准化 `mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375]` 保持一致。
5. **冻结与按 epoch 解冻骨干网络**：在配置中通过 `backbone=dict(frozen_stages=1)` 冻结第一阶段，再注册 `custom_hooks = [dict(type="UnfreezeBackboneEpochBasedHook", unfreeze_epoch=1)]` 在指定 epoch 解冻所有 `backbone.stem`/`backbone.conv1`/`backbone.norm1`/`backbone.layer{i}` 的参数梯度。
6. **新骨干网络通道数探测**：用 `ResNet(depth=18)` 配合 `torch.rand(1, 3, 32, 32)` 假输入探测输出，得到 `out_indices` 对应的四阶段特征 shape 为 `(1, 64, 8, 8)`、`(1, 128, 4, 4)`、`(1, 256, 2, 2)`、`(1, 512, 1, 1)`，可用于填写 `neck.in_channels`。

---

## 【关键机制与数据】

- **跨库注册机制（层次注册器）**：原文："MMDet、MMCls、MMSeg 中的模型注册表都继承自 MMCV 中的根注册表，允许这些存储库直接使用彼此已经实现的模块。"——这是整个文档能成立的根本原理：所有库共用 MMCV 的 root registry，因此 `mmcls.MobileNetV3`、`mmcls.TIMMBackbone` 这类字符串类型可以直接被 MMDet 解析并实例化，无需 import 实际类；`custom_imports` 的作用就是强制把 `mmcls.models` 加载进来，从而触发 `register_module` 调用。
- **MobileNetV3-small 替换为 RetinaNet 骨干的通道映射**：原文示例把 RetinaNet FPN 的 `in_channels` 由 ResNet 的 `[256, 512, 1024, 2048]` 改成 `[24, 48, 96]`（`start_level=0`），对应 `out_indices=(3, 8, 11)` 取出的三个尺度特征；预训练权重来自 `https://download.openmmlab.com/mmclassification/v0/mobilenet_v3/convert/mobilenet_v3_small-8427ecf0.pth`。
- **EfficientNet-B1 经由 TIMMBackbone 的通道映射**：原文配置 `out_indices=(1, 2, 3, 4)` 取出四层特征，`neck=dict(in_channels=[24, 40, 112, 320])` 与之对应；优化器显式覆盖为 `SGD(lr=0.01, momentum=0.9, weight_decay=0.0001)`。
- **Mosaic 数据流**：原文 pipeline 顺序为 `Mosaic → RandomAffine → RandomFlip → Normalize → Pad(size_divisor=32) → DefaultFormatBundle → Collect`。`MultiImageMixDataset` 作为外层包装，内部的子 dataset 只保留 `LoadImageFromFile` 和 `LoadAnnotations(with_bbox=True)`，mix 操作由外层 `pipeline` 接管；`filter_empty_gt=False` 防止被 mosaic 误过滤。
- **冻结/解冻 hook 机制**：原文 `UnfreezeBackboneEpochBasedHook` 实现的关键路径——`runner.epoch == self.unfreeze_epoch` 触发；通过 `is_module_wrapper` 兼容 `MMDistributedDataParallel` 包装；解冻时按 `backbone.deep_stages` 分支判断，对 `stem`/`conv1`/`norm1` 与 `layer1..layer{frozen_stages}` 全部置 `requires_grad=True` 并切回 `.train()` 模式。
- **通道数探测脚本输出（原文逐字）**：
  ```
  (1, 64, 8, 8)
  (1, 128, 4, 4)
  (1, 256, 2, 2)
  (1, 512, 1, 1)
  ```
  对应 `ResNet(depth=18)` 的 4 个 stage 输出。

---

## 【表格解读】

**原文无表格**。文中所有结构化信息都以 Python 配置代码或伪代码形式呈现，未出现 markdown 表格。

---

## 【公式解读】

**原文无公式**。所有数值关系（如 4 倍放大、边界取负、`start_level=0`）都以代码字面量给出，未用 LaTeX 或伪代码公式表达。

---

## 【关联】

- **与 MMClassification 的关系**：依赖 `mmcls.models` 的注册机制，从而可以使用 `mmcls.MobileNetV3`（原生）和 `mmcls.TIMMBackbone`（TIMM 封装）；文档末尾外链提示读者参考 [MMClassification 配置文档](https://github.com/open-mmlab/mmclassification/blob/master/docs/zh_CN/tutorials/config.md) 以使用更多 backbone。
- **与 MMCV 的关系**：底层注册表来自 MMCV 的根注册器（hierarchical registry），文档外链 [MMCV 文档](https://github.com/open-mmlab/mmcv/blob/master/docs/zh_cn/understand_mmcv/registry.md#%E6%B3%A8%E5%86%8C%E5%99%A8%E5%B1%82%E7%BB%93%E6%9E%84) 解释了这一原理；同时 hook 继承自 `mmcv.runner.hooks.Hook`，`is_module_wrapper` 来自 `mmcv.parallel`。
- **与 TIMM 的关系**：并不直接 import timm，而是通过 `mmcls.TIMMBackbone` 间接使用；并提供完整示例配置 `retinanet_timm_efficientnet_b1_fpn_1x_coco.py`（链接到 MMDetection configs/timm_example 目录）。
- **与上游算法配置的关系**：所有 backbone 替换都基于 `_base_/models/retinanet_r50_fpn.py`（RetinaNet）或 `_base_/models/faster_rcnn_r50_fpn.py`（Faster R-CNN）继承而来，通过 `_delete_=True` 删除原 backbone 字段再覆盖。
- **与 hook 子系统的关系**：`UnfreezeBackboneEpochBasedHook` 需要用户自己在 `mmdet/core/hook/unfreeze_backbone_epoch_based_hook.py` 中实现并通过 `@HOOKS.register_module()` 注册，再由 `custom_hooks` 列表加载。
- **文中给出的可定位示例配置**：`retinanet_timm_efficientnet_b1_fpn_1x_coco.py`（位于 MMDetection configs/timm_example）。
- **任务说明**：本目录为 `SSD_for_PyTorch`，但文档内容本身为通用 MMDetection FAQ，未专门涉及 SSD 训练/推理细节，仅作为教程合集被一并收录。

---

## 【使用方法】

> 以下均按原文给出的最小可工作写法汇总。

### 1. 在 MMDetection 中使用 MMClassification 的骨干网络
- 基础要求：`mmcls>=0.20.0`。
- 在配置中加入 `custom_imports = dict(imports=['mmcls.models'], allow_failed_imports=False)`。
- 用 `_delete_=True` 删除 `_base_` 中 backbone 字段，然后写入：
  ```python
  model = dict(
      backbone=dict(
          _delete_=True,
          type='mmcls.MobileNetV3',
          arch='small',
          out_indices=(3, 8, 11),
          init_cfg=dict(type='Pretrained',
                        checkpoint='https://download.openmmlab.com/mmclassification/v0/mobilenet_v3/convert/mobilenet_v3_small-8427ecf0.pth',
                        prefix='backbone.')),
      neck=dict(in_channels=[24, 48, 96], start_level=0))
  ```

### 2. 在 MMDetection 中通过 MMClassification 使用 TIMM 骨干网络
- 配置核心：
  ```python
  model = dict(
      backbone=dict(
          _delete_=True,
          type='mmcls.TIMMBackbone',
          model_name='efficientnet_b1',
          features_only=True,
          pretrained=True,
          out_indices=(1, 2, 3, 4)),
      neck=dict(in_channels=[24, 40, 112, 320]))
  optimizer = dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0001)
  ```

### 3. 在训练 pipeline 中启用 Mosaic
- 修改 `configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py`：
  - `dataset_type = 'CocoDataset'`、`data_root = 'data/coco/'`、`img_scale=(1333, 800)`；
  - 新建 `train_pipeline`（顺序为 Mosaic → RandomAffine → RandomFlip → Normalize → Pad → DefaultFormatBundle → Collect），其中 `Mosaic(pad_val=114.0)`、`RandomAffine(scaling_ratio_range=(0.1, 2), border=(-img_scale[0] // 2, -img_scale[1] // 2))`、`RandomFlip(flip_ratio=0.5)`、`Pad(size_divisor=32)`；
  - 用 `MultiImageMixDataset` 包装 `CocoDataset`（子 dataset 仅保留 LoadImageFromFile 与 LoadAnnotations(with_bbox=True)，`filter_empty_gt=False`）；
  - 最终通过 `data = dict(train=train_dataset)` 注入训练数据配置。

### 4. 在配置中冻结骨干网络，并在指定 epoch 解冻
- 在模型配置中冻结：`model = dict(backbone=dict(frozen_stages=1))`。
- 在配置中注册解冻 hook：`custom_hooks = [dict(type="UnfreezeBackboneEpochBasedHook", unfreeze_epoch=1)]`。
- 需在 `mmdet/core/hook/unfreeze_backbone_epoch_based_hook.py` 中按原文实现 `UnfreezeBackboneEpochBasedHook(Hook)`，并用 `@HOOKS.register_module()` 注册（按 `runner.epoch == self.unfreeze_epoch` 触发解冻 `backbone.stem`/`backbone.conv1`/`backbone.norm1`/`backbone.layer1..layer{frozen_stages}`）。

### 5. 探测新骨干网络的通道数
- 脚本（以 ResNet18 为例）：
  ```python
  from mmdet.models import ResNet
  import torch
  self = ResNet(depth=18)
  self.eval()
  inputs = torch.rand(1, 3, 32, 32)
  level_outputs = self.forward(inputs)
  for level_out in level_outputs:
      print(tuple(level_out.shape))
  ```
- 将 `ResNet(depth=18)` 替换为待测骨干网络，输出每一阶段的 `(C, H, W)`，据此填入 `out_indices` 与 `neck.in_channels`。
