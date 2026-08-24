---
paper_num: "29"
title: "Dynamic Large Concept Models: Latent Reasoning in an Adaptive Semantic Space"
authors: "Adaptive Semantic Space 1ByteDance Seed, 2University of Manchester, 3Mila - Quebec AI Institute, 4Tsinghua University , 5M-A-P"
date: "2026/1/19"
arxiv: "https://arxiv.org/abs/2512.24617"
pdf: "papers/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space.pdf"
slug: "dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space"
tags: []
---

# Dynamic Large Concept Models: Latent Reasoning in an Adaptive Semantic Space

> [!abstract] 摘要（原文）
> 1\. 🌟 Dynamic Large Concept Models (DLCM) 提出了一种分层语言建模框架，通过从潜在表示中学习语义边界，并将计算从 Token 转移到压缩概念空间，以解决大型语言模型中信息密度不均匀的问题。 2. 💡 该模型通过动态分割变长概念并在压缩概念空间中进行深度推理，同时引入了压缩感知缩放律和用于异构模块解耦 μP 参数化，实现了计算资源的自适应分配。 3. 📈 在实际应用中，DLCM 在匹配推理 FLOPs 的情况下，将计算重新分配到更高容量的推理主干网络中，在12个零样本 benchmarks 中平均提高了2.69%，在推理主导型任务上表现尤为突出。

## 元信息
- **发表日期**: 2026/1/19
- **作者**: Adaptive Semantic Space 1ByteDance Seed, 2University of Manchester, 3Mila - Quebec AI Institute, 4Tsinghua University , 5M-A-P
- **arXiv**: https://arxiv.org/abs/2512.24617
- **本地 PDF**: `papers/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space.pdf`
- **页数**: 24

## 图表（原文 caption + 页码）

### Figure 1 (p.4) ⭐深度解读
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-fig01.png]]
*整页渲染: ![[assets/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-p04.png]]*
> [!quote] caption
> 3.1

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 1 — DLCM 总体结构）**

**(a) 总体架构**：左侧 8 个 token 输入经含 θ 参数的蓝色编码器，由查询 Q 抽取得到 4 个语义概念嵌入 C₁–C₄；中间橙色模块接收 KV 与隐状态 S，送入紫色解码器，最终输出右侧 4 个位置的下个 token 概率分布。

**(b) 边界检测与池化**：对编码隐状态 hθ(·) 设阈值 τ，按边界 τ 将 8 个 token 动态切分为 4 段并池化得到 C₁–C₄，体现"语义自适应粒度"。

**(c) 解码器交叉注意力**：查询 q₁–q₅ 通过交叉注意力矩阵选择性聚焦 C₁–C₄，说明生成阶段在概念层而非 token 层进行推理。

**关键结论**：DLCM 将 token 级推理上移至概念级 KV 缓存，缩短序列并支持动态粒度，构成论文"潜在自适应语义空间推理"方法的核心链路。

### Figure 9 (p.7) ⭐深度解读
![[assets/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-p07.png]]
> [!quote] caption
> 4.3

> [!tip] 技术解读（多模态）
> # Description

**Note:** This page contains no rendered figure—it is a text-heavy section (Sections 3.6, 4, 4.1–4.3) that *references* "Figure 2" (attention mask illustration) and "Figure 9" (speedup plot, not shown). The figure-equivalent content here is the conceptual data flow described in text:

## Architecture / Components / Data Flow (as described)

1. **Inputs:** Tokens t₁…t_L (queries) and concept features c₁…c_M (keys/values), with variable-length mapping where each concept c_j spans a segment of tokens.
2. **Problem:** Ragged attention mask—direct Flex Attention is inefficient due to dynamic mask generation and irregular memory access.
3. **Solution — Concept Replication:** Replicate each concept feature c_j to fill its segment length, producing K̃ = repeat(c, segment_lengths) and Ṽ = repeat(c, segment_lengths). This aligns KV length with query length L.
4. **Compute:** Run FlashAttention's **VarLen** kernel (causal-style self-attention) on the replicated KV, since K/V are locally constant within each segment.
5. **Training loss:** L = L_CE + L_a (cross-entropy + load-balancing, Eq. 15), with RMSNorm on Q and K (Eq. 16).

## Key Technical Takeaway
Concept replication converts irregular concept-token cross-attention into a uniform-length VarLen self-attention problem, yielding **1.26×–1.73× speedup** over Flex Attention by trading a small memory cost for highly optimized CUDA kernels.

## Caption (verbatim from the page)

No figure caption is present on this page. The page's opening line reads:

> "**3.6 Training Objective** — The total loss combines next-token prediction with adaptive compression:
> 
> L = L_CE + L_a       (15)
> 
> where L_CE is cross-entropy on output tokens and L_a is the load-balancing loss."

The only in-line figure references are: *"Figure 2"* (ragged-boundary attention mask) and *"Figure 9"* (plotted speedup T_FA = T_8 ).

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.9) ⭐深度解读
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-tab01.png]]
> [!quote] caption
> Statistics of the pretraining data.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文联合解读**

该表量化呈现DLCM预训练语料构成：总计**1,000B tokens**，由四类数据按比例混合——Nemotron-CC（英文网页）占50%（500B）、MAP-CC（中文网页）占25%（250B）、OpenCoder-Pretrain（代码）占15%（150B）、MegaMath-Web（数学）占10%（100B）。

原文借该表论证关键结论：预训练数据**英中双主、代码与数学为辅**的四源异构配比设计，使模型在自适应语义空间中能同时获得通用语言、跨语种、编程与推理能力。该表位于第3.1节（数据设置），是后续消融与下游评估（语言/代码/数学任务）的**基座配置**，为Figure 1所示的"动态分块+潜在推理"框架提供训练数据支撑，确保模型在概念粒度推理中具备多领域知识基底。

### Table 2 (p.15) ⭐深度解读
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-tab02.png]]
> [!quote] caption
> Performance Comparison: DLCM vs. Baseline. Zero-shot accuracy (%) categorized by task type. Improvements are shown in green and regressions in red.

> [!tip] 表格解读（多模态）
> 【图文联合解读】1) 表格对比DLCM与Baseline在12项零样本任务上的准确率，按类别分：常识/通识（Commonsense QA 21.38→+1.64、OpenBookQA +3.00、PIQA +2.42、ARC Easy +2.61、ARC Challenge +1.77、HellaSwag +0.67、Winogrande +1.02）；文本理解（BoolQ −1.47、RACE −0.72）；多语言知识（C-Eval +1.71、CMMLU −0.24、MMLU −0.30）。总体平均43.92 vs 41.23，净升+2.69。

2) 论证DLCM在常识/通识推理类任务上普遍增益，但在需精细文本理解（MMLU、BoolQ、RACE）的基准略退化，整体均值仍优于基线，支撑"自适应语义空间潜变量推理"的有效性与适用边界。

3) 作为主结果定量证据，串联方法设计与消融/加速讨论，构成实验链路核心结论支撑。

### Table 3 (p.16) ⭐深度解读
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-tab03.png]]
> [!quote] caption
> Architecture Configuration Details. A unified view of the parameter settings for Baseline (LLaMA-1.3B) and DLCM (2.3B). Values are presented as Baseline / Ours .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读**

Table 3 以"Baseline(1.3B)/DLCM(2.3B)"并列对比架构参数。通用层：同用 Transformer、词表 128,815、Swish、8k 位置编码，DLCM 总参升至 2.3B。维度层：DLCM 新增主隐层 d_p=3,072 与 Cross 中间层 6,144（基线无）。层级配置：DLCM 将 32 层拆为 10 编码+16 backbone+6 解码，而基线统一 32 层。注意力：DLCM backbone 头 48、KV 头 12（基线均为 24），体现分组 KV 与交叉注意力结构。

**关键结论**：DLCM 以 encoder–backbone–decoder 三段分层、主隐层维度加倍及交叉注意力机制，仅以约 1B 参数增量即构建潜在推理架构。

**作用**：为后续推理基准实验提供可复现的架构基线，证明模型性能提升源于结构升级（分层语义空间+交叉推理）而非单纯参数扩容，从而支撑"自适应语义空间潜在推理"的核心方法论。

### Table 4 (p.17) ⭐深度解读
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-tab04.png]]
> [!quote] caption
> Ablation Study: Global Parser vs. Normal. Performance comparison on downstream tasks. Both models aim for a target compression ratio of R=4. The Global Parser achieves a realized ratio much closer to the target while consistently improving accuracy on most tasks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】【核心对象与结构】表4在目标压缩比R=4下，并列对比Global Parser与Normal两种解析器在6项下游任务（ARC-C、ARC-E、CommonsenseQA、HellaSwag、OpenBookQA、PIQA）的Acc与实现压缩比。

【关键结论】Global Parser在5项任务胜出（最高+2.29%于CommonsenseQA），仅OpenBookQA低0.006，平均提升+2.1%；更关键的是其实现压缩比3.92几近目标4，而Normal仅3.15，存在显著欠压缩。

【链路作用】作为消融核心证据，该表证明全局解析器在精准逼近目标压缩比的同时提升下游准确率，从而支撑"自适应语义空间"中"压缩率可控即语义无损"的核心技术论点。

### Table 5 (p.18) ⭐深度解读
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-tab05.png]]
> [!quote] caption
> Average tokens per concept across content types and compression ratios. Values represent the actual granularity achieved for each target compression setting.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明：图片中仅显示表格标题及周边正文段落，未呈现表格具体数值，故结合原文论述解读。**

**核心对象与数据：** 表5展示在不同内容类型（代码、结构化文本、密集散文等）与各压缩比目标下，每个"概念"实际承载的平均token数，即每个语义块的真实粒度。

**关键技术结论：** 代码/结构化文本被压缩为更短的句法单元（约几个token），而密集散文则保留为更长的语义chunk（数十token）；同一压缩比下粒度随内容自适应变化。

**方法链路作用：** 支撑DLCM"自适应语义空间"核心主张——证明模型并非机械按固定比例切分，而是在全局压缩预算内根据内容语义密度动态调整粒度，最大化信息保留，为后续推理实验提供可解释的结构性证据。

### Table 6 (p.7) ⭐深度解读
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-tab06.png]]
> [!quote] caption
> Performance comparison (Batch=1, Heads=32, Interval=6)

> [!tip] 表格解读（多模态）
> 【图文联合解读】**注：表格表头与数据列顺序错位**（表头：Seq Length / Hidden Size / Flex / Flash Varlen / Speedup；实际数据列顺序为 Flex (ms) / Flash Varlen (ms) / Speedup / Seq Length / Hidden Size，已按数据语义修正解读）。

**图文联合解读：**

表6固定Batch=1、Heads=32、Interval=6，对Flex与Flash Varlen两种注意力做3×4共12组延迟对比（Seq∈{2K,4K,8K,16K}×Hidden∈{1K,2K,4K}）。Flex从2K的32.35ms升至16K的315.69ms，Flash Varlen对应从22.48ms升至190.38ms；Flex较Flash Varlen慢1.26×–1.73×，且劣势随序列延长扩大，16K时差距稳定在1.66×–1.73×。该表以量化延迟数据支撑"Flex长序列效率劣势显著"的关键结论，为DLCM选用Flash Varlen作为底层注意力实现提供性能层面的实证依据。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf{q}_t = \mathbf{W}_q \mathbf{h}_t, \quad \mathbf{k}_t = \mathbf{W}_k \mathbf{h}_t
$$

$$
p_t = \frac{1 - \cos(\mathbf{q}_{t-1}, \mathbf{k}_t)}{2} = \frac{1}{2} \left( 1 - \frac{\mathbf{q}_{t-1}^{\top}\mathbf{k}_t}{\|\mathbf{q}_{t-1}\|_2 \|\mathbf{k}_t\|_2} \right)
$$

$$
\mathbf{c}_k^{\text{raw}} = \frac{1}{|S_k|} \sum_{t \in S_k} \mathbf{h}_t, \quad \mathbf{c}_k = \mathbf{W}_{\text{up}}\mathbf{c}_k^{\text{raw}}
$$

$$
\mathcal{L}_{\text{aux}} = \frac{R}{R-1} \left[ (R-1) \cdot F_{\text{global}} \cdot G_{\text{global}} + (1 - F_{\text{global}}) \cdot (1 - G_{\text{global}}) \right] - 1
$$

$$
\tilde{\mathbf{Z}} = \mathcal{S}(\mathbf{Z})
$$

$$
\Psi(\mathbf{H}, \mathbf{Z}) = \text{Softmax}\left( \frac{\mathbf{Q}\mathbf{K}^\top}{\sqrt{d_{\text{head}}}} + \mathbf{M} \right) \mathbf{V}\mathbf{W}_O + \mathbf{H}
$$

$$
\mathcal{L} = \mathcal{L}_{\text{CE}} + \lambda \mathcal{L}_{\text{aux}}
$$

$$
\mathbf{Q}' = \text{RMSNorm}(\mathbf{Q}), \quad \mathbf{K}' = \text{RMSNorm}(\mathbf{K})
$$

$$
\tilde{\mathbf{K}} = \texttt{repeat\_interleave}(\mathbf{K}, \text{segment\_lengths}), \quad \tilde{\mathbf{V}} = \texttt{repeat\_interleave}(\mathbf{V}, \text{segment\_lengths})
$$

$$
s_{\text{token}} = \frac{d_{\text{token}}}{d_{\text{base}}}, \quad s_{\text{concept}} = \frac{d_{\text{concept}}}{d_{\text{base}}}
$$

$$
\text{logits} = \frac{1}{s_{\text{token}}} \cdot (\mathbf{h}_{\text{final}} W_{\text{unemb}}^\top)
$$

$$
L(N, D, R, P) = E_0 + \frac{A_{\text{token}}} {(N(1-P) + t_{\text{token}})^{\delta_1}} + \frac{A_{\text{concept}} \, R^{\gamma}} {(NP + t_{\text{concept}})^{\delta_2}} + \frac{A_{\text{data}}} {(D + t_{\text{data}})^{\alpha}}.
$$

$$
\Delta_{\text{decay}} = k \, L_{\text{stable}}^{\,a} R^{\,b} N^{\,c}
$$

$$
\nabla_{\theta} \mathcal{L}_{\text{total}} = \underbrace{\nabla_{\theta} \mathcal{L}_{\text{CE}}}_{\text{anti-compression}} + \lambda \underbrace{\nabla_{\theta} \mathcal{L}_{\text{aux}}}_{\text{pro-compression}}
$$

$$
\mathbf{H} &= \mathcal{E}(\mathbf{x}) && \text{(Encoding)} \\ \mathbf{C} &= \Phi(\mathbf{H}) && \text{(Segmentation \& Pooling)} \\ \mathbf{Z} &= \mathcal{M}(\mathbf{C}) && \text{(Concept Reasoning)} \\ \hat{\mathbf{y}} &= \mathcal{D}(\Psi(\mathbf{H}, \mathbf{Z})) && \text{(Decoding)}
$$

$$
G_{\text{global}} &= \frac{1}{|\mathcal{T}|} \sum_{(i,t) \in \mathcal{T}} p_{i,t} && \text{(expected boundary rate)} \\ F_{\text{global}} &= \frac{1}{|\mathcal{T}|} \sum_{(i,t) \in \mathcal{T}} b_{i,t} && \text{(actual boundary rate)}
$$

$$
\mathbf{Q} &= \mathbf{H}\mathbf{W}_Q, \quad \text{where } \mathbf{W}_Q \in \mathbb{R}^{d_{\text{token}} \times d_{\text{head}}} \\ \mathbf{K} &= \tilde{\mathbf{Z}}\mathbf{W}_K, \quad \mathbf{V} = \tilde{\mathbf{Z}}\mathbf{W}_V, \quad \text{where } \mathbf{W}_{K,V} \in \mathbb{R}^{d_{\text{concept}} \times d_{\text{head}}}
$$

$$
\eta_{\mathcal{E}, \mathcal{D}} &= \eta^{\text{base}}_{\text{token}} \cdot s_{\text{token}}^{-1} \\ \eta_{\mathcal{M}} &= \eta^{\text{base}}_{\text{concept}} \cdot s_{\text{concept}}^{-1}
$$

## 技术点深读（DEEP）

![[deep/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space.txt`（61312 字符）供引用检索。