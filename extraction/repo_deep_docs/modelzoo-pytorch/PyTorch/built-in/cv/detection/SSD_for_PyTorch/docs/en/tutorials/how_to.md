# Tutorial 11: How to xxx

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/how_to.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/how_to.md

# 一体化深度解读:Tutorial 11: How to xxx

## 【定位】

这篇文档是 MMDetection 生态下「`How to xxx`」式的实践 FAQ/教程集合,聚焦**复用外部主干(mobilenet/efficientnet/timm)接入检测器、数据增强(Mosaic)、主干冻结/解冻切换、新主干通道数探测**四类工程落地问题,为开发者提供可拷贝即用的配置片段与示例代码。

---

## 【技术要点】

1. **跨仓模块复用(Hierarchy Registry)**:MMDet、MMCls、MMSeg 的模型注册表均继承自 MMCV 的根注册表,可直接互相引用对方已实现的模块,而无需在本仓库内复写网络。引用 MMClassification 模块需要在配置中通过 `custom_imports = dict(imports=['mmcls.models'], allow_failed_imports=False)` 显式触发 mmcls 注册逻辑,且要求 `mmcls>=0.20.0`。
2. **MMClassification 主干改造流程**:以 `RetinaNet` + `MobileNetV3-small` 为例,核心三步——① `backbone=dict(_delete_=True, type='mmcls.MobileNetV3', arch='small', out_indices=(3, 8, 11), init_cfg=...)` 替换 `_base_` 中原有 `backbone`;② 调整 `out_indices`;③ `neck=dict(in_channels=[24, 48, 96], start_level=0)` 与主干输出对齐;权重前缀 `prefix='backbone.'` 会被自动剥离以正常加载。
3. **TIMM 主干经 MMCls 包装**:使用 `type='mmcls.TIMMBackbone'` 即可调用 timm 模型,以 `EfficientNet-B1` 为例,设置 `model_name='efficientnet_b1'`、`features_only=True`、`pretrained=True`,并通过 `out_indices=(1, 2, 3, 4)` 与 `neck=dict(in_channels=[24, 40, 112, 320])` 对齐 FPN;该示例配套优化器 `SGD, lr=0.01, momentum=0.9, weight_decay=0.0001`。
4. **Mosaic 增强强制依赖 `MultiImageMixDataset`**:`Mosaic` 必须与 `MultiImageMixDataset` 共同启用;以 Faster R-CNN 为例,`train_pipeline` 顺序为 `Mosaic → RandomAffine(scaling_ratio_range=(0.1, 2), border=(-img_scale[0]//2, -img_scale[1]//2)) → RandomFlip(0.5) → Normalize → Pad(32) → DefaultFormatBundle → Collect`,其中 `RandomAffine` 用于将 Mosaic 后放大 4 倍的图像恢复至 `img_scale=(1333, 800)`;`train_dataset` 必须以 `MultiImageMixDataset` 为类型,内部再嵌套 `CocoDataset` 及最小 `LoadImageFromFile + LoadAnnotations` pipeline。
5. **冻结/解冻主干的两段式方案**:`_base_` 继承 `faster_rcnn_r50_fpn.py` 时,在 `model.backbone` 上设 `frozen_stages=1` 冻结一个 stage;在 `custom_hooks` 中声明 `dict(type="UnfreezeBackboneEpochBasedHook", unfreeze_epoch=1)`;Hook 类的 `before_train_epoch` 检测 `runner.epoch == unfreeze_epoch` 时,根据 `backbone.deep_stages` 判断后分别解冻 `stem` 或 `conv1+norm1`,再解冻 `layer1` 到 `layer{frozen_stages}` 所有参数 `requires_grad = True`,注意文中标注 "Only valid for resnet"。
6. **新主干通道数探测**:通过 `from mmdet.models import ResNet` 单跑一次 `ResNet(depth=18)` + 伪输入 `torch.rand(1, 3, 32, 32)` 即可拿到每阶段 `(C, H, W)`,从而反推 `neck.in_channels`;`ResNet-18` 对应输出四阶段通道依次为 **64 / 128 / 256 / 512**(对应分辨率 `8×8 / 4×4 / 2×2 / 1×1`)。

---

## 【关键机制与数据】

- **工作原理**:本文档展示的不是单一算法的内部数据流,而是「MMDetection 配置系统 + MMCV 注册表 + Hook 机制」共同构成的工程机制——配置继承 (`_base_`) 实现层级覆盖;`custom_imports` 实现跨仓库模块触发注册;`custom_hooks` 切入训练生命周期;`MultiImageMixDataset` 包一层数据 pipeline 实现 Mosaic 复合增强;`UnfreezeBackboneEpochBasedHook` 监听 `before_train_epoch` 切换 `requires_grad`。
- **数据流(Mosaic)**:原始 COCO 训练集 (`instances_train2017.json` + `train2017/`) → `MultiImageMixDataset` 内层 `CocoDataset` 完成 `LoadImageFromFile + LoadAnnotations` → 外层 `train_pipeline` 依次执行 Mosaic 4 拼图 → RandomAffine 缩放回 `1333×800` → RandomFlip → Normalize(`mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375]`) → Pad(size_divisor=32) → DefaultFormatBundle → Collect(`img, gt_bboxes, gt_labels`)。
- **数据流(主干通道探测)**:`torch.rand(1, 3, 32, 32)` → `ResNet(depth=18)` `forward` → 4 级 tuple 输出 → 直接打印 `tuple(level_out.shape)`。
- **性能数据(原文)**:无训练 mAP/速度等基准结果;仅提供 `ResNet-18` 在 `1×3×32×32` 输入下的输出形状 `(1, 64, 8, 8)`、`(1, 128, 4, 4)`、`(1, 256, 2, 2)`、`(1, 512, 1, 1)` 这一用于通道参考的硬数据。
- **预训练权重地址(原文)**:`https://download.openmmlab.com/mmclassification/v0/mobilenet_v3/convert/mobilenet_v3_small-8427ecf0.pth`(MobileNetV3-small 转换权重),原文特别说明「MMCls 主干权重前缀 `backbone.` 会被剥离以正常加载」。

---

## 【表格解读】

**原文无表格。** 全文均以 Python 代码片段、配置 dict、列表等结构呈现参数,未出现任何 markdown/html 表格;通道数等结构化信息以 `print` 输出形式给出,故此处不进行表格还原。

---

## 【公式解读】

**原文无公式。** 文档未涉及任何数学表达式(无 LaTeX、无伪代码形式的 loss/梯度公式);唯一近似的「数值表达式」仅为 Python 字面量(如 `border=(-img_scale[0] // 2, -img_scale[1] // 2)` 用于 Mosaic 后图像恢复尺寸),这属于配置参数而非公式,已在上文技术要点第 4 条中说明其含义。

---

## 【关联】

- **上游机制:MMCV Hierarchy Registry**:本文多次通过 `mmcls.MobileNetV3`、`mmcls.TIMMBackbone` 字符串调用形式落地了 MMCV 的层级注册表能力,原文给出官方解释链接 `https://github.com/open-mmlab/mmcv/blob/master/docs/en/understand_mmcv/registry.md#hierarchy-registry`。
- **上游模块库:MMClassification**:所有跨仓主干调用均依赖 mmcls 的注册机制,原文指向 `https://github.com/open-mmlab/mmclassification/blob/master/docs/en/tutorials/config.md` 作为更全面的 config 使用参考。
- **上游生态:TIMM**:PyTorch Image Models 通过 `mmcls.TIMMBackbone` 包装类间接进入 MMDet,体现 mmcls 作为「timm 适配层」的桥梁作用。
- **下游/配套:`MultiImageMixDataset`**:Mosaic 章节强调该数据集包装类是启用 Mosaic 的必要容器,与 `train_pipeline` 中的 `Mosaic`、`RandomAffine`、`RandomFlip` 等算子协同工作。
- **下游/配套:训练调度 Hook**:解冻主干章节通过 `mmcv.runner.hooks.HOOKS.register_module()` + 自定义 Hook,在 `before_train_epoch` 阶段改写 `requires_grad`,与 MMCV Runner 的 epoch 生命周期事件绑定。
- **配置文件层级**:所有示例均通过 `_base_ = ['../_base_/models/...', '../_base_/datasets/coco_detection.py', '../_base_/schedules/schedule_1x.py', '../_base_/default_runtime.py']` 进行继承,体现 MMDet 的「模型/数据集/调度/运行时」四段式 config 组合范式。

> 内部链接:本文档提示中给出的内部链接为 `(无)`,文末未列出其他内部教程链接,但文中嵌入了两条外部 GitHub 链接(MMCV registry 文档、MMClassification config 文档)。

---

## 【使用方法】

> 原文以「可拷贝的 config 片段 + Python 代码」形式给出,以下是按章节抽取的关键启用方式:

1. **接入 MMClassification 主干(以 RetinaNet + MobileNetV3-small 为例)**
   - 依赖声明:`# please install mmcls>=0.20.0`
   - 触发注册:`custom_imports = dict(imports=['mmcls.models'], allow_failed_imports=False)`
   - 替换主干:`model = dict(backbone=dict(_delete_=True, type='mmcls.MobileNetV3', arch='small', out_indices=(3, 8, 11), init_cfg=dict(type='Pretrained', checkpoint=pretrained, prefix='backbone.')))`
   - 对齐 neck:`neck=dict(in_channels=[24, 48, 96], start_level=0)`

2. **接入 TIMM 主干(以 RetinaNet + EfficientNet-B1 为例)**
   - 配置文件路径(原文标注):`https://github.com/open-mmlab/mmdetection/blob/master/configs/timm_example/retinanet_timm_efficientnet_b1_fpn_1x_coco.py`
   - 主干键值:`type='mmcls.TIMMBackbone', model_name='efficientnet_b1', features_only=True, pretrained=True, out_indices=(1, 2, 3, 4)`
   - neck 对齐:`neck=dict(in_channels=[24, 40, 112, 320])`
   - 优化器:`optimizer = dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0001)`

3. **启用 Mosaic(Faster R-CNN)**
   - 编辑入口:`configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py`
   - 公共参数:`data_root='data/coco/'`, `dataset_type='CocoDataset'`, `img_scale=(1333, 800)`, `pad_val=114.0`
   - 图像归一化:`img_norm_cfg = dict(mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)`
   - `train_dataset` 用 `type='MultiImageMixDataset'`,内部 `dataset` 用 `type=dataset_type`,内层 pipeline 仅保留 `LoadImageFromFile` + `LoadAnnotations(with_bbox=True)`,`filter_empty_gt=False`;最终 `data = dict(train=train_dataset)`。

4. **冻结阶段 + 延迟解冻(Faster R-CNN + ResNet)**
   - 冻结配置:`model = dict(backbone=dict(frozen_stages=1))`
   - Hook 声明:`custom_hooks = [dict(type="UnfreezeBackboneEpochBasedHook", unfreeze_epoch=1)]`
   - 实现位置:`mmdet/core/hook/unfreeze_backbone_epoch_based_hook.py`
   - 类装饰:`@HOOKS.register_module()`,继承 `mmcv.runner.hooks.Hook`,重写 `before_train_epoch(self, runner)`。
   - **原文警告**:`# Only valid for resnet.`

5. **探测新主干通道数**
   - 命令:
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
   - 替换方法:把 `ResNet(depth=18)` 换成自定义主干,其余代码不变即可读出每阶段 (C, H, W) 用于配置 `neck.in_channels`。
