# Tutorial 5: Customize Runtime Settings

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/YoloV3_ID1790_for_PyTorch/docs/tutorials/customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/YoloV3_ID1790_for_PyTorch/docs/tutorials/customize_runtime.md

# 一体化深度解读:Tutorial 5: Customize Runtime Settings

## 【定位】

这篇文档解决的是 **MMDetection (基于 PyTorch) 训练运行时配置的可定制化问题**,系统化地说明如何修改优化器、优化器构造器、学习率/动量调度策略、训练流程 (workflow) 以及自定义 Hook,从而在不改动核心代码的前提下,通过 config 文件驱动训练行为的细粒度调整。

---

## 【技术要点】

1. **优化器替换为 PyTorch 内置优化器**:仅需修改 config 中 `optimizer` 字段,例如切到 ADAM:`optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)`;切到 SGD:`optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)`。

2. **自定义优化器三步走**:在 `mmdet/core/optimizer/` 下新建模块 → 用 `@OPTIMIZERS.register_module()` 装饰类 → 通过修改 `__init__.py` 或 config 中 `custom_imports` 导入(注意**不能**直接 import 类,只能导入所在包)。

3. **优化器构造器 (Optimizer Constructor) 实现参数级差异化配置**:用于给 BatchNorm 等特定层设置不同 weight decay 等细粒度行为,通过 `@OPTIMIZER_BUILDERS.register_module()` 注册,默认实现位于 `mmcv/runner/optimizer/default_constructor.py#L11`。

4. **训练稳定/加速技巧**:梯度裁剪 `grad_clip=dict(max_norm=35, norm_type=2)`(需用 `_delete_=True` 覆盖基类配置);动量调度配合学习率调度使用 cyclic 策略(`target_ratio=(10, 1e-4)` 与 `(0.85/0.95, 1)`, `cyclic_times=1`, `step_ratio_up=0.4`)。

5. **学习率调度策略**:默认调用 `StepLRHook` 的 1x 阶跃调度;另支持 Poly (`policy='poly', power=0.9, min_lr=1e-4, by_epoch=False`) 与 CosineAnnealing (带 `warmup='linear'`, `warmup_iters=1000`, `warmup_ratio=1.0/10`, `min_lr_ratio=1e-5`)。

6. **工作流 (Workflow) 控制阶段执行顺序**:默认 `workflow = [('train', 1)]`,可改为 `[('train', 1), ('val', 1)]` 交替训练/验证;但 `EvalHook` 由 `after_train_epoch` 触发,与验证 workflow 无关,因此两者的唯一差异是后者会在每个训练 epoch 后在验证集上计算 loss。

7. **自定义 Hook**:自 v2.3.0 起 (issue #3395) 支持通过 config 直接注册 Hook;Hook 可在 `before_run/after_run/before_epoch/after_epoch/before_iter/after_iter` 6 个阶段插入逻辑,通过 `@HOOKS.register_module()` 装饰。

---

## 【关键机制与数据】

### 1. 优化器注册机制(原文)

**原文:** 自定义优化器需放进新建目录 `mmdet/core/optimizer/`,通过 `@OPTIMIZERS.register_module()` 装饰类,然后二选一导入:
- 修改 `mmdet/core/optimizer/__init__.py` 添加 `from .my_optimizer import MyOptimizer`
- 或在 config 中写 `custom_imports = dict(imports=['mmdet.core.optimizer.my_optimizer'], allow_failed_imports=False)`

**关键约束(原文):** "`mmdet.core.optimizer.my_optimizer.MyOptimizer` **cannot** be imported directly."——只能导入包,不能直接导入类,否则 registry 无法发现。`custom_imports` 允许使用任意目录结构,只要模块根在 `PYTHONPATH` 中。

### 2. 参数级优化器构造器(原文)

**原文:** "Some models may have some parameter-specific settings for optimization, e.g. weight decay for BatchNorm layers."——当不同层 (如 BN 与 conv/linear) 需要差异化超参时使用,默认构造器模板见 `default_constructor.py#L11`。

### 3. 梯度裁剪覆盖机制(原文)

**原文:** "If your config inherits the base config which already sets the `optimizer_config`, you might need `_delete_=True` to overide the unnecessary settings."——`_delete_=True` 用于在继承式 config 中彻底删除基类字段,避免 merge 失败。

### 4. 动量调度与 LR 调度联动(原文)

**原文:** "Momentum scheduler is usually used with LR scheduler, for example, the following config is used in 3D detection to accelerate convergence."——cyclic 策略的动量比 `target_ratio=(0.85 / 0.95, 1)` 表示动量在 0.85/0.95 到 1 之间循环(对应 LR 在 10 到 1e-4 之间循环),`step_ratio_up=0.4` 表示上升段占比 40%。具体实现参考 `CyclicLrUpdater#L327` 与 `CyclicMomentumUpdater#L130`。

### 5. 验证 Workflow 的副作用边界(原文)

**原文:** 三条注意事项:
- (1) "The parameters of model will not be updated during val epoch." 验证阶段不更新参数;
- (2) "`total_epochs` in the config only controls the number of training epochs" 仅控制训练 epoch 数;
- (3) "`EvalHook` is called by `after_train_epoch` and validation workflow only affect hooks that are called through `after_val_epoch`"——`EvalHook` 不受 workflow 影响,验证 workflow 仅触发 `after_val_epoch` 钩子。

### 6. 自定义 Hook 注册机制(原文)

**原文:** "MMDetection supports customized hooks in training (#3395) since v2.3.0."——v2.3.0 之前需改源码,之后可纯 config 驱动。

---

## 【表格解读】

**原文无表格。** 文档中所有配置信息均以 Python config 代码块形式给出(优化器、optimizer_config、lr_config、momentum_config、workflow、Hook 类定义等),未使用 markdown 表格组织。

---

## 【公式解读】

**原文无公式。** 文档不包含 LaTeX 数学公式或伪代码算法表达式;所有量化参数(`max_norm=35`、`norm_type=2`、`warmup_iters=1000`、`warmup_ratio=1.0/10`、`step_ratio_up=0.4`、`target_ratio=(10, 1e-4)` 等)均以 Python 字面量形式直接出现在 config 示例中,不存在 `f(x)=...` 形式的数学定义。

---

## 【关联】

文档中通过超链接显式指向的上下游组件(MMCV 训练框架)如下:

| 关联模块 | 作用 | 原文链接 |
|---|---|---|
| `torch.optim` | PyTorch 内置优化器 API 文档,定义 ADAM/SGD 等参数语义 | https://pytorch.org/docs/stable/optim.html?highlight=optim#module-torch.optim |
| `mmcv.runner.optimizer.default_constructor` | 默认 optimizer constructor 实现,可作为新构造器模板 | `mmcv/runner/optimizer/default_constructor.py#L11` |
| `mmcv.runner.hooks.lr_updater.StepLRHook` | 默认 1x 阶梯式学习率调度的底层 hook | `mmcv/runner/hooks/lr_updater.py#L153` |
| `mmcv.runner.hooks.lr_updater` (聚合) | 全部学习率调度策略(`CosineAnnealing`、`Poly` 等)所在文件 | `mmcv/runner/hooks/lr_updater.py` (master 分支) |
| `CyclicLrUpdater` | 与动量调度配套的循环式 LR 更新器 | `mmcv/runner/hooks/lr_updater.py#L327` |
| `CyclicMomentumUpdater` | 循环式动量更新器,与 `CyclicLrUpdater` 协同使用 | `mmcv/runner/hooks/momentum_updater.py#L130` |
| MMDetection config 文档 | config 继承、`_delete_` 字段语义说明 | https://mmdetection.readthedocs.io/en/latest/config.html |

**上下游关系梳理:** 文档以 **MMCV** 为运行时底座(`mmcv.runner` 提供 Hook/LR updater/optimizer builder),以 **MMDetection** 作为注册方(`mmdet/core/optimizer/`、`mmdet/core/utils/`),通过 `OPTIMIZERS`/`OPTIMIZER_BUILDERS`/`HOOKS` 三个 Registry 实现"config 即代码"的可插拔机制。用户既可基于 PyTorch 原生 API 改动,也可注册第三方实现,变更范围局限于 config 文件。

**内部链接说明:** 文档文末未提供内部链接列表(题面标注"无")。本文档本身是 mmdetection tutorials 系列中的 **Tutorial 5**,与同系列教程(如前 4 篇及后续 Tutorial 6、7)构成递进关系,但原文未显式给出其内部索引 URL。

---

## 【使用方法】

### 启用方式总览(原文汇总)

| 定制项 | 启用位置 | 关键字段 |
|---|---|---|
| 切换 PyTorch 内置优化器 | config `optimizer` | `type='Adam'` 或 `type='SGD'` 等 |
| 注册自定义优化器 | `mmdet/core/optimizer/__init__.py` 或 config `custom_imports` | `@OPTIMIZERS.register_module()` |
| 差异化参数优化 | config `optimizer` + 自定义 `MyOptimizerConstructor` | `@OPTIMIZER_BUILDERS.register_module()` |
| 梯度裁剪 | config `optimizer_config` | `grad_clip=dict(max_norm=35, norm_type=2)` |
| 动量 cyclic 调度 | config `momentum_config` | `policy='cyclic', target_ratio=(0.85/0.95, 1)` |
| LR Poly 调度 | config `lr_config` | `policy='poly', power=0.9, min_lr=1e-4, by_epoch=False` |
| LR CosineAnnealing | config `lr_config` | `policy='CosineAnnealing', warmup='linear', warmup_iters=1000` |
| 训练/验证交替 | config `workflow` | `[('train', 1), ('val', 1)]` |
| 自定义 Hook | `mmdet/core/utils/__init__.py` 或 `custom_imports` | `@HOOKS.register_module()`,在 `before_run/.../after_iter` 中填逻辑 |

### 具体代码示例(原文逐字保留)

**1. 切换到 ADAM(原文):**
```python
optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
```

**2. 自定义优化器类骨架(原文):**
```python
from .registry import OPTIMIZERS
from torch.optim import Optimizer

@OPTIMIZERS.register_module()
class MyOptimizer(Optimizer):
    def __init__(self, a, b, c):
        ...
```

**3. 通过 custom_imports 手动导入(原文):**
```python
custom_imports = dict(imports=['mmdet.core.optimizer.my_optimizer'], allow_failed_imports=False)
```

**4. Cyclic 策略联动 LR + Momentum(原文):**
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

**5. 训练/验证交替 workflow(原文):**
```python
workflow = [('train', 1), ('val', 1)]
```

**6. 自定义 Hook 骨架(原文):**
```python
from mmcv.runner import HOOKS, Hook

@HOOKS.register_module()
class MyHook(Hook):
    def __init__(self, a, b):
        pass
    def before_run(self, runner): pass
    def after_run(self, runner): pass
    def before_epoch(self, runner): pass
    def after_epoch(self, runner): pass
    def before_iter(self, runner): pass
    def after_iter(self, runner): pass
```

### 文档不完整说明

原文在 "#### 2. Register the new hook" 段落中以 "so" 结尾被截断,Hook 注册的两种方式(修改 `__init__.py` 与 `custom_imports`)只给出了前者的一句话开头;`custom_imports` 用于 Hook 注册的具体写法未给出,该片段的剩余细节**原文未涉及**,请以仓库上游 commit 为准。
