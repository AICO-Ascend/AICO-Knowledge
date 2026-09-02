# grouped_gemm_bwd 算子设计文档

> 仓 `tilelang-ascend` · 路径 `examples_experiment/grouped_gemm/design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/examples_experiment/grouped_gemm/design.md

# 深度解读：grouped_gemm_bwd 算子设计文档

---

## 【定位】

本文档是 **tilelang-ascend** 仓库中 `examples_experiment/grouped_gemm` 算子的设计说明，专门描述如何基于 TileLang 的 **Developer 模式** 在 Ascend 平台上实现 **grouped GEMM 反向传播中的权重梯度计算**——即对多个独立批次组的矩阵乘法反向传播任务，按组合并为单个 kernel 执行，每个组独立计算 $dB_i = A_i^T \times dO_i$。

---

## 【技术要点】

1. **算子语义**：分组 GEMM 权重梯度的反向传播。输入为按组拼接的激活值 $A$、输出梯度 $B$（文档中以 $dO_i$ 表示）以及每组动态长度 `batch_sizes` / `batch_offsets`；输出为每个组独立的权重梯度 $dB_i \in \mathbb{R}^{M \times N}$。
2. **三维 Kernel 并行**：使用 `T.Kernel(T.ceildiv(M, block_M), T.ceildiv(N, block_N), batch_count, threads=threads) as (bx, by, bz)`——`bx` 划 M 维、`by` 划 N 维、`bz` 划组维。
3. **动态边界保护**：通过 `T.if_then_else(i < batch_sizes[bz], A[...], 0)` 在数据搬入时按组长度屏蔽越界区域（boundary guard），不需要求 M、N、b_i 整除。
4. **K 维流水线**：在每组内沿批次维 (`batch_sizes[bz]` 当作 K 维) 使用 `T.Pipelined(num_stages=2)` 进行分块累加，每次循环完成 `A_shared^T @ B_shared` 并写回 `C_local`。
5. **Developer 模式 + 纯 Cube**：选 Developer 模式由编译器自动完成 `T.alloc_shared → L1`、`T.alloc_fragment → L0C`、同步插入；通过 `tl.disable_warp_specialized=True` 禁用 warp 优化保留基础同步。
6. **Block 选取**：`block_M=64`、`block_N=128`、`block_K=64`；C_local = 64×128×4B = 32KB < L0C 64KB 上限；双 stage 的 L1 占用约 96KB < 1MB 上限。

---

## 【关键机制与数据】

### 工作原理（数据流图，原文 §1.5）
```
输入：A[batch_sum, M], B[batch_sum, N], batch_sizes[batch_count], batch_offsets[batch_count]
  ↓
按组分配（bz 维度）
  ↓
对每个组 bz：按块并行（bx, by 维度）
  ↓ 分块搬入 A_shared[block_K, block_M], B_shared[block_K, block_N]
  ↓ 转置矩阵乘累加：C_local = A_shared^T @ B_shared（流水线）
  ↓ 搬出到 C[bz, bx*block_M, by*block_N]
输出：C[batch_count, M, N]（权重梯度）
```

### 内存搬运路径（原文 §4.4）
```
GM[A] --手动搬运（T.if_then_else）--> L1[A_shared] --T.gemm--> L0C[C_local]
GM[B] --手动搬运（T.if_then_else）--> L1[B_shared] --T.gemm--> L0C[C_local]
L0C[C_local] --T.copy--> GM[C[bz, ...]]
```
A_shared 在 `T.gemm` 中以 `transpose_A=True` 形式使用，等价于 $A_{shared}^T \in \mathbb{R}^{block\_M \times block\_K}$。

### 关键容量数据（原文 §4.5）
| Buffer | 大小 |
|--------|------|
| A_shared (64×64 fp16) | 8 192 Bytes |
| B_shared (64×128 fp16) | 16 384 Bytes |
| C_local (64×128 fp32) | 32 768 Bytes |
| **总计（L1 + L0C）** | **57 344 Bytes** |

### 性能/容量约束（原文 §5.3）
- L1 占用 = 2 × num_stages × (A_shared + B_shared) = 2 × 2 × 24KB = **96KB**，小于 L1 上限（约 1MB）。
- L0C = 32KB，小于 L0C 上限（64KB）。
- `block_N=128`，fp16 尾轴 128 > 16 对齐通过。

> 原文未提供实测性能数据（如 TFLOPS、时延）。

---

## 【表格解读】

### 表 1：模式影响（原文 §2.3）

| 维度 | 本算子的选择 |
|------|-------------|
| 内存分配 | `T.alloc_shared`（编译器映射到 L1）、`T.alloc_fragment`（编译器映射到 L0C） |
| 计算方式 | `T.gemm(A_shared, B_shared, C_local, transpose_A=True)` |
| 作用域 | 无需显式 `T.Scope`，编译器自动识别为 Cube 计算域 |
| 同步方式 | 自动同步（`tl.disable_warp_specialized=True` 禁用 warp 优化，保留基础同步） |

**解读**：四行分别说明 Developer 模式对本算子的关键抽象——内存由编译器从 `alloc_shared / alloc_fragment` 推断到 L1 / L0C；计算仅一行 `T.gemm`，且启用左矩阵转置；作用域被自动识别为 Cube；同步走"自动"路线，并显式禁用 warp 优化以避免对纯 Cube 路径产生副作用。

---

### 表 2：公式拆解（原文 §3.1）

| 步骤 | 数学表达 | 说明 |
|------|----------|------|
| 1 | $A_{tile}^{(k)} = A_{batch_i}[k \cdot block\_K : (k+1) \cdot block\_K, bx \cdot block\_M : (bx+1) \cdot block\_M]$ | 从 GM 搬入 A 的分块到 A_shared |
| 2 | $B_{tile}^{(k)} = B_{batch_i}[k \cdot block\_K : (k+1) \cdot block\_K, by \cdot block\_N : (by+1) \cdot block\_N]$ | 从 GM 搬入 B 的分块到 B_shared |
| 3 | $C_{local} += A_{tile}^{(k)T} \times B_{tile}^{(k)}$ | 转置矩阵乘累加 |
| 4 | $dB_i[bx \cdot block\_M : (bx+1) \cdot block\_M, by \cdot block\_N : (by+1) \cdot block\_N] = C_{local}$ | 搬出结果到 GM |

**解读**：四步完整刻画一次 group 内单 block 的工作流。**步骤 1–2** 表示每次流水线迭代沿 K（= 批次）方向取一个切片，分到 M/N 两个分片上；**步骤 3** 表明 K 维是 reduce 维，左矩阵被转置后参与累加；**步骤 4** 把最终结果以 `[bx, by]` 二维坐标写回 `C[bz, ...]`，**bz** 作为组索引决定写入哪个权重梯度矩阵。

---

### 表 3：TileLang API 映射（原文 §3.2）

| 步骤 | 数学表达 | TileLang API | 参数 | 模式 |
|------|----------|-------------|------|------|
| 1 | 搬入 A 分块 | `T.if_then_else` + 手动赋值 | `A_shared[i, j] = T.if_then_else(i < batch_sizes[bz], A[...], 0)` | Developer |
| 2 | 搬入 B 分块 | `T.if_then_else` + 手动赋值 | `B_shared[i, j] = T.if_then_else(i < batch_sizes[bz], B[...], 0)` | Developer |
| 3 | 转置矩阵乘 | `T.gemm` | `T.gemm(A_shared, B_shared, C_local, transpose_A=True)` | Developer |
| 4 | 搬出结果 | `T.copy` | `T.copy(C_local, C[bz, bx * block_M, by * block_N])` | Developer |

**解读**：把 §3.1 的数学步骤一一落到 TileLang 原语上。前两步刻意用 **`T.if_then_else` + 手动赋值**而非高层拷贝 API，是因为需要按 `batch_sizes[bz]` 过滤行索引——这是处理动态批次的关键；第 3 步 `T.gemm` 承担所有算力；第 4 步 `T.copy` 完成 L0C → GM 的结果回写。

---

### 表 4：API 可行性确认（原文 §3.4）

| API | 来源 | 验证状态 |
|-----|------|---------|
| `T.Kernel(..., batch_count)` | 参考实现 line 177 | ✅ 已验证（三维 kernel） |
| `T.alloc_shared` | [api-kernel-memory.md §2](../tilelang-custom-skill/tilelang-api-best-practices/references/api-kernel-memory.md) | ✅ 已验证 |
| `T.alloc_fragment` | [api-kernel-memory.md §2](../tilelang-custom-skill/tilelang-api-best-practices/references/api-kernel-memory.md) | ✅ 已验证 |
| `T.Pipelined` | [api-schedule-sync.md](../tilelang-custom-skill/tilelang-api-best-practices/references/api-schedule-sync.md) | ✅ 已验证 |
| `T.gemm(..., transpose_A=True)` | [api-compute.md §1](../tilelang-custom-skill/tilelang-api-best-practices/references/api-compute.md) | ✅ 已验证 |
| `T.if_then_else` | TileLang 内置 | ✅ 已验证（条件表达式） |
| `T.copy` | [api-kernel-memory.md §3](../tilelang-custom-skill/tilelang-api-best-practices/references/api-kernel-memory.md) | ✅ 已验证 |
| `T.clear` | 参考实现 line 182 | ✅ 已验证（清零累加器） |

**解读**：8 个 API 全部已验证。表中第三列同时给出了文档外的两个事实来源——参考实现的特定行号（line 177、line 182）以及本仓库内 4 个 tilelang-api-best-practices 参考文档的节号。**这构成了文档对 API 可行性的双重背书：参考实现 + 内部 API 参考手册**。

---

### 表 5：输入张量（原文 §4.1）

| 参数名 | Shape | dtype | 说明 |
|--------|-------|-------|------|
| A | (batch_sum, M) | float16 | 激活值矩阵，所有组的激活值拼接 |
| B | (batch_sum, N) | float16 | 输出梯度矩阵，所有组的输出梯度拼接 |
| batch_sizes | (batch_count) | int32 | 每个组的批次大小 |
| batch_offsets | (batch_count) | int32 | 每个组在总序列中的起始偏移 |

**解读**：A 与 B 都按"按组拼接"形式传入——`batch_sum` 是所有 `b_i` 之和；`batch_sizes` 描述每组实际行数（动态），`batch_offsets` 描述每组在拼接张量里的起点。这与单一 `b` 的 GEMM 反向传播最大区别在于：`b_i` 不是编译期常量。

---

### 表 6：输出张量（原文 §4.2）

| 参数名 | Shape | dtype | 说明 |
|--------|-------|-------|------|
| C | (batch_count, M, N) | float16 | 权重梯度矩阵，每个组独立输出 |

**解读**：与输入 A/B 不同，输出按组展开为三维 `(batch_count, M, N)`——每个组一个权重梯度矩阵。`bz` 直接作为第 0 维下标。

---

### 表 7：中间缓冲区（原文 §4.3）

| Buffer 名 | Shape | dtype | 存储层级 | 用途 |
|-----------|-------|-------|----------|------|
| A_shared | (block_K, block_M) | float16 | L1（shared） | A 的分块输入缓冲（转置后作为左矩阵） |
| B_shared | (block_K, block_N) | float16 | L1（shared） | B 的分块输入缓冲（右矩阵） |
| C_local | (block_M, block_N) | float32 | L0C（fragment） | 累加结果缓冲 |

**解读**：三个 buffer 覆盖完整内存层级。注意 A_shared 的逻辑 shape 是 `(block_K, block_M)`，但**语义上以转置形式 `(block_M, block_K)` 作为左矩阵进入 GEMM**——这与"权重梯度 $dB = A^T dO$"的数学语义对应。

---

### 表 8：UB 内存预算（原文 §4.5）

| Buffer | Shape | dtype | 大小 (Bytes) |
|--------|-------|-------|-------------|
| A_shared | (block_K, block_M) = (64, 64) | float16 | 8192 |
| B_shared | (block_K, block_N) = (64, 128) | float16 | 16384 |
| C_local | (block_M, block_N) = (64, 128) | float32 | 32768 |
| **总计（L1 + L0C）** | | | 57344 Bytes |

**解读**：注意 A_shared + B_shared = 24 KB 全部落在 L1，C_local = 32 KB 落在 L0C，故"总计 57 344 B"实际是 L1 ∪ L0C 之和；文档第 5.3 节的 L1 估算采用 2 × num_stages × 24KB ≈ 96KB，考虑的是**流水线倍增**后的瞬时 L1 占用。

---

### 表 9：动态轴定义（原文 §4.6）

| 动态轴 | 声明方式 | 运行时范围 |
|--------|----------|-----------|
| batch_sizes[bz] | Tensor 参数（运行时传入） | 1 ~ batch_sum（每个组动态） |
| batch_sum | JIT 参数 | 典型值：64, 128, 256 |
| M | JIT 参数 | 512 ~ 16384 |
| N | JIT 参数 | 512 ~ 16384 |

**解读**：四类参数分为**编译期 JIT**（M, N, batch_sum）与**运行时 Tensor**（batch_sizes）两类。M、N 上界 16384 是文档给出的经验范围。

---

### 表 10：循环结构总结（原文 §6.1）

| 维度 | 循环类型 | API | 理由 |
|------|----------|-----|------|
| M 方向（bx） | Block 级并行 | `T.Kernel(..., bx)` | 每个 block 处理一个 M 分块 |
| N 方向（by） | Block 级并行 | `T.Kernel(..., by)` | 每个 block 处理一个 N 分块 |
| 组维度（bz） | Block 级并行 | `T.Kernel(..., bz)` | 每个组独立并行计算 |
| K 维（批次） | 流水线迭代 | `T.Pipelined(T.ceildiv(batch_sizes[bz], block_K))` | 批次维度分块累加 |
| 元素搬入 | 向量化并行 | `T.Parallel(block_K, block_M/block_N)` | 搬入时逐元素赋值（带 boundary guard） |

**解读**：表中前 4 行描述"调度级别"的并行——前三行是**空间并行**（由三维 `T.Kernel` 直接展开），第 4 行是**时间并行**（通过流水线迭代）；最后一行落到线程级（`T.Parallel`），承载 boundary guard 的逐元素写入。

---

## 【公式解读】

### 公式 1：前向传播（原文 §1.3）
$$
O_i = A_i \times B_i, \quad i = 1, 2, ..., G
$$

**符号**：
- $O_i$：第 i 组的前向输出矩阵。
- $A_i \in \mathbb{R}^{b_i \times M}$：第 i 组的激活值。
- $B_i \in \mathbb{R}^{M \times N}$：第 i 组的权重（待反向求导的目标）。
- $G$：组数。

**作用**：定义单个组的矩阵乘法语义，明确 $A_i$ 的行数 $b_i$ 即该组批次大小。

---

### 公式 2：反向传播——权重梯度（原文 §1.3）
$$
\frac{\partial L}{\partial B_i} = A_i^T \times \frac{\partial L}{\partial O_i}
$$

**符号**：
- $\frac{\partial L}{\partial B_i} \in \mathbb{R}^{M \times N}$：对权重 $B_i$ 的梯度（**本算子的输出**）。
- $A_i^T \in \mathbb{R}^{M \times b_i}$：激活值转置。
- $\frac{\partial L}{\partial O_i} \in \mathbb{R}^{b_i \times N}$：上游传回的对输出的梯度（**本算子的输入 B**）。

**作用**：描述权重梯度的链式法则。维度匹配：$M \times b_i$ 与 $b_i \times N$ 相乘得到 $M \times N$。**这就是整个算子的核心数学**——`T.gemm(transpose_A=True)` 正是对这条公式的直接映射。

---

### 公式 3：算法伪代码（原文 §3.3）

```python
with T.Kernel(T.ceildiv(M, block_M), T.ceildiv(N, block_N), batch_count, threads=threads) as (bx, by, bz):
    A_shared = T.alloc_shared([block_K, block_M], dtype)
    B_shared = T.alloc_shared([block_K, block_N], dtype)
    C_local = T.alloc_fragment([block_M, block_N], accum_dtype)
    T.clear(C_local)
    for k in T.Pipelined(T.ceildiv(batch_sizes[bz], block_K), num_stages=num_stages):
        for i, j in T.Parallel(block_K, block_M):
            A_shared[i, j] = T.if_then_else(
                i < batch_sizes[bz],
                A[batch_offsets[bz] + k * block_K + i, bx * block_M + j], 0)
        for i, j in T.Parallel(block_K, block_N):
            B_shared[i, j] = T.if_then_else(
                i < batch_sizes[bz],
                B[batch_offsets[bz] + k * block_K + i, by * block_N + j], 0)
        T.gemm(A_shared, B_shared, C_local, transpose_A=True)
    T.copy(C_local, C[bz, bx * block_M, by * block_N])
```

**逐行解释**：
- `T.Kernel(..., batch_count)`：把 `(bx, by, bz)` 三轴并行分发，bz 对应组数。
- 三行 `T.alloc_*`：声明 L1 / L0C buffer（维度见 §4.3）。
- `T.clear(C_local)`：累加器清零。
- `T.Pipelined(T.ceildiv(batch_sizes[bz], block_K))`：循环次数 = 该组行数 / block_K，向上取整；用流水线调度。
- 两个 `T.Parallel` 循环：用 `T.if_then_else(i < batch_sizes[bz], ..., 0)` 实现 boundary guard；越界行被填 0，不影响 reduce 正确性。
- `T.gemm(..., transpose_A=True)`：核心计算，对应公式 2。
- `T.copy`：把结果从 L0C 写回 GM `[bz, bx*block_M, by*block_N]`。

---

## 【关联】

本文档是 `tilelang-ascend` 仓库对 grouped GEMM 算子的 **Ascend 平台实现设计**。它与以下三类内部资源存在显式引用关系：

### 1. 与 TileLang API 最佳实践参考文档（位于 `tilelang-custom-skill/tilelang-api-best-practices/references/`）

| 引用文档 | 章节 | 本算子用到的 API |
|----------|------|------------------|
| [api-kernel-memory.md](../tilelang-custom-skill/tilelang-api-best-practices/references/api-kernel-memory.md) | §2 | `T.alloc_shared`、`T.alloc_fragment` |
| [api-kernel-memory.md](../tilelang-custom-skill/tilelang-api-best-practices/references/api-kernel-memory.md) | §3 | `T.copy`（L0C → GM 搬出） |
| [api-schedule-sync.md](../tilelang-custom-skill/tilelang-api-best-practices/references/api-schedule-sync.md) | — | `T.Pipelined`（K 维流水线） |
| [api-compute.md](../tilelang-custom-skill/tilelang-api-best-practices/references/api-compute.md) | §1 | `T.gemm(..., transpose_A=True)` |

这些链接是**纵向依赖**：本算子的实现必须遵循这些参考文档中的 API 语义约束（如 buffer 形状、pipeline stage 数量限制等）。§3.4 表中所有 ✅ 都基于此关系成立。

### 2. 与"参考实现"的关系

§3.4 多次出现 "**参考实现 line 177 / line 182**"——表明本设计文档对应一个**外部参考实现**（具体仓库未在文档内指明），本文档的 API 可行性是基于该参考实现的特定行号做验证。`T.Kernel(..., batch_count)` 和 `T.clear` 这两个 API 的验证来源即此。

### 3. 与 TileLang GPU 版本的关系

§2.2 选型理由第 4 条明确指出："**跨平台兼容：与 GPU 版 TileLang 保持一致的编程范式**"。这表明 `tilelang-ascend` 在 grouped GEMM 这类纯 Cube 算子上**有意复用 TileLang 通用语法**，以便算法在 GPU 与 Ascend 之间可移植。

### 4. 与同目录其他实验的关系
路径 `examples_experiment/grouped_gemm/` 暗示该目录下应包含多个 grouped GEMM 变体实验；本文档（design.md）应属于其中之一，承担"权重梯度反向" 这一分支的设计说明职责，可能与对应的前向算子文档互补。

---

## 【使用方法】

文档在 §4.7 给出了**完整 JIT 配置**与**函数签名**：

```python
@tilelang.jit(
    out_idx=[2],
    pass_configs={
        "tl.disable_warp_specialized": True,  # 禁用 warp 优化
    },
)
def grouped_gemm_bwd(
    batch_sum, batch_count, M, N,
    block_M, block_N, block_K,
    num_stages=2, threads=128,
    dtype=T.float16
):
    ...
```

### 关键配置项

| 参数 | 取值 / 默认 | 含义 |
|------|-------------|------|
| `out_idx=[2]` | 固定 | 标记输出张量在参数列表中的位置（按 §4.1–4.2 张量顺序 A/B/C，应为索引 2） |
| `tl.disable_warp_specialized` | `True` | 禁用 warp 优化，保留基础同步 |
| `block_M` | 64 | M 维分块（适配 L0C 容量） |
| `block_N` | 128 | N 维分块（对齐 128 字节） |
| `block_K` | 64 | K 维（批次）分块 |
| `num_stages` | 2 | 流水线级数 |
| `threads` | 128 | 每 block 线程数 |
| `dtype` | `T.float16` | A/B/C 的计算 dtype；`accum_dtype` 为 float32（L0C 累加精度） |

### 调用前置条件（来自 §4.1）
调用方需提前计算好 `batch_sizes`（长度 `batch_count` 的 int32）以及 `batch_offsets`（长度 `batch_count` 的 int32，前缀和），并将所有组的激活/输出梯度沿 batch 维拼接为 `(batch_sum, M)` / `(batch_sum, N)` 的张量。

> **文档截断说明**：原文在 §6.2 循环伪代码处截断（"K 维流水线循" 后未续），因此 §6 之后（§7 及后续章节，如有）**原文未涉及**，本解读不做臆测。
