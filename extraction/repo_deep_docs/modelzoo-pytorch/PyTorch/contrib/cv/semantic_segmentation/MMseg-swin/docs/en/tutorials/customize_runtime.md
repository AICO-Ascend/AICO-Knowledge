# Tutorial 6: Customize Runtime Settings

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/en/tutorials/customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/en/tutorials/customize_runtime.md

# 一体化深度解读:Tutorial 6 — Customize Runtime Settings

## 【定位】

本文是 MMseg(MMSegmentation,基于 Swin 等 backbone 的语义分割框架)中**"运行时训练流程"定制指南**——围绕优化器、学习率/动量调度、工作流 (workflow)、Checkpoint/Log 等 hook,告诉用户如何在不修改训练主干代码的情况下,通过修改配置文件和注册自定义组件来定制训练运行时行为。它是 Tutorial 6,属于"自定义"系列教程的一部分,假定读者已经熟悉基础配置文件结构与 runner 流程。

## 【技术要点】

1. **优化器三档定制梯度**:① 直接使用 PyTorch 内置优化器(仅改 config 的 `type` 字段);② 自定义优化器需新建 `mmseg/core/optimizer/` 目录并在文件中 `@OPTIMIZERS.register_module()` 装饰类,然后通过 `__init__.py` 或 `custom_imports` 导入注册;③ 自定义"优化器构造器" `MyOptimizerConstructor` 配合 `@OPTIMIZER_BUILDERS.register_module()` 装饰,以实现参数级 (paramwise) 配置,例如 BatchNorm 的特殊 weight decay。

2. **关键配置默认值/示例值(原文保留)**:
   - Adam 示例:`optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)`(原文指出"性能可能下降很多")。
   - SGD 示例:`optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)`。
   - 自定义优化器:`optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)`。
   - 默认训练调度:**step learning rate with 40k/80k schedule**,底层调用 `PolyLrUpdaterHook` (MMCV 中实现)。

3. **梯度裁剪稳定训练**:`optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))`,继承基础 config 时通常需配合 `_delete_=True` 覆盖冗余设置。

4. **动量调度 (Momentum Schedule)**:`lr_config` 与 `momentum_config` 配合使用 `policy='cyclic'`,原文给出 3D 检测加速收敛的样例:`lr_config target_ratio=(10, 1e-4)`,`momentum_config target_ratio=(0.85 / 0.95, 1)`,`cyclic_times=1`,`step_ratio_up=0.4`。

5. **训练调度 (Learning Rate Schedule) 多样化**:支持 Step、ConsineAnnealing(CosineAnnealing) 等多种策略,典型配置:
   - Step:`lr_config = dict(policy='step', step=[9, 10])`。
   - CosineAnnealing 带线性 warmup:`lr_config = dict(policy='CosineAnnealing', warmup='linear', warmup_iters=1000, warmup_ratio=1.0 / 10, min_lr_ratio=1e-5)`。

6. **Workflow 控制训练-验证循环顺序**:`workflow = [('train', 1), ('val', 1)]` 表示迭代运行 1 epoch 训练+1 epoch 验证。原文强调:`total_epochs` 只控制训练 epoch 数,不影响验证 workflow;`EvalHook` 由 `after_train_epoch` 触发,workflow 中的 val 不改变 `EvalHook` 行为,仅会让 runner 在每个训练 epoch 后额外在验证集上计算 loss。

7. **Hook 定制双路径**:① 通过 `custom_hooks = [dict(type='MyHook', a=a_value, b=b_value, priority='NORMAL')]` 引入 MMCV 已实现 hook;② 修改默认 runtime hooks(`log_config`、`checkpoint_config`、`evaluation`、`lr_config`、`optimizer_config`、`momentum_config`)。其中 `log_config` 优先级为 `VERY_LOW`,其他为 `NORMAL`。

8. **Checkpoint 与日志配置**:`checkpoint_config = dict(interval=1)`,支持 `max_keep_ckpts` 控制保留数量、`save_optimizer` 决定是否存储优化器 state dict;`log_config` 包装多个 logger hook(MMCV 支持 `WandbLoggerHook`、`MlflowLoggerHook`、`TensorboardLoggerHook`)并支持设 interval。

## 【关键机制与数据】

### 工作原理与数据流(原文信息整合)

1. **优化器注册机制(原文)**:自定义优化器经 `@OPTIMIZERS.register_module()` 装饰后,需通过 `mmseg/core/optimizer/__init__.py` 的 `from .my_optimizer import MyOptimizer` 或 config 中的 `custom_imports = dict(imports=['mmseg.core.optimizer.my_optimizer'], allow_failed_imports=False)` 完成模块导入,使其在程序启动时进入主命名空间,从而被注册表发现。**只能导入包路径**(如 `mmseg.core.optimizer.my_optimizer`),**不能直接导入 `mmseg.core.optimizer.my_optimizer.MyOptimizer`**(原文加粗强调)。

2. **优化器构造器(原文)**:当某些模型参数需要单独优化设置(如 BatchNorm 不衰减),可自定义 `MyOptimizerConstructor`,其签名应为 `__init__(self, optimizer_cfg, paramwise_cfg=None)` 与 `__call__(self, model)`,返回构造好的优化器。原文提供 mmcv 默认实现的链接作为模板。

3. **Workflow 与 EvalHook 关系(原文)**:原文明确指出 `Workflows [('train', 1), ('val', 1)]` 与 `[('train', 1)]` **不会改变 `EvalHook` 的行为**,因为 `EvalHook` 由 `after_train_epoch` 触发,验证 workflow 仅影响通过 `after_val_epoch` 触发的 hook;两者唯一区别是 runner 会在每个训练 epoch 后**在验证集上计算 loss**。

4. **Hook 优先级(原文)**:`log_config`(logger hook)优先级为 `VERY_LOW`;`checkpoint_config`、`evaluation`、`lr_config`、`optimizer_config`、`momentum_config` 优先级为 `NORMAL`。

5. **默认学习率调度(原文)**:默认采用 **40k/80k 的 step 学习率**,底层调用 MMCV 的 `PolyLrUpdaterHook`。

6. **导入路径灵活性(原文)**:通过 `custom_imports` 机制,用户可使用完全不同的文件目录结构,只要模块根目录在 `PYTHONPATH` 中可被定位即可。

### 性能/参考数据(原文给出的数字)

- 默认 step 调度:**40k / 80k**。
- Adam 优化器示例 lr:**0.0003**,weight_decay:**0.0001**。
- SGD 优化器示例 lr:**0.02**,momentum:**0.9**,weight_decay:**0.0001**。
- 梯度裁剪 max_norm:**35**,norm_type:**2**。
- Cyclic LR target_ratio:**(10, 1e-4)**,cyclic_times:**1**,step_ratio_up:**0.4**。
- Cyclic Momentum target_ratio:**(0.85 / 0.95, 1)**,cyclic_times:**1**,step_ratio_up:**0.4**。
- CosineAnnealing warmup_iters:**1000**,warmup_ratio:**1.0 / 10**,min_lr_ratio:**1e-5**。
- Checkpoint 保存 interval:**1**(即每个 epoch 保存一次)。
- CyclicLR/CyclicMomentum 是文档建议参考的实现位置(原文给出 mmcv GitHub 链接)。

## 【表格解读】

> 原文无显式 markdown 表格,所有"配置项"以 Python config 代码块呈现。为便于查阅,下面将文档中所有以代码块形式出现的 config 字段**逐字**还原为表格并逐行解读。

### 表 1:优化器相关 config(逐字还原)

| 原文配置片段(逐字) | 用途/字段含义解读 |
|---|---|
| `optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)` | Adam 优化器示例;`type` 指定类名,`lr=0.0003` 为学习率,`weight_decay=0.0001` 为 L2 正则系数。原文提示"性能可能下降很多"。 |
| `optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)` | SGD 优化器示例;`momentum=0.9` 引入动量。 |
| `optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)` | 自定义优化器示例;字段 `a/b/c` 与自定义类 `MyOptimizer.__init__(self, a, b, c)` 对应。 |

### 表 2:优化器注册与导入(逐字还原)

| 原文配置片段(逐字) | 解读 |
|---|---|
| `@OPTIMIZERS.register_module()` | 注册装饰器,使自定义优化器类被注册表识别。 |
| `from .my_optimizer import MyOptimizer`(放于 `mmseg/core/optimizer/__init__.py`) | 方式一:在 `__init__.py` 中显式导入模块,使注册表能发现新模块。 |
| `custom_imports = dict(imports=['mmseg.core.optimizer.my_optimizer'], allow_failed_imports=False)` | 方式二:在 config 中声明自定义导入,程序启动时自动导入。`allow_failed_imports=False` 表示导入失败将报错。 |

### 表 3:优化器构造器(逐字还原)

| 原文配置片段(逐字) | 解读 |
|---|---|
| `@OPTIMIZER_BUILDERS.register_module()` | 注册装饰器,用于"优化器构造器"而非优化器本身。 |
| `class MyOptimizerConstructor(object):` | 自定义构造器类示例。 |
| `def __init__(self, optimizer_cfg, paramwise_cfg=None):` | 构造器签名:接收 optimizer config 与按参数细分的配置(paramwise_cfg)。 |
| `def __call__(self, model):` | 调用接口,接收模型,返回构造好的优化器实例。 |
| `optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))` | 梯度裁剪配置;`max_norm=35` 为梯度最大范数,`norm_type=2` 表示 L2 范数;`_delete_=True` 用于在继承 base config 时丢弃不需要的旧字段。 |

### 表 4:学习率与动量调度(逐字还原)

| 原文配置片段(逐字) | 解读 |
|---|---|
| `lr_config = dict(policy='cyclic', target_ratio=(10, 1e-4), cyclic_times=1, step_ratio_up=0.4)` | 循环式学习率;`target_ratio=(10, 1e-4)` 为循环过程中学习率相对 base_lr 的最大与最小倍数,`cyclic_times=1` 循环 1 轮,`step_ratio_up=0.4` 表示上升段占比 0.4。 |
| `momentum_config = dict(policy='cyclic', target_ratio=(0.85 / 0.95, 1), cyclic_times=1, step_ratio_up=0.4)` | 与 `lr_config` 配合的动量循环;`target_ratio` 表示动量在 `0.85/0.95` 与 `1` 之间循环。原文明确该配置用于 3D 检测以加速收敛。 |
| `lr_config = dict(policy='step', step=[9, 10])` | Step 学习率;在 epoch 9 和 10 处衰减(具体衰减倍率由对应 hook 决定)。 |
| `lr_config = dict(policy='CosineAnnealing', warmup='linear', warmup_iters=1000, warmup_ratio=1.0 / 10, min_lr_ratio=1e-5)` | 余弦退火 + 线性 warmup;`warmup_iters=1000` 为 warmup 迭代数,`warmup_ratio=1.0/10` 起始 lr 比例,`min_lr_ratio=1e-5` 为最低 lr 相对比例。 |

### 表 5:Workflow(逐字还原)

| 原文配置片段(逐字) | 解读 |
|---|---|
| `workflow = [('train', 1)]` | 默认工作流:1 epoch 训练。 |
| `[('train', 1), ('val', 1)]` | 迭代运行 1 epoch 训练 + 1 epoch 验证;**注意:** val epoch 中模型参数不更新;`total_epochs` 仅控制 train epoch 数,不影响 val workflow。 |

### 表 6:Hook 配置(逐字还原)

| 原文配置片段(逐字) | 解读 |
|---|---|
| `custom_hooks = [dict(type='MyHook', a=a_value, b=b_value, priority='NORMAL')]` | 自定义 hook 列表;`type` 为 MMCV 已实现的 hook 类名,`priority` 可设 `VERY_LOW`/`NORMAL`(默认)等。 |
| `checkpoint_config = dict(interval=1)` | CheckpointHook 配置;`interval=1` 每 1 个 epoch 保存一次。还可设 `max_keep_ckpts` 控制保留数,`save_optimizer` 决定是否保存优化器 state dict。 |
| `log_config = ...`(MMCV 支持 `WandbLoggerHook`、`MlflowLoggerHook`、`TensorboardLoggerHook`) | 日志配置,包装多个 logger hook 并设 interval。 |

## 【公式解读】

原文无数学公式。文档中所有"公式性"内容均为 Python config 代码块(已在上节"表格解读"中以表格形式逐字还原并逐行解读)。涉及"比率"的参数(如 `target_ratio`、`warmup_ratio`、`min_lr_ratio`)属于配置项而非数学公式,本质是相对于 `base_lr` 的乘子或 warmup 阶段的插值系数,具体衰减曲线由对应 hook(如 `PolyLrUpdaterHook`、`CyclicLrUpdater`、`CyclicMomentumUpdater`)实现,本文未给出闭式数学表达。

## 【关联】

- **与上游 Tutorial 5 的关系(推断,未在原文显式提及)**:`Tutorial 6: Customize Runtime Settings` 是教程系列中的第 6 篇,前序教程通常涉及 config 结构、模型、数据、流程等基础概念;本文假定读者已熟悉 config 字段继承机制(`_base_`、`_delete_=True` 的语义)。
- **与 MMCV 的强耦合**:
  - 优化器注册表 `OPTIMIZERS` 来自 `mmcv.runner.optimizer`;构造器注册表 `OPTIMIZER_BUILDERS` 同样来自 `mmcv.runner.optimizer`。
  - 学习率/动量调度 hook(`PolyLrUpdaterHook`、`CyclicLrUpdater`、`CyclicMomentumUpdater`)均位于 `mmcv/runner/hooks/lr_updater.py` 与 `mmcv/runner/hooks/momentum_updater.py`。
  - 默认优化器构造器模板位于 `mmcv/runner/optimizer/default_constructor.py`。
  - `CheckpointHook` 位于 `mmcv/runner/hooks/checkpoint.py`。
  - 日志 hook(`WandbLoggerHook`、`MlflowLoggerHook`、`TensorboardLoggerHook`)为 MMCV 内置。
- **与下游/同级教程的承接**:本文末尾提及 `log_config`、`checkpoint_config`、`evaluation` 的详细用法,但原文内容在 `log_config` 详细示例处被截断(以 `https://mmcv.readthedocs.io/en/latest/api.` 结束),说明该 tutorial 与后续关于 logger hook、evaluation hook 的描述存在衔接。
- **与 config 文档的交叉引用**:梯度裁剪示例中引用了 `config documentation`(说明 `_delete_=True` 等 config 继承语义详见 config 教程)。
- **与 PyTorch 优化的关联**:自定义优化器继承自 `torch.optim.Optimizer`,其参数语义(如 `lr`、`momentum`、`weight_decay`)遵循 PyTorch 官方 API(原文给出 PyTorch 优化器文档链接)。

## 【使用方法】

> 以下均来自原文,无原文未涉及内容。

1. **直接换用 PyTorch 内置优化器**:修改 config 文件中的 `optimizer` 字段:
   ```python
   optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
   ```
   也可直接设置任何 PyTorch 优化器支持的参数(详见 PyTorch 官方 optim API 文档链接)。

2. **使用自定义优化器**(完整三步):
   - 在 `mmseg/core/optimizer/my_optimizer.py` 中实现类 `MyOptimizer(Optimizer)`,并以 `@OPTIMIZERS.register_module()` 装饰;
   - 通过 `mmseg/core/optimizer/__init__.py` 导入 `from .my_optimizer import MyOptimizer`,或通过 config 中的 `custom_imports = dict(imports=['mmseg.core.optimizer.my_optimizer'], allow_failed_imports=False)` 导入;
   - 在 config 中调用:
     ```python
     optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
     ```

3. **使用自定义优化器构造器**(用于参数级优化设置,如 BatchNorm 的 weight decay):
   - 创建 `MyOptimizerConstructor`,以 `@OPTIMIZER_BUILDERS.register_module()` 装饰,实现 `__init__(self, optimizer_cfg, paramwise_cfg=None)` 与 `__call__(self, model)`;
   - 参考 mmcv 默认构造器实现作为模板。

4. **梯度裁剪(原文命令)**:
   ```python
   optimizer_config = dict(
       _delete_=True, grad_clip=dict(max_norm=35, norm_type=2))
   ```

5. **动量调度(原文命令,与 LR 调度配合)**:
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

6. **训练调度选择(原文命令)**:
   ```python
   # Step
   lr_config = dict(policy='step', step=[9, 10])
   # CosineAnnealing + Linear Warmup
   lr_config = dict(
       policy='CosineAnnealing',
       warmup='linear',
       warmup_iters=1000,
       warmup_ratio=1.0 / 10,
       min_lr_ratio=1e-5)
   ```
   默认调度为 step + 40k/80k(底层使用 `PolyLrUpdaterHook`)。

7. **Workflow 配置(原文命令)**:
   ```python
   workflow = [('train', 1)]                # 默认
   workflow = [('train', 1), ('val', 1)]   # 训练+验证交替
   ```

8. **使用 MMCV 内置 Hook(原文命令)**:
   ```python
   custom_hooks = [
       dict(type='MyHook', a=a_value, b=b_value, priority='NORMAL')
   ]
   ```

9. **Checkpoint 配置(原文命令)**:
   ```python
   checkpoint_config = dict(interval=1)
   # 还可设置 max_keep_ckpts、save_optimizer(详见 mmcv.CheckpointHook 文档)
   ```

10. **Log 配置**:通过 `log_config` 包装 logger hook(`WandbLoggerHook`、`MlflowLoggerHook`、`TensorboardLoggerHook`),支持设 interval。原文在 `log_config` 详细示例处被截断,**更详细用法原文未涉及**(文档中以 `https://mmcv.readthedocs.io/en/latest/api.` 链接结束)。
