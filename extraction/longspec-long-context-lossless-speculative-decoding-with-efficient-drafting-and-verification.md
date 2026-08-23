---
paper_num: "59"
title: "LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and Verification"
authors: "with Efficient Drafting and Verification Penghui Yang2*, Cunxiao Du1*, Fengzhuo Zhang3, Haonan Wang3, Tianyu Pang1, Chao Du1, Bo An2 1 Sea AI Lab, 2 Nanyang Technological University, 3 National University of Singapore ph"
date: "2025/2/24"
arxiv: "https://arxiv.org/abs/2502.17421"
pdf: "papers/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification.pdf"
slug: "longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification"
tags: [speculative, long-context]
---

# LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and Verification

> [!abstract] 摘要（原文）
> As Large Language Models (LLMs) can now process extremely long contexts, efficient inference over these extended inputs has become increasingly important, especially for emerging applications like LLM agents that highly depend on this capability. Speculative decoding (SD) offers a promising lossless acceleration technique compared to lossy alternatives such as quantization and model cascades. However, most state-of-the-art SD methods are trained on short texts (typically fewer than 4k tokens), making them unsuitable for long-context scenarios. Specifically, adapting these methods to long contexts presents three key challenges: (1) the excessive memory demands posed by draft models due to large Key-Value (KV) cache; (2) performance degradation resulting from the mismatch between short-context training and long-context inference; and (3) inefficiencies in tree attention mechanisms when managing long token sequences. This work introduces LongSpec, a framework that addresses these challenges through three core innovations: a memory-efficient draft model with a constant-sized KV cache; novel position indices that mitigate the training-inference mismatch; and an attention aggregation strategy that combines fast prefix computation with standard tree attention to enable efficient decoding. Experimental results confirm the effectiveness of LongSpec, achieving up to a 3.26x speedup over strong Flash Attention baselines across five long-context understanding datasets, as well as a 2.25x reduction in wall-clock time on the AIME24 long reasoning task with the QwQ model, demonstrating significant latency improvements for long-context applications. The code is available at this https URL.

## 元信息
- **发表日期**: 2025/2/24
- **作者**: with Efficient Drafting and Verification Penghui Yang2*, Cunxiao Du1*, Fengzhuo Zhang3, Haonan Wang3, Tianyu Pang1, Chao Du1, Bo An2 1 Sea AI Lab, 2 Nanyang Technological University, 3 National University of Singapore ph
- **arXiv**: https://arxiv.org/abs/2502.17421
- **本地 PDF**: `papers/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification.pdf`
- **页数**: 19

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig01.png]]
*整页渲染: ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p01.png]]*
> [!quote] caption
> The SoTA SD method, EAGLE, has a training context length of 2048, which is significantly shorter than the context lengths of modern LLMs. 2023), and their ability to handle extensive con- texts is becoming crucial for emerging applications such as LLM agents and long reasoning tasks (Tan et al., 2025; Guo et al., 2025), which now oper- ate over context windows extending to millions of tokens (Team

> [!tip] 技术解读（多模态）
> ## Main Figure Description (≤120 words)

**Figure 1** is a **bar chart** with a logarithmic y-axis (context length, 2k → 10M tokens) comparing the supported context windows of seven frontier LLMs — DeepSeek-V3, Qwen3-235B-A22B, Llama 4 Scout, Grok 3, Claude 3.7 Sonnet, GPT-4.1, and Gemini 2.5 Pro — each rendered as a colored bar topped with the model's logo. A horizontal red dashed reference line marks **2k tokens**, denoting EAGLE's training context length.

**Key technical takeaway:** The chart exposes a stark training–inference mismatch: although modern LLMs operate over 100k–10M-token contexts, the SoTA speculative decoding method EAGLE was trained on only **2,048 tokens**, rendering it ill-suited for long-context speculative decoding and motivating the proposed LONGSPEC framework.

## Caption (verbatim)

> **Figure 1:** The SoTA SD method, EAGLE, has a training context length of 2048, which is significantly shorter than the context lengths of modern LLMs.

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig02.png]]
*整页渲染: ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p04.png]]*
> [!quote] caption
> Illustration of the memory-efficient draft model, the Anchor-Offset Indices, and the Hybrid Tree Attention. (a) We use a sliding window self-attention layer to capture the local context information and a cross-attention layer to gather long-context information. (b) The differences between the vanilla indexing and the Anchor-Offset

> [!tip] 技术解读（多模态）
> LongSpec 三件套：(a) 内存高效 draft 模型——滑窗自注意力（定长窗口捕捉局部）+ 无 KV cache 的 cross-attention（直接读 target 模型 last-layer K/V 收长程信息），draft KV 占用变常数；(b) Anchor-Offset Indices——保留前 4 个位置作 attention sink，其余 token 从随机大 offset 连续编号，短上下文训练即可覆盖大位置索引、且 target 模型不 OOD（loss 仅 +0.001），弥合训练-推理位置错配；(c) Hybrid Tree Attention——前缀走 FlashAttention（快）+ tree 走 Triton mask attention（灵活），兼得两者。

### Figure 3 (p.7) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig03.png]]
*整页渲染: ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p07.png]]*
> [!quote] caption
> Decoding speed (tokens/s) across different models and settings. All results are computed at T = 1. The letters G, Q, M, L, and R on the horizontal axis represent the datasets GovReport, QMSum, Multi-News, LCC, and

> [!tip] 技术解读（多模态）
> ## Figure 3 Description

**Layout/Components:** A horizontal array of five grouped bar charts, each panel dedicated to one LLM (Vicuna-7B, Vicuna-13B, LongChat-7B, LongChat-13B, LLaMA-3.1-8B). Each panel plots decoding speed (Tokens/s, 0–120 y-axis) against five long-context datasets on the x-axis: GovReport (G), QMSum (Q), Multi-News (M), LCC (L), RepoBench-P (R). Per dataset, two paired bars compare **MagicDec** (light blue) vs **LongSpec** (dark blue), with numeric values annotated above each bar.

**Key Technical Takeaway:** LongSpec consistently outperforms MagicDec by roughly 2–2.5× across every model/dataset combination (e.g., Vicuna-7B on LCC: 50 vs 119 tokens/s; LongChat-7B on LCC: 51 vs 124 tokens/s), demonstrating that the proposed speculative decoding approach yields robust throughput gains independent of backbone model and dataset choice.

## Caption (Verbatim)

**Figure 3:** Decoding speed (tokens/s) across different models and settings. All results are computed at $T = 1$. The letters G, Q, M, L, and R on the horizontal axis represent the datasets GovReport, QMSum, Multi-News, LCC, and RepoBench-P respectively.

### Figure 4 (p.8) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig04.png]]
*整页渲染: ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p08.png]]*
> [!quote] caption
> Training loss curves on long-context data.

> [!tip] 技术解读（多模态）
> **Figure 5 – Architecture / Components / Data Flow:**

A horizontal stacked bar chart comparing per-loop latency (ms) of two speculative-decoding implementations — "EAGLE" vs. "Hybrid" — broken into four sequential stages: draft-model forward (red hatched), target-model attention (yellow), target-model FFN (green hatched), and verification (blue outline). The EAGLE bar totals ~75 ms, with target attention dominating (~49.9 ms); the Hybrid bar totals ~25 ms, with target attention compressed to ~12.5 ms, while draft, FFN, and verification stages remain roughly equal.

**Key takeaway:** Hybrid Tree Attention cuts the target-model attention latency by ~75% (49.92 → 12.54 ms), which is where almost all the end-to-end speedup originates, since the other three pipeline stages are unchanged.

**Caption verbatim:**
"Figure 5: Latency breakdown for a single speculative decoding loop comparing the EAGLE implementation and the proposed Hybrid Tree Attention. Significant latency reduction is observed in the target model's attention layer (the yellow part) using our approach."

### Figure 5 (p.8) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig05.png]]
*整页渲染: ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p08.png]]*
> [!quote] caption
> Latency breakdown for a single speculative decoding loop comparing the EAGLE implementation and the proposed Hybrid Tree Attention. Significant latency reduction is observed in the target model’s at- tention layer (the yellow part) using our approach.

> [!tip] 技术解读（多模态）
> **Figure 5 – Architecture / Components / Data Flow:**

A horizontal stacked bar chart comparing per-loop latency (ms) of two speculative-decoding implementations — "EAGLE" vs. "Hybrid" — broken into four sequential stages: draft-model forward (red hatched), target-model attention (yellow), target-model FFN (green hatched), and verification (blue outline). The EAGLE bar totals ~75 ms, with target attention dominating (~49.9 ms); the Hybrid bar totals ~25 ms, with target attention compressed to ~12.5 ms, while draft, FFN, and verification stages remain roughly equal.

**Key takeaway:** Hybrid Tree Attention cuts the target-model attention latency by ~75% (49.92 → 12.54 ms), which is where almost all the end-to-end speedup originates, since the other three pipeline stages are unchanged.

**Caption verbatim:**
"Figure 5: Latency breakdown for a single speculative decoding loop comparing the EAGLE implementation and the proposed Hybrid Tree Attention. Significant latency reduction is observed in the target model's attention layer (the yellow part) using our approach."

### Figure 6 (p.9) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig06.png]]
*整页渲染: ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p09.png]]*
> [!quote] caption
> Throughput comparison of Vanilla, MagicDec, and LONGSPEC. not suitable for such long-output scenarios because the initial inference stage of the long reasoning task is not the same as the traditional long-context task. In long reasoning tasks, where the prefix is relatively short, the draft model in MagicDec will completely degrade into the target model, failing to achieve acceleration.

> [!tip] 技术解读（多模态）
> **Figure Description**

The figure is a line chart comparing throughput (tokens/s) across batch sizes 1, 2, 4, and 8 for three methods: Vanilla (blue), MagicDec (orange), and LongSpec (green). All three curves rise with batch size, but LongSpec scales much more steeply, reaching ~561 tokens/s at batch size 8, versus MagicDec (~310) and Vanilla (~287). Vanilla and MagicDec track closely at small batches; MagicDec pulls slightly ahead at batch 4–8.

**Key technical takeaway:** LongSpec's advantage over Vanilla and MagicDec grows with batch size, demonstrating superior scalability for high-throughput inference scenarios.

**Caption (verbatim):** Figure 6: Throughput comparison of Vanilla, MagicDec, and LONGSPEC.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.6) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-tab01.png]]
> [!quote] caption
> and Figure 3 show the decoding speeds and average acceptance lengths across the five evalu- ated datasets at T = 0 and T = 1 , where T denotes the temperature used in LLM sampling. Our pro- posed method significantly outperforms all other approaches on both summarization tasks and code completion ta

> [!tip] 表格解读（多模态）
> I don't see a figure with architecture/components/data flow in the image you provided. The image contains only text — two paragraphs from what appears to be Section X (experimental results) of a paper about "LongSpec," referencing Table 1 and Figure 3 but not depicting them. Here is the caption-able text verbatim:

> "Table 1 and Figure 3 show the decoding speeds and average acceptance lengths across the five evaluated datasets at T = 0 and T = 1, where T denotes the temperature used in LLM sampling. Our proposed method significantly outperforms all other approaches on both summarization tasks and code completion tasks. When T = 0, on summarization tasks, our method can achieve an average acceptance length of around 3.5 and a speedup of up to 2.67×; and on code completion tasks, our method can achieve an average acceptance length of around 4 and a speedup of up to 3.26×. This highlights the robustness and generalizability of our speculative decoding approach, particularly in long-text generation tasks. At T = 1, our method achieves around 2.5× speedup, maintaining a substantial lead over MagicDec. This indicates that our approach is robust across different temperature settings, further validating its soundness and efficiency.
>
> Although PLD can accelerate generation on many datasets, it still does not match the performance of our proposed LongSpec. In some scenarios (e.g., when retrieval is minimal), PLD can even result in negative acceleration. For another baseline, MagicDec, while it demonstrates competitive acceptance rates compared to LongSpec, its speedup is noticeably lower in our experiments. This is because MagicDec is primarily designed"

If you intended to share an architectural diagram (e.g., the LongSpec system figure showing draft/target model interaction, the tree-based speculative decoding flow, or a model pipeline), could you re-upload it? I'd be glad to describe its components and produce the verbatim caption once I can see it.

### Table 4 (p.16) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-tab04.png]]
> [!quote] caption
> Average acceptance length τ and decoding speed (tokens/s) across different models and settings. Specifically, “Vanilla HF” refers to HuggingFace’s PyTorch-based attention implementation, while “Vanilla FA” employs Flash

> [!tip] 表格解读（多模态）
> **Note:** The image provided contains only the caption text for Table 4 — the actual table with numerical values is not visible in the image. I'll describe what the caption conveys and transcribe it.

## Description of the Referenced Figure/Table

The referenced Table 4 reports **average acceptance length τ** (a metric in speculative/sampling-based generation indicating how many tokens a draft is accepted per verification round) and **decoding speed in tokens/s** across multiple model configurations. It compares three implementations: a baseline, "Vanilla HF" (HuggingFace's PyTorch attention), and "Vanilla FA" (Flash Attention), all evaluated at temperature T = 0 (greedy decoding).

**Key Technical Takeaway (≈120 words):** The table benchmarks decoding throughput across attention backends for speculative decoding at greedy settings (T = 0). Acceptance length τ measures how many draft tokens the verifier accepts before a rejection — higher τ reduces verification overhead. Flash Attention (FA) typically yields higher tokens/s than HuggingFace's PyTorch attention due to reduced memory bandwidth via tiled/scaled-dot-product optimization, while τ remains roughly comparable across backends since acceptance depends on logits, not the attention kernel. The takeaway is that the attention implementation choice primarily affects raw decoding speed rather than acceptance behavior, and FA provides the fastest inference path when speculative acceptance is fixed.

## Verbatim Caption Transcription

> Table 4: Average acceptance length τ and decoding speed (tokens/s) across different models and settings. Specifically, "Vanilla HF" refers to HuggingFace's PyTorch-based attention implementation, while "Vanilla FA" employs Flash Attention. All results are computed at T = 0.

### Table 5 (p.16) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-tab05.png]]
> [!quote] caption
> A detailed breakdown of performance as the prefill length increases, with LongChat-7B on GovReport.

> [!tip] 表格解读（多模态）
> ## Figure Description

**Architecture/Components/Data Flow:**
This table (Table 5) presents a performance breakdown of a **speculative decoding system** running LongChat-7B on the GovReport long-context benchmark, sliced across six prefill-length buckets (0–5k through 25k–32k tokens). The components measured are:
- **Tokens/s** — end-to-end decoding throughput
- **τ** — speculative decoding parameter (avg. draft length/acceptance)
- **Draft time (ms)** — small model proposing tokens
- **Target time (ms)** — large model forward pass
- **Verify time (ms)** — token acceptance check

Data flow: input prompt → target prefill → draft proposes k tokens → target verifies batch → accepted tokens appended, looping until stop.

**Key Technical Takeaway:**
Throughput stays nearly flat (~113–117 tok/s) from 0–25k prefill, then drops ~10% to 103.68 tok/s at 25k–32k. This degradation is driven almost entirely by **target-model latency** (25.6 → 30.9 ms, +20%), while draft and verify times grow negligibly (<0.2 ms total), indicating that the large model's attention/KV-cache cost—not the speculative overhead—dominates long-context slowdown.

## Caption (Verbatim)

**Table 5:** A detailed breakdown of performance as the prefill length increases, with LongChat-7B on GovReport.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathrm{LSE}_{\mathrm{merge}} = \log\Bigl(\exp\bigl(\mathrm{LSE}_{\mathrm{cache}}\bigr) \;+\; \exp\bigl(\mathrm{LSE}_{\mathrm{specs}}\bigr)\Bigr),
$$

$$
o_{\mathrm{merge}} = &o_{\mathrm{cache}} \cdot \exp\bigl(\mathrm{LSE}_{\mathrm{cache}} - \mathrm{LSE}_{\mathrm{merge}}\bigr) \\+& o_{\mathrm{specs}} \cdot\exp\bigl(\mathrm{LSE}_{\mathrm{specs}} - \mathrm{LSE}_{\mathrm{merge}}\bigr).
$$

$$
o_{\mathrm{merge}} &= \mha\left(q, K_{\mathrm{merge}}, V_{\mathrm{merge}}\right) \\&= \sm\left( qK_{\mathrm{merge}}^\top/\sqrt{d_{qk}} \right) V_{\mathrm{merge}}.
$$

$$
q K_{\mathrm{merge}}^\top / \sqrt{d_{qk}} = \texttt{concat}\Bigl(& \underbrace{ q \, K_{\mathrm{cache}}^\top / \sqrt{d_{qk}} }_{\mathrm{sub-logits\ for\ history}} \;, \\& \underbrace{ q \, K_{\mathrm{specs}}^\top / \sqrt{d_{qk}} }_{\mathrm{sub-logits\ for\ new}} \Bigr).
$$

$$
Z_{\mathrm{cache}} \;&=\; q \,K_{\mathrm{cache}}^\top / \sqrt{d_{qk}} ,\;\\ Z_{\mathrm{specs}} \;&=\; q \, K_{\mathrm{specs}}^\top / \sqrt{d_{qk}}.
$$

$$
\mathrm{LSE}_{\mathrm{cache}} &= \log\left(\sum\nolimits_{j=1}^{N} \exp\left(Z_{\mathrm{cache}}^{(j)}\right)\right),\nonumber\\ \; \mathrm{LSE}_{\mathrm{specs}} &= \log\left(\sum\nolimits_{j=1}^{M} \exp\left(Z_{\mathrm{specs}}^{(j)}\right)\right), \,
$$

$$
o_{\mathrm{cache}} &= \frac{\sum_{j=1}^{N} \exp\left(Z_{\mathrm{cache}}^{(j)}\right) V_{\mathrm{cache}}^{(j)}}{\exp\left(\mathrm{LSE}_{\mathrm{cache}}\right)}, \nonumber\\ o_{\mathrm{specs}} &= \frac{\sum_{j=1}^{M} \exp\left(Z_{\mathrm{specs}}^{(j)}\right) V_{\mathrm{specs}}^{(j)}}{\exp\left(\mathrm{LSE}_{\mathrm{specs}}\right)}.
$$

$$
N_{\mathrm{num}} &= \sum_{j=1}^{N} \exp\bigl(Z_{\mathrm{cache}}^{(j)}\bigr) V_{\mathrm{cache}}^{(j)}\nonumber\\ &+ \sum_{j=1}^{M} \exp\bigl(Z_{\mathrm{specs}}^{(j)}\bigr) V_{\mathrm{specs}}^{(j)}, \nonumber\\[0.5em] D_{\mathrm{den}} &= \exp\bigl(\mathrm{LSE}_{\mathrm{cache}}\bigr) + \exp\bigl(\mathrm{LSE}_{\mathrm{specs}}\bigr), \nonumber\\[0.5em] o_{\mathrm{merge}} &= \frac{N_{\mathrm{num}}}{D_{\mathrm{den}}}.
$$

$$
o_{\mathrm{merge}} =& o_{\mathrm{cache}} \cdot\exp\bigl(\mathrm{LSE}_{\mathrm{cache}} - \mathrm{LSE}_{\mathrm{merge}}\bigr) \nonumber\\+& o_{\mathrm{specs}} \cdot \exp\bigl(\mathrm{LSE}_{\mathrm{specs}} - \mathrm{LSE}_{\mathrm{merge}}\bigr).
$$

$$
O_{\geq j} = \att \bigl(Q_{\geq j}, \,K_{< l-j}, \,V_{< l-j}\bigr).
$$

$$
\begin{aligned} \mathrm{LSE}_{\mathrm{merge}} &= \log\Bigl(\exp\bigl(\mathrm{LSE}_{\mathrm{cache}}\bigr) + \exp\bigl(\mathrm{LSE}_{\mathrm{specs}}\bigr)\Bigr), \end{aligned}
$$

$$
\begin{aligned} O_{\mathrm{merge}} =\; &O_{\mathrm{cache}} \cdot \exp\bigl(\mathrm{LSE}_{\mathrm{cache}} - \mathrm{LSE}_{\mathrm{merge}}\bigr)\\ +\; &O_{\mathrm{specs}} \cdot \exp\bigl(\mathrm{LSE}_{\mathrm{specs}} - \mathrm{LSE}_{\mathrm{merge}}\bigr). \end{aligned}
$$

## 相关论文

- [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] — JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting
- [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] — DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation
- [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] — SpecExtend: A Drop-in Enhancement for Speculative Decoding of Long Sequences
- [[dflash-block-diffusion-for-flash-speculative-decoding]] — DFlash: Block Diffusion for Flash Speculative Decoding
- [[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]] — DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence
- [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] — MEDUSA: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads

## 技术点深读（DEEP）

![[deep/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification.txt`（76029 字符）供引用检索。