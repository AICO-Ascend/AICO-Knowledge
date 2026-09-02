# Extend Detectron2's Defaults

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/Cascade_RCNN/docs/tutorials/extend.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/Cascade_RCNN/docs/tutorials/extend.md

# Detectron2 扩展默认值文档深度解读

## 【定位】

这篇文档解决 Detectron2 中"研究灵活性"与"工程抽象性"之间的设计张力问题,描述如何通过两种互补的接口形式（基于 `cfg` 的高级接口 + 显式参数的细粒度接口）来扩展或替换框架的默认行为,使研究者在保留默认便利的同时可深入替换各组件。

## 【技术要点】

1. **三层接口设计哲学**:文档明确指出 Detectron2 用两类接口协同解决抽象层级问题——(a) 接收 `cfg` 的"标准默认"函数/类,只需加载 config 即可工作;(b) 接受显式参数的"小型积木"组件,可灵活拼装;(c) 实验性的 `@configurable` 装饰器,使组件能同时接受 `cfg` 或显式参数。

2. **`@configurable` 装饰器机制**(链接: `../../modules/config.html#detectron2.config.configurable`):被装饰的类可被两种方式调用,但显式参数接口标注为 **experimental**,API 可能变动。

3. **完整 Mask R-CNN 显式构造示例**:文档给出一段可展开的 Python 代码,演示完全用显式参数从零构建 `GeneralizedRCNN`,涉及骨干网络、区域提议网络(RPN)、ROI 头、像素归一化等所有子组件。

4. **ResNet + FPN 骨干的具体参数**:四阶段 BottleneckBlock 的 `(n, s, i, o)` 分别为 `(3,1,64,256)`、`(4,2,256,512)`、`(6,2,512,1024)`、`(3,2,1024,2048)`;`BasicStem(3, 64)`;FPN 输出通道 `256`,`top_block=LastLevelMaxPool()`,冻结前 2 个 stage (`.freeze(2)`)。

5. **RPN 子组件关键数字**:`in_features=["p2"…"p6"]`(5 个层级);`num_anchors=3`;anchor 尺寸 `[[32],[64],[128],[256],[512]]`;aspect_ratios `[0.5, 1.0, 2.0]`;strides `[4,8,16,32,64]`;`Matcher([0.3, 0.7], [0, -1, 1], allow_low_quality_matches=True)`;`batch_size_per_image=256`、`positive_fraction=0.5`;`pre_nms_topk=(2000, 1000)`、`post_nms_topk=(1000, 1000)`、`nms_thresh=0.7`;编码/解码权重 `Box2BoxTransform([1.0, 1.0, 1.0, 1.0])`。

6. **ROI Heads 与像素归一化**:`num_classes=80`;box 头 `batch_size_per_image=512`、`positive_fraction=0.25`、proposal `Matcher([0.5], [0, 1])`;box/mask `ROIPooler` 分别使用输出尺寸 7 与 14,采样率 `(1/4, 1/8, 1/16, 1/32)`,池化类型 `"ROIAlignV2"`;`box_predictor` 的 `test_score_thresh=0.05`、delta 权重 `(10, 10, 5, 5)`;mask head 5 层卷积 `conv_dims=[256]*5`;像素均值 `pixel_mean=[103.530, 116.280, 123.675]`、`pixel_std=[1.0, 1.0, 1.0]`、输入格式 `input_format="BGR"`。

## 【关键机制与数据】

工作原理(原文):

- **默认路径**:对于仅需标准行为的用户,只需 `cfg`,函数/类从 config 中读取所需参数并执行"标准"动作,用户无需关心具体参数含义。
- **扩展路径**:当需要实现 detectron2 默认未覆盖的功能时,显式参数接口提供"小型积木",允许研究者拼接新系统(代价是需要专业知识和更多组装工作)。
- **数据流(以 Mask R-CNN 显式构造为例,原文)**:图像输入先经 `pixel_mean/std` + `BGR` 归一化 → `FPN(ResNet)` 输出 `res2-res5` 五个特征层 → `RPN` 在 `p2-p6` 5 个层级上以 3 种 anchor 尺寸(实际为 sizes×aspect_ratios=3 种宽高比)、stride 4/8/16/32/64 产生 proposals,经 `nms_thresh=0.7`、IoU 阈值 `[0.3, 0.7]` 的 `Matcher` 分配标签后,送入 `StandardROIHeads` → box 分支在 `p2-p5` 上以 `ROIPooler(7, ROIAlignV2)` 提取特征,经 `FastRCNNConvFCHead`(`fc_dims=[1024,1024]`)和 `FastRCNNOutputLayers`(80 类、delta 权重 `(10,10,5,5)`)得到检测;mask 分支在 `p2-p5` 上以 `ROIPooler(14, ROIAlignV2)` 提取特征,经 5 层 256 通道卷积的 `MaskRCNNConvUpsampleHead` 输出 80 类 mask。
- **性能数据**:原文未给出任何性能数字(无 mAP、速度、显存等指标)。

## 【表格解读】

**原文无表格**。

(说明:文档中虽有一段较长的 Python 代码块作为 Mask R-CNN 显式构造示例,但**原文本身未以表格形式**呈现任何参数表/性能对比/配置项清单,因此按"无表格写'原文无表格'"规则如实标注。代码示例中的具体参数已在【技术要点】中按原文逐字保留。)

## 【公式解读】

**原文无公式**。

(说明:文档未包含任何 LaTeX 数学公式或伪代码形式的算式表达,所有配置均以 Python 关键字参数形式给出。)

## 【关联】

文档末尾给出一条分流路径和五条横向教程链接,上下游关系如下(原文):

- **行为分级**:
  - 仅需标准行为 → 跳转 [Beginner's Tutorial](./getting_started.md)。
  - 需自定义 → 进入下述四条横向扩展教程。

- **数据侧**(上游数据相关):
  - 自定义数据集 → [Use Custom Datasets](./datasets.md)。
  - 自定义数据加载 → [Use Custom Data Loaders](./data_loading.md)。

- **模型侧**(模型结构相关):
  - 覆盖现有模型行为 → [Use Models](./models.md)。
  - 从零编写新模型 → [Write Models](./write-models.md)。

- **训练侧**(下游训练相关):
  - 自定义或重写训练循环 → [training](./training.md)。

- **装饰器 API 锚点**:文中关于 `@configurable` 实验性装饰器的说明通过相对路径 `../../modules/config.html#detectron2.config.configurable` 链接到模块 API 参考页(不属教程系列,属于工具/参考文档层)。

## 【使用方法】

启用方式/配置项/命令(原文有则写,无则写"原文未涉及"):

- **启用方式**:
  1. **走默认路径(无需扩展)**:按 [Beginner's Tutorial](./getting_started.md) 的方法加载 config 并直接使用 detectron2 提供的标准入口。
  2. **走扩展路径**:导入本教程代码示例中的具体类(`GeneralizedRCNN`、`FPN`、`ResNet`、`BasicStem`、`BottleneckBlock`、`RPN`、`StandardRPNHead`、`DefaultAnchorGenerator`、`Matcher`、`Box2BoxTransform`、`StandardROIHeads`、`ROIPooler`、`FastRCNNConvFCHead`、`FastRCNNOutputLayers`、`MaskRCNNConvUpsampleHead`、`ShapeSpec`、`LastLevelMaxPool`),用显式参数实例化后拼装新模型或新流水线,再接入对应的 [datasets.md](./datasets.md)、[data_loading.md](./data_loading.md) 与 [training.md](./training.md) 流程。

- **配置项(原文直接列出的关键参数,用于替代默认 cfg)**:
  - 骨干:`out_features=["res2","res3","res4","res5"]`,FPN `out_channels=256`,`top_block=LastLevelMaxPool()`,`.freeze(2)`。
  - RPN:`in_features=["p2","p3","p4","p5","p6"]`,`num_anchors=3`,`sizes=[[32],[64],[128],[256],[512]]`,`aspect_ratios=[0.5,1.0,2.0]`,`strides=[4,8,16,32,64]`,`offset=0.0`,`Matcher([0.3,0.7],[0,-1,1], allow_low_quality_matches=True)`,`Box2BoxTransform([1.0,1.0,1.0,1.0])`,`batch_size_per_image=256`,`positive_fraction=0.5`,`pre_nms_topk=(2000,1000)`,`post_nms_topk=(1000,1000)`,`nms_thresh=0.7`。
  - ROI Heads:`num_classes=80`,`batch_size_per_image=512`,`positive_fraction=0.25`,`Matcher([0.5],[0,1], allow_low_quality_matches=False)`,`box_in_features=["p2","p3","p4","p5"]`,box `ROIPooler(7,(1/4,1/8,1/16,1/32),0,"ROIAlignV2")`,`box_head=FastRCNNConvFCHead(ShapeSpec(channels=256,height=7,width=7), conv_dims=[], fc_dims=[1024,1024])`,`box_predictor=FastRCNNOutputLayers(ShapeSpec(channels=1024), test_score_thresh=0.05, box2box_transform=Box2BoxTransform((10,10,5,5)), num_classes=80)`,`mask_in_features=["p2","p3","p4","p5"]`,mask `ROIPooler(14,(1/4,1/8,1/16,1/32),0,"ROIAlignV2")`,`mask_head=MaskRCNNConvUpsampleHead(ShapeSpec(channels=256,width=14,height=14), num_classes=80, conv_dims=[256,256,256,256,256])`。
  - 输入归一化:`pixel_mean=[103.530,116.280,123.675]`,`pixel_std=[1.0,1.0,1.0]`,`input_format="BGR"`。

- **命令**:原文未涉及具体命令行(无 shell 命令、CLI flag 或 `python -m ...` 调用)。

- **注意事项(原文)**:`@configurable` 装饰器下的"显式参数接口"被明确标注为 **experimental and subject to change**,生产/长期代码应优先使用基于 `cfg` 的标准默认接口,或参考 [models.md](./models.md) / [write-models.md](./write-models.md) 提供的稳定扩展模式。
