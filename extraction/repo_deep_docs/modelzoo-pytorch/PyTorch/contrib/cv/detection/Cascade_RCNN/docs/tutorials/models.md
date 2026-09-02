# Use Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/Cascade_RCNN/docs/tutorials/models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/Cascade_RCNN/docs/tutorials/models.md

# 「Use Models」文档一体化深度解读

## 【定位】

这篇文档系统说明 detectron2 中模型对象的完整使用方式——从模型构建、权重加载/保存、前向调用（训练与推理两种模式）到输入输出字典约定，再到"部分执行"模型以获取中间张量的方法，是连接 `cfg` 配置、数据加载器与下游任务（检测/分割/关键点/全景）的核心使用手册。

---

## 【技术要点】

1. **模型构建入口**：`detectron2.modeling.build_model(cfg)` 返回 `torch.nn.Module`，**只构建结构并填充随机参数**，不加载任何预训练权重；另有 `build_backbone`、`build_roi_heads` 等子构建函数。

2. **权重加载与保存**：使用 `DetectionCheckpointer(model)` 包装模型；`.load(file_path_or_url)` 从 `cfg.MODEL.WEIGHTS` 或 URL 加载；`.save("model_999")` 保存到 `save_dir="output"`，生成 `output/model_999.pth`。同时识别 PyTorch 的 `.pth` 与 detectron2 model zoo 的 `.pkl` 文件，也可用 `torch.{load,save}` 或 `pickle.{dump,load}` 直接操作。

3. **调用约定**：统一通过 `outputs = model(inputs)` 调用，`inputs` 是 `list[dict]`（每张图像一个 dict）；训练时必须置于 `EventStorage()` 上下文内以便记录统计量；推理时推荐 `DefaultPredictor` 包装器，或手动 `model.eval() + torch.no_grad()`。

4. **输入字典的标准键**：`image`（C,H,W 格式 Tensor，归一化在模型内按 `cfg.MODEL.PIXEL_{MEAN,STD}` 完成）、`height`/`width`（**期望输出分辨率**，可能与 `image` 字段不一致）、`instances`（含 `gt_boxes`/`gt_classes`/`gt_masks`/`gt_keypoints`）、`proposals`（仅 Fast R-CNN 风格，含 `proposal_boxes`/`objectness_logits`）、`sem_seg`（H,W 整数 Tensor）。

5. **输出格式分模式**：训练模式输出 `dict[str -> ScalarTensor]`（各项 loss）；推理模式输出 `list[dict]`，每张图一个 dict，可包含 `instances`（`pred_boxes`/`scores`/`pred_classes`/`pred_masks`/`pred_keypoints`）、`sem_seg`（num_categories, H, W）、`proposals`、`panoptic_seg`（`(Tensor(H,W), list[dict])` 元组）。

6. **部分执行模型三种方式**：①按 `write-models.md` 重写子模块；②绕过 `forward()` 直接访问 `model.backbone`/`model.proposal_generator`/`model.roi_heads._forward_box`/`model.roi_heads.mask_pooler` 等子模块（示例中获取的是 mask head 之前的 mask features）；③使用 PyTorch forward hooks。

---

## 【关键机制与数据】

**模型构建机制**：原文：`build_model` only builds the model structure and fills it with random parameters.——意味着任何 `build_model(cfg)` 之后必须显式 load 权重才有可用模型。

**训练/推理分支机制**：原文：When in training mode, all models are required to be used under an `EventStorage`. The training statistics will be put into the storage.——`EventStorage` 是训练指标的写入容器，缺失会导致 loss 记录异常。

**输入 `image` 归一化机制**：原文：Image normalization, if any, will be performed inside the model using `cfg.MODEL.PIXEL_{MEAN,STD}`.——说明数据加载阶段不做归一化，模型内部按配置动态完成。

**`height`/`width` 的语义**：原文：the **desired** output height and width, which is not necessarily the same as the height or width of the `image` field.——这是"输出坐标系"开关：可用于在原图分辨率上输出预测结果，即便 `image` 已被预处理缩放过。

**数据流对接**：原文：The output of the default `DatasetMapper` is a dict that follows the above format. After the data loader performs batching, it becomes `list[dict]` which the builtin models support.——即 `DatasetMapper → collate → list[dict] → model(inputs)`，模型输入格式与默认 mapper 输出格式对齐。

**推理输出维度约定**（原文）：
- `pred_keypoints`: shape `(N, num_keypoint, 3)`，末维为 `(x, y, score)`，**score > 0**。
- `pred_masks`: shape `(N, H, W)`。
- `sem_seg`: shape `(num_categories, H, W)`。
- `panoptic_seg`: 元组 `(Tensor(H,W), list[dict])`；后者每条包含 `id`、`isthing`（thing 或 stuff）、`category_id`（`isthing==True` 时为 thing 类 id，否则为 stuff 类 id）。

**类别取值范围**（原文）：`gt_classes` 与 `pred_classes` 均为 long 类型 Tensor，取值在 `[0, num_categories)`。

---

## 【表格解读】

**原文无表格**。文档中的字段语义以项目符号列表形式给出，未使用 markdown 表格结构。

---

## 【公式解读】

**原文无公式**。文档以代码片段与字段列表为主，未出现 LaTeX 或伪代码形式的公式。

---

## 【关联】

- **`DetectionCheckpointer`**（`../modules/checkpoint.html#detectron2.checkpoint.DetectionCheckpointer`）：权重加载与保存的封装，是 `build_model` 之后让模型"可用"的桥梁。
- **`DefaultPredictor`**（`../modules/engine.html#detectron2.engine.defaults.DefaultPredictor`）：推理的便捷包装器，覆盖模型加载、预处理、单图（非 batch）调用；若需要 batch 推理或多图自定义流程则需绕过它直接 `model.eval() + torch.no_grad()`。
- **`Instances`**（`../modules/structures.html#detectron2.structures.Instances`）：训练时的 `gt_*` 字段容器与推理时的 `pred_*` 字段容器，是 `model(inputs)` / `model(...)` 返回值中"实例类输出"的核心数据结构。
- **`Boxes` / `PolygonMasks` / `BitMasks` / `Keypoints`**（`../modules/structures.html#detectron2.structures.Boxes` 等）：`Instances` 的子字段类型，分别承载边界框、多边形/RLE 掩码、关键点；掩码支持两种表示（多边形 vs 位图）。
- **`DatasetMapper`**（`../modules/data.html#detectron2.data.DatasetMapper`）：上游数据准备模块，其输出 dict 经 batch 后变为 `list[dict]` 即直接喂入模型——这是"模型输入格式"与"数据加载器"的标准契约。
- **`write-models.md` 教程**：当用户希望自定义模型组件或在 `forward()` 之外获取中间张量时引用的对应指南，与本文的"Partially execute a model"一节形成"重写 vs. 复用 vs. hook"三条路径的互补关系。
- **PyTorch forward hooks**（外部链接 `pytorch.org/tutorials/beginner/former_torchies/nnft_tutorial.html`）：与"部分执行"配合使用的通用机制，用于获取指定模块的输入/输出。

---

## 【使用方法】

**构建模型**（原文）：
```python
from detectron2.modeling import build_model
model = build_model(cfg)  # returns a torch.nn.Module
```

**加载检查点**（原文）：
```python
from detectron2.checkpoint import DetectionCheckpointer
DetectionCheckpointer(model).load(file_path_or_url)  # load a file, usually from cfg.MODEL.WEIGHTS
```

**保存检查点**（原文）：
```python
checkpointer = DetectionCheckpointer(model, save_dir="output")
checkpointer.save("model_999")  # save to output/model_999.pth
```

**训练调用**（原文，需置于训练循环内且配套 optimizer）：
```python
from detectron2.utils.events import EventStorage
with EventStorage() as storage:
  losses = model(inputs)
```

**推理调用**（原文，两种方式）：
```python
# 方式一：使用 DefaultPredictor 包装器（单图、含默认预处理）
# 详见 ../modules/engine.html#detectron2.engine.defaults.DefaultPredictor

# 方式二：直接推理
model.eval()
with torch.no_grad():
  outputs = model(inputs)
```

**部分执行模型获取 mask features**（原文示例）：
```python
images = ImageList.from_tensors(...)  # preprocessed input tensor
model = build_model(cfg)
features = model.backbone(images.tensor)
proposals, _ = model.proposal_generator(images, features)
instances = model.roi_heads._forward_box(features, proposals)
mask_features = [features[f] for f in model.roi_heads.in_features]
mask_features = model.roi_heads.mask_pooler(mask_features, [x.pred_boxes for x in instances])
```

**配置项关联**（原文涉及，未给出具体数值）：
- `cfg.MODEL.WEIGHTS`——检查点路径
- `cfg.INPUT.FORMAT`——`image` 字段的通道语义
- `cfg.MODEL.PIXEL_{MEAN,STD}`——模型内部图像归一化参数
