---
paper_num: "25"
title: "Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning"
authors: "Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning Bowen Jin1, Hansi Zeng2, Zhenrui Yue1, Jinsung Yoon3, Sercan ¨O. Arık3, Dong Wang1, Hamed Zamani2, Jiawei Han1 1 Department of Co"
date: "—"
arxiv: "https://arxiv.org/abs/2503.09516"
pdf: "papers/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning.pdf"
slug: "search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning"
tags: [training, rl]
---

# Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning

> [!abstract] 摘要（原文）
> 1\. 💡 SEARCH-R1 提出了一种新颖的强化学习 (RL) 框架，使大型语言模型 (LLMs) 能够学习自主生成搜索查询，并将推理与实时检索交错进行，以有效获取外部知识。 2. ⚙️ 该框架将搜索引擎建模为 RL 环境的一部分，通过检索令牌掩蔽 (retrieved token masking) 确保训练稳定性，并支持多轮推理与检索交互，使用 \<search>、\<information> 和 \<think> 等特定令牌进行结构化决策。 3. 📈 在七个问答数据集上的实验表明，SEARCH-R1 在相同设置下比 RAG 基线表现出显著的性能提升，并提供了关于 RL 优化方法、LLM 选择及响应长度动力学的宝贵见解。

## 元信息
- **发表日期**: —
- **作者**: Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning Bowen Jin1, Hansi Zeng2, Zhenrui Yue1, Jinsung Yoon3, Sercan ¨O. Arık3, Dong Wang1, Hamed Zamani2, Jiawei Han1 1 Department of Co
- **arXiv**: https://arxiv.org/abs/2503.09516
- **本地 PDF**: `papers/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning.pdf`
- **页数**: 31

## 图表（原文 caption + 页码）

### Figure 1 (p.4) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig01.png]]
*整页渲染: ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p04.png]]*
> [!quote] caption
> Demonstration of PPO and GRPO training with the search engine (SEARCH-R1).

> [!tip] 技术解读（多模态）
> **Figure 1 — Architecture / Components / Data Flow**

Two parallel pipelines (top: PPO; bottom: GRPO) start with query *q* entering a **Rollout Module** that couples a trained **Policy LLM** (yellow) with a **Search Engine** (blue), enabling multi-turn retrieval-and-reasoning. Rollout output(s) *o* are scored by frozen **Reward** and **Reference LLMs** (green) producing reward *r*. In PPO, a trained **Value LLM** also produces *v*; (*v*, *r*) feeds **GAE** → per-token advantage *A*. GRPO skips the value model: it samples *G* rollouts (*o₁…o_G*), scores each (*r₁…r_G*), and uses **Group Computation** to derive group-relative advantages (*A₁…A_G*), with a KL constraint (vs. reference) back to the policy.

**Key takeaway:** Unlike prior RL that rollout solely from π_θ(·|x), this framework makes the policy explicitly retrieval-aware via π_θ(·|x;ℛ), and uses **loss masking** so gradients update only LLM-generated tokens, not retrieved content — stabilizing training while preserving search-augmented reasoning.

**Caption (verbatim):** "Figure 1: Demonstration of PPO and GRPO training with the search engine (SEARCH-R1). During the rollout, LLMs can conduct multi-turn interactions with the search engine."

### Figure 2 (p.9) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig02.png]]
*整页渲染: ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p09.png]]*
> [!quote] caption
> (a) PPO vs. GRPO: GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO provides more stable optimization but converges at a slower rate. (b) Base vs. Instruct LLM study: Instruction-tuned LLMs converge faster, but the final performance of both modles remains highly similar. (c)

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 2):**

The figure presents four training-dynamics subplots for Search-R1 (a reinforcement-learning framework combining LLM reasoning with search engine retrieval):

- **(a) PPO vs. GRPO**: Compares two RL algorithms on Train Reward vs. Step curves (0–500 steps). GRPO (orange) converges faster but shows instability spikes, while PPO (blue) converges more slowly yet stably.
- **(b) Base vs. Instruct**: Compares Qwen2.5 base vs. instruction-tuned LLMs over 0–200 steps. Instruct (orange) starts higher and rises faster; Base (blue) climbs more slowly but converges to similar reward (~0.40).
- **(c) Response Length**: Dual-axis plot showing Response Length (blue, 900–1150 tokens) and Train Reward (red) over 0–200 steps. Length decreases initially, then increases alongside reward.
- **(d) # Valid Search**: Dual-axis plot tracking valid search-call count (blue, ~1.4–2.0) and reward (red) over steps — both grow together as training proceeds.

**Key Technical Takeaway:** Search-R1 exhibits a two-phase learning dynamic — early-stage response compression followed by reward-driven expansion through increased retrieval calls — and retrieved-token loss masking yields consistently superior QA performance (NQ 0.480 vs. 0.388; avg. 0.431 vs. 0.343).

**Verbatim Caption:**

"Figure 2: (a) PPO vs. GRPO: GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO provides more stable optimization but converges at a slower rate. (b) Base vs. Instruct LLM study: Instruction-tuned LLMs converge faster, but the final performance of both modles remains highly similar. (c) Response length study: The response length exhibits a decrease-increase-stabilize trend throughout training, aligning with the overall performance trajectory of the LLM. (d) # Valid search study: As the training proceeds, the LLM learns to call search more."

### Figure 3 (p.17) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig03.png]]
*整页渲染: ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]]*
> [!quote] caption
> Retrieved Token Loss Masking Study instruction-tuned models exhibit faster convergence and benefit from higher initial perfor- mance relative to their base counterparts. Despite this early advantage, the final performance of both model types converges to a similar level after training. These results indicate that while instruction tuning facilitates more efficient early-stage learning in reasoning

> [!tip] 技术解读（多模态）
> **Figure 3 — Retrieved Token Loss Masking Study**

The figure presents two side-by-side line plots comparing training reward trajectories across RL steps. Each subplot shows two curves: "w. mask" (blue, with error bars) versus "w.o. mask" (orange, with error bars). Subplot (a) tracks Qwen-2.5-3b-base over ~400 steps with reward range 0.0–0.4; subplot (b) tracks Qwen-2.5-7b-base over ~250 steps with reward 0.10–0.50. Both curves rise together initially, but the unmasked (orange) curve collapses to near-zero reward at the end of training in both models, while the masked (blue) curve remains stable.

**Key takeaway:** Masking the loss on retrieved tokens is essential — without it, training reward collapses late in optimization, whereas masking preserves stable convergence across model scales.

**Caption (verbatim):** "Figure 3: Retrieved Token Loss Masking Study"

### Figure 4 (p.17) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig04.png]]
*整页渲染: ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]]*
> [!quote] caption
> Study of SEARCH-R1 on base and instruct LLMs. The instruction model converges faster and starts from a better initial performance. However, the final performance of both models is very similar. F

> [!tip] 技术解读（多模态）
> **Figure 3 — Retrieved Token Loss Masking Study**

The figure presents two side-by-side line plots comparing training reward trajectories across RL steps. Each subplot shows two curves: "w. mask" (blue, with error bars) versus "w.o. mask" (orange, with error bars). Subplot (a) tracks Qwen-2.5-3b-base over ~400 steps with reward range 0.0–0.4; subplot (b) tracks Qwen-2.5-7b-base over ~250 steps with reward 0.10–0.50. Both curves rise together initially, but the unmasked (orange) curve collapses to near-zero reward at the end of training in both models, while the masked (blue) curve remains stable.

**Key takeaway:** Masking the loss on retrieved tokens is essential — without it, training reward collapses late in optimization, whereas masking preserves stable convergence across model scales.

**Caption (verbatim):** "Figure 3: Retrieved Token Loss Masking Study"

### Figure 5 (p.18) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig05.png]]
*整页渲染: ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p18.png]]*
> [!quote] caption
> Training dynamics of SEARCH-R1 with PPO and GRPO as the base RL method across four LLMs. GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO provides more stable optimization but converges at a slower rate. PPO and GRPO achieve comparable final reward performance. G

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 5):**

**Architecture/Components:** Four-panel grid of training-reward line plots (x = Step, y = Train Reward), each comparing two RL methods—**PPO** (blue) vs. **GRPO** (orange)—across four LLMs: (a) Qwen2.5-3b-base, (b) Qwen2.5-3b-it, (c) Qwen2.5-7b-base, (d) Qwen2.5-7b-it. Steps range 0–500 for base models and 0–300 for instruction-tuned variants; reward ranges ~0.1–0.5.

**Data flow:** Training-step progression → policy updates via PPO (with critic/value function) vs. GRPO (critic-free, group-relative) → logged reward trajectories.

**Key takeaway (≤120 words):** GRPO climbs faster but suffers *reward collapse* mid-training in every panel, dropping sharply before partially recovering. PPO rises more slowly yet stays monotonically stable. Both converge to comparable terminal rewards (~0.35–0.45), demonstrating that PPO's stability comes at the cost of sample efficiency, while GRPO trades reliability for faster early progress—an important consideration when selecting an RL backbone for Search-R1.

**Caption (verbatim):**
"Figure 5: Training dynamics of SEARCH-R1 with PPO and GRPO as the base RL method across four LLMs. GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO provides more stable optimization but converges at a slower rate. PPO and GRPO achieve comparable final reward performance."

### Figure 6 (p.19) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig06.png]]
*整页渲染: ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]]*
> [!quote] caption
> The training dynamics of SEARCH-R1 with a different number of retrieved pas- sages. (LLM: Qwen2.5-7b-base, RL: PPO)

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Figure 6** plots **training reward (y-axis, 0.1–0.5) vs. optimization step (x-axis, 0–500)** for the SEARCH-R1 pipeline (LLM: Qwen2.5-7b-base, RL: PPO). Three curves compare retrieval depths — `topk=1` (blue), `topk=3` (orange), `topk=5` (green). All settings start near 0.1, rise steeply until ~step 200, and plateau around 0.45–0.5 with mild oscillation.

**Key takeaway:** Retrieval depth (1 vs. 3 vs. 5 passages) yields nearly identical reward trajectories, suggesting top-k is not the dominant driver of PPO convergence in SEARCH-R1 — corroborated by Table 7, where topk=3 modestly wins on average (0.431) over topk=1 (0.375) and topk=5 (0.400).

---

## Caption (verbatim)

**Figure 6:** The training dynamics of SEARCH-R1 with a different number of retrieved passages. (LLM: Qwen2.5-7b-base, RL: PPO)

**Figure 7:** The training dynamics of SEARCH-R1 (GRPO) with different group size. (LLM: Qwen2.5-7b-base)

### Figure 7 (p.19) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig07.png]]
*整页渲染: ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]]*
> [!quote] caption
> We observe that a larger group size generally leads to faster convergence but may also increase the risk of collapse due to the inherent instability of reinforcement learning.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Figure 6** plots **training reward (y-axis, 0.1–0.5) vs. optimization step (x-axis, 0–500)** for the SEARCH-R1 pipeline (LLM: Qwen2.5-7b-base, RL: PPO). Three curves compare retrieval depths — `topk=1` (blue), `topk=3` (orange), `topk=5` (green). All settings start near 0.1, rise steeply until ~step 200, and plateau around 0.45–0.5 with mild oscillation.

**Key takeaway:** Retrieval depth (1 vs. 3 vs. 5 passages) yields nearly identical reward trajectories, suggesting top-k is not the dominant driver of PPO convergence in SEARCH-R1 — corroborated by Table 7, where topk=3 modestly wins on average (0.431) over topk=1 (0.375) and topk=5 (0.400).

---

## Caption (verbatim)

**Figure 6:** The training dynamics of SEARCH-R1 with a different number of retrieved passages. (LLM: Qwen2.5-7b-base, RL: PPO)

**Figure 7:** The training dynamics of SEARCH-R1 (GRPO) with different group size. (LLM: Qwen2.5-7b-base)

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab01.png]]
> [!quote] caption
> Template for S EARCH -R1. question will be replaced with the specific question during training and inference.

> [!tip] 表格解读（多模态）
> The figure presents Table 1, which defines the **prompt template** used in the SEARCH-R1 framework rather than a system architecture diagram. Its key component is a single template string where the token "question" (highlighted in red) serves as a placeholder slot. During training and inference, this placeholder is dynamically substituted with the actual user query, providing the language model with a standardized structure that integrates search/retrieval interaction instructions.

**Key takeaway:** SEARCH-R1 separates prompt structure from query content via template-based token substitution, enabling consistent retrieval-augmented reasoning across diverse inputs without manual prompt engineering per example.

**Caption (verbatim):**
Table 1: Template for SEARCH-R1. question will be replaced with the specific question during training and inference.

### Table 2 (p.8) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab02.png]]
> [!quote] caption
> Main results. The best performance is set in bold. † / ⋆ represents in-domain/out- domain datasets.

> [!tip] 表格解读（多模态）
> **Note:** The provided image is a **table** (Table 2), not a figure depicting architecture/components/data flow. I will describe it accordingly.

**Description:** Table 2 presents a benchmark comparison of QA methods across eight retrieval-augmented QA datasets, organized into two task categories. The "General QA" group contains four datasets (NQ†, TriviaQA*, PopQA*, HotpotQA†), while the "Multi-Hop QA" group contains four datasets (2wiki*, Musique*, Bamboogle*, HotQA*). An "Avg." column aggregates performance across benchmarks. Daggers (†) mark in-domain datasets; asterisks (*) mark out-of-domain datasets, and best results are bolded. The visible content shows only the header rows — the data rows and methods list are truncated/not rendered.

**Key technical takeaway:** The table evaluates cross-domain generalization, separately reporting single-hop and multi-hop QA accuracy to expose where methods transfer well versus where they break down on out-of-domain data.

**Caption (verbatim):**
> Table 2: Main results. The best performance is set in bold. †/∗ represents in-domain/out-domain datasets.

### Table 3 (p.8) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab03.png]]
> [!quote] caption
> The performance results of S EARCH -R1 with PPO and GRPO on seven datasets.

> [!tip] 表格解读（多模态）
> **Note:** The image shows a results table, not an architecture figure, so I describe its structure instead.

**Description:** Table 3 is a performance comparison matrix organizing results by model family (Qwen2.5-7b vs. Qwen2.5-3b), training algorithm (GRPO vs. PPO), and model variant (base vs. instruct), evaluated across seven QA datasets (NQ, TriviaQA, PopQA, HotpotQA, 2wiki, Musique, Bambooole) plus an average column. Rows are grouped by base/instruct pairs separated by dashed lines, with the best score per dataset bolded. **Key takeaway:** PPO generally outperforms GRPO on the 7B base model (avg 0.431 vs. 0.350), while GRPO is more competitive on the 3B instruct variant—suggesting the optimal RL algorithm is scale- and instruction-dependent.

**Caption (verbatim):**
"Table 3: The performance results of SEARCH-R1 with PPO and GRPO on seven datasets."

### Table 4 (p.9) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab04.png]]
> [!quote] caption
> The performance of S EARCH -R1 with and without retrieved token loss masking. The LLM trained with retrieved token loss masking achieves consistently better performance. (LLM: Qwen2.5-7b-base; RL: PPO)

> [!tip] 表格解读（多模态）
> **Description:**

Table 4 is an ablation comparison of SEARCH-R1 trained with versus without retrieved token loss masking, evaluated across seven QA benchmarks (NQ, TriviaQA, PopQA, HotpotQA, 2wiki, Musique, Bamboogle) plus an average column. The base model is Qwen2.5-7b-base optimized with PPO. Values are bolded for the masked variant.

**Key takeaway:** Masking loss on retrieved tokens prevents the LLM from being trained to directly mimic or copy retrieved passages, instead letting it focus learning on its own generated reasoning tokens — yielding ~4.4–12.8 point absolute gains across every dataset and lifting average performance from 0.343 to 0.431.

**Verbatim caption:**

> Table 4: The performance of SEARCH-R1 with and without retrieved token loss masking. The LLM trained with retrieved token loss masking achieves consistently better performance. (LLM: Qwen2.5-7b-base; RL: PPO)

### Table 5 (p.17) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab05.png]]
> [!quote] caption
> Main results. The best performance is set in bold. † / ⋆ represents in-domain/out- domain datasets.

> [!tip] 表格解读（多模态）
> **Description**

The image displays a results comparison table (Table 5) rather than an architectural figure. Its structure consists of:

- **Rows (Methods):** Reserved for comparing different QA models/approaches (the row entries themselves are not visible in the cropped view).
- **Columns (Evaluation Benchmarks):** Split into two thematic groups:
  - *General QA:* NQ†, TriviaQA*, PopQA*
  - *Multi-Hop QA:* HotpotQA†, 2wiki*, Musique*, Bamboogle*
  - Plus a final **Avg.** column for overall performance aggregation.
- **Notation convention:** † marks in-domain datasets; * marks out-of-domain datasets; best result per column is bolded.

No data flow or neural architecture components are depicted — only the benchmark grid.

**Key technical takeaway:** The evaluation deliberately stresses generalization by pairing in-domain (NQ, HotpotQA) with out-of-domain (TriviaQA, PopQA, 2wiki, Musique, Bamboogle) QA benchmarks, and averages across both single-hop and multi-hop reasoning tasks.

**Caption (verbatim):**
> Table 5: Main results. The best performance is set in bold. †/* represents in-domain/out-domain datasets.

### Table 6 (p.18) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab06.png]]
> [!quote] caption
> The performance of S EARCH -R1 with and without retrieved token loss masking. The LLM trained with retrieved token loss masking achieves consistently better performance. (RL: PPO)

> [!tip] 表格解读（多模态）
> **Main Figure (Figure 5, partial view):**

The visible portion shows four scatter/trajectory panels tracking a reward metric ("rd", y-axis ~0.4–0.5) over training steps. Per the surrounding text, these plots compare PPO (blue) vs. GRPO (orange) curves during Search-R1 optimization.

**Components/inferred data flow:**
- **PPO branch**: policy network + separate value (critic) function → policy updates with warm-up
- **GRPO branch**: group-relative baseline → critic-free policy updates
- Both feed reward signals from retrieved-token-masked SEARCH-R1 rollouts

**Key technical takeaway:**
PPO avoids the reward collapse that GRPO exhibits over extended training, yielding more stable policy updates; both methods ultimately reach comparable final reward performance, traded off against PPO's extra critic overhead and warm-up requirement.

**Caption transcribed verbatim:**

*"Table 6: The performance of SEARCH-R1 with and without retrieved token loss masking. The LLM trained with retrieved token loss masking achieves consistently better performance. (RL: PPO)"*

### Table 7 (p.19) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab07.png]]
> [!quote] caption
> The number of retrieved passages study in S EARCH -R1 training. (LLM: Qwen2.5- 7b-base; RL: PPO)

> [!tip] 表格解读（多模态）
> **Description of the Main Table/Figure:**

Table 7 presents an ablation study on the number of retrieved passages (top-k) during SEARCH-R1 training using PPO reinforcement learning with Qwen2.5-7b-base. It compares three configurations—topk=1, topk=3, and topk=5—across seven QA benchmarks (NQ, TriviaQA, PopQA, HotpotQA, 2wiki, Musique, Bamboogle) plus an average column. Results show scores ranging from 0.146 (size=1 on Musique) up to 0.638 (size=3 on TriviaQA), with the average column values being 0.375, 0.431, and 0.400 respectively.

**Key Technical Takeaway:**

topk=3 achieves the best average performance (0.431), outperforming both topk=1 (0.375) and topk=5 (0.400), suggesting that a moderate number of retrieved passages provides an optimal balance—enough context for multi-hop reasoning but not so much that noise from irrelevant passages degrades the model's learning signal during RL fine-tuning.

**Caption (Verbatim):**

Table 7: The number of retrieved passages study in SEARCH-R1 training. (LLM: Qwen2.5-7b-base; RL: PPO)

### Table 8 (p.20) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab08.png]]
> [!quote] caption
> The group size study of S EARCH -R1 (GRPO) on seven datasets. (LLM: Qwen2.5-7b- base)

> [!tip] 表格解读（多模态）
> **Description of the Main Figure (Table 8)**

This table presents an ablation study on the **group size hyperparameter** used in GRPO (Group Relative Policy Optimization) training within the SEARCH-R1 framework, evaluated across seven question-answering benchmarks (NQ, TriviaQA, PopQA, HotpotQA, 2wiki, Musique, Bamboogle) plus an average column. The LLM backbone is Qwen2.5-7b-base. Three configurations are compared: size=1 (no grouping baseline), size=3, and size=5.

**Key Technical Takeaway**

Counterintuitively, **smaller group size (size=1) yields the best average performance (0.410)**, while increasing group size to 3 and 5 monotonically degrades average scores (0.363 and 0.350). Larger groups also hurt most benchmarks—except Bamboogle, where size=3 is best (0.400, bold). This suggests that for retrieval-augmented GRPO, frequent policy updates with minimal rollouts per batch are more effective than broader relative comparisons.

**Caption (Verbatim)**

> Table 8: The group size study of SEARCH-R1 (GRPO) on seven datasets. (LLM: Qwen2.5-7b-base)

### Table 9 (p.20) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab09.png]]
> [!quote] caption
> A case study of R1 and S EARCH -R1.

> [!tip] 表格解读（多模态）
> **Description:** The figure presents a side-by-side comparison of two models answering the multi-hop question "Curious is a women's fragrance by a singer born in what city and state?" (ground truth: McComb, Mississippi). **R1** attempts the query in a single parametric pass, producing a confident but hallucinated answer ("Houston"). **Search-R1** instead drives an iterative loop of `<think>` → `<search>` → `<information>` tags, emitting three sequential queries ("Curious fragrance information," "Britney Spears birthplace," "McComb, Mississippi location") that retrieve supporting passages and converge on the correct answer. **Key takeaway:** Interleaving chain-of-thought reasoning with explicit retrieval actions lets Search-R1 decompose multi-hop questions, ground each step in external evidence, and correct hallucinations that closed-book models make.

**Caption (verbatim):** Table 9: A case study of R1 and SEARCH-R1.

### Table 10 (p.22) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab10.png]]
> [!quote] caption
> S EARCH -R1 case study 1 (successful): S EARCH -R1 conduct multi-step reasoning, search, with self-verification and finally answer the question.

> [!tip] 表格解读（多模态）
> **Figure Description:**

The figure presents an annotated trace of a SEARCH-R1 execution answering "What type of profession does Chris Jericho and Gary Barlow have in common?" The architecture uses four tag-based primitives that compose a ReAct-style loop: **<think>** (internal reasoning/state update), **<search>** (issues a query), **<information>** (retrieved document payload), and **<answer>** (terminal output). The data flow alternates reasoning with retrieval: each <think> block plans the next query, <search> emits it, and <information> returns context that feeds back into another <think>. The agent iteratively queries each entity, accumulates profession sets, then performs a cross-entity verification step before emitting the final answer "musician."

**Key takeaway:** SEARCH-R1 interleaves explicit reasoning tokens with retrieved evidence, enabling self-verification across multiple retrieval steps rather than relying on a single-shot lookup.

**Caption (verbatim):**
Table 10: SEARCH-R1 case study 1 (successful): SEARCH-R1 conduct multi-step reasoning, search, with self-verification and finally answer the question.

### Table 11 (p.23) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab11.png]]
> [!quote] caption
> S EARCH -R1 case study 2 (failed): S EARCH -R1 sometimes fail to decompose the complex problem and can be mislead by irrelevent searched passages.

> [!tip] 表格解读（多模态）
> **Architecture/Components & Data Flow:**
The table presents a SEARCH-R1 case study structured as a Q&A trace:
- **Question** (multi-hop retrieval query about Weezer's debut album)
- **Ground Truth** (reference answer: "The Blue Album")
- **SEARCH-R1 Agent Trace** — a sequence of structured tokens:
  - `<think>` reasoning step articulating intent
  - `<search>` query issued to retriever
  - `<information>` retrieved document (Doc 1) containing the correct answer
  - `<think>` second reasoning step that *paraphrases* the retrieved content
  - `<answer>` final output ("Weezer")

**Key Takeaway:** Despite retrieving a passage containing the correct span, the model failed at answer *extraction*, copying an entity from the question ("Weezer") instead of selecting the album title — illustrating that retrieval success does not guarantee grounded answer generation.

**Caption (verbatim):**
Table 11: SEARCH-R1 case study 2 (failed): SEARCH-R1 sometimes fail to decompose the complex problem and can be mislead by irrelevant searched passages.

### Table 12 (p.23) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab12.png]]
> [!quote] caption
> S EARCH -R1 case study 3 (successful): S EARCH -R1 can easily answer the question if the relevant information can be found with one search engine call.

> [!tip] 表格解读（多模态）
> **Architecture & Data Flow**

This isn't a traditional schematic diagram but rather a step-by-step execution trace of SEARCH-R1 (an LLM-based reasoning + retrieval agent) solving a single QA task. The components visible are: (1) `<think>` blocks where the model plans its reasoning, (2) `<search>` tags that issue a query to an external search engine, (3) `<information>` tags returning retrieved web documents (here "Doc 3: Ronald Ryan"), and (4) a final `<think>` → `<answer>` chain producing "Ronald Ryan," matching the ground truth.

Data flow: Question → reasoning → query → retrieval → injected evidence → reasoning → answer.

**Key Technical Takeaway**
A single search call retrieving the right document was sufficient—the model grounded its answer directly from injected web content without needing multi-hop retrieval.

---

**Verbatim Caption:**
"Table 12: SEARCH-R1 case study 3 (successful): SEARCH-R1 can easily answer the question if the relevant information can be found with one search engine call."

### Table 13 (p.24) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab13.png]]
> [!quote] caption
> S EARCH -R1 case study 4 (successful): S EARCH -R1 can write the right query to search for auxiliary information not provided in the previous search engine calls.

> [!tip] 表格解读（多模态）
> ## Main Figure Description

This case study illustrates the **SEARCH-R1 agent's reasoning-and-search loop** through a structured trace.

**Components / Data Flow:**
- **Question** (multi-entity query) → **`<think>`** (plan internal reasoning) → **`<search>`** (issue web query) → **`<information>`** (retrieve document) → loop continues → **`<answer>`** (final output).
- Two parallel iterative cycles: one for *Garajonay National Park*, another for *Teide National Park*, each emitting its own think/search/information triple.
- The model's `<think>` blocks adaptively refocus between cycles (e.g., "Now I need to find the location of Teide National Park"), driving precise, decomposable query generation.

**Key takeaway:** SEARCH-R1 autonomously *decomposes* compound questions and *formulates tailored queries* for each missing entity, rather than relying on a single broad search.

**Caption (verbatim):**
"Table 13: SEARCH-R1 case study 4 (successful): SEARCH-R1 can write the right query to search for auxiliary information not provided in the previous search engine calls."

### Table 14 (p.25) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab14.png]]
> [!quote] caption
> S EARCH -R1 case study 5 (failed): S EARCH -R1 fails to answer the question with insufficient or misleading retrieved information.

> [!tip] 表格解读（多模态）
> ## Description of the Main Figure

The figure is not a traditional architecture diagram but a **trace table** illustrating the Search-R1 agent's execution flow on a failed case. It shows an iterative **think → search → information** loop:

- **Components:** (1) a Question + Ground Truth header, (2) `<think>` reasoning steps, (3) `<search>` query tags, (4) `<information>` retrieved document blocks (Doc 1 / Doc 2), and (5) a final `<answer>` tag.
- **Data flow:** question → reasoning plan → query → retrieved passages → updated reasoning → refined query → retrieved passages (repeated) → final answer.
- **Key takeaway:** Despite multi-hop reasoning, the agent hallucinates "Sam Peckinpah" because the retriever returns off-topic documents (a Steve Cochran bio, a Sam Peckinpah bio) that never confirm a shared film, exposing Search-R1's sensitivity to misleading retrieval. (119 words)

## Caption (verbatim)

Table 14: SEARCH-R1 case study 5 (failed): SEARCH-R1 fails to answer the question with insufficient or misleading retrieved information.

### Table 15 (p.26) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab15.png]]
> [!quote] caption
> S EARCH -R1 case study 6 (successful): S EARCH -R1 can easily answer the question with multi-hop reasoning when sufficient and accurate context is retrieved.

> [!tip] 表格解读（多模态）
> **Description (architecture/components/data flow):**

The figure illustrates a two-hop iterative retrieval-reasoning loop executed by SEARCH-R1. The pipeline cycles through four repeating units enclosed in XML-style tags:

1. `<think>` — the agent reasons about the next sub-goal (e.g., "find the distributing company").
2. `<search>` — issues a query string to a retriever.
3. `<information>` — retrieved document(s) are injected back into the prompt.
4. `<think>` → `<search>` → `<information>` repeats for the second hop ("Empire Distribution location"), resolving the entity to its headquarters.
5. `<answer>` emits the final span.

**Key takeaway:** Structured *think-search* interleaving with explicit retrieved-context insertion lets the model decompose multi-hop questions into verifiable sub-queries, succeeding when retrieval returns accurate supporting docs.

**Caption (verbatim):**

Table 15: SEARCH-R1 case study 6 (successful): SEARCH-R1 can easily answer the question with multi-hop reasoning when sufficient and accurate context is retrieved.

### Table 16 (p.27) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab16.png]]
> [!quote] caption
> S EARCH -R1 case study 7 (failed): S EARCH -R1 failed to write the right queries to decompose a complex problem at the beginning. The model answer the question without obtaining enough evidence.

> [!tip] 表格解读（多模态）
> **Architecture/Components/Data Flow:**
The figure depicts a multi-turn retrieval-augmented reasoning loop executed by the SEARCH-R1 agent. Each turn follows a tagged pipeline: `<think>` (intermediate reasoning about the next query), `<search>` (emitted query string sent to a retrieval module), and `<information>` (the top-k retrieved document snippets returned to the agent). This three-stage loop (Think → Search → Information) iterates, accumulating evidence in context, until the model emits an `<answer>` tag with its final prediction. In this trace the same broad query is issued twice with no decomposition, so only generic document passages return and the loop terminates with a guessed answer.

**Key takeaway:** Successful retrieval hinges on early query decomposition; without splitting a multi-hop question into targeted sub-queries, the agent re-retrieves redundant evidence and answers from insufficient context.

**Caption (verbatim):**
"Table 16: Search-R1 case study 7 (failed): Search-R1 failed to write the right queries to decompose a complex problem at the beginning. The model answer the question without obtaining enough evidence."

### Table 17 (p.28) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab17.png]]
> [!quote] caption
> S EARCH -R1 case study 8 (successful): S EARCH -R1 can write query to search for insufficient information.

> [!tip] 表格解读（多模态）
> **Description (≈95 words):**

The figure is not an architectural diagram but a **trace table** (Table 17) showing one execution of the SEARCH-R1 agent on a two-hop comparison QA task. Structure: **Question / Ground Truth** rows on top, followed by a sequential transcript of agent turns. Each turn is tagged with one of three semantic roles — `<think>` (internal reasoning/planning), `<search>…</search>` (issued query), and `<information> Doc… </information>` (retrieved evidence) — shown with color-coded labels. Data flow loops: **think → search → information → think → … → answer**. Two iterative search-think cycles are visible before the final `<answer>` tag.

**Key takeaway:** SEARCH-R1 interleaves reasoning with retrieval, issuing *multiple targeted queries* to disambiguate each candidate independently — verifying both options before answering.

**Caption (verbatim):** "Table 17: SEARCH-R1 case study 8 (successful): SEARCH-R1 can write query to search for insufficient information."

### Table 18 (p.29) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab18.png]]
> [!quote] caption
> S EARCH -R1 case study 9 (successful): The first query written by the LLM is not very meaningful. However, upon that, LLM starts to write the query and solve the problem step by step.

> [!tip] 表格解读（多模态）
> **Architecture / Data Flow**

SEARCH-R1 is an LLM-based agent that solves multi-hop questions through an iterative **Think → Search → Retrieve → Think** loop. Each cycle: (1) the model reflects in `<think>` blocks, (2) emits a `<search>` query to an external retriever, (3) ingests the retrieved `<information>` documents, and (4) repeats until it converges on an `<answer>`. State is preserved across steps via the growing prompt context.

**Key technical takeaway:** Query quality improves across iterations—the first query ("Jed Hoyer or John William Henry II") is weak, but subsequent queries (e.g., "Jed Hoyer birth year") become more targeted, enabling step-by-step evidence gathering for multi-hop reasoning.

---

**Caption (verbatim):**

Table 18: SEARCH-R1 case study 9 (successful): The first query written by the LLM is not very meaningful. However, upon that, LLM starts to write the query and solve the problem step by step.

### Table 19 (p.30) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab19.png]]
> [!quote] caption
> S EARCH -R1 case study 10 (successful): S EARCH -R1 learns to stop searching when it finds out the external knowledge source is not sufficient to answer the question.

> [!tip] 表格解读（多模态）
> **Description:**

This table presents an iterative retrieval-then-reasoning trace from SEARCH-R1, not a diagram with explicit architecture. The data flow consists of a repeating cycle of three colored components:

- **`<think>` blocks (blue)** — internal reasoning that assesses whether retrieved evidence answers the question and decides the next action.
- **`<search>` tags (orange)** — issued queries sent to an external knowledge source.
- **`<information>` blocks (orange)** — retrieved documents returned from the source.

The loop continues until the model determines sufficient evidence has been gathered (or knowledge is insufficient), after which it terminates searching.

**Key takeaway:** SEARCH-R1 autonomously learns a *stop-searching* policy — the `<think>` step evaluates retrieved documents and halts the retrieve–reason loop once the external source is judged inadequate or the answer is located, rather than relying on a fixed iteration budget.

**Caption (verbatim):**

Table 19: SEARCH-R1 case study 10 (successful): SEARCH-R1 learns to stop searching when it finds out the external knowledge source is not sufficient to answer the question.

### Table 20 (p.31) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab20.png]]
> [!quote] caption
> S EARCH -R1 case study 11 (failed): The LLM can be misled by irrelevant retrieved information and provide a wrong answer.

> [!tip] 表格解读（多模态）
> **Description (architecture/components/data flow + key takeaway):**

The case study depicts SEARCH-R1's iterative retrieval-augmented reasoning pipeline applied to a multi-hop QA task. The flow proceeds as: **Question** → **Think** (plan query) → **Search** (issue query) → **Information** (retrieve document) → **Think** (interpret findings) → **Search** (follow-up query) → **Information** → **Think** (synthesize) → **Answer**. Components include an LLM reasoner producing explicit `<think>` traces and a search engine returning top-k documents.

**Key takeaway:** Despite retrieving two relevant-looking passages, the model hallucinated the answer ("London Charles") instead of the ground truth "Mani," demonstrating that surface-level relevance in retrieved documents is insufficient — SEARCH-R1 needs evidence-grounding or relevance filtering to prevent confidently propagating misaligned facts. (104 words)

**Caption verbatim:**

Table 20: SEARCH-R1 case study 11 (failed): The LLM can be misled by irrelevant retrieved information and provide a wrong answer.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathcal{J}_{GRPO}(\theta) = \, & \mathbb{E}_{x \sim \mathcal{D}, \{ y_i \}_{i=1}^{G} \sim \pi_{\text{old}}( \cdot| x; \se)} \Bigg[ \frac{1}{G} \sum_{i=1}^{G} \frac{1}{\sum_{t=1}^{|y_i|} I(y_{i,t})} \sum_{t=1: I(y_{i,t})=1}^{|y_i|} \min \Bigg( \frac{\pi_{\theta}(y_{i,t} | x, y_{i,<t}; \se)}{\pi_{\text{old}}(y_{i,t} | x, y_{i,<t}; \se)} \hat{A}_{i,t}, \nonumber \\[8pt] & \hspace{120pt} \text{clip} \Bigg( \frac{\pi_{\theta}(y_{i,t} | x, y_{i,<t}; \se)}{\pi_{\text{old}}(y_{i,t} | x, y_{i,<t}; \se)}, 1 - \epsilon, 1 + \epsilon \Bigg) \hat{A}_{i,t} \Bigg) - \beta \mathbb{D}_{KL} \left[ \pi_{\theta} || \pi_{\text{ref}} \right] \Bigg],
$$

$$
\max_{\pi_\theta} \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi_{\theta}(\cdot \mid x; \se)} \left[ r_{\phi}(x, y) \right] - \beta \mathbb{D}_{\text{KL}} \left[ \pi_{\theta}(y \mid x; \se) \,||\, \pi_{\text{ref}}(y \mid x; \se) \right],
$$

$$
\mathcal{J}_{PPO}(\theta) = \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi_{\text{old}}( \cdot| x; \se)} \left[ \frac{1}{\sum_{t=1}^{|y|} I(y_t)} \sum_{t=1: I(y_t)=1}^{|y|} \min \left( \frac{\pi_{\theta}(y_t | x, y_{<t}; \se)}{\pi_{\text{old}}(y_t | x, y_{<t}; \se)} A_t, \text{clip} \left( \frac{\pi_{\theta}(y_t | x, y_{<t}; \se)}{\pi_{\text{old}}(y_t | x, y_{<t}; \se)}, 1 - \epsilon, 1 + \epsilon \right) A_t \right) \right],
$$

$$
r_{\phi}(x, y) = \text{EM}(a_\text{pred}, a_\text{gold}),
$$

## 相关论文

- [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] — DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
- [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] — From ATOP to ZCube: Automated Topology Optimization Pipeline and A Highly Cost-Effective Network Topology for Large Model Training
- [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] — Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEMENT LEARNING
- [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] — AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning

## 技术点深读（DEEP）

![[deep/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning.txt`（100895 字符）供引用检索。