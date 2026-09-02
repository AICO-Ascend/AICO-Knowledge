# 教程 4: 自定义模型

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/zh_cn/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/zh_cn/tutorials/customize_models.md

# 一体化深度解读: 教程 4 — 自定义模型

## 【定位】
这篇文档是 MMSegmentation 系列教程的第 4 篇, 系统性说明如何在不修改核心库的前提下, 通过注册器 (registry) 机制向语义分割框架中**注入自定义优化器、优化器构造器、主干网络 (backbone)、解码头 (decoder head) 和损失函数**, 从而支持研究/业务侧的快速实验与定制。

## 【技术要点】

1. **优化器接入三步法**: 新建 `mmseg/core/optimizer/my_optimizer.py` → 用 `@OPTIMIZERS.register_module` 装饰继承自 `torch.optim.Optimizer` 的类 → 在 `mmseg/core/optimizer/__init__.py` 中导入该类, 注册器即可自动发现。
2. **配置域驱动**: 优化器行为由配置文件 `optimizer = dict(type='...', ...)` 域控制; 框架已支持 PyTorch 全部原生优化器, 例如 Adam 的可参考配置为 `lr=0.0003, weight_decay=0.0001` (原文说明此配置会造成数值掉点)。
3. **细粒度优化 (Optimizer Constructor)**: 对 BatchNorm 等层做权重衰减等差异化处理时, 可通过实现 `@OPTIMIZER_BUILDERS.register_module` 装饰的构造器类, 重写 `__call__(model)` 返回定制化 optimizer。
4. **Backbone 解耦开发**: 新建文件 `mmseg/models/backbones/mobilenet.py` → 用 `@BACKBONES.register_module` 装饰继承 `nn.Module` 的类 → 必须实现 `__init__` / `forward` (返回 tuple) / `init_weights(pretrained)` 三个方法 → 在 `backbones/__init__.py` 中导入并在配置文件的 `backbone` 域中按字符串名引用。
5. **Decoder Head 继承体系**: 所有解码头都必须继承基类 `BaseDecodeHead`; PSPNet 示例要求实现 `__init__` / `init_weights` / `forward` 三个方法, 关键超参 `pool_scales=(1, 2, 3, 6)`。
6. **Loss 函数加权模板**: 利用 `weighted_loss` 装饰器包装逐元素损失函数 (如 `loss = torch.abs(pred - target)` 即 L1), 再用 `@LOSSES.register_module` 暴露 `MyLoss(nn.Module)` 类, 通过 `loss_weight` 在多损失融合时加权。

## 【关键机制与数据】

工作原理 (基于注册器模式 + 配置驱动):
- **注册机制**: 所有自定义组件以装饰器 (`@OPTIMIZERS.register_module` / `@OPTIMIZER_BUILDERS.register_module` / `@BACKBONES.register_module` / `@HEADS.register_module()` / `@LOSSES.register_module`) 标记, 框架在 `__init__.py` 的导入阶段自动构建全局注册表, 后续配置文件中以 `type='类名'` 字符串即可解析。
- **数据流 (以 PSPNet 配置为例)**: 输入经 `ResNetV1c` (depth=50, 4 stages, dilations=(1,1,2,4), strides=(1,2,1,1), `contract_dilation=True`) 提取 4 阶段特征 → 取 `in_index=3` 的最深特征 (in_channels=2048) → `PSPHead` 用 `channels=512` 做 PPM (Pyramid Pooling, 池化尺度 1/2/3/6) 解码 → 输出 `num_classes=19` 通道的分割 logits, 由 `CrossEntropyLoss(use_sigmoid=False, loss_weight=1.0)` 监督。
- **性能数据**: 原文未提供新的性能数据, 仅提示 Adam 配置 `lr=0.0003, weight_decay=0.0001` 较 SGD (`lr=0.02, momentum=0.9, weight_decay=0.0001`) "数值表现会掉点"。

## 【表格解读】
**原文无表格**。

(文档以代码片段和散文形式给出指导, 未呈现任何参数表/性能对比表/配置清单表。)

## 【公式解读】
**原文无公式**。

(文档未给出 LaTeX 数学公式; `loss = torch.abs(pred - target)` 是代码形式, 表示 L1 逐元素损失; 该式符号含义: `pred` 为模型预测, `target` 为真值标签, `abs` 为逐元素绝对值。)

## 【关联】

该文档处于 MMSegmentation 教程体系的扩展篇, 与上游教程的关联如下 (根据文档自然引用推断):

- **与教程 1/2/3 的关系**: 本篇是"如何修改框架内部"的延续 — 前序教程通常讲解数据集、配置文件结构、推理训练基本流程, 本教程基于这些基础说明"在已有架构上做局部扩展"。
- **与 `BaseDecodeHead` 基类的关系**: 教程显式要求新解码头继承该基类 (链接到 `mmseg/models/decode_heads/decode_head.py`), 所有标准解码头 (PSPHead / FPN / UPerNet 等) 均在此基类上派生。
- **与 PSPNet 论文的关系**: 引用论文 `https://arxiv.org/abs/1612.01105`, `pool_scales=(1,2,3,6)` 即对应 PSPNet 原始 PPM 模块的 4 个池化尺度。
- **与 PyTorch 优化器生态的关系**: 链接到 PyTorch 官方文档 `https://pytorch.org/docs/stable/optim.html?highlight=optim#module-torch.optim`, 说明自定义类应继承 `torch.optim.Optimizer`。
- **与 MMCV 注册器的关系**: 全部 `@xxx.register_module` 装饰器和 `build_from_cfg` 工具来自 `mmcv.runner` / `mmcv.utils`, 体现对 MMCV 的依赖。

(注: 原文未提供文末内部链接列表, 以上关联基于文档中显式提到的外链与代码引用整理。)

## 【使用方法】

启用方式 (原文涉及内容):

1. **启用自定义优化器** — 在配置文件里修改 `optimizer` 域:
   ```python
   optimizer = dict(type='MyOptimizer', a=a_value, b=b_value, c=c_value)
   ```
   也可直接切换为 PyTorch 内置优化器, 如 Adam:
   ```python
   optimizer = dict(type='Adam', lr=0.0003, weight_decay=0.0001)
   ```

2. **启用自定义 optimizer constructor** — 在配置文件里通过 `optimizer` 域指向该构造器类 (具体配置键名原文未展开), 由其返回定制化 optimizer 对象。

3. **启用自定义 backbone** — 在配置文件 `model.backbone` 域中按字符串引用:
   ```python
   model = dict(
       backbone=dict(type='MobileNet', arg1=xxx, arg2=xxx),
       ...
   )
   ```

4. **启用自定义 decoder head** — 在 `model.decode_head` 域中指定类型与参数, 完整 PSPNet 示例配置见原文代码块 (含 `type='PSPHead'`, `in_channels=2048`, `in_index=3`, `channels=512`, `pool_scales=(1,2,3,6)`, `dropout_ratio=0.1`, `num_classes=19`, `norm_cfg=dict(type='SyncBN', requires_grad=True)`, `align_corners=False`, `loss_decode=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0)`)。

5. **启用自定义 loss** — 在 `loss_decode` 域中引用:
   ```python
   loss_decode = dict(type='MyLoss', loss_weight=1.0)
   ```
   通过修改 `loss_weight` 调整其在多损失融合中的权重。

> 说明: 上述为文档中直接出现的命令/配置写法; 文档未提供 CLI 启动命令或完整端到端训练入口, 故"完整训练启动方式"原文未涉及。
