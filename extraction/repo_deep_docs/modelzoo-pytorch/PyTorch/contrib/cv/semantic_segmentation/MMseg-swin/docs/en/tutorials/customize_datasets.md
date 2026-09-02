# Tutorial 2: Customize Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/en/tutorials/customize_datasets.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/en/tutorials/customize_datasets.md

# 一体化深度解读:MMseg-swin 教程文档「Customize Datasets」

---

## 【定位】

本文档系统阐述了 MMSegmentation 中**数据集自定义与配置**的完整方法论,覆盖数据配置结构、文件夹级数据集组织、数据集混合(Repeat / Concatenate / Multi-image Mix)三大定制路径,目标是为开发者提供将自有数据接入训练管线或组合多源数据进行数据增强的统一规范。

---

## 【技术要点】

1. **数据配置核心字段**:使用 `data` 字典统一管理数据集与数据加载器,关键字段包括 `train / val / test`(各阶段数据集实例配置)、`samples_per_gpu`(每 GPU 单批次样本数)、`workers_per_gpu`(每 GPU 加载子进程数)。
2. **Batch Size 推算规则**:`batch_size = gpu_number × samples_per_gpu`;文档示例中 8 卡 DDP 训练 + `samples_per_gpu=4` ⇒ `batch_size=16`;`workers_per_gpu=0` 表示在主进程加载。
3. **Dataloader 配置两套语法**(v0.24.1 前后兼容):旧版只能使用全局 dataloader 字段;v0.24.1 起支持 `train_dataloader / val_dataloader / test_dataloader` 独立配置,且**专用配置优先级高于全局配置**。
4. **默认行为差异**:训练阶段 dataloader 默认 `shuffle=True, drop_last=True`;验证/测试阶段默认 `shuffle=False, drop_last=False`;测试/验证阶段 `samples_per_gpu` 默认 `1`,**当前不支持 batch inference**。
5. **文件夹数据集组织约定**:固定目录结构 `my_dataset/{img_dir, ann_dir}/{train, val}/`,通过**相同文件名后缀**自动匹配图像-标注对;通过 `split` 参数 + split txt 实现样本子集筛选。
6. **数据集混合三类机制**:`RepeatDataset`(以 `times=N` 包裹原数据集实现重复采样)、配置级 Concat(同一数据集类型下多 `ann_dir` / 多 `split` 列表化、或在 `train` 字段使用列表连接不同数据集)、`MultiImageMixDataset`(作为包装器与 `Mosaic` / `mixup` 等多图混合增强协同)。

---

## 【关键机制与数据】

### 数据流与优先级

(原文:)训练 / 验证 / 测试数据集实例通过 `config` 与 `build and registry` 机制构建。当同时存在全局 dataloader 字段(`samples_per_gpu / workers_per_gpu / shuffle`)与专用 `train_dataloader / val_dataloader / test_dataloader` 时,**专用配置优先级更高**——例如原文示例中,全局 `samples_per_gpu=4, workers_per_gpu=4, shuffle=True` 与 `val_dataloader=dict(samples_per_gpu=1, workers_per_gpu=4, shuffle=False)` 并存时,单卡训练 batch_size 为 `4`(并打乱),而验证 / 测试 batch_size 为 `1`(不打乱)。

### 文件夹数据集匹配机制

(原文:)训练对的构成规则——`img_dir/train/xxx{img_suffix}` 与 `ann_dir/train/xxx{seg_map_suffix}` 因**后缀文件名相同**自动配对。`split` 参数用于进一步筛选:split txt 中列出的前缀(如 `xxx`, `zzz`)决定加载哪些子集。原文强调**标注图像形状为 (H, W),像素值必须落在 `[0, num_classes - 1]` 范围内**,并推荐使用 Pillow 的 `'P'`(palette)模式创建带颜色的标注图像。

### Repeat 机制

(原文:)通过 `RepeatDataset` 包装器以 `times=N` 控制原数据集的重复次数,常用于类别不均衡场景下的过采样。

### Concatenate 双路径

(原文:)路径 A——同类数据集(同 type)下将 `ann_dir` 或 `split` 设为列表实现拼接;当两者同时为列表时,按**位置一一对应**(如 `ann_dir_1` 对应 `split_1.txt`)。
路径 B——异类数据集时,直接将多个 dataset config 组成 Python 列表赋值给 `train` 字段,`val / test` 仍为单一数据集。

### Multi-image Mix 机制

(原文:)`MultiImageMixDataset` 是多图混合数据增强(如 mosaic / mixup)的容器;在 train_pipeline 中典型用法为 `RandomMosaic(prob=1)` 配合 `Resize` / `RandomFlip` / `Normalize` / `DefaultFormatBundle` / `Collect(keys=['img', 'gt_semantic_seg', ...])` 流水线。(注:原文在 `Collect` 行截断,具体采集键未完整给出。)

### 默认数值锚点(原文明确给出)

- 8 GPU + `samples_per_gpu=4` ⇒ `batch_size = 8 × 4 = 16`
- `workers_per_gpu = 0` ⇒ 主进程加载
- `samples_per_gpu` 测试 / 验证默认 = 1
- v0.24.1 起引入独立 dataloader 配置
- `shuffle=True, drop_last=True`(训练默认);`shuffle=False, drop_last=False`(验证/测试默认)

---

## 【表格解读】

**原文无表格。** 文档全部通过 Python 配置代码块与目录树代码块表达配置语义,未出现结构化表格。

---

## 【公式解读】

**原文无公式。** 文档中存在一处算术表达(非 LaTeX 公式):"`batch_size` is `8*4=16`",即 `batch_size = num_gpus × samples_per_gpu`,已在上文「关键机制与数据」中按原文数字逐字保留并解释。

---

## 【关联】

文档明确引用了 mmcv 框架的两个机制作为构建基础(以下为外链,非本仓库内部链接):

- **[`config`](https://github.com/open-mmlab/mmcv/blob/master/docs/en/understand_mmcv/config.md)** —— 数据集实例通过该机制由 `data.train / val / test` 字段构建,即"用配置驱动对象实例化"。
- **[`build and registry`](https://github.com/open-mmlab/mmcv/blob/master/docs/en/understand_mmcv/registry.md)** —— `type='ADE20KDataset'` 等字符串通过注册表机制反查到对应 Dataset 类,实现解耦。
- **[`Pillow P 模式`](https://pillow.readthedocs.io/en/stable/handbook/concepts.html#palette)** —— 标注图像的创建方式(调色板模式)。
- **`train_pipeline / test_pipeline`** —— 数据集实例与处理流水线之间的衔接字段,贯穿数据增强(`Resize / RandomFlip / Normalize / DefaultFormatBundle / Collect`)与数据集定义。
- **v0.24.1 版本兼容性** —— 与下游使用 `train_dataloader / val_dataloader / test_dataloader` 的训练脚本存在版本耦合。

(文末未提供本仓库内部的其他 tutorial / API 链接。)

---

## 【使用方法】

### 启用方式总览(原文逐项保留)

**1) 数据配置最小完整示例:**

```python
data = dict(
    samples_per_gpu=4,
    workers_per_gpu=4,
    train=dict(type='ADE20KDataset', data_root='data/ade/ADEChallengeData2016',
               img_dir='images/training', ann_dir='annotations/training',
               pipeline=train_pipeline),
    val=dict(type='ADE20KDataset', data_root='data/ade/ADEChallengeData2016',
             img_dir='images/validation', ann_dir='annotations/validation',
             pipeline=test_pipeline),
    test=dict(type='ADE20KDataset', data_root='data/ade/ADEChallengeData2016',
              img_dir='images/validation', ann_dir='annotations/validation',
              pipeline=test_pipeline))
```

**2) 推荐(v0.24.1+)专用 dataloader 配置:**

```python
data = dict(
    train=dict(type='xxx', ...),
    val=dict(type='xxx', ...),
    test=dict(type='xxx', ...),
    train_dataloader=dict(samples_per_gpu=4, workers_per_gpu=4, shuffle=True),
    val_dataloader=dict(samples_per_gpu=1, workers_per_gpu=4, shuffle=False),
    test_dataloader=dict(samples_per_gpu=1, workers_per_gpu=4, shuffle=False))
```

**3) 文件夹数据集启用三步:**
- 按 `data/my_dataset/{img_dir, ann_dir}/{train, val}/` 结构组织文件;
- 在 dataset config 中指定 `data_root`、`img_dir`、`ann_dir`,可选 `split='split_xxx.txt'`;
- 标注图像使用 Pillow `'P'` 模式创建,像素值 ∈ `[0, num_classes - 1]`。

**4) Repeat Dataset 配置:**

```python
dataset_A_train = dict(
    type='RepeatDataset', times=N,
    dataset=dict(type='Dataset_A', ..., pipeline=train_pipeline))
```

**5) 同类 Concat(多 ann_dir / 多 split / 两者同时):**

```python
dataset_A_train = dict(
    type='Dataset_A', img_dir='img_dir',
    ann_dir=['anno_dir_1', 'anno_dir_2'],
    split=['split_1.txt', 'split_2.txt'],
    pipeline=train_pipeline)
```

**6) 异类 Concat(在 `train` 字段以列表合并):**

```python
data = dict(
    imgs_per_gpu=2, workers_per_gpu=2,
    train=[dataset_A_train, dataset_B_train],
    val=dataset_A_val, test=dataset_A_test)
```

**7) Multi-image Mix(Mosaic 流水线示例):**

```python
train_pipeline = [
    dict(type='RandomMosaic', prob=1),
    dict(type='Resize', img_scale=(1024, 512), keep_ratio=True),
    dict(type='RandomFlip', prob=0.5),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_semantic_seg', ...])  # 原文截断
]
```

**注意事项(原文标注):**
- `samples_per_gpu` 仅对训练生效;测试 / 验证阶段使用 `test_dataloader / val_dataloader` 独立设置;
- v0.24.1 之前除 `train / val / test / samples_per_gpu / workers_per_gpu` 外的 `data` 键都视作 PyTorch `DataLoader` 的 kwargs,且三阶段共享同一组参数;
- `Mosaic` 示例在原文中配置不完整(`Collect` 行被截断),启用时需参照 `MultiImageMixDataset` 的标准 pipeline 模板补全。
