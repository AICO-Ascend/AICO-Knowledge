# 教程 2: 自定义数据集

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/zh_cn/tutorials/customize_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/zh_cn/tutorials/customize_dataset.md

# 一体化深度解读:教程 2 — 自定义数据集

---

## 【定位】

这篇文档是 MMDetection 框架下「自定义数据集」的官方教程,系统说明了当用户需要将自有标注数据接入 MMDetection 训练流水线时的三种核心路径(转 COCO/PASCAL 离线格式、转中间格式、新写 CustomDataset 子类)以及通过三种 dataset wrapper(RepeatDataset/ClassBalancedDataset/ConcatDataset)在训练阶段组合/重采样数据集的方法。

---

## 【技术要点】

1. **三路径选择框架**:支持新数据格式有三条路线——离线转为 COCO/PASCAL、离线/在线转为 MMDetection 定义的中间格式、或新建继承 `CustomDataset` 的类。MMDetection 官方推荐「离线转 COCO + 修改配置」路径。
2. **COCO JSON 三键结构**:`images`(含 `file_name`/`height`/`width`/`id`)、`annotations`(含 `segmentation`/`area`/`iscrowd`/`image_id`/`bbox`/`category_id`/`id`)、`categories`(含 `id`/`name`)为必备顶层字段。
3. **配置文件两处修改**:①`data` 字段的 `train/val/test` 各自增加 `classes` 元组;②`model` 字段内的 `num_classes` 由 COCO 默认 80 改为自定义类别数(示例为 5)。实例中 `bbox_head` 三处与 `mask_head` 一处共四处 `num_classes` 需同步修改。
4. **annotations 三条校验规则**:①`categories` 长度 == 配置 `classes` 元组长度;②`classes` 与 `categories[*].name` 元素及顺序一致(字符串顺序影响标签索引与可视化);③`annotations[*].category_id` 必须落在 `categories[*].id` 集合内。
5. **中间标注格式(ann dict 结构)**:每个样本字典含 `filename`(相对路径)、`width`、`height`,训练时额外含 `ann` 子字典,后者强制包含 `bboxes`(numpy float32,shape `(n,4)`)与 `labels`(numpy int64,shape `(n,)`),可选包含 `bboxes_ignore`/`labels_ignore`。
6. **三种 dataset wrapper**:①`RepeatDataset` 用 `times=N` 整体重复;②`ClassBalancedDataset` 用 `oversample_thr=1e-3` 按类别频率重采样(需实例化 `self.get_cat_ids(idx)`);③`ConcatDataset` 既支持同类型多标注文件合并(可设 `separate_eval=False`),也支持不同类型数据集拼接。

---

## 【关键机制与数据】

### 工作原理 / 数据流

**路径 A — 离线转 COCO(推荐)**:
原始标注 → 外部脚本产出符合 COCO schema 的 JSON(必含 `images`/`annotations`/`categories`) → 在 `configs/my_custom_config.py` 中以 `_base_` 继承预训练配置 → 仅修改 `classes` 元组与 `num_classes` → 复用 `CocoDataset` 直接训练。

**路径 B — 中间格式转换(在线或离线)**:
原始标注 → 在线时自定义 `CustomDataset` 子类并重写 `load_annotations(self, ann_file)` 与 `get_ann_info(self, idx)`(参照 `CocoDataset`/`VOCDataset`);离线时先转 pickle/json,再使用 `CustomDataset` 加载。

**路径 C — Dataset Wrapper 改造数据分布**:
原始 Dataset 配置 → 作为 `dataset` 子字段嵌入 wrapper 配置(`RepeatDataset`/`ClassBalancedDataset`/`ConcatDataset`) → 由 wrapper 在 `__init__` 阶段完成重复、类别均衡或拼接。

### 原文锚定的关键参数

| 维度 | 原文取值 |
|------|---------|
| 默认 `num_classes`(COCO) | 80 |
| 示例自定义类别数 | 5 |
| `bbox_head` 中需修改 `num_classes` 的位置数 | 3(对应 Cascade Mask R-CNN 的三个 stage) |
| `mask_head` 中需修改 `num_classes` 的位置数 | 1 |
| 每 GPU `samples_per_gpu`(示例) | 2 |
| 每 GPU `workers_per_gpu`(示例) | 2 |
| `oversample_thr`(类别均衡示例) | 1e-3 |
| 重复因子 `times`(RepeatDataset) | N(用户自定义) |
| 中间格式 `bboxes` 类型 | numpy float32,shape `(n,4)` |
| 中间格式 `labels` 类型 | numpy int64,shape `(n,)` |
| 自定义示例 `annotation.txt` 图片宽高 | 1280×720(000001.jpg)、1280×720(000002.jpg) |
| 自定义示例 `MyDataset.CLASSES` | `('person','bicycle','car','motorcycle')` 共 4 类 |
| 文本标注文件结构 | `#` 分隔块;每块包含 `filename`、宽高、bbox 数量、若干 `x1 y1 x2 y2 label` 行 |

### 性能 / 评估机制说明(原文)

- 原文:实例分割数据「MMDetection 目前只支持评估 COCO 格式的 mask AP」,即非 COCO mask 格式无法获得标准的 mask AP 评估。
- 原文:`categories` 中不连续的 `id` 会被框架自动映射为连续索引,因此 `name` 的字符串顺序就是真正的标签序号,可视化标签与 loss 索引皆受其影响。

---

## 【表格解读】

**原文无表格。**

(原文中所有结构化内容均以 Python 代码块 / YAML 风格配置块 / `annotation.txt` 文本块呈现,未出现 markdown 表格或表格化参数表。)

---

## 【公式解读】

**原文无公式。**

(原文中无 LaTeX 数学公式或带运算符号的伪代码表达式。出现的形如 `<np.ndarray, float32> (n, 4)`、`<np.ndarray, int64> (n, )` 均为数组 shape/类型标注,而非公式。)

---

## 【关联】

1. **与「教程 1:配置文件」的关系**:本文示例配置 `configs/my_custom_config.py` 使用 `_base_ = './cascade_mask_rcnn_r50_fpn_1x_coco.py'` 继承自基础配置,说明自定义数据集的能力建立在配置继承机制之上,与教程 1 紧密耦合。
2. **与 `CustomDataset` 基类**:在线转换路径要求子类继承 `mmdet/datasets/custom.py` 中的 `CustomDataset`,所有 wrapper 的 `dataset` 子字段也接受 `CustomDataset` 的任意子类(包括 `CocoDataset`、`VOCDataset`、用户自定义 `MyDataset`)。
3. **与 CityScapes 官方支持**:原文以 CityScapes 为官方实践范例,链接到 `tools/dataset_converters/cityscapes.py` 与 `configs/cityscapes`,说明「转 COCO + 改配置」路径在生产级数据集中已有落地。
4. **与内部链接 `../../mmdet/datasets/dataset_wrappers.py` 的关系**:本教程最后一段在介绍 `ClassBalancedDataset` 时显式提供此源码链接,意味着 `RepeatDataset`/`ClassBalancedDataset`/`ConcatDataset` 三类 wrapper 的具体实现(构造、`__len__`、`get_cat_ids` 调用逻辑、`oversample_thr` 重采样算法)统一封装在该模块中,使用者可参照该文件确认实现细节。
5. **与 `pipeline` 字段耦合**:所有 wrapper 示例配置尾部都包含 `pipeline=train_pipeline`,表明 dataset wrapper 只改变「样本如何被枚举」,不改变「单样本如何被 transform」,二者职责正交。
6. **与 `bbox_head`/`mask_head` 多 stage 结构耦合**:Cascade Mask R-CNN 的 `roi_head.bbox_head` 是列表(三个 `Shared2FCBBoxHead`),意味着 `num_classes` 必须在列表每一项内都改一遍,这是 cascade 类检测器特有的耦合点,单 stage 检测器只需改一处。

---

## 【使用方法】

### 启用条件与触发入口

**路径 A — 离线转 COCO**:
1. 将自定义标注转为 COCO JSON(必备三键:`images`/`annotations`/`categories`)。
2. 新建 `configs/my_custom_config.py`,`_base_` 指向预训练配置(如 `cascade_mask_rcnn_r50_fpn_1x_coco.py`)。
3. 在 `data.train/val/test` 中填入 `classes=('a','b','c','d','e')`、`ann_file`、`img_prefix`,`type='CocoDataset'`。
5. 在 `model.roi_head.bbox_head` 三处与 `mask_head` 中将 `num_classes` 从 80 改为 5。
6. 校验:`categories` 长度 == `classes` 长度;`categories[*].name` 与 `classes` 顺序一致;`annotations[*].category_id` ∈ `categories[*].id`。

**路径 B — 中间格式 + 自定义类**:
1. 在 `mmdet/datasets/my_dataset.py` 中定义继承 `CustomDataset` 的 `MyDataset`,设置 `CLASSES` 元组。
2. 重写 `load_annotations(self, ann_file)`:解析自定义文本格式,产出 `data_infos` 列表(每元素含 `filename`/`width`/`height`/`ann`)。
3. 重写 `get_ann_info(self, idx)`:返回 `self.data_infos[idx]['ann']`。
4. 在配置中以 `type='MyDataset'` 引用,`ann_file='image_list.txt'`,`pipeline=train_pipeline`。

**路径 C — Dataset Wrapper**:
- 重复:`type='RepeatDataset'`,`times=N`),内层 `dataset` 字段放原始配置。
- 类别均衡:`type='ClassBalancedDataset'`,`oversample_thr=1e-3`,且原始 dataset 类须实现 `self.get_cat_ids(idx)`。
- 合并同类型多文件:在 `ann_file` 字段传入列表(`['anno_file_1','anno_file_2']`),可加 `separate_eval=False` 让合并后的整体作为单一评估单元。
- 合并不同类型数据集:分别定义 `dataset_A_val`、`dataset_B_val`,然后在 `data` 字段中聚合(原文 `dataset_A_val = dict()`、`dataset_B_val = dict()` 处示例被截断)。

### 关键配置项速查

| 配置项 | 含义 | 原文示例值 |
|------|------|---------|
| `dataset_type` | 数据集类名 | `'CocoDataset'` / `'MyDataset'` |
| `classes` | 类别名元组 | `('a','b','c','d','e')` |
| `ann_file` | 标注文件路径或列表 | `'path/to/your/train/annotation_data'` |
| `img_prefix` | 图片前缀路径 | `'path/to/your/train/image_data'` |
| `samples_per_gpu` | 每 GPU 批样本数 | 2 |
| `workers_per_gpu` | 每 GPU 数据加载 worker 数 | 2 |
| `num_classes` | 类别总数(改自默认 80) | 5 |
| `times` | RepeatDataset 重复倍数 | N |
| `oversample_thr` | 类别均衡阈值 | 1e-3 |
| `separate_eval` | ConcatDataset 是否合并评估 | `False` |

### 推荐路径

原文明确建议:「推荐训练之前进行离线转换,这样就可以继续使用 `CocoDataset` 且只需修改标注文件的路径以及训练的种类」,即路径 A 为官方推荐路径,其它两条路径适用于必须保留自有标注格式或需要动态重采样/拼接的特殊场景。
