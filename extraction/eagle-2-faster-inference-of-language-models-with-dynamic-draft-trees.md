---
paper_num: "5"
title: "EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees"
authors: "Yuhui Li♠ Fangyun Wei‡ Chao Zhang♠ Hongyang Zhang♣† ♠Peking University ‡Microsoft Research ♣University of Waterloo †Vector Institute hongyang.zhang@uwaterloo.ca"
date: "2024/6/24"
arxiv: "https://arxiv.org/abs/2406.16858"
pdf: "papers/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees.pdf"
slug: "eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees"
tags: [speculative]
---

# EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees

> [!abstract] 摘要（原文）
> 1\. 🚀 EAGLE-2 提出了一种基于上下文的动态草稿树结构，通过利用 draft model 的置信度得分来准确近似标记的接受率，从而突破了静态草稿树的局限性。 2. 💡 该方法在不改变原始 LLM 输出分布的前提下实现了无损加速，无需额外训练即可动态调整草稿树结构，显著提升了推理过程中的 token 接受数量。 3. 📈 在多项生成任务的广泛评估中，EAGLE-2 相比 EAGLE-1 实现了 20%-40% 的进一步提速，在多种主流模型上表现出 3.05x-4.26x 的显著推理加速效果。

## 元信息
- **发表日期**: 2024/6/24
- **作者**: Yuhui Li♠ Fangyun Wei‡ Chao Zhang♠ Hongyang Zhang♣† ♠Peking University ‡Microsoft Research ♣University of Waterloo †Vector Institute hongyang.zhang@uwaterloo.ca
- **arXiv**: https://arxiv.org/abs/2406.16858
- **本地 PDF**: `papers/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees.pdf`
- **页数**: 12

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig01.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p01.png]]*
> [!quote] caption
> Speedup ratios of different methods at tempera- ture=1. For speculative sampling, the Vicuna series uses

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心数据**：该图为温度=1（非贪婪采样）下四种目标模型（Vicuna 7B/13B、LLaMA2-Chat 7B/13B）上三种加速方法的推理加速比对比柱状图。EAGLE-2 分别取得 3.05×、3.80×、3.19×、3.92×，均显著高于 EAGLE（2.13×/2.32×/2.22×/2.68×）和 Speculative sampling（仅 Vicuna 系列为 1.50×、1.62×，LLaMA2-Chat 因无合适 draft 模型标 N/A）。

**2) 关键结论**：在非贪婪设置下，EAGLE-2 相对 EAGLE 仍有 1.4×–1.5× 的提升，验证了"动态 draft tree"机制比静态 draft tree 在采样场景下更优；而 Medusa 等方法因放宽接受条件、无法保证输出分布一致性，故未参与比较。

**3) 论文作用**：作为首页 Figure 1，是 EAGLE-2 方法有效性的"第一印象"证据，与 Figure 2（temperature=0 贪婪场景）互补，共同构成论文对动态 draft 树在两种采样模式下普适加速能力的核心实验支撑。

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig02.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p02.png]]*
> [!quote] caption
> Speedup ratios of different methods at temperature=0. For speculative sampling, the Vicuna series uses Vicuna- 68M as the draft model. LLaMA2-Chat 7B, 13B, and LLaMA3-Instruct 8B lack suitable draft models and are marked as N/A. LLaMA2-Chat 70B and LLaMA3-Instruct 70B use LLaMA2-Chat 7B and LLaMA3-Instruct 8B as draft models, respectively. In Table 1, we present comparisons with additional methods

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图2展示温度=0下，五种加速方法（EAGLE-2、EAGLE、Medusa、Lookahead、Speculative sampling）在7个LLM上的加速比。EAGLE-2在所有模型上均最优：Vicuna 7B/13B为3.62x/4.26x，LLaMA2-Chat 7B/13B/70B为3.43x/4.21x/3.51x，LLaMA3-Instruct 8B/70B为3.46x/3.29x；EAGLE居次（约2.7–3.0x）；Medusa仅适用于Vicuna（约1.9–2.1x）；Lookahead与Speculative sampling分别约1.4–1.6x和1.4–1.9x，且后者在LLaMA2-Chat 7B/13B及LLaMA3 8B上标记N/A。该图作为核心实验证据，验证了动态草稿树相比固定草稿（speculative sampling）和单链扩展（Lookahead）的全面优势，并支撑后续Table 2对大模型τ值与加速比的进一步分析。

### Figure 3 (p.3) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig03.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]]*
> [!quote] caption
> Comparison of standard speculative sampling and EAGLE. For simplicity, EAGLE’s tree-structured draft is shown only in the verification stage, while the illustration of the drafting stage uses a chain-structured draft. Here, ti denotes the i-th token embedding, and fi denotes the i-th feature vector in the second-to-top-layer of LLM before LM head. the token sequence ta, ta+1, · · · , tb. Speculati

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

图3分(a)草稿、(b)验证两阶段对比标准投机采样与EAGLE：(a)中标准法仅以token t₂,t₃串行经"Token自回归草稿模型"生成t₄、t₅；EAGLE额外引入LLM倒数第二层特征f₁,f₂,f₃，作为"特征自回归草稿模型"输入，联合预测f₃→t₄、f₄→t₅。(b)中标准法对链式草稿(t₄,t₅)逐一验证，接受t₄而拒绝t₅；EAGLE采用动态树形草稿（如t₄分叉出t₅,t₆），单次LLM前向即可并行验证多候选，使t₄、t₆同时被接受。该图直观论证了"特征级自回归预测+动态树形草稿验证"是EAGLE-2相较传统投机采样提升接受率、加速推理的核心机制，是后续消融与基准实验的逻辑起点。

### Figure 4 (p.3) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig04.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]]*
> [!quote] caption
> Differences between EAGLE and EAGLE-2. EA- GLE always uses a fixed draft shape. When the query is “10+2=”, the next token is very likely to be correctly pre- dicted as “1”. However, with a static draft tree, EAGLE would still add two candidates, even though the probability of the other candidate “3” being correct is very low. EAGLE- 2, on the other hand, adjusts the shape of draft tree based on th

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 4）：**

1) **核心结构**：图中以"10+2="为查询，分两栏对比——左侧EAGLE从该前缀并行扩展4个同层候选 token（"="、"+"、"1"、"3"），呈固定宽度草稿树；右侧EAGLE-2先输出高置信度 token "1"，再沿"1"向下延伸出"2"，形成动态深度优先的树形分支。

2) **技术结论**：EAGLE的静态树形在"10+2="场景下仍生成低概率候选项"3"，浪费验证开销；EAGLE-2依据草稿模型置信度自适应调整树形（宽→深），将算力集中于高概率路径，提升单次验证接受率。

3) **论文作用**：作为EAGLE-2方法核心创新（Dynamic Draft Tree）的可视化动机图，引出后文基于置信度阈值的动态树构建算法，是连接EAGLE基础框架与EAGLE-2加速方案的桥梁。

### Figure 5 (p.3) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig05.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]]*
> [!quote] caption
> Overall, the acceptance rate of draft tokens is position-dependent, with the highest acceptance rate at position P1 and the lowest at position P6. Draft tokens in the upper left side of the draft tree (such as position P1) have higher acceptance rates, while those in the lower 3

> [!tip] 技术解读（多模态）
> 【图文联合解读】**1) 核心对象与数据：** 图(a)为草稿树结构——Query根节点分支为P1/P2，再分至P3-P6共6个位置；图(b)散点图显示各位置token接受率分布，P1约70%点接近1.0，P2中位数降至约0.3，P3-P6散布明显下移；图(c)排序曲线与y=x虚线对比，中段下凹。

**2) 关键技术结论：** 接受率呈强位置依赖——树上层/左侧(P1)最高，树深层/右侧(P6)最低，验证原文"upper left side…higher acceptance rates"判断。

**3) 论文中作用：** 作为EAGLE-2动态草稿树的核心动机证据，说明EAGLE-1的静态均匀树非最优，应依据各位置历史接受率动态扩展高接受率分支、剪除低接受率分支，从而提升整体加速比。

### Figure 6 (p.4) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig06.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p04.png]]*
> [!quote] caption
> Average acceptance rates for different confidence score intervals of the draft model. The red dashed line connects (0,0) and (1,1) to aid in visual assessment. The original LLM is Vicuna 7B. aspects: how to expand the draft tree (Section 4.1) and how to rerank draft tokens (Section 4.2). During the expansion phase, we input the most promising nodes from the latest layer of the draft tree into the 

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图6（右半）为柱状图，横轴为草稿模型置信度（0–1.0，分箱约20档），纵轴为目标LLM（Vicuna 7B）的实际接受率（0–1.0）。蓝色柱条与红色虚线 y=x 高度贴合：低置信区间（≈0.1）接受率约0.1，中段（≈0.5）约0.5，高置信（≈0.9–1.0）升至0.8–1.0，表明草稿模型置信度与真实接受率呈近线性、校准良好。

**技术结论：** 验证了草稿模型输出的置信分数可作为可靠信号，用于预测哪些draft token易被目标模型接受。

**链路作用：** 该图为第4.1节动态草稿树扩展（挑选高置信节点继续展开）与第4.2节重排序（按置信度加权）提供定量依据，是EAGLE-2"置信驱动"投机解码框架的实证基石。

### Figure 7 (p.5) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig07.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p05.png]]*
> [!quote] caption
> Illustration of EAGLE-2. The numbers beside the edges represent the confidence scores of the draft model, and the numbers in brackets within the blocks represent the value of the nodes. During the expansion phase, we select the top 2 nodes with the highest value from the current layer (orange blocks) as inputs to the draft model and connect the generated tokens (green blocks) to the draft tree. In

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示EAGLE-2两阶段流程：①扩张（Top-2）——以"It(1.0)"为根，按草稿模型置信度（0.6/0.2/0.8/0.1…）动态建树，从当前层选top-2高值节点 a(0.48)、to(0.14) 继续扩展生成绿块子节点 good/nice/be/do；②重排序（Top-8）——对全树节点按值排序后取 [It, is, has, a, the, to, good, be] 展平为1D序列，并配合树状 attention mask，使每 token 仅可见其祖先节点，保证分支互不可见。

该图论证了 EAGLE-2 的核心技术：动态草稿树通过"扩张深化—重排保连通—树状掩码保障并行验证正确性"，在保持 speculative decoding 正确性的同时显著提升接受率与速度，是论文区别于 EAGLE-1（静态树）的关键方法论支撑，也直接服务于 §5 在 Vicuna、LLaMA2/3 多模型上的加速实验。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.7) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-tab01.png]]
> [!quote] caption
> Speedup ratios and average acceptance lengths τ of different methods. V represents Vicuna, L2 represents LLaMA2-Chat. SpS denotes standard speculative sampling, with its draft model being Vicuna-68M. Methods like Medusa relax acceptance conditions under non-greedy settings, which do not guarantee lo

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文联合解读**

**1) 核心对象与结构**：表格在 T=0 与 T=1 两档下，对比 Vicuna/LLaMA2-Chat（7B、13B）在 6 个基准（MT-bench、HumanEval、GSM8K、Alpaca、CNN/DM、Natural Ques.）上的加速比与平均接受长度 τ，涵盖 SpS、PLD、Medusa、Lookahead、Hydra、EAGLE、EAGLE-2 共 7 种方法。量化结果：EAGLE-2 在 V 13B 上 Mean speedup 达 4.04x（τ=4.65，T=0）、3.65x（T=1），V 7B 达 3.39x/2.94x，均为各列最高；HumanEval 单项最高 5.00x（L2 13B, T=0）。

**2) 关键结论**：在保证无损采样的前提下，EAGLE-2 相对 EAGLE 再提升约 30–40%（如 V 7B：2.78x→3.39x），显著优于 Hydra（2.55x）、SpS（1.76x），验证动态草稿树在更长 τ 下仍能保持高接受率。

**3) 论文作用**：作为方法部分提出的核心实验证据，与 Fig.1/2 互补，量化支撑"动态草稿树带来无损加速领先"的全文论点。

### Table 2 (p.8) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-tab02.png]]
> [!quote] caption
> Speedup ratios and average acceptance lengths τ with LLaMA2-Chat 70B, LLaMA3-Instruct 70B, and LLaMA3-Instruct 8B as the original LLMs, with the tem- perature set to 0, on the MT-bench dataset.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

Table 2 在 MT-bench（temp=0）上对比三种原模型下各推测解码方法的加速比与平均接受长度 τ。LLaMA2-Chat 70B 下 PLD 1.31×、Lookahead 1.52×、EAGLE 3.01×(τ=3.81)、**EAGLE-2 3.51×(τ=4.48)**；LLaMA3-Instruct 70B 下 EAGLE 2.83× → EAGLE-2 **3.29×**；LLaMA3-Instruct 8B 下 EAGLE 2.72× → EAGLE-2 **3.46×**。

关键结论：动态 draft tree 使 EAGLE-2 在三档模型上均稳定超越 EAGLE，加速比提升约 0.46–0.74×，τ 同步上升，验证其在不同规模 LLM 上的通用性。

该表作为论文核心实验证据，定量支撑"动态树优于静态树"的核心论点，与 Fig.2 趋势互补，构成 EAGLE-2 方法有效性的实证基础。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-tab03.png]]
> [!quote] caption
> Ablation experiment results with temperature set to 0 on Vicuna 7B. “w/o value” indicates not using value and directly using confidence, “w/o reranking” indicates not performing reranking, and “w/o both” indicates neither value nor reranking is used.

> [!tip] 表格解读（多模态）
> 【图文联合解读】

⚠️ **图与 caption 不符**：caption 写的是 Vicuna 7B 消融实验（w/o value / w/o reranking），但图片实际呈现的是 EAGLE-2 与基线/前身的主结果对比表，而非消融表。

① **结构与数据**：列含 Model / Method / Speedup / τ（平均接受长度）。**LLaMA2-Chat 70B** 上：PLD 1.31x、Lookahead 1.52x、EAGLE 3.01x、EAGLE-2 **3.51x**（τ 由 1.39 升至 4.48）；**LLaMA3-Instruct 70B**：EAGLE-2 3.29x vs EAGLE 2.83x；**LLaMA3-Instruct 8B**：EAGLE-2 3.46x vs EAGLE 2.72x。

② **关键论证结论**：EAGLE-2 在 70B / 8B、不同架构上均稳定优于 PLD、Lookahead、EAGLE；τ 同步增大证明动态草稿树显著提升了 token 平均接受长度，从而兑现更高的推理加速比。

③ **在论文中的作用**：作为主结果表，定量建立 EAGLE-2 跨规模/跨架构的普适优越性，是支撑"动态草稿树 + 重排序"全文方法的核心实证。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
V_i=\prod_{t_j \in \text{Path}\left(\text{root}, t_i\right)} p_j \approx \prod_{t_j \in \text{Path}\left(\text{root}, t_i\right)} c_j,
$$

## 相关论文

- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]] — BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DIFFUSION LANGUAGE MODELS
- [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] — MEDUSA: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads
- [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] — JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting
- [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] — EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty
- [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] — DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation

## 技术点深读（DEEP）

![[deep/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees.txt`（46933 字符）供引用检索。