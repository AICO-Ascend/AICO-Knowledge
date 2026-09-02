# Use Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/FasterRCNN-Resnet50-FPN_ID1552_for_PyTorch/docs/tutorials/models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/FasterRCNN-Resnet50-FPN_ID1552_for_PyTorch/docs/tutorials/models.md

# 一体化深度解读：detectron2 "Use Models" 指南

---

## 【定位】

这篇文档解决 detectron2 中「模型生命周期管理」与「模型调用接口」的问题——从模型构建、权重加载/保存，到训练与推理模式的调用方式，再到输入/输出的标准数据结构约定，最后介绍如何通过部分执行模型（partial execution）来获取中间张量。它本质上是一份面向开发者与研究者的 detectron2 模型 API 集成手册，配套的代码仓为 FasterRCNN-Resnet50-FPN 的 PyTorch 实现。

---

## 【技术要点】

1. **模型构建入口**：`build_model(cfg)` 仅搭建模型结构并填入随机参数，返回 `torch.nn.Module`；构建子模型使用 `build_backbone`、`build_roi_heads` 等。
2. **检查点加载/保存**：通过 `DetectionCheckpointer(model).load(file_path_or_url)` 加载权重（通常来自 `cfg.MODEL.WEIGHTS`）；通过 `checkpointer.save("model_999")` 保存到 `output/model_999.pth`；同时识别 PyTorch 的 `.pth` 与 model zoo 的 `.pkl` 格式。
3. **训练模式约束**：所有模型必须在 `EventStorage` 上下文管理器中调用 `model(inputs)`，训练统计指标会被自动写入 storage。
4. **推理两种方式**：①使用 `DefaultPredictor` 包装类（自动加载模型 + 预处理 + 单图输入）；②手动调用 `model.eval()` + `torch.no_grad()`，传入 `list[dict]`。
5. **统一数据结构**：训练和推理的输入均为 `list[dict]`，每张图像一个 dict；训练输出为 `dict[str -> ScalarTensor]`（loss 字典），推理输出为 `list[dict]`（每图一个 dict）。
6. **部分执行模型的三种途径**：①重写子模型组件使其返回所需中间输出；②直接调用模型内部子模块（如 `model.backbone`、`model.roi_heads._forward_box`）；③使用 PyTorch `forward hooks` 抓取中间张量。

---

## 【关键机制与数据】

### 1. 模型调用数据流（原文）

**输入端**：`inputs` 为 `list[dict]`，每张图像一个 dict，包含以下键：
- `"image"`：`Tensor`，形状 `(C, H, W)`，通道含义由 `cfg.INPUT.FORMAT` 定义；归一化由模型内部使用 `cfg.MODEL.PIXEL_{MEAN,STD}` 完成。
- `"height"` / `"width"`：**期望的**输出高宽，不一定与 `image` 字段一致——例如 `image` 字段可能已是 resize 后的图，但希望输出保持原始分辨率。
- `"instances"`（训练用）：包含 `"gt_boxes"`（N 个 `Boxes`）、`"gt_classes"`（N 个 long 型标签，范围 `[0, num_categories)`）、`"gt_masks"`（`PolygonMasks` 或 `BitMasks`，N 个）、`"gt_keypoints"`（`Keypoints`，N 个关键点集）。
- `"proposals"`（Fast R-CNN 类模型用）：包含 `"proposal_boxes"`（P 个 `Boxes`）、`"objectness_logits"`（P 个分数）；提供时模型以该分辨率输出，比从 `image` 分辨率输出更省且更准。
- `"sem_seg"`：`Tensor[int]`，形状 `(H, W)`，语义分割 ground truth，类别从 0 开始。

**输出端**：
- **训练模式**：输出 `dict[str -> ScalarTensor]`，所有 loss 项。
- **推理模式**：输出 `list[dict]`，每图一个 dict，可能字段：
  - `"instances"`：`Instances` 对象，含 `pred_boxes`（N 个 `Boxes`）、`scores`（N 个分数）、`pred_classes`（N 个标签，范围 `[0, num_categories)`）、`pred_masks`（`Tensor`，形状 `(N, H, W)`）、`pred_keypoints`（`Tensor`，形状 `(N, num_keypoint, 3)`，最后一维为 `(x, y, score)`，分数 > 0）。
  - `"sem_seg"`：`Tensor`，形状 `(num_categories, H, W)`。
  - `"proposals"`：`Instances`，含 `proposal_boxes`（N 个 `Boxes`）和 `objectness_logits`（N 个分数）。
  - `"panoptic_seg"`：元组 `(Tensor, list[dict])`，前者形状 `(H, W)`，每个元素为像素段 id；后者每个 dict 含 `"id"`、`"isthing"`（thing 还是 stuff）、`"category_id"`（当 `isthing==True` 时为 thing 类 id，否则为 stuff 类 id）。

### 2. 数据加载器衔接（原文）

默认 `DatasetMapper` 输出的 dict 符合上述格式；DataLoader 做 batch 化后得到 `list[dict]`，与内置模型输入格式一致。

### 3. 部分执行示例（原文 mask features）

```
images = ImageList.from_tensors(...)        # 预处理后输入张量
model = build_model(cfg)
features = model.backbone(images.tensor)
proposals, _ = model.proposal_generator(images, features)
instances = model.roi_heads._forward_box(features, proposals)
mask_features = [features[f] for f in model.roi_heads.in_features]
mask_features = model.roi_heads.mask_pooler(mask_features, [x.pred_boxes for x in instances])
```

该流程拆解了 Faster R-CNN 的 forward 链路：backbone → proposal_generator → roi_heads._forward_box → mask_pooler，以获取 mask head 之前的特征。

---

## 【表格解读】

原文无表格。文档中"输入字段"、"输出字段"以嵌套的项目符号列表呈现，并非 markdown 表格结构。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档处于 detectron2 教程体系的中游，与以下模块紧密相关（均通过文末内部链接）：

| 链接锚点 | 关联模块 | 与本文档的关系 |
|---------|---------|--------------|
| `detectron2.checkpoint.DetectionCheckpointer` | `checkpoint.py` | 实现本文档示例中加载/保存检查点的核心类 |
| `detectron2.engine.defaults.DefaultPredictor` | `engine/defaults.py` | 推理便捷包装器，是本文档"Use a Model → Inference"章节中推荐的简单推理入口 |
| `detectron2.structures.Instances` | `structures/instances.py` | 同时作为输入字段（训练用 `gt_*` 容器）和输出字段（`pred_*` 容器）的统一数据结构 |
| `detectron2.structures.Boxes` | `structures/boxes.py` | 输入 `gt_boxes`、`proposal_boxes` 与输出 `pred_boxes` 的 box 容器 |
| `detectron2.structures.PolygonMasks` / `BitMasks` | `structures/masks.py` | 输入 `gt_masks` 的两种 mask 容器实现 |
| `detectron2.structures.Keypoints` | `structures/keypoints.py` | 输入 `gt_keypoints` 的关键点容器 |
| `detectron2.data.DatasetMapper` | `data/dataset_mapper.py` | 产生符合本文档"Model Input Format"的 dict，是数据→模型的桥接器 |

文档本身还提到 `[tutorial](./write-models.md)` 作为延伸——指向"如何写自定义模型"的下游教程，与本文档"Partially execute a model → option 1"形成上下游。

---

## 【使用方法】

原文明确给出的启用方式与命令（按场景归类）：

### 构建模型
```python
from detectron2.modeling import build_model
model = build_model(cfg)  # 返回 torch.nn.Module
```

### 加载已有权重
```python
from detectron2.checkpoint import DetectionCheckpointer
DetectionCheckpointer(model).load(file_path_or_url)  # 通常来自 cfg.MODEL.WEIGHTS
```

### 保存权重
```python
checkpointer = DetectionCheckpointer(model, save_dir="output")
checkpointer.save("model_999")  # 保存到 output/model_999.pth
```

### 训练模式
```python
from detectron2.utils.events import EventStorage
with EventStorage() as storage:
    losses = model(inputs)
```

### 推理模式（直接调用）
```python
model.eval()
with torch.no_grad():
    outputs = model(inputs)
```

### 推理模式（推荐便捷接口）
原文未给出 `DefaultPredictor` 的完整调用示例，仅指明其为带"模型加载 + 预处理 + 单图输入"默认行为的模型包装器，详见其 API 文档。

### 配置文件相关键（原文提到的 cfg 项）
- `cfg.MODEL.WEIGHTS`：权重文件路径
- `cfg.INPUT.FORMAT`：图像通道含义定义
- `cfg.MODEL.PIXEL_MEAN` / `cfg.MODEL.PIXEL_STD`：图像归一化参数
