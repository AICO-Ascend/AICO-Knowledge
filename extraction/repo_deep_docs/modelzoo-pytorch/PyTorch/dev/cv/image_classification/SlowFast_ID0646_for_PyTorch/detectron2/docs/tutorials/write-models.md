# Write Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/write-models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/write-models.md

# 深度解读: detectron2 "Write Models" 教程

## 【定位】
本篇文档解决「在 detectron2 既有标准模型 (如 Generalized R-CNN) 基础上, 如何以最小代价注入/替换特定组件 (backbone、ROI heads、box predictor 等)」的问题, 同时描述「文本配置无法表达时的代码级深度定制」能力。

## 【技术要点】
1. **Registry 注册机制**: 通过 `@XXX_REGISTRY.register()` 装饰器把继承自特定基类 (如 `Backbone`、`ROIHeads`) 的自定义类注册到全局注册表中, 使 cfg 中字符串字段能映射到具体实现。
2. **Backbone 接口契约**: 自定义 backbone 必须实现三个成员 — `__init__(self, cfg, input_shape)`、`forward(self, image)` 返回 `dict[str, Tensor]`、`output_shape(self)` 返回 `dict[str, ShapeSpec]`; `ShapeSpec` 用来声明每个特征层的 `channels` 与 `stride`。
3. **示例 ToyBackbone**: 单层 `nn.Conv2d(3, 64, kernel_size=7, stride=16, padding=3)`, 输出特征名 `"conv1"`, `ShapeSpec(channels=64, stride=16)`。
4. **配置端启用**: 导入自定义代码后, 只需 `cfg.MODEL.BACKBONE.NAME = 'ToyBackbone'` 即可让 `build_model(cfg)` 自动构造模型。
5. **ROI heads 扩展**: 新建 `ROIHeads` 子类并注册到 `ROI_HEADS_REGISTRY` 即可改变 Generalized R-CNN 的检测头; `DensePose` 与 `MeshRCNN` 是官方两个实例。
6. **配置 + 代码混合定制**: 在 FastRCNNOutputLayers 上加自定义 loss, 再用 `configurable.__init__` 机制把 `box_predictor=MyRCNNOutput(...)` 传给 `StandardROIHeads`, 可只替换部分参数而不重写全部初始化逻辑。

## 【关键机制与数据】
**Registry 作为「名字→实现」的桥接机制**: 文档原文明确「detectron2 can link the name of the class to its implementation」, 注册名 (即注册时使用的类名字符串) 必须与 cfg 中对应字段 (如 `MODEL.BACKBONE.NAME`) 完全一致, `build_model` 才能在构造时查到目标类。

**两阶段定制流程 (以 Faster R-CNN box head 加自定义 loss 为例)**:
- 阶段 1 (必须): 实现 `FastRCNNOutputLayers` 的子类/变体 `MyRCNNOutput`, 重写 loss 相关计算 (原文未给出具体数值公式)。
- 阶段 2 (必须): 调用 `StandardROIHeads(cfg, backbone.output_shape(), box_predictor=MyRCNNOutput(...))` 显式替换默认 `FastRCNNOutputLayers`。
- 阶段 3 (可选): 把上述组合包成 `MyStandardROIHeads` 并 `@ROI_HEADS_REGISTRY.register()`, 使之也能通过 cfg 启用。

**数据流 (ToyBackbone)**:
`image (Tensor)` → `nn.Conv2d(3, 64, k=7, s=16, p=3)` → `{"conv1": feature_map}` (shape 由 `ShapeSpec(channels=64, stride=16)` 声明)。`output_shape()` 输出的 stride=16 是下游 FPN / 头网络对齐 anchor 步长的关键。

> 原文未提供任何 benchmark 数字、训练耗时、精度指标等性能数据。

## 【表格解读】
**原文无表格**。

## 【公式解读】
**原文无公式**。
(唯一可视为伪代码/算式描述的是 `nn.Conv2d(3, 64, kernel_size=7, stride=16, padding=3)` 这一调用, 已在上文技术要点中逐参数解释; 不构成数学公式。)

## 【关联】
- 与 **`Backbone` 基类** (../modules/modeling.html#detectron2.modeling.Backbone): 注册自定义 backbone 必须继承自该抽象类, 实现其 `forward` 与 `output_shape` 接口。
- 与 **`BACKBONE_REGISTRY`** (../modules/modeling.html#detectron2.modeling.BACKBONE_REGISTRY): 注册表的运行时容器, 装饰器 `@BACKBONE_REGISTRY.register()` 是注册动作的入口。
- 与 **`ROIHeads` 基类** (../modules/modeling.html#detectron2.modeling.ROIHeads): Generalized R-CNN 中检测头 (包括 box/mask/keypoint 分支) 的抽象基类, 自定义任务 (如 DensePose) 通过其子类注入。
- 与 **`FastRCNNOutputLayers`** (../modules/modeling.html#detectron2.modeling.FastRCNNOutputLayers): box head 默认输出层, 文档中「自定义 loss」一节的修改切入点。
- 与 **`configurable.__init__`** (../modules/config.html#detectron2.config.configurable): 让组件构造函数既能从 cfg 取参数, 又能被显式关键字参数覆盖, 是「只换一两个组件、其余保持默认」的关键支撑。
- 与 **`projects/`** (../../projects/) 与 **`projects/DensePose`** (../../projects/DensePose): 官方对「自定义 backbone + 自定义 ROI heads」这一模式的项目级示例集合, DensePose 与 MeshRCNN 给出完整实现范例。
- 与 **模型注册表清单** (../modules/modeling.html#model-registries): 提供所有可注册 registry 的完整列表, 是「我到底能在哪些点做替换」的索引。

## 【使用方法】

**方式 A — 注册新组件并在 cfg 中启用** (以 backbone 为例):
1. 编写继承 `Backbone` 的类, 用 `@BACKBONE_REGISTRY.register()` 装饰, 实现 `__init__`、`forward`、`output_shape`。
2. 在运行入口 (或被 main 脚本 import 的模块) 中 `import` 该文件, 触发注册副作用。
3. 读取 cfg, 设 `cfg.MODEL.BACKBONE.NAME = 'ToyBackbone'`, 调用 `build_model(cfg)`。
4. 对 ROI heads 同理: 写 `ROIHeads` 子类, 用 `@ROI_HEADS_REGISTRY.register()` 注册, 后续在 cfg 中通过对应字段名引用 (原文未给出具体字段名, 需查 `model-registries` 文档)。

**方式 B — 代码级显式传参** (适用于文本配置表达不了的深度定制):
1. 实例化所需子模块 (如 `MyRCNNOutput(...)`)。
2. 调用 `StandardROIHeads(cfg, backbone.output_shape(), box_predictor=MyRCNNOutput(...))`, 其余参数保持默认 — 这一能力依赖 `configurable.__init__` 让被覆盖的关键字参数优先级高于 cfg 派生参数。
3. (可选) 如仍想从 cfg 启用, 把上一步包成一个 `MyStandardROIHeads` 并 `@ROI_HEADS_REGISTRY.register()`, 在子类 `__init__` 里显式传入 `box_predictor=MyRCNNOutput(...)`。

**关键配置项 / 命令**:
- `cfg.MODEL.BACKBONE.NAME`: 字符串, 决定 backbone 实际使用的注册类名。
- 装饰器 `@BACKBONE_REGISTRY.register()` / `@ROI_HEADS_REGISTRY.register()`: 注册动作, 无参数。
- `ShapeSpec(channels=…, stride=…)`: 声明 backbone 输出特征图的元数据, 原文中示例值 `channels=64, stride=16`。
- `build_model(cfg)`: 由注册名到实际模型对象的最终装配函数 (原文未列出函数签名细节, 属隐含依赖)。

> 原文未涉及安装命令、CLI flag、yaml 配置字段全列表、版本要求等工程化启用细节, 这些需结合 `config.html` 与 `model-registries` 文档获取。
