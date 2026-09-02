# 核内 pipeline 示例

> 仓 `tilelang-ascend` · 路径 `.agents/skills/tilelang-pass-analyzer/references/pass-designs/pipeline_planning & inject_pipeline_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/.agents/skills/tilelang-pass-analyzer/references/pass-designs/pipeline_planning & inject_pipeline_design.md

# 深度解读：tilelang-ascend 核内流水线规划与注入设计

---

## 【定位】

本文档描述 TileLang-Ascend 中**核内软件流水线（intra-kernel software pipelining）**的完整设计方案：通过对 `T.Pipelined` 标注的循环自动分析 CopyIn/CopyOut 与 Compute 操作的读写依赖，规划 `stage` 与 `order`，并将其注入生成 prologue/body/epilogue 三段式流水线结构，从而在 NPU 的 Cube/Vector 核内实现数据搬运与计算的 overlap，隐藏访存延迟。

---

## 【技术要点】

1. **双 Pass 协作架构**：核内流水线由 `PipelinePlanning`（规划）与 `InjectSoftwarePipeline`（注入）两个 Pass 协作完成，前者分配 `stage`/`order` 注解，后者将其展开为三段式 IR 并管理 buffer 多版本。

2. **流水线阶段语义**：
   - `PipelineAnnotation.stage`：流水阶段偏移，`0` 表示首个 stage（与 prologue/epilogue 计算相关）
   - `PipelineAnnotation.order`：实际执行顺序（同一 stage 内的排列位置）
   - `PipelineAnnotation.async`：CopyIn 到 shared buffer 时标记为异步操作

3. **三段式流水线结构**（以 `num_stages=3` 为例）：
   - **prologue**（prefetch 阶段）：执行 `num_stages-1` 个 CopyIn（图中 A0、A1、A2），驱动流水线
   - **body**（main body 阶段）：Compute 与 CopyIn 交替（如 B0 A3, B1 A4 ...），实现 overlap
   - **epilogue**（剩余阶段）：仅执行剩余 Compute（B2 B3 B4）

4. **Buffer 多版本管理**：当 buffer 在不同 stage 被写和读且需要并行时，将 buffer 第一维扩展为多个版本：
   - `num_versions 上界 = use_stage - def_stage + 1`
   - 访问重写：`Store: indices.insert(0, floormod(loop_var - min, num_versions))`
   - 优化条件：需写 block 在 order 上先于读 block、stage 不同、区域有重叠

5. **依赖校验机制**（`ValidatePipelineBody`）：
   - `order` 唯一性：每个语句的 `order` 必须唯一
   - 必须满足 `stage(src) <= stage(dst)`，否则报错
   - 同 stage 内必须 `order(src) < order(dst)`

6. **异步操作支持**：通过 `software_pipeline_async_stages = {0}` 标记；对 async 操作生成 `async_wait`/`async_commit`，并在循环边界插入边界检查谓词。

---

## 【关键机制与数据】

### 工作原理与数据流（PipelinePlanning Pass）

1. **入口**：扫描 PrimFunc body 中带 `num_stages` 注解的 for 循环
2. **BufferRegionCollector**：通过 `VisitStmt_/VisitExpr_` 收集每个操作的 `reads[]`/`writes[]`，检测 `is_global_copy_pattern`（GM→L1/UB 的搬运模式）
3. **条件表达式准备**（`prepare_for_condition`）：若某操作的 write buffer 被条件表达式中的 `BufferLoad` 引用，则标记为条件准备操作
4. **Use-Def 分析**：对每个 `copy_stage`，遍历后续操作的 reads，若有 buffer 区域重叠则更新 `last_use_stage`；若发现多写冲突则报错
5. **Stage/Order 分配**：
   - 跳过 `copy_stage`(有活跃 `last_use`) 和 `prepare_for_condition` 操作
   - 主逻辑操作：`stage = num_stages, order = order_idx++`
   - copy_stage（消费位置匹配）：`stage = 0, order = order_idx++`
6. **尾部优化**：若所有 copy 操作在末尾 → 循环移到开头，`stage` 减 1
7. **注解输出**：`software_pipeline_stage` → `stages[]`、`software_pipeline_order` → `orders[]`、`software_pipeline_async_stages` → `{0}`

### 工作原理与数据流（InjectSoftwarePipeline Pass）

1. 递归访问 for 循环，提取 `pipeline_body`、`predicate_condition`、`pipeline_allocs` 及注解
2. `Blockize`：将子语句转为独立 Block
3. `GetBufferAccessInfo()`：分析每个 buffer 的 `def_stage`/`use_stage`
4. `ComputeBufferVersions()`：计算 buffer 需要的版本数，超过 1 时调用 `RewriteAllocBuffer()` 扩展第一维
5. `EmitImpl()` 生成三段：
   - prologue：`[min, min + max_stage)`，unroll=true
   - body：`[min + max_stage, min + extent)`，unroll=false
   - epilogue：`[min + extent, min + extent + max_stage)`，unroll=true
6. 每个 block 内：计算 `skewed_loop_var = new_loop_var - stage`，添加边界检查谓词，重写 buffer 访问，必要时添加 `IfThenElse` 保护与 `async_scope` AttrStmt
7. `PopulateWaitCounts()` 计算 async wait count；`CompletePipelineLoopStatements()` 插入 `async_wait`/`async_commit`

### 业务场景性能分析（原文定性描述）

- **核内串行执行**：搬运和计算完全串行，5 份数据之间虽无数据依赖，但因操作不重叠，核利用率低
- **流水排布（num_stages=3, prefetch 模式）**：prefetch 阶段执行 A0/A1/A2，main body 阶段 B0/A3、B1/A4 等交替，epilogue 阶段执行 B2/B3/B4
- **适用算子**：所有存在"搬运→计算→搬运→计算"重复模式的算子，如分片 GEMM、FlashAttention 的 KV 循环等

> 注：原文未提供量化性能数据（如提升倍数、throughput 数字等）。

---

## 【表格解读】

**原文无传统 markdown 表格**，但包含两个结构化算法 trace，下文以表格形式逐字还原并解读：

### 表 1：Stage/Order 分配算法示例（对应原文 §3.3.1）

| idx | copy | last_use | reads | writes | 分配说明 |
|-----|------|----------|-------|--------|----------|
| 0 | true | 2 | [GM] | [L1_A] | CopyIn A；跳过（copy_stage 有活跃 last_use） |
| 1 | true | 3 | [GM] | [L1_B] | CopyIn B；跳过（copy_stage 有活跃 last_use） |
| 2 | false | - | [L1_A, L1_B] | [L0C] | GEMM；主逻辑：`stage=2, order=0` |
| 3 | false | - | [L0C] | [UB] | CopyOut；主逻辑：`stage=2, order=2` |
| 4 | false | - | [UB] | [GM] | WriteBack；主逻辑：`stage=2, order=4` |

**分配结果**：
- `stages = [0, 0, 2, 0, 2]`（实际偏移后会调整）
- `orders = [1, 3, 0, 2, 4]`

**解读**：本例中 `num_stages=2`。idx=0 的 CopyIn A 因 last_use=2（被 idx=2 的 GEMM 消费），分配 `stage=0, order=1`；idx=1 的 CopyIn B 因 last_use=3（被 idx=3 的 CopyOut 消费），分配 `stage=0, order=3`。主逻辑操作（idx=2/3/4）分配到 `stage=2`，order 按出现顺序递增。`stage=0` 表示 CopyIn 提前 2 个 stage 执行（即 prologue 中 prefetch），从而在 body 阶段实现 CopyIn 与 Compute 的 overlap。

### 表 2：Buffer 多版本分析（对应原文 §3.3.2，文档此处被截断）

| 项目 | 取值 | 说明 |
|------|------|------|
| buffer | "L1_A" | 待分析的目标 buffer |
| def_stage | 0 | stage 0 写入 |
| use_stage | 2 | stage 2 读取（GEMM） |
| num_versions 上界 | 3 | `use - def + 1 = 2 - 0 + 1 = 3` |
| 写 block stage | 0 | CopyIn A |
| 写 block order < 读 block order | Y | 满足顺序先于 |
| stage(写) < stage(读) | Y | 0 < 2 |
| 区域重叠 | Y | 满足 |
| need_multi_version | true | 触发多版本 |
| 扩展 | L1_A[M,N] → L1_A[3,M,N] | 在第一维插入 version 维度 |
| Store 访问重写 | indices.insert(0, floormod(loop_var - min, 3)) | 分配版本号 |

**解读**：因 CopyIn A（stage=0）和 GEMM（stage=2）需要并行（body 阶段 A 的下一次 CopyIn 与 GEMM 的 Compute 同时进行），必须保留旧版本数据用于当前 GEMM 读取，同时为新版本腾出空间写入新数据。通过将 buffer 第一维扩展为 3 个版本（实际使用 2 个即可轮转，上界为 3），并以 `floormod(loop_var - min, 3)` 索引，使每个迭代访问不同的物理 slot，实现"滚动"复用。

---

## 【公式解读】

### 公式 1：Buffer 版本数上界

$$\text{num\_versions}_{\text{上界}} = use\_stage - def\_stage + 1$$

**符号含义**：
- `def_stage`：buffer 被定义（写入）的最早 stage
- `use_stage`：buffer 被使用的最晚 stage
- 含义：要保证从 `def_stage` 写入到 `use_stage` 读取期间旧值不被覆盖，最少需要 `(use - def + 1)` 个版本轮转。

### 公式 2：Buffer 版本数优化判定

多版本仅当同时满足以下三个条件才真正需要：
1. 写 block 的 `order` 先于读 block 的 `order`
2. 写 block 的 `stage` 严格小于读 block 的 `stage`（即 stage 不同）
3. 两者的 buffer 区域有重叠

若全部为 Y，则 `need_multi_version = true`，按上界分配版本；否则可保持单版本以节省内存。

### 公式 3：Skewed Loop Variable（流水线偏移）

$$\text{skewed\_loop\_var} = \text{new\_loop\_var} - stage$$

**符号含义**：
- `new_loop_var`：流水线展开后的新循环变量
- `stage`：该 block 所属的流水阶段偏移
- 作用：将各 stage 的访问"提前"到对应的 prologue/body/epilogue 段中，使 CopyIn 提前 stage 个迭代执行。

### 公式 4：BufferStore 版本索引

$$\text{indices}[0] = \text{floormod}(\text{loop\_var} - \text{min}, \text{num\_versions})$$

**符号含义**：
- `loop_var`：当前循环变量
- `min`：循环下界
- `num_versions`：buffer 版本数
- 作用：在扩展后的 buffer 第一维插入版本号，使同一物理地址在不同迭代中映射到不同 slot，实现版本轮转。

### 公式 5：tvm_access_ptr 索引重写

$$\text{index} = \text{old\_index} + \text{floormod}(\dots) \times \text{offset}$$

**符号含义**：
- `old_index`：原访问索引
- `offset`：单个版本占用元素数
- 作用：低层地址计算同样需加上版本偏移。

### 公式 6：循环分段边界

| 段 | 范围 | unroll |
|----|------|--------|
| prologue | `[min, min + max_stage)` | true |
| body | `[min + max_stage, min + extent)` | false |
| epilogue | `[min + extent, min + extent + max_stage)` | true |

**符号含义**：
- `min`/`extent`：原始 for 循环的下界/范围
- `max_stage`：所有 block 中的最大 stage 值
- prologue 段驱动流水线，epilogue 段排空流水线，两者均 unroll；body 段是流水线稳态循环。

---

## 【关联】

### 上下游 Pass 关系

- **上游**：用户在 Python 层通过 `T.Pipelined(initra_core_proc_num, num_stages=3)` 标注循环，生成带 `num_stages` 注解的 IR
- **下游**：流水线注入完成后，生成的三段式 IR 会被后续 Pass 进一步处理（如 LowerTileOp、LowerOpaqueBlock、PlanAndUpdateBufferAllocation 等），最终生成 NPU 可执行的指令

### 与其他特性的关系

- **`prepare_for_condition`**：与条件表达式（如循环边界判断）耦合，确保条件准备操作不被流水线提前
- **Buffer 多版本**：与 `RewriteAllocBuffer()` Pass 协作，扩展 buffer 第一维后需下游 Pass 处理实际的内存分配
- **Async 机制**：通过 `async_wait`/`async_commit` 与硬件异步拷贝单元配合，依赖 NPU 架构支持的 DMA 异步能力
- **`is_global_copy_pattern` 检测**：用于识别 GM→L1/UB 的搬运模式，这是判断 `copy_stage` 与标记 `async` 的依据

### 内部链接引用

- **../T.pipelined.md**（`../../T.pipelined.md`）：本文档定义了 Pass 端实现，其对应的 Python 前端 API 与循环标注语义在 `T.pipelined.md` 中描述，用户通过 `T.Pipelined(loop_num, num_stages)` 接口触发本文档所述的流水线规划与注入流程。

---

## 【使用方法】

### Python 端调用

```python
# 在循环上标注 num_stages 即可触发流水线规划与注入
for k_i in T.Pipelined(initra_core_proc_num, num_stages=3):
    T.copy(Q[m_i, :], q_l1[k_i * LEN:(k_i+1)*LEN])   # Stage 0: CopyIn
    T.copy(K[k_i * LEN:(k_i+1)*LEN, :], k_l1)         # Stage 0: CopyIn
    T.gemm(q_l1, k_l1, l0c)                            # Stage 1: Compute
T.copy(l0c, C)                                          # Stage 2: CopyOut
```

### Pass 调用链（手动）

```python
def OptimizeForTarget(mod: IRModule, target: Target) -> IRModule:
    mod = tilelang.transform.PipelinePlanning()(mod)            # 核内 pipeline 规划
    mod = tilelang.transform.InjectSoftwarePipeline()(mod)      # 核内流水排布注入
```

### 关键配置项

| 配置 | 含义 | 取值 |
|------|------|------|
| `num_stages` | 流水线深度 | 用户在 `T.Pipelined(loop_num, num_stages=N)` 中指定 |
| `software_pipeline_stage` | 生成的 stage 数组 | 由 PipelinePlanning 自动分配 |
| `software_pipeline_order` | 生成的 order 数组 | 由 PipelinePlanning 自动分配 |
| `software_pipeline_async_stages` | 标记异步 stage | `{0}`（若支持异步拷贝） |

### 触发条件

- 用户在 for 循环上标注 `num_stages` 注解（通过 `T.Pipelined`）
- 循环体内存在可被识别为搬运（GM→shared）与计算的操作
- Pass 校验通过（无多写冲突、依赖关系合法）

> 注：原文未涉及更多关于启用条件、错误处理消息或调试接口的内容。

---

**附注**：原文档在 §3.3.2 "Buffer 多版本管理"末尾被截断（`Lo...`），后续关于 Load 访问重写、完整示例的内容缺失。本解读基于现有原文进行，未对缺失部分进行推测或臆造。

## 图文联合解读

- `image-1.png`: **图1解读：**

1) **画面内容**：横向线性序列，5组交替方块（A0→B0→A1→B1→A2→B2→A3→B3→A4→B4），A代表CopyIn搬运，B代表Compute计算，不同颜色区分各数据切片；箭头严格串联，每一方块必须等前一方块完成才能开始。

2) **论证结论**：5份无数据依赖的切片完全串行执行，搬运与计算零重叠，总耗时≈5×(T_A+T_B)，内存访存延迟完全暴露，核利用率低。

3) **与文档关系**：作为对比基线（"串行执行"图），引出后文num_stages=3流水排布图——通过A、B并行执行来隐藏访存延迟，呼应"显著提升算子吞吐率"的技术目标。
- `image-2.png`: **1) 图示内容**：图分三区呈现5片数据的双操作流水线排布。上排A0~A4为CopyIn（搬运），下排B0~B4为Compute（计算）。"prefetch"区预填A0、A1、A2；"main body"区A3、A4与B0、B1时间重叠；"epilogue"区排空B2、B3、B4。箭头A_i→B_i标注读写依赖。

**2) 技术结论**：num_stages=3的prefetch模式下，搬运与计算在核内时间轴上交错并行；prologue预热buffer、body稳态并行、epilogue排空收尾，三段式结构清晰展示buffer多版本管理。

**3) 与文档论点关系**：印证"搬运→计算"重复模式可被自动排成软件流水线，验证PipelinePlanning+InjectSoftwarePipeline两Pass协同生成的prologue/body/epilogue三段式结构正确，并直观展示了访存延迟被计算掩盖带来的吞吐率提升。
