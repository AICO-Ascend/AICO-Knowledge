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

### Figure 1 (p.2)
![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p02.png]]
> [!quote] caption
> End-to-end decoding speedup over standard autoregressive decoding on H100 GPUs across math, coding, and chat benchmarks. DFlash denotes the original block-parallel drafting method, DDTree is tree-based variant of DFlash, and JetSpec denotes our method. Both employ a tree budget of 256 tokens using Algorithm 1. acceleration. Despite these advances, head-based SD still faces a causality-efficiency d

### Figure 2 (p.3) ⭐MiniMax深度解读
![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p03.png]]
> [!quote] caption
> Expected speculative decoding speedup scales as a function of draft length γ, under different per-token drafting costs c and acceptance rates α. Comparing the two panels shows that reducing c substantially improves the scalability of speculative decoding with respect to γ, and increasing α further amplifies this effect. The results highlight that pushing per-token drafting cost c low and acceptanc

> [!tip] 技术解读（MiniMax 多模态）
> 【MiniMax 解读】JetSpec 因果并行草稿头(Fig.3)：轻量 draft head 接冻结目标模型 M_q 中间层融合特征，单次前向并行预测所有 γ 个 draft 位的 top-k 候选→组成 k^γ 候选树；输出重排为广度优先、分支级因果序列再回灌 M_q 验证（满足 tree-SD 左到右依赖）。M_q 冻结只训 head。把草稿成本 c 压到 head 级、接受率 α 保持高→加速随 γ 单调增长，破解 c/α 鱼与熊掌。架构核心图。

### Figure 3 (p.4)
![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p04.png]]
> [!quote] caption
> JetSpec design overview. JetSpec extracts fused hidden features from the frozen target model and conditions a causal-parallel draft head to generate high-quality candidate trees in one forward pass.

### Figure 4 (p.15)
![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p15.png]]
> [!quote] caption
> Tree-quality failure mode at MATH-500 prompt #0, decode step 0. Both heads draft from the same prefix (last token “We”). The causal head’s rank-1 branch (“ are told that”) is faithful: target joint Σ log p ≈Σ log r, so tree verification walks 6 tokens along it. The diffusion head’s rank-1 branch (“ given told that”) is incoherent (target joint Σ log p = −63.32 nats, i.e. probability ≈e−63) because

### Figure 5 (p.18)
![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p18.png]]
> [!quote] caption
> Figure 5: Causal attention mask used for training with multiple sampled blocks. Each query can attend to the full verified prefix and to the anchor plus earlier positions within its own block, but cannot attend to future positions or positions from other sampled blocks. JETSPEC reuses intermediate representations from the frozen target model as draft-head context. For

### Figure 6 (p.19)
![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p19.png]]
> [!quote] caption
> Each sampled block includes an anchor position and multiple future token positions. The anchor is retained as block context and excluded from the loss, while loss is applied only to future token positions within each block. allowing the causal draft head to condition on rich target-model features while keeping the target model frozen.

## 全文文本
全文已存 `extraction/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting.txt`（70018 字符）供引用检索。