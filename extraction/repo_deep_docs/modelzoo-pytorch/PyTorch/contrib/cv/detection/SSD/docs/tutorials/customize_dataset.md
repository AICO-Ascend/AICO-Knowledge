# Tutorial 2: Customize Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/SSD/docs/tutorials/customize_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/SSD/docs/tutorials/customize_dataset.md

# SSD 文档深度解读 — Tutorial 2: Customize Datasets

## 【定位】

本文档面向需要在 MMDetection（SSD 目标检测框架）中接入自有数据集的开发者,系统讲解了"支持新数据格式"的三种主流路径(转成 COCO/PASCAL 现有格式、转成自定义中间格式、在线继承 `CustomDataset`),并介绍了通过 **Dataset Wrappers**(`RepeatDataset` / `ClassBalancedDataset` / `ConcatDataset`)对数据集进行重复、类别均衡与拼接的封装机制,是 SSD 检测流程中"数据层自定义"的标准 tutorial。

---

## 【技术要点】

1. **首选方案:转 COCO 离线格式**
   官方推荐把自定义数据集转成 COCO 格式后离线转换,后续只需修改 config 中的 `ann_file` 与 `classes`,无需重写 `Dataset` 类。

2. **COCO JSON 三大必需字段**
   `images`(含 `file_name`/`height`/`width`/`id`)、`annotations`(实例标注列表,含 `bbox`/`category_id`/`image_id` 等)、`categories`(类别名+ID)。原文给出样本:`height=427, width=640, id=1268`;`bbox=[192.81, 224.8, 74.73, 33.43]`,`category_id=16`。

3. **Config 端最小改动示例**
   `dataset_type='CocoDataset'`,自定义 `classes=('a','b','c','d','e')`,在 `data` 字典的 `train/val/test` 子项中替换 `ann_file` 即可,`samples_per_gpu=2, workers_per_gpu=2`。

4. **中间格式 (Middle Format)**
   数据集标注是 list of dict,每张图必须含 `filename`(相对路径)、`width`、`height`(测试用);训练额外含 `ann` dict,其中 `bboxes` 为 `np.ndarray float32 (n,4)`,`labels` 为 `np.ndarray int64 (n,)`,可选 `bboxes_ignore`、`labels_ignore`。

5. **自定义 Dataset 类继承 `CustomDataset`**
   仅需重写两个方法:`load_annotations(self, ann_file)`(解析原始标注)和 `get_ann_info(self, idx)`(返回索引对应图的 `ann` 字典),并通过 `@DATASETS.register_module()` 注册。原文给出从文本 `annotation.txt` 解析的 `MyDataset` 完整实现,`CLASSES = ('person','bicycle','car','motorcycle')`。

6. **三种 Dataset Wrappers**
   - `RepeatDataset`:通过 `times=N` 简单重复;
   - `ClassBalancedDataset`:基于类别频率重采样,需 `oversample_thr=1e-3`,依赖被包装数据集实现 `self.get_cat_ids(idx)`;
   - `ConcatDataset`:支持单类型多 `ann_file` 列表形式拼接,并可通过 `separate_eval=False` 把拼接集合作为整体评估。

---

## 【关键机制与数据】

**工作原理/数据流(原文)**

- **COCO 路径**:用户离线把数据 → COCO JSON → 在 config 中以 `type='CocoDataset'` + `ann_file` 指向新 JSON,`classes` 元组覆盖默认类别;`samples_per_gpu=2, workers_per_gpu=2` 控制 dataloader 行为。
- **中间格式路径**:解析脚本把任意原始标注 → 中间格式 dict 列表 → 保存为 pickle/json → 直接用 `CustomDataset` 加载;或在线继承 `CustomDataset`,在 `load_annotations` 中实时完成解析。
- **Wrappers 数据流**:`RepeatDataset/ClassBalancedDataset` 在原 dataset config 外再包一层,`dataset=dict(...)` 字段嵌入原始 config;`ClassBalancedDataset` 通过调用 `get_cat_ids(idx)` 取得该样本类别,依据类别频次与 `oversample_thr=1e-3` 决定采样权重;`ConcatDataset` 接受 `ann_file=['anno_file_1','anno_file_2']` 列表,评估时可设置 `separate_eval=False` 整体评估。

**性能数据**
原文:未给出任何 benchmark/AP/速度数字。仅在文末链接了 [cityscapes.py](https://github.com/open-mmlab/mmdetection/blob/master/tools/convert_datasets/cityscapes.py) 与 [cityscapes configs](https://github.com/open-mmlab/mmdetection/blob/master/configs/cityscapes) 作为"我们用这种方式支持 CityScapes"的实证引用,但**未列出具体性能指标**。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **`CustomDataset`(基类)**:`../../mmdet/datasets/custom.py`(原文未直接给出链接,作为 `MyDataset`、`CocoDataset`、`VOCDataset` 的共同父类被反复引用)。
- **`Dataset Wrappers` 实现**:`../../mmdet/datasets/dataset_wrappers.py` — 文末给出的内部链接,文档原文说 "You may refer to [source code](../../mmdet/datasets/dataset_wrappers.py) for details",承载 `RepeatDataset` / `ClassBalancedDataset` / `ConcatDataset` 三类的实现。
- **`CocoDataset` 参考实现**:`https://github.com/open-mmlab/mmdetection/blob/master/mmdet/datasets/coco.py` — 展示如何继承 `CustomDataset` 完成 `load_annotations` 与 `get_ann_info` 的重写。
- **`VOCDataset` 参考实现**:`https://github.com/open-mmlab/mmdetection/blob/master/mmdet/datasets/voc.py` — 同上,PASCAL VOC 范式。
- **离线转换脚本**:`tools/convert_datasets/pascal_voc.py`、`tools/convert_datasets/cityscapes.py` — 演示"先离线转中间格式再加载"的范式。
- **下游配置链路**:本文修改的 `dataset_A_train` / `data` 字典最终被 `mmdet/models/detectors` 下各类检测器(`SSD`/`Faster R-CNN` 等)在训练循环中作为 dataloader 数据源消费;`train_pipeline` 与检测器的数据增强/批采样逻辑紧耦合。
- **同类教程**:作为 "Tutorial 2" 的一部分,上文应是 Tutorial 1(配置与运行基础),下文预期是 Tutorial 3(自定义模型/自定义损失)等,但原文未给出这些兄弟 tutorial 的链接。

---

## 【使用方法】

**启用方式与配置项**(原文摘录)

- **COCO 风格启用**(以 5 类自定义数据集为例):
  ```python
  dataset_type = 'CocoDataset'
  classes = ('a','b','c','d','e')
  data = dict(
      samples_per_gpu=2,
      workers_per_gpu=2,
      train=dict(type=dataset_type, classes=classes,
                 ann_file='path/to/your/train/data', ...),
      val=dict(type=dataset_type, classes=classes,
               ann_file='path/to/your/val/data', ...),
      test=dict(type=dataset_type, classes=classes,
                ann_file='path/to/your/test/data', ...))
  ```

- **自定义文本格式启用**(`MyDataset` 注册 + config):
  ```python
  dataset_A_train = dict(
      type='MyDataset',
      ann_file='image_list.txt',
      pipeline=train_pipeline)
  ```

- **`RepeatDataset` 启用**:
  ```python
  dataset_A_train = dict(
      type='RepeatDataset', times=N,
      dataset=dict(type='Dataset_A', ..., pipeline=train_pipeline))
  ```

- **`ClassBalancedDataset` 启用**:
  ```python
  dataset_A_train = dict(
      type='ClassBalancedDataset', oversample_thr=1e-3,
      dataset=dict(type='Dataset_A', ..., pipeline=train_pipeline))
  ```

- **`ConcatDataset` 启用**(同类型多 ann_file):
  ```python
  dataset_A_train = dict(
      type='Dataset_A',
      ann_file=['anno_file_1','anno_file_2'],
      pipeline=train_pipeline)
  # 整体评估(不再分别评估每个子集)
  dataset_A_train = dict(
      type='Dataset_A',
      ...)  # 原文在 separate_eval=False 处截断,具体完整写法原文未涉及
  ```

- **命令**:原文未涉及任何 CLI/启动命令(本文是数据层 tutorial,训练启动命令由外层 training 脚本承担)。
