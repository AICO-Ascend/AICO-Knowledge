# Extend Detectron2's Defaults

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/FasterRCNN_ID0100_for_PyTorch/docs/tutorials/extend.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/FasterRCNN_ID0100_for_PyTorch/docs/tutorials/extend.md

# 一体化深度解读：Detectron2 「Extend Default」 文档

---

## 【定位】

这篇文档解决「**Detectron2 在面对研究型二次开发需求时，如何在「保持高层抽象易用性」与「允许底层灵活替换」之间取得平衡**」的问题——它定义了 detectron2 的三层扩展接口（config 风格、显式参数风格、`@configurable` 装饰器风格），并给出一个完整 Mask R-CNN 的显式构造样例，让用户知道当标准默认行为不够用时如何「拼接」自己的系统。

---

## 【技术要点】

1. **detectron2 的三层接口并存策略**——为应对「研究需要新做法」与「标准任务易用性」的张力，把接口拆为三层：① 接受 `cfg` 的「标准默认」函数/类；② 只接受显式参数的「小积木」函数/类；③ 用 `@configurable` 装饰、可同时用 cfg 或显式参数调用的实验性类。
2. **config 风格接口 = 标准默认实现**：函数/类从 `cfg` 中读取所需项并执行「标准」操作，用户只需加载配置并传递，无需关心每个参数的含义。
3. **显式参数接口 = 灵活拼接组件**：每个组件只接受定义良好的显式参数，需要用户具备专业知识才能正确组合；这些组件可在标准默认之外被灵活复用。
4. **`@configurable` 装饰器是实验性接口**：允许同一类既接受 config 也接受显式参数，原文明确标注其「显式参数接口为 experimental，subject to change」。
5. **Mask R-CNN 显式构造示例**展示了完整可堆叠的积木组合：`GeneralizedRCNN` 内部嵌套 `FPN`（含 `ResNet`/`BasicStem`/`BottleneckBlock`/`LastLevelMaxPool`）+ `RPN`（含 `StandardRPNHead`/`DefaultAnchorGenerator`/`Matcher`/`Box2BoxTransform`）+ `StandardROIHeads`（含 `FastRCNNConvFCHead`/`FastRCNNOutputLayers`/`MaskRCNNConvUpsampleHead`/`ROIPooler`）+ 像素归一化参数。
6. **新手与扩展的分流**：原文明确「如果只要标准行为，看 [Beginner's Tutorial] 即可；要扩展则看 datasets / data_loading / models / write-models / training 五篇教程」。

---

## 【关键机制与数据】

### 工作原理（原文核心论断）

- **抽象层级的张力**（原文：「Research is about doing things in new ways」）——detectron2 必须同时具备**薄抽象**（允许突破既有抽象、替换为新实现）与**高层抽象**（让普通用户无需关心细节），通过两层接口共同化解。
- **「config 风格」与「显式参数风格」的边界**：原文：「Such functions and classes implement the 'standard default' behavior」对应第①类；「Each of these is a small building block of the entire system」对应第②类。
- **「`@configurable` 装饰器」的混合调用能力**：原文明确说它们「can be called with either a config, or with explicit arguments」，并标注显式参数接口「currently experimental and subject to change」。

### 代码示例中的关键数值（原文 Mask R-CNN 显式构造）

| 组件 | 关键数值 / 配置（原文） | 备注 |
|---|---|---|
| `BasicStem` | `(3, 64)` | 输入 3 通道，输出 64 通道 stem |
| ResNet stages | 块数 `[3, 4, 6, 3]`，步长 `[1, 2, 2, 2]`，输入通道 `[64, 256, 512, 1024]`，瓶颈/输出通道比 `o // 4 : o` | 对应 ResNet-50 的典型 stage 配置；stride_in_1x1=True |
| `freeze(2)` | 冻结前 2 个 stage | 常用迁移学习设置 |
| FPN | `out_features=["res2","res3","res4","res5"]`，`in_features` 同上，out dim `256`，`top_block=LastLevelMaxPool()` | 生成 p2–p6 共 5 个层级 |
| RPN `in_features` | `["p2","p3","p4","p5","p6"]` | 与 FPN 输出 + top block 一致 |
| `StandardRPNHead` | `in_channels=256, num_anchors=3` | FPN 通道 = 256，每点 3 个 anchor |
| `DefaultAnchorGenerator` | `sizes=[[32],[64],[128],[256],[512]]`，`aspect_ratios=[0.5, 1.0, 2.0]`，`strides=[4, 8, 16, 32, 64]`，`offset=0.0` | 5 级 anchor 尺寸，分别对应 p2–p6 步长 |
| `Matcher` (RPN) | 阈值 `[0.3, 0.7]`，标签 `[0, -1, 1]`，`allow_low_quality_matches=True` | RPN 阶段 IoU 匹配规则 |
| `Box2BoxTransform` (RPN) | `[1.0, 1.0, 1.0, 1.0]` | 编码时 Δx,Δy,Δw,Δh 的方差权重 |
| RPN 采样 | `batch_size_per_image=256, positive_fraction=0.5` | 每图 256 个 anchor，正样本占 50% |
| RPN topk | `pre_nms_topk=(2000, 1000)`，`post_nms_topk=(1000, 1000)` | 训练/推断时的 topk |
| RPN NMS | `nms_thresh=0.7` | RPN 后处理 |
| `StandardROIHeads` | `num_classes=80, batch_size_per_image=512, positive_fraction=0.25` | COCO 80 类，每图采样 512 个 proposal，正样本 25% |
| `proposal_matcher` | IoU `[0.5]`，标签 `[0, 1]`，`allow_low_quality_matches=False` | Fast R-CNN 阶段匹配 |
| `box_in_features` | `["p2","p3","p4","p5"]` | 检测头使用的 FPN 层级 |
| `box_pooler` | 输出 `7`，采样率 `(1/4, 1/8, 1/16, 1/32)`，`pooler_type="ROIAlignV2"` | RoIAlign 到 7×7 |
| `box_head` | `FastRCNNConvFCHead`，`conv_dims=[]`，`fc_dims=[1024, 1024]` | 无 conv，全连接 1024→1024 |
| `box_predictor` | 输入 1024 维，`test_score_thresh=0.05`，`Box2BoxTransform((10, 10, 5, 5))`，`num_classes=80` | class-agnostic bbox 回归标准差 10,10,5,5 |
| `mask_pooler` | 输出 `14`，采样率同 box，`pooler_type="ROIAlignV2"` | mask 分支 14×14 |
| `mask_head` | `MaskRCNNConvUpsampleHead`，输入 `channels=256, width=14, height=14`，`num_classes=80`，`conv_dims=[256, 256, 256, 256, 256]` | mask head 5 层 conv 后上采样 |
| 像素归一化 | `pixel_mean=[103.530, 116.280, 123.675]`，`pixel_std=[1.0, 1.0, 1.0]`，`input_format="BGR"` | 与 Caffe 风格预训练模型一致的 BGR 均值 |

> 注：原文未给出性能数据（mAP、速度等），故此处不臆造。

---

## 【表格解读】

**原文无表格**（文档中包含的代码块为可折叠的 Python 示例，非表格）。上一节「关键机制与数据」中所列参数表为我根据代码块按组件维度重新整理的导读表格，便于阅读，但不属原文表格。

---

## 【公式解读】

**原文无公式**。文档中无 LaTeX 或伪代码形式的数学公式，仅含 Python 构造代码与正文的概念性描述。

---

## 【关联】

利用文末的内部链接信息，可梳理出 detectron2 扩展体系的导航图：

- **入口与定位**
  - `./getting_started.md`（新手教程）—— 原文明确「如果只需要标准行为，看这个教程即可」，与本文是「标准 vs 扩展」的二选一入口关系。
  - `./datasets.md` —— 覆盖标准数据集之外的「**自定义数据集**」扩展路径。
  - `./data_loading.md` —— 覆盖 `train/test` 数据加载逻辑的**自定义 DataLoader**。
  - `./models.md` 与 `./write-models.md` —— 前者描述「**如何改写现有模型行为**」（overwrite），后者描述「**如何写新模型**」（write new）。本文给出的 Mask R-CNN 显式构造示例正是这两篇文档所讨论能力的最小可运行缩影。
  - `./training.md` —— 默认训练循环 + Hook 自定义 + 自写训练循环，与本文示例中的 batch_size / positive_fraction / pre_nms_topk 等训练相关参数相互呼应。

- **底层机制引用**
  - `../../modules/config.html#detectron2.config.configurable` —— `@configurable` 装饰器的 API 参考。本文反复强调该装饰器为「experimental」接口，详细信息需跳转该锚点查阅。

- **上下游逻辑链**
  - 横向并列：datasets / data_loading / models / write-models / training 五篇教程共同构成「**detectron2 完整扩展面**」；本文是它们的导览页。
  - 上下游：本文与 `configurable` API 文档之间是「教程层 ↔ 模块参考层」的关系；本文与 `getting_started.md` 之间是「高级扩展 ↔ 入门标准用法」的关系。

---

## 【使用方法】

**原文未涉及具体的启用命令、配置文件路径或启动参数**——本文档是一篇概念性 / 设计哲学性 guide，没有给出 CLI、yaml 配置或 shell 命令。

但文档隐含的「**使用方法**」可归纳如下（仅基于原文表述）：

1. **何时使用 config 风格（标准默认）**：当任务与 detectron2 内置标准实现一致时，按 `./getting_started.md` 的方式加载默认配置并运行。
2. **何时使用显式参数风格（小积木）**：当标准默认无法满足需求时，按本文给出的 Mask R-CNN 示例那样，直接用 `GeneralizedRCNN(backbone=..., proposal_generator=..., roi_heads=..., pixel_mean=..., pixel_std=..., input_format=...)` 的方式**逐组件显式构造**。
3. **何时使用 `@configurable` 装饰器接口**：当希望同一组件既能通过 config 也能通过显式参数调用时使用，但原文明确标注其「显式参数接口为 experimental and subject to change」。
4. **遇到具体场景时跳转对应教程**：
   - 自定义数据集 → `./datasets.md`
   - 自定义数据加载 → `./data_loading.md`
   - 改写现有模型行为 → `./models.md`
   - 写新模型 → `./write-models.md`
   - 自定义训练循环 / Hook → `./training.md`

> 仓库中本路径位于 `FasterRCNN_ID0100_for_PyTorch/docs/tutorials/extend.md`，其作为 detectron2 上游教程的转载/镜像，本身不附带额外的启用步骤；具体命令、yaml 字段、训练启动方式均不在本文档范围内，需查阅 `getting_started.md` 及各分项教程。
