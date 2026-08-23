---
paper_num: "54"
title: "NanoFlow: Towards Optimal Large Language Model Serving Throughput"
authors: "Kan Zhu University of Washington Yufei Gao University of Washington Tsinghua University Yilong Zhao University of Washington UC Berkeley Liangyu Zhao University of Washington Gefei Zuo University of Michigan Yile Gu Univ"
date: "2024/8/23"
arxiv: "https://arxiv.org/abs/2408.12757"
pdf: "papers/nanoflow-towards-optimal-large-language-model-serving-throughput.pdf"
slug: "nanoflow-towards-optimal-large-language-model-serving-throughput"
tags: []
---

# NanoFlow: Towards Optimal Large Language Model Serving Throughput

> [!abstract] 摘要（原文）
> 1. Large Language Models (LLMs) have resulted in a surging demand for planet-scale serving systems, where tens of thou- sands of GPUs continuously serve hundreds of millions of users. Consequently, throughput has emerged as a key met- ric that determines serving systems’ performance. Due to large model sizes and memory-intensive self-attention, LLM serving has been commonly assume

## 元信息
- **发表日期**: 2024/8/23
- **作者**: Kan Zhu University of Washington Yufei Gao University of Washington Tsinghua University Yilong Zhao University of Washington UC Berkeley Liangyu Zhao University of Washington Gefei Zuo University of Michigan Yile Gu Univ
- **arXiv**: https://arxiv.org/abs/2408.12757
- **本地 PDF**: `papers/nanoflow-towards-optimal-large-language-model-serving-throughput.pdf`
- **页数**: 17

## 图表（原文 caption + 页码）

### Figure 1 (p.3) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig01.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p03.png]]*
> [!quote] caption
> Transformer architecture. The operations in the yellow boxes have large batch sizes and share model weight parameters across requests; hence, they are compute-bound. Operations in green boxes require loading a unique KV cache for each request; hence, they are memory-bound. The blue box represents network operations that perform synchronization between operations. • A comprehensive evaluation of Na

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】NanoFlow Transformer 流水(Fig.1)：算子分三类——compute-bound（W_O/K/V/up/down/gate 密集投影，跨请求共享权重、大 batch 摊权重载入）、memory-bound（prefill/decode attention，载每请求 KV、小 batch 避压 KV）、network-bound（AllGather/AllReduce，NVLink 同步）。device-stream 级算子融合：沿关键路径重排+协调度，单设备内只跨 CUDA stream 注入 micro-batch 状态→串行依赖转并行，吞吐 1.91x、达理论峰 68.5%。异构 batch 是关键。架构核心图。

### Figure 2 (p.5) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig02.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p05.png]]*
> [!quote] caption
> Comparison of network time and compute time. The closer to yellow, the more compute-bound the workload is, whereas the closer to blue indicates the workload is more network-bound. LMSYS-Chat Splitwise

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Figure 2** is a 2D heatmap comparing the ratio of network time to compute time across LLM inference configurations. The **y-axis** lists six large models (LLaMA-3 8B, Mistral 8x7B, LLaMA-2 70B, LLaMA-3 70B, Qwen2 72B, LLaMA-3 405B), while the **x-axis** lists thirteen GPU accelerators (V100, A100 40/80GB, H100, H200, B100, B200, MI250/300/325X, Gaudi2/3, Ada6000 PCIe) plus a "Compute Bound" reference column. Each cell holds a numeric ratio (0.119–2.609), with color encoding dominance: **yellow → compute-bound**, **blue → network-bound**.

**Key takeaway:** Workloads shift dramatically toward network-bound (ratio > 1) on PCIe-attached accelerators like Ada6000, while older/lower-bandwidth GPUs remain firmly compute-bound. This guides hardware selection: high-bandwidth interconnects (NVLink, Infinity Fabric) keep large-model inference compute-dominated, whereas slow interconnects expose communication as the bottleneck.

## Caption (Verbatim)

> Figure 2: Comparison of network time and compute time. The closer to yellow, the more compute-bound the workload is, whereas the closer to blue indicates the workload is more network-bound.

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig03.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p05.png]]*
> [!quote] caption
> Comparison of compute time and memory time.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Figure 2** is a 2D heatmap comparing the ratio of network time to compute time across LLM inference configurations. The **y-axis** lists six large models (LLaMA-3 8B, Mistral 8x7B, LLaMA-2 70B, LLaMA-3 70B, Qwen2 72B, LLaMA-3 405B), while the **x-axis** lists thirteen GPU accelerators (V100, A100 40/80GB, H100, H200, B100, B200, MI250/300/325X, Gaudi2/3, Ada6000 PCIe) plus a "Compute Bound" reference column. Each cell holds a numeric ratio (0.119–2.609), with color encoding dominance: **yellow → compute-bound**, **blue → network-bound**.

**Key takeaway:** Workloads shift dramatically toward network-bound (ratio > 1) on PCIe-attached accelerators like Ada6000, while older/lower-bandwidth GPUs remain firmly compute-bound. This guides hardware selection: high-bandwidth interconnects (NVLink, Infinity Fabric) keep large-model inference compute-dominated, whereas slow interconnects expose communication as the bottleneck.

## Caption (Verbatim)

> Figure 2: Comparison of network time and compute time. The closer to yellow, the more compute-bound the workload is, whereas the closer to blue indicates the workload is more network-bound.

### Figure 4 (p.8) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig04.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p08.png]]*
> [!quote] caption
> Execution pipeline of existing systems. The green, yellow, and blue operations correspond to memory-, compute-, and network-bound operations. Operations in the previous and next layer are denoted by dotted borders. "WASTED" shows the stages in the pipeline where the most constrained resource, compute, is underutilized. Small operations (i.e. layernorm, activation, etc.) are omitted for simplicity.

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 4) — Description**

Figure 4 illustrates the per-layer execution pipeline of existing LLM serving systems, ordered left-to-right within a single Layer: **KQV** projection (compute-bound, yellow) → **DecAttn** (memory-bound, green; "Prefill Attention") → **PF** → **Attn.AG** (network-bound, blue) → **O** projection → **O.AG** (network-bound) → the large **UGD** (Up, Gate, Down) feed-forward block (compute-bound, yellow) → **UGD.AR** (network-bound, blue) → next layer's KQV (dotted border). Small ops (layernorm, activations) are omitted.

**Key technical takeaway:** The repeated "WASTED" segments between major kernels reveal that compute hardware sits idle while waiting on memory- or network-bound stages, exposing a structural inefficiency in how current pipelines overlap heterogeneous operations.

**Caption (verbatim):**

"Figure 4: Execution pipeline of existing systems. The green, yellow, and blue operations correspond to memory-, compute-, and network-bound operations. Operations in the previous and next layer are denoted by dotted borders. \"WASTED\" shows the stages in the pipeline where the most constrained resource, compute, is underutilized. Small operations (i.e. layernorm, activation, etc.) are omitted for simplicity."

### Figure 5 (p.8) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig05.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p08.png]]*
> [!quote] caption
> Interference characteristics between GEMM and GEMV kernels. The points on the x-axis correspond unique GEMM-GEMV implementation pairs. The y-axis denotes the GEMM and GEMV kernels’ normalized performance P. ferent implementations of overlapping kernels exponentially expand the profiling space, resulting in millions of possible configurations. This immense complexity makes exhaustive exploration in

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 4) — Description**

Figure 4 illustrates the per-layer execution pipeline of existing LLM serving systems, ordered left-to-right within a single Layer: **KQV** projection (compute-bound, yellow) → **DecAttn** (memory-bound, green; "Prefill Attention") → **PF** → **Attn.AG** (network-bound, blue) → **O** projection → **O.AG** (network-bound) → the large **UGD** (Up, Gate, Down) feed-forward block (compute-bound, yellow) → **UGD.AR** (network-bound, blue) → next layer's KQV (dotted border). Small ops (layernorm, activations) are omitted.

**Key technical takeaway:** The repeated "WASTED" segments between major kernels reveal that compute hardware sits idle while waiting on memory- or network-bound stages, exposing a structural inefficiency in how current pipelines overlap heterogeneous operations.

**Caption (verbatim):**

"Figure 4: Execution pipeline of existing systems. The green, yellow, and blue operations correspond to memory-, compute-, and network-bound operations. Operations in the previous and next layer are denoted by dotted borders. \"WASTED\" shows the stages in the pipeline where the most constrained resource, compute, is underutilized. Small operations (i.e. layernorm, activation, etc.) are omitted for simplicity."

### Figure 6 (p.11) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig06.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p11.png]]*
> [!quote] caption
> Execution pipeline of LLaMA-2 70B, automatically generated by NanoFlow. The solid background and shaded background represents input batch 0-768 and 768-2048, respectively. R stands for resource utilization. By overlapping the compute-, memory-, and network-intensive operations, NanoFlow increases compute utilization and improves the serving throughput. data size of the offload is balanced across i

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The main figure (Figure 6) depicts an execution pipeline for a LLaMA-2 70B transformer layer, automatically scheduled by NanoFlow. Operations are arranged left-to-right along a timeline marked "Layer," including:

- **Attention blocks**: DecAttn1–4 (decoding attention), KQV1–4 (query/key/value projections), PF1 (prefill), Attn.AG1–2, O.AG1, O.AR1–2
- **FFN blocks**: O1–O3 (linear projections), Up,Gate,Down (UGD) 1–2, UGD.AR1–3
- **Inter-stage steps**: Prefill Attention and AG-to-AR Transform

Two batches are processed concurrently: solid-background cells represent input batch 0–768 (prefill), while shaded cells represent batch 768–2048 (decoding), denoted with resource-utilization values (R = 0.1–0.9). NanoFlow interleaves compute-bound (KQV, attention), memory-bound (UGD), and network-bound (UGD.AR/Attn.AG) operations so that heterogeneous resources remain busy.

**Key takeaway**: Overlapping compute-, memory-, and network-intensive kernels across batches lets NanoFlow raise GPU utilization toward the optimal throughput ceiling.

## Caption (verbatim)

Figure 6: Execution pipeline of LLaMA-2 70B, automatically generated by NanoFlow. The solid background and shaded background represents input batch 0-768 and 768-2048, respectively. R stands for resource utilization. By overlapping the compute-, memory-, and network-intensive operations, NanoFlow increases compute utilization and improves the serving throughput.

### Figure 7 (p.11) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig07.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p11.png]]*
> [!quote] caption
> Offline throughput comparison. NanoFlow outper- forms all baselines for all the workload settings. TP stands for the number of GPUs used with tensor parallelism. • How do the various techniques proposed in NanoFlow contribute to the end-to-end throughput? (§6.4) • What is the compute, memory and network resource usage pattern of NanoFlow? (§6.5) • How does NanoFlow improve performance when ap- pli

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The main figure (Figure 6) depicts an execution pipeline for a LLaMA-2 70B transformer layer, automatically scheduled by NanoFlow. Operations are arranged left-to-right along a timeline marked "Layer," including:

- **Attention blocks**: DecAttn1–4 (decoding attention), KQV1–4 (query/key/value projections), PF1 (prefill), Attn.AG1–2, O.AG1, O.AR1–2
- **FFN blocks**: O1–O3 (linear projections), Up,Gate,Down (UGD) 1–2, UGD.AR1–3
- **Inter-stage steps**: Prefill Attention and AG-to-AR Transform

Two batches are processed concurrently: solid-background cells represent input batch 0–768 (prefill), while shaded cells represent batch 768–2048 (decoding), denoted with resource-utilization values (R = 0.1–0.9). NanoFlow interleaves compute-bound (KQV, attention), memory-bound (UGD), and network-bound (UGD.AR/Attn.AG) operations so that heterogeneous resources remain busy.

**Key takeaway**: Overlapping compute-, memory-, and network-intensive kernels across batches lets NanoFlow raise GPU utilization toward the optimal throughput ceiling.

## Caption (verbatim)

Figure 6: Execution pipeline of LLaMA-2 70B, automatically generated by NanoFlow. The solid background and shaded background represents input batch 0-768 and 768-2048, respectively. R stands for resource utilization. By overlapping the compute-, memory-, and network-intensive operations, NanoFlow increases compute utilization and improves the serving throughput.

### Figure 8 (p.13) ⭐深度解读
![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p13.png]]
> [!quote] caption
> Latency comparison. The x-axis shows the number of incoming requests per second and the y-axis shows the normalized latency. NanoFlow handles higher request within 200ms SLO constraints.

> [!tip] 技术解读（多模态）
> **Description:** Figure 8 is a latency-comparison plot with three side-by-side sub-panels—(a) Splitwise, (b) LMSYS-Chat-1M, and (c) ShareGPT—each plotting **request rate (req/s)** on the x-axis against **normalized latency in ms/token** on the y-axis. Four serving systems are overlaid: vLLM, DeepSpeed-FastGen, TensorRT-LLM, and NanoFlow (the authors' system, shown in red). A red dashed horizontal line marks the ~200 ms/token SLO threshold. The baselines' latency curves rise steeply and cross the SLO line at low request rates (≈6–17 req/s), while NanoFlow stays flat under the SLO threshold up to 17–32 req/s before escalating.

**Key technical takeaway:** NanoFlow sustains a 200 ms/token latency budget under request loads 2–4× higher than vLLM/DeepSpeed-FastGen across all three real-world traces, demonstrating superior SLO-conforming throughput.

**Caption (verbatim):** "Figure 8: Latency comparison. The x-axis shows the number of incoming requests per second and the y-axis shows the normalized latency. NanoFlow handles higher request within 200ms SLO constraints."

### Figure 9 (p.13) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig09.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p13.png]]*
> [!quote] caption
> Ablation study results for NanoFlow. Nano-batching and overlapping improves NanoFlow’s performance.

> [!tip] 技术解读（多模态）
> **Description:** Figure 8 is a latency-comparison plot with three side-by-side sub-panels—(a) Splitwise, (b) LMSYS-Chat-1M, and (c) ShareGPT—each plotting **request rate (req/s)** on the x-axis against **normalized latency in ms/token** on the y-axis. Four serving systems are overlaid: vLLM, DeepSpeed-FastGen, TensorRT-LLM, and NanoFlow (the authors' system, shown in red). A red dashed horizontal line marks the ~200 ms/token SLO threshold. The baselines' latency curves rise steeply and cross the SLO line at low request rates (≈6–17 req/s), while NanoFlow stays flat under the SLO threshold up to 17–32 req/s before escalating.

**Key technical takeaway:** NanoFlow sustains a 200 ms/token latency budget under request loads 2–4× higher than vLLM/DeepSpeed-FastGen across all three real-world traces, demonstrating superior SLO-conforming throughput.

**Caption (verbatim):** "Figure 8: Latency comparison. The x-axis shows the number of incoming requests per second and the y-axis shows the normalized latency. NanoFlow handles higher request within 200ms SLO constraints."

### Figure 10 (p.13) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig10.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p13.png]]*
> [!quote] caption
> While the non-overlapping baseline sequentially executes operations, which mostly uses only one resource at a given time, the NanoFlow instance can concurrently utilize multiple resources and achieves 68.5% average compute utilization. Due to kernel interfer- ence, NanoFlow provides lower than optimal compute usage.

> [!tip] 技术解读（多模态）
> **Description:**

The figure presents two side-by-side panels comparing resource utilization over a ~3000 µs window, each containing three stacked time-series subplots measuring **Compute** (yellow), **Memory** (green), and **Network** (blue) usage as percentages.

- **Panel (a) — Non-overlap pipeline:** Resources are utilized serially with clear isolation. Compute spikes (~70%, ~55%, ~87%) dominate certain windows, Memory shows an early burst to ~80% then stays low, and Network has distinct isolated bursts (~60%, ~75%, ~40%) — each resource peaks when others are idle.
- **Panel (b) — NanoFlow:** The same three resources exhibit interleaved, overlapping utilization. Compute stays active across most of the timeline at varying levels (~30–90%), Memory sustains moderate usage peaking around ~70%, and Network shows distributed micro-bursts, indicating concurrent execution.

**Key takeaway:** NanoFlow overlaps compute, memory, and network operations in time, eliminating idle gaps and sustaining higher aggregate utilization, whereas the non-overlap pipeline leaves resources sequentially idle. (107 words)

**Caption (verbatim):**

(a) Non-overlap pipeline resource usage

(b) NanoFlow resource usage

### Figure 11 (p.13) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig11.png]]
*整页渲染: ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p13.png]]*
> [!quote] caption
> We find that

> [!tip] 技术解读（多模态）
> **Figure description (≈110 words):**
The bar chart compares normalized per-GPU throughput (%) between two LLM serving systems—vLLM (blue) and NanoFlow (orange)—across five models: Llama-3-70B, Qwen2-72B, Deepseek-67B, Mixtral-8x7B, and Llama-3-8B. Absolute throughput values are annotated inside each bar (e.g., 593 vs. 1306 for Llama-3-70B). A red dashed horizontal line at 100% marks the "Optimal" baseline. NanoFlow consistently outperforms vLLM, with the largest absolute gap on Mixtral-8x7B (997 → 5188 tokens). **Key takeaway:** NanoFlow roughly doubles per-GPU throughput versus vLLM on dense models and achieves >5× improvement on the sparse MoE model, indicating that NanoFlow's optimizations are particularly effective for expert-routing workloads.

**Caption verbatim:**
*No standalone caption is present in the image. Visible text labels are: legend "vLLM / NanoFlow"; axis label "Normalized Per-GPU Throughput (%)"; reference line "Optimal"; bar value annotations (e.g., "70.6%", "32.0%", "1306", "593", "12756", "5187"); and x-axis model names (Llama-3-70B, Qwen2-72B, Deepseek-67B, Mixtral-8x7B, Llama-3-8B).*

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.7) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-tab02.png]]
> [!quote] caption
> Comparison of operation runtimes between cost model estimation and real-world measurements.

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**

The table decomposes operation-level runtime into three resource channels: Compute (GFLOP), Memory Load (GB), and Network Usage (GB). For each operation (e.g., KQV, Proj, etc., with row "KQV" visible showing 27487.0 GFLOP, 10.5 GB memory load, 0 GB network), it breaks the estimated latency *T_est* into three additive sub-times—*T_comp*, *T_mem*, *T_net*—and compares their sum against a measured *Real Time* column. This enables a resource-bottleneck attribution (compute- vs. memory- vs. network-bound) per kernel.

**Key takeaway:** The model predicts end-to-end runtime as a sum of independently estimated compute, memory, and network latency components, isolating which resource channel dominates each operation's wall-clock cost.

**Caption (verbatim):**

Table 2: Comparison of operation runtimes between cost model estimation and real-world measurements.

### Table 3 (p.9) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-tab03.png]]
> [!quote] caption
> Performance P of GEMV and network kernels with different resource utilization R .

> [!tip] 表格解读（多模态）
> ## Description

**Architecture/Components**: The table is a 3×N lookup matrix translating *Resource Utilization* (R, columns 0→1) into *Performance* (P, values) for three kernel classes: **GEMM** (definitionally identity: P = R), **GEMV** (saturates early — R=0.2 already yields P=0.3, plateauing near R=0.9), and **Network** (steeper front-end: R=0.2 → P=0.5, capped at P=1 by R=0.9).

**Data Flow**: An auto-search consumes the interference profile, queries this table to convert each co-located kernel's allocated R into achievable P, then selects combinations maximizing aggregate throughput. The red-highlighted row (R=0.2 → P=0.3) illustrates the GEMV row used to trade 0.2 units of GEMM performance for 0.3 units of GEMV.

**Key Takeaway**: Across all evaluated GEMM shapes and 64 batch sizes, R-to-P translation is stable (σ < 5% of mean), so a single table universally parameterizes kernel trade-offs for subsequent search.

## Caption (verbatim)

*Table 3: Performance P of GEMV and network kernels with different resource utilization R.*

### Table 4 (p.12) ⭐深度解读
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-tab04.png]]
> [!quote] caption
> The average and standard deviation of input and output lengths in the sampled datasets.

> [!tip] 表格解读（多模态）
> **Note:** No figure is present in the provided content — only paragraphs of paper text plus **Table 4**'s caption. There is no architecture diagram, component diagram, or data-flow figure to describe, so I cannot supply the requested figure summary without fabricating content. Below I transcribe exactly what appears verbatim.

### Verbatim caption
> **Table 4:** The average and standard deviation of input and output lengths in the sampled datasets.

### Body text (verbatim, as supplied)
> standard for data center-scale inference.
>
> **Baselines.** We consider three widely-used serving frameworks as baselines.
>
> vLLM⁶ [17, 52] is a state-of-the-art serving system delivering high throughput. vLLM implements pagedAttention for increasing GPU memory utilization, as well as the chunked prefill for higher GPU utilization.
>
> DeepSpeed-FastGen⁷ [13, 23] is a serving framework developed by Microsoft. It dynamically composes prefill with decode requests to ensure that the engine is operating in a high throughput regime. We vary the `max-ragged-batch-size` to tune the batch size for highest throughput.
>
> TensorRT-LLM⁸ [26, 27] is a high-performance LLM inference engine built upon NVIDIA's TensorRT SDK. We set `max-num-tokens` by calculating the maximum capacity for the KV-cache in the GPU memory. We also enable paged KV-cache and dynamic batching optimizations when compiling.
>
> **Datasets.** Splitwise [32] is a conversation trace collected from a real production environment at Microsoft, with a total of around 20000 requests. LMSYS-Chat-1M [56] is a large-scale dataset with 1 million real-world conversations from 25 different LLMs. ShareGPT [1] is a dataset with conversations collected from the ShareGPT API. We use the full trace from Splitwise and randomly sample 50,000 requests from ShareGPT and LMSYS-Chat-1M for our evaluation. Table 4 shows the average input length and output length in tokens for the sampled datasets we use.

If you intended to share an actual figure image, please re-upload it and I'll provide the architecture/data-flow description plus the key technical takeaway as requested.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
T_{mem} = \frac{MemSize}{MemBW}
$$

$$
T_{Compute} &\approx \frac{2B_{Dense} \cdot P_{Model}}{Compute}
$$

$$
T_{net} \approx 4\cdot\frac{N_{GPU}B_{Dense}D_{model} S_{type} L }{NetBW}
$$

$$
T_R &= \frac{T_{Mem}}{T_{Compute}} \approx \frac{Compute}{MemBW} \frac{MemSize}{P_{model}} \frac{1}{2B_{dense}}
$$

$$
\mathrm{Throughput_{optimal}} &= \frac{B_{Dense}}{T_{Compute}} = \frac{Compute}{2 P_{Model}}
$$

## 技术点深读（DEEP）

![[deep/nanoflow-towards-optimal-large-language-model-serving-throughput]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/nanoflow-towards-optimal-large-language-model-serving-throughput.txt`（78749 字符）供引用检索。