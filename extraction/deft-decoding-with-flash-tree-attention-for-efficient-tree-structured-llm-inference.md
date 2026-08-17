---
paper_num: "53"
title: "DeFT: Decoding with Flash Tree-attention for Efficient Tree-structured LLM Inference"
authors: ""
date: "2024/4/1"
arxiv: "https://arxiv.org/abs/2404.00242"
pdf: "papers/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference.pdf"
slug: "deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference"
tags: []
---

# DeFT: Decoding with Flash Tree-attention for Efficient Tree-structured LLM Inference

> [!abstract] 摘要（原文）
> 1. Large language models (LLMs) are increasingly employed for complex tasks that process multiple generation calls in a tree structure with shared prefixes of tokens, including few-shot prompting, multi-step reasoning, speculative decoding, etc. However, existing inference systems for tree-based applications are inefficient due to improper partitioning of queries and KV cache duri

## 元信息
- **发表日期**: 2024/4/1
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2404.00242
- **本地 PDF**: `papers/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference.pdf`
- **页数**: 32

## 图表（原文 caption + 页码）

### Figure 1 (p.1)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p01.png]]
> [!quote] caption
> Usually, these applications produce substantially more tokens than traditional ones, to provide large space for tree search (Graves, 2012; Lu et al., 2022; Liu et al., 2023) or selection, as shown in Table 1.

### Figure 2 (p.5) ⭐深度解读
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p05.png]]
> [!quote] caption
> Overview of DEFT. Input Metadata is prepared in the system elaborated in Appendix A.1. In QKV

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】DeFT flash 树注意力(Fig.2)：① Input Metadata（Q + 共享前缀 K0 + 分支 K1/K2 + 树拓扑）载入 SM；② Phase1 QKV 准备(HBM 2TB/s)：KV-Guided Grouping 跨分支复用 K0、Flattened Tree KV Splitting 把树切成均衡组 G0/G1/G2 并行；③ Phase2 注意力计算(Shared Mem 19TB/s)：DeFT kernel 各 split 跑部分注意力 + 树拓扑感知全局归约(A0/A1/A2→Final)，避免跨全分支全局同步。消除共享前缀冗余 KV IO、平衡 SM 负载→内存高效、硬件友好的树结构投机解码注意力。架构核心图。

### Figure 3 (p.6)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p06.png]]
> [!quote] caption
> Comparison of QKV partitioning strategies during the QKV Preparation Phase between DEFT-

### Figure 4 (p.9)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p09.png]]
> [!quote] caption
> Latency breakdown for specula- tive decoding with a token tree of 32 queries, whose tree topology is from Medusa (Cai et al., 2024). U means unpaged memory.

### Figure 5 (p.15)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p15.png]]
> [!quote] caption
> Illustration of DEFT. (Left) System overview. (Right) The data flow of DEFT-Node (DEFT-Flatten is similar except for QKV partitioning) using a decoding tree example.

### Figure 6 (p.16)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p16.png]]
> [!quote] caption
> Discussion of tree-based decoding with tree queries (Miao et al., 2023) and tree KV.

### Figure 7 (p.17)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p17.png]]
> [!quote] caption
> Analysis for two case studies of tree-based decoding. (Left) Multi-step reasoning. (Right) Speculative decoding. Blue boxes mean shareable past KV cache in storage and memory access during the tree attention calculation, while yellow boxes mean the KV cache of generated context. which states to pursue further and the sequence in which to explore them; (3) Tree Search-based

### Figure 8 (p.19)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p19.png]]
> [!quote] caption
> Operations of Tree Attention-Medusa (Cai et al., 2024). No Kernel Fusion or Tiling strategy is applied, which introduces significant IO of partial results like QK⊤, DCM, and Softmax between GPU global memory and on-chip shared memory.

### Figure 9 (p.19)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p19.png]]
> [!quote] caption
> Overview of two stages in DEFT Attention Kernel (DEFT-Node for example, and DEFT-Flatten is similar). Stage 1–calculate partial attentions. Based on the QKV grouping results after KV-Guided Grouping

### Figure 10 (p.20)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p20.png]]
> [!quote] caption
> Detailed attention operations of DEFT kernel (DEFT-Node for example, and DEFT-Flatten is similar). Based on the same decoding tree in Figure 3.

### Figure 11 (p.21)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p21.png]]
> [!quote] caption
> When the number of leaf nodes/queries ln is sufficiently large, the IO cost of partial results might become comparable to that of the KV cache. For instance, in the Llama models (Touvron et al., 2023a;b), where dhead =128, with ln =29, the total IO cost of QKT , M, QK⊤ sc , M + QK⊤ sc , and

### Figure 12 (p.23)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p23.png]]
> [!quote] caption
> The detailed procedure of reconstructing tree templates for multi-step reasoning. (Left)

### Figure 13 (p.25)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p25.png]]
> [!quote] caption
> Comparison of split strategies DEFT-Node and DEFT-Flatten in sorting task. Speedup ratio refers to the ratio between the per iteration latency of DEFT-Node and DEFT-Flatten. Tree Node Len std represents the standard deviation of the tree node lengths for each iteration.

### Figure 14 (p.26)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p26.png]]
> [!quote] caption
> Per iteration latency for few-shot prompting tasks with different tree width. e2e means decoding latency(optimal end-to-end latency), while Attn means only the attention overhead.

### Figure 15 (p.26)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p26.png]]
> [!quote] caption
> The chunk size selection is a trade-off between IO redundancy and threadblock scheduling: a larger chunk size means less redundancy of Query IO but may cause potential idle SMs of GPUs due to fewer threadblocks during GPU scheduling.

### Figure 16 (p.27)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p27.png]]
> [!quote] caption
> Time per output token(TPOT) of DEFT with different prompt lengths in speculative decoding. 2500 5000 7500 10000 12500 15000 17500 20000

### Figure 17 (p.27)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p27.png]]
> [!quote] caption
> Decoding latency of DEFT with different prompt lengths in speculative decoding.

### Figure 18 (p.28)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p28.png]]
> [!quote] caption
> Attention latency of DEFT with different prompt lengths in speculative decoding.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\begin{aligned} \textstyle \operatorname{SegAttn}(\mA_0, \mA_1, \mA_2)= \frac{ \mA_0 e^{\operatorname{LSE}(\mQ, \mK_0)} + \mA_1 e^{\operatorname{LSE}(\mQ, \mK_1)} + \mA_2 e^{\operatorname{LSE}(\mQ, \mK_2)} }{ e^{\operatorname{LSE}(\mQ, \mK_0)} + e^{\operatorname{LSE}(\mQ, \mK_1)} + e^{\operatorname{LSE}(\mQ, \mK_2)} } \,, \text{ where } e := \text{exp} \,. \end{aligned}
$$

## 全文文本
全文已存 `extraction/fulltext/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference.txt`（112630 字符）供引用检索。