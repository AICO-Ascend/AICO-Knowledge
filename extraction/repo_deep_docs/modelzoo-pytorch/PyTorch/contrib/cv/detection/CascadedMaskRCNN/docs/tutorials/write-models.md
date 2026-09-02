# Write Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/tutorials/write-models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/tutorials/write-models.md

# CascadedMaskRCNN 「Write Models」文档深度解读

---

## 【定位】

这篇文档面向 detectron2 用户,说明如何通过**注册机制 (registration mechanism)** 来**定制/扩展现有模型组件**(如 backbone、ROI heads),或在必要时**从零实现一个全新模型**,从而在不修改 detectron2 内部代码的前提下复用其标准模型框架并替换其中可插拔的部分。

---

## 【技术要点】

- **核心机制:注册表 (Registry)**
  detectron2 提供一套注册机制,允许用户**覆盖 (override) 标准模型内部组件**的行为,从而以可插拔方式修改模型。

- **添加新 Backbone 的代码骨架**
  - 导入 `BACKBONE_REGISTRY`、`Backbone`、`ShapeSpec`
  - 通过装饰器 `@BACKBONE_REGISTRY.register()` 注册自定义类
  - 自定义类继承自 `Backbone`,需实现 `__init__`、`forward`、`output_shape` 三个方法

- **ToyBackBone 示例中的关键参数**(原文代码字面值)
  - `nn.Conv2d(3, 64, kernel_size=7, stride=16, padding=3)` —— 输入通道 3、输出通道 64、卷积核 7、步长 16、padding 3
  - `forward` 返回字典 `{"conv1": self.conv1(image)}`
  - `output_shape` 返回字典 `{"conv1": ShapeSpec(channels=64, stride=16)}`

- **启用自定义 Backbone 的配置方式**
  在 config 对象中设置 `cfg.MODEL.BACKBONE.NAME = 'ToyBackBone'`,随后 `build_model(cfg)` 便会调用 `ToyBackBone` 而非默认 backbone。

- **添加自定义 ROI Heads**
  通过实现一个 `ROIHeads` 的子类,并将其放入 `ROI_HEADS_REGISTRY`,即可在 Generalized R-CNN meta-architecture 之上添加新能力 (例如新任务)。

- **完整注册表清单**
  文档明确指向 `model-registries` 的 API 文档,说明**模型的不同部分或整个模型**都可以通过注册表来定制。

---

## 【关键机制与数据】

原文未给出任何性能数据 (如 mAP、FLOPs、推理耗时等)。

原文呈现的机制工作流如下 (基于示例代码推导):

1. **定义阶段**:用户编写继承自 `Backbone` (或 `ROIHeads`) 的子类。
2. **注册阶段**:通过 `@BACKBONE_REGISTRY.register()` 装饰器(原文代码字面值)将类登记到对应注册表。
3. **配置阶段**:在 config 中指定名字,例如 `cfg.MODEL.BACKBONE.NAME = 'ToyBackBone'`。
4. **构建阶段**:`build_model(cfg)` 在运行时根据 cfg 名称查表,调用用户自定义的 `ToyBackBone` 代替默认实现。
5. **返回约定**:`forward` 必须返回特征字典,`output_shape` 必须返回与 `forward` 键对应的 `ShapeSpec` 字典(原文示例中两字典键名一致,均为 `"conv1"`,且 channels=64、stride=16 互相匹配)。

原文示例中 backbone 将输入图像做一次 stride=16 的 7×7 卷积,直接输出单层特征 `"conv1"`,这是为演示而简化的最小 backbone。

---

## 【表格解读】

**原文无表格。**

(原文仅以代码块与散文形式说明,未出现任何参数表、性能对比表或配置项表格。)

---

## 【公式解读】

**原文无公式。**

(原文未包含任何 LaTeX 公式、伪代码公式或数学表达式。)

---

## 【关联】

利用文末提供的内部链接信息,本文与以下 detectron2 模块/项目存在明确关联:

| 链接指向 | 关系性质 |
|---|---|
| `../modules/modeling.html#detectron2.modeling.ROIHeads` | 提供 `ROIHeads` 基类的 API 参考,本文以此作为"实现新 ROI 子类"的基础 |
| `../../projects/DensePose` | **示例项目**:展示如何实现新的 `ROIHeads` 子类以承载 DensePose 新任务 |
| `https://github.com/facebookresearch/meshrcnn` | **外部示例项目**:展示通过新 `ROIHeads` 实现 meshrcnn 新任务 |
| `../../projects/` | **示例索引目录**:汇集多种不同架构的实现示例 |
| `../modules/modeling.html#model-registries` | **完整注册表 API 文档**:列出所有可用注册表(如 `BACKBONE_REGISTRY`、`ROI_HEADS_REGISTRY` 等),用于定位可注册点 |

总体来看,本文定位为 detectron2 模型定制化体系的"导览页":它本身只给出最小骨架 (ToyBackBone) 与一个扩展点 (ROIHeads),而把更完整的 API 与更丰富的实例 (DensePose、meshrcnn、projects/ 目录) 通过链接外延。

---

## 【使用方法】

根据原文,启用自定义模型组件的具体步骤如下:

1. **导入注册表与基类**(以 Backbone 为例):
   ```python
   from detectron2.modeling import BACKBONE_REGISTRY, Backbone, ShapeSpec
   ```

2. **继承基类并用装饰器注册**:
   ```python
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

3. **在 config 中通过名字切换**:
   ```python
   cfg.MODEL.BACKBONE.NAME = 'ToyBackBone'
   ```

4. **调用 `build_model(cfg)`**:此时 detectron2 会查 `BACKBONE_REGISTRY`,依据 `'ToyBackBone'` 字符串调用用户类,替换默认 backbone。

5. **类比做法 (ROI Heads)**:编写 `ROIHeads` 子类并注册到 `ROI_HEADS_REGISTRY`,即可在 Generalized R-CNN meta-architecture 中添加新能力。

原文**未涉及**命令行启用方式、环境变量、YAML 配置文件层级结构、CLI 启动脚本等具体配置项;亦未涉及完整注册表清单 (需要跳转至 `../modules/modeling.html#model-registries` 查看)。
