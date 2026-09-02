# Tutorial 11: How to xxx

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/how_to.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/how_to.md

# 一体化深度解读:MMDetection "How to xxx" 教程文档

## 【定位】
本文档是 MMDetection 系列教程的 "How to" 问题汇总(对应 Tutorial 11),聚焦于跨仓库骨干网络复用(`mmcls`/`timm`)、`Mosaic` 数据增强、骨干网络阶段性冻结/解冻、以及自定义骨干网络的通道探测等高频工程实践问题的可复用解答模板。

## 【技术要点】

1. **跨仓库骨干网络复用机制**:`MMDet` / `MMCls` / `MMSeg` 共享 `MMCV` 根注册表,通过 `custom_imports = dict(imports=['mmcls.models'], allow_failed_imports=False)` 触发 `mmcls` 的 `register_module`,即可在 `MMDet` 配置中以 `type='mmcls.MobileNetV3'` 或 `type='mmcls.TIMMBackbone'` 的方式直接引用 MMClassification 中已实现的模块,无需重复实现;依赖版本要求 `mmcls>=0.20.0`。

2. **`MobileNetV3-small` 替换 RetinaNet 骨干的工程模板**:在 `_base_` 中以 `retinanet_r50_fpn.py` 为父配置,用 `_delete_=True` 删除父配置中的 backbone 字段,然后写入 `arch='small'`、`out_indices=(3, 8, 11)`,并同步修改 `neck=dict(in_channels=[24, 48, 96], start_level=0)`;预训练权重 `pretrained = 'https://download.openmmlab.com/mmclassification/v0/mobilenet_v3/convert/mobilenet_v3_small-8427ecf0.pth'` 通过 `init_cfg=dict(type='Pretrained', checkpoint=pretrained, prefix='backbone.')` 加载,其中 `prefix='backbone.'` 会在加载时自动剥离,使得 MMCls 格式的权重能正常映射到 MMDet 模型。

3. **通过 `mmcls.TIMMBackbone` 接入 timm 的 EfficientNet-B1**:`type='mmcls.TIMMBackbone'`,`model_name='efficientnet_b1'`,`features_only=True`,`pretrained=True`,`out_indices=(1, 2, 3, 4)`,`neck=dict(in_channels=[24, 40, 112, 320])`;该示例配套优化器为 `SGD, lr=0.01, momentum=0.9, weight_decay=0.0001`。

4. **`Mosaic` 增强必须搭配 `MultiImageMixDataset`**:`Mosaic` 会将图像放大 4 倍,需紧跟 `RandomAffine(scaling_ratio_range=(0.1, 2), border=(-img_scale[0] // 2, -img_scale[1] // 2))` 以恢复原始尺寸;典型训练管线参数为 `img_scale=(1333, 800)`、`pad_val=114.0`、`flip_ratio=0.5`、归一化 `mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375]`、`size_divisor=32`,数据声明使用 `type='MultiImageMixDataset'`,并在子 `dataset` 中保留 `CocoDataset` 的 `LoadImageFromFile` / `LoadAnnotations(with_bbox=True)`,且显式 `filter_empty_gt=False`。

5. **基于 Epoch 的骨干解冻 Hook 模式**:在配置层先 `backbone=dict(frozen_stages=1)`,再注册自定义 hook `dict(type='UnfreezeBackboneEpochBasedHook', unfreeze_epoch=1)`;Hook 继承 `mmcv.runner.hooks.Hook`,重写 `before_train_epoch(runner)`,在 `runner.epoch == self.unfreeze_epoch` 时根据 `is_module_wrapper(model)` 解包获取 `model.backbone`,并依据 `deep_stem` 分支选择解冻 `stem`/`conv1`+`norm1`,随后用 `for i in range(1, backbone.frozen_stages + 1): m = getattr(backbone, f'layer{i}')` 对所有冻结层执行 `m.train()` 并将 `param.requires_grad = True`(仅 ResNet 有效)。

6. **新骨干网络通道探测方法**:通过 `mmdet.models.ResNet` 单独构建骨干,`self.eval()`,输入伪张量 `torch.rand(1, 3, 32, 32)`,对 `self.forward(inputs)` 返回的多 stage 输出逐级 `print(tuple(level_out.shape))`;以 `ResNet(depth=18)` 为例,四阶段输出张量形状分别为 `(1, 64, 8, 8)`、`(1, 128, 4, 4)`、`(1, 256, 2, 2)`、`(1, 512, 1, 1)`,对应通道数 `[64, 128, 256, 512]`,可直接用该脚本替换为自定义骨干以获取其输出通道。

## 【关键机制与数据】

**层级注册表(Hierarchy Registry)原理**:MMCV 提供根注册表,各子库继承后形成的层级注册表允许跨仓库按 `mmcls.MobileNetV3` 这种带命名空间的形式调用其他仓库注册的类,这是文档所有跨仓库骨干复用方案的根机制(原文:"The model registry in MMDet, MMCls, MMSeg all inherit from the root registry in MMCV.")。

**MMCls → MMDet 权重映射原理**:MMClassification 预训练权重的 key 前缀为 `backbone.`,而 MMDet 中 backbone 子模块本身已命名为 `backbone`,因此必须用 `init_cfg.prefix='backbone.'` 让 MMDet 在加载时剥离该前缀,使权重能够正确对位(原文:"The pre-trained weights of backbone network in MMCls have prefix='backbone.'. The prefix in the keys will be removed so that these weights can be normally loaded.")。

**Mosaic 数据流原理**:`MultiImageMixDataset` 的作用是包装一个内部数据集(负责基础 `LoadImageFromFile` 与 `LoadAnnotations`)并在其外层应用 `pipeline` 列表(此处即 Mosaic + RandomAffine + RandomFlip + Normalize + Pad + DefaultFormatBundle + Collect);RandomAffine 的 `border=(-img_scale[0] // 2, -img_scale[1] // 2)` 用来补偿 Mosaic 产生的 4 倍放大,使最终输出尺寸回到 `(1333, 800)`(原文:"The image will be enlarged by 4 times after Mosaic processing, so we use affine transformation to restore the image size.")。

**Hook 解冻触发时机**:`before_train_epoch` 在每个 epoch 训练开始前被调用,通过 `runner.epoch` 与预设 `unfreeze_epoch` 比对实现一次性触发,保证冻结→解冻转换只在指定 epoch 边界发生,不会扰乱其余阶段的训练动力学。

**ResNet-18 探测输出**(原文实测):四 stage 输出 shape 分别为 `(1, 64, 8, 8)`、`(1, 128, 4, 4)`、`(1, 256, 2, 2)`、`(1, 512, 1, 1)`,输入尺寸 `1×3×32×32` 经 32× 下采样后与 18 层 ResNet 的 `out_indices` 默认取值一致;用户可借此推断各 stage 通道以正确设置下游 `neck.in_channels`。

## 【表格解读】

**原文无表格**。文档以四个独立的代码示例(配置 + Python)取代了结构化表格,所有数值/参数已在前文【技术要点】逐条列出。

## 【公式解读】

**原文无公式**。无 LaTeX 或伪代码形式公式。

## 【关联】

- **MMCV 根注册表 → 跨仓库复用**:本文档整套 "通过 MMCls 复用骨干" 的方案建立在 MMCV 的 [Hierarchy Registry 机制](https://github.com/open-mmlab/mmcv/blob/master/docs/en/understand_mmcv/registry.md#hierarchy-registry)之上,没有层级注册表则 `type='mmcls.MobileNetV3'` / `type='mmcls.TIMMBackbone'` 这种带命名空间的类无法解析。

- **MMClassification → MMDetection**:timm 包装(`TIMMBackbone`)和 `MobileNetV3` 都并非由 MMDetection 实现,而是从 [MMClassification 文档的 config 教程](https://github.com/open-mmlab/mmclassification/blob/master/docs/en/tutorials/config.md)中获得,MMDetection 仅作为调用方;因此读者若需更丰富的 backbone 列表或字段语义,应回查 MMClassification 文档。

- **`MultiImageMixDataset` ↔ `Mosaic` 增强**:`Mosaic` 是多图混合类增强家族的一员,文档要求必须与 `MultiImageMixDataset` 配合使用——该数据集包装类持有内层 dataset 与外层 pipeline,二者构成"加载→混合→格式化"的级联数据流,任一缺失都将破坏训练管线。

- **`frozen_stages` ↔ `UnfreezeBackboneEpochBasedHook`**:前者是 ResNet 等骨干在 `MMDetection` 中内置的冻结粒度控制参数(取 `[-1, 0, 1, 2, 3, 4]` 等,`-1` 不冻结、`1` 冻结 stem+layer1、以此类推),后者是用户自定义 hook,通过 `custom_hooks` 注入运行器,二者协同实现 "先冻结后解冻" 的微调范式;Hook 中明确写有 "Only valid for resnet.",说明 `deep_stem` 分支与 `conv1`/`norm1`/`layer{i}` 的命名假设是 ResNet 特有的。

- **骨干通道探测 ↔ `neck.in_channels`**:探测脚本(ResNet-18 → `[64, 128, 256, 512]`)输出的通道数正是后续配置 `neck=dict(in_channels=[...])` 与 `out_indices` 选择所依赖的元数据,二者形成 "探测→配置" 的工作闭环。

## 【使用方法】

文档本身就是一组 "How to" 操作模板,所有启用方式均以完整可复制的代码片段给出,核心启用要点如下(均直接摘自原文):

- **跨仓库骨干启用**:
  ```python
  custom_imports = dict(imports=['mmcls.models'], allow_failed_imports=False)
  model = dict(
      backbone=dict(
          _delete_=True,
          type='mmcls.MobileNetV3',  # 或 'mmcls.TIMMBackbone'
          ...))
  ```
  并需满足 `mmcls>=0.20.0`;timm 路线额外需 `features_only=True, pretrained=True`。

- **Mosaic 启用**:在配置中同时声明 `train_pipeline`(以 `Mosaic` 起首,后接 `RandomAffine`/`RandomFlip`/`Normalize`/`Pad`/`DefaultFormatBundle`/`Collect`)以及 `train_dataset=dict(_delete_=True, type='MultiImageMixDataset', dataset=dict(type=dataset_type, ..., filter_empty_gt=False), pipeline=train_pipeline)`,最后用 `data=dict(train=train_dataset)` 重新挂载。

- **阶段性解冻启用**:配置层 `model = dict(backbone=dict(frozen_stages=1))` + `custom_hooks = [dict(type='UnfreezeBackboneEpochBasedHook', unfreeze_epoch=1)]`;运行时需要在 `mmdet/core/hook/unfreeze_backbone_epoch_based_hook.py` 实现 `UnfreezeBackboneEpochBasedHook`(以 `@HOOKS.register_module()` 注册、`Hook` 基类、`before_train_epoch` 重写)。

- **新骨干通道探测**:直接执行 `python -c` 形式的脚本(`ResNet(depth=18)` → 替换为自定义骨干),输入 `torch.rand(1, 3, 32, 32)`,读取 `level_outputs` 各 stage 的 `shape` 即可获得通道列表;若输入尺寸变更,需同步修改 `torch.rand` 的空间维度以避免最后 stage 输出尺寸过小。
