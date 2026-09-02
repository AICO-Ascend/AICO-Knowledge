# Fused MoE Kernel Features

> 仓 `vllm` · 路径 `docs/design/moe_kernel_features.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/moe_kernel_features.md

# vLLM Fused MoE Kernel Features —— 深度解读

---

## 【定位】

这篇文档是 vLLM 项目中关于 **Fused MoE (Mixture of Experts) Kernel 特性的总览性 design 文档**,核心解决"如何在多种可选的 MoE kernel 中作出选择"的问题——它系统性梳理了 vLLM 支持的两大类组件:
1. **All2All 通信 backend**(`FusedMoEPrepareAndFinalizeModular` 的子类,负责 EP 专家并行下的 dispatch/combine)
2. **Experts kernel**(`fused_experts` 等实现,负责实际计算)

通过列出每个实现支持的"激活格式 / 量化类型 / 量化格式 / 异步性 / TopK 权重施加位置 / Modular 适配"等维度,帮助用户为特定 workload / 硬件 / 量化方案挑选合适的组合。

---

## 【技术要点】

1. **两阶段流水线架构**:MoE kernel 由 **prepare/finalize** (all2all 通信层) 和 **experts** (计算层) 共同组成,两者通过"激活格式"与"量化格式"必须兼容的约束组合使用。
2. **All2All backend 五选一**:`naive` / `deepep_high_throughput` / `deepep_low_latency` / `flashinfer_nvlink_two_sided` / `flashinfer_nvlink_one_sided`,通过 `--all2all-backend` 命令行参数或 `ParallelConfig.all2all_backend` 参数选择。
3. **量化格式四元组表示法**:**G**(Grouped) / **G(N)**(Grouped w/block size N,如 G(128)) / **A**(Per activation token) / **T**(Per tensor)。
4. **两种输出激活格式**:`standard`(标准) 与 `batched`(批处理),由 prepare 步决定,finalize 步必须接收相同格式;所有 backend 的 `prepare` 都接受 standard 输入,所有 `finalize` 都返回 standard 输出。
5. **量化时机灵活性**:量化可发生在 dispatch 之前或之后,例如 `deepep_high_throughput` 仅支持 fp8 的 block-quantized 格式,**其它格式会先以更高精度 dispatch,再在之后量化**;反过来 `flashinfer_nvlink_*` 系列支持调度前后多种量化方案。
6. **异步能力差异**:仅部分 backend 支持 **DBO (Dual Batch Overlap)** 与 **shared expert overlap**(共享专家在 combine 阶段被计算),只有 `deepep_*` 两个 backend 标注 `Async=Y`。
7. **TopK 权重施加位置特殊语义**:部分模型(如 **Llama**)在 `topk==1` 时要求把 topk 权重施加在**输入激活**而非输出上;modular kernel 由 `FusedMoEPrepareAndFinalizeModular` 子类负责,non-modular kernel 则由 experts 函数自行处理该 flag。
8. **拓扑限制**:`flashinfer` 是唯一可**不带 EP 单独工作**(可 EP 或 DP 不带 EP)的 backend;其它所有 backend **仅在 `EP+DP` 或 `EP+TP` 拓扑**下可用。

---

## 【关键机制与数据】

### 工作原理(三层结构)

| 层 | 角色 | 代表类 |
|---|---|---|
| Communication backend | 实现 EP 下的 dispatch/combine | `FusedMoEPrepareAndFinalizeModular` 子类 |
| Experts kernel | 完成被路由 token 的实际 expert 计算 | Triton / DeepGemm / Cutlass 等 `fused_experts` |
| Quantization method | 决定量化方案与权重格式 | `FusedMoEMethodBase` 子类(如 `ModelOptFp8MoEMethod`) |

**数据流方向**:
- 原始激活 → (backend) prepare → (experts) 计算 → (backend) finalize → 原始激活类型
- 所有 `prepare` 方法**接收 standard 输入**,所有 `finalize` 方法**返回 standard 输出**(原文:*"All the backend `prepare` methods expect activations in the standard format and all the `finalize` methods return activations in standard format"*)
- **prepare 步的输出 = 量化后的类型**;**finalize 步输入类型 = 原始激活类型**(原文举例如:若原输入 bfloat16 + fp8/per-tensor scales,则 `prepare` 输出 fp8/per-tensor,`finalize` 接收 bfloat16)

### 量化时机约束(原文案例)

| 格式支持情况 | 行为 |
|---|---|
| 路径 A: backend 仅支持块量化 fp8(如 `deepep_high_throughput`) | 其它格式会**先以高精度 dispatch,再在之后量化**(原文:*"Any other format will result in dispatching in higher precision and quantizing afterwards"*) |
| 路径 B: backend 支持调度后量化(如 `deepep_low_latency`,标注³ "All quantization happens after dispatch") | 量化统一延迟到 dispatch 之后 |
| 路径 C: `naive` backend 标注 "all" 量化类型——支持 mxfp4 / nvfp4 / int4 / int8 / fp8 全套(脚注¹) | 灵活适配 |

### 性能/能力向量化指标(原文摘录)

- **`deepep_high_throughput`** 的量化格式:`G(128), A, T²` —— 即支持 fp8 block-quant(group size 128)、per-token、per-tensor,标注² 表示 "A,T quantization occurs after dispatch"。
- **`flashinfer_nvlink_one_sided`** 是支持**最多量化类型**的 backend:`nvfp4, bf16, mxfp8, fp8` 四种兼具。
- 所有 backend 都支持 Apply Weight On Input(naive 例外,标注⁶ "depends on the experts implementation")。

---

## 【表格解读】

> **原文有两张关键表格,以下用 markdown 逐字还原。**(注意:原文中第一张表的"cutlass_fp8"行因文本被截断而不完整,以下严格按可见内容重现。)

### 表 1 — All2All backend 特性对比

| Backend | Output act. format | Quant. types | Quant. format | Async | Apply Weight On Input | Subclass |
| ------- | ------------------ | ------------ | ------------- | ----- | --------------------- | --------- |
| naive | standard | all¹ | G,A,T | N | ⁶ | [`MoERunner`][vllm.model_executor.layers.fused_moe.runner.moe_runner.MoERunner] |
| deepep_high_throughput | standard | fp8 | G(128),A,T² | Y | Y | [`DeepEPHTPrepareAndFinalize`][vllm.model_executor.layers.fused_moe.prepare_finalize.deepep_ht.DeepEPHTPrepareAndFinalize] |
| deepep_low_latency | batched | fp8 | G(128),A,T³ | Y | Y | [`DeepEPLLPrepareAndFinalize`][vllm.model_executor.layers.fused_moe.prepare_finalize.deepep_ll.DeepEPLLPrepareAndFinalize] |
| flashinfer_nvlink_two_sided | standard | nvfp4,fp8 | G,A,T | N | N | [`FlashInferNVLinkTwoSidedPrepareAndFinalize`][vllm.model_executor.layers.fused_moe.prepare_finalize.flashinfer_nvlink_two_sided.FlashInferNVLinkTwoSidedPrepareAndFinalize] |
| flashinfer_nvlink_one_sided | standard | nvfp4,bf16,mxfp8,fp8 | G,A,T | N | N | [`FlashInferNVLinkOneSidedPrepareAndFinalize`][vllm.model_executor.layers.fused_moe.prepare_finalize.flashinfer_nvlink_one_sided.FlashInferNVLinkOneSidedPrepareAndFinalize] |

**Table Key 注释:**
1. All types: **mxfp4, nvfp4, int4, int8, fp8**
2. **A,T quantization occurs after dispatch**(per-token 与 per-tensor 量化发生在 dispatch 之后)
3. **All quantization happens after dispatch**(所有量化发生在 dispatch 之后)
4. *Controlled by `--moe-backend` (`flashinfer_cutlass` or `flashinfer_trtllm`)* —— (此脚注对应原始表格中某个未列出的行,因为表格被截断所以无法定位)
5. *This is a no-op dispatcher…These cannot be selected via environment variable. These are generally used for testing or adapting an expert subclass to the `fused_experts` API.*
6. *This depends on the experts implementation.*
- G — **Grouped**
- G(N) — **Grouped w/block size N**
- A — **Per activation token**
- T — **Per tensor**

**逐行解读**:

- **`naive`**:作为最朴素的 baseline,支持全部量化类型,无异步、无 NVLink 约束,子类直接关联 `MoERunner` 而非专用 prepare/finalize。Apply Weight on Input 的可用性依赖具体的 experts 实现(脚注⁶)。
- **`deepep_high_throughput`**:高吞吐场景,使用 **DeepEP** 库,强制要求 fp8 量化,量化格式细节为 G(128) + A + T,且 A/T 量化**延迟到 dispatch 之后**(脚注²),原生支持 async(→ DBO / shared expert overlap)与 Apply Weight on Input。
- **`deepep_low_latency`**:低延迟场景,**输出采用 batched 格式**(而非 standard),这是与 high_throughput 的关键差异;所有量化都在 dispatch 后完成(脚注³)。
- **`flashinfer_nvlink_two_sided`**:通过 NVLink 通信,支持 nvfp4 与 fp8 两种量化,**无 async**(→ 不能用 DBO),**不支持 Apply Weight on Input**(Y/N 标记 N)。
- **`flashinfer_nvlink_one_sided`**:单边 NVLink,支持**最丰富的量化类型**:nvfp4 / bf16 / mxfp8 / fp8 四种,同样 N/N(no async, no weight-on-input)。

### 表 2 — Experts Kernel 特性对比

| Kernel | Input act. format | Quant. types | Quant. format | Activation function | Apply Weight On Input | Modular | Source |
| ------ | ----------------- | ------------ | ------------- | ------------------- | --------------------- | ------- | ------ |
| triton | standard | all¹ | G,A,T | silu, gelu,</br>swigluoai,</br>silu_no_mul,</br>gelu_no_mul | Y | Y | [`fused_experts`][vllm.model_executor.layers.fused_moe.fused_moe.fused_experts],</br>[`TritonExperts`][vllm.model_executor.layers.fused_moe.experts.triton_moe.TritonExperts] |
| triton (batched) | batched | all¹ | G,A,T | silu, gelu | ⁶ | Y | [`BatchedTritonExperts`][vllm.model_executor.layers.fused_moe.experts.fused_batched_moe.BatchedTritonExperts] |
| deep gemm | standard,</br>batched | fp8 | G(128),A,T | silu, gelu | ⁶ | Y | [`DeepGemmExperts`][vllm.model_executor.layers.fused_moe.experts.deep_gemm_moe.DeepGemmExperts],</br>[`BatchedDeepGemmExperts`][vllm.model_executor.layers.fused_moe.experts.batched_deep_gemm_moe.BatchedDeepGemmExperts] |
| cutlass_fp4 | standard,</br>batched | nvfp4 | A,T | silu | Y | Y | [`CutlassExpertsFp4`][vllm.model_executor.layers.fused_moe.experts.cutlass_moe.CutlassExpertsFp4] |
| cutlass_fp8 | standard,</br>batched | fp8 | A,T | silu, gelu | Y | Y | [`CutlassExpertsFp8`][vllm.model_executor.laye... *(原文被截断)* |

**Table Key** (与表 1 共享,见上)

**逐行解读**:

- **`triton` / `TritonExperts`**:基础 Triton 实现,支持 standard 格式输入、最广的量化类型、所有常见激活函数(silu / gelu / **swigluoai** / silu_no_mul / gelu_no_mul),显式支持 Apply Weight On Input。Modular 接口形式为 `TritonExperts`。
- **`triton (batched)` / `BatchedTritonExperts`**:仅匹配需要 batched 格式的 backend(如 `DeepEPLLPrepareAndFinalize`),所以只支持 silu / gelu,Apply Weight 同样依赖具体实现。
- **`deep gemm`**:单行覆盖两种入口 `DeepGemmExperts` + `BatchedDeepGemmExperts`,专为 **fp8 + G(128)** 设计,激活函数仅 silu / gelu。
- **`cutlass_fp4` / `CutlassExpertsFp4`**:基于 CUTLASS 的 nvfp4 实现,只用 A + T 量化格式(无 block-grouped),仅 silu。
- **`cutlass_fp8`** *(原文截断)*:基于 CUTLASS 的 fp8 实现,支持 standard 与 batched 双入口、A+T、silu/gelu,与 cutlass_fp4 对称。

### Modular kernels 支持的 `FusedMoEMethodBase` 量化方法

原文以 bullet 形式列出,严格保留:

- [`ModelOptFp8MoEMethod`][vllm.model_executor.layers.quantization.modelopt.ModelOptFp8MoEMethod]
- [`Fp8MoEMethod`][vllm.model_executor.layers.quantization.fp8.Fp8MoEMethod]
- [`CompressedTensorsW4A4Nvfp4MoEMethod`][vllm.model_executor.layers.quantization.compressed_tensors.compressed_tensors_moe.compressed_tensors_moe_w4a4_nvfp4.CompressedTensorsW4A4Nvfp4MoEMethod]
- [`CompressedTensorsW8A8Fp8MoEMethod`][vllm.model_executor.layers.quantization.compressed_tensors.compressed_tensors_moe.compressed_tensors_moe_w8a8_fp8.CompressedTensorsW8A8Fp8MoEMethod]
- [`GptOssMxfp4MoEMethod`][vllm.model_executor.layers.quantization.mxfp4.GptOssMxfp4MoEMethod]
- [`UnquantizedFusedMoEMethod`][vllm.model_executor.layers.fused_moe.UnquantizedFusedMoEMethod]

---

## 【公式解读】

**原文无显式数学公式**。

但文档使用了一套**符号约定**(本质为"配置组合记号"),逐字符解读如下:

| 记号 | 含义 | 作用 |
|---|---|---|
| `G` | Grouped | 表示"按 expert 分组"的量化 |
| `G(N)` | Grouped w/block size N | 表示"按 expert 分组 + 内部 block 量化,块大小为 N",例如 `G(128)` 即 block size = **128** |
| `A` | Per activation token | 表示"按 token 粒度"的 scale(逐 token 一个 scale) |
| `T` | Per tensor | 表示"整个 tensor 共用"一个 scale(per-tensor) |

此外一些组合记号:
- `G,A,T` 表示同时支持 Grouped、Per-token、Per-tensor 三种量化尺度。
- `G(128),A,T` 表示支持块大小 128 的 Grouped + Per-token + Per-tensor,**专门用于 fp8**(`deepep_*` 系列的关键约束)。
- `A,T` 表示"无 grouped 量化,只有逐 token 与逐 tensor"(e.g. `cutlass_fp4`、`cutlass_fp8`)。

> 上述记号是表格列值的"语法",并非数学公式,故严格意义上原文**不含 LaTeX / 伪代码形式的公式**。

---

## 【关联】

文档主要通过以下结构与上下文章节发生耦合:

1. **强耦合 → [Fused MoE Modular Kernel](./fused_moe_modular_kernel.md)**(链接出现 2 次):
   - 第 1 次:解释 standard / batched 两种激活格式的细节时,*"More details on the formats can be found in the [Fused MoE Modular Kernel](./fused_moe_modular_kernel.md) document"*
   - 第 2 次:解释 prepare / finalize / experts 流水线中各步激活的"类型与格式"时,*"See the diagrams in [Fused MoE Modular Kernel](./fused_moe_modular_kernel.md) for more details on the types and formats of activations at each step of the MoE process"*
   - 也就是说,本文是**外层目录页**,真正的"图示与机制细节"在 `fused_moe_modular_kernel.md`。

2. **隐含关联**:
   - 与 `MoERunner`(`vllm.model_executor.layers.fused_moe.runner.moe_runner`)耦合,定义在 EP 入口层。
   - 与各类 `FusedMoEMethodBase` 子类(quantization 层)耦合,决定哪些量化格式**可与 modular kernel 配对**。
   - 与 `ParallelConfig.all2all_backend` 耦合(运行时配置入口)。
   - 通过 `fused_experts` 函数接口(EP 计算入口)与"experts 实现族"耦合。

---

## 【使用方法】

### 启用 All2All backend

通过命令行参数选择(原文):
```bash
--all2all-backend <backend_name>
```

或通过 Python `ParallelConfig` 配置:
```python
ParallelConfig(all2all_backend=<backend_name>)
```

可选 backend:<br>
`naive` / `deepep_high_throughput` / `deepep_low_latency` / `flashinfer_nvlink_two_sided` / `flashinfer_nvlink_one_sided`

> 原文特别说明:**除 `flashinfer` 外,所有 backend 仅在 `EP+DP` 或 `EP+TP` 拓扑下工作**;`flashinfer` 是唯一支持在无 EP 时单独 DP 工作的 backend。

### 配对约束(原文语义)

要与某个 `FusedMoEPrepareAndFinalizeModular` 子类**成功组合**,对应的 experts kernel 必须满足三重兼容性:
1. **激活格式**一致(standard ↔ standard, batched ↔ batched)
2. **量化类型**交集非空
3. **量化格式**交集非空

> 原文:*"To be used with a particular `FusedMoEPrepareAndFinalizeModular` subclass, MoE kernels must have compatible activation formats, quantization types and quantization formats."*

### TopK 权重施加点

- modular kernel:由 `FusedMoEPrepareAndFinalizeModular` 子类处理
- non-modular kernel:由 experts 函数自身根据 flag 处理
- 适用模型示例:**Llama 在 `topk==1` 时**需要在 input 端施加权重

### Async 启用条件

原文指出:**支持 `Async=Y` 的 backend**(`deepep_high_throughput`、`deepep_low_latency`)才能启用 **DBO (Dual Batch Overlap)** 与 **shared expert overlap**(共享专家在 combine 阶段被计算)。

### 未提及内容

- 具体性能 benchmark 数字、延迟/吞吐数据 —— **原文未涉及**
- 硬件兼容性矩阵(如 H100 vs A100) —— **原文未涉及**
- 显存占用 / 安装要求 —— **原文未涉及**
- `--moe-backend` 参数的完整使用示例 —— **原文仅在脚注⁴ 中提到"由 `--moe-backend` (`flashinfer_cutlass` 或 `flashinfer_trtllm`) 控制"**,未给出更多细节(注:其目标行因表格截断而无法完整对照)
