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
> 【图文联合解读】**图4联合解读：**

图4以2×2子图展示强扩展性实验，对比AREAL（蓝实线）与verl（橙虚线）在GPU数从128增至512时的吞吐量，纵轴约18k–37k tokens/秒，覆盖7B/32B模型与16k/32k上下文四种组合。AREAL扩展接近理想线性线，32B模型下吞吐由约18k提升至35k；verl斜率显著偏低，且在32B+32k上下文时直接OOM导致数据缺失。

该图用以论证AREAL异步RL框架的扩展性优势：在更大模型、更长上下文场景下仍保持近线性加速比，而同步基线verl已触及显存瓶颈，从而为论文"大规模异步RL可行且高效"的核心结论提供关键实证支撑。

### Figure 5 (p.9) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig05.png]]
*整页渲染: ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p09.png]]*
> [!quote] caption
> Ablation studies of the decoupled PPO objective and staleness control with a 1.5B model on math reasoning tasks. Both algorithmic choices are essential. With a moderate staleness value and the decoupled objective, training progress can be accelerated by over 2× while maintaining final evaluation performance.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（图5，p.9）**

**1）核心对象与数据：** 三面板消融实验，基于1.5B模型在数学推理任务上的训练。(a)(b)分别为naive PPO与解耦目标（式5）下MaxStaleness∈{0,1,2,4,8,16,∞}的奖励曲线；(c)为有效吞吐量条形图，定量数据为128.7→269.3→356.6→356.6→371.7→382.4→396.8 k tokens/s，随staleness单调递增。

**2）关键结论：** 仅增大staleness会劣化naive PPO（曲线发散、奖励下降）；而解耦目标使所有staleness曲线紧贴η=0 oracle，性能几乎无损。二者结合即"适度staleness+解耦目标"可获得>2×训练加速且保持最终评估性能——证实两个算法选择缺一不可。

**3）论文链路作用：** 该图为AREAL异步RL框架的核心算法决策提供实证：它把"解耦PPO目标"与"staleness容忍度"确立为系统级最优配置，支撑后文大规模实验的高吞吐-高性能主张，是方法论可行性的关键消融证据。

### Figure 6 (p.10) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig06.png]]
*整页渲染: ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p10.png]]*
> [!quote] caption
> Ablation studies on system optimizations. experimental setup, we configured 32 micro-batches for the standard setting and established a token budget of 32,768 per micro-batch for the dynamic batching approach. As demonstrated in Figure 6a, dynamic batching yields an average of 30% throughput improvements across various model sizes.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图6(b)展示中断式生成消融：1.5B模型吞吐量231k vs 207k tokens/s，7B为130k vs 111k，可中断机制带来约12%–17%提升。结合未渲染的图6(a)：动态批处理在1B/7B/32B较常规批处理分别达427.4/454.7/387.7 vs 404.4/303.1/283.0 TFLOPs/GPU，平均~30%吞吐增益。两图共同量化验证AREAL的两项系统优化——动态微批次分配与可中断生成——均显著提升吞吐，在论文方法链中为异步RL框架的工程可行性提供关键实验支撑。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.8) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab01.png]]
> [!quote] caption
> End-to-End Performance Comparison. We evaluate on the AIME24 benchmark for math and LiveCodeBench (8/1/24-2/1/25) for coding. We limit the maximum generation length to 32K tokens and sample 32 responses per question, reporting the average pass@1 accuracy. * represents the best known reproducible res

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 联合解读**

表1在AIME24（1.5B/7B）与LiveCodeBench（14B/32B）上对比AReaL与VeRL、Sync.AReaL，统一32K长度、32样本、平均pass@1。AReaL精度与最优基线持平或略优：42.2 vs 43.1*（1.5B）、63.1 vs 63.0（7B）、58.1 vs 57.9*（14B）、61.0 vs 61.2（32B），但训练小时数显著降低：14.8 vs 33.6（1.5B）、25.4 vs 57.7（7B）、21.9 vs 44.4（14B）、31.1 vs 51.1（32B），普遍约2×加速。该表直接量化证明论文核心结论——"异步RL以一半训练时间达到同等精度"，呼应Figure 1对推理设备闲置的诊断，确立AReaL在效率–性能权衡上的优势。

### Table 2 (p.9) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab02.png]]
> [!quote] caption
> Evaluation scores when varying data staleness, comparing performance with and without the decoupled objective. Numbers within ± 1 of the oracle score are underlined.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表2图文联合解读：**

表2在Max.Stale∈{0(Oracle),1,2,4,8,16,∞}下，对比AIME24/25、AMC23、MATH500四个基准在使用/不使用解耦目标(W/o/With)时的得分，Oracle分别为42.0/32.9/84.4/89.2。

**核心结论：** 无解耦目标时，性能随陈旧度增大显著衰减（如AIME24在Stale=4仅23.3、∞为34.0）；引入解耦目标后表现稳健，多数cell与Oracle差距≤1（图中下划线标示，如AIME24在Stale=4仍达42.2、AMC23在Stale=4为85.1）。

**方法作用：** 异步RL系统中训练端不可避免消费陈旧 rollout 数据，该表实证解耦目标可有效抑制staleness带来的优化偏差，为AREAL异步生成-训练架构的可行性提供关键实验支撑。

### Table 4 (p.25) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab04.png]]
> [!quote] caption
> Results on math benchmarks. Model AIME24 AIME25 AMC23 MATH 500

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读**

Table 4 横向对比 1.5B/7B 基模型与同步、异步 AReaL 在 AIME24/25、AMC23、MATH 500 上的表现。1.5B 基线 29.3/24.4/71.0/84.3 → 异步 AReaL 升至 42.2/32.0/85.1/89.5；7B 基线 54.3/41.7/89.5/92.8 → 升至 63.1/47.3/93.6/94.3。

**关键结论**：异步 AReaL 与同步版精度几乎持平，多项指标略优（如 AMC23：1.5B +0.7、7B +0.4；MATH 500：7B +0.1），且均显著优于基模型（1.5B AIME24 提升 12.9，7B 提升 8.8）。

**论文作用**：此表与 Figure 4（强可扩展性）构成"精度+效率"双重证据链，支撑 AReaL 核心论点——异步训练机制在可扩展性优势的同时未牺牲模型准确率，验证系统设计的有效性。

### Table 5 (p.26) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab05.png]]
> [!quote] caption
> Results on coding benchmarks. Model LiveCodeBench v5 Codeforces CodeContests

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读（Table 5）：**

**注：** 您提供的原文讲解段落对应的是 *Figure 5（消融实验）*，与本图 *Table 5* 并非同对象；以下基于图片内容解读 Table 5。

**核心数据：** 表5对比 base / Sync. AReaL / AReaL 三档模型在 LiveCodeBench v5、Codeforces、CodeContests 上的结果。14B 组：AReaL 在 LiveCodeBench 以 58.1 领先（+4.7 vs base 53.4）；32B 组：Sync. AReaL 在 LiveCodeBench 61.2、Codeforces 1911/96.9% 居首，AReaL 在 CodeContests 36.5% 最高。

**关键结论：** 异步 AReaL 相对同步版在 LiveCodeBench 提升（14B +1.4）；32B 整体优于 14B，验证异步 RL 系统在代码推理任务上的可扩展性。

**整体作用：** 与 Figure 5 消融（算法设计）互补，Table 5 提供真实编程基准上的最终性能证据，闭环支撑"异步 RL + 解耦目标"完整方法链。

### Table 6 (p.26) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab06.png]]
> [!quote] caption
> Generalization results on DeepSeek-Distilled-Llama-8B across math benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 图文联合解读**

**1) 核心对象与数据**：表6展示DeepSeek蒸馏Llama在数学基准上的泛化对比（注意：caption写8B，但可见行为14B与32B模型）。三个数据列对应不同数学基准得分。14B：base 53.4/32.0、Sync AReaL 56.7/37.0、AReaL异步版58.1/35.9；32B：base 57.4/34.3、Sync 61.2/36.3、AReaL异步61.0/36.5。

**2) 关键结论**：异步AReaL相较base模型在14B上提升约4.7分（53.4→58.1），32B上提升3.6分（57.4→61.0），且与同步版本得分基本持平（14B甚至略超），证明异步训练未牺牲泛化质量。

**3) 在论文中的作用**：该表是方法验证的关键支撑——在系统效率（图6消融的吞吐优化）之外，证明AReaL异步RL范式在数学推理任务上保持了与同步RL相当甚至更优的最终性能，强化了"效率-效果兼得"的核心论点。

### Table 7 (p.26) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab07.png]]
> [!quote] caption
> Staleness-throughput trade-off on small-scale academic setup.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 7 图文联合解读**

该表以 DeepSeek-Distilled-Llama-8B 为基线，对比 AReaL 在两个超参设置（η=4 与 η=8）下于 AIME24/AMC23/MATH500/AIME25 四项数学基准上的准确率：基线 50.4/84.2/89.1/23.3；η=4 提升至 58.4/92.3/92.2/42.6；η=8 仍达 57.2/91.5/91.9/41.6。

**关键结论**：在小型学术配置（DeepSeek-Qwen-1.5B、8k 上下文、batch 64×16、8 GPU）下，将 η（staleness）从 4 翻倍至 8，性能仅下降约 1 个百分点，表明 AReaL 对异步带来的陈旧性高度鲁棒，与大规 Table 2 的结论一致。

**作用**：在小规模下复现 staleness–throughput 权衡实验，验证了系统对异步陈旧性的容忍度，为大规工业部署中提高吞吐量（允许更大 η）提供了可推广的实证支撑。

### Table 8 (p.26) ⭐深度解读
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-tab08.png]]
> [!quote] caption
> Staleness-throughput trade-off using RLOO algorithm. Model AIME24 AIME25 AMC23 MATH500 Throughput

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心内容**：表格对比 DeepSeek-Distilled-Qwen-1.5B 基线与 η∈{0,1,2,4,8,16} 共 6 个 AREAL RLOO 变体在 AIME24、AIME25、AMC23、MATH500 上的准确率及训练吞吐量（k tokens/s）。

**关键结论**：吞吐量随 η 单调上升（27.1k → 52.0k）；准确率 η=4 达峰（AIME24=34.1、AIME25=28.1，MATH500=86.9），η=8 跌至谷底（29.9/23.2），η=16 回升（32.8/25.9）；所有 RL 版本均显著优于无 RL 基线（29.3/24.4）。

**论文作用**：作为附录 C.4 消融，与正文 PPO 陈旧性实验呼应，论证 RLOO 对异步陈旧训练的容忍性优于 PPO，支撑 AREAL 异步 RL 框架可行性的核心论断。

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