---
paper_num: "33"
title: "AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning"
authors: "Learning System for Language Reasoning Wei Fu12∗, Jiaxuan Gao1, Xujie Shen2, Chen Zhu2, Zhiyu Mei12, Chuyi He2, Shusheng Xu12, Guo Wei2, Jun Mei2, Jiashu Wang3, Tongkai Yang2, Binhang Yuan3, Yi Wu1 1 IIIS, Tsinghua Unive"
date: "2026/1/17"
arxiv: "https://arxiv.org/abs/2505.24298"
pdf: "papers/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning.pdf"
slug: "areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning"
tags: [rl]
---

# AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning

> [!abstract] 摘要（原文）
> 1\. 🏆 AReaL 提出了一个完全异步的强化学习系统，通过彻底解耦 LLM 的生成和训练过程，解决了同步 RL 系统在处理长推理任务时 GPU 利用率低和扩展性差的问题。 2. 🌟 为了在异步环境下保持 RL 训练的稳定性，AReaL 引入了对数据时效性的控制，并采用了一种解耦的 PPO 目标函数，使其能够有效利用来自不同策略版本的数据。 3. 🚀 实验结果表明，与同步系统相比，AReaL 在数学和代码推理基准测试中实现了高达 2.77 倍的训练加速，同时保持或提升了最终模型性能，并展示了良好的可扩展性。

## 元信息
- **发表日期**: 2026/1/17
- **作者**: Learning System for Language Reasoning Wei Fu12∗, Jiaxuan Gao1, Xujie Shen2, Chen Zhu2, Zhiyu Mei12, Chuyi He2, Shusheng Xu12, Guo Wei2, Jun Mei2, Jiashu Wang3, Tongkai Yang2, Binhang Yuan3, Yi Wu1 1 IIIS, Tsinghua Unive
- **arXiv**: https://arxiv.org/abs/2505.24298
- **本地 PDF**: `papers/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning.pdf`
- **页数**: 27

## 图表（原文 caption + 页码）

### Figure 1 (p.4) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig01.png]]
*整页渲染: ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]]*
> [!quote] caption
> Execution timeline of a synchronous (left) and a one-step overlap (right) RL system showing underutilized inference devices. … Rollout Controller Reward Service

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图以时间轴横向对比两种RL系统的执行流：左侧同步系统将24次生成任务（蓝条1-24，分布于4张GPU）依次排布，待全部生成完毕后才执行3轮训练块（橙块"1-8/9-16/17-24"）与权重加载（黄条），导致GPU在训练与加载阶段完全闲置；右侧一步重叠方案则把训练固定在单张GPU上进行，其余3张GPU持续滚动生成，使推理设备空置时间显著减少。

原文借此论证：**同步流水线存在严重的推理—训练串行空泡，是端到端吞吐的关键瓶颈**；即便仅做一步重叠也能回收大量空闲算力，从而为AReaL所提出的"全异步、生成与训练深度交叠"的整体架构提供量化动机，是其方法设计的核心起点，并在后续Table 1中转化为对AIME24/LiveCodeBench上端到端效率提升的实验依据。

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig02.png]]
*整页渲染: ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]]*
> [!quote] caption
> The AREAL architecture featuring asynchronous generation and training components.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示AREAL异步架构核心组成：①**生成端**（左虚线框）含多个Interruptible Rollout Worker（GPU节点，以"…"示意可扩展），受Rollout Controller（CPU）调度，由Reward Service（CPU）打分；②**训练端**（右虚线框）含多个Trainer Worker（GPU节点），通过Parameter Service做参数Save/Load（紫色箭头）；③数据通路为Rollout Controller → Aggregate Batch → Replay Buffer → Send Full Batch，左→右流动（蓝箭头Trajectory、绿箭头Prompt）；④红箭头Interrupt Signal支持生成途中刷新权重。

原文论证结论：解耦generation与training，避免同步RLHF的吞吐瓶颈；"可中断rollout"机制使轨迹可基于近实时策略生成，保证数据新鲜度。

论文整体作用：该架构是AREAL方法落地的系统工程核心，支撑其在大规模语言推理任务上实现高吞吐、近实时策略更新的RL训练链路。

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig03.png]]
*整页渲染: ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]]*
> [!quote] caption
> Illustration of generation management in AREAL. Vertical lines show the ready time for the next step training. Blue crosses show the interrupted requests when new parameters arrive. 4

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图以时间轴展示AREAL的异步生成-训练流水线：GPU1/GPU2并行执行生成任务（蓝色，编号1–9及字母a–g），GPU3负责训练（橙色，Batch1=1–4、Batch2=5–8、Batch3=9–c），三批之间通过黄色Load Weight加载新参数（θ₀→θ₁→θ₂），竖虚线标出"下一批次训练就绪时刻"。

图中蓝叉标记θ₁/θ₂到达时被中断的旧请求，中断后必须以新权重重做绿色KV Cache Recompute才能复用。该图论证了AREAL的核心机制：**用"可中断生成+重计算"换取参数新鲜度**——避免stale data的同时，量化了异步带来的KV重算开销，是支撑文中"训练不被生成阻塞、生成不因训练而等待"的关键设计图示。

### Figure 4 (p.8) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig04.png]]
*整页渲染: ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p08.png]]*
> [!quote] caption
> The strong scaling trend. Dotted lines indicate ideal linear scaling. verl consistently encounters OOM with 32k context length and the 32B model so the data points are missing. 8

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（≤220字）：**

**核心对象与数据**：2×3强扩展子图，分别对应 1.5B/7B/32B 模型与 16k/32k 上下文长度；横轴 GPU 数（32–512），纵轴吞吐 (token/s)。AReaL（蓝实线）整体逼近理想线性虚线：如 1.5B@16k 从 ≈29k 升至 ≈140k（32→256 GPU），7B@16k 在 512 GPU 时达 ≈100k；32B@32k 场景中 verl（橙线）因 OOM 数据点缺失，仅 AReaL 仍可跑通至 ≈33k。verl 在各子图均明显低于理想线。

**关键技术结论**：异步 RL 框架在跨模型规模、跨上下文长度下保持近线性扩展，显存与调度优于同步 verl，唯一支持 32B+32k 训练。

**论文作用**：作为系统效率实证支柱，为 Table 4 中 AIME24/25 等基准精度突破提供吞吐与可扩展性算力基础。

### Figure 5 (p.9) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig05.png]]
*整页渲染: ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p09.png]]*
> [!quote] caption
> Ablation studies of the decoupled PPO objective and staleness control with a 1.5B model on math reasoning tasks. Both algorithmic choices are essential. With a moderate staleness value and the decoupled objective, training progress can be accelerated by over 2× while maintaining final evaluation performance.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图5联合解读：**

图5基于1.5B模型在数学推理任务上做了三组消融：(a) naïve PPO学习曲线显示staleness=0/1训练奖励最高(≈-0.7)，staleness=16/∞仅≈-1.5；(b) 加入解耦目标(eq.5)后，staleness=2/4反而追平甚至略优于0/1；(c) 有效吞吐随staleness单调上升——0→128.7、1→269.3、2→356.6、4→356.6、8→371.7、16→382.4、∞→396.8 (k tokens/s)。

**技术结论**：解耦目标与适度staleness缺一不可。naïve PPO对异步延迟高度敏感；解耦目标使算法对staleness鲁棒，二者协同可在staleness=2~4时实现>2×加速(吞吐128.7→356+)且维持最终性能。

**论文作用**：作为关键消融，验证AREAL异步框架两条核心算法设计（解耦PPO目标 + staleness控制）的必要性与协同增益，为后续大规模实验提供方法论支撑。

### Figure 6 (p.10) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig06.png]]
*整页渲染: ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p10.png]]*
> [!quote] caption
> Ablation studies on system optimizations. experimental setup, we configured 32 micro-batches for the standard setting and established a token budget of 32,768 per micro-batch for the dynamic batching approach. As demonstrated in Figure 6a, dynamic batching yields an average of 30% throughput improvements across various model sizes.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图6通过两组消融实验量化两项系统优化：(a)动态微批次分配在1B/7B/32B模型上吞吐量达427.4/454.7/387.7 TFLOPs/GPU，较常规批处理(404.4/303.1/283.0)平均提升约30%；(b)可中断生成在1.5B/7B上吞吐达231k/130k tokens/s，比非中断方案(207k/111k)提升12%–17%。两图共同论证动态微批次与可中断生成均显著加速，验证AREAL异步RL框架在大规模语言推理训练中的工程可行性，为其系统设计提供关键量化支撑。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.8) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab01.png]]
> [!quote] caption
> End-to-End Performance Comparison. We evaluate on the AIME24 benchmark for math and LiveCodeBench (8/1/24-2/1/25) for coding. We limit the maximum generation length to 32K tokens and sample 32 responses per question, reporting the average pass@1 accuracy. * represents the best known reproducible res

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文联合解读**

表1对比 basemodel / VeRL / Sync.AReaL / AReaL 在 1.5B–32B 四个规模上、针对 AIME24（数学）与 LiveCodeBench（代码）的 pass@1、节点数、PPO 步数与训练小时数。

**关键数据**：AReaL 在准确率与基线相当或更优（7B 63.1 vs Sync 63.0；14B 58.1 vs VeRL 57.9*；32B 61.0 vs 61.2）的同时，将训练耗时近乎砍半（1.5B 33.6→14.8h、7B 52.1→25.4h、14B 44.4→21.9h、32B 46.4→31.1h）。

**论文作用**：作为端到端系统级实证，验证异步 RL 设计（图1所述 rollout/训练流水线重叠）在跨规模、跨任务下均能保精度并显著提升训练效率，直接支撑论文核心效率主张。

### Table 2 (p.9) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab02.png]]
> [!quote] caption
> Evaluation scores when varying data staleness, comparing performance with and without the decoupled objective. Numbers within ± 1 of the oracle score are underlined.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 表的核心对象与结构**

该表展示AREAL在四个数学基准（AIME24、AIME25、AMC23、MATH 500）上、按最大数据陈旧度（1, 2, 4, 8, 16, ∞）分组，对比"不使用/使用解耦目标（W/o vs With）"的评估得分；陈旧度=0为Oracle同步基线（42.0 / 32.9 / 84.4 / 89.2），下划线标注与Oracle相差±1以内的得分。

**2) 关键技术结论**

去掉解耦目标后，性能随陈旧度增大急剧恶化——例如AIME24在陈旧度=4时骤降至23.3（远低于Oracle 42.0），AIME25同步跌至23.1；引入解耦目标后，各陈旧度下得分几乎贴近Oracle（AIME24在陈旧度=4仍达42.2，下划线），证明解耦目标对陈旧数据具有强鲁棒性。

**3) 在论文方法链中的作用**

该表是AREAL异步RL框架可行性的核心实证，支撑了"解耦生成与训练目标即可容忍异步带来的数据陈旧"这一关键论点，使系统在保持接近同步（Oracle）水平的前提下获得吞吐增益。

### Table 4 (p.25) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab04.png]]
> [!quote] caption
> Results on math benchmarks. Model AIME24 AIME25 AMC23 MATH 500

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读**

该表对比1.5B与7B模型在AIME24/25、AMC23、MATH500四道数学基准上的三组配置（basemodel、Sync. AReaL、AReaL异步）。7B模型上，异步AReaL相对基线提升显著（AIME24 +8.8、AIME25 +5.6），且与同步版性能基本持平（AIME24 63.1 vs 63.0；MATH500 94.3 vs 94.2）。该表与图4强扩展性形成互补：图4证明异步框架获得更高吞吐，本表则验证异步训练不损失模型精度。它是论文"异步RL核心贡献"的关键有效性证据，支撑了方法在规模与质量上的双重优势。

### Table 5 (p.26) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab05.png]]
> [!quote] caption
> Results on coding benchmarks. Model LiveCodeBench v5 Codeforces CodeContests

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 数据**：展示 6 个模型在 3 项编程基准（LiveCodeBench v5、Codeforces 评分/通过率、CodeContests）的成绩。14B 组：base 53.4/1801·95.8%/32.0、Sync 56.7/1845·96.4%/37.0、AReaL 58.1/1840·96.3%/35.9；32B 组：57.4/1839·96.3%/34.3、61.2/1911·96.9%/36.3、61.0/1889·96.7%/36.5。

**关键结论**：异步 AReaL 14B 在 LiveCodeBench 较 base 提升 +4.7（53.4→58.1），且反超 32B base（57.4）；32B 下异步与同步基本持平（61.0 vs 61.2），编码任务上未损失性能。

**论文作用**：与 Figure 5（数学消融）互补，证明异步 RL 框架在编码推理任务同样有效，验证方法跨域通用性与可扩展性。

### Table 6 (p.26) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab06.png]]
> [!quote] caption
> Generalization results on DeepSeek-Distilled-Llama-8B across math benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表展示AReaL在DeepSeek-Distilled-Llama-8B上的跨模型家族泛化结果，对比基线与两种学习率(η=4、η=8)的微调表现。四个数学基准上微调均显著超越基线(50.4/84.2/89.1/23.3)：η=4达58.4/92.3/92.2/42.6，AIME25提升最大(+19.3)；η=8为57.2/91.5/91.9/41.6，略低于η=4。该表证明AReaL异步RL框架不依赖特定基座，可有效迁移至不同模型家族，验证方法的普适性。

### Table 7 (p.26) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab07.png]]
> [!quote] caption
> Staleness-throughput trade-off on small-scale academic setup.

> [!tip] 表格解读（多模态）
> 【图文联合解读】# Table 7 联合解读

**1) 核心对象与数据：** 表中对比基线模型与两种不同陈旧度阈值（η=4、η=8）下 AReaL 微调模型在 AIME24、AMC23、MATH500、AIME25 四个数学推理基准上的表现。η=4 取得 58.4/92.3/92.2/42.6，η=8 为 57.2/91.5/91.9/41.6，均显著优于 DeepSeek-Distilled-Llama-8B 基线的 50.4/84.2/89.1/23.3。

**2) 关键结论：** η=4 略优于 η=8，表明在小规模学术设置下较小的 staleness 阈值带来更稳定的策略优化收益；同时验证了大规模设置（Table 2）中"陈旧度—吞吐权衡"的初步结论可迁移至少 GPU 场景。

**3) 论文链路作用：** 该表是"小规模可复现性验证"实验，连接 Table 2（大规模主结果）与消融结论，证明 AReaL 在 8 GPU、1.5B 模型等受限资源下仍有效，强化了系统设计的通用性与鲁棒性论证。

### Table 8 (p.26) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab08.png]]
> [!quote] caption
> Staleness-throughput trade-off using RLOO algorithm. Model AIME24 AIME25 AMC23 MATH500 Throughput

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 解读**

**1）核心对象与数据**：表格展示 RLOO 算法下，1.5B 模型在不同 staleness η∈{0,1,2,4,8,16} 时于 AIME24/25、AMC23、MATH500 上的准确率与吞吐量。吞吐量随 η 增大从 27.1k 升至 52.0k（近翻倍）；准确率波动小，AIME24 介于 29.9–34.1，MATH500 稳定在 86 左右；η=4 取得 AIME24/25 峰值（34.1/28.1）；即使 η=16 仍优于基线 DeepSeek-Distilled-Qwen-1.5B（32.8 vs 29.3）。

**2）技术结论**：佐证 RLOO 对异步训练具有更好的容忍度——高 staleness 带来近一倍吞吐增益，性能却几乎无损。

**3）论文链路作用**：作为 C.4 节补充实验，配合 Table 7（PPO）共同扩展 AReaL 异步框架对多种 RL 算法（RLOO/PPO）兼容性的实证支撑，强化"异步化不牺牲收敛质量"的核心主张。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\pibehav(\cdot|s) = \begin{cases} \pi_{\theta+j}(\cdot|s) & \text{if } t_j\leq t\leq t_{j+1} \text{ and } s\in \mathcal{S}_t(q) \\ \text{arbitrary} & \text{otherwise} \end{cases}
$$

$$
J(\theta)= \mathbb{E}_{q\sim\mathcal{D}, a_t\sim\pi_\theta\left(\cdot|q,a_{<t}\right)} \left[ \sum_{t=1}^H \gamma^{t-1}r(s_t,a_t) \right].
$$

$$
J_\mathrm{PPO}(\theta)= \mathbb{E}_{q\sim\mathcal{D}, a_t\sim\pi_{\mathrm{old}}\left(\cdot|q,a_{<t}\right)} \left[ \sum_{t=1}^H \min\left( u_t(\theta)\hat{A}(s_t,a_t),\mathrm{clip}\left(u_t(\theta),1-\epsilon,1+\epsilon\right)\hat{A}(s_t,a_t)\right) \right],
$$

$$
\lfloor (N_r-1) /B \rfloor \leq i + \eta.
$$

$$
J(\theta)&= \mathbb{E}_{q\sim\mathcal{D}, a_t\sim\pibehav} \left[ \sum_{t=1}^H \min( \underset {{\text{Importance Ratio}}} { \boxed{ \frac{\pi_\theta}{\pibehav} } } \hat{A}_t,\quad \overbrace{ \frac{\piprox}{\pibehav} \mathrm{clip}( \underset{\text{Trust Region Center}}{ \boxed{ \frac{\pi_\theta}{\piprox} } } ,1-\epsilon,1+\epsilon )\hat{A}_t }^\text{Importance Ratio} ) \right] \\ &= \mathbb{E}_{q\sim\mathcal{D}, a_t\sim\pibehav} \left[ \sum_{t=1}^H \frac{\piprox}{\pibehav} \min\left( u_t^\mathrm{prox}(\theta)\hat{A}_t, \mathrm{clip}\left( u_t^\mathrm{prox}(\theta),1-\epsilon,1+\epsilon \right)\hat{A}_t) \right) \right],
$$

## 相关论文

- [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] — Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning
- [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] — DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEMENT LEARNING
- [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] — Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning
- [[hybridflow-a-flexible-and-efficient-rlhf-framework]] — HybridFlow: A Flexible and Efficient RLHF Framework

## 技术点深读（DEEP）

![[deep/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning.txt`（88470 字符）供引用检索。