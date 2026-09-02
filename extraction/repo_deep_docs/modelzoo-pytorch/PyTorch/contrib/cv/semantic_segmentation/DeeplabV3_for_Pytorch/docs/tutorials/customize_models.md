# Tutorial 4: Customize Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs/tutorials/customize_models.md

# 深度解读: Tutorial 4: Customize Models

## 【定位】

这篇文档解决"MMSegmentation 框架如何让用户在不修改框架主体的前提下, 通过注册表机制自定义优化器、优化器构造器、新骨干网络 (backbone)、新解码头 (decode head)、新损失函数等模型组件"的问题, 描述的是 mmseg 模型扩展能力。

---

## 【技术要点】

1. **注册表机制贯穿全篇**: 五个可定制组件均使用装饰器 (decorator) 注册 —— `@OPTIMIZERS.register_module` / `@OPTIMIZER_BUILDERS.register_module` / `@BACKBONES.register_module` / `@HEADS.register_module` / `@LOSSES.register_module`, 注册后必须在对应 `__init__.py` 中 `import`, 注册表才能加载到新模块。

2. **自定义优化器只需 2 步**: 在 `mmseg/core/optimizer/my_optimizer.py` 实现 `MyOptimizer`, 类必须继承 `torch.optim.Optimizer`; 再在 `__init__.py` 中 `from .my_optimizer import MyOptimizer` 即可在 config 里通过 `optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)` 调用。

3. **优化器配置保持 PyTorch 兼容**: 默认 SGD 示例 `optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)`; 改用 Adam 仅需 `optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)`, 参数直接对齐 [PyTorch optim API](https://pytorch.org/docs/stable/optim.html?highlight=optim#module-torch.optim)。

4. **优化器构造器用于参数细粒度调度**: 通过 `@OPTIMIZER_BUILDERS.register_module` 注册的 `CocktailOptimizerConstructor` 类需实现 `__init__(self, optimizer_cfg, paramwise_cfg=None)` 与 `__call__(self, model)`, 用途是对模型不同层 (例如 BatchNorm) 做差异化 weight_decay。

5. **新 backbone 必须遵守 3 接口约束**: 必须继承 `nn.Module`、实现 `forward(self, x) → tuple` (返回多尺度特征 tuple)、实现 `init_weights(self, pretrained=None)`。backbone 在 config 中对应 `model.backbone` 字段。

6. **新 head 必须继承 `BaseDecodeHead`**: 派生类需要实现 `__init__`、`init_weights`、`forward(self, inputs)` 三个方法; PSPHead 的标准 config 字段包括 `in_channels=2048`、`in_index=3`、`channels=512`、`pool_scales=(1, 2, 3, 6)`、`dropout_ratio=0.1`、`num_classes=19`、`align_corners=False`、`loss_decode` (内部含 `CrossEntropyLoss`, `use_sigmoid=False`, `loss_weight=1.0`)。

7. **新损失通过 `weighted_loss` 装饰器实现逐元素加权**: 函数 `my_loss(pred, target)` 必须断言 `pred.size() == target.size() and target.numel() > 0`; 类 `MyLoss(nn.Module)` 在 `forward` 中校验 `reduction_override in (None, 'none', 'mean', 'sum')`, 默认 `reduction='mean'`, `loss_weight=1.0`, 内部用 `self.loss_weight * my_loss(pred, target, weight, reduction=reduction, avg_factor=avg_factor)` 输出。

---

## 【关键机制与数据】

### 工作流: 注册 → import → 配置引用

每个自定义组件的工作流都是相同的"三段式":

| 阶段 | 操作 |
|---|---|
| ① 实现 | 在约定路径的 `.py` 文件中用对应 `@xxx.register_module` 装饰器包装类 |
| ② 暴露 | 在同目录的 `__init__.py` 中 `from .xxx import Xxx` |
| ③ 引用 | 在 config 文件对应字段写 `type='Xxx'` |

原文未给出该流程的性能数据; 所有"数据"都是配置超参 (下条)。

### 关键配置超参 (原文逐字)

- **SGD 默认**: `lr=0.02, momentum=0.9, weight_decay=0.0001`
- **Adam 示例**: `lr=0.0003, weight_decay=0.0001` (原文注: "the performance will drop a lot")
- **PSPHead 配置**: `in_channels=2048, in_index=3, channels=512, pool_scales=(1, 2, 3, 6), dropout_ratio=0.1, num_classes=19, align_corners=False`
- **PSPHead 依赖的 backbone (ResNetV1c, depth=50)**:
  - `num_stages=4`
  - `out_indices=(0, 1, 2, 3)`
  - `dilations=(1, 1, 2, 4)`
  - `strides=(1, 2, 1, 1)`
  - `norm_cfg=dict(type='SyncBN', requires_grad=True)`
  - `norm_eval=False`
  - `style='pytorch'`
  - `contract_dilation=True`
  - `pretrained='pretrain_model/resnet50_v1c_trick-2cccc1ad.pth'`
- **PSPHead 损失**: `type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0`
- **MyLoss 默认**: `reduction='mean', loss_weight=1.0`

### 组件分类 (原文逐字)

> "There are mainly 2 types of components in MMSegmentation."
> - **backbone**: "usually stacks of convolutional network to extract feature maps, e.g., ResNet, HRNet."
> - **head**: "the component for semantic segmentation map decoding."

---

## 【表格解读】

**原文无表格。** 文档以代码块与正文叙述形式组织, 未出现任何 markdown 表格。

---

## 【公式解读】

**原文无公式。** 文档未出现任何数学公式或 LaTeX 表达式; 唯一的"算式"是损失函数代码行:

```python
loss = torch.abs(pred - target)
return loss
```

以及加权封装行:

```python
loss = self.loss_weight * my_loss(
    pred, target, weight, reduction=reduction, avg_factor=avg_factor)
return loss
```

这两段不是数学公式, 而是 Python 表达式, 不在此节展开。

---

## 【关联】

文档基于 MMSegmentation 框架的模块化设计, 与以下模块/类/上游关系强耦合:

- **`mmcv.runner`** — 提供基础注册表 `OPTIMIZERS` 与 `OPTIMIZER_BUILDERS`, 优化器与构造器必须从这里导入并装饰; `mmcv.utils.build_from_cfg` 同样来自 mmcv。
- **`mmseg.core.optimizer`** — 子包, 自定义优化器存放位置 (`my_optimizer.py`)。
- **`mmseg.models.backbones`** — 子包, 新 backbone 存放位置; 现有参考实现含 ResNet、HRNet (见 backbone 分类说明); PSPHead 配置示例引用了 `ResNetV1c` (depth=50, num_stages=4)。
- **`mmseg.models.decode_heads`** — 子包, 新 head 存放位置; 所有 head 必须继承 **`BaseDecodeHead`** (位于 `mmseg/models/decode_heads/decode_head.py`)。
- **`mmseg.models.losses`** — 子包, 新损失存放位置; 依赖同一目录下的 `utils.weighted_loss` 装饰器与 `LOSSES` 注册表 (从 `..builder` 导入)。
- **`mmseg.registry`** — 提供 `BACKBONES` 等注册表对象 (新 backbone 例子中 `from ..registry import BACKBONES`)。
- **`mmseg.builder`** — 提供 `LOSSES` 注册表对象 (新 loss 例子中 `from ..builder import LOSSES`)。
- **上游模型组装 (`EncoderDecoder`)** — PSPHead config 中 `type='EncoderDecoder'`, 表明新组件最终被装配进 EncoderDecoder 容器 (backbone + decode_head + auxiliary_head 三段式)。
- **外部参考** — [PSPNet 论文 (arXiv:1612.01105)](https://arxiv.org/abs/1612.01105); [PyTorch optim API](https://pytorch.org/docs/stable/optim.html?highlight=optim#module-torch.optim); [mmsegmentation 源码 — decode_head.py](https://github.com/open-mmlab/mmsegmentation/blob/master/mmseg/models/decode_heads/decode_head.py)。

---

## 【使用方法】

### 启用自定义优化器

```python
# mmseg/core/optimizer/my_optimizer.py
from mmcv.runner import OPTIMIZERS
from torch.optim import Optimizer

@OPTIMIZERS.register_module
class MyOptimizer(Optimizer):
    def __init__(self, a, b, c):
        ...

# mmseg/core/optimizer/__init__.py
from .my_optimizer import MyOptimizer
```

在 config 中:
```python
optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
```

### 启用自定义优化器构造器

在 `mmseg/core/optimizer/` 下注册一个 `@OPTIMIZER_BUILDERS.register_module` 类, 实现 `__init__(optimizer_cfg, paramwise_cfg=None)` 与 `__call__(model) → my_optimizer`; config 端调用方式原文未给具体字段名。

### 启用新 backbone (MobileNet 示例)

1. 创建 `mmseg/models/backbones/mobilenet.py`, 类装饰 `@BACKBONES.register_module`, 实现 `__init__(arg1, arg2)`、`forward(x) → tuple`、`init_weights(pretrained=None)`。
2. 在 `mmseg/models/backbones/__init__.py` 中 `from .mobilenet import MobileNet`。
3. 在 config 中:
```python
model = dict(
    ...,
    backbone=dict(type='MobileNet', arg1=xxx, arg2=xxx),
    ...)
```

### 启用新 head (PSPHead 示例)

1. 在 `mmseg/models/decode_heads/psp_head.py` 中定义 `class PSPHead(BaseDecodeHead)`, 实现 `__init__(self, pool_scales=(1, 2, 3, 6), **kwargs)`、`init_weights()`、`forward(inputs)`。
2. 在 `mmseg/models/decode_heads/__init__.py` 中 import。
3. config 端在 `model.decode_head` 字段中指定 `type='PSPHead'` 及 `in_channels=2048, in_index=3, channels=512, pool_scales=(1, 2, 3, 6), dropout_ratio=0.1, num_classes=19, norm_cfg, align_corners=False, loss_decode=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0)`。

### 启用新损失 (MyLoss 示例)

1. 在 `mmseg/models/losses/my_loss.py` 中: 用 `@weighted_loss` 装饰函数 `my_loss(pred, target)`, 用 `@LOSSES.register_module` 装饰类 `MyLoss(nn.Module)` (含 `reduction='mean', loss_weight=1.0`)。
2. 在 `mmseg/models/losses/__init__.py` 中:
```python
from .my_loss import MyLoss, my_loss
```
3. config 端在 head 的 `loss_decode` 字段中引用:
```python
loss_decode=dict(type='MyLoss', loss_weight=1.0)
```

> 原文未涉及以下内容: 启用自定义构造器后 config 端的具体字段名与配置语法、自定义组件的单元测试方法、热加载/动态注册流程。
