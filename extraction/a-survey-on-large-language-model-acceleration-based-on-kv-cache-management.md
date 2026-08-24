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
> 【图文联合解读】**Table 2 联合解读**

**核心对象与结构**：该表横向汇总了 22 种 KV cache 选择/淘汰方法（如 FastGen、H2O、StreamingLLM、SnapKV、InfLLM、Quest、RetrievalAttention、MagicPIG、LoopServe 等），纵向沿 5 个维度进行二进制勾选——是否保留 Initial/Top-k/Recent tokens、是否 Permanent eviction、是否 Dynamic selection，并标注 Selection granularity（token/block/cluster/event）与核心 Remark（如 accumulative attention score、ANN search、Local Sensitive Hash、block-level KV management 等）。

**关键结论**：约 17/22 方法以 token 为粒度，3 种（InfLLM、Quest、PQCache）转向 block 粒度，SqueezedAttention 采用 cluster、EM-LLM 采用 event，体现"由 token → block/cluster/event"的粗粒化趋势；同时 Dynamic selection 已被 15 种方法采用，Top-k + Recent 组合成为主流范式，反映出动态、自适应、按重要性筛选已成为 KV cache 管理的主流设计共识。

**论文作用**：该表是综述"selection strategy"章节的核心归纳工具，用统一框架横向对比方法族，支撑后续关于"粗粒度 + 动态选择"加速范式趋势的论证，并为方法分类与实验基准选择提供索引。

### Table 4 (p.11) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab04.png]]
> [!quote] caption
> TABLE IV: The summary of existing KV Cache merging approaches.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 联合解读**

**1) 核心对象与结构**：该表汇总13种KV Cache合并方法，按Merge Layer分为两组——Cross-layer组（含CCM、LoMA、DMC、D2O、CaM、AIM、Look-M、KVMerger、CHAI等10种，✓标记在Merge Layer列）与Intra-layer组（含ZeroMerge、MinCache、KVSharer）。其余维度为Merge Unit（Token/Head/Layer）、Merge Metric（Cosine Similarity、Attention Score、Sliding Window、Weighted Gaussian Kernel、Euclidean/Angular Distance等）、Merge Type（Many-to-One / Two-to-One / Many-to-Many）、Training-free。

**2) 关键技术结论**：Token级合并单元、Many-to-One合并类型为主导路线；训练方法上10/13为Training-free（仅CCM/LoMA/DMC需训练）；Cross-layer合并数量（10）远超Intra-layer（3），说明跨层冗余利用为合并策略的研究重心。

**3) 论文整体作用**：作为KV Cache管理总分类"压缩"大类下的合并策略子表，与Table 1（量化）、Table 2（淘汰）、Table 3（共享）并列支撑综述的二维分类法，明确合并在"免训练+相似度驱动"范式下的技术定位，为后续低开销压缩方案提供选型图谱。

### Table 5 (p.13) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab05.png]]
> [!quote] caption
> TABLE V: The summary of existing mixed-precision quantization models.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 5 系统对比了 11 种 KV Cache 混合精度量化方法（含 Intial 基线），沿 **Keys 量化策略、Values 量化粒度、重要 Token 处理、Outlier storing、Channel Reorder** 等多维特征横向展开。

**Keys 量化呈多元路径**：KVQuant 用 Channel+Pre-RoPE；SKVQ/MiKV/GEAR 采用 Dynamic outlier-aware；WKVQuant 用 Learnable shifting；QAQ 实现自适应位宽；Atom 按 Group 分组；ZIPVL 仍采常规方案。Values 多为 Per-Token 或保留 Recent/Middle 窗口。辅助技术上，QAQ 同时勾选四项最为完整，SKVQ、Atom 引入 Channel Reorder 优化分布。

原文借此论证：混合精度量化的核心思想是 **"差异化位宽 + 异常值/重要 Token 保护"**，用以在精度与效率间取得权衡，奠定论文对 KV Cache 量化路径的系统化归纳。

### Table 6 (p.14) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab06.png]]
> [!quote] caption
> TABLE VI: The summary of outlier redistribution models in Sec. IV-D3.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 图文联合解读（离群值再分配模型汇总）**

1) **核心对象与结构**：表汇总 **11 种**再分配方法，按 Operation 分 **6 类**——添加虚拟 token（MassiveAct）、Hadamard 旋转（QuaRot/Qserve/Q-INT4，3 种共占 27%）、缩放（SmoothQuant）、缩放+移位（QS+/OmniQuant）、旋转+置换（DuQuant）、仿射变换（AffineQuant/FlatQuant）。Learn 列以 ✓/× 区分可学习性（约 6 个 ✓），Remarks 标注参数空间（如 H,s∈ℝᶜ）。注：图中部分公式字符（□）因字体缺失乱码，可据上下文还原为对角矩阵 diag(·)、转置 T 等。

2) **原文论证的关键结论**：支撑"再分配策略由刚性→柔性"演进——从固定 Hadamard（3 种）到可学习缩放（AWQ），再到参数化仿射变换（AffineQuant、FlatQuant 叠加分解），离群值抑制能力随参数自由度提升。

3) **论文链路作用**：作为 Sec. IV-D3 小结，串联 KV cache 量化主轴，论证"再分配→抑制离群→提升量化精度"的核心论点，为后续部署策略章节铺垫。

### Table 7 (p.18) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab07.png]]
> [!quote] caption
> TABLE VII: The summary of Model-based Attention Grouping and Sharing approaches.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 7 图文联合解读：**

该表汇总 **16 种**基于模型的注意力分组/共享方法，沿四条维度横向对比：① 方法名、② 应用位置（层内/跨层）、③ 层内分组组件、④ 跨层共享组件、⑤ 是否需重训练。

**1）核心结构与数据**：层内类 8 种（含 MQA、GQA、AsymGQA、Weighted GQA、QCQA、KDGQA、GQKVA、MLKV、DHA），其中 7 种对 K、V 分组，仅 GQKVA 对 Q、K、V 全分组；跨层类 6 种（LCKV、SA、LISA、Wu et al.、CLLA、SVFormer），共享对象覆盖 K&V、Q/K/V、仅 V 或 Attention Weight；混合位置仅 CLA、MLKV、DHA 三种。所有方法几乎都需重训练，仅 LISA、DHA 采用轻量适配。

**2）关键结论**：K、V 是分组/共享的最普遍组件；层内方法聚焦多头压缩，跨层方法侧重层间冗余消除，两者结合（MLKV、DHA）成为趋势。

**3）论文作用**：作为 KV Cache 管理分类体系中"模型结构改造"分支的总览表，与 Table 6（量化/合并）互补，支撑论文"通过修改注意力结构降低 KV Cache 占用"的论述主线。

### Table 8 (p.19) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab08.png]]
> [!quote] caption
> TABLE VIII: The summary of Model-based Intra-layer approaches.

> [!tip] 表格解读（多模态）
> 【图文联合解读】## Table 8 图文联合解读

**1) 核心对象与结构**
表格汇总了 7 种**模型驱动的层内（Intra-layer）** KV Cache 管理方法，分为两大类：
- **Enhanced Attention**（增强注意力，3 种，均属 Augmented Architecture）：MLA（Latent compression）、FLASH（Linear approximation）、Infini-Attention（Compressive cache）；
- **Transformer 架构改造类**（4 种）：YOCO（Single global KV cache）、CEPE（Parallel encoding with cross-attn）、XC-Cache（Encoder cross-attention）、Block Transformer（Hierarchical local KV）。
最后一列标注训练代价：MLA/FLASH/Infini-Attention/YOCO/XC-Cache 需**完全重训**，仅 CEPE 与 Block Transformer 为 **Lightweight**。

**2) 论证的关键技术结论**
该表说明层内优化并非单一路径：可通过**注意力机制重写**（压缩、线性化、压缩记忆）实现 KV 压缩，也可通过**全局缓存、跨注意力编码、分层局部 KV**重构整体架构；多数方案需重训练，少数支持轻量适配。

**3) 在论文中的作用**
作为综述的核心对照表之一，与 Table 5/6/7（Cross-layer / Within-layer 等）并列，从**改动粒度维度**系统呈现 KV Cache 加速方法谱系，为读者横向比较方法代价与适用场景提供依据。

### Table 9 (p.0) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab09.png]]
> [!quote] caption
> TABLE IX: The summary of Non-Transformer Architectures.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 9 联合解读**

**1) 核心结构与数据**：该表汇总 7 种非 Transformer 架构，分四列——Method、Key Mechanism、No Traditional KV Cache、KV Cache Compression。其中 RWKV（线性注意力+RNN 并行）、Mamba（选择性状态空间）、MCSD（斜率衰减融合）、MixCon（Transformer+Conba+MoE）共 4 项标注"无传统 KV 缓存"；RetNet（保留机制）、GoldFinch（RWKV+改进 Transformer）、RecurFormer（Mamba 替换部分注意力头）共 3 项标注"KV 缓存压缩"。

**2) 关键结论**：非 Transformer 架构并非简单优化 KV 缓存，而是从根本上规避或替代注意力缓存机制，从架构层面实现推理加速，与 Transformer 内的 KV 缓存管理形成互补的技术路径。

**3) 论文作用**：与 Table 7、8 共同构成"Transformer 内部 KV 缓存优化→架构级替代"的双轨综述框架，扩展加速方法学的视野。

### Table 11 (p.0) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab11.png]]
> [!quote] caption
> TABLE XI: Comparison of Scheduling Approaches for KV Cache Optimization.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表11图文联合解读：**

表11以6项调度特征（Prefix-aware、Preemptive、Fairness-oriented、Layer-specific、Hierarchical、Dynamic）为列、12种KV缓存调度系统为行构建对照矩阵。数据呈明显策略聚类：批量类（BatchLLM/RadixAttention/Echo）独占Prefix-aware；切换类（FastServe/FlowKV/FastSwitch）含Preemptive，且FastServe/FastSwitch额外覆盖Fairness-oriented；层缓存类（LayerKV/CachedAttention）聚焦Layer-specific；混合感知类（ALISA/LAMPS/Apt-Serve/FGOS）主导Hierarchical与Dynamic，每系统仅实现1-2维特征。原文据此论证KV缓存调度无通用最优方案、各机制互补而非替代，作为全文按策略分类综述加速方法学体系的核心支撑。

### Table 14 (p.30) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab14.png]]
> [!quote] caption
> TABLE XIV: Multi-modal Benchmark Tasks. Specifically, for task abbreviation, Conv: conversation task; Desc: description task; Reas: reasoning task; Perc: perception task; Pred: prediction task; SUMM: summary task.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table XIV 图文联合解读：**

1) **核心结构与数据**：该表枚举10个多模态基准（LLaVA-Bench、MMBench、MileBench、MLVU、LongVideoBench、Video-MME、NExT-QA、MVBench、MSVD-QA、MSRVTT-QA），沿9个任务维度（Conv/Desc/Reas/Perc/Pred/Count/Retrieval/Order/SUMM）打勾标注，并附语言支持。MLVU覆盖最广（含Conv、Perc、Pred、Retrieval、Order、SUMM 6类），任务最单一的是MSVD-QA、MSRVTT-QA（仅Reas）。语言上仅MMBench支持EN/ZH双语，其余9项均为EN。

2) **技术结论**：原文借此论证——多模态场景下的KV-Cache压缩方案必须同时应对**长视频、检索、计数、排序、摘要**等多类异构任务，而非仅文本对话；并揭示当前评估生态以英文为主，对中文多模态的覆盖明显不足。

3) **论文作用**：作为KV-Cache加速方法在**多模态LLM**分支的评测清单，与前面表格的纯文本基准互补，为后续方法对比提供统一任务坐标。

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