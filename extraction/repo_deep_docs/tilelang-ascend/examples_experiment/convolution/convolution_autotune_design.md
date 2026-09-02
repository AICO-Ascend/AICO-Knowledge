# Convolution Autotune 算子设计文档

> 仓 `tilelang-ascend` · 路径 `examples_experiment/convolution/convolution_autotune_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/examples_experiment/convolution/convolution_autotune_design.md

# Convolution Autotune 算子设计文档深度解读

## 【定位】

本文档描述 `tilelang-ascend` 中 `convolution_autotune` 算子的设计与实现：将标准 2D 卷积分解为 PyTorch 端 `im2col` + Ascend NPU 端块级 `GEMM`，并通过 `@tilelang.autotune` 自动搜索 `(block_M, block_N, K_L1)` 最优分块配置，从而在 NPU 上以可调优的方式支持任意 stride / padding 的 2D 卷积。

---

## 【技术要点】

1. **两步算法架构**：CPU/PyTorch 端完成 `im2col` 变换（输入 `(B,C,H,W) → (C·KH·KW, B·HO·WO)`，卷积核 `(OC,C,KH,KW) → (OC, C·KH·KW)`），NPU 端执行 `C = A @ B` 的标准 GEMM。
2. **自动调优三参数**：`@tilelang.autotune` 自动探索 `block_M`、`block_N`、`K_L1` 三个核心分块维度，对应 L1 buffer 形状与 K 维步进。
3. **零填充对齐**：当 `M/N/K` 不能被 block size 整除时，先在 PyTorch 端做零填充（`pad`）到 `M_pad / N_pad / K_pad`，运算后 `slice` 回原始尺寸，从而去除整除约束。
4. **Developer 模式编程模型**：采用 `T.Kernel(m_num * n_num, is_npu=True)` 一维 cid，通过 `bx = cid // n_num`、`by = cid % n_num` 映射到 2D block 网格；使用 `T.alloc_shared` 分配 L1、`T.alloc_fragment` 分配 L0C 累加器。
5. **K 维 `T.serial` 顺序迭代**：`loop_k = T.ceildiv(K, K_L1)`，每次循环通过 `T.copy` 搬运 `block_M × K_L1` 与 `K_L1 × block_N` tile，由 `T.gemm_v0(..., init=(k == 0))` 在首步清零、后续累加。
6. **数据类型与同步**：`A/B/C` dtype 为 `float16`，累加器 `C_L0` 为 `float32`；通过环境/编译开关 `TL_ASCEND_AUTO_SYNC: True` 自动同步，无需手动 `T.barrier_all`。

---

## 【关键机制与数据】

**工作原理（数据流，原文 §1.5）**：

- `Input(B,C,H,W)` 经 PyTorch `im2col` → `Input_flat(C·KH·KW, B·HO·WO)`，再 pad → `Input_flat_pad(K_pad, N_pad)`。
- `Kernel(OC,C,KH,KW)` 经 PyTorch `view` → `Kernel_flat(OC, C·KH·KW)`，再 pad → `Kernel_flat_pad(M_pad, K_pad)`。
- NPU 端通过 `T.copy: GM → L1` 搬运 tile 到 `A_L1`、`B_L1`；`T.gemm_v0` 在 L1 上执行 `L1 @ L1 → L0C`，沿 K 维 `T.serial` 迭代累加；最后 `T.copy: L0C → GM` 得到 `Output_flat_pad`，PyTorch 端 `slice + reshape + permute` 回 `Output(B, OC, HO, WO)`。

**API 可行性（原文 §3.4）**：所有 API（`T.prim_func`、`T.Tensor`、`T.Kernel(..., is_npu=True)`、`T.alloc_shared`、`T.alloc_fragment`、`T.copy`、`T.gemm_v0(... init=...)`、`T.serial`、`T.ceildiv`、`@tilelang.autotune(configs, ref_prog, supply_prog, atol, rtol)`）均已通过 `examples/gemm/` 与 `examples/convolution/` 中相应示例验证通过。

**技术约束（原文 §3.5.1）**：本算子不涉及"不支持三维 Kernel / threads 仅 1 或 2 / 动态循环边界 / 动态边界流水线"四类已知限制——`loop_k = T.ceildiv(K, K_L1)` 为静态表达式（JIT 时 K 与 K_L1 已知），未使用 `threads` 与 `T.Pipelined`。

**性能数据**：原文未给出具体 perf 数字或调优前后对比数据。

---

## 【表格解读】

### 表 1：编程模式选型理由（原文 §2.2）

```
| 考量维度 | 分析 | 结论 |
|---------|------|------|
| 计算类型 | 纯 GEMM 矩阵乘 | Developer 模式 T.gemm_v0 完全覆盖 |
| 是否含 matmul | 是，核心计算即为标准 GEMM | Developer 模式提供 T.gemm_v0 直接支持 |
| 是否含归约 | 是，GEMM 内含 K 维归约累加 | T.gemm_v0 已封装归约语义 |
| 是否需要手动流水线 | 否，仅需 K 维顺序迭代 | T.serial 足够 |
| 是否需要核间通信 | 否，各 block 独立计算不重叠的输出区域 | 无需手动同步 |
| 是否需要特殊硬件原语 | 否，标准 GEMM 即可 | 无需 T.mma 等底层原语 |
| GEMM 后是否需要 element-wise 后处理 | 否，直接输出到 GM | 无融合需求，非融合算子 |
```

**逐行解读**：七项考量共同得出结论——本算子是"纯 GEMM + 顺序迭代 + 无通信 + 无融合"的形态，完美匹配 Developer 模式 `T.gemm_v0` 的能力边界，因此无需切到 Expert 模式去手动管理流水线或低层 mma 原语。

---

### 表 2：模式影响（原文 §2.3）

| 维度 | 本算子的选择 |
|------|-------------|
| 内存分配 | `T.alloc_shared` 分配 L1（自动映射），`T.alloc_fragment` 分配 L0C（自动映射） |
| 计算方式 | `T.gemm_v0` 标准块级矩阵乘 + `T.serial` K 维迭代 |
| 作用域 | 编译器自动处理（无显式 `T.Scope`），仅 Vector 核参与（纯 Cube 计算由编译器自动调度） |
| 同步方式 | 通过 `TL_ASCEND_AUTO_SYNC: True` 自动同步，无需手动 `T.barrier_all` |

**逐行解读**：内存上 L1 用 `alloc_shared`（共享内存）、L0C 用 `alloc_fragment`（片上累加器），二者均交由编译器自动映射；计算上完全由 `T.gemm_v0` + `T.serial` 表达，不显式声明 `T.Scope`；同步交给编译开关 `TL_ASCEND_AUTO_SYNC: True` 统一处理。

---

### 表 3：公式拆解（原文 §3.1）

| 步骤 | 数学表达 | 说明 |
|------|----------|------|
| 1 | `block_num = (M // block_M) × (N // block_N)` | 将 M×N 输出空间划分为 m_num × n_num 个 block |
| 2 | `A_tile = A[bx·block_M : (bx+1)·block_M, k·K_L1 : (k+1)·K_L1]` | 从 GM 加载 A 的一个 tile 到 L1 |
| 3 | `B_tile = B[k·K_L1 : (k+1)·K_L1, by·block_N : (by+1)·block_N]` | 从 GM 加载 B 的一个 tile 到 L1 |
| 4 | `C_L0 += A_L1 · B_L1` | K 维分块累加，accum_dtype=float32 |
| 5 | `C[bx·block_M, by·block_N] = C_L0` | 将 L0C 结果搬回 GM 输出 |

**逐行解读**：步骤 1 完成 2D block 网格划分；步骤 2/3 描述 GM→L1 的 tile 切片坐标；步骤 4 是核心 GEMM 累加（`float32` 精度）；步骤 5 写回 GM。这一拆解直接对应后续 TileLang API 映射。

---

### 表 4：TileLang API 映射（原文 §3.2）

| 步骤 | 数学表达 | TileLang API | 参数 | 模式 |
|------|----------|-------------|------|------|
| 1 | block 划分 | `T.Kernel(m_num * n_num, is_npu=True) as (cid, _)` | block_num, is_npu | Developer |
| 2 | L1 buffer 分配 | `T.alloc_shared((block_M, K_L1), dtype)` | shape, dtype | Developer |
| 3 | L0C fragment 分配 | `T.alloc_fragment((block_M, block_N), accum_dtype)` | shape, accum_dtype | Developer |
| 4 | GM→L1 搬运 A tile | `T.copy(A[bx * block_M, k * K_L1], A_L1)` | src(DDR slice), dst(L1) | Developer |
| 5 | GM→L1 搬运 B tile | `T.copy(B[k * K_L1, by * block_N], B_L1)` | src(DDR slice), dst(L1) | Developer |
| 6 | 矩阵乘累加 | `T.gemm_v0(A_L1, B_L1, C_L0, init=(k == 0))` | A_L1, B_L1, C_L0, init | Developer |
| 7 | K 维迭代 | `T.serial(loop_k)` | range=T.ceildiv(K, K_L1) | Developer |
| 8 | L0C→GM 搬运 | `T.copy(C_L0, C[bx * block_M, by * block_N])` | src(L0C), dst(DDR slice) | Developer |

**逐行解读**：8 步对应一个完整 GEMM block 计算的 tile 化生命周期——Kernel 启动 → buffer 分配 → 两路 GM→L1 → `gemm_v0` 累加（首次 init 清零、后续累加）→ K 维 `T.serial` 循环 → 结果写回 GM。

---

### 表 5：API 可行性确认（原文 §3.4）

| API | 来源 | 验证状态 |
|-----|------|---------|
| `T.prim_func` | `api-kernel-memory.md` §1 | ✅ 已通过 examples/gemm/example_gemm.py 验证 |
| `T.Tensor((shape), dtype)` | `api-kernel-memory.md` §1 | ✅ 已通过所有 GEMM 示例验证 |
| `T.Kernel(block_num, is_npu=True) as (cid, _)` | `api-kernel-memory.md` §1 | ✅ 已通过所有 GEMM 示例验证 |
| `T.alloc_shared(shape, dtype)` | `api-kernel-memory.md` §2 (Developer) | ✅ 已通过 examples/gemm/ 验证 |
| `T.alloc_fragment(shape, dtype)` | `api-kernel-memory.md` §2 (Developer) | ✅ 已通过 examples/gemm/ 验证 |
| `T.copy(src, dst)` | `api-kernel-memory.md` §3 | ✅ 已通过所有搬运场景验证 |
| `T.gemm_v0(A, B, C, init)` | `api-compute.md` §1 | ✅ 已通过 examples/gemm/ 验证 |
| `T.serial(N)` | `api-schedule-sync.md` | ✅ 已通过所有循环场景验证 |
| `T.ceildiv(a, b)` | `examples/gemm/example_gemm.py:40` | ✅ 已通过 GEMM 示例验证 |
| `@tilelang.autotune(configs, ref_prog, supply_prog, atol, rtol)` | `examples/convolution/example_convolution_autotune.py:45-51` | ✅ 本算子已直接使用并验证 |

**逐行解读**：10 个 API 全部已通过相关示例验证，其中 `@tilelang.autotune` 是直接来自本算子同名示例 `example_convolution_autotune.py:45-51`，验证证据最强。

---

### 表 6：本项目已知限制检查（原文 §3.5.1）

| 约束 | 本算子是否涉及 | 处理方案 |
|------|---------------|----------|
| 不支持三维 Kernel | **No** | 使用一维 `T.Kernel(m_num * n_num, is_npu=True)` 足以表达 2D block 划分 |
| threads 参数限制（仅 1 或 2） | **No** | 未使用 `threads` 参数，默认值即可 |
| 动态循环边界不支持 | **No** | `loop_k = T.ceildiv(K, K_L1)` 是静态表达式（K 和 K_L1 均在 JIT 编译时已知） |
| 流水线不支持动态边界 | **No** | 未使用 `T.Pipelined`，仅使用 `T.serial` |

**逐行解读**：四条已知限制均不触发——核心原因是本算子全部循环边界由编译期常量 `K` 与编译期调优常量 `K_L1` 共同决定，无需动态循环。

---

### 表 7：参考实现差异说明（原文 §3.5.2）

| 差异项 | 标准 Conv2d (cuDNN/Direct) | 本项目（Ascend im2col+GEMM） | 转换方案 |
|--------|---------------------------|-------------------------------|----------|
| 计算方式 | 直接卷积或 Winograd 等 | im2col 展开 + GEMM | 用 PyTorch 端 im2col + NPU 端 GEMM |
| 内存占用 | 无中间矩阵膨胀 | im2col 矩阵膨胀 C·KH·KW 倍 | 通过零填充对齐去除整除约束，在可接受范围内 |
| Kernel 维度 | 3D (batch, out_h, out_w) | 2D (M, N) | 通过 `cid // n_num` / `cid % n_num` 将 1D cid 映射到 2D |
| 并行粒度 | 线程级/warp级 | block 级（每 block 处理 block_M × block_N 输出） | block 粒度由 autotune 自动选择 |

**逐行解读**：四类差异中三、四项是硬件/编程模型差异，第二项是 im2col 的固有代价（用零填充缓解整除约束），第一项是最核心的计算范式差异——以"显式 GEMM"取代"卷积原语"。

---

### 表 8：本项目同类实现参考（原文 §3.5.3）

| 文件路径 | 相似度 | 关键参考点 |
|----------|--------|-----------|
| `examples/convolution/example_convolution.py` | **几乎相同** | 非 autotune 版本，核函数结构完全一致 |
| `examples/gemm/example_gemm.py` | **高度相似** | T.gemm_v0 + alloc_shared + alloc_fragment 模式、K 维 tiling、T.serial 迭代结构 |
| `examples/gemm/example_gemm_autotune.py` | **高度相似** | autotune 装饰器用法、configs 生成逻辑 |

**逐行解读**：本算子是 `example_convolution.py`（非 autotune 版本）的超集（加上 autotune），同时复用 `example_gemm.py` 的 GEMM 编程骨架与 `example_gemm_autotune.py` 的 autotune 用法。

---

### 表 9：输入张量（原文 §4.1）

| 参数名 | Shape | dtype | 说明 |
|--------|-------|-------|------|
| `input_t` | `(B, C, H, W)` | `float16` | 输入特征图，位于 GM (NPU) |
| `kernel_t` | `(OC, C, KH, KW)` | `float16` | 卷积核权重，位于 GM (NPU) |

**逐行解读**：两个输入均为 `float16`，位于 GM (NPU)；shape 即标准 NCHW 输入 + OCHW 卷积核。

---

### 表 10：输出张量（原文 §4.2）

| 参数名 | Shape | dtype | 说明 |
|--------|-------|-------|------|
| `output` | `(B, OC, HO, WO)` | `float16` | 卷积输出，位于 GM (NPU) |

**逐行解读**：输出仍是 `float16`，位置在 GM (NPU)；`HO/WO` 由 `⌊(H+2P-KH)/S⌋+1`、`⌊(W+2P-KW)/S⌋+1` 给出（见公式节）。

---

### 表 11：中间缓冲区（PyTorch 端，原文 §4.3，**原文表格被截断**）

| Buffer 名 | Shape | dtype | 存储层级 | 用途 |
|-----------|-------|-------|----------|------|
| `input_flat` | `(C·KH·KW, B·HO·WO)` | `float16` | GM (NPU) | im2col 变换后的输入矩阵 |
| `kernel_flat` | `(OC, C·KH·KW)` | `float16` | GM (NPU) | 卷积核展平矩阵 |

> **注**：原文 §4.3 表格在"卷积核展平矩阵"一行后被截断（文档末尾的 `---` 之后没有更多内容），后续行（如 pad 后的 `M_pad/N_pad/K_pad` 缓冲、`accumulator` 等）原文未给出。

**逐行解读（前两行）**：两个中间矩阵同样位于 GM (NPU) 且 dtype 为 `float16`，分别对应 im2col 后输入与展平后卷积核。`input_flat` 的行数 `C·KH·KW` 与 GEMM 的 K 维一致；`kernel_flat` 的行数 `OC` 与 GEMM 的 M 维一致。

---

## 【公式解读】

### 公式 1：标准 2D 卷积（原文 §1.3）

$$
\text{Output}(n, oc, h_o, w_o) = \sum_{c=0}^{C-1} \sum_{kh=0}^{KH-1} \sum_{kw=0}^{KW-1} \text{Input}(n, c, h_o \cdot S + kh - P, w_o \cdot S + kw - P) \cdot \text{Kernel}(oc, c, kh, kw)
$$

**符号含义**：
- `n` ∈ `[0, B)` —— batch 内样本索引
- `oc` ∈ `[0, OC)` —— 输出通道索引
- `h_o, w_o` —— 输出空间坐标
- `c` ∈ `[0, C)` —— 输入通道（求和维度）
- `kh, kw` —— 卷积核空间坐标（求和维度）
- `S` —— stride（步长）
- `P` —— padding（零填充量）
- `h_o·S + kh − P`、`w_o·S + kw − P` —— 通过 stride 与 padding 还原到输入特征图上的采样坐标

**作用**：定义 2D 卷积的数学语义——在每个输出位置上对所有输入通道与卷积核空间位置做乘累加。

---

### 公式 2：输出空间尺寸（原文 §1.3）

$$
HO = \left\lfloor \frac{H + 2P - KH}{S} \right\rfloor + 1, \quad WO = \left\lfloor \frac{W + 2P - KW}{S} \right\rfloor + 1
$$

**符号含义**：
- `H, W` —— 输入高/宽
- `KH, KW` —— 卷积核高/宽
- `S` —— stride
- `P` —— padding

**作用**：由输入尺寸与卷积超参确定输出 `Output(B, OC, HO, WO)` 的空间维度。

---

### 公式 3：im2col 后的矩阵维度（原文 §1.3）

$$
\text{Input\_flat} \in \mathbb{R}^{(C \cdot KH \cdot KW) \times (B \cdot HO \cdot WO)}
$$

**符号含义**：行数 `C·KH·KW` 是 im2col 把每个卷积窗口内的所有 `(c, kh, kw)` 展平得到的"通道 × 核高 × 核宽"维度；列数 `B·HO·WO` 把 batch 与输出空间合并为 2D 矩阵的列索引。

**作用**：将卷积的"输入滑动窗口采样"等价表示为矩阵行，把"输出空间"等价表示为矩阵列。

---

### 公式 4：展平后的卷积核（原文 §1.3）

$$
\text{Kernel\_flat} \in \mathbb{R}^{OC \times (C \cdot KH \cdot KW)}
$$

**符号含义**：行数 `OC` 是输出通道；列数 `C·KH·KW` 与 `Input_flat` 的行数对齐，是后续 GEMM 的公共维度 K。

**作用**：将 OCHW 卷积核等价表示为 2D 矩阵，便于与 `Input_flat` 做矩阵乘。

---

### 公式 5：等价矩阵乘（原文 §1.3）

$$
\text{Output\_flat} = \text{Kernel\_flat} \cdot \text{Input\_flat}
$$

**符号含义**：标准的 2D 矩阵乘——`Output_flat ∈ ℝ^(OC × B·HO·WO)`。

**作用**：把卷积计算等价替换为一次矩阵乘，NPU 端只需实现 GEMM。

---

### 公式 6：reshape 回 4D（原文 §1.3）

$$
\text{Output} \in \mathbb{R}^{B \times OC \times HO \times WO}
$$

**符号含义**：将 `(OC, B·HO·WO)` 形态的 `Output_flat` 重组为 NCHW 4D 张量。

**作用**：恢复卷积的 4D 语义输出。

---

### 公式 7：K 维 GEMM 分块（原文 §3.1 步骤 4）

$$
C_{L0} \mathrel{+}= A_{L1} \cdot B_{L1}, \quad \text{accum\_dtype} = \text{float32}
$$

**符号含义**：
- `A_L1` —— `(block_M, K_L1)` 的 A tile
- `B_L1` —— `(K_L1, block_N)` 的 B tile
- `C_L0` —— `(block_M, block_N)` 的累加器 fragment
- `accum_dtype=float32` —— 累加在 float32 下进行，避免 fp16 累加溢出/精度损失

**作用**：在 K 维顺序迭代中逐步累加得到 `(block_M, block_N)` 输出 tile。

---

## 【关联】

文档本身明确引用并依赖以下内部模块/示例：

1. **API 参考文档**
   - `api-kernel-memory.md` §1（`T.prim_func` / `T.Tensor` / `T.Kernel(..., is_npu=True)`）—— 核函数与张量声明规范
   - `api-kernel-memory.md` §2（`T.alloc_shared` / `T.alloc_fragment`，Developer 部分）—— 内存分配规范
   - `api-kernel-memory.md` §3（`T.copy`）—— 数据搬运规范
   - `api-compute.md` §1（`T.gemm_v0`）—— 计算原语规范
   - `api-schedule-sync.md`（`T.serial`）—— 循环与同步规范

2. **同模块示例（上游/相似实现）**
   - `examples/convolution/example_convolution.py` —— **几乎相同**的非 autotune 版本，核函数结构完全一致（视为本算子的直接祖先）
   - `examples/convolution/example_convolution_autotune.py:45-51` —— `@tilelang.autotune(configs, ref_prog, supply_prog, atol, rtol)` 的**直接使用来源**
   - `examples/gemm/example_gemm.py` —— `T.gemm_v0` + `alloc_shared` + `alloc_fragment` + K 维 tiling + `T.serial` 的核心 GEMM 范式来源；`T.ceildiv` 用法示例位于该文件 `:40`
   - `examples/gemm/example_gemm_autotune.py` —— autotune 装饰器用法与 `configs` 生成逻辑的参考

3. **上下游关系**
   - **上游**：本算子依赖 `tilelang.autotune` 装饰器（提供 `configs / ref_prog / supply_prog / atol / rtol` 五要素）、`T.gemm_v0` 计算原语以及 `T.copy` 搬运原语。
   - **下游**：作为 `examples/convolution/` 下的 autotune 版本示例，给需要自动调优 block size 的卷积场景提供模板。
   - **本文档内部**：§2 模式选型 → §3 API 映射 → §3.5 约束确认 → §4 数据规格，呈现"模式决策 → 代码骨架 → 可行性 → 数据布局"的递进逻辑；§1.5 数据流图与 §3.3 计算伪代码互相印证。

---

## 【使用方法】

原文涉及的使用/启用信息：

1. **入口示例文件**：`examples/convolution/example_convolution_autotune.py`（@tilelang.autotune 的具体使用位置见该文件 `:45-51`）。
2. **autotune 装饰器签名**（原文 §3.4）：
   ```python
   @tilelang.autotune(configs, ref_prog, supply_prog, atol, rtol)
   ```
   其中 `configs` 由 `(block_M, block_N, K_L1)` 三维度的候选组合构成（具体候选集在原示例文件中给出）。
3. **底层核函数签名**（原文 §3.3 伪代码）：
   ```python
   @T.prim_func
   def main(
       A: T.Tensor((M, K), "float16"),    # Kernel_flat
       B: T.Tensor((K, N), "float16"),    # Input_flat
       C: T.Tensor((M, N), "float16"),    # Output_flat
   ):
   ```
   其中 `M = OC`、`K = C·KH·KW`、`N = B·HO·WO`。
4. **编译/同步开关**（原文 §2.3）：`TL_ASCEND_AUTO_SYNC: True`，启用后无需手动 `T.barrier_all`。
5. **运行流程**：调用方需自行用 PyTorch 在 CPU 或 NPU 上完成 `im2col`（将 `(B,C,H,W)` 展开为 `(C·KH·KW, B·HO·WO)`）与卷积核展平，再按需 pad 到 block size 整数倍，最后调用本算子的 `@T.prim_func` 完成 GEMM；运行结束后对结果 `slice` 回原始尺寸并 `reshape + permute` 回 `(B, OC, HO, WO)`。

> **注**：原文 §4.3 表格在末尾被截断（缺 pad 后缓冲等后续行），§5 及之后的"性能测试 / 使用示例 / 调优结果"等章节**原文未涉及**，因此本文档的"使用方法"无法给出端到端可运行命令示例；如需完整调用流程，请直接参阅 `examples/convolution/example_convolution_autotune.py`。
