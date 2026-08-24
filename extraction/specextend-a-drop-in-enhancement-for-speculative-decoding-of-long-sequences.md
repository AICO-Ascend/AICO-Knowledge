---
paper_num: "60"
title: "SpecExtend: A Drop-in Enhancement for Speculative Decoding of Long Sequences"
authors: "Speculative Decoding of Long Sequences Jungyoub Cha Hyunjong Kim Sungzoon Cho Seoul National University {jungyoub.cha, hjkim0811, zoon}@snu.ac.kr"
date: "2025/5/27"
arxiv: "https://arxiv.org/abs/2505.20776"
pdf: "papers/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences.pdf"
slug: "specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences"
tags: [speculative]
---

# SpecExtend: A Drop-in Enhancement for Speculative Decoding of Long Sequences

> [!abstract] 摘要（原文）
> Speculative decoding is a widely used technique for accelerating inference in large language models (LLMs), but its performance degrades as input length grows, with significant drops even at moderate lengths. Yet, this early degradation has remained largely underexplored. We introduce SpecExtend, a drop-in enhancement that improves speculative decoding on long sequences without additional training. SpecExtend integrates efficient attention mechanisms such as FlashAttention and Hybrid Tree Attention to accelerate prefill and verification steps. To improve both draft accuracy and speed on long inputs without retraining, we propose Cross-model Retrieval, a novel KV cache eviction strategy that leverages the target model's attention scores to dynamically select relevant context for the smaller draft model. Extensive evaluations show that SpecExtend accelerates speculative decoding by up to 2.84x on 16K-token long document summarization and up to 3.86x on long-form reasoning, while preserving the short-input performance of state-of-the-art frameworks. Our code is available at this https URL .

## 元信息
- **发表日期**: 2025/5/27
- **作者**: Speculative Decoding of Long Sequences Jungyoub Cha Hyunjong Kim Sungzoon Cho Seoul National University {jungyoub.cha, hjkim0811, zoon}@snu.ac.kr
- **arXiv**: https://arxiv.org/abs/2505.20776
- **本地 PDF**: `papers/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences.pdf`
- **页数**: 12

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig01.png]]
*整页渲染: ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p01.png]]*
> [!quote] caption
> Performance and memory usage of speculative decoding with Llama-3.1-8B-Instruct and EAGLE-3 across varying input lengths. Performance significantly declines well before the shift of memory bottleneck.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图1展示Llama-3.1-8B-Instruct+EAGLE-3在1K–128K输入长度下的双轴数据：绿色折线为吞吐量(tokens/s)，堆叠柱为显存占用(蓝Model Weights+橙KV Cache)。量化可见：吞吐量从1K的~150骤降至4K的~45 tokens/s；而KV Cache在≤32K时仍<2 GiB，直至128K才增至~16 GiB与权重持平。

**技术结论**：性能崩塌远早于显存瓶颈出现，说明长序列下推测解码减速的主因并非KV Cache显存/带宽，而源自其他机制(如草稿模型匹配率下降、注意力计算开销等)。

**论文作用**：以"反直觉"现象作为核心动机，引出SpecExtend——针对非显存瓶颈的长序列性能退化，提出对推测解码的即插即用增强方案。

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig02.png]]
*整页渲染: ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p02.png]]*
> [!quote] caption
> Overview of SpecExtend. FlashAttention accelerates the prefill phases of both target and draft models, and Hybrid Tree Attention accelerates the verification phase. We use the target model’s attention scores obtained from verification to select the most relevant input chunks to retain in the draft model’s KV cache, enhancing both draft speed and accuracy on long inputs without additional training.

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图展示SpecExtend整体流程：长输入序列切分为8个Chunk，经Flash Attention Prefill并行输入Target与Draft模型；Target通过Hybrid Tree Attention验证Draft生成的候选Token，其Attention Scores经"Cross-model Retrieval"反向回传，从8个Chunk中筛选出{1,3,7,8}保留至Draft Model KV Cache，实现draft与target的KV对齐。

论文以此论证三项drop-in加速技术——Prefill阶段FlashAttention、Verify阶段Hybrid Tree Attention、基于注意力分数的Chunk选择性缓存——在无需额外训练下兼顾draft速度与准确性，为Table 2中相对自回归生成取得显著Speedup提供了核心方法学支撑。

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig03.png]]
*整页渲染: ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p04.png]]*
> [!quote] caption
> Left figure shows acceptance rates for hard and easy tokens, where CMR enables more accurate drafting in both cases compared to StreamingLLM.

> [!tip] 技术解读（多模态）
> 【图文联合解读】左图：Hard/Easy token接受率（%），CMR≈61.5/75，均高于StreamingLLM的60/70.5；右图：1st/2nd/3rd/Resampled四位置的自然散度D_LK，CMR前三位置约0.25–0.33、Resampled约0.74，均低于StreamingLLM的0.37–0.39与0.84。

论文据此论证两点核心结论：(1)CMR在难易token上drafting均更准确，接受率提升；(2)CMR使draft分布与target模型在所有位置均更对齐，分布差异更小。

该图在论文中的作用：作为SpecExtend核心模块CMR的微观有效性证据，与第4节端到端加速比互补，从"分布层"和"接受率层"共同支撑CMR作为长序列推测解码"即插即用"增强模块的核心论点。

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig04.png]]
*整页渲染: ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p05.png]]*
> [!quote] caption
> (a) Average accepted length of Vicuna-7B/68M across different draft model cache settings. (b) End-to-end latency breakdown of speculative decoding on 16K-token inputs. retrieved context to identify and generate tokens corresponding to a planted “needle” in long inputs (Li et al., 2024a; Contributors, 2023). We com- pare its accuracy against three draft model cache strategies: (1) Full KV Cache whi

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图(a) 平均接受长度（Vicuna-7B/68M，1K→16K 输入）**
- Standard（绿）：从 ~3.75 骤降至 ~1.7
- StreamingLLM（橙）：从 ~3.7 降至 ~2.55
- SpecExtend（蓝）：始终最高，从 ~3.8 仅降至 ~2.95

**图(b) 16K-token 端到端时延堆叠（Target/Draft Prefill + Verification + Drafting）**
- Standard 总计约 17 s，Verification（绿）占主导 ~12 s、Drafting（粉）~3 s
- With SpecExtend 总时延骤降至 ~5.5 s，验证与起草段均显著压缩

**论证结论与作用**：原文以(a)说明长序列下传统 KV cache 失效致接受长度崩塌、加速失效；以(b)量化SpecExtend 作为 drop-in 模块带来的约 3 倍时延收益。该图在论文实验链路中承担"质量不丢、墙钟显著降低"的双重证据，是支撑 SpecExtend 在长上下文投机解码有效性的核心可视化。

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig05.png]]
*整页渲染: ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p06.png]]*
> [!quote] caption
> Speedup comparison of standard speculative decoding and SpecExtend across varying input lengths on

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

1) 该图为四面板分组柱状图（图片可见右侧"LC-7B/LC-68M"与"LC-7B/EAGLE"两面板），横轴为GovReport上1K–16K输入长度，纵轴加速比0–3.5，深浅蓝柱对比标准投机解码与SpecExtend。关键数据：LC-68M在8K由1.12升至2.30、16K由1.51升至2.84；EAGLE在16K由1.81升至3.21。

2) 原文论证：标准投机解码随序列增长加速比显著衰减（16K仅1.51/1.81），而SpecExtend始终保持>1.8并呈上升趋势，长序列增益最明显，证实其对长输入的稳健加速能力。

3) 该图是论文核心实验证据，验证SpecExtend作为即插即用模块在不同draft模型（LC-68M、EAGLE）与各长度下均稳定提升加速比，支撑其长序列泛化性与工程实用价值。

### Figure 6 (p.7) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig06.png]]
*整页渲染: ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p07.png]]*
> [!quote] caption
> Decoding speed (left) and average ac- cepted length (right) of the DeepSeek-R1-Distill-Llama- 8B/EAGLE-3 setup on the long reasoning task with the AIME-24 benchmark.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图6联合解读：**

图6对比Naive AR、EAGLE-3、EAGLE-3+SpecExtend三种方法在DeepSeek-R1-Distill-Llama-8B/AIME-24长推理任务上的解码速度（左，Tok/s）与平均接受长度（右）。具体数据：Naive AR为31.42/1.00，EAGLE-3为30.34/1.89，EAGLE-3+SpecExtend跃升至117.21/5.95。

**关键结论：** 单独EAGLE-3在长推理场景下速度甚至略低于自回归基线（30.34 vs 31.42），表明草稿模型在长序列后段出现退化；叠加SpecExtend后速度提升约3.7倍，接受长度提升约3.1倍。

**作用：** 该图是验证SpecExtend作为即插即用模块在长思维链推理场景下有效性的核心定量证据，支撑论文"无需重训练即可恢复并放大EAGLE-3加速收益"的核心主张。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.4) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-tab01.png]]
> [!quote] caption
> Perplexity and draft accuracy of needle tokens in the Needle Retrieval task, using different draft model settings. The first three methods use Vicuna-160M as the draft model, while TriForce uses Vicuna-7B.

> [!tip] 表格解读（多模态）
> 【图文联合解读】图中未显示前三列的方法名；4列草稿配置大小为160M、160M、160M（Vicuna）和7B（TriForce）。针令牌的PPL依次为8.311、2.435、2.237、2.191，准确率为0.081、0.166、0.823、0.976。7B TriForce较最佳160M配置准确率升0.153（15.3个百分点），PPL降0.046，说明强化草稿模型可显著改善长上下文预测。该表用于诊断小草稿失效，并作为SpecExtend增强长序列推测的动机。

### Table 2 (p.6) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-tab02.png]]
> [!quote] caption
> Average accepted length ( τ ), decoding speed (tokens/s) and speedup of speculative decoding with and without SpecExtend. Speedup is measured relative to naive autoregressive generation.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表以四组子图对比 V-7B/LC-7B 分别搭配 V-68M/LC-68M 与 EAGLE 两种草稿模型，在 1K–16K 输入长度下标准投机解码与加入 SpecExtend 后的加速比。量化显示：标准方法随序列变长加速急剧衰减（V-7B/V-68M 由 1K 的 1.78× 降至 8K 的 1.08×），而 SpecExtend 保持并放大增益，16K 峰值达 LC-7B/EAGLE 的 3.21×。原文借此论证：SpecExtend 作为即插即用模块，无需重训练即可恢复并显著提升长序列下的投机解码效率，是论文方法链路的关键终端定量证据。

### Table 3 (p.7) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-tab03.png]]
> [!quote] caption
> Speedup comparison of off-the-shelf methods for long sequence generation with Vicuna-7B. Standard refers to standard tree-based speculative decoding.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读**

**1) 核心对象与结构**：表 3 在 Vicuna-7B 上对比 5 种长序列生成加速方法（FlashDecoding、TriForce、MagicDec、Standard 树推测解码、Standard + SpecExtend），在 GovReport、PG-19、BookSum 三个长文本数据集、1K–16K 五档生成长度上报告加速比。数据上，SpecExtend 在所有 15 个组合中均加粗最高：GovReport 1K 达 2.28×、16K 达 2.65×；PG-19 由 1K 的 1.74× 提升至 16K 的 2.70×；BookSum 在 16K 取得全表最高 2.81×。

**2) 关键结论**：Standard 方法在 4K/8K 处出现明显衰减（如 GovReport 8K 仅 1.08×，BookSum 8K 仅 1.05×），说明标准推测解码难以应对长序列；FlashDecoding 加速随长度增长但绝对值偏低（最高 1.58×）；TriForce 在长序列下退化（GovReport 16K 跌至 1.02×）。SpecExtend 通过持续的 ~2× 加速，验证了其在长序列场景下对标准方法的"即插即用"增益。

**3) 在论文中的定位**：该表是方法主实验核心证据，与 Figure 3 的接受率/散度分析互补——前者从端到端加速比证明有效性，后者从机制层面解释为何 CMR 草稿更准，从而共同支撑 SpecExtend 作为长序列推测解码增强方案的结论。

### Table 4 (p.8) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-tab04.png]]
> [!quote] caption
> Ablation study of SpecExtend components. The standard setting refers to tree-based speculative decoding with Vicuna-7B/68M. FA denotes FlashAttention for prefill, HTA denotes Hybrid Tree Attention, and CMR denotes Cross-model Retrieval.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表格展示EAGLE与EAGLE-3作为草稿模型时，启用与否SpecExtend在1K–16K长度下的接受长度τ、Tok/s及Speedup。数据显示：未启用SpecExtend时，加速比随序列增长急剧衰减——EAGLE在16K仅1.02×、EAGLE-3在16K降至0.83×（已低于baseline）；启用后长序列性能反而跃升，EAGLE 16K Speedup由1.02×提至1.85×，EAGLE-3 16K由0.83×提至2.36×，Tok/s近乎翻倍。该消融用于论证FA（FlashAttention预填充）、HTA（Hybrid Tree Attention）、CMR（Cross-model Retrieval）三组件协同是SpecExtend维持长序列投机解码收益的核心，从而支撑"drop-in增强"这一核心论据。

### Table 5 (p.8) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-tab05.png]]
> [!quote] caption
> Evaluation of SpecExtend on LLaMA-3.1-8B-Instruct with EAGLE and EAGLE-3 on the GovReport dataset.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 5对比LLaMA-3.1-8B-Instruct在GovReport上、EAGLE与EAGLE-3在1K–16K输入下的τ（接受长度）、Tok/s、Speedup三组指标，每行配对启用/不启用SpecExtend两种配置。

**核心结论**：标准投机解码随长度急剧衰减——EAGLE-3在16K时Speedup仅0.83×（反慢于自回归），EAGLE也仅1.02×。SpecExtend显著抬升τ（EAGLE-3@16K：1.49→3.80），使Speedup恢复并反超至2.36×；EAGLE@16K由1.02×提升至1.85×。而1K处增益极小（EAGLE-3：2.76×→2.75×），印证其专为长序列优化。

**论文作用**：与Figure 5形成"图+表"互证，定量佐证SpecExtend作为drop-in模块在长上下文下恢复并增强投机解码加速比的核心主张，是实验链路中"长序列有效性"的关键证据。

### Table 6 (p.8) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-tab06.png]]
> [!quote] caption
> Evaluation of SpecExtend on LLaMA-3.1-8B- Instruct with EAGLE for inputs up to 128K tokens on the PG-19 dataset. Naive autoregressive generation runs out of memory beyond 64K tokens, thus speedup values are omitted.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 图文联合解读**

**1) 核心数据：** 表展示 LLaMA-3.1-8B-Instruct + EAGLE 在 PG-19 数据集 32K/64K/128K 三档长度下启用 SpecExtend 前后的对比。无 SpecExtend 时，τ≈1.73，Tok/s 稳定在 ~8.45；启用后 τ 跃升至 ~2.72（32K: 2.73；64K: 2.71；128K: 2.72），Tok/s 提升至 22.59–23.05（32K 给出 2.08× speedup，64K 与 128K 因自回归基线 OOM 而省略）。

**2) 关键技术结论：** SpecExtend 作为 EAGLE 的即插即用增强，长度从 32K 延展至 128K 仍保持约 2.7× 的吞吐加速与一致的高接受温度（τ 显著增大意味着平均接受草稿更长），验证了"短序列训练、长序列零样本可用"的核心论断。

**3) 在论文中的作用：** 该表是长上下文扩展性的关键证据——证明 SpecExtend 不仅可替代密集近邻注意力，还能在 64K 以上（朴素方法显存不足）继续提供稳定的推测解码加速，补齐了 Figure 6（推理任务）之外的通用长文本实验链路。

### Table 7 (p.11) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-tab07.png]]
> [!quote] caption
> Latency overhead of a single retrieval cache update step on 16K token inputs.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表展示16K token输入下检索缓存的单步延迟开销：完整前向Forward=53.76 ms，启用检索后升至54.11 ms（仅多0.35 ms，约0.65%）；逐token增量Forward=0.84 ms、缓存Update=0.34 ms。

原文借此论证检索缓存机制近乎"零成本"——既不显著拖慢主前向（开销<1%），增量维护代价也极低（每token合计≈1.18 ms）。这证明SpecExtend对长序列的适配高效可行，是支撑其作为"drop-in"增强模块、可无缝接入既有投机解码流水线的关键效率证据。

### Table 8 (p.12) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-tab08.png]]
> [!quote] caption
> Ablation study of Cross-model Retrieval parameters. The table reports decoding speed (tokens/s) using Vicuna-7B as the target model on 8K-token GovReport inputs.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 图文联合解读：**

该表展示跨模型检索（Cross-model Retrieval）四个超参数对解码速度（tokens/s）的影响，每参数对比 Vicuna-68M 与 EAGLE 两个草稿模型。Working Cache Size 在 1024（Vicuna-68M 达 33.69）与 2048（EAGLE 达 45.33）最优；Chunk Size=32 时两者同时达到峰值 33.52 与 49.68；Top-k 在 32–64 区间最佳；Retrieval Frequency=4 与 8 分别取得 33.59 与 48.52 的最高速度。过小缓存、过大 Top-k 或过低频检索都会显著掉速。

论文借此论证：每个超参数均存在"过犹不及"的甜点区间，且所选默认值（cache≈1024–2048、chunk=32、top-k≈32–64、frequency≈4–8）合理。该消融是 SpecExtend 主实验的前置验证，确保后续长序列加速收益来源于方法设计而非参数巧合，支撑整体实验链路可信度。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\frac{T_{avg}^{sd}}{T_t} = \frac{1}{\tau(n,d)} \left( \frac{d \cdot T_d}{T_t} + \frac{T_v(n)}{T_t} \right)
$$

## 相关论文

- [[dflash-block-diffusion-for-flash-speculative-decoding]] — DFlash: Block Diffusion for Flash Speculative Decoding
- [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] — LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and Verification
- [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] — JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting
- [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] — DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation
- [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] — EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty
- [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] — MEDUSA: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads

## 技术点深读（DEEP）

![[deep/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences.txt`（44368 字符）供引用检索。