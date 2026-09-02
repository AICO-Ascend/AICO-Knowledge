# Tutorial 5: Customize Runtime Settings

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/SSD/docs/tutorials/customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/SSD/docs/tutorials/customize_runtime.md

# 一体化深度解读：Tutorial 5: Customize Runtime Settings

## 【定位】

这篇文档是 MMDetection（SSD 基于该框架）训练流程的"运行时自定义"指南，目标是让用户在不修改底层源码的前提下，通过配置文件按需替换/扩展**优化器（optimizer）**、**优化器构造器（constructor）**、**训练调度（lr/momentum schedule）**、**工作流（workflow）**和**钩子（hooks）**，从而灵活控制训练过程的优化策略、迭代顺序与运行时行为。

---

## 【技术要点】

1. **PyTorch 内置优化器替换**：仅需修改 config 中 `optimizer` 字段的 `type`，例如切换到 Adam：`optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)`，文中特别标注"performance could drop a lot"（原文警告）。
2. **自定义优化器三步流程**：
   - 在 `mmdet/core/optimizer/my_optimizer.py` 中通过 `@OPTIMIZERS.register_module()` 装饰器定义继承自 `torch.optim.Optimizer` 的类；
   - 通过修改 `mmdet/core/optimizer/__init__.py` 或在 config 中设置 `custom_imports = dict(imports=['mmdet.core.optimizer.my_optimizer'], allow_failed_imports=False)` 完成注册（注意：必须导入包而非类本身，**不能**直接 import `mmdet.core.optimizer.my_optimizer.MyOptimizer`）；
   - 在 config 中将 `optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)` 引用。
3. **优化器构造器（constructor）**：用于参数级别的精细调整（如对 BatchNorm 层设置不同的 weight_decay），通过 `@OPTIMIZER_BUILDERS.register_module()` 装饰器注册 `__call__(self, model)` 接口返回优化器实例，默认实现位于 mmcv 的 `default_constructor.py`。
4. **梯度裁剪（stabilize training）**：通过 `optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))` 实现；若 config 继承自基础 config 需要用 `_delete_=True` 覆盖。
5. **学习率/动量调度**：
   - 默认 Step 1x 策略调用 MMCV 的 `StepLRHook`；
   - Poly 策略：`policy='poly', power=0.9, min_lr=1e-4, by_epoch=False`；
   - CosineAnnealing 策略：`warmup='linear', warmup_iters=1000, warmup_ratio=1.0/10, min_lr_ratio=1e-5`；
   - Cyclic momentum schedule（用于 3D 检测加速收敛）：`target_ratio=(0.85/0.95, 1), cyclic_times=1, step_ratio_up=0.4`。
6. **工作流（workflow）**：默认 `workflow = [('train', 1)]`（每轮仅训练），可改为 `[('train', 1), ('val', 1)]` 交替训练与验证；`total_epochs` 只控制训练 epoch 数；该配置与 `EvalHook` 解耦，`EvalHook` 由 `after_train_epoch` 触发。

---

## 【关键机制与数据】

- **优化器切换机制（原文）**：`We already support to use all the optimizers implemented by PyTorch, and the only modification is to change the `optimizer` field of config files`——通过 config-driven 注册机制避免代码侵入。
- **注册机制关键点（原文）**：`The module `mmdet.core.optimizer.my_optimizer` will be imported at the beginning of the program and the class `MyOptimizer` is then automatically registered. Note that only the package containing the class `MyOptimizer` should be imported.`——这是装饰器+包级导入触发自动注册的标准模式。
- **梯度裁剪数据（原文）**：`grad_clip=dict(max_norm=35, norm_type=2)`——norm_type=2 即 L2 范数裁剪，max_norm=35 是数值阈值（未解释 35 的来源，原文未提）。
- **训练调度默认值（原文）**：`By default we use step learning rate with 1x schedule`——默认 StepLR 1x 调度。
- **Workflow 与 EvalHook 的关系（原文）**：`Workflows `[('train', 1), ('val', 1)]` and `[('train', 1)]` will not change the behavior of `EvalHook` because `EvalHook` is called by `after_train_epoch` and validation workflow only affect hooks that are called through `after_val_epoch`——这是关于 workflow 影响范围的明确边界说明：开启 val workflow 后只会在每个训练 epoch 后额外跑一次验证 loss 计算。
- **训练阶段验证的行为说明（原文）**：`The parameters of model will not be updated during val epoch`——验证 epoch 内不更新参数。
- **性能数据**：原文仅给出**警示性提示**（原文：`the performance could drop a lot`），未提供具体性能数字。

---

## 【表格解读】

**原文无表格。** 文档中所有信息均通过 Python 代码块和段落文字呈现，包括：optimizer 示例、custom_imports 示例、MyOptimizer 模板代码、gradient clip 示例、momentum_config 示例、lr_config 示例、MyHook 模板代码等，但**没有任何 markdown 表格**形式的内容。

---

## 【公式解读】

**原文无公式。** 文档中未出现任何 LaTeX 数学公式或数学推导式。文档涉及的所有"计算参数"均以 Python 配置字典形式给出，例如：

- `target_ratio=(0.85 / 0.95, 1)` —— 这是 cyclic schedule 中动量比值的两个端点（动量从 0.85/0.95 → 1），但未以公式形式表达；
- `warmup_ratio=1.0 / 10` —— warmup 初始学习率与目标学习率的比值，仅以分数形式呈现。

---

## 【关联】

- **MMCV 框架**：所有底层注册机制（`OPTIMIZERS`、`OPTIMIZER_BUILDERS`、`HOOKS`）和 LR/momentum 调度器均来自 MMCV，本文档多次引用 mmcv 仓库链接：
  - [`default_constructor.py`](https://github.com/open-mmlab/mmcv/blob/9ecd6b0d5ff9d2172c49a182eaa669e9f27bb8e7/mmcv/runner/optimizer/default_constructor.py#L11)——优化器构造器默认实现模板；
  - [`CyclicLrUpdater`](https://github.com/open-mmlab/mmcv/blob/f48241a65aebfe07db122e9db320c31b685dc674/mmcv/runner/hooks/lr_updater.py#L327) 和 [`CyclicMomentumUpdater`](https://github.com/open-mmlab/mmcv/blob/f48241a65aebfe07db122e9db320c31b685dc674/mmcv/runner/hooks/momentum_updater.py#L130)——cyclic 策略实现；
  - [`StepLRHook`](https://github.com/open-mmlab/mmcv/blob/f48241a65aebfe07db122e9db320c31b685dc674/mmcv/runner/hooks/lr_updater.py#L153)——默认 StepLR；
  - [`lr_updater.py`（mmcv）](https://github.com/open-mmlab/mmcv/blob/master/mmcv/runner/hooks/lr_updater.py)——所有支持的 lr schedule 列表入口。
- **PyTorch 优化器 API**：自定义/替换优化器遵循 [PyTorch optim 文档](https://pytorch.org/docs/stable/optim.html?highlight=optim#module-torch.optim) 规范。
- **MMDetection 配置体系**：与 [config documentation](https://mmdetection.readthedocs.io/en/latest/config.html) 关联，尤其是 `_delete_=` 与 config 继承机制相关。
- **上下游关系**：本教程是 Tutorial 系列第 5 篇（典型 MMDetection 教程序列：1 数据流水线、2 模型、3 数据集、4 推理、5 运行时自定义），位于"模型/数据已就绪，开始调训练策略"的环节，向上承接模型配置，向下衔接训练启动与 EvalHook、CheckpointHook 等运行时钩子。
- **版本特性（原文）**：`MMDetection supports customized hooks in training (#3395) since v2.3.0`——hook 自定义在 v2.3.0 后通过 config 即可完成，之前需改代码。

---

## 【使用方法】

> 文档中所有"启用方式/配置项/命令"均以 Python config 字典的形式给出，原文未涉及命令行调用。

**1. 切换 PyTorch 内置优化器（原文）**：
```python
optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
# 或默认 SGD
optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)
```

**2. 注册自定义优化器（原文）**：
- 文件路径：`mmdet/core/optimizer/my_optimizer.py`
- 装饰器：`@OPTIMIZERS.register_module()`
- 继承：`class MyOptimizer(Optimizer)`
- 任一注册方式（原文）：
```python
# 方式 A：修改 __init__.py
from .my_optimizer import MyOptimizer

# 方式 B：config 中 custom_imports
custom_imports = dict(imports=['mmdet.core.optimizer.my_optimizer'], allow_failed_imports=False)
```

**3. 自定义优化器构造器（原文）**：使用 `mmcv.runner.optimizer.OPTIMIZER_BUILDERS` 装饰器，模板见 `default_constructor.py`。

**4. 梯度裁剪（原文）**：
```python
optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))
```

**5. 学习率策略（原文）**：
```python
# Poly
lr_config = dict(policy='poly', power=0.9, min_lr=1e-4, by_epoch=False)
# CosineAnnealing with linear warmup
lr_config = dict(policy='CosineAnnealing', warmup='linear', warmup_iters=1000,
                 warmup_ratio=1.0 / 10, min_lr_ratio=1e-5)
# Cyclic（与 momentum 联合用于 3D 检测）
lr_config = dict(policy='cyclic', target_ratio=(10, 1e-4),
                 cyclic_times=1, step_ratio_up=0.4)
momentum_config = dict(policy='cyclic', target_ratio=(0.85 / 0.95, 1),
                       cyclic_times=1, step_ratio_up=0.4)
```

**6. 工作流配置（原文）**：
```python
# 默认
workflow = [('train', 1)]
# 训练+验证交替
workflow = [('train', 1), ('val', 1)]
```

**7. 自定义钩子（原文，文档此处被截断）**：
- 模板：`@HOOKS.register_module() class MyHook(Hook)`，需实现 `before_run / after_run / before_epoch / after_epoch / before_iter / after_iter` 中需要的方法；
- 注册方式：修改 `mmdet/core/utils/__init__.py` 导入新文件（原文此处不完整，后续步骤未在提供的原文中呈现）。
