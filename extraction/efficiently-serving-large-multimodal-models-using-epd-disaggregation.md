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
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig01.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p01.png]]*
> [!quote] caption
> Aggregated (top) vs. disaggregated (bottom) sys- tem architectures. In the aggregated setup, the encoder (E) and LLM share the same GPUs, leading to interference be- tween encode and prefill stages (e.g., LLM-4 delays E5).

> [!tip] 技术解读（多模态）
> **Figure 1 Description (architecture/components/data flow + key takeaway):**

The figure contrasts two serving topologies across 4 GPU rows. **Aggregated (top, DP=4):** each row holds a tensor-parallel (TP) LLM shard (LLM¹–LLM⁴); a fifth encoder stage E5 is squeezed into row 4 alongside LLM⁴, so prefill of one LLM stalls the encoder (visible as E5 pushed right after LLM⁴). **Disaggregated (bottom, P=3, E=1):** E5 is pinned to its own dedicated GPU row at the top, while rows 2–4 host only LLM¹/LLM⁴, LLM²/LLM⁵, LLM³ respectively — eliminating cross-stage contention.

**Key takeaway:** Decoupling the encoder onto a separate GPU pool removes prefill-induced encoder stalls, the dominant source of TTFT inflation in aggregated multimodal serving. (~95 words)

**Caption (verbatim):**

"Figure 1: Aggregated (top) vs. disaggregated (bottom) system architectures. In the aggregated setup, the encoder (E) and LLM share the same GPUs, leading to interference between encode and prefill stages (e.g., LLM-4 delays E5). Disaggregation isolates these stages across GPUs, reducing contention and improving utilization. This separation enables better performance under multimodal workloads, addressing key limitations of existing systems."

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig02.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p02.png]]*
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
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig03.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p03.png]]*
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
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig04.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p04.png]]*
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
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig05.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p06.png]]*
> [!quote] caption
> SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively. The top and bottom rows show results for 2 and 4 images per request. EPD consistently outperforms all baselines across configurations. question answering items that span diverse video lengths, topic

> [!tip] 技术解读（多模态）
> **Figure Description**

The figure is a 2×3 grid of line plots comparing SLO attainment (%) versus request rate (req/s) across three LMM serving systems: **EPD** (blue), **DistServe** (green), and **vLLM** (red). Columns correspond to three models of increasing scale — MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B — while rows contrast workload difficulty with 2 images/request (top) versus 4 images/request (bottom). Each plot includes a horizontal dashed reference line marking the 90% SLO target and vertical dashed lines indicating each system's goodput threshold.

**Key Technical Takeaway:** EPD consistently sustains >90% SLO attainment at substantially higher request rates than both baselines across all model scales and image counts, whereas DistServe and vLLM collapse below ~10% SLO due to cross-stage interference that worsens with model size (8B→26B) and heavier prefill workloads (2→4 images).

**Caption (verbatim):**

Figure 5: SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively. The top and bottom rows show results for 2 and 4 images per request. EPD consistently outperforms all baselines across configurations.

### Figure 6 (p.7) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig06.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]]*
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
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig07.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]]*
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
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig08.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]]*
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
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig09.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p09.png]]*
> [!quote] caption
> As shown, EPD is the only configuration that achieves the SLO requirements, while the other baselines fail to meet the SLOs entirely, even at low request rates.

> [!tip] 技术解读（多模态）
> **Figure 9 — Description:**

**Architecture/Components/Data Flow:** A 2-D line chart comparing SLO attainment (%) on the y-axis (0–100) versus Request Rate (req/s) on the x-axis (~0.005–0.035) for three serving systems on NPUs. Three series are plotted: **EPD** (blue line with circles), **DistServe** (green line with diamonds), and **vLLM** (red line with triangles). A horizontal dashed reference line marks the SLO target (~95%), and a vertical dashed line indicates a low-rate threshold (~0.01 req/s). EPD starts near 100% and gradually degrades to ~20% as request rate increases, while DistServe and vLLM remain flat near 0%.

**Key Technical Takeaway (≤120 words):** EPD is the **only** configuration that achieves positive SLO attainment under the strict TTFT ≤ 8.5s / TPOT ≤ 0.12s constraints on the InternVL2-8B LMM with a heavy encoding workload (8 × 4032×3024 images/request). Baseline disaggregated systems (DistServe, vLLM) fail to meet SLOs entirely, even at very low request rates, demonstrating that **EPD's encoding–prefill–decoding disaggregation is essential** for serving high-resolution multimodal workloads on memory-constrained NPUs — a regime where encoding dominates and traditional GPU-style disaggregation benefits (~24.4%) amplify to ~35.2% TTFT improvement.

**Caption (verbatim):**
> Figure 9: SLO attainment (↑) on NPUs under varying request rates for a synthetic workload using the InternVL2-8B model. EPD maintains positive SLO attainment under strict TTFT constraints, while baselines fail to meet the criteria.

### Figure 10 (p.13) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig10.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]]*
> [!quote] caption
> Left: Impact of varying the number of encoding workers in the EPD method. The notation xEyP denotes a configuration with x encoder and y prefill workers. The DistServe method uses a fixed 7P configuration, assigning 7 workers to handle both encoding and prefill steps. Middle: Effect of the number of images per request on end-to-end throughput. Right: Sensitivity to encoding and prefill batch sizes

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 11) — Architecture/Components/Data Flow:**

A 2×3 grid of subplots comparing SLO attainment (%) versus request rate (req/s) across three LMMs — MiniCPMv-2.6 (a), InternVL2-8B (b), and InternVL2-26B (c) — with the top and bottom rows representing 6 and 8 images per request, respectively. Three serving methods are overlaid in each subplot: EPD (blue), DistServe (green), and vLLM (red). Vertical dashed markers indicate the maximum sustainable request rate at the 90% SLO threshold.

**Key Technical Takeaway:** EPD sustains near-100% SLO attainment at substantially higher request rates than DistServe and vLLM across every model scale and image count, confirming that encoder–prefill–decode disaggregation scales gracefully while the baselines collapse under modest load due to encoder-side compute bottlenecks.

**Caption (verbatim):**

"Figure 11: SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively. The top and bottom rows show results for 6 and 8 images per request. EPD consistently outperforms all baselines, demonstrating robust performance as image count increases."

### Figure 11 (p.13) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig11.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]]*
> [!quote] caption
> SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively. The top and bottom rows show results for 6 and 8 images per request. EPD consistently outperforms all baselines, demonstrating robust performance as image count increases.. content of this image?”),

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 11) — Architecture/Components/Data Flow:**

A 2×3 grid of subplots comparing SLO attainment (%) versus request rate (req/s) across three LMMs — MiniCPMv-2.6 (a), InternVL2-8B (b), and InternVL2-26B (c) — with the top and bottom rows representing 6 and 8 images per request, respectively. Three serving methods are overlaid in each subplot: EPD (blue), DistServe (green), and vLLM (red). Vertical dashed markers indicate the maximum sustainable request rate at the 90% SLO threshold.

**Key Technical Takeaway:** EPD sustains near-100% SLO attainment at substantially higher request rates than DistServe and vLLM across every model scale and image count, confirming that encoder–prefill–decode disaggregation scales gracefully while the baselines collapse under modest load due to encoder-side compute bottlenecks.

**Caption (verbatim):**

"Figure 11: SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively. The top and bottom rows show results for 6 and 8 images per request. EPD consistently outperforms all baselines, demonstrating robust performance as image count increases."

### Figure 12 (p.16) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig12.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p16.png]]*
> [!quote] caption
> Breakdown of latency for encode and prefill stages using the InternVL2-8B model across varying numbers of images per request. Subfigures (a) and (b) show results on GPU and NPU, respectively. Light green denotes encode latency and light blue indicates prefill latency. NPUs demonstrate distinct latency characteristics compared to GPUs as input size increases. E.3. SLO Criteria

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**
Figure 12 presents two stacked bar charts comparing the latency breakdown (%) of encode (green) vs. prefill (blue) stages for the InternVL2-8B model as the number of images per request (#I/R) grows from 1 to 8. Subfigure (a) reports GPU measurements; subfigure (b) reports NPU measurements. The encode share shrinks with larger inputs while prefill grows, but the trend differs between hardware. On GPU at #I/R=8, encode ≈25%/prefill ≈75%, whereas NPU retains ≈40% encode. **Key takeaway:** NPUs exhibit a 10–20% higher encode-to-prefill latency ratio than GPUs across multimodal workloads, motivating EPD disaggregation since encoding and prefilling have asymmetric resource requirements that benefit from being separated on NPUs.

**Caption (verbatim):**
"Figure 12: Breakdown of latency for encode and prefill stages using the InternVL2-8B model across varying numbers of images per request. Subfigures (a) and (b) show results on GPU and NPU, respectively. Light green denotes encode latency and light blue indicates prefill latency. NPUs demonstrate distinct latency characteristics compared to GPUs as input size increases."

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.7) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab01.png]]
> [!quote] caption
> Mean TTFT latency (in seconds) ( ↓ ) for varying video lengths at a fixed request rate of 1 request/sec. Results are averaged over 100 Video-MME samples. EPD achieves the lowest latency across all video lengths.

> [!tip] 表格解读（多模态）
> # Main Figure Description

The figure presents a **performance benchmark table** comparing Mean TTFT (Time To First Token) latency across varying video lengths at a sustained request rate of 1 request/sec. Key components include:

- **Rows**: Different video length categories (typically short/medium/long in the Video-MME benchmark)
- **Columns**: Competing methods/models being evaluated for latency
- **Metric**: TTFT in seconds (lower is better, indicated by ↓)
- **Evaluation conditions**: 100 Video-MME samples, averaged

**Key technical takeaway**: EPD (a method proposed in the source paper) achieves the lowest TTFT latency across all video lengths, demonstrating that its design is robust to input scale while maintaining responsiveness under sustained load.

# Caption (Verbatim Transcription)

> Table 1: Mean TTFT latency (in seconds) (↓) for varying video lengths at a fixed request rate of 1 request/sec. Results are averaged over 100 Video-MME samples. EPD achieves the lowest latency across all video lengths.

### Table 2 (p.8) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab02.png]]
> [!quote] caption
> Comparison of the maximum number of images supported per request for various image resolutions across different models. Higher values are better; best values in each row are italicized.

> [!tip] 表格解读（多模态）
> **Note:** The content you've shared contains text only — specifically a table caption and accompanying paragraph. There is no visible figure, diagram, architecture, or data-flow chart in the provided image to describe visually.

**Key technical takeaway (≤120 words):** The passage describes a disaggregated inference system called **EPD**, compared against aggregated systems **DistServe** and **vLLM**. Across three multimodal models (MiniCPMv, InternVL2-8B, InternVL2-26B) tested at multiple image resolutions with batch size 1 and 80% of memory allocated to the KV cache, **EPD supports substantially more images per request**. Notably, at 4032×3024 resolution, EPD handles 7× more images than DistServe for InternVL2-26B and 10× more for InternVL2-8B. For InternVL2-8B, the 19-image ceiling reflects the model's *maximum context length* rather than an EPD limitation — suggesting EPD's actual capacity is even higher. This demonstrates EPD's advantage for high-resolution, multi-image multimodal workloads.

**Caption verbatim:**
> Table 2: Comparison of the maximum number of images supported per request for various image resolutions across different models. Higher values are better; best values in each row are italicized.

### Table 3 (p.8) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab03.png]]
> [!quote] caption
> Comparison of the maximum supported batch sizes for E and P stages across different models and image reso- lutions. Higher values are better; italicized values indicate the best in each row. OOM denotes cases where the model ran out of memory.

> [!tip] 表格解读（多模态）
> **Main Figure (Table 3) Description:**
The main visual is a comparison table showing maximum supported batch sizes across three multimodal models (MiniCPMv 2.6, InternVL2-8B, InternVL2-26B) under three image resolutions (313×234, 787×444, 4032×3024) with varying patch counts. Columns contrast DistServe's combined (E, P) batching against EPD's separate E and P stage batch sizes. EPD consistently supports dramatically larger batch sizes, while DistServe frequently hits OOM (Out of Memory), especially at high resolutions on the 26B model.

**Key Technical Takeaway:**
EPD's encoder-prefill disaggregation unlocks far higher throughput in multimodal LLM serving. By isolating the E stage (which does not need LLM weights or KV cache) from P, EPD achieves up to a **22× larger encoding batch** (MiniCPM-V 2.6, 787×444: 22 vs. 1) and **14.5× larger prefill batch** (29 vs. 2), and avoids OOM entirely where DistServe fails on the 26B model at 4032×3024 — directly translating the ~95% E-worker memory savings into scalability.

**Caption (verbatim):**
Table 3: Comparison of the maximum supported batch sizes for E and P stages across different models and image resolutions. Higher values are better; italicized values indicate the best in each row. OOM denotes cases where the model ran out of memory.

### Table 4 (p.8) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab04.png]]
> [!quote] caption
> Effect of ablating IRP feature from the proposed system on TTFT (s). Disabling IRP negatively affects the TTFT (up to 2.9x worse ) for various multiple images/ re- quest (#I/R). Results are averaged over 100 requests.

> [!tip] 表格解读（多模态）
> I don't actually see a figure in what you've shared — only two columns of body text from page 8 of the paper (discussions of "EPD Supports a Higher Number of Images per Request," "EPD Supports Higher Batch Sizes," and Table 4's caption/IRP ablation discussion). No architecture diagram, system components, or data-flow visual is present in the image content provided.

If you intended to attach a figure (e.g., the EPD system architecture showing the disaggregated Encoder/Prefill/Decode stages, IRP parallelization, or the offline optimizer), it didn't come through — only the text page rendered.

Could you re-share with the actual figure image included? Once I can see it, I'll gladly:
1. Describe the architecture/components/data flow + one key technical takeaway (≤120 words), and
2. Transcribe the caption verbatim.

### Table 5 (p.9) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab05.png]]
> [!quote] caption
> Ablating the offline optimizer reduces goodput by 2.2× on average when configurations are selected randomly. ↓ indicates lower is better; ↑ indicates higher is better.

> [!tip] 表格解读（多模态）
> **Description of the Main Table (Effect of Dynamic Role Switching — Table 6 contents):**

The table contrasts two system configurations under a shifted mixed workload: (i) full **EPD** (Encoder–Prefill–Decode) with dynamic role switching, versus (ii) **w/o Switch**, where role assignment is fixed. The workload injects 100 requests at 3 req/s, split into 10 short requests (50 output tokens) followed by 90 long requests (500 output tokens), simulating a workload-characteristic shift. Three performance metrics are measured — end-to-end Latency, **TTFT** (Time to First Token), and **TPOT** (Time Per Output Token) — all reported in seconds, lower-is-better. EPD achieves 28.01s / 1.42s / 0.05s; w/o Switch degrades to 61.10s (2.2×), 1.33s (0.9×), and 0.12s (2.4×).

**Key takeaway:** Disabling dynamic role switching dramatically inflates end-to-end latency (2.2×) and per-token latency (2.4×), while TTFT barely improves (0.9×), indicating role switching is critical for absorbing workload shifts without penalizing time-to-first-token responsiveness.

**Caption (verbatim):**
"Table 5: Ablating the offline optimizer reduces goodput by 2.2x on average when configurations are selected randomly. ↓ indicates lower is better; ↑ indicates higher is better."

### Table 6 (p.9) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab06.png]]
> [!quote] caption
> Ablating dynamic role-switching from EPD de- grades TPOT by 2.4× and increases end-to-end latency by 2.2×. Results are averaged over 100 requests with one 4K image each. ↓ indicates lower is better.

> [!tip] 表格解读（多模态）
> **Description (main figure = Table 6 + discussion paragraph):**

The table presents an ablation study of dynamic role-switching in an EPD (Encoder–Prefill–Decode) serving system for multimodal LLM inference. It compares a static **5E1P2D** configuration (5 Encoder, 1 Prefill, 2 Decode workers, offline-optimized for 50-token outputs) against a runtime-reconfigured **2E1P5D** layout that migrates three Encoder workers to Decode when the workload grows to 500 output tokens. Data flow: request → encoder (4K image) → prefill (prompt) → decode (token generation). Metrics are TPOT and end-to-end latency, averaged over 100 requests.

**Key takeaway:** Static encoder/prefill/decode partitions decay sharply under decode-heavy workloads; in-place worker migration between roles recovers roughly **2×** end-to-end speedup with no additional hardware.

**Caption (verbatim):**

> Table 6. Ablating dynamic role-switching from EPD degrades TPOT by 2.4× and increases end-to-end latency by 2.2×. Results are averaged over 100 requests with one 4K image each. ↓ indicates lower is better.
>
> Without dynamic worker migration, the system performs poorly because it remains fixed in the initial configuration (5E1P2D, optimized offline for 50 tokens) and is unable to adapt to the increased decoding demand. In contrast, the EPD system with migration dynamically reconfigures itself (2E1P5D) to handle the new workload (500 output tokens) by shifting three E instances to D, resulting in approximately 2× better performance.

### Table 7 (p.12) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab07.png]]
> [!quote] caption
> SLO attainment results ( ↑ ) for online audio bench- marking with ultravox-v0 3 (24 audio files per re- quest). All baselines use 4 GPUs: vLLM operates in data- parallel (DP) mode, DistServe uses a 3P1D configuration, and EPD adopts a 2E1P1D setup. EPD achieves consis- tently high SLO attainment and

> [!tip] 表格解读（多模态）
> **Description of the main figure (Table 7):**
The table presents SLO (Service-Level Objective) attainment and goodput results for an online audio benchmarking workload using the `ultravox-v0_3` model (24 audio files/request) across varying request rates. Three 4-GPU systems are compared: **vLLM** (data-parallel mode), **DistServe** (3P1D: 3 prefill + 1 decode), and **EPD** (2E1P1D: 2 encode + 1 prefill + 1 decode). The data flow is audio file → encoder → prefill (LLM) → decode. **Key takeaway:** Splitting the encoding stage out (EPD) consistently yields the highest SLO attainment and goodput across all request rates, because the encode/prefill/decdecode disaggregation removes prefix interference and improves load balancing for long audio contexts.

**Caption (verbatim):**
"Table 7: SLO attainment results (↑) for *online audio* benchmarking with `ultravox-v0_3` (24 audio files per request). All baselines use 4 GPUs: vLLM operates in data-parallel (DP) mode, DistServe uses a 3P1D configuration, and EPD adopts a 2E1P1D setup. EPD achieves consistently high SLO attainment and the highest goodput across all request rates."

### Table 8 (p.12) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab08.png]]
> [!quote] caption
> Comparison of maximum supported KV cache size (in terms of percentage of free memory) on prefill node for various #images/ request. Image resolution fixed to 4K. Higher ( italicized ) is better.

> [!tip] 表格解读（多模态）
> **Description:**

The table (Table 8) compares three vision-language models — **MiniCPM-V 2.6**, **InternVL2-8B**, and **InternVL2-26B** — by reporting the *maximum supported KV cache size* (as a percentage of free memory) on the prefill node as the number of images per request increases (5, 10, 20, 40, 80), with image resolution fixed at 4K. The two percentage columns represent two KV-cache-size regimes (e.g., larger vs. smaller target allocations), with "OOM" (Out-of-Memory) and "OOCL" (Out-of-Context-Length) indicating failure modes.

**Key technical takeaway:** Smaller VLMs (MiniCPM-V 2.6, InternVL2-8B) scale to many more images per request before exhausting the KV cache, whereas the 26B model hits OOM after only ~10 images even at minimal cache allocation — revealing that model size, not just KV budget, dominates prefill memory pressure for high-resolution multi-image workloads.

**Caption verbatim:**

> Table 8: Comparison of maximum supported KV cache size (in terms of percentage of free memory) on prefill node for various #images/ request. Image resolution fixed to 4K. Higher *(italicized)* is better.

### Table 9 (p.16) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab09.png]]
> [!quote] caption
> outlines the SLO criteria for TTFT and TPOT across various models and different numbers of images per request (#I/R). These criteria are empirically derived based on the characteristics of the underlying models, such as the compu- tational complexity of the MME and LLM. We also consider what is real

> [!tip] 表格解读（多模态）
> **Note:** The supplied image is a **data table** (Table 9), not an architecture/block diagram. I'll adapt by describing its tabular structure (rows/columns) as the "components" and the trend across cells as the implicit "data flow."

### Main figure (table) — structure & key takeaway
**Components:** A 4-row × 7-column matrix. Columns are grouped by **model** (MiniCPM-V 2.6, InternVL 8B, InternVL 26B), each split into two metrics — **TTFT** (time-to-first-token) and **TPOT** (time-per-output-token). Rows are the **number of images per request (#I/R)**: 2, 4, 6, 8.

**Key takeaway:** TTFT scales roughly linearly with #I/R for every model (e.g., MiniCPM-V 2.6: 1.40 → 5.10 s; InternVL 26B: 3.50 → 15.00 s), reflecting cumulative vision-encoder and prefill cost. TPOT, by contrast, stays nearly flat, confirming it is governed by per-token decoding rather than input-image count.

### Caption / surrounding text — verbatim transcription

"Table 9 outlines the SLO criteria for TTFT and TPOT across various models and different numbers of images per request (#I/R). These criteria are empirically derived based on the characteristics of the underlying models, such as the computational complexity of the MME and LLM. We also consider what is realistically achievable by both our method and the baselines on a fixed number (8 GPUs) used in experiments. Across models, as #I/R increases, there is an approximately linear increase in the TTFT criteria due to the higher encoding load and additional tokens generated during the prefill stage. In contrast, TPOT requires only minor adjustments since it is not directly impacted by changes in #I/R."

| #I/R | MiniCPM-V 2.6 |   | InternVL 8B |   | InternVL 26B |    |
|------|---------------|---|-------------|---|--------------|-----|
|      | TTFT          | TPOT | TTFT      | TPOT | TTFT       | TPOT |
| 2    | 1.40          | 0.04 | 1.20      | 0.05 | 3.50       | 0.07 |
| 4    | 2.60          | 0.04 | 2.40      | 0.06 | 7.05       | 0.08 |
| 6    | 3.90          | 0.06 | 3.55      | 0.09 | 11.00      | 0.95 |
| 8    | 5.10          | 0.06 | 5.00      | 0.18 | 15.00      | 0.15 |

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