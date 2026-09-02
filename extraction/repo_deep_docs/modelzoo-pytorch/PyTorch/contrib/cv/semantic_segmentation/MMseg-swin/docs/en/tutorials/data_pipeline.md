# Tutorial 3: Customize Data Pipelines

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/en/tutorials/data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/en/tutorials/data_pipeline.md

# 一体化深度解读：MMseg-swin Tutorial 3 — Customize Data Pipelines

---

## 【定位】

这篇文档解决**如何在 MMSegmentation 框架下理解、设计、并扩展语义分割任务的数据预处理流水线（data pipeline）**的问题——它既是 pipeline 设计原则的说明，也是新增自定义 transform 的三步操作指南，并以 PSPNet 流水线为示例展示了端到端的 train/test pipeline 配置。

---

## 【技术要点】

1. **基于 dict 的链式 pipeline 架构**：每个 transform 是一个「以 dict 为输入、以 dict 为输出」的操作，多个 transform 顺序串联构成 pipeline；`Dataset` 返回的 dict 键值需与模型 `forward` 方法的参数对齐。语义分割样本尺寸不一致，由 MMCV 的 `DataContainer` 类型协助收集与分发。
2. **Dataset 与 pipeline 解耦**：dataset 负责标注处理方式，data pipeline 负责从原始文件到模型输入的全部步骤；二者通过相同的 dict 协议解耦。
3. **四类 transform 分类**：data loading / pre-processing / formatting / test-time augmentation（TTA），每一类承担明确职责边界。
4. **PSPNet 完整 train/test pipeline 参数**：归一化采用 `mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True`；`crop_size=(512, 1024)`；Resize 用 `img_scale=(2048, 1024), ratio_range=(0.5, 2.0)`；RandomCrop 用 `cat_max_ratio=0.75`；RandomFlip 用 `flip_ratio=0.5`；Pad 用 `pad_val=0, seg_pad_val=255`；test 阶段用 `MultiScaleFlipAug`（默认 `flip=False`，内含 5 个子 transform）。
5. **每个 transform 显式声明对 dict 字段的影响**：用 `add` / `update` / `remove` 三类操作精确描述字段增删改，方便审计与调试。
6. **自定义 pipeline 的三步接入流程**：在文件中用 `@PIPELINES.register_module()` 注册类 → `from .my_pipeline import MyTransform` 导入 → 在 config 的 pipeline 列表中以 `dict(type='MyTransform')` 使用。

---

## 【关键机制与数据】

**工作原理（dict-in / dict-out 流水线机制）**：
- `Dataset` 与 `DataLoader` 配合多 worker 加载数据，`Dataset` 返回的 dict 键直接对应模型 `forward` 的参数名。
- 由于分割图与原图尺寸可能不同，引入了 MMCV 中的 `DataContainer`（[源码](https://github.com/open-mmlab/mmcv/blob/master/mmcv/parallel/data_container.py)）以承载可变尺寸数据。
- pipeline 由 operations 序列组成，**每个 operation 都以 dict 为输入并输出 dict**，下一阶段的 input 是上一阶段的 output，因此 pipeline 等价于一个 dict 上的「函数复合链」。

**数据流（按 PSPNet train_pipeline 顺序串联 10 步）**：
原文 train_pipeline 顺序为：`LoadImageFromFile → LoadAnnotations → Resize(img_scale=(2048,1024), ratio_range=(0.5,2.0)) → RandomCrop(crop_size=(512,1024), cat_max_ratio=0.75) → RandomFlip(flip_ratio=0.5) → PhotoMetricDistortion → Normalize(**img_norm_cfg) → Pad(size=(512,1024), pad_val=0, seg_pad_val=255) → DefaultFormatBundle → Collect(keys=['img','gt_semantic_seg'])`。
原文 test_pipeline 顺序为：`LoadImageFromFile → MultiScaleFlipAug(img_scale=(2048,1024), flip=False, transforms=[Resize(keep_ratio=True), RandomFlip, Normalize(**img_norm_cfg), ImageToTensor(keys=['img']), Collect(keys=['img'])])`。

**各 transform 对 dict 的精确字段影响**（原文按四类分组列出）：
- **Data loading**：`LoadImageFromFile` add `img, img_shape, ori_shape`；`LoadAnnotations` add `gt_semantic_seg, seg_fields`。
- **Pre-processing**：`Resize` add `scale, scale_idx, pad_shape, scale_factor, keep_ratio`，update `img, img_shape, *seg_fields`；`RandomFlip` add `flip`，update `img, *seg_fields`；`Pad` add `pad_fixed_size, pad_size_divisor`，update `img, pad_shape, *seg_fields`；`RandomCrop` update `img, pad_shape, *seg_fields`；`Normalize` add `img_norm_cfg`，update `img`；`SegRescale` update `gt_semantic_seg`；`PhotoMetricDistortion` update `img`。
- **Formatting**：`ToTensor` / `ImageToTensor` / `Transpose` update 由 `keys` 指定的字段；`ToDataContainer` update 由 `fields` 指定；`DefaultFormatBundle` update `img, gt_semantic_seg`；`Collect` add `img_meta`（其键由 `meta_keys` 指定），并 remove 除 `keys` 指定之外的所有键。
- **Test time augmentation**：`MultiScaleFlipAug`。

**性能/基准数据**：原文未给出具体数值指标或性能基准（属于 tutorial 类而非 benchmark 类文档），故无数据可标注。

---

## 【表格解读】

**原文无表格**（文档主体为分类列表与 Python 代码块，未呈现任何 markdown 或文本表格）。

---

## 【公式解读】

**原文无公式**（文档为 pipeline 设计说明与代码示例，未包含数学公式或伪代码公式段）。

---

## 【关联】

- **与 MMCV 的关系**：引入了 MMCV 中的 `DataContainer` 类型来处理语义分割中尺寸不一的数据，并链接到其 [源码位置](https://github.com/open-mmlab/mmcv/blob/master/mmcv/parallel/data_container.py)；`@PIPELINES.register_module()` 装饰器也是 MMCV 注册器机制的一部分，说明本 pipeline 系统是建立在 MMCV 注册/构建体系之上的。
- **与上游教程的关系**：作为 "Tutorial 3"，它处于 MMSegmentation 教程系列中"模型 → 数据"的实践侧——通常位于教程 1（config 基础）/教程 2（自定义模型）之后，为教程 4（自定义数据集/训练策略）等提供 pipeline 层基础。
- **与 config 体系的关系**：所有 pipeline 均以 Python list 形式在 config 文件中声明，每项为 `dict(type=..., ...)`，这与文档中"使用 config 文件"的扩展步骤一致；`Collect.meta_keys` 与 `Collect.keys` 两套参数配合，决定了 `img_meta` 与最终送往模型 forward 的键集合。
- **与下游模型 forward 的关系**：pipeline 末端 `Collect(keys=['img','gt_semantic_seg'])` 输出的 dict 键需要与模型 `forward` 方法的参数名（如 `img`、`gt_semantic_seg`）对齐，否则会因参数名不匹配报错——这是「`Dataset` 返回 dict 与模型 forward 参数对应」这一设计原则在 pipeline 末端的具象化。
- **上下游模块关系**：train 与 test pipeline **共享上游数据加载与基础变换**（`LoadImageFromFile`），但 test 末端通过 `MultiScaleFlipAug` 封装多尺度/翻转测试增强，其子 `transforms` 内嵌独立的 Normalize/Collect——这表明 train/test pipeline 在「数据加载 → 增强 → 收集」三段上既同构又有分支。
- **内部链接**：原文未给出内部链接，仅给出 1 个外部链接（MMCV DataContainer 源码）。

---

## 【使用方法】

**启用方式（自定义 pipeline 三步接入）**：

1. **在任意文件（如 `my_pipeline.py`）中编写新 transform**：以 dict 为输入、dict 为输出，并使用 `@PIPELINES.register_module()` 注册：
   ```python
   from mmseg.datasets import PIPELINES

   @PIPELINES.register_module()
   class MyTransform:
       def __call__(self, results):
           results['dummy'] = True
           return results
   ```

2. **导入该类**：
   ```python
   from .my_pipeline import MyTransform
   ```

3. **在 config 文件的 pipeline 列表中以 `dict(type='MyTransform')` 使用**（原文示例把 `MyTransform` 插入在 `Pad` 之后、`DefaultFormatBundle` 之前；归一化参数与 PSPNet 一致：`mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True`，`crop_size=(512, 1024)`，`img_scale=(2048, 1024)`）。

**关键配置项 / 参数速查（按原文 PSPNet 示例）**：
- `img_norm_cfg`：`mean=[123.675, 116.28, 103.53]`，`std=[58.395, 57.12, 57.375]`，`to_rgb=True`。
- `crop_size = (512, 1024)`：同时作为 RandomCrop 和 Pad 的目标尺寸。
- `Resize(img_scale=(2048, 1024), ratio_range=(0.5, 2.0))`：长边 2048、短边 1024，缩放比在 [0.5, 2.0] 区间随机采样。
- `RandomCrop(crop_size=crop_size, cat_max_ratio=0.75)`：单类最大占比 0.75。
- `RandomFlip(flip_ratio=0.5)`：50% 概率水平翻转。
- `Pad(size=crop_size, pad_val=0, seg_pad_val=255)`：图像 pad 值为 0，分割图 pad 值为 255（忽略标签约定）。
- `MultiScaleFlipAug(img_scale=(2048, 1024), flip=False)`：测试阶段多尺度翻转增强，`transforms` 字段可自定义子流水线；原文示例内嵌 `Resize(keep_ratio=True), RandomFlip, Normalize, ImageToTensor(keys=['img']), Collect(keys=['img'])`。
- `Collect(keys=[...], meta_keys=...)`：`keys` 决定保留哪些送模型，`meta_keys` 决定收集哪些元信息进 `img_meta`。

**命令**：原文未涉及任何 CLI / shell 命令（属纯 config + Python 接入方式）。
