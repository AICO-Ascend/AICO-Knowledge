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
> 【图文联合解读】**图文联合解读**

**核心对象与结构：** Figure 1 横向并列展示 Search-R1 的两种 RL 训练范式。上半部分为 **PPO**：策略 LLM（Trained Model，黄色）在 rollout 阶段多轮调用 Search Engine（蓝色）；训练时由 Value 函数 v 与即时奖励 r 经 **GAE** 计算 Advantage A，并以 Frozen Reference Model（绿色）做 KL 锚定。下半部分为 **GRPO**：移除 Critic，对同一 query 采样 G 条 rollout（r₁…r_G），经 **Group Computation** 生成逐样本归一化的优势 A₁…A_G。两者共用同一带 search engine 的多轮 rollout 通路。

**关键论证结论：** Search-R1 验证了"LLM+搜索引擎"可在 PPO（有 critic）与 GRPO（无 critic）两种主流 RL 算法下统一训练，证明 search engine 接入与具体 RL 框架解耦，方法具有算法无关的通用性。

**论文整体作用：** 作为 Method 部分的总览图，统摄后续 PPO/GRPO 消融与主实验的实验链路，是读者理解 Search-R1 训练闭环的入口。

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
> 【图文联合解读】**图文联合解读：**

图(b)为Qwen-2.5-7b-base在约200步RL训练中的Train Reward曲线，对比"w. mask"（蓝）与"w.o. mask"（橙）。两者起点均约0.10–0.15；带掩码曲线约150步升至~0.45并稳定；不带掩码曲线整体滞后，且在近终点处出现剧烈塌陷（骤降至~0.10），训练不稳定。

**技术结论：** 检索到的外部token应被屏蔽、不参与损失计算；掩码策略可加速收敛并避免不相关检索内容干扰策略更新。

**方法作用：** 该实验验证了Search-R1训练链路中"retrieved-token-loss-masking"这一关键设计选择的必要性，为RL+检索的整体流程提供消融支撑。

### Figure 4 (p.17) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig04.png]]
*整页渲染: ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]]*
> [!quote] caption
> Study of SEARCH-R1 on base and instruct LLMs. The instruction model converges faster and starts from a better initial performance. However, the final performance of both models is very similar. F

> [!tip] 技术解读（多模态）
> 【图文联合解读】**核心对象与结构**：图(b)展示Qwen2.5-7b-base/instruct在PPO RL训练下的Train Reward曲线（Step 0–200，奖励区间0.15–0.50）。Base（蓝）初始奖励约0.18，约50步后开始抬升；Instruct（橙）初始约0.38，全程高位震荡；两者最终均收敛于~0.45。

**关键技术结论**：用以论证SEARCH-R1对底座模型鲁棒——指令微调版收敛更快、起点更优，但最终性能与基础版几乎一致，说明该RL训练范式不依赖特定的模型初始化。

**论文整体作用**：作为支撑性消融实验，与Table 4（检索token loss masking消融）并列，证明SEARCH-R1的关键设计选择在多种设置下均有效，强化方法可推广性的论证。

### Figure 5 (p.18) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig05.png]]
*整页渲染: ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p18.png]]*
> [!quote] caption
> Training dynamics of SEARCH-R1 with PPO and GRPO as the base RL method across four LLMs. GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO provides more stable optimization but converges at a slower rate. PPO and GRPO achieve comparable final reward performance. G

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图5展示了Search-R1在Qwen2.5-7b-base（500步，奖励0.1→0.55）与Qwen2.5-7b-it（约300步，奖励0.3→0.5）上PPO与GRPO的训练曲线对比。GRPO（橙）初期爬升更陡，约150步即接近收敛；PPO（蓝）爬升较缓但全程平稳；在7b-it图中GRPO约200步处出现明显下跌，印证其"后段不稳定"。

论文借此论证Search-R1框架对底层RL算法不敏感，PPO与GRPO最终奖励可比、均可作为可行基座，从而支撑其方法链路的算法兼容性结论，强化"RL+检索"范式的普适性主张。

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

图7展示SEARCH-R1采用GRPO算法、基于Qwen2.5-7b-base模型时，不同组大小（group size=1/3/5）在约500步训练过程中奖励（reward）的动态变化曲线。横轴为训练步数（Step），纵轴为奖励值，绿色×标记（size=1）曲线明显位于上方，在0.4–0.6区间剧烈波动；蓝线（size=5）与橙线（size=3）则贴近底部、几乎重叠且波动微弱。

原文借此说明：组大小并非PPO收敛的主导因素——size=1反而获得最高奖励，而size=3与size=5训练信号极弱（提示GRPO在该设定下需更大群体方差才能形成有效优势），从而佐证检索深度（top-k）并非性能瓶颈这一关键结论。在全文实验链路中，该图与表7互为补充，共同构成"对超参不敏感、方法鲁棒"的论证支撑，强化了SEARCH-R1框架无需精细调参即可稳定训练的核心卖点。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.8) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab02.png]]
> [!quote] caption
> Main results. The best performance is set in bold. † / ⋆ represents in-domain/out- domain datasets.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表2以Qwen2.5 3B/7B为骨干，对比Direct、CoT、IRCoT、Search-o1、RAG、SFT、R1及拒绝采样，评估4个通用QA和3个多跳QA（NQ、HotpotQA为域内，其余域外）。7B Search-R1-base平均0.431（拒绝采样0.348），7项中6项最佳，仅2Wiki由instruct版0.414领先；3B instruct版平均0.325。说明RL+搜索带来稳定主增益；该表承担跨域泛化证据，并衔接训练曲线：有效搜索增加，GRPO快但后期不稳，PPO更稳。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab03.png]]
> [!quote] caption
> The performance results of S EARCH -R1 with PPO and GRPO on seven datasets.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 3 给出 Qwen2.5-7B/3B 上 Search-R1-base/instruct 在 7 个 QA 任务（NQ、TriviaQA、PopQA、HotpotQA、2wiki、Musique、Bamboogle）的成绩：7B 端 Search-R1-base 平均 0.431，6 个数据集最优，显著领先 Rejection Sampling（0.348）、RAG（0.304）、IRCoT（0.239）等基线；3B 端 Search-R1-instruct（0.325）略胜 base（0.303）。论文借此论证基于 RL（PPO/GRPO）训练在通用与多跳问答均稳定超越 CoT/SFT/RAG，方法具备规模与任务通用性。该表作为主结果对齐两套 RL 算法与多基线，为方法有效性提供核心量化支撑。

### Table 4 (p.9) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab04.png]]
> [!quote] caption
> The performance of S EARCH -R1 with and without retrieved token loss masking. The LLM trained with retrieved token loss masking achieves consistently better performance. (LLM: Qwen2.5-7b-base; RL: PPO)

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读**

Table 4 对比 Search-R1 在 7 个 QA 基准上"是否 mask 检索 token loss"的消融结果（Qwen2.5-7b-base + PPO）。带 mask 版本在 NQ(0.480)、TriviaQA(0.638)、PopQA(0.457)、HotpotQA(0.433)、2wiki(0.382)、Musique(0.196)、Bamboogle(0.432) 七项全部领先，平均分 0.431 对 0.343，绝对提升 0.088；Bamboogle 涨幅最大(+0.128)。

**论证结论**：训练中对检索文本 token 不计算 loss 是关键设计——避免模型退化为抄写检索内容，使 PPO 梯度信号集中在自身生成的推理 token 上。

**论文作用**：作为方法关键消融之一，为 Search-R1 "仅对生成 token 计算 loss"的 RL 训练策略提供实证支撑，验证了方法设计的合理性与必要性。

### Table 5 (p.17) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab05.png]]
> [!quote] caption
> Main results. The best performance is set in bold. † / ⋆ represents in-domain/out- domain datasets.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 5 展示在 Qwen2.5-14b-Base/Instruct 上 10 种方法在 7 个 QA 基准（NQ†、TriviaQA⋆、PopQA⋆、HotpotQA†、2wiki⋆、Musique⋆、Bamboogle⋆）上的精确匹配率（EM）。**Search-R1-base 平均 0.479，在全部 7 项中均取得最高分**（NQ 0.486、TriviaQA 0.676、PopQA 0.480、HotpotQA 0.468、2wiki 0.470、Musique 0.241、Bamboogle 0.528），较 R1-base（0.357）、Search-o1（0.310）、RAG（0.281）、IRCoT（0.221）等基线平均提升 12–20 分。

原文借此论证：引入搜索引擎交互的强化学习训练，相比传统 RAG、IRCoT 及纯推理 R1 基线均带来显著且一致的提升，**证明了"推理+检索"联合强化学习的有效性**。该表是论文主实验的核心证据，集中呈现 Search-R1 的方法贡献与性能优势。

### Table 6 (p.18) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab06.png]]
> [!quote] caption
> The performance of S EARCH -R1 with and without retrieved token loss masking. The LLM trained with retrieved token loss masking achieves consistently better performance. (RL: PPO)

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 图文联合解读**

**1) 核心对象与数据**
该表对比 SEARCH-R1 在 Qwen2.5-7B-Base 与 Qwen2.5-3B-Base 上"有无检索 token 损失掩码"（w. mask / w.o. mask）两种变体，在 NQ、TriviaQA、PopQA、HotpotQA、2wiki、Musique、Bamboogle 共 7 个 QA 基准及平均分上的精确匹配率。结果显示：7B-Base w. mask 平均 0.431 vs w.o. mask 0.343（+0.088），7 项全部领先；3B-Base 0.303 vs 0.262（+0.041），6/7 项胜出，仅 Musique、Bamboogle 两小集略低。

**2) 关键结论**
原文借此论证"对外部检索 token 做损失掩码"是必要训练技巧：避免将奖励/梯度信号错误分配给非模型自身生成内容，从而稳定 RL 优化、提升泛化。

**3) 在论文中的作用**
属训练细节消融实验，支撑 SEARCH-R1 多轮"思考—检索—推理"RL 框架的核心设计：损失必须仅覆盖模型输出 token，是其方法可信复现与推广的关键贡献之一。

### Table 7 (p.19) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab07.png]]
> [!quote] caption
> The number of retrieved passages study in S EARCH -R1 training. (LLM: Qwen2.5- 7b-base; RL: PPO)

> [!tip] 表格解读（多模态）
> 【图文联合解读】表格展示Qwen2.5-7b-base+PPO在7个QA基准（NQ/TriviaQA/PopQA/HotpotQA/2wiki/Musique/Bamboogle）上topk∈{1,3,5}的实证对比：topk=3平均0.431全面领先topk=5（0.400）与topk=1（0.375），并在7个数据集中的6个上取得最优（如Musique 0.196 vs 0.156/0.146，Bamboogle 0.432 vs 0.352/0.328）。原文借此论证两点关键结论：①检索深度并非PPO收敛的主导驱动因素（因训练轨迹近乎重合）；②topk=3为搜索质量与上下文噪声的最优折中。该消融与Figure 7（GRPO组大小）共同支撑"SEARCH-R1对关键超参鲁棒、可稳定收敛"的核心实验论断，并为默认topk=3的设计选择提供量化依据。

### Table 8 (p.20) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab08.png]]
> [!quote] caption
> The group size study of S EARCH -R1 (GRPO) on seven datasets. (LLM: Qwen2.5-7b- base)

> [!tip] 表格解读（多模态）
> 【图文联合解读】表8以Qwen2.5-7B-Base为骨干，对SEARCH-R1的GRPO组大小1、3、5进行消融，覆盖7个数据集。平均分依次为0.410、0.363、0.350，size=1总体最优；NQ、TriviaQA、PopQA分别为0.463、0.605、0.449。仅Bamboogle例外：size=3为0.400，高于size=1的0.384。该表说明增大采样组并无稳定收益，用于确定训练超参并检验检索增强GRPO策略。

### Table 9 (p.20) ⭐深度解读
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-tab09.png]]
> [!quote] caption
> A case study of R1 and S EARCH -R1.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表对比了 SEARCH-R1 在检索文档数量 size=1/3/5 三种设置下，于 NQ、TriviaQA、PopQA、HotpotQA、2wiki、Musique、Bamboogle 七个数据集上的表现。数据显示：**size=1 平均最优（0.410）**，NQ（0.463）、TriviaQA（0.605）、PopQA（0.449）、HotpotQA（0.392）、2wiki（0.413）、Musique（0.163）均居首；仅 Bamboogle 上 size=3（0.400）略胜。

论文借此论证关键结论：**SEARCH-R1 检索单文档即可获得最佳性能**，增加检索数量反而因引入噪声而拖累效果（0.410→0.363→0.350），说明该方法具备从最小化检索上下文中精准推理的能力。

在全论文链路中，此消融实验支撑了"检索增强 + 强化学习"框架的简洁性主张，为 SEARCH-R1 相对 R1 的设计选择提供了实验依据。

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