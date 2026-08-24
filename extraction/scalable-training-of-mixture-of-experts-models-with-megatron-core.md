---
paper_num: "12"
title: "Scalable Training of Mixture-of-Experts Models with Megatron Core"
authors: "Scalable Training of Mixture-of-Experts Models with Megatron Core Technical Report NVIDIA1"
date: "2026/3/8"
arxiv: "https://arxiv.org/abs/2603.07685"
pdf: "papers/scalable-training-of-mixture-of-experts-models-with-megatron-core.pdf"
slug: "scalable-training-of-mixture-of-experts-models-with-megatron-core"
tags: [moe, training]
---

# Scalable Training of Mixture-of-Experts Models with Megatron Core

> [!abstract] 摘要（原文）
> 1\. 🚀 本报告介绍了 NVIDIA Megatron-Core 框架中用于大规模混合专家模型（MoE）训练的系统级优化方案，旨在解决参数-计算不匹配带来的内存、通信和计算效率瓶颈。 2. 🛠️ 该框架通过 MoE Parallel Folding 实现多维度并行，解耦了注意力机制与 MoE 层的并行映射，并引入了 FP8/FP4 低精度训练、细粒度激活重计算及卸载等技术来应对存储压力。 3. 📈 为了提升性能，系统集成 DeepEP 和 HybridEP 优化了 Token 分发通信，并结合分组 GEMM 与算子融合等计算优化手段，显著提升了在 NVIDIA GB200 及 H100 集群上大规模 MoE 模型训练的吞吐量。

## 元信息
- **发表日期**: 2026/3/8
- **作者**: Scalable Training of Mixture-of-Experts Models with Megatron Core Technical Report NVIDIA1
- **arXiv**: https://arxiv.org/abs/2603.07685
- **本地 PDF**: `papers/scalable-training-of-mixture-of-experts-models-with-megatron-core.pdf`
- **页数**: 88

## 图表（原文 caption + 页码）

### Figure 1 (p.9) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig01.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p09.png]]*
> [!quote] caption
> Data flow through an MoE layer: Route, Dispatch, Compute, and Combine stages.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 图示内容：** 展示MoE层前向传播的Route与Dispatch两阶段数据流。`Input Tokens [B×S, H]` 进入绿色**TopKRouter**：先经`Gating Linear`，再由`Softmax/Sigmoid`打分，最后`Top-k Selection + Load Balancing`输出`routing map`与`probs`；随后蓝色**Token Dispatcher**执行`Permute`（按专家分组tokens）→`All-to-All`（跨GPU发送）→`Postprocess`（预处理），将tokens分发至右侧`Shared`通路及各Expert。

**2) 关键结论：** 原文以此论证MoE的核心机制是**token级稀疏激活**与**跨GPU All-to-All通信**的耦合，路由决策与分发传输构成性能与扩展性的关键瓶颈。

**3) 论文作用：** 作为方法总览图，为后续章节深入讨论路由策略、通信优化、Expert并行计算等具体技术提供整体框架铺垫。

### Figure 2 (p.10) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig02.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p10.png]]*
> [!quote] caption
> Router architecture: linear projection, score function, top-𝑘selection, and load balancing. combine_postprocess (backward).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示Megatron-Core中MoE TopKRouter架构：左为分数函数（softmax归一化得[BxS, E]维分数），中为Top-K选择，输出两个并行产物——逐token概率[BxS, E]（加权组合专家输出）与路由映射[BxS, E]（dispatcher布尔掩码）；下方为两类负载均衡机制：无辅助损失的Expert Bias与全局batch级的Global_aux_loss。原文借此论证Router同时兼容aux-loss与aux-loss-free双路径，可灵活切换细粒度路由与均衡策略；该图是后续细粒度MoE并行调度、分组GEMM与token-dropless训练等扩展组件的路由计算基础。

### Figure 3 (p.13) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig03.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p13.png]]*
> [!quote] caption
> Dense Model vs MoE Model parameter/compute scaling.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图3图文解读**

图以双对数坐标对比约30个LLM的"总参数量（1B–1000B）"与"每token前向FLOPs"，●为Dense、▲为MoE，并标注≈2N参考线。Dense模型（LLaMA-3.1-405B、Nemotron-4 340B、Falcon-180B、OPT-175B/BLOOM-176B等）严格落在2N带内；MoE模型（Mixtral-8x22B、DeepSeek-V3、Hunyuan-Large、Qwen3-MoE-235B、Kimi-K2、Grok-1、Ling-1T等）总参数可达数百至千亿级，但FLOPs仅数十至百亿B，远低于2N线。论文借此论证MoE以稀疏激活实现"高参数、低算力"的扩展优势，从而引出Megatron-Core针对专家/张量/流水线并行的可扩展MoE训练方案。

### Figure 4 (p.15) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig04.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p15.png]]*
> [!quote] caption
> Expert Parallelism (EP) distributes experts across GPUs. The all-to-all communication dispatches tokens to their assigned experts and combines results.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示 **EP=4、8 Experts、2 Experts/GPU**（GPU0 持 E0/E1，GPU1 持 E2/E3）的 MoE 数据流：token 序列 [T0][T1][T2]… 经路由后，由 **All-to-All dispatch** 分发到各 GPU 对应专家计算，再经 **All-to-All combine** 回收结果。原文借此论证：EP 将专家切分到多 GPU 以摊薄单设备显存与算力，关键代价是 all-to-all 通信。该图是论文方法学的起点，为后续 EP 通信优化与大规模扩展性实验提供架构基础。

### Figure 5 (p.17) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig05.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p17.png]]*
> [!quote] caption
> Parallelism mappings: traditional constraints vs. MoE Parallel Folding decoupling.

> [!tip] 技术解读（多模态）
> 【图文联合解读】## 图文联合解读

**1) 核心对象与结构：**
左侧（传统方案）上为 TP2-DP2：序列被切成 Seq1/Seq2 两段，每段 2 个 Rank（Rank1–3）各持 1/2 Attn；下为 ETP2-EP2：4 个 Experts 被拆成两组分发到不同 Rank。右侧（Parallel Folding）上为 TP2-CP2：4 个 Rank 同处 Seq1，靠 Context Parallel 切分序列；下为 ETP2-EP1：所有 Experts（1/2 E1–E4）完整堆叠在每个 Rank 上（EP=1，专家本地化）。

**2) 关键技术结论：**
绿色虚线箭头显示二者可等价映射，证明可将原本耦合的 DP×EP 解耦为 CP×EP1——在保持等效序列并行度的同时，消除 EP 带来的跨设备 Expert 通信开销。

**3) 论文链路中的作用：**
该图作为 MoE Parallel Folding 方案的形式化定义与可行性证据，为后续显存/通信收益及大规模训练实验奠定理论基础，是该方法从"概念"走向"实现验证"的桥梁。

### Figure 6 (p.18) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig06.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p18.png]]*
> [!quote] caption
> Parallel Folding: decoupled attention and MoE parallelism mappings.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图6展示了 Parallel Folding 中 **Attention 层在单一 TP 组内**的并行配置：8 张 GPU（GPU0–GPU7）构成一个 TP=8 的张量并行组，组内通过 TP AllReduce（8 路通信）完成 attention 集合通信，A2A Scope 限定为这 8 GPU。

**论证结论**：传统方案中 attention（TP/CP）与 MoE（EP）必须共享同一并行映射，导致通信域膨胀；而 folded 布局将二者解耦——attention 在小组内保持高 TP/CP，MoE 在同小组内独立使用 ETP=1、高 EP，all-to-all 与 attention 集合通信都局限在 NVLink 互连的小 GPU 组内，从而降低跨域通信开销。

**论文作用**：作为核心方法的可视化证据，支撑 Parallel Folding 在 MoE 训练中实现 attention–MoE 解耦并行、提升可扩展性的设计主张。

### Figure 7 (p.22) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig07.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p22.png]]*
> [!quote] caption
> Memory-Efficient Permutation.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图7 联合解读：**

Figure 7 并列对比 Baseline（左）与 Memory-Efficient Permutation（右）两条 MoE 专家块前向通路，以蓝/粉色块区分临时中间张量与反向保存张量。Baseline 依次为 Router→Permute→A2A+LocalPermute→FC1→SwiGLU→FC2→Unpermute+A2A→Unpermute，粉色保存张量密集，且需缓存 probs 至最后 Unpermute 阶段。

优化版将 Permute 提前到 Router 之前，probs 与 routing map 由已置换 token 产出；并将 A2A 拆为"A2A+LocalPermute"与"A2A+Permute"双路径，用 Fused WeightedSwiGLU 内部吸收 probs（图中标注 [B×TopK×S, H] 张量就地释放），省去多处反向缓存。

**技术结论**：重排计算顺序与算子融合可显著削减 MoE 激活显存。**论文作用**：属 Megatron-Core MoE 显存优化链路的关键一环，为后续更大规模稀疏专家扩展奠定基础。

### Figure 8 (p.23) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig08.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p23.png]]*
> [!quote] caption
> Selective Recomputation.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图8展示了DeepSeek-V3架构中的**选择性重计算（Selective Recomputation）策略**。图例标注了七类操作的内存管理方式：紫色core_attn（fused_attn无需重算）、粉色moe_act、绿色layernorm、蓝色mlp_up_proj、黄色dispatch均采用**output-discarding**（丢弃输出，反向时重算）；红色虚线框标记moe模块，橙色虚线框标记shared_experts。右下块图可见shared_experts内部FC1→Swiglu→FC2三段结构，灰色阴影区域表示各模块的重计算范围。备注指出dense mlp模块的mlp_recompute未在图中绘出。

**技术结论：** 论文据此论证——重算应优先施加于"显存密集但计算廉价"的算子（layernorm、dispatch、mlp_up_proj等），从而以极小计算开销换取显著的激活显存节省，是MoE大规模训练的关键显存优化手段之一。

**论文作用：** 该图与Figure 7（通信计算重叠）共同构成第3章的两大训练加速支柱，支撑后文吞吐量与显存占用实验的优化依据。

### Figure 9 (p.24) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig09.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p24.png]]*
> [!quote] caption
> Fine-grained activation offloading: stream overlap for forward and backward passes.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图9展示前向传播中细粒度激活卸载的两流时间线。Compute Stream依次执行Forward FC1与FC2（深绿块），D2H Stream负责Offload to CPU（深灰块）。关键在于：FC1的激活无需等FC2完成即可启动卸载，箭头指示其起始时刻，浅绿"Overlap"区表明D2H传输与FC2计算在时间上完全并行。

论文借此论证：通过流级重叠，可将激活offload开销隐藏于后续计算之下，避免串行等待的墙钟代价，从而在保留大规模MoE训练所需显存卸载能力的同时，最小化对训练吞吐的影响。该机制是Megatron-Core细粒度activation offloading调度方案的核心组成部分，与并行/流水策略协同实现大规模MoE模型的可扩展训练。

### Figure 10 (p.26) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig10.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p26.png]]*
> [!quote] caption
> Fine-grained offloading and recomputation: complementary memory optimization strategies. optimization target. Megatron-Core provides two techniques: precision-aware optimization that reduces storage requirements, and CPU offloading that moves inactive state off-GPU.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示MoE层细粒度内存策略：左路Attention（mlp_norm→QKV→Core Attn→Attn Proj→mlp_norm），右路MoE（Dispatch→FC1→MoE Act→FC2→Combine），绿色活跃、灰色中间态，Shared Experts分支并行汇入。共8处配置：mlp_norm/attn_proj/expert_fc1/moe_act采用offload，layernorm/moe_act采用recompute，core_attn/mla_up_proj可OR切换，FC2输出可Discard。

技术结论：原文论证精度感知优化与CPU offloading互补，按模块粒度独立配置，使显存占用与重算开销可按需权衡。

整体作用：作为Megatron-Core的细粒度内存优化接口，与粗粒度选择性recompute构成完整栈，为大规模MoE训练提供关键显存节流能力，是系统级可扩展方案的核心配置层。

### Figure 11 (p.28) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig11.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p28.png]]*
> [!quote] caption
> Comparison of sharding strategies: (a) FSDP2 shards each parameter uniformly; (b) Megatron-FSDP flattens per-module and shards non-uniformly, aligning with communication buffers.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图(a)展示FSDP2策略下3个Linear模块在Device Rank 0/1上的分布：Linear 1采用Shard_Param按模块分片集体缓冲（蓝色，每Rank各持一份对应条目），Linear 2、3为均匀分片（绿/红色），再以DTensor形式映射至各Rank对应位置。原文借此论证FSDP2"逐参数均匀分片"使通信缓冲与shard不对齐、引入额外开销；该图为对比铺垫(b) Megatron-FSDP"按模块扁平化、非均匀分片并对齐通信缓冲"的核心论点服务，是论文分布式训练设计章节中支撑其sharding strategy优越性的关键原理示意。

### Figure 12 (p.28) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig12.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p28.png]]*
> [!quote] caption
> Persistent double-buffer design: two pre-allocated buffers are cycled across FSDP collectives, eliminating allocation overhead and enabling NCCL User Buffer Registration.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示对比FSDP梯度处理两种方案：上方为torch.empty的CUDACachingAllocator每次通信重新分配；下方Persistent双缓冲设计——两个预分配buffer在FSDP collectives间循环复用，经Reduce Scatter产出Gradient shard。

原文借此论证：**消除每次collective的分配开销，并使NCCL User Buffer Registration成为可能**。该设计在论文中支撑Table 12关于不同并行策略（degree 𝑑）对内存与通信影响的对比实验，是MoE大规模训练通信栈优化的核心环节，对降低显存峰值、提升集合通信效率至关重要。

### Figure 13 (p.30) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig13.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p30.png]]*
> [!quote] caption
> Expert parallelism across 4 GPUs with 4 experts.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心对象与结构**：图示 4 块 GPU（GPU0–3），每卡承载 1 个专家，整体并行处理 8 个 token（a1–a8，每卡 2 个）。数据流为：Attention Layer 输出 → 本地 Router 决策 → token 被染色标记目标专家（如 a2 标绿、a1 标蓝）→ 经 EP group 的 **Dispatch（All-to-All 集合通信）** 将 token 跨卡路由至对应专家所在 GPU。

2) **关键技术结论**：Expert Parallelism 的核心通信代价来自 Dispatch 阶段的 **All-to-All**：Router 在本地完成路由决策后，token 必须在 EP group 内重新分发，使每卡只处理分到本地专家的子集——这是 EP 区别于 TP/PP 的标志性通信模式。

3) **论文中的作用**：作为 §4.2.1 "Communication Anatomy" 的开篇图，奠定后续讨论 Combine、GEMM 切分、All-to-All 优化（如双向/TMA 加速）等问题的基础，是 Megatron-Core MoE 通信栈设计的参照原型。

### Figure 14 (p.31) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig14.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p31.png]]*
> [!quote] caption
> The dispatch kernel design of HybridEP.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示HybridEP调度内核两路数据流：①节点间（绿框）从其他节点同rank获取RDMA Token/Prob/Scaling factor；②本地（粉框）从注意力层与路由器取Token/Prob/Scaling factor。前者由RDMA warp组跨节点交换后送入"Global Memory→SM warp group"，与本地输入共同经FIFO转发至目标expert。论证核心：HybridEP将跨节点RDMA与节点内dispatch解耦——先由RDMA warp组完成同rank交换，再由SM warp组在节点内FIFO推送，避免SM直接处理RDMA数据。该设计是MoE专家并行通信栈中dispatch阶段token高效路由的关键实现。

### Figure 15 (p.31) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig15.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p31.png]]*
> [!quote] caption
> The combine kernel design of HybridEP.

> [!tip] 技术解读（多模态）
> 【图文联合解读】1) **对象与结构**：图中是 HybridEP 的两条并行 combine 路径，每条处理 Token、Prob 两类数据：本地 Global Memory→SM/intra-node warp group，或其他节点同 rank 的 RDMA Token/Prob→SM/inter-node warp group；随后均经 SMEM Cyclic FIFO。  
2) **技术结论**：节点内与 RDMA 通信分工处理，并用共享内存循环队列衔接，减少 CPU 调度、拷贝和同步开销。  
3) **作用**：作为 MoE 通信到专家计算的 kernel 实现图，支撑 HybridEP 的低开销 token 组合及性能扩展性实验。

### Figure 16 (p.32) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig16.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p32.png]]*
> [!quote] caption
> Merged FWD-FWD Timeline with all-to-all Overlapping.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 16）**

该图展示双微批次（u-Batch Even / Odd）在 MoE 流水线中的三段时序，每行均包含 FWD→BWD→FWD；三段顶部标注"Merged"，下方虚线框分别标记 ubatch 0（归属 Even 行）与 ubatch 1（归属 Odd 行）。

**关键结论**：1F1B 流水使 ubatch 1 的 FWD 与 ubatch 0 的 BWD 并发；"Merged"段表明连续的 FWD-FWD 阶段可与 MoE 专家路由的 all-to-all 通信重叠执行，从而隐藏通信开销。

**论文作用**：作为 Megatron-Core MoE 扩展方法的核心调度图，支撑其"计算-通信全重叠"的高吞吐训练策略。

### Figure 17 (p.33) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig17.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p33.png]]*
> [!quote] caption
> Merged FWD-BWD Timeline with all-to-all Overlapping.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图17图文联合解读：**

**1) 核心对象与结构**：图示为按奇偶分流的微批次双轨时间轴（u-Batch-Even / u-Batch-Odd），横向分为三段："Not Merged"段仅含 ubatch0 的 FWD；"Merged-1"段将 ubatch0 的 BWD 与 ubatch1 的 FWD 并排放置；"Merged-2"段将 ubatch1 的 BWD 与 ubatch2 的 FWD 并行呈现，颜色块以绿(FWD)/灰(BWD)区分。

**2) 论证的技术结论**：原文借此说明，在 MoE 训练中，相邻微批次的前向计算与上一微批次的反向计算可"合并"(merged)重叠执行，而非严格串行；该调度使 all-to-all（专家并行 dispatch/combine）通信得以嵌入计算空隙，从而隐藏通信开销。

**3) 在论文整体中的作用**：作为"All-to-All Overlapping"优化策略的可视化佐证，支撑 Megatron-Core MoE 流水线实现通信-计算重叠、提升大规模专家并行训练吞吐量的核心方法论结论。

### Figure 18 (p.34) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig18.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p34.png]]*
> [!quote] caption
> EP all-to-all communication overlap strategies: baseline vs. 1F1B with W/D split.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图18展示三种EP all-to-all通信与计算的执行时间线对比：

1）**Baseline（无重叠）**：F/Attention→F/Dispatch(A2A)→F/MLP→F/Combine(A2A)→B/Combine→B/MLP→B/Dispatch→B/Attention严格串行，A2A通信占迭代时间30–40%。

2）**1F1B Overlap Baseline**：分Compute Stream与Communication Stream两轨，将F/ATTN-F/MLP与B/COMBINE-B/DISPATCH错位并行，但仍存在尾部暴露A2A。

3）**1F1B Overlap with W/D Split**：进一步把MLP拆为D/MLP与W/MLP两段，与A2A更细粒度交错；暴露A2A通信压缩至<5%，overlap ratio达93%，较中间方案获得明显Speed Up。

**结论**：论文用此图论证W/D Split是EP通信隐藏的最优方案，将通信瓶颈从30–40%降至5%以下。

**作用**：位于EP通信优化章节，作为支撑Megatron-Core MoE大规模训练效率的关键可视化证据，为后续性能数字提供机理说明。

### Figure 19 (p.35) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig19.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p35.png]]*
> [!quote] caption
> Interleaved PP Timeline with all-to-all Overlapping.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图19展示了**交错式PP时间线**（PP=4，VPP=3，Grad accumulation=8）在**warmup阶段**对all-to-all通信的隐藏策略。图例用橙/蓝/粉三色区分FWD的三条虚拟管道及对应BWD，每格数字标记微批次序号（1–8）。红色框出warmup结束时多执行的一个额外微batch，其fprop紧接主时间线起点的microbatch（标注"Execute one extra micro-batch"），而bprop则与下方相邻微batch的fprop/bprop重叠（多箭头所示）。

关键结论：**通过在warmup阶段注入额外微batch**，使后续微batch的前向/反向与MoE all-to-all通信在时间轴上**计算-通信交叠**，从而隐藏通信开销。

在论文中，该图支撑Megatron-Core交错流水线中"**通信隐藏于计算**"的核心优化链路，是MoE大规模训练高效率的关键实证。

### Figure 20 (p.37) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig20.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p37.png]]*
> [!quote] caption
> The pipeline for permute fusion in the training process. • Preprocessing: Permutation is fundamentally a data transfer process that requires tokens to be stored consecutively in the buffer corresponding to each expert. The purpose of the preprocessing step is to generate an offset map (Row ID map in figure 20), which indicates the offset of each token in the input and output buffers. This ensures 

> [!tip] 技术解读（多模态）
> 【图文联合解读】**结构**：permute fusion 流水线分 Forward/Backward 两路。Forward：tokens、probs → Preprocess Kernel（生成 row ID map）→ Permute Kernel → permuted tokens/probs → Linear FC1 → Act Function（融合 probs）→ output。Backward：gradient → Act Function(反) → Linear FC1(反) → permuted grad → Unpermute Kernel（复用 row ID map）→ tokens grad、probs grad。黄色虚线框标注 row ID map 在前后向间共享。

**结论**：offset map 一次生成、前后向双向复用，避免反复构建路由索引；permute 与 FC1/激活融合，消除"多小 kernel 启动 + GPU 额外开销"。

**作用**：MoE 专家并行中高效 token 路由/调度的核心机制，是大规模 MoE 可扩展训练的关键支撑。

### Figure 21 (p.38) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig21.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p38.png]]*
> [!quote] caption
> The workflow of the router fusion. • Computation of MoE auxiliary loss: Building on step 2, the auxiliary loss computation is fused into a single kernel.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图21展示MoE路由器的融合流程：输入经Gating Linear产生Logits后，分两路径并行演示——上路采用Topk/Group Topk搭配Sigmoid/Softmax，下路用Topk搭配Sigmoid/Softmax，两路径分别汇聚为单一"Fused kernel"。

**关键论证：** 路由器中的Top-k专家选择与激活函数可被融合为单个kernel，省去多次中间张量写回与launch开销，相比传统分步执行显著降低访存与调度代价。

**在论文中的位置：** 该图隶属Megatron-Core的MoE性能优化模块（与Figure 19/20的grouped GEMM等并列），是支撑其端到端可扩展训练链路中路由器层级算子融合优化的关键可视化说明。

### Figure 22 (p.39) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig22.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p39.png]]*
> [!quote] caption
> Traditional execution (top) versus CUDA Graph execution (bottom).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图22 联合解读**

**核心对象与结构**：上下两幅子图均含 CPU/GPU 双时间线。上图（传统执行）CPU 侧交替出现 *Python & Framework* 与 *Launch K1* 等多次调用块，GPU 侧 K1、K2 之间形成 "CPU Overhead" 气泡；下图（CUDA Graph 执行）CPU 侧仅一个 *Graph Launch (Single API call)* 长块，GPU 侧 K1、K2 紧密背靠背，底部绿色箭头标注 "NO GPU BUBBLE"。

**关键技术结论**：原文借此论证——逐核启动路径下 CPU 调度开销足以让 GPU 产生空闲等待，而单次 API 提交整张计算图可彻底消除该空泡。

**论文中作用**：MoE 训练含大量细粒度专家计算与 all-to-all 通信核，传统调度极易使 GPU 空转。本图为 Megatron-Core 集成 CUDA Graph 提供执行模型层面的动机支撑。

### Figure 23 (p.39) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig23.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p39.png]]*
> [!quote] caption
> Full versus layer-wise CUDA Graphs in one training iteration (three layers, two microbatches).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图23解读：**

图示一次训练迭代（3层、2微批次）的调度序列：前向块F₁₁–F₁₃、损失块L、反向块B₁₁–B₁₃依次排列。**紫色虚框（Layer-wise CUDA Graphs）**逐层独立封装每个F/B；**橙色虚框（Full CUDA Graphs）**将整段前向（或整段迭代）打包为单一图。

**技术结论：** MoE模型中各层专家路由使每层处理的token数动态变化，Full CUDA Graph要求全段shape一致，因此**无法捕获**；Layer-wise方案将每层作为独立子图capture，既复用kernel消除launch开销，又容忍层内shape浮动。

**方法链作用：** 是论文针对MoE特殊结构对CUDA Graph机制的关键改造，构成Megatron-Core可扩展MoE训练性能优化的核心组件之一。

### Figure 24 (p.40) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig24.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p40.png]]*
> [!quote] caption
> Partial CUDA Graphs capture static components (attention, shared experts, router, preprocessing) while leaving dynamic expert computation outside the graph.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图24联合解读**

1) **结构与数据流**：图24将单个MoE Transformer层按"静态/动态形状"划分为三个CUDA Graph scope与三段图外区。紫色"attn"框内含 LayerNorm→Attention QKV→Core Attention→Attention Projection→Bias·Dropout·Add 共5个静态算子；绿色"moe_router"框含 Gating→Top-K Routing，并旁路接入Shared Expert；蓝色"moe_preprocess"框含Permutation与AG A2A-v in/out splits。图外（红色"Dynamic Shapes"括号）为 Global A2A-v exchange tokens、Local Permutation、Routed Experts GEMM、Local Unpermutation、Global A2A-v recover tokens、Unpermutation。

2) **关键技术结论**：CUDA Graph只捕获形状固定的组件（attention、router/shared expert、preprocess），将每迭代变化的per-expert token数对应的Routed Experts GEMM及dispatch/combine通信排除在图外。

3) **链路作用**：在dropless MoE训练中通过per-layer partial graph capture，在最大化kernel launch优化（静态路径）与容忍动态token分布之间取得平衡，是MoE与CUDA Graph协同的性能基础设施。

### Figure 25 (p.41) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig25.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p41.png]]*
> [!quote] caption
> Transformer layer forward pass: without (upper) and with (lower) partial CUDA Graphs. CPU overhead is largely eliminated for static components.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图25联合解读**

**1）核心对象与结构**
该图为NSight Systems profiler时间线，对比Transformer层前向传播两版本在+104~109ms（无CUDA Graph，上）与+97.5~103ms（部分CUDA Graph，下）区间的执行序列。按MoE流程划分为**preprocess、dispatch、routed experts（含GroupedGEMM_parallel/nvls）、combine**四个阶段。上图各kernel块之间存在明显**空白间隙**（CPU launch overhead）；下图左侧绿色"CUDA Graph"区块连续紧凑，可见`cudaMemcpyAsync`等异步调用将多步操作封装，kernel间隙被消除，而dispatch/combine等动态部分仍保留外部调度。

**2）关键技术结论**
Megatron-Core对静态可复现的计算段（attn、expert GEMM等）实施CUDA Graph捕获，可基本消除CPU发射开销与launch latency；对依赖token路由、动态专家分配的dispatch/combine则保留非图路径，从而兼顾**执行效率与动态灵活性**。

**3）在论文中的作用**
作为NSight实测证据，支撑文中核心论点——Partial CUDA Graphs是Megatron-Core MoE训练实现高吞吐的关键优化之一，与并行张量/专家、TokenDrop等优化协同，使大规模MoE训练可扩展。

### Figure 26 (p.42) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig26.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p42.png]]*
> [!quote] caption
> Why Pipeline Parallelism prevents CUDA Graphs from being shared across microbatches. With PP (top): Execution is interleaved—multiple forward passes run before any backward pass. If microbatches share a graph, F_mb1 overwrites saved context of F_mb0 before B_mb0 uses it, causing memory corruption. Each microbatch needs its own graph (𝐿× 𝑀× 2 graphs total). Without PP (bottom): Execution is sequent

> [!tip] 技术解读（多模态）
> 【图文联合解读】图中以 \(L\) 层、\(M\) 个微批比较执行顺序：启用 PP 时连续运行 \(F_{mb0},F_{mb1},\ldots\)，再统一反向；禁用 PP 时按 \(F_{mb0}\!→\!B_{mb0}\!→\!F_{mb1}\!→\!B_{mb1}\) 执行。CUDA Graph 保存的反向上下文会被后续前向覆盖，故 PP 下不能跨微批共享，总计需 \(L·M·2\) 个图；无 PP 仅需 \(L·2\) 个。图中解释了两者冲突，为图数量估算及 MoE 训练优化设计提供依据。

### Figure 27 (p.45) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig27.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p45.png]]*
> [!quote] caption
> ECHO workflow for forward and backward passes. The planner generates routing and hot expert maps. Expert Dispatch clones hot expert weights to spare slots; Expert Gradient Dispatch reduces gradients back to home experts.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图27（Backward）图文联合解读：**

**1) 核心结构：** 图示ECHO反向计算流，自底向上为：Combine backward → FC2 双轨（dgrad 主路径 + wgrad 并行）→ MoE act backward → FC1 双轨（dgrad + wgrad）→ Dispatch Backward。两条黄色模块贯穿全程——左侧 "Expert Dispatch" 将 home expert 权重分发至 dgrad 计算路径；右侧 "Expert Gradient Dispatch" 从 wgrad 路径汇聚梯度回传 home expert。两条横向 dashed 线划分出 FC2、MoE act、FC1、dispatch 四个阶段。

**2) 关键结论：** 反向与前向结构对称——dgrad 在被克隆的 hot expert 上算、wgrad 归约回 home expert，从而在不改 MoE 算法的前提下，保持专家并行并复用热专家权重，避免跨 rank 重复存储。

**3) 论文作用：** 与前向图配对构成完整 ECHO 调度示意图，是论证"调度即扩展性"的核心证据，支撑 ECHO 在不修改路由/并行框架条件下实现 MoE 高效训练的结论。

### Figure 28 (p.46) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig28.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p46.png]]*
> [!quote] caption
> Memory layout comparison across three execution modes. Left: Eager mode allocates memory dynamically based on actual usage. Middle: Baseline static shape requires worst-case sized buffers for each layer independently, causing severe fragmentation when actual usage is lower. Right: Paged Stashing uses a single worst-case tmp buffer shared across layers for computation, while a paged stashing buffer

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**核心对象与结构：** 图分三列对比三种执行模式的显存布局。每列含多层（行）×多专家（Exp 0/1/2）的方块堆叠，绿色为实际占用 token（编号 0–5），白色为空闲区，虚线框表示预分配但未用容量。Eager 列贴合实际、无浪费；Static Shape 列每层独立预留最坏容量，白色碎片显著；Paged Stashing 列各层共享一个超尺寸 tmp 缓冲区，配合 Stashing buffer 将分散 token 紧凑填入。

**关键结论：** Paged Stashing 以"共享最坏尺寸 tmp + 分页暂存"机制，在保留静态分配优势的同时，把碎片率逼近 Eager 水平，兼顾稳定性与显存利用率。

**论文作用：** 为 MoE 训练中 Expert Parallel 显存瓶颈提供解决方案的可视化依据，支撑 Paged Stashing 作为 Megatron Core 中 MoE 通信–计算重叠优化的核心设计。

### Figure 29 (p.46) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig29.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p46.png]]*
> [!quote] caption
> Paged Stashing stream overlap. Forward pass: After Layer N computes, its activations are stashed (copied from tmp buffer to paged stashing buffer) on a dedicated Pack stream while Layer N+1 computes on the main Compute stream—the stash is completely overlapped. Backward pass: Activations for Layer N are pre-fetched (reloaded from stashing buffer to tmp buffer) on the Unpack stream before Layer N b

> [!tip] 技术解读（多模态）
> 【图文联合解读】**联合解读：**

1) **图示对象**：横向时间线对比两条 CUDA Stream——绿色 Compute Stream（依次执行 Forward Layer N、N+1），深灰 Stash Stream（执行 Layer N 激活从 tmp buffer 拷至 stash buffer）；两者在时间轴上以箭头衔接，浅绿"Overlap"区表明 Layer N 的 stash 拷贝与 Layer N+1 的前向计算完全并行执行。

2) **关键结论**：前向 stash 通信可与下一层计算 kernel 完全重叠，专用 Pack Stream 使 tmp→paged stash 的拷贝延迟被计算掩盖，不引入额外气泡。

3) **链路作用**：作为 MoE 训练显存-计算重叠优化的核心证据，证明 paged stashing 通过流并行实现了激活备份零开销，是支撑大规模 MoE 流水线高吞吐的关键环节。

### Figure 30 (p.50) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig30.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p50.png]]*
> [!quote] caption
> FP8 training recipes: Per-Tensor Scaling, Blockwise FP8, and MXFP8. A reduced-precision training recipe consists of: • Data format. There are two types of FP8 format: E4M3 and E5M2 [71, 74]. Usually there are two combinations used in training: ∘E4M3: Inputs, weights, and gradients are all quantized in the E4M3 format. ∘Hybrid: Inputs and weights are quantized in E4M3, while gradients are quantized

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图示内容（量化）**：展示三种FP8量化方案的缩放因子粒度。Per-Tensor为整张量1个scale（最粗，单色大方块）；Blockwise为128×128块1个scale（中等，2×2示意）；MXFP8为1×32元素1个scale（最细，6×6共36个小色块）。底部双向箭头标注粒度光谱：左侧"Coarse / Fewer Scales"，右侧"Fine / More Scales"。

**技术结论**：FP8训练配置由"数据格式（E4M3/Hybrid）+ 缩放粒度"联合定义；粒度越细→scale越多→数值精度越高，但scale元数据存储与计算开销也越大，三者构成精度–效率的权衡谱系。

**方法作用**：位于第5.3节首图，承接前文"三堵墙"分析，作为Reduced-Precision Recipes的形式化铺垫，为后续NVFP4讨论建立粒度对比基准。

### Figure 31 (p.52) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig31.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p52.png]]*
> [!quote] caption
> The computation of a linear layer with various FP8 recipes. Note the differences in quantization granularity and tensor layout requirements across platforms. precise due to the finer-grained scaling granularity, and has better performance due to the native support of MXFP8 in the Tensor Core. Therefore, MXFP8 is the default FP8 recipe on the Blackwell platform.

> [!tip] 技术解读（多模态）
> 【图文联合解读】## 图文联合解读

**核心对象与结构**：图31由四个子图(a-d)组成，分别展示线性层在不同平台、不同FP8方案下的前向(Forward)、反向(Backward)、优化器(Optimizer)计算流程。Hopper平台(a/c)需要"Cast and Transpose"以适配行/列量化布局；Blackwell(b)仅需"Cast to FP8"无需转置；(c)引入Blockwise(1D行/列+2D块)；(d)在Blackwell上使用MXFP8原生"Quantize"操作，所有张量(输入、权重、梯度)均为Rowwise/Colwise MXFP8。

**关键技术结论**：MXFP8(d)相较Per-tensor(a/b)和Blockwise(c)，量化粒度更细(finer-grained)，因此精度更精确；且Blackwell Tensor Core原生支持MXFP8，性能更佳，故成为Blackwell默认FP8方案。

**论文链路作用**：该图属于精度/量化章节，为MoE大模型训练选择低精度数值方案提供决策依据，与并行策略、通信优化共同构成Megatron-Core可扩展训练栈的核心组件。

### Figure 32 (p.53) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig32.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p53.png]]*
> [!quote] caption
> FP8 primary weight quantization scheme for blockwise scaling.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示展示 **FP8 主权重按块缩放（blockwise scaling）量化在数据并行（DP）下的边界处理**：

1) **核心对象与结构**：左图表示权重矩阵被划分为多个量化块（红框即一块），该块在 2D 布局下可能被切分到不同 DP rank；中图（DP rank 0）演示"块不完整"情形——仅用当前 rank 持有的子块数据计算 local abs-max；右图（DP rank 1）演示"块完全不在本 rank"情形——将该块 abs-max 置 0。

2) **关键结论**：在 DP 切分下，量化块的 abs-max 必须在各 rank 本地按 2D 布局感知地独立计算，空块置 0 不参与缩放，从而保证跨 rank 量化后统计量一致、避免溢出。

3) **论文作用**：该图是 FP8 量化章节中"分布式正确性"的支撑图，衔接块级缩放方案与 Megatron-Core 的并行栈，使 FP8 主权重量化可与 TP/DP/EP 并行兼容，服务于 MoE 大规模训练中的显存与吞吐优化。

### Figure 33 (p.54) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig33.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p54.png]]*
> [!quote] caption
> FP8 primary weight quantization scheme for delayed scaling and per-tensor current scaling.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图示内容**：三个权重矩阵(Weight 0/1/2)按 DP rank 边界 flatten 拼接到一条全局权重 buffer；每个 rank 持有其对应分片的 FP32 master weights，经三步完成量化——① Step 1 取本地 abs-max；② Step 2 通过 all-reduce 在 rank 间汇总得 global abs-max；③ Step 3 据此将 master 权重量化（partial cast）为 FP8 model weights。

**技术结论**：方案采用 **delayed scaling**（沿用上一 step 的 global abs-max，避免当前步等待同步）与 **per-tensor current scaling**（整条 flattened buffer 共享单一张量级缩放因子），在保证量化精度的同时把同步开销降到最低。

**论文作用**：支撑 Megatron-Core 中分布式优化器的 FP8 量化流水线，使 all-reduce 通信与 FP8 cast 流水并行，是 MoE 大模型可扩展 FP8 训练栈中实现权重低精度存储/通信的关键一环。

### Figure 34 (p.57) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig34.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p57.png]]*
> [!quote] caption
> SDPA exhibits 𝑂(𝑠2) complexity, while MoE and the remaining attention operations exhibit 𝑂(𝑠) complexity. Therefore, SDPA dominates the computation at longer sequence lengths.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图(b)展示4K→256K序列长度下SDPA与MoE占总FLOPs占比的此消彼长：SDPA（红）由4K约13%单调升至256K约90%；MoE（蓝）由4K的59.4%降至256K的约6%。两曲线在约16K附近交叉，4K时MoE主导（59.4%），64K时SDPA主导（69.7%）。

原图用以论证：SDPA复杂度为Θ(s²)、MoE及其他操作仅Θ(s)，故长序列训练时注意力成为算力瓶颈。论文据此强调须重点优化SDPA（如FlashAttention内核），才能使MoE模型在长序列场景下保持可扩展性。

### Figure 35 (p.59) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig35.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p59.png]]*
> [!quote] caption
> Communication and computation patterns of TP and two types of CP.

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图以表格形式对比TP与两种CP（Context Parallel）在Core Attention中的通信与计算模式：CP(P2P)线性层权重复制，K/V切片直接送入SDPA并伴点对点通信；CP(A2A)权重同样复制，但K/V先经All-to-All重分布再输入SDPA；TP权重被切分并行、无额外集合通信步骤。

关键结论：CP方案下线性层权重在各rank上重复存储，attention输入仍需通过P2P或A2A通信才能正确分片到各rank；而TP通过将权重本身切分，使各rank天然持有对应分片，通信模式更简洁高效。

该图为论文论证长序列训练中CP与TP的通信开销权衡提供直观对比，是方法选型与性能分析的核心参考依据。

### Figure 36 (p.61) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig36.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p61.png]]*
> [!quote] caption
> Unpacked vs. Packed sequences.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构**
图(a)"Unpacked sequences"展示5条变长序列（橙、蓝、米、绿、紫），按各自长度独立放置，未做拼接。最长序列（如蓝色）决定批处理行高，其余序列（尤其米色）右侧留有大量空白/padding，仅为对齐最长序列。

**2) 关键技术结论**
"未打包"模式下，短序列被强制padding到与最长序列等长，造成**显著的计算浪费**——GPU算力消耗在无意义的padding token上，**吞吐效率下降**。这在MoE训练中尤其严重，因为不同样本激活的专家数与序列长度相关，padding会污染token路由与负载统计。

**3) 在论文中的作用**
该图作为**动机图**，引出后文提出的"Packed sequences"方案：通过将多条样本拼接填满固定context长度，消除padding冗余，从而**提升MoE训练吞吐与专家路由统计的准确性**，是该方法整体效率优化的关键铺垫。

### Figure 37 (p.61) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig37.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p61.png]]*
> [!quote] caption
> Compute imbalance in causal attention over packed sequences. are partitioned and which CP communication group is used by attention operators, without requiring any parameter redistribution or optimizer-state migration. Therefore, Dynamic-CP provides a practical form of dynamic parallelism for variable-length training with minimal framework overhead. Related work, including

> [!tip] 技术解读（多模态）
> 【图文联合解读】图中用4×4与4×2网格表示打包序列的因果注意力有效计算：左图7个单元集中为6+1，右图呈4+3分布，体现等长切分不等于计算均衡。原文据此指出变长样本会导致Context Parallel通信组负载不均；Dynamic-CP按序列长度动态选择切分和通信组，无需迁移参数或优化器状态，仅增加很小框架开销。该图是Dynamic-CP的动机性论证，并非性能实验。

### Figure 38 (p.61) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig38.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p61.png]]*
> [!quote] caption
> Dynamic Context Parallelism for Packed Sequences.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图(a)展示三条不等长序列（橙长/蓝中/绿短）打包输入。(b)标准CP2方案：每个微批次将整条打包序列在GPU-0与GPU-1上重复切分并行，双卡各持有完全相同的橙+蓝+绿序列，存在显著冗余。(c)动态CP方案：微批次0的橙色长序列仍用CP2双卡拆分；微批次1则按长度自适应——蓝序列归GPU-0、绿序列归GPU-1，各自改为CP1单卡执行，CP组数随序列长度动态切换。该机制有效消除短序列的跨GPU通信与重复计算开销，是Megatron-Core处理变长packed sequences以提升MoE训练吞吐的关键并行优化。

### Figure 39 (p.64) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig39.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p64.png]]*
> [!quote] caption
> Load balancing strategies in Megatron-Core MoE.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图分两栏对比Megatron-Core MoE的两种负载均衡策略：(a)辅助损失法沿 Logits→Score Function→Top-k Selection→Dispatch 路径，先按分数函数计算专家接收概率 P_i=(1/T)Σ probs(x,i)，再统计路由频次 f_i=(1/(T·topk))Σ routing_map(t,i)，以 L_aux=α·E·Σ(f_i·P_i) 做梯度反向传播的"可微软均衡"；(b)Sinkhorn 路线沿 Logits→exp→Row/Col Norm 迭代收敛→Top-k→Dispatch，以矩阵归一化分配实现"非可微硬均衡"（图中示例矩阵元素为 -4,-3,-2,-1）。两者为框架提供互补的专家路由机制选择，是支撑大规模MoE可扩展训练栈的关键模块之一。

### Figure 40 (p.65) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig40.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p65.png]]*
> [!quote] caption
> Shared expert architecture in Megatron-Core MoE. The shared expert processes all tokens while routed experts process only their assigned tokens. When overlap is enabled, shared expert computation runs in parallel with the token dispatch/combine communication, hiding its latency. FLOP and per parameter. The architecture has been adopted by NVIDIA’s Nemotron-3 Super and Ultra models.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图40展示Megatron-Core MoE的**共享专家架构**流程。核心结构：输入token流（T1–T7）经门控选Top-K→**Token Dispatch**（All-to-All通信，橙色框）→Norm→**Routed Experts Compute**（橙色框）→Norm→**Token Combine**（橙色框）→Add叠加共享专家输出→输出token。

**关键技术结论**：共享专家处理**全部token**，路由专家仅处理Top-K被分配的token；当启用overlap时，共享专家计算与Token Dispatch/Combine的All-to-All通信**并行执行**，从而隐藏通信延迟。

**论文作用**：该图是Megatron-Core实现**计算–通信重叠（overlap）**优化的核心证据，支撑其作为Nemotron-3 Super/Ultra模型采用的MoE架构基础，证明双分支设计可在不增加关键路径时延的前提下扩展专家容量。

### Figure 41 (p.66) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig41.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p66.png]]*
> [!quote] caption
> Flexible Pipeline Parallel Placement. 66

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示DeepSeek-V3在16 PP×2 VPP共32虚拟阶段上的灵活流水线布局：PP Rank 0首段承载Embedding+3个Dense Decoder（计算量≈2个MoE Decoder当量）；PP Rank 1–13为标准阶段，每rank均布2个MoE Decoder；末端PP Rank 14放置MTP（多token预测）层，PP Rank 15放置轻量Loss层，绿色箭头标示数据流向。

**技术结论：** 打破传统均匀层分配，支持异构层（轻量Embed/Loss/Dense vs 重型MoE/MTP）按计算与内存特性差异化编排至pipeline首尾，避免出现瓶颈rank。

**论文作用：** 与Table 10配套，证明Megatron-Core具备非均匀pipeline placement能力，是训练超大规模MoE模型（如DeepSeek-V3）的关键系统级支撑。

### Figure 42 (p.67) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig42.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p67.png]]*
> [!quote] caption
> An example of granular upcycling a dense layer into E2G2T2 fine-grained MoE. E2G2T2 denotes 4 experts, top 2, with half intermediate size. (1) We shard MLP weights in the intermediate dimension (4ℎ→2ℎ) then duplicate the shards. (2) We initialize half the router weights then duplicate them. This ensures Top2 always selects one of each MLP shard so MoE output is the same as the dense model at the s

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 42）：**

图示E2G2T2细粒度MoE结构：输入经**Grouped Router→topK/Softmax**，从**4个专家**中选通**top-2**（红箭头激活，灰X门控），每个专家含W1(**h×2h**)与W2(**2h×h**)，即中间维为密集MLP的一半，求和后输出。

**关键技术结论：** 将密集MLP中间维切分为两半(4h→2h)并复制成2组专家，同时复制路由器权重使Top2**必然各选中一个不同分片**，训练起始MoE输出与原密集模型严格一致。

**作用：** 这是"granular upcycling"的核心机制，实现从密集检查点**无损初始化**细粒度MoE，是论文扩大专家数量同时保持训练稳定性的关键链路。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.15) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab02.png]]
> [!quote] caption
> Contrasting parallelism requirements of attention and MoE layers within a single Transformer block.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表沿"计算特性 / TP / CP / EP"四个维度对比同一Transformer块内Attention（稠密）与MoE（稀疏）层的并行需求。Attention每token与全序列交互，QKV矩阵大适配高TP，长序列受益于高CP，无EP概念；MoE每token仅路由K/E个专家，单专家维度小使高TP适得其反，无序列依赖使CP失效，必须以EP分布大量专家。

关键结论：同一块内两类层并行需求根本冲突，无法用单一方案统一处理，必须为MoE引入EP并设计TP/EP/CP细粒度可调的多维混合并行。

作用：作为方法动机表，支撑Megatron-Core中MoE专用并行调度（分片、组限专家、All-to-All通信优化）的设计依据。

### Table 4 (p.23) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab04.png]]
> [!quote] caption
> summarizes the memory reduction achieved by different recomputation targets for the DeepSeek-V3 configuration in Table 3 .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明：图像中未呈现 Table 4 的实际表格内容，仅展示了引用该表的两段正文（Granular recomputation 与 Output-discarding recomputation），数据无法辨认。以下仅依据原文解读：**

1) **核心对象**：Table 4 量化对比了 DeepSeek-V3 配置下，不同重计算（recomputation）目标所获得的显存节省幅度，包括专家 MLP 激活函数、LayerNorm、MLA 上投影等细粒度模块，以及"丢弃输出"重计算策略。

2) **关键技术结论**：原文论证两点——①细粒度（granular）重计算仅对选定的子模块重算，附加计算开销 <5%，却能显著降低激活显存；②"输出丢弃"重计算在前向时及时释放 checkpoint 模块的输出，反向时再重算恢复，进一步压缩显存，且不损失梯度正确性与训练动力学。

3) **在论文链路中的作用**：Table 4 作为实验证据，支撑 MoE 大模型训练栈中显存优化的两类核心技术主张，与 Table 3 的模型配置、Figure 4 的 EP 通信方案共同构成 Megatron-Core 在计算、通信、激活三维度协同扩展 MoE 训练的方法论闭环。

### Table 5 (p.25) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab05.png]]
> [!quote] caption
> Memory and throughput impact of fine-grained activation offloading.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表5核心内容**：对比两模型在开启细粒度激活卸载（+Offload）前后的显存与吞吐。
- **DeepSeek-V3 full**（TP1PP8EP32VPP4, MXFP8）：169→151 GB（**−10.7%**），945→930 TF/s（**−1.6%**）——显存显著节省，吞吐近乎无损；
- **Qwen3-235B**（TP2→TP1 + EP16→EP64）：172→175 GB（**+1.7%**），800→920 TF/s（**+15.0%**）——结合并行折叠后，显存略增但吞吐大幅跃升。

**技术结论**：激活卸载与MoE Parallel Folding（尤其EP扩展）存在强协同——以极低代价换取显存，或近乎"白嫖"地获取吞吐增益，验证了Megatron Core中激活管理与并行解耦策略的实用性。

**实验链作用**：作为支撑性数据，证明在数十B–千B级MoE模型训练中，激活卸载是平衡显存与吞吐的关键优化手段，为整篇方法的可扩展性论证提供量化证据。

### Table 7 (p.32) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab07.png]]
> [!quote] caption
> EP Scaling Performance for HybridEP and all-to-all (in µs).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 7 联合解读**

1) **对象与数据**：该表量化了 HybridEP 与 all-to-all 两种 MoE 通信原语，在 GB200 与 H100 两种硬件上、EP size ∈ {8,16,32,64} 的 dispatch 与 combine 时延（µs）。关键读数：GB200 EP=64 dispatch 为 675 vs 930，差距温和；H100 EP=64 dispatch 达 4626 vs 9164，HybridEP 近乎 2× 加速；combine 趋势一致。

2) **关键结论**：HybridEP 在大 EP 规模下显著优于传统 all-to-all，且优势在缺乏高速域内互联的 H100 上被放大——印证了 Fig.7 中 Memory-Efficient Permutation 路线（将 permute 前置、融合 group send/recv、释放中间张量）所带来的通信开销削减与显存节省。

3) **链路作用**：作为论文 MoE 训练栈的通信层基准证据，Table 7 与 Fig.7 共同支撑"Megatron-Core 通过 HybridEP + 内存高效排列实现大规模 EP 可扩展训练"的核心论点，是实验评估章节的关键性能锚点。

### Table 8 (p.49) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab08.png]]
> [!quote] caption
> Summary of the impact from reduced-precision training on the Three

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表8 图文联合解读：**

表8以"三堵墙"为行、低精度训练收益为列，给出量化结论：**内存墙**——FP8/FP4分别降低激活50%/75%，消除BF16权重副本并保留BF16优化器状态（§4.1.3 / 5.3.5 / 4.1.6）；**通信墙**——参数AllGather量减半（§5.3.5）；**计算墙**——Tensor Core GEMM加速，但伴随量化kernel额外开销（§4.3.5 / 4.3.2）。

论文借此论证：低精度训练并非单一优化，而是**同时**撬动内存、通信、计算三维的"全栈杠杆"，是MoE规模化突破显存与带宽瓶颈的核心使能技术。

该表与第4–5章各节实现细节形成"结论—落地"映射，作为Megatron-Core方法完备性的横截面总结，凸显"精度压缩+系统优化"协同设计的整体逻辑。

### Table 9 (p.58) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab09.png]]
> [!quote] caption
> SDPA performance in cuDNN for DeepSeek-V3.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表9图文联合解读：**

表9对比Hopper与Blackwell两代GPU平台下DeepSeek-V3 SDPA算子在cuDNN中的前/反向TFLOPS，覆盖序列长度4096与16384。数据上Blackwell实现压倒性领先：序列4096时前向1324 vs 553 TFLOPS（≈2.4×）、反向1083 vs 422（≈2.57×）；序列16384时前向1698 vs 638 TFLOPS（≈2.66×）、反向1298 vs 523（≈2.48×）；且两平台均呈现"长序列TFLOPS更高"的特征，反向约为前向的76–82%。

该表用于论证新一代Blackwell架构对注意力计算的核心加速能力，量化其在DeepSeek-V3这一MoE超大模型训练中的硬件红利，支撑论文在新一代平台上开展大规模MoE训练的方法选择与性能预期。

### Table 10 (p.66) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab10.png]]
> [!quote] caption
> Layer distribution for DeepSeek-V3 with flexible asymmetric VPP (PP = 16 , VPP = 2 ).

> [!tip] 表格解读（多模态）
> 【图文联合解读】所引 Figure 10 卸载/重计算段落与 Table 10 不匹配；以下按表下正文解读。表展示 DeepSeek‑V3 在 PP=16、VPP=2 时的非对称布局：16 个 PP rank；rank 0 为 embedding＋3 decoder／2 decoder，rank 1–13 各 2／2 decoder，rank 14 为 2 decoder／MTP，rank 15 为 2 decoder／loss，共 61 个 decoder。说明灵活 VPP 可摆脱层数整除及首尾模块限制，通过细粒度分层实现负载均衡；该表为虚拟流水并行提供配置实例，连接模型结构与大规模 MoE 训练，并非性能实验。

### Table 11 (p.69) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab11.png]]
> [!quote] caption
> Unified throughput benchmarks (per-GPU figures) for two mixture-of-experts models on NVIDIA GB300, GB200, and H100. All configurations use force-balanced routing. The Dtype column specifies the FP8

> [!tip] 表格解读（多模态）
> 【图文联合解读】**注意**：用户提供的引用段落实际是关于"Figure 11 分片策略对比（FSDP2 vs Megatron-FSDP）"的描述，与图中所示的 Table 11 吞吐基准表不匹配。以下解读严格依据图中表格内容：

---

**Table 11 图文联合解读**

该表在统一 SeqLen=4096、force-balanced 路由下，对比 DeepSeek-V3 与 Qwen3-235B 两款 MoE 在 GB300 / GB200 / H100 三代硬件上的单卡吞吐（TFLOPs/GPU、Tokens/s/GPU）。量化结果：DeepSeek-V3 在 GB300/256 卡 MXFP8 下达到 1233 TF 与 4730 tokens/s，较同规模 GB200 BF16（857 TF / 3298 tokens/s）提速约 **44%**；GB200 MXFP8 为 1048 TF，H100（1024 卡 FP8-BLK）仅 368 TF。Qwen3-235B 趋势一致：GB300 MXFP8 974 TF vs GB200 BF16 750 TF（**+30%**）。长序列 131072 下吞吐骤降至 1556 tokens/s。

**技术结论**：Blackwell 架构 + MXFP8 相对 Hopper / BF16 带来显著代际收益（约 1.3–1.4×），H100 性能约为 Blackwell 的 30%，长序列受注意力成本制约吞吐。

**论文作用**：作为统一基准，支撑 Megatron-Core 在多代际 NVIDIA 硬件上规模化训练 MoE 模型的核心方法主张。

### Table 12 (p.70) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab12.png]]
> [!quote] caption
> Impact of parallelism strategies on memory and communication. d = parallelism degree. †Requires distributed optimizer (--use-distributed-optimizer).

> [!tip] 表格解读（多模态）
> 【图文联合解读】1. 表12以并行度d量化TP、EP、PP、CP、DP：TP激活（配SP）、权重、状态均为1/d；EP激活约1且受负载影响，MoE权重/状态1/d；PP基础激活1（VPP时>1），权重/状态1/d；CP仅激活1/d；DP仅在分布式优化器下状态1/d。  
2. 各策略单层通信依次为高、中、中、中、低；TP/PP/EP切分参数，CP不减权重，DP通信最低。  
3. 表为MoE训练的显存—通信权衡及混合并行选型提供依据，连接算法、显存优化与扩展性能实验。

### Table 13 (p.72) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab13.png]]
> [!quote] caption
> Memory bottleneck solutions.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 13 图文联合解读**

1）**核心对象与结构**：图示为论文 Table 13 的局部可见内容，仅呈现"Memory Bottleneck (Memory Wall)"这一行的三字段条目——**类别名、Symptom（症状）、Solutions（解决方案）**。症状列具体描述为：被迫使用全重计算（full recomputation）或过大的并行度以避免 OOM 显存溢出；解决列为：应用 Table 13 所列的显存节省技术以降低显存占用。

2）**论证的关键技术结论**：作者将显存瓶颈归纳为一种可枚举的故障模式（Memory Wall），其根因是激活/参数驻留显存超限；通过引入系统化的显存节省技术（如选择性重计算、参数分片、混合精度等），可在**不显著牺牲计算效率**的前提下缓解 OOM，替代"粗放式"地堆叠并行度或全量重算。

3）**在论文链路中的作用**：Table 13 位于方法诊断篇，作为 **MoE 训练中四大瓶颈（显存、通信、计算、扩展性）的问题–对策速查表**之一，与正文各章节的优化方案（如选择性重计算、all-to-all 调度、并行策略搜索）一一对应，为读者按症状选择对应优化提供导航。

### Table 14 (p.72) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab14.png]]
> [!quote] caption
> Communication bottleneck solutions.

> [!tip] 表格解读（多模态）
> 【图文联合解读】# Table 14 图文联合解读

**说明**：图片仅清晰显示表格的标题（"Table 14: Communication bottleneck solutions"）及前后语境文字，表格主体的行列内容未能完整呈现，以下结合可见信息与原文上下文进行解读。

## 1) 核心对象与结构

根据可见内容，Table 14 围绕**通信瓶颈（Communication Wall）**展开，结构上呈现"症状—解决方案"的映射关系：
- **症状（Symptom）**：Profiling 显示 collective operations 占用大量时间；
- **解决方案（Solutions）**：定位瓶颈通信类型并施加对应优化（如行内引用 "(Table 14)" 所指）。

## 2) 原文论证的关键结论

该表将 MoE 训练中的通信瓶颈分类化、可操作化：它把"通信成为 wall"的现象与具体优化手段一一对应，避免了笼统优化。结合 Figure 14 中 HybridEP dispatch kernel 的 RDMA 跨节点 + 节点内转发设计，论文意在说明：MoE all-to-all / dispatch 的通信热点需通过**端到端定制内核**（HybridEP）按通信模式精准解决，而非套用通用集合通信原语。

## 3) 在整体方法链路中的作用

Table 14 是论文"性能诊断→优化映射"工具链的**速查表**，位于系统优化章节末尾的实践指南位置，配合 HybridEP、内核融合、并行策略等内容，为读者在部署 MoE 大模型训练时提供**自检—归因—施治**的闭环参考，支撑论文"可扩展 MoE 训练"这一核心贡献的工程落地。

### Table 15 (p.73) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab15.png]]
> [!quote] caption
> CPU overhead bottleneck solutions.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 15 图文联合解读：**

该表为"问题—对策"两行结构。**Symptom**：Nsight Systems 时间轴显示 GPU kernel 间出现空隙，CPU 发起 kernel 速度跟不上。**Solutions**：通过减少 host 端 kernel 启动次数并启用 CUDA Graphs 来降低 CPU 开销。

论文借此论证：MoE 训练扩展时，单步 kernel 数量激增，CPU 调度成为关键瓶颈，导致 GPU 出现空泡。该表作为性能瓶颈诊断清单的一节，配合 Figure 14/15 等 profiling 视图，主张借助 CUDA Graphs 等技术消除 host overhead，否则大量小 kernel 将抵消 GPU 算力。它是论文优化章节"识别瓶颈→给出方案"链路的标准条目，体现 Megatron-Core 在大规模 MoE 端到端调优中的工程完备性。

### Table 16 (p.73) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab16.png]]
> [!quote] caption
> Computation bottleneck solutions.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**注：图片仅显示了表格的引导文字（Symptom / Solutions 段落及表题），未呈现表格主体内容（具体的 kernel 优化手段清单），故主要依据原文及上下文进行解读。**

表格 16 聚焦 **"计算瓶颈"（Computation Bottleneck）**，对应症状为：无通信或 CPU 瓶颈的前提下，GPU SM 利用率仍偏低。其核心结构列出三类内核级优化手段：①**Batching**——合并小 kernel，降低调度/访存开销；②**Fusion**——算子融合，消除中间张量读写；③**Lower precision**——降低数值精度以缩减计算量与带宽占用。原文借此论证：在通信与 CPU 瓶颈已被排除后，低效 kernel 本身仍会拉低吞吐，必须从内核层面系统补齐短板。该表与论文中针对通信、CPU、调度等其他瓶颈的方案表并列，共同构成 **Megatron-Core 全栈性能调优链路**，支撑 MoE 在高密度 Expert 并行下的可扩展训练。

### Table 17 (p.74) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab17.png]]
> [!quote] caption
> DeepSeek-V3 final optimized configurations on GB200 and H100. † Parallel Folding is used; TP

> [!tip] 表格解读（多模态）
> 【图文联合解读】表 17 对比 DeepSeek-V3 在 GB200（256 卡）与 H100（1024 卡）的最终优化配置：TP/PP/EP 分别 1/4/64 与 2/8/64（均 VPP=4，EP=64），GBS/MBS/SeqLen 同为 8192/1/4096；精度 MXFP8 对 FP8-Blockwise，Dispatcher 用 HybridEP 与 DeepEP；Recompute 范围、CUDA Graphs、EP all-to-all Overlap 按硬件特性差异化；最终性能 1048 vs 368 TFLOPS/GPU。

论文论证：MoE 大模型训练无"统一最优配方"，需按硬件定制——GB200 借 CUDA Graphs+MXFP8 即高效，H100 则需更激进 Recompute 与 EP 通信掩盖。作为端到端案例，它验证 Megatron-Core 对前沿 MoE 模型与异构硬件的灵活适配能力，是论文"可扩展 MoE 训练"主张的关键实证。

### Table 18 (p.74) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab18.png]]
> [!quote] caption
> DeepSeek-V3 optimization summary by platform.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **表格核心内容**：Table 18 按"Category × 平台（GB200 / H100）"两列组织，汇总 DeepSeek-V3 在两大硬件平台上的优化项。可见行"Parallelism"显示 GB200 与 H100 两栏**完全一致**，均采用 *Parallel Folding* 与 *Flexible VPP* 两种并行策略（其余行在截图中不可见）。

2) **论证的关键结论**：两平台在并行维度上**优化配置对齐**，表明 Megatron-Core 所提的 Parallel Folding（计算/通信折叠）与 Flexible VPP（弹性虚拟流水线）属于**跨硬件可移植的通用机制**，并非某一 GPU 专属技巧，验证了方法的可复现性。

3) **在论文中的作用**：该表置于 DeepSeek-V3 端到端 case study 末尾，**作为平台无关性的实证证据**——将前文抽象的 MoE 优化技术（EP overlap、Parallel Folding、Flexible VPP 等）落地到具体 GPU，串联起"通用框架 → 真实大模型训练"的实验链路，强化"Megatron-Core 方案具备规模化、工程化部署能力"的核心论点。

（注：截图仅可见 Parallelism 一行，其余优化项如 Communication、Memory 等分类未能呈现，已据原文推测框架。）

### Table 19 (p.86) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab19.png]]
> [!quote] caption
> Notation and abbreviations used throughout this report.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 19 图文联合解读**

该表为全报告符号/缩写索引，分6类共约25项：①**模型参数**E专家数、K top-k路由(K≤E)、h隐维、Nactive∝K(激活)、Ntotal∝E(总参)；②**训练维度**T每GPU token、B批大小、s序列长、L MoE层数；③**并行维度**：TP/PP/CP/DP通用 + MoE专属EP/ETP/EDP及调度VPP；④**批配**MBS/GBS/GA；⑤**精度**BF16/FP8-BLK(Hopper)/MXFP8(Blackwell)；⑥**度量缩写**MFU/GEMM/SDPA/MLA/MTP。

**技术结论**：以 Nactive∝K、Ntotal∝E 定量刻画MoE稀疏激活；引入EP/ETP/EDP等MoE专属并行维度，体现MoE相比稠密模型的并行扩展性。

**论文作用**：作为统一术语索引，支撑后续scaling law公式、并行策略以及Fig.19所示all-to-all与interleaved PP重叠调度的图表解读。

### Table 20 (p.87) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab20.png]]
> [!quote] caption
> Parallelism and training configuration details for benchmark entries reported in Table 11 .

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 20 列示 DeepSeek-V3 与 Qwen3-235B 两类 MoE 模型在 GB300/GB200/H100 上的训练配置：GPU 数、序列长度（4k 与 128k）、精度格式（MXFP8/BF16/FP8-BLK）、实测算力（TF），以及 TP/PP/CP/EP/VPP/MBS/GBS 超参。关键数据：DeepSeek-V3 在 GB300/256 GPU/MXFP8 下达 1233 TF，较同硬件 BF16（857 TF）提升约 1.44 倍；Qwen3-235B 在 128k 序列、GB300 下仍获 1150 TF；同硬件下 MXFP8 较 BF16 普遍提速 1.22–1.23 倍。

原文论证：(1) Megatron Core 在异构硬件上均实现 SOTA 吞吐；(2) MXFP8 较 BF16/FP8-BLK 带来显著算力增益；(3) 即使 EP64 大规模专家并行与长序列下仍保持高利用率。

作用：作为 Table 11 性能条目的可复现配置补充，贯通"硬件—精度—并行策略—吞吐"实验链路，支撑"可扩展 MoE 训练"核心结论。

## 关键公式（原文截图，无 LaTeX 源 — 引用前请核对图片）

### 公式截图 (p.64)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-eq01.png]]
> 原文文本线索：`output(x) = 𝑊↑·`

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.9 `(𝑝𝑖= 𝜎(𝑙𝑖)/ ∑︀`
- p.16 `World Size = TP × CP × PP × DP,`
- p.16 `at minimum. Since EP ⊆DP, requesting EP=8 forces DP ≥8. Combined with CP=8 for long sequences, the`
- p.17 `• Traditional: EP ≤DP = 8, so maximum EP is 8.`
- p.42 `results in 𝐿×𝑀×2 graphs in total (where 𝐿= layers per GPU, 𝑀= microbatches, ×2 for forward/backward).`
- p.64 `output(x) = 𝑊↑·`

## 相关论文

- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey
- [[muon-is-scalable-for-llm-training]] — Muon is Scalable for LLM Training
- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[zero-memory-optimizations-toward-training-trillion-parameter-models]] — ZeRO: Memory Optimizations Toward Training Trillion Parameter Models
- [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] — GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints

## 技术点深读（DEEP）

![[deep/scalable-training-of-mixture-of-experts-models-with-megatron-core]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/scalable-training-of-mixture-of-experts-models-with-megatron-core.txt`（264084 字符）供引用检索。