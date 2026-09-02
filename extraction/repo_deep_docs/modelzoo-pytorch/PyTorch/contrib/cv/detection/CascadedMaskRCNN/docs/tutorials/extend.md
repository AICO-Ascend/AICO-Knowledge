# Extend Detectron2's Defaults

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/tutorials/extend.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/tutorials/extend.md

【定位】
这篇文档解决 Detectron2 在"研究灵活性（薄抽象、允许改写一切）"与"工程易用性（高层抽象、配置即用）"之间的张力问题，描述了 Detectron2 提供的两种/三种接口形态（cfg 驱动的标准接口、显式参数的小积木、以及带 `@configurable` 装饰器的实验性双形态接口）及其在 Mask R-CNN 这种复杂模型上的实际组装方式。

---

【技术要点】

1. **三层抽象的分工**：原文明示存在三类接口——(a) 接收 `cfg` 的"标准默认"函数/类；(b) 具有明确显式参数的小型构建块；(c)（实验性）用 `@configurable` 装饰、既可传 cfg 也可传显式参数的类，其显式参数接口目前 __experimental__ 并可能变动。

2. **Mask R-CNN 的显式构造入口**：`GeneralizedRCNN(...)` 接受 `backbone`、`proposal_generator`、`roi_heads` 三个一级子组件，外加 `pixel_mean=[103.530, 116.280, 123.675]`、`pixel_std=[1.0, 1.0, 1.0]`、`input_format="BGR"`。

3. **Backbone = FPN(ResNet(...))**：
   - `BasicStem(3, 64)` 输入 3 通道、输出 64 通道；
   - `ResNet.make_stage(BottleneckBlock, n, s, ...)` 的四个 stage 分别为 `[3, 4, 6, 3]` 个 block，步长 `[1, 2, 2, 2]`，输入通道 `[64, 256, 512, 1024]`，输出通道 `[256, 512, 1024, 2048]`，`bottleneck_channels = out_channels // 4`，并设置 `stride_in_1x1=True`；
   - `out_features=["res2", "res3", "res4", "res5"]`，再 `.freeze(2)` 冻结前两层；
   - FPN 取这些特征、输出通道 `256`、附加 `top_block=LastLevelMaxPool()`，得到 `p6`。

4. **RPN 显式参数**：
   - `in_features=["p2", "p3", "p4", "p5", "p6"]`，`head=StandardRPNHead(in_channels=256, num_anchors=3)`；
   - `DefaultAnchorGenerator(sizes=[[32],[64],[128],[256],[512]], aspect_ratios=[0.5, 1.0, 2.0], strides=[4, 8, 16, 32, 64], offset=0.0)`；
   - `anchor_matcher=Matcher([0.3, 0.7], [0, -1, 1], allow_low_quality_matches=True)`；
   - `box2box_transform=Box2BoxTransform([1.0, 1.0, 1.0, 1.0])`；
   - 采样：`batch_size_per_image=256, positive_fraction=0.5`；NMS：`pre_nms_topk=(2000, 1000), post_nms_topk=(1000, 1000), nms_thresh=0.7`。

5. **StandardROIHeads 显式参数**：
   - 检测分支：`num_classes=80, batch_size_per_image=512, positive_fraction=0.25, proposal_matcher=Matcher([0.5], [0, 1], allow_low_quality_matches=False)`；
   - `box_pooler=ROIPooler(7, (1/4, 1/8, 1/16, 1/32), 0, "ROIAlignV2")`，`box_head=FastRCNNConvFCHead(ShapeSpec(channels=256, height=7, width=7), conv_dims=[], fc_dims=[1024, 1024])`；
   - `box_predictor=FastRCNNOutputLayers(ShapeSpec(channels=1024), test_score_thresh=0.05, box2box_transform=Box2BoxTransform((10, 10, 5, 5)), num_classes=80)`；
   - Mask 分支：`mask_pooler=ROIPooler(14, (1/4, 1/8, 1/16, 1/32), 0, "ROIAlignV2")`，`mask_head=MaskRCNNConvUpsampleHead(ShapeSpec(channels=256, width=14, height=14), num_classes=80, conv_dims=[256, 256, 256, 256, 256])`。

6. **教程分流指引**：若只需"标准默认"行为，[Beginner's Tutorial](./getting_started.md) 即可；要扩展则需结合 [datasets.md](./datasets.md)、[data_loading.md](./data_loading.md)、[models.md](./models.md)、[write-models.md](./write-models.md)、[training.md](./training.md) 五个子教程。

---

【关键机制与数据】

- **机制（双形态接口）**：原文把 detectron2 的接口分为"cfg 驱动"与"显式参数驱动"两条路径。前者由 cfg 自动读取、隐藏细节；后者由用户显式提供每个参数，可任意重新拼装。第三类 `@configurable` 装饰的类允许用任一形式调用，但原文明确标注其显式参数接口为 __experimental__，可能后续变更。

- **数据流（Mask R-CNN 装配顺序，原文示例）**：`GeneralizedRCNN` 内
  1. `backbone = FPN(ResNet(BasicStem, [ResNet.make_stage(...)*4], out_features=["res2"…"res5"]).freeze(2), in_features, 256, top_block=LastLevelMaxPool())` → 产生 `p2…p6`；
  2. `proposal_generator = RPN(in_features=p2…p6, head=StandardRPNHead(256, 3), anchor_generator=DefaultAnchorGenerator(...), anchor_matcher=Matcher([0.3,0.7],[0,-1,1],allow_low_quality_matches=True), box2box_transform=Box2BoxTransform([1,1,1,1]), batch_size_per_image=256, positive_fraction=0.5, pre_nms_topk=(2000,1000), post_nms_topk=(1000,1000), nms_thresh=0.7)`；
  3. `roi_heads = StandardROIHeads(num_classes=80, batch_size_per_image=512, positive_fraction=0.25, proposal_matcher=Matcher([0.5],[0,1],allow_low_quality_matches=False), box_in_features=p2…p5, box_pooler=ROIPooler(7, (1/4,1/8,1/16,1/32), 0, "ROIAlignV2"), box_head=FastRCNNConvFCHead(ShapeSpec(256,7,7), [], [1024,1024]), box_predictor=FastRCNNOutputLayers(ShapeSpec(1024), 0.05, Box2BoxTransform((10,10,5,5)), 80), mask_in_features=p2…p5, mask_pooler=ROIPooler(14, (1/4,1/8,1/16,1/32), 0, "ROIAlignV2"), mask_head=MaskRCNNConvUpsampleHead(ShapeSpec(256,14,14), 80, [256]*5))`；
  4. `pixel_mean/std + input_format="BGR"` 决定输入归一化与通道顺序。
- **性能数据**：原文未涉及具体 benchmark / 速度 / 精度数字。
- **新增/改写入口（原文）**：通过把"小积木"按需重排即可实现 detectron2 不直接支持的新模型，例如替换 `proposal_generator`、改 `roi_heads` 子模块、或自定义 backbone 阶段参数（如 `conv_dims`、`fc_dims`、`test_score_thresh=0.05`、`nms_thresh=0.7` 等都是显式可控点）。

---

【表格解读】

原文无表格（正文仅含一段叙述与一段 Python 代码示例，无参数表/对比表/配置项表）。

---

【公式解读】

原文无公式（无 LaTeX 公式或伪代码形式的公式块；示例仅是 Python 类的显式参数化调用）。

---

【关联】

- **与"标准默认"层的关系**：原文将本篇定位为对 "Standard Default" 之外的扩展路径——若不需扩展，参 [Beginner's Tutorial](./getting_started.md)；需要扩展时再按本文给出的显式组件链拼装。
- **与 `@configurable` 的关系**：第三类接口由 [`@configurable`](../../modules/config.html#detectron2.config.configurable) 装饰器提供，原文标注其显式参数形态为 __experimental__、可能变动；这是介于 cfg 接口与显式接口之间的桥梁。
- **与数据集/数据加载的关系**：扩展自定义数据走 [Use Custom Datasets](./datasets.md)；扩展训练/推理数据加载逻辑走 [Use Custom Data Loaders](./data_loading.md)。
- **与模型层的关系**：覆盖/改写检测模型默认行为见 [Use Models](./models.md)；从头实现新模型见 [Write Models](./write-models.md)。
- **与训练的关系**：训练循环可由 hooks 扩展或完全自写，见 [training](./training.md)。
- **在 CascadedMaskRCNN 仓中的角色**：该篇位于 `PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/tutorials/`，作为 detectron2 官方"扩展机制"教程在 Cascade Mask R-CNN 仓中的本地化副本，为该模型仓的下游自定义（自定义数据集/loader/head/training loop）提供入口指引。

---

【使用方法】

原文未涉及具体启动命令、超参开关或配置文件项；其"启用方式"以 **代码示例** 形式给出（即上文中 `GeneralizedRCNN(backbone=FPN(...), proposal_generator=RPN(...), roi_heads=StandardROIHeads(...), pixel_mean=[103.530, 116.280, 123.675], pixel_std=[1.0, 1.0, 1.0], input_format="BGR")` 这段 Python 装配代码），并以 `<details>` 折叠块呈现（点击展开）。  
扩展时分流指引（原文列出）：标准用法 → [Beginner's Tutorial](./getting_started.md)；自定义数据集 → [datasets.md](./datasets.md)；自定义数据加载 → [data_loading.md](./data_loading.md)；覆盖/改写模型行为 → [models.md](./models.md) 与 [write-models.md](./write-models.md)；自定义训练 → [training](./training.md)。
