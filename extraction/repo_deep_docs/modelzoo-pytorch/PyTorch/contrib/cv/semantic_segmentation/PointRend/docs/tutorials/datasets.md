# Use Custom Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/datasets.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/datasets.md

# 「Use Custom Datasets」深度解读

## 【定位】
本文档面向需要在 detectron2 框架中使用自定义数据集（含实例检测/分割、语义/全景分割、关键点检测等任务）的开发者，系统说明了 `DatasetCatalog`/`MetadataCatalog` 这两套数据集 API 的工作机制，并给出注册新数据集与登记元数据的标准做法。

## 【技术要点】
- **两步注册流程**：第①步通过 `DatasetCatalog.register("my_dataset", my_dataset_function)` 将数据集名与一个返回 `list[dict]` 的函数绑定；第②步可选地为该数据集登记 `Metadata`（共享信息）。
- **数据契约**：`my_dataset_function` 多次调用必须返回**相同顺序、相同内容**的数据；注册在进程退出前一直生效；返回值中每个 dict 代表一张图像。
- **支持两类格式**：(1) detectron2 的标准 dataset dict（与 COCO 风格兼容，推荐）；(2) 自定义 dict（可携带新任务所需扩展键，但需配套自定义 mapper）。
- **标准字段按任务裁剪**：Common=`file_name, height, width, image_id`；Instance 检测/分割/关键点 → 加 `annotations`；语义分割 → `sem_seg_file_name`；全景分割 → `pan_seg_file_name, segments_info`。
- **`annotations` 子键规则**：`category_id` 取值范围 `[0, num_categories-1]`，其中 `num_categories` 保留给"background"；`bbox_mode` 必须是 `BoxMode.XYXY_ABS` 或 `BoxMode.XYWH_ABS`；多边形序列以 `[x1, y1, ..., xn, yn]`（n≥3）形式给出，像素绝对坐标；RLE 需通过 `pycocotools.mask.encode(np.asarray(mask, order="F"))` 转换，且默认 dataloader 使用时 `cfg.INPUT.MASK_FORMAT` 必须设为 `bitmask`。
- **关键点坐标约定**：本框架使用**浮点坐标**，而 COCO 原格式为 `[0, W-1 or H-1]` 的整数像素索引，detectron2 在加载时会给 COCO 关键点坐标加 **0.5** 完成转换；`v[i]` 表示可见性，可见性说明见 COCO 官网。
- **Fast R-CNN 扩展键**（带预计算 proposals 时使用，文档明确说明此类模型"rarely used today"）：`proposal_boxes` 形状 `(K, 4)`，`proposal_objectness_logits` 形状 `(K,)`，`proposal_bbox_mode` 默认为 `BoxMode.XYXY_ABS`。
- **空标注图像**：`annotations=[]` 的图像默认会在训练中被剔除，可通过 `DATALOADER.FILTER_EMPTY_ANNOTATIONS` 配置保留。
- **内存与设计原则**：每个 dict 应只保存"小但充分"的样本信息（路径+标注），不要把共享的 dataset 级属性塞进每条样本——这类共享信息应通过 `Metadata` 提供。

## 【关键机制与数据】
- **数据流（注册 → 访问 → 使用）**：用户实现 `my_dataset_function()`，通过 `DatasetCatalog.register("my_dataset", my_dataset_function)` 注册；下游通过 `DatasetCatalog.get("my_dataset")` 取回 `List[Dict]`；dataloader 在取数据时按 dict 中字段解释图像与标注。
- **Standard dict 加载机制**：detectron2 按 COCO 风格的注解规范将原始数据集加载为 `list[dict]`，作为该框架的"标准表示"；其作用是让一个 dict 能直接驱动多个内置功能（数据增强、评估、可视化、训练循环）。
- **全景分割的颜色/标签机制**：`pan_seg_file_name` 必须为 RGB 图，像素值是整数 id，编码方式见 `panopticapi.utils.id2rgb`；id 的语义由 `segments_info` 给出；若某 id 不在 `segments_info` 中，该像素视为 unlabeled，在训练和评估时通常被忽略。
- **自定义扩展机制**：dict 中可放入任意自定义键以适配新任务，但需要为 dataloader 编写自定义 `mapper`（参见 `./data_loading.md`）。
- **特殊示例**：文档附注指出 `PanopticFPN` 实际并不使用上述"全景分割"格式，而是把"实例分割"与"语义分割"两种数据格式组合使用（参见 `builtin_datasets.md` 中关于 COCO 的说明）。
- **性能数据**：原文未涉及任何具体指标、基准测试结果或吞吐数据。

## 【表格解读】

原文包含 1 张 list-table（标准 dict 字段与任务的对应关系），逐字还原如下：

| Task | Fields |
| --- | --- |
| Common | file_name, height, width, image_id |
| Instance detection/segmentation | annotations |
| Semantic segmentation | sem_seg_file_name |
| Panoptic segmentation | pan_seg_file_name, segments_info |

逐行解读：
- **Common** —— 任何标准任务都必须提供的公共字段：`file_name`（图像文件的完整路径）、`height`/`width`（整数，图像尺寸）、`image_id`（str 或 int，唯一标识一张图，许多 evaluator 需要据此识别图像）。
- **Instance detection/segmentation** —— 任务级字段为 `annotations`（list[dict]），对应图像中每个实例的标注集合，是实例检测/实例分割/关键点检测的载体。
- **Semantic segmentation** —— 任务级字段为 `sem_seg_file_name`（str），语义分割真值文件的完整路径，文件为灰度图，像素值即整数类别标签。
- **Panoptic segmentation** —— 任务级字段为 `pan_seg_file_name`（RGB 路径，像素为整数 id）+ `segments_info`（list[dict]，定义每个 id 的语义）；不在 `segments_info` 中的 id 视为 unlabeled。

## 【公式解读】

原文无公式。

（文档中的 `[x1, y1, ..., xn, yn]`、`[x1, y1, v1, ..., xn, yn, vn]`、`(K, 4)`、`(K,)`、`[0, num_categories-1]`、`+0.5` 偏移量等均为字面量记法/取值范围/形状描述，非独立公式表达式，未按公式体例呈现，因此本节按要求标注为"原文无公式"。）

## 【关联】
- **数据集与元数据 API**：`DatasetCatalog`、`MetadataCatalog` 是注册与查询数据集/共享属性的入口，文档围绕两者展开。
- **标准数据格式支撑模块**：`structures.BoxMode` 定义 bbox 模式枚举（`XYXY_ABS`、`XYWH_ABS`），`annotations.bbox_mode`、`Fast R-CNN` 的 `proposal_bbox_mode` 都依赖它。
- **数据集加载工具**：`detectron2.data.datasets.load_coco_json`、`detectron2.data.load_proposals_into_dataset` 用于把 COCO 注解、预计算 proposals 装入 dataset dict；`detectron2.evaluation.DatasetEvaluator` 依赖 `image_id` 等字段识别样本。
- **Dataloader / Mapper**：自定义 dict 需配合自定义 mapper，详见 `./data_loading.md`。
- **内置数据集列表**：哪些数据集被 detectron2 原生支持参见 `builtin_datasets.md`（含 COCO 全景格式、PanopticFPN 的特殊处理说明）。
- **典型任务示例**：以 `TensorMask`（`../../projects/TensorMask`）为代表的实例分割项目，会直接消费上文定义的 `annotations`/`bbox`/`bbox_mode`/`segmentation` 等字段。
- **Colab 教程**：文档给出 [Colab tutorial](https://colab.research.google.com/drive/16jcaJoc6bCFAQ96jDe2HwtXj7BMD_-m5) 链接，作为"如何注册并训练自定义格式数据集"的活示例。

## 【使用方法】
- **注册数据集**（Python）：
  ```python
  from detectron2.data import DatasetCatalog

  def my_dataset_function():
      ...
      return list[dict]   # 按"Standard Dataset Dicts"或自定义格式返回

  DatasetCatalog.register("my_dataset", my_dataset_function)
  # 后续访问：
  data: List[Dict] = DatasetCatalog.get("my_dataset")
  ```
- **常见可配置项**：
  - `cfg.INPUT.MASK_FORMAT = "bitmask"`：当 `annotations.segmentation` 使用 COCO 压缩 RLE `dict` 时，默认 dataloader 要求此设置。
  - `DATALOADER.FILTER_EMPTY_ANNOTATIONS`：控制是否剔除 `annotations=[]` 的空标注图像。
- **Fast R-CNN（带预计算 proposals）训练**：在每条样本 dict 中提供 `proposal_boxes`（形状 `(K, 4)`）、`proposal_objectness_logits`（形状 `(K,)`）、`proposal_bbox_mode`（`BoxMode` 成员，默认 `BoxMode.XYXY_ABS`）。
- **元数据使用**：通过 `MetadataCatalog.get(dataset_name).some_metadata` 读取/写入；`Metadata` 的具体字段（如类别名、类别颜色、文件根目录等）取决于下游代码需要，原文未给出完整字段清单（文档在"If you register a new dataset through `DatasetCatalog.register`, you may also"处截断，未涉及更多元数据 API 的具体使用步骤）。
- **注意事项**（原文给出的隐式约束）：
  - `my_dataset_function` 必须幂等（多次调用结果一致）。
  - 注册在进程退出前持续生效。
  - 每个 dict 应只放小而充分的信息；跨样本共享信息走 `Metadata`。
  - COCO 关键点坐标与 detectron2 内部浮点坐标存在 `+0.5` 的转换差异。

> 文档原文以"If you register a new dataset through `DatasetCatalog.register`, you may also"截断，元数据（Metadata）一节的剩余 API 用法在原文中并未完整给出；本节其余内容均严格基于原文已出现的字段、命令与配置项。
