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
> 【图文联合解读】图示4个雷达图（Llama-3.1-8B/3.2-3B、Qwen-3-8B/4B），每图8轴对应BoolQ/CB/COPA/MultiRC/RTE/WiC/WSC/Avg任务，对比DHRD（红实线）、Gemini 2.5 Flash CoT（紫点线）、Pooled Baseline（蓝虚线）。DHRD在CB（93-100）、COPA、RTE等小样本任务上增益最显著，Avg分（如Qwen-3-8B 87、Llama-3.2-3B 95）逼近甚至持平Gemini教师，全面超Baseline。

**技术结论**：训练时双头推理蒸馏对齐"输入-理由-标签"三元组，无需测试时CoT即可获得教师级精度。

**论文作用**：开篇概览图，定量支撑"训练时推理替代测试时推理"的核心主张，为Table 1与消融实验铺垫。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-fig02.png]]
*整页渲染: ![[assets/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-p03.png]]*
> [!quote] caption
> Dual-head fine-tuning on a shared decoder. The classification head pools hidden states over the input span (blue) to produce K class logits. The train-only reasoning head applies a causal LM loss over the full sequence, covering both classification input tokens (blue) and teacher rationale tokens (orange). During training, inputs concatenate task text with teacher rationales. At inference, only th

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示了论文核心架构——共享解码器上的双头微调设计。左侧：输入 tokens（ℝᴸ）经 Decoder-only 模型生成 Embedding Tokens（ℝᴸˣᴰ），分为两路：(1) **分类头**对蓝色输入跨度 pooling（ℝᴾˣᴰ）后经 MLP 输出 K 维分类 logits；(2) **推理头**（仅训练用）通过 LM Head 对完整序列做因果 LM 损失，输出 ℝᴸˣⱽ logits。右侧细化训练输入：蓝色分类嵌入（ℝᴸᶜˡˢˣᴰ）与橙色教师推理嵌入拼接成 ℝ⁽ᴸᶜˡˢ⁺ᴸʳˢ⁾ˣᴰ，LM Head 在其上做生成式对齐。

原文借此论证：推理蒸馏仅作用于训练阶段，推理时丢弃 LM Head，因此"白嫖"教师推理能力而不增加推理开销。该图是方法论基石，直接支撑表 2 关于 <REASON>/<ANS> 对齐消融的前提——若双头架构无法在共享表征中同时承载分类与生成信号，后续对齐实验无从谈起。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.4) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-tab01.png]]
> [!quote] caption
> SuperGLUE results (higher is better). Rel. ∆ (%) is the relative percentage change versus the pooled baseline for the same backbone ( α =0 , β =1 ). All DHRD rows use the optimal weights selected on the validation split: α = β =1 for Llama-3.1-8B, Llama-3.2-3B, and Qwen-3-8B; α =0 . 5 , β =1 for Qwe

> [!tip] 表格解读（多模态）
> 【图文联合解读】1) 该表展示四个骨干（Llama-3.1-8B/Qwen-3-8B/Llama-3.2-3B/Qwen-3-4B）在 SuperGLUE 七任务（BoolQ/CB/COPA/MultiRC/RTE/WiC/WSC）上 Baseline vs DHRD 逐项与平均分，并附教师 Gemini 2.5 Flash（Avg 86.40）作参。DHRD 平均 87.52/87.23/81.57/85.05 全面超越基线 86.29/86.09/77.34/84.50，Rel. Δ 为 +1.43/+1.32/+5.47/+0.65%。

2) 论证结论：DHRD 跨骨干稳定优于 pooled 分类器；8B 模型 DHRD（87.52/87.23）反超教师 Gemini（86.40），证明"训练时推理"可替代"测试时 CoT"；小模型 Llama-3.2-3B 增益最大（+5.47%），对弱基座更友好。

3) 整体作用：与 Figure 1 互证，定量锚定"训练时推理等价于测试时推理"的核心主张；其 α/β 最优选择（8B 取 1/1，Qwen-3-4B 取 0.5/1）为附录 B 消融提供基线，验证方法的跨规模可迁移性。

### Table 2 (p.4) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-tab02.png]]
> [!quote] caption
> Ablations on rationale/label alignment (SuperGLUE). ConsistentReasoningLabel (aligned <REASON> and <ANS> ), OnlyLabel (aligned <ANS> ), ShuffleReasoning (misaligned <REASON> ,

> [!tip] 表格解读（多模态）
> 【图文联合解读】**【核心对象与量化结构】** Table 2在SuperGLUE 7任务（BoolQ/CB/COPA/MultiRC/RTE/WiC/WSC）上对比Llama-3.1-8B与3.2-3B在α=β=1下四种理据-标签对齐设置的均值：ConsistentReasoningLabel（双对齐）最高87.52/81.57；OnlyLabel降为85.99（-1.75%）/78.44（-3.84%）；ShuffleReasoning降为82.54（-5.70%）/65.06（-20.24%）；ShuffleReasoningLabel双错位崩塌至45.09（-48.48%）/44.64（-45.27%）。

**【关键技术结论】** 理据-答案必须严格语义一致：一旦打乱REASON与ANS对应关系，即便ANS仍对齐，性能即大幅下滑，证明教师理据提供了与监督标签耦合的"推理路径监督"，双对齐是DHRD蒸馏生效的必要前提。

**【方法链作用】** 作为Figure 2双头架构的关键消融，配合主实验共同支撑"训练时引入对齐理据提升分类精度"的核心论点，排除"仅LM loss就够"的简化解释。

### Table 3 (p.9) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-tab03.png]]
> [!quote] caption
> SuperGLUE results (higher is better). Rel. ∆ (%) is the relative percentage change compared to each model’s pooled baseline ( α =0 , β =1 ). Reasoning / CoT fine-tuned models follows ( α =1 , β =0 ) with CoT at inference using the Reasoning Head (refer to Appendix E.6).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读**

表3展示SuperGLUE 7个任务在Llama-3.1-8B、Qwen3-8B、Llama-3.2-3B、Qwen3-4B四模型上Baseline与DHRD三种(β,α)配置的逐任务得分、均值及相对基线提升率。

关键结论：① 纯CoT微调严重损伤小模型能力，Llama-3.1-8B均值由86.29跌至71.65，Qwen3-8B亦降至78.14；② DHRD(β=1, α=1)配置普遍最优，其中Llama-3.2-3B获最高+5.47%提升；③ 推理仅训练时启用、推理时使用Classification Head，可稳定超越pooled基线，验证"train-time-only reasoning"设计有效。

该表作为主实验核心结果，跨模型规模验证双头蒸馏的鲁棒性，并以小模型增益最显著支撑论文对弱基模型收益更强的核心主张。

### Table 4 (p.10) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-tab04.png]]
> [!quote] caption
> SuperGLUE benchmark overview with task type, train, validation, and test dataset sizes

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读**

1) **核心数据**：该表列出SuperGLUE 7项任务——BoolQ（QA，Acc，9427/3270/3245）、CB（NLI，F1/Acc，250/56/250）、COPA（QA，Acc，400/100/500）、MultiRC（QA，F1/EM，27243/4848/9693）、RTE（NLI，Acc，2490/277/3000）、WiC（WSD，Acc，5428/638/1400）、WSC（Coref.，Acc，554/104/146）。任务类型涵盖QA、NLI、WSD、Coref.四类；训练规模极不均衡，从CB的250到MultiRC的27243，相差逾百倍；指标多为Accuracy，仅CB用F1/Acc、MultiRC用F1/EM。

2) **技术结论**：原文据此说明双头推理蒸馏方法在**任务类型多样、数据规模跨度极大**的场景下均能稳定提升精度，验证其泛化性。

3) **链路作用**：该表与下文QPS对比实验（CoT vs 非CoT推理效率）前后衔接，共同构成方法在"**精度—效率**"双维度上的完整实验验证闭环。

### Table 5 (p.10) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-tab05.png]]
> [!quote] caption
> Throughput (queries per second, higher is better). Classification uses a pooled head at inference (no decoding). Reasoning uses CoT-style decoding (train-time only in DHRD). The rightmost column shows the speedup of our deployed path over CoT decoding on the same backbone.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图像无法辨认 Table 5 主体（QPS 数据行缺失），仅显示附录 D 标题与 caption，以下结合原文解读：**

1) **结构与对象**：Table 5 比较同一解码器 backbone 下两种推理路径的吞吐量（QPS，数值越高越好）——分类路径采用 pooled head 推理（无解码），推理路径采用 CoT 式解码（DHRD 中仅训练时使用），最右列为 DHRD 部署路径相对同 backbone CoT 解码的加速比。

2) **关键技术结论**：DHRD 在推理时省去 CoT 自回归解码，仅用 pooled head 分类即可获得显著 QPS 加速，论证了"训练时用 reasoning 蒸馏、部署时只跑分类"在速度上的实际收益。

3) **论文链路作用**：作为附录 D 的效率补充证据，与主文精度提升互补，回应"引入 reasoning 是否拖慢部署"的潜在质疑，强化 DHRD 兼顾精度与推理效率的核心卖点。

### Table 6 (p.12) ⭐深度解读
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-tab06.png]]
> [!quote] caption
> Third-party assets and licenses.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1. **核心对象与结构**：图像中并未呈现表格的具体行列内容，仅可见正文引述"Table 6 lists the assets and licenses"及表标题"Table 6: Third-party assets and licenses"，属于合规性声明型表格，用于罗列论文所使用的第三方数据集与预训练模型及其对应许可证信息。

2. **关键技术结论**：原文明确所有第三方资产均"在其原始条款下使用，且仅用于非商业研究"（non-commercial research），以声明形式约束使用边界，保障上游资源的合规性。

3. **论文链路中的作用**：该表不属于方法/实验链路的技术模块，而是置于附录或末尾的**法律合规声明**，与正文的 dual-head reasoning distillation 方法无算法层面关联，仅满足开源/学术发表中对第三方资源归属与许可的披露规范。

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