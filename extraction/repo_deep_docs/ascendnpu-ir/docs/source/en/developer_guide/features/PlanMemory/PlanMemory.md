# Plan Memory

> 仓 `ascendnpu-ir` · 路径 `docs/source/en/developer_guide/features/PlanMemory/PlanMemory.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/en/developer_guide/features/PlanMemory/PlanMemory.md

# PlanMemory 文档一体化深度解读

---

## 【定位】

本文档系统描述了 HIVM Dialect 中 `PlanMemoryPass` 这一变换（Transformation）——它解决的是 **Ascend 片上存储（on-chip memory）地址规划问题**：在输入 IR 中 `memref.alloc` 仅含缓冲区的名称与尺寸但无地址的背景下，PlanMemory 基于缓冲区生命周期（lifetime）为 IR 中所有缓冲区显式分配片上地址（UB/L1/L0C/Workspace），并在片上容量受限时通过复用策略在内存占用与流水线性能之间取得平衡。

---

## 【技术要点】

1. **片上存储 buffer 模型与对齐约束**：Ascend 采用显式地址控制的 buffer 架构。不同 buffer 有不同的对齐要求——UB/L1 为 32 字节，L0A/L0B/L0C 为 512 字节，BT/FP 为 64 字节。所有实际占用的 buffer 空间会自动按对应对齐大小向上对齐。

2. **三步主流程**：实现位于 `bishengir/lib/Dialect/HIVM/Transforms/PlanMemory.cpp`，依次为 ① **Lifetime analysis**（基于社区 `Liveness` 遍历 `scf.for`/`scf.if`/`scf.while` 收集 gen/kill，计算每个 buffer 的 BufferLife）→ ② **Memory allocation**（从生命周期与复用规则推导地址）→ ③ **OP rewrite**（用 `hivm.hir.pointer_cast(offset)` 替换原 `alloc`，并回填起始地址）。

3. **两种分配模式**：当所有 buffer 大小总和能装入一个 **Memory Scope**（如 UB、L1）时使用 **sequential**（顺序分配）；否则切换为 **reuse**（复用分配），复用又包含 **inplace** 与 **三级复用（Level2/Level1/Level0）**。

4. **Inplace 三条件**：① 处于同一 Memory Scope（如均为 UB）；② 形如 `A = B + C`，其中 A 的 kill 等于 C 的 gen；③ 硬件 inplace 约束满足。满足后 output 与 input 共用同一基址。

5. **三级复用按高级别优先、回退低级别**：**Level2** 优先复用同流水线（pipeline type）缓冲区，避免跨流水线（MTE_PIPE ↔ V_PIPE）引入额外依赖；**Level1** 在同一 loop 中当单 buffer 欲复用双 buffer 的一个 slot 时，将单 buffer 升级为双 buffer，避免流水线停顿；**Level0** 不区分流水线，任取两个生命周期不重叠的 buffer 共享地址以追求最大复用。

6. **Workspace 机制**：PlanMemory 还为 CV 流程分配少量 Workspace（`memref_ext.alloc_workspace`），用于 Cube 结果从 L0C 经 Workspace 暂存再转入 UB 的中间过渡，其大小会上报 framework runtime。

---

## 【关键机制与数据】

**工作原理（数据流）：**
- 原文：输入 IR 中 `memref.alloc` 仅含 name 与 size，无地址 → PlanMemory 基于 lifetime 计算非重叠缓冲区的偏移量（offset）→ 将 `memref.alloc`（`LOCAL_MEM_PLAN`）与 `memref_ext.alloc_workspace`（`GLOBAL_WORKSPACE_PLAN`）整体替换为 `hivm.hir.pointer_cast(offset)`，offset 为该 memory space 内的字节偏移。
- 原文：复用判定核心是 **non-overlapping lifetimes**（生命周期不重叠的 buffer 可以共享同一偏移）。BufferLife 由「first write (gen) → last read (kill)」界定；**Alias** 关系（如 `subview` 前后）用于识别 inplace 候选并赋同基址。

**Cube 与 Vector 的存储分工（原文）：**
- 原文：Cube（矩阵）使用 **L0A**（左矩阵，如 feature map，512B 对齐）、**L0B**（右矩阵，如 weight，512B 对齐）、**L0C**（矩阵乘结果与中间结果，512B 对齐），三者从 L1 加载；PlanMemory 主要为 L1 与 L0C 分配地址。
- 原文：Vector 访问 **UB**，存储 vector 计算的输入与输出；PlanMemory 也在 UB 内为不同缓冲区分配空间。
- 原文：若 Cube 后接 Vector 计算，需将 Cube 结果从 L0C 搬出至 Workspace，再进入 UB。

**三级复用的流水线行为（原文）：**
- 原文：不同 PIPE（MTE_PIPE / V_PIPE）可并行。Level2 选择「同流水线复用」——例如示例中 C 复用 B（同为 Vector OP，V_PIPE 本就串行，复用不引入跨流水线依赖）；若 C 复用 A（DMA），则 op1（MTE_PIPE）须等 op4（V_PIPE），破坏 MTE_PIPE 与 V_PIPE 并行。
- 原文：Level1 解决「单 buffer 复用双 buffer 单 slot」导致的流水线停顿——示例中 C 升级为双 buffer 后，op1 用 A0、op3 用 C1（backed by A1），实现 load-compute overlap 而不互相等待。

**性能权衡（原文）：**
- 原文：Level2 优点——同流水线复用不增加跨流水线依赖，整体性能更优；缺点——可复用空间较小，复用成功率可能更低。
- 原文：Level1 优点——避免双缓冲场景下的流水线停顿；缺点——需为新双 buffer 多分配一个 slot，复用成功率可能下降。
- 原文：Level0 优点——实现最大化复用；缺点——忽略流水线结构，不当复用会损害性能。

**失败时的量化示例（原文错误信息）：**
- 原文：`requires 3219456 bits while 1572864 bits available!`——当任一时刻活跃缓冲区的总大小超出该 scope 实际硬件容量时，PlanMemory 报 `UB overflow`（或对应 scope 的 overflow）并失败；提示可能的诱因为 tiling 基本块过大或多缓冲（multi-buffer）启用后部分 op 占用额外 local buffer。

---

## 【表格解读】

### 表格 1：Buffer 对齐要求（原文逐字还原）

| Buffer | Alignment | Role |
|-----|-----|-----|
| Unified Buffer (UB) | 32 bytes | General cache for vector/scalar ops |
| L1 Buffer | 32 bytes | Temporary feature maps and other convolution data |
| L0A Buffer | 512 bytes | Temporary left matrix (e.g. feature map) for matrix ops |
| L0B Buffer | 512 bytes | Temporary right matrix (e.g. weight) for matrix ops |
| L0C Buffer | 512 bytes | Temporary matrix op intermediate and output |
| BT Buffer | 64 bytes | BiasTable for matrix bias |
| FP Buffer | 64 bytes | Fixpipe: quantization/ReLU parameters, etc. |

**逐行解读：**
- **UB / L1 Buffer（32 bytes）**：通用缓存与卷积临时 feature map，面向 vector/scalar 运算与卷积数据；32B 对齐反映了向量访存的最小粒度。
- **L0A / L0B / L0C Buffer（512 bytes）**：均为 Cube（矩阵）单元配套的临时缓冲——L0A 装左矩阵（如 feature map），L0B 装右矩阵（如 weight），L0C 装矩阵乘结果与中间输出；512B 对齐说明矩阵访存按更大的矩阵行粒度进行。
- **BT Buffer（64 bytes）**：BiasTable，承载矩阵运算的 bias 参数；64B 对齐介于向量与矩阵之间。
- **FP Buffer（64 bytes）**：Fixpipe 相关，承载量化/ReLU 等参数；64B 对齐同样介于通用与矩阵粒度之间。

### 表格 2：API 选项（原文逐字还原）

| Option | Default Value | Description |
|--------|--------|--------|
| `-mem-plan-mode=global-work-space-plan` | false | Use `GLOBAL_WORKSPACE_PLAN` in the CV pipeline. |
| `enable-global-workspace-reuse` | false | Reuse buffers in the workspace. |
| `restrict-inplace-as-isa` | false | Restrict inplace to match ISA behavior. |

**逐行解读：**
- **`-mem-plan-mode=global-work-space-plan`**：默认 `false`（即默认走 `LOCAL_MEM_PLAN`）；启用后在 CV 流程中使用 `GLOBAL_WORKSPACE_PLAN`（即把 `memref_ext.alloc_workspace` 纳入 PlanMemory 的地址规划）。
- **`enable-global-workspace-reuse`**：默认 `false`；启用后允许在 workspace 内部复用缓冲区。
- **`restrict-inplace-as-isa`**：默认 `false`；启用后收紧 inplace 条件，使其严格匹配 ISA 行为——意味着原本可 inplace 的 op 在该开关下可能被拒绝共用偏移，以规避 ISA 不允许的覆盖语义。

---

## 【公式解读】

原文无公式。文档未给出 LaTeX 或伪代码形式的数学公式；其中 `Shared A [A0, A1]`、`op1(A0, A1) // DMA OP, Double Buffer` 等代码片段属于三级复用章节的伪代码示例，用以阐释流水线行为而非表达代数关系。

---

## 【关联】

- **HIVM Dialect**：PlanMemory 是 `bishengir/lib/Dialect/HIVM/Transforms/PlanMemory.cpp` 实现的 Pass，最终生成 `hivm.hir.pointer_cast` 这类 HIVM 自有算子，故属于 HIVM 变换链的一环。
- **MLIR 基础结构**：依赖 MLIR 社区 `Liveness` 分析，并遍历 `scf.for` / `scf.if` / `scf.while` 等结构化控制流，是标准的 MLIR Pass 实现范式。
- **MemRef 与 Workspace 扩展**：上游消费 `memref.alloc`（记为 `LOCAL_MEM_PLAN`）与 `memref_ext.alloc_workspace`（记为 `GLOBAL_WORKSPACE_PLAN`），下游产出 `hivm.hir.pointer_cast(offset)`；同时与 `subview` 产生的 Alias 关系耦合以识别 inplace。
- **硬件单元**：分配目标直接绑定到 Ascend 片上存储单元（**UB**、**L1**、**L0A/L0B/L0C**、**BT**、**FP**），并面向 **Cube（矩阵）** 与 **Vector** 两条计算路径的不同 buffer 拓扑；Workspace 是 Cube → Vector 数据迁移的中转。
- **流水线（PIPE）模型**：Level2 复用策略显式区分 **MTE_PIPE（DMA）** 与 **V_PIPE（Vector）**；Level1 涉及 **Double Buffer** 的 slot 调度，与上层 tiling 阶段的 double-buffer 决策形成约束关系。
- **Tiling 与多缓冲（multi-buffer）**：错误信息中提示 `tiling basic block is too large or block number is more than what user expect due to multi-buffer feature is enabled`——说明 PlanMemory 的容量约束与上游 tiling 阶段、以及是否启用多缓冲存在耦合，是该 Pass 的关键上下游交互点。
- **测试用例**：测试文件 `bishengir/test/Dialect/HIVM/plan-memory.mlir` 给出典型 `CHECK` 用例（验证 `memref.alloc` 被消除、并出现 `hivm.hir.pointer_cast` 形式），与 HIVM 测试基础设施对接。

---

## 【使用方法】

**Pass 启用方式（原文未给出具体 driver/命令行调用方式）**，但提供了三类与 PlanMemory 行为相关的配置项（详见上文【表格解读】中的 API 选项表）：

- `-mem-plan-mode=global-work-space-plan`：默认 `false`；设为启用时在 CV 流程中使用 `GLOBAL_WORKSPACE_PLAN`。
- `enable-global-workspace-reuse`：默认 `false`；启用后允许 workspace 内部缓冲区复用。
- `restrict-inplace-as-isa`：默认 `false`；启用后将 inplace 限制为严格匹配 ISA 行为。

**测试验证（原文）：** 典型 lit CHECK 模板如下：

```mlir
// CHECK-NOT: memref.alloc()
// CHECK: %[[CONST0:.*]] = arith.constant 0 : i64
// CHECK: {{.*}} = hivm.hir.pointer_cast(%[[CONST0]])
```

测试文件路径：`bishengir/test/Dialect/HIVM/plan-memory.mlir`。

**容量约束（原文）：** 任一时刻所有活跃缓冲区总大小不得超过对应 Memory Scope 的实际硬件容量，否则报例如 `UB overflow` 错误（示例：`requires 3219456 bits while 1572864 bits available!`），并提示 tiling 基本块过大或 multi-buffer 启用导致额外 local buffer 占用过多。

## 图文联合解读

- `HardwareStructure.png`: **图文联合解读：**

1）图示展示Atlas A2硬件架构，分AIC（Cube单元）与AIV（Vector单元）两大块，含L0A/L0B/L0C、BT、FP、L1、Unified Buffer等片上存储，通过MTE1/MTE2/MTE3传输引擎与Global Memory/L2 Cache交互，Scalar单元经Instruction Sequence分发至各指令队列。

2）论证了硬件需**显式地址管理**：各Buffer按32/64/512字节对齐且容量受限，数据流与指令流分离。

3）正因片上存储有限且地址需软件编排，PlanMemory必须基于**生命周期**对`memref.alloc`分配地址并执行**Buffer级复用**，以避免溢出覆盖、契合硬件对齐约束，从而支撑算法在受限内存下的正确与高效执行。
- `plan_memory_level2.png`: **图示解读**

1. **画面内容**：上下两组对照，上方 Shared Memory 中 C（黄色）与 A0/A1 同区，对应 Pipeline 中 op1–op4 紧密相接无间隙，标注"Reuse Same PIPE"；下方 C 被置于 B 旁（红圈+箭头示地址迁移），对应 Pipeline 第二段 op1 延后出现，与首段间出现 GAP，标注"Reuse Different PIPE"。

2. **技术结论**：当缓冲区被同一 PIPE 内的操作复用时，Pipeline 无间断；跨 PIPE 复用时，硬件需等待上一 PIPE 释放，产生 GAP，影响吞吐。

3. **与文档关系**：印证 PlanMemory 内存复用策略须遵循 PIPE 边界与生命周期，否则会引入额外数据依赖与性能损耗。
- `plan_memory_level1.png`: **图示解读：**
1) 图对比两种内存分配方案：上图用单缓冲C，下图用双缓冲C0/C1（复用A0/A1空间），右侧对应流水线时序图。
2) 双缓冲复用虽省内存，但因数据依赖产生GAP，使流水线出现等待空档；单缓冲无依赖、空档消失。
3) 印证文档观点：PlanMemory需基于生命周期分析，权衡内存复用与流水线连续性，避免不当复用引入性能惩罚。
- `plan_memory_level0.png`: **图文联合解读：**

图示三部分：左侧为「Buffer Life」表，标注 A 的生命周期 [1,3]、B 为 [4,6]，二者时间不重叠；中间为朴素分配——UB 内分别为 A、B 各自占据独立空间；右侧经红色箭头变换后，A、B 合并为「A/B」共享同一段 UB，并在首部保留 UB 标记。

该图论证了 **PlanMemory 基于生命周期做内存复用**的核心结论：当两个 `memref.alloc` 缓冲的生命区间不重叠时，可让它们复用同一段物理地址。

正对应文档「Algorithm Principle」中「assigns addresses based on lifetime to avoid overwrites」与「performs memory reuse」的论点，是该算法最直观的示意图例。
