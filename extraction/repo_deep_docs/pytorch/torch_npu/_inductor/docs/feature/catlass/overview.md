# Catlass特性介绍

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/catlass/overview.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/catlass/overview.md

# Catlass 特性文档深度解读

## 【定位】

本文档介绍 **inductor-ascend 中引入的 Catlass 特性**——昇腾对标 NVIDIA CUTLASS 的高性能 GEMM Kernel 库，用于在 PyTorch 编译模式 (`torch.compile`) 下提供与 CUTLASS 等价的 GEMM 优化及 Epilogue CV 融合能力，从而消除 Eager 模式下"矩阵乘法 + Pointwise 算子"链式执行带来的 Kernel 启动开销与全局内存 I/O 瓶颈。

---

## 【技术要点】

1. **对标关系**：Catlass 在昇腾领域对标 NVIDIA CUTLASS，提供高度优化的 GEMM Kernel，并在 Epilogue 阶段支持自定义后处理操作的融合。
2. **融合范畴**：支持将部分 **pointwise 类算子**（如 ReLU、SiLU、Bias Add 等）直接融合到 GEMM Kernel 的 Epilogue 中，减少内存访问与 Kernel 启动次数。
3. **算子覆盖**：通过 `TORCHINDUCTOR_CATLASS_ENABLED_OPS` 环境变量声明可对 `mm, addmm, bmm, grouped_mm` 四类矩阵乘算子进行 Catlass 模板调优尝试。
4. **后端调优切换**：通过 `TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS` 环境变量可声明对 matmul 类算子尝试的后端集合（示例为 `CATLASS,ATen`）。
5. **CV 融合开关**：通过 `CATLASS_EPILOGUE_FUSION=1` 开启 Catlass epilogue 的 CV（Compute Vector）融合功能，使 SiLU 等尾块算子可被融合进 GEMM Kernel。
6. **Autotune 机制**：在 `TORCHINDUCTOR_MAX_AUTOTUNE=1` 下，inductor 会对同一 matmul shape 调优多个不同 tiling/swizzle 参数的 Catlass Kernel，并与 `aclnn` 实现的 `mm` 进行性能比较，自动选择最优算子。

---

## 【关键机制与数据】

### 工作原理

- **Eager 模式痛点**：传统 Eager 模式下 `mm` 之后接 `pointwise` 算子（如 ReLU、SiLU、Bias Add）会作为独立 Kernel 依次执行，导致 **频繁的 Kernel 启动开销** 与 **大量全局内存数据传输（I/O 瓶颈）**。
- **融合机制**：Catlass 在 GEMM Kernel 的 **Epilogue 阶段**（Kernel 的最后阶段）直接融合部分支持的 pointwise 算子，避免中间结果写回 HBM。
- **典型融合模式**：示例中 `mm + silu` 被融合为单一 `catlass_fused_silu_0` Kernel，其内部 IR 仍保留 `aten.sigmoid` 与 `aten.mul` 两个原语（`%sigmoid = call_function[target=torch.ops.aten.sigmoid.default](args = (%mm,))`，`%mul = call_function[target=torch.ops.aten.mul.Tensor](args = (%mm, %sigmoid))`），由 Catlass 在 Kernel 端完成 sigmoid→mul 链路。
- **Autotune 选择**：对 `(512, 256) × (256, 1024)` 的 matmul，Catlass 会展开多个 tiling config（如 `catlass_gemm_0` 至 `catlass_gemm_3`），分别对应不同 `BlockM / BlockN / BlockK / Swizzle` 参数。

### 性能数据（原文日志）

- 原文日志中各候选 Kernel 的耗时与相对最优比例（针对 `AUTOTUNE mm(512x256, 256x1024)`）：
  - `catlass_gemm_3`：**0.0083 ms / 100.0%**
  - `catlass_gemm_0`：**0.0085 ms / 98.1%**
  - `mm`（aclnn）：**0.0086 ms / 96.9%**
  - `catlass_gemm_1`：**0.0088 ms / 94.2%**
  - `catlass_gemm_2`：**0.0107 ms / 77.7%**
- 原文 Autotune 总耗时：**`SingleProcess AUTOTUNE benchmarking takes 3.5552 seconds and 2.3107 seconds precompiling for 5 choices`**——即对 5 个候选做 2.3107 秒预编译 + 3.5552 秒实测。
- 示例输入 dtype：`torch.float32`；并设置 `torch_npu.npu.matmul.allow_hf32 = True`。

---

## 【表格解读】

原文无独立 Markdown 表格，但 Autotune 日志本质为**结构化候选列表**，按"耗时升序"逐字还原如下：

| 候选算子 | 耗时 (ms) | 相对最优 (%) | 模板名（Kernel Tile / Swizzle 参数） |
|---|---|---|---|
| `catlass_gemm_3` | 0.0083 | 100.0% | `AtlasA5_BasicMatmulTla_MmadPingpong_GemmIdentityBlockSwizzle_3_0_80_128_256_80_128_64` |
| `catlass_gemm_0` | 0.0085 | 98.1% | `AtlasA5_BasicMatmulTla_MmadPingpong_GemmIdentityBlockSwizzle_3_0_128_160_128_128_160_48` |
| `mm`（aclnn） | 0.0086 | 96.9% | — |
| `catlass_gemm_1` | 0.0088 | 94.2% | `AtlasA5_BasicMatmulTla_MmadPingpong_GemmIdentityBlockSwizzle_3_0_112_96_256_112_96_64` |
| `catlass_gemm_2` | 0.0107 | 77.7% | `AtlasA5_BasicMatmulTla_MmadPingpong_GemmIdentityBlockSwizzle_3_0_128_80_256_128_80_64` |

**逐行解读**：
- 表头对应原文日志的"算法名 / 耗时 / 相对比例 / 模板描述"。`%` 表示该候选相对于当前最优候选的吞吐/速度比例（越高越优，最优为 100%）。
- 第一行 `catlass_gemm_3` 在该 shape 下耗时最低，被选为最优。模板名 `3_0_80_128_256_80_128_64` 中数字按模板命名约定对应 `BlockM=80`、`BlockN=128`、`BlockK=256`、`SwizzleDir=80`、末尾两个尾数描述 swizzle offset/参数。
- `catlass_gemm_0` 与 `_gemm_3` 仅相差 0.0002 ms（98.1%），但在 BlockM（128 vs 80）与 Swizzle 参数上不同，体现 autotune 在 `BlockM`/`BlockN`/`BlockK` 网格上的细粒度搜索。
- `mm`（aclnn）行耗时 0.0086 ms（96.9%），说明在本 shape 下默认 aclnn 实现的 `mm` 与最优 Catlass Kernel 性能非常接近，但仍被 `catlass_gemm_3` 反超。
- `catlass_gemm_1`（`BlockM=112, BlockN=96`）与 `catlass_gemm_2`（`BlockM=128, BlockN=80`）均明显慢于最优，验证了 **`BlockM × BlockN` 选择对 M=N=512 量级 shape 的敏感性**。

---

## 【公式解读】

原文无公式。唯一可被解读为"算子复合表达式"的，是 `output_code.py` 中注释给出的 Graph fragment（伪 IR 形式）：

```text
%sigmoid : [num_users=1] = call_function[target=torch.ops.aten.sigmoid.default](args = (%mm,), kwargs = {})
%mul     : [num_users=1] = call_function[target=torch.ops.aten.mul.Tensor]  (args = (%mm, %sigmoid), kwargs = {})
```

**符号含义**：
- `%mm`：上游 `aten.mm` 的输出张量（即 GEMM 结果，shape 推断为 `(512, 1024)`）。
- `%sigmoid`：`aten.sigmoid` 对 `%mm` 的逐元素输出，即 `σ(%mm)`。
- `%mul`：`aten.mul.Tensor` 对 `%mm` 与 `%sigmoid` 的逐元素乘积，语义为 **`%mm · σ(%mm)`**，即 **SiLU 激活函数**（`x · sigmoid(x)`）。
- 两者均被 `[num_users=1]` 标注为单消费者，无下游进一步算子，是 Catlass epilogue **整链路 CV 融合**的典型模式。

---

## 【关联】

### 上下游 / 同级模块关系
- **上游/对标**：**NVIDIA CUTLASS**（Gemm Kernel 库 + Epilogue 融合）。Catlass 在昇腾侧提供等价能力。
- **承载框架**：**`torch._inductor`**（PyTorch 编译模式后端）。本文档路径 `torch_npu/_inductor/docs/feature/catlass/overview.md` 表明 Catlass 是 inductor 在 NPU 后端的一个 feature 接入点。
- **运行后端**：**CANN**（昇腾异构计算架构），通过 `acl/acl.h`、`runtime/rt_ffts.h`、`tiling/platform/platform_ascendc.h` 等头文件被 Catlass Kernel 直接调用；示例中 `torch_npu.npu.matmul.allow_hf32` 即 CANN 层 mm 的 TF32 开关。
- **Autotune 机制**：复用 `torch._inductor` 的 `SingleProcess AUTOTUNE benchmarking`，由 `torch._inductor.select_algorithm` 等模块支撑，并通过 `torch._inductor.async_compile.AsyncCompile` 异步编译 Catlass 模板。
- **可融合尾块算子**：示例中的 `aten.silu` 展开为 `sigmoid`+`mul` 两个 ATen 原语，二者均在 Catlass epilogue 融合范围内（文档首段明列 `ReLU、SiLU、Bias Add`）。

### 内部链接/算子映射
- 文档注释中提到的内部链接：
  - `args = (%mm,)` —— 链接到 `aten.sigmoid.default` 的输入；
  - `args = (%mm, %sigmoid)` —— 链接到 `aten.mul.Tensor` 的输入。
- 这两个 IR 节点均在 Catlass 生成的 `catlass_fused_silu_0` Kernel 内部被消化，体现 **IR 层算子↔Kernel 层 epilogue 融合算子**的对应关系。

---

## 【使用方法】

### 启用方式（环境变量，原文示例）

| 环境变量 | 作用 | 示例值 |
|---|---|---|
| `TORCHINDUCTOR_MAX_AUTOTUNE` | 开启 max autotune | `1` |
| `TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS` | 对 matmul 类算子尝试的后端集合 | `CATLASS,ATen` |
| `TORCHINDUCTOR_NPU_CATLASS_DIR` | Catlass 库所在路径 | `/path/to/catlass/dir` |
| `CATLASS_EPILOGUE_FUSION` | 开启 Catlass epilogue 的 CV 融合功能 | `1` |
| `TORCHINDUCTOR_CATLASS_ENABLED_OPS` | 启用 Catlass 调优尝试的 matmul 类算子 | `mm,addmm,bmm,grouped_mm` |

### 编译调用

```python
torch_npu.npu.matmul.allow_hf32 = True        # 允许 HF32/TF32 路径下的 mm
forward_mm = torch.compile(forward_mm, backend="inductor")  # 编译模式，inductor 后端
compile_result = forward_mm(a, b)
```

### 验证方式

- **运行时**：观察 stdout 中的 `AUTOTUNE mm(...)` 日志，确认出现 `catlass_gemm_*` 候选行及百分比排序。
- **生成代码**：在 `torch_compile_debug` 目录的 `output_code.py` 中查找 `catlass_fused_silu_*`（或对应融合名）的 `async_compile.catlass(r'''...''')` 代码块，其 C++ 内核入口为 `PT_EXPORT int catlass_fused_silu_0(const float* X, const float* W, const float* Y, ...)`，签名中带 `M / N / K`、`workspace_size`、`workspace`、`aclrtStream stream` 参数，证明已被融合进单 Kernel。
