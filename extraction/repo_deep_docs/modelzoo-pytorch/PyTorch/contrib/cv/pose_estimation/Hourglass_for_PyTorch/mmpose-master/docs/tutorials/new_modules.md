# Tutorial 4: Adding New Modules

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/pose_estimation/Hourglass_for_PyTorch/mmpose-master/docs/tutorials/new_modules.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/pose_estimation/Hourglass_for_PyTorch/mmpose-master/docs/tutorials/new_modules.md

# 深度解读：Tutorial 4: Adding New Modules

## 【定位】

本文档是 mmpose 项目中面向开发者的扩展教程（Tutorial 4），系统说明如何在 mmpose 框架内自定义并注册**优化器、优化器构造器、模型组件（backbone / keypoint_head / detector）以及损失函数**这四类核心模块，以通过 registry 机制接入到训练流程中。

---

## 【技术要点】

1. **优化器注册机制**：通过 `mmcv.runner.OPTIMIZERS` 注册装饰器 `@OPTIMIZERS.register_module()` 把新优化器挂入注册表，并在 `mmpose/core/optimizer/__init__.py` 中 `from .my_optimizer import MyOptimizer` 暴露它，使配置文件中 `optimizer=dict(type='MyOptimizer', a=..., b=..., c=...)` 即可生效。

2. **优化器构造器（parameter-wise 配置）**：使用 `@OPTIMIZER_BUILDERS.register_module()` 装饰器，构造器类需实现 `__init__(self, optimizer_cfg, paramwise_cfg=None)` 与 `__call__(self, model)`，用于对不同参数（如 BatchNorm）施加差异化的超参（如 weight decay），从 `mmcv.utils import build_from_cfg`、`mmcv.runner import OPTIMIZER_BUILDERS, OPTIMIZERS` 取相应工具。

3. **模型组件三层结构**：原文明确定义三类组件 —— `detectors`（整体姿态检测 pipeline，通常由 backbone + keypoint_head 构成）、`backbone`（特征提取 FCN 网络，如 ResNet、HRNet）、`keypoint_head`（姿态估计专用头，常含 deconv 层）。Top-Down 2D 姿态估计模型中 `model.type='TopDown'`，其下挂 `backbone` 与 `keypoint_head` 两个子字段。

4. **模型组件注册流程**：backbone 与 keypoint_head 各自需在对应目录下（如 `mmpose/models/backbones/my_model.py`、`mmpose/models/keypoint_heads/my_head.py`）继承 `nn.Module`，使用 `@BACKBONES.register_module()` / `@HEADS.register_module()` 注册，分别覆写 `__init__`、`forward(x)`（**必须返回 tuple**）、`init_weights(pretrained=None)` 三个方法，并在各 `__init__.py` 中 `from .xxx import Xxx` 暴露。

5. **损失函数注册与设计**：损失放在 `mmpose/models/losses/my_loss.py`，使用 `@LOSSES.register_module()` 装饰，类继承 `nn.Module`。`MyLoss` 类暴露 `use_target_weight=False` 选项；其 `forward(output, target, target_weight)` 内部通过 `output.reshape((batch_size, num_joints, -1)).split(1, 1)` 拆出每个关节的热力图，按关节循环累加，最终 `return loss / num_joints` 取均值；并在 `__init__.py` 中 `from .my_loss import MyLoss, my_loss` 暴露。

6. **PyTorch 原生优化器的即插即用**：原文显式说明"已经支持使用 PyTorch 实现的所有优化器"，唯一改动是修改 config 中 `optimizer` 字段，例如切换到 Adam 仅需 `optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)`，并提示参数命名遵循 PyTorch [optim 官方 API 文档](https://pytorch.org/docs/stable/optim.html?highlight=optim#module-torch.optim)。

---

## 【关键机制与数据】

**工作原理（registry-driven plug-in）**：

- **注册表导入链**：自定义模块只有在对应 `__init__.py` 中被显式 import 后，注册表扫描时才能发现它们；这是 mmpose/mmcv "import 即注册" 的核心机制。
- **配置→构造链路**：`optimizer` / `model` / `loss_pose` 等字段以 dict 形式写在 config 中，运行期由 `build_from_cfg` 依据 `type` 键查 registry 取出对应类并实例化。
- **TopDown 模型组装**：以 `type='TopDown'` 为根，逐级嵌套 `backbone` dict 和 `keypoint_head` dict，与 `mmpose/models/registry.py` 中的 `BACKBONES`、`HEADS` 注册表键名严格对应。
- **Loss 的 per-joint 计算流程**：`batch_size × num_joints × H × W` 的输出与 target 经 `reshape(...).split(1, 1)` 切分为 `num_joints` 个 1×N 张量；遍历每个关节按 `use_target_weight` 选择是否 `mul(target_weight[:, idx])` 加权，最后除以 `num_joints` 得到标量损失。
- **优化器构造器的 fine-grained 调参**：通过 `paramwise_cfg` 把模型参数分组（如 BatchNorm 不衰减、卷积层权重衰减更大），构造器类在 `__call__` 中按组生成优化器参数列表。

**性能数据**：原文未涉及任何 benchmark、性能对比或精度数字。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。（注：loss 计算属于循环累加求均值的代码逻辑 `return loss / num_joints`，并非以公式形式给出。）

---

## 【关联】

原文未提供内部链接；根据其内容，可梳理出如下上下层依赖关系：

- **mmcv 依赖**：所有注册机制（`OPTIMIZERS`、`OPTIMIZER_BUILDERS`、`BACKBONES`、`HEADS`、`LOSSES`）以及工具函数 `build_from_cfg` 均来自 `mmcv`（`mmcv.runner` / `mmcv.utils`），表明 mmpose 构建在 mmcv 通用框架之上。
- **上游教程**：作为 "Tutorial 4"，逻辑上承接 Tutorial 1/2/3 关于 config、data pipeline、模型训练的基础内容，并向后衔接更复杂的模型开发。
- **下游配置字段**：
  - `optimizer` 字段 —— 与 config 中的 `lr_config`、`optimizer_config`、`lr_config` 等训练调度字段耦合；
  - `model` 字段（`type='TopDown'`）—— 与 `mmpose/models/detectors/top_down.py` 中的 `TopDown` detector 实现绑定；
  - `loss_pose` 字段 —— 在 model dict 内被 detector 调用，与 `keypoint_head` 计算出的热力图形成数据流闭环。
- **同类教程并列关系**：与 mmpose 中 "Add New Datasets"、"Add New Metrics"、"Add New Transforms" 等扩展教程并列，共同构成模块化扩展体系。
- **PyTorch 官方接口**：`optimizer` 参数命名对齐 `torch.optim` 官方 API（[链接](https://pytorch.org/docs/stable/optim.html?highlight=optim#module-torch.optim)）。

---

## 【使用方法】

**1. 自定义优化器**
- 在 `mmpose/core/optimizer/my_optimizer.py` 中继承 `torch.optim.Optimizer` 并用 `@OPTIMIZERS.register_module()` 装饰；
- 在 `mmpose/core/optimizer/__init__.py` 中添加 `from .my_optimizer import MyOptimizer`；
- 在 config 中使用：
  ```python
  optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
  ```
- 切到 PyTorch 原生优化器（如 Adam）：
  ```python
  optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
  ```

**2. 自定义优化器构造器**
- 在 `mmpose/core/optimizer/` 下新建模块，继承类用 `@OPTIMIZER_BUILDERS.register_module()` 装饰；
- 实现 `__init__(self, optimizer_cfg, paramwise_cfg=None)` 与 `__call__(self, model)`，返回构造好的优化器。

**3. 新增模型组件（以 backbone + keypoint_head 为例）**
- 创建 `mmpose/models/backbones/my_model.py`，继承 `nn.Module`，使用 `@BACKBONES.register_module()`，实现 `__init__`、`forward(x)`（须返回 tuple）、`init_weights(pretrained=None)`；
- 在 `mmpose/models/backbones/__init__.py` 中 `from .my_model import MyModel`；
- 创建 `mmpose/models/keypoint_heads/my_head.py`，使用 `@HEADS.register_module()`，覆写 `forward(self, x)` 与 `init_weights(self)`；
- 在 `mmpose/models/keypoint_heads/__init__.py` 中 `from .my_head import MyHead`；
- config 中按 TopDown 结构挂载：
  ```python
  model = dict(
      type='TopDown',
      backbone=dict(type='MyModel', arg1=xxx, arg2=xxx),
      keypoint_head=dict(type='MyHead', arg1=xxx, arg2=xxx))
  ```

**4. 新增损失函数**
- 在 `mmpose/models/losses/my_loss.py` 中定义函数式 loss 与继承 `nn.Module` 的损失类，使用 `@LOSSES.register_module()`；
- 在 `mmpose/models/losses/__init__.py` 中 `from .my_loss import MyLoss, my_loss`；
- config 中通过 `loss_pose` 字段启用：
  ```python
  loss_pose=dict(type='MyLoss', use_target_weight=False)
  ```
