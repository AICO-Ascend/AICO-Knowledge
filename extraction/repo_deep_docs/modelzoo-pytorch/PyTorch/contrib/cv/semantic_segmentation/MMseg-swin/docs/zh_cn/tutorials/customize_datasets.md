# 教程 2: 自定义数据集

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/zh_cn/tutorials/customize_datasets.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/zh_cn/tutorials/customize_datasets.md

# 一体化深度解读:MMseg-swin 自定义数据集教程

## 【定位】

本教程解决 **如何在 MMSegmentation 语义分割框架中接入自定义数据集** 的问题,系统介绍了 **数据重组织**、**数据集包装(重复/拼接)** 与 **多图混合数据増广** 三类定制手段,使得用户无需修改框架源码即可将自己的数据或组合数据送入训练流程。

## 【技术要点】

1. **目录式数据组织约定**:自定义数据集按 `data/my_dataset/{img_dir,ann_dir}/{train,val}` 二级目录摆放,图像与标注按"同名前缀"配对(如 `xxx{img_suffix}` 与 `xxx{seg_map_suffix}`)。

2. **基于 split 文本的子集筛选**:通过 `split` 参数指向一个纯文本文件,逐行列出被允许加载的样本前缀;未列入前缀的样本不会进入 `Dataset` 迭代器。

3. **标注格式硬约束**:标注图像形状必须为 `(H, W)`,像素值必须落在 **`[0, num_classes - 1]`** 闭区间内;若需要彩色的可视化标注,可借助 Pillow 的 **`'P'` 模式(Palette 调色板模式)** 构造带颜色的标注。

4. **`RepeatDataset` 包装**:通过 `dict(type='RepeatDataset', times=N, dataset=...)` 将原数据集整体重复 `N` 次,用于在不平衡或多源数据下人为放大某数据集的采样权重。

5. **两类拼接策略**:
   - **同类异标注**:`ann_dir`、`split` 字段均可接收字符串列表(长度对齐),以"逐项对应"方式横向扩展样本池。
   - **异类拼接**:在顶层 `data=dict(train=[dataset_A_train, dataset_B_train], ...)` 处将多个独立数据集配置放入同一个 `train` 列表,框架按顺序拼接样本迭代。

6. **`MultiImageMixDataset` 多图混合**:作为 wrapper 与 `RandomMosaic`/`MixUp` 等多图増广配合,把多个样本融合为一张送入后续 `Resize` → `RandomFlip` → `Normalize` → `DefaultFormatBundle` → `Collect` 的标准管线。

## 【关键机制与数据】

### 数据流与配对机制(原文)
- **配对依据**:`img_dir` 与 `ann_dir` 中**同前缀**文件自动组成一个训练对(如 `xxx` 前缀同时出现在两个目录)。
- **split 过滤原理**:若给定 `split` 文本,文件前缀必须出现在该文本中才被加载。例如 `split` 为 `xxx / zzz` 时,只有 `xxx{img_suffix}`、`zzz{img_suffix}` 及其对应标注被加载,而 `yyy` 被排除。
- **标注形状与数值**:`(H, W)` 与原图一致,像素取值范围 `[0, num_classes - 1]`;Pillow `'P'` 模式用于生成带调色板的彩色标注。

### RepeatDataset 数据流(原文)
- 原始 `Dataset_A` 的完整配置作为 `dataset` 字段传入,`RepeatDataset` 作为最外层包装;迭代时会顺序产出 `Dataset_A` 的全部样本 `N` 遍,实现采样权重的等比放大。

### ConcatDataset 数据流(原文)
- **方式一(同类异标注)**:`ann_dir` 与 `split` 均可为字符串列表,列表长度对齐时按下标一一对应(`ann_dir_1` ↔ `split_1.txt`,`ann_dir_2` ↔ `split_2.txt`)。
- **方式二(异类拼接)**:`dataset_A_train` 与 `dataset_B_train` 各自是完整的 dict 配置;在顶层 `data` 的 `train` 字段以 Python 列表形式同时收纳,`val`/`test` 各自保持单数据集配置。

### MultiImageMixDataset 数据流(原文)
- 外层 `train_dataset` 为 `MultiImageMixDataset`,其内嵌 `dataset` 提供基础样本加载(`LoadImageFromFile` + `LoadAnnotations`)。
- 外层 `pipeline`(`train_pipeline`)以 `RandomMosaic`(prob=1)打头,做四图拼接増广;后续 `Resize`(`img_scale=(1024, 512)`,`keep_ratio=True`)→ `RandomFlip`(`prob=0.5`)→ `Normalize`(`**img_norm_cfg`)→ `DefaultFormatBundle`→ `Collect(keys=['img','gt_semantic_seg'])` 完成从多图融合到模型输入张量的收束。
- 顶层 `data` 中 `imgs_per_gpu=2`、`workers_per_gpu=2`,表示每个 GPU 同时送 2 张样本(融合图)、并启 2 个数据加载 worker。

> 原文未提供基准性能数字(如 mIoU/Iters-per-second),本文不做臆测。

## 【表格解读】

**原文无表格**。原文以代码块和目录树代替表格组织信息,关键配置项已在前文【技术要点】与【关键机制与数据】中以条目化形式完整覆盖。

## 【公式解读】

**原文无公式**。教程中出现的"公式型"内容仅为目录树与 Python 配置字典语法,不存在 LaTeX 数学公式或伪代码表达式。

## 【关联】

- **与数据管线(`pipeline`)的关系**:本教程中的 `train_pipeline` / `test_pipeline` 与 `RandomMosaic`、`Resize`、`RandomFlip`、`Normalize`、`DefaultFormatBundle`、`Collect` 等算子属于上游"教程 4:自定义数据流水线(Customize Data Pipelines)"、`教程 5:増广(Album) 与 Mosaic/MixUp 増广`所描述模块的**下游消费方**。
- **与配置文件体系的关系**:`dataset_A_train / dataset_B_train / data` 的组织方式直接对应仓库根目录的 `configs/_base_/datasets/` 下 `*.py` 配置模板,本教程是其**用户级覆写范式**。
- **与模型(`Swin-Transformer`)的关系**:本教程定义的 `train_dataset` 与 `MultiImageMixDataset` 是 Swin/MMseg 训练入口的输入端,改动此处即可让同一套 `Swin`/`UperNet` 模型在不同自定义/混合数据集上训练,而无需改动模型代码本身。
- **`reduce_zero_label=False`**:作为 `MultiImageMixDataset` 内嵌 dataset 的关键参数,与"标注像素值范围 `[0, num_classes - 1]`"中的 `0` 号类别处理策略直接耦合;若背景类 `0` 需忽略则改为 `True`。
- **`palette` 与 `classes`**:与 `教程 1:自定义标注` 中"调色板与类别名"约定一致,确保可视化结果与训练语义对齐。

## 【使用方法】

### 方法 A —— 纯目录组织(原文给出)
```text
├── data
│   ├── my_dataset
│   │   ├── img_dir
│   │   │   ├── train/{xxx,yyy,zzz}{img_suffix}
│   │   │   ├── val/...
│   │   ├── ann_dir
│   │   │   ├── train/{xxx,yyy,zzz}{seg_map_suffix}
│   │   │   ├── val/...
```
- `split` 文本(可选):
  ```text
  xxx
  zzz
  ```
- 像素值范围:`[0, num_classes - 1]`;彩色标注使用 Pillow `'P'` 模式。

### 方法 B —— `RepeatDataset` 重复(原文给出)
```python
dataset_A_train = dict(
    type='RepeatDataset',
    times=N,
    dataset=dict(type='Dataset_A', ..., pipeline=train_pipeline))
```

### 方法 C —— 同类拼接(原文给出)
- 仅拼 `ann_dir`:`ann_dir=['anno_dir_1','anno_dir_2']`
- 仅拼 `split`:`split=['split_1.txt','split_2.txt']`
- 同时拼二者:`ann_dir=[...]` 与 `split=[...]` 列表**等长对齐**,按下标配对。

### 方法 D —— 异类拼接(原文给出)
```python
dataset_A_train = dict(...)
dataset_B_train = dict(...)

data = dict(
    imgs_per_gpu=2, workers_per_gpu=2,
    train=[dataset_A_train, dataset_B_train],
    val=dataset_A_val, test=dataset_A_test)
```

### 方法 E —— 多图混合増广(原文给出)
```python
train_pipeline = [
    dict(type='RandomMosaic', prob=1),
    dict(type='Resize', img_scale=(1024, 512), keep_ratio=True),
    dict(type='RandomFlip', prob=0.5),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img','gt_semantic_seg']),
]

train_dataset = dict(
    type='MultiImageMixDataset',
    dataset=dict(
        classes=classes, palette=palette, type=dataset_type,
        reduce_zero_label=False,
        img_dir=data_root + "images/train",
        ann_dir=data_root + "annotations/train",
        pipeline=[dict(type='LoadImageFromFile'),
                  dict(type='LoadAnnotations')]),
    pipeline=train_pipeline)
```

> 原文未涉及命令行启动入口与具体 CLI 参数(如 `python tools/train.py ...`),仅给出**配置层**用法;如需 CLI 调用方式请参考同仓库 `getting_started.md` 与 `train.md`(原文未列出)。
