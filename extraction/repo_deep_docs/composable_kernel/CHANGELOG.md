# Changelog for Composable Kernel

> 仓 `composable_kernel` · 路径 `CHANGELOG.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/composable_kernel/CHANGELOG.md

# Composable Kernel CHANGELOG 一体化深度解读

## 【定位】

这篇 CHANGELOG 是 AMD ROCm 生态下 **Composable Kernel (CK)** 这一面向 AMD GPU 的高性能算子/内核库的版本演进记录，自 **ROCm 5.7.0 的 CK 0.2.0** 一直贯穿到 **ROCm 10.0 的 CK 1.2.0**，按版本号 × ROCm 版本双轴组织 Added / Changed / Optimized / Fixes / Upcoming changes / Known issues 等条目，描述了 GEMM、FMHA、卷积、归一化、量化、池化、规约等模块的能力扩展与架构支持（Gfx9/Gfx11/Gfx12/Gfx942/Gfx950）演进。

---

## 【技术要点】

1. **量化 GEMM 矩阵扩张**：CK Tile 的 row-column 量化 GEMM 新增"多 D（bias）+ 大张量"支持；a8w8 路径通过 eight-waves 流水线重排调度、加宽 epilogue 存储以及 C/D 的 nontemporal 访存来提升性能（ROCm 10.0 / CK 1.2.0）。

2. **Blockscale / Microscaling (MX) 体系全面铺开**：从 ROCm 7.0 起依次加入 MX FP8/FP6/FP4 GEMM、Flatmm MX FP8/FP4、blockscale 2D、aquant 模式 Col-Col-Row-Col、abquant 模式 eightwarps + preshuffleB、FP8 块尺度 / 动态张量级 / per-tensor 量化（FMHA fwd V3 @ gfx950）等多档精度路径。

3. **CK-Tile 调度与流水线增强**：包含 `Arch` 模板参数（`gfx9_t`/`gfx12_t` 等）以支持同 kernel 跨架构多目标链接、`make_kernel`/`CShuffleEpilogueProblem` 移除 `BlockSize` 以兼容 Wave32、gfx950 上的 compute async pipeline、persistent async input scheduler、Ping-pong 调度（沿 K 维）、rotating buffer，以及 Stream-K 版本的 mixed fp8/bf16 GEMM。

4. **FMHA 能力大幅扩展**：逐步覆盖 hdim 为 32 倍数、logit soft-capping、FP8 KV cache（batch prefill）、streamingllm sink 与 gpt-oss sink（qr_ks_vs / qr_async / qr_async_trload / splitkv 等多种流水线）、FP8 块尺度/张量级/逐张量量化、WMMA（gfx12）、gfx11 通用支持、f32 输入、KV cache 多 layout + 灵活 page size + 多 lookup table 配置。

5. **Convolution 模块向"分组化"统一**：从 ROCm 6.0 起统一 grouped convolution API（#817），加入 GKCYX 布局（forward / backward weight / backward data）、NGCHW & NHWGC 的 2D/3D 支持、Split K（bwd data）、bf16/f32/f16 多精度支持、RDNA 3 (gfx12) 上的 3D 分组卷积，**且明文宣告 non-grouped convolution 已弃用**（ROCm 7.1.0）。

6. **工具链、构建与底层替换**：移除 gfx940/gfx941 支持（#1944）；用 Clang20 内建函数替换裸 buffer load/store intrinsics（#1876）；DL/DPP kernel 默认启用；引入 CK-Tile dispatcher（C++ + Python 前端的统一 kernel dispatch、代码生成、按架构过滤，最初覆盖 GEMM，ROCm 7.2.0）；即将要求 C++20（ROCm 7.1.1 起预告，ROCm 7.2.0 复述）；新增 SGPR 多内存大小加载 API、`pk_int4_t` B 张量类型、Pooling、Top-k Sigmoid、reduce / multi reduction、batched contraction 等新算子。

---

## 【关键机制与数据】

> 说明：原文为变更日志，未给出性能数字、延迟/吞吐等具体数据；以下机制与限定均直接引自原文。

- **原文**：CK Tile row-column 量化 GEMM 引入 "multiple D (bias) and large tensor support"。
- **原文**：a8w8 GEMM 的三条性能改进 = "better instruction scheduling in the eight-waves pipeline + wider epilogue stores + nontemporal C/D memory access"。
- **原文**：TF32 卷积 "could be enabled/disabled via `DTYPES` of 'tf32'"，适用架构 gfx942 与 gfx950。
- **原文**：MX FP8/FP4 on gfx950 仅作用于 FMHA forward 的 `"qr" pipeline only"。
- **原文**：FP8 per-tensor quantization for FMHA forward V3 pipeline 在 gfx950 上可用。
- **原文**：`load_tile_transpose` 新增"takes reference to output tensor as output parameter"的 overload。
- **原文**：transpose GEMM pipeline 中"Use data type from LDS tensor view when determining tile distribution for transpose"。
- **原文**：blockscale GEMM 在 abquant 模式下加入 "eightwarps support" 与 "preshuffleB support"。
- **原文**：CK_TILE grouped convolution 引入 "explicit GEMM" 支持（forward 与 backward weight）。
- **原文**：FMHA FWD 新增 streamingllm sink 与 gpt-oss sink；streamingllm 覆盖 `qr_ks_vs / qr_async / splitkv`；gpt-oss sink 覆盖 `qr_ks_vs / qr_async / qr_async_trload / splitkv`。
- **原文**：FMHA batch prefill kernel 支持 "several KV cache layouts, flexible page sizes, and different lookup table configurations"。
- **原文**：新增 `gfx1153` target；FMHA 新增 `gfx11` 支持；FMHA 引入 WMMA (gfx12) 支持。
- **原文**：CK-Tile dispatcher 是 "a unified kernel dispatch, code generation and architecture-based kernel filtering system with C++ and Python frontends starting with GEMM support"。
- **原文**：CK Tile universal GEMM on gfx950 新增 "compute async pipeline"。
- **原文**：`make_kernel` 移除 `BlockSize`（PR #2594），并新增 optional template parameter `Arch`（取值如 `gfx9_t`, `gfx12_t`）以"support linking multiple object files that have the same kernel compiled for different architectures"。
- **原文**：FMHA examples/tests 可"built for multiple architectures (gfx9, gfx950, gfx12) at the same time"。
- **原文**：移除 `BlockSize` 目的："to support Wave32 in CK Tile (#2594)"。
- **原文**：ROCm 6.1.0 ckProfiler 引入"an option to vary the number of warm-up cycles and iterations (#1124)"；同版本 GEMM XDL 加"generic instances (#1161)"。
- **原文**：归一化反向操作加入 gamma/beta 参数："Added gamma and beta parameters for the layernorm and groupnorm bwd operations (#1133)"。
- **原文**：ROCm 6.1.0 GEMM 新增优化："New performance optimizations for GEMM operations on MI200 and MI300 architectures (#1135)"；ROCm 6.1.0 修复"Fixed some conversion issues for fp8 data type (#1099)"，缩短 build time（#1084）。
- **原文**：ROCm 7.0.0 删除对 gfx940 与 gfx941 的支持（#1944），并"Replaced the raw buffer load/store intrinsics with Clang20 built-ins (#1876)"。
- **原文**：ROCm 7.0.0 中 "DL and DPP kernels are now enabled by default"；grouped convolution 实例工厂对 NGCHW/GKYXC/NGKHW 三类布局的实例数被精简（forward/weight/data 各一条声明）。
- **原文**：ROCm 7.1.0 宣告"Non-grouped convolutions are deprecated. Their functionality is supported by grouped convolution."
- **原文**：ROCm 7.1.1 与 ROCm 7.2.0 复述"Composable Kernel will be adopting C++20 features in an upcoming ROCm release, updating the minimum compiler requirement to C++20."
- **原文**：ROCm 6.0.0 修复 "Fixed a hazard associated with inline v_dot (#808)"，修复"two bugs in grouped convolution backward data without K padding (#848 #876)"。

---

## 【表格解读】

**原文无表格。** 整篇 CHANGELOG 仅以 Markdown 列表（含少量带 `( #PR号 )` 的引用）形式记录变更，未出现任何参数表、性能对比表、配置矩阵或命令行选项表。

---

## 【公式解读】

**原文无公式。** 文档内未出现任何数学公式或伪代码表达式，所有机制描述均以自然语言给出。

---

## 【关联】

> 内部链接：原文未提供任何相对路径/内部锚点链接，但有一处外部文档定位链接：**https://rocm.docs.amd.com/projects/composable_kernel/en/latest/**（用于指向 Composable Kernel 官方用户文档）。

可基于文档内容归纳的关联/上下文如下：

- **跨版本族谱**：CK 1.2.0 同时发布在 ROCm 10.0、ROCm 7.13、ROCm 7.2.0 三个 ROCm 版本下；CK 1.1.0 对应 ROCm 7.1.1 / 7.1.0 / 7.0.0 / 6.1.0 / 6.0.0；CK 0.2.0 对应 ROCm 5.7.0（即更早期版本与 ROCm 主线并行维护）。
- **算子间耦合**：FMHA 模块与卷积/GEMM 模块在量化路径上互通——FP8 块尺度量化、MX FP8/FP4 与 FP8 per-tensor 量化同时出现在 GEMM/Flatmm 与 FMHA 两侧；blockscale GEMM 的 aquant / abquant 模式扩展（Col-Col-Row-Col、eightwarps、preshuffleB）反映 GEMM ↔ Conv 通用的张量尺度方案。
- **API 演进链**：`make_kernel` 的 `BlockSize` 删除 → `Arch` 新增 → Wave32 与跨架构对象文件链接，反映"C++ 模板参数治理"在 CK-Tile 一侧的连锁改造。
- **构建链改造**：Clang20 built-ins 替换裸 buffer load/store（#1876）与 C++20 编译器最低要求，构成"语言标准 + 编译器内置"协同升级；gfx940/gfx941 移除 (#1944) 与 gfx11/gfx1153/gfx12/WMMA/gfx950 引入，对应硬件目标支持矩阵的此消彼长。
- **Convolution ↔ Grouped Convolution 收敛**：从 ROCm 6.0 API 调整（#817）→ ROCm 6.0 支持 NGCHW/NHWGC 2D/3D → ROCm 7.0 增 GKCYX 布局与 Split K → ROCm 7.1.0 宣告 non-grouped 弃用，明确把所有卷积能力收敛到 grouped 入口。
- **文档链接入口**：所有功能均以同一外部文档链接（`rocm.docs.amd.com/.../composable_kernel`）作为权威说明，CHANGELOG 本身只承担"变更事实记录"角色。

---

## 【使用方法】

- **TF32 卷积开关**（ROCm 7.13 / CK 1.2.0）：原文："could be enabled/disabled via `DTYPES` of 'tf32'"，适用 gfx942、gfx950。
- **CK-Tile dispatcher 入口**（ROCm 7.2.0 / CK 1.2.0）：原文："a unified kernel dispatch, code generation and architecture-based kernel filtering system with C++ and Python frontends starting with GEMM support"，表示提供 C++ 与 Python 两套前端。
- **跨架构 kernel 编译/链接**（ROCm 7.2.0 / CK 1.2.0）：原文：`make_kernel` 增 optional template parameter `Arch`（`gfx9_t`, `gfx12_t` 等），用于"linking multiple object files that have the same kernel compiled for different architectures"；FMHA examples/tests 可同时为 gfx9 / gfx950 / gfx12 构建。
- **Wave32 适配**（ROCm 7.2.0 / CK 1.2.0）：原文：移除 `make_kernel` 与 `CShuffleEpilogueProblem` 中的 `BlockSize`，"to support Wave32 in CK Tile (#2594)"。
- **ckProfiler 调参**（ROCm 6.1.0 / CK 1.1.0）：原文："Added an option to vary the number of warm-up cycles and iterations for ckProfiler (#1124)"。
- **编译器要求（预告）**：原文（ROCm 7.1.1 与 ROCm 7.2.0 重复）："Composable Kernel will be adopting C++20 features in an upcoming ROCm release, updating the minimum compiler requirement to C++20."
- **支持的 GPU 目标**：原文明示新增 `gfx1153`（ROCm 7.13）、`gfx11`（FMHA）、`gfx12`（WMMA、3D grouped conv on RDNA 3）；移除 `gfx940` 与 `gfx941`（ROCm 7.0，#1944）。
- **新算子可直接调用**：原文仅声明新增 pool、top-k sigmoid、reduce / multi reduction、batched contraction、elementwise、batched GEMM DL 等 kernel，是否需通过特定 API 启用需查阅外部文档（https://rocm.docs.amd.com/projects/composable_kernel/en/latest/）。
