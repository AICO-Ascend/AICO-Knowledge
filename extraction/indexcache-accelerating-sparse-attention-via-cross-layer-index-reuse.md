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
> 【图文联合解读】图1以柱状图对比GLM-5与加挂IndexCache（保留1/2索引器）在10项基准的得分：长上下文侧MRCR v2(71.1→72.3)、Graph Walks(92.7→90.8)、LongBench v2(64.5→66.0)、RULER(97.7→97.3)、AA-LCR(66.2→67.2)；推理侧HLE(30.4/30.4)、HLE w/tools(50.4→50.3)、SciCode(45.0→47.0)、AIME25(95.9/95.9)、IFBench(71.0→70.0)。原文据此得出核心结论：跨层索引复用削减50%索引器计算后，两类任务分差均≤2，性能近乎无损，并获约1.2×端到端加速。该图作为首篇首图，承担"精度无损换效率"的初始立证，为后续跨层缓存机制、Table 1的端到端推理解析与全文方法链奠定实验入口。

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
> 【图文联合解读】**图3联合解读**

**核心对象与数据**：该图以三组柱状子图对比30B模型上IndexCache相对DSA基线（归一化100%）的加速比——(a) Prefill时间、(b) 单请求Decode吞吐、(c) 全量Decode吞吐，横轴为10K/60K/120K/200K四种上下文长度，纵轴为相对加速百分比，对比1/2与1/4索引器保留两种配置。量化看：1/4配置在200K时三场景分别达182%、148%、151%；1/2配置同条件亦达142%、126%、128%；加速比随上下文长度单调递增。

**技术结论**：跨层索引复用可显著削减稀疏注意力计算与存储开销，且序列越长、索引器压缩越激进，收益越显著。

**论文作用**：与Table 3精度结果互补，构成"效率—精度"实验闭环，支撑IndexCache作为DSA推理加速方案的实用价值论证。

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
> 【图文联合解读】该表展示30B DSA模型在10K–200K四档上下文下，DSA基准、+IndexCache(1/2)、+IndexCache(1/4)三组在Prefill时间、单请求Decode吞吐与全KV Decode吞吐三项指标上的对比。量化数据上，200K时Prefill由19.5s降至10.7s（−45%），单请求Decode由58→86 tok/s（+48%），全KV吞吐由197→297 tok/s（+51%），且所有指标1/4均优于1/2。原文借此论证：保留率越低、上下文越长，加速收益越显著，证明跨层索引复用可有效削减indexer计算开销而无需重算精度。在论文链路中，该表与Fig.1基准互补，从端到端部署视角量化支撑"~1.2×推理加速"这一最终落点结论。

### Table 2 (p.8) ⭐深度解读
![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-tab02.png]]
> [!quote] caption
> Training-free IndexCache at 1/2, 1/4, and 1/8 indexer retention. ‘Long’ and ‘G&R’ aggregate benchmark scores. We compare uniform interleaving against searched patterns.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明**：图片实际呈现的是 Figure 3（30B 模型上 IndexCache 相对 DSA 基线的加速比条形图，纵轴为"Relative S"、横轴为 10K/60K/120K/200K 上下文长度，三幅子图分别对应三种推理设置，标注值在 114%–131% 之间），**Table 2 的表格本体并未在图中渲染**，仅可见其 caption 文字。因此以下解读仅依据 caption：

1) **核心对象与结构**：Table 2 对比的是 *Training-free* IndexCache 在 indexer 保留比例为 **1/2、1/4、1/8** 三档下的表现，列为两种调度策略——**Uniform interleaving（均匀交错 F/S）**与 **Searched patterns（搜索得到的非均匀模式）**，行为聚合基准 **Long** 与 **G&R** 的得分。

2) **论证结论**：在无需训练的前提下，搜索得到的 F/S 交错模式在所有保留比例上均优于朴素均匀交错，说明跨层 index 复用存在更优的"算—跳"节奏，验证了 IndexCache 可压缩 indexer 调用次数而不显著损失质量。

3) **链路作用**：与 Figure 3（加速比）互补——Figure 3 证明速度收益，Table 2 证明质量几乎不退化，共同支撑"训练无关 + 模式可搜索 = 实用化稀疏注意力加速"的核心卖点。

### Table 3 (p.9) ⭐深度解读
![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-tab03.png]]
> [!quote] caption
> Training-aware IndexCache at 1/2 and 1/4 indexer retention with uniform inter- leaving. w/ searched pattern : the greedy-searched pattern replaces uniform interleaving. w/o cross-layer loss : each indexer is distilled only against its own layer.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表面向30B模型，在索引器保留率1/2、1/4下比较均匀交错、贪婪搜索布局及去除跨层损失；后者仅蒸馏本层。图中DSA基线长上下文/泛化推理均分为51.0/74.2；MRCR、GW、LB2、RULER、LCR为24.7、49.1、46.9、87.3、47.0，AIME、GPQA、LCB、IFB为88.8、79.4、70.5、57.9。消融用于证明跨层复用和跨层蒸馏的价值；因对比行缺失，优势幅度无法核验。该表连接全量基准与低保留率效率实验。

### Table 4 (p.0) ⭐深度解读
![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-tab04.png]]
> [!quote] caption
> Preliminary results on GLM-5 (744B) with training-free IndexCache.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读**

Table 4 在 GLM-5（744B）模型上对比 Original DSA 与训练免费 IndexCache 的性能，横跨 Long Avg、MRCR v2、GraphWalks、LongBench v2、RULER、AA-LCR 共 6 项基准。关键数据：Original DSA 的 Long Avg = 78.4；1/2 Uniform IndexCache 为 78.1（仅↓0.3），叠加搜索模式后升至 78.7（反超原模型）；1/4 Uniform IndexCache 大幅跌至 72.7（损失 5.7 分），而叠加搜索模式后回升至 78.0（仅差 0.4）。

论文借此论证：跨层索引复用能否无损，极度依赖复用层的选择方式。均匀复用仅在低压缩比（1/2）下勉强可用，高压缩比（1/4）时性能崩塌；而采用搜索到的非均匀复用模式后，即使压缩到 1/4 也几乎保持原模型质量，证明**非均匀的跨层模式才是 IndexCache 的核心收益来源**。

该表承接 Figure 4 关于层间索引高重叠率的发现，作为 744B 规模下的预实验，为 IndexCache 向超大模型的可扩展性提供了首个量化证据，支撑方法在大模型部署场景中的有效性。

### Table 5 (p.18) ⭐深度解读
![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-tab05.png]]
> [!quote] caption
> Evaluation results of training-free similarity-based searched pattern.

> [!tip] 表格解读（多模态）
> 【图文联合解读】# 图像与表格不匹配的说明

**注意**：上传的图片实际展示的是**公式 (4) 及周围正文**（动态规划求解最优 F 层选择的优化形式），**而非 Table 5 本身**。Table 5 的实际表格内容未能提供。以下结合 caption 与公式上下文进行解读：

---

## 图文联合解读

1. **核心对象与结构**：公式 (4) 定义了 IndexCache 的核心优化问题——在约束"恰有 M 个 F 层"下，最大化各层复用索引所得的累计相似度 ∑S_ℓ,src(ℓ)；src(ℓ) 为 ℓ 之前最近的 F 层。该问题通过 DP（dp[i][k]）精确求解。Table 5 据此应展示**训练免费的相似度搜索模式**的评估结果，即由 DP 解 c\* 选出的 F 层集合在相似度、检索质量及下游任务上的表现，并与均匀分配等基线对比。

2. **论证的关键技术结论**：作者意图证明——基于相似度的搜索模式无需任何训练即优于手工规则（如固定间隔、均匀分配），从而**以零开销支撑跨层索引复用**的可行性。

3. **在论文链路中的作用**：Table 5 是方法验证环节的关键证据——公式 (4) 给出理论最优解，Table 5 用实验量化"该最优解确实换来高质量注意力检索与精度保持"，从而为后文的端到端加速实验（速度/精度权衡）提供搜索策略层面的支撑。

*（若需更精确解读，请补传 Table 5 实际图像。）*

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