# AllGather-GEMM (Allgather Gemm)

> 仓 `triton-distributed-ascend` · 路径 `docs_ascend/en/tutorial/allgather_gemm.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/triton-distributed-ascend/docs_ascend/en/tutorial/allgather_gemm.md

# 一体化深度解读：AllGather-GEMM (Fused Distributed Kernel)

## 【定位】
本文档描述如何在 Ascend NPU 上用 Triton-distributed 将 AllGather 集合通信与 GEMM 矩阵乘法融合到**单个 kernel 启动**中，消除通信→DDR→计算的中间写回，实现 allgather 与 Cube 流水线的 overlap。

## 【技术要点】
1. **融合架构**：AllGather 与 GEMM 融合为一个 kernel，省去 AllGather 先把分片矩阵聚合到 DDR 再由独立 GEMM kernel 读取的标准流程，gathered 数据驻留在片上对称内存并直接送入 Cube Engine。
2. **两/三阶段流水线（按 subblock_idx 划分）**：
   - **Phase 1**（subblock_idx == 1 且 pid < rank_size）：通过 URMA（UDMA）将本地 A 子块写入其他 rank 的对称内存。
   - **Phase 2**（subblock_idx == 0 或 subblock_idx == 1 且 pid >= rank_size）：把本地 A 子块写入本 rank 自身的 peer_mem。
   - **Phase 3**（barrier_all() 之后）：所有 cube core 从本地对称内存读 gathered A，执行 `tl.dot(a_block, b_block)` 计算 `C = A_gathered @ B`。
3. **URMA 双约束**：原文明确列出 (1) single core single pe；(2) full block priority。Phase 1 因此使用 UDMA 以获得更高的跨卡带宽；Phase 2 与 Consumer 阶段则使用 MTE 以支持细粒度 tile 级并行与双缓冲流水线 overlap。
4. **双缓冲 (Double Buffering)**：`buffer_num` 通常为 2；迭代 i 用 `buffer_id = global_id % buffer_num`，vector core 写迭代 i+1 的 buffer slot 与 cube core 读迭代 i 的 slot 并行；`barrier_all()` 保证写完再读。
6. **pvalue 参数**：控制每次通信迭代聚集 A 的 tile 行数；越大越能摊薄每次 `barrier_all()` 的开销，但增加对称内存占用。对称内存布局为 `[buffer_num, rank_size * BLOCK_M * pvalue, K]`。
7. **Cube/Vector 分离（CV separation）**：kernel 是混合核，会在 AscendNPU-IR 中被切分为 cube func 与 vector func；`libshmem_device.barrier_all()` 是 mix core API，切分后同时存在于两个 func 中。

## 【关键机制与数据】
- **工作原理**：用 `sub_vec_id()` 把通信任务分配给同一 AICore 上不同的 sub-block；vector 子核负责 URMA/MTE 搬运，cube 核负责 GEMM。同一 tile iteration 内 Phase 1（跨卡 UDMA）与 Phase 2（本地 MTE）相继写入，再经 `barrier_all()` 同步，最后 Phase 3 触发全 cube 核并行 GEMM；与此同时 vector 核可继续为下一 tile 通信。
- **数据流（原文给的伪代码）**：
  - Phase 1 dst：`peer_mem_ptr + (buffer_id * buffer_row_size + rank * BLOCK_SIZE_M * pvalue) * K`，src：`a_ptr + global_id_m * BLOCK_SIZE_M * pvalue * K`，size=`actual_block_size_m * K * dtype.primitive_bitwidth // 8`，pe=`target_rank`。
  - Phase 2：`tl.store(peer_ptr + remote_offset, local_a_data, mask=mask)`，使用 MTE。
  - Phase 3：从本地对称内存读取 gathered A 后做 `tl.dot(a_block, b_block)`。
- **性能数据**：原文未给出具体 benchmark 数字/数字指标，仅有定性陈述——
  - 原文："URMA communication performs better than MTE"（性能权衡依据）。
  - 原文："achieving pipeline overlap between allgather and cube computation"。
  - 原文："double buffering naturally overlaps communication latency with Cube Engine computation, achieving near full utilization for large K dimensions"。
  - 原文："Using larger pvalue can reduce the number of iterations and barrier calls, but increases memory requirements"。

## 【表格解读】
**原文无表格**。文档中所有参数（如 `BLOCK_SIZE_M`、`BLOCK_SIZE_N`、`BLOCK_SIZE_K`、`COMM_BLOCK_SIZE_M`、`COMM_BLOCK_SIZE_K`、`pvalue`、`buffer_num`、`rank_size`、`M`、`N`、`K` 及 stride 系列）都以 Triton kernel 函数签名参数的形式在代码中罗列，而非以表格呈现。

## 【公式解读】
1. **对称内存布局（伪代码维度表达式，原文逐字保留）**：
   - `Symmetric memory layout: [buffer_num, rank_size * BLOCK_M * pvalue, K]`
   - 含义：`buffer_num` = 双缓冲槽数；`rank_size * BLOCK_M * pvalue` = 每个 buffer slot 的 M 维行数（AllGather 收集所有 rank 的贡献，每 rank 提供 `BLOCK_M * pvalue` 行）；`K` = K 维长度。
   - 派生量（原文）：`Total rows in symmetric memory per buffer slot: rank_size * BLOCK_M * pvalue`。

2. **Phase 1 putmem 的 dst 地址（原文逐字保留，Python 形式）**：
   - `peer_mem_ptr + (buffer_id * buffer_row_size + rank * BLOCK_SIZE_M * pvalue) * K`
   - 符号含义：`peer_mem_ptr` 为目标 rank 的对称内存基址；`buffer_id` 为当前双缓冲槽；`buffer_row_size = BLOCK_SIZE_M * pvalue * rank_size` 表示一个 buffer slot 一行的 stride；`rank * BLOCK_SIZE_M * pvalue` 为把"来自当前 rank"的数据放在目标 rank 的第 `rank` 个 slot 区段。

3. **Phase 1 putmem 的 src（原文逐字保留）**：
   - `a_ptr + global_id_m * BLOCK_SIZE_M * pvalue * K`
   - 含义：本地 A 中对应 `global_id_m` 这一 m-tile 块起始的整段数据（长度为 `actual_block_size_m * K`）。

4. **GEMM 调度中的循环分块数（原文逐字保留）**：
   - `num_loops_m = tl.cdiv(M, BLOCK_SIZE_M * pvalue)`
   - `num_loops_n = tl.cdiv(N, BLOCK_SIZE_N)`
   - `num_k_blocks = tl.cdiv(K, BLOCK_SIZE_K)`
   - `comm_num_m_blocks = tl.cdiv(actual_block_size_m, COMM_BLOCK_SIZE_M)`
   - `comm_num_k_blocks = tl.cdiv(K, COMM_BLOCK_SIZE_K)`
   - 作用：分别控制 GEMM 的 m/n 循环次数、K 维分块数，以及 Phase 2 把本地 A 切成 `COMM_BLOCK_SIZE_M × COMM_BLOCK_SIZE_K` 小块的总数。

5. **swizzle 坐标计算（原文逐字保留）**：
   - `data_row_idx, data_col_idx = gemm_swizzle2d(iter_id, data_rows, data_cols, tile_rows, tile_cols, swizzle_offset, swizzle_direction=1)`
   - 作用：将线性 `iter_id` 映射为二维 GEMM tile 坐标，以优化访存模式（来自 `triton_dist.language.extra.ascend.algorithm`）。

## 【关联】
- **通信原语依赖**：使用 `libshmem_device.putmem(...)` 与 `libshmem_device.barrier_all()`（来自 `triton-distributed` 的 symmetric memory / SHMEM 设备侧 API），对应内部链接 `peer_mem`、`rank`、`rank_size`、`buffer_num`。
- **矩阵形状/步长参数**：`M`、`N`、`K`、`A.stride(0)`（即代码中的 `stride_am`），以及 `a_ptr / b_ptr / c_ptr`（对应内部链接 `A`、`B`、`C`）。文档把 stride 全列于 kernel 签名：`stride_am, stride_ak, stride_bk, stride_bn, stride_cm, stride_cn`。
- **算法/工具**：导入 `triton_dist.language.extra.ascend.algorithm` 中的 `dist_swizzle2d` 与 `gemm_swizzle2d`，说明本文属于该 `extra.ascend` 算法子模块的一部分。
- **CV 分离（Cube/Vector Separation）**：与 AscendNPU-IR 的 mix-kernel 切分流程相关——`barrier_all()` 作为 mix core API 同时存在于 vector func 与 cube func。
- **URMA / UDMA vs MTE 选择**：Phase 1 用 UDMA 取跨卡高带宽，Phase 2 / Consumer 用 MTE 取细粒度 tile 级并行能力，两者在同一 tile iteration 内串行衔接，靠 `barrier_all()` 同步。

## 【使用方法】
原文未给出可直接复制的运行命令/CLI/配置文件，仅给出 **kernel 编写指引**，要点（原文有则列、无则不补）：
- 编写一个 `@triton.jit` 函数 `kernel_allgather_gemm`，签名参数完整列表（原文逐字保留）：
  - 矩阵指针：`a_ptr, b_ptr, c_ptr, peer_mem_ptr`
  - 分布式参数：`rank, rank_size, buffer_num`
  - 矩阵维度：`M, N, K`
  - stride：`stride_am, stride_ak, stride_bk, stride_bn, stride_cm, stride_cn`
  - meta-parameters（constexpr）：`pvalue, BLOCK_SIZE_M, BLOCK_SIZE_N, BLOCK_SIZE_K, COMM_BLOCK_SIZE_M, COMM_BLOCK_SIZE_K`
- 启动时需要的外部依赖（原文 import 部分）：`torch, torch_npu, triton, triton.language as tl`，以及 `libshmem_device`、`triton_dist.language.extra.ascend.algorithm`（`dist_swizzle2d, gemm_swizzle2d`）。
- buffer_num 典型值：`2`（"typically 2"）。
- 关于调优：`pvalue` 越大 → 单次 barrier 开销摊薄越多，但对称内存占用增加（公式 `rank_size * BLOCK_M * pvalue`）。
- 注意：原文提供的代码片段在末尾被截断（以 `remote_ptr = dl.symm_at(peer_mem_pt` 终止），后续 Phase 2 / Phase 3 的完整实现需参考仓库源码。
