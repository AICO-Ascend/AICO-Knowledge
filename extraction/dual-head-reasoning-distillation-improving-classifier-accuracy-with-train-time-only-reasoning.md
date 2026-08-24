---
paper_num: "28"
title: "Dual-Head Reasoning Distillation: Improving Classifier Accuracy with Train-Time-Only Reasoning"
authors: "Classifier Accuracy with Train-Time-Only Reasoning Jillian Xu∗ University of Waterloo j23xu@uwaterloo.ca Dylan Zhou Google dylanzhou@google.com Vinay Shukla Google vinayshukla@google.com Yang Yang Google lizyang@google.c"
date: "2026/1/19"
arxiv: "https://arxiv.org/abs/2509.21487"
pdf: "papers/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning.pdf"
slug: "dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning"
tags: []
---

# Dual-Head Reasoning Distillation: Improving Classifier Accuracy with Train-Time-Only Reasoning

> [!abstract] 摘要（原文）
> 1\. 💡 Dual-Head Reasoning Distillation (DHRD) 提出了一种训练时推理 (train-time reasoning) 的新方法，通过在训练时使用推理头 (reasoning head) 和教师推理 (teacher rationales) 来提升分类准确率，同时避免了推理时的吞吐量 (throughput) 惩罚。 2. 🛠️ 该方法对 decoder-only LM 施加了一个加权联合目标，该目标结合了标签交叉熵 (label cross-entropy) 和 token 级别的 LM loss，用于在包含原始输入和教师（如 Gemini 2.5 Flash）生成推理的序列上进行训练。 3. 📈 在七项 SuperGLUE 任务上，DHRD 比 pooled baselines 提高了 0.65–5.47% 的准确率，尤其在 entailment/causal tasks 上增益显著，且推理时由于不生成推理，其 QPS 比 CoT decoding 快 96–142 倍。

## 元信息
- **发表日期**: 2026/1/19
- **作者**: Classifier Accuracy with Train-Time-Only Reasoning Jillian Xu∗ University of Waterloo j23xu@uwaterloo.ca Dylan Zhou Google dylanzhou@google.com Vinay Shukla Google vinayshukla@google.com Yang Yang Google lizyang@google.c
- **arXiv**: https://arxiv.org/abs/2509.21487
- **本地 PDF**: `papers/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning.pdf`
- **页数**: 12

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-fig01.png]]
*整页渲染: ![[assets/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-p02.png]]*
> [!quote] caption
> SuperGLUE per-task scores for four backbones. DHRD (train-time reasoning) consistently beats the pooled-classifier baseline and rivals teacher model Gemini 2.5 Flash, with the largest gains on CB/COPA/RTE. ‘Avg’ is the macro-average, tabulated results can be found in Table 1. improvements are attributable to alignment of input–rationale–label triplets rather than to generic LM regularization; inte

> [!tip] 技术解读（多模态）
> 【图文联合解读】**【图示内容】** 图以两张雷达图分别展示 Llama-3.2-3B+BoolQ 与 Qwen-3-4B+BoolQ 两个主干在 SuperGLUE 八项任务（CB/COPA/MultiRC/RTE/WiC/WSC/BoolQ/Avg）上 Teacher（CoT Zero-shot，紫点线）、Baseline（pooled classifier，蓝虚线）与 DHRD（红实线）的得分。DHRD 几乎完全包络 Baseline，在 CB（≈89 vs 78）、COPA（≈79 vs 75）、RTE（≈92 vs 91）等低资源推理任务上提升最显著，Avg 也略优，整体逼近 Teacher 曲线。

**【技术结论】** 原文据此论证：DHRD 仅在训练阶段引入 CoT 推理，跨主干稳健提升分类头精度；增益源于"输入–理由–标签"三元组对齐，而非通用 LM 正则化。

**【整体作用】** 作为开篇概览图，定量支撑"训练时推理可替代测试时推理"的核心主张，为后续 Table 1 与消融实验铺垫。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-fig02.png]]
*整页渲染: ![[assets/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-p03.png]]*
> [!quote] caption
> Dual-head fine-tuning on a shared decoder. The classification head pools hidden states over the input span (blue) to produce K class logits. The train-only reasoning head applies a causal LM loss over the full sequence, covering both classification input tokens (blue) and teacher rationale tokens (orange). During training, inputs concatenate task text with teacher rationales. At inference, only th

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示共享解码器上的双头架构：①**分类头**对蓝色输入token（L_cls个，D维嵌入ℝ^(L_cls×D)）池化输出K类logits；②**推理头**通过LM Head对全序列（蓝色分类token+橙色教师推理token，共L_cls+L_rat个，ℝ^((L_cls+L_rat)×D)）施加因果LM损失。原文据此论证：推理头仅在训练时借助教师思维链做辅助蒸馏，推理阶段完全弃用，使分类器零开销吸收推理知识。该图是论文DHRD方法的**核心架构图**，支撑"训练时推理、推理时仅分类"的整体链路设计，是其相对传统CoT蒸馏的关键创新点。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.4) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-tab01.png]]
> [!quote] caption
> SuperGLUE results (higher is better). Rel. ∆ (%) is the relative percentage change versus the pooled baseline for the same backbone ( α =0 , β =1 ). All DHRD rows use the optimal weights selected on the validation split: α = β =1 for Llama-3.1-8B, Llama-3.2-3B, and Qwen-3-8B; α =0 . 5 , β =1 for Qwe

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

表1给出4个backbone在SuperGLUE 8任务及Avg上的Baseline vs DHRD量化对比，含教师模型Gemini 2.5 Flash作参照：Llama-3.1-8B Avg 86.29→87.52(+1.43%)、Qwen-3-8B 86.09→87.23(+1.32%)、Llama-3.2-3B 77.34→81.57(+5.47%)、Qwen-3-4B 84.50→85.05(+0.65%)；最优权重α=β=1（Qwen-3-4B例外为α=0.5）。

论文借此论证：仅训练时推理蒸馏的DHRD在4个不同规模/架构的backbone上均稳定超越pooled分类器基线，Avg已达或逼平Gemini 2.5 Flash教师，且CB/COPA/RTE小任务提升最显著——表明增益来自输入-推理-标签三元组对齐，而非通用LM正则化。

该表与Figure 1互补，前者提供逐任务精确数值，后者展示条形直观对比，共同构成DHRD方法主实验的核心证据链，支撑"推理蒸馏优于pooled分类器"的核心结论。

### Table 2 (p.4) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-tab02.png]]
> [!quote] caption
> Ablations on rationale/label alignment (SuperGLUE). ConsistentReasoningLabel (aligned <REASON> and <ANS> ), OnlyLabel (aligned <ANS> ), ShuffleReasoning (misaligned <REASON> ,

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 联合解读：**

**核心对象与数据**：表格对比 Llama-3.1-8B / 3.2-3B 在 SuperGLUE 7 个任务上 4 种对齐设置的平均准确率。ConsistentReasoningLabel 最佳（87.52 / 81.57）；OnlyLabel 略降（-1.75% / -3.84%）；ShuffleReasoning（仅打乱理由文本）下降显著（-5.70% / -20.24%）；ShuffleReasoningLabel（理由与标签均错配）出现灾难性坍塌（-48.48% / -45.27%，如 MultiRC 降至 0.0）。

**关键技术结论**：理由内容与其标签对齐必须同时成立，模型才真正从教师推理中获益；缺少理由或破坏对齐都会损害性能，证明推理头并非学到了"理由→标签"的捷径，而是依赖连贯的语义关联。

**在论文中的作用**：该消融为 Figure 2 双头架构的合理性提供因果证据——train-only 推理头确实需要真实、对齐的教师推理作为监督，方法不能被简化为正则化技巧，是支撑主结论的核心实验之一。

### Table 3 (p.9) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-tab03.png]]
> [!quote] caption
> SuperGLUE results (higher is better). Rel. ∆ (%) is the relative percentage change compared to each model’s pooled baseline ( α =0 , β =1 ). Reasoning / CoT fine-tuned models follows ( α =1 , β =0 ) with CoT at inference using the Reasoning Head (refer to Appendix E.6).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读**

该表呈现SuperGLUE 7项任务（BoolQ/CB/COPA/MultiRC/RTE/WiC/WSC）上4款模型（Llama-3.1-8B、Qwen3-8B、Llama-3.2-3B、Qwen3-4B）的DHRD方法对比，含Baseline与三种(α,β)组合的设置。

**关键数据**：Baseline均值为86.29/86.09/77.34/84.50；DHRD(β=1,α=1)最优达87.52(+1.43%)、87.23(+1.32%)、**81.57(+5.47%)**、-1.05%；纯推理推理(α=1,β=0)跌至71.65/78.14，远低于Baseline。

**技术结论**：推理仅在训练时使用、推理时退化为分类头，可稳定提升分类精度（小模型Llama-3.2-3B提升最显著+5.47%）；而强制推理输出反致大幅退化。

**论文作用**：作为主实验核心证据，验证"训练期推理蒸馏+双头推理"方法在标准分类基准上的有效性与普适性，支撑全文方法主张。

### Table 4 (p.10) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-tab04.png]]
> [!quote] caption
> SuperGLUE benchmark overview with task type, train, validation, and test dataset sizes

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表（Table 4）展示SuperGLUE基准的7项任务概览：BoolQ、CB、COPA、MultiRC、RTE、WiC、WSC，涵盖QA、NLI、WSD、Coref.四类任务，指标多为Accuracy或F1/F1-EM；训练规模悬殊（CB仅250，MultiRC达27243）。原文以此论证双头推理蒸馏方法在不同任务类型与数据规模下的泛化有效性，并与下方QPS对比实验（CoT vs 非CoT推理效率）衔接，共同构成方法在"精度—效率"双维度的实验验证链路。

### Table 5 (p.10) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-tab05.png]]
> [!quote] caption
> Throughput (queries per second, higher is better). Classification uses a pooled head at inference (no decoding). Reasoning uses CoT-style decoding (train-time only in DHRD). The rightmost column shows the speedup of our deployed path over CoT decoding on the same backbone.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

图中实际显示的是附录 D 的标题"QPS Results on same decoder backbones"及 Table 5 的 caption，**Table 5 主体（QPS 数据行）未在图中呈现**，仅可依据原文 caption 解读。

1) **核心对象**：Table 5 度量吞吐量（queries/sec，越高越好），对比同一 decoder backbone 下"分类头推理（pooled head，无解码）"与"CoT 解码"两条路径，末列为前者相对后者的加速比。

2) **关键结论**：DHRD 在部署时仅走 classification head，无需自回归生成，因此相较同 backbone 的 CoT 解码可获得显著推理加速——以推理成本换取训练期 reasoning 的精度增益。

3) **论文作用**：置于附录 D，与主表（精度）互补，构成"精度↑ + 推理吞吐↑"的双重论证，回应"CoT 推理贵"这一潜在质疑，强化 DHRD 实用价值。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\begin{aligned} s_i &= [\,x_i,\ \text{\texttt{<REASON>}},\ r_i,\ \text{\texttt{<ANS>}},\ y_i\,],\qquad L_i = |s_i|, \qquad L^{(x)}_i = |x_i|. \end{aligned}
$$

$$
\mathcal{L}_{\mathrm{cls}} = -\frac{1}{B}\sum_{i=1}^B \Big( \mathbf{z}_i[y_i] - \log\!\sum_{k=1}^K e^{\mathbf{z}_i[k]} \Big).
$$

$$
\mathcal{L}_{\mathrm{reason}} = -\,\frac{1}{N}\sum_{i=1}^{B}\sum_{t=1}^{L_i-1} m_{i,t+1}\, \log\!\left( \frac{\exp\{\ell_{i,t}[\,v_{i,t+1}\,]\}} {\sum_{w=1}^{V}\exp\{\ell_{i,t}[w]\}} \right), \qquad N=\sum_{i=1}^{B}\sum_{t=1}^{L_i-1} m_{i,t+1}.
$$

$$
\mathcal{L}_{\mathrm{total}} = \beta\,\mathcal{L}_{\mathrm{cls}} + \alpha\,\mathcal{L}_{\mathrm{reason}}, \quad \alpha,\beta \ge 0.
$$

## 技术点深读（DEEP）

![[deep/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning.txt`（40047 字符）供引用检索。