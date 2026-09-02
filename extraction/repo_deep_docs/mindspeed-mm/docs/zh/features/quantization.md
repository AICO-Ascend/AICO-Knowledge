# MindSpeed MM FSDP2后端低精度训练指南

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/quantization.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/quantization.md

# 深度解读：MindSpeed MM FSDP2 后端低精度训练指南

---

## 【定位】

这篇文档面向在 MindSpeedMM 框架下、基于 FSDP2 后端进行大规模多模态/大模型训练的用户，说明如何通过"量化配方 (QuantizationRecipe) + FSDP 低精度 all-gather"两条主线，把权重/激活/梯度降到 mxfp8 等低精度表示，从而**降低通信开销与显存占用**，同时保持模型精度。

---

## 【技术要点】

1. **核心机制是「量化配方 (Recipe) + 模块化量化转换器 (QuantizeConverter) + FSDP 低精度 all-gather」三件套**：用 `recipe_name` 选定缩放策略/粒度/数据类型，用 `quant_converters` 把 linear/MoE-GMM 接入量化算子，用 `enable_fsdp_low_precision_all_gather` 把跨卡权重通信从 bf16 降到 mxfp8。
2. **配方命名采用结构化模板**：`<scaling_strategy>_<scaling_granularity>[-blocksize0-blocksize1-blocksize2]_<inputs_dtype>_<weight_dtype>_<grads_dtype>`，例如 `mxfp8` = `dynamic_MX-1-1-32_E4M3_E4M3_E4M3`，原文明确"**当前仅支持 `mxfp8` 缩放策略**"。
3. **缩放粒度仅支持 `mx`**，理论上文档还列出 `per_tensor`、`per_channel`，但原文用括号注明"仅支持 mx"，其余粒度为预留字段；块大小 `1-1-32` 即 `blocksize0=1, blocksize1=1, blocksize2=32`，符合 MX-FP8 block-scaling 规范（每 32 元素一个缩放因子）。
4. **量化目标由模块级通配符控制**：`apply_modules='model.layers.{*}'` 默认覆盖全部 Transformer 层；`ignored_modules=['*lm_head','*gate']` 默认排除输出头与 MoE gate，原文以"*"前缀作为通配符语法（与 apply_modules 的 `{*}` 略有差异）。
5. **FSDP 低精度 all-gather 提供两种模式**：`on-demand`（按需通信当前层权重）和 `all`（前反向一次性通信全部权重），原文明确 "**若启用重计算，系统将自动切换为 'all' 模式**"，并警告 'all' 模式"通信量翻倍，相较 bf16 时间无明显变化，显存略增"。
6. **硬件与精度风险双重约束**：原文用 ⚠️ 标注两条硬限制——"**仅支持 950 机器，910B&C 不支持**"以及"低精度训练可能引起精度损失，建议谨慎使用"。

---

## 【关键机制与数据】

### 工作原理（基于原文复述，无臆造数字）

- **量化路径**：`recipe_name` 选择配方 → `quant_converters` 把指定子模块（如 `quantize.linear.mx` 对 linear、`quantize.moe.mx` 对 MoE-GMM）替换为量化算子 → 前向时输入/权重按 `inputs_dtype`/`weight_dtype` 量化，反向时梯度按 `grads_dtype` 反量化/再量化 → `apply_modules` / `ignored_modules` 用通配符裁剪作用范围。
- **通信路径**：FSDP2 在前向/反向的 all-gather 阶段不再通信 bf16 权重，而是通信 `weight_dtype`（mxfp8 即 E4M3）权重与 MX 缩放因子；当 `fsdp_low_precision_all_gather_mode='on-demand'` 时，仅按需拉取当前层权重；启用重计算时系统自动切到 `'all'`，即前向一次性拉完所有层权重。
- **MoE 兼容**：原文明确"**在 MoE 模型中可以同时使用 `quantize.linear.mx` 和 `quantize.moe.mx`**"，前者负责 FFN/Attention 的普通 linear，后者专门负责 MoE 专家的 GMM。

### 性能数据

**原文未给出具体数值化的性能对比（如吞吐加速比、显存节省百分比等），仅给出定性描述**："显著降低通信开销与内存占用"、"提升训练效率与显存利用率"、"适用于大模型训练场景"，以及' all '模式相对于 bf16 "**时间无明显变化**"和"**显存略增**"两个定性结论。

---

## 【表格解读】

### 表 1：参数概览（原文逐字还原）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `recipe_name` | str | mxfp8（必填） | 使用的量化配方名,同时也是使能量化的标识 |
| `apply_modules` | str | 'model.layers.{*}' | 应用量化的层或模块 |
| `ignored_modules` | str | '*lm_head'，'*gate' | 不应用量化的子模块列表 |
| `quant_converters` | str | 'quantize.linear.mx', 'quantize.moe.mx' | 使用的量化转换器列表,分别表示对linear线性层和moe里的gmm做量化 |
| `enable_fsdp_low_precision_all_gather` | bool | `True` | 是否启用低精度通信 |
| `fsdp_low_precision_all_gather_mode` | str | 'on-demand' | FSDP低精度all-gather，按需聚合前向或反向权重 |

**逐行解读**：
- `recipe_name` 是唯一**必填**项，且必须用预定义名（当前仅 `mxfp8`）；它同时承担"使能开关"角色——不填就等同于不开启量化。
- `apply_modules` 默认覆盖所有 Transformer 层，是典型大模型全量化策略；支持通配符便于灵活裁剪。
- `ignored_modules` 默认跳过 `lm_head`（输出头，精度敏感）和 `*gate`（MoE 路由门控，离散决策不宜量化），体现了"敏感模块保精度"的工程经验。
- `quant_converters` 把 linear 与 MoE-GMM 分成两类，因为 GMM 沿 token-专家维度的累加器行为与普通 linear 不同，需专用算子。
- `enable_fsdp_low_precision_all_gather` 默认开，**意味着只要用了 `recipe_name=mxfp8` 就自动打开低精度通信**，无需额外步骤。
- `fsdp_low_precision_all_gather_mode` 默认 `on-demand`，是带宽/显存友好的折中方案。

### 表 2：`recipe_name` 字段说明（原文逐字还原）

| 字段 | 说明 |
|------|------|
| `scaling_strategy` | 缩放策略，如 `dynamic`、`delayed` |
| `scaling_granularity` | 缩放粒度，如 `mx`（仅支持）、`per_tensor`、`per_channel` |
| `blocksize0-blocksize1-blocksize2` | 可选，块大小（仅用于块量化） |
| `inputs_dtype` / `weight_dtype` / `grads_dtype` | 输入、权重、梯度的数据类型，如 `E4M3`、`E5M2` |

**逐行解读**：
- `scaling_strategy` 当前实际生效的只有 `dynamic`（参见预定义配方 `dynamic_MX-...`），`delayed` 是为后续扩展预留。
- `scaling_granularity` 括号内"仅支持"指 **当前实现只支持 `mx`**，其余为字段占位。
- `blocksize` 仅在块量化时使用，对 `mxfp8` 而言取 `1-1-32`，对应 MX-FP8 的标准 32 元素块缩放。
- 三个 dtype 字段独立指定，允许前向用 E4M3、梯度用 E5M2 等组合，覆盖更广的精度-动态范围权衡。

### 表 3：`fsdp_low_precision_all_gather_mode` 模式说明（原文逐字还原）

| 模式 | 说明 |
|------|------|
| `on-demand` | 仅在前向或反向传播时，通信当前所需的权重 |
| `all` | 前向和反向均通信全部权重 |

**逐行解读**：
- `on-demand` 是默认模式，按层粒度 lazy 拉取，通信与计算尽量流水化，显存峰值低。
- `all` 是一次性把全部层权重拉到本地，**通信量约翻倍**（前向 + 反向均全量），与重计算 (recomputation) 兼容性最好，因为重计算会重做前向，需要随时能访问到全部权重。
- 文档特别警告：`all` 模式下"**AG 通信全部权重会造成通信量翻倍，时间相较 bf16 无明显变化；同时因需要通信缩放因子等必须参数，显存会有略微增长**"——即 `all` 模式主要是为兼容重计算而存在，本身并不带来额外加速收益。

---

## 【公式解读】

原文给出的"公式"实质上是一段**配方命名模板/伪语法**，逐字保留如下：

```
<scaling_strategy>_<scaling_granularity>[-blocksize0-blocksize1-blocksize2]_<inputs_dtype>_<weight_dtype>_<grads_dtype>
```

并给出**实例化样例**（原文逐字保留）：

```
mxfp8: dynamic_MX-1-1-32_E4M3_E4M3_E4M3
```

**符号含义与作用说明**（不臆造，仅依据原文字段定义）：

- `<scaling_strategy>`：缩放策略，可选 `dynamic`、`delayed` 等；`dynamic` 表示缩放因子在运行时按张量动态计算，实例中取 `dynamic`。
- `<scaling_granularity>`：缩放粒度，取值 `mx`/`per_tensor`/`per_channel`；实例取 `MX`，即 MX-FP8 block-scaling。
- `[-blocksize0-blocksize1-blocksize2]`：可选段，仅在块量化时填；实例中 `1-1-32` 表示块在三个维度上的尺寸（MX-FP8 标准为 `1×1×32`，沿最内层连续 32 个元素共享一个缩放因子）。
- `<inputs_dtype>` / `<weight_dtype>` / `<grads_dtype>`：分别表示**输入激活、权重、反向梯度**的低精度数据类型；实例统一取 `E4M3`（4-bit 指数 + 3-bit 尾数的 FP8 格式）。`E5M2` 作为另一可选值（更高动态范围、更低精度）被原文列出但本配方未采用。

整体上，该模板把"如何量化"这件事压缩成一个可读、可校验、可扩展的字符串，对应配置侧 `recipe_name` 单字段。

> 原文无数学公式（如损失函数、量化公式 $x_q = \mathrm{round}(x/s)\cdot s$ 等）出现。

---

## 【关联】

原文未提供任何文末内部链接（内部链接字段标注为"无"），但根据文档本身的内容可以梳理出以下**模块级依赖与协同关系**（均为原文显式提及）：

- **FSDP2 后端**：低精度 all-gather 是 FSDP2 的能力之一，因此本文档的适用前提是后端必须为 **FSDP2**（其他后端如 DDP/ZeRO 路径未在文档中涉及）。
- **重计算 (Recomputation / Gradient Checkpointing)**：`fsdp_low_precision_all_gather_mode` 在开启重计算时**自动从 `on-demand` 切到 `all'`，因此量化训练与重计算存在强耦合。
- **MoE 模块**：通过 `quantize.moe.mx` 转换器接入到 **MoE 专家的 GMM (Grouped GEMM)**，与普通 FFN 的 `quantize.linear.mx` 并存；`ignored_modules` 默认 `*gate` 也表明量化与 MoE 路由紧耦合。
- **transformer.layers 结构**：默认 `apply_modules='model.layers.{*}'` 直接依赖 MindSpeedMM 的 `model.layers.{*}` 命名约定；`ignored_modules` 中的 `*lm_head`、`*gate` 同样是上层模型结构的固定路径。
- **硬件平台**：受限于 **昇腾 950 机器**（910B&C 不支持），这意味着该特性依赖特定代次 NPU 的 FP8/MX 硬件算子。

---

## 【使用方法】

### 启用方式

在原有训练 YAML 配置的 `training` 字段下新增 `quantization_plan` 子块即可启用低精度训练与低精度通信，原文给出完整示例脚本（**逐字保留**）：

```yaml
training:
  quantization_plan:
    recipe_name: mxfp8
    apply_modules: ['model.layers.{*}']
    ignored_modules: ['*lm_head', '*gate']
    quant_converters: ['quantize.linear.mx', 'quantize.moe.mx']
    enable_fsdp_low_precision_all_gather: True
    fsdp_low_precision_all_gather_mode: 'on-demand'
```

### 关键配置项说明（基于原文）

- **`recipe_name: mxfp8`**：当前唯一支持的预定义配方，对应 `dynamic_MX-1-1-32_E4M3_E4M3_E4M3`；填写该字段即**同时充当使能开关**。
- **`apply_modules`**：使用 `{*}` 形式覆盖全部 Transformer 层；也支持精确路径如 `'model.layers.0.self_attn'`。
- **`ignored_modules`**：以 `*` 前缀通配符排除特定子模块，原文示例 `*q_proj`、`*gate`。
- **`quant_converters`**：列表形式，可同时启用 `quantize.linear.mx`（普通 linear）和 `quantize.moe.mx`（MoE-GMM），后者需在 MoE 模型中才有意义。
- **`enable_fsdp_low_precision_all_gather: True`**：开启 FSDP 低精度 all-gather。
- **`fsdp_low_precision_all_gather_mode: 'on-demand'`**：默认按需通信；如训练脚本中启用了重计算，则**框架会自动改用 `'all'`**，无需用户手动改。

### 注意事项（原文 ⚠️ 逐字摘录）

- ⚠️ **目前低精度训练相关功能仅支持在 950 机器上运行，910B&C 等机器不支持。**
- ⚠️ **低精度训练过程中可能引起精度损失，造成模型性能下降，非框架本身问题，建议谨慎使用。**
