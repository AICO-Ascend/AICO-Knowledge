# CustomOp

> 仓 `ascendnpu-ir` · 路径 `docs/source/en/developer_guide/features/CustomOp/CustomOp.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/en/developer_guide/features/CustomOp/CustomOp.md

```markdown
# CustomOp 文档一体化深度解读

## 【定位】
本文档面向昇腾 NPU 上基于 MLIR 的 AscendNPU-IR（bishengir）编译器栈，描述当内置算子集无法满足特定计算、私有算子或性能需求时，用户如何通过 **CustomOp** 机制自行定义算子并接入整套编译流水（含 lowering、链接、调度），重点给出 API 形态、可调属性、Lowering 路径、Builtin/Custom/Custom Macro 三种 MLIR 用法及其能力边界。

---

## 【技术要点】
1. **三种 op 形态**：`hivm.hir.custom` 用于普通算子（Builtin 名以 `__builtin` 为前缀）或用户自定义算子；`hivm.hir.custom_macro` 用于带显式同步的"宏"算子（同时指定 `pipe_in`/`pipe_out`）。
2. **Generic API**：算子由 `name`、`inputs`、`outputs` 三段描述，其中 `outputs` 必为 **init operands**（既是结果初值也是写入位置）。其余全部能力通过属性（attribute）声明，包括 `CoreType`、`Pipe`、`InPipe`/`OutPipe`、`VFMode`、`Symbol`、`sync_event_slots`、`iterator_types`、`indexing_map`、`max_rank`、`align_dim`、`arg_attrs`、`extra_buffers_types`/`extra_buffers_sizes`、`temp_buffers`、`no_side_effect`、`bitcode`/`source`/`compile`。
3. **Builtin 命名空间保留**：`__builtin_*` 名称由 `bishengir-compile` 内置的 template library 提供实现并自动链接；用户自命名算子必须自行给出实现位置、编译命令和全部所需信息。
4. **Lowering 路径**：所有 CustomOp 经 `HIVMToStandard` pass 归一化——Builtins 转换为 builtin 库调用；用户提供实现的算子被转换为对用户函数的 `call`，再由 **BiSheng Compiler** 经 `bishengir-compile` 链接用户源/对象文件并编译为最终 object。
5. **核心调度属性**：`CoreType`（执行核类型）、`Pipe`（执行流水线，宏算子额外有 `InPipe`/`OutPipe`，对应汇编属性 `hivm.pipe_in`/`hivm.pipe_out`）、`VFMode`（向量单元模式 SIMT/SIMD/MIX，在 cube 核上被忽略）；其中 Builtin 允许不显式声明，由编译器做正确性检查与 canonicalize。
6. **同步与铺平元数据**：宏算子的 `sync_event_slots` 列表长度必须与实现内部同一 pipe pair 的 `set_flag`/`wait_flag` 对数一一对应，由 `GraphSyncSolver` 自动注入 `sync_related_args` 与 set/wait flag；`iterator_types` / `indexing_map` 为铺平与结构化 lowering 提供 per-operand 信息；`max_rank` 默认 `5`，影响 flatten/layout pass 的张量秩上界。

---

## 【关键机制与数据】

### 工作原理与数据流
- **CustomOp IR 入口**：上层模型产生 `hivm.hir.custom "name" { attrs... } ins(..) outs(..)` 形式的算子，承载调度属性 + 输入输出 SSA 值；宏算子则用 `hivm.hir.custom_macro`，把 pipe 拆为 `pipe_in`/`pipe_out` 并声明同步槽位。
- **Lowering 通道**：原图（ASCII 图）显示 `HIVMToStandard` 把所有 CustomOp 转译为 standard dialect 的 `call`：
  - Builtins → builtin 库的函数调用；
  - 用户实现 → 用户提供的 `Symbol` 函数调用 → `bishengir-compile` 把用户源/对象与 IR 链接并产出 object。
- **铺平/布局/同步协同**：
  - `iterator_types`（`HIVM_IteratorTypeAttr`）和 `indexing_map`（`ArrayAttr<AffineMapAttr>`，等价于 Linalg 的 `indexing_maps`）共同驱动 tiling/flatten；
  - `arg_attrs`（如 `{align_dim = 1 : i64}` on operand 2）携带 per-operand 对齐提示，由 alignment adjustment / memory planning / layout transformation 等 pass 消费；
  - `extra_buffers_types` / `extra_buffers_sizes`（元素个数）经 `hivm-alloc-extra-buffer` pass 实化为 `memref` 并追加到 `temp_buffers`（汇编中即 `tmps` 操作数段）。

### 性能/规模数据
- `max_rank` 默认值 **5**（`i64` 属性，原文："default is **5**"）。
- `sync_event_slots` 列表长度约束："The list length must match the number of internal `set_flag`/`wait_flag` pairs declared in the macro implementation for the same pipe pair."（即与同一 pipe pair 下的 flag 对数严格对齐）。
- Limitations 表中两条状态原文："**User implementations** … **Work in progress**"；"**Passes interactions** … **NA, work in progress**"，提示用户实现接入与多 pass 协同均尚未完成。

---

## 【表格解读】

### 表 1：Capabilities（✅ 能力清单）

| Feature | Description |
| --- | --- |
| **CoreType** | Custom op execution core. |
| **Pipe** | Custom op execution pipe (`hivm.hir.custom`). |
| **InPipe / OutPipe** | Macro custom op input/output pipes (`hivm.hir.custom_macro`). |
| **VFMode** | Custom op running mode on vector core, SIMT/SIMD/MIX. |
| **Symbol** | User provided implementation function name |
| **sync_event_slots** | Macro sync-slot declaration for GraphSyncSolver integration. |
| **iterator_types** | Tiling / flatten iterator semantics per operand. |
| **indexing_map** | Per-operand affine maps for structured lowering. |
| **max_rank** | Upper bound on tensor rank for layout passes (default 5). |
| **align_dim** / **arg_attrs** | Per-operand alignment hints for adjustment passes. |
| **extra_buffers_*** / **tmps** | Scratch buffer declaration and allocation. |
| **no_side_effect** | Pure-op marking for optimization. |
| **Builtins** | Set of builtins (name reserved). |

**逐行解读**：
- 前 5 行构成**调度核心属性集**：`CoreType`（核类型）、`Pipe`（普通 op 的执行流水）、`InPipe`/`OutPipe`（宏 op 的输入/输出流水，分别写到 `hivm.pipe_in` / `hivm.pipe_out`）、`VFMode`（向量模式，cube 核上无效）、`Symbol`（用户函数名）——共同决定 CustomOp 在硬件上的运行位置。
- 中间 4 行是**铺平/同步元数据**：`sync_event_slots` 由 `GraphSyncSolver` 自动注入同步；`iterator_types` 与 `indexing_map` 提供 per-operand 仿射信息以驱动 tiling/flatten；`max_rank` 默认 5，限定 flatten/layout 能处理的最大张量秩。
- 后 4 行是**实现与优化辅助**：`align_dim`/`arg_attrs` 给 alignment adjustment pass 用；`extra_buffers_*` + `tmps` 走 `hivm-alloc-extra-buffer` pass 物化为 scratch memref；`no_side_effect` 标记无副作用以辅助优化；`Builtins` 列出由编译器内建提供的算子集合（命名以 `__builtin` 保留）。

### 表 2：Limitations（⚠️ 限制清单）

| Limitation | Description | Status |
| --- | --- | --- |
| **User implementations** | Custom op lowered to user provided implementations:<br>- HIVM IR link to user provided sources/objects<br>- Specific commands registration to bishengir-compile | Work in progress. |
| **Passes interactions** | Transformation passes that adapt to custom op:<br>- Flatten optimization<br>- Alignment adjustment<br>- Memory planning<br>- Layout transformation<br>- ... more to go | NA, work in progress. |

**逐行解读**：
- **User implementations**（进行中）：用户自定义算子下层到用户实现的关键环节——HIVM IR 链接用户源/对象、向 `bishengir-compile` 注册特定编译命令——目前仍处 Work in progress，意味着用户侧接入链路的稳定性/完备性尚不成熟。
- **Passes interactions**（NA，进行中）：围绕 CustomOp 的四大类变换 pass——Flatten 优化、对齐调整、内存规划、布局变换——以及"more to go"暗示的更多 pass——目前尚无可用的稳定状态（NA），表明在通用优化流水线中 CustomOp 还不能像内置算子一样被多 pass 协同改造。

---

## 【公式解读】
原文无独立数学公式；与公式作用等价的"声明/约束表达式"在文档中以 MLIR/属性语法形式给出，逐字保留并解读如下：

### 表达式 A：Builtin 调用（汇编伪代码）
```mlir
%0 = hivm.hir.custom
       "__builtin_gather_load"
       ins(%arg0, %arg1, %c4_i64, %c0_i32, %c2_i64, %c1_i64, %c2_i32, %c2_i32, %c0_i32, %c0_i32
           : memref<?xf32>, tensor<3x3xi64>, i64, i32, i64, i64, i32, i32, i32, i32)
       outs(%empty : tensor<3x3xf32>) -> tensor<3x3xf32>
```
- 符号解读：
  - `%0`：算子输出 SSA 值（一个 `tensor<3x3xf32>`）；
  - `"__builtin_gather_load"`：op 名，前缀 `__builtin` 触发编译器内置库自动链接，无需 `Symbol`/`bitcode` 等；
  - `ins(...)`：输入列表，依次为源 memref、index tensor 与若干标量常量，类型紧跟冒号后；
  - `outs(%empty : tensor<3x3xf32>)`：init operand——既是结果初值也是写入位置；
  - `-> tensor<3x3xf32>`：op 的返回类型。

### 表达式 B：Custom 用户算子（汇编伪代码）
```mlir
%0 = hivm.hir.custom
      { hivm.tcore_type = #hivm.tcore_type<VECTOR>, hivm.pipe = #hivm.pipe<PIPE_V>, hivm.vf_mode = #hivm.vf_mode<SIMD>,
        symbol = "my_custom" }
      "my_custom_op"
      ins(%arg0, %arg1, %c4_i64, %c0_i32, %c2_i64, %c1_i64, %c2_i32, %c2_i32, %c0_i32, %c0_i32
          : memref<?xf32>, tensor<3x3xi64>, i64, i32, i64, i64, i32, i32, i32, i32)
      outs(%empty : tensor<3x3xf32>) -> tensor<3x3xf32>
```
- 符号解读（相对 A 增量）：
  - 属性字典中：`tcore_type<VECTOR>` 指定向量核；`pipe<PIPE_V>` 指定 V 流水线；`vf_mode<SIMD>` 指定向量单元以 SIMD 运行（cube 核上此属性被忽略）；`symbol = "my_custom"` 是用户提供的实现函数名，由 `HIVMToStandard` 转译为对 `my_custom` 的 `call`；
  - `"my_custom_op"` 为 op 名（非 `__builtin` 前缀，需用户指定实现位置与编译命令）。

### 表达式 C：Custom Macro 宏算子（汇编伪代码）
```mlir
%0 = hivm.hir.custom_macro
      { hivm.tcore_type = #hivm.tcore_type<VECTOR>,
        hivm.pipe_in = #hivm.pipe<PIPE_MTE2>,
        hivm.pipe_out = #hivm.pipe<PIPE_V>,
        hivm.vf_mode = #hivm.vf_mode<SIMD>,
        symbol = "custom_macro_add_int32",
        sync_event_slots = [
          #hivm.sync_event_slot<#hivm.pipe<PIPE_MTE2>, #hivm.pipe<PIPE_V>>
        ] }
      "macro_add"
      ins(%arg0, %arg1 : memref<?xi32>, memref<?xi32>)
      outs(%dst : memref<32xi32, #hivm.address_space<ub>>)
```
- 符号解读：
  - `custom_macro` op 类：将 pipe 拆为 `pipe_in`/`pipe_out`，分别对应汇编属性 `hivm.pipe_in` / `hivm.pipe_out`；
  - `sync_event_slots = [#hivm.sync_event_slot<PIPE_MTE2, PIPE_V>]`：声明宏内部 `set_flag`/`wait_flag` 配对所在的 pipe pair；列表长度必须与实现中同一 pipe pair 的 `set_flag`/`wait_flag` 对数严格匹配；
  - `symbol = "custom_macro_add_int32"`：宏算子的设备端实现名；
  - `outs(%dst : memref<32xi32, #hivm.address_space<ub>>)`：`%dst` 是 init operand，且其地址空间落在 `ub`（Unified Buffer）。

---

## 【关联】
- **属性定义文件 / Dialect**：`TCoreTypeAttr`、`PipeAttr`、`VFModeAttr`、`HIVM_IteratorTypeAttr` 在文中以"Refer to …Attr"形式被多次引用，构成 `hivm.hir.custom[_macro]` 的属性语义基础。
- **优化 Pass 协同**（Limitations 表中列出）：
  - **Flatten optimization / Alignment adjustment / Memory planning / Layout transformation**：围绕 CustomOp 的变换 pass 链，目前仍处 Work in progress；
  - **hivm-alloc-extra-buffer pass**：消费 `extra_buffers_types`/`extra_buffers_sizes`，物化 `memref` scratch buffer 并接到 `temp_buffers`（汇编 `tmps` 操作数段）；
  - **GraphSyncSolver**：消费 `sync_event_slots`，自动填充 `sync_related_args` 并围绕宏注入 set/wait flag。
- **Lowering 通道**：`HIVMToStandard` 是 CustomOp 下沉到 standard dialect 的唯一汇合点；其后由 **BiSheng Compiler** 借助 `bishengir-compile` 完成 builtin 库调用或用户函数链接，产出最终 object。
- **生态/前端**：
  - **Triton frontend**：负责把 `align_dim` 等注册信息生成到 `arg_attrs`，并把实现 artifact 路径填到 `bitcode` / `source` / `compile`；
  - **Linalg 对照**：`indexing_map` 的角色类比 Linalg 的 `indexing_maps`（per-operand 仿射映射），便于结构化 lowering。
- **Builtin 实现后端**：`__builtin_*` 名空间对应的内置实现随 `bishengir-compile` 一同发布，链接到 self-contained template library，无需用户另行提供。
- **内部锚点**：`sync_event_slots` 属性条目通过 `[Macro sync_event_slots](#macro-sync-event-slots)` 链接到后文 *Macro sync_event_slots: one slot vs two slots* 小节（文档在 "for exam" 处被截断，原文未给出完整内容；本节提到的 SSA 名 `out`/`a`/`b`/`L` 推测属于该截断小节中的示例片段，原文未涉及完整定义，本解读不予臆造）。

---

## 【使用方法】
- **Builtin 用法**：直接写 `hivm.hir.custom "__builtin_xxx"`，由编译器自动链接内置 template library；可省略调度属性，由编译器做正确性检查与 canonicalize。
- **用户自定义普通算子**：写 `hivm.hir.custom "my_custom_op"`，并显式给出：
  - `symbol`（实现函数名，例：`symbol = "my_custom"`）；
  - 调度属性 `CoreType` / `Pipe` / `VFMode`；
  - 必要时 `iterator_types` / `indexing_map` / `max_rank`（默认 5）/ `align_dim`+`arg_attrs` / `extra_buffers_*` / `no_side_effect`；
  - 实现 artifact：`bitcode` / `source` / `compile`（通常由 Triton 前端写入），并按 `bishengir-compile` 要求注册特定编译命令与链接命令。
- **宏算子（带跨流水线同步）**：用 `hivm.hir.custom_macro "macro_xxx"`，额外指定：
  - `pipe_in` / `pipe_out`（对应 `hivm.pipe_in` / `hivm.pipe_out`）；
  - `sync_event_slots`：列表长度须等于宏实现内部同一 pipe pair 的 `set_flag`/`wait_flag` 对数，由 `GraphSyncSolver` 自动展开；
  - 设备端实现名通过 `symbol` 指定。
- **out / a / b / L 链接使用**：原文未涉及（文档在 *Macro sync_event_slots: one slot vs two slots* 小节被截断）。
```
