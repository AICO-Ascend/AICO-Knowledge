# Tutorial 5: Customize Runtime Settings

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/tutorials/customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/tutorials/customize_runtime.md

【定位】
这篇文档是 MMDetection 的"教程 5:自定义运行时设置",系统说明如何在不修改核心源码的前提下,通过配置文件灵活定制训练过程的**优化器**、**学习率/动量调度**、**训练工作流 (workflow)** 以及**训练钩子 (hooks)** 四大运行时维度。

【技术要点】
1. **PyTorch 内置优化器直接使用**:仅需在 config 中修改 `optimizer` 字段,如切到 `Adam`:`optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)`。
2. **自定义优化器注册流程**:在 `mmdet/core/optimizer/` 下新建类(继承 `torch.optim.Optimizer`),用 `@OPTIMIZERS.register_module()` 装饰,然后通过 `__init__.py` 导入或 config 中 `custom_imports` 导入完成注册。
3. **优化器构造器 (Optimizer Constructor)**:用于参数级别的细粒度调参(如 BatchNorm 的 weight_decay),通过 `@OPTIMIZER_BUILDERS.register_module()` 注册并实现 `__call__(model)`。
4. **梯度裁剪稳定训练**:`optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))`,继承基础 config 时需 `_delete_=True` 覆盖。
5. **动量调度配合学习率调度**(3D 检测示例):cyclic 策略下 lr `target_ratio=(10, 1e-4)`,momentum `target_ratio=(0.85 / 0.95, 1)`,两者 `cyclic_times=1, step_ratio_up=0.4`。
6. **学习率调度**:默认 `StepLRHook` 的 1x step 策略;另外支持 Poly(`policy='poly', power=0.9, min_lr=1e-4, by_epoch=False`)与 CosineAnnealing(配 `warmup='linear', warmup_iters=1000, warmup_ratio=1.0/10, min_lr_ratio=1e-5`)。
7. **工作流 (workflow)**:默认 `workflow = [('train', 1)]`;可设为 `[('train', 1), ('val', 1)]` 交替训/验证(验证阶段不更新参数)。
8. **自定义 Hook**:自 v2.3.0 (#3395) 起支持,继承 `Hook` 并实现 `before_run / after_run / before_epoch / after_epoch / before_iter / after_iter` 任一阶段,通过 `@HOOKS.register_module()` 注册。

【关键机制与数据】
- **默认优化器配置** (原文):`optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)`。
- **默认工作流** (原文):`workflow = [('train', 1)]`,即每个 epoch 都训练 1 次。
- **调度机制联动** (原文):默认 step 1x 调度调用 mmcv 的 `StepLRHook`;momentum scheduler 通常与 LR scheduler 配合,3D 检测中采用 cyclic 策略以加速收敛。
- **EvalHook 与 workflow 的关系** (原文):`EvalHook` 由 `after_train_epoch` 触发,与 `[('train', 1), ('val', 1)]` workflow 的差别仅在于后者会在每训练 epoch 后通过 `after_val_epoch` 在验证集上计算 loss;**不会**改变 `EvalHook` 行为。`total_epochs` 仅控制训练 epoch 数,不影响验证 workflow。
- **Hook 自定义支持版本** (原文):MMDetection v2.3.0 起支持(对应 issue #3395),v2.3.0 之前需改源码注册 hook。
- **导入方式限制** (原文):注册时只能导入类所在包路径,如 `mmdet.core.optimizer.my_optimizer`,而**不能**直接 `from mmdet.core.optimizer.my_optimizer import MyOptimizer`;只要模块根在 `PYTHONPATH` 下,目录结构可任意。
- **优化器构造器模板** (原文):给出 mmcv `default_constructor.py` 链接作为新构造器的参考实现。

【表格解读】
原文无表格。

【公式解读】
原文无公式(仅以 Python 配置字典形式给出调度参数,见技术要点第 5、6 条)。

【关联】
文档中提到的关联模块/特性(均为外部链接,无内部链接):
- **PyTorch 官方优化器 API 文档**:作为修改 `lr` 等参数的参考依据。
- **mmcv `default_constructor.py`**:作为自定义优化器构造器的模板来源。
- **mmcv `lr_updater.py`** 中的 `StepLRHook`(默认调度实现)、`CyclicLrUpdater`(循环 LR 调度实现),以及更多调度策略(`CosineAnnealing`、`Poly` 等)。
- **mmcv `momentum_updater.py`** 中的 `CyclicMomentumUpdater`:与 `CyclicLrUpdater` 配对的动量调度器。
- **MMDetection config 文档**:解释 `_delete_=True` 字段在继承覆盖时的语义。
- **EvalHook 与 `after_train_epoch`/`after_val_epoch`**:workflow 配置与 hook 触发时机联动,影响验证 loss 的计算时机。
- **MMDetection issue #3395**:v2.3.0 引入自定义 hook 能力的来源。

【使用方法】
1. **切换内置优化器**:在 config 文件中改写 `optimizer` 字段,如 `optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)`,参数遵循 PyTorch Optimizer API。
2. **注册自定义优化器 MyOptimizer(a,b,c)**:在 `mmdet/core/optimizer/my_optimizer.py` 定义后,通过 `mmdet/core/optimizer/__init__.py` 导入,或在 config 中加 `custom_imports = dict(imports=['mmdet.core.optimizer.my_optimizer'], allow_failed_imports=False)`,然后在 config 中 `optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)`。
3. **自定义优化器构造器**:在 `mmdet/core/optimizer/` 下新建继承 `object` 的类,用 `@OPTIMIZER_BUILDERS.register_module()` 注册,实现 `__call__(self, model)` 返回构建好的优化器。
4. **梯度裁剪**:在 config 中 `optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))`。
5. **动量调度**:在 config 中加 `momentum_config = dict(policy='cyclic', target_ratio=(0.85 / 0.95, 1), cyclic_times=1, step_ratio_up=0.4)`,常与 `lr_config` 配合。
6. **学习率调度**:Poly 用 `lr_config = dict(policy='poly', power=0.9, min_lr=1e-4, by_epoch=False)`;CosineAnnealing 用 `lr_config = dict(policy='CosineAnnealing', warmup='linear', warmup_iters=1000, warmup_ratio=1.0 / 10, min_lr_ratio=1e-5)`。
7. **修改 workflow**:将 config 中 `workflow = [('train', 1)]` 改为 `[('train', 1), ('val', 1)]` 即可在每训练 epoch 后跑一次验证。
8. **注册自定义 Hook MyHook(a,b)**:在 `mmdet/core/utils/my_hook.py` 定义继承 `Hook` 的类(实现各生命周期方法),在 `mmdet/core/utils/__init__.py` 导入;然后在 config 中通过 `custom_hooks` 字段引用即可生效(原文该部分代码被截断,但思路与自定义优化器一致)。
