---
paper_num: "4"
title: "EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty"
authors: "Yuhui Li♠ Fangyun Wei‡ Chao Zhang♠ Hongyang Zhang♣† ♠Peking University ‡Microsoft Research ♣University of Waterloo †Vector Institute hongyang.zhang@uwaterloo.ca Vicuna 7B Vicuna 13B Vicuna 33B LLaMA2-Chat 7B LLaMA2-Chat "
date: "2026/6/29"
arxiv: "https://arxiv.org/abs/2401.15077"
pdf: "papers/eagle-speculative-sampling-requires-rethinking-feature-uncertainty.pdf"
slug: "eagle-speculative-sampling-requires-rethinking-feature-uncertainty"
tags: [speculative]
---

# EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty

> [!abstract] 摘要（原文）
> 1\. 🦅 EAGLE是一种高效的Speculative Sampling框架，其核心创新在于在特征（第二顶层）层面进行自回归，并通过引入提前一个时间步的Token序列来解决特征预测中的不确定性。 2. ⚡️ 实验结果表明，EAGLE在LLaMA2-Chat 70B上实现了2.7x-3.5x的推理速度提升， throughput 翻倍，且理论上保证了生成文本的分布不变性。 3. 💡 EAGLE具有出色的通用性和可靠性，无需对原始LLM进行微调即可应用于多种模型和任务，并与现有加速技术（如gpt-fast）兼容，显著降低了LLM系统的运行成本。

## 元信息
- **发表日期**: 2026/6/29
- **作者**: Yuhui Li♠ Fangyun Wei‡ Chao Zhang♠ Hongyang Zhang♣† ♠Peking University ‡Microsoft Research ♣University of Waterloo †Vector Institute hongyang.zhang@uwaterloo.ca Vicuna 7B Vicuna 13B Vicuna 33B LLaMA2-Chat 7B LLaMA2-Chat 
- **arXiv**: https://arxiv.org/abs/2401.15077
- **本地 PDF**: `papers/eagle-speculative-sampling-requires-rethinking-feature-uncertainty.pdf`
- **页数**: 13

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig01.png]]
*整页渲染: ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p01.png]]*
> [!quote] caption
> Speedup ratio of Vicuna and LLaMA2-Chat inference latency on the MT-bench for greedy (temperature=0) settings. Speedup ratio of Medusa and Lookahead are copied from their original technical reports. With speculative sampling, there is a lack of suitable draft models to accelerate the 7B model. Employing a 7B model as the draft model for a 13B model results in slow speeds due to the high overhead o

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图1展示MT-bench贪心解码下，6个模型（Vicuna 7B/13B/33B、LLaMA2-Chat 7B/13B/70B）相对Vanilla（1.00x基线）的推理加速比。EAGLE以2.78x–3.07x全面领先且稳定在~3倍；Medusa约1.92–1.97x、Lookahead约1.45–1.64x；传统Speculative sampling因无合适draft model，7B/13B均标N/A，仅33B（1.27x）、70B（1.88x）可用且显著低于EAGLE；DistillSpec仅适用于LLaMA2-Chat 70B（2.13x）。

该图作为开篇核心motivation，量化揭示现有无损加速方法在中小模型上"无draft可用"或加速有限的瓶颈，直接支撑后文提出基于"重思feature uncertainty"的EAGLE方案——无需微调backbone即可在所有规模模型上取得一致且最高的加速比。

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig02.png]]
*整页渲染: ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p02.png]]*
> [!quote] caption
> Speedup ratio on the MT-bench for non-greedy (temperature=1) settings. Lookahead is confined to greedy decoding, and the non-greedy generation of Medusa does not guarantee lossless performance. Therefore, EAGLE is not compared with these methods. I 𝑓I 𝑝(am)=0.6 𝑝(always)=0.4 sampling am 𝑓am 𝑝(excited)=0.3 𝑝(ready)=0.7 sampling always 𝑓always 𝑝(begin)=0.8 𝑝(look)=0.2 𝑝always 𝑝I 𝑝am

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 2）**

**1) 核心对象与数据**
该柱状图展示了在 MT-bench 上 **temperature=1（非贪心采样）** 设置下，EAGLE 与 Speculative sampling（SS）、DistillSpec（DS）、Vanilla 在 6 个模型上的加速比。EAGLE 在 Vicuna 7B/13B/33B、LLaMA2-Chat 7B/13B/70B 上分别取得 **2.13× / 2.32× / 2.40× / 2.22× / 2.68× / 2.67×** 的稳定加速；SS 与 DS 仅在 Vicuna 33B（1.22×、1.09×）和 LLaMA2-Chat 70B（2.06×、1.84×）上有数据，其余模型标记为 N/A。

**2) 关键论证结论**
图中数据直接支撑三点：（a）EAGLE 在非贪心采样下仍保持 **2.1×–2.7×** 的无损加速，覆盖全部 6 个模型；（b）在两类基线可比的设置中，EAGLE 均 **显著优于** SS 与 DS；（c）Lookahead 受限于贪心解码、Medusa 在非贪心下不能保证无损，故被排除对比——这反衬出 EAGLE 在真实采样场景下的适用性优势。

**3) 在论文整体链路中的作用**
该图属于实验核心证据之一，与 Table 2 的接受长度/接受率互补，共同证明 EAGLE 不仅在贪心设置（Fig.1）有效，在更具实用性的采样生成中同样具备 **普适性、无损性与稳定性**，是其"重新思考特征不确定性"方法主张的关键支撑。

### Figure 3 (p.2) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig03.png]]
*整页渲染: ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p02.png]]*
> [!quote] caption
> Uncertainty in feature sequences. The next fea- ture following fI is contingent on the sampling outcome and cannot be determined solely based on fI, where both “always” and “am” are possible to follow the token “I” and lead to two branches.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（图3）：**

图3展示特征不确定性结构：中心 token "I" → f_I（p_I: p(am)=0.6, p(always)=0.4），经红色虚线"采样"分叉为两条分支——左支"always"→f_always（p(begin)=0.8, p(look)=0.2），右支"am"→f_am（p(excited)=0.3, p(ready)=0.7）。**核心论证**：f_I 之后的下一特征无法由 f_I 唯一确定，必须依赖实际采样结果，从而形成带不同概率分布的分支链，颠覆了先前工作将特征序列视为确定性链的假设。**论文作用**：该图是 EAGLE 重写特征预测头、显式建模特征不确定性的理论起点，支撑其在 Figure 2 中于 Vicuna/LLaMA2-Chat 7B/13B/33B/70B 上实现 2.13x–2.68x 的加速比。

### Figure 4 (p.3) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig04.png]]
*整页渲染: ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p03.png]]*
> [!quote] caption
> Accuracy and speedup ratio of draft models based on tokens, features and feature&shifted-token at tempera- ture=0, tested on MT-bench with Vicuna 7B as the original LLM. Feature&shifted-token refers to using a feature se- quence and a token sequence advanced by one time step as inputs. achieved a speedup ratio of 2.7x-3.5x, doubled through- put, and theoretically guaranteed the preservation of the

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图4 联合解读：**

图4展示三类draft模型（token、feature、feature&shifted-token）在MT-bench/Vicuna 7B、temperature=0下，随训练epoch（1–7）变化的加速比（左）与预测准确率（右）。定量结果：feature&shifted-token加速比由≈2.0升至≈2.7，准确率由≈0.62升至≈0.78；feature居中（加速≈1.5→1.85，准确率≈0.55→0.65）；token最差（加速≈1.4→1.5，准确率仅≈0.25→0.30），三者差距随训练扩大。

该图论证EAGLE核心设计——draft模型同时输入特征序列与前移一步的token序列，显著优于纯token或纯特征方案，验证"特征不确定性须结合下一token联合建模"的关键假设。

在论文方法链中，本图作为消融实验，为EAGLE架构合理性提供直接证据，并支撑后续在LLaMA2-Chat等更大模型上实现2.7×–3.5×加速（Table 4）的结论。

### Figure 5 (p.4) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig05.png]]
*整页渲染: ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p04.png]]*
> [!quote] caption
> A comparison of the methods for drafting the fourth and fifth tokens, t4 and t5. t (represented by blue blocks) denotes tokens, and f (orange blocks) signifies the features, with subscripts indicating their positions in the se- quence. The red border indicates the predictions of the draft model. For simplicity, the n in the n-gram for Lookahead, as shown in the figure, has been set to 2.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图5联合解读**

图5对比Medusa（左）与EAGLE（右）生成t₄、t₅的机制（Lookahead的n取2）：Medusa仅用单一f₂经两个并行Head直接预测t₄、t₅；EAGLE则采用**级联自回归**——先用[t₂,t₃,f₁,f₂]经嵌入+自回归头预测f₃，再由f₃预测t₄；继而将t₄反馈，连同[t₂,t₃,f₁,f₂]预测f₄，再得t₅。蓝块=token，橙块=feature，红框=草稿预测。

该图直观论证EAGLE把已生成token回灌至下一轮特征预测，**降低了特征不确定性**这一核心技术结论（呼应论文标题"speculative sampling requires rethinking feature uncertainty"）。它作为方法论核心图示，衔接Table 5关于EAGLE接受长度τ的量化验证，构成"机制示意→实证增益"的完整论证链。

### Figure 6 (p.4) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig06.png]]
*整页渲染: ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p04.png]]*
> [!quote] caption
> Pipeline of EAGLE. The upper section illustrates the computational process, while the lower section displays the corresponding generation results for each step. In the upper section, green blocks represent token embeddings, or- ange blocks represent features, red boxes indicate the predic- tions of the draft model, and blue modules with snowflake icons represent the use of target LLM parameters, w

> [!tip] 技术解读（多模态）
> 【图文联合解读】**Figure 6 图文联合解读**

① **核心结构**：上图展示 EAGLE 三步推理流水线——目标 LLM（Forward 1，带雪花标记的蓝色模块即冻结参数）输出特征 f_how、f_can，Draft model 经 Forward 1→2→3 复用 Embedding 层与 LM Head，中间仅训练一个 "One Auto-regression Head" 在特征层自回归，逐次预测 f_I→f_make→f_with→f_you，再经 LM Head 与"Sampling multiple times"并行生成候选树（"I"/"make/help"等）。下图以"How can"为 Query 画出树状生成结构：经 FeatExtrapolator 一次产出多层分支 token。

② **论证结论**：EAGLE 区别于 Speculative Sampling/Lookahead 的 token 级预测及 Medusa 的单特征多 head 预测，转而在**特征序列**上做自回归，并冻结目标 LLM 的 Embedding 与 LM Head 仅训练轻量 auto-regression head，实现高效并行 draft。

③ **论文作用**：作为方法总图，配合 Figure 5 横向对比，奠定 §3.1 drafting phase 的核心叙事，为后续 Table 6 等加速比实验提供架构依据。

### Figure 7 (p.7) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig07.png]]
*整页渲染: ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p07.png]]*
> [!quote] caption
> Speedup ratios of EAGLE with and without the use of tree attention. The evaluation dataset is MT-bench, with the temperature parameter set to 0.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**Figure 7 图文联合解读**

**1) 核心数据**：在 MT-bench（temperature=0）上对比三种方案在 6 个 LLM（Vicuna 7B/13B/33B 与 LLaMA2-Chat 7B/13B/70B）上的加速比。EAGLE w/ tree attention（蓝）范围 **2.78×–3.07×**（最高 Vicuna 13B 的 3.07×、LLaMA2-Chat 13B 的 3.03×）；EAGLE w/o tree attention（绿）为 **2.27×–2.66×**；Vanilla（橙）统一为 1.00×。可见树注意力在每个模型上稳定额外贡献约 **0.30×–0.51×**。

**2) 关键结论**：树注意力（tree attention）不是装饰性组件，而是 EAGLE 获得最高加速比的关键——它使所有 6 个模型、跨越 7B–70B 的不同规模均获得一致且显著的进一步提速，论证了"为投机解码构造层级/树形 KV 计算"这一设计取舍的正确性。

**3) 在论文中的作用**：该图属于消融/组件贡献类实验，与 Table 7（不同 batch size、吞吐量下的加速比）共同支撑"EAGLE 各核心模块（特征不确定性预测 + 树注意力）均不可或缺"的主线，为论文方法论提供经验性证据。

### Figure 8 (p.8) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig08.png]]
*整页渲染: ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p08.png]]*
> [!quote] caption
> Performance of draft models with varying inputs. The target LLM is Vicuna 7B, and the test dataset is MT-bench.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（≤220字）：**

图8以Vicuna-7B/MT-bench为基准，在2×4网格（行：T=0/1；列：Speedup/τ/0-α/1-α）中对比四种draft输入。量化显示：feature&shifted-token（蓝线）在所有指标全面最优——T=0时加速比≈2.7×、τ≈3.7、0-α≈0.78、1-α≈0.68；T=1时加速比≈2.0×、τ≈3.0；纯token（绿）始终最差，纯feature（红）次之，且其0-α/1-α明显低于双输入方案。

**论证结论**：draft模型必须同时利用目标LLM的下一层feature与偏移后的token，二者缺一不可；token偏移是显著提升接受率τ与walltime加速的关键。

**链路作用**：直接验证EAGLE核心架构选择——"feature + shifted-token"输入是其投机采样相对纯token基线实现显著加速（约2.7×）的根因，构成论文方法主张的关键实验证据。

### Figure 9 (p.12) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig09.png]]
*整页渲染: ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p12.png]]*
> [!quote] caption
> However, the optimal tree structure is likely context-dependent. For instance, as batch size increases and redundant computational resources decrease, a smaller tree might be preferable. Tuning the draft structure could potentially lead to improved performance. query query

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示 EAGLE 草稿的两类计算拓扑：左图启用树注意力，以 1 个“query”为根，连同 22 个候选共 23 个节点（最长 5 步），可同时处理多条分支路径；右图无树注意力，仅为“query＋5 个 token”的 6 节点单链。论文指出，最优树形依赖上下文；批量增大、冗余计算浪费减少时，较小的树可能更优。该图位于“草稿生成—主模型验证”链路，揭示并行收益与注意力开销的权衡。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.6) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-tab01.png]]
> [!quote] caption
> Speedup ratio and average acceptance length τ on HumanEval, GSM8K, and Alpaca. T denotes temperature, V represents Vicuna, and LC stands for LLaMA2-Chat.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表1比较T=0/1时Vicuna 7B/13B/33B与LLaMA2-Chat 7B/13B/70B在HumanEval、GSM8K、Alpaca上的加速比和平均接受长度τ。六个模型在三个任务上的加速为2.29×–3.76×，τ为3.29–4.52；T=0各项均高于T=1，LC-13B在HumanEval最高（3.76×、4.52）。该表跨模型、温度和任务验证EAGLE能将高接受率转化为稳定约3倍加速，承接Figure 1对草稿模型选择成本的分析，支撑“利用低不确定性特征突破传统投机采样瓶颈”的核心主张。

### Table 2 (p.6) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-tab02.png]]
> [!quote] caption
> Average acceptance length τ and acceptance rate α on MT-bench. T denotes temperature.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 联合解读**

**1) 核心对象与数据**：表格列出6个模型（Vicuna 7B/13B/33B与LLaMA2-Chat 7B/13B/70B）在MT-bench上的平均接受长度τ及各阶接受率α（0-α至4-α）。T=0时τ在3.62–3.98，0-α达0.74–0.79；T=1时τ降至3.17–3.46，0-α为0.71–0.73；随阶数增加，接受率缓慢衰减，但4-α仍维持在0.64–0.71，说明EAGLE对多token draft的预测依然稳健。

**2) 关键论证**：印证"特征不确定性建模"有效——即便温度升高使分布更分散，EAGLE的draft token仍以高概率被目标模型接受，且每多draft一个token仅带来小幅α下降，从而保证τ较长。

**3) 实验链路作用**：与Figure 2（非贪心速度比）形成"微观接受率—宏观加速比"互补，共同支撑EAGLE在T=1下仍可无损加速的核心结论。

### Table 3 (p.6) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-tab03.png]]
> [!quote] caption
> Speedup ratio, average acceptance length τ , and acceptance rate α on MT-bench at temperature=0. The target LLM is Mixtral 8x7B Instruct-v0.1.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **表格结构与数据**：单行展示7个核心指标——加速比1.50x、平均接受长度τ=3.25、5个位置的接受率α（0-α至4-α依次为0.67/0.62/0.61/0.64/0.63）。实验条件为MT-bench、temperature=0，目标LLM为Mixtral 8x7B Instruct-v0.1。

2) **关键结论**：τ=3.25却仅获得1.50x加速，加速效率明显受限；各位置接受率稳定在0.61–0.67且未显著衰减。这与论文核心论点（图3所示的特征序列不确定性——下一特征依赖采样结果，存在多分支可能）相互印证：drafter难以精准预测后续特征，制约了EAGLE类投机采样的效率上限，需重新思考特征不确定性建模。

3) **论文作用**：作为定量实验证据，串联"特征不确定性→投机采样效率受限→方法需重构"的论证链，为作者后续改进方案提供baseline对照。

### Table 4 (p.6) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-tab04.png]]
> [!quote] caption
> Generation speed of EAGLE combined with gpt- fast, evaluated on MT-bench with LLaMA2-Chat 7B at temperature=0.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读：**

Table 4 报告 EAGLE 与 gpt-fast 结合后，在 MT-bench 上以 LLaMA2-Chat 7B 为基模型、温度=0 时的生成速度：整体加速比 **1.50x**，参数 τ=3.25；自回归步数 α 从 0 到 4 对应的指标值依次为 0.67、0.62、0.61、0.64、0.63，仅在 0.61–0.67 区间小幅波动，未随 α 增大而显著退化。

该表作为 Figure 4（Vicuna 7B 上 2.7x–3.5x 加速）的**跨模型对照验证**：在更换基模型（LLaMA2-Chat vs Vicuna）与推理栈（gpt-fast）后，EAGLE 仍维持稳定加速，且随 α 增大无明显质量损失，从而支撑论文核心结论——基于"特征+偏移 token"的草稿机制具有**模型/框架无关的通用加速能力**，而非依赖特定模型的偶然现象。

（约 210 字）

### Table 5 (p.7) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-tab05.png]]
> [!quote] caption
> Average acceptance length τ of EAGLE with and without the use of tree attention. The evaluation dataset is MT-bench, with the temperature parameter set to 0.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 图文联合解读**

该表对比了 EAGLE 在 MT-bench（温度=0）上，链式（Chain）与树状（Tree）注意力两种草稿解码方式下的平均接受长度 τ，涵盖 Vicuna（7B/13B/33B）与 LLaMA2-Chat（7B/13B/70B）共 6 个模型。

**量化结果**：所有模型 Tree 严格优于 Chain：Vicuna 7B/13B/33B 由 3.20/3.23/2.97 提升至 3.94/3.98/3.68（+0.71~+0.75）；LLaMA2-Chat 7B/13B/70B 由 3.00/3.18/3.12 提升至 3.62/3.90/3.81（+0.62~+0.69），增益稳定在 0.6–0.75 之间，且与模型规模无明显相关性。

**论证结论**：Tree attention 通过一次性并行验证多条候选 token 序列，显著提高草稿被主模型接受的长度，直接降低推理步数。

**论文作用**：该表为 EAGLE 的核心模块（tree-attention 草稿机制）提供了端到端的有效性证据，与图 5 的机制示意互补——前者讲原理，后者用量化的 τ 增益验证其加速收益，支撑论文"EAGLE 通过特征层投机 + 树状解码取得显著加速"的总体结论。

### Table 6 (p.7) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-tab06.png]]
> [!quote] caption
> The speedup ratios and average acceptance length τ using different training datasets evaluated on the MT-bench, with the target LLM being LLaMA2-Chat 7B and the tem- perature set to 0. “Fixed dataset” refers to both questions and answers originating from the ShareGPT dataset. “Data generated by targ

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 解读**

1）核心对象：MT-bench（温度=0，目标模型LLaMA2-Chat 7B）上两种训练数据策略的EAGLE推测解码效果对比。结构为2行数据：①固定数据集（Q&A均来自ShareGPT）→Speedup 2.78x、τ=3.62；②目标LLM生成数据（Q来自ShareGPT，A由目标LLM生成）→Speedup 2.88x、τ=3.75。

2）关键结论：当训练答案由目标LLM自行生成时，Speedup提升约0.10x、τ提升约0.13，说明训练数据的分布与目标模型对齐能改善草稿模型的特征预测质量。

3）论文作用：该表属于EAGLE实验链路中的**数据消融环节**，验证了"草稿模型训练数据需贴合目标模型分布"的设计原则，为后续主实验提供数据构造依据。

### Table 7 (p.8) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-tab07.png]]
> [!quote] caption
> Speedup ratios at different batch sizes and through- put of EAGLE. The evaluation dataset is MT-bench, with the temperature parameter set to 0.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 7 图文联合解读**

**① 表的核心内容**：该表在 MT-bench（temperature=0）上展示 EAGLE 加速比随 batch size 的变化，并给出吞吐加速。Vicuna 7B 在 batch=1/2/3/4 下分别为 2.90x、2.87x、2.65x、2.76x，吞吐 1.97x；LLaMA2-Chat 70B 为 3.01x、2.81x、2.50x、2.40x，吞吐 1.99x。

**② 关键结论**：两模型均在 batch=1 时取得峰值加速（70B 达 3.01x），随着 batch 增大加速比整体下降（70B 降至 2.40x），说明推测采样在低并发场景收益最大；且逐请求加速（2.4–3.0x）显著高于吞吐加速（~2x），表明批并行部分抵消了推测带来的延迟优势。

**③ 在论文中的作用**：该表作为消融/扩展实验，与 Figure 7（tree attention 对比）并列，验证 EAGLE 在不同部署规模（7B/70B）和并发度下的鲁棒性，为"投机采样需重思特征不确定性"提供实证支撑。

### Table 8 (p.13) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-tab08.png]]
> [!quote] caption
> Speedup ratio, average acceptance length τ and acceptance rate α on HumanEval, GSM8K, and Alpaca at temperature = 0.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**1) 核心对象与结构**
Table 8 在温度=0下，列示 EAGLE 在 HumanEval、GSM8K、Alpaca 三个数据集上，对 Vicuna 7B/13B/33B 与 LLaMA2-Chat 7B/13B/70B 共六个目标模型的加速比、平均接受长度 τ 与 0-α~4-α 多档接受率。HumanEval 加速 3.17x–3.76x、τ≈4.24–4.52；GSM8K 加速 2.91x–3.25x、τ≈3.82–4.03；Alpaca 加速 2.78x–3.03x、τ≈3.61–3.83；0-α 接受率集中在 0.70–0.85，并随档位递增逐档递减。

**2) 关键技术结论**
跨代码、数学、对话三类任务与 7B–70B 全规模，EAGLE 均稳定取得 2.7–3.8x 加速、τ≥3.6，表明其对特征不确定性的处理具备良好的任务与模型泛化能力。

**3) 在论文中的实验链路作用**
该表作为"全场景基准"实验，与 Figure 8 (MT-bench) 等补充实验串联，构成 EAGLE 在加速比与接受率维度上的完整验证链，支撑论文"重新审视特征不确定性可提升推测采样"的核心论点。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
L_{reg} = \text{Smooth L1}(f_{i+1}, \text{Draft\_Model}(T_{2:i+1}, F_{1:i})).
$$

$$
{p}_{i+2}=\text{Softmax}(\text{LM\_Head}({f}_{i+1})), \\ \hat{p}_{i+2}=\text{Softmax}(\text{LM\_Head}(\hat{f}_{i+1})), \\ L_{cls} = \text{Cross\_Entropy}({p}_{i+2},\hat{p}_{i+2}).
$$

## 相关论文

- [[dflash-block-diffusion-for-flash-speculative-decoding]] — DFlash: Block Diffusion for Flash Speculative Decoding
- [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] — DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation
- [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]] — EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees
- [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] — LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and Verification
- [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] — SpecExtend: A Drop-in Enhancement for Speculative Decoding of Long Sequences
- [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] — JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting

## 技术点深读（DEEP）

![[deep/eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/eagle-speculative-sampling-requires-rethinking-feature-uncertainty.txt`（50318 字符）供引用检索。