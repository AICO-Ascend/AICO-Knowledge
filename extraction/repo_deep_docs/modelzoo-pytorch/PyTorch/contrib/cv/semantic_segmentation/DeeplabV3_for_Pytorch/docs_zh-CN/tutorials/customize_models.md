# 教程 4: 自定义模型

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs_zh-CN/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs_zh-CN/tutorials/customize_models.md

# 一体化深度解读：教程 4 自定义模型

---

## 【定位】

这篇文档解决"如何向 MMSegmentation 框架扩展自定义组件"的问题——围绕**优化器、优化器构造器、主干网络 (backbone)、解码头 (decoder head)、损失函数**这五大可定制点，给出从代码注册到配置文件调用的端到端扩展范式。

---

## 【技术要点】

1. **自定义优化器 (MyOptimizer)**：通过 `@OPTIMIZERS.register_module` 装饰器将继承自 `torch.optim.Optimizer` 的类注册到 `mmcv.runner.OPTIMIZERS` 注册表；随后在 `mmseg/core/optimizer/__init__.py` 中导入，配置文件中改 `optimizer` 域的 `type` 即可切换。原文示例参数：`SGD (lr=0.02, momentum=0.9, weight_decay=0.0001)` 与 `Adam (lr=0.0003, weight_decay=0.0001)`。

2. **定制优化器构造器 (CocktailOptimizerConstructor)**：通过 `@OPTIMIZER_BUILDERS.register_module` 装饰器注册到 `OPTIMIZER_BUILDERS`，用于对模型不同层（如 BatchNorm）做**细粒度**的参数差异化配置（如权重衰减分组）。

3. **新增主干网络**：在 `mmseg/models/backbones/` 下新建文件，需实现 `__init__(arg1, arg2)`、`forward(x)`（注释明确要求返回 tuple）、`init_weights(pretrained=None)` 三个方法；随后在 `backbones/__init__.py` 中导入，在配置文件中通过 `model.backbone.type='MobileNet'` 启用。

4. **新增解码头 (PSPHead)**：必须继承基类 `BaseDecodeHead`，需实现 `__init__`、`init_weights`、`forward(inputs)` 三个函数；PSPHead 特有参数 `pool_scales=(1, 2, 3, 6)`；完整配置中 `in_channels=2048, channels=512, num_classes=19, dropout_ratio=0.1, in_index=3`。

5. **新增损失函数 (MyLoss)**：通过 `@LOSSES.register_module` 与 `@weighted_loss` 双装饰器模式，`weighted_loss` 装饰器负责对每个样本做加权；类接受 `reduction` 与 `loss_weight` 两个核心参数；在解码头中通过 `loss_decode=dict(type='MyLoss', loss_weight=1.0)` 启用。

6. **注册器 (Registry) 发现机制**：所有扩展都遵循"**装饰器注册 → 包 `__init__.py` 导入 → 配置文件 `type` 字段切换**"的统一三步模式，这是 MMSegmentation 配置驱动 (config-driven) 架构的核心。

---

## 【关键机制与数据】

**工作原理：装饰器 + 注册表 + 配置驱动**
- 原文：`@OPTIMIZERS.register_module`、`@OPTIMIZER_BUILDERS.register_module`、`@BACKBONES.register_module`、`@HEADS.register_module`、`@LOSSES.register_module` —— 五大注册器分别承担不同组件的发现与加载。
- 原文：`from ..registry import BACKBONES` 与 `from ..builder import LOSSES` 表明 BACKBONES 取自 `registry`，而 LOSSES 取自 `builder`，二者来源不同。
- 原文：`forward(self, x): # should return a tuple` —— 明确主干网络的 forward 必须返回 tuple，对应 MMSegmentation 多阶段特征图的输出约定。
- 原文：`assert pred.size() == target.size() and target.numel() > 0` —— 损失函数内部对输入张量形状与样本数量的断言。

**性能/数值数据**（仅原文出现的）：
- 原文：SGD 优化器 `lr=0.02, momentum=0.9, weight_decay=0.0001`（示例配置文件）。
- 原文：Adam 优化器 `lr=0.0003, weight_decay=0.0001`（示例配置文件），原文同时指出"数值表现会掉点"。
- 原文：PSPHead 配置中 `pool_scales=(1, 2, 3, 6)`、`dropout_ratio=0.1`、`num_classes=19`、`in_channels=2048`、`channels=512`、`in_index=3`。
- 原文：主干预训练权重 `'pretrain_model/resnet50_v1c_trick-2cccc1ad.pth'`、norm 配置 `dict(type='SyncBN', requires_grad=True)`、`out_indices=(0, 1, 2, 3)`、`dilations=(1, 1, 2, 4)`、`strides=(1, 2, 1, 1)`、`style='pytorch'`、`contract_dilation=True`。

**数据流**：注册器发现 → 包 `__init__.py` 导入 → 配置文件 `type` 字段引用 → `build_from_cfg` 实例化 → 进入 `EncoderDecoder` 等模型组装。

---

## 【表格解读】

**原文无表格**。原文以代码块、配置片段和列表形式呈现内容，未提供任何 markdown/HTML 形式的参数表或对比表。

---

## 【公式解读】

**原文无公式**。原文仅涉及代码片段（Python 类定义、装饰器、配置文件），未出现 LaTeX 公式或伪代码形式的公式。唯一可被视为"准公式"的是损失计算式 `loss = torch.abs(pred - target)`，但该表达式仅作为 `@weighted_loss def my_loss` 函数体内部的代码行，并非独立公式，故不单列。

---

## 【关联】

本教程作为"教程 4"位于 MMSegmentation 文档系列，向上承接基础的模型构建流程，向下与以下模块/特性形成耦合：

- **上游依赖**：
  - `mmcv.runner.OPTIMIZERS` / `mmcv.runner.OPTIMIZER_BUILDERS` / `mmcv.utils.build_from_cfg` —— 来自 mmcv 框架，是注册机制的基础设施。
  - `mmseg.models.decode_heads.decode_head.BaseDecodeHead` —— 所有解码头继承的基类（链接：`https://github.com/open-mmlab/mmsegmentation/blob/master/mmseg/models/decode_heads/decode_head.py`）。
  - `mmseg.models.losses.utils.weighted_loss` —— 损失函数的样本加权装饰器。
  - `mmseg.models.registry.BACKBONES` 与 `mmseg.models.builder.LOSSES` —— 文档显示二者**来源不同**（registry vs builder）。

- **同级引用**：
  - PSPNet 解码头的设计参照论文 `arxiv.org/abs/1612.01105`。
  - PyTorch 官方优化器文档：`pytorch.org/docs/stable/optim.html?highlight=optim#module-torch.optim`，作为参数设置参考。

- **下游应用**：自定义完成后均通过**配置文件的对应 `type` 字段**激活：`optimizer.type`、`model.backbone.type`、`model.decode_head.type`、`model.decode_head.loss_decode.type`。

- **文件路径关联**（原文内部提及的具体位置）：
  - `mmseg/core/optimizer/my_optimizer.py`
  - `mmseg/core/optimizer/__init__.py`
  - `mmseg/models/backbones/mobilenet.py`
  - `mmseg/models/backbones/__init__.py`
  - `mmseg/models/decode_heads/psp_head.py`
  - `mmseg/models/decode_heads/__init__.py`
  - `mmseg/models/losses/my_loss.py`
  - `mmseg/models/losses/__init__.py`

> 注：原文未提供内部交叉链接（仅一个外部 GitHub 链接指向 BaseDecodeHead 源码），故关联信息主要从文件路径与导入语句推导。

---

## 【使用方法】

**1. 自定义优化器启用**：

```python
optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
```

**2. PyTorch 内置优化器直接调用**（无需注册）：
- SGD：`dict(type='SGD', lr=0.02, momentum=0.9, weight_decay=0.0001)`
- Adam：`dict(type='Adam', lr=0.0003, weight_decay=0.0001)`

**3. 自定义主干网络启用**：

```python
model = dict(
    ...
    backbone=dict(
        type='MobileNet',
        arg1=xxx,
        arg2=xxx),
    ...
)
```

**4. 自定义解码头启用**（以 PSPHead 完整配置为例）：

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

**5. 自定义损失函数启用**：

```python
loss_decode = dict(type='MyLoss', loss_weight=1.0)
```

> 注：原文**未涉及**任何命令行启动方式、训练/推理脚本调用、checkpoint 加载细节或环境配置项。
