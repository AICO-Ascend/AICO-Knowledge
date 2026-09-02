# 教程 6: 自定义运行设定

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs_zh-CN/tutorials/customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs_zh-CN/tutorials/customize_runtime.md

# 「教程 6: 自定义运行设定」一体化深度解读

## 【定位】

这篇文档面向使用 mmsegmentation 框架（DeepLabV3_for_Pytorch 同源体系）的开发者，系统性地说明如何在不改动框架源码的前提下，通过修改配置文件或新增少量模块文件来定制训练过程的优化器、学习率计划、运行工作流以及运行期钩子，从而实现对训练运行时的全维度扩展与微调。

## 【技术要点】

1. **PyTorch 内置优化器一键替换**：通过修改配置文件 `optimizer` 字段的 `type` 即可切换 PyTorch 自带的所有优化器，例如改用 ADAM：`optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)`，其余参数通过 `lr` 字段控制。
2. **自定义优化器三级接入流程**：① 在 `mmseg/core/optimizer/my_optimizer.py` 中继承 `torch.optim.Optimizer` 并用 `@OPTIMIZERS.register_module()` 装饰；② 通过 `__init__.py` 导入或 `custom_imports` 字段把模块加入注册表；③ 在配置文件 `optimizer` 字段中以 `type='MyOptimizer', a=a_value, b=b_value, c=c_value` 形式调用。
3. **自定义优化器构造器（Optimizer Constructor）**：通过 `@OPTIMIZER_BUILDERS.register_module()` 注册一个继承 `object` 的类（实现 `__init__(optimizer_cfg, paramwise_cfg=None)` 与 `__call__(model)`），可在构造时为不同参数组（如 BatchNorm 层）设置差异化的 weight decay。
4. **训练稳定性/加速增强选项**：使用梯度截断 `optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))`；使用动量计划表 `momentum_config = dict(policy='cyclic', target_ratio=(0.85 / 0.95, 1), cyclic_times=1, step_ratio_up=0.4)` 与 `CyclicLrUpdater` 配合。
5. **学习率计划表多策略支持**：默认采用 `PolyLrUpdaterHook`（基于 40k/80k 迭代步），另外支持 `step`（`lr_config = dict(policy='step', step=[9, 10])`）和 `CosineAnnealing`（带 `warmup='linear'`, `warmup_iters=1000`, `warmup_ratio=1.0/10`, `min_lr_ratio=1e-5`）。
6. **运行钩子双层管理**：`custom_hooks` 列表用于挂载用户自定义的 MMCV 钩子（带 `priority='NORMAL'`），而 6 个框架内置运行时钩子（`log_config` 优先级为 `VERY_LOW`，其余 5 个为 `NORMAL`）则通过同名顶级配置字段直接修改；工作流 `workflow` 控制 (phase, epochs) 顺序，默认 `[('train', 1)]`，扩展为 `[('train', 1), ('val', 1)]` 后每轮训练后会自动跑一次验证（注意 `EvalHook` 由 `after_train_epoch` 触发，验证阶段不更新模型参数，`total_epochs` 仅控制训练 epoch 数）。

## 【关键机制与数据】

- **优化器注册机制**：使用 mmsegmentation 提供的 `@OPTIMIZERS.register_module()` 装饰器；注册项导入可通过修改 `mmseg/core/optimizer/__init__.py` 或在配置文件中使用 `custom_imports = dict(imports=['mmseg.core.optimizer.my_optimizer'], allow_failed_imports=False)`；仅需导入包路径而非具体类（如原文明确指出：`mmseg.core.optimizer.my_optimizer.MyOptimizer` **不能** 被直接导入）。
- **优化器构造器默认实现引用**：原文指出默认实现位于 `mmcv/runner/optimizer/default_constructor.py` 的 L11，可作为新构造器模板。
- **学习率计划默认值**：原文："我们根据默认的训练迭代步数 40k/80k 来设置学习率"，对应 `PolyLrUpdaterHook` 实现位于 `mmcv/runner/hooks/lr_updater.py` L196。
- **动量计划表的协同参数**：`target_ratio=(0.85 / 0.95, 1)`（动量比值的上下界）与 `target_ratio=(10, 1e-4)`（学习率比值的上下界）一一对应；`cyclic_times=1, step_ratio_up=0.4` 在两侧完全一致。
- **工作流差异机制**：原文明确指出 `[('train', 1), ('val', 1)]` 与 `[('train', 1)]` 不会改变 `EvalHook` 的行为——因为 `EvalHook` 由 `after_train_epoch` 触发；二者的实际差异在于"runner 将在每次训练 epoch 结束后计算在验证集上的损失"。
- **优先级分层（原文）**：日志钩子 `log_config` 的优先级为 `VERY_LOW`，其他内置运行时钩子（`checkpoint_config`, `evaluation`, `lr_config`, `optimizer_config`, `momentum_config`）的优先级均为 `NORMAL`。
- **检查点配置可选参数**：`max_keep_ckpts`（仅保存少量检查点）、`save_optimizer`（决定是否保存优化器状态字典），并可通过 `interval=1` 控制保存间隔。
- **评估配置参数传递**：`evaluation` 配置除 `interval` 键外的其他参数（如 `metric='mIoU'`）将被传递给 `dataset.evaluate()`。

## 【表格解读】

**原文无表格**

（文档全部内容以代码片段、配置字典与散文段落形式呈现，没有任何 markdown 表格或 CSV 类结构化数据。）

## 【公式解读】

**原文无公式**

（文档未给出 LaTeX 公式或伪代码形式数学表达，仅有若干 PyTorch 配置字典与 Python 类骨架代码，例如 `optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))` 等属于参数配置而非数学公式。）

## 【关联】

本文档作为「教程 6」，处于 mmsegmentation 教程系列的运行时定制环节，向上承接训练配置基础，向下衔接模型部署与推理（虽未直接论述）。文档中显式引用了以下外部模块/特性，构成上下游依赖关系：

- **PyTorch 优化器体系**：依赖 `torch.optim.Optimizer` 基类与 PyTorch 官方优化器 API 文档 `https://pytorch.org/docs/stable/optim.html`。
- **MMCV 运行器（Runner）**：
  - `mmcv/runner/optimizer/default_constructor.py`（L11）—— 默认优化器构造器模板；
  - `mmcv/runner/optimizer/__init__.py`—— `OPTIMIZER_BUILDERS` 与 `OPTIMIZERS` 注册表来源；
  - `mmcv/runner/hooks/lr_updater.py`（L196 `PolyLrUpdaterHook`；L327 `CyclicLrUpdater`）—— 学习率调度器；
  - `mmcv/runner/hooks/momentum_updater.py`（L130 `CyclicMomentumUpdater`）—— 动量调度器；
  - `mmcv/runner/hooks/checkpoint.py`（L9 `CheckpointHook`）—— 检查点保存；
  - `mmcv/runner/hooks/` 中的 `LoggerHook`（如 `WandbLoggerHook`、`MlflowLoggerHook`、`TensorboardLoggerHook`）—— 多后端日志记录。
- **mmsegmentation 评估模块**：`mmseg/core/evaluation/eval_hooks.py`（L7 `EvalHook`）—— 与 `after_train_epoch`/`after_val_epoch` 钩子回调关联，是工作流差异化的关键。
- **mmsegmentation 注册表与工具**：`mmseg/core/optimizer/` 目录（含 `registry.py` 与 `__init__.py`）、`mmseg/utils.py` 的 `get_root_logger`、`mmcv.utils.build_from_cfg`。
- **配置继承机制**：通过 `_delete_=True` 覆盖从基础配置继承下来的 `optimizer_config`，与 mmsegmentation 配置继承体系深度耦合（链接指向 `https://mmsegmentation.readthedocs.io/en/latest/config.html`）。

文档内部链接：原文未提供内部链接（仅外链），所以无本仓库内的页内跳转。

## 【使用方法】

> 以下配置项均为原文给出的可直接复用的配置字典片段，组合使用即可启用对应功能。

**① 切换内置优化器（以 ADAM 为例）：**
```python
optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
```

**② 通过 `custom_imports` 加载自定义优化器：**
```python
custom_imports = dict(imports=['mmseg.core.optimizer.my_optimizer'], allow_failed_imports=False)
optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
```

**③ 启用梯度截断（从基础配置继承时需 `_delete_=True`）：**
```python
optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))
```

**④ 启用动量计划表（与循环学习率配合，常用于 3D 检测加速收敛）：**
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

**⑤ 切换学习率计划表：**
```python
# 步衰减
lr_config = dict(policy='step', step=[9, 10])
# 余弦退火 + 线性 warmup
lr_config = dict(
    policy='CosineAnnealing',
    warmup='linear',
    warmup_iters=1000,
    warmup_ratio=1.0 / 10,
    min_lr_ratio=1e-5)
```

**⑥ 配置工作流（交替训练与验证）：**
```python
workflow = [('train', 1), ('val', 1)]   # 默认仅训练时为 [('train', 1)]
```

**⑦ 注册自定义钩子：**
```python
custom_hooks = [
    dict(type='MyHook', a=a_value, b=b_value, priority='NORMAL')
]
```

**⑧ 修改默认运行时钩子配置：**
```python
checkpoint_config = dict(interval=1)   # 可选 max_keep_ckpts、save_optimizer
log_config = dict(
    interval=50,
    hooks=[
        dict(type='TextLoggerHook'),
        dict(type='TensorboardLoggerHook')
    ])
evaluation = dict(interval=1, metric='mIoU')   # metric 透传给 dataset.evaluate()
```

**命令行**：原文未提供具体的 shell 命令，所有启用方式均通过修改 Python 配置文件完成。
