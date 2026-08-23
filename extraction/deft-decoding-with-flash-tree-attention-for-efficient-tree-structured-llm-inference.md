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

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig01.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p01.png]]*
> [!quote] caption
> Usually, these applications produce substantially more tokens than traditional ones, to provide large space for tree search (Graves, 2012; Lu et al., 2022; Liu et al., 2023) or selection, as shown in Table 1.

> [!tip] 技术解读（多模态）
> No figure is visible on this page — it is the title page of the paper "DEFT: Decoding with Flash Tree-Attention for Efficient Tree-structured LLM Inference," containing only the title, author affiliations, abstract, and the opening of the Introduction. The text references "Figure 1" (illustrating tree-structured LLM applications such as self-consistency, few-shot prompting, multi-step reasoning, and speculative decoding) and "Table 1" (showing token volume differences), but neither the figure nor its caption appears in the provided image, so I cannot describe the figure's architecture/components/data flow or transcribe its caption verbatim.

### Figure 2 (p.5) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig02.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p05.png]]*
> [!quote] caption
> Overview of DEFT. Input Metadata is prepared in the system elaborated in Appendix A.1. In QKV

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】DeFT flash 树注意力(Fig.2)：① Input Metadata（Q + 共享前缀 K0 + 分支 K1/K2 + 树拓扑）载入 SM；② Phase1 QKV 准备(HBM 2TB/s)：KV-Guided Grouping 跨分支复用 K0、Flattened Tree KV Splitting 把树切成均衡组 G0/G1/G2 并行；③ Phase2 注意力计算(Shared Mem 19TB/s)：DeFT kernel 各 split 跑部分注意力 + 树拓扑感知全局归约(A0/A1/A2→Final)，避免跨全分支全局同步。消除共享前缀冗余 KV IO、平衡 SM 负载→内存高效、硬件友好的树结构投机解码注意力。架构核心图。

### Figure 3 (p.6) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig03.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p06.png]]*
> [!quote] caption
> Comparison of QKV partitioning strategies during the QKV Preparation Phase between DEFT-

> [!tip] 技术解读（多模态）
> ## Main Figure Description (≤120 words)

The figure compares QKV partitioning strategies for tree-structured KV cache attention in three panels:

**(a)** Dataflow: Decoding Tree Metadata → Phase 1 (QKV Preparation) → Phase 2 (Attention Calculation, loading groups $G_i$ onto SM$_i$). Contrasts Vanilla Tree Attention (low parallelism, dense causal mask) with Q-Guided vs. KV-Guided grouping.

**(b)** Q-Guided grouping (Flash-Attention, Flash-Decoding/Radix) loads the prefix KV$_0$ redundantly for each query group, while KV-Guided grouping (DeFT-Node, DeFT-Node-Chunk) is IO-aware—KV$_0$ is loaded only once and shared.

**(c)** DeFT-Flatten performs load-balanced partitioning via depth-first flattening, blockwise splitting, and bitmask extraction (KV-BCM) for even workload distribution.

**Key takeaway:** KV-Guided grouping eliminates redundant prefix KV loads by binding each KV node to all queries sharing it, making the partitioning prefix-aware and IO-efficient compared to query-driven baselines.

## Caption (verbatim)

**Figure 3: Comparison of QKV partitioning strategies during the QKV Preparation Phase between DeFT-Node/Node-Chunk/Flatten and different attention algorithm baselines.** Note that the partitioning is logically designed without incurring any data movement costs for QKV. The amount of IO between the GPU HBM and shared memory required by each group is highlighted in red rectangles. Part (a) illustrates the dataflow of a two-cascaded decoding tree example and three categories of QKV partitioning strategies: no partition(Vanilla Tree Attention), Q-Guided Grouping and KV-Guided Grouping. The partitioning strategy will guide the loading of QKV during the subsequent *Attention calculation phase*, where each QKV group $G_i$ will be loaded into $SM_i$ on the GPU. Part (b) shows the comparison of Q-Guided Grouping and KV-Guided Grouping, where the latter can be IO-aware of prefix KV cache $KV_0$ and only load it once. DeFT-Node-Chunk is a weak load-balancing improvement of DeFT-Node by splitting large nodes (e.g., $KV_0$) to chunks. Part (c) illustrates the details (discussed in Remark 3.1) of Flattened Tree KV Splitting in DeFT-Flatten for load-balanced partitions, including Depth-first Flatten strategy, Evenly block-wise strategy, and Bit mask. For a summary of baselines and DeFT, see Table 2. See analysis of tree-attention baselines (Cai et al., 2024; Miao et al., 2023) in Remark 3.2.

### Figure 4 (p.9) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig04.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p09.png]]*
> [!quote] caption
> Latency breakdown for specula- tive decoding with a token tree of 32 queries, whose tree topology is from Medusa (Cai et al., 2024). U means unpaged memory.

> [!tip] 技术解读（多模态）
> **Figure 4 — Architecture & Data Flow**

A stacked bar chart comparing decoding latency (seconds) across six attention methods for speculative decoding with a 32-query Medusa token tree. Each bar is partitioned into three components: **Attention** (orange, bottom), **KV Management** (blue, middle), and **Other** (green, top). Methods include Radix Attention, DeFT-Flatten, DeFT-Node, DeFT-Node-Chunk, and two unpaged variants (U). Total latency rises from ~50s (Radix Attention) to >275s (unpaged Tree Attention-Medusa).

**Key technical takeaway:** With **unpaged KV caching**, KV management dominates (69.1–83.4% of latency) due to costly tensor materialization, but **paged memory flips the bottleneck to attention** (51.1–58.3%)—eliminating data-movement overhead and exposing attention as the next optimization target.

**Caption (verbatim):**
Figure 4: Latency breakdown for speculative decoding with a token tree of 32 queries, whose tree topology is from Medusa (Cai et al., 2024). U means unpaged memory.

### Figure 5 (p.15) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig05.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p15.png]]*
> [!quote] caption
> Illustration of DEFT. (Left) System overview. (Right) The data flow of DEFT-Node (DEFT-Flatten is similar except for QKV partitioning) using a decoding tree example.

> [!tip] 技术解读（多模态）
> **Architecture/Components/Data Flow:**

The figure shows DeFT's system design in two panels. **Left (System Overview):** Four modules coordinate tree-based decoding — (1) *Branch Controller* uses a user-defined function to drive branching from a prompt; (2) *Sequence Tree Manager* (with Tree Handler + Branch Result Storage) maintains tree topology, executes fork/remove operations, and decides when to stop; (3) *KV Cache Manager* handles per-branch KV cache and fork/remove operations; (4) *Model Interface* runs the DeFT Attention Kernel + MLP over #layers, returning logits and memory pointers. Updated KV flows back to the cache manager, while logits loop to the controller.

**Right (Data Flow — DeFT-Node):** From the decoding tree (S0 prompt → S1 "System is difficult", S2 "has changed the") plus current query tokens, QKV groups are built per-branch KV chunk, prepared from HBM to shared memory, and fed into the DeFT Attention Kernel for grouped attention.

**Key Takeaway:** DeFT co-designs attention kernels with tree-structured KV cache management — grouping QKV by branch enables shared-memory-resident attention without re-tokenizing or padding speculative branches.

**Caption (verbatim):**

Figure 5: **Illustration of DeFT**. (Left) System overview. (Right) The data flow of DeFT-Node (DeFT-Flatten is similar except for QKV partitioning) using a decoding tree example.

### Figure 6 (p.16) ⭐深度解读
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p16.png]]
> [!quote] caption
> Discussion of tree-based decoding with tree queries (Miao et al., 2023) and tree KV.

> [!tip] 技术解读（多模态）
> **Figure 6 Description (architecture/components/data flow + key takeaway)**

The figure illustrates tree-based decoding in two parts. **(a)** shows two query topologies paired with their KV caches: a *Sequence KV* (s₀) feeding a flat **Query Token Tree** of up to 64 tokens (t₁→t₂, t₃, t₄, t₅), versus a *Tree KV* (s₀ branching into s₁, s₂) paired with parallel queries (t₁, t₂), enabling shared-prefix reuse. **(b)** shows the **Bit Mask** mechanism: each query token tᵢ carries a 64-bit mask M[tᵢ] encoding causal connectivity (pᵢ bits: 1=no mask, 0=masked) between the token tree and tᵢ.

**Key takeaway:** Causal correctness in parallel tree decoding is preserved by a per-token 64-bit bit mask, which is far more storage-efficient than materializing full causal masks while still supporting speculative/multi-step reasoning workloads.

**Caption (verbatim):**
Figure 6: Discussion of tree-based decoding with tree queries (Miao et al., 2023) and tree KV.

### Figure 7 (p.17) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig07.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p17.png]]*
> [!quote] caption
> Analysis for two case studies of tree-based decoding. (Left) Multi-step reasoning. (Right) Speculative decoding. Blue boxes mean shareable past KV cache in storage and memory access during the tree attention calculation, while yellow boxes mean the KV cache of generated context. which states to pursue further and the sequence in which to explore them; (3) Tree Search-based

> [!tip] 技术解读（多模态）
> ## Figure 7 Description

**Architecture / Components / Data Flow:**
Figure 7 contrasts two tree-based decoding scenarios that share KV-cache I/O patterns. **Left — Multi-step reasoning** proceeds in three stages: (1) thought generation via TreeAttention(P_g, S), (2) thought evaluation via TreeAttention(P_e, S), and (3) tree-search-based expansion, where prompt P branches into thoughts G₁ and G₂, each producing children (G₁.₁, G₁.₂, G₂.₁, G₂.₂). **Right — Speculative decoding** first uses draft models/heads to build a token tree T_t (t₀ → t₁, t₂, t₃ → t₄), then verifies tokens against the LLM, retaining verified tokens V_t = {t₀, t₂, t₄} and reusing their KV cache before stepping into Step 3. Blue boxes mark **shareable past KV cache**; yellow boxes mark **generated KV cache**.

**Key takeaway:** TreeAttention amortizes I/O by sharing KV cache across the prompt P, common prefix S, and any verified/cached tree nodes across all decoding stages.

## Caption (Verbatim)

> Figure 7: Analysis for two case studies of tree-based decoding. (Left) Multi-step reasoning. (Right) Speculative decoding. Blue boxes mean shareable past KV cache in storage and memory access during the tree attention calculation, while yellow boxes mean the KV cache of generated context.

### Figure 8 (p.19) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig08.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p19.png]]*
> [!quote] caption
> Operations of Tree Attention-Medusa (Cai et al., 2024). No Kernel Fusion or Tiling strategy is applied, which introduces significant IO of partial results like QK⊤, DCM, and Softmax between GPU global memory and on-chip shared memory.

> [!tip] 技术解读（多模态）
> # Main Figure Description

## Architecture & Data Flow (Figure 8)

**Components:**
- **Kernel:** `TreeAttnMedusa(Q,K,V,DCM)` — loads groups `G_T` (G₀…Gₘ) into streaming multiprocessors (`SM_i`)
- **Tree Topo:** KV pairs (KV₀, KV₁, KV₂) are tiled per query (Q₁, Q₂)
- **Masked block (DCM):** Dense causal mask matrix; `Sc` = scale factor
- **Two memory regions:** Global Memory (HBM) ↔ Compute in SMs (shared memory)

**Data flow (sequential, no fusion):**
1. Load Q,K in QKV groups → compute **S = Q@K⊤** → write S
2. Load Sc, S → compute **S′ = S/Sc** → write S′
3. Load S, DCM → compute **Ms = S+DCM** → write Ms
4. Load Ms → compute **P = Softmax(Ms)** → write P
5. Load P,V → compute **O = P@V** → write O

## Key Technical Takeaway (≤120 words)

The figure illustrates an **unfused, un-tiled attention kernel** where every intermediate tensor (QK⊤, DCM, Softmax, P) is round-tripped between HBM and on-chip shared memory. This causes heavy IO traffic proportional to the attention matrix size, wasting bandwidth and leaving shared memory underutilized. The author's contrast this with Flash-Attention-style **Kernel Fusion + Tiling**, where intermediates stay in registers/shared memory and softmax is computed incrementally—drastically reducing IO. This motivates DeFT's two-stage design (Figure 9), which fuses per-group and applies a tree-topology-aware global reduction instead of materializing partial results globally.

## Caption (Verbatim)

**Figure 8:** Operations of Tree Attention-Medusa (Cai et al., 2024). No *Kernel Fusion* or *Tiling* strategy is applied, which introduces significant IO of partial results like QK⊤, DCM, and Softmax between GPU global memory and on-chip shared memory.

### Figure 9 (p.19) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig09.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p19.png]]*
> [!quote] caption
> Overview of two stages in DEFT Attention Kernel (DEFT-Node for example, and DEFT-Flatten is similar). Stage 1–calculate partial attentions. Based on the QKV grouping results after KV-Guided Grouping

> [!tip] 技术解读（多模态）
> # Main Figure Description

## Architecture & Data Flow (Figure 8)

**Components:**
- **Kernel:** `TreeAttnMedusa(Q,K,V,DCM)` — loads groups `G_T` (G₀…Gₘ) into streaming multiprocessors (`SM_i`)
- **Tree Topo:** KV pairs (KV₀, KV₁, KV₂) are tiled per query (Q₁, Q₂)
- **Masked block (DCM):** Dense causal mask matrix; `Sc` = scale factor
- **Two memory regions:** Global Memory (HBM) ↔ Compute in SMs (shared memory)

**Data flow (sequential, no fusion):**
1. Load Q,K in QKV groups → compute **S = Q@K⊤** → write S
2. Load Sc, S → compute **S′ = S/Sc** → write S′
3. Load S, DCM → compute **Ms = S+DCM** → write Ms
4. Load Ms → compute **P = Softmax(Ms)** → write P
5. Load P,V → compute **O = P@V** → write O

## Key Technical Takeaway (≤120 words)

The figure illustrates an **unfused, un-tiled attention kernel** where every intermediate tensor (QK⊤, DCM, Softmax, P) is round-tripped between HBM and on-chip shared memory. This causes heavy IO traffic proportional to the attention matrix size, wasting bandwidth and leaving shared memory underutilized. The author's contrast this with Flash-Attention-style **Kernel Fusion + Tiling**, where intermediates stay in registers/shared memory and softmax is computed incrementally—drastically reducing IO. This motivates DeFT's two-stage design (Figure 9), which fuses per-group and applies a tree-topology-aware global reduction instead of materializing partial results globally.

## Caption (Verbatim)

**Figure 8:** Operations of Tree Attention-Medusa (Cai et al., 2024). No *Kernel Fusion* or *Tiling* strategy is applied, which introduces significant IO of partial results like QK⊤, DCM, and Softmax between GPU global memory and on-chip shared memory.

### Figure 10 (p.20) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig10.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p20.png]]*
> [!quote] caption
> Detailed attention operations of DEFT kernel (DEFT-Node for example, and DEFT-Flatten is similar). Based on the same decoding tree in Figure 3.

> [!tip] 技术解读（多模态）
> ## Description of Figure 10

**Architecture & Components:** Figure 10 illustrates the two-stage DeFT attention kernel via two subfigures. Subfigure (a) shows the kernel overview: a `DeFT_func(QKV_Groups)` host function (blue box) launches Stage 1 thread blocks that compute FlashAttention per QKV group (G₀, G₁, G₂), writing LSE and partial attention results to Global Memory (HBM, green). Stage 2 launches a Thread Block 3 calling `DeFT_Global_Reduction`, which invokes a global reduction kernel (red box) reading LSE and partial attention values, performing the numerically stable LogSumExp-based merge in SMs with shared memory, and writing the final attention back. Subfigure (b) zooms into Stage 2: partial outputs from Q₁/KV₀, Q₁/KV₁, Q₂/KV₀, Q₂/KV₂ are **remapped by query** (grouping LSE₀+LSE₁ for Q₁ and LSE₂+LSE₃ for Q₂), then passed to the global reduction kernel producing the final Q₁, Q₂ attention.

**Key Technical Takeaway (≤120 words):** DeFT exploits the tree-structured KV cache by exploiting query identity across multiple QKV groups. Stage 1 computes FlashAttention locally per group, producing (LSE, partial attention) pairs. Stage 2 remaps these by query—grouping all partial results sharing the same query—and runs a single GPU reduction kernel that merges them via the numerically stable max+exp+sum trick. This decomposition (1) amortizes KV reuse without redundant I/O, (2) keeps the working set local to FlashAttention, and (3) avoids full causal-materialization costs that plague Medusa/SpecInfer. **The global reduction is query-keyed, not QKV-group-keyed**, which is what makes the tree topology exploitable.

## Caption (Verbatim Transcription)

Figure 10: **Detailed attention operations of DeFT kernel** (**DeFT-Node** for example, and **DeFT-Flatten** is similar). Based on the same decoding tree in Figure 3.

To obtain the accurate final attention, partial attentions from QKV groups with identical queries need to be grouped for *Global Reduction*.

### Figure 11 (p.21) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig11.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p21.png]]*
> [!quote] caption
> When the number of leaf nodes/queries ln is sufficiently large, the IO cost of partial results might become comparable to that of the KV cache. For instance, in the Llama models (Touvron et al., 2023a;b), where dhead =128, with ln =29, the total IO cost of QKT , M, QK⊤ sc , M + QK⊤ sc , and

> [!tip] 技术解读（多模态）
> **Figure Description (Table 11: Notations)**

This table defines the mathematical notations used throughout the DEFT (Decoding with Flash Tree-attention) paper for analyzing tree-decoding IO complexity. It catalogs variables spanning tree topology (leaf nodes *l_n*, node count *#node*, per-node token length *n_i*, root-to-leaf path length *N_i*, and total tree length *N_tree*), attention kernel parameters (*d_head*, scale factor *s_c* = √*d_head*), and a derived metric *F_s* — the prefix-sharing factor — quantifying KV-cache reuse across branches.

**Key Technical Takeaway:** The shared-prefix factor *F_s* = (Σ N_i) / N_tree captures how tree-structured speculative decoding amortizes KV-cache IO across multiple query branches; tree-topology-aware schemes (DEFT) leverage *F_s* to reduce HBM accesses, whereas sequence-based methods incur *F_s* times the KV-cache IO overhead since they cannot exploit branch sharing.

**Caption (verbatim):**
Table 11: **Notations**.

### Figure 12 (p.23) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig12.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p23.png]]*
> [!quote] caption
> The detailed procedure of reconstructing tree templates for multi-step reasoning. (Left)

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

Figure 12 illustrates a two-stage pipeline for building decoding tree templates from real reasoning traces. **Left panel (green, "Reconstruct thought trees")**: A Prompt node expands breadthwise into w thoughts at each of d depths, forming a thought tree. Each node is labeled `thought_i_j`; checkmarks denote "best thought to keep," red minus signs mark "thoughts to prune," and dashed ellipses indicate depth/width omission. **Right panel (orange, "Tree templates for decoding")**: Each selected thought is encoded with five metadata fields — start/end iteration, thought size, parent id, and children id — which feed two structured tables: *Branch records* (which thoughts to generate at iteration i from parent (i-1,k)) and *Prune records* (which thoughts to discard at iteration j). These tables drive the tree decoder to replicate ToT structure faithfully.

**Key technical takeaway:** Tree-decoding guidance requires only two compact record types (branch + prune) derived from iteration-tagged thought metadata, enabling ToT reasoning to be replayed on standard tree-aware attention kernels without re-running LLM inference.

**Caption verbatim:**

Figure 12: **The detailed procedure of reconstructing tree templates for multi-step reasoning.** (Left) Reconstructing reasoning trees from practical reasoning records as outlined in (Besta et al., 2023) involves capturing the following aspects: (1) the structure of trees, characterized by their depth *d* and width *w*; (2) the token length associated with each thought; and (3) the best thought at each depth along with its corresponding score. For the task of document merging, the tree depth is set to *d* = 3, with a width of *w* = 10 at each depth. For sorting 128 numbers, the depth is reduced to *d* = 10, while maintaining the same width of *w* = 10. See details of tree topology for other multi-step reasoning tasks in Table 13. (Right) Utilizing the extracted thought information from Left, we can generate tree templates for decoding, encompassing *branch records* and *prune records*. These records are instrumental in guiding the tree decoding process to produce decoding trees that faithfully replicate the structure of the tree-of-thoughts.

### Figure 13 (p.25) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig13.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p25.png]]*
> [!quote] caption
> Comparison of split strategies DEFT-Node and DEFT-Flatten in sorting task. Speedup ratio refers to the ratio between the per iteration latency of DEFT-Node and DEFT-Flatten. Tree Node Len std represents the standard deviation of the tree node lengths for each iteration.

> [!tip] 技术解读（多模态）
> **Figure Description:**

The main figure (Figure 13) is a dual-axis time-series line plot titled "sorting" comparing two metrics across decoding steps (0–~3500):
- **Solid blue line (left axis):** *Speedup Ratio* (range 0.25–2.00) — the per-iteration latency ratio of DEFT-Node vs. DEFT-Flatten.
- **Dashed red line (right axis):** *Tree Node Len std* (range 150–400) — standard deviation of tree node lengths per iteration.

**Data flow/architecture:** Each decoding step produces a tree-structured query set; the plot correlates speedup gains against structural variability of that tree.

**Key takeaway:** Speedup ratio inversely tracks tree-node-length standard deviation — when node lengths become highly variable, speedup collapses sharply, suggesting DEFT-Flatten's flattening strategy excels only when tree structure is balanced.

**Caption verbatim:**
"Figure 13: Comparison of split strategies DEFT-Node and DEFT-Flatten in *sorting* task. *Speedup ratio* refers to the ratio between the per iteration latency of DEFT-Node and DEFT-Flatten. *Tree Node Len std* represents the standard deviation of the tree node lengths for each iteration."

### Figure 14 (p.26) ⭐深度解读
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p26.png]]
> [!quote] caption
> Per iteration latency for few-shot prompting tasks with different tree width. e2e means decoding latency(optimal end-to-end latency), while Attn means only the attention overhead.

> [!tip] 技术解读（多模态）
> **Architecture/Components/Data Flow:**
Figure 14 is a 2×2 grid of line plots showing per-iteration latency (Time, ms) over 400 decoding steps for few-shot prompting tasks. Each subplot varies the tree width (10, 20, 30, 50). Five curves are compared per subplot: DeFT-Flatten-e2e, Radix-e2e, DeFT-Flatten-Attn, Radix-Attn, and Medusa-Attn. The "e2e" curves measure end-to-end decoding latency, while "Attn" curves isolate attention overhead, allowing joint visualization of system-level vs. kernel-level performance as tree topology changes.

**Key Technical Takeaway:**
DeFT-Flatten's relative advantage over Radix Attention grows monotonically with tree width (1.24× at w=20, 1.33× at w=50) because wider trees increase KV-cache prefix reuse across parallel speculative-decoding branches, while attention overhead in competing schemes (e.g., Medusa) scales linearly with tree width via DCM growth.

**Caption (verbatim):**
"Figure 14: Per iteration latency for few-shot prompting tasks with different tree width. *e2e* means decoding latency(optimal end-to-end latency), while *Attn* means only the attention overhead."

### Figure 15 (p.26) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig15.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p26.png]]*
> [!quote] caption
> The chunk size selection is a trade-off between IO redundancy and threadblock scheduling: a larger chunk size means less redundancy of Query IO but may cause potential idle SMs of GPUs due to fewer threadblocks during GPU scheduling.

> [!tip] 技术解读（多模态）
> **Architecture/Components/Data Flow:**
Figure 14 is a 2×2 grid of line plots showing per-iteration latency (Time, ms) over 400 decoding steps for few-shot prompting tasks. Each subplot varies the tree width (10, 20, 30, 50). Five curves are compared per subplot: DeFT-Flatten-e2e, Radix-e2e, DeFT-Flatten-Attn, Radix-Attn, and Medusa-Attn. The "e2e" curves measure end-to-end decoding latency, while "Attn" curves isolate attention overhead, allowing joint visualization of system-level vs. kernel-level performance as tree topology changes.

**Key Technical Takeaway:**
DeFT-Flatten's relative advantage over Radix Attention grows monotonically with tree width (1.24× at w=20, 1.33× at w=50) because wider trees increase KV-cache prefix reuse across parallel speculative-decoding branches, while attention overhead in competing schemes (e.g., Medusa) scales linearly with tree width via DCM growth.

**Caption (verbatim):**
"Figure 14: Per iteration latency for few-shot prompting tasks with different tree width. *e2e* means decoding latency(optimal end-to-end latency), while *Attn* means only the attention overhead."

### Figure 16 (p.27) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig16.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p27.png]]*
> [!quote] caption
> Time per output token(TPOT) of DEFT with different prompt lengths in speculative decoding. 2500 5000 7500 10000 12500 15000 17500 20000

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 15)**

**Components / data flow:** Two side-by-side panels compare Single Layer Attention Latency (μs, y-axis) across KV Chunk Sizes of 128/256/512/1024 (x-axis) for Prompt Length = 1000 (left) and 4000 (right). Each panel plots 8 curves: DeFT-Flatten (solid) vs DeFT-Node-Chunk (dashed), each at four candidate tree sizes t ∈ {32, 64, 128, 256}, color-coded warm-to-cool (orange→yellow) by t with circle/square/triangle/x markers.

**Key takeaway:** Attention latency grows steeply with tree size t — t=256 (yellow) sits highest at ~300–1200 μs, while t=32 (orange) stays lowest near ~60 μs. DeFT-Flatten consistently beats DeFT-Node-Chunk at matched t, with the gap widening at t=128/256, especially in the 4000-token panel where DeFT-Node-Chunk exceeds 1100 μs vs DeFT-Flatten's ~700 μs at t=256.

**Caption (verbatim):**
*Figure 15: Ablation study for KV chunk size with DEFT. t is the token tree size in speculative decoding.*

### Figure 17 (p.27) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig17.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p27.png]]*
> [!quote] caption
> Decoding latency of DEFT with different prompt lengths in speculative decoding.

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 15)**

**Components / data flow:** Two side-by-side panels compare Single Layer Attention Latency (μs, y-axis) across KV Chunk Sizes of 128/256/512/1024 (x-axis) for Prompt Length = 1000 (left) and 4000 (right). Each panel plots 8 curves: DeFT-Flatten (solid) vs DeFT-Node-Chunk (dashed), each at four candidate tree sizes t ∈ {32, 64, 128, 256}, color-coded warm-to-cool (orange→yellow) by t with circle/square/triangle/x markers.

**Key takeaway:** Attention latency grows steeply with tree size t — t=256 (yellow) sits highest at ~300–1200 μs, while t=32 (orange) stays lowest near ~60 μs. DeFT-Flatten consistently beats DeFT-Node-Chunk at matched t, with the gap widening at t=128/256, especially in the 4000-token panel where DeFT-Node-Chunk exceeds 1100 μs vs DeFT-Flatten's ~700 μs at t=256.

**Caption (verbatim):**
*Figure 15: Ablation study for KV chunk size with DEFT. t is the token tree size in speculative decoding.*

### Figure 18 (p.28) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig18.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p28.png]]*
> [!quote] caption
> Attention latency of DEFT with different prompt lengths in speculative decoding.

> [!tip] 技术解读（多模态）
> ## Description (Figure 18)

**Type:** Comparative line plot, two side-by-side panels sharing a legend.

**Layout:**
- **Left panel:** Token Tree Size (#Queries) = 32 — right sub-plot mirrors with 64 queries.
- **X-axis:** Prompt Length (tokens), ~2,500 → 20,000.
- **Y-axis:** Attention Latency (seconds), 0 → ~30+.
- **Series (4):** Radix-Attention (pink/circles), DeFT-Flatten (olive/squares), DeFT-Node (teal/diamonds), DeFT-Node-Chunk (purple/triangles).

**Trend:** Radix-Attention grows steepest (≈33 s at 20 k tokens, 64 queries); DeFT-Node tracks below it; DeFT-Node-Chunk and DeFT-Flatten stay near-flat (≈8–10 s), with DeFT-Flatten lowest.

**Key takeaway:** Under speculative decoding, DeFT-Flatten scales sub-linearly with prompt length, while Radix-Attention latency explodes — DeFT-Flatten delivers ~3–4× speedup that widens as prompts grow and tree queries increase.

## Caption (verbatim)

**Figure 18:** Attention latency of DeFT with different prompt lengths in speculative decoding.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.2) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab01.png]]
> [!quote] caption
> Comparison of efficiency in sequence-based CoT (Wei et al., 2022) and tree-based ToT (Yao et al., 2023) decoding for a reasoning task. The task is sort- ing 128 numbers from Besta et al. (2023). The total gen- erated tokens of CoT is only 525 while 38 , 315 in ToT, resulting in inefficiency in end-t

> [!tip] 表格解读（多模态）
> ## Description

Table 1 compares four decoding configurations on a 128-number sorting task (Besta et al., 2023) across three efficiency metrics. **Rows (components/strategies):**
- *Flash-Decoding + CoT*: sequence-based baseline (latency 21s, IO-KV 0.6 TB, IO-PA 0).
- *Flash-Decoding + ToT*: tree-based, naive KV splitting (429.65s, 59.96 TB, 0).
- *Tree Attention + ToT* (Medusa-style): shares prefixes but incurs partial-attention IO (380.87s, 12.40 TB, 3.69 TB).
- *DeFT-Flatten (ours) + ToT*: flattens tree KV with prefix-aware memory (94.67s, 12.40 TB, 0).

**Data flow:** IO is decomposed into IO-KV (loading KV cache) and IO-PA (QK^T/softmax partials). CoT generated only 525 tokens vs. 38,315 for ToT — explaining the latency/IO gap.

**Key takeaway:** DeFT-Flatten delivers a **4.02× speedup** over the best baseline (94.67s vs. 380.87s) by eliminating redundant KV loads (59.96→12.40 TB) without paying the IO-PA tax that Tree Attention incurs.

## Caption (verbatim)

Table 1: **Comparison of efficiency in sequence-based CoT (Wei et al., 2022) and tree-based ToT (Yao et al., 2023) decoding for a reasoning task.** The task is *sorting 128 numbers* from Besta et al. (2023). The total generated tokens of CoT is only 525 while 38,315 in ToT, resulting in inefficiency in end-to-end latency (second) and IO (TB). IO mainly consists of two parts as follows. (i) *KV cache*: IO–KV; (ii) *Partial results during attention calculation like QK^T and softmax*: IO–PA; Baselines: (i) *Flash-Decoding* (Dao et al., 2023); (ii) *Tree Attention*: tree attention in Medusa (Cai et al., 2024).

### Table 2 (p.7) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab02.png]]
> [!quote] caption
> Comparison of QKV partitioning strategies for baselines (most of which are shown in Figure 3) and D E FT. For IO redundancy, significant issues are highlighted in red , while negligible ones are in blue . “Q” refers to queries, and “KV” refers to the KV cache. “DCM” stands for Dense Causal Mask (a m

> [!tip] 表格解读（多模态）
> **Description of the Main Figure (Table 2):**

The table compares QKV partitioning strategies across nine attention algorithms along four axes: **Grouping Indicator** (Q-guided vs. KV-guided), **KV Split Granularity** (none / by block / by tree node / GEMM), **IO Redundancy** (color-coded: red = significant, blue = negligible), and **Load-balancing Level** (rated by ★).

**Key Technical Takeaway:** While Q-guided methods (Flash, Radix, Tree Attention) introduce heavy KV/PA/DCM IO redundancy, DeFT-Flatten uniquely combines KV-guided grouping with depth-first block-flattened splitting, achieving top-tier load balancing (★★★) while keeping IO overhead negligible (only Q and the lightweight Bit Causal Mask). This avoids the trade-off between prefix-awareness and SM utilization seen in prior tree-based methods.

---

**Verbatim Caption Transcription:**

Table 2: Comparison of QKV partitioning strategies for baselines (most of which are shown in Figure 3) and DEFT. For IO redundancy, significant issues are highlighted in red, while negligible ones are in blue. "Q" refers to queries, and "KV" refers to the KV cache. "DCM" stands for Dense Causal Mask (a matrix), and "BCM" refers to Bit Causal Mask (a set of 64-bit integers). "PA" represents partial results during attention calculations, including Q*K*^T, Softmax, etc. More ⋆ symbols indicate better-balanced workloads for QKV partitions. Details on IO complexity can be found in Appendix A.5.

### Table 3 (p.8) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab03.png]]
> [!quote] caption
> Comparison of baselines and D E FT. Attention kernels of baselines are implemented to fit its memory management. Therefore, for a fair comparison with baselines, we implement D E FT-Node and D E FT-Flatten that fit both paged (Kwon et al., 2023)/unpaged memory management.

> [!tip] 表格解读（多模态）
> Note: What you've provided is a **table caption with column headers**, not a main figure with architecture/components/data flow. There is no figure image, diagram, or architecture illustration in your input — only the textual caption and beginning of Table 3's header row. I therefore cannot describe a figure's architecture/components/data flow because none is present. Below is what can be extracted from what's given.

**Caption (transcribed verbatim):**
"Table 3: **Comparison of baselines and DEFT.** Attention kernels of baselines are implemented to fit its memory management. Therefore, for a fair comparison with baselines, we implement DEFT-Node and DEFT-Flatten that fit both paged (Kwon et al., 2023)/unpaged memory management."

**Table header row (transcribed verbatim):**
"Method | Flash-Decoding | Tree Attention-Medusa | Radix Attention(Zheng et al., 2023) | DEFT"

**Key technical takeaway from the caption alone (≤120 words):**
The table benchmarks DEFT against three attention baselines (Flash-Decoding, Tree Attention-Medusa, and Radix Attention). To ensure a fair comparison, the authors customized each baseline's attention kernel to match its native memory management scheme. They additionally produced two DEFT variants — DEFT-Node (for paged memory, following Kwon et al., 2023, i.e., vLLM-style) and DEFT-Flatten (for unpaged/continuous memory) — so that performance differences reflect algorithmic rather than memory-management artifacts.

If you intended to share a figure, please re-upload it or paste its caption.

### Table 4 (p.8) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab04.png]]
> [!quote] caption
> Workloads generation . ToT-BFS stands for Tree-of-Thoughts (Yao et al., 2023) using breadth-first search. APPS (Hendrycks et al., 2021) is a competitive programming problem dataset. Medusa (Cai et al., 2024) is a speculative decoding framework. “GoT” stands for Graph-of-Thoughts (Besta et al., 2023)

> [!tip] 表格解读（多模态）
> # Note on the Provided Image

The image you shared **does not contain a figure** — it consists only of text content from the paper: **Table 4** (Workloads generation) plus surrounding paragraphs covering IO complexity analysis, implementation details, and the beginning of Section 4 (Experiments). Therefore, I cannot describe architecture/components/data flow, as no figure is present.

## What is actually shown (Table 4 + adjacent text)

**Table 4 — Workloads generation** maps three decoding tasks to their data sources and collection methods:

| Task | Prompt Dataset | Decoding Tree Source | Collection Method | Stopping Criteria |
|---|---|---|---|---|
| Few-shot prompting | APPS | — | Pad prompt to 4000 tokens | 400 iterations |
| Multi-step reasoning | 4 tasks in GoT | ToT-BFS | Reconstruct from interaction records with GPT-3.5 in GoT | End of task (~3500 iterations) |
| Speculative decoding | APPS | Medusa | Record token tree shape and accepted token length per step | ~1000 steps (max length = 6000) |

**Key takeaway from the text:** DEFT-Flatten is claimed to have favorable **IO complexity** compared to Flash-Decoding, Tree Attention-Medusa, and Tree Attention-SpecInfer. The DEFT attention kernel is built in **OpenAI Triton**, exposing explicit control over global→shared memory access and thread-block–granular attention computation.

## Caption Verbatim Transcription

> **Table 4: Workloads generation.** ToT-BFS stands for Tree-of-Thoughts (Yao et al., 2023) using breadth-first search. APPS (Hendrycks et al., 2021) is a competitive programming problem dataset. Medusa (Cai et al., 2024) is a speculative decoding framework. "GoT" stands for Graph-of-Thoughts (Besta et al., 2023), which contains iteration records using GPT-3.5 for complex reasoning tasks within ToT-BFS. See more details in Table 13.

If you intended to share a different figure (e.g., the DEFT architecture diagram), please re-upload it and I'll describe it directly.

### Table 6 (p.10) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab06.png]]
> [!quote] caption
> [Different KV Splitting Strategies] Comparison of D E FT-Node, D E FT-Node-Chunk and D E FT- Flatten in average attention latency (second) with NVIDIA A100 (80GB) for Llama3-8B model(GQA). This table is supplementary to Table 16. The fastest method is in bold , and the second fastest is underlined .

> [!tip] 表格解读（多模态）
> ## Description

**Architecture/Components:** The table is organized in a benchmark-comparison layout with rows indexed by *Memory/Method* (Radix Attention baseline plus three DEFT variants: Node, Node-Chunk, Flatten) and columns grouped into three workload categories — *Few-shot Prompting* (b=20,30,50 contexts), *Multi-Step Reasoning* (Sorting, Document, Keyword), and *Speculative Decoding* (Set, t=32/64/128/256). Each cell reports mean attention latency in seconds.

**Data flow:** A single benchmark sweep over Llama3-8B (GQA) on an A100 80GB accumulates per-task latency values, which are then ranked within each cell — bold = fastest, underline = second fastest.

### Key technical takeaway

**DEFT-Flatten is uniformly fastest across every workload**, dominating from short prompts (b=20: 3.47s vs. Radix's 5.99s) through long-context reasoning (Keyword: 2.57s vs. 3.11s) up to deep speculative decoding (t=256: 40.56s vs. 145.43s — a ~3.6× speedup). The hierarchy Flatten > Node > Node-Chunk shows that **collapsing hierarchical KV indices into a flat layout minimizes tree-walk overhead, and the win grows with sequence length**, making Flatten the most scalable KV-splitting strategy.

## Verbatim Caption

> **Table 6:** **[Different KV Splitting Strategies]** Comparison of DEFT-Node, DEFT-Node-Chunk and DEFT-Flatten in average attention latency (second) with NVIDIA A100 (80GB) for Llama3-8B model(GQA). This table is supplementary to Table 16. The fastest method is in bold, and the second fastest is underlined. Radix Attention is the best baseline in decoding latency. See details of more baselines in Table 16.

### Table 8 (p.10) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab08.png]]
> [!quote] caption
> [Different Model Sizes] Comparison of decoding latency speedup and Attention/FFN latency ratio (in short as A/F-LR ) between D E FT and Radix Attention for Codellama-34B and Codellama-7B models. Radix Attention is the best baseline in decoding latency. b represents the tree width, and t denotes the 

> [!tip] 表格解读（多模态）
> **Description:** The visible content is the caption for Table 8, which presents a quantitative comparison of decoding latency performance between DEFT and Radix Attention across two model sizes (Codellama-34B and Codellama-7B). The table organizes results by workload category—Few-shot Prompting, Multi-step Reasoning (Sorting), and Speculative Decoding—with tree width *b*=30 and token tree size *t*=64. Metrics reported include decoding latency speedup and the Attention/FFN latency ratio (A/F-LR).

**Key technical takeaway:** DEFT achieves decoding latency speedups over the strongest baseline (Radix Attention) by restructuring attention over a sparse token tree, making the attention workload lighter than the FFN workload and yielding favorable A/F-LR trade-offs across model scales and inference regimes.

**Caption (verbatim):**
> Table 8: [Different Model Sizes] Comparison of decoding latency speedup and Attention/FFN latency ratio (in short as A/F-LR) between DEFT and Radix Attention for Codellama-34B and Codellama-7B models. Radix Attention is the best baseline in decoding latency. *b* represents the tree width, and *t* denotes the token tree size. For multi-step reasoning, we test the task *sorting* whose prompt length is about 1k tokens.

### Table 9 (p.18) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab09.png]]
> [!quote] caption
> Comparison among D E FT and concurrent works in single-context large-batch sampling scenarios, including Chunk-Attention (Ye et al., 2024a), Hygragen (Juravsky et al., 2024) and Bifurcated-Attention (Athi- waratkun et al., 2024). RelayAttention (Zhu et al., 2024) and Cascade-inference (Ye et al., 20

> [!tip] 表格解读（多模态）
> # Clarification

The provided image does **not** show an architecture diagram with components/data flow. It contains **Table 9**, a comparison matrix, plus a "Comparison of differences" discussion section. I'll describe the table and transcribe its caption verbatim.

---

## Description of the Table (Table 9)

The table is a **side-by-side comparative matrix** benchmarking six methods for single-context large-batch tree-decoding:

- **Rows (axes of comparison):** IO-aware levels · Tree KV split granularity · Load-balanced level · Goal metrics
- **Columns (methods):** Chunk-Attention · Hygragen · Bifurcated-Attention · DeFT-Node · DeFT-Node-Chunk · DeFT-Flatten

**The follow-up discussion identifies two key technical gaps in prior work that DeFT addresses:**
1. **Depth-limited IO-awareness** — prior methods (Chunk-Attention, Hygragen, Bifurcated) only exploit KV-cache reuse for two levels (root + depth-1), wasting reuse potential in deeper trees (e.g., multi-step reasoning with thousand-token non-root prefixes).
2. **Workload imbalance** — splitting purely by depth produces uneven QKV groups; DeFT introduces finer-grained split granularity (per-node or flatten-then-block) for more balanced compute.

**Key takeaway (≤120 words):** DeFT generalizes KV-cache IO reuse to *all* tree depths—not just root + depth-1—enabling reuse of long non-root prefix tokens (e.g., thousands of tokens in chain-of-thought reasoning). Concurrently, by decoupling KV-split granularity from tree depth (splitting per-node or after flattening) and operating at every level, DeFT achieves better load balancing across QKV groups without sacrificing this multi-level IO benefit, addressing both hardware-inefficiency gaps of prior single-context large-batch sampling methods.

---

## Verbatim Caption Transcription

> **Table 9:** Comparison among DEFT and concurrent works in single-context large-batch sampling scenarios, including Chunk-Attention (Ye et al., 2024a), Hygragen (Juravsky et al., 2024) and Bifurcated-Attention (Athiwaratkun et al., 2024). RelayAttention (Zhu et al., 2024) and Cascade-inference (Ye et al., 2024b) are similar to Hygragen. More ⋆ means more balanced workloads after tree split, which also shows how insensitive the acceleration is to the tree topology.

### Table contents (verbatim)

| Method | Chunk-Attention | Hygragen | Bifurcated-Attention | DeFT-Node | DeFT-Node-Chunk | DeFT-Flatten |
|---|---|---|---|---|---|---|
| **IO-aware levels** | 2 (depth ≤ 1) | 2 (depth ≤ 1) | 2 (depth ≤ 1) | all (every depth) | all (every depth) | all (every depth) |
| **Tree KV split granularity** | by node first, then by block | by tree depth | by tree depth | by tree node | by tree node, then by block | flatten tree, then by block |
| **Load-balanced level** | ⋆⋆⋆ | ⋆⋆ | ⋆⋆ | ⋆ | ⋆⋆⋆ | ⋆⋆⋆⋆ |
| **Goal metrics** | throughput | throughput | latency | latency | latency | latency |

If you intended to share a *separate* architectural diagram (e.g., DeFT's system pipeline), please re-upload that figure and I'll analyze it as requested.

### Table 10 (p.18) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab10.png]]
> [!quote] caption
> Technique list of D E FT. What we propose is in red . The details of the first four techniques are in Section 3.3, while the details of the following techniques are discussed in this chapter.

> [!tip] 表格解读（多模态）
> **Description (≈115 words):**
Table 9 is a 6-column × 4-row comparison matrix contrasting Chunk-Attention, Hygragen, Bifurcated-Attention, and three DEFT variants (Node, Node-Chunk, Flatten) along four axes: IO-aware levels, tree KV split granularity, load-balanced level (★★★★ = best), and goal metric. Reading row-by-row, one traces how each method partitions the decoding tree's KV cache—from coarse 2-level (root/leaf) splits in prior work to fine-grained per-node splits in DEFT. **Key takeaway:** Unlike competitors that only handle 2-level IO (depth ≤ 1) and split by depth, DEFT spans every depth with node-level granularity and load-balancing, enabling KV reuse across multi-step prefixes that are otherwise re-materialized.

**Verbatim caption:**
Table 9: Comparison among DEFT and concurrent works in single-context large-batch sampling scenarios, including Chunk-Attention (Ye et al., 2024a), Hygragen (Juravsky et al., 2024) and Bifurcated-Attention (Athiwaratkun et al., 2024). RelayAttention (Zhu et al., 2024) and Cascade-inference (Ye et al., 2024b) are similar to Hygragen. More ⋆ means more balanced workloads after tree split, which also shows how insensitive the acceleration is to the tree topology.

### Table 11 (p.21) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab11.png]]
> [!quote] caption
> Notations .

> [!tip] 表格解读（多模态）
> **Note:** The provided image is a notation/legend table (Table 11), not an architecture figure with components/data flow. I'll describe it accordingly.

**Description of Table 11 (Notations Table):**
This is a symbol-definition reference table laying out the mathematical variables used throughout the paper's analysis of tree-based speculative decoding. It defines: tree-topology quantities (*lₙ* = number of leaf/queries, *Nᵢ* = root→leaf token path length, *N_tree* = total tokens per tree, *#node* = total nodes, *nᵢ* = node token length); attention parameters (*d_head* = head dimension, *s_c* = √d_head scaling); and the prefix-sharing factor *F_s = (ΣNᵢ)/N_tree*, which quantifies how much KV-cache IO a method can save by reusing shared prefixes across tree branches.

**Key Technical Takeaway:** Sequence-based decoders (naive attention, Flash-Decoding) pay an *F_s*-fold KV-cache IO penalty because they ignore tree topology, while tree-aware fused kernels (DEFT Node/Flatten) share prefix loads. Caveat — partial-result tensors (QKᵀ, Softmax) become the new IO bottleneck once *lₙ* is large (e.g., Llama with *lₙ*=29, *d_head*=128 makes their IO match the KV-cache IO). SpecInfer's Q-Guided Grouping forfeits KV sharing entirely, loading the full cache per query.

**Caption (verbatim):**
Table 11: Notations.

### Table 12 (p.22) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab12.png]]
> [!quote] caption
> IO complexity breakdown for various methods. O (1) denotes the IO cost for a single data in the tensor across all layers and heads, which is equivalent to # heads ∗ # layer ∗ dtype _ size . The best among all methods in the table is in red , while the (potential) worst is in blue . Query IO is omitt

> [!tip] 表格解读（多模态）
> **Description (≤120 words)**
The figure presents Table 12, a comparative ledger of IO complexity for eight attention-scheduling methods used in tree-decoding / speculative LLM inference. The table is structured as a matrix: rows enumerate the methods (Naive Attention, Flash-Decoding, Radix-Attention, Tree Attention-M/S, DEFT-Node, DEFT-Node-Chunk, DEFT-Flatten), while columns trace the attention data-flow pipeline — KV cache, QKᵀ, scaled QKᵀ/s_c, Mask(M), M + QKᵀ/s_c, and Softmax — each annotated with a Big-O memory-access cost. Best/worst entries are color-coded (red/blue). **Key takeaway:** the DEFT family attains the optimal KV-cache footprint O(2d_head·N_tree) while collapsing every downstream intermediate-tensor IO to zero, eliminating the redundant passes still incurred by Flash-Decoding and Radix-Attention (both O(2d_head·ΣN_i)).

**Caption (verbatim)**
Table 12: **IO complexity breakdown for various methods.** 𝒪(1) denotes the IO cost for a single data in the tensor across all layers and heads, which is equivalent to #heads ∗ #layer ∗ dtype_size. The best among all methods in the table is in red, while the (potential) worst is in blue. Query IO is omitted as it is 𝒪(kln d_head) for all methods. Here, k is the number of QKV groups: for DEFT-Node k = #node; for DEFT-Node-Chunk k = ∑_{i=1}^{#node} ceil(n_i/b_s), which is the node number after chunk wise; for DEFT-Flatten, k = Ntree/b_s, where b_s is the block size of KV; for others, k = 1. M in Tree Attention-M is short for Medusa (Cai et al., 2024), while S in Tree Attention-S is short for SpecInfer (Miao et al., 2023).

### Table 13 (p.23) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab13.png]]
> [!quote] caption
> Details of generated workloads . For multi-step reasoning, we include these 4 tasks from Besta et al. (2023): (1) Sorting 128 numbers ( sorting in short); (2) Document merging ( document in short); (3) Keyword counting ( keyword in short); (4) Set intersection ( set in short). d , and w means depth 

> [!tip] 表格解读（多模态）
> ## Figure Description

**Architecture/Components:** Table 13 is a 4-column specification table organizing workload generation parameters. Columns include **Task** (listing reasoning categories), **Tree Shape** (defining depth *d* and width *w* parameters per subtask), **Decoding Tree Source** (specifying ToT-BFS method from Besta et al. 2023), and **Records Contents** (enumerating stored metadata: prompts, tree shapes, thought sizes). Rows map four reasoning tasks (sorting, document, keyword, set) to their respective tree topologies.

**Key Technical Takeaway:** Workload construction decouples **topology specification** (shape parameters) from **content sourcing** (benchmark prompts), enabling systematic stress-testing of speculative decoding trees across diverse reasoning workloads using the tree skeletons from Medusa (Cai et al., 2024).

## Caption (Verbatim)

Table 13: **Details of generated workloads.** For multi-step reasoning, we include these 4 tasks from Besta et al. (2023): (1) Sorting 128 numbers (*sorting* in short); (2) Document merging (*document* in short); (3) Keyword counting (*keyword* in short); (4) Set intersection (*set* in short). *d* and *w* means depth and width of the tree, respectively. *t* means the token tree size for speculative decoding, where the tree topology is from Medusa (Cai et al., 2024).

### Table 14 (p.24) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab14.png]]
> [!quote] caption
> [GPU Utilization Microbenchmark] Latency of a single layer of Attention (in µ s), SM Compute Throughput Ratio, Memory Throughput Ratio, and Low Utilization Ratio for D E FT on an NVIDIA A100 (80GB) using the LLama3-8B model (GQA). The workload is speculative decoding with 64 queries and a prompt wit

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**
This table compares two DEFT attention-layer implementations—DEFT-Node and DEFT-Flatten—on an NVIDIA A100 (80GB) running Llama3-8B under speculative decoding with 64 queries (4k-token prompt). The measurements cover four GPU-usage metrics: per-layer attention latency (μs), SM compute throughput ratio, memory bandwidth ratio, and the time ratio spent below 5% SM utilization. Data flows from input workload → attention layer → profiler → reported metrics. Key takeaway: DEFT-Flatten is ~4.2× faster (226.82 μs vs 961.38 μs), boosts compute throughput from 7.60% to 21.19%, lifts memory throughput from 17.39% to 51.91%, and eliminates low-utilization idle time (0.00% vs 82.35%), demonstrating that flattening the tree structure is critical to keeping SMs busy in speculative decoding.

**Caption (verbatim):**
Table 14: [GPU Utilization Microbenchmark] Latency of a single layer of Attention (in μs), SM Compute Throughput Ratio, Memory Throughput Ratio, and Low Utilization Ratio for DEFT on an NVIDA A100 (80GB) using the LLama3-8B model (GQA). The workload is speculative decoding with 64 queries and a prompt with 4k tokens. The *Compute Throughput Ratio* refers to the utilization of the Streaming Multiprocessors (SMs) in the GPU. The *Memory Throughput Ratio* represents the ratio between actual memory throughput and maximum bandwidth. The *Low Utilization Time Ratio* is defined as the proportion of time when the *Compute Throughput Ratio* falls below 5%.

### Table 15 (p.24) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab15.png]]
> [!quote] caption
> Inference accuracy of D E FT in attention score and perplexity (PPL) . PPL is calculated after 400 iterations of decoding. Vanilla Attention is the implementation from Huggingface Transformers.

> [!tip] 表格解读（多模态）
> There is no figure provided in your message — only the caption for **Table 15** along with its column headers. I'll address each part of your request based on what is actually supplied.

## What the Table Appears to Convey

**Components shown:** A results table with three metric columns:
- Relative Attention Error (↓)
- Perplexity / PPL (↓)
- Relative PPL Error (↓)

**Data context:** DEFT's inference outputs are compared against a baseline ("Vanilla Attention" from Huggingface Transformers), with PPL computed after 400 decoding iterations.

**Key technical takeaway:** DEFT trades negligible accuracy degradation in attention scores and language-modeling perplexity relative to canonical Huggingface attention, implying it is a near-lossless approximation suitable for inference.

## Caption Verbatim Transcription

> **Table 15:** Inference accuracy of **DEFT** in attention score and perplexity (PPL). PPL is calculated after 400 iterations of decoding. Vanilla Attention is the implementation from Huggingface Transformers.

If you intended to share an actual figure (architecture diagram, etc.), it did not come through — please re-upload the image and I'll provide the architecture/data-flow description you asked for.

### Table 16 (p.25) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab16.png]]
> [!quote] caption
> Average attention latency (in seconds) for tree-based decoding and its impact on decoding latency. Here, b represents the tree width, and t denotes the token tree size (i.e., the number of tree-structured queries). Attention Speedup over the best attention refers to the speedup of D E FT-Flatten com

> [!tip] 表格解读（多模态）
> ## Description

The figure is **a data table (Table 16)**, not an architecture diagram, so there is no architecture/components/data flow to describe. Instead, it presents numerical latency benchmarks structured as follows:

**Structure:**
- **Columns:** Grouped into four workload categories — *Few-shot Prompting* (b = 20/30/50), *Multi-Step Reasoning* (Sorting, Document, Keyword, Set), and *Speculative Decoding* (t = 32/64/128/256).
- **Rows:** Memory regimes (*Unpaged* vs. *Paged*) × Methods (Flash-Decoding, Tree Attention-Medusa, Radix Attention, DEFT-Flatten), followed by three speedup-ratio rows.

**Key takeaway:** DEFT-Flatten achieves up to **3.59× attention speedup** and **2.23× decoding speedup** over Radix Attention on large speculative-decoding trees (t = 256), while remaining stable where baselines (Flash-Decoding) hit OOM on the A100 80GB.

## Caption (verbatim)

> Table 16: Average attention latency (in seconds) for tree-based decoding and its impact on decoding latency. Here, *b* represents the tree width, and *t* denotes the token tree size (i.e., the number of tree-structured queries). *Attention Speedup over the best attention* refers to the speedup of DEFT-Flatten compared to the best baseline (typically *Tree Attention-Medusa*) in attention calculation. *Radix Attention* is the best baseline for decoding latency. Note that KV cache management is not included in the attention latency. ⋆ denotes out-of-memory (OOM) errors for the A100 80GB GPU. For more details on decoding latency, see Table 5.

### Table 17 (p.25) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab17.png]]
> [!quote] caption
> Average end-to-end IO (TB) during decoding. Data format is Left/Right: (Left) KV Cache IO; (Right) partial results IO, including QK T , QK ⊤ /s c , Mask M , M + QK ⊤ /s c and Softmax . b means tree width. t denotes the token tree size (i.e., the number of tree-structured queries). ⋆ means out of mem

> [!tip] 表格解读（多模态）
> ## Description

**Architecture/Components**: The table evaluates four decoding strategies—Flash-Decoding, Tree Attention-Medusa, Radix Attention, and DeFT-Flatten—across three workload categories: Few-shot Prompting (varying branch width *b*), Multi-Step Reasoning (Sorting/Document/Keyword/Set), and Speculative Decoding (varying tree size *t*). Each cell reports two I/O metrics: KV Cache I/O and partial-results I/O (QK^T, QK^T/s_c, Mask M, M+QK^T/s_c, Softmax). A summary row quantifies DeFT-Flatten's relative reduction.

**Key Takeaway**: DeFT-Flatten flattens tree-structured speculative queries into prefix-aligned chunks, collapsing KV cache reads (up to ~99.6% reduction) while keeping partial-results I/O competitive—making long-context speculative decoding tractable where alternatives OOM.

**Verbatim caption**:
"Table 17: Average end-to-end IO (TB) during decoding. Data format is Left/Right: (Left) KV Cache IO; (Right) partial results IO, including $QK^T, QK^\top/s_c$, Mask $M$, $M + QK^\top/s_c$ and Softmax. $b$ means tree width. $t$ denotes the token tree size (i.e., the number of tree-structured queries).⋆ means out of memory for A100 80GB."

### Table 18 (p.28) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab18.png]]
> [!quote] caption
> [Ablation Study of Model Size and Prompt Length] Comparison of decoding speedup and Attention/FFN latency ratio ( A/F-LR ) between D E FT and Radix Attention for Codellama-34B and Codellama-7B across varying prompt lengths in the sorting reasoning task. Radix Attention is the best baseline in decodi

> [!tip] 表格解读（多模态）
> **Note:** The image shows a *table* (Table 18), not an architecture/component diagram, so I'll describe its structure and contents instead.

**Description (~120 words):**
The table compares DEFT against the Radix Attention baseline across two model sizes (Codellama-7B, Codellama-34B) and three prompt lengths (1k, 5k, 8k tokens) on a sorting reasoning task, organized into three metric blocks: (1) **Decoding latency Speedup** of DEFT over Radix Attention, (2) **Radix Attention's A/F-LR**, and (3) **DEFT-Flatten's A/F-LR**, where A/F-LR is the Attention-to-FFN latency ratio. Speedups grow with prompt length (7B: 1.09× → 1.53×; 34B: 1.03× → 1.28×), and A/F-LR rises for both methods as sequences lengthen. DEFT-Flatten consistently produces a lower A/F-LR than Radix Attention at every configuration, confirming attention-side latency reduction.

**Key takeaway:** DEFT-Flatten systematically reduces the Attention/FFN latency ratio versus Radix Attention across all scales, but the decoding speedup shrinks at 34B (max 1.28× vs. 1.53× at 7B), revealing diminishing returns on larger models with longer contexts.

**Caption (verbatim):**
Table 18: [Ablation Study of Model Size and Prompt Length] Comparison of decoding speedup and Attention/FFN latency ratio (A/F-LR) between DEFT and Radix Attention for Codellama-34B and Codellama-7B across varying prompt lengths in the sorting reasoning task. Radix Attention is the best baseline in decoding latency.

### Table 19 (p.28) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab19.png]]
> [!quote] caption
> [Different GPUs] Speedup of D E FT in average attention latency (second) with NVIDIA RTX 4090 (24GB) for LLama3-8B model(GQA). Radix Attention is the best baseline in decoding latency.

> [!tip] 表格解读（多模态）
> **Architecture/Components/Data Flow:** This benchmark table (Table 19) compares three attention computation methods under Paged memory on an NVIDIA RTX 4090 (24GB), running the LLama3-8B model with GQA. The components evaluated are Radix Attention (baseline), DEFT-Node-Chunk, and DEFT-Flatten. The data flow measures average attention latency (seconds) across three workload regimes—Few-shot Prompting (b=30), Multi-Step Reasoning-Sorting, and Speculative Decoding (t=64)—with a final row reporting the attention speedup of DEFT over the best decoding baseline.

**Key Technical Takeaway:** DEFT-Flatten consistently yields the lowest latency across all three scenarios (2.95s, 23.86s, 14.04s), achieving up to a **2.40× speedup** in speculative decoding workloads compared to Radix Attention's decode path, demonstrating its effectiveness for tree-structured KV-cache attention.

**Caption (verbatim):**
> Table 19: [Different GPUs] Speedup of DEFT in average attention latency (second) with NVIDIA RTX 4090 (24GB) for LLama3-8B model(GQA). Radix Attention is the best baseline in decoding latency.

### Table 20 (p.28) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab20.png]]
> [!quote] caption
> [Different Model Architectures(GQA)] Speedup of D E FT in average attention latency (second) with NVIDIA A100(80GB) for Codellama-34B model(GQA). Radix Attention is the best baseline in decoding latency.

> [!tip] 表格解读（多模态）
> **Description (≈120 words):**

The table compares attention latency (seconds) across three attention schemes — Radix Attention (baseline), DeFT-Node-Chunk, and DeFT-Flatten — evaluated under paged memory on Codellama-34B (GQA) with an NVIDIA A100 80GB. Rows represent methods; columns represent workloads: Few-shot Prompting (b=30), Multi-Step Reasoning–Sorting, and Speculative Decoding (t=64). DeFT-Flatten consistently wins, recording 9.62s, 84.30s, and 48.76s respectively, versus Radix Attention's 16.85s, 95.14s, and 164.33s. The bottom row reports attention speedup over the best decoding baseline: 1.75×, 1.13×, and 3.37×. **Key takeaway:** flattening the attention computation tree yields the largest gains on speculative decoding (3.37×) by eliminating per-node overhead that dominates long-horizon generation.

**Caption (verbatim):**

Table 20: **[Different Model Architectures(GQA)]** Speedup of **DeFT** in average attention latency (second) with NVIDIA A100(80GB) for Codellama-34B model(GQA). Radix Attention is the best baseline in decoding latency.

### Table 21 (p.29) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab21.png]]
> [!quote] caption
> [Different Model Architectures(MHA)] Speedup of D E FT in average attention latency (second) with NVIDIA A100(80GB) for Codellama-7B model(MHA). Radix Attention is the best baseline in decoding latency.

> [!tip] 表格解读（多模态）
> **Description of the main figure (Table 21 + Algorithm 1):**

The page presents two artifacts. **Table 21** is a benchmark table comparing average attention latency (seconds) across three methods—**Radix Attention** (baseline), **DEFT-Node-Chunk**, and **DEFT-Flatten**—evaluated on an NVIDIA A100 80GB using the Codellama-7B MHA model. It reports latencies for three workloads: Few-shot Prompting (b=30), Multi-Step Reasoning-Sorting, and Speculative Decoding (t=64), ending with a "Attention Speedup over the best decoding" row showing 1.50×, 1.23×, and 2.65× gains respectively.

**Algorithm 1 (DEFT-Node, Phase 1: QKV Preparation)** pseudocode takes a query matrix Q ∈ R^(b_q,d), key/value cache lists KL/VL for N sequences, and tree topology T. It builds two mappings—QMapKV[idx] (queries → their prefix KV indices via GetPrefixKVIndices) and KVMapQ[i] (each sequence's KV → all queries sharing it via GroupQueryToKV)—then returns both maps.

**Key technical takeaway:**
DEFT-Node exploits a prefix tree of shared KV caches to compute attention in two phases: first prepare per-query KV index mappings (Phase 1, shown), then apply Flash Attention on grouped QKV partitions and merge via global LogSumExp reduction (Phase 2), mirroring Flash-Decoding. This tree-aware grouping avoids redundant KV reads across shared prompt prefixes, yielding up to 2.65× speedup over Radix Attention on speculative decoding, where shared-prefix reuse is heaviest.

**Caption transcribed verbatim:**

Table 21: [Different Model Architectures(MHA)] Speedup of DEFT in average attention latency (second) with NVIDIA A100(80GB) for Codellama-7B model(MHA). Radix Attention is the best baseline in decoding latency.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\begin{aligned} \textstyle \operatorname{SegAttn}(\mA_0, \mA_1, \mA_2)= \frac{ \mA_0 e^{\operatorname{LSE}(\mQ, \mK_0)} + \mA_1 e^{\operatorname{LSE}(\mQ, \mK_1)} + \mA_2 e^{\operatorname{LSE}(\mQ, \mK_2)} }{ e^{\operatorname{LSE}(\mQ, \mK_0)} + e^{\operatorname{LSE}(\mQ, \mK_1)} + e^{\operatorname{LSE}(\mQ, \mK_2)} } \,, \text{ where } e := \text{exp} \,. \end{aligned}
$$

## 技术点深读（DEEP）

![[deep/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference.txt`（112630 字符）供引用检索。