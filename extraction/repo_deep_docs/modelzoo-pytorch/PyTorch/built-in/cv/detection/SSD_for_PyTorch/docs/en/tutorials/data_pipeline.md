# Tutorial 3: Customize Data Pipelines

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/data_pipeline.md

# 代码仓「modelzoo-pytorch」数据流水线文档深度解读

## 【定位】
本文档描述在 MMDetection 框架下如何自定义目标检测任务的数据流水线（Data Pipeline），涵盖流水线设计原理、各类变换操作的字段增删行为，以及如何编写、注册和使用自定义流水线变换。

---

## 【技术要点】

1. **数据加载机制**：采用 PyTorch 标准 `Dataset` + `DataLoader` 多 worker 模式；由于检测任务中图像尺寸、gt bbox 尺寸不一致，引入 MMCV 的 `DataContainer` 类型来收集和分发变长数据。

2. **流水线数据流**：流水线由一串操作组成，每个操作以 `dict` 为输入并输出 `dict` 给下一个变换；数据集定义标注处理，流水线定义数据准备步骤，二者解耦。

3. **操作四大分类**：① 数据加载（Loading）；② 预处理（Pre-processing）；③ 格式化（Formatting）；④ 测试时增强（Test-time augmentation）。

4. **关键配置参数**（原文 Faster R-CNN pipeline 示例）：
   - 归一化参数 `mean=[123.675, 116.28, 103.53]`，`std=[58.395, 57.12, 57.375]`，`to_rgb=True`
   - `Resize` 缩放尺度 `img_scale=(1333, 800)`，`keep_ratio=True`
   - `RandomFlip` 翻转概率 `flip_ratio=0.5`
   - `Pad` 尺寸对齐 `size_divisor=32`

5. **训练 vs 测试流水线差异**：测试流水线通过 `MultiScaleFlipAug` 包装器嵌套子变换列表（`Resize`/`RandomFlip`/`Normalize`/`Pad`/`ImageToTensor`/`Collect`），且无标注加载步骤。

6. **自定义流水线三步法**：
   ① 在 `my_pipeline.py` 中通过 `@PIPELINES.register_module()` 装饰类；
   ② 在 config 中通过 `custom_imports = dict(imports=['path.to.my_pipeline'], allow_failed_imports=False)` 引入；
   ③ 通过 `tools/misc/browse_dataset.py` 可视化结果。

---

## 【关键机制与数据】

- **流水线工作原理**（原文）：每个 operator 接收一个 `dict`，可向结果字典**新增**键（绿色标记）、**更新**已有键（橙色标记）或**移除**键；蓝色块代表 pipeline operation。
- **数据流方向**（原文）：图像文件 → `LoadImageFromFile` → `LoadAnnotations` → `Resize` → `RandomFlip` → `Normalize` → `Pad` → `DefaultFormatBundle` → `Collect`，最终输出送入模型 forward 方法。
- **`Collect` 操作行为**（原文）：新增 `img_meta` 字段（键由 `meta_keys` 指定），并**移除**除 `keys` 指定之外的所有其他键。
- **可视化工具**（原文）：`tools/misc/browse_dataset.py` 可视化浏览检测数据集（图像和 bbox 标注），或保存到指定目录。
- **参考实现链接**（原文）：`DataContainer` 源码见 `https://github.com/open-mmlab/mmcv/blob/master/mmcv/parallel/data_container.py`。

---

## 【表格解读】

原文无显式表格，但流水线操作与字段影响可整理如下（依据原文操作清单）：

| 阶段 | 操作 (Transform) | 新增字段 (add) | 更新字段 (update) | 移除字段 (remove) |
|---|---|---|---|---|
| Data loading | LoadImageFromFile | img, img_shape, ori_shape | — | — |
| Data loading | LoadAnnotations | gt_bboxes, gt_bboxes_ignore, gt_labels, gt_masks, gt_semantic_seg, bbox_fields, mask_fields | — | — |
| Data loading | LoadProposals | proposals | — | — |
| Pre-processing | Resize | scale, scale_idx, pad_shape, scale_factor, keep_ratio | img, img_shape, *bbox_fields, *mask_fields, *seg_fields | — |
| Pre-processing | RandomFlip | flip | img, *bbox_fields, *mask_fields, *seg_fields | — |
| Pre-processing | Pad | pad_fixed_size, pad_size_divisor | img, pad_shape, *mask_fields, *seg_fields | — |
| Pre-processing | RandomCrop | — | img, pad_shape, gt_bboxes, gt_labels, gt_masks, *bbox_fields | — |
| Pre-processing | Normalize | img_norm_cfg | img | — |
| Pre-processing | SegRescale | — | gt_semantic_seg | — |
| Pre-processing | PhotoMetricDistortion | — | img | — |
| Pre-processing | Expand | — | img, gt_bboxes | — |
| Pre-processing | MinIoURandomCrop | — | img, gt_bboxes, gt_labels | — |
| Pre-processing | Corrupt | — | img | — |
| Formatting | ToTensor | — | 由 `keys` 指定 | — |
| Formatting | ImageToTensor | — | 由 `keys` 指定 | — |
| Formatting | Transpose | — | 由 `keys` 指定 | — |
| Formatting | ToDataContainer | — | 由 `fields` 指定 | — |
| Formatting | DefaultFormatBundle | — | img, proposals, gt_bboxes, gt_bboxes_ignore, gt_labels, gt_masks, gt_semantic_seg | — |
| Formatting | Collect | img_meta（键由 `meta_keys` 指定） | — | 除 `keys` 指定外的所有其他键 |
| Test-time augmentation | MultiScaleFlipAug | （包装多尺度+翻转增强） | — | — |

**表格解读**：原文中 "*bbox_fields" 等带星号前缀表示对应字段组的通配展开（即遍历 `bbox_fields`/`mask_fields`/`seg_fields` 列表中的每个实际字段名）。整个流水线从原始文件路径读入，经加载→几何变换（Resize/Flip/Crop/Pad/Expand）→像素级变换（Normalize/Distortion/Corrupt）→格式化打包（FormatBundle/Collect）→模型输入，符合典型检测训练管线惯例。

---

## 【公式解读】

原文无公式（无 LaTeX 数学式或伪代码公式）。

---

## 【关联】

- **`DataContainer` 类型**（原文）：定义于 MMCV `mmcv/parallel/data_container.py`，用于收集和分发变长数据，是流水线能处理不同尺寸 bbox/mask 的基础。
- **`useful_tools` 工具集**（原文链接）：`../useful_tools.md` 文档提供了 `browse_dataset.py` 等可视化与调试工具，用于检查自定义流水线对数据增强的实际效果。
- **`@PIPELINES.register_module()` 注册器**：与 MMDetection 的其他 Registry（DATASETS/MODELS 等）机制一致，自定义 transform 必须先注册才能在 config 的 `type='MyTransform'` 字段中通过字符串引用。
- **`custom_imports` 配置项**：用于在启动训练时按需 import 自定义模块路径，依赖注册器机制；`allow_failed_imports=False` 表示导入失败则报错。
- **上游教程**：本文档标记为 "Tutorial 3"，对应数据准备环节，与模型配置（Tutorial 1/Tutorial 2）构成完整训练流程链。

---

## 【使用方法】

**1. 标准流水线启用方式**（原文示例）：在模型 config 文件中通过 `train_pipeline = [...]` 与 `test_pipeline = [...]` 列表定义，按顺序串联各 `dict(type='XXX', ...)` 操作。

**2. 自定义流水线启用步骤**（原文）：

- **步骤 ①**：新建文件 `my_pipeline.py`，继承类并装饰：
  ```python
  @PIPELINES.register_module()
  class MyTransform:
      def __init__(self, p=0.5):
          self.p = p
      def __call__(self, results):
          if random.random() > self.p:
              results['dummy'] = True
          return results
  ```

- **步骤 ②**：在 config 中加入导入与流水线条目：
  ```python
  custom_imports = dict(imports=['path.to.my_pipeline'], allow_failed_imports=False)
  # 在 train_pipeline 列表中加入：
  dict(type='MyTransform', p=0.2),
  ```

- **步骤 ③**：使用 `tools/misc/browse_dataset.py` 可视化流水线输出（详见 `../useful_tools.md`）。

**3. 关键配置项说明**（原文）：
- `with_bbox=True`：控制 `LoadAnnotations` 是否加载 bbox 标注。
- `keep_ratio=True`：控制 `Resize` 是否保持宽高比。
- `flip_ratio=0.5`：控制 `RandomFlip` 的水平翻转概率。
- `size_divisor=32`：控制 `Pad` 对齐到 32 的倍数（适配主流 backbone 的下采样倍数）。
- `to_rgb=True`：控制 `Normalize` 是否将 BGR 转为 RGB。
- `meta_keys`：`Collect` 操作中用于生成 `img_meta` 字段的键列表。
