# Anti-Outlier 离群值抑制

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/anti_outlier.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/anti_outlier.md

# Anti-Outlier 离群值抑制 文档深度解读

## 【定位】
本文档介绍昇腾自研大模型推理引擎 mindie-llm 中 **Anti-Outlier（离群值抑制）** 特性，旨在解决大模型量化过程中因激活值分布出现极端离群点而拉大量化 Scale、导致正常数值量化分辨率下降、最终引起模型精度损失的问题，使量化后的模型仍能保持较高推理精度。

---

## 【技术要点】

1. **核心目标**：针对激活值中存在数值极大的异常值（Outlier）拉大量化区间、降低量化分辨率这一现象，通过平滑/抑制离群值来改善数据分布，从而保全量化精度。
2. **可与多种量化方式组合**：原文明确 Anti-Outlier 可配合 **W4A8、W8A8、W8A8C8** 等量化方式一起使用，并以 **W8A8 + Anti-Outlier + PDMIX** 为示例展示 `quant_model_description.json` 的内容。
3. **非对称离群值抑制算法引入 norm_bias**：针对主流使用 RmsNorm 作为 `input_layernorm` 与 `post_attention_layernorm` 的开源大模型（如 LLaMA、Qwen 系列），启用非对称离群值抑制时会引入额外偏置项 `norm_bias`。
4. **计算等价性的两步抵消逻辑**：
   - **Norm 层引入**：执行 Norm 操作时将 `norm_bias` 加到权重中。
   - **Linear 层抵消**：随后 Linear 层计算前将对应的 `norm_bias` 减去。
5. **不同量化场景下的融合方式**：
   - **Per-tensor 场景**：`norm_bias` 直接融合进 Linear 层的量化偏置 `quant_bias`（如 `q_proj.quant_bias`）。
   - **Per-token 场景**：`norm_bias` 体现为 Linear 层的普通偏置 `bias`（如 `q_proj.bias`）。
6. **PDMIX 场景下的性能优化建议**：在 PDMIX 场景（P 阶段使用 Per-token 量化）下，离群值抑制的 bias 对量化精度影响较小，可在保证等价性前提下同时移除 Norm 层与 Linear 层的 Bias，从而节省一次 Add 计算开销。
7. **原始 Linear 层 Bias 状态决定融合策略**：
   - 原 Linear 层已有 Bias（如 Qwen2 系列）：直接融合进原有 Bias。
   - 原 Linear 层无 Bias（如 Qwen3-32B）：新建一个 Bias 层来存储该值。

---

## 【关键机制与数据】

**工作原理（数据流 / 算子改造）**

原文所述执行逻辑（按推理顺序）：

1. **量化权重反量化阶段（参考图 1：量化权重推理时流程）**
   - 加载由 msModelSlim 工具生成的量化权重。
   - 对 `weight` / `quant_bias` / `input_scale` / `weight_offset` 等以 `W8A8_MIX` 标识的张量做反量化与 Linear 计算。
   - Norm 层（如 `input_layernorm.weight`、`post_attention_layernorm.weight`）仍以 `FLOAT` 形式保存。

2. **norm_bias 的引入与抵消**
   - 原文：*"在执行Norm操作时，将`norm_bias`加到权重中"* → 即 Norm 阶段完成 +norm_bias。
   - 原文：*"在随后的Linear层计算前，将对应的`norm_bias`减去"* → 即 Linear 阶段完成 -norm_bias。
   - 两者数学上等价，物理上通过 Bias 张量吸收到 Linear 的 `quant_bias`（Per-tensor）或 `bias`（Per-token）。

3. **PDMIX 场景下的可选优化**
   - 原文：*"在PDMIX场景（P阶段使用Per-token量化）下，离群值抑制的bias对量化精度的影响通常较小"* → 因此原文建议 *"在保证等价性的前提下，在Norm层和Linear层同时移除Bias"* 来 *"节省一次Add计算开销"*。
   - 注意原文并未给出具体节省的数值（未提供 ms、% 等性能数字）。

4. **原始权重的 dtype/shape 信息（表 1 原文）**
   - 假设原始权重 shape 为 `[n]`，则 `input_layernorm.bias` 与 `post_attention_layernorm.bias` 的 dtype 均为 `fp32`，shape 均为 `[n]`。
   - 原文未给出具体数值规模（如隐藏维度 n 的取值）。

> 性能数据：原文未提供具体的加速比、显存节省、精度提升百分比等数字指标，仅以"性能优化建议"形式给出方向性建议。

---

## 【表格解读】

**表 1：权重量化后部分层的 dtype 及 shape 信息（假设原始权重的 shape 为 `[n]`）**

| Tensor 信息 | input_layernorm.bias | post_attention_layernorm.bias |
|---|---|---|
| dtype | fp32 | fp32 |
| shape | [n] | [n] |

**逐行解读**：

- **dtype 行（fp32 / fp32）**：两个 Norm 层的 Bias 张量在量化后仍保持 **fp32** 高精度存储，而未走 `W8A8_MIX` 等低精度量化路径。这说明 Norm 层 Bias 在 Anti-Outlier 机制中需要保留高精度，以确保 norm_bias 引入/抵消的计算等价性。
- **shape 行（[n] / [n]）**：两个 Bias 的形状与原始权重 shape 一致为 `[n]`，即与对应 Norm 层权重维度对齐；这意味着 `norm_bias` 在 Norm 阶段是逐通道（per-channel）加到权重上的。
- **表 1 适用范围（原文：*"假设原始权重的shape为 `[n]`"*）**：原文明确该表给出的是 "部分层" 的示例信息，针对的是引入 norm_bias 后的 Norm 层 Bias，并未列出 Linear 层的 `quant_bias`、`weight_offset`、`input_scale` 等 `W8A8_MIX` 标识的张量。

原文另含一段 JSON 示例（位于 "特性简介" 段），并非传统表格，附 markdown 表格化逐字还原如下：

**表 1-附：`quant_model_description.json` 部分内容（W8A8 + Anti-Outlier + PDMIX 示例）**

| 键 (Tensor 名) | 值 (量化方式) |
|---|---|
| model.layers.0.self_attn.q_proj.weight | W8A8_MIX |
| model.layers.0.self_attn.q_proj.bias | FLOAT（optional） |
| model.layers.0.self_attn.q_proj.quant_bias | W8A8_MIX |
| model.layers.0.self_attn.q_proj.input_scale | W8A8_MIX |
| model.layers.0.mlp.down_proj.weight_offset | W8A8_MIX |
| model.layers.0.input_layernorm.weight | FLOAT |
| model.layers.0.input_layernorm.bias | FLOAT（optional） |
| model.layers.0.post_attention_layernorm.weight | FLOAT |
| model.layers.0.post_attention_layernorm.bias | FLOAT（optional） |

**解读**：Linear 层的 `weight` 与 `quant_bias`/`input_scale`/`weight_offset` 均以 `W8A8_MIX` 量化；而 Norm 层（`input_layernorm` / `post_attention_layernorm`）的 `weight` 和 `bias` 保持 `FLOAT`，印证了表 1 的结论。

---

## 【公式解读】

原文无 LaTeX 数学公式或伪代码公式。原文以文字描述形式给出了等价变换的执行逻辑（Norm 加 bias / Linear 减 bias），可视为隐式的"等价恒等式"：

```
Norm(x) + norm_bias ≡ Norm(x)        // 偏置吸收到下游 Linear.bias / quant_bias 中
Linear(x, W, B + norm_bias)          // Linear 层减去 norm_bias 实现抵消
```

原文未提供显式公式、无 $...$ 或代码块形式的数学表达，故按要求标注 **"原文无公式"**。

---

## 【关联】

1. **上游量化工具**：原文指向 `https://gitcode.com/Ascend/msit/blob/master/msmodelslim/README.md`（**msModelSlim** 工具），由其负责生成带有离群值抑制的量化权重；mindie-llm 仅负责消费其产物（`quant_model_description.json` + 量化权重目录）。
2. **可组合的量化方式**：原文列出了 **W4A8、W8A8、W8A8C8** 以及 **PDMIX**，表明 Anti-Outlier 是一类"量化前处理/校准手段"，与具体位宽和 PD 分离/混合策略正交叠加。
3. **依赖的 Norm 类型**：原文强调针对使用 **RmsNorm**（即 LLaMA、Qwen 等）的模型生效；隐含未覆盖 LayerNorm 系（如 BERT 系）的相关说明。
4. **下游推理执行**：原文给出推理命令 `examples.run_pa`（`torchrun --nproc_per_node 2 ... -m examples.run_pa --model_path ...`），说明 Anti-Outlier 量化权重由 `atb_speed`（`ATB_SPEED_HOME_PATH`）框架加载执行。
5. **文档互引**：原文末尾"内部链接: (无)"表明本文档在仓库内未挂接其他关联文档链接。

---

## 【使用方法】

### 一、生成带有 Anti-Outlier 的量化权重

使用 msModelSlim 工具，以 Qwen3-14B 为例：

```sh
msmodelslim quant --model_path {浮点权重路径} --save_path {量化权重路径} --device npu --model_type Qwen3-14B --quant_type w8a8 --trust_remote_code True
```

- `--quant_type w8a8`：原文使用 W8A8 作为示例；如需 W4A8、W8A8C8 等组合，请参考 msModelSlim 工具文档。
- 原文：*"执行上述命令会默认使用msModelSlim工具的最佳实践方式执行量化"*。
- 更详细的量化参数配置：参考 msModelSlim 工具文档（链接见上）。

### 二、执行推理

以 Qwen3-14B-W8A8PDMIX 权重为例，使用以下命令执行对话测试（原文示例：输入 "What's deep learning?"，最长输出 20 token）：

```bash
cd ${ATB_SPEED_HOME_PATH}
torchrun --nproc_per_node 2 --master_port 12350 -m examples.run_pa --model_path {量化权重路径}
```

### 三、配置/启用项

- 原文未提供独立的开关配置文件或环境变量；启用 Anti-Outlier 的方式即在 **量化阶段** 通过 msModelSlim 工具以"最佳实践"方式生成（默认即包含 Anti-Outlier）。
- 性能优化开关（PDMIX 下同时移除 Norm 层与 Linear 层的 Bias）原文以"建议"形式给出，**未提供具体配置项或环境变量名称**。

> 备注：文档中提及了图 1（量化权重推理时流程），原文为 `![](./figures/anti_outlier_quantization.png "量化权重推理时流程-5")`，仅给出文件名与标题，未给出图内可量化的标注数据，故按"原文提供图片标题、未给出图片内数据"处理，不作额外推断。

## 图文联合解读

- `anti_outlier_quantization.png`: **图示内容**：数据流从左至右——float16/bfloat16激活值经"Norm离群值处理"后仍保持高精度，再量化成int8，与int8权重做MatMul+反量化，最终结果还原为float16/bfloat16。

**论证结论**：离群值抑制必须在量化前的高精度域（Norm层）完成，先抑制异常值再量化为int8，可避免离群点拉偏量化Scale，保留正常数值的量化分辨率。

**与文档关系**：对应文档"Norm层引入norm_bias"步骤，直观呈现Anti-Outlier在W8A8场景下"前置Norm高精度处理+后置Linear抵消"的等效计算流程。
