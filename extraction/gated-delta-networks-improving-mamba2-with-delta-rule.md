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
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-fig01.png]]
*整页渲染: ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p07.png]]*
> [!quote] caption
> Visualization of the (hybrid) architecture and block design of Gated DeltaNet models.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

1) 图分三块：左为Gated DeltaNet-H1架构（N×重复，每块含Gated DeltaNet+MLP→SWA+MLP共2子层）；中为H2混合架构（Mamba2+MLP→Gated DeltaNet+MLP→SWA+MLP共3子层）；右为Block设计，展示四条并行路径——q/k（Linear+Conv+SiLU+L2 norm）、v（Linear+Conv+SiLU）、α/β（Linear+SiLU）汇入Gated Delta Rule→Norm→Linear输出。

2) 论证结论：delta-rule线性注意力配合乘性门控α、β可显著增强联想召回；H1/H2通过交错DeltaNet、Mamba2(SSM)、SWA，实现选择性长程记忆+结构化递归+局部上下文三者的优势融合。

3) 在论文中地位：作为架构总图定义模型骨架，为后续WikiText ppl 16.42、zero-shot ppl 55.32及H2最优ppl 15.91等核心实验结果提供结构支撑。

### Figure 2 (p.8) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-fig02.png]]
*整页渲染: ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p08.png]]*
> [!quote] caption
> Length extrapolation on six long benchmarks.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图2图文联合解读**

该图以3×2网格展示6个长文本基准(GovReport、Qasper等)上、序列长度从4k扩展至20k时的性能曲线，纵轴为各任务指标。图例含四条线：Mamba1(橙)、DeltaNet(蓝)、GatedDeltaNet及另一变体(绿/棕)。

**关键观察**：在所有基准上，**Mamba1退化最严重**——如GovReport从~9.1降至~6.0，Qasper从~20降至~13；**DeltaNet(蓝)居中**，16k后也明显下滑；而**GatedDeltaNet系列(绿/棕)**曲线始终位于最下方簇，在20k处仍保持稳定。

**论证作用**：该实验用以证明——**门控(gating)与Delta规则的组合显著改善了Mamba2/DeltaNet基线的长度外推能力**，是验证"Gated DeltaNet"核心设计(在Delta规则上引入遗忘门)有效性的关键证据，呼应论文标题"improving Mamba2 with delta rule"的主旨。

### Figure 3 (p.9) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-fig03.png]]
*整页渲染: ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p09.png]]*
> [!quote] caption
> Training throughput comparison of 1.3B models on a single H100 GPU. standalone mixers: Samba outperforms Mamba, while Gated DeltaNet-H1 and -H2 outperform

> [!tip] 技术解读（多模态）
> 【图文联合解读】图3为折线图，横轴为序列长度×批大小组合（2K×16→16K×2），纵轴为训练吞吐（K tokens/s，~25–60）。展示8个1.3B模型在单卡H100上的表现：Transformer++（蓝线）随序列增长由~55急降至~27 K/s；而DeltaNet、Mamba1/2、Gated DeltaNet、Samba等线性注意力/Gated RNN基线保持平稳（~38–50 K/s）。

原文借此论证两点：(1) 独立混合器中Samba优于Mamba；(2) 所提Gated DeltaNet-H1与-H2吞吐超越Samba，证明Delta Rule+门控机制兼具高质量与高效率。

该图作用：与下游语言建模/下游任务质量指标形成互补，从算力成本维度佐证所提架构"质量–效率"双重优势，闭环论证其工程实用性。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-tab01.png]]
> [!quote] caption
> Comparison of different linear RNN models and their corresponding online learning objectives using the framework from Liu et al. ( 2024 ). For convenience, we simplify Longhorn’s vector-valued β to scalar β .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文联合解读**

该表用Liu(2024)在线学习框架，统一对比LA、Mamba2、Longhorn、DeltaNet与本文Gated DeltaNet五者的目标函数及状态更新规则。Gated DeltaNet目标为‖**S**_t−α_t**S**_{t-1}‖²_F−2⟨**S**_t**k**_t, β_t(**v**_t−α_t**S**_{t-1}**k**_t)⟩，对应更新为α_t(**I**−β_t**k**_t**k**_t^T)**S**_{t-1}+β_t**v**_t**k**_t^T。作者据此论证：Gated DeltaNet同时融合Mamba2的乘性遗忘门α_t与DeltaNet的delta-rule增量门β_t，是两者的自然统一体。在论文整体链路上，该表为Fig.1架构设计及H1/H2混合变体实验奠定"选择性遗忘+联想召回"的双重理论动机。

### Table 2 (p.5) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-tab02.png]]
> [!quote] caption
> Zero-shot performance comparison on S-NIAH benchmark suite for 1.3B models (see § 4 for setups)

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表2核心**：1.3B模型在S-NIAH三任务（pass-key、数字、UUID检索）零样本对比，序列长1K–8K。

**关键数据**：Gated DeltaNet在S-NIAH-1 8K达91.8（SOTA），Mamba2骤降至30.4；S-NIAH-2 4K为92.2，远超Mamba2的56.2；S-NIAH-3 4K为27.6 vs Mamba2的4.6，三项均最优。

**论证结论**：原文借表说明Mamba2采用负内积损失，长序列关联召回衰减严重；而delta rule优化在线回归‖S_t k_t − v_t‖²，可视为隐式SGD更新，故Gated DeltaNet在上下文关联回忆上显著优于Mamba2。

**论文作用**：作为消融对比的核心证据，支撑"门控+delta rule优于Mamba2"的核心方法论主张。

### Table 3 (p.7) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-tab03.png]]
> [!quote] caption
> Performance comparison on language modeling and zero-shot common-sense reasoning.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心数据：** Table 3 对比 10 个模型在 WikiText/LAMBADA 困惑度与 7 项零样本推理（PIQA、HellaSwag、WinoGrande、ARC-e/c、SIQA、BoolQ）上的表现。混合组中 Gated DeltaNet-H1 综合均值 56.40 最高，H2 次之 56.18；纯循环组内 Gated DeltaNet 以 55.32 居首，超过 Mamba2(54.89)、DeltaNet(52.14)、Mamba(53.12)；其 Wiki.ppl 16.42、LMB.ppl 12.17 均为该组最低。

**2) 关键结论：** 门控机制叠加 delta 更新规则相对 DeltaNet/Mamba2 实现全指标提升，验证方法有效性；H1/H2 混合架构同时超越 Transformer++(52.25) 与 Samba(54.00)，确立其作为新一代基础架构的竞争力。

**3) 论文作用：** 与 Figure 3 的吞吐量曲线互补，形成"质量–效率"双维度论证，支撑 Gated DeltaNet 的核心主张。

### Table 4 (p.7) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-tab04.png]]
> [!quote] caption
> Accuracy on recall-world retrieval tasks with input truncated to 2K tokens. SQD: SQUADE. TQA: Trivial QA.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表4展示2K长度检索任务（SWDE/SQD/FDA/TQA/NQ/Drop/Avg）上各模型准确率。纯循环模型中Gated DeltaNet平均30.6，优于Mamba2（29.8）、DeltaNet（26.2），SWDE提升至25.4；混合模型中Gated DeltaNet-H2平均40.1，超越Transformer++（37.0）与Samba（37.3），SWDE/SQD/TQA分别达38.2/40.4/63.3。该表作为关键实验证据，验证门控+Delta规则结合显著增强模型的检索/记忆能力，是论文"改进Mamba2"主张的核心实证支撑。

### Table 5 (p.9) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-tab05.png]]
> [!quote] caption
> Accuracy on 14 tasks from LongBench ( Bai et al. , 2023 ): Narrative QA, QasperQA, MultiField QA, HotpotQA, 2WikiMulti QA, Musique, GovReport, QMSum, MultiNews, TRec, Trivia QA, SamSum, LCC, and RepoBench-P by order.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 图文联合解读**

该表对比了Gated DeltaNet及混合变体（H1/H2）与8个基线（RetNet、HGRN2、Mamba、DeltaNet、Mamba2、Transformer++、Samba等）在LongBench 14个长上下文任务上的精度。在纯循环模型组，Gated DeltaNet平均分达16.6，明显高于Mamba2(13.5)与DeltaNet(13.6)；在混合模型组，H2版本以18.4的平均分大幅超越Samba(15.9)与Transformer++(11.0)，并在MultiNews(40.5)、SamSum(27.9)、MultiField QA(27.1)等任务上取得全表最高分。该表作为长文本评估的核心证据，验证了"门控机制+Delta规则"对Mamba2长上下文理解能力的实质性提升，并证明将门控Delta模块嵌入混合架构可进一步放大优势，支撑论文的核心方法论主张。

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

## 技术点深读（DEEP）

![[deep/gated-delta-networks-improving-mamba2-with-delta-rule]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/gated-delta-networks-improving-mamba2-with-delta-rule.txt`（79000 字符）供引用检索。