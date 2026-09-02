# Tutorial 1: Learn about Configs

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/en/tutorials/config.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/en/tutorials/config.md

# MMseg-swin 配置文件教程深度解读

## 【定位】

本文档是 MMSegmentation 配置系统的入门教程，介绍如何理解、组织与命名实验配置文件，通过模块化与继承式设计支持语义分割模型（如 PSPNet）的灵活构建与变体实验。

---

## 【技术要点】

1. **四类基础组件**：配置文件 `config/_base_` 下包含四种基础组件类型——`dataset`、`model`、`schedule`、`default_runtime`，DeepLabV3、PSPNet 等大多数方法都可由这四类组件各取一个组合而成。

2. **继承层级约束**：同一文件夹下推荐**仅保留一个 _primitive_ 配置**，其他配置通过 `_base_` 继承，最大继承层级为 **3 层**。

3. **配置文件命名规范**：`{model}_{backbone}_[misc]_[gpu x batch_per_gpu]_{resolution}_{iterations}_{dataset}`，其中 `{}` 为必选字段，`[]` 为可选字段。
   - 必选字段：`{model}`、`{backbone}`、`{resolution}`、`{iterations}`、`{dataset}`
   - 可选字段：`[misc]`（如 `dconv`、`gcb`、`attention`、`mstrain`）、`[gpu x batch_per_gpu]`（默认 `8x2`）

4. **PSPNet 示例骨干配置**：使用 `ResNetV1c`，`depth=50`、`num_stages=4`、`out_indices=(0,1,2,3)`、`dilations=(1,1,2,4)`、`strides=(1,2,1,1)`、`style='pytorch'`，并加载预训练权重 `open-mmlab://resnet50_v1c`。

5. **PSPHead 解码头参数**：`in_channels=2048`、`in_index=3`、`channels=512`、`pool_scales=(1, 2, 3, 6)`、`dropout_ratio=0.1`。

6. **辅助头（FCNHead）参数**：`in_channels=1024`、`in_index=2`、`channels=256`、`num_convs=1`、`loss_weight=0.4`（通常为 decode head 损失权重的 0.4）；decode head `loss_weight=1.0`。

7. **数据归一化配置**：`mean=[123.675, 116.28, 103.53]`、`std=[58.395, 57.12, 57.375]`、`to_rgb=True`，与 ImageNet 预训练骨干保持一致。

8. **训练流水线数据规格**：`img_scale=(2048, 1024)`、`crop_size=(512, 1024)`、`ratio_range=(0.5, 2.0)`、`cat_max_ratio=0.75`、`flip_ratio=0.5`。

---

## 【关键机制与数据】

**配置系统工作原理（原文）：**

- 通过 `python tools/print_config.py /PATH/TO/CONFIG` 命令可打印完整配置；通过 `--cfg-options xxx.yyy=zzz` 可在命令行覆盖任意字段值。
- 模块化设计：将 `dataset / model / schedule / default_runtime` 分离为四个基础组件，便于组合新方法。
- 继承机制：通过 `_base_ = '../deeplabv3/deeplabv3_r50_512x1024_40ki_cityscapes.py'` 方式继承已有方法配置，再覆写差异字段，实现变体管理。
- 对于全新的方法结构（与现有方法均不共享结构），需在 `configs` 下新建 `xxxnet` 文件夹。

**PSPNet 模型数据流（原文示例）：**

| 模块 | 输入通道 | 输入索引 | 中间通道 | 损失权重 |
|------|---------|---------|---------|---------|
| backbone (ResNetV1c) | RGB 图像 | - | 多尺度特征 | - |
| decode_head (PSPHead) | 2048 | 3 | 512 | 1.0 |
| auxiliary_head (FCNHead) | 1024 | 2 | 256 | 0.4 |

**训练增强流水线顺序（原文）：**
`LoadImageFromFile` → `LoadAnnotations` → `Resize(img_scale=(2048,1024), ratio_range=(0.5,2.0))` → `RandomCrop((512,1024), cat_max_ratio=0.75)` → `RandomFlip(ratio=0.5)` → `PhotoMetricDistortion` → `Normalize` → `Pad((512,1024), pad_val=0, seg_pad_val=255)` → `DefaultFormatBundle` → `Collect(keys=['img','gt_semantic_seg'])`。

---

## 【表格解读】

原文无表格。

（文档主体为代码块与说明文字，未出现结构化表格。原文中唯一的"格式示意"为配置命名模板 `{model}_{backbone}_[misc]_[gpu x batch_per_gpu]_{resolution}_{iterations}_{dataset}`，并非表格形式。）

---

## 【公式解读】

原文无公式。

（文档未涉及任何数学公式或伪代码表达式，仅包含配置字段的定义与说明。）

---

## 【关联】

**与文中提到的其他模块/上下游关系：**

- **`mmcv` 配置系统**：原文末尾指向 `https://mmcv.readthedocs.io/en/latest/understand_mmcv/config.html`，作为配置文件机制的底层依赖文档；MMSegmentation 的配置系统构建于 mmcv 之上。

- **`mmseg/models/backbones/resnet.py`**：在 PSPNet 示例注释中被引用，提供 `ResNetV1c` 骨干类型的实现细节。

- **`mmseg/models/decode_heads`**：在 `PSPHead` 与 `FCNHead` 的注释中均被引用，作为可用解码头/辅助头类型的来源目录。

- **已有方法配置**：以 DeepLabV3 为例（`_base_ = ../deeplabv3/deeplabv3_r50_512x1024_40ki_cityscapes.py`），演示如何继承既有方法作为新方法变体的起点。

- **`config/_base_`**：作为四种基础组件（dataset、model、schedule、default_runtime）的存放目录，是所有 primitive 配置的来源。

- **`tools/print_config.py`**：作为配置检查工具被引用，是与配置系统直接交互的入口。

- **数据集生态**：命名规范中提到的 `cityscapes`、`voc12aug`、`ade` 三类数据集，对应 PSPNet 示例中的 `num_classes`（19 / 21 / 150）。

---

## 【使用方法】

**1. 查看完整配置（原文）：**

```bash
python tools/print_config.py /PATH/TO/CONFIG
```

**2. 命令行覆盖配置字段（原文）：**

```bash
python tools/print_config.py /PATH/TO/CONFIG --cfg-options xxx.yyy=zzz
```

**3. 基于已有方法构建变体（原文）：**

新建配置文件，指定 `_base_` 指向目标方法配置，再覆写差异字段。例如在 DeepLabV3 基础上修改：

```python
_base_ = '../deeplabv3/deeplabv3_r50_512x1024_40ki_cityscapes.py'
# 然后覆写需要修改的字段
```

**4. 全新方法结构（原文）：**

在 `configs` 下新建 `xxxnet` 文件夹组织配置文件。

**5. PSPNet 示例的关键配置项（原文已给出，可直接复用）：**

- `norm_cfg = dict(type='SyncBN', requires_grad=True)`
- 骨干 `pretrained='open-mmlab://resnet50_v1c'`
- 测试模式 `test_cfg = dict(mode='whole')`（选项：`'whole'` 整图全卷积测试 / `'sliding'` 滑窗测试）
- 数据归一化 `mean=[123.675, 116.28, 103.53]`、`std=[58.395, 57.12, 57.375]`、`to_rgb=True`
- 类别数依据数据集设定：`cityscapes=19`、`VOC=21`、`ADE20k=150`
