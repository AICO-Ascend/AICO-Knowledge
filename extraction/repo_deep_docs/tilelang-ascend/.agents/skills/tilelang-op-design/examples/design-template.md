# {算子名称} 算子设计文档

> 仓 `tilelang-ascend` · 路径 `.agents/skills/tilelang-op-design/examples/design-template.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/.agents/skills/tilelang-op-design/examples/design-template.md

# 「tilelang-ascend」算子设计模板深度解读

## 【定位】

这是一份 **TileLang Ascend 算子设计的标准化模板（design-template.md）**，用于在实现具体算子之前，按照"概述 → 编程模式选型 → API 映射 → 数据规格 → Tiling → 调度 → 同步 → 融合算子 → 验证"九大章节的结构化流程，产出可执行、可约束检查、可验证的算子设计文档。它解决的核心问题是：**在 Ascend 后端使用 TileLang 编写算子时，缺乏统一的、约束驱动的设计表达规范**。

---

## 【技术要点】

1. **九大章节的强约束结构**：模板强制按"概述（含数学公式、数据流图）→ 编程模式（Developer/Expert/混合）→ API 映射（含伪代码）→ 数据规格与内存规划 → Tiling 策略 → 循环与调度 → 同步策略 → 融合算子设计 → 验证方案"逐节填写，每节都有失效模式提示（如"⚠️ Host 侧 Buffer 操作约束""尾块必须显式设计"）。

2. **编程模式三选一（Developer / Expert / 混合）**：基于"计算类型、是否含 matmul、是否含归约、是否需要流水线"四个维度选型，并在 §2.3 中显式记录内存分配、计算方式、作用域、同步方式四个维度的选择。

3. **CV 融合算子的 workspace 消除机制**：Developer 模式通过 `T.Kernel(block_num, threads=2, is_npu=True) as (cid)`（**单轴 + threads=2**）消除 `vid`，通过片上 `alloc_shared/alloc_fragment` 直连 Cube↔Vector，由四个 pass 处理中转/同步，从而**无需 workspace 也无需 vid**；Expert/混合模式则需填写 workspace 表 + `workspace_idx`。

4. **三层存储显式规划（GM/L1/L0/L0A/L0B/L0C/UB）**：§4.3 中间缓冲区表要求标注每一块 buffer 的"存储层级"（UB、L1、L0A/L0B/L0C），§4.5 还要求按 dtype 计算字节预算（例：`float16 (128,128)` → 32768 bytes），并与目标平台 UB 容量（如 A2/A3 的 196608 / 192KB）比对。

5. **本项目四条已知硬约束的检查表（§3.5.1）**：不支持三维 Kernel、threads 参数限制（**仅 1 或 2**）、动态循环边界不支持、流水线不支持动态边界；对 GPU 参考实现的差异（Kernel 维度、循环边界动态性、GEMM API `T.gemm_v0` vs `T.gemm`、内存分配层级、threads 数量）必须逐项列出转换方案。

6. **数据重排算子的搬运性能可行性表（§5.5）**：要求按 `结构/dtype 路径 × 代表性最大 case × GM pass 次数 × DMA 数/平均字节 × GM 标量访问 × 地址 div/mod × AIV 并行度` 七列评估，且大张量主路径**禁止逐元素 strided GM 访问**。

---

## 【关键机制与数据】

### 工作原理（模板约束机制）

- **数学公式 → 子表达式 → API 映射的分解链路（§3.1–§3.3）**：先用 `| 步骤 | 数学表达 | 说明 |` 表拆解公式（最小单元示例为 "1 | {子表达式} | {说明}"），再映射到 TileLang API（如 `T.tile.exp(dst, src)`、`T.reduce_sum(buf, out, dim=-1)`），最后落到 `with T.Kernel(block_num, is_npu=True) as (cid, vid):` 的伪代码框架，分四步：分配 buffer → `T.copy` 搬入 → 核心计算 → `T.copy` 搬出。

- **Cube + Vector 融合的数据搬运路径（§4.4 示例）**：
  ```
  GM[A] --T.copy--> L1[a_l1] --T.copy--> L0A[a_l0a]
  GM[B] --T.copy--> L1[b_l1] --T.copy--> L0B[b_l0b]
  L0A + L0B --T.gemm--> L0C[c_l0c] --T.copy--> UB[c_ub]
  UB[c_ub] --后处理--> UB[c_ub] --T.copy--> GM[C]
  ```
  对应纯 Vector 路径为 `GM[A] --T.copy--> UB[a_ub] --计算--> UB[c_ub] --T.copy--> GM[C]`。

- **CV 融合 Developer 模式的消 workspace 链路（§8.2）**：模板明确点出 **"Developer 模式默认消除 workspace/vid：`threads=2` 是消 vid 前提，消 vid 是消 workspace 前提"**，并以"菱形依赖"逻辑串联三个消除层级。

- **尾块/非整除的统一处理契约（§5.4 与 §6.4 双重提示）**：输入、输出 GM 两侧必须使用 `valid_*` extent 的 `BufferRegion`，前端按动态切片裁剪搬运。**禁止**"标量 GM 起点配完整 UB tile"，**禁止** host 侧 padding + crop。

- **L0 门槛测试的协作边界（§9.2）**：设计阶段只输出 L0 用例（规则 shape、block 整除），L1/L2/Boundary 完整分层套件**由 `tilelang-op-test-design` 生成**，明确切分"Stage 1（场景 A）"与"Stage 2（场景 B）"两阶段职责。

- **混合容差精度契约（§9.3）**：逐元素 `|actual-golden| ≤ atol + rtol·|golden|`，整体判定 `matched_ratio ≥ required_matched_ratio` **且** `max_abs_error ≤ max_abs_error_limit`；阈值**仅按 dtype**（与算子类别无关），整型按 0 误差精确匹配。

> 注：原文为模板，所有具体数值（shape、dtype、block size、字节数、UB 容量等）均以 `{占位符}` 表示，未给出具体算子的真实数据。

---

## 【表格解读】

### 表 1：§2.3 模式影响表（原文逐字还原）

| 维度 | 本算子的选择 |
|------|-------------|
| 内存分配 | `{如: T.alloc_ub 显式指定 UB}` |
| 计算方式 | `{如: T.Parallel + 运算符}` |
| 作用域 | `{如: 编译器自动分离 / 显式 T.Scope}` |
| 同步方式 | `{如: 自动同步 / 手动 T.barrier_all}` |

**逐行解读**：四个维度构成 Developer/Expert 模式对算子行为差异的全景。内存分配区分显式层级（`T.alloc_ub`）与编译器自动分配；计算方式区分算子级并行（`T.Parallel`）与指令级；作用域区分编译器自动分离与显式 `T.Scope`；同步方式区分自动同步与显式 `T.barrier_all`。模板用 "如:" 给出 Developer 模式典型示例。

---

### 表 2：§3.1 公式拆解表（原文逐字还原）

| 步骤 | 数学表达 | 说明 |
|------|----------|------|
| 1 | `{子表达式}` | `{说明}` |
| 2 | `{子表达式}` | `{说明}` |
| ... | ... | ... |

**逐行解读**：用于将 §1.3 整体公式按"子表达式 + 说明"粒度分解，是 §3.2 API 映射的输入依赖。`...` 行表示公式步骤数为可变量，最少填一行。

---

### 表 3：§3.2 TileLang API 映射表（原文逐字还原）

| 步骤 | 数学表达 | TileLang API | 参数 | 模式 |
|------|----------|-------------|------|------|
| 1 | `{子表达式}` | `{如: T.tile.exp(dst, src)}` | `{参数说明}` | `{Developer/Expert}` |
| 2 | `{子表达式}` | `{如: T.reduce_sum(buf, out, dim=-1)}` | `{参数说明}` | `{Developer/Expert}` |
| ... | ... | ... | ... | ... |

**逐行解读**：在表 2 基础上增加"API + 参数 + 模式"三列，形成完整的"数学 → API"映射轨迹。模板通过两个典型示例暗示 API 选型：`T.tile.exp` 用于逐元素 `exp`、`T.reduce_sum(buf, out, dim=-1)` 用于按 -1 维归约；每步都需标注所属模式，便于后续 §8 的 CV 融合判定。

---

### 表 4：§3.5.1 本项目已知限制检查表（原文逐字还原）

| 约束 | 本算子是否涉及 | 处理方案 |
|------|---------------|----------|
| 不支持三维 Kernel | `{Yes/No}` | `{block_metadata 方案 / 不涉及}` |
| threads 参数限制（仅 1 或 2） | `{Yes/No}` | `{threads=2 或移除 / 不涉及}` |
| 动态循环边界不支持 | `{Yes/No}` | `{静态边界 + if 条件判断 / 不涉及}` |
| 流水线不支持动态边界 | `{Yes/No}` | `{改用 T.serial / 不涉及}` |

**逐行解读**：四条硬约束对应 Ascend 后端编译器的现实局限。`threads` 仅 1 或 2 是关键硬约束；动态循环边界需用"静态边界 + if 判断"模式伪装；流水线不兼容动态边界时降级为 `T.serial`。每行明确 `Yes/No` 二态决策与对应处理方案。

---

### 表 5：§3.5.2 参考实现差异说明表（原文逐字还原）

| 差异项 | 参考实现（GPU） | 本项目（Ascend） | 转换方案 |
|--------|----------------|-----------------|----------|
| Kernel 维度 | `{三维 T.Kernel(m, n, batch)}` | `{一维 + block_metadata}` | `{参考 examples/grouped_gemm/}` |
| 循环边界 | `{动态 T.Pipelined(batch_sizes[bz])}` | `{静态 + if k < k_iters}` | `{预计算 max_iters}` |
| GEMM API | `{T.gemm}` | `{T.gemm_v0}` | `{查阅 api-compute.md}` |
| 内存分配 | `{T.alloc_shared 自动映射}` | `{T.alloc_L1 显式层级}` | `{Expert 模式}` |
| threads | `{threads=128}` | `{threads=2 或移除}` | `{NPU 限制}` |

**逐行解读**：这是 GPU→Ascend 迁移的差异清单。**Kernel 维度**差异要求把三维折叠为一维 + `block_metadata`（参考 `examples/grouped_gemm/`）；**循环边界**差异要求动态索引转静态边界 + 运行时 `if`；**GEMM API**差异：`T.gemm` → `T.gemm_v0`（api-compute.md 速查表）；**内存分配**差异：GPU 的自动 `alloc_shared` 对应 Ascend 显式 `alloc_L1`，触发 Expert 模式选型；**threads**差异：GPU `threads=128` 降至 Ascend 的 `threads=2 或移除`。

---

### 表 6：§3.5.3 本项目同类实现参考表（原文逐字还原）

| 文件路径 | 相似度 | 关键参考点 |
|----------|--------|-----------|
| `{examples/xxx/example_xxx.py}` | `{高度相似}` | `{Kernel 结构、API 用法、同步方式}` |

**逐行解读**：模板强制列出 `examples/` 中最相似的实现，从三个维度（Kernel 结构、API 用法、同步方式）抽取可复用模式。`相似度` 列用于评估借鉴程度。

---

### 表 7：§4.1 输入张量表（原文逐字还原）

| 参数名 | Shape | dtype | 说明 |
|--------|-------|-------|------|
| `{A}` | `{(M, N)}` | `{float16}` | `{输入矩阵}` |
| ... | ... | ... | ... |

**逐行解读**：模板示例为 `(M, N)` 的 `float16` 矩阵；多输入时通过 `...` 扩展行数。

---

### 表 8：§4.2 输出张量表（原文逐字还原）

| 参数名 | Shape | dtype | 说明 |
|--------|-------|-------|------|
| `{C}` | `{(M, N)}` | `{float16}` | `{输出矩阵}` |
| ... | ... | ... | ... |

**逐行解读**：与 §4.1 结构完全对称，便于评估输入/输出规模一致性。

---

### 表 9：§4.3 中间缓冲区表（原文逐字还原）

| Buffer 名 | Shape | dtype | 存储层级 | 用途 |
|-----------|-------|-------|----------|------|
| `{a_ub}` | `{(block_M, block_N)}` | `{float16}` | `{UB}` | `{输入 tile 缓冲}` |
| `{tmp}` | `{(1, block_N)}` | `{float32}` | `{UB}` | `{归约临时缓冲}` |
| ... | ... | ... | ... | ... |

**逐行解读**：模板示例展示了"块级 tile 缓冲"+"归约临时缓冲"两类典型 buffer——`a_ub` 用于存输入 tile，`tmp` 用 `float32` 存归约中间结果（避免精度损失）。"存储层级"列强制填写，约束 L1/L0/UB 层级映射，是 §4.5 字节预算的输入。

---

### 表 10：§4.5 UB 内存预算表（原文逐字还原）

| Buffer | Shape | dtype | 大小 (Bytes) |
|--------|-------|-------|-------------|
| `{a_ub}` | `{(128, 128)}` | `{float16}` | `{32768}` |
| ... | ... | ... | ... |
| **总计** | | | `{总字节数}` / `{目标平台 UB 容量，例如 196608 (192KB, A2/A3设备)}` |

**逐行解读**：**唯一包含具体数字示例**的表——`(128,128) × float16 = 128×128×2 = 32768 bytes`。总计行形如"X / 196608 (192KB)"，显式列出目标平台的 UB 容量作为判定基准（A2/A3 设备为 196608 bytes）。

---

### 表 11：§4.6 动态轴定义表（原文逐字还原）

| 动态轴 | 声明方式 | 运行时范围 |
|--------|----------|-----------|
| `{K}` | `{T.dyn['K']}` | `{1 ~ 64K}` |

**逐行解读**：动态轴声明方式示例为 `T.dyn['K']`，运行时范围示例为 `1 ~ 64K`。模板要求"无动态轴则写'无'"。

---

### 表 12：§5.5 数据搬运性能可行性表（原文逐字还原）

| 结构/dtype 路径 | 代表性最大 case | GM pass | DMA 数/平均字节 | GM 标量访问 | 地址 div/mod | AIV 并行度 | 结论 |
|-----------------|-----------------|---------|------------------|-------------|--------------|------------|------|
| `{通用 fallback}` | `{shape, dtype}` | `{次数}` | `{数量/字节}` | `{数量}` | `{数量}` | `{core/串行任务}` | `{可行/需重设计}` |

**逐行解读**：七列覆盖重排算子搬运性能的完整评估维度——路径/用例/GM 访问次数/DMA 负载/标量 GM 访问/地址计算开销/AIV 并行度/可行性结论。该表是"数据重排算子必填"项。

---

### 表 13：§6.1 循环结构总结表（原文逐字还原）

| 维度 | 循环类型 | API | 理由 |
|------|----------|-----|------|
| `{M 方向}` | `{block 级并行}` | `{T.Kernel}` | `{每个 block 处理一个 M 分块}` |
| `{K 方向}` | `{迭代}` | `{T.serial(K // block_K)}` | `{K 维分块迭代累加}` |
| `{元素级}` | `{向量化}` | `{T.Parallel(block_M, block_N)}` | `{block 内逐元素并行}` |

**逐行解读**：三个典型并行层级——**M 方向 block 级并行**（`T.Kernel`）、**K 方向迭代**（`T.serial(K // block_K)`）、**元素级向量化**（`T.Parallel(block_M, block_N)`）。模板要求按"维度+类型+API+理由"四列抽象并行设计。

---

### 表 14：§8.2 workspace 表（原文逐字还原，回退写法）

| workspace | Shape | dtype | 用途 |
|-----------|-------|-------|------|
| workspace_1 | `{[block_num, block_M, block_N]}` | `{accum_dtype}` | `{用途}` |
| workspace_2 | `{...}` | `{...}` | `{...}` |

**逐行解读**：仅在 Expert/混合/Developer 复杂场景回退时填写，shape 示例为 `[block_num, block_M, block_N]`，dtype 使用 `accum_dtype`，与 GEMM 累加器精度匹配。`workspace_idx` 行示例为 `[4, 5, 6]`，**根据函数签名参数位置确定**。

---

### 表 15：§7.2 同步点说明表（原文逐字还原）

| 位置 | 同步 API | 理由 |
|------|----------|------|
| `{搬入后}` | `{T.barrier_all()}` | `{等待 DMA 搬运完成}` |
| ... | ... | ... |

**逐行解读**：手动同步模式下的同步点登记。模板示例为 DMA 搬入完成后调 `T.barrier_all()` 等待 DMA 完成。

---

### 表 16：§9.2 L0 门槛测试计划表（原文逐字还原）

| 用例名 | 级别 | Shape | dtype | 说明 |
|--------|------|-------|-------|------|
| `{l0_basic}` | L0 | `{(32, 32)}` | `{float16}` | `{最小功能验证，规则 shape（block 整除）}` |
| `{l0_typical}` | L0 | `{(128, 128)}` | `{float16}` | `{典型规则配置}` |

**逐行解读**：模板给出最小 L0 用例集——`l0_basic (32,32)` 最小功能验证、`l0_typical (128,128)` 典型规模。两者均为规则 shape 且 block 整除，专门用于 Stage 2 快速精度收敛。L1/L2/Boundary **不在此手工枚举**。

---

## 【公式解读】

### 公式 1（§1.3 数学公式）

$$
{数学公式}
$$

**逐字保留原式**：原文为占位符 LaTeX 公式 `${数学公式}$`，未给出具体公式内容。

**符号含义**：因原文为模板，符号含义由后续使用者填入。模板要求：将此公式在 §3.1 按"子表达式"粒度拆解，并在 §3.2 映射到 TileLang API。

---

### 公式 2（§5.2 Block 划分伪代码）

```python
block_M = {值}  # {选择理由}
block_N = {值}  # {选择理由}
block_num = (M // block_M) * (N // block_N)
```

**逐行解释**：
- `block_M = {值}`：M 方向 block tile 大小，`{选择理由}` 处填选择依据（如 UB 容量、对齐约束）。
- `block_N = {值}`：N 方向 block tile 大小，同上。
- `block_num = (M // block_M) * (N // block_N)`：**总 block 数 = 两方向 tile 数之积**，隐含要求 M、N 能被 `block_M`、`block_N` 整除——这是 §6.4 尾块处理契约的前置条件。

---

## 【关联】

### 上游约束文档

- **`../references/ascend-constraints.md §5`**：被 §1.4（Host 侧 Buffer 操作约束）、§5.4（非整除必须显式设计）、§6.4（尾块必须显式设计）三处引用，作为模板中三条 ⚠️ 警告的权威来源。具体约束包括：(a) host 侧只允许共享原 storage 的 view 操作；(b) `reshape` 必须证明零拷贝；(c) `valid_*` extent 的 `BufferRegion` 机制。

### 编程模式权威指南（§8.2 唯一外部链接）

- **`../../tilelang-custom-skill/tilelang-programming-model-guide/references/mode-examples.md#6-cv-融合--推荐写法消除-workspace--vidthreads2`**：作为 §8.2 "Developer 模式推荐写法消除 workspace/vid (threads=2)" 的模板来源，规范了 `T.Kernel(block_num, threads=2, is_npu=True) as (cid)` 的写法、装饰器无 `workspace_idx`、签名无 `workspace_*` 参数、Cube↔Vector 改片上 `alloc_shared/alloc_fragment` 直连、四个 pass 处理中转/同步的具体形态。

### 关联 API 文档

- **`api-compute.md`**：被 §3.5.2 引用，作为 GEMM API `T.gemm` → `T.gemm_v0` 的转换查询表。

### 同类实现参考库

- **`examples/grouped_gemm/`**：被 §3.5.2 引用，作为"三维 Kernel → 一维 + block_metadata"转换的样例。

### 验证套件协作边界

- **`tilelang-op-test-design/references/precision-standard.md`**：被 §9.3 引用，提供混合容差判定、`isnan`/`Inf` mask 严格检查、dtype 级阈值等精度比对定义的完整细节。
- **`tilelang-op-test-design` skill**：§9.2 明确将 L1/L2/Boundary 完整分层套件委派给该 skill，分两阶段协作——Stage 1（场景 A）产出本节 L0 计划，Stage 2（场景 B）在 L0 通过后读真实实现扩展。

### pass_configs 体系（贯穿 §3.4 / §7.3 / §8.5）

| 用途 | PassConfigKey | 涉及章节 |
|------|---------------|----------|
| 自动 CV 分离 | `TL_ASCEND_AUTO_CV_COMBINE` | §8.5 |
| 自动核间同步 | `TL_ASCEND_AUTO_CV_SYNC` | §8.5 |
| 自动同步 | `TL_ASCEND_AUTO_SYNC` | §7.3、§8.5 |
| 内存规划 | `TL_ASCEND_MEMORY_PLANNING` | §8.5 |

这四个 PassConfigKey 在 §7.3 和 §8.5 出现两次，构成 Developer 模式的自动同步四件套，是 §8.2 中"中转/同步交给四个 pass"承诺的具体配置开关。

---

## 【使用方法】

### 启用流程（按模板本身的设计意图还原）

1. **复制模板**：将 `design-template.md` 复制到目标算子目录，按章节顺序填充 `{占位符}`。
2. **从公式到 API**：先在 §1.3 写出数学公式 → §3.1 拆解子表达式 → §3.2 映射 TileLang API → §3.3 落地伪代码。
3. **编程模式决策**：在 §2.1–§2.3 明确选定 Developer/Expert/混合，并根据 §3.5.1–§3.5.3 检查硬约束、列出 GPU 参考实现差异、引用同类实现。
4. **内存规划**：§4.1–§4.6 完整记录输入/输出/中间 buffer/JIT 配置，§4.5 按 dtype 计算字节预算并与目标平台 UB 容量比对（A2/A3 = 196608 bytes）。
5. **Tiling 与调度**：§5 选定 block size（基于对齐 + UB + L0 三约束），§6 设计循环结构（block / 迭代 / 向量化三层），§7 选定同步模式。
6. **CV 融合分支（仅融合算子）**：§8 走 Developer 模式默认路径（消除 workspace/vid），需确认 `threads=2`；仅复杂场景回退到 workspace 表。
7. **验证委派**：§9.2 仅给出 L0 门槛用例，L1/L2/Boundary 由 `tilelang-op-test-design` 在 Stage 2 扩展。

### 配置项（pass_configs 完整枚举）

```python
pass_configs = {
    tilelang.PassConfigKey.TL_ASCEND_AUTO_CV_COMBINE: True / False,   # 自动 CV 分离
    tilelang.PassConfigKey.TL_ASCEND_AUTO_CV_SYNC: True / False,       # 自动核间同步
    tilelang.PassConfigKey.TL_ASCEND_AUTO_SYNC: True / False,          # 自动同步
    tilelang.PassConfigKey.TL_ASCEND_MEMORY_PLANNING: True / False,    # 内存规划
}
```

`@tilelang.jit(out_idx=[{输出索引}], pass_configs={...})` 是 §4.7 给出的 JIT 装饰器骨架。

### 命令

原文无独立 CLI/命令模板，API 调用形式均以 Python 嵌入代码呈现（如 `T.copy`、`T.gemm_v0`、`T.barrier_all()`）。启用方式以"复制模板 + 逐节填占位符"为主，**未涉及独立命令调用**。

### 注

原文未涉及（i）具体算子 `tilelang.compile(...)` 入口命令；（ii）CI/CD 阶段触发条件；（iii）Stage 1/Stage 2 阶段切换的具体自动化手段——这些均在配套的 `tilelang-op-test-design` skill 与 `tilelang-custom-skill` 体系中约定。
