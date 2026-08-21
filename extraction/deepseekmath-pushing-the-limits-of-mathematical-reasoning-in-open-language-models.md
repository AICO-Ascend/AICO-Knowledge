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
![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p01.png]]
> [!quote] caption
> Top1 accuracy of open-source models on the competition-level MATH benchmark

> [!tip] 技术解读（多模态）
> **Figure 1 Description (≤120 words):**

The figure is a time-series scatter plot tracking MATH benchmark Top@1 accuracy of open-source LLMs from early 2023 to January 2024. The X-axis shows dates; the Y-axis shows accuracy (10–50+). Plotted models form an ascending dashed trend line: LLaMA1-65B (~10), WizardMath-70B (~23), Qwen-14B (~25), Mistral-7B (~28), Llemma-34B (~30), Qwen-72B (~35), culminating in **DeepSeekMath-7B** (~51.7, marked by a red star). Three horizontal dashed reference lines denote closed-source baselines: GPT-4 early version (~42), GPT-4 API (~52), and Gemini-Ultra (~53).

**Key takeaway:** A compact 7B open-source model surpassed GPT-4's level on competition-grade math, showing that data curation + targeted RL (GRPO) can close the gap to frontier proprietary systems without tool use or ensembling.

**Caption (verbatim):**
"Figure 1 | Top1 accuracy of open-source models on the competition-level MATH benchmark (Hendrycks et al., 2021) without the use of external toolkits and voting techniques."

### Figure 2 (p.5) ⭐深度解读
![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p05.png]]
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
![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p07.png]]
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
![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p13.png]]
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
![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p19.png]]
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
![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p20.png]]
> [!quote] caption
> Performance of iterative reinforcement learning with DeepSeekMath-Instruct 7B on

> [!tip] 技术解读（多模态）
> **Figure 6 Description:**

The figure consists of two side-by-side line plots tracking model accuracy over training steps. The left panel shows GSM8K benchmark (y-axis: 83–89%) and the right shows MATH (y-axis: 47–52%); both share an x-axis of steps (0–5300). Three colored curves represent successive training iterations: Iteration-0 (purple), Iteration-1 (orange), and Iteration-2 (green). Iteration-0 plateaus earliest and lowest on both benchmarks, while Iterations-1 and 2 extend further and reach higher accuracies (~89% on GSM8K, ~52% on MATH).

**Key takeaway:** Iterative reinforcement learning yields substantial performance gains, with the largest jump occurring after the first iteration—suggesting that successive rounds of RL progressively refine the policy beyond the SFT initialization.

**Caption (verbatim):**
"Figure 6 | Performance of iterative reinforcement learning with DeepSeekMath-Instruct 7B on two benchmarks."

### Figure 7 (p.21) ⭐深度解读
![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p21.png]]
> [!quote] caption
> The Maj@K and Pass@K of SFT and RL DeepSeekMath 7B on GSM8K and MATH

> [!tip] 技术解读（多模态）
> ## Figure Description (≤120 words)

The figure consists of **two side-by-side line plots** comparing model accuracy on two math benchmarks: **GSM8K** (left) and **MATH** (right). Both plots share an x-axis of "K: number of candidates" on a log scale (1, 4, 8, 16, 32, 64) and a y-axis of accuracy (%). Four curves are plotted: **Maj@K-Instruct (purple), Maj@K-RL (orange), Pass@K-Instruct (green), and Pass@K-RL (blue)**, evaluated on the DeepSeekMath 7B model at temperature 0.7. All curves rise monotonically with K. Pass@K curves (green/blue) climb steeply and converge near the top (~97–99% on GSM8K, ~85–87% on MATH), while Maj@K curves (purple/orange) plateau at lower values. **Key takeaway**: RL boosts Maj@K but not Pass@K, indicating RL sharpens the top-K output distribution rather than expanding the model's underlying capability.

## Caption (verbatim)

**Figure 7 | The Maj@K and Pass@K of SFT and RL DeepSeekMath 7B on GSM8K and MATH (temperature 0.7). It was noted that RL enhances Maj@K but not Pass@K.**

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