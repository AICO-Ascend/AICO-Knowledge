# Tutorial 5: Customize Runtime Settings

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/FCOS/docs/tutorials/customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/FCOS/docs/tutorials/customize_runtime.md

# 一体化深度解读: FCOS 自定义运行时设置教程

## 【定位】

这篇文档解决的是 **如何在 MMDetection/FCOS 训练流程中自定义运行时设置**——具体涵盖优化器(含自研扩展)、学习率/动量调度、训练-验证工作流、以及训练钩子四大维度的可定制化能力,使使用者既能沿用 PyTorch 内置组件,也能注册自定义实现而无需修改框架源码。

---

## 【技术要点】

1. **优化器自定义的两条路径**: 一是直接切换 PyTorch 内置优化器(如 `Adam`, 示例 `lr=0.0003, weight_decay=0.0001`),通过修改 config 中 `optimizer` 字段即可;二是通过在 `mmdet/core/optimizer/` 下新建文件→`OPTIMIZERS.register_module()`→加入 `__init__.py` 或使用 `custom_imports` 导入,实现自研优化器(如 `MyOptimizer(a,b,c)`)。

2. **优化器构造器 (Optimizer Constructor) 机制**: 当需要对 BatchNorm 等特定层做参数级细粒度调优(如不同层不同 weight decay)时,可通过继承 `OPTIMIZER_BUILDERS.register_module()` 的 `MyOptimizerConstructor` 实现 `__call__(model)`,输入模型返回构造好的 optimizer;模板参考 mmcv 的 `default_constructor.py`。

3. **梯度裁剪与动量调度作为训练稳定/加速器**: 通过 `optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))` 注入梯度裁剪;通过 `CyclicLrUpdater` + `CyclicMomentumUpdater` 配对实现"循环 LR + 循环动量"以加速收敛,示例中 `target_ratio=(10, 1e-4)`、`cyclic_times=1`、`step_ratio_up=0.4`,动量比 `target_ratio=(0.85/0.95, 1)`。

4. **学习率调度策略**: 默认使用 `StepLRHook` 的 1× step schedule;还支持 `Poly`(power=0.9, min_lr=1e-4, by_epoch=False)与 `CosineAnnealing`(warmup='linear', warmup_iters=1000, warmup_ratio=1.0/10, min_lr_ratio=1e-5)。

5. **Workflow 控制训练/验证迭代顺序**: 默认 `workflow = [('train', 1)]` 只跑训练;改为 `[('train', 1), ('val', 1)]` 则每训练 1 epoch 后插入验证 epoch,但 val 阶段不更新模型参数,且不会改变 `EvalHook` 行为。

6. **钩子 (Hook) 机制与生命周期**: 自 v2.3.0 起支持配置化注入自定义钩子,通过 `@HOOKS.register_module()` 注册继承自 `Hook` 的类,在 `before_run/after_run/before_epoch/after_epoch/before_iter/after_iter` 六个生命周期节点插入逻辑。

---

## 【关键机制与数据】

**工作原理 / 数据流(以"自研优化器注册"为例)**:

1. 用户在 `mmdet/core/optimizer/my_optimizer.py` 中定义 `MyOptimizer(Optimizer)`,用 `@OPTIMIZERS.register_module()` 装饰;
2. 通过两条路径之一让注册器能发现该类:
   - 路径 A: 在 `mmdet/core/optimizer/__init__.py` 内 `from .my_optimizer import MyOptimizer`;
   - 路径 B: 在 config 中写 `custom_imports = dict(imports=['mmdet.core.optimizer.my_optimizer'], allow_failed_imports=False)`,程序启动时自动 import;
3. config 中 `optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)` 由 mmcv 的 `build_from_cfg` 按 `type` 字段查表实例化;
5. ⚠️ 原文强调: **只能 import 包路径** `mmdet.core.optimizer.my_optimizer`,不能直接 `import mmdet.core.optimizer.my_optimizer.MyOptimizer`(原文:)。

**性能/经验性数据(原文有的)**:
- 原文提示使用 Adam 会"性能 drop a lot"(未给出具体数值, 仅作定性提示)。
- 梯度裁剪示例 `max_norm=35, norm_type=2`。
- CosineAnnealing 的 `warmup_iters=1000`、warmup_ratio=`1.0/10`。
- 3D 检测场景中循环策略的动量比为 `0.85/0.95`。

**关于 EvalHook 与 validation workflow 的差异**:
原文明确指出 `EvalHook` 由 `after_train_epoch` 触发,而 validation workflow 只触发 `after_val_epoch` 钩子;因此二者的**唯一差异**是: 在 `train, 1), ('val', 1)]` 配置下,runner 会在每训练 epoch 后额外计算验证集上的 loss。

---

## 【表格解读】

**原文无表格**(整篇文档由叙述段落、Python 代码片段和散列配置示例构成,未出现任何 markdown 表格或参数对照表)。

---

## 【公式解读】

**原文无公式**(文档未出现 LaTeX 数学公式或伪代码公式;仅出现以下形式化配置"伪代码",按原文逐字保留并解释关键符号含义):

### 公式 1 — 优化器定义(原文逐字):

```python
optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
```

- `type`: 选择 PyTorch 已注册的优化器类名,此处为 `'Adam'`(原文提示"性能可能 drop a lot")。
- `lr`: 学习率,值 `0.0003`。
- `weight_decay`: L2 正则化系数,值 `0.0001`。

### 公式 2 — 自研优化器 config 接入:

```python
optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
```

- `type`: 类名字符串,需与 `@OPTIMIZERS.register_module()` 注册名一致。
- `a/b/c_value`: 占位符,代表用户在 config 中设定的 `MyOptimizer.__init__` 三个参数取值。

### 公式 3 — 梯度裁剪:

```python
optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))
```

- `_delete_=True`: 继承基 config 时用于剔除基 config 中不需要的字段。
- `grad_clip`: dict,声明启用梯度裁剪。
- `max_norm=35`: 梯度范数上限。
- `norm_type=2`: L2 范数。

### 公式 4 — Poly 学习率:

```python
lr_config = dict(policy='poly', power=0.9, min_lr=1e-4, by_epoch=False)
```

- `policy='poly'`: 调度策略。
- `power=0.9`: 多项式衰减指数。
- `min_lr=1e-4`: 学习率下限。
- `by_epoch=False`: 按 iter 而非 epoch 衰减。

### 公式 5 — CosineAnnealing:

```python
lr_config = dict(
    policy='CosineAnnealing',
    warmup='linear',
    warmup_iters=1000,
    warmup_ratio=1.0 / 10,
    min_lr_ratio=1e-5)
```

- `warmup='linear'`: 线性 warmup。
- `warmup_iters=1000`: warmup 步数。
- `warmup_ratio=1.0/10`: warmup 起始 lr = base_lr × 此值。
- `min_lr_ratio=1e-5`: 余弦退火下限占 base_lr 的比例。

### 公式 6 — 循环学习率 / 动量:

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

- `policy='cyclic'`: 循环调度策略。
- `target_ratio`: 学习率为 `(base_lr × 10, base_lr × 1e-4)` 区间循环;动量为 `(0.85/0.95 × base_mom, 1 × base_mom)` 区间循环(原文说明该动量区间源于 3D 检测场景)。
- `cyclic_times=1`: 循环 1 轮。
- `step_ratio_up=0.4`: 上升段占总步数 40%。

### 公式 7 — Workflow:

```python
workflow = [('train', 1)]          # 默认
workflow = [('train', 1), ('val', 1)]  # 训练-验证交替
```

- 元组 `(phase, epochs)`,`phase ∈ {'train','val'}`,`epochs` 为该阶段持续 epoch 数。

---

## 【关联】

文档虽未在文末给出"内部链接"区,但通篇提及的外部依赖/上游模块构成了完整的关联图谱,主要锚点如下:

1. **依赖 MMCV 的 `runner` 与 `builder` 模块**:
   - `OPTIMIZERS` / `OPTIMIZER_BUILDERS` 注册器源自 `mmcv.runner.optimizer`(`OPTIMIZER_BUILDERS, OPTIMIZERS`)与 `mmcv.utils.build_from_cfg`;
   - `HOOKS` 注册器与 `Hook` 基类源自 `mmcv.runner`;
   - 调度器实现位于 mmcv 仓库:`mmcv/runner/hooks/lr_updater.py`(StepLRHook、CosineAnnealing、Poly、CyclicLrUpdater)和 `mmcv/runner/hooks/momentum_updater.py`(CyclicMomentumUpdater);
   - 默认 optimizer constructor 模板: `mmcv/runner/optimizer/default_constructor.py`。

2. **依赖 PyTorch 原生能力**:
   - `torch.optim.Optimizer` 是所有自研优化器的基类(原文要求继承该类);
   - 用户可参考 PyTorch 官方文档 `https://pytorch.org/docs/stable/optim.html?highlight=optim#module-torch.optim` 来设置 `optimizer` 字段参数。

4. **与 MMDetection 框架自身结构的关系**:
   - 自研优化器要求文件放置于 `mmdet/core/optimizer/` 命名空间;
   - 自研 Hook 要求文件放置于 `mmdet/core/utils/`(`mmdet/core/utils/my_hook.py`);
   - 自 v2.3.0 起 MMDetection 才支持"无需改代码、仅改 config 即可注入自定义 Hook"的特性(#3395)。

5. **与 config 继承体系的关系**:
   - `_delete_=True` 字段是 MMDetection config 继承机制的一部分,详见原文链接的 mmdetection readthedocs 配置文档;
   - `custom_imports` 是 config 级模块注入机制,使得不放在 `mmdet/core/...` 下的自研模块只要 `PYTHONPATH` 能定位即可被加载。

6. **与 EvalHook 的关系**:
   - 验证 workflow 不影响 `EvalHook`,后者由 `after_train_epoch` 触发;这一点在 Workflow 节中作为"Note 3"被显式说明。

---

## 【使用方法】

**(一) 直接切换内置优化器**: 修改 config 中的 `optimizer` 字段,如:

```python
optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
```

**(二) 注册并启用自研优化器 `MyOptimizer`**:

1. 在 `mmdet/core/optimizer/my_optimizer.py` 定义继承 `torch.optim.Optimizer` 的类,用 `@OPTIMIZERS.register_module()` 装饰;
2. 二选一完成注册发现:
   - 在 `mmdet/core/optimizer/__init__.py` 加入 `from .my_optimizer import MyOptimizer`;或
   - 在 config 顶部加 `custom_imports = dict(imports=['mmdet.core.optimizer.my_optimizer'], allow_failed_imports=False)`(⚠️ 仅 import 包,不能 import 类)。
3. config 中改写:
   ```python
   optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
   ```

**(三) 启用自定义优化器构造器**: 定义继承 `object` 的 `MyOptimizerConstructor`,用 `@OPTIMIZER_BUILDERS.register_module()` 装饰,实现 `__init__(optimizer_cfg, paramwise_cfg=None)` 与 `__call__(model)`,在 config 中按 optimizer builder 字段挂载(原文未给出完整 config 片段)。

**(四) 启用梯度裁剪**:

```python
optimizer_config = dict(
    _delete_=True, grad_clip=dict(max_norm=35, norm_type=2))
```

**(五) 启用循环 LR + 循环动量加速收敛**:

```python
lr_config = dict(policy='cyclic', target_ratio=(10, 1e-4), cyclic_times=1, step_ratio_up=0.4)
momentum_config = dict(policy='cyclic', target_ratio=(0.85/0.95, 1), cyclic_times=1, step_ratio_up=0.4)
```

**(六) 切换学习率调度策略**:

```python
# Poly
lr_config = dict(policy='poly', power=0.9, min_lr=1e-4, by_epoch=False)
# CosineAnnealing
lr_config = dict(policy='CosineAnnealing', warmup='linear', warmup_iters=1000, warmup_ratio=1.0/10, min_lr_ratio=1e-5)
```

**(七) 配置训练-验证工作流**:

```python
workflow = [('train', 1)]                 # 仅训练(默认)
workflow = [('train', 1), ('val', 1)]     # 训练后插入验证(注: val 不更新参数, 不影响 EvalHook)
```

**(八) 注册自定义 Hook**:

1. 在 `mmdet/core/utils/my_hook.py` 定义继承 `mmcv.runner.Hook` 的 `MyHook`,用 `@HOOKS.register_module()` 装饰,按需实现六个生命周期方法;
2. 在 `mmdet/core/utils/__init__.py` import 该模块(原文此节被截断,后续 import 方式与 optimizer 相同:`__init__.py` 导入或 `custom_imports`,原文未给出完整示例)。

---

> 注: 本教程原文在 "Customize hooks → Register the new hook" 节末尾被截断,后续关于"在 config 中通过 `custom_imports` 导入 hook 模块"以及 "在 `custom_imports` 中如何指定 hook" 的具体示例在原文未呈现,以上解读严格基于实际可见内容,未做臆测补充。
