# 自定义算子

> 仓 `ascendnpu-ir` · 路径 `docs/source/zh_cn/developer_guide/features/custom_op.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/zh_cn/developer_guide/features/custom_op.md

```markdown
# 自定义算子（AscendNPU-IR Feature）一体化深度解读

## 【定位】

本文档描述 AscendNPU-IR 中"自定义算子（CustomOp）"的接口、能力与降级流程，解决"上游算子集合无法覆盖用户特定计算逻辑/私有算子/性能瓶颈场景"时，如何把用户自有的实现接入到 AscendNPU（HIVM）编译流水线中，使其可与其他算子统一编译并下沉到昇腾硬件的问题。

---

## 【技术要点】

1. **三类算子形态**：
   - 内置算子（`__builtin_` 前缀），由 `bishengir-compile` 自动链接配套内置模板库；
   - `hivm.hir.custom`：普通自定义算子，用 `symbol` + 用户提供的实现（`bitcode`/`source`/`compile`）；
   - `hivm.hir.custom_macro`：Macro 自定义算子，使用 `InPipe`/`OutPipe` + `sync_event_slots` 描述搬运与计算流水。
2. **统一接口形式**：`hivm.hir.custom "name" { attrs... } ins(..) outs(..) -> ...`；`outs` 可指定 `init` 操作数（即"初始化位置/初始值"）。
3. **结构化降级接口（仿 Linalg）**：通过 `iterator_types`（取值集合固定：`parallel / broadcast / transpose / reduction / interleave / deinterleave / inverse / pad / concat / gather / cumulative / opaque`）、`indexing_map`（`ArrayAttr<AffineMapAttr>`）、`max_rank`（默认 `5`，`i64`），让自定义算子暴露 `getIteratorTypesArray` 与 `getIndexingMaps`，从而被 flatten / broadcast / 布局类 Pass 当作"原生结构化算子"处理。
4. **Macro 同步机制**：Macro 实现体中每对"同方向 Pipe 的 `set_flag`/`wait_flag`"必须在 MLIR 中用一条 `#hivm.sync_event_slot<#hivm.pipe<...>, #hivm.pipe<...>>` 声明，`GraphSyncSolver` 据此分配 event ID 并在 macro 前后注入 set/wait。单槽位 / 双槽位是两种典型模式。
5. **临时 buffer（`tmps`）声明**：通过 `extra_buffers_types` + `extra_buffers_sizes` 描述，由 `hivm-alloc-extra-buffer` Pass 自动分配 `memref` 并追加到 `temp_buffers`（汇编中表现为 `tmps` 操作数段），通常无需手动设置。
6. **降级流程**：CustomOp → `HIVMToStandard` Pass（内置算子调内置库；用户提供实现 → 调用函数名 → `bishengir-compile` 按用户提供的链接命令链接） → 毕昇编译器输出 Object Files。

---

## 【关键机制与数据】

### 降级流程（原文 ASCII 图，逐字还原）

```text
┌─────────────────────────────────────────────────────────────────┐
│                          CustomOp                               │
│    hivm.hir.custom "name" { attrs... } ins(..) outs(...)        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  HIVMToStandard                                                 │
│  ───────────────────────────────────────────────────────────────│
│  • 内置算子                                                     │
│    -> 调用内置库                                                │
│  • 用户提供的实现 ->                                            │
|    -> 调用用户提供的函数名                                      |
|      -> bishengir-compile 使用用户提供的链接命令进行链接        |
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
            毕昇编译器将其编译为 Object Files
```

工作原理：
- **入口**：`hivm.hir.custom`/`hivm.hir.custom_macro` 算子在 MLIR 层面作为统一入口承接"内置/用户自定义/Macro 自定义"三种来源。
- **HIVMToStandard**：内置算子直接路由到内置库；用户实现则使用 `symbol` 中给出的函数名，并通过 `bitcode`/`source`/`compile` 中的链接命令让 `bishengir-compile` 完成链接。
- **后端**：链接后的产物被毕昇编译器进一步编译为 Object Files，进入硬件后端工具链。

### Macro 同步的事件机制（原文伪代码）

单槽位伪代码：
```text
load_gm_to_ubuf(src0)
load_gm_to_ubuf(src1)
set_flag(MTE2 → V, event 0)
wait_flag(MTE2 → V, event 0)
vector_vadd(...)
```

双槽位伪代码：
```text
load_gm_to_ubuf(src0)
set_flag(MTE2 → V, event 0)
load_gm_to_ubuf(src1)
set_flag(MTE2 → V, event 1)
wait_flag(MTE2 → V, event 0)
wait_flag(MTE2 → V, event 1)
vector_vadd(...)
```

原文性能数据：**原文未涉及具体性能数字**（未给出时延、吞吐或编译时间等量化数据）。

---

## 【表格解读】

### 表 1：参数说明

| 参数 | 描述 |
| --- | --- |
| `name` | 唯一算子名称。**注意**：部分名称为内置算子预留，命名多以 `__builtin` 为前缀。编译器会自动将此类内置算子链接到 `bishengir-compile` 配套内置模板库，无需用户额外配置。若使用自定义算子名称，用户需指定实现位置、编译命令及所有必要的信息。 |
| `inputs` | 输入参数 |
| `outputs` | 输出结果，可指定为 `init` 操作数，用作操作结果的初始值，或操作结果将写入的初始位置。 |

解读：`name` 字段是关键分流点——以 `__builtin` 为前缀的进入"内置算子"路径，由编译器自动处理；其余名字则要求用户补齐 `bitcode`/`source`/`compile` 等信息。`outputs` 支持"初始化/目标位置"双重语义，使 CustomOp 复用 `init` 形式即可承担"输出既有初始化"的场景。

### 表 2：属性说明

| 属性名 | 说明 | 备注/示例 |
| --- | --- | --- |
| `CoreType` | 在哪种核类型上执行 | 参见 `TCoreTypeAttr` |
| `Pipe` | 在哪个 Pipe 上执行（用于 `hivm.hir.custom`） | 参见 `PipeAttr` |
| `InPipe` | Macro 自定义算子的输入 Pipe | 参见 `PipeAttr`（`hivm.pipe_in`） |
| `OutPipe` | Macro 自定义算子的输出 Pipe | 参见 `PipeAttr`（`hivm.pipe_out`） |
| `VFMode` | 在向量单元上的运行模式 | 参见 `VFModeAttr`。当核类型为 Cube 时此属性被忽略。注意：内置算子可指定或不指定，编译器会检查正确性并规范化 |
| `Symbol` | 实现函数的名称 | - |
| `sync_event_slots` | Macro 自定义算子的同步槽位元信息。`GraphSyncSolver` 会据此填充 `sync_related_args`，并在 macro 前后注入 `set/wait flag`。 | 列表长度必须与 macro 实现体内、同一 Pipe 对上的 `set_flag`/`wait_flag` 对数一致。详见 [Macro sync_event_slots](#macro算子同步槽位sync_event_slots) |
| `iterator_types` | 逐操作数的迭代器语义，供结构化降级与 flatten 类 Pass 使用（`HIVM_IteratorTypeAttr`） | 可选；设置时长度应覆盖参与 tiling 的输入与输出 |
| `indexing_map` | 逐操作数的仿射索引映射（与 Linalg 的 `indexing_maps` 作用相同） | 可选，类型为 `ArrayAttr<AffineMapAttr>` |
| `max_rank` | flatten/布局类 Pass 支持的最大张量秩 | 可选 `i64` 属性，默认值 5 |
| `align_dim` | 逐操作数的维度对齐提示 | 通过 `arg_attrs` 挂在对应操作数上 |
| `arg_attrs` | 逐操作数的字典属性数组 | 类型为 `ArrayAttr`（例如操作数 2 上的 `{align_dim = 1 : i64}`）。Triton 前端根据注册类上的 `align_dim` 自动生成 |
| `extra_buffers_types` | 临时 buffer 的元素类型 | 由 `hivm-alloc-extra-buffer` Pass 分配 `memref` 并追加到 `temp_buffers`（汇编中为 `tmps`） |
| `extra_buffers_sizes` | 临时 buffer 的一维大小（元素个数） | 同上 |
| `temp_buffers` | 传给设备实现的临时 `memref`（`tmps` 操作数段） | 通常由 `extra_buffers_*` 属性自动填充，无需手动设置 |
| `no_side_effect` | 表示算子无副作用 | - |
| `bitcode` / `source` / `compile` | 实现产物路径及可选编译命令 | 通常由 Triton 前端设置 |

解读：属性大致可分为四类——①执行目标定位（`CoreType` / `Pipe` / `InPipe` / `OutPipe` / `VFMode`）；②实现绑定（`Symbol` / `bitcode` / `source` / `compile`）；③结构化降级（`iterator_types` / `indexing_map` / `max_rank`，默认 `max_rank=5`）；④优化提示与副作用（`align_dim` / `arg_attrs` / `no_side_effect`）。`sync_event_slots` 与 `extra_buffers_*`/`temp_buffers` 则属于"流水线同步"和"运行时内存分配"两类辅助属性。

### 表 3：支持能力一览

| 特性 | 说明 |
| --- | --- |
| CoreType | 自定义算子执行核 |
| Pipe | 自定义算子执行 pipe（`hivm.hir.custom`） |
| InPipe / OutPipe | Macro 自定义算子的输入/输出 pipe（`hivm.hir.custom_macro`） |
| VFMode | 自定义算子在向量核上的运行模式：SIMT/SIMD/MIX |
| Symbol | 使用者提供的函数名称 |
| sync_event_slots | Macro 同步槽位声明，用于 GraphSyncSolver 集成 |
| iterator_types | Tiling / flatten 的逐操作数迭代器语义 |
| indexing_map | 结构化降级的逐操作数仿射映射 |
| max_rank | 布局 Pass 支持的最大张量秩（默认 5） |
| align_dim / arg_attrs | 对齐调整 Pass 的逐操作数对齐提示 |
| extra_buffers_* / tmps | 临时 buffer 声明与分配 |
| no_side_effect | 纯算子标记，便于优化 |
| 内置算子 | 一组内置算子（名称预留） |

解读：这是"能力清单"视图，与表 2 属性说明互为映射：表 2 给出"字段语义"，本表给出"面向用户的特性条目"，并显式给出向量运行模式枚举（`SIMT` / `SIMD` / `MIX`）以及 `max_rank` 的默认值 `5`。

### 表 4：Macro sync_event_slots 模式对比

| 模式 | Python / MLIR 槽位数 | 典型设备代码 | 适用场景 |
| --- | --- | --- | --- |
| 单槽位 | 1 × `(PIPE_MTE2, PIPE_V, INTERNAL)` | 两次 GM→UB 搬运完成后，一次 `set_flag` + `wait_flag`，再执行向量计算 | 默认场景：两次 load 连续执行，向量计算开始前只需一次 MTE2 到 V 的同步 |
| 双槽位 | 2 × `(PIPE_MTE2, PIPE_V, INTERNAL)` | `load` → `set_flag(0)` → `load` → `set_flag(1)` → `wait_flag(0)` → `wait_flag(1)` → 向量计算 | 每次 GM→UB 需要独立 event 的场景，如流水重叠、或需按次确认搬运完成 |

解读：单槽位用 1 个 event 涵盖两次搬运的同步开销，适合"搬运连续、不需独立确认"的默认情形；双槽位为每一次搬运各分配一个 event，可与搬运并行进行以便按次确认完成，原文用此来表达流水重叠的语义。两者都要求"槽位数 = 同方向 Pipe 上的 `set_flag`/`wait_flag` 对数"，否则 GraphSyncSolver 分配的 event ID 与 kernel 不匹配。

---

## 【公式解读】

**原文无 LaTeX 公式**。原文中仅有伪代码（单槽位、双槽位），已分别在「关键机制与数据」节中逐行呈现并解读其流水线语义，无符号化的数学公式需额外解读。

---

## 【关联】

- 与 **`HIVMToStandard` Pass** 的关系：所有 CustomOp（内置/用户/Macro）最终都经 `HIVMToStandard` 降级，是该 Pass 的核心消费者。
- 与 **`bishengir-compile`** 的关系：内置算子由 `bishengir-compile` 自动链接内置模板库；用户实现则需用户提供链接命令，由 `bishengir-compile` 完成链接。
- 与 **`hivm-alloc-extra-buffer` Pass** 的关系：消费 `extra_buffers_types`/`extra_buffers_sizes`，分配 `memref` 并追加到 `temp_buffers`（汇编层 `tmps`）。
- 与 **`GraphSyncSolver`** 的关系：消费 Macro 自定义算子的 `sync_event_slots`，填充 `sync_related_args` 并在 macro 前后注入 `set/wait flag`。
- 与 **结构化降级 Pass（flatten / broadcast / 布局类）** 的关系：通过 `iterator_types` / `indexing_map` / `max_rank`（默认 `5`）暴露 `getIteratorTypesArray` 与 `getIndexingMaps`，使这些 Pass 可将其视作原生结构化算子处理。
- 与 **对齐调整 Pass** 的关系：通过 `align_dim` / `arg_attrs` 提供逐操作数对齐提示。
- 与 **Triton 前端** 的关系：Triton 通过 `al.register_custom_op` 注册类暴露 `core` / `pipe` / `mode` / `symbol` / `bitcode` / `iterator_types` 等字段，并基于 `align_dim` 自动生成 MLIR `arg_attrs`；常见路径属性（`bitcode` / `source` / `compile`）通常由 Triton 前端设置。
- 与 **Macro 同步**：本文档内部以 [Macro sync_event_slots](#macro算子同步槽位sync_event_slots) 自引用指向表 4 与单/双槽位示例段。

---

## 【使用方法】

**内置算子声明（`__builtin_` 前缀，编译器自动链接模板库）**：

```mlir
%0 = hivm.hir.custom
       "__builtin_gather_load"
       ins(%arg0, %arg1, %c4_i64, %c0_i32, %c2_i64, %c1_i64, %c2_i32, %c2_i32, %c0_i32, %c0_i32
           : memref<?xf32>, tensor<3x3xi64>, i64, i32, i64, i64, i32, i32, i32, i32)
       outs(%empty : tensor<3x3xf32>) -> tensor<3x3xf32>
```

**自定义算子声明（用户实现）**：

```mlir
%0 = hivm.hir.custom
      { hivm.tcore_type = #hivm.tcore_type<VECTOR>, hivm.pipe = #hivm.pipe<PIPE_V>, hivm.vf_mode = #hivm.vf_mode<SIMD>,
        symbol = "my_custom" }
      "my_custom_op"
      ins(%arg0, %arg1, %c4_i64, %c0_i32, %c2_i64, %c1_i64, %c2_i32, %c2_i32, %c0_i32, %c0_i32
          : memref<?xf32>, tensor<3x3xi64>, i64, i32, i64, i64, i32, i32, i32, i32)
      outs(%empty : tensor<3x3xf32>) -> tensor<3x3xf32>
```

**自定义 Macro 算子（含 sync_event_slots 单槽位示例）**：

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

**双槽位 sync_event_slots MLIR 片段**：

```mlir
sync_event_slots = [
  #hivm.sync_event_slot<#hivm.pipe<PIPE_MTE2>, #hivm.pipe<PIPE_V>>,
  #hivm.sync_event_slot<#hivm.pipe<PIPE_MTE2>, #hivm.pipe<PIPE_V>>
]
```

**结构化降级属性使用（`iterator_types` + `indexing_map` + `max_rank=5`）**：

```mlir
#map2d = affine_map<(d0, d1) -> (d0, d1)>
%0 = hivm.hir.custom
    {hivm.tcore_type = #hivm.tcore_type<VECTOR>,
     hivm.pipe = #hivm.pipe<PIPE_V>,
     hivm.vf_mode = #hivm.vf_mode<SIMD>,
     symbol = "k_named_maps",
     max_rank = 5 : i64,
     iterator_types = [#hivm.iterator_type<parallel>, #hivm.iterator_type<parallel>],
     indexing_map = [#map2d, #map2d, #map2d]}
    "user.named_maps"
    ins(%arg0, %arg1 : memref<2x2xf32>, tensor<2x2xf32>)
    outs(%empty : tensor<2x2xf32>) -> tensor<2x2xf32>
```

**Triton 注册示例**：

```python
@al.register_custom_op
class tiled_custom_op:
    core = al.CORE.VECTOR
    pipe = al.PIPE.PIPE_V
    mode = al.MODE.SIMT
    symbol = "my_tiled_func"
    bitcode = "/path/to/kernel.bc"
    iterator_types = [
        al.IteratorType.Parallel,
        al.IteratorType.Broadcast,
    ]

    def __init__(self, x, y, out=None):
        # 每个结构化操作数（输入 + 输出）对应一个仿射映射。
        self.indexing_map = [
            al.affine_map.get_identity(2),
            al.affine_map.get_identity(2),
            al.affine_map.get_identity(2),
        ]
```

**操作数对齐属性（`align_dim` 通过 `arg_attrs` 挂载）**：

```mlir
%0 = hivm.hir.custom { ... }
    "my_custom_op"
    ins(%arg0 {align_dim = 1 : i64}, %arg1 {align_dim = 0 : i64} : memref<?xf32>, memref<?xf32>)
    outs(%dst : tensor<?xf32>) -> tensor<?xf32>
```

**启用要点（基于原文提炼）**：
- 算子名以 `__builtin` 为前缀 → 走内置库路径，否则需提供 `bitcode`/`source`/`compile`；
- Macro 算子必须通过 `InPipe`/`OutPipe` + `sync_event_slots` 声明搬运—计算流水，且槽位数要与实现中同方向 Pipe 的 `set_flag`/`wait_flag` 对数严格一致；
- 期望参与 tiling/flatten/布局类 Pass 的自定义算子应声明 `iterator_types` + `indexing_map`（覆盖参与 tiling 的输入与输出），并可显式指定 `max_rank`（默认 `5`）；
- 临时 buffer 通过 `extra_buffers_types` + `extra_buffers_sizes` 声明，由 `hivm-alloc-extra-buffer` 自动生成 `temp_buffers`（汇编 `tmps`），通常无需手动写；
- `no_side_effect` 用于标记纯算子以辅助优化；
- `align_dim` 通过 `arg_attrs` 挂到对应操作数上，Triton 前端会基于注册类的 `align_dim` 自动生成。

**原文未涉及**：`CLI` 启动开关、环境变量、`bishengir-compile` 的具体链接命令模板与可选项、用户实现的端到端构建脚本——文档中均未给出。
```

> 备注：原文末尾的"Triton 示例（在 `_`"存在截断，因此未再额外补充该段示例；其它内容均严格基于原文未做臆造。
