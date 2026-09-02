# Tutorial 5: Customize Runtime Settings

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch/docs/tutorials/customize_runtime.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch/docs/tutorials/customize_runtime.md

# 一体化深度解读：Tutorial 5 - Customize Runtime Settings

## 【定位】
本文档是 MMDetection 教程系列的第五篇，系统性地介绍如何在训练运行时自定义**优化器、优化器构造器、训练调度（学习率策略）、工作流（train/val 切换）以及训练 Hook**，从而在不修改底层训练代码的前提下，通过配置文件灵活控制模型训练的运行时行为。

---

## 【技术要点】

### 1. 优化器切换——仅修改 config 即可
- 内置支持所有 PyTorch 优化器；改 `optimizer` 字段即可
- **Adam 示例**：`type='Adam', lr=0.0003, weight_decay=0.0001`（原文警告：性能可能下降很多）
- **SGD 示例**：`type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001`
- 学习率调整只需修改 `lr`，其余参数遵循 PyTorch 官方 optim API

### 2. 自定义优化器——三步注册机制
- **Step 1**：在 `mmdet/core/optimizer/my_optimizer.py` 中继承 `torch.optim.Optimizer`，用 `@OPTIMIZERS.register_module()` 注册，参数为 `a, b, c`
- **Step 2**：注册到命名空间，两种方式：
  - 修改 `mmdet/core/optimizer/__init__.py`：`from .my_optimizer import MyOptimizer`
  - 或在 config 中：`custom_imports = dict(imports=['mmdet.core.optimizer.my_optimizer'], allow_failed_imports=False)`
- ⚠️ 原文特别说明：**只能导入包路径 `mmdet.core.optimizer.my_optimizer`，不能直接导入类 `MyOptimizer`**（否则无法触发注册）
- **Step 3**：在 config 中使用 `optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)`

### 3. 自定义优化器构造器——参数细粒度控制
- 用于给某些层（如 BatchNorm）设置特殊的 weight decay 等
- 继承对象用 `@OPTIMIZER_BUILDERS.register_module()` 装饰，实现 `__init__(optimizer_cfg, paramwise_cfg=None)` 和 `__call__(model)`
- 默认构造器代码链接到 mmcv runner/optimizer/default_constructor.py 可作为模板

### 4. 附加训练技巧（梯度裁剪 & 动量调度）
- **梯度裁剪**：`optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))`
  - 当 config 继承自已设 `optimizer_config` 的 base config 时，需 `_delete_=True` 来覆盖
- **Cyclic LR**：`policy='cyclic', target_ratio=(10, 1e-4), cyclic_times=1, step_ratio_up=0.4`
- **Cyclic Momentum**：`policy='cyclic', target_ratio=(0.85/0.95, 1), cyclic_times=1, step_ratio_up=0.4`
- 常与 LR scheduler 配合使用（原文示例为 3D 检测中加速收敛）

### 5. 训练调度（学习率策略）
- 默认 **1x 步进调度**，调用 MMCV 的 `StepLRHook`
- **Poly**：`policy='poly', power=0.9, min_lr=1e-4, by_epoch=False`
- **CosineAnnealing**：`policy='CosineAnnealing', warmup='linear', warmup_iters=1000, warmup_ratio=1.0/10, min_lr_ratio=1e-5`

### 6. 工作流控制 & 自定义 Hook
- **默认工作流**：`workflow = [('train', 1)]` —— 仅训练 1 个 epoch
- **加入验证**：`[('train', 1), ('val', 1)]` —— 每训练 1 epoch 验证 1 epoch
  - ⚠️ 三个关键注意点（详见原文 Notes）：
    1. val epoch 中**模型参数不更新**
    2. `total_epochs` 只控制训练 epoch 数，**不影响验证工作流**
    3. `EvalHook` 由 `after_train_epoch` 触发，与验证 workflow 行为相互独立；两种 workflow 的**唯一差异**是 runner 是否在每个训练 epoch 后在验证集上计算 loss
- **自定义 Hook**（自 v2.3.0 起，#3395）：继承 `mmcv.runner.Hook`，使用 `@HOOKS.register_module()` 注册，可在 `before_run / after_run / before_epoch / after_epoch / before_iter / after_iter` 六个生命周期点注入逻辑

---

## 【关键机制与数据】

### 数据流与工作原理

**优化器注册机制**：
- 触发条件：模块被 import → `@OPTIMIZERS.register_module()` 自动将类写入注册表
- 查找时机：runner 初始化时根据 config 中的 `type` 字段从注册表取出对应类
- 因此"只能导入包、不能直接导入类"的限制是注册机制能正常工作的关键前提

**优化器构造器调用链**：
- runner → 解析 `optimizer_config` → 调用 `OPTIMIZER_BUILDERS` 中注册的构造器 → 构造器根据 `paramwise_cfg` 对模型参数分组 → 返回构建好的优化器实例

**Hook 生命周期**（按时间顺序）：
`before_run` → 循环 `before_epoch` → 循环 `before_iter` → 训练 → `after_iter` → 循环 `after_epoch` → 循环结束 → `after_run`

**工作流与 EvalHook 的解耦关系**：
- `EvalHook`：监听 `after_train_epoch`，因此无论 workflow 如何，都会执行
- 验证 workflow：影响 `after_val_epoch` 触发的 hooks
- 二者**不会相互影响**，可独立配置

### 性能/配置数据
原文明确给出的关键数值：
- Adam 初始 lr：`0.0003`，weight decay：`0.0001`（性能可能大幅下降）
- SGD 初始 lr：`0.02`，momentum：`0.9`，weight decay：`0.0001`
- 梯度裁剪阈值：`max_norm=35`，`norm_type=2`（即 L2 范数）
- Cyclic LR 目标比：`(10, 1e-4)`，cyclic 1 次，上升步占比 0.4
- Cyclic Momentum 目标比：`(0.85/0.95, 1)` —— 即基础动量/峰值动量 与 1 的比值
- CosineAnnealing：warmup 1000 iter，warmup_ratio=0.1，最小 lr 比例 1e-5
- Poly：power=0.9，min_lr=1e-4，按 iter 调度

---

## 【表格解读】

**原文无表格。** 文档以代码片段（Python config 字典）和文字说明为主，未呈现任何结构化对比表格。

---

## 【公式解读】

**原文无公式。** 文档未给出 LaTeX 数学表达式或伪代码形式的公式。所有内容都以 Python 字典形式的配置示例呈现。

---

## 【关联】

本文档是 MMDetection 教程系列的**第 5 篇**，处于"自定义"主题链中，与其他教程（Tutorial 1-4、6+）共同构成完整的自定义训练体系：

| 关联特性 / 模块 | 来源库 | 角色 |
|---|---|---|
| `OPTIMIZERS` 注册表 | `mmcv.runner.optimizer` | 优化器类注册中心 |
| `OPTIMIZER_BUILDERS` 注册表 | `mmcv.runner.optimizer` | 优化器构造器注册中心 |
| `HOOKS` 注册表 | `mmcv.runner` | Hook 类注册中心 |
| `StepLRHook` | `mmcv/runner/hooks/lr_updater.py` | 默认学习率调度器 |
| `CyclicLrUpdater` | `mmcv/runner/hooks/lr_updater.py:327` | 循环学习率调度器 |
| `CyclicMomentumUpdater` | `mmcv/runner/hooks/momentum_updater.py:130` | 循环动量调度器 |
| `EvalHook` | `mmcv/runner/hooks/eval.py` | 验证 hook，由 `after_train_epoch` 触发 |
| 默认优化器构造器 | `mmcv/runner/optimizer/default_constructor.py:11` | 自定义构造器的模板 |
| PyTorch optim API | pytorch.org | 内置优化器参考 |
| MMDetection v2.3.0（#3395） | mmdet | 支持自定义 hook 的版本起 |

**依赖关系**：本文档的几乎所有机制都建立在 MMCV 的注册器体系（Registry）与 Hook 机制之上；MMDetection 本身作为上层框架，仅做路径组织与默认配置封装。

---

## 【使用方法】

### 启用方式（基于 config 修改，无需改代码）

1. **切换 PyTorch 内置优化器**：直接在 config 中改 `optimizer` 字段
   ```python
   optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
   ```

2. **使用自定义优化器**：完成代码实现 + 注册导入 + config 引用三步

3. **梯度裁剪**：在 config 设置 `optimizer_config` 字段
   ```python
   optimizer_config = dict(_delete_=True, grad_clip=dict(max_norm=35, norm_type=2))
   ```

4. **切换学习率调度**：在 config 中修改 `lr_config`
   ```python
   lr_config = dict(policy='poly', power=0.9, min_lr=1e-4, by_epoch=False)
   ```

5. **启用动量调度**（需配合 LR scheduler）：
   ```python
   momentum_config = dict(policy='cyclic', target_ratio=(0.85/0.95, 1), cyclic_times=1, step_ratio_up=0.4)
   ```

6. **修改工作流**：
   ```python
   workflow = [('train', 1), ('val', 1)]
   ```

7. **使用自定义 Hook**：完成代码实现 + 注册导入后，在 config 的 `custom_hooks` 字段引用

> ⚠️ **原文备注**：文档在"Register the new hook"小节末尾被截断（原文最后一行 "so "），下文（自定义 hook 的具体 config 使用方法）原文未涉及，未给出后续内容。
