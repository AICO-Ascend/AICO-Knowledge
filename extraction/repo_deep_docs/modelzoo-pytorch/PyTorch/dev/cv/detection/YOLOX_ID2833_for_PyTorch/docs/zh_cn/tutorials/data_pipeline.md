# 教程 3: 自定义数据预处理流程

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/zh_cn/tutorials/data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/zh_cn/tutorials/data_pipeline.md

# 一体化深度解读：自定义数据预处理流程

---

## 【定位】

本教程是面向基于 `mmdet` 的目标检测框架（此处为 YOLOX）的「数据预处理流程（Data Pipeline）」定制指南，解决「如何在不重写数据加载逻辑的情况下，灵活插入、替换或扩展逐操作（per-transform）的数据处理行为」这一核心问题，使训练 / 推理阶段的数据流可配置、可扩展、可被 registry 装饰器接管。

---

## 【技术要点】

1. **数据流程与数据集解耦**：数据集类只负责解析标注，**数据流程**（由一组 transform 操作组成）才负责把样本字典转换成模型 `forward` 所需的字典；每个 transform 都接收 dict、输出 dict。
2. **使用 `DataContainer` 处理变长输入**：由于目标检测图像尺度不同，`MMCV` 引入 `DataContainer` 类来**收集与分发**（collect & dispatch）不同大小的输入数据。
3. **操作四分类**：流程中的 transform 归入四大类——**数据加载（Data loading）**、**预处理（Pre-processing）**、**格式变化（Formatting）**、**测试时数据增强（Test-time augmentation）**；每类对 dict 字段的"增加 / 更新 / 移除"语义清晰。
4. **典型 Faster R-CNN 训练管线示例**：`img_norm_cfg = dict(mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)`；`Resize` 使用 `img_scale=(1333, 800), keep_ratio=True`；`RandomFlip` 的 `flip_ratio=0.5`；`Pad` 的 `size_divisor=32`。
5. **自定义 transform 三步法**：在 `my_pipeline.py` 中以 `@PIPELINES.register_module()` 注册；以一个 dict 为输入、输出 dict；在配置中通过 `custom_imports = dict(imports=['path.to.my_pipeline'], allow_failed_imports=False)` 确保模块被加载，再在管线中以 `dict(type='MyTransform', p=0.2)` 形式插入。
6. **可视化辅助工具**：使用 `tools/misc/browse_dataset.py` 可直观浏览检测数据集或将增强后的图像保存到指定目录，用法参见[日志分析](../useful_tools.md)。

---

## 【关键机制与数据】

- **工作原理（pipeline figure，原文配图 `../../../resources/data_pipeline.png`）**：蓝色块是数据处理操作，结果字典经过每个操作后，会**新增键（绿色）**或**更新已有键（橙色）**。
- **数据流形态**：每个 transform 内部以 `__call__(self, results)` 形式被调用，输入输出都是 `dict`，因此链式可组合；变量尺寸的张量由 `DataContainer` 包装以便 `DataLoader` 跨进程分发。
- **dict 字段语义（按类别，原文）**：
  - **Data loading**：
    - `LoadImageFromFile` —— 增加 `img, img_shape, ori_shape`
    - `LoadAnnotations` —— 增加 `gt_bboxes, gt_bboxes_ignore, gt_labels, gt_masks, gt_semantic_seg, bbox_fields, mask_fields`
    - `LoadProposals` —— 增加 `proposals`
  - **Pre-processing**：每个操作对 `*bbox_fields / *mask_fields / *seg_fields` 这种"通配字段"做同步更新，保证 bbox / mask / seg 与图像几何变换一致：
    - `Resize` —— 增加 `scale, scale_idx, pad_shape, scale_factor, keep_ratio`；更新 `img, img_shape, *bbox_fields, *mask_fields, *seg_fields`
    - `RandomFlip` —— 增加 `flip`；更新 `img, *bbox_fields, *mask_fields, *seg_fields`
    - `Pad` —— 增加 `pad_fixed_size, pad_size_divisor`；更新 `img, pad_shape, *mask_fields, *seg_fields`
    - `RandomCrop` —— 更新 `img, pad_shape, gt_bboxes, gt_labels, gt_masks, *bbox_fields`
    - `Normalize` —— 增加 `img_norm_cfg`；更新 `img`
    - `SegRescale` —— 更新 `gt_semantic_seg`
    - `PhotoMetricDistortion` —— 更新 `img`
    - `Expand` —— 更新 `img, gt_bboxes`
    - `MinIoURandomCrop` —— 更新 `img, gt_bboxes, gt_labels`
    - `Corrupt` —— 更新 `img`
  - **Formatting**：负责把 numpy 转为 tensor、收拢字段：
    - `ToTensor / ImageToTensor / Transpose / ToDataContainer` —— 更新由 `keys` 指定
    - `DefaultFormatBundle` —— 更新 `img, proposals, gt_bboxes, gt_bboxes_ignore, gt_labels, gt_masks, gt_semantic_seg`
    - `Collect` —— 增加 `img_metas`（其字段由 `meta_keys` 指定）；**移除除 `keys` 指定外的所有键**
  - **Test-time augmentation**：`MultiScaleFlipAug`，内嵌 `Resize / RandomFlip / Normalize / Pad / ImageToTensor / Collect` 形成"多尺度 + 翻转"增强。
- **数值参数**：`mean=[123.675, 116.28, 103.53]`、`std=[58.395, 57.12, 57.375]`、`to_rgb=True`、`img_scale=(1333, 800)`、`keep_ratio=True`、`flip_ratio=0.5`、`size_divisor=32`、`MyTransform` 的 `p=0.2`。

---

## 【表格解读】

原文无表格。文档采用"`操作 → dict 字段影响`"的小节列表代替了表格（例如 "增加：img, img_shape, ori_shape"），未以 markdown 表格形式呈现任何参数 / 性能 / 配置项对比。

---

## 【公式解读】

原文无公式。文档全部内容由文字、Python 配置代码块和配图说明构成，未出现任何数学公式或伪代码式表达式。

---

## 【关联】

- **与数据加载层的关系**：依赖 PyTorch 的 `Dataset / DataLoader` 多进程加载机制，并经由 `MMCV` 的 `DataContainer` 处理目标检测中尺寸不一的输入；`DataContainer` 的实现细节链接到 https://github.com/open-mmlab/mmcv/blob/master/mmcv/parallel/data_container.py 。
- **与数据集类的关系**：标注的解析归数据集类（Dataset）所有，**transform 流程独立于数据集**，二者通过 `results` dict 解耦。
- **与下游 model / head 的关系**：流程最终输出的字典对应 model `forward` 方法的各个参数；`Collect` 操作通过白名单 `keys` 决定哪些字段进入模型，`img_metas` 等元信息由 `meta_keys` 抽取。
- **与可视化 / 日志分析工具的关系**：文末给出的 `tools/misc/browse_dataset.py` 进一步链接到[日志分析](../useful_tools.md)，提示数据流程的可视化调试与训练日志分析属于同一工具集。
- **与配置体系的关系**：自定义 transform 通过 `custom_imports` 注入到注册表，从而可被 `Config` 解析为 `dict(type='MyTransform', p=0.2)` 的标准 cfg 写法所引用。

---

## 【使用方法】

1. **编写自定义 transform**（原文示例）：
   ```python
   import random
   from mmdet.datasets import PIPELINES

   @PIPELINES.register_module()
   class MyTransform:
       def __init__(self, p=0.5):
           self.p = p
       def __call__(self, results):
           if random.random() > self.p:
               results['dummy'] = True
           return results
   ```
   - 必须以 `@PIPELINES.register_module()` 注册。
   - 入参 / 出参都是 `dict`（即 `results`）。

2. **在配置中启用**（原文示例）：
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
   - `custom_imports.imports` 指向自定义文件所在路径，确保训练脚本能正确导入新增模块。
   - `allow_failed_imports=False` 表示导入失败即报错（严格模式）。
   - 新增的 `MyTransform` 以 `dict(type='MyTransform', p=0.2)` 形式插入到 `Normalize / Pad` 与 `DefaultFormatBundle` 之间。

3. **可视化数据增强结果**（原文有则写）：使用 `tools/misc/browse_dataset.py` 可在终端直观浏览检测数据集（图像与标注信息），或将图像保存到指定目录；具体使用方法参见 [日志分析](../useful_tools.md)。
