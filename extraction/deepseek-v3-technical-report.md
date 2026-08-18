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
![[assets/deepseek-v3-technical-report-p12.png]]
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
![[assets/deepseek-v3-technical-report-p15.png]]
> [!quote] caption
> Firstly, in order to accelerate model training, the majority of core computation kernels, i.e., GEMM operations, are implemented in FP8 precision. These GEMM operations accept FP8 tensors as inputs and produce outputs in BF16 or FP32. As depicted in Figure 6, all three GEMMs associated with the Linear operator, namely Fprop (forward pass), Dgrad (activation backward pass), and Wgrad (weight backwa

> [!tip] 技术解读（多模态）
> **Figure Description (architecture/components/data flow + key takeaway):**

The diagram depicts a mixed-precision training framework for a `Linear` operator, split into a forward pass and two backward passes. In the **forward (Fprop)**, a BF16 `Input` is cast to FP8 and multiplied with FP8 `Weight`; the matrix product accumulates in FP32, producing a BF16 `Output`. In the **activation backward (Dgrad)**, the BF16 `Output Gradient` is cast to FP8 and combined with the FP8 weight, accumulating to FP32 and yielding a BF16 `Input Gradient`. In the **weight backward (Wgrad)**, the cached FP8 forward input and FP8 output gradient are multiplied with FP32 accumulation, producing an FP32 `Weight Gradient` consumed by an BF16 `Optimizer States` block that updates an FP32 `Master Weight`, which is then re-quantized to FP8 for the next step. **Key takeaway:** compute-heavy GEMMs (Fprop, Dgrad, Wgrad) run in FP8 with FP32 accumulation, while inputs/outputs, optimizer states, and master weights stay in higher precision to preserve numerical stability.

**Caption (verbatim):**

Figure 6 | The overall mixed precision framework with FP8 data format. For clarification, only the `Linear` operator is illustrated.

### Figure 10 (p.48) ⭐深度解读
![[assets/deepseek-v3-technical-report-p48.png]]
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