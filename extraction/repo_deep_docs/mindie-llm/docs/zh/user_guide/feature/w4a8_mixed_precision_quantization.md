# W4A8混合量化

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/w4a8_mixed_precision_quantization.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/w4a8_mixed_precision_quantization.md

# W4A8 混合量化 — 一体化深度解读

## 【定位】

这篇文档描述了 mindie-llm（昇腾自研大模型推理引擎）在 DeepSeek R1/V3 模型上提供的一种**分层差异化量化能力（W4A8 混合量化）**：把同一模型中不同性质的层（MLP 前三层、MLA & 共享专家层、路由专家层）分别用 W8A8 Dynamic、W8A8、W4A8 Dynamic 三种精度组合起来，以在保持精度的同时降低显存/带宽占用，并说明量化后权重的目录结构、描述文件格式与张量 dtype/shape。

---

## 【技术要点】

1. **分层量化策略（DeepSeek R1/V3 专用）**
   - 前三层 MLP：`W8A8 Dynamic` 量化
   - MLA & 共享专家层：`W8A8` 量化
   - 路由专家层（`experts`）：`W4A8 Dynamic` 量化

2. **W4A8 Dynamic 的量化方式**
   - 权重：4bit 量化
   - 激活：8bit 量化
   - 权重同时使用 **Per-channel** 与 **Per-group** 两种粒度

3. **适用性与约束**
   - 仅支持 DeepSeek-R1、DeepSeek-V3 模型
   - 仅支持配合 Anti-Outlier 离群值处理使用
   - 暂不支持与 KV Cache int8 量化配合使用
   - 若要开启"共享专家混置"特性，需更换为**共享专家层量化为 W4A8**的特殊权重，并保持开启

4. **支持的原始权重类型**：float16 或 bfloat16

5. **量化后输出物**
   - 权重文件 `quant_model_weight_w8a8.safetensors`
   - 权重描述文件 `quant_model_description.json`（含每层每个张量的量化类型，如 `W8A8`、`W8A8_DYNAMIC`、`W4A8_DYNAMIC`、`FLOAT`）
   - 推理配置相关：`config.json`、`quant_model_description.json`、`tokenizer_config.json`、`tokenizer.json`、`tokenizer.model`

6. **反量化所需的额外张量**：MatMul 权重新增 `weight_scale`、`weight_scale_second`、`scale_bias` 三个张量，用于对 MatMul 计算结果做反量化。

---

## 【关键机制与数据】

**工作原理 / 数据流**

- 量化分粒度进行：原始模型被划分为三类层（MLP 前三层、MLA & 共享专家、路由专家），分别走不同的量化路径；同一个权重会被打上 `W8A8`、`W8A8_DYNAMIC`、`W4A8_DYNAMIC` 或保持 `FLOAT`（如 `model.embed_tokens.weight`）的标签，写入 `quant_model_description.json` 中。
- 推理时（对应原文 **图 1**），量化权重进入 MatMul 计算后，会额外使用 `weight_scale`、`weight_scale_second`、`scale_bias` 进行**反量化**，把 int4 计算结果还原回浮点域。
- 原文给出了量化后描述文件 `quant_model_description.json` 的部分样例，可看到 `mlp.gate_proj.weight` 在不同 layer 上分别被标记为 `W8A8`、`W8A8_DYNAMIC`、`W4A8_DYNAMIC`，并对应携带 `weight_scale`（必要时还有 `weight_scale_second` 和 `scale_bias`）。

**性能数据**
- 原文：**未给出**具体的吞吐量、延迟、显存节省、精度（perplexity / 评测分数）等量化性能数据。
- 原文：**未给出**具体的 group_num（Per-group 的 group 大小）数值。

---

## 【表格解读】

### 表 1 — float16 权重量化后 dtype 及 shape 信息（假设原始权重 shape 为 [n, k]）

**（原文表格逐字还原）**

| Tensor信息 | weight | weight_scale | weight_scale_second | scale_bias |
|--|--|--|--|--|
| dtype | int4 | float32 | float32 | uint64 |
| shape | [n, k] | [n, 1] | [n, group_num] | [n,group_num] |

**逐行解读**：
- **dtype 行**：量化后的权重张量 `weight` 本身被压成 `int4`；`weight_scale` 和 `weight_scale_second` 两种 scale 都是 `float32`；`scale_bias` 则使用 `uint64`。
- **shape 行**：设原始权重为 `[n, k]`（典型 Linear/MatMul 权重矩阵形状）：
  - `weight`：`[n, k]`，逐元素压成 int4；
  - `weight_scale`：`[n, 1]`，每输出通道一个 Per-channel 的 float32 scale；
  - `weight_scale_second`：`[n, group_num]`，每输出通道内按 group 再细分的 float32 scale（即 Per-group scale），`group_num` 取决于 group 大小配置；
  - `scale_bias`：`[n, group_num]`（原文无空格），与 `weight_scale_second` 同形，使用 uint64 类型——结合正文"仅当浮点权重存在 bias 场景时，量化权重才会有 bias"可知，该张量仅在原始权重带 bias 的层出现。

### 表 2 — bfloat16 权重量化后 dtype 及 shape 信息（假设原始权重 shape 为 [n, k]）

**（原文表格逐字还原）**

| Tensor信息 | weight | weight_scale | weight_scale_second | scale_bias |
|--|--|--|--|--|
| dtype | int4 | bfloat32 | bfloat32 | uint64 |
| shape | [n, k] | [n, 1] | [n, group_num] | [n,group_num] |

**逐行解读**：
- 与表 1 完全相同的 shape 布局，**唯一差异**在两种 scale 张量的 dtype：`weight_scale` 与 `weight_scale_second` 改为 `bfloat32`，与 bfloat16 原始权重保持同一数值家族。
- `weight` 仍为 `int4`，`scale_bias` 仍为 `uint64`、shape 仍为 `[n, group_num]`，bias 是否存在同样依赖原始权重是否带 bias。
- 总结：当用户从 float16 权重切换到 bfloat16 权重做 W4A8 Dynamic 量化时，只需相应地把 scale 张量由 float32 换成 bfloat32，其余 shape 与反量化流程不变。

---

## 【公式解读】

**原文无公式。**

本文档未给出任何 LaTeX 公式或伪代码形式的量化/反量化数学表达式。文中涉及的"4bit/8bit 量化"、"Per-channel"、"Per-group"、"反量化"等概念均以文字和表格（dtype/shape）形式描述，没有给出 $Q(w) = \text{round}(w / s) - z$ 这类显式公式。

---

## 【关联】

文档末尾给出的内部链接信息为 **（无）**，因此本节仅基于正文出现的特性/模块名称梳理其上下游关系：

- **Anti-Outlier 离群值处理**：原文明确"W4A8 混合量化仅支持配合 Anti-Outlier 使用"，说明 Anti-Outlier 是该量化方案的前置/配套特性，应在量化前启用以抑制激活离群值对低 bit 权重的影响。
- **KV Cache int8 量化**：原文标注"暂不支持 KV Cache int8 量化配合使用"，说明 KV Cache int8 与 W4A8 混合量化在当前版本互斥，不应同时开启。
- **共享专家混置（共享专家层量化）特性**：原文指出"如需开启共享专家混置特性，需要更换为共享专家层量化为 W4A8 的特殊权重，且保持开启"，即共享专家混置是另一个特性分支，会把共享专家层从默认的 W8A8 切换到 W4A8，与本特性的路由专家 W4A8 形成更激进的量化方案，但需要使用特制的权重文件。
- **MLA（Multi-head Latent Attention）层**：作为 DeepSeek 模型的注意力结构，MLA 在本文中归入"W8A8"量化档位，与"MLP 前三层 W8A8 Dynamic"、"路由专家 W4A8 Dynamic"并列，是分层方案中的一档。
- **W8A8 Dynamic / W8A8 量化**：作为 W4A8 混合量化的"上层"量化能力，被直接复用在前三层 MLP 和 MLA/共享专家层上，可视为其依赖的子能力。

---

## 【使用方法】

**原文未涉及具体的启用命令或配置项参数。**

本文档仅描述了 W4A8 混合量化的能力定义、适用范围、量化后权重目录与描述文件示例、以及量化后张量的 dtype/shape，**未提供**：

- 启动量化的 CLI 命令（如 `mindie-llm quantize ...`）；
- 量化配置文件（如 JSON/YAML 字段 `quant_type: w4a8_mixed` 之类）；
- 推理侧如何指定加载混合量化权重的参数；
- Per-group 的 `group_num` 取值或推荐配置；
- 性能调优开关。

如需在工程中开启该特性，需参考 mindie-llm 项目中量化工具与推理启动的专门章节（本文档未给出对应的内部链接）。

## 图文联合解读

- `w4a8_mixed_precision_quantization.png`: **图文联合解读：**

图示描绘W4A8推理数据流：权重int4经反量化转为int8，与int8激活值进行MatMul运算，结果输出为float16/bfloat16。

**技术结论：** 权重以低精度int4存储节省空间，运行时反量化为int8参与计算，激活值保持int8，输出回插高精度，验证了"Per-channel和Per-group对权重4bit量化、对激活8bit量化"的混合精度策略。

**与文档关系：** 对应文档所述路由专家层W4A8 Dynamic量化路径，与quant_model_description.json中weight_scale、weight_scale_second等反量化参数协同实现。
