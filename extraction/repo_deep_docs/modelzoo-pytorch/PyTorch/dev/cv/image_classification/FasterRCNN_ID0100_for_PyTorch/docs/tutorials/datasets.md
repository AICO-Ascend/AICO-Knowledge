# Use Custom Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/FasterRCNN_ID0100_for_PyTorch/docs/tutorials/datasets.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/FasterRCNN_ID0100_for_PyTorch/docs/tutorials/datasets.md

# 深度解读:detectron2 自定义数据集注册指南

## 【定位】

本篇文档阐释 detectron2 中 **`DatasetCatalog` / `MetadataCatalog`** 两套数据集 API 的工作机制,并系统说明如何**注册自定义数据集**(自定义数据加载函数 + 自定义标注格式 + 全局元数据),从而复用 detectron2 内置的 dataloader、评估、可视化等下游能力。

---

## 【技术要点】

1. **注册机制**:通过 `DatasetCatalog.register("my_dataset", my_dataset_function)` 把名字与返回 `list[dict]` 的函数绑定;后续通过 `DatasetCatalog.get("my_dataset")` 取得数据。**注册在进程退出前一直有效**,且要求函数**多次调用结果一致**。

2. **标准数据集 dict 字段**(每个 dict 对应一张图像):`file_name`、`height`、`width`、`image_id`(str 或 int,评估用来标识图像)、`annotations`(实例级标注 list[dict])、`sem_seg_file_name`(语义分割灰度标签图路径)。`annotations` 可为空,但默认会被从训练中过滤掉——可用 `DATALOADER.FILTER_EMPTY_ANNOTATIONS` 配置保留。

3. **标注子字段**(每条 `annotations[i]`):必须包含 `bbox`(`list[float]`,4 个数)、`bbox_mode`(必须是 `structures.BoxMode` 成员,目前支持 `BoxMode.XYXY_ABS`、`BoxMode.XYWH_ABS`)、`category_id`(int,范围 `[0, num_categories-1]`,其中 `num_categories` 被保留表示"背景")。可选字段包括 `segmentation`、`keypoints`、`iscrowd`。

4. **分割 mask 两种合法形式**:① `list[list[float]]` —— 多边形列表,每个 `list[float]` 为一条连通分量的 `[x1, y1, …, xn, yn]`,**绝对像素坐标**;② `dict` —— COCO 压缩 RLE,含 `size` 与 `counts` 键;可用 `pycocotools.mask.encode(np.asarray(mask, order="F"))` 把 0/1 uint8 mask 转成 RLE dict,此时 `cfg.INPUT.MASK_FORMAT` 必须设为 `bitmask`。

5. **关键点格式**:`[x1, y1, v1, …, xn, yn, vn]`,`n` 等于关键点类别数;`v[i]` 是 visibility 标志;坐标为绝对像素。**注意:COCO 原格式关键点坐标是 `[0, H-1]` 或 `[0, W-1]` 的整数,detectron2 自动加 0.5 转为浮点连续坐标**。

6. **Fast R-CNN 预计算 proposal 专用字段**:`proposal_boxes`(numpy 2D,shape `(K, 4)`)、`proposal_objectness_logits`(numpy,shape `(K,)`)、`proposal_bbox_mode`(默认 `BoxMode.XYXY_ABS`)。文档明确指出这种用法"今天已很少用"。

7. **Metadata 机制**:`MetadataCatalog.get(dataset_name).<key> = <value>` 配置整个数据集的共享信息(类名、颜色、文件根目录等),供增强、评估、可视化、日志共用;**避免把样本级共享信息塞进每条样本 dict**。内置会消费的关键 key 包括 `thing_classes`、`thing_colors`、`stuff_classes`、`stuff_colors`、`keypoint_names`、`keypoint_flip_map`(原文 `keypoint_flip_map` 描述被截断)。

---

## 【关键机制与数据】

- **原文**:注册函数"必须返回相同的数据如果被多次调用"——保证 `DatasetCatalog.get()` 重复拉取时一致;典型做法是内部固定地从磁盘解析,不引入随机性。
- **原文**:数据集 dict 在内存中持有(有时会被序列化并产生多份副本);故文档**强调每个 dict 应只放"小而充分"的信息**(文件名、标注),**不要把完整样本(图像、mask 大数组)塞进 list[dict]**,完整加载留给 dataloader。这是为了控制内存占用。
- **原文**:`cfg.INPUT.MASK_FORMAT = "bitmask"` 是使用 COCO RLE 标注 + 默认 dataloader 时的**必要配置**。
- **原文**:`DATALOADER.FILTER_EMPTY_ANNOTATIONS` 控制是否丢弃 `annotations=[]` 的图像(默认丢弃)。
- **原文**:`load_coco_json` 函数**会自动设置** `thing_classes` 这一 metadata。
- **原文**:EXIF 元数据存在时,`file_name` 指向的图像**在加载时会自动按 EXIF 信息做旋转/翻转**。
- **原文**:关键点 COCO→detectron2 坐标转换:"Detectron2 adds 0.5 to COCO keypoint coordinates to convert them from discrete pixel indices to floating point coordinates."
- **数据流简述**:用户函数 → `DatasetCatalog` 注册表 → 训练时 dataloader 按需加载完整样本 → 配合 `MetadataCatalog` 完成增广/可视化/评估。
- **性能/数字**:原文**未提供**任何基准性能数字或吞吐量数据。

---

## 【表格解读】

**原文无表格。** 文档主要以项目符号列表(标注子字段、metadata 键清单)与代码片段方式描述字段定义,未出现 markdown/html 表格。

---

## 【公式解读】

**原文无显式数学公式。** 但文档以伪代码/格式约定描述了几类数据结构约定,逐字保留并解释如下:

- **多边形坐标序列**(原文:`[x1, y1, ..., xn, yn]`)
  - 符号:`x_i, y_i` = 第 `i` 个顶点的横、纵坐标(单位:像素,**绝对值**)。
  - 作用:表示一条简单多边形;`segmentation` 为 `list[list[float]]` 时,每个内层 list 是这样一条多边形,外层 list 对应一个实例的全部连通分量。

- **关键点坐标序列**(原文:`[x1, y1, v1,..., xn, yn, vn]`)
  - 符号:`x_i, y_i` = 第 `i` 个关键点的绝对像素坐标;`v_i` = visibility 标志(参考 COCO 格式);`n` = 关键点类别数。
  - 作用:detectron2 标准的关键点标注数组格式;**注意 `v` 与坐标成对出现,不可拆开**。

- **COCO→detectron2 关键点偏移**(原文自然语言描述,无 LaTeX,但可形式化为 `x_det = x_coco + 0.5`)
  - 符号:`x_coco` ∈ {0, …, W−1},`x_det` 为 detectron2 内的浮点坐标。
  - 作用:把整数像素索引对齐到"像素中心"浮点坐标。

- **Fast R-CNN proposal 张量形状**(原文:`(K, 4)` / `(K, )`)
  - 符号:`K` = 该图像的预计算 proposal 数;每条 proposal 用 4 个数表示一个 bbox。
  - 作用:`proposal_boxes` 用 `(K, 4)` 张量承载候选框,`proposal_objectness_logits` 用 `(K,)` 承载对应的 objectness 分数。

---

## 【关联】

依据文末给出的内部链接清单,本文档与其他模块/文档的耦合关系如下:

| 关联对象 | 关系类型 | 在本文中的角色 |
|---|---|---|
| `../modules/data.html#detectron2.data.DatasetCatalog` | 核心 API | 注册与查询数据集函数 |
| `../modules/data.html#detectron2.data.MetadataCatalog` | 核心 API | 存储数据集级共享元数据 |
| `builtin_datasets.md` | 上游/平行文档 | 列出 detectron2 已原生支持的数据集,本文是其补充(自定义路径) |
| `../modules/structures.html#detectron2.structures.BoxMode`(两处) | 配套类型 | `bbox_mode` 字段必须是该枚举成员,目前仅支持 `XYXY_ABS`、`XYWH_ABS` |
| `./data_loading.md` | 下游文档 | 自定义 dataset dict 时**需配套写新的 mapper**,由 dataloader 处理 |
| `../modules/evaluation.html#detectron2.evaluation.DatasetEvaluator` | 下游消费方 | 评估阶段会读 `image_id`、annotation 等;与本文 dataset dict 字段约定直接耦合 |
| `../modules/data.html#detectron2.data.datasets.load_coco_json` | 配套工具 | 自动从 COCO json 灌入数据集并**自动设置 `thing_classes`** metadata |
| `../modules/data.html#detectron2.data.load_proposals_into_dataset` | 配套工具 | 与 Fast R-CNN 预计算 proposal 字段(`proposal_boxes` / `proposal_objectness_logits`)协同 |
| `../../projects/TensorMask` | 项目示例 | 作为"新建任务/自定义 mapper"路径下的下游消费示例,体现本文约定的扩展能力 |

---

## 【使用方法】

### 启用方式(注册数据集)

```python
def my_dataset_function():
    ...
    return list[dict]   # 按"标准 dict"或自定义 dict 格式

from detectron2.data import DatasetCatalog
DatasetCatalog.register("my_dataset", my_dataset_function)

# 访问
data: List[Dict] = DatasetCatalog.get("my_dataset")
```

### 注册元数据

```python
from detectron2.data import MetadataCatalog
MetadataCatalog.get("my_dataset").thing_classes = ["person", "dog"]
```

### 关键配置项

- `DATALOADER.FILTER_EMPTY_ANNOTATIONS` —— 是否过滤掉 `annotations=[]` 的图像(默认过滤)。
- `cfg.INPUT.MASK_FORMAT = "bitmask"` —— 当 `segmentation` 用 COCO RLE dict 时,**必须**设为 `bitmask` 才能与默认 dataloader 协作。

### RLE mask 转换(原文命令)

```python
pycocotools.mask.encode(np.asarray(mask, order="F"))
```

### 与 COCO 协同

- 直接调用 `load_coco_json` 会自动填充数据集 dict 并设置 `thing_classes` metadata;若用 Fast R-CNN 预计算 proposal,可结合 `load_proposals_into_dataset` 把 `proposal_boxes` / `proposal_objectness_logits` 字段并入数据集。

### 新增任务 / 自定义字段

- 在 dict 中加自定义 key,但**必须配套为 dataloader 写新的 mapper**(见 `data_loading.md`);**避免在每条样本 dict 中存放大数组/共享数据**,共享信息一律放到 `Metadata`。

> 说明:原文在 `keypoint_flip_map` 元数据键的描述处被截断(以 *"Used by ke"* 结束),后续 metadata 清单、其他可能的字段说明均不在已提供文本范围内,本解读未作任何外推。
