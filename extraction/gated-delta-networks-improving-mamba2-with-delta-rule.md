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
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与数据：** 图2为6子图矩阵，依次展示GovReport、QMSum、NarrativeQA、Qasper、CodeParrot、PG19六个长文本基准上Perplexity随序列长度（4k→20k）变化的曲线；纵轴量化范围因任务不同（如QMSum约12–18、CodeParrot约5–20）；横轴对数刻度。每条曲线对应7个模型：Mamba1、Mamba2、DeltaNet、Samba、GatedDeltaNet及其两个消融变体H1、H2。

**2) 关键结论：** 论文用以论证Delta-rule更新与门控机制结合后，模型在训练窗口外（>4k）能稳定保持低困惑度。定量看，六个基准上GatedDeltaNet-H2（红橙）始终处于最低带（如QMSum≈13、CodeParrot≈6），且随长度几乎不恶化；而Mamba1（橙）在多数基准（如CodeParrot ≈15–18）最高，Mamba2（紫）在NarrativeQA（≈18–20）次差。H2较H1的差距说明门控策略的具体设计对长度外推有关键影响。

**3) 论文作用：** 此图与Table 2互补——后者证明检索式任务（短上下文）上的优势，本图则补齐长上下文外推维度，共同支撑"Gated DeltaNet全面优于Mamba2/DeltaNet"的核心结论，构成方法链路中泛化性证据的关键一环。

### Figure 3 (p.9) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-fig03.png]]
*整页渲染: ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p09.png]]*
> [!quote] caption
> Training throughput comparison of 1.3B models on a single H100 GPU. standalone mixers: Samba outperforms Mamba, while Gated DeltaNet-H1 and -H2 outperform

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1）图示对象与数据**：1.3B模型在单卡H100上的训练吞吐（Kt/s），横轴为"序列长度×batch size"四档（2K×16 → 16K×2）。共8条曲线：Gated DeltaNet-H1全程最高（≈55→52.5，几乎平稳）；H2稳定≈49–50；Mamba2≈48；DeltaNet/Gated DeltaNet≈45–46；Samba 45→43微降；Mamba1最低≈38；Transformer++从55断崖式跌至≈26.5。

**2）原文结论**：standalone mixer层面Samba＞Mamba，Gated DeltaNet-H1/H2＞Mamba2；线性注意力类架构吞吐对序列长度鲁棒，Transformer++则严重退化，验证门控+delta rule对Mamba2的硬件效率增益。

**3）论文作用**：与Table 3精度互补，从效率侧论证"又快又好"；是支撑Gated DeltaNet价值主张的关键工程证据。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-tab01.png]]
> [!quote] caption
> Comparison of different linear RNN models and their corresponding online learning objectives using the framework from Liu et al. ( 2024 ). For convenience, we simplify Longhorn’s vector-valued β to scalar β .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表1解读**

**核心对象与结构**：表1沿Liu et al. (2024)在线学习框架，分"方法/在线目标/递推更新"三列，对比5种线性RNN——LA、Mamba2、Longhorn、DeltaNet、Gated DeltaNet。其中LA无任何门控或delta修正；Mamba2仅引入遗忘门α_t（如‖S_t-α_t S_{t-1}‖²_F项）；Longhorn与DeltaNet分别以标量化β_t实现delta修正的近似与精确形式；Gated DeltaNet的目标函数同时含α_t遗忘项与β_t delta修正项，递推式为S_t=S_{t-1}(α_t(I-β_t k_t k_t^T))+β_t v_t k_t^T，最为完整。

**关键技术结论**：Gated DeltaNet不是临时拼接，而是Mamba2门控机制与DeltaNet delta规则的形式统一与严格推广，二者缺一不可。

**论文链路作用**：该表为图1的混合架构与block设计提供理论锚点，证明所提方法为两线演进的自然融合终点，支撑后续消融与基准实验的合理性。

### Table 2 (p.5) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-tab02.png]]
> [!quote] caption
> Zero-shot performance comparison on S-NIAH benchmark suite for 1.3B models (see § 4 for setups)

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 解读**

该表对比 1.3B 规模的 DeltaNet、Mamba2、Gated DeltaNet 在 S-NIAH 三类检索任务（pass-key、数字、UUID）上、1K–8K 上下文长度下的零样本表现。Gated DeltaNet 全面领先：S-NIAH-2 在 4K 达 92.2（Mamba2 仅 56.2、DeltaNet 18.6），S-NIAH-3 的 4K 为 27.6（vs Mamba2 4.6）。

论文借此论证关键结论：Mamba2 采用的简单内积损失难以建模键值关联，而 Delta 规则以在线回归 ‖Sₜkₜ−vₜ‖² 优化快权重（等价于测试时 SGD），因此门控 Delta 规则在上下文联想回忆能力上显著优于 Mamba2，为 Gated DeltaNet 架构的核心动机与设计选择提供关键实验依据。

### Table 3 (p.7) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-tab03.png]]
> [!quote] caption
> Performance comparison on language modeling and zero-shot common-sense reasoning.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 3 展示 10 个模型在 Wiki/LMB 困惑度及 8 项零样本推理任务的表现，分**纯循环**与**注意力/混合**两组。

**核心数据**：纯循环组中，Gated DeltaNet 以 Wiki ppl **16.42**、LMB ppl **12.17**、Avg **55.32** 全面优于 Mamba2(54.89) 与 DeltaNet(52.14)；混合组中，Gated DeltaNet-H1 取得 Avg **56.40**（榜首），H2 的 Wiki ppl **15.91** 为全表最低，均超越 Samba(54.00)。

**论证结论**：门控+Δ规则同时改进 Mamba2 与 DeltaNet；将门控、Δ 规则与注意力结合的混合架构（Gated DeltaNet-H1/H2）达 SOTA。

**作用**：作为论文主实验核心表，从**建模效率**（ppl）与**应用能力**（下游推理）双维度验证所提方法的先进性与泛化性。

### Table 4 (p.7) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-tab04.png]]
> [!quote] caption
> Accuracy on recall-world retrieval tasks with input truncated to 2K tokens. SQD: SQUADE. TQA: Trivial QA.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表对比9个模型在6项检索/QA任务（输入截断至2K）上的准确率。

**核心数据**：循环模型组中，Gated DeltaNet平均30.6为最高，较Mamba2(29.8)、DeltaNet(26.2)分别+0.8和+4.4，并在SWDE(25.4)、SQD(34.8)、Drop(19.8)三项居首；混合架构Gated DeltaNet-H2以平均40.1全面超越Transformer++(37.0)与Samba(37.3)。

**技术结论**：门控机制叠加Delta规则相对Mamba2的真实检索能力具有稳定改进；混合少量注意力层后，Gated DeltaNet即可超过全注意力Samba基线。

**论文作用**：聚焦"召回/检索"这一长上下文核心痛点，是验证Gated DeltaNet相对Mamba2/DeltaNet优势、并支撑混合方案SOTA主张的关键实验证据。

### Table 5 (p.9) ⭐深度解读
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-tab05.png]]
> [!quote] caption
> Accuracy on 14 tasks from LongBench ( Bai et al. , 2023 ): Narrative QA, QasperQA, MultiField QA, HotpotQA, 2WikiMulti QA, Musique, GovReport, QMSum, MultiNews, TRec, Trivia QA, SamSum, LCC, and RepoBench-P by order.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表对比9个模型在LongBench 14项任务上的准确率，分为循环模型（RetNet/HGRN2/Mamba/DeltaNet/Mamba2/Gated DeltaNet）与注意力或混合模型（Transformer++/Samba/Gated DeltaNet-H1/H2）。数据显示：Gated DeltaNet平均16.6，超越Mamba2（13.5）与DeltaNet（13.6）；混合变体Gated DeltaNet-H2平均18.4，显著优于Samba（15.9），并在TRec（40.5 vs 22.7）、MultiNews（13.0 vs 11.0）等任务上大幅领先。

论文借此论证：门控机制+Delta规则在长上下文理解基准上同时优于纯Mamba2基线和DeltaNet，门控-Delta架构相较Samba等混合架构亦具优势，从而支撑其作为新一代高效长序列模型的核心主张，是论文实验链路中证明方法有效性的关键实证。

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