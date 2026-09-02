# Write Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/Cascade_RCNN/docs/tutorials/write-models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/Cascade_RCNN/docs/tutorials/write-models.md

【定位】
本文档介绍 detectron2 提供的**模型注册与扩展机制 (registration mechanism)**: 在不必从零实现整套模型的前提下, 通过注册装饰器和配置项, 让用户可以替换或扩展标准模型的内部组件 (例如 backbone、ROI heads), 从而复用既有建模管线、专注改动想要自定义的部分。

【技术要点】
- **核心机制**: 提供注册机制, 允许"覆盖标准模型内部组件的行为", 而不要求整套重写; 既可新增 backbone, 也可扩展 Generalized R-CNN 的 ROI heads。
- **Backbone 自定义三件套**: 必须继承 `Backbone`, 实现 `__init__(self, cfg, input_shape)`、`forward(self, image)`、`output_shape(self)` 三个接口。
- **示例骨干网络参数 (ToyBackBone)**: 仅一层 `nn.Conv2d(3, 64, kernel_size=7, stride=16, padding=3)`, 输出特征图命名为 `"conv1"`, 通道数 64、下采样步长 16。
- **输出形状声明**: 通过 `ShapeSpec(channels=64, stride=16)` 告知下游模块特征维度与分辨率变化, key 同样使用 `"conv1"` 与 forward 对齐。
- **注册与挂载**: 用装饰器 `@BACKBONE_REGISTRY.register()` 注册到全局表, 再通过配置 `cfg.MODEL.BACKBONE.NAME = 'ToyBackBone'` 激活; `build_model(cfg)` 会调用自定义类而非默认 backbone。
- **ROI heads 扩展**: 在 `ROI_HEADS_REGISTRY` 中注册新的 `ROIHeads` 子类, 即可为 Generalized R-CNN meta-architecture 增加新任务能力。

【关键机制与数据】
- 工作原理: 注册器 (registry) 相当于一个"名称→类"的全局字典; 用户通过装饰器把自定义类写入字典, 再以字符串名称的形式在 cfg 中指定, `build_model(cfg)` 在构造模型时按名查表、实例化对应类, 实现"配置驱动 + 行为可插拔"。
- 数据流 (ToyBackBone 为例, 原文): 输入图像 → `conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=16, padding=3)` → `forward` 返回 `{"conv1": feature_map}` → `output_shape` 返回 `{"conv1": ShapeSpec(channels=64, stride=16)}` → `build_model(cfg)` 据此替换默认 backbone。
- 性能/训练数据: 原文未提供任何基准数值或训练指标, 不做臆测。

【表格解读】
原文无表格。

【公式解读】
原文无公式。

【关联】
- `../modules/modeling.html#detectron2.modeling.ROIHeads` — `ROIHeads` 基类的 API 文档, 是子类化以新增 ROI 能力的入口。
- `../../projects/DensePose` — DensePose 项目, 作为"自定义 ROIHeads 以执行新任务"的实例参考。
- `../../projects/` — 目录索引, 包含实现不同架构的更多项目样例。
- `../modules/modeling.html#model-registries` — 全部注册表 (registries) 的完整清单, 是"还能往哪些槽位里塞自定义组件"的官方索引。
- 上下游关系: BACKBONE_REGISTRY 与 ROI_HEADS_REGISTRY 都属于上述"全部注册表"集合中的成员; `build_model(cfg)` 是连接 cfg 字符串名称与注册类实例化的桥梁, 文档示例隐含了"配置层 → 注册表 → 模型构造"的链式依赖。

【使用方法】
- **注册自定义 backbone**:
  ```python
  from detectron2.modeling import BACKBONE_REGISTRY, Backbone, ShapeSpec

  @BACKBONE_REGISTRY.register()
  class ToyBackBone(Backbone):
      def __init__(self, cfg, input_shape):
          super().__init__()
          self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=16, padding=3)

      def forward(self, image):
          return {"conv1": self.conv1(image)}

      def output_shape(self):
          return {"conv1": ShapeSpec(channels=64, stride=16)}
  ```
- **启用方式**: 在配置对象中设置 `cfg.MODEL.BACKBONE.NAME = 'ToyBackBone'`, 然后调用 `build_model(cfg)` 即可让自定义类生效。
- **扩展 ROI heads (原文)**: 实现一个新的 `ROIHeads` 子类, 注册到 `ROI_HEADS_REGISTRY`, 即可为 Generalized R-CNN 增加新任务能力。
- **完整注册表清单**: 原文指引查阅 `../modules/modeling.html#model-registries` 获取所有可注册槽位; 模板项目列表见 `../../projects/`。
