# Tutorial 3: Customize Data Pipelines

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/en/tutorials/data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/en/tutorials/data_pipeline.md

# 深度解读：Tutorial 3: Customize Data Pipelines

---

## 【定位】

这篇文档解决"在 MMSegmentation 中如何理解、设计与扩展自定义数据预处理流水线（Data Pipeline）"的问题——即以 PSPNet 为示例，阐明从原始数据到模型输入的转换链路如何由可插拔的 transform 序列组成，并指导开发者如何注册并接入自定义 transform。

---

## 【技术要点】

1. **基础数据加载范式**：遵循 `Dataset` + `DataLoader` 多 worker 加载约定，`Dataset` 返回一个 dict，其字段对应模型 `forward` 方法的参数；为应对语义分割中样本尺寸不一致的问题，MMCV 引入 `DataContainer` 类型来收集与分发变长数据。

2. **数据集与流水线的解耦**：Dataset 负责标注处理，Data Pipeline 负责所有数据 dict 的准备步骤；一个 pipeline 是一个操作序列，每个操作"输入一个 dict，输出一个 dict"，传给下一级 transform。

3. **四类操作划分**：操作按用途分为 **Data loading**、**Pre-processing**、**Formatting**、**Test-time augmentation** 四大类。文档以 PSPNet 为示例给出了 train_pipeline 与 test_pipeline 的完整定义。

4. **PSPNet 关键配置数值（原文逐字保留）**：
   - 图像归一化：`mean=[123.675, 116.28, 103.53]`, `std=[58.395, 57.12, 57.375]`, `to_rgb=True`
   - 训练裁剪尺寸：`crop_size = (512, 1024)`
   - 训练 `Resize`：`img_scale=(2048, 1024)`, `ratio_range=(0.5, 2.0)`
   - 训练 `RandomCrop`：`crop_size=crop_size`, `cat_max_ratio=0.75`
   - 训练 `RandomFlip`：`flip_ratio=0.5`
   - 训练 `Pad`：`size=crop_size`, `pad_val=0`, `seg_pad_val=255`
   - 测试 `MultiScaleFlipAug`：`img_scale=(2048, 1024)`, `flip=False`，子 transforms 含 `Resize(keep_ratio=True)`、`RandomFlip`、`Normalize`、`ImageToTensor(keys=['img'])`、`Collect(keys=['img'])`
   - 训练 `Collect`：`keys=['img', 'gt_semantic_seg']`

5. **每个操作的 dict 字段影响**：文档以"add / update / remove"三类别精确刻画每个 transform 对数据 dict 字段的副作用（详见下节）。

6. **自定义流水线的三步接入法**：(a) 在任意文件（如 `my_pipeline.py`）中以 `@PIPELINES.register_module()` 注册新 transform 类，使其 `__call__(results)` 返回 dict；(b) `from .my_pipeline import MyTransform` 导入；(c) 在 config 中通过 `dict(type='MyTransform')` 插入流水线任意位置。

---

## 【关键机制与数据】

### 工作原理与数据流（基于原文）

**原文：** "we use `Dataset` and `DataLoader` for data loading with multiple workers. `Dataset` returns a dict of data items corresponding the arguments of models' forward method."

→ 数据从磁盘经 `Dataset` 读出后被组装成 dict，dict 的 key 必须与模型 forward 参数对齐；多 worker 并行由 `DataLoader` 提供。

**原文：** "Since the data in semantic segmentation may not be the same size, we introduce a new `DataContainer` type in MMCV to help collect and distribute data of different size."

→ 因语义分割各样本 H×W 不同，常规 tensor 难以表达；`DataContainer` 作为容器承载变长数据，由分布式/收集逻辑自行处理对齐。原文链接：`https://github.com/open-mmlab/mmcv/blob/master/mmcv/parallel/data_container.py`。

**原文：** "The data preparation pipeline and the dataset is decomposed. ... A pipeline consists of a sequence of operations. Each operation takes a dict as input and also output a dict for the next transform."

→ 流水线是**单向串联**：op_i(results_i) → results_{i+1}，整条链路形如 results₀ → op₁ → op₂ → … → op_n → results_n，results_n 即模型 forward 的输入。

**原文（PSPNet train_pipeline 链路）：**
```
LoadImageFromFile → LoadAnnotations → Resize(2048×1024, ratio 0.5~2.0)
→ RandomCrop(512×1024, cat_max_ratio=0.75) → RandomFlip(0.5)
→ PhotoMetricDistortion → Normalize(mean/std) → Pad(512×1024, pad_val=0, seg_pad_val=255)
→ DefaultFormatBundle → Collect(['img','gt_semantic_seg'])
```

**原文（test_pipeline 链路）：**
```
LoadImageFromFile → MultiScaleFlipAug(scale=2048×1024, flip=False)
   └→ Resize(keep_ratio=True) → RandomFlip → Normalize
      → ImageToTensor(keys=['img']) → Collect(keys=['img'])
```

### 各 transform 对 dict 字段的精确副作用（原文逐字复述）

| 类别 | 操作 | 字段副作用（原文） |
|---|---|---|
| Data loading | `LoadImageFromFile` | add: img, img_shape, ori_shape |
| Data loading | `LoadAnnotations` | add: gt_semantic_seg, seg_fields |
| Pre-processing | `Resize` | add: scale, scale_idx, pad_shape, scale_factor, keep_ratio；update: img, img_shape, *seg_fields |
| Pre-processing | `RandomFlip` | add: flip；update: img, *seg_fields |
| Pre-processing | `Pad` | add: pad_fixed_size, pad_size_divisor；update: img, pad_shape, *seg_fields |
| Pre-processing | `RandomCrop` | update: img, pad_shape, *seg_fields |
| Pre-processing | `Normalize` | add: img_norm_cfg；update: img |
| Pre-processing | `SegRescale` | update: gt_semantic_seg |
| Pre-processing | `PhotoMetricDistortion` | update: img |
| Formatting | `ToTensor` | update: specified by `keys` |
| Formatting | `ImageToTensor` | update: specified by `keys` |
| Formatting | `Transpose` | update: specified by `keys` |
| Formatting | `ToDataContainer` | update: specified by `fields` |
| Formatting | `DefaultFormatBundle` | update: img, gt_semantic_seg |
| Formatting | `Collect` | add: img_meta（其 keys 由 `meta_keys` 指定）；**remove**: 除 `keys` 指定外所有其他 keys |
| Test-time augmentation | `MultiScaleFlipAug` | （原文未列字段副作用） |

> 原文无性能/吞吐/精度等量化 benchmark 数据。

---

## 【表格解读】

**原文无表格**（markdown 表格意义上的表格不存在）。原文以 Python 代码块形式呈现 pipeline 字典，并以上方 3 列语义表（类别 / 操作 / 字段副作用）枚举各 transform 的影响。该语义表已在上节"关键机制与数据"中逐字还原。

---

## 【公式解读】

**原文无公式**（既无 LaTeX 数学式，也无伪代码形式的算法表达式）。

---

## 【关联】

文档自身**未提供文末内部链接**（"内部链接: (无)"）。但从行文中可识别出以下关联节点：

- **外部依赖：MMCV**
  - 通过 `DataContainer` 类型（位于 `mmcv/parallel/data_container.py`）承载变长语义分割样本；
  - 注册机制 `@PIPELINES.register_module()` 依赖 MMCV 的 registry 体系（即 `mmseg.datasets.PIPELINES`）。
- **下游模块：模型 forward**
  - pipeline 最终输出的 dict key 必须与模型 `forward` 方法签名一致（原文："`Dataset` returns a dict of data items corresponding the arguments of models' forward method"）。
- **示例模型：PSPNet**
  - 文档以 PSPNet 的 train_pipeline / test_pipeline 作为典型配置蓝本；该 pipeline 与 `BiseNetV1_for_PyTorch` 同属 MMSegmentation 生态，故配置项（mean/std、crop、scale 等）通常可直接复用或微调。
- **配置层**
  - 自定义 transform 通过 `dict(type='MyTransform')` 嵌入 config 任意位置，与 mmseg 的"配置即代码"风格一致。
- **Test-time augmentation 链路**
  - `MultiScaleFlipAug` 内部又嵌套一条子 pipeline（Resize→Flip→Normalize→ImageToTensor→Collect），与训练 pipeline 共享若干 transform 但出口不同（仅保留 `img`）。

---

## 【使用方法】

以下命令/配置均**逐字取自原文**：

### 1. 定义归一化与裁剪参数（PSPNet 示例）

```python
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
crop_size = (512, 1024)
```

### 2. 配置 train_pipeline

```python
train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations'),
    dict(type='Resize', img_scale=(2048, 1024), ratio_range=(0.5, 2.0)),
    dict(type='RandomCrop', crop_size=crop_size, cat_max_ratio=0.75),
    dict(type='RandomFlip', flip_ratio=0.5),
    dict(type='PhotoMetricDistortion'),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='Pad', size=crop_size, pad_val=0, seg_pad_val=255),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_semantic_seg']),
]
```

### 3. 配置 test_pipeline

```python
test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=(2048, 1024),
        # img_ratios=[0.5, 0.75, 1.0, 1.25, 1.5, 1.75],
        flip=False,
        transforms=[
            dict(type='Resize', keep_ratio=True),
            dict(type='RandomFlip'),
            dict(type='Normalize', **img_norm_cfg),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img']),
        ])
]
```

### 4. 自定义 transform 三步接入

**(a) 编写并注册**（`my_pipeline.py`，原文逐字）：

```python
from mmseg.datasets import PIPELINES

@PIPELINES.register_module()
class MyTransform:

    def __call__(self, results):
        results['dummy'] = True
        return results
```

**(b) 导入**：

```python
from .my_pipeline import MyTransform
```

**(c) 在 config 中插入**（位于 `Pad` 之后、`DefaultFormatBundle` 之前，原文示例）：

```python
train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations'),
    dict(type='Resize', img_scale=(2048, 1024), ratio_range=(0.5, 2.0)),
    dict(type='RandomCrop', crop_size=crop_size, cat_max_ratio=0.75),
    dict(type='RandomFlip', flip_ratio=0.5),
    dict(type='PhotoMetricDistortion'),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='Pad', size=crop_size, pad_val=0, seg_pad_val=255),
    dict(type='MyTransform'),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_semantic_seg']),
]
```

> 原文未涉及具体的训练启动命令（如 `tools/train.py` 调用方式）、环境变量或多机配置；亦未提供 benchmark/精度复现脚本入口。
