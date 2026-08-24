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
> 【图文联合解读】图1为temperature=1下四种LLM（Vicuna 7B/13B、LLaMA2-Chat 7B/13B）三种lossless加速方法的推理加速比柱状图。数据：Vicuna 7B为3.05x(EAGLE-2)/2.13x(EAGLE)/1.50x(投机采样)；Vicuna 13B为3.80x/2.32x/1.62x；LLaMA2-Chat 7B为3.19x/2.22x（投机采样N/A）；LLaMA2-Chat 13B为3.92x/2.68x（N/A）。原文借该图论证两点：①EAGLE-2的动态草稿树机制在全部模型上稳定超越EAGLE与投机采样；②在保证输出分布不变前提下仍取得3-4倍显著加速。该图作为论文首图，对全文方法部分起总览性铺垫作用，为Table 1的细粒度对比与动态草稿树算法阐述建立直观性能基准。

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig02.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p02.png]]*
> [!quote] caption
> Speedup ratios of different methods at temperature=0. For speculative sampling, the Vicuna series uses Vicuna- 68M as the draft model. LLaMA2-Chat 7B, 13B, and LLaMA3-Instruct 8B lack suitable draft models and are marked as N/A. LLaMA2-Chat 70B and LLaMA3-Instruct 70B use LLaMA2-Chat 7B and LLaMA3-Instruct 8B as draft models, respectively. In Table 1, we present comparisons with additional methods

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图2对比了EAGLE-2与四种基线方法（EAGLE、Medusa、Lookahead、Speculative sampling）在7个模型（Vicuna 7B/13B、LLaMA2-Chat 7B/13B/70B、LLaMA3-Instruct 8B/70B）上的推理加速比（temperature=0）。量化显示：EAGLE-2在Vicuna 13B达**4.26×**峰值，所有模型稳定在**3.29×–4.26×**，系统性地领先EAGLE（2.72×–3.07×）、Lookahead（1.43×–1.61×）与Medusa/Spec Sampling。原文借此论证动态草稿树带来的稳定且显著的加速收益，构成论文核心实验证据，支撑"EAGLE-2为当前最快推测解码方法"的结论，并衔接Table 1的扩展对比。

### Figure 3 (p.3) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig03.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]]*
> [!quote] caption
> Comparison of standard speculative sampling and EAGLE. For simplicity, EAGLE’s tree-structured draft is shown only in the verification stage, while the illustration of the drafting stage uses a chain-structured draft. Here, ti denotes the i-th token embedding, and fi denotes the i-th feature vector in the second-to-top-layer of LLM before LM head. the token sequence ta, ta+1, · · · , tb. Speculati

> [!tip] 技术解读（多模态）
> 【图文联合解读】草稿阶段(a)：标准方法对token(t2,t3→t4→t5)链式自回归；EAGLE额外引入上一层特征f1,f2，自回归预测f3,f4后映射为token。验证阶段(b)：标准方法链式校验t4→t5，单分支接受；EAGLE改用树结构(t4分支为t5、t6)，由原LLM一次性并行验证，可同时接受多token。论文以此图论证核心方法学结论：①特征级自回归降低草稿难度，②动态草稿树扩展一次验证的接受基数，构成EAGLE-2"特征预测+树形验证"双层加速推理框架的可视化基础，后续实验均围绕二者带来的端到端加速展开验证。

### Figure 4 (p.3) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig04.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]]*
> [!quote] caption
> Differences between EAGLE and EAGLE-2. EA- GLE always uses a fixed draft shape. When the query is “10+2=”, the next token is very likely to be correctly pre- dicted as “1”. However, with a static draft tree, EAGLE would still add two candidates, even though the probability of the other candidate “3” being correct is very low. EAGLE- 2, on the other hand, adjusts the shape of draft tree based on th

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图4下半部对比了EAGLE与EAGLE-2的草稿树结构。EAGLE对"10+2"生成两分支"="和"+"，再对"10+2="静态地生成两分支"1"和"3"；EAGLE-2同样生成"="、"+"两分支，但识别到"1"高置信后，动态沿"="延伸出链式节点"1→2"。原文以此论证：**EAGLE-2依据置信度自适应调整草稿树形状**，将算力集中在高概率路径上，避免在低概率候选（如"3"）上浪费验证开销。该图作为方法论示例，引出后文提出的动态草稿树（dynamic draft tree）机制，是EAGLE-2相较EAGLE实现进一步加速加速比的核心创新证据。

### Figure 5 (p.3) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig05.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]]*
> [!quote] caption
> Overall, the acceptance rate of draft tokens is position-dependent, with the highest acceptance rate at position P1 and the lowest at position P6. Draft tokens in the upper left side of the draft tree (such as position P1) have higher acceptance rates, while those in the lower 3

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与数据：** 图(a)为二元draft树结构（Query→P1/P2→P3–P6，共6个叶子位置）；图(b)为散点图，纵轴Accept Rate(0–1)，横轴Position(1–6)，每点对应一次query。量化趋势：P1接受率密集集中在~1.0（全图最高），P2次之（约0.4–0.9），P3分散于0.2–0.5，P4、P6普遍跌至0.0–0.2（最低），P5相对偏高（0.2–0.9）。

**2) 关键结论：** draft token接受率具有显著的**位置依赖性**——左上（浅层、靠左分支）token接受率高，深层（尤其P6）接受率低。说明并非所有draft位置同等有价值。

**3) 在论文中的作用：** 该图是EAGLE-2从静态树转向**动态draft树**的核心动机证据：既然接受率随位置差异巨大，等宽静态扩展浪费算力；动态树据此对高接受率分支多扩展、低接受率分支少扩展，从而提升speculative decoding的整体加速比。

### Figure 6 (p.4) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig06.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p04.png]]*
> [!quote] caption
> Average acceptance rates for different confidence score intervals of the draft model. The red dashed line connects (0,0) and (1,1) to aid in visual assessment. The original LLM is Vicuna 7B. aspects: how to expand the draft tree (Section 4.1) and how to rerank draft tokens (Section 4.2). During the expansion phase, we input the most promising nodes from the latest layer of the draft tree into the 

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图6图文联合解读**

**1）核心对象与数据**：横轴为draft模型输出的置信度（0–1，分10个区间），纵轴为目标LLM Vicuna 7B在同一置信度区间内的实际接受率。蓝色柱体沿红色虚线 y=x 近似单调递增——置信度≈1.0区间接受率约0.98，最低区间（≈0.0–0.05）接近0.00。

**2）关键技术结论**：置信度与接受率高度正相关、几近线性；中段（0.4–0.6）柱体略超对角线，说明draft模型的置信度略偏保守但具有强校准性，可作为token排序与节点筛选的可靠信号。

**3）在论文中的作用**：为§4.1（动态扩展draft tree）与§4.2（draft token重排）提供经验支撑——按置信度从最新一层中挑选"最有希望"的节点送入下一轮扩展的做法是合理且有保障的。

### Figure 7 (p.5) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig07.png]]
*整页渲染: ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p05.png]]*
> [!quote] caption
> Illustration of EAGLE-2. The numbers beside the edges represent the confidence scores of the draft model, and the numbers in brackets within the blocks represent the value of the nodes. During the expansion phase, we select the top 2 nodes with the highest value from the current layer (orange blocks) as inputs to the draft model and connect the generated tokens (green blocks) to the draft tree. In

> [!tip] 技术解读（多模态）
> 【图文联合解读】**【对象与结构】** 动态草稿树：根"It(1.0)"分叉为is/has双层；橙色top-2节点(a=0.48, to=0.14)作扩展输入，生成绿色子节点good/nice/be/do；Rerank后保留top-8蓝色节点(It,is,has,a,the,to,good,be)，扁平为1D序列后按树结构构建仅可见祖先节点的注意力掩码。

**【技术结论】** 局部扩展(top-2选节点)与全局重排(top-8选草稿)解耦，使草稿树依据上下文动态自适应生成多条高置信候选，而非依赖预设静态结构。

**【论文作用】** 直观看]<]minimax[>[展示EAGLE-2相对EAGLE"动态草稿树"的核心创新，支撑其以更少草稿模型调用换取更高接受率与推理加速比的实验结论。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.7) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-tab01.png]]
> [!quote] caption
> Speedup ratios and average acceptance lengths τ of different methods. V represents Vicuna, L2 represents LLaMA2-Chat. SpS denotes standard speculative sampling, with its draft model being Vicuna-68M. Methods like Medusa relax acceptance conditions under non-greedy settings, which do not guarantee lo

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 联合解读**

① **结构与数据**：展示 SpS/PLD/Medusa/Lookahead/Hydra/EAGLE/EAGLE-2 共 7 种方法，在 Vicuna 与 LLaMA2-Chat 7B、13B 四模型、6 任务（MT-bench、HumanEval、GSM8K、Alpaca、CNN/DM、Natural Ques.）、T=0 与 T=1 下的加速比及平均接受长度 τ。EAGLE-2 全面领先：T=0 下 V 13B 均值 4.04×（τ=4.65），L2 13B 4.10×（4.68）；T=1 下 V 13B 3.65×、L2 13B 3.88×，均显著超越 PLD（1.36–1.70×）、Hydra、EAGLE。

② **关键结论**：动态草稿树在保证 lossless 加速前提下，使 EAGLE-2 速度与接受长度同时跃升；Medusa 因放宽接受条件不保证 lossless，表中仅作参考而不与 EAGLE-2 直接对比。

③ **论文作用**：与图 1 互补——图 1 仅展示 T=1 子集，本表提供多模型、多任务、双温度的完整 benchmark，是 EAGLE-2 优越性的核心量化证据。

### Table 2 (p.8) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-tab02.png]]
> [!quote] caption
> Speedup ratios and average acceptance lengths τ with LLaMA2-Chat 70B, LLaMA3-Instruct 70B, and LLaMA3-Instruct 8B as the original LLMs, with the tem- perature set to 0, on the MT-bench dataset.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读：**

该表在 MT-bench（temperature=0）上对比三类目标模型的加速比与平均接受长度 τ：LLaMA2-Chat 70B 上 PLD/Lookahead/EAGLE 仅 1.31–3.01×，而 **EAGLE-2 达 3.51×（τ=4.48）**；LLaMA3-Instruct 70B 与 8B 上 EAGLE-2 分别取得 3.29×（τ=4.16）与 **3.46×（τ=4.53）**，均优于 EAGLE 的 2.83×/2.72×。

原文借此论证两点关键结论：①EAGLE-2 的动态草稿树机制相对前作 EAGLE 稳定带来约 0.4–0.7× 的额外加速；②接受长度的同步提升（τ↑约 0.5）说明草稿质量与树扩展策略有效。

在论文链路中，该表作为核心定量证据，与 Figure 2 互补，完整支撑"动态草稿树显著加速 LLM 推理"的实验结论。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-tab03.png]]
> [!quote] caption
> Ablation experiment results with temperature set to 0 on Vicuna 7B. “w/o value” indicates not using value and directly using confidence, “w/o reranking” indicates not performing reranking, and “w/o both” indicates neither value nor reranking is used.

> [!tip] 表格解读（多模态）
> 【图文联合解读】注意：题目标注为 Table 3（消融实验），但所给图片实际展示的是 Table 2（速度对比表），与 caption 不一致。以下基于图片真实内容解读：

**1) 核心对象与数据**
表格列出三种模型（LLaMA2-Chat 70B、LLaMA3-Instruct 70B、LLaMA3-Instruct 8B）在不同方法下的加速比 Speedup 与平均接受长度 τ。具体数值：LLaMA2-Chat 70B 上 PLD 1.31×(τ=1.39)、Lookahead 1.52×(τ=1.64)、EAGLE 3.01×(τ=3.81)、EAGLE-2 3.51×(τ=4.48)；LLaMA3-Instruct 70B 上 EAGLE 2.83×、EAGLE-2 3.29×；LLaMA3-Instruct 8B 上 EAGLE 2.72×、EAGLE-2 3.46×。

**2) 关键结论**
EAGLE-2 在所有模型与规模上均取得最高加速比与最长接受长度 τ，相对 EAGLE 在 70B 量级上提升约 0.5×，证明动态 draft tree 带来稳定的加速增益，且 τ 的同步提升说明增益来源于 draft 质量的提升而非仅靠并行。

**3) 在论文中的链路作用**
作为主结果表，用具体量化数据证明 EAGLE-2 相对基线（PLD/Lookahead）与前作 EAGLE 的全面领先，构成支撑论文"动态草稿树"核心贡献的关键证据。

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