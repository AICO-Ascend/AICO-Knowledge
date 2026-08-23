---
paper_num: "12"
title: "Scalable Training of Mixture-of-Experts Models with Megatron Core"
authors: "Scalable Training of Mixture-of-Experts Models with Megatron Core Technical Report NVIDIA1"
date: "2026/3/8"
arxiv: "https://arxiv.org/abs/2603.07685"
pdf: "papers/scalable-training-of-mixture-of-experts-models-with-megatron-core.pdf"
slug: "scalable-training-of-mixture-of-experts-models-with-megatron-core"
tags: [moe, training]
---

# Scalable Training of Mixture-of-Experts Models with Megatron Core

> [!abstract] 摘要（原文）
> 1\. 🚀 本报告介绍了 NVIDIA Megatron-Core 框架中用于大规模混合专家模型（MoE）训练的系统级优化方案，旨在解决参数-计算不匹配带来的内存、通信和计算效率瓶颈。 2. 🛠️ 该框架通过 MoE Parallel Folding 实现多维度并行，解耦了注意力机制与 MoE 层的并行映射，并引入了 FP8/FP4 低精度训练、细粒度激活重计算及卸载等技术来应对存储压力。 3. 📈 为了提升性能，系统集成 DeepEP 和 HybridEP 优化了 Token 分发通信，并结合分组 GEMM 与算子融合等计算优化手段，显著提升了在 NVIDIA GB200 及 H100 集群上大规模 MoE 模型训练的吞吐量。

## 元信息
- **发表日期**: 2026/3/8
- **作者**: Scalable Training of Mixture-of-Experts Models with Megatron Core Technical Report NVIDIA1
- **arXiv**: https://arxiv.org/abs/2603.07685
- **本地 PDF**: `papers/scalable-training-of-mixture-of-experts-models-with-megatron-core.pdf`
- **页数**: 88

## 图表（原文 caption + 页码）

### Figure 1 (p.9) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig01.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p09.png]]*
> [!quote] caption
> Data flow through an MoE layer: Route, Dispatch, Compute, and Combine stages.

> [!tip] 技术解读（多模态）
> **Figure 1 — MoE Layer Data Flow**

The diagram depicts a four-stage forward pipeline flanked by a pre-norm on the left and a post-norm on the right, with an optional shared-expert path running along the top.

- **Route (green):** Hidden states enter the router, which produces a top-k expert assignment and routing weights.
- **Dispatch (blue):** Tokens are permuted so same-expert tokens are contiguous, then shipped to the GPUs hosting their assigned experts via AllGather, all-to-all, or Flex/DeepEP/HybridEP.
- **Compute (yellow):** Each GPU runs its local experts in a single fused Grouped GEMM.
- **Combine (blue):** Outputs are inverse-permuted and weighted-summed; shared-expert outputs (top path) are optionally merged here.

**Key takeaway:** The permutation before all-to-all communication makes per-expert work dense and contiguous, allowing many small experts to be served by one Grouped GEMM — eliminating per-expert kernel-launch overhead and keeping GPU utilization high even when individual expert loads are tiny.

**Caption (verbatim):** *Figure 1: Data flow through an MoE layer: Route, Dispatch, Compute, and Combine stages.*

### Figure 2 (p.10) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig02.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p10.png]]*
> [!quote] caption
> Router architecture: linear projection, score function, top-𝑘selection, and load balancing. combine_postprocess (backward).

> [!tip] 技术解读（多模态）
> ## Figure Description: Megatron Core MoE TopKRouter

**Architecture & Data Flow:**
The router pipeline processes tokens in four stages:

1. **Gating Layer (Linear Projection)** – Input hidden states are projected to produce logits of shape [BxS, E] (batch × sequence × experts).
2. **Score Function** – Logits pass through either Softmax or a sigmoid-based function to produce scores [BxS, E].
3. **Top-K Selection** – Selects the top-scoring experts per token.
4. **Dual Outputs** – A **Per-Token Probability** vector [BxS, E] (used as weights to combine expert outputs) and a **Boolean Routing Map** [BxS, E] (used by the dispatcher).

A separate **Load-Balancing Mechanisms** module attaches auxiliary signals: an **auxiliary-bias-free** Expert Bias, plus Z-loss/Sinkhorn regularizers and three granularities of aux-loss (micro-batch, sequence, global-batch).

**Key Technical Takeaway:** The router decouples *capacity balancing* (loss-based: Z-loss, aux-loss, Sinkhorn) from *routing behavior* (top-k selection + bias), enabling stable expert utilization without coupling balancing directly to the gating score — a design that improves scalability in large MoE training.

## Caption (verbatim)

**Figure 2:** Router architecture: linear projection, score function, top-k-selection, and load balancing.

### Figure 3 (p.13) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig03.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p13.png]]*
> [!quote] caption
> Dense Model vs MoE Model parameter/compute scaling.

> [!tip] 技术解读（多模态）
> ## Figure Description

The figure is a **log-log scatter plot** comparing LLMs on two axes:
- **X-axis:** Total Parameters (Billions), 10¹–10³
- **Y-axis:** Forward FLOPs per Token (Billions), 10¹–10³

**Components:**
- **Dense models (● circles)** — BLOOM, Cohere, Gemma, LLaMA, GPT, Qwen, Phi, Nemotron, etc.
- **MoE models (▲ triangles)** — DeepSeek-V2/V3, Mixtral, Jamba, Grok-1, Ling, Hunyuan-Large, Qwen3-MoE, etc.
- **Dashed "~2N reference line"** with shaded confidence band
- **Color-coded legend** distinguishing model families

**Data flow:** Models are positioned by (total params, FLOPs/token). Dense points hug the 2N line; MoE points fall well below it.

**Key takeaway (≤120 words):** The plot visualizes the **Parallelism Paradox of MoE**. Dense models track the 2N reference line, so adding parameters also adds proportional compute (a virtuous cycle). MoE models break this — DeepSeek-V3 carries 685B total parameters but activates only 37B (18:1 ratio), so it sits far below the 2N line at low FLOPs/token. The implication is that MoE memory grows linearly with total parameters while compute grows only with active parameters, creating communication-heavy scaling pressure on distributed training.

## Caption (verbatim)

**Figure 3:** Dense Model vs MoE Model parameter/compute scaling.

### Figure 4 (p.15) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig04.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p15.png]]*
> [!quote] caption
> Expert Parallelism (EP) distributes experts across GPUs. The all-to-all communication dispatches tokens to their assigned experts and combines results.

> [!tip] 技术解读（多模态）
> # Description of Figure 4

The figure illustrates **Expert Parallelism (EP)** for Mixture-of-Experts (MoE) layers, showing how a pool of E experts is sharded across multiple GPUs (each GPU holds E/N experts, where N is the GPU count). The data flow proceeds in three stages: (1) **Token Dispatch** via all-to-all communication — each token's routing decision (from the gating network) sends it to the GPU hosting its assigned expert; (2) **Local Expert Compute** — each GPU runs its resident experts on the gathered tokens (GEMM); and (3) **Result Combine** via a second all-to-all that returns expert outputs to the originating GPUs.

**Key technical takeaway:** EP provides two compounding benefits — (a) grouping tokens boosts arithmetic intensity, improving GEMM efficiency, and (b) the all-to-all communication volume stays **constant** as the expert count grows, since only the number of participating GPUs scales.

# Caption (Verbatim)

> **Figure 4:** Expert Parallelism (EP) distributes experts across GPUs. The all-to-all communication dispatches tokens to their assigned experts and combines results.

### Figure 5 (p.17) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig05.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p17.png]]*
> [!quote] caption
> Parallelism mappings: traditional constraints vs. MoE Parallel Folding decoupling.

> [!tip] 技术解读（多模态）
> # Figure 5 Description

## Architecture / Components / Data Flow

**Two-row layout** comparing Attention (top) and MoE Layer (bottom) parallelism across three configurations:

- **Left (DP4 → EP4):** 4 ranks process 4 sequences (Seq 1–4); attention uses full DP, MoE maps one expert (E1–E4) per rank.
- **Middle (TP2-DP2 → ETP2-EP2):** Sequences split in half; attention is tensor-parallel (1/2 Attn per rank), MoE shards experts 2-ways (1/2 E1–E4).
- **Right (TP2-CP2 → ETP2-EP1):** Single sequence; attention tensor+context parallel, MoE keeps experts whole but replicated across ranks.

**Dashed arrows:**
- *Black (Legacy Mappings):* rigid 1:1 coupling — TP/CP/DP dimensions force the MoE layer into the same partition.
- *Green (MoE Parallel Folding):* decouples MoE's EP from attention's DP, allowing experts to fold across arbitrary sub-groups (TP×CP×DP).

## Key Technical Takeaway

Traditional parallelism forces **EP ≤ DP** because MoE inherits the attention's data-parallel mesh. Parallel Folding breaks this constraint by letting EP "fold" across TP × CP × DP groups independently — e.g., with DP=8, TP=CP=2, legacy caps EP=8, but folding unlocks EP=64 (with ETP=1, EDP=1, PP=4 on 256 GPUs), enabling far higher expert counts without sacrificing attention's tensor/context parallelism.

## Caption (verbatim)

> **Figure 5: Parallelism mappings: traditional constraints vs. MoE Parallel Folding decoupling.**

### Figure 6 (p.18) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig06.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p18.png]]*
> [!quote] caption
> Parallel Folding: decoupled attention and MoE parallelism mappings.

> [!tip] 技术解读（多模态）
> ## Figure 6 Description

**Architecture/Components/Data Flow:**
Figure 6 illustrates "Parallel Folding," a technique that decouples the parallelism mappings for attention and MoE layers. The diagram contrasts two regimes: (1) a *traditional* layout where attention (TP/CP) and MoE (EP) must share one parallelism configuration, and (2) the *folded* layout where both mappings coexist within the same small group of GPUs. Within each group, tokens flow first through attention layers executed under a high TP/CP setting, then through MoE layers executed under an independent ETP=1 / high-EP setting, with all-to-all and attention collectives staying local to the NVLink-connected GPUs.

**Key Technical Takeaway (≤120 words):**
Parallel Folding lets attention and MoE layers use *different* optimal parallel strategies on the *same* GPU group. Attention keeps high TP/CP for large matmuls and long-sequence context, while MoE uses ETP=1 to retain full expert width for efficient GEMMs. Because both parallelism dimensions collapse into one GPU group, all communication stays inside the NVLink domain, GPU requirements drop from ~64 (CP=8, EP=8) to as few as 8, and each dimension can be tuned independently — removing the forced compromise at the heart of the dense-sparse mismatch.

**Caption (verbatim):**
> Figure 6: Parallel Folding: decoupled attention and MoE parallelism mappings.

### Figure 7 (p.22) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig07.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p22.png]]*
> [!quote] caption
> Memory-Efficient Permutation.

> [!tip] 技术解读（多模态）
> **Architecture / Data Flow:**
Figure 7 contrasts two MoE expert-block forward passes. The *Baseline* (left) runs the Router on full hidden states, then performs Permute → A2A + Local Permute → FC1 → SwiGLU → FC2 → Unpermute + A2A, saving many pink (backward-saved) tensors along the way. The *Memory-Efficient Permutation* (right) moves Permute *before* the Router (producing probs and routing map from permuted tokens), splits A2A into "A2A + Local Permute" and "A2A + Permute" paths, and replaces SwiGLU with a *Fused WeightedSwiGLU* that absorbs probs internally. Finally, no Unpermute save is required because the tensor is already released.

**Key takeaway:** Reordering permutation ahead of routing and folding weights into SwiGLU eliminates intermediate hidden-state checkpoints, shrinking backward-pass activation memory.

**Caption (verbatim):** *Figure 7: Memory-Efficient Permutation.*

### Figure 8 (p.23) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig08.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p23.png]]*
> [!quote] caption
> Selective Recomputation.

> [!tip] 技术解读（多模态）
> # Figure 8: Selective Recomputation (DeepSeek-V3)

## Architecture & Components

The diagram depicts a single **Transformer Layer** composed of two sub-blocks:

**MLA block (top):** LayNorm → Down_proj → Up_proj + RoPE → Core-attn → Proj Linear → bias-drop-add

**DeepSeekMoE block (bottom):** LayNorm splits into two parallel expert paths:
- **Routed Experts:** fp32 Router → probs → Token Dispatcher → Grouped FC1 → Swiglu → Grouped FC2 → Token Combiner
- **Shared Experts:** FC1 → Swiglu → FC2

Both paths merge into a final bias-drop-add.

**Color-coded legend** distinguishes recomputation targets: green (LayerNorm), blue (mla_up_proj), pink (moe_act/Swiglu), yellow (dispatch), purple (core_attn — skipped under fused_attn). Red/orange dashed boxes mark MoE vs. shared-expert scopes.

## Key Technical Takeaway (≤120 words)

Selective recomputation targets only memory-intensive yet compute-cheap operations — LayerNorm, MLA up-projection, MoE activations (Swiglu), and token dispatch — discarding their outputs after downstream consumption since they will be recomputed during backprop. By combining *granular recomputation* (fine-grained selection, <5% compute overhead) with *output-discarding recomputation* (freeing activations immediately after use, like a memory-efficient checkpoint variant), Megatron-Core MoE achieves substantial memory reduction without compromising gradient correctness — a critical enabler for training large MoE models like DeepSeek-V3 at scale.

## Caption (verbatim)

**Figure 8:** Selective Recomputation.

### Figure 9 (p.24) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig09.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p24.png]]*
> [!quote] caption
> Fine-grained activation offloading: stream overlap for forward and backward passes.

> [!tip] 技术解读（多模态）
> ## Figure Description

**Layout:** A horizontal timeline diagram split by a dashed center line into two regions — *Forward Pass* (left) and *Backward Pass* (right). Two parallel tracks run along the time axis:

- **Compute Stream (top, green):** Sequential blocks — `Forward FC1` → `Forward FC2` (forward), then `Backward FC2` → `Backward FC1` (backward).
- **D2H Stream (bottom, dark):** `Offload to CPU` block fires immediately after `Forward FC2`; `Prefetch from CPU` block fires just before `Backward FC1`.

**Data flow:** Activations produced by a forward module are streamed to CPU via a dedicated Device-to-Host copy engine, while the next compute module continues on the GPU. The shaded "Overlap" / "Latency hidden" regions show the D2H transfer running concurrently with downstream compute, so PCIe transfer cost is masked by compute time.

**Key takeaway:** Because the Copy Engine and Compute Engine are independent, offload latency is fully hidden whenever module compute time exceeds transfer time — making PCIe offloading effectively "free" and enabling fine-grained activation offloading beyond coarse layer-level schemes.

## Caption (verbatim)

**Figure 9: Fine-grained activation offloading: stream overlap for forward and backward passes.**

### Figure 10 (p.26) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig10.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p26.png]]*
> [!quote] caption
> Fine-grained offloading and recomputation: complementary memory optimization strategies. optimization target. Megatron-Core provides two techniques: precision-aware optimization that reduces storage requirements, and CPU offloading that moves inactive state off-GPU.

> [!tip] 技术解读（多模态）
> **Figure Description (≤120 words):**

The diagram depicts a transformer + MoE block split into two parallel computational paths (left: attention path; right: MoE path with Shared Experts). Each module (MLP Norm, RMSNorm, QKV Linear, Core Attn, Attn Proj, MoE Act, Expert FC1, Expert FC2, Dispatch, Combine) has an associated `output` block annotated with either `--offload-modules=<name>` (transfer activations to CPU) or `--recompute-modules=<name>` (discard & re-compute on backward). A "Discard" block marks tokens dropped after Combine.

**Key technical takeaway:** Offloading and activation recomputation are complementary, per-module strategies — offloading saves memory with zero compute cost during forward, while selective recomputation trades GPU compute for freed memory. Fine-grained tagging lets different modules in the same block adopt different policies, maximizing throughput while fitting within GPU memory budgets.

**Caption (verbatim):**

Figure 10: Fine-grained offloading and recomputation: complementary memory optimization strategies.

### Figure 11 (p.28) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig11.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p28.png]]*
> [!quote] caption
> Comparison of sharding strategies: (a) FSDP2 shards each parameter uniformly; (b) Megatron-FSDP flattens per-module and shards non-uniformly, aligning with communication buffers.

> [!tip] 技术解读（多模态）
> ## Figure Description

**Main figure (Figure 11):** Side-by-side comparison of two sharding strategies across two device ranks.

- **(a) FSDP2 uniform sharding (left):** A "(Shard, Param)-Shaped Per-Module Collective Buffer" sits at top, holding each Linear (1, 2, 3) split evenly into Rank 0 / Rank 1 sub-blocks. Below, Device Rank 0 and Device Rank 1 each receive independent copies of all three linears with matched uniform shards. Colored dashed arrows depict redundant gather/scatter flows crossing between ranks and the buffer for *every* parameter.

- **(b) Megatron-FSDP non-uniform sharding (right):** A single "Per-Module Collective Buffer (Uniformly Partitioned by DP-Shard Size)" concatenates Linear 1–3 into one contiguous strip. Device Rank 0 holds Linear 1 Rank 0 and Device Rank 1 holds Linear 1 Rank 1; shard boundaries are *non-uniform* and aligned to the buffer's flat layout, with the remaining ranks implied by the alignment.

**Key takeaway:** Non-uniform, per-module sharding aligns shard boundaries with communication buffer layouts, eliminating redundant copies and cutting communication overhead ~10% on Llama3 405B.

## Caption (verbatim)

**Figure 11:** Comparison of sharding strategies: (a) FSDP2 shards each parameter uniformly; (b) Megatron-FSDP flattens per-module and shards non-uniformly, aligning with communication buffers.

### Figure 12 (p.28) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig12.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p28.png]]*
> [!quote] caption
> Persistent double-buffer design: two pre-allocated buffers are cycled across FSDP collectives, eliminating allocation overhead and enabling NCCL User Buffer Registration.

> [!tip] 技术解读（多模态）
> ## Figure Description

**Main figure (Figure 11):** Side-by-side comparison of two sharding strategies across two device ranks.

- **(a) FSDP2 uniform sharding (left):** A "(Shard, Param)-Shaped Per-Module Collective Buffer" sits at top, holding each Linear (1, 2, 3) split evenly into Rank 0 / Rank 1 sub-blocks. Below, Device Rank 0 and Device Rank 1 each receive independent copies of all three linears with matched uniform shards. Colored dashed arrows depict redundant gather/scatter flows crossing between ranks and the buffer for *every* parameter.

- **(b) Megatron-FSDP non-uniform sharding (right):** A single "Per-Module Collective Buffer (Uniformly Partitioned by DP-Shard Size)" concatenates Linear 1–3 into one contiguous strip. Device Rank 0 holds Linear 1 Rank 0 and Device Rank 1 holds Linear 1 Rank 1; shard boundaries are *non-uniform* and aligned to the buffer's flat layout, with the remaining ranks implied by the alignment.

**Key takeaway:** Non-uniform, per-module sharding aligns shard boundaries with communication buffer layouts, eliminating redundant copies and cutting communication overhead ~10% on Llama3 405B.

## Caption (verbatim)

**Figure 11:** Comparison of sharding strategies: (a) FSDP2 shards each parameter uniformly; (b) Megatron-FSDP flattens per-module and shards non-uniformly, aligning with communication buffers.

### Figure 13 (p.30) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig13.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p30.png]]*
> [!quote] caption
> Expert parallelism across 4 GPUs with 4 experts.

> [!tip] 技术解读（多模态）
> # Figure 13 Description

## Architecture & Data Flow
Figure 13 depicts **Expert Parallelism (EP) across 4 GPUs, each hosting 1 expert**. The diagram illustrates the standard EP communication anatomy with two main collective operations per MoE layer:

1. **Dispatch phase** (all-to-all scatter): Tokens on each GPU are routed to their assigned experts across all 4 GPUs based on the router's expert assignments.
2. **Combine phase** (all-to-all gather): Expert outputs are returned to the original token-owning ranks.

The figure shows bidirectional communication arrows between every pair of GPUs (a fully connected all-to-all topology), where tokens traveling from rank *i* to rank *j* carry the hidden-dimension activations for tokens assigned to expert *j*.

## Key Technical Takeaway
Standard NCCL all-to-all underutilizes bandwidth for fine-grained MoE workloads, so optimized dispatchers (DeepEP, HybridEP) use fused kernels and hardware primitives to approach peak bandwidth while overlapping communication with computation from adjacent microbatches to hide latency.

## Caption (verbatim)
**Figure 13: Expert parallelism across 4 GPUs with 4 experts.**

### Figure 14 (p.31) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig14.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p31.png]]*
> [!quote] caption
> The dispatch kernel design of HybridEP.

> [!tip] 技术解读（多模态）
> **Note:** The figure graphic itself is not visible in the provided image (only its caption and surrounding text appear). The description below is reconstructed from the figure caption and the in-text architecture description.

**Architecture / Data Flow (Figure 14):**
The HybridEP dispatch kernel moves tokens from global memory into shared memory using routing information, then pushes them to destinations through a FIFO queue. In the inter-node path, an RDMA warp group first exchanges data between GPUs that share the same local index across nodes, after which the data is forwarded internally within each node.

**Key Technical Takeaway:**
By using an RDMA warp group to perform a same-index cross-node exchange *before* intra-node forwarding, HybridEP overlaps inter-node and intra-node transfers and avoids sending duplicated payloads directly through the network interface—reducing cross-node traffic versus naive all-to-all.

**Caption (verbatim):**
Figure 14: The dispatch kernel design of HybridEP.

### Figure 15 (p.31) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig15.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p31.png]]*
> [!quote] caption
> The combine kernel design of HybridEP.

> [!tip] 技术解读（多模态）
> **Note:** The figure graphic itself is not visible in the provided image (only its caption and surrounding text appear). The description below is reconstructed from the figure caption and the in-text architecture description.

**Architecture / Data Flow (Figure 14):**
The HybridEP dispatch kernel moves tokens from global memory into shared memory using routing information, then pushes them to destinations through a FIFO queue. In the inter-node path, an RDMA warp group first exchanges data between GPUs that share the same local index across nodes, after which the data is forwarded internally within each node.

**Key Technical Takeaway:**
By using an RDMA warp group to perform a same-index cross-node exchange *before* intra-node forwarding, HybridEP overlaps inter-node and intra-node transfers and avoids sending duplicated payloads directly through the network interface—reducing cross-node traffic versus naive all-to-all.

**Caption (verbatim):**
Figure 14: The dispatch kernel design of HybridEP.

### Figure 16 (p.32) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig16.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p32.png]]*
> [!quote] caption
> Merged FWD-FWD Timeline with all-to-all Overlapping.

> [!tip] 技术解读（多模态）
> ## Figure Description (Figure 16)

**Architecture/Components & Data Flow:**
The figure depicts a **timeline-style pipeline schedule** for the *Merged FWD-FWD* overlap strategy in a 1F1B pipeline-parallel scheme. Horizontally laid-out swim lanes typically represent:
- **Two adjacent micro-batches (MB 0 and MB 1)** running forward passes in parallel
- **Stages** along the vertical axis (pipeline stages across devices)
- **Two interleaved kernel streams per stage:** a compute stream (FWD pass: Attention → MLP → EP all-to-all dispatch/combine) and a communication stream (all-to-all over NVLink/IB)

Each MB0 and MB1 block executes its forward pass simultaneously; their **EP all-to-all dispatch/combine kernels are issued on a separate CUDA stream** so they overlap with the other micro-batch's GEMM compute, effectively hiding cross-node EP latency behind parallel computation.

**Key Technical Takeaway (≤120 words):**
Merging two forward passes doubles peak activation memory (2× overhead) and offers limited all-to-all hiding because forward compute is only ~half the cost of backward compute — leaving slack where communication cannot be fully overlapped. This motivates the preferred **Merged FWD-BWD (DualPipe-equivalent)** scheme, which pairs a forward pass of one micro-batch with a backward pass of another, exploiting the roughly 2× compute asymmetry to more thoroughly hide EP all-to-all behind useful GEMM work without increasing activation memory.

## Caption (Verbatim Transcription)

**Figure 16:** Merged FWD-FWD Timeline with all-to-all Overlapping.

### Figure 17 (p.33) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig17.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p33.png]]*
> [!quote] caption
> Merged FWD-BWD Timeline with all-to-all Overlapping.

> [!tip] 技术解读（多模态）
> **Figure 17 — Description**

Figure 17 depicts a **merged FWD-BWD timeline** (one forward and the backward of micro-batch 0) plotted on a time axis, with two operation tracks:
- **Compute track (lower)**: sequential forward (F) and backward (B) blocks for adjacent micro-batches.
- **Communication track (upper)**: all-to-all (expert-parallel dispatch/combine) operations issued between forward/backward stages.

The arrow flow shows **F → all-to-all → B → all-to-all → F**, where all-to-all communication is *interleaved* with subsequent compute so the dispatch/combine overlaps the next forward's attention/MLP, hiding EP latency behind useful work.

**Key technical takeaway (≤120 words):**
Merged FWD-BWD overlaps all-to-all communication with compute using two CUDA streams (Compute Stream for fwd/bwd, Comm Stream for token dispatch/combine), plus a W/D split that separates weight-gradient (W/mlp) from data-gradient (D/mlp) computation to break the dependency that normally forces B/dispatch to wait on B/mlp. This lets B/dispatch overlap with F/mlp, dramatically reducing idle time. Combined with stream separation and the W/D split, the EP communication overhead drops from **30–40% (after DeepEP) to under 5% of iteration time** in DeepSeek-V3 training on H100, with no extra activation memory.

**Caption (verbatim):**
> Figure 17: Merged FWD-BWD Timeline with all-to-all Overlapping.

### Figure 18 (p.34) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig18.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p34.png]]*
> [!quote] caption
> EP all-to-all communication overlap strategies: baseline vs. 1F1B with W/D split.

> [!tip] 技术解读（多模态）
> **Description:**
The figure (whose image area appears blank in this rendering) compares two Expert-Parallelism all-to-all communication overlap strategies side-by-side: a **baseline** pipeline schedule versus an optimized **1F1B with Warmup/Decay (W/D) split** schedule. The diagram would show a pipeline of micro-batches with timeline bars representing GEMM compute and all-to-all communication across pipeline stages, illustrating how 1F1B scheduling overlaps expert-dispatch/reduce collectives with neighboring micro-batches' matrix multiplications — particularly during the warmup (W) and decay (D) phases — to hide latency.

**Key takeaway:** Restructuring pipeline scheduling into a 1F1B W/D split enables deeper communication–compute overlap than the naive baseline, which is critical for fine-grained MoE models where all-to-all otherwise dominates iteration time.

**Caption (verbatim):**
> Figure 18: EP all-to-all communication overlap strategies: baseline vs. 1F1B with W/D split.

### Figure 19 (p.35) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig19.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p35.png]]*
> [!quote] caption
> Interleaved PP Timeline with all-to-all Overlapping.

> [!tip] 技术解读（多模态）
> I'm unable to fully complete this task as requested because **the actual figure visualization (Figure 19) is not rendered/visible in the provided image** — only its caption and surrounding section text appear. The upper portion of the page where the timeline diagram should be displayed is blank. Without seeing the diagram itself, I cannot accurately describe its specific architecture, components, or data flow, since fabricating those details would be unreliable.

What I can transcribe verbatim is the caption:

**Caption (verbatim):**
> "Figure 19: Interleaved PP Timeline with all-to-all Overlapping."

**Contextual clues from the surrounding text** (Section 4.3 "Breaking the Compute Efficiency Wall") suggest the figure depicts a pipeline-parallel (PP) execution timeline showing how all-to-all communication operations (used in MoE token dispatching) are overlapped with pipeline stages to hide communication latency — a key technique for hiding expert-routing communication behind compute. But I cannot confirm the specific layout, axes, or components shown without the actual figure being visible.

If you can re-share the image with the figure rendered, or provide the figure on a separate page, I'd be glad to give a precise description of its architecture/components/data flow and the key technical takeaway.

### Figure 20 (p.37) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig20.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p37.png]]*
> [!quote] caption
> The pipeline for permute fusion in the training process. • Preprocessing: Permutation is fundamentally a data transfer process that requires tokens to be stored consecutively in the buffer corresponding to each expert. The purpose of the preprocessing step is to generate an offset map (Row ID map in figure 20), which indicates the offset of each token in the input and output buffers. This ensures 

> [!tip] 技术解读（多模态）
> **Figure 20 — Description**

The figure is not visually rendered in the provided page (only its caption appears); based on the surrounding text, the diagram depicts the **permute fusion pipeline** used in MoE training, organized as a left-to-right data-flow with three sequential stages:

1. **Preprocessing** — Generates a *Row ID map* (offset table) describing where each token sits in the input/output buffers; runs once per forward pass and is reused.
2. **Permute** — A memory-transfer kernel that scatters tokens from the input buffer into the per-expert buffer using the offset map, then feeds them into the expert MLP. In the memory-efficient variant, the routing probabilities are permuted alongside the tokens.
3. **Unpermute / Combine** — The inverse operation that gathers token contributions back to their original positions; a copy-and-sum step (probability-weighted in the non-memory-efficient path, plain sum in the memory-efficient path), with accumulation done in **FP32**.

**Key technical takeaway:** Fusing permute into a single GPU kernel avoids the many small-kernel launches and CPU-side overhead of native PyTorch scatter/gather operations — critical at MoE scale, where permutation is fundamentally a data-movement bottleneck rather than compute.

**Caption (verbatim):**
*"Figure 20: The pipeline for permute fusion in the training process."*

### Figure 21 (p.38) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig21.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p38.png]]*
> [!quote] caption
> The workflow of the router fusion. • Computation of MoE auxiliary loss: Building on step 2, the auxiliary loss computation is fused into a single kernel.

> [!tip] 技术解读（多模态）
> **Description of Figure 21:**

The figure area on the page appears blank/unrendered in the visible scan, with only the caption "Figure 21: The workflow of the router fusion." present beneath an empty space. Based on the caption and surrounding context, the intended figure illustrates the **router fusion workflow** within the MoE (Mixture-of-Experts) router module, depicting how the gating/routing computation — including auxiliary loss computation (step 3, "Computation of MoE auxiliary loss") — is fused into a single optimized kernel rather than being executed as separate operations. The workflow likely shows the sequential pipeline: token input → router/gating score computation → top-k expert selection → fused auxiliary loss → output dispatch tokens, highlighting how kernel fusion consolidates these steps to reduce launch overhead and memory traffic. **Key takeaway:** Router fusion collapses multiple router sub-operations (gating, top-k selection, load-balancing loss) into one kernel, eliminating intermediate memory round-trips and reducing per-iteration latency in fine-grained MoE training. Future work notes communication may also be folded into the fusion scope.

**Caption verbatim:**

Figure 21: The workflow of the router fusion.

### Figure 22 (p.39) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig22.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p39.png]]*
> [!quote] caption
> Traditional execution (top) versus CUDA Graph execution (bottom).

> [!tip] 技术解读（多模态）
> # Main Figure (Figure 23): Description

**Architecture / Components:**
- **Left panel — Full CUDA Graph**: A single captured graph wraps the entire forward-backward pass across all three layers and both microbatches as one monolithic replayable unit. Requires static, pre-determined shapes (hence only compatible with token-dropping-with-padding).
- **Right panel — Layer-wise CUDA Graphs**: The iteration is decomposed into per-layer sub-graphs (one per layer × microbatch). Each block contains its own captured kernel sequence, reducing per-replay scope so dynamic MoE token counts can be tolerated at layer boundaries.

**Data flow (both panels):**
Tokens → Layer 1 (microbatch A, microbatch B) → Layer 2 (A, B) → Layer 3 (A, B) → Loss / backward, with GPU timelines showing kernel execution lanes and CPU launch gaps.

---

# Key Technical Takeaway (≈70 words)

CUDA Graphs capture a workload into a single replayable graph, eliminating per-op Python/framework and kernel-launch CPU overhead — but they require **static, predetermined shapes**, which conflicts with MoE's dynamically varying per-expert token counts. Megatron-Core resolves this with **two modes**: a *full* graph for dense/padded MoE (maximum host-overhead hiding) and a *layer-wise* graph that tolerates shape changes between layers (better for fine-grained MoE).

---

# Caption (verbatim)

> Figure 23: Full versus layer-wise CUDA Graphs in one training iteration (three layers, two microbatches).

### Figure 23 (p.39) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig23.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p39.png]]*
> [!quote] caption
> Full versus layer-wise CUDA Graphs in one training iteration (three layers, two microbatches).

> [!tip] 技术解读（多模态）
> # Main Figure (Figure 23): Description

**Architecture / Components:**
- **Left panel — Full CUDA Graph**: A single captured graph wraps the entire forward-backward pass across all three layers and both microbatches as one monolithic replayable unit. Requires static, pre-determined shapes (hence only compatible with token-dropping-with-padding).
- **Right panel — Layer-wise CUDA Graphs**: The iteration is decomposed into per-layer sub-graphs (one per layer × microbatch). Each block contains its own captured kernel sequence, reducing per-replay scope so dynamic MoE token counts can be tolerated at layer boundaries.

**Data flow (both panels):**
Tokens → Layer 1 (microbatch A, microbatch B) → Layer 2 (A, B) → Layer 3 (A, B) → Loss / backward, with GPU timelines showing kernel execution lanes and CPU launch gaps.

---

# Key Technical Takeaway (≈70 words)

CUDA Graphs capture a workload into a single replayable graph, eliminating per-op Python/framework and kernel-launch CPU overhead — but they require **static, predetermined shapes**, which conflicts with MoE's dynamically varying per-expert token counts. Megatron-Core resolves this with **two modes**: a *full* graph for dense/padded MoE (maximum host-overhead hiding) and a *layer-wise* graph that tolerates shape changes between layers (better for fine-grained MoE).

---

# Caption (verbatim)

> Figure 23: Full versus layer-wise CUDA Graphs in one training iteration (three layers, two microbatches).

### Figure 24 (p.40) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig24.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p40.png]]*
> [!quote] caption
> Partial CUDA Graphs capture static components (attention, shared experts, router, preprocessing) while leaving dynamic expert computation outside the graph.

> [!tip] 技术解读（多模态）
> **Note:** The figure image is not rendered/visible on this page—only the caption and surrounding text appear. Based on the caption and surrounding discussion, here is a description:

**Architecture / Components / Data Flow**
The figure (Figure 24) illustrates a **Partial CUDA Graph** approach for dropless MoE transformer layers. Per-layer graphs are captured that include only **static-shape components**: attention layers (fixed token count), router computation (fixed I/O shapes), Expert Parallelism (EP) preprocessing (static permutation metadata), shared experts (if present), and dense-block MLPs. The **dynamic routed-expert GEMM computation** is left outside the graph, since per-expert token counts vary each iteration. Input tokens flow through the static subgraph → dynamic expert dispatch → expert compute (ungraphed) → output recombination.

**Key Takeaway**
Partial CUDA Graphs sidestep the static-shape constraint of full CUDA Graphs in dropless MoE by graphing everything *except* the per-expert dynamic GEMM, still capturing the bulk of CPU overhead reduction without needing device-host synchronization.

**Caption (verbatim)**
Figure 24: Partial CUDA Graphs capture static components (attention, shared experts, router, preprocessing) while leaving dynamic expert computation outside the graph.

### Figure 25 (p.41) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig25.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p41.png]]*
> [!quote] caption
> Transformer layer forward pass: without (upper) and with (lower) partial CUDA Graphs. CPU overhead is largely eliminated for static components.

> [!tip] 技术解读（多模态）
> **Figure 25 — Transformer Layer Forward Pass: Without (Upper) vs. With (Lower) Partial CUDA Graphs**

**Architecture / Data Flow (inferred from caption & surrounding text):**
Each panel shows the per-layer timeline of a Mixture-of-Experts transformer block executed on a GPU stream. Operations are split into:
- *Static segments* (grappable): input-norm → **attn** → residual → **MoE router** (projection + top-k + aux-loss) → **EP pre-process** (token-metadata & permutation) → shared expert.
- *Dynamic segments* (eager): **token dispatch** → **Expert GEMMs** (variable M) → **token combine** → output projection → next layer.

In the *upper* (no-graphs) panel, a CPU-launch gap appears between every kernel, so static operations still pay per-op host overhead. In the *lower* (partial-graphs) panel, the `attn + moe_router + moe_preprocess` scopes are fused into a single captured graph — those host gaps collapse — while dispatch/combine/expert-GEMM remain eager (and thus still show overhead, since shapes are dynamic).

**Key technical takeaway (≤120 words):**
By partitioning each MoE layer into static "scopes" (attn + router + EP preprocessing) and capturing *only* those scopes in CUDA Graphs, Megatron-Core eliminates per-kernel CPU launch overhead for the bulk of the layer while leaving the data-dependent expert path (dispatch / variable-M GEMMs / combine) in eager mode. The result is near-graph speed without giving up correctness under dynamic token routing — the residual CPU cost is confined to the narrow dispatch↔combine window.

**Caption (verbatim):**
*Figure 25: Transformer layer forward pass: without (upper) and with (lower) partial CUDA Graphs. CPU overhead is largely eliminated for static components.*

### Figure 26 (p.42) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig26.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p42.png]]*
> [!quote] caption
> Why Pipeline Parallelism prevents CUDA Graphs from being shared across microbatches. With PP (top): Execution is interleaved—multiple forward passes run before any backward pass. If microbatches share a graph, F_mb1 overwrites saved context of F_mb0 before B_mb0 uses it, causing memory corruption. Each microbatch needs its own graph (𝐿× 𝑀× 2 graphs total). Without PP (bottom): Execution is sequent

> [!tip] 技术解读（多模态）
> ## Figure 26 Description

**Components & Layout:** A two-panel comparative diagram contrasting CUDA Graph sharing under pipeline parallelism (PP) vs. non-PP execution, with two GPU columns (likely representing microbatches 0 and 1, i.e., F_mb0/B_mb0 and F_mb1/B_mb1) and a shared memory region for saved forward context.

**Top panel — With PP (interleaved):** Timeline runs left-to-right showing `F_mb0 → F_mb1 → B_mb0 → B_mb1`. The shared saved-context buffer is overwritten by F_mb1 *before* B_mb0 reads it, producing a memory-corruption hazard. Workaround: capture one distinct graph per microbatch ⇒ **L·M·2 graphs**.

**Bottom panel — Without PP (sequential):** Timeline runs `F_mb0 → B_mb0 → F_mb1 → B_mb1`. Each microbatch fully drains forward+backward before the next forward begins, so context is consumed safely. Microbatches can share graphs ⇒ **L·2 graphs**.

**Key takeaway:** Graph sharing across microbatches is *only* safe when backward passes complete before subsequent forward passes touch shared saved tensors — interleaved PP scheduling breaks this invariant, inflating graph count by a factor of M.

---

## Verbatim Caption

> **Figure 26:** Why Pipeline Parallelism prevents CUDA Graphs from being shared across microbatches. **With PP** (top): Execution is interleaved—multiple forward passes run before any backward pass. If microbatches share a graph, F_mb1 overwrites saved context of F_mb0 before B_mb0 uses it, causing memory corruption. Each microbatch needs its own graph (L·M·2 graphs total). **Without PP** (bottom): Execution is sequential—each microbatch completes (forward+backward) before the next starts. Context is consumed before being overwritten, so microbatches can safely share graphs (only L·2 graphs total).

### Figure 27 (p.45) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig27.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p45.png]]*
> [!quote] caption
> ECHO workflow for forward and backward passes. The planner generates routing and hot expert maps. Expert Dispatch clones hot expert weights to spare slots; Expert Gradient Dispatch reduces gradients back to home experts.

> [!tip] 技术解读（多模态）
> ## Figure 27 Description

**Note:** The figure image area appears blank/empty in the rendered page, so the description is reconstructed from the caption and surrounding text.

**Architecture / Components / Data Flow**

The diagram illustrates the ECHO workflow spanning forward and backward passes:

1. **Planner** — generates per-step *routing maps* and identifies *hot experts* (heavily-trafficked experts that cause load imbalance).
2. **Forward pass** — **Expert Dispatch** clones the weights of these hot experts into under-utilized spare slots on other ranks, so incoming tokens can be routed to replicated copies.
3. **Backward pass** — **Expert Gradient Dispatch** gathers/scatters gradients computed on the cloned replicas and reduces them back to the original "home" experts to keep parameters synchronized.

**Key technical takeaway**
ECHO turns worst-case expert load into near-typical load by cloning only the hot experts each step rather than replicating every expert, reducing peak memory and communication while preserving training correctness through gradient reduction.

## Caption (verbatim)

> **Figure 27:** ECHO workflow for forward and backward passes. The planner generates routing and hot expert maps. Expert Dispatch clones hot expert weights to spare slots; Expert Gradient Dispatch reduces gradients back to home experts.

### Figure 28 (p.46) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig28.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p46.png]]*
> [!quote] caption
> Memory layout comparison across three execution modes. Left: Eager mode allocates memory dynamically based on actual usage. Middle: Baseline static shape requires worst-case sized buffers for each layer independently, causing severe fragmentation when actual usage is lower. Right: Paged Stashing uses a single worst-case tmp buffer shared across layers for computation, while a paged stashing buffer

> [!tip] 技术解读（多模态）
> ## Figure 28 — Memory Layout Comparison Across Three Execution Modes

**Architecture / Components (three side-by-side panels):**
- **Left (Eager mode):** Memory allocated dynamically per-layer based on actual runtime usage — no over-allocation, but allocation overhead per layer.
- **Middle (Static-shape baseline):** Each layer independently reserves a worst-case-sized buffer; layers with sparse token usage leave large unused gaps (severe fragmentation).
- **Right (Paged Stashing):** A single shared worst-case *tmp buffer* holds current-layer computation, while a separate *paged stashing buffer* stores only the actually-used tokens in fixed-size pages (default 64 tokens/page), eliminating fragmentation.

**Data flow:** activations → tmp buffer (compute) → paged stash pages → reload on backward → returned to free list.

**Key technical takeaway:** Paged Stashing decouples worst-case compute memory from actual activation storage via OS-style paging, drastically lowering footprint compared to static worst-case allocation while keeping a single shared computation buffer for efficiency.

## Verbatim Caption

**Figure 28:** Memory layout comparison across three execution modes. **Left:** Eager mode allocates memory dynamically based on actual usage. **Middle:** Baseline static shape requires worst-case sized buffers for each layer independently, causing severe fragmentation when actual usage is lower. **Right**: Paged Stashing uses a single worst-case tmp buffer shared across layers for computation, while a paged stashing buffer stores only the actual tokens, significantly reducing total memory footprint.

### Figure 29 (p.46) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig29.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p46.png]]*
> [!quote] caption
> Paged Stashing stream overlap. Forward pass: After Layer N computes, its activations are stashed (copied from tmp buffer to paged stashing buffer) on a dedicated Pack stream while Layer N+1 computes on the main Compute stream—the stash is completely overlapped. Backward pass: Activations for Layer N are pre-fetched (reloaded from stashing buffer to tmp buffer) on the Unpack stream before Layer N b

> [!tip] 技术解读（多模态）
> ## Figure 28 — Memory Layout Comparison Across Three Execution Modes

**Architecture / Components (three side-by-side panels):**
- **Left (Eager mode):** Memory allocated dynamically per-layer based on actual runtime usage — no over-allocation, but allocation overhead per layer.
- **Middle (Static-shape baseline):** Each layer independently reserves a worst-case-sized buffer; layers with sparse token usage leave large unused gaps (severe fragmentation).
- **Right (Paged Stashing):** A single shared worst-case *tmp buffer* holds current-layer computation, while a separate *paged stashing buffer* stores only the actually-used tokens in fixed-size pages (default 64 tokens/page), eliminating fragmentation.

**Data flow:** activations → tmp buffer (compute) → paged stash pages → reload on backward → returned to free list.

**Key technical takeaway:** Paged Stashing decouples worst-case compute memory from actual activation storage via OS-style paging, drastically lowering footprint compared to static worst-case allocation while keeping a single shared computation buffer for efficiency.

## Verbatim Caption

**Figure 28:** Memory layout comparison across three execution modes. **Left:** Eager mode allocates memory dynamically based on actual usage. **Middle:** Baseline static shape requires worst-case sized buffers for each layer independently, causing severe fragmentation when actual usage is lower. **Right**: Paged Stashing uses a single worst-case tmp buffer shared across layers for computation, while a paged stashing buffer stores only the actual tokens, significantly reducing total memory footprint.

### Figure 30 (p.50) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig30.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p50.png]]*
> [!quote] caption
> FP8 training recipes: Per-Tensor Scaling, Blockwise FP8, and MXFP8. A reduced-precision training recipe consists of: • Data format. There are two types of FP8 format: E4M3 and E5M2 [71, 74]. Usually there are two combinations used in training: ∘E4M3: Inputs, weights, and gradients are all quantized in the E4M3 format. ∘Hybrid: Inputs and weights are quantized in E4M3, while gradients are quantized

> [!tip] 技术解读（多模态）
> ## Description of Figure 30

**Architecture/Components:** The figure visually compares three FP8 quantization scaling schemes applied to a 2D weight/activation tensor (depicted as a colored matrix, likely with red/blue halves for E4M3 and E5M2):

1. **Per-Tensor Scaling** — a single FP32 scale factor (`amax`-derived) is applied to the entire tensor, shown as one global scalar.
2. **Blockwise FP8** — the tensor is partitioned into user-defined groups/tiles (e.g., 1×128, 128×128), each with its own FP32 scale.
3. **MXFP8** — the tensor is partitioned into fixed 32-element micro-blocks along the reduction dimension, each paired with an E8M0 (power-of-two) scale, aligned with NVIDIA's microscaling spec.

Arrows/data flow: raw tensor → `amax` reduction → per-scheme scale generation → quantized FP8 outputs → (optional) backward gradient path. E4M3 vs E5M2 typically indicated for weights/activations vs gradients.

**Key Takeaway (≤120 words):** Fine-grained scaling granularity (per-tensor → block → 32-element MX block) tightens the dynamic-range representation, improving numerical accuracy at the cost of more scale metadata and quantization compute. Per-tensor is cheapest but least accurate; blockwise balances overhead and accuracy; MXFP8 standardizes micro-block sizing to be hardware-friendly on Blackwell tensor cores. Choosing a recipe is therefore a per-tensor vs block-level trade-off between quantization-error convergence and CPU/GPU overhead in the training pipeline.

## Caption (verbatim)

**Figure 30: FP8 training recipes: Per-Tensor Scaling, Blockwise FP8, and MXFP8.**

### Figure 31 (p.52) ⭐深度解读
![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p52.png]]
> [!quote] caption
> The computation of a linear layer with various FP8 recipes. Note the differences in quantization granularity and tensor layout requirements across platforms. precise due to the finer-grained scaling granularity, and has better performance due to the native support of MXFP8 in the Tensor Core. Therefore, MXFP8 is the default FP8 recipe on the Blackwell platform.

> [!tip] 技术解读（多模态）
> ## Figure 31 Description

The figure presents a 2×2 grid comparing FP8 linear-layer computation recipes across NVIDIA GPU platforms (Hopper vs. Blackwell).

**Components/panels:**
- **(a) Per-tensor Current scaling on Hopper** — single FP32 scale applied to the entire tensor before FP8 quantization.
- **(b) Per-tensor Current scaling on Blackwell** — same per-tensor scaling, but adapted to Blackwell's tensor-core layout (added column-wise quantized FP8 buffers for activations/weights).
- **(c) Blockwise FP8 on Hopper** — finer-grained, block-level FP8 scales to mitigate quantization error, with row-major layout.
- **(d) MXFP8 on Blackwell** — microscaling (MX) block-quantized FP8 (e.g., E4M3 with per-block E8M0 scales), natively accelerated by Blackwell Tensor Cores, with column-major storage of both FP8 values and scales.

**Key technical takeaway:** Blackwell's native MXFP8 hardware support enables finer block-level quantization than Hopper's blockwise FP8, but imposes additional column-wise storage for activations and weights — making MXFP8 the default Blackwell recipe.

## Caption (verbatim)

> **Figure 31:** The computation of a linear layer with various FP8 recipes. Note the differences in quantization granularity and tensor layout requirements across platforms.

### Figure 32 (p.53) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig32.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p53.png]]*
> [!quote] caption
> FP8 primary weight quantization scheme for blockwise scaling.

> [!tip] 技术解读（多模态）
> **Figure 32 Description:**

The figure illustrates the **FP8 primary weight quantization scheme with blockwise scaling**. It depicts the data flow from FP32 master weights (top) being partitioned into small blocks (e.g., 1×16 or 16×16 tiles), with each block independently computing its amax (absolute maximum) from the FP32 tensor, deriving a per-block FP32 scale factor, and quantizing the values to FP8 (E4M3 or E5M2) format. Arrows show the per-block scaling factor being retained in FP32 alongside the FP8 quantized values.

**Key Technical Takeaway:**
Blockwise scaling enables finer-grained quantization granularity than tensor-level or row-wise scaling — each block gets its own FP32 amax-derived scale factor, which dramatically reduces quantization error for outlier-prone weight matrices. Crucially, the FP32 block scale is preserved (not quantized) so that forward/backward passes share consistent scales, eliminating forward–backward quantization mismatch during training.

**Verbatim Caption:**
"Figure 32: FP8 primary weight quantization scheme for blockwise scaling."

### Figure 33 (p.54) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig33.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p54.png]]*
> [!quote] caption
> FP8 primary weight quantization scheme for delayed scaling and per-tensor current scaling.

> [!tip] 技术解读（多模态）
> ## Figure Description

The figure (which appears as a large blank area in the rendered page, with only the Step 3 bullet and caption visible) illustrates the **FP8 primary weight quantization pipeline** using a delayed-scaling strategy with per-tensor current scaling. Based on the surrounding context, the diagram depicts a multi-stage data flow:

- **Step 1 (inferred):** Maintain high-precision (master) FP32/FP16 weights.
- **Step 2 (inferred):** Compute a *global* abs-max reduction across the full tensor and quantize the master weights to FP8 using that single scaling factor (delayed scaling = scale applied separately from cast, not embedded per-block).
- **Step 3 (visible bullet):** Perform a **partial cast** — using the global abs-max together with master weights to cast only the required slice to FP8, leaving other slices in higher precision until needed.

**Key technical takeaway:** By using *delayed* per-tensor scaling rather than blockwise embedded scales, the scheme avoids per-block reduction kernels, enables efficient partial casting, and shrinks the AllGather communication volume for distributed training. (108 words)

## Caption (verbatim)

**Figure 33: FP8 primary weight quantization scheme for delayed scaling and per-tensor current scaling.**

### Figure 34 (p.57) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig34.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p57.png]]*
> [!quote] caption
> SDPA exhibits 𝑂(𝑠2) complexity, while MoE and the remaining attention operations exhibit 𝑂(𝑠) complexity. Therefore, SDPA dominates the computation at longer sequence lengths.

> [!tip] 技术解读（多模态）
> **Figure 34 — SDPA vs. MoE Complexity**

**Architecture / Components / Data Flow:**
The figure visually contrasts the computational cost scaling of two operation types as sequence length (n) increases on the x-axis:
- **MoE / remaining attention ops:** a straight line following **Θ(n)** linear scaling.
- **SDPA (Scaled Dot-Product Attention):** a steeply rising curve following **Θ(n²)** quadratic scaling.

The two curves intersect at a crossover region beyond typical 4K–8K training lengths; from that point onward, the SDPA curve overtakes and dwarfs the MoE line, illustrating that attention — not expert routing/MLPs — becomes the dominant FLOP consumer at long contexts (e.g., 16K, 64K).

**Key Technical Takeaway (≤120 words):**
SDPA scales quadratically (Θ(n²)) in sequence length while MoE and other attention operations scale only linearly (Θ(n)), so at long contexts SDPA dominates compute. At 64K tokens SDPA alone consumes ~69 % of FLOPs versus 10–15 % at short sequences. Because cuDNN/FlashAttention already optimizes SDPA heavily, this compute shift is not a new bottleneck; the practical wall becomes memory and communication. Optimizations must therefore target those two walls without introducing overhead that would erode long-context training throughput.

**Caption (verbatim):**
> Figure 34: SDPA exhibits Θ(n²) complexity, while MoE and the remaining attention operations exhibit Θ(n) complexity. Therefore, SDPA dominates the computation at longer sequence lengths.

### Figure 35 (p.59) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig35.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p59.png]]*
> [!quote] caption
> Communication and computation patterns of TP and two types of CP.

> [!tip] 技术解读（多模态）
> # Figure 35 Description

**Note:** The figure image itself is not rendered on the provided page — only the caption and surrounding text are visible. Based on the textual context, the figure would depict three parallel/distributed execution patterns side-by-side:

**Architecture / Components:**
- **TP (Tensor Parallelism):** Shards linear weights; requires extra collectives in linear layers; SDPA runs on head-sharded tensors.
- **P2P CP (Peer-to-Peer Context Parallelism):** Exchanges KV cache in a ring-style pattern within the CP group; communication overlaps with SDPA computation; tensors remain sequence-sharded.
- **All-to-all CP:** Performs sequence↔head resharding before and after SDPA; avoids the multi-step ring exchange but requires reshape collectives.

**Data Flow:** Input → (optional all-to-all reshape) → SDPA on sharded tensors → KV exchange / weight collectives → output reshape.

**Key Technical Takeaway:** TP is best within a node (fast comms, parameter memory savings); P2P CP excels across nodes (overlaps comms with compute); Megatron-Core's **hierarchical CP** composes them — e.g., all-to-all CP + TP inside a node for SDPA efficiency, P2P CP across nodes to preserve comm-compute overlap.

**Caption (verbatim):**
> *Figure 35: Communication and computation patterns of TP and two types of CP.*

### Figure 36 (p.61) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig36.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p61.png]]*
> [!quote] caption
> Unpacked vs. Packed sequences.

> [!tip] 技术解读（多模态）
> **Description of Figure 38 (main figure):**

The figure illustrates three sub-panels comparing partitioning strategies for three packed sequences (orange, blue, green) on two GPUs:

- **(a) Input sequences:** Three sequences of varying length are packed together into microbatches. The orange sequence is long enough to require splitting; the blue and green sequences each fit on a single GPU.
- **(b) Standard CP2 (DP=1, CP=2):** A fixed context-parallel degree of 2 forces *all* sequences in every microbatch to be split across the two GPUs. The blue and green sequences are unnecessarily partitioned despite fitting on one device.
- **(c) Dynamic-CP:** The CP degree is chosen per-sequence at runtime. The orange sequence still uses CP=2 in microbatch-0, but blue and green each run independently with CP=1 in microbatch-1, eliminating wasteful splits.

**Key technical takeaway:** Dynamic-CP enables per-microbatch context-parallel resizing as a lightweight runtime decision that changes only token-slice partitioning and CP communication groups — avoiding any parameter/optimizer-state redistribution, and so eliminating the compute imbalance that rigid CP2 imposes on short sequences in packed batches.

**Caption verbatim:**
> Figure 38: Dynamic Context Parallelism for Packed Sequences.

### Figure 37 (p.61) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig37.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p61.png]]*
> [!quote] caption
> Compute imbalance in causal attention over packed sequences. are partitioned and which CP communication group is used by attention operators, without requiring any parameter redistribution or optimizer-state migration. Therefore, Dynamic-CP provides a practical form of dynamic parallelism for variable-length training with minimal framework overhead. Related work, including

> [!tip] 技术解读（多模态）
> **Description of Figure 38 (main figure):**

The figure illustrates three sub-panels comparing partitioning strategies for three packed sequences (orange, blue, green) on two GPUs:

- **(a) Input sequences:** Three sequences of varying length are packed together into microbatches. The orange sequence is long enough to require splitting; the blue and green sequences each fit on a single GPU.
- **(b) Standard CP2 (DP=1, CP=2):** A fixed context-parallel degree of 2 forces *all* sequences in every microbatch to be split across the two GPUs. The blue and green sequences are unnecessarily partitioned despite fitting on one device.
- **(c) Dynamic-CP:** The CP degree is chosen per-sequence at runtime. The orange sequence still uses CP=2 in microbatch-0, but blue and green each run independently with CP=1 in microbatch-1, eliminating wasteful splits.

**Key technical takeaway:** Dynamic-CP enables per-microbatch context-parallel resizing as a lightweight runtime decision that changes only token-slice partitioning and CP communication groups — avoiding any parameter/optimizer-state redistribution, and so eliminating the compute imbalance that rigid CP2 imposes on short sequences in packed batches.

**Caption verbatim:**
> Figure 38: Dynamic Context Parallelism for Packed Sequences.

### Figure 38 (p.61) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig38.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p61.png]]*
> [!quote] caption
> Dynamic Context Parallelism for Packed Sequences.

> [!tip] 技术解读（多模态）
> **Description of Figure 38 (main figure):**

The figure illustrates three sub-panels comparing partitioning strategies for three packed sequences (orange, blue, green) on two GPUs:

- **(a) Input sequences:** Three sequences of varying length are packed together into microbatches. The orange sequence is long enough to require splitting; the blue and green sequences each fit on a single GPU.
- **(b) Standard CP2 (DP=1, CP=2):** A fixed context-parallel degree of 2 forces *all* sequences in every microbatch to be split across the two GPUs. The blue and green sequences are unnecessarily partitioned despite fitting on one device.
- **(c) Dynamic-CP:** The CP degree is chosen per-sequence at runtime. The orange sequence still uses CP=2 in microbatch-0, but blue and green each run independently with CP=1 in microbatch-1, eliminating wasteful splits.

**Key technical takeaway:** Dynamic-CP enables per-microbatch context-parallel resizing as a lightweight runtime decision that changes only token-slice partitioning and CP communication groups — avoiding any parameter/optimizer-state redistribution, and so eliminating the compute imbalance that rigid CP2 imposes on short sequences in packed batches.

**Caption verbatim:**
> Figure 38: Dynamic Context Parallelism for Packed Sequences.

### Figure 39 (p.64) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig39.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p64.png]]*
> [!quote] caption
> Load balancing strategies in Megatron-Core MoE.

> [!tip] 技术解读（多模态）
> **Figure 39 Description**

The figure (not fully rendered in the text but referenced by its caption) illustrates **load balancing strategies in Megatron-Core MoE**, contextualized by the surrounding passage. Based on the discussion:

**Architecture / Components / Data Flow:**
- A token stream enters the MoE router, which assigns tokens to experts under a configurable capacity limit (the "droppable mode").
- When the token count for an expert exceeds its capacity, excess tokens are **dropped** and routed through a **residual/bypass path** rather than being processed by that expert.
- The "pad-to-max" variant pads all expert inputs to the same capacity, converting dynamic per-expert shapes into **static tensors**, enabling CUDA Graph optimizations.
- Residual traffic merges back with routed-expert outputs to produce the final layer output.

**Key Technical Takeaway (≤120 words):**
Droppable mode provides **predictable memory bounds** during early training when the router is poorly initialized — instead of letting token imbalance cause out-of-memory failures, overflow tokens are deterministically dropped and bypassed via residual connections. The pad-to-max extension is the critical enabler for system-level optimizations: by forcing all expert inputs to a uniform capacity, it converts MoE's inherently variable per-expert workloads into fixed tensor shapes, making techniques like CUDA Graphs (which require static dimensions) applicable and unlocking consistent kernel launches, reduced launch overhead, and reproducible memory footprints across training iterations.

**Caption (verbatim):**
"Figure 39: Load balancing strategies in Megatron-Core MoE."

### Figure 40 (p.65) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig40.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p65.png]]*
> [!quote] caption
> Shared expert architecture in Megatron-Core MoE. The shared expert processes all tokens while routed experts process only their assigned tokens. When overlap is enabled, shared expert computation runs in parallel with the token dispatch/combine communication, hiding its latency. FLOP and per parameter. The architecture has been adopted by NVIDIA’s Nemotron-3 Super and Ultra models.

> [!tip] 技术解读（多模态）
> ## Figure Description

**Architecture / Components / Data Flow**

Figure 40 illustrates the **Shared Expert Architecture** in Megatron-Core's Mixture-of-Experts (MoE) layer. The diagram depicts three parallel processing branches fed by the same input token stream:

1. **Shared Expert branch** (always-on): receives *all* tokens directly, bypassing the router.
2. **Router → Token Dispatch** branch: routes each token to its assigned top-*k* routed experts via an All-to-All communication.
3. **Routed Experts**: process only their dispatched subset of tokens; results return through Token Combine (another All-to-All).

The two outputs are summed to produce the MoE layer's final activation.

**Key Technical Takeaway:** When **communication-computation overlap** is enabled, the shared expert's GEMM executes concurrently with the token-dispatch/combine All-to-All collectives, effectively hiding the All-to-All latency behind useful compute.

## Caption (verbatim)

> **Figure 40:** Shared expert architecture in Megatron-Core MoE. The shared expert processes *all* tokens while routed experts process only their assigned tokens. When overlap is enabled, shared expert computation runs in parallel with the token dispatch/combine communication, hiding its latency.

### Figure 41 (p.66) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig41.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p66.png]]*
> [!quote] caption
> Flexible Pipeline Parallel Placement. 66

> [!tip] 技术解读（多模态）
> # Figure 41 Description

**Note:** The figure graphic itself is not visually rendered on this page — only the caption appears. Based on the surrounding text and Table 10, Figure 41 illustrates **Flexible Pipeline Parallel Placement** for DeepSeek-V3 across 16 PP ranks × 2 VPP ranks, showing layer assignment along a pipeline timeline.

**Architecture / Data Flow:**
- **Horizontal axis:** PP rank 0 → 15 (16 stages)
- **Vertical axis:** VPP rank 0 vs. VPP rank 1 (2 virtual stages per physical rank)
- **Rank 0:** embedding + 3 dense decoders → 2 decoders (absorbs 3 cheap layers to match 2 MoE cost)
- **Ranks 1–13:** 2 MoE decoders each (steady-state heavy compute)
- **Rank 14:** 2 decoders → MTP (multi-token prediction layer)
- **Rank 15:** 2 decoders → loss layer
- Arrows would show forward/backward microbatch propagation between VPP stages.

**Key Takeaway (≤120 words):** *Flexible Asymmetric VPP* breaks the assumption of uniform layer counts per stage. By packing 3 lightweight dense decoders into rank 0 (cost-equivalent to 2 MoE layers) and isolating the heavyweight MTP and loss layers at the tail ranks, the scheme achieves true computational balance despite DeepSeek-V3's heterogeneous workload (61 decoders + 1 MTP). This enables pipeline parallelism for arbitrary layer counts, eliminates bubble overhead from cost mismatch, and gives practitioners fine-grained control over placement of specialized layers (MTP, encoder-decoder, embedding, loss).

# Caption (Verbatim)

**Figure 41: Flexible Pipeline Parallel Placement.**

### Figure 42 (p.67) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig42.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p67.png]]*
> [!quote] caption
> An example of granular upcycling a dense layer into E2G2T2 fine-grained MoE. E2G2T2 denotes 4 experts, top 2, with half intermediate size. (1) We shard MLP weights in the intermediate dimension (4ℎ→2ℎ) then duplicate the shards. (2) We initialize half the router weights then duplicate them. This ensures Top2 always selects one of each MLP shard so MoE output is the same as the dense model at the s

> [!tip] 技术解读（多模态）
> ## Figure 42 Description

The figure illustrates the granular upcycling procedure that converts a single dense MLP layer into an **E2G2T2 fine-grained MoE** (4 experts, top-2 routing, half intermediate size).

**Architecture / Data Flow:**
1. **Start:** A dense MLP block with weight matrix of shape [in × intermediate × out].
2. **MLP sharding:** The intermediate dimension is split into shards, then each shard is duplicated, producing 4 smaller experts grouped into 2 pairs (E2G2T2 grouping).
3. **Router initialization:** Router weights are initialized for half the experts and duplicated, mirroring the shard duplication.
4. **Forward pass:** With Top-2 routing, each token is dispatched to one expert from each group; since duplicated experts are functionally identical at init, the aggregated output reconstructs the original dense activation.

**Key Technical Takeaway:**
The shard-then-duplicate scheme guarantees that the upcycled MoE's output is *bit-equivalent* to the source dense model at step 0, yielding a lossless warm-start with zero initial performance regression before fine-grained specialization training.

## Caption (verbatim)

**Figure 42:** An example of granular upcycling a dense layer into E2G2T2 fine-grained MoE. E2G2T2 denotes 4 experts, top 2, with half intermediate size. (1) We shard MLP weights in the intermediate dimension (H/2) then duplicate the shards. (2) We initialize half the router weights then duplicate them. This ensures Top2 always selects one of each MLP shard so MoE output is the same as the dense model at the start of training.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.11) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab01.png]]
> [!quote] caption
> MoE component to process group mapping.

> [!tip] 表格解读（多模态）
> **Description**

The figure (Table 1) defines how each Mixture-of-Experts (MoE) component — experts, routing/gating, and token-dispatch logic — is assigned to a distinct process group under a hybrid parallelism scheme. Architecturally, attention blocks live on one configuration (tensor-parallel, TP=4 in the example) while the MoE block is carved into its own process group using Expert Tensor Parallelism (ETP=1) plus a higher Expert Parallelism (EP) degree. Data flows: tokens → attention (TP-sharded) → router scores experts → tokens dispatched across EP shards → intra-expert computation (ETP) → outputs merged back into the global stream.

**Key takeaway:** *Parallel Folding* decouples the parallelism axes of attention and MoE so each layer family is independently tuned for its compute/communication profile.

**Caption (verbatim):**
"Table 1: MoE component to process group mapping."

### Table 2 (p.15) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab02.png]]
> [!quote] caption
> Contrasting parallelism requirements of attention and MoE layers within a single Transformer block.

> [!tip] 表格解读（多模态）
> **Figure description:**

The diagram illustrates Expert Parallelism (EP) data flow. A token sequence [T0]…[Tn] enters a **Router**, which directs tokens via **All-to-All Dispatch** to four GPUs. With EP=4, 8 Experts Total, 2 Experts per GPU: GPU 0 holds {E0, E1}, GPU 1 {E2, E3}, GPU 2 {E4, E5}, GPU 3 {E6, E7}. Each GPU processes its assigned tokens through its local experts, then results are merged via **All-to-All Combine** back into the original token order [T0]…[Tn].

**Key takeaway:** All-to-all communication volume remains *constant* as expert count grows—only GPU count changes—while grouping tokens from many sources per expert boosts GEMM compute intensity.

**Caption (verbatim):**

> Figure 4: Expert Parallelism (EP) distributes experts across GPUs. The all-to-all communication dispatches tokens to their assigned experts and combines results.

### Table 5 (p.25) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab05.png]]
> [!quote] caption
> Memory and throughput impact of fine-grained activation offloading.

> [!tip] 表格解读（多模态）
> **Description (≈120 words):**

The table compares two LLMs—**DeepSeek-V3 full** (TP1PP8EP32VPP4, MXFP8) and **Qwen3-235B** (TP2→TP1 + EP16→EP64)—across four columns: *Baseline* (memory & throughput), *+Offload* (memory & throughput), *Mem Δ*, and *Throughput Δ*.

- **DeepSeek-V3 full**: 169 GB → 151 GB (**−10.7%** memory), 945 → 930 TF/s (**−1.6%** throughput).
- **Qwen3-235B**: 172 → 175 GB (**+1.7%** memory), 800 → 920 TF/s (**+15.0%** throughput).

**Key takeaway:** Fine-grained activation offloading's benefit is workload-dependent—DeepSeek-V3 trades negligible throughput for double-digit memory savings, while Qwen3-235B gains 15% throughput at the cost of a marginal 1.7% memory increase, indicating offloading can be tuned toward either memory recovery or compute acceleration depending on the parallelization configuration.

**Caption (verbatim):**
"Table 5: Memory and throughput impact of fine-grained activation offloading."

### Table 6 (p.29) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab06.png]]
> [!quote] caption
> summarizes the memory optimization techniques described in this section and their primary targets.

> [!tip] 表格解读（多模态）
> **Note:** No actual figure image was included in the prompt — only text from a section on memory optimization in distributed training. My description below is reconstructed from the textual context describing the overlap mechanism.

**Architecture / Components / Data Flow:**
The figure likely depicts a pipeline of transformer layers arranged across model-parallel ranks, where each layer performs a forward pass, then backward pass (with activation recomputation). AllReduce of parameter gradients and ReduceScatter of sharded gradients are scheduled to overlap with backward computation of subsequent layers, while AllGather of parameters overlaps with forward computation of the next layer.

**Key Technical Takeaway (≤120 words):**
Increasing the micro-batch size enlarges the computation window available to hide collective communication (AllGather, ReduceScatter, AllReduce) behind forward/backward kernels, improving pipeline efficiency on tensor-parallel ranks. However, this comes at the cost of higher activation memory, since more micro-batches' activations (or their recomputed versions) must reside on the device simultaneously. The trade-off is exposed to users via the `overlap_param_gather` and `overlap_grad_reduce` flags, letting practitioners tune the compute–communication overlap based on their memory budget and per-GPU compute throughput. Roughly: bigger micro-batches ⇒ more overlap opportunity ⇒ better scaling, but bounded by HBM capacity.

**Caption transcribed verbatim (the only caption-like text provided):**

"4.1.8. Summary

Table 6 summarizes the memory optimization techniques described in this section and their primary targets."

(No figure caption was present in the supplied excerpt — only the Section 4.1.8 heading and its lead sentence referring to Table 6.)

### Table 7 (p.32) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab07.png]]
> [!quote] caption
> EP Scaling Performance for HybridEP and all-to-all (in µs).

> [!tip] 表格解读（多模态）
> **Description of the Main Figure (Table 7):**

This table presents a **performance benchmark comparison** of two expert-parallel communication strategies—**HybridEP** vs. **all-to-all**—measured on two GPU platforms (**NVIDIA GB200** and **H100**) across four **EP sizes** (8, 16, 32, 64). The data flow shows latency (in microseconds) for two MoE collective operations: **dispatch** and **combine**, organized as EP size × communication method × hardware. Both operations grow with EP size, but HybridEP grows gracefully while all-to-all inflates sharply, particularly on H100.

**Key Technical Takeaway:** HybridEP demonstrates **dramatically better scalability than pure all-to-all**—on H100 at EP=64, HybridEP achieves ~4398–4626 µs versus all-to-all's ~8727–9164 µs (≈2× speedup), with the gap widening as EP size grows, confirming HybridEP's superior communication efficiency at scale.

**Verbatim Caption:**
"Table 7: EP Scaling Performance for HybridEP and all-to-all (in μs)."

### Table 9 (p.58) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab09.png]]
> [!quote] caption
> SDPA performance in cuDNN for DeepSeek-V3.

> [!tip] 表格解读（多模态）
> **Description**

The figure is a benchmark table (Table 9) comparing cuDNN-implemented Scaled Dot-Product Attention (SDPA) for DeepSeek-V3 across two NVIDIA GPU platforms (Hopper, Blackwell) at two sequence lengths (4096, 16384), reporting forward- and backward-pass throughput in TFLOPS. **Key technical takeaway:** Blackwell delivers roughly 2.4–2.7× the forward TFLOPS and ~2.5× the backward TFLOPS of Hopper at every sequence length tested; longer sequences (16384) push forward throughput higher on both platforms—most strikingly on Blackwell (1324 → 1698 TFLOPS, ≈28% jump)—indicating that Blackwell's larger scale-up factors compound with the cuDNN SDPA kernel's sequence-length scaling. *(≈80 words)*

**Caption (verbatim):**

> Table 9: SDPA performance in cuDNN for DeepSeek-V3.

### Table 10 (p.66) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab10.png]]
> [!quote] caption
> Layer distribution for DeepSeek-V3 with flexible asymmetric VPP (PP = 16 , VPP = 2 ).

> [!tip] 表格解读（多模态）
> ## Figure Description

The figure presents **Table 10: Layer distribution for DeepSeek-V3 with flexible asymmetric VPP (PP = 16, VPP = 2)** and the corresponding pipeline layout diagram.

**Architecture / Components:**
- 16 Pipeline Parallel (PP) ranks, each split into two VPP ranks (VPP rank 0 and VPP rank 1).
- **PP rank 0 (VPP rank 0)** hosts the embedding layer plus 3 decoder layers; its VPP rank 1 holds 2 decoder layers.
- **PP ranks 1–13** are symmetric: 2 decoders in each VPP rank (MoE Decoder blocks).
- **PP rank 14** holds 2 decoders on VPP rank 0 and the **MTP (Multi-Token Prediction)** module on VPP rank 1.
- **PP rank 15** holds 2 decoders on VPP rank 0 and the **loss** computation on VPP rank 1.

**Data flow:** Tokens flow sequentially across PP ranks (0 → 15), with each rank's two VPP sub-ranks processing micro-batches staggered to hide latency (pipeline-bubble suppression).

**Key Technical Takeaway (≈50 words):**
Asymmetric VPP breaks the uniform-layer assumption of traditional pipeline parallelism by permitting unequal layer assignments across VPP sub-ranks—placing the embedding, MTP, and loss stages on lighter sub-ranks while distributing uniform 2-layer decoder blocks on the rest, achieving fine-grained load balancing and latency hiding for heterogeneous architectures. (49 words)

## Caption (Verbatim)

> Table 10: Layer distribution for DeepSeek-V3 with flexible asymmetric VPP (PP = 16, VPP = 2).

### Table 11 (p.69) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab11.png]]
> [!quote] caption
> Unified throughput benchmarks (per-GPU figures) for two mixture-of-experts models on NVIDIA GB300, GB200, and H100. All configurations use force-balanced routing. The Dtype column specifies the FP8

> [!tip] 表格解读（多模态）
> The table benchmarks two mixture-of-experts models (DeepSeek-V3 and Qwen3‑235B) across three NVIDIA platforms (Blackwell GB300/GB200 and Hopper H100) under force‑balanced routing. Each row maps a Model+System+GPU‑count+sequence‑length+dtype configuration (MXFP8, BF16, or FP8‑BLK) to per‑GPU TensorFLOP throughput (Per‑GPU TF) and per‑GPU token throughput (Tokens/s/GPU). Key takeaway: Blackwell's MXFP8 microscaling on GB300 delivers roughly 3.3× higher per‑GPU TF (1,233 vs 368) and tokens/s (4,730 vs 1,412) than H100's blockwise FP8 on DeepSeek‑V3, and MXFP8 also yields ~22% speedup over BF16 on the same GB200 platform.

**Verbatim caption:**
"Table 11: Unified throughput benchmarks (per-GPU figures) for two mixture-of-experts models on NVIDIA GB300, GB200, and H100. All configurations use force-balanced routing. The Dtype column specifies the FP8 recipe: FP8-BLK denotes blockwise FP8 on Hopper, and MXFP8 denotes microscaling FP8 on Blackwell."

### Table 12 (p.70) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab12.png]]
> [!quote] caption
> Impact of parallelism strategies on memory and communication. 𝑑 = parallelism degree. † Requires

> [!tip] 表格解读（多模态）
> **Description:** Table 12 compares five parallelism strategies (TP, EP, PP, CP, DP) across four dimensions: peak activation memory, weight memory, optimizer states, and per-layer communication cost. TP achieves the strongest activation, weight, and optimizer memory scaling (all 1/d) but pays the highest communication cost. EP, PP, and CP offer medium communication with varied memory profiles (e.g., PP activation can exceed 1 with VPP; CP/DP keep weights full but shard optimizer states via ZeRO-style sharding). **Key takeaway:** No single strategy dominates — TP minimizes per-device memory but maximizes comms, while DP minimizes comms but requires full weight replication, motivating hybrid schemes like 3D/4D parallelism to balance memory and communication overhead.

**Caption (verbatim):**
"Table 12: Impact of parallelism strategies on memory and communication. *d* = parallelism degree. †Requires distributed optimizer (--use-distributed-optimizer)."

### Table 13 (p.72) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab13.png]]
> [!quote] caption
> Memory bottleneck solutions.

> [!tip] 表格解读（多模态）
> **Description:**
The main element is Table 13, a structured lookup table enumerating memory-bottleneck mitigations for large-model training. It contains four columns — **Optimization**, **Overhead**, **Config**, **Reference** — across five rows of techniques (FP8 Training, Selective Recomputation, Precision-Aware Optimizer, Activation Offloading, Optimizer Offloading). The "Overhead" column is the decision axis: three entries flagged *Low* (computation-recompute / precision tricks, all in-GPU) precede two *Medium* entries (host/offload-based). The "Config" column maps each optimization to a corresponding CLI flag (e.g., `--fp8-format`, `--recompute-granularity`, `--offload-optimizer-states`), and the "Reference" column back-links each row to a numbered subsection (§4.1.3–§4.1.6). Below the table, prose introduces *Communication Bottleneck (Communication Wall)* with its diagnostic symptom and points forward to Table 14 — forming a "diagnose → consult table → apply config" workflow.

**Key Takeaway (≤120 words):**
The table's central design principle is **cost-tiered memory relief**: practitioners should first attempt *Low-overhead* in-device optimizations (FP8 formats, selective recomputation, precision-aware optimizer states) before falling back to *Medium-overhead* offloading of activations or optimizer states to host memory. Every technique is gated by a single CLI flag, enabling incremental, composable tuning tied to §§4.1.3–4.1.6 of the paper — a clean "try cheap, then expensive" escalation strategy for memory-constrained training.

**Caption (verbatim transcription):**
"Table 13: Memory bottleneck solutions."

### Table 14 (p.72) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab14.png]]
> [!quote] caption
> Communication bottleneck solutions.

> [!tip] 表格解读（多模态）
> ## Main Figure Description

The table ("Table 14") presents communication bottleneck solutions for distributed training, organized into three columns:

**Columns:** Communication Type | Config (command-line flag) | Reference

**Rows (five entries):**
1. **DP gradient reduce and param gather** → `--overlap-grad-reduce --overlap-param-gather` → —
2. **TP communication** → `--tp-comm-overlap` → —
3. **EP dispatcher** → `--moe-token-dispatcher-type` → §4.2.2
4. **EP all-to-all hiding** → `--overlap-moe-expert-parallel-comm` → §4.2.3
5. **PP send/recv** → `--pipeline-model-parallel-layout` → §7.5

**Architecture/Components:** The figure maps five parallelism strategies (DP = Data Parallel, TP = Tensor Parallel, EP = Expert Parallel for MoE, PP = Pipeline Parallel) to their corresponding configuration flags that mitigate communication overhead.

**Key Technical Takeaway:** Overlap-based optimizations dominate the solution space—four of five flags (`overlap-*`, `tp-comm-overlap`, `pipeline-model-parallel-layout`) hide communication latency by running collectives concurrently with computation, rather than reducing raw communication volume.

## Caption (verbatim)

**Table 14:** Communication bottleneck solutions.

### Table 15 (p.73) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab15.png]]
> [!quote] caption
> CPU overhead bottleneck solutions.

> [!tip] 表格解读（多模态）
> **Description:**

Table 15 presents a three-column reference table titled "GPU overhead bottleneck solutions," with columns for **Optimization**, **Config**, and **Reference**. It enumerates three mitigations targeting GPU-launch overhead: (1) disabling Python's garbage collector via `--manual-gc --manual-gc-interval 10` (no citation), (2) reducing kernel launches by decreasing tensor parallelism or increasing micro-batch size (no citation), and (3) enabling CUDA Graphs via `--cuda-graph-impl transformer_engine` (cited §4.3.6). Below the table, the surrounding text introduces the **Computation Bottleneck (Compute Efficiency Wall)**, where GPU kernels underutilize hardware—typically owing to small GEMMs in fine-grained MoE architectures—with the diagnostic symptom of low GPU SM utilization absent communication or CPU stalls, and remedies via batching/fusion/lower-precision kernels (Table 16).

**Key takeaway:** GPU underutilization often stems from launch Python-side overhead, not hardware saturation; toggling manual GC, tuning TP/MBS, and activating CUDA Graphs recover SM occupancy.

**Caption (verbatim):**

Table 15: GPU overhead bottleneck solutions.

### Table 16 (p.73) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab16.png]]
> [!quote] caption
> Computation bottleneck solutions.

> [!tip] 表格解读（多模态）
> The image does not contain a diagram or architecture figure—instead, it presents **Table 16** ("Computation bottleneck solutions") as the main visual element, followed by an Example paragraph and a Summary subsection (9.1.4).

**Table 16 — Description:** A three-column reference table mapping each computation-bottleneck optimization to its CLI flags and document section: (1) Grouped GEMM → `--moe-grouped-gemm` (§4.3.2); (2) Kernel fusions → `--moe-router-fusion --moe-permute-fusion` (§4.3.2); (3) FP8 precision → `--fp8-format --fp8-recipe` (§5). The data flow implied: profile compute-bound kernels → select an MoE-grouped-GEMM path, fuse the router/permute epilogues into one kernel, or drop to FP8 GEMMs.

**Key technical takeaway:** "the same model on different hardware can require entirely different optimization strategies" — on NVL8 (cross-node EP), all-to-all communication dominates (~30–50% of step time), whereas on NVL72 (intra-NVLink EP), enabling FP8 unmasks CPU/host-side launch latency as the new ceiling.

**Caption (verbatim):**
"Table 16: Computation bottleneck solutions."

### Table 17 (p.74) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab17.png]]
> [!quote] caption
> DeepSeek-V3 final optimized configurations on GB200 and H100. † Parallel Folding is used; TP

> [!tip] 表格解读（多模态）
> **Description (architecture/components/data flow + key takeaway):**

This table is a side-by-side comparison of two final optimized training configurations for the DeepSeek-V3 MoE model, deployed on two GPU clusters. The "architecture/components" are seven configuration axes: hardware scale (256×GB200 vs 1024×H100), 3D parallelism (TP/PP/EP with VPP), batch geometry (GBS/MBS/SeqLen), numerics (MXFP8 vs FP8-Blockwise), MoE token dispatcher (HybridEP vs DeepEP), activation recompute targets, and kernel-launch/runtime features (CUDA Graphs, EP all-to-all overlap). The "data flow" implication: GB200 uses TP=1 across dense modules with larger EP=64 for experts, while H100 uses TP=2/PP=8/EP=64, funneling identical sequence batches (8192/1/4096) through different precision/dispatcher pipelines.

**Key technical takeaway:** GB200 delivers **1048 TFLOPS/GPU — ~2.85× the 368 TFLOPS/GPU of H100** — enabled by higher per-GPU FLOPS, MXFP8 precision, narrower recompute scope, and CUDA Graphs. H100 compensates by enabling EP all-to-all overlap, since VPP=4 and SeqLen=4096 are shared across both platforms.

**Verbatim caption:**

Table 17: DeepSeek-V3 final optimized configurations on GB200 and H100. †Parallel Folding is used; TP applies to the non-MoE modules only, expert TP is always 1.

### Table 18 (p.74) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab18.png]]
> [!quote] caption
> DeepSeek-V3 optimization summary by platform.

> [!tip] 表格解读（多模态）
> **Description of the main figure:**

The image displays a table titled "Table 18: DeepSeek-V3 optimization summary by platform," which organizes optimization dimensions for the DeepSeek-V3 model across two hardware platforms. The table is structured with three columns: a "Category" column on the left for grouping optimization types (such as attention, MoE routing, communication, or kernel-level optimizations), and two data columns labeled "GB200" and "H100" to compare the specific optimizations applied on each platform. The header row is visible, but the body of the table is not shown in the cropped image.

**Key technical takeaway:** DeepSeek-V3 employs platform-specific optimizations, with distinct kernel/operator choices tailored to NVIDIA's GB200 versus H100 architectures, indicating that achieving peak efficiency requires GPU-generation-aware tuning rather than a single unified implementation.

**Verbatim caption:**
Table 18: DeepSeek-V3 optimization summary by platform.

### Table 19 (p.86) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab19.png]]
> [!quote] caption
> summarizes the notation used throughout this report.

> [!tip] 表格解读（多模态）
> No figure is present in the provided image. The content shown is only a section heading and a single descriptive sentence:

**Heading:** "A. Notation Reference"
**Body text:** "Table 19 summarizes the notation used throughout this report."

This appears to be introductory text from an appendix section that references a separate table (Table 19), but neither the table itself nor any architectural diagram, component diagram, or data-flow illustration is included in the image. There is no caption to transcribe verbatim either.

If you intended to share a specific figure (e.g., a model architecture diagram or pipeline schematic), it may not have uploaded correctly. Please try uploading the figure again, and I'll be happy to describe its architecture, components, data flow, and key technical takeaway as requested.

### Table 20 (p.87) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab20.png]]
> [!quote] caption
> Parallelism and training configuration details for benchmark entries reported in Table 11 .

> [!tip] 表格解读（多模态）
> **Description (≈93 words):**

Table 20 catalogs nine distributed-training configurations for DeepSeek-V3 and Qwen3-235B across NVIDIA GB300, GB200, and H100 clusters. Each row pairs a *Configuration* column (hardware × GPU count × sequence length × numeric format × achieved TF throughput) with a *Hyper-parameters* column listing parallelism axes—TP (tensor), PP/CPP (pipeline, virtual pipeline), CP (context), EP (expert), VPP (virtual-pipeline stage), and MBS/GBS (micro/global batch sizes)—with values given as an ASCII-formatted sequence. **Key takeaway:** MXFP8/FP8‑BLK numerics lift throughput ~35–44% over BF16 at identical scale (DeepSeek‑V3 on GB200: 1048–1233 TF vs 857 TF), and extending to 128k tokens simply adds CP=4 while preserving ~1,150 TF on GB300.

**Caption (verbatim):**

Table 20: Parallelism and training configuration details for benchmark entries reported in Table 11.

## 关键公式（原文截图，无 LaTeX 源 — 引用前请核对图片）

### 公式截图 (p.9)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-eq01.png]]
> 原文文本线索：`(𝑝𝑖= 𝜎(𝑙𝑖)/ ∑︀`

### 公式截图 (p.16)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-eq02.png]]
> 原文文本线索：`World Size = TP × CP × PP × DP,`

### 公式截图 (p.16)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-eq03.png]]
> 原文文本线索：`at minimum. Since EP ⊆DP, requesting EP=8 forces DP ≥8. Combined with CP=8 for long sequences, the`

### 公式截图 (p.17)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-eq04.png]]
> 原文文本线索：`• Traditional: EP ≤DP = 8, so maximum EP is 8.`

### 公式截图 (p.64)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-eq05.png]]
> 原文文本线索：`output(x) = 𝑊↑·`

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.9 `(𝑝𝑖= 𝜎(𝑙𝑖)/ ∑︀`
- p.16 `World Size = TP × CP × PP × DP,`
- p.16 `at minimum. Since EP ⊆DP, requesting EP=8 forces DP ≥8. Combined with CP=8 for long sequences, the`
- p.17 `• Traditional: EP ≤DP = 8, so maximum EP is 8.`
- p.42 `results in 𝐿×𝑀×2 graphs in total (where 𝐿= layers per GPU, 𝑀= microbatches, ×2 for forward/backward).`
- p.64 `output(x) = 𝑊↑·`

## 相关论文

- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey
- [[muon-is-scalable-for-llm-training]] — Muon is Scalable for LLM Training
- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[zero-memory-optimizations-toward-training-trillion-parameter-models]] — ZeRO: Memory Optimizations Toward Training Trillion Parameter Models
- [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] — GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints

## 技术点深读（DEEP）

![[deep/scalable-training-of-mixture-of-experts-models-with-megatron-core]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/scalable-training-of-mixture-of-experts-models-with-megatron-core.txt`（264084 字符）供引用检索。