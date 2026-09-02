# 教程 6: 自定义运行配置

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/zh_cn/tutorials/6_customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/zh_cn/tutorials/6_customize_runtime.md

# 教程 6：自定义运行配置 — 一体化深度解读

## 【定位】
本教程面向 MMPose 项目中的高级用户，系统性地说明如何在不修改框架主干代码的前提下，通过纯配置文件 + 极少量新模块的方式自定义**优化器、训练策略（学习率/动量）、工作流与钩子**这四大运行时核心维度，从而把 MMPose 适配到特定任务或研究需求中。

## 【技术要点】

1. **PyTorch 原生优化器配置化**：所有 PyTorch `torch.optim` 中的优化器可直接通过 `optimizer = dict(type=..., lr=..., ...)` 形式启用，参数键名直接映射到 PyTorch API（如 Adam 的 `betas / eps / amsgrad`）。
2. **自定义优化器三步流程**：在 `mmpose/core/optimizer/` 下新写继承 `Optimizer` 的类并用 `@OPTIMIZERS.register_module()` 装饰 → 通过修改 `__init__.py` 或在配置文件中写 `custom_imports` 完成注册 → 在配置中以 `type='MyOptimizer'` 调用。
3. **优化器构造器（参数分组）**：通过 `@OPTIMIZER_BUILDERS.register_module()` 注册 `MyOptimizerConstructor`，在 `__call__` 中按 `paramwise_cfg` 对 BN 层等做差异化学习率/权重衰减。
4. **梯度截断与动量调度**：用 `optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))` 稳定训练；用 `policy='cyclic'` 的 `lr_config` 与 `momentum_config` 联动加速收敛（原文给出了具体 3D 检测示例参数）。
5. **学习率策略**：默认阶梯式衰减（`StepLRHook`），另支持 `poly`（`policy='poly', power=0.9, min_lr=1e-4, by_epoch=False`）与 `CosineAnnealing`（含 `linear` warmup，`warmup_iters=1000`，`warmup_ratio=1.0/10`，`min_lr_ratio=1e-5`）。
6. **工作流与钩子体系**：工作流 `workflow=[('train',1), ('val',1)]` 控制阶段顺序与轮数；钩子通过继承 `mmcv.runner.Hook` 的六个生命周期方法（`before_run/after_run/before_epoch/after_epoch/before_iter/after_iter`）插入逻辑，用 `custom_hooks` 列表挂载，并通过 `priority='NORMAL'/'HIGHEST'` 控制顺序。

## 【关键机制与数据】

**优化器工作原理**：
- PyTorch 内置优化器在配置层被 `mmcv.runner.optimizer` 解析为 `OPTIMIZERS` 注册表中的实例，参数键值直接转发给底层 `torch.optim` 构造器。
- 自定义优化器必须先进入注册表才能被配置识别：`__init__.py` 隐式导入或 `custom_imports` 显式导入，二者底层均触发 `@OPTIMIZERS.register_module()` 的注册副作用。
- **原文数据**：示例 Adam 学习率 `lr=0.0003`，权重衰减 `weight_decay=0.0001`；完整 Adam 参数映射 `lr=0.001, betas=(0.9, 0.999), eps=1e-08, weight_decay=0, amsgrad=False`。

**梯度截断机制**（原文）：`optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))` —— `max_norm=35` 为梯度范数上限，`norm_type=2` 表示采用 L2 范数计算，由 `optimizer_config` 钩子在每次 `after_train_iter` 调用 `torch.nn.utils.clip_grad_norm_`。

**循环学习率/动量机制**（原文）：3D 检测示例同时启用 `CyclicLrUpdater` 与 `CyclicMomentumUpdater`：
- 学习率在 `(10, 1e-4)` 区间循环，`step_ratio_up=0.4` 决定上升阶段占比，`cyclic_times=1` 表示循环一次。
- 动量在 `(0.85/0.95, 1)` 区间反向循环（学习率升则动量降，动量升时学习率降），二者相位相反。

**工作流机制**：
- 默认 `workflow = [('train', 1)]` 每轮仅训练；扩展为 `[('train', 1), ('val', 1)]` 时，验证阶段不更新权重，**仅影响 `after_val_epoch` 钩子**，不影响 `after_train_epoch` 上的 `EpochEvalHook`。
- `total_epochs` 只控制训练轮数，与验证阶段次数无关。

**钩子优先级机制**：注册时默认 `NORMAL`，可设为 `HIGHEST`；默认运行钩子（`log_config / checkpoint_config / evaluation / lr_config / optimizer_config / momentum_config`）中仅日志钩子为 `VERY_LOW`，其余均为 `NORMAL`。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式（仅有配置字典形式的伪代码，已在"技术要点"中保留）。

## 【关联】

- **与 MMCV 的深度耦合**：本文所有自定义能力（优化器构造器、循环学习率/动量调度、CheckpointHook、LoggerHook、EvalHook）均来自 MMCV 的 `mmcv.runner` 子模块，文档多次指向 `mmcv/runner/optimizer/default_constructor.py`、`mmcv/runner/hooks/lr_updater.py`、`mmcv/runner/hooks/momentum_updater.py`、`mmcv/runner/hooks/checkpoint.py`。
- **与 MMPose 自身模块的耦合**：自定义扩展点统一约定在 `mmpose/core/optimizer/` 与 `mmpose/core/utils/` 目录，需通过 `__init__.py` 或 `custom_imports` 接入注册器；自定义钩子与 `EvalHook`（位于 `mmpose/core/evaluation/eval_hooks.py`）配合工作流共同决定验证时机。
- **与其他教程的衔接**：原文明确"前面的教程已经讲述了如何修改 `optimizer_config / momentum_config / lr_config`"，说明本教程处于系列第 6 篇，向前承接基础配置教程，向后通常接日志、可视化、部署等教程。
- **外部链接信息**（原文提供的参考入口）：
  - PyTorch 优化器 API：`https://pytorch.org/docs/stable/optim.html`
  - `CyclicLrUpdater`：`mmcv/runner/hooks/lr_updater.py#L327`
  - `CyclicMomentumUpdater`：`mmcv/runner/hooks/momentum_updater.py#L130`
  - `StepLRHook`：`mmcv/runner/hooks/lr_updater.py#L153`
  - 默认优化器构造器：`mmcv/runner/optimizer/default_constructor.py#L11`
  - `CheckpointHook`：`mmcv/runner/hooks/checkpoint.py#L9`
  - `EvalHook`：`mmpose/core/evaluation/eval_hooks.py#L11`
  - `CheckpointHook` 参数文档：`mmcv.readthedocs.io/.../mmcv.runner.CheckpointHook`
  - `LoggerHook` 文档：`mmcv.readthedocs.io/.../mmcv.runner.LoggerHook`

## 【使用方法】

**启用方式/配置项/命令汇总**（均直接摘自原文）：

1. **PyTorch 优化器**：
   ```python
   optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
   optimizer = dict(type='Adam', lr=0.001, betas=(0.9, 0.999), eps=1e-08, weight_decay=0, amsgrad=False)
   ```

2. **自定义优化器（注册）**：
   - 在 `mmpose/core/optimizer/__init__.py` 中 `from .my_optimizer import MyOptimizer`
   - 或配置中 `custom_imports = dict(imports=['mmpose.core.optimizers.my_optimizer'], allow_failed_imports=False)`

3. **自定义优化器（调用）**：
   ```python
   optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
   ```

4. **梯度截断**：
   ```python
   optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))
   ```

5. **循环学习率 + 动量**：
   ```python
   lr_config = dict(policy='cyclic', target_ratio=(10, 1e-4), cyclic_times=1, step_ratio_up=0.4)
   momentum_config = dict(policy='cyclic', target_ratio=(0.85 / 0.95, 1), cyclic_times=1, step_ratio_up=0.4)
   ```

6. **多项式学习率策略**：
   ```python
   lr_config = dict(policy='poly', power=0.9, min_lr=1e-4, by_epoch=False)
   ```

7. **余弦退火 + 线性 warmup**：
   ```python
   lr_config = dict(
       policy='CosineAnnealing',
       warmup='linear',
       warmup_iters=1000,
       warmup_ratio=1.0 / 10,
       min_lr_ratio=1e-5)
   ```

8. **工作流**：
   ```python
   workflow = [('train', 1)]
   workflow = [('train', 1), ('val', 1)]
   ```

9. **自定义钩子（调用）**：
   ```python
   custom_hooks = [dict(type='MyHook', a=a_value, b=b_value)]
   custom_hooks = [dict(type='MyHook', a=a_value, b=b_value, priority='NORMAL')]
   ```

10. **MMCV 内置钩子**：
    ```python
    mmcv_hooks = [dict(type='MMCVHook', a=a_value, b=b_value, priority='NORMAL')]
    ```

11. **模型权重文件配置**：
    ```python
    checkpoint_config = dict(interval=1)
    ```
    （可通过 `max_keep_ckpts` 限制保存数量，通过 `save_optimizer` 决定是否保存优化器状态。）

12. **日志配置**：
    ```python
    log_config = dict(
        interval=50,
        hooks=[
            dict(type='TextLoggerHook'),
            dict(type='TensorboardLoggerHook')
        ])
    ```
    （支持的日志钩子：`WandbLoggerHook`、`MlflowLoggerHook`、`TensorboardLoggerHook`。）

13. **测试配置**：
    ```python
    evaluation = dict(interval=1, metric='mAP')
    ```
    （除 `interval` 外其他参数透传给 `dataset.evaluate()`。）
