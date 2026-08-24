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
> 【图文联合解读】**图文联合解读：**

图示两NPU经XCCL分布式传输协议交互：每端含AIV核、DMA引擎、片上Unified Buffer（Ping-Pong双区）；外存分App Data（KV$）、Metadata（eventID/chunkID/TailPtr）、Managed Data（Ring含head/tail）。8步红箭头串联MTE2读→MTE3写→元数据轮询全流程。

论证：①MTE2/MTE3内存语义实现zero-copy传输；②Ping-Pong双区使步骤1/2并行，隐藏片间延迟；③元数据轮询替代CPU中断，降低kernel launch开销；④同时支持DMA引擎双路径。

作用：作为CloudMatrix384跨NPU集合通信（PD分离推理中KV cache transfer）的硬件原生机制，支撑高吞吐低延迟MoE推理服务。

### Figure 8 (p.12) ⭐深度解读
![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig08.png]]
*整页渲染: ![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p12.png]]*
> [!quote] caption
> Trade-off between MTE and DMA. To improve communication efficiency, we employ NPU-Direct Unified Remote Memory Access (URMA), a technique on Ascend NPUs similar to IBGDA on GPUs [15]. NPU-Direct URMA enables AIV cores to issue remote memory access requests directly to the DMA engine, bypassing both the host CPU and AI CPU as shown in §2.2. Although NPU-Direct URMA incurs higher startup latency com

> [!tip] 技术解读（多模态）
> 【图文联合解读】图8展示A2E与E2A两种MoE通信原语。结构：上方Attention NPU组（含NPU/DMA/AIV/Mem(data)），下方Expert组（Mem含meta+data），红色箭头标注5步流程。A2E以最左侧Expert为trampoline：①Attention下发meta，②AIV处理，③拉取data回Attention，④⑤跨Expert级联更新meta与data；E2A反向：Expert先横向汇聚，再经Attention端AIV回流meta与data。

论证关键：采用两阶段路由，以trampoline NPU解耦meta与data传输，避免Attention↔Expert直连开销；结合URMA绕过主机CPU直连DMA，降低MTE与DMA延迟权衡。

作用：是CloudMatrix384 MoE推理中dispatch/combine的核心通信原语，支撑大规模专家并行的可扩展调度。

### Figure 10 (p.12) ⭐深度解读
![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig10.png]]
*整页渲染: ![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p12.png]]*
> [!quote] caption
> This redesign centers on three key components: • First, we introduce the Data Parallel (DP) group abstraction, inspired by SGLang [24].

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**核心对象与结构：** 该图展示 DeepSeek 单个 MoE 层在多 Die（Die 0–3 及 N–1/N）上的并行执行时间线，每 Die 依次执行 MLAPrologue（红）→ MLA（黄）→ All2All（绿）→ O → Gating 序列。关键视觉差异：(1) Die 0/1 的 MLA 块宽度明显大于 Die 2/3，量化呈现 MLA 延迟的 die 间差异；(2) 各 Die 的 All2All 被红色虚线垂直对齐，标示同步点；(3) Die 2/3 在 Gating 之后出现蓝色空白段，代表空闲等待。

**论证的技术结论：** 配合三种 Key Technique——① DP-LB 调度将不同 Die 的 MLA 延迟拉齐，避免 All2All 同步时的短板效应；② MLAPrologue 与 MLA 采用 TP=1 配合 All2All，避免 KV cache 重复；③ Proactive GC 回收 Gating 后空闲 Die 的 CPU 资源，消除 stragglers。

**论文作用：** 该图作为 FlowServe 推理架构中分布式 MoE 调度章节的标志性图示，直观串联"延迟变异—同步阻塞—资源闲置"三大痛点与其解决方案，是论文分布式执行优化的核心证据。

### Figure 12 (p.16) ⭐深度解读
![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig12.png]]
*整页渲染: ![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p16.png]]*
> [!quote] caption
> Step 1: Collecting Expert Load Distribution. First, we collect data on expert loads across NPUs. We define expert load as the total number of tokens routed to each expert within a given time interval. Token count directly reflects both communication overhead (MoE-Dispatch and

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示FlowServe EPLB四阶段闭环：①两NPU Die内MLA→Gating→Collect采集Expert Stats；②EPLB算法基于token计数（如表中Expert 1承载Token3的510 tokens/step）决策冗余专家布局；③Expert Reconfig更新Logical-Physical Expert Map；④LB→Dispatch按新映射执行，支持DeepSeek模型最高288路专家并行。原文以"token数代理负载"统一表征通信与计算开销，论证可同时优化MoE-Dispatch均衡与计算均衡，构成论文MoE推理服务的核心调度链路。

### Figure 17 (p.22) ⭐深度解读
![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig17.png]]
*整页渲染: ![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p22.png]]*
> [!quote] caption
> 1. A request first arrives at a randomly selected Job Executor (JE), which assigns it to a prefill

> [!tip] 技术解读（多模态）
> 【图文联合解读】**核心对象与结构：** 图示 M prefill × N decode 异构部署（示意各 3 组），含 Job Executor 全局调度器、Prefill/Decode 两侧 TE 集群，每 TE 为二级结构：TE Shell → DP（Master + 多 Executor）→ Generator + RTC-DistFlow，共 9 步箭头（1–9 及 8a/8b）刻画"JE 路由 → Prefill Shell → DP 内调度 → 跨 TE KV 直传 → Decode Shell → 重新生成"的端到端请求流。

**论证结论：** 证明解耦方案全互联可落地——RTC-DistFlow 实现低开销跨 TE KV cache 迁移，JE 统一弹性调度 M prefill/N decode 实例，达成资源解耦与负载均衡。

**论文作用：** 作为 CloudMatrix384 解耦推理架构的蓝图，衔接底层硬件拓扑与上层调度策略，为后续吞吐/延迟实验提供方法基线。

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