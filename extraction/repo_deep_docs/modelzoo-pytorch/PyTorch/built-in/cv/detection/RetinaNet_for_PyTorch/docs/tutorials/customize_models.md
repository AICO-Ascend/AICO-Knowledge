# Tutorial 4: Customize Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch/docs/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch/docs/tutorials/customize_models.md

# 深度解读: Tutorial 4: Customize Models

## 【定位】

这篇文档是 MMDetection 框架中的"Tutorial 4: Customize Models",目标是指导开发者如何在该框架中自定义/扩展检测模型的各个组件——包括 backbone (骨干网络)、neck (颈部网络)、head (检测头)、roi extractor 与 loss (损失函数),通过注册机制、配置文件继承和模块化设计将新组件接入到现有框架中。

---

## 【技术要点】

1. **模型组件的 5 类划分**: backbone (如 ResNet/MobileNet)、neck (如 FPN/PAFPN)、head (如 bbox/mask prediction)、roi extractor (如 RoI Align)、loss (如 FocalLoss/L1Loss/GHMLoss)。
2. **注册器模式 (Registry Pattern)**: 每个组件类型通过 `@BACKBONES.register_module()`、`@NECKS.register_module()`、`@HEADS.register_module()` 等装饰器注册,实现配置字符串到类的映射。
3. **两种导入新模块方式**:
   - 修改 `__init__.py` 文件直接 `from .mobilenet import MobileNet`;
   - 或在配置文件中使用 `custom_imports = dict(imports=['mmdet.models.backbones.mobilenet'], allow_failed_imports=False)`,避免修改源码。
4. **配置文件驱动**: 通过 `model = dict(backbone=dict(type='MobileNet', arg1=xxx, arg2=xxx), ...)` 在 config 中启用自定义组件。
5. **head 的继承式扩展**: 例如 `DoubleHeadRoIHead` 继承 `StandardRoIHead`,只覆写 `_bbox_forward` 等关键方法,其他逻辑复用基类。
6. **配置文件继承机制**: 自 MMDetection 2.0 起,可通过 `_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'` 复用已有配置,再覆写差异部分。

---

## 【关键机制与数据】

### 1. 工作原理 (基于原文代码骨架还原)

**(a) Backbone 注册流程 (原文)**:
- 在 `mmdet/models/backbones/mobilenet.py` 中定义继承 `nn.Module` 的 `MobileNet` 类;
- 用 `@BACKBONES.register_module()` 装饰;
- 实现三个方法: `__init__(self, arg1, arg2)`、`forward(self, x)` (应返回 tuple)、`init_weights(self, pretrained=None)`。

**(b) Neck 注册流程 (原文)**:
- 在 `mmdet/models/necks/pafpn.py` 中用 `@NECKS.register_module()` 注册 `PAFPN`;
- `__init__` 接受参数: `in_channels, out_channels, num_outs, start_level=0, end_level=-1, add_extra_convs=False`;
- `forward(self, inputs)` 接收多尺度特征输入。

**(c) Head 注册流程 (原文)**: 以 Double Head R-CNN (arxiv: 1904.06493) 为例
- **bbox head**: 在 `mmdet/models/roi_heads/bbox_heads/double_bbox_head.py` 实现 `DoubleConvFCBBoxHead(BBoxHead)`,采用双分支结构 (原文 ASCII 图):
  ```
                    /-> shared convs -> /-> cls
  roi features                          \-> reg
                    \-> shared fc   -> /-> cls
                                        \-> reg
  ```
  - 参数: `num_convs=0, num_fcs=0, conv_out_channels=1024, fc_out_channels=1024, conv_cfg=None, norm_cfg=dict(type='BN')`,并 `kwargs.setdefault('with_avg_pool', True)`;
  - 覆写 `init_weights()` (因 ConvModule 已初始化 conv) 与 `forward(self, x_cls, x_reg)`。
- **RoI Head**: 在 `mmdet/models/roi_heads/double_roi_head.py` 实现 `DoubleHeadRoIHead(StandardRoIHead)`,覆写 `_bbox_forward(self, x, rois)`:
  - 对 cls 分支和 reg 分支分别提取 RoI 特征,reg 分支额外使用 `reg_roi_scale_factor` 缩放因子;
  - 流程: roi_extractor → (可选 shared_head) → bbox_head(x_cls, x_reg) → cls_score, bbox_pred。

**(d) Loss 注册 (原文,被截断)**: 在 `mmdet/models/losses/my_loss.py` 实现 `MyLoss`,通过 `@weighted_loss` 装饰器使损失支持逐元素加权。

### 2. 配置示例中的关键数据 (原文)

| 字段 | 取值 | 来源 |
|---|---|---|
| `_base_` | `'../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'` | Double Head R-CNN config |
| `type` (roi_head) | `'DoubleHeadRoIHead'` | 同上 |
| `reg_roi_scale_factor` | `1.3` | 同上 |
| `num_convs` / `num_fcs` | `4` / `2` | 同上 |
| `in_channels` / `conv_out_channels` / `fc_out_channels` | `256` / `1024` / `1024` | 同上 |
| `roi_feat_size` / `num_classes` | `7` / `80` | 同上 |
| `bbox_coder` | `DeltaXYWHBBoxCoder`, `target_means=[0.,0.,0.,0.]`, `target_stds=[0.1,0.1,0.2,0.2]` | 同上 |
| `reg_class_agnostic` | `False` | 同上 |
| `loss_cls` | `CrossEntropyLoss, use_sigmoid=False, loss_weight=2.0` | 同上 |
| `loss_bbox` | `SmoothL1Loss, beta=1.0, loss_weight=2.0` | 同上 |
| neck `in_channels` / `out_channels` / `num_outs` | `[256,512,1024,2048]` / `256` / `5` | PAFPN config 示例 |

> 原文注: "The arguments are set according to the `__init__` function of each module."——即配置文件中每个字段都对应模块 `__init__` 的形参。

### 3. 修改原 `_delete_` 机制 (原文)

`bbox_head=dict(_delete_=True, type='DoubleConvFCBBoxHead', ...)` 中的 `_delete_=True` 含义(原文虽未明说但示例给出):在配置继承 `_base_` 时,将 `_delete_=True` 设为 True 会丢弃 `_base_` 中同名字段再重新定义,这是 MMDetection 配置系统的标准做法。

---

## 【表格解读】

**原文无表格**。

(配置示例使用 Python dict 字面量展示,非表格形式,但已在上方「关键机制与数据」中以表格形式整理其关键字段取值。)

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

原文无内部链接 (无)。根据原文内容可梳理的逻辑上下游关系:

1. **与注册器 `builder` 的关联**: 所有 `@XXX.register_module()` 装饰器依赖 `mmdet/models/builder.py` 中的 `BACKBONES` / `NECKS` / `HEADS` 注册字典,以及 `build_*` 工厂函数。
2. **与 `BBoxHead` / `StandardRoIHead` 基类的关联**: `DoubleConvFCBBoxHead` 继承 `BBoxHead`;`DoubleHeadRoIHead` 继承 `StandardRoIHead`,复用其 `init_assigner_sampler / init_bbox_head / init_mask_head / forward_train / forward_dummy / simple_test` 等方法,仅覆写 `_bbox_forward`。
3. **与 `BaseRoIHead` / `BBoxTestMixin` / `MaskTestMixin` 的关联**: `StandardRoIHead` 自身通过多继承组合了基类与测试 mixin,Double Head 在此基础上做减法式修改。
4. **与配置继承的关联**: Double Head R-CNN config 通过 `_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'` 继承 Faster R-CNN R50-FPN 1x COCO 配置,只重定义 roi_head 子结构。
5. **与 `mmdet.core` 的关联**: `bbox2result`, `bbox2roi`, `build_assigner`, `build_sampler` 等工具函数被 `StandardRoIHead` 引用。
6. **与 `mmcv` / ConvModule 的关联**: 原文 `init_weights` 中 `conv layers are already initialized by ConvModule` 表明初始化逻辑来自 mmcv 的 ConvModule 封装。

---

## 【使用方法】

### 启用新 backbone (原文: MobileNet 示例)

**步骤 1**: 在 `mmdet/models/backbones/mobilenet.py` 定义 `MobileNet(nn.Module)`,使用 `@BACKBONES.register_module()` 注册,并实现 `__init__(arg1, arg2)` / `forward(x)` / `init_weights(pretrained=None)`。

**步骤 2**: 二选一导入
- 修改 `mmdet/models/backbones/__init__.py` 加 `from .mobilenet import MobileNet`;
- 或在 config 中加 `custom_imports = dict(imports=['mmdet.models.backbones.mobilenet'], allow_failed_imports=False)`。

**步骤 3**: config 启用 (原文):
```python
model = dict(
    ...,
    backbone=dict(
        type='MobileNet',
        arg1=xxx,
        arg2=xxx),
    ...,
)
```

### 启用新 neck (原文: PAFPN 示例)

config 写法 (原文):
```python
neck=dict(
    type='PAFPN',
    in_channels=[256, 512, 1024, 2048],
    out_channels=256,
    num_outs=5)
```

### 启用新 head (原文: Double Head R-CNN 示例)

config 写法 (原文):
```python
_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'
model = dict(
    roi_head=dict(
        type='DoubleHeadRoIHead',
        reg_roi_scale_factor=1.3,
        bbox_head=dict(
            _delete_=True,
            type='DoubleConvFCBBoxHead',
            num_convs=4,
            num_fcs=2,
            in_channels=256,
            conv_out_channels=1024,
            fc_out_channels=1024,
            roi_feat_size=7,
            num_classes=80,
            bbox_coder=dict(
                type='DeltaXYWHBBoxCoder',
                target_means=[0., 0., 0., 0.],
                target_stds=[0.1, 0.1, 0.2, 0.2]),
            reg_class_agnostic=False,
            loss_cls=dict(
                type='CrossEntropyLoss', use_sigmoid=False, loss_weight=2.0),
            loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=2.0))))
```

并需要在 `mmdet/models/bbox_heads/__init__.py` 与 `mmdet/models/roi_heads/__init__.py` 中注册,或使用:
```python
custom_imports = dict(
    imports=['mmdet.models.roi_heads.double_roi_head',
             'mmdet.models.bbox_heads.double_bbox_head'])
```

### 启用新 loss (原文)

在 `mmdet/models/losses/my_loss.py` 中定义 `MyLoss`,使用 `@weighted_loss` 装饰器实现逐元素加权。原文此节在 `from ` 处被截断,后续启用方式 (注册到 losses 注册器与 config 中的 `loss_xxx=dict(type='MyLoss', ...)` 调用方式) **原文未涉及**。
