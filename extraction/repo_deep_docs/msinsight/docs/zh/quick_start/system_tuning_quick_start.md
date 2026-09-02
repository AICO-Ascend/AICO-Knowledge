# 快速入门（系统调优篇）

> 仓 `msinsight` · 路径 `docs/zh/quick_start/system_tuning_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msinsight/docs/zh/quick_start/system_tuning_quick_start.md

# 一体化深度解读：系统调优快速入门指南

## 【定位】

这篇文档是 MindStudio Insight 针对多卡昇腾训练/推理场景下"快慢卡（卡间性能不均衡）"问题的快速入门教程，提供从 msProf 采集数据导入到 Summary → Communication → Timeline 三页签逐步定位系统性能瓶颈（卡空闲、Host 未及时下发任务）的标准化分析路径。

## 【技术要点】

1. **三步分析流程**：导入 msProf 系统数据 → Summary 页签看整体资源利用 → Communication 页签对比各卡通信耗时差异 → Timeline 页签确认空闲/计算分布。
2. **样例规模**：双机 16 卡（`MultiProfLevel2MemoryUB_db`），含 8 个 `node1_` 节点目录 + 8 个 `ubuntu2204_` 节点目录，每节点含 `ASCEND_PROFILER_OUTPUT`、`FRAMEWORK`、`PROF_xxx` 三个子目录。
3. **Summary 观察结论**：在计算/通信概览中发现 8 卡、15 卡的空闲时间明显。
4. **Communication 观察结论**：15 卡的第一个通信算子耗时最短；通信耗时不能单独作为快慢判断依据，需结合 Summary 空闲时间与 Timeline 综合判断。
5. **Timeline 关键操作**：右键通信算子缩略图中 15 卡的最小通信算子 → 选择 "Find in Timeline" → 框选 Overlap Analysis 泳道 → 查看 Slice List。
6. **Overlap Analysis 泳道结构**：包含 Computing（Ascend Hardware 投影）、Communication（Communication 投影）、Free 三个子泳道；最终量化结论为 Free 用时约为 Computing 用时的 3 倍。

## 【关键机制与数据】

**工作原理（分析路径机制）：**

原文采用"由粗到细、由整体到局部"的瓶颈定位逻辑：
- 第一层（Summary）：用计算/通信概览快速识别哪些卡的资源未被充分利用（空闲时间明显）。
- 第二层（Communication）：在"Communication Duration Analysis"单选模式下，对比各卡通信算子缩略图耗时差异，识别同步阶段的等待差异。多卡并行场景的通信阶段通常包含"等待其他卡到达同步点"的时间。
- 第三层（Timeline）：通过 Overlap Analysis 泳道投影，将卡行为分解为 Computing / Communication / Free 三态，量化空闲比例，定位瓶颈根因（用户代码纯 CPU 操作耗时长、Host 系统线程抢占等）。

**性能数据：**

原文: Free 用时是计算用时的 3 倍左右（来自 15 卡在选定时间窗口内 Slice List 的量化结果）。

原文: 识别为关键异常的卡号 = 8、15（Summary 中空闲时间明显），重点分析对象 = 15（首个通信算子耗时最短）。

原文: 节点时间戳样例 `node1_2166651_20240619060505060_ascend_pt`、`PROF_000001_20240619140505099_GNIJBPBEBIHIHCKB`，对应 2024-06-19 采集时段的 8 卡 + 8 卡双机配置。

**数据流：**

原文: 数据源 msProf（昇腾官方 profiling 工具）→ 导出 `MultiProfLevel2MemoryUB_db` 根目录 → MindStudio Insight 整体导入（非单子目录）→ 同时渲染 Summary / Communication / Timeline 三视图。

## 【表格解读】

### 表 1：1.2 开始前检查

| 检查项 | 要求 |
| --- | --- |
| 工具安装 | 已完成 MindStudio Insight 安装，安装方法请参见 [MindStudio Insight 安装指南](../install_guide/mindstudio_insight_install_guide.md)。 |
| 版本配套 | MindStudio Insight、CANN 与采集工具版本需匹配，版本关系请参见 [版本发布说明](../release_notes/release_notes.md)。 |
| 样例数据 | 已下载本文提供的系统性能样例数据，并能在本地访问。 |
| 数据来源 | 样例数据由 [msProf](https://gitcode.com/Ascend/msprof) 采集，包含 Summary、Communication、Timeline 所需信息。 |
| 适用场景 | 适用于多卡训练或推理场景的系统性能入门分析，尤其适合学习快慢卡、通信耗时和空闲时间分析。 |

逐行解读：
- **工具安装**：前置硬性条件，必须先完成 MindStudio Insight 安装，对应链接为安装指南。
- **版本配套**：强调 Insight、CANN、msProf 三者版本需匹配，配套关系见版本发布说明，避免因版本错配导致数据无法解析。
- **样例数据**：用户需本地可访问本文指定的样例包（双机 16 卡）。
- **数据来源**：明确样例由 msProf 采集，且必须包含 Summary / Communication / Timeline 所需信息（即三类页面共同依赖的数据字段）。
- **适用场景**：定位为"多卡训练或推理的系统性能入门"，重点用例为快慢卡、通信耗时、空闲时间分析。

### 表 2：1.4 术语速查

| 术语 | 说明 |
| --- | --- |
| msProf | 用于采集系统性能数据的工具。本文使用其导出的分析数据进行系统调优。 |
| Summary（概览） | 用于查看整体计算/通信概况、资源利用情况和初步瓶颈判断。 |
| Communication（通信） | 用于查看通信耗时和通信算子分布，帮助判断是否存在慢卡。 |
| Timeline（时间线） | 用于查看卡在时间上的行为分布，确认计算、通信和空闲状态。 |
| Overlap Analysis | 时间线中的分析泳道，用于同时观察 Computing、Communication 和 Free 的关系。 |
| Computing | 表示卡正在计算。 |
| Communication | 表示卡正在通信。 |
| Free | 表示卡处于空闲状态。 |
| 快慢卡 | 指集群中不同卡的性能不均衡现象。 |

逐行解读：
- **msProf**：外部数据采集工具，本文分析的所有数据均出自其导出结果。
- **Summary / Communication / Timeline**：文档定义的"三页签"分析入口，分别承担整体概览、卡间通信差异、时间轴行为分析的不同职责。
- **Overlap Analysis**：时间线视图下的专用分析泳道，是判断 Computing/Communication/Free 关系的核心工具。
- **Computing / Communication / Free**：卡在时间维度的三种基本状态，构成卡行为的正交分解。
- **快慢卡**：本文核心问题定义，即卡间性能不均衡，是系统调优的主要目标场景之一。

### 表 3：3. 常见问题与排查入口

| 现象 | 建议处理 |
| --- | --- |
| 导入 `MultiProfLevel2MemoryUB_db` 后无数据显示 | 先确认导入的是整个根目录，而不是某个子目录；如果仍然无数据显示，请参考 [FAQ](../support/faq.md) 中的数据导入问题。 |
| 页面显示与本文截图不完全一致 | 不同 MindStudio Insight、CANN 或 msProf 版本的界面字段可能略有差异，请以 Summary、Communication、Timeline 页签中的关键指标为准。 |
| 无法判断哪张卡是瓶颈 | 先在 Communication 页签观察通信耗时，再在 Timeline 页签确认该卡在通信前的计算/空闲状态。 |
| 想了解 Timeline 泳道含义 | 参考 [Timeline 泳道介绍](../best_practices/Timeline_Common_Lanes_and_Interface.md)。 |

逐行解读：
- **导入无显示**：常见根因是误导入单子目录而非根目录 `MultiProfLevel2MemoryUB_db`，再次失败后跳转 FAQ。
- **界面与截图不一致**：归因为版本差异，强调以三大页签的关键指标为准，不强求界面字段一一对应。
- **无法判断瓶颈卡**：给出标准排查顺序——Communication 看耗时差异 → Timeline 看通信前行为。
- **泳道含义不明**：指引至独立的 Timeline 泳道介绍文档深入学习。

## 【公式解读】

原文无公式。

## 【关联】

本文定位为系统调优的"快速入门"，因此与大量上下游文档形成衔接关系：

- **数据采集侧**：向上依赖 [msProf 工具](https://gitcode.com/Ascend/msprof) 提供原始 profiling 数据；安装前置依赖 [MindStudio Insight 安装指南](../install_guide/mindstudio_insight_install_guide.md)。
- **版本配套**：通过 [版本发布说明](../release_notes/release_notes.md) 校验 Insight / CANN / msProf 三方版本一致性。
- **能力深入**：作为入口引导用户进入 [MindStudio Insight 系统调优](../user_guide/system_tuning.md) 与 [基础操作](../user_guide/basic_operations.md) 两个核心 user guide 文档。
- **Timeline 进阶**：详细泳道含义跳转至 [Timeline 泳道介绍](../best_practices/Timeline_Common_Lanes_and_Interface.md)（在文档正文中被引用两次：术语表外、问题排查处）。
- **Host 侧根因分析**：当识别出 Free 时长 ≈ 3× Computing 时长后，下一步推荐 [基于 Linux Kernel Trace 的 Host Bound 问题分析](../best_practices/Host_Bound_Analysis_with_Linux_Kernel_Trace.md)，形成从"卡空闲"到"Host 侧未及时下发任务"的根因追溯链路。
- **异常排查**：异常处理统一跳转 [FAQ](../support/faq.md)。
- **样例数据**：下载来源 [系统数据](https://gitcode.com/zhangruoyu2/msinsight-quick-start-demo/blob/main/system)，为外部 GitCode 仓库。

整体关系可概括为：本文是入口与示例 → 基础操作文档承接通用 UI → 系统调优文档承接深入能力 → Timeline/Host Bound 文档承接专项深入 → FAQ/版本说明承接异常处理。

## 【使用方法】

**启用方式（基于原文操作步骤）：**

1. **数据准备**：从 GitCode 下载样例数据，解压后确认根目录 `MultiProfLevel2MemoryUB_db` 完整（包含 16 个节点子目录，每节点含 ASCEND_PROFILER_OUTPUT、FRAMEWORK、PROF_xxx 三个子目录）。
2. **数据导入**：在 MindStudio Insight 中选择导入整个 `MultiProfLevel2MemoryUB_db` 根目录（**注意**：非单一子目录）。
3. **Step 1 Summary 分析**：切换到 Summary（概览）页签，观察计算/通信概览，识别空闲时间明显的卡（样例中为 8、15 卡）。
4. **Step 2 Communication 分析**：切换到 Communication 页签，选中 "Communication Duration Analysis（通信耗时分析）" 单选项，对比各卡通信算子缩略图耗时（样例中 15 卡的首个通信算子耗时最短）。
5. **Step 3 Timeline 分析**：
   - 右键 15 卡的最小通信算子 → 选择 "Find in Timeline"；
   - 适当缩放时间轴；
   - 框选 Overlap Analysis 泳道，查看 Slice List 中 Free / Computing / Communication 用时比例（样例结果：Free ≈ 3× Computing）。
6. **下一步动作**：补充 Host 侧数据（参考 Host Bound 分析文档），定位卡空闲根因（用户代码纯 CPU 操作 / Host 系统线程抢占）。

**配置项/命令：**

原文未涉及具体的配置项或命令行操作（明确声明"不展开 msProf 数据采集命令"）。

## 图文联合解读

- `system_quick_start_summary_overview.png`: **图文联合解读：**

图示MindStudio Insight的Summary页签，展示16卡（Rank 0–15）的Computation/Communication Overview柱状图。Rank 8和15的柱体明显高于其他卡（红线箭头标注），辅以Advice提示Computing、Communication、Free最大差值均超阈值，论证存在**快慢卡（性能不均衡）**。该图对应文档第2步"在Summary页签观察整体资源利用情况"，作为定位性能瓶颈的起点，为后续Communication/Timeline页签深入分析慢卡原因提供依据。
- `system_quick_start_comm_duration_analysis.png`: **图意解读**：

1) **画面内容**：Communication页签下选择"Communication Duration Analysis"（红框标注1），展示16个Rank（0-15）的横向条形图，绿色条为通信耗时，左侧8卡（rank 0-7）耗时集中在31100ms附近，右侧8卡（rank 8-15）约在31280ms附近，红色箭头指向rank 15，提示存在显著差异；底部"Slow Rank List"显示当前域通信相对均衡。

2) **技术结论**：通过跨Rank通信时长对比可识别"快慢卡"，rank 15的条形末端明显错位，提示其为潜在性能短板卡。

3) **与文档关系**：对应文档第3步——在Communication页签判断可能的性能瓶颈卡，为后续Timeline页签定位空闲与计算分布提供线索。
- `system_quick_start_timeline_slow_question.gif`: **图文联合解读：**

图中 Communication 页签展示了 16 个 Rank 的通信耗时横向条形图（31088–31295 ms）。可见 Rank 0–7 与 8–15 形成两个时间簇，机内通信均衡且工具判定"未检测到明显慢卡"。然而两簇间存在约 150 ms 的时差，提示跨机通信为下一步瓶颈排查重点，衔接文档从 Summary→Communication→Timeline 的调优路径。
- `system_quick_start_selected_unit_list.png`: **1) 图中内容**
上方为 Timeline 的 Overlap Analysis 时间轴，自上而下展示 Computing、Communication、Communication(Not…)、Free 等并行轨道，以绿色色块密度反映各阶段活跃时序，并标注了一段明显的 Free（空闲）区间；下方为 Slice List 表格，红框圈出 Wall Duration(ms) 列，列出 Totals=253.126ms、Computing=50.375ms、Free=202.751ms 等数据。

**2) 技术结论**
空闲时间(202.75ms)远大于计算时间(50.38ms)，Free 占比约 80%，说明该卡长时间等待，空闲与计算严重分布不均，存在明显的卡间性能失衡瓶颈。

**3) 与文档关系**
对应文档第 1.1 节第 4 步"在 Timeline 页签进一步确认空闲与计算分布"：通过 Wall Duration 红框数值与时间轴 Free 区段，直观量化空闲占比，佐证"快慢卡导致系统性能瓶颈"的分析路径。
