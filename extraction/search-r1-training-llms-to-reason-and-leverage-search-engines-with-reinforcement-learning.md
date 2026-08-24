---
paper_num: "25"
title: "Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning"
authors: "Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning Bowen Jin1, Hansi Zeng2, Zhenrui Yue1, Jinsung Yoon3, Sercan ¨O. Arık3, Dong Wang1, Hamed Zamani2, Jiawei Han1 1 Department of Co"
date: "—"
arxiv: "https://arxiv.org/abs/2503.09516"
pdf: "papers/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning.pdf"
slug: "search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning"
tags: [training, rl]
---

# Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning

> [!abstract] 摘要（原文）
> 1\. 💡 SEARCH-R1 提出了一种新颖的强化学习 (RL) 框架，使大型语言模型 (LLMs) 能够学习自主生成搜索查询，并将推理与实时检索交错进行，以有效获取外部知识。 2. ⚙️ 该框架将搜索引擎建模为 RL 环境的一部分，通过检索令牌掩蔽 (retrieved token masking) 确保训练稳定性，并支持多轮推理与检索交互，使用 \<search>、\<information> 和 \<think> 等特定令牌进行结构化决策。 3. 📈 在七个问答数据集上的实验表明，SEARCH-R1 在相同设置下比 RAG 基线表现出显著的性能提升，并提供了关于 RL 优化方法、LLM 选择及响应长度动力学的宝贵见解。

## 元信息
- **发表日期**: —
- **作者**: Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning Bowen Jin1, Hansi Zeng2, Zhenrui Yue1, Jinsung Yoon3, Sercan ¨O. Arık3, Dong Wang1, Hamed Zamani2, Jiawei Han1 1 Department of Co
- **arXiv**: https://arxiv.org/abs/2503.09516
- **本地 PDF**: `papers/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning.pdf`
- **页数**: 31

## 图表（原文 caption + 页码）

### Figure 1 (p.4) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig01.png]]
*整页渲染: ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p04.png]]*
> [!quote] caption
> Demonstration of PPO and GRPO training with the search engine (SEARCH-R1).

> [!tip] 技术解读（多模态）
> 【图文联合解读】1) 图横向并列 **PPO（上）** 与 **GRPO（下）** 两条训练流程。PPO：查询 *q*→Rollout（Policy LLM + Search Engine）→观测 *o*，再经 Value LLM 得 *v*、Reward Model 与 Reference LLM（⊕）得 *r*，送入 **GAE** 输出优势 *A*；GRPO：同一 Rollout 对 *q* 采样 **G 条** *o₁…o_G*，由 Reward Model 得 *r₁…r_G*，经 **Group Computation** 归一化生成 *A₁…A_G*，仅以 KL 锚定、**无 Critic**。

2) 论证关键结论：Search-R1 把"带搜索引擎的多轮 rollout"做成可复用的中间通路；PPO 需额训 Value 网络，GRPO 用组内归一化替代 Critic，省显存且更易扩展。

3) 在论文中作用：作为方法总览图，确立 Search-R1 统一框架，衔接后文在多 QA 基准上对比两算法检索增强推理效果的实验链路。

### Figure 2 (p.9) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig02.png]]
*整页渲染: ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p09.png]]*
> [!quote] caption
> (a) PPO vs. GRPO: GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO provides more stable optimization but converges at a slower rate. (b) Base vs. Instruct LLM study: Instruction-tuned LLMs converge faster, but the final performance of both modles remains highly similar. (c)

> [!tip] 技术解读（多模态）
> 【图文联合解读】1) 四子图横轴均为训练步Step。(a) 0-500步：PPO(蓝)缓升至~0.40；GRPO(橙)约200步即达~0.40，随后骤降归零。(b) 0-200步：Base由~0.05缓升至~0.35，Instruct由~0.25速升至~0.40，终值相近。(c) 响应长度(950-1100)呈"降-升-稳"三段轨迹，与奖励(~0.5)同向。(d) 有效搜索次数由~1.4升至~1.85，与奖励协同上升。

2) 论证：GRPO收敛快但存崩溃风险；PPO稳而慢；指令微调仅加速收敛、不抬上限；模型自发学得更频繁调用搜索，长度与奖励耦合演化。

3) 作用：为Search-R1的算法选型(GRPO)、基座选择(Instruct)及奖励塑造(长度+搜索激励)提供关键实证支撑。

### Figure 3 (p.17) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig03.png]]
*整页渲染: ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]]*
> [!quote] caption
> Retrieved Token Loss Masking Study instruction-tuned models exhibit faster convergence and benefit from higher initial perfor- mance relative to their base counterparts. Despite this early advantage, the final performance of both model types converges to a similar level after training. These results indicate that while instruction tuning facilitates more efficient early-stage learning in reasoning

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 3：Retrieved Token Loss Masking Study）**

**(1) 核心对象与数据**
该图为消融实验，对比"对检索 token 做 loss 掩码（w. mask）"与"不做掩码（w.o. mask）"下 RL 训练奖励曲线，分两幅：**(a) Qwen-2.5-3b-base**（约 400 步）：w. mask（蓝）稳步上升至 ~0.40 并保持稳定；w.o. mask（橙）前期攀升至 ~0.40，但在 ~300 步后**骤降至接近 0**。**(b) Qwen-2.5-7b-base**（约 225 步）：w. mask 收敛至 ~0.45 且平稳；w.o. mask 同样在训练末段（约 215 步）出现**奖励崩塌**。

**(2) 关键技术结论**
不做掩码时，模型会"奖励黑客"——倾向直接复述检索到的原文以刷高似然，导致训练中后期奖励崩溃；而对检索 token 屏蔽 loss 可避免该退化，训练曲线稳定且最终性能更优。

**(3) 在论文中的作用**
这是 Search-R1 在算法设计上的**关键消融**，证明"对检索内容 token 进行 loss masking"是 PPO/GRPO 训练搜索增强 LLM 稳定收敛的必要设计，支撑了正文 Table 3 中稳定性能结果的合理性。

### Figure 4 (p.17) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig04.png]]
*整页渲染: ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]]*
> [!quote] caption
> Study of SEARCH-R1 on base and instruct LLMs. The instruction model converges faster and starts from a better initial performance. However, the final performance of both models is very similar. F

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图(a)(b)分别展示Qwen2.5-3B与7B的Base/Instruct模型在200步RL训练中的Train Reward曲线。Base模型起始奖励低（3B≈0.05，7B≈0.17），约100步后才追上；Instruct模型起始即较高（3B≈0.20，7B≈0.30），收敛更快；但两者最终奖励趋于一致（3B≈0.35–0.40，7B≈0.45–0.50）。原文借此论证：SEARCH-R1对预训练范式不敏感，无论base还是instruct起点，最终均收敛至相近性能，体现方法对底层LLM选择的鲁棒性。该图作为消融/适用性实验的关键证据，支撑了"RL训练可独立于指令微调阶段"的整体方法假设。

### Figure 5 (p.18) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig05.png]]
*整页渲染: ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p18.png]]*
> [!quote] caption
> Training dynamics of SEARCH-R1 with PPO and GRPO as the base RL method across four LLMs. GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO provides more stable optimization but converges at a slower rate. PPO and GRPO achieve comparable final reward performance. G

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

图示 Search-R1 在 Qwen2.5-3b/7b（含 base 与 it 共 4 个模型）上分别采用 PPO 与 GRPO 作为底层 RL 算法时的 Train Reward–Step 训练曲线，横轴跨度约 300–500 步，纵轴奖励区间约 0.1–0.5。

- **核心结构**：四幅子图均含橙（GRPO）、蓝（PPO）两条曲线。
- **关键现象**：GRPO 在全部 4 个模型中均更早爬升至高位，但中段出现明显 reward 塌陷（曲线骤降至接近 0）；PPO 上升较慢，但全程平滑无崩塌；两者最终收敛到相近奖励。
- **论证结论**：原文借此支撑"GRPO 收敛更快但训练不稳定、PPO 优化更稳健但速度较慢、最终性能可比"的论断。
- **论文作用**：作为训练动力学证据，与 Table 5 主结果互证，为 Search-R1 框架中 PPO/GRPO 算法选型的合理性提供实验依据。

### Figure 6 (p.19) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig06.png]]
*整页渲染: ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]]*
> [!quote] caption
> The training dynamics of SEARCH-R1 with a different number of retrieved pas- sages. (LLM: Qwen2.5-7b-base, RL: PPO)

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图展示SEARCH-R1在Qwen2.5-7b-base+PPO下，检索topk=1/3/5三条训练奖励曲线（step 0–500，纵轴0.1–0.55）：均从~0.1起步，~step 200前快速攀升，之后在0.45–0.55区间震荡收敛；topk=5于step 320附近出现明显下探，三者在收敛阶段高度交织。

原文借此论证：检索深度变化下训练动力学高度一致，证明SEARCH-R1对topk超参不敏感、训练稳定。

该图属消融实验，与Figure 5（不同LLM/RL组合）互补，为"检索增强RL训练具备鲁棒性"这一核心结论提供量化支撑。

### Figure 7 (p.19) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig07.png]]
*整页渲染: ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]]*
> [!quote] caption
> We observe that a larger group size generally leads to faster convergence but may also increase the risk of collapse due to the inherent instability of reinforcement learning.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图7呈现Qwen2.5-7b-base上SEARCH-R1(GRPO)三种group size（1/3/5）的训练奖励曲线。**size=5（蓝）**约120步升至~0.5后于~150步骤降归零；**size=3（橙）**在~200步同样崩塌；**size=1（绿）**缓慢爬升、稳定收敛至~0.5，全程未崩（500步）。

原文据此论证关键结论：group size越大收敛越快，但GRPO基于采样的高方差使崩塌风险显著上升——这是强化学习固有不稳定性的体现。

该图作为附录消融实验，在方法链路中支撑**超参trade-off讨论**：揭示"加速收敛"与"训练稳定"之间的张力，为主实验默认超参选择及PPO/GRPO对比（Table 7）提供定量依据。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.8) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab02.png]]
> [!quote] caption
> Main results. The best performance is set in bold. † / ⋆ represents in-domain/out- domain datasets.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读**

Table 2 在 Qwen2.5-7B/3B 两个基座上，对比 Direct/CoT/IRCoT/Search-o1/RAG/SFT/R1/Rejection Sampling 与 Search-R1 共 11 种方法，在 NQ†、TriviaQA⋆、PopQA⋆、HotpotQA†（域内†）及 2wiki⋆、Musique⋆、Bamboogle⋆（域外⋆）七项 QA 上的准确率。

关键数值：Search-R1-base 在 7B 上平均 **0.431**，全面压制 RAG（0.304）与 Rejection Sampling（0.348），并在 NQ/TriviaQA/PopQA/HotpotQA/Musique/Bamboogle 六项夺最优；3B 上 Search-R1-instruct 以 **0.325** 居首。

论文借此核心论证：RL 联合搜索引擎微调显著优于传统 RAG、SFT 与推理时检索增强，且在域内域外均稳定提升，是支撑 Search-R1 方法有效性的关键总表证据。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab03.png]]
> [!quote] caption
> The performance results of S EARCH -R1 with PPO and GRPO on seven datasets.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表3在7个QA数据集(NQ、TriviaQA、PopQA、HotpotQA、2wiki、Musique、Bamboogle)上对比11种方法在Qwen2.5-7B/3B基座与指令版上的平均表现。关键数据：Search-R1-base(7B)以0.431均分全面领先，大幅超过RAG(0.304)、Search-o1(0.206)及拒绝采样(0.348)；Search-R1-instruct(3B)达0.325亦为最优。该表证明RL驱动的Search-R1(PPO/GRPO)在通用QA与多跳QA、两种模型规模下均显著优于CoT、IRCoT、RAG等基线，是论文验证"强化学习+搜索引擎协同推理"方法有效性的核心主实验证据。

### Table 4 (p.9) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab04.png]]
> [!quote] caption
> The performance of S EARCH -R1 with and without retrieved token loss masking. The LLM trained with retrieved token loss masking achieves consistently better performance. (LLM: Qwen2.5-7b-base; RL: PPO)

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 4 对比 Search-R1 在 Qwen2.5-7b-base + PPO 下，是否对检索 token 做 loss masking 在 7 个 QA 基准上的表现：带 mask 版本 NQ 0.480/TriviaQA 0.638/PopQA 0.457/HotpotQA 0.433/2wiki 0.382/Musique 0.196/Bamboogle 0.432，均值 0.431；无 mask 版本对应为 0.388/0.567/0.391/0.325/0.321/0.108/0.304，均值 0.343。七项全部领先，平均提升约 8.8 个百分点（Bamboogle +0.128、Musique +0.088 最显著）。

论文据此论证：训练时屏蔽检索文档 token 的 loss，避免 LLM 在外部检索内容上消耗梯度信号，是 Search-R1 的关键设计。该消融支撑了整体方法链路——多轮检索与推理联合 PRL 训练中"让模型专注于学习何时、如何调用搜索，而非记忆检索内容"的核心假设。

### Table 5 (p.17) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab05.png]]
> [!quote] caption
> Main results. The best performance is set in bold. † / ⋆ represents in-domain/out- domain datasets.

> [!tip] 表格解读（多模态）
> 【图文联合解读】1) 表格展示 Qwen2.5-14b-Base/Instruct 上 10 种方法在 3 个 General QA（NQ†/TriviaQA⋆/PopQA⋆）与 4 个 Multi-Hop QA（HotpotQA†/2wiki⋆/Musique⋆/Bamboogle⋆）上的精确匹配率及均值。Search-R1-base 在全部 7 项均加粗最优（Avg.=0.479），较 R1-base（0.357）、Search-o1（0.310）、RAG（0.281）分别 +12.2/+16.9/+19.8 点；Search-R1-instruct（0.433）亦超 R1-instruct（0.339）。

2) 论证结论：Search-R1 基于 RL 的"检索-推理联合训练"在域内†与域外⋆任务上一致超越 CoT/RAG/SFT/R1 系列等基线，multi-hop 提升尤显著（Bamboogle 0.528 vs RAG 0.192），体现强泛化能力。

3) 论文作用：作为主结果表与 Figure 5 训练动力学互证——前者证 RL 训练可稳定收敛，本表证收敛后模型跨域达 SOTA，共同支撑 Search-R1 范式有效性及对 PPO/GRPO 的算法无关性。

### Table 6 (p.18) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab06.png]]
> [!quote] caption
> The performance of S EARCH -R1 with and without retrieved token loss masking. The LLM trained with retrieved token loss masking achieves consistently better performance. (RL: PPO)

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 图文联合解读**

Table 6 在 Qwen2.5-7B 与 3B 基座上对比 SEARCH-R1（PPO）训练时**是否对检索 token 做 loss 掩码**在 NQ、TriviaQA、PopQA、HotpotQA、2wiki、Musique、Bamboogle 七项 QA 基准的 Exact Match 得分。7B 带 mask 平均 0.431 vs 不带 0.343；NQ 0.480 vs 0.388、TriviaQA 0.638 vs 0.567、Musique 0.196 vs 0.108；3B 平均 0.303 vs 0.262，原文指出**带 mask 在绝大多数基准上均更优**，仅 Bamboogle 极个别点例外。结论：屏蔽检索片段的梯度可避免外部文本污染策略/价值信号，使 LLM 专注于自身推理生成与搜索调用决策，从而稳定提升 RAG-RL 性能。此消融支撑了 Search-R1 框架"仅对模型自身输出计算 RL 损失"这一核心训练机制设计的必要性。

### Table 7 (p.19) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab07.png]]
> [!quote] caption
> The number of retrieved passages study in S EARCH -R1 training. (LLM: Qwen2.5- 7b-base; RL: PPO)

> [!tip] 表格解读（多模态）
> 【图文联合解读】1) 表格展示 SEARCH-R1 训练时检索片段数 topk∈{1,3,5} 对 Qwen2.5-7b-base+PPO 在 7 个数据集（NQ、TriviaQA、PopQA、HotpotQA、2wiki、Musique、Bamboogle）及 Avg. 上的影响：topk=3 平均 0.431 最高且各列数值加粗全面胜出，topk=5 次之（0.400），topk=1 最差（0.375）。

2) 关键结论：检索片段并非越多越好，呈非单调关系——topk=1 信息不足、topk=5 引入噪声反拖累推理，topk=3 为最优折中。

3) 在论文中作为检索数量的消融实验，与 Figure 7 的 group size 消融并列，共同为训练超参选择与 RL 稳定性提供实证依据。

### Table 8 (p.20) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab08.png]]
> [!quote] caption
> The group size study of S EARCH -R1 (GRPO) on seven datasets. (LLM: Qwen2.5-7b- base)

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 联合解读**

1) **对象与数据**：Qwen2.5-7b-base 上 Search-R1 (GRPO) 在 NQ/TriviaQA/PopQA/HotpotQA/2wiki/Musique/Bamboogle 七数据集的 group size（1/3/5）消融。size=1 平均 0.410，size=3 为 0.363，size=5 为 0.350；size=1 在 NQ(0.463)、TriviaQA(0.605)、PopQA(0.449)、HotpotQA(0.392)、2wiki(0.413)、Musique(0.163) 六个任务上均最优，仅 Bamboogle 上 size=3 略胜 (0.400)。

2) **关键结论**：GRPO 组规模增大反而损害检索增强推理性能，size=1（无组内优势估计）即足以甚至最优，挑战"大 group 必优"的常规 GRPO 假设。

3) **链路作用**：作为消融支撑 Search-R1 训练对超参的低依赖性与鲁棒性，免去大 group 带来的采样开销，巩固其简洁可复现的设计主张。

### Table 9 (p.20) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab09.png]]
> [!quote] caption
> A case study of R1 and S EARCH -R1.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 9 图文联合解读**

该表展示 size=1/3/5 三种配置在 7 个 QA 基准（NQ、TriviaQA、PopQA、HotpotQA、2wiki、MusiQue、Bamboogle）上的得分。size=1 全面领先，平均 0.410（NQ 0.463、TriviaQA 0.605、PopQA 0.449、2wiki 0.413 加粗）；size=3 均降至 0.363，size=5 降至 0.350，规模越大性能越差。

原文借此论证关键结论：SEARCH‑R1 采用单文档检索即可达到最优，扩大检索返回量反而引入噪声、稀释有效信号、降低精度。该消融支撑了论文方法链路中检索模块的设计——少而精的检索配合 PPO/GRPO 强化学习训练优于多文档方案，证明模型在 R1 蒸馏框架下可习得精准调取搜索的能力。

### Table 10 (p.22) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab10.png]]
> [!quote] caption
> Search-R1 case study 1 (successful): Search-R1 conduct multi-step reasoning, search, with self-verification and finally answer the question.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 10 联合解读**

**核心对象与数据**：该表记录了 Search-R1 模型对多跳问答"What type of profession does Chris Jericho and Gary Barlow have in common?"的完整执行轨迹。模型共发起 5 次 `<search>` 调用、5 段 `<think>` 反思，依次检索两人各自职业、共同职业，并最终自验证纠正中间错误（如曾把"摔角手"误判为共同点），输出正确答案 `musician`（与 Ground Truth 一致）。

**论证的技术结论**：该案例直接支撑论文核心论点——经强化学习训练后，LLM 能自主编排多轮"思考—检索—验证"循环，调用搜索引擎补充外部知识，并在推理出错时通过迭代反思自我修正，无需人工设计推理链。

**在论文整体中的作用**：作为 Case Study 1，它与定量基准测试（Benchmark 指标）互补，以可读的 trace 形式直观展示 Search-R1 在 7B/13B 规模上涌现的自主多步推理与自验证能力，是证明 RL 训练有效性的关键定性证据。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathcal{J}_{GRPO}(\theta) = \, & \mathbb{E}_{x \sim \mathcal{D}, \{ y_i \}_{i=1}^{G} \sim \pi_{\text{old}}( \cdot| x; \se)} \Bigg[ \frac{1}{G} \sum_{i=1}^{G} \frac{1}{\sum_{t=1}^{|y_i|} I(y_{i,t})} \sum_{t=1: I(y_{i,t})=1}^{|y_i|} \min \Bigg( \frac{\pi_{\theta}(y_{i,t} | x, y_{i,<t}; \se)}{\pi_{\text{old}}(y_{i,t} | x, y_{i,<t}; \se)} \hat{A}_{i,t}, \nonumber \\[8pt] & \hspace{120pt} \text{clip} \Bigg( \frac{\pi_{\theta}(y_{i,t} | x, y_{i,<t}; \se)}{\pi_{\text{old}}(y_{i,t} | x, y_{i,<t}; \se)}, 1 - \epsilon, 1 + \epsilon \Bigg) \hat{A}_{i,t} \Bigg) - \beta \mathbb{D}_{KL} \left[ \pi_{\theta} || \pi_{\text{ref}} \right] \Bigg],
$$

$$
\max_{\pi_\theta} \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi_{\theta}(\cdot \mid x; \se)} \left[ r_{\phi}(x, y) \right] - \beta \mathbb{D}_{\text{KL}} \left[ \pi_{\theta}(y \mid x; \se) \,||\, \pi_{\text{ref}}(y \mid x; \se) \right],
$$

$$
\mathcal{J}_{PPO}(\theta) = \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi_{\text{old}}( \cdot| x; \se)} \left[ \frac{1}{\sum_{t=1}^{|y|} I(y_t)} \sum_{t=1: I(y_t)=1}^{|y|} \min \left( \frac{\pi_{\theta}(y_t | x, y_{<t}; \se)}{\pi_{\text{old}}(y_t | x, y_{<t}; \se)} A_t, \text{clip} \left( \frac{\pi_{\theta}(y_t | x, y_{<t}; \se)}{\pi_{\text{old}}(y_t | x, y_{<t}; \se)}, 1 - \epsilon, 1 + \epsilon \right) A_t \right) \right],
$$

$$
r_{\phi}(x, y) = \text{EM}(a_\text{pred}, a_\text{gold}),
$$

## 相关论文

- [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] — DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
- [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] — From ATOP to ZCube: Automated Topology Optimization Pipeline and A Highly Cost-Effective Network Topology for Large Model Training
- [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] — Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEMENT LEARNING
- [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] — AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning

## 技术点深读（DEEP）

![[deep/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning.txt`（100895 字符）供引用检索。