# 教程 5: 自定义运行时配置

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/zh_cn/tutorials/customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/zh_cn/tutorials/customize_runtime.md

# 一体化深度解读：BEVDet_for_PyTorch · 教程 5 自定义运行时配置

## 【定位】

本教程是 BEVDet（基于 MMDetection3D 框架的 3D 检测方案）训练阶段"运行时配置"的自定义手册，解决"在不改动框架主干代码的前提下，如何灵活替换/扩展优化器、学习率规程、工作流、训练钩子以及评估/日志/检查点等运行时行为"这一工程问题，从而让用户能在同一套训练基础设施上适配不同模型、收敛策略和实验需求。

## 【技术要点】

1. **双层优化器扩展机制**
   - 框架已默认支持 PyTorch 所有 `torch.optim` 优化器，仅需修改配置文件中的 `optimizer` 字段，例如 `Adam` 范例：`type='Adam', lr=0.0003, weight_decay=0.0001`（原文明确提示"这样可能会使性能大幅下降"）。
   - 若需自定义算法，需走"实现 `Optimizer` 子类 → 注册到 `OPTIMIZERS` → 配置中 `type` 字段切换"三步流程。

2. **优化器构造器 (Optimizer Constructor) 支持细粒度参数调度**
   - 通过 `OPTIMIZER_BUILDERS` 注册的构造器可针对特定参数子集（如 BatchNorm 层 weight decay）单独设置，原文给出默认实现链接 `mmcv/runner/optimizer/default_constructor.py#L11`，可作为新构造器模版。

3. **训练过程稳定与加速的两个常用配置**
   - 梯度裁剪：`optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))`。
   - 动量规划器 (Momentum Scheduler)：原文给出"3D 检测中用于加速收敛"的 `cyclic` 策略，与学习率规划器配套使用，参数包含 `target_ratio`、`cyclic_times`、`step_ratio_up=0.4`。

4. **学习率规程默认与可选方案**
   - 默认 `StepLRHook`（阶梯式衰减 1× 规程）。
   - 备选包括多项式衰减 `poly`（`power=0.9, min_lr=1e-4, by_epoch=False`）和余弦退火 `CosineAnnealing`（带 `warmup='linear'`、`warmup_iters=1000`、`warmup_ratio=1.0/10`、`min_lr_ratio=1e-5`）。

5. **工作流 (Workflow) 灵活编排**
   - 工作流是 `(阶段, epoch 数)` 的列表。默认 `workflow = [('train', 1)]`，可改为 `[('train', 1), ('val', 1)]` 交替运行；原文明确指出：验证时模型参数不更新、`max_epochs` 只控制训练 epoch 数、`EvalHook` 仍由 `after_train_epoch` 触发，验证工作流区别仅在 runner 会在每训练 epoch 后在验证集上计算损失。

6. **钩子 (Hook) 系统的三级定制路径**
   - 路径 A：自定义钩子（继承 `Hook`，按 `before_run / after_run / before_epoch / after_epoch / before_iter / after_iter` 六个时点覆盖）→ 通过 `@HOOKS.register_module()` + `custom_imports` 或 `__init__.py` 暴露 → 在配置中以 `custom_hooks=[dict(type='MyHook', a=…, b=…)]` 装载，可设置 `priority='NORMAL'/'HIGHEST'`。
   - 路径 B：直接使用 MMCV 已实现钩子，仅改配置。
   - 路径 C：修改框架默认运行时钩子：`log_config`、`checkpoint_config`、`evaluation`、`lr_config`、`optimizer_config`、`momentum_config`，其中日志钩子优先级为 `VERY_LOW`，其余均为 `NORMAL`。

## 【关键机制与数据】

### 工作原理与数据流（按原文叙述）

- **优化器注入路径**：用户配置 `optimizer` → MMCV `build_from_cfg` 查找 `OPTIMIZERS` 注册表 → 实例化 `Optimizer`（内置或自定义子类）；若配置中包含 optimizer constructor，则先调用 constructor 对模型参数按 `paramwise_cfg` 做分组后再实例化。
- **梯度裁剪注入路径**：通过 `optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))` 把裁剪行为附加到优化器 step 之上；继承自基础配置时 `_delete_=True` 用于清除父配置冗余键。
- **动量与学习率联动**：`cyclic` 策略下动量按 `target_ratio=(0.85/0.95, 1)` 在区间内循环，配套 LR 的 `target_ratio=(10, 1e-4)` 同步循环；`step_ratio_up=0.4` 决定上升段比例，原文称"通常和学习率规划器一起使用"且"3D 检测中被用于加速模型收敛"。
- **钩子调度机制**：自定义钩子按 `priority` 在注册阶段确定次序；默认运行时钩子（除日志外）均为 `NORMAL`，注册阶段日志钩子被设为 `VERY_LOW`。
- **评估数据流**：`evaluation` 中的 `interval` 控制 `EvalHook` 触发频次，`metric` 等其他参数透传给 `dataset.evaluate()`；验证工作流通过 `after_val_epoch` 钩子调用，与 `EvalHook` 行为相互独立。

### 性能/参数数据（原文出现即标注）

- 原文：**"如果您想使用 ADAM （注意到这样可能会使性能大幅下降）"** — 即 Adam 在该 3D 检测体系下被定性为可能导致性能下降。
- 原文：`lr=0.0003, weight_decay=0.0001`（Adam 范例）。
- 原文：`lr=0.02, momentum=0.9, weight_decay=0.0001`（SGD 范例）。
- 原文：梯度裁剪 `max_norm=35, norm_type=2`。
- 原文：cyclic 动量 `target_ratio=(0.85/0.95, 1)`、cyclic LR `target_ratio=(10, 1e-4)`，两者均 `cyclic_times=1, step_ratio_up=0.4`。
- 原文：余弦退火 `warmup_iters=1000, warmup_ratio=1.0/10, min_lr_ratio=1e-5`。
- 原文：评估默认 `interval=1, metric='bbox'`。
- 原文：日志默认 `interval=50`。
- 原文：检查点默认 `interval=1`，支持 `max_keep_ckpts`、`save_optimizer` 字段。

## 【表格解读】

**原文无表格**（原文以 Python 代码块形式给出配置示例，未采用 markdown 表格组织参数对照）。

为便于查阅，下表为根据原文代码块**逐字还原**的关键配置速查（非原文表格，仅为解读辅助）：

| 配置项 | 原文示例字段 | 取值 | 作用 |
|---|---|---|---|
| optimizer (内置 Adam) | type / lr / weight_decay | 'Adam' / 0.0003 / 0.0001 | 直接调用 PyTorch 优化器 |
| optimizer (内置 SGD) | type / lr / momentum / weight_decay | 'SGD' / 0.02 / 0.9 / 0.0001 | 默认优化器范例 |
| optimizer (自定义) | type / a / b / c | 'MyOptimizer' / 自定义 | 通过注册器使用自实现优化器 |
| optimizer_config | grad_clip.max_norm / norm_type / _delete_ | 35 / 2 / True | 梯度裁剪，继承基础配置时清冗余 |
| momentum_config (cyclic) | policy / target_ratio / cyclic_times / step_ratio_up | 'cyclic' / (0.85/0.95, 1) / 1 / 0.4 | 动量按学习率节奏循环 |
| lr_config (cyclic) | policy / target_ratio / cyclic_times / step_ratio_up | 'cyclic' / (10, 1e-4) / 1 / 0.4 | 学习率循环 |
| lr_config (poly) | policy / power / min_lr / by_epoch | 'poly' / 0.9 / 1e-4 / False | 多项式衰减 |
| lr_config (CosineAnnealing) | policy / warmup / warmup_iters / warmup_ratio / min_lr_ratio | 'CosineAnnealing' / 'linear' / 1000 / 1.0/10 / 1e-5 | 余弦退火+线性 warmup |
| workflow | (阶段, epoch) 列表 | [('train', 1)] 或 [('train', 1), ('val', 1)] | 阶段编排 |
| custom_hooks | type / priority / … | 'MyHook' / 'NORMAL' 或 'HIGHEST' | 自定义钩子装载 |
| checkpoint_config | interval | 1 | `CheckpointHook` 触发间隔 |
| log_config | interval / hooks | 50 / [TextLoggerHook, TensorboardLoggerHook] | 日志钩子组合 |
| evaluation | interval / metric | 1 / 'bbox' | `EvalHook` 触发间隔与指标 |
| custom_imports | imports / allow_failed_imports | ['mmdet3d.core.optimizer.my_optimizer'] / False | 程序伊始强制导入 |

## 【公式解读】

**原文无公式**（全文以 Python 配置与类定义伪代码形式表达，未出现数学公式或 LaTeX）。

如需以伪代码形式还原优化器调用逻辑（**非原文**）：

```
optimizer_cfg = config['optimizer']
optimizer_cls = OPTIMIZERS.get(optimizer_cfg['type'])   # 注册表查找
optimizer = build_from_cfg(optimizer_cfg, OPTIMIZERS)    # 实例化

if 'optimizer_config' in config:
    grad_clip = optimizer_cfg.grad_clip                  # max_norm=35, norm_type=2
    # 在 OptimizerHook.step 内做梯度裁剪
```

符号含义：`OPTIMIZERS` 为 MMCV 全局优化器注册器；`grad_clip.max_norm` 为裁剪阈值上限，`norm_type=2` 表示 L2 范数；`_delete_=True` 是 MMCV 配置系统保留字段，用于在 `_base_` 继承时删除冗余键。

## 【关联】

本文以"运行时配置"为中心，与框架其他组件的关系如下：

- **与优化器栈的关联**：`OPTIMIZERS` / `OPTIMIZER_BUILDERS` 注册器位于 `mmcv.runner.optimizer`，由 `mmdet3d/core/optimizer/__init__.py` 与 `mmdet3d/core/__init__.py` 串入主命名空间；自定义钩子路径 `mmdet3d/core/utils/my_hook.py` 同理通过 `mmdet3d/core/utils/__init__.py` 注册。
- **与学习率/动量规划器的关联**：底层实现由 MMCV 提供，链接为 `mmcv/runner/hooks/lr_updater.py`（含 `StepLRHook`、多项式、余弦退火、`CyclicLrUpdater`）与 `mmcv/runner/hooks/momentum_updater.py`（`CyclicMomentumUpdater`）。
- **与执行器 (Runner) 的关联**：`workflow` 由 Runner 直接消费；`max_epochs` 仅控制训练 epoch；`EvalHook` 由 `after_train_epoch` 触发，验证工作流通过 `after_val_epoch` 影响其他钩子。
- **与运行时默认钩子的关联**：`optimizer_config`/`lr_config`/`momentum_config`/`checkpoint_config`/`log_config`/`evaluation` 属于内置钩子，被 Runner 自动注册；`custom_hooks` 是用户扩展钩子的并列通道。
- **与配置继承机制的关联**：`_delete_=True` 字段用于 `_base_` 继承时清理父配置无意义字段，依赖 MMCV 配置系统语义。
- **与上游教程的衔接**：本文为"教程 5"，承接前序教程所建立的数据集、模型与配置体系，是模型训练入口侧的可定制化层。

## 【使用方法】

1. **直接使用内置优化器**
   修改配置 `optimizer` 字段，例如：
   ```python
   optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
   ```

2. **注册并使用自定义优化器**
   - 新建 `mmdet3d/core/optimizer/my_optimizer.py`，继承 `torch.optim.Optimizer` 并以 `@OPTIMIZERS.register_module()` 装饰。
   - 在 `mmdet3d/core/optimizer/__init__.py` 中 `from .my_optimizer import MyOptimizer` 并加入 `__all__`；或在配置中加 `custom_imports = dict(imports=['mmdet3d.core.optimizer.my_optimizer'], allow_failed_imports=False)`。
   - 在配置中：`optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)`。
   - **注意**：必须导入包路径而非具体类路径（如 `mmdet3d.core.optimizer.my_optimizer` 合法，`mmdet3d.core.optimizer.my_optimizer.MyOptimizer` 不合法）。

3. **自定义优化器构造器**
   在 `mmdet3d/core/optimizer/` 下新建构造器文件，继承 `object` 并以 `@OPTIMIZER_BUILDERS.register_module()` 装饰，实现 `__call__(self, model) -> my_optimizer`；可参考 `mmcv/runner/optimizer/default_constructor.py`。

4. **梯度裁剪 / 动量规划器**
   ```python
   optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))
   lr_config = dict(policy='cyclic', target_ratio=(10, 1e-4), cyclic_times=1, step_ratio_up=0.4)
   momentum_config = dict(policy='cyclic', target_ratio=(0.85/0.95, 1), cyclic_times=1, step_ratio_up=0.4)
   ```

5. **学习率规程切换**
   ```python
   lr_config = dict(policy='poly', power=0.9, min_lr=1e-4, by_epoch=False)
   # 或
   lr_config = dict(policy='CosineAnnealing', warmup='linear', warmup_iters=1000,
                    warmup_ratio=1.0/10, min_lr_ratio=1e-5)
   ```

6. **工作流设置**
   ```python
   workflow = [('train', 1)]                       # 仅训练
   workflow = [('train', 1), ('val', 1)]            # 交替
   ```
   须配合 `runner = dict(type='EpochBasedRunner', max_epochs=...)` 中 `max_epochs` 控制训练 epoch 数（原文未涉及具体配置命令细节）。

7. **自定义钩子三步走**
   - 在 `mmdet3d/core/utils/my_hook.py` 中继承 `mmcv.runner.Hook` 实现六个时点方法之一或多个，并以 `@HOOKS.register_module()` 装饰。
   - 在 `mmdet3d/core/utils/__init__.py` 中 `from .my_hook import MyHook`；或配置中 `custom_imports = dict(imports=['mmdet3d.core.utils.my_hook'], allow_failed_imports=False)`。
   - 配置：
     ```python
     custom_hooks = [dict(type='MyHook', a=a_value, b=b_value, priority='NORMAL')]
     ```
     `priority` 可选 `'NORMAL'` 或 `'HIGHEST'`，默认 `NORMAL`。

8. **调整默认运行时钩子**
   ```python
   checkpoint_config = dict(interval=1)            # 可加 max_keep_ckpts、save_optimizer
   log_config = dict(interval=50, hooks=[dict(type='TextLoggerHook'),
                                         dict(type='TensorboardLoggerHook')])
   evaluation = dict(interval=1, metric='bbox')    # 其他参数透传 dataset.evaluate()
   ```
