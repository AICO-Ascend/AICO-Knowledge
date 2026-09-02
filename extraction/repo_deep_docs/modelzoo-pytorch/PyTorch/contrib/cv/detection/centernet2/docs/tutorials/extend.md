# Extend Detectron2's Defaults

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/centernet2/docs/tutorials/extend.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/centernet2/docs/tutorials/extend.md

# 深度解读:Extend Detectron2's Defaults

---

## 【定位】

这篇文档描述了 Detectron2 (CenterNet2 中复用的底层框架) 在面对"研究需要不断以新方式做事情"这一核心张力时,所采用的**双层/三层接口设计哲学**,并以 Mask R-CNN 为例,演示如何**从"纯配置 → 配置+局部覆盖 → 全显式参数"三种粒度逐级深入**,从而在标准易用与最大灵活之间取得平衡。

---

## 【技术要点】

1. **两种设计张力的并存**(原文第 1-2 段):detectron2 须同时支持"非常薄的抽象,允许打破既有抽象以新方式做事"和"较高级别的抽象,让用户不需关心细节即可做标准事"。

2. **三类接口形式**(原文对应条目 1/2/3):
   - **类型 A — 标准默认行为接口**:函数/类接收 `cfg` 参数,内部按需从配置中读取并执行"标准"操作;
   - **类型 B — 显式参数构建块接口**:每个函数/类有明确显式参数,需用户自行理解参数意义并拼接;
   - **类型 C — `@configurable` 装饰器接口**:同一函数/类可被以 cfg、显式参数、或两者混合方式调用(原文标注"显式参数接口目前为 experimental")。

3. **构造 Mask R-CNN 的三种粒度**(原文示例 1/2/3):
   - **Config-only**:`model = build_model(cfg)`,只加载并传入 config;
   - **Mixture 混合**:`GeneralizedRCNN(cfg, roi_heads=StandardROIHeads(cfg, batch_size_per_image=666), pixel_std=[57.0, 57.0, 57.0])`,在 cfg 基础上对部分字段做覆盖;
   - **Full explicit 全显式**:见下方"关键机制与数据"。

4. **FPN/Backbone 显式构造的关键参数**(原文 detail 代码块):
   - Backbone:输入通道 3、初始通道 64、`norm="FrozenBN"`、`ResNet.make_default_stages(50, stride_in_1x1=True, norm="FrozenBN")`、输出特征 `["res2", "res3", "res4", "res5"]`、`.freeze(2)` 冻结前两个 stage;
   - FPN:in_features 与 backbone 输出对齐、out_channels=256、`top_block=LastLevelMaxPool()`。

5. **RPN 显式构造的关键参数**(原文 detail 代码块):
   - `in_features=["p2", "p3", "p4", "p5", "p6"]`、`StandardRPNHead(in_channels=256, num_anchors=3)`;
   - 锚点生成:`sizes=[[32], [64], [128], [256], [512]]`、`aspect_ratios=[0.5, 1.0, 2.0]`、`strides=[4, 8, 16, 32, 64]`、`offset=0.0`;
   - 匹配与回归:`Matcher([0.3, 0.7], [0, -1, 1], allow_low_quality_matches=True)`、`Box2BoxTransform([1.0, 1.0, 1.0, 1.0])`;
   - 采样与 NMS:`batch_size_per_image=256`、`positive_fraction=0.5`、`pre_nms_topk=(2000, 1000)`、`post_nms_topk=(1000, 1000)`、`nms_thresh=0.7`。

6. **ROI Heads 显式构造的关键参数**(原文 detail 代码块):
   - `num_classes=80`、`batch_size_per_image=512`、`positive_fraction=0.25`;
   - `proposal_matcher=Matcher([0.5], [0, 1], allow_low_quality_matches=False)`;
   - box 分支:`box_in_features=["p2","p3","p4","p5"]`、box_pooler `ROIPooler(7, (1/4,1/8,1/16,1/32), 0, "ROIAlignV2")`;box_head `FastRCNNConvFCHead(ShapeSpec(channels=256, height=7, width=7), conv_dims=[], fc_dims=[1024, 1024])`;box_predictor `FastRCNNOutputLayers(ShapeSpec(channels=1024), test_score_thresh=0.05, box2box_transform=Box2BoxTransform((10,10,5,5)), num_classes=80)`;
   - mask 分支:`mask_in_features=["p2","p3","p4","p5"]`、mask_pooler `ROIPooler(14, (1/4,1/8,1/16,1/32), 0, "ROIAlignV2")`;mask_head `MaskRCNNConvUpsampleHead(ShapeSpec(channels=256, width=14, height=14), num_classes=80, conv_dims=[256,256,256,256,256])`;
   - 顶层:`pixel_mean=[103.530, 116.280, 123.675]`、`pixel_std=[1.0, 1.0, 1.0]`、`input_format="BGR"`。

---

## 【关键机制与数据】

> 原文:接口分为三类——cfg-only、标准 default;显式参数构建块;`@configurable` 装饰器(可混用)。其工作机制是:**同一组件在标准入口走"cfg → 默认实现"路径;一旦用户传入显式参数,即在内部绕开默认,从显式实例构造"小积木"再拼接为完整模型**。换言之,`@configurable` 提供了"按需降级"的能力——上层用 cfg 一键完成,下层用 explicit args 自由重写。

> 原文:全显式 Mask R-CNN 示例展示了 detectron2 的**模块层级**:`GeneralizedRCNN` 由 `backbone` + `proposal_generator` + `roi_heads` 三大子模块组成,每个子模块又由若干"小积木"组合(例如 RPN = 锚点生成 + 匹配器 + 回归变换 + 采样策略 + NMS 阈值)。

> 原文:在 Mixture 示例中,`pixel_std=[57.0, 57.0, 57.0]` 与全显式示例中的 `pixel_std=[1.0, 1.0, 1.0]` 体现了"覆盖默认归一化"的常见做法;`batch_size_per_image=666` 体现了"在 cfg 基础上临时改采样数"的能力。

> 原文(数据流方向):粗略可概括为 `像素输入 → Backbone(stem→stages→输出 res2-5) → FPN(融合为 p2-6) → RPN(生成 proposals) → ROI Heads(box 分支 + mask 分支) → 最终预测`。原文未给出训练 loss 数值或推理 mAP 数据。

> 原文:整篇无任何性能/基准数字,**不含 mAP、FPS、batch size、训练 epoch 等实测数据**。

---

## 【表格解读】

**原文无表格。**

全文仅以"分类列表 + 一段长代码示例"组织,未出现任何参数表、性能对比表或配置项表。

---

## 【公式解读】

**原文无公式。**

全文未出现 LaTeX 公式、伪代码公式或带等号的数学表达式。代码示例中的参数数值(如 `sizes=[[32],…]`、`Box2BoxTransform((10,10,5,5))`、`conv_dims=[1024, 1024]`)是**构造参数而非数学公式**。

---

## 【关联】

本文是 Detectron2 tutorials 的**"扩展与自定义"总览页**,在概念层面统摄下游若干教程,并通过 `@configurable` 反向回指到 config 体系。

| 关联方向 | 链接(原文) | 关系 |
|---|---|---|
| 上游/工具基座 | `../modules/config.html#detectron2.config.configurable` | 提供 `@configurable` 装饰器实现,是本文第三类接口的依赖机制 |
| 入门/标准用法 | `./getting_started.md` | "如果你只要标准行为,看这里就够了"——与本文"扩展"路径互为补充 |
| 数据集扩展 | `./datasets.md`("Use Custom Datasets") | 标准数据集之外的扩展入口 |
| 数据加载扩展 | `./data_loading.md`("Use Custom Data Loaders") | 自定义 DataLoader,替换标准数据加载逻辑 |
| 模型使用/覆盖 | `./models.md`("Use Models") | 在已有模型上重写行为,介于"标准 default"与"显式构造"之间 |
| 模型编写 | `./write-models.md`("Write Models") | 完全自定义新模型,对应本文"全显式参数"的极端情形 |
| 训练循环扩展 | `./training.md`("training") | 通过 Hooks 或自定义 loop 替换默认训练流程 |

文档结构关系可概括为:**本文 = 抽象总论;`getting_started` = 标准用法入口;`datasets`/`data_loading`/`models`/`write-models`/`training` = 自底向上的五类具体扩展路径**。

---

## 【使用方法】

> 原文:三种启用方式对应三种用户场景——
>
> 1. **只想用标准行为**(加载预训练、做标准训练/推理):阅读并使用 [Beginner's Tutorial](./getting_started.md),按其中给出的入口(`build_model(cfg)` 等)调用即可;
>
> 2. **需要扩展 detectron2**:按需进入以下教程——
>    - 自定义数据集 → [`./datasets.md`](./datasets.md);
>    - 自定义数据加载器 → [`./data_loading.md`](./data_loading.md);
>    - 重写已有模型行为 → [`./models.md`](./models.md);
>    - 编写全新模型 → [`./write-models.md`](./write-models.md);
>    - 自定义训练循环(通过 Hooks 或自行编写) → [`./training.md`](./training.md)。
>
> 3. **想利用 `@configurable` 做"cfg + 局部覆盖"**:
>    ```python
>    model = GeneralizedRCNN(
>      cfg,
>      roi_heads=StandardROIHeads(cfg, batch_size_per_image=666),
>      pixel_std=[57.0, 57.0, 57.0])
>    ```
>    其余配置仍由 cfg 提供,只对需要变动的子模块显式注入。
>
> 4. **想完全自底向上拼接**:
>    按原文 detail 代码块逐个实例化 `FPN(ResNet(...))`、`RPN(...)`、`StandardROIHeads(...)`,再交给 `GeneralizedRCNN(...)`。原文中 `FrozenBN`、`ROIAlignV2`、`LastLevelMaxPool` 等组件均为 detectron2 已提供的小积木。

> 原文未涉及:具体的 yaml 配置项开关、命令行参数、环境变量、模型 checkpoint 下载链接等,**这些信息在本文之外的教程中给出**。
