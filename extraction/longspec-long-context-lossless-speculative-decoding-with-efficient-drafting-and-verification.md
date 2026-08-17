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

### Figure 1 (p.1)
![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p01.png]]
> [!quote] caption
> The SoTA SD method, EAGLE, has a training context length of 2048, which is significantly shorter than the context lengths of modern LLMs. 2023), and their ability to handle extensive con- texts is becoming crucial for emerging applications such as LLM agents and long reasoning tasks (Tan et al., 2025; Guo et al., 2025), which now oper- ate over context windows extending to millions of tokens (Team

### Figure 2 (p.4) ⭐深度解读
![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p04.png]]
> [!quote] caption
> Illustration of the memory-efficient draft model, the Anchor-Offset Indices, and the Hybrid Tree Attention. (a) We use a sliding window self-attention layer to capture the local context information and a cross-attention layer to gather long-context information. (b) The differences between the vanilla indexing and the Anchor-Offset

> [!tip] 技术解读（多模态）
> LongSpec 三件套：(a) 内存高效 draft 模型——滑窗自注意力（定长窗口捕捉局部）+ 无 KV cache 的 cross-attention（直接读 target 模型 last-layer K/V 收长程信息），draft KV 占用变常数；(b) Anchor-Offset Indices——保留前 4 个位置作 attention sink，其余 token 从随机大 offset 连续编号，短上下文训练即可覆盖大位置索引、且 target 模型不 OOD（loss 仅 +0.001），弥合训练-推理位置错配；(c) Hybrid Tree Attention——前缀走 FlashAttention（快）+ tree 走 Triton mask attention（灵活），兼得两者。

### Figure 3 (p.7)
![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p07.png]]
> [!quote] caption
> Decoding speed (tokens/s) across different models and settings. All results are computed at T = 1. The letters G, Q, M, L, and R on the horizontal axis represent the datasets GovReport, QMSum, Multi-News, LCC, and

### Figure 4 (p.8)
![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p08.png]]
> [!quote] caption
> Training loss curves on long-context data.

### Figure 5 (p.8)
![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p08.png]]
> [!quote] caption
> Latency breakdown for a single speculative decoding loop comparing the EAGLE implementation and the proposed Hybrid Tree Attention. Significant latency reduction is observed in the target model’s at- tention layer (the yellow part) using our approach.

### Figure 6 (p.9)
![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p09.png]]
> [!quote] caption
> Throughput comparison of Vanilla, MagicDec, and LONGSPEC. not suitable for such long-output scenarios because the initial inference stage of the long reasoning task is not the same as the traditional long-context task. In long reasoning tasks, where the prefix is relatively short, the draft model in MagicDec will completely degrade into the target model, failing to achieve acceleration.

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

## 全文文本
全文已存 `extraction/fulltext/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification.txt`（76029 字符）供引用检索。