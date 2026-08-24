---
paper_num: "69"
title: "Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning"
authors: "Reinforcement Learning Zhenyu Hou∗ Yujiang Li∗ Jie Tang Yuxiao Dong Tsinghua University"
date: "2026/7/8"
arxiv: "https://arxiv.org/abs/2607.07508"
pdf: "papers/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning.pdf"
slug: "single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning"
tags: [rl]
---

# Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning

> [!abstract] 摘要（原文）
> Reinforcement learning (RL) is becoming increasingly important for post-training large language models (LLMs). Previous RL pipelines for LLMs were mostly synchronous and batch-interleaved, which is inefficient for long-horizon agentic tasks. Recently, asynchronous RL has emerged as a more efficient alternative by updating the model as rollouts arrive. However, existing asynchronous RL systems often emphasize throughput, while leaving training stability and task effectiveness largely underexplored. For example, a key challenge is that group-wise sampling in the widely-used GRPO framework does not naturally fit asynchronous agentic training. In this paper, we present Single-rollout Asynchronous Optimization (SAO) to address the stability and off-policy challenges in asynchronous RL. To reduce off-policy effects and improve generalization, we replace group-wise sampling with single-rollout sampling, that is, using one rollout per prompt. We further improve this single-rollout strategy with practical value-model training designs. To improve optimization stability, we introduce a strict double-side token-level clipping strategy. SAO is able to train stably for one thousand steps and consistently outperform GRPO and its variants on agentic coding and reasoning benchmarks, such as SWE-Bench Verified, BeyondAIME, and IMOAnswerBench. We also demonstrate that single-rollout RL is particularly effective in a simulated online learning setting, where the model must adapt to changing evolving environments. To this end, SAO is successfully deployed in the agentic RL pipeline for training the open GLM-5.2 model (750B-A40B).

## 元信息
- **发表日期**: 2026/7/8
- **作者**: Reinforcement Learning Zhenyu Hou∗ Yujiang Li∗ Jie Tang Yuxiao Dong Tsinghua University
- **arXiv**: https://arxiv.org/abs/2607.07508
- **本地 PDF**: `papers/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning.pdf`
- **页数**: 14

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig01.png]]
*整页渲染: ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p01.png]]*
> [!quote] caption
> The performance of SAO on reasoning and coding benchmarks. The four reasoning benchmarks are evaluated in a reasoning-with-Python-tool setting, where the baseline is the Qwen3- 30B-A3B SFT model; SWE-Bench Verified evaluates coding with the Qwen3-30B-A3B baseline. SAO outperforms the corresponding baseline and GRPO across all five benchmarks. ∗Equal Contribution. Work done while ZH and YL interned

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图1联合解读**

该图为柱状图，对比SAO（深蓝）、GRPO（浅蓝）与基线（白）在多基准上的得分。可读取的量化结果：MMT Nov 2025上SAO达**88.3**，较GRPO（76.0）提升**12.3**分；IMO Answer Bench上SAO为**55.8**，超出基线53.3；SWE-Bench Verified上SAO得**29.8**，较GRPO（27.0）和基线（23.0）分别提升**2.8**与**6.8**分。

原文借此论证核心结论——SAO在四个推理基准与一个编码基准（共五项）上**全面稳定超越**GRPO与Qwen3-30B-A3B SFT基线，是支撑"单次rollout异步优化策略优于传统同步GRPO"主张的**首要经验证据**。

该图作为论文首页Figure 1，奠定整篇实验链路的基调——先以宏观性能对比建立方法有效性，再逐项剖析机制（异步、效率、单rollout假设），形成"结果先行、机理跟进"的论证结构。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig02.png]]
*整页渲染: ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p03.png]]*
> [!quote] caption
> Overview of SAO with single rollout design. The numbers denote the generation order of trajectories. For SAO, each trajectory becomes available for training immediately upon completion.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**核心对象与结构**：图分两行对比。上行（SAO）：编号 7、9（及 8）三条轨迹**逐条独立**送入 Training 模块，参数 π_θ 与 π_rollout 通过反向箭头同步迭代；下行（GRPO）：编号 3→2→1 的轨迹必须**积攒为一组**后整体送入 Training。右侧附两幅相同的 Trust Region 图，以横轴 A、纵轴 π_θ / π_rollout 给出上下界 1+ε_h 与 1-ε_l 围成的灰色安全区域，表明两方法均受同一信任域约束。

2）**关键技术结论**：SAO 单轨迹一完成即可训练（"ready for training"），无需等齐整组，从而消除 GRPO 中因等待最慢样本造成的 GPU 气泡；同步保证新旧策略比仍在 1±ε 信任域内。

3）**论文链路作用**：该图是方法概述的总锚点，承上启下——直观展示 SAO 把同步组训练拆解为异步流水线，启下各节中"Rollout–Train 交叠""资源利用率/吞吐提升""信任域约束保持"等分析与实验的对比基准。

### Figure 3 (p.6) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig03.png]]
*整页渲染: ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p06.png]]*
> [!quote] caption
> Performance comparison between SAO and GRPO (w/ DIS) during training. It can be observed that SAO almost consistently outperforms the optimized GRPO during the training process on different benchmarks. 4

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图3以Qwen3-30B-A3B为基模型，在AIME 2025与Beyond（AIME之外）两个数学基准上，对SAO、GRPO(w/ DIS)与Vanilla GRPO三条曲线进行了约1000步训练的准确率对比。**量化结果**显示：在AIME 2025上，SAO最终达到约95%，GRPO(w/ DIS)约92%；在Beyond基准上，SAO约70%，GRPO(w/ DIS)约65–67%；Vanilla GRPO在约150步后骤降至约73%并迅速崩溃退出。

**技术结论**：图中SAO曲线在两个基准的训练全程几乎全程位于GRPO(w/ DIS)之上，直观支撑原文"SAO almost consistently outperforms the optimized GRPO"的核心论断；同时Vanilla GRPO的早崩反衬出DIS稳定化与单rollout异步策略的必要性。

**作用定位**：作为论文的主对比实验图，它在方法/实验链路中扮演关键验证角色——将提出的SAO与经改进的强基线GRPO并列训练，是证明"单rollout+异步优化"在智能体RL中相对主流GRPO具有稳定性与性能双重优势的核心证据。

### Figure 4 (p.7) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig04.png]]
*整页渲染: ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p07.png]]*
> [!quote] caption
> Training dynamics of asynchronous single-rollout RL. (a) Explained Variance for SAO and a single-critic-update baseline. (b) Critic gradient norm during value training under full-parameter optimization and frozen-attention optimization used in SAO. (c) Token-level clip ratio during training for SAO with the proposed DIS and the VAPO baseline.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图4(b)(c)分别展示SAO训练动力学的两项关键诊断。**(b)** 为 Critic Gradient Norm 曲线，上方"SAO w/o Frozen attention"（全参数优化）在~500步后梯度飙升至约10且持续增长；下方 SAO（冻结注意力）稳定保持在4–5，证明冻结注意力对价值网络训练的正则化必要性。**(c)** 为 Token-level Clip Ratio，紫色 SAO 曲线在~500步附近出现峰值约0.006，蓝色 vanilla VAPO（无DIS）全程趋近于0，说明 DIS 机制允许更积极的策略更新并触发裁剪。两图共同支撑论文核心论断：异步单次rollout需配合**冻结注意力价值训练**与**DIS解耦裁剪**两项设计，二者协同保证异步架构下 critic 稳定与 policy 高效探索，是 SAO 优于串行VAPO的实验证据基础。

### Figure 5 (p.9) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig05.png]]
*整页渲染: ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p09.png]]*
> [!quote] caption
> Online learning simulation under changing writing-style preferences. 5

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示训练步数(0–430)与奖励(0–0.75)曲线，对比SAO(深蓝)与Running Mean基线(浅蓝)在单rollout在线学习下的表现。两处灰色阴影区(步150–170、290–310)代表风格奖励切换：SAO峰值约0.70–0.75，切换后迅速回升；Running Mean则适应滞后明显，稳态性能偏低(约0.45–0.60)。

该图论证在非平稳偏好下，SAO相比运行均值优势估计具备更快适应速度与更高稳态奖励，凸显其对偏好漂移的鲁棒性。

在实验链路中，此图作为消融对比，验证SAO相对传统优势估计的必要性，为单rollout异步优化方法的核心论点提供关键实证。

### Figure 6 (p.13) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig06.png]]
*整页渲染: ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p13.png]]*
> [!quote] caption
> Training reward for token-level SAO training and step-level variants, where token-level shows better training rewards.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图中横轴为训练步数（部分截断），纵轴为Reward（范围约0.42–0.54），对比三条曲线：SAO（token-level，浅蓝）、Step-level(Average)（紫）、Step-level(Last-Token)（深蓝）。训练起点三者均约0.44–0.45，中段曲线交织；最终SAO升至约0.47，明显高于Step-level(Average)的~0.44与Step-level(Last-Token)的~0.45。

原文借此论证：**在单次rollout异步优化框架下，采用token级优势估计（即SAO）比step级聚合（Average/Last-Token）能获得更高的训练奖励**，验证token级细粒度信用分配在agentic RL中的有效性。

在论文整体链路中，该图属于消融/对比实验环节，为前文方法部分提出的token级SAO算法提供直接经验证据，说明其设计选择（非step级粗粒度回报聚合）在奖励优化上具有可观测优势，支撑后续任务性能（pass@k）的整体提升结论。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-tab01.png]]
> [!quote] caption
> Experimental Results on math reasoning benchmarks(Accuracy %).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 联合解读**

该表列示Qwen3-30B-A3B在AIME2025、BeyondAIME、HMMT Nov 2025、IMOAnswerBench四项数学基准上的Accuracy%。核心数据：基线w/python仅14.6/10.5/17.3/7.8；施加SAO后跃至**97.3/74.8/88.3/74.0**，不仅全面超越同模型的GRPO(84.2/54.8/76.0/55.8)，还反超Claude-Sonnet-4.5与GPT-5 High，逼近更大规模GLM-4.7。消融项"SAO w/ DIS only"(94.2/71.5/86.7/71.3)与"GRPO+DIS"(93.5/70.8/84.0/70.0)均明显回落，证实双组件缺一不可。原文以此支撑"SAO全五基准均胜出"的核心论断，是实验链路中量化方法优越性的关键证据。

### Table 2 (p.6) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-tab02.png]]
> [!quote] caption
> Experimental Results on SWE-Bench Verified (Accuracy %).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读**

**①核心数据：** Table 2 量化展示 Qwen3-30B-A3B 在 SWE-Bench Verified 上的代码修复准确率：基座 23.0% → +GRPO(w/ DIS) 27.0% → +SAO(本文) **29.8%**。SAO 较基座绝对提升 **6.8 个百分点**，相对 GRPO(w/ DIS) 再提升 **2.8 个百分点**。下方三张训练曲线（AIME 2025、BeyondAIME、HMMT-Nov-2025）同步显示 SAO 紫线全程高于 GRPO(w/ DIS) 蓝线，且 Vanilla GRPO 浅蓝线在 ~200 步后崩溃，与表头量化结果形成"终值—过程"互证。

**②关键结论：** 配合 Figure 2"单轨迹生成即可训练、GRPO 须整组完成才能训练"的机制对比，Table 2 实证了 SAO 去除组内同步等待后，在代码修复这一典型 agentic RL 任务上既提升 **样本效率** 又提升 **最终精度**。

**③整体作用：** Table 2 是论文方法有效性的**主基准证据**，与 Figure 2（机制图）+ 数学三曲线（泛化证据）共同构成"机制创新→代码任务量化→数学任务过程"的完整验证链，支撑 SAO 相对 Vanilla GRPO 与 GRPO(w/ DIS) 的全面优越性主张。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-tab03.png]]
> [!quote] caption
> Ablation results of value model training strategy and critic update frequency. We compare partial parameters, i.e., frozen-attention, with full-parameter value update in RL training, as well as the effectiveness of faster critic updates per policy step. We report Accuracy (%) for all datasets

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读**

**1) 核心结构与数据：**
表格对比3种配置在AIME2025与BeyondAIME两个数学基准上的准确率（%）：①SAO（Frozen Attention + Critic频率=2）：97.3 / 74.8；②Single-step-update（Frozen Attention + 频率=1）：95.00 / 69.75；③Full-Parameter Value Training（全参数更新 + 频率=2）：90.62 / 74.50。变量为"Value训练策略（部分冻结 vs 全参数）"和"Critic更新频率（1 vs 2）"。

**2) 关键论证结论：**
- **冻结注意力优于全参数训练**：在同等频率=2下，Frozen Attention在AIME2025上比Full-Parameter高约6.7个百分点（97.3 vs 90.62），说明仅训练价值模型的部分参数即可，且效果更佳，验证了SAO的轻量化设计；
- **更高Critic更新频率有效**：SAO（频率=2）相比Single-step-update（频率=1），AIME2025提升2.3点、BeyondAIME提升5.05点，表明"每策略步更新两次Critic"的异步策略带来显著增益。

**3) 在论文链路中的作用：**
该表作为消融实验，支撑SAO方法的两大核心设计选择——价值模型局部训练与加速Critic更新，与Figure 3（SAO vs GRPO的训练曲线对比）共同构成方法有效性证据链，证明各组件选择均有数据支撑。

### Table 4 (p.8) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-tab04.png]]
> [!quote] caption
> Ablation results of value model training strategy and critic update frequency. We compare partial parameters, i.e., frozen-attention, with full-parameter value update in RL training, as well as the effectiveness of faster critic updates per policy step. We report Accuracy (%) for all datasets

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 联合解读**

**1) 核心数据**：表格对比了5种设置在 AIME2025 / BeyondAIME 上的准确率（%）：SAO（完整方法）= 97.3 / 74.8；去掉 Faster value = 95.0 / 69.8（↓2.3 / 5.0）；去掉 Frozen attention = 90.6 / 74.5（↓6.7 / 0.3）；Vanilla VAPO（无 DIS）= 91.3 / 69.0；Running mean baseline = 79.8 / 55.3。

**2) 关键结论**：两项消融均造成性能下降，证明二者缺一不可——冻结注意力对 AIME 至关重要（−6.7），对应 Figure 4(b) 中全参数优化导致 critic 梯度爆炸（≈10）的问题；加速 critic 更新则对 BeyondAIME 收益更大（−5.0），对应 Figure 4(a) 中 explained variance 的领先。

**3) 论文链路作用**：Table 4 是 Figure 4 训练动力学诊断的**性能验证**——前者证明现象（梯度不稳、价值预测不准），本表量化证实 SAO 的两个工程设计（frozen-attention + faster critic updates）以及 DIS 共同带来了相对 baseline 超 17 点的总体提升，闭合了"诊断→设计→增益"的论证链。

### Table 5 (p.13) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-tab05.png]]
> [!quote] caption
> The ablation on the action granularity for value and policy model training. Step-level denotes that each agent step is viewed as an action to calculate the value. Token-level refers to each token being viewed as an action. We report the results with the same training steps (400 steps).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**1) 核心对象与数据**
Table 5 在固定 400 训练步下，比较了三种动作粒度方案在 AIME2025 与 BeyondAIME 上的得分：Step-level (Average) 为 85.8 / 60.5，Step-level (Last-Token) 为 87.3 / 62.8，Token-level 为 89.8 / 66.8。三行单调递增，最优与最差之间在 AIME2025 相差 4.0 分，在 BeyondAIME 相差 6.3 分。

**2) 关键技术结论**
将每个 token 视为动作用于价值估计时效果最好；同为 Step-level 时，仅用末 token 聚合显著优于全步平均。结论：动作粒度越细，信用分配与策略优化越有效，验证了"token 级动作"的必要性。

**3) 在论文中的作用**
作为异步优化框架的关键设计消融，Table 5 支撑了作者在价值/策略模型训练中采用细粒度（token 级）动作的设计选择，是整套方法实证链路中的重要一环。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbb{E}\left[ \frac{1}{|y|} \sum_{t=1}^{|y|} \min \left( r_t(\theta) \hat{A}_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon) \hat{A}_t \right) \right]
$$

$$
\hat{A}_t^{\text{GAE}} = \sum_{l=0}^{|y|-t-1} (\gamma \lambda)^l \delta_{t+l}
$$

$$
\hat{A}_{i,t} = \frac{R_i - \mu_R}{\sigma_R}, \quad \text{with} \quad \mu_R = \frac{1}{G}\sum_{j=1}^G R_j
$$

$$
L(\theta) = \hat{\mathbb{E}}_t \left[ f(r_t(\theta), \epsilon_l, \epsilon_h) \hat{A}_t \log \pi_{\theta}(a_t|s_t) \right]
$$

$$
r_t(\theta) = \exp\left( \log \pi_\theta(a_t|s_t) - \log \pi_{\text{rollout}}(a_t|s_t) \right)
$$

$$
f(x; \epsilon_\ell, \epsilon_h) = \begin{cases} x, & \text{if } 1-\epsilon_\ell < x < 1+\epsilon_h \\ 0, & \text{otherwise} \end{cases}
$$

$$
\hat{A}(a_{i, N}) = \delta + \gamma \lambda \hat{A}(a_{i+1, 0})
$$

$$
\delta = r_t + \gamma V(a_{i+1, 0}) - V(a_{i, N})
$$

## 相关论文

- [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] — AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEMENT LEARNING
- [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] — DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
- [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] — Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning
- [[hybridflow-a-flexible-and-efficient-rlhf-framework]] — HybridFlow: A Flexible and Efficient RLHF Framework

## 技术点深读（DEEP）

![[deep/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning.txt`（45212 字符）供引用检索。