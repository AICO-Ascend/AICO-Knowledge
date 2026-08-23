---
paper_num: "32"
title: "Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with Large-Scale Asynchronous RL"
authors: "Search with Large-Scale Asynchronous RL Jiaxuan Gao1, Wei Fu12, Minyang Xie1, Shusheng Xu2, Chuyi He2, Zhiyu Mei2, Banghua Zhu3, Yi Wu1∗ 1 IIIS, Tsinghua University, 2 Ant Group 3 University of Washington samjia2000@gmai"
date: "2026/1/17"
arxiv: "https://arxiv.org/abs/2508.07976"
pdf: "papers/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl.pdf"
slug: "beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl"
tags: []
---

# Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with Large-Scale Asynchronous RL

> [!abstract] 摘要（原文）
> 

## 元信息
- **发表日期**: 2026/1/17
- **作者**: Search with Large-Scale Asynchronous RL Jiaxuan Gao1, Wei Fu12, Minyang Xie1, Shusheng Xu2, Chuyi He2, Zhiyu Mei2, Banghua Zhu3, Yi Wu1∗ 1 IIIS, Tsinghua University, 2 Ant Group 3 University of Washington samjia2000@gmai
- **arXiv**: https://arxiv.org/abs/2508.07976
- **本地 PDF**: `papers/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl.pdf`
- **页数**: 21

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig01.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p01.png]]*
> [!quote] caption
> (Left) Asynchronous RL brings substantial improvements: Through RL training, our agent, ASearcher-Web-QwQ, obtains +15.0, +22.4, and +15.6 improvements on GAIA, xBench, and

> [!tip] 技术解读（多模态）
> # Figure Description

**Architecture/Components/Data Flow:**
The figure depicts a comparative chart for what appears to be a method called **DEPA** (with a variant labeled **DEPA-R**), benchmarking it against several baseline models. The layout shows performance results along a categorical axis (multiple models/tasks listed vertically) against a metric scale (0–2 range). Legend entries distinguish **"Avg@4"** and per-stage breakdowns (**Stage 1** vs **Stage 2**) for two configurations, suggesting a two-stage pipeline evaluation. Data flow appears to compare token-level decoding metrics (e.g., EOS/NLL-related indicators) across competing approaches.

**Key Technical Takeaway:**
DEPA's two-stage variant achieves higher aggregate scores than single-stage baselines, indicating that separating the pipeline into Stage 1 + Stage 2 yields measurable gains in the Avg@4 metric.

# Caption (Verbatim — as rendered; text is heavily overlapping/garbled in the source)

> "Figure : ... DEPA vs ... 1,NLL 2, ... 1,EOS 2, ... 1, ... 2, ... Avg@4 Stage 1 Stage 2 Stage 1 Stage 2 ... (a) ... 2-output ... (b) ..."

**Note:** The page (arXiv:2508.07976v4) has severely overlapping/illegible glyphs in this figure region, so a clean verbatim transcription is not possible from the rendered image alone — most labels appear stacked and unreadable.

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig02.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p03.png]]*
> [!quote] caption
> Comparison between ASearcher and Search-R1. (Left) Search-R1 is only equipped with search tools and lacks web browsing capability. (Right) ASearcher utilizes a simple agent design with two basic tools including search and browsing tools, without relying on any external LLM. ASearcher is a comprehensive agent capable of both reasoning and summarizing lengthy web contents. Notably, both reasoning an

> [!tip] 技术解读（多模态）
> **Figure Description (Architecture & Data Flow):**

The figure contrasts two agent architectures for search-augmented QA. **Search-R1 (left)** uses a single-loop pipeline: User Query → Trainable LLM Gen → Tool Calling → Search Query → External Search Engine → Top-K Entries, looping back over ≤10 turns to produce an Answer. **ASearcher (right)** extends this with a dual-tool design: the same LLM Gen / Tool Calling dispatch can invoke either the Search tool (→ Search Engine → Top-K Entries) **or** a Browser tool (→ Webpage ~100K chars → Summarize ~100 chars), allowing up to **128 turns** before yielding the Answer. The legend distinguishes trainable components (blue LLM Gen), external tools (pink), external info (green), and tool-calling logic (orange).

**Key Technical Takeaway:** ASearcher's novelty lies in jointly optimizing **long-horizon reasoning and long-context summarization** through end-to-end RL on a single LLM — no external LLM is required, and the 128-turn budget enables multi-hop web evidence synthesis (Figure 2).

**Caption (Verbatim):**

Figure 2: Comparison between ASearcher and Search-R1. (Left) Search-R1 is only equipped with search tools and lacks web browsing capability. (Right) ASearcher utilizes a simple agent design with two basic tools including search and browsing tools, without relying on any external LLM. ASearcher is a comprehensive agent capable of both reasoning and summarizing lengthy web contents. Notably, both reasoning and summarization abilities are optimized through end-to-end RL training.

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig03.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p04.png]]*
> [!quote] caption
> A case study on a complex query from GAIA. Search-R1-32B is unable to break down the complex question and has severe hallucinations. Search-o1 (QwQ) can identify the corrects articles through extensive tool calls, but easily misses key information and fails to verify wrong conclusions. Our end-to-end RL agent, ASearcher-Web-QwQ, exhibits key behaviors featuring

> [!tip] 技术解读（多模态）
> ## Description (≤120 words)

The figure compares three systems on a complex GAIA multi-hop query (answer: "Mice"). It is organized as a three-column case study:

1. **Search-R1-32B** (left): Fails — cannot decompose the query, hallucinates (claims alvei = Coprococcus), lacks verification, and ends with the wrong answer ("Pigs").
2. **Search-o1 (QwQ)** (middle): Identifies the genus but misses key information, jumps to a wrong conclusion, and cannot verify it.
3. **ASearcher-Web-QwQ** (right): Performs a structured pipeline — focused search → key-info extraction → uncertainty-aware source identification → cross-document inference (vet/animal filtering) → grounded verification — arriving at the correct answer "Mice."

**Key takeaway:** End-to-end RL agents that explicitly incorporate *uncertainty-aware reasoning, precise noisy-content extraction, cross-document inference, and grounded verification* outperform tool-call baselines on complex multi-hop search tasks.

## Caption (verbatim)

**Figure 3:** A case study on a complex query from GAIA. **Search-R1-32B** is unable to break down the complex question and has severe hallucinations. **Search-o1 (QwQ)** can identify the correct articles through extensive tool calls, but easily misses key information and fails to verify wrong conclusions. Our end-to-end RL agent, **ASearcher-Web-QwQ**, exhibits key behaviors featuring Search Intelligence: *uncertainty-aware reasoning* (list and examine candidate answers), *precise extraction* from noisy contents, *cross-document inference*, and *grounded verification*.

### Figure 4 (p.7) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig04.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p07.png]]*
> [!quote] caption
> Data Synthesis Agent. Starting from a seed QA, the data synthesis agent iteratively modifies the question through two actions, Injection and Fuzz. Through injection, the agent enriches the question by adding some external facts. Through Fuzz, the agent blurs certain information to increase uncertainty and difficulty. The related fact to the question are tracked during the synthesis process.

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 4 — Data Synthesis Agent)

**Architecture & Components:**
- **Synthetic QA & Facts** (left): seed QA pair + supporting facts feed an LLM agent.
- **Two Actions** branching from the agent:
  - **Extract Fact & Inject** (top): a Search Engine/Browser retrieves external facts and injects them into the question.
  - **Select Info. & Fuzz** (bottom): specific values (e.g., "2014") are blurred into uncertain placeholders (e.g., "early 2010s").
- **Quality Verification** (right): three sequential checks — (1) Basic Quality (solvability + clarity), (2) Difficulty Measurement (model must produce wrong answer among distractors), (3) Answer Uniqueness.

**Data Flow:** Seed QA → Agent → {Inject | Fuzz} → Modified Question + tracked supporting facts → 3-step Verification → loop until pass.

**Key Technical Takeaway:** The agent's two complementary actions (Injection adds facts to broaden reasoning; Fuzz hides facts to increase difficulty) combined with the 3-step verifier create a self-curating loop that yields hard-but-solvable multi-hop QA pairs.

---

## Verbatim Caption Transcription

**Figure 4:** Data Synthesis Agent. Starting from a seed QA, the data synthesis agent iteratively modifies the question through two actions, *Injection* and *Fuzz*. Through *injection*, the agent enriches the question by adding some external facts. Through *Fuzz*, the agent blurs certain information to increase uncertainty and difficulty. The related fact to the question are tracked during the synthesis process. Each time the question is modified, a quality verification step is applied to ensure quality and difficulty of the synthetic questions.

### Figure 5 (p.7) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig05.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p07.png]]*
> [!quote] caption
> Statistics from our data synthesis process. (Left) The distribution of the number of supporting facts. (Middle) The distribution of the number of fuzz actions and injection actions. (Right) The accuracy distribution of QwQ-32B in answering the generated questions without using any tools. • The model finds a correct answer with only a few search turns (i.e., ≤1 turns).

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 4 — Data Synthesis Agent)

**Architecture & Components:**
- **Synthetic QA & Facts** (left): seed QA pair + supporting facts feed an LLM agent.
- **Two Actions** branching from the agent:
  - **Extract Fact & Inject** (top): a Search Engine/Browser retrieves external facts and injects them into the question.
  - **Select Info. & Fuzz** (bottom): specific values (e.g., "2014") are blurred into uncertain placeholders (e.g., "early 2010s").
- **Quality Verification** (right): three sequential checks — (1) Basic Quality (solvability + clarity), (2) Difficulty Measurement (model must produce wrong answer among distractors), (3) Answer Uniqueness.

**Data Flow:** Seed QA → Agent → {Inject | Fuzz} → Modified Question + tracked supporting facts → 3-step Verification → loop until pass.

**Key Technical Takeaway:** The agent's two complementary actions (Injection adds facts to broaden reasoning; Fuzz hides facts to increase difficulty) combined with the 3-step verifier create a self-curating loop that yields hard-but-solvable multi-hop QA pairs.

---

## Verbatim Caption Transcription

**Figure 4:** Data Synthesis Agent. Starting from a seed QA, the data synthesis agent iteratively modifies the question through two actions, *Injection* and *Fuzz*. Through *injection*, the agent enriches the question by adding some external facts. Through *Fuzz*, the agent blurs certain information to increase uncertainty and difficulty. The related fact to the question are tracked during the synthesis process. Each time the question is modified, a quality verification step is applied to ensure quality and difficulty of the synthetic questions.

### Figure 6 (p.9) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig06.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p09.png]]*
> [!quote] caption
> (Left) Test scaling of ASearcher-Web-QwQ. Data points are obtained by enforcing different minimum turns.The accuracy is averaged over GAIA, xBench-DeepSearch, and Frames. (Middle)

> [!tip] 技术解读（多模态）
> **Figure description (architecture/components/data flow + key takeaway):**

Figure 6 is a three-panel empirical analysis of ASearcher-Web-QwQ supporting the section's claim that scaling RL trajectory length is hard.

- **Left panel** – Accuracy (y-axis, ~52–55%) vs. enforced minimum tool-call turns (x-axis, 6–12). Accuracy rises monotonically with more tool calls, justifying long-horizon training.
- **Middle panel** – #Tool calls per trajectory vs. training step (0–200), tracking MIN/MAX/AVG. The MAX curve climbs to ~70 while AVG stays near 10, revealing a widening gap between long and short rollouts.
- **Right panel** – #Generated tokens per trajectory (log scale, 10³–10⁵) vs. training step. MAX trajectories reach ~10⁵ tokens while MIN stays ~10³, a ~100× spread.

**Key takeaway:** Long-horizon agentic RL suffers from extreme runtime variance — the longest trajectories consume ~100× more tokens than the shortest, making synchronous batched training inefficient and motivating the asynchronous design introduced later.

**Caption (verbatim):**

"Figure 6: (Left) Test scaling of ASearcher-Web-QwQ. Data points are obtained by enforcing different minimum turns. The accuracy is averaged over GAIA, xBench-DeepSearch, and Frames. (Middle) Number of tool calls versus training steps. During training time, long trajectories require much more tool calls than short ones. (Right) Number of generated tokens versus training steps. The number of output tokens exhibits significant variance, with long trajectories exceeding short ones by up to two orders of magnitude."

### Figure 7 (p.10) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig07.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p10.png]]*
> [!quote] caption
> One-Step-off RL v.s. Fully Asynchronous RL. In batch generation systems, a batch should wait for the longest trajectory, leading to significant GPU idle time. In contrast, fully asynchronous RL achieves faster training than batch generation RL by fully decoupling training and trajectory generation, achieving near-full resource utilization for trajectory generation. example for batch generation RL 

> [!tip] 技术解读（多模态）
> ## Figure 7 Description

The figure compares two RL training paradigms for agentic LLM systems:

**One-Step-Off RL (top):** Trajectories (Traj 1–12) execute in parallel with alternating LLM Gen and Tool calls. While training for step N overlaps with step N+1 generation, the batch is blocked by the slowest trajectory (Traj 7), producing a visible "Idle Time" gap before Train Step N+1 begins.

**Fully Async RL (bottom):** All trajectories run independently with no synchronization barrier. Training steps (N, N+1, N+2) launch as soon as any sufficient batch is ready — Traj 7 can span multiple training versions while other trajectories continuously feed new batches.

**Key Takeaway:** Fully decoupling trajectory rollout from model updates eliminates GPU idle time caused by long-running trajectories, yielding near-full resource utilization and faster training than batch-generation alternatives.

*(120 words)*

## Caption (verbatim)

**Figure 7:** One-Step-off RL v.s. Fully Asynchronous RL. In batch generation systems, a batch should wait for the longest trajectory, leading to significant GPU idle time. In contrast, fully asynchronous RL achieves faster training than batch generation RL by fully decoupling training and trajectory generation, achieving near-full resource utilization for trajectory generation.

### Figure 8 (p.14) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig08.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p14.png]]*
> [!quote] caption
> Comparison of the performance of QwQ-32B agent before and after RL Training. training pipeline trains the agent to learn complex search strategies to perform precise searches, extract key information, and resolve conflict information.

> [!tip] 技术解读（多模态）
> **Main figure description**

Figure 8 contains two grouped bar charts comparing three variants of the QwQ-32B agent across three benchmarks (GAIA, xBench-DeepSearch, Frames). The left panel plots Avg@4 Score (%) and the right panel plots Pass@4 Score (%). Each benchmark group contains three bars: "Before RL" (tan), "ASearcher-v1 (ours)" (coral), and "ASearcher-v2 (ours)" (purple).

**Data flow**: Base model → RL training (v1 then v2) → evaluation on three deep-research test suites via two scoring protocols.

**Key takeaway (≤120 words):** RL training delivers monotonic gains on every benchmark under both metrics. ASearcher-v2 uniformly dominates v1 and the un-tuned baseline. The largest absolute improvement appears on xBench-DeepSearch, where Avg@4 nearly doubles (28.7 → 42.1 → 51.1) and Pass@4 climbs from 51.0 to 75.0. On Frames the gains are smaller (already a strong baseline), suggesting RL helps most where the base agent struggles most. The Pass@4 gaps being larger than Avg@4 gaps indicates RL also improves the agent's consistency/reliability, not just peak performance.

**Caption (verbatim):** Figure 8: Comparison of the performance of QwQ-32B agent before and after RL Training.

### Figure 9 (p.15) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig09.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p15.png]]*
> [!quote] caption
> Training Dynamics of ASearcher-Local-7B.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Architecture/Components:** Two tri-panel figures (Fig. 9: ASearcher-Local-7B; Fig. 10: ASearcher-Local-14B), each containing three side-by-side line plots sharing the x-axis (Training Step: 0–300+ for 7B, 0–225 for 14B). Y-axes track per-trajectory metrics: (a) # Generated Tokens (up to 1000/800), (b) # Search Queries (0–6), and (c) # URL Accesses (0–0.4 / 0–2.5). Red curves denote averages over a gray grid.

**Data flow:** Training step progresses → measured agent behavior (token output length, search-tool usage, web retrieval) evolves, revealing the learning trajectory.

**Key Takeaway:** Both models exhibit emergent scaling — generated tokens and search-query counts grow over training (U-shaped for tokens: initial dip, then rise), indicating RL autonomously induces longer, more tool-intensive reasoning chains rather than requiring hand-engineered trajectories.

## Caption Verbatim

**Figure 9:** Figure 9: Training Dynamics of ASearcher-Local-7B.

**Figure 10:** Figure 10: Training Dynamics of ASearcher-Local-14B.

Subplot labels (verbatim):
- (a) Generated Tokens
- (b) Search Queries
- (c) URL Accesses

### Figure 10 (p.15) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig10.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p15.png]]*
> [!quote] caption
> Training Dynamics of ASearcher-Local-14B. 15

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Architecture/Components:** Two tri-panel figures (Fig. 9: ASearcher-Local-7B; Fig. 10: ASearcher-Local-14B), each containing three side-by-side line plots sharing the x-axis (Training Step: 0–300+ for 7B, 0–225 for 14B). Y-axes track per-trajectory metrics: (a) # Generated Tokens (up to 1000/800), (b) # Search Queries (0–6), and (c) # URL Accesses (0–0.4 / 0–2.5). Red curves denote averages over a gray grid.

**Data flow:** Training step progresses → measured agent behavior (token output length, search-tool usage, web retrieval) evolves, revealing the learning trajectory.

**Key Takeaway:** Both models exhibit emergent scaling — generated tokens and search-query counts grow over training (U-shaped for tokens: initial dip, then rise), indicating RL autonomously induces longer, more tool-intensive reasoning chains rather than requiring hand-engineered trajectories.

## Caption Verbatim

**Figure 9:** Figure 9: Training Dynamics of ASearcher-Local-7B.

**Figure 10:** Figure 10: Training Dynamics of ASearcher-Local-14B.

Subplot labels (verbatim):
- (a) Generated Tokens
- (b) Search Queries
- (c) URL Accesses

### Figure 11 (p.16) ⭐深度解读
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig11.png]]
*整页渲染: ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p16.png]]*
> [!quote] caption
> Left: Word count of reflective keywords during training time. Right: Word count of keywords indicating explicit reference of external information. sophisticated prompt-based agents powered by Large Reasoning Models through offline RL [19], SFT on simulated trajectories with real-world web data [32, 17], and constructing challenging QAs for RL training. [34].

> [!tip] 技术解读（多模态）
> **Figure 11 Description (≤120 words):**

Figure 11 contains two side-by-side line plots tracking keyword frequency per training trajectory across ~420 training steps. The **left panel** plots six reflective keywords (search, alternatively, wait, check, confirm, however) — "search" dominates, climbing sharply after step ~250 to ~8k occurrences/trajectory, with "alternatively" as the secondary rising signal. The **right panel** plots five explicit reference keywords (doc, mention, source, earlier, previous) — "doc" rises most steeply post-step 250 to ~2.5k, followed by "previous." Both plots share axes (Training Step × Word Count/Traj) and exhibit a synchronized inflection near step 250, indicating emergent behaviors.

**Key takeaway:** Reflective and external-reference behaviors co-emerge around training step 250, with "search" and "doc" usage growing most aggressively — suggesting RL training progressively induces more deliberate, source-grounded reasoning patterns.

**Caption (verbatim):**

Figure 11: Left: Word count of reflective keywords during training time. Right: Word count of keywords indicating explicit reference of external information.

### Figure 12 (p.20) ⭐深度解读
![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p20.png]]
> [!quote] caption
> A case study on a complex query from GAIA. Search-R1-32B is unable to break down the complex question and has severe hallucinations. Search-o1 (QwQ) can identify the corrects articles through extensive tool calls, but easily misses key information and fails to verify wrong conclusions. Our end-to-end RL agent, ASearcher-Web-QwQ, exhibits key behaviors featuring

> [!tip] 技术解读（多模态）
> **Figure Description:**

The diagram presents a three-column case study comparing agents on a complex multi-hop query about a "C1 genus named for Copenhagen" alvei species. Each column traces a parallel pipeline: **Question** (Q) → **Search operations** (focused search, hallucination, mis-key info, comparative analysis, cross-doc inference) → **Retrieved documents** (D) → **Reasoning thoughts** (T) → **Final Answer** (A). Left: Search-R1-32B fails with hallucinations (❌ "Goats"). Middle: Search-o1 (QwQ) fails due to missing info and unverified conclusions (❌ "Goats"). Right: ASearcher-Web-QwQ succeeds (✅ "Mice") by combining precise extraction, cross-document inference, and confirmation.

**Key Takeaway:** End-to-end RL training instills Search Intelligence behaviors—uncertainty-aware reasoning, precise extraction from noisy content, cross-document inference, and rigorous confirmation—that baseline RAG/agentic methods systematically lack.

**Caption (verbatim):**

Figure 12: A case study on a complex query from GAIA. Search-R1-32B is unable to break down the complex question and has severe hallucinations. Search-o1 (QwQ) can identify the corrects articles through extensive tool calls, but easily misses key information and fails to verify wrong conclusions. Our end-to-end RL agent, **ASearcher-Web-QwQ**, exhibits key behaviors featuring Search Intelligence: *uncertainty-aware reasoning* (list and examine candidate answers), *precise extraction from noisy contents, cross-document inference,* and *rigorous confirmation*.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
J(\pi) = \mathbb{E}\left[\sum_{t=0}^{\infty} \gamma^t R(s_t, a_t) \bigg| a_t \sim \pi(s_t)\right]
$$

$$
\mathcal J_{GRPO}(\theta)=\mathbb E_{x\sim \mathcal D,\{\tau_i\}_{i=1}^G\sim\pi_{\theta_{old}}(\cdot|x)}\Bigg[&\frac{1}{G}\sum_{i=1}^G\frac{1}{\sum_{t=0}^{T_i-1}|a^i_t|}\sum_{t=0}^{T_i-1}\sum_{j=1}^{|a_t^i|}\min\Bigg( \frac{\pi_\theta(a_{t,j}^i|s_t,a_{t,<j}^i)}{\pi_{\theta_{old}}(a_{t,j}^i|s_t,a_{t,<j}^i)}\hat A_{i},\nonumber \\ &\text{clip}\Bigg(\frac{\pi_\theta(a_{t,j}^i|s_t,a_{t,<j}^i)}{\pi_{\theta_{old}}(a_{t,j}^i|s_t,a_{t,<j}^i)},1-\epsilon,1+\epsilon\Bigg)\hat A_{i}\Bigg) \Bigg]
$$

## 技术点深读（DEEP）

![[deep/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl.txt`（66936 字符）供引用检索。