---
paper_num: "50"
title: "A Survey on Large Language Model Acceleration based on KV Cache Management"
authors: "A Survey on Large Language Model Acceleration based on KV Cache Management Haoyang Li, Yiming Li, Anxin Tian, Tianhao Tang, Zhanchao Xu, Xuejia Chen, Nicole Hu, Wei Dong, Qing Li Fellow, IEEE, Lei Chen Fellow, ACM/IEEE,"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2412.19442"
pdf: "papers/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management.pdf"
slug: "a-survey-on-large-language-model-acceleration-based-on-kv-cache-management"
tags: [kv-cache]
---

# A Survey on Large Language Model Acceleration based on KV Cache Management

> [!abstract] 摘要（原文）
> 1\. 🤖 大语言模型（LLMs）在推理过程中面临巨大的计算和内存需求，尤其是处理长上下文时，KV cache管理已成为解决此瓶颈的关键优化技术。 2. ⚙️ 该综述系统地将KV cache管理策略划分为token-level、model-level和system-level优化，涵盖了从数据压缩到架构创新再到系统资源调度的广泛技术。 3. 🚀 该研究不仅提供了详细的分类和比较分析，还指出未来研究方向应侧重于跨类别集成、实际部署案例、领域特定优化及隐私安全等挑战。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: A Survey on Large Language Model Acceleration based on KV Cache Management Haoyang Li, Yiming Li, Anxin Tian, Tianhao Tang, Zhanchao Xu, Xuejia Chen, Nicole Hu, Wei Dong, Qing Li Fellow, IEEE, Lei Chen Fellow, ACM/IEEE,
- **arXiv**: https://arxiv.org/abs/2412.19442
- **本地 PDF**: `papers/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management.pdf`
- **页数**: 40

## 图表（原文 caption + 页码）
_未检测到带 caption 的 figure_

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.2) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab01.png]]
> [!quote] caption
> Notation Summary

> [!tip] 表格解读（多模态）
> # Description

The image does not contain a **figure** — it displays **Table 1 ("Notation Summary")**, a two-column reference table pairing mathematical symbols with their definitions for a paper on **Key-Value (KV) cache management in transformer-based LLMs**. 

**Architecture/components covered:**
- **Inputs:** tokens X, dense embeddings X, positional encoding ℙ(X), embedding matrix E ∈ ℝ^(d_vocab × d_x)
- **Attention mechanism:** Query/Key/Value matrices (Q_i, K_i, V_i), weight matrices W_Qi, W_Ki, W_Vi, output weight W_O, head dimensions d_k, d_v
- **Self-attention output:** Z_i
- **Feed-forward layer:** weights W₁, W₂ and biases b₁, b_2
- **KV-cache specifics:** sequence index t, cache size t_c, current K^t, V^t, and cached K^(t-1), V^(t-1)
- **Model scale:** h heads per layer, L transformer layers
- **Output:** conditional probability P(x_{t+1} | x_1; …; x_t)

**Key technical takeaway:** The notation makes explicit that KV caching stores past **keys/values across layers and heads** (K̂^(t-1), V̂^(t-1)), enabling autoregressive decoding to reuse previously computed attention states rather than recomputing them at every step — the central efficiency lever the survey explores.

# Caption (verbatim)

**TABLE 1**
**Notation Summary**

### Table 4 (p.11) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab04.png]]
> [!quote] caption
> The summary of existing KV Cache merging approaches.

> [!tip] 表格解读（多模态）
> **Description (≤120 words)**

The image displays **Table 4**, which is intended as a summary of existing KV Cache merging approaches in LLM inference optimization. The visible table structure shows a column-based layout comparing multiple methods (categorized by what appear to be broad grouping columns followed by individual method columns), with hierarchical row headers on the left side likely categorizing approaches by a key axis (e.g., whether merging was the focus, training-free vs. needs training, with/without parameter updates, or retention criterion such as attention scores). However, the table body is heavily garbled/corrupted in the image, so per-method details (technique name, compression ratio, performance, etc.) are not legible. **Key takeaway:** Existing KV Cache merging methods can be systematically classified along multiple axes, but the current visible rendering prevents extracting specific numerical or methodological comparisons.

**Caption transcribed verbatim:**

> TABLE 4
> The summary of existing KV Cache merging approaches.

### Table 5 (p.13) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab05.png]]
> [!quote] caption
> The summary of existing mixed-precision quantization models.

> [!tip] 表格解读（多模态）
> # Main Figure Description

**Architecture/Components/Data Flow:** The image contains only the header portion of **Table 5**, consisting of a title bar, a descriptive caption line, and the topmost row of column headers. No body content, data rows, architecture diagram, or data flow is visible — the table appears truncated, with the column headers rendered as garbled/illegible glyphs (showing symbols resembling "N", "B", "M", "N", "B", etc.). Consequently, the figure cannot convey any structural or quantitative information beyond its labeled purpose: a summary/comparison of existing mixed-precision quantization models.

**Key Technical Takeaway:** Because only the table heading is legible, no method, bit-width allocation strategy, or quantization framework can be identified from the figure itself. Any takeaway must come from the caption's stated intent — that the table is intended to benchmark or contrast prior mixed-precision quantization approaches — rather than from rendered content. (~95 words)

---

## Caption (Verbatim Transcription)

> **TABLE 5**
> The summary of existing mixed-precision quantization models.

### Table 6 (p.14) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab06.png]]
> [!quote] caption
> The summary of outlier redistribution models in Sec. 4.4.3.

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**
The figure shows a fragment of Table 6 listing outlier redistribution attention formulations. The visible row presents the standard softmax attention block: query (Q) and key (K) matrices interact via scaled dot-product (Q K^T / √d), while a separate outlier/key component k⁰ is paired with V and v^T (likely the outlier-aware value projection). The data flow is Q,K → scaled dot-product → softmax → weighted combination with V, with k⁰/v^T handling redistributed outlier tokens. The table summarizes how different papers treat these outlier tokens in attention.

**Key takeaway:** Outlier redistribution models adapt the attention block by introducing dedicated k⁰/v^T pathways to handle outlier tokens separately from the standard softmax(QK^T/√d)·V pipeline.

**Caption (verbatim):**
"TABLE 6 — The summary of outlier redistribution models in Sec. 4.4.3."

### Table 7 (p.18) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab07.png]]
> [!quote] caption
> The summary of Model-based Attention Grouping and Sharing approaches.

> [!tip] 表格解读（多模态）
> **Main Figure Description:**

The visible portion shows the header section of a comparison table titled "TABLE 7" with the caption "The summary of Model-based Attention Grouping and Sharing approaches." Below the caption, the table appears to have multiple columns, each featuring a small stylized "M"-like icon in the header row (likely a model/network symbol). The columns are subdivided into rows containing additional smaller icons (resembling module or attention-head markers). The bottom portion of the table is cropped, so the underlying comparative content (method names, parameters, accuracy metrics) is not legible.

**Key Technical Takeaway (≤120 words):**
The figure is a summary table cataloging various Model-based Attention Grouping and Sharing methods, organized in a multi-column grid layout. Each column represents a distinct approach, while sub-rows group or share attention components (heads/layers) across the model. The repeating "M" icons visually emphasize the model-centric framing of these techniques. Although most numerical/textual data is cropped, the structural takeaway is that these methods differ primarily in *how* attention units are grouped (e.g., by layer, task, or shared parameters) versus independently allocated. This taxonomy aids readers in selecting grouping/sharing strategies based on desired trade-offs between parameter efficiency, representational capacity, and cross-task generalization in multi-task or multi-head transformer architectures.

**Caption Transcribed Verbatim:**
"TABLE 7
The summary of Model-based Attention Grouping and Sharing approaches."

### Table 8 (p.19) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab08.png]]
> [!quote] caption
> The summary of Model-based Intra-layer approaches.

> [!tip] 表格解读（多模态）
> **Description:**

The image shows only the header portion of a table (Table 8), so the full architecture/data flow cannot be assessed. Visible components include:

- **Title block:** "TABLE 8 / The summary of Model-based Intra-layer approaches."
- **Column header row:** A "Method" label on the left, followed by several column headers whose text appears corrupted or rendered as garbled glyphs (showing scattered black shapes such as "¶," "¶," "¶," "♦," "K," "K"), making the column names illegible.

**Key technical takeaway (inferred):** Because the visible content is limited to the header and column labels are unreadable, no substantive technical claim can be drawn from this figure alone — the rendering artifacts obscure the comparative metrics that the table is meant to summarize for model-based intra-layer methods.

**Caption (transcribed verbatim):**

> TABLE 8
> The summary of Model-based Intra-layer approaches.

### Table 9 (p.20) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab09.png]]
> [!quote] caption
> The summary of Non-Transformer Architectures.

> [!tip] 表格解读（多模态）
> **Description of the Figure:**

The figure is labeled **TABLE 9** and titled "The summary of Non-Transformer Architectures." Below the title is a horizontal divider line, beneath which the table body appears as garbled, illegible glyphs (likely a rendering/font issue where text or symbols failed to display properly). No discernible architecture diagram, component labels, or data flow arrows are readable. As such, the intended structural elements—architectural components, layer types, or inter-module data flow—cannot be described from the visual content.

**Key Technical Takeaway (inferred from context):**

Non-Transformer architectures (e.g., RNN, CNN, state-space, and MLP-based models) are typically summarized in a comparative table highlighting their core building blocks, recurrence versus convolution versus token-mixing mechanisms, and information propagation pathways that differ from self-attention.

**Caption Transcribed Verbatim:**

> "TABLE 9
> The summary of Non-Transformer Architectures."

### Table 10 (p.23) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab10.png]]
> [!quote] caption
> Comparison of Memory Management Techniques for KV Cache

> [!tip] 表格解读（多模态）
> **Caption (verbatim):**
> TABLE 10
> Comparison of Memory Management Techniques for KV Cache Optimization

**Note on description:** The table's body content (rows, columns, technique names, metrics) is not visible in the provided image — only the table heading, caption, and page number ("23") are shown. Without the underlying data (likely comparing techniques such as PagedAttention, vLLM-style paging, offloading, quantization, or eviction strategies across memory, latency, and throughput dimensions), I cannot accurately describe specific architecture/components, data flow, or derive a grounded technical takeaway.

If you can share the table rows (or a clearer image including the body), I can immediately provide a ≤120-word synthesis covering the compared techniques, their core mechanism, and one key insight (e.g., "paged allocation reduces fragmentation vs. contiguous pre-allocation" or "offloading trades recompute latency for memory headroom").

### Table 11 (p.25) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab11.png]]
> [!quote] caption
> Comparison of Scheduling Approaches for KV Cache Optimization.

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**

Table 11 is a comparison matrix that cross-references 12 KV cache scheduling systems (rows) against a set of taxonomy criteria (columns; column headers appear garbled in the figure). Each "X" marks whether a given approach implements a specific scheduling feature. Architecturally, the table organizes systems by optimization strategy: batch-oriented schemes (BatchLLM, RadixAttention, Echo), multi-stage/switching schedulers (FastServe, FlowKV, FastSwitch), layer/attention-cached methods (LayerKV, CachedAttention), and hybrid/context-aware systems (ALISA, LAMPS, Apt-Serve, FGOS). The principal takeaway is that no single system covers all dimensions—each approach addresses a specific subset, and recent systems (LAMPS, Apt-Serve, FGOS) tend to combine hybrid caching with adaptive/multi-stage scheduling, reflecting a broader trend toward context-aware, multi-objective KV cache management.

**Caption verbatim:**

TABLE 11
Comparison of Scheduling Approaches for KV Cache Optimization.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf{Z}_i = \text{Attention}(\mathbf{Q}_i, \mathbf{K}_i, \mathbf{V}_i) = \text{Softmax}\left(\frac{\mathbf{Q}_i \mathbf{K}_i^\top}{\sqrt{d_k}}\right) \mathbf{V}_i,
$$

$$
P(x_{t+1} | x_1, x_2, \cdots, x_t) = \text{Softmax}(\mathbf{h}_t \mathbf{W}_{\text{out}} + \mathbf{b}_{\text{out}}),
$$

$$
x_{t+1} \sim P(x_{t+1} | x_1, x_2, \cdots, x_t).
$$

$$
\text{TD}(\mathbf{W}) = \prod_{k=1}^n \mathcal{T}_{(k)}[d_{k-1}, i_k, j_k, d_k],
$$

$$
\mathbf{Q}_i = \mathbf{X}\mathbf{W}_{Q_i}, \quad \mathbf{K}_i = \mathbf{X}\mathbf{W}_{K_i}, \quad \mathbf{V}_i = \mathbf{X}\mathbf{W}_{V_i},
$$

$$
\mathbf{Z}=\text{Concat}(\mathbf{Z}_1, \mathbf{Z}_2, \dots, \mathbf{Z}_h)\mathbf{W}_O,
$$

$$
\text{FFN}(\mathbf{Z}) = \sigma(\mathbf{Z}\mathbf{W}_1 + \mathbf{b}_1)\mathbf{W}_2 + \mathbf{b}_2
$$

$$
\mathbf{q}_i^t &= \mathbf{x}_t \mathbf{W}_{Q_i}, \quad \mathbf{k}_i^t = \mathbf{x}_t \mathbf{W}_{K_i}, \quad \mathbf{v}_i^t = \mathbf{x}_t \mathbf{W}_{V_i},
$$

$$
\mathbf{K}_i^{t} &= \text{Concat}(\mathbf{\hat{K}}_i^{t-1}, \mathbf{k}_i^t ), \ \mathbf{V}_i^{t} = \text{Concat}(\mathbf{\hat{V}}^{t-1}_i, \mathbf{V}_i^t ),
$$

$$
\mathbf{z}^t_i = \text{Softmax}\left(\frac{\mathbf{q}_i^t {\mathbf{K}_i^t}^\top}{\sqrt{d_k}}\right) \mathbf{V}_i^t,
$$

$$
O\left(L\cdot h \cdot t_c \cdot t \cdot (d_k+d_v)+ L\cdot h \cdot t_c\left(\triangle_1 + \triangle_2\right)\right)
$$

$$
O(L\cdot h \cdot t_c \cdot (d_k+d_v) \cdot sizeof(Float16))
$$

## 相关论文

- [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] — CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion
- [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] — KV Cache Optimization Strategies for Scalable and Efficient LLM Inference
- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] — Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter
- [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] — IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse

## 技术点深读（DEEP）

![[deep/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management.txt`（233789 字符）供引用检索。