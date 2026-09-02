# Tutorial 5: Training Tricks

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/en/tutorials/training_tricks.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/en/tutorials/training_tricks.md

# 一体化深度解读:MMSegmentation 训练技巧 (Training Tricks)

## 【定位】
本文档是 MMSegmentation 官方教程系列的第 5 篇,集中介绍五种**开箱即用的语义分割训练技巧**,包括分层学习率、在线难例挖掘 (OHEM)、类别平衡损失、多损失联合训练以及指定忽略标签索引,目的是在不改网络结构的前提下,通过损失/采样/优化层面的调节提升模型收敛速度与精度。

---

## 【技术要点】

1. **分层学习率 (Different LR for Backbone and Heads)**:通过 `optimizer.paramwise_cfg.custom_keys` 把任何名字中含 `'head'` 的参数组的学习率乘以 `lr_mult=10.`,使 head 的 LR 为 backbone 的 10 倍。
2. **在线难例挖掘 OHEM**:在 `decode_head` 中配置 `sampler=dict(type='OHEMPixelSampler', thresh=0.7, min_kept=100000)`;若未指定 `thresh`,则按 loss 取 top `min_kept` 个像素。
3. **类别平衡损失 (Class Balanced Loss)**:在 `loss_decode` 中通过 `class_weight=[...]` 给 19 个 Cityscapes 类别赋权,作为 `CrossEntropyLoss` 的 `weight` 参数传入。
4. **多损失联合训练 (Multiple Losses)**:在 `decode_head` 与 `auxiliary_head` 的 `loss_decode` 上同时挂载 `CrossEntropyLoss(loss_weight=1.0)` 与 `DiceLoss(loss_weight=3.0)`,以 1:3 加权求和;日志中以 `loss_name` 区分。
5. **忽略指定标签索引 (Ignore specified label index)**:在 `decode_head` / `auxiliary_head` 上设 `ignore_index=0`,并把 `CrossEntropyLoss` 的 `avg_non_ignore=True`,使均值只统计非忽略像素。
6. **命名约束**:`loss_name` 必须以 `loss_` 前缀开头,否则不会进入反向传播图。

---

## 【关键机制与数据】

- **分层 LR 数据流**:`optimizer.paramwise_cfg.custom_keys['head']['lr_mult']=10.` → MMCV 的 `DefaultOptimizerConstructor` 遍历参数组,匹配 `'head'` 子串的参数名 → 把对应参数的 base LR ×10 后写入优化器。原文:"the LR of any parameter group with `'head'` in name will be multiplied by 10."
- **OHEM 采样数据流**:`OHEMPixelSampler` 按像素置信度 (或 loss) 筛选 → 保留置信度 < `0.7` 的像素,且每张图至少保留 `100000` 像素。原文:"only pixels with confidence score under 0.7 are used to train. And we keep at least 100000 pixels during training. If `thresh` is not specified, pixels of top `min_kept` loss will be selected."
- **类别平衡数据流**:`class_weight` (19 维,对应 Cityscapes 19 类) → `CrossEntropyLoss(weight=class_weight)` → 类别出现频率低时该类 loss 被放大、频率高时被压缩。
- **多损失数据流**:`loss_ce` (CE, ×1.0) 与 `loss_dice` (Dice, ×3.0) 在 `decode_head` 与 `auxiliary_head` 内**独立计算**,各自 head 求和后再汇总;`loss_name` 同时作为日志键。
- **忽略标签数据流**:label==`ignore_index` (此处为 0,背景) 的像素 **不计入 loss 平均分母** (在 `avg_non_ignore=True` 下),但仍参与前向以维持张量形状。原文:"each pixel counts for loss calculation" (默认) → 切到 `avg_non_ignore=True` 后 "the average loss would only be calculated in non-ignored labels"。
- **性能相关数字** (原文直接出现):
  - 19 个 Cityscapes 类别权重:`[0.8373, 0.9180, 0.8660, 1.0345, 1.0166, 0.9969, 0.9754, 1.0489, 0.8786, 1.0023, 0.9539, 0.9843, 1.1116, 0.9037, 1.0865, 1.0955, 1.0865, 1.1529, 1.0507]` (原文标注 "DeepLab used this class weight for cityscapes")。
  - OHEM 阈值 `0.7`、最小保留像素数 `100000`。
  - 多损失权重比 CE:Dice = 1:3。

---

## 【表格解读】

**原文无表格**。文中以 Python 配置代码块的形式给出各技巧的开关方法,不包含显式表格结构(无参数表/性能对比表/配置项表)。可视为每段代码块对应一个"配置小卡",但不属于表格。

---

## 【公式解读】

**原文无显式数学公式**。但文档隐含若干公式化关系,按伪代码/数学式逐字还原:

1. **分层 LR**
$$
\text{LR}_{\text{param}} = \text{LR}_{\text{base}} \cdot \text{lr\_mult}, \quad \text{lr\_mult} = \begin{cases} 10, & \text{if ``head''} \in \text{param\_name} \\ 1, & \text{otherwise} \end{cases}
$$
符号含义:`LR_param` 该参数实际学习率;`LR_base` 优化器基准学习率;`lr_mult` 来自 `paramwise_cfg.custom_keys['head']['lr_mult']` (示例值 10.)。

2. **OHEM 像素筛选**
$$
\mathcal{P}_{\text{kept}} = \begin{cases} \{p : \text{conf}(p) < 0.7\}, & \text{if thresh specified} \\ \text{top-}K(\text{loss}, K=100000), & \text{otherwise} \end{cases}
$$
符号含义:`P_kept` 保留下来的像素集合;`conf(p)` 像素置信度;`K = min_kept = 100000`。

3. **类别平衡加权 CE**
$$
\mathcal{L}_{\text{CE}}^{\text{bal}} = -\frac{1}{N}\sum_{i=1}^{N} w_{y_i}\log \frac{\exp(z_{y_i})}{\sum_c \exp(z_c)},\quad w_{y_i} = \text{class\_weight}[y_i]
$$
符号含义:`w_{y_i}` 即 19 维 `class_weight` 中对应真值类 `y_i` 的权重;`z_c` 第 `c` 类 logit。

4. **多损失加权和**
$$
\mathcal{L}_{\text{total}} = \underbrace{1.0}_{\text{CE weight}} \cdot \mathcal{L}_{\text{CE}} \;+\; \underbrace{3.0}_{\text{Dice weight}} \cdot \mathcal{L}_{\text{Dice}}
$$
符号含义:`loss_weight` 取自各 loss 字典中的 `loss_weight` 字段 (示例 1.0 与 3.0);同样公式在 `decode_head` 与 `auxiliary_head` 内各自独立计算。

5. **忽略索引平均 loss**
$$
\mathcal{L} = \frac{1}{|\{i: y_i \ne 0\}|}\sum_{i: y_i \ne 0} \ell_i
$$
符号含义:分母仅统计 `y_i != ignore_index` (此处 `ignore_index=0`、背景) 的像素;`avg_non_ignore=True` 时该公式生效。

---

## 【关联】

文档内/外引用的关键关联点:

- **MMCV `DefaultOptimizerConstructor`**:分层 LR 依赖该优化器构造器按参数名匹配并乘系数,详见 https://mmcv.readthedocs.io/en/latest/api.html#mmcv.runner.DefaultOptimizerConstructor 。
- **PyTorch `torch.nn.CrossEntropyLoss`**:文档把 `class_weight` 透传为其 `weight` 参数,行为遵循 PyTorch 官方定义 (https://pytorch.org/docs/stable/nn.html?highlight=crossentropy#torch.nn.CrossEntropyLoss )。
- **`mmseg/core/seg/sampler`**:OHEM 的像素采样器实现位置,链接 https://github.com/open-mmlab/mmsegmentation/tree/master/mmseg/core/seg/sampler 。
- **PR #1409**:`avg_non_ignore` 与 `ignore_index` 实现的来源 (https://github.com/open-mmlab/mmsegmentation/pull/1409 ),用于在 loss 计算时按非忽略像素求平均。
- **下游配置文件**:每条技巧都基于已有的 base config 继承并就地修改,如 `./pspnet_r50-d8_512x1024_40k_cityscapes.py`、`./fcn_unet_s5-d16_64x64_40k_drive.py`、`./fcn_unet_s5-d16_4x4_512x1024_160k_cityscapes.py`,表明这些技巧可与任意 head (PSPNet、UNet) 组合。
- **辅助头 `auxiliary_head`**:多损失与忽略索引两节都同时配置 `decode_head` 与 `auxiliary_head`,说明这些技巧可作用于主 head 与辅助 head 两侧。
- **同系列教程**:标题为 "Tutorial 5",暗示存在 Tutorial 1–4 的姊妹文档 (原文未给出链接,仅以序号表达顺序)。

---

## 【使用方法】

以下五项均通过**继承并修改**对应 base config 的方式启用,无需改动代码:

1. **分层 LR** — 在 config 中:
   ```python
   optimizer=dict(
       paramwise_cfg = dict(
           custom_keys={'head': dict(lr_mult=10.)}))
   ```
2. **OHEM** — 在 `model.decode_head` 加采样器 (以 PSPNet+Cityscapes 为例):
   ```python
   _base_ = './pspnet_r50-d8_512x1024_40k_cityscapes.py'
   model=dict(
       decode_head=dict(
           sampler=dict(type='OHEMPixelSampler', thresh=0.7, min_kept=100000)))
   ```
   不指定 `thresh` 时自动切换为 top-`min_kept` loss 模式。
3. **类别平衡 Loss** — 在 `model.decode_head.loss_decode` 设 19 维 `class_weight` (以 PSPNet+Cityscapes 为例,见上原文列表)。
4. **多损失** — 在 `decode_head` 与 `auxiliary_head` 的 `loss_decode` 上并列配置 `CrossEntropyLoss` 与 `DiceLoss` (以 UNet+DRIVE 为例,权重 1.0 与 3.0);`loss_name` 必须以 `loss_` 为前缀才能进入反向图与日志。
5. **忽略指定标签** — 在 `decode_head` / `auxiliary_head` 上设 `ignore_index=0`,并在 `CrossEntropyLoss` 字典中加 `avg_non_ignore=True` (以 UNet+Cityscapes 为例)。

原文未给出独立的 CLI 启用命令或超参脚本路径,所有启用方式均通过 Python 配置 `_base_` 继承 + 字段覆盖完成。
