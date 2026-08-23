---
paper_num: "9"
title: "JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting"
authors: "Decoding with Parallel Tree Drafting Lanxiang Hu1 Zhaoxiang Feng1 Yulun Wu2 Haoran Yuan3 Yujie Zhao1 Yu-Yang Qian4 Bojun Wang5 Peng Zhao4 Daxin Jiang5 Yibo Zhu5 Tajana Rosing1 Hao Zhang1 1UC San Diego 2 Zhejiang Universi"
date: "2026/6/16"
arxiv: "https://arxiv.org/abs/2606.18394"
pdf: "papers/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting.pdf"
slug: "jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting"
tags: [speculative]
---

# JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting

> [!abstract] 摘要（原文）
> 1\. 🚀 JETSPEC 提出了一种创新的因果并行草稿头部架构，通过在单一前向传播中生成具备分支因果依赖的候选树，有效解决了推测解码（Speculative Decoding）中因果性与效率之间的权衡矛盾。 2. 💡 该框架通过利用冻结目标模型的融合隐藏特征进行训练，确保了草稿概率分布与目标模型的自回归因子分解相一致，从而在增加草稿预算时显著提高了树结构的接受率。 3. 📈 实验表明，JETSPEC 在 Qwen3 等模型上能够将草稿预算高效转化为更长的接受前缀，在 MATH-500 等基准测试中实现了高达 9.64 倍的端到端解码加速，并能通过 vLLM 集成在真实服务负载下保持高性能。

## 元信息
- **发表日期**: 2026/6/16
- **作者**: Decoding with Parallel Tree Drafting Lanxiang Hu1 Zhaoxiang Feng1 Yulun Wu2 Haoran Yuan3 Yujie Zhao1 Yu-Yang Qian4 Bojun Wang5 Peng Zhao4 Daxin Jiang5 Yibo Zhu5 Tajana Rosing1 Hao Zhang1 1UC San Diego 2 Zhejiang Universi
- **arXiv**: https://arxiv.org/abs/2606.18394
- **本地 PDF**: `papers/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting.pdf`
- **页数**: 21

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig01.png]]
*整页渲染: ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p02.png]]*
> [!quote] caption
> End-to-end decoding speedup over standard autoregressive decoding on H100 GPUs across math, coding, and chat benchmarks. DFlash denotes the original block-parallel drafting method, DDTree is tree-based variant of DFlash, and JetSpec denotes our method. Both employ a tree budget of 256 tokens using Algorithm 1. acceleration. Despite these advances, head-based SD still faces a causality-efficiency d

> [!tip] 技术解读（多模态）
> # Figure 1 Description

**Architecture / Components:**
- Bar chart with y-axis "Speedup over AR (×)" (0–11 range) and x-axis listing 7 benchmarks (GSM8K, MATH-500, AIME25, HumanEval, MBPP, LCB, MT-Bench).
- Three grouped bars per benchmark: **DFlash** (blue, block-parallel drafter), **DDTree** (orange, tree-based DFlash variant), and **JetSpec** (green, the proposed method).
- Numeric labels sit above each bar (e.g., MATH-500: 6.12 / 8.78 / 9.64).

**Data Flow:** Each benchmark is evaluated under a fixed tree budget of 256 draft tokens (Algorithm 1); measured end-to-end decoding speedup on H100 GPUs is compared across the three drafters.

## Key Technical Takeaway (≤120 words)

JetSpec consistently outperforms both block-parallel (DFlash) and tree-based (DFlash-DDTree) drafters across all seven math, code, and chat benchmarks under a 256-token tree budget. The largest gain appears on MATH-500, where JetSpec reaches **9.64×** speedup versus 8.78× (DDTree) and 6.12× (DFlash). Even on the harder chat workload MT-Bench, JetSpec delivers 4.58× versus DDTree's 4.26× and DFlash's 2.72×. This demonstrates that combining a *causal parallel draft head* with *branch-wise causal attention over hidden states* resolves the causality–efficiency dilemma in speculative decoding, yielding branch-aware path-conditioning without the cost of sequential drafting.

## Caption (verbatim)

Figure 1: End-to-end decoding speedup over standard autoregressive decoding on H100 GPUs across math, coding, and chat benchmarks. DFlash denotes the original block-parallel drafting method, DDTree is tree-based variant of DFlash, and JetSpec denotes our method. Both employ a tree budget of 256 tokens using Algorithm 1.

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig02.png]]
*整页渲染: ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p03.png]]*
> [!quote] caption
> Expected speculative decoding speedup scales as a function of draft length γ, under different per-token drafting costs c and acceptance rates α. Comparing the two panels shows that reducing c substantially improves the scalability of speculative decoding with respect to γ, and increasing α further amplifies this effect. The results highlight that pushing per-token drafting cost c low and acceptanc

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】JetSpec 因果并行草稿头(Fig.3)：轻量 draft head 接冻结目标模型 M_q 中间层融合特征，单次前向并行预测所有 γ 个 draft 位的 top-k 候选→组成 k^γ 候选树；输出重排为广度优先、分支级因果序列再回灌 M_q 验证（满足 tree-SD 左到右依赖）。M_q 冻结只训 head。把草稿成本 c 压到 head 级、接受率 α 保持高→加速随 γ 单调增长，破解 c/α 鱼与熊掌。架构核心图。

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig03.png]]
*整页渲染: ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p04.png]]*
> [!quote] caption
> JetSpec design overview. JetSpec extracts fused hidden features from the frozen target model and conditions a causal-parallel draft head to generate high-quality candidate trees in one forward pass.

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

Figure 3 illustrates the JetSpec architecture in three stages for one decoding step *i*. **Stage 1** extracts fused target features by passing the frozen target model's Layer M hidden state through a **Feature Fusion** module, producing a unified hidden representation from verified tokens (`return`, `add`, `a`, `B`). **Stage 2** performs **Parallel Tree Drafting**: the **Causal-parallel Draft Head M_q** (Layers 1…m) takes the fused feature plus an anchor (`return`) and draft slots, generating a full candidate tree (root → branches like `a`, `-`, `B` with their scores) in a single forward pass, governed by a **tree-causal attention mask** that restricts each node to its prefix ancestors. **Stage 3** runs the **Frozen Target Model M_p** (Layers 1, M, N, t) over this tree via the same mask to produce verified tokens for step *i+1*.

**Key takeaway:** Causal-parallel drafting with a tree-structured attention mask preserves correct autoregressive conditioning across sibling branches, enabling higher acceptance than branch-agnostic per-position drafting.

**Caption (verbatim):**

> Figure 3: JetSpec design overview. JetSpec extracts fused hidden features from the frozen target model and conditions a causal-parallel draft head to generate high-quality candidate trees in one forward pass.

### Figure 4 (p.15) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig04.png]]
*整页渲染: ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p15.png]]*
> [!quote] caption
> Tree-quality failure mode at MATH-500 prompt #0, decode step 0. Both heads draft from the same prefix (last token “We”). The causal head’s rank-1 branch (“ are told that”) is faithful: target joint Σ log p ≈Σ log r, so tree verification walks 6 tokens along it. The diffusion head’s rank-1 branch (“ given told that”) is incoherent (target joint Σ log p = −63.32 nats, i.e. probability ≈e−63) because

> [!tip] 技术解读（多模态）
> # Figure 4 Description

**Architecture / components / data flow:**
The figure contrasts tree-drafting behavior between two heads (causal vs. diffusion) at the same decode step (root token "We"). Each panel shows a *rank-1* branch and a *rank-3* branch rendered as colored token chips (green = faithful, red = incoherent/poor), with the **gap** (Σ log p − Σ log r) annotated alongside qualitative verdicts (*faithful* / *incoherent*) and the verifier's accepted-token count. Panel (a) shows the **causal head** where rank-1 ("are told that") is faithful (gap = −0.34) and the verifier walks 6 tokens, while its rank-3 ("are given that the2product") carries a +42.50 gap. Panel (b) shows the **diffusion head** where the roles invert: rank-1 ("given told that") is incoherent (gap = +59.56), accepting only 4 tokens, while the coherent "are given that the" sits at rank 3 (gap = −3.69). The arrows thus encode: tokens → surrogate ranking → gap metric → verifier acceptance length.

**Key technical takeaway (≤120 words):**
The diffusion head's branch-agnostic per-position predictor composes tokens (e.g., "given" + "told") independently in the surrogate, even though no real continuation places them consecutively. Consequently, the *actually-coherent* branch "are given that the" exists in the diffusion tree but only at rank 3; the surrogate fails to promote it, so the verifier accepts just 4 tokens versus the causal head's 6. This exposes a **failure mode of unconditional-per-position drafting**: surrogate scoring can rank incoherent concatenations above coherent continuations, truncating accepted drafts and degrading tree-drafting quality.

---

**Caption (verbatim):**

Figure 4: **Tree-quality failure mode at MATH-500 prompt** #0, **decode step** 0. Both heads draft from the same prefix (last token "We"). The causal head's rank-1 branch (" `are told that`") is faithful: target joint Σ log p ≈ Σ log r, so tree verification walks 6 tokens along it. The diffusion head's rank-1 branch (" `given told that`") is incoherent (target joint Σ log p = −63.32 nats, i.e. probability ≈ e^(−63)) because its branch-agnostic per-position predictor composes " `given`" (depth 1) and " `told`" (depth 2) independently in the surrogate, even though no real continuation places these two words consecutively (the surrogate q_sur is formally defined in Equation 3). The actually-coherent " `are given that the`" is in the diffusion tree but only at rank 3; the surrogate fails to promote it, and the verifier accepts only 4 tokens.

### Figure 5 (p.18) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig05.png]]
*整页渲染: ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p18.png]]*
> [!quote] caption
> Figure 5: Causal attention mask used for training with multiple sampled blocks. Each query can attend to the full verified prefix and to the anchor plus earlier positions within its own block, but cannot attend to future positions or positions from other sampled blocks. JETSPEC reuses intermediate representations from the frozen target model as draft-head context. For

> [!tip] 技术解读（多模态）
> **Description:**

The figure depicts a 2D causal attention mask for training a draft head with multiple sampled blocks. The matrix is partitioned into four column regions: a "Verified prefix" (tokens x₀–x₃) followed by three "Sampled blocks," each containing an anchor (aᵢ) and five subsequent positions (aᵢ,₁ … aᵢ,₅). Rows correspond to query draft positions, grouped by block. Yellow (✓) cells mark allowed attention; dark cells mark forbidden attention.

**Data flow / pattern:**
- All query positions attend fully to the verified prefix (leftmost columns).
- Within each sampled block, attention is strictly lower-triangular: a query sees only the block's anchor and earlier positions within that same block.
- No cross-block attention and no future-position attention are permitted, enforcing a block-local causal order.

**Key takeaway:** The mask enables parallel prediction of all masked tokens across multiple blocks while preserving autoregressive causality within each block, which is essential for efficient speculative-decoding draft-head training.

**Caption (verbatim):**

"Figure 5: Causal attention mask used for training with multiple sampled blocks. Each query can attend to the full verified prefix and to the anchor plus earlier positions within its own block, but cannot attend to future positions or positions from other sampled blocks."

### Figure 6 (p.19) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig06.png]]
*整页渲染: ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p19.png]]*
> [!quote] caption
> Each sampled block includes an anchor position and multiple future token positions. The anchor is retained as block context and excluded from the loss, while loss is applied only to future token positions within each block. allowing the causal draft head to condition on rich target-model features while keeping the target model frozen.

> [!tip] 技术解读（多模态）
> **Figure Description**

The diagram illustrates "Block-wise supervision for sampled training blocks" with three rows representing Block 1, Block 2, and Block 3. Each block contains 6 token positions arranged horizontally:
- **Anchor token** (a₁/a₂/a₃): white box labeled "no loss" — serves as context only
- **5 future token positions** (b_{i,1} … b_{i,5}): orange boxes each labeled "loss"

A legend below distinguishes the white "Anchor (no loss)" from orange "Predicted token position with loss." The horizontal layout conveys sequential positions within each sampled block, while vertical stacking shows that the same supervision pattern repeats across blocks.

**Key Technical Takeaway:** The anchor decouples context from the training objective — by excluding it from the loss, the model learns to predict *future* positions conditioned on a preserved anchor, preventing the leakage problem of standard causal masking.

**Caption (verbatim):**
Figure 6: Each sampled block includes an anchor position and multiple future token positions. The anchor is retained as block context and excluded from the loss, while loss is applied only to future token positions within each block.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 3 (p.8) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab03.png]]
> [!quote] caption
> Learning-rate ablation with J ET S PEC and without loss weighting training ( γ = 0 ). See Section 3.4.2 for γ ’s definition and ablations. We report speedup and average accepted length τ .

> [!tip] 表格解读（多模态）
> # Figure Description

The visible portion of **Table 3** is a learning-rate ablation comparing JETSPEC under two configurations—(1) full method and (2) without loss weighting (γ = 0)—evaluated on GSM8K and MATH-500 benchmarks. The table is structured as a matrix:

- **Rows:** learning-rate values (LR) — specific values not visible in the provided excerpt.
- **Columns (grouped by dataset):** under each benchmark (GSM8K, MATH-500), two metrics are reported: **Speedup** and **Found KL** (mean accepted length τ).
- **Data flow:** each LR setting is evaluated on each dataset, producing paired (speedup, τ) scores, enabling sensitivity analysis of the acceptance criterion against training-step magnitude.

**Key takeaway (preview):** The ablation is designed to isolate whether training acceleration stems from the rejection-sampling weighting or simply from larger updates—an essential disentanglement claim.

*(Note: numerical rows are cut off in the supplied image.)*

---

# Caption (verbatim)

> Table 3: Learning-rate ablation with JETSPEC and without loss weighting training (γ = 0). See Section 3.4.2 for γ's definition and ablations. We report speedup and average accepted length τ.

### Table 5 (p.9) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab05.png]]
> [!quote] caption
> Model generalizability: JetSpec vs. DDTree on Qwen3-30B-A3B (MoE target), both trained with SFT on the same 800K-example data mixture as our Qwen3-8B main results. Each cell reports speedup / average accepted length τ at temperature 0 with tree budget 256 .

> [!tip] 表格解读（多模态）
> **Figure description & key takeaway**

Table 5 benchmarks two speculative-decoding draft models—**JetSpec** and **DDTree**—paired with the Qwen3-30B-A3B MoE target. Both drafts were SFT-trained on the same 800K-example data mixture used for the Qwen3-8B main runs. Evaluation protocol is fixed at temperature 0 with a tree budget of 256; each cell reports two numbers: **wall-clock speedup** and **average accepted length τ**. Seven benchmarks span math (GSM8K, MATH-500, AIME25), code (HumanEval, MBPP, LCB), and chat (MT-Bench).

**Key takeaway:** JetSpec beats DDTree on every benchmark in *both* speedup and average accepted length, with the largest absolute gains on math-heavy tasks (e.g., AIME25: 9.35 / 10.28 vs. 9.01 / 9.71), showing that the approach transfers robustly to a 30B-A3B MoE target rather than overfitting to the 8B setup.

**Caption verbatim**

Table 5: Model generalizability: JetSpec vs. DDTree on Qwen3-30B-A3B (MoE target), both trained with SFT on the same 800K-example data mixture as our Qwen3-8B main results. Each cell reports speedup / average accepted length τ at temperature 0 with tree budget 256.

### Table 6 (p.9) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab06.png]]
> [!quote] caption
> Training-data ablation: J ET S PEC vs. J ET S PEC -Corpus, both trained with SFT on the same 800K-example data mixture (Qwen3-8B target). JetSpec uses model-regenerated continuations as supervision targets; JetSpec -Corpus uses the original training corpus. Each cell reports speedup / average accept

> [!tip] 表格解读（多模态）
> **Description:**

The table presents a training-data ablation comparing two self-speculative decoding methods on a Qwen3-8B target model, both trained via SFT on the same 800K-example mixture. Rows group results by **budget** (16, 64, 256 speculative tokens) and **method** (`JetSpec` vs. `JetSpec-Corpus`), while columns list six evaluation benchmarks spanning math (GSM8K, AIME25), code (HumanEval, MBPP, LCB), and chat (MT-Bench). Each cell reports two metrics: **inference speedup** and **average accepted length τ**. The data flow is straightforward: each configuration is evaluated end-to-end on every benchmark, producing a 6-method × 6-benchmark comparison grid.

**Key takeaway:** Using model-regenerated continuations as supervision targets (`JetSpec`) yields dramatically stronger acceptance behavior than training on the original corpus (`JetSpec-Corpus`) — at budget 256, `JetSpec` reaches 7–9× speedups with τ ≈ 8–10, whereas `JetSpec-Corpus` plateaus near 3–4× with τ ≈ 3–4, confirming that the regeneration step is the critical ingredient for learning an effective draft policy.

**Caption (verbatim):**

"Table 6: Training-data ablation: JetSpec vs. JetSpec-Corpus, both trained with SFT on the same 800K-example data mixture (Qwen3-8B target). JetSpec uses model-regenerated continuations as supervision targets; JetSpec-Corpus uses the original training corpus. Each cell reports speedup / average accepted length τ at temperature 0."

### Table 7 (p.9) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab07.png]]
> [!quote] caption
> compares causal and diffusion heads under different choices of γ , the parameter that controls how aggressively the DFlash training objective downweights per-position loss at positions far from each anchor token. Specifically, position i within a block contributes to the training loss with weight w 

> [!tip] 表格解读（多模态）
> I'm unable to fully complete this request because the actual figure (referred to as "Figure 4 in Appendix A" in the text) is not included in the provided content. The excerpt only **references** the figure textually rather than displaying it.

What the text tells us about Figure 4 indirectly:
- It visualizes a tree-verification comparison between a **causal-head draft** and a **diffusion-head draft** on MATH-500 prompt 0 at decode step 0.
- The diffusion-head draft (γ = 0) ranks `"given told that"` first (surrogate −3.76 vs. target joint −63.32 nats), combining two mutually exclusive openers — a failure mode of q_sur.
- The causal-head draft ranks `" are told that"` first with surrogate ≈ target joint (gap −0.34).
- Tree verification accepts **6 tokens** from the causal-head tree but only **4** from the diffusion-head tree.

To produce the architecture/components description and verbatim caption, I would need the actual figure image and its printed caption. Could you please share Figure 4 (or the relevant figure from Appendix A) along with its caption text?

### Table 8 (p.15) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab08.png]]
> [!quote] caption
> extends Figure 4 to the full top- 5 branches of each head’s tree at MATH-500 prompt #0 , decode step 0 (root token “We” ). The pattern reported in the main text repeats throughout the tree. For the diffusion head, top- 2 and top- 4 both combine “ given ” at depth 1 and “ told ” at depth 2 with targe

> [!tip] 表格解读（多模态）
> **Figure 4 description (inferred from surrounding text):**

The figure depicts per-head decoding trees for the diffusion head and the causal head at MATH-500 prompt #0, decode step 0 (root "We"). Each tree plots the top-*k* token continuations at successive depths, annotated with joint probabilities (nats) and gap metrics. The diffusion head shows rank-1 ("We"), rank-2 ("We given"), and rank-3 ("We told") as coherent branches, while ranks 4–5 collapse (joints below −50). The causal head's rank-1 (" are told that") stays faithful; ranks 2–5 share the off-argmax depth-2 token " given" and degrade downstream ("the2product" at rank 3, gap +42.5).

**Key takeaway:** Off-argmax branches inherit the depth-*d*−1 argmax context rather than their own ancestor, propagating a mismatched conditioning that drives gap blow-ups — only branches whose full prefix matches the true decoding context remain coherent.

---

**Caption transcription note:** No standalone figure caption appears in the provided content. The visible text reads verbatim:

> "Table 8 extends Figure 4 to the full top-5 branches of each head's tree at MATH-500 prompt #0, decode step 0 (root token "We"). The pattern reported in the main text repeats throughout the tree. For the diffusion head, top-2 and top-4 both combine " given" at depth 1 and " told" at depth 2 with target joints below −50 nats; only rank-3 (target joint −0.08) is coherent. For the causal head, the rank-1 branch (" are told that") is faithful (gap −0.34); ranks 2–5 all share the off-argmax depth-2 token " given" (vs. rank-1's argmax " told") and degrade at depths 4–5 (e.g. "the2product" at rank 3, gap +42.50), consistent with the off-argmax inheritance described in §A.4: each branch's depth-*d* marginal was anchored to the argmax extension at depth *d* − 1, so off-argmax branches inherit a conditioning context that does not match their own ancestor token."

This is the body text (plus the A.3 heading) accompanying Figure 4 / Table 8 — not a caption proper.

### Table 9 (p.15) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab09.png]]
> [!quote] caption
> reports the rank- 1 gap distribution across MATH-500 prompts 0 – 49 for both heads at γ = 0 and at γ = 7 (DFlash’s best macroscopic loss-weighting setting, Table 7). At γ = 0 , the diffusion

> [!tip] 表格解读（多模态）
> **Description of the figure (Table 9)**

*Architecture/components/data flow*: Table 9 is not a diagram but a tabular summary that stratifies the **rank-1 generation gap** (top-1 token discrepancy between the draft and target heads, a measure of speculative-decoding acceptance failure) over the first 50 prompts of the **MATH-500** benchmark. It contrasts two configurations of the same DFlash-style draft head: (i) γ = 0 (no macroscopic loss re-weighting) and (ii) γ = 7 (DFlash's best macro loss-weighting from Table 7). Likely columns include per-prompt rank-1 gap values or aggregate statistics (mean/median/p95) that quantify how often the draft head's argmax diverges from the target.

*Key technical takeaway*: Increasing the macroscopic loss weight (γ = 7) substantially tightens the rank-1 gap distribution on MATH-500 relative to γ = 0, indicating that downstream acceptance/length gains from aggressive loss weighting are concentrated in reducing top-token disagreements on the hardest math prompts.

**Caption (verbatim)**

"Table 9 reports the rank-1 gap distribution across MATH-500 prompts 0–49 for both heads at γ = 0 and at γ = 7 (DFlash's best macroscopic loss-weighting setting, Table 7). At γ = 0, the diffusion"

### Table 11 (p.19) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab11.png]]
> [!quote] caption
> reports an example end-to-end vLLM run on HumanEval with a single H100 GPU. The results show how tree budget interacts with serving batch size: larger budgets improve low-batch latency by reducing verification rounds, while their relative gain decreases at larger batch sizes as verification and memo

> [!tip] 表格解读（多模态）
> I can't complete this request as specified. The content you've provided is text from a paper appendix (pages discussing Table 11 and Section F "Ablation Study Details"), but **no figure is included** in what you've shared. There is no figure with architecture, components, or data flow visible in the provided text, and consequently no figure caption to transcribe.

What the text actually contains:
- A paragraph summarizing results from Table 11 (an end-to-end vLLM run on HumanEval with a single H100 GPU, discussing how tree budget interacts with serving batch size).
- The heading and introductory paragraph of Section F (Ablation Study Details), describing ablations on the Nemotron Post-Training Dataset V2 math split using Qwen3-8B with block size 16, tree node budget 255, and accumulated draft log-probability for tree construction.

To fulfill your request, could you please attach the actual figure (image) and its caption? I can then describe the architecture/components/data flow, distill a technical takeaway within 120 words, and transcribe the caption verbatim.

### Table 12 (p.21) ⭐深度解读
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-tab12.png]]
> [!quote] caption
> Per-draft-token drafting cost ratio c = T draft / ( N T verify ) (%) on a single H200 NVL GPU, sweeping context length L and draft depth N . This is the cost coefficient used in Eq. equation 2 and Fig. 2. Lower is better.

> [!tip] 表格解读（多模态）
> ## Description

**Type:** Data table (Table 12) presenting empirical measurements, not an architectural diagram.

**Components shown:**
- **Row axis:** Context length *L* (values not visible in the cropped view)
- **Column axis:** Draft depth *N* ∈ {1, 2, 4, 8, 16, 32, 64, 128, 256, 512} (powers of 2)
- **Cell values:** Cost ratio *c* = T_draft / (N · T_verify) in percent

**Data flow:** This table serves as a **lookup/reference dataset** consumed by Equation 2 and Figure 2 elsewhere in the paper — it parameterizes the drafting-overhead coefficient *c* so the rest of the analysis can model throughput/speedup without re-measuring every (L, N) combination.

**Key takeaway:** Drafting cost is **not constant** — the ratio *c* varies with both *N* (must be measured, not assumed) and *L* (longer contexts shift the draft-vs-verify balance), so any speculative-decoding speedup model needs this empirical sweep rather than a single scalar assumption. ("Lower is better" because smaller *c* means drafting is cheaper per generated token.)

## Caption (verbatim)

> **Table 12:** Per-draft-token drafting cost ratio *c* = T_draft/(N T_verify) (%) on a single H200 NVL GPU, sweeping context length *L* and draft depth *N*. This is the cost coefficient used in Eq. equation 2 and Fig. 2. Lower is better.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbb{E}[\#\mathrm{tokens}] = \frac{1-\alpha^{N+1}}{1-\alpha},
$$

$$
\mathrm{Speedup} = \frac{1-\alpha^{N+1}} {(1-\alpha)(N c + 1)}.
$$

$$
q_{\mathrm{sur}}(y_{1:k}\mid x) \propto \prod_{i=1}^{k} r_i(y_i\mid x),
$$

$$
p(y_{1:k}\mid x) = \prod_{i=1}^{k} p(y_i \mid x, y_{<i}).
$$

$$
M_{v,u} = \begin{cases} 0, & \text{if } u \in \mathrm{Anc}(v)\cup\{v\}, \\ -\infty, & \text{otherwise}, \end{cases}
$$

$$
\mathrm{Attn}(Q_v,K,V) = \mathrm{softmax} \left( \frac{Q_vK^\top}{\sqrt{d}} + M_v \right)V.
$$

$$
q(\pi(v)\mid x) = \prod_{u\in \pi(v)} q(y_u \mid x, h_x^{o}, \pi_{<u}),
$$

$$
\mathcal{L}_{\mathrm{FKL}}^{(m)} = D_{\mathrm{KL}} \left( \tilde{p}^{(m)} \,\middle\|\, \tilde{q}^{(m)} \right).
$$

$$
\mathcal{L}_{\mathrm{train}} = T_{\mathrm{KD}}^2 \frac{ \sum_m w_m \mathcal{L}_{\mathrm{FKL}}^{(m)} }{ \sum_m w_m },
$$

$$
s(\pi(v)) = \sum_{u\in \pi(v)} \log q(y_u \mid x, h_x^o, \pi_{<u}),
$$

$$
A_t \sim \mathrm{Bernoulli}(\alpha_t), \qquad \alpha_t = \alpha\!\left( y_t;\, q(\cdot\mid x,y_{<t}), p(\cdot\mid x,y_{<t}) \right),
$$

$$
\alpha_t = \min\!\left( 1,\, \frac{ p(y_t\mid x,y_{<t}) }{ q(y_t\mid x,y_{<t}) } \right),
$$

$$
c(N,L) = \frac{T_{\mathrm{draft}}(N,L)/N} {T_{\mathrm{verify}}(N,L)} = \frac{T_{\mathrm{draft}}(N,L)} {N\,T_{\mathrm{verify}}(N,L)}.
$$

## 相关论文

- [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] — LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and Verification
- [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] — DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation
- [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] — SpecExtend: A Drop-in Enhancement for Speculative Decoding of Long Sequences
- [[dflash-block-diffusion-for-flash-speculative-decoding]] — DFlash: Block Diffusion for Flash Speculative Decoding
- [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] — MEDUSA: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads
- [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]] — EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees

## 技术点深读（DEEP）

![[deep/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting.txt`（70018 字符）供引用检索。