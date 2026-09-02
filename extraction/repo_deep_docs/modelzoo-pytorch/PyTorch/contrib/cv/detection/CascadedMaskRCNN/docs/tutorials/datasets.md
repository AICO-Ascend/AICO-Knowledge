# Use Custom Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/tutorials/datasets.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/tutorials/datasets.md

# 一体化深度解读：detectron2 Custom Datasets 指南

---

## 【定位】

本文档系统讲解 detectron2 数据集 API（`DatasetCatalog`、`MetadataCatalog`）的工作原理，并说明如何注册自定义数据集、配置标准数据字典字段以及挂载元数据，使 detectron2 的内置数据加载器与下游训练/评估流程能够直接复用。

---

## 【技术要点】

1. **数据集注册两阶段流程**：使用 detectron2 自定义数据集必须 (1) **注册**——通过 `DatasetCatalog.register("my_dataset", my_dataset_function)` 将数据集名称与返回 `list[dict]` 的函数绑定；(2) **可选注册元数据**——通过 `MetadataCatalog.get("my_dataset").some_key = some_value` 补充数据集级共享信息（如 `thing_classes`）。

2. **数据函数不变量要求**：注册函数在多次调用时必须返回相同的数据；注册在进程退出前持续有效；函数可执行任意逻辑，但必须返回 `list[dict]`，每个 dict 对应一张图像。

3. **标准数据字典必备与可选字段**：`file_name`、`height`、`width`、`image_id`、`annotations`（可为空 list，空标注图默认从训练中移除，可通过 `DATALOADER.FILTER_EMPTY_ANNOTATIONS` 保留）；`annotations` 中每个实例 dict 至少包含 `bbox`（4 个 float）、`bbox_mode`（必须是 `BoxMode` 成员，目前支持 `BoxMode.XYXY_ABS`、`BoxMode.XYWH_ABS`）、`category_id`（取值范围 `[0, num_categories-1]`，`num_categories` 保留为"背景"类）。

4. **bbox 模式与语义分割标注**：`bbox_mode` 必须是 `structures.BoxMode` 成员；`segmentation` 支持两种格式——`list[list[float]]` 多边形（每条多边形 `[x1, y1, ..., xn, yn]`，坐标为像素绝对值）或 dict（包含 `"size"` 与 `"counts"`，即 COCO 压缩 RLE 格式，可用 `pycocotools.mask.encode(np.asarray(mask, order="F"))` 转换）；当使用 RLE 时须将 `cfg.INPUT.MASK_FORMAT` 设为 `bitmask`。

5. **关键点标注格式差异**：`keypoints` 字段为 `[x1, y1, v1, ..., xn, yn, vn]`，其中 `n` 等于关键点类别数；可见性 `v[i]` 来源于 [COCO format](http://cocodataset.org/#format-data)；COCO 格式的关键点坐标是 `[0, H-1 或 W-1]` 范围内的整数，detectron2 会在转换时加 0.5 变为浮点坐标。

6. **Fast R-CNN 预计算 proposals 专用字段**：当训练带预计算 proposals 的 Fast R-CNN 时，需要额外三个键——`proposal_boxes`（形状 `(K, 4)` 的 2D numpy 数组）、`proposal_objectness_logits`（形状 `(K,)` 的 numpy 数组）、`proposal_bbox_mode`（默认 `BoxMode.XYXY_ABS`）。

---

## 【关键机制与数据】

### 数据流与工作机制

- **注册-检索机制**：`DatasetCatalog.register(name, func)` 将字符串名称与数据生产函数绑定；后续通过 `DatasetCatalog.get(name)` 获取完整 `List[Dict]`。原文："Here, the snippet associates a dataset named 'my_dataset' with a function that returns the data. The function must return the same data if called multiple times. The registration stays effective until the process exits."

- **标准字典与扩展性**：detectron2 把数据集读入为 `list[dict]`，每个 dict 对应一张图像，且"dict may have the following fields, and the required fields vary based on what the dataloader or the task needs"。如果用户需要支持标准任务之外的新任务，可使用**自定义字段**，但下游 mapper 必须能正确处理（参见 `data_loading.md`）。

- **元数据（Metadata）的作用域**：`Metadata` 是 key-value 映射，承载整个数据集共享信息（类别名、类别颜色、文件根目录等），用于增强、评估、可视化、日志；原文："Metadata is a key-value mapping that contains information that's shared among the entire dataset, and usually is used to interpret what's in the dataset."

- **内存优化提示**：每个 dict 故意只保存**小而足**的信息（如文件名与标注），完整样本的读取由 data loader 完成；共享属性应放在 `Metadata` 而非每个 sample 中，原文："To avoid extra memory, do not save such information inside each sample."

- **crowd 区域标注**：`iscrowd` 字段取值 0（默认）或 1；若不确定含义，**不要**包含此字段。

---

## 【表格解读】

**原文无表格**。原文未给出任何 markdown 形式的参数表、性能对比表或配置项表格，仅以列表（`+` 与 `*` 项目符号）方式罗列字段与元数据键。

---

## 【公式解读】

**原文无公式**。文档以代码片段（注册函数、字段描述）为主，未出现数学公式或 LaTeX 伪代码表达式。唯一的"准公式"形式为 bbox 多边形与关键点的向量表示 `[x1, y1, ..., xn, yn]` 以及 `[x1, y1, v1, ..., xn, yn, vn]`，它们是数据结构描述而非数学公式。

---

## 【关联】

本文档位于 detectron2 数据集使用链路的上游配置层，与以下模块/文档形成紧密依赖关系：

- **核心 API 引用**
  - [`DatasetCatalog`](../modules/data.html#detectron2.data.DatasetCatalog)：数据集注册表，提供 `register`/`get` 接口。
  - [`MetadataCatalog`](../modules/data.html#detectron2.data.MetadataCatalog)：元数据注册表，提供 `get(name).key = value` 访问模式。
  - [`BoxMode`](../modules/structures.html#detectron2.structures.BoxMode)（出现两次引用）：定义 `bbox_mode` 取值，当前内置 `BoxMode.XYXY_ABS` 与 `BoxMode.XYWH_ABS`。

- **内置数据集与加载器**
  - [builtin_datasets.md](builtin_datasets.md)：列出了 detectron2 原生支持的数据集，作为"自定义数据集"的对照基准。
  - [`load_coco_json`](../modules/data.html#detectron2.data.datasets.load_coco_json)：当加载 COCO 格式数据集时，会**自动**设置 `thing_classes` 元数据（原文："If you load a COCO format dataset, it will be automatically set by the function `load_coco_json`."）。
  - [`load_proposals_into_dataset`](../modules/data.html#detectron2.data.load_proposals_into_dataset)：与 Fast R-CNN 预计算 proposals 流程相关（文档链接中提及）。

- **下游加载与评估**
  - [./data_loading.md](./data_loading.md)：当自定义 dict 引入新任务字段时，需要编写新的 mapper 配合 dataloader（原文："Usually this requires writing a new `mapper` for the dataloader (see [Use Custom Dataloaders](./data_loading.md))."）。
  - [`DatasetEvaluator`](../modules/evaluation.html#detectron2.evaluation.DatasetEvaluator)：评估阶段需要通过 `image_id` 标识图像，因此 `image_id` 在标准字典中是必备字段。

- **示例项目**
  - [../../projects/TensorMask]：作为使用自定义数据流的项目案例（出现在链接列表中），可作为复杂任务的参考实现。

- **配套教程**
  - [Colab tutorial](https://colab.research.google.com/drive/16jcaJoc6bCFAQ96jDe2HwtXj7BMD_-m5)：活生生的注册与训练示例，覆盖本文档的所有要点。

---

## 【使用方法】

### 启用自定义数据集的最小步骤

1. **实现数据加载函数**：编写返回 `list[dict]` 的 Python 函数，每个 dict 对应一张图像并包含所需字段。

2. **注册数据集**：
   ```python
   from detectron2.data import DatasetCatalog
   DatasetCatalog.register("my_dataset", my_dataset_function)
   data: List[Dict] = DatasetCatalog.get("my_dataset")
   ```

3. **（可选）注册元数据**：
   ```python
   from detectron2.data import MetadataCatalog
   MetadataCatalog.get("my_dataset").thing_classes = ["person", "dog"]
   ```

### 标准任务的关键配置项（原文涉及）

- **空标注图过滤**：`DATALOADER.FILTER_EMPTY_ANNOTATIONS`（默认会移除 `annotations` 为空的图像；设为 False 可保留）。
- **mask 格式**：`cfg.INPUT.MASK_FORMAT` 在使用 COCO RLE dict 形式的 `segmentation` 时必须设为 `bitmask`。
- **bbox 格式**：`bbox_mode` 必须是 `BoxMode` 枚举成员，目前支持 `BoxMode.XYXY_ABS`、`BoxMode.XYWH_ABS`；Fast R-CNN 的 `proposal_bbox_mode` 默认 `BoxMode.XYXY_ABS`。
- **category_id 取值范围**：`[0, num_categories-1]`，其中 `num_categories` 保留为"背景"类。

### 常用元数据键（原文列出）

- `thing_classes`（`list[str]`）：实例检测/分割任务所需，COCO 格式数据集由 `load_coco_json` 自动设置。
- `thing_colors`（`list[tuple(r, g, b)]`，取值 `[0, 255]`）：实例类别的可视化颜色；缺省时随机生成。
- `stuff_classes`（`list[str]`）：语义/全景分割的 stuff 类别名。
- `stuff_colors`（`list[tuple(r, g, b)]`，取值 `[0, 255]`）：stuff 类别的可视化颜色；缺省时随机生成。
- `keypoint_names`（`list[str]`）：关键点名称列表。
- `keypoint_flip_map`（`list[tuple[str]]`）：关键点水平翻转映射（原文该条目在截断处戛然而止，后续细节未在原文中给出）。

### 自定义新任务的提示

原文："When designing a custom format, note that all dicts are stored in memory (sometimes serialized and with multiple copies). To save memory, each dict is meant to contain **small** but sufficient information about each sample, such as file names and annotations."——即每个 sample 字典应保持精简，完整样本由 data loader 按需加载。
