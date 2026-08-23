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
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig01.png]]
*整页渲染: ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p02.png]]*
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
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig02.png]]
*整页渲染: ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p06.png]]*
> [!quote] caption
> Train NLLs for modeling the per-token likelihood on LM1B. Models are trained on 16B tokens. Training under the discrete diffusion NELBO, where half of the tokens in a batch are masked on average, has similar training variance to an AR model with a random batch size. so that Et∼U[0,1]q(xℓ t = m|xℓ) = 0.5. Thus, training on the diffusion objective involves estimating loss gradients with 2x fewer tok

> [!tip] 技术解读（多模态）
> **Description:**

The figure is a line plot titled "Train Negative Log-Likelihood (NLL) for Single Token Generation on LM1B," with training steps (0–250k+) on the x-axis and NLL (3.0–4.0) on the y-axis. Four curves are compared: **BD3-LM (NELBO)** (red, highly spiky throughout), **BD3-LM (Tuned schedule)** (purple, smooth), **AR** (orange, smooth baseline), and **AR (random batch size)** (green, spiky). All start near NLL ≈ 4.0 and decrease, but the spiky curves retain visible variance while tuned/standard AR settle near 3.15.

**Key takeaway:** Tuning the masking noise schedule is critical — it collapses BD3-LM training variance to match standard AR, while the default NELBO schedule yields variance comparable to AR trained with random batch sizes (an unfair comparison baseline).

**Verbatim caption:**

"Figure 2: Train NLLs for modeling the per-token likelihood on LM1B. Models are trained on 16B tokens. Training under the discrete diffusion NELBO, where half of the tokens in a batch are masked on average, has similar training variance to an AR model with a random batch size."

### Figure 3 (p.21) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig03.png]]
*整页渲染: ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p21.png]]*
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
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig04.png]]
*整页渲染: ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p22.png]]*
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
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig05.png]]
*整页渲染: ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p23.png]]*
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
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig06.png]]
*整页渲染: ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p26.png]]*
> [!quote] caption
> Sample from MDLM (Sahoo et al., 2024a) of length L = 1024 and T = 5K diffusion steps.

> [!tip] 技术解读（多模态）
> ## Description

This figure is **not an architecture diagram** but rather a **qualitative sample** illustrating the output of MDLM (Sahoo et al., 2024a), a masked diffusion language model. There is no architecture, component, or data-flow schematic — the "figure" is simply a rendered block of generated text wrapped between `<lendoftext>` sentinel tokens.

**Reading the output:** The generated passage (~1024 tokens, produced over 5K diffusion steps) is a topical mishmash blending multiple domains — art criticism (Paolo Capacotti, Giuliano/Angiolo/Leonetto Romei/Fiastri family), a museum crime anecdote (Franco Belzina's life, the broken candle, statue restoration), WWII history (Canadian/Italian POWs, statues removed from Cooper–Paris), and music industry references (record labels, festivals). **Key takeaway:** despite MDLM achieving competitive perplexity, the 1024-token sample exhibits topic drift, entity hallucination, and incoherent transitions — a common failure mode where diffusion-style generation lacks the autoregressive consistency that maintains long-range coherence in causal LMs.

## Caption (verbatim)

> **Figure 6:** Sample from MDLM (Sahoo et al., 2024a) of length *L* = 1024 and *T* = 5K diffusion steps. The generative perplexity of this sample under GPT2-Large is 69.26 and its entropy is 5.6.

### Figure 7 (p.27) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig07.png]]
*整页渲染: ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p27.png]]*
> [!quote] caption
> Sample from BD3-LM for block size L′ = 16 of length L = 2031 under T = 5K diffusion steps (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 24.3, and its entropy is 5.5. 27

> [!tip] 技术解读（多模态）
> **Figure description:** This figure is not an architecture diagram but a *sample generation* from BD3-LM, a block-wise discrete diffusion language model. It displays a single block of continuous narrative text (≈2,031 tokens) bounded by `<lendoftext>` end-of-document markers. The content is a coherent, multi-paragraph story about a girl traveling to Mexico, her mother being detained at a Bangkok airport on the way home, and broader commentary on Calais refugees — demonstrating that the model produces long, fluent, topic-consistent passages.

**Key technical takeaway:** Despite being trained with a context length of only L = 1,024, BD3-LM generates sequences of length L = 2,031 (nearly 2× the training window) using only T = 5K diffusion steps with block size L' = 16, yielding coherent text with GPT2-Large generative perplexity 24.3 and entropy 5.5 — showing block diffusion can extrapolate beyond training context.

**Caption (verbatim):**
> Figure 7: Sample from BD3-LM for block size L' = 16 of length L = 2031 under T = 5K diffusion steps (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 24.3, and its entropy is 5.5.

### Figure 8 (p.28) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig08.png]]
*整页渲染: ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p28.png]]*
> [!quote] caption
> Sample from an AR model (Sahoo et al., 2024a) with length L = 2003 (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 10.6 and its entropy is 5.5. 28

> [!tip] 技术解读（多模态）
> **Description**

This is not a traditional architecture diagram — it is a qualitative-output figure. The figure consists of a single boxed block of generated English text flanked by `<lendofftext>` sentinel tokens. The text is one long, unsegmented passage (~2,000 tokens) produced by an autoregressive language model; it drifts incoherently across multiple unrelated topics (an NFL game recap, a personal dispute over a tree in "Charlotte Gardens," architectural commentary on a building, and assorted trivia), with frequent name/topic confusions, fabricated quotes, and hallucinated entities. There are no labeled components, arrows, or data-flow stages — the "architecture" is implicit (AR transformer with context length 1024 producing a 2003-token sample, benchmarked against GPT2-Large, achieving perplexity 10.6 and entropy 5.5).

**Key takeaway:** The sample illustrates that even a long-context AR model (L=1024) trained to generate beyond its context (L=2003) still produces locally fluent but globally incoherent, topic-drifting text — demonstrating that long-context AR pretraining alone does not guarantee coherent long-form generation.

**Caption (verbatim):**
Figure 8: Sample from an AR model (Sahoo et al., 2024a) with length L = 2003 (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 10.6 and its entropy is 5.5.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab01.png]]
> [!quote] caption
> Test perplexities for single- token generation (PPL; ↓ ) across 16B tokens on LM1B.

> [!tip] 表格解读（多模态）
> **Description:**
The displayed item is **Table 1** (not an architecture diagram), a four-row results table comparing perplexity (PPL ↓) on LM1B after 16B training tokens. It benchmarks four configurations:

- **AR** (autoregressive baseline): **22.88**
- **AR + random batch size**: 24.37 (degrades due to batching variance)
- **BD3-LM** with L′ = 1 (block-diffusion, single-token block): **≤ 25.56**
- **BD3-LM L′ = 1 + tuned schedule**: **22.88** (matches AR)

The accompanying paragraph explains *why* — although block-diffusion with L′ = 1 is expectation-equivalent to the AR negative log-likelihood (Eq. 8 ≈ Eq. 1), the cross-entropy is only computed over **masked** tokens $\mathbf{x}_t^\ell = \mathbf{m}$, yielding a loss with higher variance than AR's full-token cross-entropy. A tuned noise schedule closes this ~3-point perplexity gap.

**Key technical takeaway:** Block diffusion and AR are theoretically equivalent in expectation at L′ = 1, but block diffusion suffers from high *training variance* because its loss only sees masked tokens; a tuned sampling schedule is required to recover matching test perplexity (22.88) on LM1B.

**Caption verbatim:**
*Table 1: Test perplexities for single-token generation (PPL; ↓) across 16B tokens on LM1B.*

### Table 2 (p.7) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab02.png]]
> [!quote] caption
> Perplexities (PPLs; ↓ ) and variances of the NELBO Var X ,t [ L BD ( X ; θ )] (Var. NELBO; ↓ ). Models are trained on LM1B using a linear schedule for 65B tokens, then finetuned for 10B tokens.

> [!tip] 表格解读（多模态）
> **Description**

The provided content is not a figure but **Table 2**, a numerical results table from an experimental study on language modeling. It has a hierarchical layout:

- **Top-level grouping (4 columns):** four prior distributions — 𝒰[0,.5], 𝒰[.3,.8], 𝒰[.5,1], 𝒰[0,1].
- **Second-level columns:** Perplexity (PPL) and Variance of NELBO (Var. NELBO) under each prior.
- **Rows:** three values of the parameter **L′** (128, 16, 4), controlling the budget/size of a latent block.

**Key technical takeaway:** There is a clear PPL ↔ variance trade-off with respect to L′. Larger L′ (128) yields the lowest estimator variance (e.g., **1.03** for 𝒰[0,.5]) but the worst PPL (31.72), whereas smaller L′ (4) achieves the best PPL (**29.16** under 𝒰[.5,1]) at the cost of much higher variance (8.28). The choice of prior interval also matters: the narrowest prior 𝒰[.5,1] paired with L′ = 4 gives the best-of-both on PPL with moderate variance. This indicates practitioners can tune L′ and the prior to balance sample efficiency and model quality depending on downstream priorities.

**Caption (verbatim)**

> Table 2: Perplexities (PPLs; ↓) and variances of the NELBO Var**ₓ,ₜ**[𝓛_BD(**X**; θ)] (Var. NELBO; ↓). Models are trained on LM1B using a linear schedule for 65B tokens, then finetuned for 10B tokens.

### Table 3 (p.7) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab03.png]]
> [!quote] caption
> Test perplexities (PPL; ↓ ) of mod- els trained for 65B tokens on LM1B. Best diffusion value is bolded.

> [!tip] 表格解读（多模态）
> There is no main figure on this page — only narrative text and **Table 3**. I'll describe the table and key takeaway instead.

## Table 3 — Architecture / Data Flow (conceptual structure)

**What's shown:** Perplexity (PPL ↓) on LM1B after 65B training tokens, grouped by model family:

- **Autoregressive baseline:** Transformer-X Base (23.5) → Transformer (22.83)
- **Diffusion baselines:** D3PM absorb (≤82.34), SEDD (≤32.68), MDLM (≤31.78)
- **Block diffusion (BD3-LMs, the paper's proposal):** with block size L′ = 16 → ≤30.60; L′ = 8 → ≤29.83; L′ = 4 → ≤28.23 (bolded as best diffusion value)

The table is a *column-organ chart* in spirit: one column for PPL, one column for method, rows sorted to make the Pareto improvement of BD3-LMs visually obvious.

## Key Technical Takeaway

BD3-LMs at small block sizes (L′ = 4) achieve 28.23 PPL on LM1B, beating both autoregressive Transformers (22.83) — wait, *approaching* them — and prior diffusion LMs (MDLM 31.78) by a clear margin, demonstrating that **block-wise diffusion bridges the gap between diffusion and autoregressive language modeling**.

## Verbatim Caption

> **Table 3:** Test perplexities (PPL; ↓) of models trained for 65B tokens on LM1B. Best diffusion value is bolded.

### Table 4 (p.8) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab04.png]]
> [!quote] caption
> Test perplexities (PPL; ↓ ) on OWT for models trained for 524B to- kens. Best diffusion value is bolded.

> [!tip] 表格解读（多模态）
> # Response

I don't see a figure in the provided image — only two columns of body text and **Table 4**. Below I describe what is actually present (Table 4), then transcribe its caption verbatim.

---

## What is shown (Table 4)

**Structure / components:**
- A single-column **table** reporting test **perplexity (PPL)** on OpenWebText (OWT), with lower-is-better indicated by ↓.
- Models grouped into two families:
  - **Autoregressive / discrete diffusion baselines:** AR (Sahoo et al., 2024a), SEDD (Lou et al., 2024), MDLM (Sahoo et al., 2024a).
  - **BD3-LMs** at three block sizes: L′ = 16, 8, 4.

**Numeric content (PPL ≤):**
| Method | PPL (↓) |
|---|---|
| AR | 17.54 |
| SEDD | ≤ 24.10 |
| MDLM | ≤ 22.98 |
| BD3-LMs L′ = 16 | ≤ 22.27 |
| BD3-LMs L′ = 8 | ≤ 21.68 |
| BD3-LMs L′ = 4 | **≤ 20.73** |

**Key takeaway (≤120 words):**
> All BD3-LM variants outperform prior diffusion language models (MDLM and SEDD) on OWT after 524B tokens, with smaller block sizes monotonically improving perplexity: 22.27 → 21.68 → 20.73 at L′ = 16 / 8 / 4. The best BD3-LM (L′ = 4) reaches 20.73 PPL, still trailing the autoregressive baseline (17.54) but establishing a new state-of-the-art among discrete-diffusion LMs and corroborating the LM1B trend in Table 3.

---

## Caption (transcribed verbatim)

**Table 4:** Test perplexities (PPL; ↓) on OWT for models trained for 524B tokens. Best diffusion value is bolded.

### Table 5 (p.8) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab05.png]]
> [!quote] caption
> Zero-shot validation perplexities ( ↓ ) of models trained for 524B tokens on OWT. All perplexities for diffusion models are upper bounds.

> [!tip] 表格解读（多模态）
> # Description

**Note:** The provided image is a data table (Table 5), not an architecture/flow diagram — there are no components, modules, or data-flow arrows to describe. I will instead describe the table's content.

**Table structure:**
- **Columns (7 evaluation benchmarks):** PTB, Wikitext, LM1B, Lambada, AG News, Pubmed, Arxiv
- **Rows (4 models):** AR (autoregressive), SEDD, MDLM, BD3-LM (L′=4)
- **Cell values:** zero-shot validation perplexity (↓ lower is better); bold = best per column
- **Constraint:** all diffusion-model values are reported as upper bounds; models trained on 524B tokens from OWT

**Key technical takeaway:** Autoregressive (AR) modeling remains strongest on 4 of 7 benchmarks (PTB, Wikitext, LM1B, AG News), while discrete diffusion models (MDLM, BD3-LM) are competitive or superior on others (Lambada, Pubmed, Arxiv), suggesting diffusion-based LMs are viable on some domains but have not yet matched AR across the board — with caveat that diffusion perplexities are upper bounds. (≈75 words)

---

**Caption (verbatim):**

> Table 5: Zero-shot validation perplexities (↓) of models trained for 524B tokens on OWT. All perplexities for diffusion models are upper bounds.

### Table 6 (p.8) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab06.png]]
> [!quote] caption
> Generation length statistics from sampling 500 documents from models trained on OWT.

> [!tip] 表格解读（多模态）
> I don't see a main figure with architecture/components/data flow in the provided image. The image contains two paragraphs of academic text and **Table 6** (a data table, not an architecture figure).

Here's what is visible:

**Table 6 content:**
| | Median # tokens | Max # tokens |
|---|---|---|
| OWT train set | 717 | 131K |
| AR | 4008 | 131K |
| SEDD | 1021 | 1024 |
| BD3-LM L′ = 16 | 798 | 9982 |

**Key technical takeaway from the surrounding text (≤120 words):** BD3-LMs overcome the fixed-context-length limitation of prior diffusion language models (e.g., SEDD), generating sequences up to **≈10× longer** than SEDD while remaining competitive with autoregressive (AR) baselines on the OWT dataset. Unlike SSD-LM's Gaussian diffusion formulation, BD3-LM uses discrete diffusion with an efficient masked-sampler where the number of function evaluations (NFEs) is upper-bounded by the sequence length *L* (tokens are never remasked). This enables long-form generation without the heavy diffusion-step cost (≥40K NFEs) that Gaussian block-diffusion methods require.

**Caption transcribed verbatim:**
> Table 6: Generation length statistics from sampling 500 documents from models trained on OWT.

If you intended to share a different figure (e.g., the BD3-LM architecture diagram), please re-upload it.

### Table 7 (p.9) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab07.png]]
> [!quote] caption
> Generative perplexity (Gen. PPL; ↓ ) and number of function evaluations (NFEs; ↓ ) of 300 samples of lengths L = 1024 , 2048 . All models are trained on OWT. AR, SEDD, MDLM, BD3-LMs use 110M parameters and are trained on 524B tokens, while SSD-LM uses 400M parameters and is pre-trained on 122B token

> [!tip] 表格解读（多模态）
> **Description (Table 7):**
This results table benchmarks generative perplexity (Gen. PPL, lower is better) and number of function evaluations (NFEs, lower is better) across autoregressive (AR), standard diffusion (SEDD, MDLM), and block diffusion (SSD-LM, BD3-LMs) language models at sequence lengths L=1024 and L=2048. BD3-LMs dominate the diffusion category, with the smallest block size (L'=4) achieving the best scores (25.7 / 23.6) while using only 1K–2K NFEs—an order of magnitude fewer steps than SSD-LM's 40K–80K, yet with substantially lower perplexity.

**Key takeaway:** Block-wise discrete diffusion matches autoregressive generation quality at diffusion-model step counts.

---

**Caption (verbatim):**

*BD3-LMs achieve the best generative perplexities compared to previous diffusion methods. Relative to SSD-LM, our discrete approach yields samples with improved generative perplexity using an order of magnitude fewer generation steps. We also qualitatively examine samples taken from BD3-LM and baselines (AR, MDLM) trained on the OWT dataset; we report samples in Suppl. D. We observe that BD3-LM samples have higher coherence than MDLM samples and approach the quality of AR.*

### Table 8 (p.9) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab08.png]]
> [!quote] caption
> Effect of the noise schedule on like- lihood estimation. We finetune BD3-LMs on 3B tokens from LM1B and evaluate on a linear schedule. For clipped schedules, we compare optimal clipping for L ′ = 4 , 16 .

> [!tip] 表格解读（多模态）
> **Description of the main figure (Table 8):**

The table is a 3-column results grid (Noise schedule / PPL / Var. NELBO) split into two block-size regimes, **L' = 4** (top) and **L' = 16** (bottom). Each block lists five noise schedules: two *clipped* uniforms (𝒰[0.45, 0.95] and 𝒰[0.3, 0.8]), a linear 𝒰[0,1], and auxiliary schedules (logarithmic, square-root, square, or cosine depending on regime). Best values per column are bolded. Data flow is implicit: schedules are applied during BD3-LM finetuning on 3B LM1B tokens, then evaluated under the linear schedule.

**Key takeaway:** Clipped-uniform masking strictly dominates non-clipped schedules in both block-size regimes, yielding the lowest perplexity and lowest variance NELBO simultaneously — at small L'=4 favoring aggressive clipping 𝒰[0.45, 0.95], while at large L'=16 favoring tighter 𝒰[0.3, 0.8].

**Caption (verbatim):**

"Table 8: Effect of the noise schedule on likelihood estimation. We finetune BD3-LMs on 3B tokens from LM1B and evaluate on a linear schedule. For clipped schedules, we compare optimal clipping for L' = 4, 16."

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