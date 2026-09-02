# Tutorial 5: Customize Runtime Settings

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/en/tutorials/customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/en/tutorials/customize_runtime.md

【定位】
本文是 MMDetection3D / BEVDet 训练框架下的 **"Tutorial 5: Customize Runtime Settings"**，聚焦训练阶段的运行期可定制能力——系统性地讲解如何自定义优化器、优化器构造器、学习率/动量调度、训练 workflow 以及 hook，使研究者能够在不改动框架主体代码的前提下灵活调整训练超参与执行流程。

【技术要点】

1. **PyTorch 内置优化器直接复用**：通过修改 config 的 `optimizer.type` 字段切换优化器，无需写代码；例如改用 Adam 时配 `lr=0.0003, weight_decay=0.0001`，文档明确提示"performance could drop a lot"。
2. **自研优化器注册机制**：在 `mmdet3d/core/optimizer/my_optimizer.py` 中通过 `@OPTIMIZERS.register_module()` 装饰器注册自定义类，再通过 `mmdet3d/core/optimizer/__init__.py` 或 `mmdet3d/core/__init__.py` 的 `from .optimizer import *` 让注册器可见，亦可在 config 用 `custom_imports` 手动导入。
3. **优化器构造器（parameter-wise 配置）**：使用 `@OPTIMIZER_BUILDERS.register_module()` 注册的 `MyOptimizerConstructor` 可针对 BatchNorm 等层做差异化 weight decay，参考 `default_constructor.py`。
4. **梯度裁剪稳定训练**：`optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))`，并提示继承基 config 时需 `_delete_=True` 覆盖父配置。
5. **Cyclic LR + Cyclic Momentum 联合加速收敛**：3D 检测示例，`lr_config` 用 `target_ratio=(10, 1e-4)`、`momentum_config` 用 `target_ratio=(0.85/0.95, 1)`，`cyclic_times=1`、`step_ratio_up=0.4`。
6. **学习率调度**：默认调用 `StepLRHook` 的 1x schedule；另支持 Poly（`power=0.9, min_lr=1e-4, by_epoch=False`）和 CosineAnnealing（带 linear warmup，warmup_iters=1000、warmup_ratio=1.0/10、min_lr_ratio=1e-5）。
7. **Workflow 控制训练/验证迭代顺序**：默认 `[('train', 1)]`；可改为 `[('train', 1), ('val', 1)]`，并明确 `max_epochs` 只影响训练 epoch 数。
8. **自定义 Hook 注册**：通过 `@HOOKS.register_module()` 装饰 `Hook` 子类，覆盖 `before_run/after_run/before_epoch/after_epoch/before_iter/after_iter` 六个生命周期回调；自 v2.3.0 起可纯 config 启用而无需改框架代码。

【关键机制与数据】

- **工作原理**（原文）：注册器机制——`OPTIMIZERS`、`OPTIMIZER_BUILDERS`、`HOOKS` 分别维护三类组件的可索引字典；模块只要被导入主命名空间，装饰器就自动完成登记；config 中通过 `type='MyXxx'` 字符串查表匹配，参数按 kwargs 透传给构造函数。
- **数据流**（原文）：训练循环由 runner 调度，按 workflow 顺序执行 `(phase, epochs)`；每个 phase 内依次触发 hook 的 `before_epoch → before_iter → [train_step] → after_iter → after_epoch`；`EvalHook` 由 `after_train_epoch` 触发，独立于 validation workflow。
- **性能/超参数据**（原文）：
  - Adam 样例：`lr=0.0003, weight_decay=0.0001`
  - SGD 样例：`lr=0.02, momentum=0.9, weight_decay=0.0001`
  - Gradient clip：`max_norm=35, norm_type=2`
  - Cyclic LR：`target_ratio=(10, 1e-4), cyclic_times=1, step_ratio_up=0.4`
  - Cyclic Momentum：`target_ratio=(0.85/0.95, 1), cyclic_times=1, step_ratio_up=0.4`
  - Poly schedule：`power=0.9, min_lr=1e-4, by_epoch=False`
  - CosineAnnealing：`warmup_iters=1000, warmup_ratio=1.0/10, min_lr_ratio=1e-5`

【表格解读】

原文无表格。

【公式解读】

原文无公式（仅有 `target_ratio` 等元组形式的数值参数，已在上文逐项列出）。

【关联】

- **上游框架依赖**：所有注册器（`OPTIMIZERS`、`OPTIMIZER_BUILDERS`、`HOOKS`）来自 `mmcv.runner.optimizer` 与 `mmcv.runner`；默认 `DefaultOptimizerConstructor` 来自 `mmcv/runner/optimizer/default_constructor.py`（v1.3.7）。
- **下游被引用组件**：
  - `StepLRHook`（默认 1x schedule）位于 `mmcv/runner/hooks/lr_updater.py#L167`；
  - `CyclicLrUpdater`（`#L358`）与 `CyclicMomentumUpdater`（`mmcv/runner/hooks/momentum_updater.py#L225`）分别提供 cyclic 学习率与动量更新；
  - `EvalHook` 由 `after_train_epoch` 触发，与 validation workflow 行为解耦；
  - 自定义 Hook 通过 `mmdet3d/core/utils/my_hook.py` 路径接入，对应 `mmdet3d/core/utils/__init__.py` 的导入点。
- **与同仓其他 Tutorial 的关系**：本文是 Tutorial 5，通常接续 config 基础（Tutorial 1）与模型定制（Tutorial 2）等，引用 `mmdetection.readthedocs.io` 的 config 文档以解释 `_delete_` 用法。

【使用方法】

- **切换内置优化器**：在 config 中 `optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)`，参数与 `torch.optim` API 对齐。
- **注册自定义优化器**：(1) 在 `mmdet3d/core/optimizer/my_optimizer.py` 定义类并加 `@OPTIMIZERS.register_module()`；(2) 在 `mmdet3d/core/optimizer/__init__.py` 加 `from .my_optimizer import MyOptimizer` 并填入 `__all__`，或在 `mmdet3d/core/__init__.py` 加 `from .optimizer import *`，亦可在 config 用 `custom_imports = dict(imports=['mmdet3d.core.optimizer.my_optimizer'], allow_failed_imports=False)`；(3) config 中 `optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)`。
- **自定义优化器构造器**：仿照 `default_constructor.py` 实现 `__init__(optimizer_cfg, paramwise_cfg=None)` 与 `__call__(model)`，加 `@OPTIMIZER_BUILDERS.register_module()`。
- **启用梯度裁剪**：`optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))`。
- **启用 Cyclic LR + Momentum**：按上文 `lr_config` / `momentum_config` 字典配置。
- **切换 LR schedule**：Poly 用 `lr_config = dict(policy='poly', power=0.9, min_lr=1e-4, by_epoch=False)`；CosineAnnealing 用对应带 warmup 的配置。
- **改 Workflow**：`workflow = [('train', 1), ('val', 1)]`；注意 `max_epochs` 仅约束训练 epoch。
- **注册自定义 Hook**：在 `mmdet3d/core/utils/my_hook.py` 中定义 `Hook` 子类并加 `@HOOKS.register_module()`，在 `mmdet3d/core/utils/__init__.py` 中导入；自 v2.3.0 起可纯 config 启用。
