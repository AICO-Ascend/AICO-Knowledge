# Tutorial 3: Customize Data Pipelines

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch/docs/tutorials/data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch/docs/tutorials/data_pipeline.md

# 教程 3: 自定义数据流水线 — 一体化深度解读

## 【定位】

这篇文档解决"如何在 MMDetection (含 RetinaNet_for_PyTorch) 的目标检测框架中理解、配置和扩展数据预处理流水线 (data pipeline)"的问题——描述了从原始标注/图像到模型 forward 输入的整套数据流编排能力。

---

## 【技术要点】

- **数据流载体**: 基于 PyTorch 标准的 `Dataset` + `DataLoader` (多 worker), 每个样本是一个 dict, 字段名与模型 `forward()` 的参数对应; 由于检测中图像尺寸与 gt bbox 尺寸可变, 引入 MMCV 中的 `DataContainer` 类型承载变长数据。
- **关注点分离**: 数据集 (Dataset) 只负责"如何读标注"; 流水线 (Pipeline) 负责"如何一步步把一个数据 dict 加工成模型可消费的输入"。Pipeline 由一系列 transform 串成, 每一步 dict 进、dict 出。
- **四类操作划分**: 数据加载 (data loading) → 预处理 (pre-processing) → 格式化 (formatting) → 测试时增强 (test-time augmentation)。
- **Faster R-CNN 标准管线 (示例)**: `img_norm_cfg = dict(mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)`; 训练流水 8 步; 测试流水用 `MultiScaleFlipAug` 包裹 6 步内部 transform。
- **关键超参数字 (原文)**: `img_scale=(1333, 800)`, `keep_ratio=True`, `flip_ratio=0.5`, `size_divisor=32`; 测试时 `flip=False` (因为多尺度翻转增强由外层 `MultiScaleFlipAug` 控制)。
- **扩展机制**: 通过 `@PIPELINES.register_module()` 注册新 transform, 在任意 `.py` 中定义后 import 进 config, 即可像内置算子一样以 `dict(type='MyTransform')` 形式插入流水线列表。

---

## 【关键机制与数据】

### 流水线数据流原理 (原文机制)

- 每个 operation (蓝色块) 接收一个 dict, 输出一个新的 dict, 后一个 op 以前一个 op 的输出为输入。
- 算子可 **新增** 键 (绿色标记, 如 `LoadImageFromFile` 新增 `img`, `img_shape`, `ori_shape`), 也可 **更新** 已有键 (橙色标记, 如 `Resize` 更新 `img`, `img_shape`, `*bbox_fields`, `*mask_fields`, `*seg_fields`)。
- `Collect` 是收尾算子: 新增 `img_meta` (其字段由 `meta_keys` 指定), 同时**移除**未在 `keys` 中列出的所有其它键——这是把数据 dict 收缩为模型 forward 真正需要的张量子集的关键步骤。
- `DataContainer` (MMCV 提供) 解决"同一 batch 内图像/掩码尺寸不一"的收集与分发问题, 详见文中给出的 mmcv 源码链接。

### 关键参数与数值 (原文)

- 归一化均值: `[123.675, 116.28, 103.53]` (按 RGB 通道)
- 归一化标准差: `[58.395, 57.12, 57.375]`
- `to_rgb=True` (BGR→RGB)
- `img_scale=(1333, 800)` — 检测输入的 (宽, 高)
- `keep_ratio=True` — Resize 时保持长宽比
- `flip_ratio=0.5` — 训练时 50% 概率翻转
- `size_divisor=32` — Pad 对齐到 32 的倍数 (适配网络下采样)

### 性能/对比数据

原文未涉及具体性能数据或基准对比。

---

## 【表格解读】

**原文无表格** (无 markdown 表格、无参数对比表、无性能对比表)。

不过原文以**列表**形式给出了每个 transform 对 dict 字段的"新增/更新/移除"语义, 实际属于结构化表格信息, 现将 `Data loading` 与 `Formatting` 两类逐字还原为表格以便阅读:

| 类别 | 操作 (type) | add | update | remove |
|---|---|---|---|---|
| Data loading | `LoadImageFromFile` | `img`, `img_shape`, `ori_shape` | — | — |
| Data loading | `LoadAnnotations` | `gt_bboxes`, `gt_bboxes_ignore`, `gt_labels`, `gt_masks`, `gt_semantic_seg`, `bbox_fields`, `mask_fields` | — | — |
| Data loading | `LoadProposals` | `proposals` | — | — |
| Formatting | `ToTensor` | — | specified by `keys` | — |
| Formatting | `ImageToTensor` | — | specified by `keys` | — |
| Formatting | `Transpose` | — | specified by `keys` | — |
| Formatting | `ToDataContainer` | — | specified by `fields` | — |
| Formatting | `DefaultFormatBundle` | — | `img`, `proposals`, `gt_bboxes`, `gt_bboxes_ignore`, `gt_labels`, `gt_masks`, `gt_semantic_seg` | — |
| Formatting | `Collect` | `img_meta` (由 `meta_keys` 指定) | — | 未在 `keys` 中列出的所有其它键 |

逐行解读:
- `LoadImageFromFile` 是入口, 把磁盘文件解码成图像张量并记录原始/缩放后尺寸。
- `LoadAnnotations` 一次性把所有监督信号读齐: bbox、忽略框、类别、掩码、可选语义分割, 同时建立字段索引 `bbox_fields`/`mask_fields` 供后续算子做"通配更新"。
- `LoadProposals` 是为两阶段检测 (R-CNN 系列) 准备 region proposals 的可选算子。
- `ToTensor`/`ImageToTensor`/`Transpose` 是面向张量的轻量转换, 行为完全由 `keys` 决定。
- `ToDataContainer` 把指定字段包成 `DataContainer`, 解决变长收集。
- `DefaultFormatBundle` 是一次性把 7 类常见字段统一转成张量/容器的批处理算子, 是训练流水线的标准搭配。
- `Collect` 是流水线的"出口闸门": 留下 `img` 等真正喂给模型的字段, 把所有中间过程键全部清理掉, 并把元信息统一打包进 `img_meta` (后续送入模型以还原 padding/origin scale)。

Pre-processing 类原文以"无表格列表"呈现, 此处亦以表格逐字还原:

| 操作 (type) | add | update |
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

解读要点:
- `*bbox_fields`/`*mask_fields`/`*seg_fields` 这种"通配写法"依赖 `LoadAnnotations` 中建立的字段索引, 表示"对所有登记过的 bbox/mask/seg 字段都做同样的更新"——这正是 pipeline 与 dataset 解耦后能复用的关键设计。
- `Resize` 既 add 又 update: 新增的 5 个字段是为可复现/可逆 (反推原图坐标) 服务; update 体现几何变换作用到图像与所有监督信号。
- `Pad` 只更新 `mask_fields`/`seg_fields` 而不更新 `*bbox_fields`, 因为 bbox 用归一化坐标 (或原坐标) 表示, padding 不影响其数值。
- `Normalize` 把自己用过的 `img_norm_cfg` 记录到 dict 中, 是为了让推理/可视化时按相同均值方差反向还原。

---

## 【公式解读】

**原文无公式** (文档中无 LaTeX 数学公式, 无伪代码公式; 仅以 Python `dict` 字面量配置参数形式给出)。

---

## 【关联】

虽然文末"内部链接"字段标注为 (无), 但原文正文中**显式指向**了以下外部/上下游资源, 构成 pipeline 机制的依赖网络:

- **`mmcv.parallel.data_container.DataContainer`** — 链接 `https://github.com/open-mmlab/mmcv/blob/master/mmcv/parallel/data_container.py`: 解决变长数据收集的核心数据结构, 是流水线中 `ToDataContainer` 与 `DefaultFormatBundle` 的底层依赖。
- **`Dataset` + `DataLoader` (PyTorch 标准范式)** — 上游: Dataset 负责 `__getitem__` 返回初始 dict, DataLoader 负责多 worker 批量化; Pipeline 在 `Dataset` 内部被调用。
- **模型 `forward()` 方法的输入参数** — 下游: Pipeline 终态 dict 的字段名 (`img`, `gt_bboxes`, `gt_labels`, `img_meta` 等) 必须与检测模型 forward 签名对齐, 因此修改 collect keys 时需同步检查 head/net 的接口。
- **配置文件 (config)** — 配置载体: Pipeline 是 config 中的 Python list, 通过 `dict(type=...)` 实例化, 因此本教程的"扩展自定义 pipeline"步骤最终落地在 config 文件中。
- **`resources/data_pipeline.png`** — 视觉化依赖: 图中蓝色块 (pipeline ops) 与绿/橙色字段标记是理解"每步 add vs update"分类的官方图示。
- **Faster R-CNN 示例** — 横向参照: 同一 pipeline 机制被 R-CNN 系列共用, RetinaNet_for_PyTorch 作为单阶段检测器同样消费这套流水线 (其差异主要在 head 与 loss, 而非 pipeline 结构)。
- **测试时增强 `MultiScaleFlipAug`** — 推理分支: 包裹一个内部子流水线, 实现了"对同一图像做多尺度+翻转产生多份预测再合并"的机制。

---

## 【使用方法】

### 1. 在 config 中"使用"流水线 (启用方式)

直接以 Python `dict` 列表形式在 config 文件中声明, 训练与测试分别定义 `train_pipeline` 与 `test_pipeline`; 原文示例 (Faster R-CNN) 完整列出, 此处逐字保留:

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

### 2. 关键配置项 (原文有)

- `mean`/`std`/`to_rgb` — 图像归一化 (`Normalize` 算子)。
- `img_scale=(1333, 800)` / `keep_ratio=True` — 几何 resize (`Resize` 算子)。
- `flip_ratio=0.5` — 训练翻转概率 (`RandomFlip` 算子); 测试 pipeline 内 `RandomFlip` 的 `flip` 由外层 `MultiScaleFlipAug` 决定。
- `size_divisor=32` — Pad 对齐粒度 (`Pad` 算子)。
- `with_bbox=True` — `LoadAnnotations` 是否加载 bbox。
- `keys` (Collect 与 ImageToTensor) — 决定最终保留哪些字段以及哪些字段转 tensor。
- `meta_keys` (Collect) — 决定 `img_meta` 中收集哪些元信息字段。
- `fields` (ToDataContainer) — 决定哪些字段包成 `DataContainer`。

### 3. 添加自定义算子 (扩展方式, 原文三步法)

1. **写算子类** (例如 `my_pipeline.py`):

```python
from mmdet.datasets import PIPELINES

@PIPELINES.register_module()
class MyTransform:

    def __call__(self, results):
        results['dummy'] = True
        return results
```

2. **导入该类**: `from .my_pipeline import MyTransform`
3. **在 config 的 pipeline 列表中按位置插入**:

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
    dict(type='MyTransform'),          # ← 自定义算子在此处插入
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_bboxes', 'gt_labels']),
]
```

### 4. 原文未涉及的部分

- 未给出完整的命令行启动方式 (命令行调用通常在更上层的 train/test 教程中描述, 本教程不涉及)。
- 未给出 RetinaNet_for_PyTorch 的专属 pipeline (本教程示例沿用 Faster R-CNN, 但机制对该 repo 内所有检测模型通用)。
- 未给出各算子的可调超参完整枚举 (仅展示被示例用到的子集)。
