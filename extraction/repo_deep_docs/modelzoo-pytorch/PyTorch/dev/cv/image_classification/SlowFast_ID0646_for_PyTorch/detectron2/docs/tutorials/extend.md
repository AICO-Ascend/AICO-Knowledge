# Extend Detectron2's Defaults

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/extend.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/extend.md

# 深度解读:Extend Detectron2's Defaults

## 【定位】

这篇文档解决"如何在 Detectron2 已有抽象之上做研究级定制"的问题——它向用户解释 Detectron2 是如何用三种不同的接口形态(纯 config / 显式参数 / 两者混合)同时支持"开箱即用"与"无侵入式扩展"的。

## 【技术要点】

1. **抽象张力的双重需求**:研究型项目一方面需要"很薄的抽象"以便用新方式做事,另一方面又需要"足够高级的抽象"以便用户不必关心细节。Detectron2 通过下面的多形态接口同时满足两者。

2. **三类接口共存**:
   - **类型 1:Config-only 函数/类**——接受从 yaml 创建的 `cfg`,实现"标准默认"行为,用户只需加载专家写好的 config。
   - **类型 2:显式参数函数/类**——有明确显式参数的小积木,需要用户理解每个参数含义,组合更灵活。**[LazyConfig 系统](lazyconfigs.md) 就依赖这种接口**。
   - **类型 3:`@configurable` 装饰的函数/类**——既可只用 config,也可只用显式参数,也可两者混合调用。其显式参数接口"目前是实验性的"(原文:"currently experimental")。

3. **`@configurable` 装饰器**:通过 [`@configurable`](../modules/config.html#detectron2.config.configurable) 装饰,函数/类既支持 config,又支持显式参数,或两者混合。这是 Detectron2 灵活性的关键机制。

4. **Mask R-CNN 三种构建方式示例**(原文给出完整代码):
   - **Config-only**:`model = build_model(cfg)`——一行代码搞定。
   - **混合方式**:`GeneralizedRCNN(cfg, roi_heads=StandardROIHeads(cfg, batch_size_per_image=666), pixel_std=[57.0, 57.0, 57.0])`——只用 cfg 之外的少量参数覆盖。
   - **全显式参数**:在 `<details>` 折叠块中给出约 60 个显式参数,完整定义 backbone=FPN+ResNet+BasicStem、proposal_generator=RPN、roi_heads=StandardROIHeads 等所有组件。

5. **明确分层指引**:仅需标准行为 → [Beginner's Tutorial](./getting_started.md);需要扩展 → 看 [datasets.md](./datasets.md)、[data_loading.md](./data_loading.md)、[models.md](./models.md)、[write-models.md](./write-models.md)、[training.md](./training.md) 五个教程。

## 【关键机制与数据】

**工作原理**(均为原文叙述):
- Config-only 接口读取 yaml 中自己关心的字段并执行"标准"操作,用户无需知道哪个参数被使用。原文:"Users only need to load an expert-made config and pass it around, without having to worry about which arguments are used and what they all mean."
- 显式参数接口每个都是大系统的小积木,需要用户专业判断,组合成本更高但灵活性更强。原文:"But they can be stitched together in more flexible ways."
- 当需要实现 detectron2 内置"标准默认"之外的功能时,可复用这些明确定义的组件。
- LazyConfig 系统依赖显式参数接口(原文:"The LazyConfig system relies on such functions and classes.")。

**原文示例中的关键数字/参数**:
- ResNet-50 FPN 骨干:`out_features=["res2","res3","res4","res5"]`,256 通道,`freeze(2)` 冻结前两个 stage
- RPN:`in_features=["p2","p3","p4","p5","p6"]`,`num_anchors=3`,anchor 大小 `[[32],[64],[128],[256],[512]]`,aspect_ratios `[0.5, 1.0, 2.0]`,strides `[4, 8, 16, 32, 64]`
- RPN matcher 阈值 `[0.3, 0.7]`、标签 `[0, -1, 1]`;`pre_nms_topk=(2000, 1000)`、`post_nms_topk=(1000, 1000)`、`nms_thresh=0.7`、`batch_size_per_image=256`、`positive_fraction=0.5`
- ROI Heads:80 类(COCO),`batch_size_per_image=512`,`positive_fraction=0.25`,box proposal_matcher `[0.5]` 标签 `[0, 1]`
- 池化:`ROIPooler(7, (1/4, 1/8, 1/16, 1/32), 0, "ROIAlignV2")`(box)和 `ROIPooler(14, ...)`(mask)
- box_head `fc_dims=[1024, 1024]`;box_predictor `test_score_thresh=0.05`,box2box_transform `(10, 10, 5, 5)`
- mask_head `conv_dims=[256, 256, 256, 256, 256]`
- 像素均值 `[103.530, 116.280, 123.675]`,标准差默认 `[1.0, 1.0, 1.0]`(混合示例中覆盖为 `[57.0, 57.0, 57.0]`),`input_format="BGR"`

## 【表格解读】

**原文无表格**。

## 【公式解读】

**原文无公式**。文中仅有 Python 代码示例,未出现任何数学公式或 LaTeX 表达式。

## 【关联】

- 文档核心围绕 [`@configurable` 装饰器](../modules/config.html#detectron2.config.configurable)展开,该装饰器是三类接口之间灵活切换的纽带。
- [Yacs Configs](configs.md) 是类型 1(config-only)接口的详细教程,被文档直接引用。
- [LazyConfig 系统](lazyconfigs.md) 是类型 2(显式参数)接口的另一种组织方式,文档明确指出 "The LazyConfig system relies on such functions and classes"。
- 文档作为扩展指南,把读者引向下游的扩展教程:
  - 数据集自定义 → [Use Custom Datasets](./datasets.md)
  - 数据加载器自定义 → [Use Custom Data Loaders](./data_loading.md)
  - 模型使用 → [Use Models](./models.md)
  - 编写模型 → [Write Models](./write-models.md)
  - 训练循环 → [training](./training.md)
- [Beginner's Tutorial](./getting_started.md) 是仅需标准行为时的入口,与本文档形成"入门 → 扩展"的上下游关系。
- 上文完整 Mask R-CNN 示例同时涉及 `build_model(cfg)`(类型 1)、`GeneralizedRCNN(cfg, ...)`(类型 3 混合)、以及手工组装所有组件(类型 2 全显式参数),三类接口在同一示例中并存。

## 【使用方法】

原文未给出独立的"启用方式"或"配置项"——本文档是概念性 guide,而非操作手册。具体使用方法分散在文中链接到的下游教程中:

- **仅需标准行为**:加载专家 yaml config,然后调用 `build_model(cfg)` 等(详见 [getting_started.md](./getting_started.md))。
- **需要扩展时**:
  - 自定义数据集 → 看 [datasets.md](./datasets.md)
  - 自定义 DataLoader → 看 [data_loading.md](./data_loading.md)
  - 改写或编写模型 → 看 [models.md](./models.md) 和 [write-models.md](./write-models.md)
  - 自定义训练流程 → 看 [training.md](./training.md)
- **Config 系统本身**:[configs.md](configs.md) 讲解 Yacs Config;[lazyconfigs.md](lazyconfigs.md) 讲解 LazyConfig。
