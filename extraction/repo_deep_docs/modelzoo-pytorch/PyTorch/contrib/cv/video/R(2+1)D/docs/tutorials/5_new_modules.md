# Tutorial 5: Adding New Modules

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/video/R(2+1)D/docs/tutorials/5_new_modules.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/video/R(2+1)D/docs/tutorials/5_new_modules.md

# 一体化深度解读:Tutorial 5: Adding New Modules

## 【定位】

这篇文档是 mmaction2 项目的扩展开发指南,系统性地介绍如何在该项目(尤其是 R(2+1)D 等视频识别模型所在的位置)中通过注册表机制自定义 **optimizer / optimizer constructor / 组件(backbone/head/loss) / 学习率调度器** 四大类对象,使得用户无需改动框架核心代码,仅通过新增文件 + 修改 config 即可接入新的算法实现。

---

## 【技术要点】

1. **统一注册表(Registry)模式**:所有可插拔对象都通过 `@XXX.register_module()` 装饰器注册到对应 builder(`OPTIMIZERS` / `OPTIMIZER_BUILDERS` / `BACKBONES` / `HEADS` / `LOSSES` / `HOOKS`),然后在 `__init__.py` 中 `from .xxx import Yyy` 让注册生效,最后在 config 文件里通过 `type='类名'` 字符串方式引用。
2. **Optimizer 自定义**:继承 `torch.optim.Optimizer`,在 `mmaction/core/optimizer/my_optimizer.py` 实现,并在 `mmaction/core/optimizer/__init__.py` 导入;框架已支持全部 PyTorch 内置 optimizer,例如切到 Adam 只需改 `optimizer` 字段。
3. **Optimizer Constructor 自定义**:用于做"参数级"的精细配置(例如对 BN 层或某层单独设置 lr/weight_decay),继承 `DefaultOptimizerConstructor` 并覆写 `add_params(self, params, module)` 方法;config 通过 `constructor='MyOptimizerConstructor'` + `paramwise_cfg=dict(fc_lr5=True)` 启用。
4. **新 Backbone 接入**:在 `mmaction/models/backbones/resnet.py` 定义 `nn.Module` 子类,需实现 `__init__`、`forward` (原文明确要求"should return a tuple")、`init_weights(pretrained=None)` 三个方法,典型例子是 TSN 用的 ResNet。
5. **新 Head 接入**:在 `mmaction/models/heads/tsn_head.py` 继承 [BaseHead](/mmaction/models/heads/base.py),并覆写 `init_weights(self)` 与 `forward(self, x)`,原文示例中 TSNHead 使用 `num_classes=400`、`in_channels=2048`。
6. **新 Loss 接入**:在 `mmaction/models/losses/my_loss.py` 同时实现函数版 `my_loss(pred, target)` 和类版 `MyLoss(nn.Module)`,导入时两者都要 import,使用方式如 `loss_bbox=dict(type='MyLoss')`。
7. **学习率调度器(updater)自定义**:在 `mmaction/core/lr` 下继承 `LrUpdaterHook`,**仅需覆写 `get_lr(self, runner, base_lr)`** 一方法即可;config 用 `policy='RelativeStep'` + 自定义参数(如 `steps=[20,40,60]` 与 `lrs=[0.1,0.01,0.001]`)触发。训练入口在 [`train.py`](/mmaction/apis/train.py) 中通过 `runner.register_training_hooks(...)` 注册。

---

## 【关键机制与数据】

### 4 类模型组件划分(原文)

> recognizer(整个识别流水线 = backbone + cls_head) / backbone(FCN 提特征,例如 ResNet、BNInception) / cls_head(分类头,通常 FC + pooling) / localizer(时序定位模型,目前有 BSN、BMN、SSN)

### 配置数值(原文给出,可直接复用)

- **SGD optimizer(原文)**: `optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)`
- **Adam optimizer(原文)**: `optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)`,原文同时注明"performance will drop a lot"
- **Optimizer + custom constructor(原文)**: `optimizer = dict(type='SGD', constructor='MyOptimizerConstructor', paramwise_cfg=dict(fc_lr5=True), lr=0.02, momentum=0.9, weight_decay=0.0001)`
- **TSNHead config(原文)**: `cls_head=dict(type='TSNHead', num_classes=400, in_channels=2048, arg1=xxx, arg2=xxx)`
- **Step LR(原文)**: `lr_config = dict(policy='step', step=[20, 40])`
- **RelativeStep LR(原文)**: `lr_config = dict(policy='RelativeStep', steps=[20, 40, 60], lrs=[0.1, 0.01, 0.001])`

### 训练 hook 注册数据流(原文)

```
runner.register_training_hooks(
    cfg.lr_config,
    optimizer_config,
    cfg.checkpoint_config,
    cfg.log_config,
    cfg.get('momentum_config', None))
```
这段代码位于 [`train.py`](/mmaction/apis/train.py),证明学习率 hook 的注册由 config `lr_config` 驱动,框架不写死策略。

### RelativeStep 的学习率选择逻辑(原文伪代码)

```python
progress = runner.epoch if self.by_epoch else runner.iter
for i in range(len(self.steps)):
    if progress < self.steps[i]:
        return self.lrs[i]
```
含义:根据当前 epoch(或 iter)与 `steps` 列表的比较,落在第 i 段就返回 `lrs[i]`;原文对该函数的约束是 `assert len(steps) == (len(lrs))`,保证步数与学习率一一对应。

---

## 【表格解读】

**原文无表格**。原文所有结构化信息都以代码块 / config 片段 / 项目符号列表呈现,而非 markdown 表格。唯一具有"对照"性质的对照是 4 类模型组件的列表(recognizer / backbone / cls_head / localizer),已在上文【关键机制与数据】中以原文文字形式还原。

---

## 【公式解读】

**原文无公式**。文中既无 LaTeX 数学式,也无伪代码数学表达式。最接近"公式"的是 `RelativeStepLrUpdaterHook.get_lr` 中的 if/for 逻辑(见上文),但那是 Python 选择结构而非数学公式,故不计入公式条目。

---

## 【关联】

依据文末/文中给定的内部链接,各节之间的依赖与上下游关系如下:

| 文档小节 | 涉及的内部链接 | 关系 |
|---|---|---|
| Customize Optimizer | `/mmaction/core/optimizer/copy_of_sgd.py` | CopyOfSGD 是该节的**示例实现**,演示如何基于 PyTorch Optimizer 写自定义 optimizer |
| Customize Optimizer Constructor | `/mmaction/core/optimizer/tsm_optimizer_constructor.py` | TSMOptimizerConstructor 是该节的**示例实现**,演示 `add_params` 覆写法 |
| Add new heads | `/mmaction/models/heads/base.py` | BaseHead 是新 head 类的**继承父类**,必须先存在才能让 TSNHead 类等正常工作 |
| Add new learning rate scheduler (updater) | `/mmaction/apis/train.py` | `train.py` 在该节作为**调用入口**,通过 `register_training_hooks` 把 `cfg.lr_config` 中的 policy 变成实际 hook |

纵向看,本文档处在"框架使用 → 框架扩展"的最末一环,与前序 tutorial 形成"先学会用、再学会改"的递进关系:自定义 optimizer / constructor 是对**训练侧**的扩展;backbone / head / loss 是对**模型侧**的扩展;lr_updater 则介于二者之间,既是 optimizer 的伴随策略,也通过 hook 体系与 train 流程耦合。

---

## 【使用方法】

以下内容全部来自原文,逐条列出对应配置/命令:

### 1. 启用自定义 Optimizer(原文)

- 在 `mmaction/core/optimizer/my_optimizer.py` 用 `@OPTIMIZERS.register_module()` 注册 `class MyOptimizer(Optimizer)`,构造函数接收 `a, b, c` 三个参数。
- 在 `mmaction/core/optimizer/__init__.py` 加一行 `from .my_optimizer import MyOptimizer`。
- 在 config 中:
  ```python
  optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
  ```
- 直接复用 PyTorch 内置 optimizer(原文示例):
  ```python
  optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
  ```
  其它参数遵循 [PyTorch optim API doc](https://pytorch.org/docs/stable/optim.html?highlight=optim#module-torch.optim)。

### 2. 启用自定义 Optimizer Constructor(原文)

- 在 `mmaction/core/optimizer/my_optimizer_constructor.py`:
  ```python
  @OPTIMIZER_BUILDERS.register_module()
  class MyOptimizerConstructor(DefaultOptimizerConstructor):
      ...
  ```
- 在 `mmaction/core/optimizer/__init__.py` 导入 `MyOptimizerConstructor`。
- 在 config 中通过 `constructor` 字段启用:
  ```python
  optimizer = dict(
      type='SGD',
      constructor='MyOptimizerConstructor',
      paramwise_cfg=dict(fc_lr5=True),
      lr=0.02,
      momentum=0.9,
      weight_decay=0.0001)
  ```

### 3. 接入新 Backbone(以 ResNet 为例,原文)

- 新建 `mmaction/models/backbones/resnet.py`,实现 `ResNet(nn.Module)` 的 `__init__(self, arg1, arg2)`、`forward(self, x)`(返回 tuple)、`init_weights(self, pretrained=None)`。
- 在 `mmaction/models/backbones/__init__.py` 加 `from .resnet import ResNet`。
- config 中使用:
  ```python
  model = dict(
      ...,
      backbone=dict(type='ResNet', arg1=xxx, arg2=xxx))
  ```

### 4. 接入新 Head(以 TSNHead 为例,原文)

- 新建 `mmaction/models/heads/tsn_head.py`,`class TSNHead(BaseHead)`,覆写 `__init__(self, arg1, arg2)`、`forward(self, x)`、`init_weights(self)`。
- 在 `mmaction/models/heads/__init__.py` 加 `from .tsn_head import TSNHead`。
- config 中使用:
  ```python
  model = dict(
      ...,
      cls_head=dict(
          type='TSNHead',
          num_classes=400,
          in_channels=2048,
          arg1=xxx,
          arg2=xxx))
  ```

### 5. 接入新 Loss(原文)

- 在 `mmaction/models/losses/my_loss.py` 同时定义函数 `my_loss(pred, target)` 与类 `MyLoss(nn.Module)`,前者用 `torch.abs(pred - target)` 计算 L1 类损失,并带 `assert pred.size() == target.size() and target.numel() > 0` 校验。
- 在 `mmaction/models/losses/__init__.py` 一次性导入两者:`from .my_loss import MyLoss, my_loss`。
- config 中替换对应损失字段:
  ```python
  loss_bbox=dict(type='MyLoss')
  ```

### 6. 启用学习率调度器(原文)

- **使用框架默认 step 策略**:
  ```python
  lr_config = dict(policy='step', step=[20, 40])
  ```
- **使用自定义 RelativeStep 策略**:在 `mmaction/core/lr` 下写 `RelativeStepLrUpdaterHook(LrUpdaterHook)`,只覆写 `get_lr(self, runner, base_lr)`,然后在 config 中:
  ```python
  lr_config = dict(policy='RelativeStep', steps=[20, 40, 60], lrs=[0.1, 0.01, 0.001])
  ```
- 训练侧由 [`train.py`](/mmaction/apis/train.py) 调用 `runner.register_training_hooks(cfg.lr_config, ...)` 完成绑定,无需额外命令。
- 原文未涉及 CLI 命令或脚本调用方式,因此除上述 config 字段外,无更多启动选项。
