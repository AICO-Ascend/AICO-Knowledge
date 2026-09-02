# 教程 2: 自定义数据集

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs_zh-CN/tutorials/customize_datasets.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs_zh-CN/tutorials/customize_datasets.md

# 一体化深度解读：教程 2: 自定义数据集

## 【定位】

这篇文档是 MMSegmentation（在此仓库中服务于 DeeplabV3_for_Pytorch 路径下的语义分割任务）中"自定义数据集"的官方教程，旨在指导用户通过**目录重组**与**数据集混合（Repeat/Concat）**两种方式，把自己的数据接入 MMSegmentation 的训练/验证流程，从而不必修改框架源码即可训练/评估自定义分割数据。

---

## 【技术要点】

1. **目录组织约定**：自定义数据集需按 `img_dir`（图像）+ `ann_dir`（标注）的双目录结构组织，并在各自下面再分 `train` / `val` 两个子目录；图像与标注按**同样首缀（prefix）**配对形成训练对。

2. **`split` 文本过滤机制**：通过提供 `split` 文本（每行一个样本前缀，如 `xxx`、`zzz`），仅加载列在其中的前缀对应的文件，可单独指定或与目录配合使用。

3. **标注格式硬约束**：标注图与图像形状一致 (H, W)，像素值必须落在 `[0, num_classes - 1]` 范围内；允许使用 Pillow 的 `'P'`（调色板 Palette）模式制作带颜色的标注。

4. **`RepeatDataset` 包装器**：以 `type='RepeatDataset'` 包装原数据集配置，通过 `times=N` 控制重复次数，使原数据被复用 N 次参与训练。

5. **同类型数据集 Concat（3 种拼接粒度）**：
   - 拼接两个 `ann_dir` 文件夹（`ann_dir = ['anno_dir_1', 'anno_dir_2']`）；
   - 拼接两个 `split` 文件列表（`split = ['split_1.txt', 'split_2.txt']`）；
   - 同时拼接 `ann_dir` 列表 + `split` 列表（一对一对应，例如 `ann_dir_1`↔`split_1.txt`，`ann_dir_2`↔`split_2.txt`）。

6. **异类型数据集 Concat**：在 `data` 字典中将多个数据集对象放入同一个 `train` 列表中，并配合 `imgs_per_gpu`、`workers_per_gpu` 等公共字段；`val` / `test` 字段仍接受单一数据集配置。

---

## 【关键机制与数据】

**工作原理与数据流（基于原文推断与原文表述）：**

- **样本配对原理**：框架基于"同前缀"约定，将 `img_dir/{split}/<prefix>{img_suffix}` 与 `ann_dir/{split}/<prefix>{seg_map_suffix}` 视为一对；`split` 文本本质上是一个**白名单过滤器**，决定了实际参与训练的样本集合。

- **`RepeatDataset` 机制**：它是一个包装（wrapper）类，将原 `Dataset_A` 的样本在每次 epoch 中按 `times=N` 的设定**重复采样**，相当于在不增加新数据的前提下提升该数据集在训练中的曝光权重。

- **Concat 机制**：无论是同类型多目录/多 split，还是异类型多个数据集对象，本质都是把"数据集实例"汇聚到一个列表中；框架按列表顺序依次迭代每个数据集的样本，实现**样本级别的混合**。同类型拼接还支持在 `ann_dir` 与 `split` 之间建立"目录-列表"一一对应，从而把两组标注/列表视为同一逻辑训练集。

- **性能数据**：原文中未给出任何性能数字（mIoU、速度、显存等），故此处不杜撰。

---

## 【表格解读】

**原文无表格。** 原文通过目录树（`none` 代码块）和若干 Python 配置代码块来表达结构，但未出现 markdown 表格形式的关键参数表/性能对比/配置项汇总。

---

## 【公式解读】

**原文无公式。** 文中未出现任何 LaTeX 或伪代码形式的数学公式。

---

## 【关联】

**原文无内部链接。** 文中没有列出指向仓库其他章节/模块的内部链接（如回到索引、前往下一节等），但从内容上下文可识别其上下游关系：

- **上游/前置**：本教程是 MMSegmentation 用户教程系列的"教程 2"，其前置是关于框架基本使用的入门文档；本教程涉及到的 `pipeline`、`img_dir`、`ann_dir`、`split`、`num_classes` 等，是更上层"配置文件说明"文档中的关键字段。
- **下游/承接**：本教程仅讲"数据组织与混合"，未涉及标注工具、数据增强（`pipeline`）内部细节，也未涉及具体模型的训练启动命令；这些分别在 MMSegmentation 文档体系的"教程 3：自定义数据流水线（pipeline）"、"教程 4：训练与测试"等模块中展开。
- **同名类库引用**：文中以纯字符串形式提到了 `RepeatDataset` 与 `Dataset_A`/`Dataset_B`，属于 MMSegmentation 中 `mmseg.datasets` 模块内的数据集包装器与自定义数据集类。

---

## 【使用方法】

下面所有内容均**逐字保留原文**的配置写法，便于直接复用。

### 方式一：通过目录重组自定义数据集

按以下目录结构组织数据（原文 `none` 代码块）：

```none
├── data
│   ├── my_dataset
│   │   ├── img_dir
│   │   │   ├── train
│   │   │   │   ├── xxx{img_suffix}
│   │   │   │   ├── yyy{img_suffix}
│   │   │   │   ├── zzz{img_suffix}
│   │   │   ├── val
│   │   ├── ann_dir
│   │   │   ├── train
│   │   │   │   ├── xxx{seg_map_suffix}
│   │   │   │   ├── yyy{seg_map_suffix}
│   │   │   │   ├── zzz{seg_map_suffix}
│   │   │   ├── val
```

`split` 文本示例（原文）：

```none
xxx
zzz
```

加载结果（原文）：仅有以下 4 个文件被加载——
`data/my_dataset/img_dir/train/xxx{img_suffix}`、
`data/my_dataset/img_dir/train/zzz{img_suffix}`、
`data/my_dataset/ann_dir/train/xxx{seg_map_suffix}`、
`data/my_dataset/ann_dir/train/zzz{seg_map_suffix}`。

标注硬约束（原文）：标注与图像同形状 (H, W)，像素值范围 `[0, num_classes - 1]`；可用 Pillow `'P'` 模式制作带颜色标注（原文链接：<https://pillow.readthedocs.io/en/stable/handbook/concepts.html#palette>）。

### 方式二：通过混合数据自定义数据集

**重复（Repeat）数据集**（原文 Python 配置）：

```python
dataset_A_train = dict(
        type='RepeatDataset',
        times=N,
        dataset=dict(  # 这是 Dataset_A 数据集的原始配置
            type='Dataset_A',
            ...
            pipeline=train_pipeline
        )
    )
```

**拼接（Concat）数据集 — 方式 1（同类型数据集）**（原文 Python 配置）：

1. 拼接两个标注文件夹 `ann_dir`：

```python
dataset_A_train = dict(
    type='Dataset_A',
    img_dir = 'img_dir',
    ann_dir = ['anno_dir_1', 'anno_dir_2'],
    pipeline=train_pipeline
)
```

2. 拼接两个 `split` 文件列表：

```python
dataset_A_train = dict(
    type='Dataset_A',
    img_dir = 'img_dir',
    ann_dir = 'anno_dir',
    split = ['split_1.txt', 'split_2.txt'],
    pipeline=train_pipeline
)
```

3. 同时拼接 `ann_dir` 与 `split`（一对一对应：`ann_dir_1`↔`split_1.txt`，`ann_dir_2`↔`split_2.txt`）：

```python
dataset_A_train = dict(
    type='Dataset_A',
    img_dir = 'img_dir',
    ann_dir = ['anno_dir_1', 'anno_dir_2'],
    split = ['split_1.txt', 'split_2.txt'],
    pipeline=train_pipeline
)
```

**拼接（Concat）数据集 — 方式 2（不同类型数据集）**（原文 Python 配置）：

```python
dataset_A_train = dict()
dataset_B_train = dict()

data = dict(
    imgs_per_gpu=2,
    workers_per_gpu=2,
    train = [
        dataset_A_train,
        dataset_B_train
    ],
    val = dataset_A_val,
    test = dataset_A_test
    )
```

**复杂组合示例：分别重复再拼接**（原文 Python 配置）：

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
dataset_A_val = dict(
    ...
    pipeline=test_pipeline
)
dataset_A_test = dict(
    ...
    pipeline=test_pipeline
)
dataset_B_train = dict(
    type='RepeatDataset',
    times=M,
    dataset=dict(
        type='Dataset_B',
        ...
        pipeline=train_pipeline
    )
)
data = dict(
    imgs_per_gpu=2,
    workers_per_gpu=2,
    train = [
        dataset_A_train,
        dataset_B_train
    ],
    val = dataset_A_val,
    test = dataset_A_test
)
```

**启用方式（原文未涉及）**：原文未给出具体的命令行启动方式（如 `python tools/train.py` 之类）或环境变量/超参启动说明，因此"如何运行训练"不在本教程覆盖之内。
