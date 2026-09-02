# Tutorial 6: Customize Runtime Settings

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/en/tutorials/customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/en/tutorials/customize_runtime.md

# 文档深度解读: Tutorial 6: Customize Runtime Settings

---

## 【定位】

这篇文档是 MMSegmentation 框架下 BiseNetV1_for_PyTorch 模型仓的运行时定制教程,系统性说明如何自定义训练过程中的**优化器、优化器构造器、学习率调度器、训练工作流、Hooks** 等运行时组件,解决"在不修改框架核心代码的前提下,通过配置文件或轻量级代码扩展灵活调整训练流程"的问题。

---

## 【技术要点】

1. **优化器切换(Optimizer Switching)**: 通过修改 config 文件中的 `optimizer` 字段即可切换 PyTorch 已实现的优化器(如 `Adam`,原文示例 `Adam` 使用 `lr=0.0003`, `weight_decay=0.0001`)。
2. **自定义优化器注册三步法**: 在 `mmseg/core/optimizer/` 目录下新建文件 → 通过 `@OPTIMIZERS.register_module()` 装饰 → 在 `__init__.py` 或使用 `custom_imports` 显式导入,即可使新优化器出现在注册表中。
3. **优化器构造器(Optimizer Constructor)**: 用于精细化参数配置(如对 BatchNorm 层设定特定的 weight_decay),通过 `@OPTIMIZER_BUILDERS.register_module()` 注册,模板位于 MMCV `default_constructor.py`。
4. **梯度裁剪(Gradient Clip)**: 通过 `optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))` 稳定训练;当 config 继承自已有 `optimizer_config` 的 base config 时,需用 `_delete_=True` 覆盖。
5. **动量调度(Momentum Schedule)**: 与 LR scheduler 配合使用,原文示例 `CyclicLrUpdater` 中 `target_ratio=(10, 1e-4)`, `cyclic_times=1`, `step_ratio_up=0.4`;`CyclicMomentumUpdater` 中 `target_ratio=(0.85 / 0.95, 1)`,相同 `cyclic_times=1`, `step_ratio_up=0.4`。
6. **训练工作流(Workflow)**: 默认 `workflow = [('train', 1)]` 仅训练;改为 `[('train', 1), ('val', 1)]` 时每个 epoch 依次做 1 轮训练与 1 轮验证,但 `EvalHook` 由 `after_train_epoch` 触发,因此 val epoch 主要影响 `after_val_epoch` 类型的 hooks(主要用于计算验证集 loss)。
7. **默认 Runtime Hooks 与优先级**: `log_config` 的优先级为 `VERY_LOW`,其余 `checkpoint_config`、`evaluation`、`lr_config`、`optimizer_config`、`momentum_config` 的优先级均为 `NORMAL`;新增 hook 通过 `custom_hooks` 列表注册,如 `dict(type='MyHook', a=a_value, b=b_value, priority='NORMAL')`。

---

## 【关键机制与数据】

**工作原理 / 数据流**:

- **注册表机制(Registry Mechanism)**: 优化器/构造器/Hook 通过 `@OPTIMIZERS.register_module()` 等装饰器进入注册表。config 中 `optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)` 的 `type` 字段即注册表 key。
- **自定义模块的导入路径约束(原文)**: "Only the package containing the class `MyOptimizer` should be imported. `mmseg.core.optimizer.my_optimizer.MyOptimizer` **cannot** be imported directly."——只能导入包级别的模块,不能直接导入具体类路径。
- **PYTHONPATH 灵活性**: 使用 `custom_imports` 时,只要模块根位于 `PYTHONPATH`,用户可以使用完全不同的目录结构。
- **配置继承与覆盖(原文)**: "If your config inherits the base config which already sets the `optimizer_config`, you might need `_delete_=True` to override the unnecessary settings."——通过 `_delete_=True` 字段从父 config 中删除已有键。
- **默认学习率策略(原文)**: "By default we use step learning rate with 40k/80k schedule, this calls `PolyLrUpdaterHook` in MMCV."——即默认 40000/80000 次迭代的 step schedule,实际实现是 `PolyLrUpdaterHook`。
- **Workflow 副作用细节(原文)**: Workflow 中 val epoch 期间模型参数**不会**更新;`total_epochs` 仅控制训练 epoch 数,**不影响**验证 workflow;`[('train', 1), ('val', 1)]` 与 `[('train', 1)]` 的唯一区别是 runner 会在每训练 epoch 后计算验证集 loss。
- **Checkpoint 配置字段(原文)**: `checkpoint_config = dict(interval=1)`,可通过 `max_keep_ckpts` 控制保留的 checkpoint 数量,通过 `save_optimizer` 控制是否保存 optimizer state_dict。
- **Log 框架支持**: 原文列出 MMCV 支持的 logger hook 包括 `WandbLoggerHook`、`MlflowLoggerHook`、`TensorboardLoggerHook`(原文日志配置截断)。

**性能数据**: 原文未提供具体的性能基准数字,仅以"note that the performance could drop a lot"作为 ADAM 的定性提示(无具体数值)。

---

## 【表格解读】

**原文无表格**。文档以代码片段和配置示例为主,未提供参数表、性能对比表或配置项总表。

---

## 【公式解读】

**原文无公式**。文档未包含任何 LaTeX 公式或伪代码公式。可视为配置片段中出现的关键数值表达式,已在【技术要点】中以原文形式保留。

---

## 【关联】

文档通过以下外部链接与上游/下游模块紧密关联(原文给出的引用):

| 关联项 | 链接 / 模块 | 作用 |
|---|---|---|
| PyTorch Optimizer API | https://pytorch.org/docs/stable/optim.html?highlight=optim#module-torch.optim | 自定义优化器时,参数遵循 PyTorch Optimizer 接口 |
| 默认优化器构造器模板 | https://github.com/open-mmlab/mmcv/blob/9ecd6b0d5ff9d2172c49a182eaa669e9f27bb8e7/mmcv/runner/optimizer/default_constructor.py#L11 | `DefaultOptimizerConstructor` 作为新构造器的实现模板 |
| `CyclicLrUpdater` | https://github.com/open-mmlab/mmcv/blob/f48241a65aebfe07db122e9db320c31b685dc674/mmcv/runner/hooks/lr_updater.py#L327 | 循环学习率更新器实现 |
| `CyclicMomentumUpdater` | https://github.com/open-mmlab/mmcv/blob/f48241a65aebfe07db122e9db320c31b685dc674/mmcv/runner/hooks/momentum_updater.py#L130 | 循环动量更新器实现 |
| `PolyLrUpdaterHook` | https://github.com/open-mmlab/mmcv/blob/826d3a7b68596c824fa1e2cb89b6ac274f52179c/mmcv/runner/hooks/lr_updater.py#L196 | 默认 40k/80k step 调度的实际多边形 LR 实现 |
| LR Updater 全集 | https://github.com/open-mmlab/mmcv/blob/master/mmcv/runner/hooks/lr_updater.py | 包含 `CosineAnnealing`、`Poly` 等多种 LR schedule |
| `CheckpointHook` | https://github.com/open-mmlab/mmcv/blob/9ecd6b0d5ff9d2172c49a182eaa669e9f27bb8e7/mmcv/runner/hooks/checkpoint.py#L9 | 用于初始化 checkpoint 保存行为 |
| CheckpointHook 参数文档 | https://mmcv.readthedocs.io/en/latest/api.html#mmcv.runner.CheckpointHook | `max_keep_ckpts`、`save_optimizer` 等参数说明 |
| MMCV Logger 文档 | https://mmcv.readthedocs.io/en/latest/api.html | `WandbLoggerHook`、`MlflowLoggerHook`、`TensorboardLoggerHook` 用法 |
| Config 文档 | https://mmsegmentation.readthedocs.io/en/latest/config.html | `_delete_=True` 等 config 继承机制 |

**模块间关系**:
- 文档同时引用 MMSegmentation(`mmseg/core/optimizer/`)与 MMCV(`mmcv/runner/hooks/`、`mmcv/runner/optimizer/`),体现了 **MMEngine/MMCV 作为底层 runner 框架、MMSegmentation 作为领域扩展** 的两层架构。
- 本教程属于 Tutorial 系列(标题"Tutorial 6"),前序教程覆盖了 config 结构、数据 pipeline、模型自定义等内容;`optimizer_config`、`momentum_config`、`lr_config` 的修改在"先前的教程"中已涉及。
- 文档末尾被截断(`log_config` 段落以 `https://mmcv.readthedocs.io/en/latest/api.` 终止),后续 `evaluation` 配置与完整 log_config 说明未给出。

---

## 【使用方法】

**启用方式 / 配置项 / 命令**(仅原文出现的内容):

### 1. 切换/使用 PyTorch 内置优化器
修改 config 的 `optimizer` 字段:
```python
optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
```

### 2. 注册自定义优化器(三步)
- **步骤 1**: 在 `mmseg/core/optimizer/` 下新建 `my_optimizer.py`,使用 `@OPTIMIZERS.register_module()` 装饰器,继承 `torch.optim.Optimizer`。
- **步骤 2a**: 在 `mmseg/core/optimizer/__init__.py` 中添加 `from .my_optimizer import MyOptimizer`。
- **步骤 2b**(替代方案): 在 config 中声明
  ```python
  custom_imports = dict(imports=['mmseg.core.optimizer.my_optimizer'], allow_failed_imports=False)
  ```
- **步骤 3**: 在 config 中使用
  ```python
  optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
  ```

### 3. 自定义优化器构造器
使用 `@OPTIMIZER_BUILDERS.register_module()` 装饰 `MyOptimizerConstructor`,实现 `__init__(optimizer_cfg, paramwise_cfg=None)` 与 `__call__(model)` 方法。

### 4. 梯度裁剪
```python
optimizer_config = dict(
    _delete_=True, grad_clip=dict(max_norm=35, norm_type=2))
```

### 5. 动量调度(配合 LR 调度)
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

### 6. 自定义训练 Schedule
- Step schedule: `lr_config = dict(policy='step', step=[9, 10])`
- CosineAnnealing schedule:
  ```python
  lr_config = dict(
      policy='CosineAnnealing',
      warmup='linear',
      warmup_iters=1000,
      warmup_ratio=1.0 / 10,
      min_lr_ratio=1e-5)
  ```

### 7. 自定义 Workflow
```python
workflow = [('train', 1)]              # 默认:仅训练
workflow = [('train', 1), ('val', 1)]  # 1 训练 + 1 验证,交替进行
```

### 8. 注册自定义 Hook
```python
custom_hooks = [
    dict(type='MyHook', a=a_value, b=b_value, priority='NORMAL')
]
```

### 9. 修改 Checkpoint 配置
```python
checkpoint_config = dict(interval=1)
```
可通过 `max_keep_ckpts`(保留数量)与 `save_optimizer`(是否保存 optimizer state_dict)进一步控制(原文未给出示例数值)。

**命令 / 训练启动脚本**: 原文未涉及具体启动命令(如 `python tools/train.py` 等),相关启动方式请参考仓库内其他教程文档。
