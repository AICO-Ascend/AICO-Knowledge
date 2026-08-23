---
paper_num: "57"
title: "Kimi K3: Open Frontier Intelligence"
authors: ""
date: "2026/7/27"
arxiv: "https://arxiv.org/abs/2607.24653"
pdf: "papers/kimi-k3-open-frontier-intelligence.pdf"
slug: "kimi-k3-open-frontier-intelligence"
tags: []
---

# Kimi K3: Open Frontier Intelligence

> [!abstract] 摘要（原文）
> We introduce Kimi K3, a 2.8T parameter Mixture-of-Experts model with 104 billion activated parameters, native vision capabilities, and a 1-million-token context window. Kimi K3 is built on Kimi Delta Attention and Attention Residuals, which improve information flow across sequence length and model depth. Together with Stable LatentMoE, which effectively activates 16 of 896 routed experts per token, and refined training and data recipes, these advances yield an approximately 2.5x improvement in overall scaling efficiency over Kimi K2. Post-training highlights reinforcement learning across general, agentic, and coding domains and multiple reasoning-effort levels, enabling compositional generalization and robust long-horizon execution. At 2.8T scale, Kimi K3 is supported by infrastructure advances in multiple areas: algorithm-system co-design for KDA, perfectly balanced expert-parallel training with efficient memory management, million-token agentic RL with persistent rollout and sandbox states, and deployment innovations. Extensive evaluations show that Kimi K3 achieves frontier-level performance across long-horizon coding, agentic, knowledge, reasoning, and vision tasks. While its overall performance still trails the most powerful proprietary models, namely Claude Fable 5 and GPT-5.6 Sol, Kimi K3 consistently outperforms other open and proprietary models evaluated in our suite. We release the full Kimi K3 model weights to facilitate future research and accelerate the broader deployment and adoption of frontier intelligence.

## 元信息
- **发表日期**: 2026/7/27
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2607.24653
- **本地 PDF**: `papers/kimi-k3-open-frontier-intelligence.pdf`
- **页数**: 47

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig01.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p01.png]]*
> [!quote] caption
> Kimi K3 main results. 1https://huggingface.co/moonshotai/Kimi-K3[cs.CL] 7 Aug 2026

> [!tip] 技术解读（多模态）
> **Figure description (≈115 words)**

Figure 1 is a multi-panel horizontal bar chart comparing Kimi K3 against six baselines (Kimi K2, GLM-5.2, GLM-5.2, GPT-5/5.6 Sol, Fab le 5, Opus 4.8) across two grouped domains: **Coding** (DeepSWE, Terminal-Bench 2.1, FrontierSWE, Kimi Code Bench 2.0, ProgramBench, SWE-Marathon) and **General & Visual Agents** (GDPval-AA v2 Elo, BrowseComp, AutomationBench, JobBench, CharXiv w/ tool, ZeroBench w/ tool). Kimi K3 bars are highlighted in blue; all bars are capped ("maxed out on thinking effort: max or xhigh"). Numeric scores are labeled at bar ends.

**Key takeaway:** Kimi K3 consistently outperforms every open-weight peer and is competitive with top proprietary frontier models across all twelve benchmarks, with the widest lead on SWE-Marathon (42.0 vs 35.0 next-best).

**Caption (verbatim):**

> Figure 1: Kimi K3 main results.

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig02.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p03.png]]*
> [!quote] caption
> The Kimi K3 architecture, organized around token, channel, and layer mixing, with a native vision pathway at the input.

> [!tip] 技术解读（多模态）
> Kimi K3 架构总览：每个 block 由 3 层 Kimi Delta Attention (KDA) + 1 层 Gated MLA 组成混合注意力，每个注意力层后接 Stable LatentMoE（16/896 路由专家+共享专家）做稀疏 channel mixing。深度维度引入 Attention Residuals (AttnRes)：用可学习 pseudo-query w 对 embedding 及前序各 block 输出算注意力权重 α，实现跨层选择性信息检索，突破顺序残差累积。输入侧原生视觉通路：MoonViT-V2 编码图像/视频经轻量 projector 映射进共享 embedding 空间。token/channel/layer 三维信息流设计，scaling 效率较 K2 提升 ~2.5×。

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig03.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p05.png]]*
> [!quote] caption
> Lower-bounded decay and its effect on chunkwise KDA computation. (a) Kimi Linear uses an unbounded negative-Softplus mapping, whereas Kimi K3 bounds the log-decay with a scaled sigmoid; the curves show A = 0 and gmin = −5. (b) Kimi Linear evaluates each diagonal tile with an explicit position-pair computation, while the bounded range in Kimi K3 allows all causal tiles to use dense Tensor Core matr

> [!tip] 技术解读（多模态）
> 下界衰减与 chunkwise KDA 计算：(a) Kimi Linear 用无界 negative-Softplus 映射 g=−e^A·Softplus(z)，K3 改为 g=g_min·Sigmoid(e^A·z) 把 log-decay 下界到 g_min=−5；(b) 有界范围使所有 causal tile（含对角 tile）都能用稠密 Tensor Core 矩阵乘，消掉逐位置对的 diagonal 路径。g_min=−5 时 16-token tile 累计 log-decay∈(−80,0)，rescale 因子 <e^80 仍在 BF16 动态范围内——分块线性注意力在 Tensor Core/NPU 上高效落地的关键参数化技巧。

### Figure 4 (p.7) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig04.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p07.png]]*
> [!quote] caption
> Gate and up branches of GLU, SwiGLU, and SiTU-GLU, together with their scalar responses, where σ denotes the sigmoid function. Both branches receive the scalar input x, and all curves share the domain x ∈[−10, 100]; the inset magnifies the near-origin region. SiTU-GLU, shown in red with β1 = 4 and β2 = 25, closely follows SwiGLU near the origin and approaches the bound |f(x)| ≤β1β2 = 100 for large

> [!tip] 技术解读（多模态）
> **Figure 4 Description:**

The figure is a two-panel comparison of three gated linear unit (GLU) activation variants. The left panel is a table listing the **Gate branch** and **Up branch** formulas for GLU (σ(x) and x), SwiGLU (x·σ(x) and x), and the proposed SiTU-GLU (β₁tanh(x/β₁)·σ(x) and β₂tanh(x/β₂)). The right panel plots the scalar response f(x) over x ∈ [−10, 100] for all three, with a magnified inset near the origin. SiTU-GLU (red) closely tracks SwiGLU near zero but saturates to the bounded value |f(x)| ≤ β₁β₂ = 100, while SwiGLU and GLU grow without bound.

**Key takeaway:** SiTU-GLU replaces the unbounded multiplicative factors of SwiGLU with smooth tanh-capped variants (controlled by β₁, β₂), preserving SwiGLU's local near-origin behavior while guaranteeing bounded activations — mitigating overflow risk in low-precision training.

**Caption verbatim:**

"Figure 4: Gate and up branches of GLU, SwiGLU, and SiTU-GLU, together with their scalar responses, where σ denotes the sigmoid function. Both branches receive the scalar input x, and all curves share the domain x ∈ [−10, 100]; the inset magnifies the near-origin region. SiTU-GLU, shown in red with β₁ = 4 and β₂ = 25, closely follows SwiGLU near the origin and approaches the bound |f(x)| ≤ β₁β₂ = 100 for large positive inputs, whereas SwiGLU remains unbounded."

### Figure 5 (p.8) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig05.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p08.png]]*
> [!quote] caption
> Illustration of Quantile Balancing with m = 8 tokens, n = 4 routed experts, and k = 1 selected expert per token. (a)

> [!tip] 技术解读（多模态）
> **1) 架构描述**

图示展示 MoE 路由的 **Quantile Balancing (QB)** 三阶段流程：
- **(a) 不均衡路由**：8 个 token 通过 Top-1 路由到 4 个专家，产生负载 (4,3,1,0)；深色圆圈表示过载专家，浅色虚线圈表示欠训专家。
- **(b) Quantile Balancing**：每个专家列添加偏置调整 $b_j^{(t+1)} - b_j^{(t)}$（红色虚线），置于 margin $s_{i,j} + b_j^{(t)} - \alpha_i^{(t)}$ 的第 (q+1) 大值处，使得恰好 q=2 个 margin 高于阈值；★ 标记减去列调整后的行级 Top-k 选择。
- **(c) 均衡路由**：调整后负载变为 (2,2,2,2)，红色边表示被 QB 修改的分配。

**2) 关键技术要点**

**无辅助损失的负载均衡**：QB 通过单次前向传播从路由器得分分位数直接推导专家偏置 $b_j$，既调节分发又不影响混合权重 $p_{i,j}$ 与路由器梯度更新，避免了传统辅助损失在大规模专家池（如 LatentMoE 的 896 个专家）下适应性慢、易振荡的问题。**

**3) 图注逐字转录**

**Figure 5**: Illustration of Quantile Balancing with $m=8$ tokens, $n=4$ routed experts, and $k=1$ selected expert per token. (a) Token-wise Top-$k$ routing (tokens on the left, experts on the right) produces loads (4, 3, 1, 0); darker circles indicate overheated experts, whereas faded and dashed circles indicate underutilized and dying experts, respectively. (b) Each gray bar is the margin of the currently biased score, $s_{i,j} + b_j^{(t)} - \alpha_i^{(t)}$, so the row-wise maxima reproduce the routing in (a). The dashed red line in each column is the bias adjustment $b_j^{(t)} - \widehat{b}_j^{(t+1)}$, placed at the $(q+1)$-th largest margin so that exactly $q=2$ margins exceed it. The marker ★ denotes the row-wise Top-$k$ choice after subtracting the column adjustments, i.e., the routing in (c). (c) The retained choices yield the balanced load (2, 2, 2, 2); red edges denote assignments changed by **QB**.**

### Figure 6 (p.9) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig06.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p09.png]]*
> [!quote] caption
> Vision-tower gradient norms in our pre-training ablations. Compared with the SigLIP-initialized MoonViT-3D, the from-scratch MoonViT-V2 maintains lower gradient norms with fewer spikes, indicating more stable optimization. 9

> [!tip] 技术解读（多模态）
> **Figure Description (≤120 words):**

The figure presents two side-by-side time-series line plots comparing vision-tower gradient norms during pre-training. **Component (a) "Full training trajectory"** spans training steps 7k–30k on the x-axis and gradient norm 0–~0.7 on the y-axis. **Component (b) "Zoomed view (14k–16k)"** magnifies the dashed-box region, with y-axis range 0–0.15 and x-axis 14–16. Two series are overlaid: **MoonViT-3D (SigLIP init.)** in blue exhibits sharp, frequent spikes reaching ~0.7 in the main plot and ~0.15 in the zoom; **MoonViT-V2 (from scratch)** in red/orange remains consistently low and flat near baseline. A dashed trapezoid visually links the zoomed window back into the main trajectory.

**Key takeaway:** Training the vision encoder from scratch (MoonViT-V2) yields markedly lower and more stable gradient norms than SigLIP initialization, suggesting more stable joint optimization without contrastive pre-training.

**Caption (verbatim):**
"Figure 6: Vision-tower gradient norms in our pre-training ablations. Compared with the SigLIP-initialized MoonViT-3D, the from-scratch MoonViT-V2 maintains lower gradient norms with fewer spikes, indicating more stable optimization."

### Figure 7 (p.11) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig07.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p11.png]]*
> [!quote] caption
> Fitted scaling-law curves for Kimi K2 and Kimi K3. Kimi K3 achieves 2.5× gain in scaling efficiency over Kimi K2.

> [!tip] 技术解读（多模态）
> **Description of Figure 7:**

The figure is a log-scale scatter plot comparing validation loss against training compute (FLOPs) for two models. **Axes:** x-axis is FLOPs on a logarithmic scale (roughly 10¹⁹ to 10²¹); y-axis is Validation Loss (unmarked, linear). **Series:** two dashed lines with star markers — blue for Kimi K2 and red for Kimi K3. Both follow the characteristic power-law (Chinchilla-style) downward trend, but the Kimi K3 curve sits consistently below Kimi K2 across the entire compute range. A horizontal arrow annotation labeled "2.5×" between the two curves quantifies the horizontal shift, indicating K3 needs far fewer FLOPs to reach the same loss.

**Key technical takeaway:** Despite its much larger parameter count (2.78T vs 1.04T, +167%), Kimi K3 achieves equivalent validation loss with ~2.5× less compute than K2, demonstrating a substantial improvement in scaling efficiency.

**Caption (verbatim):**
Figure 7: Fitted scaling-law curves for Kimi K2 and Kimi K3. Kimi K3 achieves 2.5× gain in scaling efficiency over Kimi K2.

### Figure 8 (p.13) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig08.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p13.png]]*
> [!quote] caption
> Scores and the average assistant steps across a variety of public and in-house evaluations during RL. By scaling RL FLOPs, tool-call steps scale up consistently, accompanied by a comprehensive improvement in the model’s overall capability.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Layout & Components:** Figure 8 is a 2×4 grid of dual-axis line plots, each tracking two metrics across training:
- **Solid blue line** → Score (%) (left axis)
- **Dashed red line** → Avg. assistant steps (right axis)
- **Shared x-axis** → RL FLOPs (compute budget)

**Domains covered** (left→right, top→bottom): Coding Experience, General Tool Use, Web Development, Agentic Search, Professional Workflows, Office Deliverables, Agentic Chart Understanding, Agentic Visual Puzzles.

**Data flow:** RL training compute (FLOPs) increases → both capability (score) and tool-call/step count are recorded per evaluation domain, revealing whether capability gains come from "thinking harder" (more steps) or pure skill.

**Key takeaway:** Across all eight domains, average assistant steps and score co-move upward with RL FLOPs, indicating that tool-call effort scales consistently with compute and drives the model's holistic capability gains.

## Verbatim Caption

> Figure 8: Scores and the average assistant steps across a variety of public and in-house evaluations during RL. By scaling RL FLOPs, tool-call steps scale up consistently, accompanied by a comprehensive improvement in the model's overall capability.

### Figure 9 (p.15) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig09.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p15.png]]*
> [!quote] caption
> Overview of knowledge-graph-guided task synthesis. The hierarchically organized knowledge graph represents concepts at multiple levels, ranging from broad domains to fine-grained concepts. Related nodes are sampled to form a keyword set that guides the retrieval of publicly available source materials. For each synthesis instance, the system selects a task type and uses the retrieved materials to s

> [!tip] 技术解读（多模态）
> ## Figure 9 — Architecture, Components & Data Flow

The figure has two coupled components. On the **left**, a hierarchical knowledge graph is rendered radially: a central root fans outward to first-level domains (CS/AI, Biomedicine, Coding, Humanities, Math, Physics, Chemistry, …), each branching into finer-grained concept nodes on the outer ring. Edges are directed from coarser to finer concepts. A small cluster of nodes on the upper right is highlighted, indicating a *sampled* sub-graph.

On the **right**, a vertical pipeline processes that sample:
1. **Keyword Set** — related nodes are joined into a keyword set (e.g., "RoPE", "GPU kernel").
2. **Material Retrieval** — keywords query the public web to fetch heterogeneous materials (academic articles, blog posts, code repos).
3. **Task Synthesis** — a task type is chosen per instance (Coding, Knowledge, Vision, …) and a training task is produced from the retrieved materials.

**Key takeaway:** The graph's hierarchy exposes both *granularity* (which level to sample) and *coverage* (which sibling branches to combine) as controllable knobs, allowing the same DAG to scale across web-scale, knowledge- and code-intensive domains without hand-curated seed corpora.

## Caption (verbatim)

Figure 9: Overview of knowledge-graph-guided task synthesis. The hierarchically organized knowledge graph represents concepts at multiple levels, ranging from broad domains to fine-grained concepts. Related nodes are sampled to form a keyword set that guides the retrieval of publicly available source materials. For each synthesis instance, the system selects a task type and uses the retrieved materials to synthesize a corresponding task.

### Figure 10 (p.17) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig10.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p17.png]]*
> [!quote] caption
> Completion curves on Camera Repair Management System, a black-box system replication task in which the agent reconstructs a hidden 3D-camera repair system as a web application through oracle queries. Completion denotes verifier-assessed task progress. 5

> [!tip] 技术解读（多模态）
> **Figure description:**

The figure is a step plot (completion curve) titled "Camera Repair Management System Replication," benchmarking four frontier models on a black-box system-replication task. The x-axis is "Normalized executor tool-call progress (%)" (0–100) and the y-axis is "Completion curve (%)" (0–100), i.e., verifier-assessed task progress as a function of tool calls consumed. Four curves are shown: **Kimi K3 (1.000, red)** — rises sharply around 60% tool progress and saturates at 100%; **Opus 4.8 (0.918, purple)** — gradual climb reaching ~92%; **GPT-5.5 (0.893, blue)** — aggressive early gains but plateaus near 89%; **Kimi K2.6 (0.560, green)** — flat, finishing at ~56%.

**Key takeaway:** Kimi K3 is the only model to fully complete the hidden 3D-camera repair system replication, reaching 100% verifier-confirmed completion while competitors stall at 56–92%, indicating stronger long-horizon agentic tool use. (~95 words)

**Caption verbatim:**

> Figure 10: Completion curves on Camera Repair Management System, a black-box system replication task in which the agent reconstructs a hidden 3D-camera repair system as a web application through oracle queries. Completion denotes verifier-assessed task progress.

### Figure 11 (p.19) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig11.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p19.png]]*
> [!quote] caption
> Computation, communication and offloading overlapped in different PP phases.

> [!tip] 技术解读（多模态）
> ## Figure Description

The figure (Figure 11) is a **pipeline-parallel execution timeline** showing how heterogeneous operations are overlapped across PP stages (rows labeled PP0, PP1, PP2) along a horizontal time axis.

**Components & Data Flow:**
- **Top legend strip**: categorizes operations — Computation, EP Comm, NCCL Comm, Local/Remote Activation Offload, plus auxiliary ops (DataLoader, ViT fwd, gather param, MoE block ops: Attn/SE1/MLP/SE2/EP-D/EP-C, reduce grad, offload/onload).
- **Timeline cells** (numbered 1–6, repeating): blue = forward pass; dark red = backward pass; orange = EP dispatch/recompute; hatched/dashed = shared-expert stages (SE1, SE2); dashed outlines = remote offload/onload.
- **Arrows** show remote offload from PP0 → PP2 (ViT activations pushed down-stream early, consumed late).

**Key Technical Takeaway:** Latency-hiding via aggressive overlap — vision activations are offloaded early in PP0 and only onloaded when needed in PP2, while all-to-all EP dispatch/combine and NCCL collectives are scheduled inside forward/backward kernels to avoid serializing communication with compute.

## Caption (verbatim)

**Figure 11:** Computation, communication and offloading overlapped in different PP phases.

### Figure 12 (p.23) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig12.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p23.png]]*
> [!quote] caption
> Fine-grained prefix caching within a physical cache block. A 6144-token physical block contains twelve 512-token hash blocks, with cached MLA blocks shown in blue and empty blocks in light gray. The markers below show the KDA checkpoint status at each hash boundary. An open circle (◦) denotes a boundary without a stored checkpoint, a gray dot (•) denotes a persisted KDA checkpoint, and an orange d

> [!tip] 技术解读（多模态）
> **Figure Description (Architecture / Components / Data Flow):**

The diagram illustrates a two-tier cache alignment scheme. A 6144-token physical block is divided into 12 equal 512-token *hash blocks*. The top row (**MLA KV**) shows five blue (cached) hash blocks followed by seven light-gray (empty) ones. The bottom row (**KDA ckpt**) places a marker at every hash-block boundary—open circles (○) for unstored boundaries, gray dots (●) for persisted checkpoints, and one orange dot (●) marking the hit at B = 2560. A downward arrow describes the recovery flow: *restore the KDA checkpoint at B; copy-on-write the partial MLA block; resume prefill from token B with zero recompute of [0, B)*.

**Key Technical Takeaway (≤120 words):**
Prefix hashing is decoupled from physical-block allocation: the coarse 6144-token block remains the allocation unit, while fine-grained 512-token *hash blocks* drive MLA cache lookup. Because MLA's per-token KV can be aligned to arbitrary hash endpoints but KDA's recurrent state can only be snapshotted sparsely, checkpoints are persisted at the last MLA hash boundary processed. On a partial-block hit at B = 2560, the KDA snapshot plus copy-on-write of the partial MLA block enables zero-recompute resumption across a chunk boundary that block-granular caching would have missed.

**Caption (verbatim):**

Figure 12: **Fine-grained prefix caching within a physical cache block.** A 6144-token physical block contains twelve 512-token hash blocks, with cached MLA blocks shown in blue and empty blocks in light gray. The markers below show the KDA checkpoint status at each hash boundary. An open circle (○) denotes a boundary without a stored checkpoint, a gray dot (●) denotes a persisted KDA checkpoint, and an orange dot (●) marks the checkpoint hit at B = 2560. Persisted checkpoints are sparse and typically coincide with conversation-turn boundaries. The request reuses the five MLA hash blocks and the KDA checkpoint at B, then resumes prefill without recomputing [0, B).

### Figure 13 (p.32) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig13.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p32.png]]*
> [!quote] caption
> Score vs. per-task inference cost on Kimi Code Bench 2.0, BrowseComp, GDPval-AA v2, and AA-Briefcase. Kimi K3 is marked with a star.

> [!tip] 技术解读（多模态）
> # Figure 13 Description

**Architecture/Components:** A 2×2 grid of scatter plots comparing **Kimi K3** (red star) against frontier proprietary (Claude Faible 5, Claude Opus 4.8, Claude Sonnet 5, Claude Mythos 5, GPT-5.5/5.6 Sol) and open-weight (GLM-5.2) models. Each panel plots a quality metric against **cost per task (USD)**:
- (a) Kimi Code Bench 2.0 — Score % vs cost
- (b) BrowseComp — Score % vs cost (includes low/medium/high/max effort variants and token-budget points)
- (c) GDPval-AA v2 — Elo vs cost
- (d) AA-Briefcase — Elo vs cost

**Data flow:** Each point represents one (model, configuration) deployment; proximity to the upper-left corner = better cost-efficiency frontier.

**Key Technical Takeaway:** Kimi K3 consistently lands on the Pareto frontier across all four suites — delivering near-SOTA accuracy at roughly **half the cost of Claude Faible 5** (e.g., 91.2% on Kimi Code Bench at ~$2 vs. 90.4% for GPT-5.6 Sol at ~$4; within 50 Elo of GPT-5.6 on GDPval-AA v2 at ~13% lower cost).

**Caption (verbatim):**
> *Figure 13: Score vs. per-task inference cost on Kimi Code Bench 2.0, BrowseComp, GDPval-AA v2, and AA-Briefcase. Kimi K3 is marked with a star.*

### Figure 14 (p.33) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig14.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p33.png]]*
> [!quote] caption
> Case study: GPU kernel optimization on AttnRes. 7

> [!tip] 技术解读（多模态）
> **Figure 14 Description:**

The figure is a step-line chart comparing GPU kernel optimization trajectories across four models on the AttnRes benchmark. **Axes:** x-axis = "Active hours" (0–20); y-axis = "Speedup vs. FLA Triton Baseline (%)" (0–64.1). **Series (step lines with markers):**
- 🔴 Kimi K3 (red) — rises earliest and steepest, plateauing near **59.7%** by ~13 h
- 🔵 Claude Fable 5 (blue) — climbs later, converging to **57.1%** by ~15 h
- 🟢 GPT-5.5 (green) — gradual ramp, ceiling at **30.8%** by ~20 h
- 🟤 GPT-5.6 Sol (maroon) — slowest progression, maxes out at **17.3%** by ~18 h

Dashed horizontal reference lines mark each model's final value.

**Key Technical Takeaway (≤120 words):**
Kimi K3 dominates in GPU kernel optimization, reaching the highest speedup (~59.7% over FLA Triton baseline) on AttnRes with the fastest wall-clock convergence among all evaluated agents. It surpasses Claude Fable 5 by ~2.6 pp and nearly doubles GPT-5.6 Sol's result. The step-wise trajectory reveals aggressive early-stage exploration: Kimi K3 begins climbing within ~1–2 hours and hits ~40% speedup by hour 5, while competitors remain near zero past hour 4. This indicates superior sample efficiency and search-space navigation for kernel-level performance engineering on Hopper-class GPUs.

**Caption (verbatim):**
Figure 14: Case study: GPU kernel optimization on AttnRes.

### Figure 15 (p.34) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig15.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p34.png]]*
> [!quote] caption
> Case study: GPU compiler development with MiniTriton. (a) CUDA-core and (b) tensor-core rooflines of MiniTriton kernels on an NVIDIA L20 (sm_89) against torch eager, torch.compile, Triton, and cuBLAS baselines (losing points included); (c) training-loss curves of the character-level GPT trained with MiniTriton versus torch eager; (d) two-GPU data-parallel training built on MiniTriton’s own distrib

> [!tip] 技术解读（多模态）
> **Description (architecture/components/data flow):** Figure 15 is a four-panel benchmark suite for MiniTriton, an in-house GPU compiler. Panels (a) and (b) are log–log roofline plots on an NVIDIA L20 (sm_89): (a) fp32 CUDA-core throughput (GFLOP/s) vs arithmetic intensity (FLOP/byte), and (b) tensor-core rooflines split into tf32 and bf16 tiers. Each plots MiniTriton against torch eager, torch.compile, Triton, and cuBLAS for kernels (matmul, softmax, flash_attn, kda, gpt50m_step), with losing points included for fairness. Panel (c) overlays training-loss curves (character-level GPT, 100 steps) for MiniTriton vs torch eager. Panel (d) shows cross-entropy for single-GPU vs two-GPU NCCL DDP, identical seeds/schedule, demonstrating lossless scaling. **Key takeaway:** MiniTriton sits on or near the roofline across kernels/precisions and converges identically to torch eager, while custom NCCL primitives match single-GPU training loss.

### Figure 16 (p.46) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig16.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p46.png]]*
> [!quote] caption
> Structure of the Kimi K3 chat template. (a) Context layout: global option messages precede the input messages, while one-shot option messages follow them, so that per-request options leave the history KV cache intact; dynamically loaded tools are injected mid-session as input option messages (dashed). (b) Anatomy of an assistant message: the body is organized into think, response, and tools channe

> [!tip] 技术解读（多模态）
> ## Description

The figure (Figure 16) depicts the **Kimi K3 chat template** across three panels illustrating the request/response structure:

**(a) Context layout** — A vertical stack of three zones feeding into a generation prefix:
- **Global option messages** (`tool-declare`, `think-effort`) appear *before* input messages
- **Input messages** (system / user / tool / assistant) carry the conversation history; dynamically loaded tools are injected mid-session as dashed "dynamic tool-declare" option messages
- **One-shot option messages** (`tool-choice`, `response-format`) are appended *after* input messages
- Prefix emits `[open]think[sep]` and `[open]response[sep]`

**(b) Assistant message** — Each assistant turn is an XML-like envelope `[open]message role="assistant"[sep]...` containing three sub-channels: `think`, `response`, and `tools`, closed by `[end_of_msg]`.

**(c) Tools channel** — Parallel tool calls are wrapped in `[open]call tool="..." index="N"[sep]` blocks, each with typed `[open]argument key type ... [close]argument[sep]` fields (e.g., `{"timeout": 150}`), enabling result matching by index.

**Key takeaway:** Placing per-request (one-shot) options *after* input messages keeps the historical KV cache reusable across requests, while the XML-style special-token markup (`[open]`/`[sep]`/`[close]`) eliminates tokenizer ambiguity and supports grammar-constrained decoding.

## Caption (verbatim)

> **Figure 16:** Structure of the Kimi K3 chat template. **(a)** Context layout: global option messages precede the input messages, while one-shot option messages follow them, so that per-request options leave the history KV cache intact; dynamically loaded tools are injected mid-session as input option messages (dashed). **(b)** Anatomy of an assistant message: the body is organized into `think`, `response`, and `tools` channels. **(c)** Expansion of the `tools` channel: parallel tool calls are indexed so that tool results can be matched to their calls, and arguments are typed.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.11) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-tab01.png]]
> [!quote] caption
> Architectural comparison between Kimi K2 and Kimi K3.

> [!tip] 表格解读（多模态）
> ## Description

The table compares Kimi K2 and K3 across ~22 architectural dimensions, organized into parameter counts, MoE/attention structure, context, and vision components. Key columns list the per-model value and a Δ showing relative change.

**Architecture/Components:** Both use MoE. K3 scales total parameters from 1.04T → 2.78T (+167%) and activated params from 32.6B → 104.2B (+220%), achieved by raising layers (61→93), routed experts (384→896), active experts/token (8→16), shared experts (1→2), and per-expert hidden dim (2,048→3,072). A new **Latent MoE Dimension (3584, 0.5×)** appears in K3. Attention shifts from pure MLA to a **Hybrid KDA–MLA** (69 KDA + 24 MLA layers), with activation changing SwiGLU → **SiTU-GLU**. Training context jumps 8× (128K → 1M). K3 also adds a native ViT encoder (401M params, 27 layers, patch 14, 12 heads).

**Key Technical Takeaway:** K3's gains come from jointly widening MoE capacity *and* replacing uniform MLA with a hybrid KDA–MLA stack, enabling 1M-token context with a native vision tower.

## Caption (verbatim)

*Table 1: Architectural comparison between Kimi K2 and Kimi K3.*

### Table 2 (p.27) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-tab02.png]]
> [!quote] caption
> Performance comparison of Kimi K3 against proprietary and open-source models. Bold denotes the best result for each benchmark and underline the second-best. Unless otherwise noted, Kimi K3 results are obtained with reasoning effort set to max and temperature equal to 1 . 0 . For HLE-Full, MMMU-Pro, 

> [!tip] 表格解读（多模态）
> **Note:** The provided image contains only the caption for **Table 2** — no figure, diagram, or actual table data is visible, so I cannot describe a graphical architecture or data flow. The following describes what the caption indicates about the table itself.

**Description:** Table 2 is a benchmark comparison matrix where rows are models (Kimi K3 vs. proprietary and open-source competitors) and columns are intelligence/reasoning benchmarks (e.g., HLE-Full, MMMU-Pro, CharXiv (RQ), Math-Vision, ZeroBench, plus standard suites). Cells contain performance scores; for select hard benchmarks, two scores are reported — without and with tool augmentation (general tools for HLE-Full, Python for vision benchmarks). Bold marks the best per column, underline the second-best.

**Key technical takeaway:** Kimi K3 is stress-tested under maximum reasoning effort (temperature 1.0) head-to-head with top frontier models, including tool-augmented variants — a deliberate apples-to-apples comparison rather than a single-config benchmark.

**Caption (verbatim):**

> Table 2: Performance comparison of Kimi K3 against proprietary and open-source models. **Bold** denotes the best result for each benchmark and underline the second-best. Unless otherwise noted, Kimi K3 results are obtained with reasoning effort set to max and temperature equal to 1.0. For HLE-Full, MMMU-Pro, CharXiv (RQ), Math-Vision, and ZeroBench, each cell reports the scores without and with tool augmentation (general tools for HLE-Full, Python for the vision benchmarks), in that order. <sup>†</sup>On the official Agents' Last Exam leaderboard, the Claude Faible 5 entry runs at xhigh effort with 40% of tasks annotated as downgraded.

### Table 3 (p.29) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-tab03.png]]
> [!quote] caption
> Results on our in-house benchmarks. Bold denotes the best reported result per benchmark; “-” denotes scores not yet included in this report. Unless otherwise noted, models are evaluated at maximum reasoning effort (GPT-5.5 at xhigh); harness assignments are shown in the Harness column. a 13 fallback

> [!tip] 表格解读（多模态）
> # Clarification

The image provided does **not** contain a figure with architecture, components, or data flow. It contains a **table** (Table 3) showing benchmark results from a Kimi K3 technical report. I cannot describe architecture/components/data flow that isn't present.

What is shown:
- A **header banner** ("Kimi K3: Open Frontier Intelligence" / "TECHNICAL REPORT")
- A **table caption** describing methodology and footnotes
- The **top row of a results table**, with column headers beginning to appear at the bottom (e.g., "Proprietary," "Open Weight")

There is no schematic, diagram, model architecture illustration, or data-flow visualization in this image.

# Verbatim Caption Transcription

> **Table 3:** Results on our in-house benchmarks. **Bold** denotes the best reported result per benchmark; "–" denotes scores not yet included in this report. Unless otherwise noted, models are evaluated at maximum reasoning effort (GPT-5.5 at *xhigh*); harness assignments are shown in the Harness column. ᵃ13 fallbacks and 1 refusal out of 80 tasks. ᵇ10 refusals out of 80 tasks. ᶜ3 refusals out of 80 tasks. ᵈIncludes 2 tasks that Claude Fable 5 refused to answer. ᵉIncludes 14 tasks that Claude Fable 5 refused to answer. ᶠ6 refusals out of 95 tasks. ᵍReported metric is 1−hallucination rate; higher is better.

If you intended to share a different figure (e.g., a model architecture diagram), please upload it and I'll describe that instead.

### Table 4 (p.29) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-tab04.png]]
> [!quote] caption
> Results on the in-house Kimi Webdev Bench: Kimi K3 (max) against Claude Opus 4.8 (max), both run with the Claude Code harness. The comparison is performed under blind expert judging, where experts score each output on code quality, feature completeness, visual fidelity, and interaction experience wi

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**
Table 4 presents a blind A/B comparison between Kimi K3 (max) and Claude Opus 4.8 (max) on the in-house Kimi Webdev Bench, with both models sharing the same Claude Code harness for fair parity. The table is structured as a domain-stratified results matrix: rows are four task categories (Games, 3D / WebGL / Shader, Website / UI Clone, Overall), and columns are four rating metrics (Win %, Tie %, Lose %, Win − Lose net margin). Domain experts score each output on code quality, feature completeness, visual fidelity, and interaction experience without model attribution. **Key takeaway:** Kimi K3 wins overall at 58.6% vs 27.6% losses (+31.0%), with its largest advantage in 3D/WebGL/Shader rendering tasks (+59.1% margin).

**Caption (verbatim):**
Table 4: Results on the in-house Kimi Webdev Bench: Kimi K3 (max) against Claude Opus 4.8 (max), both run with the Claude Code harness. The comparison is performed under blind expert judging, where experts score each output on code quality, feature completeness, visual fidelity, and interaction experience without knowing which model produced it. Win, Tie, and Lose report the percentage of prompts where Kimi K3's output is preferred, rated comparable, or dispreferred, respectively.

### Table 5 (p.32) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-tab05.png]]
> [!quote] caption
> Headline independent third-party evaluations of Kimi K3 (as of July 23, 2026). Bold denotes the best result per benchmark and underline the second best. Baseline scores are as reported by each source under its own evaluation setup a Text Arena entry is the xhigh variant listed on the leaderboard. b 

> [!tip] 表格解读（多模态）
> **Description of the main figure:**

The image displays the header and caption for **Table 5** of the "Kimi K3: Open Frontier Intelligence" technical report. The actual table data is not visible — only the descriptive caption is shown. The caption introduces a results table presenting independent third-party benchmark evaluations of the Kimi K3 model as of July 23, 2026, comparing it against baseline scores reported by various leaderboard sources.

**Key technical takeaway:**
Kimi K3's performance is benchmarked against multiple external leaderboards (e.g., Text Arena), with formatting conventions encoding results — **bold** marks the best score per benchmark and *underline* the second best — while parenthetical numbers indicate Kimi K3's specific leaderboard rank, and Elo-style scores are noted to drift as matches accumulate.

**Caption transcribed verbatim:**

> Table 5: Headline independent third-party evaluations of Kimi K3 (as of July 23, 2026). **Bold** denotes the best result per benchmark and <u>underline</u> the second best. Baseline scores are as reported by each source under its own evaluation setup ᵃText Arena entry is the xhigh variant listed on the leaderboard. ᵇText Arena entry is the high variant listed on the leaderboard. Numbers in parentheses are Kimi K3's rank on that leaderboard. Elo-style scores drift as additional matches accumulate.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf{S}_t = \left(\mathbf{I}-\beta_t\bm{k}_t\bm{k}_t^{\top}\right) \operatorname{Diag}(\bm{\alpha}_t)\mathbf{S}_{t-1} + \beta_t\bm{k}_t\bm{v}_t^{\top}, \qquad \tilde{\bm{o}}_t = \mathbf{S}_t^{\top}\bm{q}_t.
$$

$$
\bm{\gamma}_{[t]}^{i\rightarrow j} := \prod_{r=i}^{j}\bm{\alpha}_{[t]}^r, \qquad \bm{\gamma}_{[t]}^r := \bm{\gamma}_{[t]}^{1\rightarrow r}.
$$

$$
\bm{y}_t = \mathbf{W}_o\!\left[ \operatorname{Sigmoid}\!\left(\mathbf{W}_g\bm{x}_t\right) \odot \operatorname{RMSNorm}(\tilde{\bm{o}}_t) \right].
$$

$$
\bm{k}_{i} = \bm{v}_{i} = \begin{cases} \bm{h}_1 & i = 0 \\ f_i(\bm{h}_{i}) & 1 \leq i \leq l-1 \end{cases}
$$

$$
{\alpha_{i \to l}} = \frac{\phi\left(\bm{q}_{l}, \bm{k}_{i}\right)}{\sum_{j=0}^{l-1} \phi\left(\bm{q}_{l}, \bm{k}_{j}\right)}, \qquad \bm{h}_{l} = \sum_{i=0}^{l-1} {\alpha_{i \to l}} \cdot \bm{v}_{i}.
$$

$$
\mathbf{V} = \begin{cases} [\bm{b}_0, \bm{b}_1, \ldots, \bm{b}_{n-1}]^\top & \text{if } i = 1 \text{ (first layer of block } n\text{)} \\ [\bm{b}_0, \bm{b}_1, \ldots, \bm{b}_{n-1}, \bm{b}_n^{i-1}]^\top & \text{if } i \geq 2 \text{ (subsequent layers)} \end{cases}
$$

$$
\operatorname{SiTU\text{-}GLU}(\bm{x}) = \left[\beta_1\tanh\!\left(\frac{\mathbf{W}_g\bm{x}}{\beta_1}\right)\odot\operatorname{Sigmoid}(\mathbf{W}_g\bm{x})\right] \odot \left[\beta_2\tanh\!\left(\frac{\mathbf{W}_u\bm{x}}{\beta_2}\right)\right],
$$

$$
\mathcal{T}_i = \operatorname{argtop}_{k}\!\left(\bm{s}_i+\bm{b}\right), \qquad p_{i,j} = \frac{s_{i,j}}{\sum_{r\in\mathcal{T}_i}s_{i,r}}, \quad j\in\mathcal{T}_i.
$$

$$
\sum_{i=1}^{m}\mathbf{1}\!\left[s_{i,j}+\widehat{b}_j^{(t+1)}>\alpha_i^{(t)}\right],
$$

$$
\mathcal{L}_{\mathrm{LK}} = -\log \sum_{x \in \mathcal{V}} \min\!\left(p(x), q(x)\right),
$$

$$
\begin{aligned} \mathbf{M}_{[i+1]}^{t \leftarrow 1} := \prod_{r \leftarrow 1}^{t}\mathbf{M}_r \in \mathbb{R}^{d_k\times d_k}, \qquad \mathbf{S}_{[i+1]}^{t} & =\widetilde{\mathbf{S}}_{[i+1]}^{t} + \mathbf{M}_{[i+1]}^{t \leftarrow 1}\mathbf{S}_{[i]}^{T_i} \\ & = \widetilde{\mathbf{S}}_{[i+1]}^{t} + \mathbf{M}_{[i+1]}^{t \leftarrow 1}\sum_{j=1}^{i}\Big(\prod_{l \leftarrow j+1}^{i}\mathbf{M}_{[l]}^{T_l \leftarrow 1}\Big)\widetilde{\mathbf{S}}_{[j]}^{T_j}\in \mathbb{R}^{d_k\times d_v}. \end{aligned}
$$

$$
\beta\tanh\!\left(\frac{z}{\beta}\right) = z + O\!\left(\frac{z^3}{\beta^2}\right).
$$

$$
\left\|\operatorname{SiTU\text{-}GLU}(\bm{x})\right\|_{\infty} \leq \beta_1\beta_2 = 100,
$$

$$
\max_{x_{i,j}\in\{0,1\}} \sum_{i,j} x_{i,j}s_{i,j} \qquad \text{s.t.}\qquad \sum_j x_{i,j}=k, \qquad \sum_i x_{i,j}=\frac{mk}{n}.
$$

$$
\max_{x_{i,j}\in[0,1]}\min_{\alpha_i,\beta_j}\; \sum_{i,j} x_{i,j}s_{i,j} - \sum_i \alpha_i\Big(\sum_j x_{i,j} - k\Big) - \sum_j \beta_j\Big(\sum_i x_{i,j} - \tfrac{mk}{n}\Big).
$$

$$
\min_{\alpha_i,\beta_j}\max_{x_{i,j}\in[0,1]}\; \sum_{i,j} x_{i,j}\big(s_{i,j} - \alpha_i - \beta_j\big) + k\sum_i \alpha_i + \frac{mk}{n}\sum_j \beta_j.
$$

$$
\min_{\alpha_i,\beta_j}\; \mathcal{L}(\bm{\alpha},\bm{\beta}) := \sum_{i,j}\max\big(0,\; s_{i,j} - \alpha_i - \beta_j\big) + k\sum_i \alpha_i + \frac{mk}{n}\sum_j \beta_j.
$$

$$
\min_{\alpha}\; k\alpha + \sum_{j}\max\big(0,\; s_{i,j} - \beta_j - \alpha\big).
$$

$$
\alpha_i^* = \operatorname{quantile}_{1-k/n}\big(\bm{s}_i - \bm{\beta}\big).
$$

$$
\beta_j^* = \operatorname{quantile}_{1-k/n}\big(\bm{s}_{:,j} - \bm{\alpha}\big).
$$

## 技术点深读（DEEP）

![[deep/kimi-k3-open-frontier-intelligence]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/kimi-k3-open-frontier-intelligence.txt`（189122 字符）供引用检索。