# Use Custom Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/tutorials/datasets.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/tutorials/datasets.md

```markdown
# 一体化深度解读: detectron2 《Use Custom Datasets》

---

## 【定位】
这篇文档解决"如何让 detectron2 识别并消费用户自定义数据集"的问题——通过解释 `DatasetCatalog` / `MetadataCatalog` 两套注册机制的字段语义, 使开发者能够把自有数据接入 detectron2 的标准数据加载管线。

---

## 【技术要点】

1. **数据集注册两步法**: 任何自定义数据集都需要 (1) 调用 `DatasetCatalog.register("name", fn)` 注册一个返回 `list[dict]` 的取数函数; (2) 可选地通过 `MetadataCatalog.get("name").key = value` 注入元数据(如 `thing_classes`)。注册的函数"必须保证多次调用返回相同数据", 注册在进程生命周期内持续有效。

2. **标准 dict 必填字段**: `file_name`(全路径, EXIF 会触发旋转/翻转)、`height` / `width`(int)、`image_id`(str/int, 评估必需),以及 `annotations`(list[dict], 关键点/实例任务必需, 可为空但默认会被过滤)。`DATALOADER.FILTER_EMPTY_ANNOTATIONS` 控制是否保留空标注样本。

3. **每条 annotation 必填三项**: `bbox`(`list[float]` 4 元素)、`bbox_mode`(int, 必须是 `BoxMode.XYXY_ABS` 或 `BoxMode.XYWH_ABS` 之一)、`category_id`(int ∈ [0, num_categories-1], num_categories 保留为 "background")。

4. **分割/关键点的可选字段**:
   - `segmentation`: 两种形态——`list[list[float]]`(多边形, `[x1,y1,...,xn,yn]`, 绝对像素坐标)或 `dict`(COCO 压缩 RLE, 键 `"size"` / `"counts"`, 由 `pycocotools.mask.encode(np.asarray(mask, order="F"))` 生成); 若用 RLE 必须设置 `cfg.INPUT.MASK_FORMAT = "bitmask"`。
   - `keypoints` 格式 `[x1,y1,v1,...,xn,yn,vn]`, `n` 等于关键点类别数; detectron2 在加载 COCO 关键点时"加 0.5"将其从离散像素索引转换为浮点坐标(原始 COCO 为 [0, H-1] 或 [0, W-1] 的整数)。
   - `iscrowd`: 0/1, 默认 0, 对应 COCO 的 "crowd region"。

5. **Fast R-CNN 预计算 proposals 字段**: `proposal_boxes`(`(K,4)` numpy 数组)、`proposal_objectness_logits`(`(K,)` numpy 数组)、`proposal_bbox_mode`(int, 成员 of `BoxMode`, 默认 `BoxMode.XYXY_ABS`)。

6. **内置 metadata 键约定**: `thing_classes` / `thing_colors` (用于实例任务, 颜色范围 [0,255], 缺省随机)、`stuff_classes` / `stuff_colors` (用于语义/全景分割)、`keypoint_names` / `keypoint_flip_map` (用于关键点检测)。其中 `thing_classes` 在调用 `load_coco_json` 时会自动填入。

7. **自定义 dict 的内存原则**: 所有 dict 都常驻内存(可能多份副本), 因此 dict "应当只保存小而足的信息"(路径与标注), 真实样本的加载延后到 dataloader 中; 跨样本共享的属性必须放在 `Metadata`, **不要**塞进每个 sample dict。

---

## 【关键机制与数据】

**工作原理** (原文):
- 注册阶段: `DatasetCatalog.register(name, fn)` 把名字与取数函数绑定, 通过 `DatasetCatalog.get(name)` 取出 `List[Dict]`; 元数据阶段: `MetadataCatalog.get(name).thing_classes = [...]` 把共享属性挂到元数据节点。
- 数据流: 用户函数返回 `list[dict]` → 注册表查询 → dataloader / mapper 在运行时按需读图、做增广 → 评估时通过 `image_id` 关联 GT 与预测。
- "Fast R-CNN (with precomputed proposals) is rarely used today." —— 文档明确指出带预计算 proposals 的 Fast R-CNN 已很少使用。

**性能/数据数字**: 原文**未提供**任何 benchmark 数字、速度、mAP、显存或训练时长等性能指标。文档仅说明"`category_id` 取值范围 [0, num_categories-1]"、`segmentation` 像素值在 `[0,255]` 的颜色范围、`keypoint` 数量等于关键点类别数等**结构性**约定, 不属于性能数据。

---

## 【表格解读】

**原文无表格。** 文档以嵌套列表方式列举了标准 dict 字段、annotation 子字段和 metadata 键, 未使用 markdown 表格。

---

## 【公式解读】

**原文无公式。** 文档未出现 LaTeX 或伪代码形式的数学公式, 只在文本中使用了 `list[float]`、`list[list[float]]`、`dict`、`int` 等类型注解, 这些不属于公式。

---

## 【关联】

依据文末及文中出现的内部链接, 本文与以下模块/特性构成上下游:

- **[`../modules/data.html#detectron2.data.DatasetCatalog`](../modules/data.html#detectron2.data.DatasetCatalog)** — 本文主轴, 提供 `register` / `get` 接口, 是自定义数据集的"入口"。
- **[`../modules/data.html#detectron2.data.MetadataCatalog`](../modules/data.html#detectron2.data.MetadataCatalog)** — 与上者配对, 承载跨样本共享的元数据(类名、颜色、关键点翻折映射等)。
- **[`builtin_datasets.md`](builtin_datasets.md)** — 列举 detectron2 已内置支持的数据集, 是判断"是否需要自定义"的对照表。
- **[`../modules/structures.html#detectron2.structures.BoxMode`](../modules/structures.html#detectron2.structures.BoxMode)** (出现两次) — 定义 `bbox_mode` / `proposal_bbox_mode` 的合法取值集合 `BoxMode.XYXY_ABS` 与 `BoxMode.XYWH_ABS`, 是 bbox 表示层。
- **[`./data_loading.md`](./data_loading.md)** — 自定义 dict 进入 dataloader 时, 需要写对应的 `mapper` 才能正确解析(原文明确指引: "writing a new mapper for the dataloader")。
- **[`../modules/data.html#detectron2.data.datasets.load_coco_json`](../modules/data.html#detectron2.data.datasets.load_coco_json)** — 当输入是 COCO 格式 JSON 时可直接调用, 它会自动设置 `thing_classes`。
- **[`../modules/data.html#detectron2.data.load_proposals_into_dataset`](../modules/data.html#detectron2.data.load_proposals_into_dataset)** — 与 Fast R-CNN 预计算 proposals 路径相关, 用于把 proposals 灌入数据集 dict。
- **[`../modules/evaluation.html#detectron2.evaluation.DatasetEvaluator`](../modules/evaluation.html#detectron2.evaluation.DatasetEvaluator)** — 评估模块, 通过 `image_id` 把数据集 dict 与预测结果匹配, 因此 `image_id` 被声明为"evaluation 必需"。
- **[`../../projects/TensorMask`](../../projects/TensorMask)** — 项目示例, 演示如何基于本文的注册机制为新任务构建自定义数据集(原文链接目录提到, 用于展示"新任务自定义 dict"的下游消费方式)。

整体上, 本文位于 detectron2 数据层 (DatasetCatalog / MetadataCatalog) 与下游消费方 (mapper、evaluator、可视化、augmentation) 之间的契约位置。

---

## 【使用方法】

以下均来自原文, 按使用流程列出:

1. **注册数据集函数** (Python):
   ```python
   def my_dataset_function():
       ...
       return list[dict]  # 标准 dict 或自定义 dict

   from detectron2.data import DatasetCatalog
   DatasetCatalog.register("my_dataset", my_dataset_function)
   # 取数:
   data: List[Dict] = DatasetCatalog.get("my_dataset")
   ```

2. **注册元数据** (Python):
   ```python
   from detectron2.data import MetadataCatalog
   MetadataCatalog.get("my_dataset").thing_classes = ["person", "dog"]
   ```

3. **COCO 风格 JSON 直加载** (原文): 调用 `load_coco_json`, 它会自动写入 `thing_classes`; bbox 默认 `XYWH_ABS`。

4. **bbox 格式配置** (原文): `bbox_mode` / `proposal_bbox_mode` 必须是 `BoxMode.XYXY_ABS` 或 `BoxMode.XYWH_ABS`; proposals 默认 `BoxMode.XYXY_ABS`。

5. **RLE 分割 mask 的 mask format 配置** (原文): 当使用 COCO 压缩 RLE dict 形式的 `segmentation` 时, 必须设置 `cfg.INPUT.MASK_FORMAT = "bitmask"`。

6. **空标注样本过滤** (原文): 通过 `DATALOADER.FILTER_EMPTY_ANNOTATIONS` 配置项决定是否保留 `annotations` 为空的图片(默认会被剔除)。

7. **EXIF 触发增强** (原文): 当图像带 EXIF 元数据时, dataloader 可能对其应用旋转/翻转——因此 `file_name` 应提供"图像文件的完整路径"。

> 注: 原文末尾被截断(`keypoint_flip_map` 描述以 "Used for ke" 结束), 上述 `【使用方法】` 中未涉及被截断部分; 该截断段落的键(`keypoint_flip_map`)在前文 metadata 列表中已提及, 后续语义以原文实际给出为准。
```
