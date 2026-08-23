---
paper_num: "18"
title: "Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve"
authors: "Amey Agrawal*2, Nitin Kedia1, Ashish Panwar1, Jayashree Mohan1, Nipun Kwatra1, Bhargav S. Gulavani1, Alexey Tumanov2, and Ramachandran Ramjee1 1Microsoft Research India 2Georgia Institute of Technology"
date: "2024/3/4"
arxiv: "https://arxiv.org/abs/2403.02310"
pdf: "papers/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve.pdf"
slug: "taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve"
tags: [disaggregated-serving]
---

# Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve

> [!abstract] 摘要（原文）
> 1\. 💡 针对大型语言模型（LLM）推理中吞吐量与延迟的权衡问题，现有调度器因预填充和解码阶段的特性差异，常导致生成停顿和流水线气泡。 2. 🧠 Sarathi-Serve通过引入“分块预填充”将大型预填充请求拆分为计算量相等的块，并采用“无停顿调度”将新请求的预填充块与现有解码操作合并，以确保批处理计算均匀。 3. 🚀 实验结果显示，Sarathi-Serve在维持低尾延迟的同时显著提高了LLM服务容量，例如在不同模型和硬件上实现高达5.6倍的端到端服务容量增益。

## 元信息
- **发表日期**: 2024/3/4
- **作者**: Amey Agrawal*2, Nitin Kedia1, Ashish Panwar1, Jayashree Mohan1, Nipun Kwatra1, Bhargav S. Gulavani1, Alexey Tumanov2, and Ramachandran Ramjee1 1Microsoft Research India 2Georgia Institute of Technology
- **arXiv**: https://arxiv.org/abs/2403.02310
- **本地 PDF**: `papers/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve.pdf`
- **页数**: 18

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig01.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p01.png]]*
> [!quote] caption
> Yi-34B running on two A100 GPUs serving 128 requests from arxiv-summarisation trace. 1a highlights one of the many generation stalls lasting over several seconds in vLLM [53]. 1b shows the impact of increasing load on tail latency. Sarathi-Serve improves throughput while eliminating generation stalls. 1

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 1)

The figure compares **Sarathi-Serve vs vLLM** using Yi-34B on two A100 GPUs serving 128 requests from the *arxiv-summarisation* trace.

**Subfigure (a) – Generation stall:** A cumulative line plot of *Tokens Generated* vs *Time (s)*. The vLLM curve (orange) shows visible flat plateaus — stalls of several seconds where token generation halts. The Sarathi-Serve curve (teal) rises monotonically and steeper. An inset zooms into one stall region (~200–225 s) to emphasize the gap.

**Subfigure (b) – Tail latency:** A grouped bar chart of *Time-between-tokens, P99 (seconds)* at QPS ∈ {0.55, 0.7, 1.0}. vLLM's P99 grows sharply with load (≈0.5 → 1.3 s), while Sarathi-Serve stays flat near 0.3 s across all loads.

### Key Technical Takeaway
By combining **chunked-prefills** (splitting prefill into near-uniform chunks) with **stall-free scheduling** (injecting new requests without pausing decodes), Sarathi-Serve removes long generation stalls and keeps P99 tail latency nearly constant under increasing QPS — a regime where vLLM degrades severely.

## Caption (Verbatim)

> **Figure 1:** Yi-34B running on two A100 GPUs serving 128 requests from *arxiv-summarisation* trace. 1a highlights one of the many generation stalls lasting over several seconds in vLLM [53]. 1b shows the impact of increasing load on tail latency. Sarathi-Serve improves throughput while eliminating generation stalls.

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig02.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p02.png]]*
> [!quote] caption
> Current LLM serving systems involve a tradeoff be- tween throughput and latency depending on their scheduling policy. Prioritizing prefills optimizes throughput but sacrifices TBT (time-between-tokens) tail latency whereas prioritizing decodes has the opposite effect. Sarathi-Serve serves high throughput with low TBT latency via stall-free batching. (The figure is illustrative and actual values wi

> [!tip] 技术解读（多模态）
> **Figure Description:**

The figure is a 2D scatter plot comparing four LLM serving systems on a Throughput (y-axis) vs. TBT Latency (x-axis) plane. Four systems are plotted:
- **FasterTransformer** (bottom-left, red dot): Decode-prioritizing — low throughput, low TBT latency
- **Orca** (middle, pink dot): Prefill-prioritizing with iteration-level batching
- **vLLM** (top-right, blue dot): Prefill-prioritizing with paged attention — high throughput, high TBT latency
- **Sarathi-Serve** (top-left, green star): Stall-free batching — high throughput, low TBT latency

Dashed trajectory lines connect the points, illustrating how prior approaches (Orca → vLLM via paged attention) trend toward higher latency as throughput is optimized.

**Key Technical Takeaway:** Sarathi-Serve uniquely occupies the favorable top-left region, breaking the conventional throughput-latency tradeoff by using stall-free batching to coalesce ongoing decodes with prefill chunks from new requests.

**Caption (verbatim):**

Figure 2: Current LLM serving systems involve a tradeoff between throughput and latency depending on their scheduling policy. Prioritizing prefills optimizes throughput but sacrifices TBT (time-between-tokens) tail latency whereas prioritizing decodes has the opposite effect. Sarathi-Serve serves high throughput with low TBT latency via stall-free batching. (The figure is illustrative and actual values will depend on the model and workload characteristics.)

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig03.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p05.png]]*
> [!quote] caption
> Throughput of the prefill and decode phases with different batch sizes for Mistral-7B running on a single A100 GPU. We use prompt length of 1024 for both prefill and decode experiments. Note that different y-axis, showing pre- fills are much more efficient than decode. Further, note that batching boosts decode throughput almost linearly but has a marginal effect on prefill throughput.

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 4)

**Architecture/Components:** Two side-by-side stacked bar charts breaking down LLM inference runtime for Mistral-7B on a single A100 GPU. The left chart ("Prefill") plots total time (ms) against sequence length (128 → 2K), while the right chart ("Decode") plots time (ms) against batch size (1 → 64). Each bar is segmented into three stacked components shown in the legend: **linear** (teal, hatched), **attention** (gray), and **others** (red, hatched).

**Data Flow:** The decomposition shows how the wall-clock time of a forward pass is partitioned among operator categories. Prefill scales sharply with sequence length (peaking ~145 ms at 2K tokens), dominated by linear layers, while decode remains flat across batch sizes (~10–25 ms) since the per-token cost is nearly constant.

**Key Technical Takeaway:** **Linear (matmul) layers—not attention—dominate LLM inference runtime**, contributing >80% of total time even at long sequence lengths. Furthermore, because of low arithmetic intensity in decode, the cost of one linear operation on **1 decode token ≈ the cost on 128 prefill tokens**, implying decode is fundamentally memory-bound and batching is the lever to amortize linear-layer weight-loading cost. (~118 words)

---

## Captions Verbatim

**Figure 3:** "Throughput of the prefill and decode phases with different batch sizes for Mistral-7B running on a single A100 GPU. We use prompt length of 1024 for both prefill and decode experiments. Note that different y-axis, showing prefills are much more efficient than decode. Further, note that *batching boosts decode throughput almost linearly but has a marginal effect on prefill throughput*."

**Figure 4:** "Prefill and decode time with different input sizes for Mistral-7B running on single A100 GPU. Linear layers contribute to the majority of runtime in both prefill and decode phases. Due to the low arithmetic intensity in decode batches, the cost of linear operation for 1 decode token is nearly same as 128 prefill tokens."

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig04.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p05.png]]*
> [!quote] caption
> Prefill and decode time with different input sizes for Mistral-7B running on single A100 GPU. Linear layers contribute to the majority of runtime in both prefill and decode phases. Due to the low arithmetic intensity in decode batches, the cost of linear operation for 1 decode token is nearly same as 128 prefill tokens. into linear, attention and others, and shows their individual contributions. F

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 4)

**Architecture/Components:** Two side-by-side stacked bar charts breaking down LLM inference runtime for Mistral-7B on a single A100 GPU. The left chart ("Prefill") plots total time (ms) against sequence length (128 → 2K), while the right chart ("Decode") plots time (ms) against batch size (1 → 64). Each bar is segmented into three stacked components shown in the legend: **linear** (teal, hatched), **attention** (gray), and **others** (red, hatched).

**Data Flow:** The decomposition shows how the wall-clock time of a forward pass is partitioned among operator categories. Prefill scales sharply with sequence length (peaking ~145 ms at 2K tokens), dominated by linear layers, while decode remains flat across batch sizes (~10–25 ms) since the per-token cost is nearly constant.

**Key Technical Takeaway:** **Linear (matmul) layers—not attention—dominate LLM inference runtime**, contributing >80% of total time even at long sequence lengths. Furthermore, because of low arithmetic intensity in decode, the cost of one linear operation on **1 decode token ≈ the cost on 128 prefill tokens**, implying decode is fundamentally memory-bound and batching is the lever to amortize linear-layer weight-loading cost. (~118 words)

---

## Captions Verbatim

**Figure 3:** "Throughput of the prefill and decode phases with different batch sizes for Mistral-7B running on a single A100 GPU. We use prompt length of 1024 for both prefill and decode experiments. Note that different y-axis, showing prefills are much more efficient than decode. Further, note that *batching boosts decode throughput almost linearly but has a marginal effect on prefill throughput*."

**Figure 4:** "Prefill and decode time with different input sizes for Mistral-7B running on single A100 GPU. Linear layers contribute to the majority of runtime in both prefill and decode phases. Due to the low arithmetic intensity in decode batches, the cost of linear operation for 1 decode token is nearly same as 128 prefill tokens."

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig05.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]]*
> [!quote] caption
> Arithmetic intensity trend for LLaMA2-70B lin- ear operations with different number of token running on four A100s. Decode batches have low arithmetic intensity i.e., they are bottlenecked by memory fetch time, leading to low compute utilization. Prefill batches are compute bound with sub-optimal bandwidth utilization. Sarathi-Serve forms balanced batches by combining decodes and prefill chunks to

> [!tip] 技术解读（多模态）
> # Main Figure Description (Figure 7 — Scheduling Timeline Comparison)

**Architecture/Components:** Four horizontal timelines compare serving systems (vLLM, Orca, FasterTransformer, Sarathi-Serve) processing four requests (A, B, C, D). Each row shows token-batch composition over time: decode iterations are marked with subscript *d*, prefills with *p*, and chunked prefills with *p0, p1*. Request enter/exit points are annotated below each bar.

**Data Flow:** Requests enter the scheduler, get batched, and exit upon completion. vLLM and Orca exhibit red "Decodes stalled" regions where full prefills interrupt ongoing decode streams. FasterTransformer drains decodes before admitting prefills (no stalls, but low decode-batch size). Sarathi-Serve interleaves *chunked* prefills (p0, p1) with decodes—green "No stalls" label—preserving large hybrid batches.

**Key Takeaway:** Sarathi-Serve eliminates generation stalls by splitting prefills into chunks co-scheduled with decodes, achieving stall-free execution without sacrificing decode batch size or throughput.

---

**Caption (verbatim):**

"Figure 7: A generation stall occurs when one or more prefills are scheduled in between consecutive decode iterations of a request. A, B, C and D represent different requests. Subscript *d* represents a decode iteration, *p* represents a full prefill and *p0*, *p1* represent two chunked prefills of a given prompt. vLLM induces generation stalls by scheduling as many prefills as possible before resuming ongoing decodes. Despite supporting hybrid batches, Orca cannot mitigate generation stalls because the execution time of batches containing long prompts remains high. FasterTransformer is free of generation stalls as it finishes all ongoing decodes before scheduling a new prefill but compromises on throughput due to low decode batch size. In contrast, Sarathi-Serve generates a schedule that eliminates generation stalls yet delivers high throughput."

### Figure 6 (p.6) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig06.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]]*
> [!quote] caption
> Linear layer execution time as function of number of tokens in a batch for LLaMA2-70B on A100(s) with different tensor parallel degrees. When the number of tokens is small, execution time is dictated by the cost of fetching weights from HBM memory. Hence, execution time is largely stagnant in the 128-512 tokens range, especially for higher tensor parallel degrees. Once the number of tokens in the 

> [!tip] 技术解读（多模态）
> # Main Figure Description (Figure 7 — Scheduling Timeline Comparison)

**Architecture/Components:** Four horizontal timelines compare serving systems (vLLM, Orca, FasterTransformer, Sarathi-Serve) processing four requests (A, B, C, D). Each row shows token-batch composition over time: decode iterations are marked with subscript *d*, prefills with *p*, and chunked prefills with *p0, p1*. Request enter/exit points are annotated below each bar.

**Data Flow:** Requests enter the scheduler, get batched, and exit upon completion. vLLM and Orca exhibit red "Decodes stalled" regions where full prefills interrupt ongoing decode streams. FasterTransformer drains decodes before admitting prefills (no stalls, but low decode-batch size). Sarathi-Serve interleaves *chunked* prefills (p0, p1) with decodes—green "No stalls" label—preserving large hybrid batches.

**Key Takeaway:** Sarathi-Serve eliminates generation stalls by splitting prefills into chunks co-scheduled with decodes, achieving stall-free execution without sacrificing decode batch size or throughput.

---

**Caption (verbatim):**

"Figure 7: A generation stall occurs when one or more prefills are scheduled in between consecutive decode iterations of a request. A, B, C and D represent different requests. Subscript *d* represents a decode iteration, *p* represents a full prefill and *p0*, *p1* represent two chunked prefills of a given prompt. vLLM induces generation stalls by scheduling as many prefills as possible before resuming ongoing decodes. Despite supporting hybrid batches, Orca cannot mitigate generation stalls because the execution time of batches containing long prompts remains high. FasterTransformer is free of generation stalls as it finishes all ongoing decodes before scheduling a new prefill but compromises on throughput due to low decode batch size. In contrast, Sarathi-Serve generates a schedule that eliminates generation stalls yet delivers high throughput."

### Figure 7 (p.6) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig07.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]]*
> [!quote] caption
> A generation stall occurs when one or more prefills are scheduled in between consecutive decode iterations of a request. A, B, C and D represent different requests. Sub- script d represents a decode iteration, p represents a full prefill and p0, p1 represent two chunked prefills of a given prompt. vLLM induces generation stalls by scheduling as many pre- fills as possible before resuming ongoing d

> [!tip] 技术解读（多模态）
> # Main Figure Description (Figure 7 — Scheduling Timeline Comparison)

**Architecture/Components:** Four horizontal timelines compare serving systems (vLLM, Orca, FasterTransformer, Sarathi-Serve) processing four requests (A, B, C, D). Each row shows token-batch composition over time: decode iterations are marked with subscript *d*, prefills with *p*, and chunked prefills with *p0, p1*. Request enter/exit points are annotated below each bar.

**Data Flow:** Requests enter the scheduler, get batched, and exit upon completion. vLLM and Orca exhibit red "Decodes stalled" regions where full prefills interrupt ongoing decode streams. FasterTransformer drains decodes before admitting prefills (no stalls, but low decode-batch size). Sarathi-Serve interleaves *chunked* prefills (p0, p1) with decodes—green "No stalls" label—preserving large hybrid batches.

**Key Takeaway:** Sarathi-Serve eliminates generation stalls by splitting prefills into chunks co-scheduled with decodes, achieving stall-free execution without sacrificing decode batch size or throughput.

---

**Caption (verbatim):**

"Figure 7: A generation stall occurs when one or more prefills are scheduled in between consecutive decode iterations of a request. A, B, C and D represent different requests. Subscript *d* represents a decode iteration, *p* represents a full prefill and *p0*, *p1* represent two chunked prefills of a given prompt. vLLM induces generation stalls by scheduling as many prefills as possible before resuming ongoing decodes. Despite supporting hybrid batches, Orca cannot mitigate generation stalls because the execution time of batches containing long prompts remains high. FasterTransformer is free of generation stalls as it finishes all ongoing decodes before scheduling a new prefill but compromises on throughput due to low decode batch size. In contrast, Sarathi-Serve generates a schedule that eliminates generation stalls yet delivers high throughput."

### Figure 8 (p.7) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig08.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p07.png]]*
> [!quote] caption
> A 2-way pipeline parallel iteration-level schedule in Orca across 4 requests (A,B,C,D) shows the existence of pipeline bubbles due to non-uniform batch execution times.

> [!tip] 技术解读（多模态）
> ## Figure Description

**Architecture:** Figure 8 presents two 2-way pipeline-parallel (PP) iteration-level schedules for serving 4 LLM requests (A, B, C, D) across GPU0 and GPU1 along a shared timeline.

**Components:**
- **Orca (top):** Schedules requests in coarse prefill/decode blocks (e.g., A_p/B_p on GPU0, C_p/D_p). This produces visible gaps labeled "Bubble due to prefill length variation" and "Bubble due to prefill-decode interference."
- **Sarathi-Serve (bottom):** Uses *uniform-compute batches* (e.g., A_p1, B_p1, A_p2, B_p2, … interleaved with decode micro-steps). Result: "Minimal Bubbles."

**Data flow:** Micro-batches traverse GPU0 → GPU1; pipeline stalls occur whenever a stage idles waiting on the slower stage caused by heterogeneous prefill/decode token compositions.

**Key takeaway (≤120 words):** Pipeline parallelism alone does not eliminate bubbles during LLM inference because prefill/decode compute times vary drastically (prefill of a 4k-token prompt ≈1150 ms vs. decode ≈200 ms in Falcon-180B). Non-uniform micro-batches leave GPUs idle, wasting ~950 ms cycles and raising latency. Sarathi-Serve mitigates this by chunking prefills and constructing uniform-compute batches, keeping both pipeline stages saturated.

## Caption (verbatim)

**Figure 8:** A 2-way pipeline parallel iteration-level schedule in Orca across 4 requests (A,B,C,D) shows the existence of pipeline bubbles due to non-uniform batch execution times. Sarathi-Serve is able to minimize these stalls by creating uniform-compute batches.

### Figure 9 (p.8) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig09.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p08.png]]*
> [!quote] caption
> The incremental cost of coalescing prefills with decode batches. We consider two batching schemes – (i) Decode +

> [!tip] 技术解读（多模态）
> **Description:**

Figure 9 is a comparative performance study structured as a 2×3 grid of bar charts evaluating three batching strategies—**Decode-only**, **Decode + Chunked Prefill** (Sarathi-Serve), and **Decode + Full Prefill** (Orca-style). Row (a) benchmarks **Mistral-7B on one A100** (token budget 256); row (b) benchmarks **LLaMA2-70B on four A100s** (token budget 512). Each row sweeps context lengths {1024, 2048, 4096} across batch sizes {1, 32, 64}, plotting Batch Time (ms) with annotated speedup multipliers.

**Key takeaway:** Naïve hybrid batching inflates TBT latency by up to 28.3× (Decode + Full Prefill), whereas chunked prefill keeps the overhead close to Decode-only, with the gap widening at larger batch sizes and longer contexts—validating Sarathi-Serve's stall-free design.

**Caption (verbatim):**

Figure 9: The incremental cost of coalescing prefills with decode batches. We consider two batching schemes – (i) Decode + Full Prefill represents the hybrid batching of Orca wherein the entire prefill is executed in a single iteration along with ongoing decodes. (ii) Decode + Chunked Prefill represents Sarathi-Serve wherein prefills are chunked before being coalesced with ongoing decodes with a fixed token budget. Sarathi-Serve processes prefill tokens with much lower impact on the latency of decodes. Further, the relative impact of Sarathi-Serve on latency reduces with higher decode batch size and context lengths.

### Figure 10 (p.11) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig10.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p11.png]]*
> [!quote] caption
> Capacity (in queries per second) of Mistral-7B and

> [!tip] 技术解读（多模态）
> # Description

I do not see a figure (diagram, architecture, or visualization) in the provided image. The content shown is a **text section** from a research paper, specifically Section 5.1 "Capacity Evaluation," containing prose discussion about experimental methodology. There is no architecture, component diagram, or data flow illustration present to describe — only references to external figures (e.g., "Table 3") that are not visible here.

**Key technical takeaway** (from the visible text): The paper defines two SLO regimes on **P99 TTFT** (Time-To-First-Token) — *strict* (for interactive applications, individual-token latency constraints matter) and *relaxed* (for offline/batch workloads where only end-to-end completion time matters). The strict SLO threshold is set at **25× the decode-step execution time** with a 4k-token prefill, 32-batch size, and no prefill interference.

---

# Verbatim Transcription

> **5.1 Capacity Evaluation**
>
> We evaluate Sarathi-Serve, Orca and ... and both datasets under two differ... *relaxed* and *strict*. Similar to Pate... the intrinsic performance limitation... pair, we define the SLO on P99 T... 25× the execution time of a decod... (with prefill length of 4k and 32 b... any prefill interference for the s... respectively. **Table 3** shows a sum... thresholds. Note that the *strict* S... target desired for interactive appl... the other hand, the *relaxed* confi... systems where the complete sequen... be generated within a predictabl... constraints on individual tokens is ... experiments, we ensure that the ma... i.e., the queuing delay does not bl... seconds on median scheduling del...

*(Note: The image is cropped on the right side, so many lines are truncated mid-sentence. Ellipses [...] indicate cut-off text.)*

### Figure 11 (p.11) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig11.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p11.png]]*
> [!quote] caption
> Capacity of LLaMA2-70B and Falcon-180B (mod- els with pipeline parallelism) with different schedulers under strict (SLO-S) and relaxed (SLO-R) latency SLOs.

> [!tip] 技术解读（多模态）
> **Figure 10 — Capacity comparison across schedulers**

Components: Grouped bar chart with three schedulers (Orca, vLLM, Sarathi-Serve) compared per model under two SLO regimes — strict (SLO-S) and relaxed (SLO-R). Two sub-panels show results on two workloads: (a) *openchat_sharegpt4* and (b) *arxiv_summarization*. Models evaluated are Mistral-7B and Yi-34B. Y-axis is Max Capacity (queries/sec).

Key takeaway: Sarathi-Serve consistently beats Orca and vLLM under both strict and relaxed SLOs across both datasets — most notably 4.00× over Orca on Yi-34B/openchat_sharegpt4 under strict SLO, enabled by its adaptive token-budget chunked prefill that mitigates latency violations from long prompts.

**Caption (verbatim):**

Figure 10: Capacity (in queries per second) of Mistral-7B and Yi-34B with different schedulers under strict (SLO-S) and relaxed (SLO-R) latency SLOs.

### Figure 12 (p.12) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig12.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p12.png]]*
> [!quote] caption
> Latency – Throughput tradeoff in vLLM and

> [!tip] 技术解读（多模态）
> # Main Figure: Figure 13 — TP Scaling Performance on Falcon-180B

## Architecture / Components / Data Flow

**Panel (a) — Median Time-Between-Tokens (P50 TBT):**
- **Type:** Grouped bar chart
- **X-axis:** Batch Size (8, 16, 32, 64, 128)
- **Y-axis:** P50 TBT in seconds (0–0.3+)
- **Series:** Two configurations — TP8 (orange, cross-node tensor parallelism) vs. TP4:PP2 (teal, 4-way intra-node TP + 2-way cross-node pipeline parallelism)

**Panel (b) — Serving Capacity:**
- **Type:** Grouped bar chart
- **X-axis:** Latency SLO regime — strict (SLO-S) and relaxed (SLO-R)
- **Y-axis:** Max Capacity (0–1.25)
- **Series:** Three bars per SLO — vLLM TP8, vLLM TP4:PP2 hybrid, Sarathi-Serve TP4:PP2

## Key Technical Takeaway

Cross-node all-reduce communication inflates TP latency by ~2× versus pipeline parallelism on commodity Ethernet; chunked-prefills + PP make pipeline parallelism viable, boosting Falcon-180B capacity by **4.3× (strict)** and **3.6× (relaxed)** over vLLM.

## Caption (Verbatim Transcription)

**Figure 13:** TP scales poorly across nodes. (a) Median TBT for decode-only batches: cross node TP increases median TBT by more than 2× compared to a 4-way TP within node and PP across nodes. (b) Capacity under strict (SLO-S) and relaxed (SLO-R) latency SLOs: Sarathi-Serve increases Falcon-180B's serving capacity by 4.3× and 3.6× over vLLM's TP-only and hybrid-parallel configurations under strict SLOs.

### Figure 13 (p.12) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig13.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p12.png]]*
> [!quote] caption
> TP scales poorly across nodes. (a) Median TBT for decode-only batches: cross node TP increases median TBT by more than 2× compared to a 4-way TP within node and PP across nodes. (b) Capacity under strict (SLO-S) and re- laxed (SLO-R) latency SLOs: Sarathi-Serve increases Falcon- 180B’s serving capacity by 4.3× and 3.6× over vLLM’s TP- only and hybrid-parallel configurations under strict SLOs.

> [!tip] 技术解读（多模态）
> # Main Figure: Figure 13 — TP Scaling Performance on Falcon-180B

## Architecture / Components / Data Flow

**Panel (a) — Median Time-Between-Tokens (P50 TBT):**
- **Type:** Grouped bar chart
- **X-axis:** Batch Size (8, 16, 32, 64, 128)
- **Y-axis:** P50 TBT in seconds (0–0.3+)
- **Series:** Two configurations — TP8 (orange, cross-node tensor parallelism) vs. TP4:PP2 (teal, 4-way intra-node TP + 2-way cross-node pipeline parallelism)

**Panel (b) — Serving Capacity:**
- **Type:** Grouped bar chart
- **X-axis:** Latency SLO regime — strict (SLO-S) and relaxed (SLO-R)
- **Y-axis:** Max Capacity (0–1.25)
- **Series:** Three bars per SLO — vLLM TP8, vLLM TP4:PP2 hybrid, Sarathi-Serve TP4:PP2

## Key Technical Takeaway

Cross-node all-reduce communication inflates TP latency by ~2× versus pipeline parallelism on commodity Ethernet; chunked-prefills + PP make pipeline parallelism viable, boosting Falcon-180B capacity by **4.3× (strict)** and **3.6× (relaxed)** over vLLM.

## Caption (Verbatim Transcription)

**Figure 13:** TP scales poorly across nodes. (a) Median TBT for decode-only batches: cross node TP increases median TBT by more than 2× compared to a 4-way TP within node and PP across nodes. (b) Capacity under strict (SLO-S) and relaxed (SLO-R) latency SLOs: Sarathi-Serve increases Falcon-180B's serving capacity by 4.3× and 3.6× over vLLM's TP-only and hybrid-parallel configurations under strict SLOs.

### Figure 14 (p.13) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig14.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p13.png]]*
> [!quote] caption
> Overhead of chunked-prefills in prefill computation for Yi-34B (TP-2) normalized to the cost of no-chunking, shown for various prompt lengths using chunk lengths of 512, 1024 and 2048.

> [!tip] 技术解读（多模态）
> **Figure 14 — Bar chart of overhead from chunked-prefills**

**Architecture/Components:** Grouped vertical bar chart. X-axis = prompt length (2K, 4K, 8K tokens). Y-axis = overhead (0.00–1.50, normalized to no-chunking cost). Three colored bar series per group representing chunk sizes of **512** (solid orange), **1024** (solid teal), and **2048** (hatched tan).

**Data flow/trend:** Within each prompt-length cluster, bar height decreases monotonically as chunk size grows — i.e., finer chunking ⇒ larger overhead. Across prompt lengths, the overhead stays roughly constant for a given chunk size (≈1.25 for 512, ≈1.20 for 1024, ≈1.00 for 2048).

**Key technical takeaway:** Even the smallest 512-token chunk adds only ~25% overhead to Yi-34B prefill compute, and larger 2048-token chunks become nearly free — confirming chunking is a viable, low-cost mechanism for interleaving prefill with decode batches.

**Caption (verbatim):**
*Figure 14: Overhead of chunked-prefills in prefill computation for Yi-34B (TP-2) normalized to the cost of no-chunking, shown for various prompt lengths using chunk lengths of 512, 1024 and 2048.*

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.10) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-tab01.png]]
> [!quote] caption
> Models and GPU configurations (GQA: grouped- query attention, SW: sliding window).

> [!tip] 表格解读（多模态）
> ## Description & Technical Takeaway

Note: No figure depicting architecture/components/data flow is visible in the provided input—only **Table 1** and its caption are shown. Below I describe the table that is present and offer a takeaway based on it.

**Main figure (table) — components shown:**
- **Rows:** two datasets — `openchat_sharegpt4` and `arxiv_summarization`
- **Columns:** grouped under two families
  1. *Prompt Tokens* — Median, P90, Std. deviation
  2. *Output Tokens* — Median, P90, Std. deviation
- **Data flow / reported values:**
  - `openchat_sharegpt4`: prompt median = 1730, P90 = 5696, σ = 2088 | output median = 415, P90 = 834, σ = 101
  - `arxiv_summarization`: prompt median = 7059, P90 = 12985, σ = 3638 | output median = 208, P90 = 371, σ = 265

**Key technical takeaway (≈70 words):**
arXiv prompts are roughly **4× longer in median** than ShareGPT prompts (7059 vs 1730) and **~2.3× more variable** (σ = 3638 vs 2088), while outputs are markedly shorter (median 208 vs 415). This asymmetry argues for **asymmetric KV-cache sizing and attention budgeting**—expanding capacity for the long, variable context phase while keeping the decoding phase compact.

## Verbatim Caption Transcription

> Table 1: Models and GPU configurations (GQA: grouped-query attention, SW: sliding window).

### Table 2 (p.10) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-tab02.png]]
> [!quote] caption
> Datasets used for evaluation.

> [!tip] 表格解读（多模态）
> **Note:** The provided content contains text and a data table (SLO targets per model), but **no architecture/system diagram** depicting components or data flow. I cannot describe a figure that isn't present. I'll describe what is actually visible and transcribe the available caption.

**What is visible:**
A small table listing four evaluated models (Mistral-7B, Yi-34B, LLaMA2-70B, Falcon-180B) against two SLO configurations — *relaxed SLO* and *strict SLO* — measured by **P99 TBT (s)** (Tail Token-Bound Time). Values range from 0.1 s (strict, 7B) up to 5 s (relaxed, 70B/180B).

**Caption verbatim:**
> Table 2: Datasets used for evaluation.

**Key technical takeaway (from surrounding text, ≤120 words):**
Sarathi-Serve is an LLM inference serving system that combines **chunked prefills** with **stall-free batching** atop **pipeline (PP)** and **tensor (TP)** parallelism, using NCCL for inter-GPU communication. It targets both loose and strict latency SLOs by tuning the per-step token budget (chunksize), which lets long prefill requests share a batch with active decode requests without stalling ongoing generations. Evaluation spans four models (7B–180B) and asks: maximum load under SLO, deployment trade-offs (TP vs. PP), chunked-prefill overhead, and the marginal benefit of stall-free batching in isolation vs. tandem use. This SLO table operationalizes that evaluation by fixing per-model tail-latency targets, enabling fair load comparisons across model scales.

### Table 3 (p.10) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-tab03.png]]
> [!quote] caption
> SLOs for different model configurations.

> [!tip] 表格解读（多模态）
> ## Figure Description

**Architecture/Components/Data Flow:** Table 3 is a 4×3 matrix presenting the P99 Time-Between-Tokens (TBT) Service Level Objectives (in seconds) used to evaluate Sarathi-Serve across four LLM scales. The columns compare a *relaxed* SLO versus a *strict* SLO regime, while the rows stratify by model size: Mistral-7B (0.5 s / 0.1 s), Yi-34B (1 s / 0.2 s), LLaMA2-70B (5 s / 1 s), and Falcon-180B (5 s / 1 s).

**Key Technical Takeaway:** Tolerance budgets scale roughly with model size — larger models (≥70B params) require ~10× looser token-latency targets than 7B models, reflecting their inherently slower per-token decode cost. Mistral-7B permits the tightest strict SLO (0.1 s), whereas both 70B and 180B models share an identical 1 s strict budget, suggesting TBT ceilings plateau for the largest configurations regardless of parameter count.

## Caption (verbatim)

**Table 3: SLOs for different model configurations.**

### Table 4 (p.13) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-tab04.png]]
> [!quote] caption
> TTFT and TBT latency measured in seconds for hybrid-batching and chunked-prefills used in isolation as well as when they are used in tandem, evaluated over 128 requests for Yi-34B running on two A100s with a token budget of 1024. By using both hybrid-batching and chunked-prefills , Sarathi-Serve is 

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**

The main figure (Figure 14) is a grouped bar chart depicting the **overhead of chunked-prefills** in prefill computation for the Yi-34B model (TP-2). The x-axis shows prefill lengths (2K, 4K, 8K tokens), and the y-axis shows overhead normalized to the no-chunking baseline (range 0.00–1.50). Three chunk-size variants are compared per prefill length: 512 (orange, diagonal hatching), 1024 (teal, horizontal hatching), and 2048 (cream, diagonal hatching). Smaller chunks (512) consistently incur the highest overhead (~1.27–1.33×), 1024-chunks are intermediate (~1.18–1.23×), and 2048-chunks hover near parity (~0.97–1.02×). The data flow is straightforward: prompt → chunked prefill stages → comparison against non-chunked prefill.

**Key takeaway:** Chunked-prefill overhead is small and bounded (<35%); using larger chunks (2048) nearly eliminates overhead, making chunked-prefills cost-effective for production serving.

**Caption (verbatim):**

Figure 14: Overhead of *chunked-prefills* in prefill computation for Yi-34B (TP-2) normalized to the cost of no-chunking, shown for various prompt lengths using chunk lengths of 512, 1024 and 2048.

## 相关论文

- [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] — SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills
- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[sglang-efficient-execution-of-structured-language-model-programs]] — SGLang: Efficient Execution of Structured Language Model Programs
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation

## 技术点深读（DEEP）

![[deep/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve.txt`（82501 字符）供引用检索。