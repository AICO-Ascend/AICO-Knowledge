# conv2d (im2col + GEMM) 算子设计文档

> 仓 `tilelang-ascend` · 路径 `examples_experiment/convolution/convolution_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/examples_experiment/convolution/convolution_design.md

# 一体化深度解读：conv2d (im2col + GEMM) 算子设计文档

---

## 【定位】

这篇文档定义并论证了 **conv2d 算子**（基于 im2col + GEMM 分解策略）在华为 Ascend NPU 上用 TileLang 的 **Developer 自动化模式** 进行实现与 Tiling 的完整技术方案——目标是避开手写复杂的 DMA/Pipeline/Cube-Vector 切分，转而交由编译器自动映射 Cube 计算单元、MTE 数据搬运、UB/L0C 内存层级以及同步原语，从而在 Ascend 上获得与标准 GEMM 等价的 2D 卷积性能。

---

## 【技术要点】

1. **算子拆分策略（im2col + GEMM）**：4D 卷积 `(B,C,H,W) ↦ (B,OC,HO,WO)` 被拆为两步——在 host 侧用 PyTorch 完成 **im2col 展平**将输入变换为 `(C·KH·KW, B·HO·WO)`；在 NPU 侧用 TileLang 完成 **GEMM** `C(OC, B·HO·WO) = Kernel_flat(OC, C·KH·KW) @ Input_flat(C·KH·KW, B·HO·WO)`，结果再 `view + permute` 恢复为 4D 卷积输出形状。

2. **动态 Padding 处理（非整除对齐）**：当 `M=OC, N=B·HO·WO, K=C·KH·KW` 非 block 大小 **128** 的整数倍时，在 host 侧 zero-pad 到下一个 128 的倍数；GEMM 计算完成后再 `裁剪 [:M, :N]` 回原始尺寸——零填充区域乘积为零贡献，不影响正确性。

3. **TileLang Developer 模式（全自动）**：选定 Developer 模式而非 Pipelined/MANUAL；具体由 `T.gemm_v0` 原语驱动 Cube 计算、`T.alloc_shared`/`T.alloc_fragment` 让编译器自动将缓冲区映射到 L1/UB 或 L0A/L0B/L0C，作用域（Cube/Vector）与同步（`TL_ASCEND_AUTO_SYNC`）均由 pass 全权处理。

4. **Block 三向分块 = 128**：固定 `block_M = block_N = block_K = 128`；其中 `block_M=block_N=128` 是为了让 `C_L0` 累积 128·128·4B = 64KB **恰好填满 L0C**（A2/A3 设备 L0C 容量），`block_K=128` 是为在 L1 带宽与 L0A/L0B 容量之间折中。

5. **片上内存预算受设备容量硬约束**：UB 总占用（A_L1 + B_L1 = 32KB + 32KB = **64KB**），仅占 A2/A3 UB 容量 192KB 的 1/3；L0C = 64KB 被 `C_L0` 整块占用——若 block 尺寸扩到 256 将导致 L0C 溢出，因此搜索空间被硬限为 `block ≤ 128`。

6. **JIT 编译开关**：通过 `@tilelang.jit(out_idx=[-1], pass_configs=…)` 开启三项关键 Pass——`TL_ASCEND_AUTO_CV_COMBINE`（自动 Cube/Vector 分离）、`TL_ASCEND_AUTO_SYNC`（自动插入同步）、`TL_ASCEND_MEMORY_PLANNING`（自动内存规划）。

---

## 【关键机制与数据】

**工作原理（数据流，文档 §1.5 已绘出）**：

- **入口侧**：`Input (B,C,H,W)` 经 host 端 im2col → `Input_flat (C·KH·KW, B·HO·WO)`；`Kernel (OC,C,KH,KW)` 经 `view` → `Kernel_flat (OC, C·KH·KW)`。
- **NPU 侧搬运路径**（原文 §4.4）：`GM[Kernel] ──T.copy──► L1/UB[A_L1]`、`GM[Input] ──T.copy──► L1/UB[B_L1]`，随后 `T.gemm_v0(A_L1, B_L1, C_L0)` 在 L0C 上做 K 维累加，K 循环结束后 `T.copy(C_L0, C[block])` 写回 GM。
- **动态 Padding 在 GM 侧完成**：在 GM 上先 pad 再送入 GEMM；GEMM 完成后裁剪。
- **Cube 单元归属**：原文（§5.1）明确 "核心为矩阵乘法 `T.gemm_v0`，该原语在 Cube 计算单元上执行"，im2col 在 host CPU/NPU 上用 PyTorch 完成，不占用 TileLang 计算资源——这是为何该算子被归为「纯 Cube」计算类型。

**数据规模示例（原文给出的明示数值）**：

- Block 三向尺寸全为 128（统一值）。
- A2/A3 **UB 容量 192KB**（原文 §4.5 注释），本算子 UB 占用 64KB = 1/3。
- A2/A3 **L0C 容量 64KB**（原文 §4.6 注释），本算子 L0C 占用 64KB = 完全填满。

**性能数据**：原文未给出任何 wall-clock、TFLOPS、对比基准等性能数字，仅做了设备容量预算分析；故性能结论此节留空。

---

## 【表格解读】

> **说明**：以下逐字还原原文中所有 markdown 表格（共计 12 张），随后逐表逐行解读其含义与对设计的作用。

### 表 1：编程模式选型理由（§2.2）

| 算子特征 | 分析 | 结论 |
|---------|------|------|
| 计算类型 | 核心为 GEMM（矩阵乘法），T.gemm_v0 原语 | 编译器可自动管理 |
| 是否含 matmul | 是，GEMM 是主要计算 | Developer 模式对 GEMM 支持完善 |
| 是否含归约 | 否（K 维的累加由 GEMM 内部完成） | 无需手动 reduce |
| 是否需要流水线 | 否 | 标准 GEMM 无需 Pipelined |
| 内存分配 | GEMM 的 shared/fragment 层级遵循固定模式 | T.alloc_shared / T.alloc_fragment 编译器自动映射 |

**解读**：这是选型决策的核心证据矩阵。每一行的「分析」判定该特征是否需要人工干预，「结论」给出对应自动化路径——五条全部落入编译器自动管理范畴，因此结论锁死为 Developer 模式。

### 表 2：模式影响（§2.3）

| 维度 | 本算子的选择 |
|------|-------------|
| 内存分配 | `T.alloc_shared` 编译器自动判断 L1 或 UB；`T.alloc_fragment` 编译器自动判断 L0A/L0B/L0C |
| 计算方式 | `T.gemm_v0(A, B, C, init=...)` 块级矩阵乘 |
| 作用域 | 编译器自动分离 Cube / Vector 作用域 |
| 同步方式 | pass_configs 开启 `TL_ASCEND_AUTO_SYNC` 自动插入同步 |

**解读**：把 Developer 模式带来的"自动化收益"逐维落到本算子的实现细节——尤其是「作用域自动分离」直接呼应"纯 Cube 计算"的判定（§5.1）。

### 表 3：公式拆解（§3.1）

| 步骤 | 数学表达 | 说明 |
|------|----------|------|
| 1 | `Input_flat = im2col(Input)` | 将 (B,C,H,W)→(C·KH·KW, B·HO·WO) |
| 2 | `Kernel_flat = Kernel.view(OC, -1)` | 将 (OC,C,KH,KW)→(OC, C·KH·KW) |
| 3 | `Output = Kernel_flat @ Input_flat` | 矩阵乘法 C(M,N) = A(M,K) × B(K,N) |
| 4 | `Output = Output.view(OC,B,HO,WO).permute(1,0,2,3)` | 恢复 4D 卷积输出形状 |

**解读**：这是 im2col+GEMM 拆解的形式化逐行表达，对应文档前言（§1.4）三步分解策略；步骤 4 的 `permute(1,0,2,3)` 是为把 Channel 维从第 1 维移回到第 2 维（PyTorch 的 NCHW 约定）。

### 表 4：TileLang API 映射（GEMM 核心）（§3.2）

| 步骤 | 数学表达 | TileLang API | 参数 | 模式 |
|------|----------|-------------|------|------|
| 数据搬入 A | A[block] → L1 | `T.copy(A[offset], A_L1)` | implicitly: GM→L1 | Developer |
| 数据搬入 B | B[block] → L1 | `T.copy(B[offset], B_L1)` | implicitly: GM→L1 | Developer |
| 矩阵乘 | C_L0 += A_L1 × B_L1 | `T.gemm_v0(A_L1, B_L1, C_L0, init=(k==0))` | init 标识首次迭代清零 | Developer |
| 数据搬出 | C_L0 → C[block] | `T.copy(C_L0, C[offset])` | implicitly: L0C→GM | Developer |

**解读**：将数学动作精确翻译为 TileLang API，并指出每次 `T.copy` 的隐含方向；`init=(k==0)` 是 K 维逐块累加模式中用于首次清零累加器的关键开关，避免在第一次迭代前还需额外 zero-fill 缓冲。

### 表 5：API 可行性确认（§3.4）

| API | 来源 | 状态 |
|-----|------|------|
| `T.alloc_shared` | api-kernel-memory.md §2.1 | ✅ 已验证 |
| `T.alloc_fragment` | api-kernel-memory.md §2.2 | ✅ 已验证 |
| `T.copy` | api-kernel-memory.md §3 | ✅ 已验证 |
| `T.gemm_v0` | api-compute.md §1 | ✅ 已验证，examples/developer_mode/gemm_developer.py |
| `T.ceildiv` | TileLang DSL 内置 | ✅ 已验证 |
| `T.serial` | api-schedule-sync.md §1 | ✅ 已验证 |
| `T.Kernel(..., is_npu=True)` | api-kernel-memory.md §1.3 | ✅ 已验证 |
| `@tilelang.jit(out_idx=[-1], ...)` | api-kernel-memory.md §1.4 | ✅ 已验证 |

**解读**：列出本实现依赖的全部 API 及其文档出处，全部"已验证"。`out_idx=[-1]` 标记最后一个张量为输出，是 L1/UB 内存规划的前提条件之一。

### 表 6：本项目已知限制检查（§3.5.1）

| 约束 | 本算子是否涉及 | 处理方案 |
|------|---------------|----------|
| 不支持三维 Kernel | **No** | 使用一维 T.Kernel(m_num * n_num)，通过 bx/by 线性化 2D block grid |
| threads 参数限制（仅 1 或 2） | **No** | 不使用 threads 参数，使用默认值 |
| 动态循环边界不支持 | **No** | block_M/N/K 均为编译期常量(128)，loop_k 由 T.ceildiv 处理 |
| 流水线不支持动态边界 | **No** | 未使用 T.Pipelined |

**解读**：这是「避雷表」——逐条说明本文实现如何主动规避已知的 TileLang/Ascend 后端限制；用一维 Kernel + bx/by 线性化代替 2D Kernel 是规避"不支持三维 Kernel"的典型做法。

### 表 7：本项目同类实现参考（§3.5.3）

| 文件路径 | 相似度 | 关键参考点 |
|----------|--------|-----------|
| `examples/developer_mode/gemm_developer.py` | 高度相似 | GEMM Kernel 结构、T.gemm_v0 用法、T.serial K 循环 |
| `examples/convolution/example_convolution_autotune.py` | 同一算子 | autotune 变体，block 搜索空间 [64,128] |
| `examples/developer_mode/matmul_add_developer.py` | 相似 | T.copy + T.gemm_v0 组合模式 |

**解读**：明确指出三个可直接对照的参考实现，第三个（autotune 变体）透露了上游已有的 block 搜索空间上限 `[64,128]`，与本文 block ≤ 128 的限制一致。

### 表 8：输入张量（§4.1）

| 参数名 | Shape | dtype | 说明 |
|--------|-------|-------|------|
| A (kernel) | `(M, K)` = `(OC, C·KH·KW)` | float16 | 卷积核展平矩阵 |
| B (input) | `(K, N)` = `(C·KH·KW, B·HO·WO)` | float16 | im2col 展平特征图 |

**解读**：A、B 分别对应 Kernel_flat 和 Input_flat，dtype 为 float16（与下文 A_L1/B_L1 一致）。

### 表 9：输出张量（§4.2）

| 参数名 | Shape | dtype | 说明 |
|--------|-------|-------|------|
| C (output) | `(M, N)` = `(OC, B·HO·WO)` | float16 | GEMM 结果，后续 reshape 为 (B,OC,HO,WO) |

**解读**：C 仍为 float16——意味着 L0C 上以 float32 累加（精度更高），写回 GM 时截回 float16。

### 表 10：中间缓冲区（片上）（§4.3）

| Buffer 名 | Shape | dtype | 存储层级 | 大小 (Bytes) | 用途 |
|-----------|-------|-------|----------|-------------|------|
| A_L1 | `(128, 128)` | float16 | L1/UB (自动) | 32768 | 矩阵 A 的 K 方向分块缓冲 |
| B_L1 | `(128, 128)` | float16 | L1/UB (自动) | 32768 | 矩阵 B 的 K 方向分块缓冲 |
| C_L0 | `(128, 128)` | float32 | L0C (自动) | 65536 | 矩阵乘累加结果（accum 精度） |

**解读**：三个缓冲区占据三种不同片上存储层级——A_L1/B_L1 在 L1/UB（自动二选一），C_L0 在 L0C；dC_L0 用 float32 是 Ascend 累加器典型配置，避免 K 维求和溢出/丢精度。

### 表 11：UB 内存预算（§4.5）

| Buffer | Shape | dtype | 大小 (Bytes) |
|--------|-------|-------|-------------|
| A_L1 | `(128, 128)` | float16 | 32,768 |
| B_L1 | `(128, 128)` | float16 | 32,768 |
| **A + B 总计** | | | **65,536 (64 KB)** |

**解读**：原文紧接此表给出 "A2/A3 设备 UB 容量 192KB，64KB 用量仅占 1/3"，并明确 "C_L0 分配在 L0C（独立于 UB），不占用 UB 空间"——这是为何 block=128 还能进一步上调（如 256→128KB）但受限的不是 UB 而是 L0C。

### 表 12：L0 内存预算（§4.6）

| Buffer | Shape | dtype | 大小 (Bytes) |
|--------|-------|-------|-------------|
| C_L0 | `(128, 128)` | float32 | 65,536 (64 KB) |

**解读**：此表是 §4.5 的对照说明，并指出 "A2/A3 设备 L0C 容量为 64KB，`block_M=128, block_N=128` 恰好填满 L0C"——这是为何搜索空间硬限为 `block ≤ 128` 的根本原因（原文因篇幅在 §5.2 末尾被截断，但已通过本表交代清楚）。

---

## 【公式解读】

### 公式 1：标准 2D 卷积定义（原文 §1.3）

$$
\text{Output}(n, oc, i, j) = \sum_{c=0}^{C-1} \sum_{m=0}^{KH-1} \sum_{k=0}^{KW-1} \text{Input}(n, c, i \cdot s + m - p, j \cdot s + k - p) \cdot \text{Kernel}(oc, c, m, k)
$$

**符号释义**（原文表格已列，逐项含义）：

- **Input `(B, C, H, W)`** — 输入特征图，4 元组 `(批大小 b、通道数 c、空间高 h、空间宽 w)`。
- **Kernel `(OC, C, KH, KW)`** — 卷积核，4 元组 `(输出通道数 oc、输入通道数 c、核高 m、核宽 k)`，索引顺序 `(oc, c, m, k)`。
- **Output `(B, OC, HO, WO)`** — 输出特征图 `(批大小 n、输出通道 oc、输出高 i、输出宽 j)`。
- **stride `s`** — 卷积步长，控制 `i, j` 的偏移量。
- **padding `p`** — 零填充量，控制 `(i·s + m - p)`、`(j·s + k - p)` 是否越界。
- 三重求和遍历 `(c, m, k)`，等价于一次完整卷积滑窗。

### 公式 2：输出空间尺寸（原文 §1.3）

$$
HO = \left\lfloor \frac{H + 2p - KH}{s} \right\rfloor + 1, \quad WO = \left\lfloor \frac{W + 2p - KW}{s} \right\rfloor + 1
$$

**符号释义**：H/W 为输入空间高宽；`KH/KW` 为核高宽；`p` 为单边填充（故乘 2 表示两侧填充）；`s` 为步长；向下取整 `⌊·⌋` 即"只保留完整滑窗次数"。此即 im2col 步所依赖的 `HO · WO` 总输出位置数——也是 GEMM 中 N 维度的来源。

### 公式 3：GEMM 形式（文档中作为 "C = A @ B" 文本表达，配合 §3.1 表）

$$
C(M,N) = \text{Kernel\_flat}(M,K) \times \text{Input\_flat}(K,N), \quad \text{即 C = K\_pad @ I\_pad}
$$

**符号释义**（对照 §3.1 与 §4.1/§4.2）：

- **A = Kernel_flat**：shape `(M, K) = (OC, C·KH·KW)`，M 对应"输出通道行维度"。
- **B = Input_flat**：shape `(K, N) = (C·KH·KW, B·HO·WO)`，N 对应"批次 × 输出空间像素列维度"。
- **C = Output_pad**：shape `(M, N) = (OC, B·HO·WO)`，最终经裁剪再 view+permute 变为 `(B, OC, HO, WO)`。

### 伪代码公式（§3.3 GEMM Kernel 骨架）

原文以 Python `@T.prim_func` 给出算法骨架，其关键数学动作：

$$
C[m, n] = \sum_{k} A[m, k] \cdot B[k, n]
$$

分块后逐 block 执行；其中 `init=(k==0)` 是 Ascend GEMM 上"首次清零、后续累加"模式的标志位——伪代码中 `T.gemm_v0(A_L1, B_L1, C_L0, init=(k == 0))` 承担的就是该公式的硬件级实施。

---

## 【关联】

由于原文（文末）注明 **"内部链接: (无)"**，以下关联全由文中提及的文件路径与 API 名交叉得出：

- **同算子变体（上行）**：`examples/convolution/example_convolution_autotune.py` ——同一 conv2d 算子的 autotune 版本，其 block 搜索空间 `[64, 128]` 与本文硬限 `block ≤ 128`（§4.6）相吻合；可视为本算子在 "静态固定 block" 与 "运行时搜索 block" 两个分支中的对照实现。
- **核心算子模式参考（强相似）**：`examples/developer_mode/gemm_developer.py` ——本文 §3.5.3 标注其为「高度相似」，本算子的 `T.gemm_v0 + T.serial K 循环 + T.copy 搬运` 模式即从该文件复用而来；该文件本身在 §3.4 中被列为 `T.gemm_v0` API 的验证用例。
- **附加算子合成参考**：`examples/developer_mode/matmul_add_developer.py` ——「T.copy + T.gemm_v0 组合模式」的相似实现，可在 GEMM 后追加 bias/activation 时直接复用为模板。
- **API 文档上游**：
  - `api-kernel-memory.md`（§1.3/§1.4/§2.1/§2.2/§3）——`T.Kernel(is_npu=True)`、 `@tilelang.jit(out_idx=[-1])`、`T.alloc_shared`、`T.alloc_fragment`、`T.copy` 的来源（§3.4）。
  - `api-compute.md`（§1）——`T.gemm_v0` 的来源（§3.4）。
  - `api-schedule-sync.md`（§1）——`T.serial` 的来源（§3.4）。
- **算子拆分上下游**：
  - 上游：host 端的 PyTorch im2col（§1.4 步骤 1 + §1.5 数据流图 `im2col (host torch)`）。
  - 下游：NPU 端的 GEMM 计算（§1.4 步骤 2）+ GM 上的动态 Padding（§1.4 步骤 3）+ host 侧 view+permute 还原（§1.4 步骤 4）。
- **Pass / JIT 配置相关性**：§4.8 的 `TL_ASCEND_AUTO_CV_COMBINE / TL_ASCEND_AUTO_SYNC / TL_ASCEND_MEMORY_PLANNING` 三项配置是与 §2.3「模式影响」表逐条对应的开关，自动 Cube/Vector 分离、自动同步、自动内存规划三件事由同一基础设施 `tilelang.PassConfigKey` 提供。

---

## 【使用方法】

> **注**：原文没有给出命令行运行方式、API 调用样例或独立启动脚本；以下只汇总原文中**确实出现的**配置项与启用手段。

### 1. JIT 装饰器与 Pass 配置（原文 §4.8 完整照录）

```python
@tilelang.jit(
    out_idx=[-1],      # 最后一个参数 C 为输出
    pass_configs={
        tilelang.PassConfigKey.TL_ASCEND_AUTO_CV_COMBINE: True,    # 自动 Cube/Vector 分离
        tilelang.PassConfigKey.TL_ASCEND_AUTO_SYNC: True,          # 自动同步插入
        tilelang.PassConfigKey.TL_ASCEND_MEMORY_PLANNING: True,    # 自动内存规划
    },
)
```

### 2. Block 尺寸约束（综合 §5.2 与 §4.5/§4.6）

- `block_M = block_N = 128`（受 L0C 64KB 容量硬约束）。
- `block_K = 128`（受 L0A/L0B 各 64KB 容量、L1 带宽折中）。
- 不允许 `block > 128`，否则 L0C 溢出。
- `block_M/N/K 均为编译期常量`；`M, N, K` 可通过 `@tilelang.jit` 参数在编译期传入（§4.7）。

### 3. TileLang 算子骨架签名（§3.3）

```python
@T.prim_func
def main(A: T.Tensor((M, K), "float16"),
         B: T.Tensor((K, N), "float16"),
         C: T.Tensor((M, N), "float16")):
    with T.Kernel(m_num * n_num, is_npu=True) as (cid, _):
        bx = cid // n_num
        by = cid % n_num
        # ... (详见原文)
```

### 4. 自动同步与作用域（§2.3）

- 自动同步：依赖 `TL_ASCEND_AUTO_SYNC=True`。
- 自动作用域（Cube / Vector）：依赖 `TL_ASCEND_AUTO_CV_COMBINE=True`。
- 自动内存规划：依赖 `TL_ASCEND_MEMORY_PLANNING=True`。

### 5. 输入/输出数据流入口（§1.5 / §4.1 / §4.2）

- 输入：`A` 形状 `(M, K) = (OC, C·KH·KW)` 来自 Kernel view，`B` 形状 `(K, N) = (C·KH·KW, B·HO·WO)` 来自 host 端 im2col。
- 输出：`C` 形状 `(M, N) = (OC, B·HO·WO)`，dtype float16，再经 host `view + permute` 变为 `(B, OC, HO, WO)`。

### 6. 动态 Padding 边界条件（§1.4 步骤 3 / §1.5 数据流图）

- 当 `M, N, K` 非 128 整数倍时，host 侧 zero-pad 到下一个 128 的倍数；
- GEMM 完成后由 `裁剪 [:M, :N]` 还原原始尺寸。

> 原文未涉及的常用启用方式（如 CLI 启动、Python 入口调用、env 变量、性能调优开关等），本节不臆造，留空。
