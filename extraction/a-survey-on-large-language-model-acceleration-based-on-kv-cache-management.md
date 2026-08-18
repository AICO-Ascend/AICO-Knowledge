---
paper_num: "50"
title: "A Survey on Large Language Model Acceleration based on KV Cache Management"
authors: "A Survey on Large Language Model Acceleration based on KV Cache Management Haoyang Li, Yiming Li, Anxin Tian, Tianhao Tang, Zhanchao Xu, Xuejia Chen, Nicole Hu, Wei Dong, Qing Li Fellow, IEEE, Lei Chen Fellow, ACM/IEEE,"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2412.19442"
pdf: "papers/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management.pdf"
slug: "a-survey-on-large-language-model-acceleration-based-on-kv-cache-management"
tags: [kv-cache]
---

# A Survey on Large Language Model Acceleration based on KV Cache Management

> [!abstract] 摘要（原文）
> 1\. 🤖 大语言模型（LLMs）在推理过程中面临巨大的计算和内存需求，尤其是处理长上下文时，KV cache管理已成为解决此瓶颈的关键优化技术。 2. ⚙️ 该综述系统地将KV cache管理策略划分为token-level、model-level和system-level优化，涵盖了从数据压缩到架构创新再到系统资源调度的广泛技术。 3. 🚀 该研究不仅提供了详细的分类和比较分析，还指出未来研究方向应侧重于跨类别集成、实际部署案例、领域特定优化及隐私安全等挑战。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: A Survey on Large Language Model Acceleration based on KV Cache Management Haoyang Li, Yiming Li, Anxin Tian, Tianhao Tang, Zhanchao Xu, Xuejia Chen, Nicole Hu, Wei Dong, Qing Li Fellow, IEEE, Lei Chen Fellow, ACM/IEEE,
- **arXiv**: https://arxiv.org/abs/2412.19442
- **本地 PDF**: `papers/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management.pdf`
- **页数**: 40

## 图表（原文 caption + 页码）
_未检测到带 caption 的 figure_

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf{Z}_i = \text{Attention}(\mathbf{Q}_i, \mathbf{K}_i, \mathbf{V}_i) = \text{Softmax}\left(\frac{\mathbf{Q}_i \mathbf{K}_i^\top}{\sqrt{d_k}}\right) \mathbf{V}_i,
$$

$$
P(x_{t+1} | x_1, x_2, \cdots, x_t) = \text{Softmax}(\mathbf{h}_t \mathbf{W}_{\text{out}} + \mathbf{b}_{\text{out}}),
$$

$$
x_{t+1} \sim P(x_{t+1} | x_1, x_2, \cdots, x_t).
$$

$$
\text{TD}(\mathbf{W}) = \prod_{k=1}^n \mathcal{T}_{(k)}[d_{k-1}, i_k, j_k, d_k],
$$

$$
\mathbf{Q}_i = \mathbf{X}\mathbf{W}_{Q_i}, \quad \mathbf{K}_i = \mathbf{X}\mathbf{W}_{K_i}, \quad \mathbf{V}_i = \mathbf{X}\mathbf{W}_{V_i},
$$

$$
\mathbf{Z}=\text{Concat}(\mathbf{Z}_1, \mathbf{Z}_2, \dots, \mathbf{Z}_h)\mathbf{W}_O,
$$

$$
\text{FFN}(\mathbf{Z}) = \sigma(\mathbf{Z}\mathbf{W}_1 + \mathbf{b}_1)\mathbf{W}_2 + \mathbf{b}_2
$$

$$
\mathbf{q}_i^t &= \mathbf{x}_t \mathbf{W}_{Q_i}, \quad \mathbf{k}_i^t = \mathbf{x}_t \mathbf{W}_{K_i}, \quad \mathbf{v}_i^t = \mathbf{x}_t \mathbf{W}_{V_i},
$$

$$
\mathbf{K}_i^{t} &= \text{Concat}(\mathbf{\hat{K}}_i^{t-1}, \mathbf{k}_i^t ), \ \mathbf{V}_i^{t} = \text{Concat}(\mathbf{\hat{V}}^{t-1}_i, \mathbf{V}_i^t ),
$$

$$
\mathbf{z}^t_i = \text{Softmax}\left(\frac{\mathbf{q}_i^t {\mathbf{K}_i^t}^\top}{\sqrt{d_k}}\right) \mathbf{V}_i^t,
$$

$$
O\left(L\cdot h \cdot t_c \cdot t \cdot (d_k+d_v)+ L\cdot h \cdot t_c\left(\triangle_1 + \triangle_2\right)\right)
$$

$$
O(L\cdot h \cdot t_c \cdot (d_k+d_v) \cdot sizeof(Float16))
$$

## 相关论文

- [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] — CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion
- [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] — KV Cache Optimization Strategies for Scalable and Efficient LLM Inference
- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] — Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter
- [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] — IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse

## 技术点深读（DEEP）

![[deep/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management.txt`（233789 字符）供引用检索。