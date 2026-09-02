# 内存管理

> 仓 `ascendnpu-ir` · 路径 `docs/source/zh_cn/developer_guide/features/plan_memory.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/zh_cn/developer_guide/features/plan_memory.md

# ascendnpu-ir `PlanMemory.md` 一体化深度解读

---

## 【定位】

这篇文档描述 AscendNPU IR 中 HIVM（Heterogeneous Intermediate Representation Virtual Machine）的 **PlanMemoryPass** —— 即片上内存地址规划变换。它解决"输入 IR 中的 `memref.alloc` 只含 Buffer 名字与大小、不含地址信息"的问题，基于生命区间分析与多级分配策略，为 UB/L1/L0C 等片上存储显式规划内存地址偏移，既满足硬件对齐与地址不冲突约束，又通过复用尽量减少内存占用、保障算子流水性能。

---

## 【技术要点】

1. **硬件 Buffer 类型与对齐要求（原文表格）：UB/L1 需 32 字节对齐；L0A/L0B/L0C 需 512 字节对齐；BT/FP 需 64 字节对齐**。每个 Buffer 占用空间会自动按其对齐要求向上取整。
2. **生命区间（BufferLife）分析**：通过社区 `Liveness` 类分析节点活跃性，遍历含 `scf.for`/`scf.if`/`scf.while` 的 IR，收集每个 op 的 gen（首次写入）与 kill（最后一次读取），得到 Buffer 从 gen 到 kill 的执行区间。生命周期不重叠即可共享内存。
3. **三类内存复用**：
   - **Alias 别名**：`subview` 前后数据等本质同源关系。
   - **Inplace 复用**：op 输出可写入输入位置（如等宽 `vcast` f16→i16）。需满足三条件——同 Memory Scope、依赖关系允许（如 `A = B + C` 中 A 的 kill 即 C 的 gen）、符合硬件约束。
   - **三级分配复用**（见下）。
4. **三级分配策略（按优先级从高到低，失败自动降级回滚重试）**：
   - **Level 2：同流水优先复用** —— 优先在非 DMA 的同类型流水内部复用（如 Vector 与 Vector），避免引入 PIPE 间额外依赖。
   - **Level 1：Double Buffer 保护** —— Single Buffer 复用 Double Buffer 时，Single Buffer 自动转 Double Buffer，防止流水被打断。
   - **Level 0：全量生命周期复用** —— 仅按生命周期是否重叠判断，不考虑流水并行约束。
5. **Cube/Vector 计算单元的内存分配侧重点不同**：Cube 相关分配集中在 L1 与 L0C 空间（L0A/L0B 数据由 L1 搬入）；Vector 相关分配集中在 UB 空间。
6. **Workspace 内存分配**：少量 `memref_ext.alloc_workspace`（`GLOBAL_WORKSPACE_PLAN`）用于 CV 场景，Cube 计算完成后结果需经 Workspace 暂存再搬入 UB 给 Vector 使用；片外空间由 Runtime 统一管理，算子仅需反馈所需 Workspace 大小。
7. **OP 变换**：内存地址计算完成后，将 `memref_ext.alloc_workspace`（`GLOBAL_WORKSPACE_PLAN`）与 `memref.alloc`（`LOCAL_MEM_PLAN`）替换为 `hivm.hir.pointer_cast(offset)`，`offset` 为 Buffer 在对应内存空间的字节偏移量。
8. **接口选项（命令行参数，原文表格）**：
   - `-mem-plan-mode=global-work-space-plan`（默认 `false`）：CV 流水线使用 `GLOBAL_WORKSPACE_PLAN`。
   - `enable-global-workspace-reuse`（默认 `false`）：启用 Workspace 内 Buffer 复用。
   - `restrict-inplace-as-isa`（默认 `false`）：限制 inplace 规则以匹配 ISA 行为。

---

## 【关键机制与数据】

### 工作原理（核心流程，原文）

1. **生命区间分析**：对 IR 中每个 Buffer 进行 gen 和 kill 分析；
2. **内存分配**：基于生命区间为各 Buffer 分配内存地址；
3. **OP 变换**：使用 `hivm.hir.pointer_cast(offset)` 替换原 `alloc`，写回起始地址。

> 主流程源文件路径（原文）：`bishengir/lib/Dialect/HIVM/Transforms/PlanMemory.cpp`

### 内存分配模式（原文）

- **顺序分配**：所有 Buffer 内存占用之和能容纳在对应 Memory Scope（UB、L1 等）范围内时使用。
- **可复用分配**：总占用超出对应内存空间大小时使用，包括 Inplace 复用与三级分配复用。

### 三级分配策略示例（原文伪代码场景）

```text
Shared A [A0, A1]    // DMA OP, Double Buffer
Shared B [B]
Shared C [C]
Shared D [D0, D1]    // DMA OP, Double Buffer
Loop i:
  // sync
  op1(A0, A1) // DMA OP, Double Buffer
  op2(B)      // Vector OP
  op3(C)      // Vector OP
  op4(D0, D1) // DMA OP, Double Buffer
```

- **Level 2 效果**：C 与 B 复用（同为 Vector 指令，`V_PIPE` 本就串行），不引入额外流水依赖。
- **Level 1 效果**：C 复用 Double Buffer 时自动开 Double Buffer，`op1` 用 A0、`op3` 用 C1（即 A1），不需等待，`MTE_PIPE` 与 `V_PIPE` 仍可并行。
- **问题场景**：若不保护，C 单 Buffer 与 A 复用，会在 `op1`(DMA PIPE) 与 `op4`(Vector PIPE) 之间引入额外依赖，导致 `MTE_PIPE` 与 `V_PIPE` 无法并行，流水性能下降。

### 错误信息（原文性能/报错数据）

当总内存需求超出硬件空间上限时，PlanMemory Pass 编译失败并上报对应 Memory Scope overflow，例如 UB overflow：

> 原文：`loc("/tmp/tmp0h121237/kernel.ttadapter.mlir":2:3): error: ub overflow, requires 3219456 bits while 1572864 bits available! (possible reason: tiling basic block is too large or block number is more than what user expect due to multi-buffer feature is enabled and some ops need extra local buffer.)`

### 关键术语

| 术语 | 含义 |
|---|---|
| BufferLife | 单个 Buffer 从首次写入（gen）到最后一次读取（kill）的执行区间 |
| Alias | 两数据本质同源，例如 `subview` 前后 |
| Inplace 复用 | op 输出写到输入位置以减少 alloc |
| pointer_cast | `hivm.hir.pointer_cast(offset)`，`offset` 为该 Buffer 在对应内存空间中的字节偏移量 |

---

## 【表格解读】

### 表 1：各类 Buffer 的对齐要求与功能（原文逐字还原）

| Buffer | 对齐要求 | 功能 |
|-----|-----|-----|
| Unified Buffer (UB) | 32字节对齐 | 通用缓存空间，主要用于向量和标量运算 |
| L1 Buffer | 32字节对齐 | 暂存feature map等卷积使用到的数据 |
| L0A Buffer | 512字节对齐 | 暂存矩阵运算的左矩阵（feature map） |
| L0B Buffer | 512字节对齐 | 暂存矩阵运算的右矩阵（weight） |
| L0C Buffer | 512字节对齐 | 暂存矩阵运算的中间结果和输出矩阵 |
| BT Buffer | 64字节对齐 | BiasTable Buffer，存放矩阵运算中的Bias |
| FP Buffer | 64字节对齐 | Fixpipe Buffer，存放量化参数、Relu参数等 |

**逐行解读：**
- **UB（Unified Buffer）**：32 字节对齐，是通用缓存空间，主要承担 Vector 与标量运算的输入/输出，是 PlanMemory 分配的重点空间之一。
- **L1 Buffer**：32 字节对齐，卷积场景下暂存 feature map，作为 L0A/L0B 的数据源。
- **L0A Buffer**：512 字节对齐，专门存放矩阵乘法左矩阵（即 feature map），由 L1 搬入。
- **L0B Buffer**：512 字节对齐，专门存放矩阵乘法右矩阵（即 weight），由 L1 搬入。
- **L0C Buffer**：512 字节对齐，存放矩阵乘的中间结果与最终输出矩阵，是 Cube 单元运算产物中转处。
- **BT Buffer**：64 字节对齐，BiasTable Buffer，存放矩阵运算所需的 Bias。
- **FP Buffer**：64 字节对齐，Fixpipe Buffer，存放量化参数、Relu 参数等后处理参数。

> 表格使用提示：可看出 Cube 相关（L0A/L0B/L0C）对齐粒度最大（512B），是因矩阵数据宽度大；UB/L1 次之（32B），主要服务向量与卷积；BT/FP（64B）服务 Bias 与 Fixpipe 附属参数。PlanMemory 的对齐规则与硬件强约束一致，是分配合法性的前提。

---

### 表 2：PlanMemory 接口选项（原文逐字还原）

| 选项 | 默认值 | 说明 |
|--------|--------|--------|
| `-mem-plan-mode=global-work-space-plan` | false | CV流水线中使用`GLOBAL_WORKSPACE_PLAN` |
| `enable-global-workspace-reuse` | false | 启用Workspace内的Buffer复用 |
| `restrict-inplace-as-isa` | false | 限制inplace规则以匹配ISA行为 |

**逐行解读：**
- **`-mem-plan-mode=global-work-space-plan`**（默认 `false`）：开启后走 `GLOBAL_WORKSPACE_PLAN` 模式，适用于 CV 流水线场景。默认走 `LOCAL_MEM_PLAN`。
- **`enable-global-workspace-reuse`**（默认 `false`）：是否对 Workspace 内部的 Buffer 也进行复用。开启可进一步压低内存占用，但需结合依赖与硬件约束。
- **`restrict-inplace-as-isa`**（默认 `false`）：将 inplace 规则限制为仅匹配 ISA 行为。开启更保守，可避免 ISA 不允许的 inplace 引入非法依赖或精度问题。

---

### 表 3：测试用例典型 CHECK（原文逐字还原）

```mlir
// CHECK-NOT: memref.alloc()
// CHECK: %[[CONST0:.*]] = arith.constant 0 : i64
// CHECK: {{.*}} = hivm.hir.pointer_cast(%[[CONST0]])
```

**逐行解读：**
- `CHECK-NOT: memref.alloc()`：验证 PlanMemory Pass 已将所有 `memref.alloc` 全部替换，没有残留 alloc。
- 第二条 `CHECK`：验证存在 `arith.constant 0 : i64` —— 即产生偏移量 0 的常量。
- 第三条 `CHECK`：验证存在 `hivm.hir.pointer_cast(%[[CONST0]])` —— 即使用偏移量 0 进行 `pointer_cast`，表示该 Buffer 的地址偏移量被正确写回为常量 0。
- 三条 CHECK 联合确认了 OP 变换阶段的核心行为：`alloc` 被替换为带偏移量的 `pointer_cast`。

---

## 【公式解读】

原文无公式。文档中出现的伪代码示例（如 Level1/Level2/Level0 的 Buffer 共享示例）均为文字/代码块描述调度关系，未给出数学表达式。

---

## 【关联】

本文描述的 PlanMemoryPass 在仓内上下游关系如下（原文显式提及）：

- **上游依赖**：
  - **Liveness 分析（社区 `Liveness` 类）**：生命区间分析阶段调用，用于得到节点活跃性，再由此推导出 Buffer 的 gen/kill。
  - **IR 结构**：处理含 `scf.for` / `scf.if` / `scf.while` 的控制流 IR；消费 `memref.alloc`（`LOCAL_MEM_PLAN`）与 `memref_ext.alloc_workspace`（`GLOBAL_WORKSPACE_PLAN`）；识别 `subview`（Alias）、`vcast`（Inplace）等 op 类型。
- **下游产出**：
  - 输出 `hivm.hir.pointer_cast(offset)`，供后续 Pass（指令生成、指令发射、流水调度）使用，作为真实内存地址的依据。
  - 与 **Cube 计算单元（L0A/L0B/L0C/L1）** 和 **Vector 计算单元（UB）** 的存储资源紧密耦合。
- **运行时协作**：片外空间由框架 Runtime 统一申请管理，算子需通过 PlanMemory 反馈所需 Workspace 大小。
- **硬件接口**：依赖 Atlas A2 训练 / Atlas A2 推理系列产品的硬件架构与 Buffer 对齐约束；Buffer 对齐粒度即为硬件强约束。
- **错误反馈**：当总内存需求超出硬件上限时，PlanMemory Pass 直接编译失败并上报 Memory Scope overflow（如 ub overflow）。

---

## 【使用方法】

### 启用方式（原文）

通过命令行选项（Pass 选项）控制 PlanMemoryPass 的行为，原文给出三类选项：

| 选项 | 默认值 | 用途 |
|---|---|---|
| `-mem-plan-mode=global-work-space-plan` | false | CV 流水线切到 `GLOBAL_WORKSPACE_PLAN` 模式 |
| `enable-global-workspace-reuse` | false | 启用 Workspace 内 Buffer 复用 |
| `restrict-inplace-as-isa` | false | 限制 inplace 规则以匹配 ISA 行为 |

### 配置项（原文使用约束）

1. **总内存约束（用户需保证）**：同一时刻申请的所有 Buffer 的总大小，不超过对应硬件内存空间的实际大小。
2. **自动对齐（原文）**：每个 Buffer 的实际占用空间会自动进行字节对齐，对齐大小见「硬件背景」一节的表格（UB/L1 32B，L0A/L0B/L0C 512B，BT/FP 64B）。
3. **超限失败行为**：若总内存需求超出硬件空间上限，PlanMemory Pass 编译失败并上报对应 Memory Scope overflow，例如：
   > 原文：`loc("/tmp/tmp0h121237/kernel.ttadapter.mlir":2:3): error: ub overflow, requires 3219456 bits while 1572864 bits available!`
4. **测试用例**：典型测试文件 `bishengir/test/Dialect/HIVM/plan-memory.mlir` 中用 FileCheck 检查 `memref.alloc` 被替换为 `hivm.hir.pointer_cast`。

> 原文未涉及具体的 pipeline 配置位置/Driver 调用模板；具体如何把该 Pass 串到编译 pipeline 中需结合仓内其他文档。

## 图文联合解读

- `HardwareStructure_zh.png`: **图文联合解读：**

图示展示了Atlas A2芯片AIC（含Cube/MTE1/MTE2/FixPipe/Scalar及L1/L0A/L0B/L0C/BT/FP Buffer）和AIV（含Vector/MTE2/MTE3/Scalar/Unified Buffer/DCache）的层次化结构，标注了数据流（灰实线，经MTE1/MTE2/MTE3搬运）与指令流（橙虚线）路径，并连接Global Memory与L2 Cache。

该图直观论证：片上存在多类**对齐要求不同的专用Buffer**（L0A/L0B/L0C需512B对齐，UB/L1需32B对齐），数据需经多级搬运在Buffer与计算单元间流转，且Cube结果需经L0C→FixPipe/搬运单元才能供Vector使用，由此决定了**软件必须显式管理各Buffer地址、按生命周期复用、并预留Workspace**的技术必要性。

这与文档论点完全呼应：PlanMemory正是基于该硬件结构，对L1、L0C、UB及Workspace空间进行有约束的分配与复用，以避免内存覆写。
- `plan_memory_level2.png`: **图文解读：**

图示展示了**共享内存复用**的两场景对比：上方"Shared Memory"中C缓冲区与A0/A1区重叠复用，下方C被安置在B旁不同位置；通过红箭头映射到右侧两条"流水线"，标注"GAP"区分"Reuse Same PIPE"与"Reuse Different PIPE"两种复用时机。

**结论：** 当两Buffer生命区间无重叠时（C与A0/A1无依赖），可在同PIPE内复用内存以节省空间；存在重叠时（如需等待），只能跨PIPE复用，并产生GAP导致性能下降。

**与文档的对应：** 直观印证了"基于BufferLife生命区间判断是否可复用内存"的核心算法，并解释了文档所述"三级分配算法在保障性能前提下提升内存复用率"的设计动机——复用越早（GAP越小），流水线越紧凑。
- `plan_memory_level1.png`: **图文联合解读：**

**1) 图示内容**：上图采用单Buffer方案，共享内存中A0/A1/D0/D1/B与一个黄色C共用，红圈标注A0、A1、C复用同一块地址，对应pipeline中两次op1-op4串行执行，起始有较宽GAP；下图改用多Buffer方案，C拆分为C0、C1两块黄缓冲，红圈圈出独立地址，pipeline两次迭代可在更早时刻启动（上图虚线靠右、下图虚线靠左），GAP显著缩短。

**2) 技术结论**：对生命区间重叠的中间结果（C）拆分为多个物理Buffer，可消除单Buffer带来的写后读串行依赖，从而压缩pipeline迭代间隔、隐藏访存延迟。

**3) 与文档关系**：佐证PlanMemory"三级分配算法"——在内存复用（单Buffer）与执行并行（多Buffer）间权衡，印证其"尽量保障性能前提下提升内存利用率"的设计目标。
- `plan_memory_level0.png`: **图示解读**：左框标注两个Buffer的生命区间——A[1,3]与B[4,6]无重叠；中框显示其在UB中原本各自独立占用空间；箭头指向右框，二者合并共用同一块A/B内存。

**技术结论**：当Buffer生命区间不重叠时可复用同一地址，这是PlanMemory基于BufferLife判断内存能否共用的核心依据。

**与文档关系**：直观佐证文档"生命区间无重叠即可共用内存"的分配原则，是PlanMemory内存复用算法的最小示例。
