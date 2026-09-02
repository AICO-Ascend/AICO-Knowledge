# 教程 5: 训练技巧

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/zh_cn/tutorials/training_tricks.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/zh_cn/tutorials/training_tricks.md

# 《训练技巧 (Tutorial 5: Training Tricks)》深度解读

---

## 【定位】

这篇文档是 MMSegmentation（语义分割框架）的教程 5，集中描述 **"如何通过配置文件层面的修改，提升语义分割模型的训练效果/收敛速度"** 的若干经验性技巧，主干—解码头分组学习率、OHEM 难样本挖掘、类别平衡损失、多损失加权求和、按需忽略特定 label 这类工程化手段。原文均以 `_base_` 继承 + `model=dict(decode_head=...)` 的 MMConfig 字段覆盖方式给出具体写法。

---

## 【技术要点】

1. **分组学习率 (LR multiplier for head)**：通过 `optimizer.paramwise_cfg.custom_keys` 把 `'head'` 模块参数的 `lr_mult` 设为 `10.`，让解码头学习率是主干网络的 10 倍。底层实现依赖 MMCV 的 `DefaultOptimizerConstructor`。
2. **OHEM 像素采样 (Online Hard Example Mining)**：在 `decode_head.sampler` 中指定 `type='OHEMPixelSampler'`；`thresh=0.7`（置信分数阈值，低于此值的像素参与训练）；`min_kept=100000`（最少保留像素数）。若未设 `thresh`，则按 loss 排序的前 `min_kept` 个像素被选中。
3. **类别平衡损失 (Class Balanced Loss)**：在 `CrossEntropyLoss` 中通过 `class_weight=[…]` 传入 19 个浮点数（Cityscapes 19 类），作为 `weight` 参数传递给 `CrossEntropyLoss`。注释明确说明这是 "DeepLab 对 cityscapes 使用的权重"。
4. **多损失同时训练 (Multiple Losses)**：`loss_decode` 可以是 **list**，每个元素是一个独立的损失字典；以 UNet + DRIVE 为例，使用 `CrossEntropyLoss` (`loss_weight=1.0`) 与 `DiceLoss` (`loss_weight=3.0`) **1:3 加权求和**。每个损失需指定 `loss_name`，并 **必须以 `loss_` 为前缀**，才能被纳入反向传播图。
5. **按类别忽略 label (Ignore specific labels)**：默认 `avg_non_ignore=False`；开启方式为在 `decode_head` / `auxiliary_head` 同时设置 `ignore_index=0` 与 `loss_decode=dict(avg_non_ignore=True)`，使损失只在非忽略像素上求平均。原文给出对应 PR 链接 (`mmsegmentation/pull/1409`)。
6. **统一的配置模式**：所有技巧都遵循同一写法——`_base_ = 'xxx.py'` 继承基础配置，再用 `model=dict(decode_head=dict(...))` / `auxiliary_head=dict(...)` 字段覆盖，避免修改 baseline 全部配置。

---

## 【关键机制与数据】

- **分组 LR 的作用机理**：原文："任何被分组到 `'head'` 的参数的学习率都将乘以 10"；这是一种让高层解码模块更快更新、低层主干特征保持稳定的常见做法（出于"语义层需要更激进调整"的经验假设）。
- **OHEM 的双模式触发条件**：
  - 模式 A（指定 `thresh`）："只有置信分数在 0.7 以下的像素值点会被拿来训练"——按置信度过滤；
  - 模式 B（未指定 `thresh`）："前 `min_kept` 个损失的像素值点才会被选择"——按 loss 排序选难样本。
  - 兜底约束："训练时我们至少要保留 100000 个像素值点"（`min_kept`）。
- **Class Balanced Loss 的数据**：原文给出的 `class_weight` 列表共 **19 项**，覆盖 Cityscapes 19 个语义类别；注释明确 "DeepLab 对 cityscapes 使用这种权重"。具体数值原文一字未改。
- **多损失的加权策略**：原文："`CrossEntropyLoss` 和 `DiceLoss` 的 `1:3` 的加权和"——即 CE 占 1 份、Dice 占 3 份。命名约束原文："`loss_name` 的名字必须带有 `loss_` 前缀，这样它才能被包括在反传的图里"。
- **ignore_index 的作用范围**：原文示例以 Cityscapes label=0（背景）为忽略目标，并在 `decode_head` 与 `auxiliary_head` 两处都设置 `ignore_index=0`，表示对两条 head 分支都生效。
- **数据流（推断，原文未直接给出）**：所有配置修改均作用于 `decode_head`（部分含 `auxiliary_head`）；`sampler` 在 head 内部对像素做选择，`loss_decode` 在 head 前向之后计算 loss；`paramwise_cfg` 由 optimizer constructor 在参数分组阶段读取。性能数据原文未提供。

---

## 【表格解读】

**原文无表格**。文档以代码片段形式给出配置示例，未提供任何参数表/性能对比/配置项对照表。

---

## 【公式解读】

**原文无公式**。文档未使用 LaTeX 或伪代码形式的公式，仅给出 Python 配置字典形式。每个公式语义（如 CE/Dice 的 1:3 加权）是通过权重数字隐式表达，没有显式的 $\mathcal{L} = \alpha \mathcal{L}_{CE} + \beta \mathcal{L}_{Dice}$ 这类书写。

---

## 【关联】

- **MMCV 的 `DefaultOptimizerConstructor`**：分组学习率功能依赖此构造器，文档外链 `mmcv.readthedocs.io/en/latest/api.html#mmcv.runner.DefaultOptimizerConstructor`。  
- **`mmseg/core/seg/sampler`**：OHEM 像素采样的实现位置，原文外链 `github.com/open-mmlab/mmsegmentation/tree/master/mmseg/core/seg/sampler`。  
- **PyTorch 的 `torch.nn.CrossEntropyLoss`**：`class_weight` 的最终落点，原文外链 `pytorch.org/docs/stable/nn.html?highlight=crossentropy#torch.nn.CrossEntropyLoss`。  
- **MMConfig 配置继承**：所有技巧都依赖 `_base_ = './xxx.py'` 的配置继承机制，与教程体系中的其他配置文件（如 `pspnet_r50-d8_512x1024_40k_cityscapes.py`、`fcn_unet_s5-d16_64x64_40k_drive.py`、`fcn_unet_s5-d16_4x4_512x1024_160k_cityscapes.py`）存在基础配置依赖关系。  
- **辅助头 (`auxiliary_head`)**：多损失与 ignore_index 两节同时修改 `decode_head` 与 `auxiliary_head`，说明这些技巧适用于 **多 head（Deep Supervision）** 结构。  
- **关联 PR**：`mmsegmentation/pull/1409` 是 ignore_index + avg_non_ignore 特性的实现来源。  
- **内部链接**：原文标注 "(无)"，本节所列关联均为文中显式给出的外部/相对路径，未做推断。

---

## 【使用方法】

启用方式统一：在 MMConfig 中以 `_base_` 继承一个 baseline config，再用字段覆盖方式写入新 `model` / `optimizer` 字段。具体配置项如下，均来自原文：

**① 分组 LR**
```python
optimizer=dict(
    paramwise_cfg = dict(
        custom_keys={
            'head': dict(lr_mult=10.)}))
```
将 `optimizer` 字段整体覆盖到 baseline 配置中即可。

**② OHEM**
```python
_base_ = './pspnet_r50-d8_512x1024_40k_cityscapes.py'
model=dict(
    decode_head=dict(
        sampler=dict(type='OHEMPixelSampler', thresh=0.7, min_kept=100000)))
```
可调项：`thresh`（置信阈值，省略时退化为 loss 排序模式）、`min_kept`（最少保留像素数）。

**③ 类别平衡损失**
```python
_base_ = './pspnet_r50-d8_512x1024_40k_cityscapes.py'
model=dict(
    decode_head=dict(
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0,
            class_weight=[0.8373, 0.9180, 0.8660, 1.0345, 1.0166, 0.9969, 0.9754,
                        1.0489, 0.8786, 1.0023, 0.9539, 0.9843, 1.1116, 0.9037,
                        1.0865, 1.0955, 1.0865, 1.1529, 1.0507])))
```
`class_weight` 长度需与类别数一致（Cityscapes 为 19）。

**④ 多损失**
```python
_base_ = './fcn_unet_s5-d16_64x64_40k_drive.py'
model = dict(
    decode_head=dict(loss_decode=[
        dict(type='CrossEntropyLoss', loss_name='loss_ce',   loss_weight=1.0),
        dict(type='DiceLoss',         loss_name='loss_dice', loss_weight=3.0)]),
    auxiliary_head=dict(loss_decode=[
        dict(type='CrossEntropyLoss', loss_name='loss_ce',   loss_weight=1.0),
        dict(type='DiceLoss',         loss_name='loss_dice', loss_weight=3.0)]),
)
```
注意：`loss_name` 必须以 `loss_` 为前缀，否则不会进入反向传播图。

**⑤ 忽略特定 label**
```python
_base_ = './fcn_unet_s5-d16_4x4_512x1024_160k_cityscapes.py'
model = dict(
    decode_head=dict(
        ignore_index=0,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0,
            avg_non_ignore=True)),
    auxiliary_head=dict(
        ignore_index=0,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0,
            avg_non_ignore=True)),
)
```
`avg_non_ignore=False` 为默认；启用 `avg_non_ignore=True` 后必须同时设置 `ignore_index`，损失才仅在非忽略像素上求平均。

原文未涉及 CLI 启动命令、性能基准或超参搜索脚本，所有启用均通过修改配置文件完成。
