# Tutorial 4: Customize Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/en/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/en/tutorials/customize_models.md

# 一体化深度解读:Tutorial 4: Customize Models

## 【定位】
本篇文档是 MMSegmentation 面向用户的扩展开发教程,系统说明如何通过注册器 (registry) 机制,以最小侵入方式向框架注入自定义的**优化器、优化器构造器、骨干网络 (backbone)、分割解码头 (decode head)、损失函数**这五类组件,从而在不修改框架源码主干的条件下完成模型定制。

---

## 【技术要点】

1. **基于注册器 (registry) 的即插即用扩展**
   框架通过 `mmcv.runner.OPTIMIZERS`、`OPTIMIZER_BUILDERS`,以及 `mmseg.models.builder` 中的 `BACKBONES`、`HEADS`、`LOSSES` 五大注册器进行组件登记;**装饰器** (`@register_module`) 是唯一触发登记的机制,被登记的类即可通过配置文件 `type='ClassName'` 字段被加载。

2. **自定义优化器三步流程**
   - 在 `mmseg/core/optimizer/my_optimizer.py` 实现 `MyOptimizer(Optimizer)`,使用 `@OPTIMIZERS.register_module` 装饰。
   - 在 `mmseg/core/optimizer/__init__.py` 中 `from .my_optimizer import MyOptimizer` 以触发注册。
   - 在 config 中将 `optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)` 改为 `type='MyOptimizer'` 并填入自定义参数 `a`、`b`、`c`。
   - 原文给出 Adam 示例:`optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)`,且明确"框架已支持 PyTorch 全部内置优化器,只需修改 type 字段"。

3. **自定义优化器构造器 (optimizer constructor) 用于参数级 (param-wise) 精细调参**
   - 通过 `@OPTIMIZER_BUILDERS.register_module` 装饰的 `CocktailOptimizerConstructor` 实现 `__init__(self, optimizer_cfg, paramwise_cfg=None)` 与 `__call__(self, model)`,在 `__call__` 中遍历模型参数并返回最终 `optimizer`。
   - 典型场景:为 BatchNorm 层单独设置 `weight_decay`(批量归一化权重衰减通常需置零)。

4. **新增 backbone 的三步模板 (MobileNet 示例)**
   - 在 `mmseg/models/backbones/mobilenet.py` 中以 `@BACKBONES.register_module` 装饰继承自 `nn.Module` 的类,必须实现 `__init__(arg1, arg2)`、`forward(self, x)` (返回 `tuple`) 与 `init_weights(self, pretrained=None)`。
   - 在 `mmseg/models/backbones/__init__.py` 中 `from .mobilenet import MobileNet`。
   - 在 config 的 `model.backbone` 中以 `dict(type='MobileNet', arg1=xxx, arg2=xxx)` 形式调用。
   - **backbone 定义为"堆叠的卷积网络以提取特征图"**,代表为 ResNet、HRNet。

5. **新增 decode head 必须继承 `BaseDecodeHead`**
   - 新头放在 `mmseg/models/decode_heads/psp_head.py` (以 PSPNet 为例),使用 `@HEADS.register_module()` 装饰并继承 `BaseDecodeHead`;实现 `__init__(pool_scales=(1,2,3,6), **kwargs)`、`init_weights()`、`forward(inputs)`。
   - 在 `mmseg/models/decode_heads/__init__.py` 中 import 完成注册。
   - config 端把头挂到 `model.decode_head` 字段,通过 `type='PSPHead'` 选定。

6. **新增损失函数模板 (`MyLoss` + `weighted_loss`)**
   - 在 `mmseg/models/losses/my_loss.py` 中以 `@weighted_loss` 装饰函数式 `my_loss(pred, target)`,并以 `@LOSSES.register_module` 装饰 `MyLoss(nn.Module)` 类;类内构造器签名 `__init__(self, reduction='mean', loss_weight=1.0)`,`forward` 中需支持 `reduction_override` 三档 (`None/'none'/'mean'/'sum'`)。
   - 在 `mmseg/models/losses/__init__.py` 中 `from .my_loss import MyLoss, my_loss`。
   - 通过 config 的 `loss_decode=dict(type='MyLoss', loss_weight=1.0)` 接入 head;`loss_weight` 用于多损失加权平衡。

---

## 【关键机制与数据】

### 工作原理与数据流

- **注册器机制**:装饰器把类写入全局注册表 → `__init__.py` 的 import 语句是注册**触发器**(不导入就不会注册) → 配置文件中 `type='ClassName'` 字符串作为 key 在注册表中查找并实例化。这是 OpenMMLab 系列框架统一的组件加载范式。
- **config 驱动模型构建**:`model = dict(type='EncoderDecoder', backbone=..., decode_head=..., ...)` 这种嵌套字典结构描述了从 backbone 抽特征 → head 解码 → loss 计算的完整数据通路。
- **head 数据流细节 (原文 PSPNet 配置)**:backbone `ResNetV1c` 输出 4 个尺度 (`out_indices=(0,1,2,3)`),PSPHead 通过 `in_index=3` 选取第 4 个 (即最深) 特征图 (其 `in_channels=2048`),经 4 个不同 `pool_scales=(1,2,3,6)` 的 PPM 金字塔池化后汇聚到 `channels=512` 的解码通道,`dropout_ratio=0.1`,最终 `num_classes=19` 类别预测,`align_corners=False` 控制上采样插值。
- **多任务损失平衡机制**:`loss_weight` 标量乘到 `my_loss` 输出上,实现"按元素加权"的整体平衡;`reduction_override` 在训练/验证不同阶段切换 reduction 方式。
- **性能数据 (原文):** 未给出任何 benchmark 数字。仅一处定性描述——使用 Adam 代替 SGD"performance will drop a lot"(无具体数值)。

---

## 【表格解读】

**原文无表格**(整篇文档全部以代码块 + 散文叙述呈现,无任何 markdown 表格结构)。

---

## 【公式解读】

**原文无公式**(文档内仅包含 Python 代码示例与散文说明,无任何数学公式或伪代码)。

---

## 【关联】

- **与"教程 1-3"系列构成方法论闭环**:本篇文档 (`Tutorial 4: Customize Models`) 是 MMSegmentation 模型自定义系列教程的第 4 篇,与"如何运行/配置/数据准备/可视化"等教程共同构成完整的用户入门闭环。本仓库路径 `BiseNetV1_for_PyTorch/docs/en/tutorials/customize_models.md` 即说明该文档被同步进了 BiseNetV1 模型工程内。
- **上游依赖 (mmcv)**:所有注册器 (`OPTIMIZERS`、`OPTIMIZER_BUILDERS`) 均来自 `mmcv.runner`,说明 MMSegmentation 是 OpenMMLab 生态中**底层依赖 mmcv** 的项目,共享 mmcv 的 runner/registry 基础设施。
- **下游被定制对象**:文档提到的 5 个可定制点恰好覆盖了**训练侧** (optimizer/optimizer constructor) 与**模型侧** (backbone/head/loss) 三大环节,任何修改都通过 config 文件接入,不影响其他模块。
- **BaseDecodeHead**:作为所有新分割解码头的基类,其内部已实现 `loss_decode` 字段读取与多损失加权逻辑,自定义 head 只需实现少量方法即可复用整套训练流程。
- **PSPNet 引用**:文档以 PSPNet (arXiv:1612.01105) 作为新 head 的演示范例,与 `BaseDecodeHead` 抽象形成"基类 + 经典实现"的演示组合。
- **文末/文内链接**:
  - PyTorch 官方 optim API 文档 `https://pytorch.org/docs/stable/optim.html?highlight=optim#module-torch.optim`(作为 optimizer 参数设置的官方参考)。
  - `BaseDecodeHead` 源码 `https://github.com/open-mmlab/mmsegmentation/blob/master/mmseg/models/decode_heads/decode_head.py`。
  - PSPNet 论文 `https://arxiv.org/abs/1612.01105`。
  - (本任务提供的内部链接清单标注为"无"。)

---

## 【使用方法】

**启用方式 (统一范式: 实现 → 注册 → config 调用)**

- **自定义优化器**:
  1. 在 `mmseg/core/optimizer/` 下新建文件,以 `@OPTIMIZERS.register_module` 装饰继承 `torch.optim.Optimizer` 的类;
  2. 在同目录 `__init__.py` 中 `from .my_optimizer import MyOptimizer`;
  3. 在 config 中将 `optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)` 替换为 `optimizer = dict(type='MyOptimizer', a=..., b=..., c=...)`。

- **使用 PyTorch 内置优化器 (无需注册)**:
  - SGD: `optimizer = dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)`
  - Adam: `optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)`

- **自定义优化器构造器** (参数级调参,例如为 BN 层设置不同 weight_decay):
  - 在 `mmseg/core/optimizer/` 下新建文件,装饰 `@OPTIMIZER_BUILDERS.register_module`,实现 `__init__(self, optimizer_cfg, paramwise_cfg=None)` 和 `__call__(self, model)`,在 `__call__` 中构造并返回优化器。

- **新增 backbone** (MobileNet 模板):
  1. 在 `mmseg/models/backbones/mobilenet.py` 中用 `@BACKBONES.register_module` 装饰 `MobileNet(nn.Module)`,实现 `__init__`、`forward` (返回 tuple)、`init_weights(pretrained=None)`;
  2. 在 `mmseg/models/backbones/__init__.py` 中 `from .mobilenet import MobileNet`;
  3. config 中:`model = dict(..., backbone=dict(type='MobileNet', arg1=xxx, arg2=xxx), ...)`。

- **新增 decode head** (PSPHead 模板):
  1. 在 `mmseg/models/decode_heads/psp_head.py` 中 `@HEADS.register_module()` 装饰继承 `BaseDecodeHead` 的类,实现 `__init__(pool_scales=(1,2,3,6), **kwargs)`、`init_weights`、`forward`;
  2. 在同目录 `__init__.py` 中 import;
  3. config 中完整示例 (原文):
     ```python
     norm_cfg = dict(type='SyncBN', requires_grad=True)
     model = dict(
         type='EncoderDecoder',
         pretrained='pretrain_model/resnet50_v1c_trick-2cccc1ad.pth',
         backbone=dict(
             type='ResNetV1c',
             depth=50,
             num_stages=4,
             out_indices=(0, 1, 2, 3),
             dilations=(1, 1, 2, 4),
             strides=(1, 2, 1, 1),
             norm_cfg=norm_cfg,
             norm_eval=False,
             style='pytorch',
             contract_dilation=True),
         decode_head=dict(
             type='PSPHead',
             in_channels=2048,
             in_index=3,
             channels=512,
             pool_scales=(1, 2, 3, 6),
             dropout_ratio=0.1,
             num_classes=19,
             norm_cfg=norm_cfg,
             align_corners=False,
             loss_decode=dict(
                 type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0)))
     ```

- **新增 loss** (MyLoss 模板):
  1. 在 `mmseg/models/losses/my_loss.py` 中用 `@weighted_loss` 装饰函数 `my_loss(pred, target)`,用 `@LOSSES.register_module` 装饰 `MyLoss(nn.Module)` 类 (构造器含 `reduction='mean'`、`loss_weight=1.0`,`forward` 支持 `reduction_override` ∈ {None, 'none', 'mean', 'sum'});
  2. 在 `mmseg/models/losses/__init__.py` 中 `from .my_loss import MyLoss, my_loss`;
  3. config 中修改 head 的 `loss_decode` 字段:`loss_decode=dict(type='MyLoss', loss_weight=1.0)`,`loss_weight` 用以在多损失间做平衡。

**命令行启动方式**:原文未涉及任何具体训练/测试命令行参数 (如 `python tools/train.py ...`),仅说明配置文件层面的修改方法。
