---
paper_num: "6"
title: "BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DIFFUSION LANGUAGE MODELS"
authors: ""
date: "2025/3/12"
arxiv: "https://arxiv.org/abs/2503.09573"
pdf: "papers/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models.pdf"
slug: "block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models"
tags: [speculative]
---

# BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DIFFUSION LANGUAGE MODELS

> [!abstract] 摘要（原文）
> 1\. 🚀 本文提出了块扩散语言模型（BD3-LMs），通过在离散去噪扩散和自回归模型之间进行插值，成功解决了传统离散扩散模型在处理任意长度生成和推理效率上的限制。 2. 💡 研究人员开发了一种高效的训练算法及数据驱动的噪声调度策略，通过显著降低梯度方差，有效弥补了扩散模型与自回归模型在困惑度（Perplexity）上的性能差距。 3. 📈 实验结果表明，BD3-LMs 在多个语言建模基准测试中达到了离散扩散模型的新前沿水平，并支持长序列的高质量、并行化生成，同时提升了推理效率。

## 元信息
- **发表日期**: 2025/3/12
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2503.09573
- **本地 PDF**: `papers/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models.pdf`
- **页数**: 28

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p02.png]]
> [!quote] caption
> Block diffusion sequentially generates blocks of tokens by performing diffusion within each block and conditioning on previous blocks. By combining strength from autoregressive and diffusion models, block diffusion overcomes the limitations of both approaches by supporting variable-length, higher-quality generation and improving inference efficiency with KV caching and parallel sampling. network a

> [!tip] 技术解读（多模态）
> **Figure description**

The figure compares three text generation paradigms side-by-side, each illustrated with a token-level generation trace (highlighted spans = already-decided tokens, blue arrows = next decoding step):

1. **Autoregression** – generates tokens left-to-right (✓ high quality, ✓ arbitrary-length, ✓ KV caching, ✗ not parallelizable).
2. **Diffusion** – denoises a fixed-length window in parallel (✗ lower quality, ✗ fixed-length, ✗ no KV caching, ✓ parallelizable).
3. **Block Diffusion (proposed)** – applies within-block diffusion in parallel across the block's tokens, while chaining blocks autoregressively with KV-cached conditioning (✓ all four properties).

**Key takeaway:** Hybridizing diffusion *inside* blocks and autoregression *between* blocks inherits AR's KV cache and variable length while recovering diffusion's parallel sampling, yielding faster, higher-quality, length-flexible generation.

**Caption (verbatim):**
Figure 1: Block diffusion sequentially generates blocks of tokens by performing diffusion within each block and conditioning on previous blocks. By combining strength from autoregressive and diffusion models, block diffusion overcomes the limitations of both approaches by supporting variable-length, higher-quality generation and improving inference efficiency with KV caching and parallel sampling.

### Figure 2 (p.6) ⭐深度解读
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p06.png]]
> [!quote] caption
> Train NLLs for modeling the per-token likelihood on LM1B. Models are trained on 16B tokens. Training under the discrete diffusion NELBO, where half of the tokens in a batch are masked on average, has similar training variance to an AR model with a random batch size. so that Et∼U[0,1]q(xℓ t = m|xℓ) = 0.5. Thus, training on the diffusion objective involves estimating loss gradients with 2x fewer tok

> [!tip] 技术解读（多模态）
> **Description:**

The figure is a line plot titled "Train Negative Log-Likelihood (NLL) for Single Token Generation on LM1B," with training steps (0–250k+) on the x-axis and NLL (3.0–4.0) on the y-axis. Four curves are compared: **BD3-LM (NELBO)** (red, highly spiky throughout), **BD3-LM (Tuned schedule)** (purple, smooth), **AR** (orange, smooth baseline), and **AR (random batch size)** (green, spiky). All start near NLL ≈ 4.0 and decrease, but the spiky curves retain visible variance while tuned/standard AR settle near 3.15.

**Key takeaway:** Tuning the masking noise schedule is critical — it collapses BD3-LM training variance to match standard AR, while the default NELBO schedule yields variance comparable to AR trained with random batch sizes (an unfair comparison baseline).

**Verbatim caption:**

"Figure 2: Train NLLs for modeling the per-token likelihood on LM1B. Models are trained on 16B tokens. Training under the discrete diffusion NELBO, where half of the tokens in a batch are masked on average, has similar training variance to an AR model with a random batch size."

### Figure 3 (p.21) ⭐深度解读
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p21.png]]
> [!quote] caption
> x1 t x2 t x3 t x1 x2 x3 x1 t x2 t x3 t x1 x2 x3

> [!tip] 技术解读（多模态）
> ## Description of Figure 3

The figure visualizes a **6×6 specialized attention mask** for a block-diffusion language model with *L = 6* tokens and block size *L' = 2*. Three structurally distinct mask regions are highlighted:
- **Top-left 3×3 (Block Diagonal, M_BD, orange):** tokens *x¹ₜ, x²ₜ, x³ₜ* attend only to tokens within their own 2-token block (intra-block denoising).
- **Top-right 3×3 (Offset Block Causal, M_OBC, blue):** the denoising tokens cross-attend to conditional context blocks that were finalized *before* them.
- **Bottom 3×6 (Block Causal, M_BC, yellow):** context tokens *x¹, x², x³* update via standard block-causal attention across preceding context.

**Key technical takeaway:** The mask's block-level structure yields extreme sparsity, enabling FlexAttention to compile a single fused kernel (via `block_diff_mask` + `torch.compile`) that skips fully-masked regions, reducing both FLOPs and memory.

## Caption (verbatim)

**Figure 3: Example of Specialized Attention Mask**

### Figure 4 (p.22) ⭐深度解读
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p22.png]]
> [!quote] caption
> We can adapt the masking strategy from Fig. 3 to a FlexAttention compatible sparse masking function as above. This enables the creation of a customized JIT attention operation that uses significantly less memory with up to ≈5X speedup over the naive native scaled_dot_product_attention implementation in PyTorch (≥2.5) on a A5000 GPU with L = 1024 and batch size B = 16. 22

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**

The figure presents a PyTorch `block_diff_mask` function implementing a FlexAttention-compatible sparse attention mask for block diffusion. The data flow operates on query/key indices (`q_idx`, `kv_idx`) of length `2n` (concatenated `x_t` and `x_0` tokens):

1. **Token flagging** – classifies whether each position belongs to `x_t` (index < n) or `x_0` (index ≥ n) via `x0_flag_q` / `x0_flag_kv`.
2. **Block indexing** – maps positions to blocks using `block_size` (offset by n for `x_0`).
3. **Three composite masks** are computed and OR-combined:
   - **M_BD** (block diagonal): intra-block self-attention on noised tokens.
   - **M_OBC** (offset block-causal): cross-attention from `x_t` → earlier `x_0` blocks.
   - **M_BC** (block-causal): attended-to `x_0` blocks for updating `x_0`.

**Key takeaway:** This sparse boolean mask compiles into a JIT attention kernel, yielding up to ~5× speedup and significantly reduced memory over naive `scaled_dot_product_attention` (PyTorch ≥2.5) on an A5000 GPU (L=1024, B=16).

**Caption (verbatim):**

"Figure 4: We can adapt the masking strategy from Fig. 3 to a FlexAttention compatible sparse masking function as above. This enables the creation of a customized JIT attention operation that uses significantly less memory with up to ≈5X speedup over the naive native scaled_dot_product_attention implementation in PyTorch (≥ 2.5) on a A5000 GPU with L = 1024 and batch size B = 16."

### Figure 5 (p.23) ⭐深度解读
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p23.png]]
> [!quote] caption
> Attention computation using FlexAttention with our proposed custom mask.

> [!tip] 技术解读（多模态）
> ## Description

**Components & Data Flow:**
The figure presents a PyTorch code snippet implementing attention via `torch.nn.attention.flex_attention`. The pipeline is:

1. **Mask definition** — A `block_diff_mask` function is wrapped with `functools.partial` to bind `seq_len` and `block_size`, producing a custom block-wise sparsity pattern.
2. **Sparse block mask generation** — `create_block_mask` compiles this pattern into an optimized, hardware-friendly sparse mask of shape `(seq_len*2, seq_len*2)` on the target device.
3. **Kernel compilation** — `@torch.compile` with `mode="max-autotune-no-cudagraphs"` fuses and autotunes the computation in one pass (no cudagraph overhead, avoiding extra copies on small graphs).
4. **Attention execution** — `single_pass_block_diff_attn(q, k, v, block_mask)` calls `flex_attention` passing the precomputed mask, which dynamically skips unmasked blocks.

**Key Takeaway:** Replacing FlashAttention with this FlexAttention + custom block-mask recipe yields ≈15% speedup on an A5000 (L=1024, B=16) while preserving structured dependency constraints — block-level sparsity precomputation enables kernel fusion that FlashAttention cannot exploit.

## Caption (verbatim)

Figure 5: Attention computation using FlexAttention with our proposed custom mask.

### Figure 6 (p.26) ⭐深度解读
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p26.png]]
> [!quote] caption
> Sample from MDLM (Sahoo et al., 2024a) of length L = 1024 and T = 5K diffusion steps.

> [!tip] 技术解读（多模态）
> ## Description

This figure is **not an architecture diagram** but rather a **qualitative sample** illustrating the output of MDLM (Sahoo et al., 2024a), a masked diffusion language model. There is no architecture, component, or data-flow schematic — the "figure" is simply a rendered block of generated text wrapped between `<lendoftext>` sentinel tokens.

**Reading the output:** The generated passage (~1024 tokens, produced over 5K diffusion steps) is a topical mishmash blending multiple domains — art criticism (Paolo Capacotti, Giuliano/Angiolo/Leonetto Romei/Fiastri family), a museum crime anecdote (Franco Belzina's life, the broken candle, statue restoration), WWII history (Canadian/Italian POWs, statues removed from Cooper–Paris), and music industry references (record labels, festivals). **Key takeaway:** despite MDLM achieving competitive perplexity, the 1024-token sample exhibits topic drift, entity hallucination, and incoherent transitions — a common failure mode where diffusion-style generation lacks the autoregressive consistency that maintains long-range coherence in causal LMs.

## Caption (verbatim)

> **Figure 6:** Sample from MDLM (Sahoo et al., 2024a) of length *L* = 1024 and *T* = 5K diffusion steps. The generative perplexity of this sample under GPT2-Large is 69.26 and its entropy is 5.6.

### Figure 7 (p.27) ⭐深度解读
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p27.png]]
> [!quote] caption
> Sample from BD3-LM for block size L′ = 16 of length L = 2031 under T = 5K diffusion steps (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 24.3, and its entropy is 5.5. 27

> [!tip] 技术解读（多模态）
> **Figure description:** This figure is not an architecture diagram but a *sample generation* from BD3-LM, a block-wise discrete diffusion language model. It displays a single block of continuous narrative text (≈2,031 tokens) bounded by `<lendoftext>` end-of-document markers. The content is a coherent, multi-paragraph story about a girl traveling to Mexico, her mother being detained at a Bangkok airport on the way home, and broader commentary on Calais refugees — demonstrating that the model produces long, fluent, topic-consistent passages.

**Key technical takeaway:** Despite being trained with a context length of only L = 1,024, BD3-LM generates sequences of length L = 2,031 (nearly 2× the training window) using only T = 5K diffusion steps with block size L' = 16, yielding coherent text with GPT2-Large generative perplexity 24.3 and entropy 5.5 — showing block diffusion can extrapolate beyond training context.

**Caption (verbatim):**
> Figure 7: Sample from BD3-LM for block size L' = 16 of length L = 2031 under T = 5K diffusion steps (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 24.3, and its entropy is 5.5.

### Figure 8 (p.28) ⭐深度解读
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p28.png]]
> [!quote] caption
> Sample from an AR model (Sahoo et al., 2024a) with length L = 2003 (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 10.6 and its entropy is 5.5. 28

> [!tip] 技术解读（多模态）
> **Description**

This is not a traditional architecture diagram — it is a qualitative-output figure. The figure consists of a single boxed block of generated English text flanked by `<lendofftext>` sentinel tokens. The text is one long, unsegmented passage (~2,000 tokens) produced by an autoregressive language model; it drifts incoherently across multiple unrelated topics (an NFL game recap, a personal dispute over a tree in "Charlotte Gardens," architectural commentary on a building, and assorted trivia), with frequent name/topic confusions, fabricated quotes, and hallucinated entities. There are no labeled components, arrows, or data-flow stages — the "architecture" is implicit (AR transformer with context length 1024 producing a 2003-token sample, benchmarked against GPT2-Large, achieving perplexity 10.6 and entropy 5.5).

**Key takeaway:** The sample illustrates that even a long-context AR model (L=1024) trained to generate beyond its context (L=2003) still produces locally fluent but globally incoherent, topic-drifting text — demonstrating that long-context AR pretraining alone does not guarantee coherent long-form generation.

**Caption (verbatim):**
Figure 8: Sample from an AR model (Sahoo et al., 2024a) with length L = 2003 (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 10.6 and its entropy is 5.5.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\M_{\text{full}} = \begin{bmatrix} \M_{BD} & \M_{OBC} \\ \mathbf{0} & \M_{BC} \end{bmatrix}
$$

$$
\log p_\theta(\x) = \sum_{\ell=1}^L \log p_\theta(\xl \mid \x^{<\ell}),
$$

$$
p_\theta(\x_s \mid \x_t) = \prod_{\ell=1}^L p_\theta(\xl_s \mid \x_t) = \sum_{\x} \left[\prod_{\ell=1}^L q(\xl_s \mid \xl_t, \xl) p_\theta(\xl \mid \x_t)\right],
$$

$$
\mathcal{L}(\x; \theta) = \E_q\Bigg[- \log p_\theta( \x | \x_{t(1)}) + \sum_{j=1}^T \KL[q(\x_{s(j)} | \x_{t(j)}, \x) \| p_\theta(\x_{s(j)} | \x_{t(j)})] + \KL[q(\x_{t(T)} | \x) \| p_\theta(\x_{t(T)})] \Bigg]
$$

$$
\log p_\theta(\x) &= \sum_{b = 1}^{B} \log p_\theta(\x^{b} \mid \x^{<b}),
$$

$$
p_\theta(\x_s^b \mid \x_t^b, \x^{<b}) = \sum_{\x^b} q(\x_s^b \mid \x_t^b, \x^b)p_\theta(\x^b\mid \x^b_t,\x^{<b})
$$

$$
- \log p_\theta(\x) \leq \mathcal{L}_\text{BD}(\x; \theta) := \sum_{b=1}^{B} \mathcal{L}(\x^b, \x^{<b}; \theta),
$$

$$
\x_\text{logits}^b, \mathbf{K}^b, \mathbf{V}^b \gets \x^b_\theta(\x^b_t, \mathbf{K}^{1:b-1}, \mathbf{V}^{1:b-1}) := \x^b_\theta(\x^b_t, \x^{<b}),
$$

$$
\mathcal{L}_\text{BD}(\mathbf{X}; \theta) := l(\mathbf{X}; \theta) = \frac{1}{K} \sum_{k=1}^K \sum_{b=1}^B \frac{\alpha_{t(k, b)}'}{1-\alpha_{t(k,b)}} \log p_\theta \left( \x^{(k),b} \mid \x_{t(k,b)}^{(k),b}, \x^{(k), <b} \right)
$$

$$
\text{Var}_{\mathbf{X}, t}\left[ \nabla_\theta l (\mathbf{X}; \theta) \right] &\approx \frac{1}{M-1} \sum_{m=1}^M \left\lVert \nabla_\theta l (\mathbf{X}^m; \theta) - \frac{1}{M} \sum_{m=1}^M \nabla_\theta l(\mathbf{X}^m; \theta) \right\rVert^2_2
$$

$$
[Q_t]_{ij} = \begin{cases} 1 & \text{if } i = j = m \\ \at & \text{if } i = j \neq m \\ 1-\at & \text{if } j = m, i \neq m \end{cases}
$$

$$
[Q_{t|s}]_{ij} = \begin{cases} 1 & \text{if } i = j = m \\ \ats & \text{if } i = j \neq m \\ 1-\ats & \text{if } j = m, i \neq m \end{cases}
$$

$$
q(\xl_t | \xl) = \text{Cat} \left( \xl_t; \overline{Q}_t \xl \right), \quad \text{with} \quad \overline{Q}_{t(i)} = Q_{t(1)} Q_{t(2)} \dots Q_{t(i)}
$$

$$
q(\xl_{s} | \xl_t, \xl) = \frac{q(\xl_t | \xl_{s}, \xl) q(\xl_{s} | \xl)}{q(\xl_t | \xl)} = \text{Cat} \left( \xl_{s}; \frac{Q_{t|s} \xl_t \odot Q_s^\top \xl}{{(\xl_t)}^\top Q_t^\top \xl} \right)
$$

$$
\mathcal{L}_{\text{diffusion}} &= \sum_{b=1}^{B} \mathbb{E}_{t \sim [0, 1]} \mathbb{E}_{q} \left[ \frac{\at'}{1-\at} \log p_\theta(\x^b \mid \x_t^b, \x^{<b}) \right]
$$

$$
\mathcal{L}_{\text{recons}} &= - \mathbb{E}_q \log \p (\x^b | \x_{t(1)}^b, \x^{<b}) \nonumber \\ &= - \log \p (\x^b | \x_{t(1)}^b = \x^b, \x^{<b}) \nonumber \\ &= 0
$$

$$
\mathcal{L}_{\text{BD}} (\x; \theta) &= \sum_{b=1}^{B} \mathbb{E}_{t \sim [0, 1]} \mathbb{E}_{q} \left[ \frac{\at'}{1-\at} \log p_\theta(\x^b \mid \x_t^b, \x^{<b}) \right]
$$

$$
-\log \p(\x) &\leq - \sum_{b=1}^{L} \mathbb{E}_{t \sim [0, 1]} \frac{1}{t} q(\x_t^b = \m | \x^b) \log p_\theta(\x^b \mid \x_t^b = \m,\x^{<b}) \nonumber \\ & \text{\footnotesize{ $\because q(\x^b_t = \m | \x^b) = t$, we get:}} \nonumber \\ &= - \sum_{b=1}^{L} \mathbb{E}_{t \sim [0, 1]} \log p_\theta(\x^b \mid \x_t^b = \m,\x^{<b}) \nonumber \\ &= - \sum_{b=1}^{L} \log p_\theta(\x^b \mid \m, \x^{<b})
$$

$$
\mathcal{L}_1 &= \sum_{b=1}^{L} \log \mathbb{E}_{t \sim [0, 1]} \mathbb{E}_q \frac{\at'}{1-\at} p_\theta(\x^b \mid \x_t^b,\x^{<b}) \nonumber \\ &= - \sum_{b=1}^{L} \log p_\theta(\x^b \mid \m,\x^{<b})
$$

$$
\mathcal{L}_2 = \sum_{b=1}^{L/2} \log \mathbb{E}_{t \sim [0, 1]} \mathbb{E}_q \frac{\at'}{1-\at} p_\theta(\x^b \mid \x_t^b, \x^{<b})
$$

## 相关论文

- [[dflash-block-diffusion-for-flash-speculative-decoding]] — DFlash: Block Diffusion for Flash Speculative Decoding
- [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]] — EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees
- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] — DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation
- [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] — LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and Verification
- [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] — MEDUSA: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads

## 技术点深读（DEEP）

![[deep/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models.txt`（98874 字符）供引用检索。