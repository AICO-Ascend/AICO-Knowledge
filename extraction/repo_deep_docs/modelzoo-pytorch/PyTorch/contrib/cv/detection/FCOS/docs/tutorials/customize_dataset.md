# Tutorial 2: Customize Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/FCOS/docs/tutorials/customize_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/FCOS/docs/tutorials/customize_dataset.md

# 深度解读：FCOS 中「Customize Datasets」教程文档

---

## 【定位】

这篇文档解决「**如何让 MMDetection/FCOS 使用自定义数据集**」的问题，描述其支持的多种数据接入路径——既可将数据转为 COCO/PASCAL VOC 等已有格式，也可直接转为 MMDetection 定义的「中间格式」，还可以通过 `RepeatDataset`/`ClassBalancedDataset`/`ConcatDataset` 三种 wrapper 改变数据分布，从而在不动框架源码的前提下复用训练流程。

---

## 【技术要点】

1. **推荐路径：转 COCO 离线转换**。先在外部把任意格式转为 COCO json，再仅修改 config 中 `ann_file` 路径与 `classes` 元组即可复用 `CocoDataset`，避免侵入框架。
2. **COCO json 三件套键**：`images`（含 `file_name`/`height`/`width`/`id`）、`annotations`（含 `segmentation`（可选）/`area`/`iscrowd`/`image_id`/`bbox`/`category_id`/`id`）、`categories`（含 `id`/`name`）。
3. **config 三处必须同步**：`train` / `val` / `test` 三个 dict 都要传入 `type=dataset_type`、`classes=classes`、`ann_file=...`，与示例中 `samples_per_gpu=2`、`workers_per_gpu=2` 共同构成最小可用 data 配置。
4. **中间格式是「每图一个 dict」的列表**：必含 `filename`、`width`、`height`，训练时附加 `ann`（其中 `bboxes` 为 `(n,4)` `float32`、`labels` 为 `(n,)` `int64`，可选 `bboxes_ignore`/`labels_ignore`），测试时只读前三项。
5. **自定义 Dataset 两条路**：在线——继承 `CustomDataset` 并覆写 `load_annotations(self, ann_file)` 与 `get_ann_info(self, idx)`；离线——将标注转成上述中间格式并存为 pickle/json，再直接用 `CustomDataset`。
6. **三种 wrapper**：`RepeatDataset(times=N)` 整体重复、`ClassBalancedDataset(oversample_thr=1e-3)` 按类别频率过采样（要求数据具备 `self.get_cat_ids(idx)` 接口）、`ConcatDataset` 拼接多个数据集（`ann_file` 可传入列表，`separate_eval=False` 时整体评估）。
7. **注意事项**：实例分割数据集目前**仅支持 COCO 格式的 mask AP 评估**；建议离线转换以保持与 `CocoDataset` 兼容。

---

## 【关键机制与数据】

**工作原理（数据流）**：
- 离线路线：原始标注 → 转 COCO json → 写 config（指向 json 与类别）→ 训练时 `CocoDataset` 直接消费。
- 在线路线：原始文本标注 → 自定义 `MyDataset.load_annotations` 解析 → 构造 `data_infos` 列表（每元素即一份「中间格式」dict）→ `get_ann_info(idx)` 返回对应 `ann` → 训练 pipeline 在此基础上做增强与模型输入。

**原文示例给出的具体数值（原文摘录）**：
- COCO bbox 示例：`[192.81, 224.8, 74.73, 33.43]`，`area=1035.749`，`iscrowd=0`，`image_id=1268`，`category_id=16`，`id=42986`。
- 中间格式图像尺寸示例：`width=1280, height=720`；自定义数据集文本格式示例中 `000001.jpg` 标 2 个框，`000002.jpg` 标 3 个框。
- `samples_per_gpu=2`、`workers_per_gpu=2`、`classes=('a','b','c','d','e')`（5 类示例）。
- `oversample_thr=1e-3` 用于 `ClassBalancedDataset`。
- 自定义 Dataset 类声明的 `CLASSES = ('person', 'bicycle', 'car', 'motorcycle')`（4 类）。

**性能数据**：原文未涉及任何训练/推理性能数字。

---

## 【表格解读】

**原文无表格**。文档以配置代码块与标注 json 示例承载参数化信息，未提供参数表或性能对比表。可视化信息全部以 Python dict/列表的「代码片段」形式给出（已在「关键机制与数据」中按原文摘录）。

---

## 【公式解读】

**原文无公式**。文中涉及的数据约定（如 `(n, 4)` 浮点 bbox、`(n,)` int64 label）以代码注释 `<np.ndarray, float32> (n, 4)` 的形式表达，而非数学公式。

---

## 【关联】

- **`../../mmdet/datasets/dataset_wrappers.py`**：文中「Class balanced dataset」一节明确指出「请参考源码以了解细节」，该文件是 `RepeatDataset` / `ClassBalancedDataset` / `ConcatDataset` 三种 wrapper 的实现位置，是本教程在「改变数据分布」维度上的直接上游/下游模块。
- **`CustomDataset`**（`mmdet/datasets/custom.py`）：自定义数据集示例 `MyDataset` 通过 `@DATASETS.register_module()` 与 `class MyDataset(CustomDataset)` 关联到此基类，是「自定义 Dataset」路径的基类。
- **`CocoDataset` / `VOCDataset`**（`mmdet/datasets/coco.py`、`voc.py`）：被作为「在线自定义」时仿照的两个范例（覆写 `load_annotations` 与 `get_ann_info`）。
- **`tools/convert_datasets/pascal_voc.py`**：离线转换到中间格式 + pickle/json 的参考脚本；`tools/convert_datasets/cityscapes.py` 与 `configs/cityscapes` 是「推荐转 COCO 离线转换」路径的官方示范。
- **`builder.DATASETS`**：通过 `@DATASETS.register_module()` 将 `MyDataset` 注册进 MMDetection 的数据集注册表，使其可在 config 中通过 `type='MyDataset'` 字符串引用。
- **FCOS 与本教程的关系**：本文档位于 `PyTorch/contrib/cv/detection/FCOS/docs/tutorials/`，是 FCOS 在 MMDetection 体系下的「使用教程」，下游接 FCOS 的 `train_pipeline` / `test_pipeline`，上游决定可喂入的训练样本分布。

---

## 【使用方法】

**启用方式（原文给出的最小化配置范式）**：

1. **COCO 格式自定义数据集（5 类示例，原文）**：
```python
dataset_type = 'CocoDataset'
classes = ('a', 'b', 'c', 'd', 'e')
data = dict(
    samples_per_gpu=2,
    workers_per_gpu=2,
    train=dict(type=dataset_type, classes=classes,
               ann_file='path/to/your/train/data', ...),
    val=dict(  type=dataset_type, classes=classes,
               ann_file='path/to/your/val/data',   ...),
    test=dict( type=dataset_type, classes=classes,
               ann_file='path/to/your/test/data',  ...))
```

2. **自定义文本格式数据集（原文 `MyDataset` 示例）**：
- 实现文件：`mmdet/datasets/my_dataset.py`
- 注册：`@DATASETS.register_module()`，类继承 `CustomDataset`，`CLASSES = ('person','bicycle','car','motorcycle')`
- config 调用：
```python
dataset_A_train = dict(
    type='MyDataset',
    ann_file='image_list.txt',
    pipeline=train_pipeline)
```

3. **`RepeatDataset` wrapper**：`type='RepeatDataset', times=N`，原 dataset 配置放进内层 `dataset=dict(...)`。
4. **`ClassBalancedDataset` wrapper**：`type='ClassBalancedDataset', oversample_thr=1e-3`，原 dataset 配置放进内层 `dataset=dict(...)`；原 dataset 需提供 `self.get_cat_ids(idx)`。
5. **`ConcatDataset`（同类型多 ann_file）**：
```python
dataset_A_train = dict(
    type='Dataset_A',
    ann_file=['anno_file_1','anno_file_2'],
    pipeline=train_pipeline)
```
测试/评估时若需「整体评估而非分数据集评估」，需设置 `separate_eval=False`（原文在文档截断处出现该字段的设置方式）。

**命令行 / 启动命令**：原文未涉及具体训练启动命令，仅停留在 config 层。
