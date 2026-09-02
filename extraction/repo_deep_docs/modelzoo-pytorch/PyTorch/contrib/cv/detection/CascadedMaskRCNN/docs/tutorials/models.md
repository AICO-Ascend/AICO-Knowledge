# Use Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/tutorials/models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/tutorials/models.md

# 深度解读:detectron2「Use Models」教程文档

---

## 【定位】

这篇文档是 detectron2 中关于「如何使用内置模型」的入门级指南,系统说明了模型的构建(checkpoint 加载/保存)、调用(训练/推理)方式、标准化输入输出格式,以及如何获取模型内部中间张量的三种策略。

---

## 【技术要点】

1. **模型构建入口**:通过 `detectron2.modeling` 中的 `build_model(cfg)` 构造一个 `torch.nn.Module`,仅建立结构并填充**随机参数**,实际权重需后续 checkpoint 加载。子组件另有 `build_backbone`、`build_roi_heads` 等同名工厂函数。
2. **Checkpoint 机制**:`DetectionCheckpointer` 同时支持 PyTorch 原生 `.pth` 格式以及 detectron2 model zoo 中的 `.pkl` 格式,可通过 `cfg.MODEL.WEIGHTS` 指定的路径或 URL 加载,也可通过 `save_dir` 指定的目录保存(文件名如 `"model_999"` 对应 `output/model_999.pth`)。
3. **两种调用模式**:
   - **训练模式**:`EventStorage()` 上下文管理器中调用,损失会被记录到 storage。
   - **推理模式**:`model.eval()` + `torch.no_grad()`,输入为 `list[dict]`,每个 dict 对应一张图像。
4. **输入格式约定**:内置模型统一接受 `list[dict]`,每个 dict 必含 `"image"` (C, H, W) 张量;可选 `"height"`/`"width"`(期望输出分辨率,与 image 实际尺寸可不同)、`"instances"`(训练用,含 gt_boxes/gt_classes/gt_masks/gt_keypoints)、`"proposals"`(Fast R-CNN 风格,含 proposal_boxes/objectness_logits)、`"sem_seg"`(语义分割 GT,(H, W),`Tensor[int]`)。
5. **输出格式约定**:
   - 训练:`dict[str -> ScalarTensor]`,键为各损失名。
   - 推理:`list[dict]`,可能含 `"instances"`(pred_boxes/scores/pred_classes/pred_masks/pred_keypoints)、`"sem_seg"`(`Tensor`,shape `(num_categories, H, W)`)、`"proposals"`、`"panoptic_seg"`(元组 `(Tensor, list[dict])`,tensor shape `(H, W)`,含 `id`/`isthing`/`category_id`)。
6. **部分执行(Partial Execution)**:通过手动调用 `model.backbone`、`model.proposal_generator`、`model.roi_heads._forward_box`、`model.roi_heads.mask_pooler` 等子模块,可绕过 `forward()` 获取中间张量(如 mask features);文档示例展示的中间张量获取路径为:`ImageList → backbone → proposal_generator → roi_heads._forward_box → mask_pooler`。

---

## 【关键机制与数据】

### 工作原理

- **模型装配流程**:`build_model(cfg)` → 返回随机初始化 `torch.nn.Module` → 通过 `DetectionCheckpointer` 加载 `file_path_or_url`(通常来自 `cfg.MODEL.WEIGHTS`)得到可用模型。
- **图像归一化在模型内部完成**:文档明确指出 "Image normalization, if any, will be performed **inside the model** using `cfg.MODEL.PIXEL_{MEAN,STD}`",因此数据加载器只负责 resize 等预处理,不做像素归一化。
- **通道含义由配置决定**:`cfg.INPUT.FORMAT` 定义 `"image"` 字段的通道含义(原文未展开具体取值)。
- **分辨率解耦**:`"height"`/`"width"` 是**期望输出分辨率**,即使 `"image"` 已被 resize,输出仍可恢复到原始分辨率;若提供 `"proposals"`,模型在此 proposal 分辨率下输出,比直接按 image 分辨率输出更高效、更准确(原文)。
- **训练/推理数据流**:
  - 数据加载侧:`DatasetMapper` 输出符合上述格式的单样本 dict → DataLoader 批处理后变成 `list[dict]` → 模型直接消费。
  - 训练侧:被 `EventStorage` 包裹,损失写入 storage。
  - 推理侧:`DefaultPredictor` 是单图推理的封装,包含模型加载、预处理等默认行为。

### 关键数据/参数(原文)

- `"image"` 张量格式:`(C, H, W)` Tensor
- `"sem_seg"` 输入格式:`Tensor[int]`,`(H, W)`,值表示从 0 开始的类别标签
- `gt_classes`:长整型 Tensor,范围 `[0, num_categories)`
- `pred_classes`:长整型 Tensor,范围 `[0, num_categories)`
- `pred_masks`:`Tensor`,shape `(N, H, W)`
- `pred_keypoints`:`Tensor`,shape `(N, num_keypoint, 3)`,最后一维每行 `(x, y, score)`,scores > 0
- `sem_seg` 输出:`Tensor`,shape `(num_categories, H, W)`
- `panoptic_seg` 输出:元组 `(Tensor, list[dict])`,tensor shape `(H, W)`,元素为像素的 segment id

### 性能说明(原文)

- 原文未提供任何 benchmark、AP 数值或速度指标。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

按文中内部链接梳理的上下游/对等模块关系:

| 出处模块 | 关联类型 | 链接/API |
|---|---|---|
| Checkpoint | 加载/保存 | `../modules/checkpoint.html#detectron2.checkpoint.DetectionCheckpointer` |
| 推理封装 | 上层封装 | `../modules/engine.html#detectron2.engine.defaults.DefaultPredictor` |
| 输入/输出结构体 | 训练 GT | `../modules/structures.html#detectron2.structures.Instances` |
| 输入/输出结构体 | 边界框 | `../modules/structures.html#detectron2.structures.Boxes` |
| 输入结构体 | 多边形 mask | `../modules/structures.html#detectron2.structures.PolygonMasks` |
| 输入结构体 | 位图 mask | `../modules/structures.html#detectron2.structures.BitMasks` |
| 输入结构体 | 关键点 | `../modules/structures.html#detectron2.structures.Keypoints` |
| 数据加载器 | 上游数据生产者 | `../modules/data.html#detectron2.data.DatasetMapper` |
| 模型自定义 | 同级教程 | `./write-models.md`(用于「重写子模块」场景) |
| PyTorch 钩子 | 外部 API | `https://pytorch.org/tutorials/beginner/former_torchies/nnft_tutorial.html#forward-and-backward-function-hooks` |

**关系解读**:
- `DatasetMapper` 是数据上游,产出符合本文档所述格式的单样本 dict,DataLoader 批处理后即直接喂入模型。
- `Instances`、`Boxes`、`PolygonMasks`、`BitMasks`、`Keypoints` 是模型输入输出双方都使用的结构化容器,在训练时承载 GT,在推理时承载预测。
- `DefaultPredictor` 是本文档推荐的"开箱即用"推理封装,内置了本文档「Load/Save a Checkpoint」一节中的 checkpoint 加载逻辑与「Model Input Format」一节中的预处理逻辑。
- `DetectionCheckpointer` 既能消费 `.pth` 也能消费 `.pkl`(model zoo 格式)。
- 当用户需要中间张量时,`./write-models.md` 提供「重写子组件」的路径,PyTorch forward/backward hooks 提供「不动模型结构」的非侵入式路径,与本文档的「部分执行」路径形成三条互补方案。

---

## 【使用方法】

### 构建模型
```python
from detectron2.modeling import build_model
model = build_model(cfg)  # 返回 torch.nn.Module,随机初始化
```

### 加载/保存 Checkpoint
```python
from detectron2.checkpoint import DetectionCheckpointer
DetectionCheckpointer(model).load(file_path_or_url)  # 通常 cfg.MODEL.WEIGHTS

checkpointer = DetectionCheckpointer(model, save_dir="output")
checkpointer.save("model_999")  # 保存到 output/model_999.pth
```

### 训练调用
```python
from detectron2.utils.events import EventStorage
with EventStorage() as storage:
    losses = model(inputs)  # inputs: list[dict]
```

### 推理调用(直接)
```python
model.eval()
with torch.no_grad():
    outputs = model(inputs)
```

### 推理调用(封装)
使用 `DefaultPredictor`,无需自行处理 checkpoint 加载、预处理,仅处理单图(非 batch)。

### 底层文件操作
- `.pth` 文件:使用 `torch.load` / `torch.save`
- `.pkl` 文件:使用 `pickle.load` / `pickle.dump`

### 部分执行示例(获取 mask features)
```python
images = ImageList.from_tensors(...)        # 预处理后的输入张量
model = build_model(cfg)
features = model.backbone(images.tensor)
proposals, _ = model.proposal_generator(images, features)
instances = model.roi_heads._forward_box(features, proposals)
mask_features = [features[f] for f in model.roi_heads.in_features]
mask_features = model.roi_heads.mask_pooler(mask_features, [x.pred_boxes for x in instances])
```

### 自定义输入
原文明确指出 "Users can implement custom models that support any arbitrary input format",即自定义模型可自行约定输入格式;本文档仅描述**内置**模型遵循的约定。
