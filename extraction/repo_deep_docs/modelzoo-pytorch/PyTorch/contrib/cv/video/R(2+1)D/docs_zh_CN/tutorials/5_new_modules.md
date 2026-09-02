# 教程 5：如何添加新模块

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/video/R(2+1)D/docs_zh_CN/tutorials/5_new_modules.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/video/R(2+1)D/docs_zh_CN/tutorials/5_new_modules.md

【定位】
这篇教程文档解决的是 **如何为 MMAction2 项目扩展和定制深度学习训练组件** 的问题，具体涵盖自定义优化器、自定义优化器构造器、新增 backbone / head / loss function，以及新增学习率调度器（updater hook）四类扩展能力，使开发者能够在不修改框架主干的前提下，按需注入自定义模块。

【技术要点】

1. **自定义优化器**：在 `mmaction/core/optimizer/my_optimizer.py` 中继承 `torch.optim.Optimizer`，使用 `@OPTIMIZERS.register_module()` 装饰器（来自 `mmcv.runner`）注册新优化器 `MyOptimizer`，并在 `mmaction/core/optimizer/__init__.py` 中 `from .my_optimizer import MyOptimizer` 导入。配置示例：`optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)`。参考实现：`CopyOfSGD`（`/mmaction/core/optimizer/copy_of_sgd.py`）。

2. **自定义优化器构造器**：在 `mmaction/core/optimizer/my_optimizer_constructor.py` 中继承 `DefaultOptimizerConstructor` 并重写 `add_params(self, params, module)` 方法，使用 `@OPTIMIZER_BUILDERS.register_module()` 装饰器。配置示例通过 `constructor` 字段指定，搭配 `paramwise_cfg=dict(fc_lr5=True)` 进行逐层细粒度参数设置。参考实现：`TSMOptimizerConstructor`（`/mmaction/core/optimizer/tsm_optimizer_constructor.py`）。

3. **添加新 backbone**：在 `mmaction/models/backbones/resnet.py` 中继承 `nn.Module`，使用 `@BACKBONES.register_module()` 装饰器，必须实现 `forward(self, x)`（应返回一个元组）和 `init_weights(self, pretrained=None)` 两个方法；随后在 `__init__.py` 中导入。配置示例通过 `model.backbone=dict(type='ResNet', arg1=xxx, arg2=xxx)` 使用。

4. **添加新 head**：在 `mmaction/models/heads/tsn_head.py` 中继承 `BaseHead`（`/mmaction/models/heads/base.py`），使用 `@HEADS.register_module()` 装饰器，必须重写 `init_weights(self)` 和 `forward(self, x)` 方法。配置示例：`cls_head=dict(type='TSNHead', num_classes=400, in_channels=2048, arg1=xxx, arg2=xxx)`。

5. **添加新 loss function**：在 `mmaction/models/losses/my_loss.py` 中既可实现函数式 `my_loss(pred, target)`，也可基于 `nn.Module` 实现 `MyLoss` 类，并使用 `@LOSSES.register_module()` 装饰器；在 `__init__.py` 中同时导入函数和类。配置示例：`loss_bbox=dict(type='MyLoss')`。

6. **添加新学习率调节器（updater hook）**：在 `mmaction/core/lr` 下编写自定义钩子，继承 `mmcv.LrUpdaterHook`，使用 `@HOOKS.register_module()` 装饰器；只需重写 `get_lr(self, runner, base_lr)` 方法，函数在每个训练周期/迭代前被调用并返回新学习率。配置示例：`lr_config = dict(policy='RelativeStep', steps=[20, 40, 60], lrs=[0.1, 0.01, 0.001])`。默认注册入口在 `/mmaction/apis/train.py` 的 `runner.register_training_hooks(...)` 中。

【关键机制与数据】

**工作原理 / 数据流：**
- **注册器机制**（Registry）是整篇文档的核心设计模式：`mmcv.runner` 暴露 `OPTIMIZERS`、`OPTIMIZER_BUILDERS`、`BACKBONES`、`HEADS`、`LOSSES`、`HOOKS` 等注册器，开发者用装饰器把类挂入注册表后，框架可通过配置中的 `type` 字符串按名查找并实例化。
- **优化器与构造器的分层关系**：构造器（`OPTIMIZER_BUILDERS`）负责把模型参数按规则分组并附加到优化器对象上（如 `paramwise_cfg` 控制 BatchNorm / FC 层的差异化 lr/weight_decay），而优化器（`OPTIMIZERS`）只负责具体的梯度更新逻辑。
- **模型组件 4 类划分**（原文）：识别器（recognizer = backbone + cls_head 流水线）、主干网络（backbone，FCN 特征提取器如 ResNet / BNInception）、分类头（cls_head，含池化的 FC 层）、时序检测器（localizer，已支持 BSN/BMN/SSN）。
- **Head 的 forward 约定**：原文 ResNet 示例的 `forward` 注释"应该返回一个元组"——表示 backbone 输出多尺度特征序列；head 则继承自 `BaseHead` 并重写 `init_weights` 与 `forward`。
- **LR hook 调度时机**：自定义 `RelativeStepLrUpdaterHook` 在每个训练周期/迭代前调用 `get_lr(runner, base_lr)`，通过 `runner.epoch`（按 epoch 调度）或 `runner.iter`（按迭代调度）读取当前进度。
- **训练入口装配**（原文 `train.py`）：`runner.register_training_hooks(cfg.lr_config, optimizer_config, cfg.checkpoint_config, cfg.log_config, cfg.get('momentum_config', None))` 把 lr_config 等训练期钩子统一挂到 runner 上。

**性能数据：**
- 原文未提供任何基准测试结果、性能数字或训练指标。

【表格解读】
原文无表格。

【公式解读】
原文无公式。

【关联】

- **`/mmaction/core/optimizer/copy_of_sgd.py`**（CopyOfSGD）：作为"自定义优化器"小节的具体参考实现，演示了如何继承 `torch.optim.Optimizer` 并通过 `@OPTIMIZERS.register_module()` 注册。
- **`/mmaction/core/optimizer/tsm_optimizer_constructor.py`**（TSMOptimizerConstructor）：作为"自定义优化器构造器"小节的具体参考实现，演示继承 `DefaultOptimizerConstructor` 并重写 `add_params` 以实现层间差异化参数配置。
- **`/mmaction/models/heads/base.py`**（BaseHead）：作为"添加新的 heads"小节的基类，所有自定义 cls_head（如 TSNHead）通过继承该类获得通用接口，再重写 `init_weights` 与 `forward` 即可。
- **`/mmaction/apis/train.py`**：作为"添加新的学习率调节器"小节的装配入口，其内部调用 `runner.register_training_hooks(...)` 把 `cfg.lr_config` 指定的 LR 调度钩子挂入训练 runner；上游关系上，`train.py` 依赖 `mmcv.runner` 提供的基础设施（如 `LrUpdaterHook`、`DefaultOptimizerConstructor`），下游关系上，所有自定义组件（backbone/head/loss/optimizer/updater）均需在各自 `__init__.py` 完成导入后才能被该训练入口通过配置 `type` 字段动态加载。
- **与外部依赖的关联**：自定义优化器参数设置"可参考 PyTorch API 文档"；所有支持的 LR 更新器"可参考 mmcv" 中 `mmcv/runner/hooks/lr_updater.py`，意味着本教程的能力边界受 `mmcv` 注册器体系约束。

【使用方法】

**启用方式 / 配置项：**

1. **注册新优化器**：将新文件放到 `mmaction/core/optimizer/` 下，类上加 `@OPTIMIZERS.register_module()`，并在 `mmaction/core/optimizer/__init__.py` 中 `from .your_file import YourClass`，随后在配置文件以 `optimizer = dict(type='YourClass', ...)` 使用。

2. **注册新优化器构造器**：将新文件放到 `mmaction/core/optimizer/` 下，类继承 `DefaultOptimizerConstructor` 并加 `@OPTIMIZER_BUILDERS.register_module()`，同样需在 `__init__.py` 导入；配置中使用方式：
   ```python
   optimizer = dict(
       type='SGD',
       constructor='YourConstructor',
       paramwise_cfg=dict(fc_lr5=True),
       lr=0.02,
       momentum=0.9,
       weight_decay=0.0001)
   ```

3. **注册新 backbone**：在 `mmaction/models/backbones/` 添加文件，继承 `nn.Module`，实现 `forward`（返回元组）和 `init_weights`，加 `@BACKBONES.register_module()`，并在 `__init__.py` 导入；配置：
   ```python
   model = dict(
       ...
       backbone=dict(type='YourBackbone', arg1=xxx, arg2=xxx))
   ```

4. **注册新 head**：在 `mmaction/models/heads/` 添加文件，继承 `BaseHead`（来自 `/mmaction/models/heads/base.py`），重写 `init_weights` 和 `forward`，加 `@HEADS.register_module()`，并在 `__init__.py` 导入；配置：
   ```python
   model = dict(
       ...
       cls_head=dict(type='YourHead', num_classes=400, in_channels=2048, arg1=xxx, arg2=xxx))
   ```

5. **注册新 loss**：在 `mmaction/models/losses/` 添加 `my_loss.py`，可选同时实现函数版本和 `nn.Module` 类版本，加 `@LOSSES.register_module()`，在 `__init__.py` 导入；配置示例：`loss_bbox=dict(type='MyLoss')`。

6. **注册新学习率调节器**：在 `mmaction/core/lr` 下编写继承 `mmcv.LrUpdaterHook` 的类，重写 `get_lr(self, runner, base_lr)`，加 `@HOOKS.register_module()`，并在对应 `__init__.py` 导入；配置文件替换：
   ```python
   lr_config = dict(policy='RelativeStep', steps=[20, 40, 60], lrs=[0.1, 0.01, 0.001])
   ```
   训练入口 `/mmaction/apis/train.py` 中的 `runner.register_training_hooks(...)` 会自动将其挂载到训练流程上。

**默认 LR 配置参考（无需自定义时）**：原文给出示例 `lr_config = dict(policy='step', step=[20, 40])` 作为通过配置直接切换调度策略的常规做法。
