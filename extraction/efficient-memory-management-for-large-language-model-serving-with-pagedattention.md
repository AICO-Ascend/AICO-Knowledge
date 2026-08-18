---
paper_num: "52"
title: "Efficient Memory Management for Large Language Model Serving with PagedAttention"
authors: "Model Serving with PagedAttention Woosuk Kwon1,∗Zhuohan Li1,∗Siyuan Zhuang1 Ying Sheng1,2 Lianmin Zheng1 Cody Hao Yu3 Joseph E. Gonzalez1 Hao Zhang4 Ion Stoica1 1UC Berkeley 2Stanford University 3Independent Researcher 4"
date: "2023/9/13"
arxiv: "https://arxiv.org/abs/2309.06180"
pdf: "papers/efficient-memory-management-for-large-language-model-serving-with-pagedattention.pdf"
slug: "efficient-memory-management-for-large-language-model-serving-with-pagedattention"
tags: []
---

# Efficient Memory Management for Large Language Model Serving with PagedAttention

> [!abstract] 摘要（原文）
> 1. High throughput serving of large language models (LLMs) requires batching sufficiently many requests at a time. How- ever, existing systems struggle because the key-value cache (KV cache) memory for each request is huge and grows and shrinks dynamically. When managed inefficiently, this memory can be significantly wasted by fragmentation and redundant duplication, limiting the

## 元信息
- **发表日期**: 2023/9/13
- **作者**: Model Serving with PagedAttention Woosuk Kwon1,∗Zhuohan Li1,∗Siyuan Zhuang1 Ying Sheng1,2 Lianmin Zheng1 Cody Hao Yu3 Joseph E. Gonzalez1 Hao Zhang4 Ion Stoica1 1UC Berkeley 2Stanford University 3Independent Researcher 4
- **arXiv**: https://arxiv.org/abs/2309.06180
- **本地 PDF**: `papers/efficient-memory-management-for-large-language-model-serving-with-pagedattention.pdf`
- **页数**: 16

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p01.png]]
> [!quote] caption
> Left: Memory layout when serving an LLM with 13B parameters on NVIDIA A100. The parameters (gray) persist in GPU memory throughout serving. The memory for the KV cache (red) is (de)allocated per serving request. A small amount of memory (yellow) is used ephemerally for activation. Right: vLLM smooths out the rapid growth curve of KV cache memory seen in existing systems [31, 60], leading to a nota

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】PagedAttention 内存布局(Fig.1)：13B 模型在 A100-40G 上参数占 65%（26GB 常驻）、KV cache >30%（每请求动态）、激活小片。传统系统把每请求 KV 存成单连续张量→内部+外部碎片严重、batch 受限。PagedAttention 借 OS 虚拟内存分页：KV 切成固定块（如 16 token）存非连续物理显存，每请求 block table 映射逻辑→物理（类比页表）；请求间可共享物理块（并行采样/beam search/前缀共享）；碎片仅剩 sub-block 余量（~1 token vs GB 级）→近乎零 KV 浪费、吞吐 2-4x。架构核心图，KV-cache/serving 基石。

### Figure 2 (p.2) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p02.png]]
> [!quote] caption
> Average percentage of memory wastes in different LLM serving systems during the experiment in §6.2. percentage of memory is used for other data, including ac- tivations – the ephemeral tensors created when evaluating the LLM. Since the model weights are constant and the ac- tivations only occupy a small fraction of the GPU memory, the way the KV cache is managed is critical in determining the maxi

> [!tip] 技术解读（多模态）
> **Figure Description:**

The figure is a stacked bar chart titled along the y-axis "KV cache usage (%)" comparing four LLM serving systems across four memory categories:
- **Token states (green)** – actual usable KV cache
- **Reservation (orange)** – reserved but unused memory
- **Internal fragmentation (red)** – wasted within allocated chunks
- **External fragmentation (gray)** – wasted across chunks

**Bar values:**
| System | Token | Reservation | Internal frag. | External frag. |
|---|---|---|---|---|
| Orca (Max) | 20.4 | 13.3 | 57.3 | 8.9 |
| Orca (Pow2) | 26.8 | 17.9 | 13.6 | 41.6 |
| Orca (Oracle) | 38.2 | 25.2 | ~0 | 36.6 |
| vLLM | 96.3 | ~0 | ~0 | ~3 |

**Key technical takeaway:** Existing LLM serving systems waste 60–80% of KV cache memory due to fragmentation and over-reservation from contiguous pre-allocation, whereas vLLM's paged, non-contiguous KV cache approach retains ~96% of memory for actual token states—directly enabling larger batch sizes and higher throughput.

**Caption (verbatim):**
Figure 2. Average percentage of memory wastes in different LLM serving systems during the experiment in §6.2.

### Figure 3 (p.4) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p04.png]]
> [!quote] caption
> KV cache memory management in existing systems. Three types of memory wastes – reserved, internal fragmentation, and external fragmentation – exist that prevent other requests from fitting into the memory. The token in each memory slot represents its KV cache. Note the same tokens can have different KV cache when at different positions. 3

> [!tip] 技术解读（多模态）
> **Figure 3 Description**

The figure is a horizontal memory-layout diagram illustrating how existing LLM serving systems statically pre-allocate a contiguous chunk of GPU memory for each request's KV cache. Two request allocations are shown side by side.

**Components (left → right):**
- **Request A (yellow):** 7 prompt tokens ("Four…our") occupying KV cache slots, followed by generated tokens ("fathers," "brought," "forth"), a `<eos>` token, 2 *reserved* future slots, then **2,038 never-used slots (internal fragmentation)**.
- **White gap:** *External fragmentation* between the two allocations.
- **Request B (green):** 3 prompt tokens ("You only live"), one generated token ("once"), reserved slots, `<eos>`, and **507 never-used slots (internal fragmentation)**.

**Data flow:** Prompt tokens → KV cache filled token-by-token as decoding progresses → reserved/future slots allocated upfront for the maximum possible sequence length.

**Key takeaway:** Pre-allocating contiguous memory for worst-case sequence lengths simultaneously wastes capacity through three mechanisms — reserved future slots, internal fragmentation (over-provisioned unused slots), and external fragmentation (allocator gaps) — driving effective memory utilization down to ~20.4%.

**Verbatim caption:**

**Figure 3.** KV cache memory management in existing systems. Three types of memory wastes – reserved, internal fragmentation, and external fragmentation – exist that prevent other requests from fitting into the memory. The token in each memory slot represents its KV cache. Note the same tokens can have different KV cache when at different positions.

### Figure 4 (p.5) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p05.png]]
> [!quote] caption
> vLLM system overview.

> [!tip] 技术解读（多模态）
> ## Main Figure: Figure 4 (vLLM System Overview)

**Architecture/Components/Data Flow:**
- **Scheduler** (top, green): central coordinator that distributes work to GPU workers.
- **KV Cache Manager** (middle-left): maintains logical↔physical block tables for the KV cache; interfaces with both block allocators.
- **Block Allocators** (bottom): separate CPU and GPU allocators hand out physical memory blocks.
- **Worker 0 … Worker N−1** (right column): each holds a **Cache Engine** + a **Model Shard** (one model partition per GPU).
- *Data flow:* Scheduler → all Workers (dispatch); Scheduler → KV Cache Manager → Block Allocators (memory bookkeeping); KV Cache Manager ↔ Workers (KV block management instructions).

**Key Technical Takeaway (≈110 words):**
vLLM decouples the centralized **scheduler/KV-cache manager** from the per-GPU **worker shards**, so the cache can be managed as paged, non-contiguous blocks across distributed devices. By pushing paging decisions to a single controller while keeping compute local, the system achieves near-zero KV-cache waste and flexible memory sharing across requests — addressing fragmentation and pre-allocation pain points that prior LLM serving systems could not solve, without slowing down token generation.

**Caption (verbatim):**
*Figure 4. vLLM system overview.*

### Figure 5 (p.5) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p05.png]]
> [!quote] caption
> Illustration of the PagedAttention algorithm, where the attention key and values vectors are stored as non-contiguous blocks in the memory. block size (𝐵). Denote the key block 𝐾𝑗= (𝑘(𝑗−1)𝐵+1, . . . ,𝑘𝑗𝐵) and value block 𝑉𝑗= (𝑣(𝑗−1)𝐵+1, . . . , 𝑣𝑗𝐵). The attention com- putation in Eq. 4 can be transformed into the following block- wise computation: 𝐴𝑖𝑗= exp(𝑞⊤ 𝑖𝐾𝑗/ √ 𝑑) Í⌈𝑖/𝐵⌉ 𝑡=1 exp(𝑞⊤ 𝑖𝐾𝑡1/ √ 𝑑

> [!tip] 技术解读（多模态）
> ## Main Figure: Figure 4 (vLLM System Overview)

**Architecture/Components/Data Flow:**
- **Scheduler** (top, green): central coordinator that distributes work to GPU workers.
- **KV Cache Manager** (middle-left): maintains logical↔physical block tables for the KV cache; interfaces with both block allocators.
- **Block Allocators** (bottom): separate CPU and GPU allocators hand out physical memory blocks.
- **Worker 0 … Worker N−1** (right column): each holds a **Cache Engine** + a **Model Shard** (one model partition per GPU).
- *Data flow:* Scheduler → all Workers (dispatch); Scheduler → KV Cache Manager → Block Allocators (memory bookkeeping); KV Cache Manager ↔ Workers (KV block management instructions).

**Key Technical Takeaway (≈110 words):**
vLLM decouples the centralized **scheduler/KV-cache manager** from the per-GPU **worker shards**, so the cache can be managed as paged, non-contiguous blocks across distributed devices. By pushing paging decisions to a single controller while keeping compute local, the system achieves near-zero KV-cache waste and flexible memory sharing across requests — addressing fragmentation and pre-allocation pain points that prior LLM serving systems could not solve, without slowing down token generation.

**Caption (verbatim):**
*Figure 4. vLLM system overview.*

### Figure 6 (p.6) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p06.png]]
> [!quote] caption
> Block table translation in vLLM. divides it into physical KV blocks (this is also done on CPU RAM for swapping; see §4.5). The KV block manager also maintains block tables—the mapping between logical and physical KV blocks of each request. Each block table entry records the corresponding physical blocks of a logical block and the number of filled positions. Separating logical and physical KV block

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 7)**

**Architecture/Components:**
- **Two requests** (A: "Four score and seven years ago our fathers brought"; B: "It was the best of times") each shown with their own **Logical KV blocks** (contiguous, per-request view).
- A shared **Physical KV blocks** pool (9 blocks) on GPU DRAM, where tokens from both requests are interleaved non-contiguously.
- **Block tables** (arrows) translate each request's logical block indices to the corresponding physical block indices.

**Data flow:** Request → logical block assignment → block table lookup → non-contiguous physical KV blocks in GPU → PagedAttention kernel reads via block table.

**Key takeaway:** By virtualizing KV cache through block tables, vLLM decouples logical block ordering from physical placement, allowing multiple requests to share GPU memory without contiguity—eliminating internal fragmentation and boosting batching throughput.

**Caption (verbatim):**
*Figure 7. Storing the KV cache of two requests at the same time in vLLM.*

### Figure 7 (p.6) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p06.png]]
> [!quote] caption
> Storing the KV cache of two requests at the same time in vLLM. requests and the latest tokens for generation phase requests) as one sequence and feeds it into the LLM. During LLM’s computation, vLLM uses the PagedAttention kernel to access the previous KV cache stored in the form of logical KV blocks and saves the newly generated KV cache into the physical KV blocks. Storing multiple tokens within

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 7)**

**Architecture/Components:**
- **Two requests** (A: "Four score and seven years ago our fathers brought"; B: "It was the best of times") each shown with their own **Logical KV blocks** (contiguous, per-request view).
- A shared **Physical KV blocks** pool (9 blocks) on GPU DRAM, where tokens from both requests are interleaved non-contiguously.
- **Block tables** (arrows) translate each request's logical block indices to the corresponding physical block indices.

**Data flow:** Request → logical block assignment → block table lookup → non-contiguous physical KV blocks in GPU → PagedAttention kernel reads via block table.

**Key takeaway:** By virtualizing KV cache through block tables, vLLM decouples logical block ordering from physical placement, allowing multiple requests to share GPU memory without contiguity—eliminating internal fragmentation and boosting batching throughput.

**Caption (verbatim):**
*Figure 7. Storing the KV cache of two requests at the same time in vLLM.*

### Figure 8 (p.7) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p07.png]]
> [!quote] caption
> Parallel sampling example. generates a single sequence. In the remainder of this paper, we assume the more general case in which a request gener- ates multiple sequences. In parallel sampling, one request includes multiple samples sharing the same input prompt, allowing the KV cache of the prompt to be shared as well. Via its PagedAttention and paged memory management, vLLM can realize this sharin

> [!tip] 技术解读（多模态）
> ## Main Figure: Figure 9 — Beam Search Example

**Architecture / Data Flow:** Four beam candidates (0–3) begin from a shared prompt block (Block 0). After the first iteration, candidates 0–2 share Blocks 1–3 and diverge at Block 4. At the dotted line (next iteration), only candidates 1 and 2 produce top-k successors, so their blocks (1, 3) remain shared; Blocks 2, 4, 5, and 8 are freed (✗) and new Blocks 9–12 are allocated. Final sharing: all share Blocks 0, 1, 3; candidates 0/1 share Block 6; candidates 2/3 share Block 7.

**Key Technical Takeaway:** vLLM enables *physical block sharing with reference counting* across beam candidates, invoking copy-on-write only when a new token writes into an existing shared block. This reduces the large KV-cache copies (e.g., candidate 3 copying from candidate 2) that plague prior systems to copying a single block — a substantial memory and bandwidth savings.

**Caption (verbatim):** *Figure 9.* Beam search example.

### Figure 9 (p.7) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p07.png]]
> [!quote] caption
> Beam search example. sample space. The algorithm relies on the beam width pa- rameter 𝑘, which determines the number of top candidates retained at every step. During decoding, beam search ex- pands each candidate sequence in the beam by considering all possible tokens, computes their respective probabilities us- ing the LLM, and retains the top-𝑘most probable sequences out of 𝑘· |𝑉| candidates, wh

> [!tip] 技术解读（多模态）
> ## Main Figure: Figure 9 — Beam Search Example

**Architecture / Data Flow:** Four beam candidates (0–3) begin from a shared prompt block (Block 0). After the first iteration, candidates 0–2 share Blocks 1–3 and diverge at Block 4. At the dotted line (next iteration), only candidates 1 and 2 produce top-k successors, so their blocks (1, 3) remain shared; Blocks 2, 4, 5, and 8 are freed (✗) and new Blocks 9–12 are allocated. Final sharing: all share Blocks 0, 1, 3; candidates 0/1 share Block 6; candidates 2/3 share Block 7.

**Key Technical Takeaway:** vLLM enables *physical block sharing with reference counting* across beam candidates, invoking copy-on-write only when a new token writes into an existing shared block. This reduces the large KV-cache copies (e.g., candidate 3 copying from candidate 2) that plague prior systems to copying a single block — a substantial memory and bandwidth savings.

**Caption (verbatim):** *Figure 9.* Beam search example.

### Figure 10 (p.8) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p08.png]]
> [!quote] caption
> Shared prompt example for machine translation.

> [!tip] 技术解读（多模态）
> **Figure 10 — Shared prompt for machine translation**

**Architecture / Components:**
- A common **Shared prefix** (yellow box) holding a few-shot translation template: *"Translate English to French: 'sea otter' => 'loutre de mer', 'peppermint' => 'menthe poivrée', 'plush girafe' => 'girafe en peluche'"*
- Two independent requests (**Sequence A**, **Sequence B**) that each append a **Task input** (e.g., `"<cheese>"`, `"I love you"`) to that shared prefix.
- Each sequence is decoded independently, producing a **Sequence LLM output** (`"fromage"`, `"Je t'aime"`).

**Data flow:** identical prefix → per-request task input appended → per-request forward pass → independent outputs.

**Key technical takeaway:** Because user prompts frequently share long prefixes, the LLM service provider can pre-compute and cache the KV cache of the shared prefix once, then only run the prompt-phase on each request's unique suffix—reducing redundant computation analogous to OS shared-library mapping.

**Caption (verbatim):**
> Figure 10. Shared prompt example for machine translation. The examples are adopted from [5].

### Figure 11 (p.9) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p09.png]]
> [!quote] caption
> Input and output length distributions of the (a)

> [!tip] 技术解读（多模态）
> **Figure 11 Description**

**Components:** Two side-by-side density histograms comparing token-length distributions across two datasets, each plotting Input tokens (blue) and Output tokens (orange) against # Tokens (0–2000) on the x-axis and Density (×10⁻²) on the y-axis.

**Data flow/structure:** Panel (a) ShareGPT uses a y-scale up to ~2×10⁻², with reported means of 161.31 (input) and 337.99 (output). Panel (b) Alpaca uses a y-scale up to ~8×10⁻², with means of 19.31 (input) and 58.45 (output). Both distributions are heavily right-skewed, with most sequences short but long tails.

**Key takeaway:** ShareGPT sequences are an order of magnitude longer than Alpaca's (≈10× input, ≈6× output), motivating vLLM's PagedAttention to handle variable, sometimes very long context lengths without memory waste.

**Caption (verbatim):** "Figure 11. Input and output length distributions of the (a) ShareGPT and (b) Alpaca datasets."

### Figure 12 (p.10) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p10.png]]
> [!quote] caption
> Single sequence generation with OPT models on the ShareGPT and Alpaca dataset

> [!tip] 技术解读（多模态）
> **Figure 12 Description:**

The figure is a 2×3 grid of line plots comparing five LLM serving systems (FasterTransformer, Orca-Max, Orca-Pow2, Orca-Oracle, and vLLM) on a common axis. The top row evaluates three OPT model sizes (13B/1 GPU, 66B/4 GPUs, 175B/8 GPUs) on the ShareGPT workload; the bottom row repeats the same three configurations on the Alpaca workload. Each subplot plots **normalized latency (s/token, y-axis: 0–1.0)** against **request arrival rate (req/s, x-axis)**, so every curve traces how latency degrades as load increases. Data flows left→right as load grows, and vertical saturation points mark the throughput ceiling of each system.

**Key takeaway:** Across all six panels, the blue vLLM curve consistently extends furthest right before its latency climbs — sustaining near-baseline latency at request rates that cause Orca variants (green/orange/red) and FasterTransformer (gray) to saturate, demonstrating vLLM's superior scheduling/batching efficiency for both small and large OPT models on long-context (ShareGPT) and shorter-context (Alpaca) traces.

**Caption (verbatim):**
"Figure 12. Single sequence generation with OPT models on the ShareGPT and Alpaca dataset"

### Figure 13 (p.10) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p10.png]]
> [!quote] caption
> Average number of batched requests when serv- ing OPT-13B for the ShareGPT (2 reqs/s) and Alpaca (30 reqs/s) traces.

> [!tip] 技术解读（多模态）
> **Figure 12 Description:**

The figure is a 2×3 grid of line plots comparing five LLM serving systems (FasterTransformer, Orca-Max, Orca-Pow2, Orca-Oracle, and vLLM) on a common axis. The top row evaluates three OPT model sizes (13B/1 GPU, 66B/4 GPUs, 175B/8 GPUs) on the ShareGPT workload; the bottom row repeats the same three configurations on the Alpaca workload. Each subplot plots **normalized latency (s/token, y-axis: 0–1.0)** against **request arrival rate (req/s, x-axis)**, so every curve traces how latency degrades as load increases. Data flows left→right as load grows, and vertical saturation points mark the throughput ceiling of each system.

**Key takeaway:** Across all six panels, the blue vLLM curve consistently extends furthest right before its latency climbs — sustaining near-baseline latency at request rates that cause Orca variants (green/orange/red) and FasterTransformer (gray) to saturate, demonstrating vLLM's superior scheduling/batching efficiency for both small and large OPT models on long-context (ShareGPT) and shorter-context (Alpaca) traces.

**Caption (verbatim):**
"Figure 12. Single sequence generation with OPT models on the ShareGPT and Alpaca dataset"

### Figure 14 (p.11) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p11.png]]
> [!quote] caption
> Parallel generation and beam search with OPT-13B on the Alpaca dataset.

> [!tip] 技术解读（多模态）
> ## Main Figure (Figure 14)

**Architecture/Components:**
- A 2×3 grid of line plots evaluating LLM serving systems on OPT-13B with the Alpaca dataset.
- **Top row (a–c):** Parallel generation at parallel sizes 2, 4, 6.
- **Bottom row (d–f):** Beam search at beam widths 2, 4, 6.
- **Y-axis:** Normalized latency (s/token), 0–1.0; **X-axis:** Request rate (req/s).
- **Four systems compared via colored curves:** Orca (Max) – red ✕; Orca (Pow2) – orange ▲; Orca (Oracle) – green ■; vLLM – blue ●.

**Data flow / interpretation:** Each curve stays near-zero latency until saturation, then spikes sharply upward. The knee-point of each curve marks the maximum sustainable request rate before queueing explodes.

**Key technical takeaway:** vLLM consistently sustains the highest request rates across all configurations, and its lead over Orca baselines widens as parallelism/beam-width grows—evidence that PagedAttention-based KV-cache sharing scales with multi-sequence generation, delivering up to 2.3× the throughput of Orca (Oracle) at beam-width 6.

## Caption (verbatim)

**Figure 14.** Parallel generation and beam search with OPT-13B on the Alpaca dataset.

### Figure 15 (p.11) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p11.png]]
> [!quote] caption
> Average amount of memory saving from sharing KV blocks, when serving OPT-13B for the Alpaca trace.

> [!tip] 技术解读（多模态）
> ## Main Figure (Figure 14)

**Architecture/Components:**
- A 2×3 grid of line plots evaluating LLM serving systems on OPT-13B with the Alpaca dataset.
- **Top row (a–c):** Parallel generation at parallel sizes 2, 4, 6.
- **Bottom row (d–f):** Beam search at beam widths 2, 4, 6.
- **Y-axis:** Normalized latency (s/token), 0–1.0; **X-axis:** Request rate (req/s).
- **Four systems compared via colored curves:** Orca (Max) – red ✕; Orca (Pow2) – orange ▲; Orca (Oracle) – green ■; vLLM – blue ●.

**Data flow / interpretation:** Each curve stays near-zero latency until saturation, then spikes sharply upward. The knee-point of each curve marks the maximum sustainable request rate before queueing explodes.

**Key technical takeaway:** vLLM consistently sustains the highest request rates across all configurations, and its lead over Orca baselines widens as parallelism/beam-width grows—evidence that PagedAttention-based KV-cache sharing scales with multi-sequence generation, delivering up to 2.3× the throughput of Orca (Oracle) at beam-width 6.

## Caption (verbatim)

**Figure 14.** Parallel generation and beam search with OPT-13B on the Alpaca dataset.

### Figure 16 (p.12) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p12.png]]
> [!quote] caption
> Translation workload where the input prompts share a common prefix. The prefix includes (a) 1 example with 80 tokens or (b) 5 examples with 341 tokens.

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 18 — Ablation Experiments):**

The figure contains two subplots:

- **(a) Kernel latency (μs) vs. context length (64→256):** Compares four lines — vLLM (bs=8/32) and FasterTransformer (bs=8/32). vLLM shows 20–26% higher per-kernel latency than FT, but still wins end-to-end.
- **(b) Normalized latency (s/token) vs. block size (1→256):** Two traces (ShareGPT, Alpaca). Both form a U-shape; best region around block size 16–32. Alpaca degrades sharply beyond 32 because short sequences suffer fragmentation, while ShareGPT tolerates larger blocks.

**Data flow narrative:** tokens → PagedAttention block table → GPU KV-cache reads → attention kernel → output latency.

**Key takeaway:** PagedAttention adds ~20–26% kernel overhead over FasterTransformer, yet vLLM still outperforms it end-to-end, and a block size of 16 is the sweet spot — large enough to saturate GPU parallelism, small enough to keep internal fragmentation low.

**Caption (verbatim):** "Figure 18. Ablation experiments."

### Figure 17 (p.12) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p12.png]]
> [!quote] caption
> Performance on chatbot workload.

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 18 — Ablation Experiments):**

The figure contains two subplots:

- **(a) Kernel latency (μs) vs. context length (64→256):** Compares four lines — vLLM (bs=8/32) and FasterTransformer (bs=8/32). vLLM shows 20–26% higher per-kernel latency than FT, but still wins end-to-end.
- **(b) Normalized latency (s/token) vs. block size (1→256):** Two traces (ShareGPT, Alpaca). Both form a U-shape; best region around block size 16–32. Alpaca degrades sharply beyond 32 because short sequences suffer fragmentation, while ShareGPT tolerates larger blocks.

**Data flow narrative:** tokens → PagedAttention block table → GPU KV-cache reads → attention kernel → output latency.

**Key takeaway:** PagedAttention adds ~20–26% kernel overhead over FasterTransformer, yet vLLM still outperforms it end-to-end, and a block size of 16 is the sweet spot — large enough to saturate GPU parallelism, small enough to keep internal fragmentation low.

**Caption (verbatim):** "Figure 18. Ablation experiments."

### Figure 18 (p.12) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p12.png]]
> [!quote] caption
> Ablation experiments. handle the long prompts, as PagedAttention resolves the problem of memory fragmentation and reservation. 7

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 18 — Ablation Experiments):**

The figure contains two subplots:

- **(a) Kernel latency (μs) vs. context length (64→256):** Compares four lines — vLLM (bs=8/32) and FasterTransformer (bs=8/32). vLLM shows 20–26% higher per-kernel latency than FT, but still wins end-to-end.
- **(b) Normalized latency (s/token) vs. block size (1→256):** Two traces (ShareGPT, Alpaca). Both form a U-shape; best region around block size 16–32. Alpaca degrades sharply beyond 32 because short sequences suffer fragmentation, while ShareGPT tolerates larger blocks.

**Data flow narrative:** tokens → PagedAttention block table → GPU KV-cache reads → attention kernel → output latency.

**Key takeaway:** PagedAttention adds ~20–26% kernel overhead over FasterTransformer, yet vLLM still outperforms it end-to-end, and a block size of 16 is the sweet spot — large enough to saturate GPU parallelism, small enough to keep internal fragmentation low.

**Caption (verbatim):** "Figure 18. Ablation experiments."

### Figure 19 (p.13) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p13.png]]
> [!quote] caption
> (a) Overhead of recomputation and swapping for different block sizes. (b) Performance when serving OPT-13B with the ShareGPT traces at the same request rate.

> [!tip] 技术解读（多模态）
> # Figure 19 Description

**Architecture/Components/Data Flow:**
The figure presents two side-by-side line plots comparing two KV-cache recovery mechanisms — **Recomputation** vs. **Swapping** — across varying block sizes:

- **Plot (a) Microbenchmark:** Plots *Time (ms)* vs. *Block size* (1 → 256), with four curves: *Recompute, Swap in, Swap out, Swap in + out*. Swap-in latency is highest at small block sizes (≈140 ms) and drops steeply as block size grows, converging toward recompute (~20 ms).
- **Plot (b) End-to-end performance:** Plots *Normalized latency (s/token)* vs. *Block size* for serving OPT-13B on ShareGPT traces. Both curves form a U-shape, dipping to a minimum around block size 16–64.

**Key Technical Takeaway (≤120 words):**
Recomputation and swapping exhibit complementary regimes: swapping suffers severe PCIe-bandwidth overhead at small block sizes due to many small CPU↔GPU transfers, while recomputation stays roughly constant because it bypasses KV blocks entirely. Recomputation is preferred when block size is small; swapping wins at large block sizes (though recomputation never exceeds ~20% of swapping's latency). For medium block sizes (16–64), both mechanisms yield comparable end-to-end latency — providing a tunable design knob for vLLM's recovery policy.

**Caption (verbatim):**
"Figure 19. (a) Overhead of recomputation and swapping for different block sizes. (b) Performance when serving OPT-13B with the ShareGPT traces at the same request rate."

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
P(x) = P(x_1) \cdot P(x_2\mid x_1) \cdots P(x_n \mid x_1, \ldots, x_{n-1}).
$$

$$
q_i = W_q x_i, \ k_i = W_k x_i, \ v_i = W_v x_i.
$$

$$
a_{ij} = \frac{\exp(q_i^\top k_j / \sqrt{d})}{\sum_{t=1}^{i}\exp(q_i^\top k_t / \sqrt{d})}, \ o_i = \sum_{j=1}^{i} a_{ij} v_j.
$$

$$
A_{ij} = \frac{\exp(q_i^\top K_j / \sqrt{d})}{\sum_{t=1}^{\lceil i/B \rceil}\exp(q_i^\top K_t\mathbf{1} / \sqrt{d})}, \ o_i = \sum_{j=1}^{\lceil i/B \rceil} V_j A_{ij}^\top,
$$

## 技术点深读（DEEP）

![[deep/efficient-memory-management-for-large-language-model-serving-with-pagedattention]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/efficient-memory-management-for-large-language-model-serving-with-pagedattention.txt`（82023 字符）供引用检索。