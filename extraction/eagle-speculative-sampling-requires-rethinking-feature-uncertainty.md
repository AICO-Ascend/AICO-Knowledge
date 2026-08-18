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

### Figure 1 (p.1)
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p01.png]]
> [!quote] caption
> Speedup ratio of Vicuna and LLaMA2-Chat inference latency on the MT-bench for greedy (temperature=0) settings. Speedup ratio of Medusa and Lookahead are copied from their original technical reports. With speculative sampling, there is a lack of suitable draft models to accelerate the 7B model. Employing a 7B model as the draft model for a 13B model results in slow speeds due to the high overhead o

### Figure 2 (p.2) ⭐深度解读
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p02.png]]
> [!quote] caption
> Speedup ratio on the MT-bench for non-greedy (temperature=1) settings. Lookahead is confined to greedy decoding, and the non-greedy generation of Medusa does not guarantee lossless performance. Therefore, EAGLE is not compared with these methods. I 𝑓I 𝑝(am)=0.6 𝑝(always)=0.4 sampling am 𝑓am 𝑝(excited)=0.3 𝑝(ready)=0.7 sampling always 𝑓always 𝑝(begin)=0.8 𝑝(look)=0.2 𝑝always 𝑝I 𝑝am

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】EAGLE 架构图(Fig.4)：目标 LLM 产出第二顶层特征 f_t 与下一 token t_{t+1}；轻量 draft model 在特征层自回归，输入 f_t + 超前一拍的 t_{t+1}，预测 f_{t+1}，再经 LM head 得 draft token t_{t+2}。「特征+超前 token」消除采样下 f_{t+1} 的不确定性→接受率↑，Vicuna/LLaMA2-70B 上 2.68x。架构核心图。

### Figure 3 (p.2) ⭐深度解读
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p02.png]]
> [!quote] caption
> Uncertainty in feature sequences. The next fea- ture following fI is contingent on the sampling outcome and cannot be determined solely based on fI, where both “always” and “am” are possible to follow the token “I” and lead to two branches.

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】EAGLE 架构图(Fig.4)：目标 LLM 产出第二顶层特征 f_t 与下一 token t_{t+1}；轻量 draft model 在特征层自回归，输入 f_t + 超前一拍的 t_{t+1}，预测 f_{t+1}，再经 LM head 得 draft token t_{t+2}。「特征+超前 token」消除采样下 f_{t+1} 的不确定性→接受率↑，Vicuna/LLaMA2-70B 上 2.68x。架构核心图。

### Figure 4 (p.3)
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p03.png]]
> [!quote] caption
> Accuracy and speedup ratio of draft models based on tokens, features and feature&shifted-token at tempera- ture=0, tested on MT-bench with Vicuna 7B as the original LLM. Feature&shifted-token refers to using a feature se- quence and a token sequence advanced by one time step as inputs. achieved a speedup ratio of 2.7x-3.5x, doubled through- put, and theoretically guaranteed the preservation of the

### Figure 5 (p.4)
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p04.png]]
> [!quote] caption
> A comparison of the methods for drafting the fourth and fifth tokens, t4 and t5. t (represented by blue blocks) denotes tokens, and f (orange blocks) signifies the features, with subscripts indicating their positions in the se- quence. The red border indicates the predictions of the draft model. For simplicity, the n in the n-gram for Lookahead, as shown in the figure, has been set to 2.

### Figure 6 (p.4)
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p04.png]]
> [!quote] caption
> Pipeline of EAGLE. The upper section illustrates the computational process, while the lower section displays the corresponding generation results for each step. In the upper section, green blocks represent token embeddings, or- ange blocks represent features, red boxes indicate the predic- tions of the draft model, and blue modules with snowflake icons represent the use of target LLM parameters, w

### Figure 7 (p.7)
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p07.png]]
> [!quote] caption
> Speedup ratios of EAGLE with and without the use of tree attention. The evaluation dataset is MT-bench, with the temperature parameter set to 0.

### Figure 8 (p.8)
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p08.png]]
> [!quote] caption
> Performance of draft models with varying inputs. The target LLM is Vicuna 7B, and the test dataset is MT-bench.

### Figure 9 (p.12)
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p12.png]]
> [!quote] caption
> However, the optimal tree structure is likely context-dependent. For instance, as batch size increases and redundant computational resources decrease, a smaller tree might be preferable. Tuning the draft structure could potentially lead to improved performance. query query

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