# Write Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/FasterRCNN_ID0100_for_PyTorch/docs/tutorials/write-models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/FasterRCNN_ID0100_for_PyTorch/docs/tutorials/write-models.md

【定位】
本文档面向需要在 detectron2 中"修改/扩展既有模型组件"而非完全从零构建模型的开发者，系统性介绍 detectron2 提供的**注册机制 (registration mechanism)** 如何允许用户在不改动标准模型主结构的前提下，替换或新增 backbone、ROI heads 等内部子组件，从而实现对模型各部分的定制化扩展。

【技术要点】
1. **双场景定位**：detectron2 既支持"完全从零实现新模型"，也支持"通过注册机制覆写既有模型的内部组件"，文档重点放在后者。
2. **Backbone 注册示例**：通过 `@BACKBONE_REGISTRY.register()` 装饰器将自定义 `ToyBackBone(Backbone)` 子类注册到 `BACKBONE_REGISTRY`，注册后可通过 `cfg.MODEL.BACKBONE.NAME = 'ToyBackBone'` 切换默认 backbone。
3. **Backbone 必实现接口**：自定义 Backbone 需实现 `__init__(self, cfg, input_shape)`、`forward(self, image)` 与 `output_shape()` 三个方法，并通过 `ShapeSpec(channels=64, stride=16)` 描述输出特征图的通道数与下采样步长。
4. **具体卷积参数示例**：示例 backbone 中第一层定义为 `nn.Conv2d(3, 64, kernel_size=7, stride=16, padding=3)`，即输入 3 通道、输出 64 通道、卷积核 7×7、步长 16、padding 3；forward 返回字典 `{"conv1": self.conv1(image)}`，output_shape 返回字典 `{"conv1": ShapeSpec(channels=64, stride=16)}`，二者键名严格对应。
5. **模型装配入口**：`build_model(cfg)` 是注册机制生效的关键入口，会读取 cfg 配置并依据注册表调用相应实现（如 `ToyBackBone`）。
6. **ROI Heads 扩展模式**：若需给 Generalized R-CNN 元架构 (meta-architecture) 增加新能力，需实现一个 `ROIHeads` 子类并放入 `ROI_HEADS_REGISTRY`，从而在 R-CNN 流程中插入新的 head 行为。

【关键机制与数据】
- **工作原理（原文）**：detectron2 通过多个**注册表 (registries)** 抽象模型内部组件。开发者将自定义实现（如 `ToyBackBone` 或自定义 `ROIHeads` 子类）注册到对应注册表后，框架内部构建模型（如 `build_model(cfg)`）便会以注册类替换默认实现，形成"配置驱动 + 注册发现"的扩展范式。
- **数据流（原文）**：以 backbone 为例——`cfg` 中 `MODEL.BACKBONE.NAME` 决定 backbone 具体类 → `build_model(cfg)` 实例化该 backbone → 输入 `image` 经 `forward` 得到特征字典（如 `{"conv1": ...}`）→ `output_shape()` 把每个特征层的 `ShapeSpec`（channels、stride 等）汇报给下游 head，用于决定后续层的输入维度与空间分辨率。
- **性能数据**：原文无任何性能/benchmark/数字指标，示例中出现的数字（3、64、7、16、3）均为卷积层参数而非性能数据。
- **覆盖范围（原文）**：注册机制可应用于"different parts of a model, or the entire model"，即既能替换某个子模块（backbone、heads），也能替换整个模型本身。

【表格解读】
原文无表格。

【公式解读】
原文无公式。

【关联】
- **与 ROIHeads 模块的关联**：文档将自定义 `ROIHeads` 子类注册到 `ROI_HEADS_REGISTRY` 的做法，直接对应链接 [detectron2.modeling.ROIHeads](../modules/modeling.html#detectron2.modeling.ROIHeads) 所描述的 Generalized R-CNN head 基类，二者是"基类定义 ↔ 注册扩展"的关系。
- **与注册表体系的关联**：所有可注册组件的完整清单见 [model-registries](../modules/modeling.html#model-registries)，本文给出的 backbone 与 ROI heads 示例都隶属于该注册表体系，BACKBONE_REGISTRY 与 ROI_HEADS_REGISTRY 只是其中两项。
- **与项目示例的关联**：文档引用 [projects/DensePose](../../projects/DensePose) 作为"自定义 ROIHeads 实现新任务"的范本（dense pose 任务），引用外部 [meshrcnn](https://github.com/facebookresearch/meshrcnn) 作为另一典型示例，二者均为利用注册机制改造 heads 的实际工程案例。
- **与 projects 目录的关联**：[projects/](../../projects/) 被定位为"包含实现不同架构的更多示例"的集合入口，文档引导读者到此获取完整扩展案例库，构成"文档讲解 → 项目示例"的下游引用链。
- **与上游 `build_model(cfg)` 的关联**：`build_model(cfg)` 是注册机制落地的统一装配点，文档中 backbone 与 ROI heads 的切换都依赖它，cfg 配置项（如 `cfg.MODEL.BACKBONE.NAME`）是驱动该装配流程的配置输入。

【使用方法】
- **启用新 backbone 的配置写法**（原文有）：
  - 在自定义 backbone 类前加上装饰器：`@BACKBONE_REGISTRY.register()`
  - 在 config 对象中设置：`cfg.MODEL.BACKBONE.NAME = 'ToyBackBone'`
  - 之后调用 `build_model(cfg)` 时框架会自动使用 `ToyBackBone` 替代默认 backbone
- **启用新 ROI heads 的方式**（原文有）：
  - 实现 `ROIHeads` 的子类（详见链接 [detectron2.modeling.ROIHeads](../modules/modeling.html#detectron2.modeling.ROIHeads)）
  - 将其放入 `ROI_HEADS_REGISTRY` 中
  - 参考 [projects/DensePose](../../projects/DensePose) 与 [meshrcnn](https://github.com/facebookresearch/meshrcnn) 的具体写法
- **其他配置项/命令行开关**（如环境变量、CLI flag、特定 yaml key 列表等）：原文未涉及，仅给出 `cfg.MODEL.BACKBONE.NAME` 一项 cfg 写法作为代表。
