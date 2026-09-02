# Introduction to Performance Tuning Tools

> 仓 `docs` · 路径 `FrameworkPTAdapter/26.0.0/en/pytorch_model_migration_fine_tuning/introduction_to_performance_tuning_tools.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/docs/FrameworkPTAdapter/26.0.0/en/pytorch_model_migration_fine_tuning/introduction_to_performance_tuning_tools.md

# 性能调优工具综述 — 一体化深度解读

## 【定位】

本文档是昇腾 NPU 上 PyTorch 训练场景**性能调优工具集的总览**，旨在说明当模型在 NPU 上训练出现瓶颈或需要性能优化时，可使用哪几类 CANN 系分析工具，并介绍各工具的能力边界与适用场景。

---

## 【技术要点】

1. **工具集基于 CANN 构建**：所有性能调优工具均为 CANN-based 分析工具，专门用于分析运行在 NPU 上的模型训练效率。
2. **包含四类工具**：
   - **Ascend PyTorch Profiler** —— 基于 CANN 实现，采集硬件执行效率与性能数据；
   - **性能对比工具（performance comparison tool）** —— 来自开源社区，对 Profiler 采集的数据进行专项对比分析；
   - **集群分析工具（cluster analysis tool）** —— 来自开源社区，针对集群数据进行分析；
   - **MindStudio Insight** —— 集成 CANN 数据分析与可视化功能的可视化调优工具。
3. **Ascend PyTorch Profiler 采集四类数据**：PyTorch 层算子信息、CANN 层算子信息、底层 NPU 算子信息、算子显存使用信息，可从多角度分析 PyTorch 训练性能。
4. **性能对比工具的对比维度**：支持同一平台或不同平台上的模型性能差异对比，**当前支持 GPU vs NPU 以及 NPU vs NPU** 两种对比场景；通过训练时间与显存使用识别劣化算子。
5. **性能对比工具的三维分解**：将训练时间分解为**计算、通信、调度**三个维度，并分别在算子粒度上对比计算与通信的算子；同时将训练总显存分解为算子级显存使用进行对比。
6. **集群分析工具的聚焦域**：当前主要基于**通信域、通信时间、通信矩阵**分析迭代时延，从而识别慢设备、慢节点、慢链路。
7. **MindStudio Insight 的可视化能力**：面向 LLM 集群场景，提供时间线视图、通信分析、计算时间等可视化展示。

---

## 【关键机制与数据】

**工作原理/数据流（基于原文）：**

- **数据采集层**：Ascend PyTorch Profiler 作为接口层，在 PyTorch 训练场景中**综合采集** PyTorch 层算子、CANN 层算子、底层 NPU 算子及算子显存使用四类性能数据。
- **专项分析层**：性能对比工具与集群分析工具均来自开源社区，作用于 Profiler 采集到的数据之上 —— 前者侧重横向对比（跨平台/算子粒度），后者侧重纵向剖析（集群迭代时延）。
- **可视化层**：MindStudio Insight 将 CANN 数据分析与可视化集成，主要面向 LLM 集群场景，提供时间线、通信、计算时间等视图，帮助定位瓶颈。
- **三维分解机制**：性能对比工具将训练时间显式拆解为 `计算（computation）`、`通信（communication）`、`调度（scheduling）` 三个维度；总显存被拆解为算子级显存使用进行对比。

**性能数据**：原文未提供具体的性能数字、benchmark 数据或量化指标。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

根据文中提及的内容，存在如下外部模块/上下游关系（均为 gitcode 链接，原文标注为外部参考）：

1. **Ascend PyTorch Profiler** → 进一步参考《CANN Performance Tuning Tool User Guide》中的 "Ascend PyTorch tuning tool" 章节
   `https://gitcode.com/Ascend/pytorch/blob/v2.7.1-26.0.0/docs/en/ascend_pytorch_profiler/ascend_pytorch_profiler_user_guide.md`
2. **性能对比工具（compare_tools）** → 参考 msprof-analyze 仓库的 "compare_tool_instruct"
   `https://gitcode.com/Ascend/msprof-analyze/blob/26.0.0/docs/en/user_guide/compare_tool_instruct.md`
3. **集群分析工具（cluster_analyse）** → 参考 msprof-analyze 仓库的 "cluster_analyse_instruct"
   `https://gitcode.com/Ascend/msprof-analyze/blob/26.0.0/docs/en/user_guide/cluster_analyse_instruct.md`
4. **MindStudio Insight** → 参考 msinsight 仓库的 "Installation and uninstallation"
   `https://gitcode.com/Ascend/msinsight/blob/26.0.0/docs/en/user_guide/overview.md`

**上下游关系链**：Ascend PyTorch Profiler 作为数据采集入口 → 性能对比工具 / 集群分析工具 对其数据进行专项分析 → MindStudio Insight 提供可视化集成。该路径与文档标题 "FrameworkPTAdapter/26.0.0/en/pytorch_model_migration_fine_tuning/"（PyTorch 模型迁移与微调路径）形成上下游呼应：本文档定位于性能调优环节，是模型迁移/微调后的性能验证与优化阶段。

> 备注：原文标注"内部链接: (无)"，上述链接均为文档中出现的**外部 gitcode 仓库链接**，不属于仓内内部交叉引用。

---

## 【使用方法】

原文未涉及具体启用方式、配置项或命令。仅在各工具介绍中指向了对应外部用户手册的链接，需前往以下页面查阅具体使用方法：

- Ascend PyTorch Profiler → `ascend_pytorch_profiler_user_guide.md`
- 性能对比工具 → `compare_tool_instruct.md`
- 集群分析工具 → `cluster_analyse_instruct.md`
- MindStudio Insight → `overview.md`（Installation and uninstallation）

具体调用命令、API 接口、环境配置等启用细节需在上述子文档中查询，原文 overview 未给出。
