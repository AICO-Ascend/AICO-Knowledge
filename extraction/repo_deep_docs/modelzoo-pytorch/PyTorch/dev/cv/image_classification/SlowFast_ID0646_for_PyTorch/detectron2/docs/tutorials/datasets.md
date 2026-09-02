# Use Custom Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/datasets.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/datasets.md

# Detectron2 自定义数据集使用指南 - 深度解读

## 【定位】

这篇文档是 detectron2 数据集 API（`DatasetCatalog` 与 `MetadataCatalog`）的官方使用教程,解决「如何把自定义数据集接入 detectron2 现有的数据加载与训练流水线」这一问题,系统阐述数据集注册机制、标准/自定义字典格式约定、以及贯穿全数据集的元数据（Metadata）机制。

---

## 【技术要点】

1. **两步接入流程**:使用自定义数据集需完成 (1) `DatasetCatalog.register(name, func)` 注册一个返回 `list[dict]` 的函数;(2) 可选地注册 `Metadata` 元数据。注册在进程结束前一直生效,且同名函数多次调用必须返回**相同顺序、相同内容**的数据。

2. **标准数据集字典 (`Standard Dataset Dicts`)**:每个 `dict` 对应一张图片,核心字段按任务分为四类:通用字段 (`file_name`、`height`、`width`、`image_id`)、实例检测/分割 (`annotations`)、语义分割 (`sem_seg_file_name`)、全景分割 (`pan_seg_file_name` + `segments_info`)。

3. **bbox 坐标格式约束**:`bbox_mode` 必须是 `detectron2.structures.BoxMode` 枚举成员,目前支持 `BoxMode.XYXY_ABS` 与 `BoxMode.XYWH_ABS`;`category_id` 取值范围 `[0, num_categories-1]`,其中 `num_categories` 保留作"背景"类。

4. **分割标注双格式**:`segmentation` 既可为 `list[list[float]]`(每个 `list[float]` 为一条多边形 `[x1,y1,…,xn,yn]`,n≥3,绝对像素坐标),也可为 dict(COCO 压缩 RLE,含 `size`/`counts` 键,可通过 `pycocotools.mask.encode(np.asarray(mask, order="F"))` 生成);后者需将 `cfg.INPUT.MASK_FORMAT` 设为 `"bitmask"`。

5. **关键点格式与 COCO 转换**:`keypoints` 格式为 `[x1,y1,v1,…,xn,yn,vn]`,n 等于关键点类别数;Xs/Ys 是 `[0, W 或 H]` 范围内的绝对浮点坐标。COCO 原坐标是 `[0, W-1 或 H-1]` 的离散像素索引,**detectron2 会加 0.5** 转换为浮点坐标。

6. **预计算 proposals (Fast R-CNN)**:需额外提供 `proposal_boxes`(`shape=(K,4)` 的 numpy 2D 数组)、`proposal_objectness_logits`(`shape=(K,)` 的 numpy 数组)、`proposal_bbox_mode`(默认 `BoxMode.XYXY_ABS`)。空 `annotations` 列表默认从训练中剔除,可通过 `DATALOADER.FILTER_EMPTY_ANNOTATIONS` 保留。

---

## 【关键机制与数据】

**数据集注册机制**:`DatasetCatalog.register("my_dataset", my_dataset_function)` 将字符串名与返回数据的函数绑定;后续通过 `DatasetCatalog.get("my_dataset")` 取出 `List[Dict]`。该机制本质是一个进程内的全局名字到函数/数据的映射表。

**自定义数据集字典的内存权衡** (原文):"all dicts are stored in memory (sometimes serialized and with multiple copies)"。每个 dict 应只包含**小但充分**的信息(文件名+标注),真实样本加载发生在 dataloader;跨样本共享的属性必须放 Metadata,否则浪费内存。

**全景分割文件编码** (原文):panoptic 真实标签是 RGB 图,像素值由 `panopticapi.utils.id2rgb` 编码,id 定义在 `segments_info` 中;未在 `segments_info` 中出现的 id 在训练/评估中通常被忽略。

**关键点可见性字段 v[i]**:用于表示该关键点的可见性(参考 COCO 格式说明链接 cocodataset.org/#format-data)。

**PanopticFPN 模型特例** (原文):"The PanopticFPN model does not use the panoptic segmentation format defined here, but a combination of both instance segmentation and semantic segmentation data format"——它复用了 instance + semantic 两条数据流,而非本节描述的 panoptic 格式。

---

## 【表格解读】

**原文表格(任务字段对照表)**:

| Task | Fields |
|---|---|
| Common | `file_name`, `height`, `width`, `image_id` |
| Instance detection/segmentation | `annotations` |
| Semantic segmentation | `sem_seg_file_name` |
| Panoptic segmentation | `pan_seg_file_name`, `segments_info` |

逐行解读:
- **Common 行**:所有任务共享 4 个通用字段——`file_name`(图像完整路径)、`height`/`width`(图像尺寸,整数)、`image_id`(唯一 id,字符串或整数,评估器需据此识别图像)。
- **Instance detection/segmentation 行**:仅需追加 `annotations`(实例标注列表),实例分割和关键点检测复用同一结构。
- **Semantic segmentation 行**:只需 `sem_seg_file_name`,指向单通道灰度图,像素值是整数类别标签。
- **Panoptic segmentation 行**:同时需要 `pan_seg_file_name`(RGB 图,像素值是 `id2rgb` 编码的整数 id)与 `segments_info`(定义每个 id 含义的列表)。

---

## 【公式解读】

原文无公式。

---

## 【关联】

依据文末与文中出现的内部链接,本文档与下列模块/文档形成上下游依赖:

- **上游/横向文档**:
  - [builtin_datasets.md](./builtin_datasets.md)——列出 detectron2 内置支持的数据集,提供 COCO 等标准数据集的注册指引(文中两次引用,包括 PanopticFNN 例外的说明跳转)。
  - [Use Custom Dataloaders](./data_loading.md)——处理自定义数据集字典时通常需要编写新的 mapper,本文档明确指向该文档。
  - [TensorMask 项目](../../projects/TensorMask)——作为 detectron2 项目示例,展示自定义数据集与自定义模型协同工作的范式。

- **API 模块**:
  - [`detectron2.data.DatasetCatalog`](../modules/data.html#detectron2.data.DatasetCatalog)——数据集注册中心,本文档核心 API。
  - [`detectron2.data.MetadataCatalog`](../modules/data.html#detectron2.data.MetadataCatalog)——元数据注册中心,与 DatasetCatalog 并列。
  - [`detectron2.structures.BoxMode`](../modules/structures.html#detectron2.structures.BoxMode)——定义 bbox 坐标格式枚举(`XYXY_ABS`/`XYWH_ABS`),`bbox_mode`/`proposal_bbox_mode` 字段必须引用其成员。
  - [`detectron2.evaluation.DatasetEvaluator`](../modules/evaluation.html#detectron2.evaluation.DatasetEvaluator)——评估器接口,`image_id` 字段被评估器用于识别图像。
  - [`detectron2.data.datasets.load_coco_json`](../modules/data.html#detectron2.data.datasets.load_coco_json)——COCO 格式 JSON 加载函数,与标准字典格式直接对应。
  - [`detectron2.data.load_proposals_into_dataset`](../modules/data.html#detectron2.data.load_proposals_into_dataset)——把预计算 proposals 注入数据集的工具函数,服务于 Fast R-CNN 训练链路。

---

## 【使用方法】

**注册数据集(原文示例命令)**:
```python
def my_dataset_function():
    ...
    return list[dict]  # Detectron2 标准字典 或 自定义字典

from detectron2.data import DatasetCatalog
DatasetCatalog.register("my_dataset", my_dataset_function)
data: List[Dict] = DatasetCatalog.get("my_dataset")
```

**关键配置项**:
- `cfg.INPUT.MASK_FORMAT = "bitmask"` —— 当 `segmentation` 采用 COCO 压缩 RLE (`dict`) 格式时,使用默认 dataloader 必须设置。
- `cfg.DATALOADER.FILTER_EMPTY_ANNOTATIONS` —— 控制是否剔除 `annotations` 为空列表的样本(默认剔除,设 False 保留)。
- `cfg.MODEL.ROI_HEADS.NUM_CLASSES`(关联) —— 与 `category_id ∈ [0, num_categories-1]` 的范围相对应,需配合 Metadata 中的类别数设置。

**元数据访问模式(原文)**:`MetadataCatalog.get(dataset_name).some_metadata`,用于存放类名、类颜色、文件根目录等共享属性。

**Colab 实时示例**(原文提供):https://colab.research.google.com/drive/16jcaJoc6bCFAQ96jDe2HwtXj7BMD_-m5 —— 演示自定义格式数据集的注册与训练全流程。
