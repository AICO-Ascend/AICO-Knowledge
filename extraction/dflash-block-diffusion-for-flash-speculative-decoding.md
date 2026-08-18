---
paper_num: "7"
title: "DFlash: Block Diffusion for Flash Speculative Decoding"
authors: "Jian Chen 1 Yesheng Liang 1 Zhijian Liu 1"
date: "2026/2/4"
arxiv: "https://arxiv.org/abs/2602.06036"
pdf: "papers/dflash-block-diffusion-for-flash-speculative-decoding.pdf"
slug: "dflash-block-diffusion-for-flash-speculative-decoding"
tags: [speculative]
---

# DFlash: Block Diffusion for Flash Speculative Decoding

> [!abstract] 摘要（原文）
> 1\. 🚀 DFlash 提出了一种利用轻量级块扩散（block diffusion）模型进行并行草稿生成的投机解码框架，有效解决了 autoregressive LLM 序列化解码导致的推理延迟瓶颈。 2. 🧠 该方法通过将 target LLM 的隐藏层特征注入 draft model 的 KV cache 中，实现了对未来 token 块的精确条件建模，从而显著提升了草稿的预测质量与接受率。 3. 📈 实验表明，DFlash 在多种主流模型和任务上实现了超过 6 倍的无损加速，其性能相较于目前最先进的投机解码方法 EAGLE-3 提升了约 2.5 倍。

## 元信息
- **发表日期**: 2026/2/4
- **作者**: Jian Chen 1 Yesheng Liang 1 Zhijian Liu 1
- **arXiv**: https://arxiv.org/abs/2602.06036
- **本地 PDF**: `papers/dflash-block-diffusion-for-flash-speculative-decoding.pdf`
- **页数**: 13

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p02.png]]
> [!quote] caption
> Speedup comparison between DFlash, EAGLE-3 against Autoregressive Decoding on Qwen3-8B (Yang et al., 2025) with the

> [!tip] 技术解读（多模态）
> **Description (73 words):**
The figure is a grouped bar chart comparing speculative decoding speedup across seven benchmarks (GSM8K, Math500, AIME25, HumanEval, MBPP, LiveCodeBench, MT-Bench) on Qwen3-8B. Baseline (gray) is normalized to 1.00×, EAGLE-3 (green) achieves 1.81×–2.23×, while DFlash (blue) ranges from 2.75× (MT-Bench) to 6.08× (Math500). **Key takeaway:** DFlash delivers 2.5×–3× higher speedup than EAGLE-3 across most benchmarks, peaking at 6.08× on Math500, demonstrating that block-diffusion drafting substantially outperforms autoregressive speculative decoding on reasoning-heavy tasks.

**Caption (verbatim):**
Figure 1. Speedup comparison between DFlash, EAGLE-3 against Autoregressive Decoding on Qwen3-8B (Yang et al., 2025) with the Transformers backend. Overall, DFlash achieves more than 2.5x higher speedup than EAGLE-3.

### Figure 2 (p.4) ⭐深度解读
![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p04.png]]
> [!quote] caption
> DFlash Inference Design. Hidden context features extracted from the target model are fused and injected into each draft layer’s

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】DFlash 设计：block-diffusion draft model 块内并行生成多 token（非逐 token 自回归）→低 draft 延迟；目标 LLM 先 prefill 产首 token 并取若干层隐藏态，concat 后过投影层融成 target context feature，注入每个 draft 层的 KV cache 并跨轮复用，持续提供上下文引导→接受长度随 draft 深度增长，无 token-embedding 稀释（优于 EAGLE 式输入融合）。架构核心图。

### Figure 3 (p.3) ⭐深度解读
![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p03.png]]
> [!quote] caption
> Draft cost of 1, 3, 5-layer DFlash and 1-layer EAGLE-3.

> [!tip] 技术解读（多模态）
> **Figure Description:**

Figure 3 is a grouped bar chart comparing draft-token generation latency across four configurations: 1-layer EAGLE-3 (gray) versus DFlash with 1 (blue), 3 (orange), and 5 (green) layers. The x-axis shows the number of draft tokens (4, 8, 16), and the y-axis shows latency in milliseconds.

**Key Technical Takeaway:**
EAGLE-3's latency grows steeply and roughly linearly with the number of draft tokens (~6→11→25 ms), reflecting its autoregressive per-token drafting cost. In contrast, DFlash latency stays nearly flat (~2–6 ms) across all budgets because it generates all draft tokens in parallel within a single forward pass—decoupling cost from speculation length.

**Caption (verbatim):**
Figure 3. Draft cost of 1, 3, 5-layer DFlash and 1-layer EAGLE-3.

### Figure 4 (p.5) ⭐深度解读
![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p05.png]]
> [!quote] caption
> DFlash training attention. The target model provides context features (blue) that condition the draft model. The input consists of clean prompt tokens p and clean response tokens r.

> [!tip] 技术解读（多模态）
> ## Figure 4 Description

**Architecture / Components:** The figure displays two attention-mask grids illustrating DFlash's training-time sparse attention. The left grid encodes the input sequence: prompt tokens *p* (blue), a contiguous block of clean response tokens *r* (yellow) used as anchors, and surrounding mask tokens *m* (green) for parallel prediction. Invisible tokens (white) sit between blocks. The right grid shows the resulting attention pattern: bidirectional attention *within* each block plus KV-injected target features, while attention *across* blocks is disallowed.

**Key technical takeaway:** By concatenating all blocks into a single sequence processed jointly under a sparse causal attention mask, DFlash trains multiple draft blocks in parallel within one forward/backward pass—achieving efficient joint training without inter-block information leakage.

## Caption (Verbatim)

**Figure 4. DFlash training attention.** The target model provides context features (blue) that condition the draft model. The input consists of clean prompt tokens *p* and clean response tokens *r*. Within each masked block, a subset of clean response tokens (yellow) is randomly sampled as anchors, while mask tokens *m* (green) mark positions for parallel prediction. Invisible tokens (white) denote the attention mask, which enforces causal consistency and prevents inter-block information leakage during training.

### Figure 5 (p.13) ⭐深度解读
![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p13.png]]
> [!quote] caption
> The loss decay makes training converge faster and better. A.5.2. RANDOM SAMPLING OF MASKED BLOCKS

> [!tip] 技术解读（多模态）
> ## Figure Description

**Type:** Line chart — *Acceptance Length vs. Training Epoch*

**Axes:**
- **X-axis:** Epoch (1 → 9)
- **Y-axis:** Acceptance Length on Math500 (≈4.3 → 6.5)

**Series (two curves):**
| Curve | Color | Behavior |
|---|---|---|
| With loss decay | Blue | Starts ≈4.45, climbs steeply to ≈6.4 by epoch 7, plateaus |
| Without loss decay | Orange | Starts ≈4.25, rises more slowly, catches up by epoch 7–8 |

**Key Technical Takeaway:** Both variants converge to similar final acceptance lengths (~6.35) by epoch 7, but the **exponentially decaying token weights (loss decay) yield substantially faster early-training convergence** — the blue curve leads by ~0.2–0.3 acceptance-length points during epochs 2–4 before the two merge. This validates emphasizing early-token accuracy in the draft-model objective.

---

**Caption (verbatim):**
> Figure 5. The loss decay makes training converge faster and better.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf{H}_{t} = \mathrm{RMSNorm} \left( W_c[\mathbf{H}^{(l_1)};\ldots;\mathbf{H}^{(l_5)}] \right).
$$

$$
\begin{aligned} \mathbf{Q}_i &= W_i^Q \mathbf{H}_d, \\ \mathbf{K}_i &= [W_i^K \mathbf{H}_t;\, W_i^K \mathbf{H}_d]_{\mathrm{seq}}, \\ \mathbf{V}_i &= [W_i^V \mathbf{H}_t;\, W_i^V \mathbf{H}_d]_{\mathrm{seq}}. \end{aligned}
$$

$$
5 \times 2048 \times 2048 \times 2 \approx 42\text{ MB},
$$

## 相关论文

- [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] — SpecExtend: A Drop-in Enhancement for Speculative Decoding of Long Sequences
- [[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]] — BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DIFFUSION LANGUAGE MODELS
- [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] — DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation
- [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] — LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and Verification
- [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] — JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting
- [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] — EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty

## 技术点深读（DEEP）

![[deep/dflash-block-diffusion-for-flash-speculative-decoding]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/dflash-block-diffusion-for-flash-speculative-decoding.txt`（54200 字符）供引用检索。