# Use Custom Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/Cascade_RCNN/docs/tutorials/datasets.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/Cascade_RCNN/docs/tutorials/datasets.md

# 一体化深度解读:Cascade_RCNN / docs/tutorials/datasets.md

## 【定位】
本文档是 detectron2(被 Cascade_RCNN 项目所基于的检测框架)中"自定义数据集"的接入指南,阐述如何通过 `DatasetCatalog` 与 `MetadataCatalog` 两套注册机制,让任何格式的数据集复用 detectron2 的 dataloader、评估器、可视化与训练流程。

---

## 【技术要点】

1. **两步接入流程**:注册数据集函数(`DatasetCatalog.register`)→ 可选地注册元数据(`MetadataCatalog.get(name).key = value`),注册在进程退出前一直有效。
2. **数据集函数要求**:必须返回一个 `list[dict]`,且多次调用应返回**相同**数据;每条 dict 对应一张图像,字段按需填写。
3. **标准 dataset dict 必备/可选字段**:`file_name`、`height/width`、`image_id`、`annotations`;实例/关键点任务需要 `annotations`,其下 `bbox`、`bbox_mode`、`category_id` 为必需,`segmentation`、`keypoints`、`iscrowd` 为可选。
4. **bbox 格式枚举**:必须是 `structures.BoxMode` 的成员,当前支持 `BoxMode.XYXY_ABS` 与 `BoxMode.XYWH_ABS`(坐标均为绝对像素)。
5. **segmentation 两种表达**:`list[list[float]]` 的多边形(每条 `[x1,y1,...,xn,yn]`,绝对像素),或 COCO 压缩 RLE dict(`{"size","counts"}`),后者需设置 `cfg.INPUT.MASK_FORMAT = "bitmask"`。
6. **关键点坐标转换**:COCO 整数索引 → detectron2 浮点坐标的转换公式为 **detectron2 坐标 = COCO 坐标 + 0.5**(用于把离散像素索引变为浮点像素坐标)。
7. **空标注过滤**:默认训练会剔除 `annotations` 为空的图像;可通过配置 `DATALOADER.FILTER_EMPTY_ANNOTATIONS` 改变行为。
8. **Fast R-CNN 预计算 proposal 字段**:`proposal_boxes`(shape `(K,4)`)、`proposal_objectness_logits`(shape `(K,)`)、`proposal_bbox_mode`(默认 `BoxMode.XYXY_ABS`)。
9. **自定义 task 字段**:dict 内允许放任意自定义键,但需自行配套 mapper;**全图共享信息应放入 Metadata**,不要塞进每条样本里以节约内存。
10. **Metadata 内置键族**:`thing_classes/thing_colors`、`stuff_classes/stuff_colors`、`keypoint_names/keypoint_flip_map` 等(原文列表在末尾被截断)。

---

## 【关键机制与数据】

### 工作原理 / 数据流

1. **注册侧**:`DatasetCatalog.register("my_dataset", my_dataset_function)` 把"名字"与"返回 `list[dict]` 的函数"绑定。下游通过 `DatasetCatalog.get("my_dataset")` 取数据。
   - 原文:"The registration stays effective until the process exits."
2. **数据契约**:函数必须可重复调用得到相同结果;返回的 dict 可遵循 detectron2 标准格式,也可完全自定义(但需要配套下游处理)。
   - 原文:"The function can do arbitrary things and should returns the data in either of the following formats: 1. Detectron2's standard dataset dict ... 2. Any custom format."
3. **类别 id 范围**:`category_id ∈ [0, num_categories-1]`;`num_categories` 被保留为"background"。
   - 原文:"an integer in the range [0, num_categories-1] representing the category label. The value num_categories is reserved to represent the 'background' category, if applicable."
4. **关键点格式**:`[x1, y1, v1, …, xn, yn, vn]`,`n` 等于关键点类别数;`v[i]` 为可见性标志;`xs/ys` 为绝对像素浮点。
   - 原文:"list[float]): in the format of [x1, y1, v1,..., xn, yn, vn]."
5. **多边形 segmentation**:`list[list[float]]`,每个内层 list 表示一个连通分量的简单多边形,点对为绝对像素。
6. **RLE segmentation**:由 `pycocotools.mask.encode(np.asarray(mask, order="F"))` 得到;使用默认 dataloader 时 `cfg.INPUT.MASK_FORMAT` 必须设为 `bitmask`。
7. **iscrowd**:`0`(默认)或 `1`,语义对齐 COCO "crowd region";不清楚时**不要**包含该字段。
   - 原文:"Don't include this field if you don't know what it means."
8. **语义分割字段**:`sem_seg_file_name`(灰度图,像素值为整数类别标签)。
9. **Fast R-CNN 预计算 proposal 三件套**:`proposal_boxes` `(K,4)`、`proposal_objectness_logits` `(K,)`、`proposal_bbox_mode`(默认 `XYXY_ABS`)。
   - 原文明确说明:"Fast R-CNN (with precomputed proposals) is rarely used today."
10. **内存管理**:每个 dict 只保存"小但足够"的信息(路径、标注),**完整加载**在 dataloader 中发生;共享属性走 Metadata。
    - 原文:"each dict is meant to contain small but sufficient information about each sample, such as file names and annotations. Loading full samples typically happens in the data loader."

### 性能 / 数值类数据(原文给出)

- 关键点 COCO→detectron2 转换:**+0.5 偏移**(整数 → 浮点)。
  - 原文:"Detectron2 adds 0.5 to COCO keypoint coordinates to convert them from discrete pixel indices to floating point coordinates."
- RLE 转换命令:`pycocotools.mask.encode(np.asarray(mask, order="F"))`(Fortran 顺序)。
- 颜色范围:Metadata 中的颜色 tuple 取值在 `[0, 255]`。
  - 原文:"Pre-defined color (in [0, 255]) for each thing category."
- bbox 坐标:绝对像素单位,无归一化。
- 关键点类别数 = 内层点数 / 3。

> 注:原文未给出任何 benchmark、时延、精度等性能数据。

---

## 【表格解读】

**原文无表格**。原文使用项目符号列表罗列 `Standard Dataset Dicts` 字段与 `Metadata` 内置键,未使用任何 markdown 表格结构。为便于检索,将 Metadata 内置键(原文以 `*` 列表给出,**逐字摘录**)整理为表格并逐行解读:

| Metadata 键 | 类型 | 含义 | 缺失影响 |
|---|---|---|---|
| `thing_classes` | `list[str]` | 实例/thing 类别名列表;若用 `load_coco_json` 加载 COCO 数据集会**自动**填入 | 所有实例检测/分割功能不可用 |
| `thing_colors` | `list[tuple(r,g,b)]` | 每个 thing 类的预定义颜色,值域 `[0, 255]` | 可视化时退化为**随机颜色** |
| `stuff_classes` | `list[str]` | 语义/全景分割中的 stuff 类别名 | 语义/全景分割功能不可用 |
| `stuff_colors` | `list[tuple(r,g,b)]` | 每个 stuff 类的预定义颜色,值域 `[0, 255]` | 可视化时退化为**随机颜色** |
| `keypoint_names` | `list[str]` | 关键点名称列表 | 关键点检测功能不可用 |
| `keypoint_flip_map` | `list[tuple[str]]` | 关键点水平翻转配对 | 原文此处被截断,后续字段未给出 |

逐行解读:
- `thing_classes` 是**实例任务**最关键的元数据,原文明确:如果用 COCO 格式数据集,`load_coco_json` 会自动填充。
- `thing_colors` / `stuff_colors` 只影响**可视化**,缺失会随机分配颜色,不影响训练/评估。
- `stuff_classes` 仅在语义分割、全景分割任务中被读取。
- `keypoint_names` 与 `keypoint_flip_map`(原文末尾被截断)用于关键点检测与水平镜像增强。
- 原文明确警告:不提供这些键可能导致部分 builtin 功能不可用——这是**契约式**的,而不是抛错。

---

## 【公式解读】

**原文无公式**(无 LaTeX、无伪代码公式)。但原文含两条**坐标/编码转换的"准公式"**,以文字形式给出,在此逐字保留并解释:

### 准公式 1:关键点坐标转换

$$
x_{\text{detectron2}} = x_{\text{COCO}} + 0.5,\quad
y_{\text{detectron2}} = y_{\text{COCO}} + 0.5
$$

- 符号含义:
  - $x_{\text{COCO}}, y_{\text{COCO}}$:COCO 原始关键点坐标,**整数**,取值范围 `[0, H-1]` 或 `[0, W-1]`,语义为"像素索引"。
  - $x_{\text{detectron2}}, y_{\text{detectron2}}$:detectron2 标准关键点坐标,**浮点**,语义为"像素中心坐标"。
- 作用:把离散像素索引转为浮点像素中心坐标,与 detectron2 内部所有 bbox、mask 的浮点像素中心约定一致。
- 来源:原文 "Detectron2 adds 0.5 to COCO keypoint coordinates to convert them from discrete pixel indices to floating point coordinates."

### 准公式 2:RLE 编码(命令式)

$$
\text{rle\_dict} = \texttt{pycocotools.mask.encode}(\texttt{np.asarray(mask, order="F")})
$$

- 符号含义:
  - `mask`:`uint8` 0/1 分割掩码,`H × W`。
  - `order="F"`:按 **Fortran(列优先)** 顺序序列化,这是 `pycocotools` 的硬性要求。
  - `rle_dict`:包含 `"size"` 与 `"counts"` 两键的 COCO 压缩 RLE 表示。
- 作用:把二维 0/1 矩阵压缩为 COCO 通用 RLE,使 detectron2 能与 COCO 评估生态互通。
- 配套配置:使用默认 dataloader 时需设置 `cfg.INPUT.MASK_FORMAT = "bitmask"`。

### 准公式 3:bbox 枚举

$$
\text{bbox\_mode} \in \{\texttt{BoxMode.XYXY\_ABS},\ \texttt{BoxMode.XYWH\_ABS}\}
$$

- 符号含义:
  - `XYXY_ABS`:左上角 `(x1, y1)` + 右下角 `(x2, y2)`,绝对像素。
  - `XYWH_ABS`:左上角 `(x, y)` + 宽高 `(w, h)`,绝对像素。
- 作用:为检测框提供显式坐标系,避免不同数据集默认 `(x,y,w,h)` / `(x1,y1,x2,y2)` 带来的歧义。
- 默认值:`proposal_bbox_mode` 默认 `BoxMode.XYXY_ABS`(用于 Fast R-CNN 预计算 proposal)。

---

## 【关联】

依据文末及正文中的内部链接,本文档处于 detectron2 文档体系的"数据层"中心节点,与以下模块强耦合:

| 链接目标 | 关系 |
|---|---|
| `../modules/data.html#detectron2.data.DatasetCatalog` | **核心 API**:数据集注册表,本文档的主操作对象 |
| `../modules/data.html#detectron2.data.MetadataCatalog` | **核心 API**:元数据注册表,与 DatasetCatalog 一一对应 |
| `builtin_datasets.md` | **上游**:列出 detectron2 已内建支持的数据集(COCO、Cityscapes 等),决定是否需要"自定义" |
| `../modules/structures.html#detectron2.structures.BoxMode` (×2) | **下游**:bbox 坐标格式枚举 `BoxMode.XYXY_ABS` / `BoxMode.XYWH_ABS` 的定义 |
| `./data_loading.md` | **下游**:自定义格式时需配套编写 mapper,属于 dataloader 侧 |
| `../modules/evaluation.html#detectron2.evaluation.DatasetEvaluator` | **下游**:评估器依赖 `image_id` 与 `category_id`,对应 `annotations` 字段 |
| `../modules/data.html#detectron2.data.datasets.load_coco_json` | **便捷路径**:加载 COCO 数据集会自动设置 `thing_classes` 等 Metadata |
| `../modules/data.html#detectron2.data.load_proposals_into_dataset` | **下游工具**:把预计算 proposal 注入 dataset,对应 Fast R-CNN 的 `proposal_boxes/logits/mode` 字段 |
| `../../projects/TensorMask` | **同层示例**:detectron2 项目目录,展示如何基于本文档的注册机制承载新任务 |

逻辑链路:**builtin_datasets.md → (本文档)注册自定义数据集 → Metadata 注入类别/颜色/关键点 → 数据流经 dataloader(mapper,见 data_loading.md)→ 由 structures.BoxMode 解释坐标 → 训练/评估(用 DatasetEvaluator)→ 可视化/日志使用 thing_colors 等**。

---

## 【使用方法】

### 注册数据集

```python
from detectron2.data import DatasetCatalog

def my_dataset_function():
    # 必须返回 list[dict],且多次调用结果一致
    return [
        {
            "file_name": "/path/to/img1.jpg",
            "height": 480,
            "width": 640,
            "image_id": 1,
            "annotations": [
                {
                    "bbox": [x1, y1, x2, y2],          # 4 个 float
                    "bbox_mode": 0,                     # BoxMode.XYXY_ABS = 0
                    "category_id": 0,                   # [0, num_categories-1]
                    # 可选:
                    # "segmentation": [[x1,y1,...,xn,yn]],  # 多边形
                    # 或 {"size":[H,W], "counts": "..."}     # COCO RLE
                    # "keypoints": [x1,y1,v1,...],            # v ∈ {0,1,2}
                    # "iscrowd": 0,
                }
            ],
            # 可选:"sem_seg_file_name": "/path/to/gt.png",
        },
        ...
    ]

DatasetCatalog.register("my_dataset", my_dataset_function)
data = DatasetCatalog.get("my_dataset")  # List[Dict]
```

### 注册元数据

```python
from detectron2.data import MetadataCatalog
MetadataCatalog.get("my_dataset").thing_classes = ["person", "dog"]
# 其他常用键:
# .thing_colors   = [(R,G,B), ...]   # [0,255], 可视化
# .stuff_classes  = [...]
# .keypoint_names = [...]
# .keypoint_flip_map = [("left_eye","right_eye"), ...]
```

### 相关配置项(原文中明确出现)

| 配置 | 作用 | 取值/默认 |
|---|---|---|
| `DATALOADER.FILTER_EMPTY_ANNOTATIONS` | 控制是否剔除 `annotations=[]` 的图像 | 默认 **True(剔除)**,设为 `False` 可保留 |
| `cfg.INPUT.MASK_FORMAT` | 当 annotation 用 COCO RLE 时,必须配合设置 | 设为 `"bitmask"`(配合默认 dataloader) |
| `proposal_bbox_mode` | 预计算 proposal 的 bbox 格式 | 默认 `BoxMode.XYXY_ABS` |

### 命令式工具(原文给出)

- COCO RLE 编码:`pycocotools.mask.encode(np.asarray(mask, order="F"))` —— Fortran 顺序,**不可省略 `order="F"`**。
- 一键加载 COCO 并自动填 Metadata:`detectron2.data.datasets.load_coco_json(...)`(详见 `../modules/data.html#detectron2.data.datasets.load_coco_json`)。
- 注入预计算 proposal:`detectron2.data.load_proposals_into_dataset(...)`(详见对应模块页)。

### 快速起步链接

原文指向一份可交互的 Colab 教程:
> [https://colab.research.google.com/drive/16jcaJoc6bCFAQ96jDe2HwtXj7BMD_-m5](https://colab.research.google.com/drive/16jcaJoc6bCFAQ96jDe2HwtXj7BMD_-m5)
用于演示"注册 + 训练自定义格式数据集"的完整流程,适合作为本文档的实操补充。

---

> **文档末尾说明**:原文在 Metadata 键列表处被截断(`keypoint_flip_map` 之后的内容未给出),本解读仅基于已呈现内容,未对未给出字段做推测。
