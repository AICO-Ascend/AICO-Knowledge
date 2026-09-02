# Use Custom Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/Faster_Mask_RCNN_for_PyTorch/docs/tutorials/datasets.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/Faster_Mask_RCNN_for_PyTorch/docs/tutorials/datasets.md

# 一体化深度解读: Detectron2 自定义数据集使用指南

---

## 【定位】

本文档解决 detectron2 框架中如何注册、使用自定义数据集的问题,通过阐述 `DatasetCatalog` 与 `MetadataCatalog` 两大数据 API 的工作机制,使用户能够在复用 detectron2 数据加载器的前提下,接入自有格式的数据(标准 COCO 式标注或自定义任务标注),并为下游增强/评估/可视化提供元数据支撑。

---

## 【技术要点】

1. **两步注册流程**: 自定义数据集需先实现一个返回 `list[dict]` 的函数,然后通过 `DatasetCatalog.register("my_dataset", my_dataset_function)` 告知 detectron2;后续可通过 `DatasetCatalog.get("my_dataset")` 取回数据。注册在进程退出前持续生效,且函数多次调用需返回相同数据。

2. **标准数据集字典格式(类 COCO JSON)**: 每张图像一个 dict,核心字段包括 `file_name`、`height`、`width`、`image_id`、`annotations`(实例/关键点标注列表,可为空)以及 `sem_seg_file_name`(语义分割任务需要)。`annotations` 子字典中 `bbox`、`bbox_mode`、`category_id` 三项必填。

3. **bbox 坐标格式枚举**: `bbox_mode` 必须是 `BoxMode`(枚举类)的成员,当前支持 `BoxMode.XYXY_ABS` 与 `BoxMode.XYWH_ABS` 两种格式;Fast R-CNN 的预计算 proposal 默认为 `BoxMode.XYXY_ABS`。

4. **类别 ID 范围约束**: `category_id` 取值范围为 `[0, num_categories-1]`,其中 `num_categories` 保留用于表示"背景"类别(如适用)。

5. **分割掩码两种表达**: `segmentation` 字段可为多边形列表 `list[list[float]]`(每个连通分量一个 `[x1,y1,...,xn,yn]` 绝对像素坐标)或 COCO 压缩 RLE dict(键 `"size"` 与 `"counts"`);后者若使用默认数据加载器,需将 `cfg.INPUT.MASK_FORMAT` 设为 `"bitmask"`。

6. **关键点坐标格式与差异**: 关键点字段为 `[x1,y1,v1,...,xn,yn,vn]` 的扁平数组,v 表示可见性;detectron2 与 COCO 的关键点坐标存在偏移——COCO 是 `[0, H-1 或 W-1]` 的离散像素整数,detectron2 在加载时会将 COCO 关键点坐标加 0.5 转为浮点连续坐标。

7. **元数据(Metadata)机制**: 通过 `MetadataCatalog.get(dataset_name).key = value` 为数据集附加全局共享信息(类名、颜色、关键点名等),常被增强、评估、可视化、日志等功能消费;原文档明确列举的内置元数据键包括 `thing_classes`、`thing_colors`、`stuff_classes`、`stuff_colors`、`keypoint_names`、`keypoint_flip_map` 等(其中颜色 RGB 取值范围 `[0, 255]`)。

---

## 【关键机制与数据】

- **原文: 注册机制**: `DatasetCatalog.register("my_dataset", my_dataset_function)` 将字符串名称与取数函数绑定;注册生命周期 = 进程生命周期;函数必须是**幂等**的(多次调用返回相同结果)。

- **原文: 数据加载流**: 用户函数返回 `list[dict]`(轻量元信息,如文件名 + 标注)→ 序列化驻留内存 → 数据加载器 (`./data_loading.md` 中详述的 `mapper`)在取样时按需加载完整样本。原文明确建议"为节省内存,不要把共享信息存到每个 sample 中,而应使用 Metadata"。

- **原文: 关键点坐标转换偏差**: COCO 关键点坐标是离散整数像素索引,detectron2 在加载时**统一加 0.5** 转换为浮点连续坐标——这是 COCO 与 detectron2 标准格式间唯一显式标注的数值偏移。

- **原文: 性能/资源考量**: "all dicts are stored in memory (sometimes serialized and with multiple copies). To save memory, each dict is meant to contain small but sufficient information"——明确数据集中每条 dict 应保持"小而足"的体积。

- **原文: 空标注过滤**: 默认情况下训练会剔除 `annotations` 为空的图像;可通过配置项 `DATALOADER.FILTER_EMPTY_ANNOTATIONS` 控制保留。

- **原文: 提案框数据约定(用于 Fast R-CNN)**: 需额外字段 `proposal_boxes`(shape `(K, 4)` 的 2D numpy 数组)、`proposal_objectness_logits`(shape `(K,)` 的 1D 数组)、`proposal_bbox_mode`(枚举,默认 `BoxMode.XYXY_ABS`);同时说明 Fast R-CNN(使用预计算 proposals)在今天"很少使用"。

- **原文: COCO 自动元数据**: 通过 `load_coco_json` 加载 COCO 格式数据集时,`thing_classes` 元数据会被自动设置。

---

## 【表格解读】

**原文无表格。**

(原文采用项目符号列表(`+`/`*`)逐条描述字段与元数据键,并未以表格形式呈现。)

---

## 【公式解读】

**原文无数学公式。**

(原文涉及的数据结构描述采用的是结构化文本与代码片段,而非 LaTeX/伪代码公式。可视为"伪代码格式的数据契约":

```
dataset_dict := {
  file_name: str,
  height: int, width: int,
  image_id: str | int,
  annotations: list[{
    bbox: list[float, float, float, float],
    bbox_mode: BoxMode.XYXY_ABS | BoxMode.XYWH_ABS,
    category_id: int ∈ [0, num_categories-1],
    segmentation?: list[list[float]] | dict,
    keypoints?: list[float],   # 长度 = 3 × keypoint_count
    iscrowd?: 0 | 1,
  }],
  sem_seg_file_name?: str,    # 灰度图, 像素值 = 类别标签
  proposal_boxes?: ndarray[K, 4],          # 仅 Fast R-CNN
  proposal_objectness_logits?: ndarray[K], # 仅 Fast R-CNN
  proposal_bbox_mode?: BoxMode,            # 默认 XYXY_ABS
}
```

其中 `bbox_mode` 枚举值含义: `XYXY_ABS` = `(x1, y1, x2, y2)` 绝对坐标,`XYWH_ABS` = `(x, y, w, h)` 绝对坐标。)

---

## 【关联】

本文档在 detectron2 生态中的上下游关系:

- **直接调用/API 关系**:
  - [`DatasetCatalog`](../modules/data.html#detectron2.data.DatasetCatalog) 与 [`MetadataCatalog`](../modules/data.html#detectron2.data.MetadataCatalog) 是本文档的两大入口 API,前者管数据取数,后者管共享元数据。
  - [`structures.BoxMode`](../modules/structures.html#detectron2.structures.BoxMode) 定义 `bbox_mode` 字段的合法值枚举(`XYXY_ABS` / `XYWH_ABS`),本指南在 `annotations.bbox_mode`、`proposal_bbox_mode` 两处均引用该枚举。
  - [`data.datasets.load_coco_json`](../modules/data.html#detectron2.data.datasets.load_coco_json) 用于加载 COCO JSON 格式,会自动设置 `thing_classes` 元数据。
  - [`data.load_proposals_into_dataset`](../modules/data.html#detectron2.data.load_proposals_into_dataset) 与 Fast R-CNN 训练所需的 `proposal_boxes` / `proposal_objectness_logits` / `proposal_bbox_mode` 字段相关。

- **上下游文档**:
  - [`builtin_datasets.md`](builtin_datasets.md): 列出了 detectron2 内置支持的数据集(用户在决定是否需要注册自定义数据集前应先查阅)。
  - [`./data_loading.md`](./data_loading.md): 文档明确指出,使用自定义数据集 dict 时,通常需要编写新的 `mapper` 来对接数据加载器,具体在 `data_loading.md` 中阐述。
  - [`../modules/evaluation.html#detectron2.evaluation.DatasetEvaluator`](../modules/evaluation.html#detectron2.evaluation.DatasetEvaluator)(内部链接中提及): 评估阶段需要 `image_id` 标识图像,这与 `annotations` 中 `category_id` 的范围约束共同构成本指南隐含的"评估可用性"前提。
  - [`../../projects/TensorMask`](../../projects/TensorMask): 文档内部链接指向 TensorMask 项目,作为自定义数据集 dict 同样适用的下游任务范例之一。

- **方法论串联**: 注册(`DatasetCatalog`) → 元数据配置(`MetadataCatalog`) → 数据加载/映射(`data_loading.md` 中的 `mapper`) → 评估(`DatasetEvaluator`) → 可视化/日志(消费 metadata) 构成完整数据流水线,本指南位于链路最上游的"注册与契约定义"环节。

---

## 【使用方法】

**注册数据集(原文示例):**
```python
def my_dataset_function():
    ...
    return list[dict]   # 标准 dict 或自定义 dict

from detectron2.data import DatasetCatalog
DatasetCatalog.register("my_dataset", my_dataset_function)

# 后续访问数据
data: List[Dict] = DatasetCatalog.get("my_dataset")
```

**注册元数据(原文示例):**
```python
from detectron2.data import MetadataCatalog
MetadataCatalog.get("my_dataset").thing_classes = ["person", "dog"]
```

**关键配置项(原文明确提到的):**
- `cfg.INPUT.MASK_FORMAT = "bitmask"`: 当 `annotations.segmentation` 采用 COCO 压缩 RLE dict 时,需设置此项以启用默认数据加载器。
- `cfg.DATALOADER.FILTER_EMPTY_ANNOTATIONS`: 控制是否在训练中剔除 `annotations` 为空的图像(默认剔除)。

**函数约束(原文约定):**
- 自定义函数必须**幂等**(多次调用返回相同数据)。
- 返回 dict 中 `bbox` 长度恒为 4,`keypoints` 长度 = 3 × 关键点类别数。
- `category_id ∈ [0, num_categories-1]`(整数),`num_categories` 保留为背景类。
- Fast R-CNN(预计算 proposals)模式下需额外提供 `proposal_boxes`(shape `(K, 4)`)、`proposal_objectness_logits`(shape `(K,)`)、`proposal_bbox_mode`(默认 `BoxMode.XYXY_ABS`),且原文指出该模式"在今天很少使用"。
