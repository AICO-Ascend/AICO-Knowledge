# vLLM IR: Functional Intermediate Representation

> 仓 `vllm` · 路径 `docs/design/vllm_ir.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/vllm_ir.md

# vLLM IR 设计文档一体化深度解读

> 注: 原文在「3. IR Fusion and Transformation Passes」一节中途被截断 (止于 `# Before SP pass` / `all_reduce =`), 以下解读基于原文实际呈现的内容, 不对截断之后的内容进行臆测。

---

## 【定位】

vLLM IR 是一套位于「低层 torch op」与「vLLM 高层算子层 (如 `RMSNorm`、量化算子)」之间的 **函数式中间表示 (Functional IR)**, 通过把算子的 **语义** 与 **实现/分发** 解耦, 简化编译与 kernel 注册/分发流程, 并以 torch FX dialect 形式与原生 torch op、custom op 及旧的 `CustomOp` 体系共存。

---

## 【技术要点】

1. **算子声明**: 用 `@register_op` 装饰器声明一个 IR op, 其原生 PyTorch 实现同时承担三个角色 — 语义定义、默认实现、测试参考基准 (见 `rms_norm` 示例, `epsilon=1e-5`, `variance_size` 可选)。
2. **实现注册**: 用 `@ir.ops.<op>.register_impl("<provider>", supports_args=..., supported=..., inplace=...)` 注册内核实现; 示例中通过 `current_platform.is_cuda_alike()` 做平台静态判断, 通过 `rms_norm_no_var` 做参数级动态判断 (`variance_size is None`)。
3. **内核优先级选择**: 配置一个 provider 优先级列表, 按顺序查找第一个同时满足 `supported` 与 `supports_args` 的实现; 用户优先级 **前置于** 平台默认, 缺失项自动追加。
4. **配置入口**:
   - CLI: `--ir-op-priority.<op_name>=<provider1>,<provider2>,...`
   - Python: `VllmConfig(kernel_config=KernelConfig(ir_op_priority={...}))`
5. **`maybe_inplace` 重载**: 模型层显式选择允许实现复用输入内存 (返回后 `x` 或 `residual` 使用为 UB), 编译流程会跟踪「donated input」并写入 `PassContext`, 供后续 **clone elimination** 使用。
6. **编译管道 (截断处)**: Dynamo Tracing → AOTAutograd + Functionalization (对 `maybe_inplace` 做手工转 `default`) → IR Fusion & Transformation Passes (含 SP pass 等) → (后续未呈现)。

---

## 【关键机制与数据】

- **数据流 (原文示例)**: Python 端调用 `ir.ops.rms_norm(x, weight, epsilon)` → Dynamo 追踪后落入 FX 图为 `torch.ops.vllm_ir.rms_norm.default(x, weight, 1e-5); x = None` (opaque to Dynamo, 不被分解) → 预 AOTAutograd 钩子把 `fused_add_rms_norm.maybe_inplace(...)` 转成 `...default(...)` → 后续 IR pass 在 functional FX 图上做融合/切分等变换。
- **`RMSNorm` 默认超参 (原文)**: `eps = 1e-6`, `weight = nn.Parameter(torch.ones(hidden_size))`。
- **`fused_add_rms_norm` 返回结构 (原文)**: 元组 `(x2, residual_out)`, 通过 `out[0]` / `out[1]` 解构。
- **donated-input 跟踪 (原文)**: 「The pass also tracks which inputs were 'donated' (passed to `maybe_inplace`), storing this information in vLLM's `PassContext` for later use in clone elimination.」
- **可扩展性 (原文)**: 「ops and implementations can be registered anywhere, in-tree or out-of-tree」。
- **autotune (原文)**: 「The compiler can autotune over available implementations (future feature)」 — 标记为未来特性, 当前非可用能力。
- **OOT 后端 (原文)**: 「OOT compiler backends can lower from the higher-level representation (in-progress)」 — 标记为进行中。
- 原文未提供任何 benchmark / 性能数字 / 延迟 / 吞吐数据。

---

## 【表格解读】

原文未使用 markdown 表格, 但「Platform Defaults」一节以 Python `dict` 字面量形式给出了多平台的 `ir_op_priority` 默认值 (属于配置项), 以下逐字还原为表格并逐行解读:

**表 1 — CUDA/XPU/ROCm 在 Inductor 编译下的默认优先级 (原文: `CUDA/XPU/ROCm platform defaults (when compiling with Inductor)`)**

| op_name | priority list |
|---|---|
| `rms_norm` | `["native"]` |
| `fused_add_rms_norm` | `["native"]` |

解读: 走 `torch.compile` + Inductor 后端时, 各平台统一默认走原生 PyTorch 实现 (`native`), 即不强制走自定义 CUDA/XPU/ROCm kernel, 把优化交给编译器上层 pass。

**表 2 — CUDA 在 eager 或 Dynamo-only 模式下的默认优先级 (原文: `CUDA platform defaults (eager or Dynamo-only)`)**

| op_name | priority list |
|---|---|
| `rms_norm` | `["vllm_c", "native"]` |
| `fused_add_rms_norm` | `["vllm_c", "native"]` |

解读: 关闭 Inductor 时, CUDA 平台优先尝试 `vllm_c` provider (`torch.ops._C` C++/CUDA 内核), 不支持则回退 `native`。

**表 3 — ROCm 计划中的默认优先级 (原文: `ROCm platform defaults (future - currently same as CUDA)`)**

| op_name | priority list |
|---|---|
| `rms_norm` | `["aiter", "vllm_c", "native"]` |
| `fused_add_rms_norm` | `["aiter", "vllm_c", "native"]` |

解读: 原文明确标注「future - currently same as CUDA」, 即此 ROCm 默认 **尚未生效**, 当前实际行为等同于表 2 (CUDA eager/Dynamo-only)。

**表 4 — XPU 在 eager 或 Dynamo-only 模式下的默认优先级 (原文: `XPU platform defaults (eager or Dynamo-only)`)**

| op_name | priority list |
|---|---|
| `rms_norm` | `["xpu_kernels", "native"]` |
| `fused_add_rms_norm` | `["xpu_kernels", "native"]` |

解读: XPU 平台在非 Inductor 路径下优先使用 `xpu_kernels` provider, 再回退 `native`。

**叠加规则 (原文)**: 「User-specified priorities are prepended to platform defaults, so you only need to specify the out-of-order implementations, other implementations are appended automatically.」 — 用户通过 CLI / `KernelConfig` 指定的 provider 会 **前插** 到平台默认列表前, 因此只需显式给出「顺序异常」的实现, 其余按平台默认补齐。

---

## 【公式解读】

**原文无公式。**

(文档中仅有 Python 函数伪代码形式的 RMSNorm 计算: `variance = x_var.pow(2).mean(dim=-1, keepdim=True); x = x * torch.rsqrt(variance + epsilon)`, 这是实现源码而非数学公式, 故不计入「公式」一节。)

---

## 【关联】

文档文末给出的内部链接及对应关系:

- **`torch_compile.md`** — 描述 `torch.compile` 编译管线本身。vLLM IR 重度定制该管线 (Dynamo Tracing → AOTAutograd → 自定义 IR pass → 后端 lowering), 文档「Compilation Pipeline」整节均建立在与该链接文档互补的前提上; 关闭 Inductor 与走 Inductor 的行为差异也直接源自 `torch.compile` 的两种执行模式。
- **`fusions.md`** — 描述融合/fusion 机制。文档「3. IR Fusion and Transformation Passes」一节展示的 SP pass 等变换就是 fusion 能力的具体应用; IR 让「pattern matching in fusion/transformation passes only requires a single, simple pattern per op」, 这一点直接对应 fusions.md 中的 pattern matching 模型。
- **`custom_op.md`** — 描述 torch 自定义 op 机制。文档明确把 vLLM IR 视作 **CustomOp 方案的 piecewise 替代** (「piecewise migration from the previous `CustomOp` approach」), 且 IR op 在 `torch.library` 中以 `vllm_ir` 命名空间注册为 custom op, 与 torch 自定义 op 完全互操作 (「fully compatible with 'regular' torch ops & custom torch ops/kernels」)。

**上下游关系梳理 (原文范围内)**:
- 下层: `torch` / `torch.compile` / `torch.library` / `torch.ops._C` (C++ 扩展)。
- 中间层 (本文主题): `vllm.ir` 模块 + `vllm.ir.ops.*` 注册表 + 编译期 IR pass + `PassContext`。
- 上层 (消费方): `vllm/model_executor/layers/layernorm.py` 等模型层 (如 `RMSNorm.forward` 直接调用 `ir.ops.rms_norm` / `ir.ops.fused_add_rms_norm.maybe_inplace`)。
- 配置层: `vllm.config.VllmConfig` / `KernelConfig.ir_op_priority`, 由 CLI `--ir-op-priority.<op_name>=...` 写入。
- 平台适配层: `current_platform.is_cuda_alike()` 等平台探测 + 各平台的 provider (vllm_c / aiter / xpu_kernels / native)。

---

## 【使用方法】

**1. 启用 (原文隐含)**: 通过 `vllm serve` 启动模型即生效; 若需使用 `torch.compile` 路径, 与上层 `torch.compile` 文档联动 (`torch_compile.md`)。

**2. 命令行 (原文示例)**:

```bash
# CUDA: rms_norm 使用 vllm_c 实现
vllm serve meta-llama/Llama-3.2-1B \
  --ir-op-priority.rms_norm=vllm_c

# ROCm: aiter 优先, 回退 vllm_c, 再回退 native
vllm serve meta-llama/Llama-3.2-1B \
  --ir-op-priority.rms_norm=aiter,vllm_c,native

# 同时配置多个 op
vllm serve meta-llama/Llama-3.2-1B \
  --ir-op-priority.rms_norm=vllm_c \
  --ir-op-priority.fused_add_rms_norm=vllm_c
```

**3. Python 配置 (原文示例)**:

```python
from vllm import LLM
from vllm.config import VllmConfig, KernelConfig

llm = LLM(
    model="meta-llama/Llama-3.2-1B",
    vllm_config=VllmConfig(
        kernel_config=KernelConfig(
            ir_op_priority={
                "rms_norm": ["vllm_c", "native"],
                "fused_add_rms_norm": ["vllm_c", "native"],
            }
        )
    )
)
```

**4. 自定义 op 实现 (原文模式)**:
- 用 `@register_op` 声明语义 (含 `maybe_inplace` 重载)。
- 用 `@ir.ops.<op>.register_impl("<provider>", supports_args=<fn>, supported=<bool>, inplace=<bool>)` 注册内核; 可在 in-tree 或 out-of-tree 注册。

**5. 平台默认生效条件**: 用户未显式指定某 op 的优先级时, 按上文「表格解读」表 1–4 的规则选取; 用户显式提供的 provider 列表前插, 缺失项自动按平台默认补齐。

**原文未涉及**: 性能基准、量化算子的 IR 声明样例 (除动机中提及外)、`PassContext` 的完整 API、自动调优 (autotune) 的启用方式、OOT 后端 lowering 的具体配置 — 原文明确标注 autotune 为「future feature」、OOT 后端为「in-progress」, 故均不展开。
