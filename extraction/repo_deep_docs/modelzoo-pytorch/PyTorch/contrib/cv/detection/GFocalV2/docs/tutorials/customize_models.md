# Tutorial 4: Customize Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/GFocalV2/docs/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/GFocalV2/docs/tutorials/customize_models.md

# 一体化深度解读:GFocalV2 Tutorial 4 — Customize Models

---

## 【定位】

这篇文档是 MMDetection 框架下的「Tutorial 4: Customize Models」,系统化地说明如何**向检测模型中扩展/自定义 5 类组件**(backbone、neck、head、roi extractor、loss),以 MobileNet(backbone)、PAFPN(neck)、Double Head R-CNN(head)三个具体案例演示"新增文件 → 注册装饰器 → 导入模块 → 修改 config"的标准扩展流程。

---

## 【技术要点】

1. **5 类组件的工程化抽象**:文档将检测模型拆解为 `backbone` / `neck` / `head` / `roi_extractor` / `loss`,每类都有对应的 registry 与 builder,这种「按角色注册」的范式是扩展性的基础。
2. **Registry 装饰器注册机制**:新增组件必须使用 `@BACKBONES.register_module()`(显式调用)、`@NECKS.register`(直接传类)、`@HEADS.register_module()` 等装饰器,被注册后由 `builder` 在 config 解析时按字符串 `type='MobileNet'` 实例化。
3. **两种模块导入方式(互斥)**:① 修改 `mmdet/models/<子目录>/__init__.py` 加 `from .xxx import Xxx`;② 在 config 中写 `custom_imports = dict(imports=['mmdet.models.backbones.mobilenet'], allow_failed_imports=False)`,后者属于"不修改源码"的侵入式注册。
4. **Backbone 必须实现的契约**:继承 `nn.Module`,提供 `__init__`、`forward`(**必须返回 tuple**,适配多尺度特征)、`init_weights(pretrained=None)` 三个方法。
5. **Neck 的典型参数契约**(以 PAFPN 为例):`in_channels / out_channels / num_outs / start_level=0 / end_level=-1 / add_extra_convs=False`,反映 FPN 系 neck 跨层融合的维度约定。
6. **Head 的层级继承与两阶段修改策略**:bbox head 继承 `BBoxHead`,RoI head 继承 `StandardRoIHead` 并仅覆写 `_bbox_forward`,在 `_bbox_forward` 中通过 `self.reg_roi_scale_factor=1.3` 提取两组不同尺度的 RoI 特征(`bbox_cls_feats`、`bbox_reg_feats`)分别送入分类/回归分支。
7. **Loss 的 `weighted_loss` 装饰器**:文档末尾(被截断)指出,为 bbox 回归新增损失 `MyLoss` 时需实现于 `mmdet/models/losses/my_loss.py`,并通过 `weighted_loss` 装饰器实现逐元素加权。

---

## 【关键机制与数据】

### 工作原理与数据流

- **Backbone(以 MobileNet 为例)**:`forward(x)` 接收输入图像张量 → 输出 `tuple`(多尺度特征图)→ 送入 neck / head。`init_weights(pretrained=None)` 支持加载预训练权重。
- **Neck(以 PAFPN 为例)**:`forward(inputs)` 接收来自 backbone 的多尺度特征列表,做跨层融合,输出 `num_outs` 个尺度的特征。原文中给出 PAFPN 典型配置:`in_channels=[256, 512, 1024, 2048]`, `out_channels=256`, `num_outs=5`。
- **Head(以 Double Head R-CNN 为例)**:文档给出 ASCII 数据流图:

  ```
                                        /-> cls
                    /-> shared convs ->
                                        \-> reg
  roi features
                                        /-> cls
                    \-> shared fc    ->
                                        \-> reg
  ```

  即把 RoI 特征分别走两条子网络(convs 共享分支 + fc 共享分支),分别输出 cls/reg。

  在 `DoubleHeadRoIHead._bbox_forward` 中:
  - `bbox_cls_feats = self.bbox_roi_extractor(x[:self.bbox_roi_extractor.num_inputs], rois)` — 正常尺度提取用于 cls
  - `bbox_reg_feats = self.bbox_roi_extractor(..., rois, roi_scale_factor=self.reg_roi_scale_factor)` — 用 `reg_roi_scale_factor` 缩放后用于 reg
  - 两路特征各自经 `shared_head`(若启用)→ `self.bbox_head(bbox_cls_feats, bbox_reg_feats)` → `cls_score, bbox_pred`

  返回 `dict(cls_score, bbox_pred, bbox_feats)`。

### 性能/配置数据(原文)

- Double Head R-CNN 完整 config 中的关键数值(原文逐字给出):
  - `reg_roi_scale_factor=1.3`
  - `num_convs=4`, `num_fcs=2`, `in_channels=256`
  - `conv_out_channels=1024`, `fc_out_channels=1024`
  - `roi_feat_size=7`, `num_classes=80`
  - `bbox_coder=DeltaXYWHBBoxCoder`, `target_means=[0., 0., 0., 0.]`, `target_stds=[0.1, 0.1, 0.2, 0.2]`
  - `reg_class_agnostic=False`
  - `loss_cls=CrossEntropyLoss(use_sigmoid=False, loss_weight=2.0)`
  - `loss_bbox=SmoothL1Loss(beta=1.0, loss_weight=2.0)`

### 上下文继承机制

- 原文:"Since MMDetection 2.0, the config system supports to inherit configs such that the users can focus on the modification."
- 通过 `_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'` 继承基础配置,然后**仅覆写差异部分**(`roi_head` 整段替换)。

### 关于文档截断

- 「Add new loss」一节在 `from ..builde` 处被截断,后面的 Loss 完整示例、装饰器使用、注册导入步骤在原文中不可见;本文档不对未给出内容做猜测。

---

## 【表格解读】

**原文无表格。** 该教程以代码片段 + ASCII 数据流图 + config 字典呈现,未出现 markdown/html 表格结构。

---

## 【公式解读】

**原文无公式(LaTeX/数学公式)。** 唯一结构化表示是 Double Head R-CNN 的 ASCII 数据流分支图,已在【关键机制与数据】节完整保留并解读其数据流。

---

## 【关联】

- **与 backbone/neck/head/loss/roi_extractor 五类 registry 的关联**:本文是 MMDetection 模型扩展的总纲,所有新增组件最终都要挂到对应 registry(`BACKBONES / NECKS / HEADS / ROI_EXTRACTORS / LOSSES`)。
- **与配置系统的关联**:依赖 `_base_` 继承机制(`_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'`)实现增量配置覆写,Double Head R-CNN 示例中的 `bbox_head` 用 `_delete_=True` 删去父 config 中同名字段后再重定义。
- **与既有类的继承关系**:Double Head 案例展示了三层继承链 `BaseRoIHead → StandardRoIHead → DoubleHeadRoIHead`,以及 `BBoxHead → DoubleConvFCBBoxHead`,覆写策略集中在 `_bbox_forward`,其余训练/测试/初始化逻辑全部继承。
- **与 builder 的关联**:所有 `@register_module()` 的类由 `from ..builder import HEADS / build_head / build_roi_extractor` 等 factory 函数按 config 字符串 `type` 装配,这与文档中 `build_head`、`build_assigner`、`build_sampler` 的导入语句形成闭环。
- **与上下游教程的关联**(文末未给出内部链接):Tutorial 4 在 MMDetection 教程体系中通常位于「数据流/config 入门」之后,「自定义数据集/自定义评测/自定义训练流程」之前,本文档侧重模型结构侧的可扩展性。

---

## 【使用方法】

文档给出的可执行配置与命令如下:

1. **新增 backbone** 后,在 config 中:
   ```python
   model = dict(
       backbone=dict(type='MobileNet', arg1=xxx, arg2=xxx),
       ...
   )
   ```
2. **新增 neck** 后,在 config 中:
   ```python
   neck=dict(
       type='PAFPN',
       in_channels=[256, 512, 1024, 2048],
       out_channels=256,
       num_outs=5)
   ```
3. **新增 head** 后,使用 `_base_` 继承 + 局部覆写:
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
4. **避免修改源码的注册方式**:在 config 顶部加 `custom_imports=dict(imports=['mmdet.models.backbones.mobilenet'], allow_failed_imports=False)`(neck / head 案例中同样用法,imports 列表按需增减)。
5. **新增 loss 的文件位置**:`mmdet/models/losses/my_loss.py`,使用 `weighted_loss` 装饰器;**完整调用方式与注册步骤因原文截断未给出,本文不做补全**。
