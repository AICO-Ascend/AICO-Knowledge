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
> 【图文联合解读】**图文联合解读：**

图(a)展示DLCM总览结构：输入token经编码器（蓝色圆角模块）后，通过Q查询机制映射至4个概念槽C₁–C₄（内含a、ba、bn等字符符号），再经后续"MH"模块继续处理。图(b)展示边界检测与池化：token序列(s、B、b、a、o、b、bn)按阈值K动态切分边界，池化为C₁–C₄四个概念。

原文借此论证：DLCM以"概念"（concept）替代传统token作为推理粒度，通过边界检测自适应分块、Q查询检索形成潜变量序列，实现语义空间中的动态推理。该图作为全文方法基石，为Table 1预训练数据统计与下游对比实验提供架构锚点。

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

### Table 2 (p.15) ⭐深度解读
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-tab02.png]]
> [!quote] caption
> Performance Comparison: DLCM vs. Baseline. Zero-shot accuracy (%) categorized by task type. Improvements are shown in green and regressions in red .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读**

**1) 核心对象与数据：** 该表展示 DLCM 与 Baseline 在 12 项零样本基准任务上的准确率（%）对比，按 MMLU 类（8 项）、阅读理解（2 项）、中文（2 项）三类组织。DLCM 平均得分 43.92%，Baseline 41.23%，整体 +2.69%。MMLU 类中 OpenBookQA（+3.00）、ARC Easy（+2.61）、PIQA（+2.42）提升最大；阅读理解类两项均下降（BoolQ -1.47、RACE -0.72）；中文任务表现参差（C-Eval +1.71，CMMLU -0.24）。

**2) 关键技术结论：** 论文据此论证"在自适应语义潜空间做推理"的 DLCM 在多数任务上系统性地优于标准 Transformer 基线，**尤其是常识/知识类推理任务获益最显著**，而涉及长文本精确比对（阅读理解）的任务略逊，揭示了潜空间聚合在长跨度检索上的局限。

**3) 在论文中的作用：** 作为主实验证据，承接第 3.6 节"ragged-boundary 注意力掩码"（Figure 2）所示结构设计与第 4 节方法论述，并以 Table 2 的整体平均增益 +2.69% 量化支撑"自适应语义潜空间推理"方案的有效性，与 Figure 9 的加速比共同构成"性能-效率"双线验证。

### Table 3 (p.16) ⭐深度解读
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-tab03.png]]
> [!quote] caption
> Architecture Configuration Details. A unified view of the parameter settings for Baseline (LLaMA-1.3B) and DLCM (2.3B). Values are presented as Baseline / Ours .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读：**

该表以"Baseline / DLCM"并列形式，对比LLaMA-1.3B与DLCM-2.3B的架构配置，分四模块呈现：

- **General**：DLCM参数量2.3B（≈1.8×基线），共享Vocab=128,815、Max Pos=8k、Swish激活；
- **Dimension**：DLCM新增Main Hidden *dₚ*=3,072，自/交叉注意中间层均扩至6,144；
- **Layer**：DLCM将32层重构为Encoder 10 + Backbone 16 + Decoder 6三段式；
- **Attention**：DLCM保留24个Attn Heads但KV Heads减半至12，Backbone独立48 Heads / 24 KV Heads。

**技术结论**：DLCM并非简单堆叠参数，而是通过编码器-骨干-解码器分层与双维度隐藏设计，将推理从token级拓展至concept级潜在语义空间。**作用**：为后续性能/效率实验提供公平架构对照基线，验证"自适应语义空间潜在推理"设计而非单纯增大模型即可带来增益。

### Table 4 (p.17) ⭐深度解读
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-tab04.png]]
> [!quote] caption
> Ablation Study: Global Parser vs. Normal. Performance comparison on downstream tasks. Both models aim for a target compression ratio of R = 4 . The Global Parser achieves a realized ratio much closer to the target while consistently improving accuracy on most tasks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表格解读：**

**1) 核心数据**：表4在目标压缩比 R=4 下，对比 Global Parser 与 Normal 两种解析策略在 6 项下游任务上的 Acc：ARC-C（0.3038 vs 0.2858）、ARC-E（0.6296 vs 0.6242）、CSQA（0.2457 vs 0.2228）、HellaSwag（0.3507 vs 0.3499）、OpenBookQA（0.3220 vs 0.3280）、PIQA（0.6806 vs 0.6785），平均提升 +2.1%；实际压缩比 3.92 vs 3.15。

**2) 关键结论**：Global Parser 在多数任务上精度更优（5/6 胜），且实际压缩比 3.92 更逼近目标 R=4，证明全局解析策略既能稳定压缩、又能保留判别性语义。

**3) 论文作用**：作为消融实验，验证"全局解析"是该自适应语义空间方法的关键设计，对"动态概念建模"主线起到设计选择合理性的支撑作用。

### Table 5 (p.18) ⭐深度解读
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-tab05.png]]
> [!quote] caption
> Average tokens per concept across content types and compression ratios. Values represent the actual granularity achieved for each target compression setting.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 5 展示六类内容（Casual 中/英、Technical 中/英、Code、Math/Science）在 Target 8/4/2 三档压缩下的实际"每概念平均 token 数"：Target 8 跨度 6.09–10.58（Technical English 最高），Target 4 收窄至 3.27–4.41（Math/Science 最高 4.41），Target 2 趋近均匀的 1.76–2。

关键结论：实际粒度随压缩目标自适调整——低压缩对粗概念（≈10 token），高压缩对细且均匀颗粒（≈2 token），跨内容类型差异随压缩加深而收敛，证明动态语义空间具备按需细分化能力。

论文作用：作为结论处的核心实证，支撑"自适应潜在推理"主张，验证模型在不同语料/压缩设置下均能稳定控制概念粒度。

### Table 6 (p.7) ⭐深度解读
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-tab06.png]]
> [!quote] caption
> Performance comparison (Batch=1, Heads=32, Interval=6)

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 6 在 Batch=1、Heads=32、Interval=6 固定配置下对比 Flex 与 Flash Varlen 两种注意力实现。表中前两列（误标 Seq Length/Hidden Size）实为二者实际延迟（ms），"Flex (ms)" 列为加速比（1.26×–1.73×），后两列依次为扫描序列长度（2K/4K/8K/16K）与隐藏维度（1K/2K/4K）。

核心发现：Flex 在全部 12 组配置中均快于 Flash Varlen；序列越长优势越显著（16K 时达 1.66×–1.73×），短序列（2K）下收窄至 1.44×–1.48×，整体呈稳定单调加速。

该表用以论证 Flex 注意力机制的可靠性，是论文"动态概念建模"高效潜在推理链路的工程基石；配合 Figure 9 的速度比趋势曲线，共同支撑"自适应语义空间下推理高效性"这一核心结论。

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