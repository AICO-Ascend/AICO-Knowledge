# Backward Compatibility and Change Log

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/centernet2/docs/notes/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/centernet2/docs/notes/changelog.md

【定位】本篇文档是 detectron2（CenterNet2 依赖的上游框架）的"向后兼容性与变更日志"，向使用者说明库的兼容性策略、配置版本演进历史以及若干会导致结果静默错误的历史回归问题。

【技术要点】
1. 稳定性分层：API 文档（[API documentation](https://detectron2.readthedocs.io/modules/index.html)）中列出的函数/类名、参数、文档化的类属性被视为 *stable*（稳定）；其余 API 视为 *internal*（内部），变更可能性更大。
2. 弃用过渡策略：稳定 API 若必须破坏，会先经历一段合理时长的 deprecation warning，再真正破坏，并写入 release logs。
3. 项目目录定位：`detectron2/projects` 下以及以 `detectron2.projects` 导入的项目均为研究性项目（research projects），全部视为 experimental（实验性）。
4. "default" 语义警告：类/函数名含 "default" 或文档明确说明产生 "default behavior" 的，其行为可能随新特性加入而改变。
5. 配置版本变更：v1 将 `RPN_HEAD.NAME` 重命名为 `RPN.HEAD_NAME`；v2 在 release 前进行了一批量化的配置重命名，且自开源以来 config version 未再变更。
6. 静默回归（silent regressions）记录了若干会导致结果不正确但不易察觉的窗口期缺陷。

【关键机制与数据】
- 兼容策略的工作原理：通过"稳定 API vs 内部 API"两层划分 + deprecation warning + release logs 记录三个机制降低对使用者的破坏面。
- 与 fork 的对比论据：原文表述"using it as a library will still be less disruptive than forking, because the frequency and scope of API changes will be much smaller than code changes"，即作为库引用的破坏频率和范围远小于直接 fork 后跟随代码改动。
- 历史静默回归窗口（原文逐条）：
  - `04/01/2020 - 05/11/2020`：当 `TRAIN_ON_PRED_BOXES=True` 时精度错误（Bad accuracy）。
  - `03/30/2020 - 04/01/2020`：ResNets 构建不正确（not correctly built）。
  - `12/19/2019 - 12/26/2019`：使用 aspect ratio grouping 导致精度下降。
  - `至 11/9/2019`：测试时增强（TTA）未预测最后一个类别。
- 入口指引：详细变更需在 release logs 中搜索关键字 "incompatible changes"。

【表格解读】原文无表格。

【公式解读】原文无公式。

【关联】
- 上游依赖：本文件属于 CenterNet2 仓内 `contrib/cv/detection/centernet2/docs/notes/changelog.md`，但内容主体为 detectron2 的兼容性策略，因此与 detectron2 的 API 文档、release logs、`detectron2/projects` 子项目存在引用关系。
- 配置文件演进：v1/v2 的配置重命名说明本框架的配置文件经历了破坏性变更，影响所有依赖配置键的下游代码（如 RPN 相关模块）。
- 静默回归与训练流程：`TRAIN_ON_PRED_BOXES` 涉及两阶段训练中的预测框迭代训练策略；`aspect ratio grouping` 涉及数据加载的采样分组；TTA 涉及推理时的多尺度/翻转增强流程——这三类问题分别落在训练策略、数据加载、推理增强三个模块上。

【使用方法】原文未涉及具体启用方式或配置命令；仅为兼容性说明与变更日志记录文档。如需查询具体 breaking change，应按原文指引在 [release logs](https://github.com/facebookresearch/detectron2/releases) 中搜索 "incompatible changes"。
