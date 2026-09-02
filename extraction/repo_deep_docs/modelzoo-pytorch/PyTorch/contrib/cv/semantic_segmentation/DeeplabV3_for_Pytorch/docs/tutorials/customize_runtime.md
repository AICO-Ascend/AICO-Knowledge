# Tutorial 6: Customize Runtime Settings

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs/tutorials/customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs/tutorials/customize_runtime.md

# 一体化深度解读：Tutorial 6 - Customize Runtime Settings

## 【定位】
本文是 MMSegmentation（mmseg）面向高级用户/开发者的教程（Tutorial 6），系统性阐述如何**在不解码核心训练框架的前提下，通过配置文件和注册机制扩展训练运行时的优化器、学习率调度、工作流、钩子（hooks）等行为**，从而适配下游定制需求。

---

## 【技术要点】

1. **PyTorch 原生优化器的零侵入替换**：直接修改配置文件的 `optimizer` 字段即可换用任何 `torch.optim` 中实现的优化器；原文示例为 `Adam`，配 `lr=0.0003, weight_decay=0.0001`。
2. **自研优化器的注册路径**：在 `mmseg/core/optimizer/` 下新建文件 → 用 `@OPTIMIZERS.register_module()` 装饰类继承 `torch.optim.Optimizer` → 通过修改 `__init__.py` 或配置 `custom_imports = dict(imports=['mmseg.core.optimizer.my_optimizer'], allow_failed_imports=False)` 导入 → 配置 `type='MyOptimizer', a=..., b=..., c=...` 启用。
3. **逐参数优化器构造器（Optimizer Constructor）**：通过 `@OPTIMIZER_BUILDERS.register_module()` 注册一个接受 `optimizer_cfg` 和 `paramwise_cfg` 的 `__call__(self, model)` 类，可针对 BatchNorm 等层单独设置 weight decay。
4. **梯度裁剪 + 动量调度叠加**：在 `optimizer_config` 中追加 `grad_clip=dict(max_norm=35, norm_type=2)`（覆盖父配置时需 `_delete_=True`）；通过 `momentum_config` 与 `lr_config` 联用 `cyclic` 策略加速收敛，原文给出 3D 检测示例 `target_ratio=(0.85 / 0.95, 1)` 等。
5. **训练调度默认值与替代项**：默认调用 mmcv 中的 `PolyLrUpdaterHook`（40k/80k 步进）；支持 step（`lr_config = dict(policy='step', step=[9, 10])`）和 CosineAnnealing（带 `warmup='linear'`、`warmup_iters=1000`、`warmup_ratio=1.0/10`、`min_lr_ratio=1e-5`）。
6. **工作流与运行时钩子**：默认 `workflow = [('train', 1)]`，加入 `('val', 1)` 即可让验证穿插于训练；内置运行时钩子按优先级运行（log_config 为 `VERY_LOW`，lr_config/optimizer_config/momentum_config/evaluation/checkpoint_config 为 `NORMAL`），并可通过 `custom_hooks` 列表追加。

---

## 【关键机制与数据】

### 优化器注册机制（基于 mmcv registry）
- 原文：通过 `@OPTIMIZERS.register_module()` 装饰，使得类被自动登记到全局注册表；只有包含类的**包**（如 `mmseg.core.optimizer.my_optimizer`）能被导入，直接导入具体类 `mmseg.core.optimizer.my_optimizer.MyOptimizer` 是被禁止的（原文加粗 "**cannot**"）。
- 原文：`custom_imports` 机制允许用户使用任意目录结构，只要模块根在 `PYTHONPATH` 中可定位即可被运行时自动加载。

### 优化器构造器原理
- 原文：默认实现位于 `mmcv/runner/optimizer/default_constructor.py#L11`，作为新构造器模板；构造器接收 `optimizer_cfg` 与 `paramwise_cfg=None`，`__call__(model)` 返回构造好的 optimizer 实例，承担"weight decay for BatchNorm layers"等参数差异化设置。

### 工作流与 EvalHook 的关系
- 原文：`workflow = [('train', 1), ('val', 1)]` 与 `[('train', 1)]` 不会改变 `EvalHook` 的行为，因为 `EvalHook` 由 `after_train_epoch` 触发；验证 workflow 仅影响通过 `after_val_epoch` 调用的钩子，且 **val epoch 期间模型参数不会被更新**，故二者唯一区别是后者会让 runner 在每个训练 epoch 后计算验证集损失。
- 原文：`total_epochs` 仅控制训练 epoch 数，不影响验证 workflow。

### 运行时钩子优先级（原文）
- `log_config` → priority `VERY_LOW`
- `checkpoint_config` / `evaluation` / `lr_config` / `optimizer_config` / `momentum_config` → priority `NORMAL`

### 训练调度默认值（原文）
- 默认策略：step learning rate with 40k/80k schedule，调用 `PolyLrUpdaterHook`（位于 `mmcv/runner/hooks/lr_updater.py#L196`）。

### Cyclic Momentum/LR 原文关键数值
- `lr_config.target_ratio=(10, 1e-4)`，`cyclic_times=1`，`step_ratio_up=0.4`
- `momentum_config.target_ratio=(0.85 / 0.95, 1)`，`cyclic_times=1`，`step_ratio_up=0.4`
- 原文说明：该配置源自 3D detection 场景，用于配合 LR scheduler 加速收敛。

### 梯度裁剪原文关键数值
- `grad_clip=dict(max_norm=35, norm_type=2)`

### Checkpoint hook（原文）
- `checkpoint_config = dict(interval=1)` 初始化 `CheckpointHook`
- 可配置 `max_keep_ckpts` 控制保留数量，`save_optimizer` 决定是否存优化器 state dict。

### 日志钩子（原文）
- mmcv 现支持 `WandbLoggerHook`、`MlflowLoggerHook`、`TensorboardLoggerHook`，由 `log_config` 包装并设置 interval。

> 注：原文未给出任何具体的性能指标（mIoU、fps、收敛 epoch 数等），**性能数据"原文未涉及"**。

---

## 【表格解读】

**原文无表格**（整篇教程以代码片段和文字说明为主，未呈现参数表或性能对比表）。

---

## 【公式解读】

**原文无公式**（文档未出现 LaTeX 数学公式或伪代码形式的算法表达式，仅有 Python 配置字典片段，不构成数学/算法公式）。

---

## 【关联】

本文处于 "Tutorial 6" 位置，属于 mmseg 教程系列的运行时定制章节。它与以下 mmcv/mmseg 模块存在明确上下游或并列关系：

| 上游依赖 / 协作模块 | 关系 | 原文链接/路径 |
|---|---|---|
| `torch.optim`（PyTorch 官方） | 优化器 API 来源 | https://pytorch.org/docs/stable/optim.html?highlight=optim#module-torch.optim |
| `mmcv/runner/optimizer/default_constructor.py` | 默认优化器构造器模板 | https://github.com/open-mmlab/mmcv/blob/9ecd6b0d5ff9d2172c49a182eaa669e9f27bb8e7/mmcv/runner/optimizer/default_constructor.py#L11 |
| `mmcv/runner/hooks/lr_updater.py` (PolyLrUpdaterHook) | 默认 LR 调度器 | https://github.com/open-mmlab/mmcv/blob/826d3a7b68596c824fa1e2cb89b6ac274f52179c/mmcv/runner/hooks/lr_updater.py#L196 |
| `mmcv/runner/hooks/lr_updater.py` (CyclicLrUpdater) | Cyclic LR 调度器 | https://github.com/open-mmlab/mmcv/blob/f48241a65aebfe07db122e9db320c31b685dc674/mmcv/runner/hooks/lr_updater.py#L327 |
| `mmcv/runner/hooks/momentum_updater.py` (CyclicMomentumUpdater) | Cyclic 动量调度器 | https://github.com/open-mmlab/mmcv/blob/f48241a65aebfe07db122e9db320c31b685dc674/mmcv/runner/hooks/momentum_updater.py#L130 |
| `mmcv/runner/hooks/checkpoint.py` (CheckpointHook) | Checkpoint 钩子 | https://github.com/open-mmlab/mmcv/blob/9ecd6b0d5ff9d2172c49a182eaa669e9f27bb8e7/mmcv/runner/hooks/checkpoint.py#L9 |
| mmcv `WandbLoggerHook` / `MlflowLoggerHook` / `TensorboardLoggerHook` | 日志钩子 | （由 `log_config` 包装，原文未给具体文件链接） |
| `EvalHook` | 评估钩子，挂在 `after_train_epoch` | （原文以文字形式提及） |
| `mmseg/core/optimizer/__init__.py` | 自定义优化器注册入口 | （原文以代码说明） |
| `mmseg/utils.py` 中 `get_root_logger` | 日志工具 | （在 "Customize optimizer constructor" 代码片段中 import） |

文档内部三类配置呈互补关系：`optimizer_config`（优化器级行为）、`lr_config` + `momentum_config`（调度级行为）、`checkpoint_config` + `log_config` + `evaluation`（运行时 IO 与监控），共同由 MMCV Runner 串接调度。

---

## 【使用方法】

以下均**直接来自原文**的配置/命令：

### 1. 切换 PyTorch 原生优化器
```python
optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
```

### 2. 注册并使用自研优化器（关键三步）
- 创建 `mmseg/core/optimizer/my_optimizer.py`，类继承 `torch.optim.Optimizer`，装饰 `@OPTIMIZERS.register_module()`，构造参数 `a, b, c`。
- 在 `mmseg/core/optimizer/__init__.py` 添加 `from .my_optimizer import MyOptimizer`；**或**在配置中写 `custom_imports = dict(imports=['mmseg.core.optimizer.my_optimizer'], allow_failed_imports=False)`。
- 配置中改写为：
  ```python
  optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
  ```

### 3. 自定义优化器构造器
- 在 `mmcv.runner.optimizer` 中导入 `OPTIMIZER_BUILDERS, OPTIMIZERS`，装饰 `@OPTIMIZER_BUILDERS.register_module()`，实现 `__init__(self, optimizer_cfg, paramwise_cfg=None)` 与 `__call__(self, model) -> my_optimizer`。

### 4. 梯度裁剪
```python
optimizer_config = dict(
    _delete_=True, grad_clip=dict(max_norm=35, norm_type=2))
```

### 5. Cyclic LR + Momentum（3D 检测示例）
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

### 6. 训练调度切换
- Step：`lr_config = dict(policy='step', step=[9, 10])`
- CosineAnnealing + warmup：
  ```python
  lr_config = dict(
      policy='CosineAnnealing',
      warmup='linear',
      warmup_iters=1000,
      warmup_ratio=1.0 / 10,
      min_lr_ratio=1e-5)
  ```

### 7. 工作流配置
```python
workflow = [('train', 1)]              # 默认
workflow = [('train', 1), ('val', 1)]  # 加入验证 epoch
```

### 8. 自定义钩子
```python
custom_hooks = [
    dict(type='MyHook', a=a_value, b=b_value, priority='NORMAL')
]
```

### 9. Checkpoint 配置
```python
checkpoint_config = dict(interval=1)
```

> 备注：原文在 `Log config` 一节于 `The detail usages ca` 处截断，未列完毕；本文档基于原文如实收录，不做臆补。文中其它命令行（如训练启动命令 `python tools/train.py ...`）**"原文未涉及"**。
