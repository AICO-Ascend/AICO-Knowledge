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
![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig02.png]]
*整页渲染: ![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p23.png]]*
> [!quote] caption
> FlowServe selects the appropriate DistFlow [10] backend based on the network fabric. For MLA models like DeepSeek and Kimi K2, both interconnects satisfy TTFT and TPOT SLAs.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**(a) 集群层：** CloudMatrix384 SuperPod 含 48 台 910C 服务器、共计 384 颗 NPU（每服务器配 2 CPU + 多 NPU + 1 NIC），三层互连并用：VPC（绿色，管理面）、UB（蓝色，节点内/间全互联总线）、RoCE（红色，RDMA 数据面）。

**(b) 芯片层：** 单颗 910C 由 Die 0 与 Die 1 经高带宽 NoC 互连构成；每 Die 采用解耦 DaVinci 架构，含 AIC（Cube + Buffer）与 AIV（Scalar + Vector + Unified Buffer），辅以 AI CPU、DMA、Misc 单元，通过 MTE2/MTE3 访存。

**论证作用：** 该图奠定全篇硬件底座——(1) 双 Die + NoC 提供片上高带宽，是 MoE-Attention 解耦、专家并行卸载的算力前提；(2) 图中显式的 RoCE/VPC/UB 三类互连直接对应后文"异构 Prefill-Decode 部署"中 910B 预填充 ↔ 910C 解码的 KV-cache 跨片传输路径，并支撑 FlowServe 依据网络拓扑选择 DistFlow 后端、保障 MLA 模型（DeepSeek、Kimi K2）的 TTFT/TPOT SLA。

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
> 【图文联合解读】**图文联合解读**

图示展示DeepSeek单MoE层在FlowServe上跨N+1个Die（Die 0至Die N）的并行执行时序：每Die流水线为 MLAPrilogue → MLA → All2All → O → Gating → Dispatch → MoE → Combine → Next Layer，两条红色虚线标出Dispatch前与Combine后的全局同步点。它支撑四项关键技术结论：①DP-LB均衡MLA时延波动；②MoE-LB均衡MoE时延；③Proactive GC消除CPU straggler；④MTP+Dynamic MicroBatch提升整体吞吐。在论文方法链路中，此图是调度优化方案的可视化骨架——把"DP组抽象（受SGLang启发）+四类负载/内存/batching策略"映射到具体流水时序，为后续Figure 11+的端到端性能评估提供机制锚点，证明四条技术可正交叠加而非冲突。

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