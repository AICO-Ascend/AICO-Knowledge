# Timeline设计文档

> 仓 `msinsight` · 路径 `docs/zh/development_guide/design/Timeline.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msinsight/docs/zh/development_guide/design/Timeline.md

# Timeline 设计文档深度解读

## 【定位】

本文档定义了 msinsight（MindStudio Insight）中 **Timeline（时间线）** 子模块的完整设计：在昇腾异构计算架构下，把训练/推理过程中的 host 侧 API 调用和 device 侧 task 耗时"平铺"在同一时间轴上，并将其关联呈现，以帮助用户快速识别 host 瓶颈或 device 瓶颈，支撑深度调优——即一篇**面向可视化性能调优工具的前端设计与功能矩阵规格说明书**。

---

## 【技术要点】

1. **三层级泳道单元（Unit）模型**：`CardUnit` → `ProcessUnit`/`LabelUnit`（主要区别在于"有没有预览信息"）→ `ThreadUnit`/`CounterUnit`（最小单元，分别对应 timeline 的两种数据展示模式）。一个 Unit 可表示设备、进程、线程、任务流等。
2. **切片（Slice）概念**：表示一个动作、事件、算子等，是泳道上图形化的最小展示单位。
3. **双数据场景并存**：
   - **TEXT 场景**：数据源为 `Google Trace Format` 的 `json` 文件；
   - **DB 场景**：数据源为 msprof 工具采集解析的 `ascend_profiler_output.db` 文件。
   - "两个场景数据结构不同，因此后端有两份逻辑分别处理两种数据"。
4. **Timeline 界面四区划**：工具栏（区域一）+ 时间线树状图（区域二）+ 图形化窗格（区域三）+ 数据窗格（区域四）。
5. **数据窗格四种 Tab**：Slice Detail（选中详情）、Slice List（选中列表）、System View（系统视图）、Find（发现）。
6. **前端跳转目标算子机制**：`CategorySearch.tsx → CategorySearchContent → doJumpSlice` 只更新 `session.locateUnit`；真正执行跳转的是 `units/hooks/useLocate.tsx` 中的 `useJumpTarget`（仅在 `Scroller` 中使用），依赖项为 `[session, dom, unitsArea, tuningScroller]`（原文建议精简为 `[session.units, session.locateUnit, dom, unitsArea, tuningScroller]`，因为"`session` 太大了，很容易引起重新生成函数，消耗大量计算资源"）。

---

## 【关键机制与数据】

**整体工作原理**（基于原文）：

- **数据采集 → 后端处理 → 前端渲染**：device 端由 msprof 采集生成 `ascend_profiler_output.db`，TEXT 场景下由其他工具产出 `Google Trace Format` 的 `json`。"后端有两份逻辑分别处理两种数据"，处理后的结果以 Unit（泳道）+ Slice（切片）的形式下发到前端。
- **前后端跳转链路（原文）**：
  1. 用户在 `CategorySearch.tsx` 的 `CategorySearchContent` 中触发 `jumpSlice`；
  2. `jumpSlice` 调用 `doJumpSlice`，**只**更新 `session.locateUnit`（这是一个 mobx 可观察对象，使用 `runInAction` 包裹）；
  3. `useJumpTarget` 在 `autorun` 中侦听 `session.locateUnit` 变化：当 `session.locateUnit !== undefined` 时，通过 `getTargetUnit(getRootUnit(session.units), session.locateUnit.target)` 找到目标 Unit；
  4. 找到目标后调用 `handleUnitSelection(targetUnit)` + `session.locateUnit?.onSuccess(targetUnit)`，再调用 `getNormalUnitHeight(unitsArea, orderOptions, targetUnit)` 与 `scrollToResult(scrollHResult, tuningScroller)` 让泳道滚到目标位置；
  5. 最后 `runInAction(() => { session.locateUnit = undefined; })` 清空状态，避免重复触发。
- **目标 Unit 匹配规则（原文截取的 `doJumpSlice` 内联 target 函数）**：
  `unit instanceof ThreadUnit && Boolean(unit.metadata.cardId.includes(slice.rankId)) && unit.metadata.processId === slice.pid && unit.metadata.threadId === slice.tid`，即必须同时满足"是 ThreadUnit、卡 ID 包含目标 rankId、processId 等于 pid、threadId 等于 tid"四个条件。
- **数据窗格系统视图维度（原文）**：按"机器名称、卡序号"维度展示综合指标、Python API 汇总、CANN API 汇总、Ascend Hardware Task 汇总、HCCL 汇总、覆盖分析、亲和 API、亲和优化器、AICPU 算子、ACLNN 算子、算子融合等。
- **关键性能数据**：原文没有给出具体性能数字（如延迟、吞吐、内存占用等），仅有"性能调优能力"的功能性描述。原文标注的具体数字/枚举均出自功能矩阵表，已在【表格解读】中完整复刻。

---

## 【表格解读】

> 以下表格**逐字还原**原文"三、功能详解"中的功能矩阵（61 条）。

| 序号 | 一级功能 | 二级功能 | 三级功能 |
|:---:|:---|:---|:---|
| 1 | 平铺训练/推理过程 | 展示泳道、切片 | / |
| 2 | 标记列表 | 将选中区域进行标记并保存 | / |
| 3 | 树状图过滤 | 按卡过滤 | / |
| 4 |  | 按泳道过滤 | / |
| 5 | 算子搜索 | 图形窗口选中 | / |
| 6 |  | 跳转数据窗口发现 | 同名算子发现 |
| 7 |  |  | 点击跳转图形窗口选中 |
| 8 | 展示连线事件 | 全量展示 | / |
| 9 |  | 图形窗口选中单个展示 | / |
| 10 | 图形窗口复原 | / | / |
| 11 | 图形窗口放大缩小 | W、S键放大缩小 | / |
| 12 |  | Ctrl/cmd+鼠标滚轮放大缩小 | / |
| 13 | 树状图右键操作 | 整屏显示 | / |
| 14 |  | 在通信中查找 | / |
| 15 |  | 放大所选内容 | / |
| 16 |  | 控制缩放 | 撤消缩放 |
| 17 |  |  | 重置缩放 |
| 18 |  | 控制置顶 | 取消置顶 (全部) |
| 19 |  |  | 置顶 (按相同组) |
| 20 |  |  | 取消置顶 (按相同组) |
| 21 |  | 控制隐藏 | 隐藏 |
| 22 |  |  | 显示全部已隐藏泳道 |
| 23 |  | 在事件视图中显示 | 跳转数据窗口事件视图 |
| 24 |  | 控制python调用栈 | 显示 python 调用栈 |
| 25 |  | 控制python调用栈 | 隐藏 python 调用栈 |
| 26 | 树状图右键操作 | 控制全部子项 | 收起全部子项 |
| 27 |  |  | 展开全部子项 |
| 28 |  | 控制SET/WAIT事件 | 隐藏 SET/WAIT 事件 |
| 29 |  |  | 显示 SET/WAIT 事件 |
| 30 |  | 控制泳道高度自适应 | 开启泳道高度自适应 |
| 31 |  |  | 关闭泳道高度自适应 |
| 32 |  | 恢复所有卡的默认偏移量 | / |
| 33 |  | 控制基准算子 | 设置基准算子 |
| 34 |  |  | 自定义算子**对齐至**基准算子时间 |
| 35 |  |  | 清除基准算子 |
| 36 | 树状图设置时间偏移量 | / | / |
| 37 | 树状图设置置顶 | / | / |
| 38 | 图形窗口拖动选择区间与泳道 | 查看选择区间与泳道 | / |
| 39 |  | 跳转数据窗口选中列表 | / |
| 40 | 图形窗口选中Slice | 查看Slice详情 | / |
| 41 |  | 跳转数据窗口选中详情 | / |
| 42 | 数据窗口系统视图 | 统计系统视图 | 按机器名称、卡序号查看 |
| 43 |  |  | 查看综合指标 |
| 44 |  |  | 查看 Python API 汇总 |
| 45 |  |  | 查看 CANN API 汇总 |
| 46 |  |  | 查看 Ascend Hardware Task 汇总 |
| 47 |  |  | 查看 HCCL 汇总 |
| 48 |  |  | 查看覆盖分析 |
| 49 |  |  | 查看算子详情 |
| 50 |  |  | 点击跳转 Timeline 图形窗口具体算子 |
| 51 | 数据窗口系统视图 | 专家系统视图 | 按机器名称、卡序号查看 |
| 52 |  |  | 查看亲和 API |
| 53 |  |  | 查看亲和优化器 |
| 54 |  |  | 查看 AICPU 算子 |
| 55 |  |  | 查看 ACLNN 算子 |
| 56 |  |  | 查看算子融合 |
| 57 |  |  | 点击跳转 Timeline 图形窗口具体算子 |
| 58 |  | 事件视图 | 查看泳道所有算子详情 |
| 59 |  |  | 点击跳转 Timeline 图形窗口具体算子 |
| 60 | 数据对比 | 设置基准卡 | / |
| 61 |  | 设置对比卡 | / |

**逐行/逐簇解读**：

- **序号 1–2：可视化骨架与持久化**。"平铺训练/推理过程"是 Timeline 的核心能力（条目 1），通过"标记列表"（条目 2）允许用户把当前选中区间保存下来，便于后续对比/复盘。
- **序号 3–7：过滤与搜索**。树状图支持按卡/按泳道过滤（3、4），算子搜索支持"图形窗口选中"（5）和"跳转数据窗口 → 发现 → 同名算子发现 → 点击跳转回图形窗口"（6、7）两条路径，形成"数据窗格 ↔ 图形窗格"的闭环跳转。
- **序号 8–12：连线事件与视图控制**。"展示连线事件"既支持全量（8）也支持选中单条（9）；图形窗口支持复原（10）、W/S 键放大缩小（11）、Ctrl/cmd + 鼠标滚轮放大缩小（12）——三种缩放交互入口。
- **序号 13–35：树状图右键菜单（最大簇）**。覆盖五大类二级菜单：
  - **视图跳转/缩放**：整屏显示、在通信中查找、放大所选内容（13–15）；
  - **缩放控制**：撤消/重置缩放（16、17）；
  - **置顶控制**：全部取消、按相同组置顶/取消置顶（18–20）；
  - **隐藏控制**：隐藏单条、显示全部已隐藏泳道（21、22）；
  - **事件视图跳转**（23）；
  - **Python 调用栈显隐**（24、25）；
  - **子项折叠**：收起/展开全部子项（26、27）；
  - **SET/WAIT 事件显隐**（28、29，SET/WAIT 通常用于 Ascend 上的同步原语）；
  - **泳道高度自适应开关**（30、31）；
  - **卡偏移量恢复**（32）；
  - **基准算子管理**：设置、自定义算子"对齐至"基准算子时间、清除（33–35）——这是多卡对齐分析的关键能力。
- **序号 36–37：树状图顶层操作**。"设置时间偏移量"和"设置置顶"作为独立的一级功能，与右键菜单中的同类操作呼应。
- **序号 38–41：图形窗口交互出口**。"拖动选择区间与泳道"产生两个动作——留在图形窗口查看（38）和跳转到数据窗格"选中列表"（39）；"选中 Slice"同样产生两个动作——留在图形窗口看详情（40）和跳转到数据窗格"选中详情"（41）。
- **序号 42–59：数据窗格系统视图（最大二级功能簇）**，分三类：
  - **统计系统视图（42–50）**：按"机器名称、卡序号"维度提供 7 类汇总——综合指标、Python API、CANN API、Ascend Hardware Task、HCCL、覆盖分析、算子详情——并支持"点击跳转 Timeline 图形窗口具体算子"（50）实现跨窗格定位。
  - **专家系统视图（51–57）**：在统计维度之上叠加"亲和 API / 亲和优化器 / AICPU 算子 / ACLNN 算子 / 算子融合"五类专家视角（52–56），同样以"点击跳转具体算子"（57）作为出口。
  - **事件视图（58–59）**：列出泳道所有算子详情并可跳转回图形窗口（59）。
- **序号 60–61：数据对比**。"设置基准卡 + 设置对比卡"两动作构成多卡对比分析的最小操作集，与序号 33–35 的"基准算子"互为补充（一个对齐时间，一个对齐设备）。

> 原文中的数字与命令逐字保留：键盘组合 `W`/`S`（条目 11）、`Ctrl/cmd+鼠标滚轮`（条目 12）、同步原语 `SET/WAIT`（条目 28–29）、对齐动作"对齐至"（条目 34，加粗原文中已加粗保留）。

---

## 【公式解读】

**原文无数学公式。**

文档中出现的可执行片段均为 **TypeScript / 伪代码**（mobx action、React hook），已在【关键机制与数据】中以代码形式逐字摘录并解读，不在此节按 LaTeX 形式复述。

---

## 【关联】

依据原文与文末链接，Timeline 模块处于以下关系网中：

- **./TrackRender.md（泳道绘制设计）**：在"四、4.1 泳道绘制设计"中明确指向此文件，提示**本节只描述前端泳道操作，跳转到 TrackRender.md 查看绘制细节**——说明 Timeline 文档只覆盖"操作层"，渲染层在姐妹文档中。
- **msprof 工具**：DB 场景的数据来源完全依赖 msprof 采集解析的 `ascend_profiler_output.db`，二者是"采集 → 解析 → 可视化"的上下游。
- **Google Trace Format**：TEXT 场景的输入标准，msinsight 兼容这一业界通用 trace 格式，说明 Timeline 不是封闭工具。
- **Ascend 硬件/CANN 软件栈**：树状图中"Card 层级"包含 Ascend Hardware 各 Stream 任务流、HCCL 通信、Memory、AI Core Freq 等，是 CANN（Ascend Compute Architecture for Neural Networks）暴露给上层的可观测数据。
- **PyTorch / CANN / HCCL / ACLNN / AICPU**：在数据窗格的"专家系统视图"中作为亲和性分析的五个对象（条目 52–56），是 Timeline 调优建议的语义对象。
- **前端组件层级**：`CategorySearch.tsx`（搜索入口）→ `useLocate.tsx`（定位 hook）→ `Scroller`（滚动容器）→ `ChartContainer/Units`（泳道渲染容器），构成"触发 → 状态更新 → 响应式 autorun → 渲染重绘"的完整链路。
- **覆盖分析（Overlap Analysis）**：在 DB 场景树状图中作为 Card 层级的子项，并在系统视图条目 48 中作为独立汇总维度。

---

## 【使用方法】

> 仅复述原文给出的可启用项；未提及的部分一律标注"原文未涉及"。

- **数据源选择**：原文给出两种场景（TEXT / DB），由上游数据采集决定，**未给出启动命令**。
- **键盘快捷键**（原文）：
  - `W` / `S` —— 图形窗口放大缩小（条目 11）；
  - `Ctrl/cmd + 鼠标滚轮` —— 图形窗口放大缩小（条目 12）。
- **工具栏按钮**（原文）：标记列表、过滤（按卡/按泳道）、搜索、连线事件、复原、缩小/放大。
- **树状图右键菜单**：覆盖"整屏显示 / 在通信中查找 / 放大所选内容 / 缩放 / 置顶 / 隐藏 / 事件视图 / Python 调用栈 / 子项折叠 / SET/WAIT 事件 / 泳道高度自适应 / 卡偏移量 / 基准算子"等十余类。
- **跨窗格跳转**：在数据窗口的"系统视图 / 事件视图"中点击算子可"点击跳转 Timeline 图形窗口具体算子"（条目 50、57、59）。
- **多卡对比**：通过"数据对比 → 设置基准卡 / 设置对比卡"（条目 60、61）启用。
- **基准算子对齐**：通过树状图右键菜单"设置基准算子 → 自定义算子对齐至基准算子时间 → 清除基准算子"三步操作（条目 33–35）。
- **环境变量 / 配置项 / 启动命令 / 安装步骤**：**原文未涉及**。

---

> **附注**：原文文档末尾的 `doJumpSlice` 实现片段在本文档传输中被截断（仅给出 `target` 匹配函数的前 4 行，未到函数结尾），"4.2.1.1 分析如何调整目标算子的左右位置"小节也因此未能展示完整内容——以上均忠实于原文边界，本解读未做补全或推测。

## 图文联合解读

- `3fc49b58-9b42-43a9-80e0-fcfc374a7b43.png`: **图示解读：**

**① 图中内容：** 左侧为数据管理器（罗列.msprof/db文件），中部为树状分层结构（机器→Host→Ascend Hardware→Stream 0~43），右侧为按时间轴（0:03.625→0:06.125）平铺的彩色条带；红色框标注**Unit/泳道**（每行Stream）、**Slice/切片**（如紫红色EVENT_WAIT块）。

**② 技术结论：** 论证了Timeline的"行=泳道、块=切片"映射模型——同一Host下多Stream并行承载不同事件，事件在时间维度上以切片形式可视化呈现。

**③ 与文档关系：** 直观对应文档"二、界面介绍"的区域二（树状图）与区域三（图形化窗格），以及"一、概念描述"中Unit/Slice基础定义，是其结构化图示。
- `9cb08917-92a4-4761-b0f9-233e9b4013ed.png`: **图文联合解读：**

1）图示内容：MindStudio Insight Timeline 主界面，按红框编号标注四大区域——①工具栏（过滤/搜索/缩放）、②时间线树状图（Python/CPU→Thread→CANN→Ascend Hardware→HBM/LLC/HCCL/NPU_MEM/Stars Soc Info/ac pmu 多级泳道）、③图形化窗格（横向时间轴00:00.079.500起，含4.7ms跨度标注，下方按泳道平铺彩色算子切片LinearWithGrad、Reduc…）、④数据窗格（选中详情表，含ProfilerStep#2耗时293.14ms、LinearWithGradAccumulationAndAsyncCommunication等指标的持续/自用/平均/次数）。

2）技术结论：验证了文档所述"工具栏+树状图+图形化+数据窗格"四区架构，以及DB场景下按"机器→Host/Card→Stream/Memory/HCCL"的层级分层逻辑，实现host与device时间轴的关联可视化。

3）文档关系：直接对应"二、界面介绍"段落，是该章节的实证配图。
- `6699ff0c-3211-4f7b-b5d9-af81867ed589.png`: **图文联合解读：**

1) **图中所绘**：展示Timeline界面顶部的**区域一·工具栏**：上方Tab栏（时间线/内存/算子/概览）和红框标注的快捷按钮组，从左至右依次为标记（旗形）、过滤、搜索、连线事件、复原、以及时间轴缩放控件（显示当前10.6s刻度，含±号），下方为时间线树状图起始节点"ubuntu..._0 / Card: 0-3"。

2) **论证结论**：工具栏严格按设计文档描述布局，按钮序列与文档一一对应；时间轴缩放控件以"10.6s"为当前视窗基准，佐证文档"时间轴缩小放大"功能的存在。

3) **与文档关系**：该图即为文档「区域一：工具栏」段落的可视化佐证，印证"标记→过滤→搜索→连线→复原→缩放"的功能排列顺序与树状图入口展示。
- `1cd4d8b0-4ee8-4c73-8612-70a6ef09f3d2.png`: **图文联合解读：**

1）图示内容：左为DB场景树状图，展示「机器→Card-0-3→进程→Ascend Hardware→Stream 0~6（含MSTX domain）」分层；右为对应图形化窗格，多色彩条纵向铺陈各Stream任务耗时，底部以"EVEN…"标注事件节点；顶部选项卡切换"时间线/内存/算子/概览/通信"。

2）技术结论：Tree-Pane双向映射实现"层级勾选即渲染"，Stream间并行任务条可视化呈现时间重叠关系，支持瓶颈快速定位。

3）对应论点：直接印证文档"区域二树状图+区域三图形窗格"的DB场景描述，落地"Stream任务流耗时"的泳道数据展示模式。
- `6657b59a-1b71-4ff4-80cc-53006f0875a1.png`: **图示内容：** 左侧树状图列出两组泳道单元（baselinehubmns010…的Card 8 含 Stream 0/2/3/4；localhost…的 Host 进程89093 及 Card 8 的 Stream 0/2/3/4/5）；右侧红框为图形化窗格，在 00:04.095–00:04.145 时间轴上以绿、蓝、红及紫色（EVENT_WAIT/EVE…）切片平铺呈现各 Stream 任务流的起止与等待。

**技术结论：** 证明 Timeline 能将 host 进程与 device 多 Stream 的算子/事件切片在同一时间轴上并行可视化，并清晰呈现 EVENT_WAIT 等空闲间隔。

**与文档关系：** 对应"区域二 时间线树状图"与"区域三 图形化窗格"，印证"泳道分层 + 切片平铺"的 Timeline 设计，将 host 与 device 关联以辅助瓶颈定位。
- `b115b6a8-ae77-4149-8746-a32cac7bd924.png`: **图文解读：**
图中展示了时间线界面"区域四：数据窗格"的"选中详情"标签页，以 `EVENT_WAIT` 切片为例，呈现标题、开始时间（4072ms971μs30ns）、持续时间（16ms955μs60ns）及 modelId、taskType、streamId、taskId、connectionId 等参数。该图印证文档所述——点击泳道中的切片后，数据窗格可联动展示其纳秒级时序与关联标识，支撑用户进行深度调优与瓶颈定位。
- `486b33b4-a836-4844-bccc-04b4c12ed3c4.png`: **图文联合解读：**

图示截取了 Timeline 界面的搜索工具栏区域，顶部为 Tab 切换（时间线/内存/算子/概览/通信），中部为功能图标（42.6hour 时间轴），红框标注的是搜索输入控件，包含"请输入"提示、大小写匹配（Aa）、整词匹配（W）和搜索图标，并被命名为 `CategorySearchContent`，下方为 CPU、CANN 等泳道列表。

该配图佐证了文档"区域一：工具栏"中关于"搜索"快捷按钮的描述，展示了搜索组件的 UI 结构与字段定义，体现 Timeline 工具通过分类搜索（CategorySearchContent）帮助用户在大量泳道与切片中快速定位目标事件的设计，支撑深度调优的论点。
- `3ff09761-8f25-4169-b555-3217aee576a0.png`: **图文联合解读：**

图示为Timeline"深度像素换算算法"示意：左侧红框标"到目标泳道的像素数"指向泳道起点，右侧标注"到目标算子深度换算的像素数"对应Y轴坐标；中部堆叠呈现Python→Megatron→GPTModel→HcclAllgatherBase的层层调用栈，绿色高亮当前选中切片（标题HcclAllgatherBase，持续431us10ns，Input Dims "256,1,12288"，Input type "c10::Half"）。

该图佐证文档论点：①"泳道+切片"嵌套结构单元定义，以线程为最小Unit承载host调用栈；②图形化窗格通过"深度→像素"换算将算子调用层级映射到纵向坐标，实现API耗时的平铺呈现与下钻分析；③底部数据窗格配合切片选中，输出耗时与算子参数，支撑瓶颈识别。
- `dee8c49c-e640-42fb-9eaf-3d37552c0479.png`: **图文联合解读：**

图示内容：描述可拖动面板的坐标计算逻辑。画出了 x/y 视口坐标轴、Container 容器、主内容区与可拖动组件，记录了 `mouseevent.clientX`、`Container.left`、`Container.clientWidth`、`鼠标移动距离` 及"可拖动组件左边界新位置"五个关键标注。

论证结论：拖拽动作通过鼠标 X 位移驱动组件左边界相对 Container.left 的变化，从而动态计算主内容区宽度。

与文档关系：对应文档"有置顶泳道时，会分出置顶树状图"——该图阐释了置顶树状图与主树状图之间分隔条拖拽的几何/数学基础。
- `26c0143e-30ad-4d64-9f0e-f3db473c0edd.png`: **图文联合解读：**

图中展示了容器（Container）中"主内容"与"可拖动组件"的两种布局状态：上方为初始位置（主内容在左、可拖动组件在右），下方为拖动后位置互换；并标注了 x/y 视口边界及"主内容相对视口距离"（红色虚线箭头）。

该图论证了 Timeline 工具栏中**可拖拽组件的位置互换机制**——通过视口坐标计算真实内容偏移，实现拖动后子元素的精准重排。

对应文档"区域一工具栏"中**连线事件、可拖动面板**等交互能力的实现原理，为支撑用户自定义泳道/工具布局提供几何依据。
- `4.4.1-rectangle-select.png`: **图文联合解读：**

图中展示了DB场景下Card层级的时间线页：左侧树状图按Host/卡分层，呈现Python、CANN、Ascend Hardware（Stream 0-8）、AI Core Freq、HCCL、NPU MEM、HBM、LLC等泳道；右侧图形化窗格用彩色切片平铺各Stream任务流，红框标定580.2ms时间窗聚焦流2/3任务细节。

该图论证了：**Card层能汇聚多维度异构数据（计算/通信/内存），并通过时间窗聚焦实现host-device关联与瓶颈定位**，Stream 5密集切片暗示高算力利用率。

对应文档"区域二、三"论点：以泳道分层组织多源数据、以图形化切片呈现host与device耗时关联，支撑深度调优。
- `4.5.1-counter-units.png`: **图示内容**：HBM泳道下展开6条CounterUnit子轨道（0/Read蓝、0/Write品红、1/Read紫、1/Write蓝、2/Read绿、2/Write蓝），以柱状图呈现内存读写带宽随时间分布；中间竖线划分两次迭代周期，首尾均出现尖峰。

**技术结论**：作为 Timeline 最小单元之一，CounterUnit 通过离散柱状图展示计数器型时序指标，可对比多设备读写吞吐，识别内存瓶颈。

**与文档关系**：对应文档"ThreadUnit、CounterUnit 为最小单元，对应 Timeline 两种数据展示模式"以及"Card 层级包含 Memory 内存数据"的论述，是该数据模式与内存维度的可视化实例。
- `2231a890-6a4a-4dea-ade2-1969000e7546.png`: **图解读：**
1) 画了一个数据库表结构，字段包括 deviceId(INTEGER)、timestampNs(INTEGER)、bandwidth(NUMERIC)、hbmId(INTEGER)、type(INTEGER)，代表 DB 场景下采集的内存带宽类时序数据 schema。
2) 论证了 Timeline 在 DB 场景下，Memory/HBM 类数据以结构化表存储，时间戳粒度为纳秒，并按 device、hbm、type 多维分类记录带宽。
3) 呼应文档"区域二：DB 场景 Card 层级包含 Memory 内存数据"的论点，说明后端需对应数据库表逻辑来解析呈现内存相关泳道数据。
- `9dd45295-1558-4a4b-a674-04a290118b12.png`: **图解读：**

1）图中展示DB浏览器表结构视图，含字段、索引、外键等标签页；可见6个字段（deviceId高亮、llcId、timestampNs、hitRate、throughput、mode），类型分别为INTEGER/REAL，均可空。

2）论证该表为LLC（末级缓存）性能监测表，按device+时间戳记录命中率与吞吐，对应文档中DB场景Card层级下的"Memory内存数据"。

3）佐证Timeline后端需解析ascend_profiler_output.db多样化表结构，以支撑深度调优。
- `a15afbe9-72a4-43ab-9d91-e693c8b898fb.png`: **图文联合解读：**

1）图中内容：DDR数据格式定义表，含字段名（deviceId/timestampNs/read/write）、类型（INTEGER/NUMERIC）、索引及含义；下方为变更记录，标注2024/3/7"330首次上线"。

2）技术结论：规定了Timeline底层Memory数据的采集规范——以纳秒为时间单位、B/s为带宽单位，通过deviceId索引区分多卡DDR读写流量。

3）与文档关系：此图为文档"区域二—Card层级—Memory内存数据"提供数据格式契约，支撑DB场景下内存带宽时间序列的可视化与瓶颈分析。
- `00d33d96-5365-4a84-8523-b8e094c67961.png`: **图文联合解读：**

图示为DB场景下"L2 Buffer带宽"表的字段结构（l2BufferBwLevel/mataBwLevel/timestampNs/deviceId）。论证了Timeline的DB场景数据源自`ascend_profiler_output.db`，按时间戳与设备维度细粒度组织Ascend Hardware层级指标。对应文档"DB场景：数据来源msprof工具采集解析的`ascend_profiler_output.db`文件"论点，为区域三图形化窗格中Card下的底层数据展示提供数据来源支撑。
- `58e6e86b-4ced-445f-848d-b74935e0b3e3.png`: **图文联合解读：**

1) 图中展示了一张数据表结构，包含7个字段：accId、readBwLevel、writeBwLevel、readOstLevel、writeOstLevel（均为INTEGER）、timestampNs（NUMERIC）、deviceId（INTEGER），其中 accId 被高亮选中。

2) 该表对应文档「区域二」所述的 **Memory 内存数据**底层存储：acId 关联加速卡 ID，read/writeBwLevel 记录内存带宽层级，read/writeOstLevel（On-chip SRAM Transfer）记录片上传输层级，timestampNs 提供纳秒级时间戳，deviceId 标识设备——论证了 Timeline 内存数据以"带宽+片上传输"双维度、按时间戳有序存储的技术结论。

3) 此表结构印证文档论点：DB 场景下 Timeline 是将 profiler 采集数据（ascend_profiler_output.db）按设备+时间轴结构化组织，为图形化窗格中 Memory 泳道的渲染提供数据支撑。
- `33ef74a7-48bf-4214-bf90-79ac5baae4c9.png`: **图文解读：**

1) **图内容**：数据库表结构截图，含5字段——`type`(INTEGER)、`ddr`/`hbm`(NUMERIC)、`timestampNs`(INTEGER)、`deviceId`(INTEGER)，均非主键非必填。

2) **技术结论**：该表为DB场景下计数器(Counter)数据的存储schema，记录设备DDR/HBM内存指标随时间戳的采样值。

3) **与文档关系**：对应文档"最小单元ThreadUnit/CounterUnit"中CounterUnit的数据来源，印证Timeline在DB场景下通过`deviceId`+`timestampNs`时序字段实现内存类指标的时序绘制。
- `a3ed0024-5ece-4652-b9e7-101f8dc034a9.png`: **图文联合解读：**

1. **图示内容**：呈现 `SAMPLE_PMU_TIMELINE` 数据表结构，含 `deviceId`、`timestampNs`、`totalCycle`、`usage(%)`、`freq(MHz)`、`coreId`、`coreType(AIC/AIV)` 七个字段，并附变更记录（330首发，2024/3/13 新增 coreType 区分 AIC/AIV 核）。

2. **技术论证**：该表定义昇腾 AI Core 上 PMU 性能监控采样的最小数据单元——以纳秒时间戳 + cycle 数 + 利用率/频率 + 核 ID+ 类型为索引，承载 device 侧硬件指标的时序落库，是 DB 场景 `ascend_profiler_output.db` 的底层数据形态。

3. **与文档关系**：呼应文档"DB 场景"与"Card 层级下 AI Core Freq 等层级"的论述，为 Timeline 设备侧 task 耗时与利用率可视化提供数据源依据，coreType 字段则支撑 AIC/AIV 异构核的分类渲染。
- `949bfaa5-08e1-4b56-b374-99ca5c05e133.png`: 图示解读：

**1) 图中内容：** 网络端口监控数据表结构，包含deviceId、timestampNs、bandwidth、收/发包速率（rx/tx PacketRate、ByteRate）、累计收/发包数量与字节数（rx/tx Packets、Bytes）、收/发错误与丢包计数（rx/tx Errors、Dropped）以及端口号（funcId）等字段，使用INTEGER/NUMERIC类型。

**2) 技术结论：** 定义了一套按时间戳采样的网络端口指标Schema，速率类用NUMERIC（高精度），累计量用INTEGER，结构支持上下行双向监控。

**3) 与文档关系：** 对应文档中"Card层级—其他昇腾硬件系统数据"的网卡端口性能数据模型，为Timeline图形化窗格中设备侧网络瓶颈分析提供数据支撑。
- `9750e1a4-d502-4e84-aeb9-7dac65e70756.png`: **图文联合解读：**

**1) 图中内容：** 定义了"HCCS"数据表的字段结构，包含4个字段：deviceId（INTEGER，有索引）、timestampNs（INTEGER，本地时间戳）、txThroughput/NUMERIC（发送带宽B/s）、rxThroughput/NUMERIC（接收带宽B/s），并标注变更记录（2024/3/7首次上线）。

**2) 技术结论：** HCCS是DB场景下的通信带宽表，按设备维度记录收发吞吐量，用于刻画卡间互联的通信性能数据。

**3) 与文档论点关系：** 对应文档"区域二·DB场景·Card层级·底层数据"中的通信类数据，是timeline树状图中Channel层在DB数据源中的表结构定义，支撑host与device关联呈现及通信瓶颈识别。
- `c9f8d81c-9911-452d-a0ce-b74a312c6f36.png`: **图示内容**：一张PCIe数据格式表，列出`deviceId`、`timestampNs`（本地时间,ns）及`tx/rx`双向的Post带宽、Nonpost带宽、Cpl完成包、Nonpost延迟等字段，每个指标均含Min/Max/Avg三档数值。

**技术结论**：PCIe监测需按Tx/Rx两个方向分别采集Posted与Non-Posted两类事务的带宽，且Non-Posted因需等待完成包而额外记录传输延迟；多字段配合Min/Max/Avg表明数据采用时间窗口内的统计聚合采样，而非瞬时值。

**与文档关联**：该表对应文档中“其他昇腾硬件系统数据”层级的CounterUnit——印证Timeline通过Counter单元按时间序列绘制PCIe等硬件计数器指标，与ThreadUnit并列构成Timeline两种数据展示模式之一。
- `52df275e-599d-4559-b8b7-f70e3aace185.png`: **图文联合解读：**

图示为数据库表结构定义界面（DB场景），展示三字段：`deviceId` (INTEGER)、`timestampNs` (NUMERIC)、`freq` (INTEGER)。对应文档"区域二：Card层级"中 **AI Core Freq** 等硬件计数器数据的底层存储结构——以设备ID、纳秒时间戳、频率值的时序记录形式组织，支撑Timeline时间轴上的CounterUnit（计数模式）数据展示，论证了DB场景下硬件指标数据以时序表形式落库的设计结论。
- `a6c38060-4127-4d25-82aa-8ddac73a01e6.png`: **图文联合解读：**

1) **图示内容**：DB 浏览器中 `counter @main` 表的 schema 与样本行，含 id、name、pid、timestamp、cat、args 六列；数据按 pid 分为五组（512 带宽、1717600 HBM 吞吐、1717632 LLC、1717664 内存、1717728 缓存层级），每行记录一次计数器采样。

2) **技术结论**：Counter 的持久化采用"进程级 pid + 时间戳 + 键值 args"模型，同一 counter 跨时间采样形成时序，与 Timeline 的 CounterUnit 一一对应。

3) **与文档关系**：佐证文档"CounterUnit 是最小展示单元"及"DB 场景数据来源于 `ascend_profiler_output.db`"两点论断。
- `a769b4ed-22ac-481a-851e-60e35ccf8e2c.png`: 1）图绘DB场景Card层级展开视图：根节点"0"下"Ascend Hardware"子层展开Stream 0/22/23/32/33/35、Communication、OVERLAP_ANALYSIS、HBM等泳道；红色"start"切片锚定迭代起点，彩色窄带密集呈现各task耗时，紫色"EVEN…"切片配合粉色箭头与垂直虚线跨Stream指示event关联事件。

2）论证多Stream并发并行执行、迭代周期性节拍清晰可辨，且host/device事件可通过切片与虚线跨流关联，直观呈现"泳道+切片"基础概念及深度调优能力。

3）与文档关系：对应"区域二 时间线树状图"中DB场景描述——Card→Ascend Hardware下各Stream任务流耗时数据的实例化展示。
- `4.7.1-unit-slices.png`: **图文联合解读：**

1) **图示内容**：展示 DB 场景下的 Timeline 界面，左侧树状图按层级呈现 Python（host）→ CANN CPU（线程：Thread 13877/15127 等）→ Ascend Hardware / AI Core Freq / HCCL / NPU MEM / HBM / Stars Soc Info（device 各类 CounterUnit）。右侧图形化窗格以蓝红框高亮 CANN 泳道下的多色 Slice，蓝色竖线标识当前时间戳 00:00.982，顶部灰条为 Python 端 API 耗时。

2) **技术结论**：验证 ThreadUnit 与 CounterUnit 共存于同一泳道视图，ThreadUnit 以多色 Slice 呈现 task 事件、CounterUnit 以波形呈现 NPU 硬件指标，实现 host/device 在统一时间轴上的关联。

3) **与文档关系**：直观印证文档中"基础概念"对 Unit 的分类（CardUnit→ThreadUnit/CounterUnit）及"区域二树状图"对 DB 场景层级（机器→Host/Card→Stream/HCCL/Memory 等）的描述。
- `4.7.2-unit-slice-summary.png`: # 图文联合解读

**1) 图中内容**：DB场景下Timeline界面，左侧树状图展开"机器→Host(Python/CANN/CPU)、Card(Ascend Hardware/AI Core Freq/HCCL/NPU MEM/Acc PMU/HBM/Stars Soc Info/NPU)"层级泳道；红框高亮前4条泳道（Pyth
- `4.7.3-slice-detail.png`: **图示解读：** 界面顶部为标签栏与时间轴，区域二展示 Python(13877)→Thread 13877 的泳道层级，区域三平铺大量横条切片（如 `pretrain_gpt`、`mindspeed_llm`、`megatron/core/pipeline_parallel` 等），区域四展示选中切片的标题、起止/持续/自用时间及 Python id 等参数。

**论证结论：** 验证了文档"泳道承载切片"的层级模型——ProcessUnit/ThreadUnit 作为最小单元，每条切片代表一次 host 侧 API 调用，可被选中并在数据窗格中读取其元信息。

**与论点关系：** 实物佐证文档"一·基础概念"中 Unit/Slice 的定义，并对应"二·界面介绍"中区域二与区域四的协同交互逻辑。
- `4.7.4-search-count.png`: **图文联合解读：**

该图展示了时间线工具栏中的**搜索功能**演示：顶部Tab栏（时间线/内存/算子/概览/通信）切换数据维度，工具栏含标记、过滤、搜索、连线等快捷按钮；搜索框输入"event"后，在结果中通过数字"180421"（红框标注，高亮提示关键匹配项）定位事件，并支持"在查找窗口打开"跳转。下方列出Thread 15002/15015等线程片段。

**论证结论：** 搜索功能支持跨线程、跨数据维度的事件精准定位与结果计数展示，验证了工具栏（区域一）"快速检索与筛选"的能力，为用户提供host瓶颈的定位手段。
- `4.7.5-search-slice.png`: **图解读：** 1) 界面展示时间线页签下的工具栏（含搜索框输入"event"，匹配1/180421条结果）、左侧泳道树状图（System→CPU→CANN→Thread层级，Thread 15001被选中）与右侧图形化窗格（高亮一条蓝色切片标注"AscendCL:act..."），红色箭头指示搜索命中的事件位置。2) 论证了线程作为最小泳道单元承载切片事件、时间轴按微秒级精度展开、搜索可在树状维度定位具体事件的可行性。3) 对应文档"区域一工具栏（搜索）"、"区域二泳道树状图"、"区域三图形化窗格"的论述，共同支撑ThreadUnit承载Slice进行可视化调优的核心设计。
- `4.7.6-search-slice-list.png`: **图示内容**：区域四"数据窗格"的"查找"标签页，展示按序列号筛选的 EVENT_WAIT 事件列表，包含名称、开始时间、时长(ns)及"点击跳转Timeline"链接，共22469条分页。

**技术结论**：查找结果以表格形式呈现，每条事件支持一键跳转至图形化窗格定位，实现列表↔时间线双向联动。

**文档关联**：论证了"区域四"作为数据检索入口，通过点击事件可在"区域三"图形化窗格中定位对应切片，支撑"快速识别host/device瓶颈"的设计目标。
- `4.7.7-jump-to-slice.png`: **图文联合解读：**

1) **图中内容**：展示 Timeline「查找」结果列表，含「卡序号」下拉、列头（名称/开始时间/时长(ns)/点击跳转Timeline），表格列出 10 条 `EVENT_WAIT` 事件记录，按开始时间升序排列；最右列"点击"链接被红框高亮，底部显示共 22469 条、分页 10 条/页。

2) **技术结论**：验证了 Timeline 提供「按事件名检索 → 列表化呈现 → 行级联动跳转」的数据流；红框强调结果与图形化窗格间存在"反向锚定"交互路径。

3) **与文档论点关系**：呼应文档"区域四 数据窗格"与"区域三 图形化窗格"联动定位的设计思想，体现 host 侧等待事件可被搜索筛选并快速回溯到 Timeline 上对应切片，支撑瓶颈识别的调优闭环。
- `4.7.8-select-rectangle-search-slice-list.png`: **1) 图中内容：** 展示Timeline界面四级结构——顶部时间轴（标注558.9ms跨度，当前指针00:01.338），左侧树状图按"Python/CANN/Ascend Hardware/HCCL/NPU MEM/HBM"分层泳道（Unit），中部图形窗格以彩色色块呈现各线程与NPU的Slice分布，底部"选中列表"数据表汇总选中泳道（Thread 13877/15015/15127等）的AscendCL算子耗时统计（Totals 96.16ms）。

**2) 技术结论：** 论证泳道与切片的层级映射关系——选中多线程泳道后，下方数据窗格自动聚合这些Unit下的所有Slice（API/算子），输出总时长、自用时间及最大/最小/平均耗时等多维统计，实现"图形→数据"下钻分析。

**3) 与文档关系：** 对应文档"泳道→切片"基础概念及"四个区域"中区域二、三、四的联动关系，印证了"Unit作为最小展示单元、Slice作为动作事件"的定义，并展示多Unit选中触发的数据聚合机制。
- `4.7.9-select-name-time-to-search-slice-list.png`: **图解读：**

图示Timeline的"区域三图形化窗格"与"区域四数据窗格"的联动。

1. **画面内容**：上方为时间线树状图+泳道（含PyTorch/CANN线程、Ascend Hardware/HCCL/HBM等NPU数据流），泳道内彩色色条即**切片（Slice）**，代表各算子/事件；红色框标注了放大的558.9ms选区。下方面板"选中列表"展示该选区内各切片类型（如AscendCL@aclrtCreateEvent共109次、aclrtMemcpy等）的耗时统计；右侧"更多"面板进一步展开该切片每次发生的开始时间与时长。

2. **论证结论**：图形化窗格与数据窗格通过选中区实现数据下钻——同一切片在时间轴的分布、聚合统计、逐次明细三层信息一体化呈现。

3. **与论点关系**：印证"泳道/切片分层模型"及"区域三+区域四"四区划分的设计，支持用户从宏观耗时定位到具体瓶颈事件。
- `4.7.10-search-in-event-view.png`: **图文联合解读：**

1）**图示内容**：左侧为 Timeline 树状图，列出 Thread 15127/15128/16569/18002、Ascend Hardware NPU、AI Core Freq、HCCL、NPU MEM、Acc PMU、HBM、Stars Soc Info 等泳道；右侧为彩色切片堆叠的时间轴；中部弹出的右键菜单标注"在事件视图中显示"（红框突出）。

2）**技术结论**：泳道支持细粒度交互，菜单提供缩放、锁区、隐藏、自适应等操作，并实现 Timeline ↔ 事件视图的联动跳转。

3）**与文档关系**：印证文中"泳道（Unit）是层级化最小单元""图形化窗格呈现 host/device 切片"的设计，并补充说明其右键交互能力，与"帮助用户快速识别瓶颈、支撑深度调优"的论点呼应。
- `4.8.1-use-case.png`: **图文联合解读：**

图示为UML用例图：角色"调优人员"通过Include关系派生"单卡专家建议"与"集群专家建议"两个一级用例；前者再细分亲和优化器/亲和API(Pytorch)、AI CPU算子、ACLNN算子、算子融合(CANN)等识别；后者包含慢卡与慢链路识别。

论证结论：MindStudio Insight在Timeline可视化之上，向调优人员提供分层（单卡/集群）、分级（优化器/算子/链路）的专家诊断能力。

文档呼应：印证文中"帮助用户快速识别host或device瓶颈""提供筛选分类、专家建议等功能支撑深度调优"的论点，是Timeline调优闭环的能力地图。
- `4.8.2-sequence-diagram.png`: **图解读：**

1. **结构**：UML时序图，含优化人、ModuleManager/ProtocolManager、AdvisorModule、AdvisorProtocolUtil、AdvisorProtocol/FromRequestJson、AdvisorRequestHandler、process进程模块、DataBaseManager共8个角色，纵向分启动注册（Register两次）和前端请求处理（点击→ToRequest→Handler→Query→返回→ToResponseJson→展示）两大阶段。

2. **技术结论**：论证了DB场景下"前端→协议转换→Handler分发→数据库查询→结果组装→前端渲染"的完整数据链路，采用分层（注册层/请求层/查询层）解耦设计。

3. **与文档关系**：该图直接对应文档"DB场景"后端逻辑，体现"两个场景数据结构不同，因此后端有两份逻辑分别处理"中DB侧的实现，支撑Timeline分层架构设计论点。
- `4.8.3-affinity-api-flowchart.png`: **图文联合解读：**

1) **图示内容**：流程图描述 API 摘要生成算法。从"开始"出发，经"生成所有匹配规则首个 API 集合"→"查询数据库中以 aten 开头的记录"，经两次"查询结果为 0"判断（Y 分支短路直跳"结束"）→"筛选时间段不重复的顶层 API"→"筛选匹配的 API 序列并排序"→"形成摘要按分页输出"→"结束"。

2) **技术结论**：该流程实现了基于 aten 算子的专家建议摘要生成，采用双层"空结果短路"机制减少无效查询，并通过时间不重叠原则对匹配序列去重排序，最终按分页提供结构化建议数据。

3) **与文档关系**：对应文档开篇所述 Timeline "提供各种筛选分类、专家建议等功能，支撑用户进行深度调优"——此流程图即为该专家建议特性的后端实现逻辑，与前端 UI 形成"前端呈现–后端算法"的相互印证。
- `4.8.4-ai-cpu-kernel-flowchart.png`: **图文联合解读：**

**图示内容：** 纵向流程图，自上而下依次为"开始→组装查询命令→执行查询→组装结果→结束"五个节点，呈标准线性查询流水线。

**技术结论：** 该流程体现"装配—执行—装配"三段式查询架构，对应文档所述后端处理 Timeline 数据的统一骨架；TEXT（Google Trace JSON）与 DB（ascend_profiler_output.db）两种场景的差异可封装于"执行"与"装配"阶段，共用同一查询框架。

**与文档关系：** 印证文档"后端有两份逻辑分别处理两种数据"的论点，说明异构数据源通过统一的命令组装与结果装配机制解耦，支撑跨场景查询复用。
- `551bb7d1-6c53-4d56-a39e-079fd8a7fb21.png`: **图文联合解读：**

图示为四节点流程图，描绘 Timeline 工具栏中"连线事件"功能的执行链路：①查询全量连线（起止符）→②查询数据（平行四边形，I/O 处理）→ ③性能优化（平行四边形，I/O 处理）→ ④返回前端渲染（起止符）。

**技术结论：** 该图论证了连线事件采用"查询-优化-渲染"的线性数据流水线，即先拉取完整连线关系，再做性能优化，最后回传前端绘制，避免一次性返回造成渲染卡顿。

**与文档关系：** 对应文档"区域一·工具栏"中提到的"连线事件"快捷按钮，补充说明其内部后端处理流程，呼应文档"帮助用户快速识别 host/device 瓶颈"的设计目标。
- `0aaa104a-0954-403e-9838-8fd7f0a0120a.png`: **图解：**

1) **图里画了什么**：展示TEXT场景下Slice（切片）的数据库表结构，字段含id（INTEGER主键）、flow_id、name、cat、track_id、timestamp、type，均为TEXT/INTEGER类型，部分字段标注"不是null"。

2) **论证了什么技术结论**：该表结构与Google Trace Event Format严格对应，timestamp+track_id+flow_id三字段联合定位时间轴上的事件节点，佐证Slice是承载"动作/事件/算子"语义的最小数据单元。

3) **与文档论点的关系**：此图对应文档"数据场景-TEXT场景"中"Google Trace Format的json文件"持久化落地的DB Schema定义，是后端两套逻辑（TEXT/DB）中TEXT分支的数据结构证明，支撑Timeline解析层对切片字段的映射实现。
- `ecdd8ded-e432-45ea-9c34-7ea8092f1e4a.png`: ## 图文联合解读

**画面内容**：深色背景的筛选弹窗，列出四个未勾选条目——HostToDevice、async_npu、async_task_queue、fwdwd（每项前置彩色方块图标），底部"All"（蓝高亮）与"None"两个批量操作按钮。

**技术结论**：这是 Timeline 工具栏"过滤"功能的泳道分类选择面板，支持按 host↔device 通信、异步任务等多类泳道逐项显隐，"All/None"实现一键全选或清空。

**与文档论点关系**：对应文档"区域一：工具栏"中"过滤（支持按卡或按泳道过滤展示）"所述能力，说明用户可通过该面板对 async 相关泳道进行精细筛选，以快速定位 host/device 瓶颈。
- `d1225d4b-7bb7-43c2-93c5-8b64b1673a75.png`: # 图文联合解读

**图示内容**：流程图描绘了 Timeline 连线（host↔device关联事件）的后端渲染管线——从"查询连线点→屏幕500等分→type分类→可见性过滤（去重+剔除左右屏外端点+收集中段）→按 trackId 排序→分支判断（算子调优场景查 flagId 算子 / 普通场景二分查缓存深度）→按 flowId+时间排序→组装返回前端"。

**技术结论**：连线采用"屏幕离散化+视口裁剪+分层查询"策略，按数据场景分流处理，确保大量 host-device 关联线在大时间跨度下高效渲染。

**与文档关系**：对应文档"将host与device进行关联呈现"的设计论点，阐释了工具栏"连线事件"功能的后端实现路径，体现 DB/TEXT 两套逻辑差异化的处理思路。
