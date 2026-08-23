---
paper_num: "46"
title: "MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs"
authors: "Ziheng Jiang1,∗Haibin Lin1,∗Yinmin Zhong2,∗Qi Huang1 Yangrui Chen1 Zhi Zhang1 Yanghua Peng1 Xiang Li1 Cong Xie1 Shibiao Nong1 Yulu Jia1 Sun He1 Hongmin Chen1 Zhihao Bai1 Qi Hou1 Shipeng Yan1 Ding Zhou1 Yiyao Sheng1 Zhuo "
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2402.15627"
pdf: "papers/megascale-scaling-large-language-model-training-to-more-than-10000-gpus.pdf"
slug: "megascale-scaling-large-language-model-training-to-more-than-10000-gpus"
tags: [training]
---

# MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs

> [!abstract] 摘要（原文）
> 1\. 🚀 MegaScale是一个用于在超过10,000个GPU上训练大型语言模型(LLM)的生产系统，旨在解决大规模训练中的效率和稳定性挑战。 2. ⚙️ MegaScale通过算法-系统协同设计，整合了模型优化、计算与通信重叠、算子优化、数据管道及网络调优，并利用深度可观测性和鲁棒训练框架实现故障容忍。 3. 💥 该系统在12,288个GPU上训练175B LLM时实现了55.2%的Model FLOPs Utilization (MFU)，比Megatron-LM提升1.34倍，并在数周的实际生产运行中自主修复和恢复了100多次。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Ziheng Jiang1,∗Haibin Lin1,∗Yinmin Zhong2,∗Qi Huang1 Yangrui Chen1 Zhi Zhang1 Yanghua Peng1 Xiang Li1 Cong Xie1 Shibiao Nong1 Yulu Jia1 Sun He1 Hongmin Chen1 Zhihao Bai1 Qi Hou1 Shipeng Yan1 Ding Zhou1 Yiyao Sheng1 Zhuo 
- **arXiv**: https://arxiv.org/abs/2402.15627
- **本地 PDF**: `papers/megascale-scaling-large-language-model-training-to-more-than-10000-gpus.pdf`
- **页数**: 16

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig01.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p02.png]]*
> [!quote] caption
> Data parallel training with ZeRO2. dependencies that contribute to stability issues. We develop a robust training framework to automate fault localization and recovery. We design heartbeat messages encapsulating various forms of information to facilitate real-time anomaly detection and provide early warnings. We implement a suite of diagnostic tests to identify nodes causing disruptions. We optimi

> [!tip] 技术解读（多模态）
> **Figure Description:**

The diagram depicts a two-stage data-parallel training loop using ZeRO2, shown as two identical, parallel pipelines (one per model replica) connected by two synchronization operations.

**Per-replica data flow (left → right):**
`Model Replica` → `Forward` (consumes `Data 0` / `Data 1`) → `Backward` → `Reduce-Scatter` → `Update Params` → `All-Gather` → (loops back to Model Replica)

**Cross-replica communication:**
- `sync grads`: vertical arrow between the two Reduce-Scatter nodes
- `gather params`: vertical arrow between the two All-Gather nodes

**Key technical takeaway (≤120 words):**
ZeRO2 eliminates memory redundancy in data-parallel training by partitioning gradients and optimizer states across devices instead of replicating them. After Backward, Reduce-Scatter ensures each rank retains only its slice of the globally averaged gradients (memory-efficient synchronization), enabling local parameter updates. The subsequent All-Gather temporarily reconstructs the full parameter set on every rank so the next Forward pass can proceed — then the partition resumes. This pipelined scatter-then-gather pattern achieves Megatron-LM–comparable throughput on a 175B model (55.2% MFU, 1.34× speedup) across 12,288 GPUs while keeping per-device memory proportional to 1/N rather than the full model+optimizer footprint.

**Caption (verbatim):**
Figure 1: Data parallel training with ZeRO2.

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig02.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p03.png]]*
> [!quote] caption
> Interleaved 1F1B pipeline. update the model. Instead of duplicating model states (like the optimizer states, gradients, and parameters), Zero Redun- dancy Optimizer (ZeRO) [11] shards these states across every data-parallel process. As a result, the traditional all-reduce operations that aggregate gradients are decomposed into sep- arate reduce-scatter and all-gather operations. This is because ev

> [!tip] 技术解读（多模态）
> **1) 架构/组件/数据流描述**

该图为**交错式 1F1B 流水线调度图**（Interleaved 1F1B Pipeline）。纵轴为 3 个流水线阶段（stage 0/1/2），横轴为时间步。每个阶段被细分为多个**虚拟子阶段**（图中以红、蓝色块区分），相同数字（如 0、1、2…5）代表同一 micro-batch 的前向/反向传递。红色虚线标出阶段内的交错切换点。整体体现"前向-反向交替执行"的 1F1B 节奏，以及通过虚拟子阶段增加流水线深度来减少气泡（pipeline bubble）的设计。

**2) 关键技术要点**

**核心创新**：将每个流水线阶段再切分为多个虚拟子阶段（virtual stages / model chunks），在相同内存占用下使同一时刻处于 in-flight 的 micro-batch 数翻倍，从而**显著降低流水线气泡比例**，提升训练吞吐——这是 Megatron-LM 交错调度相较于经典 1F1B 的关键改进。**

**3) 逐字转录 Caption**

> **Figure 2: Interleaved 1F1B pipeline.**

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig03.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p04.png]]*
> [!quote] caption
> Overlapping communication in tensor parallelism (TP) and sequence parallelism (SP) with parallel transformer block (PTB). with a large receptive field created by stacking layers of such windowed attention. This enables faster training without com- promising the accuracy. LAMB optimizer. Efficient training at a large scale is often hindered by batch size constraints. Particularly, increasing the ba

> [!tip] 技术解读（多模态）
> ## Figure 3 Description

**Architecture / Components / Data Flow**

The figure compares three transformer-block designs for hiding communication in 3D parallelism:

- **(a) PTB with SP + TP (baseline):** LayerNorm → **All-Gather** (SP) → QKV *ColParaLinear* ‖ *ColParaLinear* (TP) → Self-Attention → *RowParaLinear* ‖ *RowParaLinear* → **Reduce-Scatter** → LayerNorm. SP and TP regions are explicitly delineated.

- **(b) Fuse communication into Linears:** Same logical flow, but the All-Gather is folded into a fused *ColParaLinear-with-AG*, and the Reduce-Scatter is folded into a fused *RowParaLinear-with-RS*, removing the standalone comm nodes.

- **(c) Overlap communication with GEMM:** Two CUDA streams (S0 = kernel, S1 = comm). *Top* — input chunks A0…AN are copied on S1 while A×W GEMM runs on S0, producing B0…BN. *Bottom* — output chunks C0…CN are reduce-scattered on S1 concurrently with B×W GEMM on S0. Legend distinguishes kernel (pink) vs. comm (green) regions.

**Key Technical Takeaway (≈55 words):** By fusing all-gather/reduce-scatter into the linear layers and issuing them on a separate CUDA stream, MegaScale overlaps collective communication with the GEMM kernel on the critical path, hiding inter-rank latency without altering the tensor-parallel math—reducing SP/TP overhead to near-zero.

## Caption (verbatim)

**Figure 3: Overlapping communication in tensor parallelism (TP) and sequence parallelism (SP) with parallel transformer block (PTB).**

### Figure 4 (p.4) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig04.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p04.png]]*
> [!quote] caption
> The cool-down phase can be viewed as the inverse of the warm-up phase, allowing for the inverse application of the same technique. As for the steady phase, both the forward and backward computation are independent of adjacent communication operations. Taking the backward as an example, as shown in the right part of

> [!tip] 技术解读（多模态）
> **Figure Description (≈110 words)**

This diagram illustrates a **pipeline-parallel deep learning training schedule**, decomposed into a *Warm-up Phase* (left) and a *Steady Phase* (right) across two consecutive pipeline stages (`stage i` and `stage i+1`). Each horizontal dashed line represents a **stream** (a sub-batch / micro-batch), with solid arrows denoting **forward (FWD)** and **backward (BWD)** computation dependencies. Inter-stage communication is captured by **Send (S)** and **Receive (R)** operations attached to the streams. A large gray downward arrow at the top highlights **Communication Overlap**, showing how gradient/activation transfers are scheduled concurrently with computation. The warm-up phase fills the pipeline (only forward passes plus S/R ops), while the steady phase interleaves FWD/BWD blocks so that backward passes overlap with the sends from the next stage.

**Key Takeaway:** Backward computation is deliberately overlapped with the *Send* of activations/gradients, hiding communication latency behind compute—a core optimization in pipelined distributed training.

---

**Caption (transcribed verbatim):**

> *Communication Overlap*
> stage i | stage i+ 1
> Warm-up Phase | Steady Phase
>
> **Legend:** S — Send | R — Receive | --- Stream → Dependency | FWD — Forward | BWD — Backward

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig05.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p06.png]]*
> [!quote] caption
> Robust training workflow. interval and help recover the transmission more quickly when the link flapping period is short. 4

> [!tip] 技术解读（多模态）
> **Description:**

The figure depicts a fault-tolerant LLM training architecture split into a **Driver** (green) and **Executors** (yellow) cluster managed by **Kubernetes**. The Driver contains a User API (submits jobs), a Checker (triggers "stop && check" on executors and receives "check results"), a Log Analyser (collects executor "heartbeats" and triggers the Checker on anomalies), and state stores for Training Job Info, Evicted Pods, and Blocked IPs. Executors (0…N) each run training processes on one node.

**Key takeaway:** The system achieves automated fault recovery by combining heartbeat-based anomaly detection with lightweight self-check diagnostics; when a node fails, the driver blocks its IP via Kubernetes, evicts the pod, and replenishes it with a healthy node, then resumes from the latest checkpoint — yielding fault tolerance at >10,000-GPU scale with negligible human intervention.

**Caption (verbatim):**
"Figure 5: Robust training workflow."

### Figure 6 (p.8) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig06.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p08.png]]*
> [!quote] caption
> Inconsistent MFU observed in large-scale training. Differ- ent colors denote distinct executions of the same training job. mitigates the bandwidth constraints of HDFS, leading to a substantial reduction in the recovery time. 5

> [!tip] 技术解读（多模态）
> # Main Figure Description (Figure 7)

**Architecture/Components:** A 2D grid layout depicting a distributed training cluster of 12 hosts (host 0–11), each containing 4 GPU ranks, totaling 48 ranks (numbered 0–47). A vertical color bar maps execution time from 2.0s (light pink) to 2.5s (dark red). Three communication types are shown via dashed arrows: **TP Comm** (green, tensor parallelism), **DP Comm** (purple, data parallelism), and **PP Comm** (orange, pipeline parallelism). Rank 20 is rendered with a hatched pattern indicating user selection, revealing 3D dependency visualization.

**Data flow:** Latency measurements from the forward/backward computation phase across ranks are aggregated and rendered as a heat-map, exposing inter-machine variance and communication dependencies.

**Key Technical Takeaway:** Approximately **0.5% of machines are stragglers** (e.g., ranks 40, 41 on host 10; rank 32 on host 8 shown in dark red) that disproportionately bottleneck end-to-end training, since the slowest rank dictates overall throughput—explaining why peak MFU fluctuates across runs despite identical configurations.

---

# Verbatim Caption

**Figure 6:** Inconsistent MFU observed in large-scale training. Different colors denote distinct executions of the same training job.

**Figure 7:** Performance heat-map. The color denotes the running time of the code segments on a rank. The figure also shows the 3D visualization feature, where rank 20 has been selected and the dependency across different parallelism dimensions become visible.

### Figure 7 (p.8) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig07.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p08.png]]*
> [!quote] caption
> We gather latency data of the computation phase (forward and backward) across devices and average the latency across steps. The aggregated data is visualized host 0 0 1 2 3 host 3 12 13 14 15 host 6 24 25 26 27 host 9 36 37 38 39 host 4 16 17 18 19 host 7 28 29 30 31 host 10 40 41 42 43 host 5 20 21 22 23 host 8 32 33 34 35 host 11 44 45 46 47 host 1 4 5 6 7 host 2 8 9 10 11 DP Comm TP Comm PP Com

> [!tip] 技术解读（多模态）
> # Main Figure Description (Figure 7)

**Architecture/Components:** A 2D grid layout depicting a distributed training cluster of 12 hosts (host 0–11), each containing 4 GPU ranks, totaling 48 ranks (numbered 0–47). A vertical color bar maps execution time from 2.0s (light pink) to 2.5s (dark red). Three communication types are shown via dashed arrows: **TP Comm** (green, tensor parallelism), **DP Comm** (purple, data parallelism), and **PP Comm** (orange, pipeline parallelism). Rank 20 is rendered with a hatched pattern indicating user selection, revealing 3D dependency visualization.

**Data flow:** Latency measurements from the forward/backward computation phase across ranks are aggregated and rendered as a heat-map, exposing inter-machine variance and communication dependencies.

**Key Technical Takeaway:** Approximately **0.5% of machines are stragglers** (e.g., ranks 40, 41 on host 10; rank 32 on host 8 shown in dark red) that disproportionately bottleneck end-to-end training, since the slowest rank dictates overall throughput—explaining why peak MFU fluctuates across runs despite identical configurations.

---

# Verbatim Caption

**Figure 6:** Inconsistent MFU observed in large-scale training. Different colors denote distinct executions of the same training job.

**Figure 7:** Performance heat-map. The color denotes the running time of the code segments on a rank. The figure also shows the 3D visualization feature, where rank 20 has been selected and the dependency across different parallelism dimensions become visible.

### Figure 8 (p.9) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig08.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p09.png]]*
> [!quote] caption
> The trace shows events collected in a pipeline group on a unified timeline. Dependencies become visible when an event is selected.

> [!tip] 技术解读（多模态）
> **Figure 8 — Pipeline Trace Visualization**

**Architecture/Components/Data Flow:** The figure is a horizontally-stacked per-rank timeline visualization. Each row corresponds to a GPU worker (rank[0], rank[4], rank[8], rank[12]) within a pipeline-parallel group. Along each row, colored blocks denote discrete events — "forward" (green), "bac…" (backward, pink/red), "L" (loss/optimizer, gray), and short pink vertical spikes (likely all-reduce/comms). Time advances left→right, and curved pink arrows above/below the lanes represent inter-rank data-flow dependencies between producer and consumer stages. Selection of an event highlights its causal chain across ranks.

**Key Technical Takeaway:** Unified per-rank timeline plus dependency edges makes cascading NCCL timeouts visually traceable to a single stalled GPU worker, enabling rapid fault localization in 3D-parallel training.

**Caption (verbatim):**
"Figure 8: The trace shows events collected in a pipeline group on a unified timeline. Dependencies become visible when an event is selected."

### Figure 9 (p.10) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig09.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p10.png]]*
> [!quote] caption
> Weak-scaling training performance of Megatron-LM and

> [!tip] 技术解读（多模态）
> ## Figure 9 Description

**Components:** A grouped bar chart comparing Model FLOPs Utilization (MFU, %) between two systems — Megatron-LM (gray bars) and MegaScale (red hatched bars) — across three GPU counts (2,240 / 4,480 / 11,200) for the 530B model under weak-scaling conditions.

**Data values (annotated on bars):**
- 2,240 GPUs: Megatron-LM 49.20% vs MegaScale 54.30%
- 4,480 GPUs: Megatron-LM 48.80% vs MegaScale 54.10%
- 11,200 GPUs: Megatron-LM 48.20% vs MegaScale 54.30%

**Key takeaway:** MegaScale sustains ~54% MFU across a 5× GPU range, while Megatron-LM degrades slightly (49.2→48.2%), showing MegaScale's near-linear weak-scaling enabled by overlapping 3D-parallel communication.

## Caption (verbatim)

**Figure 9:** Weak-scaling training performance of Megatron-LM and MegaScale on the 530B model, where the batch size is scaled proportionally with the number of GPUs.

### Figure 10 (p.11) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig10.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p11.png]]*
> [!quote] caption
> The training loss curves in microbenchmark experiments.

> [!tip] 技术解读（多模态）
> # Figure 11: Production-Scale LLM Training Loss Curve

## Description

**Architecture/Components:**
- **Axes:** X-axis shows normalized "consumed tokens rate" (0.0–1.0, i.e., training progress from start to completion); Y-axis shows "loss" (≈0.2–0.8).
- **Curve:** A single composite line formed of many colored segments, exhibiting a sharp early drop from ~0.8 down to ~0.2 within the first ~5% of tokens, then a long flat plateau around 0.2.
- **Color encoding:** Each distinct color marks a fresh training restart after a fault; the curve is continuous across restarts because loss normalization anchors each segment.
- **System context:** Production run on **>10,000 GPUs**, several weeks long, training a **hundreds-of-billions-parameter** model on **multi-trillion tokens**.

**Data flow:** Tokens are fed continuously into the GPU cluster → loss is computed and logged per checkpoint → on failure, state is restored and training resumes from the last checkpoint → the new segment is plotted in a fresh color but joined seamlessly to the prior curve via shared loss scale.

## Key Technical Takeaway
MegaScale sustains smooth convergence across **100+ restarts** at >10K-GPU scale, demonstrating that its automatic fault detection and recovery pipeline (covering >90% of hardware/software faults) introduces no visible loss regression versus an uninterrupted run — validating reliability for multi-week, multi-trillion-token production LLM training.

## Caption (verbatim)
> Figure 11: The normalized training loss curve of a real production run on more than 10,000 GPUs for several weeks. This run trains a model with hundreds of billions of parameters on multi-trillion tokens. Different colors indicate training restarts. MegaScale repairs and recovers the training process for over 100 times in presence of failures.

### Figure 11 (p.11) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig11.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p11.png]]*
> [!quote] caption
> The normalized training loss curve of a real production run on more than 10,000 GPUs for several weeks. This run trains a model with hundreds of billions of parameters on multi-trillion tokens. Different colors indicate training restarts. MegaScale repairs and recovers the training process for over 100 times in presence of failures.

> [!tip] 技术解读（多模态）
> # Figure 11: Production-Scale LLM Training Loss Curve

## Description

**Architecture/Components:**
- **Axes:** X-axis shows normalized "consumed tokens rate" (0.0–1.0, i.e., training progress from start to completion); Y-axis shows "loss" (≈0.2–0.8).
- **Curve:** A single composite line formed of many colored segments, exhibiting a sharp early drop from ~0.8 down to ~0.2 within the first ~5% of tokens, then a long flat plateau around 0.2.
- **Color encoding:** Each distinct color marks a fresh training restart after a fault; the curve is continuous across restarts because loss normalization anchors each segment.
- **System context:** Production run on **>10,000 GPUs**, several weeks long, training a **hundreds-of-billions-parameter** model on **multi-trillion tokens**.

**Data flow:** Tokens are fed continuously into the GPU cluster → loss is computed and logged per checkpoint → on failure, state is restored and training resumes from the last checkpoint → the new segment is plotted in a fresh color but joined seamlessly to the prior curve via shared loss scale.

## Key Technical Takeaway
MegaScale sustains smooth convergence across **100+ restarts** at >10K-GPU scale, demonstrating that its automatic fault detection and recovery pipeline (covering >90% of hardware/software faults) introduces no visible loss regression versus an uninterrupted run — validating reliability for multi-week, multi-trillion-token production LLM training.

## Caption (verbatim)
> Figure 11: The normalized training loss curve of a real production run on more than 10,000 GPUs for several weeks. This run trains a model with hundreds of billions of parameters on multi-trillion tokens. Different colors indicate training restarts. MegaScale repairs and recovers the training process for over 100 times in presence of failures.

### Figure 12 (p.12) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig12.png]]
*整页渲染: ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p12.png]]*
> [!quote] caption
> The MFU becomes stable after addressing the stragglers and problematic code segments. Different colors represent different training trials with the same setup. executing diagnostic tests is less than 10 minutes. Moreover, the system can catch up to the training progress prior to the crash within 15 minutes from the latest checkpoints, maintain- ing over 90% effective training time rate, which is c

> [!tip] 技术解读（多模态）
> # Figure 12 Description

**Chart Type:** Line plot tracking Model FLOPs Utilization (MFU) over training steps.

**Axes:**
- **Y-axis:** MFU, ranging from 0.0 to 0.6
- **X-axis:** step, ranging from 0 to ~30,000

**Components / Data:**
- Multiple overlapping time-series traces (rendered in different colors — warm orange/red tones for early steps, transitioning to blue tones for later steps)
- Early steps (0–~10,000): visible dips/spikes where MFU momentarily drops well below 0.5
- Later steps (~10,000–30,000): traces flatten tightly around ~0.48–0.50 with only minor perturbations
- Each trace = one independent training trial with the same setup

**Key Technical Takeaway (≈115 words):**
After diagnosing and removing computational stragglers plus garbage-collection–induced noise, MFU converges to a stable plateau near 0.48–0.50 across all trials. The residual variance seen early on was traced to the forward pass — specifically irregular garbage collection and certain PyTorch operations on the critical path, *not* hardware. Synchronous collective communication forces every rank to wait for the slowest one, so any per-rank timing fluctuation propagates into step latency. The figure is empirical proof that disciplined code profiling (CUDA event timers, reverse chronological inspection) directly translates to stable, reproducible throughput at scale.

# Caption (verbatim)

> Figure 12: The MFU becomes stable after addressing the stragglers and problematic code segments. Different colors represent different training trials with the same setup.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.10) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-tab02.png]]
> [!quote] caption
> Strong-scaling training performance for the 175B model. We set the batch size to 6144 when training with 3072 to 12288 GPUs. For 256 to 1024 GPUs, we decrease the batch size to 768 due to GPU memory limit. We report the training time required for training 300B tokens here. The number in parentheses 

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**

The figure is a grouped bar chart plotting **Model FLOPs Utilization (MFU, %)** on the y-axis against **#GPUs** (2240, 4480, 11200) on the x-axis, comparing two systems: **Megatron-LM** (gray hatched bars) versus **MegaScale** (red hatched bars). Data labels sit atop each bar. Across all three GPU counts, MegaScale consistently delivers ~5–6 percentage points higher MFU than Megatron-LM, and unlike Megatron-LM (which slightly degrades from 49.20% → 48.80% → 48.20%), MegaScale stays flat at ~54%.

**Key takeaway:** MegaScale's optimizations preserve near-constant MFU as GPU count grows — demonstrating strong-scaling efficiency that Megatron-LM lacks.

**Caption (verbatim):**

Table 2: Strong-scaling training performance for the 175B model. We set the batch size to 6144 when training with 3072 to 12288 GPUs. For 256 to 1024 GPUs, we decrease the batch size to 768 due to GPU memory limit. We report the training time required for training 300B tokens here. The number in parenthesis in the MFU column represents the speedup of MegaScale compared to Megatron-LM.

### Table 3 (p.11) ⭐深度解读
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-tab03.png]]
> [!quote] caption
> MFU improvement breakdown when training the 175B model with 256 GPUs and batch size 256.

> [!tip] 表格解读（多模态）
> **Caption Verbatim (the only caption present in the provided text):**

"Table 3: MFU improvement breakdown when training the 175B model with 256 GPUs and batch size 256."

---

**Note:** The passage does not contain a description or caption of an actual figure. It references **Figure 10a** (convergence comparison — MegaScale with parallel transformer block + sliding window attention vs. baseline) and **Figure 10b** (effect of LAMB optimizer vs. ADAM with 4× larger batch size), but only provides a Table 3 caption. Without the figure itself or its caption text, I cannot describe an "architecture/components/data flow" diagram or its specific caption.

If you can share the figure's caption text (e.g., "Figure 10: ...") or an image of the figure, I'd be happy to provide the requested architecture description and verbatim transcription.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\begin{aligned} y = x + \text{MLP}(\text{LN}(x + \text{Attention}(\text{LN}(x)))) \end{aligned}
$$

$$
\begin{aligned} y = x + \text{MLP}(\text{LN}(x)) + \text{Attention}(\text{LN}(x)) \end{aligned}
$$

## 相关论文

- [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] — Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] — From ATOP to ZCube: Automated Topology Optimization Pipeline and A Highly Cost-Effective Network Topology for Large Model Training
- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey
- [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] — Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning

## 技术点深读（DEEP）

![[deep/megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/megascale-scaling-large-language-model-training-to-more-than-10000-gpus.txt`（77210 字符）供引用检索。