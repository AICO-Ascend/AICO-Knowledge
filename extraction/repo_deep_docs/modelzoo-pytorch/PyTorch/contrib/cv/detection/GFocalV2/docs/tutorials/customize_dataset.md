# Tutorial 2: Customize Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/GFocalV2/docs/tutorials/customize_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/GFocalV2/docs/tutorials/customize_dataset.md

## 【定位】

这篇文档说明如何在 MMDetection 中接入新的检测数据格式，既支持离线转换为 COCO/PASCAL VOC 或统一中间格式，也支持自定义数据集类以及 `RepeatDataset`、`ClassBalancedDataset`、`ConcatDataset` 等数据集包装器。

## 【技术要点】

1. **提供两条数据接入路线**
   - 将新数据转换为已有的 **COCO** 或 **PASCAL VOC** 格式。
   - 将新数据转换为 MMDetection 定义的中间格式。
   - 转换既可在训练前离线完成，也可训练时在线完成；文档推荐：**离线转换为 COCO 格式**，继续使用 `CocoDataset`。

2. **COCO 格式需要三个顶层键**
   - `images`：包含 `file_name`、`height`、`width`、`id`。
   - `annotations`：包含实例标注，示例中提供 `segmentation`、`area`、`iscrowd`、`image_id`、`bbox`、`category_id`、`id`。
   - `categories`：包含类别 `id` 和类别名 `name`。
   - 原文的五类配置使用：
     ```python
     dataset_type = 'CocoDataset'
     classes = ('a', 'b', 'c', 'd', 'e')
     ```
     训练、验证和测试分别修改各自的 `ann_file`，全局数据配置还给出：
     ```python
     samples_per_gpu=2
     workers_per_gpu=2
     ```

3. **中间格式以“每张图片一个字典”为基本结构**
   - 测试信息包含 `filename`、`width`、`height`。
   - 训练时额外包含 `ann`，其中至少包括 NumPy 数组形式的 `bboxes` 和 `labels`。
   - 数组类型及形状为：
     - `bboxes`：`<np.ndarray, float32> (n, 4)`
     - `labels`：`<np.ndarray, int64> (n,)`
     - `bboxes_ignore`：`<np.ndarray, float32> (k, 4)`，可选
     - `labels_ignore`：`<np.ndarray, int64> (k,)`，可选
   - crowd、difficult 或 ignored 框通过后两个字段表达。

4. **自定义数据集分为在线转换和离线转换**
   - 在线转换：继承 `CustomDataset`，实现：
     ```python
     load_annotations(self, ann_file)
     get_ann_info(self, idx)
     ```
     原文用 `CocoDataset` 和 `VOCDataset` 作为参考实现。
   - 离线转换：先把标注转换成中间格式，再保存为 pickle 或 JSON，之后直接使用 `CustomDataset`；原文以 `pascal_voc.py` 为例。

5. **文本格式可以通过注册新数据集类接入**
   - 在 `mmdet/datasets/my_dataset.py` 中继承 `CustomDataset`。
   - 使用：
     ```python
     @DATASETS.register_module()
     ```
     注册新数据集。
   - 文本文件按“`#`—图片名—宽高—框数量—若干条框标注”分块。
   - 自定义类声明：
     ```python
     CLASSES = ('person', 'bicycle', 'car', 'motorcycle')
     ```
     `load_annotations` 负责形成 `data_infos`，`get_ann_info` 返回当前图片的 `ann`。

6. **数据集包装器可调整采样分布或组合数据**
   - `RepeatDataset`：通过 `times=N` 重复整个数据集。
   - `ClassBalancedDataset`：按类别频率重复，类别不足的底层数据集需实现 `self.get_cat_ids(idx)`；原文参数为 `oversample_thr=1e-3`。
   - `ConcatDataset`：组合数据集；同类数据集可传入 `ann_file` 列表，若把组合结果作为整体评测，可设置 `separate_eval=False`。
   - 原文对实例分割数据集还限定：**目前只有 COCO 格式支持 mask AP 评测**。

## 【关键机制与数据】

整体数据流可概括为：

`原始标注 → 转换脚本或自定义解析器 → COCO JSON / 中间格式 → Dataset 类 → 配置中的 type、classes、ann_file、pipeline → train_pipeline 与评测流程`

- **原文：**推荐的 COCO 路径中，用户转换数据后主要修改配置中的标注路径和类别，不需要重写数据集类。
- **原文：**中间格式可以直接被 `CustomDataset` 使用；在线转换则由自定义 Dataset 在训练期间完成格式解析。
- **原文：**五类 COCO 示例采用 `samples_per_gpu=2` 和 `workers_per_gpu=2`，训练、验证、测试均配置 `type=dataset_type`、`classes=classes` 以及各自 `ann_file`。
- **原文：**文本格式示例中，`000001.jpg` 尺寸为 `1280 720`、包含 `2` 条框；`000002.jpg` 同样为 `1280 720`、包含 `3` 条框。每条标注前 `4` 项被加入 `bboxes`，第 `5` 项被加入 `labels`。
- **原文：**底层 `Dataset_A` 被包装后仍放入包装器的 `dataset` 字典，并继续使用 `train_pipeline`。
- **原文：**没有给出训练耗时、精度提升、吞吐率等 benchmark 数字，也未给出具体 AP 数值；关于实例分割仅说明 COCO 格式支持 mask AP 评测。
- **原文未说明：**中间格式中 `bboxes` 的具体坐标排列顺序，也未解释自定义文本标签 `1`、`2`、`3` 如何与 `CLASSES` 元组建立对应关系。
- **原文示例存在两处字面不一致：**
  1. 文本格式被描述为 `annotation.txt`，配置示例却使用 `ann_file='image_list.txt'`。
  2. `load_annotations` 在 `if ann_line != '#': continue` 后仍对作为分隔符的 `ann_line` 执行 `split(' ')`；按所贴代码字面运行，会得到非数值内容并与后续 `float(ann)` 不一致。原文没有给出修正后的实现。
- 所给原文在第一种 `ConcatDataset` 配置中途截断，其余两种拼接方式没有提供，不能据原文补写。

## 【表格解读】

原文无表格。

文中的 JSON 字典、Python 数据集类和配置字典均以代码块形式展示，不属于 Markdown 表格或参数对照表。

## 【公式解读】

原文无公式。

`(n, 4)`、`(n,)`、`(k, 4)` 和 `(k,)` 是 NumPy 数组形状描述，不是数学公式。

## 【关联】

- `CocoDataset` 和 `VOCDataset` 是实现自定义数据解析方法的参考数据集类，分别对应在线读取 COCO 与 VOC 标注的路线。
- `tools/convert_datasets/cityscapes.py` 位于适配流程上游，负责将 Cityscapes 数据转换为现有格式；对应的微调配置则位于下游配置体系。
- `tools/convert_datasets/pascal_voc.py` 是离线转换的参考实现，转换后的中间标注可交给 `CustomDataset`。
- 自定义 `MyDataset` 中，`mmcv.list_from_file` 负责读取文本，`DATASETS` 注册器让配置能够通过 `type='MyDataset'` 找到实现，`CustomDataset` 提供基类能力，`numpy` 负责生成规定类型和形状的数组。
- 内部链接 [`../../mmdet/datasets/dataset_wrappers.py`](../../mmdet/datasets/dataset_wrappers.py) 指向数据集包装器源码；原文档将其作为 `RepeatDataset` 和 `ClassBalancedDataset` 具体行为的进一步实现参考。
- 配置层是格式适配与训练/评测之间的衔接点：包装器不替换基础数据集，而是包住包含 `type`、标注和 `pipeline` 的原始数据集配置。

## 【使用方法】

### 1. 使用已转换的 COCO 数据集

原文推荐的配置形式为：

```python
dataset_type = 'CocoDataset'
classes = ('a', 'b', 'c', 'd', 'e')

data = dict(
    samples_per_gpu=2,
    workers_per_gpu=2,
    train=dict(
        type=dataset_type,
        classes=classes,
        ann_file='path/to/your/train/data',
        ...),
    val=dict(
        type=dataset_type,
        classes=classes,
        ann_file='path/to/your/val/data',
        ...),
    test=dict(
        type=dataset_type,
        classes=classes,
        ann_file='path/to/your/test/data',
        ...))
```

主要配置项是 `type`、`classes`、`ann_file` 和各数据集的 `pipeline`。

### 2. 使用中间格式

先将标注保存为 pickle 或 JSON，再通过 `CustomDataset` 读取。典型自定义数据集需要：

- 继承 `CustomDataset`。
- 注册到 `DATASETS`。
- 实现 `load_annotations(self, ann_file)`。
- 实现 `get_ann_info(self, idx)`。

### 3. 注册文本格式数据集

原文给出的配置入口为：

```python
dataset_A_train = dict(
    type='MyDataset',
    ann_file = 'image_list.txt',
    pipeline=train_pipeline
)
```

实际启用时，应将 `ann_file` 与所创建解析器读取的标注文件对应起来。原文同时提到 `annotation.txt` 和 `image_list.txt`，两者并不一致。

### 4. 使用数据集包装器

重复数据集：

```python
dataset_A_train = dict(
    type='RepeatDataset',
    times=N,
    dataset=dict(
        type='Dataset_A',
        ...
        pipeline=train_pipeline
    )
)
```

类别均衡采样：

```python
dataset_A_train = dict(
    type='ClassBalancedDataset',
    oversample_thr=1e-3,
    dataset=dict(
        type='Dataset_A',
        ...
        pipeline=train_pipeline
    )
)
```

拼接同类数据集：

```python
dataset_A_train = dict(
    type='Dataset_A',
    ann_file=['anno_file_1', 'anno_file_2'],
    pipeline=train_pipeline
)
```

若将拼接结果作为整体评测，原文要求设置：

```python
separate_eval=False
```

原文未涉及安装、数据转换或训练启动所用的 shell 命令，仅提供 Python 数据集实现与配置写法。
