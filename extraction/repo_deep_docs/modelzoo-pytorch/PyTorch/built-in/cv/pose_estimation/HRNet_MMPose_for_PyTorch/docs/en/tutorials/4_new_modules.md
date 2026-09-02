# Tutorial 4: Adding New Modules

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/en/tutorials/4_new_modules.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/en/tutorials/4_new_modules.md

# PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/en/tutorials/4_new_modules.md 深度解读

## 【定位】

本教程系统阐述如何在 MMPose 框架中**扩展自定义模块**，覆盖优化器、优化器构造器、模型组件（骨干网络/关键点头）以及损失函数四大定制维度，目的是让用户在不修改框架核心代码的前提下，通过注册机制与配置文件完成新模块的接入与复用。

## 【技术要点】

1. **注册机制驱动扩展**：所有自定义模块均依赖装饰器注册，`@OPTIMIZERS.register_module()`（优化器）、`@OPTIMIZER_BUILDERS.register_module()`（优化器构造器）、`@BACKBONES.register_module()`（骨干网络）、`@HEADS.register_module()`（关键点头）、`@LOSSES.register_module()`（损失函数），配合对应包的 `__init__.py` 导入即可被框架自动发现。

2. **优化器四级定制路径**：
   - 在 `mmpose/core/optimizer/my_optimizer.py` 中实现类；
   - 在 `mmpose/core/optimizer/__init__.py` 中导入；
   - 在 `optimizer = dict(type='XXX', ...)` 配置字段中按需切换；
   - 框架已默认可直接切换所有 PyTorch 原生优化器，例如 Adam：`dict(type='Adam', lr=0.0003, weight_decay=0.0001)`，SGD：`dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)`。

3. **模型组件三类职责划分**：detectors 负责整体流程（典型如 TopDown），backbone 负责特征提取（"usually an FCN network to extract feature maps, e.g., ResNet, HRNet"），keypoint_head 负责姿态估计任务（"usually contains some deconv layers"），并各自有专属注册器与子目录。

4. **关键点头对外接口约束**：继承 `nn.Module`，必须重写 `forward(self, x)`（"should return a tuple" for backbone）和 `init_weights(self)`，backbone 的 `init_weights` 还接受 `pretrained` 参数以适配预训练权重加载。

5. **损失函数加权策略**：通过 `weighted_loss` 装饰器可使损失对每个元素加权；自定义 `MyLoss` 内部维护 `use_target_weight` 标志，遍历 `num_joints` 个关节点并在最后 `return loss / num_joints` 实现按关节数归一化。

6. **优化器构造器的细粒度控制**：`CocktailOptimizerConstructor` 类型通过 `__call__(self, model)` 暴露对模型参数分组的接口，用于解决类似 BatchNorm 层不应与常规层共享相同 weight decay 等参数特异性设置问题。

## 【关键机制与数据】

**工作原理（基于注册中心 + 配置驱动）**：MMPose 的模块化体系由 mmcv 的 build_from_cfg 机制承担装配职责——模块实现只是普通的 PyTorch 类，必须在对应子目录的 `__init__.py` 中显式导入，框架运行时读取配置文件中 `type` 字段的字符串名，再通过注册表查表实例化，从而做到"代码-配置分离"。

**数据流（以 loss 计算为例）**：
- 输入 `output` 与 `target` 被 `reshape((batch_size, num_joints, -1))` 后按关节切分为 `split(1, 1)`；
- 在循环中逐关节取出 `heatmap_pred` / `heatmap_gt`；
- 根据 `use_target_weight` 决定是否乘以 `target_weight[:, idx]` 后送入 `self.criterion`（即 `my_loss`，先取 `torch.abs(pred - target)` 再 `torch.mean`，等价于 MAE/L1 损失）；
- 最终累加并除以 `num_joints` 得到单张图的平均关节损失。

**性能/参数数据（原文）**：
- 原文：SGD 示例 `lr=0.02, momentum=0.9, weight_decay=0.0001`；
- 原文：Adam 示例 `lr=0.0003, weight_decay=0.0001`，并附带说明"though the performance will drop a lot"——表明原文未提供具体数值，仅给出定性表述。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无独立公式段落，但关键点头损失模块隐含一个聚合公式，可还原为：

$$
\mathcal{L} = \frac{1}{N_j} \sum_{i=1}^{N_j} \frac{1}{N_{pix}} \sum_{(x,y)} \big| \hat{H}_i(x,y) - H_i(x,y) \big|
$$

其中：
- $N_j = \texttt{num\_joints}$：关节数；分母与之相乘实现逐关节归一化，对应原文 `return loss / num_joints`。
- $(x,y)$：热图上的像素位置，由 `output.reshape((batch_size, num_joints, -1)).split(1, 1)` 展平后遍历。
- $\hat{H}_i$ 与 $H_i$：第 $i$ 个关节的预测热图与真值热图，由 `heatmap_pred` 与 `heatmap_gt` 给出。
- $\text{use\_target\_weight}$ 为真时，$\hat{H}_i$ 与 $H_i$ 同时乘以 `target_weight[:, idx]`，实现可见性加权。
- 内层 $\frac{1}{N_{pix}} \sum |\cdot|$ 对应 `torch.abs(pred - target).mean()`（即 MAE/L1 损失）。

## 【关联】

本教程定位为 MMPose 扩展体系的**总入口**，与仓库其他教程存在明确上下游关系：
- 与同目录 **Tutorial 1~3**（数据流、配置文件解读、模型自定义等）形成 MMPose 整体上手路径——本篇是其"模块扩展"分支；
- 引用了 **mmcv** 生态的 `OPTIMIZERS`、`OPTIMIZER_BUILDERS`、`build_from_cfg` 等基元，说明 MMPose 严重依赖 MMCV 注册中心，可对应仓库中 `mmcv/runner/optimizer` 相关源码；
- 涉及的 PyTorch 官方优化器 API 链接 `https://pytorch.org/docs/stable/optim.html` 与本仓代码无直接内部链接，但提供了所有 PyTorch 原生优化器切换的可行性；
- 上下游模块在文末以下游消费方式呈现：自定义结果通过 `optimizer`、`model`、`loss_keypoint` 等配置字段被上层训练流程与 TopDown detector 装配使用，本身不提供对外导出链接。

## 【使用方法】

**启用自定义优化器（配置驱动）**：
```python
optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
# 或直接切换为 PyTorch 原生:
optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
```

**启用自定义优化器构造器**：在 `mmpose/core/optimizer/` 下新建文件并以 `@OPTIMIZER_BUILDERS.register_module()` 装饰类，在 `__init__.py` 导入，然后在配置 `optimizer` 字段中以 `type` 引用即可，原文未给出具体 config 写法。

**启用自定义骨干网络 / 关键点头（top-down 2D 姿态估计）**：
1. 在 `mmpose/models/backbones/my_model.py` 与 `mmpose/models/keypoint_heads/my_head.py` 中分别实现并用 `@BACKBONES.register_module()` / `@HEADS.register_module()` 注册；
2. 在对应 `__init__.py` 中加入 `from .my_model import MyModel` 与 `from .my_head import MyHead`；
3. 在配置文件中按 TopDown detector 范式编写：
   ```python
   model = dict(
       type='TopDown',
       backbone=dict(type='MyModel', arg1=xxx, arg2=xxx),
       keypoint_head=dict(type='MyHead', arg1=xxx, arg2=xxx))
   ```

**启用自定义损失**：
1. 在 `mmpose/models/losses/my_loss.py` 实现函数 `my_loss` 与类 `MyLoss`，类用 `@LOSSES.register_module()` 装饰；
2. 在 `mmpose/models/losses/__init__.py` 中加入 `from .my_loss import MyLoss, my_loss`；
3. 在模型配置中改写 `loss_keypoint` 字段：
   ```python
   loss_keypoint = dict(type='MyLoss', use_target_weight=False)
   ```
