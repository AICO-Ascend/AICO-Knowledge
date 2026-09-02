# Tutorial 1: Learn about Configs

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/GFocalV2/docs/tutorials/config.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/GFocalV2/docs/tutorials/config.md

# 深度解读:GFocalV2 配置文件教程

## 【定位】

这篇文档是 GFocalV2(基于 mmdetection 框架)配置系统的入门教程,介绍其**模块化与继承式配置设计**——通过 `_base_` 下四类基础组件的组合复用,以及 `_base_` 继承机制,帮助用户快速搭建、查看、修改检测实验配置。

## 【技术要点】

1. **配置查看命令**:可使用 `python tools/print_config.py /PATH/TO/CONFIG` 打印完整配置,并通过 `--cfg-options xxx.yyy=zzz` 临时覆盖字段查看更新后的配置。
2. **四类基础组件**:`config/_base_` 目录下固定为 4 类——`dataset`(数据集)、`model`(模型)、`schedule`(训练调度)、`default_runtime`(默认运行设置);Faster R-CNN、Mask R-CNN、Cascade R-CNN、RPN、SSD 等可由"各取一类"拼装而成。
3. **继承层级与原始(primitive)配置**:同一目录下推荐只有 **1 个** primitive 配置,其他配置继承自它,最大继承层级为 **3**。
4. **配置文件命名规则**:模板为 `{model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}`,`{xxx}` 必填,`[yyy]` 可选。
5. **归一化层(norm)规范**:默认使用 `bn`(Batch Normalization);其他选项包括 `gn`(Group Normalization)、`syncbn`(Synchronized BN);`gn-head`/`gn-neck`/`gn-all` 分别表示只在 head、只在 neck、整个模型(含 backbone)应用 GN。
6. **调度(schedule)规范**:`1x` = 12 epochs,`2x` = 24 epochs,`20e` = 20 epochs(级联模型使用);`1x`/`2x` 在第 8/16、11/22 epoch 处学习率衰减 10 倍,`20e` 在第 16、19 epoch 处衰减 10 倍;默认批大小标记为 `8x2`(8 卡 × 每卡 2 张)。

## 【关键机制与数据】

**工作原理(原文:)** 配置系统采用模块化 + 继承设计。`_base_` 提供四类可复用基本组件,detector 配置通过 `_base_ = ...` 字段引入其他配置文件,实现"字段级覆盖"——子配置中重定义某字段会替换父配置的同名字段,从而只修改必要字段而无需重写整个配置文件。**最大继承深度为 3 层**,鼓励贡献者从已有方法(如 Faster R-CNN)继承,而非从零构建。

**训练调度数据(原文:)** 关于学习率衰减节点,文档给出具体 epoch 边界——`1x`/`2x` 在 8/16、11/22 epoch 处衰减因子为 10;`20e` 在 16、19 epoch 处衰减因子为 10。

**Mask R-CNN 示例中的数据(原文:)** ResNet-50 backbone:`depth=50`、`num_stages=4`、`out_indices=(0,1,2,3)`、`frozen_stages=1`、`style='pytorch'`;FPN neck 输入通道 `[256, 512, 1024, 2048]`、输出通道 `256`、`num_outs=5`;RPN head 输入/特征通道 `256`,anchor `scales=[8]`、`ratios=[0.5, 1.0, 2.0]`、`strides=[4, 8, 16, 32, 64]`,loss_cls 用 `CrossEntropyLoss`(`use_sigmoid=True`,`loss_weight=1.0`),loss_bbox 用 `L1Loss`(`loss_weight=1.0`);RoIAlign `output_size=7`、`sampling_ratio=0`(自适应),`featmap_strides=[4, 8, 16, 32]`,`out_channels=256`,box head 类型 `Shared2FCBBoxHead`(原文示例在此处截断)。

## 【表格解读】

**原文无表格。**(文档以代码块和列表形式承载配置示例与字段说明,未提供表格结构。)

## 【公式解读】

**原文无公式。**(文档为配置系统说明,未包含数学公式。)

## 【关联】

- **`_base_` 体系下游组件**:四类基础组件 `dataset / model / schedule / default_runtime` 通过 `_base_` 字段被其他配置继承,形成"原始配置 → 派生配置 → 实验配置"的三级链路(最大 3 层)。
- **与 mmdetection 模块的引用关系**(均为外链,文档以注释形式嵌入 GitHub 源码锚点):
  - backbone:`https://github.com/open-mmlab/mmdetection/blob/master/mmdet/models/backbones/resnet.py#L288`
  - neck(FPN):`https://github.com/open-mmlab/mmdetection/blob/master/mmdet/models/necks/fpn.py#L10`
  - dense head(RPNHead):`https://github.com/open-mmlab/mmdetection/blob/master/mmdet/models/dense_heads/rpn_head.py#L12`
  - anchor generator:`https://github.com/open-mmlab/mmdetection/blob/master/mmdet/core/anchor/anchor_generator.py#L10`
  - box coder(DeltaXYWHBBoxCoder):`https://github.com/open-mmlab/mmdetection/blob/master/mmdet/core/bbox/coder/delta_xywh_bbox_coder.py#L9`
  - smooth L1 loss:`https://github.com/open-mmlab/mmdetection/blob/master/mmdet/models/losses/smooth_l1_loss.py#L56`
  - StandardRoIHead:`https://github.com/open-mmlab/mmdetection/blob/master/mmdet/models/roi_heads/standard_roi_head.py#L10`
  - SingleRoIExtractor:`https://github.com/open-mmlab/mmdetection/blob/master/mmdet/models/roi_heads/roi_extractors/single_level.py#L10`
  - RoIAlign:`https://github.com/open-mmlab/mmdetection/blob/master/mmdet/ops/roi_align/roi_align.py#L79`
- **外部依赖**:详细配置语法参考 [mmcv 配置工具文档](https://mmcv.readthedocs.io/en/latest/utils.html#config)。

## 【使用方法】

- **打印完整配置**:`python tools/print_config.py /PATH/TO/CONFIG`
- **临时覆盖配置项并查看更新结果**:`python tools/print_config.py /PATH/TO/CONFIG --cfg-options xxx.yyy=zzz`
- **新建继承自现有方法的配置**:在配置首行写 `_base_ = ../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py`,再覆盖必要字段。
- **新建全新方法且不与现有方法共享结构**:在 `configs` 目录下创建 `xxx_rcnn` 文件夹(原文:`you may create a folder xxx_rcnn under configs`)。(原文在示例部分截断,后续 `bbox_head` 内部字段的完整配置项未给出。)
