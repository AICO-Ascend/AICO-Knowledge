# Tutorial 5: Customize Runtime Settings

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/customize_runtime.md

# 深度解读：Tutorial 5 — Customize Runtime Settings

## 【定位】

本教程解决**「在不修改底层训练框架代码的前提下，如何通过配置文件与自定义模块机制，灵活定制 MMDetection 训练过程中的优化器、学习率/动量调度、运行流程（workflow）以及训练钩子（hooks）」**这一问题，向开发者展示了从 PyTorch 内置优化器到自研优化器/构造器/钩子的完整接入路径。

---

## 【技术要点】

1. **PyTorch 原生优化器切换**：仅修改 config 的 `optimizer` 字段即可替换；举例使用 `Adam`（`lr=0.0003, weight_decay=0.0001`，文档同时提示性能可能下降明显）；`SGD` 默认形式为 `type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001`。
2. **自研优化器三步接入法**：(1) 在 `mmdet/core/optimizer/my_optimizer.py` 中继承 `torch.optim.Optimizer` 并用 `@OPTIMIZERS.register_module()` 装饰；(2) 通过修改 `mmdet/core/optimizer/__init__.py` **或** 在 config 中写 `custom_imports = dict(imports=['mmdet.core.optimizer.my_optimizer'], allow_failed_imports=False)` 注册；(3) 在 config `optimizer` 字段中以 `dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)` 形式调用。
3. **自研优化器构造器（Optimizer Constructor）**：用于参数级精细调参（如对 BatchNorm 单独设置 weight_decay）；通过 `@OPTIMIZER_BUILDERS.register_module()` 注册，模板参考 mmcv 的 `default_constructor.py`。
4. **训练稳定与加速技巧**：
   - **梯度裁剪**：`optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))`，继承 base config 时需 `_delete_=True`。
   - **动量调度**：`momentum_config = dict(policy='cyclic', target_ratio=(0.85/0.95, 1), cyclic_times=1, step_ratio_up=0.4)`，与 `lr_config`（`policy='cyclic', target_ratio=(10, 1e-4), cyclic_times=1, step_ratio_up=0.4`）配对用于 3D 检测加速收敛。
5. **学习率调度多样化**：除默认 `StepLRHook` 的 1x step 调度外，支持 `Poly`（`policy='poly', power=0.9, min_lr=1e-4, by_epoch=False`）与 `CosineAnnealing`（`warmup='linear', warmup_iters=1000, warmup_ratio=1.0/10, min_lr_ratio=1e-5`）。
6. **Workflow 与 Hook 机制**：默认 `workflow = [('train', 1)]`；可通过 `[('train', 1), ('val', 1)]` 交替训练/验证；自研 Hook 需继承 `mmcv.runner.Hook` 并实现 `before_run / after_run / before_epoch / after_epoch / before_iter / after_iter` 六个生命周期方法。

---

## 【关键机制与数据】

**优化器注册机制（基于 Registry）**：MMDetection 通过全局注册表 `OPTIMIZERS`、`OPTIMIZER_BUILDERS`、`HOOKS` 实现「配置驱动 + 模块插拔」。文档原文强调：使用 `custom_imports` 时**必须只导入到包含 `MyOptimizer` 类的包路径**（如 `mmdet.core.optimizer.my_optimizer`），**不能**直接导入 `mmdet.core.optimizer.my_optimizer.MyOptimizer`，否则注册逻辑不会被触发。只要模块根路径在 `PYTHONPATH` 中，文件目录结构可以自由组织。

**Workflow 行为差异**（原文三条 Note）：
- `val` 阶段**不更新**模型参数。
- `total_epochs` 只控制训练 epoch 数，不影响 val workflow。
- `EvalHook` 由 `after_train_epoch` 触发，因此 `[('train', 1), ('val', 1)]` 与 `[('train', 1)]` 在 `EvalHook` 行为上**完全一致**；两者的唯一区别是 runner 会在每个训练 epoch 后**额外计算一次验证集上的 loss**。

**Cyclic LR 与 Momentum 配对原理**：通过 `step_ratio_up=0.4` 控制上升比例，`cyclic_times=1` 设置循环次数，`target_ratio` 给出学习率（`(10, 1e-4)`）与动量（`(0.85/0.95, 1)`）的起止比 —— 文档指明该配对用于 **3D detection** 加速收敛，具体实现见 mmcv 的 `CyclicLrUpdater` 与 `CyclicMomentumUpdater`。

**Hook 自定义前提**：文档明确「MMDetection 自 v2.3.0 起通过 PR #3395 支持自定义 hook」，v2.3.0 之前用户需要手动修改代码完成注册。

---

## 【表格解读】

**原文无表格**。

文档全程以代码配置块（config dict）和 API 路径说明形式呈现，未出现任何 markdown 表格。

---

## 【公式解读】

**原文无 LaTeX 公式**。

文档中出现的均为 **Python config dict 形式**的伪代码/配置声明（无算术公式表达），已在「技术要点」与「关键机制与数据」节中按原文逐字保留并解释其字段含义。

---

## 【关联】

1. **与上游 mmcv 的强耦合**：
   - `torch.optim.Optimizer`（PyTorch 原生优化器基类）
   - `mmcv.utils.build_from_cfg`、`mmcv.runner.optimizer.OPTIMIZER_BUILDERS / OPTIMIZERS`
   - `mmcv.runner.HOOKS / Hook`、`mmcv.runner.hooks.lr_updater`（`StepLRHook`、`CosineAnnealing`、`Poly`、`CyclicLrUpdater`）
   - `mmcv.runner.hooks.momentum_updater`（`CyclicMomentumUpdater`）
   - `mmdet.utils.get_root_logger`
   文档显式给出的 mmcv GitHub 链接均为**外部链接**，文末**未提供任何仓库内部链接**（按提示标注为「无」）。

2. **与同教程其他章节的关系**（基于文档内部行文）：
   - 「Customize optimization settings」承接 `optimizer` 与 `optimizer_config` 字段；
   - 「Customize training schedules」与上文 `lr_config`、`momentum_config` 字段形成闭环；
   - 「Customize workflow」与 `total_epochs` 配置相关；
   - 「Customize hooks」与 `EvalHook` 行为直接关联（`after_train_epoch` vs `after_val_epoch` 触发差异）。
3. **关于本文档所在路径的观察**：原文路径位于 `SSD_for_PyTorch/docs/en/tutorials/`，但全文内容均针对通用 MMDetection 框架（`mmdet/core/...`），而非 SSD 专属内容；这暗示该文档为上游 MMDetection tutorial 的**整体移植/复用版本**，未对 SSD 模型做特殊定制。

---

## 【使用方法】

> 注：原文在「注册自研 Hook」小节末尾**被截断**（以 ` ```pyt ` 不完整代码块结束），以下仅汇总原文已展示的可用方式。

**① 切换 PyTorch 内置优化器**：直接修改 config 的 `optimizer` 字段，按 PyTorch 优化器 API 传参。
```python
optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
```

**② 接入自研优化器**：在 `mmdet/core/optimizer/` 下新建模块、用 `@OPTIMIZERS.register_module()` 装饰，然后在 config 中：
```python
custom_imports = dict(imports=['mmdet.core.optimizer.my_optimizer'], allow_failed_imports=False)
optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
```

**③ 启用梯度裁剪**：
```python
optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))
```

**④ 启用 Cyclic 学习率 + 动量调度**（3D 检测推荐）：
```python
lr_config = dict(policy='cyclic', target_ratio=(10, 1e-4), cyclic_times=1, step_ratio_up=0.4)
momentum_config = dict(policy='cyclic', target_ratio=(0.85 / 0.95, 1), cyclic_times=1, step_ratio_up=0.4)
```

**⑤ 切换学习率策略**：
```python
# Poly
lr_config = dict(policy='poly', power=0.9, min_lr=1e-4, by_epoch=False)
# CosineAnnealing + linear warmup
lr_config = dict(policy='CosineAnnealing', warmup='linear', warmup_iters=1000,
                 warmup_ratio=1.0 / 10, min_lr_ratio=1e-5)
```

**⑥ 修改 workflow 交替训练/验证**：
```python
workflow = [('train', 1), ('val', 1)]
```

**⑦ 接入自研 Hook**：在 `mmdet/core/utils/my_hook.py` 中继承 `Hook`、用 `@HOOKS.register_module()` 装饰，并通过修改 `mmdet/core/utils/__init__.py` 或 `custom_imports` 完成注册（具体配置项原文**因文档截断未给出**）。
