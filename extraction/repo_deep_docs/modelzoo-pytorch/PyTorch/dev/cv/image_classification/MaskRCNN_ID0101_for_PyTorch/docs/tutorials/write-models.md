# Write Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/tutorials/write-models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/tutorials/write-models.md

# 深度解读:`PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/tutorials/write-models.md`

---

## 【定位】

这篇文档解决"如何在 detectron2 中编写或扩展自定义模型"的问题,核心说明 detectron2 提供的**注册机制 (Registry)**,允许开发者无需改动框架源码即可替换或新增标准模型的内部组件 (如 backbone、ROI heads 等)。

---

## 【技术要点】

1. **两条建模路径**:文档明确指出两条路线——一是"完全从零实现新模型",二是"利用注册机制修改/扩展现有模型某组件",后者更常见且风险更低。
2. **注册机制入口**:通过 `@BACKBONE_REGISTRY.register()` 装饰器将自定义类注册到 detectron2 的全局注册表,框架在调用 `build_model(cfg)` 时会根据配置自动选择对应实现。
3. **自定义 Backbone 的最小骨架**:必须继承 `Backbone` 基类,并实现 `__init__(self, cfg, input_shape)`、`forward(self, image)`、`output_shape(self)` 三个方法,后两者返回值需保持 dict 形式以与下游网络对齐。
4. **示例 backbone 的关键算子参数**:`nn.Conv2d(3, 64, kernel_size=7, stride=16, padding=3)`——输入 3 通道 (RGB)、输出 64 通道、卷积核 7×7、步长 16、padding=3。
5. **配置层覆盖方式**:在配置对象中通过 `cfg.MODEL.BACKBONE.NAME = 'ToyBackBone'` 即可将 backbone 切换为自定义实现,无需修改任何代码。
6. **ROIHeads 扩展点**:为 Generalized R-CNN 元架构添加新能力时,需继承 `ROIHeads` 并注册到 `ROI_HEADS_REGISTRY`;典型参考实现见 detectron2 内部的 DensePose 项目以及 FacebookResearch 的 meshrcnn。

---

## 【关键机制与数据】

**工作原理 (原文梳理):**

- **注册→配置→构建** 三段式流程:
  1. **注册阶段** — 用户用 `@BACKBONE_REGISTRY.register()` (装饰器语法) 把 `ToyBackBone` 类挂入 `BACKBONE_REGISTRY`;同理 `ROI_HEADS_REGISTRY` 接收 `ROIHeads` 子类。
  2. **配置阶段** — 通过 YAML/Python config 将名字字符串 (如 `'ToyBackBone'`) 写入 `cfg.MODEL.BACKBONE.NAME`。这一字符串即注册表里的"键"。
  3. **构建阶段** — 调用 `build_model(cfg)` 时,detectron2 内部根据配置名查注册表,实例化对应的类,从而替换默认实现。

- **数据流 (基于示例 backbone):**
  `image` (RGB 张量,3 通道) → `nn.Conv2d(3, 64, kernel_size=7, stride=16, padding=3)` → 输出特征图 (`{"conv1": feat_map}`);`output_shape()` 同步返回 `{"conv1": ShapeSpec(channels=64, stride=16)}`,供下游 FPN/ROIHeads 据此分配 anchor、计算感受野等。

- **设计约定:**
  - `forward` 与 `output_shape` 必须返回**同名的 dict key** (此处都是 `"conv1"`),形成"特征名—形状描述"的一致性契约。
  - `ShapeSpec(channels=64, stride=16)` 中的 `stride=16` 直接由 Conv2d 的 stride 决定,意味着该 backbone 输出特征相对于输入下采样 16 倍,这是后续 anchor 设计与 FPN 层级匹配的关键。

- **性能数据:** 原文未涉及任何性能/基准数据。

---

## 【表格解读】

**原文无表格。** 文档全文未出现任何表格 (无参数表、无性能对比、无配置项表格),仅以代码示例与说明性段落呈现内容。

---

## 【公式解读】

**原文无公式。** 文档未给出 LaTeX 或伪代码形式的数学公式;若将 `nn.Conv2d(3, 64, kernel_size=7, stride=16, padding=3)` 视为算子调用,其形状推导属于代码而非公式表达,故不列入本节。

---

## 【关联】

利用文末内部链接,梳理出本文与 detectron2 其他模块/项目的关系:

| 关联对象 | 链接 | 与本文的关系 |
|---|---|---|
| `detectron2.modeling.ROIHeads` | `../modules/modeling.html#detectron2.modeling.ROIHeads` | Generalized R-CNN 中 ROI 阶段的可扩展基类;文档第二节"为 ROI heads 增加新能力"直接以此为父类 |
| `projects/DensePose` | `../../projects/DensePose` | 官方项目示例,演示如何通过继承 `ROIHeads` 注册新任务 (人体密集姿态估计),是本文 ROIHeads 扩展示例的具体参照 |
| `projects/` 目录 | `../../projects/` | 汇集多种"基于注册机制实现不同架构"的完整工程案例,本文把它作为扩展范式的总入口 |
| 模型注册表 API | `../modules/modeling.html#model-registries` | 注册机制的完整 API 列表 (如 `BACKBONE_REGISTRY`、`ROI_HEADS_REGISTRY` 等),文档最后一段指向此处,作为进一步查阅的总索引 |

整体来看,本文处于 detectron2 **"模型扩展"** 知识链的入口层:**注册机制 + 基类约定** → 单点示例 (backbone、ROI heads) → 项目级完整实现 (DensePose、meshrcnn) → API 全景 (model-registries)。

---

## 【使用方法】

**启用步骤 (原文提取,逐条对应):**

1. **导入注册装饰器与基类**
   ```python
   from detectron2.modeling import BACKBONE_REGISTRY, Backbone, ShapeSpec
   ```

2. **定义并注册自定义类** (以 backbone 为例)
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

3. **在 config 中指定新组件名**
   ```python
   cfg.MODEL.BACKBONE.NAME = 'ToyBackBone'
   ```

4. **调用框架的统一构建入口**
   ```python
   model = build_model(cfg)   # 框架将自动实例化 ToyBackBone
   ```

5. **ROIHeads 类扩展 (原文给出方向)**:实现 `ROIHeads` 子类 → 用 `ROI_HEADS_REGISTRY` 注册 → 在 cfg 中指向新类名。详细配置字段与命令行参数原文未展开,需参照 [ROIHeads API 文档](../modules/modeling.html#detectron2.modeling.ROIHeads) 与 [DensePose 项目](../../projects/DensePose) 中的实际配置示例。

> **说明**:文档未提供 CLI 命令、yaml 片段或具体的 config key 完整列表;若需精确字段,应跳转文末内部链接 [`model-registries`](../modules/modeling.html#model-registries) 与 [`projects/`](../../projects/) 查看。
