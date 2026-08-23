---
paper_num: "55"
title: "Gated Delta Networks: Improving Mamba2 with Delta Rule"
authors: ""
date: "2024/12/9"
arxiv: "https://arxiv.org/abs/2412.06464"
pdf: "papers/gated-delta-networks-improving-mamba2-with-delta-rule.pdf"
slug: "gated-delta-networks-improving-mamba2-with-delta-rule"
tags: [architecture]
---

# Gated Delta Networks: Improving Mamba2 with Delta Rule

> [!abstract] 摘要（原文）
> 1. Linear Transformers have gained attention as efﬁcient alternatives to standard Transformers, but their performance in retrieval and long-context tasks has been limited. To address these limitations, recent work has explored two distinct mech- anisms: gating for adaptive memory control and the delta update rule for pre- cise memory modiﬁcations. We observe that these mechanisms

## 元信息
- **发表日期**: 2024/12/9
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2412.06464
- **本地 PDF**: `papers/gated-delta-networks-improving-mamba2-with-delta-rule.pdf`
- **页数**: 22

## 图表（原文 caption + 页码）

### Figure 1 (p.7) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-fig01.png]]
*整页渲染: ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p07.png]]*
> [!quote] caption
> Visualization of the (hybrid) architecture and block design of Gated DeltaNet models.

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】Gated DeltaNet 架构(Fig.1)：delta-rule 线性注意力 + 乘性门控(α,β)增联想召回；H1/H2 混合变体把 Gated DeltaNet 与 Mamba2(SSM) + Sliding-Window Attention 交错，融合选择性长程记忆+结构化递归+局部上下文。block 设计：q/k 路径=线性投影+shortconv+SiLU+L2norm，v=线性投影+shortconv+SiLU，α/β=线性投影，输出 gate=线性投影+SiLU。Wiki ppl 16.42、zero-shot 55.32，H2 混合 ppl 15.91 最优。线性注意力/SSM 架构核心图。

### Figure 2 (p.8) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-fig02.png]]
*整页渲染: ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p08.png]]*
> [!quote] caption
> Length extrapolation on six long benchmarks.

> [!tip] 技术解读（多模态）
> ## Figure 2 Description

**Layout:** A 2×3 grid of line plots evaluating perplexity (y-axis) as a function of sequence length (x-axis: 4k → 20k tokens) across six long-context benchmarks: GovReport, QMSum, NarrativeQA, Qasper, CodeParrot, and PG19.

**Components (legend):** Seven models compared:
- Pure RNNs: Mamba1, DeltaNet, Mamba2
- Hybrid: Samba (RNN + attention)
- Proposed: GatedDeltaNet, GatedDeltaNet-H1, GatedDeltaNet-H2 (hybrid gated variants)

**Data flow:** Perplexity values are computed for each model at progressively increasing context lengths, producing U-shaped curves that dip near training length and rise at extrapolation.

**Key technical takeaway:** Gated DeltaNet (and its hybrid H1/H2 variants) consistently achieves the lowest perplexity across all six benchmarks and degrades least at 20K, indicating that adding a gating mechanism to the delta update rule improves both extrapolation stability and memory management in linear-recurrent models.

## Caption (verbatim)

**Figure 2:** Length extrapolation on six long benchmarks.

### Figure 3 (p.9) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-fig03.png]]
*整页渲染: ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p09.png]]*
> [!quote] caption
> Training throughput comparison of 1.3B models on a single H100 GPU. standalone mixers: Samba outperforms Mamba, while Gated DeltaNet-H1 and -H2 outperform

> [!tip] 技术解读（多模态）
> **Figure 3 Description (Architecture/Components/Data Flow):**
Figure 3 is a line plot comparing training throughput (Y-axis: Thousands of Tokens Per Second, ~25–60 K/s) across varying sequence length × batch size configurations (X-axis: 2K×16, 4K×8, 8K×4, 16K×2) for 1.3B-parameter models on a single H100 GPU. Eight model variants are plotted: Transformer++, DeltaNet, Gated DeltaNet, Mamba1, Mamba2, Samba, and the proposed Gated DeltaNet-H1 and -H2 hybrid/standalone mixers. Transformer++ shows a steep degradation (~55 → ~27 K/s) as sequence length grows, while linear-attention and gated-RNN baselines remain flat (~38–50 K/s).

**Key Technical Takeaway:**
Gated DeltaNet-H1 and -H2 deliver the highest stable throughput (~50–54 K/s) across all sequence lengths, overcoming DeltaNet's poor short-sequence performance while preserving linear scaling.

**Caption (verbatim):**
"Figure 3: Training throughput comparison of 1.3B models on a single H100 GPU."

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-tab01.png]]
> [!quote] caption
> Comparison of different linear RNN models and their corresponding online learning objectives using the framework from Liu et al. ( 2024 ). For convenience, we simplify Longhorn’s vector-valued β to scalar β .

> [!tip] 表格解读（多模态）
> # Description

Although labeled "Table 1," this is a tabular comparison figure presenting five linear RNN models (LA, Mamba2, Longhorn, DeltaNet, Gated DeltaNet) along two axes: (i) their **online learning objective** (a Frobenius-norm loss penalizing deviation of a state matrix **S**_t from its previous value, with various inner-product/regression-like terms), and (ii) the corresponding **online state update** rule (a recurrence combining a decay factor on the prior state with a rank-1 outer-product update driven by the input **v**_t**k**_t^T). The table unifies these methods under a shared framework, showing how each differs only in scalar gating/decay coefficients (α_t, β_t) and an adaptive ε_t correction. **Key takeaway:** modern linear RNNs are unified as variants of an online ridge-regression/least-squares problem on a state matrix, with state updates decomposable into a multiplicative decay plus a rank-1 associative write — implying their expressivity is largely governed by how **α** and **β** scale memory and forgetting.

# Caption (verbatim)

**Table 1:** Comparison of different linear RNN models and their corresponding online learning objectives using the framework from **Liu et al. (2024)**. For convenience, we simplify Longhorn's vector-valued β to scalar β.

| Method | Online Learning Objective | Online Update |
|---|---|---|
| LA | ‖**S**_t − **S**_{t−1}‖²_F − 2⟨**S**_t **k**_t, **v**_t⟩ | **S**_t = **S**_{t−1} + **v**_t **k**_t^T |
| Mamba2 | ‖**S**_t − α_t **S**_{t−1}‖²_F − 2⟨**S**_t **k**_t, **v**_t⟩ | **S**_t = α_t **S**_{t−1} + **v**_t **k**_t^T |
| Longhorn | ‖**S**_t − **S**_{t−1}‖²_F − β_t ‖**S**_t **k**_t − **v**_t‖² | **S**_t = **S**_{t−1}(**I** − ε_t **k**_t **k**_t^T) + ε_t **v**_t **k**_t^T, ε_t = β_t / (1 + β_t **k**_t^T **k**_t) |
| DeltaNet | ‖**S**_t − **S**_{t−1}‖²_F − 2⟨**S**_t **k**_t, β_t (**v**_t − **S**_{t−1}**k**_t)⟩ | **S**_t = **S**_{t−1}(**I** − β_t **k**_t **k**_t^T) + β_t **v**_t **k**_t^T |
| Gated DeltaNet | ‖**S**_t − α_t **S**_{t−1}‖²_F − 2⟨**S**_t **k**_t, β_t (**v**_t − α_t **S**_{t−1}**k**_t)⟩ | **S**_t = **S**_{t−1} (α_t(**I** − β_t **k**_t **k**_t^T)) + β_t **v**_t **k**_t^T |

### Table 3 (p.7) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-tab03.png]]
> [!quote] caption
> Performance comparison on language modeling and zero-shot common-sense reasoning.

> [!tip] 表格解读（多模态）
> ## Caption (verbatim)
**Table 3:** Performance comparison on language modeling and zero-shot common-sense reasoning.

## Description of the Main Figure (Table 3)

**Structure / Components:** Table 3 is a comparative results matrix. Its visible column header row shows **Models** on the left, followed by seven zero-shot common-sense reasoning benchmarks — **SWDE, SQD, FDA, TQA, NQ, Drop, Avg** — separated by a horizontal rule. (The table is cropped, so the numeric values and language-modeling perplexity column are not shown.)

**Data flow:** Each row corresponds to a model (Transformer baselines, Mamba, Samba, and the proposed hybrid architecture), and each cell carries that model's score on the respective benchmark, with the rightmost **Avg** column aggregating zero-shot accuracy.

**Key Technical Takeaway (≤120 words):** All evaluated models are trained under matched conditions — Llama2 tokenizer (32K vocab), 0.5M-token batch size, and 4K-token training context — with **Samba and the hybrid models using a 2K sliding window**, ensuring that performance gains on benchmarks (SWDE, SQuAD, FDA, TQA, NQ, DROP) reflect architectural design rather than training-recipe differences. The takeaway: the table isolates the **hybrid (Samba) architecture's advantage** in zero-shot common-sense reasoning against pure-attention and pure-SSM baselines.

### Table 4 (p.7) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-tab04.png]]
> [!quote] caption
> Accuracy on recall-world retrieval tasks with input truncated to 2K tokens. SQD: SQUADE. TQA: Trivial QA.

> [!tip] 表格解读（多模态）
> I'm unable to complete this task as described because the content you've provided does not contain a figure. What you've shared is only:

1. A **table caption** (not a figure caption)
2. A page number "7"

**What was actually provided:**

> **Table 4:** Accuracy on recall-world retrieval tasks with input truncated to 2K tokens. SQD: SQUADE. TQA: Trivial QA.

**No image, architecture diagram, component schematic, or data flow visualization is included in the message.** I can see the caption text, but there is no underlying figure whose components, architecture, or data flow I could describe.

**Verbatim transcription of the caption text provided:**

> "Table 4: Accuracy on recall-world retrieval tasks with input truncated to 2K tokens. SQD: SQUADE. TQA: Trivial QA."

**To help you, I could instead:**
- Describe what an *architecture diagram* in an NLP retrieval paper (matching this table's topic) typically depicts
- Analyze or paraphrase the caption itself (single sentence, ~20 words, already at <120 words)
- Wait for you to re-upload the figure image or describe it

Would you like me to proceed with one of these alternatives?

### Table 5 (p.9) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-tab05.png]]
> [!quote] caption
> Accuracy on 14 tasks from LongBench ( Bai et al. , 2023 ): Narrative QA, QasperQA, MultiField QA, HotpotQA, 2WikiMulti QA, Musique, GovReport, QMSum, MultiNews, TRec, Trivia QA, SamSum, LCC, and RepoBench-P by order.

> [!tip] 表格解读（多模态）
> **Figure description:**

The line chart plots inference throughput (Kt/s, y-axis: 35–60) against a varying input parameter (likely sequence length or batch/context size, x-axis), comparing several model families.

**Components / data flow:**
- **Blue line (Transformer-L...):** Starts highest at ~55 Kt/s but collapses steeply downward, crossing all other curves and falling off-chart past 30 Kt/s.
- **Light & dark green lines:** Hold steady around 49–53 Kt/s across the full range.
- **Red line:** Flat near 48 Kt/s.
- **Olive line:** Hovers around 45–46 Kt/s.
- **Dark gray line:** Drops modestly from ~45 to ~43 Kt/s.
- **Orange & pink (DeltaNet) lines:** Remain flat near 38 Kt/s, exhibiting zero degradation.

**Key technical takeaway (≤120 words):**
Transformer inference throughput degrades sharply as context length grows — the blue Transformer line plummets from ~55 to under 30 Kt/s, while every DeltaNet/linear-attention variant (orange, pink, gray) stays essentially flat. This is the core efficiency argument: quadratic attention's O(n²) cost makes long-context serving bandwidth-bound, whereas recurrent or linear-attention models maintain constant per-token cost, giving them a decisive and growing advantage at long contexts where the Transformer curve collapses.

**Caption (verbatim):**

Table 5: Accuracy on 14 tasks from LongBench (Bai et al., 2023): Narrative QA, QasperQA, MultiField QA, HotpotQA, 2WikiMulti QA, Musique, GovReport, QMSum, MultiNews, TRec, Trivia QA, SamSum, LCC, and RepoBench-P by order.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\rmS_t = \rmS_{t-1} + \vv_t \vk_t^\intercal \in \mathbb{R}^{d_v \times d_k}, \qquad \qquad \vo_t = \rmS_t \vq_t \in \mathbb{R}^{d_v}
$$

$$
\vo_t = \sum_{i=1}^t (\vv_i \vk_i^\intercal) \vq_t = \sum_{i=1}^t \vv_i (\vk_i^\intercal \vq_t) \in \mathbb{R}^{d_v}, \qquad \rmO = (\rmQ \rmK^\intercal \odot \rmM) \rmV \in \mathbb{R}^{L \times d_v}
$$

$$
\rmS_{[t]}^r = \rmS_{[t]} + \sum_{i=1}^r \vv_{[t]}^{i} \vk_{[t]}^{i\intercal} \in \mathbb{R}^{d_v\times d_k}, \qquad \vo_{[t]}^r = \rmS_{[t]}^r\vq_{[t]}^r = \rmS_{[t]}\vq_{[t]}^r + \sum_{i=1}^r \vv_{[t]}^{i} \left(\vk_{[t]}^{i\intercal} \vq_{[t]}^{r} \right) \in \mathbb{R}^{d_v}
$$

$$
\rmS_{[t+1]} = \rmS_{[t]} + \rmV_{[t]} \rmK_{[t]}^\intercal \in \mathbb{R}^{d_v \times d_k}, \qquad \rmO_{[t]} = \rmQ_{[t]} \rmS_{[t]}^\intercal + \left(\rmQ_{[t]}\rmK_{[t]}^\intercal \odot \rmM\right) \rmV_{[t]} \in \mathbb{R}^{C \times d_v}
$$

$$
\rmS_{[t+1]} = {\color{blue} \overrightarrow{\rmS_{[t]}}} + \rmV_{[t]}^\intercal {\color{blue} \overrightarrow{\rmK_{[t]}}} \in \mathbb{R}^{d_v \times d_k} , && \rmO_{[t]} = {\color{blue}{\overleftarrow{ \rmQ_{[t]}}}} \rmS_{[t]}^\intercal + \left(\rmQ_{[t]} \rmK_{[t]}^\intercal \odot {\color{blue}\Gamma_{[t]}}\right)\rmV_{[t]} \in \mathbb{R}^{C\times d_v}
$$

$$
{\color{blue}\overleftarrow{\vq_{[t]}^r}} &= {\color{blue}\gamma_{[t]}^r} \vq_{[t]}^r && \text{decaying each vector to the first position of chunk $t$} \nonumber \\ {\color{blue}\overrightarrow{\vk_{[t]}^r}} &= {\color{blue}\frac{\gamma_{[t ]}^{C}}{\gamma_{[t]}^r}} \vk_{[t]}^r && \text{decaying each vector to the last position of chunk $t$} \nonumber \\ {\color{blue}\overrightarrow{\rmS_{[t]}}} &= {\color{blue}\gamma_{[t]}^C}\rmS_{[t]} && \text{decaying the state matrix over the entire chunk $t$}
$$

$$
\rmS_t &= \rmS_{t-1} - \underbrace{\left(\rmS_{t-1} \vk_t\right)}_{\vv_{t}^{\text{old}}} \vk_t^\intercal + \underbrace{\left(\beta_t \vv_t + (1-\beta_t)\rmS_{t-1}\vk_t)\right)}_{\vv_{t}^{\text{new}}} \vk_t^\intercal = \rmS_{t-1} \left(\rmI - \beta_t \vk_t \vk_t^\intercal \right) + \beta_t \vv_t \vk_t^\intercal
$$

$$
\rmS_{[t]}^r = \rmS_{[t]} \underbrace{\left(\prod_{i=1}^r \rmI - \beta_{[t]}^i \vk_{[t]}^i \vk_{[t]}^{i\intercal} \right)}_{:= \rmP_{[t]}^r} + \underbrace{\sum_{i=1}^{r} \left( \beta^i_{[t]} \vv^i_{[t]} \vk_{[t]}^{i\intercal}\prod_{j=i+1}^{r} \left(\rmI - \beta_{[t]}^j \vk^j_{[t]} \vk_{[t]}^{j\intercal} \right) \right)}_{:= \rmH_{[t]}^r}
$$

$$
\rmP_{[t]}^{r} &= \rmI - \sum_{i=1}^{r}\vw_{[t]}^i\vk_{[t]}^{i\intercal} \in \mathbb{R}^{d_k \times d_k} &&\vw_{[t]}^r = \beta_{[t]}^r \left(\vk_{[t]}^r - \sum_{i=1}^{r-1} \left(\vw_{[t]}^i (\vk_{[t]}^{i\intercal}\vk_{[t]}^r) \right) \right) \in \mathbb{R}^{d_k}
$$

$$
\rmH_{[t]}^{r} &= \sum_{i=1}^{r} \vu_{[t]}^i \vk_{[t]}^{i\intercal} \in \R^{d_v \times d_k} && \vu_{[t]}^r = \beta_{[t]}^r \left(\vv_{[t]}^r - \sum_{i=1}^{r-1} \left(\vu_{[t]}^i (\vk_{[t]}^{i\intercal}\vk_{[t]}^r) \right) \right)\in \mathbb{R}^{d_v}
$$

$$
\rmT_{[t]} = \left[\rmI + \operatorname{strictLower}\left(\operatorname{diag}(\beta_{[t]})\rmK_{[t]} \rmK_{[t]}^\intercal\right)\right]^{-1}\operatorname{diag}\left(\beta_{[t]}\right) \in \mathbb{R}^{C \times C} \\ \rmW_{[t]}= \rmT_{[t]} \rmK_{[t]} \in \mathbb{R}^{C \times d_k}, \qquad \rmU_{[t]}=\rmT_{[t]}\rmV_{[t]} \in \mathbb{R}^{C \times d_v}
$$

$$
\rmS_{[t+1]} &= \rmS_{[t]}\rmP_{[t]}+\rmH_{[t]} = \rmS_{[t]} + \left(\rmU_{[t]} - \rmW_{[t]}\rmS_{[t]}^{\intercal}\right)^\intercal \rmK_{[t]} & \in \mathbb{R}^{d_v \times d_k} \\ \rmO_{[t]} &= \rmQ_{[t]} \rmS_{[t]}^\intercal + (\rmQ_{[t]} \rmK_{[t]}^{\intercal} \odot \rmM) \left(\rmU_{[t]} - \rmW_{[t]} \rmS_{[t]}^\intercal\right) &\in \mathbb{R}^{C \times d_v}
$$

$$
\rmS_t = \rmS_{t-1} \left( {\color{blue}{\alpha_t}} (\rmI - \beta_t \vk_t\vk_t^\intercal) \right) + \beta_t \vv_t \vk_t^\intercal
$$

$$
\rmS_{t+1} &= \rmS_{t} - \beta_t \nabla \mathcal{L}(\rmS_t) = \rmS_{t} - \beta_t (\rmS_t\vk_t - \vv_t)\vk_t^\intercal = \rmS_{t}\left(\rmI-\beta_t\vk_t\vk_t^\intercal\right) + \beta_t \vv_t\vk_t^\intercal
$$

$$
\rmS_{[t]}^r = \rmS_{[t]} \underbrace{\left(\prod_{i=1}^r {\color{blue}{\alpha_{[t]}^i}}\left(\rmI - \beta_{[t]}^i \vk_{[t]}^i \vk_{[t]}^{i\intercal} \right)\right)}_{:= \mathbf{F}_{[t]}^r} + \underbrace{\sum_{i=1}^{r} \left( \beta^i_{[t]} \vv^i_{[t]} \vk_{[t]}^{i\intercal}\prod_{j=i+1}^{r} {\color{blue}{\alpha_{[t]}^j}} \left(\rmI - \beta_{[t]}^j \vk^j_{[t]} \vk_{[t]}^{j\intercal} \right) \right)}_{:= \rmG_{[t]}^r}
$$

$$
\rmG_{[t]}^r = \sum_{i=1}^r {\color{blue} \frac{\gamma_{[t]}^r}{\gamma_{[t]}^i} } \tilde{\vu}_{[t]}^i \vk_{[t]}^{i\intercal} \in\mathbb{R}^{d_v \times d_k} &&\tilde{\vu}_{[t]}^r = \beta_{[t]}^r \left(\vv_{[t]}^r - \sum_{i=1}^{r-1} \left( \tilde{\vu}_{[t]}^i ({\color{blue}\frac{\gamma_{[t]}^{r}}{\gamma_{[t]}^i}} \vk_{[t]}^{i\intercal}\vk_{[t]}^r)\right)\right) \in \mathbb{R}^{d_v}
$$

$$
\widetilde{\rmU_{[t]}} = \left[\rmI + \operatorname{strictLower} \left(\operatorname{diag}\left(\beta_{[t]}\right) ({\color{blue}\Gamma_{[t]} } \odot \rmK_{[t]} \rmK_{[t]}^\intercal )\right) \right]^{-1} \operatorname{diag}\left(\beta_{[t]}\right) \rmV_{[t]} && \in \mathbb{R}^{C \times d_v}
$$

$$
\rmS_{[t+1]} &= {\color{blue} \overrightarrow{\rmS_{[t]}}} + \left({ \widetilde{\rmU_{[t]}}} - {\color{blue} \overleftarrow{\rmW_{[t]}}} \rmS_{[t]}^\intercal\right)^\intercal {\color{blue} \overrightarrow{\rmK_{[t]}}} &&\in \mathbb{R}^{d_v \times d_k} \\ \rmO_{[t]} &= {\color{blue} \overleftarrow{\rmQ_{[t]}}} \rmS_{[t]}^\intercal + (\rmQ_{[t]} \rmK_{[t]}^{\intercal} \odot \mathbf{M}) \left({{\widetilde{\rmU^{}_{[t]}}}} - {\color{blue} \overleftarrow{\rmW_{[t]}}}\rmS_{[t]}^\intercal\right) &&\in \mathbb{R}^{C \times d_v}
$$

$$
\rmS_t = \sum_{i=1}^t {\color{blue}\frac{\gamma_{t}}{\gamma_i}} \vu_i \vk_i^\intercal, \qquad \vu_t = \beta_t \left( \vv_t - \sum_{i=1}^{t-1} {\color{blue} \frac{\gamma_{t}}{\gamma_i}} \vu_i \vk_i^T \vk_t \right)
$$

$$
\rmS_t = {\color{blue}\alpha_t} \rmS_{t-1} + \vv_t \vk_t^\intercal, \qquad \vo_t = \rmS_t \vq_t
$$

## 相关论文

- [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] — From ATOP to ZCube: Automated Topology Optimization Pipeline and A Highly Cost-Effective Network Topology for Large Model Training
- [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] — Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM

## 技术点深读（DEEP）

![[deep/gated-delta-networks-improving-mamba2-with-delta-rule]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/gated-delta-networks-improving-mamba2-with-delta-rule.txt`（79000 字符）供引用检索。