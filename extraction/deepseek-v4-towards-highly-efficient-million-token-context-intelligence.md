---
paper_num: "20"
title: "DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence"
authors: "Towards Highly Efficient Million-Token Context Intelligence DeepSeek-AI research@deepseek.com"
date: "2026/4/28"
arxiv: "https://arxiv.org/abs/2606.19348"
pdf: "papers/deepseek-v4-towards-highly-efficient-million-token-context-intelligence.pdf"
slug: "deepseek-v4-towards-highly-efficient-million-token-context-intelligence"
tags: [long-context]
---

# DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence

> [!abstract] 摘要（原文）
> 1\. 🚀 DeepSeek-V4 系列模型，包括 DeepSeek-V4-Pro 和 DeepSeek-V4-Flash，支持百万级上下文长度，并采用混合注意力机制（CSA 和 HCA）显著提升了长上下文处理效率，相比 DeepSeek-V3.2 大幅降低了 FLOPs 和 KV 缓存占用。 2. 💡 该系列在架构上引入了流形约束超连接 (mHC) 以增强残差连接，并采用 Muon 优化器以实现更快收敛和更高训练稳定性。 3. 🏆 DeepSeek-V4-Pro-Max 在核心任务上重新定义了开放模型的领先水平，其能力通过专家训练和策略蒸馏 (OPD) 的两阶段后训练流程得到整合与增强。

## 元信息
- **发表日期**: 2026/4/28
- **作者**: Towards Highly Efficient Million-Token Context Intelligence DeepSeek-AI research@deepseek.com
- **arXiv**: https://arxiv.org/abs/2606.19348
- **本地 PDF**: `papers/deepseek-v4-towards-highly-efficient-million-token-context-intelligence.pdf`
- **页数**: 58

## 图表（原文 caption + 页码）

### Figure 1 (p.14)
![[assets/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-p14.png]]
> [!quote] caption
> 2.4. Muon Optimizer

### Figure 5 (p.15) ⭐深度解读
![[assets/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-p15.png]]
> [!quote] caption
> This forms a fine-grained pipeline among experts, keeping both computation and communication continuous throughout the wave. The wave-based scheduling speeds up the 15

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】DeepSeek-V4 细粒度 EP(Fig.5)：MoE 层拆 Dispatch/Linear-1/Linear-2/Combine 四段。Comet 仅粗粒度重叠 Dispatch↔L1、L2↔Combine；本方案把 expert 再切 wave，一波 dispatch 完即开算、下一波并行 dispatch→稳态下「当前波计算+下一波 token 传输+上一波结果回送」三路并发=连续计算-通信流水。因单层通信<计算，融合成单流水 kernel 藏住互连延迟→低带宽互连也不掉吞吐。架构核心图，与 MoE/EP 相关。

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.8 `<×< | "1 < = 1<, 1)`
- p.8 `ized: ˆ- : = RMSNorm(vec(- :)) ∈R 1×<hc3. Then, we follow the conventional HC to generate the`
- p.10 `B = hB· ,`
- p.14 `B= ∇, LB(,`

## 相关论文

- [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] — LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and Verification

## 全文文本
全文已存 `extraction/fulltext/deepseek-v4-towards-highly-efficient-million-token-context-intelligence.txt`（45725 字符）供引用检索。