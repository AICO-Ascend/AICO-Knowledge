# 教程 6: 自定义运行设定

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/zh_cn/tutorials/customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/zh_cn/tutorials/customize_runtime.md

# 一体化深度解读：BiseNetV1_for_PyTorch 教程 6 — 自定义运行设定

---

## 【定位】

本教程解决如何在 MMSegmentation 框架内**通过纯配置文件方式自定义训练运行的全部关键子模块**（优化器、训练计划表、工作流、钩子）的问题，使开发者无需改动框架源码即可适配不同的训练需求。

---

## 【技术要点】

1. **优化器自定义三段式**：① 在 `optimizer` 域切换 PyTorch 内置优化器；② 在 `mmseg/core/optimizer/` 下新建文件并用 `@OPTIMIZERS.register_module()` 注册自定义类；③ 通过 `__init__.py` 导入或 `custom_imports` 让注册器发现该类。
2. **优化器构造器（constructor）粒度控制**：通过实现 `@OPTIMIZER_BUILDERS.register_module()` 的 `MyOptimizerConstructor` 类，可对不同参数组（如 BatchNorm 层）差异化设置 weight_decay 等超参。
3. **额外训练稳定/加速机制**：
   - 梯度截断（gradient clip）：`grad_clip=dict(max_norm=35, norm_type=2)`
   - 动量计划表（momentum schedule）：与 cyclic LR 联动，`target_ratio=(0.85/0.95, 1)`、`cyclic_times=1`、`step_ratio_up=0.4`
4. **默认训练计划**：基于 `PolyLrUpdaterHook`，按 40k/80k 迭代步设置学习率；同时支持 `Step`、`CosineAnnealing`（含 `warmup='linear'`、`warmup_iters=1000`、`warmup_ratio=1.0/10`、`min_lr_ratio=1e-5`）等。
5. **工作流（workflow）**：默认 `[('train', 1)]`，可改为 `[('train', 1), ('val', 1)]` 实现交替；`total_epochs` 仅控制训练 epoch 数，**不影响**验证工作流。
6. **三类 runtime hook 配置**：`checkpoint_config`（`interval=1`）、`log_config`（`interval=50`，可叠加 `TextLoggerHook`/`TensorboardLoggerHook`）、`evaluation`（`interval=1, metric='mIoU'`）；这些钩**不被** `custom_hooks` 注册。

---

## 【关键机制与数据】

### 工作原理（注册器机制）

- **优化器发现机制**：自定义 `MyOptimizer` 类后，必须通过 `from .my_optimizer import MyOptimizer` 写入 `mmseg/core/optimizer/__init__.py` **或**通过配置文件 `custom_imports = dict(imports=['mmseg.core.optimizer.my_optimizer'], allow_failed_imports=False)` 让模块在程序启动时被导入，**不可直接导入 `MyOptimizer` 类**，否则注册器无法自动发现。
- **钩子优先级机制**（原文）：`log_config`、`checkpoint_config`、`evaluation`、`lr_config`、`optimizer_config`、`momentum_config` **不**走 `custom_hooks` 注册；其中仅 logger hook 的优先级为 `VERY_LOW`，其余均为 `NORMAL`。

### 数据流（workflow → EvalHook）

- **原文**：工作流 `[('train', 1), ('val', 1)]` 与 `[('train', 1)]` **不会改变** `EvalHook` 的行为——因为 `EvalHook` 由 `after_train_epoch` 触发，而验证工作流仅影响通过 `after_val_epoch` 调用的钩子。两者的**唯一区别**在于：交替工作流会让 runner 在每个训练 epoch 结束后计算验证集上的 loss。
- 验证阶段模型的参数**不会自动更新**（原文）。

### 性能/默认数据

- 原文：**默认训练迭代步数为 40k/80k**（用于 `PolyLrUpdaterHook` 的学习率调度基线）。
- 原文：**ADAM 示例** `lr=0.0003, weight_decay=0.0001`（同时警告该操作可能使模型表现下降）。
- 原文：优化器构造器默认实现的参考链接指向 `mmcv/runner/optimizer/default_constructor.py`，可作为新构造器的模板。

---

## 【表格解读】

**原文无表格。**

> 备注：原文中所有配置均以 Python `dict` 形式给出，并未以表格形式整理参数对照；因此无表格可逐字还原。

---

## 【公式解读】

**原文无公式。**

> 备注：原文未出现任何 LaTeX 数学公式或伪代码形式的算法表达式；所有参数化逻辑均通过配置字典实现。

---

## 【关联】

### 上下游/关联模块

| 关联对象 | 关系说明 |
|---|---|
| **MMCV `OPTIMIZERS` 注册器** | 自定义优化器通过 `@OPTIMIZERS.register_module()` 加入该全局注册器（来自 `mmcv.runner.optimizer`） |
| **MMCV `OPTIMIZER_BUILDERS` 注册器** | 自定义构造器通过 `@OPTIMIZER_BUILDERS.register_module()` 注册，与 `OPTIMIZERS` 同源 |
| **`mmseg/core/optimizer/__init__.py`** | 是注册器发现新优化器的"主命名空间"入口 |
| **`PolyLrUpdaterHook`（MMCV）** | 框架默认的训练计划表实现，与 `CosineAnnealing`、`Step` 并列为可选项 |
| **`CyclicLrUpdater` / `CyclicMomentumUpdater`（MMCV）** | 动量计划表与学习率计划表必须联动使用，原文给出 3D 检测常用配置示例 |
| **`CheckpointHook`（MMCV）** | 由 `checkpoint_config` 初始化，支持 `max_keep_ckpts`、`save_optimizer` 参数 |
| **`EvalHook`（mmseg）** | 由 `evaluation` 配置初始化，触发时机为 `after_train_epoch`；额外参数透传给 `dataset.evaluate()` |
| **`WandbLoggerHook` / `MlflowLoggerHook` / `TensorboardLoggerHook`（MMCV）** | 由 `log_config.hooks` 列表装配 |
| **`after_train_epoch` / `after_val_epoch` 钩子时机** | 决定 `EvalHook` 与 workflow 验证行为的差异，是本文最重要的语义关系 |
| **`_delete_=True`（配置覆盖机制）** | 当继承基础配置需要重写 `optimizer_config` 时使用 |

### 内部链接信息

（无）——原文未提供内部锚点链接，所有引用均指向外部 GitHub 或官方文档站。

---

## 【使用方法】

### 1. 切换 PyTorch 内置优化器

修改配置文件的 `optimizer` 域（示例：切换为 Adam）：

```python
optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
```

### 2. 启用自定义优化器

- 新建文件 `mmseg/core/optimizer/my_optimizer.py`，定义继承 `torch.optim.Optimizer` 的类并用 `@OPTIMIZERS.register_module()` 装饰。
- 二选一让注册器发现该类：
  - **方式 A**：在 `mmseg/core/optimizer/__init__.py` 中添加 `from .my_optimizer import MyOptimizer`
  - **方式 B**：在配置文件中写 `custom_imports = dict(imports=['mmseg.core.optimizer.my_optimizer'], allow_failed_imports=False)`（模块根路径需加入 `PYTHONPATH`）
- 在配置中调用：`optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)`

### 3. 自定义优化器构造器

实现 `MyOptimizerConstructor` 类（注册到 `OPTIMIZER_BUILDERS`），可参照 `mmcv/runner/optimizer/default_constructor.py` 的默认实现作为模板。

### 4. 启用梯度截断

```python
optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))
```

> 若配置继承自已设置 `optimizer_config` 的基础配置，需用 `_delete_=True` 重写。

### 5. 启用 cyclic 学习率 + 动量联动

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

### 6. 切换训练计划表

```python
# Step schedule
lr_config = dict(policy='step', step=[9, 10])

# CosineAnnealing schedule
lr_config = dict(
    policy='CosineAnnealing',
    warmup='linear',
    warmup_iters=1000,
    warmup_ratio=1.0 / 10,
    min_lr_ratio=1e-5)
```

### 7. 自定义工作流

```python
workflow = [('train', 1)]                              # 默认：仅训练 1 epoch
workflow = [('train', 1), ('val', 1)]                  # 训练 1 epoch、验证 1 epoch 交替
```

### 8. 启用自定义 Hook / 修改 Runtime Hook

```python
# 自定义 hook（MMCV 已实现）
custom_hooks = [
    dict(type='MyHook', a=a_value, b=b_value, priority='NORMAL')
]

# 检查点配置
checkpoint_config = dict(interval=1)   # 可选参数：max_keep_ckpts、save_optimizer

# 日志配置
log_config = dict(
    interval=50,
    hooks=[
        dict(type='TextLoggerHook'),
        dict(type='TensorboardLoggerHook')
    ])

# 评估配置
evaluation = dict(interval=1, metric='mIoU')   # 其余键透传给 dataset.evaluate()
```
