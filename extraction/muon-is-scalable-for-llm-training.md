---
paper_num: "64"
title: "Muon is Scalable for LLM Training"
authors: ""
date: "2025/2/24"
arxiv: "https://arxiv.org/abs/2502.16982"
pdf: "papers/muon-is-scalable-for-llm-training.pdf"
slug: "muon-is-scalable-for-llm-training"
tags: [training]
---

# Muon is Scalable for LLM Training

> [!abstract] 摘要（原文）
> Recently, the Muon optimizer based on matrix orthogonalization has demonstrated strong results in training small-scale language models, but the scalability to larger models has not been proven. We identify two crucial techniques for scaling up Muon: (1) adding weight decay and (2) carefully adjusting the per-parameter update scale. These techniques allow Muon to work out-of-the-box on large-scale training without the need of hyper-parameter tuning. Scaling law experiments indicate that Muon achieves $\sim\!2\times$ computational efficiency compared to AdamW with compute optimal training. Based on these improvements, we introduce Moonlight, a 3B/16B-parameter Mixture-of-Expert (MoE) model trained with 5.7T tokens using Muon. Our model improves the current Pareto frontier, achieving better performance with much fewer training FLOPs compared to prior models. We open-source our distributed Muon implementation that is memory optimal and communication efficient. We also release the pretrained, instruction-tuned, and intermediate checkpoints to support future research.

## 元信息
- **发表日期**: 2025/2/24
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2502.16982
- **本地 PDF**: `papers/muon-is-scalable-for-llm-training.pdf`
- **页数**: 19

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig01.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p01.png]]*
> [!quote] caption
> Scaling up with Muon. (a) Scaling law experiments comparing Muon and Adam. Muon is ∼2× more computational efficient than Adam with compute optimal training. (b) The MMLU performance of our Moonlight model optimized with Muon and other comparable models. Moonlight advances the Pareto frontier of performance vs training FLOPs. ∗Corresponding author: zhouxinyu@moonshot.cn[cs.LG] 24 Feb 2025

> [!tip] 技术解读（多模态）
> **Figure 1 Description (≤120 words):**

Figure 1 is a two-panel scaling analysis. **(a) Left panel** plots LM loss vs. PFLOP/s-days on a log-x scale, overlaying two fitted scaling-law lines with star data points: a red dashed line for **AdamW** (higher loss, steeper offset) and a blue dashed line for **Muon** (consistently lower loss). A horizontal arrow at the low-loss region annotates "0.519× FLOPs," quantifying Muon's compute advantage. **(b) Right panel** is a Pareto-frontier scatter plot of MMLU Score (y) vs. Training FLOPs (x), where red stars mark **Moonlight-2.4B-1.2T** and **Moonlight-2.4B-5.7T**, and orange dots benchmark ~15 competing models (Gemma, Qwen, OLMo, Llama, DeepSeek, StableLM, DCLM, MAP-Neo). A dashed frontier line plus blue shaded region highlight Moonlight's advanced Pareto position. **Key takeaway:** Muon attains ~2× compute-optimal efficiency over AdamW, enabling Moonlight to dominate the MMLU vs. FLOPs Pareto frontier.

**Caption verbatim:**

Figure 1: Scaling up with Muon. **(a)** Scaling law experiments comparing Muon and Adam. Muon is ∼ 2× more computational efficient than Adam with compute optimal training. **(b)** The MMLU performance of our Moonlight model optimized with Muon and other comparable models. Moonlight advances the Pareto frontier of performance vs training FLOPs.

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig02.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p04.png]]*
> [!quote] caption
> Validation loss curves for AdamW (green), Muon without weight decay (red), and Muon with weight decay (blue).

> [!tip] 技术解读（多模态）
> **Figure Description (≤120 words):**

The figure is a line plot tracking **Validation Loss** (y-axis, ~2.25–2.55) against **Training Iterations** (x-axis, 0–65k+). It compares three optimizer curves on LLM training:

- **Green** — AdamW (baseline)
- **Red** — Muon without weight decay
- **Blue** — Muon with weight decay

All curves descend monotonically. Both Muon variants stay below AdamW throughout training, converging to ~2.25. An **inset plot** (top-right) shows the *difference* in loss between vanilla Muon and Muon-w/-weight-decay, with annotated crossover points: vanilla Muon is better by 0.023 at iteration 24,000, but Muon-with-weight-decay overtakes it, winning by 0.017 at iteration 66,000 — illustrating the benefit of weight decay emerges late in training.

**Key takeaway:** Adding weight decay makes Muon *outperform* AdamW and eventually surpass vanilla Muon at convergence.

**Caption (verbatim):**
> Figure 2: Validation loss curves for AdamW (green), Muon without weight decay (red), and Muon with weight decay (blue).

### Figure 3 (p.7) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig03.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p07.png]]*
> [!quote] caption
> Fitted scaling law curves for Muon and AdamW optimizers.

> [!tip] 技术解读（多模态）
> **Main figure description (Figure 3):**

A log–log line chart comparing optimizer scaling behavior. The x-axis is compute (PFLOP/s-days, 10⁻²–10¹) and the y-axis is LM loss at seqlen=8K (range 2.2–4.0). Multiple solid curves depict individual model-size runs from Table 2 (399M, 545M, 822M, 1.1B, 1.5B params) — blue family for Muon and red family for AdamW. Overlaid dashed lines are the fitted power-law envelopes: **blue dashed = Muon**, **red dashed = AdamW**.

**Key takeaway:** Muon's envelope sits below AdamW's across the entire compute range, and Table 3 quantifies the gap — LM loss ≈ 2.506·C⁻⁰·⁰⁵² (Muon) vs 2.608·C⁻⁰·⁰⁵⁴ (AdamW) — i.e., a ~0.1 absolute loss reduction at equivalent compute, with comparable exponent.

**Caption (verbatim):**
> Figure 3: Fitted scaling law curves for Muon and AdamW optimizers.

### Figure 4 (p.10) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig04.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p10.png]]*
> [!quote] caption
> SVD entropy of weight matrices across different training iterations. We categorize the weight matrices into 6 different groups: 1) AttnQO denotes the weight matrices related to the query and output projection in the attention layer; 2) AttnKV denotes the weight matrices related to the key and value projection in the attention layer; 3) Experts denotes the weight matrices in expert models; 4) Share

> [!tip] 技术解读（多模态）
> ## Figure Description

**Layout/Components:** Figure 4 is a 1×6 grid of line plots showing SVD entropy (y-axis) vs. training iterations in K (x-axis, 0–~30K). Each subplot corresponds to a different weight-matrix group in a MoE-style transformer: AttnQO, AttnKV, Experts, SharedExperts, Router, and Dense. Two curves are overlaid per panel: **AdamW (red)** and **Muon (blue)**.

**Key Takeaway:** Muon consistently produces **higher SVD entropy** than AdamW across all six weight-matrix groups, indicating Muon preserves richer singular-value diversity in learned weights throughout training, while AdamW drives entropy toward a lower-rank regime — suggesting Muon induces a more balanced/conditioned weight spectrum during LLM training.

(≈85 words)

## Caption Verbatim

**Figure 4:** SVD entropy of weight matrices across different training iterations. We categorize the weight matrices into 6 different groups: 1) AttnQO denotes the weight matrices related to the query and output projection in the attention layer; 2) AttnKV denotes the weight matrices related to the key and value projection in the attention layer; 3) Experts denotes the weight matrices in expert models; 4) SharedExperts denotes the weight matrices in shared expert models; 5) Router denotes the weight matrices in the router; 6) Dense denotes the weight matrices in the first dense layer. The SVD entropy is calculated as the macro-average of the weight matrices in each group across all layers. For weights in expert models, we only calculate 3 out of 64 experts in different layers for efficiency.

### Figure 5 (p.15) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig05.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p15.png]]*
> [!quote] caption
> Optimization Landscapes for Scaling Law Hyper-parameters Across FLOPs Budgets

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The figure consists of **three side-by-side scatter/line plots** displaying loss landscapes across FLOPs budgets (five levels: 1.1e+20, 1.9e+20, 3.9e+20, 5.7e+20, 1.0e+21, color-coded purple→yellow):

1. **Loss vs. Train Tokens** (log-scale x-axis): Loss decreases monotonically with more tokens; larger FLOPs budgets achieve lower final loss.
2. **Loss vs. Learning Rate**: Bowl-shaped (U) curves, each with a distinct minimum identifying the optimal learning rate per FLOPs budget.
3. **Loss vs. Batch Size**: Loss rises with batch size (200–900), with larger budgets consistently achieving lower loss across the range.

**Key takeaway:** Across all three hyper-parameters, higher FLOPs budgets consistently dominate lower ones (lower loss everywhere), confirming that the optimal hyper-parameters scale predictably with compute—enabling reliable extrapolation to larger training runs.

## Verbatim Caption

**Figure 5: Optimization Landscapes for Scaling Law Hyper-parameters Across FLOPs Budgets**

### Figure 6 (p.15) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig06.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p15.png]]*
> [!quote] caption
> D

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The figure consists of **three side-by-side scatter/line plots** displaying loss landscapes across FLOPs budgets (five levels: 1.1e+20, 1.9e+20, 3.9e+20, 5.7e+20, 1.0e+21, color-coded purple→yellow):

1. **Loss vs. Train Tokens** (log-scale x-axis): Loss decreases monotonically with more tokens; larger FLOPs budgets achieve lower final loss.
2. **Loss vs. Learning Rate**: Bowl-shaped (U) curves, each with a distinct minimum identifying the optimal learning rate per FLOPs budget.
3. **Loss vs. Batch Size**: Loss rises with batch size (200–900), with larger budgets consistently achieving lower loss across the range.

**Key takeaway:** Across all three hyper-parameters, higher FLOPs budgets consistently dominate lower ones (lower loss everywhere), confirming that the optimal hyper-parameters scale predictably with compute—enabling reliable extrapolation to larger training runs.

## Verbatim Caption

**Figure 5: Optimization Landscapes for Scaling Law Hyper-parameters Across FLOPs Budgets**

### Figure 7 (p.17) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig07.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p17.png]]*
> [!quote] caption
> Training dynamics comparison between Moonlight and Moonlight-A

> [!tip] 技术解读（多模态）
> **Main Figure Description**

The figure is a 2×2 grid of line plots comparing training dynamics of two optimizer variants across ~38,000 iterations (red = Moonlight-A with AdamW, blue = Moonlight with Muon):
- **(a) Training Loss**: Both descend from ~2.20 to ~1.90; Moonlight converges lower (~1.88) than Moonlight-A (~1.92).
- **(b) Gradient Norm**: Moonlight-A exhibits recurrent explosive spikes up to ~1.0; Moonlight remains stable near ~0.05–0.1.
- **(c) Max Attention Logit (Layer 1)**: Moonlight's logits balloon to ~120 around iteration 20k before decaying; Moonlight-A stays flat near ~20.
- **(d) Large Attention Logits Ratio**: Moonlight shows a sharp mid-training spike (~0.00014); Moonlight-A stays ~0.

**Key takeaway**: Muon delivers lower, more stable loss with bounded gradients, but its normalization induces larger transient attention-logit magnitudes in early layers—an instability the authors apparently judge benign given the convergence behavior.

**Caption (verbatim):**

*Figure 7: Training dynamics comparison between Moonlight and Moonlight-A*

### Figure 8 (p.9) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig08.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p09.png]]*
> [!quote] caption
> 6.

> [!tip] 技术解读（多模态）
> # Main Figure Description

**Structure (components):** Table 5 is a benchmark comparison matrix with rows organized into four evaluation categories (English: MMLU/MMLU-pro/BBH/TriviaQA; Code: HumanEval/MBPP; Math: GSM8K/MATH/CMath; Chinese: C-Eval/CMMLU) and four model columns (Llama3.2-3B, Qwen2.5-3B, DSV2-Lite, Moonlight). Header rows report model metadata (Activated/Total Params, Training Tokens, Optimizer).

**Data flow:** Parameters → Token budget → Optimizer choice → Benchmark scores (bold = best per row).

**Key Technical Takeaway (≈75 words):** Despite using only 5.7T training tokens and 2.24B activated params, Moonlight (Muon optimizer) achieves best-in-class scores on 11/13 benchmarks — e.g., MMLU 70.0, GSM8K 77.4, CMMLU 78.2 — outperforming denser models trained on 2–3× more tokens. Notably, it matches DSV2-Lite's activated-param footprint while improving MMLU by +11.7, demonstrating Muon's superior compute-efficiency frontier.

# Caption (verbatim)

**Table 5: Comparison of different models on various benchmarks.**

### Figure 9 (p.18) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig09.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p18.png]]*
> [!quote] caption
> Distribution of singular values for each weight matrix in the attention layers. We use WC to denote the weight matrices at each layer that compress the hidden states to the shared latent spaces for keys and values, WV to denote the weight matrices up-projecting the values from the latent space, WO to denote the output projection matrices, and WKR, WKC, WQR and WQC to denote the projection matrices

> [!tip] 技术解读（多模态）
> **Main Figure (Figure 8) — Description**

This scatter plot compares GSM8k accuracy against training compute (FLOPs, log-scale) for open-source LLMs. **Components**: orange circles mark competing models (Qwen-2.5-14B, OLMo-2, Gemma-2, Llama-3.1, DeepSeek, StableLM, DCLM, Amber, MAP-Neo); red stars mark the paper's Moonlight checkpoints; a dashed blue envelope delineates the "GSM8k Performance Frontier." **Data flow**: each point = (training FLOPs → GSM8k score). **Key takeaway**: Moonlight-2.4B-5.7T (~1e23 FLOPs, ≈77 GSM8k) sits on the compute-efficiency frontier, matching or exceeding models like OLMo-2-13B while using roughly an order of magnitude fewer FLOPs than Qwen-2.5-14B — empirically demonstrating that Muon is compute-scalable.

**Captions (verbatim):**

> Figure 8: The GSM8k performance of our Moonlight model optimized with Muon and other comparable models.

> Figure 9: Distribution of singular values for each weight matrix in the attention layers. We use WC to denote the weight matrices at each layer that compress the hidden states to the shared latent spaces for keys and values, WV to denote the weight matrices up-projecting the values from the latent space, WO to denote the output projection matrices, and WKR, WKC, WQR and WQC to denote the projection matrices for the part of keys and queries with and without RoPE respectively. We set the spines of each line graph red if the corresponding weight matrix optimized by Muon has a lower singular entropy than AdamW.

### Figure 10 (p.19) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig10.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p19.png]]*
> [!quote] caption
> Distribution of singular values for each weight matrix in the feed-forward network (FFN) layers. We use WI, WV and WO to denote the weight matrices involved in the FFN layer with SwiGLU activation function, where WI represents the input projection to the Swish1 function, WV represents the extra input projection interacting with Swish1 activations, and WO represents the output projection. We use E0

> [!tip] 技术解读（多模态）
> **Description & Key Takeaway**

Figure 10 is a matrix visualization of singular value (SV) distributions across an LLM's FFN weight matrices, comparing two optimizers. **Layout:** rows index weight matrices organized by expert (E0–E3, plus a shared expert "SE") and the router (RW), each split into WO/WI/WV projections; columns index transformer layers L2–L27. **Per cell:** two overlaid line plots — red = AdamW, blue = Muon — showing sorted singular value spectra with characteristic decay curves. **Highlighting:** cells are outlined red where Muon yields lower singular entropy than AdamW. **Data flow:** layer-wise SV spectra are extracted per trained model and tiled into a comparative grid.

**Key takeaway:** Muon produces consistently more "spectrally uniform" (lower-entropy) weight matrices than AdamW across most FFN layers and experts, suggesting better-conditioned, more isotropic representations at scale.

**Caption (verbatim):**

"Figure 10: Distribution of singular values for each weight matrix in the feed-forward network (FFN) layers. We use WI, WV and WO to denote the weight matrices involved in the FFN layer with SwiGLU activation function, where WI represents the input projection to the Swish₁ function, WV represents the extra input projection interacting with Swish₁ activations, and WO represents the output projection. We use E0, E2, E3 to denote three arbitrarily selected expert models and SE to denote the weights in the shared expert model. We use RW to denote the weights in the router. We set the spines of each line graph red if the corresponding weight matrix optimized by Muon has a lower singular entropy than AdamW."

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.6) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-tab01.png]]
> [!quote] caption
> Controlling Muon’s Update RMS Across Different Model Params

> [!tip] 表格解读（多模态）
> **Description:**

Table 1 presents a 3×4 comparison matrix evaluating three methods (Baseline, Update Norm, Adjusted LR) against four metrics: Training loss, Validation loss, query weight RMS, and MLP weight RMS.

Results show Update Norm achieves the lowest training loss (2.72) and best validation loss (2.789), but at the cost of substantially higher query weight RMS (4.918e-2) and MLP weight RMS (5.01e-2). In contrast, Adjusted LR matches the validation loss (2.789) while keeping query weight RMS (3.496e-2) and MLP weight RMS (4.89e-2) closer to baseline levels.

**Key takeaway:** Adjusting the learning rate is the more effective lever for controlling Muon's update RMS — it preserves validation performance while successfully constraining weight magnitudes, unlike direct norm rescaling which inflates them.

**Caption (verbatim):**
"Table 1: Controlling Muon's Update RMS Across Different Model Params"

### Table 3 (p.7) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-tab03.png]]
> [!quote] caption
> Fitted parameters of the scaling law curves

> [!tip] 表格解读（多模态）
> **Description:** Although the submission is labeled "main figure," what is provided is **Table 3**, not a graphical figure. The table reports fitted scaling-law parameters for language-model loss at a sequence length of 8K, comparing two optimizers side-by-side. It contains a single data row ("LM loss (seqlen=8K)") with two columns: **Muon**, yielding the fitted curve 2.506 × C^(−0.052), and **AdamW**, yielding 2.608 × C^(−0.054). There is no architecture diagram, pipeline, or data-flow schematic—only parameter values organized in a 2-column × 1-row grid beneath a title and headers. **Key takeaway:** Muon's fitted scaling-law front coefficient (2.506) is ~4% lower than AdamW's (2.608) at seq=8K, while its decay exponent is marginally shallower (−0.052 vs −0.054), indicating Muon attains a uniformly better loss curve across compute C, rather than merely better asymptotics.

**Caption (verbatim):**
> **Table 3:** Fitted parameters of the scaling law curves

### Table 4 (p.8) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-tab04.png]]
> [!quote] caption
> Comparison of different models at around 1.2T tokens.

> [!tip] 表格解读（多模态）
> **Description of the main figure (Table 4):**

The main figure is actually **Table 4** — a benchmark comparison matrix across three models at matched ~1.2T training tokens. **Components:** top rows list model specs (activated/total params, training tokens, optimizer), followed by grouped benchmarks — English (MMLU, MMLU-pro, BBH, TriviaQA), Code (HumanEval, MBPP), Math (GSM8K, MATH, CMath), and Chinese (C-Eval, CMMLU) — with best scores bolded. Data flow is column-wise: each model reports downward through shared evaluation categories. A footnote (†) notes parameter counts exclude embeddings.

**Key technical takeaway:** Moonlight@1.2T (Muon optimizer) beats its AdamW twin Moonlight-A and DSV3-Small on most benchmarks — most starkly on Code (HumanEval 37.2 vs 29.3/26.8) and Math (GSM8K 45.0 vs 43.8/31.4) — confirming Muon's scaling effectiveness at fixed parameter/token budgets despite identical architecture.

*(≈119 words)*

**Caption transcribed verbatim:**

> Table 4: Comparison of different models at around 1.2T tokens.

### Table 5 (p.9) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-tab05.png]]
> [!quote] caption
> Comparison of different models on various benchmarks.

> [!tip] 表格解读（多模态）
> ## Description

The figure is **Table 5**, a benchmark comparison matrix with four model columns (Llama3.2-3B, Qwen2.5-3B, DSV2-Lite, Moonlight) and grouped benchmark rows organized into **English** (MMLU, MMLU-pro, BBH, TriviaQA), **Code** (HumanEval, MBPP), **Math** (GSM8K, MATH, CMath), and **Chinese** (C-Eval, CMMLU). A top metadata block reports activated/total parameters, training tokens, and optimizer. Bolded cells flag per-row winners, and footnotes clarify parameter exclusion and TriviaQA evaluation scope.

**Key takeaway:** Moonlight (2.24B activated / 15.29B total, MoE, Muon optimizer, 5.7T tokens) achieves top scores on 9 of 12 benchmarks—beating DSV2-Lite (same architecture, AdamW) and remaining competitive with dense models trained on 3× more tokens—demonstrating the Muon optimizer's superior compute efficiency at the Pareto frontier.

## Caption (verbatim)

**Table 5: Comparison of different models on various benchmarks.**

### Table 6 (p.10) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-tab06.png]]
> [!quote] caption
> Examining the impact of optimizer interchangeability between pretraining and SFT phases.

> [!tip] 表格解读（多模态）
> ## Description of Main Figure

The figure presents **seven side-by-side line plots** displaying **SVD entropy of weight matrices** across training iterations (0–~45K) for distinct weight-matrix groups within a Mixture-of-Experts (MoE) transformer. Each subplot tracks **two curves (red and blue)**, likely corresponding to two model variants being compared. The categories include: **AttnQO** (query/output projection), **AttnKV** (key/value projection), **Experts**, **SharedExperts**, **Router**, and **Dense** (first dense layer). SVD entropy is macro-averaged across layers (or 3-of-64 experts per layer for efficiency).

**Key technical takeaway:** Across nearly all subplots, **entropy drops sharply within the first few thousand iterations then stabilizes**, indicating that weight-matrix spectral structure **rapidly crystallizes early in training**—suggesting heavy pretraining-time computation could potentially be optimized or early-stopped without significant spectral loss. Counterintuitively, the **red (smaller/slower) curve often shows a brief initial entropy *dip* before recovering**, implying a transient spectral re-organization phase.

## Verbatim Caption Transcription

**Figure 4:** SVD entropy of weight matrices across different training iterations. We categorize the weight matrices into six different groups: 1) AttnQO denotes the weight matrices related to the query and output projection in the attention layer; 2) AttnKV denotes the weight matrices related to the key and value projection in the attention layer; 3) [Experts] denotes the weight matrices in expert models; 4) SharedExperts denotes the weight matrices in shared expert models; 5) [R]outer denotes the weight matrices in the router; 6) Dense denotes the weight matrices in the first dense layer. The SVD entropy is calculated as the macro-average of the weight matrices in each group across all layers. For weight matrices in expert models, we only calculate 3 out of 64 experts in different layers for efficiency.

*Note: The leftmost characters of the original caption are partially cut off; bracketed terms above [Experts], [R]outer are reconstructed from context to reflect the truncated text as displayed.*

### Table 9 (p.14) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-tab09.png]]
> [!quote] caption
> Empirical Relationships Between Scaling Law Parameters and Computational Budget (FLOPs)

> [!tip] 表格解读（多模态）
> **Description of Table 9**

The table presents four fitted power-law relationships of the form *a · C^b*, where C is the compute budget (FLOPs) and each column represents a different training hyperparameter:
- **N(C)** — model parameter count: 0.0483359 · C^0.5112684
- **D(C)** — dataset/token count: 3.4480927 · C^0.4887316
- **η(C)** — learning rate: 0.0127339 · C^−0.0574752
- **B(C)** — batch size: 0.0065202 · C^0.4137915

**Key takeaway:** Model size and dataset tokens scale almost identically with C (exponents ≈ 0.5), recovering the Chinchilla-style joint allocation. However, learning rate surprisingly decreases with more compute (negative exponent), while batch size grows sub-linearly — a nuance often overlooked in simpler scaling prescriptions.

**Caption (verbatim):** *Table 9: Empirical Relationships Between Scaling Law Parameters and Computational Budget (FLOPs)*

### Table 10 (p.16) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-tab10.png]]
> [!quote] caption
> presents a comparative analysis between our Moonlight model (optimized with Muon) and publicly available models trained with greater computational resources, including LLama3.1-8B (Grattafiori et al. 2024), Gemma-9B (Gemma Team et al. 2024) and Qwen2.5-7B (Yang et al. 2024). Figure 8 illustrates the

> [!tip] 表格解读（多模态）
> I'm unable to complete this request as specified, because the excerpt you provided contains **only running paragraph text from page 16 of the paper** — no figure image and no figure caption are present in the input. The text merely *references* Figures 8, 9, and 10, but does not include them.

Here's what the passage actually contains:

- A paragraph mentioning **Table 10** (a comparison between Moonlight/Muon vs. Llama3.1‑8B, Gemma‑9B, Qwen2.5‑7B) and referencing **Figure 8** (GSM8k benchmarks).
- Section heading **F — Singular Value Distributions of Weight Matrices**, which states that Figures 9 and 10 show that Muon‑optimized matrices have a **flatter singular‑value spectrum** than AdamW‑optimized ones, supporting the hypothesis that Muon yields a more diverse update spectrum.

If you can paste the actual **image** of Figure 8, 9, or 10, or copy out its caption text, I can then:
1. Describe the architecture/components/data flow and give a ≤120‑word technical takeaway, and
2. Transcribe the caption verbatim.

No hallucinated description would be faithful in lieu of the actual figure.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
H(\sigma) = -\frac{1}{\log n}\sum_{i=1}^n \frac{\sigma^2_i}{\sum_{j=1}^n \sigma^2_j} \log \frac{\sigma^2_i}{\sum_{j=1}^n \sigma^2_j} \notag
$$

$$
\mathbf{M}_t &= \mu \mathbf{M}_{t-1} + \nabla\mathcal{L}_t(\mathbf{W}_{t-1}) \notag \\ \mathbf{O}_t &= \text{Newton-Schulz}(\mathbf{M}_t)\text{\footnotemark[1]} \\ \mathbf{W}_t &= \mathbf{W}_{t-1} - \eta_t \mathbf{O}_t \notag
$$

$$
\mathbf{X}_k &= a \mathbf{X}_{k-1} + b (\mathbf{X}_{k-1} \mathbf{X}_{k-1}^\mathrm{T}) \mathbf{X}_{k-1} + c (\mathbf{X}_{k-1} \mathbf{X}_{k-1}^\mathrm{T})^2 \mathbf{X}_{k-1}
$$

$$
\mathbf{W}_t = \mathbf{W}_{t-1} - \eta_t (\mathbf{O}_t + \lambda \mathbf{W}_{t-1})
$$

$$
\mathbf{W}_t = \mathbf{W}_{t-1} - \eta_t (0.2\cdot\mathbf{O}_t\cdot\sqrt{\max(A,B)} + \lambda \mathbf{W}_{t-1})
$$

$$
\mathbf{W}_t = \mathbf{W}_{t-1} - \eta_t (0.2\cdot\mathbf{O}_t\cdot\sqrt{H} + \lambda \mathbf{W}_{t-1})
$$

$$
\mathbf{W}_t = \mathbf{W}_{t-1} - \eta_t (0.2\cdot\mathbf{O}_t/\mathop{\text{RMS}}(\mathbf{O}_t) + \lambda \mathbf{W}_{t-1})
$$

## 相关论文

- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core
- [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] — From ATOP to ZCube: Automated Topology Optimization Pipeline and A Highly Cost-Effective Network Topology for Large Model Training
- [[zero-memory-optimizations-toward-training-trillion-parameter-models]] — ZeRO: Memory Optimizations Toward Training Trillion Parameter Models
- [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] — GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints
- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey

## 技术点深读（DEEP）

![[deep/muon-is-scalable-for-llm-training]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/muon-is-scalable-for-llm-training.txt`（55936 字符）供引用检索。