---
paper_num: "24"
title: "KIMI K2: OPEN AGENTIC INTELLIGENCE"
authors: ""
date: "2026/1/19"
arxiv: "https://arxiv.org/abs/2507.20534"
pdf: "papers/kimi-k2-open-agentic-intelligence.pdf"
slug: "kimi-k2-open-agentic-intelligence"
tags: []
---

# KIMI K2: OPEN AGENTIC INTELLIGENCE

> [!abstract] 摘要（原文）
> 1\. 🚀 Kimi K2是一款万亿参数的MoE大型语言模型，激活参数达320亿，其预训练采用了新颖的MuonClip优化器，在15.5万亿token数据上实现了无损失尖峰的稳定训练。 2. 🤖 该模型通过大规模agentic数据合成管线和结合可验证奖励与自批判机制的强化学习框架进行后训练，显著提升了其在工具使用、软件工程和通用任务中的agentic能力。 3. 🏆 Kimi K2在Tau2-Bench、ACEBench、SWE-Bench Verified和LiveCodeBench v6等多个Agentic和编程基准测试中取得了领先的开放模型表现，并在LMSYS Arena排行榜上成为排名第一的开源模型。

## 元信息
- **发表日期**: 2026/1/19
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2507.20534
- **本地 PDF**: `papers/kimi-k2-open-agentic-intelligence.pdf`
- **页数**: 32

## 图表（原文 caption + 页码）

### Figure 1 (p.1)
![[assets/kimi-k2-open-agentic-intelligence-p01.png]]
> [!quote] caption
> Kimi K2 main results.2 1https://huggingface.co/moonshotai/Kimi-K2-Instruct 2All models evaluated above are non-thinking models. For SWE-bench Multilingual, we evaluated only Claude 4 Sonnet because the cost of Claude 4 Opus was prohibitive.[cs.LG] 3 Feb 2026

### Figure 2 (p.4)
![[assets/kimi-k2-open-agentic-intelligence-p04.png]]
> [!quote] caption
> Left: During a mid-scale training run, attention logits rapidly exceed 1000, which could lead to potential numerical instabilities and even training divergence. Right: Maximum logits for Kimi K2 with MuonClip and t = 100 over the entire training run. The max logits rapidly increase to the capped value of 100, and only decay to a stable range after approximately 30% of the training steps, demonstra

### Figure 3 (p.5)
![[assets/kimi-k2-open-agentic-intelligence-p05.png]]
> [!quote] caption
> Per-step training loss curve of Kimi K2, without smoothing or sub-sampling. It shows no spikes throughout the entire training process. Note that we omit the very beginning of training for clarity. A key advancement in the pre-training data of Kimi K2 over Kimi K1.5 is the introduction of a synthetic data generation strategy to increase token utility. Specifically, a carefully designed rephrasing p

### Figure 4 (p.5)
![[assets/kimi-k2-open-agentic-intelligence-p05.png]]
> [!quote] caption
> • Fidelity verification: To ensure consistency between original and rewritten content, we perform fidelity checks that compare the semantic alignment of each rephrased passage with its source. This serves as an initial quality control step prior to training.

### Figure 5 (p.7)
![[assets/kimi-k2-open-agentic-intelligence-p07.png]]
> [!quote] caption
> Sparsity Scaling Law. Increasing sparsity leads to improved model performance. We fixed the number of activated experts to 8 and the number of shared experts to 1, and varied the total number of experts, resulting in models with different sparsity levels. 10 11

### Figure 6 (p.7)
![[assets/kimi-k2-open-agentic-intelligence-p07.png]]
> [!quote] caption
> Scaling curves for models with number of atten- tion heads equals to number of layers and their counter- parts with doubled attention heads. Doubling the number of attention heads leads to a reduction in validation loss of approximately 0:5% to 1:2%.

### Figure 7 (p.8)
![[assets/kimi-k2-open-agentic-intelligence-p08.png]]
> [!quote] caption
> Computation, communication and offloading overlapped in different PP phases.

### Figure 8 (p.10)
![[assets/kimi-k2-open-agentic-intelligence-p10.png]]
> [!quote] caption
> Data synthesis pipeline for tool use. (a) Tool specs are from both real-world tools and LLMs; agents and tasks are the generated from the tool repo. (b) Multi-agent pipeline to generate and filter trajectories with tool calling. (a) t-SNE visualization of real MCP tools, colored by their original source categories (b) t-SNE visualization of synthetic tools, colored by pre-defined domain categories

### Figure 9 (p.10)
![[assets/kimi-k2-open-agentic-intelligence-p10.png]]
> [!quote] caption
> t-SNE visualizations of tool embeddings. (a) Real-world MCP tools exhibit natural clustering based on their original source categories. (b) Synthetic tools are organized into pre-defined domain categories, providing systematic coverage of the tool space. Together, they ensure comprehensive representation across different tool functionalities.

### Figure 10 (p.14)
![[assets/kimi-k2-open-agentic-intelligence-p14.png]]
> [!quote] caption
> Parameter update utilizing a checkpoint engine

### Figure 11 (p.29)
![[assets/kimi-k2-open-agentic-intelligence-p29.png]]
> [!quote] caption
> Chinese in-house benchmark evaluation. rate, i.e. 98.9. On FaithJudge’s RAG tasks the hallucination rate is 7.4 %, likewise present as 92.6 for table consistency.

### Figure 12 (p.30)
![[assets/kimi-k2-open-agentic-intelligence-p30.png]]
> [!quote] caption
> Applying QK-Clip to Muon in a small-scale setting with an aggresive threshold (t = 30) has negligible impact on loss, indicating that it is a safe and effective method for constraining attention logits.

### Figure 13 (p.32)
![[assets/kimi-k2-open-agentic-intelligence-p32.png]]
> [!quote] caption
> pipeline for RL weight update

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf W_q^{h} \gets \gamma^{\alpha} \mathbf W_q^{h} \qquad \mathbf W_k^{h} \gets \gamma^{1-\alpha} \mathbf W_k^{h}
$$

$$
S_{\max} = \max_{i,j} \bigl(q_i^{\vphantom{\top}}\! \cdot k_j\bigr)
$$

$$
|q_i \!\cdot\! k_j| \le \|q_i\|\|k_j\| \le \|x_i\|\|x_j\|\|\mathbf W_q\|\|\mathbf W_k\|,
$$

$$
\mathbf W_{t-1}=\sum_i \sigma_i\,u_i v_i^{\top}
$$

$$
q_i\cdot k_j=(x_i \mathbf W_q)\cdot (x_j \mathbf W_k).
$$

$$
L_{\mathrm{RL}}(\theta) = \mathbb{E}_{x \sim\mathcal{D}}\left[ \frac{1}{K} \sum_{i=1}^K \left[ \left( r(x, y_i) - \bar{r}(x)- \tau \log \frac{\pi_\theta(y_i | x)}{{\pi}_{\mathrm{old}}(y_i | x)} \right)^2 \right]\right] \, ,
$$

$$
\Delta\mathbf W_t &= \sum_j \bar\sigma\,\bar u_j \bar v_j^{\top}
$$

$$
\mathbf W_t \leftarrow \sum_i \sigma_i u_i v_i^{\top} + \sum_j \bar\sigma\,\bar u_j \bar v_j^{\top}
$$

$$
\mathbf{Q}^{h} = \mathbf X \mathbf W_q^{h}, \quad \mathbf K^{h} = \mathbf X \mathbf W_k^{h}, \quad \mathbf V^{h} = \mathbf X \mathbf W_v^{h}.
$$

$$
\mathbf O^{h} = \operatorname{softmax}\left( \frac{1}{\sqrt{d}} \mathbf Q^{h} \mathbf K^{h\top} \right) \mathbf V^{h}.
$$

$$
S_{\max}^{h} = \frac{1}{\sqrt{d}} \max_{\mathbf X \in B} \max_{i,j} \mathbf Q_i^{h} \mathbf K_j^{h\top}
$$

## 技术点深读（DEEP）

![[deep/kimi-k2-open-agentic-intelligence]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/kimi-k2-open-agentic-intelligence.txt`（112693 字符）供引用检索。