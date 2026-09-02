# dequantize_gemm (Unsigned INT4) 算子设计文档

> 仓 `tilelang-ascend` · 路径 `examples_experiment/dequantize_gemm/design_fine_grained.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/examples_experiment/dequantize_gemm/design_fine_grained.md

【定位】
本设计文档描述了在 Ascend 平台上对「UINT8 打包的 Unsigned INT4 权重」做「细粒度反量化 + 矩阵乘法」算子的设计与实现方案，提供 FP16 与 INT8 双计算模式，覆盖数据规格、tiling、内存预算、API 映射、Python 端反量化策略、验证方案与运行命令。

【技术要点】
1. **两种计算模式**：FP16 模式（A:FP16 / B:INT4→FP16 / C:FP16，FP32 累加）vs INT8 模式（A:INT8 / B:INT4→INT8 / C:INT32，INT32 累加）。
2. **INT4 反量化在 Python 端执行**：原文明确指出 "`tir.reinterpret` 在 Ascend 平台存在兼容性问题"，故采用 `torch_unpack_uint4_to_fp16`（及对应 INT8 版本）在 host/torch 侧把 UINT8 拆分为 4-bit 值；NPU 端只跑纯 Cube GEMM。
3. **Developer 编程模式**：FP16 GEMM 与 INT8 GEMM 都选 Developer 模式，理由是"纯 Cube 计算，编译器自动优化"。
4. **Tiling 固定参数**：FP16 (block_M=128, block_N=256, block_K=64)；INT8 (block_M=128, block_N=128, block_K=64)；并满足 `M%block_M==0、N%block_N==0、K%block_K==0、K%2==0（INT4 打包要求）`。
5. **pass_configs 四开关一致**：两种模式均开启 `TL_ASCEND_AUTO_CV_COMBINE / TL_ASCEND_AUTO_SYNC / TL_ASCEND_MEMORY_PLANNING / TL_ASCEND_AUTO_CV_SYNC` 四个开关。
6. **GEMM 调用形式**：累积循环 `T.gemm_v0(A_L1, B_L1, C_L0, init=(k == 0))`，首块初始化累加器，k 内串行累加，最后 `T.copy(C_L0, C[...])` 写回 GM。

【关键机制与数据】
- **数据流（原文 §2.1）**：输入 A 为 (M, K) 的 FP16/INT8 激活；输入 B_packed 为 (N, K/2) 的 UINT8（packed INT4）；反量化后 B_dequant 为 (K, N) 的 FP16/INT8（同时完成转置）；输出 C 为 (M, N) 的 FP16/INT32。
- **内存预算（原文 §5.2）**：FP16 模式 A_L1 16KB + B_L1 32KB + C_L0 128KB(F32 累加) = **176 KB < L1 ≈1MB**；INT8 模式 A_L1 8KB + B_L1 8KB + C_L0 64KB(I32 累加) = **80 KB < L1 容量**。
- **精度容差（原文 §7.2）**：FP16 模式 RTOL=1e-2、ATOL=1e-2；INT8 模式 RTOL=ATOL=0（INT32 精确匹配）。
- **测试矩阵规模（原文 §7.1）**：Level 0 使用 M=N=K=256 基础功能验证；Level 1 使用 512 典型规模验证；Level 2 维度由用户指定。
- **公式等价性**：参考实现 ref_program_* 把 INT4 解包后提升到 FP32/INT32 做 `torch.matmul`，用于 NPU 实现的精度对齐基线（原文 §7.3）。

【表格解读】

**表 1 输入输出规格（§2.1，逐字还原）**

| 阶段 | 数据 | 形状 | 类型 | 说明 |
|------|------|------|------|------|
| **输入 A** | A | (M, K) | FP16/INT8 | 激活矩阵 |
| **输入 B** | B_packed | (N, K/2) | UINT8 | 权重（packed INT4） |
| **反量化后** | B_dequant | (K, N) | FP16/INT8 | 反量化并转置 |
| **输出** | C | (M, N) | FP16/INT32 | 输出矩阵 |

解读：B 在 GM 是 (N, K/2) 的 UINT8 打包（一字节装两个 4-bit），进入 GEMM 之前已扩成 (K, N) 并完成转置，故 GEMM 实际是 `A(M,K) × B_dequant^T(N,K)`；输出形状固定为 (M, N)。

**表 2 两种模式对比（§2.2，逐字还原）**

| 特性 | FP16 模式 | INT8 模式 |
|------|----------|----------|
| **输入 A** | FP16 | INT8 |
| **反量化输出** | FP16 | INT8 |
| **累加类型** | FP32 | INT32 |
| **输出类型** | FP16 | INT32 |
| **计算单元** | Cube (FP16) | Cube (INT8) |
| **精度** | 较高 | 中等 |
| **范围** | FP16 范围 | INT8 范围 (0-15) |

解读：两者核心差异在数据类型链与累加器——FP16 走 FP32 累加保留精度，INT8 走 INT32 累加避免溢出；由于 Unsigned INT4 范围 0–15，反量化输出为非负向量，对 INT8 的正区间无符号表示友好。

**表 3 编程模式选择（§3.1，逐字还原）**

| 模式 | FP16 GEMM | INT8 GEMM |
|------|-----------|-----------|
| **编程模式** | Developer | Developer |
| **理由** | 纯 Cube 计算，编译器自动优化 | 纯 Cube 计算，编译器自动优化 |

解读：因为反量化已搬到 Python 端，NPU 端只剩下"无修饰"的 Cube GEMM，文档判断无需手动调度，选择 Developer 模式让编译器自动优化。

**表 4 内存分配 API（§4.1，逐字还原）**

| 操作 | FP16 模式 | INT8 模式 |
|------|----------|----------|
| A 缓冲区 | `T.alloc_shared((block_M, block_K), "float16")` | `T.alloc_shared((block_M, block_K), "int8")` |
| B 缓冲区 | `T.alloc_shared((block_K, block_N), "float16")` | `T.alloc_shared((block_K, block_N), "int8")` |
| C 缓冲区 | `T.alloc_fragment((block_M, block_N), "float")` | `T.alloc_fragment((block_M, block_N), "int32")` |

解读：A、B 落在 L1 Shared（共享缓冲，可被 Cube 复用），C 落在 L0C Fragment（Cube 累加器专用片段）；注意 FP16 模式下 C 累加器显式分配为 `float`（即 FP32），与"FP32 累加"一致；INT8 模式下为 `int32`。

**表 5 数据搬运与计算 API（§4.2/§4.3，逐字还原）**

| 操作 | API |
|------|-----|
| GM → L1/Shared | `T.copy(src, dst)` |
| L0C → GM | `T.copy(C_L0, C[...])` |

| 操作 | FP16 模式 | INT8 模式 |
|------|----------|----------|
| GEMM | `T.gemm_v0(A_L1, B_L1, C_L0, init=(k == 0))` | `T.gemm_v0(A_L1, B_L1, C_L0, init=(k == 0))` |

解读：`T.gemm_v0` 是接 L1 输入、写到 L0C 累加器的 Cube 指令；`init=(k==0)` 表示仅在 k 循环首步清零，避免每轮重复清空累加器。两种模式 GEMM 调用的形参签名相同，仅 dtype 链路不同。

**表 6 Tiling 参数（§5.1，逐字还原）**

| 参数 | FP16 模式 | INT8 模式 | 说明 |
|------|----------|----------|------|
| block_M | 128 | 128 | M 维度分块 |
| block_N | 256 | 128 | N 维度分块 |
| block_K | 64 | 64 | K 维度分块 |

解读：两种模式 M、K 维度分块一致，N 维度差异（FP16 取 256，INT8 取 128），与对应 L1/Cube 容量与 §5.2 内存预算数值自洽；FP16 模式 B_L1 = 64×256×2=32KB，INT8 模式 B_L1 = 64×128×1=8KB。

**表 7 测试用例（§7.1，逐字还原）**

| Level | M | N | K | 模式 | 说明 |
|-------|---|---|---|------|------|
| 0 | 256 | 256 | 256 | FP16 | 基础功能验证 |
| 1 | 512 | 512 | 512 | FP16 | 典型规模验证 |
| 2 | 用户指定 | 用户指定 | 用户指定 | FP16 | 自定义维度 |
| 0 | 256 | 256 | 256 | INT8 | 基础功能验证 |
| 1 | 512 | 512 | 512 | INT8 | 典型规模验证 |
| 2 | 用户指定 | 用户指定 | 用户指定 | INT8 | 自定义维度 |

解读：每种模式三档 Level，0/1 是固定小/中等规模烟雾与典型验证，2 留给用户自定义（与 §9 的 `--m/--n/--k` 命令行参数呼应）。

**表 8 精度容差（§7.2，逐字还原）**

| 模式 | RTOL | ATOL | 说明 |
|------|------|------|------|
| FP16 | 1e-2 | 1e-2 | FP16 精度容差 |
| INT8 | 0 | 0 | INT32 精确匹配 |

解读：INT8 路径由于只用整数运算（在 FP16/INT8 → INT32 全整数链路且参考实现同样转 INT32 后用 `torch.matmul`），理论上可位级对齐故设为 0 容差；FP16 必须放宽容差。

**表 9 文件清单（§8，逐字还原）**

| 文件 | 说明 |
|------|------|
| `design_fine_grained.md` | 本设计文档 |
| `example_dequant_gemm_fine_grained.py` | 算子实现（FP16 + INT8 双模式） |

解读：实现仅集中在单个 Python 示例脚本中，文档与实现一一对应；同目录下命名相近的 `design_fine_grained.md` 即为本设计文档。

【公式解读】

**主公式（原文 §1.3）**

$$
C[i,j] = \sum_k A[i,k] \times B_{dequant}^T[j,k]
$$

符号说明：
- $C[i,j]$：输出矩阵第 $(i,j)$ 个元素。
- $A[i,k]$：输入激活矩阵 A 在 $(i,k)$ 位置的值。
- $B_{dequant}^T[j,k]$：先把 GM 中 B_packed 做反量化得到 B_dequant（形状 $(K,N)$），再转置后取第 $(j,k)$ 位置（等价于原 B_packed 中第 $(j,k)$ 个 4-bit 值反量化）。
- $\sum_k$：沿 K 维收缩（reduce），得到 M×N 输出。

**Unsigned INT4 反量化公式（原文 §1.3）**

```
u4 = (val >> (pos * 4)) & 0xF
fp16 = float16(u4)    // 范围 0-15
i8   = int8(u4)       // 范围 0-15
```

符号说明：
- `val`：UINT8 打包字节，含两个连续的 4-bit 值。
- `pos`：当前要取的 4-bit 在字节中的位置（0 或 1，由 `j % 2` 决定）。
- `(val >> (pos * 4)) & 0xF`：先把目标 nibble 移到低 4 位，再掩码 0xF，提取出 0–15 的无符号 4-bit 值 `u4`。
- `fp16 = float16(u4)`：FP16 模式下转半精度浮点；`i8 = int8(u4)`：INT8 模式下转 8-bit 整数；两者都是无符号扩展，因此范围严格在 0–15，没有负号位解释问题。

【关联】
原文未提供文末内部链接信息；按文中逻辑关联：
- 上游/数据准备：依赖 packing 阶段把 INT4 权重按 K 维两两打包成 UINT8（形状 (N, K/2)）。
- 下游/对比：本设计文档与同目录 `example_dequant_gemm_fine_grained.py` 实现一一对应（§8 表 9）。
- 工具链：与 TileLang Ascend 的 Developer 模式、`pass_configs`（`TL_ASCEND_AUTO_CV_COMBINE` / `AUTO_SYNC` / `MEMORY_PLANNING` / `AUTO_CV_SYNC`）、`T.copy` / `T.gemm_v0` / `T.alloc_shared` / `T.alloc_fragment` 等原语绑定（§3.2、§4）。
- 与 `tir.reinterpret` 的关系：受其 Ascend 兼容性限制，因而把反量化下沉到 Python 端（§6.1）。

【使用方法】
原文 §9 给出的运行方式：
```bash
# 设置环境
source set_env.sh

# 运行主程序
python examples/dequantize_gemm/example_dequant_gemm_fine_grained.py

# 自定义维度
python examples/dequantize_gemm/example_dequant_gemm_fine_grained.py --m 1024 --n 1024 --k 1024
```
可配置项：模式（FP16/INT8，由脚本内部选择/切换，文档未给单独 CLI 标志）、维度 `--m / --n / --k`（用户自定义，对应测试用例 Level 2，§7.1）；约束见 §5.3：`M%block_M==0、N%block_N==0、K%block_K==0、K%2==0`。
