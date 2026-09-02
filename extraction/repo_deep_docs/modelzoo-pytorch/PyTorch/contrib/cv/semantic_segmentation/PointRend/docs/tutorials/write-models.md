# Write Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/write-models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/write-models.md

# 深度解读：Detectron2 "Write Models" 指南

---

## 【定位】

本指南面向需要在 detectron2 现有模型基础上进行**模块级定制或扩展**的用户，介绍两条核心路径：通过 **Registry 注册机制** 把自定义组件（backbone、box head 等）以字符串名形式接入配置系统，或在代码中通过 **`__init__` 显式参数** 绕开配置直接构造变体模型，从而支持从"轻量替换"到"深度定制"的不同需求层次。

---

## 【技术要点】

1. **Registry 注册机制是配置名 → 代码实现的桥接器**：对"backbone feature extractor""box head"等常见可定制概念，detectron2 提供了注册表（如 `BACKBONE_REGISTRY`、`ROI_HEADS_REGISTRY`），用户用 `@XXX_REGISTRY.register()` 装饰器把子类登记进去，之后只需在配置里写类名字符串，`build_model(cfg)` 即可定位到具体实现。

2. **`Backbone` 基类接口契约**：任何想注册成 backbone 的类必须实现 `__init__(self, cfg, input_shape)`、`forward(self, image)`、`output_shape(self)` 三方法；`forward` 与 `output_shape` 必须返回**字典**，键为特征名（如 `"conv1"`），值为 `ShapeSpec`（含 `channels`、`stride`）。原文 ToyBackbone 示例中 `Conv2d(3, 64, kernel_size=7, stride=16, padding=3)` 与 `ShapeSpec(channels=64, stride=16)` 是一对严格对应的"实际算子通道数/步长 ↔ 输出规格描述"。

3. **配置驱动的实例化路径**：原文给出 `cfg.MODEL.BACKBONE.NAME = 'ToyBackbone'` 这一关键字段——它就是注册时登记的名字字符串，`build_model(cfg)` 会沿着这条名字查注册表、找到类、然后用 `cfg` 实例化。

4. **Generalized R-CNN 的 ROI 头可整体替换**：`ROIHeads` 子类化后放进 `ROI_HEADS_REGISTRY`，原文明确指出 **DensePose** 与 **MeshRCNN** 就是这类"新任务=新 ROIHeads"的两个真实示例，证明该机制足以承载新增任务而非仅微调参数。

5. **配置能力受限时的显式构造路径**：当文本配置无法表达深度定制时，可绕过 Registry，直接调用组件的 `__init__` 并传入自定义对象。原文以"Faster R-CNN 的 box head 换为自定义 loss"为例，步骤是：① 写 `FastRCNNOutputLayers` 的子类 `MyRCNNOutput`；② 在构造 `StandardROIHeads` 时通过 `box_predictor=MyRCNNOutput(...)` 参数注入；③（可选）再把整组 `StandardROIHeads` 包成 `MyStandardROIHeads` 重新登记，以恢复配置化使用。

6. **`@configurable` 机制简化"保持其他参数不变"**：在步骤 ② 中只覆盖 `box_predictor` 一个参数而让其余参数走默认，是因为 `StandardROIHeads` 的 `__init__` 被装饰为 `@configurable`，使得调用者既可全量传参也可只覆盖个别命名参数——这是 detectron2 把"配置参数 → 函数实参"统一起来的具体实现细节，原文点出此机制即"easily achieved by using the configurable `__init__` mechanism"。

---

## 【关键机制与数据】

**Registry 注册路径（数据流）**：
1. 用户实现 `Backbone` 子类 → 用 `@BACKBONE_REGISTRY.register()` 装饰
2. 导入该代码 → 注册表里出现 `ToyBackbone` 这个名字
3. 用户在 cfg 或代码里设 `MODEL.BACKBONE.NAME = 'ToyBackbone'`
4. `build_model(cfg)` 读到名字 → 查注册表 → 用 `cfg` 实例化 `ToyBackbone(cfg, input_shape)`

**原文 ToyBackbone 实测参数**：
- 卷积层：`nn.Conv2d(3, 64, kernel_size=7, stride=16, padding=3)`（输入 3 通道 → 输出 64 通道，7×7 核、步长 16、padding 3）
- 输出特征字典：`{"conv1": ...}`
- `output_shape()` 返回：`{"conv1": ShapeSpec(channels=64, stride=16)}` —— 注意 `stride=16` 与卷积层 `stride=16` 完全一致，这是接口契约要求

**显式构造路径的数据流**（以 Faster R-CNN 自定义 box head 为例）：
1. 用户写 `MyRCNNOutput(FastRCNNOutputLayers)` 子类，承载自定义 loss
2. 构造 `StandardROIHeads(cfg, backbone.output_shape(), box_predictor=MyRCNNOutput(...))` —— 显式把自定义 box_predictor 塞进去，其余参数走 `@configurable` 默认
3. （可选）再写 `MyStandardROIHeads(StandardROIHeads)` 子类并登记到 `ROI_HEADS_REGISTRY`，把这一整套变体"打包"成可由配置名加载的对象

---

## 【表格解读】

**原文无表格**。原文依赖代码块而非表格来说明用法，所有结构化信息（参数、接口契约、注册步骤）均以 Python 代码 + 散文段落呈现，无 markdown/html 表格。

---

## 【公式解读】

**原文无公式**。原文未出现 LaTeX 或伪代码形式的数学公式/算法伪代码。涉及"卷积输出尺寸"等隐含算术也未给出（如 ToyBackbone 中 `Conv2d(3, 64, kernel_size=7, stride=16, padding=3)` 的输出空间尺寸并未在文中以公式形式列出），故严格按原文不补写。

---

## 【关联】

**上游/同级模块与项目**：
- `[Backbone]`(../modules/modeling.html#detectron2.modeling.Backbone) —— 注册机制的基类接口契约定义处
- `[BACKBONE_REGISTRY]`(../modules/modeling.html#detectron2.modeling.BACKBONE_REGISTRY) —— backbone 注册表本身
- `[ROIHeads]`(../modules/modeling.html#detectron2.modeling.ROIHeads) —— Generalized R-CNN 头部基类，承载新任务（如 DensePose、MeshRCNN）
- `[model-registries]`(../modules/modeling.html#model-registries) —— 完整注册表清单，原文指引用户前往查阅"还有哪些组件可以这样登记"
- `[FastRCNNOutputLayers]`(../modules/modeling.html#detectron2.modeling.FastRCNNOutputLayers) —— 显式构造路径中被替换的对象（box head 的具体输出层）
- `[configurable __init__]`(../config.html#detectron2.config.configurable) —— 让 `__init__` 既可全量调用也可按名覆盖的装饰器机制，是显式构造能"只覆盖一个参数"的关键依赖

**真实世界项目示例**：
- `[DensePose]`(../../projects/DensePose) —— 通过自定义 `ROIHeads` 实现密集姿态估计任务的范例
- `[MeshRCNN]`(https://github.com/facebookresearch/meshrcnn) —— 另一个通过自定义 `ROIHeads` 承载 3D 网格预测新任务的范例
- `[projects/]`(../../projects/) —— 汇集更多"不同架构整体实现"的范例目录，是"整个模型都可登记替换"的实际证据

**整体关系链**（原文视角）：
Registry 注册路径 是**首选 / 通用方案**（覆盖"主组件级"定制），显式构造路径 是**Registry 表达力不足时的补充**；两者并非互斥——显式构造写好的变体常常又会再被登记进 Registry（步骤 ③）以恢复配置化使用，从而形成"显式写 → 登记 → 配置用"的闭环。

---

## 【使用方法】

**1. 注册自定义 backbone（Registry 路径）**：
```python
from detectron2.modeling import BACKBONE_REGISTRY, Backbone, ShapeSpec

@BACKBONE_REGISTRY.register()
class ToyBackbone(Backbone):
    def __init__(self, cfg, input_shape):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=16, padding=3)
    def forward(self, image):
        return {"conv1": self.conv1(image)}
    def output_shape(self):
        return {"conv1": ShapeSpec(channels=64, stride=16)}
```
随后通过配置或代码启用：
```python
cfg.MODEL.BACKBONE.NAME = 'ToyBackbone'   # 在 config 文件中设置等价
model = build_model(cfg)
```

**2. 替换 ROI heads 承载新任务**：
实现 `[ROIHeads]` 子类 → `@ROI_HEADS_REGISTRY.register()` → 在 config 中指定对应名字（参考 `[projects/DensePose]` 与 `MeshRCNN` 的写法）。

**3. 用显式参数构造变体（不依赖配置）**：
```python
# Step 1: 自定义 box 输出层
class MyRCNNOutput(FastRCNNOutputLayers):
    # 自定义 loss ...
    pass

# Step 2: 用 @configurable 机制只覆盖 box_predictor 参数
roi_heads = StandardROIHeads(
    cfg, backbone.output_shape(),
    box_predictor=MyRCNNOutput(...)
)

# Step 3（可选）: 把整套变体再登记，恢复配置化使用
@ROI_HEADS_REGISTRY.register()
class MyStandardROIHeads(StandardROIHeads):
    def __init__(self, cfg, input_shape):
        super().__init__(cfg, input_shape,
                         box_predictor=MyRCNNOutput(...))
```

**关键配置项（原文明确出现的）**：
- `cfg.MODEL.BACKBONE.NAME` —— 字符串类名，指向注册表中的 backbone 实现

**关键命令 / 调用**：
- `@BACKBONE_REGISTRY.register()`、`@ROI_HEADS_REGISTRY.register()` —— 注册装饰器
- `build_model(cfg)` —— 触发"读配置名 → 查注册表 → 实例化"的入口
- `StandardROIHeads(cfg, input_shape, box_predictor=...)` —— 显式构造入口（依赖 `@configurable`）
- `ShapeSpec(channels=..., stride=...)` —— 描述 backbone 输出规格的标准数据结构
