---
paper_num: "1"
title: "IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse"
authors: "IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse Yushi Bai1†, Qian Dong1†, Ting Jiang2, Xin Lv2 Zhengxiao Du2, Aohan Zeng12, Jie Tang1, Juanzi Li1 1Tsinghua University 2Z.ai"
date: "2026/3/12"
arxiv: "https://arxiv.org/abs/2603.12201"
pdf: "papers/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse.pdf"
slug: "indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse"
tags: [sparse-attention, kv-cache]
---

# IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse

> [!abstract] 摘要（原文）
> 1\. 🚀 IndexCache 提出了一种针对 DeepSeek Sparse Attention (DSA) 的高效策略，通过将 Transformer 层分为保留索引器的 Full 层和复用邻近 Full 层索引的 Shared 层，大幅降低了计算开销。 2. 💡 该研究提供了训练前贪心搜索和训练中多层蒸馏两种优化方案，前者无需微调模型即可优化索引器层配置，后者通过联合训练使模型适配跨层索引复用。 3. 📈 在 30B 规模的 DSA 模型上实验表明，IndexCache 可去除 75% 的索引器计算，在保持模型性能的同时，实现了最高 1.82× 的预填充速度提升和 1.48× 的解码速度提升。

## 元信息
- **发表日期**: 2026/3/12
- **作者**: IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse Yushi Bai1†, Qian Dong1†, Ting Jiang2, Xin Lv2 Zhengxiao Du2, Aohan Zeng12, Jie Tang1, Juanzi Li1 1Tsinghua University 2Z.ai
- **arXiv**: https://arxiv.org/abs/2603.12201
- **本地 PDF**: `papers/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse.pdf`
- **页数**: 18

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-fig01.png]]
*整页渲染: ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p01.png]]*
> [!quote] caption
> Benchmark comparison between GLM-5 and GLM-5 + IndexCache. IndexCache removes 50% of indexer computations while maintaining comparable performance across both long-context and reasoning tasks, delivering ∼1.2× end-to-end speedup.ai. 1[cs.CL] 12 Mar 2026

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图为条形对比图，横轴列出5个基准（HLE、HLE w/ tools、SciCode、AIME25、IFBench），蓝/灰双柱对照 GLM-5 与 GLM-5+IndexCache：得分几乎持平（30.4/30.4、50.4/50.3、45.0/47.0、95.9/95.9、71.0/70.0），SciCode 略升，验证"性能无损"。

原文借此论证：IndexCache 跨层复用 indexer，省去 50% 索引计算，端到端仍可获约 1.2× 加速，是支撑"稀疏注意力高效化"主张的关键实验锚点，位于论文开篇以快速建立方法的可信度与价值印象。

### Figure 2 (p.3) ⭐深度解读
![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p03.png]]
> [!quote] caption
> Side-by-side comparison of inference loops. (a) Standard DSA runs the lightning indexer at every layer. (b) IndexCache adds a single conditional branch (red lines): F layers compute and cache fresh indices; S layers reuse the cached indices. Note that Tcache is a temporary buffer holding only the current index tensor; it is overwritten at each F layer and requires no additional GPU memory beyond w

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】IndexCache 架构图(Fig.2)：对比 (a) 标准 DSA（每层跑 lightning indexer）与 (b) IndexCache（加条件分支：F 层算并缓存索引到临时 buffer T_cache，S 层直接复用 T_cache 跳过 indexer）。T_cache 仅存当前索引张量、每 F 层覆写、无额外显存。利用 token 选择跨层冗余消除稳定层 indexer 计算。架构核心图。

### Figure 3 (p.8) ⭐深度解读
![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-fig03.png]]
*整页渲染: ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p08.png]]*
> [!quote] caption
> Relative speedup of IndexCache over the DSA baseline across three inference settings on the 30B model. DSA baseline is normalized to 100%.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图3以30B模型为对象，柱状图对比DSA基线与IndexCache在两种索引粒度（1/2 indexer、1/4 indexer）下的相对加速比。(a) Prefill阶段加速随上下文长度递增：10K时1/2与1/4索引器分别为121%/127%，200K时提升至142%/**182%**；(b) Decode阶段同样呈正相关，10K为115%/124%，60K达119%/更高值。原文借此论证：IndexCache通过跨层索引复用，在更长上下文与更稀疏的索引器配置下收益放大，证明其方法在prefill/decode全流程均稳定超越DSA基线，是论文"稀疏注意力高效加速"主张的核心定量证据。

### Figure 4 (p.16) ⭐深度解读
![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-fig04.png]]
*整页渲染: ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p16.png]]*
> [!quote] caption
> Pairwise top-k index overlap ratio between all layer pairs of the 30B DSA model.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) 该图为30B DSA模型46层两两之间的top-k索引重叠率热力图（0–1.0）。对角线为1.0（黄色，自重叠），层间总体呈青绿色（约0.4–0.6）；红色方框按贪心搜索的1/4 IndexCache模式将约每4层划为一组，框内对角邻域明显更亮（≈0.7–1.0），表明相邻层共享索引比例显著更高。

2) 论文借此论证：跨层存在显著的索引冗余，且冗余随层距增大而衰减；1/4分块共享模式恰对应高重叠区，从而验证IndexCache"跨层复用top-k索引"的设计可行性。

3) 该图为方法链路的经验基石——先证冗余、再设计缓存复用策略，最终支撑稀疏注意力加速与质量保持之间的平衡。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.7) ⭐深度解读
![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-tab01.png]]
> [!quote] caption
> End-to-end inference performance of the 30B DSA model with IndexCache at two retention ratios. Prefill time : seconds (lower is better). Decode per request : tokens/s under single concurrency (higher is better). Decode full : total tokens/s (higher is better). Decode throughput is reported per GPU.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文联合解读：**

Table 1 展示 30B DSA 模型在 10K–200K 四种上下文长度下，IndexCache 以 1/2、1/4 两种保留率对三项端到端指标的影响：Prefill 时间（s）、单请求 Decode 吞吐（tok/s）、满 KV Decode 吞吐（tok/s）。

**核心数据结论：** 在 1/4 保留率下，200K Prefill 由 19.5s 降至 10.7s（↓约 45%），单请求 Decode 由 58 升至 86 tok/s（+约 48%），满 KV Decode 由 197 升至 297 tok/s（+约 51%）。保留率越低、序列越长，加速度越大，且 Prefill 与 Decode 同步增益，1/4 全面优于 1/2。

**论文作用：** 作为端到端实测证据，验证跨层索引复用可大幅削减索引计算开销并稳定提速，是支撑论文核心论点"~1.2× 端到端加速且精度无损"的关键定量依据。

### Table 2 (p.8) ⭐深度解读
![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-tab02.png]]
> [!quote] caption
> Training-free IndexCache at 1/2, 1/4, and 1/8 indexer retention. ‘Long’ and ‘G&R’ aggregate benchmark scores. We compare uniform interleaving against searched patterns.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读**

Table 2 对比 6 种配置（Original DSA + 1/2、1/4、1/8 三档索引器保留率 × 均匀间隔 Unif. / 搜索模式 Search）在 2 项聚合分数（Long、G&R）与 9 项基准（MRCR、GW、LB2、RULER、LCR、AIME、GPQA、LCB、IFB）上的得分。关键数据：Long 均分由 Original 50.2，随均匀间隔降至 47.4 / 43.0 / 35.3，崩塌明显；改用 Search pattern 后回升至 50.3 / 49.9 / 46.1，且 1/4+Search 在 G&R（74.9 vs 74.6）与 MRCR（25.1 vs 24.5）反超原 DSA。

原文借此论证：均匀跨层复用难以承受保留率下降，**搜索非均匀 F/S 配比**可在训练-free 条件下以 1/2 乃至 1/4 的索引器算力恢复 DSA 质量。该表是 IndexCache "低开销保精度" 主张的核心实证，承接 Fig.2 的 F/S 层条件分支缓存架构，为后续训练版对比与端到端加速评估奠定基线。

### Table 3 (p.9) ⭐深度解读
![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-tab03.png]]
> [!quote] caption
> Training-aware IndexCache at 1/2 and 1/4 indexer retention with uniform inter- leaving. w/ searched pattern : the greedy-searched pattern replaces uniform interleaving. w/o cross-layer loss : each indexer is distilled only against its own layer.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读**

**1）核心内容与量化数据：**
该表对比了 Original DSA 与 1/2、1/4 索引器保留率下多种 IndexCache 变体在 Long-Context（MRCR、GW、LB2、RULER、LCR）与 General & Reasoning（AIME、GPQA、LCB、IFB）共 9 个基准上的平均得分。1/2 Unif. IndexCache 在 Long 平均上以 **51.6**（DSA 为 51.0）实现反超，G&R 平均 **74.5** 持平 DSA 的 74.2；1/4 Unif. IndexCache 仍保持 50.6/74.1。

**2）关键技术结论：**
- **w/o cross-layer loss** 时 Long 平均骤降至 **49.8**（MRCR 从 23.8→24.6、LCR 从 49.8→44.0），证明跨层蒸馏损失是性能核心；
- **w/ searched pattern** 在 RULER/AIME 局部更优（87.5/89.6）但 Long 整体降至 50.6，说明贪心搜索并不优于均匀交错；
- 1/2 配置即可无损替代 DSA，1/4 仍维持可比性能，验证高压缩可行性。

**3）整体方法链作用：**
作为消融表，Table 3 量化验证 IndexCache 三大设计——跨层索引复用、均匀交错模式、训练感知蒸馏——各自贡献，并与 Figure 3 的速度提升互补，共同支撑"以极低开销无损加速 DSA"的结论。

### Table 4 (p.10) ⭐深度解读
![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-tab04.png]]
> [!quote] caption
> Preliminary results on GLM-5 (744B) with training-free IndexCache.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 联合解读：**

该表给出 GLM-5 (744B) 上无训练 IndexCache 的初步结果，对比 Original DSA 与 1/2、1/4 均匀及"搜索模式"在 Long Avg、MRCR v2、GraphWalks、LongBench v2、RULER、AA-LCR 六项指标上的表现。

关键数据：1/2 均匀 + 搜索模式 Long Avg 达 78.7，与原 DSA 的 78.4 基本持平；1/4 均匀单独使用降至 72.7，性能明显下滑，但 1/4 + 搜索模式回升至 78.0，几乎无损；AA-LCR 上 1/4 + 搜索模式甚至以 67.6 超过原 DSA 的 66.2。

技术结论：在激进稀疏比 (1/4) 下，仅均匀索引复用会损失精度，而结合层间 pattern 搜索仍可维持甚至超越原 DSA 性能，证实 IndexCache 跨层复用思路在大规模模型上的可扩展性。

论文作用：作为将方法从 30B 模型外推到 744B 的可行性证据，支撑训练-free 部署的实用价值主张。

### Table 5 (p.18) ⭐深度解读
![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-tab05.png]]
> [!quote] caption
> Evaluation results of training-free similarity-based searched pattern.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与数据：** 表5对比三种配置在四个基准上的表现（Avg/MRCR v2/GraphWalks/RULER）：Original DSA 为 54.0/24.5/49.6/87.9；采用 1/2 Uniform IndexCache 后下降至 50.7/22.0/46.6/83.6；再叠加 "+Searched pattern"（基于相似度搜索的模式）后分别为 49.8/22.9/43.5/82.9。

**2) 关键结论：** 引入基于相似度的训练免搜索模式后，平均分仅从 50.7 微降至 49.8（−0.9），且 MRCR v2 反而回升（22.0→22.9），其余两项小幅下降。说明在压缩一半索引缓存的情形下，用相似性搜索得到的稀疏模式能以极小的精度代价（≈4 Avg 分 vs Original DSA）缓解均匀采样带来的性能损失。

**3) 在论文中的作用：** 该表是"无需训练即可恢复稀疏注意力质量"的支撑实验，验证 IndexCache 的搜索模块作为即插即用模块的实用价值，强化了全文"跨层索引复用＋轻量搜索"的核心技术叙事。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathcal{L}^{\mathrm{I}}_{\mathrm{multi}} = \sum_{j=0}^{m} \frac{1}{m+1}\sum_{t} D_{\mathrm{KL}}\!\left( \mathbf{p}^{(\ell+j)}_{t} \,\big\|\, \mathbf{q}^{(\ell)}_t \right),
$$

$$
\mathcal{L}^{\mathrm{I}}_{\mathrm{avg}} = \sum_{t} D_{\mathrm{KL}}\!\left( \bar{\mathbf{p}}_{t} \,\big\|\, \mathbf{q}^{(\ell)}_t \right).
$$

$$
\nabla_\theta \, \mathcal{L}^{\mathrm{I}}_{\mathrm{multi}} &= -\sum_{j=0}^{m} \frac{1}{m+1} \sum_{t} \nabla_\theta \sum_{s} \mathbf{p}^{(\ell+j)}_{t}(s) \log \mathbf{q}^{(\ell)}_t(s) \notag \\ &= -\sum_{t} \nabla_\theta \sum_{s} \underbrace{\Bigl(\textstyle\sum_{j=0}^{m} \frac{1}{m+1} \mathbf{p}^{(\ell+j)}_{t}(s)\Bigr)}_{\bar{\mathbf{p}}_{t}(s)} \log \mathbf{q}^{(\ell)}_t(s) \;=\; \nabla_\theta \, \mathcal{L}^{\mathrm{I}}_{\mathrm{avg}}.
$$

## 相关论文

- [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] — Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter
- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] — A Survey on Large Language Model Acceleration based on KV Cache Management
- [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] — KV Cache Optimization Strategies for Scalable and Efficient LLM Inference
- [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] — CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion

## 技术点深读（DEEP）

![[deep/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse.txt`（58028 字符）供引用检索。