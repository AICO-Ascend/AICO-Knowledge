# Tutorial 3: Customize Data Pipelines

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs/tutorials/data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs/tutorials/data_pipeline.md

【定位】
这篇文档是 MMSeg 数据流水线（data pipeline）的定制教程，核心解决两个问题：①说明语义分割任务中"数据准备流水线与数据集解耦"的设计思路，并梳理流水线操作的分类（数据加载 / 预处理 / 格式化 / 测试时增强）及其对数据字典字段的增删改；②给出在 mmseg 中注册并使用自定义 pipeline 变换（transform）的标准步骤。

【技术要点】
- **数据加载机制**：基于 PyTorch `Dataset` + `DataLoader` 多 worker；`Dataset` 返回 dict，字段对应模型 `forward` 的参数。
- **变长数据容器**：因语义分割各样本尺寸不同，引入 MMCV 的 `DataContainer` 来收集和分发不同尺寸的数据。
- **流水线结构**：pipeline 由若干顺序操作组成，每步输入为 dict、输出也为 dict；操作分为 data loading、pre-processing、formatting、test-time augmentation 四类。
- **典型 PSPNet 训练流水线配置**：包含 `LoadImageFromFile`、`LoadAnnotations`、`Resize`、`RandomCrop`、`RandomFlip`、`PhotoMetricDistortion`、`Normalize`、`Pad`、`DefaultFormatBundle`、`Collect` 共 10 步。
- **关键超参与数值**：归一化采用 ImageNet 风格配置 `mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True`；`crop_size=(512, 1024)`；`Resize` 的 `img_scale=(2048, 1024)`、`ratio_range=(0.5, 2.0)`；`RandomFlip` 的 `flip_ratio=0.5`；`RandomCrop` 的 `cat_max_ratio=0.75`；`Pad` 的 `pad_val=0, seg_pad_val=255`。
- **自定义 pipeline 三步走**：①在 `my_pipeline.py` 中用 `@PIPELINES.register_module()` 装饰类；②从 `mmseg.datasets` 导入 `PIPELINES` 注册表并 `from .my_pipeline import MyTransform`；③在 config 文件的 pipeline 列表中以 `dict(type='MyTransform')` 形式插入。

【关键机制与数据】
**工作原理**：数据流从原始文件出发，每经过一步 transform，dict 字段按规则被 add / update / remove（详见下方分类列表）。原文四类操作的字段变化规则：
- **Data loading**（原文）：`LoadImageFromFile` → add `img, img_shape, ori_shape`；`LoadAnnotations` → add `gt_semantic_seg, seg_fields`。
- **Pre-processing**（原文）：`Resize` → add `scale, scale_idx, pad_shape, scale_factor, keep_ratio`，update `img, img_shape, *seg_fields`；`RandomFlip` → add `flip`，update `img, *seg_fields`；`Pad` → add `pad_fixed_size, pad_size_divisor`，update `img, pad_shape, *seg_fields`；`RandomCrop` → update `img, pad_shape, *seg_fields`；`Normalize` → add `img_norm_cfg`，update `img`；`SegRescale` → update `gt_semantic_seg`；`PhotoMetricDistortion` → update `img`。
- **Formatting**（原文）：`ToTensor` / `ImageToTensor` / `Transpose` → update 由 `keys` 指定；`ToDataContainer` → update 由 `fields` 指定；`DefaultFormatBundle` → update `img, gt_semantic_seg`；`Collect` → add `img_meta`（由 `meta_keys` 指定其子键），remove 除 `keys` 指定外的所有键。
- **Test time augmentation**（原文）：`MultiScaleFlipAug` 作为测试增强封装，内部嵌套 `Resize(keep_ratio=True) → RandomFlip → Normalize → ImageToTensor → Collect`。
- **性能/数值数据**：原文未提供基准训练指标或吞吐量数据，仅给出配置超参数（见上）。

【表格解读】
原文无表格。文档中操作的字段变化以分级标题 + 短列表形式呈现（每条以"add / update / remove: 字段名"形式列出），未使用 markdown 表格结构。

【公式解读】
原文无公式。文档以 Python 字典列表形式定义流水线配置，未出现数学公式或 LaTeX 表达式。

【关联】
- **上游框架依赖**：依赖 MMCV 提供 `DataContainer`（用于变长数据收集与分发）和 `DataLoader` 多 worker 加载机制；引用了 MMCV 仓库中 `mmcv/parallel/data_container.py` 作为 `DataContainer` 实现来源。
- **下游/同仓模块**：示例流水线以 PSPNet 为典型场景，所列操作（`Resize`、`RandomCrop`、`PhotoMetricDistortion` 等）属于 mmseg.datasets.pipelines 模块；通过 `@PIPELINES.register_module()` 装饰器将自定义类接入 `mmseg.datasets.PIPELINES` 注册表，从而在配置文件中可被 `type` 字段引用，与官方内置 pipeline 等价替换。
- **测试时分支**：训练流水线经过 `DefaultFormatBundle + Collect` 输出模型可直接消费的 dict；测试流水线则经 `MultiScaleFlipAug` 包装，提供多尺度+翻转增强后的推理输入。
- **内部链接**：本任务给定的"内部链接"为"无"，文档本身仅含一处外链（指向 MMCV `DataContainer` 源码）。

【使用方法】
- **启用自定义 pipeline 的标准流程**（原文给出三步）：
  1. 在任意文件（如 `my_pipeline.py`）中定义类，签名 `def __call__(self, results): ... return results`，并用 `@PIPELINES.register_module()` 装饰；示例类 `MyTransform` 在结果字典中新增 `dummy=True`。
  2. 在使用处 `from mmseg.datasets import PIPELINES`（确保触发注册），并 `from .my_pipeline import MyTransform`。
  3. 在 config 文件的 `train_pipeline` 列表中以 `dict(type='MyTransform')` 插入，可放在 `Pad` 之后、`DefaultFormatBundle` 之前（原文示例即此位置）。
- **配置项/命令**：原文未涉及具体启动命令或环境变量；仅有 Python 字典形式的配置片段作为可复制的模板（见上文"技术要点"中给出的 `img_norm_cfg` 与 `crop_size` 数值）。
