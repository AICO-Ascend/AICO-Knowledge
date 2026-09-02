# Use Custom Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/RetinaNet/docs/tutorials/datasets.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/RetinaNet/docs/tutorials/datasets.md

# 《Use Custom Datasets》文档一体化深度解读

## 【定位】
本篇文档是 detectron2 中关于"如何注册并使用自定义数据集"的总纲式 Guide,系统阐述 `DatasetCatalog` / `MetadataCatalog` 两套核心 API 的协作机制,以及标准/自定义两种数据字典格式的字段约定,目标是让用户能够把自有数据集接入 detectron2 的数据加载、训练与评估流水线。

## 【技术要点】
1. **两步接入流程**:使用自定义数据集必须完成 (1) `DatasetCatalog.register(name, fn)` 注册数据获取函数,(2) 通过 `MetadataCatalog.get(name).key = value` 注册元数据;两者缺一不可。
2. **数据获取函数的契约**:函数需返回 `list[dict]`,且"多次调用必须返回相同数据",注册在整个进程生命周期内有效。
3. **标准 Dataset Dict 的核心字段**:`file_name`、`height`、`width`、`image_id`、`annotations`(每实例一 dict,必填 `bbox` + `bbox_mode` + `category_id`)、`sem_seg_file_name`;`bbox_mode` 必须为 `BoxMode.XYXY_ABS` 或 `BoxMode.XYWH_ABS` 之一,`category_id` 取值范围 `[0, num_categories-1]`,`num_categories` 保留为"background"。
4. **关键点与分割的特殊格式**:关键点格式 `[x1, y1, v1, ..., xn, yn, vn]`,`n` 等于关键点类别数;注意 COCO 原格式是整数像素索引,detectron2 在转换时"adds 0.5 to COCO keypoint coordinates"以得到浮点坐标;`segmentation` 接受多边形列表或 COCO 压缩 RLE(`pycocotools.mask.encode(np.asarray(mask, order="F"))`),后者需设置 `cfg.INPUT.MASK_FORMAT = "bitmask"`。
5. **Fast R-CNN(预计算 proposal)扩展字段**:需要额外三个键——`proposal_boxes` (K, 4) 二维数组、`proposal_objectness_logits` (K,) 一维数组、`proposal_bbox_mode`(默认 `BoxMode.XYXY_ABS`)。
6. **关键 Metadata 键清单**:`thing_classes` / `thing_colors`(实例任务)、`stuff_classes` / `stuff_colors`(语义/全景分割)、`keypoint_names` / `keypoint_flip_map`(关键点);颜色取值 `[0, 255]`;`thing_classes` 在通过 `load_coco_json` 加载 COCO 格式数据时会被自动设置。

## 【关键机制与数据】

**工作原理(注册 → 取数 → 元数据 → 下游使用)**
- 原文:"associates a dataset named 'my_dataset' with a function that returns the data. The function must return the same data if called multiple times. The registration stays effective until the process exits."——注册本质是"名字 → 函数"绑定,生命周期为进程级,不可撤销(原文未提及注销 API)。
- 原文:"When designing a custom format, note that all dicts are stored in memory (sometimes serialized and with multiple copies). To save memory, each dict is meant to contain __small__ but sufficient information about each sample, such as file names and annotations. Loading full samples typically happens in the data loader."——即 dict 故意只放"路径+轻量标注",真正重数据在 dataloader 内按需加载,这一约束是性能/内存控制的关键设计。
- 原文:"For attributes shared among the entire dataset, use `Metadata`... do not save such information inside each sample."——元数据刻意从每样本 dict 中剥离,避免冗余。

**数据流与过滤**
- 原文:"images with empty `annotations` will by default be removed from training, but can be included using `DATALOADER.FILTER_EMPTY_ANNOTATIONS`."——空标注样本默认被训练流程剔除,需通过配置项显式保留。

**性能/数值类数据**:原文未给出基准速度、吞吐、显存等性能数字,仅给出"颜色取值 [0, 255]"、`bbox` 4 个数、`category_id` 范围等结构性参数(已在【技术要点】中列出)。

## 【表格解读】
原文无表格。

## 【公式解读】
原文无公式。

(注:原文中关于关键点坐标"Detectron2 adds 0.5 to COCO keypoint coordinates to convert them from discrete pixel indices to floating point coordinates"是一句陈述式说明,而非公式表达;多边形 `[x1, y1, ..., xn, yn]` 仅为列表格式约定,亦非数学公式。)

## 【关联】
本文处于 detectron2 数据体系的"注册层"上游,与以下模块/特性存在直接调用或对接关系(基于文末/文中提供的内部链接):

| 关联方向 | 模块/链接 | 关系性质 |
|---|---|---|
| 下游数据格式 | [`detectron2.structures.BoxMode`](../modules/structures.html#detectron2.structures.BoxMode) | `bbox_mode` 字段与 Fast R-CNN 的 `proposal_bbox_mode` 必须取值自该枚举,本 Guide 两次链接到它 |
| 数据注册核心 | [`detectron2.data.DatasetCatalog`](../modules/data.html#detectron2.data.DatasetCatalog) | 注册入口 `register / get` 的实现位置 |
| 元数据核心 | [`detectron2.data.MetadataCatalog`](../modules/data.html#detectron2.data.MetadataCatalog) | 元数据键值映射的载体,所有 `thing_classes` 等都挂在它上面 |
| 内置数据集 | [`builtin_datasets.md`](builtin_datasets.md) | 与"自定义"并列的另一条接入路径;如果数据是内置支持的,优先走 builtin |
| 数据加载 | [`./data_loading.md`](./data_loading.md) | "Custom Dataset Dicts for New Tasks"小节显式指向它,因为自定义 dict 通常需要配套自定义 mapper |
| 评估对接 | [`detectron2.evaluation.DatasetEvaluator`](../modules/evaluation.html#detectron2.evaluation.DatasetEvaluator) | `image_id` 字段"Required by evaluation to identify the images",评估依赖该字段 |
| COCO 加载便捷路径 | [`detectron2.data.datasets.load_coco_json`](../modules/data.html#detectron2.data.datasets.load_coco_json) | `thing_classes` 在 COCO 格式下会被此函数"automatically set" |
| 预计算 proposal | [`detectron2.data.load_proposals_into_dataset`](../modules/data.html#detectron2.data.load_proposals_into_dataset) | 对应文档"Fast R-CNN (with precomputed proposals) is rarely used today"一段提及的三键(`proposal_boxes` / `proposal_objectness_logits` / `proposal_bbox_mode`)的注入入口 |
| 项目示例 | [`../../projects/TensorMask`](../../projects/TensorMask) | 列在文末"Projects that use custom datasets"类链接区的下游项目之一,展示自定义任务如何消费本文约定的 dict 格式 |

## 【使用方法】

**注册数据集(最小化示例,原文给出)**
```python
def my_dataset_function():
    ...
    return list[dict]  # 见下文"标准/自定义 dict 格式"

from detectron2.data import DatasetCatalog
DatasetCatalog.register("my_dataset", my_dataset_function)
# 后续取数
data: List[Dict] = DatasetCatalog.get("my_dataset")
```

**注册元数据(原文示例)**
```python
from detectron2.data import MetadataCatalog
MetadataCatalog.get("my_dataset").thing_classes = ["person", "dog"]
```

**配置项(原文明确提及)**
- `DATALOADER.FILTER_EMPTY_ANNOTATIONS`:控制是否剔除空标注样本(默认剔除)。
- `cfg.INPUT.MASK_FORMAT = "bitmask"`:当 `segmentation` 使用 COCO 压缩 RLE(`dict` 含 `"size"` / `"counts"`)时必须设置,才能被默认 dataloader 正确处理。
- `bbox_mode` 取值:`BoxMode.XYXY_ABS` 或 `BoxMode.XYWH_ABS`(二选一)。
- `proposal_bbox_mode` 默认值:`BoxMode.XYXY_ABS`。
- `segmentation`(RLE 形式)的生成命令(原文给出):
  ```
  pycocotools.mask.encode(np.asarray(mask, order="F"))
  ```

**COCO 关键点坐标转换规则(原文给出)**:COCO 原格式坐标为 `[0, H-1 或 W-1]` 区间的整数像素索引;detectron2 在加载时会"+0.5"转换为浮点连续坐标。

**Color / Id 数值约束(原文给出)**
- 颜色(`thing_colors`、`stuff_colors`)取值范围 `[0, 255]` 的 (r, g, b) 元组;未设置时随机生成。
- `category_id` 取值 `[0, num_categories-1]`,其中 `num_categories` 保留作 background。

**辅助参考(原文提供的入口)**:[Colab tutorial](https://colab.research.google.com/drive/16jcaJoc6bCFAQ96jDe2HwtXj7BMD_-m5) 给出"register and train on a dataset of custom formats"的完整可运行示例。
