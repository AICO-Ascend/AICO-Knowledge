# 教程 4: 自定义模型

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/zh_cn/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/zh_cn/tutorials/customize_models.md

# 一体化深度解读：MMDetection 自定义模型教程

---

## 【定位】

这篇文档解决"如何在 MMDetection 框架内不修改核心代码、按统一的注册机制扩展自定义模型组件"的问题,具体覆盖 Backbone / Neck / Head / Loss 四类组件的"定义—注册—配置引用"全流程。

---

## 【技术要点】

1. **模型组件五分类法**:文档开篇将检测模型拆为五类——主干网络(FCN,如 ResNet、MobileNet)、Neck(FPN、PAFPN)、Head(分类/回归/掩码预测)、RoI Extractor(如 RoI Align)、Loss(如 FocalLoss、L1Loss、GHMLoss)。
2. **Registry 注册装饰器机制**:新增组件统一用装饰器模式 `@BACKBONES.register_module()` / `@NECKS` / `@HEADS` / `@LOSSES.register_module()` 注入,`forward` 签名必须返回 tuple(以 backbone 为例)。
3. **三步法导入规范**:每类组件均遵循"① 在指定路径新建文件并装饰注册 → ② 在对应 `__init__.py` 中 `from .xxx import ...` 或用 `custom_imports` 字典 → ③ 在配置文件中以 `type='类名'` 引用"。
4. **`custom_imports` 非侵入式注册**:通过 `dict(imports=['mmdet.models.backbones.mobilenet'], allow_failed_imports=False)` 加入配置文件,可避免修改原始 `__init__.py`。
5. **Head 改造的继承范式**:Double Head R-CNN 例中,新 `DoubleHeadRoIHead` 继承 `StandardRoIHead` 仅覆写 `_bbox_forward`,新 `DoubleConvFCBBoxHead` 继承 `BBoxHead`,并通过 `_delete_=True` 在配置中替换父类默认 head。
6. **`weighted_loss` 装饰器**:用于把函数式损失自动加权重,封装进 `nn.Module` 子类的 `forward` 后,通过 `loss_weight`、`reduction`、`reduction_override`、`avg_factor` 四个参数完成加权聚合。

---

## 【关键机制与数据】

### 工作原理——以 Double Head R-CNN 为例(原文)
- 核心思路:同一 RoI 特征经过**两个分支**(shared convs → cls/reg 与 shared fc → cls/reg),使分类更依赖空间敏感的 conv 特征,回归更依赖位置鲁棒的 fc 特征。
- 在 `_bbox_forward` 中,先用 `bbox_roi_extractor` 提一次 cls 特征,再用同一提取器**以 `roi_scale_factor=self.reg_roi_scale_factor`** 再提一次 reg 特征,从而给两条分支送入不同尺度的 RoI。
- 配置采用继承(`_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'`)+ 局部覆写方式。
- 文档强调"从 MMDetection 2.0 起,配置系统支持继承,用户可专注于修改"。

### 数据流 / 关键数值(原文逐字保留)
- `DoubleHeadRoIHead.__init__` 新增参数:`reg_roi_scale_factor`
- `_bbox_forward` 调用:`bbox_roi_extractor(x[:self.bbox_roi_extractor.num_inputs], rois)` 与同一调用追加 `roi_scale_factor=self.reg_roi_scale_factor`
- 配置层关键数值:
  - `num_convs=4`, `num_fcs=2`, `in_channels=256`, `conv_out_channels=1024`, `fc_out_channels=1024`, `roi_feat_size=7`, `num_classes=80`
  - `bbox_coder`: `DeltaXYWHBBoxCoder`, `target_means=[0., 0., 0., 0.]`, `target_stds=[0.1, 0.1, 0.2, 0.2]`
  - `loss_cls`: `CrossEntropyLoss`, `use_sigmoid=False`, `loss_weight=2.0`
  - `loss_bbox`: `SmoothL1Loss`, `beta=1.0`, `loss_weight=2.0`
  - `reg_roi_scale_factor=1.3`
- `MyLoss` 默认参数:`reduction='mean'`, `loss_weight=1.0`

### 性能数据
原文未涉及性能/精度数字。

---

## 【表格解读】

**原文无表格**。所有数值(例如 `num_convs=4`、`target_stds=[0.1, 0.1, 0.2, 0.2]` 等)均以 Python 配置字典片段形式给出,未以表格组织。

---

## 【公式解读】

**原文无公式**。Loss 实现以伪代码/代码片段呈现(如 `loss = torch.abs(pred - target)`),未出现 LaTeX 数学公式。

---

## 【关联】

原文未在文末给出内部链接(标注:无)。但文档内出现的关键依赖与上下游关系如下,可作为扩展阅读指引:

- **基类继承链**:`MobileNet`(nn.Module) → `BBoxHead`(作为 `DoubleConvFCBBoxHead` 父类) → `BaseRoIHead`(作为 `StandardRoIHead` 父类) → `DoubleHeadRoIHead`(最终自定义 RoI Head);`BBoxTestMixin`、`MaskTestMixin` 作为 RoI Head 的测试混入类。
- **损失族系**:`weighted_loss` 装饰器(utils.py)→ 函数式 `my_loss` → `MyLoss(nn.Module)`;并与内置的 `FocalLoss` / `L1Loss` / `GHMLoss` 同列于 `mmdet/models/losses/`。
- **构造器函数**:文档间接引用 `build_assigner`、`build_sampler`、`build_head`、`build_roi_extractor`(出现于 `StandardRoIHead` 示例代码中)。
- **上游配置模板**:`faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py` 作为 Double Head R-CNN 配置的 `_base_`,体现"基线检测模型 + 局部覆写 Head"的扩展范式。
- **论文出处**:Double Head R-CNN 来源 `https://arxiv.org/abs/1904.06493`(原文给出链接)。

---

## 【使用方法】

### 1. 新增 Backbone(如 MobileNet)
- 文件位置:`mmdet/models/backbones/mobilenet.py`
- 装饰器:`@BACKBONES.register_module()`
- 配置引用:
  ```python
  model = dict(
      backbone=dict(type='MobileNet', arg1=xxx, arg2=xxx), ...)
  ```

### 2. 新增 Neck(如 PAFPN)
- 文件位置:`mmdet/models/necks/pafpn.py`
- 构造参数示例:`in_channels, out_channels, num_outs, start_level=0, end_level=-1, add_extra_convs=False`
- 配置引用:
  ```python
  neck=dict(type='PAFPN', in_channels=[256,512,1024,2048], out_channels=256, num_outs=5)
  ```

### 3. 新增 Head(如 Double Head R-CNN)
- 需新增两个文件:`mmdet/models/roi_heads/bbox_heads/double_bbox_head.py` 与 `mmdet/models/roi_heads/double_roi_head.py`,并分别在 `mmdet/models/bbox_heads/__init__.py` 和 `mmdet/models/roi_heads/__init__.py` 中 import。
- 配置覆写(原文逐字):
  ```python
  roi_head=dict(
      type='DoubleHeadRoIHead',
      reg_roi_scale_factor=1.3,
      bbox_head=dict(
          _delete_=True,
          type='DoubleConvFCBBoxHead',
          num_convs=4, num_fcs=2, in_channels=256,
          conv_out_channels=1024, fc_out_channels=1024,
          roi_feat_size=7, num_classes=80,
          bbox_coder=dict(type='DeltaXYWHBBoxCoder',
                          target_means=[0.,0.,0.,0.],
                          target_stds=[0.1,0.1,0.2,0.2]),
          reg_class_agnostic=False,
          loss_cls=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=2.0),
          loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=2.0)))
  ```

### 4. 新增 Loss(如 MyLoss)
- 文件位置:`mmdet/models/losses/my_loss.py`,函数式实现需加 `@weighted_loss`,类需加 `@LOSSES.register_module()`
- 类构造参数:`reduction='mean'`, `loss_weight=1.0`
- 在 Head 中通过 `loss_bbox=dict(type='MyLoss', loss_weight=1.0)` 引用(原文写为 `loss_bbox=dict(type='MyLoss', loss_weight=1.0))`,末尾多出一个右括号,疑似原文笔误)。

### 5. 通用注册手段(避免改源码)
```python
custom_imports = dict(
    imports=['mmdet.models.backbones.mobilenet'],
    allow_failed_imports=False)
```
或同时导入多个模块:
```python
custom_imports=dict(
    imports=['mmdet.models.roi_heads.double_roi_head',
             'mmdet.models.bbox_heads.double_bbox_head'])
```
加入配置文件即可生效。
