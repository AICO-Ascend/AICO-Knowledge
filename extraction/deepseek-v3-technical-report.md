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
> 【图文联合解读】**图文联合解读：**

图示展示 **8 个 PP rank**（Device 0–7）与 **20 个双向 micro-batch** 的 DualPipe 调度，色块区分 Forward（橙）、Backward（深/浅绿）、Backward for weights（蓝）及计算-通信重叠区（共享黑框）。正反向 batch 同时从 pipeline 两端注入，中部 Device 3–4 前后向大面积重叠，蓝色权重梯度块填补气泡时间。

**原文论证：** 双向流水线 + 细粒度计算-通信 overlap 显著压缩 pipeline bubble，使跨节点 EP 下的 all-to-all 通信被前向/反向计算完全掩盖。

**论文作用：** 作为训练基础设施章节的核心可视化证据，支撑"MoE 训练近乎零通信开销"这一关键声明，与 FP8、低精度优化、跨节点 EP 设计共同构成 DeepSeek-V3 高效训练闭环的方法学支撑。

### Figure 6 (p.15) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-fig06.png]]
*整页渲染: ![[assets/deepseek-v3-technical-report-p15.png]]*
> [!quote] caption
> Firstly, in order to accelerate model training, the majority of core computation kernels, i.e., GEMM operations, are implemented in FP8 precision. These GEMM operations accept FP8 tensors as inputs and produce outputs in BF16 or FP32. As depicted in Figure 6, all three GEMMs associated with the Linear operator, namely Fprop (forward pass), Dgrad (activation backward pass), and Wgrad (weight backwa

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示DeepSeek-V3的FP8混合精度训练框架，以Linear算子为例，包含三个GEMM：**Fprop**（BF16 Input→FP8，与Weight相乘，FP32累加→Output BF16）、**Dgrad**（BF16 Output Gradient→FP8，与Weight相乘→Input Gradient BF16）、**Wgrad**（FP8输入相乘→Weight Gradient FP32→BF16）。权重经Optimizer在FP32 Master Weight上更新，再转FP8供前/反向使用。

**论证结论：** 多数核心GEMM可采用FP8计算、FP32累加、BF16/FP32输出的混合精度策略，在不损失数值稳定性的前提下显著加速训练、降低显存。

**方法链地位：** 该框架是DeepSeek-V3高效训练的关键基础设施，支撑其671B参数模型以经济成本完成端到端FP8训练，是后续Table 6基准对比（性能对标GPT-4o/Claude-3.5）的工程前提。

### Figure 10 (p.48) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-fig10.png]]
*整页渲染: ![[assets/deepseek-v3-technical-report-p48.png]]*
> [!quote] caption
> 48

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图10由左右两个子图组成，分别对比16B与230B DeepSeek-V2模型在BF16与FP8两种精度下的训练loss曲线（EMA平滑系数0.9）：横轴为训练token数（B），纵轴为loss；两图均含放大显示FP8−BF16残差的插图，幅值仅约±0.001，两条曲线高度重合。

该图论证的关键结论是：FP8混合精度训练相对BF16基线loss几乎无损，差值始终在极小噪声范围内波动，证明低精度训练框架是收敛等价的。

在论文链路中，它是"低精度训练消融"章节的核心实证，与FP8 GEMM/累加策略、tile-wise与group-wise量化方案共同构成DeepSeek-V3以FP8完成全量训练可行性论证的关键依据。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab01.png]]
> [!quote] caption
> | Training costs of DeepSeek-V3, assuming the rental price of H800 is $2 per GPU hour.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表量化展示DeepSeek-V3三阶段训练成本：预训练2664K H800 GPU小时（$5.328M，占总成本95.5%）、上下文扩展119K（$0.238M）、后训练仅5K（$0.01M），总计2788K GPU小时、$5.576M（按$2/GPU·h计）。

论文借此核心论证：尽管为671B参数MoE大模型，凭借FP8混合精度、MoE稀疏激活、高效通信等优化，整体训练仅约558万美元，远低于同规模稠密模型，凸显极致训练经济性。该表置于报告开篇，作为"高性能+低成本"主论点的关键实证，为后续架构创新与训练策略的可信度提供量化背书。

### Table 2 (p.13) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab02.png]]
> [!quote] caption
> | Comparison of pipeline bubbles and memory usage across different pipeline parallel methods. 𝐹 denotes the execution time of a forward chunk, 𝐵 denotes the execution time of a full backward chunk, 𝑊 denotes the execution time of a "backward for weights" chunk, and 𝐹 & 𝐵 denotes the execution time o

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读**

表格横向对比1F1B、ZB1P、DualPipe三种流水线并行方案的三项指标——气泡时间、参数内存、激活内存。气泡公式逐级缩减：1F1B为(PP−1)(F+B)，ZB1P利用"反向权重"叠加降为(PP−1)(F+B−2W)，DualPipe借助双向流水进一步压缩至(PP/2−1)(F&B+B−3W)，有效阶段数折半使气泡近乎减半。代价是参数内存由1×升至2×、激活内存由PP增至PP+1。

论文借此定量论证：DualPipe以可控的额外内存，换取显著更小的流水线气泡，是其跨节点专家并行（DualPipe + Expert Parallel）链路中缓解流水线空泡、提升端到端训练效率的核心调度创新。

### Table 3 (p.25) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab03.png]]
> [!quote] caption
> | Comparison among DeepSeek-V3-Base and other representative open-source base models. All models are evaluated in our internal framework and share the same evaluation setting. Scores with a gap not exceeding 0.3 are considered to be at the same level. DeepSeek- V3-Base achieves the best performance 

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 3 将 DeepSeek-V3-Base 与主流开源基座模型在同一内部评测框架下进行多基准横向比较。图中可见 Multilingual / MMMLU-non-English (EM, 5-shot) 一行四个模型得分依次为 64.0、74.8、73.8、79.4，V3-Base 以 **79.4** 加粗居首。原文据此论证：在统一设置下，V3-Base 在多数基准（尤以数学、代码任务）取得最优，并设定 0.3 分作为"同一梯队"判据，避免微小差异被夸大。该表在论文实验链路中充当"基座主竞技场"，承接前文架构（MLA/DeepSeekMoE/FP8 训练）与流水线创新，为后训练 SFT/RL 章节提供统一可比基线，验证基础模型的相对优势起点。

### Table 4 (p.26) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab04.png]]
> [!quote] caption
> | Ablation results for the MTP strategy. The MTP strategy consistently enhances the model performance on most of the evaluation benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明**：图片仅呈现标题与正文段落，表格具体数值未在图中展示，以下解读依据原文描述进行。

**1）核心对象与结构**：Table 4 为 MTP（Multi-Token Prediction）策略的消融实验表。在两种规模下对比：
- 小规模：15.7B 参数 MoE 基线，1.33T tokens 训练；
- 大规模：228.7B 参数 MoE 基线，540B tokens 训练。
两组均保持训练数据与架构不变，仅追加 1 层深度 MTP 模块；推理时直接丢弃 MTP 模块，保证推理成本完全一致。

**2）关键结论**：MTP 在两种规模、绝大多数评测基准上一致提升模型性能，且不增加任何推理开销——证实其为"训练期免费增益"。

**3）论文作用**：位于第 4.5 节"讨论"的消融研究，与 4.5.2 的无辅助损失负载均衡消融并列，分别支撑 MTP 与 DualPipe/负载均衡两项核心架构创新，为 DeepSeek-V3 整体性能收益提供可分解的归因证据。

### Table 5 (p.27) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab05.png]]
> [!quote] caption
> | Ablation results for the auxiliary-loss-free balancing strategy. Compared with the purely auxiliary-loss-based method, the auxiliary-loss-free strategy consistently achieves better model performance on most of the evaluation benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表5在参数与训练量相同下，对比两种MoE均衡策略：Small为2.4B激活/15.7B总参数、1.33T token，Large为20.9B/228.7B、578B。免辅助损失法在多数基准更优，如Small BBH由37.3升至39.3，Large HumanEval由40.2升至46.3；仅Pile及个别项互有胜负。该消融排除规模和训练量影响，验证无辅助损失均衡通常仍能提升能力，为V3采用该MoE方案提供直接依据。

### Table 6 (p.31) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab06.png]]
> [!quote] caption
> presents the evaluation results, showcasing that DeepSeek-V3 stands as the best- performing open-source model. Additionally, it is competitive against frontier closed-source models like GPT-4o and Claude-3.5-Sonnet.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图像说明**：图片仅显示该表的引用段落（caption），未呈现表格实际数据，故仅依据原文解读。

**图文联合解读**：

1）**核心对象与结构**：表6位于第5.3.2节"Standard Evaluation"，属于标准基准综合评测表，对比对象涵盖开源模型与前沿闭源模型（GPT-4o、Claude-3.5-Sonnet等），按多维度基准（推理、代码、数学、中文等）横向列出得分。

2）**关键论证结论**：用"开源最佳 + 闭源可竞争"的双重定位支撑 DeepSeek-V3 的整体性能优势——既证明开源阵营领先，又证明其已逼近闭源前沿模型能力上限。

3）**论文链路作用**：该表位于实验章节核心位置，是 FP8 训练、MLA、MoE 等架构/系统创新的最终落地验证；前文技术细节证明方法可行，本表则量化证明方法有效，构成"技术创新→性能实证"的闭环论证。

### Table 7 (p.33) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab07.png]]
> [!quote] caption
> | English open-ended conversation evaluations. For AlpacaEval 2.0, we use the length- controlled win rate as the metric.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表对比 DeepSeek-V3 与 DeepSeek-V2.5-0905、Qwen2.5-72B-Instruct、LLaMA-3.1 405B、GPT-4o-0513、Claude-Sonnet-3.5-1022 在 Arena-Hard 与 AlpacaEval 2.0（长度受控胜率）上的成绩。V3 以 85.5 / 70.0 双双居首：AlpacaEval 较第二名 Claude（52.0）领先 18 分，Arena-Hard 微超 Claude（85.2），相对自家 V2.5（76.2/50.5）也有显著提升。该表用于论证 V3 在英语开放式对话与人类偏好对齐上已超越主流开源与闭源模型，达到 SOTA；作为文末综合评测链路的关键一环，与推理、代码、多语言等章节协同，支撑论文"全方位领先"的总结论。

### Table 8 (p.34) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab08.png]]
> [!quote] caption
> | Performances of GPT-4o, Claude-3.5-sonnet and DeepSeek-V3 on RewardBench.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 图文联合解读**

**① 核心对象与结构**：在 RewardBench 上对比 DeepSeek-V3（含基线与 maj@6）与 GPT-4o（0513/0806/1120 三版）、Claude-3.5-sonnet（0620/1022 两版），按 Chat / Chat-Hard / Safety / Reasoning / Average 五列打分。V3 基线均值 87.0，maj@6 升至 89.6；对比组最高为 Claude-3.5-sonnet-1022 的 88.7 与 GPT-4o-0806 的 86.7。

**② 关键结论**：Chat 列各家均 >95.8 区分度低；Chat-Hard、Safety 拉开档次；maj@6 在 Reasoning 子项提升最大（84.3→89.2，+4.9），均分反超两大对手，证明 V3 奖励模型的判别与对齐能力已达国际顶尖闭源水平。

**③ 论文作用**：属对齐评估章节关键证据，用以支撑"开源 V3 在偏好奖励建模上可对标 GPT-4o/Claude-3.5"的整体论证。

### Table 9 (p.34) ⭐深度解读
![[assets/crops/deepseek-v3-technical-report-tab09.png]]
> [!quote] caption
> | The contribution of distillation from DeepSeek-R1. The evaluation settings of Live- CodeBench and MATH-500 are the same as in Table 6.

> [!tip] 表格解读（多模态）
> 【图文联合解读】图像仅显示表9题注及5.4.1引言，表格数值行未呈现，故无法辨认，仅依据原文：表9以DeepSeek‑V2.5为基线，消融DeepSeek‑R1蒸馏的贡献，考察加入/不加入该蒸馏在LiveCodeBench与MATH‑500上的表现，评测设置同表6。具体增益数值因内容缺失无法确定。该消融旨在说明R1蒸馏能增强代码与数学推理能力，连接R1推理能力输出与V3系列后训练改进的验证环节。

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