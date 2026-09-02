# 版本说明书

> 仓 `docs` · 路径 `MindSeriesSDK/26.1.0/zh/_menu_release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/docs/MindSeriesSDK/26.1.0/zh/_menu_release_notes.md

## 【定位】

本文档是 MindSeriesSDK 26.1.0 的**版本说明书导航页**，用于按 SDK 分类进入 Rec、Vision、Index、RAG、Multimodal、Agent 和 Driving 的具体版本说明文档，本身不记录功能变更或版本差异。

## 【技术要点】

1. 文档以“版本说明书”为主标题，通过 Markdown 项目符号提供七个 SDK 文档入口。
2. 覆盖的模块包括：
   - Rec SDK
   - Vision SDK
   - Index SDK
   - RAG SDK
   - Multimodal SDK
   - Agent SDK
   - Driving SDK
3. 七个链接均固定到 `branch_v26.1.0` 分支，表明这些入口用于访问 **26.1.0** 分支下的版本说明书。
4. 原文未提供功能新增、缺陷修复、兼容性变化、配置参数、API 差异或启用命令；这些内容需要进入各 SDK 对应的 release notes 才能进一步确认。
5. 各 SDK 的版本说明相对独立，本文只负责建立导航关系，不包含各模块之间的数据流或版本依赖说明。

## 【关键机制与数据】

- **原文：**页面通过“版本说明书”标题和七条链接构成统一导航，读者先选择 Rec、Vision、Index、RAG、Multimodal、Agent 或 Driving，再跳转到对应仓库的 `branch_v26.1.0` 文档。
- **原文：**全部链接使用 GitCode 公共仓库路径，当前页面没有提供安装、升级、编译、运行、卸载或排障流程。
- **原文：**可确认的唯一版本标识是 `26.1.0`，它出现在七个目标链接的分支名 `branch_v26.1.0` 中。
- 原文没有性能数据、吞吐率、时延、资源占用、精度变化或基准测试结果。
- 原文描述的是**文档访问机制**，而非软件运行机制，因此不存在可进一步拆解的数据流或处理链路。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

原始文档未提供文内或站内内部链接；按给定信息，内部链接为无。页面提供的是七个指向其他 GitCode 仓库的外部链接，其上下游关系可概括为：

| 上游导航模块 | 对应外部版本说明书 |
|---|---|
| Rec SDK | [Rec SDK 版本说明书](https://gitcode.com/Ascend/RecSDK/blob/branch_v26.1.0/docs/zh/release_notes_rec.md) |
| Vision SDK | [Vision SDK 版本说明书](https://gitcode.com/Ascend/VisionSDK/blob/branch_v26.1.0/docs/zh/release_notes_vision.md) |
| Index SDK | [Index SDK 版本说明书](https://gitcode.com/Ascend/IndexSDK/blob/branch_v26.1.0/docs/zh/release_notes_index.md) |
| RAG SDK | [RAG SDK 版本说明书](https://gitcode.com/Ascend/RAGSDK/blob/branch_v26.1.0/docs/zh/release_notes.md) |
| Multimodal SDK | [Multimodal SDK 版本说明书](https://gitcode.com/Ascend/MultimodalSDK/blob/branch_v26.1.0/docs/zh/release_notes_mm.md) |
| Agent SDK | [Agent SDK 版本说明书](https://gitcode.com/Ascend/AgentSDK/blob/branch_v26.1.0/docs/zh/aura/08_release_notes_agent.md) |
| Driving SDK | [Driving SDK 版本说明书](https://gitcode.com/Ascend/DrivingSDK/blob/branch_v26.1.0/docs/zh/release_note/release_notes.md) |

这些链接与本文不是嵌套的文内上下游关系，而是平行的外部文档入口；原文也未说明这些 SDK 之间存在调用、依赖或部署顺序。

## 【使用方法】

启用方式、配置项及命令：**原文未涉及**。

原文唯一给出的使用方式是：进入本页后，根据实际使用的 SDK 选择对应版本说明书链接，并访问其固定在 `branch_v26.1.0` 分支下的文档。
