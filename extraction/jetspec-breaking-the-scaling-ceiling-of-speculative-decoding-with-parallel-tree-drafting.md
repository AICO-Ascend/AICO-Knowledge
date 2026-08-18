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
![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p02.png]]
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
![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p03.png]]
> [!quote] caption
> Expected speculative decoding speedup scales as a function of draft length γ, under different per-token drafting costs c and acceptance rates α. Comparing the two panels shows that reducing c substantially improves the scalability of speculative decoding with respect to γ, and increasing α further amplifies this effect. The results highlight that pushing per-token drafting cost c low and acceptanc

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】JetSpec 因果并行草稿头(Fig.3)：轻量 draft head 接冻结目标模型 M_q 中间层融合特征，单次前向并行预测所有 γ 个 draft 位的 top-k 候选→组成 k^γ 候选树；输出重排为广度优先、分支级因果序列再回灌 M_q 验证（满足 tree-SD 左到右依赖）。M_q 冻结只训 head。把草稿成本 c 压到 head 级、接受率 α 保持高→加速随 γ 单调增长，破解 c/α 鱼与熊掌。架构核心图。

### Figure 3 (p.4) ⭐深度解读
![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p04.png]]
> [!quote] caption
> JetSpec design overview. JetSpec extracts fused hidden features from the frozen target model and conditions a causal-parallel draft head to generate high-quality candidate trees in one forward pass.

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

Figure 3 illustrates the JetSpec architecture in three stages for one decoding step *i*. **Stage 1** extracts fused target features by passing the frozen target model's Layer M hidden state through a **Feature Fusion** module, producing a unified hidden representation from verified tokens (`return`, `add`, `a`, `B`). **Stage 2** performs **Parallel Tree Drafting**: the **Causal-parallel Draft Head M_q** (Layers 1…m) takes the fused feature plus an anchor (`return`) and draft slots, generating a full candidate tree (root → branches like `a`, `-`, `B` with their scores) in a single forward pass, governed by a **tree-causal attention mask** that restricts each node to its prefix ancestors. **Stage 3** runs the **Frozen Target Model M_p** (Layers 1, M, N, t) over this tree via the same mask to produce verified tokens for step *i+1*.

**Key takeaway:** Causal-parallel drafting with a tree-structured attention mask preserves correct autoregressive conditioning across sibling branches, enabling higher acceptance than branch-agnostic per-position drafting.

**Caption (verbatim):**

> Figure 3: JetSpec design overview. JetSpec extracts fused hidden features from the frozen target model and conditions a causal-parallel draft head to generate high-quality candidate trees in one forward pass.

### Figure 4 (p.15) ⭐深度解读
![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p15.png]]
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
![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p18.png]]
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
![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p19.png]]
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