# Tutorial 3: Customize Data Pipelines

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/GFocalV2/docs/tutorials/data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/GFocalV2/docs/tutorials/data_pipeline.md

# GFocalV2 教程 3 数据流水线自定义深度解读

## 【定位】
本文档是 MMDetection（GFocalV2 贡献代码目录下）的 **Tutorial 3：Customize Data Pipelines**，围绕目标检测中"数据准备流水线如何组织、字段如何流转、如何扩展"三大问题，给出一套基于 dict-in / dict-out 的可插拔机制说明。

## 【技术要点】

1. **整体范式**：数据装载使用 `Dataset` + `DataLoader`（多 worker 模式），`Dataset` 返回一个 dict，其键-值直接对应模型 `forward` 方法的参数；流水线由顺序的操作组成，每一步接收 dict 并返回 dict。
2. **变长数据处理**：由于检测中图像大小、bbox 大小不固定，**原文** "we introduce a new `DataContainer` type in MMCV to help collect and distribute data of different size" — 即通过 MMCV 的 `DataContainer` 来收纳和分发变长张量（详见 mmcv/parallel/data_container.py）。
3. **四大类操作**（**原文**："categorized into data loading, pre-processing, formatting and test-time augmentation"）：(a) 数据加载 LoadImageFromFile / LoadAnnotations / LoadProposals；(b) 预处理 Resize / RandomFlip / Pad / RandomCrop / Normalize / SegRescale / PhotoMetricDistortion / Expand / MinIoURandomCrop / Corrupt；(c) 格式化 ToTensor / ImageToTensor / Transpose / ToDataContainer / DefaultFormatBundle / Collect；(d) 测试时增强 MultiScaleFlipAug。
4. **字段操作语义**：流水线上每个操作可执行三类动作 — `add`（新增键，图中标记为绿色）、`update`（更新已有键，图中标记为橙色）、`remove`（如 `Collect` 会移除 `keys` 之外的字段）。
5. **流水线与数据集解耦**：**原文** "The data preparation pipeline and the dataset is decomposed. Usually a dataset defines how to process the annotations and a data pipeline defines all the steps to prepare a data dict."
6. **自定义注册机制**：通过 `mmdet.datasets.PIPELINES` 注册表 + `@PIPELINES.register_module()` 装饰器把新类加入流水线，写完 → import → 在 config 中以 `dict(type='MyTransform')` 引用即可。

## 【关键机制与数据】

**工作原理与数据流**（以原文 Faster R-CNN 训练流水线为例）：

```
原始图像 + 标注
  ↓ LoadImageFromFile     →  add: img, img_shape, ori_shape
  ↓ LoadAnnotations       →  add: gt_bboxes, gt_bboxes_ignore, gt_labels, gt_masks, gt_semantic_seg, bbox_fields, mask_fields
  ↓ Resize                →  update: img/img_shape + *bbox_fields/*mask_fields/*seg_fields
  ↓ RandomFlip            →  add: flip；update: img + 全部 *_fields
  ↓ Normalize             →  add: img_norm_cfg；update: img
  ↓ Pad                   →  update: img, pad_shape
  ↓ DefaultFormatBundle   →  update: img/proposals/gt_* 系列（统一成 DataContainer/Tensor）
  ↓ Collect               →  add: img_meta；保留 keys=[img, gt_bboxes, gt_labels]，其余全部 remove
  ↓ 送入 model.forward(img, gt_bboxes, gt_labels, img_meta=...)
```

> **图中色块的含义**（**原文**）：蓝色 = 流水线操作；绿色 = 操作新增的键；橙色 = 操作更新的键。

**关键参数（**原文**）**：

| 用途 | 参数值（原文） |
|------|---------------|
| 图像归一化均值 | `mean=[123.675, 116.28, 103.53]` |
| 图像归一化方差 | `std=[58.395, 57.12, 57.375]` |
| RGB 通道顺序 | `to_rgb=True` |
| Resize 目标尺寸 | `img_scale=(1333, 800)`，`keep_ratio=True` |
| 随机水平翻转 | `flip_ratio=0.5` |
| Pad 对齐因子 | `size_divisor=32` |
| Collect 保留键 | `keys=['img', 'gt_bboxes', 'gt_labels']` |

测试流水线以 `MultiScaleFlipAug` 包裹：内部 `flip=False`、`img_scale=(1333, 800)`、内部子流水线 `Resize(keep_ratio=True) → RandomFlip → Normalize → Pad(size_divisor=32) → ImageToTensor(keys=['img']) → Collect(keys=['img'])`。

各操作对 dict 字段的具体修改（**原文**，按四类组织）：

- **Data loading**：`LoadImageFromFile` add `img, img_shape, ori_shape`；`LoadAnnotations` add `gt_bboxes, gt_bboxes_ignore, gt_labels, gt_masks, gt_semantic_seg, bbox_fields, mask_fields`；`LoadProposals` add `proposals`。
- **Pre-processing**：`Resize` add `scale, scale_idx, pad_shape, scale_factor, keep_ratio` / update `img, img_shape, *bbox_fields, *mask_fields, *seg_fields`；`RandomFlip` add `flip` / update `img, *bbox_fields, *mask_fields, *seg_fields`；`Pad` add `pad_fixed_size, pad_size_divisor` / update `img, pad_shape, *mask_fields, *seg_fields`；`RandomCrop` update `img, pad_shape, gt_bboxes, gt_labels, gt_masks, *bbox_fields`；`Normalize` add `img_norm_cfg` / update `img`；`SegRescale` update `gt_semantic_seg`；`PhotoMetricDistortion` update `img`；`Expand` update `img, gt_bboxes`；`MinIoURandomCrop` update `img, gt_bboxes, gt_labels`；`Corrupt` update `img`。
- **Formatting**：`ToTensor / ImageToTensor / Transpose` update `keys` 指定字段；`ToDataContainer` update `fields` 指定字段；`DefaultFormatBundle` update `img, proposals, gt_bboxes, gt_bboxes_ignore, gt_labels, gt_masks, gt_semantic_seg`；`Collect` add `img_meta`（内容由 `meta_keys` 决定）/ remove 除 `keys` 指定外的所有键。
- **Test-time augmentation**：`MultiScaleFlipAug`（多尺度+翻转的推理增强容器）。

## 【表格解读】
原文无表格（所有可配置项与字段效应均以嵌套 bullet 列表 + Python 代码块呈现，未出现 markdown 表格结构）。

## 【公式解读】
原文无公式（亦无伪代码形式的数学表达式，仅含 dict / list 字面量与 Python 调用片段）。

## 【关联】

- **上游依赖 — MMCV**：文档将 `DataContainer` 的设计与实现显式外链至 `https://github.com/open-mmlab/mmcv/blob/master/mmcv/parallel/data_container.py`，表明流水线对"变长张量"的统一打包完全复用 MMCV 的并行原语。
- **同级模块 — `mmdet.datasets.PIPELINES` 注册表**：所有内置操作（`LoadImageFromFile`、`Resize`、`Normalize`、`DefaultFormatBundle`、`Collect` 等）以及用户自定义类都通过 `mmdet.datasets.PIPELINES` 注册表管理；自定义类必须使用 `@PIPELINES.register_module()` 装饰并以字符串 `type` 在 config 中被查到。
- **下游消费方**：流水线的最终产物（`img, gt_bboxes, gt_labels, ...` 加 `img_meta`）作为关键字参数直接送入模型 `forward`，因此流水线的字段集合**必须**与对应检测模型 `forward` 的形参对齐（这也是 GFocalV2 与同一仓库内其他检测器贡献能够共享流水线配置文件的根本原因）。
- **同系列教程**：本文档为 Tutorial 3，承接 Tutorial（关于 config / 自定义模型）之后，与本仓其他基于 MMDetection 的检测/分割模块（同一 PyTorch/contrib/cv/detection 树）共用相同的流水线语法。

> （文末内部链接信息显示无内部锚点链接可供引用。）

## 【使用方法】

**自定义一个流水线的三步流程**（**原文**）：
1. 在任意 .py 文件（如 `my_pipeline.py`）中实现新类 —— 输入 dict、返回 dict，并通过 `@PIPELINES.register_module()` 注册：
   ```python
   from mmdet.datasets import PIPELINES

   @PIPELINES.register_module()
   class MyTransform:
       def __call__(self, results):
           results['dummy'] = True
           return results
   ```
2. 在使用处导入：
   ```python
   from .my_pipeline import MyTransform
   ```
3. 在 config 文件中以字符串类型引用：
   ```python
   img_norm_cfg = dict(
       mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
   train_pipeline = [
       dict(type='LoadImageFromFile'),
       dict(type='LoadAnnotations', with_bbox=True),
       dict(type='Resize', img_scale=(1333, 800), keep_ratio=True),
       dict(type='RandomFlip', flip_ratio=0.5),
       dict(type='Normalize', **img_norm_cfg),
       dict(type='Pad', size_divisor=32),
       dict(type='MyTransform'),                 # ← 新增的自定义步骤
       dict(type='DefaultFormatBundle'),
       dict(type='Collect', keys=['img', 'gt_bboxes', 'gt_labels']),
   ]
   ```

**可直接调整的常用配置项**（**原文**）：
- `img_norm_cfg.mean/std/to_rgb` —— 图像归一化超参；
- `Resize.img_scale`、`keep_ratio` —— 输入尺度与是否保宽高比；
- `RandomFlip.flip_ratio` —— 翻转概率；
- `Pad.size_divisor` —— padding 对齐因子（须与主干网络的下采样倍数一致）；
- `Collect.keys` / `Collect.meta_keys` —— 控制最终送给 `forward` 的数据字段与元信息字段；
- `MultiScaleFlipAug.img_scale / flip / transforms` —— 控制测试时增强的多尺度范围与是否翻转。
