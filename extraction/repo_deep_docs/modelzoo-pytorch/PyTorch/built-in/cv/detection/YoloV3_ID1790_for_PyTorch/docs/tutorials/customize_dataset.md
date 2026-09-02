# Tutorial 2: Customize Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/YoloV3_ID1790_for_PyTorch/docs/tutorials/customize_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/YoloV3_ID1790_for_PyTorch/docs/tutorials/customize_dataset.md

# 文档深度解读:Tutorial 2: Customize Datasets

---

## 【定位】

这篇文档是 MMDetection 官方教程系列的第二篇,旨在解决**"当用户拥有自有数据格式时,如何接入 MMDetection 框架进行目标检测(及实例分割)训练与评测"**这一问题。它系统描述了 MMDetection 对自定义数据集的三层支持能力:**格式重整到 COCO/PASCAL**、**在线/离线转换为中间格式**、以及**通过数据集包装器(dataset wrappers)调整数据分布**。

---

## 【技术要点】

1. **首选路线:转换为 COCO/PASCAL 现有格式**
   - MMDetection 推荐将新数据**离线**转换为 COCO 格式,训练时只需修改 config 的标注路径与类别字段。
   - COCO 标注 JSON 必须包含三个键:`images`(含 `file_name` / `height` / `width` / `id`)、`annotations`(实例标注)、`categories`(类别名与 ID)。

2. **次选路线:转为 MMDetection 自定义中间格式**
   - 中间格式定义为 list of dict,每个 dict 对应一张图,字段为 `filename` / `width` / `height`,训练时额外含 `ann`(内部又是 dict,含 `bboxes` numpy array 与 `labels` numpy array,可选 `bboxes_ignore` / `labels_ignore`)。
   - `bboxes` 为 `(n, 4)` `float32`,`labels` 为 `(n,)` `int64`。

3. **两种转换时机**
   - **Online**:继承 `CustomDataset`,覆写 `load_annotations(self, ann_file)` 与 `get_ann_info(self, idx)` 两方法(参考 `CocoDataset` / `VOCDataset`)。
   - **Offline**:先用脚本把标注转成上述中间格式再存为 pickle/json,然后直接用 `CustomDataset` 加载(参考 `pascal_voc.py`)。

4. **自定义数据集完整示例**
   - 演示了如何从一个文本格式 `annotation.txt`(每张图以 `#` 开头,随后是文件名 `000001.jpg`、`1280 720`、bbox 数量 `2`、再跟若干 `x1 y1 x2 y2 label` 行)读出图像与标注,封装为 `MyDataset(CustomDataset)`,并在 config 中通过 `type='MyDataset'`、`ann_file='image_list.txt'` 启用。
   - 该示例中定义的类别元组为 `('person', 'bicycle', 'car', 'motorcycle')` 共 4 类(原图标注中实际出现的 label 为 1/2/3)。

5. **数据集包装器(dataset wrappers)**
   - 支持三种包装器:`RepeatDataset`、`ClassBalancedDataset`、`ConcatDataset`。
   - `RepeatDataset` 通过参数 `times=N` 简单重复整个数据集。
   - `ClassBalancedDataset` 按类别频次重复,关键参数为 `oversample_thr=1e-3`,且要求被包装的数据集实现 `self.get_cat_ids(idx)`。
   - `ConcatDataset` 提供三种拼接方式(同类型不同 ann_file 列表、`separate_eval=False` 等),用于训练与评测时按需合并多个数据源。

6. **训练 batch 与并行配置**
   - 在 config 中通过 `samples_per_gpu=2`、`workers_per_gpu=2` 控制单卡 batch size 与 DataLoader worker 数量(原文以 5 类 COCO 自定义数据集为例)。

---

## 【关键机制与数据】

**工作原理与数据流**(原文描述):

- **COCO 标注 JSON 必要键结构**(原文):
  - `images`:list,每项含 `file_name`、`height`、`width`、`id`(如 `'COCO_val2014_000000001268.jpg'`、`height: 427`、`width: 640`、`id: 1268`)。
  - `annotations`:list,字段包括 `segmentation`、`area`、`iscrowd`、`image_id`、`bbox`(`[x, y, w, h]` 四元组,例如 `[192.81, 224.8, 74.73, 33.43]`)、`category_id`、`id`。
  - `categories`:`{'id': 0, 'name': 'car'}` 形式。

- **中间格式数据结构**(原文):
  - 外层为 list of dict;每 dict 含 `filename`、`width`、`height` 与可选 `ann`。
  - `ann` 内部 `bboxes` 为 `(n, 4)` float32 ndarray;`labels` 为 `(n,)` int64 ndarray;`bboxes_ignore` 为 `(k, 4)` float32;`labels_ignore` 为 `(k,)` int64(可选)。
  - 原文示例中 `filename='a.jpg'`、`width=1280`、`height=720`。

- **自定义文本标注文件格式**(原文示例 `annotation.txt`):
  - 每张图以单独一行 `#` 分隔,后跟文件名、宽高两数、bbox 数量、若干 bbox 行,例如 `10 20 40 60 1`(即 `x_min=10, y_min=20, x_max=40, y_max=60, label=1`)。

- **性能/数值数据**:原文**未给出**任何训练速度、mAP、显存占用等性能数字;所给数字仅是字段示例值(如 `area: 1035.749`、`samples_per_gpu=2`、`oversample_thr=1e-3`)。

---

## 【表格解读】

**原文无表格**(无 markdown 表格或类似的对照表)。文中以代码块形式给出了 COCO JSON 字段示例、中间格式 dict 示例、自定义文本标注示例以及若干 config 片段,但都不是结构化表格。

---

## 【公式解读】

**原文无公式**(无 LaTeX 数学公式,无伪代码公式)。

---

## 【关联】

文档显式指向的外部/内部模块与资源如下:

- **基类与现成实现**
  - `CustomDataset`:在线转换方案的基类;`RepeatDataset` / `ClassBalancedDataset` / `ConcatDataset` 等 wrapper 继承自其上层抽象。
  - `CocoDataset`(链接:`https://github.com/open-mmlab/mmdetection/blob/master/mmdet/datasets/coco.py`):作为在线转换的参考实现。
  - `VOCDataset`(链接:`https://github.com/open-mmlab/mmdetection/blob/master/mmdet/datasets/voc.py`):另一个在线转换参考。
  - 内部链接 `../../mmdet/datasets/dataset_wrappers.py`:**即 `RepeatDataset`、`ClassBalancedDataset`、`ConcatDataset` 三个 wrapper 类的源代码**,文档在 Class balanced dataset 章节末尾明确"You may refer to [source code](../../mmdet/datasets/dataset_wrappers.py) for details"。

- **离线转换工具脚本**
  - `pascal_voc.py`(链接:`https://github.com/open-mmlab/mmdetection/blob/master/tools/convert_datasets/pascal_voc.py`):PASCAL VOC → 中间格式的离线转换样例。
  - `cityscapes.py`(链接:`https://github.com/open-mmlab/mmdetection/blob/master/tools/convert_datasets/cityscapes.py`):CityScapes → COCO 格式转换样例,文档将其作为"重整为现有格式"路线的代表案例。

- **预置 configs**
  - CityScapes 的下游 finetuning configs(链接:`https://github.com/open-mmlab/mmdetection/blob/master/configs/cityscapes`):为同一数据集提供训练配置范例。

- **上下游关系**
  - 上游:**数据采集/标注工具**产出原始标注 → 经 `tools/convert_datasets/*.py` 离线转换 → 得到 COCO JSON 或中间格式 pkl/json。
  - 下游:**configs** 通过 `dataset_type`、`ann_file`、`pipeline` 等字段把数据接入训练流程;**模型**(`YoloV3` 等)与 **evaluators**(如 COCO mask AP evaluator)最终消费这些数据。文档明确指出"**MMDetection only supports evaluating mask AP of dataset in COCO format for now**",即下游实例分割评测强制要求 COCO 格式。

---

## 【使用方法】

> 说明:文档正文在 `ConcatDataset` 第一种拼接示例之后被截断(`dataset_A_train = dict(` 后没有给出完整代码),下列信息均严格基于**原文可见内容**。

- **路线 A:转换到 COCO 格式 + 复用 `CocoDataset`**(原文)
  - 将自有标注转为 COCO JSON。
  - 在 config(`configs/my_custom_config.py`)中设置:
    ```python
    dataset_type = 'CocoDataset'
    classes = ('a', 'b', 'c', 'd', 'e')
    data = dict(
        samples_per_gpu=2,
        workers_per_gpu=2,
        train=dict(type=dataset_type, classes=classes, ann_file='path/to/your/train/data', ...),
        val=dict(  type=dataset_type, classes=classes, ann_file='path/to/your/val/data',   ...),
        test=dict( type=dataset_type, classes=classes, ann_file='path/to/your/test/data', ...))
    ```

- **路线 B:自定义 `MyDataset` + `CustomDataset`**(原文)
  - 在 `mmdet/datasets/my_dataset.py` 中通过 `@DATASETS.register_module()` 注册 `class MyDataset(CustomDataset)`,实现 `load_annotations(self, ann_file)` 与 `get_ann_info(self, idx)`。
  - config 启用方式:
    ```python
    dataset_A_train = dict(
        type='MyDataset',
        ann_file='image_list.txt',
        pipeline=train_pipeline)
    ```

- **路线 C:使用 `RepeatDataset`**(原文)
  ```python
  dataset_A_train = dict(
      type='RepeatDataset',
      times=N,
      dataset=dict(type='Dataset_A', ..., pipeline=train_pipeline))
  ```

- **路线 D:使用 `ClassBalancedDataset`**(原文)
  ```python
  dataset_A_train = dict(
      type='ClassBalancedDataset',
      oversample_thr=1e-3,
      dataset=dict(type='Dataset_A', ..., pipeline=train_pipeline))
  ```
  前提:被包装数据集需实现 `self.get_cat_ids(idx)`。

- **路线 E:使用 `ConcatDataset` 拼接**(原文,但**示例被截断**)
  - 同类型不同 ann_file 的拼接方式:
    ```python
    dataset_A_train = dict(
        type='Dataset_A',
        ann_file=['anno_file_1', 'anno_file_2'],
        pipeline=train_pipeline)
    ```
  - 整体评测而非按子集分别评测的开关 `separate_eval=False`(原文已提及该参数,但完整代码示例**原文未给出**)。

- **命令行/启动方式**:原文**未涉及**任何具体的训练启动命令(如 `tools/train.py` 的调用方式),仅描述 config 写法与 wrapper 用法。
