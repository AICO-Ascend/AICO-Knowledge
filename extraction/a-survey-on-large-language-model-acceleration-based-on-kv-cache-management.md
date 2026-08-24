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
> 【图文联合解读】该表横向对比22种KV Cache选择方法，沿"初始/Top-k/近期token、永久驱逐、动态选择、粒度"四类特征勾选。数据上：Top-k使用最广（21/22），近期token约15种，初始token仅6种；16种支持永久驱逐；粒度以token为主（17种），另有block(3)、cluster、event各1种。原文借此论证：KV Cache管理已由单一保留策略演化为"多策略融合+动态选择+粗粒度"体系，Top-k与近期token为通用基线，永久驱逐成主流，block/cluster粒度与量化检索类方法代表新方向。本表是论文KV Cache分类总览的核心索引，为后文按"选择—驱逐—量化"展开提供全景参照。

### Table 4 (p.11) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab04.png]]
> [!quote] caption
> TABLE IV: The summary of existing KV Cache merging approaches.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 联合解读**

该表对比12种KV Cache合并方法，从合并层级、单元、度量、类型、是否免训练6维度展开。统计显示：9种层内合并（仅ZeroMerge/MinCache/KVSharer跨层），合并单元以Token为主（10种，CHAI用Head、KVSharer用Layer），Many-to-One最多（9种），LoMA为Many-to-Many，D2O/MinCache为Two-to-One；Cosine Similarity度量最常用（4次）；仅CCM/LoMA/DMC需训练，其余9种免训练。

论文借此建立合并方法的系统分类体系，揭示"层内+Token级+Many-to-One+免训练"为主流范式，作为整篇KV Cache加速综述中合并策略子方向的核心归纳表。

### Table 5 (p.13) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab05.png]]
> [!quote] caption
> TABLE V: The summary of existing mixed-precision quantization models.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表5以11个条目（含Initial）为对象，按Key量化、Value粒度、重要Token、Outlier外存和通道重排5维比较。基线采用Middle Key、Recent Value；KIVI为Channel/Per-Token，QAQ采用自适应位宽，CacheGen强调分层与token-locality。6/11兼用重要Token与异常值外存，仅SKVQ、Atom、QAQ重排通道，QAQ机制最全。该表连接方案设计与实验讨论，支撑“多机制协同”结论，并指向自适应位宽与局部性方向；其本身不含精度、速度数据，不能单独验证性能。

### Table 6 (p.14) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab06.png]]
> [!quote] caption
> TABLE VI: The summary of outlier redistribution models in Sec. IV-D3.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读**

表6归集Sec. IV-D3中**11种离群值再分配**模型，按操作分5族：①虚拟令牌——MassiveAct(1)；②Hadamard旋转——QuaRot/Qserve/Q-INT4(3)；③对角缩放/移位——SmoothQuant、QS+(2)；④可学习缩放移位——AWQ、OmniQuant(2)；⑤旋转+置换DuQuant、仿射变换AffineQuant/FlatQuant(3)。**6/11支持可学习参数**。

**关键结论**：离群值再分配是低位量化的前置步骤，操作路径沿"固定旋转→对角缩放→缩放+移位→可学习仿射变换"逐级增强表征能力；Hadamard族公式统一形式为$\hat{W}=WH^T$，约束$H^T H=I$以等方差抹平极端值。

**论文作用**：与Table 6、8并列构成"Transformer内KV优化→架构级替代"双轨框架，本表专责量化侧离群值处理方法学图谱，为低比特加速章节提供系统索引。

### Table 7 (p.18) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab07.png]]
> [!quote] caption
> TABLE VII: The summary of Model-based Attention Grouping and Sharing approaches.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 表格核心内容：** Table 7 系统汇总了 16 种 Model-based 注意力分组/共享方法，列维度包括：方法名、应用位置（层内/跨层）、层内分组组件、跨层共享组件、是否需重训练。其中纯跨层方法 7 种（MQA、GQA、AsymGQA、Weighted GQA、QCQA、KDGQA、GQKVA），纯层内 6 种（LCKV、SA、LISA、Wu et al.、CLLA、SVFormer），同时跨层+层内仅 3 种（CLA、MLKV、DHA）。

**2) 关键结论：** 跨层共享几乎都以 K、V 为主（7/7 仅共享 K,V），仅 GQKVA 共享 Q,K,V；层内分组则呈现"K,V"（MQA 类）与"Q,K,V/Attention Weight"（SA、LISA 等）两条路线。大多方法需重训练，但 MLKV 支持 Uptrain，LISA 与 DHA 支持 Lightweight adaption，体现从"训练改造"向"轻量适配"的演进。

**3) 论文作用：** 作为综述方法分类的子表之一，与 Table 6（量化）、Table 8（合并）等并列，共同构成 KV Cache 管理的完整分类体系；该表聚焦"模型结构层面"的压缩策略，体现从单维度（仅层内或仅跨层）向双维度协同（CLA/MLKV/DHA）发展的技术趋势。

### Table 8 (p.19) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab08.png]]
> [!quote] caption
> TABLE VIII: The summary of Model-based Intra-layer approaches.

> [!tip] 表格解读（多模态）
> 【图文联合解读】# Table 8 图文联合解读

**核心对象与结构**：表格汇总7种"基于模型的层内（Intra-layer）"KV Cache管理方法，按改造方式分为两类——**Enhanced Attention（增强注意力，3种）**：MLA（潜在压缩）、FLASH（线性近似）、Infini-Attention（压缩缓存）；**第二类（4种）**：YOCO（单一全局KV）、CEPE（并行编码+交叉注意力）、XC-Cache（编码器交叉注意力）、Block Transformer（分层局部KV）。所有方法"Alteration Type"列均打勾（✓），且全部需要重训练或轻量训练。

**关键技术结论**：层内方法通过**修改模型内部架构**直接降低KV Cache开销；KV Cache管理策略呈多样化（压缩、线性化、全局共享、分层），且**无一例外需要训练**，这是与训练无关方法的本质区别；CEPE与Block Transformer为"Lightweight"，部署门槛相对较低。

**论文链路作用**：与Inter-layer、Cross-layer及训练无关方法并列，构成论文"Model-based vs Training-free"分类框架下的重要分支，系统呈现需改模型的层内优化全景。

### Table 9 (p.0) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab09.png]]
> [!quote] caption
> TABLE IX: The summary of Non-Transformer Architectures.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 9 图文联合解读**

该表汇总 7 种非 Transformer 架构对 KV Cache 的两类处理路径：
- **4 种"无传统 KV Cache"**（RWKV、Mamba、MCSD、MixCon）：分别采用 RNN-like 线性并行、选择性状态空间、斜率衰减融合、Conba+MoE 混合机制，从架构层面彻底摒弃 KV Cache。
- **3 种"KV Cache 压缩"**（RetNet、GoldFinch、RecurFormer）：分别用保留机制、RWKV 改进 Transformer、Mamba 替换部分注意力头，仍保留但压缩 Cache。

**核心结论**：原文借此论证 LLM 加速存在两条替代路线——**架构原生规避**（线性/状态空间替代注意力）与**在 Transformer 内压缩**，二者均绕开标准 KV Cache 的显存与复杂度瓶颈。

**论文作用**：与前文 Transformer-based KV Cache 优化方法互补，形成"主流架构内压缩 + 非 Transformer 架构替代"的完整加速图景，为读者提供体系化设计选型参考。

### Table 10 (p.23) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab10.png]]
> [!quote] caption
> TABLE X: Comparison of Memory Management Techniques for KV Cache Optimization.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 10 图文联合解读**

**1) 核心对象与结构**：表格以9种代表性方法（vLLM、vTensor、LeanKV、DMS、eLLM、Apt-Serve、ChunkAttention、MemServe、FlashForge）为行，5种内存管理技术（Paged Memory、Virtual Memory、Dynamic Sparsity、Prefix Sharing、Distributed Memory）为列，用"✓"标记每种方法所采用的技术组合。其中vLLM同时采用分页+虚拟内存（2项），MemServe/eLLM/Apt-Serve则融合虚拟内存与分布式内存；LeanKV、DMS专注于动态稀疏；ChunkAttention、FlashForge则聚焦前缀共享。

**2) 关键技术结论**：说明当前KV Cache优化无单一通用方案，各方法沿"分页/虚拟化/稀疏/共享/分布式"五条技术路径形成互补。

**3) 论文中的作用**：作为综述分类表，建立KV Cache内存管理技术体系，为后续按技术维度展开的方法学分析提供索引框架。

### Table 11 (p.0) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab11.png]]
> [!quote] caption
> TABLE XI: Comparison of Scheduling Approaches for KV Cache Optimization.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

表11横向比较12种KV Cache调度方法在6维特征（Prefix-aware / Preemptive / Fairness-oriented / Layer-specific / Hierarchical / Dynamic）上的覆盖。量化数据：Dynamic维度最普遍（5/12：RadixAttention、ALISA、LAMPS、Apt-Serve、FGOS）；Prefix-aware、Preemptive、Layer-specific、Hierarchical各3项；Fairness-oriented仅2项，且必与Preemptive共现（FastServe、FastSwitch）。

**关键结论**：多数方法专精单一维度，而FastServe/FastSwitch以"抢占+公平"组合形成差异化定位，CachedAttention、LAMPS、Apt-Serve代表多维融合方向；整体揭示调度策略从单维优化向多维动态协作演进。

**论文作用**：作为调度策略分类表，与压缩、稀疏类表构成"压缩—管理—稀疏"完整对照体系，为读者选取KV Cache优化方案提供决策依据。

### Table 12 (p.26) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab12.png]]
> [!quote] caption
> TABLE XII: Comparison of Hardware-aware Design Approaches for KV Cache Optimization.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 12 横向对比 24 种硬件感知 KV Cache 优化方法，按 4 类硬件策略打标：Single/Multi-GPU（9 项，如 DeFT、vLLM、ORCA）、Heterogeneous（8 项，如 APEX、DistServ、HCache、InstInfer）、I/O-aware（6 项，如 Bifurcated Attention、FastDecode、Tree Attention）、SSD-based（3 项：Cake、FlexInfer、Multi-Bin Batching）。其中 FlashAttention 与 gLLM 同时占据 Single/Multi-GPU 与 Heterogeneous 两列，凸显"单/多卡+异构"跨层次融合趋势。该表与 Table 10、11 并列，构成"调度—复用—淘汰"三位一体全景图，为读者按高并发/低延迟/多租户等部署场景横向选型提供索引。

### Table 13 (p.28) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab13.png]]
> [!quote] caption
> TABLE XIII: Long-context Text Benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 13 梳理了 13 个长上下文文本评测基准，沿 Q-A、摘要、推理、检索、生成、聚合 6 类任务和语种两维展开。数据要点：①LongBench、L-Eval、LongEval 任务覆盖面最广（5/6 类），LongBench 与 M4LE 支持中英双语，OneRuler 扩展至 26 种语言；②推理与生成是多数基准（≥10/13）的核心维度，Q-A 与摘要仅 LongBench 等少数覆盖；③检索维度被约 10 个基准采纳，BAMBOO/ZEROSCROLLS 覆盖最窄。

在论文方法链中，该表支撑"KV-Cache 加速方法需在多任务长上下文基准上验证"这一论断。它揭示了基准任务的覆盖不均（Q-A、摘要缺位）与多语种评估薄弱的现状，为加速方法的公平对比、评测协议选择以及后续研究指引（如补齐摘要与多语种评估）提供了工具清单与缺口依据。

### Table 14 (p.30) ⭐深度解读
![[assets/crops/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management-tab14.png]]
> [!quote] caption
> TABLE XIV: Multi-modal Benchmark Tasks. Specifically, for task abbreviation, Conv: conversation task; Desc: description task; Reas: reasoning task; Perc: perception task; Pred: prediction task; SUMM: summary task.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

表格汇总10个多模态基准（LLaVA-Bench、MMBench、MileBench、MLVU、LongVideoBench、Video-MME、NExT-QA、MVBench、MSVD-QA、MSRVTT-QA），按 Conv/Desc/Reas/Perc/Pred/Count/Retrieval/Order/SUMM 共9类任务勾选支持能力并标注语种。MLVU覆盖最广（Reas+Perc+Pred+Retrieval+Order+SUMM共6类），多数基准聚焦"推理+感知+预测"组合；仅MMBench支持中英双语，其余均为英文。

**技术结论：** 表明多模态场景下KV-Cache加速方法需在推理、感知、预测、检索、排序、摘要等异构任务上保持鲁棒，加速方案应具备任务无关的通用性。

**论文作用：** 作为实验链路的多模态评测清单，为不同KV-Cache压缩/管理方法的横向对比提供统一任务维度，支撑长视频与多模态LLM加速的实证评估。

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