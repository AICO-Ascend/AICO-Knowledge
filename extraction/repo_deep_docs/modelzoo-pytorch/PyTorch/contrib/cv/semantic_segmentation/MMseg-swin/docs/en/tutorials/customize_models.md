# Tutorial 4: Customize Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/en/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/en/tutorials/customize_models.md

# 《Tutorial 4: Customize Models》深度解读

---

## 【定位】

本文是 MMSegmentation（Swin-MMseg 变体）的**模型自定义教程**，系统说明如何在该语义分割框架中扩展或替换三类核心组件——**优化器（Optimizer）**、**网络模块（Backbone / Decode Head）**、**损失函数（Loss）**，以及如何实现参数级细粒度的**优化器构造器（Optimizer Constructor）**，从而把框架的开放性下沉到训练全流程的每一环。

---

## 【技术要点】

1. **优化器注册机制**：通过 `@OPTIMIZERS.register_module` 装饰器把继承自 `torch.optim.Optimizer` 的自定义类注册到注册表，并在 `mmseg/core/optimizer/__init__.py` 中显式 `import`，即可被配置文件的 `optimizer` 字段以 `type='MyOptimizer'` 形式调用。

2. **PyTorch 优化器开箱即用**：所有 PyTorch 原生优化器可直接切换，仅需改 config 字段。原文给出示例：原文:"SGD, lr=0.02, momentum=0.9, weight_decay=0.0001" 与 "Adam, lr=0.0003, weight_decay=0.0001"。

3. **优化器构造器（Optimizer Constructor）**：使用 `@OPTIMIZER_BUILDERS.register_module` 注册，类需实现 `__init__(optimizer_cfg, paramwise_cfg=None)` 与 `__call__(model)`，返回构造好的 optimizer 实例，作用对象是参数组（param-wise）级别的细粒度配置（例如 BatchNorm 层的 weight decay 单独设置）。

4. **新 Backbone 注册约定**：放在 `mmseg/models/backbones/` 下，使用 `@BACKBONES.register_module` 装饰器，必须实现 `__init__`、`forward`（**返回值应为 tuple**，原文明示"should return a tuple"）、`init_weights(pretrained=None)` 三方法，并在 `backbones/__init__.py` 中导入。

5. **新 Decode Head 继承约定**：所有新分割头必须派生自 **BaseDecodeHead**（原文给出 github 链接），典型示例为 PSPHead，其 `__init__` 接受 `pool_scales=(1, 2, 3, 6)`，并需实现 `init_weights()` 与 `forward(inputs)`；并在 `mmseg/models/decode_heads/__init__.py` 中暴露。

6. **新 Loss 注册机制**：损失函数定义在 `mmseg/models/losses/` 下；用 `@weighted_loss` 装饰函数层（支持逐元素加权），用 `@LOSSES.register_module` 装饰类层；类内 `forward` 必须支持 `reduction_override`（取值集合为 `(None, 'none', 'mean', 'sum')`），并通过 `loss_weight`（默认 1.0）与其它损失平衡。

---

## 【关键机制与数据】

- **优化器调用数据流**：原文:"the optimizers are defined by the field `optimizer`"，配置 → 注册表查找（registry）→ 实例化。即 `optimizer = dict(type=..., ...)` 这种声明式写法由 mmcv runner 在构建训练器时解析。
- **Head 注册数据流**：PSPNet config 中 `model = dict(type='EncoderDecoder', ..., backbone=..., decode_head=...)`，通过 `type='PSPHead'` 字符串触发注册表反查；`decode_head` 中还嵌套了 `loss_decode=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0)`，构成"head + loss"的耦合声明。
- **PSPHead 原文配置关键数（原文）**：
  - `in_channels=2048`
  - `in_index=3`
  - `channels=512`
  - `pool_scales=(1, 2, 3, 6)`
  - `dropout_ratio=0.1`
  - `num_classes=19`
  - `align_corners=False`
- **配套 Backbone (ResNetV1c) 关键数（原文）**：
  - `depth=50`, `num_stages=4`
  - `out_indices=(0, 1, 2, 3)`
  - `dilations=(1, 1, 2, 4)`, `strides=(1, 2, 1, 1)`
  - `style='pytorch'`, `contract_dilation=True`, `norm_eval=False`
  - `norm_cfg=dict(type='SyncBN', requires_grad=True)`
  - 预训练权重路径 `pretrain_model/resnet50_v1c_trick-2cccc1ad.pth`
- **Loss 装饰器链路（原文）**：`weighted_loss` 装饰原函数 → 类内 `forward` 调用 `my_loss(pred, target, weight, reduction, avg_factor)` → 乘以 `self.loss_weight`。原文给出示例损失实现：`loss = torch.abs(pred - target)`（即 L1 范式）。

> 注：原文未提供基准性能（如 mIoU/ACC/速度）数据，未提供论文中的精度对比。

---

## 【表格解读】

**原文无表格**。原文所有配置均以 Python 字典（`dict(...)`）形式给出，未使用 markdown 表格组织参数。

---

## 【公式解读】

**原文无公式**。原文虽使用 `@weighted_loss` 装饰器隐含了逐元素加权机制，并给出了 L1 形式损失 `loss = torch.abs(pred - target)` 的代码片段，但并未以 LaTeX 或伪代码形式给出任何数学公式。

---

## 【关联】

虽然用户提供的元数据标注"内部链接: (无)"，但原文正文中显式嵌入了以下外部/库内交叉引用，构成上下游依赖关系：

- **BaseDecodeHead**：原文链接 `https://github.com/open-mmlab/mmsegmentation/blob/master/mmseg/models/decode_heads/decode_head.py`，是所有 decode head 的基类，新增 head 必须派生自它。
- **PSPNet 论文**：原文链接 `https://arxiv.org/abs/1612.01105`，作为示例 head 的理论来源。
- **PyTorch Optim API 文档**：原文链接 `https://pytorch.org/docs/stable/optim.html?highlight=optim#module-torch.optim`，用户可直接对照 PyTorch 原生优化器参数。
- **上游注册表（registry 体系）**：`mmcv.runner.OPTIMIZERS` / `OPTIMIZER_BUILDERS` 提供 optimizer 与 builder 注册；`mmseg.models.registry`（`BACKBONES`, `HEADS`）与 `mmseg.models.builder.LOSSES` 提供模块注册。
- **教程体系内**："Tutorial 4" 表明本文是 MMSegmentation 自定义系列教程的第 4 篇，与训练流程配置、config 字段（`optimizer`、`model.backbone`、`model.decode_head`、`loss_decode`）耦合紧密，是整个 config 体系的"扩展点说明"。

---

## 【使用方法】

以下汇总原文给出的全部启用/配置片段，按功能分组：

### 1. 自定义 Optimizer（注册 + 使用）

文件位置：`mmseg/core/optimizer/my_optimizer.py`
```python
from mmcv.runner import OPTIMIZERS
from torch.optim import Optimizer

@OPTIMIZERS.register_module
class MyOptimizer(Optimizer):
    def __init__(self, a, b, c):
        ...
```
在 `mmseg/core/optimizer/__init__.py` 中加入：
```python
from .my_optimizer import MyOptimizer
```
Config 中切换：
```python
optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
```

### 2. 切换至 PyTorch 内置 Optimizer
```python
optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)
# 或
optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
```

### 3. 自定义 Optimizer Constructor（参数级）
```python
from mmcv.runner import OPTIMIZER_BUILDERS
from .cocktail_optimizer import CocktailOptimizer

@OPTIMIZER_BUILDERS.register_module
class CocktailOptimizerConstructor(object):
    def __init__(self, optimizer_cfg, paramwise_cfg=None):
        ...
    def __call__(self, model):
        return my_optimizer
```

### 4. 新增 Backbone（以 MobileNet 为例）
- 文件：`mmseg/models/backbones/mobilenet.py`，装饰 `@BACKBONES.register_module`，类需含 `forward`（返回 tuple）与 `init_weights(pretrained=None)`。
- 在 `mmseg/models/backbones/__init__.py` 中 `from .mobilenet import MobileNet`。
- Config 使用：
```python
model = dict(
    ...,
    backbone=dict(type='MobileNet', arg1=xxx, arg2=xxx),
    ...)
```

### 5. 新增 Decode Head（以 PSPHead 为例）
- 文件：`mmseg/models/decode_heads/psp_head.py`，继承 `BaseDecodeHead`，装饰 `@HEADS.register_module()`，需 `init_weights()` 与 `forward(inputs)`。
- 在 `mmseg/models/decode_heads/__init__.py` 中导出。
- Config 示例（PSPNet 完整配置）：
```python
norm_cfg = dict(type='SyncBN', requires_grad=True)
model = dict(
    type='EncoderDecoder',
    pretrained='pretrain_model/resnet50_v1c_trick-2cccc1ad.pth',
    backbone=dict(
        type='ResNetV1c', depth=50, num_stages=4,
        out_indices=(0, 1, 2, 3),
        dilations=(1, 1, 2, 4), strides=(1, 2, 1, 1),
        norm_cfg=norm_cfg, norm_eval=False,
        style='pytorch', contract_dilation=True),
    decode_head=dict(
        type='PSPHead',
        in_channels=2048, in_index=3, channels=512,
        pool_scales=(1, 2, 3, 6),
        dropout_ratio=0.1, num_classes=19,
        norm_cfg=norm_cfg, align_corners=False,
        loss_decode=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0)))
```

### 6. 新增 Loss
- 文件：`mmseg/models/losses/my_loss.py`，含 `my_loss` 函数（`@weighted_loss` 装饰）与 `MyLoss` 类（`@LOSSES.register_module`）。
- 类签名：`__init__(self, reduction='mean', loss_weight=1.0)`；`forward` 接受 `pred, target, weight=None, avg_factor=None, reduction_override=None`，并校验 `reduction_override in (None, 'none', 'mean', 'sum')`。
- 在 `mmseg/models/losses/__init__.py` 中：`from .my_loss import MyLoss, my_loss`。
- Config 中替换 head 内的 `loss_decode`：
```python
loss_decode = dict(type='MyLoss', loss_weight=1.0)
```

---

> **总结**：本教程是一份"扩展点手册"，其核心思想是把 MMSegmentation 的四大可定制点（Optimizer / Optimizer Constructor / Backbone / Head / Loss）全部纳入统一的**注册表 + 配置驱动**体系：用户只需按模板实现类、用装饰器注册、在 `__init__.py` 暴露、在 config 写 `type='YourName'`，即可无需改动框架主流程完成接入。
