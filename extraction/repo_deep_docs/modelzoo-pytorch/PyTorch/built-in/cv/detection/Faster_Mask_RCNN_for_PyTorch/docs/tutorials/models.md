# Use Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/Faster_Mask_RCNN_for_PyTorch/docs/tutorials/models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/Faster_Mask_RCNN_for_PyTorch/docs/tutorials/models.md

# 「Use Models」文档深度解读

## 【定位】
本文档系统讲解 Detectron2 中**模型的构建、权重加载/保存、训练/推理调用、输入输出格式规范，以及如何获取模型中间张量**等核心使用方式，是用户与 Detectron2 内置模型交互的标准指南。

---

## 【技术要点】

1. **模型构建入口**：通过 `detectron2.modeling` 中的 `build_model(cfg)`、`build_backbone`、`build_roi_heads` 等函数构建模型；`build_model(cfg)` 返回的是一个 `torch.nn.Module`，但**仅构建结构并填充随机参数**，需要另行加载权重。

2. **权重加载与保存**：使用 `detectron2.checkpoint.DetectionCheckpointer` 进行 `.pth` 与 `.pkl`（model zoo 格式）的检查点读写；保存路径示例 `save_dir="output"`，保存命名示例 `"model_999"`（最终落盘为 `output/model_999.pth`）。

3. **训练 vs 推理调用差异**：
   - 训练模式必须在 `EventStorage` 上下文内调用，损失会被写入 storage。
   - 推理模式调用方式为 `model.eval()` + `torch.no_grad()` 上下文；亦可使用封装好的 `DefaultPredictor`（单图推理，含加载与预处理默认行为）。
   - 模型调用统一形式：`outputs = model(inputs)`，其中 `inputs` 是 `list[dict]`。

4. **输入格式约定**：内置模型统一接收 `list[dict]`，每个 dict 对应一张图像，键值约定包括 `image`（`(C, H, W)` 张量，通道含义由 `cfg.INPUT.FORMAT` 决定，归一化在模型内由 `cfg.MODEL.PIXEL_{MEAN,STD}` 完成）、`height/width`（**期望输出分辨率**，可与图像实际分辨率不同）、`instances`（训练用 GT）、`proposals`（Fast R-CNN 风格模型使用）、`sem_seg`（`Tensor[int]`，`(H, W)`，语义分割 GT）。

5. **输出格式约定**：训练模式输出 `dict[str -> ScalarTensor]`（各损失项）；推理模式输出 `list[dict]`，每张图像一个 dict，键值按任务分为 `instances`（含 `pred_boxes`、`scores`、`pred_classes`、`pred_masks`（`(N, H, W)`）、`pred_keypoints`（`(N, num_keypoint, 3)`，每行 `(x, y, score)`，scores > 0））、`sem_seg`（`(num_categories, H, W)`）、`proposals`、`panoptic_seg`（`(Tensor, list[dict])`，张量形状 `(H, W)`）。

6. **部分执行（Partial Execution）**：由于中间张量数量极多、无 API 提供，提供了三种获取中间张量的方式——重写子模型、直接拼接子模块调用（如 `model.backbone`、`model.proposal_generator`、`model.roi_heads._forward_box`、`model.roi_heads.mask_pooler`）、或使用 PyTorch 的 forward hooks；并提示需先阅读现有 forward 代码理解内部逻辑。

---

## 【关键机制与数据】

- **数据流链路（原文）**：默认 `DatasetMapper` 的输出是单张图像的 dict（符合上述格式约定），经过 DataLoader 的 batching 后变为 `list[dict]`，这正是内置模型的标准输入格式。即 *数据加载 → DatasetMapper → DataLoader 批处理 → list[dict] → 模型*。

- **图像分辨率处理（原文）**：当输入 dict 中提供 `"height"`/`"width"` 字段时（如 `proposals` 输入路径），模型会以该期望分辨率输出，而**不是**输入 `image` 的分辨率；文档指出这样做 *more efficient and accurate*。例如 `image` 字段是预处理（如 resize）后的图像，但用户仍可要求 outputs 回到原始分辨率。

- **图像归一化（原文）**：归一化在模型内部完成，而非在数据加载阶段；均值与方差由 `cfg.MODEL.PIXEL_{MEAN,STD}` 控制，通道顺序含义由 `cfg.INPUT.FORMAT` 控制。

- **训练统计（原文）**：所有内置模型在训练模式下必须置于 `EventStorage` 上下文内，训练统计会被放入该 storage。

- **检查点文件格式（原文）**：`DetectionCheckpointer` 识别 PyTorch `.pth` 格式与 model zoo 的 `.pkl` 格式；`.pth` 可用 `torch.{load, save}` 操作，`.pkl` 可用 `pickle.{dump, load}` 操作。

- **类别标签范围（原文）**：`gt_classes` 与 `pred_classes` 均为 long 类型 Tensor，值域为 `[0, num_categories)`。

- **关键点张量维度（原文）**：`pred_keypoints` 形状为 `(N, num_keypoint, 3)`，最后一维按 `(x, y, score)` 排列，且 `scores > 0`。

- **性能/benchmark 数据**：原文未涉及具体数值指标。

---

## 【表格解读】

**原文无表格**。原文以嵌套列表/代码块的形式罗列输入输出字段约定（如 `image`、`height`、`width`、`instances`、`proposals`、`sem_seg` 等输入键，以及 `pred_boxes`、`scores`、`pred_classes`、`pred_masks`、`pred_keypoints`、`sem_seg`、`proposals`、`panoptic_seg` 等输出键），但未呈现为 markdown 表格结构，因此未做"逐字还原"。

---

## 【公式解读】

**原文无公式**。文档未出现任何 LaTeX 或伪代码形式的数学公式。

---

## 【关联】

本文档处于 Detectron2 模型使用链路的中心位置，与其上下游模块存在以下引用关系（基于文末内部链接信息）：

1. **检查点与权重管理**：[DetectionCheckpointer](../modules/checkpoint.html#detectron2.checkpoint.DetectionCheckpointer) —— 负责 `.pth`/`.pkl` 加载与保存，本文档加载/保存章节的核心 API。

2. **推理封装器**：[DefaultPredictor](../modules/engine.html#detectron2.engine.defaults.DefaultPredictor) —— 在"Use a Model → Inference"小节被引用，是 `model.eval() + torch.no_grad()` 的高层封装，提供模型加载、预处理、单图推理的默认行为。

3. **数据结构（Instances）**：[Instances](../modules/structures.html#detectron2.structures.Instances) —— 同时出现在**输入**（`"instances"` 表示 GT、`"proposals"` 表示候选框）和**输出**（推理时的 `instances` 包含 `pred_boxes`/`scores`/`pred_classes`/`pred_masks`/`pred_keypoints`，以及 `proposals` 输出）两侧，是贯穿检测/分割/关键点任务的核心容器。

4. **数据结构（Boxes）**：[Boxes](../modules/structures.html#detectron2.structures.Boxes) —— 作为 `Instances` 字段的子类，分别出现在输入侧的 `gt_boxes`、`proposal_boxes` 与输出侧的 `pred_boxes`。

5. **数据结构（Masks）**：[PolygonMasks](../modules/structures.html#detectron2.structures.PolygonMasks) / [BitMasks](../modules/structures.html#detectron2.structures.BitMasks) —— 输入侧 `gt_masks` 的两种可选格式。

6. **数据结构（Keypoints）**：[Keypoints](../modules/structures.html#detectron2.structures.Keypoints) —— 输入侧 `gt_keypoints` 字段使用，与输出侧 `pred_keypoints`（原生 Tensor，形状 `(N, num_keypoint, 3)`）形成对照。

7. **数据映射（数据上游）**：[DatasetMapper](../modules/data.html#detectron2.data.DatasetMapper) —— 在"How it connects to data loader"小节明确：默认 `DatasetMapper` 的输出即遵循本文档定义的 dict 格式，经 DataLoader 批处理后变为模型所需的 `list[dict]`。

8. **教程链接**：[./write-models.md] —— 在"Partially execute a model"中作为"重写子模型"选项的参考教程。

---

## 【使用方法】

以下命令与配置项均**直接来自原文**：

### 1. 构建模型
```python
from detectron2.modeling import build_model
model = build_model(cfg)  # returns a torch.nn.Module
```

### 2. 加载/保存检查点
```python
from detectron2.checkpoint import DetectionCheckpointer

# 加载（常使用 cfg.MODEL.WEIGHTS 路径）
DetectionCheckpointer(model).load(file_path_or_url)

# 保存
checkpointer = DetectionCheckpointer(model, save_dir="output")
checkpointer.save("model_999")  # 落盘为 output/model_999.pth
```

### 3. 训练调用（必须在 EventStorage 内）
```python
from detectron2.utils.events import EventStorage
with EventStorage() as storage:
    losses = model(inputs)
```

### 4. 推理调用（两种方式）
- **方式一：DefaultPredictor**（单图，含模型加载与预处理的默认行为）
- **方式二：直接调用**
  ```
  model.eval()
  with torch.no_grad():
      outputs = model(inputs)
  ```

### 5. 输入配置项（仅在 cfg 中调整、原文提及）
- `cfg.INPUT.FORMAT` —— 控制 `image` 字段通道含义
- `cfg.MODEL.PIXEL_{MEAN,STD}` —— 模型内部归一化使用的均值/方差
- `cfg.MODEL.WEIGHTS` —— 通常传入 `DetectionCheckpointer.load()` 的权重路径

### 6. 部分执行示例（获取 mask features）
```python
images = ImageList.from_tensors(...)  # preprocessed input tensor
model = build_model(cfg)
features = model.backbone(images.tensor)
proposals, _ = model.proposal_generator(images, features)
instances = model.roi_heads._forward_box(features, proposals)
mask_features = [features[f] for f in model.roi_heads.in_features]
mask_features = model.roi_heads.mask_pooler(mask_features, [x.pred_boxes for x in instances])
```

### 7. 数据加载器对接
使用默认 `DatasetMapper`，输出即符合本文档约定的 dict 格式；经 DataLoader 批处理后自动成为 `list[dict]`，可直接喂入内置模型。**原文未涉及**更多自定义或高级配置项。
