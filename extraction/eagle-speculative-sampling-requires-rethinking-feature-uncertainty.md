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
> 【图文联合解读】**图2解读（MT-bench，T=1）**

图2对比EAGLE、Speculative sampling、DistillSpec、Vanilla在Vicuna 7B/13B/33B与LLaMA2-Chat 7B/13B/70B共6个模型上的加速比。**EAGLE全模型稳定取得2.13x–2.68x加速**（7B最低2.13x，13B最高2.68x）；Speculative sampling仅在33B（1.03x）与70B（2.06x）有效，其余N/A；DistillSpec仅70B达1.84x，其余1.00x；Vanilla恒为1.00x基线。

原文借此论证：Lookahead仅支持贪心、Medusa非贪心不保无损，故排除比较；EAGLE基于特征不确定性的建模天然适配采样，在T=1下全模型均获显著无损加速，远超token级投机与蒸馏方法。

该图与表2（接受长度τ、接受率α）共同支撑论文核心论点——**重新思考特征不确定性是推进投机采样的关键**。

### Figure 3 (p.2) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig03.png]]
*整页渲染: ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p02.png]]*
> [!quote] caption
> Uncertainty in feature sequences. The next fea- ture following fI is contingent on the sampling outcome and cannot be determined solely based on fI, where both “always” and “am” are possible to follow the token “I” and lead to two branches.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图3联合解读**

1) **核心结构**：以 token "I" 及其特征 $f_{\text{I}}$ 为根节点（$p_{\text{I}}$：am=0.6, always=0.4），经 sampling 分叉为两条支链——左支 "always"→$f_{\text{always}}$（$p_{\text{begin}}$=0.8, $p_{\text{look}}$=0.2），右支 "am"→$f_{\text{am}}$（$p_{\text{excited}}$=0.3, $p_{\text{ready}}$=0.7），量化展示同一前缀下的双分支概率分布。

2) **关键结论**：仅凭 $f_{\text{I}}$ 无法唯一确定下一特征；下一特征取决于 sampling 结果，由此引出"特征不确定性"概念，挑战 EAGLE 假设特征可确定下一 token 的前提。

3) **论文作用**：作为动机图，揭示自回归特征预测受随机采样影响，为 EAGLE 必须重新思考特征不确定性、改进投机采样策略提供直观论据。

### Figure 4 (p.3) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig04.png]]
*整页渲染: ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p03.png]]*
> [!quote] caption
> Accuracy and speedup ratio of draft models based on tokens, features and feature&shifted-token at tempera- ture=0, tested on MT-bench with Vicuna 7B as the original LLM. Feature&shifted-token refers to using a feature se- quence and a token sequence advanced by one time step as inputs. achieved a speedup ratio of 2.7x-3.5x, doubled through- put, and theoretically guaranteed the preservation of the

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示MT-bench上Vicuna 7B三种draft模型7轮Epoch的Speedup（左）与Acc（右）曲线：feature&shifted-token最优，Speedup从≈1.95升至≈2.75、Acc从≈0.62升至≈0.78；feature次之（≈1.85/0.65）；token最差且几乎停滞（≈1.5/0.30）。

技术结论：纯token或纯特征作draft输入时接受率受限，而"特征序列+超前1拍token序列"双输入消除了采样下f_{t+1}的不确定性，使接受率与加速比同时大幅提升。

论文作用：在ablation层面定量验证EAGLE核心架构（f_t+t_{t+1}双输入）的设计必要性，支撑Vicuna/LLaMA2-70B上2.68×加速比的关键实验结论。

### Figure 5 (p.4) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig05.png]]
*整页渲染: ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p04.png]]*
> [!quote] caption
> A comparison of the methods for drafting the fourth and fifth tokens, t4 and t5. t (represented by blue blocks) denotes tokens, and f (orange blocks) signifies the features, with subscripts indicating their positions in the se- quence. The red border indicates the predictions of the draft model. For simplicity, the n in the n-gram for Lookahead, as shown in the figure, has been set to 2.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图5图文联合解读：**

图示四种推测解码生成 t₄、t₅ 的流程：①**Speculative Sampling** 调用小型 LLM 串行推理；②**Lookahead** 仅以单 token 做 2-Gram/Jacobi 匹配；③**Medusa** 多 Head 共享同一 f₂ 输入，draft 间无信息传递；④**EAGLE** 联合多 token embedding（t₂,t₃）与前序 feature（f₁,f₂），先自回归预测 f₃ 再得 t₄，下轮预测 f₃ 又作输入。

对比揭示前三者局限：仅依赖 token（Lookahead/Spec.Sampling），或忽略 draft 间 feature 不确定性累积（Medusa 所有 head 共用同一 f）。EAGLE 通过"embedding + feature 自回归"兼顾 token 确定性与 feature 上下文性，直观论证其核心动机——**重新思考 feature 不确定性**，为后文 EAGLE 方法展开与实验对比奠定框架。

### Figure 6 (p.4) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig06.png]]
*整页渲染: ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p04.png]]*
> [!quote] caption
> Pipeline of EAGLE. The upper section illustrates the computational process, while the lower section displays the corresponding generation results for each step. In the upper section, green blocks represent token embeddings, or- ange blocks represent features, red boxes indicate the predic- tions of the draft model, and blue modules with snowflake icons represent the use of target LLM parameters, w

> [!tip] 技术解读（多模态）
> 【图文联合解读】图6为EAGLE推测解码流水线。上部计算流：左侧Target LLM将"how can"经Embedding、Transformer Layers、LM Head得首token"can/I"；右侧Draft Model以"One Auto-regression Head"为核心，特征f（橙块）与嵌入e（绿块）联合输入，经Forward 1-3多层预测候选（红框：make/help、a/our等），蓝色雪花模块为冻结的目标LLM参数。下部展示对应生成树：Query"How can"采样得"I"，由FeatExtrapolator逐层外推为多层候选分支。

该图论证：草稿模型以"特征+嵌入"联合输入替代纯嵌入预测，可捕获更深层上下文；冻结目标LLM保证一致性；树状多token采样提升验证吞吐。作为方法总览，为核心论点"特征不确定性需重新思考"提供机制框架，支撑后续实验链路。

### Figure 7 (p.7) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig07.png]]
*整页渲染: ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p07.png]]*
> [!quote] caption
> Speedup ratios of EAGLE with and without the use of tree attention. The evaluation dataset is MT-bench, with the temperature parameter set to 0.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图7联合解读：**

该图量化MT-bench（temp=0）下6个模型的加速比：EAGLE含tree attention为2.78x–3.07x，不含为2.27x–2.66x，Vanilla统一为1.00x。模型覆盖Vicuna 7B/13B/33B与LLaMA2-Chat 7B/13B/70B。

**技术结论：** tree attention在所有模型上稳定带来约0.4–0.5x的额外加速，是EAGLE不可或缺的工程组件；即便剥离该模块，EAGLE仍保持2倍以上加速。

**论文作用：** 作为消融实验，一方证明EAGLE核心的特征不确定性预测机制独立有效（无需tree attention亦显著超越Vanilla），另一方面量化tree attention对端到端加速的边际贡献，为"EAGLE+tree attention"完整方案提供实证支撑。

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
> 【图文联合解读】**图文联合解读：**

1）**核心数据**：表1展示EAGLE在HumanEval、GSM8K、Alpaca三任务、Vicuna/LLaMA2-Chat共六模型、两种温度下的加速比与平均接受长度τ。T=0时加速2.78x–3.76x、τ≈3.61–4.52；T=1时降至2.21x–2.92x、τ≈3.29–3.79。大模型（如LC13B/70B）加速更显著。

2）**关键结论**：原文借此论证①EAGLE在多任务多模型上均稳定取得约2.2–3.8倍加速；②低温度（τ更高）下加速更明显，呼应"特征不确定性越低、接受率越高"的核心论点。

3）**论文作用**：与Figure 1（MT-bench基线对比）互补，构成实验链路——先证可行性，再在跨基准/跨模型/跨温度维度量化收益，支撑"重思特征不确定性"的方法论主张。

### Table 2 (p.6) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-tab02.png]]
> [!quote] caption
> Average acceptance length τ and acceptance rate α on MT-bench. T denotes temperature.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表2核心内容**：在 MT-bench 上对比 6 个模型（Vicuna 7B/13B/33B 与 LLaMA2-Chat 7B/13B/70B）在 T=0（贪心）与 T=1（采样）下的平均接受长度 τ 及 0–4 步接受率。T=0 时 τ∈[3.62, 3.98]、首步 0-α≈0.74–0.79、第 4 步仍≥0.64；T=1 时 τ∈[3.17, 3.46]、各步 α 缓慢衰减至 0.64 上下。

**论证的关键结论**：跨 7B–70B 全部模型、两种温度，τ 均稳定在 3.2–4.0 区间且高阶 α 衰减平缓，直接反驳"特征不确定性会损害投机采样"的疑虑，证明 EAGLE 的草稿模型对不同规模、采样设置均鲁棒。

**在论文中的作用**：作为支撑 Fig.2 加速比与无偏性论证的底层依据——接受长度与各步 α 是投机采样理论加速比（≈τ·R/(τ+验算)）的核心因子，验证了方法在大模型/非贪心场景下仍保持有效加速，是 EAGLE 通用性证据链的关键一环。

### Table 3 (p.6) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-tab03.png]]
> [!quote] caption
> Speedup ratio, average acceptance length τ , and acceptance rate α on MT-bench at temperature=0. The target LLM is Mixtral 8x7B Instruct-v0.1.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 3 展示在 MT-bench（温度=0）、目标模型为 Mixtral 8x7B Instruct-v0.1 时 EAGLE 的实测表现：加速比 1.50×、平均接受长度 τ=3.25、位置 0–4 的接受率 α 分别为 0.67、0.62、0.61、0.64、0.63。

原文借此论证关键结论：相较 LLaMA 等稠密模型，Mixtral 仅获 1.5× 加速，主要归因于 τ 偏短以及 MoE 模型在推测采样下的实现复杂度——MoE 需读取全部专家权重，限制了草稿模型的有效推测深度。

该表在论文实验链路中起量化锚点作用：把前文"特征序列具有采样依赖不确定性"的理论分析（图 3）落到具体数字上，揭示不确定性导致 α 较低且 τ 难以拉长，从而制约了 MoE 场景下推测采样的加速上限，呼应标题"rethinking feature uncertainty"的核心主张。

### Table 4 (p.6) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-tab04.png]]
> [!quote] caption
> Generation speed of EAGLE combined with gpt- fast, evaluated on MT-bench with LLaMA2-Chat 7B at temperature=0.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读**

表4展示 EAGLE 与 gpt-fast 推理框架结合，在 LLaMA2-Chat 7B（温度=0，MT-bench）上的生成加速效果：整体 **Speedup=1.50x**，平均接受长度 **τ=3.25**，且 0-α 至 4-α 各深度的接受率依次为 **0.67 / 0.62 / 0.61 / 0.64 / 0.63**，随位置几乎不衰减、始终高于 0.6。

原文借此论证两点：(1) EAGLE 的「特征 + 超前 token」输入设计有效消除了采样下 f_{t+1} 的不确定性，即使在 greedy 设置和轻量推理栈中仍能保持高接受率与稳定长度；(2) 该表在论文中作为**兼容性 / 可移植性证据**，呼应 Fig.4 的架构核心，证明 EAGLE 并非绑定特定框架，且在 7B 规模下亦能获得 ~1.5× 加速，与 Vicuna / LLaMA2-70B 上 2.68× 的旗舰结果形成完整证据链。

### Table 5 (p.7) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-tab05.png]]
> [!quote] caption
> Average acceptance length τ of EAGLE with and without the use of tree attention. The evaluation dataset is MT-bench, with the temperature parameter set to 0.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 联合解读**

1) **核心数据**：表5在MT-bench、temp=0下对比EAGLE有无树注意力的平均接受长度τ。Vicuna 7B/13B/33B：Chain 3.20/3.23/2.97 → Tree 3.94/3.98/3.68；LLaMA2-Chat 7B/13B/70B：Chain 3.00/3.18/3.12 → Tree 3.62/3.90/3.81。树注意力普遍带来 **+0.62~+0.75** 的稳定增益。

2) **关键结论**：相比单链Chain，树结构验证能并行检验多条草稿路径并选出最长匹配前缀，从而显著提升每次验证通过的token数，验证了树注意力是EAGLE加速的关键设计。

3) **论文作用**：作为消融实验之一，定量证明树注意力独立贡献，排除"仅靠特征预测即可提速"的误解，与Figure 5等机制图共同支撑EAGLE"特征不确定性+树验证"的整体方法链路。

### Table 6 (p.7) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-tab06.png]]
> [!quote] caption
> The speedup ratios and average acceptance length τ using different training datasets evaluated on the MT-bench, with the target LLM being LLaMA2-Chat 7B and the tem- perature set to 0. “Fixed dataset” refers to both questions and answers originating from the ShareGPT dataset. “Data generated by targ

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 图文联合解读：**

**1) 核心对象与数据：**
该表对比了 EAGLE 草案模型在两种训练数据配置下的性能，评测基准为 MT-bench，目标 LLM 为 LLaMA2-Chat 7B，温度 T=0。结果显示：① Fixed dataset（ShareGPT 的问答对）：Speedup=2.78×，平均接受长度 τ=3.62；② Data generated by target LLM（ShareGPT 问题 + 目标 LLM 生成答案）：Speedup=2.88×，τ=3.75。

**2) 关键技术结论：**
当训练答案由目标 LLM 自身生成（分布与推理阶段一致）时，Speedup 提升约 3.6%（2.78×→2.88×），τ 同步提升（3.62→3.75）。这印证了论文"特征不确定性"的核心论点——训练数据的分布与目标模型输出一致，可降低 EAGLE 草案模型预测的"特征不确定性"，从而拉长有效接受长度、提升投机采样加速比。

**3) 在论文中的作用：**
Table 6 是一项消融实验，验证训练数据选择的合理性。它为 EAGLE 后续主要结果提供了数据构建依据（采用 target LLM 自身生成数据训练），同时表明 EAGLE 对数据分布相对鲁棒，但分布对齐会带来稳定增益，支撑了"重思考特征不确定性"这一方法论主张。

### Table 7 (p.8) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-tab07.png]]
> [!quote] caption
> Speedup ratios at different batch sizes and through- put of EAGLE. The evaluation dataset is MT-bench, with the temperature parameter set to 0.

> [!tip] 表格解读（多模态）
> 【图文联合解读】## Table 7 图文联合解读

**核心数据与结构**：表格展示 EAGLE 在 MT-bench（temperature=0）上的加速比，按 batch size 1–4 及吞吐量（Throughput）两维度对比 Vicuna 7B 与 LLaMA2-Chat 70B。Vicuna 7B 分别为 2.90× / 2.87× / 2.65× / 2.76×，吞吐量 1.97×；LLaMA2-Chat 70B 为 3.01× / 2.81× / 2.50× / 2.40×，吞吐量 1.99×。

**关键技术结论**：
1. **跨 batch 鲁棒性**：70B 模型在小 batch 时加速最显著（bs=1 达 3.01×），但随 batch 增大加速比下降（→ 2.40×），反映大模型在批处理并行下推测收益被摊薄；7B 模型各 batch 加速比稳定在 2.65–2.90×，鲁棒性更强。
2. **真实服务收益**：两种模型吞吐量均稳定在约 2×（1.97× / 1.99×），证明 EAGLE 不只是单请求加速，更能带来整体吞吐近翻倍。

**在论文中的作用**：该表属于消融/扩展实验，与 Figure 7（树注意力）互补，从"批量与吞吐"角度进一步验证 EAGLE 在不同部署规模下均保持 ~2–3× 加速，巩固其作为实用化推测解码方案的核心结论。

### Table 8 (p.13) ⭐深度解读
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-tab08.png]]
> [!quote] caption
> Speedup ratio, average acceptance length τ and acceptance rate α on HumanEval, GSM8K, and Alpaca at temperature = 0.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 图文联合解读**

**1) 核心对象与数据**：表格报告 EAGLE 推测解码在温度=0 时，于 HumanEval/GSM8K/Alpaca 三基准上对 6 个目标模型（Vicuna 7B/13B/33B 与 LLaMA2-Chat 7B/13B/70B）的加速比、平均接受长度 τ、以及 0-α–4-α（分别对应 0–4 个不精确特征的接受率）。HumanEval 加速 3.17–3.76x、τ≈4.24–4.52、0-α≈0.81–0.85；GSM8K 加速 2.91–3.25x、τ≈3.82–4.03；Alpaca 加速 2.78–3.03x、τ≈3.61–3.95。随模糊特征数增加，α 单调下降幅度约 0.05–0.15。

**2) 关键论证结论**：确定性解码下 EAGLE 在代码、数学、开放生成三类任务上普遍获得 ≥2.78x 加速；接受率对少量特征失真仍保持较高水平，说明其对自投机模型引入的特征不确定性具有鲁棒性，验证"需重新思考特征不确定性"的设计必要性。

**3) 在论文链路中的作用**：与 Fig.8（MT-bench 上的输入扰动实验）互补——Table 8 提供标准基准的总体性能全景，Fig.8 剖析扰动机制，两者共同支撑论文核心论点。

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