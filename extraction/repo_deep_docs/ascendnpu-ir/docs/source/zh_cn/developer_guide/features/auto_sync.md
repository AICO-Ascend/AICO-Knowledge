# 自动同步

> 仓 `ascendnpu-ir` · 路径 `docs/source/zh_cn/developer_guide/features/auto_sync.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/zh_cn/developer_guide/features/auto_sync.md

# 深度解读：AscendNPU-IR Auto-Sync 自动同步功能

## 【定位】

这篇文档描述 AscendNPU IR（HIVM）编译器的 **Auto-Sync（自动同步插入）能力**：在 MLIR 编译流程中自动为共享数据/资源的生产者与消费者插入同步操作，保证执行顺序的正确性，同时尽量最小化同步开销（仅插入必要的同步、安全时复用硬件 event/flag）。

---

## 【技术要点】

1. **两类 Auto-Sync 解决方案（管线选择）**
   - 默认方案：`GraphSyncSolver`（核内）/ `CrossCoreGSS`（跨核，MIX 内核）/ `DelayedCrossCoreGSS`（RegBase 上 mix 拆分之后的跨核）。
   - 回退方案：`InjectSync`（核内）/ `InjectBlockSync`（块内跨核）。
   - 切换依靠编译选项，默认 `--enable-hivm-graph-sync-solver` 与 `--enable-hivm-cross-core-gss` 均为 `true`。

2. **核内同步原语（Normal-Sync）**
   - `hivm.set_flag`：操作数/属性包含 `set_pipe`、`wait_pipe`、事件 ID（`static_event_id` 和/或 `dynamic_event_id`）。在 `set_pipe` 上执行，需等该 pipe 上前序指令完成才执行，并触发事件 ID。
   - `hivm.wait_flag`：操作数/属性同 set_flag；在 `wait_pipe` 上阻塞后续指令直到匹配事件 ID 被触发。
   - `hivm.pipe_barrier`：操作数/属性 `pipe`；阻塞 `pipe` 上所有后续指令直到该 pipe 上前序指令完成。

3. **块内跨核同步原语（Block-Sync）**
   - `hivm.sync_block_set` / `hivm.sync_block_wait`：操作数/属性包含 `tcore_type`（vector/cube）、`tpipe`、`pipe`、flag ID（`static_flag_id` 和/或 `dynamic_flag_id`），可选 `ffts_base_addr`（内存型架构如 Ascend910B 通常需要），`tsync_instr_mode` 默认 `INTRA_BLOCK_SYNCHRONIZATION`。
   - `hivm.sync_block`：多模式块屏障；`hivm.anchor`：用于延迟跨核分析的位置标记；以及 sync-block lock/unlock 辅助操作。

4. **GraphSyncSolver 求解栈（默认 V2）**
   - 三阶段：IRTranslator（构建 Sync-IR）→ Solver（`SyncSolverV1`/`SyncSolverV2`，默认 v2；做冲突对收集、图可达性模型下的对选择与排序、event ID 分配/复用、可选 unit-flag 与 custom-macro 预留）→ CodeGenerator（生成 `set_flag`/`wait_flag`/`pipe_barrier`）。

5. **CrossCoreGSS / DelayedCrossCoreGSS**
   - CrossCoreGSS：复用 GSS 求解栈，配置为 `CROSS_CORE_SYNC`；仅在 MIX 内核（非 Host、非纯 AIC/AIV）运行；内存型架构且 FFTS 基址存在时插入 `SetFFTSBaseAddrOp`；支持 CV pattern、multibuffer flag-id 策略、内存型架构上的 round-robin event-id 重试、block-all 模式。
   - DelayedCrossCoreGSS（RegBase）：Step 1（拆分前）跑 CrossCoreGSS（通常关闭 CV pattern）+ `InsertAnchorsAndBackup`（Pass 名 `hivm-insert-anchors-and-backup`）插入 `hivm.anchor` 并克隆备份 mix 函数；Step 2（拆分后）匹配备份 mix 与拆分后的 cube/vector 函数，清除旧的块内同步，基于 anchor 重建区间读写信息，求解并物化回 mix/cube/vector，最后清理 anchor 与备份函数。当 `--enable-hivm-cross-core-gss` 与 `--enable-hivm-delayed-cross-core-gss` 同时为 true 时启用。

6. **InjectSync / InjectBlockSync（回退路径）**
   - InjectSync 六阶段：IRTranslator → SyncAnalyzer（冲突对插入 set_flag/wait_flag，同 pipe 插入 `pipe_barrier`）→ MoveSyncState（重定位以减少停顿）→ RemoveRedundantSync → SyncEventIdAllocation（静态/动态 ID，安全时复用）→ SyncCodegen。`--enable-hivm-inject-barrier-all-sync` 强制在相关内存效应操作前插入 `pipe_barrier(PIPE_ALL)` 而不走正常分析路径。
   - InjectBlockSync 仅在 MIX 内核上运行；FFTS 基址存在时插入 `SetFFTSBaseAddrOp`（即使禁用自动插入 set/wait 也执行）；含三种模式：InjectAllBlockSync（`--enable-hivm-inject-block-all-sync`）、InjectBlockShallowSync（面向 `ShallowCV` 融合）、InjectBlockMixSync（通过 `SyncBlockIRTranslator` 走完整五阶段 Sync 分析）。

7. **正确性与开销控制原则**
   - 求解器流程要求候选同步约束在基于图的可达性/顺序模型下保持可行（避免死锁或过度约束导致调度失败）；成对的 set/wait 必须共享相同 event/flag id 且 core/pipe 端点兼容。
   - unit-flag 同步仅对支持的操作启用；`--enable-hivm-unit-flag-sync` 在 Ascend950/RegBase 上除非显式指定否则默认启用。
   - `--enable-hivm-assume-alive-loops`（默认 `false`）假设 `for`/`while` 循环至少执行一次，影响 InjectSync/InjectBlockSync 分析。

---

## 【关键机制与数据】

- **数据流（GraphSyncSolver，核内默认路径）**：输入函数 → IRTranslator 构建 Sync-IR（包含函数、作用域、循环、条件、读写操作）→ Solver（默认 V2）收集生产者-消费者冲突对 → 在图可达性模型下做对选择与排序并分配/复用 event ID（可选 unit-flag、custom-macro 预留）→ CodeGenerator 生成 `hivm.set_flag` / `hivm.wait_flag` / `hivm.pipe_barrier`。
- **数据流（CrossCoreGSS，跨核 MIX 内核）**：复用 GSS 求解栈但配置为 `CROSS_CORE_SYNC`；在内存型架构且 FFTS 基址存在时插入 `SetFFTSBaseAddrOp`；产物为 `sync_block_set` / `sync_block_wait`（特殊模式下其他 block sync 形态）。
- **数据流（DelayedCrossCoreGSS，RegBase mix 拆分场景）**：Step 1 在拆分前插入 anchor + 备份 mix 函数；Step 2 在 cube/vector 拆分后基于 anchor 重建区间读写信息并求解，将同步物化回 mix/cube/vector。
- **数据流（InjectSync 回退路径）**：输入函数 → Sync-IR → SyncAnalyzer 插 sync 对 → MoveSyncState 重定位 → RemoveRedundantSync 删除冗余 → SyncEventIdAllocation 分配 ID → SyncCodegen 生成同步 op。
- **默认值**（原文）：
  - `--enable-hivm-graph-sync-solver` = true
  - `--enable-hivm-cross-core-gss` = true
  - `--enable-hivm-delayed-cross-core-gss` = true（RegBase 编译面上同样默认 true）
  - `--hivm-sync-solver-version` = v2
  - `--disable-auto-inject-block-sync` = false
  - `--disable-hivm-auto-inject-sync` = false
  - `--enable-hivm-inject-barrier-all-sync` = false
  - `--enable-hivm-inject-block-all-sync` = false
  - `--enable-hivm-unit-flag-sync` = false*（在 Ascend950/RegBase 上，除非显式指定该标志，否则默认启用）
  - `--enable-hivm-assume-alive-loops` = false
- **原文未提供具体性能数字（吞吐/延迟/耗时对比）**，也未给出 event/flag ID 的数量上限、具体架构下可用 pipe 列表等量化数据。

---

## 【表格解读】

> 原文表格：命令行选项（"接口说明"章节）。下表逐字还原。

| 标志 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--enable-hivm-graph-sync-solver` | bool | true | 使用GraphSyncSolver替代InjectSync进行核内自动同步 |
| `--enable-hivm-cross-core-gss` | bool | true | 使用CrossCoreGSS（或DelayedCrossCoreGSS）替代InjectBlockSync进行跨核自动同步 |
| `--enable-hivm-delayed-cross-core-gss` | bool | true | 在RegBase上，当跨核GSS启用时走延迟跨核GSS（anchors + 拆分后求解） |
| `--hivm-sync-solver-version` | string | v2 | 选择图同步求解器实现版本（`v1`或`v2`） |
| `--disable-auto-inject-block-sync` | bool | false | 禁用自动块级set/wait插入（InjectBlockSync / CrossCoreGSS / DelayedCrossCoreGSS）；FFTS基址设置仍可能执行 |
| `--disable-hivm-auto-inject-sync` | bool | false | 完全禁用核内自动同步（GraphSyncSolver与InjectSync） |
| `--enable-hivm-inject-barrier-all-sync` | bool | false | 强制InjectSync走barrier-all模式（同时覆盖GraphSyncSolver选择）；用于诊断自动同步失败 |
| `--enable-hivm-inject-block-all-sync` | bool | false | 强制块同步走block-all插入（InjectBlockSync / CrossCoreGSS / DelayedCrossCoreGSS） |
| `--enable-hivm-unit-flag-sync` | bool | false* | 对支持的操作启用unit-flag同步。*在Ascend950/RegBase上，除非显式指定该标志，否则默认启用 |
| `--enable-hivm-assume-alive-loops` | bool | false | 假设`for`/`while`循环至少执行一次（影响InjectSync / InjectBlockSync分析） |

逐行解读：

1. **`--enable-hivm-graph-sync-solver`**（bool，默认 `true`）：核心开关，开启后核内走图同步求解器路径，否则回退到 InjectSync。
2. **`--enable-hivm-cross-core-gss`**（bool，默认 `true`）：跨核块同步主开关，开启后使用 CrossCoreGSS（或 DelayedCrossCoreGSS），否则走 InjectBlockSync。
3. **`--enable-hivm-delayed-cross-core-gss`**（bool，默认 `true`）：仅在 RegBase 上且跨核 GSS 启用时生效，把跨核求解延后到 mix 拆分之后，借助 anchor + 备份 mix 恢复位置相关读写信息。
4. **`--hivm-sync-solver-version`**（string，默认 `v2`）：选择图同步求解器实现版本，可选 `v1` 或 `v2`，默认 v2 是当前推荐路径。
5. **`--disable-auto-inject-block-sync`**（bool，默认 `false`）：禁用 InjectBlockSync / CrossCoreGSS / DelayedCrossCoreGSS 的自动 set/wait 插入，但 FFTS 基址设置仍可能执行（用于保留硬件必要配置）。
6. **`--disable-hivm-auto-inject-sync`**（bool，默认 `false`）：完全禁用核内自动同步（同时关闭 GraphSyncSolver 与 InjectSync），用于诊断或手工插入同步的场景。
7. **`--enable-hivm-inject-barrier-all-sync`**（bool，默认 `false`）：调试模式，强制走 InjectSync 的 barrier-all 路径（在相关内存效应操作前插 `pipe_barrier(PIPE_ALL)`），并覆盖 GraphSyncSolver 的选择；用于诊断自动同步失败。
8. **`--enable-hivm-inject-block-all-sync`**（bool，默认 `false`）：调试模式，强制块同步走 block-all 插入路径。
9. **`--enable-hivm-unit-flag-sync`**（bool，默认 `false*`）：开启 unit-flag 同步；带星号说明在 Ascend950/RegBase 上除非显式指定否则默认启用（与表外注释一致）。
10. **`--enable-hivm-assume-alive-loops`**（bool，默认 `false`）：把 `for`/`while` 假设成至少执行一次，影响 InjectSync / InjectBlockSync 的依赖分析。

管线选择摘要（原文补充）：
- **核内**：启用 `--enable-hivm-graph-sync-solver` 且非 barrier-all → GraphSyncSolver；否则 InjectSync（除非设置 `--disable-hivm-auto-inject-sync`）。
- **跨核**：若禁用块同步则跳过；若禁用跨核 GSS 则用 InjectBlockSync；若启用延迟 GSS（RegBase）走 DelayedCrossCoreGSS；否则用 CrossCoreGSS。

---

## 【公式解读】

原文无公式（无 LaTeX、无伪代码形式的同步条件/求解目标函数）。涉及到的"图可达性/顺序模型"仅以文字描述，未给出数学化表达。

---

## 【关联】

文档本身给出的内部链接信息标注为"（无）"，但依据正文可梳理出以下模块/特性间的上下游关系：

- **同步原语定义**：`bishengir/include/bishengir/Dialect/HIVM/IR/HIVMSynchronizationOps.td` 是 HIVM 方言同步 op 的源头；`GraphSyncSolver` / `CrossCoreGSS` / `InjectSync` / `InjectBlockSync` 均以它为产出目标。
- **图同步求解器栈**（共享代码）：`IRTranslator`、`SyncSolver`（V1/V2）、`CodeGenerator` 同时被 `GraphSyncSolver` 与 `CrossCoreGSS` 复用，构成 GSS 家族的共同后端。
- **延迟跨核 Pass**：`InsertAnchorsAndBackup`（Pass 名 `hivm-insert-anchors-and-backup`，源文件 `InsertAnchorsAndBackup.cpp`）是 `DelayedCrossCoreGSS` 的配套前置 Pass；`hivm.anchor` 是它引入的中间标记。
- **回退路径**：`InjectSync` 与 `InjectBlockSync` 共享 `SyncAnalyzer`（`MemoryDependentAnalyzer.cpp`、`SyncAnalysis.cpp`）、`MoveSyncState`、`RemoveRedundantSync`、`SyncEventIdAllocation`、`SyncCodegen`、`SyncCommon`、`SyncDebug`、`IRTranslator`（Inject 侧）；`InjectBlockMixSync` 额外用 `SyncBlockIRTranslator` 构建块同步 IR。
- **Triton-Ascend 前端**：`sync_solver=True` 可让 Triton-Ascend 选用图同步求解器路径，作为上层调用方。
- **驱动与管线**：`bishengir-compile` 驱动、`bishengir/include/bishengir/Tools/bishengir-compile/Options.td`、HIVM `Passes.td`、`bishengir/lib/Dialect/HIVM/Pipelines/` 下的管线实现负责把上述编译选项映射到具体 Pass 调度。
- **外部硬件参考**：文档链接到 Ascend 官方文档《基本架构》描述 AICore 架构，作为 `set_pipe`/`wait_pipe`/`pipe` 概念的硬件背景；内存型架构（如 Ascend910B）的 `ffts_base_addr` 是与硬件特性强耦合的参数。
- **块级同步覆盖关系**：跨核同步面向 MIX 内核（cube/vector handoff），非 MIX 流程（Host、纯 AIC、纯 AIV）不应用 InjectBlockSync / CrossCoreGSS / DelayedCrossCoreGSS，与"使用约束"章节一致。

---

## 【使用方法】

启用/配置方式（原文有）：

1. **命令行选项**：通过编译器驱动（如 `bishengir-compile`）传入表中列出的编译选项（详见"接口说明"章节表格）。
   - 核内：默认走 GraphSyncSolver；可设置 `--hivm-sync-solver-version=v1|v2` 切换求解器实现版本。
   - 跨核：默认走 CrossCoreGSS；RegBase 上默认走 DelayedCrossCoreGSS（`--enable-hivm-delayed-cross-core-gss=true`）；可通过 `--enable-hivm-cross-core-gss=false` 回退到 InjectBlockSync。
   - 调试模式：`--enable-hivm-inject-barrier-all-sync`（核内 barrier-all）、`--enable-hivm-inject-block-all-sync`（块同步 block-all），用于诊断自动同步失败。
   - 关闭自动同步：`--disable-hivm-auto-inject-sync`（核内完全禁用）、`--disable-auto-inject-block-sync`（跨核禁用 set/wait；FFTS 基址设置仍可能执行）。
   - unit-flag：`--enable-hivm-unit-flag-sync`（在 Ascend950/RegBase 上即使不传也默认启用）。
2. **Triton-Ascend 前端**：可通过 `sync_solver=True` 选择图同步求解器路径。
3. **选项到 Pass 的映射**：`bishengir/include/bishengir/Tools/bishengir-compile/Options.td`、HIVM `Passes.td`，以及 `bishengir/lib/Dialect/HIVM/Pipelines/` 下的管线实现。

原文未涉及：具体的 Python/MLIR API 调用示例、CI 验证脚本、单元测试触发方式、端到端算子编译命令模板。

## 图文联合解读

- `auto_sync1.png`: **1) 图示内容**：展示 `graph-sync-solver pass` 的处理流水线。从 `input mlir` 经 `ir-translator` 和 `unroll and collect processing-orders` 进入 `solver`；`solver` 包含 `planner`（含 event-id solver、冲突处理、链式同步检测）与 `event-id ran out strategies`（含 widen sync pairs、barrier-all inserter、考虑外向反向同步），最后经 `post-solver optimizations` 与 `code-gen (mlir-rewriter)` 输出 `output mlir`。

**2) 技术结论**：自动同步插入采用分层pipeline，先规划再按策略回退，体现"最小开销"设计——正常情况精确插入同步对，仅在 event-id 耗尽时降级加宽同步或全屏障。

**3) 与文档关系**：图示对应文档"正确性 + 最小开销"目标，把"自动插入 set_flag/wait_flag/barrier"的硬件同步原语落地为编译pass的具体执行流程与回退策略。
- `auto_sync0.png`: **图解**：左列依次为 IRTranslator→SyncAnalyzer→MoveSyncState；MoveSyncState 横向连入右列 RemoveRedundantSync→EvectIdAllocation→SyncCodeGen；SyncDebug 独立于底部。

**结论**：自动同步采用"分析–状态迁移–冗余消除–ID分配–代码生成"五阶段流水线，先确保正确插入，再以冗余消除与事件ID复用控制开销。

**与文档关系**：对应文档"正确性 + 最小开销"双目标——SyncAnalyzer/MoveSyncState 保证分析正确，RemoveRedundantSync、EvectIdAllocation 体现"安全时复用硬件事件"。
