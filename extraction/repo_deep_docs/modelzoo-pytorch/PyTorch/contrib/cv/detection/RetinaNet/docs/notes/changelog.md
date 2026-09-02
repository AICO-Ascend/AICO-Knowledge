# Backward Compatibility and Change Log

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/RetinaNet/docs/notes/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/RetinaNet/docs/notes/changelog.md

【定位】
本篇文档描述 detectron2 库（RetinaNet/PyTorch 贡献版检测模块所属的上游框架）的向后兼容性策略、配置版本变更历史以及历史静默回归（silent regression）清单，目的是告知用户哪些 API 视为稳定、内部接口变更的应对方式，以及如何检索历史不兼容变更。

【技术要点】
- API 稳定性分级：API 文档（API documentation）中列出的函数/类名、参数及已文档化的类属性视为 *stable*（稳定）；其余视为 *internal*（内部），更易变更；被 `detectron2/projects` 内部使用的接口可能被提升为稳定接口。
- 稳定 API 的破坏流程：会先通过 deprecation warning 告知，并写入 release logs，再正式 break。
- 配置版本（config version）：自开源以来未变更，仅记录了 v1、v2 两次历史重命名。
- 静默回归（silent regression）会"静默"地产生错误结果且难以排查，需特别留意日期区间。
- 引用 release logs（facebookresearch/detectron2/releases）作为不兼容变更的检索入口，搜索关键字 "incompatible changes"。
- 建议：第三方项目通过 as-a-library 方式使用比 fork 更能减少破坏，原因是 API 变更频率与范围远小于代码变更。

【关键机制与数据】
工作原理与数据流（原文相关说明）：
- 原文：稳定 API "are less likely to be broken, but if needed, will trigger a deprecation warning for a reasonable period before getting broken, and will be documented in release logs."
- 原文：内部 API "are more likely to change"，但若已在 `detectron2/projects` 中被使用，"we may treat them as stable APIs and also apply the above strategies. They may be promoted to stable when we're ready."
- 原文：第三方跟进的推荐策略——"using it as a library will still be less disruptive than forking, because the frequency and scope of API changes will be much smaller than code changes."
- 原文：detectron2 自开源后 config version "has not been changed"（当前无版本号要求）。

性能数据：原文未涉及。

【表格解读】
原文无表格。

【公式解读】
原文无公式。

【关联】
- 上游/外链关联：本文档多处指向 facebookresearch/detectron2 仓库的 release logs（https://github.com/facebookresearch/detectron2/releases），作为不兼容变更与新版本发布的唯一信源。
- 与代码仓内目录的关联：本文件位于 `PyTorch/contrib/cv/detection/RetinaNet/docs/notes/changelog.md`，承接的 RetinaNet 实现属于 detectron2 体系，因此其 API/配置/版本策略与 detectron2 一致；该文档本身即作为该贡献模块对 detectron2 兼容性约定的镜像说明。
- 与其他特性的关联：
  - 与 API documentation（https://detectron2.readthedocs.io/modules/index.html）配对使用——文档中列出的接口即"stable"集合的判定依据。
  - 与配置系统（Config）相关——v1/v2 的 RPN 配置重命名属于 Config 演进历史的一部分。
  - 与 detectron2/projects 子目录相关——内部 API 是否升级为稳定 API，取决于该子目录的实际使用情况。
- 内部链接：原文未提供内部链接（用户标注"内部链接: (无)"）。

【使用方法】
- 启用方式/配置项/命令：
  - 检索历史不兼容变更：在 release logs（https://github.com/facebookresearch/detectron2/releases）中搜索关键字 "incompatible changes"。
  - 配置重命名参考：
    - v1：`RPN_HEAD.NAME` → `RPN.HEAD_NAME`
    - v2：一批配置项重命名（原文未列具体条目，仅描述"a batch of rename of many configurations before release"）。
  - 静默回归规避：若代码运行时间落在以下区间内，需复核/升级 detectron2 版本以避免对应缺陷：
    - 04/01/2020 - 05/11/2020：`TRAIN_ON_PRED_BOXES=True` 时准确率异常（bad accuracy）。
    - 03/30/2020 - 04/01/2020：ResNets 构建不正确（not correctly built）。
    - 12/19/2019 - 12/26/2019：使用 aspect ratio grouping 导致准确率下降（drop in accuracy）。
    - 截至 11/9/2019：测试时增强（test time augmentation）未预测最后一类（does not predict the last category）。
  - 原文未涉及具体启用命令、环境变量或安装步骤。
