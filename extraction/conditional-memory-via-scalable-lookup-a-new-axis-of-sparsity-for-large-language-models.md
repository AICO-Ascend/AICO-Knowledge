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
> I notice the figure you're asking about (Figure 2) is **referenced in the text but not actually displayed on this page**. The provided image contains only text content from page 6 of the paper — specifically:

- The tail of Section 2.4 (ending with the retrieval modulation formula **u**ₜ⁽ᵐ⁾ = αₜ⁽ᵐ⁾ · (**W**_V **e**_ₜ))
- Section 2.5 "System Efficiency: Decoupling Compute and Memory"
- Section 3 "Scaling Laws and Sparsity Allocation"

The page mentions *"as illustrated in Figure 2"* when discussing Engram's training/inference optimization strategies, but the figure itself is not rendered in the image you shared.

**What I can infer about Figure 2 from the text** (≤120 words):

> Figure 2 illustrates Engram's specialized optimization strategies for training and inference. For training, it depicts standard model parallelism with sharded embedding tables across GPUs using an All-to-All communication primitive (gathering active rows forward, dispatching gradients backward), enabling linear memory scaling with accelerators. For inference, it shows a prefetch-and-overlap strategy: since memory indices are known beforehand, embeddings are asynchronously fetched from host memory via PCIe while preceding backbone layers compute (acting as a latency buffer). The figure likely also conveys layer-placement tradeoffs and the multi-level cache hierarchy (HBM → Host DRAM → NVMe SSD) motivated by the Zipfian distribution of N-gram access patterns.

If you can share the page containing Figure 2 itself, I can describe its specific architecture/components/data flow and transcribe the caption verbatim.

### Figure 5 (p.16) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-fig05.png]]
*整页渲染: ![[assets/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-p16.png]]*
> [!quote] caption
> We find that three components yield the most significant gains: (i) branch- specific fusion within the multi-branch backbone, (ii) context-aware gating, and (iii) tokenizer compression. Removing any of these causes the largest regressions in validation loss. Specifically, for the “w/o multi branch” ablation, we retain the mHC backbone structure but replace the branch-specific gating with a single 

> [!tip] 技术解读（多模态）
> No figure is visible on this page (p. 16). The page consists entirely of prose that *references* a figure (Figure 5) but does not display it. Below I describe what the text tells us about that figure, and note that no caption is present to transcribe.

**Figure 5 (described from text only):**
- **Components / data flow:** Validation Loss curves and markers from structural ablations of an Engram-augmented backbone. A horizontal **dashed orange line** marks the 3B MoE baseline (Val Loss = 1.808). A **dark blue "Layer Sweep" curve** plots Val Loss vs. insertion layer (1→12) for a consolidated 1.6B Engram module. Additional **marker points** encode single-component ablations relative to a reference configuration (Engram @ Layers 2 & 6, {2,3}-grams, 1.6B params).
- **Key technical takeaway:** There is a depth trade-off in Engram injection — early placement offloads local pattern reconstruction but suffers weak gating (insufficient contextualization); later placement gains context but loses offloading benefit. **Layer 2 is optimal under a single-injection budget (1.770)**, and splitting the same 1.6B budget across **Layers 2 + 6 is best overall (1.768)**, reconciling early offloading with late contextual gating.

**Caption transcription:** No caption is rendered on this page — only inline prose referring to it ("dark blue 'Layer Sweep' curve in Figure 5"; "markers in Figure 5").

### Figure 7 (p.18) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-fig07.png]]
*整页渲染: ![[assets/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-p18.png]]*
> [!quote] caption
> The results demonstrate a distinct pattern of selectivity. The gating mechanism consistently activates (shown in red) upon completing local, static patterns. In English, we observe strong activations on multi-token named entities (e.g., “Alexander the Great”, “the Milky Way”) and formulaic phrases (e.g., “By the way”, “Princess of Wales”). This behavior generalizes effectively across languages. In

> [!tip] 技术解读（多模态）
> I need to flag an issue with your request: **there is no main figure (architecture diagram, components, or data-flow visualization) on this page.** The visible content consists of:

1. **Table 4** — a numerical data table (not an architecture figure)
2. **Running prose text** — including a section heading "6.5. Case Study: Gating Visualization"
3. **Footnote 2**
4. A reference to **"Figure 7"** in the text, but Figure 7 itself is not rendered on this page

The page primarily presents Table 4's throughput data and discusses gating-visualization results that *would* appear in Figure 7, but that figure is not included here.

---

**Caption verbatim (Table 4):**

> **Table 4 | End-to-end Inference Throughput.** We measure inference throughput with a 100B-parameter Engram layer entirely offloaded to host memory.

---

If you intended to ask about Table 4 instead of a figure, here is a brief summary within your word budget:

**Table 4 (≤120 words):** The table compares inference throughput (tokens/s) across two backbone sizes (4B-Dense and 8B-Dense) under Baseline vs. +100B Engram (CPU Offload) configurations on NVIDIA H800, with 512 sequences and Uniform(100, 1024) sequence length. 4B-Dense drops from 9,031.62 → 8,858.28 tok/s, and 8B-Dense from 6,315.52 → 6,140.02 tok/s. **Key takeaway:** Offloading a 100B-parameter embedding table incurs at most a ~2.8% throughput penalty on the 8B backbone, demonstrating that early dense blocks' compute intensity masks retrieval latency and that effective communication scales with *activated slots*, not total embedding size — a conservative baseline since all retrievals go over PCIe without HBM caching.

Please share Figure 7 (or the intended figure) and I'll describe its architecture/components/data flow as requested.

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