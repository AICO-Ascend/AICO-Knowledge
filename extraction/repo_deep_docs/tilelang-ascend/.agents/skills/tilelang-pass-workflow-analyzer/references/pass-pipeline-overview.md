# Pass Pipeline 架构详解

> 仓 `tilelang-ascend` · 路径 `.agents/skills/tilelang-pass-workflow-analyzer/references/pass-pipeline-overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/.agents/skills/tilelang-pass-workflow-analyzer/references/pass-pipeline-overview.md

# TileLang-Ascend Pass Pipeline 架构详解 · 一体化深度解读

---

## 【定位】

本篇文档系统化阐述 TileLang-Ascend 编译系统所采用的 **"两阶段分离 (LowerAndLegalize + OptimizeForTarget)" Pass Pipeline 架构**，逐一列出 33 个 Pass 的执行顺序、输入输出依赖、关键逻辑，以及 C++/Python 双层注册机制与 `PassContext` 配置开关，目的是为开发者提供一份"前端 Lowering → 后端硬件优化"的端到端流水线全景蓝图。

---

## 【技术要点】

1. **两阶段分离的 Pipeline 总体框架**：Phase 1 (`LowerAndLegalize`) 包含 **12 个 Pass**，目标是把 Python DSL 降级为平台无关的标准化 TIR，强调"语义保持、平台无关优化"；Phase 2 (`OptimizeForTarget`) 包含 **21 个 Pass**，目标是在标准化 IR 之上注入 Ascend 硬件特性 (GM/L1/UB/L0A/L0B/L0C、Cube/Vector 多核)，强调"硬件相关、性能导向"。
2. **核心 Lowering Pass (`AscendLowerParallelToVector`、`LowerTileOp`)**：将 `T.Parallel`、`T.copy`、`T.matmul` 等高层原语 lowering 到 Vector 指令与底层硬件操作；其中 `AscendLowerParallelToVector` 被文档标注为 Developer 模式关键 Pass，`LowerTileOp` 被标注为"核心 Lowering Pass，直接对应 DSL API"。
3. **Cube-Vector 核间协作三件套 (`CrossCorePipeline` → `CombineCV` → `PipelinePlanning`)**：在 Phase 2 第 2-4 步连续编排，将操作分离为 Cube (如 matmul) 与 Vector (如 element-wise) 两部分，并规划跨核流水线的阶段划分，是 Ascend 多核架构性能上限的决定因素。
4. **内存与同步三件套 (`AscendStorageRewrite` → `AscendMemoryPlanning` → `AscendSyncInsert`)**：分别在 Phase 2 第 13、20、21 步执行；其中 `AscendStorageRewrite` 负责内存共享与存储重写，`AscendMemoryPlanning` 输出 `address_map` 与 `size_map`，`AscendSyncInsert` 作为 Pipeline 最后一环插入 `T.barrier_all`、`T.set_flag`、`T.wait_flag`。
5. **`buffer_shapess` 作为 Phase 1 → Phase 2 的关键传递媒介**：在 Phase 1 第 8 步由 `CollectBufferShapes()` 生成 (`Map<Var, Array<PrimExpr>>`)，在 Phase 2 第 20 步被 `AscendMemoryPlanning()` 消费，是跨阶段数据契约的核心载体。
6. **C++/Python 双层 Pass 注册 + `PassContext` 配置开关**：C++ 端通过 `TVM_REGISTER_GLOBAL("tl.transform.<Name>").set_body_typed(...)` 注册，Python 端通过 `tvm._ffi._init_api("tl.transform", __name__)` 加载并暴露 `AscendSyncInsert(target, platform)` 等 wrapper；运行时通过 `tvm.transform.PassContext(opt_level=3, config=pass_configs)` 上下文传递 `TL_ASCEND_AUTO_SYNC`、`TL_ASCEND_MEMORY_PLANNING`、`TL_ASCEND_AUTO_CV_COMBINE`、`TL_ASCEND_AUTO_CV_SYNC` 四个配置键（默认均为 `False`）来启用/禁用对应的 Pass。

---

## 【关键机制与数据】

**数据流（跨阶段契约）：**
```
DSL IR ──(AscendInferBufferScope)──> buffer scope annotations
        ──(BufferShapeCollector)──> buffer shapes (初步)
        ──(BindTarget)──> target attr (Ascend NPU)
        ──(Simplify)──> simplified IR
        ──(AscendLowerParallelToVector)──> vectorized IR
        ──(LayoutInference)──> layout annotations
        ──(CollectBufferShapes)──> 【buffer_shapess】 ← 跨阶段关键输出
        ──(LowerTileOp)──> lowered tile ops
        ──(LegalizeVectorizedLoop)──> legalized loops
        ──(LegalizeSafeMemoryAccess)──> safe memory IR
        ──(Simplify)──> final Phase 1 IR
        ↓ Phase 边界
        ──(PlanAndUpdateBufferAllocationLocation)──> buffer allocation plan
        ──(CrossCorePipeline)──> cross-core pipeline
        ──(CombineCV)──> separated CV ops
        ──(PipelinePlanning)──> pipeline layout
        ──(InjectSoftwarePipeline)──> software pipeline
        ──(AscendLowerOpaqueBlock)──> executable IR
        ──(NarrowDataType(32))──> narrowed data types
        ──(ConfigIndexBitwidth)──> configured indices
        ──(Flatten2DBuffer)──> 2D buffers
        ──(FlattenBuffer)──> 1D buffers
        ──(Simplify ×3)──> simplified IR
        ──(VectorizeLoop)──> vectorized loops
        ──(AscendStorageRewrite(is_npu))──> optimized storage
        ──(UnrollLoop)──> unrolled loops
        ──(RenormalizeSplitPattern)──> renormalized patterns
        ──(RemoveNoOp / RewriteUnsafeSelect / HoistIfThenElse)──> 清理 IR
        ──(AscendMemoryPlanning, 消费 buffer_shapess)──> 【address_map, size_map】
        ──(AscendSyncInsert, 消费 address_map + size_map)──> final IR with syncs
        → CANN 工具链 → NPU 执行
```

**Pass 编排四原则（原文）：**
- **依赖优先**：上游 Pass 必须先执行，例如 `AscendInferBufferScope` → `BufferShapeCollector`。
- **数据就绪**：Pass 所需数据必须可用，例如 `AscendMemoryPlanning` 需要 `buffer_shapess`。
- **逻辑连贯**：相关 Pass 集中编排，例如 Lowering 相关 Pass 在 Phase 1 连续编排。
- **优化分层**：基础优化先执行，高级优化后执行；`Simplify` 在多处执行，逐步优化 IR。

**Pass 数量统计（原文）：**
- Phase 1：12 个 Pass。
- Phase 2：21 个 Pass。
- 全 Pipeline 合计：33 个 Pass。

**Ascend 硬件内存层级（原文）：** GM / L1 / UB / L0A / L0B / L0C，其中 L0A/L0B/L0C 是 Cube 核专用寄存器层级，由 `AscendInferBufferScope` 静态推断。

**Developer 模式特性（原文）：** `AscendLowerParallelToVector` 是 Developer 模式的关键 Pass，决定如何执行 Vector 计算。

**性能数据：** 原文未提供具体数字、benchmark、时延或吞吐等量化性能数据。

---

## 【表格解读】

### 表格 1：Pass 编排原则（原文逐字还原）

| 原则 | 说明 | 示例 |
|-----|------|-----|
| **依赖优先** | 上游 Pass 必须先执行 | `AscendInferBufferScope` → `BufferShapeCollector` |
| **数据就绪** | Pass 需要的数据必须可用 | `AscendMemoryPlanning` 需要 `buffer_shapess` |
| **逻辑连贯** | 相关 Pass 集中编排 | Lowering 相关 Pass 在 Phase 1 连续编排 |
| **优化分层** | 基础优化先执行，高级优化后执行 | `Simplify` 在多处执行，逐步优化 IR |

**解读：** 这是整个 Pipeline 编排的"宪法"。四原则分别对应：(a) Pass DAG 的拓扑序；(b) 跨阶段数据契约（如 `buffer_shapess`）；(c) 内聚性（如 Phase 1 中 Lowering 相关 Pass 集中）；(d) 由浅入深的渐进优化（`Simplify` 在 Phase 1 第 5/12 步、Phase 2 第 11/16 步重复出现，是"优化分层"的典型体现）。

---

### 表格 2：Phase 1 Pass 列表（按执行顺序，原文逐字还原）

| 步骤 | Pass | 功能 | 输入依赖 | 输出供给 | 关键逻辑 |
|------|------|------|---------|---------|---------|
| 1 | `AscendInferBufferScope()` | 推断 buffer scope (L1/UB/L0A/L0B/L0C) | DSL IR | buffer scope annotations | 分析 buffer 访问模式，推断内存层级 |
| 2 | `BufferShapeCollector()` | 收集 buffer 形状信息 | buffer scope | buffer shapes (初步) | 为后续 Pass 提供形状信息 |
| 3 | `tir.transform.BindTarget(target)` | 绑定 Target 信息 | IR | target attr | 记录编译目标（Ascend NPU） |
| 4 | `HostProcesser()` | Host 端数据处理 | IR | processed host data | 处理 CPU 端数据准备 |
| 5 | `tir.transform.Simplify()` | 简化 IR 表达式 | IR | simplified IR | 算术简化、常量折叠 |
| 6 | `AscendLowerParallelToVector()` | Parallel 循环 → Vector 指令 | simplified IR | vectorized IR | **核心 Pass**：将高级 Parallel 原语 lowering 到 Vector 指令 |
| 7 | `LayoutInference()` | 推断 fragment/shared memory layout | vectorized IR | layout annotations | 分析数据布局，推断最优 layout |
| 8 | `CollectBufferShapes()` | 再次收集 buffer 形状 | layout annotations | `buffer_shapess` | **关键输出**：为 Phase 2 提供 buffer 形状 |
| 9 | `LowerTileOp()` | Tile 操作 → 底层 IR | buffer shapes | lowered tile ops | **核心 Pass**：将 `T.copy`、`T.matmul` 等 lowering 到具体硬件操作 |
| 10 | `LegalizeVectorizedLoop()` | 合法化向量化循环 | lowered tile ops | legalized loops | 确保向量化循环符合硬件约束 |
| 11 | `LegalizeSafeMemoryAccess()` | 安全内存访问检查 | legalized loops | safe memory IR | 检查内存访问是否越界、是否符合硬件规范 |
| 12 | `tir.transform.Simplify()` | 再次简化 | safe memory IR | final Phase 1 IR | 清理冗余 IR，为 Phase 2 准备 |

**解读：** 12 个 Pass 可分为四组：
- **元信息准备（1-4）**：scope 推断 → 形状收集 → Target 绑定 → Host 处理，奠定 IR 的属性层基础。
- **首轮 Lowering 与简化（5-6）**：`Simplify` 做算术/常量折叠后，`AscendLowerParallelToVector` 完成 Developer 模式的核心 Parallel→Vector lowering。
- **Layout 与形状二次确定（7-8）**：先推断 fragment/shared memory 的最优 layout，再"二次"收集 buffer 形状，得到跨阶段契约 `buffer_shapess`（注意 typo：原文即写作 `buffer_shapess`，带两个 `s`）。
- **Tile 操作 Lowering 与合法化（9-12）**：`LowerTileOp` 把 `T.copy`、`T.matmul` 等 DSL API 直接对应到硬件操作，随后经向量化合法化、安全内存访问检查、最终 `Simplify` 输出 Phase 1 IR。

---

### 表格 3：Phase 2 Pass 列表（按执行顺序，原文逐字还原）

| 步骤 | Pass | 功能 | 输入依赖 | 输出供给 | 关键逻辑 |
|------|------|------|---------|---------|---------|
| 1 | `tir.transform.PlanAndUpdateBufferAllocationLocation()` | Buffer 分配位置规划 | Phase 1 IR | buffer allocation plan | 确定每个 buffer 在代码中的分配位置 |
| 2 | `CrossCorePipeline()` | 跨核流水线规划 | buffer scope, allocation plan | cross-core pipeline | **核心 Pass**：规划 Cube-Vector 核间流水线 |
| 3 | `CombineCV()` | 分离 Cube/Vector 操作 | cross-core pipeline | separated CV ops | 将操作分离为 Cube 和 Vector 两部分 |
| 4 | `PipelinePlanning()` | 流水线 layout 推断 | separated CV ops | pipeline layout | 推断流水线中每个阶段的 layout |
| 5 | `InjectSoftwarePipeline()` | 软件流水线注入 | pipeline layout | software pipeline | 注入软件流水线，提升吞吐量 |
| 6 | `AscendLowerOpaqueBlock()` | Block IR → 可执行 IR | software pipeline | executable IR | 将 Block IR lowering 到可执行形式 |
| 7 | `tir.transform.NarrowDataType(32)` | 数据类型缩窄 | executable IR | narrowed data types | 缩窄数据类型以减少内存占用 |
| 8 | `ConfigIndexBitwidth()` | 索引位宽配置 | narrowed data types | configured indices | 配置索引变量的位宽 |
| 9 | `Flatten2DBuffer()` | Buffer 扁平化到 2D | configured indices | 2D buffers | 将多维 buffer 扁平化为 2D |
| 10 | `FlattenBuffer()` | Buffer 扁平化到 1D | 2D buffers | 1D buffers | 将 2D buffer 扁平化为 1D |
| 11 | `tir.transform.Simplify()` | 简化 | 1D buffers | simplified IR | 清理扁平化后的冗余 IR |
| 12 | `VectorizeLoop()` | 循环向量化（可配置） | simplified IR | vectorized loops | 将循环转换为向量指令 |
| 13 | `AscendStorageRewrite(is_npu)` | 存储重写优化 | vectorized loops | optimized storage | **核心 Pass**：优化内存访问模式，共享存储 |
| 14 | `tir.transform.UnrollLoop()` | 循环展开 | optimized storage | unrolled loops | 展开小循环以提升性能 |
| 15 | `tir.transform.RenormalizeSplitPattern()` | 重规范化分割模式 | unrolled loops | renormalized patterns | 规范化循环分割模式 |
| 16 | `tir.transform.Simplify()` | 简化 | renormalized patterns | simplified IR | 清理展开后的冗余 IR |
| 17 | `tir.transform.RemoveNoOp()` | 移除空操作 | simplified IR | no-op removed | 删除无实际作用的 IR |
| 18 | `tir.transform.RewriteUnsafeSelect()` | 重写不安全 select | no-op removed | safe select | 重写可能导致硬件异常的 select |
| 19 | `tir.transform.HoistIfThenElse()` | 提升 if-then-else | safe select | hoisted conditionals | 提升 if-then-else 以减少分支开销 |
| 20 | `AscendMemoryPlanning()` | 内存规划 | `buffer_shapess` | `address_map`, `size_map` | **关键 Pass**：规划 buffer 地址，输出地址映射 |
| 21 | `AscendSyncInsert()` | 同步插入 | `address_map`, `size_map` | final IR with syncs | **最后一环**：插入同步指令 |

**解读：** 21 个 Pass 可分为五段：
- **核间流水线规划（1-5）**：从 buffer 分配位置出发，连续编排 `CrossCorePipeline → CombineCV → PipelinePlanning → InjectSoftwarePipeline`，构成 Ascend 多核性能上限的核心链路；`PipelinePlanning` 与 `InjectSoftwarePipeline` 形成"layout 推断 → 软件流水线注入"的二段式协作。
- **Lowering 与位宽优化（6-8）**：`AscendLowerOpaqueBlock` 把 Block IR 转为可执行 IR；`NarrowDataType(32)` 把数据位宽缩到 32，`ConfigIndexBitwidth` 再把索引位宽做硬件适配——两者构成"数据/索引"两条位宽优化路径。
- **Buffer 扁平化（9-11）**：先 `Flatten2DBuffer` 再 `FlattenBuffer`，由 N 维 → 2D → 1D 逐步扁平化，并以 `Simplify` 收尾。
- **向量化 + 存储重写 + 循环展开（12-16）**：`VectorizeLoop` 完成循环向量化（文档标注"可配置"），`AscendStorageRewrite(is_npu)` 优化内存访问与共享存储，`UnrollLoop` + `RenormalizeSplitPattern` + `Simplify` 联合做循环展开规范化。
- **IR 清理 + 内存规划 + 同步插入（17-21）**：`RemoveNoOp → RewriteUnsafeSelect → HoistIfThenElse` 完成 IR 安全清理；`AscendMemoryPlanning` 跨阶段消费 Phase 1 产出的 `buffer_shapess`，生成 `address_map` 与 `size_map`；`AscendSyncInsert` 作为最后一环，插入 `T.barrier_all / set_flag / wait_flag`，保证执行正确性。

---

### 表格 4：Pass 配置键定义（原文逐字还原）

| 配置键 | 默认值 | 启用对象 |
|-----|-------|---------|
| `TL_ASCEND_AUTO_SYNC` (`tl.ascend_auto_sync`) | `False` | `AscendSyncInsert` |
| `TL_ASCEND_MEMORY_PLANNING` (`tl.ascend.memory_planning`) | `False` | `AscendMemoryPlanning` |
| `TL_ASCEND_AUTO_CV_COMBINE` (`tl.ascend_auto_cv_combine`) | `False` | `CombineCV` |
| `TL_ASCEND_AUTO_CV_SYNC` (`tl.ascend_auto_cross_core_sync`) | `False` | `CrossCorePipeline` |

**解读：** 四个配置键默认均为 `False`（即默认跳过对应 Pass），表明该 Pipeline 的 Ascend 专用优化属于"按需开启"模式。开发者可通过 `PassContext(config=pass_configs)` 在 `opt_level=3` 下注入这些开关；任一 Pass 内部均通过 `ctx->GetConfig<Bool>(kAscendAutoSync, Bool(false)).value()` 读取配置，并在 `false` 时直接 `return f` 跳过。注意：四个开关对应 Phase 2 链路中的**核间协作 (CrossCorePipeline/CombineCV)** 与**收尾阶段 (MemoryPlanning/SyncInsert)**，而 Phase 1 的 Lowering 链路没有对应配置开关（默认常开）。

---

### 表格 5：关键文件路径（原文截断，仅含表头与首行）

| 类别 | 文件路径 | 说明 |
|-----|---------|------|
| **Pipeline …**（原文此处被截断） | — | — |

**解读：** 原文档"关键文件路径"表只保留了表头与第一行"Pipeline"前缀便被截断，未提供完整路径列表；除此之外，文中已显式给出的文件路径包括：`src/transform/<pass_name>.cc`、`tilelang/transform/_ffi_api.py`、`tilelang/transform/__init__.py`、`tilelang/engine/phase.py:79-105`、`tilelang/jit/kernel.py:223`、`tilelang/transform/pass_config.py`、`src/transform/ascend_sync_insert.cc:65-69`，可用于定位实现。

---

## 【公式解读】

**原文无公式。** 文档以 Pass 编排表、C++/Python 代码片段和自然语言描述为主，未出现 LaTeX 数学公式或伪代码形式的算法表达式。文档中出现的"代码片段"均为：

- C++ 注册：`TVM_REGISTER_GLOBAL("tl.transform.AscendSyncInsert").set_body_typed(AscendSyncInsert);`
- Python 加载：`tvm._ffi._init_api("tl.transform", __name__)`
- Python Wrapper：`def AscendSyncInsert(target: Target, platform: str): return _ffi_api.AscendSyncInsert(target, platform)`
- Pipeline 调用框架：`def OptimizeForTarget(mod, target, platform): mod = AscendMemoryPlanning()(mod); mod = AscendSyncInsert(target, platform)(mod); return mod`
- 配置读取：`bool ascend_auto_sync = ctx->GetConfig<Bool>(kAscendAutoSync, Bool(false)).value();`

这些属于代码示例而非数学/算法公式，故按要求标注为"原文无公式"。

---

## 【关联】

本篇文档位于 `.agents/skills/tilelang-pass-workflow-analyzer/references/pass-pipeline-overview.md`，是 **tilelang-pass-workflow-analyzer** Skill 的 references 引用文件之一。从其内容结构与定位看：

- **与 Phase 1 / Phase 2 Pass 列表的关联**：表格中列出的 33 个 Pass 名称（如 `AscendSyncInsert`、`AscendMemoryPlanning`、`CrossCorePipeline`、`CombineCV`、`AscendStorageRewrite`）是后续 Pass 级别深度文档的索引锚点；本文档中"关键 Pass 说明"小节已经为 6 个核心 Pass（`AscendInferBufferScope`、`AscendLowerParallelToVector`、`LowerTileOp`、`CollectBufferShapes`、`CrossCorePipeline`、`CombineCV`、`InjectSoftwarePipeline`、`AscendStorageRewrite`、`AscendMemoryPlanning`、`AscendSyncInsert`）提供了功能/逻辑/重要性的"摘要级"描述，对应的"完整级"说明应位于同级 references 目录下其他文档或源文件 `src/transform/<pass_name>.cc` 的注释中。
- **与代码实现的关联**：文档显式引用 `tilelang/engine/phase.py:79-105` 中的 `OptimizeForTarget(mod, target, platform)` 函数、`tilelang/jit/kernel.py:223` 的 `PassContext` 用法、`tilelang/transform/pass_config.py` 的 `PassConfigKey` 枚举、`tilelang/transform/_ffi_api.py` 的 FFI 加载入口、`tilelang/transform/__init__.py` 的 Python Wrapper、`src/transform/ascend_sync_insert.cc:65-69` 的配置读取——这些是 Pipeline 在源码层的"投影位置"，可作为按图索骥的入口。
- **与 `buffer_shapess` 跨阶段契约的关联**：作为唯一被两次显式提及的跨阶段数据属性（一次由 Phase 1 `CollectBufferShapes` 生成、一次被 Phase 2 `AscendMemoryPlanning` 消费），它是文档结构上的"中轴线"，将前后两阶段串联为单一数据流故事。
- **与上下游 Skill 的关联**：本文档属于 `tilelang-pass-workflow-analyzer` Skill 的 references 子文件，上游被 Skill 主入口的 workflow 调度引用，下游可能与更细粒度的 single-pass 详解、错误排查指南、性能调优指南形成 references 网络。

---

## 【使用方法】

文档本身是**架构综述**，未直接给出 CLI/SDK 启用命令，但其描述的机制可被开发者用于以下实践：

1. **在 `PassContext` 中启用 Ascend 专用 Pass（原文代码）：**
   ```python
   with tvm.transform.PassContext(opt_level=3, config=pass_configs):
       # pass_configs 中注入以下键以启用对应 Pass（默认均为 False）
       pass_configs = {
           "tl.ascend_auto_sync": True,               # 启用 AscendSyncInsert
           "tl.ascend.memory_planning": True,          # 启用 AscendMemoryPlanning
           "tl.ascend_auto_cv_combine": True,          # 启用 CombineCV
           "tl.ascend_auto_cross_core_sync": True,     # 启用 CrossCorePipeline
       }
   ```
2. **通过 `@tilelang.jit` 触发全 Pipeline**：由架构总览图可知，从 `@tilelang.jit` 装饰的 DSL kernel 出发，Pipeline 会自动依次执行 Phase 1（12 Pass）→ Phase 2（21 Pass）→ CANN 工具链 → NPU 执行。
3. **在 Python 侧直接调用单 Pass（原文代码示例）：**
   ```python
   from tilelang.transform import AscendSyncInsert
   mod = AscendSyncInsert(target, platform)(mod)
   ```
4. **在 Python 侧直接调用 `OptimizeForTarget` 入口（原文代码示例）：**
   ```python
   from tilelang.engine.phase import OptimizeForTarget
   mod = OptimizeForTarget(mod, target, platform)
   ```

**备注：** 关于"如何新增一个 Pass、新增一类优化、或在何处挂载自定义配置键"的开发者扩展指南，原文未涉及；表格 5（关键文件路径）的完整内容在原文末尾被截断，因此具体的文件清单不完整。
