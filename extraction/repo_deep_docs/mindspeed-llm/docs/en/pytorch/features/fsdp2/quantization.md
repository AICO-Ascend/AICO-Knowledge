# MindSpeed LLM FSDP2 Back-End Low-Precision Training Guide

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/fsdp2/quantization.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/fsdp2/quantization.md

# MindSpeed LLM FSDP2 Back-End Low-Precision Training Guide 一体化深度解读

---

## 【定位】

这篇文档系统说明在 MindSpeed LLM 框架的 **FSDP2 后端**上如何启用**低精度训练**（以 `mxfp8` 为代表），并通过 `QuantizationRecipe` 配方与**低精度 all-gather 通信**协同降低通信开销与显存占用，从而在大模型 LLM 训练场景中兼顾效率与精度。

---

## 【技术要点】

1. **量化配方（QuantizationRecipe）命名规范**：以 `<scaling_strategy>_<scaling_granularity>[-blocksize0-blocksize1-blocksize2]_<inputs_dtype>_<weight_dtype>_<grads_dtype>` 五段式/可选段式字符串描述一份量化配方，目前仅支持 `MX` 缩放粒度。
2. **预置 `mxfp8` 配方**：`dynamic_MX-1-1-32_E4M3_E4M3_E4M3`，即动态 MX 缩放、块尺寸 1-1-32、输入/权重/梯度均为 `E4M3`。
3. **量化粒度可控**：`quant_block_size` 默认 `32`，结合 `quant_format`（`E4M3` / `E5M2` / `HIF8`）控制具体数据格式。
4. **模块级范围控制**：通过 `quant_apply_modules`（如 `'model.layers.{*}'`）与 `quant_ignored_modules`（如 `'*lm_head'`、`'*gate'`）分别圈定应用与豁免范围，支持通配符。
5. **多种 Converter 并行支持**：`quantize.linear.mx` 用于标准线性层（FFN/Attention），`quantize.moe.mx` 专用于 MoE 专家模块，MoE 模型可两者叠加使用。
6. **低精度 All-Gather 通信**：通过 `enable_fsdp_low_precision_all_gather`（默认 `True`）+ `fsdp_low_precision_all_gather_mode`（默认 `'on-demand'`）让 FSDP 在前/反向时按需聚合低精度权重，与量化训练协同放大效率收益。

---

## 【关键机制与数据】

- **量化与通信协同的工作原理**：先通过 `QuantizationRecipe` 把权重按指定 dtype（典型为 `E4M3`）量化为低精度，再在 FSDP2 后端执行参数 all-gather 时直接搬运低精度权重，避免了"先反量化再通信"造成的额外带宽与显存开销。
- **on-demand vs all 模式**：`on-demand`（默认）只搬运前/反向当前真正需要的权重；`all` 模式则在前后向均搬运所有权重。**启用 recomputation 时框架会自动切换为 `all` 模式以保证计算一致性**。
- **MXFP8 块式量化**：默认块尺寸为 `32`，与 MX 规范一致；MX 是当前**唯一支持的缩放粒度**。
- **EFSDP 配套约束**：启用 efsdp 时，必须把 `efsdp_shard_placement_fn` 设为 `shard_by_dim_0`，以保证量化权重的分片与通信正确性。
- **性能数据**：原文未给出任何具体的吞吐/显存/加速比数字，所有量化与通信收益均以"显著降低通信开销与内存占用"等定性表述呈现。

---

## 【表格解读】

### 表 1：参数总览（原文 Parameter Overview）

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--model.quant_recipe_name` | str | `mxfp8` (required) | Name of the quantization recipe. |
| `--model.quant_format` | str | `E4M3` | FP8 data format used for quantization. Supported values: `E4M3`, `E5M2`, `HIF8`. |
| `--model.quant_block_size` | int | `32` | Block size for MXFP8 block-wise quantization. |
| `--model.quant_apply_modules` | str | `'model.layers.{*}'` | Layers or modules to which quantization applies. |
| `--model.quant_ignored_modules` | str | `'*lm_head'`, `'*gate'` | List of submodules to which quantization does not apply. |
| `--model.quant_converters` | str | `'quantize.linear.mx'` | List of quantization converters to use. |
| `--model.enable_fsdp_low_precision_all_gather` | bool | `True` | Whether to enable low-precision communication. |
| `--model.fsdp_low_precision_all_gather_mode` | str | `'on-demand'` | FSDP low-precision all-gather mode. Aggregates the weights needed for the forward or backward pass on demand. |

**逐行解读：**
- `quant_recipe_name`：唯一必填项，原文以 `mxfp8` 作为示例预设。
- `quant_format`：FP8 数据格式三选一（`E4M3`/`E5M2`/`HIF8`），默认 `E4M3`。
- `quant_block_size`：仅对 MXFP8 块式量化生效，默认 `32`，与 MX 规范一致。
- `quant_apply_modules`：默认作用于全部 Transformer 层 `'model.layers.{*}'`，可用更具体路径覆盖某一子模块（如 `model.layers.0.self_attn`）。
- `quant_ignored_modules`：默认豁免 `lm_head` 与 `gate`（MLP 门控），避免对敏感层引入精度损失。
- `quant_converters`：默认仅启用线性层 MX 量化；MoE 场景需追加 `quantize.moe.mx`。
- `enable_fsdp_low_precision_all_gather`：低精度通信总开关，默认开启。
- `fsdp_low_precision_all_gather_mode`：低精度 all-gather 模式，默认按需 (`on-demand`)。

### 表 2：`quant_recipe_name` 字段含义（原文）

| Field | Description |
|---|---|
| `scaling_strategy` | Scaling strategy, such as `dynamic` or `delayed`. |
| `scaling_granularity` | Scaling granularity, such as `mx` (the only supported option), `per_tensor`, or `per_channel`. |
| `blocksize0-blocksize1-blocksize2` | Optional block size, used only for block quantization. |
| `inputs_dtype` / `weight_dtype` / `grads_dtype` | Data types for inputs, weights, and gradients, such as `E4M3` and `E5M2`. |

**逐行解读：**
- `scaling_strategy`：缩放策略，原文举例 `dynamic`、`delayed`；并未指明 `mxfp8` 实际使用 `dynamic`。
- `scaling_granularity`：缩放粒度，`mx` 是当前**唯一支持**的选项；`per_tensor` / `per_channel` 仅作为示例枚举列出。
- `blocksize0-blocksize1-blocksize2`：可选项，仅在块式量化下生效，`mxfp8` 取 `1-1-32`。
- 末三段分别描述输入、权重、梯度的目标 dtype，原文以 `E4M3`、`E5M2` 为例。

### 表 3：低精度 All-Gather 模式（原文）

| Mode | Description |
|---|---|
| `on-demand` | Communicates only the weights needed for the forward or backward pass. |
| `all` | Communicates all weights in both the forward and backward passes. |

**逐行解读：**
- `on-demand`：按需通信，仅搬运当前 step 前/反向所需的权重，**通信量最小**，适合大多数训练场景。
- `all`：全集通信，前后向均搬运所有权重，**带宽开销更大**，但能保证权重可见性，与 recomputation 兼容。

---

## 【公式解读】

原文给出的"公式"是量化配方的**字符串命名规范**：

```
<scaling_strategy>_<scaling_granularity>[-blocksize0-blocksize1-blocksize2]_<inputs_dtype>_<weight_dtype>_<grads_dtype>
```

**符号逐项含义：**

| 符号 | 含义 |
|---|---|
| `scaling_strategy` | 缩放策略（如 `dynamic`、`delayed`） |
| `scaling_granularity` | 缩放粒度，当前唯一可用值为 `mx` |
| `-blocksize0-blocksize1-blocksize2` | 可选块尺寸三元组，仅在块量化时使用；如 `mxfp8` 取 `1-1-32` |
| `inputs_dtype` | 输入张量的目标精度（如 `E4M3`） |
| `weight_dtype` | 权重张量的目标精度（如 `E4M3`） |
| `grads_dtype` | 梯度张量的目标精度（如 `E4M3`） |

**对照示例**：`mxfp8 → dynamic_MX-1-1-32_E4M3_E4M3_E4M3`，即动态缩放 + MX 粒度 + 块尺寸 1-1-32 + 输入/权重/梯度均为 `E4M3`。

---

## 【关联】

- **FSDP2 后端**：本文是 FSDP2 系列文档的一篇，依赖 `--parallel.fsdp_implementation custom` 与 FSDP2 的参数分片机制，量化后的低精度权重必须经过正确的分片/聚合才能被消费。
- **EFSDP（Expert FSDP）**：文档 Notes 明确指出，启用 efsdp 时需配合 `--parallel.efsdp_shard_placement_fn shard_by_dim_0` 才能正确处理量化权重的分片与通信。
- **MoE 模型**：示例脚本同时使用 `quantize.linear.mx` 与 `quantize.moe.mx` 两种 converter，调用的是 `tests/tools/fsdp2/moe_hf_param_merge_experts.sh`，说明 MoE 专家模块走专门的量化路径。
- **Recomputation（重计算）**：与 `fsdp_low_precision_all_gather_mode` 直接耦合——一旦启用重计算，框架会自动切换为 `all` 模式。
- **Qwen3 MoE 30B 示例**：`examples/fsdp2/qwen3_moe/pretrain_qwen3_30b_4k_fsdp2_A3.yaml` 作为最小可运行端到端示例，串联起量化参数与 FSDP2 训练流程。
- **MX 量化策略体系**：当前唯一支持的 `scaling_granularity` 为 `mx`，文档预告后续会扩展更多策略/配方。
- 文档内未提供内部超链接。

---

## 【使用方法】

**最小启用示例**（原文 Example Script 节）：

```bash
QUANT_ARGS="
    --model.quant_recipe_name mxfp8 \
    --model.quant_format E4M3 \
    --model.quant_block_size 32 \
    --model.enable_fsdp_low_precision_all_gather \
    --model.quant_converters quantize.linear.mx quantize.moe.mx \
    --parallel.efsdp_shard_placement_fn shard_by_dim_0 \
    --parallel.fsdp_implementation custom
"

bash tests/tools/fsdp2/moe_hf_param_merge_experts.sh
torchrun $DISTRIBUTED_ARGS train_fsdp2.py \
    examples/fsdp2/qwen3_moe/pretrain_qwen3_30b_4k_fsdp2_A3.yaml \
    $QUANT_ARGS \
    | tee logs/pretrain_qwen3_moe_30b_a3b_4K_fsdp2_${TIMESTAMP}.log
```

**关键启用步骤**：
1. 设置 `--model.quant_recipe_name`（必填，如 `mxfp8`），按需覆写 `quant_format` / `quant_block_size`。
2. 通过 `--model.quant_apply_modules` 与 `--model.quant_ignored_modules` 圈定量化作用范围（支持通配符）。
3. MoE 模型追加 `--model.quant_converters quantize.moe.mx`，与 `quantize.linear.mx` 叠加使用。
4. 启用 `--model.enable_fsdp_low_precision_all_gather`，并按需选择 `--model.fsdp_low_precision_all_gather_mode`（默认 `on-demand`；启用 recomputation 时自动变 `all`）。
5. 若同时启用 efsdp，必须追加 `--parallel.efsdp_shard_placement_fn shard_by_dim_0`，否则量化权重的分片/通信不正确。
6. 将上述 `QUANT_ARGS` 直接追加到既有训练启动脚本即可生效。

> 文档未提供任何性能基准测试脚本或结果数字，因此"效果如何验证"未涉及。
