# Use Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/centernet2/docs/tutorials/models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/centernet2/docs/tutorials/models.md

# 文档一体化深度解读：`models.md`（detectron2 中的模型使用指南）

> 注：原文在末尾出现截断（"in o"），以下解读基于截至截断处的可读内容。

---

## 【定位】

这篇文档系统说明 detectron2 中**模型对象的构建、检查点加载/保存、训练与推理调用方式、输入/输出数据结构约定、以及获取中间张量的"部分执行"技巧**，是连接配置 (`cfg`)、数据加载器与 detectron2 内置模型之间数据契约的权威参考。

---

## 【技术要点】

1. **模型构建入口**：通过 `detectron2.modeling.build_model(cfg)` 获得一个 `torch.nn.Module`，该函数仅搭建结构并填充随机参数，**不加载任何权重**。子模块另有 `build_backbone`、`build_roi_heads` 等。
2. **检查点加载/保存**：`DetectionCheckpointer(model).load(file_path_or_url)` 负责加载，常用 `cfg.MODEL.WEIGHTS` 作为路径；保存通过 `DetectionCheckpointer(model, save_dir="output").save("model_999")`，输出文件为 `output/model_999.pth`。支持 PyTorch `.pth` 与 model zoo 的 `.pkl` 文件格式。
3. **调用协议**：`outputs = model(inputs)`，`inputs` 类型为 `list[dict]`，每个 `dict` 对应一张图像。训练模式必须置于 `EventStorage` 上下文管理器中才能写入训练统计；推理可直接 `model.eval()` + `torch.no_grad()`，或使用 `DefaultPredictor` 封装类（自动处理加载、预处理、单图而非批量）。
4. **标准输入字典字段**（每图一个）：
   - `"image"`：`(C, H, W)` 张量，归一化在模型内完成，依赖 `cfg.INPUT.FORMAT` 与 `cfg.MODEL.PIXEL_{MEAN,STD}`；
   - `"height"/"width"`：**期望的**输出分辨率（可与缩放后输入分辨率不同，方便回到原图分辨率，更高效更准确）；
   - `"instances"`：训练用真值对象，含 `gt_boxes`、`gt_classes`（`Tensor[long]`，范围 `[0, num_categories)`）、`gt_masks`（`PolygonMasks` 或 `BitMasks`）、`gt_keypoints`；
   - `"sem_seg"`：`(H, W)` 整数张量，0 开始的类别标签；
   - `"proposals"`：仅 Fast R-CNN 风格模型使用，含 `proposal_boxes`、`objectness_logits`。
   - 推理时**仅 `"image"` 必需**，`"height"/"width"` 可选。
5. **标准输出结构**：
   - 训练模式输出 `dict[str -> ScalarTensor]`，即各损失项；
   - 推理模式输出 `list[dict]`，每张图一个字典，可能包含：
     - `"instances"`：`pred_boxes`、`scores`、`pred_classes`，可选 `pred_masks (N, H, W)`、`pred_keypoints (N, num_keypoint, 3)`（每行 `(x, y, score)`，score>0）；
     - `"sem_seg"`：`(num_categories, H, W)` 预测；
     - `"proposals"`：`proposal_boxes`、`objectness_logits`；
     - `"panoptic_seg"`：元组 `(pred, segments_info)`，`pred` 形状 `(H, W)`，`segments_info` 为可选 `list[dict]`，每项含 `id`、`isthing`、`category_id`。像素未出现在 `segments_info` 中视为 void 标签（参考 Panoptic Segmentation 论文）。若 `segments_info is None`，则 `pred` 中像素值 ≥ -1，`-1` 代表 void，否则 `category_id = pixel // metadata.label_divisor`。
6. **获取中间张量的三种方法**：
   - **(a) 编写子模型**：按 `write-models.md` 教程重写某个组件（如 head），使其返回所需的中间输出；
   - **(b) 部分执行**：跳过 `forward()`，按数据流手动调用子组件（例：从 `ImageList.from_tensors` 出发，依次调用 `model.backbone` → `model.proposal_generator` → `model.roi_heads`，并通过 `model.roi_heads.in_features` 与 `model.roi_heads.mask_pooler` 拿到 mask 特征）；
   - **(c) forward hooks**：注册 PyTorch 前向钩子获取特定模块的输入/输出，可与方法 (b) 互补。
   - 原文强调："All options require you to read documentation and sometimes code of the existing models to understand the internal logic"。

---

## 【关键机制与数据】

**工作原理与数据流（基于原文）：**

- **构建 → 加载 → 调用** 链路：`build_model(cfg)` 构造空壳 → `DetectionCheckpointer.load(...)` 把权重灌入 → 训练用 `EventStorage` 包裹的 `model(inputs)`，推理用 `model.eval()` + `model(inputs)` 或 `DefaultPredictor`。
- **数据加载器对接（原文："How it connects to data loader"）**：默认的 `DatasetMapper` 输出的 `dict` 直接遵循上述"模型输入格式"；经过数据加载器的 batching 后变成 `list[dict]`，恰好是内置模型期望的输入类型——这意味着若自定义数据加载器，输出格式必须与此约定一致。
- **图像分辨率分离（原文："image" vs "height/width"）**：模型内部对 `image` 字段做缩放/归一化，但若提供 `"height"/"width"`，输出会回到这两个字段指定的分辨率，可与输入 `image` 的实际分辨率不同——文档明确指出这样做 "is more efficient and accurate"。
- **Panoptic Segmentation 输出解析**：当 `segments_info` 为 `None` 时，像素值的归类规则由 `category_id = pixel // metadata.label_divisor` 给出。

**性能/数字数据**：原文未给出任何 benchmark、性能对比或量化指标，因此本节不补充。

> 原文："It includes default behavior including model loading, preprocessing, and operates on single image rather than batches."
> 原文："Confidence scores are larger than 0."
> 原文："If a pixel's id does not exist in segments_info, it is considered to be void label defined in Panoptic Segmentation (https://arxiv.org/abs/1801.00868)."
> 原文："category_id = pixel // metadata.label_divisor"
> 原文："All options require you to read documentation and sometimes code of the existing models to understand the internal logic"

---

## 【表格解读】

原文无表格。（整篇文档以代码块、列表项和散文式描述构成，未出现任何 markdown 表格或参数对照表。）

---

## 【公式解读】

原文无独立公式（LaTeX 或伪代码形式）。

可视为"类公式"的两处原文片段已包含在前文：

- **逐字保留**：`category_id = pixel // metadata.label_divisor`
  - 符号说明：`pixel` 为 `pred` 张量中某位置的整数值；`metadata.label_divisor` 是来自数据集元信息的常数；`category_id` 为推得的类别编号；`//` 为整数除法。该式仅在 `segments_info is None` 时生效。
- **部分执行的代码骨架**（视作伪代码）：
  ```python
  images = ImageList.from_tensors(...)
  model = build_model(cfg)
  model.eval()
  features = model.backbone(images.tensor)
  proposals, _ = model.proposal_generator(images, features)
  instances, _ = model.roi_heads(images, features, proposals)
  mask_features = [features[f] for f in model.roi_heads.in_features]
  mask_features = model.roi_heads.mask_pooler(mask_features, [x.pred_boxes for x in instances])
  ```
  含义：手动沿"backbone → proposal_generator → roi_heads"管线推进，并将 `roi_heads.in_features` 指定的特征图与 ROI 框（取自 `instances.pred_boxes`）送入 `mask_pooler`，得到 mask 头所需的池化后特征。

---

## 【关联】

本文是 detectron2 教程体系中的"模型使用"入口，与以下模块在内部链接中显式互联：

- **检查点**：`DetectionCheckpointer`（`../modules/checkpoint.html#detectron2.checkpoint.DetectionCheckpointer`）——本文的 Load/Save 一节即围绕它展开，链接指向其 API 详情。
- **推理封装**：`DefaultPredictor`（`../modules/engine.html#detectron2.engine.defaults.DefaultPredictor`）——本文在 Inference 节中作为"开箱即用"的简易推理包装器推荐使用。
- **数据结构**（多次出现，构成输入/输出的契约基础）：
  - `Instances`（`../modules/structures.html#detectron2.structures.Instances`）——出现在输入 `instances`/`proposals`、输出 `instances`/`proposals`。
  - `Boxes`（`../modules/structures.html#detectron2.structures.Boxes`）——包装 `gt_boxes`/`pred_boxes`/`proposal_boxes`。
  - `PolygonMasks` 与 `BitMasks`（`../modules/structures.html#detectron2.structures.PolygonMasks` / `BitMasks`）——`gt_masks` 字段的二选一表示。
  - `Keypoints`（`../modules/structures.html#detectron2.structures.Keypoints`）——`gt_keypoints` 字段。
- **数据加载**：`DatasetMapper`（`../modules/data.html#detectron2.data.DatasetMapper`）——"How it connects to data loader"一节明示：mapper 输出格式即本文定义的标准输入格式，batching 后得到 `list[dict]`。
- **自定义模型**：在 "Partially execute a model" 第 1 项中链接 `./write-models.md`，说明如需更精细地控制中间输出，可参考配套的"编写模型"教程。

> 上游依赖：`cfg`、`build_model`、`EventStorage`（`detectron2.utils.events`）；下游消费者：训练 hook、评估器、可视化工具——文档未直接列出，但按 detectron2 框架惯例均消费此处的 `list[dict]` 输出。

---

## 【使用方法】

以下汇总原文给出的可直接运行/复制的命令与配置项：

1. **构建模型（原文命令）**：
   ```python
   from detectron2.modeling import build_model
   model = build_model(cfg)  # returns a torch.nn.Module
   ```
2. **加载已有权重（原文命令）**：
   ```python
   from detectron2.checkpoint import DetectionCheckpointer
   DetectionCheckpointer(model).load(file_path_or_url)  # 常用 cfg.MODEL.WEIGHTS
   ```
3. **保存权重（原文命令）**：
   ```python
   checkpointer = DetectionCheckpointer(model, save_dir="output")
   checkpointer.save("model_999")  # → output/model_999.pth
   ```
4. **训练模式下调用（必须在 `EventStorage` 内，原文命令）**：
   ```python
   from detectron2.utils.events import EventStorage
   with EventStorage() as storage:
       losses = model(inputs)
   ```
5. **推理时直接调用（原文命令）**：
   ```
   model.eval()
   with torch.no_grad():
       outputs = model(inputs)
   ```
   或改用 `DefaultPredictor`（本文档推荐用于"simple inference"；具体参数与使用方式请见其 API 文档页面）。
6. **手动操作 `.pth`/`.pkl`**：原文允许用 `torch.{load,save}` 与 `pickle.{dump,load}` 任意操作模型文件。
7. **相关配置项**（用于驱动标准输入语义，原文明确提及）：
   - `cfg.MODEL.WEIGHTS`：加载权重的文件路径。
   - `cfg.INPUT.FORMAT`：定义 `image` 张量通道含义。
   - `cfg.MODEL.PIXEL_MEAN` 与 `cfg.MODEL.PIXEL_STD`：模型内部图像归一化参数。
   - 输入 `dict` 中的 `"height"/"width"`：指定输出分辨率；若希望在原图分辨率下输出，应提供原始图像高度/宽度。
8. **部分执行获取中间张量**：见前文"关键机制"小节给出的完整 7 行代码骨架，其等价于在已知模型内部成员（`backbone`、`proposal_generator`、`roi_heads.in_features`、`roi_heads.mask_pooler`）基础上的最小化管线调用。

**未涉及**（原文未提及，需查阅其他文档）：分布式训练包装、AMP 混合精度、Triton/TensorRT 导出等均不在本文档范围内。
