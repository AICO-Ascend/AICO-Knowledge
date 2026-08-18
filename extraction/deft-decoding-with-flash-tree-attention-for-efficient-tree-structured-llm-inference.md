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
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p01.png]]
> [!quote] caption
> Usually, these applications produce substantially more tokens than traditional ones, to provide large space for tree search (Graves, 2012; Lu et al., 2022; Liu et al., 2023) or selection, as shown in Table 1.

> [!tip] 技术解读（多模态）
> No figure is visible on this page — it is the title page of the paper "DEFT: Decoding with Flash Tree-Attention for Efficient Tree-structured LLM Inference," containing only the title, author affiliations, abstract, and the opening of the Introduction. The text references "Figure 1" (illustrating tree-structured LLM applications such as self-consistency, few-shot prompting, multi-step reasoning, and speculative decoding) and "Table 1" (showing token volume differences), but neither the figure nor its caption appears in the provided image, so I cannot describe the figure's architecture/components/data flow or transcribe its caption verbatim.

### Figure 2 (p.5) ⭐深度解读
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p05.png]]
> [!quote] caption
> Overview of DEFT. Input Metadata is prepared in the system elaborated in Appendix A.1. In QKV

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】DeFT flash 树注意力(Fig.2)：① Input Metadata（Q + 共享前缀 K0 + 分支 K1/K2 + 树拓扑）载入 SM；② Phase1 QKV 准备(HBM 2TB/s)：KV-Guided Grouping 跨分支复用 K0、Flattened Tree KV Splitting 把树切成均衡组 G0/G1/G2 并行；③ Phase2 注意力计算(Shared Mem 19TB/s)：DeFT kernel 各 split 跑部分注意力 + 树拓扑感知全局归约(A0/A1/A2→Final)，避免跨全分支全局同步。消除共享前缀冗余 KV IO、平衡 SM 负载→内存高效、硬件友好的树结构投机解码注意力。架构核心图。

### Figure 3 (p.6) ⭐深度解读
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p06.png]]
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
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p09.png]]
> [!quote] caption
> Latency breakdown for specula- tive decoding with a token tree of 32 queries, whose tree topology is from Medusa (Cai et al., 2024). U means unpaged memory.

> [!tip] 技术解读（多模态）
> **Figure 4 — Architecture & Data Flow**

A stacked bar chart comparing decoding latency (seconds) across six attention methods for speculative decoding with a 32-query Medusa token tree. Each bar is partitioned into three components: **Attention** (orange, bottom), **KV Management** (blue, middle), and **Other** (green, top). Methods include Radix Attention, DeFT-Flatten, DeFT-Node, DeFT-Node-Chunk, and two unpaged variants (U). Total latency rises from ~50s (Radix Attention) to >275s (unpaged Tree Attention-Medusa).

**Key technical takeaway:** With **unpaged KV caching**, KV management dominates (69.1–83.4% of latency) due to costly tensor materialization, but **paged memory flips the bottleneck to attention** (51.1–58.3%)—eliminating data-movement overhead and exposing attention as the next optimization target.

**Caption (verbatim):**
Figure 4: Latency breakdown for speculative decoding with a token tree of 32 queries, whose tree topology is from Medusa (Cai et al., 2024). U means unpaged memory.

### Figure 5 (p.15) ⭐深度解读
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p15.png]]
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
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p17.png]]
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
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p19.png]]
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
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p19.png]]
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
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p20.png]]
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
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p21.png]]
> [!quote] caption
> When the number of leaf nodes/queries ln is sufficiently large, the IO cost of partial results might become comparable to that of the KV cache. For instance, in the Llama models (Touvron et al., 2023a;b), where dhead =128, with ln =29, the total IO cost of QKT , M, QK⊤ sc , M + QK⊤ sc , and

> [!tip] 技术解读（多模态）
> **Figure Description (Table 11: Notations)**

This table defines the mathematical notations used throughout the DEFT (Decoding with Flash Tree-attention) paper for analyzing tree-decoding IO complexity. It catalogs variables spanning tree topology (leaf nodes *l_n*, node count *#node*, per-node token length *n_i*, root-to-leaf path length *N_i*, and total tree length *N_tree*), attention kernel parameters (*d_head*, scale factor *s_c* = √*d_head*), and a derived metric *F_s* — the prefix-sharing factor — quantifying KV-cache reuse across branches.

**Key Technical Takeaway:** The shared-prefix factor *F_s* = (Σ N_i) / N_tree captures how tree-structured speculative decoding amortizes KV-cache IO across multiple query branches; tree-topology-aware schemes (DEFT) leverage *F_s* to reduce HBM accesses, whereas sequence-based methods incur *F_s* times the KV-cache IO overhead since they cannot exploit branch sharing.

**Caption (verbatim):**
Table 11: **Notations**.

### Figure 12 (p.23) ⭐深度解读
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p23.png]]
> [!quote] caption
> The detailed procedure of reconstructing tree templates for multi-step reasoning. (Left)

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

Figure 12 illustrates a two-stage pipeline for building decoding tree templates from real reasoning traces. **Left panel (green, "Reconstruct thought trees")**: A Prompt node expands breadthwise into w thoughts at each of d depths, forming a thought tree. Each node is labeled `thought_i_j`; checkmarks denote "best thought to keep," red minus signs mark "thoughts to prune," and dashed ellipses indicate depth/width omission. **Right panel (orange, "Tree templates for decoding")**: Each selected thought is encoded with five metadata fields — start/end iteration, thought size, parent id, and children id — which feed two structured tables: *Branch records* (which thoughts to generate at iteration i from parent (i-1,k)) and *Prune records* (which thoughts to discard at iteration j). These tables drive the tree decoder to replicate ToT structure faithfully.

**Key technical takeaway:** Tree-decoding guidance requires only two compact record types (branch + prune) derived from iteration-tagged thought metadata, enabling ToT reasoning to be replayed on standard tree-aware attention kernels without re-running LLM inference.

**Caption verbatim:**

Figure 12: **The detailed procedure of reconstructing tree templates for multi-step reasoning.** (Left) Reconstructing reasoning trees from practical reasoning records as outlined in (Besta et al., 2023) involves capturing the following aspects: (1) the structure of trees, characterized by their depth *d* and width *w*; (2) the token length associated with each thought; and (3) the best thought at each depth along with its corresponding score. For the task of document merging, the tree depth is set to *d* = 3, with a width of *w* = 10 at each depth. For sorting 128 numbers, the depth is reduced to *d* = 10, while maintaining the same width of *w* = 10. See details of tree topology for other multi-step reasoning tasks in Table 13. (Right) Utilizing the extracted thought information from Left, we can generate tree templates for decoding, encompassing *branch records* and *prune records*. These records are instrumental in guiding the tree decoding process to produce decoding trees that faithfully replicate the structure of the tree-of-thoughts.

### Figure 13 (p.25) ⭐深度解读
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p25.png]]
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
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p26.png]]
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
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p27.png]]
> [!quote] caption
> Time per output token(TPOT) of DEFT with different prompt lengths in speculative decoding. 2500 5000 7500 10000 12500 15000 17500 20000

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 15)**

**Components / data flow:** Two side-by-side panels compare Single Layer Attention Latency (μs, y-axis) across KV Chunk Sizes of 128/256/512/1024 (x-axis) for Prompt Length = 1000 (left) and 4000 (right). Each panel plots 8 curves: DeFT-Flatten (solid) vs DeFT-Node-Chunk (dashed), each at four candidate tree sizes t ∈ {32, 64, 128, 256}, color-coded warm-to-cool (orange→yellow) by t with circle/square/triangle/x markers.

**Key takeaway:** Attention latency grows steeply with tree size t — t=256 (yellow) sits highest at ~300–1200 μs, while t=32 (orange) stays lowest near ~60 μs. DeFT-Flatten consistently beats DeFT-Node-Chunk at matched t, with the gap widening at t=128/256, especially in the 4000-token panel where DeFT-Node-Chunk exceeds 1100 μs vs DeFT-Flatten's ~700 μs at t=256.

**Caption (verbatim):**
*Figure 15: Ablation study for KV chunk size with DEFT. t is the token tree size in speculative decoding.*

### Figure 17 (p.27) ⭐深度解读
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p27.png]]
> [!quote] caption
> Decoding latency of DEFT with different prompt lengths in speculative decoding.

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 15)**

**Components / data flow:** Two side-by-side panels compare Single Layer Attention Latency (μs, y-axis) across KV Chunk Sizes of 128/256/512/1024 (x-axis) for Prompt Length = 1000 (left) and 4000 (right). Each panel plots 8 curves: DeFT-Flatten (solid) vs DeFT-Node-Chunk (dashed), each at four candidate tree sizes t ∈ {32, 64, 128, 256}, color-coded warm-to-cool (orange→yellow) by t with circle/square/triangle/x markers.

**Key takeaway:** Attention latency grows steeply with tree size t — t=256 (yellow) sits highest at ~300–1200 μs, while t=32 (orange) stays lowest near ~60 μs. DeFT-Flatten consistently beats DeFT-Node-Chunk at matched t, with the gap widening at t=128/256, especially in the 4000-token panel where DeFT-Node-Chunk exceeds 1100 μs vs DeFT-Flatten's ~700 μs at t=256.

**Caption (verbatim):**
*Figure 15: Ablation study for KV chunk size with DEFT. t is the token tree size in speculative decoding.*

### Figure 18 (p.28) ⭐深度解读
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p28.png]]
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

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\begin{aligned} \textstyle \operatorname{SegAttn}(\mA_0, \mA_1, \mA_2)= \frac{ \mA_0 e^{\operatorname{LSE}(\mQ, \mK_0)} + \mA_1 e^{\operatorname{LSE}(\mQ, \mK_1)} + \mA_2 e^{\operatorname{LSE}(\mQ, \mK_2)} }{ e^{\operatorname{LSE}(\mQ, \mK_0)} + e^{\operatorname{LSE}(\mQ, \mK_1)} + e^{\operatorname{LSE}(\mQ, \mK_2)} } \,, \text{ where } e := \text{exp} \,. \end{aligned}
$$

## 技术点深读（DEEP）

![[deep/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference.txt`（112630 字符）供引用检索。