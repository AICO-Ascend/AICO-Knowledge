---
paper_num: "22"
title: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models"
authors: "Reasoning in Open Language Models Zhihong Shao1,2∗†, Peiyi Wang1,3∗†, Qihao Zhu1,3∗†, Runxin Xu1, Junxiao Song1 Xiao Bi1, Haowei Zhang1, Mingchuan Zhang1, Y.K. Li1, Y. Wu1, Daya Guo1∗ 1DeepSeek-AI, 2Tsinghua University, "
date: "2026/1/19"
arxiv: "https://arxiv.org/abs/2402.03300"
pdf: "papers/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models.pdf"
slug: "deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models"
tags: []
---

# DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models

> [!abstract] 摘要（原文）
> 1\. 💡 DeepSeekMath 7B 是一个开放语言模型，通过在DeepSeek-Coder-Base-v1.5 7B基础上进行120B数学相关token的预训练，在MATH benchmark上实现了51.7%的Top1准确率，接近GPT-4和Gemini-Ultra的性能。 2. 🛠️ 模型的出色表现归因于从Common Crawl中精心筛选的120B高质量DeepSeekMath Corpus，以及引入了Group Relative Policy Optimization (GRPO)——一种无需critic模型的PPO变体，显著优化了强化学习资源消耗。 3. 🔬 论文还探讨了Code训练对数学推理的积极作用，并提出了一个统一的RL范式来分析不同算法，指出强化学习主要通过提升Maj@K来增强模型性能，而非直接提升其基础能力。

## 元信息
- **发表日期**: 2026/1/19
- **作者**: Reasoning in Open Language Models Zhihong Shao1,2∗†, Peiyi Wang1,3∗†, Qihao Zhu1,3∗†, Runxin Xu1, Junxiao Song1 Xiao Bi1, Haowei Zhang1, Mingchuan Zhang1, Y.K. Li1, Y. Wu1, Daya Guo1∗ 1DeepSeek-AI, 2Tsinghua University, 
- **arXiv**: https://arxiv.org/abs/2402.03300
- **本地 PDF**: `papers/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models.pdf`
- **页数**: 30

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig01.png]]
*整页渲染: ![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p01.png]]*
> [!quote] caption
> Top1 accuracy of open-source models on the competition-level MATH benchmark

> [!tip] 技术解读（多模态）
> **Figure 1 Description (≤120 words):**

The figure is a time-series scatter plot tracking MATH benchmark Top@1 accuracy of open-source LLMs from early 2023 to January 2024. The X-axis shows dates; the Y-axis shows accuracy (10–50+). Plotted models form an ascending dashed trend line: LLaMA1-65B (~10), WizardMath-70B (~23), Qwen-14B (~25), Mistral-7B (~28), Llemma-34B (~30), Qwen-72B (~35), culminating in **DeepSeekMath-7B** (~51.7, marked by a red star). Three horizontal dashed reference lines denote closed-source baselines: GPT-4 early version (~42), GPT-4 API (~52), and Gemini-Ultra (~53).

**Key takeaway:** A compact 7B open-source model surpassed GPT-4's level on competition-grade math, showing that data curation + targeted RL (GRPO) can close the gap to frontier proprietary systems without tool use or ensembling.

**Caption (verbatim):**
"Figure 1 | Top1 accuracy of open-source models on the competition-level MATH benchmark (Hendrycks et al., 2021) without the use of external toolkits and voting techniques."

### Figure 2 (p.5) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig02.png]]
*整页渲染: ![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p05.png]]*
> [!quote] caption
> An iterative pipeline that collects mathematical web pages from Common Crawl.

> [!tip] 技术解读（多模态）
> **Figure Description**

The figure depicts a four-step iterative pipeline that bootstraps a mathematical web corpus from Common Crawl:

1. **Train a FastText Model** — uses the current *Math Seed* to build a classifier.
2. **Recall Math-Related Webpages From Common Crawl** — applies the fastText model to the *Deduplicated Common Crawl (40B HTML pages)*, retaining top-ranked pages to build the *Math Corpus*.
3. **Discover Math-Related Domains** — clusters the corpus by base URL and flags domains where >10% of pages were recalled (e.g., `mathoverflow.net`).
4. **Annotate Math-Related URL Path From Labelers** — human labelers mark math-specific URL paths within those domains, expanding the seed corpus.

The dashed arrows show feedback from step 4 → step 1, closing the loop for the next iteration.

**Key technical takeaway:** Domain-driven seed enrichment (step 3–4) compensates for fastText's limited positive diversity, yielding 35.5M math pages / 120B tokens after 4 iterations, at which point 98% recall saturation is reached and the loop terminates.

**Caption (verbatim):**
> Figure 2 | An iterative pipeline that collects mathematical web pages from Common Crawl.

### Figure 3 (p.7) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig03.png]]
*整页渲染: ![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p07.png]]*
> [!quote] caption
> Benchmark curves of DeepSeek-LLM 1.3B trained on different mathematical corpora.

> [!tip] 技术解读（多模态）
> ## Figure Description

**Layout:** A 2×2 grid of benchmark curves evaluating DeepSeek-LLM 1.3B trained on four mathematical corpora: **MathPile** (blue), **OpenWebMath** (orange), **Proof-Pile-2** (green), and **DeepSeekMath Corpus** (red).

**Panels (Acc% vs. Training Tokens in B):**
- **GSM8K** (top-left): DeepSeekMath climbs to ~24%, others plateau around 12–14%; MathPile collapses to ~2%.
- **MATH** (top-right): DeepSeekMath reaches ~13%, OpenWebMath/Proof-Pile-2 ~10–11%, MathPile flat at ~3%.
- **CMATH** (bottom-left): DeepSeekMath ~43% vs. ~18% for others; MathPile drops to ~0%.
- **BBH** (bottom-right): DeepSeekMath ~34%, Proof-Pile-2 ~32%, MathPile ~25%.

**Key Technical Takeaway:** DeepSeekMath Corpus demonstrates the **steepest and most sustained learning curve** across all four benchmarks, reaching higher accuracy with continued training, while smaller/English-centric corpora plateau early or even degrade (e.g., MathPile on GSM8K/CMATH) — evidencing the corpus's superior scale and quality.

## Caption (Verbatim)

**Figure 3 | Benchmark curves of DeepSeek-LLM 1.3B trained on different mathematical corpora.**

### Figure 4 (p.13) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig04.png]]
*整页渲染: ![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p13.png]]*
> [!quote] caption
> Demonstration of PPO and our GRPO. GRPO foregoes the value model, instead

> [!tip] 技术解读（多模态）
> ## Figure Description (≤120 words)

The figure contrasts **PPO** (top) and **GRPO** (bottom) RL training pipelines for a query `q`. In **PPO**, a trained Policy Model produces output `o`, which feeds a frozen Reference Model and Reward Model (combined via KL penalty into reward `r`) and a separately trained Value Model producing `v`. Both `r` and `v` flow into a **GAE** (Generalized Advantage Estimation) block yielding advantage `A`, which updates the policy.

In **GRPO**, the policy samples a *group* of outputs `{o₁, …, o_G}` per query. Only frozen Reference and Reward Models are used (with KL applied directly to the loss). Per-sample rewards `{r₁, …, r_G}` are passed to a **Group Computation** block that derives advantages `{A₁, …, A_G}`—no value model or GAE required.

**Key takeaway:** GRPO replaces the learned value function (≈ policy-sized, memory-heavy) with group-relative reward statistics, cutting training cost while exploiting reward models' comparative nature.

## Caption (verbatim)

> **Figure 4 | Demonstration of PPO and our GRPO. GRPO foregoes the value model, instead estimating the baseline from group scores, significantly reducing training resources.**

### Figure 5 (p.19) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig05.png]]
*整页渲染: ![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p19.png]]*
> [!quote] caption
> Performance of the DeepSeekMath-Instruct 1.3B model, which was further trained

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 5):**

Two side-by-side line plots compare four training methods across training steps (0–~8500) on accuracy (%):

- **GSM8K (left):** Y-axis 56–66%
- **MATH (right):** Y-axis 27–30%
- **Four methods plotted:** RFT (purple), Online RFT (green), GRPO+OS (orange), GRPO+PS (blue)

**Data flow:** All methods initialize from the SFT model. RFT/Online RFT use rule-based filtering/rewards, while PPO/GRPO methods use a learned reward model. Outputs sampled either from the frozen SFT model (offline) or the real-time policy model (online) feed back into training.

**Key takeaway:** GRPO variants (especially GRPO+PS, blue) consistently outperform RFT/Online RFT, with GRPO+PS reaching ~66% on GSM8K and ~30% on MATH—demonstrating that online policy sampling with model-based rewards yields superior gains over offline rejection-sampling baselines.

**Caption (verbatim):**

"Figure 5 | Performance of the DeepSeekMath-Instruct 1.3B model, which was further trained using various methods, on two benchmarks."

### Figure 6 (p.20) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig06.png]]
*整页渲染: ![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p20.png]]*
> [!quote] caption
> Performance of iterative reinforcement learning with DeepSeekMath-Instruct 7B on

> [!tip] 技术解读（多模态）
> **Figure 6 Description:**

The figure consists of two side-by-side line plots tracking model accuracy over training steps. The left panel shows GSM8K benchmark (y-axis: 83–89%) and the right shows MATH (y-axis: 47–52%); both share an x-axis of steps (0–5300). Three colored curves represent successive training iterations: Iteration-0 (purple), Iteration-1 (orange), and Iteration-2 (green). Iteration-0 plateaus earliest and lowest on both benchmarks, while Iterations-1 and 2 extend further and reach higher accuracies (~89% on GSM8K, ~52% on MATH).

**Key takeaway:** Iterative reinforcement learning yields substantial performance gains, with the largest jump occurring after the first iteration—suggesting that successive rounds of RL progressively refine the policy beyond the SFT initialization.

**Caption (verbatim):**
"Figure 6 | Performance of iterative reinforcement learning with DeepSeekMath-Instruct 7B on two benchmarks."

### Figure 7 (p.21) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig07.png]]
*整页渲染: ![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p21.png]]*
> [!quote] caption
> The Maj@K and Pass@K of SFT and RL DeepSeekMath 7B on GSM8K and MATH

> [!tip] 技术解读（多模态）
> ## Figure Description (≤120 words)

The figure consists of **two side-by-side line plots** comparing model accuracy on two math benchmarks: **GSM8K** (left) and **MATH** (right). Both plots share an x-axis of "K: number of candidates" on a log scale (1, 4, 8, 16, 32, 64) and a y-axis of accuracy (%). Four curves are plotted: **Maj@K-Instruct (purple), Maj@K-RL (orange), Pass@K-Instruct (green), and Pass@K-RL (blue)**, evaluated on the DeepSeekMath 7B model at temperature 0.7. All curves rise monotonically with K. Pass@K curves (green/blue) climb steeply and converge near the top (~97–99% on GSM8K, ~85–87% on MATH), while Maj@K curves (purple/orange) plateau at lower values. **Key takeaway**: RL boosts Maj@K but not Pass@K, indicating RL sharpens the top-K output distribution rather than expanding the model's underlying capability.

## Caption (verbatim)

**Figure 7 | The Maj@K and Pass@K of SFT and RL DeepSeekMath 7B on GSM8K and MATH (temperature 0.7). It was noted that RL enhances Maj@K but not Pass@K.**

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.6) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab01.png]]
> [!quote] caption
> | Performance of DeepSeek-LLM 1.3B trained on different mathematical corpora, evalu- ated using few-shot chain-of-thought prompting. Corpus sizes are calculated using our tokenizer with a vocabulary size of 100K.

> [!tip] 表格解读（多模态）
> There is no figure in the provided image — only a bulleted list of corpus descriptions, a "Training Setting" paragraph, and **Table 1** (benchmark results). I will therefore describe the table content instead, and transcribe its caption verbatim.

**Description of Table 1 (components / data flow) + key takeaway (≈120 words):**
The table compares a 1.3B-parameter DeepSeek-LLM across five rows (No Math Training baseline, MathPile 8.9B, OpenWebWebMath 13.6B, Proof-Pile-2 51.9B, and the proposed DeepSeekMath Corpus 120.2B tokens). Columns report corpus size and few-shot CoT accuracy on English benchmarks (GSM8K, MATH, OCW, SAT, MMLU-STEM) and Chinese benchmarks (CMATH, Gaokao MathCloze, Gaokao MathQA). The data flow is: base LLM → continued pretraining on a math corpus → evaluation. **Key takeaway:** simply scaling existing open math corpora plateaus (e.g., Proof-Pile-2 yields only 14.3% GSM8K vs. 11.5% for the smaller OpenWebMath), whereas the curated 120.2B DeepSeekMath Corpus more than doubles gains (23.8% GSM8K, 41.5% CMATH, 56.3% SAT) — showing corpus *quality/selection* matters far more than raw token count.

**Caption (verbatim):**
"Table 1 | Performance of DeepSeek-LLM 1.3B trained on different mathematical corpora, evaluated using few-shot chain-of-thought prompting. Corpus sizes are calculated using our tokenizer with a vocabulary size of 100K."

### Table 2 (p.8) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab02.png]]
> [!quote] caption
> | Comparisons between DeepSeekMath-Base 7B and strong base models on English and Chinese mathematical benchmarks. Models are evaluated with chain-of-thought prompting. Minerva results are quoted from Lewkowycz et al. (2022a).

> [!tip] 表格解读（多模态）
> **Note:** No figure (image/diagram) has been provided in this input — only the caption for **Table 2**. Without the underlying visual, I cannot describe architectural components or data flow. The caption itself contains no figure content to summarize beyond what is transcribed below.

---

**Caption (verbatim transcription):**

Table 2 | Comparisons between DeepSeekMath-Base 7B and strong base models on English and Chinese mathematical benchmarks. Models are evaluated with chain-of-thought prompting. Minerva results are quoted from Lewkowycz et al. (2022a).

---

If you intended to share a figure (e.g., a model architecture diagram or a results plot), please re-upload the image and I'll provide the requested description and transcription.

### Table 3 (p.9) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab03.png]]
> [!quote] caption
> | Few-shot evaluation of base models’ ability to solve mathematical problems using tools and the ability to conduct informal-to-formal theorem proving in Isabelle.

> [!tip] 表格解读（多模态）
> **Description (Table 3):**

The table presents a few-shot benchmark comparison across four evaluation tracks: two **tool-augmented math problem-solving** tasks (GSM8K+Python, MATH+Python, using Program-of-Thought) and two **informal-to-formal theorem-proving** tasks (miniF2F-valid and miniF2F-test, compiled to Isabelle). Rows report exact-match accuracy for five base models spanning 7B–34B parameters: Mistral, CodeLlama (7B/34B), Llemma (7B/34B), and DeepSeekMath-Base (7B).

**Key takeaway:** DeepSeekMath-Base 7B scores 66.9% / 31.4% / 25.8% / 24.6%, surpassing the 4.9× larger Llemma 34B (64.6% / 26.3% / 21.0% / 21.3%) on every benchmark—demonstrating that math-pretraining, not scale, drives tool-use and proof competence. (99 words)

**Caption (verbatim):**

Table 3 | Few-shot evaluation of base models' ability to solve mathematical problems using tools and the ability to conduct informal-to-formal theorem proving in Isabelle.

### Table 4 (p.9) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab04.png]]
> [!quote] caption
> | Evaluation on natural language understanding, reasoning, and code benchmarks. DeepSeek-Coder-Base-v1.5 † is the checkpoint right before learning rate decay, which is used to train DeepSeekMath-Base. On MMLU and BBH, we use few-shot chain-of-thought prompting. On HumanEval and MBPP, we evaluate mod

> [!tip] 表格解读（多模态）
> The image contains two tables (no architectural figure present):

**Table 3** benchmarks base models on math reasoning (GSM8K+Python, MATH+Python) and formal proof autoformalization (miniF2F-valid/test). It compares Mistral 7B, CodeLlama 7B/34B, Llemma 7B/34B, and DeepSeekMath-Base 7B at a glance.

**Key takeaway:** DeepSeekMath-Base 7B achieves the top score across all four tasks—66.9% (GSM8K), 31.4% (MATH), 25.8% (miniF2F-valid), 24.6% (miniF2F-test)—surpassing models 5× its size (e.g., Llemma 34B at 64.6% / 26.3%) and demonstrating strong informal-to-formal proving via few-shot prompting + Sledgehammer.

**Table 4** contrasts Mistral 7B, DeepSeek-Coder-Base-v1.5/v1.5†, and DeepSeekMath-Base 7B on general reasoning (MMLU, BBH) and code (HumanEval, MBPP), showing DeepSeekMath-Base matches/exceeds its coder predecessor on coding while gaining reasoning.

---

**Captions (verbatim):**

> Table 3 | Few-shot evaluation of base models' ability to solve mathematical problems using tools and the ability to conduct informal-to-formal theorem proving in Isabelle.

> Table 4 | Evaluation on natural language understanding, reasoning, and code benchmarks. DeepSeek-Coder-Base-v1.5† is the checkpoint right before learning rate decay, which is used to train DeepSeekMath-Base. On MMLU and BBH, we use few-shot chain-of-thought prompting. On HumanEval and MBPP, we evaluate model performance under the zero-shot setting and a few-shot setting, respectively.

### Table 5 (p.12) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab05.png]]
> [!quote] caption
> | Performance of Open- and Closed-Source models with both Chain-of-Thought and Tool-Integrated Reasoning on English and Chinese Benchmarks. Scores in gray denote majority votes with 32 candidates; The others are Top1 scores. DeepSeekMath-RL 7B beats all open- source models from 7B to 70B, as well as

> [!tip] 表格解读（多模态）
> ## Main Figure Description

**Note:** The provided content is a table caption (Table 5), not a figure caption.

This Table 5 presents a comparative benchmark evaluation of open-source and closed-source language models across English and Chinese reasoning benchmarks. The architecture is a standard results matrix where rows represent models (e.g., DeepSeekMath-RL 7B, DeepSeekMath-Instruct 7B, and various open-source 7B–70B baselines plus closed-source competitors) and columns represent benchmarks evaluated under two reasoning regimes: **Chain-of-Thought (CoT)** and **Tool-Integrated Reasoning (TIR)**. Cell values are scores displayed in two formats: gray-highlighted entries denote majority votes from 32 candidate samples, while others are Top-1 (greedy) scores.

**Key Technical Takeaway:** DeepSeekMath-RL 7B — despite being RL-tuned only on GSM8K and MATH CoT instruction data — outperforms every open-source 7B–70B model and most closed-source models on all benchmarks, including Chinese and TIR evaluations. This demonstrates that RL post-training on a narrow math reasoning distribution generalizes broadly across languages and reasoning paradigms. (≈117 words)

## Caption (Verbatim)

> Table 5 | Performance of Open- and Closed-Source models with both Chain-of-Thought and Tool-Integrated Reasoning on English and Chinese Benchmarks. Scores in gray denote majority votes with 32 candidates; The others are Top1 scores. DeepSeekMath-RL 7B beats all open-source models from 7B to 70B, as well as the majority of closed-source models. Although DeepSeekMath-RL 7B is only further trained on chain-of-thought-format instruction tuning data of GSM8K and MATH, it improves over DeepSeekMath-Instruct 7B on all benchmarks.

### Table 6 (p.16) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab06.png]]
> [!quote] caption
> | Investigation of how code affects mathematical reasoning under different training settings. We experiment with DeepSeek-LLM 1.3B, and evaluate its mathematical reasoning performance without and with tool use via few-shot chain-of-thought prompting and few-shot program-of-thought prompting, respect

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**

Table 6 evaluates DeepSeek-LLM 1.3B under four training configurations: (1) **Two-stage code-first**: 400B code tokens → 150B math tokens; (2) **Two-stage general-first**: 400B general tokens → 150B math tokens (control); (3) **One-stage math-only**: 150B math tokens; (4) **One-stage mixed**: 400B code + 150B math tokens together. Evaluation tests mathematical reasoning both *without* tools (few-shot CoT prompting) and *with* tools (few-shot PoT prompting that generates Python). **Key takeaway**: Code training substantially boosts math performance in both two-stage and one-stage regimes, with code-first training improving program-aided GSM8K/MATH accuracy. Notably, one-stage mixed training not only preserves coding ability but also mitigates catastrophic forgetting that two-stage training causes — yielding synergistic gains across reasoning modes.

**Caption (verbatim):**

Table 6 | Investigation of how code affects mathematical reasoning under different training settings. We experiment with DeepSeek-LLM 1.3B, and evaluate its mathematical reasoning performance without and with tool use via few-shot chain-of-thought prompting and few-shot program-of-thought prompting, respectively.

### Table 7 (p.17) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab07.png]]
> [!quote] caption
> | Investigation of how different settings of code and math training affect model perfor- mance of language understanding, reasoning, and coding. We experiment with DeepSeek-LLM 1.3B. We evaluate the models on MMLU and BBH using few-shot chain-of-thought prompting. On HumanEval and MBPP, we conduct z

> [!tip] 表格解读（多模态）
> **Description:**

This is a results table (Table 7) rather than an architecture/data-flow figure, so it has no diagram of components or pipelines. Instead, it presents an ablation comparing how varying the proportion of code-related training data and math corpus (ArXiv) affects downstream performance of the DeepSeek-LLM 1.3B model. Rows represent model variants differing in training-data mix; columns report accuracy across English benchmarks (GSM8K, MATH, OCW, SAT, MMLU STEM) and Chinese benchmarks (CMATH, Gaokao MathCloze, Gaokao MathQA), with MMLU and BBH evaluated via few-shot chain-of-thought, HumanEval zero-shot, and MBPP few-shot.

**Key takeaway:** Increasing code data improves coding/reasoning but does not transfer to math or general language understanding—math corpus inclusion is required for math gains, indicating code and math skills are largely orthogonal.

**Caption (verbatim):**

Table 7 | Investigation of how different settings of code and math training affect model performance of language understanding, reasoning, and coding. We experiment with DeepSeek-LLM 1.3B. We evaluate the models on MMLU and BBH using few-shot chain-of-thought prompting. On HumanEval and MBPP, we conduct zero-shot and few-shot evaluations, respectively.

### Table 8 (p.17) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab08.png]]
> [!quote] caption
> | Effect of math training on different arXiv datasets. Model performance is evaluated with few-shot chain-of-thought prompting.

> [!tip] 表格解读（多模态）
> **Description:**

The table is a small results matrix (3 rows × 2 metric columns) reporting model accuracy on the miniF2F mathematical-reasoning benchmark under three pretraining-corpus conditions for the arXiv slice. Columns are `miniF2F-valid` and `miniF2F-test`; rows compare a baseline with **No Math Training** (20.1% / 21.7%) against two math-augmented variants—**MathPile** (16.8% / 16.4%) and **ArXiv-RedPajama** (14.8% / 11.9%). There is no architecture or data-flow diagram; it is purely an ablation-style comparison table.

**Key takeaway:** Counter-intuitively, injecting either dedicated math corpus (MathPile) or general arXiv text (ArXiv-RedPajama) *degrades* miniF2F performance relative to the plain baseline—ArXiv-RedPajama dropping accuracy by ~5–10 points—suggesting these math/training mixes misalign with the formal-proof distribution miniF2F probes.

**Caption (verbatim):**

> **Table 8 | Effect of math training on different arXiv datasets. Model performance is evaluated with few-shot chain-of-thought prompting.**

### Table 9 (p.17) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab09.png]]
> [!quote] caption
> | Effect of math training on different arXiv corpora, the base model being DeepSeek- Coder-Base-v1.5 7B. We evaluate informal-to-formal proving in Isabelle.

> [!tip] 表格解读（多模态）
> I'm unable to describe a "main figure" here because **no figure is included in the image you shared** — only the caption of Table 9 and a paragraph of body text from what appears to be the DeepSeek-Coder / DeepSeekMath paper. There are no visual elements (no diagram, no architecture, no data flow) for me to analyze.

If you're expecting a figure, it may have been cropped, mis-uploaded, or the document only contained this caption + paragraph on the page. Could you re-share the image with the actual figure visible?

### Verbatim transcription of the provided text

**Table 9 caption:**
> Table 9 | Effect of math training on different arXiv corpora, the base model being DeepSeek-Coder-Base-v1.5 7B. We evaluate informal-to-formal proving in Isabelle.

**Body paragraph:**
> Code training also improves mathematical reasoning without tool use. Under the two-stage training setting, the initial stage of code training already results in moderate enhancements. It also boosts the efficiency of the subsequent math training, eventually leading to the best performance. However, combining code tokens and math tokens for one-stage training compromises mathematical reasoning without tool use. One conjecture is that DeepSeek-LLM 1.3B, due to its limited scale, lacks the capacity to fully assimilate both code and mathematical data simultaneously.

### Quick text-only takeaway (since no figure exists to describe)
- **Two-stage training** (code → math) outperforms **one-stage** (code+math mixed) for tool-free mathematical reasoning, likely because the 1.3B/7B scale is too small to absorb both modalities simultaneously.

### Table 10 (p.19) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab10.png]]
> [!quote] caption
> | The data source and gradient coefficient of different methods. 𝑃 𝑠𝑓𝑡 denotes the data distribution of supervised fine-tuning datasets. 𝜋 𝜃 𝑠𝑓𝑡 and 𝜋 𝜃 denote the supervised fine-tuned model and the real-time policy model during the online training process, respectively.

> [!tip] 表格解读（多模态）
> **Description:**

The figure presents two side-by-side line plots comparing four reinforcement learning fine-tuning methods—**RFT** (purple), **Online RFT** (green), **GRPO+OS** (orange), and **GRPO+PS** (blue)—across two math reasoning benchmarks: **GSM8K** (left, scores ~63–66) and **MATH** (right, scores ~26–31). Each curve traces performance over training, with GRPO+PS (blue) consistently achieving the highest and most stable scores on both benchmarks, while Online RFT (green) and RFT (purple) lag behind, often near or at the bottom of the visible range. Per the accompanying notation, the methods differ in their data source distribution (P_sft vs. online rollouts) and gradient weighting between the supervised-fine-tuned model π_θ_sft and the real-time policy π_θ.

**Key technical takeaway:** Using the online policy's data distribution together with a positive-similarity (PS) gradient coefficient against π_θ_sft yields the best reasoning performance, indicating that mixing a controlled reference term into the GRPO objective accelerates convergence.

**Caption (verbatim):**

> Table 10 | The data source and gradient coefficient of different methods. P_sft denotes the data distribution of supervised fine-tuning datasets. π_θ_sft and π_θ denote the supervised fine-tuned model and the real-time policy model during the online training process, respectively.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\footnotesize \mathcal{J}_{PPO}(\theta) = \mathbb{E}{[q \sim P(Q), o \sim \pi_{\theta_{old}}(O|q)]} \frac{1}{|o|} \sum_{t=1}^{|o|} \min \left[ \frac{\pi_\theta(o_{t} | q, o_{<t})}{\pi_{\theta_{old}}(o_{t} | q, o_{<t})} A_{t}, \text{clip} \left( \frac{\pi_\theta(o_{t} | q, o_{<t})}{\pi_{\theta_{old}}(o_{t} | q, o_{<t})}, 1 - \epsilon, 1 + \epsilon \right) A_{t} \right] ,
$$

$$
r_{t} = r_\phi(q, o_{\le t}) - \beta \log\frac{\pi_{\theta}(o_{t}|q, o_{<t})}{\pi_{ref}(o_{t}|q, o_{<t})},
$$

$$
\footnotesize \begin{split} \mathcal{J}_{GRPO}(\theta) &= \mathbb{E}{[q \sim P(Q), \{o_i\}_{i=1}^G \sim \pi_{\theta_{old}}(O|q)]} \\ & \frac{1}{G}\sum_{i=1}^G\frac{1}{|o_i|} \sum_{t=1}^{|o_i|} \left\{ \min \left[ \frac{\pi_\theta(o_{i,t} | q, o_{i,<t})}{\pi_{\theta_{old}}(o_{i,t} | q, o_{i,<t})} \hat{A}_{i,t}, \text{clip} \left( \frac{\pi_\theta(o_{i,t} | q, o_{i,<t})}{\pi_{\theta_{old}}(o_{i,t} | q, o_{i,<t})}, 1 - \epsilon, 1 + \epsilon \right) \hat{A}_{i,t} \right] - \beta \mathbb{D}_{KL}\left[\pi_{\theta} || \pi_{ref}\right]\right\} , \end{split}
$$

$$
\small \mathbb{D}_{KL}\left[\pi_{\theta} || \pi_{ref}\right] = \frac{\pi_{ref}(o_{i,t}|q,o_{i,<t})}{\pi_{\theta}(o_{i,t}|q,o_{i,<t})}- \log\frac{\pi_{ref}(o_{i,t}|q,o_{i,<t})}{\pi_{\theta}(o_{i,t}|q,o_{i,<t})} - 1,
$$

$$
\nabla_{\theta}\mathcal{J}_{\textcolor{red}{\mathcal{A}}}(\theta) = \mathbb{E}[\underbrace{(q,o) \sim \textcolor{red}{\mathcal{D}}}_{Data \ Source}]\left( \frac{1}{|o|} \sum_{t=1}^{|o|} \underbrace{GC_{{\mathcal{A}}}(q, o, t, \textcolor{red}{\pi_{{rf}}})}_{Gradient \ Coefficient} \nabla_{\theta}\log \pi_{\theta}(o_t | q, o_{<t})\right).
$$

$$
\mathcal{J}_{SFT}(\theta)=\mathbb{E}[q, o \sim P_{sft}(Q, O)]\left(\frac{1}{|o|}\sum_{t=1}^{|o|} \log \pi_\theta(o_t | q, o_{<t})\right).
$$

$$
\nabla_{\theta}\mathcal{J}_{SFT} = \mathbb{E}[q, o \sim P_{sft}(Q, O)]\left(\frac{1}{|o|}\sum_{t=1}^{|o|} \nabla_{\theta} \log \pi_\theta(o_{t} | q, o_{<t})\right).
$$

$$
\mathcal{J}_{RFT}(\theta)= \mathbb{E}[q \sim P_{sft}(Q), o \sim \pi_{sft}(O|q)]\left( \frac{1}{|o|}\sum_{t=1}^{|o|} \mathbb{I}(o) \log \pi_\theta(o_{t} | q, o_{<t})\right).
$$

$$
\nabla_{\theta}\mathcal{J}_{RFT}(\theta)= \mathbb{E}[{q \sim P_{sft}(Q), o \sim \pi_{sft}(O|q)}]\left( \frac{1}{|o|}\sum_{t=1}^{|o|} {\mathbb{I}(o)} \nabla_{\theta}\log \pi_\theta(o_{t} | q, o_{<t})\right).
$$

$$
GC_{RFT}(q, o, t) = \mathbb{I}(o)=\left\{ \begin{aligned} 1 & & {\rm the \ answer \ of \ o \ is \ correct} \\ 0 & & {\rm the \ answer \ of \ o \ is \ incorrect} \\ \end{aligned} \right.
$$

$$
\nabla_{\theta}\mathcal{J}_{OnRFT}(\theta)= \mathbb{E}[{q \sim P_{sft}(Q), o \sim \pi_{\theta}(O|q)}]\left( \frac{1}{|o|}\sum_{t=1}^{|o|} {\mathbb{I}(o)} \nabla_{\theta}\log \pi_\theta(o_{t} | q, o_{<t})\right).
$$

$$
\footnotesize \begin{split} \mathcal{J}_{DPO}(\theta) = \mathbb{E}{[q \sim P_{sft}(Q), o^+, o^- \sim \pi_{sft}(O|q)]} \log \sigma \left( \beta \frac{1}{|o^+|}\sum_{t=1}^{|o^+|} \log \frac{\pi_{\theta}(o^+_t | q, o^+_{<t})}{\pi_{\text{ref}}(o^+_t | q, o^+_{<t})} - \beta \frac{1}{|o^-|}\sum_{t=1}^{|o^-|} \log \frac{\pi_{\theta}(o^-_{<t} | q, o^-_{<t})}{\pi_{\text{ref}}(o^-_{<t} | q,o^-_{<t})} \right) \end{split}
$$

$$
\footnotesize \begin{split} \nabla_{\theta}\mathcal{J}_{DPO}(\theta) = \mathbb{E}{[q \sim P_{sft}(Q), o^+, o^- \sim \pi_{sft}(O|q)]} & \left( \frac{1}{|o^+|}\sum_{t=1}^{|o^+|} GC_{DPO} (q,o,t) \nabla_{\theta}\log\pi_{\theta}(o^+_t | q, o^+_{<t}) \right. \\ - & \left. \frac{1}{|o^-|}\sum_{t=1}^{|o^-|} GC_{DPO} (q,o,t) \nabla_{\theta}\log\pi_{\theta}(o^-_t | q, o^-_{<t}) \right) \end{split}
$$

$$
\footnotesize GC_{DPO}(q,o,t) = \sigma\left(\beta\log \frac{\pi_{\theta}(o^-_t | q, o^-_{<t})}{\pi_{\text{ref}}(o^-_t | q, o^-_{<t})} - \beta\log \frac{\pi_{\theta}(o^+_t | q, o^+_{<t})}{\pi_{\text{ref}}(o^+_t | q, o^+_{<t})}\right)
$$

$$
\footnotesize \mathcal{J}_{PPO}(\theta) = \mathbb{E}{[q \sim P_{sft}(Q), o \sim \pi_{\theta_{old}}(O|q)]} \frac{1}{|o|} \sum_{t=1}^{|o|} \min \left[ \frac{\pi_\theta(o_{t} | q, o_{<t})}{\pi_{\theta_{old}}(o_{t} | q, o_{<t})} A_{t}, \text{clip} \left( \frac{\pi_\theta(o_{t} | q, o_{<t})}{\pi_{\theta_{old}}(o_{t} | q, o_{<t})}, 1 - \epsilon, 1 + \epsilon \right) A_{t} \right].
$$

$$
\footnotesize \begin{split} \nabla_{\theta}\mathcal{J}_{PPO}(\theta) = \mathbb{E}{[q \sim P_{sft}(Q), o \sim \pi_{\theta_{old}}(O|q)]} \frac{1}{|o|} \sum_{t=1}^{|o|} A_t \nabla_{\theta}\log \pi_\theta(o_{t} | q, o_{<t}) \end{split}
$$

$$
GC_{PPO}(q, o, t, \pi_{\theta_{rm}}) = A_t,
$$

$$
\footnotesize \begin{split} \mathcal{J}_{GRPO}(\theta) &= \mathbb{E}{[q \sim P_{sft}(Q), \{o_i\}_{i=1}^G \sim \pi_{\theta_{old}}(O|q)]} \\ & \frac{1}{G}\sum_{i=1}^G\frac{1}{|o_i|} \sum_{t=1}^{|o_i|} \left[\frac{\pi_\theta(o_{i,t} | q, o_{i,<t})}{\pi_{\theta_{old}}(o_{i,t} | q, o_{i,<t})} \hat{A}_{i,t} - \beta (\frac{\pi_{ref}(o_{i,t}|q,o_{i,<t})}{\pi_{\theta}(o_{i,t}|q,o_{i,<t})}- \log\frac{\pi_{ref}(o_{i,t}|q,o_{i,<t})}{\pi_{\theta}(o_{i,t}|q,o_{i,<t})} - 1)\right]. \end{split}
$$

$$
\footnotesize \begin{split} \nabla_{\theta}\mathcal{J}_{GRPO}(\theta) & = \mathbb{E}{[q \sim P_{sft}(Q), \{o_i\}_{i=1}^G \sim \pi_{\theta_{old}}(O|q)]} \\ & \frac{1}{G}\sum_{i=1}^G\frac{1}{|o_i|} \sum_{t=1}^{|o_i|} \left[\hat{A}_{i,t} + \beta \left(\frac{\pi_{ref}(o_{i,t}|o_{i,<t})}{\pi_{\theta}(o_{i,t}|o_{i,<t})} - 1\right)\right] \nabla_{\theta}\log \pi_\theta(o_{i,t} | q, o_{i,<t}). \end{split}
$$

$$
\footnotesize GC_{GRPO}(q, o, t, \pi_{\theta_{rm}}) = \hat{A}_{i,t} + \beta \left(\frac{\pi_{ref}(o_{i,t}|o_{i,<t})}{\pi_{\theta}(o_{i,t}|o_{i,<t})} - 1\right),
$$

## 技术点深读（DEEP）

![[deep/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models.txt`（81353 字符）供引用检索。