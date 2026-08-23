---
paper_num: "30"
title: "HybridFlow: A Flexible and Efficient RLHF Framework"
authors: "Guangming Sheng The University of Hong Kong gmsheng@connect.hku.hk Chi Zhang ByteDance zhangchi.usc1992@bytedance.com Zilingfeng Ye ByteDance yezilingfeng@bytedance.com Xibin Wu ByteDance wuxibin@bytedance.com Wang Zhang"
date: "2026/1/17"
arxiv: "https://arxiv.org/abs/2409.19256"
pdf: "papers/hybridflow-a-flexible-and-efficient-rlhf-framework.pdf"
slug: "hybridflow-a-flexible-and-efficient-rlhf-framework"
tags: [rl]
---

# HybridFlow: A Flexible and Efficient RLHF Framework

> [!abstract] 摘要（原文）
> 1\. 🤔 HybridFlow 提出了一种混合编程模型，巧妙地结合了单控制器（用于节点间数据流协调）和多控制器（用于高效执行节点内分布式 LLM 计算）范式，旨在解决 RLHF 在 LLM 对齐中面临的复杂性和效率挑战。 2. ⚙️ 该框架设计了分层 API 以实现灵活的 RLHF 算法表达和高效操作编排，并引入了 3D-HybridEngine 用于 Actor 模型在训练和生成阶段之间的高效参数重分片，实现了零内存冗余和显著降低的通信开销。 3. 🚀 实验结果表明，HybridFlow 在运行各种 RLHF 算法时，吞吐量比现有最先进的基线系统（如 DeepSpeed-Chat、OpenRLHF 和 NeMo-Aligner）提高了 1.53 倍至 20.57 倍，验证了其灵活性和高效率。

## 元信息
- **发表日期**: 2026/1/17
- **作者**: Guangming Sheng The University of Hong Kong gmsheng@connect.hku.hk Chi Zhang ByteDance zhangchi.usc1992@bytedance.com Zilingfeng Ye ByteDance yezilingfeng@bytedance.com Xibin Wu ByteDance wuxibin@bytedance.com Wang Zhang
- **arXiv**: https://arxiv.org/abs/2409.19256
- **本地 PDF**: `papers/hybridflow-a-flexible-and-efficient-rlhf-framework.pdf`
- **页数**: 19

## 图表（原文 caption + 页码）

### Figure 1 (p.3) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig01.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p03.png]]*
> [!quote] caption
> Dataflow graph of 3 RLHF algorithms [19, 43, 55].

> [!tip] 技术解读（多模态）
> **Figure 2 — HybridFlow's Programming Model**

**Architecture/components:** Two stacked paradigms. (a) *Existing RLHF* uses a pure *multi-controller* model: every GPU worker independently runs actor/critic/reward code with nested loops (`for prompts`, `while True`), tightly coupling computation and data dependencies. (b) *HybridFlow* adds a *single-controller* layer above separate multi-controller workers. The top-level controller issues remote calls (`actor.gen(prompts)`, `actor.train(responses)`) to individual model workers, each of which internally uses `def_actor.gen` / `def_comp_value` / `def_comp_reward` multi-controller functions. Inactive workers are shown in grey.

**Data flow:** Controller → remote call → per-model workers (Actor, Critic, Reward) → return values.

**Key takeaway:** Decoupling inter-node orchestration (single-controller) from intra-node distributed computation (multi-controller) eliminates train↔gen transition overhead and enables flexible model placement, yielding 1.53×–20.57× throughput gains.

**Caption (verbatim):**
"Figure 2. Programming model used in RLHF systems. (a) Existing RLHF systems adopt the multi-controller paradigm. (b) HybridFlow utilizes a hybrid programming model: the single-controller coordinates models; each model uses multi-controller paradigm in distributed computation. Inactive node in grey represents operation not executed at this time."

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig02.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p03.png]]*
> [!quote] caption
> Programming model used in RLHF systems. (a)

> [!tip] 技术解读（多模态）
> **Figure 2 — HybridFlow's Programming Model**

**Architecture/components:** Two stacked paradigms. (a) *Existing RLHF* uses a pure *multi-controller* model: every GPU worker independently runs actor/critic/reward code with nested loops (`for prompts`, `while True`), tightly coupling computation and data dependencies. (b) *HybridFlow* adds a *single-controller* layer above separate multi-controller workers. The top-level controller issues remote calls (`actor.gen(prompts)`, `actor.train(responses)`) to individual model workers, each of which internally uses `def_actor.gen` / `def_comp_value` / `def_comp_reward` multi-controller functions. Inactive workers are shown in grey.

**Data flow:** Controller → remote call → per-model workers (Actor, Critic, Reward) → return values.

**Key takeaway:** Decoupling inter-node orchestration (single-controller) from intra-node distributed computation (multi-controller) eliminates train↔gen transition overhead and enables flexible model placement, yielding 1.53×–20.57× throughput gains.

**Caption (verbatim):**
"Figure 2. Programming model used in RLHF systems. (a) Existing RLHF systems adopt the multi-controller paradigm. (b) HybridFlow utilizes a hybrid programming model: the single-controller coordinates models; each model uses multi-controller paradigm in distributed computation. Inactive node in grey represents operation not executed at this time."

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig03.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p04.png]]*
> [!quote] caption
> Dataflow execution given a model placement plan.

> [!tip] 技术解读（多模态）
> ## Description of Figure 3

**Architecture/Components:**
- **Left — Dataflow Graph (D):** Four nodes — `Gen` (actor generation), `Ref` (reference model), `RM` (reward model), `Value` — feeding into `Actor Training` and `Critic Training`.
- **Middle — Placement Plan:** Maps Actor→Machine A (GPUs 0–1), Critic→Machine B (GPUs 2–3), Ref+RM→Machine C (GPUs 4–5, colocated).
- **Right — Execution Pattern:** Three machines show how models run concurrently across devices; colocated Ref/RM on Machine C share GPU memory.

**Key Technical Takeaway:** Strategic, workload-aware placement is essential in RLHF — models with no data dependency (Actor vs. Critic) are placed on *different* device sets to enable **concurrent execution**, while dependent models (Ref/RM) are *colocated* to share GPU memory via time-sharing, trading off potential OOM risk against parallelism.

## Caption (verbatim)

Figure 3. Dataflow execution given a model placement plan. Blocks with numbers represent GPUs. In dashed boxes, the models are placed on different sets of devices and can be concurrently computed. Reference model (blue) and reward model (green) are colocated on the same set of GPUs and executed sequentially.

### Figure 4 (p.6) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig04.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p06.png]]*
> [!quote] caption
> Architecture of HybridFlow. 3D-HybridEngine and Auto-Mapping algorithm. The hybrid programming model includes a set of hierarchical APIs to enable flexible expression of the RLHF dataflow and effi- cient computation of models in the dataflow (§4). The 3D-

> [!tip] 技术解读（多模态）
> I'm unable to complete this task as requested. The image you've provided contains **only text** from a research paper (Section 2.5 "Design Considerations" and the start of Section 3 "HybridFlow Overview"). 

While the text references "Figure 2(b)" — mentioning that it illustrates a hierarchical hybrid programming model that decouples intra-node distributed computation from inter-node data transfer — the actual figure itself is **not visible** in the image you shared.

To help you accurately, could you please:
- Re-upload the image showing **Figure 2** itself, or
- Share the page/region where the figure appears

Once I can see the figure, I can describe its components, data flow, key technical takeaway, and transcribe the caption verbatim.

**What I can extract from the visible text about the figure's claimed content:**
> The figure depicts a hybrid programming model combining single-controller (used at the inter-node level for orchestrating data transfer across the few RLHF dataflow nodes) and multi-controller (used intra-node for low-latency operator dispatching to accelerators) paradigms — decoupling local model computation from inter-node communication.

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig05.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p06.png]]*
> [!quote] caption
> An illustration of hierarchical APIs. (a) Model with 3D parallel configuration, resource allocation, and 3DParallelWorker initialization. (b) Asynchronous data re- sharding between two models with collect and distribute functions in 3D_PROTO. devices, it facilitates distributed model weight initialization and establishes 3D parallel groups for each model. A parallel group includes a set of GPUs to

> [!tip] 技术解读（多模态）
> # Main Figure: HybridFlow Architecture (Figure 4)

## Description
The figure depicts a **layered architecture** of HybridFlow from bottom to top:

- **Physical Devices** (base) — underlying GPU/HW
- **Resource Pool (§4)** — virtualized device abstraction
- **Auto Mapping (§6)** — splits into Model Placement + Device Allocation, which maps models to GPUs according to given cluster configurations
- **ParallelWorker (§4)** — the orchestration layer containing Transfer Protocol (§4), LLM Training Engine, 3D-HybridEngine (§5), and LLM Generation Engine
- **User Input** (top) — RLHF dataflow graph, Model Config, Device Config

**Data flow:** user inputs (dataflow + model/device configs) → Auto Mapping places models onto the Resource Pool → ParallelWorker dispatches training/generation via the 3D-HybridEngine, coordinating transfers between stages.

## Key Technical Takeaway
The 3D-HybridEngine lets the same actor model toggle between **training and generation** with different 3D-parallel configurations while maintaining **zero memory redundancy** and minimal communication overhead across stages — the core innovation enabling efficient RLHF pipelines.

## Verbatim Caption
**Figure 4. Architecture of HybridFlow.**

### Figure 6 (p.7) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig06.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p07.png]]*
> [!quote] caption
> Implementation of PPO [55], ReMax [43], and Safe- RLHF [19]. Users can adapt to different RLHF algorithms by simply adding or deleting a few lines of code. our programming model, HybridFlow is flexible in support- ing diverse distributed execution patterns without any code change of the RLHF algorithm (Figure 6).

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Architecture/Components:** Figure 6 shows a single Python script implementing multiple RLHF algorithms (PPO, ReMax, Safe-RLHF) as three sequential stages on a single controller:
1. **Stage 1 – Generate responses:** `actor.generate_sequences(prompts)` with sampling toggle (`do_sample=False`).
2. **Stage 2 – Prepare experience:** Calls to `critic.compute_values`, `reference.compute_log_prob`, `reward.compute_reward`, and optional `cost.compute_cost` + `compute_advantages`.
3. **Stage 3 – Actor & critic training:** `critic.update_critic` followed by `actor.compute_loss` (with optional `pretrain_loss`) and `actor.update_actor`.

**Data flow:** Prompts → actor outputs (sequences) → critic/reference/reward/cost computations → advantages → loss/backprop updates, all dispatched across distributed GPUs via the `@register` transfer protocols.

**Key Technical Takeaway:** HybridFlow's modular, hybrid programming model lets researchers port between RLHF variants by merely **adding or removing a handful of code lines** — e.g., just 5 added lines converts SPU into Safe-RLHF, and deleting the critic block yields ReMax — decoupling algorithm logic from distributed execution.

## Caption (Verbatim)

**Figure 6.** Implementation of SPU [55], ReMax [43], and Safe-RLHF [19]. Users can adapt to different RLHF algorithms by simply adding or deleting a few lines of code.

### Figure 7 (p.8) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig07.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p08.png]]*
> [!quote] caption
> 3D-HybridEngine workflow in one RLHF iteration. 4 GPUs are used for actor training and generation. 1-2-2 (𝑝-𝑡-𝑑) parallel groups are used in training and 1-1-2-2 (𝑝𝑔- 𝑡𝑔-𝑑𝑔-𝑑) parallel groups are used in generation. 5 3D-HybridEngine

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 8) — Model Weights Resharding**

The figure compares two strategies for resharding actor-model weights across 2 machines × 4 GPUs between RLHF training and generation stages. Subfigure (a) "HybridFlow-V" applies the *same* parallel grouping to both phases: each GPU performs an all-gather of the **complete** weight set, then discards unused partitions — producing redundant (grey) weight copies that occupy memory. Subfigure (b) "HybridFlow" uses *different* optimized groupings per phase and restricts all-gather operations to within **Micro-DP groups only**, so each GPU retains only the partitions it actually needs, with no redundancy. Color-coded legend distinguishes GPU rank, model weight partitions, DP/TP groups, and all-gather scopes.

**Key takeaway:** Constraining all-gather to the intersection of training- and generation-time micro-DP groups eliminates redundant weight replication, freeing memory for higher throughput RLHF.

**Caption (verbatim):** Figure 8. Model weights resharding. 2 machines each with 4 GPUs are used for actor training and generation.

### Figure 8 (p.8) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig08.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p08.png]]*
> [!quote] caption
> Model weights resharding. 2 machines each with 4 GPUs are used for actor training and generation. model parameters updated in iteration 𝑖(step 1○in Figure 7), for generation within each micro DP group. Then, the batch of prompts are loaded to each model replica (step 2○), which generates responses (Generation stage of RLHF). Following this, 3D-HybridEngine performs an all-gather operation on the g

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 8) — Model Weights Resharding**

The figure compares two strategies for resharding actor-model weights across 2 machines × 4 GPUs between RLHF training and generation stages. Subfigure (a) "HybridFlow-V" applies the *same* parallel grouping to both phases: each GPU performs an all-gather of the **complete** weight set, then discards unused partitions — producing redundant (grey) weight copies that occupy memory. Subfigure (b) "HybridFlow" uses *different* optimized groupings per phase and restricts all-gather operations to within **Micro-DP groups only**, so each GPU retains only the partitions it actually needs, with no redundancy. Color-coded legend distinguishes GPU rank, model weight partitions, DP/TP groups, and all-gather scopes.

**Key takeaway:** Constraining all-gather to the intersection of training- and generation-time micro-DP groups eliminates redundant weight replication, freeing memory for higher throughput RLHF.

**Caption (verbatim):** Figure 8. Model weights resharding. 2 machines each with 4 GPUs are used for actor training and generation.

### Figure 9 (p.11) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig09.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]]*
> [!quote] caption
> PPO throughput. Numbers in parentheses are HybridFlow speedups compared with baselines. 8 16 32 64 128 # of GPUs 0 1 2 3

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Architecture/Components**: The figure consists of three rows of grouped bar charts (Figures 9, 10, 11), each containing four subfigures corresponding to Llama model sizes: 7B, 13B, 34B, and 70B. Each subfigure plots **throughput (tokens/s)** on the y-axis against the **number of GPUs** (8/16/32/64/128, varying by model size) on the x-axis. Four systems are compared via colored bars: NeMo-Aligner (blue), DS-Chat (orange), OpenRLHF (red), and HybridFlow (green).

**Data Flow**: The rows correspond to three RLHF algorithms — PPO (top), ReMax (middle), and Safe-RLHF (bottom) — illustrating end-to-end RLHF training throughput scaling.

**Key Technical Takeaway**: HybridFlow consistently and substantially outperforms all baselines across every model size and algorithm, achieving **1.5×–19.8× speedups**, with the largest gains at 70B scale where competing systems fail to scale efficiently.

## Verbatim Captions

**Figure 9.** PPO throughput. Numbers in parentheses are HybridFlow speedups compared with baselines.

**Figure 10.** ReMax throughput. Numbers in parentheses are HybridFlow speedups compared with baselines

**Figure 11.** Safe-RLHF throughput. Numbers in the parentheses are HybridFlow speedups compared with the baselines

### Figure 10 (p.11) ⭐深度解读
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]]
> [!quote] caption
> ReMax throughput. Numbers in parentheses are HybridFlow speedups compared with baselines 8 16 32 64 128 # of GPUs 0 1 2 3

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Architecture/Components**: The figure consists of three rows of grouped bar charts (Figures 9, 10, 11), each containing four subfigures corresponding to Llama model sizes: 7B, 13B, 34B, and 70B. Each subfigure plots **throughput (tokens/s)** on the y-axis against the **number of GPUs** (8/16/32/64/128, varying by model size) on the x-axis. Four systems are compared via colored bars: NeMo-Aligner (blue), DS-Chat (orange), OpenRLHF (red), and HybridFlow (green).

**Data Flow**: The rows correspond to three RLHF algorithms — PPO (top), ReMax (middle), and Safe-RLHF (bottom) — illustrating end-to-end RLHF training throughput scaling.

**Key Technical Takeaway**: HybridFlow consistently and substantially outperforms all baselines across every model size and algorithm, achieving **1.5×–19.8× speedups**, with the largest gains at 70B scale where competing systems fail to scale efficiently.

## Verbatim Captions

**Figure 9.** PPO throughput. Numbers in parentheses are HybridFlow speedups compared with baselines.

**Figure 10.** ReMax throughput. Numbers in parentheses are HybridFlow speedups compared with baselines

**Figure 11.** Safe-RLHF throughput. Numbers in the parentheses are HybridFlow speedups compared with the baselines

### Figure 11 (p.11) ⭐深度解读
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]]
> [!quote] caption
> Safe-RLHF throughput. Numbers in the parentheses are HybridFlow speedups compared with the baselines reward models. Each model is a Llama [73] model with sizes ranging from 7B to 70B. Safe-RLHF has an additional cost model whose architecture and size are the same as the re- ward model and ReMax eliminates the critic model. We use mixed precision for actor and critic training, i.e., BF16 for model 

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Architecture/Components**: The figure consists of three rows of grouped bar charts (Figures 9, 10, 11), each containing four subfigures corresponding to Llama model sizes: 7B, 13B, 34B, and 70B. Each subfigure plots **throughput (tokens/s)** on the y-axis against the **number of GPUs** (8/16/32/64/128, varying by model size) on the x-axis. Four systems are compared via colored bars: NeMo-Aligner (blue), DS-Chat (orange), OpenRLHF (red), and HybridFlow (green).

**Data Flow**: The rows correspond to three RLHF algorithms — PPO (top), ReMax (middle), and Safe-RLHF (bottom) — illustrating end-to-end RLHF training throughput scaling.

**Key Technical Takeaway**: HybridFlow consistently and substantially outperforms all baselines across every model size and algorithm, achieving **1.5×–19.8× speedups**, with the largest gains at 70B scale where competing systems fail to scale efficiently.

## Verbatim Captions

**Figure 9.** PPO throughput. Numbers in parentheses are HybridFlow speedups compared with baselines.

**Figure 10.** ReMax throughput. Numbers in parentheses are HybridFlow speedups compared with baselines

**Figure 11.** Safe-RLHF throughput. Numbers in the parentheses are HybridFlow speedups compared with the baselines

### Figure 12 (p.12) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig12.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p12.png]]*
> [!quote] caption
> Throughput of HybridFlow under different placements 32 64 96 128 # of GPUs

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 12):**

**Architecture/Components:** Two grouped bar charts comparing throughput (tokens/s) of four model-placement strategies — *Colocate*, *Split*, *Standalone*, and *HybridFlow* — across varying GPU counts. Subplot (a) evaluates a **13B model** on 16, 24, 32, 64, 96, and 128 GPUs; subplot (b) evaluates a **34B model** on 32, 48, 64, 96, and 128 GPUs.

**Data Flow:** Independent placement policies are run on identical hardware/model settings; per-GPU batch size shrinks as cluster size grows, exposing each strategy's scaling behavior under fixed global batch size.

**Key Technical Takeaway:** The optimal placement strategy is **cluster-size dependent** — *Colocate* dominates on small clusters (≤64 GPUs), *Split* wins for balanced 34B models at 96–128 GPUs, while *Standalone* excels for 13B at 128 GPUs. HybridFlow's adaptive placement (Algorithm 1) consistently matches or beats all fixed strategies, demonstrating that dynamic, model-aware resource allocation is essential for efficient large-scale RLHF training.

**Caption (verbatim):**
> *Figure 12.* Throughput of HybridFlow under different placements

### Figure 13 (p.12) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig13.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p12.png]]*
> [!quote] caption
> Placement comparison under 13B actor and reference policy & 70B critic and reward model.

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 12):**

**Architecture/Components:** Two grouped bar charts comparing throughput (tokens/s) of four model-placement strategies — *Colocate*, *Split*, *Standalone*, and *HybridFlow* — across varying GPU counts. Subplot (a) evaluates a **13B model** on 16, 24, 32, 64, 96, and 128 GPUs; subplot (b) evaluates a **34B model** on 32, 48, 64, 96, and 128 GPUs.

**Data Flow:** Independent placement policies are run on identical hardware/model settings; per-GPU batch size shrinks as cluster size grows, exposing each strategy's scaling behavior under fixed global batch size.

**Key Technical Takeaway:** The optimal placement strategy is **cluster-size dependent** — *Colocate* dominates on small clusters (≤64 GPUs), *Split* wins for balanced 34B models at 96–128 GPUs, while *Standalone* excels for 13B at 128 GPUs. HybridFlow's adaptive placement (Algorithm 1) consistently matches or beats all fixed strategies, demonstrating that dynamic, model-aware resource allocation is essential for efficient large-scale RLHF training.

**Caption (verbatim):**
> *Figure 12.* Throughput of HybridFlow under different placements

### Figure 14 (p.13) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig14.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p13.png]]*
> [!quote] caption
> Transition time between actor training and generation.

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 14):**

The figure consists of four grouped bar charts comparing transition time (seconds) across model scales (7B, 13B, 34B, 70B) versus GPU counts (8–128). Each subplot benchmarks four systems: **OpenRLHF** (red), **DS-Chat** (blue), **HybridFlow-V** (orange hatched), and **HybridFlow** (green hatched). The component axis isolates weight resharding overhead between actor training and generation phases, with all methods running identical generation workloads. HybridFlow's bars stay flat and low across GPU counts, while OpenRLHF and DS-Chat climb steeply with both scale and cluster size — a divergence most pronounced in the 70B chart.

**Key Takeaway:** HybridFlow's parallel grouping for generation eliminates per-layer all-gather overhead, capping transition time at ~5s even for 128 GPUs / 70B — a >89% reduction versus OpenRLHF's baselines.

**Caption (verbatim):**

**Figure 14.** Transition time between actor training and generation.

### Figure 15 (p.13) ⭐深度解读
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p13.png]]
> [!quote] caption
> Time breakdown on different generation parallel sizes of the actor model on 16 GPUs. various model scales, which is the time to reshard model weights from training to generation, under the same settings in §8.2. OpenRLHF’s transition time includes weight syn- chronization time between two copies of the actor model on different devices. HybridFlow reduces the transition time by 55.2% (11.7s) on ave

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 14):**

The figure consists of four grouped bar charts comparing transition time (seconds) across model scales (7B, 13B, 34B, 70B) versus GPU counts (8–128). Each subplot benchmarks four systems: **OpenRLHF** (red), **DS-Chat** (blue), **HybridFlow-V** (orange hatched), and **HybridFlow** (green hatched). The component axis isolates weight resharding overhead between actor training and generation phases, with all methods running identical generation workloads. HybridFlow's bars stay flat and low across GPU counts, while OpenRLHF and DS-Chat climb steeply with both scale and cluster size — a divergence most pronounced in the 70B chart.

**Key Takeaway:** HybridFlow's parallel grouping for generation eliminates per-layer all-gather overhead, capping transition time at ~5s even for 128 GPUs / 70B — a >89% reduction versus OpenRLHF's baselines.

**Caption (verbatim):**

**Figure 14.** Transition time between actor training and generation.

### Figure 16 (p.13) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig16.png]]
*整页渲染: ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p13.png]]*
> [!quote] caption
> Runtime of device mapping algorithm. The model size and # of GPUs are simultaneously scaled.

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 14):**

The figure consists of four grouped bar charts comparing transition time (seconds) across model scales (7B, 13B, 34B, 70B) versus GPU counts (8–128). Each subplot benchmarks four systems: **OpenRLHF** (red), **DS-Chat** (blue), **HybridFlow-V** (orange hatched), and **HybridFlow** (green hatched). The component axis isolates weight resharding overhead between actor training and generation phases, with all methods running identical generation workloads. HybridFlow's bars stay flat and low across GPU counts, while OpenRLHF and DS-Chat climb steeply with both scale and cluster size — a divergence most pronounced in the 70B chart.

**Key Takeaway:** HybridFlow's parallel grouping for generation eliminates per-layer all-gather overhead, capping transition time at ~5s even for 128 GPUs / 70B — a >89% reduction versus OpenRLHF's baselines.

**Caption (verbatim):**

**Figure 14.** Transition time between actor training and generation.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.9) ⭐深度解读
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-tab02.png]]
> [!quote] caption
> Transition overhead between training & generation

> [!tip] 表格解读（多模态）
> ## Description

The main figure shown is **Table 2**, which compares **transition overhead between training & generation** across three systems: **DS-Chat**, **HybridFlow-V**, and **HybridFlow**. The table presents three metrics:

- **Communication Volume (Comm. Vol):** DS-Chat uses `(t_pd−1)/t_pd · M`; HybridFlow-V uses `(tp−1)/tp · M`; HybridFlow uses `(tp−t_g p_g)/(t_g p_g · tp) · M`.
- **Peak Memory (Peak Mem.):** DS-Chat and HybridFlow-V both require full `M`; HybridFlow needs only `1/(t_g p_g) · M`.
- **Redundancy:** DS-Chat has `(1/t_pd) M`; HybridFlow-V has `(1/tp) M`; HybridFlow achieves **0**.

**Key technical takeaway:** HybridFlow's novel generation-stage parallel grouping (forming TP/PP groups by selecting ranks at intervals of `1/t_g` and `p/p_g`, then constructing micro-DP groups along TP/PP dimensions) enables weight overlap between training and generation on each device — eliminating reshard redundancy and shrinking peak memory by a factor of `t_g p_g`.

## Caption (verbatim)

> **Table 2.** Transition overhead between training & generation

## 关键公式（原文截图，无 LaTeX 源 — 引用前请核对图片）

### 公式截图 (p.7)
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-eq01.png]]
> 原文文本线索：`batch[“pretrain_loss”] = pretrain_loss`

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.7 `critic_metrics = critic.update_critic(batch, loss_func=algo_type)`
- p.7 `pretrain_loss = actor.compute_loss(pretrain_batch)`
- p.7 `batch[“pretrain_loss”] = pretrain_loss`
- p.7 `actor_metrics = actor.update_actor(batch, loss_func=algo_type)`
- p.8 `𝑁𝑎=𝑝×𝑡×𝑑=𝑝𝑔×𝑡𝑔×𝑑𝑔×𝑑such that 𝑑𝑔=`

## 相关论文

- [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] — AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning
- [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] — Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEMENT LEARNING
- [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] — DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
- [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] — Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning

## 技术点深读（DEEP）

![[deep/hybridflow-a-flexible-and-efficient-rlhf-framework]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/hybridflow-a-flexible-and-efficient-rlhf-framework.txt`（109820 字符）供引用检索。