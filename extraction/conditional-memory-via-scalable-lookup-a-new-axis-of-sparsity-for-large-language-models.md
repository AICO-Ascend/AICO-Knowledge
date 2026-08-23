---
paper_num: "35"
title: "Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models"
authors: "A New Axis of Sparsity for Large Language Models Xin Cheng1,2∗, Rui Tian2∗, Wangding Zeng2, Damai Dai2, Qinyu Chen2, Bingxuan Wang2, Zhenda Xie2, Kezhao Huang2, Xingkai Yu2 Chengqi Deng2, Shangyan Zhou2, Chenggang Zhao2,"
date: "2026/1/17"
arxiv: "https://arxiv.org/abs/2601.07372"
pdf: "papers/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models.pdf"
slug: "conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models"
tags: []
---

# Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models

> [!abstract] 摘要（原文）
> 1\. 💡 论文引入条件记忆作为 LLMs 稀疏性的补充轴，通过 Engram 模块实现，该模块利用现代化的 N-gram 嵌入提供 O(1) 知识查找，以解决 Transformer 在静态知识检索上的低效问题。 2. 🔬 通过对稀疏性分配问题的研究，作者发现 MoE（神经计算）和 Engram（静态记忆）之间存在 U 形缩放定律，混合分配能严格超越纯 MoE，在 iso-parameter 和 iso-FLOPs 的对比下，Engram-27B 在推理、代码和数学任务上表现更优。 3. 🚀 机制分析显示 Engram 有效减轻了早期层级的静态重建负担，从而加深了网络的有效深度并释放了注意力容量以处理全局上下文，实现了卓越的长上下文处理能力，同时其确定性寻址还支持基础设施感知的运行时预取，实现了显著的系统效率。

## 元信息
- **发表日期**: 2026/1/17
- **作者**: A New Axis of Sparsity for Large Language Models Xin Cheng1,2∗, Rui Tian2∗, Wangding Zeng2, Damai Dai2, Qinyu Chen2, Bingxuan Wang2, Zhenda Xie2, Kezhao Huang2, Xingkai Yu2 Chengqi Deng2, Shangyan Zhou2, Chenggang Zhao2,
- **arXiv**: https://arxiv.org/abs/2601.07372
- **本地 PDF**: `papers/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models.pdf`
- **页数**: 35

## 图表（原文 caption + 页码）

### Figure 2 (p.6) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-fig02.png]]
*整页渲染: ![[assets/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-p06.png]]*
> [!quote] caption
> During training, to accommodate large-scale embedding tables, we employ standard model parallelism by sharding the tables across available GPUs. An All-to-All communication primitive is used to gather active rows in the forward pass and dispatch gradients in the backward pass, enabling the total memory capacity to scale linearly with the number of accelerators.

> [!tip] 技术解读（多模态）
> **Architecture & Data Flow**

**(a) Training:** Input IDs → Vocab Embedding → Transformer Block → stack of {Engram → Attention → MoE} layers, each with residual connections. Two parallel Engram stacks are connected via an **All2All** link (likely for Mixture-of-Experts/expert routing across devices).

**(b) Inference:** Same logical layout — Vocab Embedding → alternating *Transformer Block* and *Transformer Block with Engram* — but the Engram parameters are **offloaded to host memory** (cylinder labeled "Offloaded Engram / Memory Hierarchy") and pulled into device memory only when a layer needs them (dashed arrows), separating **on-device computation** from **on-host communication**.

**Key Technical Takeaway (≤120 words):**
Engrams act as auxiliary, non-attention modules that fuse token-level memorization with contextual processing. During training, they sit alongside Attention+MoE with All2All expert routing; during inference, the large Engram lookup tables are offloaded to host memory and streamed on demand, so the device only holds the active layers. This decouples *capacity* (host-side memory hierarchy) from *compute* (device-side stack), enabling much larger embedding/memorization capacity without inflating on-device footprint or breaking the trained topology.

**Caption (verbatim):**
**(a) Engram at training**    **(b) Engram at inference**

### Figure 5 (p.16) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-fig05.png]]
*整页渲染: ![[assets/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-p16.png]]*
> [!quote] caption
> We find that three components yield the most significant gains: (i) branch- specific fusion within the multi-branch backbone, (ii) context-aware gating, and (iii) tokenizer compression. Removing any of these causes the largest regressions in validation loss. Specifically, for the “w/o multi branch” ablation, we retain the mHC backbone structure but replace the branch-specific gating with a single 

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Architecture/Components:**
The chart compares validation loss across two reference baselines — a **3B MoE baseline** (top, orange dashed, ≈1.808) and a **3B MoE + 1.6B Engram** hybrid (bottom, green dashed, ≈1.768) — against a layer-sweep curve (navy) of the same hybrid architecture inserted at layers 1–12. The right side reports ablation variants (w/o multi-branch, w/o token compression, w/o gating, +4-gram, w/o short-conv) as scatter markers. The y-axis is broken between ~1.785 and ~1.805 to highlight the narrow operating range.

**Key Technical Takeaway (≤120 words):**
Inserting a 1.6B-parameter Engram memory module alongside a 3B MoE backbone yields a consistent validation-loss reduction (~0.04 nats) regardless of injection depth, with **early-to-mid layers (1–2) producing the best results** (~1.770). Loss degrades monotonically as the module is pushed deeper, confirming that **memory benefits compound most when placed near the embedding/input layers** rather than deeper in the stack. All ablations underperform the full hybrid, indicating that multi-branch routing, token compression, gating, and short-conv components are jointly necessary for optimal performance.

## Verbatim Caption / Text Transcription

*No explicit figure caption is present in the image. Transcribing all visible text elements verbatim:*

- **Y-axis label:** Validation Loss
- **X-axis label:** Layer Index / Ablation Variations
- **Top reference line annotation:** "3B MoE Baseline"
- **Bottom reference line annotation:** "3B MoE + 1.6B Engram"
- **Legend entry:** "3B MoE + 1.6B Engram (Layer Sweep)"
- **Ablation markers (right side):** "w/o multi branch", "w/o token compress", "w/o gating", "+ 4-gram", "w/o short conv"

### Figure 7 (p.18) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-fig07.png]]
*整页渲染: ![[assets/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-p18.png]]*
> [!quote] caption
> The results demonstrate a distinct pattern of selectivity. The gating mechanism consistently activates (shown in red) upon completing local, static patterns. In English, we observe strong activations on multi-token named entities (e.g., “Alexander the Great”, “the Milky Way”) and formulaic phrases (e.g., “By the way”, “Princess of Wales”). This behavior generalizes effectively across languages. In

> [!tip] 技术解读（多模态）
> # Figure Description

**Architecture/Components/Data Flow:**
The figure is a **token-level heatmap** showing five example sentences (three English, two Chinese), each preceded by a `<bos>` (beginning-of-sequence) token. A vertical colorbar on the left maps values from 0.0 (white) → 1.0 (deep red). Each sentence is rendered as a horizontal row where individual tokens (subwords for English, characters for Chinese) are shaded according to an importance/selection score. Darker red tokens correspond to higher scores; lighter/near-white tokens correspond to lower scores.

Visually, semantically rich or "key concept" tokens (e.g., *Alexander, the Great, Bucephalus, Milky Way, Diana, Princess of Wales, 造纸术, 指南针, 张仲景, 医圣, 伤寒杂病论*) are highlighted in deep red, while function words and punctuation (*could, of, the, , , .*) fade toward white. The same `<bos>` marker consistently carries moderate emphasis.

**Data Flow:** raw text → tokenization (BPE/word-piece for English, character-level for Chinese) → per-token scalar scoring model → rendered as a color-graded token strip, evaluated across multiple languages to demonstrate cross-lingual behavior.

**Key Technical Takeaway (≤120 words):**
The visualization demonstrates that the underlying scoring mechanism produces **language-agnostic, semantically aligned token importance** — content-bearing words (named entities, domain-specific terms) are consistently up-weighted while function tokens and punctuation are suppressed, regardless of whether the input is English or Chinese. Notably, subword fragments (e.g., *B / uce / phalus*) each receive partial weight, indicating that importance is distributed across the tokenizer's segmentation rather than at the word level. The uniform treatment of `<bos>` and parallel behavior across scripts suggests the method generalizes without language-specific retraining.

# Verbatim Caption / In-Image Text

There is no descriptive figure caption printed in the image. The only textual elements present are:

- Colorbar tick label (top): `1.0`
- Colorbar tick label (bottom): `0.0`
- Row 1: `<bos> Only Alexander the Great could tame the horse B uce phal us .`
- Row 2: `<bos> By the way , I am a fan of the Milky Way .`
- Row 3: `<bos> This study analyzes the media impact of Diana , Princess of Wales .`
- Row 4: `<bos> 中国 四大 发明 包括 ： 造纸 术 、 指南 针 、 火药 和 印刷 术 。`
- Row 5: `<bos> 东汉 末年 名医 张仲景 ， 因其 卓越 的 贡献 被 后世 尊 为 ' 医圣 ' ， 并 著名 有 传世 巨 作 《 伤寒 杂病 论 》。`

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.9) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-tab01.png]]
> [!quote] caption
> | Pre-training performance comparison between dense, MoE, and Engram models . All models are trained for 262B tokens and are matched in activated parameters (3.8B). Engram-27B is iso-parameters with MoE-27B by reallocating parameters from routed experts (72 → 55) to a 5.7B-parameter Engram memory. E

> [!tip] 表格解读（多模态）
> **Description:**
This is a benchmark comparison table (Table 1) evaluating four pre-trained language model variants — **Dense-4B**, **MoE-27B** (2 shared + 72 routed experts, top-6), **Engram-27B** (2 shared + 55 routed experts + 5.7B Engram memory), and **Engram-40B** (same routing + 18.5B Engram memory) — all matched at 3.8B activated parameters and trained on 262B tokens. Rows are grouped into **Language Modeling** (Pile loss, Validation loss) and **Knowledge & Reasoning** (MMLU family, CMMLU, ARC, TriviaQA, BBH, HellaSwag, PIQA, WinoGrande, etc.). Engram-27B (bolded as best in most rows) outperforms MoE-27B on nearly every task, and Engram-40B extends these gains further.

**Key takeaway:** Reallocating routed-expert parameters into an Engram memory improves pre-training quality uniformly over an iso-activation MoE, with monotonic gains as memory scales from 5.7B → 18.5B (≈120 words).

**Caption (verbatim):**
"Table 1 | Pre-training performance comparison between dense, MoE, and Engram models. All models are trained for 262B tokens and are matched in activated parameters (3.8B). Engram-27B is iso-parameters with MoE-27B by reallocating parameters from routed experts (72 → 55) to a 5.7B-parameter Engram memory. Engram-40B further increases Engram memory (18.5B parameters) while keeping the activated-parameter budget fixed. Full training-time benchmark trajectories are reported in Appendix B."

### Table 2 (p.11) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-tab02.png]]
> [!quote] caption
> | Long-context performance comparison. Parenthetical values (e.g. (50k, 1.62) ) denote the pre-training steps and the corresponding loss prior to the long-context extension. Two key findings: (1) With only 82% of the pre-training FLOPs (41k vs. 50k), Engram-27B matches the baseline’s LongPPL ( Fang 

> [!tip] 表格解读（多模态）
> **Main figure (Table 2 — a results comparison table, not a diagram) — structure & key takeaway (≤120 words):**

The table contrasts MoE-27B against three Engram-27B checkpoints (41k / 46k / 50k pre-training steps) on 32k-token context evaluation, split into two metric blocks: **LongPPL** (Perplexity ↓ on Book, Paper, Code, L-CoT) and **RULER** (NIAH accuracy ↑ on S/MK/MV/MQ plus Other Tasks ↑ on VT, CWE, FWE, QA). Each row's parenthetical lists (pretraining steps, pre-extension loss). Bold marks best, underline marks second-best.

**Key takeaway:** Engram-27B is Pareto-superior. With only 82% of pre-training FLOPs (41k vs 50k), it *matches* MoE-27B's LongPPL and *beats* it on most RULER tasks (notably +9.5 on MQ, +26.6 on FWE, +9.5 on QA). At iso-FLOPs (50k), Engram dominates every metric.

**Transcribed data table:**

| Model | Book ↓ | Paper ↓ | Code ↓ | L-CoT ↓ | NIAH S ↑ | NIAH MK ↑ | NIAH MV ↑ | NIAH MQ ↑ | VT ↑ | CWE ↑ | FWE ↑ | QA ↑ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MoE-27B (50k, 1.63) | 4.38 | 2.91 | 2.49 | 14.16 | **100.0** | 88.0 | 92.7 | 84.2 | 77.0 | 4.5 | 73.0 | 34.5 |
| Engram-27B (41k, 1.66) | 4.37 | 2.92 | 2.50 | 14.26 | 99.6 | 88.3 | 93.0 | 89.5 | 83.2 | 3.8 | 99.6 | 44.0 |
| Engram-27B (46k, 1.63) | 4.19 | 2.84 | 2.45 | 13.59 | 97.6 | 89.0 | 95.5 | 97.0 | 87.2 | 4.3 | 98.6 | 37.5 |
| Engram-27B (50k, 1.62) | **4.14** | **2.82** | **2.44** | **13.41** | 99.3 | 89.3 | 96.5 | 97.0 | 89.0 | 5.9 | 99.3 | 40.5 |

*Bold values retained from the source; second-best positions (per the "underline" convention) are: Book 4.19, Paper 2.84, Code 2.45, L-CoT 13.59, NIAH MK 89.0, NIAH MV 95.5, NIAH MQ 97.0, VT 87.2, CWE 4.5, FWE 98.6, QA 37.5.*

**Caption (transcribed verbatim):**

Table 2 | **Long-context performance comparison**. Parenthetical values (e.g. (50k, 1.62)) denote the pre-training steps and the corresponding loss prior to the long-context extension. Two key findings: (1) With only 82% of the pre-training FLOPs (41k vs. 50k), Engram-27B matches the baseline's LongPPL (Fang et al.) performance while achieving significantly higher accuracy on RULER (Hsieh et al.); (2) Under both iso-pretraining-loss (46k) and iso-pretraining-FLOPs (50k) settings, Engram-27B substantially outperforms the baseline across all metrics. **Bold** indicates the best and <u>underline</u> the second.

### Table 4 (p.18) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-tab04.png]]
> [!quote] caption
> | End-to-end Inference Throughput . We measure infernece throughput with a 100B- parameter Engram layer entirely offloaded to host memory.

> [!tip] 表格解读（多模态）
> **Figure description:**
The figure is **Table 4**, a structured "Experimental Setup" table with two columns. It lists three configuration rows: **Hardware** (NVIDIA H800), **Workload** (512 Sequences), and **Sequence Length** (Uniform(100, 1024)). A partial horizontal rule at the bottom indicates the table continues with throughput results below the visible crop.

**Key technical takeaway:**
Offloading a 100B-parameter Engram layer entirely to host (CPU) memory still permits measurement of end-to-end inference throughput, suggesting the architecture is designed to evaluate memory-efficient inference without requiring the full parameter set resident on GPU.

**Caption transcribed verbatim:**
Table 4 | End-to-end Inference Throughput. We measure inference throughput with a 100B-parameter Engram layer entirely offloaded to host memory.

### Table 5 (p.33) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-tab05.png]]
> [!quote] caption
> | Detailed model architecture information and training hyper parameters.

> [!tip] 表格解读（多模态）
> # Description of Table 5

Based on the visible content, only the caption appears in the image; the actual table rows/columns are not rendered. The caption states this is **Table 5**, titled "Detailed model architecture information and training hyper parameters," and the page number 33 is shown at the bottom of the page.

**Expected table structure** (typical for such a caption in ML papers):
- **Components/columns**: Layer name → Layer type (Conv2d, Linear, BN, ReLU, etc.) → Output tensor shape → Kernel/stride/padding → Parameters
- **Sections**: Backbone feature extractor → Neck → Detection/segmentation head; second mini-table for optimizer (SGD/Adam), learning rate, momentum, weight decay, batch size, epochs, augmentation settings.

## One key technical takeaway

A "detailed hyperparameter table" typically reveals the **training recipe that disproportionately drives results** — e.g., optimizer/learning-rate schedule, augmentation pipeline, and loss-weight assignments — which is often more impactful than architectural novelty. Reproducibility hinges on these values.

## Caption (verbatim)

> **Table 5 | Detailed model architecture information and training hyper parameters.**

### Table 6 (p.35) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-tab06.png]]
> [!quote] caption
> | The table illustrates Top-5 merged tokens by Tokenizer Compression and the overall compression ratio is 23.43% for our 128k tokenizer.

> [!tip] 表格解读（多模态）
> **Description**

The figure is a tabular listing of the Top-5 most frequent merged tokens produced by a trained 128k subword tokenizer. Each row contains: (1) a rank index, (2) a token frequency count, and (3) the canonical token form followed by representative merged variants — typically a base character plus its whitespace-prefixed counterpart and accented/case variants (e.g., `'a'` merged with `'A'`, `'ㅁa'`, `'ㅁA'`, `'á'`, `'ã'`, etc.). The top token (163 occurrences) is whitespace `' '` merged with newlines, carriage returns, and tab/return combinations, indicating whitespace/punctuation dominates merges. Vowel tokens (`'a'`, `'o'`, `'e'`, `'i'`) follow at 54/40/35/30 counts respectively.

**Key technical takeaway:** The tokenizer aggressively merges whitespace and casing/diacritic variants of the same underlying character, yielding a 23.43% compression ratio — a strong signal that the corpus is whitespace-heavy and that case/accent normalization at the subword level substantially reduces sequence length without losing semantic content.

**Caption (verbatim):**

> Table 6 | The table illustrates Top-5 merged tokens by *Tokenizer Compression* and the overall compression ratio is 23.43% for our 128k tokenizer.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\text{CKA}(K, L) = \frac{\text{HSIC}(K, L)}{\sqrt{\text{HSIC}(K, K)\text{HSIC}(L, L)}}
$$

$$
a_j = \frac{\sum_{i \in \mathcal{I}_j} S_{i,j} \cdot i}{\sum_{i \in \mathcal{I}_j} S_{i,j}}, \quad \text{where } \mathcal{I}_j = \mathop{\text{argtop}k}_{i} (S_{i,j}).
$$

$$
z_{t,n,k} \triangleq \phi_{n,k}(g_{t,n}), \quad \mathbf{e}_{t,n,k} = \mathbf{E}_{n,k}[z_{t,n,k}].
$$

$$
\mathbf{e}_t \triangleq \mathop{\Vert}_{n=2}^{N} \mathop{\Vert}_{k=1}^{K} \mathbf{e}_{t,n,k}.
$$

$$
\mathbf{k}_t = \mathbf{W}_K \mathbf{e}_t, \quad \mathbf{v}_t = \mathbf{W}_V \mathbf{e}_t
$$

$$
\alpha_t = \sigma\left( \frac{\text{RMSNorm}(\mathbf{h}_t)^\top \text{RMSNorm}(\mathbf{k}_t)}{\sqrt{d}} \right).
$$

$$
\mathbf{Y} = \text{SiLU}\left( \text{Conv1D}( \text{RMSNorm}(\tilde{\mathbf{V}}) ) \right) + \tilde{\mathbf{V}},
$$

$$
\alpha_t^{(m)} = \sigma\left( \frac{\text{RMSNorm}(\mathbf{h}_t^{(m)})^\top \text{RMSNorm}(\mathbf{W}_K^{(m)} \mathbf{e}_t)}{\sqrt{d}} \right).
$$

$$
P_{\mathrm{MoE}}^{(\mathrm{sparse })} = \rho\, P_{\mathrm{sparse}}, \qquad P_{\mathrm{Engram}} = (1-\rho)\, P_{\mathrm{sparse}}.
$$

## 技术点深读（DEEP）

![[deep/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models.txt`（100228 字符）供引用检索。