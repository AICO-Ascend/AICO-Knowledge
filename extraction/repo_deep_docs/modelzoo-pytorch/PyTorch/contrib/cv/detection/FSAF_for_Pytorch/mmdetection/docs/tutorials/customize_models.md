# Tutorial 4: Customize Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/tutorials/customize_models.md

# 一体化深度解读:Tutorial 4: Customize Models

## 【定位】

这篇文档是 mmdetection 框架面向开发者的「模型自定义教程」,系统说明如何在该框架中扩展 5 类核心模型组件(backbone / neck / head / roi extractor / loss),通过注册器(registry)机制与配置(config)系统让用户在不修改框架主干代码的前提下接入自研网络结构或损失函数。

---

## 【技术要点】

1. **组件五分类体系**:backbone(FCN 特征提取,如 ResNet、MobileNet)、neck(backbone 与 head 之间的连接器,如 FPN、PAFPN)、head(任务相关输出,如 bbox 预测、mask 预测)、roi extractor(从特征图抽取 RoI 特征,如 RoI Align)、loss(head 内计算损失的组件,如 FocalLoss、L1Loss、GHMLoss)。

2. **基于装饰器的注册机制**:每个新组件通过 `@BACKBONES.register_module()`、`@NECKS.register_module()`、`@HEADS.register_module()` 等装饰器注册到 mmdetection 的全局注册表,以便 config 中的 `type='XXX'` 字符串能映射到具体类。原文示例:`@BACKBONES.register_module() class MobileNet(nn.Module)`。

3. **两种模块导入方式**:
   - **方式 A**(侵入式):在 `mmdet/models/backbones/__init__.py` 中加入 `from .mobilenet import MobileNet`。
   - **方式 B**(非侵入式,推荐):在 config 中加 `custom_imports = dict(imports=['mmdet.models.backbones.mobilenet'], allow_failed_imports=False)`,从而避免改动框架源码。

4. **head 三件套实现范式**(以 Double Head R-CNN 为例):实现新 head 通常需写三类文件——`bbox_heads/double_bbox_head.py`(继承 `BBoxHead` 的 `DoubleConvFCBBoxHead`,实现 `__init__/init_weights/forward`)、`roi_heads/double_roi_head.py`(继承 `StandardRoIHead` 重写 `_bbox_forward`)、并在 `__init__.py` 或 config `custom_imports` 中注册。

5. **config 继承与 `_delete_=True` 机制**(自 MMDetection 2.0 起):通过 `_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'` 继承基础配置,再用 `_delete_=True` 删除旧字段后注入 `DoubleHeadRoIHead` 与 `DoubleConvFCBBoxHead`,只需关注差异部分。

6. **损失函数扩展**:在 `mmdet/models/losses/my_loss.py` 实现新损失时,使用 `@weighted_loss` 装饰器即可让损失支持逐元素加权(原文此节在截断处中断,具体写法示例不完整)。

---

## 【关键机制与数据】

**注册器-配置解耦工作流**(原文):

```
新组件定义 (.py + @register_module)
        ↓
  两种途径被发现:
   (a) __init__.py 显式 from .xxx import Xxx
   (b) config 中 custom_imports = dict(imports=[...])
        ↓
config 中以 type='Xxx' 字符串引用
        ↓
build_* 函数 (如 build_backbone / build_head) 在 registry 中查找并实例化
```

**Double Head R-CNN 关键数据流**(原文):
- 共享特征经两个分支进入 head:`roi features → shared convs → cls / reg`,以及 `roi features → shared fc → cls / reg`(即双分支结构)。
- 回归分支的特征提取使用 `roi_scale_factor=self.reg_roi_scale_factor` 对 RoI 做放大,而分类分支保持原尺度;config 中设定 `reg_roi_scale_factor=1.3`,即回归 RoI 较分类 RoI 放大 1.3 倍。
- 关键调用顺序(原文 `_bbox_forward`):`bbox_roi_extractor(...)` → `shared_head(...)`(可选) → `bbox_head(cls_feats, reg_feats)` → 返回 `dict(cls_score, bbox_pred, bbox_feats)`。

**config 数值快照**(Double Head R-CNN,原文):
- `num_convs=4, num_fcs=2`(共享 conv/fc 层数)
- `in_channels=256, conv_out_channels=1024, fc_out_channels=1024`(特征维度)
- `roi_feat_size=7, num_classes=80`(对应 COCO 数据集 80 类)
- `target_stds=[0.1, 0.1, 0.2, 0.2]`(bbox 编码 σ,即 xy 比 wh 收敛更快)
- `loss_cls=CrossEntropyLoss(use_sigmoid=False, loss_weight=2.0)`
- `loss_bbox=SmoothL1Loss(beta=1.0, loss_weight=2.0)`

> 原文未给出训练/推理的速度或精度对比数据(如 mAP、FPS),故性能数据一栏无可引用。

---

## 【表格解读】

**原文无表格**。

文档主要以代码块、列表与 ASCII 结构图(`/-> cls \-> reg` 等)形式承载信息,没有提供如「backbone 性能对比」「neck 参数表」之类的表格化内容。

---

## 【公式解读】

**原文无公式**(无 LaTeX 数学式)。

文档中涉及的唯一带数学色彩的内容是 bbox 编码的目标均值与方差 `target_means=[0.,0.,0.,0.]`、`target_stds=[0.1,0.1,0.2,0.2]`,以及 SmoothL1Loss 的 `beta=1.0`、RoI 缩放因子 `reg_roi_scale_factor=1.3` 等数值,均以配置字典呈现,未写成显式公式。

---

## 【关联】

由于用户提供的元信息中标注 `内部链接: (无)`,本文档在本教程体系中**未显式给出与其他文档的内部链接**。但从上下文可推断其上下游关系(基于原文内容):

- **上游/基础依赖**:本教程依赖 [Tutorial 1: Config System](配置文件体系)与 [Tutorial 2: Customize Dataset](自定义数据集)所奠定的注册机制与 config 写法,因为每个新组件最终都以 `type='XXX'` 字符串形式被 config 引用。
- **下游/平行教程**:与本教程同级的「Customize Runtime」(自定义运行时/钩子)、「Customize Losses」(自定义损失的展开篇,本篇已开头但被截断)、「Customize Data Pipelines」互不直接引用,共同覆盖模型开发的横切面。
- **核心 API 依赖**:大量使用 `mmdet.models.builder`(BACKBONES/NECKS/HEADS 注册器)、`mmdet.core`(bbox 编解码、assigner、sampler、bbox2result 等工具),以及父类 `BBoxHead`、`BaseRoIHead`、`StandardRoIHead`、`BBoxTestMixin`、`MaskTestMixin`。
- **学术参考**:Double Head R-CNN 的实现链接到 arXiv `1904.06493`(原文给出 URL: https://arxiv.org/abs/1904.06493)。

---

## 【使用方法】

**启用一个自定义组件的标准流程**(以原文 MobileNet backbone 为例):

1. **定义组件文件**(原文):
   ```
   mmdet/models/backbones/mobilenet.py
   ```
   类结构需包含 `__init__(self, arg1, arg2)`、`forward(self, x)`(返回 tuple)与 `init_weights(self, pretrained=None)`。

2. **注册到注册表**(原文二选一):
   - 在 `mmdet/models/backbones/__init__.py` 添加 `from .mobilenet import MobileNet`,并用 `@BACKBONES.register_module()`。
   - 或在 config 中加入:
     ```python
     custom_imports = dict(
         imports=['mmdet.models.backbones.mobilenet'],
         allow_failed_imports=False)
     ```

3. **在 config 中启用**(原文):
   ```python
   model = dict(
       backbone=dict(type='MobileNet', arg1=xxx, arg2=xxx), ...)
   ```

**启用 Double Head R-CNN 的完整 config**(原文):
```python
_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'
model = dict(
    roi_head=dict(
        type='DoubleHeadRoIHead',
        reg_roi_scale_factor=1.3,
        bbox_head=dict(
            _delete_=True,
            type='DoubleConvFCBBoxHead',
            num_convs=4, num_fcs=2,
            in_channels=256,
            conv_out_channels=1024, fc_out_channels=1024,
            roi_feat_size=7, num_classes=80,
            bbox_coder=dict(type='DeltaXYWHBBoxCoder',
                            target_means=[0.,0.,0.,0.],
                            target_stds=[0.1,0.1,0.2,0.2]),
            reg_class_agnostic=False,
            loss_cls=dict(type='CrossEntropyLoss',
                          use_sigmoid=False, loss_weight=2.0),
            loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=2.0))))
```

**关于 loss 的部分**:原文 "Add new loss" 一节在 `@weighted_loss` 装饰器说明后被截断,`my_loss.py` 的完整写法、注册步骤、config 调用形式**原文未给出**,故此部分启用方式**原文未涉及完整说明**。
