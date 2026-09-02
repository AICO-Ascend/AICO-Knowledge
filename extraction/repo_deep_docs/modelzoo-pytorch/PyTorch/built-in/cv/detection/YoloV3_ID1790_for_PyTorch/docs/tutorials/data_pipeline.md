# Tutorial 3: Customize Data Pipelines

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/YoloV3_ID1790_for_PyTorch/docs/tutorials/data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/YoloV3_ID1790_for_PyTorch/docs/tutorials/data_pipeline.md

# 深度解读：MMDetection 数据流水线自定义指南

## 【定位】

这篇文档系统性地介绍 MMDetection 中**数据流水线（Data Pipeline）的设计原理、内置算子语义以及自定义扩展方法**，解决"目标检测任务中如何灵活组装/扩展数据预处理流程"的问题，使开发者能够在不改框架源码的前提下，按需注入新的数据变换算子。

---

## 【技术要点】

1. **数据加载抽象**：基于 `Dataset` + `DataLoader` 多 worker 范式，`Dataset` 返回一个 `dict`，其键值与模型 `forward` 方法的形参一一对应。
2. **变长数据容器**：由于目标检测样本维度可变（图像尺寸、gt bbox 数量等），引入 MMCV 中的 `DataContainer` 类型来收集和分发不同尺寸的数据。
3. **流水线与数据集解耦**：数据集（`Dataset`）负责处理标注，流水线（Pipeline）负责数据字典（data dict）的全部准备步骤；流水线由一连串操作组成，每个操作**输入 dict、输出 dict**。
4. **四类算子分类**：
   - 数据加载（Data loading）
   - 预处理（Pre-processing）
   - 格式化（Formatting）
   - 测试时增强（Test-time augmentation，TTA）
5. **字典字段约定**：每个操作通过 `add` / `update` / `remove` 三类动作管理字典字段；蓝色块为流水线操作，绿色键为新加，橙色键为更新。
6. **自定义算子三步流程**：编写新类（实现 `__call__`）→ 用 `@PIPELINES.register_module()` 注册 → 在 config 中以 `type='MyTransform'` 引用。

---

## 【关键机制与数据】

**工作原理**（原文：流水线的运作方式）：
- 原文：*"Each operation takes a dict as input and also output a dict for the next transform."* —— 流水线本质是一条 dict→dict 的有向无环链。
- 原文：*"With the pipeline going on, each operator can add new keys (marked as green) to the result dict or update the existing keys (marked as orange)."* —— 数据键空间随流水线推进单调扩张或被覆盖。

**Fast/Faster R-CNN 训练流水线（原文给出的具体参数）**：
- 图像尺度归一化：`img_scale=(1333, 800)`，`keep_ratio=True`
- 翻转概率：`flip_ratio=0.5`
- 像素归一化：`mean=[123.675, 116.28, 103.53]`，`std=[58.395, 57.12, 57.375]`，`to_rgb=True`
- 填充对齐：`size_divisor=32`
- 收集键：`keys=['img', 'gt_bboxes', 'gt_labels']`

**性能数据**：原文未涉及任何性能数字（FPS、mAP、显存等）。

**数据流图（原文 Figure 描述）**：蓝色块 = pipeline operations，绿色 = 新增键，橙色 = 更新键。

---

## 【表格解读】

原文未出现规整的 markdown 表格，但**以"操作名 + add/update/remove 字段"的形式列举了每个算子对字典的副作用**，我将其逐字还原为表格，便于纵览：

### 数据加载类

| 算子 (type) | add（新增键） | update（更新键） | remove（删除键） |
|---|---|---|---|
| `LoadImageFromFile` | `img`, `img_shape`, `ori_shape` | — | — |
| `LoadAnnotations` | `gt_bboxes`, `gt_bboxes_ignore`, `gt_labels`, `gt_masks`, `gt_semantic_seg`, `bbox_fields`, `mask_fields` | — | — |
| `LoadProposals` | `proposals` | — | — |

### 预处理类

| 算子 (type) | add | update |
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

### 格式化类

| 算子 (type) | add | update | remove |
|---|---|---|---|
| `ToTensor` | — | 由 `keys` 指定 | — |
| `ImageToTensor` | — | 由 `keys` 指定 | — |
| `Transpose` | — | 由 `keys` 指定 | — |
| `ToDataContainer` | — | 由 `fields` 指定 | — |
| `DefaultFormatBundle` | — | `img`, `proposals`, `gt_bboxes`, `gt_bboxes_ignore`, `gt_labels`, `gt_masks`, `gt_semantic_seg` | — |
| `Collect` | `img_meta`（其键由 `meta_keys` 指定） | — | 除 `keys` 指定之外的全部键 |

### 测试时增强类

| 算子 (type) | 作用 |
|---|---|
| `MultiScaleFlipAug` | 包裹一组 transforms，组成多尺度 + 翻转的测试时增强包 |

**表格解读**：
- `*bbox_fields` / `*mask_fields` / `*seg_fields` 是**通配字段**，代表 `LoadAnnotations` 中对应列表里的全部键，避免逐条罗列。
- `Collect` 是流水线末端的关键**收束点**：通过 `keys` 白名单保留少量进入训练/推理的张量，其余（含 `img_shape`、`ori_shape`、`flip`、`scale_factor` 等元信息）全部 `remove`，仅通过 `meta_keys` 二次聚合到 `img_meta` 中，以便下游仍能访问图像原始尺寸、缩放比等信息。
- `DefaultFormatBundle` 与 `Collect` 协同：前者把 ndarray → tensor / DataContainer，后者把 dict 收敛为模型可消费的紧凑结构。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游模块**：`MMCV`（特别是 `mmcv.parallel.data_container.DataContainer`，详见原文给出的 GitHub 链接 `https://github.com/open-mmlab/mmcv/blob/master/mmcv/parallel/data_container.py`），提供变长数据的并行收集与分发能力，是 `Pad`/`Collect`/`ToDataContainer` 能正确处理不同尺寸图像与不等长 bbox 的基础。
- **下游模块**：流水线末端 `Collect` 输出的 `img` / `gt_bboxes` / `gt_labels` 直接喂给检测模型的 `forward` 方法；`img_meta` 提供给 RPN/RoI Head 用于后处理（如坐标反推、原始尺度恢复）。
- **横向模块**：文档示例以 **Faster R-CNN** 为对象，但流水线框架与 `Mask R-CNN`、`RetinaNet` 等共享——只要替换 `train_pipeline` / `test_pipeline`，即可迁移到其他检测器。
- **测试时增强**：`MultiScaleFlipAug` 内部子流水线结构 `dict(type='MultiScaleFlipAug', ..., transforms=[...])` 与训练流水线形成对称关系，使同一组基础算子可在训练/测试两侧复用。

---

## 【使用方法】

### 启用方式

MMDetection 默认即启用流水线机制，只要在配置文件中声明 `train_pipeline` / `test_pipeline` 即可。原文给出了一个**完整可用的 Faster R-CNN 配置片段**（见上文【关键机制与数据】节）。

### 关键配置项

| 配置项 | 取值示例 | 作用 |
|---|---|---|
| `img_scale` | `(1333, 800)` | 缩放目标尺寸 |
| `keep_ratio` | `True` | 是否保持宽高比 |
| `flip_ratio` | `0.5` | 水平翻转概率 |
| `mean` / `std` | `[123.675, 116.28, 103.53]` / `[58.395, 57.12, 57.375]` | 像素归一化参数 |
| `to_rgb` | `True` | 是否按 RGB 顺序 |
| `size_divisor` | `32` | 填充对齐的整除基数（与网络下采样总步长匹配） |
| `keys`（在 `Collect` 中） | `['img', 'gt_bboxes', 'gt_labels']` | 最终保留下来的张量键 |
| `meta_keys`（在 `Collect` 中） | 原文未给出具体列表 | 决定 `img_meta` 中聚合哪些元信息 |

### 自定义流水线三步命令（原文）

1. **编写并注册**：
   ```python
   from mmdet.datasets import PIPELINES

   @PIPELINES.register_module()
   class MyTransform:
       def __call__(self, results):
           results['dummy'] = True
           return results
   ```
2. **导入类**：`from .my_pipeline import MyTransform`
3. **在 config 流水线列表的任意位置插入**：`dict(type='MyTransform')`（原文示例中插入到 `Pad` 与 `DefaultFormatBundle` 之间）。

### 命令行运行

原文未涉及具体启动命令。
