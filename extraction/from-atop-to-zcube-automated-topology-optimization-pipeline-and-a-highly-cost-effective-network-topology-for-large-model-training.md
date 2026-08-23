---
paper_num: "10"
title: "From ATOP to ZCube: Automated Topology Optimization Pipeline and A Highly Cost-Effective Network Topology for Large Model Training"
authors: "Pipeline and A Highly Cost-Effective Network Topology for Large Model Training Zihan Yan1, Dan Li1, Li Chen2, Dian Xiong3, Kaihui Gao2, Yiwei Zhang1, Rui Yan1, Menglei Zhang4, Bochun Zhang4, Zhuo Jiang4, Jianxi Ye4, Haib"
date: "2025/8/27"
arxiv: "https://dl.acm.org/doi/10.1145/3718958.3750503"
pdf: "papers/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training.pdf"
slug: "from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training"
tags: [training, architecture]
---

# From ATOP to ZCube: Automated Topology Optimization Pipeline and A Highly Cost-Effective Network Topology for Large Model Training

> [!abstract] 摘要（原文）
> 1\. 🚀 研究人员提出了 ATOP（自动化拓扑优化管道），通过将网络拓扑建模为一组可搜索的超参数，并结合高性能仿真器与进化算法，实现了大规模 GPU 集群网络架构的自动化设计与多目标优化。 2. 💡 该项目通过 ATOP 发现了一种新型拓扑结构 ZCube，其具备低网络直径、出色的容错能力和极高的成本效益，在多种规模的 GPU 集群中均表现优异。 3. 📈 仿真与实验结果表明，与现有的 Rail-optimized Fat-tree (ROFT)、Rail-only 和 HPN 等主流拓扑相比，ZCube 在保持相同全归约性能的前提下，显著提升了 LLM 训练速度，并将网络硬件成本降低了 26% 至 46%。

## 元信息
- **发表日期**: 2025/8/27
- **作者**: Pipeline and A Highly Cost-Effective Network Topology for Large Model Training Zihan Yan1, Dan Li1, Li Chen2, Dian Xiong3, Kaihui Gao2, Yiwei Zhang1, Rui Yan1, Menglei Zhang4, Bochun Zhang4, Zhuo Jiang4, Jianxi Ye4, Haib
- **arXiv**: https://dl.acm.org/doi/10.1145/3718958.3750503
- **本地 PDF**: `papers/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training.pdf`
- **页数**: 21

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig01.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p01.png]]*
> [!quote] caption
> ATOP search results on different GPU scales, each point representing a topology. For each scale, we label the three notable points in each plot: Best performance, Most

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

The figure is a 2×2 grid of scatter plots showing ATOP's topology search results at four GPU scales (256, 1024, 4k, 16k). Each subplot maps the performance–cost Pareto frontier: x-axis = GPT-3-22B/175B iteration time (s), y-axis = network cost ($), color = Total NIC Ports/GPU (1–8). Points represent individual candidate topologies; a Pareto-frontier curve traces optimal trade-offs. Reference topologies (HPN, Rail-only, BCube, 3-layer Rail-Optimized FT, Optimized FT) are explicitly labeled, along with three annotated extremes — *Best Performance*, *Cost-effective (ZCube)*, and *Budget-friendly*. The flow is: ATOP enumerates topologies → evaluates (time, cost, NIC count) → ranks on Pareto front → surfaces ZCube.

**Key takeaway:** ZCube consistently dominates prior SOTA (ROFT, Rail-only, HPN) on the Pareto curve across all scales, yielding 3–7% faster LLM training and 26–46% lower hardware cost.

**Caption (verbatim):**

Figure 1: ATOP search results on different GPU scales, each point representing a topology. For each scale, we label the three notable points in each plot: Best performance, Most Cost-effective, and Budget-friendly.

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig02.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p03.png]]*
> [!quote] caption
> GPT-3 training timeline on rank 0 of classical in- terleaved 1F1B schedule, excluding TP communication as it typically occurs on the intra-server network. • Expert parallelism (EP), used in mixture-of-expert (MoE) models, generates all-to-all traffic among GPUs [45]. We learn from LLM researchers and training frameworks that EP traffic may co-exist with DP traffic but rarely with PP traffic [45, 4

> [!tip] 技术解读（多模态）
> ## Figure Description

**Architecture/Components:** Figure 2 is a horizontal Gantt-style timeline visualization for a single GPU rank executing GPT-3 training under the classical interleaved 1F1B schedule. It contains four parallel tracks:
- **Comp** (computation): alternating **F** (Forward, green) and **B** (Backward, yellow) micro-batches
- **DP Comm** (data-parallel collectives): **AG** (All-Gather) and **RS** (Reduce-Scatter) operations (peach)
- **PP Send**: pipeline-parallel activation sends (blue ticks)
- **PP Recv**: pipeline-parallel activation receives (red ticks)

**Data Flow:** Time progresses left→right; computation phases are interleaved 1-forward/1-backward, while DP collectives and PP send/recv events are overlaid to show when each overlaps with compute.

**Key Takeaway:** The visualization reveals five distinct traffic periods (DP-only, PP-only, EP-only, mixed DP-PP, mixed DP-EP) that can co-occur on the same GPU—a foundational observation motivating ATOP's topology co-design.

## Caption (Verbatim)

**Figure 2: GPT-3 training timeline on rank 0 of classical interleaved 1F1B schedule, excluding TP communication as it typically occurs on the intra-server network.**

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig03.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p04.png]]*
> [!quote] caption
> (a) The max number of flow per 100 Gbps under all-to-all traffic in a 256-GPUs topology. (b) The performance degradation of GPT-3 training after a Single ToR Fault in a 4k-GPUs topology. ZCube and Best-Perf are new topologies generated by ATOP. human intuition that struggles to reason about increasingly vast design spaces.

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 3):**

The figure contains two paired bar charts comparing six GPU cluster topologies (BCube, ROFT, Rail-only, HPN, ZCube, Best-perf) along cost-vs-performance axes.

**(a) Throughput chart** — Y-axis: max flow per 100 Gbps (0–3). Three bars per topology: ECMP+PXN OFF (light blue), ECMP+PXN ON (yellow), and Ideal LB (orange). ROFT and Best-perf peak highest (~2.5–2.7); Best-perf costs 250% while ROFT is the 100% baseline.

**(b) Fault-tolerance chart** — Y-axis: GPT-3 iteration time (s, 0–6). Two bars per topology: Single ToR Fault (blue) vs. No Switch Fault (yellow), with a dashed line plotting degradation percentage. ROFT/Rail-only degrade ~46%, while ZCube (-2.8%) and HPN (~0%) remain stable.

**Key Technical Takeaway:** ZCube (ATOP-generated, 52% cost) dominates the trade-off — it nearly matches ROFT's all-to-all throughput while eliminating ROFT's severe 46.9% fault-tolerance penalty, demonstrating that automated topology search can simultaneously cut cost and improve reliability.

**Caption (verbatim):**
Figure 3: (a) The max number of flow per 100 Gbps under all-to-all traffic in a 256-GPUs topology. (b) The performance degradation of GPT-3 training after a Single ToR Fault in a 4k-GPUs topology. ZCube and Best-Perf are new topologies generated by ATOP.

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig04.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p05.png]]*
> [!quote] caption
> Overview of ATOP allows the system to explore novel topology designs automatically, not limited to variants or combinations of existing ones. It can produce high-performance asymmetric topologies, such as ZCube (§5), which requires additional ports for middle-layer switches.

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

Figure 4 illustrates the ATOP (Automated Topology Optimization Pipeline) architecture, comprising two main components: **Topology Modeling** and the **Optimization Loop**. Data flow: *Topology Constraints* and *Optimization Objectives* feed into Topology Modeling, which defines the search space passed to the Optimizer. Inside the loop, the **Topology Optimizer** generates *New Topologies* evaluated by the **Topology Evaluator**, whose feedback refines the search space iteratively. The entire pipeline targets *Topologists' Performance* and outputs the *Optimal Topology*.

**Key technical takeaway:** ATOP decouples structural modeling from search, enabling automatic exploration beyond hand-crafted DCN designs — yielding high-performance asymmetric topologies (e.g., ZCube) that human designers may overlook.

**Caption (verbatim):**

Figure 4: Overview of ATOP

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig05.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p06.png]]*
> [!quote] caption
> Examples of constructing inter-layer and intra-layer connections in ATOP. Unmentioned hyperparameters = 0.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Figure 5** illustrates ATOP's 3-step topology construction process for two connection types:

**Inter-layer (top):** Hierarchical GPU-switch stack → (1) set switch-node counts per layer (N₂=4, N₃=2), (2) define per-layer block counts (H¹ᵢⱼ), (3) specify inter-block wiring (Eᵢⱼ).

**Intra-layer (bottom):** 2D node grid (Dim 1 × Dim 2) → (1) choose per-dimension sizes (S¹ᵢ=4, S²ᵢ=2) partitioning nodes into multi-dimensional coordinates, (2) set outward-connection counts per dimension (P¹ᵢ=3, P²ᵢ=1), (3) compute connection pattern via matrix A and offset C hyperparameters.

## Key Technical Takeaway

ATOP abstracts DCN topology generation through a unified hyperparameter search: a small set of integer hyperparameters (Sᵏᵢ, Pᵏᵢ, Aⁱᵏᵣₜ, Cⁱᵏₜ) deterministically generates complex multi-dimensional architectures (Dragonfly, Torus, HyperX), enabling flexible modeling of both hierarchical and peer-to-peer connectivity without enumerating topologies. (72 words)

## Caption (verbatim)

**Figure 5: Examples of constructing inter-layer and intra-layer connections in ATOP. Unmentioned hyperparameters = 0.**

### Figure 6 (p.9) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig06.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p09.png]]*
> [!quote] caption
> During the 4k GPUs search process: (a) The Pareto- optimal topologies generated by ATOP; (b) All the topologies generated by ATOP.

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 7, with Figure 6 context):**

The page presents two paired topology-search scatter plots visualizing ATOP's GPU network optimization output.

**Figure 6 (left):** Two panels—(a) Pareto-optimal and (b) all generated topologies—for a 4k-GPU search. Axes plot Network Cost ($) vs. GPT-3-175B iteration time (s); points are color-coded by Total NIC Ports/GPU (1–8).

**Figure 7 (right):** Two higher-scale panels—(a) adjusting an existing 4k-GPU DCN and (b) expanding 1k→4k GPUs. Axes span $1–5×10⁷ cost vs. 2–7s iteration time, colored by NIC Ports/GPU. Labeled reference topologies include Best Performance (upper-left), Budget-friendly (lower-right), HPN, BCube, Rail-only, and 3-layer Rail-Optimized FT, with **ZCube** marked at the Pareto inflection point.

**Key takeaway:** ZCube consistently sits at the cost–performance inflection point across scales, making it the most cost-effective topology while remaining competitive with the highest-performance designs.

**Caption (Figure 7, verbatim):**
*Figure 7: (a) The search results of ATOP when adjusting an existing 4k-GPU DCN. (b) The search results when expanding a DCN from 1k GPUs to 4k GPUs.*

### Figure 7 (p.9) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig07.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p09.png]]*
> [!quote] caption
> (a) The search results of ATOP when adjusting an existing 4k-GPU DCN. (b) The search results when expanding a DCN from 1k GPUs to 4k GPUs. be unfair to other topologies. However, in Case 3, even expanding directly to a 3-layer ROFT requires adding some links.

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 7, with Figure 6 context):**

The page presents two paired topology-search scatter plots visualizing ATOP's GPU network optimization output.

**Figure 6 (left):** Two panels—(a) Pareto-optimal and (b) all generated topologies—for a 4k-GPU search. Axes plot Network Cost ($) vs. GPT-3-175B iteration time (s); points are color-coded by Total NIC Ports/GPU (1–8).

**Figure 7 (right):** Two higher-scale panels—(a) adjusting an existing 4k-GPU DCN and (b) expanding 1k→4k GPUs. Axes span $1–5×10⁷ cost vs. 2–7s iteration time, colored by NIC Ports/GPU. Labeled reference topologies include Best Performance (upper-left), Budget-friendly (lower-right), HPN, BCube, Rail-only, and 3-layer Rail-Optimized FT, with **ZCube** marked at the Pareto inflection point.

**Key takeaway:** ZCube consistently sits at the cost–performance inflection point across scales, making it the most cost-effective topology while remaining competitive with the highest-performance designs.

**Caption (Figure 7, verbatim):**
*Figure 7: (a) The search results of ATOP when adjusting an existing 4k-GPU DCN. (b) The search results when expanding a DCN from 1k GPUs to 4k GPUs.*

### Figure 8 (p.10) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig08.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p10.png]]*
> [!quote] caption
> (a) A ZCube(n, k+1) is constructed from 𝑛ZCube(n, k) and 𝑛𝑘switches. (b) An example of ZCube(2, 3). (c) An example of ZCube(84,3)-partial. ZCube(𝑛,𝑘+ 1) is equipped with (𝑘+ 1) NIC ports numbered from level-0 to level-𝑘. In addition to equipping each GPU with multi- port NICs [41], ZCube can also be implemented using multiple NICs for each GPU. For instance, when constructing ZCube(𝑛, 2), each GPU

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 8) — Description**

The figure depicts the recursive hierarchical construction of the ZCube topology across three panels:

- **(a) General construction:** ZCube(n, k+1) is built by interconnecting *n* copies of ZCube(n, k) at the lower levels (Level 0…k−1) with *n^k* new switches at the top (Level k). GPUs (orange) sit at Level 0; switches (teal) populate intermediate levels.
- **(b) Concrete example — ZCube(2, 3):** Eight GPUs labeled 000…111 connect through Level-0 and Level-1 switches to four Level-2 switches.
- **(c) ZCube(84, 3)-partial:** 84 GPUs per pod (Pod 0…Pod 83), each pod containing 84 Level-1 switches and one Level-0 sub-structure, aggregated under 3,528 Level-2 switches (0…3527).

**Data flow:** GPU ↔ Level-0 ↔ … ↔ Level-(k−1) switches ↔ Level-k switches ↔ … ↔ peer GPU, with hop count equal to k (the diameter).

**Key technical takeaway (≤120 words):** ZCube is an intentionally *asymmetric* DCN topology that exploits port-count asymmetry between leaf (2n ports) and intermediate (3n ports) switches to achieve very small diameter. ZCube(n,2) links n² GPUs with diameter 2, and ZCube(n,4) links n⁴ GPUs with diameter 4 — surpassing 3-layer Fat-Tree, which connects only 524 288 GPUs (16.8 %) at diameter 5 with the same 128-port switches. Because GPUs need only 200 Gbps NICs (vs. 400 Gbps in ROFT) and fewer switches are used, ZCube cuts switch count by 33–60 % and optical-transceiver cost by 25–50 %, while improving fault tolerance via fewer failure points.

**Caption (verbatim):**

*Figure 8: (a) A ZCube(n, k+1) is constructed from n ZCube(n, k) and n^k switches. (b) An example of ZCube(2, 3). (c) An example of ZCube(84,3)-partial.*

### Figure 9 (p.11) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig09.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p11.png]]*
> [!quote] caption
> The training iteration time for GPT-3 175B and MoE-GPT models and the corresponding network costs on various topologies, under different numbers of GPUs.

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 9)

**Architecture/Components:** A three-panel grouped bar chart comparing training iteration time (s, y-axis) across six network topologies — ZCube, HPN, Rail-only, ROFT, BCube, Dragonfly (x-axis) — for two models (GPT-3 175B in cyan, MoE-GPT in orange) at three scales: 1024 GPUs, 4096 GPUs, and 16384 GPUs. Network costs ($M) are annotated beneath each topology label. Values are labeled atop each bar.

**Data Flow:** For each scale panel → topology group → model pair, the chart conveys iteration latency; cost annotations allow cost/latency trade-off comparison across scales.

**Key Technical Takeaway:** ZCube(128,2) consistently delivers the lowest or near-lowest iteration times at all three scales while incurring the cheapest network cost (≈$3.99M at 1024 GPUs, $15.20M at 4096 GPUs, $64.20M at 16384 GPUs), outperforming HPN/Rail-only/ROFT on both axes — and the gap widens at larger scales (e.g., 13.79 s for MoE-GPT on Dragonfly vs. lower on ZCube at 16384 GPUs).

## Caption (verbatim)

**Figure 9: The training iteration time for GPT-3 175B and MoE-GPT models and the corresponding network costs on various topologies, under different numbers of GPUs.**

**Figure 10: CDF of PP flow completion time during a GPT-3 175B training iteration on 16384 GPUs.**

### Figure 10 (p.11) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig10.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p11.png]]*
> [!quote] caption
> CDF of PP flow completion time during a GPT-3 175B training iteration on 16384 GPUs. GPU clusters, the failure probability of a single switch is 0.03%.

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 9)

**Architecture/Components:** A three-panel grouped bar chart comparing training iteration time (s, y-axis) across six network topologies — ZCube, HPN, Rail-only, ROFT, BCube, Dragonfly (x-axis) — for two models (GPT-3 175B in cyan, MoE-GPT in orange) at three scales: 1024 GPUs, 4096 GPUs, and 16384 GPUs. Network costs ($M) are annotated beneath each topology label. Values are labeled atop each bar.

**Data Flow:** For each scale panel → topology group → model pair, the chart conveys iteration latency; cost annotations allow cost/latency trade-off comparison across scales.

**Key Technical Takeaway:** ZCube(128,2) consistently delivers the lowest or near-lowest iteration times at all three scales while incurring the cheapest network cost (≈$3.99M at 1024 GPUs, $15.20M at 4096 GPUs, $64.20M at 16384 GPUs), outperforming HPN/Rail-only/ROFT on both axes — and the gap widens at larger scales (e.g., 13.79 s for MoE-GPT on Dragonfly vs. lower on ZCube at 16384 GPUs).

## Caption (verbatim)

**Figure 9: The training iteration time for GPT-3 175B and MoE-GPT models and the corresponding network costs on various topologies, under different numbers of GPUs.**

**Figure 10: CDF of PP flow completion time during a GPT-3 175B training iteration on 16384 GPUs.**

### Figure 11 (p.12) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig11.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p12.png]]*
> [!quote] caption
> The topology diagrams of ROFT and ZCube on a real testbed. 1M 4M 16M 64M 256M 1G 4G 16G

> [!tip] 技术解读（多模态）
> ## Figure 11 Description (Main Figure)

**Architecture & Components:**
- **(a) ROFT topology:** Traditional 2-tier fat-tree. 4 Spine Switches (top) connect to 4 Leaf Switches (middle), each Leaf links to 4 servers. Every server hosts 4 NICs (NIC1–NIC4) driving 4 GPUs (GPU1–GPU4). All links run at 400 Gbps (blue).
- **(b) ZCube topology:** Novel 2-tier design using 4 L2 Switches (top) and 4 L1 Switches (middle) in a denser, more symmetric mesh arrangement. Same 4-server, 4-GPU/server layout, but every link operates at only 200 Gbps (purple).

**Data flow:** Packets traverse Server NIC → Leaf/L1 switch → Spine/L2 switch → peer Leaf/L1 → destination NIC → GPU, identical end-to-end path on both fabrics.

**Key takeaway (≤120 words):** Despite using lower-rate (200 Gbps) links and only 48×200G links versus ROFT's 32×400G links, ZCube matches ROFT's ideal bisection bandwidth and identical All-reduce/All-to-all throughput (Fig. 12). Its shorter network diameter accelerates parameter-plane flows, yielding up to 7% faster LLM training and 26–46% lower network cost. Additionally, ZCube's richer L1↔L2 mesh provides stronger fault tolerance without sacrificing performance.

**Caption (verbatim):**
"Figure 11: The topology diagrams of ROFT and ZCube on a real testbed."

### Figure 12 (p.12) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig12.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p12.png]]*
> [!quote] caption
> Collective communication performance on real- world deployment. ZCube and ROFT achieve the same all-reduce and all-to-all perfor- mance, while ZCube reduces hardware cost by 25% by using only 48×200G links, compared to ROFT’s 32×400G links.

> [!tip] 技术解读（多模态）
> ## Figure 11 Description (Main Figure)

**Architecture & Components:**
- **(a) ROFT topology:** Traditional 2-tier fat-tree. 4 Spine Switches (top) connect to 4 Leaf Switches (middle), each Leaf links to 4 servers. Every server hosts 4 NICs (NIC1–NIC4) driving 4 GPUs (GPU1–GPU4). All links run at 400 Gbps (blue).
- **(b) ZCube topology:** Novel 2-tier design using 4 L2 Switches (top) and 4 L1 Switches (middle) in a denser, more symmetric mesh arrangement. Same 4-server, 4-GPU/server layout, but every link operates at only 200 Gbps (purple).

**Data flow:** Packets traverse Server NIC → Leaf/L1 switch → Spine/L2 switch → peer Leaf/L1 → destination NIC → GPU, identical end-to-end path on both fabrics.

**Key takeaway (≤120 words):** Despite using lower-rate (200 Gbps) links and only 48×200G links versus ROFT's 32×400G links, ZCube matches ROFT's ideal bisection bandwidth and identical All-reduce/All-to-all throughput (Fig. 12). Its shorter network diameter accelerates parameter-plane flows, yielding up to 7% faster LLM training and 26–46% lower network cost. Additionally, ZCube's richer L1↔L2 mesh provides stronger fault tolerance without sacrificing performance.

**Caption (verbatim):**
"Figure 11: The topology diagrams of ROFT and ZCube on a real testbed."

### Figure 13 (p.15) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig13.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]]*
> [!quote] caption
> In the search results of Case 3, the comparison between the number of modified links (another cost metric) and training performance.

> [!tip] 技术解读（多模态）
> **Figure 14 — "16k GPUs Multi-tenant DCN Search" (main figure for Use Case 4)**

**Architecture / components / data flow:** A 2-D scatter plot where each point is a candidate topology evaluated by ATOP's search pipeline. X-axis = Average Iteration Time (s) for GPT-3-175B training (lower = faster); Y-axis = Network Cost ($) (lower = cheaper); color encodes Total NIC Ports/GPU (1→8 gradient). A blue Pareto-frontier curve traces non-dominated points. Labeled reference topologies are overlaid: Best Performance, Cost-effective (ZCube), 3-layer Rail-Optimized FT, HPN, Rail-only, BCube. Two shaded regions — "Cost-effective (ZCube)" upper-right and "Budget-friendly" lower-left — bracket the search space.

**Key technical takeaway:** ZCube lands on the *reflection point* of the Pareto frontier in multi-tenant scenarios, simultaneously capping cost while preserving near-best training throughput — confirming it as the most cost-effective topology when 16k GPUs serve four co-located tenants.

**Caption (verbatim):** *Figure 14: The search results of ATOP when building a new data center for multi-tenancy.*

### Figure 14 (p.15) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig14.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]]*
> [!quote] caption
> The search results of ATOP when building a new data center for multi-tenancy.

> [!tip] 技术解读（多模态）
> **Figure 14 — "16k GPUs Multi-tenant DCN Search" (main figure for Use Case 4)**

**Architecture / components / data flow:** A 2-D scatter plot where each point is a candidate topology evaluated by ATOP's search pipeline. X-axis = Average Iteration Time (s) for GPT-3-175B training (lower = faster); Y-axis = Network Cost ($) (lower = cheaper); color encodes Total NIC Ports/GPU (1→8 gradient). A blue Pareto-frontier curve traces non-dominated points. Labeled reference topologies are overlaid: Best Performance, Cost-effective (ZCube), 3-layer Rail-Optimized FT, HPN, Rail-only, BCube. Two shaded regions — "Cost-effective (ZCube)" upper-right and "Budget-friendly" lower-left — bracket the search space.

**Key technical takeaway:** ZCube lands on the *reflection point* of the Pareto frontier in multi-tenant scenarios, simultaneously capping cost while preserving near-best training throughput — confirming it as the most cost-effective topology when 16k GPUs serve four co-located tenants.

**Caption (verbatim):** *Figure 14: The search results of ATOP when building a new data center for multi-tenancy.*

### Figure 15 (p.15) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig15.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]]*
> [!quote] caption
> The search results of ATOP when building a new heterogeneous data center with strict search space con- straints.

> [!tip] 技术解读（多模态）
> **Figure 14 — "16k GPUs Multi-tenant DCN Search" (main figure for Use Case 4)**

**Architecture / components / data flow:** A 2-D scatter plot where each point is a candidate topology evaluated by ATOP's search pipeline. X-axis = Average Iteration Time (s) for GPT-3-175B training (lower = faster); Y-axis = Network Cost ($) (lower = cheaper); color encodes Total NIC Ports/GPU (1→8 gradient). A blue Pareto-frontier curve traces non-dominated points. Labeled reference topologies are overlaid: Best Performance, Cost-effective (ZCube), 3-layer Rail-Optimized FT, HPN, Rail-only, BCube. Two shaded regions — "Cost-effective (ZCube)" upper-right and "Budget-friendly" lower-left — bracket the search space.

**Key technical takeaway:** ZCube lands on the *reflection point* of the Pareto frontier in multi-tenant scenarios, simultaneously capping cost while preserving near-best training throughput — confirming it as the most cost-effective topology when 16k GPUs serve four co-located tenants.

**Caption (verbatim):** *Figure 14: The search results of ATOP when building a new data center for multi-tenancy.*

### Figure 16 (p.16) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig16.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p16.png]]*
> [!quote] caption
> During the ATOP optimization process: (a) The relationship between the number of Pareto-optimal topologies and the total number of topologies generated by ATOP; (b) The Jaccard distance between the Pareto-optimal topology sets of different generations; (c) The relationship between the HyperVolume indicator and the total number of topologies.

> [!tip] 技术解读（多模态）
> **Figure 16 — ATOP Convergence Analysis**

The figure comprises three side-by-side line plots, each charting a convergence metric (y-axis) against the total number of topologies searched (x-axis, 0–100k) for four GPU scales — 256, 1024, 4096, and 16384 GPUs — distinguished only by color.

- **(a) Num of Pareto-optimal** rises monotonically and saturates (≈4 500–5 200), confirming the Pareto front grows then stabilizes; larger GPU scales reach higher plateaus.
- **(b) Jaccard Distance** between consecutive Pareto-optimal sets decays rapidly from ~0.55 toward 0, indicating inter-generation set overlap converges.
- **(c) HyperVolume** indicator climbs quickly toward ≈1.0 and plateaus, signaling coverage of objective space is essentially complete.

**Key takeaway:** Across all four scales, ATOP's NSGA-II-based search exhibits consistent dual convergence — the Pareto-optimal topology set and the HyperVolume both stabilize well before exhausting the 100k topology budget, validating search efficiency.

**Caption (verbatim):**
"Figure 16: During the ATOP optimization process: (a) The relationship between the number of Pareto-optimal topologies and the total number of topologies generated by ATOP; (b) The Jaccard distance between the Pareto-optimal topology sets of different generations; (c) The relationship between the HyperVolume indicator and the total number of topologies."

### Figure 17 (p.17) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig17.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p17.png]]*
> [!quote] caption
> Two scenarios degrade all-to-all performance: (a) ECMP hash collision: In Non-blocking 2-layer Rail-Optimized

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Figure 17** illustrates two network topology scenarios that degrade all-to-all communication performance:

**(a) ROFT (2-layer Rail-Optimized Fat-Tree):** A 3-tier architecture with Spine Switches (×M) at the top, Leaf Switches (×K) within each Pod (×R), and GPUs (×K) per server (×M). During cross-pod communication, multiple flows traverse identical paths, causing **ECMP hash collisions** at spine/leaf uplinks, leading to bandwidth contention.

**(b) BCube(n, 2):** A server-centric topology with Level-1 Switches (×n) and Level-0 Switches (×n), where each GPU's NIC must perform **forwarding** for peer GPUs, consuming NIC bandwidth and breaking full bisection guarantees.

**Key takeaway:** ZCube avoids both pitfalls by combining the non-blocking property of Fat-Trees (no hash collisions) with the low-diameter property of BCube (no NIC-level forwarding required).

## Caption (verbatim)

**Figure 17:** Two scenarios degrade all-to-all performance: (a) ECMP hash collision: In Non-blocking 2-layer Rail-Optimized Fat-Tree (*N* represents the total number of GPUs, *N* = *RMK*), ECMP may cause flow collisions during cross-pod all-to-all communication. (b) Not a full bisection bandwidth topology: In BCube(*n*, 2), GPU's NIC needs to forward traffic for other GPUs, which makes it not a full bisection bandwidth topology.

### Figure 18 (p.17) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig18.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p17.png]]*
> [!quote] caption
> The average JCT for group all-to-all communica- tion under different topologies with link failures on 4096 GPUs, with shading representing the standard deviation of the JCT.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Figure 17** illustrates two network topology scenarios that degrade all-to-all communication performance:

**(a) ROFT (2-layer Rail-Optimized Fat-Tree):** A 3-tier architecture with Spine Switches (×M) at the top, Leaf Switches (×K) within each Pod (×R), and GPUs (×K) per server (×M). During cross-pod communication, multiple flows traverse identical paths, causing **ECMP hash collisions** at spine/leaf uplinks, leading to bandwidth contention.

**(b) BCube(n, 2):** A server-centric topology with Level-1 Switches (×n) and Level-0 Switches (×n), where each GPU's NIC must perform **forwarding** for peer GPUs, consuming NIC bandwidth and breaking full bisection guarantees.

**Key takeaway:** ZCube avoids both pitfalls by combining the non-blocking property of Fat-Trees (no hash collisions) with the low-diameter property of BCube (no NIC-level forwarding required).

## Caption (verbatim)

**Figure 17:** Two scenarios degrade all-to-all performance: (a) ECMP hash collision: In Non-blocking 2-layer Rail-Optimized Fat-Tree (*N* represents the total number of GPUs, *N* = *RMK*), ECMP may cause flow collisions during cross-pod all-to-all communication. (b) Not a full bisection bandwidth topology: In BCube(*n*, 2), GPU's NIC needs to forward traffic for other GPUs, which makes it not a full bisection bandwidth topology.

### Figure 19 (p.18) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig19.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p18.png]]*
> [!quote] caption
> Comparison between packet-level network simulation (with packet spraying for load balancing) and the real-world testbed in §6.2. I

> [!tip] 技术解读（多模态）
> ## Description of Figure 19

The figure consists of **four side-by-side line plots** comparing BusBw (GB/s) versus Data Size (1M–16G) for two traces: **TestBed** (blue solid) and **Simulation** (orange dashed).

**Components/Panels:**
- **Panel 1:** ROFT Allreduce (Y-axis 0–200 GB/s)
- **Panel 2:** ZCube Allreduce (Y-axis 0–200 GB/s)
- **Panel 3:** ROFT All-to-all (Y-axis 0–50 GB/s)
- **Panel 4:** ZCube All-to-all (Y-axis 0–50 GB/s)

**Data flow:** Each plot shows measured bandwidth rising with message size and saturating at large payloads. The two curves nearly overlap across the full size range in all four panels.

**Key technical takeaway (≤120 words):** Packet-level simulation using packet-spraying load balancing tracks the real testbed with very small deviation across both ROFT and ZCube topologies and across both Allreduce and All-to-all collectives. The simulator accurately reproduces the sub-saturation ramp-up regime (1M–64M) as well as the saturated plateau (~200 GB/s for Allreduce, ~50 GB/s for All-to-all). This tight alignment validates using the simulator as a faithful proxy for hardware measurement when evaluating topology designs.

## Caption (verbatim)

**Figure 19:** Comparison between packet-level network simulation (with packet spraying for load balancing) and the real-world testbed in §6.2.

### Figure 20 (p.19) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig20.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p19.png]]*
> [!quote] caption
> Comparison of the CDF of flow completion times between NS-3 and flow-level simulators.

> [!tip] 技术解读（多模态）
> # Figure 20 Description

**Architecture/Components:** The figure presents two side-by-side Cumulative Distribution Function (CDF) plots comparing flow-level simulator results against packet-level NS-3 simulations. **Left panel ("All-to-all FCT CDF")** plots CDF vs. flow completion time (0.8–2.0 ms), comparing NS-3 (blue) vs. Flow-level simulator (orange). **Right panel ("GPT-3-22B Training FCT CDF")** plots CDF vs. flow completion time (0.000–0.030 ms), comparing Astra-sim+NS-3 (blue) vs. Astra-sim+Flow-level simulator (orange). The two-panel layout cross-validates simulators across both raw collective-communication workloads and realistic training traces.

**Key Technical Takeaway:** The flow-level simulator closely tracks NS-3 results across both microbenchmarks and large-model training, with relative errors bounded under ~7% (per Table 5), validating it as a low-fidelity-but-fast surrogate for evaluating GPU-cluster network topologies.

# Caption (Verbatim)

**Figure 20:** Comparison of the CDF of flow completion times between NS-3 and flow-level simulators.

### Figure 21 (p.20) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig21.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]]*
> [!quote] caption
> ROFT topology for a 16384 GPU cluster based on 51.2 Tbps switches.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The page presents a comparative study of four network topologies for a **16,384 GPU cluster** built from 51.2 Tbps switches:

1. **Figure 21 – ROFT (Rail-Optimized Fat-Tree)**: 3-tier hierarchy: Core (128×400G) → Super-Pod Spines (64×400G) → Pod Leaves (64×400G) → 8-NIC servers. Groups 512 servers per Pod, 2,048 per Super-Pod.
2. **Figure 22 – Rail-only**: 2-layer CLOS per rail. 8 rail interconnects (L2 SWs) each fan out to all pods' L1 SWs; every server uses 8 NICs pinned to one rail.
3. **Figure 23 – HPN (dual-port ROFT)**: Spines (128×400G) → Leaves (128×200G) → dual-port servers (2×200G); folds two Fat-Tree pods into one.
4. **Figure 24 – ZCube(128,2)**: L2 SWs (128×200G + 128×200G dual-port) connect to L1 SWs serving 16 servers each, with cross-pod L2↔L1 diagonal links.

**Key takeaway:** The four designs trade switch count, cabling, and oversubscription differently—ROFT maximizes per-server bandwidth with more switches, while HPN and ZCube reduce switch/cabling cost by leveraging dual-port NICs and richer connectivity patterns.

## Captions (verbatim)

**Figure 21:** ROFT topology for a 16384 GPU cluster based on 51.2 Tbps switches.

**Figure 22:** Rail-only topology for a 16384 GPU cluster based on 51.2 Tbps switches. Each Rail-interconnection adopts a 2-layer CLOS architecture, consistent with [51] and [57].

**Figure 23:** HPN topology (dual-port designs for ROFT) for a 16384 GPU cluster based on 51.2 Tbps switches.

**Figure 24:** ZCube(128,2) topology for a 16384 GPU cluster based on 51.2 Tbps switches.

### Figure 22 (p.20) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig22.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]]*
> [!quote] caption
> Rail-only topology for a 16384 GPU cluster based on 51.2 Tbps switches. Each Rail-interconnection adopts a 2-layer CLOS architecture, consistent with [51] and [57].

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The page presents a comparative study of four network topologies for a **16,384 GPU cluster** built from 51.2 Tbps switches:

1. **Figure 21 – ROFT (Rail-Optimized Fat-Tree)**: 3-tier hierarchy: Core (128×400G) → Super-Pod Spines (64×400G) → Pod Leaves (64×400G) → 8-NIC servers. Groups 512 servers per Pod, 2,048 per Super-Pod.
2. **Figure 22 – Rail-only**: 2-layer CLOS per rail. 8 rail interconnects (L2 SWs) each fan out to all pods' L1 SWs; every server uses 8 NICs pinned to one rail.
3. **Figure 23 – HPN (dual-port ROFT)**: Spines (128×400G) → Leaves (128×200G) → dual-port servers (2×200G); folds two Fat-Tree pods into one.
4. **Figure 24 – ZCube(128,2)**: L2 SWs (128×200G + 128×200G dual-port) connect to L1 SWs serving 16 servers each, with cross-pod L2↔L1 diagonal links.

**Key takeaway:** The four designs trade switch count, cabling, and oversubscription differently—ROFT maximizes per-server bandwidth with more switches, while HPN and ZCube reduce switch/cabling cost by leveraging dual-port NICs and richer connectivity patterns.

## Captions (verbatim)

**Figure 21:** ROFT topology for a 16384 GPU cluster based on 51.2 Tbps switches.

**Figure 22:** Rail-only topology for a 16384 GPU cluster based on 51.2 Tbps switches. Each Rail-interconnection adopts a 2-layer CLOS architecture, consistent with [51] and [57].

**Figure 23:** HPN topology (dual-port designs for ROFT) for a 16384 GPU cluster based on 51.2 Tbps switches.

**Figure 24:** ZCube(128,2) topology for a 16384 GPU cluster based on 51.2 Tbps switches.

### Figure 23 (p.20) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig23.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]]*
> [!quote] caption
> HPN topology (dual-port designs for ROFT) for a 16384 GPU cluster based on 51.2 Tbps switches.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The page presents a comparative study of four network topologies for a **16,384 GPU cluster** built from 51.2 Tbps switches:

1. **Figure 21 – ROFT (Rail-Optimized Fat-Tree)**: 3-tier hierarchy: Core (128×400G) → Super-Pod Spines (64×400G) → Pod Leaves (64×400G) → 8-NIC servers. Groups 512 servers per Pod, 2,048 per Super-Pod.
2. **Figure 22 – Rail-only**: 2-layer CLOS per rail. 8 rail interconnects (L2 SWs) each fan out to all pods' L1 SWs; every server uses 8 NICs pinned to one rail.
3. **Figure 23 – HPN (dual-port ROFT)**: Spines (128×400G) → Leaves (128×200G) → dual-port servers (2×200G); folds two Fat-Tree pods into one.
4. **Figure 24 – ZCube(128,2)**: L2 SWs (128×200G + 128×200G dual-port) connect to L1 SWs serving 16 servers each, with cross-pod L2↔L1 diagonal links.

**Key takeaway:** The four designs trade switch count, cabling, and oversubscription differently—ROFT maximizes per-server bandwidth with more switches, while HPN and ZCube reduce switch/cabling cost by leveraging dual-port NICs and richer connectivity patterns.

## Captions (verbatim)

**Figure 21:** ROFT topology for a 16384 GPU cluster based on 51.2 Tbps switches.

**Figure 22:** Rail-only topology for a 16384 GPU cluster based on 51.2 Tbps switches. Each Rail-interconnection adopts a 2-layer CLOS architecture, consistent with [51] and [57].

**Figure 23:** HPN topology (dual-port designs for ROFT) for a 16384 GPU cluster based on 51.2 Tbps switches.

**Figure 24:** ZCube(128,2) topology for a 16384 GPU cluster based on 51.2 Tbps switches.

### Figure 24 (p.20) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig24.png]]
*整页渲染: ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]]*
> [!quote] caption
> ZCube(128,2) topology for a 16384 GPU cluster based on 51.2 Tbps switches. 880

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The page presents a comparative study of four network topologies for a **16,384 GPU cluster** built from 51.2 Tbps switches:

1. **Figure 21 – ROFT (Rail-Optimized Fat-Tree)**: 3-tier hierarchy: Core (128×400G) → Super-Pod Spines (64×400G) → Pod Leaves (64×400G) → 8-NIC servers. Groups 512 servers per Pod, 2,048 per Super-Pod.
2. **Figure 22 – Rail-only**: 2-layer CLOS per rail. 8 rail interconnects (L2 SWs) each fan out to all pods' L1 SWs; every server uses 8 NICs pinned to one rail.
3. **Figure 23 – HPN (dual-port ROFT)**: Spines (128×400G) → Leaves (128×200G) → dual-port servers (2×200G); folds two Fat-Tree pods into one.
4. **Figure 24 – ZCube(128,2)**: L2 SWs (128×200G + 128×200G dual-port) connect to L1 SWs serving 16 servers each, with cross-pod L2↔L1 diagonal links.

**Key takeaway:** The four designs trade switch count, cabling, and oversubscription differently—ROFT maximizes per-server bandwidth with more switches, while HPN and ZCube reduce switch/cabling cost by leveraging dual-port NICs and richer connectivity patterns.

## Captions (verbatim)

**Figure 21:** ROFT topology for a 16384 GPU cluster based on 51.2 Tbps switches.

**Figure 22:** Rail-only topology for a 16384 GPU cluster based on 51.2 Tbps switches. Each Rail-interconnection adopts a 2-layer CLOS architecture, consistent with [51] and [57].

**Figure 23:** HPN topology (dual-port designs for ROFT) for a 16384 GPU cluster based on 51.2 Tbps switches.

**Figure 24:** ZCube(128,2) topology for a 16384 GPU cluster based on 51.2 Tbps switches.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 3 (p.18) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-tab03.png]]
> [!quote] caption
> The average communication path length between GPU pairs and average path stretch for different topologies, both before and after a single-switch failure. ∗ indicates that considering intra-server interconnection, the communication path length within a server is considered to be 1.

> [!tip] 表格解读（多模态）
> # Description

**Main figure (Table 3):** A comparison table evaluating four network topologies — **ROFT**, **Rail-only**, **Dragonfly**, and **BCube(32,2)** — at a scale of **1024 GPUs**. It reports six metrics in two groups: (1) **APL** (average path length), **APL_fail** (after one switch failure), and **APS×10⁻⁴** (path stretch) treating intra-server paths normally; and (2) the starred variants (**APL\***, **APL\*_fail**, **APS\***) where the intra-server path is normalized to 1. Data flows left→right: GPU Scale → Topology → unstarred metrics → starred metrics.

**Key technical takeaway:** ROFT achieves an APS\* of **20.83×10⁻⁴** versus Dragonfly's **25.26×10⁻⁴** (≈17% improvement) at 1024 GPUs, while degrading minimally under single-switch failure (**APL\*: 5.349 → 5.360**), demonstrating both superior path efficiency and robustness compared to incumbent datacenter topologies.

# Caption (verbatim)

*Table 3: The average communication path length between GPU pairs and average path stretch for different topologies, both before and after a single-switch failure. \* indicates that considering intra-server interconnection, the communication path length within a server is considered to be 1.*

### Table 4 (p.19) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-tab04.png]]
> [!quote] caption
> Simulation results of GPT-3-22B model training time, using different network simulators as the network backend of Astra-Sim 2.0 [54].

> [!tip] 表格解读（多模态）
> **Description:**

The table compares GPT-3-22B iteration time (in seconds) produced by two network backends inside Astra-Sim 2.0: **NS-3** (packet-level) versus a **Flow-level** simulator. Results are grouped by GPU scale (64 and 256 GPUs), each spanning five network topologies: **ROFT, Dragonfly, BCube, HPN, ZCube**, with a final column showing the relative error between the two simulators. Data flow: input (scale + topology) → both simulators compute iteration time → comparison via relative error.

**Key takeaway:** Flow-level simulation tracks NS-3 within ≤3.7% across all topologies, and its accuracy improves at larger scale (errors drop from 0.3–3.7% at 64 GPUs to 0.2–3.2% at 256 GPUs), suggesting it is a faithful yet cheaper substitute for packet-level modeling in large-scale distributed training.

**Caption (verbatim):**

**Table 4: Simulation results of GPT-3-22B model training time, using different network simulators as the network backend of Astra-Sim 2.0 [54].**

### Table 5 (p.19) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-tab05.png]]
> [!quote] caption
> 64 MB All-to-all collective communication job com- pletion time, using different network simulators.

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**

The table presents a comparison between two simulation approaches for evaluating the completion time of a 64 MB All-to-All collective communication job across five network topologies. It is organized into three logical components: (1) the **Topology** column listing the evaluated networks (ROFT, Dragonfly, BCube(8,2), HPN, ZCube(8,2)); (2) the **All-to-All (ms)** measurements, split into NS-3 packet-level simulation results and Flow-level simulation results; and (3) the **Relative Error** quantifying agreement between the two methods. The data flow moves left-to-right: each topology's NS-3 execution time is compared against the flow-level approximation, with discrepancies reported as percentages.

**Key technical takeaway:** Flow-level simulation closely tracks NS-3 packet-level results across all topologies, with relative errors ranging only from 2.0% to 7.3%, validating it as a faithful yet computationally cheaper surrogate for modeling collective communication performance.

**Caption (verbatim):**

Table 5: 64 MB All-to-all collective communication job completion time, using different network simulators.

### Table 6 (p.19) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-tab06.png]]
> [!quote] caption
> Switch and cable counts required by different topolo- gies when building a 16384 GPU cluster with 51.2 Tbps switches.

> [!tip] 表格解读（多模态）
> ## Description

**Main Figure:** Table 6 — a comparative resource-count table for interconnect topologies targeting a **16,384-GPU cluster** with **51.2 Tbps** leaf-class switches.

**Components compared (rows):** ROFT (Rail-Optimized Fat-Tree), Rail-only, HPN, ZCube(128,2).

**Columns:** Topology │ #Switches (51.2 Tbps) │ Cables (Count × Per-cable bandwidth).

| Topology | Switches | Cables |
|---|---|---|
| ROFT | 640 | 49,152 × 400G |
| Rail-only | 384 | 32,768 × 400G |
| HPN | 384 | 16,384 × 400G + 32,768 × 200G |
| **ZCube(128,2)** | **256** | **49,152 × 200G** |

**Data flow:** The table quantifies the physical-layer bill-of-materials (switch population + cabling) each topology demands to deliver bandwidth to a 16k-GPU fabric, with ZCube highlighted as the most switch-efficient option.

### Key Technical Takeaway
ZCube(128,2) cuts the required 51.2 Tbps switch count to **256 (≈60% fewer than ROFT, 33% fewer than HPN/Rail-only)** while using only **200G cables** (no 400G links). It still needs the most cable *count* (49,152), but at half the per-cable rate, this tradeoff minimizes switch hardware cost—typically the dominant capex—without sacrificing cabling structure. In short, ZCube is the most switch-economical topology at this scale.

### Verbatim Caption
> Table 6: Switch and cable counts required by different topologies when building a 16384 GPU cluster with 51.2 Tbps switches.

### Table 7 (p.21) ⭐深度解读
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-tab07.png]]
> [!quote] caption
> Configurations of the evaluated topology in § 6.

> [!tip] 表格解读（多模态）
> **Description (table contents & key takeaway):**

The table compares six network topologies — ROFT, Rail-only, Dragonfly, BCube, HPN, and ZCube — across three deployment scales. Each row lists the number of switches, switch radix (ports × per-port speed, e.g., 32×400G), copper cables, fiber cables, optical modules, and NIC ports per server. The three row groups grow from small clusters (~64–264 switches) through mid-tier (up to 876) to large fabric sizes (up to 2064 switches), allowing a like-for-like cost/cabling comparison.

**Key takeaway:** ROFT and Rail-only are pure fiber fabrics using 400G low-radix switches with a single NIC per server; Dragonfly uses predominantly copper and needs many more switches; BCube/HPN/ZCube deploy 200G optics with two NIC ports — showing that cable medium (fiber vs. copper) and switch radix jointly govern cable and optical-module counts even at identical node counts.

**Caption (verbatim):**
Table 7: Configurations of the evaluated topology in §6.

## 关键公式（原文截图，无 LaTeX 源 — 引用前请核对图片）

### 公式截图 (p.5)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-eq01.png]]
> 原文文本线索：`𝑖𝑗∈{𝑑| 𝑑> 0, 𝑁𝑖mod 𝑑= 0} ∪{0} to H`

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.5 `𝑖𝑗∈{𝑑| 𝑑> 0, 𝑁𝑖mod 𝑑= 0} ∪{0} to H`
- p.5 `𝑖𝑗∈{𝑑| 𝑑> 0, 𝑁𝑗mod 𝑑= 0} ∪{0} to H`
- p.6 `𝑖∈{𝑑| 𝑁remained > 0, 𝑁remained mod 𝑑= 0} to H`

## 相关论文

- [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] — Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
- [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] — MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey
- [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] — Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning
- [[muon-is-scalable-for-llm-training]] — Muon is Scalable for LLM Training
- [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] — GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints

## 技术点深读（DEEP）

![[deep/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training.txt`（107386 字符）供引用检索。