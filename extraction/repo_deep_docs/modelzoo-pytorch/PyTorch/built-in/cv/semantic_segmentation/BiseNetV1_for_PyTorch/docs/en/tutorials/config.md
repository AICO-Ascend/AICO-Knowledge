# Tutorial 1: Learn about Configs

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/en/tutorials/config.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/en/tutorials/config.md

# 一体化深度解读:BiseNetV1_for_PyTorch Configs Tutorial

---

## 【定位】

这篇文档是 `BiseNetV1_for_PyTorch` (基于 mmsegmentation 风格) 配置系统的入门教程,旨在让使用者理解该框架如何通过**模块化(modular)+ 继承(inheritance)**的方式组织实验配置文件,从而能够快速派生、修改和复用已有模型 (如 PSPNet、DeepLabV3 等) 的配置。

---

## 【技术要点】

1. **配置系统的设计理念**:采用模块化(modular)+继承(inheritance)双机制,便于开展各种实验;通过 `python tools/print_config.py /PATH/TO/CONFIG` 查看完整配置,并可通过 `--cfg-options xxx.yyy=zzz` 临时覆盖参数进行调试。
2. **四大基础组件类型**:位于 `config/_base_` 下,分别为 `dataset`、`model`、`schedule`、`default_runtime`;多数模型 (如 DeepLabV3、PSPNet) 可由这四类各一份组合而成,称为 **primitive** (原始) 配置。
3. **继承层级限制**:同一文件夹下建议**仅保留一个** primitive 配置,其它配置通过 `_base_` 继承,最大继承层级为 **3 层**;鼓励基于已有方法 (例如 DeepLabV3) 继承后修改字段。
4. **配置文件命名规范**:`{model}_{backbone}_[misc]_[gpu x batch_per_gpu]_{resolution}_{iterations}_{dataset}`,其中 `{xxx}` 必填、`[yyy]` 可选,例如 `psp_r50_512x1024_40ki_cityscapes.py`。
5. **PSPNet 完整示例**:`EncoderDecoder` 分割器 + `ResNetV1c` 主干 (depth=50, 4 stages, dilations=(1,1,2,4)) + `PSPHead` 解码头 (pool_scales=(1,2,3,6)) + `FCNHead` 辅助头 (loss_weight=0.4)。
6. **训练/测试管线 (pipeline)**:训练包含 `LoadImageFromFile → LoadAnnotations → Resize → RandomCrop → RandomFlip → PhotoMetricDistortion → Normalize → Pad → DefaultFormatBundle → Collect`;测试模式支持 `'whole'` (整图全卷积) 和 `'sliding'` (滑窗裁剪)。

---

## 【关键机制与数据】

### 配置继承工作原理 (原文)

- **继承入口**:在配置文件中通过 `_base_ = ../deeplabv3/deeplabv3_r50_512x1024_40ki_cityscapes.py` 引用父配置。
- **字段覆盖**:子配置可覆盖父配置中的任何 dict 字段,例如修改 `decode_head`、`auxiliary_head`、`train_pipeline` 等。
- **同步批归一化 (SyncBN)**:语义分割通常使用 `SyncBN`,即 `norm_cfg = dict(type='SyncBN', requires_grad=True)`,用于跨 GPU 同步统计量。

### 模型字段关键数据 (原文)

- **backbone**:`ResNetV1c`, `depth=50`, `num_stages=4`, `out_indices=(0,1,2,3)`, `dilations=(1,1,2,4)`, `strides=(1,2,1,1)`, `norm_eval=False`, `style='pytorch'`, `contract_dilation=True`。
- **pretrained**:`open-mmlab://resnet50_v1c` (ImageNet 预训练权重)。
- **decode_head (PSPHead)**:`in_channels=2048`, `in_index=3`, `channels=512`, `pool_scales=(1,2,3,6)`, `dropout_ratio=0.1`, `num_classes=19` (Cityscapes)。
- **auxiliary_head (FCNHead)**:`in_channels=1024`, `in_index=2`, `channels=256`, `num_convs=1`, `dropout_ratio=0.1`, `loss_weight=0.4`。
- **loss_decode**:`CrossEntropyLoss`, `use_sigmoid=False`, 主头 `loss_weight=1.0`, 辅助头 `loss_weight=0.4`。

### 数据/归一化参数 (原文)

- **dataset**:`dataset_type='CityscapesDataset'`, `data_root='data/cityscapes/'`。
- **img_norm_cfg**:`mean=[123.675, 116.28, 103.53]`, `std=[58.395, 57.12, 57.375]`, `to_rgb=True` (与预训练 backbone 一致)。
- **crop_size**:`(512, 1024)`。
- **train_pipeline 增强**:`Resize(img_scale=(2048,1024), ratio_range=(0.5,2.0))`, `RandomCrop(crop_size=(512,1024), cat_max_ratio=0.75)`, `RandomFlip(flip_ratio=0.5)`。
- **Pad 参数**:`size=(512,1024)`, `pad_val=0`, `seg_pad_val=255` (255 为忽略标签)。

### 测试模式 (原文)

- `test_cfg = dict(mode='whole')`:`'whole'` 为整图全卷积测试,`'sliding'` 为滑窗裁剪测试。
- `MultiScaleFlipAug` 用作测试时增强的封装,`img_scale=(2048,1024)` 决定最大测试尺度。

---

## 【表格解读】

**原文无表格。**

(原文中所有结构化信息均以 Python dict/列表形式给出,如 `model = dict(...)`、`train_pipeline = [...]`,未使用 markdown 表格呈现。)

---

## 【公式解读】

**原文无公式。**

(文档为配置说明,不涉及数学公式或 LaTeX 表达式。)

---

## 【关联】

- **上游框架依赖**:文档末尾引用了 `mmcv` 的 config 文档 `https://mmcv.readthedocs.io/en/latest/understand_mmcv/config.html`,作为配置系统的底层规范来源。
- **同系列模型引用**:示例以 **PSPNet + ResNet50V1c** 为完整示范,同时提及 **DeepLabV3** 作为继承示例 (`_base_ = ../deeplabv3/deeplabv3_r50_512x1024_40ki_cityscapes.py`),说明该配置体系可平滑迁移到其它语义分割模型。
- **下游模块位置提示**:
  - backbone 实现见 `mmseg/models/backbones/resnet.py`。
  - 解码头/辅助头实现见 `mmseg/models/decode_heads`(PSPHead、FCNHead)。
- **数据集映射关系**:示例中说明 `num_classes` 在 Cityscapes=19、VOC=21、ADE20k=150 之间随数据集切换;`crop_size=(512,1024)` 与 Cityscapes 高分辨率图像的典型配置对应。
- **BiseNetV1 自身**:本文档位于 `BiseNetV1_for_PyTorch/docs/`,是为该模型配置提供基础设施支持的通用教程,具体 BiseNetV1 的 config 应在 `configs/` 子目录下按本规范派生。
- **(无) 内部链接**:文档内未提供指向同仓其它 md 文件的内部链接。

---

## 【使用方法】

### 1. 查看完整配置 (原文)
```bash
python tools/print_config.py /PATH/TO/CONFIG
```

### 2. 临时覆盖配置项进行调试 (原文)
```bash
python tools/print_config.py /PATH/TO/CONFIG --cfg-options xxx.yyy=zzz
```

### 3. 基于已有方法派生新配置 (原文)

- **场景 A — 基于现有方法微调**:在子配置中写
  ```python
  _base_ = ../deeplabv3/deeplabv3_r50_512x1024_40ki_cityscapes.py
  ```
  然后仅覆盖需要修改的字段。
- **场景 B — 全新方法**:在 `configs/` 下创建 `xxxnet` 文件夹,自行组合 `dataset / model / schedule / default_runtime` 四类基础组件。

### 4. 命名规范 (原文)

格式:`{model}_{backbone}_[misc]_[gpu x batch_per_gpu]_{resolution}_{iterations}_{dataset}`

字段说明:
- `{model}`:模型类型,如 `psp`、`deeplabv3`。
- `{backbone}`:主干类型,如 `r50` (ResNet-50)、`x101` (ResNeXt-101)。
- `[misc]`:杂项/插件,如 `dconv`、`gcb`、`attention`、`mstrain`。
- `[gpu x batch_per_gpu]`:GPU 数 × 每 GPU batch,默认 `8x2`。
- `{iterations}`:训练迭代数,如 `160k`。
- `{dataset}`:数据集,如 `cityscapes`、`voc12aug`、`ade`。

### 5. 测试模式切换 (原文)
```python
test_cfg = dict(mode='whole')   # 整图全卷积
test_cfg = dict(mode='sliding') # 滑窗裁剪
```
