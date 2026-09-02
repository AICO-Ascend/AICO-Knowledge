# Write Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/FasterRCNN-Resnet50-FPN_ID1552_for_PyTorch/docs/tutorials/write-models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/FasterRCNN-Resnet50-FPN_ID1552_for_PyTorch/docs/tutorials/write-models.md

# 深度解读：detectron2 "Write Models" 指南

## 【定位】

本文档面向需要在 detectron2 框架内**自定义或扩展模型组件**的开发者，系统说明如何通过 detectron2 的**注册机制 (registration mechanism)** 将新实现的骨干网络、ROI heads 等模块无缝接入现有的 Generalized R-CNN 等元架构中，避免从零重写整套模型。

---

## 【技术要点】

1. **注册机制核心思想**：detectron2 并不要求用户重写整模型，而是提供 `*_REGISTRY` 系列注册表，允许覆盖标准模型内部各组件的行为。
2. **自定义 Backbone 三要素**：
   - 必须继承 `Backbone` 基类（来自 `detectron2.modeling`）；
   - 用 `@BACKBONE_REGISTRY.register()` 装饰器注册类；
   - 实现三个核心方法：`__init__(self, cfg, input_shape)`、`forward(self, image)`、`output_shape()`。
3. **forward 必须返回特征字典**：返回值为 `{"特征名": 张量}` 形式，原文示例 `return {"conv1": self.conv1(image)}`。
4. **output_shape 必须声明各特征层的 ShapeSpec**：原文中 `ShapeSpec(channels=64, stride=16)` 表示 conv1 输出 64 通道、下采样 16 倍。
5. **Backbone 切换方法**：通过配置文件设置 `cfg.MODEL.BACKBONE.NAME = 'ToyBackBone'`，再调用 `build_model(cfg)`，框架会自动用 `ToyBackBone` 替换默认 backbone。
6. **扩展 ROI heads 的方式**：实现 `ROIHeads` 的子类并放入 `ROI_HEADS_REGISTRY`，即可为 Generalized R-CNN 增加新的下游能力（如 DensePose、Mesh R-CNN 等）。

---

## 【关键机制与数据】

- **工作原理（原文）**：detectron2 提供 "*a registration mechanism that lets you override the behavior of certain internal components of standard models*"，即通过装饰器注册 + 字符串命名配置，让 `build_model(cfg)` 在装配模型时按名字查表、用用户自定义类替换默认实现。
- **数据流（原文示例 ToyBackBone）**：
  - 输入图像 → `nn.Conv2d(3, 64, kernel_size=7, stride=16, padding=3)` → 输出特征字典 `{"conv1": tensor}`。
  - 同时向框架报告 `"conv1": ShapeSpec(channels=64, stride=16)`，供后续 FPN/head 根据 stride 与 channel 数对齐。
- **可注册组件范围（原文）**：用户可在不同的 registry 中注册 backbone、ROI heads 等 "different parts of a model, or the entire model"。
- **典型实例（原文）**：DensePose 与 meshrcnn 是通过实现新的 `ROIHeads` 子类来执行新任务的代表性项目。

> 注：原文未提供任何性能数据（mAP、速度等），故不列举。

---

## 【表格解读】

**原文无表格。** 文档以代码片段和说明性文字为主，未给出参数对照表或性能对比表。

---

## 【公式解读】

**原文无公式。** 文档未包含任何 LaTeX 公式或伪代码数学表达式；唯一的"形式化定义"是 `ToyBackBone` 的 Python 类骨架（已在上文"技术要点"中逐字段解读）。

---

## 【关联】

文档串联起 detectron2 模型生态的多处关键节点：

| 文档提到的对象 | 内部链接指向 | 关系说明 |
|---|---|---|
| `ROIHeads` 基类 | `../modules/modeling.html#detectron2.modeling.ROIHeads` | 扩展检测头时必须继承的抽象基类；本文档以 DensePose、Mesh R-CNN 为例说明如何子类化 |
| DensePose 项目 | `../../projects/DensePose` | 示范级实现——用新的 `ROIHeads` 子类将实例级关键点 / 部位解析任务挂接到 Generalized R-CNN |
| 其他 projects | `../../projects/` | 集中存放各类扩展架构的实例，可作为编写新模型的参考库 |
| 模型注册表全集 | `../modules/modeling.html#model-registries` | API 文档入口，列出 `BACKBONE_REGISTRY`、`ROI_HEADS_REGISTRY` 等所有可用注册表，定位"能注册哪些组件、覆盖模型哪一部分" |

整体来看，本文档是 detectron2 **"模型装配 + 插件化扩展"** 模式的入口索引，向下指向具体可注册组件的 API 文档，向外指向 projects 中真实落地的扩展范例。

---

## 【使用方法】

**原文涉及的启用方式与配置项**：

1. **导入所需符号**：
   ```python
   from detectron2.modeling import BACKBONE_REGISTRY, Backbone, ShapeSpec
   ```
2. **用装饰器注册自定义类**：
   ```python
   @BACKBONE_REGISTRY.register()
   class ToyBackBone(Backbone):
       ...
   ```
3. **在配置中按字符串名启用**：
   ```python
   cfg.MODEL.BACKBONE.NAME = 'ToyBackBone'
   ```
4. **调用 `build_model(cfg)`** 即可让框架使用自定义 `ToyBackBone`。
5. **扩展 ROI heads**：编写 `ROIHeads` 子类并注册到 `ROI_HEADS_REGISTRY`（具体配置键名原文未列出，需结合 `../modules/modeling.html#model-registries` 与具体项目源码确认）。

> 文档未提供命令行、YAML 配置或 CLI flag 的具体写法；以上步骤均直接来源于原文代码示例与文字说明。
