# MindSpeed LLM FSDP2后端低精度训练指南

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/fsdp2/quantization.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/fsdp2/quantization.md

# MindSpeed LLM FSDP2 后端低精度训练文档深度解读

## 【定位】

本文档是 MindSpeed LLM 框架下 **基于 FSDP2 后端实现低精度训练（如 mxfp8 等）** 的使用指南，通过配置量化配方（QuantizationRecipe）与低精度 all-gather 模式，在保持模型精度的前提下降低通信开销与显存占用，服务于大模型训练场景。

---

## 【技术要点】

1. **量化配方（Quantization Recipe）驱动低精度训练**：核心开关为 `--model.quant_recipe_name`，文档标注其为 **必填项**，默认值为 `mxfp8`，通过命名规则 `<scaling_strategy>_<scaling_granularity>[-blocksize0-blocksize1-blocksize2]_<inputs_dtype>_<weight_dtype>_<grads_dtype>` 完整描述缩放策略、粒度、块大小与三种数据精度。

2. **MX 缩放策略为当前唯一支持项**：文档明确警告"当前仅支持 `MX` 缩放策略，后续将支持更多策略与配方"，`scaling_granularity` 字段虽列出 `mx` / `per_tensor` / `per_channel` 三种取值，但实际可用范围受限于 MX。

3. **分块量化块大小可调**：通过 `--model.quant_block_size` 控制，默认值为 **`32`**（MXFP8 分块量化块大小），与配方中的 `blocksize0-blocksize1-blocksize2` 字段对应。

4. **FP8 数据格式三选一**：通过 `--model.quant_format` 指定，默认 `E4M3`，支持 `E4M3` / `E5M2` / `HIF8` 三种 FP8 数据格式，分别对应输入/权重/梯度的精度（`inputs_dtype` / `weight_dtype` / `grads_dtype`）。

5. **量化范围通过通配符精确控制**：通过 `--model.quant_apply_modules`（默认 `model.layers.{*}`）与 `--model.quant_ignored_modules`（默认 `*lm_head` `*gate`）配合，支持按层或子模块粒度启用/排除量化。

6. **专用量化转换器支持 MoE 模型**：通过 `--model.quant_converters` 指定（默认 `quantize.linear.mx`），文档提示 MoE 模型可同时使用 `quantize.linear.mx`（普通线性层）与 `quantize.moe.mx`（专家模块）两种转换器。

7. **低精度 all-gather 通信**：通过 `--model.enable_fsdp_low_precision_all_gather`（bool，默认 `True`）启用 FSDP 低精度 all-gather 模式，并以 `--model.fsdp_low_precision_all_gather_mode`（默认 `on-demand`）控制通信粒度——`on-demand` 按需聚合当前层权重，`all` 则前向/反向均通信全部权重。

---

## 【关键机制与数据】

### 工作原理（原文摘述）

- **量化配方机制**：通过 `quant_recipe_name` 命名规则，将缩放策略、缩放粒度、块大小、输入/权重/梯度数据类型整合为一个字符串标识，框架据此构造量化器。原文给出预定义配方：`mxfp8` 对应 `dynamic_MX-1-1-32_E4M3_E4M3_E4M3`，即采用 `dynamic` 缩放策略 + `MX` 粒度 + 1×1×32 块大小 + 三种张量均使用 `E4M3` 格式。

- **低精度 all-gather 通信机制**：原文指出"启用后，在前向/反向传播中，FSDP 会以低精度权重（如 mxfp8）进行参数的 all-gather 操作，显著降低通信开销和内存占用"。文档强调在已开启低精度训练的基础上，可"进一步启用该模式以最大化效率提升"。

- **量化应用/排除机制**：通过通配符路径匹配实现选择性量化。原文示例：`'model.layers.{*}'`（所有 Transformer 层）、`'model.layers.0.self_attn'`（第 0 层自注意力）、`'*q_proj'`（排除所有 q_proj）、`'*gate'`（排除 MLP gate 部分）。

- **重计算的耦合行为**：原文"若启用重计算，系统将自动切换为 'all' 模式，确保计算一致性"，说明低精度通信模式会随重计算开关自适应调整。

- **efsdp 与量化的耦合约束**：原文注意事项"在开启 efsdp 时，由于底层框架的限制，`efsdp_shard_placement_fn` 需要设置为 `shard_by_dim_0`，以确保量化权重的正确切分与通信"。

### 性能数据

> **原文未提供量化前后的吞吐/显存对比数据**，仅以定性描述"显著降低通信开销与内存占用"。

---

## 【表格解读】

### 表 1：低精度训练参数概览

| 参数 | 类型 | 默认值 | 说明 |
|------|------|------|------|
| `--model.quant_recipe_name` | str | mxfp8（必填） | 使用的量化配方名 |
| `--model.quant_format` | str | `E4M3` | 量化使用的 FP8 数据格式，支持 `E4M3`、`E5M2`、`HIF8` |
| `--model.quant_block_size` | int | `32` | MXFP8 分块量化块大小 |
| `--model.quant_apply_modules` | str | 'model.layers.{*}' | 应用量化的层或模块 |
| `--model.quant_ignored_modules` | str | '*lm_head' '*gate' | 不应用量化的子模块列表 |
| `--model.quant_converters` | str | 'quantize.linear.mx' | 使用的量化转换器列表 |
| `--model.enable_fsdp_low_precision_all_gather` | bool | `True` | 是否启用低精度通信 |
| `--model.fsdp_low_precision_all_gather_mode` | str | 'on-demand' | FSDP低精度all-gather，按需聚合前向或反向权重 |

**逐行解读**：
- **quant_recipe_name**：整个低精度训练的唯一强制入口，决定采用何种缩放策略与数据格式。
- **quant_format**：默认 `E4M3` 是 FP8 中动态范围与精度较均衡的格式，`E5M2` 动态范围更大但精度更低，`HIF8` 是文档支持但未在预定义配方示例中出现的第三种 FP8 变体。
- **quant_block_size=32**：与配方中的 `blocksize2=32` 对应，是 MX 格式标准块大小。
- **quant_apply_modules='model.layers.{*}'**：默认量化所有 Transformer 层，符合大模型训练中"decoder 层计算量最大"的直觉。
- **quant_ignored_modules='*lm_head' '*gate'**：默认保留 LM 头与 MoE/MLP gate 部分不量化，体现"输出层与路由层对精度更敏感"的设计权衡。
- **quant_converters='quantize.linear.mx'**：默认使用通用线性层 MX 量化器，MoE 场景需要追加 `quantize.moe.mx`。
- **enable_fsdp_low_precision_all_gather=True**：默认即开启低精度通信，反映该能力在 FSDP2 训练路径中是"开箱即用"的标配优化。
- **fsdp_low_precision_all_gather_mode='on-demand'`**：默认按需通信，节省带宽；与重计算冲突时自动升级为 `all`。

### 表 2：quant_recipe_name 字段含义

| 字段 | 说明 |
|------|------|
| `scaling_strategy` | 缩放策略，如 `dynamic`、`delayed` |
| `scaling_granularity` | 缩放粒度，如 `mx`（仅支持）、`per_tensor`、`per_channel` |
| `blocksize0-blocksize1-blocksize2` | 可选，块大小（仅用于块量化） |
| `inputs_dtype` / `weight_dtype` / `grads_dtype` | 输入、权重、梯度的数据类型，如 `E4M3`、`E5M2` |

**逐行解读**：
- **scaling_strategy**：决定量化缩放因子（scale factor）的计算时机，`dynamic` 表示前向时即时计算，`delayed` 表示延迟更新；原文只展示了这两种。
- **scaling_granularity**：决定 scale 的共享范围，`mx` 当前唯一可用，`per_tensor` / `per_channel` 文档列出但未支持。
- **blocksize0-blocksize1-blocksize2**：可选字段，仅块量化生效；预定义配方 `mxfp8` 取 `1-1-32`，意味着最后一维按 32 元素分块。
- **三种 dtype 字段**：允许输入、权重、梯度使用不同 FP8 格式以平衡精度与范围，但预定义 `mxfp8` 配方三者统一为 `E4M3`。

### 表 3：低精度 all-gather 模式

| 模式 | 说明 |
|------|------|
| `on-demand` | 仅在前向或反向传播时，通信当前所需的权重 |
| `all` | 前向和反向均通信全部权重 |

**逐行解读**：
- **`on-demand`**：通信粒度最细，仅按需取当前计算层权重，节省带宽但可能引入额外的同步开销。
- **`all`**：一次性通信所有层权重，通信粒度粗但计算流水更顺；原文明确当重计算开启时系统强制使用此模式。

---

## 【公式解读】

原文给出 `quant_recipe_name` 的格式定义（伪代码形式）：

```
<scaling_strategy>_<scaling_granularity>[-blocksize0-blocksize1-blocksize2]_<inputs_dtype>_<weight_dtype>_<grads_dtype>
```

**符号逐项说明**：

| 占位符 | 含义 | 取值/示例 |
|--------|------|----------|
| `scaling_strategy` | 缩放因子更新策略 | `dynamic`（即时计算）、`delayed`（延迟更新） |
| `scaling_granularity` | 缩放因子共享粒度 | `mx`（当前唯一支持）、`per_tensor`、`per_channel` |
| `blocksize0` | 第 0 维块大小（可选） | `mxfp8` 配方中取 `1` |
| `blocksize1` | 第 1 维块大小（可选） | `mxfp8` 配方中取 `1` |
| `blocksize2` | 第 2 维块大小（可选） | `mxfp8` 配方中取 `32` |
| `inputs_dtype` | 输入张量数据类型 | `E4M3`、`E5M2`、`HIF8` |
| `weight_dtype` | 权重张量数据类型 | `E4M3`、`E5M2`、`HIF8` |
| `grads_dtype` | 梯度张量数据类型 | `E4M3`、`E5M2`、`HIF8` |

**实例**：`mxfp8` → `dynamic_MX-1-1-32_E4M3_E4M3_E4M3`，含义为采用 `dynamic` 策略 + `MX` 粒度 + 三维块大小 1×1×32 + 输入/权重/梯度均使用 `E4M3` 格式。

> 原文无其他数学公式。

---

## 【关联】

文档未提供内部链接，但根据正文内容可识别以下关联关系：

- **FSDP2 后端**：本文档所有功能均建立在 `train_fsdp2.py` 启动入口与 `examples/fsdp2/qwen3_moe/pretrain_qwen3_30b_4k_fsdp2_A3.yaml` 配置之上，依赖 FSDP2 的分片机制。
- **`efsdp_shard_placement_fn`（来自 efsdp 特性）**：文档在注意事项中显式约束——开启 efsdp 时必须将 `efsdp_shard_placement_fn` 设置为 `shard_by_dim_0`，二者构成强耦合。
- **重计算（Recomputation）**：与 `fsdp_low_precision_all_gather_mode` 存在自动切换关系（开启重计算 → 强制 `all` 模式）。
- **MoE 模型支持**：通过 `quantize.moe.mx` 转换器与 `examples/fsdp2/qwen3_moe/` 示例目录体现，本特性与大模型 MoE 训练路径直接绑定。
- **`quant_converters` 模块**：作为量化转换器注册入口，目前内置 `quantize.linear.mx` 与 `quantize.moe.mx` 两个实现，属于本特性的可扩展点。

---

## 【使用方法】

### 启用方式

在原有 FSDP2 训练脚本基础上追加 `QUANT_ARGS` 环境变量即可，完整示例（原文摘录）：

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

torchrun $DISTRIBUTED_ARGS train_fsdp2.py \
    examples/fsdp2/qwen3_moe/pretrain_qwen3_30b_4k_fsdp2_A3.yaml \
    $QUANT_ARGS \
    | tee logs/pretrain_qwen3_moe_30b_a3b_4K_fsdp2_${TIMESTAMP}.log
```

### 关键配置项分类汇总

- **必填项**：`--model.quant_recipe_name`（如 `mxfp8`）
- **量化精度控制**：`--model.quant_format`（`E4M3` / `E5M2` / `HIF8`）、`--model.quant_block_size`（默认 32）
- **量化范围控制**：`--model.quant_apply_modules`（默认 `model.layers.{*}`）、`--model.quant_ignored_modules`（默认 `*lm_head` `*gate`）
- **量化转换器**：`--model.quant_converters`（默认 `quantize.linear.mx`，MoE 场景追加 `quantize.moe.mx`）
- **低精度通信开关**：`--model.enable_fsdp_low_precision_all_gather`（默认 `True`）
- **低精度通信模式**：`--model.fsdp_low_precision_all_gather_mode`（默认 `on-demand`，可选 `all`）
- **efsdp 配套设置**：`--parallel.efsdp_shard_placement_fn shard_by_dim_0`、`--parallel.fsdp_implementation custom`

### 注意事项（原文摘录）

- 开启 efsdp 时，`efsdp_shard_placement_fn` 必须设置为 `shard_by_dim_0`，以确保量化权重的正确切分与通信。
- 启用重计算时，系统会自动将 `fsdp_low_precision_all_gather_mode` 切换为 `all`，无需手动干预。
