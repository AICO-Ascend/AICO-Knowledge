# 自动融合与调度

> 仓 `ascendnpu-ir` · 路径 `docs/source/zh_cn/developer_guide/features/hfusion_auto_schedule.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/zh_cn/developer_guide/features/hfusion_auto_schedule.md

# HFusion AutoSchedule 文档一体化深度解读

## 【定位】

本文档系统阐述了 HFusion 中 **AutoSchedule 模块**的能力与实现机制：在 Bisheng IR 上完成大范围算子融合后，自动面向 Ascend NPU 生成高效的执行 schedule（含合法 Tiling 方案、循环结构、Transform Dialect 序列），解决"融合后如何调度"的自动化与硬件适配问题。

---

## 【技术要点】

1. **轴映射驱动的循环生成**：`DimensionAnalyzer` 通过 `getCommonAxis`、`getNormalizedInterchange` 等建立融合图中各 op 与 anchor 的轴对应关系，覆盖 broadcast、reduce、transpose 等复杂模式，为 Tiling 提供维度级精确信息。

2. **基于 FusionKind 的策略选择**：`AutoScheduleBase.cpp::applySchedule()` 按融合类型分发调度器——`FusionKind::PureElemwise` → `PureElemwiseScheduler`；`FusionKind::AnyPB` / `LastAxisPBR` / `AnyPBR` → `AnyPBRScheduler`。

3. **三层硬件对齐约束**：`getStrideAlignments()`（UB 访存 32 字节对齐）、`getSizeAlignments()`、`getTileAlignments()` 三类约束在 `calculateTilingImpl()` 中通过 `alignTo(alignment)` 统一施加，作用于 `stride`/`size`/`tile` 三维概念。

4. **多候选 Tiling 方案与最优 TilingKey 选择**：`StmtExprBuilder` + `Expr` 系统结合静态/动态 shape 生成 `TilingCases`，再按"代价 + 对齐"等准则筛选最优 `TilingKey`。

5. **Transform Dialect 间接生效**：调度器不直接改写 IR，而是构造 Transform 程序，由 `AutoScheduleInterpreter` 翻译为 `fuseIntoContaining` / `fuseLoops` / `coalesceLoops` / `tileUsingFor` 等原语序列后落地到目标 IR。

6. **Reduce 多核并行能力**：`analyzeMultiCoreReduceInfo()` 在满足特定条件（如最低维对齐、合法 stride-align）时启用多核 reduce，需与 `setBufferSize`/`maxBufferCnt` 的片上资源约束协同。

---

## 【关键机制与数据】

### 整体调度主流程（原文：SchedulerBase::runOnOperation）

```
Pass入口 → applySchedule() 选调度器
       → runPreScheduleProcedure()
            ├─ IO cache 插入
            └─ analyzeAndVerifyKernelImpl()  内核分析与合法性检查
       → runScheduleProcedure()
            ├─ calculateTilingImpl()   生成 TilingComputeFn + TilingCases
            ├─ 选 TilingKey（代价/对齐）
            ├─ createScheduleImpl()    针对该 TilingKey 构造调度描述
            └─ applyScheduleImpl()    交 Transform 解释器执行
       → runPostScheduleProcedure()  结构优化、统计收集
       → AutoScheduleInterpreter 解析 + 应用 Transform Dialect
```

### Stride-Align 优化路径（原文：AnyPBRSchedule.cpp::calculateTilingImpl）

1. 基于问题规模生成初始 Tiling 方案；
2. 遍历 `KernelInfo::getStrideAlignments()` 与 `getTileAlignments()`；
3. 对相关维度执行 `alignTo(alignment)`（对齐粒度，典型为 32 字节）；
4. 输出满足 stride-align 约束的 `TilingCases`。

### 核心硬件数据（原文明确给出的）

- **GM（全局内存）**：容量大、延迟高——原文"GM 容量大但访问延迟高"。
- **片上内存（L1/UB）**：延迟低、容量有限——原文"片上内存（如 L1、UB）延迟低但容量有限"。
- **UB 访存对齐**：原文明确"UB 访问需 32 字节对齐（`stride-align`）"，否则导致"访存异常或性能下降"。

### 核心代码位置（原文）

- 头文件：`bishengir/include/bishengir/Dialect/HFusion/Transforms/AutoSchedule/`
- 实现文件：`bishengir/lib/Dialect/HFusion/Transforms/AutoSchedule/`
- 基类声明：`AutoScheduleBase.h`
- KernelInfo：`KernelInfo.h`
- Tiling 工具：`TilingUtils.h/cpp`
- 调度操作封装：`ScheduleOperations.cpp`
- 解释器：`AutoScheduleInterpreter.cpp`

> 注：原文未给出端到端 benchmark 性能数字（如加速比、吞吐率），仅给出"高性能""动态 shape 支持""reduce 多核并行"等定性描述。

---

## 【表格解读】

### 表 1：核心接口与抽象（原文逐字还原）

| 类型       | 名称               | 说明                                                                 |
| ---------- | ------------------ | -------------------------------------------------------------------- |
| 基类       | `SchedulerBase`    | 所有调度器的抽象基类，封装统一调度主流程                             |
| 调度器     | `PureElemwiseScheduler` | 纯元素级算子融合策略                                                 |
| 调度器     | `AnyPBRScheduler`  | `Pointwise`/`Broadcast`/`Reduce`等复杂融合的通用策略                |
| 内核描述   | `KernelInfo`       | 融合内核的IO、维度、对齐需求、多核能力等统一描述                     |
| 对齐接口   | `getStrideAlignments()` | 返回`stride`对齐约束（维度索引，对齐粒度），如32字节对齐            |
| 对齐接口   | `getSizeAlignments()`  | 返回`size`维度对齐约束                                               |
| 对齐接口   | `getTileAlignments()`  | 返回`tile`维度对齐约束                                               |
| 轴分析     | `DimensionAnalyzer` | 提供`getCommonAxis`、`getInterchange`、`getNormalizedInterchange`等 |
| 调度原语   | `cacheRead` / `cacheWrite` | IO缓存                                                              |
| 调度原语   | `tileUsingFor` / `tileUsingForAll` / `tileReductionUsingFor` | Tiling |
| 调度原语   | `fuseLoops` / `fuseIntoContaining` / `coalesceLoops` | 循环融合与合并     |
| 调度原语   | `setBufferSize`    | 资源约束                                                             |

**逐行解读**：
- **`SchedulerBase`**：调度器抽象基类，对应模板方法模式——统一主流程、把策略差异点留给子类覆盖（如 `calculateTilingImpl`、`createScheduleImpl`、`analyzeAndVerifyKernelImpl`）。
- **`PureElemwiseScheduler`** / **`AnyPBRScheduler`**：两大具体策略实现。前者处理规整逐元素图；后者处理含 Pointwise/Broadcast/Reduce 的复杂融合。
- **`KernelInfo`**：调度与 Tiling 的"内核画像"，聚合 IO、shape、对齐、多核能力等元信息，是 `get*Alignments()` 的数据源。
- **三组 `get*Alignments()`**：分别描述 `stride`、`size`、`tile` 三类对齐约束。stride-align 与硬件 UB 32 字节对齐直接挂钩；size-align 覆盖 `transpose`/`concat`/`cast` 等 op 的特殊粒度；tile-align 是前两者的综合作用面。
- **`DimensionAnalyzer`**：轴映射分析工具，承担 `getCommonAxis`（公共轴）/ `getInterchange`（换轴）/ `getNormalizedInterchange`（归一化换轴）等接口，是循环生成的前置分析。
- **IO 缓存原语**：`cacheRead`/`cacheWrite` 用于将 GM 数据搬入片上，是片上复用的基础操作。
- **Tiling 原语**：`tileUsingFor`、`tileUsingForAll` 处理通用 Tiling；`tileReductionUsingFor` 针对 reduce 轴专门 Tiling。
- **循环融合原语**：`fuseIntoContaining` 将内层 loop 融进外层、`fuseLoops` 合并同级 loop、`coalesceLoops` 合并同构连续 loop，共同构建统一 loop 结构。
- **`setBufferSize`**：片上 buffer 容量上限约束，与 `maxBufferCnt` 配合管理多 buffer 共存。

### 表 2：使用约束（原文逐字还原）

| 约束类型      | 说明                                                                 | 相关接口 / 实现 |
| ------------- | -------------------------------------------------------------------- | ---------------- |
| **Stride对齐** | UB等片上内存访问需满足32字节对齐，避免非对齐访存                  | `getStrideAlignments()`，`calculateTilingImpl()`中对维度`alignTo()` |
| **Size对齐**   | 部分op（如`transpose`、`concat`、`cast`）要求tile/size满足特定对齐 | `getSizeAlignments()` |
| **Tile对齐**   | stride与size约束的综合，作用于Tiling方案                        | `getTileAlignments()` |
| **Reduce轴**   | `reduce`、`broadcast`、`extract_slice`、`transpose`等op有最低维对齐要求 | `KernelInfo`中各op的stride-align逻辑 |
| **片上buffer** | 多buffer共存的容量与分配受L1/UB等限制                            | `setBufferSize`，`maxBufferCnt` |
| **多核reduce** | 需满足特定条件才可启用多核并行`reduce`                              | `analyzeMultiCoreReduceInfo()` |

**逐行解读**：
- **Stride 对齐（32 字节）**：最关键的硬件硬约束，违例会"访存异常或性能下降"。`calculateTilingImpl` 通过 `alignTo()` 向上取整。
- **Size 对齐**：针对 `transpose`/`concat`/`cast` 等 op 的特殊粒度需求，由 `getSizeAlignments()` 暴露。
- **Tile 对齐**：strde-align 与 size-align 的合流，作用于最终 Tiling 方案。
- **Reduce 轴**：原文列举 `reduce`、`broadcast`、`extract_slice`、`transpose` 均有"最低维对齐要求"，其约束来源于 `KernelInfo` 内各 op 的 stride-align 逻辑。
- **片上 buffer**：受 L1/UB 容量天花板约束，`setBufferSize` + `maxBufferCnt` 控制多 buffer 共存时的资源竞争。
- **多核 reduce**：需要先经 `analyzeMultiCoreReduceInfo()` 判定"满足特定条件"后方可启用，并非默认开启。

---

## 【公式解读】

原文无 LaTeX 公式或伪代码公式。文档以**流程步骤 + 接口契约**形式描述算法（如 `alignTo(alignment)`、`TilingComputeFn`、`TilingKey`），未给出形式化的数学表达式。

> 原文无公式。

---

## 【关联】

文档中明确涉及的上下游与关联模块（基于原文文本）：

- **HFusion 框架**：AutoSchedule 是 HFusion "大范围算子融合"流程的下游——先确定融合单元，再由 AutoSchedule 生成面向硬件的高效 schedule。原文表述："HFusion是Bisheng IR上针对算子融合和自动调度的高层框架，其中AutoSchedule模块负责在确定融合单元后……"。
- **Bisheng IR**：HFusion 所处的宿主 IR，原文表述："HFusion是Bisheng IR上针对算子融合和自动调度的高层框架"。
- **Ascend NPU 多级存储架构**（GM / L1 / UB）：AutoSchedule 的硬件约束来源，stride-align 32 字节对齐即源自 UB 访存规范。
- **MLIR Transform Dialect**：调度描述的承载与执行载体——AutoSchedule 不直接改写 IR，而是构造 Transform 程序，由 `AutoScheduleInterpreter` 翻译为具体原语。
- **FusionKind**：上游融合分析产出的融合类型标签（`PureElemwise` / `AnyPB` / `LastAxisPBR` / `AnyPBR`），是调度器分发的依据。
- **`func::FuncOp`**：Pass 入口拿到的工作单元，原文表述："AutoSchedule Pass在HFusion pipeline中被触发，得到待处理的`func::FuncOp`与其融合信息"。

> 原文文末"内部链接"为"无"，因此无内部跳转链接可解析。

---

## 【使用方法】

原文未给出启用命令、Pass 触发参数或配置项（如 mlir-opt 命令行开关、`-hfusion-auto-schedule` 类 flag、CMake 构建选项）。

文档以**架构/算法说明**为主，给出了：
- 代码入口位置（头文件/实现文件路径）；
- `FusionKind` 与调度器映射关系（策略选择逻辑）；
- 约束/对齐/接口表（可编程扩展点）。

但未涉及：
- 如何在命令行触发该 Pass；
- 是否需要开启前置 Pass（如 Fusion 分析 Pass）；
- 编译选项/环境变量。

> 原文未涉及具体的启用命令或配置项写法。
