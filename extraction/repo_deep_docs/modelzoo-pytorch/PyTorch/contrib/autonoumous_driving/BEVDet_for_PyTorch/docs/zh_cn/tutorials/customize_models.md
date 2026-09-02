# 教程 4: 自定义模型

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/zh_cn/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/zh_cn/tutorials/customize_models.md

# 教程 4：自定义模型 — 一体化深度解读

## 【定位】
本篇文档解决的是"如何在 mmdet3d（OpenMMLab 3D 检测框架）下，基于注册器（registry）+ 配置文件（config）模式，向现有 3D 检测模型流水线中**新增或替换任意一类组成模块**（encoder / backbone / neck / head / RoI extractor / loss）"的问题，描述的是一套面向研究人员的**模块化扩展能力**。

---

## 【技术要点】

1. **模型被显式划分为 6 类组件**：encoder（含 voxel layer、voxel encoder、middle encoder，如 HardVFE、PointPillarsScatter）、backbone（FCN 类，如 ResNet、SECOND）、neck（FPN、SECONDFPN）、head（bbox/mask 预测）、RoI extractor（H3DRoIHead、PartAggregationROIHead）、loss（FocalLoss、L1Loss、GHMLoss）。
2. **注册机制是核心抽象**：每类组件对应一个注册器 decorator（`@VOXEL_ENCODERS.register_module()`、`@BACKBONES.register_module()`、`@NECKS.register`、`@HEADS.register_module()` 等），类必须继承 `nn.Module` 或 `BaseModule`，`forward` 须返回 `tuple`。
3. **两种导入新模块的方式**：
   - 源码式：在对应包的 `__init__.py` 中加 `from .xxx import XXX`；
   - 无侵入式：在 config 中用 `custom_imports = dict(imports=['mmdet3d.models.xxx.XXX'], allow_failed_imports=False)`，避免改动源码。
4. **以 SECONDFPN 为例的 neck 默认参数**：`in_channels=[128, 128, 256]`、`out_channels=[256, 256, 256]`、`upsample_strides=[1, 2, 4]`、`norm_cfg=dict(type='BN', eps=1e-3, momentum=0.01)`、`upsample_cfg=dict(type='deconv', bias=False)`、`conv_cfg=dict(type='Conv2d', bias=False)`、`use_conv_for_no_stride=False`；而在配置示例中常被改写为 `in_channels=[64, 128, 256]` / `out_channels=[128, 128, 128]`。
5. **PartA2 BBox Head 的关键默认超参**：`dropout_ratio=0.1`、`roi_feat_size=14`、`with_corner_loss=True`、`bbox_coder=dict(type='DeltaXYZWLHRBBoxCoder')`、`conv_cfg=dict(type='Conv1d')`、`norm_cfg=dict(type='BN1d', eps=1e-3, momentum=0.01)`、`loss_bbox=dict(type='SmoothL1Loss', beta=1.0/9.0, loss_weight=2.0)`、`loss_cls=dict(type='CrossEntropyLoss', use_sigmoid=True, reduction='none', loss_weight=1.0)`。
6. **Head 分单阶段/双阶段两套体系**：单阶段 head 参考 `mmdet3d/models/dense_heads/`，强调"简单高效、广泛用于自动驾驶 3D 检测"；双阶段 RoI Head（如 PartAggregationROIHead）继承 `Base3DRoIHead`，需实现 `init_weights` / `init_bbox_head` / `init_mask_head` / `init_assigner_sampler` / `forward_train` 等抽象方法，并覆写 `_bbox_forward`。

---

## 【关键机制与数据】

**工作原理（注册 → 导入 → 装配 → 配置）四步法**（原文表述）：
- Step 1 *定义*：在 `mmdet3d/models/<子目录>/<文件名>.py` 中以相应 decorator 注册一个新类；
- Step 2 *导入*：二选一——改 `__init__.py` 或写 `custom_imports`；
- Step 3 *装配*：在 config 的 `model = dict(...)` 字典里，用 `type='ClassName'` 字段替换或新增对应键（如 `voxel_encoder` / `backbone` / `neck` / `bbox_head` 等）。

**数据流**（原文未画图，仅由代码隐含）：voxel encoder / backbone / neck / RoI extractor / head 在 config 中以字典嵌套方式串成一条流水线；运行时由 `build_*` 系列 builder 根据 `type` 字段解析类并实例化。

**性能数据**：原文未给出任何精度、时延、显存数字，**所有性能留空**（不臆造）。

---

## 【表格解读】

**原文无表格。**

文档以代码块（注册装饰器、类骨架、配置字典）作为主要表达方式，没有任何 `<table>`、Markdown 表格或 ASCII 表格出现。所有结构化信息都以 Python dict / list 字面量散落在代码片段中。

---

## 【公式解读】

**原文无公式。**

文档未出现任何 LaTeX 行内公式、独立公式块、伪代码公式或数学符号表达式。"beta=1.0 / 9.0"、"eps=1e-3"、"momentum=0.01"、"loss_weight=2.0"、"loss_weight=1.0"、"reduction='none'" 等均为 **Python 字面量参数**，不是数学公式。

---

## 【关联】

1. **与 mmdet3d 模型库其他模块的关系**：
   - **BBoxHead（基类）**：PartA2BboxHead 直接继承自 `mmdet3d/models/roi_heads/bbox_heads/bbox_head.py` 中的 `BBoxHead`，意味着自定义 bbox head 至少要复用其共享 fc / 损失分支逻辑。
   - **Base3DRoIHead**：PartAggregationROIHead 继承自该类（位于 `mmdet3d/models/roi_heads/base_3droi_head.py`），享受其抽象方法骨架 + `simple_test` / `aug_test` 默认实现以及 `with_bbox` / `with_mask` 属性。
   - **builder 子系统**：`build_head`、`build_roi_extractor`、`build_assigner`、`build_sampler`（来自 `mmdet.core` 与 `mmdet3d.core`）是 PartAggregationROIHead 内部构造子模块所依赖的工厂函数。
   - **mmdet.core 复用**：`from mmdet.core import build_assigner, build_sampler`、`from mmdet.models import HEADS` 显示本 head 与 2D 检测框架 mmdet 共用 assigner / sampler / head 注册器，**形成 2D-3D 共享底座**。

2. **与上下文的上下游关系**：
   - 上游：`mmdet3d/models/voxel_encoders/`、`mmdet3d/models/backbones/`、`mmdet3d/models/necks/` 提供特征；本教程展示如何替换或扩展这些特征产生阶段。
   - 下游：`mmdet3d/models/dense_heads/`（单阶段）与 `mmdet3d/models/roi_heads/`（双阶段）共同消费 neck 输出，构成最终的检测预测。
   - 配套工具：`custom_imports` 配置项使得用户在不修改源码的前提下挂载自研模块，是与**配置系统 / 运行时装配系统**的标准接口。

3. **外部引用**：文中给出两处学术出处——SECOND 论文（MDPI Sensors 18(10):3337）与 PartA2 论文（arXiv:1907.03670），用于追溯组件的设计动机。

4. **BEVDet 上下文**：尽管文件路径位于 `BEVDet_for_PyTorch/docs/zh_cn/tutorials/`，文档本身是 mmdet3d 通用教程，路径中所有 `mmdet3d/...` 引用表明 **BEVDet 是建立在 mmdet3d 之上的 3D 检测器**，本教程为在其上扩展自定义组件提供基础。

---

## 【使用方法】

**新增组件的标准流程**（四种组件类型完全平行）：

1. **新增 encoder**（以 HardVFE 为例）
   - 建文件：`mmdet3d/models/voxel_encoders/voxel_encoder.py`，类用 `@VOXEL_ENCODERS.register_module()` 修饰；
   - 导入：`mmdet3d/models/voxel_encoders/__init__.py` 加 `from .voxel_encoder import HardVFE`；或在 config 写：
     ```python
     custom_imports = dict(imports=['mmdet3d.models.voxel_encoders.HardVFE'],
                           allow_failed_imports=False)
     ```
   - 在 config 中使用：
     ```python
     model = dict(..., voxel_encoder=dict(type='HardVFE', arg1=xxx, arg2=xxx), ...)
     ```

2. **新增 backbone**（以 SECOND 为例，继承 `BaseModule`，注册器 `BACKBONES`）
   - 文件路径：`mmdet3d/models/backbones/second.py`
   - config 装配：`model = dict(..., backbone=dict(type='SECOND', arg1=xxx, arg2=xxx), ...)`

3. **新增 neck**（以 SECONDFPN 为例）
   - 文件路径：`mmdet3d/models/necks/second_fpn.py`，类用 `@NECKS.register` 修饰；
   - config 装配示例：
     ```python
     model = dict(..., neck=dict(type='SECONDFPN',
                                 in_channels=[64, 128, 256],
                                 upsample_strides=[1, 2, 4],
                                 out_channels=[128, 128, 128]), ...)
     ```

4. **新增 head / RoI Head**（以 PartA2 为例）
   - **bbox head**：文件 `mmdet3d/models/roi_heads/bbox_heads/parta2_bbox_head.py`，继承 `BBoxHead`，注册器 `HEADS`；
   - **RoI Head**：文件 `mmdet3d/models/roi_heads/part_aggregation_roi_head.py`，继承 `Base3DRoIHead`，重写 `init_*` 与 `forward_train` 等抽象方法，并覆写 `_bbox_forward(seg_feats, part_feats, voxels_dict, rois)`；
   - 通过 `model = dict(..., roi_head=dict(type='PartAggregationROIHead', semantic_head=..., num_classes=3, bbox_head=dict(...), ...), ...)` 在 config 中装配；
   - 单阶段检测器请直接参考 `mmdet3d/models/dense_heads/` 中的样例（原文特别提示："由于这些 heads 简单高效，因此这些 heads 普遍应用在自动驾驶场景下的 3D 检测任务中"）。

> 原文未涉及：CLI 命令、环境变量、预训练权重下载链接、训练/评测启动脚本——这些留给其他教程或仓库根目录的 README。
