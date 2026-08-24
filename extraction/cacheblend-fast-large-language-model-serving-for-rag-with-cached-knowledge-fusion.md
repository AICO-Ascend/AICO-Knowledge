---
paper_num: "67"
title: "CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion"
authors: "RAG with Cached Knowledge Fusion Jiayi Yao University of Chicago/CUHK Shenzhen Hanchen Li University of Chicago Yuhan Liu University of Chicago Siddhant Ray University of Chicago Yihua Cheng University of Chicago Qizheng"
date: "2024/5/26"
arxiv: "https://arxiv.org/abs/2405.16444"
pdf: "papers/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion.pdf"
slug: "cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion"
tags: [kv-cache]
---

# CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion

> [!abstract] 摘要（原文）
> Large language models (LLMs) often incorporate multiple text chunks in their inputs to provide the necessary contexts. To speed up the prefill of the long LLM inputs, one can pre-compute the KV cache of a text and re-use the KV cache when the context is reused as the prefix of another LLM input. However, the reused text chunks are not always the input prefix, which makes precomputed KV caches not directly usable since they ignore the text's cross-attention with the preceding texts. Thus, the benefits of reusing KV caches remain largely unrealized. This paper tackles just one challenge: when an LLM input contains multiple text chunks, how to quickly combine their precomputed KV caches in order to achieve the same generation quality as the expensive full prefill (i.e., without reusing KV cache)? This challenge naturally arises in retrieval-augmented generation (RAG) where the input is supplemented with multiple retrieved texts as the context. We present CacheBlend, a scheme that reuses the precomputed KV caches, regardless prefix or not, and selectively recomputes the KV values of a small subset of tokens to partially update each reused KV cache. In the meantime, the small extra delay for recomputing some tokens can be pipelined with the retrieval of KV caches within the same job, allowing CacheBlend to store KV caches in slower devices with more storage capacity while retrieving them without increasing the inference delay. By comparing CacheBlend with the state-of-the-art KV cache reusing schemes on three open-source LLMs of various sizes and four popular benchmark datasets of different tasks, we show that CacheBlend reduces time-to-first-token (TTFT) by 2.2-3.3x and increases the inference throughput by 2.8-5x from full KV recompute without compromising generation quality. The code is available at this https URL.

## 元信息
- **发表日期**: 2024/5/26
- **作者**: RAG with Cached Knowledge Fusion Jiayi Yao University of Chicago/CUHK Shenzhen Hanchen Li University of Chicago Yuhan Liu University of Chicago Siddhant Ray University of Chicago Yihua Cheng University of Chicago Qizheng
- **arXiv**: https://arxiv.org/abs/2405.16444
- **本地 PDF**: `papers/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion.pdf`
- **页数**: 16

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig01.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p02.png]]*
> [!quote] caption
> Contrasting full KV recompute, prefix caching, full KV reuse, and CacheBlend’s selective KV recompute. full KV recompute (Figure 1(a)). Despite many optimizations, the delay and computation of prefill grow super-linearly with the input length, and can easily slow down the service, especially on long LLM inputs (e.g., in RAG) [11, 53, 60].

> [!tip] 技术解读（多模态）
> 【图文联合解读】图1由四个子图横向对比四种KV缓存策略：(a)完整KV重算——对全输入做prefill，最慢但质量好；(b)前缀缓存——仅复用前缀KV，略快且质量好；(c)全KV复用——直接拼接各块KV并忽略跨注意力，虽快但质量低；(d)CacheBlend（本文）——复用全部KV但仅选择性重算其中一小部分，实现"又快又好"。原文借此构建"速度-质量"二维权衡空间，明确指出前三类方案各有缺陷：全重算延迟超线性增长，RAG场景下尤为严重；前缀缓存收益有限；全复用损害质量。从而论证CacheBlend选择性重算同时兼得两端收益的必要性，为全文核心方法定位与动机奠基。

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig02.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p04.png]]*
> [!quote] caption
> Generation quality improves as more text chunks are retrieved. and fetch top-k relevant chunks from the database, based on the least L2 distance between the embeddings of the query and the chunk respectively. Figure 2 shows the generation quality, measured using a standard F1-score metric, with an increasing number of selected text chunks. We can see that the quality improves significantly as more

> [!tip] 技术解读（多模态）
> 【图文联合解读】## 图文联合解读

**核心对象与数据**：图2含两个子图——(a) Musique、(b) 2WikiMQA数据集，横轴为LLM输入的相关文本块数(5–45/5–35)，纵轴为F1-Score(0.15–0.35)。对比两条曲线：蓝色实线（Full KV recompute，带跨块attention）随块数增加F1持续上升，Musique在约25块时峰值≈0.32，2WikiMQA在约30块时峰值≈0.32；橙色虚线（Full KV reuse，无跨块attention）基本持平于0.20–0.23，甚至后期略降。两线间标注的垂直箭头即"跨块attention带来的收益"。

**论证的关键结论**：检索的文本块越多，生成质量越高；但若仅复用各块独立预计算的KV cache而不重新融合跨块attention，质量增益受限；跨块attention是性能提升的关键。

**在论文中的作用**：该图作为CacheBlend的核心动机实验，证明"全量KV重算"虽质量最优但代价高、"全量KV复用"虽快但丢质量，从而为后续提出的"选择性KV重算融合"方案（兼顾质量与速度）提供立论依据。

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig03.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p04.png]]*
> [!quote] caption
> An illustrative example of an LLM input with two text chunks prepended to a query. Full KV recompute (b), with- out reusing KV cache, is slow but gives the correct answer. Full KV reuse (c), however, gives the wrong answer as it neglects cross-attention between the chunks (Figure 4). uses this KV cache to generate the answer, it will start to ramble and not produce the right answer.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图(a)展示典型LLM输入结构：Chunk1（Messi进13球）+Chunk2（Cristiano进8球）+Query"谁进球更多"。
(b)完整KV重算时，模型输出正确答案"Messi进球多于Cristiano"（✓）；
(c)完整KV复用时，模型却开始ramble，输出"该问题关于世界杯……Messi与Ronaldo的名字广为人知……"（✗）。
原因在于复用两段KV cache时，**丢失了chunk间的cross-attention**——模型无法跨块比较"Messi的13"与"Cristiano的8"。

论文借此论证：纯KV复用会损害答案正确性，从而为**CacheBlend**所采用的"选择性KV重算+部分复用融合"策略提供了核心动机——既保留跨块注意力以保证正确率，又避免完全重算的开销，达成速度与精度的折中。

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig04.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p05.png]]*
> [!quote] caption
> Contrasting the attention matrices of (a) full KV recompute and (b) full KV reuse. The yellow boxes highlight the cross-attention. The right-hand side plots show the resulting forward attention matrices whose discrepancies are a result of the different cross-attention between the two methods. 4

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图4联合解读**

**核心对象**：图(a)上排左为26×26注意力矩阵，黄框（行15–25、列0–15）内有数个明显亮点，右侧17×45前向注意力呈清晰对角分布；图(b)同位置黄框完全空白，右侧前向注意力在列17附近出现异常纵向亮带，对角结构紊乱。

**技术结论**：完整KV重用因跳过文本块间cross-attention，导致前向注意力偏移、生成错误；完整KV重算注意力正确但开销大。两者前向注意力的差异即源于cross-attention的有无。

**论文作用**：以可视化对比证明"单纯复用缓存必丢精度"，从而为CacheBlend的核心思路——选择性重算部分层的KV以恢复chunk间cross-attention，同时保留缓存加速——提供直接动机与理论支撑。

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig05.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p06.png]]*
> [!quote] caption
> Illustrated contrast between (a) full KV recompute and (b) selective KV recompute on one layer. 0 10 20 30 40 50

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图5解读（CacheBlend机制图）**

**1）核心对象与结构**：展示单层 Transformer 内 QKV 注意力计算的两种方式。(a) Full KV recompute：全部 token 的 K_i、V_i 均重新计算（深灰块），与 Q_i 相乘生成完整 Attn Matrix；(b) Selective KV recompute：仅对 K_i、V_i 中**2 个选中 token** 深色重算，其余浅色"Re-used"直接复用缓存 KV，从而以极小重算量（仅2 token）维持注意力输出。

**2）论证的关键结论**：CacheBlend 不必像全量重算那样耗费全部 token 的 QKV 前向，只需选择性重算少数关键 token 的 KV 即可修正朴素缓存融合带来的精度损失，实现"算力开销 ≪ 精度损失"，为 RAG 场景下低延迟复用多文档 KV cache 提供微观机制依据。

**3）链路作用**：该图属于方法核心机制图（Fig 5–9），将"KV cache 融合"的具体注意力计算过程可视化，为后续 Fig 10–12 的端到端延迟-吞吐性能提升提供机理支撑。

### Figure 6 (p.6) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig06.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p06.png]]*
> [!quote] caption
> Attention deviation reduces as we recompute the KV of more tokens on each layer. Importantly, the biggest drop in attention deviation results from recomputing the KV of the tokens with the highest KV deviation (i.e., HKVD tokens). on layer 𝑖, so that the attention matrix includes attention between selected tokens and all other tokens. • Finally, it runs the same attention module to produce the inp

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图6联合解读：**

**结构数据：** 三模型（Mistral-7B点线、Yi-34B虚线、Llama-70B实线）的前向注意力偏差随逐层KV重计算比例（0–50%）的衰减曲线。起始偏差约0.55–0.60，前5%内骤降至~0.20，随后缓慢收敛于0.10–0.15，三模型走势一致，Mistral-7B全程略低。

**技术结论：** 该图支撑CacheBlend核心论点——按HKVD分数仅重算少量token的KV即可大幅削减注意力偏差，且最陡降发生于最高KV偏差token处，验证"选择性部分重算"策略的合理性：以极小重算开销逼近全量重算精度。

**链路作用：** 它是论文"重算预算–精度权衡"实验的关键定量证据，为后续"仅重算~10% KV即可保持生成质量"的全栈优化结论提供底层理论支撑。

### Figure 7 (p.7) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig07.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p07.png]]*
> [!quote] caption
> Distribution of KV deviation of different tokens on one layer. 5 vs. 6 12 vs. 13 21 vs. 22 31 vs. 32

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示三模型连续层的KV偏差CDF分布：Mistral-7B(层4-6)、Yi-34B(层10-12)、Llama-70B(层4-6)，横轴分别约0–60、0–75、0–60。三图均呈现陡升长尾形态——CDF在偏差≈20–30处迅速趋近1.0，仅极少数token的偏差延伸至60–75。

**论证结论**：相邻层间及跨模型间KV偏差分布高度一致，表明绝大多数token前后层生成的KV近似相同，仅个别"长尾"token显著偏离。该CDF为CacheBlend核心策略——**选择性重算长尾token的KV、复用其余缓存**——提供了直接的量化实证。

**链路作用**：该图以分布视角证实"KV偏差集中在少量关键token"，从而支撑全文选择性KV融合方案，使其区别于全量重算，在保持生成质量的同时显著加速RAG推理。

### Figure 8 (p.7) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig08.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p07.png]]*
> [!quote] caption
> Rank correlation of the KV deviation per token be- tween two consecutive layers. expensive and defeats the purpose of selective KV recom- pute. Instead, we observe that the HKVD tokens on different layers are not independent:

> [!tip] 技术解读（多模态）
> 【图文联合解读】## Figure 8 图文联合解读

**1) 核心对象与数据**
该图以三组柱状图分别展示 Mistral-7B（4 对层：5/6、12/13、21/22、31/32）、Yi-34B（5/6、16/17、31/32、46/47）与 Llama-70B（11/12、21/22、41/42、61/62）中**相邻层间逐 token KV 偏差的 Spearman 秩相关系数**。三个模型在所有采样层对上的秩相关均稳定在 **≈0.95–1.0** 区间，接近完全正相关。

**2) 关键技术结论**
HKVD（高 KV 偏差）token 在不同层之间**并非独立**：一旦某 token 在某一层被识别为"重要"，其相邻层几乎必然也属于重要 token。这一强跨层相关性为后续策略提供了统计支撑——无需对每层独立、逐 token 重算 KV 偏差。

**3) 在论文方法链路中的作用**
该结论直接支撑 CacheBlend 的**选择性 KV 重算（selective KV recompute）** 设计：可利用层间秩相关，仅在少量代表层中识别关键 token，并将其"扩散"应用到相邻层缓存，从而**以极低开销完成关键 KV 的重计算与融合**，避免全 token、全层重算带来的高昂代价，是 CacheBlend 实现"快"的核心经验依据之一。

### Figure 9 (p.7) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig09.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p07.png]]*
> [!quote] caption
> CacheBlend selects the HKVD (high KV deviation) tokens of one layer by computing KV deviation of only the HKVD tokens selected from the previous layer and selecting the tokens among them with high KV deviation.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心对象与结构**：图示三层（Layer 1–3）双行结构，上行"Updated KV"、下行"Precomputed KV"。Layer 1全量重算所有token，Layer 2仅重算3个token，Layer 3仅重算2个token。流程为：底层KV deviation（黑色条形图）→ 选取HKVD token（Selected列）→ 送入上一层重算。浅色立方=Re-used（缓存复用），深色立方=Re-computed（重算）。

2) **论证的关键结论**：验证逐层递归选择HKVD token策略——仅基于上一层选出的高偏差子集计算当前层偏差并选择性重算，使每层重算量递减，无需全层重算即可获得完整KV。

3) **在论文中的作用**：作为CacheBlend选择性重算机制的核心可视化，支撑其"逐层级联HKVD选择→少量重算+大量缓存复用"的效率论证，是方法相比全量重算显著提速的关键证据。

### Figure 10 (p.8) ⭐深度解读
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p08.png]]
> [!quote] caption
> (a) Smartly picking the recompute ratio will not incur an extra delay. (b) Smartly picking storage device(s) to store KVs saves cost while not increasing delay. recompute of one layer, the KV-loading delay should be able to hide the selective recompute delay, i.e., without incurring any extra delay on time-to-first-token (TTFT).

> [!tip] 技术解读（多模态）
> ## Figure 10 Description

**Figure 10** illustrates two design choices in CacheBlend's loading controller, presented as two panels:

**Panel (a) – Recompute ratio:** Line plot of Prefill delay (TTFT, y-axis) vs. Re-compute ratio %, x-axis 0–50). A dashed line ("w/o pipelining") rises steeply from ~1 to ~3.5s; a solid line ("w. pipelining") stays nearly flat, rising only slightly from ~1 to ~2s. An annotation marks 26.8% as the optimal ratio for a 1 GB/s SSD where no extra delay is introduced.

**Panel (b) – Storage device choice:** Bar chart comparing Prefill delay across GPU, CPU RAM, SSD (32 Gbps), and SSD (4 Gbps), with hatched bars for w/o pipelining and solid bars for w. pipelining. The annotation identifies the cheapest device (CPU RAM) that introduces no extra delay under a 15% recompute ratio.

## Key Technical Takeaway (≤120 words)

CacheBlend exploits **pipelining of KV loading and selective recomputation** so that, as long as the recompute delay T_recompute remains ≤ the KV-loading delay T_load, the recomputation is "hidden" and TTFT is not penalized. This lets the controller decouple quality from latency: (1) pick the smallest recompute ratio r* whose quality drop is negligible (empirically ~15%), then (2) select the cheapest storage device whose T_load ≥ T_recompute. Result: KV caches can be stored on slower, cheaper media (e.g., CPU RAM or 32 Gbps SSD instead of GPU HBM) without increasing TTFT, cutting cost while preserving inference quality.

## Caption (verbatim)

**Figure 10.** *(a) Smartly picking the recompute ratio will not incur an extra delay. (b) Smartly picking storage device(s) to store KVs saves cost while not increasing delay.*

### Figure 11 (p.9) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig11.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p09.png]]*
> [!quote] caption
> CacheBlend system (green stared) in light of LLM context augmented generation for a single request. CacheBlend uses text provided by the retriever, interacts with the storage device(s), and provides KV cache on top of LLM inference engines.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**1) 图示核心对象与结构**
展示CacheBlend处理单条RAG请求的完整6步流程：用户提问"Can we use drones in agriculture?"→①Loading Controller(★)→②抓取4个文本块(Drone Chunk#1/#2、Agri Chunk#1/#2)→③写入三层KV Cache Store(CPU/SSD/慢盘)→④读出KV Cache #1-4并触发KV Cache Fusor(★)→⑤产出Fused KV Cache→⑥返回回复"Drones can…"并回写Potential New KV Cache。

**2) 原文论证的关键技术结论**
验证CacheBlend两大核心组件——**Loading Controller**负责调度检索文本与缓存I/O，**KV Cache Fusor**对各块复用缓存做选择性重算融合，得到全局一致的Fused KV Cache，从而避免全量重计算并保证语义正确性；同时预计算新缓存回写，为后续请求复用。

**3) 在论文方法链路中的作用**
作为系统级架构总览图，承上(缓存复用动机)启下(选择性重算、融合策略及端到端性能实验)，为读者建立"控制器+融合器+分层存储"的整体设计心智模型。

### Figure 12 (p.10) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig12.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p10.png]]*
> [!quote] caption
> CacheBlend reduces TTFT by 2.2-3.3× compared to full KV recompute with negligible quality drop across four datasets and three models.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图以4×3散点矩阵展示**TTFT（横轴）vs生成质量（纵轴，F1/RougeL）**权衡：四行为2WikiMQA、MusiQue、SAMSum、MultiNews四个RAG数据集，三列为Mistral-7B、Yi-34B、Llama-70B三种模型，对比CacheBlend、全KV复用、前缀缓存、全KV重算四种策略。

**关键结论**：CacheBlend（红方块）在所有12组实验中均显著左移于全KV重算（如Llama-70B的2WikiMQA上TTFT由~3s降至~1s），TTFT加速达2.2–3.3×；同时其质量点几乎与全KV重算重合，验证"质量损失可忽略"。全KV复用虽最快但质量严重塌陷（点远低于红线），前缀缓存则仍偏慢。

**论文作用**：作为主实验结果，直观证明CacheBlend在Pareto前沿上兼顾速度与质量，是RAG多文档缓存融合方案的有效性核心证据。

### Figure 13 (p.10) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig13.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p10.png]]*
> [!quote] caption
> Generation quality of CacheBlend with Yi-34B vs MapReduce and MapRerank. 7

> [!tip] 技术解读（多模态）
> 【图文联合解读】图13在四个数据集（2WikiMQA、Musique用F1-Score；SAMSum、MultiNews用RougeL）上以TTFT(s)为横轴、质量为纵轴散点对比CacheBlend（红方块）、MapReduce（绿星）、MapRerank（紫十字），箭头指向左上代表"更优"。前三个数据集上CacheBlend得分约0.32–0.37，均高于MapReduce且TTFT减半（约0.7–0.8s vs 1.7–3.1s）；MultiNews上CacheBlend略低（0.16 vs 0.20）但仍更快。MapRerank虽TTFT最低，质量却明显劣化。该图论证"缓存融合能在保持生成质量的同时大幅降低首token延迟"，是论文核心实验结论之一，证明CacheBlend在RAG长上下文场景下兼顾速度与质量，是方法链路中最终落地收益的关键支撑图。

### Figure 14 (p.11) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig14.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p11.png]]*
> [!quote] caption
> CacheBlend achieves lower TTFT with higher throughput in RAG scenarios compared with baselines of similar quality. 3 6 9 12 (a) Number of chunks

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构**：Figure 14 为 2×3 网格，横轴为每秒平均请求速率（吞吐量），纵轴为 TTFT（首 token 延迟，秒）；列分别为 Mistral-7B、Yi-34B、Llama-70B 三种模型，行分别为 2WikiMQA 与 Musique 扩展数据集。比较 CacheBlend（红方块）、Full KV 重算（蓝三角）、Prefix Caching RAM（浅蓝圆点）与 RAM+SSD（绿菱形）四种策略。

**2) 关键结论**：在两数据集与三模型下，CacheBlend 曲线始终位于右下——例如 Llama-70B 上请求率达 ~0.85/s 时 TTFT 约 7s，而 Full KV recompute 仅 ~0.2/s 即超 8s；Mistral-7B 上 CacheBlend 可承载 ~4 req/s 时 TTFT 仍 <2s，基线在 1 req/s 前已劣化。即"相似质量下更低 TTFT、更高吞吐"。

**3) 论文链路作用**：作为端到端服务性能图，是方法有效性的总验证——把"KV cache 融合"的微观机制（Fig 5–9）落到 RAG 服务宏观指标（延迟-吞吐曲线），支撑 §6 性能评估核心结论。

### Figure 15 (p.11) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig15.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p11.png]]*
> [!quote] caption
> CacheBlend outperforms baseline with varying chunk numbers, chunk lengths, and batch sizes. • SAMSum [25]: This dataset comprises multiple pairs of dialogues and summaries, and requires the LLM to output a summary to a new dialogue. It is intended to test the few-shot learning ability of language models and contains 200 test cases. • MultiNews [20]: This dataset consists of news articles and human

> [!tip] 技术解读（多模态）
> 【图文联合解读】图1×3折线图量化对比CacheFuse与Full KV重算的TTFT：(a)块数3→12，前者由~0.05s缓升至~0.25s，后者从~0.25s飙升至~1.2s；(b)块长300→900，前者稳定于0.15–0.3s，后者达~1.45s；(c)批大小2→10，前者0.2→1.6s，后者从~0.7s急升至~7.8s。原文借此论证CacheFuse在RAG不同配置下TTFT均显著低于基线，且差距随规模扩大。在论文中作为Figure 14的补充消融，验证方法对块数、长度、批大小等关键超参的鲁棒性，强化"缓存融合可显著降低首token时延"的核心结论。

### Figure 16 (p.8) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig16.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p08.png]]*
> [!quote] caption
> This means that even if the storage device is a fast device (ex. CPU RAM), the delay will be lower-bounded by the minimal recomputation to guarantee quality.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图16解读：**

**1) 核心对象与数据：** 图16在Yi-34B模型上对比四种方法于2WikiMQA、Musique、SAMSum、MultiNews四个数据集的生成质量（F1或RougeL）随重算比（Re-compute Ratio）的变化。CacheBlend（红线方块）集中在5%–18%重算区间，质量约0.30–0.38 F1 / ~0.18 RougeL，几乎贴合Full KV recompute（蓝三角，~100%重算）；Full KV reuse（橙×，0%重算）质量骤降至0.15–0.18；Prefix Caching（蓝圆）同样需近100%重算。

**2) 关键结论：** 5%–18%的选择性重算即可逼近全量KV重算的质量，最小必要重算量即构成系统延迟下界。

**3) 在论文中的作用：** 在整体实验链路中提供"质量等价性"关键证据，支撑CacheBlend以极小重算开销替代Prefix Caching全量重算、从而实现RAG推理加速的核心论点。

### Figure 17 (p.12) ⭐深度解读
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig17.png]]
*整页渲染: ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p12.png]]*
> [!quote] caption
> CacheBlend’s outperforms baselines when using RAM and slower disks

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图示内容**
两幅散点图对比CPU RAM（左）与Slow Disk 4Gbps（右）下四种方法的TTFT（0–3s）与F1-Score（0–0.4）。RAM场景TTFT≈0.7s、F1≈0.32，质量与Prefix Caching/Full Recomp（F1≈0.33）持平但延迟仅其1/3；Full KV Reuse TTFT最低（0.15s）但F1仅≈0.15。Slow Disk场景TTFT≈1.3s、F1≈0.32，仍优于Full KV Reuse（F1≈0.15）并与另两方法持平。

**技术结论**
论文借此论证：CacheBlend在不同存储介质下均能以更低延迟保持与全重计算相当的高质量输出，突破"低延迟必损质量"瓶颈。

**论文作用**
属实验评估中的稳健性/泛化性验证环节，证明方法不依赖特定硬件即可在速度-质量维度取得帕累托最优，强化了全文核心卖点。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\begin{aligned} {q}_{m+l} {k}_{m} &={(\mathbb{R}^{d}_{\Theta, m+l}q)}^{T}{(\mathbb{R}^{d}_{\Theta, m}k)}\\ &= \sum_{i=0}^{d/2-1}({q_{[2i]}k_{[2i]}\cos (m+l-m)\theta_{i}}\\ & \quad +{q_{[2i+1]}k_{[2i+1]}\cos (m+l-m)\theta_{i}}) \\ &= \sum_{i=0}^{d/2-1}({q_{[2i]}k_{[2i]}+ {q_{[2i+1]}k_{[2i+1]}})\cos l\theta_{i}} \\ \end{aligned}
$$

$$
q_{m}, k_{m}= \begin{pmatrix} \cos m\theta & -\sin m\theta\\ \sin m\theta & \cos m\theta\\ \end{pmatrix} \{ \begin{pmatrix} q_{[0]}\\ q_{[1]}\\ \end{pmatrix}, \begin{pmatrix} k_{[0]}\\ k_{[1]}\\ \end{pmatrix} \}
$$

$$
\begin{aligned} {q}_{im} {k}_{j(m-n)} &= q_{[0]i}k_{[0]j}\cos (m-m+n)\theta\\ & \quad +q_{[1]i}k_{[1]j}\cos (m-m+n)\theta \\ &= (q_{[0]i}k_{[0]j}+q_{[1]i}k_{[1]j})\cos n\theta \\ \end{aligned}
$$

## 相关论文

- [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] — A Survey on Large Language Model Acceleration based on KV Cache Management
- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] — KV Cache Optimization Strategies for Scalable and Efficient LLM Inference
- [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] — IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse
- [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] — Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter

## 技术点深读（DEEP）

![[deep/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion.txt`（75206 字符）供引用检索。