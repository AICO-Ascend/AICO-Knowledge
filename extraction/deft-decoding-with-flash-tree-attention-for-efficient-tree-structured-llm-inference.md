---
paper_num: "53"
title: "DeFT: Decoding with Flash Tree-attention for Efficient Tree-structured LLM Inference"
authors: ""
date: "2024/4/1"
arxiv: "https://arxiv.org/abs/2404.00242"
pdf: "papers/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference.pdf"
slug: "deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference"
tags: []
---

# DeFT: Decoding with Flash Tree-attention for Efficient Tree-structured LLM Inference

> [!abstract] 摘要（原文）
> 1. Large language models (LLMs) are increasingly employed for complex tasks that process multiple generation calls in a tree structure with shared prefixes of tokens, including few-shot prompting, multi-step reasoning, speculative decoding, etc. However, existing inference systems for tree-based applications are inefficient due to improper partitioning of queries and KV cache duri

## 元信息
- **发表日期**: 2024/4/1
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2404.00242
- **本地 PDF**: `papers/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference.pdf`
- **页数**: 32

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig01.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p01.png]]*
> [!quote] caption
> Usually, these applications produce substantially more tokens than traditional ones, to provide large space for tree search (Graves, 2012; Lu et al., 2022; Liu et al., 2023) or selection, as shown in Table 1.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图1将序列式解码（上：两独立Prompt各生成一条）与树式解码（下：四类场景）对比：(1) Self-consistency——单Prompt分支G₁/G₂；(2) Few-shot prompting——示例+P₁/P₂并行生成；(3) Tree-of-thoughts——P经Search History多层分支为P₁.₁/P₁.₂/P₂.₁/P₂.₂及对应生成；(4) Speculative decoding——draft产出token树t₀–t₄，verify后保留t₀/t₂/t₄的KV cache。配色区分蓝色shareable KV、黄色非共享生成。

**技术结论：** 原文借此说明树搜索/选择类应用产出的token量远多于传统任务，而树结构中存在大量共享前缀（蓝色KV），但序列式注意力无法利用此冗余。

**链路作用：** 作为动机图，引出DEFT需设计Flash Tree Attention以高效处理共享与非共享KV并存的结构化推理。

### Figure 2 (p.5) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig02.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p05.png]]*
> [!quote] caption
> Overview of DEFT. Input Metadata is prepared in the system elaborated in Appendix A.1. In QKV

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示DEFT两阶段流水线：①阶段1（QKV Preparation）在HBM中读取含共享前缀的Tree KV（KV₀/KV₁/KV₂），经KV-Guided Grouping扁平分组为G₀/G₁/G₂，按IO感知与负载均衡加载至对应SM₀/₁/₂；②阶段2（Attention Calculation）在Shared Memory（19 TB/s）内并行运行DEFT Attention Kernel得局部A₀/A₁/A₂，再经Global Reduction合并为Final Attention。

原文据此论证：利用HBM（2 TB/s）与SM（19 TB/s）近10×带宽差，将树结构推测解码中的共享前缀复用与并行注意力解耦，缓解KV加载瓶颈。该图为全文方法总览，衔接§3.3 QKV准备细节与后续注意力核性能分析。

### Figure 3 (p.6) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig03.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p06.png]]*
> [!quote] caption
> Comparison of QKV partitioning strategies during the QKV Preparation Phase between DEFT-

> [!tip] 技术解读（多模态）
> 【图文联合解读】图3展示QKV准备阶段分区策略对比：

**(a)** 两级级联解码树含查询Qa/Qb与节点KV0-KV2；Vanilla Tree Attention无分区并行度低；Q-Guided Grouping仅2组（Flash-Attention采用，G0:Qa+KV0+KV1, G1:Qb+KV0+KV2）；KV-Guided（本文）按KV对应查询分组提升并行度。

**(b)** Flash-Decoding/Radix对Q-Guided再做KV切分得G00-G11四组，但仍无KV IO感知；本文DeFT-Node按节点分3组（G0:Qa+Qb+KV0, G1:Qa+KV1, G2:Qb+KV2），DeFT-Node-Chunk再切节点KV得G00/G01/G1/G2四组。

**(c)** DeFT-Flatten通过深度优先展平→均匀块切→64位位因果掩码(KV-BCM，按KV块归属节点标记)，实现G0/G1/G2负载均衡。红色框标各组HBM-SharedMemory间IO量。

**论证**：逻辑分区不增QKV数据搬移成本，KV-Guided以IO感知实现高并行，奠基Attention阶段高效加载。

**论文作用**：作为DeFT核心图示，确立从Q导向到KV导向分区的演进路线，支撑Flash Tree Attention整体框架。

### Figure 4 (p.9) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig04.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p09.png]]*
> [!quote] caption
> Latency breakdown for specula- tive decoding with a token tree of 32 queries, whose tree topology is from Medusa (Cai et al., 2024). U means unpaged memory.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示6种注意力方法在Medusa树形拓扑（size=32）下的延迟分解（Attention/KV Management/Other三类）。量化结果：DeFT-Flatten约50s最低（Other 57.08%），DeFT-Node-Chunk约53s次之；非分页版DeFT-Node(U)飙至193s、Tree Attention-Medusa(U)达278s，其KV Management占比分别高达69.11%与83.40%。

技术结论：分页KV管理是消除树形spec decoding瓶颈的关键——非分页实现因KV管理主导而严重劣化。

论文作用：作为动机实验，量化证明Flash Tree Attention搭配分页存储的必要性，为DeFT方法的有效性提供实证支撑。

### Figure 5 (p.15) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig05.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p15.png]]*
> [!quote] caption
> Illustration of DEFT. (Left) System overview. (Right) The data flow of DEFT-Node (DEFT-Flatten is similar except for QKV partitioning) using a decoding tree example.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 5）**

左图展示DEFT系统四模块——模型接口（含DeFT Attention Kernel×#layer）、KV Cache Manager、Sequence Tree Manager与Branch Controller，通过Query/KV/Tree Topology三路元数据协同；右图以iter=0提示"Machine Learning"(S₀)在iter=3分叉为S₁"System is difficult"与S₂"has changed the"为例，按KV分组打包QKV（如Group 1：KV="System is difficult" + Q="difficult"）后送入注意力核并行计算。该图论证"按KV分组的Flash树形Attention"是消除树解码QKV冗余的核心机制，为Table 5的延迟对比实验提供方法学支撑。

### Figure 6 (p.16) ⭐深度解读
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p16.png]]
> [!quote] caption
> Discussion of tree-based decoding with tree queries (Miao et al., 2023) and tree KV.

> [!tip] 技术解读（多模态）
> **Figure 6 Description (architecture/components/data flow + key takeaway)**

The figure illustrates tree-based decoding in two parts. **(a)** shows two query topologies paired with their KV caches: a *Sequence KV* (s₀) feeding a flat **Query Token Tree** of up to 64 tokens (t₁→t₂, t₃, t₄, t₅), versus a *Tree KV* (s₀ branching into s₁, s₂) paired with parallel queries (t₁, t₂), enabling shared-prefix reuse. **(b)** shows the **Bit Mask** mechanism: each query token tᵢ carries a 64-bit mask M[tᵢ] encoding causal connectivity (pᵢ bits: 1=no mask, 0=masked) between the token tree and tᵢ.

**Key takeaway:** Causal correctness in parallel tree decoding is preserved by a per-token 64-bit bit mask, which is far more storage-efficient than materializing full causal masks while still supporting speculative/multi-step reasoning workloads.

**Caption (verbatim):**
Figure 6: Discussion of tree-based decoding with tree queries (Miao et al., 2023) and tree KV.

### Figure 7 (p.17) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig07.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p17.png]]*
> [!quote] caption
> Analysis for two case studies of tree-based decoding. (Left) Multi-step reasoning. (Right) Speculative decoding. Blue boxes mean shareable past KV cache in storage and memory access during the tree attention calculation, while yellow boxes mean the KV cache of generated context. which states to pursue further and the sequence in which to explore them; (3) Tree Search-based

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图7联合解读：**

图7对比两类树状解码的KV缓存复用。左为多步推理：提示P经两步TreeAttention生成G₁、G₂，再树搜索扩展为4叶节点(G₁.₁/G₁.₂/G₂.₁/G₂.₂)；右为投机解码：草稿模型产出5节点token树T_t(t₀→t₁/t₂,t₃→t₄)，验证后保留V_t={t₀,t₂,t₄}进入下一步G₃。蓝色框（共享历史KV）与黄色框（生成KV）的统一配色，论证DeFT的Flash Tree Attention KV缓存共享机制对**多步推理**与**投机解码**两类树状推理场景均通用，体现其作为统一加速方案的普适性，为论文核心实验对比提供方法论支撑。

### Figure 8 (p.19) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig08.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p19.png]]*
> [!quote] caption
> Operations of Tree Attention-Medusa (Cai et al., 2024). No Kernel Fusion or Tiling strategy is applied, which introduces significant IO of partial results like QK⊤, DCM, and Softmax between GPU global memory and on-chip shared memory.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示 Medusa 树形注意力逐算子流程：左侧给出 KV0/KV1/KV2 三节点树拓扑及稠密因果掩码 DCM，Q/K 经 GEMM 分块（m×k、k×n）后写入 HBM；右侧 SM 通过多次 Load/Write 从 HBM 反复读取 S、S′、Ms、P 等中间结果，依次完成 S=QK⊤、S/Sc、S+DCM、Softmax、O=PV 全链路，每步都伴随一次全局内存往返。原文据此论证：未采用 Kernel Fusion 与 Tiling，导致 QK⊤、DCM、Softmax 等中间量产生显著冗余 IO。该图在论文中充当低效基线，反衬 DEFT 所提 Flash Tree Attention 融合分块策略的必要性。

### Figure 9 (p.19) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig09.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p19.png]]*
> [!quote] caption
> Overview of two stages in DEFT Attention Kernel (DEFT-Node for example, and DEFT-Flatten is similar). Stage 1–calculate partial attentions. Based on the QKV grouping results after KV-Guided Grouping

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图9深度解读**

图示DEFT-Node两阶段kernel：3组QKV（G0=Q1·KV0、G1=Q1·KV1、G2=Q2·KV2）构成KV0→{KV1,KV2}的树拓扑（Tree Topo）。Stage1各组在SM上并行FlashAttn得PA_i与LSE_i写回HBM；Stage2从HBM加载PA₀:₂+LSE₀:₂至SM₃，依TreeTopo做DeFT_reduction归约为全局Attention。

**论证结论**：相比中间量（QK⊤、Softmax、P）频繁往返HBM的未融合kernel，该设计融合组内计算并以tree-aware LSE归约避免中间结果全局物化，显著降低IO并充分利用共享内存。

**论文作用**：作为DeFT树结构解码核心机制的可视化基础，衔接KV-Guided Grouping与FlashAttention分块思想，支撑高效树结构LLM推理的整体论证链。

### Figure 10 (p.20) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig10.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p20.png]]*
> [!quote] caption
> Detailed attention operations of DEFT kernel (DEFT-Node for example, and DEFT-Flatten is similar). Based on the same decoding tree in Figure 3.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 10b · Stage 2）：**

1) **核心对象与结构**：图示 Stage 1 输出的 4 组偏量——`Q1/KV0→(lse0,lse1,PA0,PA1)`、`Q1/KV1→(lse2,PA2)`、`Q1/KV2→(lse3,PA3)`、`Q2/KV0→偏量`。中部"Remap LSEᵢ and PAᵢ for each Query"将其按查询重组为 **Lse/PA Map for Q1**（lse0,lse2,PA0,PA2）和 **for Q2**（lse1,lse3,PA1,PA3），再由右侧 *Global reduction kernel* 用 LogSumExp 合并为最终 **Attention of Q1,Q2**。

2) **论证结论**：偏量可按 Query 归并复用，证明树形解码中"共享 KV"路径只需按 Q 分组做一次全局归约，即可数值稳定地得到与全量 FlashAttention 等价的结果，从而把多 QKV 组并行计算与单次 Reduce 衔接。

3) **方法链路作用**：补全 Figure 10(a) 两阶段内核的 Stage 2 实现细节，支撑"分 QKV 组并行 + 按 Query 归约"的核心架构，是论文证明 DEFT-Node/Flatten 在树状投机解码中正确且高效的关键图示。

### Figure 11 (p.21) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig11.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p21.png]]*
> [!quote] caption
> When the number of leaf nodes/queries ln is sufficiently large, the IO cost of partial results might become comparable to that of the KV cache. For instance, in the Llama models (Touvron et al., 2023a;b), where dhead =128, with ln =29, the total IO cost of QKT , M, QK⊤ sc , M + QK⊤ sc , and

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构：**
图分三栏对比 QKV 分块策略——左栏 Vanilla Tree Attention 展示 G₀ 中 Q_a、Q_b 与 KV₀/KV₁/KV₂ 的关系，用 3×3 掩码矩阵 M 标出 KV-Guided Grouping；中栏 Medusa 采用 GEMM 分块（Q 块 m×k，KV 块 k×n），DCM 退化为单块 m×n；右栏 SpecInfer 用 Q-BCM 二值掩码 "110"（Q_a）和 "101"（Q_b）做 Q-Guided Grouping。

**2) 关键技术结论：**
Vanilla 的 KV-Guided Grouping 产生大量空块浪费；Medusa 的 GEMM 均匀分块忽略树结构掩码；SpecInfer 的 Q-Guided Grouping 按查询精准定位所需 KV，三者在内存访问粒度与计算冗余上各有权衡，凸显需要专门的树注意力内核。

**3) 论文作用：**
作为 Figure 3 的补充，该图铺垫 DEFT 设计的动机——证明现有树注意力实现未能联合优化分块与掩码，支撑 Flash Tree Attention 借助分块稀疏矩阵乘融合 KV-Guided/Q-Guided 分组的必要性。

### Figure 12 (p.23) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig12.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p23.png]]*
> [!quote] caption
> The detailed procedure of reconstructing tree templates for multi-step reasoning. (Left)

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图12图文联合解读**

图12展示DEFT从实际多步推理记录重建思维树模板的过程。左侧从Prompt出发构建深度d、宽度w的思维树（节点thought i,j），用✓保留最优路径、⊖标记待剪枝节点；右侧将每个思维编码为五元组元数据（start_iter=100, end_iter=103, thought_size=3, parent_id=thought i-1,k, children_id=None），并据此导出Branch records（迭代100，从(i-1,k)生成(i,j)）与Prune records（迭代103，剪枝(i,j)）。该图论证了树模板可由真实推理轨迹结构化重建，为FlashTreeAttention的高效树状批解码提供预处理输入，是DEFT方法链路的模板构建核心环节。

### Figure 13 (p.25) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig13.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p25.png]]*
> [!quote] caption
> Comparison of split strategies DEFT-Node and DEFT-Flatten in sorting task. Speedup ratio refers to the ratio between the per iteration latency of DEFT-Node and DEFT-Flatten. Tree Node Len std represents the standard deviation of the tree node lengths for each iteration.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图13以sorting任务为载体，对比DEFT-Node与DEFT-Flatten两种分割策略。横轴为推理步数（0–3500），蓝色实线为加速比（Node/Flatten每步延迟比，左轴1.25–2.0），红色虚线为树节点长度标准差（右轴150–400）。可见：节点长度std较低时，加速比稳定在1.3–2.0区间；std出现周期性尖峰（如step≈700处飙至400）时，加速比同步骤降，极端点甚至跌至0.25以下。

**技术结论：** 树节点长度方差小→DEFT-Node更优（加速1.5×+）；方差大→Flatten反超，揭示两种策略存在互补适用域。

**论文作用：** 属实验消融分析，为DEFT依据负载特征自适应选择分割策略提供量化依据，支撑整体系统的鲁棒性论证。

### Figure 14 (p.26) ⭐深度解读
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p26.png]]
> [!quote] caption
> Per iteration latency for few-shot prompting tasks with different tree width. e2e means decoding latency(optimal end-to-end latency), while Attn means only the attention overhead.

> [!tip] 技术解读（多模态）
> **Architecture/Components/Data Flow:**
Figure 14 is a 2×2 grid of line plots showing per-iteration latency (Time, ms) over 400 decoding steps for few-shot prompting tasks. Each subplot varies the tree width (10, 20, 30, 50). Five curves are compared per subplot: DeFT-Flatten-e2e, Radix-e2e, DeFT-Flatten-Attn, Radix-Attn, and Medusa-Attn. The "e2e" curves measure end-to-end decoding latency, while "Attn" curves isolate attention overhead, allowing joint visualization of system-level vs. kernel-level performance as tree topology changes.

**Key Technical Takeaway:**
DeFT-Flatten's relative advantage over Radix Attention grows monotonically with tree width (1.24× at w=20, 1.33× at w=50) because wider trees increase KV-cache prefix reuse across parallel speculative-decoding branches, while attention overhead in competing schemes (e.g., Medusa) scales linearly with tree width via DCM growth.

**Caption (verbatim):**
"Figure 14: Per iteration latency for few-shot prompting tasks with different tree width. *e2e* means decoding latency(optimal end-to-end latency), while *Attn* means only the attention overhead."

### Figure 15 (p.26) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig15.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p26.png]]*
> [!quote] caption
> The chunk size selection is a trade-off between IO redundancy and threadblock scheduling: a larger chunk size means less redundancy of Query IO but may cause potential idle SMs of GPUs due to fewer threadblocks during GPU scheduling.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图15在Prompt长度=1000与4000两组下，给出**单层Attention延迟(μs)随KV Chunk Size(128/256/512/1024)** 的消融曲线，对比 **DeFT-Flatten（实线）** 与 **DeFT-Node-Chunk（虚线）** 在候选树规模 **t=32/64/128/256** 四档下的性能。

核心结论：延迟随chunk增大**先降后微升**，最优chunk size集中在 **256–512**；以t=256、Prompt=4000为例，延迟从chunk=128时约1190μs降至chunk=512时约680μs；DeFT-Flatten整体略优于Node-Chunk。该结果直接呼应caption所述——chunk size是**Query IO冗余与SM线程块调度**的折中。

在论文中，该消融为DeFT采用Flatten策略及推荐KV切分超参提供了实证依据，是方法选型与性能优化闭环的关键一环。

### Figure 16 (p.27) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig16.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p27.png]]*
> [!quote] caption
> Time per output token(TPOT) of DEFT with different prompt lengths in speculative decoding. 2500 5000 7500 10000 12500 15000 17500 20000

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 16）**

1）**核心对象与数据**：图16为双子图（token树大小 t=32 与 t=64），横轴为 prompt 长度（2500–20000 tokens），纵轴为 TPOT（ms/token），生成长度固定为 1000，对比 Radix-Attention、DEFT-Flatten、DEFT-Node、DEFT-Node-Chunk 四种方法。在 prompt=20000、t=64 时，Radix-Attention 约 37 ms/token，DEFT-Node 约 27 ms/token，而 DEFT-Node-Chunk 与 DEFT-Flatten 仅约 12–14 ms/token；随 prompt 增长，Radix-Attention 斜率最陡，DEFT-Flatten/Node-Chunk 近似线性且平稳。

2）**关键技术结论**：DEFT-Flatten 与 DEFT-Node-Chunk 在长 prompt 下显著优于 Radix-Attention，验证了 KV 切分策略对长上下文推测解码的扩展性优势；DEFT-Node 因逐节点开销大，扩展性较差。

3）**论文整体作用**：作为关键实验证据，支撑"DEFT 在树结构推测解码下可高效处理长上下文"的核心主张。

### Figure 17 (p.27) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig17.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p27.png]]*
> [!quote] caption
> Decoding latency of DEFT with different prompt lengths in speculative decoding.

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图分两栏展示生成长度1000时、树规模分别为32与64查询下，Radix-Attention与三种DEFT变体（Flatten/Node/Node-Chunk）随prompt长度（≈1k–20k）变化的解码延迟。量化读数：prompt=20k时，Flatten仅≈9s（树32）与≈13s（树64），Node-Chunk≈10.5s与≈15s，增长最缓；Radix在树64、prompt=20k飙至≈37.5s且斜率最陡，Node也达≈28s。

该实验论证：DEFT-Flatten与Node-Chunk对prompt长度呈近线性低增长，而Radix-Attention随树规模增大劣化显著，凸显树结构注意力下Flash树注意机制在长上下文推测解码中降低IO与延迟的必要性，作为论文核心实验结论之一支撑所提方法的优越性。

### Figure 18 (p.28) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig18.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p28.png]]*
> [!quote] caption
> Attention latency of DEFT with different prompt lengths in speculative decoding.

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图展示推测解码（Generation length=1000）下，DEFT 四种变体（Flatten、Node、Node-Chunk）与 Radix-Attention 在 prompt 长度 500–20000 tokens 范围内的 Attention 延迟（秒），分 Token Tree Size=32（左）与 64（右）两个子图。

**核心数据**：树=32、prompt=20k 时，Radix-Attention 与 DeFT-Node 同处 20–24s 高位，DeFT-Flatten/Node-Chunk 仅约 5–6s；树=64、prompt=20k 时，Radix-Attention 飙至 ~33s，DeFT-Node ~23s，而 DeFT-Flatten/Node-Chunk 仅 8–10s。

**论证结论**：Radix-Attention 与 DeFT-Node 延迟随 prompt 长度与树规模呈陡峭上扬，而 DeFT-Flatten 与 Node-Chunk 始终保持低斜率线性增长，验证 chunk 化策略在长 prompt、大草稿树场景下对 Attention 开销的有效抑制。

**论文作用**：与 Table 18（A/F-LR 消融）配合，从 Attention 单一算子延迟维度量化解释 DEFT 加速来源，支撑"长上下文 + 树形推测解码"下 Flash Tree Attention 整体高效性论证。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.2) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab01.png]]
> [!quote] caption
> Comparison of efficiency in sequence-based CoT (Wei et al., 2022) and tree-based ToT (Yao et al., 2023) decoding for a reasoning task. The task is sort- ing 128 numbers from Besta et al. (2023). The total gen- erated tokens of CoT is only 525 while 38 , 315 in ToT, resulting in inefficiency in end-t

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文联合解读：**

该表量化对比"排序128个数字"任务中四种方案的 **Latency / IO-KV / IO-PA** 三项指标。序列式CoT仅生成525 token，而树式ToT生成38,315 token（约73倍），凸显树形解码的token爆炸问题。

具体数据：Flash-Decoding+CoT延迟仅21s；Flash-Decoding+ToT延迟飙至429.65s、IO-KV高达59.96；Tree Attention+ToT将IO-KV降至12.40，但新增IO-PA=3.69。本文DeFT-Flatten+ToT以 **94.67s**、IO-KV=12.40、IO-PA=0，相对最优基线实现 **4.02× 加速**。

**作用**：该表作为关键动机实验，量化揭示树形推理中KV cache与partial attention（QK^T、softmax）的IO瓶颈，为本文提出的Flash Tree Attention（DeFT）方法提供必要性论证与效率基准。

### Table 2 (p.6) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab02.png]]
> [!quote] caption
> Comparison of QKV partitioning strategies for baselines (most of which are shown in Figure 3) and DeFT. For IO redundancy, significant issues are highlighted in red, while negligible ones are in blue. “Q” refers to queries, and “KV” refers to the KV cache. “DCM” stands for Dense Causal Mask (a matri

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 联合解读：**

1）表格横向对比9种Attention算法的5个维度（Grouping Indicator、KV Split Granularity、IO Redundancy、Load-balancing Level）。数据要点：Flash-Attention/Flash-Decoding/Radix均为Q-guided，IO冗余落在KV侧（●●●）；Tree Attention-M/Vanilla Tree采用entire tree分组，产生DCM和PA冗余；DeFT三个变体统一改为KV-guided，DeFT-Node/Node-Chunk的冗余仅剩Q（●/●●）。

2）原文借此论证：现有baseline的Q-guided策略在树形解码下无法避免KV或BCM/PA/DCM的显著IO冗余，而DeFT通过KV-guided按树节点切分，把冗余压缩到可忽略的Q侧，实现IO与负载均衡的帕累托最优。

3）该表是DeFT设计动机的核心证据，承接Figure 3的分块示意，并为Figure 2的整体框架与后续实验section提供"为什么必须KV-guided"的方法论铺垫。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab03.png]]
> [!quote] caption
> Comparison of baselines and D E FT. Attention kernels of baselines are implemented to fit its memory management. Therefore, for a fair comparison with baselines, we implement D E FT-Node and D E FT-Flatten that fit both paged (Kwon et al., 2023)/unpaged memory management.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 表核心对象与结构**
Table 3 对比 4 种树状注意力方法的两维属性：**内存管理方式**（paged / unpaged）与**底层实现框架**（Triton / PyTorch）。具体配置为：Flash-Decoding（unpaged + Triton）、Tree Attention-Medusa（unpaged + PyTorch）、Radix Attention（paged + Triton）、DEFT（unpaged/paged + Triton）。

**2) 原文论证的关键结论**
caption 指出基线内核均**绑定于单一内存管理**，无法跨范式对比。因此作者特地为 DEFT 实现 **DEFT-Node** 与 **DEFT-Flatten** 两种变体，使其同时适配 paged（vLLM 风格）与 unpaged 内存管理。该表证明：只有 DEFT 能与三类基线全部正面对齐，凸显其内存抽象上的**通用性与公平对比基础**。

**3) 在论文中的作用**
作为方法学桥接表，它位于 Figure 3（QKV 分区策略）与 Figure 10（DEFT-Node kernel 细节）之间，为后续 Wall-clock 与吞吐实验提供"配置等价性"前提，是 DEFT 宣称"通用、高效、可落地"论证链中的关键一环。

### Table 4 (p.8) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab04.png]]
> [!quote] caption
> Workloads generation . ToT-BFS stands for Tree-of-Thoughts (Yao et al., 2023) using breadth-first search. APPS (Hendrycks et al., 2021) is a competitive programming problem dataset. Medusa (Cai et al., 2024) is a speculative decoding framework. “GoT” stands for Graph-of-Thoughts (Besta et al., 2023)

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构：** Table 4 为"工作负载生成"配置表，列出 4 种方法及其对应的内存与实现——Flash-Decoding（Triton/未分页）、Tree Attention-Medusa（PyTorch/未分页）、Radix Attention（Triton/分页）、DEFT（Triton/双支持未分页与分页），并定义 ToT-BFS（树形思维 BFS）、APPS（编程题集）、Medusa（投机解码框架）、GoT（图思维，用 GPT-3.5 在 ToT-BFS 内做复杂推理）四类评测负载。

**2) 论证结论：** 强调 DEFT 唯一同时支持未分页与分页两种内存模式，且以 Triton 高效实现，覆盖从投机解码（Medusa 树拓扑）到链式/图式思维推理的多样树结构负载，凸显其通用性。

**3) 论文作用：** 作为实验基线设定表，与 Figure 4（Medusa 32-query 树延迟分解）互补：Table 4 定义"测什么、用什么测"，Figure 4 展示"测出来多快"，共同支撑"Flash Tree Attention 全面优于 Flash-Decoding / Tree Attention / Radix Attention"的系统级加速结论。

### Table 5 (p.9) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab05.png]]
> [!quote] caption
> Comparison of D E FT-Flatten and baselines in average decoding latency (in seconds) for tree-based decoding. Here, b represents the tree width, and t denotes the token tree size (i.e., the number of tree-structured queries). The fastest method is in bold , and the second fastest is underlined . Radi

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图表联合解读：**

表5对比DEFT-Flatten与Flash-Decoding、Tree Attention-Medusa、Radix Attention在三类树形解码场景（共11组配置）下的平均解码延迟。DEFT-Flatten在所有配置中均最优：Few-shot Prompting（b=20/30/50）下9.98/10.99/12.48s，Multi-Step Reasoning下10.90–94.67s，Speculative Decoding（t=32–256）下42.23/46.60/56.96/84.27s，且Flash-Decoding在t=128、256时OOM。

相对最强基线Radix Attention：注意力加速1.15×–3.59×，端到端解码加速1.03×–2.23×，且随树规模t增大而单调上升（t=256达2.23×），接近"无注意力"上界4.36×。该表以量化结果论证了DEFT-Flatten在树形解码场景下对paged KV cache的高效利用及其相对Radix Attention的显著优势，是论文核心实验证据之一。

### Table 6 (p.10) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab06.png]]
> [!quote] caption
> [Different KV Splitting Strategies] Comparison of D E FT-Node, D E FT-Node-Chunk and D E FT- Flatten in average attention latency (second) with NVIDIA A100 (80GB) for Llama3-8B model(GQA). This table is supplementary to Table 16. The fastest method is in bold , and the second fastest is underlined .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**表格核心内容**：在A100上对Llama3-8B（GQA）比较三种KV切分策略——DEFT-Node、DEFT-Node-Chunk、DEFT-Flatten与基线Radix Attention，在少样本提示（b=20/30/50）、多步推理（Sorting/Document/Keyword/Set）、推测解码（t=32/64/128/256）共11种负载下的平均注意力延迟（秒）。

2）**关键结论**：DEFT-Flatten在几乎所有场景下均为最优（加粗），如Few-shot b=50仅5.87s（Radix为9.96s），t=256为40.56s（Radix高达145.43s，**加速约3.6×**）；DEFT-Node-Chunk次之（多场景下划线）。将树状KV展平为单一连续张量后调用Flash Attention，显著优于按节点或按chunk切分的方案，验证了"展平"是Tree Attention的最高效组织方式。

3）**链路作用**：作为Table 16的消融补充，该表在系统层面对DEFT的KV布局决策给出实证依据，是支撑"Flash Tree Attention"核心方法论的关键实验闭环。

### Table 7 (p.10) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab07.png]]
> [!quote] caption
> [Different Prompt Lengths] Comparison of D E FT-Flatten and Radix Attention in the efficiency of multi-step reasoning task sorting . The original prompt length is approx- imately 1K tokens, and we pad it to lengths of 5K, 8K, or 10K tokens.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 7 图文联合解读**

该表比较 **DEFT-Flatten 与 Radix Attention** 在多步推理任务 sorting 上的加速比，横轴为 padding 后的 prompt 长度 L = 1k/5k/8k/10k，纵轴分 Attention 与 Decoding 两行。量化数据：Attention 加速依次为 **1.39× → 1.71× → 1.97× → 1.84×**；Decoding 加速为 **1.09× → 1.37× → 1.53× → 1.67×**。

关键结论：DEFT-Flatten 在所有长度上均优于 Radix；其中 **Decoding 增益随 prompt 长度单调递增**（10k 达 1.67×），Attention 在 8k 处达到峰值 1.97×。这直接论证了 DEFT-Flatten 的扁平调度策略在长 prompt、树形共享 KV 场景下扩展性更强，弥补了 Radix Attention 树遍历开销随上下文增长而放大的短板，从而在论文"树形解码效率优于前缀复用"的整体论证链中，作为长上下文鲁棒性的关键实证支撑。

### Table 8 (p.10) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab08.png]]
> [!quote] caption
> [Different Model Sizes] Comparison of decoding latency speedup and Attention/FFN latency ratio (in short as A/F-LR ) between D E FT and Radix Attention for Codellama-34B and Codellama-7B models. Radix Attention is the best baseline in decoding latency. b represents the tree width, and t denotes the 

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表横向对比DEFT与Radix Attention在Codellama-7B/34B、三类树状推理场景（Few-shot b=30、Multi-step Sorting、Speculative t=64）下的解码加速比与A/F-LR。

**核心数据**：解码加速比在所有场景均为正（7B: 1.34×/1.09×/1.85×；34B: 1.23×/1.03×/1.78×），其中Speculative场景最高；Radix原A/F-LR在Speculative场景最大（7B=2.12，34B=1.66），而DEFT-Flatten的A/F-LR全面低于Radix（多<1，最低0.42）。

**关键结论**：加速比与原A/F-LR呈正相关——注意力占比越高，DEFT收益越大；DEFT通过Flash Tree Attention有效压低Attention相对开销。

**论文作用**：作为跨模型规模与跨任务泛化性的关键证据，支撑"DEFT在注意力主导场景优势显著"这一核心论断。

### Table 9 (p.18) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab09.png]]
> [!quote] caption
> Comparison among D E FT and concurrent works in single-context large-batch sampling scenarios, including Chunk-Attention (Ye et al., 2024a), Hygragen (Juravsky et al., 2024) and Bifurcated-Attention (Athi- waratkun et al., 2024). RelayAttention (Zhu et al., 2024) and Cascade-inference (Ye et al., 20

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图像说明**：所提供图片仅含 Table 9 的标题及上文公式段落，未呈现表格的行列数据（具体方法行、延迟/吞吐/加速比等列缺失），故以下解读主要依据原文 caption。

**核心对象**：表格对比 DEFT 与 Chunk-Attention、Hygragen、Bifurcated-Attention、RelayAttention、Cascade-inference 在单上下文大批量采样场景下的性能；并以 ★ 数衡量树切分后负载均衡度（★ 越多越均衡）。

**关键技术结论**：caption 强调 DEFT 对树拓扑不敏感——即便切分更均衡（如更多 ★），加速效果依然稳定，说明其优势来自动态树拆分机制而非特定树形；RelayAttention、Cascade-inference 被归类为与 Hygragen 类似的静态切分类方法，与 DEFT 形成方法路线区分。

**论文作用**：Table 9 与 Table 8 互补，分别覆盖单上下文大批量与多上下文两种推理场景，通过横向对比同期工作（如 Hygragen、Chunk-Attention）凸显 DEFT 在树结构解码下的通用性与负载均衡鲁棒性，强化"对树拓扑不敏感"这一核心卖点，支撑全文 efficiency 论证主线。

### Table 10 (p.18) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab10.png]]
> [!quote] caption
> Technique list of DeFT. What we propose is in red. The details of the first four techniques are in Section 3.3, while the details of the following techniques are discussed in this chapter.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表为DeFT技术清单（Technique / Goal 两列6行），列出6项优化技术：(1) KV-Guided Grouping（提升GPU利用率、最小化HBM↔shared memory的KV IO）；(2) Flattened Tree KV Splitting（平衡注意力计算负载）；(3) Bit Causal Mask[Miao 2023]（低IO记录树因果）；(4) Kernel Fusion[Dao 2022/2023]（减少中间结果IO）；(5) Tiling[Dao 2022/2023]（适配shared memory容量）；(6) Tree-topology Aware Global Reduction（保证整树注意力正确性）。其中(1)(2)(6)无引用标注，为本文所提（原文标红）；(3)(4)(5)承自FlashAttention系列工作。

**论证结论**：三类目标——内存IO优化、计算平衡、树结构正确性——共同构成DEFT内核的优化栈。

**链路作用**：与Figure 10互证，作为实现章节总览：前四项支撑Section 3.3的FlashTreeAttention基础设计，后两项支撑DEFT-Node/Flatten内核在树状投机解码中的正确高效落地。

### Table 11 (p.21) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab11.png]]
> [!quote] caption
> Notations .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**1) 核心对象与结构**：该表列出8个关键符号——l_n（解码树叶节点/查询数）、N_i（根到叶i的token总长）、N_tree（整树token总长）、#node（节点总数）、n_i（节点i的token长）、d_head（LLM头维度）、s_c（缩放因子=√d_head）、F_s=ΣN_i/N_tree（前缀共享因子）。

**2) 论证的关键技术结论**：这些符号支撑DeFT的IO成本量化分析。原文指出当l_n充分大（如Llama模型d_head=128、l_n=29）时，QK⊤等部分结果IO可与KV cache量级相当；而F_s则精确度量了树结构前缀复用对KV cache IO的压缩比例。

**3) 在论文中的作用**：作为Figure 11 IO代价分解的符号基础，为DeFT相对FlashAttention与投机解码的复杂度优势分析提供统一的数学表述框架。

### Table 12 (p.22) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab12.png]]
> [!quote] caption
> IO complexity breakdown for various methods. O (1) denotes the IO cost for a single data in the tensor across all layers and heads, which is equivalent to # heads ∗ # layer ∗ dtype _ size . The best among all methods in the table is in red , while the (potential) worst is in blue . Query IO is omitt

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表对比7种方法（Naive/Flash-Decoding/Radix/Tree Attention-M/S/DEFT-Node/Chunk）在KV cache、QK⊤、Mask、Softmax等6个环节的IO复杂度。DEFT-Node与DEFT-Node-Chunk仅需加载O(2d_head·Ntree) KV cache，其余环节均为0；Tree Attention-M/S因逐节点mask与softmax仍需O(l_n·Ntree)开销，Naive更高达O(2ΣN_i)。红色最优、蓝色最差。该表以形式化复杂度证明DEFT通过节点合并与chunk划分，将树形解码KV IO降至Flash级下界，是其Flash-Tree-Attention设计实现理论最优IO的核心证据。

### Table 13 (p.23) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab13.png]]
> [!quote] caption
> Details of generated workloads . For multi-step reasoning, we include these 4 tasks from Besta et al. (2023): (1) Sorting 128 numbers ( sorting in short); (2) Document merging ( document in short); (3) Keyword counting ( keyword in short); (4) Set intersection ( set in short). d , and w means depth 

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 13 解读**

该表列出 DEFT 评估所用的三类工作负载及其树形/规模参数：①多步推理 4 任务——sorting（d=10）、document（d=3）、keyword（d=5）、set（d=8），统一 w=10，树源自 Besta 等(2023) 的 ToT-BFS；②少样本提示，d=1，w∈{10,20,30}；③投机解码，t∈{32,64,128,256}，树取自 Medusa。

表中明确每类负载的解码树来源与记录内容（prompt、树形、thought size、分支/剪枝记录等），为实验提供可复现的统一基准。其作用在于：让 DEFT 在三种典型树形解码场景下系统测试 Flash Tree Attention 的效率与正确性，从而支撑"DEFT 通用且对不同树结构均显著加速"的核心结论。

### Table 14 (p.24) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab14.png]]
> [!quote] caption
> [GPU Utilization Microbenchmark] Latency of a single layer of Attention (in µ s), SM Compute Throughput Ratio, Memory Throughput Ratio, and Low Utilization Ratio for D E FT on an NVIDIA A100 (80GB) using the LLama3-8B model (GQA). The workload is speculative decoding with 64 queries and a prompt wit

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**① 核心数据**：表14在A100/LLama3-8B（GQA, 64 query, 4k prompt）下对比DeFT-Node与DeFT-Flatten——单层Attention延迟961.38μs → 226.82μs（约4.2×加速）；SM Compute Throughput 7.60% → 21.19%；Memory Throughput 17.39% → 51.91%；Low Utilization Time Ratio 82.35% → 0%。

**② 技术结论**：将树结构flatten为稠密注意力大幅提升SM计算与显存带宽利用率，彻底消除Node版因kernel间同步导致的82.35%长时低利用率瓶颈。

**③ 论文作用**：作为系统级微基准，从硬件层面量化解释为何DeFT-Flatten端到端性能优于Node版本，为论文"flatten优于node"的核心技术主张提供底层证据。

### Table 15 (p.24) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab15.png]]
> [!quote] caption
> Inference accuracy of D E FT in attention score and perplexity (PPL) . PPL is calculated after 400 iterations of decoding. Vanilla Attention is the implementation from Huggingface Transformers.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 15 图文联合解读**

该表对比四种注意力实现（Vanilla、Radix、DEFT-Node-Chunk、DEFT-Flatten）在 MHA 与 GQA 下的精度。量化数据显示：Radix 的相对注意力误差为 0.545%/0.540%，而 DEFT-Node-Chunk 与 DEFT-Flatten 分别降至 0.403%/0.403% 与 0.407%/0.404%，误差减半；400 步解码后 PPL 均为 1.000/1.002，相对 PPL 误差 ≤9×10⁻⁶。原文借此论证 DEFT 在保留 tree 结构并行优势的同时，注意力精度优于 Radix、生成质量与 Vanilla 一致。在论文链路中，该表属"精度验证"环节，为后续 speedup 章节提供"无损"前提，支撑 DEFT 高效无损推理的核心结论。

### Table 16 (p.25) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab16.png]]
> [!quote] caption
> Average attention latency (in seconds) for tree-based decoding and its impact on decoding latency. Here, b represents the tree width, and t denotes the token tree size (i.e., the number of tree-structured queries). Attention Speedup over the best attention refers to the speedup of D E FT-Flatten com

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心数据**：表16对比三种树结构解码场景（Few-shot Prompting b=20/30/50、Multi-Step Reasoning 四类任务、Speculative Decoding t=32/64/128/256）下，Flash-Decoding、Tree Attention-Medusa、Radix Attention、DEFT-Flatten 的平均 attention 延迟。例如 Speculative t=128 下，DEFT-Flatten 仅 24.46s，而 Radix 76.10s、Tree-Attention 41.10s；Attention 加速比在 t=256 时达 3.59×（vs Radix）。

2) **关键结论**：Tree Attention-Medusa 虽是 attention 最优基线，但 Radix 在解码延迟上仍占优；DEFT-Flatten 同时优于两者——attention 较最优基线加速 1.02–1.70×、较 Radix 加速 1.15–3.59×，解码端加速 1.03–2.23×，且随 token 树规模 t 增大加速越显著。

3) **论文作用**：与 Table 6（KV 切分策略）互为补充，从系统层面验证 DEFT-Flatten 在 Paged 内存下的端到端优势，构成论文方法有效性的核心实验证据。

### Table 17 (p.25) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab17.png]]
> [!quote] caption
> Average end-to-end IO (TB) during decoding. Data format is Left/Right: (Left) KV Cache IO; (Right) partial results IO, including QK T , QK ⊤ /s c , Mask M , M + QK ⊤ /s c and Softmax . b means tree width. t denotes the token tree size (i.e., the number of tree-structured queries). ⋆ means out of mem

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）该表量化展示三类树结构解码场景（Few-shot b=20/30/50、Multi-Step 排序/文档/关键词/集合、Speculative t=32/64/128/256）下四种方法的端到端解码IO（TB），左列KV Cache IO、右列QK^T等partial results IO。例如Flash-Decoding在t=128下KV IO高达340.09TB，t=128/256超A100 80GB(⋆)；DEFT-Flatten降至13.15TB与40.56TB。

2）原文用以论证DEFT-Flatten通过扁平化存储显著削减IO开销，相对最优attention获1.02×–1.70×加速、相对Radix Attention获1.15×–3.59× attention加速及1.03×–2.23×端到端加速。

3）该表与Figure 17延迟曲线互补，从IO维度实证DEFT在三类树结构推理场景下的普适有效，构成方法验证的关键实验证据。

### Table 18 (p.28) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab18.png]]
> [!quote] caption
> [Ablation Study of Model Size and Prompt Length] Comparison of decoding speedup and Attention/FFN latency ratio ( A/F-LR ) between D E FT and Radix Attention for Codellama-34B and Codellama-7B across varying prompt lengths in the sorting reasoning task. Radix Attention is the best baseline in decodi

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表展示DEFT与Radix Attention在Codellama-7B/34B、1k/5k/8k prompt下的解码加速比与A/F-LR（Attention/FFN延迟比）。量化数据：7B加速1.09×→1.37×→1.53×，34B为1.03×→1.28×；Radix的A/F-LR在7B高达2.50、34B为0.48–1.16，DEFT-Flatten则降至0.42–1.25。

原文论证：①prompt越长、模型越小，DEFT加速越显著，因注意力开销占比高、Flash Tree Attention优化空间大；②34B时A/F-LR<1，FFN主导，注意力优化边际收益递减；③DEFT-Flatten系统性压低A/F-LR，证明其消除树结构注意力冗余的有效性。

作用：作为消融与扩展性实验，回答"规模与长度是否影响优势"的关键疑问，巩固DEFT方法在不同部署场景下的通用性结论。

### Table 19 (p.28) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab19.png]]
> [!quote] caption
> [Different GPUs] Speedup of D E FT in average attention latency (second) with NVIDIA RTX 4090 (24GB) for LLama3-8B model(GQA). Radix Attention is the best baseline in decoding latency.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 19 图文联合解读**

**1) 核心数据**：表格以 NVIDIA RTX 4090 为平台，对比 DeFT 与最佳基线 Radix Attention 在 Llama3-8B（GQA）模型上的解码性能。Decoding latency Speedup 方面，7B 模型随 prompt 长度从 1k→5k→8k 分别达 1.09×、1.37×、1.53×；34B 模型为 1.03×、1.18×、1.28×。A/F-LR（显存加载率）方面，DeFT-Flatten 全面低于 Radix Attention（7B：0.89/1.09/1.25 vs 1.12/1.89/2.50；34B：0.42/0.57/0.67 vs 0.48/0.86/1.16）。

**2) 关键结论**：DeFT 在不同 prompt 长度与模型规模下均实现稳定的解码加速，且 prompt 越长加速比越高；更低的 A/F-LR 表明其树结构访存更高效，验证了 Flash Tree Attention 的有效性。

**3) 论文作用**：该表属"不同 GPU"硬件泛化性实验，与 A100、H100 结果互补，证明 DeFT 在消费级 GPU 上同样具备实用加速优势，强化全文跨平台鲁棒性论证。

### Table 20 (p.28) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab20.png]]
> [!quote] caption
> [Different Model Architectures(GQA)] Speedup of D E FT in average attention latency (second) with NVIDIA A100(80GB) for Codellama-34B model(GQA). Radix Attention is the best baseline in decoding latency.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 20 图文联合解读**

该表在 NVIDIA A100(80GB) 上、采用 Paged KV 内存，针对 **Codellama-34B（GQA 架构）** 测量三种树状解码场景下 Radix Attention 基线与 DEFT 两种变体（Node-Chunk、Flatten）的平均注意力延迟（秒）。关键数据：Few-shot Prompting(b=30) 4.26→3.07→2.95；Multi-Step Reasoning-Sorting 26.36→24.61→23.86；Speculative Decoding(t=64) 33.63→15.39→14.04；相对最佳基线的加速比为 **1.44×、1.10×、2.40×**。

原文借此论证：在 GQA 这类非 MHA 架构上，**DEFT-Flatten 同样显著优于 Radix Attention**，尤其在 Speculative Decoding 场景下加速达 2.4×，证明方法的架构无关性。该表与 Table 21 共同构成"不同模型架构（MHA / GQA）"消融实验，强化 DEFT 通用高效的结论，是论文实验链路中支撑泛化性的关键证据。

### Table 21 (p.29) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab21.png]]
> [!quote] caption
> [Different Model Architectures(MHA)] Speedup of D E FT in average attention latency (second) with NVIDIA A100(80GB) for Codellama-7B model(MHA). Radix Attention is the best baseline in decoding latency.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 21给出Codellama-7B（MHA架构）在A100、三类树状解码场景的平均注意力延迟（秒）：Radix Attention基线为12.39/53.96/96.55，DEFT-Flatten降至8.24/43.91/36.48，DEFT-Node-Chunk介于二者之间；DEFT-Flatten相对Radix分别取得1.50×、1.23×、2.65×加速，Speculative场景收益最大。

论文将其与对应GQA架构表配对，论证DEFT-Flatten在MHA与GQA上均显著优于Radix（Speculative场景MHA 2.65× vs GQA 2.4×），证明方法不依赖特定注意力头形式，具备架构无关的通用性。

在实验链路中，该表是从"单架构性能"迈向"跨架构泛化"验证的关键衔接，与其他消融共同支撑"DEFT是通用高效树状解码方案"的最终结论。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\begin{aligned} \textstyle \operatorname{SegAttn}(\mA_0, \mA_1, \mA_2)= \frac{ \mA_0 e^{\operatorname{LSE}(\mQ, \mK_0)} + \mA_1 e^{\operatorname{LSE}(\mQ, \mK_1)} + \mA_2 e^{\operatorname{LSE}(\mQ, \mK_2)} }{ e^{\operatorname{LSE}(\mQ, \mK_0)} + e^{\operatorname{LSE}(\mQ, \mK_1)} + e^{\operatorname{LSE}(\mQ, \mK_2)} } \,, \text{ where } e := \text{exp} \,. \end{aligned}
$$

## 技术点深读（DEEP）

![[deep/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference.txt`（112630 字符）供引用检索。