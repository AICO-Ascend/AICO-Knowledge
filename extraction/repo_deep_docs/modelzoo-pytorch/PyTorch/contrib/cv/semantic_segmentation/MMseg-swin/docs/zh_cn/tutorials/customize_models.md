# 教程 4: 自定义模型

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/zh_cn/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/zh_cn/tutorials/customize_models.md

# 深度解读：MMSegmentation 自定义模型教程

## 【定位】

本教程是 MMSegmentation 的"教程 4：自定义模型"，系统说明如何通过注册器（registry）机制与配置文件，向 MMSegmentation 框架中新增/替换优化器、骨干网络（backbone）、解码头（decoder head）以及损失函数，从而实现模型组件层面的扩展与定制。

---

## 【技术要点】

1. **自定义优化器（Custom Optimizer）**：在 `mmseg/core/optimizer/my_optimizer.py` 中实现继承自 `torch.optim.Optimizer` 的子类，并用 `@OPTIMIZERS.register_module` 装饰；随后在 `mmseg/core/optimizer/__init__.py` 中导入，使注册器能够发现新模块，最后在配置文件中以 `optimizer = dict(type='MyOptimizer', a=..., b=..., c=...)` 形式调用。
2. **自定义优化器构造器（Optimizer Constructor）**：通过 `@OPTIMIZER_BUILDERS.register_module` 注册继承自 `object` 的构造器类，实现 `__init__(self, optimizer_cfg, paramwise_cfg=None)` 与 `__call__(self, model)` 方法，可对 BatchNorm 等层的 weight decay 等细粒度参数做差异化处理。
3. **自定义骨干网络（Backbone）**：在 `mmseg/models/backbones/mobilenet.py`（以 MobileNet 为例）中实现继承自 `nn.Module` 的类，使用 `@BACKBONES.register_module` 装饰；必须实现 `__init__`、`forward`（**注释明确指出 forward 应返回一个 tuple**）以及 `init_weights(pretrained=None)` 三个方法。
4. **自定义解码头（Decoder Head）**：在 `mmseg/models/decode_heads/psp_head.py`（以 PSPNet 为例）中实现继承自 `BaseDecodeHead` 的 `PSPHead`，需实现 `__init__(self, pool_scales=(1, 2, 3, 6), **kwargs)`、`init_weights()` 与 `forward(inputs)` 三个函数，并在 `mmseg/models/decode_heads/__init__.py` 中导入。
5. **自定义损失函数（Loss）**：在 `mmseg/models/losses/my_loss.py` 中通过 `@weighted_loss` 装饰器包装逐元素损失函数 `my_loss(pred, target)`，并用 `@LOSSES.register_module` 注册封装类 `MyLoss(nn.Module)`；调用时通过 `loss_decode=dict(type='MyLoss', loss_weight=1.0)` 在解码头中替换默认损失。
6. **通用三步接入流程**：每个新组件的接入都遵循同一模式——**（a）在对应子目录下创建实现文件** → **（b）在该子目录的 `__init__.py` 中执行 `from .xxx import Xxx`** → **（c）在配置文件的对应域中以 `type='Xxx'` 的字典形式引用**，依赖注册器自动发现并加载。

---

## 【关键机制与数据】

- **注册器机制（Registry）**：MMSegmentation 通过 `BACKBONES`、`HEADS`、`LOSSES`、`OPTIMIZERS`、`OPTIMIZER_BUILDERS` 等注册器实现"即插即用"的组件管理；新组件必须在所在目录的 `__init__.py` 中显式导入，注册器才能在构建模型时查找到它。
- **SGD 默认配置（原文）**：
  ```python
  optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)
  ```
- **Adam 备选配置（原文）**：文档明确指出"数值表现会掉点"（原文:），示例配置为：
  ```python
  optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
  ```
- **PSPNet 完整配置文件关键参数（原文）**：骨干使用 `ResNetV1c`（depth=50，num_stages=4，out_indices=(0,1,2,3)，dilations=(1,1,2,4)，strides=(1,2,1,1)，style='pytorch'，`contract_dilation=True`）；解码头 PSPHead 的 `in_channels=2048`、`in_index=3`、`channels=512`、`pool_scales=(1,2,3,6)`、`dropout_ratio=0.1`、`num_classes=19`、`align_corners=False`；损失采用 `CrossEntropyLoss`（`use_sigmoid=False`、`loss_weight=1.0`）；`norm_cfg = dict(type='SyncBN', requires_grad=True)`，`pretrained='pretrain_model/resnet50_v1c_trick-2cccc1ad.pth'`。
- **Loss 类签名（原文）**：`MyLoss` 接受 `reduction='mean'`、`loss_weight=1.0`；`forward` 接受 `pred, target, weight=None, avg_factor=None, reduction_override=None`，其中 `reduction_override` 必须属于 `(None, 'none', 'mean', 'sum')`；`weighted_loss` 装饰器可对计算损失时的每个样本做加权（原文）。
- **模块分类（原文）**：MMSegmentation 中主要有 2 种组件——**主干网络（backbone）** 与 **解码头（decoder head）**；前者负责卷积网络堆叠做特征提取（如 ResNet、HRNet），后者负责语义分割图的解码得到分割结果。
- **forward 输出约定（原文）**：骨干网络的 `forward` 方法注释明确指出"should return a tuple"，以兼容多尺度特征输出的下游使用。
- **解码头基类**：所有新建解码头均应继承 [`BaseDecodeHead`](https://github.com/open-mmlab/mmsegmentation/blob/master/mmseg/models/decode_heads/decode_head.py)。

---

## 【表格解读】

**原文无表格**。原文档以代码片段和说明性文字为主，未提供参数对照表或性能对比表。

---

## 【公式解读】

**原文无公式**。文档中未出现任何 LaTeX 公式或伪代码形式的数学表达式；唯一涉及计算的代码为示例性的逐元素损失 `loss = torch.abs(pred - target)`，属于代码片段而非公式。

---

## 【关联】

- **BaseDecodeHead 基类**：作为所有 decoder head 的父类，新解码头必须继承自它，PSPHead 即为典型示例。
- **EncoderDecoder 模型容器**：PSPNet 配置中以 `type='EncoderDecoder'` 作为整体分割网络的容器，将 `backbone` 与 `decode_head` 两个子模块组装在一起。
- **PyTorch 优化器体系**：文档指出"已经支持了 PyTorch 自带的全部优化器"，并引导用户参考 [PyTorch 官方 optim 文档](https://pytorch.org/docs/stable/optim.html?highlight=optim#module-torch.optim) 设置参数。
- **MMSegmentation 内部模块**：文档涉及到的关键文件包括 `mmseg/core/optimizer/`、`mmseg/core/optimizer/__init__.py`、`mmseg/models/backbones/__init__.py`、`mmseg/models/decode_heads/__init__.py`、`mmseg/models/losses/__init__.py`、`mmseg/models/builder.py`（隐含）等。
- **上下游教程关系**：作为"教程 4"，它通常位于"教程 1（配置文件）"、"教程 2（自定义数据集）"、"教程 3（自定义数据预处理/transform）"之后，承接前述教程构建的数据与配置，向下游衔接"教程 5（自定义运行流程/钩子）"、"教程 6（自定义评测指标）"等教程（基于 MMSegmentation 教程系列通用结构）。
- **论文引用**：PSPNet 解码头实现对应论文 [arXiv:1612.01105](https://arxiv.org/abs/1612.01105)。
- **内部链接**：原文未提供任何内部链接（标注为"无"），所有跳转均为外部链接（GitHub 仓库与 arXiv）。

---

## 【使用方法】

### 1. 启用自定义优化器（原文）
- 在 `mmseg/core/optimizer/my_optimizer.py` 中实现 `MyOptimizer(Optimizer)`，构造参数为 `a, b, c`，并使用 `@OPTIMIZERS.register_module` 装饰。
- 在 `mmseg/core/optimizer/__init__.py` 中添加 `from .my_optimizer import MyOptimizer`。
- 在配置文件中：
  ```python
  optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
  ```

### 2. 启用自定义优化器构造器（原文）
- 实现 `CocktailOptimizerConstructor` 类，构造时接收 `optimizer_cfg, paramwise_cfg=None`，`__call__(model)` 返回构造好的 optimizer。
- 使用 `@OPTIMIZER_BUILDERS.register_module` 装饰并在 `__init__.py` 中导入。

### 3. 启用自定义骨干网络（原文，以 MobileNet 为例）
- 文件路径：`mmseg/models/backbones/mobilenet.py`，装饰器 `@BACKBONES.register_module`。
- 在 `mmseg/models/backbones/__init__.py` 中添加 `from .mobilenet import MobileNet`。
- 配置文件引用：
  ```python
  model = dict(
      ...,
      backbone=dict(type='MobileNet', arg1=xxx, arg2=xxx),
      ...)
  ```

### 4. 启用自定义解码头（原文，以 PSPHead 为例）
- 文件路径：`mmseg/models/decode_heads/psp_head.py`，类签名 `class PSPHead(BaseDecodeHead)`，装饰器 `@HEADS.register_module()`。
- 在 `mmseg/models/decode_heads/__init__.py` 中导入该模块。
- 配置文件中的关键字段：`type='PSPHead'`、`in_channels=2048`、`in_index=3`、`channels=512`、`pool_scales=(1,2,3,6)`、`dropout_ratio=0.1`、`num_classes=19`、`loss_decode=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0)`。

### 5. 启用自定义损失函数（原文，以 MyLoss 为例）
- 文件路径：`mmseg/models/losses/my_loss.py`，使用 `@weighted_loss` 装饰 `my_loss(pred, target)`，并用 `@LOSSES.register_module` 注册 `MyLoss(nn.Module)`。
- 在 `mmseg/models/losses/__init__.py` 中添加 `from .my_loss import MyLoss, my_loss`。
- 在解码头组件的 `loss_decode` 域中引用：
  ```python
  loss_decode=dict(type='MyLoss', loss_weight=1.0)
  ```

### 6. 切换内置优化器（原文示例）
- 使用 Adam（原文提示"数值表现会掉点"）：
  ```python
  optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
  ```
- 参数可直接按 PyTorch 优化器文档设置，无需修改源码。
