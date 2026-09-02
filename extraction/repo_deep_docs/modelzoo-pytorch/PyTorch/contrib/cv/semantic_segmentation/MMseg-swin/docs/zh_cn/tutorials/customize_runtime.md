# 教程 6: 自定义运行设定

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/zh_cn/tutorials/customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/zh_cn/tutorials/customize_runtime.md

# 一体化深度解读:MMseg-swin 教程 6 — 自定义运行设定

---

## 【定位】

本文档是 MMseg-swin (基于 MMSegmentation 框架的 Swin Transformer 语义分割实现) 的"教程 6",系统性地讲解如何通过修改配置文件或新增代码,在**优化器、优化构造器、学习率/动量计划表、工作流、钩子 (hooks)、日志/检查点/评估配置**这六大维度自定义训练运行时行为。它不解决模型结构问题,而是解决"如何把训练跑得更稳、更快、更可控"的工程问题。

---

## 【技术要点】

1. **PyTorch 内置优化器的配置化启用**:通过修改配置文件 `optimizer` 字段即可切换任何 PyTorch 内置优化器;以 ADAM 为例,示例参数为 `type='Adam', lr=0.0003, weight_decay=0.0001`;默认 SGD 配置为 `type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001`。
2. **自定义优化器的三步接入流程**:在 `mmseg/core/optimizer/` 下新建 `my_optimizer.py` 定义继承自 `torch.optim.Optimizer` 的 `MyOptimizer`(参数 `a,b,c`),用 `@OPTIMIZERS.register_module()` 装饰,然后通过修改 `mmseg/core/optimizer/__init__.py` 导入 **或** 在配置中使用 `custom_imports = dict(imports=['mmseg.core.optimizer.my_optimizer'], allow_failed_imports=False)` 让注册表自动发现,最后在 `optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)` 中启用。
3. **优化器构造器 (optimizer constructor) 用于细粒度参数分组**:通过实现继承自 `object` 的 `MyOptimizerConstructor`(用 `@OPTIMIZER_BUILDERS.register_module()` 注册,实现 `__init__(optimizer_cfg, paramwise_cfg=None)` 与 `__call__(model)`),可以在构造阶段对 BatchNorm 等层做差异化 weight decay;其默认实现位于 mmcv `default_constructor.py`。
4. **额外训练稳定/加速设置**:
   - **梯度截断**:`optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))`,继承基础配置时需用 `_delete_=True` 重写。
   - **动量计划表 (Cyclic momentum)**:`momentum_config = dict(policy='cyclic', target_ratio=(0.85 / 0.95, 1), cyclic_times=1, step_ratio_up=0.4)`,常与 `lr_config = dict(policy='cyclic', target_ratio=(10, 1e-4), cyclic_times=1, step_ratio_up=0.4)` 联用。
5. **训练计划表 (LR scheduler)**:默认按 40k/80k 迭代使用 mmcv 的 `PolyLrUpdaterHook`;另支持 `Step`(如 `policy='step', step=[9, 10]`)与 `CosineAnnealing`(`warmup='linear', warmup_iters=1000, warmup_ratio=1.0/10, min_lr_ratio=1e-5`)。
6. **工作流与钩子**:工作流定义形如 `workflow = [('train', 1)]`(默认)或 `[('train', 1), ('val', 1)]`(交替);自定义钩子通过 `custom_hooks = [dict(type='MyHook', a=a_value, b=b_value, priority='NORMAL')]` 注册,而 `log_config`(interval=50, 默认含 `TensorboardLoggerHook`)、`checkpoint_config`(interval=1, 由 mmcv `CheckpointHook` 初始化)、`evaluation`(interval=1, metric='mIoU')属于运行时内置钩子,不通过 `custom_hooks` 注册;**只有 logger hook 优先级为 `VERY_LOW`,其余均为 `NORMAL`**。

---

## 【关键机制与数据】

- **优化器切换原理**:MMSegmentation 通过注册表机制 (`OPTIMIZERS`) + mmcv 的 `build_from_cfg` 把 `optimizer = dict(type=...)` 配置项动态映射为对应类的实例。原文:"我们已经支持 PyTorch 自带的所有优化器,唯一需要修改的地方是在配置文件里的 `optimizer` 域里面"。
- **自定义优化器注册路径**:文档明确指出"`mmseg.core.optimizer.my_optimizer.MyOptimizer` **不能** 被直接导入",而只能导入包 `mmseg.core.optimizer.my_optimizer`,原因是要触发包级 `__init__.py` 中的注册逻辑。
- **工作流与 EvalHook 的耦合关系**(原文):"`EvalHook` 被 `after_train_epoch` 调用,而且验证的工作流仅仅影响通过调用 `after_val_epoch` 的钩子",因此 `[('train', 1), ('val', 1)]` 与 `[('train', 1)]` 相比,**区别仅在于 runner 将在每次训练 epoch 结束后计算在验证集上的损失**;`EvalHook` 自身行为不变;`total_epochs` 仅控制训练 epoch 数,不影响验证工作流。
- **构造器优先级**:文档通过 `"在这些钩子里,只有 logger hook 有 `VERY_LOW` 优先级,其他的优先级都是 `NORMAL`"` 明确内置运行时钩子优先级分布。
- **默认训练迭代步数**(原文):"我们根据默认的训练迭代步数 40k/80k 来设置学习率"。
- **性能/基准数据**:原文未提供具体数值性能或基准对比。

---

## 【表格解读】

**原文无表格。**

文档全程使用 Python 代码片段作为配置示例,而非参数表/对比表。代码片段本身已在【技术要点】中按字段逐条还原,这里不再做表格化转写。

---

## 【公式解读】

**原文无公式。**

文档中涉及"动量计划表 (Cyclic)"、`target_ratio`、warmup_ratio 等概念是工程参数,而非数学公式;无 LaTeX/伪代码公式表达,故按要求标注"原文无公式"。

---

## 【关联】

本文是 MMSegmentation "教程"系列的第 6 篇,与其他教程/外部模块存在如下关联(原文给出的):

- **与 mmcv 的深度依赖**:几乎所有可扩展点都来自 mmcv 的注册表与 runner 机制:
  - `OPTIMIZER_BUILDERS`、`OPTIMIZERS`、`build_from_cfg` 来自 `mmcv.runner.optimizer` 与 `mmcv.utils`。
  - 学习率计划表由 mmcv 的 `mmcv/runner/hooks/lr_updater.py` 提供(默认 `PolyLrUpdaterHook` 在该文件 L196,`CyclicLrUpdaterHook` 在 L327)。
  - 动量计划表由 `mmcv/runner/hooks/momentum_updater.py` 提供(`CyclicMomentumUpdater` 在 L130)。
  - 默认优化器构造器实现见 `mmcv/runner/optimizer/default_constructor.py` L11。
  - 检查点由 `mmcv/runner/hooks/checkpoint.py` L9 的 `CheckpointHook` 初始化。
  - 日志钩子 (含 `WandbLoggerHook`、`MlflowLoggerHook`、`TensorboardLoggerHook`) 见 mmcv `LoggerHook` 文档。
- **与 MMSegmentation 本体的关联**:评估钩子 (`EvalHook`) 由 `mmseg/core/evaluation/eval_hooks.py` L7 初始化;`evaluation` 配置中除 `interval` 外的参数透传给 `dataset.evaluate()`。
- **与配置文件的关联**:配置文档(`https://mmsegmentation.readthedocs.io/en/latest/config.html`)专门解释 `_delete_=True` 等字段语义,与本教程的"梯度截断继承"示例交叉引用。

> 备注:用户提供的"内部链接"清单为空 `(无)`,故本节无法引用本文档内部的锚点/兄弟教程链接;上文全部关联来自原文中以 URL 形式给出的外部源码/文档链接。

---

## 【使用方法】

原文给出了完整的、可直接复制的启用方式,汇总如下:

**① 切换内置优化器**:在配置文件中直接修改 `optimizer` 字段,例如:
```python
optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
# 或默认 SGD
optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)
# 或自定义优化器
optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
```

**② 启用梯度截断**:
```python
optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))
```

**③ 启用动量 + 学习率循环计划表 (cyclic)**:
```python
lr_config = dict(policy='cyclic', target_ratio=(10, 1e-4), cyclic_times=1, step_ratio_up=0.4)
momentum_config = dict(policy='cyclic', target_ratio=(0.85 / 0.95, 1), cyclic_times=1, step_ratio_up=0.4)
```

**④ 选择 LR scheduler**:
```python
# Step
lr_config = dict(policy='step', step=[9, 10])
# CosineAnnealing
lr_config = dict(policy='CosineAnnealing', warmup='linear', warmup_iters=1000, warmup_ratio=1.0/10, min_lr_ratio=1e-5)
```

**⑤ 调整工作流**:
```python
# 默认:仅训练
workflow = [('train', 1)]
# 交替训练/验证
[('train', 1), ('val', 1)]
```

**⑥ 注册自定义钩子**:
```python
custom_hooks = [dict(type='MyHook', a=a_value, b=b_value, priority='NORMAL')]
```

**⑦ 修改内置运行时钩子**:
```python
checkpoint_config = dict(interval=1)               # CheckpointHook
log_config = dict(interval=50, hooks=[dict(type='TextLoggerHook'), dict(type='TensorboardLoggerHook')])
evaluation = dict(interval=1, metric='mIoU')       # EvalHook
```

**⑧ 通过 `custom_imports` 拉入外部自定义模块**(原文):`custom_imports = dict(imports=['mmseg.core.optimizer.my_optimizer'], allow_failed_imports=False)`。

> 注:`CheckpointHook` 的更多参数(`max_keep_ckpts`、`save_optimizer` 等)以及 logger hooks 的详细用法,原文只给出链接指向,未在此文档中给出完整示例。
