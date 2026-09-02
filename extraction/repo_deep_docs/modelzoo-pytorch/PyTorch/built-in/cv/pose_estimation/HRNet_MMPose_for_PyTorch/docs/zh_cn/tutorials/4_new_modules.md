# 教程 4: 增加新的模块

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/zh_cn/tutorials/4_new_modules.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/zh_cn/tutorials/4_new_modules.md

# 一体化深度解读：教程 4 - 增加新的模块

## 【定位】

这篇文档是 MMPose 项目的扩展开发指南，描述如何通过注册机制（register mechanism）向 MMPose 框架添加自定义优化器、优化器构造器、主干网络（backbone）、关键点头（keypoint_head）和损失函数，从而扩展框架在姿势估计任务中的可定制能力。

---

## 【技术要点】

1. **自定义优化器**：通过 `@OPTIMIZERS.register_module()` 装饰器将优化器类注册到 `OPTIMIZERS` 注册器（位于 `mmcv.runner`），并在 `mmpose/core/optimizer/__init__.py` 中导入该类；之后通过修改配置文件的 `optimizer` 字段即可启用，例如 `optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)`。

2. **PyTorch 内置优化器的便捷切换**：MMPose 已支持 PyTorch 实现的所有优化器，只需修改 `optimizer` 字段的 `type` 与对应参数。原文给出两个具体示例：
   - SGD：`optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)`
   - Adam：`optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)`（原文注释"虽然这会造成网络效果下降"）

3. **自定义优化器构造器**：通过 `@OPTIMIZER_BUILDERS.register_module()` 装饰器注册到 `OPTIMIZER_BUILDERS`（位于 `mmcv.runner`），用于对模型不同层（如 BatchNorm 层）进行细粒度参数调整（例如特定层的权值衰减）。需实现 `__init__(self, optimizer_cfg, paramwise_cfg=None)` 与 `__call__(self, model)` 两个方法。

4. **新增模型的三大基础组件**：检测器（detector）、主干网络（backbone）、关键点头（keypoint_head）；扩展流程一致——**新建文件 → 在对应 `__init__.py` 中导入 → 在配置文件中以 `model` 字段挂载**。

5. **新增主干网络的代码骨架**：路径 `mmpose/models/backbones/my_model.py`，需继承 `nn.Module`，重写 `forward(self, x)`（应返回一个 tuple）和 `init_weights(self, pretrained=None)`，并使用 `@BACKBONES.register_module()` 装饰器。

6. **新增关键点头 + 损失函数的代码骨架**：路径分别为 `mmpose/models/keypoint_heads/my_head.py` 与 `mmpose/models/losses/my_loss.py`，分别使用 `@HEADS.register_module()` 和 `@LOSSES.register_module()` 装饰器。损失函数示例 `MyLoss` 通过 `use_target_weight=False` 控制是否按元素加权，最终通过 `loss_keypoint=dict(type='MyLoss', use_target_weight=False)` 接入模型。

---

## 【关键机制与数据】

### 注册器机制（贯穿全文的核心）

MMPose 依赖 mmcv 提供的注册器（Registry）实现"配置驱动"的模块装配。原文未列出注册器源码，但通过多处装饰器调用清晰展示了这一机制：
- 优化器：`@OPTIMIZERS.register_module()`（来自 `mmcv.runner`）
- 优化器构造器：`@OPTIMIZER_BUILDERS.register_module()`（来自 `mmcv.runner`）
- 主干网络：`@BACKBONES.register_module()`（来自 `mmpose.models.builder`）
- 关键点头：`@HEADS.register_module()`（来自 `mmpose.models.builder`）
- 损失函数：`@LOSSES.register_module()`（来自 `mmpose.models`）

每次新模块新增后，必须在对应目录的 `__init__.py` 中显式 import 才能让注册器找到它——这是"导入即注册"的隐式契约。

### 配置文件驱动的组件装配

文档展示了一种自上而下的配置范式：
- 优化器由 `optimizer` 字段定义并切换
- 模型由 `model` 字段定义；自顶向下的 2D 姿态估计模型将 `type` 设为 `'TopDown'`，其下嵌套 `backbone` 与 `keypoint_head` 两个子字段
- 损失由 `loss_keypoint` 字段定义

### 数据流（以 `MyLoss` 损失函数为例，原文逐字给出）

```text
forward(self, output, target, target_weight):
    batch_size  = output.size(0)
    num_joints  = output.size(1)
    heatmaps_pred = output.reshape((batch_size, num_joints, -1)).split(1, 1)
    heatmaps_gt   = target.reshape((batch_size, num_joints, -1)).split(1, 1)
    loss = 0.
    for idx in range(num_joints):
        heatmap_pred = heatmaps_pred[idx].squeeze(1)
        heatmap_gt   = heatmaps_gt[idx].squeeze(1)
        if self.use_target_weight:
            loss += criterion(heatmap_pred * target_weight[:, idx],
                              heatmap_gt   * target_weight[:, idx])
        else:
            loss += criterion(heatmap_pred, heatmap_gt)
    return loss / num_joints
```
原文无任何性能指标或基准数据。

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。** （损失函数的计算逻辑以 Python 代码块形式给出，未以数学公式或 LaTeX 表示。）

---

## 【关联】

原文未提供文末内部链接（"内部链接: (无)"），但根据文中描述可梳理如下上下游关系：

- **上游依赖**：所有扩展均依赖 mmcv 的注册器系统（`mmcv.runner` 中的 `OPTIMIZERS`、`OPTIMIZER_BUILDERS`）以及 mmpose 自有的构建器（`mmpose.models.builder` 中的 `BACKBONES`、`HEADS`，`mmpose.models` 中的 `LOSSES`）。
- **平行扩展点**：自定义优化器、自定义优化器构造器、自定义 backbone、自定义 keypoint head、自定义 loss 五者构成 MMPose 的"扩展点矩阵"，彼此独立但均通过同一注册范式接入。
- **下游消费方**：所有新组件最终都被 `model` / `optimizer` / `loss_keypoint` 配置文件字段装配，由训练管线调用。
- **文档内部关联**（原文上下文推断）：本教程是 MMPose 教程系列的第 4 篇，前置教程应涉及基础配置与已有模块使用；后置教程可能涉及数据集、评估指标等扩展（原文未显式提及）。
- **外部参考**：优化器参数设置指向 PyTorch 官方 API 文档 `https://pytorch.org/docs/stable/optim.html?highlight=optim#module-torch.optim`。

---

## 【使用方法】

> 以下命令/配置均**逐字**取自原文。

### 1. 添加自定义优化器

**(a)** 在 `mmpose/core/optimizer/my_optimizer.py` 中实现并注册：

```python
from mmcv.runner import OPTIMIZERS
from torch.optim import Optimizer

@OPTIMIZERS.register_module()
class MyOptimizer(Optimizer):
    def __init__(self, a, b, c):
        ...
```

**(b)** 在 `mmpose/core/optimizer/__init__.py` 中导入：

```python
from .my_optimizer import MyOptimizer
```

**(c)** 在配置文件中切换：

```python
optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
```

或切换为内置 PyTorch 优化器：

```python
optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)
optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
```

### 2. 添加自定义优化器构造器

路径：自定义文件，注册到 `OPTIMIZER_BUILDERS`，需实现 `__init__(self, optimizer_cfg, paramwise_cfg=None)` 与 `__call__(self, model)`。原文未给出 `optimizer_cfg` 中具体可配字段（仅在示例中显示 `paramwise_cfg=None`）。

### 3. 添加自定义主干网络

**(a)** 新建 `mmpose/models/backbones/my_model.py`，注册到 `BACKBONES`，需重写 `forward(self, x)` 与 `init_weights(self, pretrained=None)`。
**(b)** 在 `mmpose/models/backbones/__init__.py` 中 `from .my_model import MyModel`。
**(c)** 在配置文件中挂载（自顶向下 2D 姿态估计模型）：

```python
model = dict(
    type='TopDown',
    backbone=dict(type='MyModel', arg1=xxx, arg2=xxx),
    keypoint_head=dict(type='MyHead', arg1=xxx, arg2=xxx))
```

### 4. 添加自定义关键点头

**(a)** 新建 `mmpose/models/keypoint_heads/my_head.py`，继承 `nn.Module`，注册到 `HEADS`，重写 `forward(self, x)` 与 `init_weights(self)`。
**(b)** 在 `mmpose/models/keypoint_heads/__init__.py` 中 `from .my_head import MyHead`。

### 5. 添加自定义损失函数

**(a)** 新建 `mmpose/models/losses/my_loss.py`，注册到 `LOSSES`：

```python
import torch
import torch.nn as nn
from mmpose.models import LOSSES

def my_loss(pred, target):
    assert pred.size() == target.size() and target.numel() > 0
    loss = torch.abs(pred - target)
    loss = torch.mean(loss)
    return loss

@LOSSES.register_module()
class MyLoss(nn.Module):
    def __init__(self, use_target_weight=False):
        super(MyLoss, self).__init__()
        self.criterion = my_loss()
        self.use_target_weight = use_target_weight

    def forward(self, output, target, target_weight):
        ...（见上文"数据流"小节）...
```

**(b)** 在 `mmpose/models/losses/__init__.py` 中：

```python
from .my_loss import MyLoss, my_loss
```

**(c)** 在配置文件的模型字段中通过 `loss_keypoint` 启用：

```python
loss_keypoint = dict(type='MyLoss', use_target_weight=False)
```

> 备注：原文在"添加新的损失函数"小节开头提到 `装饰器 weighted_loss 使损失函数能够为每个元素加权`，但所附 `MyLoss` 代码示例并未实际使用该装饰器，仅以注释形式说明其作用——这是一处文档与代码不一致之处，**严格按原文如实保留**。
