# Write Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/Faster_Mask_RCNN_for_PyTorch/docs/tutorials/write-models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/Faster_Mask_RCNN_for_PyTorch/docs/tutorials/write-models.md

# 深度解读:Detectron2 "Write Models" 教程文档

---

## 【定位】

这篇文档解决**如何在 detectron2 中通过注册机制 (Registry) 扩展或替换现有模型组件**的问题,告诉开发者:不必每次从零实现完整模型,而可以通过注册新的 Backbone、ROI Heads 等子模块,以最小侵入方式定制标准模型(如 Generalized R-CNN)的内部行为。

---

## 【技术要点】

1. **注册机制 (Registry) 是核心扩展手段**:detectron2 提供多种 Registry(如 `BACKBONE_REGISTRY`、`ROI_HEADS_REGISTRY`),开发者通过装饰器 `@XXX_REGISTRY.register()` 将自定义组件注入框架,实现对标准模型内部模块的覆盖,而无需重写整个模型。
2. **新 Backbone 必须继承抽象基类 `Backbone`**:自定义 Backbone 需实现 `__init__(self, cfg, input_shape)`、`forward(self, image)`、`output_shape(self)` 三个方法,框架会在 `build_model(cfg)` 时根据配置自动调用。
3. **配置驱动模型选择**:通过修改 config 对象(如 `cfg.MODEL.BACKBONE.NAME = 'ToyBackBone'`)即可切换到自定义组件,无需改动调用代码。
4. **示例 `ToyBackBone` 的关键参数**:使用单层 `nn.Conv2d(3, 64, kernel_size=7, stride=16, padding=3)` 作为占位实现,返回特征图 dict `{"conv1": ...}`,并通过 `ShapeSpec(channels=64, stride=16)` 描述输出维度。
5. **扩展 ROI Heads 实现新任务能力**:通过继承 `ROIHeads` 基类并注册到 `ROI_HEADS_REGISTRY`,可在 Generalized R-CNN 元架构中加入新的下游能力(典型实例为 DensePose 的关键点 UV 回归、Mesh R-CNN 的网格预测等)。
6. **Registry 是模块化的基础**:文档明确指出多个 Registry 共同覆盖"模型的不同部分甚至整个模型",完整列表需查阅 API 文档。

---

## 【关键机制与数据】

**整体工作流程 (基于原文):**

```
用户定义自定义类
        ↓
用 @BACKBONE_REGISTRY.register() / @ROI_HEADS_REGISTRY.register() 注册
        ↓
在 config 中指定 NAME = "自定义类名"
        ↓
调用 build_model(cfg) → 框架查表 → 实例化自定义类
        ↓
替代标准组件,接入整体前向计算
```

**关键代码片段与参数 (原文保留):**

- **注册装饰器**:`@BACKBONE_REGISTRY.register()`
- **卷积层参数**:`nn.Conv2d(3, 64, kernel_size=7, stride=16, padding=3)`(输入通道=3, 输出通道=64, kernel=7, stride=16, padding=3)
- **输出 shape 描述**:`ShapeSpec(channels=64, stride=16)`(输出特征图通道数=64, 下采样步幅=16)
- **前向返回**:`return {"conv1": self.conv1(image)}`(特征图以 dict 形式返回,key 为层级名)
- **配置切换命令**:`cfg.MODEL.BACKBONE.NAME = 'ToyBackBone'`
- **模型构建入口**:`build_model(cfg)`

**原文未提供任何性能数据 / 基准测试数字。**

---

## 【表格解读】

**原文无表格**。文档以代码示例 + 散文叙述形式呈现,未包含参数表、性能对比或配置项表格。

---

## 【公式解读】

**原文无公式**(无 LaTeX 数学表达式,也无伪代码形式的算法公式)。文档仅以一段 Python 代码示例展示实现方式,代码本身不含数学公式。

---

## 【关联】

根据文末给出的内部链接,本文档与以下模块/项目存在上下游或并列关系:

| 内部链接 | 指向内容 | 与本文档的关系 |
|---|---|---|
| `../modules/modeling.html#detectron2.modeling.ROIHeads` | `ROIHeads` 抽象类 API 文档 | 本文示例提到要继承该类才能在 `ROI_HEADS_REGISTRY` 中注册,属于**前置依赖类** |
| `../../projects/DensePose` | DensePose 项目 | 作为"实现新 ROIHeads 完成新任务"的**典型实例**,展示了本文档模式的下游应用 |
| `../../projects/` | detectron2 官方 projects 目录 | 提供"实现不同架构"的**更多示例集合**,本文档是这些项目背后的机制讲解 |
| `../modules/modeling.html#model-registries` | 所有 Registry 的 API 列表 | 给出可注册组件的**全集索引**,是本文档提及的"完整列表"出处 |

整体来看,本文档属于 detectron2 **"扩展性机制"的总览教程**:Registry 是抽象层,API 文档给出全量接口,projects/ 目录给出真实用例,DensePose / Mesh R-CNN 则是 ROIHeads 扩展模式的代表工程。

---

## 【使用方法】

以下启用方式与配置项均**逐字摘录自原文**:

**1. 注册自定义 Backbone(完整代码示例):**
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

**2. 在 config 中启用自定义 Backbone:**
```python
cfg.MODEL.BACKBONE.NAME = 'ToyBackBone'
```

**3. 触发框架使用自定义组件:**
调用 `build_model(cfg)`,框架将自动实例化 `ToyBackBone` 替代默认 Backbone。

**4. 扩展 ROI Heads 的路径:**
- 继承 `ROIHeads` 子类(详见 [API 文档](../modules/modeling.html#detectron2.modeling.ROIHeads))
- 将子类放入 `ROI_HEADS_REGISTRY`
- 参考实例:[DensePose](../../projects/DensePose)、[Mesh R-CNN](https://github.com/facebookresearch/meshrcnn)、[projects/](../../projects/)

**5. 查询所有可用 Registry:**
查阅 [model-registries API 文档](../modules/modeling.html#model-registries),可在这些 Registry 中注册组件以定制模型的"不同部分或整个模型"。
