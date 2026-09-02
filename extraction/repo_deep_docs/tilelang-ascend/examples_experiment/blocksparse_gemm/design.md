# BlockSparse GEMM 算子设计文档

> 仓 `tilelang-ascend` · 路径 `examples_experiment/blocksparse_gemm/design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/examples_experiment/blocksparse_gemm/design.md

# BlockSparse GEMM 算子设计文档 · 一体化深度解读

---

## 【定位】

本篇文档描述 **tilelang-ascend（面向 Ascend NPU 的 TileLang 项目）中「BlockSparse GEMM（块稀疏矩阵乘法）」算子的完整设计**：如何在 NPU 上以分块矩阵乘法为骨架、结合 BlockMask 跳过零块计算、并在 T.gemm_v0 / Developer 模式 / L1 + L0C 自动映射等本项目特定约束下落地实现，最终产出 `C = A @ B` 的块稀疏高效版本。

---

## 【技术要点】

1. **块稀疏矩阵乘（C = A @ B）**：输出 C 的每个分块 `C[i,j]` 仅在 `BlockMask[i,j,k] == True` 时才对 K 维第 k 个块执行 GEMM 累加；为 False 则跳过该块的乘法以节省算力。
2. **三档分块尺寸 + 显式索引分解**：`block_M / block_N / block_K` 控制 A、B、C 的子块形状；由于 Ascend 端不支持二维 Kernel，使用 `T.Kernel(m_num * n_num, is_npu=True)` 一维调度，并通过 `bx = cid // n_num`, `by = cid % n_num` 手动分解出 (i, j)。
3. **Developer 模式 + 自动内存映射**：`T.alloc_shared` 自动映射到 L1（A_shared、B_shared），`T.alloc_fragment` 自动映射到 L0C（C_local），由 `pass_configs` 启用 `TL_ASCEND_AUTO_SYNC` 与 `TL_ASCEND_MEMORY_PLANNING`。
4. **T.serial 而非 T.Pipelined**：因含 `if BlockMask[bx, by, k]` 条件判断，改用静态计算次数的 `T.serial((K + block_K - 1) // block_K)`，以规避流水线在条件分支下的同步与硬件错误。
5. **BlockMask 用 int8 而非 bool**：Ascend NPU 不支持 bool 数据类型，掩码采用 `int8`（1 表示需计算，0 表示跳过），并在调用处依赖 `BlockMask[:,:,0]=1` 配合 `init=(k==0)` 完成首块累加器初始化。
6. **API 收敛于 T.gemm_v0**：以 `T.gemm_v0(A_shared, B_shared, C_local, init=(k == 0))` 替代参考实现的 `T.gemm` + `T.clear`，并配合 `T.copy` 完成 GM ↔ L1 的搬运、L0C → GM 的输出写回。

---

## 【关键机制与数据】

### 工作原理（原文 §1.4 算法描述）

1. 将矩阵 A、B、C 分块为 `(block_M, block_K)` / `(block_K, block_N)` / `(block_M, block_N)` 的子块；
2. 对每个输出块 `C[i, j]`，遍历 K 维所有块；
3. 通过 `BlockMask[i, j, k]` 判定是否需计算当前块；
4. 若为 True → 执行矩阵乘累加；若为 False → 跳过，节省计算资源。

### 数据流（原文 §1.5 ASCII 图 + §4.4 搬运路径）

```
GM[A]  ──T.copy──▶ L1[A_shared]
GM[B]  ──T.copy──▶ L1[B_shared]
                      │
                      │   if BlockMask[i,j,k] == True
                      ▼
                   L0C[C_local]   ◀── T.gemm_v0（累加）
                      │
                      └──────T.copy──────▶ GM[C]
```

- **GM → L1**：A、B 分块从全局内存搬运到片上 L1 共享缓冲。
- **L1 → L0C**：通过 T.gemm_v0 完成矩阵乘并就地累加到 L0C（C_local）。
- **L0C → GM**：最终将结果从 C_local 写回 GM 中的 C。

### 性能数据

> **原文：未提供任何性能（吞吐、加速比、时延）数字。** 文档仅停留在设计层面，未给出实测或参考 benchmark。

---

## 【表格解读】

> 原文包含多张关键表格，按章节顺序逐字还原并逐行解读。

### 表 1 · 模式影响（原文 §2.3）

| 维度 | 本算子的选择 |
|------|-------------|
| 内存分配 | T.alloc_shared（自动映射到 L1）、T.alloc_fragment（自动映射到 L0C） |
| 计算方式 | T.gemm_v0（标准 GEMM API） |
| 作用域 | 编译器自动分离 Cube 域 |
| 同步方式 | 自动同步（通过 pass_configs 启用） |
| pass_configs | 启用 TL_ASCEND_AUTO_SYNC、TL_ASCEND_MEMORY_PLANNING 等 |

**解读**：表格自上而下定义了 Developer 模式下算子的 5 个工程维度——存储分配（原语映射到 L1/L0C）、计算接口（`T.gemm_v0`）、任务域（Cube 自动隔离）、同步机制（pass_configs 自动插入）和具体的 pass 开关（`TL_ASCEND_AUTO_SYNC`/`TL_ASCEND_MEMORY_PLANNING`），决定了后续 API 选型的基调。

### 表 2 · 公式拆解（原文 §3.1）

| 步骤 | 数学表达 | 说明 |
|------|----------|------|
| 1 | 分配 buffer | A_shared, B_shared, C_local 等片上存储 |
| 2 | 循环 K 维度 | for k in range((K + block_K - 1) // block_K) |
| 3 | 条件判断 | if BlockMask[bx, by, k] == True |
| 4 | 数据搬入 | T.copy(A[bx*block_M, k*block_K], A_shared) |
| 5 | 数据搬入 | T.copy(B[k*block_K, by*block_N], B_shared) |
| 6 | 矩阵乘累加 | T.gemm_v0(A_shared, B_shared, C_local, init=(k == 0)) |
| 7 | 数据搬出 | T.copy(C_local, C[bx*block_M, by*block_N]) |

**解读**：表格把算子拆为 7 个有序步骤——先分配 L1/L0C 缓冲，再对 K 维分块迭代，按掩码条件决定是否真正执行 GM→L1→L0C 的搬运与 GEMM，最后一次性将累加结果写回 GM。第 6 步使用 `init=(k==0)` 实现首块累加器初始化，规避了 `T.clear` 的缺失。

### 表 3 · TileLang API 映射（原文 §3.2）

| 步骤 | 数学表达 | TileLang API | 参数 | 模式 |
|------|----------|-------------|------|------|
| 1 | 分片上存储 | T.alloc_shared((block_M, block_K), dtype) | shape, dtype="float16" | Developer |
| 2 | 分累加器 | T.alloc_fragment((block_M, block_N), accum_dtype) | shape, accum_dtype="float" | Developer |
| 3 | 循环迭代 | T.serial((K + block_K - 1) // block_K) | 静态计算循环次数 | Developer |
| 4 | 条件判断 | if BlockMask[bx, by, k]: | - | Python 控制流 |
| 5 | 数据搬入 | T.copy(A[bx*block_M, k*block_K], A_shared) | src, dst | Developer |
| 6 | 数据搬入 | T.copy(B[k*block_K, by*block_N], B_shared) | src, dst | Developer |
| 7 | 矩阵乘 | T.gemm_v0(A_shared, B_shared, C_local, init=(k == 0)) | A, B, C, init | Developer |
| 8 | 数据搬出 | T.copy(C_local, C[bx*block_M, by*block_N]) | src, dst | Developer |

**解读**：表格把 §3.1 的 7 步进一步细化为 8 条 API 调用。前 2 步完成 buffer 分配（注意 `accum_dtype="float"` 即 fp32，对应 L0C 高精度累加）；第 3 步显式强调用 **静态上界** 计算循环次数，以契合 `T.serial` 的需求；第 4 步用纯 Python `if` 做掩码判断；第 5–6 步 GM→L1 搬运；第 7 步用 `T.gemm_v0` + `init=(k==0)` 替代 `T.gemm` + `T.clear`；第 8 步回写 GM。

### 表 4 · API 可行性确认（原文 §3.4）

| API | 来源 | 状态 | 备注 |
|-----|------|------|------|
| T.Kernel(block_num, is_npu=True) | examples/gemm/example_gemm.py | ✅ 已验证 | 一维 Kernel，手动索引分解 |
| T.alloc_shared | examples/developer_mode/gemm_developer.py | ✅ 已验证 | Developer 模式自动映射到 L1 |
| T.alloc_fragment | examples/developer_mode/gemm_developer.py | ✅ 已验证 | Developer 模式自动映射到 L0C |
| T.serial | examples/developer_mode/gemm_developer.py | ✅ 已验证 | 串行循环（条件判断场景推荐） |
| T.gemm_v0 | examples/gemm/example_gemm.py | ✅ 已验证 | 本项目专用 GEMM API，init参数替代T.clear |
| T.copy | examples/gemm/example_gemm.py | ✅ 已验证 | 数据搬运原语 |
| if BlockMask[bx, by, k] | Python 控制流 | ✅ 已验证 | 条件判断支持，注意索引顺序 |

**解读**：表格逐条标注每个 API 的来源样例与可行性验证状态，确认本算子所用全部原语均已在项目 examples 中跑通；其中 `T.gemm_v0` 与 `T.serial` 是本项目相对 GPU 参考实现的"专用替代项"。

### 表 5 · 本项目已知限制检查（原文 §3.5.1）

| 约束 | 本算子是否涉及 | 处理方案 |
|------|---------------|----------|
| 不支持三维 Kernel | **Yes** | 使用一维 Kernel + 手动索引分解（bx = cid // n_num, by = cid % n_num） |
| threads 参数限制（仅 1 或 2） | **Yes** | 移除 threads 参数（参考实现 threads=128 不支持） |
| 不支持 bool 数据类型 | **Yes** | BlockMask 使用 int8，参考实现使用 bool，需转换 |
| autotuner 参数形式限制 | **Yes** | dtype 参数使用字符串 "float16"，不能用 T.float16 |
| 动态循环边界不支持 | **No** | 循环边界为 (K + block_K - 1) // block_K，静态计算 |
| Pipelined 条件判断场景限制 | **Yes** | 改用 T.serial，避免同步问题和硬件错误 |

**解读**：表格把 6 项项目已知约束逐条对照本算子，给出每项是否命中（Yes/No）与具体规避方案。前 5 项均通过参数/类型层改造解决，仅第 6 项触发循环原语替换（`T.Pipelined` → `T.serial`），是设计上最重要的折衷。

### 表 6 · 参考实现差异说明（原文 §3.5.2）

| 差异项 | 参考实现（GPU） | 本项目（Ascend） | 转换方案 |
|--------|----------------|-----------------|----------|
| Kernel 维度 | `T.Kernel(T.ceildiv(N, block_N), T.ceildiv(M, block_M), threads=thread_num)` (二维) | `T.Kernel(m_num * n_num, is_npu=True)` (一维) | 手动索引分解：bx = cid // n_num, by = cid % n_num |
| threads 参数 | `threads=128` | 不支持 threads > 2 | 移除 threads 参数，依赖编译器自动调度 |
| GEMM API | `T.gemm(A_shared, B_shared, C_local)` | `T.gemm_v0(A_shared, B_shared, C_local, init=...)` | 使用本项目专用 API T.gemm_v0 |
| BlockMask dtype | `T.Tensor(..., "bool")` | `T.Tensor(..., "int8")` | **Ascend不支持bool，必须用int8** |
| dtype参数形式 | `dtype=T.float16` | `dtype="float16"` | **autotuner需要字符串形式** |
| 累加器初始化 | `T.clear(C_local)` | `T.gemm_v0(..., init=(k == 0))` | **T.clear不存在，使用init参数** |
| 循环结构 | `T.Pipelined(..., num_stages)` | `T.serial(...)` | **条件判断场景改用T.serial** |
| Tensor shape计算 | `T.ceildiv(K, block_K)` | `(K + block_K - 1) // block_K` | 避免在Tensor shape中使用T.ceildiv |
| 内存分配 | `T.alloc_shared`, `T.alloc_fragment` (自动映射) | 相同 API，编译器映射到 L1/L0C | Developer 模式保持一致 |
| Swizzle | `T.use_swizzle(panel_size=10, enable=enable_rasteration)` | `T.use_swizzle(cid, M, N, K, block_M, block_N, off=3)`（手动计算） | 参考本项目用法，或暂不启用（性能优化可选） |
| Pipelined | `T.Pipelined(..., num_stages)` | T.serial（条件判断场景） | 本项目支持 T.Pipelined，但条件判断场景受限 |

**解读**：表格列出 11 项 GPU 参考实现到 Ascend 实现的迁移差异。最关键的 3 处用粗体强调：`bool → int8`、`dtype=T.float16 → "float16"`、`T.clear → T.gemm_v0(..., init=...)`；循环从 Pipelined 改为 serial 由"条件判断场景受限"驱动；Swizzle 行说明该项目已提供更精细的手动计算 API，但被列为"性能优化可选"，并非必选。

### 表 7 · 本项目同类实现参考（原文 §3.5.3）

| 文件路径 | 相似度 | 关键参考点 |
|----------|--------|-----------|
| `examples/gemm/example_gemm.py` | 高度相似 | 一维 Kernel + 手动索引分解、T.gemm_v0 用法、T.alloc_L1/L0C（Expert 模式参考） |
| `examples/developer_mode/gemm_developer.py` | **最高相似** | Developer 模式 GEMM、T.alloc_shared/fragment、T.gemm_v0、pass_configs 配置 |
| `examples/gemm/example_gemm_intrinsic.py` | 中等相似 | T.use_swizzle 用法、持久化调度、多 buffer stage |
| `examples/grouped_gemm/example_grouped_gemm_fwd.py` | 中等相似 | 条件数据访问（通过 block_metadata）、静态循环边界 |

**解读**：表格按相似度排序了 4 个可参考的示例：`gemm_developer.py` 为本算子最直接的模板（模式 + API 同源），`example_gemm.py` 提供 Kernel/索引分解范式，`example_gemm_intrinsic.py` 可选地引入 Swizzle 与持久调度优化，`grouped_gemm_fwd.py` 在"条件访问 + 静态循环"上具有方法论参考价值。

### 表 8 · 输入张量（原文 §4.1）

| 参数名 | Shape | dtype | 说明 |
|--------|-------|-------|------|
| A | (M, K) | float16 | 输入矩阵（左矩阵） |
| B | (K, N) | float16 | 输入矩阵（右矩阵） |
| BlockMask | (M // block_M, N // block_N, (K + block_K - 1) // block_K) | int8 | 块稀疏掩码（1 表示需计算，0 表示跳过）**注意：Ascend NPU不支持bool，必须用int8** |

**解读**：输入包含两个 GEMM 矩阵（fp16）与一块三维 BlockMask（int8）。BlockMask 的形状体现"逐 (i, j, k) 块" 三维粒度，且 K 维采用向上取整写法 `(K + block_K - 1) // block_K`，并以加粗注释提醒 int8 是由不支持 bool 而来的硬约束。

### 表 9 · 输出张量（原文 §4.2）

| 参数名 | Shape | dtype | 说明 |
|--------|-------|-------|------|
| C | (M, N) | float16 | 输出矩阵（结果） |

**解读**：单输出张量 C 与输入矩阵同为 fp16；这意味着 L0C 上以 fp32 完成的高精度累加（见下表）最终会降精度写回 fp16。

### 表 10 · 中间缓冲区（原文 §4.3）

| Buffer 名 | Shape | dtype | 存储层级 | 用途 |
|-----------|-------|-------|----------|------|
| A_shared | (block_M, block_K) | float16 | L1（Developer 自动映射） | A 矩阵分块缓冲 |
| B_shared | (block_K, block_N) | float16 | L1（Developer 自动映射） | B 矩阵分块缓冲 |
| C_local | (block_M, block_N) | float32 | L0C（Developer 自动映射） | 矩阵乘累加缓冲（高精度） |

**解读**：表格给出三块片上 buffer 的"层级-精度-用途"组合：A/B 在 L1 上以 fp16 缓冲（用于 GM→L1 暂存），C 在 L0C 上以 **fp32** 累加（满足累加精度要求），三者的存储位置均依赖 Developer 模式自动映射，而非手工指定。

---

## 【公式解读】

> 原文 §1.3 给出一个块稀疏矩阵乘的完整数学式，原文 §3.3 给出一个 Python 计算伪代码。下面逐字保留原式并解释。

### 公式 1 · 块稀疏 GEMM 数学定义（原文 §1.3）

$$
C_{i \times block_M:(i+1) \times block_M,\; j \times block_N:(j+1) \times block_N}
\;=\;
\sum_{k}
\text{BlockMask}[i, j, k]
\times
\bigl(
A_{i \times block_M:(i+1) \times block_M,\; k \times block_K:(k+1) \times block_K}
\times
B_{k \times block_K:(k+1) \times block_K,\; j \times block_N:(j+1) \times block_N}
\bigr)
$$

**符号含义**：

| 符号 | 含义 |
|------|------|
| $C_{(\cdot):(\cdot),\,(\cdot):(\cdot)}$ | 输出矩阵 C 的某个子切片（Python 切片式索引，闭区间右端点取 `(i+1)*block_M` 之前的整行/列） |
| $i, j, k$ | 块级坐标，分别枚举 M/N/K 维分块位置 |
| $\text{BlockMask}[i, j, k]$ | 三维布尔掩码，True=该块参与计算，False=该块被跳过 |
| $A_{i \cdot block_M : (i+1) \cdot block_M,\; k \cdot block_K : (k+1) \cdot block_K}$ | A 矩阵的一个 `(block_M, block_K)` 子块 |
| $B_{k \cdot block_K : (k+1) \cdot block_K,\; j \cdot block_N : (j+1) \cdot block_N}$ | B 矩阵的一个 `(block_K, block_N)` 子块 |
| $block_M, block_N, block_K$ | 沿 M/N/K 维的分块大小 |
| $\sum_k$ | 对所有合法 k 求和（即 K 维全块迭代） |

**作用**：用一条公式统一表达"按块判断 + 块级 GEMM 累加"。`BlockMask` 作为 0/1 开关，等价于把"是否执行子块 GEMM"嵌入到数学求和中；其与 §1.4 算法描述、§1.5 数据流图、§3.3 伪代码中的 `if BlockMask[bx, by, k]` 完全对应。

### 公式 2 · 计算伪代码（原文 §3.3）

```python
@tilelang.jit(out_idx=[-1], pass_configs=pass_configs)
def blocksparse_matmul(M, N, K, block_M, block_N, block_K, num_stages,
                      dtype="float16", accum_dtype="float"):
    m_num = M // block_M
    n_num = N // block_N
    k_num = (K + block_K - 1) // block_K

    @T.prim_func
    def block_sparse_matmul(
        A: T.Tensor((M, K), dtype),
        B: T.Tensor((K, N), dtype),
        BlockMask: T.Tensor((m_num, n_num, k_num), "int8"),
        C: T.Tensor((M, N), dtype),
    ):
        with T.Kernel(m_num * n_num, is_npu=True) as (cid, _):
            bx = cid // n_num   # M 维 block 索引
            by = cid % n_num    # N 维 block 索引

            A_shared = T.alloc_shared((block_M, block_K), dtype)
            B_shared = T.alloc_shared((block_K, block_N), dtype)
            C_local  = T.alloc_fragment((block_M, block_N), accum_dtype)

            for k in T.serial(k_num):
                if BlockMask[bx, by, k]:
                    T.copy(A[bx*block_M, k*block_K], A_shared)
                    T.copy(B[k*block_K, by*block_N], B_shared)
                    T.gemm_v0(A_shared, B_shared, C_local, init=(k == 0))

            T.copy(C_local, C[bx*block_M, by*block_N])

    return block_sparse_matmul
```

**逐段解释**：

| 行/段 | 作用 |
|-------|------|
| `@tilelang.jit(out_idx=[-1], pass_configs=pass_configs)` | JIT 装饰器；`-1` 表示 C 作为输出张量，`pass_configs` 启用自动同步与内存规划 |
| 函数签名 `blocksparse_matmul(M, N, K, block_M, block_N, block_K, num_stages, dtype="float16", accum_dtype="float")` | 暴露维度、分块大小、阶段数、计算/累加精度等可调参数 |
| `m_num = M // block_M; n_num = N // block_N; k_num = (K + block_K - 1) // block_K` | 预计算各维块数；K 维用向上取整以兜底非整除 |
| `BlockMask: T.Tensor((m_num, n_num, k_num), "int8")` | 三维掩码为 int8，呼应 §3.5.1 "不支持 bool" 约束 |
| `with T.Kernel(m_num * n_num, is_npu=True) as (cid, _):` | 一维 NPU Kernel，总块数 `m_num * n_num` |
| `bx = cid // n_num; by = cid % n_num` | 把一维 cid 还原为二维 (M, N) 块坐标 |
| `A_shared = T.alloc_shared((block_M, block_K), dtype)` 等 | 分配 L1 共享缓冲（fp16） |
| `C_local = T.alloc_fragment((block_M, block_N), accum_dtype)` | 分配 L0C 累加缓冲（fp32） |
| `for k in T.serial(k_num):` | 静态循环 K 维块，使用 `T.serial` 而非 `T.Pipelined`，绕开条件分支下的流水线限制 |
| `if BlockMask[bx, by, k]:` | 块稀疏的核心——按掩码决定是否进入分支 |
| `T.copy(A[bx*block_M, k*block_K], A_shared)` / `T.copy(B[k*block_K, by*block_N], B_shared)` | GM → L1 搬运 A、B 子块 |
| `T.gemm_v0(A_shared, B_shared, C_local, init=(k == 0))` | 本项目专用 GEMM 原语；`init=(k==0)` 承担首块累加器初始化（依赖"BlockMask[:,:,0]=1"的前提） |
| `T.copy(C_local, C[bx*block_M, by*block_N])` | L0C → GM 写回输出 |

---

## 【关联】

文档本身未提供内部链接（文末 `(无)`），但通过引用文件名展示了以下上下游关系：

- **本算子所选模式的根模板**：`examples/developer_mode/gemm_developer.py`（Developer 模式 GEMM、`T.alloc_shared`/`T.alloc_fragment`、`T.gemm_v0`、`pass_configs` 配置）——这是本算子的最高相似度参考。
- **API 范式来源**：`examples/gemm/example_gemm.py`（一维 Kernel、手动索引分解、`T.gemm_v0`、`T.copy`），以及 `examples/gemm/example_gemm_intrinsic.py`（`T.use_swizzle` 用法、持久化调度、多 buffer stage，本算子可选优化）。
- **方法论类比**：`examples/grouped_gemm/example_grouped_gemm_fwd.py`——通过 `block_metadata` 做条件数据访问、使用静态循环边界，与本算子的"BlockMask + T.serial + 静态循环"模式方法论相通。
- **外部 GPU 参考实现**：文档显式区分了"GPU 版 TileLang（外部参考）"与"本项目 Ascend 版"——前者使用二维 Kernel、`threads=128`、`T.gemm`、`bool` 掩码、`T.clear`、`T.Pipelined`、`T.ceildiv` 等；本项目在 §3.5.2 表格中给出了逐项转换方案。
- **后端 Pass 配置**：`pass_configs` 启用 `TL_ASCEND_AUTO_SYNC`、`TL_ASCEND_MEMORY_PLANNING`，这是 Developer 模式实现"自动同步 + 自动内存规划"的开关，与 `TL_ASCEND_*` 系列优化 Pass 同属一个体系（虽文档未展开 Pass 实现细节）。

---

## 【使用方法】

> **原文未提供**「调用示例 / 完整 Python 入口 / 运行命令 / autotuner 启动方式 / pass_configs 完整定义」等内容。

文档仅在以下位置涉及"如何使用"的间接信息：

- §3.3 给出了**算子函数的完整伪代码**（含 `@tilelang.jit(out_idx=[-1], pass_configs=pass_configs)` 装饰器、参数列表 `M, N, K, block_M, block_N, block_K, num_stages, dtype="float16", accum_dtype="float"`，以及内层 `T.prim_func`），可作为启用参考；
- §3.5.1 提示 `dtype` 参数必须传**字符串 `"float16"`** 而非 `T.float16`，否则 autotuner 无法识别；
- §3.5.2 提示 `pass_configs` 需启用 `TL_ASCEND_AUTO_SYNC`、`TL_ASCEND_MEMORY_PLANNING`，但未列出 `pass_configs` 的具体定义代码；
- §4.1–§4.3 给出调用所需的 4 个张量（A、B、BlockMask、C）的 shape/dtype，可作为输入构造依据。

**结论**：文档在"算子内部如何实现"层面完整，但"外部如何调用 / 构建输入 / 触发编译 / 运行"等用户级入口内容**原文未涉及**。
