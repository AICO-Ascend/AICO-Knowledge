# Tutorial 3: Customize Data Pipelines

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/SSD/docs/tutorials/data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/SSD/docs/tutorials/data_pipeline.md

# 一体化深度解读：Tutorial 3: Customize Data Pipelines

## 【定位】

这篇文档系统性地描述了 MMCV/MMDet 体系中**面向目标检测任务的数据准备流水线（Data Pipeline）的设计与定制方法**——解决"如何把变长/变尺寸的检测样本（image、gt bbox、mask 等）通过一系列可组合、可扩展的 transform 步骤转换为模型 forward 方法所需的 dict 输入"这一工程核心问题。

---

## 【技术要点】

1. **数据加载范式**：基于 `Dataset` + `DataLoader` 多 worker 机制；`Dataset` 返回 dict，对应模型 `forward` 的参数命名；为应对目标检测样本不等长问题，引入 MMCV 的 `DataContainer` 类型（用于收集/分发不同 size 的数据）。

2. **流水线与数据集解耦**：dataset 负责标注解析，pipeline 负责所有 dict 准备步骤；pipeline 由一序列 operations 组成，每步输入 dict、输出 dict；operation 可向结果 dict **新增键（绿色）** 或 **更新已有键（橙色）**。

3. **Faster R-CNN 训练流水线组成（8 步）**：`LoadImageFromFile` → `LoadAnnotations(with_bbox=True)` → `Resize(img_scale=(1333, 800), keep_ratio=True)` → `RandomFlip(flip_ratio=0.5)` → `Normalize(mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)` → `Pad(size_divisor=32)` → `DefaultFormatBundle` → `Collect(keys=['img', 'gt_bboxes', 'gt_labels'])`。

4. **Faster R-CNN 测试流水线（1+1 复合 transform）**：先 `LoadImageFromFile`，再 `MultiScaleFlipAug(img_scale=(1333, 800), flip=False, transforms=[...])`；内层 transforms 依次为 `Resize(keep_ratio=True)` → `RandomFlip` → `Normalize(**img_norm_cfg)` → `Pad(size_divisor=32)` → `ImageToTensor(keys=['img'])` → `Collect(keys=['img'])`。

5. **Operations 四类划分**：data loading、pre-processing、formatting、test-time augmentation；每类下的 op 都有明确的 **add / update / remove 字段列表**（详见后文表格解读）。

6. **自定义 pipeline 三步法**：① 在 `my_pipeline.py` 中用 `@PIPELINES.register_module()` 注册类，类实现 `__call__(self, results): results['dummy'] = True; return results`；② `from .my_pipeline import MyTransform` 导入；③ 在 config 的 pipeline 列表里加入 `dict(type='MyTransform')`。

---

## 【关键机制与数据】

### 1. 流水线执行模型（原文）
每个 operation 都是 **dict-in / dict-out** 的纯函数式节点；operation 可向 dict 注入新键（add）或就地修改已有键（update），并最终由 `Collect` 操作清掉不在白名单里的键，从而保证送入模型的 dict 干净可控。

### 2. 变长数据的容器化（原文）
目标检测中 image 大小、gt bbox 个数、mask 形状都可能不一致；MMCV 提供 `DataContainer` 类型来封装这类数据，使 `DataLoader` 的 collate 阶段可以正确处理张量堆叠或保留为列表。具体实现链接指向 `mmcv/parallel/data_container.py`。

### 3. 数据流示例（Faster R-CNN，train_pipeline，原文）
依次经过：磁盘读图 → 解析标注 → 缩放到 (1333, 800) 保持比例 → 50% 概率翻转 → 用 ImageNet 均值方差做归一化并转 RGB → 填充到 32 倍数边长 → 转为模型可消费的 tensor bundle → 仅保留 `img / gt_bboxes / gt_labels` 三键送入模型。

### 4. 测试阶段增强（原文）
`MultiScaleFlipAug` 是一个**复合 transform**，对外封装"多尺度 + 翻转"的 TTA 思路；对内把 `Resize / RandomFlip / Normalize / Pad / ImageToTensor / Collect` 子流水线串起来执行。

### 5. 性能数据（原文）
原文未涉及任何吞吐量、mAP、显存等性能数字。

---

## 【表格解读】

**原文无表格**（markdown 表格形式）。但文档以**分类列表**形式罗列了所有 operation 对 dict 字段的 add/update/remove 行为，下面将其**逐字整理为表格**以便对照解读（内容与原文一致，未新增任何条目）：

### 数据加载（Data loading）

| Operation | Add | Update | Remove |
|---|---|---|---|
| `LoadImageFromFile` | `img`, `img_shape`, `ori_shape` | — | — |
| `LoadAnnotations` | `gt_bboxes`, `gt_bboxes_ignore`, `gt_labels`, `gt_masks`, `gt_semantic_seg`, `bbox_fields`, `mask_fields` | — | — |
| `LoadProposals` | `proposals` | — | — |

**解读**：这一类只"产出"数据，不修改任何已有键。`LoadAnnotations` 一次产出全部 GT 类别字段，并附带 `bbox_fields` / `mask_fields` 这类**字段索引**，供后续 `Resize / RandomFlip / Pad` 等使用 `*bbox_fields`、`*mask_fields` 形式批量更新。

### 预处理（Pre-processing）

| Operation | Add | Update |
|---|---|---|
| `Resize` | `scale`, `scale_idx`, `pad_shape`, `scale_factor`, `keep_ratio` | `img`, `img_shape`, `*bbox_fields`, `*mask_fields`, `*seg_fields` |
| `RandomFlip` | `flip` | `img`, `*bbox_fields`, `*mask_fields`, `*seg_fields` |
| `Pad` | `pad_fixed_size`, `pad_size_divisor` | `img`, `pad_shape`, `*mask_fields`, `*seg_fields` |
| `RandomCrop` | — | `img`, `pad_shape`, `gt_bboxes`, `gt_labels`, `gt_masks`, `*bbox_fields` |
| `Normalize` | `img_norm_cfg` | `img` |
| `SegRescale` | — | `gt_semantic_seg` |
| `PhotoMetricDistortion` | — | `img` |
| `Expand` | — | `img`, `gt_bboxes` |
| `MinIoURandomCrop` | — | `img`, `gt_bboxes`, `gt_labels` |
| `Corrupt` | — | `img` |

**解读**：这一类以**几何变换 + 像素级变换**为主，使用 `*_fields` 这种通配机制保证对所有 bbox / mask / seg 同步生效。`Normalize` 比较特别——它把归一化参数也回写到 dict（`img_norm_cfg`），便于可视化/反归一化时复用。

### 格式化（Formatting）

| Operation | Add | Update | Remove |
|---|---|---|---|
| `ToTensor` | — | specified by `keys` | — |
| `ImageToTensor` | — | specified by `keys` | — |
| `Transpose` | — | specified by `keys` | — |
| `ToDataContainer` | — | specified by `fields` | — |
| `DefaultFormatBundle` | — | `img`, `proposals`, `gt_bboxes`, `gt_bboxes_ignore`, `gt_labels`, `gt_masks`, `gt_semantic_seg` | — |
| `Collect` | `img_meta`（keys 由 `meta_keys` 指定） | — | all other keys except for those specified by `keys` |

**解读**：`Collect` 是流水线的"守门人"——它会保留 `keys` 白名单内的字段，把它们之外的字段全部清掉，同时把元信息（`meta_shape / scale_factor / flip / ...`）汇总到 `img_meta` 字典中。这是把"训练用的 GT 字段"与"测试时不需要的字段"分离的关键设计。

### 测试时增强（Test-time augmentation）

| Operation | 说明 |
|---|---|
| `MultiScaleFlipAug` | 复合 transform；详见下文 |

**解读**：原文仅列出该 op 名称未列字段表。它本身不直接修改字段，而是**递归调度其内嵌 `transforms` 列表**，相当于一个轻量级子 pipeline。

---

## 【公式解读】

**原文无公式**（既无 LaTeX 表达式，也无伪代码算法）。

---

## 【关联】

文档显式给出了**唯一一个外部依赖链接**：`DataContainer` 的实现位于 MMCV 仓库
`https://github.com/open-mmlab/mmcv/blob/master/mmcv/parallel/data_container.py`，这是理解"为什么目标检测能跟图像分类共享同一套 DataLoader"的关键。

文档内部**未提供任何内部链接**（题目已注明"内部链接: (无)"）。但从内容可以梳理出以下**上下游 / 模块间关系**：

- **上游（数据源）**：`Dataset` 类负责解析标注 → 产出原始 dict（至少含 `img`）。
- **同级（流水线内部）**：data loading 阶段产出原始字段；pre-processing 阶段以 `*_fields` 通配方式同步更新几何相关字段；formatting 阶段由 `Collect` 收口，最终把字段分为"模型输入张量"与"`img_meta` 元信息字典"两束。
- **下游（消费方）**：模型 `forward` 方法的参数命名必须与 `Collect(keys=[...])` 中保留的键一致（Faster R-CNN 示例中即 `img / gt_bboxes / gt_labels`）。
- **横向（增强）**：`MultiScaleFlipAug` 是测试时把整条子流水线（Resize/RandomFlip/Normalize/Pad/ImageToTensor/Collect）重新跑一遍的容器。
- **扩展接口**：`PIPELINES.register_module` 注册机制使得用户自定义 transform 可以像内置 op 一样被序列化到 config 的 `dict(type='MyTransform')` 中，形成"配置驱动的流水线组装"模式。

---

## 【使用方法】

### 1. 在 config 中定义 train_pipeline / test_pipeline（原文示例，原文已给出完整代码块）
关键参数：

| 配置项 | 取值（原文示例） |
|---|---|
| `img_norm_cfg.mean` | `[123.675, 116.28, 103.53]` |
| `img_norm_cfg.std` | `[58.395, 57.12, 57.375]` |
| `img_norm_cfg.to_rgb` | `True` |
| `Resize.img_scale` | `(1333, 800)` |
| `Resize.keep_ratio` | `True` |
| `RandomFlip.flip_ratio` | `0.5` |
| `Pad.size_divisor` | `32` |
| `LoadAnnotations.with_bbox` | `True` |
| `MultiScaleFlipAug.img_scale` | `(1333, 800)` |
| `MultiScaleFlipAug.flip` | `False` |
| `Collect.keys` | 训练：`['img', 'gt_bboxes', 'gt_labels']`；测试：`['img']` |

### 2. 扩展自定义 pipeline（三步法，原文）
- **步骤 1**：新建 `my_pipeline.py`，通过 `@PIPELINES.register_module()` 注册 `MyTransform` 类，实现 `__call__(self, results): results['dummy'] = True; return results`。
- **步骤 2**：`from .my_pipeline import MyTransform`。
- **步骤 3**：在 config 的 `train_pipeline` 列表里追加 `dict(type='MyTransform')`（原文示例放在 `Pad` 与 `DefaultFormatBundle` 之间）。

### 3. 启用方式 / 启动命令
原文未涉及具体的训练启动命令或注册入口文件位置；扩展自定义 op 时是否需要在 `__init__.py` 中导入、由框架自动发现，未在原文中说明。
