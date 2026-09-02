# 教程 7：如何自定义模型运行参数

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/video/R(2+1)D/docs_zh_CN/tutorials/7_customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/video/R(2+1)D/docs_zh_CN/tutorials/7_customize_runtime.md

# 一体化深度解读：MMAction2 自定义模型运行参数教程

## 【定位】

本教程系统讲解如何在 MMAction2 视频动作识别框架中自定义训练的"运行时参数"，覆盖**优化器构造、学习率调度、工作流编排、训练钩子（Hook）**四大扩展维度，使用户能够在不修改训练主循环的前提下精细化控制训练行为。

---

## 【技术要点】

1. **优化器（Optimizer）三层扩展机制**
   - 第一层：直接通过配置 `optimizer` 字段调用 PyTorch 内置优化器（如 SGD、Adam），可指定 `lr`、`momentum`、`betas`、`eps`、`weight_decay`、`amsgrad` 等参数。
   - 第二层：通过 `OPTIMIZERS.register_module()` 装饰器注册自定义优化器类，需在 `mmaction/core/optimizer/__init__.py` 导入或使用 `custom_imports`。
   - 第三层：通过 `OPTIMIZER_BUILDERS.register_module()` 注册自定义优化器构造器 `MyOptimizerConstructor`，实现参数粒度（如 BatchNorm 层的 weight_decay）的细粒度配置。

2. **梯度裁剪与动量调度的"训练稳定与加速"附加设置**
   - `optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))` 用于梯度裁剪。
   - `CyclicLrUpdater` 与 `CyclicMomentumUpdater` 联动使用（`step_ratio_up=0.4`、`cyclic_times=1`），使动量随学习率周期变化。

3. **学习率调度策略的可配置项**
   - 默认使用 MMCV 的 `StepLRHook`；亦支持 `Poly`（`power=0.9, min_lr=1e-4, by_epoch=False`）与 `CosineAnnealing`（含 `warmup='linear'`、`warmup_iters=1000`、`warmup_ratio=1.0/10`、`min_lr_ratio=1e-5`）。

4. **工作流（Workflow）控制训练—验证编排**
   - 默认为 `[('train', 1)]`，可改为 `[('train', 1), ('val', 1)]`；`total_epochs` 仅控制训练 epoch 数；`EvalHook` 由 `after_train_epoch` 触发，验证工作流只触发 `after_val_epoch` 钩子。

5. **钩子（Hook）系统的三段式扩展流程**
   - 创建（继承 `Hook` 基类并用 `@HOOKS.register_module()` 装饰器注册）、注册（通过 `__init__.py` 导入或 `custom_imports`）、配置（写入 `custom_hooks` 列表）。
   - 钩子拥有 `before_run / after_run / before_epoch / after_epoch / before_iter / after_iter` 六个生命周期回调点。
   - `priority` 取值为 `'NORMAL'`（默认）或 `'HIGHEST'`。

6. **默认钩子修改点**
   - 六个默认钩子：`log_config`（VERY_LOW 优先级）、`checkpoint_config`、`evaluation`、`lr_config`、`optimizer_config`、`momentum_config`（后五个为 NORMAL）。
   - `checkpoint_config = dict(interval=1)` 控制权重保存间隔，可设置 `max_keep_ckpts`、`save_optimizer`。
   - `log_config` 支持 `TextLoggerHook`、`TensorboardLoggerHook`、`WandbLoggerHook`、`MlflowLoggerHook`。
   - `evaluation = dict(interval=1, metrics='bbox')` 初始化 `EvalHook`。

---

## 【关键机制与数据】

### 优化器注册与实例化机制
原文描述了完整的注册器-装饰器机制：`@OPTIMIZERS.register_module()` 将自定义优化器注入全局注册表。注册时通过两条路径——**修改 `mmaction/core/optimizer/__init__.py`** 或在配置中通过 `custom_imports = dict(imports=['mmaction.core.optimizer.my_optimizer'], allow_failed_imports=False)` 显式导入——使 `MyOptimizer` 类能被 `runner` 识别。原文特别提示：`mmaction.core.optimizer.my_optimizer.MyOptimizer` **不会**被直接导入，只有包级别的 `mmaction.core.optimizer.my_optimizer` 会被加载。

### 学习率与动量联动调度数据流
原文给出用于 3D 检测的 cyclic 调度配置：
- `target_ratio=(10, 1e-4)` 表示学习率在 10 倍与 1e-4 之间循环；
- `target_ratio=(0.85 / 0.95, 1)` 表示动量在约 0.8947 与 1 之间循环；
- `cyclic_times=1`、`step_ratio_up=0.4` 控制上升段占总周期的 40%。
该机制通过 `CyclicLrUpdater` 与 `CyclicMomentumUpdater` 联动实现，使学习率下降时动量上升，反之亦然。

### 工作流对钩子触发的影响
原文明确指出两条工作流 `[('train', 1), ('val', 1)]` 与 `[('train', 1)]` **不会**改变 `EvalHook` 的行为，因为 `EvalHook` 由 `after_train_epoch` 调用，验证工作流只影响 `after_val_epoch` 触发的钩子。两者唯一区别：前者会在每轮训练后额外计算验证集上的 loss。

### 默认钩子优先级矩阵（原文描述）
| 钩子 | 优先级 |
|------|--------|
| log_config | VERY_LOW |
| checkpoint_config | NORMAL |
| evaluation | NORMAL |
| lr_config | NORMAL |
| optimizer_config | NORMAL |
| momentum_config | NORMAL |

---

## 【表格解读】

**原文无表格。** 文档以代码片段和文字说明为主，未提供结构化表格。所有配置信息以 Python `dict` 字面量形式给出（如 `optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))`）。

---

## 【公式解读】

**原文无公式。** 文档未涉及数学公式或 LaTeX 表达式。学习率/动量的调度仅以配置参数（`target_ratio`、`cyclic_times`、`step_ratio_up` 等）描述，未给出解析式。

---

## 【关联】

根据原文及文末提及的外部链接，本教程与以下模块/特性形成上下游依赖：

### 上游基础模块（MMCV Runner）
- **`mmcv.runner.OPTIMIZERS`**：优化器注册器，自定义优化器须用 `@OPTIMIZERS.register_module()` 装饰。
- **`mmcv.runner.optimizer.OPTIMIZER_BUILDERS`**：优化器构造器注册器，用于实现 `MyOptimizerConstructor.__call__(model)` 接口。
- **`mmcv.runner.HOOKS`**：钩子注册器，提供 `Hook` 基类及其六个生命周期方法。
- **`mmcv.runner.hooks.lr_updater.StepLRHook` / `CyclicLrUpdater`**：默认与循环学习率调度的实现位置（链接至 `mmcv/runner/hooks/lr_updater.py`）。
- **`mmcv/runner/hooks/momentum_updater.py`**：`CyclicMomentumUpdater` 的源码位置。
- **`mmcv/runner/hooks/checkpoint.py`**：`CheckpointHook` 的实现位置。
- **`mmcv.runner.LoggerHook`**：`TextLoggerHook`、`TensorboardLoggerHook`、`WandbLoggerHook`、`MlflowLoggerHook` 的基类与文档入口。
- **`mmcv.runner.CheckpointHook`**：权重保存钩子，`interval`、`max_keep_ckpts`、`save_optimizer` 等参数的定义源。

### 框架内部模块（MMAction2）
- **`mmaction/core/optimizer/`**：自定义优化器的推荐存放路径（如 `my_optimizer.py`）。
- **`mmaction/core/utils/`**：自定义钩子的推荐存放路径（如 `my_hook.py`）。
- **`mmaction/core/evaluation/eval_hooks.py`**：`EvalHook` 在 MMAction2 内部的实现位置（`evaluation = dict(interval=1, metrics='bbox')` 初始化此钩子）。
- **`mmaction/core/evaluation/eval_hooks.py#L12`**：`EvalHook` 的具体代码行（由原文链接标注）。

### 上下游教程关联
- **教程 1–6（隐含）**：本教程属于第 7 篇，前序教程应覆盖数据集、模型、配置文件等基础；本教程聚焦运行时的"训练循环"层。
- **PyTorch API（外部）**：用户自定义优化器时需参考 `https://pytorch.org/docs/stable/optim.html`，确保继承 `torch.optim.Optimizer`。

---

## 【使用方法】

原文未涉及 CLI 启动命令，所有"启用方式"均通过**修改配置文件**实现。汇总关键启用范式如下：

### 1. 使用 PyTorch 内置优化器
```python
optimizer = dict(type='Adam', lr=0.001, betas=(0.9, 0.999), eps=1e-08, weight_decay=0, amsgrad=False)
```

### 2. 注册自定义优化器
- 在 `mmaction/core/optimizer/my_optimizer.py` 中定义：
  ```python
  from mmcv.runner import OPTIMIZERS
  from torch.optim import Optimizer

  @OPTIMIZERS.register_module()
  class MyOptimizer(Optimizer):
      def __init__(self, a, b, c):
          pass
  ```
- 在 `mmaction/core/optimizer/__init__.py` 写入 `from .my_optimizer import MyOptimizer`，或在配置中使用 `custom_imports = dict(imports=['mmaction.core.optimizer.my_optimizer'], allow_failed_imports=False)`。
- 在配置中启用：
  ```python
  optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
  ```

### 3. 注册自定义优化器构造器
- 用 `@OPTIMIZER_BUILDERS.register_module()` 装饰 `MyOptimizerConstructor`，实现 `__init__(self, optimizer_cfg, paramwise_cfg=None)` 与 `__call__(self, model)`。
- 默认构造器模板链接：`mmcv/runner/optimizer/default_constructor.py#L11`。

### 4. 梯度裁剪 / 动量调度
```python
optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))
lr_config = dict(policy='cyclic', target_ratio=(10, 1e-4), cyclic_times=1, step_ratio_up=0.4)
momentum_config = dict(policy='cyclic', target_ratio=(0.85/0.95, 1), cyclic_times=1, step_ratio_up=0.4)
```

### 5. 学习率调度
```python
# Poly
lr_config = dict(policy='poly', power=0.9, min_lr=1e-4, by_epoch=False)

# CosineAnnealing
lr_config = dict(policy='CosineAnnealing', warmup='linear', warmup_iters=1000,
                 warmup_ratio=1.0/10, min_lr_ratio=1e-5)
```

### 6. 工作流
```python
workflow = [('train', 1)]                 # 默认
workflow = [('train', 1), ('val', 1)]     # 每轮训练后做验证
```

### 7. 自定义钩子
- 继承 `Hook` 实现六个生命周期方法，用 `@HOOKS.register_module()` 装饰。
- 通过 `__init__.py` 导入或 `custom_imports` 暴露。
- 配置启用：
  ```python
  custom_hooks = [dict(type='MyHook', a=a_value, b=b_value, priority='NORMAL')]
  ```
- `priority` 可选 `'NORMAL'`（默认）或 `'HIGHEST'`。

### 8. 使用 MMCV 内置钩子
```python
mmcv_hooks = [dict(type='MMCVHook', a=a_value, b=b_value, priority='NORMAL')]
```

### 9. 修改默认钩子
```python
checkpoint_config = dict(interval=1)                       # 可加 max_keep_ckpts、save_optimizer
log_config = dict(
    interval=50,
    hooks=[dict(type='TextLoggerHook'), dict(type='TensorboardLoggerHook')]
)
evaluation = dict(interval=1, metrics='bbox')
```
