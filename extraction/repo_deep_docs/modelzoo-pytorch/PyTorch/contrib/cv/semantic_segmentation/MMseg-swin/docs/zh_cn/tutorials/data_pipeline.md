# 教程 3: 自定义数据流程

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/zh_cn/tutorials/data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/zh_cn/tutorials/data_pipeline.md

# 一体化深度解读：MMseg-swin 自定义数据流程教程

---

## 【定位】

这篇文档解决「如何在 MMSeg（基于 MMCV 的语义分割框架）中设计与扩展数据准备流程（Data Pipeline）」的问题——说明数据流程的结构、四类变换操作的职责、PSPNet 训练/测试流程的具体字典变换链，以及如何注册自定义的 Pipeline 类并接入到训练配置中。

---

## 【技术要点】

1. **数据容器 DataContainer**：由于语义分割中图像输入尺寸不同，MMCV 引入 `DataContainer` 类型来收集和分发不同大小的输入数据（原文链接指向上游 MMCV 仓库的 `mmcv/parallel/data_container.py`）。
2. **数据集与流程解耦**：数据集（Dataset）只负责处理标注（annotations），数据流程（pipeline）负责准备送入模型前向方法所需的字典——流程由「数据加载、预处理、格式变化、测试时增强」四类操作串联而成。
3. **PSPNet 训练流程共 10 步**（按顺序）：`LoadImageFromFile` → `LoadAnnotations` → `Resize` → `RandomCrop` → `RandomFlip` → `PhotoMetricDistortion` → `Normalize` → `Pad` → `DefaultFormatBundle` → `Collect(keys=['img', 'gt_semantic_seg'])`。
4. **PSPNet 测试流程以 MultiScaleFlipAug 包裹**：外层 `MultiScaleFlipAug` 内部再嵌套 `Resize(keep_ratio=True)` → `RandomFlip` → `Normalize` → `ImageToTensor` → `Collect(keys=['img'])`；被注释掉的 `img_ratios=[0.5, 0.75, 1.0, 1.25, 1.5, 1.75]` 提示多尺度滑窗的常见倍率。
5. **关键超参与数值**：
   - 图像归一化参数 `mean=[123.675, 116.28, 103.53]`，`std=[58.395, 57.12, 57.375]`，`to_rgb=True`
   - 裁剪尺寸 `crop_size=(512, 1024)`，与 `Resize` 目标 `img_scale=(2048, 1024)`、缩放区间 `ratio_range=(0.5, 2.0)`
   - `RandomCrop` 的 `cat_max_ratio=0.75`；`RandomFlip` 的 `flip_ratio=0.5`；`Pad` 的 `pad_val=0`、`seg_pad_val=255`
6. **自定义流程三步接入**：① 用 `@PIPELINES.register_module()` 装饰器注册新变换类；② 在 `__init__.py` 中 `from .my_pipeline import MyTransform`；③ 在配置文件的 `train_pipeline` 列表中加入 `dict(type='MyTransform')`。

---

## 【关键机制与数据】

### 工作原理：字典流（dict flow）

- **入口**：每个变换（transform）以一个字典 `results` 作为输入，输出一个新的字典给下一个变换。
- **驱动**：MMSeg/MMCV 在 `Dataset` 的 `__getitem__` 中按配置顺序依次调用 `pipeline` 列表里的每个变换。
- **输出**：最终字典中的键对应模型前向方法（`forward_train`/`forward_test`）的参数，其中图像和标签经过 `DefaultFormatBundle` / `ImageToTensor` 转为张量，由 `Collect` 收拢 `img_meta` 元信息。

### 各操作对字典域的副作用（原文逐条）

> 原文以列表形式给出每个操作「增加 / 更新 / 移除」哪些字典域。

**数据加载（Data loading）**
- `LoadImageFromFile` — **增加**：`img`、`img_shape`、`ori_shape`
- `LoadAnnotations` — **增加**：`gt_semantic_seg`、`seg_fields`

**预处理（Pre-processing）**
- `Resize` — **增加**：`scale`、`scale_idx`、`pad_shape`、`scale_factor`、`keep_ratio`；**更新**：`img`、`img_shape`、`*seg_fields`
- `RandomFlip` — **增加**：`flip`；**更新**：`img`、`*seg_fields`
- `Pad` — **增加**：`pad_fixed_size`、`pad_size_divisor`；**更新**：`img`、`pad_shape`、`*seg_fields`
- `RandomCrop` — **更新**：`img`、`pad_shape`、`*seg_fields`
- `Normalize` — **增加**：`img_norm_cfg`；**更新**：`img`
- `SegRescale` — **更新**：`gt_semantic_seg`
- `PhotoMetricDistortion` — **更新**：`img`

**格式（Formatting）**
- `ToTensor` / `ImageToTensor` / `Transpose` / `ToDataContainer` — **更新**：由 `keys` 指定
- `DefaultFormatBundle` — **更新**：`img`、`gt_semantic_seg`
- `Collect` — **增加**：`img_meta`（其内部键由 `meta_keys` 指定）；**移除**：除 `keys` 指定外的所有键

**测试时数据增强**
- `MultiScaleFlipAug` —— 原文未单独列出其字典域副作用（其内部嵌套一组 transforms）。

### 性能数据

原文未涉及任何训练耗时、推理速度、mIoU 等性能数字，本节不臆造。

---

## 【表格解读】

**原文无表格**。原文以「列表 + 子标题」的方式罗列每个变换对字典域的增删改条目，并非以表格形式呈现；为忠实于原文，此处不做结构重构。

---

## 【公式解读】

**原文无公式**。原文中出现的均为 Python 配置字典（如 `mean=[123.675, 116.28, 103.53]` 等数值字面量），并非数学公式或 LaTeX 表达式，因此无公式需要解释。

---

## 【关联】

- **上游 / 底层框架**：MMCV 提供了 `DataContainer`（数据容器）与 `DataParallel` 的多线程数据加载能力，文档显式给出链接 `https://github.com/open-mmlab/mmcv/blob/master/mmcv/parallel/data_container.py`，说明本 pipeline 机制严重依赖 MMCV。
- **数据集层**：与数据集类（Dataset）解耦——数据集只负责标注解析，pipeline 负责样本组装，二者通过 `meta_keys` / `seg_fields` 等字典键互通。
- **模型前向层**：pipeline 输出字典的键（`img`、`gt_semantic_seg`、`img_meta`）与 MMSeg 模型 `forward_train` / `forward_test` 的参数命名一致；`Collect` 操作是 pipeline 与模型前向之间的「收口」。
- **测试流程**：训练与测试共用基础变换（`LoadImageFromFile`、`Normalize`、`Resize`），但测试流程外层包了 `MultiScaleFlipAug`，用于多尺度+翻转的测试时增强（TTA）。
- **拓展接口**：`PIPELINES.register_module` 装饰器与 `mmseg.datasets.PIPELINES` 注册表，是与 MMSeg「注册器（Registry）」机制的统一接入点，新增 `MyTransform` 可与内置变换以相同方式插入到字典链中。
- **本文为教程系列第 3 篇**（标题「教程 3: 自定义数据流程」），与同目录下其他教程（如配置说明、模型定义、自定义数据集等）属于姊妹篇，但文末未提供内部链接，故不强行关联。

---

## 【使用方法】

### 自定义 Pipeline 类的三步流程（原文「拓展和使用自定义的流程」节）

1. **编写变换类**（保存为例如 `my_pipeline.py`）：

   ```python
   from mmseg.datasets import PIPELINES

   @PIPELINES.register_module()
   class MyTransform:

       def __call__(self, results):
           results['dummy'] = True
           return results
   ```

   - 必须继承可调用对象并实现 `__call__(self, results)`：输入 `results` 字典，输出新的字典。

2. **导入新类**（通常在对应数据集目录的 `__init__.py` 中）：

   ```python
   from .my_pipeline import MyTransform
   ```

3. **在配置文件中使用**：

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
       dict(type='MyTransform'),                # ← 插入自定义变换
       dict(type='DefaultFormatBundle'),
       dict(type='Collect', keys=['img', 'gt_semantic_seg']),
   ]
   ```

### 启用命令 / 配置项

- **原文未涉及**：具体的 CLI 启动命令、训练脚本入口、`tools/train.py` 用法等均未在本教程中出现，本节不予补全。
