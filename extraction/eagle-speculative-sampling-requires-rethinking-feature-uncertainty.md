---
paper_num: "4"
title: "EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty"
authors: "Yuhui Li♠ Fangyun Wei‡ Chao Zhang♠ Hongyang Zhang♣† ♠Peking University ‡Microsoft Research ♣University of Waterloo †Vector Institute hongyang.zhang@uwaterloo.ca Vicuna 7B Vicuna 13B Vicuna 33B LLaMA2-Chat 7B LLaMA2-Chat "
date: "2026/6/29"
arxiv: "https://arxiv.org/abs/2401.15077"
pdf: "papers/eagle-speculative-sampling-requires-rethinking-feature-uncertainty.pdf"
slug: "eagle-speculative-sampling-requires-rethinking-feature-uncertainty"
tags: [speculative]
---

# EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty

> [!abstract] 摘要（原文）
> 1\. 🦅 EAGLE是一种高效的Speculative Sampling框架，其核心创新在于在特征（第二顶层）层面进行自回归，并通过引入提前一个时间步的Token序列来解决特征预测中的不确定性。 2. ⚡️ 实验结果表明，EAGLE在LLaMA2-Chat 70B上实现了2.7x-3.5x的推理速度提升， throughput 翻倍，且理论上保证了生成文本的分布不变性。 3. 💡 EAGLE具有出色的通用性和可靠性，无需对原始LLM进行微调即可应用于多种模型和任务，并与现有加速技术（如gpt-fast）兼容，显著降低了LLM系统的运行成本。

## 元信息
- **发表日期**: 2026/6/29
- **作者**: Yuhui Li♠ Fangyun Wei‡ Chao Zhang♠ Hongyang Zhang♣† ♠Peking University ‡Microsoft Research ♣University of Waterloo †Vector Institute hongyang.zhang@uwaterloo.ca Vicuna 7B Vicuna 13B Vicuna 33B LLaMA2-Chat 7B LLaMA2-Chat 
- **arXiv**: https://arxiv.org/abs/2401.15077
- **本地 PDF**: `papers/eagle-speculative-sampling-requires-rethinking-feature-uncertainty.pdf`
- **页数**: 13

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p01.png]]
> [!quote] caption
> Speedup ratio of Vicuna and LLaMA2-Chat inference latency on the MT-bench for greedy (temperature=0) settings. Speedup ratio of Medusa and Lookahead are copied from their original technical reports. With speculative sampling, there is a lack of suitable draft models to accelerate the 7B model. Employing a 7B model as the draft model for a 13B model results in slow speeds due to the high overhead o

> [!tip] 技术解读（多模态）
> **Figure Description (≤120 words):**

This bar chart compares inference speedup ratios across six LLM backbones (Vicuna 7B/13B/33B, LLaMA2-Chat 7B/13B/70B) on the MT-bench benchmark under greedy (temperature=0) settings. Six methods are benchmarked: EAGLE, Medusa, Lookahead, Speculative sampling, DistillSpec, and Vanilla (baseline). EAGLE (blue bars) consistently achieves the highest speedup, ranging from 2.78x–3.07x across all model sizes. Medusa (1.92x–1.97x) is shown on Vicuna models; Lookahead (1.45x–1.64x) on LLaMA2-Chat; DistillSpec (1.12x–2.13x) on Vicuna 33B and LLaMA2-Chat 70B. Speculative sampling is marked N/A for 7B models (no suitable draft model) and at 1.00x for 13B (7B-as-draft overhead negates gains). Vanilla baseline is normalized to 1.00x.

**Key Technical Takeaway:** EAGLE delivers ~2x the speedup of competing methods (e.g., 3.01x vs. Lookahead 1.45x on LLaMA2-Chat 70B) while preserving the output text distribution.

**Verbatim Caption:**

Figure 1: Speedup ratio of Vicuna and LLaMA2-Chat inference latency on the MT-bench for greedy (temperature=0) settings. Speedup ratio of Medusa and Lookahead are copied from their original technical reports. With speculative sampling, there is a lack of suitable draft models to accelerate the 7B model. Employing a 7B model as the draft model for a 13B model results in slow speeds due to the high overhead of the 7B model, rendering it less efficient than vanilla autoregressive decoding. These scenarios are marked as N/A. In this paper, we only compare with speculative sampling based methods that do not need to finetune the backbone models, ensuring the output text distribution remains constant.

### Figure 2 (p.2) ⭐深度解读
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p02.png]]
> [!quote] caption
> Speedup ratio on the MT-bench for non-greedy (temperature=1) settings. Lookahead is confined to greedy decoding, and the non-greedy generation of Medusa does not guarantee lossless performance. Therefore, EAGLE is not compared with these methods. I 𝑓I 𝑝(am)=0.6 𝑝(always)=0.4 sampling am 𝑓am 𝑝(excited)=0.3 𝑝(ready)=0.7 sampling always 𝑓always 𝑝(begin)=0.8 𝑝(look)=0.2 𝑝always 𝑝I 𝑝am

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】EAGLE 架构图(Fig.4)：目标 LLM 产出第二顶层特征 f_t 与下一 token t_{t+1}；轻量 draft model 在特征层自回归，输入 f_t + 超前一拍的 t_{t+1}，预测 f_{t+1}，再经 LM head 得 draft token t_{t+2}。「特征+超前 token」消除采样下 f_{t+1} 的不确定性→接受率↑，Vicuna/LLaMA2-70B 上 2.68x。架构核心图。

### Figure 3 (p.2) ⭐深度解读
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p02.png]]
> [!quote] caption
> Uncertainty in feature sequences. The next fea- ture following fI is contingent on the sampling outcome and cannot be determined solely based on fI, where both “always” and “am” are possible to follow the token “I” and lead to two branches.

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】EAGLE 架构图(Fig.4)：目标 LLM 产出第二顶层特征 f_t 与下一 token t_{t+1}；轻量 draft model 在特征层自回归，输入 f_t + 超前一拍的 t_{t+1}，预测 f_{t+1}，再经 LM head 得 draft token t_{t+2}。「特征+超前 token」消除采样下 f_{t+1} 的不确定性→接受率↑，Vicuna/LLaMA2-70B 上 2.68x。架构核心图。

### Figure 4 (p.3) ⭐深度解读
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p03.png]]
> [!quote] caption
> Accuracy and speedup ratio of draft models based on tokens, features and feature&shifted-token at tempera- ture=0, tested on MT-bench with Vicuna 7B as the original LLM. Feature&shifted-token refers to using a feature se- quence and a token sequence advanced by one time step as inputs. achieved a speedup ratio of 2.7x-3.5x, doubled through- put, and theoretically guaranteed the preservation of the

> [!tip] 技术解读（多模态）
> ## Figure 4 Description

The figure contains two side-by-side line plots tracking draft model performance across 7 training epochs:

**Left plot — Speedup ratio:** Y-axis ranges 1.5–2.5x
**Right plot — Accuracy (Acc):** Y-axis ranges 0.4–0.8

**Three curves compared (legend at top):**
- 🔵 **feature&shifted-token** (blue) — top performer
- 🟢 **feature** (green) — middle performer
- 🟠 **token** (orange) — lowest, nearly flat

**Data flow insight:** All curves rise with training, but feature&shifted-token consistently dominates on both metrics, suggesting that combining the second-to-top-layer feature stream with an autoregressively shifted token sequence yields better draft predictions than either modality alone. Tokens alone barely learn useful draft signals.

**Key takeaway:** *Feature-level signals carry richer next-token predictive information than raw token IDs; injecting a one-step-shifted token alongside features gives EAGLE its largest single accuracy/speedup lift.*

---

### Caption (verbatim)

> **Figure 4:** Accuracy and speedup ratio of draft models based on tokens, features and feature&shifted-token at temperature=0, tested on MT-bench with Vicuna 7B as the original LLM. Feature&shifted-token refers to using a feature sequence and a token sequence advanced by one time step as inputs.

### Figure 5 (p.4) ⭐深度解读
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p04.png]]
> [!quote] caption
> A comparison of the methods for drafting the fourth and fifth tokens, t4 and t5. t (represented by blue blocks) denotes tokens, and f (orange blocks) signifies the features, with subscripts indicating their positions in the se- quence. The red border indicates the predictions of the draft model. For simplicity, the n in the n-gram for Lookahead, as shown in the figure, has been set to 2.

> [!tip] 技术解读（多模态）
> ## Description of Figure 6 (EAGLE Pipeline)

**Architecture & Components:**
The draft model consists of three modules: a frozen **Embedding layer** and **LM Head** (inherited from the target LLM, blue/snowflake), and a trainable **Autoregression Head** (yellow) sitting between them.

**Data Flow:**
Input tokens pass through the frozen Embedding layer, get concatenated with the feature sequence to form a fused sequence (2×hidden_dim), the Autoregression Head predicts the next feature, the frozen LM Head converts it into a token distribution, and Sampling produces multiple candidate tokens. The predicted feature + sampled token are fed back for the next step, building a **tree-structured draft** (e.g., 10 tokens in 3 forward passes).

**Key Technical Takeaway:** EAGLE's innovation is predicting the *next feature* (not just the next token) from a fused token–feature sequence, leveraging the target LLM's frozen embedding/LM head while training only a lightweight Autoregression Head—dramatically accelerating speculative decoding.

## Verbatim Caption (Figure 6)

**Figure 6: Pipeline of EAGLE.** The upper section illustrates the computational process, while the lower section displays the corresponding generation results for each step. In the upper section, **green** blocks represent token embeddings, **or­ange** blocks represent features, **red** boxes indicate the predictions of the draft model, and **blue** modules with snowflake icons represent the use of target LLM parameters, which are not subject to training.

### Figure 6 (p.4) ⭐深度解读
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p04.png]]
> [!quote] caption
> Pipeline of EAGLE. The upper section illustrates the computational process, while the lower section displays the corresponding generation results for each step. In the upper section, green blocks represent token embeddings, or- ange blocks represent features, red boxes indicate the predic- tions of the draft model, and blue modules with snowflake icons represent the use of target LLM parameters, w

> [!tip] 技术解读（多模态）
> ## Description of Figure 6 (EAGLE Pipeline)

**Architecture & Components:**
The draft model consists of three modules: a frozen **Embedding layer** and **LM Head** (inherited from the target LLM, blue/snowflake), and a trainable **Autoregression Head** (yellow) sitting between them.

**Data Flow:**
Input tokens pass through the frozen Embedding layer, get concatenated with the feature sequence to form a fused sequence (2×hidden_dim), the Autoregression Head predicts the next feature, the frozen LM Head converts it into a token distribution, and Sampling produces multiple candidate tokens. The predicted feature + sampled token are fed back for the next step, building a **tree-structured draft** (e.g., 10 tokens in 3 forward passes).

**Key Technical Takeaway:** EAGLE's innovation is predicting the *next feature* (not just the next token) from a fused token–feature sequence, leveraging the target LLM's frozen embedding/LM head while training only a lightweight Autoregression Head—dramatically accelerating speculative decoding.

## Verbatim Caption (Figure 6)

**Figure 6: Pipeline of EAGLE.** The upper section illustrates the computational process, while the lower section displays the corresponding generation results for each step. In the upper section, **green** blocks represent token embeddings, **or­ange** blocks represent features, **red** boxes indicate the predictions of the draft model, and **blue** modules with snowflake icons represent the use of target LLM parameters, which are not subject to training.

### Figure 7 (p.7) ⭐深度解读
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p07.png]]
> [!quote] caption
> Speedup ratios of EAGLE with and without the use of tree attention. The evaluation dataset is MT-bench, with the temperature parameter set to 0.

> [!tip] 技术解读（多模态）
> # Figure 7 Description

**Chart type:** Grouped bar chart comparing three configurations across six LLMs.

**Axes/Series:**
- **X-axis:** Six target models — Vicuna {7B, 13B, 33B} and LLaMA2-Chat {7B, 13B, 70B}
- **Y-axis:** Speedup ratio (0–3, relative to Vanilla = 1.00×)
- **Three bars per model:**
  - 🔵 Blue: EAGLE **w/** tree attention (~2.78–3.07×)
  - 🟢 Green: EAGLE **w/o** tree attention (~2.27–2.66×)
  - 🟠 Orange: Vanilla autoregressive decoding (baseline, 1.00×)

**Key technical takeaway:** Adding tree attention yields a consistent ~0.4–0.5× additional speedup on top of EAGLE's chain decoding, pushing peak speedups to ~3× across both Vicuna and LLaMA2-Chat families — confirming that structured speculative trees generalize across model sizes.

**Caption (verbatim):**
> Figure 7: Speedup ratios of EAGLE with and without the use of tree attention. The evaluation dataset is MT-bench, with the temperature parameter set to 0.

### Figure 8 (p.8) ⭐深度解读
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p08.png]]
> [!quote] caption
> Performance of draft models with varying inputs. The target LLM is Vicuna 7B, and the test dataset is MT-bench.

> [!tip] 技术解读（多模态）
> **Description (Figure 8):**

The figure is a 2×4 grid of line plots evaluating four draft-model input configurations on the MT-bench dataset with Vicuna-7B as the target LLM. Rows vary temperature (T=0, T=1); columns report four metrics over training epochs (1→6): walltime Speedup, average acceptance length (τ), acceptance rate with precise inputs (0-α), and acceptance rate with one imprecise feature (1-α). Four curves are compared: feature&shifted-token (blue), feature&unshifted-token (orange), feature (red), and token (green).

**Key takeaway:** The "feature + shifted-token" combo dominates every metric and temperature, while token-only inputs perform worst—showing that temporal feature shifts give the draft model substantially richer context than tokens alone.

**Caption (verbatim):**
"Figure 8: Performance of draft models with varying inputs. The target LLM is Vicuna 7B, and the test dataset is MT-bench. Speed refers to the walltime speedup ratio, τ denotes the average acceptance length, 0-α represents the acceptance rate with entirely precise inputs, 1-α indicates the acceptance rate when the input includes one imprecise feature, and T refers to the temperature."

### Figure 9 (p.12) ⭐深度解读
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p12.png]]
> [!quote] caption
> However, the optimal tree structure is likely context-dependent. For instance, as batch size increases and redundant computational resources decrease, a smaller tree might be preferable. Tuning the draft structure could potentially lead to improved performance. query query

> [!tip] 技术解读（多模态）
> ## Figure 9 Description

**Architecture / Components:**
- **Left tree (with tree attention):** A root "query" node expands into 4 children (k=4). The branching is asymmetric — the leftmost branch is the deepest (≈5 levels) and widest, while rightmost branches terminate quickly. Nodes represent draft tokens; edges encode parent→child continuation candidates.
- **Right chain (no tree attention):** A linear vertical sequence descending from "query" — a single path, representing the standard chain-structured draft used in vanilla speculative sampling.

**Data Flow:** Start at the query, autoregressively expand the draft model for 5 forward passes to populate the tree/chain, then the target LLM verifies all nodes in one parallel pass, accepting/rejecting along each path.

**Key Technical Takeaway:** Branching factor and depth are not uniform — high-probability continuations are grown deeper and wider, concentrating speculative budget where acceptance likelihood is greatest, which is the central efficiency lever over chain drafting.

## Caption (verbatim)

> Figure 9: Structure of EAGLE's draft. The left side shows the draft structure when tree attention is employed, while the right side depicts the draft structure without the use of tree attention.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
L_{reg} = \text{Smooth L1}(f_{i+1}, \text{Draft\_Model}(T_{2:i+1}, F_{1:i})).
$$

$$
{p}_{i+2}=\text{Softmax}(\text{LM\_Head}({f}_{i+1})), \\ \hat{p}_{i+2}=\text{Softmax}(\text{LM\_Head}(\hat{f}_{i+1})), \\ L_{cls} = \text{Cross\_Entropy}({p}_{i+2},\hat{p}_{i+2}).
$$

## 相关论文

- [[dflash-block-diffusion-for-flash-speculative-decoding]] — DFlash: Block Diffusion for Flash Speculative Decoding
- [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] — DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation
- [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]] — EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees
- [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] — LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and Verification
- [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] — SpecExtend: A Drop-in Enhancement for Speculative Decoding of Long Sequences
- [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] — JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting

## 技术点深读（DEEP）

![[deep/eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/eagle-speculative-sampling-requires-rethinking-feature-uncertainty.txt`（50318 字符）供引用检索。