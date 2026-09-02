# Tutorial 4: Customize Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/FCOS/docs/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/FCOS/docs/tutorials/customize_models.md

## 【定位】

这篇文档说明如何在 MMDetection 的注册与配置体系中自定义模型的 backbone、neck、head、RoI extractor 分类下的新 head，以及 loss，从而实现新模型组件的接入和复用。

## 【技术要点]

1. **模型被划分为 5 类组件**
   - `backbone`：通常采用 FCN 提取特征图，例如 ResNet、MobileNet。
   - `neck`：位于 backbone 与 head 之间，例如 FPN、PAFPN。
   - `head`：执行具体任务，例如边界框预测和掩码预测。
   - `roi extractor`：从特征图中提取 RoI 特征，例如 RoI Align。
   - `loss`：在 head 中计算损失，例如 FocalLoss、L1Loss、GHMLoss。

2. **新 backbone 必须注册、导入并写入配置**
   - 示例文件为 `mmdet/models/backbones/mobilenet.py`。
   - 类需要继承 `nn.Module`，提供 `__init__`、`forward` 和 `init_weights`。
   - `forward` 被明确要求返回 tuple。
   - 注册方式为：
     ```python
     @BACKBONES.register_module()
     ```
   - 除了修改 `mmdet/models/backbones/__init__.py`，还可以通过 `custom_imports` 动态导入：
     ```python
     custom_imports = dict(
         imports=['mmdet.models.backbones.mobilenet'],
         allow_failed_imports=False)
     ```
   - 接入配置时通过 `type='MobileNet'` 指定实现，`arg1`、`arg2` 由自定义类读取。

3. **新 neck 以 PAFPN 为接口示例**
   - `PAFPN` 需要注册到 `NECKS`，实现 `forward(self, inputs)`。
   - 构造参数包括 `in_channels`、`out_channels`、`num_outs`，以及默认参数：
     - `start_level=0`
     - `end_level=-1`
     - `add_extra_convs=False`
   - 示例配置为：
     ```python
     neck=dict(
         type='PAFPN',
         in_channels=[256, 512, 1024, 2048],
         out_channels=256,
         num_outs=5)
     ```
   - 原文的 neck 动态导入路径写成了 `mmdet.models.necks.mobilenet`，但对应定义文件是 `pafpn.py`，两者存在明显的不一致，应以实际模块定义和注册位置为准。

4. **新 bbox head 可以同时处理分类与回归两路特征**
   - `DoubleConvFCBBoxHead` 继承 `BBoxHead`，定义了 `__init__`、`init_weights` 和双输入的 `forward(self, x_cls, x_reg)`。
   - 关键默认参数包括：
     - `num_convs=0`
     - `num_fcs=0`
     - `conv_out_channels=1024`
     - `fc_out_channels=1024`
     - `conv_cfg=None`
     - `norm_cfg=dict(type='BN')`
   - 默认通过 `kwargs.setdefault('with_avg_pool', True)` 启用平均池化。
   - 结构示意是同一批 RoI 特征分别进入 shared convs 和 shared fc，两条分支继续产生 `cls` 与 `reg` 结果。

5. **Double Head RoI Head 继承 StandardRoIHead，并只定制边界框前向流程**
   - `DoubleHeadRoIHead(DoubleRoIHead)` 新增 `reg_roi_scale_factor`。
   - `_bbox_forward` 使用 `self.bbox_roi_extractor.num_inputs` 截取前若干层输入特征。
   - 分类特征直接提取；回归特征提取时额外传入 `roi_scale_factor`。
   - `StandardRoIHead` 提供的 RoI head、初始化、采样、训练、掩码和测试等其余逻辑可继续复用。
   - 原文的 Double Head 配置还指定：
     - `reg_roi_scale_factor=1.3`
     - `num_convs=4`
     - `num_fcs=2`
     - `in_channels=256`
     - `conv_out_channels=1024`
     - `fc_out_channels=1024`
     - `roi_feat_size=7`
     - `num_classes=80`

6. **新 loss 通过 `weighted_loss` 装饰器支持逐元素加权**
   - 新 loss 放在 `mmdet/models/losses/my_loss.py`。
   - 原文只给出了文件路径、装饰器用途以及一个被截断的导入片段；没有给出 `MyLoss` 的完整实现、注册方式或配置示例，因此不能从本文继续推导其具体计算公式和参数。

## 【关键机制与数据]

- **原文：整体组件关系。** backbone 负责从输入生成特征图，neck 位于 backbone 与 head 之间，RoI extractor 面向 RoI 特征提取，head 承担任务输出，loss 位于 head 中并计算训练损失。本文以 MobileNet、PAFPN 和 Double Head R-CNN 展示如何替换或扩展这些环节。

- **原文：PAFPN 的数据接口。** PAFPN 接收 `inputs`，按照构造时给出的输入、输出通道以及输出数量处理多尺度特征。示例接收 4 个输入尺度，通道数依次为 `[256, 512, 1024, 2048]`，统一输出到 `256` 个通道，并设置 `num_outs=5`。`start_level`、`end_level` 和 `add_extra_convs` 在该示例中分别保留默认值。

- **原文：Double Head 的双路 RoI 特征。** `_bbox_forward` 对前 `self.bbox_roi_extractor.num_inputs` 层特征执行两次 RoI 特征提取：
  1. 第一次得到 `bbox_cls_feats`；
  2. 第二次为边界框回归得到 `bbox_reg_feats`，并应用 `reg_roi_scale_factor`。
  
  当 `self.with_shared_head` 为真时，两路特征都会经过 `self.shared_head`。随后 `self.bbox_head(bbox_cls_feats, bbox_reg_feats)` 一次产生 `cls_score` 和 `bbox_pred`。返回字典保留 `bbox_feats=bbox_cls_feats`，但没有保存回归分支特征。

- **原文：分类与回归分支结构。** `DoubleConvFCBBoxHead` 的结构示意为：
  - RoI 特征 → shared convs → `cls` / `reg`
  - RoI 特征 → shared fc → `cls` / `reg`
  
  示例配置将 shared convs 数量设为 `4`、shared fc 数量设为 `2`。

- **原文：回归编解码与损失配置。** Double Head 使用 `DeltaXYWHBBoxCoder`：
  - `target_means=[0., 0., 0., 0.]`
  - `target_stds=[0.1, 0.1, 0.2, 0.2]`
  - `reg_class_agnostic=False`
  
  分类使用 `CrossEntropyLoss`，配置为 `use_sigmoid=False, loss_weight=2.0`；回归使用 `SmoothL1Loss`，配置为 `beta=1.0, loss_weight=2.0`。原文没有进一步说明这些设置的计算过程或效果。

- **原文：性能数据。** 原文未提供准确率、推理速度、显存占用、参数量或训练时间等性能数据。

## 【表格解读]

原文无表格。

## 【公式解读]

原文无公式。

## 【关联]

- **注册体系关系：** `BACKBONES`、`NECKS` 和 `HEADS` 是组件接入配置系统的入口。新增类必须先注册，再通过模块导入或 `custom_imports` 使配置能够根据 `type` 找到对应实现。
- **backbone 与 neck 的上下游关系：** backbone 输出特征图，neck 接收并处理这些特征，之后再交给 head。MobileNet 与 PAFPN 分别代表两个层级上的可替换组件。
- **RoI extractor、bbox head 与 RoI head 的关系：**
  - `StandardRoIHead` 继承 `BaseRoIHead`，并组合 `BBoxTestMixin`、`MaskTestMixin`。
  - `DoubleHeadRoIHead` 继承 `StandardRoIHead`，保留其通用生命周期，只覆盖 `_bbox_forward` 中的分类/回归双路提取逻辑。
  - `DoubleHeadRoIHead` 调用 `bbox_roi_extractor` 产生两路特征，再调用 `DoubleConvFCBBoxHead` 得到分类和回归结果。
- **配置继承关系：** Double Head 配置继承 `../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py`，只覆盖新的 RoI head 和 bbox head。原文指出，自 MMDetection 2.0 起支持这种配置继承。
- **损失与 head 的关系：** 分类和回归损失作为 bbox head 配置的一部分，由 head 训练过程使用。`weighted_loss` 用于让 loss 支持逐元素权重。
- **路径信息需要注意：** 原文前文把新增 bbox head 放在 `mmdet/models/roi_heads/bbox_heads/double_bbox_head.py`，后文又要求修改 `mmdet/models/bbox_heads/__init__.py`；动态导入路径也采用后者。原文内部存在路径差异，实施时应以当前仓库目录结构为准。
- **链接信息：** 原文没有提供文末内部链接。唯一显示的链接是 Double Head R-CNN 的外部论文地址：`https://arxiv.org/abs/1904.06493`；本文的类设计和配置均以该论文所代表的 Double Head R-CNN 为示例。
- **与 FCOS 的关系：** 本文只提供通用模型定制方法，没有展开 FCOS 特有的检测头、回归目标或性能配置。

## 【使用方法]

- **接入新 backbone：**
  ```python
  model = dict(
      ...
      backbone=dict(
          type='MobileNet',
          arg1=xxx,
          arg2=xxx),
      ...
  ```
  同时将 `MobileNet` 注册到 `BACKBONES` 并完成导入。`forward` 必须返回 tuple，`init_weights` 用于接收可选的预训练权重。

- **接入新 neck：**
  ```python
  neck=dict(
      type='PAFPN',
      in_channels=[256, 512, 1024, 2048],
      out_channels=256,
      num_outs=5)
  ```
  如不希望修改 `mmdet/models/necks/__init__.py`，可在配置中设置 `custom_imports`；但原文给出的 `mmdet.models.necks.mobilenet` 路径与 `pafpn.py` 定义不一致，需要核对修正。

- **接入 Double Head R-CNN：**
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
                  type='CrossEntropyLoss',
                  use_sigmoid=False,
                  loss_weight=2.0),
              loss_bbox=dict(
                  type='SmoothL1Loss',
                  beta=1.0,
                  loss_weight=2.0))))
  ```
  该配置用 `_delete_=True` 替换基础 Faster R-CNN 配置中的 bbox head，并设置 `DoubleHeadRoIHead` 使用的回归 RoI 缩放因子 `1.3`。

- **不修改原始注册文件：**
  ```python
  custom_imports=dict(
      imports=[
          'mmdet.models.roi_heads.double_roi_head',
          'mmdet.models.bbox_heads.double_bbox_head'
      ])
  ```
  backbone 示例还使用 `allow_failed_imports=False`，要求列出的模块必须成功导入。

- **新增 loss：** 在 `mmdet/models/losses/my_loss.py` 中定义 `MyLoss`，并使用 `weighted_loss` 装饰器使其支持逐元素加权。原文没有提供启用后的完整配置或命令。

- **命令：** 原文未涉及任何 shell 命令或 CLI 启动方式。
