# Tutorial 4: Customize Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/YoloV3_ID1790_for_PyTorch/docs/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/YoloV3_ID1790_for_PyTorch/docs/tutorials/customize_models.md

# 一体化深度解读: Tutorial 4: Customize Models

## 【定位】

这篇文档是 MMDetection (被嵌入在 `modelzoo-pytorch/YoloV3_ID1790_for_PyTorch/docs/tutorials/` 下作为通用检测框架文档) 的「自定义模型组件」教程, 解决"如何在不改动 MMDetection 主体代码的前提下, 为检测模型新增/替换 backbone、neck、head、loss 等可插拔组件"的问题, 给出统一的三步范式 (定义类 → 注册导入 → 配置文件中使用)。

---

## 【技术要点】

1. **5 类模型组件分类** (原文核心结论): backbone (FCN 特征提取网络, 例 ResNet/MobileNet)、neck (backbone 与 head 之间的桥梁, 例 FPN/PAFPN)、head (特定任务头, 例 bbox/mask 预测)、roi extractor (从特征图提取 RoI 特征, 例 RoI Align)、loss (head 内计算损失的组件, 例 FocalLoss/L1Loss/GHMLoss)。
2. **三步注册范式** (新增任意组件通用流程):
   - 第 1 步: 在对应目录新建文件并定义继承 `nn.Module` 的类 (例 `mmdet/models/backbones/mobilenet.py` → `class MobileNet(nn.Module)`, 需实现 `forward` 返回 tuple、`init_weights` 等);
   - 第 2 步: 用 `@BACKBONES.register_module()` (或 `@NECKS.register`、`@HEADS.register_module()`) 装饰器注册, 然后**两种**导入方式二选一: ① 在 `mmdet/models/<子目录>/__init__.py` 加 `from .mobilenet import MobileNet`; ② 在 config 中加 `custom_imports = dict(imports=['mmdet.models.backbones.mobilenet'], allow_failed_imports=False)` (无须改原代码);
   - 第 3 步: 在 config 的 `model=dict(...)` 中按 `type='MobileNet', arg1=xxx, arg2=xxx` 形式声明使用。
3. **Backbone 模板约定**: `__init__(self, arg1, arg2)` 接收配置参数, `forward(self, x)` 返回 tuple (多尺度特征图), `init_weights(self, pretrained=None)` 用于加载预训练。
4. **Neck 模板约定** (以 PAFPN 为例): `__init__` 接受 `in_channels, out_channels, num_outs, start_level=0, end_level=-1, add_extra_convs=False` 等参数; 配置示例给出 `in_channels=[256, 512, 1024, 2048], out_channels=256, num_outs=5`。
5. **Head 自定义范式** (以 Double Head R-CNN, arXiv:1904.06493 为例): 必须**同时**新增 bbox head 与 RoI head 两层 ——
   - bbox head 继承 `BBoxHead`, 核心创新是 `forward(self, x_cls, x_reg)` 接收两条分支特征分别做分类/回归;
   - RoI head 继承 `StandardRoIHead` (`StandardRoIHead` 又继承自 `BaseRoIHead, BBoxTestMixin, MaskTestMixin`), 通过覆写 `_bbox_forward` 让 cls/reg 走不同 RoI scale 的 RoI extractor;
   - 子类化策略为"只重写差异部分, 其余继承父类", 例 DoubleHeadRoIHead 继承 StandardRoIHead 已实现的 `init_assigner_sampler / init_bbox_head / init_mask_head / init_weights / forward_dummy / forward_train / simple_test` 等方法。
6. **配置继承 (config inheritance)**: 自 MMDetection 2.0 起, config 支持 `_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'` 这样的继承, Double Head R-CNN 示例即继承自 `faster_rcnn_r50_fpn_1x_coco.py`, 再覆写 `model.roi_head` 子字段, 通过 `_delete_=True` 删除父配置中同名旧字段。
7. **Loss 自定义约定**: 在 `mmdet/models/losses/my_loss.py` 中实现, 用 `weighted_loss` 装饰器使损失支持逐元素加权 (原文代码在 `from ..builde` 处截断, 不完整)。

---

## 【关键机制与数据】

**工作原理 (按文档呈现的"事件流")**:

- 注册机制: 装饰器 (`@BACKBONES.register_module()` / `@NECKS.register` / `@HEADS.register_module()`) 将类登记到 MMDetection 的全局 registry, 此时**类名字符串** (`'MobileNet'` / `'PAFPN'` / `'DoubleHeadRoIHead'`) 才能被 config 中的 `type='...'` 字段解析; 没有 registry 的导入, config 中的 `type` 字段无从查表, 触发时便会报 "未注册" 错误。
- 双轨导入: `custom_imports` 机制是 MMDetection 为"不修改 mmdet 源码也能扩展"提供的 hook, 让外部模块被动态装载到 registry; `allow_failed_imports=False` 表示导入失败立即报错。
- 数据流 (forward) — 以 Double Head R-CNN `_bbox_forward` 为例:
  1. `bbox_cls_feats = self.bbox_roi_extractor(x[:N], rois)` (N = `bbox_roi_extractor.num_inputs`) → 原始 scale 的 RoI 特征用于分类;
  2. `bbox_reg_feats = self.bbox_roi_extractor(x[:N], rois, roi_scale_factor=self.reg_roi_scale_factor)` → **放大 `reg_roi_scale_factor` 倍** 的 RoI 特征用于回归 (原文示例取 `1.3`);
  3. 若 `with_shared_head`, 两条分支各自再过 shared_head;
  4. `cls_score, bbox_pred = self.bbox_head(bbox_cls_feats, bbox_reg_feats)` → Double Head 把 cls/reg 输入分离, head 内部走"conv 分支 + fc 分支"双路 (见 head 类 docstring 中的 ASCII 图: `/-> shared convs -> /-> cls, \-> reg`; `\-> shared fc -> /-> cls, \-> reg`);
  5. 返回 dict `{cls_score, bbox_pred, bbox_feats}` 供后续 loss 计算。
- 文件落位: 各类组件必须放在固定目录以让 build 工厂找到 ——
  - backbone → `mmdet/models/backbones/`
  - neck → `mmdet/models/necks/`
  - bbox head → `mmdet/models/roi_heads/bbox_heads/` (注意子目录)
  - roi head → `mmdet/models/roi_heads/`
  - loss → `mmdet/models/losses/`

**性能/参数数据 (原文出现的具体数字, 标"原文")**:
- 原文: `reg_roi_scale_factor=1.3` —— DoubleHeadRoIHead 用于回归分支的 RoI 缩放因子 (放大 1.3 倍意味着回归分支看到更大空间范围, 与原文 paper 思想一致);
- 原文: `num_convs=4, num_fcs=2, in_channels=256, conv_out_channels=1024, fc_out_channels=1024, roi_feat_size=7, num_classes=80` —— DoubleConvFCBBoxHead 的具体配置 (80 类对应 COCO);
- 原文: bbox_coder 用 `DeltaXYWHBBoxCoder`, `target_means=[0., 0., 0., 0.]`, `target_stds=[0.1, 0.1, 0.2, 0.2]` (x/y 与 w/h 的方差不同, 反映对宽高的容许误差更大);
- 原文: `loss_cls=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=2.0)` 与 `loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=2.0)` —— cls/reg 损失权重均设为 2.0;
- 原文: PAFPN 示例 `in_channels=[256, 512, 1024, 2048], out_channels=256, num_outs=5` —— 该取值匹配 ResNet50 FPN 的 4 个 stage 加 1 个额外输出 (5 个 out 通道)。

> 注: 原文末尾的 loss 添加段代码被截断 (`from ..builde` 后中断), 故该子节细节不完整。

---

## 【表格解读】

**原文无表格** (全文为教程散文 + 代码块形式, 没有 markdown/HTML 表格)。

---

## 【公式解读】

**原文无公式** (文档以代码与配置项为主, 没有数学公式或伪代码形式的公式)。

---

## 【关联】

**与同目录下其他教程 / MMDetection 模块生态的关联** (基于原文提及的关系, 无文末内部链接, 由用户标注 "(无)"):

- **上游教程**: 当前为 Tutorial 4, 暗示存在 Tutorial 1/2/3 (config 基础、构建模型、修改数据集等) — 原文未给出链接, 但承接"MMDetection 2.0 起 config 支持继承"这一基础能力, 故读者需先掌握 config system 才能理解 `_base_=...` 与 `_delete_=True` 的语义。
- **`from ..builder import BACKBONES / NECKS / HEADS`**: 全部组件都依赖 `mmdet/models/builder.py` 中的 registry 工厂, 任何自定义组件都被该工厂按 `type` 字符串动态实例化 ——
  - `BACKBONES` 供 `model.backbone=dict(type='MobileNet', ...)`;
  - `NECKS` 供 `model.neck=dict(type='PAFPN', ...)`;
  - `HEADS` 同时供 bbox_head / roi_head / mask_head;
  - `LOSSES` (虽未在本段代码中完整展示, 但属于同类体系) 供 `model.roi_head.bbox_head.loss_cls=dict(type='MyLoss', ...)`。
- **`StandardRoIHead` / `BaseRoIHead` / `BBoxHead`**: 双层基类链 ——
  - `BaseRoIHead` 是抽象基类, 定义 roi_head 必须实现的接口 (`init_assigner_sampler / init_bbox_head / init_mask_head / init_weights` 等);
  - `StandardRoIHead` 提供"一个 bbox head + 一个 mask head"的标准实现, 是大多数单阶段/双阶段 detector 的默认 roi head;
  - `DoubleHeadRoIHead` 单点覆写 `_bbox_forward` 即可复用其余逻辑, 体现"继承 + 覆写"的设计哲学;
  - `BBoxHead` 是 bbox head 的基类, `DoubleConvFCBBoxHead` 继承它并改写 `forward(self, x_cls, x_reg)` 签名。
- **`custom_imports` 与 `__init__.py` 两种导入**: 是**并列**关系, 二选一; `custom_imports` 适合外部 patch 场景, `__init__.py` 写法适合长期纳入仓库的扩展。
- **外部依赖 (论文)**: Double Head R-CNN 引用 `https://arxiv.org/abs/1904.06493` — 文档内嵌链接, 表明该教程示例与外部学术工作直接对应。
- **被嵌入位置**: 该教程物理路径在 `YoloV3_ID1790_for_PyTorch/docs/tutorials/customize_models.md`, 说明此模型仓库随附了 MMDetection 的通用定制文档, 但 YoloV3 本身是单阶段 (无 RoI head) 检测器, 因此本文中的 RoI head / bbox head 章节对 YoloV3 实战**并不直接使用**, 主要面向基于 MMDetection 框架的开发者。

---

## 【使用方法】

按原文给出的三种启用方式:

1. **新增 backbone** (例 MobileNet):
   - 在 `mmdet/models/backbones/mobilenet.py` 定义 `class MobileNet(nn.Module)` 并用 `@BACKBONES.register_module()` 装饰;
   - 在 `mmdet/models/backbones/__init__.py` 加 `from .mobilenet import MobileNet`, 或在 config 加 `custom_imports = dict(imports=['mmdet.models.backbones.mobilenet'], allow_failed_imports=False)`;
   - config 中写:
     ```python
     model = dict(
         backbone=dict(type='MobileNet', arg1=xxx, arg2=xxx),
         ...)
     ```

2. **新增 neck** (例 PAFPN):
   - 在 `mmdet/models/necks/pafpn.py` 定义 `class PAFPN(nn.Module)` 并用 `@NECKS.register` 装饰, `__init__` 含 `in_channels, out_channels, num_outs, start_level=0, end_level=-1, add_extra_convs=False`;
   - 同 backbone 的两种导入方式;
   - config 中写 `neck=dict(type='PAFPN', in_channels=[256,512,1024,2048], out_channels=256, num_outs=5)`。

3. **新增 head** (例 Double Head R-CNN):
   - 同时在 `mmdet/models/roi_heads/bbox_heads/double_bbox_head.py` (继承 `BBoxHead`, 装饰 `@HEADS.register_module()`) 与 `mmdet/models/roi_heads/double_roi_head.py` (继承 `StandardRoIHead`) 各定义一个类;
   - 在两个 `__init__.py` 中导入, 或在 config 加 `custom_imports=dict(imports=['mmdet.models.roi_heads.double_roi_head', 'mmdet.models.bbox_heads.double_bbox_head'])`;
   - config 利用 `_base_` 继承自 Faster R-CNN FPN 1x, 然后覆写:
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
                 conv_out_channels=1024,
                 fc_out_channels=1024,
                 roi_feat_size=7,
                 num_classes=80,
                 bbox_coder=dict(type='DeltaXYWHBBoxCoder',
                                 target_means=[0.,0.,0.,0.],
                                 target_stds=[0.1,0.1,0.2,0.2]),
                 reg_class_agnostic=False,
                 loss_cls=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=2.0),
                 loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=2.0))))
     ```

4. **新增 loss** (例 MyLoss):
   - 在 `mmdet/models/losses/my_loss.py` 定义类, 用 `weighted_loss` 装饰器使其支持逐元素加权 (原文示例 `from ..builde...` 处被截断, 完整实现未给出, 故 `__init__` 参数/配置字段写法"原文未完整展示")。

> **注意事项 (基于原文可推断的隐含约束)**: 自定义组件的 `__init__` 参数必须与 config 中 dict 的 key 一一对应; `forward` 返回 tuple 是 backbone 与 neck 的硬性约定 (因为下游可能有 FPN 类 neck 期望多尺度输入); 注册装饰器必须放在类定义**正上方**, 否则 registry 找不到。
