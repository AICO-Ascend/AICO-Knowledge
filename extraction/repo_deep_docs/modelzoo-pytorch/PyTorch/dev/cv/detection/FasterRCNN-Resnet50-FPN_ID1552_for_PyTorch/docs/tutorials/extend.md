# Extend Detectron2's Defaults

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/FasterRCNN-Resnet50-FPN_ID1552_for_PyTorch/docs/tutorials/extend.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/FasterRCNN-Resnet50-FPN_ID1552_for_PyTorch/docs/tutorials/extend.md

# 一体化深度解读:Extend Detectron2's Defaults

## 【定位】

这篇文档解决 detectron2 在"研究灵活性"与"标准易用性"之间如何设计 API 抽象的问题——即当内置"标准默认行为"无法满足需求时,如何通过分层接口(cfg-only、显式参数、`@configurable`)自行替换或重组 detectron2 的各个组件,从而扩展检测器的默认实现。

---

## 【技术要点】

1. **设计张力(research vs. abstractions)**:detectron2 同时需要"足够薄的抽象"(便于研究者打破/替换)和"足够高级的抽象"(便于用户在不理解细节的前提下跑通标准流程)。

2. **三类接口分层**:
   - **cfg-only 接口**:函数/类接收 `cfg` 参数,从配置里读取所需信息并执行"标准默认"行为(原文:"it will read what it needs from the config and do the 'standard' thing")。
   - **显式参数接口**:每个组件是"小积木",用户需理解每个参数含义,但可被灵活拼装(原文:"well-defined explicit arguments … can be stitched together in more flexible ways")。
   - **`@configurable`(实验性)**:被装饰的类既可接受 `cfg`,也可接受显式参数;其显式参数接口"experimental and subject to change"。

3. **Mask R-CNN 完整显式构造示例(原文代码块)**:用 `GeneralizedRCNN(...)` 一行式地把 `FPN(ResNet)` + `RPN` + `StandardROIHeads` 全部以显式参数方式拼装,作为 cfg-only 之外的替代路径。

4. **Backbone 配置(ResNet+FPN)**:ResNet 4 个 stage 参数 `n=[3,4,6,3]`、`stride=[1,2,2,2]`、`in_channels=[64,256,512,1024]`、`out_channels=[256,512,1024,2048]`;输出特征 `["res2","res3","res4","res5"]` 并 `.freeze(2)`;FPN 接收这些特征,FPN 输出 256 通道,`top_block=LastLevelMaxPool()`。

5. **RPN 配置(关键数字)**:5 个特征层 `["p2","p3","p4","p5","p6"]`;`num_anchors=3`;anchor `sizes=[[32],[64],[128],[256],[512]]`、`aspect_ratios=[0.5,1.0,2.0]`、`strides=[4,8,16,32,64]`;`Matcher([0.3,0.7],[0,-1,1],allow_low_quality_matches=True)`;`Box2BoxTransform([1.0,1.0,1.0,1.0])`;`batch_size_per_image=256`,`positive_fraction=0.5`,`pre_nms_topk=(2000,1000)`,`post_nms_topk=(1000,1000)`,`nms_thresh=0.7`。

6. **ROI Heads 配置(关键数字)**:`num_classes=80`;`batch_size_per_image=512`,`positive_fraction=0.25`;`proposal_matcher=Matcher([0.5],[0,1],allow_low_quality_matches=False)`;`box_pooler=ROIPooler(7,(1/4,1/8,1/16,1/32),0,"ROIAlignV2")`;`box_head=FastRCNNConvFCHead(ShapeSpec(256,7,7), conv_dims=[], fc_dims=[1024,1024])`;`box_predictor=FastRCNNOutputLayers(ShapeSpec(1024), test_score_thresh=0.05, Box2BoxTransform((10,10,5,5)), num_classes=80)`;`mask_pooler=ROIPooler(14,(1/4,1/8,1/16,1/32),0,"ROIAlignV2")`;`mask_head=MaskRCNNConvUpsampleHead(ShapeSpec(256,14,14), num_classes=80, conv_dims=[256,256,256,256,256])`。

---

## 【关键机制与数据】

### 抽象双层原理

原文明确把 detectron2 的接口划分为两类(并加上实验性的第三类):

| 层级 | 接口形态 | 用户负担 | 灵活度 |
|---|---|---|---|
| 第一类 | `f(cfg)` —— 内部从 cfg 自取所需 | 最低(只需 load config 并传入) | 标准默认 |
| 第二类 | 显式命名参数 | 较高(需懂每个参数语义) | 任意拼装 |
| 第三类(实验) | `@configurable` 装饰器 | 二者皆可 | 接口"subject to change" |

原文:"Users only need to load a given config and pass it around, without having to worry about which arguments are used and what they all mean."——这说明 cfg-only 路径的设计目的是屏蔽细节;而显式参数路径("small building block … can be stitched together in more flexible ways")则是扩展性所在。

### 数据流(以示例 Mask R-CNN 为例,原文代码块即数据流)

```
输入图像 (BGR, mean=[103.530,116.280,123.675], std=[1,1,1])
        │
        ▼
ResNet(BasicStem(3,64), 4 stages, freeze(2))  →  ["res2","res3","res4","res5"]
        │
        ▼
FPN(..., out_channels=256) + LastLevelMaxPool()  →  ["p2","p3","p4","p5","p6"]
        │
        ▼
RPN(StandardRPNHead 256→3 anchors, anchors str=[4,8,16,32,64])
        │   pre_nms_topk=(2000,1000), post_nms_topk=(1000,1000), nms=0.7
        ▼
StandardROIHeads
   ├─ box:  matcher[0.5]/[0,1], ROIAlignV2 7×7, FC[1024,1024], FastRCNNOutputLayers, δ=(10,10,5,5), score_thresh=0.05
   └─ mask: ROIAlignV2 14×14, ConvUpsample [256,256,256,256,256]
```

工作原理要点(全部对应原文代码,无臆造):
- **Anchor 设计**:5 个尺度 `[[32],[64],[128],[256],[512]]` 与 FPN 5 级 `p2~p6` 一一对应,每个位置 3 种宽高比 `0.5/1.0/2.0`,偏移 `offset=0.0`。
- **正负样本分配**:RPN 用 `Matcher` 的阈值 `[0.3, 0.7]` 区分前景/背景/忽略(`[0,-1,1]`),且 `allow_low_quality_matches=True`;ROI 头则更严格,阈值 `[0.5]`、标签 `[0,1]`、`allow_low_quality_matches=False`。
- **采样配比**:RPN 每图 256 proposal,正样本占 0.5;ROI 每图 512,正样本占 0.25(原文:"batch_size_per_image=256, positive_fraction=0.5"; "batch_size_per_image=512, positive_fraction=0.25")。
- **回归损失权重**:RPN `Box2BoxTransform([1,1,1,1])`(xywh 等权);ROI 检测头 `Box2BoxTransform((10,10,5,5))`(原文括号里就是这 4 个值,xy 权重大于 wh,对应 Faster R-CNN 经典设定)。
- **Mask 头**:5 层 256 通道卷积,与 ROI 14×14 对齐输出。
- **图像归一化**:`pixel_mean=[103.530, 116.280, 123.675]`、`pixel_std=[1.0,1.0,1.0]`、`input_format="BGR"`,这是 COCO 预训练的标准 BGR 均值。

> 性能数据 / benchmark 数字:原文未给出训练/推理耗时或 FPS 等指标,故此处不引用任何数字。

---

## 【表格解读】

**原文无表格**(原文中没有以 markdown/HTML 表格形式呈现的参数表或性能对比表,示例代码以嵌套字典/列表形式给出,不属于结构化表格)。

为便于查阅,以下"参数清单"系**对原文代码块中出现的关键数字逐字整理**(非原文表格,仅做聚合):

| 组件 | 参数 | 原文数值 | 含义(基于原文表述) |
|---|---|---|---|
| `ResNet.stages` | n / stride / in_ch / out_ch | `[3,4,6,3]` / `[1,2,2,2]` / `[64,256,512,1024]` / `[256,512,1024,2048]` | 4 个 ResNet stage 的块数、下采样、输入输出通道 |
| `ResNet` | out_features | `["res2","res3","res4","res5"]` | 输出特征名 |
| `ResNet` | freeze | `.freeze(2)` | 冻结前 2 个 stage |
| `FPN` | out_channels | `256` | FPN 每级通道 |
| `FPN` | top_block | `LastLevelMaxPool()` | 增加 p6 |
| `StandardRPNHead` | in_channels / num_anchors | `256` / `3` | RPN head 输入通道与每点锚点数 |
| `DefaultAnchorGenerator` | sizes | `[[32],[64],[128],[256],[512]]` | 5 级 anchor 边长 |
| `DefaultAnchorGenerator` | aspect_ratios | `[0.5, 1.0, 2.0]` | 宽高比 |
| `DefaultAnchorGenerator` | strides | `[4, 8, 16, 32, 64]` | 各层下采样步长 |
| `DefaultAnchorGenerator` | offset | `0.0` | anchor 中心偏移 |
| `Matcher` (RPN) | thresholds / labels / low-quality | `[0.3, 0.7]` / `[0, -1, 1]` / `True` | IoU 阈值划分 fg/bg/ignore |
| `Box2BoxTransform` (RPN) | weights | `[1.0, 1.0, 1.0, 1.0]` | 框回归权重 |
| `RPN` | batch_size_per_image | `256` | 每图采样 proposal 数 |
| `RPN` | positive_fraction | `0.5` | 正样本占比 |
| `RPN` | pre_nms_topk | `(2000, 1000)` | (train, test) NMS 前 top-k |
| `RPN` | post_nms_topk | `(1000, 1000)` | (train, test) NMS 后 top-k |
| `RPN` | nms_thresh | `0.7` | NMS IoU 阈值 |
| `StandardROIHeads` | num_classes | `80` | COCO 类别数 |
| `StandardROIHeads` | batch_size_per_image | `512` | 每图采样 ROI 数 |
| `StandardROIHeads` | positive_fraction | `0.25` | 正样本占比 |
| `Matcher` (ROI) | thresholds / labels / low-quality | `[0.5]` / `[0, 1]` / `False` | 比 RPN 更严格的 ROI 匹配 |
| `ROIPooler` (box) | output_size / scales / sampling / type | `7` / `(1/4,1/8,1/16,1/32)` / `0` / `"ROIAlignV2"` | ROI Align 输出 7×7 |
| `FastRCNNConvFCHead` | ShapeSpec | `channels=256, h=7, w=7` | head 输入 |
| `FastRCNNConvFCHead` | conv_dims / fc_dims | `[]` / `[1024, 1024]` | 仅 FC 层,1024→1024 |
| `FastRCNNOutputLayers` | ShapeSpec | `channels=1024` | 预测器输入 |
| `FastRCNNOutputLayers` | test_score_thresh | `0.05` | 推理时分数阈值 |
| `Box2BoxTransform` (ROI) | weights | `(10, 10, 5, 5)` | xy/wh 回归权重 |
| `ROIPooler` (mask) | output_size / scales / sampling / type | `14` / `(1/4,1/8,1/16,1/32)` / `0` / `"ROIAlignV2"` | mask ROI Align 14×14 |
| `MaskRCNNConvUpsampleHead` | ShapeSpec | `channels=256, h=14, w=14` | mask head 输入 |
| `MaskRCNNConvUpsampleHead` | conv_dims | `[256, 256, 256, 256, 256]` | 5 层 256 通道卷积 |
| `GeneralizedRCNN` | pixel_mean | `[103.530, 116.280, 123.675]` | BGR 像素均值 |
| `GeneralizedRCNN` | pixel_std | `[1.0, 1.0, 1.0]` | 像素标准差 |
| `GeneralizedRCNN` | input_format | `"BGR"` | 输入通道顺序 |

---

## 【公式解读】

**原文无公式**(全文没有 LaTeX 或伪代码形式的数学公式;所有数值均为参数列表形式出现)。

---

## 【关联】

原文指向的内部文档(均位于同一 `docs/tutorials/` 目录):

- `./getting_started.md` —— "Beginner's Tutorial":如果仅需标准默认行为,该教程就足够;本文是它的"扩展版"前置说明,告诉用户在标准流程不够用时才进入下文。
- `./datasets.md` —— "Use Custom Datasets":针对内置数据集不够用时,自定义数据集的接入方式。
- `./data_loading.md` —— "Use Custom Data Loaders":当默认 `data loader` 逻辑不满足需求时,如何编写自己的 dataloader。
- `./models.md` —— "Use Models":如何覆盖 detectron2 内置标准模型的行为(对应本文"显式参数/积木式组件"那条路径)。
- `./write-models.md` —— "Write Models":如何从零编写新模型(对应"打破现有抽象并替换"的设计目标)。
- `./training.md` —— "training":默认训练循环及其 hook 机制,或自定义训练循环。
- `../../modules/config.html#detectron2.config.configurable` —— `@configurable` 装饰器的 API 文档,本文提到的"实验性"第三类接口(`@configurable`)即来自此模块。

整体上下游关系(基于原文表述):

```
extend.md(本文:哲学+Mask R-CNN 显式拼装示例)
  │
  ├─→ getting_started.md  ← 标准默认路径起点
  │
  ├─→ datasets.md         ← 数据集层扩展(下游数据源)
  ├─→ data_loading.md     ← 数据加载层扩展(数据集 → 模型之间的衔接)
  │
  ├─→ models.md           ← 在已有模型上覆盖行为
  ├─→ write-models.md     ← 从零写新模型(backbone/proposal_generator/roi_heads 等积木的完全替换)
  │
  ├─→ training.md         ← 训练循环与 hook 扩展
  │
  └─→ config.html#detectron2.config.configurable ← @configurable 装饰器,
        是"cfg-only / 显式参数"双形态 API 的实现机制
```

原文的设计逻辑:配置(cfg)驱动 → 数据(dataset/loader) → 模型(backbone/proposal_generator/roi_heads,即可被积木式替换) → 训练循环(可注入 hook)。本文是这条扩展链路最顶层的"哲学 + 入口"文档,下面的 6 篇教程分别对应其中的一个环节。

---

## 【使用方法】

原文未给出具体命令、配置文件示例或启用步骤;它是一篇**概念性 + 示例代码**的导读。原文给出的、与"使用方式"相关的直接陈述如下:

1. **判断使用路径**:
   - "If you only need the standard behavior, the [Beginner's Tutorial](./getting_started.md) should suffice." —— 仅需标准行为 → 走 `getting_started.md`。
   - "If you need to extend detectron2 to your own needs, see the following tutorials for more details." —— 需要扩展 → 按需求跳转:
     - 自定义数据集 → `./datasets.md`
     - 自定义 dataloader → `./data_loading.md`
     - 覆盖/扩展模型行为 → `./models.md` 与 `./write-models.md`
     - 自定义训练流程(hook 或自有循环) → `./training.md`

2. **使用 `@configurable` 双形态调用**:由 `../../modules/config.html#detectron2.config.configurable` 提供,既可 `MyClass(cfg)` 也可 `MyClass(arg1=..., arg2=...)`,但原文明确指出"their explicit argument interfaces are currently experimental and subject to change"。

3. **显式构造 Mask R-CNN 的方式**(原文代码块):直接 `import` 各积木类(`GeneralizedRCNN`、`FPN`、`ResNet`、`BasicStem`、`BottleneckBlock`、`LastLevelMaxPool`、`RPN`、`StandardRPNHead`、`DefaultAnchorGenerator`、`Matcher`、`Box2BoxTransform`、`StandardROIHeads`、`ROIPooler`、`FastRCNNConvFCHead`、`FastRCNNOutputLayers`、`MaskRCNNConvUpsampleHead`、`ShapeSpec`)并按原文括号内的全部参数实例化,得到一个等价的、不依赖 cfg 的 Mask R-CNN。

> **原文未涉及**:具体的安装命令、命令行启动方式、yaml config 文件路径、训练/评估脚本、超参搜索或环境变量配置等"运行级"步骤——这些都在 `getting_started.md` 等下游教程中。
