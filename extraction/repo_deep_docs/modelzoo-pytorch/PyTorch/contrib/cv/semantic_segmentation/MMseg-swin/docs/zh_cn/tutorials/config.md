# 教程 1: 学习配置文件

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/zh_cn/tutorials/config.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/zh_cn/tutorials/config.md

# 深度解读：MMseg 配置文件教程（Tutorial 1: 学习配置文件）

---

## 【定位】

这篇文档是 MMseg（MMSegmentation）框架的**入门级教程**，系统讲解了**配置文件的结构组织、命名规范、组件继承机制**，并以 **PSPNet + ResNet50V1c** 为完整示例逐字段注释了语义分割任务的配置。它解决的核心问题是：**让使用者理解如何通过"组合 + 继承"的方式高效编写/复用语义分割实验配置**，降低算法复现与实验迭代的成本。

---

## 【技术要点】

1. **四大基础组件（`_base_`）**：在 `config/_base_` 目录下提供 4 种原子配置——
   - `dataset`（数据集）
   - `model`（模型）
   - `schedule`（训练策略）
   - `default runtime`（运行时的默认设置）
   
   通过组合这些组件即可构造 DeepLabV3、PSPNet 等完整模型，这种从原子组件拼装的配置被定义为"**原始配置（primitive）**"。

2. **三层继承深度上限**：同一文件夹内**只允许一个 primitive 文件**，其他配置文件都应继承自该 primitive，从而保证配置文件的**最大继承深度 ≤ 3**。社区贡献者被强烈建议基于已有方法配置（如 DeepLabV3）做继承，而不是从零写起。

3. **配置打印/覆盖命令行**：
   ```
   python tools/print_config.py /PATH/TO/CONFIG
   python tools/print_config.py /PATH/TO/CONFIG --cfg-options xxx.yyy=zzz
   ```
   `print_config.py` 用于展开并查看最终配置；`--cfg-options` 允许在不修改文件的情况下覆盖任意字段。

4. **配置命名规范（强制项 + 可选项）**：
   ```
   {model}_{backbone}_[misc]_[gpu x batch_per_gpu]_{resolution}_{iterations}_{dataset}
   ```
   - `{model}`：如 `psp`、`deeplabv3`
   - `{backbone}`：如 `r50`（ResNet-50）、`x101`（ResNeXt-101）
   - `[misc]`：可选插件/设置，如 `dconv`、`gcb`、`attention`、`mstrain`
   - `[gpu x batch_per_gpu]`：默认 `8x2`
   - `{iterations}`：如 `160k`
   - `{dataset}`：如 `cityscapes`、`voc12aug`、`ade`

5. **PSPNet（ResNet50V1c）示例关键参数**：
   - 主干：`ResNetV1c`，`depth=50`，`num_stages=4`，`out_indices=(0,1,2,3)`，`dilations=(1,1,2,4)`，`strides=(1,2,1,1)`
   - 归一化：`SyncBN`（`requires_grad=True`）
   - 解码头（`PSPHead`）：`in_channels=2048`，`in_index=3`，`channels=512`，`pool_scales=(1,2,3,6)`，`dropout_ratio=0.1`，`num_classes=19`（cityscapes），损失权重 `1.0`
   - 辅助头（`FCNHead`）：`in_channels=1024`，`in_index=2`，`num_convs=1`，`dropout_ratio=0.1`，`num_classes=19`，损失权重 `0.4`（默认）
   - 测试模式：`'whole'`（整图全卷积）或 `'sliding'`（滑窗裁剪）
   - 数据集：`CityscapesDataset`，`data_root='data/cityscapes/'`，`crop_size=(512,1024)`，`samples_per_gpu=2`，`workers_per_gpu=2`
   - 图像归一化：`mean=[123.675, 116.28, 103.53]`，`std=[58.395, 57.12, 57.375]`，`to_rgb=True`

6. **数据增广 pipeline 顺序**：训练流水线为有序列表，依次为 `LoadImageFromFile` → `LoadAnnotations` → `Resize(img_scale=(2048,1024), ratio_range=(0.5,2.0))` → `RandomCrop(crop_size=(512,1024), cat_max_ratio=0.75)` → `RandomFlip(flip_ratio=0.5)` → `PhotoMetricDistortion` → `Normalize` → `Pad(size=(512,1024), pad_val=0, seg_pad_val=255)` → `DefaultFormatBundle` → `Collect(keys=['img','gt_semantic_seg'])`。**测试时**则由 `MultiScaleFlipAug` 封装，可设置 `img_scale=(2048,1024)` 和 `flip=False/True` 组合多次增强。

---

## 【关键机制与数据】

**工作机制 / 数据流（基于原文）：**

1. **组合 + 继承的实验管理机制**：将"模型定义、数据集、增强、训练策略"四类要素原子化放入 `_base_/`，通过 `_base_ = '../deeplabv3/deeplabv3_r50_512x1024_40ki_cityscapes.py'` 的形式声明继承，再在子配置中**只覆盖需要变更的字段**。这与传统 OpenMMLab 风格一脉相承（原文链接到 [mmcv config 文档](https://mmcv.readthedocs.io/en/latest/understand_mmcv/config.html)）。

2. **完整分割器组成**（以 PSPNet 示例）：
   - `segmentor = EncoderDecoder`
     - 编码部分：`backbone = ResNetV1c(depth=50)`，通过 `pretrained='open-mmlab://resnet50_v1c'` 加载 ImageNet 预训练权重
     - 主干 4 个 stage 都会被取出（`out_indices=(0,1,2,3)`），其中 stride/dilation 有专门设置以适配语义分割（如 stage3 的 `dilation=4, stride=1`）
     - 解码部分：`decode_head = PSPHead`（基于多尺度池化 `pool_scales=(1,2,3,6)`）
     - 辅助监督：`auxiliary_head = FCNHead`，提供中间层辅助损失（`loss_weight=0.4`）

3. **测试两种模式**（原文）：
   - `'whole'`：整张图像全卷积（fully-convolutional）测试
   - `'sliding'`：在图像上做滑窗裁剪窗口（sliding crop window）测试
   两者统一通过 `test_cfg = dict(mode='whole')` 切换。

4. **类别数经验值**（原文）：cityscapes 为 19，VOC 为 21，ADE20k 为 150。

5. **图像预处理常数**（原文）：`mean=[123.675, 116.28, 103.53]`，`std=[58.395, 57.12, 57.375]`，由 ImageNet 预训练主干所需。

> 注：原文档**未提供**训练精度（如 mIoU）、参数量、推理速度等性能数据，因此本节不臆测。

---

## 【表格解读】

**原文无表格。**

原文中仅有配置命名规范的伪代码模板（`{model}_{backbone}_[misc]_[gpu x batch_per_gpu]_{resolution}_{iterations}_{dataset}`）以及 PSPNet 示例的 Python 配置字典，并不包含任何结构化表格（参数对照表、性能对比表等）。

---

## 【公式解读】

**原文无公式。**

文档仅以命名模板和 Python 字面量定义的形式描述配置，未出现 LaTeX 公式或伪代码形式的数学表达。

---

## 【关联】

**与本教程紧密相关的上下游模块/教程**（基于原文自身提及与 mmseg 生态的常规理解）：

1. **上游 / 数据源**：
   - `mmseg/datasets/`：定义 `CityscapesDataset` 等数据集类型（如 `dataset_type = 'CityscapesDataset'`）。
   - `mmseg/models/backbones/resnet.py`：定义 `ResNetV1c` 等主干网络类（供 `backbone.type` 引用）。
   - `mmseg/models/decode_heads`：定义 `PSPHead`、`FCNHead` 等解码头/辅助头类。
   - `mmcv`：[mmcv config 文档](https://mmcv.readthedocs.io/en/latest/understand_mmcv/config.html) 是配置文件语法的更底层说明，原文档推荐读者参照该链接。

2. **同系列其他教程**（基于标题"教程 1"推断）：
   - 本文档为 **Tutorial 1**，意味着 mmseg 文档体系中还有后续教程（如"自定义数据集"、"自定义模型"、"自定义损失/优化器"等）。**原文未列出具体内部链接**（任务注明"(无)"）。

3. **工具脚本**：
   - `tools/print_config.py` 是直接配套工具，用于展开并查看最终合并后的配置，配合 `--cfg-options key=value` 可在命令行直接覆盖任意字段。

4. **继承链路示例**：
   - 子配置 → primitive（如 `../deeplabv3/deeplabv3_r50_512x1024_40ki_cityscapes.py`）→ `_base_/` 下原子组件（dataset / model / schedule / runtime）
   - 在 subconfig 内通过 `_base_ = 'xxx.py'` 字段声明继承，遵循"**最大继承深度 ≤ 3**"的硬性约束。

---

## 【使用方法】

**1. 查看/打印某份配置文件的最终展开形式：**

```
python tools/print_config.py /PATH/TO/CONFIG
```

**2. 在查看时直接覆盖某个字段（无需修改文件）：**

```
python tools/print_config.py /PATH/TO/CONFIG --cfg-options xxx.yyy=zzz
```

**3. 新建一个实验配置的两种推荐方式（原文）：**

- **方式 A — 继承已有方法**：如果修改基于 DeepLabV3，先在子配置中写入
  ```
  _base_ = '../deeplabv3/deeplabv3_r50_512x1024_40ki_cityscapes.py'
  ```
  然后仅覆写需要变更的字段（学习率、数据增强、损失权重等）。

- **方式 B — 创建全新的方法族**：若新模型与已有方法毫无共享结构，需在 `configs/` 下新建一个 `xxxnet/` 文件夹，并将其作为独立 primitive 使用。

**4. 命名规范（强制遵循）：**

```
{model}_{backbone}_[misc]_[gpu x batch_per_gpu]_{resolution}_{iterations}_{dataset}
```

例如 `psp_r50_512x1024_40ki_cityscapes.py`：PSPNet 模型 + ResNet-50 主干 + 输入分辨率 512×1024 + 40k 次迭代 + cityscapes 数据集。`[misc]`（如 `dconv`、`attention`）、`[gpu x batch_per_gpu]`（默认 `8x2`）为可选项。

**5. 继承深度约束**：同一目录至多一个 primitive 文件，最大继承深度 **3 层**。

> 备注：原文档在 PSPNet 示例末尾以 `---` 截断（`test=dict(...` 部分未给出 `}` 闭合），但已展示的全部要素（`samples_per_gpu=2`、`workers_per_gpu=2`、完整 train/val/test `data` 字典与 pipeline）足以支撑上述方法的实施。**原文未涉及**模型训练的启动命令（如 `tools/train.py`）及具体的训练超参（lr、optimizer、schedule step），故此处不补充。
