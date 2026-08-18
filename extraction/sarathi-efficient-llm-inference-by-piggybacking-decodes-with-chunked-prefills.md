---
paper_num: "17"
title: "SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills"
authors: "Amey Agrawal*2, Ashish Panwar1, Jayashree Mohan1, Nipun Kwatra1, Bhargav S. Gulavani1, and Ramachandran Ramjee1 1Microsoft Research India 2Georgia Institute of Technology"
date: "2023/8/31"
arxiv: "https://arxiv.org/abs/2308.16369"
pdf: "papers/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills.pdf"
slug: "sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills"
tags: [disaggregated-serving]
---

# SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills

> [!abstract] 摘要（原文）
> 1\. 💡 SARATHI通过引入\`chunked-prefills\`和\`decode-maximal batching\`技术，解决了\`LLM\`推理中\`decode\`阶段\`GPU\`利用率低以及\`pipeline parallelism\`中由于\`prefill\`和\`decode\`时间差异导致的\`pipeline bubbles\`问题。 2. 🚀 \`decode-maximal batching\`使\`decode\`请求能够“\`piggyback\`”于\`prefill\`块，将内存密集型\`decode\`操作转变为计算密集型，并创建了计算负载均匀的\`hybrid batches\`，显著减少了\`pipeline bubbles\`。 3. 📈 SARATHI在\`LLaMA-13B\`模型上将\`decode throughput\`提高了高达10倍，\`end-to-end throughput\`提高了1.33倍；在\`GPT-3\`的\`pipeline parallelism\`中，它将\`bubbles\`减少了6.29倍，实现了1.91倍的\`end-to-end throughput\`提升。

## 元信息
- **发表日期**: 2023/8/31
- **作者**: Amey Agrawal*2, Ashish Panwar1, Jayashree Mohan1, Nipun Kwatra1, Bhargav S. Gulavani1, and Ramachandran Ramjee1 1Microsoft Research India 2Georgia Institute of Technology
- **arXiv**: https://arxiv.org/abs/2308.16369
- **本地 PDF**: `papers/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills.pdf`
- **页数**: 16

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p01.png]]
> [!quote] caption
> Example two-stage pipeline parallel schedule. (a)

> [!tip] 技术解读（多模态）
> **Description of the main figure:**

The figure compares two GPU pipeline-parallel schedules across GPU1 and GPU2 over time. **(a) Baseline (iteration-level scheduling):** Each request (A, B, C, D) executes its full prefill (A_p, B_p, C_p, D_p) as one large chunk, followed by decode tokens (A_p1B_p1, C_p1D_p1, A_p2B_p2). Mismatched prefill durations create idle "Bubble" gaps on the downstream GPU, and decodes occupy entire slots inefficiently.

**(b) SARATHI:** Prefills are split into smaller equal-sized chunks (A_p1, B_p1, A_p2, B_p2, C_p1, D_p1, etc.). Each batch is constructed as one prefill chunk plus multiple piggybacked decodes (C_p1A_p1, D_p1A_p2, C_p2B_p1, B_p2C_p1, D_p2A_p1). Uniform chunk sizes eliminate cross-GPU bubbles, and decodes ride along at negligible cost.

**Key technical takeaway:** Slicing prefills into uniform chunks and maximally batching them with decodes saturates GPU compute and eliminates pipeline bubbles, yielding order-of-magnitude higher decode throughput.

**Caption (verbatim):**

"Figure 1: **Example two-stage pipeline parallel schedule.** (a) In prior solutions like Orca [48], pipeline bubbles are common due to varying prompt and decode compute times. Further, decodes are highly inefficient (decode *cost-per-token* is order-of-magnitude higher than Prefill). (b) SARATHI significantly reduces pipeline bubbles and enables more efficient *piggybacked decodes*."

### Figure 2 (p.3) ⭐深度解读
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p03.png]]
> [!quote] caption
> High-level architecture of a decoder block. sequence length of each request (i.e., the number of input tokens in the given query), and H is the model’s embedding size (e.g., 5120 for LLaMA-13B).

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】SARATHI chunked-prefill：把 prompt 切成等长 prefill chunk（匹配流水级算力），在途 decode 请求 piggyback 到每个 prefill chunk 上→单次前向混合 prefill+decode token。解耦长 prefill 与 decode 延迟：每个流水级跑统一 hybrid-phase 步、消除 prefill-decode bubble、打满 GPU。更高单卡利用率+decode 吞吐+更大 batch。架构核心图。

### Figure 3 (p.4) ⭐深度解读
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p04.png]]
> [!quote] caption
> Per-token prefill and decode time with different batch sizes (sequence length = 1024) for LLaMa-13B on A6000 GPU. Prefill saturates GPU compute even at batch size of 1 and results in almost constant per-token time across batch sizes. Decode under-utilizes GPU compute and costs as much as 200× prefill for batch size 1. The incremental cost of linear operators for decode is almost zero as batch size

> [!tip] 技术解读（多模态）
> # Figure 4 Description (Primary Multi-Panel Figure)

## Architecture / Components / Data Flow
Figure 4 is a 2×2 layout analyzing **LLaMA-13B on A6000 GPU** through two linked lenses:

- **Top row (Figure 4a — Throughput, single layer):** Two line plots showing *Throughput (tokens/ms)* vs. *Batch Size* (1–512) for **Prefill** (left) and **Decode** (right), with five curves per plot representing sequence lengths {64, 128, 256, 512, 1024}.
- **Bottom row (Figure 4b — Arithmetic intensity, 1K seq length, per-request):** Two stacked bar charts of *Arithmetic intensity* vs. *Batch Size* (1, 2, 4, 8 for prefill; 1, 2, 4, 8, 256 for decode), broken down into four transformer ops: **preproj, attn, postproj, ffn**.

**Data flow:** profile each transformer op → measure per-op arithmetic intensity → correlate with measured tokens/ms throughput → explain why prefill and decode scale differently.

## Key Technical Takeaway
Prefill is *compute-bound* (high arithmetic intensity, saturates ≈180 tokens/ms), so throughput is insensitive to batch size; decode is *memory-bound* (vector-matrix multiplications, ~2 orders of magnitude lower arithmetic intensity), so per-token decode cost is up to **200×** prefill — making decode optimization the critical lever for LLM inference efficiency.

## Captions (verbatim)

**Figure 3:** Figure 3: Per-token prefill and decode time with different batch sizes (sequence length = 1024) for LLaMa-13B on A6000 GPU. Prefill saturates GPU compute even at batch size of 1 and results in almost constant per-token time across batch sizes. Decode under-utilizes GPU compute and costs as much as 200× prefill for batch size 1. The incremental cost of linear operators for decode is almost zero as batch size increases. The attention cost does not benefit from batch size as it is memory-bound.

**Figure 4:** Figure 4: Impact of the arithmetic intensity (bottom) on the throughput (top) of prefills and decodes for LLaMA-13B on A6000 GPU.

**Figure 4a:** (a) Throughput of a single layer of LLaMA-13B on A6000 GPU.

**Figure 4b:** (b) Arithmetic intensity with 1K sequence length (per-request).

### Figure 4 (p.4) ⭐深度解读
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p04.png]]
> [!quote] caption
> Impact of the arithmetic intensity (bottom) on the throughput (top) of prefills and decodes for LLaMA-13B on A6000 GPU. operations. Figure 4b shows the arithmetic intensity of each operation separately for prefill (left) and decode phases (right).

> [!tip] 技术解读（多模态）
> # Figure 4 Description (Primary Multi-Panel Figure)

## Architecture / Components / Data Flow
Figure 4 is a 2×2 layout analyzing **LLaMA-13B on A6000 GPU** through two linked lenses:

- **Top row (Figure 4a — Throughput, single layer):** Two line plots showing *Throughput (tokens/ms)* vs. *Batch Size* (1–512) for **Prefill** (left) and **Decode** (right), with five curves per plot representing sequence lengths {64, 128, 256, 512, 1024}.
- **Bottom row (Figure 4b — Arithmetic intensity, 1K seq length, per-request):** Two stacked bar charts of *Arithmetic intensity* vs. *Batch Size* (1, 2, 4, 8 for prefill; 1, 2, 4, 8, 256 for decode), broken down into four transformer ops: **preproj, attn, postproj, ffn**.

**Data flow:** profile each transformer op → measure per-op arithmetic intensity → correlate with measured tokens/ms throughput → explain why prefill and decode scale differently.

## Key Technical Takeaway
Prefill is *compute-bound* (high arithmetic intensity, saturates ≈180 tokens/ms), so throughput is insensitive to batch size; decode is *memory-bound* (vector-matrix multiplications, ~2 orders of magnitude lower arithmetic intensity), so per-token decode cost is up to **200×** prefill — making decode optimization the critical lever for LLM inference efficiency.

## Captions (verbatim)

**Figure 3:** Figure 3: Per-token prefill and decode time with different batch sizes (sequence length = 1024) for LLaMa-13B on A6000 GPU. Prefill saturates GPU compute even at batch size of 1 and results in almost constant per-token time across batch sizes. Decode under-utilizes GPU compute and costs as much as 200× prefill for batch size 1. The incremental cost of linear operators for decode is almost zero as batch size increases. The attention cost does not benefit from batch size as it is memory-bound.

**Figure 4:** Figure 4: Impact of the arithmetic intensity (bottom) on the throughput (top) of prefills and decodes for LLaMA-13B on A6000 GPU.

**Figure 4a:** (a) Throughput of a single layer of LLaMA-13B on A6000 GPU.

**Figure 4b:** (b) Arithmetic intensity with 1K sequence length (per-request).

### Figure 5 (p.5) ⭐深度解读
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p05.png]]
> [!quote] caption
> Pipeline bubbles in LLM inference A 2-way PP iteration-level schedule [48] across 4 requests (A,B,C,D) shows the existence of pipeline bubbles due to non-uniform batch execution times. set of layers; compared to TP which shards each layer across the participating GPUs. As discussed in §2.3, compared to TP, PP has a much better compute-communication ratio and does not require expensive interconnect

> [!tip] 技术解读（多模态）
> **Figure description (architecture/components/data flow):**

The diagram shows a 2-way Pipeline Parallel (PP) LLM inference schedule with two GPU timelines (GPU1 on top, GPU2 below) processing 4 requests (A–D). GPU1 executes a sequence of micro-batches: A₂ → B₂ → C₂ → D₂, followed by three idle gaps labeled PB₁, PB₂, and PB₃. GPU2 runs the same micro-batches but time-offset. The legend distinguishes three block types — Prefill (pink), Decode (blue), and Pipeline Bubble (hatched/dotted). Annotations mark chunk boundaries (A₂B₀₁, C₂D₂₁, A₂B₀₂) and a time arrow indicates progression. PB₁, PB₂, PB₃ each correspond to a distinct bubble cause identified in §3.3.

**Key technical takeaway:** Even iteration-level PP scheduling in LLM inference leaves GPU cycles wasted, because non-uniform prefill/decode work and diverging KV-cache lengths across micro-batches produce pipeline bubbles.

**Caption (verbatim):**

"Figure 5: Pipeline bubbles in LLM inference A 2-way PP iteration-level schedule [48] across 4 requests (A,B,C,D) shows the existence of pipeline bubbles due to non-uniform batch execution times."

### Figure 6 (p.6) ⭐深度解读
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p06.png]]
> [!quote] caption
> Example of how attention mask is set across dif- ferent chunk prefill iterations in SARATHI (q and k represent “query" and “key" tokens, respectively). The attention mask for v (“values") is set similarly.

> [!tip] 技术解读（多模态）
> ## Description

Figure 6 illustrates SARATHI's chunked-prefill attention masking across three successive iterations of a prefill sequence split into chunks of 4 tokens.

**Components shown:** Three binary attention mask matrices:
- **Iteration 1** (queries q0–q3, keys k0–k3): standard lower-triangular causal mask within the chunk.
- **Iteration 2** (q4–q7, keys k0–k7): lower-triangular within the current chunk, *plus* full attention to all prior-chunk keys (k0–k3, shaded green).
- **Iteration 3** (q8–q11, keys k0–k11): same pattern — each query attends to all previous chunks' keys (green) and causal-masked current-chunk keys (pink).

**Data flow:** Tokens are processed chunk-by-chunk; each query token peeks at all preceding key tokens (intra- and inter-chunk) but never future ones.

**Key takeaway:** Setting the mask this way makes chunked-prefill mathematically equivalent to a full prefill while enabling compute-saturation scheduling.

## Verbatim Caption

"Figure 6: Example of how attention mask is set across different chunk prefill iterations in SARATHI (q and k represent 'query' and 'key' tokens, respectively). The attention mask for v ('values') is set similarly."

### Figure 7 (p.7) ⭐深度解读
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p07.png]]
> [!quote] caption
> The effect of tile quantization on the runtime of one iteration of LLaMA-13B on A6000 GPU. maximal batching with that of the baseline scheme that com- putes prefill and decode iterations separately. With baseline batching, a decode-only iteration spends 12.49 milliseconds per token. In contrast, per-token decode time is only 1.2 mil- liseconds with decode-maximal batching. This shows that pig- gyb

> [!tip] 技术解读（多模态）
> ## Description

**Figure 7** is a line plot decomposing one transformer iteration of **LLaMA-13B on an A6000 GPU** into four time components as a function of sequence length (x-axis: 0–1024 tokens; y-axis: 0–250 ms):

- **preproj** (blue, solid, squares) — attention pre-projection
- **postproj** (orange, dashed, diamonds) — attention post-projection (smallest, flat)
- **ffn** (green, dash-dot, circles) — feed-forward block
- **total compute** (red, dotted, stars) — aggregate of the three

The data flow is: input tokens → (preproj + postproj attention block) + ffn block → summed into total compute. Curves are roughly piecewise-linear with visible jumps near batch-boundary tile-quantization effects.

**Key takeaway:** FFN dominates per-iteration cost (~2–3× attention), and total runtime grows nearly linearly with sequence length, with **quantization-induced step jumps** becoming more pronounced at longer contexts — indicating that tile-quantization overhead is a first-order concern for long-sequence inference.

## Caption (verbatim)

> Figure 7: The effect of tile quantization on the runtime of one iteration of LLaMA-13B on A6000 GPU.

### Figure 8 (p.9) ⭐深度解读
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p09.png]]
> [!quote] caption
> Decode-only speedup with SARATHI on an A6000 GPU with LLaMA-13B (chunk size = 256).

> [!tip] 技术解读（多模态）
> ## Figure 8 Description

**Type & Layout:** A grouped bar chart with the x-axis showing **Batch Size** (2, 4, 6, 8, 10, 12, 14, 16, 18) and the y-axis showing **Speedup (decode-only)** on a scale of 0–10×.

**Components/Data Encoding:** Each batch-size cluster contains three bars distinguishing sequence lengths via color/pattern:
- 🟧 Solid orange — Sequence length **1K**
- ⬜ Diagonal-hatched gray — Sequence length **2K**
- 🟩 Cross-hatched green — Sequence length **3K**

**Trend:** Speedup is **highest at small batch sizes** (peak ~10× at batch=2, seq=1K) and monotonically **decreases as batch size grows**, plateauing near 2.5–3× at batch=18. Shorter sequences consistently outperform longer ones.

**Key Technical Takeaway:** SARATHI's *decode-maximal batching* (piggybacking decode tokens onto prefill chunks with matrix-multiplication reuse of GPU weights) yields an **order-of-magnitude decode speedup for small batches (up to 10×)** and still delivers **2.8×–10× gains** across all tested configurations on LLaMA-13B/A6000.

---

### Caption (Verbatim)

**Figure 8:** Decode-only speedup with **S**ARATHI on an A6000 GPU with LLaMA-13B (chunk size = 256).

### Figure 9 (p.10) ⭐深度解读
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p10.png]]
> [!quote] caption
> Normalized throughput (tokens/ms) for LLaMa 13B on A6000 GPU with different sequence lengths, P:D ratios, and chunk sizes. 2 4 6 8 10 12 14 16 18

> [!tip] 技术解读（多模态）
> ## Figure Description

The main figure (Figure 10) is a 2×3 grid of stacked bar charts comparing inference latency between baseline (orange) and SARATHI (blue). Each bar is decomposed into four operation components—**preproj** (hatched), **attn**, **postproj** (cross-hatched), and **ffn**—revealing where time is spent.

**Layout:**
- Top row: prefill chunk size = 256; Bottom row: chunk size = 512
- Columns: sequence length = 1K, 2K, 3K (left to right)
- X-axis: batch size (2→18 for 1K, 2→8 for 2K, 2→6 for 3K)
- Y-axis: Time in seconds (0–10)

**Data flow:** For each (batch size, seq len, chunk size) configuration, two bars show total kernel time split into preprojection, attention, postprojection, and feed-forward components.

### Key Technical Takeaway (≤120 words)
SARATHI (blue) consistently outperforms the baseline (orange) across all configurations, with the FFN kernel dominating total runtime (~50–60%). The speedup primarily arises from reduced attention and postprojection overhead, while FFN time remains nearly identical—indicating SARATHI's gains come from better overlap of prefill/decode phases and KV-cache reuse rather than FFN acceleration. Larger chunk sizes (512) yield higher absolute throughput than smaller chunks (128) due to better arithmetic intensity, though optimal P:D ratios shift. Improvements of ~10–25% persist across batch sizes and sequence lengths.

### Caption (verbatim)
**Figure 10:** Breakdown of total time spent on different operations for LLaMa 13B on A6000 GPU with varying sequence lengths and batch sizes, using prefill chunk sizes of 256 (top half) and 512 (bottom half). Orange and blue bars represent baseline and SARATHI, respectively.

### Figure 10 (p.10) ⭐深度解读
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p10.png]]
> [!quote] caption
> Breakdown of total time spent on different operations for LLaMa 13B on A6000 GPU with varying sequence lengths and batch sizes, using prefill chunk sizes of 256 (top half) and 512 (bottom half). Orange and blue bars represent baseline and SARATHI, respectively. for sequence length of 1K as shown in Figure 9a. Using the chunk size of 512 for sequence length=1K at batch size of 18 also provides sign

> [!tip] 技术解读（多模态）
> ## Figure Description

The main figure (Figure 10) is a 2×3 grid of stacked bar charts comparing inference latency between baseline (orange) and SARATHI (blue). Each bar is decomposed into four operation components—**preproj** (hatched), **attn**, **postproj** (cross-hatched), and **ffn**—revealing where time is spent.

**Layout:**
- Top row: prefill chunk size = 256; Bottom row: chunk size = 512
- Columns: sequence length = 1K, 2K, 3K (left to right)
- X-axis: batch size (2→18 for 1K, 2→8 for 2K, 2→6 for 3K)
- Y-axis: Time in seconds (0–10)

**Data flow:** For each (batch size, seq len, chunk size) configuration, two bars show total kernel time split into preprojection, attention, postprojection, and feed-forward components.

### Key Technical Takeaway (≤120 words)
SARATHI (blue) consistently outperforms the baseline (orange) across all configurations, with the FFN kernel dominating total runtime (~50–60%). The speedup primarily arises from reduced attention and postprojection overhead, while FFN time remains nearly identical—indicating SARATHI's gains come from better overlap of prefill/decode phases and KV-cache reuse rather than FFN acceleration. Larger chunk sizes (512) yield higher absolute throughput than smaller chunks (128) due to better arithmetic intensity, though optimal P:D ratios shift. Improvements of ~10–25% persist across batch sizes and sequence lengths.

### Caption (verbatim)
**Figure 10:** Breakdown of total time spent on different operations for LLaMa 13B on A6000 GPU with varying sequence lengths and batch sizes, using prefill chunk sizes of 256 (top half) and 512 (bottom half). Orange and blue bars represent baseline and SARATHI, respectively.

### Figure 11 (p.11) ⭐深度解读
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p11.png]]
> [!quote] caption
> Comparison with iteration-level scheduler Orca for LLaMa 13B on A6000 GPU. configuration of sequence length and chunk size, we show the effect of varying batch sizes. Further, for each run, we also show the runtime across different operations i.e., preproj, attention, postproj, and ffn.

> [!tip] 技术解读（多模态）
> **Description (architecture/components/data flow + key takeaway):**

Figure 11 compares SARATHI against Baseline and Orca iteration-level scheduling on LLaMa 13B / A6000 GPU. Subfigure (a) is a grouped bar chart of normalized throughput vs. sequence length (1K/2K/3K), with four bars per group (Baseline, Orca worst-case, Orca best-case, SARATHI). Subfigure (b) is a line chart of normalized throughput vs. Prefill/Decode ratio (0–100%), plotting three SARATHI chunk-size curves (128, 256, 512) plus an Orca best-case curve. Data flows from the x-axis configuration into the y-axis normalized throughput metric. **Key takeaway:** SARATHI consistently outperforms Orca, achieving throughput gains of 1.27×, 1.25×, and 1.23× across 1K, 2K, and 3K sequence lengths, while Orca best-case degrades toward baseline as sequence length grows.

**Caption (verbatim):**

Figure 11: Comparison with iteration-level scheduler Orca for LLaMa 13B on A6000 GPU.

(a) Varying sequence lengths (chunk size=256 for SARATHI). We choose the maximum batch size which fits for the sequence length (18, 10 and 6 for 1K, 2K and 3K sequence lengths, respectively)

(b) Varying P:D ratio (sequence length=1K, batch size=18).

### Figure 12 (p.12) ⭐深度解读
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p12.png]]
> [!quote] caption
> Impact of SARATHI on pipeline bubbles (top) and request completion times (bottom) for GPT-3 deployed on DGX A100(s) in simulation. the effect of variable sequence lengths on request latencies.

> [!tip] 技术解读（多模态）
> ## Description of Figure 12

**Components:** Two stacked subplots comparing three serving strategies on simulated GPT-3 inference: **SARATHI** (blue dashed), **TP+PP** (orange solid), and **TP-only with 8 replicas** (green dash-dot, bottom panel only).

**Data flow / layout:**
- **Subplot (a) — "Comparison of bubble time":** CDF (0–1) of per-request pipeline bubble time on the y-axis vs. Bubble Time in seconds (0–~85 s) on the x-axis. SARATHI's curve rises steeply and saturates at CDF ≈ 1.0 by ~20 s, while TP+PP's curve is broad, stretching out to ~85 s.
- **Subplot (b) — "End-to-end request completion time":** Time to complete (s) on y-axis vs. Num Requests (0–10 000) on x-axis. All curves are roughly linear; TP+PP is the slowest (~3 700 s at 10K), TP (8 replicas) intermediate (~2 900 s), and SARATHI fastest (~1 900 s).

**Key technical takeaway (≤120 words):** SARATHI cuts the median pipeline bubble time by ~6.29× (equal-compute chunking) and accelerates end-to-end serving 1.91× over the TP+PP baseline and 1.48× over TP-only. By trading a smaller batchable KV cache for tighter prefill-decode fusion, it makes pipeline-parallel LLM inference competitive with — or better than — tensor-parallel-only deployment, despite TP-PP supporting 2.45× larger batches.

## Caption (verbatim)

Figure 12: Impact of S𝖠𝗋𝖺𝗍𝗁𝗂 on pipeline bubbles (top) and request completion times (bottom) for GPT-3 deployed on DGX A100(s) in simulation.

### Figure 13 (p.13) ⭐深度解读
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p13.png]]
> [!quote] caption
> Ablation study: Effect of varying the chunk size on different components of the system for LLaMa 13B on A6000 GPU. measure the time to compute the prefill phase for various se- quence lengths using the full sequence at once - this represents our baseline prefill performance. For each long sequence, we then compute the prefill with chunked-prefills and compare its end-to-end runtime with the baseli

> [!tip] 技术解读（多模态）
> **Figure Description:**
Figure 13 consists of three grouped bar charts comparing prefill-attention speedup (panels a, b) and overall end-to-end speedup (panel c) for LLaMa 13B on an A6000 GPU. Each chart plots speedup (y-axis, 0–1.4) against sequence length (x-axis: 1K, 2K, 3K), with eight bars per group representing chunk sizes from 64 to 512 (legend: 64, 128, 192, 256, 320, 384, 448, 512). Panel (a) isolates self-attention in prefill-only mode, panel (b) compares chunked-prefills against full prefill, and panel (c) shows the integrated batch throughput when chunked-prefills runs alongside decode-maximal batching.

**Key Technical Takeaway:**
Despite a 5× prefill slow-down at chunk size 64, end-to-end throughput nearly matches baseline, while chunk size 128 delivers up to 1.16× higher throughput despite being >2× slower in prefill—demonstrating that decode piggybacking compensates for prefill overhead, with a visible tile-quantization effect favoring chunk sizes that are multiples of 128 (e.g., 256 outperforms 320).

**Caption (verbatim):**
Figure 13: **Ablation study:** Effect of varying the chunk size on different components of the system for LLaMa 13B on A6000 GPU.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
B = \lfloor \left(\frac{M_G - M_S}{L*m_{kv}}\right) \rfloor
$$

## 相关论文

- [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] — Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve
- [[sglang-efficient-execution-of-structured-language-model-programs]] — SGLang: Efficient Execution of Structured Language Model Programs
- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation

## 技术点深读（DEEP）

![[deep/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills.txt`（76688 字符）供引用检索。