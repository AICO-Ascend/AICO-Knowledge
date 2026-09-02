# Tutorial 6: Customize Runtime Settings

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/en/tutorials/6_customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/en/tutorials/6_customize_runtime.md

# 一体化深度解读:Tutorial 6 — Customize Runtime Settings

## 【定位】
本文是 MMPose 文档体系中的第 6 篇教程,聚焦于**项目运行时的四大可定制维度**——优化器(optimizer)、学习率/动量调度(training schedule)、工作流(workflow)以及钩子(hooks),为开发者提供在不改框架源码的前提下,通过修改 config 文件或注册自定义组件来适配自身训练需求的标准化路径。

---

## 【技术要点】

1. **PyTorch 原生优化器即插即用**:无需改任何代码,仅修改 config 中 `optimizer` 字段的 `type` 即可切换全部 PyTorch 内置优化器;参数直接对应 `torch.optim` API 文档,例如 `Adam` 完整字段为 `lr`、`betas`、`eps`、`weight_decay`、`amsgrad` 五项。
2. **自研优化器三步接入法**:① 在 `mmpose/core/optimizer/` 下新建文件并以 `@OPTIMIZERS.register_module()` 装饰类;② 通过修改 `__init__.py` 或 config 中 `custom_imports` 触发注册机制(注意只导入包,不能直接 `from ... import MyOptimizer`);③ 在 config 中用 `type='MyOptimizer'` 调用。
3. **Optimizer Constructor 实现参数细粒度控制**:用于处理 BatchNorm 等特殊层需差异化超参(如不同 weight decay)的场景,实现模板即 `__call__(model) → optimizer`,参考对象是 mmcv 中的 `default_constructor.py`。
4. **训练稳定/加速两件套**:
   - 梯度裁剪:`optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))`(基于 L2 范数 35 上限);
   - 动量调度:`CyclicMomentumUpdater` 与 `CyclicLrUpdater` 配对使用,3D 检测场景中给出 `target_ratio=(0.85/0.95, 1)` 与学习率 `target_ratio=(10, 1e-4)` 同步循环。
5. **三种典型学习率策略**:默认 `StepLRHook`、Poly(`policy='poly', power=0.9, min_lr=1e-4, by_epoch=False`)、CosineAnnealing(配合 `linear` warmup,`warmup_iters=1000`,`warmup_ratio=1.0/10`,`min_lr_ratio=1e-5`)。
6. **Workflow 决定 phase 顺序**:`workflow = [('train', 1)]` 为默认;改为 `[('train', 1), ('val', 1)]` 后会在每轮训练后强制跑验证并计算 loss,但**不会改变 `EpochEvalHook` 行为**,因为后者由 `after_train_epoch` 触发,而验证 workflow 仅影响 `after_val_epoch` 钩子。

---

## 【关键机制与数据】

**工作原理与数据流**(原文):

- **Optimizer 注册机制**:MMPose 通过 mmcv 的 `Registry` 模式管理优化器,类被 `@OPTIMIZERS.register_module()` 装饰后,只要所在模块被导入(无论通过 `__init__.py` 隐式导入还是 `custom_imports` 显式导入),类名就会自动加入全局注册表,config 中的字符串 `type` 即可反查到类。
- **gradient clip 数据流**:`optimizer_config` 字段会被 `OptimizerHook` 消费,在 `optimizer.step()` 之前对 `model.parameters()` 的梯度按 L2 范数裁剪;`max_norm=35` 是原文中给出的具体阈值,`norm_type=2` 即欧氏范数。
- **Cyclic 调度联动原理**:`lr_config.policy='cyclic'` 与 `momentum_config.policy='cyclic'` 共用 `cyclic_times` 与 `step_ratio_up`,原文示例中二者均为 `cyclic_times=1, step_ratio_up=0.4`,意味着在前 40% 训练步内,学习率从基准的 10 倍下降到 `1e-4`,动量从 `0.85/0.95 ≈ 0.8947` 上升回 `1`,实现"高 LR 低动量探索 + 低 LR 高动量收敛"的循环。
- **Workflow 与 Hook 触发链**:`total_epochs` 仅约束训练 epoch 次数;`[('train', 1), ('val', 1)]` 中 val 阶段不更新参数(无反向传播),但 `EpochEvalHook` 仍按 `after_train_epoch` 时机执行,二者解耦。

---

## 【表格解读】
**原文无表格**。本文以代码片段与字段说明形式呈现配置项,未使用表格化排版。

---

## 【公式解读】
**原文无公式**。所有数值与调度规则均以 Python 字典配置形式给出,未以数学符号或 LaTeX 形式表达。

---

## 【关联】

本文处于 MMPose 教程体系的运行机制层,与以下外部模块/特性存在引用关系(均为原文中提供的 GitHub 锚点链接):

- **mmcv/runner/optimizer/default_constructor.py**:默认 `OptimizerConstructor` 的参考实现,作为自定义构造器的模板。
- **mmcv/runner/hooks/lr_updater.py**:`StepLRHook`(默认调度)、`CosineAnnealing`、`Poly` 策略以及 `CyclicLrUpdater` 均在此文件。
- **mmcv/runner/hooks/momentum_updater.py**:`CyclicMomentumUpdater` 在此,需与 `CyclicLrUpdater` 配对使用。
- **EpochEvalHook 与 Workflow 的语义边界**:验证 workflow 只会触发 `after_val_epoch` 时机上的钩子,而 `EpochEvalHook` 走的是 `after_train_epoch` 路径,因此二者职责正交,选择哪种取决于是否需要在每 epoch 训练后再额外跑一次"含 loss 计算"的验证轮次。
- **上游教程**:本文未直接引用前 5 篇教程,但其内容(配置系统、注册机制)是 Tutorial 0~5 已建立概念的下游应用。

---

## 【使用方法】

**启用方式 / 配置项 / 命令**(原文):

1. **切换 PyTorch 内置优化器**——直接修改 config:
   ```python
   optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
   ```
2. **启用自研优化器**——config 端指定 `type` + 参数:
   ```python
   optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
   ```
   并按"1.定义类 → 2.导入注册 → 3.修改 config"三步走。
3. **梯度裁剪**:
   ```python
   optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))
   ```
4. **学习率调度**:
   ```python
   # Poly
   lr_config = dict(policy='poly', power=0.9, min_lr=1e-4, by_epoch=False)
   # CosineAnnealing + linear warmup
   lr_config = dict(policy='CosineAnnealing', warmup='linear',
                    warmup_iters=1000, warmup_ratio=1.0/10, min_lr_ratio=1e-5)
   # Cyclic(配合 momentum_config 同步使用)
   lr_config = dict(policy='cyclic', target_ratio=(10, 1e-4),
                    cyclic_times=1, step_ratio_up=0.4)
   ```
5. **Workflow 切换**:
   ```python
   workflow = [('train', 1)]            # 默认:仅训练
   workflow = [('train', 1), ('val', 1)] # 每 epoch 训练后跑验证
   ```

> **注**:原文中 "Customize self-implemented hooks" 子节在导入位置被截断("Here we g..."),因此关于"实现自定义 Hook、注册新 Hook、修改 config"三步法的具体命令与 `Hook` 基类签名,本文未涉及。
