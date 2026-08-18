---
paper_num: "44"
title: "Efficiently Serving Large Multimodal Models Using EPD Disaggregation"
authors: "Efficiently Serving Large Multimodal Models Using EPD Disaggregation Gursimran Singh 1 Xinglu Wang 2 Yifan Hu 1 Timothy Yu 1 Linzi Xing 1 Wei Jiang 3 Zhefeng Wang 3 Xiaolong Bai 3 Yi Li 3 Ying Xiong 1 Yong Zhang 1 Zhenan"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2501.05460"
pdf: "papers/efficiently-serving-large-multimodal-models-using-epd-disaggregation.pdf"
slug: "efficiently-serving-large-multimodal-models-using-epd-disaggregation"
tags: [multimodal, disaggregated-serving]
---

# Efficiently Serving Large Multimodal Models Using EPD Disaggregation

> [!abstract] 摘要（原文）
> 1\. 💡 本文提出了一种新颖的Encode-Prefill-Decode (EPD) Disaggregation框架，通过将LMM推理的编码、Prefill和解码阶段解耦到专用资源上，解决了现有LMM服务系统中的性能瓶颈。 2. 🚀 该框架引入了多媒体令牌缓存、Intra-Request Parallelization (IRP)、优化资源分配和动态角色切换等创新机制，以提高LMM的服务效率。 3. 📈 实验结果表明，与现有系统相比，EPD显著提升了内存效率（高达15倍）、批处理大小（高达22倍）、每请求图像数量以及SLO达成率，并大幅降低了Time to First Token (TTFT)。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Efficiently Serving Large Multimodal Models Using EPD Disaggregation Gursimran Singh 1 Xinglu Wang 2 Yifan Hu 1 Timothy Yu 1 Linzi Xing 1 Wei Jiang 3 Zhefeng Wang 3 Xiaolong Bai 3 Yi Li 3 Ying Xiong 1 Yong Zhang 1 Zhenan
- **arXiv**: https://arxiv.org/abs/2501.05460
- **本地 PDF**: `papers/efficiently-serving-large-multimodal-models-using-epd-disaggregation.pdf`
- **页数**: 17

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p01.png]]
> [!quote] caption
> Aggregated (top) vs. disaggregated (bottom) sys- tem architectures. In the aggregated setup, the encoder (E) and LLM share the same GPUs, leading to interference be- tween encode and prefill stages (e.g., LLM-4 delays E5).

> [!tip] 技术解读（多模态）
> **Figure 1 Description (architecture/components/data flow + key takeaway):**

The figure contrasts two serving topologies across 4 GPU rows. **Aggregated (top, DP=4):** each row holds a tensor-parallel (TP) LLM shard (LLM¹–LLM⁴); a fifth encoder stage E5 is squeezed into row 4 alongside LLM⁴, so prefill of one LLM stalls the encoder (visible as E5 pushed right after LLM⁴). **Disaggregated (bottom, P=3, E=1):** E5 is pinned to its own dedicated GPU row at the top, while rows 2–4 host only LLM¹/LLM⁴, LLM²/LLM⁵, LLM³ respectively — eliminating cross-stage contention.

**Key takeaway:** Decoupling the encoder onto a separate GPU pool removes prefill-induced encoder stalls, the dominant source of TTFT inflation in aggregated multimodal serving. (~95 words)

**Caption (verbatim):**

"Figure 1: Aggregated (top) vs. disaggregated (bottom) system architectures. In the aggregated setup, the encoder (E) and LLM share the same GPUs, leading to interference between encode and prefill stages (e.g., LLM-4 delays E5). Disaggregation isolates these stages across GPUs, reducing contention and improving utilization. This separation enables better performance under multimodal workloads, addressing key limitations of existing systems."

### Figure 2 (p.2) ⭐深度解读
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p02.png]]
> [!quote] caption
> Impact of disaggregation on supported batch size and number of images per request for the MiniCPM- V 2.6 model. Removing the LLM from the GPU signifi- cantly increases capacity, enabling larger batches and higher- resolution inputs. This demonstrates the memory efficiency benefits of disaggregation. representations. This stage is computationally intensive, especially for high-resolution or complex

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 2) Description:**

The figure is a grouped bar chart comparing **Max Batch Size** (y-axis, 0–~48) against **#Images/Request** (x-axis: 1, 3, 5, 15, 20, 30, 40) for two configurations on the MiniCPM-V 2.6 model:
- **Aggregated** (green) — encode+prefill+decode on the same GPUs
- **Disaggregated** (blue) — LLM and KV-cache removed

At 1 image/request, disaggregated reaches ~48 vs. ~6 for aggregated; at 3 images, ~16 vs. ~2. At ≥15 images/request, the aggregated setup goes OOM (zero batch), while disaggregated still supports small but nonzero batches.

**Key takeaway:** Disaggregating the LLM from the vision encoder unlocks an order-of-magnitude larger batch capacity (up to ~15×) and avoids OOM on multi-image requests, directly translating to better TTFT/TPOT SLO compliance.

**Caption (verbatim):**

> Figure 2: Impact of disaggregation on supported batch size and number of images per request for the MiniCPM-V 2.6 model. Removing the LLM from the GPU significantly increases capacity, enabling larger batches and higher-resolution inputs. This demonstrates the memory efficiency benefits of disaggregation.

### Figure 3 (p.3) ⭐深度解读
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p03.png]]
> [!quote] caption
> The inference pipeline of EPD Disaggregation. stages—EP-migration and PD-migration—handle the trans- fer of data from encoding to prefill and from prefill to de- code, respectively. We denote the input text prompt as ip, multimodal data as im, and the output text as o. The steps are as follows:

> [!tip] 技术解读（多模态）
> **Architecture/Components/Data Flow**

The figure depicts the **EPD (Encode–Prefill–Decode) Disaggregation** inference pipeline, splitting LMM serving across three independent GPU pools:

- **E GPUs (yellow)** — host the *Encoding Queue* and *Encoding Stage*, feeding tokens into an *EP Bridge Queue*.
- **P GPUs (orange)** — host the *Prefill Queue* and *Prefill Stage*, feeding into a *PD Bridge Queue*.
- **D GPUs (green)** — host the *Decode Queue* and *Decode Stage*.

Data flows left→right: multimodal inputs are encoded on E GPUs, migrated to P GPUs via **EP-migration** (transferring token embeddings), then migrated to D GPUs via **PD-migration** (transferring the KV cache + first output token) for decoding. Each pool runs in data-parallel mode with its own bridge queue buffering cross-pool transfers.

**Key technical takeaway:** Disaggregating encoding from prefill (beyond prior PD-disaggregation systems like SplitWise/Mooncake) enables parallel frame encoding for long-video multimodal workloads, eliminating the encoding bottleneck tightly coupled with prefill and unlocking flexible, per-stage SLO-driven scaling. (~80 words)

**Caption (verbatim):**

*Figure 3: The inference pipeline of EPD Disaggregation.*

### Figure 4 (p.4) ⭐深度解读
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p04.png]]
> [!quote] caption
> System architecture of the proposed EPD Disaggregated Inference. the data associated with the request. In the decoding stage, workers load the LLM weights for decoding tasks and use the KV cache.

> [!tip] 技术解读（多模态）
> **Main Figure Description (architecture/components/data flow):**

The figure depicts an **EPD Disaggregated Inference** architecture with three pipeline stages arranged left-to-right: an **Encoding Instance** (yellow) holding Encoder Weights + MM Cache, a **Prefill Instance** (orange) holding LLM Weights + MM/KV Caches, and a **Decoding Instance** (green) holding LLM Weights + KV Cache. Each instance has its own Scheduler and Block Manager. A central **Scheduler/Load Balancer** assigns incoming multi-media requests, while a **Monitoring & Dynamic Role Switching** module oversees queues (EP Bridge Queue, PD Bridge Queue) and triggers instance migration (e.g., "Migrate 1 D instance to P"). Data flows via **Async Transfer** (§3.2.1) between stages over high-bandwidth links; parallelism labels (TP/PP, IRP, DP) appear beneath each instance.

**Key Technical Takeaway:**

Decoupling LMM inference into three independently scalable stages—encoding, prefill, decoding—lets the system apply stage-specific parallelism (data-parallel encoding, tensor/pipeline-parallel prefill/decoding) while asynchronous bridge queues decouple cache transfers, enabling elastic role reallocation under shifting multimodal workloads.

**Caption (verbatim):**

Figure 4: System architecture of the proposed EPD Disaggregated Inference.

### Figure 5 (p.6) ⭐深度解读
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p06.png]]
> [!quote] caption
> SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively. The top and bottom rows show results for 2 and 4 images per request. EPD consistently outperforms all baselines across configurations. question answering items that span diverse video lengths, topic

> [!tip] 技术解读（多模态）
> **Figure Description**

The figure is a 2×3 grid of line plots comparing SLO attainment (%) versus request rate (req/s) across three LMM serving systems: **EPD** (blue), **DistServe** (green), and **vLLM** (red). Columns correspond to three models of increasing scale — MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B — while rows contrast workload difficulty with 2 images/request (top) versus 4 images/request (bottom). Each plot includes a horizontal dashed reference line marking the 90% SLO target and vertical dashed lines indicating each system's goodput threshold.

**Key Technical Takeaway:** EPD consistently sustains >90% SLO attainment at substantially higher request rates than both baselines across all model scales and image counts, whereas DistServe and vLLM collapse below ~10% SLO due to cross-stage interference that worsens with model size (8B→26B) and heavier prefill workloads (2→4 images).

**Caption (verbatim):**

Figure 5: SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively. The top and bottom rows show results for 2 and 4 images per request. EPD consistently outperforms all baselines across configurations.

### Figure 6 (p.7) ⭐深度解读
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]]
> [!quote] caption
> Distribution of TTFT (Y-axis) across varying numbers of images per request (X-axis) for (a) MiniCPM-V 2.6, (b)

> [!tip] 技术解读（多模态）
> **Figure 6 — Description**

Figure 6 comprises three side-by-side box-plot subplots comparing **Time-to-First-Token (TTFT, seconds)** versus **#Images per Request** for two serving frameworks—**EPD (blue)** vs. **DistServe (green)**—across three model scales: (a) MiniCPMv-2.6, (b) InternVL2-8B, and (c) InternVL2-26B. Each subplot displays a small grid of box plots (with whiskers and medians) at discrete image counts, showing the latency distribution. Components compared: per-request image count (X), TTFT distribution (Y), serving system (color).

**Key Technical Takeaway (≤120 words):**
By exploiting intra-request parallelization across the encoder and prefill stages, EPD keeps its TTFT boxes markedly lower than DistServe's in every subplot, and the gap widens as input size grows—evidence that the disaggregation strategy scales with multimodal payload size. Quantitatively, EPD cuts mean TTFT by up to **71.9 % (MiniCPM-V 2.6)**, **32.8 % (InternVL2-8B)**, and **44.9 % (InternVL2-26B)** relative to DistServe, making it the only system tested that maintains sub-second first-token latency even at 16 images/request.

**Caption (verbatim):**
"Figure 6: Distribution of TTFT (Y-axis) across varying numbers of images per request (X-axis) for (a) MiniCPM-V 2.6, (b) InternVL2-8B, and (c) InternVL2-26B. Each plot illustrates the latency behavior under increasing input sizes."

### Figure 7 (p.7) ⭐深度解读
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]]
> [!quote] caption
> SLO attainment (↑) versus request rate on the

> [!tip] 技术解读（多模态）
> **Figure 6 — Description**

Figure 6 comprises three side-by-side box-plot subplots comparing **Time-to-First-Token (TTFT, seconds)** versus **#Images per Request** for two serving frameworks—**EPD (blue)** vs. **DistServe (green)**—across three model scales: (a) MiniCPMv-2.6, (b) InternVL2-8B, and (c) InternVL2-26B. Each subplot displays a small grid of box plots (with whiskers and medians) at discrete image counts, showing the latency distribution. Components compared: per-request image count (X), TTFT distribution (Y), serving system (color).

**Key Technical Takeaway (≤120 words):**
By exploiting intra-request parallelization across the encoder and prefill stages, EPD keeps its TTFT boxes markedly lower than DistServe's in every subplot, and the gap widens as input size grows—evidence that the disaggregation strategy scales with multimodal payload size. Quantitatively, EPD cuts mean TTFT by up to **71.9 % (MiniCPM-V 2.6)**, **32.8 % (InternVL2-8B)**, and **44.9 % (InternVL2-26B)** relative to DistServe, making it the only system tested that maintains sub-second first-token latency even at 16 images/request.

**Caption (verbatim):**
"Figure 6: Distribution of TTFT (Y-axis) across varying numbers of images per request (X-axis) for (a) MiniCPM-V 2.6, (b) InternVL2-8B, and (c) InternVL2-26B. Each plot illustrates the latency behavior under increasing input sizes."

### Figure 8 (p.7) ⭐深度解读
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]]
> [!quote] caption
> As seen, EPD consistently outperforms vLLM and Dist-

> [!tip] 技术解读（多模态）
> **Figure 6 — Description**

Figure 6 comprises three side-by-side box-plot subplots comparing **Time-to-First-Token (TTFT, seconds)** versus **#Images per Request** for two serving frameworks—**EPD (blue)** vs. **DistServe (green)**—across three model scales: (a) MiniCPMv-2.6, (b) InternVL2-8B, and (c) InternVL2-26B. Each subplot displays a small grid of box plots (with whiskers and medians) at discrete image counts, showing the latency distribution. Components compared: per-request image count (X), TTFT distribution (Y), serving system (color).

**Key Technical Takeaway (≤120 words):**
By exploiting intra-request parallelization across the encoder and prefill stages, EPD keeps its TTFT boxes markedly lower than DistServe's in every subplot, and the gap widens as input size grows—evidence that the disaggregation strategy scales with multimodal payload size. Quantitatively, EPD cuts mean TTFT by up to **71.9 % (MiniCPM-V 2.6)**, **32.8 % (InternVL2-8B)**, and **44.9 % (InternVL2-26B)** relative to DistServe, making it the only system tested that maintains sub-second first-token latency even at 16 images/request.

**Caption (verbatim):**
"Figure 6: Distribution of TTFT (Y-axis) across varying numbers of images per request (X-axis) for (a) MiniCPM-V 2.6, (b) InternVL2-8B, and (c) InternVL2-26B. Each plot illustrates the latency behavior under increasing input sizes."

### Figure 9 (p.9) ⭐深度解读
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p09.png]]
> [!quote] caption
> As shown, EPD is the only configuration that achieves the SLO requirements, while the other baselines fail to meet the SLOs entirely, even at low request rates.

> [!tip] 技术解读（多模态）
> **Figure 9 — Description:**

**Architecture/Components/Data Flow:** A 2-D line chart comparing SLO attainment (%) on the y-axis (0–100) versus Request Rate (req/s) on the x-axis (~0.005–0.035) for three serving systems on NPUs. Three series are plotted: **EPD** (blue line with circles), **DistServe** (green line with diamonds), and **vLLM** (red line with triangles). A horizontal dashed reference line marks the SLO target (~95%), and a vertical dashed line indicates a low-rate threshold (~0.01 req/s). EPD starts near 100% and gradually degrades to ~20% as request rate increases, while DistServe and vLLM remain flat near 0%.

**Key Technical Takeaway (≤120 words):** EPD is the **only** configuration that achieves positive SLO attainment under the strict TTFT ≤ 8.5s / TPOT ≤ 0.12s constraints on the InternVL2-8B LMM with a heavy encoding workload (8 × 4032×3024 images/request). Baseline disaggregated systems (DistServe, vLLM) fail to meet SLOs entirely, even at very low request rates, demonstrating that **EPD's encoding–prefill–decoding disaggregation is essential** for serving high-resolution multimodal workloads on memory-constrained NPUs — a regime where encoding dominates and traditional GPU-style disaggregation benefits (~24.4%) amplify to ~35.2% TTFT improvement.

**Caption (verbatim):**
> Figure 9: SLO attainment (↑) on NPUs under varying request rates for a synthetic workload using the InternVL2-8B model. EPD maintains positive SLO attainment under strict TTFT constraints, while baselines fail to meet the criteria.

### Figure 10 (p.13) ⭐深度解读
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]]
> [!quote] caption
> Left: Impact of varying the number of encoding workers in the EPD method. The notation xEyP denotes a configuration with x encoder and y prefill workers. The DistServe method uses a fixed 7P configuration, assigning 7 workers to handle both encoding and prefill steps. Middle: Effect of the number of images per request on end-to-end throughput. Right: Sensitivity to encoding and prefill batch sizes

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 11) — Architecture/Components/Data Flow:**

A 2×3 grid of subplots comparing SLO attainment (%) versus request rate (req/s) across three LMMs — MiniCPMv-2.6 (a), InternVL2-8B (b), and InternVL2-26B (c) — with the top and bottom rows representing 6 and 8 images per request, respectively. Three serving methods are overlaid in each subplot: EPD (blue), DistServe (green), and vLLM (red). Vertical dashed markers indicate the maximum sustainable request rate at the 90% SLO threshold.

**Key Technical Takeaway:** EPD sustains near-100% SLO attainment at substantially higher request rates than DistServe and vLLM across every model scale and image count, confirming that encoder–prefill–decode disaggregation scales gracefully while the baselines collapse under modest load due to encoder-side compute bottlenecks.

**Caption (verbatim):**

"Figure 11: SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively. The top and bottom rows show results for 6 and 8 images per request. EPD consistently outperforms all baselines, demonstrating robust performance as image count increases."

### Figure 11 (p.13) ⭐深度解读
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]]
> [!quote] caption
> SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively. The top and bottom rows show results for 6 and 8 images per request. EPD consistently outperforms all baselines, demonstrating robust performance as image count increases.. content of this image?”),

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 11) — Architecture/Components/Data Flow:**

A 2×3 grid of subplots comparing SLO attainment (%) versus request rate (req/s) across three LMMs — MiniCPMv-2.6 (a), InternVL2-8B (b), and InternVL2-26B (c) — with the top and bottom rows representing 6 and 8 images per request, respectively. Three serving methods are overlaid in each subplot: EPD (blue), DistServe (green), and vLLM (red). Vertical dashed markers indicate the maximum sustainable request rate at the 90% SLO threshold.

**Key Technical Takeaway:** EPD sustains near-100% SLO attainment at substantially higher request rates than DistServe and vLLM across every model scale and image count, confirming that encoder–prefill–decode disaggregation scales gracefully while the baselines collapse under modest load due to encoder-side compute bottlenecks.

**Caption (verbatim):**

"Figure 11: SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively. The top and bottom rows show results for 6 and 8 images per request. EPD consistently outperforms all baselines, demonstrating robust performance as image count increases."

### Figure 12 (p.16) ⭐深度解读
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p16.png]]
> [!quote] caption
> Breakdown of latency for encode and prefill stages using the InternVL2-8B model across varying numbers of images per request. Subfigures (a) and (b) show results on GPU and NPU, respectively. Light green denotes encode latency and light blue indicates prefill latency. NPUs demonstrate distinct latency characteristics compared to GPUs as input size increases. E.3. SLO Criteria

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**
Figure 12 presents two stacked bar charts comparing the latency breakdown (%) of encode (green) vs. prefill (blue) stages for the InternVL2-8B model as the number of images per request (#I/R) grows from 1 to 8. Subfigure (a) reports GPU measurements; subfigure (b) reports NPU measurements. The encode share shrinks with larger inputs while prefill grows, but the trend differs between hardware. On GPU at #I/R=8, encode ≈25%/prefill ≈75%, whereas NPU retains ≈40% encode. **Key takeaway:** NPUs exhibit a 10–20% higher encode-to-prefill latency ratio than GPUs across multimodal workloads, motivating EPD disaggregation since encoding and prefilling have asymmetric resource requirements that benefit from being separated on NPUs.

**Caption (verbatim):**
"Figure 12: Breakdown of latency for encode and prefill stages using the InternVL2-8B model across varying numbers of images per request. Subfigures (a) and (b) show results on GPU and NPU, respectively. Light green denotes encode latency and light blue indicates prefill latency. NPUs demonstrate distinct latency characteristics compared to GPUs as input size increases."

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\max_{(\mathbf{p},\mathbf{b},\mathbf{s}) \in \mathcal{X}} f(\mathbf{p},\mathbf{b},\mathbf{s}) - \beta cost(\mathbf{p})
$$

$$
\max_{(\mathbf{p}, \mathbf{b}, \mathbf{s}) \in \mathcal{X}} f(\mathbf{p}, \mathbf{b}, \mathbf{s}) - \beta \cdot \text{cost}(\mathbf{p})
$$

$$
v_t^e = E(i_m)
$$

$$
v_t^p = \psi_{EP}(v_t^e)
$$

$$
kv_1^p, o_1^p = P(v_t, i_p)
$$

$$
kv_1^d, o_1^d = \psi_{PD}(kv_1^p, o_1^p)
$$

$$
kv_{t+1}^d, o_{t+1}^d = D(kv_t^d, o_t^d)
$$

## 相关论文

- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[kimi-k2-5-visual-agentic-intelligence]] — KIMI K2.5: VISUAL AGENTIC INTELLIGENCE
- [[qwen3-vl-technical-report]] — Qwen3-VL Technical Report
- [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] — DeepStack: Deeply Stacking Visual Tokens is Surprisingly Simple and Effective for LMMs
- [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] — SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills
- [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] — Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve

## 技术点深读（DEEP）

![[deep/efficiently-serving-large-multimodal-models-using-epd-disaggregation]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/efficiently-serving-large-multimodal-models-using-epd-disaggregation.txt`（69151 字符）供引用检索。