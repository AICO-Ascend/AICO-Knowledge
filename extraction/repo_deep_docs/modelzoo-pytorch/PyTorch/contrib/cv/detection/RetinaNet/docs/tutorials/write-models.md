# Write Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/RetinaNet/docs/tutorials/write-models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/RetinaNet/docs/tutorials/write-models.md

# 一体化深度解读：detectron2 Write Models 教程

> 注：该文档位于 `PyTorch/contrib/cv/detection/RetinaNet/docs/` 下，介绍的是 detectron2 框架中如何编写/注册自定义模型组件，是 modelzoo-pytorch 仓内 detectron2 系列教程之一。

---

## 【定位】

本文档解决"如何在 detectron2 中**新增或扩展模型组件**（而不必从零构建完整模型）"的问题，核心描述的是 detectron2 的**注册机制（registry mechanism）**——通过该机制，用户可以覆盖标准模型内部组件的行为，从而实现新 backbone、新 ROI heads 等定制化需求。

---

## 【技术要点】

1. **注册机制（Registry Mechanism）**  
   detectron2 不要求用户从零实现整个模型，而是提供注册机制，允许用户覆盖标准模型中特定内部组件的行为。

2. **自定义 Backbone 的标准范式**  
   继承 `Backbone` 基类，必须实现 `__init__(self, cfg, input_shape)`、`forward(self, image)`、`output_shape()` 三个方法，并通过 `@BACKBONE_REGISTRY.register()` 装饰器注册。

3. **`ShapeSpec` 声明输出形状**  
   Backbone 必须通过 `ShapeSpec(channels=..., stride=...)` 显式声明每个输出 feature map 的通道数和步长，供下游 head 使用。

4. **通过 Config 切换组件**  
   在 config 对象中设置 `cfg.MODEL.BACKBONE.NAME = 'ToyBackBone'` 后，`build_model(cfg)` 会自动调用该自定义类，而非默认 backbone。

5. **自定义 ROI Heads**  
   继承 `ROIHeads` 类并放入 `ROI_HEADS_REGISTRY`，即可为 Generalized R-CNN 元架构增加新能力（如 DensePose、Mesh R-CNN）。

6. **多 Registry 覆盖粒度**  
   detectron2 提供**一整套 registry**，用户既可注册单个组件（如 backbone、ROI heads），也可注册整个模型。

---

## 【关键机制与数据】

### 工作原理（基于原文 ToyBackBone 示例）

**数据流：**  
`cfg` 配置 → `build_model(cfg)` → 读取 `cfg.MODEL.BACKBONE.NAME` → 到 `BACKBONE_REGISTRY` 中查找同名类 → 实例化 `ToyBackBone(cfg, input_shape)` → 在 forward 中输出 `{"conv1": tensor}` → 其他 head 通过 `output_shape()` 获知 `conv1` 的 `channels=64, stride=16` 进行匹配。

**原文关键代码片段：**  
```python
self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=16, padding=3)
```
即输入 3 通道（RGB 图像），输出 64 通道，卷积核 7×7，步长 16，padding 3——一个非常简化的"玩具 backbone"，仅用于演示流程。

**ROI Heads 扩展路径：**  
新 `ROIHeads` 子类 → 注册到 `ROI_HEADS_REGISTRY` → 被 Generalized R-CNN 元架构自动调用，从而支持 DensePose（密集人体姿态估计）、Mesh R-CNN（3D 网格重建）等新任务。

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

文档通过内部链接建立了以下关联网络：

| 链接目标 | 关联内容 |
|---|---|
| `../modules/modeling.html#detectron2.modeling.ROIHeads` | `ROIHeads` 基类的 API 文档——是扩展 Generalized R-CNN 新能力（如 DensePose）必须继承的父类 |
| `../../projects/DensePose` | DensePose 项目——是**自定义 ROIHeads** 的实际范例，演示如何通过新 ROI heads 完成"密集人体姿态估计"这一新任务 |
| `../../projects/` | 项目目录——包含**多种实现不同架构**的完整范例，是学习"整套模型/组件注册"的入口 |
| `../modules/modeling.html#model-registries` | API 文档中的 **Registry 完整列表**——给出 detectron2 所有可用 registry（如 `BACKBONE_REGISTRY`、`ROI_HEADS_REGISTRY` 等），是用户注册组件的"全景参考" |

**上下游关系图（基于原文）：**  
- **上游：** 标准模型元架构（如 Generalized R-CNN）依赖 registry 在运行时解析组件名 → 实例化具体类。  
- **下游：** 用户代码 → 通过 `@XXX_REGISTRY.register()` 装饰器向 registry 注入自定义组件 → config 引用组件名字符串 → `build_model(cfg)` 在运行时将字符串解析回类。  
- **横向：** Backbone 输出 → 由 `output_shape()` 声明的 `ShapeSpec` 描述 → 被后续 head（如 ROI heads）消费。

---

## 【使用方法】

### 1. 注册自定义 Backbone（原文示例）

```python
from detectron2.modeling import BACKBONE_REGISTRY, Backbone, ShapeSpec

@BACKBONE_REGISTRY.register()
class ToyBackBone(Backbone):
  def __init__(self, cfg, input_shape):
    super().__init__()
    # create your own backbone
    self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=16, padding=3)

  def forward(self, image):
    return {"conv1": self.conv1(image)}

  def output_shape(self):
    return {"conv1": ShapeSpec(channels=64, stride=16)}
```

### 2. 在 Config 中启用自定义组件（原文）

```python
cfg.MODEL.BACKBONE.NAME = 'ToyBackBone'
```
随后调用 `build_model(cfg)`，框架将自动选用 `ToyBackBone`。

### 3. 自定义 ROI Heads（原文说明）

- 实现 `ROIHeads` 的子类；
- 注册到 `ROI_HEADS_REGISTRY`；
- 参考 [DensePose](../../projects/DensePose) 与 [meshrcnn](https://github.com/facebookresearch/meshrcnn) 了解完整范例。

### 4. 查看所有可用 Registry（原文说明）

完整 registry 列表见 [API documentation](../modules/modeling.html#model-registries)，可针对 backbone、ROI heads、proposal generator、meta-architecture 等不同部位分别定制。
