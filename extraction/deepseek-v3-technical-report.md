---
paper_num: "41"
title: "DeepSeek-V3 Technical Report"
authors: "DeepSeek-AI research@deepseek.com"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2412.19437"
pdf: "papers/deepseek-v3-technical-report.pdf"
slug: "deepseek-v3-technical-report"
tags: []
---

# DeepSeek-V3 Technical Report

> [!abstract] 摘要（原文）
> 1\. 🤖 DeepSeek-V3是一个拥有671B总参数和37B激活参数的强大MoE语言模型，其核心创新包括无辅助损失的负载均衡策略和Multi-Token Prediction训练目标。 2. 🚀 该模型通过高效的FP8混合精度训练框架和DualPipe算法，实现了近乎完全的计算-通信重叠，并以仅2.788M H800 GPU小时的经济成本完成了14.8T tokens的预训练。 3. 🏆 综合评估表明，DeepSeek-V3在知识、代码和数学等多个基准测试中超越了其他开源模型，并达到了与GPT-4o和Claude-3.5-Sonnet等领先闭源模型相当的性能。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: DeepSeek-AI research@deepseek.com
- **arXiv**: https://arxiv.org/abs/2412.19437
- **本地 PDF**: `papers/deepseek-v3-technical-report.pdf`
- **页数**: 53

## 图表（原文 caption + 页码）

### Figure 5 (p.12) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-fig05.png]]
*整页渲染: ![[assets/deepseek-v3-technical-report-p12.png]]*
> [!quote] caption
> It employs a bidirectional pipeline scheduling, which feeds micro-batches from both ends of the pipeline simultaneously and a significant portion of communications can be fully overlapped. This overlap also ensures that, as the model further scales up, as long as we maintain a constant computation-to-communication ratio, we can still employ fine-grained experts across nodes while achieving a near-

> [!tip] 技术解读（多模态）
> ## Figure 4 Description

The diagram is a **two-row timeline** (time →) showing how forward and backward pipeline chunks are interleaved at the sub-operator level:

- **Computation row** (top): sequences of ATTN and MLP operators. Each forward/backward chunk is split into *Forward* (F), *Backward-for-input* (B), and *Backward-for-weights* (W) sub-pieces — boundaries between adjacent forward and backward chunks are *not* aligned.
- **Communication row** (bottom): DISPATCH (pre-MLP all-to-all), COMBINE (post-MLP all-to-all), and a central PP (pipeline-parallel) block.

**Key takeaway:** By mis-aligning the chunk boundaries and rearranging sub-operators, DualPipe hides the all-to-all and PP communication entirely behind on-streaming GPU SMs executing computation — eliminating the 1:1 compute-to-communicate bottleneck of cross-node MoE training.

## Caption (verbatim)

**Figure 4** | Overlapping strategy for a pair of individual forward and backward chunks (the boundaries of the transformer blocks are not aligned). Orange denotes forward, green denotes "backward for input", blue denotes "backward for weights", purple denotes PP communication, and red denotes barriers. Both all-to-all and PP communication can be fully hidden.

### Figure 6 (p.15) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-fig06.png]]
*整页渲染: ![[assets/deepseek-v3-technical-report-p15.png]]*
> [!quote] caption
> Firstly, in order to accelerate model training, the majority of core computation kernels, i.e., GEMM operations, are implemented in FP8 precision. These GEMM operations accept FP8 tensors as inputs and produce outputs in BF16 or FP32. As depicted in Figure 6, all three GEMMs associated with the Linear operator, namely Fprop (forward pass), Dgrad (activation backward pass), and Wgrad (weight backwa

> [!tip] 技术解读（多模态）
> **Figure Description (architecture/components/data flow + key takeaway):**

The diagram depicts a mixed-precision training framework for a `Linear` operator, split into a forward pass and two backward passes. In the **forward (Fprop)**, a BF16 `Input` is cast to FP8 and multiplied with FP8 `Weight`; the matrix product accumulates in FP32, producing a BF16 `Output`. In the **activation backward (Dgrad)**, the BF16 `Output Gradient` is cast to FP8 and combined with the FP8 weight, accumulating to FP32 and yielding a BF16 `Input Gradient`. In the **weight backward (Wgrad)**, the cached FP8 forward input and FP8 output gradient are multiplied with FP32 accumulation, producing an FP32 `Weight Gradient` consumed by an BF16 `Optimizer States` block that updates an FP32 `Master Weight`, which is then re-quantized to FP8 for the next step. **Key takeaway:** compute-heavy GEMMs (Fprop, Dgrad, Wgrad) run in FP8 with FP32 accumulation, while inputs/outputs, optimizer states, and master weights stay in higher precision to preserve numerical stability.

**Caption (verbatim):**

Figure 6 | The overall mixed precision framework with FP8 data format. For clarification, only the `Linear` operator is illustrated.

### Figure 10 (p.48) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-fig10.png]]
*整页渲染: ![[assets/deepseek-v3-technical-report-p48.png]]*
> [!quote] caption
> 48

> [!tip] 技术解读（多模态）
> **No figure is visible on this page.**

The provided image (page 48) contains only text from an academic paper — specifically, the tail of a paragraph about MoE model divergence, a section heading ("C. Expert Specialization Patterns of the 16B Aux-Loss-Based and Aux-Loss-Free Models"), and an introductory paragraph that *references* Figure 10, but the figure itself is not rendered on this page.

**What the text tells us about the referenced figure (Figure 10):**
- It compares two 16B-parameter MoE models: an auxiliary-loss-based baseline vs. an auxiliary-loss-free variant.
- It plots **expert load** (per-layer) measured on the Pile test set.
- Data flow conceptually: Pile test tokens → MoE layers → router assigns tokens to experts → expert-activation counts aggregated per layer → visualized.
- **Key takeaway:** Removing the auxiliary load-balancing loss yields *greater expert specialization* (more skewed / concentrated expert usage) across all layers.

If you can share the image of Figure 10 itself, I can describe its specific architecture (e.g., layer-by-layer heatmap, bar chart, distribution plot) and transcribe its actual caption verbatim.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab01.png]]
> [!quote] caption
> | Training costs of DeepSeek-V3, assuming the rental price of H800 is $2 per GPU hour.

> [!tip] 表格解读（多模态）
> I'm unable to fulfill this request as described because **no figure is present in the provided content**. What you've shared is text excerpted from the DeepSeek-V3 paper (sections discussing training cost and contributions). Specifically:

- The opening line references "Table 1 | Training costs of DeepSeek-V3, assuming the rental price of H800 is $2 per GPU hour," but the table itself is not included.
- No architecture diagram, component schematic, or data-flow figure accompanies this text.

**What is available to transcribe verbatim:**

> Table 1 \| Training costs of DeepSeek-V3, assuming the rental price of H800 is $2 per GPU hour.

If you intended to share a figure (e.g., the DeepSeek-V3 MoE architecture diagram or a pipeline illustration from the paper), the image did not come through. Please re-upload the figure, and I'll be glad to:

1. Describe its architecture/components/data flow,
2. Give one key technical takeaway (≤120 words), and
3. Transcribe the caption verbatim.

### Table 2 (p.13) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab02.png]]
> [!quote] caption
> | Comparison of pipeline bubbles and memory usage across different pipeline parallel methods. 𝐹 denotes the execution time of a forward chunk, 𝐵 denotes the execution time of a full backward chunk, 𝑊 denotes the execution time of a "backward for weights" chunk, and 𝐹 & 𝐵 denotes the execution time o

> [!tip] 表格解读（多模态）
> ## Figure Description

**Table 2 — Pipeline Parallelism Method Comparison**

**Components/Columns:** Rows represent competing PP schemes (DualPipe, ZB1P, 1F1B, Chimera); columns report pipeline-bubble fraction, peak activation memory overhead, parameter-memory cost, and scaling behavior with respect to micro-batch count and pipeline stages.

**Data flow metaphor:** Each row is a Gantt-style schedule across pipeline stages, where chunks are placed sequentially — forward chunk *F*, full backward chunk *B*, weight-backward chunk *W*, or a fused *F&B* (two mutually overlapped forward/backward chunks). Bubble = idle time on the stage that currently holds the "tail" of the schedule.

**Key takeaway:** DualPipe cuts pipeline bubbles relative to ZB1P/1F1B while raising peak activation memory by only **1/PP**, and unlike Chimera it imposes no divisibility constraint between micro-batch count and pipeline stage count.

*(~110 words)*

## Caption (verbatim)

**Table 2 |** Comparison of pipeline bubbles and memory usage across different pipeline parallel methods. *F* denotes the execution time of a forward chunk, *B* denotes the execution time of a full backward chunk, *W* denotes the execution time of a "backward for weights" chunk, and *F&B* denotes the execution time of two mutually overlapped forward and backward chunks.

### Table 3 (p.25) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab03.png]]
> [!quote] caption
> | Comparison among DeepSeek-V3-Base and other representative open-source base models. All models are evaluated in our internal framework and share the same evaluation setting. Scores with a gap not exceeding 0.3 are considered to be at the same level. DeepSeek- V3-Base achieves the best performance 

> [!tip] 表格解读（多模态）
> **Description of Main Figure:**

This is a comprehensive evaluation comparison table (Table 3) showing benchmark performance across four language models with varying architectures. Columns compare architectures (Dense vs. MoE) with activated/total parameter counts spanning 21B–37B activated and 72B–671B total parameters. Rows are grouped by capability domain (English understanding, Code generation, Math reasoning, Chinese tasks, and Multilingual), totaling ~30 benchmarks including MMLU, HumanEval, GSM8K, and C-Eval. Most cells report n-shot scores.

**Key Technical Takeaway:** DeepSeek-V3-Base (MoE, 37B activated / 671B total) outperforms larger dense models—most strikingly on math (MATH: 61.6 vs. 54.4) and code (HumanEval: 65.2 vs. 54.9)—demonstrating that sparse activation can beat dense scaling at a fraction of compute per token.

**Caption (Verbatim Transcription):**
"Table 3 | Comparison among DeepSeek-V3-Base and other representative open-source base models. All models are evaluated in our internal framework and share the same evaluation setting. Scores with a gap not exceeding 0.3 are considered to be at the same level. DeepSeek-V3-Base achieves the best performance on most benchmarks, especially on math and code tasks."

### Table 4 (p.26) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab04.png]]
> [!quote] caption
> | Ablation results for the MTP strategy. The MTP strategy consistently enhances the model performance on most of the evaluation benchmarks.

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**

Table 4 presents an ablation study comparing two MoE configurations (Small: 2.4B activated / 15.7B total params, 1.33T tokens; Large: 20.9B activated / 228.7B total params, 540B tokens) each evaluated with and without the MTP (Multi-Token Prediction) auxiliary objective. Columns pair "Baseline" against "w/ MTP," with rows listing 10 benchmarks (Pile-test BPB, BBH, MMLU, DROP, TriviaQA, NaturalQuestions, HumanEval, MBPP, GSM8K, MATH) at their standard few-shot settings, alongside inference parameter counts and training-token totals. **Key takeaway:** MTP delivers consistent gains across both scales—most notably on coding/math tasks (HumanEval: 20.7→26.8 small, 44.5→53.7 large; GSM8K: 25.4→31.4 small)—while negligible overhead (Bold values in "w/ MTP" columns) and tiny degradation on Pile-test BPB (0.729→0.657 large) confirm MTP as a near-free performance booster.

**Caption (verbatim):**
Table 4 | Ablation results for the MTP strategy. The MTP strategy consistently enhances the model performance on most of the evaluation benchmarks.

### Table 5 (p.27) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab05.png]]
> [!quote] caption
> | Ablation results for the auxiliary-loss-free balancing strategy. Compared with the purely auxiliary-loss-based method, the auxiliary-loss-free strategy consistently achieves better model performance on most of the evaluation benchmarks.

> [!tip] 表格解读（多模态）
> No figure is present in the provided image — only Table 5's caption and an accompanying explanatory paragraph are visible. Based on the surrounding text, here is a description and the verbatim caption.

**Description of the table (≈110 words):**
The table presents ablation results comparing two baseline configurations against their auxiliary-loss-free counterparts. The two baselines are based on DeepSeek-V2-Lite and DeepSeek-V2, both employing auxiliary losses to encourage expert load balance together with a sigmoid gating function and top-K affinity normalization. The ablation isolates a single design variable: replacing the auxiliary-loss balancing mechanism with the proposed auxiliary-loss-free balancing strategy, while keeping the training data and all other architectural components identical. The reported numbers across multiple evaluation benchmarks show that the auxiliary-loss-free variant consistently outperforms its auxiliary-loss baseline, indicating that the balancing signal can be effectively decoupled from the loss function.

**Key technical takeaway:** The auxiliary-loss-free balancing strategy yields better benchmark performance than the auxiliary-loss-based approach, demonstrating that effective expert balancing can be achieved without injecting balancing terms into the training loss.

**Caption transcribed verbatim:**
"Table 5 | Ablation results for the auxiliary-loss-free balancing strategy. Compared with the purely auxiliary-loss-based method, the auxiliary-loss-free strategy consistently achieves better model performance on most of the evaluation benchmarks."

### Table 6 (p.31) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab06.png]]
> [!quote] caption
> | Comparison between DeepSeek-V3 and other representative chat models. All models are evaluated in a configuration that limits the output length to 8K. Benchmarks containing fewer than 1000 samples are tested multiple times using varying temperature settings to derive robust final results. DeepSeek-

> [!tip] 表格解读（多模态）
> # Description

This is **Table 6** (not an architectural figure) — a benchmark comparison matrix. **Columns** list evaluated models: DeepSeek-V2-0506, DeepSeek-V2.5-0905, Qwen2.5-72B-Inst., LLaMA-3.1-405B-Inst., Claude-3.5-Sonnet-1022, GPT-4o-0513, and DeepSeek-V3, along with header rows for architecture (MoE vs. Dense), # Activated Params, and # Total Params. **Rows** are grouped by category — English (MMLU, DROP, GPQA, FRAMES, etc.), Code (HumanEval-Mul, LiveCodeBench, Codeforces, SWE-Bench, Aider), Math (AIME, MATH-500, CNMO), and Chinese (CLUEWSC, C-Eval) — each with a specific metric. **Data flow:** benchmark dataset → model inference (≤8K output tokens, temp 0.7 averaging for some) → metric score per cell.

**Key takeaway:** DeepSeek-V3 (MoE, 37B activated / 671B total) achieves top scores on most code/math/Chinese benchmarks (bolded) while matching or exceeding GPT-4o/Claude-3.5 on several English tasks — the strongest open-source result in the comparison.

# Caption (verbatim)

**Table 6 | Comparison between DeepSeek-V3 and other representative chat models.** All models are evaluated in a configuration that limits the output length to 8K. Benchmarks containing fewer than 1000 samples are tested multiple times using varying temperature settings to derive robust final results. DeepSeek-V3 stands as the best-performing open-source model, and also exhibits competitive performance against frontier closed-source models.

### Table 7 (p.33) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab07.png]]
> [!quote] caption
> | English open-ended conversation evaluations. For AlpacaEval 2.0, we use the length- controlled win rate as the metric.

> [!tip] 表格解读（多模态）
> No figure or table image was attached to your message—only caption text and surrounding paragraphs are visible. Therefore I cannot describe architecture, components, or data flow of a visualization that wasn't provided, nor offer a technical takeaway grounded in such a figure.

Here is the caption transcribed verbatim:

> Table 7 | English open-ended conversation evaluations. For AlpacaEval 2.0, we use the length-controlled win rate as the metric.

If you intended to include the figure (e.g., a diagram, screenshot, or the Table 7 data itself), please re-upload or paste it and I'll provide the architecture/data-flow description and a ≤120-word technical takeaway as requested.

### Table 8 (p.34) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab08.png]]
> [!quote] caption
> | Performances of GPT-4o, Claude-3.5-sonnet and DeepSeek-V3 on RewardBench.

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**

The figure is a results table titled "Table 8" presenting model performance on RewardBench. **Columns**: Model | LiveCodeBench-CoT (Pass@1, Length) | MATH-500 (Pass@1, Length). **Rows**: "DeepSeek-V2.5 Baseline" (31.1 / 718 / 74.6 / 769) and "DeepSeek-V2.5 +R1 Distill" (37.4 / 783 / 83.2 / 1510). **Data flow**: Only tabular aggregates are shown; no architecture diagram or flow exists. **Key takeaway**: Applying R1 distillation on top of DeepSeek-V2.5 boosts Pass@1 on both code (+6.3) and math (+8.6), but nearly doubles output length on MATH-500 (769→1510), revealing an accuracy-vs-inference-cost tradeoff rather than a free improvement.

**Caption (verbatim):**

Table 8 | Performances of GPT-4o, Claude-3.5-sonnet and DeepSeek-V3 on RewardBench.

### Table 9 (p.34) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab09.png]]
> [!quote] caption
> | The contribution of distillation from DeepSeek-R1. The evaluation settings of Live- CodeBench and MATH-500 are the same as in Table 6.

> [!tip] 表格解读（多模态）
> **Note:** The provided image contains two **tables**, not an architectural figure. No architecture/components/data-flow diagram is present. Below I summarize what the tables show, then supply the verbatim captions.

## What the tables show

**Table 8 — RewardBench comparison** of three model families (GPT-4o, Claude-3.5-Sonnet, DeepSeek-V3) across three release snapshots each, scored on five benchmark columns (values visible: roughly 95–97 on the first column, 70–82 on the second, 86–91 on the third, 84–89 on the fourth, 84–89 on the fifth). DeepSeek-V3 with **majority voting (maj@6)** posts the best scores across the last four metrics.

**Table 9 — Distillation ablation** comparing a DeepSeek-V2.5 Baseline vs. +R1 Distill on two tasks:

| Variant | LiveCodeBench Pass@1 | … Length | MATH-500 Pass@1 | … Length |
|---|---|---|---|---|
| V2.5 Baseline | 31.1 | 718 | 74.6 | 769 |
| V2.5 + R1 Distill | 37.4 | 783 | 83.2 | 1510 |

**Key technical takeaway (≤120 words):**
R1-style reasoning distillation is highly sample-efficient: adding it on top of DeepSeek-V2.5 **lifts LiveCodeBench Pass@1 by +6.3** (31.1 → 37.4) for only ~9% more output tokens, and **boosts MATH-500 Pass@1 by +8.6** (74.6 → 83.2), though at the cost of nearly **doubling response length** (769 → 1510 tokens). Versus GPT-4o and Claude-3.5-Sonnet, DeepSeek-V3 with maj@6 is the strongest on RewardBench, while the distillation results show that long-chain reasoning traces transfer even when the student model is much smaller than the teacher.

## Verbatim captions

**Table 8 caption:**
"Table 8 | Performances of GPT-4o, Claude-3.5-sonnet and DeepSeek-V3 on RewardBench."

**Table 9 caption:**
"Table 9 | The contribution of distillation from DeepSeek-R1. The evaluation settings of LiveCodeBench and MATH-500 are the same as in Table 6."

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf{h}_i^{\prime k} = M_k [\operatorname{RMSNorm}(\mathbf{h}_i^{k-1}) ; \operatorname{RMSNorm}(\operatorname{Emb}(t_{i+k}))],
$$

$$
\mathbf{h}_{1:T-k}^{k} = \operatorname{TRM}_k(\mathbf{h}_{1:T-k}^{\prime k}),
$$

$$
P_{i+k+1}^{k} = \operatorname{OutHead}(\mathbf{h}_{i}^{k}).
$$

$$
\mathcal{L}_{\text{MTP}}^{k} = \operatorname{CrossEntropy}(P_{2 + k:T + 1}^{k}, t_{2 + k:T + 1}) = -\frac{1}{T} \sum_{i=2 + k}^{T + 1} \log P_i^k [t_i],
$$

$$
\mathcal{L}_{\text{MTP}} = \frac{\lambda}{D} \sum_{k=1}^{D} \mathcal{L}_{\text{MTP}}^{k}.
$$

$$
\begin{split} \mathcal{J}_{GRPO}(\theta) &= \mathbb{E}{[q \sim P(Q), \{o_i\}_{i=1}^G \sim \pi_{\theta_{old}}(O|q)]} \\ & \frac{1}{G}\sum_{i=1}^G \left( \min \left( \frac{\pi_\theta(o_i |q)}{\pi_{\theta_{old}}(o_i |q)} A_i, \text{clip} \left( \frac{\pi_\theta(o_i |q)}{\pi_{\theta_{old}}(o_i |q)}, 1 - \epsilon, 1 + \epsilon \right) A_i \right) - \beta \mathbb{D}_{KL}\left(\pi_{\theta} || \pi_{ref}\right)\right) , \end{split}
$$

$$
\mathbb{D}_{KL}\left(\pi_{\theta} || \pi_{ref}\right) = \frac{\pi_{ref}(o_i|q)}{\pi_{\theta}(o_i|q)}- \log\frac{\pi_{ref}(o_i|q)}{\pi_{\theta}(o_i|q)} - 1,
$$

$$
A_i = \frac{r_i - {\operatorname{mean}(\{r_1, r_2, \cdots, r_G\})}}{{\operatorname{std}(\{r_1, r_2, \cdots, r_G\})}}.
$$

$$
\boxed{\color{blue} \mathbf{c}_{t}^{KV}} &= W^{DKV} \mathbf{h}_{t}, \\ [\mathbf{k}_{t, 1}^{C};\mathbf{k}_{t, 2}^{C};...;\mathbf{k}_{t, n_{h}}^{C}] = \mathbf{k}_{t}^{C} &= W^{UK} \mathbf{c}_{t}^{KV}, \\ \boxed{\color{blue}\mathbf{k}_{t}^{R}} &= \operatorname{RoPE}({W^{KR}} \mathbf{h}_{t}), \\ \mathbf{k}_{t, i} &= [\mathbf{k}_{t, i}^{C}; \mathbf{k}_{t}^{R}], \\ [\mathbf{v}_{t, 1}^{C};\mathbf{v}_{t, 2}^{C};...;\mathbf{v}_{t, n_{h}}^{C}] = \mathbf{v}_{t}^{C} &= W^{UV} \mathbf{c}_{t}^{KV},
$$

$$
\mathbf{c}_{t}^{Q} &= W^{DQ} \mathbf{h}_{t}, \\ [\mathbf{q}_{t, 1}^{C};\mathbf{q}_{t, 2}^{C};...;\mathbf{q}_{t, n_{h}}^{C}] = \mathbf{q}_{t}^{C} &= W^{UQ} \mathbf{c}_{t}^{Q}, \\ [\mathbf{q}_{t, 1}^{R};\mathbf{q}_{t, 2}^{R};...;\mathbf{q}_{t, n_{h}}^{R}] = \mathbf{q}_{t}^{R} &= \operatorname{RoPE}({W^{QR}} \mathbf{c}_{t}^{Q}), \\ \mathbf{q}_{t, i} &= [\mathbf{q}_{t, i}^{C}; \mathbf{q}_{t, i}^{R}],
$$

$$
\mathbf{o}_{t, i} &= \sum_{j=1}^{t} \operatorname{Softmax}_j(\frac{\mathbf{q}_{t, i}^T \mathbf{k}_{j, i}}{\sqrt{d_{h} + d_{h}^{R}}}) \mathbf{v}_{j, i}^{C}, \\ \mathbf{u}_{t} &= W^{O} [\mathbf{o}_{t, 1};\mathbf{o}_{t, 2};...;\mathbf{o}_{t, n_{h}}],
$$

$$
\mathbf{h}_{t}^{\prime} & = \mathbf{u}_{t} + \sum_{i=1}^{N_{s}} {\operatorname{FFN}^{(s)}_{i}\left( \mathbf{u}_{t} \right)} + \sum_{i=1}^{N_r} {g_{i,t} \operatorname{FFN}^{(r)}_{i}\left( \mathbf{u}_{t} \right)}, \\ g_{i,t} & = \frac{g^{\prime}_{i,t}}{\sum_{j=1}^{N_r} g^{\prime}_{j,t}}, \\ g^{\prime}_{i,t} & = \begin{cases} s_{i,t}, & s_{i,t} \in \operatorname{Topk} (\{ s_{j, t} | 1 \leq j \leq N_r \}, K_{r}), \\ 0, & \text{otherwise}, \end{cases} \\ s_{i,t} & = \operatorname{Sigmoid} \left( {\mathbf{u}_{t}}^{T} \mathbf{e}_{i} \right),
$$

$$
g^{\prime}_{i,t} & = \begin{cases} s_{i,t}, & s_{i,t} + b_i \in \operatorname{Topk} (\{ s_{j, t} + b_j | 1 \leq j \leq N_r \}, K_{r}), \\ 0, & \text{otherwise}. \end{cases}
$$

$$
\mathcal{L}_{\mathrm{Bal}} & = \alpha \sum_{i=1}^{N_r}{f_i P_i}, \\ f_i = \frac{N_r}{K_r T} \sum_{t=1}^{T} \mathds{1} & \left( s_{i,t} \in \operatorname{Topk} ( \{ s_{j, t} | 1 \leq j \leq N_r \}, K_{r} ) \right), \\ s^{\prime}_{i,t} & = \frac{s_{i,t}}{\sum_{j=1}^{N_r} s_{j,t}}, \\ P_i & = \frac{1}{T} \sum_{t=1}^{T}{s^{\prime}_{i,t}},
$$

$$
\texttt{<|fim\_begin|>}f_{\text{pre}}\texttt{<|fim\_hole|>}f_{\text{suf}}\texttt{<|fim\_end|>}f_{\text{middle}}\texttt{<|eos\_token|>} . \nonumber
$$

## 技术点深读（DEEP）

![[deep/deepseek-v3-technical-report]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/deepseek-v3-technical-report.txt`（150416 字符）供引用检索。