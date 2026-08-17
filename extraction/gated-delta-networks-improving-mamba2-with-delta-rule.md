---
paper_num: "55"
title: "Gated Delta Networks: Improving Mamba2 with Delta Rule"
authors: ""
date: "2024/12/9"
arxiv: "https://arxiv.org/abs/2412.06464"
pdf: "papers/gated-delta-networks-improving-mamba2-with-delta-rule.pdf"
slug: "gated-delta-networks-improving-mamba2-with-delta-rule"
tags: [architecture]
---

# Gated Delta Networks: Improving Mamba2 with Delta Rule

> [!abstract] 摘要（原文）
> 1. Linear Transformers have gained attention as efﬁcient alternatives to standard Transformers, but their performance in retrieval and long-context tasks has been limited. To address these limitations, recent work has explored two distinct mech- anisms: gating for adaptive memory control and the delta update rule for pre- cise memory modiﬁcations. We observe that these mechanisms

## 元信息
- **发表日期**: 2024/12/9
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2412.06464
- **本地 PDF**: `papers/gated-delta-networks-improving-mamba2-with-delta-rule.pdf`
- **页数**: 22

## 图表（原文 caption + 页码）

### Figure 1 (p.7) ⭐深度解读
![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p07.png]]
> [!quote] caption
> Visualization of the (hybrid) architecture and block design of Gated DeltaNet models.

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】Gated DeltaNet 架构(Fig.1)：delta-rule 线性注意力 + 乘性门控(α,β)增联想召回；H1/H2 混合变体把 Gated DeltaNet 与 Mamba2(SSM) + Sliding-Window Attention 交错，融合选择性长程记忆+结构化递归+局部上下文。block 设计：q/k 路径=线性投影+shortconv+SiLU+L2norm，v=线性投影+shortconv+SiLU，α/β=线性投影，输出 gate=线性投影+SiLU。Wiki ppl 16.42、zero-shot 55.32，H2 混合 ppl 15.91 最优。线性注意力/SSM 架构核心图。

### Figure 2 (p.8)
![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p08.png]]
> [!quote] caption
> Length extrapolation on six long benchmarks.

### Figure 3 (p.9)
![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p09.png]]
> [!quote] caption
> Training throughput comparison of 1.3B models on a single H100 GPU. standalone mixers: Samba outperforms Mamba, while Gated DeltaNet-H1 and -H2 outperform

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\rmS_t = \rmS_{t-1} + \vv_t \vk_t^\intercal \in \mathbb{R}^{d_v \times d_k}, \qquad \qquad \vo_t = \rmS_t \vq_t \in \mathbb{R}^{d_v}
$$

$$
\vo_t = \sum_{i=1}^t (\vv_i \vk_i^\intercal) \vq_t = \sum_{i=1}^t \vv_i (\vk_i^\intercal \vq_t) \in \mathbb{R}^{d_v}, \qquad \rmO = (\rmQ \rmK^\intercal \odot \rmM) \rmV \in \mathbb{R}^{L \times d_v}
$$

$$
\rmS_{[t]}^r = \rmS_{[t]} + \sum_{i=1}^r \vv_{[t]}^{i} \vk_{[t]}^{i\intercal} \in \mathbb{R}^{d_v\times d_k}, \qquad \vo_{[t]}^r = \rmS_{[t]}^r\vq_{[t]}^r = \rmS_{[t]}\vq_{[t]}^r + \sum_{i=1}^r \vv_{[t]}^{i} \left(\vk_{[t]}^{i\intercal} \vq_{[t]}^{r} \right) \in \mathbb{R}^{d_v}
$$

$$
\rmS_{[t+1]} = \rmS_{[t]} + \rmV_{[t]} \rmK_{[t]}^\intercal \in \mathbb{R}^{d_v \times d_k}, \qquad \rmO_{[t]} = \rmQ_{[t]} \rmS_{[t]}^\intercal + \left(\rmQ_{[t]}\rmK_{[t]}^\intercal \odot \rmM\right) \rmV_{[t]} \in \mathbb{R}^{C \times d_v}
$$

$$
\rmS_{[t+1]} = {\color{blue} \overrightarrow{\rmS_{[t]}}} + \rmV_{[t]}^\intercal {\color{blue} \overrightarrow{\rmK_{[t]}}} \in \mathbb{R}^{d_v \times d_k} , && \rmO_{[t]} = {\color{blue}{\overleftarrow{ \rmQ_{[t]}}}} \rmS_{[t]}^\intercal + \left(\rmQ_{[t]} \rmK_{[t]}^\intercal \odot {\color{blue}\Gamma_{[t]}}\right)\rmV_{[t]} \in \mathbb{R}^{C\times d_v}
$$

$$
{\color{blue}\overleftarrow{\vq_{[t]}^r}} &= {\color{blue}\gamma_{[t]}^r} \vq_{[t]}^r && \text{decaying each vector to the first position of chunk $t$} \nonumber \\ {\color{blue}\overrightarrow{\vk_{[t]}^r}} &= {\color{blue}\frac{\gamma_{[t ]}^{C}}{\gamma_{[t]}^r}} \vk_{[t]}^r && \text{decaying each vector to the last position of chunk $t$} \nonumber \\ {\color{blue}\overrightarrow{\rmS_{[t]}}} &= {\color{blue}\gamma_{[t]}^C}\rmS_{[t]} && \text{decaying the state matrix over the entire chunk $t$}
$$

$$
\rmS_t &= \rmS_{t-1} - \underbrace{\left(\rmS_{t-1} \vk_t\right)}_{\vv_{t}^{\text{old}}} \vk_t^\intercal + \underbrace{\left(\beta_t \vv_t + (1-\beta_t)\rmS_{t-1}\vk_t)\right)}_{\vv_{t}^{\text{new}}} \vk_t^\intercal = \rmS_{t-1} \left(\rmI - \beta_t \vk_t \vk_t^\intercal \right) + \beta_t \vv_t \vk_t^\intercal
$$

$$
\rmS_{[t]}^r = \rmS_{[t]} \underbrace{\left(\prod_{i=1}^r \rmI - \beta_{[t]}^i \vk_{[t]}^i \vk_{[t]}^{i\intercal} \right)}_{:= \rmP_{[t]}^r} + \underbrace{\sum_{i=1}^{r} \left( \beta^i_{[t]} \vv^i_{[t]} \vk_{[t]}^{i\intercal}\prod_{j=i+1}^{r} \left(\rmI - \beta_{[t]}^j \vk^j_{[t]} \vk_{[t]}^{j\intercal} \right) \right)}_{:= \rmH_{[t]}^r}
$$

$$
\rmP_{[t]}^{r} &= \rmI - \sum_{i=1}^{r}\vw_{[t]}^i\vk_{[t]}^{i\intercal} \in \mathbb{R}^{d_k \times d_k} &&\vw_{[t]}^r = \beta_{[t]}^r \left(\vk_{[t]}^r - \sum_{i=1}^{r-1} \left(\vw_{[t]}^i (\vk_{[t]}^{i\intercal}\vk_{[t]}^r) \right) \right) \in \mathbb{R}^{d_k}
$$

$$
\rmH_{[t]}^{r} &= \sum_{i=1}^{r} \vu_{[t]}^i \vk_{[t]}^{i\intercal} \in \R^{d_v \times d_k} && \vu_{[t]}^r = \beta_{[t]}^r \left(\vv_{[t]}^r - \sum_{i=1}^{r-1} \left(\vu_{[t]}^i (\vk_{[t]}^{i\intercal}\vk_{[t]}^r) \right) \right)\in \mathbb{R}^{d_v}
$$

$$
\rmT_{[t]} = \left[\rmI + \operatorname{strictLower}\left(\operatorname{diag}(\beta_{[t]})\rmK_{[t]} \rmK_{[t]}^\intercal\right)\right]^{-1}\operatorname{diag}\left(\beta_{[t]}\right) \in \mathbb{R}^{C \times C} \\ \rmW_{[t]}= \rmT_{[t]} \rmK_{[t]} \in \mathbb{R}^{C \times d_k}, \qquad \rmU_{[t]}=\rmT_{[t]}\rmV_{[t]} \in \mathbb{R}^{C \times d_v}
$$

$$
\rmS_{[t+1]} &= \rmS_{[t]}\rmP_{[t]}+\rmH_{[t]} = \rmS_{[t]} + \left(\rmU_{[t]} - \rmW_{[t]}\rmS_{[t]}^{\intercal}\right)^\intercal \rmK_{[t]} & \in \mathbb{R}^{d_v \times d_k} \\ \rmO_{[t]} &= \rmQ_{[t]} \rmS_{[t]}^\intercal + (\rmQ_{[t]} \rmK_{[t]}^{\intercal} \odot \rmM) \left(\rmU_{[t]} - \rmW_{[t]} \rmS_{[t]}^\intercal\right) &\in \mathbb{R}^{C \times d_v}
$$

$$
\rmS_t = \rmS_{t-1} \left( {\color{blue}{\alpha_t}} (\rmI - \beta_t \vk_t\vk_t^\intercal) \right) + \beta_t \vv_t \vk_t^\intercal
$$

$$
\rmS_{t+1} &= \rmS_{t} - \beta_t \nabla \mathcal{L}(\rmS_t) = \rmS_{t} - \beta_t (\rmS_t\vk_t - \vv_t)\vk_t^\intercal = \rmS_{t}\left(\rmI-\beta_t\vk_t\vk_t^\intercal\right) + \beta_t \vv_t\vk_t^\intercal
$$

$$
\rmS_{[t]}^r = \rmS_{[t]} \underbrace{\left(\prod_{i=1}^r {\color{blue}{\alpha_{[t]}^i}}\left(\rmI - \beta_{[t]}^i \vk_{[t]}^i \vk_{[t]}^{i\intercal} \right)\right)}_{:= \mathbf{F}_{[t]}^r} + \underbrace{\sum_{i=1}^{r} \left( \beta^i_{[t]} \vv^i_{[t]} \vk_{[t]}^{i\intercal}\prod_{j=i+1}^{r} {\color{blue}{\alpha_{[t]}^j}} \left(\rmI - \beta_{[t]}^j \vk^j_{[t]} \vk_{[t]}^{j\intercal} \right) \right)}_{:= \rmG_{[t]}^r}
$$

$$
\rmG_{[t]}^r = \sum_{i=1}^r {\color{blue} \frac{\gamma_{[t]}^r}{\gamma_{[t]}^i} } \tilde{\vu}_{[t]}^i \vk_{[t]}^{i\intercal} \in\mathbb{R}^{d_v \times d_k} &&\tilde{\vu}_{[t]}^r = \beta_{[t]}^r \left(\vv_{[t]}^r - \sum_{i=1}^{r-1} \left( \tilde{\vu}_{[t]}^i ({\color{blue}\frac{\gamma_{[t]}^{r}}{\gamma_{[t]}^i}} \vk_{[t]}^{i\intercal}\vk_{[t]}^r)\right)\right) \in \mathbb{R}^{d_v}
$$

$$
\widetilde{\rmU_{[t]}} = \left[\rmI + \operatorname{strictLower} \left(\operatorname{diag}\left(\beta_{[t]}\right) ({\color{blue}\Gamma_{[t]} } \odot \rmK_{[t]} \rmK_{[t]}^\intercal )\right) \right]^{-1} \operatorname{diag}\left(\beta_{[t]}\right) \rmV_{[t]} && \in \mathbb{R}^{C \times d_v}
$$

$$
\rmS_{[t+1]} &= {\color{blue} \overrightarrow{\rmS_{[t]}}} + \left({ \widetilde{\rmU_{[t]}}} - {\color{blue} \overleftarrow{\rmW_{[t]}}} \rmS_{[t]}^\intercal\right)^\intercal {\color{blue} \overrightarrow{\rmK_{[t]}}} &&\in \mathbb{R}^{d_v \times d_k} \\ \rmO_{[t]} &= {\color{blue} \overleftarrow{\rmQ_{[t]}}} \rmS_{[t]}^\intercal + (\rmQ_{[t]} \rmK_{[t]}^{\intercal} \odot \mathbf{M}) \left({{\widetilde{\rmU^{}_{[t]}}}} - {\color{blue} \overleftarrow{\rmW_{[t]}}}\rmS_{[t]}^\intercal\right) &&\in \mathbb{R}^{C \times d_v}
$$

$$
\rmS_t = \sum_{i=1}^t {\color{blue}\frac{\gamma_{t}}{\gamma_i}} \vu_i \vk_i^\intercal, \qquad \vu_t = \beta_t \left( \vv_t - \sum_{i=1}^{t-1} {\color{blue} \frac{\gamma_{t}}{\gamma_i}} \vu_i \vk_i^T \vk_t \right)
$$

$$
\rmS_t = {\color{blue}\alpha_t} \rmS_{t-1} + \vv_t \vk_t^\intercal, \qquad \vo_t = \rmS_t \vq_t
$$

## 相关论文

- [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] — From ATOP to ZCube: Automated Topology Optimization Pipeline and A Highly Cost-Effective Network Topology for Large Model Training
- [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] — Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM

## 全文文本
全文已存 `extraction/fulltext/gated-delta-networks-improving-mamba2-with-delta-rule.txt`（79000 字符）供引用检索。