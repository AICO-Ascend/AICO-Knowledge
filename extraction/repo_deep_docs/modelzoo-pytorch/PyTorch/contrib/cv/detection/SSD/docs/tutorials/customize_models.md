# Tutorial 4: Customize Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/SSD/docs/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/SSD/docs/tutorials/customize_models.md

# 一体化深度解读：Tutorial 4: Customize Models

## 【定位】

这篇文档是 MMDetection 模型库中面向开发者的「自定义组件教程」,系统讲解如何在 MMDetection 框架内新增或替换 5 类模型组件(backbone / neck / head / roi extractor / loss),通过标准化注册机制与配置文件继承,使新组件以即插即用方式接入整个检测流水线。

---

## 【技术要点】

1. **组件五大分类**: backbone(FCN 特征提取网络,如 ResNet、MobileNet)、neck(backbone 与 head 之间的衔接,如 FPN、PAFPN)、head(任务特定输出,如 bbox / mask 预测)、roi extractor(从特征图提取 RoI 特征,如 RoI Align)、loss(head 内损失计算,如 FocalLoss、L1Loss、GHMLoss)。

2. **注册器模式(Registry)**: 每个组件类型对应一个注册器(`BACKBONES`、`NECKS`、`HEADS`),通过 `@BACKBONES.register_module()`、`@NECKS.register_module()`、`@NECKS.register` 等装饰器把类挂到全局注册表,builder 才能按字符串 `type` 字段查找并实例化。

3. **两种导入策略**:
   - **修改 `__init__.py`**: 添加 `from .mobilenet import MobileNet` 显式导入;
   - **配置式懒导入**: 在 config 中写 `custom_imports = dict(imports=['mmdet.models.backbones.mobilenet'], allow_failed_imports=False)`,无需改动原代码。

4. **配置文件继承(MMDetection 2.0+)**: 通过 `_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'` 复用基础 config,只需在 `model = dict(...)` 中覆写要修改的字段,`_delete_=True` 可删除父配置中的字段。

5. **Backbone 必须遵守的接口约定**: `forward()` 必须返回 tuple(多尺度特征图);需实现 `init_weights(self, pretrained=None)` 用于权重加载。

6. **Head 继承体系**: `BBoxHead` 是 bbox 头基类,`BaseRoIHead` 是 RoI 头基类,`StandardRoIHead` 继承 `BaseRoIHead` 并混合 `BBoxTestMixin`、`MaskTestMixin`,新 RoI 头(如 `DoubleHeadRoIHead`)继承 `StandardRoIHead` 后只需覆写差异部分(如 `_bbox_forward`)。

---

## 【关键机制与数据】

### 数据流(以 Double Head R-CNN 为典型案例)

**(原文)** 整条数据流为:`backbone` → `neck(FPN)` → RoI extractor → 双分支 bbox head → loss。

具体到 `DoubleHeadRoIHead._bbox_forward`(原文逐字):

```python
def _bbox_forward(self, x, rois):
    bbox_cls_feats = self.bbox_roi_extractor(
        x[:self.bbox_roi_extractor.num_inputs], rois)
    bbox_reg_feats = self.bbox_roi_extractor(
        x[:self.bbox_roi_extractor.num_inputs],
        rois,
        roi_scale_factor=self.reg_roi_scale_factor)
    if self.with_shared_head:
        bbox_cls_feats = self.shared_head(bbox_cls_feats)
        bbox_reg_feats = self.shared_head(bbox_reg_feats)
    cls_score, bbox_pred = self.bbox_head(bbox_cls_feats, bbox_reg_feats)
    bbox_results = dict(
        cls_score=cls_score,
        bbox_pred=bbox_pred,
        bbox_feats=bbox_cls_feats)
    return bbox_results
```

**(原文)** 解读:同一组特征 `x` 与 `rois` 被同一 roi_extractor 调用两次,第二次传入 `roi_scale_factor=self.reg_roi_scale_factor`(config 中设为 1.3),从而为分类与回归分支生成不同空间分辨率的 RoI 特征,实现分类/回归解耦。

### 关键数字(原文出现的)

- PAFPN 文档示例配置:`in_channels=[256, 512, 1024, 2048]`、`out_channels=256`、`num_outs=5`。
- DoubleConvFCBBoxHead 默认值:`num_convs=0`、`num_fcs=0`、`conv_out_channels=1024`、`fc_out_channels=1024`;config 实配 `num_convs=4`、`num_fcs=2`、`in_channels=256`、`roi_feat_size=7`、`num_classes=80`、`reg_roi_scale_factor=1.3`。
- 损失权重:`loss_cls` `loss_weight=2.0`、`loss_bbox` `loss_weight=2.0`;`SmoothL1Loss` `beta=1.0`。
- bbox 编解码:`DeltaXYWHBBoxCoder`、`target_means=[0., 0., 0., 0.]`、`target_stds=[0.1, 0.1, 0.2, 0.2]`、`reg_class_agnostic=False`。
- Loss 函数归一化项(隐含于装饰器):`weighted_loss` 装饰器使 loss 可按元素加权。

### Loss 装饰器机制(原文)

**(原文)** "The decorator `weighted_loss` enable the loss to be weighted for each element." —— `weighted_loss` 是逐元素加权的封装器,新 loss 只要用其装饰即可获得权重广播能力。

---

## 【表格解读】

**原文无表格。**(本文档仅含代码块与列表形式的配置/类定义,未提供任何 markdown 表格或结构化参数对照表。)

---

## 【公式解读】

**原文无公式。**(本文档没有显式写出数学公式或伪代码形式的算式,所有逻辑均通过 PyTorch 代码呈现。)

---

## 【关联】

**(原文)**

- **5 类组件的上下游关系**: backbone 提取多尺度特征图 → neck(FPN/PAFPN)做特征融合 → head 完成 bbox/mask 预测 → roi extractor 在 neck 输出特征图上采样 RoI → loss 在 head 内计算梯度信号。
- **继承链**: `BaseRoIHead` ← `StandardRoIHead`(混入 `BBoxTestMixin`、`MaskTestMixin`)← `DoubleHeadRoIHead`;`BBoxHead` ← `DoubleConvFCBBoxHead`。
- **外部论文**: Double Head R-CNN 来源 `https://arxiv.org/abs/1904.06493`。
- **依赖配置基线**: `_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'`,新 config 通过字段覆盖而非重写全部内容。
- **Builder 工具**: `build_head`、`build_roi_extractor`、`build_assigner`、`build_sampler` 均由 `mmdet.core` / `..builder` 提供,负责按注册表把字符串类型转为实例。
- **API 工具**: `bbox2result`、`bbox2roi` 用于在测试阶段把 batched bbox 还原为最终结果。

**(原文未涉及)** SSD 模型本体、具体数据集、性能指标 mAP 等内容,本文档作为通用 MMDetection 教程不涉及 SSD 特有细节。

---

## 【使用方法】

### 新增 backbone 的标准流程(原文)

1. 在 `mmdet/models/backbones/` 下新建文件(如 `mobilenet.py`),定义继承 `nn.Module` 的类,用 `@BACKBONES.register_module()` 装饰;实现 `__init__`、`forward`(返回 tuple)、`init_weights(pretrained=None)`。
2. 二选一导入:
   - 在 `mmdet/models/backbones/__init__.py` 加 `from .mobilenet import MobileNet`;
   - 或在 config 写 `custom_imports = dict(imports=['mmdet.models.backbones.mobilenet'], allow_failed_imports=False)`。
3. config 中使用:
   ```python
   model = dict(
       ...,
       backbone=dict(type='MobileNet', arg1=xxx, arg2=xxx),
       ...)
   ```

### 新增 neck 的标准流程(原文)

1. 新建 `mmdet/models/necks/pafpn.py`,用 `@NECKS.register` 装饰 `PAFPN(nn.Module)`;`__init__` 接受 `in_channels, out_channels, num_outs, start_level=0, end_level=-1, add_extra_convs=False`。
2. 同样两种导入方式(注意原文 necks 示例中 `custom_imports` 列表里写的路径是 `mmdet.models.necks.mobilenet`,与文件名 `pafpn.py` 不一致,属于原文档笔误)。
3. config 写法:
   ```python
   neck=dict(
       type='PAFPN',
       in_channels=[256, 512, 1024, 2048],
       out_channels=256,
       num_outs=5)
   ```

### 新增 head 的标准流程(原文,以 Double Head R-CNN 为例)

1. 新建 `mmdet/models/roi_heads/bbox_heads/double_bbox_head.py`,定义 `DoubleConvFCBBoxHead(BBoxHead)`,实现 `__init__`、`init_weights`、`forward(self, x_cls, x_reg)`。
2. 新建 `mmdet/models/roi_heads/double_roi_head.py`,定义 `DoubleHeadRoIHead(StandardRoIHead)`,通过 `__init__` 接收 `reg_roi_scale_factor` 并覆写 `_bbox_forward`。
3. 在 `mmdet/models/bbox_heads/__init__.py` 和 `mmdet/models/roi_heads/__init__.py` 注册导入,或用 `custom_imports = dict(imports=['mmdet.models.roi_heads.double_roi_head', 'mmdet.models.bbox_heads.double_bbox_head'])`。
4. config 写法(原文逐字):
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

### 新增 loss 的标准流程(原文,文档尾部被截断)

1. 在 `mmdet/models/losses/my_loss.py` 中实现新 loss 类。
2. 用 `weighted_loss` 装饰器装饰,使 loss 支持逐元素加权。
3. (原文截断于 `from ..builde...`,导入与注册细节未给出完整代码,使用者应参考其他 loss 文件的同模式写法完成 `from ..builder import LOSSES` 与 `@LOSSES.register_module()`。)

**(原文未涉及)** 训练启动命令、数据集配置路径、优化器与学习率设置、推理/测试脚本调用等操作细节,本教程文档未提供。
