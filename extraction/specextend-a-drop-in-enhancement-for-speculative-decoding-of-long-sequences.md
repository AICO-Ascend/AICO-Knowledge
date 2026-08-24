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
> 【图文联合解读】图1展示Llama-3.1-8B-Instruct+EAGLE-3在1K–128K输入长度下的吞吐量（绿线，左轴）与显存占用（堆叠柱，右轴：蓝色Model Weights+橙色KV Cache）。吞吐量从1K的~148 tokens/s骤降至4K的~50、128K仅~5；而KV Cache占比直到64K–128K才显著膨胀至~16 GiB。

**关键结论**：性能衰减远早于显存瓶颈的转移——说明主因并非显存压力，而是长序列下草稿模型命中率下降。

**论文作用**：以量化证据建立问题动机，论证现有方案（如TriForce）仅靠KV压缩无法挽救长序列投机解码收益，从而引出SpecExtend这一drop-in增强方案。

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig02.png]]
*整页渲染: ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p02.png]]*
> [!quote] caption
> Overview of SpecExtend. FlashAttention accelerates the prefill phases of both target and draft models, and Hybrid Tree Attention accelerates the verification phase. We use the target model’s attention scores obtained from verification to select the most relevant input chunks to retain in the draft model’s KV cache, enhancing both draft speed and accuracy on long inputs without additional training.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图示结构**：左侧"长输入序列"切分为8个chunk（红色chunk 3为高注意力相关片段），经FlashAttention预处理后并行输入目标模型（蓝）与草稿模型（绿）；草稿生成候选tokens，目标模型通过Hybrid Tree Attention验证；验证所得注意力分数经"跨模型检索"反馈，仅将相关chunk（1、3、7、8）保留至草稿模型KV cache。

**论证结论**：无需额外训练即可在长序列上同时提升草稿速度与准确率——三阶段加速链（FlashAttention预fill→Tree Attention验证→稀疏KV cache）共同缩短推测解码关键路径。

**论文作用**：作为方法总览图，定锚整套SpecExtend流水线，为后续Table 2中接受长度τ与加速比的实验验证提供架构对应。

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
> 【图文联合解读】**图文联合解读：**

图5在GovReport数据集上，对四种模型组合（V-7B/V-68M、V-7B/EAGLE、LC-7B/LC-68M、LC-7B/EAGLE）对比标准推测解码与SpecExtend在1K–16K输入长度下的加速比。数据揭示两个趋势：①标准推测解码随长度增加加速比急剧下滑，如V-68M从1K的1.78×降至8K的1.08×，LC-68M从1.78×降至1.12×；②SpecExtend始终稳定或上升，16K时普遍达到2.82–3.21×，较标准方法提升近一倍（V-7B/EAGLE：1.61→3.08）。

论文借此论证核心结论：长序列下草稿模型因训练上下文外分布偏移命中率骤降，SpecExtend通过扩展草稿模型窗口恢复并放大加速比。该图是论文"drop-in即插即用、长输入普遍受益"主张的关键实验支撑。

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
> 【图文联合解读】**表格核心数据**：对比四种缓存策略在 Needle Retrieval 任务上的困惑度与草稿准确率。前三种（Full KV/StreamingLLM/CMR）均用 160M 草稿模型，TriForce 用 7B。**量化结果**：困惑度由 8.311→2.435→2.237→2.191；准确率由 0.081→0.166→0.823→0.976。

**关键结论**：同样 160M 草稿模型下，CMR（SpecExtend）准确率（0.823）远超 Full KV（0.081）与 StreamingLLM（0.166），且其困惑度（2.237）已接近 TriForce 用 7B 达到的 2.191。

**实验链路作用**：作为消融/对比证据，证明 SpecExtend 的缓存策略仅以轻量 160M 草稿即可逼近 TriForce 重型 7B 草稿的检索性能，为其"即插即用、低开销增强长序列投机解码"的核心论点提供数据支撑。

### Table 2 (p.6) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-tab02.png]]
> [!quote] caption
> Average accepted length ( τ ), decoding speed (tokens/s) and speedup of speculative decoding with and without SpecExtend. Speedup is measured relative to naive autoregressive generation.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

表2在GovReport/PG-19/BookSum三数据集、1K–16K五档长度下，对比V-7B与LC-7B目标模型搭配V-68M/EAGLE/LC-68M三种草稿模型在有无SpecExtend时的τ、Tok/s与加速比。数据显示：启用SpecExtend后τ全面提升，且序列越长增益越显著——如GovReport+V-68M在16K下τ由1.59升至3.07、加速比从1.38×跃至2.82×（接近翻倍）。该表直接实证SpecExtend作为即插即用增强模块，对不同草稿架构与数据集均能稳定提升长序列推测解码效率，是支撑论文"drop-in enhancement for long sequences"核心主张的关键实验依据。

### Table 3 (p.7) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-tab03.png]]
> [!quote] caption
> Speedup comparison of off-the-shelf methods for long sequence generation with Vicuna-7B. Standard refers to standard tree-based speculative decoding.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 3 在 GovReport、PG-19、BookSum 三个长文数据集、1K–16K 上下文长度下，对比 FlashDecoding、TriForce、MagicDec、标准树形推测解码（Standard）以及 Standard+SpecExtend 五种方案的推理加速比。

数据上，现有方法加速比多集中在 1.0–1.6× 区间，如 Standard 在 16K GovReport 仅 1.38×，TriForce 甚至降至 1.02×；而 Standard+SpecExtend 在所有配置下均取得最高值（粗体），如 GovReport 1K/16K 达 2.28×/2.65×、BookSum 16K 高达 2.81×，相对 Standard 显著提升且随长度延长增益扩大。

该表承接 Figure 3 对 CMR 接受率机制的分析，以端到端加速作为核心实验证据，证明 SpecExtend 无需修改 draft 模型即可在现成推测解码上稳定叠加增益，奠定其"drop-in enhancement"的方法定位。

### Table 4 (p.8) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-tab04.png]]
> [!quote] caption
> Ablation study of SpecExtend components. The standard setting refers to tree-based speculative decoding with Vicuna-7B/68M. FA denotes FlashAttention for prefill, HTA denotes Hybrid Tree Attention, and CMR denotes Cross-model Retrieval.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表4以消融方式对比EAGLE与EAGLE-3两个草稿模型，在1K–16K上下文长度下启用/不启用SpecExtend的三项指标：平均接受长度τ、吞吐Tok/s、相对加速比Speedup。

核心数据：短序列（1K–2K）增益微弱，如EAGLE@1K仅由2.01×微升至2.04×；长序列下增益陡增——8K时EAGLE-3加速比从0.96×（已反退）跃至2.08×；16K时EAGLE-3由0.83×变为2.36×，τ从1.49恢复至3.80，EAGLE亦由1.02×升至1.85×。SpecExtend同时修复了长上下文中τ崩塌与吞吐下滑两类退化。

论文作用：验证FA（prefill FlashAttention）+HTA（Hybrid Tree Attention）+CMR（Cross-model Retrieval）三组件协同，专解长序列下tree-based speculative decoding失效（τ≈2、speedup跌破1×）的痛点，证明SpecExtend是面向长上下文不可或缺的即插即用增强。

### Table 5 (p.8) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-tab05.png]]
> [!quote] caption
> Evaluation of SpecExtend on LLaMA-3.1-8B-Instruct with EAGLE and EAGLE-3 on the GovReport dataset.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 5核心：在GovReport数据集上，以LLaMA-3.1-8B-Instruct为目标，配合EAGLE与EAGLE-3两种草稿模型，在1K/2K/4K/8K/16K五种输入长度下，对比启用/不启用SpecExtend时的接受长度τ、吞吐Tok/s及相对自回归加速比。

关键结论：短输入(1K–2K)下SpecExtend效果中性甚至略损(如EAGLE-3@1K从2.76×→2.75×)；但长输入下提升显著——16K时EAGLE从1.02×→1.85×，EAGLE-3从0.83×(反而慢于基线)跃至2.36×；8K时EAGLE-3从0.96×→2.08×。τ同步回升，说明草稿模型在长上下文下的有效接受能力被恢复。

论文作用：作为核心实证之一，验证SpecExtend以"即插即用"方式修补推测解码在长序列场景的退化，且对先进的EAGLE-3同样奏效，支撑方法的普适性。

### Table 6 (p.8) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-tab06.png]]
> [!quote] caption
> Evaluation of SpecExtend on LLaMA-3.1-8B- Instruct with EAGLE for inputs up to 128K tokens on the PG-19 dataset. Naive autoregressive generation runs out of memory beyond 64K tokens, thus speedup values are omitted.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 解读**

1) **结构与数据**：对比 SpecExtend 开关（No/Yes）在 32K/64K/128K 三档上下文下的 τ、Tok/s、Speedup。开启后 τ 由 1.73→2.73，Tok/s 由 8.45→23.05，32K 处达 2.08× 加速；64K、128K 下 Tok/s 仍稳在 22.5–22.8，Speedup 因基线 OOM 而省略。

2) **关键结论**：SpecExtend 将 EAGLE 的接受长度与吞吐近三倍化，且在 128K 长上下文下仍稳定运行，而原生自回归在 64K 以上即显存崩溃，证明方法对长序列具有可扩展性与工程必要性。

3) **论文作用**：作为长上下文场景的主实验证据，支撑 SpecExtend 即插即用、显著扩展推测解码可用长度范围的核心贡献。

### Table 7 (p.11) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-tab07.png]]
> [!quote] caption
> Latency overhead of a single retrieval cache update step on 16K token inputs.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 7 图文联合解读**

**1) 核心数据**：表格报告 16K token 输入下"检索缓存更新"各步骤的延迟（ms）：
- 标准 Forward：53.76
- 带检索的 Forward（w/ Retrieval）：54.11
- 更新时的 Forward：0.84
- Update 本身：0.34

**2) 关键结论**：在 16K 长序列下，启用检索的 Forward 仅比标准 Forward 多花 0.35 ms（54.11−53.76），增量开销 <1%；更新步骤仅 0.34 ms，几乎可忽略。说明把历史 token 的 KV 写入检索库并按需取回这一步极其轻量，远不会抵消推测解码带来的加速收益。

**3) 在论文中的作用**：SpecExtend 通过在 draft/verify 之间引入"检索缓存"扩展有效上下文。该表是为回应"检索机制本身是否昂贵"这一疑问而做的实测验证——证明它是名副其实的"drop-in"低开销增强，从延迟维度支撑了方法在长序列上的实用性与可部署性。

### Table 8 (p.12) ⭐深度解读
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-tab08.png]]
> [!quote] caption
> Ablation study of Cross-model Retrieval parameters. The table reports decoding speed (tokens/s) using Vicuna-7B as the target model on 8K-token GovReport inputs.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表格内容**：展示 Cross-model Retrieval 四个超参——Working Cache Size、Chunk Size、Top-k、Retrieval Frequency——在 Vicuna-68M 与 EAGLE 两个 draft 模型上、target= Vicuna-7B、8K GovReport 输入下的解码速度（tokens/s）。各参数均存在明显拐点：Cache 1024（Vicuna-68M 33.69）/2048（EAGLE 45.33）最佳，4096 以上 Vicuna-68M 跌至 25；Chunk=32 时两者同时达峰（33.52、49.68）；Top-k 取 32/64 较优；Retrieval Frequency=4（Vicuna-68M 33.59）/8（EAGLE 48.52）最优，过频至 128 时 Vicuna-68M 仅 23.95。

**论证结论**：四个参数均呈先升后降曲线，过大或过小均损害速度，证明 Cross-model Retrieval 模块需精细调度，而非"越大越好"。

**论文作用**：作为 SpecExtend 长序列检索增强的消融，与表 7 速度结果配套，为方法中默认超参（Cache、Chunk、Top-k、Retrieval freq）提供经验依据，支撑主实验速度增益的归因。

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