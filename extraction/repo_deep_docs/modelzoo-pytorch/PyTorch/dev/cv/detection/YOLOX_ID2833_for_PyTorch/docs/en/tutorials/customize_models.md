# Tutorial 4: Customize Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/customize_models.md

# 一体化深度解读:Tutorial 4: Customize Models

## 【定位】

这篇文档解决「如何向 MMDetection 兼容的检测框架(YOLOX_ID2833_for_PyTorch)中按规范添加新的模型组件(backbone / neck / head / roi_extractor / loss)」的问题,即描述「基于注册器(registry)+ 配置(config)系统进行 5 类检测模型组件的可插拔扩展」能力。

---

## 【技术要点】

1. **5 类模型组件划分**:backbone(FCN 特征提取,例 ResNet/MobileNet)、neck(backbone 与 head 之间的桥接,例 FPN/PAFPN)、head(任务相关,例 bbox 预测与 mask 预测)、roi extractor(从特征图提取 RoI 特征,例 RoI Align)、loss(head 内计算损失的组件,例 FocalLoss / L1Loss / GHMLoss)。

2. **基于注册器的模块发现机制**:每个新组件需用装饰器 `@BACKBONES.register_module()` / `@NECKS.register_module()` / `@HEADS.register_module()` / `@LOSSES.register_module()` 注册,然后通过两种方式之一被加载:
   - 写入对应 `__init__.py`(如 `from .mobilenet import MobileNet`);
   - 在 config 中添加 `custom_imports = dict(imports=['mmdet.models.backbones.mobilenet'], allow_failed_imports=False)`,无需改动原始代码。

3. **backbone 接口契约**:`forward(self, x)` 必须返回 **tuple**(多尺度特征图);初始化接受任意参数,如示例 `__init__(self, arg1, arg2)`。

4. **neck 接口契约**:`PAFPN.__init__` 接受 `in_channels, out_channels, num_outs, start_level=0, end_level=-1, add_extra_convs=False`;`forward(self, inputs)` 接受 backbone 输出 tuple 并返回多尺度特征图 tuple。

5. **head 双层结构(roi_head + bbox_head/mask_head)**:bbox head(如 `DoubleConvFCBBoxHead`)继承自 `BBoxHead`,RoI Head(如 `DoubleHeadRoIHead`)继承自 `StandardRoIHead`,通过覆盖 `_bbox_forward` 等方法定制行为;其中 RoI Head 负责组装 extractor + bbox head + mask head 的整体前向/训练流程。

6. **config 继承与 `_delete_=` 替换**:从 MMDetection 2.0 起 config 支持 `_base_` 继承(Double Head R-CNN 示例继承 `../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py`),对要替换的字段用 `_delete_=True` 标记后再写入新的 `type` 与参数,实现「增量修改」。

7. **loss 装饰器 `weighted_loss`**:为每个元素启用加权,需在 `mmdet/models/losses/my_loss.py` 中实现并用 `@weighted_loss` 装饰函数。

---

## 【关键机制与数据】

**工作原理与数据流(以 Double Head R-CNN 为例的端到端流程):**

- **数据流链路**:输入图像 → backbone(提取多尺度特征)→ neck(FPN/PAFPN 融合多尺度)→ RoI Head(`DoubleHeadRoIHead`)内的 **bbox_roi_extractor** 用 RoI Align 从特征图抽 RoI 特征 → 拆分为 `bbox_cls_feats` 与 `bbox_reg_feats` 两条支路(在 `_bbox_forward` 内)→ 若 `self.with_shared_head` 为真则再过 `shared_head` → `bbox_head(x_cls, x_reg)` 输出 `cls_score` 与 `bbox_pred` → loss 计算。
- **关键 RoI 尺度差异**:`DoubleHeadRoIHead._bbox_forward` 中,`bbox_cls_feats` 使用默认尺度提取,`bbox_reg_feats` 则额外传入 `roi_scale_factor=self.reg_roi_scale_factor`,在 config 中设为 `1.3`,这是该论文的核心创新点。
- **bbox_head 内部双分支(原文示意图)**:
  ```
                  /-> shared convs ->  /-> cls
  roi features                       \-> reg
                  \-> shared fc    ->  /-> cls
                                      \-> reg
  ```
  即分别用 conv 层与 FC 层处理分类与回归特征。
- **bbox_head 关键默认参数**(原文):`num_convs=0, num_fcs=0, conv_out_channels=1024, fc_out_channels=1024, conv_cfg=None, norm_cfg=dict(type='BN')`,且通过 `kwargs.setdefault('with_avg_pool', True)` 强制开启 avg pool。
- **示例 config 关键超参**(原文 Double Head R-CNN):`num_convs=4, num_fcs=2, in_channels=256, conv_out_channels=1024, fc_out_channels=1024, roi_feat_size=7, num_classes=80`,`bbox_coder=dict(type='DeltaXYWHBBoxCoder', target_means=[0.,0.,0.,0.], target_stds=[0.1,0.1,0.2,0.2])`,`reg_class_agnostic=False`,`loss_cls=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=2.0)`,`loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=2.0)`。
- **PAFPN config 示例**(原文):`in_channels=[256, 512, 1024, 2048], out_channels=256, num_outs=5`。
- **module 发现优先级**:`__init__.py` 导入优先于 `custom_imports`(原文两种方式任选其一)。

**性能数据**:原文未涉及具体指标(如 mAP、参数量、FLOPs)。

---

## 【表格解读】

**原文无表格。**(全部内容以代码块、配置片段和列表形式呈现,未出现 markdown 表格。)

---

## 【公式解读】

**原文无公式。**(除代码片段中的 loss 实现(`torch.abs(...)` 一类)外,未给出任何 LaTeX 数学表达式或伪代码公式;文档末尾 `my_loss` 示例因原文截断也不完整。)

---

## 【关联】

- **与 config 系统的关联**:整个教程以 config 文件为「装配清单」,与上游文档(自定义数据集 Tutorial 2、自定义 config Tutorial 5 等,虽本文未给出内部链接)共享 `_base_` 继承与 `custom_imports` 机制;`_delete_=True` 替换字段的方式与 config 系统的字段优先级规则紧耦合。
- **与 builder/registry 的关联**:`@BACKBONES/@NECKS/@HEADS/@LOSSES.register_module()` 来自 `mmdet.models.builder`,所有新组件必须经这些注册器才能被 `build_*` 工厂函数识别;RoI Head 内部又通过 `build_head`、`build_roi_extractor` 进行子模块装配。
- **与上下游模块的关联**:
  - **上游** backbone → neck → head 是检测 pipeline;backbone 输出 tuple 必须与 neck `in_channels` 对应(如 `[256,512,1024,2048]` 适配 ResNet-50 FPN)。
  - **下游** loss 接受 head 的预测与 target,通过 `weighted_loss` 装饰器接入加权机制,与 `loss_cls/loss_bbox` 的 `loss_weight` 配置联动。
- **与论文/外部资源的关联**:Double Head R-CNN 引用 `https://arxiv.org/abs/1904.06493`(原文给出链接);backbone 与 loss 示例(MobileNet / MyLoss)只用于演示流程,无外部论文依赖。

---

## 【使用方法】

**1. 添加新 backbone(以 MobileNet 为例)**
- 新建 `mmdet/models/backbones/mobilenet.py`,用 `@BACKBONES.register_module()` 装饰类,实现 `forward` 返回 tuple。
- 二选一注册:`mmdet/models/backbones/__init__.py` 添加 `from .mobilenet import MobileNet`,或在 config 写 `custom_imports=dict(imports=['mmdet.models.backbones.mobilenet'], allow_failed_imports=False)`。
- config 中 `model.backbone=dict(type='MobileNet', arg1=xxx, arg2=xxx)`。

**2. 添加新 neck(以 PAFPN 为例)**
- 新建 `mmdet/models/necks/pafpn.py`,用 `@NECKS.register_module()`。
- 注册二选一(同 backbone)。
- config 中 `neck=dict(type='PAFPN', in_channels=[256,512,1024,2048], out_channels=256, num_outs=5)`。

**3. 添加新 head(以 Double Head R-CNN 为例)**
- 新建 bbox head 文件 `mmdet/models/roi_heads/bbox_heads/double_bbox_head.py`,继承 `BBoxHead`,用 `@HEADS.register_module()`,实现 `forward(self, x_cls, x_reg)` 双输入。
- 新建 RoI Head 文件 `mmdet/models/roi_heads/double_roi_head.py`,继承 `StandardRoIHead`,覆盖 `_bbox_forward` 分别提取 cls/reg 特征。
- 注册二选一:写入 `mmdet/models/bbox_heads/__init__.py` 与 `mmdet/models/roi_heads/__init__.py`,或写 `custom_imports=dict(imports=['mmdet.models.roi_heads.double_roi_head', 'mmdet.models.bbox_heads.double_bbox_head'])`。
- config 通过 `_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'` 继承父配置,再在 `model.roi_head` 中指定 `type='DoubleHeadRoIHead', reg_roi_scale_factor=1.3` 以及内部 `bbox_head=dict(_delete_=True, type='DoubleConvFCBBoxHead', num_convs=4, num_fcs=2, in_channels=256, conv_out_channels=1024, fc_out_channels=1024, roi_feat_size=7, num_classes=80, bbox_coder=..., reg_class_agnostic=False, loss_cls=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=2.0), loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=2.0))`。

**4. 添加新 loss(以 MyLoss 为例)**
- 新建 `mmdet/models/losses/my_loss.py`,使用 `@LOSSES.register_module()` 与 `@weighted_loss` 装饰函数 `my_loss(pred, target)`,断言 `pred.size()==target.size() and target.numel()>0`。(注:原文此处代码在 `torch.abs(pre` 处被截断,未给出完整实现与 config 接入方式,文档信息不完整。)
