---
paper_num: "41"
title: "DeepSeek-V3 Technical Report"
authors: "DeepSeek-AI research@deepseek.com"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2412.19437"
pdf: "papers/deepseek-v3-technical-report.pdf"
slug: "deepseek-v3-technical-report"
tags: []
---

# DeepSeek-V3 Technical Report

> [!abstract] 摘要（原文）
> 1\. 🤖 DeepSeek-V3是一个拥有671B总参数和37B激活参数的强大MoE语言模型，其核心创新包括无辅助损失的负载均衡策略和Multi-Token Prediction训练目标。 2. 🚀 该模型通过高效的FP8混合精度训练框架和DualPipe算法，实现了近乎完全的计算-通信重叠，并以仅2.788M H800 GPU小时的经济成本完成了14.8T tokens的预训练。 3. 🏆 综合评估表明，DeepSeek-V3在知识、代码和数学等多个基准测试中超越了其他开源模型，并达到了与GPT-4o和Claude-3.5-Sonnet等领先闭源模型相当的性能。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: DeepSeek-AI research@deepseek.com
- **arXiv**: https://arxiv.org/abs/2412.19437
- **本地 PDF**: `papers/deepseek-v3-technical-report.pdf`
- **页数**: 53

## 图表（原文 caption + 页码）

### Figure 5 (p.12) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-fig05.png]]
*整页渲染: ![[assets/deepseek-v3-technical-report-p12.png]]*
> [!quote] caption
> It employs a bidirectional pipeline scheduling, which feeds micro-batches from both ends of the pipeline simultaneously and a significant portion of communications can be fully overlapped. This overlap also ensures that, as the model further scales up, as long as we maintain a constant computation-to-communication ratio, we can still employ fine-grained experts across nodes while achieving a near-

> [!tip] 技术解读（多模态）
> 【图文联合解读】# Figure 5 深度解读

**核心对象与结构**：图示展示 **8 个 PP（流水线并行）rank × 20 个 micro-batch** 的 DualPipe 双向调度时序。绿色方格代表正向（forward）计算，橙色代表通信（communication），蓝色代表反向（backward）计算，白色为空闲/bubble 时间。每个 PP rank 从两端同时接收 micro-batch，编号 2–9 的 micro-batch 对称分布于流水线两半，由黑色边框标注"通信-计算重叠"单元。

**论证的关键技术结论**：双向流水线使大部分通信（橙色）可被计算（绿色/蓝色）完全覆盖，显著压缩了传统单向流水线的 bubble 区；只要保持计算-通信比恒定，模型进一步扩展时仍可实现跨节点的 **细粒度专家并行（fine-grained EP）**，获得近零通信开销。

**在论文中的作用**：Figure 5 是 DeepSeek-V3 训练基础设施一节（p.12）的核心示意图，为 DualPipe 算法与跨节点 EP 协同设计提供可视化证据，支撑"大规模 MoE 训练近乎零开销"这一基础设施层面的关键声明。

### Figure 6 (p.15) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-fig06.png]]
*整页渲染: ![[assets/deepseek-v3-technical-report-p15.png]]*
> [!quote] caption
> Firstly, in order to accelerate model training, the majority of core computation kernels, i.e., GEMM operations, are implemented in FP8 precision. These GEMM operations accept FP8 tensors as inputs and produce outputs in BF16 or FP32. As depicted in Figure 6, all three GEMMs associated with the Linear operator, namely Fprop (forward pass), Dgrad (activation backward pass), and Wgrad (weight backwa

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图中所见聚焦 Wgrad（权重梯度）通路：FP8 输入先经 ⊗ 矩阵乘、再在 **FP32** 下 Σ 累加，产出 Weight Gradient (FP32)；该梯度与 Master Weight（由 Optimizer States 以"**To BF16 / To FP32**" 回写更新）共同进入优化器；同时 Input、Output Gradient 均标注"**To FP8**"用于 Dgrad 计算。原文借该图论证：尽管 Linear 的 Fprop / Dgrad / Wgrad 三类 GEMM 均以 FP8 加速以降低算力与显存，但权重梯度在 **FP32** 累加、主权重以 BF16/FP32 高精度维护，从而保证 FP8 训练下的数值稳定性。

该图是 DeepSeek-V3 **混合精度 FP8 训练框架** 的核心架构图，承接前文 tile-wise / block-wise 量化策略，为后续消融实验与训练成本下降提供方法学依据。

### Figure 10 (p.48) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-fig10.png]]
*整页渲染: ![[assets/deepseek-v3-technical-report-p48.png]]*
> [!quote] caption
> 48

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

该图展示 230B DeepSeek-V2 模型上 BF16 与 FP8 两种精度训练的 loss 曲线对比：横轴为已处理 token 数（0–~900B），纵轴为 loss（1.7–2.5），两条曲线全程几乎完全重合；右上角内嵌放大子图给出相对差 (FP8−BF16)/BF16 随训练步数的变化，振荡区间约在 ±0.5% 内。

原文借此论证：所提出的 FP8 混合精度框架（细粒度量化、累加精度保持等）可在不引入额外 spike 的前提下，逼近 BF16 基线的收敛行为，从而支撑"全程 FP8 训练无损"的核心结论。

在论文整体链路中，该图位于方法章节末尾，作为对底层训练基础设施（low-precision training framework）正确性的关键实证依据，为后续 V3 全栈 FP8 大规模预训练（14.8T tokens）的可行性提供直接经验支撑。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab01.png]]
> [!quote] caption
> | Training costs of DeepSeek-V3, assuming the rental price of H800 is $2 per GPU hour.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图表解读：**

该表按训练阶段拆分 DeepSeek-V3 的算力成本：预训练 2664K H800 GPU·h（约 $5.328M），上下文扩展 119K h（$0.238M），后训练 5K h（$0.01M），合计 2788K h、约 $5.576M。预训练占 ~95.6%，后训练仅 ~0.2%，结构极不均衡。

**论证的关键结论：** 论文借此强调，即便在 H800 以 $2/h 租金的保守假设下，671B 参数的 MoE 大模型全周期训练仅花约 558 万美元，以此证明 FP8 混合精度、MoE 稀疏、 DualPipe 等架构与工程优化带来了**极致的训练性价比**，远低于同级别模型的公开预算。

**在论文中的定位：** 该表作为成本"账单"为前文提出的多项效率创新（FP8、MLA、MoE、负载均衡、无辅助损失的路由）提供**经济性闭环论据**，是全文"高性能+低成本"叙事链的最终落点。

### Table 2 (p.13) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab02.png]]
> [!quote] caption
> | Comparison of pipeline bubbles and memory usage across different pipeline parallel methods. 𝐹 denotes the execution time of a forward chunk, 𝐵 denotes the execution time of a full backward chunk, 𝑊 denotes the execution time of a "backward for weights" chunk, and 𝐹 & 𝐵 denotes the execution time o

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

图仅清晰显示表末**DualPipe (Ours)**一行：气泡公式 $(\frac{PP}{2}-1)(F\&B+B-3W)$，内存因子 **2×**，参数量 **PP+1**。结合caption，原表横向对比了 **1F1B、ZB-H1、ZB-H2、DualPipe** 等流水线并行方法的bubble与显存开销（以F、B、W、F&B为单位量化）。

**原文论证结论：** DualPipe通过**双向流水 + 权重梯度解耦**，使bubble系数减半（$\frac{PP}{2}$ vs $PP$），同时仅以 **2×** 显存与 **PP+1** 个通信张量换取接近零的气泡空闲，显著优于ZB-H系列。

**论文作用：** 该表是DualPipe设计章节的核心量化证据，为"高效MoE/稠密训练"链路中**并行策略对比**提供可验证的复杂度公式，是支撑DualPipe相对PipeDream/ZB-H1/H2优越性主张的关键依据。

### Table 3 (p.25) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab03.png]]
> [!quote] caption
> | Comparison among DeepSeek-V3-Base and other representative open-source base models. All models are evaluated in our internal framework and share the same evaluation setting. Scores with a gap not exceeding 0.3 are considered to be at the same level. DeepSeek- V3-Base achieves the best performance 

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心对象与结构**：表3在统一框架下将DeepSeek-V3-Base（激活37B/总参671B）与Qwen-2.5-72B、LLaMA-3.1-405B、DeepSeek-V2.5等开源基模型横评，覆盖英语理解、代码、数学、中文、多语言五大域约30项基准，多数采用n-shot评测；图片可见末行MMMLU-non-English(5-shot)得分64.0/74.8/73.8/**79.4**，V3-Base显著领先。

**关键结论**：该表论证——以仅37B激活参数（远小于对手72B–405B Dense），V3-Base在多数基准上达SOTA，尤其数学与代码任务大幅超越竞品（差距>0.3视为显著领先），验证MoE架构与FP8联合训练的有效性。

**链路作用**：作为总体性能横向锚点，与后续消融、长文、推理效率表互补，为方法有效性提供跨架构可比证据。

### Table 4 (p.26) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab04.png]]
> [!quote] caption
> | Ablation results for the MTP strategy. The MTP strategy consistently enhances the model performance on most of the evaluation benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 4对比Small MoE（2.4B激活/15.7B总参，1.33T tokens）与Large MoE（20.9B激活/228.7B总参，540B tokens）有无MTP策略在10项基准上的表现。MTP在两尺度均带来近全维度增益：代码数学类最显著——HumanEval +6.1/+9.2、GSM8K +6.0/+1.7、MATH +1.9/+1.2；BBH、DROP、TriviaQA等亦稳定提升；仅NaturalQuestions（-0.4）与大模型MMLU（-0.9）微降，Pile-test BPB基本持平。作为关键消融实验，该表以双尺度对照定量证实MTP辅助目标可一致提升性能，是支撑"MTP策略有效"这一DeepSeek-V3架构创新的核心实证依据。

### Table 5 (p.27) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab05.png]]
> [!quote] caption
> | Ablation results for the auxiliary-loss-free balancing strategy. Compared with the purely auxiliary-loss-based method, the auxiliary-loss-free strategy consistently achieves better model performance on most of the evaluation benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表5图文联合解读**

表5对比*Aux-Loss-Free*与*Aux-Loss-Based*两种MoE负载均衡策略，在Small MoF（2.4B激活/15.7B总参，1.33T tokens）与Large MoF（20.9B/228.7B，578B tokens）两规模、10项基准上做消融。

数据上，无辅助损失策略在绝大多数基准胜出：Pile-test BPB由0.727降至0.724（Large：0.656→0.652），BBH 37.3→39.3（66.7→67.9），HumanEval由40.2显著跃升至46.3，GSM8K 70.7→74.5，MATH 37.2→39.6；仅MMLU（68.3→67.2）、MBPP-Small（36.6→35.8）小幅落后。

论文以此消融支撑关键技术决策：放弃传统auxiliary loss而采用*auxiliary-loss-free*均衡，避免辅助梯度损害模型质量，作为DeepSeek-V3 MoE架构的核心设计之一。

### Table 6 (p.31) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab06.png]]
> [!quote] caption
> presents the evaluation results, showcasing that DeepSeek-V3 stands as the best- performing open-source model. Additionally, it is competitive against frontier closed-source models like GPT-4o and Claude-3.5-Sonnet.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明**：所提供图片仅为 §5.3.2 "Standard Evaluation" 中的表注文字段落，并未呈现 Table 6 本身的表格内容（具体模型、各基准分数与指标列均不可见），故仅依据原文解读。

**图文联合解读**：

1）**核心对象**：Table 6 应为标准化基准评测汇总表，对比 DeepSeek-V3 与开源模型（如 LLaMA-3.1-405B、Qwen-2.5-72B 等）及闭源前沿模型（GPT-4o、Claude-3.5-Sonnet）的得分情况，但具体数值未在图中显示。

2）**技术结论**：作者借此表论证 DeepSeek-V3 是"最强开源模型"，并在多维度上与 GPT-4o、Claude-3.5-Sonnet 等闭源前沿模型具竞争力。

3）**论文作用**：作为 §5 标准评测部分的核心证据，承接上文训练方法（FP8、低精度框架等图 6 内容）的技术铺垫，量化展示方法创新的实际性能收益，支撑全篇结论。

### Table 7 (p.33) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab07.png]]
> [!quote] caption
> | English open-ended conversation evaluations. For AlpacaEval 2.0, we use the length- controlled win rate as the metric.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图表联合解读：**

1）**结构与数据**：表展示6个模型在Arena-Hard与AlpacaEval 2.0（长度控制胜率）两项英文开放式对话基准上的得分。DeepSeek-V3以85.5/70.0双榜居首；Claude-Sonnet-3.5为85.2/52.0，GPT-4o为80.4/51.1，Qwen2.5-72B-Instruct为81.2/49.1，DeepSeek-V2.5为76.2/50.5，LLaMA-3.1 405B最低为69.3/40.5。

2）**关键结论**：DeepSeek-V3在英语开放式对话上全面超越所有对比的开源与闭源前沿模型；相较上一代V2.5，Arena-Hard提升9.3分、AlpacaEval 2.0大幅跃升19.5分，对话能力实现质的飞跃。

3）**论文作用**：与标准化基准互补，作为生成质量与人类偏好对齐的端到端能力验证，证明V3在开放式场景下达到SOTA水平。

### Table 8 (p.34) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab08.png]]
> [!quote] caption
> | Performances of GPT-4o, Claude-3.5-sonnet and DeepSeek-V3 on RewardBench.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 图文联合解读**

Table 8 在 RewardBench 基准上对比 DeepSeek-V3 与 GPT-4o（3 个版本）、Claude-3.5-sonnet（2 个版本）。五列依次为 Chat / Chat-Hard / Safety / Reasoning / Average。DeepSeek-V3 基线得分 96.9 / 79.8 / 87.0 / 84.3 / **87.0**；maj@6 进一步提升至 96.9 / 82.6 / 89.5 / 89.2 / **89.6**，超过 GPT-4o 最佳版 86.7 与 Claude-3.5-sonnet-1022 的 88.7。Chat 列各模型均 >95.8 区分度低；Chat-Hard、Safety 区分明显，maj@6 在 Reasoning 子项提升最大（+4.9）。

该表支撑对齐评估章节，证明 V3 奖励模型（reward model）质量已对齐闭源前沿，并展示 maj@6 集成对偏好的稳定增益，为论文 RLAIF/RLHF 流程可靠性提供关键佐证。

（注：题目所附原文段落描述的实为 Table 7 的 R1 蒸馏结果，与本图 RewardBench 内容不符，解读以图像为准。）

### Table 9 (p.34) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab09.png]]
> [!quote] caption
> | The contribution of distillation from DeepSeek-R1. The evaluation settings of Live- CodeBench and MATH-500 are the same as in Table 6.

> [!tip] 表格解读（多模态）
> 【图文联合解读】【图片说明】图片仅显示 Table 9 的 caption 与所在节 5.4.1"Distillation from DeepSeek-R1"的引言片段，表格本体（数值行）未在画面中呈现，故以下解读以 caption 原文与论文上下文为据。

【核心对象与结构】Table 9 以 **DeepSeek-V2.5-0905** 为基线，对比 **"无 R1 蒸馏"** 与 **"+R1 蒸馏"** 两组设置，在两个基准——**LiveCodeBench（代码生成）** 与 **MATH-500（数学推理）**——上的得分差异，评估设置沿用 Table 6。

【关键结论】R1 蒸馏在两项任务上均带来明显增益，且 **MATH-500 增幅尤为突出**（数学推理类提升显著），印证 R1 长链推理信号对下游模型具备强迁移能力。

【方法链路作用】该表是 5.4 Discussion 中唯一消融实验，承担 **"为 V3 训练流程引入 R1 蒸馏"提供实证依据** 的角色，衔接基座预训练—强化学习—蒸馏三大环节，奠定 V3 后训练方案合理性。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf{h}_i^{\prime k} = M_k [\operatorname{RMSNorm}(\mathbf{h}_i^{k-1}) ; \operatorname{RMSNorm}(\operatorname{Emb}(t_{i+k}))],
$$

$$
\mathbf{h}_{1:T-k}^{k} = \operatorname{TRM}_k(\mathbf{h}_{1:T-k}^{\prime k}),
$$

$$
P_{i+k+1}^{k} = \operatorname{OutHead}(\mathbf{h}_{i}^{k}).
$$

$$
\mathcal{L}_{\text{MTP}}^{k} = \operatorname{CrossEntropy}(P_{2 + k:T + 1}^{k}, t_{2 + k:T + 1}) = -\frac{1}{T} \sum_{i=2 + k}^{T + 1} \log P_i^k [t_i],
$$

$$
\mathcal{L}_{\text{MTP}} = \frac{\lambda}{D} \sum_{k=1}^{D} \mathcal{L}_{\text{MTP}}^{k}.
$$

$$
\begin{split} \mathcal{J}_{GRPO}(\theta) &= \mathbb{E}{[q \sim P(Q), \{o_i\}_{i=1}^G \sim \pi_{\theta_{old}}(O|q)]} \\ & \frac{1}{G}\sum_{i=1}^G \left( \min \left( \frac{\pi_\theta(o_i |q)}{\pi_{\theta_{old}}(o_i |q)} A_i, \text{clip} \left( \frac{\pi_\theta(o_i |q)}{\pi_{\theta_{old}}(o_i |q)}, 1 - \epsilon, 1 + \epsilon \right) A_i \right) - \beta \mathbb{D}_{KL}\left(\pi_{\theta} || \pi_{ref}\right)\right) , \end{split}
$$

$$
\mathbb{D}_{KL}\left(\pi_{\theta} || \pi_{ref}\right) = \frac{\pi_{ref}(o_i|q)}{\pi_{\theta}(o_i|q)}- \log\frac{\pi_{ref}(o_i|q)}{\pi_{\theta}(o_i|q)} - 1,
$$

$$
A_i = \frac{r_i - {\operatorname{mean}(\{r_1, r_2, \cdots, r_G\})}}{{\operatorname{std}(\{r_1, r_2, \cdots, r_G\})}}.
$$

$$
\boxed{\color{blue} \mathbf{c}_{t}^{KV}} &= W^{DKV} \mathbf{h}_{t}, \\ [\mathbf{k}_{t, 1}^{C};\mathbf{k}_{t, 2}^{C};...;\mathbf{k}_{t, n_{h}}^{C}] = \mathbf{k}_{t}^{C} &= W^{UK} \mathbf{c}_{t}^{KV}, \\ \boxed{\color{blue}\mathbf{k}_{t}^{R}} &= \operatorname{RoPE}({W^{KR}} \mathbf{h}_{t}), \\ \mathbf{k}_{t, i} &= [\mathbf{k}_{t, i}^{C}; \mathbf{k}_{t}^{R}], \\ [\mathbf{v}_{t, 1}^{C};\mathbf{v}_{t, 2}^{C};...;\mathbf{v}_{t, n_{h}}^{C}] = \mathbf{v}_{t}^{C} &= W^{UV} \mathbf{c}_{t}^{KV},
$$

$$
\mathbf{c}_{t}^{Q} &= W^{DQ} \mathbf{h}_{t}, \\ [\mathbf{q}_{t, 1}^{C};\mathbf{q}_{t, 2}^{C};...;\mathbf{q}_{t, n_{h}}^{C}] = \mathbf{q}_{t}^{C} &= W^{UQ} \mathbf{c}_{t}^{Q}, \\ [\mathbf{q}_{t, 1}^{R};\mathbf{q}_{t, 2}^{R};...;\mathbf{q}_{t, n_{h}}^{R}] = \mathbf{q}_{t}^{R} &= \operatorname{RoPE}({W^{QR}} \mathbf{c}_{t}^{Q}), \\ \mathbf{q}_{t, i} &= [\mathbf{q}_{t, i}^{C}; \mathbf{q}_{t, i}^{R}],
$$

$$
\mathbf{o}_{t, i} &= \sum_{j=1}^{t} \operatorname{Softmax}_j(\frac{\mathbf{q}_{t, i}^T \mathbf{k}_{j, i}}{\sqrt{d_{h} + d_{h}^{R}}}) \mathbf{v}_{j, i}^{C}, \\ \mathbf{u}_{t} &= W^{O} [\mathbf{o}_{t, 1};\mathbf{o}_{t, 2};...;\mathbf{o}_{t, n_{h}}],
$$

$$
\mathbf{h}_{t}^{\prime} & = \mathbf{u}_{t} + \sum_{i=1}^{N_{s}} {\operatorname{FFN}^{(s)}_{i}\left( \mathbf{u}_{t} \right)} + \sum_{i=1}^{N_r} {g_{i,t} \operatorname{FFN}^{(r)}_{i}\left( \mathbf{u}_{t} \right)}, \\ g_{i,t} & = \frac{g^{\prime}_{i,t}}{\sum_{j=1}^{N_r} g^{\prime}_{j,t}}, \\ g^{\prime}_{i,t} & = \begin{cases} s_{i,t}, & s_{i,t} \in \operatorname{Topk} (\{ s_{j, t} | 1 \leq j \leq N_r \}, K_{r}), \\ 0, & \text{otherwise}, \end{cases} \\ s_{i,t} & = \operatorname{Sigmoid} \left( {\mathbf{u}_{t}}^{T} \mathbf{e}_{i} \right),
$$

$$
g^{\prime}_{i,t} & = \begin{cases} s_{i,t}, & s_{i,t} + b_i \in \operatorname{Topk} (\{ s_{j, t} + b_j | 1 \leq j \leq N_r \}, K_{r}), \\ 0, & \text{otherwise}. \end{cases}
$$

$$
\mathcal{L}_{\mathrm{Bal}} & = \alpha \sum_{i=1}^{N_r}{f_i P_i}, \\ f_i = \frac{N_r}{K_r T} \sum_{t=1}^{T} \mathds{1} & \left( s_{i,t} \in \operatorname{Topk} ( \{ s_{j, t} | 1 \leq j \leq N_r \}, K_{r} ) \right), \\ s^{\prime}_{i,t} & = \frac{s_{i,t}}{\sum_{j=1}^{N_r} s_{j,t}}, \\ P_i & = \frac{1}{T} \sum_{t=1}^{T}{s^{\prime}_{i,t}},
$$

$$
\texttt{<|fim\_begin|>}f_{\text{pre}}\texttt{<|fim\_hole|>}f_{\text{suf}}\texttt{<|fim\_end|>}f_{\text{middle}}\texttt{<|eos\_token|>} . \nonumber
$$

## 技术点深读（DEEP）

![[deep/deepseek-v3-technical-report]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/deepseek-v3-technical-report.txt`（150416 字符）供引用检索。