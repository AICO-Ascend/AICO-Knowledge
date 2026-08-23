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
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig01.png]]
*整页渲染: ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p02.png]]*
> [!quote] caption
> Speedup comparison between DFlash, EAGLE-3 against Autoregressive Decoding on Qwen3-8B (Yang et al., 2025) with the

> [!tip] 技术解读（多模态）
> **Description (73 words):**
The figure is a grouped bar chart comparing speculative decoding speedup across seven benchmarks (GSM8K, Math500, AIME25, HumanEval, MBPP, LiveCodeBench, MT-Bench) on Qwen3-8B. Baseline (gray) is normalized to 1.00×, EAGLE-3 (green) achieves 1.81×–2.23×, while DFlash (blue) ranges from 2.75× (MT-Bench) to 6.08× (Math500). **Key takeaway:** DFlash delivers 2.5×–3× higher speedup than EAGLE-3 across most benchmarks, peaking at 6.08× on Math500, demonstrating that block-diffusion drafting substantially outperforms autoregressive speculative decoding on reasoning-heavy tasks.

**Caption (verbatim):**
Figure 1. Speedup comparison between DFlash, EAGLE-3 against Autoregressive Decoding on Qwen3-8B (Yang et al., 2025) with the Transformers backend. Overall, DFlash achieves more than 2.5x higher speedup than EAGLE-3.

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig02.png]]
*整页渲染: ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p04.png]]*
> [!quote] caption
> DFlash Inference Design. Hidden context features extracted from the target model are fused and injected into each draft layer’s

> [!tip] 技术解读（多模态）
> ## Figure Description

**Architecture:** The diagram depicts a **diffusion-based speculative decoding** pipeline. The prompt "Diffusion is good" enters the **Target Model** (top), producing *Fused Target Context Features* (blue) and a *Target Decode Token* (orange). Simultaneously, `<mask>` tokens are converted via **Target Embedding** into *Mask Tokens* (green). These streams are concatenated and processed sequentially through stacked **Draft Layers** (Layer 1, Layer 2, ...), each containing a **KV Cache**, **Bidirectional Attention**, and **MLP**. The final output passes through a **Target LM Head** to generate tokens *for speculative decoding*.

**Key Takeaway:** Draft tokens leverage bidirectional attention over fused target context and prior decoded tokens (via KV cache), enabling parallel/non-autoregressive speculation rather than sequential left-to-right generation — accelerating inference while conditioning on full context.

(112 words)

## Verbatim Text Transcription

> "Diffusion is good" → Target Model → (column of tokens)
> Target Embedding → for `<mask> <mask> <mask>`
> KV Cache | Draft Layer 1 | Bidirectional Attention | MLP
> Draft Layer 2 → …
> Target LM Head → for speculative decoding `<eos>`
> Legend: ▢ Fused Target Context Feature | ▢ Target Decode Token | ▢ Mask Token

### Figure 3 (p.3) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig03.png]]
*整页渲染: ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p03.png]]*
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
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig04.png]]
*整页渲染: ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p05.png]]*
> [!quote] caption
> DFlash training attention. The target model provides context features (blue) that condition the draft model. The input consists of clean prompt tokens p and clean response tokens r.

> [!tip] 技术解读（多模态）
> ## Description

**Architecture/components:** Two side-by-side token grids depict a context-extension scheme. The left panel "From Target Model" shows a triangular causal mask: blue *Target Context Features* fill positions p1–p4 and r1–r2, expanding rightward down each row, with white *Invisible Tokens* elsewhere. The right panel "Mask Blocks" shows a wider grid where each response token (r1, r2, r3) is followed by three `<m>` mask tokens. Yellow *Clean Tokens* anchor each block, green *Mask Tokens* populate the `<m>` positions, and the rest remain invisible.

**Data flow:** Target context features (left) are aligned with corresponding clean-token-plus-mask-block sequences (right), so each response token is replicated as a "clean + masked" block to enrich supervision.

**Key takeaway (≤120 words):** The technique augments the target model's causal context by replicating each response token into a clean-anchor block followed by learned mask tokens. This expands the visible receptive field without breaking autoregressive causality, providing denser self-supervised signals across positions that would otherwise be invisible under strict causal masking — improving representation quality in masked-prediction-style training while maintaining compatibility with the target model's generation structure.

## Caption (verbatim transcription)

> **From Target Model** &nbsp;&nbsp;&nbsp;&nbsp; **Mask Blocks**
> 
> p1 &nbsp; p2 &nbsp; p3 &nbsp; p4 &nbsp; r1 &nbsp; r2 &nbsp;&nbsp;&nbsp; … &nbsp;&nbsp;&nbsp; r1 &nbsp; \<m\> &nbsp; \<m\> &nbsp; \<m\> &nbsp; r2 &nbsp; \<m\> &nbsp; \<m\> &nbsp; \<m\> &nbsp; r3 &nbsp; \<m\> &nbsp; \<m\> &nbsp; \<m\>
> 
> Legend: ▢ Target Context Feature &nbsp;|&nbsp; ▢ Mask Token &nbsp;|&nbsp; ▢ Clean Token &nbsp;|&nbsp; ▢ Invisible Token

### Figure 5 (p.13) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig05.png]]
*整页渲染: ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p13.png]]*
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

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.6) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab01.png]]
> [!quote] caption
> Decoding speedup over baseline and average acceptance length ( τ ) on Qwen3 models with thinking mode disabled and a

> [!tip] 表格解读（多模态）
> ## Main Figure Description

**Architecture/Components:** Table 1 is a benchmark comparison matrix structured as Model × Method versus three evaluation domains (Math, Code, Chat). Each cell reports a **decoding speedup ratio over a baseline**, with a **parenthesized secondary metric** indicating the structural hyperparameter — **draft tree size** for EAGLE-3 and **diffusion block size** for DFlash. Rows cover Qwen3 model variants (thinking-mode disabled, capped at 2048 tokens), enabling controlled isolation of the speculative-decoding algorithm from model-scale effects.

**Data flow (read order):** Model identifier → speculative method → per-domain speedup → brackets yielding the algorithm's structural knob.

**Key technical takeaway:** DFlash and EAGLE-3 expose a **single tunable parameter** (block size vs. draft tree size) that trades draft compute against acceptance rate, and the table reveals that across Math/Code/Chat, the optimal block/tree size differs by task — suggesting no universally "best" draft granularity, motivating per-domain tuning of the speculative-decoding block/tree configuration.

## Caption (verbatim)

> **Table 1.** Decoding speedup over baseline and average acceptance length ( ) on Qwen3 models with thinking mode disabled and a maximum of 2048 generated tokens. Parenthesized values indicate the draft tree size for EAGLE-3 and the diffusion block size for DFlash.

### Table 2 (p.7) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab02.png]]
> [!quote] caption
> Decoding speedup over baseline and average acceptance

> [!tip] 表格解读（多模态）
> # Figure Description

**Components/Data Flow:**
The table ("Table 2") presents a benchmark evaluation comparing two Qwen3 reasoning model variants (**Q3-4B** and **Q3-8B**) across three math/science datasets: **GPQA**, **MATH-500**, and **AIME25**. Each model is evaluated at two sampling temperatures (**T=0** for greedy and **T=1** for sampling). Two paired metrics are reported per cell — a **Speedup** factor over baseline decoding and the corresponding **average acceptance length** (the number of tokens generated per verification step, characteristic of speculative decoding).

**Key Technical Takeaway:**
Across all benchmarks and both models, **temperature 0 (greedy decoding) consistently yields higher speedups (4.17–5.82×) and longer acceptance lengths than temperature 1** (3.64–5.06×), indicating that the speculative decoder's acceptance rate is more stable under deterministic generation. The **Q3-8B shows slightly larger absolute speedups than Q3-4B** at temp=0, suggesting larger drafts benefit more from this acceleration scheme.

---

## Verbatim Caption Transcription

> **Table 2.** Decoding speedup over baseline and average acceptance length ( ) with thinking mode enabled.

*(Note: the parentheses in the caption appear empty in the source — likely a missing symbol denoting the units/context of acceptance length.)*

### Table 3 (p.7) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab03.png]]
> [!quote] caption
> Throughput (tok/s), speedup over baseline, and average

> [!tip] 表格解读（多模态）
> **Description (Table 3):**

This is a performance benchmark table (not a diagram) evaluating **DFlash** speculative-decoding throughput on SGLang with the FA4 backend. The table is organized as a 2D grid:

- **Columns:** Task, Method, Concurrency levels (1, 4, 8, 16, 32), and an Avg. column.
- **Rows:** Grouped by target model (Qwen3-4B, Qwen3-8B), then by task (Math500, HumanEval), each comparing Baseline vs. DFlash (showing throughput in tok/s plus a speedup ratio).
- **Data flow:** Concurrent requests → Baseline/DFlash kernel → measured tok/s and acceptance length.

**Key takeaway:** DFlash yields up to 4.8× speedup at concurrency=1, scaling to 2.2–4.8× even at high concurrency, while maintaining average acceptance lengths of ~6–8 tokens.

**Caption (verbatim):**
"Table 3. Throughput (tok/s), speedup over baseline, and average acceptance length on SGLang (FA4 backend)."

### Table 4 (p.8) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab04.png]]
> [!quote] caption
> Acceptance length of the base Qwen3.5-27B DFlash

> [!tip] 表格解读（多模态）
> **Description of the Main Figure (Table 4):**

The figure is a data table comparing **acceptance lengths** of two drafter configurations for speculative decoding: the *base* Qwen3.5-27B DFlash drafter versus the same drafter *fine-tuned for long context* (labeled "Long"). It is evaluated on the **LongBench** benchmark, broken down by dataset (hotpotqa, qasper, gov-report, with additional columns implied) and stratified by input **context length** (rows beginning to appear at the bottom). Acceptance length is a standard metric in speculative decoding — higher values indicate the drafter's tokens are more often accepted by the target model, yielding greater decoding speedup.

The data flow conceptually is: long context → DFlash drafter (Base or Long-tuned) → proposed tokens → target LLM verification → measured acceptance length per context-length bucket.

**Key technical takeaway (≤120 words):**
Fine-tuning the DFlash drafter on long-context data materially boosts its acceptance length compared to the base version, especially as context length grows. Since acceptance length directly translates to wall-clock speedup in speculative decoding, long-context drafter adaptation is a critical and lightweight lever for serving LLMs efficiently on long-document workloads — rather than retraining the full target model.

**Caption (verbatim transcription):**

*Table 4. Acceptance length of the base Qwen3.5-27B DFlash drafter (Base) and the drafter fine-tuned for long context (Long) across various context lengths on LongBench.*

### Table 5 (p.8) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab05.png]]
> [!quote] caption
> Speedup over baseline and average acceptance length

> [!tip] 表格解读（多模态）
> **Description (Table 5):**

This table presents speedup ratios over autoregressive baseline TPS for LLaMA-3.1-8B-Instruct under speculative decoding. Rows compare the Baseline, EAGLE-3 (10/60 draft tokens), and DFlash (block size 10) across three benchmarks (GSM8K, HumanEval, Alpaca). Columns slice results by serving concurrency (1, 4, 8, 16, 32) plus an average acceptance-length column. Cell values are speedup multipliers; DFlash rows are bolded. Data flows from raw TPS → speedup ratios → aggregated averages.

**Key takeaway:** DFlash beats EAGLE-3 at every concurrency on all three tasks (e.g., 2.4× vs. 1.6× at concurrency 1 on GSM8K; 2.8× vs. 2.0× on HumanEval), while also achieving higher average acceptance length (3.73–4.91 tokens) than EAGLE-3 variants, indicating block-parallel drafting is more efficient than tree-based token drafting.

**Caption (verbatim):**
Table 5. Speedup over baseline and average acceptance length for LLaMA-3.1-8B-Instruct on SGLang (Flashinfer backend, single B200 GPU). Baseline reports absolute throughput (TPS; tokens/s). EAGLE-3 uses 7 draft steps with top-k=2 and either 10 or 60 draft tokens. DFlash uses block size 10.

### Table 8 (p.8) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab08.png]]
> [!quote] caption
> Ablation study of training–inference block size (BS)

> [!tip] 表格解读（多模态）
> **Description (Table 8):**

Table 8 is an ablation matrix comparing **training vs. inference block-size (BS)** combinations for draft models in speculative decoding. Rows enumerate four Train/Test BS pairings (b16/b16, b16/b8, b8/b16, b8/b8); columns report speedup metrics across three benchmarks (Math500, HumanEval, MT-Bench), with two figures per benchmark (e.g., 4.64x / 6.33x). Data flow: each row supplies matched/mismatched block-size configurations that are evaluated end-to-end on a single B200 GPU under fixed draft capacity (8 layers, 5 target hidden features).

**Key takeaway (≤120 words):** Block-size consistency between training and inference is more important than absolute size. The matched b16/b16 configuration yields the strongest speedups (4.64x on Math500, 3.96x HumanEval, 2.23x MT-Bench), while mismatched pairings—particularly **train=b8, test=b16** (3.78x / 3.24x / 2.09x)—degrade performance relative to both matched settings. Training at a **larger** block size (b16) is more robust to inference downsizing than the reverse, indicating draft models generalize better when trained with longer context windows than shorter ones.

**Caption transcribed verbatim:**

> Table 8. Ablation study of training–inference block size (BS) mismatch. All draft models use 8 layers and 5 target hidden features.

### Table 9 (p.9) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab09.png]]
> [!quote] caption
> Ablation of target-feature conditioning for Qwen3-4B with 5-layer draft models and draft block size 8. Each task column reports τ / speedup.

> [!tip] 表格解读（多模态）
> **Description of the main figure (Table 9).**

Table 9 is a quantitative ablation table, not an architecture diagram. It cross-tabulates four components: rows are draft-model variants grouped under two drafting paradigms — **Autoregressive drafting** (EAGLE-3-5L vs DFlash-AR) and **Block-diffusion drafting** (DFlash × 2); each variant is tagged with one of two **Injection** mechanisms (Input fusion vs KV injection). Columns are three downstream benchmarks — GSM8K, HumanEval, MT-Bench — each reporting a paired `<acceptance length> / <speedup>` score against a Qwen3-4B target using 5-layer drafts with block size 8. The "data flow" is therefore a 2×2 (paradigm × injection) comparison swept across tasks, with bolded cells marking best-in-paradigm winners. **Key takeaway:** KV injection strictly dominates input fusion in both paradigms, boosting DFlash-AR acceptance length to 3.4–4.8 (vs EAGLE-3-5L's 3.1–4.3) and pushing block-diffusion DFlash speedup from 2.0–2.9× to 2.2–3.3× on GSM8K, confirming that target-side feature conditioning via KV is the superior signal.

**Caption (verbatim):**

> Table 9. Ablation of target-feature conditioning for Qwen3-4B with 5-layer draft models and draft block size 8. Each task column reports ⟨ / speedup.

### Table 10 (p.12) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab10.png]]
> [!quote] caption
> A 5-layer block diffusion draft model without target

> [!tip] 表格解读（多模态）
> **Description — KV Injection Architecture (Section A.3)**

DFlash's drafter is conditioned on target-model features via a lightweight KV-injection mechanism rather than full feature injection.

*Components:*
- **Concatenation stage:** hidden states from selected target layers are concatenated once and projected through a shared matrix $W_c \in \mathbb{R}^{H_t \times H_d}$ into the draft hidden space.
- **Per-layer cross-attention:** at draft layer $i$, draft tokens form queries ($Q_i = W_i^Q H_d$), while keys and values draw from *both* target features and draft tokens ($K_i = W_i^K [H_t; H_d]$, $V_i = W_i^V [H_t; H_d]$).
- **Data flow:** target hidden states → concat → $W_c$ projection → injected as extra KV entries at every draft layer; no other pathway is altered.

*Key takeaway:* target features are inserted as KV entries only — they bypass the Q projection, output projection, self-attention update, and FFN. The **only** added parameters are the shared $W_c$, keeping memory overhead small while still letting the drafter attend to rich target representations.

**Caption verbatim (Table 10):**

"Table 10. A 5-layer block diffusion draft model without target context features. The draft model achieves only modest acceptance length and speedup."

### Table 11 (p.12) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab11.png]]
> [!quote] caption
> Results across more models on SGLang. Each cell

> [!tip] 表格解读（多模态）
> I'm unable to provide an architecture/components/data flow description because **no main figure appears on this page.** The visible content is text-only from Appendix A of the paper "DFlash: Block Diffusion for Flash Speculative Decoding," specifically sections A.1 (Training Implementation), A.2 (Diffusion Drafter without Target Feature), and A.4 (Results on More Models and vLLM). There are no diagrams, schematics, or architecture illustrations present.

The only caption-like text visible is the start of a table caption at the bottom of the page:

> "Table 11. Results across more models on SGLang. Each cell..."

This caption is truncated/incomplete — it cuts off mid-sentence at the page boundary, so I cannot transcribe it verbatim in full.

If you intended to share a different page containing the main architecture figure (typically Figure 1 in such papers, showing the block diffusion drafter interacting with the target LLM in the speculative decoding loop), please re-upload that image and I'll provide the requested description and verbatim caption transcription.

### Table 12 (p.12) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab12.png]]
> [!quote] caption
> vLLM results for Qwen3.5-9B. Each cell reports DFlash

> [!tip] 表格解读（多模态）
> **Note:** The provided page contains no figure with architecture/components/data flow—only tables (10, 11, 12) and text. Below I describe the most prominent content (Table 11) and its caption.

**Main Content (Table 11) — Components/Data Shown:**
Table 11 compares DFlash against native MTP across target models on SGLang (one B200, concurrency 8). Rows list models (Qwen3.5-4B/9B/35B-A3B/27B, Qwen3-Coder-Next, GPT-OSS-20B/120B); columns compare per-model MTP vs. DFlash on three benchmarks (Math500, HumanEval, MT-Bench), with each cell formatted as **acceptance length / speedup**. DFlash consistently outperforms MTP where both exist and scales to larger Qwen3.5, Qwen3-Coder, and GPT-OSS targets (e.g., Qwen3.5-9B: 7.3/3.5 vs 6.7/1.7 on Math500).

**Key Takeaway:**
DFlash delivers monotonic speedups (1.3×–3.9× over autoregressive) across 4B–120B models and three eval suites, with the largest gains where MTP is absent or weaker—confirming the block-diffusion drafter generalizes beyond its training regime.

**Caption (verbatim):**
"Table 11. Results across more models on SGLang. Each cell reports acceptance length / speedup."

### Table 13 (p.13) ⭐深度解读
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-tab13.png]]
> [!quote] caption
> Randomly sample anchor tokens to construct masked

> [!tip] 表格解读（多模态）
> **Description (main figure/table):**

Table 13 presents an ablation comparing draft model training strategies, most likely plotting **acceptance length** (or **speedup ratio**) against variations in how anchor tokens are sampled when forming 16-token masked blocks. The architecture context is a speculative-decoding pipeline: the draft model is a shallow 3-layer transformer that consumes **5 hidden features** tapped from intermediate layers of the target (verifier) LLM; during training, source sequences are segmented into fixed-size blocks whose starting positions are sampled in different ways. Data flow is straightforward — training corpus (100K examples, §5.5) → masked-block construction → draft model → speculative generation against the frozen target.

**Key technical takeaway:** Randomly sampling anchor tokens to build masked training blocks acts as an effective **data-augmentation** mechanism, producing a more robust draft model that achieves a **longer mean acceptance length and higher inference speedup** than deterministic/non-augmented schemes, without changing model capacity.

**Caption (transcribed verbatim):**

"Table 13. Randomly sample anchor tokens to construct masked blocks during training effectively augments the training data and leads to higher acceptance length and better speedup. Both draft models use three layers and extract five hidden features from the target model. The block size is 16. We use the 100K data introduced in Section 5.5 to train both models."

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