# Tutorial 5: Customize Runtime Settings

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/customize_runtime.md

# 一体化深度解读：Tutorial 5 — Customize Runtime Settings

---

## 【定位】

这篇文档是 MMDetection 系列教程的第 5 篇（迁移至 YOLOX 仓库中的对应实现），系统性地指导用户如何在不改动训练框架主干代码的前提下，仅通过**配置文件 + 注册机制**来定制训练过程中的"运行时"行为——包括优化器与构造器、学习率 / 动量调度、训练–验证工作流以及训练钩子，从而在工程层面支撑不同检测模型（尤其是 YOLOX）对训练超参和流程的个性化需求。

---

## 【技术要点】

1. **PyTorch 原生优化器直接启用**：通过修改 config 中 `optimizer` 字段即可切换任意 PyTorch 内置优化器，例如 `Adam` 配 `lr=0.0003, weight_decay=0.0001`，所有参数透传自 `torch.optim` API。
2. **自定义优化器的"三步走"注册流程**：①在 `mmdet/core/optimizer/` 下新建实现文件并用 `@OPTIMIZERS.register_module()` 装饰类；②通过修改包内 `__init__.py` 或使用 config 的 `custom_imports` 主动 import 来纳入主命名空间；③在 config 中用 `type='MyOptimizer', a=..., b=..., c=...` 形式实例化。注意：**只能 import 包路径**，不能直接 import 类。
3. **优化器构造器（Optimizer Constructor）支持"参数级"细粒度配置**：例如 BatchNorm 层 weight decay 差异化设置，可参考 mmcv runner 的 `default_constructor.py` 模板实现自定义 `@OPTIMIZER_BUILDERS.register_module()` 类。
4. **梯度裁剪与动量调度两个常用 Trick**：通过 `optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))` 启用梯度裁剪；通过 `lr_config` + `momentum_config` 双 cyclic 策略（`target_ratio=(10, 1e-4)` 与 `target_ratio=(0.85/0.95, 1)`，`step_ratio_up=0.4`）加速 3D 检测收敛。
5. **训练调度策略支持多种 LR Scheduler**：默认 1× step schedule（调 `StepLRHook`），另支持 `poly`（`power=0.9, min_lr=1e-4, by_epoch=False`）和 `CosineAnnealing`（线性 warmup，`warmup_iters=1000, warmup_ratio=1.0/10, min_lr_ratio=1e-5`）。
6. **Workflow 控制训练 / 验证交错顺序**：默认 `[('train', 1)]`；改为 `[('train', 1), ('val', 1)]` 即可每训练 1 epoch 后跑 1 epoch 验证，且明确指出 **val 阶段不更新参数**、**`total_epochs` 只计训练 epoch**、**`EvalHook` 由 `after_train_epoch` 触发，与 val workflow 无关**——即两套 workflow 的实质差别只是 "runner 是否会在训练 epoch 结束时额外计算验证集 loss"。
7. **自定义 Hook 通过 `@HOOKS.register_module()` 注册**：可选择实现 `before_run / after_run / before_epoch / after_epoch / before_iter / after_iter` 六个回调点中的任意组合；自 v2.3.0 起无需改训练框架代码，仅 config 即可生效。

---

## 【关键机制与数据】

### 工作原理与数据流（原文梳理）

- **配置驱动的运行时注入**：所有自定义项（optimizer、optimizer constructor、hook、schedule、workflow）均不修改训练主体代码，而是通过 MMDetection 的"注册器 + 配置"机制在运行时被 `build_from_cfg` 实例化并装配到 runner。
- **注册器发现机制**：自定义类在被装饰为 `@OPTIMIZERS.register_module()` / `@OPTIMIZER_BUILDERS.register_module()` / `@HOOKS.register_module()` 后，需要被 import 进主命名空间才能被注册表发现。两种方式：(a) 修改所在包的 `__init__.py` 自动 import；(b) 在 config 里设 `custom_imports` 显式 import。
- **Import 粒度约束（原文）**：只 import 含目标类的**包**（如 `mmdet.core.optimizer.my_optimizer`），**不能直接 import 类本身**（`mmdet.core.optimizer.my_optimizer.MyOptimizer` 不被允许）。
- **梯度裁剪生效点**：通过 `optimizer_config.grad_clip` 配置，由 runner 在 optimizer.step() 之前对梯度施加约束；`max_norm=35, norm_type=2` 表明 L2 范数下裁剪到 35。
- **动量–学习率联动 cyclic 调度（原文）**：当 LR 从 `target_ratio` 的高位（10）按 `step_ratio_up=0.4` 比例升至峰值后衰减回低位（`1e-4`），动量同时从 `0.85/0.95 ≈ 0.8947` 反弹至 `1`，借助 LR 与 momentum 的反相位关系加速收敛。
- **Workflow 触发的 hook 差异（原文）**：`EvalHook` 走 `after_train_epoch`，所以无论是否配置 `('val', 1)`，`EvalHook` 都会在每个训练 epoch 后触发；配置 `('val', 1)` 的唯一额外效果是使 runner 在 `after_val_epoch` 上调用若干 hooks 并**计算验证集上的 loss**。
- **性能 / 数值数据（原文）**：仅有一处含数字的经验声明——"if you want to use ADAM (note that the performance could drop a lot)"，提示 Adam 替换默认 SGD 可能带来明显性能下降，但未给出具体数值；其他出现的 `lr=0.0003`、`weight_decay=0.0001`、`max_norm=35`、`power=0.9`、`min_lr=1e-4`、`warmup_iters=1000`、`warmup_ratio=1.0/10`、`min_lr_ratio=1e-5`、`cyclic_times=1`、`step_ratio_up=0.4`、`target_ratio=(10, 1e-4)`、`target_ratio=(0.85/0.95, 1)` 均为示例配置中的超参，文档**未给出**实际训练精度 / 速度等基准结果。

---

## 【表格解读】

**原文无表格。** 全文以"代码片段 + 解释段落"形式组织，未出现任何 markdown 表格、参数对比表或性能 benchmark 表。

---

## 【公式解读】

**原文无显式数学公式。** 全文既未出现 LaTeX 公式也未给出伪代码形式的数学表达式。可视为"纯工程配置文档"。

（若将 `target_ratio=(10, 1e-4)`、`target_ratio=(0.85/0.95, 1)` 等理解为 ratio 参数，则它们分别表示 LR 的高/低位比值与动量的反向变化比值，但文档未给出具体调度曲线公式。）

---

## 【关联】

文档未在文末提供该仓库内的"内部链接"列表（题目注明"内部链接: (无)"）。但从内容可梳理出文档所引用的**外部模块/特性**及上下游关系：

- **mmcv（OpenMMLab 计算机视觉基础库）**：
  - `mmcv.utils.build_from_cfg` —— 注册器实例化的核心工具，被 optimizer constructor 引入。
  - `mmcv.runner.optimizer.OPTIMIZER_BUILDERS / OPTIMIZERS` —— optimizer constructor 与 optimizer 的注册表宿主。
  - `mmcv.runner.HOOKS / Hook` —— 自定义 Hook 的注册表与基类。
  - `mmcv.runner.hooks.lr_updater.StepLRHook` / `CyclicLrUpdater` —— 默认与示例 LR 调度器。
  - `mmcv.runner.hooks.momentum_updater.CyclicMomentumUpdater` —— 与 `CyclicLrUpdater` 配对的动量调度器。
  - `mmcv.runner.optimizer.default_constructor` —— 默认 optimizer constructor 的参考模板。

- **MMDetection（mmdet）本体**：
  - `mmdet/core/optimizer/` —— 新建自定义优化器的默认目录约定。
  - `mmdet/core/utils/__init__.py` —— 新建自定义 Hook 时的注册导入点。
  - `mmdet.utils.get_root_logger` —— 自定义 optimizer constructor 中使用的日志工具。
  - `mmdet/core/optimizer/registry.OPTIMIZERS` —— 优化器本地注册器（继承自 mmcv）。

- **PyTorch 生态**：
  - `torch.optim.Optimizer` —— 自定义 optimizer 的父类。
  - `https://pytorch.org/docs/stable/optim.html` —— 切换原生优化器时的参数透传依据。

- **上游/下游教程**：
  - 文档以 "Tutorial 5" 编号出现，暗示存在 Tutorial 1–4；其中引用的"[config documentation]"指向 `config.html` 教程，主要用于解释 `_delete_=True` 覆盖语义——这是与**配置文件系统**的强耦合点。
  - 与"YOLOX 训练流程"的关联：本文档驻留在 `YOLOX_ID2833_for_PyTorch/docs/en/tutorials/` 下，意味着这些 runtime 自定义机制对 YOLOX 训练同样适用——特别是 LR scheduler（YOLOX 默认 cosine）、workflow 控制（YOLOX 默认 `train,1`）、以及 hook 扩展（YOLOX 中常见 EMA、MixUp 等通过 hook 实现）。

- **版本特性钩连**：
  - 明确标注 "MMDetection supports customized hooks in training (#3395) since v2.3.0"，将本文与 v2.3.0 这一 PR 绑定，说明早于该版本需修改代码而非改 config。

---

## 【使用方法】

以下均直接摘自原文，按场景分组列出启用方式与配置项：

### 1. 使用 PyTorch 内置优化器

```python
optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
```
仅需修改 config 的 `optimizer` 字段，`lr` 等任何 PyTorch `torch.optim` 支持的参数均可直接透传。

### 2. 注入自定义优化器（MyOptimizer）

**Step A — 实现**：在 `mmdet/core/optimizer/my_optimizer.py` 中：

```python
from .registry import OPTIMIZERS
from torch.optim import Optimizer

@OPTIMIZERS.register_module()
class MyOptimizer(Optimizer):
    def __init__(self, a, b, c):
        ...
```

**Step B — 注册**（二选一）：
- 方式 1：修改 `mmdet/core/optimizer/__init__.py`：
  ```python
  from .my_optimizer import MyOptimizer
  ```
- 方式 2：在 config 中显式 import：
  ```python
  custom_imports = dict(imports=['mmdet.core.optimizer.my_optimizer'],
                        allow_failed_imports=False)
  ```
  ⚠️ 仅 import 包路径，**不能** import `MyOptimizer` 类本身。

**Step C — 在 config 中启用**：
```python
optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)
# 改为
optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
```

### 3. 自定义 Optimizer Constructor（参数级细粒度配置）

模板示例：
```python
from mmcv.utils import build_from_cfg
from mmcv.runner.optimizer import OPTIMIZER_BUILDERS, OPTIMIZERS
from mmdet.utils import get_root_logger
from .my_optimizer import MyOptimizer

@OPTIMIZER_BUILDERS.register_module()
class MyOptimizerConstructor(object):
    def __init__(self, optimizer_cfg, paramwise_cfg=None):
        ...
    def __call__(self, model):
        return my_optimizer
```
参考模板见 mmcv `default_constructor.py`。

### 4. 启用梯度裁剪

```python
optimizer_config = dict(
    _delete_=True, grad_clip=dict(max_norm=35, norm_type=2))
```
若 config 继承自已有 `optimizer_config` 的 base config，需用 `_delete_=True` 覆盖冗余设置。

### 5. 启用 Cyclic LR + Momentum 联合调度（常用于 3D 检测）

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

### 6. 自定义训练调度（LR Scheduler）

- 默认（1× step）：调用 `StepLRHook`。
- Poly：
  ```python
  lr_config = dict(policy='poly', power=0.9, min_lr=1e-4, by_epoch=False)
  ```
- CosineAnnealing（带线性 warmup）：
  ```python
  lr_config = dict(
      policy='CosineAnnealing',
      warmup='linear',
      warmup_iters=1000,
      warmup_ratio=1.0 / 10,
      min_lr_ratio=1e-5)
  ```

### 7. 自定义 Workflow

- 仅训练：`workflow = [('train', 1)]`
- 训练–验证交错：`[('train', 1), ('val', 1)]`
- 注意：① val epoch 不更新参数；② `total_epochs` 只计训练 epoch，不影响 val workflow；③ `EvalHook` 由 `after_train_epoch` 触发，独立于 val workflow 配置；④ 与 `workflow=[('train', 1)]` 相比，`[('train', 1), ('val', 1)]` 的实质差异仅在于 runner 会在每训练 epoch 结束后计算验证集 loss。

### 8. 自定义训练 Hook

**Step A — 实现**（以 `mmdet/core/utils/my_hook.py` 为例）：
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
（六个回调点按需实现，对应 runner 的"运行 / epoch / iter"前后的不同阶段。）

**Step B — 注册**：与自定义 optimizer 同理，二选一：
- 修改 `mmdet/core/utils/__init__.py` 加入 `from .my_hook import MyHook`；
- 或在 config 用 `custom_imports` 主动 import 该模块。

**Step C — 在 config 中启用**（原文到此截断，Step C 的具体 config 写法**原文未涉及**，按惯例应为 `custom_hooks=[dict(type='MyHook', a=..., b=...)]` 形式，但文档未给出这一段）。

> **关于"原文未涉及"项**：以上步骤 8 的 "Step C 在 config 中启用 Hook 的具体写法"在本节选原文末尾被截断，**原文未给出**这一段配置示例；步骤 1–7 均为原文明确给出的可执行配置。文档亦未给出**命令行启动方式**（如 `tools/train.py` 的具体调用），这些内容属于 YOLOX 仓库下其它文档范畴，本篇文档未涉及。
