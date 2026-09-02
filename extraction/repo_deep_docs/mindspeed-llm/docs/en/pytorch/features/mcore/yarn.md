# YaRN

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/yarn.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/yarn.md

【定位】  
本文介绍 YaRN：通过 `ntk-by-part` 分段调整 RoPE 位置编码，使采用 RoPE 的预训练大语言模型能够在推理时扩展上下文窗口，同时尽量保持序列扩展后的任务精度。

【技术要点】

- 传统 Transformer 在序列长度增长时，计算复杂度和显存复杂度均为 \(\mathrm{O}(n^2)\)，其中 \(n\) 为序列长度；因此，减少扩展上下文所需的微调、甚至无需微调，具有重要意义。
- YaRN 面向采用 RoPE（Rotary Positional Encoding）的模型，用于推理阶段的上下文扩展。原文明确其通过 `ntk-by-part` 调整位置编码，以改善序列扩展后的准确率。
- 对 token embedding 的 RoPE，位置编码 \(\theta\) 从较低维度到较高维度逐渐增大，同时频率逐渐降低。YaRN 对不同频率区域采用不同处理方式：
  - 高频部分直接进行外推；
  - 低频部分进行线性插值；
  - 两者之间的中间区域进行线性过渡。
- DeepSeek V2 系列通过 `--rope-scaling-type yarn` 启用 YaRN。
- 主要配置包括：
  - `--beta-fast`：高频旋转周期数，默认值为 `32`；
  - `--beta-slow`：低频旋转周期数，默认值为 `1`；
  - `--rope-scaling-factor`：上下文扩展因子，高频维度使用该因子进行外推。例如，预训练模型上下文为 `4K`、扩展到 `160K` 时，扩展因子为 `40`；
  - `--rope-scaling-mscale`：注意力缩放系数函数 `yarn_get_mscale` 的输入参数；
  - `--rope-scaling-mscale-all-dim`：注意力缩放系数函数 `yarn_get_mscale` 的输入参数；
  - `--rope-scaling-original-max-position-embeddings`：预训练模型扩展前的上下文长度。
- 原文仅给出了 MMLU/MMLU-STEM 准确率对比，未提供 YaRN 启用前后的训练损失、吞吐量、显存占用或延迟数据。

【关键机制与数据】

- 原文：Transformer 的计算和显存成本随序列长度按 \(\mathrm{O}(n^2)\) 增长，因此直接扩大上下文会迅速增加计算和显存开销。
- 原文：YaRN 的核心对象是 RoPE 位置编码。token embedding 在不同维度上的位置编码 \(\theta\) 和频率不同，低维到高维表现为 \(\theta\) 逐渐增大、频率逐渐降低。
- 原文：YaRN 不对所有维度使用单一缩放方式，而是将 RoPE 维度分成三类：高频部分直接外推，低频部分线性插值，中间部分线性过渡。
- 原文：上下文扩展因子 `40` 的含义是，预训练模型的 `4K` 上下文扩展到 `160K`；该因子用于高频维度的外推。原文没有说明低频插值和中间过渡各自对应的具体计算公式。
- 原文：`--beta-fast` 和 `--beta-slow` 分别控制高频、低频旋转周期；两个 `mscale` 参数传入 `yarn_get_mscale`，但原文没有给出 `yarn_get_mscale` 的实现公式、默认数值或不同取值对缩放系数的定量影响。
- 原文：采用默认 YaRN 配置后，DeepSeek-V2-Lite-16B、DeepSeek-Math-7B、DeepSeek-V2-236B 和 DeepSeek-V2.5 的对应任务准确率分别为 `57.4%`、`56.5%`、`78.1%` 和 `79.3%`。
- 原文：除 MMLU/MMLU-STEM 准确率外，文档没有给出性能或资源消耗方面的对比数据。

【表格解读】

原文表格如下：

| Model | Task | MindSpeed LLM | Community Version |
|------|------|---------------|-----------|
| DeepSeek-V2-Lite-16B | MMLU | 57.4% | [58.3%](https://huggingface.co/deepseek-ai/DeepSeek-V2-Lite) |
| DeepSeek-Math-7B | MMLU-STEM | 56.5% | [56.5%](https://github.com/deepseek-ai/DeepSeek-Math) |
| DeepSeek-V2-236B | MMLU | 78.1% | [78.5%](https://huggingface.co/deepseek-ai/DeepSeek-V2) |
| DeepSeek-V2.5 | MMLU | 79.3% | [80.6%](https://huggingface.co/deepseek-ai/DeepSeek-V2.5) |

逐行解读：

| 原文行 | 解读 |
|---|---|
| `DeepSeek-V2-Lite-16B | MMLU | 57.4% | [58.3%](https://huggingface.co/deepseek-ai/DeepSeek-V2-Lite)` | 使用默认 YaRN 配置后，MindSpeed LLM 的 MMLU 为 `57.4%`；社区版本为 `58.3%`。前者低于后者。 |
| `DeepSeek-Math-7B | MMLU-STEM | 56.5% | [56.5%](https://github.com/deepseek-ai/DeepSeek-Math)` | 两边在 MMLU-STEM 上均为 `56.5%`，结果一致。 |
| `DeepSeek-V2-236B | MMLU | 78.1% | [78.5%](https://huggingface.co/deepseek-ai/DeepSeek-V2)` | MindSpeed LLM 的 MMLU 为 `78.1%`，低于社区版本的 `78.5%`。 |
| `DeepSeek-V2.5 | MMLU | 79.3% | [80.6%](https://huggingface.co/deepseek-ai/DeepSeek-V2.5)` | MindSpeed LLM 的 MMLU 为 `79.3%`，低于社区版本的 `80.6%`。 |

整体来看，表格只比较默认 YaRN 配置下的任务准确率，不包含上下文长度、推理速度、显存、计算量或通信开销，因此只能说明相应任务精度表现，不能直接证明计算性能或资源效率。

【公式解读】

原文出现的复杂度公式为：

\[
\mathrm{O}(n^2)
\]

逐符号说明：

- `O`：渐近复杂度记号，表示输入规模变化时计算或存储成本的增长量级。
- `n`：序列长度，即输入 token 组成的序列中包含的 token 数量。
- `^2`：平方指数，表示计算复杂度和显存复杂度随序列长度呈平方增长。

因此，当序列长度增加时，计算与显存成本会快速上升。文档借此说明，需要通过 YaRN 等位置编码扩展技术来支持更长上下文，而不能只依赖序列长度的直接放大。

此外，原文还出现 RoPE 位置编码变量 `θ`：

- `θ`：rotary positional encoding，即旋转位置编码；它在不同维度上按相应频率变化，是 YaRN 区分高频、中频和低频并进行不同处理的基础。

原文没有给出 YaRN 的外推公式、插值公式、中间过渡公式，也没有给出 `yarn_get_mscale` 的函数表达式。

【关联】

- YaRN 位于位置编码与长上下文处理链路中，其直接作用对象是采用 RoPE 的预训练语言模型。
- DeepSeek V2 系列是文档给出的具体集成对象，通过 DeepSeek V2 配置启用 YaRN。
- `--rope-scaling-mscale` 和 `--rope-scaling-mscale-all-dim` 将注意力缩放相关的控制参数传给 `yarn_get_mscale`，说明 YaRN 的上下文扩展不仅改变位置编码维度，还与注意力缩放系数存在配置关联；原文未进一步说明其内部计算关系。
- `--beta-fast`、`--beta-slow`、`--rope-scaling-factor` 和 `--rope-scaling-original-max-position-embeddings` 共同描述频率边界与上下文扩展所需的基础信息。
- 原文没有内部链接，因此没有其他文内特性、模块或上下游页面可直接关联。表格中的 Hugging Face 和 GitHub 链接属于社区版本的外部数据来源，不是文内功能模块链接。

【使用方法】

适用于使用 RoPE 位置编码、需要在推理阶段扩展上下文长度的模型。文档以 DeepSeek V2 系列配置为例。

```bash
--rope-scaling-type yarn
```

相关配置项：

```text
--beta-fast
--beta-slow
--rope-scaling-factor
--rope-scaling-mscale
--rope-scaling-mscale-all-dim
--rope-scaling-original-max-position-embeddings
```

参数说明：

- `--beta-fast`：高频旋转周期数，默认值为 `32`。
- `--beta-slow`：低频旋转周期数，默认值为 `1`。
- `--rope-scaling-factor`：上下文扩展因子。预训练上下文为 `4K`、目标上下文为 `160K` 时，该因子为 `40`。
- `--rope-scaling-mscale`：`yarn_get_mscale` 的输入参数。
- `--rope-scaling-mscale-all-dim`：`yarn_get_mscale` 的输入参数。
- `--rope-scaling-original-max-position-embeddings`：模型扩展前的上下文长度。

原文未提供完整的模型启动命令，也未为 `--rope-scaling-mscale`、`--rope-scaling-mscale-all-dim` 和 `--rope-scaling-original-max-position-embeddings` 给出具体配置示例。

## 图文联合解读

- `position_embedding.png`: **图文联合解读：**

图示绘制了RoPE位置编码的多维正弦波：横轴为位置t(0-512)，纵轴为d_model各维度。顶部低维度呈高频密集振荡，底部高维度趋近直线(频率趋零)，并在t=192、336两处用青框标注了各维度的具体编码值。

技术结论：RoPE各维度频率从高到低分布，周期从小于1到远大于1覆盖全频段，单一外推/插值策略无法兼顾。

与文档关系：直观支撑YaRN"ntk-by-part"分段策略——高频维度直接外推、低频维度线性插值、中间段平滑过渡的必要性。
- `ntk_by_parts.png`: **图文联合解读：**

**1) 图中内容：** 定义比值 r = L/λ 表示预训练长度与波长关系；定义斜坡函数 γ(rᵢ) 为三段分段函数（>β 区域为1，α~β 区间线性过渡，<α 区域为0）；给出调整后旋转角公式 h(θᵢ) = [1-γ(rᵢ)]·θᵢ/s + γ(rᵢ)·θᵢ，其中 s = L'/L 为缩放因子。

**2) 技术结论：** YaRN 将 RoPE 各维度按频率分为三段处理——高频维度外推（保持原样）、低频维度线性内插、中间维度平滑过渡，从而在不重新训练的前提下扩展上下文窗口。

**3) 与文档关系：** 该公式即为文档所述"ntk-by-part"位置编码调整的数学实现，是 YaRN 扩展上下文长度的核心机制。
