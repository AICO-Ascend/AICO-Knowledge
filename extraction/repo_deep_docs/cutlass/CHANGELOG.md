# Changelog

> 仓 `cutlass` · 路径 `CHANGELOG.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/cutlass/CHANGELOG.md

# CUTLASS 4.8.0 Changelog 深度解读

---

## 【定位】

本篇文档是 CUTLASS **4.8.0 版本 (2026-08-25)** 的 changelog，核心描述了针对下一代 NVIDIA Rubin 架构 (SM107) 的 **初步支持**，并对 CuTe DSL、CuTe DSL 扩展 (`cute_ext`)、Operator API、C++ 各层抽象进行了大量功能扩展、性能优化与缺陷修复。

---

## 【技术要点】

1. **Rubin (SM107) 首次落地**
   - 原文: 引入 "Initial Rubin support to accelerate dense GEMMs"，需要 **R615 驱动** (随 CUDA Toolkit 13.4 GA 发布，**R610 不支持**)。
   - 同时新增 FP8/FP4 Tensor Core 支持、B collector reuse、TMEM 扩展至 576 COL、SMEM 扩至 328KB (C++ 端为 327 KiB)。

2. **TMEM / SMEM 容量与分配模型重写**
   - 原文: "Extended TMEM size from 512 COL to 576 COL"。
   - 原文: "Higher SMEM (328KB) and TMEM capacity (288KB)" (Operator API 视角)。
   - 原文: C++ 端 "Set the SM107 shared-memory capacity to 327 KiB" 并 "Set the SM107 TMEM capacity to 576 columns per SM"，并更新 1SM / 2SM TMEM allocator 以走 Rubin 独占分配路径。

3. **CuTe DSL 扩展 (`cute_ext`) 预览版编译器**
   - 原文: 新增环境变量开关 `CUTE_DSL_USE_EXTENSION_COMPILER=1`，可在普通 Cute DSL kernel 中混入 `cute_ext` API；行为保持不变但 PTX/SASS 可能不同，未来将设为默认。

4. **CTA-V map 自动推导与新异步原语**
   - 原文: "CTA-V maps are now inferred automatically for `cute_ext` TMA load, store, multicast, and reduce-store operations. Explicit CTA-V maps remain supported as overrides."
   - 原文: "Added asynchronous atomic TMA reduce-store and sparse MMA operations."

5. **Operator API 增加 Rubin 预览 + nvMatmulHeuristics 算子排序**
   - 原文: "Dense GEMMs: FP8xFP8"、"Blockscaled GEMM: {MXFP8}x{MXFP4, MXFP8} and {MXFP4, NVFP4}x{MXFP4, NVFP4}"，并支持 NVFP4 的新 UE5M3 缩放因子 dtype。
   - 原文: "Operators can now be ranked by their estimated performance when nvMatmulHeuristics is available. ... This currently only supports Blackwell kernels as nvMatmulHeuristics does not yet support Rubin."

6. **C++ 端接入 SM107 / 新增 SM107 GEMM 与卷积构建器**
   - 原文: 启用现有 SM100 兼容的 [GEMM](https://github.com/NVIDIA/cutlass/blob/main/include/cutlass/gemm/collective/builders) 与 [convolution](https://github.com/NVIDIA/cutlass/blob/main/include/cutlass/conv/collective/builders/sm100_umma_builder.inl) 构建器支持新的 [`sm_107a` 与 `sm_107f` 目标](https://github.com/NVIDIA/cutlass/blob/main/CMakeLists.txt)。

7. **IKET Profiler 增强**
   - 原文: "Rubin kernels (sm107) can now be profiled."
   - 原文: "Task Scheduling can instrument the schedule with IKET ranges when constructing TaskManager objects (`iket_enable_profiling=True`) ... individual pipeline stages in a schedule may generate separate ranges (`iket_profiling_stages`)."
   - 原文: protobuf 版本要求从 **6.30 降低到 4.21**，为 IKET 过渡到 optional extra 做准备。

8. **依赖与回归修复**
   - 原文: `nvidia-cuda-nvdisasm` 改为 `nvidia-cutlass-dsl` 的可选 `[sass]` extra；`CUTE_DSL_KEEP=sass` / KeepSASS 优先解析 wheel 自带版本 (与 DSL 工具链匹配)，其次解析 `CUDA_HOME`/`CUDA_PATH`；本地提供的 nvdisasm 必须来自**不早于**产出 CUBIN 的工具链。
   - 原文: 修复 4.6.0 回归——`cute.autovec_copy` 对动态 stride 张量发按元素指令而非向量化指令 ([!3463](https://github.com/NVIDIA/cutlass/issues/3463))；修复 TVM-FFI 对 tuple 内 GPU tensor 的 env 流检测 ([!3444](https://github.com/NVIDIA/cutlass/issues/3444))。

---

## 【关键机制与数据】

- **TMEM 列数扩展 (DSL)**: 原文 "Extended TMEM size from 512 COL to 576 COL"——`TMEM_ALLOC_COL` 容量基线增加 64 列，给 ping-pong / accumulator buffer overlap 留余量。
- **SMEM 容量 (DSL/C++/Operator API)**: 原文分别给出 "328KB"、"327 KiB"、"328KB" 三处描述，**对应同一物理配置但不同精度表述** (328KB ≈ 327 KiB ≈ 327,680 bytes)。
- **Operator API 端 TMEM 容量**: 原文 "TMEM capacity (288KB)"——这是基于 576 COL × 每列 512B 推算的典型容量口径。
- **B collector reuse**: 原文 "B collector reuse" 与 "B-buffer reuse"——允许复用 B 操作数加载路径，减少 SMEM 压力与吞吐瓶颈，是 Rubin 面向 FP4/FP8 高密度 GEMM 的关键吞吐优化。
- **CTA-V map 自动推导**: 原文 "CTA-V maps are now inferred automatically for `cute_ext` TMA load, store, multicast, and reduce-store operations"——降低用户对显式 cluster shape 编程的负担，但仍保留显式覆盖。
- **TMEM accumulator-buffer planning (opt-in)**: 原文 "Added opt-in TMEM accumulator-buffer planning, including overlapping ping-pong storage for capacity-constrained kernels"——为容量受限 kernel 提供 ping-pong 重叠。
- **设备端 TMA descriptor 优化**: 原文 "Improved device-side TMA descriptor updates and grouped GEMM performance through SMEM-staged updates, workspace reuse, and reduced prologue and synchronization overhead."
- **IKET protobuf 降级**: 原文 "Reduced the protobuf version requirement of IKET profiler from 6.30 to 4.21."
- **nvMatmulHeuristics 排序 (原文)**: 仅支持 Blackwell kernel；Rubin 暂不支持。
- **已测试下游包版本 (原文)**:

| 包 | commit / 分支 |
|---|---|
| FlashAttention | main (0251105) |
| Quack | main (60d8808) |
| FlashInfer | main (109d44f) |
| cuDNN-Frontend | deveop (25b3d51) (原文拼写) |
| Pytorch | main (cf30153) |
| TensorRT-LLM | main (1cef02e) |

---

## 【表格解读】

原文无标准 markdown 表格。但为便于结构化阅读，下面**逐字**还原原文中两处强结构化列表：

**A. Operator API 预览版 Rubin GEMM 更新清单 (原文)**

| 类别 | 数据流 / dtype 组合 |
|---|---|
| Dense GEMMs | FP8 × FP8 |
| Blockscaled GEMM | {MXFP8} × {MXFP4, MXFP8} |
| Blockscaled GEMM | {MXFP4, NVFP4} × {MXFP4, NVFP4} |
| 新增 dtype 支持 | NVFP4 配套 **UE5M3** 缩放因子 dtype |

逐行解读：Dense 路径先以 FP8×FP8 落地，证明 FP8 Tensor Core 与 B-buffer reuse 通路已通；Blockscaled 路径同时覆盖 MXFP4/MXFP8 与 NVFP4 输入组合；UE5M3 缩放因子与 NVFP4 绑定，呼应 Blackwell Ultra 已开始的 NVFP4 微缩放体系。原文明确这是 "preview" 且"may need additional performance tuning"。

**B. CuTe DSL 扩展 (`cute_ext`) 新功能清单 (原文)**

| 功能 | 作用 |
|---|---|
| CTA-V map 自动推导 | 自动推断 TMA load/store/multicast/reduce-store 的 CTA-V |
| 异步原子 TMA reduce-store | 新异步原子归约写 |
| Sparse MMA | 稀疏矩阵乘指令支持 |
| 可复用 GEMM mainloop / TMA epilogue helper | 减少样板代码 |
| 可选 TMEM accumulator-buffer planning | 含 ping-pong overlap |
| 设备端 TMA descriptor 优化 | SMEM 暂存 + workspace 复用，降低 prologue/同步开销 |

**C. 新增示例清单 (原文)**：

| 架构 | API | 示例 |
|---|---|---|
| Rubin | CuTe | 传统 dtype dense GEMM (带 B collector reuse) |
| Rubin | CuTe | Grouped GEMM (带 B collector reuse) |
| Rubin | CuTe | 块缩放 dense GEMM (FP4/FP6/FP8 混合精度 + UE5M3 / block-32 scale) |
| Rubin | CuTe | 块缩放 grouped GEMM |
| Rubin | CuTe | Blockwise GEMM |
| Rubin | CuTe extension | FP4 块缩放 GEMM |
| Rubin | CuTe extension | Grouped GEMM (带 B collector reuse) |
| Blackwell | CuTe extension | Back-to-back GEMM、Blockscaled GEMM、Persistent GEMM (alpha/beta)、CLC dynamic persistent、GLU、Mixed input、Planar complex、Input transform、GeForce pingpong、Blackwell Ultra blockscaled |
| Blackwell | CuTe extension | Attention: GQA Decode |
| Blackwell | CuTe extension | Grouped GEMM: unscaled / blockscaled |
| Blackwell | CuTe extension | Top-K |
| Ampere | CuTe extension | SIMT GEMM |

> 注：原文 Blackwell CuTe 章节中示例名以列表形式给出，未对应独立 git 链接 (与 Rubin 例外的 `examples/cute/rubin/*.cu` 不同)。下游用户需进入仓库 examples 目录查找对应文件。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **C++ GEMM 主入口**: [`./media/docs/cpp/gemm_api_3x.md`](./media/docs/cpp/gemm_api_3x.md)——3.x 抽象层 GEMM API 文档，与本次启用的 SM100 兼容 GEMM builder 直接相关。
- **CuTe 教程 (4 篇)**:
  - [`./media/docs/cpp/cute/00_quickstart.md`](./media/docs/cpp/cute/00_quickstart.md)
  - [`./media/docs/cpp/cute/01_layout.md`](./media/docs/cpp/cute/01_layout.md)
  - [`./media/docs/cpp/cute/02_layout_algebra.md`](./media/docs/cpp/cute/02_layout_algebra.md)
  - [`./media/docs/cpp/cute/03_tensor.md`](./media/docs/cpp/cute/03_tensor.md)
  - [`./media/docs/cpp/cute/0t_mma_atom.md`](./media/docs/cpp/cute/0t_mma_atom.md)——MMA atom 与 CuTe 抽象的对接点，是阅读新引入的 SM107 MMA traits 的前置知识。
- **性能分析**: [`./media/docs/cpp/profiler.md#gemm`](./media/docs/cpp/profiler.md#gemm)——IKET Profiler 增强后，sm107 Rubin kernel 现可被该 profiler 抓取。
- **单元测试**:
  - [`./test/unit/gemm/device/sm100_tensorop_gemm/f8_f8_void_bf16_narrow_mma_n.cu`](./test/unit/gemm/device/sm100_tensorop_gemm/f8_f8_void_bf16_narrow_mma_n.cu)——SM100 tensorop GEMM 单元测试，是 SM107 复用 SM100 builder 的回归参照系。
  - [`./test/unit/cute/core/`](./test/unit/cute/core/)——CuTe DSL core 单元测试，承载 CTA-V map 自动推导、`cute_ext` 编译器管线等 DSL 行为的回归。
- **Rubin C++ 关键头文件** (原文含链接)：
  - `include/cute/arch/mma_sm107_umma.hpp` —— Rubin SM107 Tensor Core MMA 指令定义。
  - `include/cute/atom/mma_traits_sm107.hpp` —— 对应 CuTe MMA traits。
  - `include/cutlass/arch/arch.h` —— SM107 SMEM 容量定义。
  - `include/cute/arch/tmem_capacity_sm100.hpp` —— TMEM 容量声明（文件沿用 sm100 命名，但已更新为 576 COL）。
  - `include/cute/arch/tmem_allocator_sm100.hpp` —— 1SM / 2SM TMEM 分配器。
  - `examples/cute/rubin/rubin_fp8.cu`、`rubin_fp8_blockscaled.cu`、`rubin_fp4_blockscaled.cu`——Rubin 示例。
- **构建系统**: `CMakeLists.txt` 中的新 target `sm_107a` 与 `sm_107f`。
- **CuTe DSL 扩展**: `CuTeDSL/experimental/compiler_diagnostic/`——4.7.0 引入的 Primitives 编译器诊断示例。
- **下游协作版本**: 已在 FlashAttention (0251105)、Quack (60d8808)、FlashInfer (109d44f)、cuDNN-Frontend (25b3d51)、PyTorch (cf30153)、TensorRT-LLM (1cef02e) 上验证 (见上节"关键机制与数据")。

---

## 【使用方法】

1. **启用 CuTe DSL 扩展编译器管线 (opt-in 预览)**
   ```bash
   CUTE_DSL_USE_EXTENSION_COMPILER=1 python your_program.py
   ```
   原文："This pipeline lets user mix `cute_ext` APIs directly into `@cute.jit` and `@cute.kernel` code and is required for kernels that mix the two API surfaces."

2. **安装 nvdisasm (可选，用于 SASS 转储)**
   - 原文："`nvidia-cuda-nvdisasm` is now an optional dependency of `nvidia-cutlass-dsl` via the optional `[sass]` extra."
   - 启用 SASS 转储: `CUTE_DSL_KEEP=sass` 或 DSL 端 `KeepSASS`。
   - 解析顺序: wheel 自带 (推荐，版本与 DSL 工具链匹配) → `CUDA_HOME` / `CUDA_PATH` 下的本地 CUDA Toolkit；本地版本必须 ≥ 产出 CUBIN 的工具链版本。

3. **运行 SM107 Rubin kernel 的系统前提**
   - 原文："Executing Rubin kernels (SM107) requires the **R615 driver** which will be released with CUDA Toolkit 13.4 GA. R610 from CUDA Toolkit 13.4 Developer Preview is not sufficient."

4. **CMake 构建新目标**
   - 原文：CMake 中引入 `sm_107a` 与 `sm_107f` target，可复用 SM100 GEMM / convolution builder。用户需在 CMake 构建时显式选择新 target 才能启用 327 KiB SMEM 与 576 COL TMEM 的启动路径。

5. **IKET Profiler 配置项**
   - 原文：`iket_enable_profiling=True` —— 在构造 TaskManager 时打开 IKET range。
   - 原文：`iket_profiling_stages` —— 控制单个 schedule 中每个 pipeline stage 是否生成独立 IKET range。
   - 原文：现可仅对特定 cluster dump timing，以降低 profiling 开销。

6. **Operator API 新用法**
   - 原文：通过 `cutlass.kernels` 可**直接调用** standalone kernel，不再必须先经 `cutlass.operators` 查表。
   - 原文：自定义 epilogue fusion 现支持**按行 / 按列的部分归约** (partial reductions)。
   - 原文：Grouped GEMM 改用 `IndexPtrGroupedGemmArguments` (新)，原 `GroupedGemmArguments` 已 deprecated。
   - 原文：当环境提供 `nvMatmulHeuristics` 时，可对 Operator 按预估性能排序 (教程: `media/docs/operators/tutorials/007_heuristics.ipynb`)；当前仅支持 Blackwell。
