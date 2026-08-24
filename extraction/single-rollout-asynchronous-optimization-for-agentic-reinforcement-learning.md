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
> 【图文联合解读】图示对比SAO、GRPO与Baseline在5项基准的准确率（%）：AIME2025（80.4 / 84.2 / 97.3）、BeyondAIME（53.3 / 54.8 / 74.8）、HMMT Nov 2025（75.2 / 76.0 / 88.3）、IMOAnswerBench（53.3 / 55.8 / 74.0）、SWE-Bench Verified（23.0 / 27.0 / 29.8）。

技术结论：SAO在全部5项基准上同时优于Baseline与GRPO。推理类任务提升最显著——较GRPO提升12.3–20.0个百分点；编码任务虽绝对值偏低，仍取得对GRPO +2.8pp、对Baseline +6.8pp的正向增益，验证方法在"带Python工具的agentic推理"与"真实软件工程修复"两类异质场景下的通用有效性。

论文作用：作为headline result，与Table 1（纯数学推理）形成"广（多基准）—专（数学域）"互补，构成SAO在agentic RL设置下方法有效性的核心实证链，为后续消融与分析奠定基础。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig02.png]]
*整页渲染: ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p03.png]]*
> [!quote] caption
> Overview of SAO with single rollout design. The numbers denote the generation order of trajectories. For SAO, each trajectory becomes available for training immediately upon completion.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示GRPO与SAO两种训练范式的核心差异。GRPO（上）需生成组内全部9条轨迹后才启动训练，存在"waiting for Group"同步阻塞（已完成的1、2、7、9需等待仍在生成的3、4、5、6、8）；SAO（下）采用单轨迹完成即训练，按完成序9→8→…→1逐条进入训练端，rollout与训练流水线并行。两者共用相同Trust Region约束（π_θ/π_rollout ∈ [1−ε_l, 1+ε_h]），表明异步化并未放宽策略限制。该图论证了SAO的核心动机：在不改变信任域前提下，通过消除组同步等待提升时序利用率与样本效率，直接支撑后文SWE-Bench Verified实验中精度与训练效率的提升论证。

### Figure 3 (p.6) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig03.png]]
*整页渲染: ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p06.png]]*
> [!quote] caption
> Performance comparison between SAO and GRPO (w/ DIS) during training. It can be observed that SAO almost consistently outperforms the optimized GRPO during the training process on different benchmarks. 4

> [!tip] 技术解读（多模态）
> 【图文联合解读】图以训练步数为横轴、准确率为纵轴，对比AIME 2025、BeyondAIME、HMMT-Nov-2025：SAO（紫）几乎全程高于GRPO(DIS，蓝），终点约为96%/76%/91%，后者约95%/71%/87%；Vanilla GRPO（浅蓝）在百步后跌至约70%/42%/68%。上表最终准确率为23.0%→27.0%→29.8%。该图以同带DIS的GRPO公平对照，支撑SAO单次rollout异步优化更稳定、最终更优，并为Table 3价值模型与critic消融提供训练侧证据。

### Figure 4 (p.7) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig04.png]]
*整页渲染: ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p07.png]]*
> [!quote] caption
> Training dynamics of asynchronous single-rollout RL. (a) Explained Variance for SAO and a single-critic-update baseline. (b) Critic gradient norm during value training under full-parameter optimization and frozen-attention optimization used in SAO. (c) Token-level clip ratio during training for SAO with the proposed DIS and the VAPO baseline.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图4三子图诊断SAO训练动力学：**(a)** Explained Variance，SAO在~900步达~0.60，SAO w/o Faster value仅~0.52，差约8个百分点，验证Faster value提升价值拟合；**(b)** Critic Grad Norm，无冻结注意力时~500步后梯度飙至>10并持续增长，冻结后稳定于3–5，证明冻结注意力对价值网络训练的强正则化必要性；**(c)** Clip Ratio，SAO在~800步峰值~0.006，vanilla VAPO全程近0，表明DIS允许更积极策略更新并触发裁剪。三图共同支撑SAO两项核心设计（冻结注意力价值训练+DIS解耦裁剪），为异步架构优于串行VAPO提供关键实验证据。

### Figure 5 (p.9) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig05.png]]
*整页渲染: ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p09.png]]*
> [!quote] caption
> Online learning simulation under changing writing-style preferences. 5

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图5联合解读：**

图(a)展示Cute、Chuunibyou、Classical三种写作风格在400+训练步内的准确率动态迁移：偏好切换阴影区分别位于约175步与300步。Cute从初始~30%攀升至~73%峰值后骤降至近0%；Chuunibyou在275步附近达~78%峰值后回落；Classical则在300步后从0飙升至~65%；Academic始终贴近0%。图(b)对比SAO与Running Mean基线的奖励曲线：SAO峰值约0.72，显著高于基线的~0.55，且在两次偏好漂移阴影区后回升斜率更陡。

**论证结论**：证明SAO能在**非平稳奖励分布**下完成快速风格偏好适配，相比Running Mean基线具有更高的峰值奖励与更优的切换后恢复能力。

**整体作用**：该实验是论文验证算法**在线部署鲁棒性**的关键环节——超越静态任务基准，模拟真实场景中用户偏好时变的情形，为SAO相对传统RL方法的优势提供直接实证支撑。

### Figure 6 (p.13) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig06.png]]
*整页渲染: ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p13.png]]*
> [!quote] caption
> Training reward for token-level SAO training and step-level variants, where token-level shows better training rewards.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图6对比三种方案训练奖励（0–400步）：SAO（token级）由~0.425升至~0.54；Step-level(Average)与Step-level(Last-Token)均收敛于~0.495。token级SAO全程领先，差距约0.04–0.05。论文以此论证token级异步优化粒度优于步级均值或末token聚合，是SAO的关键设计依据，在消融链路中验证粒度选择对策略学习效率的直接影响。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-tab01.png]]
> [!quote] caption
> Experimental Results on math reasoning benchmarks(Accuracy %).

> [!tip] 表格解读（多模态）
> 【图文联合解读】表1列出AIME2025、BeyondAIME、HMMT Nov 2025、IMOAnswerBench四个数学推理基准的准确率，对比闭源模型（Claude-Sonnet-4.5、GPT-5 High、GLM-4.7在AIME2025分别达87.0%/94.6%/95.7%）与Qwen3-30B-A3B的多种配置：原始模型调用python工具时表现极差（AIME仅14.6%），关闭工具后跃升至85.0%；SFT与GRPO分别将带工具配置提升至80.4%和84.2%（AIME）。该表构建基线参照系，与图1联合论证"SAO在四个推理与一个编码基准上全面超越Qwen3基线和GRPO"的核心技术结论，是论文实验验证链路中的对照基准表。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-tab03.png]]
> [!quote] caption
> Ablation results of value model training strategy and critic update frequency. We compare partial parameters, i.e., frozen-attention, with full-parameter value update in RL training, as well as the effectiveness of faster critic updates per policy step. We report Accuracy (%) for all datasets

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

表3对比三种价值模型配置在AIME2025与BeyondAIME上的精度：①SAO（Frozen Attention，频率2）AIME2025达97.3%、BeyondAIME 74.8%，为最优；②Single-step-update（频率1）AIME降至95.00、BeyondAIME降至69.75；③Full-Parameter训练AIME仅90.62但BeyondAIME保持74.50。

**关键结论：**论文以此论证两点设计选择——价值模型冻结主干仅训练部分参数（frozen-attention）显著优于全参数更新，尤其在AIME2025上提升约6.7点；每策略步两次critic更新（频率2）较单次带来明显增益，表明更频繁的价值估计更新对策略学习至关重要。

**整体作用：**该表是消融实验核心，验证SAO框架中价值网络"轻量化训练+高频更新"组合的必要性，排除全参数价值头与低频更新的替代方案，为方法设计的合理性提供实证支撑。

### Table 4 (p.8) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-tab04.png]]
> [!quote] caption
> Ablation results of value model training strategy and critic update frequency. We compare partial parameters, i.e., frozen-attention, with full-parameter value update in RL training, as well as the effectiveness of faster critic updates per policy step. We report Accuracy (%) for all datasets

> [!tip] 表格解读（多模态）
> 【图文联合解读】表4在AIME2025、BeyondAIME上比较价值模型策略：SAO准确率为97.3%、74.8%，均最高；去掉更快价值更新降至95.0%、69.8%（分别下降2.3、5.0点），取消冻结注意力降至90.6%、74.5%，说明其主要稳定AIME训练，频繁价值更新则对两套数据均关键。图4显示全参数训练约500步后梯度升至约10，冻结注意力后稳定在4–5；二者共同构成SAO算法有效性及相对VAPO优势的分量消融与机制证据链。

### Table 5 (p.13) ⭐深度解读
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-tab05.png]]
> [!quote] caption
> The ablation on the action granularity for value and policy model training. Step-level denotes that each agent step is viewed as an action to calculate the value. Token-level refers to each token being viewed as an action. We report the results with the same training steps (400 steps).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 联合解读**

**1) 核心对象与数据**：表展示动作粒度消融，在相同400训练步下，对比三种粒度在AIME2025/BeyondAIME上的表现：Step-level (Average) 为85.8/60.5；Step-level (Last-Token) 为87.3/62.8；Token-level 为89.8/66.8。性能呈严格递增趋势，Token-level最佳，较Average版在AIME2025上提升+4.0，BeyondAIME上提升+6.3。

**2) 关键技术结论**：论文借此论证——将每个token视为动作（而非把整步聚合为单一动作）能为价值估计提供更细粒度、更准确的监督信号；即便同为Step-level，Last-Token聚合也优于Average聚合，进一步说明末步token携带了关键的未来回报信息。因此Token-level是该方法价值/策略训练粒度的合理且最优选择。

**3) 在论文链路中的作用**：作为消融实验，为论文所提单轨迹异步优化框架中"token级价值计算"这一核心设计决策提供了经验支撑，强化了方法组件选型的可信度。

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