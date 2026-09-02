# Use Custom Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/centernet2/docs/tutorials/datasets.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/centernet2/docs/tutorials/datasets.md

# 深度解读：detectron2 自定义数据集使用指南

---

## 【定位】

这篇文档解决"如何在 detectron2 中接入/注册自有格式数据集"的问题，系统化说明 `DatasetCatalog` 与 `MetadataCatalog` 的设计原理、标准数据集字典（Standard Dataset Dicts）的字段约定、以及为新任务扩展自定义字典与 Metadata 的规范。

---

## 【技术要点】

1. **数据集注册（Register）机制**：通过 `DatasetCatalog.register("my_dataset", my_dataset_function)` 把一个返回 `list[dict]` 的函数与数据集名绑定；函数必须**幂等**（多次调用返回相同顺序、相同内容的数据），注册在**进程生命周期内有效**。
2. **标准数据集字典（Standard Dataset Dicts）**：以 COCO 风格为基础，每个 dict 描述一张图；按任务差异承载不同字段——`Common` 字段为 `file_name, height, width, image_id`；实例检测/分割需 `annotations`；语义分割需 `sem_seg_file_name`；全景分割需 `pan_seg_file_name` 与 `segments_info`。
3. **bbox 坐标格式约束**：bbox 必须为 4 个 float 的 list，且 `bbox_mode` 取自 `BoxMode` 枚举，目前支持 `BoxMode.XYXY_ABS` 与 `BoxMode.XYWH_ABS`。
4. **关键点格式约定**：`keypoints` 为 `[x1, y1, v1, ..., xn, yn, vn]`；`n = 关键点类别数`；X/Y 为绝对实数坐标，范围 `[0, W or H]`；detectron2 内部对 COCO 整数坐标统一 **加 0.5** 转为浮点连续坐标。
5. **Mask 格式双形态**：实例 `segmentation` 可为多边形 list 或 COCO 压缩 RLE dict（`size` + `counts`）；使用 RLE 时必须设置 `cfg.INPUT.MASK_FORMAT = "bitmask"`。
6. **Metadata 与数据集字典的分工**：全样本共有的信息（类别名、类别颜色、文件根目录等）放在 `MetadataCatalog.get(dataset_name)` 中，**不放入每个样本 dict**，以避免内存膨胀。

---

## 【关键机制与数据】

**工作原理（原文描述）：**

- **两阶段接入流程**：原文写明"使用 detectron2 数据加载器接入自定义数据集，需要：① Register 数据集（让 detectron2 知道如何获取数据）；② 可选地 Register metadata。"
- **数据字典生命周期**：原文："all dicts are stored in memory (sometimes serialized and with multiple copies). To save memory, each dict is meant to contain small but sufficient information about each sample, such as file names and annotations. Loading full samples typically happens in the data loader."
- **空标注图像的处理**：原文："If `annotations` is an empty list, it means the image is labeled to have no objects. Such images will by default be removed from training, but can be included using `DATALOADER.FILTER_EMPTY_ANNOTATIONS`."
- **全景分割 id 映射**：原文："If an id does not appear in `segments_info`, the pixel is considered unlabeled and is usually ignored in training & evaluation."
- **PanopticFPN 特例**：原文以 note 标注："The PanopticFPN model does not use the panoptic segmentation format defined here, but a combination of both instance segmentation and semantic segmentation data format."
- **Fast R-CNN 预计算 proposals**：原文说明 Fast R-CNN（with pre-computed proposals）"are rarely used today"，需额外字段 `proposal_boxes`（shape `(K, 4)`）、`proposal_objectness_logits`（shape `(K,)`）、`proposal_bbox_mode`（默认 `BoxMode.XYXY_ABS`）。

**性能数据**：原文未提供性能/benchmark 数字。

---

## 【表格解读】

原文含 1 个表格，按任务列出字段。逐字还原如下：

| Task | Fields |
| --- | --- |
| Common | file_name, height, width, image_id |
| Instance detection/segmentation | annotations |
| Semantic segmentation | sem_seg_file_name |
| Panoptic segmentation | pan_seg_file_name, segments_info |

**逐行解读：**

- **Common 行**：`file_name` 为图像完整路径；`height`、`width` 为图像尺寸整数；`image_id`（str 或 int）为唯一 id，**被评估器（evaluator）依赖以识别图像**。所有任务都至少需要这 4 项。
- **Instance detection/segmentation 行**：额外需要 `annotations`（list[dict]），每个 dict 对应一个实例，含 `bbox`、`bbox_mode`、`category_id`，可选 `segmentation`、`keypoints`、`iscrowd`。
- **Semantic segmentation 行**：额外需要 `sem_seg_file_name`，指向**灰度图**，**像素值为整数标签**。
- **Panoptic segmentation 行**：需要 `pan_seg_file_name`（**RGB 图**，像素值经 `panopticapi.utils.id2rgb` 编码为整数 id）与 `segments_info`（list[dict]，定义每个 id 的 `id`/`category_id`/`iscrowd`）。

---

## 【公式解读】

原文无公式。

（坐标转换方面仅以自然语言描述，例如"Detectron2 adds 0.5 to COCO keypoint coordinates to convert them from discrete pixel indices to floating point coordinates"，未给出代数表达式，故不视为公式。）

---

## 【关联】

基于文末链接梳理的依赖/上下游关系：

- **核心 API**：`detectron2.data.DatasetCatalog`（../modules/data.html#detectron2.data.DatasetCatalog）、`detectron2.data.MetadataCatalog`（../modules/data.html#detectron2.data.MetadataCatalog）—— 本文档的全部内容围绕这两个 Catalog。
- **bbox 模式枚举**：`detectron2.structures.BoxMode`（../modules/structures.html#detectron2.structures.BoxMode，被引用 2 次，分别约束 `bbox_mode` 与 `proposal_bbox_mode`）。
- **数据集字典结构**：使用 `BoxMode` 表达边界框，配合 `list[dict]` 表示样本集合。
- **内置数据集说明**：链接 [builtin_datasets.md](builtin_datasets.md)，是"标准字典 + 内置支持"的对应文档。
- **数据加载层**：链接 [./data_loading.md](data_loading.md)，文档明确："Usually this requires writing a new `mapper` for the dataloader (see [Use Custom Dataloaders](./data_loading.md))."
- **评估器**：`detectron2.evaluation.DatasetEvaluator`（../modules/evaluation.html#detectron2.evaluation.DatasetEvaluator），依赖 `image_id` 字段来识别图像。
- **COCO JSON 加载工具**：`detectron2.data.datasets.load_coco_json`（../modules/data.html#detectron2.data.load_coco_json），与 RLE mask 解析相关（本文档提到 `pycocotools.mask.encode(...)`）。
- **proposals 加载**：`detectron2.data.load_proposals_into_dataset`（../modules/data.html#detectron2.data.load_proposals_into_dataset），对应 Fast R-CNN `proposal_boxes` / `proposal_objectness_logits` 字段。
- **项目示例**：../../projects/TensorMask，作为引用项目（用于演示自定义任务扩展的工程范式）。
- **实时教程**：Colab tutorial（https://colab.research.google.com/drive/16jcaJoc6bCFAQ96jDe2HwtXj7BMD_-m5）——"has a live example of how to register and train on a dataset of custom formats"。

---

## 【使用方法】

**启用方式（原文给出）：**

1. **编写数据集函数**：实现一个返回 `list[dict]` 的函数，每个 dict 满足标准格式（推荐）或自定义格式。
2. **注册数据集**：
   ```python
   from detectron2.data import DatasetCatalog
   DatasetCatalog.register("my_dataset", my_dataset_function)
   ```
3. **访问数据**：
   ```python
   data: List[Dict] = DatasetCatalog.get("my_dataset")
   ```
4. **注册元数据**（可选）：通过 `MetadataCatalog.get(dataset_name).some_metadata` 访问键值映射，用于存放类别名、类别颜色、文件根等共享信息（原文段落末尾 `you may also want t...` 被截断，具体注册语法未在原文片段中给出完整命令）。
5. **空标注训练开关**：配置 `DATALOADER.FILTER_EMPTY_ANNOTATIONS` 以决定是否将空标注图像纳入训练。
6. **Mask 加载配合**：使用 RLE 压缩 mask 时，须设置 `cfg.INPUT.MASK_FORMAT = "bitmask"`。

**原文未涉及**：Metadata 的具体注册 API 命令（`MetadataCatalog.register/...` 等）以及更多命令/CLI 入口，因原文末段以 `you may also want t` 截断而缺失。
