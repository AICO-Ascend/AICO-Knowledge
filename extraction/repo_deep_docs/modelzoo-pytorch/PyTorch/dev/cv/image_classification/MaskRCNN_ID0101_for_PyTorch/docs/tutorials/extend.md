# Extend Detectron2's Defaults

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/tutorials/extend.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/tutorials/extend.md

# 「Extend Detectron2's Defaults」深度解读

## 【定位】
这篇文档回答「detectron2 在『高层默认行为』与『可被覆写的低层组件』之间如何取得平衡」这一架构设计问题，描述其通过 cfg 接口、显式参数接口、以及 `@configurable` 实验性桥接接口三层机制让用户既能开箱即用又能灵活替换/扩展默认实现的能力。

## 【技术要点】
1. **接口设计存在张力**：detectron2 必须同时提供「极薄抽象（允许用新方式做一切）」与「高层抽象（让用户不必关心细节）」两类接口，二者协同解决研究型框架的两难。
2. **cfg 接口（标准默认行为）**：函数/类接受 `cfg` 作为唯一或主要参数，按 config 读取所需项执行「标准」流程；用户只需加载 config 并传递，无需理解各参数含义。
3. **显式参数接口（小积木）**：每个函数/类有定义良好的显式参数，是系统的可组合构建块；需要用户专业知识来取值并拼接，但能以更灵活的方式组合。
4. **@configurable 桥接接口（实验性）**：通过 `@configurable` 装饰的类既可接受 `cfg` 调用，也可接受显式参数调用；显式参数接口当前是 __experimental__，未来可能变更。
5. **Mask R-CNN 完整显式构造示例**：以 `GeneralizedRCNN` 为顶层，通过 `FPN(ResNet(...))` → `RPN(...)` → `StandardROIHeads(...)` 逐层拼接，演示如何完全脱离 cfg 显式构造一个 80 类 Mask R-CNN。
6. **教程地图**：用 cfg 默认行为 → 跳转到 `getting_started.md`；自定义数据集/数据加载器/模型/训练循环则分别对应 `datasets.md`、`data_loading.md`、`models.md`/`write-models.md`、`training.md`。

## 【关键机制与数据】
- **三类接口工作流**：
  - **cfg 接口**：函数/类接收 `cfg`，从 config 树读出所需配置 → 自动套用「标准」行为；用户负担最小。
  - **显式接口**：每个组件独立、可单独替换 → 用户用领域知识手写组合，但灵活度最大。
  - **@configurable**：同一类既支持 `cls(cfg)` 也支持 `cls(**explicit_kwargs)`；原文中明确标注其显式参数接口是 __experimental__，可能后续变更。
- **Mask R-CNN 显式构造数据流（原文给出的具体数值）**：
  - Backbone：`ResNet` + `BasicStem(3, 64)`；四阶段块数/步长/通道为 `[3,4,6,3]` / `[1,2,2,2]` / `[64,256,512,1024]` / `[256,512,1024,2048]`，bottleneck 中间通道 = `out_channels // 4`，并在 `.freeze(2)` 处冻结前两层；`out_features=["res2","res3","res4","res5"]`。
  - FPN：输入特征 `["res2","res3","res4","res5"]`，输出维度 256，`top_block=LastLevelMaxPool()` 产生 `p6`。
  - RPN：`in_features=["p2","p3","p4","p5","p6"]`、`StandardRPNHead(in_channels=256, num_anchors=3)`、`DefaultAnchorGenerator(sizes=[[32],[64],[128],[256],[512]], aspect_ratios=[0.5,1.0,2.0], strides=[4,8,16,32,64], offset=0.0)`；`Matcher([0.3,0.7], [0,-1,1], allow_low_quality_matches=True)`；`Box2BoxTransform([1.0,1.0,1.0,1.0])`；`batch_size_per_image=256`、`positive_fraction=0.5`；`pre_nms_topk=(2000,1000)`、`post_nms_topk=(1000,1000)`、`nms_thresh=0.7`。
  - ROI Heads：`StandardROIHeads(num_classes=80, batch_size_per_image=512, positive_fraction=0.25)`；`proposal_matcher=Matcher([0.5], [0,1], allow_low_quality_matches=False)`；`box_in_features=["p2","p3","p4","p5"]`；`box_pooler=ROIPooler(7, (1/4,1/8,1/16,1/32), 0, "ROIAlignV2")`；`box_head=FastRCNNConvFCHead(ShapeSpec(channels=256,height=7,width=7), conv_dims=[], fc_dims=[1024,1024])`；`box_predictor=FastRCNNOutputLayers(ShapeSpec(channels=1024), test_score_thresh=0.05, box2box_transform=Box2BoxTransform((10,10,5,5)), num_classes=80)`；`mask_in_features=["p2","p3","p4","p5"]`；`mask_pooler=ROIPooler(14, (1/4,1/8,1/16,1/32), 0, "ROIAlignV2")`；`mask_head=MaskRCNNConvUpsampleHead(ShapeSpec(channels=256,width=14,height=14), num_classes=80, conv_dims=[256,256,256,256,256])`。
  - 输入归一化（原文）：`pixel_mean=[103.530, 116.280, 123.675]`，`pixel_std=[1.0, 1.0, 1.0]`，`input_format="BGR"`。
- **使用指引**（原文）：仅需标准行为 → 看 [Beginner's Tutorial](./getting_started.md)；需要扩展 → 按"数据集/数据加载器/模型/训练"四类需求分别跳转对应文档。

## 【表格解读】
原文无表格。

## 【公式解读】
原文无公式。  
（注：原文 Mask R-CNN 示例中仅出现 `bottleneck_channels=o // 4` 这一 Python 整除表达式，属于代码字面量而非数学公式，未以 LaTeX/伪代码给出独立公式。）

## 【关联】
- **三类接口的桥接机制**：@configurable 装饰器，把 cfg 接口和显式接口统一到同一类上 → 链接 `../../modules/config.html#detectron2.config.configurable`。
- **入门级默认使用路径**：仅用 cfg 默认行为时跳转 → `./getting_started.md`。
- **数据集层扩展**：替换/添加自己的 dataset → `./datasets.md`。
- **数据加载层扩展**：替换 detectron2 默认的 data loader → `./data_loading.md`。
- **模型层扩展（覆盖 + 重写）**：覆盖现有模型行为 → `./models.md`；完全自写新模型 → `./write-models.md`。
- **训练层扩展**：基于默认 loop + hooks 或自写 loop → `./training.md`。
- **上下游关系总览**：`getting_started.md` 为「标准默认」路径入口；`datasets.md → data_loading.md → models.md / write-models.md → training.md` 形成「数据 → 模型 → 训练」的扩展流水线；`config.html#detectron2.config.configurable` 是连接 cfg 与显式接口的关键装饰器。

## 【使用方法】
- **何时使用本文**（原文表述）：
  - 只需标准行为 → 「[Beginner's Tutorial](./getting_started.md) should suffice」。
  - 需要扩展 detectron2 至自定义需求 → 根据"自定义数据集 / 自定义 data loader / 改写或重写模型 / 自定义训练"四类目标，分别阅读 `datasets.md`、`data_loading.md`、`models.md` & `write-models.md`、`training.md`。
- **cfg 接口调用方式**：加载一个 config 并作为 `cfg` 传入对应的函数/类，由内部读取所需项执行标准流程。
- **显式接口调用方式**：直接传显式参数构造组件并组装，例如示例中以 `GeneralizedRCNN(backbone=..., proposal_generator=..., roi_heads=..., pixel_mean=[...], pixel_std=[...], input_format="BGR")` 形式完整手写一个 Mask R-CNN。
- **@configurable 双形态调用**（实验性）：既可 `cls(cfg)`，也可 `cls(**explicit_kwargs)`；原文明示其显式参数接口是 __experimental__，可能后续变化。
- **关键配置/超参数清单**（原文 Mask R-CNN 示例中直接给出的字面量）：
  - Backbone：`BasicStem(3,64)`；阶段 `[3,4,6,3]` / `[1,2,2,2]` / `[64,256,512,1024]` / `[256,512,1024,2048]`；`out_features=["res2","res3","res4","res5"]`；`freeze(2)`。
  - FPN：维度 `256`，`top_block=LastLevelMaxPool()`。
  - RPN：`in_features=["p2","p3","p4","p5","p6"]`，`num_anchors=3`，`sizes=[[32],[64],[128],[256],[512]]`，`aspect_ratios=[0.5,1.0,2.0]`，`strides=[4,8,16,32,64]`，`offset=0.0`；`Matcher([0.3,0.7],[0,-1,1], allow_low_quality_matches=True)`；`Box2BoxTransform([1.0,1.0,1.0,1.0])`；`batch_size_per_image=256`，`positive_fraction=0.5`；`pre_nms_topk=(2000,1000)`，`post_nms_topk=(1000,1000)`，`nms_thresh=0.7`。
  - ROI Heads：`num_classes=80`，`batch_size_per_image=512`，`positive_fraction=0.25`；`Matcher([0.5],[0,1], allow_low_quality_matches=False)`；`box_pooler=ROIPooler(7,(1/4,1/8,1/16,1/32),0,"ROIAlignV2")`；`box_head` 用 `ShapeSpec(channels=256,height=7,width=7)` + `fc_dims=[1024,1024]`；`box_predictor` 用 `ShapeSpec(channels=1024)`、`test_score_thresh=0.05`、`Box2BoxTransform((10,10,5,5))`、`num_classes=80`；`mask_pooler=ROIPooler(14,(1/4,1/8,1/16,1/32),0,"ROIAlignV2")`；`mask_head` 用 `ShapeSpec(channels=256,width=14,height=14)`、`num_classes=80`、`conv_dims=[256,256,256,256,256]`。
  - 输入归一化：`pixel_mean=[103.530, 116.280, 123.675]`，`pixel_std=[1.0, 1.0, 1.0]`，`input_format="BGR"`。
- **命令**：原文未涉及 CLI / shell 命令。
