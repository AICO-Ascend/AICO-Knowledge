# TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS （同社区）

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/triton_cv/overview.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/triton_cv/overview.md

# 深度解读：torch_npu Inductor Triton CV 特性文档

---

## 【定位】

本篇文档围绕 **torch_npu Inductor 下的 Triton CV（Compute-Visual / 卷积-向量融合）特性** 展开，介绍了三枚与社区同名同语义的环境变量（`TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS`、`TORCHINDUCTOR_MAX_AUTOTUNE`、`TORCHINDUCTOR_PROFILE_WITH_DO_BENCH_USING_PROFILING`）的开关与默认值，以及 Triton CV 融合算子在 `torch_npu` 上的能力简介、Python 调用示例、`max-autotune` 编译日志示例与最终被选中落地到 `output_code.py` 的 AOT（Ahead-Of-Time）融合算子片段。文档解决的核心问题是：**在 NPU 设备上为 PyTorch Inductor 提供对标社区的 Triton CV 融合后端，并通过 max-autotune 机制自动挑选最优的 MM/Pointwise 融合模板**。

---

## 【技术要点】

1. **三枚环境变量（与社区同语义）**：
   - `TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS`：控制 max-autotune 候选后端集合，默认 `"ATEN,TRITON,CPP"`；若想加入 `CATLASS`，需将该值中显式列入 `"CATLASS"`。
   - `TORCHINDUCTOR_MAX_AUTOTUNE`：是否开启 max-autotune，`"1"` 开启、`"0"` 关闭，默认 `"0"`。
   - `TORCHINDUCTOR_PROFILE_WITH_DO_BENCH_USING_PROFILING`：autotune 期间是否启用 profiling，`"1"` 启用、`"0"` 不启用，默认 `"0"`。

2. **Triton CV 特性动机**：在 eager 模式下 MM 与后续 pointwise（如 ReLU/SiLU/Bias Add）作为独立 Kernel 依次执行，存在频繁 Kernel 启动开销与全局内存 I/O 瓶颈；torch_npu inductor 通过 Triton 后端对标社区，支持 cv 融合（MM+Pointwise 融合算子）。

3. **MM shape 测试用例**：示例使用 `MM_SHAPES = [(200, 256, 256)]`，前向函数 `forward_mm(self, a, b)` 调用 `torch.mm(a, b)`，并通过 `torch._dynamo.testing.rand_strided` 生成带 stride 的张量 `(M, K)`、`(K, N)`，`M=N=K=256`（其中 M=200）。

4. **autotune 候选模板（persistent + 非 persistent）**：日志中出现两类 NPU Triton 模板——
   - `triton_npu_persistent_mm_<id>`：长驻（persistent）kernel 模板
   - `triton_npu_triton_mm_<id>`：通用 Triton MM 模板
   
   关键调优参数包括 `BLOCK_K=128`、`BLOCK_M ∈ {64, 128}`、`BLOCK_N ∈ {64, 128}`、`EVEN_K=True`、`GROUP_M ∈ {1, 2, 4}`、`num_stages ∈ {2, 3, 4}`、`num_warps ∈ {4, 8}`，persistent 模板额外包含 `NUM_BLOCKS=8`、`NUM_BLOCKS_M=2`、`NUM_BLOCKS_N=4`、`NUM_SMS=8`、`NUM_TILES_PER_PROGRAM=1`、`WIDTH=8`。

5. **autotune 实测耗时**：原文日志显示 `SingleProcess AUTOTUNE benchmarking takes 48.6676 seconds and 349.0871 seconds precompiling for 462 choices`——即对 **462 个候选配置**进行预编译耗时约 349 秒，autotune 基准实测耗时约 48.67 秒。

6. **AOT 输出格式**：被选中最优模板后，会落地到 `torch_compile_debug` 目录下的 `output_code.py`，以 `triton_npu_persistent_mm` 命名空间暴露，并通过 `async_compile.triton('triton_npu_persistent_mm', ...)` 异步编译；最终 Graph 的 Source Nodes 仅有 `mm` 一项（`# Topologically Sorted Source Nodes: [mm], Original ATen: [aten.mm]`）。

7. **数据 dtype 与 stride**：示例 dtype 全部为 `torch.float16`（`ACC_TYPE='tl.float32'`，`ALLOW_TF32='False'`），tensor stride 为 `(K, 1)` 与 `(1, K)` 的标准行/列主序布局。

---

## 【关键机制与数据】

**工作原理（原文：）**：
- "传统的 PyTorch eager 模式下，矩阵乘法和随后 pointwise（如激活函数 ReLU、SiLU、Bias Add 等）通常作为独立的 Kernel 依次执行。这种方式会导致频繁的 Kernel 启动开销和大量的全局内存数据传输（I/O 瓶颈），严重影响性能。"
- "社区 PyTorch Inductor 通过 Triton 后端可以支持 cv 融合，因此 torch_npu 的 inductor 中也要对标社区功能，为 cv 融合提供相应的 triton 后端。"

**autotune 候选性能数据（原文日志逐行摘录，原文：）**：

| 模板 | 耗时(ms) | 相对最优比 | 关键差异参数 |
|---|---|---|---|
| `triton_npu_persistent_mm_164` | 0.0034 | 100.0% | `BLOCK_M=128, BLOCK_N=64, GROUP_M=2, num_warps=4, num_stages=2`（胜出）|
| `triton_npu_triton_mm_14` | 0.0034 | 99.8% | `BLOCK_M=128, BLOCK_N=64, GROUP_M=1, num_warps=4, num_stages=2` |
| `triton_npu_persistent_mm_177` | 0.0034 | 99.7% | `num_warps=8, num_stages=2` |
| `triton_npu_persistent_mm_167` | 0.0034 | 99.6% | `num_warps=8, num_stages=3` |
| `triton_npu_persistent_mm_176` | 0.0034 | 99.6% | `num_warps=4, num_stages=2` |
| `triton_npu_triton_mm_22` | 0.0035 | 99.5% | `BLOCK_M=64, BLOCK_N=128, GROUP_M=4, num_stages=3` |
| `triton_npu_persistent_mm_170` | 0.0035 | 99.5% | `num_warps=4, num_stages=2` |
| `triton_npu_persistent_mm_168` | 0.0035 | 99.2% | `num_warps=4, num_stages=4` |
| `triton_npu_persistent_mm_162` | 0.0035 | 99.2% | `num_warps=4, num_stages=4` |
| `triton_npu_persistent_mm_179` | 0.0035 | 99.1% | `num_warps=8, num_stages=3` |

**autotune 全流程耗时（原文：）**：`SingleProcess AUTOTUNE benchmarking takes 48.6676 seconds and 349.0871 seconds precompiling for 462 choices`。

**Graph Fragment 中的 tensor 元数据（原文：）**：
- `%arg0_1 : Tensor "f16[200, 256][256, 1]npu:0" = PlaceHolder[target=arg0_1]`
- `%arg1_1 : Tensor "f16[256, 256][1, 256]npu:0" = PlaceHolder[target=arg1_1]`
- `%mm : Tensor "f16[200, 256][256, 1]npu:0"[num_users=1] = call_function[target=torch.ops.aten.mm.default](args = (%arg0_1, %arg1_1), kwargs = {})`

**Profilin g（原文：）**：日志中显示 `CANN profiling data parsed in a total time of 0:00:02.020406`，`All profiling data parsed in a total time of 0:00:03.191598`，对应 `TORCHINDUCTOR_PROFILE_WITH_DO_BENCH_USING_PROFILING` 启用后的 CANN profiler 解析过程。

---

## 【表格解读】

**原文无表格**。

说明：原文以代码块、日志块、列表形式呈现配置项与示例，未提供任何结构化 markdown 表格；上面的"关键机制与数据"小节中本人**根据原文日志条目手工汇总的候选模板表**，是出于解读需要自行整理，不属于原文既有表格。

---

## 【公式解读】

**原文无公式**。

说明：原文未出现任何 LaTeX、伪代码或符号化公式。性能数据均以日志中的"毫秒（ms）+ 百分比"形式直接呈现，例如 `0.0034 ms 100.0%` 表示该候选耗时 0.0034 毫秒并相对其他候选达到 100% 的相对速度（即被选为最优）。

---

## 【关联】

根据文末 Graph fragment 中的内部链接信息 `args = (%arg0_1, %arg1_1)`：

1. **上游输入算子**：`%arg0_1` 与 `%arg1_1` 是 Graph 中以 `PlaceHolder` 形式声明的两个 NPU 张量占位符，分别承载 shape `[200, 256]`（stride `[256, 1]`）与 `[256, 256]`（stride `[1, 256]`）的 `torch.float16` 数据，是 `torch.ops.aten.mm.default` 的两个输入形参。

2. **下游唯一消费者**：`%mm` 节点的 `[num_users=1]` 表明该 MM 结果在示例模型中仅被返回（`return %mm`），未与 pointwise 算子进一步融合——文档标题虽称 "Triton cv 融合"，但当前示例展示的是 MM 模板本身的 autotune 落地结果，cv 融合能力由更上层的模板体系承接。

3. **与三枚环境变量的关联**：
   - `TORCHINDUCTOR_MAX_AUTOTUNE="1"` 是触发本节示例中 462 个候选 autotune 的开关；
   - `TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS="ATEN,TRITON,CPP"` 决定了候选集来源（ATEN / TRITON / CPP 三家后端，本示例展示的均为 NPU 扩展的 TRITON 类候选模板）；
   - `TORCHINDUCTOR_PROFILE_WITH_DO_BENCH_USING_PROFILING` 决定了 autotune 时是否拉起 CANN profiler（即日志末尾"Start parsing profiling data"的来源）。

4. **与 AOT 输出的关联**：上述 Graph 编译后落地为 `output_code.py`，其内部通过 `async_compile.triton('triton_npu_persistent_mm', ...)` 注册最优模板，并通过 `torch_npu._inductor.runtime.triton_heuristics` 触发实际执行。

---

## 【使用方法】

1. **开启 max-autotune**（原文：）
   ```shell
   export TORCHINDUCTOR_MAX_AUTOTUNE=1
   ```
   关闭：
   ```shell
   export TORCHINDUCTOR_MAX_AUTOTUNE=0
   ```

2. **自定义 max-autotune GEMM 后端集合**（原文：）
   ```shell
   export TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS="TRITON"
   ```
   加入 Catlass 后端（原文示例）：在该变量值中追加 `"CATLASS"`。

3. **启用 autotune profiling**（原文：）
   ```shell
   export TORCHINDUCTOR_PROFILE_WITH_DO_BENCH_USING_PROFILING="1"
   ```
   关闭：
   ```shell
   export TORCHINDUCTOR_PROFILE_WITH_DO_BENCH_USING_PROFILING="0"
   ```

4. **运行 Triton cv 示例**（原文 Python 代码）：通过 `import torch_npu` 启用 NPU 后端，定义 `MM_SHAPES = [(200, 256, 256)]` 后调用 `_run_both_modes(self.forward_mm, (a, b), profile_name=f"cv_mm_{M}x{N}x{K}", eager_result=eager_result)`，分别以 eager 与 `torch.compile` 模式运行并比对结果；通过 `_MAX_AUTOTUNE = os.environ.get("TORCHINDUCTOR_MAX_AUTOTUNE", "0") == "1"` 决定 profile 名标签 `"maxautotune"` 或 `"noautotune"`。

5. **查看结果**：autotune 完成后在 `torch_compile_debug` 目录下的 `output_code.py` 中查看被选中的 `triton_npu_persistent_mm` 融合算子实现，并比对 eager 与 compile 模式的输出一致性。

6. **支持的硬件**（原文：）：仅列 `<term>Atlas A5 系列产品</term>`。
