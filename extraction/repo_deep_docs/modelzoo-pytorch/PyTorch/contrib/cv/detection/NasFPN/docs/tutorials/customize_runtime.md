# Tutorial 5: Customize Runtime Settings

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/NasFPN/docs/tutorials/customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/NasFPN/docs/tutorials/customize_runtime.md

# 代码仓「modelzoo-pytorch」文档深度解读

## 【定位】

本篇文档系统性地讲解在 NasFPN (基于 MMDetection 框架) 中如何定制训练运行时的各类参数——涵盖优化器、优化器构造器、训练调度 (learning rate schedule)、工作流 (workflow) 以及训练钩子 (hooks) 五大维度,是用户在不改源码主体逻辑的前提下,通过配置文件与少量代码扩展来个性化训练流程的官方指引。

---

## 【技术要点】

1. **优化器切换机制**: 直接修改 config 文件的 `optimizer` 字段中的 `type` 即可使用任意 PyTorch 内置优化器;切换到 Adam 时参考设置为 `lr=0.0003`, `weight_decay=0.0001`。
2. **自定义优化器三步走**: ①在 `mmdet/core/optimizer/my_optimizer.py` 中继承 `torch.optim.Optimizer` 并用 `@OPTIMIZERS.register_module()` 装饰;②通过修改 `__init__.py` 或使用 `custom_imports` 让注册器发现该模块;③在 config 中用 `type='MyOptimizer'` 替换原 type。
3. **优化器构造器 (Optimizer Constructor)**: 针对 BatchNorm 等特定层做差异化设置(如 weight decay 分组),通过 `@OPTIMIZER_BUILDERS.register_module()` 注册一个返回构造后 optimizer 的可调用类,模板见 mmcv 的 `default_constructor.py`。
4. **梯度裁剪与动量调度**: 通过 `optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))` 实现梯度裁剪;动量调度通过 `cyclic` policy,`target_ratio=(0.85 / 0.95, 1)` 与 LR 调度配合使用。
5. **学习率调度**: 除默认 `StepLR` (1x schedule) 外,支持 `poly` (`power=0.9, min_lr=1e-4, by_epoch=False`) 和 `CosineAnnealing` (`warmup='linear', warmup_iters=1000, warmup_ratio=1.0/10, min_lr_ratio=1e-5`) 等。
6. **Workflow 与自定义 Hook**: workflow 控制 (phase, epochs) 执行顺序,默认 `[('train', 1)]`;自定义 Hook 自 MMDetection v2.3.0 (PR #3395) 起支持通过 config 直接挂载,实现类需实现 `before_run/after_run/before_epoch/after_epoch/before_iter/after_iter` 六生命周期方法。

---

## 【关键机制与数据】

### 数据流与控制流 (原文):

**优化器注册与发现流程**:
- 自定义优化器文件位于 `mmdet/core/optimizer/my_optimizer.py`,通过 `@OPTIMIZERS.register_module()` 装饰器将类注入 `OPTIMIZERS` 注册表;
- 两种导入方式:
  - 静态导入: 在 `mmdet/core/optimizer/__init__.py` 中加入 `from .my_optimizer import MyOptimizer`;
  - 动态导入: 在 config 中设置 `custom_imports = dict(imports=['mmdet.core.optimizer.my_optimizer'], allow_failed_imports=False)`。
- **关键限制**: 仅需导入包含类的包 (即 `mmdet.core.optimizer.my_optimizer`),**不能**直接导入 `mmdet.core.optimizer.my_optimizer.MyOptimizer`,否则注册失败。

**Hook 生命周期**:
- 文档原文列出六个可重写方法: `before_run`, `after_run`, `before_epoch`, `after_epoch`, `before_iter`, `after_iter`,均接受 `runner` 作为参数。
- 自定义 Hook 支持引入自 MMDetection v2.3.0 (PR #3395),在该版本前需手动改源码。

**Workflow 与 EvalHook 关系** (原文三条 Note):
1. val epoch 期间模型参数**不会**被更新;
2. `total_epochs` 仅控制训练 epoch 数,**不影响**验证 workflow;
3. workflow `[('train', 1), ('val', 1)]` 与 `[('train', 1)]` **不会**改变 `EvalHook` 的行为——因为 `EvalHook` 由 `after_train_epoch` 触发,而验证 workflow 仅影响 `after_val_epoch` 触发的 hooks。两者**唯一区别**在于 runner 是否在每个训练 epoch 后在验证集上计算 loss。

**Momentum schedule 与 LR schedule 协同** (3D 检测用例原文):
- LR: `policy='cyclic', target_ratio=(10, 1e-4), cyclic_times=1, step_ratio_up=0.4`;
- Momentum: `policy='cyclic', target_ratio=(0.85 / 0.95, 1), cyclic_times=1, step_ratio_up=0.4`。
- 两个 scheduler 共用相同的 `cyclic_times` 与 `step_ratio_up` 节奏。

---

## 【表格解读】

**原文无表格**。本教程以代码片段 (Python dict 形式) 给出所有配置示例,未使用任何结构化表格。

---

## 【公式解读】

**原文无公式**。文档仅包含若干算法名称 (Poly, CosineAnnealing, Cyclic) 而未列出其闭式表达式;对应的数值参数 (如 `power=0.9`, `min_lr=1e-4`) 均以 Python 字典字面量形式给出,而非数学公式。

---

## 【关联】

本教程位于 NasFPN 的 docs/tutorials 目录下,其内容**主要依赖上游 mmcv 框架**,具体关联如下:

| 关联对象 | 关联性质 | 出处位置(原文链接) |
|---|---|---|
| `torch.optim` (PyTorch 官方) | 提供 `Optimizer` 基类与所有内置优化器 | https://pytorch.org/docs/stable/optim.html |
| `mmcv.runner.optimizer` | 提供 `OPTIMIZER_BUILDERS`、`OPTIMIZERS` 注册器与默认构造器模板 `default_constructor.py` | https://github.com/open-mmlab/mmcv/blob/.../default_constructor.py |
| `mmcv.runner.hooks.lr_updater` | 提供 `StepLRHook`、CosineAnnealing、Poly、Cyclic 等 LR 调度器 | https://github.com/open-mmlab/mmcv/blob/.../lr_updater.py |
| `mmcv.runner.hooks.momentum_updater` | 提供 `CyclicMomentumUpdater`,与 LR 调度器配对 | https://github.com/open-mmlab/mmcv/blob/.../momentum_updater.py |
| `mmcv.utils.build_from_cfg` | 优化器构造器内部用于从 cfg 构建 optimizer 的工具 | 文档正文引用 |
| `mmcv.runner.HOOKS` / `Hook` | 自定义 Hook 的基类与注册器 | 文档正文引用 |
| MMDetection 主仓 | `mmdet/core/optimizer/`、`mmdet/core/utils/` 等目录约定 | 文档正文引用 |
| mmdetection 文档 | 解释 `_delete_=True` 等 config 继承语义 | https://mmdetection.readthedocs.io/en/latest/config.html |

**上下游关系**:
- **上游依赖**: mmcv 提供 runner/hook/optimizer 注册底层,PyTorch 提供优化器基类;
- **下游应用**: 本教程所教内容为 NasFPN 训练脚本提供运行时灵活度,但 NasFPN 自身并未在该教程中额外贡献新机制;
- **横向关联**: 与同目录下其它教程 (Tutorial 1-4, 例如 customize_dataset, customize_models 等) 共同构成完整的"无侵入定制"知识体系。

---

## 【使用方法】

### 1. 切换 PyTorch 内置优化器 (原文有)
```python
optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
```
直接修改 config 中的 `optimizer` 字段即可,无需改动代码。

### 2. 注册自定义优化器 (原文有)
- 文件: `mmdet/core/optimizer/my_optimizer.py`
- 类需继承 `torch.optim.Optimizer`,使用 `@OPTIMIZERS.register_module()` 装饰;
- 二选一方式让注册器发现模块:
  - 在 `mmdet/core/optimizer/__init__.py` 加 `from .my_optimizer import MyOptimizer`;
  - 或在 config 中设置 `custom_imports = dict(imports=['mmdet.core.optimizer.my_optimizer'], allow_failed_imports=False)`;
- 最后在 config 中写 `optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)`。

### 3. 自定义优化器构造器 (原文有)
- 类需用 `@OPTIMIZER_BUILDERS.register_module()` 装饰;
- 实现 `__init__(self, optimizer_cfg, paramwise_cfg=None)` 与 `__call__(self, model)`,后者返回构造好的 optimizer;
- 模板: https://github.com/open-mmlab/mmcv/blob/.../default_constructor.py

### 4. 启用梯度裁剪 (原文有)
```python
optimizer_config = dict(
    _delete_=True, grad_clip=dict(max_norm=35, norm_type=2))
```
若 config 继承自已有 `optimizer_config` 的基础配置,需用 `_delete_=True` 覆盖父配置中的相应键。

### 5. 启用动量调度 (原文有)
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

### 6. 切换学习率调度策略 (原文有)
- Poly: `lr_config = dict(policy='poly', power=0.9, min_lr=1e-4, by_epoch=False)`
- CosineAnnealing (含 warmup):
  ```python
  lr_config = dict(
      policy='CosineAnnealing',
      warmup='linear',
      warmup_iters=1000,
      warmup_ratio=1.0 / 10,
      min_lr_ratio=1e-5)
  ```

### 7. 自定义训练 workflow (原文有)
```python
# 默认
workflow = [('train', 1)]
# 训练 + 验证交替
workflow = [('train', 1), ('val', 1)]
```

### 8. 注册自定义 Hook (原文有,文档截断)
- 类继承 `mmcv.runner.Hook`,用 `@HOOKS.register_module()` 装饰;
- 实现六生命周期方法中的任意子集 (`before_run`, `after_run`, `before_epoch`, `after_epoch`, `before_iter`, `after_iter`);
- 注册方式 (文档未完整列出): 假设文件在 `mmdet/core/utils/my_hook.py`,通过修改 `mmdet/core/utils/__init__.py` 加入 `from .my_hook import MyHook` (第二行被截断,使用 `custom_imports` 的方法未在原文给出)。

> **文档完整性说明**: 原文档在 "Register the new hook" 章节末尾被截断,Hook 注册的完整步骤、配置项以及 `runtime` 字段在 config 中如何挂载自定义 Hook 的最终示例 (例如 `custom_hooks = [...]` 写法) 在原文不可见,如需精确使用方式建议参考同系列教程或其它教程章节的对应内容。
