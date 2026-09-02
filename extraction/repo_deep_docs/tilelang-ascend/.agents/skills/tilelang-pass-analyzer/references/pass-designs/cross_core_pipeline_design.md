# 核间 pipeline 示例

> 仓 `tilelang-ascend` · 路径 `.agents/skills/tilelang-pass-analyzer/references/pass-designs/cross_core_pipeline_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/.agents/skills/tilelang-pass-analyzer/references/pass-designs/cross_core_pipeline_design.md

【定位】
本文档描述 TileLang-Ascend 中 **CrossCorePipeline pass** 的设计：当用户通过 `T.Pipelined(loop_num, num_stages)` 标注的循环内同时出现 Cube（矩阵）与 Vector（tile）两类操作时，自动将该循环拆分为多 stage 双核异步并行结构，并通过扩展 workspace buffer 实现 CV 核间数据 overlap，从而隐藏计算延迟。

---

【技术要点】

1. **跨核检测机制**：`CrossCoreDetector` 遍历带 `num_stages` 注解的 `ForNode`，逐条解析 `EvaluateNode` 中的 `Call`，通过预置的 `callnodeMapPos_`（`wmma.matrix_a/b/accumulator` → cube；`shared.ub` → vec；`shared.l1` → cube 等）映射判断每条语句的 `core_scope`；当循环体内同时出现 CUBE_SCOPE 与 VEC_SCOPE 时，将 `is_cross_core` 置 true。

2. **三段式流水线重写管线**：`CrossCoreDetector`（检测） → `LoopAnalyzer`（按 scope 统计语句、收集 `tvm_access_ptr` 访问元数据） → `LoopRewriter`（按 scope 连续性 `SplitIntoStages`、通过 `CheckExposedRead` 识别共享 buffer、`CreateStagedLoops` 生成 stage 循环并添加 `i_transformed = i_outer * num_stages + i_stage` 绑定）。配套还有 `BufferMapTransformer`（扩展 buffer 维度）与 `BufferAccessAdjuster`（调整 offset）。

3. **核心常量定义**：`INVALID_SCOPE = -1`、`CUBE_SCOPE = 0`、`VEC_SCOPE = 1`；所有循环、语句、buffer 均以此 scope 标记归属核。

4. **跨核同步频率控制**：`cross_interval` 通过 `T.Pipelined(num_iters, num_stages, cross_interval)` 传入，默认 = 1。值会被写入 stage 循环注解 `tl_cross_interval`，由下游 `CombineCV` pass 在生成 `CrossCoreSetFlag` / `CrossCoreWaitFlag` 时引用；`cross_interval=N` 时 `SetFlag` 在 `i%N==N-1` 或末次迭代时执行，`WaitFlag` 在 `i%N==0` 时执行。该参数仅在核间流水线生效，核内流水线下无效。

5. **Buffer 双版本化与 offset 调整**：对 shared_buffer / workspace_buffer，沿第一维插入 `num_stages`，并把 `tvm_access_ptr` 的 offset 调整为 `original + i_stage * total_size`，同时记录 `buffer_versions` 供后续 pass 使用；外层循环长度变为 `N / num_stages`，并附 `tl_original_extent` 注解。

6. **上下游协作边界**：本 pass 仅完成循环拆分、buffer 多版本化与 stage 变量变换；实际的 `set_flag/wait_flag` 同步指令由下游 `AscendSyncInsert` pass 插入；`CrossCoreSetFlag` / `CrossCoreWaitFlag` 的精确发射时机则由 `CombineCV` pass 根据 `tl_cross_interval` 决定。

---

【关键机制与数据】

- **核间流水掩盖原理（原文）**：「C核 produce wk_1 → V核 consume wk_1 → V核 produce wk_2 → C核 consume wk_2 → C核 produce wk_3 → V核 consume wk_3」。串行模式下两核交替空闲；开启 stage=2 流水线后，每个 workspace 申请 2 块空间，使 CV 双核可在相邻 stage 异步并行，文档以「Cube 产出第 i+1 片数据的同时 Vector 消费第 i 片数据」描述 overlap。

- **典型调用模式（原文 §1.1）**：`for i T.Pipelined(cross_core_proc_num, num_stages=2):` 内先 `T.copy(...l1)` → `T.gemm(...l0c)`（Cube）→ `T.copy(acc_s_l0c, workspace_1)` → `T.copy(workspace_1, acc_s_ub_)` → `T.add(...)`（Vector）。该模式与 SFA、FlashAttention 等 GEMM+tile 融合算子的结构吻合。

- **核心变换伪流程（原文 §3.2.1）**：①收集 buffer scope 映射 → ② `CrossCoreDetector.DetectCrossCorePipelines()`，若无跨核循环则 `return f` → ③ `BufferMapTransformer.TransformBufferMap()` → ④ `LoopAnalyzer.Analyze()` → ⑤ `LoopRewriter.Rewrite()`（含 SplitIntoStages / AnalyzeSharedBuffers / CreateStagedLoops） → ⑥ `AdjustBuffersAndAccess()` → ⑦ `ExtendAllBuffers()`。输入输出均为 `PrimFunc`，输出包含多 stage 流水线结构与扩展后的 buffer shape。

- **`callnodeMapPos_` 映射（原文 §3.1.6）**：`{"wmma.matrix_a", "cube"}`、`{"wmma.matrix_b", "cube"}`、`{"wmma.accumulator", "cube"}`、`{"shared.l1", "cube"}`、`{"shared.ub", "vec"}` —— 这是判断语句归属核的唯一依据，覆盖矩阵乘相关 intrinsic 与 L1/UB shared memory 区域。

- **`cross_interval=2, num_stages=4` 时序示例（原文）**：

  ```
  迭代:   i=0      i=1       i=2      i=3
  Cube:   write_0  write_1   write_2  write_3
          wait_0   ---       wait_2   ---
          ---      set_1     ---      set_3+last
  Vector: ---      read_0    read_1   read_2
                  wait_1             wait_3
                  set_0              set_2
  ```

- **性能数据**：原文仅以定性方式描述（"核利用率低""最大粒度的 CV overlap""减少同步指令数量"），**未给出具体数字（TFLOPS、延迟降低百分比等）**。

---

【表格解读】

> 原文表格：`cross_interval` 行为参数表

| cross_interval | 同步频率 | SetFlag 时机 | WaitFlag 时机 | 适用场景 |
|----------------|----------|-------------|--------------|---------|
| 1（默认） | 每次迭代 | 每次迭代 | 每次迭代 | 默认，最高并行度 |
| N | 每 N 次迭代 | `i%N==N-1` 或末次 | `i%N==0` | 减少同步开销，多 KV cache |

**逐行解读：**

- **第 1 行（`cross_interval=1`）**：`cross_interval` 是 `T.Pipelined` 的第三个参数，默认为 1。同步频率为"每次迭代"，即每个 stage 迭代都插入一对 `CrossCoreSetFlag` / `CrossCoreWaitFlag`。原文称该模式"最大粒度的 CV overlap，但同步指令开销最大"，适合对同步延迟不敏感、追求最大并行的场景。

- **第 2 行（`cross_interval=N`）**：每隔 N 次迭代同步一次。`SetFlag` 在 `i%N==N-1` 或循环末次迭代时发射（发出数据就绪信号），`WaitFlag` 在 `i%N==0` 时发射（消费已就绪数据）。原文指出此模式"减少同步指令数量，适用于同一份数据被连续多次消费的场景（如多 query 共享同一 KV cache）"，意味着 N 越大同步开销越低，但要求数据被复用 N 次才有收益。

> 文档原文无其他表格（性能对比、配置项等）。

---

【公式解读】

> 文档原文**未给出数学公式（无 LaTeX 数学表达式）**，仅包含变量绑定式 `i_transformed = i_outer * num_stages + i_stage`（伪代码形式）。其含义如下：

```
i_transformed = i_outer * num_stages + i_stage
```

- **`i_outer`**：外层循环变量，循环范围 `N / num_stages`，附 `tl_original_extent` 注解以记录原始 extent；
- **`i_stage`**：stage 内层循环变量，范围 `[0, num_stages)`，随 stage 顺序迭代；
- **`i_transformed`**：通过 `LetStmt` 绑定给原循环体使用的"虚拟"循环变量，将二维（outer × stage）迭代展开为对原范围 `[0, N)` 的均匀分片；
- 作用：将原 for 循环等价展开为 `num_stages` 层并行执行的 stage 子循环，每个 stage 独立处理连续 `num_stages` 切片中的一片，使各 stage 在 buffer 多版本化后不会读到彼此未完成的中间结果。

文档还包含若干 mermaid 流程图（架构图 §2.1、计算流程图 §2.3）与大量伪代码（§3.2.1–§3.2.4），已在前文「技术要点」与「关键机制与数据」中按原结构保留并解读。

---

【关联】

- **下游 pass —— `AscendSyncInsert`**：本 pass 仅完成循环拆分与 buffer 多版本化，文档明确"由后续 `AscendSyncInsert` pass 插入 `set_flag/wait_flag` 同步指令"。

- **下游 pass —— `CombineCV`**：根据 stage 循环上的 `tl_cross_interval` 注解，决定 `CrossCoreSetFlag` / `CrossCoreWaitFlag` 在哪些迭代发射（具体由 `i%N` 条件决定），是 `cross_interval` 参数真正生效的位置。

- **用户 API —— `T.Pipelined(loop_num, num_stages[, cross_interval])`**：本 pass 的唯一触发入口；用户通过 `num_stages` 注解激活本 pass 的处理。详细 API 见内部链接 [`../../T.pipelined.md`](../../T.pipelined.md)。

- **硬件架构 —— Ascend NPU Cube 核 / Vector 核**：`callnodeMapPos_` 中 `wmma.*` 与 `shared.l1` 归属 Cube，`shared.ub` 归属 Vector，反映 A2/A3 系列硬件上 C/V 核通过 workspace 进行数据交互的物理事实。

- **关联算法示例**：文档在 §1.1 调用示例中点名 **SFA、FlashAttention** 等 GEMM+tile 融合算子作为典型业务场景。

---

【使用方法】

- **启用方式（原文）**：在用户脚本中，对含 Cube + Vector 混合操作的 for 循环调用 `T.Pipelined(loop_num, num_stages)` 即可触发本 pass 自动处理；无需手动开关。

- **可选参数（原文 §1.2）**：`cross_interval`，通过 `T.Pipelined` 的第三个参数传入，默认 = 1，仅在跨核流水线下生效：

  ```python
  # 默认：每次迭代同步
  for k in T.Pipelined(num_iters, num_stages=2):
      ...

  # 每 N 次迭代同步一次（减少同步开销）
  for k in T.Pipelined(num_iters, num_stages=4, cross_interval=2):
      ...
  ```

- **生效条件（原文）**：循环体必须同时含 Cube 与 Vector 作用域语句（即 `callnodeMapPos_` 中至少各命中一条），否则 `CrossCoreDetector` 不会标记为跨核循环，pass 不做任何变换即原样返回。

- **API 详细说明**：见内部链接 [`../../T.pipelined.md`](../../T.pipelined.md)。

> 注：原文至 §3.2.4 第 6 步后被截断（"重写后的 Stmt（多 s"），后续可能含 ExtendAllBuffers 返回细节、IR 对照示例与异常处理路径，本文无法覆盖。

## 图文联合解读

- `image-3.png`: **图示解读：**

1) **结构**：双泳道时序图，C 行（蓝色）为 Cube 核执行 `gemm`，V 行（青色）为 Vector 核执行消费/产生；箭头表示通过 workspace buffer（wk1→wk2→wk3）跨核数据传递。

2) **结论**：Cube 与 Vector 异步并行执行，Cube 产出 wk_i+1 时 Vector 消费 wk_i；多版本 workspace buffer 实现 ping-pong 双缓冲，隐藏核间同步延迟。

3) **关联**：直观对应文档"双核 overlap 执行"论点与 `CrossCorePipeline` 拆分 stage、扩展 workspace 维度的实现机制。
- `image-4.png`: 1) 图示：上下两行 C（Cube）/V（Vector）核，中间通过 wk1/wk2/wk3 workspace 串接。C 行 gemm_0_x 产 wk1、V 行消费 wk1 产 wk2、C 行 gemm_1_x 消费 wk2 产 wk3、V 行再消费 wk3；箭头交叉体现 stage[0] 与 stage[1] 双缓冲并行。

2) 论证：通过 workspace 多版本（[0]/[1]）实现 Cube/Vector 跨核 producer-consumer 流水——C 写 wk1[1] 同时 V 读 wk1[0]，验证双核 overlap 可行。

3) 对应文档"扩展 workspace buffer 维度实现多版本 → 生成多 stage 循环"的实现路径。
