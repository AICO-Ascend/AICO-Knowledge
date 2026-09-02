# Tutorial 7: Customize Runtime Settings

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/video/R(2+1)D/docs/tutorials/7_customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/video/R(2+1)D/docs/tutorials/7_customize_runtime.md

# 深度解读:Tutorial 7 — Customize Runtime Settings

## 【定位】

本教程是 MMAction2 项目中关于"运行时定制"的方法指南,系统讲解如何在使用 R(2+1)D 等视频模型训练时,通过配置或代码扩展,**自定义优化器、学习率调度器、训练工作流以及训练 Hook**,从而让用户在不改动框架主干的前提下,完成对训练流程的精细化控制。

---

## 【技术要点】

1. **PyTorch 内置优化器的即插即用**:通过修改 config 中的 `optimizer` 字段即可切换任意 PyTorch 优化器,字段参数与 `torch.optim` API 完全对齐(例如 `Adam` 完整参数 `lr=0.001, betas=(0.9, 0.999), eps=1e-08, weight_decay=0, amsgrad=False`)。
2. **自研优化器的三步注册流程**:在 `mmaction/core/optimizer/` 下新建文件 → 用 `@OPTIMIZERS.register_module()` 装饰类 → 在 `__init__.py` 中 import 或通过 config 中 `custom_imports` 引入,最终在 `optimizer=dict(type='MyOptimizer', a=..., b=..., c=...)` 中使用。
3. **优化器构造器(Optimizer Constructor)用于逐参数定制**:典型用例是为 BatchNorm 等特定层设置不同的 weight decay;通过继承并用 `@OPTIMIZER_BUILDERS.register_module()` 装饰实现 `__call__(model) → optimizer`。
4. **训练稳定 / 加速的附加设置**:通过 `optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))` 实现梯度裁剪;通过 `lr_config` + `momentum_config` 的 cyclic 策略联动加速收敛(原文给出 3D 检测场景下的具体参数)。
5. **学习率调度策略可切换**:默认调用 `StepLRHook`,还支持 `poly`(power=0.9, min_lr=1e-4)与 `CosineAnnealing`(配合 linear warmup,warmup_iters=1000, warmup_ratio=1.0/10, min_lr_ratio=1e-5)。
6. **Workflow 与 EvalHook 的语义边界**:`workflow` 控制 runner 自身在 `train/val` 阶段间切换的 epoch 数,不影响 `EvalHook`(它由 `after_train_epoch` 触发);只有 runner 自己通过 `after_val_epoch` 触发的 Hook 才受 workflow 控制。
7. **Hook 的自定义与默认修改**:Hook 自定义遵循 "实现新类 → 用 registry 注册 → 在 config 中指定" 三步;对于框架内置 Hook(checkpoint / log / evaluation config)则通过 config 字段直接修改默认参数。

> 注:原文在 "Customize Hooks → Customize self-implemented hooks → 1. Implement a new hook" 末尾被截断(以 "Here we give an example of creating a new hook in MMAction2 and using" 结束),后文"2. Register the new hook"、"3. Modify the config"、"Use hooks implemented in MMCV"、"Modify default runtime hooks"(含 Checkpoint / Log / Evaluation 三小节)在提供的原文片段中**未出现**,本解读不臆造其内容。

---

## 【关键机制与数据】

### 工作原理 / 数据流

1. **优化器字段解析路径**:Runner 启动时读取 config 的 `optimizer` 字典 → 根据 `type` 字符串在 `OPTIMIZERS` 注册表中查找对应类 → 实例化时把其余字段作为关键字参数传入 → 返回 PyTorch 标准 `torch.optim.Optimizer` 子类实例。
2. **自研优化器的注册链路**:`custom_imports` 或 `__init__.py` 触发 import → `@OPTIMIZERS.register_module()` 装饰器将类写入 `mmcv.runner.OPTIMIZERS` 全局注册表 → 后续 `type='MyOptimizer'` 才能被解析。注意:**只能 import 包,不能直接 import 类**(原文明确写出 `mmaction.core.optimizer.my_optimizer.MyOptimizer` **cannot** be imported directly)。
3. **Optimzier Constructor 调用链**:Runner 在构造 optimizer 时,先用 `paramwise_cfg` 分析 model 参数 → 调用用户构造器 → 由构造器决定哪些参数使用哪种 learning rate、weight decay 或不参与 weight decay(典型用于 BN 层)。
4. **学习率 / 动量调度的实现位置**:二者分别由 `lr_config` 与 `momentum_config` 触发,实现在 MMCV 的 `lr_updater.py` 与 `momentum_updater.py` 中,Runner 通过 Hook 机制在每个 step/epoch 调用。
5. **Workflow 的执行机制**:workflow 是 `(phase, epochs)` 的列表,Runner 按顺序执行;`val` 阶段仅做前向推理,**不更新参数**;`total_epochs` 只约束 `train` 阶段的 epoch 总数。

### 性能 / 参数数据(原文直接给出的具体数值)

- 原文 Adam 简化配置:`lr=0.0003, weight_decay=0.0001`
- 原文 Adam 完整配置:`lr=0.001, betas=(0.9, 0.999), eps=1e-08, weight_decay=0, amsgrad=False`
- 原文 SGD 配置:`lr=0.02, momentum=0.9, weight_decay=0.0001`
- 原文梯度裁剪:`max_norm=35, norm_type=2`
- 原文 cyclic LR:`target_ratio=(10, 1e-4), cyclic_times=1, step_ratio_up=0.4`
- 原文 cyclic momentum:`target_ratio=(0.85 / 0.95, 1), cyclic_times=1, step_ratio_up=0.4`
- 原文 Poly schedule:`policy='poly', power=0.9, min_lr=1e-4, by_epoch=False`
- 原文 CosineAnnealing schedule:`policy='CosineAnnealing', warmup='linear', warmup_iters=1000, warmup_ratio=1.0 / 10, min_lr_ratio=1e-5`

---

## 【表格解读】

**原文无表格**。

原文未出现 markdown 表格,所有配置均以 Python config 代码块形式呈现(已在【关键机制与数据】小节以列表方式还原)。

---

## 【公式解读】

**原文无公式**。

原文未出现任何 LaTeX 公式或伪代码算法块。最接近"数学表达"的是 Cyclic LR / momentum 中的 `target_ratio` 元组(如 `(10, 1e-4)`、`(0.85 / 0.95, 1)`),但它们是 Python 字面量配置项,而非公式。

---

## 【关联】

本教程位于 `PyTorch/contrib/cv/video/R(2+1)D/docs/tutorials/` 路径下,定位为 MMAction2(及同源的 R(2+1)D 视频分类模型)的运行时定制指南。它与以下外部模块和上游仓库紧密耦合:

1. **MMCV(OpenMMLab Computer Vision 基础库)**
   - `mmcv.runner.OPTIMIZERS` —— 优化器注册表(自研优化器装饰器来源)。
   - `mmcv.runner.optimizer.OPTIMIZER_BUILDERS` —— 优化器构造器注册表。
   - `mmcv.runner.hooks.lr_updater.StepLRHook` —— 默认学习率调度 Hook(默认 strategy)。
   - `mmcv.runner.hooks.lr_updater.CyclicLrUpdater` —— 循环学习率调度(原文引用第 327 行)。
   - `mmcv.runner.hooks.momentum_updater.CyclicMomentumUpdater` —— 循环动量调度(原文引用第 130 行)。
   - `mmcv/runner/optimizer/default_constructor.py`(L11) —— 默认 optimizer constructor 实现,可作为模板。

2. **MMAction2 本仓库的目录约定**
   - `mmaction/core/optimizer/` —— 自研优化器放置目录(原文明确给出此路径)。
   - `mmaction/core/optimizer/__init__.py` —— 触发自动注册的 import 入口。

3. **Hooks 体系内的上下游关系**
   - `EvalHook`:由 `after_train_epoch` 触发,**不**受 `workflow` 控制(原文 note 3 明确指出)。
   - workflow 中的 `val` phase 仅触发通过 `after_val_epoch` 注册的 Hook,影响范围窄于 `EvalHook`。

4. **教程系列内部关系**
   本篇是"Tutorial 7",与教程 1–6 同属 `docs/tutorials/` 目录系列(原文未提供这些教程的具体标题,因此无法进一步关联具体章节,但显然属于"config + runtime"系列)。

5. **R(2+1)D 模型的具体应用上下文**
   本教程放置于 `R(2+1)D/docs/tutorials/` 下,意味着 R(2+1)D 视频分类模型在训练时直接复用 MMAction2 的全部运行时定制机制——本教程中所举的 SGD/Adam/lr_config/momentum_config 在 R(2+1)D 的 config 中按相同语法使用。

---

## 【使用方法】

原文明确给出的启用方式 / 配置项 / 命令如下:

1. **使用 PyTorch 内置优化器**
   ```python
   optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
   ```
   或完整参数:
   ```python
   optimizer = dict(type='Adam', lr=0.001, betas=(0.9, 0.999), eps=1e-08, weight_decay=0, amsgrad=False)
   ```

2. **自研优化器**
   - 步骤 1:在 `mmaction/core/optimizer/my_optimizer.py` 中定义类,使用 `from mmcv.runner import OPTIMIZERS` 与 `@OPTIMIZERS.register_module()`,继承 `torch.optim.Optimizer`。
   - 步骤 2(任选其一):
     - 改 `mmaction/core/optimizer/__init__.py`:`from .my_optimizer import MyOptimizer`
     - 或在 config 中加:`custom_imports = dict(imports=['mmaction.core.optimizer.my_optimizer'], allow_failed_imports=False)`
   - 步骤 3:在 config 中改写 `optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)`

3. **自定义 Optimizer Constructor**
   ```python
   from mmcv.runner.optimizer import OPTIMIZER_BUILDERS

   @OPTIMIZER_BUILDERS.register_module()
   class MyOptimizerConstructor:
       def __init__(self, optimizer_cfg, paramwise_cfg=None):
           pass
       def __call__(self, model):
           return my_optimizer
   ```

4. **附加训练技巧**
   - 梯度裁剪:`optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))`
   - Cyclic LR + 动度联动(3D 检测示例):
     ```python
     lr_config = dict(policy='cyclic', target_ratio=(10, 1e-4), cyclic_times=1, step_ratio_up=0.4)
     momentum_config = dict(policy='cyclic', target_ratio=(0.85 / 0.95, 1), cyclic_times=1, step_ratio_up=0.4)
     ```

5. **学习率调度切换**
   - Poly:`lr_config = dict(policy='poly', power=0.9, min_lr=1e-4, by_epoch=False)`
   - CosineAnnealing + linear warmup:
     ```python
     lr_config = dict(policy='CosineAnnealing', warmup='linear', warmup_iters=1000,
                      warmup_ratio=1.0 / 10, min_lr_ratio=1e-5)
     ```

6. **Workflow 配置**
   - 默认:`workflow = [('train', 1)]`
   - 加入验证:`[('train', 1), ('val', 1)]`(注意 `val` 阶段**不更新参数**,且**不影响** `EvalHook` 行为)

7. **Hook 自定义与默认 Hook 修改**
   - 自研 Hook:实现新类 → 在 registry 注册 → 在 config 中指定(原文在"1. Implement a new hook"小节末尾被截断,具体 import、装饰器、config 写法**原文未涉及**,本节不补充)。
   - 修改默认 runtime Hook(checkpoint / log / evaluation config):**原文未涉及**(该节标题在原文中存在,但内容位于截断后的部分,本文档片段中未出现)。

---

### 解读说明

本文档原文在 Tutorial 7 中部被截断,以下小节在提供的原文片段中**不完整或缺失**:
- `2. Register the new hook`
- `3. Modify the config`(自研 Hook 部分)
- `Use hooks implemented in MMCV`
- `Modify default runtime hooks`(含 `Checkpoint config` / `Log config` / `Evaluation config` 三个子小节)

本解读严格基于原文实际可读片段,**未对缺失内容进行任何形式的臆造、补全或参数推断**。
