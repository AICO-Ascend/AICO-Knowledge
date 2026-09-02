# Tutorial 3: Customize Data Pipelines

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/tutorials/data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/tutorials/data_pipeline.md

## 【定位】

这篇文档说明检测任务中数据流水线的设计、字段变更协议、典型 Faster R-CNN 配置以及自定义流水线的注册和使用方法。

## 【技术要点】

1. **基础数据接口**  
   数据通过 `Dataset` 和支持多 worker 的 `DataLoader` 加载；`Dataset` 返回字典，字典内容对应模型 `forward` 方法所需的参数。

2. **异构尺寸处理**  
   检测数据中的图像尺寸、真值框尺寸等可能不同，因此引入 MMCV 的 `DataContainer`，用于收集和分发不同尺寸的数据。

3. **流水线结构**  
   数据集主要负责注解处理，流水线负责把数据字典加工成模型输入；流水线由按顺序执行的变换组成，每项操作都以字典为输入并返回字典。操作可以增加、更新或删除字段，按用途分为数据加载、预处理、格式化和测试时增强四类。

4. **Faster R-CNN 训练流水线**  
   依次执行图像与注解加载、尺寸调整、随机翻转、归一化、补齐、格式化及字段收集：  
   - `img_scale=(1333, 800)`、`keep_ratio=True`  
   - `mean=[123.675, 116.28, 103.53]`  
   - `std=[58.395, 57.12, 57.375]`、`to_rgb=True`  
   - `flip_ratio=0.5`  
   - `size_divisor=32`

5. **Faster R-CNN 测试流水线**  
   由 `MultiScaleFlipAug` 包装缩放、随机翻转、归一化、补齐、张量化与收集操作，外部设置 `img_scale=(1333, 800)`、`flip=False`；由于未给 `flip_ratio`，其中的 `RandomFlip` 使用默认配置。

6. **自定义流水线**  
   自定义类需通过 `PIPELINES.register_module()` 注册、导入模块，再在配置中以 `dict(type='MyTransform')` 加入流水线。原文示例会向返回字典增加 `dummy=True`。

## 【关键机制与数据】

原文：数据集与数据准备流水线是解耦的。通常，数据集定义注解如何处理；流水线则定义准备数据字典所需的全部步骤。

原文：整体数据流是“`Dataset` 返回字典 → 流水线操作逐项传递字典 → 格式化后形成模型输入”。每个操作都可以增加新字段、更新已有字段，或者为后续模型准备特定格式。

原文：MMCV 的 `DataContainer` 专门处理检测数据中尺寸不一致的问题，使 `DataLoader` 能够收集并向模型分发图像、真值框等不同尺寸的数据。

原文：典型字段变化如下：

- 数据加载  
  - `LoadImageFromFile` 增加 `img, img_shape, ori_shape`
  - `LoadAnnotations` 增加 `gt_bboxes, gt_bboxes_ignore, gt_labels, gt_masks, gt_semantic_seg, bbox_fields, mask_fields`
  - `LoadProposals` 增加 `proposals`
- 预处理  
  - `Resize` 增加 `scale, scale_idx, pad_shape, scale_factor, keep_ratio`，并更新 `img, img_shape` 及 `*bbox_fields, *mask_fields, *seg_fields`
  - `RandomFlip` 增加 `flip`，并更新图像、框、掩码和分割字段
  - `Pad` 增加 `pad_fixed_size, pad_size_divisor`，并更新 `img, pad_shape` 及相关掩码和分割字段
  - `Normalize` 增加 `img_norm_cfg` 并更新 `img`
  - `RandomCrop`、`PhotoMetricDistortion`、`Expand`、`MinIoURandomCrop`、`Corrupt` 等操作更新各自处理的图像或标注字段
- 格式化  
  - `ToTensor`、`ImageToTensor`、`Transpose` 根据指定键更新数据
  - `ToDataContainer` 根据指定 `fields` 更新字段
  - `DefaultFormatBundle` 更新 `img, proposals, gt_bboxes, gt_bboxes_ignore, gt_labels, gt_masks, gt_semantic_seg`
  - `Collect` 增加 `img_meta`，并移除除 `keys` 指定字段之外的所有其他字段
- 测试时增强  
  - 使用 `MultiScaleFlipAug` 组织多尺度与翻转相关的测试变换；原文未进一步列出其字段增删协议。

原文：训练流水线最终只收集 `img, gt_bboxes, gt_labels`；测试流水线在增强操作内部将图像转换为张量，并只收集 `img`。这种差异使训练字典包含监督标注，而测试字典保留模型执行所需字段。

原文：文档未提供吞吐量、训练耗时、精度或基准测试结果。

## 【表格解读】

原文无表格。文中的操作及其字段变化均以列表形式呈现，没有参数表、性能对比表或配置项表格。

## 【公式解读】

原文无公式。文档仅定义和举例 `DataContainer`、流水线操作及字典字段，没有数学公式、LaTeX 表达式或伪代码公式。

## 【关联】

原文：没有文末内部链接；以下关系来自正文中的显式引用和模块交互：

- **`Dataset`、`DataLoader` 与模型**：数据集产生字典形式的数据项，经 `DataLoader` 加载后进入流水线，最终按照模型 `forward` 方法所需的数据结构组织。
- **数据集与流水线**：数据集侧重注解处理，流水线侧重图像加载、变换、格式化和字段收集，两者职责分离。
- **`DataContainer` 与 MMCV**：原文通过外部链接指向 MMCV 的 `data_container.py`，说明异构尺寸数据的收集和分发依赖 MMCV 提供的容器机制。
- **格式模块与模型输入**：`ImageToTensor`、`Transpose`、`DefaultFormatBundle` 和 `Collect` 共同把中间字典转换为模型可消费的输入表示。
- **测试增强与测试流水线**：`MultiScaleFlipAug` 位于测试流水线的外层，内部复用 `Resize`、`RandomFlip`、`Normalize`、`Pad` 等操作。
- **注册表、模块与配置**：自定义类先注册到 `mmdet.datasets.PIPELINES`，再通过 `from .my_pipeline import MyTransform` 导入，最后以 `type='MyTransform'` 写入配置，使自定义操作进入执行链。

## 【使用方法】

原文：通过配置字典声明流水线，不需要直接实例化每个操作。Faster R-CNN 训练配置示例如下：

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
    dict(type='MyTransform'),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_bboxes', 'gt_labels']),
]
```

原文：自定义流水线需定义一个接收 `results`、处理后返回 `results` 的类，并通过注册装饰器注册：

```python
from mmdet.datasets import PIPELINES

@PIPELINES.register_module()
class MyTransform:

    def __call__(self, results):
        results['dummy'] = True
        return results
```

原文：随后导入该类：

```python
from .my_pipeline import MyTransform
```

并将 `dict(type='MyTransform')` 插入目标流水线。测试时增强则配置为 `MultiScaleFlipAug`，并通过 `transforms` 列表声明内部操作。

原文未提供命令行启动方式。
