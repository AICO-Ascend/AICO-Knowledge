# 教程 4: 自定义模型

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/zh_cn/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/zh_cn/tutorials/customize_models.md

# 一体化深度解读：MMDetection 自定义模型教程

---

## 【定位】

这篇文档解决**"如何向 MMDetection 框架中按需添加自定义检测组件"**的问题。具体而言，它面向需要在 MMDetection 标准流水线（backbone → neck → head）中替换或新增模块的研究者/工程师，逐类给出 backbone（Neck/Head/Loss 五大类别）的实现、注册与配置三步接入范式，使新组件能够被 MMDetection 的注册器（registry）与构建器（builder）系统自动发现并装配。

---

## 【技术要点】

1. **五大组件分类法**：原文将检测模型显式拆分为五类——**主干网络（backbone，如 ResNet/MobileNet）、Neck（如 FPN/PAFPN）、Head（如 bbox/mask 预测）、RoI 提取器（RoI extractor，如 RoIAlign）、损失（如 FocalLoss/L1Loss/GHMLoss）**，明确每一类的职责边界。

2. **注册器（Registry）机制**：所有自定义组件必须通过装饰器 `@BACKBONES.register_module()`、`@NECKS.register_module()`、`@HEADS.register_module()`、`@LOSSES.register_module()` 注册，从而被 `build_*` 函数以字符串 `type='MobileNet'` 等方式查找与实例化。

3. **三种接入路径**：
   - 直接在对应子包的 `__init__.py` 中添加 `from .xxx import YYY`；
   - 在配置文件中使用 `custom_imports=dict(imports=['mmdet.models.backbones.mobilenet'], allow_failed_imports=False)` 避免修改原始代码；
   - 在配置文件中通过 `model=dict(backbone=dict(type='MobileNet', arg1=xxx, arg2=xxx))` 这种层级字典指定新模块。

4. **PAFPN Neck 关键构造参数**：`in_channels`、`out_channels`、`num_outs`，外加可选的 `start_level=0`、`end_level=-1`、`add_extra_convs=False`；示例配置为 `in_channels=[256, 512, 1024, 2048], out_channels=256, num_outs=5`。

5. **Double Head R-CNN 的双分支结构**：在 `DoubleConvFCBBoxHead` 中，RoI 特征被并行送入两条支路——**shared convs** 与 **shared fc**——分别输出 `cls`（分类）和 `reg`（回归），实现分类/回归任务的解耦表征；`DoubleHeadRoIHead._bbox_forward()` 通过 `self.bbox_roi_extractor(..., roi_scale_factor=self.reg_roi_scale_factor)` 对回归分支使用不同尺度的 RoI 特征（`reg_roi_scale_factor=1.3`）。

6. **损失函数的 `weighted_loss` 装饰器**：通过 `@weighted_loss def my_loss(pred, target)` 把损失函数封装为支持逐样本加权（`weight` 参数）的版本，再以 `MyLoss(nn.Module)` 类封装 `reduction`（`'mean'|'none'|'sum'`，默认 `'mean'`）与 `loss_weight`（默认 `1.0`），并在 `forward()` 中允许 `reduction_override` 临时覆盖聚合方式。

---

## 【关键机制与数据】

**数据流（自定义组件接入流程）**：

```
用户代码 (新建 .py)
    │
    ▼
@*.register_module() 装饰器注册
    │
    ├─── 路径 A：手动修改 mmdet/models/<subpkg>/__init__.py
    │
    └─── 路径 B：配置文件 custom_imports=dict(imports=[...])
    │
    ▼
配置文件 model = dict(backbone/neck/head/loss=dict(type='类名', ...))
    │
    ▼
build_backbone / build_neck / build_head / build_loss (mmdet 中的构建器)
    │
    ▼
由 Runner 装配进完整 detection pipeline
```

**关键性能/配置数据**（原文出现）：

- **Double Head R-CNN 配置关键参数**（原文）：
  - `reg_roi_scale_factor=1.3`
  - `num_convs=4, num_fcs=2, in_channels=256`
  - `conv_out_channels=1024, fc_out_channels=1024, roi_feat_size=7`
  - `num_classes=80`
  - `bbox_coder=DeltaXYWHBBoxCoder`，`target_means=[0., 0., 0., 0.]`，`target_stds=[0.1, 0.1, 0.2, 0.2]`
  - `reg_class_agnostic=False`
  - `loss_cls=CrossEntropyLoss(use_sigmoid=False, loss_weight=2.0)`
  - `loss_bbox=SmoothL1Loss(beta=1.0, loss_weight=2.0)`
  - 基础配置 `_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'`

- **MyLoss 接口**：`reduction='mean'`、`loss_weight=1.0` 为默认；`reduction_override` 限定取值集合 `{None, 'none', 'mean', 'sum'}`；调用时通过 `loss_bbox=dict(type='MyLoss', loss_weight=1.0)` 在 Head 的 `loss_xxx` 字段中替换。

- **框架版本提示**（原文）："从 MMDetection 2.0 版本起，配置系统支持继承配置以使户可以专注于修改"，因此本文示例采用 `_base_ = ...` 继承 `faster_rcnn_r50_fpn_1x_coco.py`，仅覆盖需要修改的字段（其中使用 `_delete_=True` 删除原有 `bbox_head`）。

**Bbox Head 函数钩子列表（原文 StandardRoIHead 列出）**：`init_assigner_sampler`、`init_bbox_head`、`init_mask_head`、`forward_dummy`、`forward_train`、`_bbox_forward`、`_bbox_forward_train`、`_mask_forward_train`、`_mask_forward`、`simple_test`——新增 Head 时通常通过继承 `StandardRoIHead` 并覆写 `_bbox_forward`（如 Double Head）来最小化改动量。

---

## 【表格解读】

**原文无表格。**

> 原文未提供任何参数表、性能对比表或配置项表。所有配置均以 Python 配置字典（`model = dict(...)`）和类构造函数签名形式给出，没有使用 markdown 表格。

---

## 【公式解读】

**原文无公式。**

> 原文未出现 LaTeX 数学公式或伪代码公式。损失部分仅以代码片段形式给出 `my_loss = torch.abs(pred - target)` 这一 L1 风格实现示意，并非显式公式。

---

## 【关联】

- **与配置文件系统的关系**：所有自定义组件的最终启用都依赖 **MMDetection 配置继承机制**（`_base_ = '...'`）。原文明确指出"从 MMDetection 2.0 版本起，配置系统支持继承配置以使户可以专注于修改"，Double Head R-CNN 配置即继承自 `faster_rcnn_r50_fpn_1x_coco.py` 并通过 `_delete_=True` 删除/替换特定子字段（如 `bbox_head`），展示配置继承 + 局部替换的典型用法。

- **与注册器与构建器系统的关系**：本教程是文档其余定制化教程（如自定义数据集、自定义数据流水线、自定义训练策略）的**模型侧**对应篇——只有模型组件被注册后，dataset/pipeline/trainingschedule 才能在配置中通过 `train_cfg`/`test_cfg` 与之拼接。

- **与上游/下游模块的依赖关系**：
  - **上游（被本文档改造的对象）**：`mmdet/models/backbones/`、`mmdet/models/necks/`、`mmdet/models/roi_heads/bbox_heads/`、`mmdet/models/losses/`。
  - **下游（消费本文档产出的组件）**：检测器（detector）通过 `build_detector(cfg.model)` 把 backbone → neck → roi_extractor → roi_head → loss 链式装配；loss 字段（如 `loss_bbox`、`loss_cls`）则被 Head 的 `forward_train`/`_bbox_forward_train` 在计算时调用。
  - **依赖基类**：`BBoxHead`（被 `DoubleConvFCBBoxHead` 继承）、`BaseRoIHead`（被 `StandardRoIHead` 继承，`StandardRoIHead` 再被 `DoubleHeadRoIHead` 继承）构成继承链；`TestMixins`（`BBoxTestMixin`、`MaskTestMixin`）提供推理方法。

- **与外部论文/资源的关系**：Double Head R-CNN 引用了 `https://arxiv.org/abs/1904.06493`（原文内嵌链接）。

- **关联教程序号**：原文标题为"教程 4"，说明本篇位于一个序列化教程体系内，前序教程（教程 1–3）与后续教程（教程 5+）未在原文中以内部链接给出，文档末尾未提供任何内部链接列表。

---

## 【使用方法】

**1. 添加新 Backbone（如 MobileNet）—— 三步**：

```python
# Step 1：新建 mmdet/models/backbones/mobilenet.py
@BACKBONES.register_module()
class MobileNet(nn.Module):
    def __init__(self, arg1, arg2): pass
    def forward(self, x): pass  # 须返回 tuple
```

```python
# Step 2：mmdet/models/backbones/__init__.py 中导入
from .mobilenet import MobileNet
# 或在配置文件中使用：
custom_imports = dict(imports=['mmdet.models.backbones.mobilenet'],
                      allow_failed_imports=False)
```

```python
# Step 3：在配置文件中使用
model = dict(
    backbone=dict(type='MobileNet', arg1=xxx, arg2=xxx),
    ...)
```

**2. 添加新 Neck（如 PAFPN）—— 三步**：

- 新建 `mmdet/models/necks/pafpn.py`，类签名包含 `in_channels, out_channels, num_outs, start_level=0, end_level=-1, add_extra_convs=False`。
- 在 `mmdet/models/necks/__init__.py` 中 `from .pafpn import PAFPN`，或使用 `custom_imports=dict(imports=['mmdet.models.necks.pafpn.py'], allow_failed_imports=False)`。
- 配置：
  ```python
  neck=dict(
      type='PAFPN',
      in_channels=[256, 512, 1024, 2048],
      out_channels=256,
      num_outs=5)
  ```

**3. 添加新 Head（如 Double Head R-CNN）—— 完整配置文件**：

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

> 原文提示：Double Head R-CNN 主要使用了一个新的 `DoubleHeadRoIHead` 和一个新的 `DoubleConvFCBBoxHead`，**参数需要根据每个模块的 `__init__` 函数来设置**。

**4. 添加新 Loss（如 MyLoss）—— 完整流程**：

- 在 `mmdet/models/losses/my_loss.py` 中实现 `@weighted_loss def my_loss(pred, target)` 与 `@LOSSES.register_module() class MyLoss(nn.Module)`，构造参数为 `reduction='mean', loss_weight=1.0`，`forward()` 接受 `pred, target, weight=None, avg_factor=None, reduction_override=None`。
- 在 `mmdet/models/losses/__init__.py` 中：
  ```python
  from .my_loss import MyLoss, my_loss
  ```
  或在配置文件中：
  ```python
  custom_imports=dict(imports=['mmdet.models.losses.my_loss'])
  ```
- 在 Head 组件的 `loss_xxx` 字段中引用：
  ```python
  loss_bbox=dict(type='MyLoss', loss_weight=1.0)
  ```

**命令/启用方式原文未涉及 CLI 命令、shell 脚本或独立启停操作；所有启用都通过编辑配置文件（`.py` config）和 Python 包内 `__init__.py` 完成。**
