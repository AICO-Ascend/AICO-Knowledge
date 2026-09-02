# 教程 3: 自定义数据流程

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/zh_cn/tutorials/data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/zh_cn/tutorials/data_pipeline.md

# 教程 3: 自定义数据流程 —— 深度解读

## 【定位】

这篇文档系统性地描述了语义分割任务中"数据流程 (data pipeline)"的设计理念、PSPNet 标准流程示例、各类变换操作的字段影响，以及如何扩展自定义变换类——核心解决的是"如何把数据准备 (annotation handling) 与数据变换 (preprocessing) 解耦，并通过可配置的 dict 列表灵活组装训练/测试流程"的问题。

---

## 【技术要点】

1. **解耦的数据架构**：数据集 (`Dataset`) 负责标注 (annotations) 处理，数据流程 (pipeline) 负责准备一个数据字典 (data dict) 的所有步骤；流程是 `dict→dict` 的串行变换链，每个操作接收一个字典、输出一个新字典。

2. **DataContainer 机制**：因语义分割输入图像尺寸不固定，MMCV 引入 `DataContainer` 类用于收集和分发不同大小的输入数据（参见 [MMCV 源码](https://github.com/open-mmlab/mmcv/blob/master/mmcv/parallel/data_container.py)）。

3. **PSPNet 标准训练流程（8 步）**：
   - `LoadImageFromFile` → `LoadAnnotations` → `Resize` (scale=`(2048,1024)`, ratio_range=`(0.5, 2.0)`) → `RandomCrop` (crop_size=`(512,1024)`, cat_max_ratio=`0.75`) → `RandomFlip` (flip_ratio=`0.5`) → `PhotoMetricDistortion` → `Normalize` (mean=`[123.675, 116.28, 103.53]`, std=`[58.395, 57.12, 57.375]`, to_rgb=True) → `Pad` (size=crop_size, pad_val=`0`, seg_pad_val=`255`) → `DefaultFormatBundle` → `Collect` (keys=`['img', 'gt_semantic_seg']`)。

4. **PSPNet 测试流程**：`LoadImageFromFile` + `MultiScaleFlipAug`（img_scale=`(2048, 1024)`, flip=False，内嵌 4 步：Resize(keep_ratio=True)→RandomFlip→Normalize→ImageToTensor→Collect）。

5. **四类操作划分**：数据加载 (`data loading`) / 预处理 (`pre-processing`) / 格式变化 (`formatting`) / 测试时数据增强 (`test-time augmentation`)，每类对应明确的字典字段 add/update/remove 语义。

6. **自定义流程三步注册机制**：① 编写继承自 `PIPELINES.register_module()` 装饰器的类（实现 `__call__(self, results)`）；② 在 `__init__.py` 中 `from .my_pipeline import MyTransform`；③ 在 config 的 pipeline 列表里用 `dict(type='MyTransform')` 插入新步骤。

---

## 【关键机制与数据】

**工作原理与数据流**：

- **流程即字典流水线**：每个操作对传入字典 `results` 进行 in-place 或 out-of-place 修改，链式调用形成最终送入模型 `forward()` 的输入。

- **`Collect` 操作的特殊语义**：这是流程的"收口"步骤——它**移除**除 `keys` 指定字段之外的所有其他键，并**新增** `img_meta` 字段（其内部子键由 `meta_keys` 指定）。这意味着流程末尾必须用 `Collect` 清理掉中间产生的辅助字段（如 `scale`, `pad_shape`, `flip` 等），只保留模型 forward 所需的最小集合。

- **数据加载层（最前）**：
  - `LoadImageFromFile` 增加：`img`, `img_shape`, `ori_shape`
  - `LoadAnnotations` 增加：`gt_semantic_seg`, `seg_fields`

- **预处理层（中间，字段最丰富）**：
  - `Resize`：增加 `scale`, `scale_idx`, `pad_shape`, `scale_factor`, `keep_ratio`；更新 `img`, `img_shape`, `*seg_fields`
  - `RandomFlip`：增加 `flip`；更新 `img`, `*seg_fields`
  - `RandomCrop`：更新 `img`, `pad_shape`, `*seg_fields`（不增加新字段）
  - `Normalize`：增加 `img_norm_cfg`；更新 `img`
  - `Pad`：增加 `pad_fixed_size`, `pad_size_divisor`；更新 `img`, `pad_shape`, `*seg_fields`
  - `SegRescale`：更新 `gt_semantic_seg`
  - `PhotoMetricDistortion`：仅更新 `img`

- **格式变化层**：
  - `ToTensor` / `ImageToTensor` / `Transpose` / `ToDataContainer`：更新由 `keys` 参数指定的字段（这些是字段粒度可控的通用工具）
  - `DefaultFormatBundle`：更新 `img` 与 `gt_semantic_seg`（这是语义分割场景的"打包"步骤，把 ndarray 转成 DataContainer/Tensor 形式）

- **测试时增强**：`MultiScaleFlipAug` 是一个"包装型"操作，内部嵌套子 `transforms` 列表，实现多尺度+多翻转推理。

**原文标注的数值参数**（原文直接给出，整理如下）：
- 图像归一化：`mean=[123.675, 116.28, 103.53]`, `std=[58.395, 57.12, 57.375]`, `to_rgb=True`
- 训练裁剪尺寸：`crop_size=(512, 1024)`
- 短边缩放尺度：`img_scale=(2048, 1024)`（注：2048 应理解为较短边，1024 为较长边，与 Cityscapes 数据集一致）
- 缩放比例抖动范围：`ratio_range=(0.5, 2.0)`
- 类别最大占比阈值：`cat_max_ratio=0.75`
- 翻转概率：`flip_ratio=0.5`
- Pad 填充值：图像 `pad_val=0`，分割图 `seg_pad_val=255`（255 是 ignore 类别索引）

> 原文未给出性能数据（如 FPS / mIoU 等 benchmark），故不引用。

---

## 【表格解读】

**原文无表格。**

（虽然文档列出了每个 pipeline 操作对字典字段的 add/update/remove 影响，但这是以"操作名称 + 项目符号列表"形式呈现的纯文本，并非 markdown/HTML 表格结构，因此按"原文无表格"处理。）

如需可视化，可整理为如下形式的参考表（基于原文信息重构，标注为"非原文表格，仅供阅读参考"）：

| 操作 | 类型 | 增加字段 | 更新字段 |
|---|---|---|---|
| LoadImageFromFile | 数据加载 | img, img_shape, ori_shape | — |
| LoadAnnotations | 数据加载 | gt_semantic_seg, seg_fields | — |
| Resize | 预处理 | scale, scale_idx, pad_shape, scale_factor, keep_ratio | img, img_shape, *seg_fields |
| RandomFlip | 预处理 | flip | img, *seg_fields |
| Pad | 预处理 | pad_fixed_size, pad_size_divisor | img, pad_shape, *seg_fields |
| RandomCrop | 预处理 | — | img, pad_shape, *seg_fields |
| Normalize | 预处理 | img_norm_cfg | img |
| SegRescale | 预处理 | — | gt_semantic_seg |
| PhotoMetricDistortion | 预处理 | — | img |
| ToTensor | 格式 | — | keys 指定 |
| ImageToTensor | 格式 | — | keys 指定 |
| Transpose | 格式 | — | keys 指定 |
| ToDataContainer | 格式 | — | keys 指定 |
| DefaultFormatBundle | 格式 | — | img, gt_semantic_seg |
| Collect | 格式 | img_meta | all others except keys 指定 |

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

- **MMCV 框架**：`DataContainer` 类以及 `PIPELINES.register_module()` 注册器机制均来源于 MMCV，文中给出了 `mmcv/parallel/data_container.py` 的 GitHub 链接作为延伸阅读，是理解"为何需要 DataContainer"以及"如何注册新操作"的关键依赖。

- **`mmseg.datasets.PIPELINES`**：自定义变换需通过此注册器暴露给配置系统；这是与 `mmseg.datasets` 中 `Dataset` 类的衔接点（Dataset 类通过 `pipeline` 字段调用这里注册的类）。

- **`Dataset` 与 `DataLoader` 上游**：文档开篇指出使用 PyTorch 标准 `Dataset`/`DataLoader` 做多线程加载，流程在 Dataset 的 `__getitem__` 内部被触发；因此本教程向上承接数据加载机制，向下衔接模型 forward 所需的数据格式。

- **测试时增强与训练流程的对称**：`MultiScaleFlipAug` 把 `LoadImageFromFile` 之外的所有步骤内嵌到 `transforms` 子列表，与训练流程的"加载→增强→归一化→Collect"结构形成镜像，体现"训练/测试共用一套算子但组合不同"的设计哲学。

- **`*seg_fields` 通配语义**：预处理中多个操作都提到 `*seg_fields`，意味着所有分割相关标签（不限于 `gt_semantic_seg`，例如可能含 `gt_edge` 等）会被一并更新；这是与 `LoadAnnotations` 中 `seg_fields` 列表联动形成的"字段集合广播"机制。

- **本仓库 `BiseNetV1_for_PyTorch`**：文档作为通用教程不直接出现 BiseNetV1 的 pipeline，但 BiseNetV1 配置文件中的 `train_pipeline`/`test_pipeline` 应遵循本文描述的相同结构与字段约定（属于上游 MMSegmentation 体系的移植应用）。

---

## 【使用方法】

**启用自定义流程的方式（原文明确给出）**：

1. **编写变换类**（任意文件，如 `my_pipeline.py`）：
   ```python
   from mmseg.datasets import PIPELINES

   @PIPELINES.register_module()
   class MyTransform:
       def __call__(self, results):
           results['dummy'] = True
           return results
   ```

2. **导入新类**（在 `__init__.py` 或使用处）：
   ```python
   from .my_pipeline import MyTransform
   ```

3. **在 config 中插入新步骤**（以 PSPNet 训练流程为例，在 `Normalize` 与 `DefaultFormatBundle` 之间插入）：
   ```python
   img_norm_cfg = dict(
       mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
   crop_size = (512, 1024)
   train_pipeline = [
       dict(type='LoadImageFromFile'),
       dict(type='LoadAnnotations'),
       dict(type='Resize', img_scale=(2048, 1024), ratio_range=(0.5, 2.0)),
       dict(type='RandomCrop', crop_size=crop_size, cat_max_ratio=0.75),
       dict(type='RandomFlip', flip_ratio=0.5),
       dict(type='PhotoMetricDistortion'),
       dict(type='Normalize', **img_norm_cfg),
       dict(type='Pad', size=crop_size, pad_val=0, seg_pad_val=255),
       dict(type='MyTransform'),               # <— 自定义步骤插入位置
       dict(type='DefaultFormatBundle'),
       dict(type='Collect', keys=['img', 'gt_semantic_seg']),
   ]
   ```

**关键配置项参数说明**（原文覆盖）：
- `img_norm_cfg`：mean / std / to_rgb 三个键
- `Resize.img_scale`：短边缩放目标
- `Resize.ratio_range`：训练时短边的随机缩放区间 `(0.5, 2.0)`
- `RandomCrop.cat_max_ratio`：单类占比超过 0.75 时重新采样，避免类别极度不均的 crop
- `Pad.seg_pad_val=255`：分割图边缘填充值，对应 ignore label
- `Collect.keys`：流程收口保留的字段白名单
- `MultiScaleFlipAug.img_ratios`（被注释）：示例中给出了候选值 `[0.5, 0.75, 1.0, 1.25, 1.5, 1.75]` 可作为参考（注释态，未启用）
