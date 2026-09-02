# YaRN

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/mcore/yarn.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/mcore/yarn.md

# mindspeed-llm 文档深度解读：YaRN 特性

## 【定位】

本文档介绍 YaRN（Yet another RoPE extensioN）位置编码扩展技术，用于在不进行（或仅少量）微调的前提下，将基于 RoPE 位置编码的大语言模型推理上下文窗口动态扩展，并给出在 DeepSeek-V2 系列上的使能参数与 MMLU 精度对照数据。

---

## 【技术要点】

- **问题背景**：传统 Transformer 的计算/内存复杂度为 O(n²)（n 为序列长度），随着上下文窗口扩张而急剧增长；预训练时设定的最大序列长度构成主要瓶颈。
- **核心机制**：YaRN 采用 **NTK-by-parts** 方式对 RoPE 旋转位置编码 θ 进行分段处理——高频维度直接外推（extrapolation），低频维度做线性插值（interpolation），中间过渡区采用线性插值。
- **RoPE 频率分布特征**：θ 维度从低维到高维逐渐变大，对应频率逐渐变低；高频部分周期数远大于 1，低频部分周期数不到 1。
- **使能开关**：通过命令行参数 `--rope-scaling-type yarn` 启用。
- **关键配套参数**：包括 `--beta-fast`（默认 32，高频周期数）、`--beta-slow`（默认 1，低频周期数）、`--rope-scaling-factor`（上下文扩展倍数，外推时作用于高频维度）、`--rope-scaling-mscale` 与 `--rope-scaling-mscale-all-dim`（注意力缩放系数函数 `yarn_get_mscale` 的入参）、`--rope-scaling-original-max-position-embeddings`（预训练模型未扩展时的上下文长度）。
- **适用范围**：原文明确"使用 RoPE 作为位置编码的模型，在推理时均可使用 YaRN 来扩展上下文长度"。

---

## 【关键机制与数据】

**位置编码扩展的工作原理（原文描述）：**

1. 对于 token embedding，旋转位置编码 θ 在不同维度上的频率分布呈"低维→高频，高维→低频"特征。
2. 根据周期数（wavelength）的多少把维度划分为三段：
   - **高频段**：周期数远大于 1 → 直接外推（不修改），保持训练时学到的相对位置关系。
   - **低频段**：周期数不到 1 → 线性插值，避免外推导致的训推不一致。
   - **中间段**：进行线性插值过渡，保证连续性。
3. 注意力侧另由 `yarn_get_mscale` 函数计算缩放系数，参数通过 `--rope-scaling-mscale` 与 `--rope-scaling-mscale-all-dim` 控制，用于在扩展上下文后稳定注意力分布。

**性能/精度数据（原文 MMLU 表）：**

| 模型 | 任务 | MindSpeed-LLM | 社区 |
|---|---|---|---|
| DeepSeek-V2-Lite-16B | MMLU | 57.4% | 58.3% |
| DeepSeek-Math-7B | MMLU-STEM | 56.5% | 56.5% |
| DeepSeek-V2-236B | MMLU | 78.1% | 78.5% |
| DeepSeek-V2.5 | MMLU | 79.3% | 80.6% |

数据均以"使用 DeepSeek-V2 系列的 YaRN 默认配置"为前提。

---

## 【表格解读】

### 表 1：YaRN 配置参数表

| 参数 | 说明 |
|---|---|
| `--beta-fast` | 高频旋转周期数，默认值为 32 |
| `--beta-slow` | 低频旋转周期数，默认值为 1 |
| `--rope-scaling-factor` | 上下文扩展倍数，用于高频维度外推。例如，预训练模型的上下文长度为 4K，扩展到 160K 时，该值为 40 |
| `--rope-scaling-mscale` | 注意力缩放系数函数 `yarn_get_mscale` 的入参 |
| `--rope-scaling-mscale-all-dim` | 注意力缩放系数函数 `yarn_get_mscale` 的入参 |
| `--rope-scaling-original-max-position-embeddings` | 预训练模型未扩展时的上下文长度 |

**逐行解读：**
- `--beta-fast`：定义 NTK-by-parts 中"高频段"的下限阈值（周期数），默认 32，低于此值的维度被划入插值区。
- `--beta-slow`：定义"低频段"的上限阈值（周期数），默认 1，高于此值的维度被划入外推区；与 `--beta-fast` 共同划出三段区间。
- `--rope-scaling-factor`：上下文扩展倍数，原文给出 4K → 160K（即 ×40）的具体例子，且明确该因子"用于高频维度外推"。
- `--rope-scaling-mscale`：作为 `yarn_get_mscale` 函数的入参，影响注意力缩放系数大小。
- `--rope-scaling-mscale-all-dim`：同为 `yarn_get_mscale` 的入参，从命名推测与"是否对所有维度应用 mscale"相关，但原文未给出其具体语义差别。
- `--rope-scaling-original-max-position-embeddings`：原始预训练上下文长度，作为计算扩展倍数的基准。

### 表 2：MMLU 精度对照表

| 模型 | 任务 | MindSpeed-LLM | 社区 |
|---|---|---|---|
| DeepSeek-V2-Lite-16B | MMLU | 57.4% | [58.3%](https://huggingface.co/deepseek-ai/DeepSeek-V2-Lite) |
| DeepSeek-Math-7B | MMLU-STEM | 56.5% | [56.5%](https://github.com/deepseek-ai/DeepSeek-Math) |
| DeepSeek-V2-236B | MMLU | 78.1% | [78.5%](https://huggingface.co/deepseek-ai/DeepSeek-V2) |
| DeepSeek-V2.5 | MMLU | 79.3% | [80.6%](https://huggingface.co/deepseek-ai/DeepSeek-V2.5) |

**逐行解读：**
- **DeepSeek-V2-Lite-16B / MMLU**：MindSpeed-LLM 57.4% vs 社区 58.3%，差距 0.9 个百分点。
- **DeepSeek-Math-7B / MMLU-STEM**：MindSpeed-LLM 与社区均报告 56.5%，完全一致。
- **DeepSeek-V2-236B / MMLU**：MindSpeed-LLM 78.1% vs 社区 78.5%，差距 0.4 个百分点。
- **DeepSeek-V2.5 / MMLU**：MindSpeed-LLM 79.3% vs 社区 80.6%，差距 1.3 个百分点，是四组对比中差距最大者。
- 总体观察：使用 YaRN 默认配置后，MindSpeed-LLM 与社区版本的 MMLU 精度差距均在约 1 个百分点以内，未出现显著精度劣化。

---

## 【公式解读】

原文无显式公式。原文仅以文字方式提到：
- 计算/内存复杂度："O(n²)，其中 n 为序列长度"
- 注意力缩放系数函数名：`yarn_get_mscale`

由于原文未给出 `yarn_get_mscale` 的具体实现或数学定义，因此不对其内部公式做推断解读。

---

## 【关联】

- **位置编码侧**：本文档属于 RoPE 旋转位置编码扩展方向，与同仓其他长上下文/位置编码相关特性（如其他 RoPE 变体、ALiBi 等）同属"上下文窗口扩展"技术族，但原文未给出内部链接，也未点名其他具体特性文档。
- **模型侧**：文档以 DeepSeek-V2 系列为示例，因此与该仓中 DeepSeek-V2 / V2-Lite / V2.5 / DeepSeek-Math 等模型的推理部署文档存在上下游关系——YaRN 是推理阶段的开关，需配合对应模型配置文件使用。
- **上下游**：上游是 RoPE 位置编码本身的实现；下游是长上下文推理任务的实际应用。
- 用户提供的内部链接信息为"无"，故未补充额外链接。

---

## 【使用方法】

启用 YaRN 的最小命令示例（基于 DeepSeek-V2 配置）：

```bash
--rope-scaling-type yarn
```

配合以下参数一起设置（可参考上节参数表）：

```bash
--beta-fast 32
--beta-slow 1
--rope-scaling-factor 40        # 例如 4K → 160K 时设为 40
--rope-scaling-mscale <value>
--rope-scaling-mscale-all-dim <value>
--rope-scaling-original-max-position-embeddings 4096
```

**约束条件**：
- 仅对**使用 RoPE 作为位置编码**的模型在**推理**阶段生效（原文："使用 RoPE 作为位置编码的模型，在推理时均可使用 YaRN 来扩展上下文长度"）。
- 需要正确填写 `--rope-scaling-original-max-position-embeddings`，使框架能够计算实际扩展倍数。

> 注：`yarn_get_mscale` 函数的内部计算公式及 `--rope-scaling-mscale` / `--rope-scaling-mscale-all-dim` 的推荐取值范围，原文未涉及。

## 图文联合解读

- `position_embedding.png`: **图文联合解读：**

1）**图像内容**：纵轴为 d_model 各维度（从"第1维"到"第n维"），横轴为位置 t（0–512）。每行展示一条正弦/余弦波，越靠上频率越高（密集震荡），越靠下频率越低（趋于平缓）。两条青色竖框标注 t≈192 与 t≈352 的采样点，并附数值标签。

2）**技术结论**：RoPE 旋转编码在不同维度上呈现"频率从高到低连续分布"的特征——高频维度周期远小于序列长度，低频维度周期接近甚至超过序列长度，因此无法对所有维度使用单一缩放策略。

3）**与文档论点对应**：正是这一频率分布特性，为 YaRN 的 **NTK-by-parts** 分段策略提供了依据——高频维度直接外推、低频维度线性插值、中间区域平滑过渡，从而提升上下文扩展后的精度。
- `ntk_by_parts.png`: 1) 图示定义了：比值 r_i = L/λ_i 表示第 i 维旋转圈数；斜坡函数 γ(r_i) 分三段取值（>β 取 1、<α 取 0、中间线性插值）；调整后角度 h(θ_i) = [1-γ(r_i)]θ_i/s + γ(r_i)θ_i，s 为缩放因子。

2) 论证：高频维度（i 小，r_i > β）保持外推无需改变；中间区域线性插值过渡；低频维度（i 大，r_i < α）按比例 s 线性插值。

3) 与文档呼应：公式精确刻画了文档"高频外推、低频插值、中间过渡"的 NTK-by-parts 分段缩放机制，为上下文窗口扩展提供数学依据。
