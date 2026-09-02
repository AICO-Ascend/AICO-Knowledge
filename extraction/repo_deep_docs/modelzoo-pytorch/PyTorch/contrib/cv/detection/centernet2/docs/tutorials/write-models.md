# Write Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/centernet2/docs/tutorials/write-models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/centernet2/docs/tutorials/write-models.md

# 深度解读:Write Models

## 【定位】

这篇文档解决「如何在 detectron2 中扩展/定制检测模型」的问题——描述了两种把自定义实现接入现有模型体系的能力:**通过注册机制(registry)将新组件挂载到配置系统**,以及**通过显式参数构造直接用代码覆盖内部模块**。

---

## 【技术要点】

1. **注册机制(Registry)**:对"骨干网络(box head / box predictor / ROI heads)"等高频需要替换的组件,提供 `BACKBONE_REGISTRY`、`ROI_HEADS_REGISTRY` 等注册表,用户通过 `@XXX_REGISTRY.register()` 装饰器把自定义类注入,之后在 config 文件里只需用名字就能调用。
2. **`Backbone` 接口契约**:任何注册到 `BACKBONE_REGISTRY` 的子类必须实现两个方法——`forward(image)` 返回 `dict[str, Tensor]`(以特征名为键),以及 `output_shape()` 返回 `dict[str, ShapeSpec]`(同样以特征名为键,值为 `ShapeSpec`)。
3. **`ToyBackbone` 范例参数**:示例骨干包含 `nn.Conv2d(3, 64, kernel_size=7, stride=16, padding=3)`,对应 `ShapeSpec(channels=64, stride=16)`,即输入 3 通道 RGB、下采样 16 倍、输出 64 通道特征图。
5. **配置端绑定**:`cfg.MODEL.BACKBONE.NAME = 'ToyBackone'`(原文写 `ToyBackbone`) + `build_model(cfg)` 是从配置名到代码实现的链路。
6. **显式参数构造(`configurable __init__`)**:对于注册表覆盖不到的更细粒度修改,可直接实例化组件并显式传入参数;原文示例中通过把 `box_predictor=MyRCNNOutput(...)` 传给 `StandardROIHeads(cfg, backbone.output_shape(), ...)` 来替换 Faster R-CNN 的 box head 损失函数。
7. **可选的二次注册**:若想让新的 `StandardROIHeads` 变体也能从 config 文件启用,则再写一个继承类并用 `@ROI_HEADS_REGISTRY.register()` 包一层,固定写死 `box_predictor=MyRCNNOutput(...)`。

---

## 【关键机制与数据】

**工作原理 / 数据流(基于原文描述):**

- **原文:** "we provide a registration mechanism for users to inject custom implementation that will be immediately available to use in config files." —— 注册器充当"配置字符串 → Python 类"的桥接层。
- **原文:** "After importing this code, detectron2 can link the name of the class to its implementation." —— 类的"名字"是注册键,导入模块即触发注册生效。
- **原文:** "Most model components in detectron2 have a clear `__init__` interface that documents what input arguments it needs." —— 由于各组件的 `__init__` 都是显式签名,因此可以绕过 config,直接用 Python 调用构造。
- **原文:** "this can be easily achieved by using the configurable `__init__` mechanism" —— `configurable` 装饰器保证默认参数可以从 cfg 中填充,用户只需覆盖想改的那几个 kwargs。
- **原文:** "Losses are currently computed in FastRCNNOutputLayers" —— 自定义 loss 的注入点就是替换该类(而非修改训练循环)。

**性能数据:** 原文未提供任何 benchmark / 数值性能指标,本节无可写数据。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式(文档中仅含 Python 代码片段,不涉及数学表达式或伪代码公式)。

---

## 【关联】

本文处于「如何扩展 detectron2 模型」的教程位置,与下列内部模块/项目相互引用:

- 骨干注册接口:[`Backbone`](../modules/modeling.html#detectron2.modeling.Backbone) 是所有自定义骨干必须继承的抽象基类;[`BACKBONE_REGISTRY`](../modules/modeling.html#detectron2.modeling.BACKBONE_REGISTRY) 是其注册容器。
- 检测头扩展入口:[`ROIHeads`](../modules/modeling.html#detectron2.modeling.ROIHeads) 是 Generalized R-CNN 中 ROI 阶段的可替换抽象类;[`FastRCNNOutputLayers`](../modules/modeling.html#detectron2.modeling.FastRCNNOutputLayers) 是其中计算分类/回归损失的具体类,也是文档示例中"自定义 loss"的改写目标。
- 注册表全集:[`model-registries`](../modules/modeling.html#model-registries) 汇总了所有可用的 registry(`BACKBONE_REGISTRY`、`ROI_HEADS_REGISTRY` 等),本文是它们的"使用入口教程"。
- 配套示例项目:[`projects/DensePose`](../projects/DensePose) 与 [MeshRCNN](https://github.com/facebookresearch/meshrcnn) 是文档点名的两个"通过新 ROIHeads 实现新任务"的范例;更广泛的项目集合见 [`projects/`](../projects/) 目录,提供"实现不同整体架构"的更多例子。
- 配置装饰器:[`configurable`](../modules/config.html#detectron2.config.configurable) 是 `__init__` 参数默认从 cfg 取值的机制,是"显式参数构造"小节能简洁覆盖默认参数的关键。

---

## 【使用方法】

**方式 A:注册自定义组件(从 config 启用)**

1. 在自己的代码中定义一个继承自 `Backbone` 的类,实现 `forward()` 与 `output_shape()`,并加 `@BACKBONE_REGISTRY.register()` 装饰器。
2. 在加载 `build_model(cfg)` **之前** `import` 包含该类的模块。
3. 在 config 中(或代码里)设置:
   ```python
   cfg.MODEL.BACKBONE.NAME = 'ToyBackbone'
   ```
4. 调用 `build_model(cfg)` 即可让框架自动找到 `ToyBackbone`。

**方式 B:显式参数构造(代码级覆盖,无需注册)**

1. 写一个 `FastRCNNOutputLayers` 的子类(或变体) `MyRCNNOutput`,在其中放入自定义 loss。
2. 实例化 `StandardROIHeads` 时把 `box_predictor` 替换掉:
   ```python
   roi_heads = StandardROIHeads(
       cfg, backbone.output_shape(),
       box_predictor=MyRCNNOutput(...)
   )
   ```
   其余参数由 `configurable __init__` 自动从 `cfg` 填充,无需逐个手写。

**方式 C:把"方式 B 的结果"再注册回配置系统(可选)**

若希望这个带 `MyRCNNOutput` 的 `StandardROIHeads` 变体也能从 config 文件启用,新建一个继承类并固定 `box_predictor=MyRCNNOutput(...)`,再用 `@ROI_HEADS_REGISTRY.register()` 装饰,之后通过 config 中的对应名字引用即可。

**命令行 / 启动脚本:** 原文未涉及具体 CLI 启动命令或训练脚本入口;相关使用方式以"导入模块 → 构建模型"的 Python API 为主。
