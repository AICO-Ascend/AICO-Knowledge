---
paper_num: "66"
title: "Huawei Cloud Model-as-a-Service on the CloudMatrix384 SuperPod"
authors: "SuperPod xDeepServe (XDS) Team @ Huawei"
date: "2025/8/4"
arxiv: "https://arxiv.org/abs/2508.02520"
pdf: "papers/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod.pdf"
slug: "huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod"
tags: []
---

# Huawei Cloud Model-as-a-Service on the CloudMatrix384 SuperPod

> [!abstract] 摘要（原文）
> Scaled-out MoE LLMs and scaled-up SuperPods create new systems challenges for production Model-as-a-Service (MaaS), requiring disaggregation, low-latency communication, and decentralized serving. This report presents xDeepServe, the production serving system behind Huawei Cloud's MaaS offering on CloudMatrix384, a 48-server SuperPod with 384 Ascend 910C chips connected by a high-bandwidth UB fabric and global shared memory. It serves models including DeepSeek, Kimi, GLM, Qwen, and MiniMax, among others. xDeepServe is built around Transformerless, a disaggregated execution architecture that decomposes transformer inference into modular units -- attention, feedforward, and MoE -- and supports disaggregated Prefill-Decode and MoE-Attention deployments. To enable disaggregation, we develop XCCL, a memory-semantic communication layer providing microsecond-level point-to-point and scalable all-to-all primitives, and we extend FlowServe with decentralized DP groups and techniques to mitigate stragglers and synchronization variance. In a peak decoding configuration, xDeepServe reaches 2400 tokens/s per Ascend 910C chip at ~50ms time-per-output-token (TPOT).

## 元信息
- **发表日期**: 2025/8/4
- **作者**: SuperPod xDeepServe (XDS) Team @ Huawei
- **arXiv**: https://arxiv.org/abs/2508.02520
- **本地 PDF**: `papers/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod.pdf`
- **页数**: 32

## 图表（原文 caption + 页码）

### Figure 2 (p.23) ⭐深度解读
![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p23.png]]
> [!quote] caption
> FlowServe selects the appropriate DistFlow [10] backend based on the network fabric. For MLA models like DeepSeek and Kimi K2, both interconnects satisfy TTFT and TPOT SLAs.

> [!tip] 技术解读（多模态）
> I don't see a figure on this page—it consists entirely of body text (page 23 of a technical paper on FlowServe, covering DistFlow KV-transfer scheduling, heterogeneous prefill/decode deployment on Ascend NPUs, and the introduction to §5.2 "Disaggregated MoE-Attention").

The page does **reference** two figures, but they are not present on this page:
- **Figure 2** — referenced in the "Heterogeneous Prefill-Decode Deployment" paragraph for the cross-NPU KV-cache transfer path (Ascend 910B prefill ↔ Ascend 910C decode over RoCE/VPC via DistFlow).
- **Figures 18 and 19** — referenced at the very bottom of the page as illustrations of three new techniques for disaggregated MoE-Attention.

Because no figure or caption is actually rendered on the supplied image, I cannot describe its architecture/components/data flow or transcribe its caption verbatim. If you can share the page(s) containing Figure 2 or Figures 18/19, I'll provide the description and verbatim caption as requested.

### Figure 4 (p.8) ⭐深度解读
![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig04.png]]
*整页渲染: ![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p08.png]]*
> [!quote] caption
> Step 1: The sender’s serving engine invokes XCCL’s send, passing the source buffer in the app data area (e.g., KV cache), an eventID (e.g., number of sends), the receiver NPU’s ID, and the number of AIV cores to use. XCCL launches a kernel on the sender NPU. The send kernel uses MTE2 to copy data from the app data area to each AIV’s unified buffer in parallel. Step 2: The send kernel then reads th

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 4 – Distributed Send/Receive Workflow)**

**Architecture & Components:** Two symmetric NPUs (Sender left, Receiver right). Per-NPU blocks: AI Vector (Scalar + Vector units), DMA Engine, and Unified Buffer split as a Ping-Pong Buffer. Each connects to its Memory partition via MTE2/MTE3 links, partitioned into App Data Area (KV cache), Metadata Area (eventID, chunkID, TailPtr), and Managed Data Area (Ring with head/tail).

**Data Flow (8 steps):** ① Sender AIV loads app→unified buffer (MTE2). ② Unified buffer → receiver's on-chip memory via MTE3 (ping-pong overlaps with step 1). ③ Sender updates receiver's metadata. ④ Sender polls. ⑤ Receiver kernel validates metadata match. ⑥ Receiver copies back to its app area (MTE2/MTE3). ⑦ Receiver notifies sender via metadata. ⑧ Sender returns to CPU.

**Key Takeaway:** Ping-pong buffering in the unified buffer enables MTE2 and MTE3 to run concurrently, hiding transfer latency — with an optional DMA-engine zero-copy variant that bypasses the unified buffer at the cost of higher startup latency.

**Caption (verbatim):**
> Figure 4 | **Distributed Send/Receive Workflow.** *We show two NPUs and the distributed memory transfer protocol. We only show memory-semantic-based transfer using MTE2/MTE3 while remote memory copies can also be performed using the DMA engine. We also have a zero-copy version in which the send and receive kernels directly manipulate the app data area.*

### Figure 8 (p.12) ⭐深度解读
![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig08.png]]
*整页渲染: ![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p12.png]]*
> [!quote] caption
> Trade-off between MTE and DMA. To improve communication efficiency, we employ NPU-Direct Unified Remote Memory Access (URMA), a technique on Ascend NPUs similar to IBGDA on GPUs [15]. NPU-Direct URMA enables AIV cores to issue remote memory access requests directly to the DMA engine, bypassing both the host CPU and AI CPU as shown in §2.2. Although NPU-Direct URMA incurs higher startup latency com

> [!tip] 技术解读（多模态）
> I don't see an actual figure displayed on this page. Page 12 consists entirely of body text from a research paper, containing the following sections:

- Continuation of a discussion on expert/attention NPU provisioning (mentioning DeepSeek-R1/V3 with 288 experts)
- **Trampoline Forward** — describes a two-stage routing scheme (references Figure 8)
- **Trade-off between MTE and DMA** — discusses NPU-Direct URMA
- **Performance** — A2E/E2A latency results (172 μs / 193 μs)
- **Section 4: Scalable Serving System at SuperPod-scale**, with subsection **4.1 Overview** introducing FlowServe (references Figure 9 and Figure 10)

The page text *references* Figure 8, Figure 9, and Figure 10, but none of these figures are actually rendered on this page, and there is no caption to transcribe. If you'd like me to describe Figure 8 (the trampoline forward data flow) or Figures 9/10 (the redesigned FlowServe system) based on what the surrounding text describes, I can do that — but those visuals themselves are not present in the image you've shared. Could you share the page(s) where those figures actually appear?

### Figure 10 (p.12) ⭐深度解读
![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig10.png]]
*整页渲染: ![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p12.png]]*
> [!quote] caption
> This redesign centers on three key components: • First, we introduce the Data Parallel (DP) group abstraction, inspired by SGLang [24].

> [!tip] 技术解读（多模态）
> I don't see an actual figure displayed on this page. Page 12 consists entirely of body text from a research paper, containing the following sections:

- Continuation of a discussion on expert/attention NPU provisioning (mentioning DeepSeek-R1/V3 with 288 experts)
- **Trampoline Forward** — describes a two-stage routing scheme (references Figure 8)
- **Trade-off between MTE and DMA** — discusses NPU-Direct URMA
- **Performance** — A2E/E2A latency results (172 μs / 193 μs)
- **Section 4: Scalable Serving System at SuperPod-scale**, with subsection **4.1 Overview** introducing FlowServe (references Figure 9 and Figure 10)

The page text *references* Figure 8, Figure 9, and Figure 10, but none of these figures are actually rendered on this page, and there is no caption to transcribe. If you'd like me to describe Figure 8 (the trampoline forward data flow) or Figures 9/10 (the redesigned FlowServe system) based on what the surrounding text describes, I can do that — but those visuals themselves are not present in the image you've shared. Could you share the page(s) where those figures actually appear?

### Figure 12 (p.16) ⭐深度解读
![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig12.png]]
*整页渲染: ![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p16.png]]*
> [!quote] caption
> Step 1: Collecting Expert Load Distribution. First, we collect data on expert loads across NPUs. We define expert load as the total number of tokens routed to each expert within a given time interval. Token count directly reflects both communication overhead (MoE-Dispatch and

> [!tip] 技术解读（多模态）
> **Description (Figure 11):**

Figure 11 contains two sub-plots evaluating Expert Placement Load Balancing (EPLB):

**(a) Expert Load Skew:** A CDF of per-expert hit probability for a DeepSeek-R1 MoE layer under ShareGPT workload. The curve rises sharply near 0% and saturates near 1.0, with a red dashed line marking the equilibrium (~0.35%) hit probability. Most experts sit far below equilibrium, while a small tail of "hot" experts absorb disproportionate token traffic.

**(b) Latency vs. Batch Size:** Three routing strategies compared across batch sizes 8–192 on EP288:
- **MoE-Native** (blue): original token-to-expert assignment — highest latency (~150 µs at BS=192).
- **MoE-Balanced** (orange): EPLB replica placement — near-optimal.
- **MoE-Avg-Routing** (green): idealized uniform load — lower bound.

All scale linearly, but MoE-Balanced closely tracks the uniform-load baseline, recovering ~30% latency vs. Native.

**Key Takeaway:** EPLB mitigates straggler effects caused by skewed expert activation (30× token concentration) by replicating hot experts and using precomputed dispatch maps, achieving near-uniform-load latency without disturbing the natural router.

**Caption (verbatim):**
Figure 11 | A Study of Expert Placement Load Balancing. (a) We show the expert load distribution of a DeepSeek-R1 layer under the ShareGPT workload. The distribution is highly skewed—20% of experts receive more than the average load, and the hottest expert sees 30× more tokens than the average. (b) The setup uses EP288 and 1K-token sequence length. MoE-Avg-Routing, which forces uniform load across all experts; MoE-Native, which uses the original token-to-expert assignment; and MoE-Balanced, which applies our EPLB to balance expert load.

### Figure 17 (p.22) ⭐深度解读
![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig17.png]]
*整页渲染: ![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p22.png]]*
> [!quote] caption
> 1. A request first arrives at a randomly selected Job Executor (JE), which assigns it to a prefill

> [!tip] 技术解读（多模态）
> ## Figure 17 Description

The diagram illustrates a **disaggregated inference architecture** with a central **Job Executor (scheduler)** routing requests across independent **M prefill Task Executors (TEs)** and **N decode TEs** connected via full-mesh links. Each TE contains a shell wrapping a **Data-Parallel (DP) group** with a *Master* coordinating *Executors* that host a *Generator* and an *RTC-DistFlow* engine. The numbered workflow (1→9) traces a request: Job Executor assignment → prefill DP scheduling → RTC-DistFlow KV-cache registration → JE dispatch to decode TE → decode DP execution → deferred KV transfer → completion.

**Key takeaway:** Prefill (compute-bound, TP=4) and decode (memory-bound, TP=1) require distinct DP groupings; the system co-locates length-homogeneous requests per DP group to avoid stragglers that degrade tail latency and TTFT.

## Caption (verbatim)

> **Figure 17 | The Workflow of Disaggregated Prefill-Decode over CloudMatrix384.** *We support M prefill and N decode deployments with full-mesh connectivity. We illustrate the end-to-end workflow of sending a request from a prefill TE to a decode TE.*

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
h_{\ell,t} = \arg\max_{e} \text{ token\_count}[\ell][e][t].
$$

$$
L_\ell = \sum_{t\in T}\text{token\_count}[\ell][h_{\ell,t}][t].
$$

## 技术点深读（DEEP）

![[deep/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod.txt`（94761 字符）供引用检索。