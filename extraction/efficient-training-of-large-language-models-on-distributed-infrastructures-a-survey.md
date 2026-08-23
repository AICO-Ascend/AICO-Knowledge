---
paper_num: "51"
title: "Efficient Training of Large Language Models on Distributed Infrastructures: A Survey"
authors: "Efficient Training of Large Language Models on Distributed Infrastructures: A Survey Jiangfei Duan∗, Shuo Zhang∗, Zerui Wang∗, Lijuan Jiang, Wenwen Qu, Qinghao Hu, Guoteng Wang, Qizhen Weng, Hang Yan, Xingcheng Zhang, Xi"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2407.20018"
pdf: "papers/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey.pdf"
slug: "efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey"
tags: [training]
---

# Efficient Training of Large Language Models on Distributed Infrastructures: A Survey

> [!abstract] 摘要（原文）
> 1\. ✨ 本文全面综述了分布式 LLM 训练系统的最新进展，旨在解决大规模 LLM 训练在 Scalability, Efficiency 和 Reliability (SER) 方面的核心挑战。 2. ⚡️ 论文详细探讨了包括 Data, Tensor, Pipeline, Sequence 和 Expert 等多种 Hybrid Parallelism 策略，以及 Operator Optimization、Mixed-Precision Training、Memory Optimization 和 Communication Optimization 等关键技术，以提升训练效率。 3. 💾 此外，文章还深入分析了 LLM 训练的 Infrastructure (包括 AI Accelerators, Network 和 Storage) 设计、Job Scheduling 方法，并介绍了 Anomaly Detection 和 Checkpoint-based/Checkpoint-free Recovery 等 Fault Tolerance 机制以确保系统可靠性。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Efficient Training of Large Language Models on Distributed Infrastructures: A Survey Jiangfei Duan∗, Shuo Zhang∗, Zerui Wang∗, Lijuan Jiang, Wenwen Qu, Qinghao Hu, Guoteng Wang, Qizhen Weng, Hang Yan, Xingcheng Zhang, Xi
- **arXiv**: https://arxiv.org/abs/2407.20018
- **本地 PDF**: `papers/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey.pdf`
- **页数**: 42

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig01.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p02.png]]*
> [!quote] caption
> Overall structure of this survey.

> [!tip] 技术解读（多模态）
> ## Figure Description

**Architecture/Components:** The figure is a 2×3 taxonomic grid mapping the survey's six core technical chapters (Sections 3–8), each broken into numbered subsections linked by braces.

- **Section 3 — Infrastructure:** AI Accelerators, Network Infrastructure, Storage
- **Section 4 — Parallelism Schemes:** Hybrid, Auto, Heterogeneous Parallelism
- **Section 5 — Computation Optimizations:** Operator Optimization, Mixed-Precision Training
- **Section 6 — Memory Optimizations:** Activation Recomputation, Redundancy Reduction, Defragmentation, Offloading
- **Section 7 — Communication Optimizations:** Collective Communication, Scheduling, In-Network Aggregation
- **Section 8 — Fault Tolerance:** Failure Analysis, Anomaly Detection, Checkpoint-Based & Checkpoint-Free Recovery

**Key Takeaway:** The taxonomy progresses logically from **hardware substrate → distributed coordination → micro-optimization → resilience**, showing that scalable LLM training requires co-design across compute, memory, network, and fault-recovery layers—each is necessary but not sufficient alone.

## Caption (Verbatim)

**Fig. 1: Overall structure of this survey.**

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig02.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p03.png]]*
> [!quote] caption
> A typical Transformer layer contains an Attention

> [!tip] 技术解读（多模态）
> **Description:** The figure depicts a standard Transformer layer with two parallel sub-blocks sharing the same input X. **Left — Attention Block:** X → Norm → Linear(Wqkv) projects into Q, K, V in parallel → MHA/GQA (Multi-Head or Grouped-Query Attention) → Linear(Wo) → residual addition (⊕). **Right — FFN Block:** X → Norm → two parallel Linear projections W1 and W3 → SiLU activation on W1's output → element-wise product (⊙) with W3's output → Linear(W2) → residual addition (⊕). Data flows bottom-up through each block. **Key takeaway:** The FFN uses a **SwiGLU-style gated activation** (two parallel linear projections combined via SiLU·gated multiplication), which is the modern LLaMA-family replacement for the original ReLU-based two-layer FFN, yielding better parameter efficiency at comparable compute. Residual connections and pre-normalization are applied in both blocks.

**Caption (verbatim):**
"Fig. 2: A typical Transformer layer contains an Attention block and a Feed-Forward Network (FFN) block."

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig03.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p04.png]]*
> [!quote] caption
> Infrastructure overview for distributed LLM training.

> [!tip] 技术解读（多模态）
> **Figure 3 Description (≤120 words):**

The diagram depicts a hierarchical distributed LLM training infrastructure. Four **Compute Nodes** sit at the core, interconnected via the **Backend Network** (high-bandwidth training traffic). Below them, the **Frontend Network** (management & storage traffic) links the compute cluster to **Training Dataset Storage** and **Checkpoint Storage**. On the right, two orthogonal control subsystems are shown: a **Scheduling System** at the top, and a **Fault Tolerance** stack containing **Anomaly Detection** and **Failure Recover** modules.

**Key takeaway:** The architecture deliberately *decouples* compute traffic (backend) from I/O/management traffic (frontend) and pairs the data plane with dedicated reliability and scheduling planes—enabling independent scaling, lower contention, and rapid fault isolation across thousands of GPUs.

**Caption (verbatim):**
> Fig. 3: Infrastructure overview for distributed LLM training.

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig04.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p05.png]]*
> [!quote] caption
> Studies on infrastructure optimizations for distributed LLM training.

> [!tip] 技术解读（多模态）
> **Figure Description:**

The figure is a hierarchical taxonomy titled "Infrastructure for LLM Training" with four main branches expanding left-to-right:

1. **AI Accelerators** — splits into NVIDIA GPUs (Ampere, Hopper, Blackwell) and Other Accelerators (AMD GPU, GAUDI, TPU, Graphcore IPU, Cerebras CS-2).
2. **Network Infrastructure** — four sub-branches: Chip-to-Chip (Cube-Mesh/FC/Torus), Node-to-Node (GPUDirect-RDMA, InfiniBand, RoCE, iWARP), Network Topology (HPC/Training-Optimized/Reconfigurable), and Load Balancing & CC (ECMP, packet spraying, PFC, DCQCN, HPCC, etc.).
3. **Storage Systems** — Checkpoint Storage (Tectonic, HDFS, Ceph) and Training Data Storage (Lustre, GPFS, BeeGFS, Alluxio, JuiceFS, etc.).
4. **Scheduling Systems** — Workload Scheduling (Tiresias, Pollux, Sia…) and Resource Scheduling (Cassini, HIRE, Zeus, Perseus…).

**Key takeaway:** Communication overhead dominates LLM training (>90% of time in some cases), so the taxonomy is heavily weighted toward network-stack innovations—spanning physical interconnects, topology design, and congestion control—reflecting that bandwidth and latency, not raw compute, are the primary scalability bottleneck.

**Caption (verbatim):**
Fig. 4: Studies on infrastructure optimizations for distributed LLM training.

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig05.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p06.png]]*
> [!quote] caption
> Five chip-to-chip topologies: tree topology, cube-mesh topology, switch-based fully-connected topology, P2P-based

> [!tip] 技术解读（多模态）
> ## Figure Description

The figure illustrates **five chip-to-chip interconnect topologies** used in accelerator systems:

- **(a) Tree Topology**: Hierarchical structure with PCIe Switch and Root Complex forming a multi-level hierarchy.
- **(b) Cube-Mesh Topology**: A regular grid (planar mesh for 4 GPUs; cube-mesh for 8 GPUs), as in NVLink-1.0.
- **(c) Switch-based Fully-Connected**: GPUs connect through NVSwitch chips, enabling all-to-all bandwidth (e.g., DGX-2 with six NVSwitches).
- **(d) P2P-based Fully-Connected**: Direct peer-to-peer links between every chip pair (used by Intel, AMD, Huawei Ascend).
- **(e) 2D-Torus Topology**: Grid layout with wraparound edges for multiple shortest paths (Google TPUv2/v3).

**Key Takeaway**: Bandwidth, latency, and scalability trade-offs drive topology choice—torus offers redundant paths, fully-connected maximizes bandwidth but scales expensively in wiring, while mesh/tree trade cost for performance.

**Caption (verbatim)**:
"Fig. 5: Five chip-to-chip topologies: tree topology, cube-mesh topology, switch-based fully-connected topology, P2P-based fully-connected topology, and 2D-torus topology."

### Figure 6 (p.7) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig06.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p07.png]]*
> [!quote] caption
> Four typical network topologies in large-scale GPU clusters: Clos topology, Dragonfly+ topology, rail-optimization

> [!tip] 技术解读（多模态）
> **Description (architecture & key takeaway):**

The figure compares four GPU cluster network topologies built from three switch tiers — **Core (green) → Spine (red) → Leaf (blue) → GPU endpoints (purple)** — grouped into Pods. (a) **Clos** is a full fat-tree: every leaf connects to every spine, every spine to every core, giving any-to-any bandwidth at high switch cost. (b) **Dragonfly+** removes the core tier and adds direct pod-to-pod links (curved arcs). (c) **Rail-Optimized** preserves Clos's full hierarchy but aligns GPUs across racks by index onto shared leaf switches, shortening collective traffic. (d) **Rail-Only** drops the core entirely; intra-rail traffic stays local, while inter-rail traffic is offloaded to a separate side Clos.

**Key takeaway:** Network topology for LLM training is increasingly *co-designed with parallelism strategy* — rail-optimized layouts exploit predictable collective-communication patterns, while the rail-only variant trades flexibility for cost, signaling a shift toward workload-aware, slim switching fabrics.

**Caption (verbatim):**

Fig. 6: Four typical network topologies in large-scale GPU clusters: Clos topology, Dragonfly+ topology, rail-optimization topology, and rail-only topology.

### Figure 7 (p.10) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig07.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p10.png]]*
> [!quote] caption
> Studies on parallelism schemes for distributed LLM training.

> [!tip] 技术解读（多模态）
> ## Figure Description

The figure is a hierarchical taxonomy classifying **Parallelism Schemes for LLM Training** into three top-level branches:

1. **Hybrid Parallelism** — combines hand-crafted strategies: Data, Tensor, Pipeline (subdivided into Pipeline Bubble / Memory Imbalance mitigations), Sequence, and Expert Parallelism (Sparse Activation, Communication Optimization, Load Balancing).
2. **Auto Parallelism** — automated strategy selection, split into General Frameworks and Transformer-Specific approaches.
3. **Heterogeneous Parallelism** — exploits hardware heterogeneity (mixed accelerators) and model heterogeneity (e.g., RLHF), with techniques for each.

Each leaf node enumerates representative systems/papers by citation number, forming a literature map from category → subcategory → concrete works.

**Key takeaway:** The taxonomy shows that efficient LLM training is no longer solved by a single dimension (e.g., pure data parallelism); modern systems must *compose* multiple strategies—often via automation—to hide pipeline bubbles, balance MoE loads, and exploit hardware/model heterogeneity at HPC scale.

## Caption (verbatim)

**Fig. 7:** Studies on parallelism schemes for distributed LLM training.

### Figure 8 (p.12) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig08.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p12.png]]*
> [!quote] caption
> An example of 3D-parallelism with data parallelism, tensor parallelism, and pipeline parallelism.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Architecture & Components (nested, outermost → innermost):**
1. **Data Parallelism (outermost):** Two DP ranks (Rank 0, Rank 1) replicate the full model and synchronize gradients via **AllReduce (AR)** across nodes.
2. **Sequence Parallelism:** Sits inside each DP rank, coordinating activations along the sequence dimension (shown enclosing the TP group).
3. **Tensor Parallelism (TP):** Four-way partition (TP-0…TP-3) splitting weight matrices/activations across GPUs within a node, communicating via **Send/Recv** between stages.
4. **Pipeline Parallelism (innermost):** Four sequential stages assigned to contiguous LLM layer ranges — Stage 0 (Layers 0–3), Stage 1 (4–7), Stage 2 (8–11), Stage 4 (12–15) — exchanging activations via Send/Recv.

**Data flow:** Tokens → micro-batches flow left-to-right across pipeline stages while TP shards compute in parallel; gradients aggregate up the DP hierarchy via AR.

## Key Technical Takeaway (≤120 words)
3D-parallelism **hierarchically nests** three orthogonal strategies to match each to the appropriate interconnect bandwidth: **TP** uses fast intra-node NVLink for weight/activation sharding; **pipeline parallelism** exploits cheap inter-node bandwidth by only exchanging activations at layer boundaries via Send/Recv; and **DP** wraps the whole stack, replicating models and averaging gradients with AllReduce. This decomposition lets trillion-parameter LLM training scale across thousands of GPUs while balancing compute, memory, and communication costs. Each axis addresses a distinct bottleneck — memory (TP/PP) vs. throughput (DP) — that no single scheme can solve alone.

## Caption (Verbatim)
**Fig. 8:** An example of 3D-parallelism with data parallelism, tensor parallelism, and pipeline parallelism.

### Figure 9 (p.14) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig09.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p14.png]]*
> [!quote] caption
> Expert parallelism. The dotted line highlights the

> [!tip] 技术解读（多模态）
> **Figure Description (architecture/components/data flow + key takeaway):**

The figure illustrates **Expert Parallelism** across *N* devices (only Device 1 and Device N shown). Vertical data flow per device (bottom→top): Input Token Vector → **Embedding** → Add & Norm → **Attention** → Add & Norm → **Gating** → (cross-device) → **Expert-i** → (cross-device) → Add & Norm → Output Token Vector. Two **All-to-All Dispatch** operations (orange ovals) sit between the gating network and the experts, enabling tokens to be routed to—and results returned from—their assigned expert on a remote device. A dotted ellipse encloses the MoE-specific blocks (Gating + All-to-All Dispatch + Experts), distinguishing them from the standard Transformer blocks (Embedding, Attention, Add & Norm).

**Key takeaway:** Each device hosts exactly one expert; inter-device collaboration is achieved entirely through All-to-All communication around the gating layer, rather than replicating experts.

**Caption (verbatim):**
> Fig. 9: Expert parallelism. The dotted line highlights the MoE components within the transformer model, where each device maintains one expert for expert parallelism and collaborate based on All-to-All communication.

### Figure 10 (p.17) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig10.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p17.png]]*
> [!quote] caption
> An example of RLHF. Inference process: 1 The

> [!tip] 技术解读（多模态）
> **Figure 10 — RLHF architecture and data flow**

The diagram depicts an RLHF (Reinforcement Learning from Human Feedback) pipeline with two interacting phases. A Query Dataset feeds a **trainable Actor Model** (red) that generates responses. These responses, together with the original queries, are routed to three **frozen models** (blue): a Critic Model (producing a *value*), a Reward Model (producing a *score*), and a Reference Model (producing a *KL estimation*). In the training phase, the value/score/KL signals collected during inference drive gradient-descent weight updates back into the Actor and Critic models.

**Key takeaway:** RLHF decouples *inference* (frozen models producing training signals) from *training* (gradient updates of actor/critic), and the model heterogeneity — keeping reference/reward/critic frozen while only actor/critic are updated — is the central source of its extra memory and time cost. (~110 words)

**Caption (verbatim):**
"Fig. 10: An example of RLHF. **Inference process:** ① The actor model generates a response from a given query. ② The critic model, reward model, and reference model use the query and response pairs to generate the value, score, and KL divergence required for training through inference. **Training process:** ③ The actor model and critic model use the data collected in the inference process to update their weights through gradient descent."

### Figure 11 (p.19) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig11.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p19.png]]*
> [!quote] caption
> Studies on computation optimizations for distributed LLM training.

> [!tip] 技术解读（多模态）
> **Figure Description (Architecture/Components/Data Flow):**

The hierarchical tree diagram, labeled "Computational Optimizations for LLM Training," branches into two primary categories:

1. **Operator Optimizations** → splits into *Manual* (FlashAttention family, BPT, SWattention, ByteTransformer) and *Automatic* optimizations, the latter further divided into *Kernel-level* (Halide, TVM, Roller, Triton, ALCOP) and *Graph-level* compilers (Chimera, Welder, Slapo, TorchDynamo/TorchInductor, JIT-Q).

2. **Mixed-precision Training** → splits into *16-Bit Floating Point* (FP16/BF16 training, Campo, THC), *Sub-8-Bit Floating Point* (Wang et al., Sun et al., FP8-LM, Rouhani et al.), and *Low-Bit Fixed Point* with INT8 (Jetfire), INT4 (Xi et al.), and 1-Bit (BitNet, BitNet b1.58).

**Key Technical Takeaway:** Optimization strategies span a granularity spectrum—from fine-grained kernel-level tiling for memory/compute efficiency to coarse-grained graph fusion, paired with aggressive precision reduction down to binary representations.

**Caption (verbatim):**
Fig. 11: Studies on computation optimizations for distributed LLM training.

### Figure 12 (p.21) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig12.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p21.png]]*
> [!quote] caption
> Studies on memory optimizations for distributed LLM training.

> [!tip] 技术解读（多模态）
> **Description of the main figure:**

The figure is a hierarchical taxonomy diagram titled *"Memory Optimizations for LLM Training"*, organized as a three-level tree branching from a single root into four main optimization categories:

1. **Activation Recomputation** → splits into *Dynamic Evicting* (DTR, MegTaiChi, Coop) and *Static Evicting* (Checkmate, LoongTrain, Yuan et al., Selective Checkpointing, DistFlashAttn).
2. **Redundancy Reduction** → splits into *Fully Sharding* (ZeRO, FSDP) and *Partially Sharding* (ZeRO++, MiCS, PaRO, RTP, AMSP).
3. **Defragmentation** → splits into *Tensor-based* (ROAM, ZeRO-R, Imanishi et al., MegTaiChi, Coop) and *VMM-based* (GMLake, Expandable Segments).
4. **Offloading** → splits into *CPU Offloading* (Static: L2L, ZeRO-Offload, Elixir, Yuan et al.; Dynamic: TSPLIT, PatrickStar, Mobius, Harmony, TMOF, STRONGHOLD) and *SSD Offloading* (ZeRO-Infinity, Angel-PTM, Smart-Infinity, Fuyou, MoESys).

**Key technical takeaway:** No single technique dominates — each addresses a different bottleneck (compute-for-memory trade-off, parameter duplication, fragmented allocation, or capacity scaling), and practical systems typically compose multiple strategies from different branches to fit the GPU memory budget.

**Caption (verbatim):**

Fig. 12: Studies on memory optimizations for distributed LLM training.

### Figure 13 (p.25) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig13.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p25.png]]*
> [!quote] caption
> Communication traffic heatmap for InternLM-2

> [!tip] 技术解读（多模态）
> ## Figure Description

**Fig. 13** is a 128×128 GPU-pair heatmap visualizing per-iteration communication traffic for InternLM-2 102B pre-training across 128 GPUs, using a hybrid TP=8 / PP=4 / DP=4 / ZeRO-1=4 configuration.

**Components & Data Flow:**
- **Axes**: GPU index 0–127 on both x and y, representing ordered GPU pairs.
- **Color scale**: Traffic volume, ranging 256 MB (yellow) → 12 GB (deep purple) per pair.
- **Pattern overlays** (priority TP > DP/ZeRO-1 > PP):
  - ① **TP traffic**: 16 dense 8×8 diagonal squares from NVSwitch fully-connected intra-node topology.
  - ②③ **DP/ZeRO-1 traffic**: six symmetric diagonal stripes spanning 32×32 rectangular sub-grids (ReduceScatter + AllGather).
  - ④ **PP traffic**: two thin yellow lines at offsets ((32,0),(128,96)) and ((0,32),(96,128)) — Send/Recv.

**Key technical takeaway:** Because TP traffic (intra-node NVSwitch) carries the largest volume per pair, hybrid parallelism layouts that keep TP groups co-resident on the same node dominate bandwidth pressure, while PP contributes negligible traffic — making it the cheapest dimension to scale across nodes.

## Caption (verbatim)

Fig. 13: Communication traffic heatmap for InternLM-2 102B pre-training using 128 GPUs during a single iteration, with tensor parallelism (TP) size 8, pipeline parallelism (PP) size 4, data parallelism (DP) size 4 and ZeRO stage 1 (ZeRO-1) size 4. The prioritization of topology arrangement is TP >DP/ZeRO-1 >PP. There are four different data traffic loads: ① the AllReduce of TP; ②③ ReduceScatter/AllGather of DP/ZeRO-1; ④ Send/Recv of PP. The communication for TP utilizes the fully-connected topology of NVSwitch, resulting in sixteen dense square traffic patterns along the diagonals in the diagram, with each pattern representing a node. The cross-node communication traffic for DP and ZeRO-1 are shown in the diagram as six symmetric diagonal lines within the four 32×32 rectangular topologies. It is important to note that DP/ZeRO-1 also involves intra-node communication traffic, which accumulates into the same heatmap grid as TP. Due to its relatively small communication volume, PP forms two yellow lines on the heatmap at coordinates ((32, 0), (128, 96)) and ((0, 32), (96, 128)). (In this diagram, all communications use the ring-based collective algorithm)

### Figure 14 (p.26) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig14.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p26.png]]*
> [!quote] caption
> Studies on communication optimizations for distributed LLM training.

> [!tip] 技术解读（多模态）
> **Description**

The figure is a hierarchical taxonomy titled "Communication Optimizations for LLM Training," branching into three top-level categories:

1. **Collective Communication** — split into *Pre-Defined Algorithms* (libraries: MPI, NCCL, RCCL; patterns: Ring, Tree, Hybrid) and *Synthesized Algorithms* (GC3, SCCL, TACCL, Blink, P²).
2. **Communication Scheduling** — three sub-branches: *FIFO-based* (Poseidon, GradientFlow, PyTorch DDP), *Priority-based* (P3, TicTac, ByteScheduler, PACE, Lina), and *Decomposition-based* (Pipeline/Communication/Computation decomposition plus out-of-order backpropagation).
3. **In-Network Aggregation** — *Ethernet-based* (SwitchML, FPISA, NetReduce, AllReduce-Switch, PANAMA, ATP) and *InfiniBand-based* (NVIDIA Mellanox SHARP v1/v2/v3).

Each leaf lists concrete systems/methods with reference numbers.

**Key Technical Takeaway:** Optimizations form three complementary layers—custom collective algorithms (latency reduction), intelligent scheduling overlapping compute/comm (dependency-aware reordering via FIFO, priority, or decomposition), and hardware-accelerated aggregation inside switches (offloading AllReduce to the network)—which together address the dominant communication bottleneck of distributed LLM training.

**Caption (verbatim):** "Fig. 14: Studies on communication optimizations for distributed LLM training."

### Figure 15 (p.29) ⭐深度解读
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig15.png]]
*整页渲染: ![[assets/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-p29.png]]*
> [!quote] caption
> Studies on fault tolerance techniques for distributed LLM training.

> [!tip] 技术解读（多模态）
> ## Description

The figure presents a three-level hierarchical taxonomy rooted at **"Fault Tolerance for LLM Training"**, branching into three primary pillars:

1. **Anomaly Detection** — splits into *Statistical Monitoring* (Healthd, MegaScale, C4, Vela, Unicorn, Transom, NCCLK, NCCL flight recorder) and *Proactive Validation* (MegaScale lightweight tests, SuperBench, Vela, TPUv4 Preflight Check).
2. **Checkpointing-Based Recovery** — divides into *Persistent Checkpointing* (sub-classified into **Synchronous** solutions like DeepSpeed, Varuna, JIT-Checkpointing, Flash-Checkpoint, Universal Checkpointing, **Snapshot-Stall** like Check-N-Run/TorchSnapshot, and **Asynchronous** approaches DeepFreeze, CheckFreq, LightCheck, DataStates-LLM, FastPersist) and *In-Memory Checkpointing* (Gemini, REFT).
3. **Checkpointing-Free Recovery** — covers *Live Migration* (Parcae, Oobleck) and *Module Redundancy* (Bamboo, SlipStream, SWARM).

Each leaf node maps concrete systems/tools to its category, giving readers a citation-indexed landscape of the field.

## Key Technical Takeaway (≤120 words)

The taxonomy reveals a clear design spectrum: **detection-first** (statistical monitoring + proactive validation) catches faults early, while recovery strategies trade off **durability vs. overhead** — persistent checkpointing offers fault survival at storage/IO cost, in-memory checkpointing trades persistence for speed, and checkpointing-free approaches (migration/redundancy) eliminate IO bottlenecks entirely but require spare resources. Notably, persistent checkpointing has bifurcated into synchronous (strong consistency, higher stall) vs. asynchronous (lower stall, weaker guarantees) regimes, reflecting the field's shift toward overlapping compute with checkpoint IO. The taxonomy shows that no single technique dominates; modern systems (e.g., MegaScale, Vela) combine multiple pillars.

## Caption (verbatim)

Fig. 15: Studies on fault tolerance techniques for distributed LLM training.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\text{Attention}(Q, K, V) = \texttt{softmax}\left(\frac{QK^T}{\sqrt{d}}\right)V
$$

## 相关论文

- [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] — Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core
- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] — MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs
- [[zero-memory-optimizations-toward-training-trillion-parameter-models]] — ZeRO: Memory Optimizations Toward Training Trillion Parameter Models

## 技术点深读（DEEP）

![[deep/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey.txt`（271696 字符）供引用检索。