# 泳道绘制

> 仓 `msinsight` · 路径 `docs/zh/development_guide/design/TrackRender.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msinsight/docs/zh/development_guide/design/TrackRender.md

# 泳道绘制（TrackRender）深度解读

## 【定位】

本文档系统描述 msinsight 的 Timeline 视图如何将"时间轴 + 插旗标记 + 多类型泳道 + 跨泳道遮罩"组合成一个可缩放、可框选、可置顶、可跳转的可视化调优画布，明确从组件、图表类型、数据接口到交互的完整渲染管线，为泳道扩展与可视化问题定位提供依据。

---

## 【技术要点】

1. **Timeline 四大区域**：由 `时间轴区域`（TimelineAxis）、`标记区域`（TimeMarkerAxis）、`泳道区域`（包含 `UnitInfo` 泳道信息与 `Chart` 泳道内容）构成；时间轴使用自定义 `renderEngine` 持续重绘，依据 `session.domain.domainStart/domainEnd` 计算。
2. **三画布分工的标记区域**：点击插旗用 `ref=canvas`、Hover 插旗用 `ref=flagCursor`、插旗虚线用 `ref=vertical`；依赖 `width / domainStart / domainEnd / session.timelineMarker.refreshTrigger / session.selectedRange` 五参数触发重绘。
3. **三图表类型映射**：Process → `StatusChart`，Thread → `StackStatusChart`，Counter → `FilledLineChart`；Root/Card/Label 不渲染图表（在 `AscendUnit.tsx` 中定义）。
4. **双接口驱动的数据流**：静态信息走 `import/action` + `parse/success`（含 children、metadata）；展开时按泳道类型分别请求 `unit/threadTracesSummary`（线程预览）/ `unit/threadTraces`（线程数据）/ `unit/counter`（直方图）。
5. **跨泳道遮罩绘制**：`NormalCanvas` 与 `HoverCanvas` 跨泳道内容绘制，鼠标/键盘事件在内部用 `useImperativeHandle` 暴露，统一由 `ChartContainer` 实际绑定。
6. **四大交互一致性约束**：置顶依赖泳道 ID 且与父/子泳道展开兼容；框选驱动 `session.selectedRange` 并联动表格/详情；缩放统一更新 `domainStart/domainEnd`；跳转需先按需请求数据再定位。

---

## 【关键机制与数据】

### 渲染管线与组件关系

- **组件分层**（原文）：`TimelineAxis`（时间轴）、`TimeMarkerAxis`（标记）、`UnitInfo`（泳道信息：配置 + 置顶 + 泳道名称）、`Chart`（泳道内容，类型由泳道决定）。
- **绘制频率**：时间轴使用自定义渲染引擎 `renderEngine` **持续重绘**；标记区域按上述五参数变化触发重绘。

### 泳道实例化与数据装配流程

1. `import/action` 拉取所有卡的基础信息 → 遍历实例化 `new CardUnit` → 存入 `session.units`。
2. 后端 `parse/success` 事件携带单卡详情（含 `children`、`metadata`）→ 按 `type` 实例化子泳道 → 挂到 `session.units` 对应父泳道下。
3. 用户展开泳道时按类型请求不同接口获取绘制数据并渲染对应图表。

### 跨泳道遮罩的事件机制

`NormalCanvas`、`HoverCanvas` 在内部通过 `useImperativeHandle` 暴露鼠标/键盘事件方法，事件**实际绑定在父组件 `ChartContainer`** 上，由其统一调度，从而实现跨泳道坐标的 hover/选择/拖拽效果。

### 交互的关键状态耦合

- **置顶**：由 `UnitInfo` 承载，置顶泳道在滚动/展开其他泳道时保持可见；状态需与泳道 ID 绑定，数据请求链路与普通泳道一致。
- **框选**：作用于图形区域选择时间范围，状态经 `session.selectedRange` 联动表格、详情等模块。
- **缩放**：通过改变 `session.domain` 的 `domainStart / domainEnd` 驱动时间轴刻度与泳道内容**同步坐标换算**。
- **跳转**：定位到时间点/切片/算子，需同步 `domainStart/domainEnd` 与选中状态；若目标数据未加载，先触发对应泳道数据请求再定位。

---

## 【表格解读】

### 表 1：泳道类型与图表类型映射（5.2.1 节）

| 泳道类型 | 图表类型 |
|---------|---------|
| Root | - |
| Card | - |
| Process | StatusChart |
| Thread | StackStatusChart |
| Counter | FilledLineChart |
| Label | - |

**逐行解读**：
- `Root / Card / Label` 对应图表类型为 `-`，表示这三种泳道不承载可视化图表，仅作为容器或元信息节点存在。
- `Process → StatusChart`：用于呈现 Process 类型泳道（通常对应一段连续状态/过程）的状态图。
- `Thread → StackStatusChart`：线程泳道使用堆叠状态图，可在同一时间轴上堆叠展示多个线程/状态。
- `Counter → FilledLineChart`：计数器泳道使用填充折线图，呈现指标/直方图类数据。

### 表 2：数据接口列表（5.2.2 节）

| 接口 | 描述 |
|--------------------------|----------|
| import/action | 导入文件路径 |
| parse/success | 数据解析成功 |
| unit/threadTracesSummary | 获取线程预览数据 |
| unit/threadTraces | 获取线程数据 |
| unit/counter | 获取直方图数据 |

**逐行解读**：
- `import/action`：解析前端提交的文件路径，启动数据导入。
- `parse/success`：后端在单卡解析完成时返回的事件，携带该卡详情数据（children、metadata）。
- `unit/threadTracesSummary`：仅返回线程**预览**，适用于未展开的线程泳道缩略图。
- `unit/threadTraces`：返回线程**全量/详绘数据**，用于展开后的 `StackStatusChart`。
- `unit/counter`：返回直方图/计数器数据，用于 `FilledLineChart`。

### 表 3：泳道类型与请求接口对照（5.2.3 节）

| 泳道类型 | 接口 | 描述 |
|---------|--------------------------|----------|
| Label 泳道 | - | - |
| Process 泳道 | unit/threadTracesSummary | 获取线程预览数据 |
| Thread 泳道 | unit/threadTraces | 获取线程数据 |
| Counter 泳道 | unit/counter | 获取直方图数据 |

**逐行解读**：
- `Label 泳道` 无接口调用，原因是其不渲染图表，不存在绘制数据需求。
- `Process` 与 `Thread` 共享 `unit/threadTracesSummary`/`unit/threadTraces` 两条链路，但 Process 只取预览，Thread 展开后取详绘数据。
- `Counter` 独立使用 `unit/counter`，对应 `FilledLineChart` 的填充折线/直方图。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档以 Timeline 视图为核心，与以下模块/特性存在显式或隐式联动：

- **会话级状态 `session`**：
  - `session.domain.domainStart / domainEnd` → 驱动时间轴、标记、泳道内容的**统一时间域**，缩放/跳转均需更新。
  - `session.units` → 容器，承载 `CardUnit` 及其子泳道实例。
  - `session.timelineMarker.refreshTrigger` → 标记区域重绘触发器。
  - `session.selectedRange` → 框选结果，与表格、详情等其他模块联动。

- **图表渲染层**：`StatusChart`、`StackStatusChart`、`FilledLineChart` 三种图表共同支撑泳道内容绘制，新增泳道必须落到三者之一或新增图表。

- **跨泳道交互层**：`NormalCanvas` / `HoverCanvas` → `ChartContainer` 事件统一绑定，构成跨泳道的 hover/选择/拖拽能力。

- **缓存层**：`modules/timeline/src/cache/simplecache.ts` 提供数据缓存，缩放/跳转时按"复用缓存或按时间范围请求"策略降低重复请求。

- **上下游交互**：
  - 上游：数据导入（`import/action`） → 解析（`parse/success`）。
  - 下游：表格、详情等模块通过 `session.selectedRange` 与 Timeline 联动。

- **内部链接**：
  - `./figures/track-render/content-4.png` —— 文末所列内部链接，对应文档 **5.3 节 泳道遮罩** 的配图（"画布"图），说明 `NormalCanvas` 与 `HoverCanvas` 的位置与叠加关系。
  - 其他未列入"文末内部链接"的图（`overall.png`、`components-zh.png`、`components-en.png`、`flow.png`、`content-1.png`、`content-2.png`、`content-3.png`）仅在正文中以 Markdown 图片语法引用，未出现在用户给出的链接列表内。

---

## 【使用方法】

原文未提供具体的 CLI 启动命令或开关式配置项。文档给出了**开发/验证层级的使用方法**：

- **关键代码入口**（7.1 节）：
  - 泳道类定义：`modules/timeline/src/insight/units/AscendUnit.tsx`
  - 泳道信息组件：`modules/timeline/src/components/ChartContainer/Units/UnitInfo.tsx`
  - 图表类型：`StatusChart`、`StackStatusChart`、`FilledLineChart`
  - 数据缓存：`modules/timeline/src/cache/simplecache.ts`
  - 提示：路径随代码演进可能调整，应以仓库源码为准。

- **新增泳道开发步骤**（7.2 节）：
  1. 在泳道定义中补充新的 Unit 类型和必要元数据。
  2. 明确新泳道使用的图表类型。
  3. 后端补充或复用数据接口。
  4. 前端在展开泳道时触发对应数据请求。
  5. 验证置顶、框选、缩放、hover、跳转等交互是否受影响。

- **验证方法**（7.3 节）：
  - 导入包含 Timeline 数据的 **TEXT 或 DB** 数据。
  - 展开 Card、Process、Thread、Counter 等不同类型泳道。
  - 验证 `import/action`、`parse/success`、`unit/threadTracesSummary`、`unit/threadTraces`、`unit/counter` 的请求链路。
  - 验证置顶、框选、缩放、跳转、hover 是否正常。

## 图文联合解读

- `overall.png`: ## 图文联合解读

**1) 图中内容：** 全景图通过红/绿色虚线框标注了 Timeline 的四大区域——①顶部时间轴（带 00:00.395–00:00.495 时间刻度及高亮区间 00:00.429）、②标记区域（含插旗）、左侧 ③泳道信息列表（Python/Thread/AI Core Freq/HBM 等多类型泳道，其中 Thread 2050184 被高亮展开）、右侧 ④泳道内容区，可见 Thread 2050184 渲染出彩色的 StackStatusChart（CheckpointFunctionBackward 堆叠块），AI Core Freq 渲染为粉红色 FilledLineChart 填充曲线。

**2) 技术结论：** 印证了文档"不同泳道类型对应不同 Chart"的论点——Process/Thread/Counter 类泳道分别由 StatusChart、StackStatusChart、FilledLineChart 绘制，各 Chart 通过统一的 Chart 组件容器在 ④ 区域内横向铺开。

**3) 与文档关系：** 此图正是文档第 1 节所述"Timeline 全景图"配图，用实例把抽象的 ①～④ 区域与五类泳道—三类图表的映射关系可视化呈现。
- `components-zh.png`: **图示解读：**

1) **结构**：树状层级图，展示页面→主视图容器→头部/身体→各子组件的父子关系。关键节点：泳道虚拟滚动容器统一管理置顶与正常泳道；交互器派生普通/Hover双画布；泳道内容分为预览图、流水图、堆叠直方图。

2) **技术结论**：采用容器-渲染分层、虚拟滚动、多画布分离设计，实现区域解耦与性能优化。

3) **文档对应**：与文档"组件关系图"段落一一印证，明确了时间轴、标记区、泳道信息（UnitInfo）与内容（Chart）四区域的组件归属。
- `components-en.png`: **图文联合解读**

图示为 Timeline 的**组件树层级图**，自顶向下展示数据与渲染流的传递路径：`App → ChartContainer → {ChartHeader, ChartBody, HorizontalScroller}`。其中 ChartHeader 下挂 ChartRow（拆为 HeaderToolbar 与 TimelineAxis）以及 TimeMakerAxis，对应文档第 3、4 节的时间轴与标记区；ChartBody 下分四条子流——PinnedUnits/RefUnits 经 FlatternUnits 汇聚到 Unit，Unit 拆为 UnitInfo 与 Chart（再分发为 StatusChart/StackStatusChart/FilledLineChart），与文档 5.1、5.2 节泳道类型表完全吻合；另两条为 ChartInteractor（含 Normal/Hover Canvas，对应点击/hover 插旗）与 ContextMenu。

**结论**：论证了 Timeline 是"**容器—区域—单元—图表**"四层组合架构，绘制职责由 Canvas 承担、配置/置顶由 UnitInfo 负责。
**与文档关系**：图即文档 §2 组件关系的中文版，验证了各章节列出的 `<TimelineAxis/>` `<TimeMarkerAxis/>` `<UnitInfo/>` `<Chart/>` 在树中的真实位置。
- `flow.png`: ## 图文联合解读

**1) 图中内容：** 流程图自顶向下展示泳道初始化的四级数据流：①导入数据→返回卡片基本信息并初始化卡泳道；②卡片解析成功→返回子泳道信息；③按`type`字段分类初始化子泳道；④请求绘制数据→渲染泳道。箭头连接表示严格的前后依赖与数据传递。

**2) 技术结论：** 泳道渲染采用"**分层、渐进式数据装配**"策略——先以卡为单位粗粒度初始化，再按`type`细粒度分发至对应`Chart`组件（Process→StatusChart、Thread→StackStatusChart、Counter→FilledLineChart），最终触发绘制。

**3) 与文档关系：** 对应文档§5.2.2数据接口链（`import/action` → `parse/success` → `unit/threadTrace`），印证了泳道类型映射表（§5.2.1）的运行时驱动逻辑，阐明"泳道内容由Chart组件依据type动态装配渲染"这一核心论点。
- `content-1.png`: **图文联合解读：**

**1) 图中内容：** 展示 Timeline 初始空状态全景，顶部为工具栏与**时间轴区域**（刻度 00:04.487/09.500/14.500/19.500），高亮的 00:04.487 即**标记区域**的选中旗；左侧 0–7 为**泳道信息**（UnitInfo，含展开/收起控件），右侧大片空白为**泳道内容**（Chart）待渲染区。

**2) 技术结论：** 验证四大区域在无数据时仍可独立绘制——时间轴按 domain 持续渲染、标记层独立成画布、泳道骨架先行渲染，内容区由后续 Chart 按类型（StatusChart/StackStatusChart/FilledLineChart）按需填充。

**3) 与文档关系：** 直观对应文档 §1 概述四区域定义，是组件关系图的 UI 实例佐证。
- `content-2.png`: # 图文联合解读

**图示内容**：代码展示了 `newLane` 工厂函数，通过 switch-case 根据 `insightMetaData.type` 派发创建不同的泳道单元对象：Label→LabelUnit、Process→ProcessUnit、Thread→ThreadUnit、Counter→CounterUnit。红框标注了四个 case 分支及其 return 语句。

**技术结论**：泳道渲染采用工厂模式解耦类型判断与实例化，每个分支独立装配元数据（cardId、processId、dataSource 等）。

**与文档关系**：直接对应文档 §5.2.1「泳道类型」表格——Root/Card/Label 无图表，而 Process/Thread/Counter 渲染为 StatusChart/StackStatusChart/FilledLineChart，此函数即该映射的代码实现。
- `content-3.png`: **1) 图中内容**：展示 Timeline 全景界面——顶部工具栏、时间轴（00:00.300–00:02.450）、左侧层级化泳道列表（Python/CPU Thread、CANN、Ascend Hardware NPU Stream、AI Core Freq/HBM/LLC/NPU_MEM Counter、HCCL Group/Plane、Stars Soc Info），底部含 Slice Detail/Slice List/System View 标签，图表区当前为空。

**2) 技术结论**：验证了泳道采用 Root→Process→Thread 三级父子结构，NPU Stream 与 HCCL Plane 作为并行 Counter 泳道呈现，蓝色选区指示 offset/选中时间线位置，证明骨架先于数据渲染的渐进加载模式。

**3) 与文档关系**：直观印证文档所述"时间轴①、标记②、泳道信息③、泳道内容④"四分区，以及 Process→StatusChart、Thread→StackStatusChart、Counter→FilledLineChart 的类型映射。
