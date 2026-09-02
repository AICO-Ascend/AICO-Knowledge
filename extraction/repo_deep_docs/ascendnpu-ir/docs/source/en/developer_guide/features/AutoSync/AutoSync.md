# Auto-Sync

> 仓 `ascendnpu-ir` · 路径 `docs/source/en/developer_guide/features/AutoSync/AutoSync.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/en/developer_guide/features/AutoSync/AutoSync.md

# Auto-Sync 文档深度解读

---

## 【定位】

本篇文档描述 AscendNPU-IR（HIVM）编译器中的 **Auto-Sync 能力**——自动在共享数据/资源的生产者与消费者之间插入同步操作，以保证**正确性**（无数据竞争或顺序错乱）且**开销最小**（最少同步、必要时复用硬件事件）。

---

## 【技术要点】

1. **同步原语分两层**：
   - **核内同步（Intra-Core-Sync）**：`hivm.set_flag`、`hivm.wait_flag`、`hivm.pipe_barrier`，定义于 `bishengir/include/bishengir/Dialect/HIVM/IR/HIVMSynchronizationOps.td`。
   - **跨核同步 / 块内同步（Cross-Core-Sync, Intra-Block）**：`hivm.sync_block_set`、`hivm.sync_block_wait`；另有 `hivm.sync_block`（多模式块屏障）、`hivm.anchor`（延迟跨核分析的位置标记）。

2. **两套解决方案族**：
   - **默认路径**：`GraphSyncSolver` / `CrossCoreGSS` / `DelayedCrossCoreGSS`（基于图的分析，默认开启 `--enable-hivm-graph-sync-solver` 与 `--enable-hivm-cross-core-gss`）。
   - **回退路径**：`InjectSync` / `InjectBlockSync`（基于内存依赖的注入式分析，仅在 graph-sync 被关闭或启用 barrier-all / block-all 调试模式时使用）。

3. **GraphSyncSolver 三阶段管线**：`IRTranslator`（构建 Sync-IR）→ `Solver`（`SyncSolverV1` / `SyncSolverV2`，**默认 v2**，收集冲突对、成对选择、图可达性排序、分配/复用 event id，可选 unit-flag 与 custom-macro 预留）→ `CodeGenerator`（发射 `hivm.set_flag` / `hivm.wait_flag` / `hivm.pipe_barrier`）。

4. **CrossCoreGSS 仅在 MIX 核（cube + vector）运行**：复用同一套 `IRTranslator`/`SyncSolver`/`CodeGenerator`，但配置为 `CROSS_CORE_SYNC`；在基于内存的架构（如 **Ascend910B**）上，当存在 FFTS base-addr 内核参数时插入 `SetFFTSBaseAddrOp`；支持 CV pattern、multibuffer flag-id、内存架构上的轮询 event-id 重试、block-all 模式。

5. **DelayedCrossCoreGSS 用于 RegBase 管线**：在 mix-kernel **拆分之后**再解析跨核同步，配合 `InsertAnchorsAndBackup` Pass（pass 名 `hivm-insert-anchors-and-backup`）插入 `hivm.anchor` 并克隆一份备份 mix 函数以保留位置 RW 信息；启用条件为 `--enable-hivm-cross-core-gss` 与 `--enable-hivm-delayed-cross-core-gss` 同时为真（RegBase 上两者默认 `true`）。

6. **InjectSync 六阶段管线**：`IRTranslator` → `SyncAnalyzer`（按冲突对插入 set/wait，同 pipe 时插入 `pipe_barrier`）→ `MoveSyncState`（重定位以减少 stall）→ `RemoveRedundantSync`（去除冗余对）→ `SyncEventIdAllocation`（静态/动态 event id，安全时复用）→ `SyncCodegen`（发射 sync op）。调试开关 `--enable-hivm-inject-barrier-all-sync` 会在内存效应操作前直接插入 `pipe_barrier(PIPE_ALL)`，跳过常规分析路径。

7. **InjectBlockSync 子模式**（由选项与 fusion kind 控制）：
   - `InjectAllBlockSync`：每次相关 handoff 都发射 block sync（`--enable-hivm-inject-block-all-sync`）。
   - `InjectBlockShallowSync`：针对 `ShallowCV` fusion，围绕 matmul / mix-matmul / call site 同步。
   - `InjectBlockMixSync`（原文此处被截断）。

---

## 【关键机制与数据】

> 以下均为**原文原文**所描述的机制，未做扩展。

**工作原理 / 数据流：**

- **Intra-Core set/wait 对的工作原理（原文）**：
  > `hivm.set_flag` 在 `set_pipe` 上、在该 pipe 上先前所有指令完成后执行，并触发对应 event id；`hivm.wait_flag` 在 `wait_pipe` 上执行，阻塞该 pipe 上后续所有指令，直到匹配的 event id 被触发；`hivm.pipe_barrier(pipe)` 阻塞该 pipe 上后续所有指令，直到该 pipe 上先前所有指令完成。

- **Cross-Core block-sync 工作原理（原文）**：
  > `hivm.sync_block_set` 在目标 `tcore_type` 核的 `tpipe`（set pipe）上、当该 pipe 上先前所有指令完成后执行并置位 flag id；`hivm.sync_block_wait` 在目标 `tcore_type` 核的 `pipe`（wait pipe）上执行，阻塞该 pipe 上后续所有指令，直到匹配的 flag id 被触发。

- **GraphSyncSolver 默认路径（原文）**：
  > 默认 `--enable-hivm-graph-sync-solver` 与 `--enable-hivm-cross-core-gss` 均为 `true`；在 RegBase 上，`--enable-hivm-delayed-cross-core-gss` 默认也为 `true`。

- **Solver V1 vs V2（原文）**：
  > Solver 阶段支持 `SyncSolverV1` 与 `SyncSolverV2`，**默认 v2**；可选地应用 unit-flag 和 custom-macro 预留。

- **DelayedCrossCoreGSS 两步流程（原文）**：
  > Step 1（拆分前）：运行 CrossCoreGSS（通常禁用 CV pattern），随后运行 `InsertAnchorsAndBackup` 放置 `hivm.anchor` 标记并克隆备份 mix 函数；Step 2（拆分后）：`DelayedCrossCoreGSS` 匹配备份 mix 与拆分后的 cube/vector 函数，移除陈旧的 intra-block 同步，由 anchor 重建区间 RW 信息，求解并物化同步到 mix/cube/vector 函数，最后 cleanup 移除 anchor 与备份。

- **InjectSync 同 pipe 退化为 barrier（原文）**：
  > `SyncAnalyzer` 阶段：针对每对冲突操作插入 set_flag/wait_flag 对；若两个操作位于同一 pipe，则插入 `pipe_barrier`。

- **event-id 复用与重试（原文）**：
  > `SyncEventIdAllocation`：分配静态或动态 event id，安全时可复用；CrossCoreGSS 在基于内存的架构上支持轮询 (round-robin) event-id 重试。

- **Triton-Ascend 入口（原文）**：
  > 在 Triton-Ascend 中可通过 `sync_solver=True` 选择 graph-sync-solver 路径。

- **基于内存架构的 FFTS 处理（原文）**：
  > 在基于内存的架构（如 Ascend910B）上，当存在 FFTS base-addr 内核参数时，CrossCoreGSS 与 InjectBlockSync 都会插入 `SetFFTSBaseAddrOp`（InjectBlockSync 即使在禁用自动 set/wait 插入时也会执行此步）。

**性能数据：** 原文未提供任何量化性能数据。

---

## 【表格解读】

**原文无表格。** 文档以分层小节、加粗算子名与属性名列表的方式组织内容，未呈现任何表格形式的参数/性能对比/配置清单。

---

## 【公式解读】

**原文无公式。** 全文无 LaTeX 表达式、伪代码算法或数学公式。算法逻辑全部以自然语言阶段说明（如 IRTranslator → Solver → CodeGenerator）以及布尔条件（"if both operations are on the same pipe → pipe_barrier"）表达。

---

## 【关联】

> 以下关联均严格来自原文所提到的路径、pass 名、op 名与上文小节。

- **HIVM 同步原语定义** ↔ `bishengir/include/bishengir/Dialect/HIVM/IR/HIVMSynchronizationOps.td`（set_flag / wait_flag / pipe_barrier / sync_block_set / sync_block_wait / sync_block / anchor 在此声明）。
- **GraphSyncSolver 三组件** ↔
  - 头：`bishengir/include/bishengir/Dialect/HIVM/Transforms/GraphSyncSolver/`
  - 实现：`bishengir/lib/Dialect/HIVM/Transforms/GraphSyncSolver/`
    - `GraphSyncSolver.cpp`（顶层调度）
    - `SyncSolverBase.cpp` / `SyncSolverV1.cpp` / `SyncSolverV2.cpp`（求解器，默认 v2）
    - `SyncSolverIR.cpp` / `SyncSolverIRTranslator.cpp`（Sync-IR 构建）
    - `SyncSolverCodeGen.cpp`（发射 set_flag / wait_flag / pipe_barrier）
    - `GraphSolver.cpp` / `GraphSolverBase.cpp` / `GraphSolverUnitFlag.cpp`（图求解、unit-flag 模式）
    - `EventIdSolver.cpp`（event id 分配/复用）
    - `MemInfo.cpp` / `CustomMacroSync.cpp` / `Utility.cpp`（辅助）
- **CrossCoreGSS** ↔ `CrossCoreGSS.cpp`；**复用** GraphSyncSolver 的 `IRTranslator` / `SyncSolver` / `CodeGenerator`（配置为 `CROSS_CORE_SYNC`），并依赖 `SetFFTSBaseAddrOp` 处理内存架构（如 Ascend910B）。
- **DelayedCrossCoreGSS** ↔
  - 实现：`DelayedCrossCoreGSS.cpp`
  - 配套 Pass：`InsertAnchorsAndBackup.cpp`，pass 名 `hivm-insert-anchors-and-backup`
  - 依赖：`hivm.anchor`（位置标记）+ backup mix function 克隆，用于在 cube/vector 拆分后保留位置 RW 信息。
- **InjectSync** ↔
  - 头：`bishengir/include/bishengir/Dialect/HIVM/Transforms/InjectSync/`
  - 实现：`bishengir/lib/Dialect/HIVM/Transforms/InjectSync/`
    - `InjectSync.cpp`（顶层）
    - `MemoryDependentAnalyzer.cpp`（内存依赖分析）
    - `SyncAnalysis.cpp`（冲突分析）
    - `SyncEventIdAllocation.cpp`（event id 分配）
    - `IRTranslator.cpp`（Sync-IR 构建）
    - `SyncCodegen.cpp`（发射 sync op）
    - `MoveSyncState.cpp` / `RemoveRedundantSync.cpp`（重定位/去冗余）
    - `SyncCommon.cpp` / `SyncDebug.cpp`（公共 + 调试）
- **InjectBlockSync** ↔
  - 实现：`bishengir/lib/Dialect/HIVM/Transforms/InjectBlockSync.cpp`
  - 头：`bishengir/include/bishengir/Dialect/HIVM/Transforms/InjectBlockSync.h`
  - 子模式：`InjectAllBlockSync` / `InjectBlockShallowSync` / `InjectBlockMixSync`（由选项与 fusion kind 控制）。
- **Triton-Ascend 前端** ↔ 通过 `sync_solver=True` 映射到 graph-sync-solver 路径。
- **架构层分支**：基于内存的架构（如 Ascend910B）会引入 `SetFFTSBaseAddrOp`、可选 `ffts_base_addr` 属性、以及 round-robin event-id 重试；`tcore_type` 可取 `vector` / `cube`，仅 **MIX** 核触发 CrossCoreGSS / DelayedCrossCoreGSS / InjectBlockSync。
- **`tsync_instr_mode`** 属性 ↔ 默认值 `INTRA_BLOCK_SYNCHRONIZATION`（在 `sync_block_set` / `sync_block_wait` 上声明）。

---

## 【使用方法】

> 原文提供的编译/调试开关与调用入口如下；未提供的内容（如环境变量、配置文件示例）原文未涉及。

**编译选项（CL / 编译标志，原文）：**

| 选项 | 默认值 | 作用（原文） |
|---|---|---|
| `--enable-hivm-graph-sync-solver` | `true` | 启用图求解器路径（默认路径）。 |
| `--enable-hivm-cross-core-gss` | `true` | 启用 CrossCoreGSS 块级跨核同步。 |
| `--enable-hivm-delayed-cross-core-gss` | `true`（RegBase 上） | 在 RegBase 管线启用拆分后再解析的 DelayedCrossCoreGSS；需前两项同时为真才生效。 |
| `--enable-hivm-inject-barrier-all-sync` | 原文未给出默认 | 调试模式：在内存效应操作前插入 `pipe_barrier(PIPE_ALL)`，跳过常规 SyncAnalyzer 路径。 |
| `--enable-hivm-inject-block-all-sync` | 原文未给出默认 | 触发 `InjectAllBlockSync`：每次相关 handoff 都发射 block sync。 |

**前端入口：**
- **Triton-Ascend**：通过 `sync_solver=True` 切到 graph-sync-solver 路径。

**算子属性 / 操作数（直接控制同步，原文）：**
- `hivm.set_flag`：`set_pipe`, `wait_pipe`, `static_event_id` 和/或 `dynamic_event_id`。
- `hivm.wait_flag`：同上。
- `hivm.pipe_barrier`：`pipe`。
- `hivm.sync_block_set`：`tcore_type`（vector/cube）、`tpipe`、`pipe`、`static_flag_id` 和/或 `dynamic_flag_id`、可选 `ffts_base_addr`（基于内存架构如 Ascend910B 必填）、`tsync_instr_mode`（默认 `INTRA_BLOCK_SYNCHRONIZATION`）。
- `hivm.sync_block_wait`：`tcore_type`、`tpipe`、`pipe`、`static_flag_id` 和/或 `dynamic_flag_id`、`tsync_instr_mode`。

**Pass 显式调用（原文）：**
- `hivm-insert-anchors-and-backup`（由 `InsertAnchorsAndBackup.cpp` 提供，DelayedCrossCoreGSS 的 Step 1 使用）。

**Fusion kind 与子模式选择（原文）：**
- `ShallowCV` fusion → `InjectBlockShallowSync`（围绕 matmul / mix-matmul / call site）。
- `InjectBlockMixSync`（原文末尾被截断，未给出触发条件完整描述）。

> 原文未涉及的内容：API 调用示例、配置文件 schema、`sync_solver=True` 的默认值、与具体 IR 转换 hook 的对接流程——均**原文未涉及**。

## 图文联合解读

- `auto_sync1.png`: **1) 图中内容**：展示 `graph-sync-solver pass` 流水线。输入 MLIR 经 `ir-translator` → `unroll and collect processing-orders` → `planner`（内含 event-id solver、处理 processing-orders 与冲突对、graph-solver 检测 sync-pair 链）→ `post-solver optimizations` → `code-gen (mlir-rewriter)` → 输出 MLIR；另有 `event-id ran out strategies`（widen sync pairs / barrier-all inserter / outer backward sync pairs）作为 event id 耗尽时的回退分支。

**2) 技术结论**：Auto-Sync 是一条分层 IR 变换流水线：先建模处理序，再用图算法求解 sync-pair 链保证正确性，event-id 求解与回退策略兼顾最小开销与硬件资源复用。

**3) 与文档关系**：直接对应文档"correctness + minimal overhead + 安全复用硬件 event"的目标——planner/graph-solver 负责正确性，event-id 求解与 ran-out 策略负责开销最小化。
- `auto_sync0.png`: 1) **图示内容**：方框图展示 Auto-Sync 编译流程，左列 IRTranslator→SyncAnalyzer→MoveSyncState 通过弯箭头连至右列 RemoveRedundantSync→EvectIdAllocation→SyncCodeGen，SyncDebug 独立置底。

2) **技术结论**：Auto-Sync 由"分析—插入—去重—分配—生成—调试"多遍流水线串接，强调先建模再优化、后端代码生成。

3) **文档对应**：契合"正确性+最小开销"目标——SyncAnalyzer/MoveSyncState 保障正确性，RemoveRedundantSync/EvectIdAllocation 实现事件复用以降低开销。
