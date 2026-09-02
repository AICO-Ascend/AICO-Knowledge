# Tutorial 4: Customize Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/customize_models.md

# Tutorial 4: Customize Models — 一体化深度解读

## 【定位】

这篇文档是 MMDetection (在 modelzoo-pytorch 仓的 SSD_for_PyTorch 路径下) 的 **Tutorial 4**，核心解决「如何向框架内插入/替换自定义模型组件」的问题，把检测模型结构拆解为 5 类可独立扩展的模块（backbone / neck / head / roi_extractor / loss），并通过 MobileNet（backbone）、PAFPN（neck）、Double Head R-CNN（head）三组实例，端到端展示「**写代码 → 注册 → 引入 → 在 config 里组装**」的四步法。

---

## 【技术要点】

1. **五类模型组件划分**（原文第一节列出）
   - `backbone` —— FCN 提特征，例如 ResNet、MobileNet
   - `neck` —— backbone 与 head 之间的中间件，例如 FPN、PAFPN
   - `head` —— 任务相关，例如 bbox 预测、mask 预测
   - `roi_extractor` —— 从特征图上采 RoI 特征，例如 RoI Align
   - `loss` —— head 内用于计算损失的组件，例如 FocalLoss、L1Loss、GHMLoss

2. **新 Backbone 三步法**（以 MobileNet 为例）
   - 在 `mmdet/models/backbones/mobilenet.py` 中定义 `MobileNet(nn.Module)`，用 `@BACKBONES.register_module()` 装饰；`forward` 必须 **return a tuple**
   - 在 `mmdet/models/backbones/__init__.py` 加 `from .mobilenet import MobileNet`，或在 config 中加 `custom_imports = dict(imports=['mmdet.models.backbones.mobilenet'], allow_failed_imports=False)`
   - 在 config 里写 `model = dict(..., backbone=dict(type='MobileNet', arg1=xxx, arg2=xxx), ...)`

3. **新 Neck 三步法**（以 PAFPN 为例）
   - 在 `mmdet/models/necks/pafpn.py` 用 `@NECKS.register_module()` 装饰；`__init__` 接收 `in_channels / out_channels / num_outs / start_level=0 / end_level=-1 / add_extra_convs=False`
   - 通过 `__init__.py` 或 `custom_imports` 引入
   - config 示例：`neck=dict(type='PAFPN', in_channels=[256, 512, 1024, 2048], out_channels=256, num_outs=5)`

4. **新 Head 三步法**（以 Double Head R-CNN [arXiv:1904.06493] 为例）
   - 新增 **bbox head**：在 `mmdet/models/roi_heads/bbox_heads/double_bbox_head.py` 定义 `DoubleConvFCBBoxHead(BBoxHead)`，构造参数为 `num_convs=0 / num_fcs=0 / conv_out_channels=1024 / fc_out_channels=1024 / conv_cfg=None / norm_cfg=dict(type='BN')`；通过 **共享 conv** 与 **共享 fc** 双分支分别输出 cls / reg
   - 新增 **RoI head**：在 `mmdet/models/roi_heads/double_roi_head.py` 定义 `DoubleHeadRoIHead(StandardRoIHead)`，仅覆写 `_bbox_forward`；关键参数 `reg_roi_scale_factor=1.3` 用于给回归分支用更大的 RoI
   - 在 `mmdet/models/bbox_heads/__init__.py` 与 `mmdet/models/roi_heads/__init__.py` 中注册（或 `custom_imports` 一次性导入 `mmdet.models.roi_heads.double_roi_head` 与 `mmdet.models.bbox_heads.double_bbox_head`）

5. **新 Loss 三步法**（原文截断，仅给出骨架）
   - 在 `mmdet/models/losses/my_loss.py` 用 `@LOSSES.register_module()` + `@weighted_loss` 装饰；`weighted_loss` 装饰器使损失可对每个元素加权
   - 文档在 `loss = torch.abs(pre...` 处被截断，未给出 `my_loss` 的完整签名、`__init__`、注册细节与 config 引用

6. **配置继承（自 MMDetection 2.0 起）**
   - `_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'` 作为基配置
   - 用 `_delete_=True` 丢弃基配置中的旧字段后再注入新 head：`bbox_head=dict(_delete_=True, type='DoubleConvFCBBoxHead', num_convs=4, num_fcs=2, in_channels=256, conv_out_channels=1024, fc_out_channels=1024, roi_feat_size=7, num_classes=80, ..., loss_cls=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=2.0), loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=2.0))`
   - 这种"基类继承 + 局部覆写"的模式让用户只关注改动点

---

## 【关键机制与数据】

- **注册器机制**：每个组件类别对应一个 registry（`BACKBONES / NECKS / HEADS / LOSSES`），装饰器在 import 时把类挂到全局表，config 中的 `type` 字符串由 `build_*` 函数查表构造。这是 mm 系列框架 (mmcv / mmdet) 的核心扩展点。
- **`forward` 返回值约束**（原文 backbone 部分）："should return a tuple"——因为 neck/head 通常接收多尺度特征图列表，元组/列表形式保证 backbone 的多级输出可被 FPN/PAFPN 正确接收。
- **Double Head R-CNN 双分支结构**（原文 ASCII 图）：
  ```
                   /-> shared convs -> /-> cls
                                   \-> reg
  roi features
                   /-> shared fc   -> /-> cls
                                   \-> reg
  ```
  即 cls 分支走 conv，reg 分支走 fc；这是该论文的核心创新。
- **回归 RoI 放大**：`reg_roi_scale_factor=1.3` 在 `_bbox_forward` 中作为 `roi_scale_factor` 传给 `bbox_roi_extractor`，使回归分支看到的 RoI 比分类分支大 1.3 倍——这是论文里为对齐回归精度做的 trick。
- **bbox 编解码**：`bbox_coder=dict(type='DeltaXYWHBBoxCoder', target_means=[0., 0., 0., 0.], target_stds=[0.1, 0.1, 0.2, 0.2])`——xy 用 0.1、wh 用 0.2 的归一化尺度。
- **类别设置**：`num_classes=80`、`reg_class_agnostic=False`，对应 COCO 数据集 80 类、非类别无关回归。
- **损失权重**：`loss_cls.loss_weight=2.0`、`loss_bbox.loss_weight=2.0`——两路损失同等加权。
- **`_delete_=True` 机制**：基配置 `faster_rcnn_r50_fpn_1x_coco.py` 中已定义 `bbox_head`，覆写前必须显式 `_delete_` 否则新 `bbox_head` 会与旧的字段冲突。
- **`custom_imports` 机制**（原文两处出现）：通过 config 注入模块路径，避免修改 `__init__.py`；`allow_failed_imports=False` 表示导入失败即报错。

原文未给出任何性能指标（如 mAP、速度）——本节无性能数字可摘录。

---

## 【表格解读】

**原文无表格。**（整篇文档以代码块 + 步骤列表 + ASCII 框图组织，没有任何 `<table>` 或 markdown 表格形式的对比/参数表）。

---

## 【公式解读】

**原文无独立公式块**（无 LaTeX 行、无 `$$` 包围式）。文中仅出现如下数学性符号片段：

1. **`bbox_coder` 中的归一化系数**（出现在 config 块）：
   - `target_means = [0., 0., 0., 0.]` —— 编码时减去的均值，对 Δx、Δy、Δw、Δh 全为 0
   - `target_stds = [0.1, 0.1, 0.2, 0.2]` —— 编码时除以的标准差，位置量用 0.1，尺度量用 0.2
   - 含义：把 (Δx, Δy, Δw, Δh) 分别按 (0.1, 0.1, 0.2, 0.2) 归一化，使训练目标处于相近量级；这是 `DeltaXYWHBBoxCoder` 的标准做法（与 Detectron 同源）。

2. **`SmoothL1Loss` 参数 `beta=1.0`**：控制 L1/L2 转折点；当 |x|<β 时退化为 0.5·x²/β，否则为 |x|−0.5·β。

3. **被截断的 `my_loss`**：原文在 `loss = torch.abs(pre` 处终止，无法还原原式，故略。

由于原文无完整 LaTeX 公式或伪代码公式，按用户要求标注为"原文无完整公式"。

---

## 【关联】

- **上游教程**：文档开篇 "Tutorial 4"，按 Tutorial 1/2/3（无内部链接，但暗示）→ 4 的递进，覆盖 config、模型构建、自定义运行时、数据流之后，本篇聚焦"自定义组件"扩展点。
- **同框架内的关联模块**（原文中明确点名）：
  - `BACKBONES` / `NECKS` / `HEADS` / `LOSSES` registry —— 来自 `mmdet.models.builder` 或 `mmdet.models.roi_heads.builder`，与 Tutorial 2/3 中的 `build_*` 工厂函数配套
  - `BBoxHead` —— 抽象基类，DoubleConvFCBBoxHead 继承自它
  - `BaseRoIHead`、`StandardRoIHead`、`BBoxTestMixin`、`MaskTestMixin` —— RoI 头继承链
  - `bbox2result / bbox2roi / build_assigner / build_sampler` —— `mmdet.core` 工具
  - `weighted_loss` —— 来自 `mmdet.models.losses.utils`，把逐元素 loss 包装成可加权版本
- **横向关联的检测算法（作为扩展范例）**：
  - Faster R-CNN（基配置 `_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'`）
  - FPN / PAFPN（neck 范例）
  - Double Head R-CNN（arXiv:1904.06493，head 范例）
- **上下游关系**：本文是「添加组件」层，向上承接 Tutorial 2（build 机制）与 Tutorial 3（自定义数据集/运行时）；向下用户的扩展会经由 `custom_imports` 或 `__init__.py` 暴露给 config 系统，再由 `train.py` / `test.py` 加载。

---

## 【使用方法】

> 以下汇总原文中所有可执行的启用 / 配置方式。

**A. 添加 backbone（如 MobileNet）**
```python
# 文件 mmdet/models/backbones/mobilenet.py
import torch.nn as nn
from ..builder import BACKBONES

@BACKBONES.register_module()
class MobileNet(nn.Module):
    def __init__(self, arg1, arg2):
        pass
    def forward(self, x):  # should return a tuple
        pass
```
config：
```python
model = dict(
    ...,
    backbone=dict(type='MobileNet', arg1=xxx, arg2=xxx),
    ...)
```
二选一引入：`mmdet/models/backbones/__init__.py` 加 `from .mobilenet import MobileNet`，或 config 加：
```python
custom_imports = dict(
    imports=['mmdet.models.backbones.mobilenet'],
    allow_failed_imports=False)
```

**B. 添加 neck（如 PAFPN）**
文件：`mmdet/models/necks/pafpn.py`，用 `@NECKS.register_module()` 装饰；`__init__` 签名：
```python
def __init__(self, in_channels, out_channels, num_outs,
             start_level=0, end_level=-1, add_extra_convs=False):
```
config：
```python
neck=dict(type='PAFPN',
          in_channels=[256, 512, 1024, 2048],
          out_channels=256,
          num_outs=5)
```

**C. 添加 head（如 Double Head R-CNN）**
需新增两文件并注册：
- `mmdet/models/roi_heads/bbox_heads/double_bbox_head.py`：定义 `DoubleConvFCBBoxHead(BBoxHead)`
- `mmdet/models/roi_heads/double_roi_head.py`：定义 `DoubleHeadRoIHead(StandardRoIHead)`
- 在 `mmdet/models/bbox_heads/__init__.py` 和 `mmdet/models/roi_heads/__init__.py` 中分别 `from .xxx import YYY`，或 config 加：
```python
custom_imports=dict(
    imports=['mmdet.models.roi_heads.double_roi_head',
             'mmdet.models.bbox_heads.double_bbox_head'])
```
完整 config：
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

**D. 添加 loss（如 `MyLoss`）**
文件：`mmdet/models/losses/my_loss.py`，骨架：
```python
import torch
import torch.nn as nn
from ..builder import LOSSES
from .utils import weighted_loss

@weighted_loss
def my_loss(pred, target):
    assert pred.size() == target.size() and target.numel() > 0
    loss = torch.abs(pre...   # 原文在此截断，未给出完整实现
```
具体完整的 `my_loss` 签名、构造与注册方法 —— **原文未涉及**（文档到此被截断）。

---

> **说明**：原文末尾的「Add new loss」章节在代码片段 `loss = torch.abs(pre` 处被截断，因此上述 D 节的完整 `my_loss` 实现、注册装饰器、config 引用方式**均无法从原文中获取**，已按用户要求不做臆造。
