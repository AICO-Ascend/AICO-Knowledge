# 多缓冲

> 仓 `ascendnpu-ir` · 路径 `docs/source/zh_cn/developer_guide/features/multi_buffer.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/zh_cn/developer_guide/features/multi_buffer.md

# ascendnpu-ir 「多缓冲 (Multi Buffer)」Feature 文档深度解读

---

## 【定位】

本文档系统描述 AscendNPU IR 中**多缓冲（Multi Buffer）**这一基础性能优化：把循环体内某个 Buffer 扩展为 N 份物理内存，使相邻迭代的搬运与计算落到不同槽位，从而把原本串行的硬件流水线重叠起来。文档兼顾动机（为什么能提性能）、机理（在不同内存层次上如何收益）、代价（内存膨胀与同步复杂度）以及落地手段（编译选项与 IR 变换过程），并明确指出与内存管理、自动同步、CV 软流水等特性的协作关系。

---

## 【技术要点】

1. **多缓冲的本质是用内存换时间的延迟隐藏（Latency Hiding）**：将同一 Buffer 复制为 N 片物理副本，使迭代间的反依赖（WAR，Write-After-Read）消失，只保留片内的真依赖（RAW）；稳态下耗时从"各阶段耗时之和"收敛到"最长阶段的耗时"。N=2 即为最常用的 Double Buffer（双缓冲、乒乓流水）。

2. **四步使能流水线**：① `-hivm-mark-multi-buffer` 按内存层次在 Buffer 分配点上生成 `annotation.mark {hivm.multi_buffer = N}` 标记（本地 Buffer 固定 N=2，GM Workspace 由 `--set-workspace-multibuffer` 决定）；② PlanMemory 为带标记 Buffer 分配 N 份地址并生成携带多个偏移的 `hivm.hir.pointer_cast`；③ 自动同步按槽位轮转分配 flag ID 与 event ID；④ `-hivm-enable-multi-buffer` 引入 `hivm.hir.multi_buffer_counter` 计数器，对 N 取模选出当次迭代实际使用的地址，最终通过 `arith.select` 在两个单地址 `pointer_cast` 间二选一。

3. **六条硬件流水线并行**：MTE2（GM→L1/UB）、MTE1（L1→L0A/L0B）、M/Cube（矩阵乘）、V/Vector（向量计算）、FIX（含量化的 L0C 搬出）、MTE3（UB/L1→GM），各流水线异步执行，由 `hivm.set_flag`/`hivm.wait_flag` 建立先后顺序。

4. **按内存层次差异化标记与重叠**：GM（Workspace）— Cube 核与 Vector 核跨核并行；L1（cbuf）— MTE2 与 MTE1、M 重叠；L0C — M 与 FIX 重叠；UB — MTE2、V、MTE3 三段流水并行。本地 Buffer 多缓冲数量固定为 2，GM Workspace 数量在 Ascend 950PR/950DT 上默认 2，在 Atlas A3/A2 系列上默认 4。

5. **总开关 + 三类限制类选项 + GM 数量选项**：总开关 `--enable-auto-multi-buffer=true`；限制类分别为 `--limit-auto-multi-buffer-only-for-local-buffer`（bool，默认 `false`）、`--limit-auto-multi-buffer-of-local-buffer`（enum，默认 `no-l0c`）、`--limit-auto-multi-buffer-buffer`（enum，硬件相关默认 950PR/950DT 为 `no-limit`、A3/A2 为 `only-cube`）；数量选项 `--set-workspace-multibuffer`。

6. **后续演进合并为正向表达 `--multibuffer-mode`**：以四元组 `[(gm, N), (l1, N), (l0c, N), (ub, N)]` 形式直接指定各层次槽位数（N>1 开启、N=1 关闭、N=0 非法），替换语义交叠、可读性差的三个 `limit` 选项，并保留一个版本兼容期。

---

## 【关键机制与数据】

### 工作原理（伪代码对照）

**原文：**
```text
单缓冲（1片Buffer）：
iter 0: [MTE2 load][ V compute ][MTE3 store]
iter 1:                                     [MTE2 load][ V compute ][MTE3 store]
iter 2:                                                                          [MTE2 load]...
耗时 ≈ 迭代数 × (T_load + T_compute + T_store)
```

**原文：**
```text
双缓冲（2片Buffer）：
iter 0: [MTE2 load buf0][ V compute buf0 ][MTE3 store buf0]
iter 1:                 [MTE2 load buf1][ V compute buf1 ][MTE3 store buf1]
iter 2:                                 [MTE2 load buf0][ V compute buf0 ]...
进入稳态后耗时 ≈ 迭代数 × max(T_load, T_compute, T_store)
```

机制要点（按原文）：
- 多缓冲消除的是**迭代间反依赖（WAR）**；保留的是**同一片 Buffer 内部的真依赖（RAW）**。
- 第 `i` 次迭代使用第 `i % N` 片。
- 收益上界由流水线的均衡程度决定——"搬运与计算耗时相当时，收益最明显；某条流水线是绝对瓶颈时，多缓冲只能隐藏掉非瓶颈部分的耗时"。
- 收益需要足够迭代数摊薄——"稳态之外的首次搬入与末次搬出无法被隐藏，循环次数很少时收益会被这部分开销抵消"。
- "N 从 1 增到 2 即可消除相邻迭代的反依赖，继续增大 N 只在流水阶段数更多（例如 CV 软件流水）或单次搬运耗时波动较大时才有额外收益，但内存占用是线性增长的"。

### 数据流（IR 变换前后对比）

**原文 MLIR：**
```mlir
// 标记后、PlanMemory分配地址后：一个pointer_cast携带2份地址
%p = hivm.hir.pointer_cast(%addr0, %addr1) : memref<1024xf16, #hivm.address_space<ub>>
annotation.mark %p {hivm.multi_buffer = 2 : i32} : memref<1024xf16, #hivm.address_space<ub>>

// -hivm-enable-multi-buffer之后：拆成2个单地址pointer_cast，按迭代计数选择
%p0 = hivm.hir.pointer_cast(%addr0) : memref<1024xf16, #hivm.address_space<ub>>
%p1 = hivm.hir.pointer_cast(%addr1) : memref<1024xf16, #hivm.address_space<ub>>
%counter = hivm.hir.multi_buffer_counter : i64
%slot = arith.remui %counter, %c2_i64 : i64
%is1 = arith.cmpi eq, %slot, %c1_i64 : i64
%active = arith.select %is1, %p1, %p0 : memref<1024xf16, #hivm.address_space<ub>>
```

排查方法（原文）：检索 `hivm.multi_buffer` 标记与 `arith.select` 结构；两者缺失说明标记阶段未命中候选。

### 溢出回退策略（性能/可靠性数据）

**原文：**
- 在 Ascend 950PR/Ascend 950DT 上，"会先只关闭溢出内存空间对应的多缓冲后重试，逐项退让无效时再关闭总开关"。
- 在 Atlas A3 系列产品与 Atlas A2 系列产品上，"则依次关闭 `--enable-code-motion` 与多缓冲总开关后重试"。
- 开启 `--enable-tuning-mode` 可禁用该重试行为，使溢出直接暴露为编译失败。

---

## 【表格解读】

### 表 1：昇腾 AICore 内部流水线（原文「硬件背景」节）

| 流水线 | 承载的典型HIVM操作 | 作用 |
|---|---|---|
| MTE2 | `hivm.hir.load`、`hivm.hir.nd2nz` | GM搬入L1或UB |
| MTE1 | `hivm.hir.mmadL1`的搬入阶段 | L1搬入L0A与L0B |
| M（Cube） | `hivm.hir.mmadL1`的计算阶段 | 矩阵乘计算 |
| V（Vector） | `hivm.hir.vadd`等向量操作 | 向量计算 |
| FIX | `hivm.hir.fixpipe` | L0C结果搬出，含量化、ReLU等后处理 |
| MTE3 | `hivm.hir.store`、`hivm.hir.nz2nd` | UB或L1搬出至GM |

**逐行解读：**
- **MTE2**：外部数据进入芯片的第一站，对应 `hivm.hir.load`（直接搬运）与 `hivm.hir.nd2nz`（带 ND→NZ 布局转换的搬运），把 GM 上的数据搬进 L1 或 UB。
- **MTE1**：矩阵乘的前置搬运阶段，仅服务于 `hivm.hir.mmadL1`，负责把 L1 中的左右矩阵搬入 L0A 与 L0B 寄存器。
- **M（Cube）**：纯计算阶段，执行 `hivm.hir.mmadL1` 的矩阵乘累加，结果落在 L0C。
- **V（Vector）**：通用向量计算单元，以 `hivm.hir.vadd` 为代表，处理各种 elementwise/向量规约操作。
- **FIX**：结果后处理流水线，`hivm.hir.fixpipe` 在把 L0C 结果搬出的同时完成量化、ReLU 等后处理——这意味着 FIX 是"搬运+计算"混合体，是 Cube 计算链路的最后一段。
- **MTE3**：搬出流水线，对应 `hivm.hir.store` 与 `hivm.hir.nz2nd`（NZ→ND 布局转换），把 UB 或 L1 数据写回 GM。

整体上表刻画了"数据从 GM 进入 → L1/UB → L0A/L0B → L0C → 再回 GM"完整生命周期中六条可并行流水线的分工，为后文多缓冲在四类内存层次上的差异化收益形态奠定硬件基础。

### 表 2：各内存层次上的收益形态（原文「各内存层次上的收益形态」节）

| 内存层次 | 触发标记的操作 | 重叠的流水线 | 收益形态 |
|---|---|---|---|
| GM（Workspace） | 写Workspace的`hivm.hir.store`、`hivm.hir.fixpipe` | Cube核与Vector核跨核并行 | MIX算子中Cube的计算结果经Workspace交给Vector继续处理。多份Workspace让两个核错开一个迭代同时工作，而非互相等待 |
| L1（cbuf） | `hivm.hir.nd2nz` | MTE2与MTE1、M | 矩阵乘左右矩阵的搬入与当前分块的Cube计算重叠 |
| L0C | `hivm.hir.fixpipe` | M与FIX | 上一次矩阵乘结果搬出L0C的同时，下一次矩阵乘可以开始累加 |
| UB | `hivm.hir.load`、`hivm.hir.store` | MTE2、V、MTE3 | 纯Vector算子以及MIX算子的Vector侧，搬入、计算、搬出三段流水并行 |

**逐行解读：**
- **GM（Workspace）**：MIX 算子跨核（Cube ↔ Vector）交接的中转站。原文明确："GM Workspace 层次的多缓冲是 MIX 算子（如 FlashAttention）实现 Cube 与 Vector 核并行的前提，与 CV 软件流水优化配合使用，软件流水的阶段数即为 Workspace 的多缓冲数量。"即此处 N 不止 2，与 CV 软件流水阶段数挂钩。
- **L1（cbuf）**：解决矩阵乘左右矩阵在 MTE2（GM→L1）和 MTE1（→L0A/L0B）之间的搬运与 Cube 计算 M 之间的流水断裂；典型场景是 MTE2 搬下一块 tile 时，本块 tile 已经被 Cube 算上。
- **L0C**：让 FIX 流水线"搬出上一次结果"的同时 M 流水线"开始下一次累加"，避免 L0C 这块小容量寄存器成为流水瓶颈。
- **UB**：典型向量算子（`hivm.hir.load` → `hivm.hir.vadd` → `hivm.hir.store`）的三段流水完全并行，也是本地 Buffer 中固定 N=2 的最常见场景。

### 表 3：编译选项（原文「编译选项」节）

| 选项名 | 描述 | 类型 | 默认值 |
|---|---|---|---|
| --enable-auto-multi-buffer | 自动多缓冲总开关。关闭时下述三个选项均不生效 | bool | true |
| --limit-auto-multi-buffer-only-for-local-buffer | 限定多缓冲仅对片上本地Buffer（UB、L1、L0C）生效。置为`true`时跳过GM Workspace的多缓冲标记，即关闭CV跨核流水 | bool | false |
| --limit-auto-multi-buffer-of-local-buffer=\<value> | 限定本地Buffer的多缓冲范围。`no-l0c`表示不对L0C开启多缓冲；`no-limit`表示不做限制 | enum | no-l0c |
| --limit-auto-multi-buffer-buffer=\<value> | 限定MIX算子中多缓冲的作用侧。`only-cube`表示仅Cube侧（L1、L0C）；`only-vector`表示仅Vector侧（UB）；`no-limit`表示不做限制 | enum | 见下方说明 |

**逐行解读：**
- **`--enable-auto-multi-buffer`**：总开关。"关闭时下述三个选项均不生效"——即禁用整项优化。
- **`--limit-auto-multi-buffer-only-for-local-buffer`**：把 GM Workspace 这一层从多缓冲中排除，等价于关闭 CV 跨核流水（因为 CV 流水完全依赖 Workspace 多缓冲）。
- **`--limit-auto-multi-buffer-of-local-buffer`**：本地 Buffer 内部子集过滤。`no-l0c` 是默认——即 L0C 不参与多缓冲（出于容量保护）；`no-limit` 则把 L0C 也纳入多缓冲。
- **`--limit-auto-multi-buffer-buffer`**：MIX 算子的 Cube/Vector 侧选择，默认值随硬件变化（详见下表与原文说明）。

**默认值补充（原文）：**
- Ascend 950PR/Ascend 950DT：`no-limit`
- Atlas A3 训练系列/推理系列、Atlas A2 训练系列/推理系列：`only-cube`
- 显式传入时以用户取值为准。

**`--set-workspace-multibuffer` 默认值（原文）：**
- Ascend 950PR/Ascend 950DT：默认 2
- Atlas A3 系列产品与 Atlas A2 系列产品：默认 4

### 表 4：新旧选项等价关系（原文「后续演进」节，以 Ascend 950PR/Ascend 950DT 为基准）

| 现有配置 | 等价的`--multibuffer-mode` |
|---|---|
| 全部默认 | `[(gm, 2), (l1, 2), (l0c, 1), (ub, 2)]` |
| `--enable-auto-multi-buffer=false` | `[(gm, 1), (l1, 1), (l0c, 1), (ub, 1)]` |
| `--limit-auto-multi-buffer-only-for-local-buffer=true` | `[(gm, 1), (l1, 2), (l0c, 1), (ub, 2)]` |
| `--limit-auto-multi-buffer-of-local-buffer=no-limit` | `[(gm, 2), (l1, 2), (l0c, 2), (ub, 2)]` |
| `--limit-auto-multi-buffer-buffer=only-cube` | `[(gm, 2), (l1, 2), (l0c, 1), (ub, 1)]` |
| `--limit-auto-multi-buffer-buffer=only-vector` | `[(gm, 2), (l1, 1), (l0c, 1), (ub, 2)]` |

**逐行解读：**
- **全部默认**：总开关 `true`、不限制 local-only、L0C 默认关（`no-l0c`）、`no-limit`——但 `no-limit` 在 A3/A2 上是 `only-cube`，故默认下 gm=2、ub=2（来自本地 Buffer 固定 N=2），l0c=1。
- **总开关关闭**：四层全部回到单 Buffer。
- **`--limit-auto-multi-buffer-only-for-local-buffer=true`**：把 gm 强制置 1，其余本地 Buffer 维持默认行为。
- **`--limit-auto-multi-buffer-of-local-buffer=no-limit`**：把 l0c 从 1 提到 2（开启 L0C 多缓冲），其余按默认。
- **`--limit-auto-multi-buffer-buffer=only-cube`**：关闭 ub 多缓冲（MIX Vector 侧关），其余按默认。
- **`--limit-auto-multi-buffer-buffer=only-vector`**：关闭 l1 多缓冲（MIX Cube 侧关），其余按默认。

> 备注：原文明确指出 "`--multibuffer-mode` 尚未提供，本节仅用于说明演进方向。选项切换时会保留一个版本的兼容期"。

---

## 【公式解读】

文档中并未给出严格的数学公式，但提供了两段伪代码形式的"耗时近似"表达式，原文逐字保留如下：

**原文公式 1（单缓冲耗时）：**
```
耗时 ≈ 迭代数 × (T_load + T_compute + T_store)
```

**原文公式 2（双缓冲进入稳态后的耗时）：**
```
进入稳态后耗时 ≈ 迭代数 × max(T_load, T_compute, T_store)
```

**符号含义与作用解释：**
- `耗时`：整个循环算子的端到端执行时间。
- `迭代数`：循环执行的总次数。
- `T_load`：MTE2（GM→L1/UB）一次迭代的搬入耗时。
- `T_compute`：V 流水线（Vector）或 M 流水线（Cube）一次迭代的计算耗时。
- `T_store`：MTE3（UB/L1→GM）一次迭代的搬出耗时。
- `max(...)`：表示多缓冲稳态下三个阶段的瓶颈时长，由流水线均衡度决定。

公式的物理含义：**单缓冲下三段必须串行，总耗时为各阶段之和；多缓冲后三段可流水并行，总耗时收敛到最长阶段**。这是"用内存换时间"的最直接数学表达，也是后文判断"收益上界由流水线均衡程度决定"的依据——只有当 `T_load ≈ T_compute ≈ T_store` 时收益才接近最大。

---

## 【关联】

按原文内部链接，本文处于 AscendNPU IR 优化链路中的协同节点：

### 上下游与同层特性

- **[-hivm-mark-multi-buffer](../passes/hivm_passes.md#-hivm-mark-multi-buffer)**：多缓冲使能流程的第一步 Pass，按内存层次在 Buffer 分配点上生成 `annotation.mark {hivm.multi_buffer = N}` 标记。是多缓冲的"识别与标记"阶段。
- **[-hivm-enable-multi-buffer](../passes/hivm_passes.md#-hivm-enable-multi-buffer)**：多缓冲使能流程的第四步 Pass，引入 `hivm.hir.multi_buffer_counter`，通过 `arith.remui` 与 `arith.select` 把多地址 `pointer_cast` 拆为按迭代轮转的单地址 `pointer_cast`。是"选择槽位"阶段。
- **[自动同步-硬件背景](./auto_sync.md#硬件背景)**：多缓冲必须依赖 `hivm.set_flag`/`hivm.wait_flag` 在六条流水线间建立先后顺序；多缓冲开启后，flag ID（核内）与 event ID（跨核）都需要按槽位轮转，使同一槽位的生产者与消费者成对匹配——本文明确指向该文档以说明同步机制。
- **[内存管理-硬件背景](./plan_memory.md#硬件背景)**：片上各级 Buffer（UB、L1、L0A、L0B、L0C）容量有限且需显式分配地址，这是多缓冲 N 倍内存开销的硬件背景来源。
- **[内存管理-算法原理](./plan_memory.md#算法原理)**：PlanMemory 为带多缓冲标记的 Buffer 分配 N 份地址，是多缓冲流程的第二步；Level 1 内存复用策略会"保护多缓冲前提"——若同一循环内单缓冲 Buffer 复用了多缓冲 Buffer 的空间，会被自动转为多缓冲。
- **[内存管理-使用约束](./plan_memory.md#使用约束)**：多缓冲 N 倍占用若超出对应内存空间容量上限，PlanMemory 上报 overflow，错误形式与规避方式详见该节。
- **[Cube与Vector软件流水优化-硬件背景](./cv_pipelining.md#硬件背景)**：GM Workspace 多缓冲与 CV 软件流水深度绑定——"软件流水的阶段数即为 Workspace 的多缓冲数量"，CV 流水阶段多时 Workspace 的 N 也需要相应增大（原文还提到 Atlas A2/A3 系列 `--set-workspace-multibuffer` 默认 4 即对应此场景）。
- **[调试调测-调试：工具类](../../user_guide/debug_option.md#调试工具类)**：开启多缓冲后若出现精度异常或卡死，可先用 `--enable-auto-multi-buffer=false` 定位问题范围，更深入的排查手段见该节。

### 协同关系图（按原文描述）

```
循环算子
   │
   ├─ 多缓冲标记 (-hivm-mark-multi-buffer)
   │       │
   │       ├─ 本地 Buffer (UB/L1/L0C) ──── 与 内存管理 协同 (PlanMemory 分配 N 份)
   │       └─ GM Workspace ──────────────── 与 CV软件流水 协同 (阶段数 = Workspace 多缓冲数量)
   │
   ├─ 同步结构轮转 (自动同步 ─── flag ID / event ID 按槽位轮转)
   │
   └─ 槽位选择 (-hivm-enable-multi-buffer)
           │
           └─ 多缓冲 counter + arith.select
```

---

## 【使用方法】

### 配置示例（原文 bishengir-compile 命令）

**原文：**
```bash
# 关闭全部多缓冲，用于性能对比或问题定位
bishengir-compile input.mlir --enable-auto-multi-buffer=false

# 仅保留片上多缓冲，关闭GM Workspace上的CV跨核流水
bishengir-compile input.mlir --limit-auto-multi-buffer-only-for-local-buffer=true

# 片上全开，包含L0C
bishengir-compile input.mlir --limit-auto-multi-buffer-of-local-buffer=no-limit

# MIX算子仅对Vector侧的UB开启多缓冲
bishengir-compile input.mlir --limit-auto-multi-buffer-buffer=only-vector
```

### 配置要点（按原文「使用约束」节）

1. **`--limit-auto-multi-buffer-only-for-local-buffer` 与 `--limit-auto-multi-buffer-buffer` 仅对核类型为 MIX 的函数生效**。"纯 Cube 或纯 Vector 算子不存在 GM Workspace 交接，也不存在 Cube 侧与 Vector 侧的划分，配置这两个选项不会改变行为。"
2. **多缓冲候选必须位于循环内，且从 Buffer 分配点到最外层的所有祖先循环都必须是 `scf.for` 或 `scf.while`**。"位于 `scf.parallel`、`scf.forall` 等循环内的 Buffer 不满足'每次迭代轮转一个槽位'的前提，不会被标记。"
3. **本地 Buffer 的多缓冲数量固定为 2，不可通过编译选项调整**；仅 GM Workspace 的数量可通过 `--set-workspace-multibuffer` 配置。
4. **用户需保证 N 倍 Buffer 占用不超过对应内存空间的容量上限**，否则 PlanMemory 上报 overflow，规避方式见内存管理-使用约束。

### 排查手段（原文）

- 在 IR 中检索 `hivm.multi_buffer` 标记与 `arith.select` 结构；两者缺失说明标记阶段未命中候选。
- 精度异常或卡死时，先用 `--enable-auto-multi-buffer=false` 定位问题范围；进一步排查手段见 调试调测-调试：工具类。
- 编译期溢出：开启 `--enable-tuning-mode` 可禁用溢出重试回退，使 overflow 直接暴露为编译失败，便于强制减小 tiling。
