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

图示用三色图例区分可共享KV缓存（蓝）、不可共享prompt（绿）、不可共享generation（黄），对比Sequence-based与四种Tree-based解码：(1)Self-consistency——单prompt分支为G₁/G₂；(2)Few-shot prompting——示例P₁/P₂及其生成可共享；(3)Tree-of-thoughts——通过Search History在分支间共享上下文；(4)推测解码——草稿模型产出token树t₀→t₁,t₂,t₃→t₄，验证后保留t₀/t₂/t₄并跨Step history复用。Sequence-based各序列完全独立、无共享；而Tree-based蕴含丰富可共享结构，但传统实现难以高效利用。结合Table 1（ToT生成38,315 vs CoT仅525 token的开销差异），作者论证Tree-based存在严重计算冗余，从而引出DeFT借助FlashAttention对树状结构做高效分块注意力与KV缓存复用的核心贡献。

### Figure 2 (p.5) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig02.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p05.png]]*
> [!quote] caption
> Overview of DEFT. Input Metadata is prepared in the system elaborated in Appendix A.1. In QKV

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示DEFT两阶段中的**Phase 1（QKV准备）**：HBM内Input Metadata含Query、共享前缀KV_0、分支KV_1/KV_2及Tree Topo，Q_a/Q_b各映射对应分支KV。经**KV-Guided Grouping**（跨分支复用KV_0）与**Flattened Tree KV Splitting**（按树拓扑切成均衡组G_i），IO感知装入各SM_i。

原文论证：消除共享前缀冗余KV读取 + SM负载均衡，为Phase 2共享内存（19TB/s）跑部分注意力 + 树感知全局归约供均衡输入。

在论文中：作为投机解码链路的**前端预处理核心**，直接决定HBM带宽（2TB/s）利用率与SM并行度，是"内存高效、硬件友好树结构注意力"方法的基础环节。

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
> 【图文联合解读】**图4解读**

图4展示在Medusa 32查询token树的推测解码场景下，6种注意力方法的延迟分解（Attention/KV Management/Other三类，纵轴秒）。关键量化数据：非分页的Tree-Attention-Medusa（U）总延迟最高约275s，其中KV管理占比高达53.46%；而DeFT系列（带分页机制）总延迟仅55–90s区间，以DeFT-Flatten最低。

**论证结论**：非分页方案的KV管理是主要延迟瓶颈，而分页KV管理能显著压低总延迟。

**论文作用**：该图是实验链路中验证DEFT核心设计——Flash Tree Attention + 分页KV——相对Tree-Attention-Medusa实现显著加速的关键证据，支撑"分页管理是树结构LLM推理高效性必要条件"这一论点。

### Figure 5 (p.15) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig05.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p15.png]]*
> [!quote] caption
> Illustration of DEFT. (Left) System overview. (Right) The data flow of DEFT-Node (DEFT-Flatten is similar except for QKV partitioning) using a decoding tree example.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**1) 核心对象与结构**
图示一棵解码树：根节点 S0=Prompt"Machine Learning"，分叉为 S1="System is difficult" 与 S2="has changed the"，当前迭代 iter=3。底部输入元数据含 Query、KV Cache (S0,S1,S2)、Tree Topo，经"extract and pack"送入 HBM→Shared Mem。上部按 KV 前缀划分为 3 个 QKV Group（Group 0/1/2），每组 Query（"difficult/the"、"the"、"the"）按共享 KV 配对执行 Attention。

**2) 关键技术结论**
论证 DeFT 的核心机制：Query 按 KV 前缀分组复用，使共享 KV 路径只需一次访存即可被多条查询路径共同使用，从而消除树形推理中的冗余计算与内存访问；并说明 DeFT-Node 与 DeFT-Flatten 仅 QKV 划分策略不同。

**3) 在论文中的作用**
作为系统总览与算法核心图，将"解码树→元数据→QKV 分组→Flash-Tree Attention Kernel"流水线具象化，为后续核函数设计与吞吐加速实验提供机制基础。

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
> 【图文联合解读】图11对比三种Tree Attention的QKV分块策略：左侧Medusa按GEMM将KV切为m×k与k×n的tile块，产生全量partial结果M；右侧SpecInfer采用Q-Guided Grouping，把查询分为G₀（Q_a）与G₁（Q_b）两组，分别共享同一组KV₀/₁/₂，并通过Q-BCM位掩码"110""101"标注各查询实际访问的KV子集。原文论证：当叶节点数ln足够大时，partial结果的IO开销可与KV cache相当，从而说明朴素的逐tile GEMM切分存在冗余访存问题，为论文提出的Q-BCM分块与Flash Tree Attention优化提供必要性依据，是方法链路中IO分析与分块策略设计的支撑图。

### Figure 12 (p.23) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig12.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p23.png]]*
> [!quote] caption
> The detailed procedure of reconstructing tree templates for multi-step reasoning. (Left)

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图12展示两阶段构建解码树模板的流程。左绿框"Reconstruct thought trees"：Prompt节点按宽度w在d层深度上扩展为思维树，节点标为thought_i_j；✓标记保留节点，红色✗标记剪枝节点，虚线省略其余深度/宽度分支。右橙框"Tree templates for decoding"：每个保留节点封装5项元数据——start/end iteration（100/103）、thought size（3）、parent id（thought_i-1,k）、children id（None），并映射到具体文本"System is difficult"。据此生成两张结构化表：**Branch records**（迭代100，从(i-1,k)生成(i,j)）与**Prune records**（迭代103，剪掉(i,j)）。

**技术结论**：作者论证树模板可由真实推理轨迹离线重建，并通过5项元数据完整表征节点的生成时机、长度、父子关系，从而无遗漏地为解码阶段提供可调度的分支与剪枝信息。

**方法链路作用**：该模板是DeFT解码的离线预处理产物，为FlashTreeAttention提供"何时生成何分支、何时剪除何节点"的调度依据，是实现高效树结构推理的关键前置步骤。

### Figure 13 (p.25) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig13.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p25.png]]*
> [!quote] caption
> Comparison of split strategies DEFT-Node and DEFT-Flatten in sorting task. Speedup ratio refers to the ratio between the per iteration latency of DEFT-Node and DEFT-Flatten. Tree Node Len std represents the standard deviation of the tree node lengths for each iteration.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**核心对象与数据**：图示排序任务下，DEFT-Node 与 DEFT-Flatten 两种切分策略在迭代步 2000–3700 区间的对比。左轴 Speedup Ratio（蓝实线）前期稳定在 320–380 倍，后期（≈3000 后）剧烈震荡；右轴 Tree Node Len std（红虚线）在 220–300 之间周期性起伏。

2）**关键结论**：DEFT-Node 相对 DEFT-Flatten 获得高达约 350 倍的加速比，证明节点级切分显著优于展平切分，尤其在节点长度方差较小、树结构深度（d=10）× 宽度（w=10）规整的排序任务上，Node 策略能充分利用 Flash Tree Attention 的并行前缀，避免 Flatten 带来的冗余计算。

3）**在论文中的作用**：作为消融/对比实验，支撑 DEFT-Node 作为默认切分策略的设计选择，强化"树状推理的高效解码依赖于与树结构对齐的注意力切分"这一核心论点。

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
> 【图文联合解读】该图展示Prompt Length=1000时，不同token树规模（t=32/64/128/256）下单层Attention延迟随KV Chunk Size（128–1024）的变化曲线（实线为DeFT-Flatten，虚线为对照）。量化数据：t=32橙色线约90μs，t=256黄色线约270μs，延迟随t递增；多数曲线在chunk=256–512处取极小值，至1024时明显回升。原文据此论证chunk选择是Query IO冗余（越小越冗余）与SM线程块调度（越大越易空闲）的权衡；该ablation为DEFT系统确定最优KV chunk尺寸提供依据，支撑Flash Tree Attention整体推理效率的实验链路。

### Figure 16 (p.27) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig16.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p27.png]]*
> [!quote] caption
> Time per output token(TPOT) of DEFT with different prompt lengths in speculative decoding. 2500 5000 7500 10000 12500 15000 17500 20000

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示在投机解码场景下（生成长度1000、token树大小=64），三种DEFT变体（DeFT-Node、DeFT-Node-Chunk，图中推测最高红线为DeFT-Flatten）的每输出token时间（TPOT）随prompt长度（2500–20000 tokens）变化的趋势。三条曲线均单调上升，但DeFT-Flatten增速最快（20000时TPOT最高），DeFT-Node居中，DeFT-Node-Chunk最低且增速最平缓，长prompt下优势显著拉开。原文借此论证：**chunk级KV切分策略（DeFT-Node-Chunk）在长上下文投机解码中延迟最低**，验证了Table 6关于切分粒度对注意力延迟影响的结论。该图作为方法验证的关键实验，支撑了论文整体方法链中"分块注意力优化"这一核心技术贡献，证明其在真实长prompt场景下具备实用加速价值。

### Figure 17 (p.27) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig17.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p27.png]]*
> [!quote] caption
> Decoding latency of DEFT with different prompt lengths in speculative decoding.

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图展示生成长度=1000、Token Tree Size=64时，4种注意力实现的解码延迟随Prompt长度（约2000→20000 tokens）的变化。短prompt下四条曲线几乎重合（差异≈0），但随prompt延长，粉色基线斜率最陡，DeFT-Node次之，DeFT-Node-Chunk与橄榄色chunk基线增长最缓，至20000 tokens时差距已拉开数倍。论文借此论证：在推测解码的长上下文场景中，节点级KV复用叠加chunk分块的双重优化使DeFT-Node-Chunk具备最优可扩展性，是其作为论文核心高效变体的关键实验支撑。

### Figure 18 (p.28) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig18.png]]
*整页渲染: ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p28.png]]*
> [!quote] caption
> Attention latency of DEFT with different prompt lengths in speculative decoding.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图18在生成长度1000、Token Tree Size=64的推测解码设定下，对比不同注意力实现随Prompt长度（0–20000 tokens）变化的延迟曲线：红色线（朴素树注意力）斜率最陡，长prompt下延迟最高；DeFT-Node（青蓝）次之；DeFT-Node-Chunk（紫）增长最缓且接近最优基线。

核心结论：随prompt增长，朴素树注意力开销急剧膨胀，而DeFT-Node-Chunk通过分块策略显著压缩长prompt下的注意力延迟，验证了chunk机制在大上下文推测解码中的可扩展性。

该图在论文实验链路中起"长上下文效率验证"作用，作为DEFT方法论在长prompt场景下优于朴素树注意力的关键定量证据，支撑整体Tree-Structured speculative decoding的高效性论证。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 3 (p.8) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab03.png]]
> [!quote] caption
> Comparison of baselines and D E FT. Attention kernels of baselines are implemented to fit its memory management. Therefore, for a fair comparison with baselines, we implement D E FT-Node and D E FT-Flatten that fit both paged (Kwon et al., 2023)/unpaged memory management.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读：**

表3横向对比4类方法在**内存管理 × 实现栈**两个维度的差异：Flash-Decoding（unpaged/Triton）、Tree Attention-Medusa（unpaged/PyTorch）、Radix Attention（paged/Triton）、DEFT（同时支持unpaged与paged/Triton）。

**关键结论：** 现有基线的注意力kernel与底层内存管理**强耦合**——前两种仅适配连续存储，Radix Attention仅适配分页存储，二者无法互换。DEFT则通过同时实现**DEFT-Node**（匹配vLLM分页方案）与**DEFT-Flatten**（匹配连续方案）两种变体，实现对两类内存管理的通用兼容。

**在论文链路中的作用：** 此表是后续性能对比实验的**公平性前提**。它在量化层面统一了所有方法所处的实现栈（Triton）与内存维度，确保后续吞吐/延迟指标上的优势归因于DEFT算法本身（树结构注意力 + Flash-Tree-Attention kernel），而非底层存储差异引入的噪声。

### Table 5 (p.9) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab05.png]]
> [!quote] caption
> Comparison of D E FT-Flatten and baselines in average decoding latency (in seconds) for tree-based decoding. Here, b represents the tree width, and t denotes the token tree size (i.e., the number of tree-structured queries). The fastest method is in bold , and the second fastest is underlined . Radi

> [!tip] 表格解读（多模态）
> 【图文联合解读】**1) 表5核心内容**：对比 DEFT-Flatten 与三种基线（Unpaged：Flash-Decoding、Tree Attention-Medusa；Paged：Radix Attention）在 11 个树解码场景下的平均延迟（秒），覆盖三类任务——Few-shot Prompting（b=20/30/50）、Multi-Step Reasoning（Sorting/Document/Keyword/Set）、Speculative Decoding（t=32/64/128/256），并列出相对 Radix Attention 的 Attention/Decoding 加速比及上界。

**2) 关键结论**：① DEFT-Flatten 全部 11 项均最快（如 b=20: 9.98s vs 12.37s；t=256: 84.27s vs 188.66s），相对 Radix 实现 1.03×–2.23× 整体加速、1.15×–3.59× 注意力加速；② Flash-Decoding 在 t=128/256 出现 OOM，暴露其分页方案的扩展性局限；③ Speedup Upper-bound 最高 4.36×，表明注意力仍是主要瓶颈，进一步优化空间大。

**3) 论文作用**：作为系统级延迟评测核心表，与 Table 4（DEFT-Node）共同验证 DEFT 在 Paged/Unpaged 两路径下对多种树结构解码的通用加速能力，支撑"Flash Tree Attention 全面优于既有方案"的结论。

### Table 6 (p.10) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab06.png]]
> [!quote] caption
> [Different KV Splitting Strategies] Comparison of D E FT-Node, D E FT-Node-Chunk and D E FT- Flatten in average attention latency (second) with NVIDIA A100 (80GB) for Llama3-8B model(GQA). This table is supplementary to Table 16. The fastest method is in bold , and the second fastest is underlined .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表对比 Llama3-8B(GQA) 在 A100 上三种 KV 切分策略（DEFT-Node、DEFT-Node-Chunk、DEFT-Flatten）与 Radix Attention 基线在 10 个场景（Few-shot b=20/30/50、Multi-Step Sorting/Document/Keyword、Speculative Set/t=32/64/128/256）下的平均 attention 延迟。数据显示 **DEFT-Flatten 在全部 10 项中均最快**（如 5.87/2.57/13.15 秒），Radix Attention 居次，Node-Chunk 第三，Node 最慢。

**技术结论**：扁平化 KV 切分显著优于按节点/分块切分，证明在树状推理中将共享前缀展平为连续布局可最大化 FlashAttention 利用率，是 DEFT 核心设计选择。

**论文作用**：作为 Table 16 的补充消融，定量论证 KV 布局策略对 tree-structured attention 效率的关键影响，为方法选型提供实证依据。

### Table 7 (p.10) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab07.png]]
> [!quote] caption
> [Different Prompt Lengths] Comparison of D E FT-Flatten and Radix Attention in the efficiency of multi-step reasoning task sorting . The original prompt length is approx- imately 1K tokens, and we pad it to lengths of 5K, 8K, or 10K tokens.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心数据**：表7对比DEFT-Flatten与Radix Attention在多步推理排序任务中的加速比，prompt长度L=1K/5K/8K/10K。Attention加速比依次为1.39×、1.71×、1.97×、1.84×（L=8K达峰，10K略回落）；Decoding加速比依次为1.09×、1.37×、1.53×、1.67×，随长度单调递增。

**关键结论**：DEFT-Flatten在四种长度下均快于Radix Attention；Attention阶段优势随prompt变长先升后微降，Decoding阶段优势则持续扩大，说明长上下文场景下DEFT-Flatten的可扩展性更优，且其优势在端到端解码阶段更稳定。

**论文作用**：与Figure 7（多步推理树形结构示意）、Table 8（端到端解码延迟）串联成完整验证链——从结构分析到多步推理量化对比，再到整体延迟优势，系统论证Flash Tree Attention+Flatten方法在树形结构LLM推理中的高效性。

### Table 8 (p.10) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab08.png]]
> [!quote] caption
> [Different Model Sizes] Comparison of decoding latency speedup and Attention/FFN latency ratio (in short as A/F-LR ) between D E FT and Radix Attention for Codellama-34B and Codellama-7B models. Radix Attention is the best baseline in decoding latency. b represents the tree width, and t denotes the 

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表8内容**：展示DEFT与Radix Attention在Codellama-7B/34B三种场景（Few-shot b=30、Multi-step Reasoning排序约1k、Speculative Decoding t=64）的解码加速比与A/F-LR。7B加速比为1.34×/1.09×/1.85×，34B为1.23×/1.03×/1.78×；DEFT A/F-LR均≤0.89，Radix最高达2.12。

**关键结论**：DEFT在不同模型规模下均稳定超越最强基线Radix，Speculative场景加速最显著（1.78-1.85×）；DEFT A/F-LR显著低于Radix，表明Attention不再是延迟瓶颈，开销由FFN主导，印证Flash Tree Attention确实消除了Attention侧IO开销。

**论文作用**：作为方法**可扩展性（scalability）验证**，证明DEFT在不同参数量级模型与多类树形任务（少样本、多步推理、投机解码）中普遍有效，强化通用性主张并排除"加速仅适用于小模型/特定任务"的质疑。

### Table 9 (p.18) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab09.png]]
> [!quote] caption
> Comparison among D E FT and concurrent works in single-context large-batch sampling scenarios, including Chunk-Attention (Ye et al., 2024a), Hygragen (Juravsky et al., 2024) and Bifurcated-Attention (Athi- waratkun et al., 2024). RelayAttention (Zhu et al., 2024) and Cascade-inference (Ye et al., 20

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读**

⚠️ 图中仅显示 Table 9 的标题说明文字与上方公式片段，**未呈现实际数据表格主体**（行列、具体数值不可见），以下基于标题与正文语境解读：

**1) 核心对象与结构**：标题明确该表横向对比 DEFT 与 Chunk-Attention、Hygragen、Bifurcated-Attention（及与之类似的 RelayAttention、Cascade-inference）共五类方法，纵向考察其在**单上下文大批量采样**场景下的性能指标；★标注量化为"树分裂后负载均衡度"，★越多越均衡。

**2) 原文论证结论**：① DEFT 在共享前缀树解码大批量采样中相对上述并行方法具加速优势；② ★越多（拓扑越均衡）效果仍稳健，证其加速对树拓扑**不敏感**——这是相对于拓扑耦合方法的差异化卖点。

**3) 在论文链路中的作用**：与 Figure 9 的"两阶段融合内核"设计互为表里——前者解释 *为何快*（Flash 融合 + 拓扑感知分组降 IO），本表则实证 *在大批量 speculative decoding 实际部署场景下多快*，构成方法可扩展性与通用性的关键验证节点。

### Table 10 (p.18) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab10.png]]
> [!quote] caption
> Technique list of D E FT. What we propose is in red . The details of the first four techniques are in Section 3.3, while the details of the following techniques are discussed in this chapter.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**图像内容**：图片仅显示 Table 10 的 caption，表格本体（技巧列表）未呈现。caption 明确：表格列出 DEFT 采用的全部注意力算法设计技巧，作者新提的以**红色**高亮；前 4 项技巧的细节在 Section 3.3，后续技巧的细节在本章（A.4 附录）展开。

2）**原文论证的关键结论**：作者通过该表系统罗列 DEFT 技术栈，明确区分"既有方法"与"本文贡献"，将树注意力结构、FlashAttention 融合（前 4 项，正文 §3.3）与两级 kernel、Global Reduction、LSE 数值稳定合并等实现层面技巧（附录 A.4）显式分层，体现"方法层 + 实现层"的完整设计。

3）**论文整体链路中的作用**：Table 10 充当"技巧总览/索引"，衔接正文方法描述与附录实现讨论，为读者把握 DEFT 完整工程栈提供路线图，支撑其"高效树结构 LLM 推理"的核心主张。

（注：图像仅含 caption，表格具体行项与红色标注内容无法从图直接读取，上述解读基于 caption 语义与正文/图 10 上下文推断。）

### Table 11 (p.21) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab11.png]]
> [!quote] caption
> Notations .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 11（Notations）图文联合解读**

**1) 核心内容**：该表列出 DeFT 论文中树状解码注意力机制所用的 7 个关键符号及量化定义。结构上分两列——符号列（l_n、N_i、N_tree、#node、n_i、d_head、s_c）与说明列。其中 l_n 表示解码树叶节点/查询数，N_i 与 N_tree 分别表示单路径与整棵树的 token 总长度，#node 为节点总数，n_i 为单节点 token 长，d_head 为 LLM 注意力头维度（Llama 中固定为 128），s_c = √d_head 为缩放点积注意力因子。

**2) 论证的技术结论**：该符号表为前文 IO 成本分析提供量化基础。结合图 11，论文指出当 l_n 足够大（如 Llama 128 维头、l_n=29）时，部分结果（QK^T、QK⊤_sc、中间矩阵 M 等）的 IO 代价将趋近甚至超过 KV cache 本身，从而论证树状注意力中 partial result 访存不可忽略，必须被纳入 flash-style 分块 IO 优化范畴。

**3) 在论文中的作用**：此表是全文复杂度推导、IO 分析及实验对比的"语法基础"，统一了后续公式、FLOPS/IO 估算与基准测试中的变量含义，使树结构 LLM 解码的效率论证严格且可复现。

### Table 12 (p.22) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab12.png]]
> [!quote] caption
> IO complexity breakdown for various methods. O (1) denotes the IO cost for a single data in the tensor across all layers and heads, which is equivalent to # heads ∗ # layer ∗ dtype _ size . The best among all methods in the table is in red , while the (potential) worst is in blue . Query IO is omitt

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 12 图文联合解读：**

该表横向对比7种方法（Naive、Flash-Decoding、Radix、Tree Attention-M/S、DEFT-Node/-Node-Chunk）在KV cache、QK⊤、QK⊤/s_c、Mask、Softmax五类张量上的IO复杂度，关键发现：

1) **核心数据**：DEFT-Node 与 DEFT-Node-Chunk 的 KV IO 同为 O(2d_head·N_tree)（红色最优），且 attention 计算项（QK⊤、Mask、Softmax）全部清零；而 Tree Attention-M 仍有 O(l_n·N_tree) 的 mask/softmax 开销，Naive/Flash/Radix 的 KV IO 为 O(2d_head·ΣN_i)（蓝色潜在最劣），Tree Attention-S 的 KV 更膨胀为 O(2d_head·N_tree·l_n)。

2) **论证结论**：DEFT 仅付出与 Flash-Decoding 同量级的 KV IO，即可完全消除树状解码的 attention 计算 IO，显著优于 Tree Attention-M 与 SpecInfer。

3) **论文作用**：为 DEFT "KV 最小化 + 计算归零" 的核心效率优势提供理论复杂度依据，支撑其实验端对 Medusa/SpecInfer 的速度领先。

### Table 13 (p.23) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab13.png]]
> [!quote] caption
> Details of generated workloads . For multi-step reasoning, we include these 4 tasks from Besta et al. (2023): (1) Sorting 128 numbers ( sorting in short); (2) Document merging ( document in short); (3) Keyword counting ( keyword in short); (4) Set intersection ( set in short). d , and w means depth 

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 13 图文联合解读**

**1) 核心对象与数据：** 该表罗列了DEFT实验所用的两类生成负载配置。①多步推理：引用Besta et al. (2023)的4个任务——sorting(128个数)、document(文档合并)、keyword(关键词计数)、set(集合交集)，每任务标注树深度*d*与宽度*w*（如document *d*=3、*w*=10；sorting *d*=10、*w*=10）。②推测解码：基于Medusa (Cai et al., 2024)拓扑，记录每步接受的token树规模*t*及长度。

**2) 关键技术结论：** 表格说明DEFT的评测负载并非合成，而是从真实推理/解码交互中重建（捕获树形、thought长度、最优thought及其得分），保证负载的真实性与多样性（深vs浅、窄vs宽），用以严谨验证Flash Tree Attention在thought生成阶段及token验证阶段的加速效果。

**3) 在论文中的作用：** 作为实验链路的"输入基准"，为Figure 13中DEFT-Node与DEFT-Flatten策略对比、以及全文加速比实验提供统一、可复现的tree-structured负载标准。

### Table 14 (p.24) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab14.png]]
> [!quote] caption
> [GPU Utilization Microbenchmark] Latency of a single layer of Attention (in µ s), SM Compute Throughput Ratio, Memory Throughput Ratio, and Low Utilization Ratio for D E FT on an NVIDIA A100 (80GB) using the LLama3-8B model (GQA). The workload is speculative decoding with 64 queries and a prompt wit

> [!tip] 表格解读（多模态）
> 【图文联合解读】**1) 核心对象与数据：** A100/80GB + LLama3-8B(GQA) + 64 queries/4k prompt 投机解码场景下，对比 DEFT-Node 与 DEFT-Flatten 的 Attention 单层延迟与三项 GPU 利用率。DEFT-Node：961.38μs / Compute 7.60% / Memory 17.39% / 低利用率 82.35%；DEFT-Flatten：226.82μs（↓4.2×）/ 21.19%（↑2.8×）/ 51.91%（↑3.0×）/ 0%。

**2) 关键结论：** Flatten 通过摊平树结构消除 per-node kernel 调度碎片，使 SM 计算与显存带宽利用率提升数倍，并将"计算空泡"占比从 82.35% 压至 0%，证明 flatten 变换是 Flash-Tree-Attention 高效利用 GPU 的核心机制。

**3) 论文作用：** 与端到端延迟图互补，本表以微基准量化"DeFT 为何更快"，提供硬件级证据，支撑论文"tree-structured attention 可被高效实现"的核心论断。

### Table 15 (p.24) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab15.png]]
> [!quote] caption
> Inference accuracy of D E FT in attention score and perplexity (PPL) . PPL is calculated after 400 iterations of decoding. Vanilla Attention is the implementation from Huggingface Transformers.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 15 联合解读**

**① 表格核心内容**：对比 Vanilla Attention（HuggingFace 基线）与 Radix Attention、DEFT-Node-Chunk、DEFT-Flatten 三种方案在 MHA 和 GQA 两种注意力变体下的数值精度。三类指标：相对注意力误差（Radix ≈0.54%，DEFT 两方案 ≈0.40%）、PPL（MHA 均为 1.000，GQA 均为 1.002）、相对 PPL 误差（均 ≤4×10⁻⁶）。PPL 在 400 轮解码后测量。

**② 关键结论**：所有近似方案的 PPL 与基线完全一致（差异仅 10⁻⁶ 量级），注意力分数误差亦低于 0.55%，证明 DEFT 在树状结构复用 KV 的优化中**不损失推理精度**；且 DEFT 的节点分块/展平策略误差略优于 Radix Attention。

**③ 在论文中的作用**：作为"正确性护城河"实验，与 Figure 15（KV 分块尺寸的性能消融）配合——前者证明精度无损，后者展示速度增益，共同支撑"DEFT 同时实现高效且精确的树状 LLM 推理"的核心主张。

### Table 16 (p.25) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab16.png]]
> [!quote] caption
> Average attention latency (in seconds) for tree-based decoding and its impact on decoding latency. Here, b represents the tree width, and t denotes the token tree size (i.e., the number of tree-structured queries). Attention Speedup over the best attention refers to the speedup of D E FT-Flatten com

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 16 图文联合解读**

1) **核心对象与数据**：表格对比四种注意力方法在 A100 80GB 上的平均注意力耗时，覆盖三类树状解码场景——少样本提示（b=20/30/50）、多步推理（Sorting/Document/Keyword/Set）、推测解码（t=32/64/128/256）。Flash-Decoding 延迟最高（如 t=32 时 340.09 s，t=128/256 OOM）；Tree Attention-Medusa 在 unpaged 中最快（3.93–68.28 s）；Radix Attention 作为 paged 基线（5.99–145.43 s）；DEFT-Flatten 在 paged 中最低（3.47–40.56 s）。底部给出三级加速比：相对最优 attention 1.02×–1.70×、相对 Radix Attention 1.15×–3.59×、相对 Radix 解码延迟 1.03×–2.23×。

2) **关键结论**：DEFT-Flatten 在所有场景下均优于 Radix Attention 和 Tree Attention-Medusa，且在推测解码长树（t=256）下 attention 加速达 3.59×、解码加速 2.23×，证明其在 GQA 模型上的注意力效率与端到端延迟两方面均显著领先。

3) **论文作用**：该表是 DEFT 方法的核心实证支柱，配合 Table 6（KV 分块策略对比）和 Figure 16（TPOT 长 prompt 验证），系统论证 Flash Tree Attention 在 tree-structured 推测解码全流程中的有效性与可扩展性。

### Table 17 (p.25) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab17.png]]
> [!quote] caption
> Average end-to-end IO (TB) during decoding. Data format is Left/Right: (Left) KV Cache IO; (Right) partial results IO, including QK T , QK ⊤ /s c , Mask M , M + QK ⊤ /s c and Softmax . b means tree width. t denotes the token tree size (i.e., the number of tree-structured queries). ⋆ means out of mem

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表对比三类场景（Few-shot、Multi-Step、Speculative）下各attention方法的解码端到端IO（TB），格式为KV Cache IO / 部分结果IO。DEFT-Flatten在所有配置下IO最低：例如t=256推测解码仅40.56TB，而Radix为145.43、Flash-Decoding OOM；Few-shot b=50时5.87 vs 9.96 / 110.09。相对Radix取得1.73–3.59× attention加速与1.10–2.23× decoding加速。作为核心实验数据，该表定量印证DEFT通过平铺访存显著降低解码IO开销，支撑其端到端效率优势。

### Table 18 (p.28) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab18.png]]
> [!quote] caption
> [Ablation Study of Model Size and Prompt Length] Comparison of decoding speedup and Attention/FFN latency ratio ( A/F-LR ) between D E FT and Radix Attention for Codellama-34B and Codellama-7B across varying prompt lengths in the sorting reasoning task. Radix Attention is the best baseline in decodi

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 18 对比 Codellama-7B/34B、prompt 长度 1k/5k/8k 下 DEFT 与 Radix Attention 的加速比与 A/F-LR：DEFT 加速比 7B 由 1.09× 升至 1.53×、34B 由 1.03× 升至 1.28×；Radix A/F-LR 在 7B 由 1.12 升至 2.50、34B 由 0.48 升至 1.16，而 DEFT-Flatten 仅升至 1.25 与 0.67。原文论证两点：①prompt 越长 Attention 越成瓶颈，DEFT 树结构平铺的加速收益越显著；②模型越大 FFN 越主导时，DEFT 仍能维持 A/F-LR<1。作为消融实验，该表验证 DEFT 在不同模型规模与序列长度下均优于最佳基线 Radix，支撑全文"树形推测解码高效且鲁棒"的核心结论。

### Table 19 (p.28) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab19.png]]
> [!quote] caption
> [Different GPUs] Speedup of D E FT in average attention latency (second) with NVIDIA RTX 4090 (24GB) for LLama3-8B model(GQA). Radix Attention is the best baseline in decoding latency.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 19 图文联合解读：**

该表展示在 RTX 4090 上对 7B/34B 两类模型、三种 prompt 长度（1k/5k/8k）下的三项量化指标：①**DEFT 解码加速比**为 1.03×–1.53×，随 prompt 延长单调上升；②**Radix Attention 的 A/F-LR** 在 7B 上高达 1.12/1.89/2.50（>1），意味着其注意力算术量超过 Flash 内存加载，存在冗余计算；③**DEFT-Flatten 的 A/F-LR** 均显著 <1（7B：0.89/1.09/1.25；34B：0.42/0.57/0.67），表明 DEFT 通过公共前缀 token 复用将注意力计算量压缩到 Flash 加载之下，逼近理论下界。

论文借此论证：**DEFT 在消费级 GPU 上仍稳定优于最强基线 Radix Attention**，且优势随 prompt 长度放大；同时 A/F-LR 指标为"为何 DEFT 快"提供了算术/内存层面的因果解释。该表构成实验链路的"跨硬件泛化"环节，证明方法不依赖数据中心级 GPU 即可生效。

### Table 20 (p.28) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab20.png]]
> [!quote] caption
> [Different Model Architectures(GQA)] Speedup of D E FT in average attention latency (second) with NVIDIA A100(80GB) for Codellama-34B model(GQA). Radix Attention is the best baseline in decoding latency.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

表20聚焦Codellama-34B（GQA架构）在A100上的Paged Attention延迟，对比Radix Attention、DeFT-Node-Chunk与DeFT-Flatten在三类树结构任务下的表现：Few-shot Prompting(b=30)为4.26/3.07/2.95秒，Multi-Step Reasoning为26.36/24.61/23.86秒，Speculative Decoding(t=64)为33.63/15.39/14.04秒。DeFT-Flatten相对最强基线Radix Attention取得1.44×、1.10×、2.40×加速，推测解码场景收益最显著。

**论证结论：** DeFT-Flatten在GQA架构下仍稳定优于现有最优解码基线。

**论文作用：** 与Table 21（MHA）构成"不同模型架构"消融实验，共同证明DeFT-Flatten对MHA与GQA异构注意力均具通用加速能力，增强方法的架构可推广性论证。

### Table 21 (p.29) ⭐深度解读
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-tab21.png]]
> [!quote] caption
> [Different Model Architectures(MHA)] Speedup of D E FT in average attention latency (second) with NVIDIA A100(80GB) for Codellama-7B model(MHA). Radix Attention is the best baseline in decoding latency.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表量化Codellama-7B（MHA）在A100上三类树结构推理场景的Paged注意力延迟（秒）：Radix Attention为12.39/53.96/96.55；DEFT-Node-Chunk为10.12/54.20/48.96；DEFT-Flatten最优为8.24/43.91/36.48，对应加速比1.50×/1.23×/2.65×。结论：DEFT-Flatten在所有场景均超越最强基线Radix Attention，Speculative Decoding收益最显著（2.65×），证明Flash Tree Attention对树结构解码的通用加速能力。该表隶属"不同模型架构"实验组，表明DEFT不仅适用于GQA模型，在MHA上同样有效，支撑其跨架构通用性结论。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\begin{aligned} \textstyle \operatorname{SegAttn}(\mA_0, \mA_1, \mA_2)= \frac{ \mA_0 e^{\operatorname{LSE}(\mQ, \mK_0)} + \mA_1 e^{\operatorname{LSE}(\mQ, \mK_1)} + \mA_2 e^{\operatorname{LSE}(\mQ, \mK_2)} }{ e^{\operatorname{LSE}(\mQ, \mK_0)} + e^{\operatorname{LSE}(\mQ, \mK_1)} + e^{\operatorname{LSE}(\mQ, \mK_2)} } \,, \text{ where } e := \text{exp} \,. \end{aligned}
$$

## 技术点深读（DEEP）

![[deep/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference.txt`（112630 字符）供引用检索。