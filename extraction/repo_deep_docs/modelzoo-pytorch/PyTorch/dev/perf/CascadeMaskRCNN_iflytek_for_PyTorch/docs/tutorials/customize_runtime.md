# Tutorial 5: Customize Runtime Settings

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/customize_runtime.md

# 一体化深度解读：Tutorial 5: Customize Runtime Settings

## 【定位】

本文档是 MMDetection 中关于"如何在训练运行时自定义各种配置"的官方教程，主要解决用户在训练检测模型时对**优化器、学习率调度、训练工作流、训练钩子**四大运行时组件进行定制化改造的需求，使框架在不修改核心代码的情况下即可适配不同的训练策略与实验需求。

---

## 【技术要点】

1. **PyTorch 原生优化器支持**：只需修改 config 中的 `optimizer` 字段类型即可切换任意 PyTorch 优化器（如 `Adam`），并直接通过 `lr`、`weight_decay` 等字段配置参数，无需改动源码。
2. **自定义优化器三步流程**：定义类 → 注册到 `OPTIMIZERS` 注册表（两种方式：`__init__.py` 导入或 `custom_imports` 手动导入）→ 在 config 中以 `type='MyOptimizer'` 引用。
3. **自定义优化器构造器（Optimizer Constructor）**：通过 `OPTIMIZER_BUILDERS.register_module()` 注册类，可实现参数分组级别的精细调整（如 BatchNorm 权重衰减的特殊设置），调用入口为 `__call__(self, model)` 返回构造好的优化器。
4. **梯度裁剪与动量调度**：通过 `optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))` 启用梯度裁剪；通过 `momentum_config` 配合 `lr_config` 实现 Cyclic 策略（`target_ratio=(0.85 / 0.95, 1)`，`cyclic_times=1`，`step_ratio_up=0.4`）。
5. **学习率调度多策略**：默认使用 `StepLRHook`（1x 调度），同时支持 `poly`（`power=0.9, min_lr=1e-4`）和 `CosineAnnealing`（含线性 warmup，`warmup_iters=1000, warmup_ratio=1.0 / 10, min_lr_ratio=1e-5`）。
6. **工作流（Workflow）与自定义钩子**：通过 `workflow = [('train', 1), ('val', 1)]` 控制 train/val 交替执行；自定义钩子继承 `Hook` 基类，按生命周期方法（`before_run`/`after_run`/`before_epoch`/`after_epoch`/`before_iter`/`after_iter`）注入训练流程。

---

## 【关键机制与数据】

### 工作原理

**1. 注册表机制（Registry Pattern）**
- `OPTIMIZERS`、`OPTIMIZER_BUILDERS`、`HOOKS` 均为注册表装饰器（`@xxx.register_module()`），通过装饰器自动将类注册到全局字典。
- 类被引用前**必须先 import**，否则注册表无法发现该类。原文明确指出：`mmdet.core.optimizer.my_optimizer.MyOptimizer` **不能**直接 import，只能 import 包级别路径 `mmdet.core.optimizer.my_optimizer`。

**2. 自定义模块导入的两种方式**
- **方式 A**：在 `mmdet/core/optimizer/__init__.py` 中加 `from .my_optimizer import MyOptimizer`。
- **方式 B**：在 config 中设置 `custom_imports = dict(imports=['mmdet.core.optimizer.my_optimizer'], allow_failed_imports=False)`，程序启动时自动 import。
- 路径只要能被 `PYTHONPATH` 定位即可，文件目录可任意组织。

**3. 训练工作流与 EvalHook 的关系**（原文已明确说明）
- `workflow` 字段仅控制 runner 的迭代顺序，不影响 `EvalHook`。
- `EvalHook` 由 `after_train_epoch` 触发；val 工作流只会触发 `after_val_epoch` 相关的钩子。
- 因此 `[('train', 1), ('val', 1)]` 与 `[('train', 1)]` 的**唯一区别**是：前者会在每个训练 epoch 后额外在验证集上计算 loss，后者不会。

**4. 钩子生命周期**
MMDetection 自 v2.3.0 起支持通过 config 注册自定义钩子（issue #3395），无需修改源码即可在 `before_run`/`after_run`/`before_epoch`/`after_epoch`/`before_iter`/`after_iter` 六个时间点注入自定义逻辑。

**5. 优化器构造器粒度控制**
默认构造器位于 `mmcv/runner/optimizer/default_optimizer.py`（原文给出链接），可作为新构造器的模板。其作用是按参数组（如 BN 层、bias、weight）应用差异化超参（如不同的 weight_decay 或 lr_mult）。

**6. 配置覆盖机制**
当子 config 继承父 config 中已有的 `optimizer_config` 时，需要使用 `_delete_=True` 字段以覆盖父配置中的无关设置。

---

## 【表格解读】

**原文无表格**。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

本文档处于 MMDetection 训练自定义链路的"运行时配置"层级，与以下外部模块存在上下游依赖：

- **PyTorch `torch.optim`**：所有自定义优化器最终继承自 `torch.optim.Optimizer`；用户配置 `optimizer` 字段时直接调用 PyTorch 官方 API（链接：`https://pytorch.org/docs/stable/optim.html`）。
- **mmcv.runner.optimizer**：提供 `OPTIMIZER_BUILDERS`、`OPTIMIZERS` 注册器、`build_from_cfg` 工具函数以及 `DefaultOptimizerConstructor` 默认实现。
- **mmcv.runner.hooks.lr_updater**：提供 `StepLRHook`、`CyclicLrUpdater`、CosineAnnealing、Poly 等学习率调度策略的实现。
- **mmcv.runner.hooks.momentum_updater**：提供 `CyclicMomentumUpdater`，与 `CyclicLrUpdater` 配合使用。
- **EvalHook**（位于 mmcv）：通过 `after_train_epoch` 触发，区别于 workflow 中 val 阶段触发的 `after_val_epoch` 钩子。
- **上游教程**：本文档编号为 Tutorial 5，下游应承接 config 编写、模型自定义、数据流相关教程（原文未提供具体链接）。
- **GitHub issue #3395**：MMDetection v2.3.0 引入 config 级别自定义钩子功能的来源。

---

## 【使用方法】

以下汇总原文中**实际给出的**启用方式与配置示例：

### 1. 切换 PyTorch 原生优化器
```python
optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
```
或使用默认 SGD：
```python
optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)
```

### 2. 注册自定义优化器（两种方式）

**方式 A**：在 `mmdet/core/optimizer/__init__.py` 中导入
```python
from .my_optimizer import MyOptimizer
```

**方式 B**：通过 config 的 `custom_imports` 手动导入
```python
custom_imports = dict(imports=['mmdet.core.optimizer.my_optimizer'], allow_failed_imports=False)
```

**config 中引用**：
```python
optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
```

### 3. 梯度裁剪
```python
optimizer_config = dict(
    _delete_=True, grad_clip=dict(max_norm=35, norm_type=2))
```

### 4. 动量调度（Cyclic，与 LR 调度配合）
```python
lr_config = dict(
    policy='cyclic',
    target_ratio=(10, 1e-4),
    cyclic_times=1,
    step_ratio_up=0.4,
)
momentum_config = dict(
    policy='cyclic',
    target_ratio=(0.85 / 0.95, 1),
    cyclic_times=1,
    step_ratio_up=0.4,
)
```

### 5. 学习率调度

**Poly 调度**：
```python
lr_config = dict(policy='poly', power=0.9, min_lr=1e-4, by_epoch=False)
```

**CosineAnnealing 调度（含 warmup）**：
```python
lr_config = dict(
    policy='CosineAnnealing',
    warmup='linear',
    warmup_iters=1000,
    warmup_ratio=1.0 / 10,
    min_lr_ratio=1e-5)
```

### 6. 工作流配置
```python
# 默认：仅训练
workflow = [('train', 1)]

# 训练 + 验证交替
workflow = [('train', 1), ('val', 1)]
```

### 7. 自定义钩子注册

**方式 A**：在 `mmdet/core/utils/__init__.py` 中导入自定义钩子模块。

> ⚠️ **注意**：原文在 "Register the new hook" 一节**被截断**（仅展示了 "The newly defined module should be imported in `mmdet/core/utils/__init__.py` so that the registry will find the new module and add it:" 一句，后续 `custom_imports` 方式、`__init__.py` 的导入代码、以及 config 中 `custom_hooks` 字段的引用示例等内容均缺失）。完整启用方式应参考同前文"自定义优化器"的注册逻辑——通过 `@HOOKS.register_module()` 装饰 + 模块 import 暴露给注册表。**该部分具体配置写法原文未涉及**。
