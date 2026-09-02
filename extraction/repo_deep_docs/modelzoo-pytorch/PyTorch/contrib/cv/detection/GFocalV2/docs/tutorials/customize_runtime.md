# Tutorial 5: Customize Runtime Settings

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/GFocalV2/docs/tutorials/customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/GFocalV2/docs/tutorials/customize_runtime.md

# 深度解读:GFocalV2 — Tutorial 5: Customize Runtime Settings

## 【定位】

本文是 MMDetection / GFocalV2 训练流程定制系列(Tutorial 5)的运行时配置手册,聚焦**在不改训练主循环的前提下,通过 config + 注册机制 + hook 扩展点**,完成优化器、学习率策略、训练流程编排(workflow)与训练钩子(hook)的个性化定制。

---

## 【技术要点】

1. **PyTorch 原生优化器接入**:仅需修改 config 的 `optimizer` 字段即可换用任意 `torch.optim` 内置优化器,例如改用 `Adam` 时按原文给出的写法:`type='Adam', lr=0.0003, weight_decay=0.0001`(原文提示性能会下降较多);SGD 默认写法为 `type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001`。

2. **自研优化器三步接入法**:在 `mmdet/core/optimizer/` 下新建模块 → 用 `@OPTIMIZERS.register_module()` 装饰类 → 通过 `__init__.py` 导入 **或** config 中设置 `custom_imports = dict(imports=['mmdet.core.optimizer.my_optimizer'], allow_failed_imports=False)` 完成导入注册。注意原文强调:`mmdet.core.optimizer.my_optimizer.MyOptimizer` 这种"全路径直接导入"是**不被允许**的,只能导入到 package 层级。

3. **优化器构造器(Optimizer Constructor)用于参数级细粒度控制**:典型场景是 BatchNorm 等特定层不应用 weight decay,通过 `@OPTIMIZER_BUILDERS.register_module()` 注册一个 `__call__(self, model)` 接口的构造器类来实现。原文给出了签名模板(`def __init__(self, optimizer_cfg, paramwise_cfg=None)`),并指向 mmcv `default_constructor.py` 作为参考实现。

4. **训练稳定/加速三件套**(原文强调这些是 optimizer 自身不支持、需要通过 optimizer constructor 或 hook 实现的"tricks"):
   - **梯度裁剪**:`optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))`,`max_norm=35`、`norm_type=2`。
   - **Momentum schedule**:`policy='cyclic'`,`target_ratio=(0.85/0.95, 1)`,`cyclic_times=1`,`step_ratio_up=0.4`,与 LR scheduler 配对使用。
   - **LR schedule 支持**:默认是 1x step(即 `StepLRHook`);另有 `CosineAnnealing`(`warmup_iters=1000`、`warmup_ratio=1.0/10`、`min_lr_ratio=1e-5`)、`Poly`(`power=0.9`、`min_lr=1e-4`,`by_epoch=False`)、`Cyclic`(`target_ratio=(10, 1e-4)`)。

5. **Workflow 控制训练-验证交替**:默认 `workflow = [('train', 1)]`,改为 `[('train', 1), ('val', 1)]` 即可在每训练 1 个 epoch 后做 1 个验证 epoch。原文列出三条关键注意:
   - val 阶段**不更新**模型参数;
   - `total_epochs` 只控制训练 epoch 数,**不影响验证 workflow**;
   - `EvalHook` 是通过 `after_train_epoch` 触发的,workflow 加 val **不会**改变 `EvalHook` 行为,区别仅在于 runner 是否在每训练 epoch 后跑一次验证损失计算。

6. **自定义 Hook(自 v2.3.0 起支持 config 级启用)**:继承 `mmcv.runner.Hook`,实现 `before_run / after_run / before_epoch / after_epoch / before_iter / after_iter` 六个生命周期回调点,再用 `@HOOKS.register_module()` 装饰;通过修改 `mmdet/core/utils/__init__.py` 或 `custom_imports` 完成注册。

---

## 【关键机制与数据】

- **注册机制(Registry)**:GFocalV2/MMDetection 通过 `OPTIMIZERS`、`OPTIMIZER_BUILDERS`、`HOOKS` 三个注册表实现"装饰器 + import-time 自动注册",这是整个文档能"只改 config 不改训练主循环"的核心机制。
- **数据流路径(自定义优化器路径)**:`config.optimizer` → 触发对应 registry 查找 `type` 字段 → 实例化优化器/构造器 → 构造器从 `model` 抽取参数 → 返回最终 optimizer 对象供 runner 使用。
- **Hook 触发时机链**:`before_run → (before_epoch → before_iter → after_iter → after_epoch)*N → after_run`,与 workflow 编排的 (phase, epochs) 共同决定每步行为。
- **性能/经验性数据**:原文未给出 benchmark 数据,仅在 Adam 处提示"性能可能下降较多";在 3D 检测场景中报告 momentum schedule 与 LR schedule 配对可加速收敛。
- **版本依赖**:自定义 hook 的 config 化支持来自 issue/PR #3395,自 MMDetection v2.3.0 起提供。

---

## 【表格解读】

**原文无表格**。原文档所有参数与对比均以 Python config 代码块形式给出(已并入上文"技术要点"逐条复现),未出现 markdown/HTML 表格。

---

## 【公式解读】

**原文无 LaTeX/伪代码公式**。原文中可被视为"数学表达"的内容仅有以下参数化 config(均为 Python 字面量,而非公式):

- `target_ratio=(10, 1e-4)`(Cyclic LR 上下界比)
- `target_ratio=(0.85/0.95, 1)`(Cyclic Momentum 上下界比,等价于 `(0.8947..., 1)`,原文显式写作分数形式 `0.85/0.95`)
- `warmup_ratio=1.0/10`(warmup 初始 LR = base_lr × 1/10)
- `min_lr_ratio=1e-5`(CosineAnnealing 最小 LR 与 base_lr 之比)
- `power=0.9`(Poly schedule 的幂指数)

---

## 【关联】

- **与 Tutorial 1–4 的关系**:本文为 Tutorial 5,假定前序教程已覆盖数据 pipeline、模型、配置继承等基础(原文未给出 1–4 内容,本文不复述)。
- **与 GFocalV2 模型本体的关系**:GFocalV2 作为检测模型,训练时所有"优化器/LR/hook/workflow"改造均通过本文机制实现,模型文件本身无需修改。
- **上下游依赖**:
  - **上游**:MMCV 的 `torch.optim` 适配层(原文链接到 `mmcv/runner/optimizer/default_constructor.py`)。
  - **下游 hook 库**:`mmcv/runner/hooks/lr_updater.py`(StepLRHook、CosineAnnealing、Poly、CyclicLrUpdater)、`mmcv/runner/hooks/momentum_updater.py`(CyclicMomentumUpdater)。
  - **Config 文档**:`mmdetection.readthedocs.io/.../config.html`(解释 `_delete_=True` 等继承语义)。
- **文档本身存在截断**:原文在 Hook 注册章节(2. Register the new hook)未结束就被截断,因此"custom_imports 方式注册 hook"等后续步骤未在原文中给出。

---

## 【使用方法】

以下汇总原文给出的所有可直接复用的 config 片段(均逐字保留自原文):

**1. 切换 PyTorch 内置优化器**
```python
optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
```

**2. 自定义优化器导入(config 方式,免改 `__init__.py`)**
```python
custom_imports = dict(imports=['mmdet.core.optimizer.my_optimizer'], allow_failed_imports=False)
```

**3. 在 config 中启用自定义优化器**
```python
optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
```

**4. 梯度裁剪**
```python
optimizer_config = dict(
    _delete_=True, grad_clip=dict(max_norm=35, norm_type=2))
```

**5. Cyclic LR + Cyclic Momentum 联合调度**
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

**6. Poly LR**
```python
lr_config = dict(policy='poly', power=0.9, min_lr=1e-4, by_epoch=False)
```

**7. CosineAnnealing LR + linear warmup**
```python
lr_config = dict(
    policy='CosineAnnealing',
    warmup='linear',
    warmup_iters=1000,
    warmup_ratio=1.0 / 10,
    min_lr_ratio=1e-5)
```

**8. Workflow:每 epoch 训练后插入验证**
```python
workflow = [('train', 1), ('val', 1)]
```

**9. 自定义 Hook 模板**(原文截断于 hook 注册段落,此处给出实现模板,其余步骤请按原文 hook 注册小节继续)
```python
from mmcv.runner import HOOKS, Hook

@HOOKS.register_module()
class MyHook(Hook):
    def __init__(self, a, b): pass
    def before_run(self, runner): pass
    def after_run(self, runner): pass
    def before_epoch(self, runner): pass
    def after_epoch(self, runner): pass
    def before_iter(self, runner): pass
    def after_iter(self, runner): pass
```

**未涉及项**:CLI 命令行启动参数、分布式训练相关 runtime 设置,原文未涉及。
