# Tutorial 3: Customize Data Pipelines

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/FCOS/docs/tutorials/data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/FCOS/docs/tutorials/data_pipeline.md

# 一体化深度解读：FCOS 文档之「Tutorial 3: Customize Data Pipelines」

---

## 【定位】

这篇文档解决**如何在 MMDetection/FCOS 检测框架中理解、设计与扩展数据预处理流水线（Data Pipeline）**的问题，描述了面向目标检测任务的可组合、可定制的数据准备能力——从数据加载、预处理、格式化到测试时增强的完整链路，以及向配置中注入自定义算子的方法。

---

## 【技术要点】

1. **数据抽象层采用 `Dataset` + `DataLoader` + `DataContainer` 三件套**：`Dataset` 返回与模型 `forward` 方法参数对齐的 dict；由于目标检测中图像尺寸、GT bbox 尺寸等存在差异，引入 MMCV 中的 `DataContainer` 类型来收集和分发变长数据。
2. **流水线（Pipeline）解耦于数据集**：数据集（Dataset）定义如何处理标注，流水线定义如何将数据 dict 准备完毕；流水线由一连串操作（operations）组成，每个操作以 dict 为输入、输出 dict 给下一个变换。
3. **流水线操作按四类划分**：Data loading（数据加载）、Pre-processing（预处理）、Formatting（格式化）、Test time augmentation（测试时增强）。
4. **每条操作对 dict 的影响有明确契约**：分为 add（新增键）、update（更新已有键）、remove（删除键）三类；图中以绿色（新增）、橙色（更新）标注。
5. **Faster R-CNN 标准流水线关键参数**：图片缩放尺度 `img_scale=(1333, 800)`、保持比例 `keep_ratio=True`、随机翻转概率 `flip_ratio=0.5`、`Pad` 的 `size_divisor=32`、归一化参数 `mean=[123.675, 116.28, 103.53]`、`std=[58.395, 57.12, 57.375]`、`to_rgb=True`。
6. **自定义流水线的三步流程**：① 在任意文件（如 `my_pipeline.py`）中用 `@PIPELINES.register_module()` 注册新类；② 在使用处 `import` 新类；③ 在 config 文件的 pipeline 列表中加入 `dict(type='MyTransform')`。

---

## 【关键机制与数据】

### 工作原理（数据流）

- **基础调用栈**：`DataLoader` 多 worker 拉取 → `Dataset.__getitem__` 取出原始样本 → 依次经过 pipeline 中每一个 op → 每个 op 输入一个 dict、输出一个 dict（op 之间通过共享 dict 字段名进行耦合）→ 最终输出符合模型 `forward` 入参的 dict。
- **字典字段语义流转**：以 Faster R-CNN `train_pipeline` 为例——
  - `LoadImageFromFile` 先把磁盘图像加载为 `img`，记录 `img_shape`、`ori_shape`；
  - `LoadAnnotations(with_bbox=True)` 加载 `gt_bboxes`、`gt_labels` 等真值字段；
  - `Resize(img_scale=(1333,800), keep_ratio=True)` 对图像与所有 bbox/mask/seg 字段做同步缩放；
  - `RandomFlip(flip_ratio=0.5)` 以 0.5 概率水平翻转图像与相关几何字段；
  - `Normalize` 按 `mean/std/to_rgb` 参数对 `img` 做通道归一化；
  - `Pad(size_divisor=32)` 把图像 pad 到 32 的整数倍以对齐下游特征图步长；
  - `DefaultFormatBundle` 把 numpy/tensor/PolygonMasks 等统一打包；
  - `Collect(keys=['img','gt_bboxes','gt_labels'])` 收集必要字段到 `img_meta`，并移除其它键。

- **测试时增强（TTA）的特殊嵌套**：`MultiScaleFlipAug` 本身是一个容器型 op，其内部 `transforms=[...]` 子流水线负责对单张测试图像做多尺度/翻转增强；外层再通过 `ImageToTensor` 与 `Collect(keys=['img'])` 输出最终 dict。

### 数据维度（原文有的数字/参数）

| 类别 | 参数 | 原文值 |
|---|---|---|
| 归一化均值 | `mean` | `[123.675, 116.28, 103.53]` |
| 归一化方差 | `std` | `[58.395, 57.12, 57.375]` |
| 通道顺序 | `to_rgb` | `True` |
| 缩放尺度 | `img_scale` | `(1333, 800)` |
| 随机翻转概率 | `flip_ratio` | `0.5` |
| Pad 步长对齐 | `size_divisor` | `32` |
| 保持比例 | `keep_ratio` | `True` |

> 性能/吞吐数据：**原文未涉及**。

---

## 【表格解读】

> 原文以分类列表形式给出了每条 op 对 dict 字段的影响，相当于一张张"操作契约表"。下面按原文逐字还原为 markdown 表格，并逐行解读。

### 表 1 · Data loading（数据加载）

| Operation | add（新增字段） | update（更新字段） | remove（删除字段） |
|---|---|---|---|
| `LoadImageFromFile` | `img`, `img_shape`, `ori_shape` | — | — |
| `LoadAnnotations` | `gt_bboxes`, `gt_bboxes_ignore`, `gt_labels`, `gt_masks`, `gt_semantic_seg`, `bbox_fields`, `mask_fields` | — | — |
| `LoadProposals` | `proposals` | — | — |

**解读**：这一组 op 只做"读盘+解析"——把图像像素、GT 标注、外部 proposal 注入到 dict 中，并不修改已有字段。`LoadAnnotations` 在 `with_bbox=True` 时同时构建 `bbox_fields`/`mask_fields` 列表，作为后续几何变换的"作用面"。

---

### 表 2 · Pre-processing（预处理）

| Operation | add（新增字段） | update（更新字段） |
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

**解读**：这一组 op 是"几何/光度变换"——它们以通配符 `*bbox_fields`/`*mask_fields`/`*seg_fields` 命中所有几何相关字段，从而保证图像与标注同步变换。`Resize` 还会额外记录 `scale_idx`/`scale_factor`/`pad_shape` 等元信息，供下游使用；`RandomCrop` 是少数会改动 `gt_labels`（如过滤越界目标）的 op。

---

### 表 3 · Formatting（格式化）

| Operation | add（新增字段） | update（更新字段） | remove（删除字段） |
|---|---|---|---|
| `ToTensor` | — | specified by `keys` | — |
| `ImageToTensor` | — | specified by `keys` | — |
| `Transpose` | — | specified by `keys` | — |
| `ToDataContainer` | — | specified by `fields` | — |
| `DefaultFormatBundle` | — | `img`, `proposals`, `gt_bboxes`, `gt_bboxes_ignore`, `gt_labels`, `gt_masks`, `gt_semantic_seg` | — |
| `Collect` | `img_meta`（其内部键由 `meta_keys` 指定） | — | all other keys except for those specified by `keys` |

**解读**：这一组 op 负责把 numpy/PIL/PolygonMasks 等异构数据转成统一张量表示，并把元信息收拢到 `img_meta`。`Collect` 是流水线的"末端闸门"：除 `keys` 中显式保留的字段外，其余一律清掉，确保模型只看到它需要的键，避免泄露中间变量。

---

### 表 4 · Test time augmentation（测试时增强）

| Operation | 角色 |
|---|---|
| `MultiScaleFlipAug` | 容器型 op，包裹一个 `transforms` 子流水线，对测试图做多尺度/翻转增强 |

**解读**：与训练流水线不同，测试流水线以 `MultiScaleFlipAug` 作为唯一入口 op，其内部递归执行 resize→flip→normalize→pad→tensor→collect 子流水线，输出多个增强视图供模型 ensemble。

---

## 【公式解读】

**原文无公式**。

（流水线本身是程序化的 op 序列，未出现 LaTeX 数学公式或伪代码形式的数学表达。）

---

## 【关联】

> 原文内/文末**未提供内部链接**（除一张相对路径的 `data_pipeline.png` 配图）。

文档中提到的、但**指向外部仓库**的关键关联点：

- **MMCV `DataContainer`**：用于承载变长数据（图像尺寸、GT bbox 尺寸等）的容器类型，原文给出 MMCV 源码链接 `mmcv/parallel/data_container.py`，这是流水线能够处理"非定长样本"的基础设施依赖。
- **MMDetection 注册器 `@PIPELINES.register_module()`**：自定义 op 的注册入口依赖 MMDetection 的 registry 机制，因此该文档隐含要求读者熟悉 MMDetection 的配置/注册体系（与 Tutorial 1/2 的 config 编写、model 自定义相衔接）。

---

## 【使用方法】

### 一、标准流水线的启用（以 Faster R-CNN 为例）

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
在 config 文件中通过 `train_pipeline = [...]` / `test_pipeline = [...]` 字段挂接到 `data` 配置下即可生效。

### 二、自定义流水线的注入（原文给出的三步法）

**Step 1 — 编写并注册新 op**（任意文件，如 `my_pipeline.py`）：
```python
from mmdet.datasets import PIPELINES

@PIPELINES.register_module()
class MyTransform:
    def __call__(self, results):
        results['dummy'] = True
        return results
```

**Step 2 — 在使用处 import**：
```python
from .my_pipeline import MyTransform
```

**Step 3 — 在 config 的 pipeline 列表中按需插入**（原文示例将其放在 `Pad` 之后、`DefaultFormatBundle` 之前）：
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

### 三、命令行 / 启动方式

> **原文未涉及**具体的启动命令或 CLI 参数。启用方式全部通过 config 文件中的 pipeline 列表声明完成。
