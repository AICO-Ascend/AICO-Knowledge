---
paper_num: "33"
title: "AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning"
authors: "Learning System for Language Reasoning Wei Fu12∗, Jiaxuan Gao1, Xujie Shen2, Chen Zhu2, Zhiyu Mei12, Chuyi He2, Shusheng Xu12, Guo Wei2, Jun Mei2, Jiashu Wang3, Tongkai Yang2, Binhang Yuan3, Yi Wu1 1 IIIS, Tsinghua Unive"
date: "2026/1/17"
arxiv: "https://arxiv.org/abs/2505.24298"
pdf: "papers/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning.pdf"
slug: "areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning"
tags: [rl]
---

# AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning

> [!abstract] 摘要（原文）
> 1\. 🏆 AReaL 提出了一个完全异步的强化学习系统，通过彻底解耦 LLM 的生成和训练过程，解决了同步 RL 系统在处理长推理任务时 GPU 利用率低和扩展性差的问题。 2. 🌟 为了在异步环境下保持 RL 训练的稳定性，AReaL 引入了对数据时效性的控制，并采用了一种解耦的 PPO 目标函数，使其能够有效利用来自不同策略版本的数据。 3. 🚀 实验结果表明，与同步系统相比，AReaL 在数学和代码推理基准测试中实现了高达 2.77 倍的训练加速，同时保持或提升了最终模型性能，并展示了良好的可扩展性。

## 元信息
- **发表日期**: 2026/1/17
- **作者**: Learning System for Language Reasoning Wei Fu12∗, Jiaxuan Gao1, Xujie Shen2, Chen Zhu2, Zhiyu Mei12, Chuyi He2, Shusheng Xu12, Guo Wei2, Jun Mei2, Jiashu Wang3, Tongkai Yang2, Binhang Yuan3, Yi Wu1 1 IIIS, Tsinghua Unive
- **arXiv**: https://arxiv.org/abs/2505.24298
- **本地 PDF**: `papers/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning.pdf`
- **页数**: 27

## 图表（原文 caption + 页码）

### Figure 1 (p.4) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig01.png]]
*整页渲染: ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]]*
> [!quote] caption
> Execution timeline of a synchronous (left) and a one-step overlap (right) RL system showing underutilized inference devices. … Rollout Controller Reward Service

> [!tip] 技术解读（多模态）
> **Figure 2 — AREAL Architecture**

**Components & Data Flow:** Two decoupled GPU clusters. The *Generation* side hosts multiple Interruptible Rollout Workers (GPU) that send prompts (green) and trajectories (blue) through a Rollout Coordinator to a Replay Buffer. A Reward Service (CPU) returns rewards via the coordinator. The Replay Buffer sends aggregated batches through a Replay Buffer to Trainer Workers (GPU, Training cluster), which feed a Parameter Service. The Parameter Service emits interrupt signals (red) and parameter save/load updates (purple) back to the rollout workers, closing the async loop.

**Key takeaway (≤120 words):** AREAL fully decouples generation and training across separate GPU clusters coordinated via a Replay Buffer and Parameter Service. Rollout workers are *interruptible*: upon receiving new weights they discard stale KV state and continue decoding—enabling continuous, weight-updated trajectory generation without waiting for synchronized training steps. This eliminates the GPU underutilization and memory-IO bottleneck of synchronous RL.

**Caption (verbatim):**
*"Figure 2: The AREAL architecture featuring asynchronous generation and training components."*

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig02.png]]
*整页渲染: ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]]*
> [!quote] caption
> The AREAL architecture featuring asynchronous generation and training components.

> [!tip] 技术解读（多模态）
> **Figure 2 — AREAL Architecture**

**Components & Data Flow:** Two decoupled GPU clusters. The *Generation* side hosts multiple Interruptible Rollout Workers (GPU) that send prompts (green) and trajectories (blue) through a Rollout Coordinator to a Replay Buffer. A Reward Service (CPU) returns rewards via the coordinator. The Replay Buffer sends aggregated batches through a Replay Buffer to Trainer Workers (GPU, Training cluster), which feed a Parameter Service. The Parameter Service emits interrupt signals (red) and parameter save/load updates (purple) back to the rollout workers, closing the async loop.

**Key takeaway (≤120 words):** AREAL fully decouples generation and training across separate GPU clusters coordinated via a Replay Buffer and Parameter Service. Rollout workers are *interruptible*: upon receiving new weights they discard stale KV state and continue decoding—enabling continuous, weight-updated trajectory generation without waiting for synchronized training steps. This eliminates the GPU underutilization and memory-IO bottleneck of synchronous RL.

**Caption (verbatim):**
*"Figure 2: The AREAL architecture featuring asynchronous generation and training components."*

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig03.png]]
*整页渲染: ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]]*
> [!quote] caption
> Illustration of generation management in AREAL. Vertical lines show the ready time for the next step training. Blue crosses show the interrupted requests when new parameters arrive. 4

> [!tip] 技术解读（多模态）
> **Figure 2 — AREAL Architecture**

**Components & Data Flow:** Two decoupled GPU clusters. The *Generation* side hosts multiple Interruptible Rollout Workers (GPU) that send prompts (green) and trajectories (blue) through a Rollout Coordinator to a Replay Buffer. A Reward Service (CPU) returns rewards via the coordinator. The Replay Buffer sends aggregated batches through a Replay Buffer to Trainer Workers (GPU, Training cluster), which feed a Parameter Service. The Parameter Service emits interrupt signals (red) and parameter save/load updates (purple) back to the rollout workers, closing the async loop.

**Key takeaway (≤120 words):** AREAL fully decouples generation and training across separate GPU clusters coordinated via a Replay Buffer and Parameter Service. Rollout workers are *interruptible*: upon receiving new weights they discard stale KV state and continue decoding—enabling continuous, weight-updated trajectory generation without waiting for synchronized training steps. This eliminates the GPU underutilization and memory-IO bottleneck of synchronous RL.

**Caption (verbatim):**
*"Figure 2: The AREAL architecture featuring asynchronous generation and training components."*

### Figure 4 (p.8) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig04.png]]
*整页渲染: ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p08.png]]*
> [!quote] caption
> The strong scaling trend. Dotted lines indicate ideal linear scaling. verl consistently encounters OOM with 32k context length and the 32B model so the data points are missing. 8

> [!tip] 技术解读（多模态）
> **Description of Figure 4 (Strong Scaling Trend):**

The figure is a 2×3 grid of line plots comparing training throughput across model size and context length. Rows distinguish context length (ctx=16384 top, ctx=32768 bottom); columns distinguish model size (1.5B, 7B, 32B left-to-right). The y-axis shows throughput in tokens/second; the x-axis shows the number of GPUs (ranging 32–512 depending on model size). Three series are plotted: AReaL (blue solid), verl (orange dashed), and ideal linear scaling (black dotted).

**Key Takeaway:** AReaL tracks the ideal linear scaling line closely across all six configurations, while verl falls progressively further below it as the number of GPUs grows — confirming AReaL's superior multi-node scaling efficiency for RL training.

**Caption (verbatim):**

Figure 4: The strong scaling trend. Dotted lines indicate ideal linear scaling. verl consistently encounters OOM with 32k context length and the 32B model so the data points are missing.

### Figure 5 (p.9) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig05.png]]
*整页渲染: ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p09.png]]*
> [!quote] caption
> Ablation studies of the decoupled PPO objective and staleness control with a 1.5B model on math reasoning tasks. Both algorithmic choices are essential. With a moderate staleness value and the decoupled objective, training progress can be accelerated by over 2× while maintaining final evaluation performance.

> [!tip] 技术解读（多模态）
> ## Figure 5 Description

**Components/Data flow:** Figure 5 is a three-panel ablation study on a 1.5B model for math reasoning. Panel (a) plots training-reward learning curves under naive PPO across MaxStaleness values {0, 1, 2, 4, 8, 16, ∞}; panel (b) reproduces the same experiment with the decoupled PPO objective (eq. 5), where curves cluster tightly near the oracle (η=0). Panel (c) is a horizontal bar chart of effective training throughput (k tokens/s) vs. MaxStaleness, rising monotonically from 128.7 (η=0) to 396.8 (η=∞).

**Key technical takeaway:** The decoupled PPO objective stabilizes training against stale data, enabling moderate staleness (η ≤ 8) to more than triple throughput (≈3.1×) with negligible loss in final accuracy, whereas naive PPO collapses as staleness grows.

## Caption (verbatim)

**Figure 5:** Ablation studies of the decoupled PPO objective and staleness control with a 1.5B model on math reasoning tasks. Both algorithmic choices are essential. With a moderate staleness value and the decoupled objective, training progress can be accelerated by over 2× while maintaining final evaluation performance.

### Figure 6 (p.10) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig06.png]]
*整页渲染: ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p10.png]]*
> [!quote] caption
> Ablation studies on system optimizations. experimental setup, we configured 32 micro-batches for the standard setting and established a token budget of 32,768 per micro-batch for the dynamic batching approach. As demonstrated in Figure 6a, dynamic batching yields an average of 30% throughput improvements across various model sizes.

> [!tip] 技术解读（多模态）
> **Figure description (≤120 words):**

Figure 6 presents two ablation bar charts rather than an architecture diagram. **Left (6a) — Dynamic vs. Normal Batching:** Compares throughput (TFLOPs/GPU) across model scales (1B/1 node, 7B/2 nodes, 32B/8 nodes). Dynamic batching consistently outperforms normal batching: 427.4 vs 404.4 (1B), 454.7 vs 303.1 (7B), and 387.7 vs 283.0 (32B), with the largest gap (~50%) at 7B. **Right (6b) — Interruptible Generation:** Compares average throughput (tokens/s) at 1.5B and 7B on 4 nodes. Interruptible generation yields 231k vs 207k (1.5B) and 130k vs 111k (7B). **Key takeaway:** Both optimizations are validated quantitatively—dynamic micro-batch allocation delivers ~30% throughput gains, and interruptible generation adds 12–17%, confirming their inclusion in the AREAL system design.

**Caption (verbatim):**

Figure 6: Ablation studies on system optimizations.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.8) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab01.png]]
> [!quote] caption
> End-to-End Performance Comparison. We evaluate on the AIME24 benchmark for math and LiveCodeBench (8/1/24-2/1/25) for coding. We limit the maximum generation length to 32K tokens and sample 32 responses per question, reporting the average pass@1 accuracy. * represents the best known reproducible res

> [!tip] 表格解读（多模态）
> **Description of the main figure (Table 1):**

The table compares end-to-end RL training performance across four model scales (1.5B, 7B, 14B, 32B) on AIME24 (math) and LiveCodeBench (coding). Each block reports: model variant (basemodel / VeRL / Sync.AReaL / AReaL), benchmark score (pass@1 avg), number of training nodes, PPO steps, and total training hours. The data flow implies rollout generation → advantage computation → PPO updates, with AReaL asynchronously overlapping generation and training.

**Key takeaway:** AReaL matches or exceeds VeRL/Sync.AReaL accuracy while cutting training hours roughly 2× (e.g., 1.5B: 14.8 vs 33.6 h; 7B: 25.4 vs 52.1 h; 14B: 21.9 vs 44.4 h).

**Caption (verbatim):**

Table 1: End-to-End Performance Comparison. We evaluate on the AIME24 benchmark for math and LiveCodeBench (8/1/24-2/1/25) for coding. We limit the maximum generation length to 32K tokens and sample 32 responses per question, reporting the average pass@1 accuracy. * represents the best known reproducible results obtained via RL, as cited from DeepScaler [25] and DeepCoder [24] respectively. AReaL achieves comparable performance with 2× fewer training hours.

### Table 2 (p.9) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab02.png]]
> [!quote] caption
> Evaluation scores when varying data staleness, comparing performance with and without the decoupled objective. Numbers within ± 1 of the oracle score are underlined.

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**

This is an evaluation **table**, not an architecture diagram. Its structure:
- **Rows:** "Max.Stale." — varying levels of data staleness during training (values cut off in the visible crop).
- **Columns:** four math benchmarks — **AIME24, AIME25, AMC23, MATH 500** — each split into two sub-columns: **W/o** (without decoupled objective) vs. **With** (with decoupled objective).
- **Cell content:** evaluation accuracy scores; values underlined are within ±1 of the oracle (upper-bound) score.

**Key takeaway:** The decoupled objective is being tested for robustness to stale/off-policy data across diverse math reasoning benchmarks, with the underline marker acting as a salience convention to flag near-oracle performance.

**Caption (verbatim):**

"Table 2: Evaluation scores when varying data staleness, comparing performance with and without the decoupled objective. Numbers within ±1 of the oracle score are underlined."

### Table 4 (p.25) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab04.png]]
> [!quote] caption
> Results on math benchmarks. Model AIME24 AIME25 AMC23 MATH 500

> [!tip] 表格解读（多模态）
> ## Description

**Components:** A benchmark comparison table evaluating two base model scales (1.5B and 7B) under three training regimes — *baseline*, *Sync. AReaL*, and *AReaL* — across four math reasoning benchmarks (AIME24, AIME25, AMC23, MATH 500).

**Data flow:** Rows group each model variant; columns report accuracy per benchmark. We compare relative deltas across rows to measure the effect of each RL recipe over the base model.

**Key takeaway:** AReaL training yields consistently larger gains on the smaller 1.5B model (e.g., AIME24 +12.9 pts) than the 7B model (+8.8 pts), with the asynchronous AReaL variant slightly outperforming the synchronous version on most benchmarks, especially harder ones like AIME.

## Caption (verbatim)

**Table 4: Results on math benchmarks.**

### Table 5 (p.26) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab05.png]]
> [!quote] caption
> Results on coding benchmarks. Model LiveCodeBench v5 Codeforces CodeContests

> [!tip] 表格解读（多模态）
> **Clarification:** The provided item is **Table 5** (a results table), not an architecture figure. It does not contain components, data-flow diagrams, or model architecture imagery, so an "architecture/data flow" description is not applicable. Below I describe the table's content and key takeaway, then transcribe the caption verbatim.

**Description of the table:** Table 5 compares six language-model variants against three coding benchmarks (LiveCodeBench v5, Codeforces rating/percentile, CodeContests score). Six rows are split into two parameter scales — **14B** and **32B** — each containing a *base model*, a synchronously-trained *Sync. AReaL* baseline, and the authors' proposed *AReaL* method. Numbers generally rise from base → Sync. AReaL → AReaL within each scale.

**Key takeaway:** The proposed AReaL method consistently outperforms its base model on all three benchmarks at both 14B and 32B scales (e.g., 14B base 53.4 → AReaL 58.1 on LiveCodeBench v5; 32B base 57.4 → AReaL 61.0), demonstrating effective reinforcement-learning-based coding improvement, while remaining roughly comparable to the synchronous AReaL baseline.

**Caption (verbatim):** *Table 5: Results on coding benchmarks.*

### Table 6 (p.26) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab06.png]]
> [!quote] caption
> Generalization results on DeepSeek-Distilled-Llama-8B across math benchmarks.

> [!tip] 表格解读（多模态）
> I'm unable to provide an architecture/components/data flow description because no figure is present in the input — only **Table 6** (a benchmark results table). I'll describe the table's structure, the key takeaway, and transcribe its caption verbatim.

**Table structure:**
- **Columns:** Model | AIME24 | AMC23 | MATH500 | AIME25
- **Rows:** Three model variants (one baseline + two fine-tuned).
- **Data:** Numeric accuracy scores (%) per benchmark.

**Key technical takeaway (≤120 words):**
AREAL fine-tuning consistently outperforms the DeepSeek-Distilled-Llama-8B baseline across all four math benchmarks. Gains are modest on well-saturated tests (AMC23: +8.1, MATH500: +3.1) but dramatic on harder, out-of-distribution benchmarks — most notably AIME25, where performance nearly doubles from **23.3 → 42.6** (+19.3 points, an ~83% relative improvement). The smaller exploration parameter (η=4) slightly edges out η=8 across every benchmark (e.g., AIME25: 42.6 vs. 41.6; AMC23: 92.3 vs. 91.5), suggesting lower exploration yields better generalization in this regime. Overall, AREAL delivers its largest absolute wins where reasoning difficulty is highest.

**Caption (verbatim):**
*Table 6: Generalization results on DeepSeek-Distilled-Llama-8B across math benchmarks.*

### Table 7 (p.26) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab07.png]]
> [!quote] caption
> Staleness-throughput trade-off on small-scale academic setup.

> [!tip] 表格解读（多模态）
> ## Description

The table presents a **staleness-throughput trade-off study** for AREAL fine-tuned 1.5B models. **Components shown:** (1) a baseline row (DeepSeek-Distilled-Qwen-1.5B), and (2) six AREAL Fine-Tuned rows sweeping the staleness hyperparameter η ∈ {0, 1, 2, 4, 8, 16}. **Metrics columns:** accuracy on four math-reasoning benchmarks (AIME24, AIME25, AMC23, MATH500) plus generation throughput (k tokens).

**Key takeaway:** Throughput nearly **doubles** as η grows (27.1k → 52.0k), while accuracy stays competitive (e.g., η=4 achieves 34.1 on AIME24 vs. 31.7 at η=0). This empirically validates that controlled staleness in asynchronous RL training buys substantial throughput with negligible—and occasionally positive—accuracy impact.

## Caption (verbatim)

**Table 7:** Staleness-throughput trade-off on small-scale academic setup.

### Table 8 (p.26) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab08.png]]
> [!quote] caption
> Staleness-throughput trade-off using RLOO algorithm. Model AIME24 AIME25 AMC23 MATH500 Throughput

> [!tip] 表格解读（多模态）
> **Description:**

Table 8 presents a structured performance comparison across mathematical reasoning benchmarks. The leftmost "Model" column lists a baseline (DeepSeek-Distilled-Qwen-1.5B) followed by six RLOO variants parameterized by staleness coefficient η ∈ {0, 1, 2, 4, 8, 16}. Four accuracy columns (AIME24, AIME25, AMC23, MATH500) report benchmark scores, while the rightmost "Throughput" column measures training token throughput (tokens/sec, scaled to thousands). Data flow progresses left-to-right: model configuration → accuracy metrics → efficiency metric.

**Key Takeaway (≤120 words):** Increasing the staleness coefficient η from 0 → 16 in asynchronous RLOO training nearly doubles throughput (27.1k → 52.0k, ~91% gain) while keeping accuracy largely stable—AIME24 fluctuates only within a narrow 31.5–34.1 band, and MATH500 stays flat near 87. This demonstrates a favorable staleness-throughput trade-off: permitting "stale" gradients in distributed RL fine-tuning substantially accelerates training at minimal cost to downstream reasoning performance, suggesting η≈2–8 offers a practical sweet spot.

**Caption (verbatim):**
Table 8: Staleness-throughput trade-off using RLOO algorithm.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\pibehav(\cdot|s) = \begin{cases} \pi_{\theta+j}(\cdot|s) & \text{if } t_j\leq t\leq t_{j+1} \text{ and } s\in \mathcal{S}_t(q) \\ \text{arbitrary} & \text{otherwise} \end{cases}
$$

$$
J(\theta)= \mathbb{E}_{q\sim\mathcal{D}, a_t\sim\pi_\theta\left(\cdot|q,a_{<t}\right)} \left[ \sum_{t=1}^H \gamma^{t-1}r(s_t,a_t) \right].
$$

$$
J_\mathrm{PPO}(\theta)= \mathbb{E}_{q\sim\mathcal{D}, a_t\sim\pi_{\mathrm{old}}\left(\cdot|q,a_{<t}\right)} \left[ \sum_{t=1}^H \min\left( u_t(\theta)\hat{A}(s_t,a_t),\mathrm{clip}\left(u_t(\theta),1-\epsilon,1+\epsilon\right)\hat{A}(s_t,a_t)\right) \right],
$$

$$
\lfloor (N_r-1) /B \rfloor \leq i + \eta.
$$

$$
J(\theta)&= \mathbb{E}_{q\sim\mathcal{D}, a_t\sim\pibehav} \left[ \sum_{t=1}^H \min( \underset {{\text{Importance Ratio}}} { \boxed{ \frac{\pi_\theta}{\pibehav} } } \hat{A}_t,\quad \overbrace{ \frac{\piprox}{\pibehav} \mathrm{clip}( \underset{\text{Trust Region Center}}{ \boxed{ \frac{\pi_\theta}{\piprox} } } ,1-\epsilon,1+\epsilon )\hat{A}_t }^\text{Importance Ratio} ) \right] \\ &= \mathbb{E}_{q\sim\mathcal{D}, a_t\sim\pibehav} \left[ \sum_{t=1}^H \frac{\piprox}{\pibehav} \min\left( u_t^\mathrm{prox}(\theta)\hat{A}_t, \mathrm{clip}\left( u_t^\mathrm{prox}(\theta),1-\epsilon,1+\epsilon \right)\hat{A}_t) \right) \right],
$$

## 相关论文

- [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] — Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning
- [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] — DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEMENT LEARNING
- [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] — Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning
- [[hybridflow-a-flexible-and-efficient-rlhf-framework]] — HybridFlow: A Flexible and Efficient RLHF Framework

## 技术点深读（DEEP）

![[deep/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning.txt`（88470 字符）供引用检索。