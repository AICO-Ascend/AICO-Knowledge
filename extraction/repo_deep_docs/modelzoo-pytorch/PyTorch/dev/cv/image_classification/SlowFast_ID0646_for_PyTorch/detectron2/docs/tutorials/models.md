# Use Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/models.md

# 一体化深度解读：detectron2 "Use Models" 教程

## 【定位】

本文档是 detectron2 模型使用指南，系统说明如何从 Yacs 配置对象构建模型、加载/保存权重、调用模型进行训练与推理，以及定义标准的输入/输出数据格式与部分执行模型的策略。

## 【技术要点】

1. **模型构建入口**：通过 `detectron2.modeling` 下的 `build_model(cfg)`（以及 `build_backbone`、`build_roi_heads` 等）从配置对象构建 `torch.nn.Module`，仅搭建结构与随机初始化参数。
2. **权重加载/保存**：使用 `DetectionCheckpointer(model)` 类，方法 `.load(file_path_or_url)` 读取 `.pth` 或 `.pkl` 格式权重；`checkpointer = DetectionCheckpointer(model, save_dir="output")` 后调用 `.save("model_999")` 保存为 `output/model_999.pth`。
3. **训练与推理调用约定**：
   - 训练：必须置于 `EventStorage()` 上下文管理器中执行 `losses = model(inputs)`。
   - 推理：可直接 `model.eval()` + `with torch.no_grad(): outputs = model(inputs)`；或使用 `DefaultPredictor` 包装类处理单图推理。
4. **标准输入格式**：所有内建模型接受 `list[dict]`，每张图一个 dict，键包括 `"image"`（Tensor, 格式 (C, H, W)，通道含义由 `cfg.INPUT.FORMAT` 决定，归一化在模型内通过 `cfg.MODEL.PIXEL_{MEAN,STD}` 完成）、`"height"`/`"width"`、`"instances"`、`"sem_seg"`、`"proposals"`。
5. **输出格式**：训练模式输出 `dict[str -> ScalarTensor]` 损失字典；推理模式输出 `list[dict]`，每图一个 dict，含 `"instances"`、`"sem_seg"`、`"proposals"`、`"panoptic_seg"` 等键。
6. **部分执行模型的三种方案**：①按教程重写子模型组件并返回所需输出；②手动调用 `model.backbone / proposal_generator / roi_heads / mask_pooler` 等子模块逐步执行；③使用 PyTorch `forward hooks` 获取中间张量。

## 【关键机制与数据】

### 工作原理与数据流（原文）

**模型与配置分离**：`build_model` 仅搭建结构并填充随机参数；要使用训练好的权重必须借助 `DetectionCheckpointer.load`，权重路径通常取自 `cfg.MODEL.WEIGHTS`。

**训练数据流**：`DatasetMapper` 输出遵循标准格式的 dict，经 DataLoader 批量化后形成 `list[dict]` 送入模型；模型在 `EventStorage` 上下文中记录训练统计到 storage。

**推理数据流**：在 `model.eval()` 与 `torch.no_grad()` 下，单张图对应的 dict（至少含 `"image"`，可选 `"height"`/`"width"`）送入模型；输出按任务不同包含 `Instances`（含 `pred_boxes`、`scores`、`pred_classes` 等）或语义分割张量或全景分割 `(pred, segments_info)` 元组。

**分辨率解耦机制（原文）**：`"height"` 和 `"width"` 字段表示"期望"的输出高/宽，可与 `"image"` 字段的实际尺寸不同；当 `image` 已做 resize 预处理时，模型可按 `height/width` 指定分辨率输出结果，比按输入分辨率更高效精确。

**全景分割的 segments_info 规则（原文）**：若 `segments_info` 存在，每个 dict 含 `"id"`/`"isthing"`/`"category_id"` 三个字段；像素 id 不在 `segments_info` 时为 void label。若 `segments_info` 为 None，则所有像素值需 ≥ -1；`category_id = pixel // metadata.label_divisor`（原文给出此计算式）。

### 性能/具体数值

原文未提供具体性能数据或数字指标（无 mAP、FPS、参数量等）。

## 【表格解读】

**原文无表格**。

## 【公式解读】

**原文无 LaTeX/伪代码公式**。

文档中出现的一行表达式属于语义解释而非数学公式：
```
category_id = pixel // metadata.label_divisor
```
（原文出现于"Model Output Format → panoptic_seg"小节，仅用以说明 `segments_info is None` 情形下如何由像素值得到类别 id，并非算法公式。）

## 【关联】

文档通过内部链接串联到 detectron2 多个核心模块，形成"使用模型"的完整生态：

| 链接指向 | 模块/类 | 在文中的作用 |
|---|---|---|
| `../modules/checkpoint.html#detectron2.checkpoint.DetectionCheckpointer` | `DetectionCheckpointer` | 加载/保存 `.pth` 与 `.pkl` 权重 |
| `../modules/engine.html#detectron2.engine.defaults.DefaultPredictor` | `DefaultPredictor` | 单图推理包装层（含加载、预处理等默认行为） |
| `../modules/structures.html#detectron2.structures.Instances` | `Instances` | 训练 `instances`/`proposals` 字段与推理 `instances`/`proposals` 输出的容器 |
| `../modules/structures.html#detectron2.structures.Boxes` | `Boxes` | `gt_boxes`、`gt_classes`、`proposal_boxes`、`pred_boxes` 的承载结构 |
| `../modules/structures.html#detectron2.structures.PolygonMasks` / `BitMasks` | `PolygonMasks`、`BitMasks` | 训练时 `gt_masks` 字段的两种 mask 表示 |
| `../modules/structures.html#detectron2.structures.Keypoints` | `Keypoints` | 训练时 `gt_keypoints` 字段，存储 N 个关键点集合 |
| `../modules/data.html#detectron2.data.DatasetMapper` | `DatasetMapper` | 默认数据映射器，其输出即遵循上文标准输入格式 |

**上下游关系**：`DatasetMapper` → DataLoader 批量化 → `list[dict]` → `model(inputs)` → 输出（loss dict 或 list[dict]）。`DetectionCheckpointer` 负责外部权重与模型参数之间的双向同步，`DefaultPredictor` 是推理场景下 `model.eval()` + 预处理 + 单图调用的封装替代。

部分执行部分还引用了 `./write-models.md`（编写自定义模型教程）作为子模型重写方案的入口。

## 【使用方法】

### 构建（原文）
```python
from detectron2.modeling import build_model
model = build_model(cfg)  # returns a torch.nn.Module
```

### 加载权重（原文）
```python
from detectron2.checkpoint import DetectionCheckpointer
DetectionCheckpointer(model).load(file_path_or_url)  # 通常传 cfg.MODEL.WEIGHTS
```

### 保存权重（原文）
```python
checkpointer = DetectionCheckpointer(model, save_dir="output")
checkpointer.save("model_999")  # 保存为 output/model_999.pth
```

### 训练（原文）
```python
from detectron2.utils.events import EventStorage
with EventStorage() as storage:
    losses = model(inputs)
```

### 推理——直接方式（原文）
```python
model.eval()
with torch.no_grad():
    outputs = model(inputs)
```

### 推理——封装方式（原文）
使用 `DefaultPredictor` 包装类即可获得默认的模型加载、预处理与单图推理行为，详见其文档。

### 底层文件操作（原文）
`.pth` 文件可用 `torch.{load,save}`；`.pkl` 文件可用 `pickle.{dump,load}` 任意操作。

### 部分执行模型示例（原文）
```python
images = ImageList.from_tensors(...)  # 预处理后的输入
model = build_model(cfg)
model.eval()
features = model.backbone(images.tensor)
proposals, _ = model.proposal_generator(images, features)
instances, _ = model.roi_heads(images, features, proposals)
mask_features = [features[f] for f in model.roi_heads.in_features]
mask_features = model.roi_heads.mask_pooler(mask_features, [x.pred_boxes for x in instances])
```

### 关键配置项（原文）
- `cfg.INPUT.FORMAT`：定义 `"image"` 通道含义。
- `cfg.MODEL.PIXEL_MEAN` / `cfg.MODEL.PIXEL_STD`：模型内归一化参数。
- `cfg.MODEL.WEIGHTS`：权重文件路径或 URL，供 `DetectionCheckpointer.load` 使用。
- `metadata.label_divisor`：当 `panoptic_seg` 的 `segments_info` 为 None 时，通过 `pixel // metadata.label_divisor` 得到 `category_id`。
