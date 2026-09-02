# 全聚合-通用矩阵乘法（Allgather Gemm）

> 仓 `triton-distributed-ascend` · 路径 `docs_ascend/zh/tutorial/allgather_gemm.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/triton-distributed-ascend/docs_ascend/zh/tutorial/allgather_gemm.md

# 全聚合-通用矩阵乘法（AllGather Gemm）— 深度解读

## 【定位】
本文档描述如何使用 Triton-distributed 在 Ascend NPU 上编写**融合的 AllGather+GEMM 单 kernel launch 算子**，通过将 AllGather 通信原语与 GEMM 计算合并，消除标准拆分做法中通信阶段与计算阶段之间的中间 DDR 写，让 gather 来的数据保留在片上对称内存（symmetric memory）并直接送入 Cube Engine pipeline，实现 allgather 与 cube 计算的流水线重叠。

---

## 【技术要点】
1. **单 kernel 融合**：AllGather 与 GEMM 合并为 Ascend NPU 上的一次 kernel launch，消除中间 DDR 写。
2. **两阶段流水线 + subblock 划分**：使用 `sub_vec_id()` 把通信与计算任务分配到同一 AICore 上的不同 sub-block——`subblock_idx == 1 and pid < world_size` 负责 Phase 1（远端写入），`subblock_idx == 0 or (subblock_idx == 1 and pid >= world_size)` 负责 Phase 2（本地写入）。
3. **URMA 与 MTE 混合传输**：Phase 1 使用 UDMA（URMA）换取更高跨卡带宽；Phase 2 与 Consumer 阶段使用 MTE（细粒度 tile 级并行 + 双缓冲重叠）。URMA 有两条限制：（1）单核单 pe；（2）整块优先。
4. **双缓冲**：使用 `buffer_num`（原文标注"通常为 2"）跨迭代重叠通信与计算，迭代 `i` 写 buffer slot `(i+1) % buffer_num`，迭代 `i` 读 buffer slot `i % buffer_num`，两阶段间用 `barrier_all()` 同步。
5. **pvalue 参数**：每次通信迭代 gather 的 A tile 行数；更大 pvalue 可摊薄每次 `barrier_all()` 开销，但会增加对称内存 buffer 需求。
6. **对称内存布局**：`[buffer_num, rank_size * BLOCK_M * pvalue, K]`，每个 buffer slot 共 `rank_size * BLOCK_M * pvalue` 行（每个 rank 贡献 `BLOCK_M * pvalue` 行）。
7. **Cube/Vector 分离（CV separation）**：triton mix kernel 在 AscendNPU-IR 中被拆分为 cube func 与 vector func，`libshmem_device.barrier_all()` 作为 mix core type API 在拆分后同时存在于两者中。
8. **swizzle 优化**：使用 `triton_dist.language.extra.ascend.algorithm` 中的 `dist_swizzle2d` 与 `gemm_swizzle2d` 优化内存访问模式。

---

## 【关键机制与数据】

### 工作原理（三阶段流水线）

**Phase 1（Communication，subblock_idx == 1 且 pid < world_size）**：
- 通过 URMA 的 `libshmem_device.putmem` 将本地 A sub-block 写入远端对称内存
- 每个 rank 将自己的 A 分片写入**所有其他 rank** 的对称内存
- URMA 优势在于传输大数据量，故不需要分块

**Phase 2（Communication，subblock_idx == 0 或 subblock_idx == 1 且 pid >= world_size）**：
- 将本地 A sub-block 切分成 `COMM_BLOCK_SIZE_M * COMM_BLOCK_SIZE_K` 小块
- 通过 `tl.store` 写入本端对称内存
- 使用 `dl.symm_at(peer_mem_ptr, rank)` 获取本地对称内存指针

**Phase 3（Computation，barrier_all 之后所有 cube core）**：
- 从本地对称内存读取已 gather 的 A 数据
- 在 Cube Engine 上执行 `tl.dot(a_block, b_block)`，即 `C = A_gathered @ B`
- vector 可同时为下一个 tile 处理通信

### 双缓冲流（原文机制）
- 迭代 `i` 使用 `buffer_id = global_id % buffer_num`
- vector core 写迭代 `i+1` 数据到 buffer slot `(i+1) % buffer_num`
- cube core 同时用 buffer slot `i % buffer_num` 的数据做 GEMM
- `barrier_all()` 保证 buffer 被计算读取前已完全写好
- 对大 K 维实现近满载利用率（原文）

### 性能考量（原文）
- Barrier 开销：每次迭代产生一次 `barrier_all()` 调用
- 更大 pvalue → 减少迭代数与 barrier 次数 → 但增加内存需求

### 尾块处理
```
if global_id_m == num_loops_m - 1:
    actual_block_size_m = M - global_id_m * BLOCK_SIZE_M * pvalue
```

### 关键循环结构
- `num_loops_m = tl.cdiv(M, BLOCK_SIZE_M * pvalue)`
- `num_loops_n = tl.cdiv(N, BLOCK_SIZE_N)`
- `buffer_row_size = BLOCK_SIZE_M * pvalue * rank_size`
- `num_k_blocks = tl.cdiv(K, BLOCK_SIZE_K)`
- `comm_num_m_blocks = tl.cdiv(actual_block_size_m, COMM_BLOCK_SIZE_M)`
- `comm_num_k_blocks = tl.cdiv(K, COMM_BLOCK_SIZE_K)`

> 注：原文提供的 kernel 代码在 `accumulator = tl.zeros(...)` 与 `matmul_offs_am` 之后被截断，GEMM 计算的完整循环未给出。

---

## 【表格解读】
**原文无表格**。

---

## 【公式解读】

### 1. 对称内存布局
$$\text{symmetric memory layout} = [buffer\_num,\; rank\_size \times BLOCK\_M \times pvalue,\; K]$$

- `buffer_num`：双缓冲槽数量（原文：通常为 2）
- `rank_size`：参与通信的 rank 总数
- `BLOCK_M`：每个程序处理的 M 维度数量
- `pvalue`：每次通信迭代 gather 的 A tile 行数
- `K`：矩阵 K 维度
- M 维出现 `rank_size` 因子，是因为 AllGather 要从所有 rank 收集数据

### 2. 每个 buffer slot 中对称内存的总行数
$$\text{buffer\_slot\_rows} = rank\_size \times BLOCK\_M \times pvalue$$

每个 rank 贡献 `BLOCK_M * pvalue` 行。

### 3. GEMM 计算
$$C = A_{\text{gathered}} \times B$$

`A_gathered` 为 AllGather 后所有 rank 的 A 拼接矩阵，`B` 为本地 N×K 矩阵，`C` 为输出矩阵。

### 4. 迭代维度
$$\text{num\_loops\_m} = \lceil M / (BLOCK\_SIZE\_M \times pvalue) \rceil$$
$$\text{num\_loops\_n} = \lceil N / BLOCK\_SIZE\_N \rceil$$
$$\text{num\_k\_blocks} = \lceil K / BLOCK\_SIZE\_K \rceil$$

### 5. 通信维度
$$\text{comm\_num\_m\_blocks} = \lceil actual\_block\_size\_m / COMM\_BLOCK\_SIZE\_M \rceil$$
$$\text{comm\_num\_k\_blocks} = \lceil K / COMM\_BLOCK\_SIZE\_K \rceil$$

### 6. buffer 行尺寸
$$\text{buffer\_row\_size} = BLOCK\_SIZE\_M \times pvalue \times rank\_size$$

### 7. putmem 数据长度（字节）
$$\text{size} = actual\_block\_size\_m \times K \times \text{dtype.primitive\_bitwidth} / 8$$

---

## 【关联】

### 与其他模块的关系
- **`triton_dist.language.extra.ascend.algorithm`**：提供 `dist_swizzle2d` 与 `gemm_swizzle2d` 函数，用于 swizzle 算法优化内存访问模式。
- **`libshmem_device`**：提供 `putmem`（Phase 1 URMA 远端写入）与 `barrier_all()`（同步原语，CV 分离后存在于 cube func 与 vector func 两端）。
- **`dl.symm_at(peer_mem_ptr, rank)`**：用于获取当前 rank 的本地对称内存指针（Phase 2 使用）。

### 上下游/相关特性
- 与文中提及的内部链接项对应的 kernel 参数：`A`（`a_ptr`，本地 M×K 矩阵）、`B`（`b_ptr`，本地 N×K 矩阵）、`C`（`c_ptr`，输出矩阵）、`peer_mem`（`peer_mem_ptr`，共享内存指针）、`rank`、`rank_size`、`buffer_num`、`M`、`N`、`K`、`A.stride(0)`（`stride_am`）。
- URMA 通信原语：Phase 1 跨卡通信，使用 `libshmem_device.putmem`。
- MTE 通信原语：Phase 2 与 Consumer 阶段的本地 tile 级传输，使用 `tl.load` / `tl.store`。
- swizzle 机制：通过 `gemm_swizzle2d(iter_id, data_rows, data_cols, tile_rows, tile_cols, swizzle_offset, swizzle_direction=1)` 确定 GEMM tile 坐标。

---

## 【使用方法】

### 启用方式
使用 `@triton.jit` 装饰的 `kernel_allgather_gemm` 函数，需 `import triton`、`triton.language as tl`、`libshmem_device`、`dl`（含 `symm_at`）。

### Kernel 签名（原文参数列表）
```python
@triton.jit
def kernel_allgather_gemm(
    a_ptr, b_ptr, c_ptr, peer_mem_ptr,
    rank, rank_size, buffer_num,
    M, N, K,
    stride_am, stride_ak, stride_bk, stride_bn, stride_cm, stride_cn,
    pvalue: tl.constexpr,
    BLOCK_SIZE_M: tl.constexpr,
    BLOCK_SIZE_N: tl.constexpr,
    BLOCK_SIZE_K: tl.constexpr,
    COMM_BLOCK_SIZE_M: tl.constexpr,
    COMM_BLOCK_SIZE_K: tl.constexpr,
):
```

### 关键配置项
- `pvalue`：每次通信迭代 gather 的 A tile 行数；更大值 → 更少 `barrier_all()` 调用 → 更大对称内存需求
- `BLOCK_SIZE_M` / `BLOCK_SIZE_N` / `BLOCK_SIZE_K`：GEMM 计算的 tile 尺寸
- `COMM_BLOCK_SIZE_M` / `COMM_BLOCK_SIZE_K`：通信阶段的分块尺寸
- `buffer_num`：双缓冲槽数（原文：通常为 2）
- `dtype = tl.float16`（kernel 内硬编码）
- 通信阶段使用 `dtype.primitive_bitwidth // 8` 计算字节长度

> 原文未涉及具体的 kernel launch / 启动命令（grid 配置、launch 参数等），代码片段在 GEMM 计算循环处被截断。
