# ascend_lower_parallel_to_vector.cc 设计文档

> 仓 `tilelang-ascend` · 路径 `.agents/skills/tilelang-pass-analyzer/references/pass-designs/ascend_lower_parallel_to_vector_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/.agents/skills/tilelang-pass-analyzer/references/pass-designs/ascend_lower_parallel_to_vector_design.md

【定位】
这篇文档描述 TileLang-Ascend 编译器中的 `AscendLowerParallelToVector` Pass：将前端 `T.Parallel` 语义（IR 层的 `ForNode(kind=kParallel)` 并行循环）下推/转换为 AscendC 后端的向量化调用（`tl::ascend_add/exp/...`），从而用统一的并行 IR 同时承载一元/二元元素向量化计算，并兼容 `T.tile.xxx` 形式的老接口。

【技术要点】
1. **Pass 定位**：属于 Phase 1 `LowerAndLegalize` 阶段，执行时机在 `Simplify()` 之后、`LayoutInference()` 之前；Ascend 专用，默认启用，无配置开关。
2. **承载 IR**：以 `For ... in T.Parallel(M, N)` 描述 tile 内元素向量化计算，IR 形态为 `ForNode(kind=kParallel, extent=N)`，最终 lower 为 `Call(op=ascend_xxx, args=[out_ptr, in1_ptr, ..., count])`。
3. **三大内部模块**：表达式分解 `DecomposeExpr()`、广播处理 `CanBroadcast()`、GM→UB 写入处理 `AutoCopy GM→UB`，共同产出 AscendC 向量调用。
4. **维度与循环识别**：支持 1D、`Serial→Parallel`、2D (`Parallel→Parallel→Store`) 三种向量化形态；遇到三层及以上并行循环直接报"不支持3D及以上"错误。
5. **核心数据结构**：`AscendLowerParallelToVector : arith::IRMutatorWithAnalyzer`（追踪 `vector_dim_var_`/`outer_dim_var_`/`is_2d_vectorizing_`）、`VectorPlan`、`BroadcastInfo`，并维护 `temp_buffers_` 与 `temp_buffer_id_`。
6. **操作映射双轨制**：上层鼓励使用 `T.exp/T.log/T.sqrt/T.max` 等主仓符号算子（保持可移植）；AscendC 特有能力以 `T.tile.xxx` 形式在 `ascend_tile.py` 集中封装，复用原 `ascend.py` 中的 vector 操作。

【关键机制与数据】
- **工作原理（数据流）**：前端 DSL `T.Parallel` → IR `ForNode(kParallel) + BufferStore` → `AscendLowerParallelToVector` Pass（循环结构识别 → 向量化计划检测 `DetectVectorPlan` → 表达式分解 `DecomposeExpression`/广播判断 `CanBroadcast`/临时 Buffer 分配 `CreateTempBuffer`）→ 后端 IR `Call(ascend_xxx, [out_ptr, in1_ptr, in2_ptr, count])` → AscendC 代码生成（`AscendC::Add(out, in1, in2, count)`）。
- **Pass 入口流程**：① 创建 `arith::Analyzer`；② 创建 `AscendLowerParallelToVector(analyzer)`；③ 调用 `substituter.VisitStmt(f->body)` 遍历变换；④ 将 `new_body` 写回 `fptr->body`。
- **循环结构识别分支**：
  - Case 1：`parallel → (store | seq)` → `TryVectorizeStoreSeq()`
  - Case 2：`parallel → parallel → (store | seq)` → `TryVectorizeStoreSeq(is_2d=True)`（若存在第三层 For 则报错）
  - Case 3：`serial → parallel → (store | seq)` → `TryVectorizeStoreSeq(has_outer_serial=True)`，成功则保留外层 Serial 循环。
- **向量计划检测（原文, DetectVectorPlan 伪代码截断处）**：
  - 1D：`output_buffer->shape.size() == 1` 且 `indices[0]` 包含 `vector_dim_var` 时，`inner_vec_len = element_count`、`outer_extent = 1`、`is_2d_vectorizable = false`；
  - 2D：`shape.size() == 2` 且 `indices[1]` 包含 `vector_dim_var` 时，`inner_vec_len = vector_dim_extent_ or buffer->shape[1]`。
- **广播维度取值**：`BroadcastInfo::broadcast_dim` 取值为 `0` 或 `1`；涉及 `outer_extent`、`inner_vec_len`、`workspace_buffer`。
- **一元/二元算子到 AscendC 的命名约定**：向量版为 `tl::ascend_xxx()`，标量版（仅二元）以尾缀 `s` 区分，如 `ascend_adds/subs/muls/divs`。
- **性能数据**：原文未涉及任何实测数据或基准数字。

【表格解读】

**表 1：Pass 定位与触发（2.2 节）**

| 维度 | 说明 |
|------|------|
| 所属阶段 | Phase 1: LowerAndLegalize（IR Lowering 与合法化） |
| 执行时机 | 在 `Simplify()` 之后、`LayoutInference()` 之前 |
| 平台特性 | Ascend 专用 Pass |
| 启用方式 | 默认启用，无配置开关 |

逐行解读：
- *所属阶段*：明确该 Pass 属于 IR Lowering 阶段的合法化子阶段，下接布局推断。
- *执行时机*：必须在 `Simplify()`（代数化简）之后运行——保证表达式形式稳定；又必须在 `LayoutInference()` 之前——因为其输出会参与后续布局决策。
- *平台特性*：Ascend 后端专属，不影响其他后端。
- *启用方式*：无条件默认启用，不暴露配置开关，体现其作为必需 Lowering 步骤的定位。

**表 2：一元操作映射（3.1.2 节，TIR → AscendC）**

| TIR Op | AscendC Op | 说明 |
|--------|-----------|------|
| `tir.exp` | `tl::ascend_exp()` | 指数函数 |
| `tir.log` | `tl::ascend_ln()` | 自然对数 |
| `tir.sqrt` | `tl::ascend_sqrt()` | 平方根 |
| `tir.rsqrt` | `tl::ascend_rsqrt()` | 平方根倒数 |
| `tir.fabs` | `tl::ascend_abs()` | 绝对值 |
| `max(x, 0)` | `tl::ascend_relu()` | ReLU |
| `tir.bitwise_not` | `tl::ascend_bitwise_not()` | 按位取反 |

逐行解读：
- `tir.exp/log` 是初等超越函数，按 AscendC 命名 `exp/ln`（注意 `log` 映射为 `ln`，语义上是自然对数）。
- `tir.sqrt/rsqrt` 互为倒数对，单独暴露以避免运行时取倒数。
- `tir.fabs` 映射为 `ascend_abs()`：AscendC 用通用名 `abs` 而非 `fabs`，但语义仍为浮点绝对值。
- `max(x, 0)` 由模式匹配得到 `ReLU`，而不是显式 `tir.relu` Op，体现表达式分解能力。
- `tir.bitwise_not` 是该表中唯一的整数位运算原语。

**表 3：二元操作映射（3.1.2 节）**

| TIR Op | AscendC Op | Scalar版本 | 说明 |
|--------|-----------|-----------|------|
| `Add` | `tl::ascend_add()` | `ascend_adds()` | 加法 |
| `Sub` | `tl::ascend_sub()` | `ascend_subs()` | 减法 |
| `Mul` | `tl::ascend_mul()` | `ascend_muls()` | 乘法 |
| `Div` | `tl::ascend_div()` | `ascend_divs()` | 除法 |
| `Min` | `tl::ascend_min()` | - | 最小值 |
| `Max` | `tl::ascend_max()` | - | 最大值 |
| `bitwise_and` | `tl::ascend_bitwise_and()` | - | 按位与 |
| `bitwise_or` | `tl::ascend_bitwise_or()` | - | 按位或 |
| `shift_left` | `tl::ascend_bitwise_lshift()` | - | 左移 |
| `shift_right` | `tl::ascend_bitwise_rshift()` | - | 右移 |

逐行解读：
- 前四行算术运算同时给出向量版与标量版（`xxx` vs `xxxs`），对应"对每个元素施加常数"的标量广播情形——这与 `CanBroadcast()` 广播模块的能力相呼应。
- `Min/Max` 无 Scalar 版本，因为对单一常数取 `min/max` 可由编译期折叠处理，无需运行时调用。
- 后四行位运算统一前缀 `bitwise_`，命名风格一致，强调按位语义而非逻辑语义。

【公式解读】
原文无公式。文档中出现的仅为算法伪代码（Pass 入口、循环结构识别、向量计划检测），不含 LaTeX 数学公式或符号化等式。

【关联】
- **上游依赖**：`Simplify()` Pass（代数化简）——本 Pass 必须在其之后运行；前端 `T.Parallel` 原语（用户可见 API）。
- **下游衔接**：`LayoutInference()`（布局推断）——接收本 Pass 的输出（已 lower 的 `Call`）继续处理；AscendC 代码生成器——最终生成 `AscendC::Add/...` 指令。
- **与主仓的关系**：通过复用 `T.exp/T.log/T.sqrt/T.max` 等主仓符号算子实现跨后端可移植性，本 Pass 只在 Ascend 后端生效。
- **Ascend 内部模块**：与 `ascend_tile.py` 中 `T.tile.xxx` 接口（继承自原 `ascend.py` 的 vector 操作）共存——上层符号 API 与底层 vector tile 原语双轨并行，互不替代。
- **错误路径**：当遇到 3D 及以上并行循环时 Pass 报错（"不支持3D及以上"），意味着对 2D 以上的并行需要前置 Pass（如 tiling/scheduling）将其拆解。

【使用方法】
- 启用方式：默认启用，无配置开关（原文 2.2 节明示）。
- 配置项：原文未涉及任何环境变量、Tilelang 配置开关或命令行参数。
- 调用命令：原文未涉及（Pass 由编译器内部流水线调度，非用户手动调用）。
- 编写建议（原文 1.3 节）：优先在 `T.Parallel` 体内使用 `T.exp/T.log/T.sqrt/T.max` 等主仓符号算子以保持可移植；需要 AscendC 特有 vector 能力时使用 `T.tile.xxx` 接口（封装于 `ascend_tile.py`）。
