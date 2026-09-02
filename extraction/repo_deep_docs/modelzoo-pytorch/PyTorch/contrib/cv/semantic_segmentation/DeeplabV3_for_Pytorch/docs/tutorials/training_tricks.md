# Tutorial 5: Training Tricks

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs/tutorials/training_tricks.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs/tutorials/training_tricks.md

# 一体化深度解读：Tutorial 5 — Training Tricks

## 【定位】
本文档是 MMSegmentation 框架中关于**语义分割模型训练技巧（Training Tricks）的开箱即用指南**，系统讲解了三种可显著改善分割模型训练效果或收敛速度的内置机制：差异化学习率（Backbone vs Heads）、在线困难样本挖掘（OHEM）、类别平衡损失（Class Balanced Loss），并以 PSPNet + Cityscapes 配置为示范给出可直接复用的 config 片段。

---

## 【技术要点】

1. **差异化学习率（Different LR for Backbone and Heads）**：在语义分割中常让 head 的学习率大于 backbone 以获得更好性能/更快收敛；通过 `optimizer.paramwise_cfg.custom_keys` 配置 `'head': dict(lr_mult=10.)`，使名称中含 `head` 的参数组学习率乘以 10。
2. **在线困难样本挖掘（OHEM）**：通过 `mmseg/core/seg/sampler` 实现的 pixel sampler 过滤低置信度像素；示例 config 在 PSPNet decode_head 中启用 `OHEMPixelSampler(thresh=0.7, min_kept=100000)`，即仅用置信度 < 0.7 的像素训练，且至少保留 100000 个像素。
3. **OHEM 兜底策略**：若不指定 `thresh`，则按 loss 值选取 top-`min_kept` 个像素（即选 loss 最大的困难像素）。
4. **类别平衡损失（Class Balanced Loss）**：通过在 `CrossEntropyLoss` 中传入 `class_weight` 列表改变每类权重；文档以 Cityscapes 19 类为例给出 DeepLab 采用的具体权重数组（19 个浮点数）。
5. **跨工程集成**：`class_weight` 直接作为 `weight` 参数传入 PyTorch `torch.nn.CrossEntropyLoss`；`lr_mult` 机制遵循 MMCV 的 `DefaultOptimizerConstructor`。
6. **继承式配置**：所有示例 config 均通过 `_base_` 继承自 `./pspnet_r50-d8_512x1024_40k_cityscapes.py`，仅覆写需要的字段，体现 MMSegmentation 的 config 继承体系。

---

## 【关键机制与数据】

### 机制一：Paramwise 学习率乘子
- **工作原理**：MMCV 的 `DefaultOptimizerConstructor` 在构建 optimizer 时会扫描参数名，匹配到 `custom_keys` 中声明的子串后，对其参数组的 `lr` 乘以 `lr_mult`。
- **关键参数**：原文为 `lr_mult=10.`，即 head 的学习率 = 基础学习率 × 10。
- **匹配规则**：原文明确写明「any parameter group with `'head'` in name will be multiplied by 10」，即按子串匹配而非精确字段匹配。
- **原文**："you may add following lines to config to make the LR of heads 10 times of backbone."

### 机制二：OHEM 像素采样
- **数据流**：训练时前向推理得到每个像素的置信度（confidence score）→ `OHEMPixelSampler` 过滤出置信度 < `thresh` 的像素 → 保证参与训练的像素数 ≥ `min_kept`。
- **关键参数**：
  - `thresh=0.7`（置信度阈值）
  - `min_kept=100000`（最少保留像素数）
- **兜底逻辑**：未指定 `thresh` 时按 loss 降序取 top-`min_kept` 像素——即直接选最难的像素。
- **原文**："only pixels with confidence score under 0.7 are used to train. And we keep at least 100000 pixels during training."

### 机制三：类别平衡 Loss
- **工作原理**：`class_weight` 列表作为 PyTorch `CrossEntropyLoss` 的 `weight` 参数传入，对每个类别的 loss 进行加权，补偿数据集类别分布不均。
- **关键参数**：`CrossEntropyLoss(use_sigmoid=False, loss_weight=1.0)` + 19 个类别权重。
- **权重数据**（原文逐字保留）：
  ```
  [0.8373, 0.9180, 0.8660, 1.0345, 1.0166, 0.9969, 0.9754,
   1.0489, 0.8786, 1.0023, 0.9539, 0.9843, 1.1116, 0.9037,
   1.0865, 1.0955, 1.0865, 1.1529, 1.0507]
  ```
  - 原文标注：「DeepLab used this class weight for cityscapes」，即这组数值源自 DeepLab 在 Cityscapes 上的实践，非本文档新设计。
  - 19 个数值对应 Cityscapes 的 19 个评估类别。

---

## 【表格解读】

**原文无表格**。本文档所有配置均以代码块形式给出，未出现 markdown 表格结构。

---

## 【公式解读】

**原文无公式**。文档中未出现 LaTeX 公式或伪代码数学表达式，所有数值与机制均通过代码 config 与文字描述传达。

---

## 【关联】

- **上游框架依赖**：
  - **MMCV**：学习率乘子机制由 `mmcv.runner.DefaultOptimizerConstructor` 提供；文档显式给出外链 `https://mmcv.readthedocs.io/en/latest/api.html#mmcv.runner.DefaultOptimizerConstructor`。
  - **PyTorch**：`class_weight` 透传到 `torch.nn.CrossEntropyLoss(weight=...)`；文档给出外链 `https://pytorch.org/docs/stable/nn.html?highlight=crossentropy#torch.nn.CrossEntropyLoss`。
- **本仓（mmsegmentation）内的模块**：
  - **OHEM Pixel Sampler**：实现位于 `https://github.com/open-mmlab/mmsegmentation/tree/master/mmseg/core/seg/sampler`（原文外链）。
  - **基础 config**：`./pspnet_r50-d8_512x1024_40k_cityscapes.py` 被三处示例反复继承，是这些训练技巧的载体模型（PSPNet, ResNet-50 backbone, 512×1024 输入, 40k iter, Cityscapes 数据集）。
- **下游调用点**：
  - 三种技巧的注入点都落在 `model.decode_head` 字段下：
    - OHEM → `decode_head.sampler`
    - 类别平衡 → `decode_head.loss_decode.class_weight`
    - 学习率乘子 → 全局 `optimizer.paramwise_cfg`，但通过 `'head'` 子串匹配 head 区域参数。
- **跨文档关系**：作为 "Tutorial 5"，承接 Tutorial 1-4 的 config 体系，向后应衔接 Tutorial 6+ 的内容（本文档未给出内部链接，但根据序号推断属 MMSegmentation 教程系列）。

---

## 【使用方法】

文档给出了三种技巧的启用方式（均为 config 层级修改）：

### 1. 差异化学习率
在 config 的 `optimizer` 字段中添加 `paramwise_cfg`：
```python
optimizer=dict(
    paramwise_cfg=dict(
        custom_keys={
            'head': dict(lr_mult=10.)}))
```
- **生效范围**：所有名称含 `'head'` 的参数。
- **可调参数**：`lr_mult`（可改为其他倍率，如 5.、20.）。

### 2. OHEM
在基础 config 上覆写 `model.decode_head.sampler`：
```python
_base_ = './pspnet_r50-d8_512x1024_40k_cityscapes.py'
model=dict(
    decode_head=dict(
        sampler=dict(type='OHEMPixelSampler', thresh=0.7, min_kept=100000)))
```
- **可调参数**：`thresh`（置信度阈值，0~1）、`min_kept`（最少保留像素数）；不指定 `thresh` 则切换为 top-loss 选取模式。

### 3. 类别平衡 Loss
在基础 config 上覆写 `model.decode_head.loss_decode`：
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
- **可调参数**：`class_weight` 列表（必须与数据集类别数一致，Cityscapes 为 19）；`use_sigmoid`（文档写 `False`，表明走 softmax 路径）；`loss_weight`（loss 总权重，文档写 1.0）。

> **注意**：文档未涉及命令行启动方式、超参搜索范围或性能基准数字——以上均为「原文未涉及」。
