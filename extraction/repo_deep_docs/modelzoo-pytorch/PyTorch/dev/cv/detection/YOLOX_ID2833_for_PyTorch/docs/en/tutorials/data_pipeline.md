# Tutorial 3: Customize Data Pipelines

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/data_pipeline.md

## 【定位】

这篇文档说明如何基于 `Dataset`、`DataLoader` 和由多个数据变换组成的 Pipeline，加载、预处理、格式化并收集不同尺寸的目标检测数据，同时支持通过注册自定义 `Transform` 扩展训练与测试流程。

## 【技术要点】

1. **基础数据接口与并行加载**  
   遵循典型 PyTorch/MMDetection 约定，使用 `Dataset` 加载数据，并通过支持多 worker 的 `DataLoader` 分发样本；`Dataset` 返回的字典字段与模型 `forward` 方法所需参数对应。

2. **变尺寸数据处理**  
   目标检测样本的图像尺寸、真实框尺寸等可能不同，因此引入 MMCV 的 `DataContainer`，用于收集和分发不同尺寸的数据。

3. **Pipeline 机制**  
   数据集与数据准备 Pipeline 相互解耦：数据集负责处理标注，Pipeline 则按顺序完成数据字典的构造。每个操作接收一个字典并输出一个新字典，可以新增、更新或删除字段。原文将操作划分为：
   - 数据加载：`LoadImageFromFile`、`LoadAnnotations`、`LoadProposals`
   - 预处理：缩放、翻转、填充、裁剪、归一化等
   - 格式化：`ToTensor`、`ImageToTensor`、`Transpose`、`ToDataContainer`、`DefaultFormatBundle`、`Collect`
   - 测试时增强：`MultiScaleFlipAug`

4. **Faster R-CNN 示例参数**  
   原文配置如下：
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
       dict(type='DefaultFormatBundle'),
       dict(type='Collect', keys=['img', 'gt_bboxes', 'gt_labels']),
   ]
   test_pipeline = [
       dict(type='LoadImageFromFile'),
       dict(
           type='MultiScaleFlipAug',
           img_scale=(1333, 800),
           flip=False,
           transforms=[
               dict(type='Resize', keep_ratio=True),
               dict(type='RandomFlip'),
               dict(type='Normalize', **img_norm_cfg),
               dict(type='Pad', size_divisor=32),
               dict(type='ImageToTensor', keys=['img']),
               dict(type='Collect', keys=['img']),
           ])
   ]
   ```
   训练流程包含图像与标注加载、按 `(1333, 800)` 等比缩放、以 `0.5` 概率随机翻转、按给定均值和标准差归一化、按 `32` 填充，再执行格式化与字段收集；测试流程将这些预处理步骤封装在 `MultiScaleFlipAug` 中。

5. **字段变更规则**  
   预处理操作既会操作主字段，也会同步处理登记在 `bbox_fields`、`mask_fields`、`seg_fields` 等字段列表中的关联字段。例如：
   - `Resize` 更新 `img`、`img_shape`、`*bbox_fields`、`*mask_fields`、`*seg_fields`
   - `RandomFlip` 更新 `img`、`*bbox_fields`、`*mask_fields`、`*seg_fields`
   - `Pad` 更新 `img`、`pad_shape`、`*mask_fields`、`*seg_fields`
   - `Collect` 新增 `img_meta`，并移除 `keys` 之外的所有其他字段
   - `DefaultFormatBundle` 格式化 `img`、`proposals`、`gt_bboxes`、`gt_bboxes_ignore`、`gt_labels`、`gt_masks`、`gt_semantic_seg`

6. **自定义 Pipeline**  
   自定义变换需要实现“接收字典、返回字典”的调用接口，并通过 `PIPELINES.register_module()` 注册。原文导入配置和插入方式为：
   ```python
   custom_imports = dict(imports=['path.to.my_pipeline'], allow_failed_imports=False)

   img_norm_cfg = dict(
       mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
   train_pipeline = [
       dict(type='LoadImageFromFile'),
       dict(type='LoadAnnotations', with_bbox=True),
       dict(type='Resize', img_scale=(1333, 800), keep_ratio=True),
       dict(type='RandomFlip', flip_ratio=0.5),
       dict(type='Normalize', **img_norm_cfg),
       dict(type='Pad', size_divisor=32),
       dict(type='MyTransform', p=0.2),
       dict(type='DefaultFormatBundle'),
       dict(type='Collect', keys=['img', 'gt_bboxes', 'gt_labels']),
   ]
   ```
   `MyTransform` 的 `p` 默认为 `0.5`；示例配置中使用 `p=0.2`。当 `random.random() > self.p` 时，该变换向 `results` 写入 `results['dummy'] = True`。

## 【关键机制与数据】

### 数据流

1. `Dataset` 根据原始图像和标注生成初始数据字典。
2. Pipeline 中的每个操作依次接收并处理该字典。
3. `LoadImageFromFile` 新增：
   - `img`
   - `img_shape`
   - `ori_shape`
4. `LoadAnnotations` 新增：
   - `gt_bboxes`
   - `gt_bboxes_ignore`
   - `gt_labels`
   - `gt_masks`
   - `gt_semantic_seg`
   - `bbox_fields`
   - `mask_fields`
5. 预处理阶段修改图像、真实框、掩码或语义分割字段，并记录缩放、翻转、填充和归一化信息。
6. 格式化阶段按照指定键或字段将相应数据转换为适合模型处理的形式。
7. `Collect` 构造 `img_meta`，同时清除未被收集的字段，使最终数据字典成为模型所需输入。
8. `DataLoader` 负责多 worker 数据分发；由于检测数据尺寸可能不同，`DataContainer` 用于承载和传递这些变尺寸数据。

**原文：** 文档没有提供吞吐量、加速比、显存占用、准确率等性能数据。

### 字段与操作协同

- `Resize`、`RandomFlip`、`Pad` 不仅更新图像，还会同步更新已经登记在 `bbox_fields`、`mask_fields` 或 `seg_fields` 中的关联字段。
- `RandomCrop` 会更新图像及真实框、标签、掩码等标注。
- `Normalize` 保存 `img_norm_cfg`，并更新 `img`。
- `DefaultFormatBundle` 对指定图像、候选框、真实框、标签、掩码和语义分割字段统一格式化。
- `Collect` 以 `keys` 作为最终保留集合，以 `meta_keys` 指定写入 `img_meta` 的元数据键。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

- `Dataset` 负责样本和标注的初始构造，Pipeline 负责把样本字典转换为模型输入；二者通过字典式中间结果衔接。
- `DataLoader` 位于数据分发层，支持多 worker；MMCV 的 `DataContainer` 则解决检测任务中数据尺寸不一致的问题。
- 各变换不是独立模块，而是共享同一个结果字典：前一个操作的新增字段可以成为后续操作的输入或处理对象。
- `DefaultFormatBundle` 和 `Collect` 位于 Pipeline 末端，将前面的图像及标注处理结果整理为模型实际消费的字段。
- `MultiScaleFlipAug` 将缩放、翻转、归一化、填充、张量化和字段收集组合为测试时增强流程。
- 自定义变换通过 `PIPELINES.register_module()` 接入 MMDetection Pipeline 体系，再由 `custom_imports` 导入配置并加入 `train_pipeline`。
- 可使用 `tools/misc/browse_dataset.py` 可视化数据增强输出，浏览图像与边界框标注，或将图像保存到指定目录；文末的内部链接为 [useful_tools](../useful_tools.md)。

## 【使用方法】

1. 在自定义文件（如 `my_pipeline.py`）中定义接收 `results` 并返回 `results` 的变换类。
2. 使用以下装饰器注册：
   ```python
   @PIPELINES.register_module()
   ```
3. 在配置文件中使用 `custom_imports` 导入模块：
   ```python
   custom_imports = dict(imports=['path.to.my_pipeline'], allow_failed_imports=False)
   ```
4. 通过类似下面的配置项启用：
   ```python
   dict(type='MyTransform', p=0.2)
   ```
5. 确保模块导入路径相对于训练脚本所在位置。
6. 使用 `tools/misc/browse_dataset.py` 查看增强后的图像和边界框标注；原文未提供该工具的具体命令参数。
