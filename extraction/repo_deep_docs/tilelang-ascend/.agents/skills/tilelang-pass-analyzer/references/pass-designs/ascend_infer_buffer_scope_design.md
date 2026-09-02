# AscendInferBufferScope Pass 设计文档

> 仓 `tilelang-ascend` · 路径 `.agents/skills/tilelang-pass-analyzer/references/pass-designs/ascend_infer_buffer_scope_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/.agents/skills/tilelang-pass-analyzer/references/pass-designs/ascend_infer_buffer_scope_design.md

# AscendInferBufferScope Pass 设计文档深度解读

---

## 【定位】

这篇文档描述了 `AscendInferBufferScope` Pass 的设计方案: 它是 TileLang→Ascend 后端编译流水线上, 负责把前端抽象的 `T.alloc_fragment` / `T.alloc_shared` buffer scope "二次推断"为具体物理 scope (L0A/L0B/L0C/L1/UB) 的 Lowering Pass, 从而让后续 codegen 能生成正确的搬运指令、寄存器声明与访问语义。

---

## 【技术要点】

1. **Pass 注册与触发**: 注册名为 `tl.transform.InferAllocScope`, 默认启用无开关, 所属阶段为 Phase 1 (LowerAndLegalize), 执行时机在 `InjectTmpBuffer` 之后、`AscendVidReduction` 之前。

2. **GEMM 角色识别**: 基于 buffer 在 `gemm/mma/matmul` 函数调用中的参数位置, 把 `local.fragment` 分别改写为 `wmma.matrix_a` (L0A, 位置 0)、`wmma.matrix_b` (L0B, 位置 1)、`wmma.accumulator` (L0C, 位置 2); 若未参与 GEMM 则默认落到 `wmma.accumulator`。

3. **L1/UB 区分**: 对 `shared` buffer, 若仅参与 Vector 计算 → `shared.ub` (UB); 仅参与 Cube 计算 → `shared.l1` (L1); Cube+Vector 混合 → `shared.l1` (L1)。

4. **ascend_copy 链二次推断**: 对仅作为 `tl.ascend_copy` 端点的 `shared` buffer, 若对端是 L0A/L0B 则保留 `shared.l1`/L1, 否则降级为 `shared.ub`/UB。

5. **IR 全局一致性重写**: 通过 `ScopeCorrector` (StmtExprMutator) 把新 scope 同步到 `AllocateNode`、`BlockNode` (同时注入默认 `zN` Layout)、`VarNode`、`BufferLoad/Store/Call` 等节点。

6. **三类数据结构**: `BufferUseInfo` (使用语义)、`BufferAllocationInfo` (申请位置)、`AscendCopyPositionInfo` (搬运链位置) 共同支撑"收集 → 推断 → 重写"三阶段流水线。

---

## 【关键机制与数据】

### 工作原理 (三阶段流水线)

文档明确给出的处理流程, 详见 §2.2 架构图与 §3.2.1 Pass 入口流程:

- **阶段 1 — BufferUseCollector (StmtExprVisitor)**:
  - `BuildHandleAllocMapping` 建立 `handle_var → BufferAllocationInfo` 映射, 同时记录 `from_block_alloc` (来自 `Block.alloc_buffers`) 与 `from_block_alloc=false` (来自 `AllocateNode`) 两种来源。
  - `VisitExpr_(CallNode)` 三分支:
    - `tl.ascend_copy`: 解析 `args[0]/args[1]` 的 `BufferLoad` 得到 first/second buf handle, 记录到 `ascend_copy_buffer_pairs_` 并更新两端 `AscendCopyPositionInfo`, 同时把 `"tl.ascend_copy"` 加入 `func_names`。
    - `call_extern`: 取 `args[0]` 为函数名, 对 `args[1..]` 调用 `AnalyzeBufferInCall`。
    - 其他已知 OpNode: 对所有 args 调用 `AnalyzeBufferInCall`。
  - `AnalyzeBufferInCall`: 解析 `tvm_access_ptr(..., buffer_var, ...)` 取出 `buffer_var`, 加入 `func_names`/`call_sites`; 若 `IsGEMMFunction` 则 `used_in_cube=true` 并调用 `DetermineGEMMPosition`; 若 `IsVectorFunction` 则 `used_in_vector=true`。

- **阶段 2 — InferCorrectScopes (推断)**:
  - local.fragment → L0A/L0B/L0C (依据 `gemm_positions`)
  - shared → L1/UB (依据 Cube/Vector 使用模式)
  - ascend_copy 链二次推断
  - UB↔unknown pair 传播

- **阶段 3 — ScopeCorrector (StmtExprMutator)**:
  - 重写 `AllocateNode` / `BlockNode` (注入 `zN` 默认 Layout) / `VarNode` / `BufferLoad-Store-Call` 五类节点。

### 决策图 (Scope 推断决策, 原文 §2.3 mermaid)

| 起始 | 判定 | 结果 |
|------|------|------|
| local.fragment | 含 gemm_positions=0 | wmma.matrix_a / L0A |
| local.fragment | 含 gemm_positions=1 | wmma.matrix_b / L0B |
| local.fragment | 含 gemm_positions=2 | wmma.accumulator / L0C |
| local.fragment | gemm_positions 空 | wmma.accumulator (默认) |
| shared | 仅 Vector | shared.ub / UB |
| shared | 仅 Cube | shared.l1 / L1 |
| shared | Cube+Vector | shared.l1 / L1 |
| shared (端点) | 对端是 L0A/L0B | 保留 shared.l1 / L1 |
| shared (端点) | 对端非 L0A/L0B | 改为 shared.ub / UB |

### 性能数据
原文: **未提供任何性能数据 / benchmark 数字**。

---

## 【表格解读】

### 表 1: Pass 定位与触发 (原文 §2.1)

| 维度 | 说明 |
|------|------|
| 所属阶段 | Phase 1: LowerAndLegalize (IR Lowering 与合法化) |
| 执行时机 | 在 `InjectTmpBuffer` 之后、`AscendVidReduction` 之前 |
| 平台特性 | Ascend 专用 Pass |
| 启用方式 | 默认启用, 无配置开关 |
| 注册名 | `tl.transform.InferAllocScope` |

**逐行解读**:
- **所属阶段** Phase 1: LowerAndLegalize — 表明本 pass 属于 IR Lowering 阶段, 而非后端 codegen 阶段, 仍处于 `tilelang/engine/phase.py` 管控的 Python 层调度范围内。
- **执行时机** 在 `InjectTmpBuffer` 之后、`AscendVidReduction` 之前 — 这一位置决定了本 pass 的输入一定不含临时 buffer 注入带来的额外 Allocate, 同时输出必须保证后续 Vector reduction 优化看到的是已细化的物理 scope。
- **平台特性** Ascend 专用 Pass — 不会影响其他后端 (CUDA/ROCm/Metal) 的编译流。
- **启用方式** 默认启用无配置开关 — 意味着 Ascend 后端用户无需关心是否启用, 总是隐式参与。
- **注册名** `tl.transform.InferAllocScope` — Python 端调用名 (`mod = tilelang.transform.AscendInferBufferScope()(mod)`) 与 C++ 注册名 (`InferAllocScope`) 之间是同名绑定的, 用户在 phase.py 中调用的就是这一名称。

### 表 2: 函数分类规则 (原文 §3.1.4)

| 类别 | 判定关键字 (lower-case 匹配) | 排除关键字 |
|------|-----------------------------|-----------|
| GEMM 函数 | `gemm` / `mma` / `matmul` 任一包含 | — |
| Vector 函数 | 非 GEMM | `copy` / `memcpy` / `dma` 任一不包含 |

**逐行解读**:
- **GEMM 函数** 用 `kGemmKeywords = {"gemm", "mma", "matmul"}` 做"任一命中"判定, 这意味着函数名只要小写后包含这三个关键字之一就被识别为 Cube 计算。
- **Vector 函数** 用 `kVectorKeywords = {"copy", "memcpy", "dma"}` 做"全部不命中"判定, 即既不是 GEMM 又不是搬运/拷贝/DMA 操作的函数才被归类为 Vector。这是"排除式"分类, 实际涵盖了大量逐元素算子 (如 `add`/`mul`/`exp`/`reduce` 等非 GEMM、非搬运的函数)。
- 这种"包含 vs. 排除"的对偶设计保证了同一函数不会被同时归类为 GEMM 和 Vector, 但**也没有显式 whitelist 列出 Vector 函数**, 完全依赖关键字启发式, 名字不合规的函数会被错误归类。

---

## 【公式解读】

### 公式 1: GEMM 函数判定 (原文 §3.1.4)

```
IsGEMMFunction(name)   = ContainsAny(lower(name), {gemm, mma, matmul})
```

**符号解释**:
- `name`: 字符串, 表示待判定函数的名字 (来自 `call_extern` 的 `args[0]`, 或 OpNode 的 `op->name`)。
- `lower(name)`: 先转小写以实现大小写不敏感匹配。
- `{gemm, mma, matmul}`: 关键字集合, 即 `kGemmKeywords`。
- `ContainsAny(s, kwset)`: 字符串 `s` 是否包含 `kwset` 中任一关键字 (子串包含判定)。
- **作用**: 命中则把对应 buffer 标记为 `used_in_cube=true`, 并触发 `DetermineGEMMPosition` 来区分 A/B/C 位置。

### 公式 2: Vector 函数判定 (原文 §3.1.4)

```
IsVectorFunction(name) = !IsGEMMFunction(name) && !ContainsAny(lower(name), {copy, memcpy, dma})
```

**符号解释**:
- `!IsGEMMFunction(name)`: 排除 GEMM/MMA/Matmul。
- `!ContainsAny(lower(name), {copy, memcpy, dma})`: 排除搬运/拷贝/DMA 操作, 即 `kVectorKeywords` = `{"copy", "memcpy", "dma"}`。
- **作用**: 双重否定后, 表示"既不是 GEMM 也不是搬运函数"的算子, 通常对应 Ascend 的 Vector Unit 逐元素计算。命中则把 buffer 标记为 `used_in_vector=true`。

> 注: 文档第 3.2.2 节伪代码 `DetermineGEMMPosition` 在 "0 → A (L0" 处截断, `B`/`C` 的判定逻辑未在原文中给出, 本节不予臆造。

---

## 【关联】

### 上下游 Pass 关系 (原文 §2.1 phase.py 顺序)

| 位置 | Pass | 与本 Pass 的关系 |
|------|------|-----------------|
| 上游 | `InjectTmpBuffer` | 先注入临时 buffer; 本 pass 基于最终 Allocate 集合做 scope 推断 |
| **本 Pass** | `AscendInferBufferScope` | — |
| 下游 | `AscendVidReduction` | 依赖本 pass 输出的 L1/UB 细化 scope 做 Vector reduction 优化 |
| 下游 | `BufferShapeCollector` | 依赖 scope 已收敛的状态收集 shape 信息 |
| 下游 | `LowerTileOp` / `AscendMemoryPlanning` / `AscendSyncInsert` | (原文 §1.2 业务价值) 基于正确的存储级别做内存规划、地址映射与同步指令生成 |

### 前端 API 关联 (原文 §1.1)
- 用户 API: `T.alloc_fragment` / `T.alloc_shared` (统一抽象)。
- 本 pass 输出 scope: `wmma.matrix_a` / `wmma.matrix_b` / `wmma.accumulator` / `shared.l1` / `shared.ub`。
- 关联 Buffer 类型注解: `Allocate` / `Block.alloc_buffers` / `Var` / `BufferLoad` / `BufferStore` / `tvm_access_ptr` (原文 §1.3.4 列出六类需要同步重写的 IR 节点)。

### 默认 Layout 关联 (原文 §2.2 阶段 3 标注)
- `ScopeCorrector` 重写 `BlockNode` 时会同步注入默认 Layout map (`zN`), 即 scope 推断与默认 Layout 注入在同一 pass 内完成。

---

## 【使用方法】

### 启用方式
- **默认启用**: 原文明确写明"默认启用, 无配置开关" (§2.1 表格"启用方式"行)。
- **注册名**: `tl.transform.InferAllocScope` (§2.1 表格"注册名"行)。
- **Python 调用样例** (原文 §2.1 phase.py 片段):
  ```python
  mod = tilelang.transform.InjectTmpBuffer(target)(mod)
  mod = tilelang.transform.AscendInferBufferScope()(mod)   # ← 本 pass
  mod = tilelang.transform.AscendVidReduction()(mod)
  mod = tilelang.transform.BufferShapeCollector()(mod)
  ```

### 配置项 / 命令行开关
- 原文未涉及任何额外配置项、命令行开关或环境变量。Pass 仅在 Ascend 后端编译流中自动运行, 用户无可见控制点。
