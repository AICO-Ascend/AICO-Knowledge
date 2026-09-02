# Tutorial 4: Customize Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/en/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/en/tutorials/customize_models.md

# 深度解读:Tutorial 4: Customize Models

## 【定位】

本文档是 mmdet3d(基于 PyTorch 的 3D 目标检测框架)教程系列的第 4 篇,系统性阐述如何在该框架内自定义/扩展 6 类模型组件,使得研究者能够将自有方法(Voxel Encoder / Backbone / Neck / Head / RoI Extractor / Loss)以模块化方式接入既有训练与推理流水线。

---

## 【技术要点】

1. **组件 6 分类法**:文档将模型组件划分为 6 大类——encoder(含 voxel layer、voxel encoder、middle encoder)、backbone(常用 FCN,如 ResNet、SECOND)、neck(连接 backbone 与 head,如 FPN、SECONDFPN)、head(任务相关,如 bbox / mask 预测)、RoI extractor(从特征图抽取 RoI 特征,如 H3DRoIHead、PartAggregationROIHead)、loss(head 内用于计算损失的子组件,如 FocalLoss、L1Loss、GHMLoss)。

2. **标准三步接入流程**:每一类新组件的接入都遵循「① 定义类(创建新文件)→ ② 导入并注册模块 → ③ 在 config 中通过 `type` 指定使用」的固定范式。

3. **注册机制**:使用装饰器进行注册,如 `@VOXEL_ENCODERS.register_module()`、`@BACKBONES.register_module()`、`@NECKS.register`、`@HEADS.register_module()`;`forward` 方法约定**必须返回 tuple**(原文:`def forward(self, x):  # should return a tuple`)。

4. **两种导入方式**:方式一,直接修改对应子目录的 `__init__.py`(如 `mmdet3d/models/voxel_encoders/__init__.py` 中加 `from .voxel_encoder import HardVFE`);方式二,在 config 中通过 `custom_imports = dict(imports=['mmdet3d.models.voxel_encoders.HardVFE'], allow_failed_imports=False)` 注入,避免改动原始代码。

5. **SECONDFPN 默认参数**:`in_channels=[128, 128, 256]`、`out_channels=[256, 256, 256]`、`upsample_strides=[1, 2, 4]`、`norm_cfg=dict(type='BN', eps=1e-3, momentum=0.01)`、`upsample_cfg=dict(type='deconv', bias=False)`、`conv_cfg=dict(type='Conv2d', bias=False)`、另含 `use_conv_for_no_stride=False` 开关。

6. **PartA2BboxHead 关键设计**:继承自 `BBoxHead`,需实现 `__init__`、`forward(self, seg_feats, part_feats)` 以及 `loss`、`get_targets` 等方法;loss 默认配置为 `loss_bbox=dict(type='SmoothL1Loss', beta=1.0 / 9.0, loss_weight=2.0)`、`loss_cls=dict(type='CrossEntropyLoss', use_sigmoid=True, reduction='none', loss_weight=1.0)`;norm 配置为 `norm_cfg=dict(type='BN1d', eps=1e-3, momentum=0.01)`。

7. **Base3DRoIHead 抽象接口**:RoI Head 的基类用 `@abstractmethod` 标注了 5 个必须实现的方法——`init_weights`、`init_bbox_head`、`init_mask_head`、`init_assigner_sampler`、`forward_train`(原文:这些方法以 `@abstractmethod` 装饰,作为子类强制契约)。

---

## 【关键机制与数据】

- **原文:** 6 类组件中的「encoder」特指 voxel-based 方法在 backbone 之前的预处理层,包含 voxel layer / voxel encoder / middle encoder 三个子件(典型代表 HardVFE、PointPillarsScatter)。
- **原文:** 「RoI extractor」专责从 backbone-neck 输出的特征图上抽取 RoI 特征,典型如 H3DRoIHead、PartAggregationROIHead。
- **原文:** PartA2 属于 second stage(二阶段)RoI Head;**one-stage** 头请参考 `mmdet3d/models/dense_heads/` 下的实现(原文注释说明 one-stage 因简洁高效,在自动驾驶 3D 检测中更常用)。
- **原文:** 文档以 [SECOND 论文](https://www.mdpi.com/1424-8220/18/10/3337)(Sparsely Embedded Convolutional Detection)与 [PartA2 论文](https://arxiv.org/abs/1907.03670)为示例。
- **原文:** `aug_test` 行为约定——当 `rescale=False` 时,返回的 bboxes 与 masks 匹配 `imgs[0]` 的尺度。
- **原文:** 文档未给出任何训练/推理的量化性能数据(如 mAP、FPS、显存占用等)。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式(文档仅包含 Python 类定义与 config 片段,未出现 LaTeX 或伪代码形式的数学公式)。

---

## 【关联】

- **与教程系列关系**:本文为「Tutorial 4」,前序教程通常涉及 config、数据集、pipeline 等基础使用;后续可能涉及自定义数据集、自定义损失、自定义评测等。
- **与组件层级的耦合**:新增 backbone(例如 SECOND)需要与上游 `voxel_encoder`(如 HardVFE) + `middle_encoder` 配合,下游接 `neck`(如 SECONDFPN)再接 `head`,形成完整 voxel-based 检测流水线。
- **与 Builder 体系耦合**:所有组件统一通过 `mmdet3d/models/builder.py`(及 `mmdet.models.builder` 的 `HEADS`、`build_assigner`、`build_sampler`)注册与构造,新增组件必须保证装饰器名与 config 中 `type` 字符串一致。
- **与 RoI Head 基类耦合**:PartAggregationROIHead 继承自 Base3DRoIHead,后者已实现 `simple_test`、`aug_test` 等通用逻辑与 `with_bbox`、`with_mask` 两个 property,子类的修改重点通常落在 `bbox_forward`。
- **与 dense_heads / roi_heads 模块关系**:one-stage 走 `mmdet3d/models/dense_heads/` 路径,two-stage(以 PartA2 为代表)走 `mmdet3d/models/roi_heads/` 路径(包含 `bbox_heads/parta2_bbox_head.py`、`part_aggregation_roi_head.py`)。
- **文末内部链接**:无。

---

## 【使用方法】

以下流程汇总自原文:

**通用三步法(适用于 encoder / backbone / neck / head / RoI extractor / loss)**:

1. **新建文件**,置于对应目录:
   - voxel encoder:`mmdet3d/models/voxel_encoders/voxel_encoder.py`
   - backbone:`mmdet3d/models/backbones/second.py`
   - neck:`mmdet3d/models/necks/second_fpn.py`
   - bbox head:`mmdet3d/models/roi_heads/bbox_heads/parta2_bbox_head.py`
   - RoI head:`mmdet3d/models/roi_heads/part_aggregation_roi_head.py`

2. **注册并导入**,二选一:
   - 在对应 `__init__.py` 增加 `from .xxx import YYY`;
   - 或在 config 中写 `custom_imports = dict(imports=['mmdet3d.models.<submodule>.<Class>'], allow_failed_imports=False)`。

3. **在 config 中引用**(以 backbone 为例,原文):
   ```python
   model = dict(
       ...
       backbone=dict(type='SECOND', arg1=xxx, arg2=xxx),
       ...
   )
   ```
   对应 neck / voxel_encoder / neck 等键名分别为 `neck`、`voxel_encoder`、`bbox_head` 等。

**RoI Head 使用建议**(原文):如实现 two-stage 头,需继承 `Base3DRoIHead` 并至少覆写 `init_weights`、`init_bbox_head`、`init_mask_head`、`init_assigner_sampler`、`forward_train`;one-stage 头请直接参考 `mmdet3d/models/dense_heads/` 中的示例。
