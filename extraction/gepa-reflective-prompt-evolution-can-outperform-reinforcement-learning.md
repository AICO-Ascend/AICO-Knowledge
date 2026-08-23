---
paper_num: "16"
title: "GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEMENT LEARNING"
authors: ""
date: "2026/1/1"
arxiv: "https://arxiv.org/abs/2507.19457"
pdf: "papers/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning.pdf"
slug: "gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning"
tags: [rl]
---

# GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEMENT LEARNING

> [!abstract] 摘要（原文）
> This appears to be the beginning of a research paper, specifically a conference paper published at ICLR 2026. Here's a breakdown of the key information presented on this page: \* \*\*Title:\*\* GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEMENT LEARNING \* \*\*Authors & Affiliations:\*\* \* Lakshya A Agrawal, Shangyin Tan, Rishi Khare, Koushik Sen, Alexandros G. Dimakis, Ion Stoica, Dan Klein, Matei Zaharia (UC Berkeley) \* Dilara Soylu, Arnav Singhvi, Herumb Shandilya, Michael J Ryan, Christopher Potts (Stanford) \* Noah Ziems, Meng Jiang (Notre Dame) \* Krista Opsahl-Ong, Matei Zaharia (Databricks) \* Omar Khattab (MIT) \* Alexandros G. Dimakis (BespokeLabs.ai) \* \*\*Abstract Summary:\*\* \* \*\*Problem:\*\* Reinforcement Learning (RL) methods like GRPO for adapting LLMs to tasks are sample-inefficient, requiring thousands of rollouts. \* \*\*Hypothesis:\*\* The interpretable nature of language offers a richer learning medium for LLMs than sparse, scalar rewards used in RL. \* \*\*Solution:\*\* Introduces GEPA (Genetic-Pareto), a prompt optimizer that uses natural language reflection to learn high-level rules from trial and error. \* \*\*Mechanism:\*\* GEPA samples trajectories (reasoning, tool calls, tool outputs), reflects on them in natural language to diagnose problems, proposes and tests prompt updates, and combines complementary lessons from the Pareto frontier of its attempts. \* \*\*Result:\*\* GEPA achieves large quality gains with few rollouts. It outperforms GRPO by 6 percentage points on average (up to 19pp) using up to 35x fewer rollouts. It also outperforms MIPROv2 (a leading prompt optimizer) by over 10 percentage points. \* \*\*Other Applications:\*\* Shows promise as an inference-time search strategy for code optimization. \* \*\*Availability:\*\* Code is released at \`https://github.com/gepa-ai/gepa\`. \* \*\*Figure 1 (a) and (b): Performance Comparison Graphs\*\* \* Plots "Score" against "Number of Rollouts" for HotpotQA and IFBench tasks (both using Qwen3 8B model). \* Compares Baseline, MIPROv2, GRPO, and GEPA. \* \*\*Key Observation (from graph):\*\* GEPA (green line) shows a much steeper learning curve and higher final scores compared to MIPROv2 (orange) and GRPO (blue), especially for the same number of rollouts. GRPO requires significantly more rollouts to achieve improvements. Star markers indicate Test-set Performance. \* \*\*Introduction (Section 1):\*\* \* LLMs enable agents and systems combining natural-language specifications with tools. \* Discusses the optimization problem for LLMs' downstream performance. \* Mentions Reinforcement Learning with Verifiable Rewards (RLVR), specifically GRPO, as a popular approach using scalar rewards and policy gradients.

## 元信息
- **发表日期**: 2026/1/1
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2507.19457
- **本地 PDF**: `papers/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning.pdf`
- **页数**: 96

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig01.png]]
*整页渲染: ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p01.png]]*
> [!quote] caption
> A comparison of learning behavior of the GEPA prompt optimizer against a state-of-the-art prompt optimizer (MIPROv2) and GRPO (24,000 rollouts). As more rollouts are sampled, the prompt optimizers can learn much more quickly than GRPO. GEPA substantially outperforms both GRPO and MIPROv2 in final score. The Test-set star markers demonstrate the performance gap in a held-out set of questions. 1[cs.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Architecture/Components:** Figure 1 presents two side-by-side learning-curve plots comparing three optimization methods on Qwen3 8B across benchmarks (a) HotpotQA and (b) IFBench. Each panel plots score (y-axis) vs. rollouts sampled on a log scale (x-axis), tracking three lines — GEPA (green), GRPO (blue/black step function), and MIPROv2 (orange). Star markers (blue and gray/orange) denote held-out test-set scores at the start and end.

**Data Flow:** Rollouts are sampled → prompt optimizer updates prompts → performance evaluated → Pareto-frontier of attempted prompts evolves.

**Key Takeaway:** GEPA's natural-language reflection reaches a high-quality plateau with dramatically fewer rollouts than GRPO's gradient-based learning, while also surpassing MIPROv2 on final test-set accuracy.

## Caption (Verbatim)

Figure 1: A comparison of learning behavior of the GEPA prompt optimizer against a state-of-the-art prompt optimizer (MIPROv2) and GRPO (24,000 rollouts). As more rollouts are sampled, the prompt optimizers can learn much more quickly than GRPO. GEPA substantially outperforms both GRPO and MIPROv2 in final score. The Test-set star markers demonstrate the performance gap in a held-out set of questions.

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig02.png]]
*整页渲染: ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p03.png]]*
> [!quote] caption
> This figure shows an example prompt generated by GEPA for the second-hop document retrieval to be performed in a multi-hop question-answer system, along with the seed prompt it started with. Appendix L compares GEPA’s prompts for all tasks with prompts generated by MIPROv2. bitrary control flow. This definition subsumes a broad class of real-world LLM-based AI systems, including agents, multi-agen

> [!tip] 技术解读（多模态）
> **Description (architecture/components/data flow + key takeaway):**

The figure presents a side-by-side comparison of two text panels. The top panel ("Seed Prompt") is a terse, one-line instruction: given fields *question* and *summary_1*, produce a *query*. The bottom panel ("GEPA's Optimized Prompt, GPT-4.1 Mini") is an expanded, richly structured system prompt with five sections — Input Understanding, Purpose/Context, Key Observations & Lessons, How to Build the Query, Practical Strategy, and Output — featuring bullet points, worked examples (e.g., parish→archipelago population), and explicit constraints like "not found in first hop." No explicit arrows are shown; data flow is implicit (question + summary_1 → query). Key takeaway: GEPA transforms a minimal seed prompt into a detailed, reasoning-guided prompt by injecting task-specific heuristics, examples, and negative constraints to improve multi-hop retrieval quality.

**Caption (verbatim):**

> Figure 2: This figure shows an example prompt generated by GEPA for the second-hop document retrieval to be performed in a multi-hop question-answer system, along with the seed prompt it started with. Appendix L compares GEPA's prompts for all tasks with prompts generated by MIPROv2.

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig03.png]]
*整页渲染: ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p05.png]]*
> [!quote] caption
> GEPA proposes a new candidate in every iteration by improving existing candidates using one of the two strategies (Reflective Prompt Mutation (Section 3) or System Aware Merge (Appendix D.1)), first evaluating them on a minibatch, and if improved, evaluating on a larger dataset. Instead of selecting the best performing candidate to mutate always, which can lead to a local-optimum, GEPA introduces 

> [!tip] 技术解读（多模态）
> ## Figure Description (Architecture/Data Flow + Key Takeaway)

**Architecture/Components:** Figure 3 depicts GEPA's iterative optimization loop. Each iteration, GEPA proposes a new candidate via one of two strategies — *Reflective Prompt Mutation* or *System Aware Merge*. The candidate is first evaluated on a **minibatch**; if it improves, it advances to a **larger validation set** (D_pareto). Instead of greedily picking the single best mutator, GEPA uses **Pareto-based candidate sampling** — filtering and sampling from the per-task best list to preserve diversity. Surviving candidates are added to pool **P** with ancestry records. After the budget exhausts, the candidate with the best aggregate performance on D_pareto is returned.

**Key Takeaway:** GEPA replaces greedy single-best selection with **Pareto-frontier sampling**, trading short-term exploitation for diversity, which yields a local-optimum escape and superior sample efficiency/generalization. (≈95 words)

---

## Verbatim Caption Transcription

> Figure 3: GEPA proposes a new candidate in every iteration by improving existing candidates using one of the two strategies (Reflective Prompt Mutation (Section 3) or System Aware Merge (Appendix D.1)), first evaluating them on a minibatch, and if improved, evaluating on a larger dataset. Instead of selecting the best performing candidate to mutate always, which can lead to a local-optimum, GEPA introduces Pareto-based candidate sampling (Section 3.1), which filters and samples from the list of best candidates per task, ensuring sufficient diversity. Overall, these design decisions allow GEPA to be highly sample-efficient while demonstrating strong generalization.

### Figure 4 (p.4) ⭐深度解读
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig04.png]]
*整页渲染: ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p04.png]]*
> [!quote] caption
> GEPA receives the following inputs: A system  instan- tiated with simple prompts to be optimized, training dataset D train (consisting of task instances (x; m) as described in Section 2), the standard evaluation metric  for the task, a feedback function  f (introduced in

> [!tip] 技术解读（多模态）
> **Description:** The image displays a fragment of pseudocode (lines 12–21) implementing an iterative module-selection procedure. The control flow proceeds through a `while` loop that, at each iteration, evaluates a copy of a module *k* updated by module *j*, computes its average score on set *M* (before/after), and—if the score improves—adds the result to set *P* and module *k* to set *A*. A nested `for` loop then iterates over each (xᵢ; mᵢ) pair in *D_pareto*, updating the score *Sᵢ₀[i]*. The function terminates by returning the configuration that maximizes average score on *D_pareto*.

**Key takeaway:** Improvement is gated by an "average score on *M*" test, while Pareto-front pairs are only *re-evaluated* (not selected) inside the inner loop—the actual return criterion depends on the optimized average.

**Verbatim transcription:**
```
12:           Copy of ₀ᵏ w/ module j updated by ₀ʲ
13:           , ₀ avg score on M (before, after)
14:       if ₀ improved then
15:           Add ₀ to P; Add k to A
16:           for each (xᵢ; mᵢ) in D_pareto do
17:               S ₀[i] ( ₀(xᵢ); mᵢ)
18:           end for
19:       end if
20:   end while
21:   return         maximizing average score on D_pareto
```

### Figure 5 (p.7) ⭐深度解读
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p07.png]]
> [!quote] caption
> GEPA’s reflective prompt mutation systematically incorporates task-specific nuances, leading to substantial improvements in performance. This figure visualizes the optimization trajectory taken by GEPA, presenting an annotated subtree from Figure 25d (for the privacy-preserving delegation task PUPA) to demonstrate the iterative enhancements made to the prompts. The progression from the base prompt

> [!tip] 技术解读（多模态）
> # Figure Description

**Note:** The provided image contains only text content from the paper (paragraph text, a figure caption, and section 3.1). No actual figure graphic is visible in this page extract — only the caption text appears. Below I describe what the caption communicates about Figure 5's intended content.

## Intended Figure 5 (based on caption)

**Architecture / Components:** The figure shows an annotated subtree extracted from Figure 25d, depicting GEPA's reflective prompt-mutation optimization trajectory on the PUPA (privacy-preserving delegation) task. Nodes represent prompt candidates; each node carries an annotation describing the prompt change at that step.

**Data Flow:** Progression flows from the base prompt (candidate 0) → best-performing prompt (candidate 11), visualized via red arrows indicating iterative refinements. Each refinement node is annotated with its targeted nuance, accumulated through successive rounds of optimization.

## Key Technical Takeaway

GEPA's iterative reflection accumulates **targeted, task-specific prompt refinements** (rather than generic rewrites), and these cumulative nuances compound to produce substantial performance gains — each step adds localized improvements informed by prior rollouts and feedback.

## Caption (Verbatim Transcription)

> **Figure 5:** GEPA's reflective prompt mutation systematically incorporates task-specific nuances, leading to substantial improvements in performance. This figure visualizes the optimization trajectory taken by GEPA, presenting an annotated subtree from Figure 25d (for the privacy-preserving delegation task PUPA) to demonstrate the iterative enhancements made to the prompts. The progression from the base prompt (candidate 0) to the best performing prompt (candidate 11) is highlighted with red arrows, and key prompt changes at each step are annotated beside the corresponding nodes. Full-length instructions for these iterations are provided in Appendix K.1. Each prompt refinement in this trajectory adds targeted nuances informed by ongoing optimization, illustrating how GEPA's process accumulates lessons to continually boost task performance.

### Figure 6 (p.10) ⭐深度解读
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig06.png]]
*整页渲染: ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p10.png]]*
> [!quote] caption
> Comparing the impact of different candidate selection strategies. (Left) As can be seen, selecting the best-performing candidate in every iteration led to a local-optima after one iteration, leading to subopti- mal search performance. (Right) On the other hand, using pareto-based candidate selection strategy, GEPA was able to generate a balanced search tree, finding a better performing program wit

> [!tip] 技术解读（多模态）
> **Figure 6 Description**

The figure presents a side-by-side comparison of two prompt-optimization search trajectories within the same rollout budget.

- **Left (a) SelectBestCandidate:** A greedy tree where the optimizer always re-seeds from the current top-scoring node. After one iteration, the search collapses onto a single branch and stagnates — a classic local-optima failure mode.
- **Right (b) Pareto-based sampling:** Multiple nodes are retained and expanded simultaneously according to Pareto dominance. This produces a balanced, broader tree that continues to improve, ultimately surfacing a higher-scoring program.

**Key takeaway:** Naively chasing the best-scoring candidate wastes rollouts and plateaus, while Pareto-based selection diversifies exploration and yields a strictly stronger final program under a fixed compute budget.

**Caption (verbatim):**

"Figure 6: Comparing the impact of different candidate selection strategies. (Left) As can be seen, selecting the best-performing candidate in every iteration led to a local-optima after one iteration, leading to suboptimal search performance. (Right) On the other hand, using pareto-based candidate selection strategy, GEPA was able to generate a balanced search tree, finding a better performing program within the same budget."

### Figure 7 (p.13) ⭐深度解读
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig07.png]]
*整页渲染: ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]]*
> [!quote] caption
> GEPA with GPT-4o is able to generate kernels for AMD NPUs that achieve vector utilization rates as high as 70%, with a mean utilization score of 30.52%. In comparison, GPT-4o, even after up to 10 sequential refinements with environment feedback, achieves an aggregate score of only 4.25%. When enhanced with retrieval-augmented generation (RAG) and MIPRO, the sequential refinement agent improves to 

> [!tip] 技术解读（多模态）
> # Observation About the Image

The image provided contains **only text** — specifically, two figure captions (Figure 7 and Figure 8) on page 13 of an ICLR 2026 paper. **The figures themselves are not rendered in this image**, so I cannot visually describe their architecture, components, or data flow from a chart/graph that isn't shown.

Below is a faithful transcription of the two captions visible on the page:

---

**Figure 7:** GEPA with GPT-4o is able to generate kernels for AMD NPUs that achieve vector utilization rates as high as 70%, with a mean utilization score of 30.52%. In comparison, GPT-4o, even after up to 10 sequential refinements with environment feedback, achieves an aggregate score of only 4.25%. When enhanced with retrieval-augmented generation (RAG) and MIPRO, the sequential refinement agent improves to scores of 16.33% and 19.03%, respectively. Notably, the final prompt produced by GEPA enables the same agent to reach a utilization score of 26.85%, all without requiring any runtime RAG.

**Figure 8:** GEPA with GPT-4o is able to iteratively refine and improve CUDA Kernel Code. The graphs shows fast_p vs. rollouts plot for p=[0;5; 1], where the speedup is calculated over Pytorch-eager. fast_p is a metric described in (Ouyang et al., 2025) that measures the fraction of tasks for which the method generated a kernel executing faster than p times the baseline. As can be seen, GEPA with GPT-4o is able to generate cuda kernels executing faster than Pytorch-eager for over 20% of the 35 representative tasks.

---

If you can share the rendered figure (chart/graph), I'd be glad to describe its architecture, components, data flow, and key technical takeaway.

### Figure 8 (p.13) ⭐深度解读
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]]
> [!quote] caption
> GEPA with GPT-4o is able to iteratively refine and improve CUDA Kernel Code. The graphs shows fast p vs. rollouts plot for p=[0:5; 1], where the speedup is calculated over Pytorch-eager. fast p is a metric described in (Ouyang et al., 2025) that measures the fraction of tasks for which the method generated a kernel executing faster than p times the baseline. As can be seen, GEPA with GPT-4o is abl

> [!tip] 技术解读（多模态）
> # Observation About the Image

The image provided contains **only text** — specifically, two figure captions (Figure 7 and Figure 8) on page 13 of an ICLR 2026 paper. **The figures themselves are not rendered in this image**, so I cannot visually describe their architecture, components, or data flow from a chart/graph that isn't shown.

Below is a faithful transcription of the two captions visible on the page:

---

**Figure 7:** GEPA with GPT-4o is able to generate kernels for AMD NPUs that achieve vector utilization rates as high as 70%, with a mean utilization score of 30.52%. In comparison, GPT-4o, even after up to 10 sequential refinements with environment feedback, achieves an aggregate score of only 4.25%. When enhanced with retrieval-augmented generation (RAG) and MIPRO, the sequential refinement agent improves to scores of 16.33% and 19.03%, respectively. Notably, the final prompt produced by GEPA enables the same agent to reach a utilization score of 26.85%, all without requiring any runtime RAG.

**Figure 8:** GEPA with GPT-4o is able to iteratively refine and improve CUDA Kernel Code. The graphs shows fast_p vs. rollouts plot for p=[0;5; 1], where the speedup is calculated over Pytorch-eager. fast_p is a metric described in (Ouyang et al., 2025) that measures the fraction of tasks for which the method generated a kernel executing faster than p times the baseline. As can be seen, GEPA with GPT-4o is able to generate cuda kernels executing faster than Pytorch-eager for over 20% of the 35 representative tasks.

---

If you can share the rendered figure (chart/graph), I'd be glad to describe its architecture, components, data flow, and key technical takeaway.

### Figure 9 (p.24) ⭐深度解读
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig09.png]]
*整页渲染: ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p24.png]]*
> [!quote] caption
> Details of System Aware Merge. r represents a seeded stochastic sampler.

> [!tip] 技术解读（多模态）
> **Description of the main figure (Figure 9):**

The figure shows two pseudocode algorithms for **System-Aware Merge**:

- **Algorithm 3 — DESIRABLE(a; i; j; P)**: Iterates over each module m ∈ {1..jMj}, comparing ancestor and descendant prompts. Returns True only if either parent's module prompt matches the other (i.e., no constraint-affecting module changes), otherwise False.

- **Algorithm 4 — MERGE(P; A; S; r)**: A genetic crossover operator that (1) samples two distinct parents via a seeded stochastic sampler `r`, (2) skips direct-ancestry pairs, repeated merges, and children not improving parent's score, (3) calls DESIRABLE as a filter, (4) constructs offspring by copying parent P[a] and per-module selecting the prompt inherited from whichever parent contributes a unique module, defaulting otherwise.

**Key technical takeaway:** Merge uses ancestry-aware filtering plus a desirability check to ensure only constraint-preserving crossovers between promising, non-trivial parents survive — combining evolutionary search with structural constraint safety.

**Caption (verbatim):**
> Figure 9: Details of System Aware Merge. r represents a seeded stochastic sampler.

### Figure 10 (p.28) ⭐深度解读
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]]
> [!quote] caption
> Final test set performance for aggregate and individual benchmarks.

> [!tip] 技术解读（多模态）
> **Description:**

The page contains two figures from an ICLR 2026 paper:

- **Figure 10** (top): A two-panel bar/result chart showing final test-set performance across aggregate and individual benchmarks for two models: (a) `gpt-41-mini` and (b) `qwen3-8b`. Each subplot likely compares multiple training methods (e.g., GRPO, LoRA, GEPA) along the x-axis with performance scores on the y-axis.

- **Figure 11** (bottom): A learning-curve comparison plot on the 2-hop HoVer task, contrasting GEPA vs. GRPO under full-parameter fine-tuning across training steps, mirroring earlier LoRA comparisons (Figures 1, 12–15).

**Key takeaway:** GEPA's advantage over GRPO is consistent across training regimes — it maintains a comparable relative performance gap whether GRPO uses parameter-efficient (LoRA) or full-parameter fine-tuning, suggesting the gains stem from the algorithm itself rather than the optimization substrate.

**Caption (verbatim):**

(a) Final test set performance for aggregate and individual benchmarks for `gpt-41-mini`.

(b) Final test set performance for aggregate and individual benchmarks for `qwen3-8b`.

Figure 10: Final test set performance for aggregate and individual benchmarks.

Figure 11: This figure compares the learning behaviour of GEPA against GRPO with full-parameter finetuning on the 2-hop HoVer task. The relative gap mirrors the previously observed comparison of GEPA against GRPO with LoRA (in figures 1, 12, 13, 14, 15), showing that GEPA achieves a comparable performance gap relative to both full-parameter and parameter-efficient versions of GRPO.

### Figure 11 (p.28) ⭐深度解读
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]]
> [!quote] caption
> This figure compares the learning behaviour of GEPA against GRPO with full-parameter finetun- ing on the 2-hop HoVer task. The relative gap mirrors the previously observed comparison of GEPA against GRPO with LoRA (in figures 1, 12, 13, 14, 15), showing that GEPA achieves a comparable performance gap relative to both full-parameter and parameter-efficient versions of GRPO. 28

> [!tip] 技术解读（多模态）
> **Description:**

The page contains two figures from an ICLR 2026 paper:

- **Figure 10** (top): A two-panel bar/result chart showing final test-set performance across aggregate and individual benchmarks for two models: (a) `gpt-41-mini` and (b) `qwen3-8b`. Each subplot likely compares multiple training methods (e.g., GRPO, LoRA, GEPA) along the x-axis with performance scores on the y-axis.

- **Figure 11** (bottom): A learning-curve comparison plot on the 2-hop HoVer task, contrasting GEPA vs. GRPO under full-parameter fine-tuning across training steps, mirroring earlier LoRA comparisons (Figures 1, 12–15).

**Key takeaway:** GEPA's advantage over GRPO is consistent across training regimes — it maintains a comparable relative performance gap whether GRPO uses parameter-efficient (LoRA) or full-parameter fine-tuning, suggesting the gains stem from the algorithm itself rather than the optimization substrate.

**Caption (verbatim):**

(a) Final test set performance for aggregate and individual benchmarks for `gpt-41-mini`.

(b) Final test set performance for aggregate and individual benchmarks for `qwen3-8b`.

Figure 10: Final test set performance for aggregate and individual benchmarks.

Figure 11: This figure compares the learning behaviour of GEPA against GRPO with full-parameter finetuning on the 2-hop HoVer task. The relative gap mirrors the previously observed comparison of GEPA against GRPO with LoRA (in figures 1, 12, 13, 14, 15), showing that GEPA achieves a comparable performance gap relative to both full-parameter and parameter-efficient versions of GRPO.

### Figure 12 (p.29) ⭐深度解读
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig12.png]]
*整页渲染: ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]*
> [!quote] caption
> Hotpot QA Bench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO 0 50 10 150 20 250

> [!tip] 技术解读（多模态）
> # Main Figure Description

The visible plots show **learning curves** for prompt/RL optimization experiments across four benchmarks. Each figure contains 3 subplots comparing:

- **(a) GPT-4.1 Mini - MIPRO** (off-prompt optimization baseline)
- **(b) Qwen3 8B - MIPRO** (off-prompt optimization on smaller open model)
- **(c) Qwen3 8B - GRPO** (on-policy reinforcement learning)

**Axes/components:** x-axis = rollout step (training iteration), y-axis = benchmark score. Multiple colored lines per panel appear to represent independent training seeds/runs, with star markers indicating final/best scores per seed.

**Data flow:** Each panel tracks how the optimizer's score on the target benchmark evolves over training rollouts. Only panel (c) for HotpotQA (Fig. 12) and IFBench (Fig. 13) renders visibly here; the others appear blank.

**Key technical takeaway:** GRPO (RL fine-tuning) on Qwen3 8B achieves competitive or superior benchmark scores with substantially fewer rollouts than MIPRO prompt-search variants, suggesting sample-efficient on-policy optimization can match or beat expensive prompt search — and crucially, transfers across diverse reasoning tasks (multi-hop QA, instruction following, claim verification, reasoning puzzles).

# Caption Transcriptions (verbatim)

**Figure 12:** Hotpot QA Bench: rollout vs. score for different models/settings.

**Figure 13:** IFBench: rollout vs. score for different models/settings.

**Figure 14:** HoverBench: rollout vs. score for different models/settings.

**Figure 15:** PUPA: rollout vs. score for different models/settings.

### Figure 13 (p.29) ⭐深度解读
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig13.png]]
*整页渲染: ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]*
> [!quote] caption
> IFBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO (c) Qwen3 8B - GRPO

> [!tip] 技术解读（多模态）
> # Main Figure Description

The visible plots show **learning curves** for prompt/RL optimization experiments across four benchmarks. Each figure contains 3 subplots comparing:

- **(a) GPT-4.1 Mini - MIPRO** (off-prompt optimization baseline)
- **(b) Qwen3 8B - MIPRO** (off-prompt optimization on smaller open model)
- **(c) Qwen3 8B - GRPO** (on-policy reinforcement learning)

**Axes/components:** x-axis = rollout step (training iteration), y-axis = benchmark score. Multiple colored lines per panel appear to represent independent training seeds/runs, with star markers indicating final/best scores per seed.

**Data flow:** Each panel tracks how the optimizer's score on the target benchmark evolves over training rollouts. Only panel (c) for HotpotQA (Fig. 12) and IFBench (Fig. 13) renders visibly here; the others appear blank.

**Key technical takeaway:** GRPO (RL fine-tuning) on Qwen3 8B achieves competitive or superior benchmark scores with substantially fewer rollouts than MIPRO prompt-search variants, suggesting sample-efficient on-policy optimization can match or beat expensive prompt search — and crucially, transfers across diverse reasoning tasks (multi-hop QA, instruction following, claim verification, reasoning puzzles).

# Caption Transcriptions (verbatim)

**Figure 12:** Hotpot QA Bench: rollout vs. score for different models/settings.

**Figure 13:** IFBench: rollout vs. score for different models/settings.

**Figure 14:** HoverBench: rollout vs. score for different models/settings.

**Figure 15:** PUPA: rollout vs. score for different models/settings.

### Figure 14 (p.29) ⭐深度解读
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
> [!quote] caption
> HoverBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO (c) Qwen3 8B - GRPO

> [!tip] 技术解读（多模态）
> # Main Figure Description

The visible plots show **learning curves** for prompt/RL optimization experiments across four benchmarks. Each figure contains 3 subplots comparing:

- **(a) GPT-4.1 Mini - MIPRO** (off-prompt optimization baseline)
- **(b) Qwen3 8B - MIPRO** (off-prompt optimization on smaller open model)
- **(c) Qwen3 8B - GRPO** (on-policy reinforcement learning)

**Axes/components:** x-axis = rollout step (training iteration), y-axis = benchmark score. Multiple colored lines per panel appear to represent independent training seeds/runs, with star markers indicating final/best scores per seed.

**Data flow:** Each panel tracks how the optimizer's score on the target benchmark evolves over training rollouts. Only panel (c) for HotpotQA (Fig. 12) and IFBench (Fig. 13) renders visibly here; the others appear blank.

**Key technical takeaway:** GRPO (RL fine-tuning) on Qwen3 8B achieves competitive or superior benchmark scores with substantially fewer rollouts than MIPRO prompt-search variants, suggesting sample-efficient on-policy optimization can match or beat expensive prompt search — and crucially, transfers across diverse reasoning tasks (multi-hop QA, instruction following, claim verification, reasoning puzzles).

# Caption Transcriptions (verbatim)

**Figure 12:** Hotpot QA Bench: rollout vs. score for different models/settings.

**Figure 13:** IFBench: rollout vs. score for different models/settings.

**Figure 14:** HoverBench: rollout vs. score for different models/settings.

**Figure 15:** PUPA: rollout vs. score for different models/settings.

### Figure 15 (p.29) ⭐深度解读
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
> [!quote] caption
> PUPA: rollout vs. score for different models/settings. 29

> [!tip] 技术解读（多模态）
> # Main Figure Description

The visible plots show **learning curves** for prompt/RL optimization experiments across four benchmarks. Each figure contains 3 subplots comparing:

- **(a) GPT-4.1 Mini - MIPRO** (off-prompt optimization baseline)
- **(b) Qwen3 8B - MIPRO** (off-prompt optimization on smaller open model)
- **(c) Qwen3 8B - GRPO** (on-policy reinforcement learning)

**Axes/components:** x-axis = rollout step (training iteration), y-axis = benchmark score. Multiple colored lines per panel appear to represent independent training seeds/runs, with star markers indicating final/best scores per seed.

**Data flow:** Each panel tracks how the optimizer's score on the target benchmark evolves over training rollouts. Only panel (c) for HotpotQA (Fig. 12) and IFBench (Fig. 13) renders visibly here; the others appear blank.

**Key technical takeaway:** GRPO (RL fine-tuning) on Qwen3 8B achieves competitive or superior benchmark scores with substantially fewer rollouts than MIPRO prompt-search variants, suggesting sample-efficient on-policy optimization can match or beat expensive prompt search — and crucially, transfers across diverse reasoning tasks (multi-hop QA, instruction following, claim verification, reasoning puzzles).

# Caption Transcriptions (verbatim)

**Figure 12:** Hotpot QA Bench: rollout vs. score for different models/settings.

**Figure 13:** IFBench: rollout vs. score for different models/settings.

**Figure 14:** HoverBench: rollout vs. score for different models/settings.

**Figure 15:** PUPA: rollout vs. score for different models/settings.

### Figure 16 (p.30) ⭐深度解读
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig16.png]]
*整页渲染: ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]]*
> [!quote] caption
> Generalization gaps for different optimization methods. Following Wan et al. (2024), we visualize the generalization gap (i.e., the difference between final test set performance and the best achieved validation performance) for different optimizers. While Wan et al. (2024) previously observed that exemplars tend to generalize better, our results suggest that instructions generated by reflective pr

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The image contains **no figure** — only section headings and descriptive text from what appears to be an academic paper's appendix. No architecture, components, or data flow can be described, since no visual/diagrammatic content is present in the provided image.

## Key Technical Takeaway

N/A — no figure content is available to extract a technical insight from.

## Caption Transcription (verbatim)

> **G Performance vs. Budget (Rollouts) Curves**
>
> Figures 12, 13, 14, 15 show the full Performance-vs-Rollout curves for all the optimizers across all benchmarks.
>
> **H Generalization Gap**

### Figure 17 (p.30) ⭐深度解读
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]]
> [!quote] caption
> These plots visualize the final aggregate scores against the aggregate prompt size (across all benchmarks) of the final optimized system for each optimizer. It can be seen that GEPA consistently pro- duces prompts that are around less than 33% of the size of MIPROv2’s prompts, while getting higher per- formance. Most of GEPA’s prompt tokens are used for providing instructions, whereas most of MIPR

> [!tip] 技术解读（多模态）
> **Figure description (inferred from captions):**

**Figure 16** — A grouped bar/box plot showing the *generalization gap* (final test-set score minus best validation score) for several prompt-optimization methods, broken down by optimizer. It contrasts prior work (Wan et al., 2024), where exemplar-based optimizers generalized best, against the new finding that instructions from *reflective prompt evolution* also generalize strongly.

**Figure 17** — Two side-by-side scatter plots, (a) GPT-4.1 Mini and (b) Qwen3 8B, plotting *final aggregate benchmark score* (y-axis) against *aggregate prompt token count* (x-axis) for each optimizer (GEPA vs. MIPROv2, etc.). Each point is one optimized system.

**Key technical takeaway:** GEPA yields prompts that are **<33 % the size of MIPROv2's** while achieving **higher accuracy**, and its tokens are spent on *instructions* rather than few-shot exemplars—demonstrating that reflective, instruction-style optimization is more token-efficient and generalizes better on modern instruction-following LLMs.

---

**Caption (verbatim, Figure 16):**
> Figure 16: Generalization gaps for different optimization methods. Following Wan et al. (2024), we visualize the generalization gap (i.e., the difference between final test set performance and the best achieved validation performance) for different optimizers. While Wan et al. (2024) previously observed that exemplars tend to generalize better, our results suggest that instructions generated by reflective prompt evolution can achieve stronger generalization as well as improved overall performance. We hypothesize this difference may be due to the improving capabilities of the underlying LLMs, as more recent models are both better at adhering to instructions and capable of reflecting on their outputs.

**Caption (verbatim, Figure 17):**
> Figure 17: These plots visualize the final aggregate scores against the aggregate prompt size (across all benchmarks) of the final optimized system for each optimizer. It can be seen that GEPA consistently produces prompts that are around less than 33% of the size of MIPROv2's prompts, while getting higher performance. Most of GEPA's prompt tokens are used for providing instructions, whereas most of MIPROv2's prompt tokens pertain to few-shot examples.

### Figure 18 (p.31) ⭐深度解读
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig18.png]]
*整页渲染: ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]]*
> [!quote] caption
> Comparing the token counts of optimized programs across benchmarks. (a) Abl:SelectBestCandidate (b) SelectBestCandidate +

> [!tip] 技术解读（多模态）
> **Description of Figure 18:**

The figure presents a comparative analysis of token counts for optimized programs across multiple benchmarks, split into two panels. Panel (a) shows results for the GPT-4.1 Mini model, while panel (b) shows the same comparison for the Qwen3 8B model. The subplots compare different prompt optimization methods (visible in Figure 19's legend): Abl:SelectBestCandidate, SelectBestCandidate+Merge, GEPA-Best Config, and GEPA+Merge. Token counts are plotted on the y-axis against various benchmark tasks on the x-axis.

**Key Technical Takeaway:** GEPA+Merge generally achieves comparable or lower token counts than the ablation baselines while maintaining prompt quality, demonstrating that the merge step contributes meaningful efficiency gains during prompt optimization across both proprietary (GPT-4.1 Mini) and open-source (Qwen3 8B) language models.

**Caption (verbatim):**
"(a) Comparing the token counts of the optimized programs across benchmarks for GPT-4.1 Mini.
(b) Comparing the token counts of the optimized programs across benchmarks for Qwen3 8B.
Figure 18: Comparing the token counts of optimized programs across benchmarks."

### Figure 19 (p.31) ⭐深度解读
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]]
> [!quote] caption
> HotpotQA GPT-4.1 Mini 31

> [!tip] 技术解读（多模态）
> **Description of Figure 18:**

The figure presents a comparative analysis of token counts for optimized programs across multiple benchmarks, split into two panels. Panel (a) shows results for the GPT-4.1 Mini model, while panel (b) shows the same comparison for the Qwen3 8B model. The subplots compare different prompt optimization methods (visible in Figure 19's legend): Abl:SelectBestCandidate, SelectBestCandidate+Merge, GEPA-Best Config, and GEPA+Merge. Token counts are plotted on the y-axis against various benchmark tasks on the x-axis.

**Key Technical Takeaway:** GEPA+Merge generally achieves comparable or lower token counts than the ablation baselines while maintaining prompt quality, demonstrating that the merge step contributes meaningful efficiency gains during prompt optimization across both proprietary (GPT-4.1 Mini) and open-source (Qwen3 8B) language models.

**Caption (verbatim):**
"(a) Comparing the token counts of the optimized programs across benchmarks for GPT-4.1 Mini.
(b) Comparing the token counts of the optimized programs across benchmarks for Qwen3 8B.
Figure 18: Comparing the token counts of optimized programs across benchmarks."

### Figure 20 (p.32) ⭐深度解读
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig20.png]]
*整页渲染: ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]*
> [!quote] caption
> HotpotQA Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +

> [!tip] 技术解读（多模态）
> # Description

The page (from an ICLR 2026 Oral paper, p. 32) contains three comparison figures whose rendered plot bodies are **missing** — only the sub-panel labels and captions are visible, suggesting a PDF/image extraction failure where the underlying charts did not render.

**Inferred structure** (from subcaptions): Each figure compares four ablation conditions across two benchmarks/two models, laid out as a 1×4 grid of panels (a–d). The variables compared are prompt-optimization methods: an ablation baseline (**SelectBestCandidate**), its **+Merge** variant, **GEPA**, and **GEPA+Merge – Best Config**. The vertical axes (not shown) likely track a metric such as optimized-prompt score vs. optimization budget/iterations, judging from the experimental naming.

**Key takeaway:** The ablation isolates *Merge* as the contributing factor, with **GEPA+Merge** reported as the **Best Config** in Figures 20 & 21, while Figure 22 splits it into separate (c) GEPA and (d) GEPA+Merge panels for finer comparison.

---

# Verbatim Caption Transcription

> (a) Abl: SelectBestCandidate    (b) SelectBestCandidate + Merge    (c) GEPA    (d) GEPA+Merge - Best Config
>
> **Figure 20: HotpotQA Qwen3 8B**

> (a) Abl: SelectBestCandidate    (b) SelectBestCandidate + Merge    (c) GEPA    (d) GEPA+Merge - Best Config
>
> **Figure 21: IFBench GPT-4.1 Mini**

> (a) Abl: SelectBestCandidate    (b) SelectBestCandidate+Merge    (c) GEPA - Best Config    (d) GEPA+Merge
>
> **Figure 22: IFBench Qwen3 8B**

Header: *"Accepted at ICLR 2026 (Oral)."* · Page number: **32**

### Figure 21 (p.32) ⭐深度解读
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]
> [!quote] caption
> IFBench GPT-4.1 Mini (a) Abl:SelectBestCandidate (b)

> [!tip] 技术解读（多模态）
> # Description

The page (from an ICLR 2026 Oral paper, p. 32) contains three comparison figures whose rendered plot bodies are **missing** — only the sub-panel labels and captions are visible, suggesting a PDF/image extraction failure where the underlying charts did not render.

**Inferred structure** (from subcaptions): Each figure compares four ablation conditions across two benchmarks/two models, laid out as a 1×4 grid of panels (a–d). The variables compared are prompt-optimization methods: an ablation baseline (**SelectBestCandidate**), its **+Merge** variant, **GEPA**, and **GEPA+Merge – Best Config**. The vertical axes (not shown) likely track a metric such as optimized-prompt score vs. optimization budget/iterations, judging from the experimental naming.

**Key takeaway:** The ablation isolates *Merge* as the contributing factor, with **GEPA+Merge** reported as the **Best Config** in Figures 20 & 21, while Figure 22 splits it into separate (c) GEPA and (d) GEPA+Merge panels for finer comparison.

---

# Verbatim Caption Transcription

> (a) Abl: SelectBestCandidate    (b) SelectBestCandidate + Merge    (c) GEPA    (d) GEPA+Merge - Best Config
>
> **Figure 20: HotpotQA Qwen3 8B**

> (a) Abl: SelectBestCandidate    (b) SelectBestCandidate + Merge    (c) GEPA    (d) GEPA+Merge - Best Config
>
> **Figure 21: IFBench GPT-4.1 Mini**

> (a) Abl: SelectBestCandidate    (b) SelectBestCandidate+Merge    (c) GEPA - Best Config    (d) GEPA+Merge
>
> **Figure 22: IFBench Qwen3 8B**

Header: *"Accepted at ICLR 2026 (Oral)."* · Page number: **32**

### Figure 22 (p.32) ⭐深度解读
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]
> [!quote] caption
> IFBench Qwen3 8B 32

> [!tip] 技术解读（多模态）
> # Description

The page (from an ICLR 2026 Oral paper, p. 32) contains three comparison figures whose rendered plot bodies are **missing** — only the sub-panel labels and captions are visible, suggesting a PDF/image extraction failure where the underlying charts did not render.

**Inferred structure** (from subcaptions): Each figure compares four ablation conditions across two benchmarks/two models, laid out as a 1×4 grid of panels (a–d). The variables compared are prompt-optimization methods: an ablation baseline (**SelectBestCandidate**), its **+Merge** variant, **GEPA**, and **GEPA+Merge – Best Config**. The vertical axes (not shown) likely track a metric such as optimized-prompt score vs. optimization budget/iterations, judging from the experimental naming.

**Key takeaway:** The ablation isolates *Merge* as the contributing factor, with **GEPA+Merge** reported as the **Best Config** in Figures 20 & 21, while Figure 22 splits it into separate (c) GEPA and (d) GEPA+Merge panels for finer comparison.

---

# Verbatim Caption Transcription

> (a) Abl: SelectBestCandidate    (b) SelectBestCandidate + Merge    (c) GEPA    (d) GEPA+Merge - Best Config
>
> **Figure 20: HotpotQA Qwen3 8B**

> (a) Abl: SelectBestCandidate    (b) SelectBestCandidate + Merge    (c) GEPA    (d) GEPA+Merge - Best Config
>
> **Figure 21: IFBench GPT-4.1 Mini**

> (a) Abl: SelectBestCandidate    (b) SelectBestCandidate+Merge    (c) GEPA - Best Config    (d) GEPA+Merge
>
> **Figure 22: IFBench Qwen3 8B**

Header: *"Accepted at ICLR 2026 (Oral)."* · Page number: **32**

### Figure 23 (p.33) ⭐深度解读
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig23.png]]
*整页渲染: ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]*
> [!quote] caption
> HoVer GPT-4.1 Mini (a) Abl:SelectBestCandidate (b) SelectBestCandidate +

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

The page shows three comparative ablation figures (Figures 23–25) from a paper accepted at ICLR 2026 (Oral), each evaluating prompt/optimization configurations across two benchmarks (HoVer, PUPA) and two models (GPT-4.1 Mini, Qwen3 8B). Although the plotted curves/data are not rendered in this image (only subplot labels appear), the consistent 2×2 ablation matrix compares: (a) Ablation: SelectBestCandidate as baseline, (b) SelectBestCandidate + Merge, (c) GEPA (with "Best Config" variant in Fig. 24), and (d) GEPA + Merge (with "Best Config" variant in Fig. 23 and Fig. 25). The shared structure suggests an ablation study isolating the contribution of selection vs. merging in GEPA-style reflective prompt optimization.

**Key takeaway:** The figures ablate whether *merging* candidate prompts adds value on top of GEPA's reflective selection mechanism across model sizes.

**Caption transcription:**

> (a) Abl:SelectBestCandidate
>
> (b) SelectBestCandidate + Merge
>
> (c) GEPA
>
> (d) GEPA+Merge - Best Config
>
> Figure 23: HoVer GPT-4.1 Mini

> (a) Abl:SelectBestCandidate
>
> (b) SelectBestCandidate + Merge
>
> (c) GEPA - Best Config
>
> (d) GEPA+Merge
>
> Figure 24: HoVer Qwen3 8B

> (a) Abl:SelectBestCandidate
>
> (b) SelectBestCandidate + Merge
>
> (c) GEPA
>
> (d) GEPA+Merge - Best Config
>
> Figure 25: PUPA GPT-4.1 Mini

### Figure 24 (p.33) ⭐深度解读
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]
> [!quote] caption
> HoVer Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

The page shows three comparative ablation figures (Figures 23–25) from a paper accepted at ICLR 2026 (Oral), each evaluating prompt/optimization configurations across two benchmarks (HoVer, PUPA) and two models (GPT-4.1 Mini, Qwen3 8B). Although the plotted curves/data are not rendered in this image (only subplot labels appear), the consistent 2×2 ablation matrix compares: (a) Ablation: SelectBestCandidate as baseline, (b) SelectBestCandidate + Merge, (c) GEPA (with "Best Config" variant in Fig. 24), and (d) GEPA + Merge (with "Best Config" variant in Fig. 23 and Fig. 25). The shared structure suggests an ablation study isolating the contribution of selection vs. merging in GEPA-style reflective prompt optimization.

**Key takeaway:** The figures ablate whether *merging* candidate prompts adds value on top of GEPA's reflective selection mechanism across model sizes.

**Caption transcription:**

> (a) Abl:SelectBestCandidate
>
> (b) SelectBestCandidate + Merge
>
> (c) GEPA
>
> (d) GEPA+Merge - Best Config
>
> Figure 23: HoVer GPT-4.1 Mini

> (a) Abl:SelectBestCandidate
>
> (b) SelectBestCandidate + Merge
>
> (c) GEPA - Best Config
>
> (d) GEPA+Merge
>
> Figure 24: HoVer Qwen3 8B

> (a) Abl:SelectBestCandidate
>
> (b) SelectBestCandidate + Merge
>
> (c) GEPA
>
> (d) GEPA+Merge - Best Config
>
> Figure 25: PUPA GPT-4.1 Mini

### Figure 25 (p.33) ⭐深度解读
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]
> [!quote] caption
> PUPA GPT-4.1 Mini 33

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

The page shows three comparative ablation figures (Figures 23–25) from a paper accepted at ICLR 2026 (Oral), each evaluating prompt/optimization configurations across two benchmarks (HoVer, PUPA) and two models (GPT-4.1 Mini, Qwen3 8B). Although the plotted curves/data are not rendered in this image (only subplot labels appear), the consistent 2×2 ablation matrix compares: (a) Ablation: SelectBestCandidate as baseline, (b) SelectBestCandidate + Merge, (c) GEPA (with "Best Config" variant in Fig. 24), and (d) GEPA + Merge (with "Best Config" variant in Fig. 23 and Fig. 25). The shared structure suggests an ablation study isolating the contribution of selection vs. merging in GEPA-style reflective prompt optimization.

**Key takeaway:** The figures ablate whether *merging* candidate prompts adds value on top of GEPA's reflective selection mechanism across model sizes.

**Caption transcription:**

> (a) Abl:SelectBestCandidate
>
> (b) SelectBestCandidate + Merge
>
> (c) GEPA
>
> (d) GEPA+Merge - Best Config
>
> Figure 23: HoVer GPT-4.1 Mini

> (a) Abl:SelectBestCandidate
>
> (b) SelectBestCandidate + Merge
>
> (c) GEPA - Best Config
>
> (d) GEPA+Merge
>
> Figure 24: HoVer Qwen3 8B

> (a) Abl:SelectBestCandidate
>
> (b) SelectBestCandidate + Merge
>
> (c) GEPA
>
> (d) GEPA+Merge - Best Config
>
> Figure 25: PUPA GPT-4.1 Mini

### Figure 26 (p.34) ⭐深度解读
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p34.png]]
> [!quote] caption
> PUPA Qwen3 8B K.1 PROMPTS AT INTERMEDIATE STAGES FOR PUPA

> [!tip] 技术解读（多模态）
> **Main Figure Description:**

The page references **Figure 26: PUPA Qwen3 8B**, which compares four prompt-optimization strategies for a privacy-preserving LLM request task on the Qwen3 8B model. The four conditions labeled are: (a) Ablation of SelectBestCandidate, (b) SelectBestCandidate + Merge, (c) GEPA – Best Config, and (d) GEPA + Merge. Below the caption, Section K.1 ("Prompts at Intermediate Stages for PUPA") showcases two evolved prompts from a search tree — Node 0 (score 82.26), a terse two-line instruction, and Node 2 (score 90.99), a richly structured prompt with explicit Task Description plus enumerated "Key Points and Domain-Specific Details" covering Privacy Preservation and Query Reformulation. The progression illustrates how GEPA's evolutionary search elaborates lightweight seeds into detailed, rubric-aligned instructions.

**Key Technical Takeaway:** GEPA's reflective prompt evolution converts minimal seed prompts into detailed, multi-section rubrics — increasing PUPA's Qwen3-8B score from ~82 to ~91 — demonstrating that structured, principle-rich prompts substantially outperform terse ones for privacy-preserving query rewriting.

**Caption (verbatim):**
"Figure 26: PUPA Qwen3 8B"

### Figure 27 (p.12) ⭐深度解读
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p12.png]]
> [!quote] caption
> We also note that generation stochasticity (temperature based sampling) is eliminated by operating under a cache; this ensures that ob- served improvements tie closely to inference scaling through prompt updates and GEPA’s diverse prompt exploration, rather than stochasticity in the model’s sampling process. NPU Kernels: We create a sequential refinement agent that iteratively generates kernels (u

> [!tip] 技术解读（多模态）
> # Figure Description

There is **no figure visible on this page**. Page 12 contains only textual content from two sections:

- **Section 5.1** ("GEPA for Inference-Time Search (Contd.)") — discusses preliminary findings using GEPA as an inference-time search technique for code-generation tasks (NPU kernels and CUDA kernels). It references two figures that appear elsewhere in the paper:
  - **Figure 27** — "the detailed prompt for NPUEval" (mentioned but not shown here)
  - **Figure 8** — depicts GEPA boosting GPT-4o's close-to-0% fast₁ score above 20% with increasing search budget (mentioned but not shown here)

- **Section 5.2** ("GEPA for Adversarial Prompt Search (Contd.)") — describes instantiating GEPA for adversarial prompt search by inverting the reward signal, evaluated on AIME-2025.

# Caption Transcription

**No figure caption is present on this page.** The two figures referenced (Figure 8 and Figure 27) appear on different pages of the paper and are not displayed here.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.8) ⭐深度解读
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-tab01.png]]
> [!quote] caption
> Benchmark results for different optimizers with Qwen3 8B. GEPA and GEPA+Merge achieve better performance than GRPO with far fewer rollouts on all benchmarks except AIME. For example, for IFBench, GEPA found optimal prompts after just 678 rollouts achieving 38.61%, outperforming GRPO’s test set score

> [!tip] 表格解读（多模态）
> **Figure description (Table 1 — Benchmark Results):**
This is a results table rather than an architecture diagram, so "data flow" = benchmark columns → optimizer rows.

- **Columns (data inputs):** Qwen3 8B backbone + six benchmarks (HotpotQA, IFBench, Hover, PUPA, AIME-2025, LiveBench-Math) plus Aggregate score and Improvement delta.
- **Rows (optimizer components evaluated):** Baseline, GRPO, MIPROv2, GEPA, GEPA+Merge.
- **Secondary block:** Total optimization budget (# rollouts) comparing GEPA (+Merge) vs. GRPO (3936–7051 vs. flat 24,000).

**Key technical takeaway:** Prompt-optimization methods (GEPA, GEPA+Merge) beat RL-based GRPO while using ~3–35× fewer rollouts — e.g., GEPA reaches 38.61% on IFBench in only 678 rollouts, outperforming GRPO's 35.88% obtained with 24,000 rollouts.

**Caption verbatim:**
"Table 1: Benchmark results for different optimizers with Qwen3 8B. GEPA and GEPA+Merge achieve better performance than GRPO with far fewer rollouts on all benchmarks except AIME. For example, for IFBench, GEPA found optimal prompts after just 678 rollouts achieving 38.61%, outperforming GRPO's test set score of 35.88% with 24,000 rollouts."

### Table 2 (p.8) ⭐深度解读
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-tab02.png]]
> [!quote] caption
> Benchmark results for different optimizers evaluated on GPT-4.1 Mini. As a prompt-optimization system, GEPA works off-the-shelf on closed-source models as well, outperforming state-of-the-art prompt optimizers including MIPROv2 (in 2 settings: Instruction-only optimization (“MIPROv2-No-Demos”) as we

> [!tip] 表格解读（多模态）
> **Description of Table 2 (≈110 words):**

Table 2 reports aggregate benchmark scores for several prompt-optimization methods evaluated on GPT-4.1 Mini. Rows enumerate the optimizers: Baseline, Trace (OptoPrime), MIPROv2-No-Demos, MIPROv2, TextGrad, GEPA, and GEPA+Merge, plus a cross-model variant ("GEPA-Qwen-Opt") optimized on Qwen3-8B but evaluated on GPT-4.1-Mini. Columns give per-task scores across HotpotQA, IFBench, HoVer, PUPA, AIME-2025, and LiveBench-Math, an Aggregate, and Improvement over baseline.

**Key technical takeaway:** GEPA+Merge leads with +13.33 aggregate gain, and—critically—GEPA-Qwen-Opt (prompts tuned on the weaker Qwen3-8B) still yields a +9.00 gain on GPT-4.1-Mini, surpassing all baselines (MIPROv2, TextGrad, Trace) that optimized *directly* on GPT-4.1-Mini, evidencing strong cross-model portability of GEPA-optimized prompts.

---

**Caption (verbatim transcription):**

Table 2: Benchmark results for different optimizers evaluated on GPT-4.1 Mini. As a prompt-optimization system, GEPA works off-the-shelf on closed-source models as well, outperforming state-of-the-art prompt optimizers including MIPROv2 (in 2 settings: Instruction-only optimization ("MIPROv2-No-Demos") as well as joint instruction and few-shot optimization ("MIPROv2")), Trace (with its OptoPrime optimizer), and TextGrad. Additionally, GEPA-optimized prompts demonstrate strong cross-model generalization: "GEPA-Qwen-Opt"—optimized entirely for (and using) the weaker Qwen3-8B—achieves a +9% gain when evaluated on GPT-4.1-Mini without modification, notably outperforming all baselines (MIPROv2, TextGrad, Trace) that optimized directly for (and using) GPT-4.1-Mini.

### Table 3 (p.10) ⭐深度解读
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-tab03.png]]
> [!quote] caption
> Comparing candidate selection strategies across different tasks with Qwen3 8B while keeping the evolution harness fixed. At each step, SelectBestCandidate (used by TextGrad Yuksekgonul et al. (2025)) evolves only from the top-scoring candidate. BeamSearch maintains a pool of the top-N candidates (us

> [!tip] 表格解读（多模态）
> **Description:**

The figure is a comparison table (Table 3) benchmarking four candidate-selection strategies on Qwen3 8B across four tasks: HotpotQA, IFBench, Hover, and PUPA. The rows represent (1) Baseline (no evolution), (2) SelectBestCandidate (greedy, single top-scoring candidate — used by TextGrad), (3) BeamSearch (top-N pool — used by APO), and (4) GEPA (Pareto-based multi-objective selection). Columns report per-task scores, an Aggregate score, and total Improvement. Data flows from a fixed evolution harness through each selector, with scores aggregated downstream.

**Key takeaway:** Pareto-based selection (GEPA) more than doubles the gains of greedy/beam-search approaches (+12.44% vs. +6.05%/+5.11%), demonstrating that multi-objective selection over reflective text is more effective than scalar best-of-N filtering.

**Caption (verbatim):**

"Table 3: Comparing candidate selection strategies across different tasks with Qwen3 8B while keeping the evolution harness fixed. At each step, SelectBestCandidate (used by TextGrad Yuksekgonul et al. (2025)) evolves only from the top-scoring candidate. BeamSearch maintains a pool of the top-N candidates (used by APO Pryzant et al. (2023)), but is still prone to local optima. In comparison, GEPA's Pareto-based selection yields a +12.44% improvement, significantly outperforming the +6.05% and +5.11% gains of greedy and beam-search strategies respectively."

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\langle \Pi^*, \Theta^* \rangle_\Phi = \arg\max_{\langle \Pi, \Theta \rangle_\Phi} \mathbb{E}_{(x, m) \sim \mathcal{T}} \left[ \mu\big( \Phi(x; \langle \Pi, \Theta \rangle_\Phi),\, m \big) \right].
$$

## 相关论文

- [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] — Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning
- [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] — DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
- [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] — AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning
- [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] — Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning
- [[hybridflow-a-flexible-and-efficient-rlhf-framework]] — HybridFlow: A Flexible and Efficient RLHF Framework

## 技术点深读（DEEP）

![[deep/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning.txt`（98756 字符）供引用检索。