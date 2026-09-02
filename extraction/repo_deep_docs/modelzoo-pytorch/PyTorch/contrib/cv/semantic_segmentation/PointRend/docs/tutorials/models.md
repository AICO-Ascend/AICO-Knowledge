# Use Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/models.md

# Detectron2 「Use Models」文档深度解读

## 【定位】
本文档是 Detectron2 模型使用指南，系统说明如何基于 yacs 配置构建模型、加载/保存检查点、调用模型进行训练与推理，并定义内置模型的标准输入/输出 dict 格式及部分执行（partial execution）模型以获取中间张量的三种方法。

---

## 【技术要点】

1. **从 yacs 配置构建模型**：通过 `detectron2.modeling.build_model(cfg)` 构建得到 `torch.nn.Module`，该函数只搭建结构并填充随机参数，需要另行加载权重。函数族还包括 `build_backbone`、`build_roi_heads`。

2. **检查点加载/保存**：使用 `detectron2.checkpoint.DetectionCheckpointer` —— `DetectionCheckpointer(model).load(file_path_or_url)` 加载（通常用 `cfg.MODEL.WEIGHTS`），`checkpointer.save("model_999")` 保存到 `output/model_999.pth`；识别 PyTorch `.pth` 与 Detectron2 模型库的 `.pkl` 两种格式。

3. **模型调用契约**：`outputs = model(inputs)`，`inputs` 为 `list[dict]`，每个 dict 对应一张图。训练模式必须在 `EventStorage` 上下文内；推理可使用 `DefaultPredictor` 包装器（含模型加载、预处理等默认行为，且单图输入）或手动 `model.eval()` + `torch.no_grad()`。

4. **标准输入格式（训练/推理通用字典键）**：`image` (Tensor, (C,H,W)，通道含义由 `cfg.INPUT.FORMAT` 定义，归一化由 `cfg.MODEL.PIXEL_{MEAN,STD}` 在模型内部完成)；`height`、`width`（期望输出分辨率，可与 image 不同以恢复原始分辨率）；`instances`（训练用，含 `gt_boxes: Boxes`、`gt_classes: Tensor(long, [0, num_categories))`、`gt_masks: PolygonMasks|BitMasks`、`gt_keypoints: Keypoints`）；`sem_seg: Tensor[int]`（(H,W)，值即类别）；`proposals`（Fast R-CNN 风格用，含 `proposal_boxes: Boxes`、`objectness_logits: Tensor`）。推理时仅 `image` 必填，`height/width` 可选。全景分割训练未定义标准格式（使用自定义 DataLoader 产生的自定义格式）。

5. **标准输出格式**：
   - 训练模式：`dict[str -> ScalarTensor]`，即各损失值。
   - 推理模式：`list[dict]`（按图），可能含 `instances`（`pred_boxes: Boxes`、`scores: Tensor(N)`、`pred_classes: Tensor(N, [0, num_categories))`、`pred_masks: Tensor(N,H,W)`、`pred_keypoints: Tensor(N, num_keypoint, 3)`，末维为 (x, y, score)，score>0）；`sem_seg: Tensor(num_categories, H, W)`；`proposals`（`proposal_boxes: Boxes`、`objectness_logits`）；`panoptic_seg`：`(pred: Tensor(H,W), segments_info: Optional[list[dict]])`，当 `segments_info` 存在时每个 dict 含 `id`、`isthing`、`category_id`，缺失 id 视为 void；当 `segments_info is None`，所有像素值 ≥ −1，value −1 为 void，否则 `category_id = pixel // metadata.label_divisor`。

6. **与 DataLoader 的对接**：`detectron2.data.DatasetMapper` 的输出即为符合上述格式的单个 dict，DataLoader 批量化后变成 `list[dict]` 供内置模型消费。

7. **部分执行模型（获取中间特征）三种选项**：
   - **写子模型**：按照教程自定义一个组件（如某 head），返回所需张量；
   - **直接拆解组件调用**：如 `model.backbone(images.tensor)` → `model.proposal_generator(images, features)` → `model.roi_heads(images, features, proposals)`，并对 `mask_features` 在 ROI heads 的 mask_pooler 上手动调用；
   - **PyTorch forward hooks**：获取某模块的输入/输出，必要时与 partial execution 组合。
   - 示例代码片段（原文为单图注释）：`ImageList.from_tensors(...)` → `model = build_model(cfg); model.eval()` → `features = model.backbone(images.tensor)` → `proposals, _ = model.proposal_generator(images, features)` → `instances, _ = model.roi_heads(images, features, proposals)` → `mask_features = [features[f] for f in model.roi_heads.in_features]` → `mask_features = model.roi_heads.mask_pooler(mask_features, [x.pred_boxes for x in instances])`。

---

## 【关键机制与数据】

| 机制 | 原文要点 |
|---|---|
| 配置驱动的构建 | `build_model(cfg)` 仅搭建结构并填充随机参数；`build_backbone`、`build_roi_heads` 为子模型构建器 |
| 模型持久化 | 检查点文件格式为 `.pth`（使用 `torch.{load, save}`）或 `.pkl`（使用 `pickle.{dump, load}`） |
| 图像归一化时机 | 在模型内部完成，使用 `cfg.MODEL.PIXEL_{MEAN, STD}` 与 `cfg.INPUT.FORMAT` |
| 推理分辨率调整 | `height/width` 指**期望**输出分辨率，可与 `image` 张量尺寸不同（如 `image` 已被 resize 但期望原图分辨率输出） |
| 训练依赖 | 必须处于 `with EventStorage() as storage: losses = model(inputs)` 上下文 |
| 推理封装 | `DefaultPredictor` 集成模型加载、预处理，单图输入而非 batch |
| input → list[dict] 来源 | `DatasetMapper` 输出 dict → DataLoader 批量化 → `list[dict]` |
| panoptic_seg 像素类别回推 | 公式 `category_id = pixel // metadata.label_divisor`（见【公式解读】一节） |

原文未给出具体性能数据（FPS、mAP 等）；文档偏 API 契约说明。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式（除一段伪代码式的 `category_id = pixel // metadata.label_divisor` 表达，可视作内联表达式）：

$$
\texttt{category\_id} = \texttt{pixel} // \texttt{metadata.label\_divisor}
$$

- `category_id`：像素对应的类别 ID；
- `pixel`：`panoptic_seg.pred` 张量中 (H,W) 像素位置的整数值（**前提**：`segments_info is None` 且 `pixel ≥ -1`）；
- `metadata.label_divisor`：数据集/模型元数据中的标签除数（一个预定义常量），用于从 segment id 中"剥离"实例编号从而恢复类别；
- 作用：当未提供 `segments_info` 时，仍能从像素值回推出类别 ID，`value == -1` 的像素被视作 void 标签。

---

## 【关联】

本文档与 Detectron2 其他模块及教程存在以下引用/依赖关系：

- **`DetectionCheckpointer`**（[checkpoint 模块](../modules/checkpoint.html#detectron2.checkpoint.DetectionCheckpointer)）：负责 `.pth`/`.pkl` 模型持久化的核心 API。
- **`DefaultPredictor`**（[engine 模块](../modules/engine.html#detectron2.engine.defaults.DefaultPredictor)）：对 `model(inputs)` 的高层单图推理封装，集成加载与预处理。
- **`Instances`、`Boxes`、`PolygonMasks`、`BitMasks`、`Keypoints`**（[structures 模块](../modules/structures.html#detectron2.structures.Instances)）：标准输入/输出中标注（gt_*）与预测（pred_*）字段的容器类；`Instances` 同时承载训练与推理两种用途的对象。
- **`DatasetMapper`**（[data 模块](../modules/data.html#detectron2.data.DatasetMapper)）：默认数据映射器，其单样本输出格式与本文档定义的模型输入格式一致，是 DataLoader → Model 衔接的关键。
- **下一篇教程 `./write-models.md`**：在"部分执行模型"小节中作为可选方案 1 被引用，指导用户如何编写/改造子模型。
- **PyTorch 官方**：[Forward and Backward Function Hooks 教程](https://pytorch.org/tutorials/beginner/former_torchies/nnftc_tutorial.html#forward-and-backward-function-hooks) 用于方案 3。
- **外部论文**：[Panoptic Segmentation (Kirillov et al., 2018, arXiv:1801.00868)](https://arxiv.org/abs/1801.00868) 定义了 void label 语义。

---

## 【使用方法】

| 用途 | 代码/命令 |
|---|---|
| 构建模型 | `from detectron2.modeling import build_model`<br>`model = build_model(cfg)` （返回 `torch.nn.Module`） |
| 加载权重 | `from detectron2.checkpoint import DetectionCheckpointer`<br>`DetectionCheckpointer(model).load(file_path_or_url)` （通常用 `cfg.MODEL.WEIGHTS`） |
| 保存权重 | `checkpointer = DetectionCheckpointer(model, save_dir="output")`<br>`checkpointer.save("model_999")` → 写入 `output/model_999.pth` |
| 训练（必须套 `EventStorage`） | `from detectron2.utils.events import EventStorage`<br>`with EventStorage() as storage:`<br>`    losses = model(inputs)` |
| 推理（推荐） | 使用 `DefaultPredictor`（自带权重加载与预处理，单图输入；用法详见其 API 文档） |
| 推理（手动） | `model.eval()`<br>`with torch.no_grad():`<br>`    outputs = model(inputs)` |
| 推断分辨率控制 | 在 inputs dict 中传入 `"height"`、`"width"` 键以指定**期望**输出分辨率（不依赖 `image` 张量尺寸） |
| 数据接入 | `DatasetMapper` 单样本输出 → DataLoader 批量化 → `list[dict]` 直接喂入内置模型 |
| 获取中间特征（方案 1） | 编写自定义子模型/head（参考 `./write-models.md`） |
| 获取中间特征（方案 2） | 拆解组件顺序调用：`model.backbone(images.tensor)` → `model.proposal_generator(images, features)` → `model.roi_heads(images, features, proposals)`；再对 `model.roi_heads.mask_pooler` 等子模块按需调用（如示例中用 `[features[f] for f in model.roi_heads.in_features]` 取出 mask_features 并送入 `mask_pooler`） |
| 获取中间特征（方案 3） | 在目标 `nn.Module` 上注册 forward hook（参考 PyTorch Hooks 教程） |
| 模型文件读写（手动） | `.pth` → `torch.{load, save}`；`.pkl` → `pickle.{dump, load}` |

> 备注：原文末尾存在截断痕迹（"...of the exist"）。"partially execute a model" 段落结尾的完整说明未给出，所述"三个选项"已据可读到的部分完整提取，未外推未提及之内容。
