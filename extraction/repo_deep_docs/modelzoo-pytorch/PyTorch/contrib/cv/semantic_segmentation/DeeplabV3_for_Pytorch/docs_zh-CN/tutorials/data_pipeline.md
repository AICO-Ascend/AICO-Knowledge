# 教程 3: 自定义数据流程

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs_zh-CN/tutorials/data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs_zh-CN/tutorials/data_pipeline.md

# 教程 3: 自定义数据流程 — 一体化深度解读

## 【定位】

本文档解决"如何为 mmsegmentation 系列模型（如 DeepLabV3 / PSPNet）按可插拔方式自定义数据预处理流程"的问题，重点说明 Dataset/DataLoader 取数范式、`DataContainer` 对变长输入的收集与分发机制、四类操作的字段级语义，以及自定义变换的三步接入流程（编写 → 注册 → 在 config 串接）。

---

## 【技术要点】

1. **基础范式**：使用 `Dataset` 与 `DataLoader` 进行多线程加载；`Dataset` 返回 dict，对应模型 forward 的参数；语义分割图像尺寸不一，因此引入 MMCV 的 `DataContainer` 类型处理不同大小数据的收集与分发。

2. **流程与数据集解耦**：数据集只负责处理标注信息，数据流程（pipeline）由若干顺序执行的变换组成，每步以 dict 为输入、输出 dict 给下一步；流程被划分为四类——**data loading / pre-processing / formatting / test-time augmentation**。

3. **PSPNet 训练流程关键参数（原文给出）**：
   - `img_norm_cfg = dict(mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)`
   - `crop_size = (512, 1024)`
   - `Resize(img_scale=(2048, 1024), ratio_range=(0.5, 2.0))`
   - `RandomCrop(crop_size=crop_size, cat_max_ratio=0.75)`
   - `RandomFlip(flip_ratio=0.5)`
   - `Pad(size=crop_size, pad_val=0, seg_pad_val=255)`
   - `Collect(keys=['img', 'gt_semantic_seg'])`

4. **PSPNet 测试流程关键参数（原文给出）**：通过 `MultiScaleFlipAug(img_scale=(2048, 1024), flip=False)` 包裹子流程，子流程顺序为 `Resize(keep_ratio=True) → RandomFlip → Normalize → ImageToTensor(keys=['img']) → Collect(keys=['img'])`；注释中给出常见多尺度比例 `img_ratios=[0.5, 0.75, 1.0, 1.25, 1.5, 1.75]`（被注释掉）。

5. **字段级契约**：每个操作都显式声明对 dict 字段的"增加 / 更新 / 移除"语义。例如 `LoadImageFromFile` 增加 `img, img_shape, ori_shape`；`LoadAnnotations` 增加 `gt_semantic_seg, seg_fields`；`Resize` 增加 `scale, scale_idx, pad_shape, scale_factor, keep_ratio` 并更新 `img, img_shape, *seg_fields`；`Collect` 会"增加 `img_meta`、移除除 `keys` 指定之外的全部键"——这一行为是流程收尾的关键。

6. **自定义变换三步接入**：
   - 步骤 1：在 `my_pipeline.py` 中用 `@PIPELINES.register_module()`（从 `mmseg.datasets` 导入）装饰一个实现 `__call__(self, results)` 的类；
   - 步骤 2：`from .my_pipeline import MyTransform`；
   - 步骤 3：在 config 的 `train_pipeline` 中以 `dict(type='MyTransform')` 插入（原文示例中插入位置在 `Pad` 之后、`DefaultFormatBundle` 之前）。

---

## 【关键机制与数据】

**工作原理（数据流，原文描述）：**

1. **数据流方向**：`Dataset.__getitem__` → 一串 pipeline 变换依次对 dict 进行"增/改/删" → 最终 `Collect` 把除保留键外的多余字段移除、只保留 `img`（或再加上 `gt_semantic_seg`）与合成的 `img_meta` → 送入 `DataLoader` 进行多线程批处理。
2. **`DataContainer` 的作用**（原文）：用于在批处理阶段收集并分发不同尺寸的输入数据；原文指引去 MMCV 的 `mmcv/parallel/data_container.py` 查看实现（未在本文给出源码细节）。
3. **四类操作的职责分工**（原文）：
   - **Data loading**：`LoadImageFromFile`、`LoadAnnotations` —— 从磁盘/标注读取原始数据。
   - **Pre-processing**：`Resize / RandomFlip / Pad / RandomCrop / Normalize / SegRescale / PhotoMetricDistortion` —— 几何与颜色扰动、归一化。
   - **Formatting**：`ToTensor / ImageToTensor / Transpose / ToDataContainer / DefaultFormatBundle / Collect` —— 转为张量、按规定键汇总 meta。
   - **Test-time augmentation**：`MultiScaleFlipAug` —— 测试阶段的多尺度 + 翻转增强（其内部嵌一组子 transforms）。
4. **训练流与测试流不对称**：训练流（PSPNet 示例）显式包含 `PhotoMetricDistortion`、`DefaultFormatBundle`，而测试流包在 `MultiScaleFlipAug` 内，使用 `ImageToTensor`（图像专用）代替 `DefaultFormatBundle`，并且**只 `Collect(['img'])`** 不再收集 `gt_semantic_seg`（因为推理没有真值）。

**性能数据**：原文未提供任何速度、mIoU、显存等数字；PSPNet 流程里出现的 `2048×1024`、`512×1024 crop`、`flip_ratio=0.5`、`cat_max_ratio=0.75` 等均为"配置参数"而非性能数字，因此本节无可标注的性能数据。

---

## 【表格解读】

**原文无表格**。原文中与"表"结构最接近的是按"操作 → 字段增/改/删"分组的列表（见上【技术要点】第 5 条）；为便于查阅，我**基于原文逐字**整理为下表（不做任何扩充）：

| 类别 | 操作 | 增加 (add) | 更新 (update) | 移除 (remove) |
|---|---|---|---|---|
| Data loading | LoadImageFromFile | img, img_shape, ori_shape | — | — |
| Data loading | LoadAnnotations | gt_semantic_seg, seg_fields | — | — |
| Pre-processing | Resize | scale, scale_idx, pad_shape, scale_factor, keep_ratio | img, img_shape, *seg_fields | — |
| Pre-processing | RandomFlip | flip | img, *seg_fields | — |
| Pre-processing | Pad | pad_fixed_size, pad_size_divisor | img, pad_shape, *seg_fields | — |
| Pre-processing | RandomCrop | — | img, pad_shape, *seg_fields | — |
| Pre-processing | Normalize | img_norm_cfg | img | — |
| Pre-processing | SegRescale | — | gt_semantic_seg | — |
| Pre-processing | PhotoMetricDistortion | — | img | — |
| Formatting | ToTensor | — | 由 `keys` 指定 | — |
| Formatting | ImageToTensor | — | 由 `keys` 指定 | — |
| Formatting | Transpose | — | 由 `keys` 指定 | — |
| Formatting | ToDataContainer | — | 由 `keys` 指定 | — |
| Formatting | DefaultFormatBundle | — | img, gt_semantic_seg | — |
| Formatting | Collect | img_meta (meta_keys 指定) | — | 除 `keys` 之外的全部键 |
| Test-time aug | MultiScaleFlipAug | （原文未列字段级增/改/删） | （原文未列字段级增/改/删） | （原文未列字段级增/改/删） |

逐行解读：

- **LoadImageFromFile / LoadAnnotations**：流程入口；前者把磁盘图像读入并记录原始与解码后形状，后者把语义分割标注读入并以 `seg_fields` 占位（方便后续按通配符 `*seg_fields` 批量更新）。
- **Resize / RandomCrop / Pad / RandomFlip**：都通过 `*seg_fields` 通配符同步处理标注，避免语义错位；其中 `Resize` 还会把 `img_scale / scale_idx / scale_factor / keep_ratio` 写入 meta，便于模型/可视化反推尺寸。
- **Normalize / SegRescale / PhotoMetricDistortion**：仅作用于图像或仅作用于分割标注；`Normalize` 同时把归一化参数 `img_norm_cfg` 写入 meta，便于复现/反归一化。
- **ToTensor / ImageToTensor / Transpose / ToDataContainer**：键控变换，作用域由调用方传入的 `keys` 决定；`ImageToTensor` 是图像专用版本。
- **DefaultFormatBundle**：把图像转成 `ImageTensor`（含 img、img_shape、ori_shape）、把分割标注转成 `SegTensor` 的语义分割专用打包格式。
- **Collect**：流程收尾阀门——只放行 `keys` 列表里的键，并把其他字段打包成 `img_meta`；这是保证最终 batch dict 干净、避免冗余字段被 collate 误处理的关键一步。
- **MultiScaleFlipAug**：原文未给出该操作的字段级说明，只交代其是测试时增强的容器，承载一组子 transforms。

---

## 【公式解读】

**原文无公式**。原文仅包含字典形式的配置（`img_norm_cfg / crop_size / train_pipeline / test_pipeline`）与 Python 代码片段，没有任何数学公式或伪代码公式需要解释。配置中出现的"参数对"如 `mean=[123.675, 116.28, 103.53]`、`std=[58.395, 57.12, 57.375]` 是按 RGB 三通道排列的归一化常数，可在【技术要点】第 3 条中查阅原文出处。

---

## 【关联】

- **DataContainer（MMCV）**：本文核心依赖之一，负责变长输入的收集与分发；原文给出外链 `https://github.com/open-mmlab/mmcv/blob/master/mmcv/parallel/data_container.py`（本文档被标注"内部链接: (无)"，故将其归为外部关联）。
- **数据集模块（`mmseg.datasets`）**：自定义流程的注册器 `@PIPELINES.register_module()` 即从此模块导入 `PIPELINES`；说明 pipeline 与 dataset 在代码组织上同属 mmseg 的 datasets 体系。
- **配置文件（config）体系**：自定义流程的最终落点是 `train_pipeline` / `test_pipeline` 这两个 Python list 配置项，体现了"用 Python dict/list 即配置"的 OpenMMLab 风格。
- **训练 ↔ 测试流差异**：PSPNet 示例同时给出了 `train_pipeline` 与 `test_pipeline`，二者共享 `LoadImageFromFile` 与 `img_norm_cfg`，但训练端使用 `DefaultFormatBundle + Collect(['img','gt_semantic_seg'])`，测试端则使用 `ImageToTensor + Collect(['img'])` 并被 `MultiScaleFlipAug` 包裹——这是同一管线在训练/推理两端的"分流点"。
- **与文末内部链接信息**：原文给出的链接状态为"（无）"，因此本节其余关系均按文档正文文本归纳，未引用任何额外的内部交叉链接。

---

## 【使用方法】

**原文未涉及"命令行的启用方式"**；但提供了可直接在 config 中复制的启用方式：

1. **使用内置 PSPNet 流程（原文已给出完整 dict，可直接粘贴进 config）**：
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
       dict(type='DefaultFormatBundle'),
       dict(type='Collect', keys=['img', 'gt_semantic_seg']),
   ]
   test_pipeline = [
       dict(type='LoadImageFromFile'),
       dict(
           type='MultiScaleFlipAug',
           img_scale=(2048, 1024),
           flip=False,
           transforms=[
               dict(type='Resize', keep_ratio=True),
               dict(type='RandomFlip'),
               dict(type='Normalize', **img_norm_cfg),
               dict(type='ImageToTensor', keys=['img']),
               dict(type='Collect', keys=['img']),
           ])
   ]
   ```
   注：原文将 `img_ratios=[0.5, 0.75, 1.0, 1.25, 1.5, 1.75]` 注释在 `MultiScaleFlipAug` 中，默认未启用；启用时取消注释即可。

2. **注册并使用自定义流程（原文给出的三步流程）**：
   - 步骤 1：新建 `my_pipeline.py`，装饰器注册 + 实现 `__call__(self, results)`：
     ```python
     from mmseg.datasets import PIPELINES

     @PIPELINES.register_module()
     class MyTransform:
         def __call__(self, results):
             results['dummy'] = True
             return results
     ```
   - 步骤 2：在流程装配处导入：`from .my_pipeline import MyTransform`
   - 步骤 3：在 `train_pipeline` 中插入 `dict(type='MyTransform')`（原文示例将其放在 `Pad` 之后、`DefaultFormatBundle` 之前）。

3. **字段级约束（原文列出，作为使用守则）**：自定义类应当像内置操作一样，遵循 dict 字段的"增 / 改 / 删"约定；最后务必让 `Collect` 仅保留训练/测试真正需要的键，避免不必要的字段进入 batch。
