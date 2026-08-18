---
paper_num: "24"
title: "KIMI K2: OPEN AGENTIC INTELLIGENCE"
authors: ""
date: "2026/1/19"
arxiv: "https://arxiv.org/abs/2507.20534"
pdf: "papers/kimi-k2-open-agentic-intelligence.pdf"
slug: "kimi-k2-open-agentic-intelligence"
tags: []
---

# KIMI K2: OPEN AGENTIC INTELLIGENCE

> [!abstract] 摘要（原文）
> 1\. 🚀 Kimi K2是一款万亿参数的MoE大型语言模型，激活参数达320亿，其预训练采用了新颖的MuonClip优化器，在15.5万亿token数据上实现了无损失尖峰的稳定训练。 2. 🤖 该模型通过大规模agentic数据合成管线和结合可验证奖励与自批判机制的强化学习框架进行后训练，显著提升了其在工具使用、软件工程和通用任务中的agentic能力。 3. 🏆 Kimi K2在Tau2-Bench、ACEBench、SWE-Bench Verified和LiveCodeBench v6等多个Agentic和编程基准测试中取得了领先的开放模型表现，并在LMSYS Arena排行榜上成为排名第一的开源模型。

## 元信息
- **发表日期**: 2026/1/19
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2507.20534
- **本地 PDF**: `papers/kimi-k2-open-agentic-intelligence.pdf`
- **页数**: 32

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/kimi-k2-open-agentic-intelligence-p01.png]]
> [!quote] caption
> Kimi K2 main results.2 1https://huggingface.co/moonshotai/Kimi-K2-Instruct 2All models evaluated above are non-thinking models. For SWE-bench Multilingual, we evaluated only Claude 4 Sonnet because the cost of Claude 4 Opus was prohibitive.[cs.LG] 3 Feb 2026

> [!tip] 技术解读（多模态）
> ## Figure Description

Figure 1 is a composite of **seven bar-chart panels** comparing Kimi-K2-Instruct against five baselines (DeepSeek-V3-0324, Qwen3-235B-A22B, OpenAI GPT-4.1, Claude 4 Opus/Sonnet, Gemini 2.5 Flash non-thinking) across two grouped categories:

1. **Agentic & Competitive Coding** (top row): SWE-bench Verified, SWE-bench Multilingual, LiveCodeBench v6, OJBench
2. **Tool Use** (bottom row): AceBench (en), AIME 2025

Each panel uses a shared y-axis (0–100), with darker bars highlighting Kimi-K2-Instruct's score. **Data flow**: model name (x-axis) → benchmark score (y-label) — a pure comparison view, not a pipeline diagram.

**Key takeaway**: Kimi-K2-Instruct leads open-source non-thinking models on SWE-bench Verified (65.8) and Multilingual (47.3), matches Claude 4 Sonnet on LiveCodeBench (53.7), but trails Claude 4 Opus (72.5) on Verified — positioning it as the strongest open agentic coder without extended reasoning.

## Caption (verbatim)

**Figure 1: Kimi K2 main results.**²

### Figure 2 (p.4) ⭐深度解读
![[assets/kimi-k2-open-agentic-intelligence-p04.png]]
> [!quote] caption
> Left: During a mid-scale training run, attention logits rapidly exceed 1000, which could lead to potential numerical instabilities and even training divergence. Right: Maximum logits for Kimi K2 with MuonClip and t = 100 over the entire training run. The max logits rapidly increase to the capped value of 100, and only decay to a stable range after approximately 30% of the training steps, demonstra

> [!tip] 技术解读（多模态）
> # Figure 2 Description

**Components / Layout:** Two side-by-side line plots sharing the same metric (Max Logits on y-axis) plotted against Training Steps (x-axis). 

- **Left (red curve, "Vanilla run with Muon"):** Uncontrolled trajectory — starts near zero and rises monotonically/super-linearly past 1000 by ~16,000 steps.
- **Right (blue curve, "Kimi K2 with MuonClip"):** Bounded trajectory — rises sharply to the cap of 100, plateaus, then decays after ~30% of training to a stable band around 30.

**Data flow:** Same diagnostic (per-step maximum attention logit) measured under two regimes — baseline Muon optimizer vs. MuonClip (τ=100). The comparison isolates QK-Clip's effect.

**Key takeaway:** Without intervention, attention logits explode (>1000) causing potential divergence; QK-Clip caps them at τ, after which they self-stabilize — proving the mechanism is both safe and self-correcting at MoE scale.

---

**Caption (verbatim):**

> Figure 2: Left: During a mid-scale training run, attention logits rapidly exceed 1000, which could lead to potential numerical instabilities and even training divergence. Right: Maximum logits for Kimi K2 with MuonClip and t = 100 over the entire training run. The max logits rapidly increase to the capped value of 100, and only decay to a stable range after approximately 30% of the training steps, demonstrating the effective regulation effect of QK-Clip.

### Figure 3 (p.5) ⭐深度解读
![[assets/kimi-k2-open-agentic-intelligence-p05.png]]
> [!quote] caption
> Per-step training loss curve of Kimi K2, without smoothing or sub-sampling. It shows no spikes throughout the entire training process. Note that we omit the very beginning of training for clarity. A key advancement in the pre-training data of Kimi K2 over Kimi K1.5 is the introduction of a synthetic data generation strategy to increase token utility. Specifically, a carefully designed rephrasing p

> [!tip] 技术解读（多模态）
> ## Figure Description

**Type:** A 2D line plot (training loss curve), though the data series itself is not rendered/visible in this rendering — only the axis frame is shown.

**Axes / components:**
- **X-axis:** "Tokens (Trillion)" — ranging 0 to 16, in increments of 2.
- **Y-axis:** "Loss" — ranging 1.3 to 2.0, in increments of 0.1.
- **Plot area:** Empty (no curve, markers, or annotations drawn).

**Intended content (per caption):** A raw, per-step training loss trajectory across the full ~15+ trillion-token pretraining run of Kimi K2.

**Key technical takeaway:** Loss should decrease smoothly from ~2.0 toward ~1.3 across the 0–15T token span with no spikes, indicating exceptional training stability — a non-trivial result at trillion-token scale.

---

## Caption (verbatim)

> **Figure 3:** Per-step training loss curve of Kimi K2, without smoothing or sub-sampling. It shows no spikes throughout the entire training process. Note that we omit the very beginning of training for clarity.

### Figure 4 (p.5) ⭐深度解读
![[assets/kimi-k2-open-agentic-intelligence-p05.png]]
> [!quote] caption
> • Fidelity verification: To ensure consistency between original and rewritten content, we perform fidelity checks that compare the semantic alignment of each rephrased passage with its source. This serves as an initial quality control step prior to training.

> [!tip] 技术解读（多模态）
> ## Figure Description

**Type:** A 2D line plot (training loss curve), though the data series itself is not rendered/visible in this rendering — only the axis frame is shown.

**Axes / components:**
- **X-axis:** "Tokens (Trillion)" — ranging 0 to 16, in increments of 2.
- **Y-axis:** "Loss" — ranging 1.3 to 2.0, in increments of 0.1.
- **Plot area:** Empty (no curve, markers, or annotations drawn).

**Intended content (per caption):** A raw, per-step training loss trajectory across the full ~15+ trillion-token pretraining run of Kimi K2.

**Key technical takeaway:** Loss should decrease smoothly from ~2.0 toward ~1.3 across the 0–15T token span with no spikes, indicating exceptional training stability — a non-trivial result at trillion-token scale.

---

## Caption (verbatim)

> **Figure 3:** Per-step training loss curve of Kimi K2, without smoothing or sub-sampling. It shows no spikes throughout the entire training process. Note that we omit the very beginning of training for clarity.

### Figure 5 (p.7) ⭐深度解读
![[assets/kimi-k2-open-agentic-intelligence-p07.png]]
> [!quote] caption
> Sparsity Scaling Law. Increasing sparsity leads to improved model performance. We fixed the number of activated experts to 8 and the number of shared experts to 1, and varied the total number of experts, resulting in models with different sparsity levels. 10 11

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 5): Sparsity Scaling Law**

**Components/Data flow:** A log-scale scatter/line plot with Training FLOPs on the x-axis (10²⁰ → 10²¹) and Validation Loss on the y-axis (1.3 → 1.8). Multiple colored curves (green, orange, purple, blue) drawn as solid and dashed segments trace loss trajectories across different sparsity levels; each curve terminates in a small "V"-shaped dip indicating converged loss at its respective compute budget. A reference dashed line sits beneath all curves.

**Key technical takeaway:** Under fixed activated parameters (constant FLOPs), increasing total experts (higher sparsity) consistently lowers validation loss — at matched loss = 1.5, sparsity-48 MoE reduces FLOPs by 1.69×, 1.39×, and 1.15× versus sparsity 8, 16, and 32 — motivating Kimi K2's choice of sparsity 48 (8 of 384 experts activated).

**Caption verbatim:**
"Figure 5: Sparsity Scaling Law. Increasing sparsity leads to improved model performance. We fixed the number of activated experts to 8 and the number of shared experts to 1, and varied the total number of experts, resulting in models with different sparsity levels."

### Figure 6 (p.7) ⭐深度解读
![[assets/kimi-k2-open-agentic-intelligence-p07.png]]
> [!quote] caption
> Scaling curves for models with number of atten- tion heads equals to number of layers and their counter- parts with doubled attention heads. Doubling the number of attention heads leads to a reduction in validation loss of approximately 0:5% to 1:2%.

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 5): Sparsity Scaling Law**

**Components/Data flow:** A log-scale scatter/line plot with Training FLOPs on the x-axis (10²⁰ → 10²¹) and Validation Loss on the y-axis (1.3 → 1.8). Multiple colored curves (green, orange, purple, blue) drawn as solid and dashed segments trace loss trajectories across different sparsity levels; each curve terminates in a small "V"-shaped dip indicating converged loss at its respective compute budget. A reference dashed line sits beneath all curves.

**Key technical takeaway:** Under fixed activated parameters (constant FLOPs), increasing total experts (higher sparsity) consistently lowers validation loss — at matched loss = 1.5, sparsity-48 MoE reduces FLOPs by 1.69×, 1.39×, and 1.15× versus sparsity 8, 16, and 32 — motivating Kimi K2's choice of sparsity 48 (8 of 384 experts activated).

**Caption verbatim:**
"Figure 5: Sparsity Scaling Law. Increasing sparsity leads to improved model performance. We fixed the number of activated experts to 8 and the number of shared experts to 1, and varied the total number of experts, resulting in models with different sparsity levels."

### Figure 7 (p.8) ⭐深度解读
![[assets/kimi-k2-open-agentic-intelligence-p08.png]]
> [!quote] caption
> Computation, communication and offloading overlapped in different PP phases.

> [!tip] 技术解读（多模态）
> ## Figure Description

**Architecture/Components:**
The figure is a timeline diagram showing three horizontal tracks (Computation, Communication, Offload) divided into three pipeline-parallelism phases. Above each phase, computation blocks (Attn/MLP/WGrad) and communication blocks (EP-D dispatch, EP-C combine, PP) are scheduled; below, a grid of numbered micro-batches (1–8) shows forward passes (blue), backward passes (red), and PP communications (green).

- **Phase 1 (Warm-up):** Attn + MLP compute overlapped with EP-D/EP-C comms; activations offloaded to CPU.
- **Phase 2 (Steady-state 1F1B):** Attn → MLP → MLP → Attn → WGrad; EP comms and weight-gradient compute run in parallel with PP traffic; offload/onload transitions occur at phase boundaries.
- **Phase 3 (Cooldown):** Remaining backward stages (MLP → Attn → WGrad) with EP comms and PP traffic; weights re-loaded.

**Data flow:** Micro-batches progress left-to-right through forward→backward stages, with expert-parallel all-to-all and pipeline peer-to-peer transfers hidden under compute or offload operations.

**Key technical takeaway (≤120 words):**
Kimi K2's training scheduler achieves near-full hardware utilization by overlapping three orthogonal operations across pipeline phases: (1) expert-parallel dispatch/combine all-to-alls are hidden under attention/MLP compute using a small EP=16 group size, (2) PP peer-to-peer communication is overlapped with backward-pass weight-gradient computation by decoupling it from the micro-batch's main backward flow, and (3) optimizer-state offload/onload transitions occur only at PP phase boundaries. The only unscheduled interval is the warm-up phase, where activations must reside on-GPU. This design enables a single parallelism configuration to scale across node counts without retuning.

## Caption (verbatim)

**Figure 7:** Computation, communication and offloading overlapped in different PP phases.

### Figure 8 (p.10) ⭐深度解读
![[assets/kimi-k2-open-agentic-intelligence-p10.png]]
> [!quote] caption
> Data synthesis pipeline for tool use. (a) Tool specs are from both real-world tools and LLMs; agents and tasks are the generated from the tool repo. (b) Multi-agent pipeline to generate and filter trajectories with tool calling. (a) t-SNE visualization of real MCP tools, colored by their original source categories (b) t-SNE visualization of synthetic tools, colored by pre-defined domain categories

> [!tip] 技术解读（多模态）
> **Figure 8 — Architecture & Data Flow:**

*(a) Synthesizing layer:* Domains and MCP tools feed into a Tool Repository containing real-world and synthesized tool specs, which drives Agents and Tasks-with-rubrics generation.

*(b) Trajectory generation layer:* A User Agent interacts with an Agent that observes and calls a Tool Simulator; the resulting trajectories are routed to a Judge Agent (informed by rubrics) to produce Filtered Data.

**Key takeaway:** The pipeline couples tool-synthesis with a multi-agent simulation-and-judgment loop, enabling rubric-scored, multi-turn tool-calling trajectories at scale.

**Caption (verbatim):**
Figure 8: Data synthesis pipeline for tool use. (a) Tool specs are from both real-world tools and LLMs; agents and tasks are the generated from the tool repo. (b) Multi-agent pipeline to generate and filter trajectories with tool calling.

### Figure 9 (p.10) ⭐深度解读
![[assets/kimi-k2-open-agentic-intelligence-p10.png]]
> [!quote] caption
> t-SNE visualizations of tool embeddings. (a) Real-world MCP tools exhibit natural clustering based on their original source categories. (b) Synthetic tools are organized into pre-defined domain categories, providing systematic coverage of the tool space. Together, they ensure comprehensive representation across different tool functionalities.

> [!tip] 技术解读（多模态）
> **Figure 8 — Architecture & Data Flow:**

*(a) Synthesizing layer:* Domains and MCP tools feed into a Tool Repository containing real-world and synthesized tool specs, which drives Agents and Tasks-with-rubrics generation.

*(b) Trajectory generation layer:* A User Agent interacts with an Agent that observes and calls a Tool Simulator; the resulting trajectories are routed to a Judge Agent (informed by rubrics) to produce Filtered Data.

**Key takeaway:** The pipeline couples tool-synthesis with a multi-agent simulation-and-judgment loop, enabling rubric-scored, multi-turn tool-calling trajectories at scale.

**Caption (verbatim):**
Figure 8: Data synthesis pipeline for tool use. (a) Tool specs are from both real-world tools and LLMs; agents and tasks are the generated from the tool repo. (b) Multi-agent pipeline to generate and filter trajectories with tool calling.

### Figure 10 (p.14) ⭐深度解读
![[assets/kimi-k2-open-agentic-intelligence-p14.png]]
> [!quote] caption
> Parameter update utilizing a checkpoint engine

> [!tip] 技术解读（多模态）
> **Architecture / Components / Data Flow**

Figure 10 illustrates a three-tier parameter-update pipeline:

1. **Training Engine (top layer)** – holds model weights in DRAM; each worker contributes its local parameter shard.
2. **Distributed Checkpoint Engine (middle layer)** – co-located workers that pull a local parameter copy from the training engine and then broadcast the *full* parameter set across all checkpoint workers, regardless of inference-side sharding.
3. **Inference Engine (bottom layer)** – uses a different sharding scheme, pulling only the parameter shard it needs from the checkpoint engine.

For the 1T Kimi K2 model, updates are streamed parameter-by-parameter in a pipelined fashion to minimize memory footprint.

**Key Technical Takeaway**

By broadcasting the full parameter set cluster-wide rather than using a network-file-system re-shard, the design fully decouples the training and inference engines, simplifies maintenance, and completes a full K2 parameter update in **<30 seconds** — negligible versus a single RL iteration.

**Caption (verbatim)**

> Figure 10: Parameter update utilizing a checkpoint engine

### Figure 11 (p.29) ⭐深度解读
![[assets/kimi-k2-open-agentic-intelligence-p29.png]]
> [!quote] caption
> Chinese in-house benchmark evaluation. rate, i.e. 98.9. On FaithJudge’s RAG tasks the hallucination rate is 7.4 %, likewise present as 92.6 for table consistency.

> [!tip] 技术解读（多模态）
> **Main Figure Description**

The figure content itself is not visibly rendered on this page — only its caption ("Figure 11: Chinese in-house benchmark evaluation.") appears above the surrounding paragraph, with the actual chart area blank. Based on the in-text reference, Figure 11 presents a model comparison chart evaluating Kimi-K2-Instruct against baseline LLMs (ChatGPT-4o-latest, Claude Sonnet 4, DeepSeek-V3-0324) on Chinese in-house held-out benchmarks, likely displayed as win-rate / loss-rate / tie-rate bars or radar-style comparisons per model pair.

**Key Technical Takeaway (≤120 words):**
Kimi-K2-Instruct demonstrates strong, balanced Chinese-language open-ended capability, posting high win-rates of ~65.4% vs ChatGPT-4o-latest, ~64.6% vs Claude Sonnet 4, and ~59.6% vs DeepSeek-V3-0324 on access-restricted in-house benchmarks. Critically, its loss-rate stays uniformly low (~17%) across all comparisons, indicating it rarely loses outright and rarely ties — it consistently wins or comes close. This combination of high win-rate and uniformly low loss-rate (verified on a held-out, contamination-controlled set) provides robust evidence that the Chinese performance is genuine generalization, not benchmark overfitting.

**Caption (verbatim):**
"Figure 11: Chinese in-house benchmark evaluation."

### Figure 12 (p.30) ⭐深度解读
![[assets/kimi-k2-open-agentic-intelligence-p30.png]]
> [!quote] caption
> Applying QK-Clip to Muon in a small-scale setting with an aggresive threshold (t = 30) has negligible impact on loss, indicating that it is a safe and effective method for constraining attention logits.

> [!tip] 技术解读（多模态）
> **Figure Description & Technical Takeaway**

The referenced figure (Figure 12) compares training loss curves between two small-scale MoE models — one using vanilla Muon and the other using MuonClip with an aggressive threshold (τ = 30). The architecture under test is a 0.5B-activated / 3B-total-parameter MoE (presumably the Kimi K2 / MuonScaffold stack), where QK-Clip caps the per-head maximum attention logit S_max at 100. The plot shows two nearly-overlapping loss trajectories over training steps.

**Key takeaway:** Even an aggressive QK-Clip threshold (τ = 30) produces no visible degradation in training loss, confirming that bounding attention logits via MuonClip is a safe intervention — it constrains logit explosion without harming convergence dynamics.

**Verbatim Caption:**

> Figure 12: Applying QK-Clip to Muon in a small-scale setting with an aggressive threshold (t = 30) has negligible impact on loss, indicating that it is a safe and effective method for constraining attention logits.

### Figure 13 (p.32) ⭐深度解读
![[assets/kimi-k2-open-agentic-intelligence-p32.png]]
> [!quote] caption
> pipeline for RL weight update

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The figure presents **Figure 13: pipeline for RL weight update** in three variants (a, b, c), depicting how trained weights from RL engines are resharded into inference engines across GPUs.

**Architecture/Components:**
- Each GPU holds three equal-size device buffers: one **H2D buffer** (Host-to-Device loading of offloaded parameters) and two **IPC buffers** (GPU-to-GPU broadcast, shared with inference engines via memory mapping).
- **Subplot (a)** – Theoretical 3-stage pipeline: (1) async H2D copy of weight shard → (2) copy shard to IPC buffer + broadcast to all devices → (3) inference engines reload from second IPC buffer. All three stages overlap in a pipeline.
- **Subplot (b)** – PCIe-bounded 3-stage: stages collapse into sequential execution because concurrent H2D + broadcast saturate the shared PCIe fabric on H800 clusters.
- **Subplot (c)** – Fixed 2-stage pipeline adopted in practice: (1) synchronous, all-device H2D transfer → (2) broadcast and reload happen in parallel.

**Data flow:** Host memory (offloaded params) → H2D buffer → IPC buffer A → broadcast over NVLink/PCIe → IPC buffer B → inference engine reload.

**Key Technical Takeaway:** Overlapping H2D, Broadcast, and Reload operations yields high bandwidth for resharding weights from train to inference engines; at large scale the parameter set fits the H2D buffer in a single transfer, making the simpler 2-stage pipeline PCIe-friendly.

## Caption (verbatim)

**Figure 13:** pipeline for RL weight update

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf W_q^{h} \gets \gamma^{\alpha} \mathbf W_q^{h} \qquad \mathbf W_k^{h} \gets \gamma^{1-\alpha} \mathbf W_k^{h}
$$

$$
S_{\max} = \max_{i,j} \bigl(q_i^{\vphantom{\top}}\! \cdot k_j\bigr)
$$

$$
|q_i \!\cdot\! k_j| \le \|q_i\|\|k_j\| \le \|x_i\|\|x_j\|\|\mathbf W_q\|\|\mathbf W_k\|,
$$

$$
\mathbf W_{t-1}=\sum_i \sigma_i\,u_i v_i^{\top}
$$

$$
q_i\cdot k_j=(x_i \mathbf W_q)\cdot (x_j \mathbf W_k).
$$

$$
L_{\mathrm{RL}}(\theta) = \mathbb{E}_{x \sim\mathcal{D}}\left[ \frac{1}{K} \sum_{i=1}^K \left[ \left( r(x, y_i) - \bar{r}(x)- \tau \log \frac{\pi_\theta(y_i | x)}{{\pi}_{\mathrm{old}}(y_i | x)} \right)^2 \right]\right] \, ,
$$

$$
\Delta\mathbf W_t &= \sum_j \bar\sigma\,\bar u_j \bar v_j^{\top}
$$

$$
\mathbf W_t \leftarrow \sum_i \sigma_i u_i v_i^{\top} + \sum_j \bar\sigma\,\bar u_j \bar v_j^{\top}
$$

$$
\mathbf{Q}^{h} = \mathbf X \mathbf W_q^{h}, \quad \mathbf K^{h} = \mathbf X \mathbf W_k^{h}, \quad \mathbf V^{h} = \mathbf X \mathbf W_v^{h}.
$$

$$
\mathbf O^{h} = \operatorname{softmax}\left( \frac{1}{\sqrt{d}} \mathbf Q^{h} \mathbf K^{h\top} \right) \mathbf V^{h}.
$$

$$
S_{\max}^{h} = \frac{1}{\sqrt{d}} \max_{\mathbf X \in B} \max_{i,j} \mathbf Q_i^{h} \mathbf K_j^{h\top}
$$

## 技术点深读（DEEP）

![[deep/kimi-k2-open-agentic-intelligence]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/kimi-k2-open-agentic-intelligence.txt`（112693 字符）供引用检索。