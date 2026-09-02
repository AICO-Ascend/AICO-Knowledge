# AutoSchedule

> 仓 `ascendnpu-ir` · 路径 `docs/source/en/developer_guide/features/AutoSchedule/HFusion_AutoSchedule.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/en/developer_guide/features/AutoSchedule/HFusion_AutoSchedule.md

# 一体化深度解读:HFusion AutoSchedule 设计与实现

---

## 【定位】

**这篇文档描述了 Ascend NPU IR (Bisheng IR) 中 HFusion 框架的 AutoSchedule 模块的能力——在算子融合单元 (fusion unit) 已经确定的前提下,基于算子融合图 (fusion graph) 的轴映射 (axis mapping) 信息,自动生成满足昇腾 NPU 硬件约束 (特别是 32 字节 UB stride-align 等) 的 Tiling 与循环调度方案,并以 MLIR Transform Dialect 程序的形式对目标 IR 进行改写,以实现高性能、可复用、可解释的自动调度。**

---

## 【技术要点】

1. **基于轴映射 (axis-mapping) 驱动循环生成**:通过 `DimensionAnalyzer` 的 `getCommonAxis`、`getNormalizedInterchange` 等接口,把算子张量维度与 anchor (融合图中的锚点) 维度对齐,从而支持 broadcast、reduce、transpose 等多种融合模式下的维度级一致性。

2. **大规模算子融合 + Transform Dialect 算子原语**:在融合过程中显式使用 MLIR Transform Dialect 的 `fuseIntoContaining`、`fuseLoops`、`coalesceLoops` 等原语,把多个算子合并到同一个内核 (kernel) 中,从而复用片上 buffer、削减 GM 读写次数。

3. **Tiling 的多方案生成与对齐约束**:`StmtExprBuilder` + `Expr` 在静态或动态 shape 下生成多个候选 `TilingCases`,并通过 `getStrideAlignments()`、`getSizeAlignments()`、`getTileAlignments()` 取得对齐约束,使用 `alignTo(alignment)` 把维度对齐到合法值,最终挑选一个最优的 `TilingKey` 构造调度描述。

4. **32 字节对齐 (32-byte alignment) 是关键硬件硬约束**:UB 等片上存储访问要求 stride-align = 32 字节;tile/size 也需满足 stride 与 size 的对齐要求 (例如 transpose、concat、cast 需要 size-align);否则会出现运行时错误或性能下降。

5. **策略分派 (strategy dispatch) 与策略扩展**:在 `AutoScheduleBase.cpp::applySchedule()` 中按 `FusionKind` 选取 scheduler,例如 `FusionKind::PureElemwise` → `PureElemwiseScheduler`,`FusionKind::AnyPB` / `LastAxisPBR` / `AnyPBR` → `AnyPBRScheduler`;所有 scheduler 继承自 `SchedulerBase`,便于扩展新策略。

6. **调度与改写解耦 (Transform Dialect 解释执行)**:Scheduler 不直接改写 IR,而是构造 Transform Dialect 程序,再由 `AutoScheduleInterpreter` 翻译为具体的 Transform operation 并应用到目标 IR 上,使调度描述成为可复用、可解释的序列,符合设计目标中的 *Engineering* 与 *Performance* 要求。

---

## 【关键机制与数据】

### 整体数据/控制流

`func::FuncOp + fusion info (来自 HFusion pipeline)` 
   → AutoSchedule Pass 入口
   → `runPreScheduleProcedure()` (前置准备)
   → `applySchedule()` 中按 `FusionKind` 选择 scheduler (`PureElemwiseScheduler` / `AnyPBRScheduler` / ...)
   → `runScheduleProcedure()`,内含:
     - `calculateTilingImpl()`:基于 `DimensionAnalyzer` + `StmtExprBuilder`/`Expr`,用 `getStrideAlignments()` / `getSizeAlignments()` / `getTileAlignments()` + `alignTo()` 产生多个 `TilingCases`,选定 `TilingKey`
     - `createScheduleImpl()`:以 `KernelInfo` 为统一描述,生成 schedule 操作序列 (cacheRead / cacheWrite / tileUsingFor / fuseLoops / setBufferSize 等)
   → `runPostScheduleProcedure()`
   → 输出 **Transform Dialect 程序** (而非改写后的 IR)
   → `AutoScheduleInterpreter` 解释并应用到目标 IR,最终生成符合昇腾硬件约束的内核

### 工作原理要点 (原文锚定)

- **轴映射**: `DimensionAnalyzer` 通过 `getCommonAxis` / `getNormalizedInterchange` 建立 tensor 维度与 anchor 维度的对应关系,为后续 Tiling 与循环构造提供维度级信息 (支持 broadcast / reduce / transpose 等模式)。
- **融合硬约束**: 在融合过程中显式施加 stride-align (32 字节)、size-align、tile-align 等约束,使生成 IR 满足 Ascend NPU 内存访问规则。
- **多核 Reduce**: 仅在满足特定条件时才启用多核并行 reduce,逻辑入口为 `analyzeMultiCoreReduceInfo()`。
- **Buffer 上限**: 片上 buffer 分配受 L1/UB 容量与 `maxBufferCnt` 限制,通过 `setBufferSize` 设定资源约束。
- **动态 shape 支持**: 在 Tiling 计算中显式支持静态或动态 shape (`StmtExprBuilder` / `Expr`)。

> 原文未给出具体性能数据 (吞吐、加速比等) 与具体 benchmark 数字,因此本节不杜撰任何量化结果。

---

## 【表格解读】

### 表 1:Core interfaces and abstractions (核心接口与抽象)

| Type      | Name              | Description                                                                |
| ---------- | ------------------ | -------------------------------------------------------------------- |
| Base class      | `SchedulerBase`    | Abstract base for all schedulers, encapsulating the common scheduling flow                            |
| Scheduler    | `PureElemwiseScheduler` | Pure elementwise fusion strategy                                                |
| Scheduler    | `AnyPBRScheduler`  | Generic strategy for Pointwise/Broadcast/Reduce and similar fusion patterns                     |
| Kernel  | `KernelInfo`       | Unified description of fused kernel I/O, dimensions, alignment, and multi-core capabilities                     |
| Alignment  | `getStrideAlignments()` | Returns stride alignment constraints (dim index, unit), e.g. 32-byte align           |
| Alignment  | `getSizeAlignments()`  | Returns size dimension alignment constraints                                              |
| Alignment  | `getTileAlignments()`  | Returns tile dimension alignment constraints                                              |
| Analysis    | `DimensionAnalyzer`| `getCommonAxis`, `getInterchange`, `getNormalizedInterchange`, etc.|
| Primitive  | `cacheRead` / `cacheWrite` | I/O cache                                                             |
| Primitive  | `tileUsingFor` / `tileUsingForAll` / `tileReductionUsingFor` | Tiling |
| Primitive  | `fuseLoops` / `fuseIntoContaining` / `coalesceLoops` | Loop fusion and coalesce    |
| Primitive  | `setBufferSize`    | Resource constraints                                                            |

**逐行解读**:

- **`SchedulerBase`** — 所有调度器的抽象基类,把"前置 → 调度 → 后置"的通用流程封装到一处,新策略只需继承即可复用流水线,这是 Extensibility 的直接体现。
- **`PureElemwiseScheduler`** — 纯 elementwise 融合的专用 scheduler (例如连续逐点算子的链式融合),无 broadcast/reduce 维度差异,可用最简调度。
- **`AnyPBRScheduler`** — 通用 PBR (Pointwise / Broadcast / Reduce) 融合策略的 scheduler,处理点算、广播、归约混合出现的复杂融合图。
- **`KernelInfo`** — 融合内核的统一描述,涵盖 I/O 端口、维度、对齐约束、多核能力等,是 scheduler 与底层之间交换信息的核心结构。
- **`getStrideAlignments()`** — 取得"按维度索引 + 单位"形式的 stride 对齐约束 (例:32 字节),是 32 字节 UB 对齐约束的查询入口。
- **`getSizeAlignments()`** — 取得 size 维度的对齐约束,处理 transpose、concat、cast 等对 size 对齐敏感的场景。
- **`getTileAlignments()`** — 取得 tile 维度的对齐约束,是 stride 与 size 约束的组合,用于把候选 tiling 投影到硬件合法空间。
- **`DimensionAnalyzer`** — 轴映射分析器,提供 `getCommonAxis` / `getInterchange` / `getNormalizedInterchange`,用于建立 tensor 维与 anchor 维的对应关系。
- **`cacheRead` / `cacheWrite`** — I/O 缓存原语,把张量数据缓存到片上,降低 GM 访问频次。
- **`tileUsingFor` / `tileUsingForAll` / `tileReductionUsingFor`** — 三类 Tiling 原语,分别针对一般 for 循环、所有维度的循环、reduce 维度的循环进行分块。
- **`fuseLoops` / `fuseIntoContaining` / `coalesceLoops`** — 循环融合与合并原语,把多个循环合并为一个连续循环,是"大规模算子融合"在循环层面的实现手段。
- **`setBufferSize`** — 资源约束原语,用来限定片上 buffer 的容量,配合 `maxBufferCnt` 控制缓冲分配。

### 表 2:Constraints and Capabilities (约束与能力)

| Constraint     | Description                                                                | API / Implementation|
| ------------- | -------------------------------------------------------------------- | ---------------- |
| **Stride align**| UB and other on-chip memory access must be 32-byte aligned.                 | `getStrideAlignments()`, `alignTo()` in `calculateTilingImpl()`|
| **Size align**  | Some ops (e.g., transpose, concat, cast) require tile/size alignment.   | `getSizeAlignments()` |
| **Tile align**  | Combination of stride and size constraints, applied to Tiling schemes.                       | `getTileAlignments()` |
| **Reduce axis**  | Reduce, broadcast, extract_slice, transpose, etc. impose lowest-dim alignment. | `KernelInfo` per-op stride-align logic|
| **On-chip buffer**| Buffer allocation limited by L1/UB capacity and `maxBufferCnt`.                           | `setBufferSize`, `maxBufferCnt`|
| **Multi-core reduce**| Multi-core parallel reduce only when specific conditions hold.                               | `analyzeMultiCoreReduceInfo()` |

**逐行解读**:

- **Stride align** — 32 字节对齐硬约束,UB 等片上存储访问的最低要求;由 `getStrideAlignments()` 取得约束,在 `calculateTilingImpl()` 中通过 `alignTo()` 把维度对齐到合法值;违反将导致运行错误或性能下降 (原文原话)。
- **Size align** — 对 size 维度 (例如 transpose、concat、cast) 的对齐约束,通过 `getSizeAlignments()` 表达,防止 tile 切分到非对齐位置。
- **Tile align** — 把 stride 和 size 约束组合后应用到候选 tiling 方案 (`TilingCases`),由 `getTileAlignments()` 表达,作为 tiling 合法性的最终过滤。
- **Reduce axis** — reduce、broadcast、extract_slice、transpose 等算子对最低维度 (lowest-dim) 引入 stride-align 约束,实现位于 `KernelInfo` 的 per-op stride-align 逻辑中。
- **On-chip buffer** — 片上 buffer 分配受 L1/UB 物理容量与 `maxBufferCnt` 双重约束,通过 `setBufferSize` 在调度中施加资源上限,避免超额分配。
- **Multi-core reduce** — 多核并行 reduce 不是默认开启的,只有满足 `analyzeMultiCoreReduceInfo()` 给出的特定条件才会启用,避免错误的多核归约引入性能或正确性风险。

---

## 【公式解读】

**原文无公式 (LaTeX / 伪代码均未出现)。** 文档未给出形如 $T_i = \text{alignTo}(d_i, a)$ 或调度 cost 模型等显式数学表达式;相关约束仅以**自然语言 + 接口名** (`alignTo(alignment)`、`getStrideAlignments()`、`32-byte alignment`) 的方式呈现,因此本节不作虚构推导。

唯一可视为"准公式"的语义化表述 (原文直接给出的关键参数与命令) 如下,逐字保留:

- 硬件硬约束:`UB access requires 32-byte alignment` (stride-align)
- 对齐修正调用形式:`alignTo(alignment)`
- 调度分派映射:
  - `FusionKind::PureElemwise` → `PureElemwiseScheduler`
  - `FusionKind::AnyPB` / `FusionKind::LastAxisPBR` / `FusionKind::AnyPBR` → `AnyPBRScheduler`
- 主流程顺序:`runPreScheduleProcedure()` → `runScheduleProcedure()` (含 `calculateTilingImpl()`、`createScheduleImpl()`) → `runPostScheduleProcedure()` → Transform Dialect application

---

## 【关联】

(原文未提供任何内部链接,因此本节基于文档自身内容梳理模块内外部关系,而非来自文末超链。)

### 模块内部组件关系

- **Pass 入口 (HFusion pipeline)** → 在 `AutoScheduleBase.cpp::applySchedule()` 中按 `FusionKind` 选择 scheduler,scheduler 都继承自 `SchedulerBase`,因此新增策略只需继承 `SchedulerBase` 即可接入。
- **`SchedulerBase` ↔ 派生 `PureElemwiseScheduler` / `AnyPBRScheduler`**:策略分派 (strategy dispatch) 是调度器扩展的边界。
- **`DimensionAnalyzer` ↔ `KernelInfo` ↔ `Scheduler`**:轴映射分析 → 内核描述 → 调度策略生成,形成自底向上的数据流。
- **`StmtExprBuilder` / `Expr` ↔ `TilingInfo` / `TilingStruct` / `TilingData` ↔ `TilingKey`**:Tiling 表达式生成 → 多候选 Tiling 描述 → 选定的最优 TilingKey。
- **`ScheduleOperations.cpp` 中的原语 (`cacheRead` / `cacheWrite` / `tileUsingFor*` / `fuseLoops` / `coalesceLoops` / `setBufferSize`)**:在 scheduler 的 `createScheduleImpl()` 中被组织为 Transform Dialect 序列。
- **Scheduler ↔ `AutoScheduleInterpreter`**:scheduler 输出 Transform Dialect **程序**,由 interpreter 解释并应用,实现"调度描述与 IR 改写解耦"。

### 上下游关系

- **上游**:AutoSchedule 接收来自 HFusion pipeline 的 `func::FuncOp` 与融合信息 (`FusionKind`);`DimensionAnalyzer` 的轴映射分析结果作为其输入。
- **下游**:AutoSchedule 的输出是 Transform Dialect 序列,经 `AutoScheduleInterpreter` 应用后,产出满足 Ascend NPU 硬件约束 (32-byte UB 对齐、tile/size 对齐、buffer 上限、多核 reduce 条件等) 的最终融合内核 IR,可交由后续算子编译流程 (例如 codegen、buffer 分配、指令发射) 使用。
- **与其他特性的关系**:文档中明确将 dynamic shape、multi-core reduce 列入 *Performance* 设计目标,表明 AutoSchedule 与动态 shape 适配、多核并行归约这两类优化同属 HFusion 性能优化栈;但**原文未给出具体特性链接**,因此不做进一步外推。

### 代码位置 (原文给出,可作为模块寻址依据)

- Headers (API 与抽象):`bishengir/include/bishengir/Dialect/HFusion/Transforms/AutoSchedule/`
- Implementation:`bishengir/lib/Dialect/HFusion/Transforms/AutoSchedule/`

---

## 【使用方法】

**原文未涉及**具体的启用命令、命令行 flag、配置文件或环境变量 (例如没有给出 `-enable-hfusion-auto-schedule`、`pass-pipeline` 写法或 `lit` 测试调用方式)。

文档中**唯一可作为"使用约束/调用规则"**的信息是:

- 启用条件:AutoSchedule 作为 HFusion pipeline 中的一个 pass 运行,接收 `func::FuncOp` 与融合信息作为输入;具体启用方式 (pass 注册、pipeline 配置、`mlir-opt` 命令行) 未在原文中说明。
- 调度策略选择由 `FusionKind` 决定 (见上文"策略分派"映射),无需用户手工指定 scheduler。
- 约束生效路径:`KernelInfo::getStrideAlignments()` 与各 scheduler 的 `calculateTilingImpl()` 会**自动**施加 stride-align / size-align / tile-align / buffer 上限 / 多核 reduce 条件;用户无需 (也无法) 在调度层面手工关闭这些约束。

若需在生产中实际启用 AutoSchedule,需补充查阅仓库中 HFusion pipeline 的 pass 注册与 `mlir-opt` / Bisheng 编译器前端的相关资料 (原文未提供)。
