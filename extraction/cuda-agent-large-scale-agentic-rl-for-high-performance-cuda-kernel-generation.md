---
paper_num: "68"
title: "CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA Kernel Generation"
authors: "CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA Kernel Generation Weinan Dai1,2,3∗, Hanlin Wu1,2,3∗, Qiying Yu1,2,3, Huan-ang Gao1,2,3, Jiahao Li1, Chengquan Jiang1, Weiqiang Lou1, Yufan Song1, Hongli Yu1,2,"
date: "2026/2/27"
arxiv: "https://arxiv.org/abs/2602.24286"
pdf: "papers/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation.pdf"
slug: "cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation"
tags: []
---

# CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA Kernel Generation

> [!abstract] 摘要（原文）
> GPU kernel optimization is fundamental to modern deep learning but remains a highly specialized task requiring deep hardware expertise. Despite strong performance in general programming, large language models (LLMs) remain uncompetitive with compiler-based systems such as this http URL for CUDA kernel generation. Existing CUDA code generation approaches either rely on training-free refinement or fine-tune models within fixed multi-turn execution-feedback loops, but both paradigms fail to fundamentally improve the model's intrinsic CUDA optimization ability, resulting in limited performance gains. We present CUDA Agent, a large-scale agentic reinforcement learning system that develops CUDA kernel expertise through three components: a scalable data synthesis pipeline, a skill-augmented CUDA development environment with automated verification and profiling to provide reliable reward signals, and reinforcement learning algorithmic techniques enabling stable training. CUDA Agent achieves state-of-the-art results on KernelBench, delivering 100\%, 100\%, and 92\% faster rate over this http URL on KernelBench Level-1, Level-2, and Level-3 splits, outperforming the strongest proprietary models such as Claude Opus 4.5 and Gemini 3 Pro by about 40\% on the hardest Level-3 setting.

## 元信息
- **发表日期**: 2026/2/27
- **作者**: CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA Kernel Generation Weinan Dai1,2,3∗, Hanlin Wu1,2,3∗, Qiying Yu1,2,3, Huan-ang Gao1,2,3, Jiahao Li1, Chengquan Jiang1, Weiqiang Lou1, Yufan Song1, Hongli Yu1,2,
- **arXiv**: https://arxiv.org/abs/2602.24286
- **本地 PDF**: `papers/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation.pdf`
- **页数**: 32

## 图表（原文 caption + 页码）
_未检测到带 caption 的 figure_

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.6 `LRFT(θ) = −Eτ∼D′`
- p.6 `where τ = (s0, s1, . . . , sT −1) denotes a filtered CUDA agent trajectory, πθ is the policy parameterized by θ,`
- p.7 `and δt = rt + γVϕ(st+1) −Vϕ(st) is the temporal difference error with Vϕ(sT ) = 0. We set γ = 1 and λ = 0.95`
- p.7 `LCLIP(θ) = Eτ∼D`
- p.7 `where ρt(θ) =`

## 技术点深读（DEEP）

![[deep/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation.txt`（74680 字符）供引用检索。