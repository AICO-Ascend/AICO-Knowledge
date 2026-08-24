---
paper_num: "50"
title: "A Survey on Large Language Model Acceleration based on KV Cache Management"
authors: "A Survey on Large Language Model Acceleration based on KV Cache Management Haoyang Li, Yiming Li, Anxin Tian, Tianhao Tang, Zhanchao Xu, Xuejia Chen, Nicole Hu, Wei Dong, Qing Li Fellow, IEEE, Lei Chen Fellow, ACM/IEEE,"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2412.19442"
pdf: "papers/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management.pdf"
slug: "a-survey-on-large-language-model-acceleration-based-on-kv-cache-management"
tags: [kv-cache]
---

# A Survey on Large Language Model Acceleration based on KV Cache Management

> [!abstract] 摘要（原文）
> 1\. 🤖 大语言模型（LLMs）在推理过程中面临巨大的计算和内存需求，尤其是处理长上下文时，KV cache管理已成为解决此瓶颈的关键优化技术。 2. ⚙️ 该综述系统地将KV cache管理策略划分为token-level、model-level和system-level优化，涵盖了从数据压缩到架构创新再到系统资源调度的广泛技术。 3. 🚀 该研究不仅提供了详细的分类和比较分析，还指出未来研究方向应侧重于跨类别集成、实际部署案例、领域特定优化及隐私安全等挑战。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: A Survey on Large Language Model Acceleration based on KV Cache Management Haoyang Li, Yiming Li, Anxin Tian, Tianhao Tang, Zhanchao Xu, Xuejia Chen, Nicole Hu, Wei Dong, Qing Li Fellow, IEEE, Lei Chen Fellow, ACM/IEEE,
- **arXiv**: https://arxiv.org/abs/2412.19442
- **本地 PDF**: `papers/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management.pdf`
- **页数**: 40

## 图表（原文 caption + 页码）
_未检测到带 caption 的 figure_

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.8) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab02.png]]
> [!quote] caption
> TABLE II: Comparison of KV cache selection strategies.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读**

该表横向对比22种KV Cache选择/淘汰方法（FastGen至LoopServe），按Initial tokens、Top-k、Recent tokens、Permanent eviction、Dynamic selection 5维度打勾，并标注选择粒度（token/block/cluster/event）与技术特征（如FastGen五类注意力结构、H2O累积注意力分数、MagicPIG采用LSH、EM-LLM按episodic events）。

**关键结论**：早期方法（FastGen、SnapKV、StreamingLLM等）以token级+永久淘汰为主；近期方法（InfLLM、EM-LLM、MagicPIG等）转向动态选择，粒度粗化至block/cluster/event，淘汰范式由静态启发式演化为动态检索驱动。

**论文作用**：与Tab1（量化）、Tab3（合并共享）并列支撑综述压缩类二维分类法，为免训练低开销方案提供选型图谱与范式演进证据。

### Table 4 (p.11) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab04.png]]
> [!quote] caption
> TABLE IV: The summary of existing KV Cache merging approaches.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 4 从合并层级、单元、度量、类型、是否免训练等6个维度，对比了12种KV Cache合并方法。

核心数据：①层级——11种为层内合并，仅KVSharer支持跨层；②单元——Token级10种（如CCM/LoMA/DMC等），CHAI为Head级，KVSharer为Layer级；③度量——余弦相似度最常用（D2O/AIM/ZeroMerge/Look-M），另有Attention Score、Sliding Window、Weighted Gaussian Kernel、Angular/Euclidean距离等；④类型——多为Many-to-One，LoMA为Many-to-Many，D2O/MinCache为Two-to-One；⑤免训练——9/12方法无需训练，仅CCM、LoMA、DMC需训练。

技术结论：表4论证了"免训练+层内+Token级+余弦相似度+多对一"已成为合并策略的主流范式（训练免费方法占75%），体现该方向正向即插即用演进。

论文作用：在KV Cache压缩分类中，该表为合并子策略提供横向基准，揭示跨层合并（KVSharer）与注意力驱动（CHAI）作为尚少探索方向的潜在机会。

### Table 5 (p.13) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab05.png]]
> [!quote] caption
> TABLE V: The summary of existing mixed-precision quantization models.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 5 横向对比 11 种 KV Cache 混合精度量化方案（含 Intial 基线），沿 Keys 量化策略、Values 粒度、重要 Token、Outlier storing、Channel Reorder 五维展开。统计：6/11 方法同时启用"重要 Token + Outlier storing"（KVQuant、SKVQ、QAQ、MiKV、GEAR、ZIPVL）；仅 SKVQ、Atom、QAQ 采用 Channel Reorder；QAQ 五维齐备最完善。该表作为量化加速章节核心对比工具，支撑作者论证"低精度 KV Cache 须多机制协同（关键 Token 保留 + 异常值外存 + 通道重排）"的关键结论，并指明自适应位宽（QAQ）与 token-locality 感知（CacheGen）为未来方向。

### Table 6 (p.14) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab06.png]]
> [!quote] caption
> TABLE VI: The summary of outlier redistribution models in Sec. IV-D3.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 图文联合解读**

**1) 核心对象与结构**：该表汇总 11 种离群值再分配（outlier redistribution）方法，按 Operation 分 6 类——Hadamard 旋转（QuaRot/Qserve/Q-INT4，共 3 种最多）、缩放（SmoothQuant、AWQ）、缩放+位移（QS+、OmniQuant）、旋转+置换（DuQuant）、仿射变换（AffineQuant、FlatQuant）、添加虚拟 token（MassiveAct）；5 种 Learnable（✓），6 种固定（✗）。

**2) 关键结论**：论文用此表论证"通过预先对权重/激活做等价变换，可将离群值分散到各通道，使后续量化更易进行"，且变换可分为无参数（旋转）与有参数（学习缩放因子）两类。

**3) 在论文中的作用**：作为 IV-D3 节"模型结构改造"分支的总览，与 Table 5 量化方法互补，支撑"改造注意力结构以降低 KV Cache 占用"的论述主线，为读者快速对比离群值处理范式提供索引。

（注：原图公式列中希腊字母部分显示为方框，但表格结构清晰可辨。）

### Table 7 (p.18) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab07.png]]
> [!quote] caption
> TABLE VII: The summary of Model-based Attention Grouping and Sharing approaches.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table VII 图文联合解读**

该表汇总 **16 种**模型驱动的注意力分组/共享方法（MQA–SVFormer），按作用位置分三类：

- **纯层内（7种）**：MQA、GQA、AsymGQA、Weighted GQA、QCQA、KDGQA 均对 **K,V** 分组，仅 **GQKVA** 含 Q；
- **纯跨层（6种）**：LCKV 共享 K,V，SA 共享 Attention Weight，SVFormer 仅共享 V，LISA/Wu et al./CLLA 共享 **Q,K,V**；
- **双轨融合（3种）**：CLA、MLKV、DHA 同时具备层内分组与跨层共享。

训练开销方面：绝大多数需完整重训或 Uptrain/Finetune，**仅 LISA 与 DHA 支持轻量适配**，是部署友好型代表。

**论证结论**：层内以 K,V 分组为主流（9/10），跨层共享成分呈"由 K,V 向 Q,K,V 乃至 Attention Weight 演进"的趋势，体现"以结构化共享压缩 KV 缓存"的架构级加速思想。

**论文作用**：与 Table 6、8 共同构成"Transformer 内部 KV 优化 → 架构级替代"双轨综述框架，扩展加速方法学视野。

### Table 8 (p.19) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab08.png]]
> [!quote] caption
> TABLE VIII: The summary of Model-based Intra-layer approaches.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 图文联合解读**

表8汇总7种基于模型的层内（Intra-layer）KV Cache加速方法，按改造方式分为两组：

- **增强架构类（3种）**：MLA[28]采用潜在压缩、FLASH[195]采用线性近似、Infini-Attention[196]采用压缩缓存——三者均需**完全重训**。
- **架构重构类（4种）**：YOCO[191]用单全局KV、CEPE[192]用并行编码交叉注意、XC-Cache[193]用编码器交叉注意、Block Transformer[194]用层级局部KV——其中CEPE与Block Transformer仅需**轻量重训**，其余2种需完全重训。

**技术结论**：该表论证了层内方案通过修改注意力/架构实现KV压缩的可行性，但普遍以重训为前提，体现"效率–训练成本"权衡。**论文作用**：作为"Model-based Intra-layer"子类的横向对照表，与层间（Inter-layer）及跨层（Cross-layer）表共同构成论文三维度分类法的关键实证支撑。

### Table 9 (p.0) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab09.png]]
> [!quote] caption
> TABLE IX: The summary of Non-Transformer Architectures.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 9 联合解读**

**1) 核心对象与结构**：表格列出 7 种非 Transformer 架构，按加速策略分两类打勾——"无传统 KV Cache"（4 项）与"KV Cache 压缩"（3 项）。具体如下：
- 无 KV Cache：RWKV（类 RNN+Transformer 并行）、Mamba（选择性状态空间）、MCSD（斜率衰减融合）、MixCon（Transformer+Conba+MoE 混合）。
- KV Cache 压缩：RetNet（保留机制）、GoldFinch（RWKV+改进 Transformer）、RecurFormer（Mamba 替换部分注意力头）。

**2) 关键结论**：论文借此证明，非 Transformer 路线通过**状态空间、保留机制、循环结构**替代 softmax 注意力，从根本上规避 KV Cache 线性膨胀问题（前三/四行），或对残余 Cache 做压缩（后三行），均能实现线性复杂度推理。

**4) 论文作用**：作为 KV Cache 加速综述的**替代方案章节**，与传统 Transformer 内 KV Cache 优化（量化、稀疏、淘汰等）形成对照，证明"换架构"是另一条加速路径。

### Table 10 (p.23) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab10.png]]
> [!quote] caption
> Comparison of Memory Management Techniques for KV Cache

> [!tip] 表格解读（多模态）
> 【图文联合解读】表10将9个LLM推理系统(vLLM、vTensor、LeanKV、DMS、eLLM、Apt-Serve、ChunkAttention、MemServe、FlashForge)在5类KV cache内存管理策略上进行"×"标记的矩阵化对比（列标题图像乱码，仅X标记可辨）。打勾分布：vLLM、LeanKV、eLLM、Apt-Serve、MemServe各命中2项；vTensor、DMS、ChunkAttention、FlashForge各1项，无系统全部覆盖。结论：各方案在内存管理维度（推测含分页、写回、共享、重计算、缓冲等）呈互补分布，无单一银弹。作用：横向梳理KV cache内存优化技术生态，为读者依据部署场景按需选型提供决策依据。

### Table 11 (p.0) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab11.png]]
> [!quote] caption
> TABLE XI: Comparison of Scheduling Approaches for KV Cache Optimization.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 11 联合解读**

表格对12种KV Cache调度方法沿6维策略（前缀感知、抢占、面向公平、层级专属、分层、动态）做勾选式归类。量化分布：单一策略中"前缀感知""抢占""层级专属"各占3项，"动态"4项最多；组合策略占6/12，其中RadixAttention（前缀+动态）、FastServe/FastSwitch（抢占+公平）、CachedAttention（层级+分层）、ALISA/LAMPS/Apt-Serve（融合2–3种）体现"多策略协同"趋势。

**关键技术结论**：单一调度维度难以同时满足吞吐、延迟与SLO公平，论文由此论证复合策略（如抢占+公平、层级+分层）已成为KV Cache调度的主流设计方向。

**论文作用**：该表与Table 10（合并/共享）、Table 12（淘汰策略）并列，构成"调度—复用—淘汰"三位一体的KV Cache优化全景图，为读者按部署场景（高并发/低延迟/多租户）选择方案提供横向索引。

### Table 14 (p.30) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab14.png]]
> [!quote] caption
> TABLE XIV: Multi-modal Benchmark Tasks. Specifically, for task abbreviation, Conv: conversation task; Desc: description task; Reas: reasoning task; Perc: perception task; Pred: prediction task; SUMM: summary task.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table XIV 图文联合解读**

**1）核心对象与结构：** 该表汇总 11 个多模态基准（每基准占两行重复），按 9 类任务维度打勾：Conv/Desc/Reas/Perc/Pred/Count/Retrieval/Order/SUMM，并标注语言。覆盖关系上，**MLVU 最广**（Perc、Pred、Retrieval、Order、SUMM 共 5 类），**MVBench** 次之（Pred、Count、Retrieval 共 3 类），LongVideoBench 覆盖 Pred+Order；语言上仅 **MMBench 为 EN/ZH 双语**，其余 10 个均为 EN。视觉问答类（MSVD-QA、MSRVTT-QA、NExT-QA）任务较窄（仅 Perc/Pred）。

**2）论证结论：** 论文用此表说明现有 KV-cache 加速方法的多模态评测已覆盖感知、预测、检索、排序、摘要等多类下游任务，具备跨基准、跨任务的泛化验证基础；同时揭示 Conv 与 Desc 类对话/描述任务在当前多模态基准中覆盖偏少，提示评估缺口。

**3）论文作用：** 属于"实验/评估链路"组件，与正文中 LLM/MLLM 加速方法（如 KV 压缩、量化、稀疏化）的效果对比章节配套，为读者按需选取多模态评测集提供索引清单。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf{Z}_i = \text{Attention}(\mathbf{Q}_i, \mathbf{K}_i, \mathbf{V}_i) = \text{Softmax}\left(\frac{\mathbf{Q}_i \mathbf{K}_i^\top}{\sqrt{d_k}}\right) \mathbf{V}_i,
$$

$$
P(x_{t+1} | x_1, x_2, \cdots, x_t) = \text{Softmax}(\mathbf{h}_t \mathbf{W}_{\text{out}} + \mathbf{b}_{\text{out}}),
$$

$$
x_{t+1} \sim P(x_{t+1} | x_1, x_2, \cdots, x_t).
$$

$$
\text{TD}(\mathbf{W}) = \prod_{k=1}^n \mathcal{T}_{(k)}[d_{k-1}, i_k, j_k, d_k],
$$

$$
\mathbf{Q}_i = \mathbf{X}\mathbf{W}_{Q_i}, \quad \mathbf{K}_i = \mathbf{X}\mathbf{W}_{K_i}, \quad \mathbf{V}_i = \mathbf{X}\mathbf{W}_{V_i},
$$

$$
\mathbf{Z}=\text{Concat}(\mathbf{Z}_1, \mathbf{Z}_2, \dots, \mathbf{Z}_h)\mathbf{W}_O,
$$

$$
\text{FFN}(\mathbf{Z}) = \sigma(\mathbf{Z}\mathbf{W}_1 + \mathbf{b}_1)\mathbf{W}_2 + \mathbf{b}_2
$$

$$
\mathbf{q}_i^t &= \mathbf{x}_t \mathbf{W}_{Q_i}, \quad \mathbf{k}_i^t = \mathbf{x}_t \mathbf{W}_{K_i}, \quad \mathbf{v}_i^t = \mathbf{x}_t \mathbf{W}_{V_i},
$$

$$
\mathbf{K}_i^{t} &= \text{Concat}(\mathbf{\hat{K}}_i^{t-1}, \mathbf{k}_i^t ), \ \mathbf{V}_i^{t} = \text{Concat}(\mathbf{\hat{V}}^{t-1}_i, \mathbf{V}_i^t ),
$$

$$
\mathbf{z}^t_i = \text{Softmax}\left(\frac{\mathbf{q}_i^t {\mathbf{K}_i^t}^\top}{\sqrt{d_k}}\right) \mathbf{V}_i^t,
$$

$$
O\left(L\cdot h \cdot t_c \cdot t \cdot (d_k+d_v)+ L\cdot h \cdot t_c\left(\triangle_1 + \triangle_2\right)\right)
$$

$$
O(L\cdot h \cdot t_c \cdot (d_k+d_v) \cdot sizeof(Float16))
$$

## 相关论文

- [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] — CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion
- [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] — KV Cache Optimization Strategies for Scalable and Efficient LLM Inference
- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] — Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter
- [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] — IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse

## 技术点深读（DEEP）

![[deep/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management.txt`（233789 字符）供引用检索。