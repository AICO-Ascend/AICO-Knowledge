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
> 【图文联合解读】**图1联合解读**

图示MoE层前向四阶段数据流：输入`[B×S, H]`经TopK Router（门控线性层→Softmax/Sigmoid打分→Top-K选择含负载均衡）输出路由图与概率；Token Dispatcher按专家重排并All-to-All分发至各GPU；Expert Computation对E个专家执行Grouped GEMM并行计算；Token Combiner通过All-to-All回收、Unpermute还原顺序后按路由概率加权合并；Shared Expert MLP以旁路跳过路由直接汇入融合，最终输出`[B×S, H]`。

**论证结论**：通过显式拆分Route–Dispatch–Compute–Combine四步，揭示MoE计算中通信（两次All-to-All）与计算（Grouped GEMM）的解耦边界，为量化通信开销与设计重叠优化提供模型基础。

**章节作用**：作为方法篇总览图，统一定义后续并行策略、张量/专家并行调度、Token-dropping及细粒度通信优化等章节所引用MoE计算图的术语体系与执行顺序。

### Figure 2 (p.10) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig02.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p10.png]]*
> [!quote] caption
> Router architecture: linear projection, score function, top-𝑘selection, and load balancing. combine_postprocess (backward).

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示 **Megatron Core MoE TopKRouter** 四阶段流程：

1. **门控层**线性投影 $W_r\in\mathbb{R}^{H\times E}$，由 $l=W_r^T x$ 得 logits $[B\times S, E]$；
2. **评分函数**支持标准 Softmax 与 Sigmoid 两形式；
3. **Top-k 选择**自 $E$ 个专家中选 $k$ 个，输出每 token 概率与布尔**路由映射** $[B\times S, E]$；
4. **负载均衡**：作用于 logits 的 z-loss/Sinkhorn、无辅助损失的**专家偏置**，以及作用于路由映射的 micro-batch/sequence/global 三粒度 aux_loss。

原文借此论证 MoE 路由的模块化设计；该图为后续 Table 2 对比注意力层与 MoE 层并行需求差异、实现可扩展 MoE 训练奠定结构基础。

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
> 【图文联合解读】**图文联合解读：**

图示 EP=4、8 个专家（每 GPU 2 个）的 MoE 专家并行流程：序列 [T0…Tn] 经 Router 决策后，通过 All-to-All Dispatch 将 token 分发至 GPU0–3 上的对应专家（E0–E7）并行计算，再经 All-to-All Combine 聚合，保持 token 顺序输出。

**技术结论：** 论证 Megatron-Core 专家并行的核心机制——通过两次 all-to-all 通信实现"按专家分片、跨 GPU 调度"，使每 GPU 仅持有部分专家，显存随 EP 度扩展而摊薄。

**论文作用：** 作为方法链路基础图，支撑后续 Table 3 的 DeepSeek-V3 配置与 Table 4 的重计算显存分析，是 EP 通信模式与专家分片策略的标准可视化说明。

### Figure 5 (p.17) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig05.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p17.png]]*
> [!quote] caption
> Parallelism mappings: traditional constraints vs. MoE Parallel Folding decoupling.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图示 Attention（上）与 MoE 层（下）在 4 Rank 上的三种并行映射**：
① DP4→EP4：每 rank 独占 1 个 expert（E1/E2/E3/E4 互斥分布）；
② TP2-DP2→ETP2-EP2：attention 切 1/2，专家按 E1/E2 与 E3/E4 分组跨 rank——属传统强耦合（绿色虚线强制约束 attention 并行维度与 expert 维度同构）；
③ TP2-CP2→ETP2-EP1：启用 MoE Parallel Folding，attention 引入 CP2，每 rank 折叠持有全部 4 个 expert 的 1/2（ETP2-EP1）。

**关键结论**：解耦 attention 并行（DP/TP/CP）与 MoE 专家并行（ETP/EP），使后者可独立取 EP1 折叠全 expert，从而削减跨 rank 通信、降低激活显存并提升 token throughput。

**作用**：奠定 Table 5 "细粒度激活 offloading" 实验所依赖的灵活并行拓扑基础，证明 MoE 训练可摆脱"attention-必须-决定-expert 分布"的传统限制。

### Figure 6 (p.18) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig06.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p18.png]]*
> [!quote] caption
> Parallel Folding: decoupled attention and MoE parallelism mappings.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示将 Attention 层的 TP=8 单一组（GPU0–GPU7，8 路 TP AllReduce，A2A Scope=8 卡）按 fold_factor=4（=TP/ETP=8/2）折叠为 MoE 层的 ETP=2 × EP=4 网格：每 2 卡纵向配对（GPU0↔GPU1 等）做 ETP=2 的 Expert TP（Expert TP AllReduce），4 对横向构成 EP=4 的 4 路 EP A2A 通信（A2A Scope 缩至 4 EP rank）。

**关键结论：** 解耦 Attention 与 MoE 并行映射，使二者通信域独立——Attention 维持 8 路张量并行通信，MoE 专家通信仅需 4 路 A2A，显著降低跨域 AllReduce 频率与开销。

**论文作用：** 作为 Megatron-Core MoE 可扩展训练的核心机制，Parallel Folding 在同一 8 卡集群上灵活切换并行策略，为后续 MEFS 优化、跨域通信隐藏及大规模 MoE 性能评估奠定方法基础。

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
> 【图文联合解读】**图8联合解读：**

**1) 核心对象与结构**：图示 DeepSeek-V3 单层 Transformer 的选择重计算策略。上半部为 MLA（LayNorm→Down_proj→Up_proj+RoPE→Core-attn→Proj Linear→bias-drop-add），下半部为 DeepSeekMoE（LayerNorm→路由专家：fp32 Router→Token Dispatcher→Grouped FC1→Swiglu→Grouped FC2→Token Combiner，共享专家：FC1→Swiglu→FC2）。色标区分 6 类模块：紫 core_attn（fused_attn 不需重算）、粉 moe_act、绿 layernorm、蓝 mla_up_proj、黄 dispatch 均标记为 "output-discarding"（不存输出，重算时重生成），红/橙虚线框标注 moe 与 shared_experts 整块重算区域，并备注 dense mlp 重算未在图中绘出。

**2) 关键技术结论**：原文论证——该策略对显存占用大但计算便宜的部分做丢弃输出、依赖重算的细粒度选择；具体到 DeepSeek-V3，对 MLA 的 up_proj、attention 输入、MoE 的 router/dispatch/Swiglu/FC1 均丢弃输出（重算而非缓存），从而以最小额外算力换显著显存节省。

**3) 论文整体作用**：作为 MoE 大模型训练内存优化链路的关键一环，与混合精度（表8）、并行策略协同，使 MoE 训练在万亿参数规模下内存可控，支撑后文吞吐/显存实验论证。

### Figure 9 (p.24) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig09.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p24.png]]*
> [!quote] caption
> Fine-grained activation offloading: stream overlap for forward and backward passes.

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图展示双流时间线：上为 **Compute Stream**（Forward FC1→FC2→Backward FC2→FC1），下为 **D2H Stream**（前向阶段 Offload to CPU、后向阶段 Prefetch from CPU）。FC2 计算时段与传输时段形成"Overlap"和"Latency hidden"两块浅绿区域，证明 D2H/H2D 传输与 FC2 计算在时间上完全重叠。

原文据此论证**细粒度激活卸载**可将设备-主机数据传输延迟隐藏于 FC2 计算之后，使 offload/prefetch 不引入额外端到端耗时。该图是 Megatron-Core 降低激活显存占用、支撑大规模 MoE 训练的关键机制示意图，量化说明了"以算换存"策略的零额外开销特性。

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
> 【图文联合解读】**图文联合解读（Figure 11）**

1) **核心对象与结构**：图示对比两种分片策略。(a) FSDP2：3个Linear层各自被均匀切成Rank0/Rank1两段，形成(Shard, Param)-Shaped Collective Buffer，两台Device各持有3个DTensor（每层一块）；(b) Megatron-FSDP：把3个Linear展平为单一Per-Module Collective Buffer，按DP-Shard Size做非均匀切片，每Device仅持有与buffer切片对齐的少量DTensor（通常对应若干完整层）。

2) **关键结论**：Megatron-FSDP将分片边界对齐到通信buffer，使每设备D tensor更少、all-gather通信次数更少，从而优于FSDP2的逐参数均匀切分。

3) **论文作用**：作为方法论论据，支撑Megatron-FSDP优于原生FSDP2的设计主张，为后续Table 11在GB300/GB200/H100上的MoE吞吐基准提供动机。

### Figure 12 (p.28) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig12.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p28.png]]*
> [!quote] caption
> Persistent double-buffer design: two pre-allocated buffers are cycled across FSDP collectives, eliminating allocation overhead and enabling NCCL User Buffer Registration.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**核心对象与结构：** 图示展示 FSDP 反向传播中持久双缓冲（double-buffer）流水线。顶部两个 `CUDACachingAllocator`（`torch.empty`）分别预分配粉色与蓝色 4 块缓冲区，经绿色箭头下放至底部形成两套"Pre-allocated buffer"（含循环箭头表示复用）。流程：Param shard → AllGather → 粉色 buffer → Transformer layer BWD → 蓝色 buffer → Reduce Scatter → Gradient shard，两组 buffer 交替跨 FSDP 集合通信复用。

**技术结论：** 原文借此论证通过预分配+循环复用双 buffer，可彻底消除每次 AllGather/Reduce-Scatter 的临时内存申请开销，并满足 NCCL User Buffer Registration（UBR）的固定地址注册要求，从而将通信与计算 overlap 最大化。

**链路作用：** 属于论文系统级 FSDP 优化章节，与 Table 12 并行策略内存/通信分析互为佐证，为 MoE+Transformer 大规模训练提供低开销通信基础设施。

### Figure 13 (p.30) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig13.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p30.png]]*
> [!quote] caption
> Expert parallelism across 4 GPUs with 4 experts.

> [!tip] 技术解读（多模态）
> 【图文联合解读】【结构】图示4 GPU×4 Expert的Expert Parallelism架构：每卡含Attention Layer和Router，产2 token（共8个a1-a8）；Router本地决策→Dispatch(EP group)以all-to-all按expert归属分发，每卡持1 Expert独立计算→输出f1-f8→Combine(EP group)再all-to-all回传原卡。负载显著不均：蓝色Expert收3条(a1/a5/a8)，黄色仅1条(a3)。

【结论】EP将每层E个expert的参数/显存分摊到各GPU（此处4卡各存1/4），破解MoE显存瓶颈（直接呼应Table 13的Memory bottleneck solutions）；代价是EP group内两次all-to-all通信开销，且暴露expert间负载不均问题。

【作用】作为EP执行流程的可视化模板，与Table 13显存优化方案互为图/表对照，为后续Scaler/Transformer Engine等组件引入及大规模扩展性/性能实验提供架构基线。

### Figure 14 (p.31) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig14.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p31.png]]*
> [!quote] caption
> The dispatch kernel design of HybridEP.

> [!tip] 技术解读（多模态）
> 【图文联合解读】HybridEP调度内核呈现双路径融合结构：①节点内走"Global Memory ⇒ SM warp group → SMEM Cyclic FIFO → SM ⇒ Global Memory"流水线；②节点间经RDMA warp group直发。三类数据（Token、Prob、Scaling factor）并行贯穿两条通道。图原论证：HybridEP把节点内NVLink与节点间RDMA合并到单一调度内核，借SMEM Cyclic FIFO作片上环形缓冲，省去主机往返。该图支撑Table 14所述通信瓶颈解法，是实现跨节点MoE可扩展训练的核心通信原语。

### Figure 15 (p.31) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig15.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p31.png]]*
> [!quote] caption
> The combine kernel design of HybridEP.

> [!tip] 技术解读（多模态）
> 【图文联合解读】1）结构：图中是 HybridEP combine 的本地/跨节点 Token、Prob 流水：Global Memory→SM 后进入 Intra-node/Inter-node warp group；每段含 1 个 Reduce warp group、2 个 SMEM Cyclic FIFO，跨节点经 RDMA 传递 Token/Prob，并连接相同 rank id。  
2）结论：核函数按节点内/节点间分工，以片上 FIFO 衔接，仅传输 token/prob，减少同步与通信开销。  
3）作用：它是 MoE token 聚合、通信实现与性能/扩展性评估之间的原理图。

### Figure 16 (p.32) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig16.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p32.png]]*
> [!quote] caption
> Merged FWD-FWD Timeline with all-to-all Overlapping.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图示内容**：横轴为时间，两行分别为Even（ubatch 0/2/4）与Odd（ubatch 1/3/5）微批次；每段顶部标"Merged"，由绿色FWD块与灰色BWD块组成，相邻偶奇ubatch的前向计算合并为统一的FWD-FWD窗口，BWD紧随其合并执行。

**关键结论**：通过将两个连续微批次的前向阶段合并，使MoE all-to-all通信与计算相互重叠，从而隐藏通信开销，解决流水线中all-to-all带来的bubble问题。

**论文作用**：作为Table 16"Computation bottleneck solutions"中与GroupedGEMM、early-reduce等并列的方案支撑图，证明通信—计算重叠策略在大规模MoE训练中可有效消除瓶颈。

### Figure 17 (p.33) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig17.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p33.png]]*
> [!quote] caption
> Merged FWD-BWD Timeline with all-to-all Overlapping.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图17联合解读**

1）**结构与对象**：横轴为训练时间流，纵向分两行（u-Batch-Even与u-Batch-Odd），共呈现6个ubatch（0–5）交错排列，每段由绿色FWD块与灰色BWD块组成；中间4段标注"Merged"，仅首段ubatch 0的FWD与末段ubatch 5的BWD标红"Not Merged"。

2）**关键结论**：图中展示FWD-BWD合并重叠调度——后一ubatch的FWD与前一ubatch的BWD并行执行，使MoE层中all-to-all通信被计算掩盖；首尾两次因无相邻阶段无法合并。

3）**论文作用**：作为Megatron-Core MoE的核心优化手段之一，通过跨ubatch流水化隐藏all-to-all延迟，是实现MoE大规模高效训练的调度基础。

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
> 【图文联合解读】**图文联合解读**

**1) 核心对象与结构**：图示 PP=4、VPP=3、GA=8 下的交错 1F1B 时间线。横轴为时间步，纵轴为 4 个 PP 阶段 ×3 个虚拟阶段（共 12 行），色块按 FWD/BWD 与 VIRTUAL_PIPE_0/1/2（黄/红/粉）区分，编号 1–8 表示 8 个 micro-batch。含 Warmup 段（填管线）和 Flush 段（排空）。

**2) 关键结论**：上图展示原调度，下图通过在 1F1B 起始前多执行一个 micro-batch，使相邻 micro-batch 的 fprop/bprop 无数据依赖（图下箭头标注），从而将 MoE 的 all-to-all 通信与 Dense 计算重叠执行，消减管线气泡。

**3) 在论文中的作用**：支撑 MoE 训练中"通信—计算重叠"的核心优化论点，是连接交错 PP 调度与 expert 并行效率分析的关键图表，为后续性能数据提供时序依据。

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
> 【图文联合解读】**图文联合解读**

**1) 核心对象与结构**
图示为路由器融合工作流：输入经 Gating Linear 产生 Logits 后，分裂为两条并行分支。蓝色上路径依次执行 Topk/Group Topk → Sigmoid/Softmax → Scale，封装为**蓝色 Fused Kernel**，输出 *Probs* 与 *Routing map*；绿色下路径执行 Topk → Sigmoid/Softmax，封装为**绿色 Fused Kernel**，输出 *Score for aux loss* 与 *Routing map for aux loss*；两者再汇入紫色 **Compute aux loss**（第二个 Fused Kernel），最终送往 Dispatch Preprocess，共三个融合内核。

**2) 关键结论**
MoE 辅助损失计算被融合进单一 kernel；上路径产生实际路由权重与分发映射，下路径仅生成供辅助损失使用的得分，二者共享 Gating Linear 输出但走独立分支，避免冗余访存与重复 Top-k 选取。

**3) 在论文中的作用**
作为 Figure 18 范式"减少 GEMM 之外的 kernel 数量"在路由阶段的实例化，支撑 Megatron Core 中 MoE 训练端到端 kernel fusion 优化链路，提升大规模 MoE 训练吞吐。

### Figure 22 (p.39) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig22.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p39.png]]*
> [!quote] caption
> Traditional execution (top) versus CUDA Graph execution (bottom).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图22 联合解读**

**核心对象与结构：** 图分上下两部分，均以时间轴（横轴 Time）为基准，纵向并列 CPU 与 GPU 两条 Timeline。上半"Traditional Execution"显示每轮迭代中 CPU 需交替执行 [Python & Framework] 与 [Launch K1/K2/K3]，每次 Launch 仅触发单个 Kernel（K1→K2→K3），Kernel 之间存在灰白色"GPU BUBBLES"间隙；下半"CUDA Graph Execution"显示 CPU 端仅需一次 Graph Launch（Single API call），GPU 端 K1–K5 五个 Kernel 紧密串联，标注"NO GPU BUBBLES"。

**关键技术结论：** 传统执行模式下 Python/框架调度开销导致 GPU 频繁空转（每两个 Kernel 出现一处气泡）；CUDA Graph 通过一次捕获后整图回放，消除逐 Kernel 的 CPU Launch 开销，使 Kernel 紧密 back-to-back 执行，GPU 利用率显著提升。

**在论文中的作用：** 该图为 Megatron-Core 引入 CUDA Graph 优化 MoE 训练流水线提供直观机理依据，是其性能优化章节的关键支撑图，与文中吞吐/加速比数据形成"机制—收益"对照。

### Figure 23 (p.39) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig23.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p39.png]]*
> [!quote] caption
> Full versus layer-wise CUDA Graphs in one training iteration (three layers, two microbatches).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**核心对象与结构**：
横轴展示一次训练迭代的执行序列，包含 2 个 microbatch × 3 个 layer 的前向（F₁₁–F₂₃）、反向（B₁₁–B₂₃）、损失 L 及优化器 Opti。两类 CUDA Graph 对比：
- **紫色虚线（Layer-wise CUDA Graphs）**：以"单层/单 microbatch"为粒度，逐小块独立 capture，需多张图拼接；
- **橙色虚线（Full CUDA Graphs）**：将整次迭代序列封装为一张大图，一次性 capture。

**关键技术结论**：
Full CUDA Graph 把全部前反向+优化器操作纳入单一图，消除了 layer-wise 方案在每个小块间的 kernel launch 开销与 CPU–GPU 同步停顿，从而获得更高吞吐与更稳定的执行时间。

**在论文中的作用**：
该图是性能优化章节中"Full CUDA Graphs 优于 Layer-wise"论点的核心可视化证据，支撑 Megatron Core 在 MoE 训练流水线中选用端到端整图 capture 的方案。

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
> 【图文联合解读】**图文联合解读：**

1) **核心对象与数据**：图为Nsight Systems对Transformer层前向的时间轴剖面，自上而下分为attention、shared experts、router、preprocess、dispatch、routed experts、combine七阶段。上半部分无CUDA Graph，attention区间（≈98.5–104ms）含约十余次独立kernel（LayerNorm、Q/K/V proj、RoPE、attn、Proj…），kernel间存在明显CPU launch间隙；下半部分启用partial CUDA Graph后，attention整段被包裹在单一绿色"cudaGraph"块内（≈98–100.5ms），耗时由约6ms压缩至约2.5ms，节省≈50%。

2) **关键技术结论**：attention作为形状/计算图静态的子模块，其CPU调度开销可被CUDA Graph彻底消除；router/dispatch/combine（含AllToAll）仍为动态，需在Graph外执行。

3) **作用**：为论文"partial CUDA Graphs"策略提供实测证据，支撑MoE训练中静态段图捕获、动态段保留的低开销优化方案。

### Figure 26 (p.42) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig26.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p42.png]]*
> [!quote] caption
> Why Pipeline Parallelism prevents CUDA Graphs from being shared across microbatches. With PP (top): Execution is interleaved—multiple forward passes run before any backward pass. If microbatches share a graph, F_mb1 overwrites saved context of F_mb0 before B_mb0 uses it, causing memory corruption. Each microbatch needs its own graph (𝐿× 𝑀× 2 graphs total). Without PP (bottom): Execution is sequent

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图分上下两栏对比：上栏（带 PP，流水线并行）时间轴上 F_mb0→F_mb1→…→B_mb0→…→B_mb1 交错执行，F_mb(i+1) 先于 B_mb(i) 完成，红色叉号标注"不可跨 microbatch 共享图"，共需 L×M×2 张图；下栏（无 PP，顺序执行）严格 F→B→F→B 交替，绿色勾标注"F_mb(i+1) 在 B_mb(i) 之后执行，可共享"，仅需 L×2 张图。

**技术结论：** PP 模式下交错调度使前向保存的张量/上下文被后续前向覆盖，反向时引发显存损坏，故每个 microbatch 必须独立捕获 CUDA Graph，使图数量随 M 线性放大。

**论文作用：** 为 MoE 训练中 CUDA Graph 实现的显存开销分析提供量化依据（L×M×2 vs L×2），论证大规模 PP 场景下图管理的扩展性挑战，是方案设计的关键约束。

### Figure 27 (p.45) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig27.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p45.png]]*
> [!quote] caption
> ECHO workflow for forward and backward passes. The planner generates routing and hot expert maps. Expert Dispatch clones hot expert weights to spare slots; Expert Gradient Dispatch reduces gradients back to home experts.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图示内容（量化）：** 图示 ECHO 前/反向计算流。前向（红色标题）：Planner 据 hidden states 同时输出 routing map（送 Token Dispatch）与 hot expert map（送 Expert Dispatch），随后经 Token Dispatch→Expert FC1→MoE act→Expert FC2→Token Combine，两级 Expert Dispatch 将热专家权重克隆至空闲槽；反向：Combine backward→FC2 dgrad/wgrad→MoE act backward→FC1 dgrad/wgrad→Dispatch Backward，Expert Gradient Dispatch 将梯度归约回原专家。

**技术结论：** 论证 ECHO 通过规划器驱动的动态克隆+空闲槽复用，实现不丢 token 的负载均衡 MoE 训练。

**论文作用：** 作为 ECHO（论文核心贡献）相对 drop-and-pad 基线的可扩展 MoE 训练完整工作流图示佐证。

### Figure 28 (p.46) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig28.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p46.png]]*
> [!quote] caption
> Memory layout comparison across three execution modes. Left: Eager mode allocates memory dynamically based on actual usage. Middle: Baseline static shape requires worst-case sized buffers for each layer independently, causing severe fragmentation when actual usage is lower. Right: Paged Stashing uses a single worst-case tmp buffer shared across layers for computation, while a paged stashing buffer

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示横轴对比三种执行模式（Eager / 静态Naïve worst buffer / 静态Paged stashing），纵轴为Layer 0/1/2下Exp 0/1/2的token（0–5）分配，深绿表实际占用、浅绿表分配缓冲。

**核心结构**：Layer 0仅Exp 2激活、Layer 2仅Exp 1/2激活，Naïve模式仍按worst-case为每层每专家预留满载缓冲，造成大量浅绿碎片；Paged Stashing采用跨层共享tmp缓冲+分页暂存未路由token，将浅绿区压缩为stashing buffer。

**论证结论**：Paged Stashing在保留静态shape编译效率的同时，规避了Eager动态分配碎片化和Naïve最坏预分配浪费，实现内存利用率最优。

**论文作用**：作为MoE显存优化的关键可视化证据，支撑"Paged Stashing"核心技术claim，与后续吞吐/显存实验数据形成机理与结果互证。

### Figure 29 (p.46) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig29.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p46.png]]*
> [!quote] caption
> Paged Stashing stream overlap. Forward pass: After Layer N computes, its activations are stashed (copied from tmp buffer to paged stashing buffer) on a dedicated Pack stream while Layer N+1 computes on the main Compute stream—the stash is completely overlapped. Backward pass: Activations for Layer N are pre-fetched (reloaded from stashing buffer to tmp buffer) on the Unpack stream before Layer N b

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图29以时间轴横向展示两条并行CUDA流：Compute流（绿色）依次执行Forward Layer N、N+1及反向Backward N+1、N；Stash流（灰色）执行tmp→stash缓冲的"Stash Layer N"与反向"Reload Layer N"。前向阶段Stash与Forward N+1完全重叠（Overlap），反向阶段Reload潜伏于Backward N+1之后被完全隐藏（Latency hidden）。

该图直观论证了**Paged Stashing通过双流DMA使激活搬运与计算全重叠、零额外开销**的关键结论。

在论文中，它是支撑MoE激活重计算/存储优化可行性的核心示意图，配合Figure 28构成"内存换显存、重叠隐藏延迟"的完整技术叙事链。

### Figure 30 (p.50) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig30.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p50.png]]*
> [!quote] caption
> FP8 training recipes: Per-Tensor Scaling, Blockwise FP8, and MXFP8. A reduced-precision training recipe consists of: • Data format. There are two types of FP8 format: E4M3 and E5M2 [71, 74]. Usually there are two combinations used in training: ∘E4M3: Inputs, weights, and gradients are all quantized in the E4M3 format. ∘Hybrid: Inputs and weights are quantized in E4M3, while gradients are quantized

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图30以三幅示意图横向对比FP8训练中三类量化缩放策略：左侧Per-Tensor整张张量共享一个缩放因子"S"，仅1 scale/tensor；中间Blockwise将张量划分为128×128块，每块独立缩放（约4块/S）；右侧MXFP8进一步细化为1×32元素为一组（36个小块各持一个S）。下方箭头从左到右标注"Coarse→Fine Granularity"与"Fewer→More Scales"，直观量化了三者的粒度差异。

原文据此论证：缩放粒度越细，量化刻度越密，数值溢出与精度损失风险越低，但缩放因子存储与计算开销越大。Per-Tensor实现最简却误差最大，Blockwise与MXFP8在保持FP8吞吐的同时显著提升训练稳定性。

在论文整体链路中，该图位于第50页低精度训练方法综述部分，为后文选择MXFP8/Blockwise FP8作为MoE大模型训练的默认数值格式提供了视觉化依据，并与Transformer Engine、DeepSeek的FP8路径衔接，构成"格式—缩放—精度—吞吐"权衡链的关键一环。

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
> 【图文联合解读】图(a)在0K–64K序列下展示三组件绝对FLOPs：SDPA（红）呈O(s²)于64K达32000+ TFLOPs，MoE（蓝）与剩余注意力（橙）为O(s)，同位置仅约10000和5000。图(b)4K–256K对数刻度显示占比演变：4K时MoE占59.4%主导，16K附近交叉于约40%，256K时SDPA升至约90%、MoE降至约6%。

该图量化论证：序列超16K后，SDPA的二次复杂度使其取代MoE成为计算主导。论文借此指明长上下文MoE训练的优化重心应从MoE通信转向SDPA，为后续序列并行与计算-通信重叠等优化策略提供量化依据。

### Figure 35 (p.59) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig35.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p59.png]]*
> [!quote] caption
> Communication and computation patterns of TP and two types of CP.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图35 图文联合解读**

**核心对象与结构**：表格对比TP与两种CP在Core Attention层的通信-计算模式。CP(P2P)：线性权重复制，SDPA前后以P2P传递sequence-sharded张量（环形通信）；CP(A2A)：线性权重复制，SDPA前后通过A2A在sequence-sharded与head-sharded布局间转换；TP：权重切分(paralleled)，单次SDPA处理head-sharded张量，无额外跨设备通信。

**关键技术结论**：CP保留完整线性权重（节省显存、可承载更长序列），代价是额外的集合通信开销；TP切分权重、通信最少但显存放大。与正文对照，该图量化了"P2P适合序列切分、A2A需配合head切分"的设计取舍。

**方法链路作用**：作为MoE长序列训练中TP×CP×EP并行组合选型的可视化决策依据，支撑后续关于通信开销与显存权衡的实验分析。

### Figure 36 (p.61) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig36.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p61.png]]*
> [!quote] caption
> Unpacked vs. Packed sequences.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图(a)展示5条长度不一的序列（橙、蓝、米黄、绿、紫）按原始长度堆叠，存在大量空白区域；图(b)将所有序列统一填充至最大长度，形成密实矩形块。原文借此论证**打包序列（packed sequences）策略**可消除padding冗余，使批次内token利用率接近100%，显著提升训练吞吐与GPU计算效率。该图是论文方法链路的基础铺垫——为后续MoE训练中变长序列的高效批处理、专家路由与token drop策略提供数据组织层面的前提。

### Figure 37 (p.61) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig37.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p61.png]]*
> [!quote] caption
> Compute imbalance in causal attention over packed sequences. are partitioned and which CP communication group is used by attention operators, without requiring any parameter redistribution or optimizer-state migration. Therefore, Dynamic-CP provides a practical form of dynamic parallelism for variable-length training with minimal framework overhead. Related work, including

> [!tip] 技术解读（多模态）
> 【图文联合解读】图像无法辨认，仅依据原文：当前页未显示 Fig.37 的可读图形或数据，底部为相关 Fig.38 示意。设 packed 序列含长度 \(n_i\) 的样本，因果注意力工作量约为 \(\sum_i n_i^2\)，长短悬殊会造成计算失衡。原文以此说明静态 CP 切分不适用于变长训练；Dynamic-CP 可按微批/序列选择 CP 组，长序列用 CP=2、短序列可各自用 CP=1，无需迁移参数或优化器状态。该图位于动机—方法论证链中，明确动态上下文并行的优化对象。

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
> 【图文联合解读】【对象】图分三栏对比 Megatron-Core MoE 三种负载均衡策略：(a) 辅助损失（梯度、可微、软均衡）经 Logits→分数函数→Top-k→Dispatch，附加 $L_{aux}=\alpha\cdot E[\sum f_i P_i]$；(b) Sinkhorn（指派、不可微、硬均衡）对 exp 矩阵迭代行列归一（no_grad）后 Top-k；(c) 无辅助损失偏置法（反馈、不可微、自适应）以 Logits+Expert Bias→Top-k→Dispatch→Token Counts 形成 $b_i\text{+=sgn}(avg-cnt_i)$ 闭环。

【结论】呈现从"梯度惩罚→组合优化→无梯度反馈"的演进路线，揭示可微软均衡与不可微硬均衡之间的权衡。

【作用】为论文 MoE 路由模块的方法选型与后续吞吐/质量对比实验提供统一基线。

### Figure 40 (p.65) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig40.png]]
*整页渲染: ![[assets/scalable-training-of-mixture-of-experts-models-with-megatron-core-p65.png]]*
> [!quote] caption
> Shared expert architecture in Megatron-Core MoE. The shared expert processes all tokens while routed experts process only their assigned tokens. When overlap is enabled, shared expert computation runs in parallel with the token dispatch/combine communication, hiding its latency. FLOP and per parameter. The architecture has been adopted by NVIDIA’s Nemotron-3 Super and Ultra models.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心结构（图中可量化信息）：** 图示展示了 Megatron-Core MoE 的双路径架构。输入为 8 个 token（T0–T7），经 Router 分流为两条并行支路：左路（绿色）为 Shared Expert，对全部 8 个 token 依次执行 FC1 与 FC2 计算；右路（橙色）为 Routed Experts，仅对每个专家的 Top-K token 依次执行 Token Dispatch → Routed Experts Compute → Token Combine。最终通过 Add 操作将两路输出逐 token 相加，输出同样为 8 个 token。两路之间存在两个 "Comp/Comm Overlap" 节点（蓝色），用虚线箭头连接 Shared Expert 计算与 Dispatch/Combine 通信。

**2) 关键技术结论：** Shared Expert 处理全量 token（计算量大但通信无关），Routed Experts 仅处理分配 token（需 All-to-All 通信）。通过 Comp/Comm Overlap，Shared Expert 的 FC1/FC2 计算可与 Token Dispatch/Combine 通信并发执行，隐藏其延迟，从而摊薄通信开销对整体吞吐的影响。

**3) 在论文中的作用：** 该图作为计算–通信重叠优化的可视化证据，支撑论文关于"通过结构与流水线优化提升 MoE 训练可扩展性"的核心方法论，并佐证其已被 NVIDIA Nemotron-3 Super/Ultra 模型采纳，体现工业落地价值。

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
> 【图文联合解读】**图文联合解读：**

1. **核心对象**：左侧为稠密 MLP（含 W1∈ℝ^{h×4h}、W2∈ℝ^{4h×h}），右侧为细粒度 MoE E2G2T2（4 专家、组大小 2、Top-2、中间维减半 2h）。MLP 权重沿中间维切片为 2h 后复制成 4 组（h×2h），路由器权重 Wg 由 2×h 复制为 4×h，配合 Top-K/Softmax 强制每组各选一名专家。

2. **关键结论**：通过"沿中间维切片+复制"与"路由器权重复制"的组合初始化策略，可保证 MoE 输出在起步阶段与稠密模型数学等价，避免性能回退。

3. **链路作用**：作为"granular upcycling"的核心可视化证据，衔接稠密预训练向细粒度 MoE 的转换流程，是论文实现低成本、可扩展 MoE 训练的关键技术支撑。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.11) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab01.png]]
> [!quote] caption
> MoE component to process group mapping.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表格内容解读：**

表格列出4类MoE组件的进程组映射及理由：①Router仅用tp/cp/tp_cp，因权重在EP各rank复制，无需专家并行切分；②Token Dispatcher用ep/tp_ep，承担专家rank间的all-to-all通信；③Experts采用ep+expt_tp+expt_dp三维切分，分别负责专家分片、专家内张量并行、梯度归约；④Shared Experts仅用tp，与稠密MLP一致。

**关键结论：**

MoE各子模块并行需求差异显著——Router可省去EP通信开销（仅复制权重即可），Experts则需独立的expt_dp以最小化跨节点梯度同步，体现Megatron-Core对每个组件做精细化映射以兼顾通信与计算效率。

**论文作用：**

支撑Figure 1"路由-分发-计算-合并"数据流中各阶段的并行实现，是论文证明"差异化进程组映射可实现MoE大规模可扩展训练"这一核心方法论的关键设计依据。

### Table 2 (p.15) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab02.png]]
> [!quote] caption
> Contrasting parallelism requirements of attention and MoE layers within a single Transformer block.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读（Table 2）：**

该表沿 Computation、TP、CP、EP 四维对比 Attention（稠密）与 MoE（稀疏）的并行需求。量化要点：①Attention 每 token 与全部 token 互注意，MoE 仅路由至 E 专家中 K 个；②Attention 大 QKV 矩阵受益高 TP，MoE 单专家维度小使高 TP 适得其反；③Attention 长序列需高 CP，MoE 无序列依赖致 CP 无效；④EP 对 Attention 不适用，却是 MoE 分发大量专家的关键。

**技术结论**：MoE 需"低 TP、零 CP、高 EP"的差异化并行策略，与稠密层截然不同。

**论文作用**：与 Figure 2 路由器模块化设计衔接，为 Megatron-Core 必须为 MoE 设计专用并行机制、实现可扩展训练提供结构基础与设计依据。

### Table 3 (p.20) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab03.png]]
> [!quote] caption
> Memory breakdown per GPU for DeepSeek-V3 with BF16 training (PP​4×VPP​4×EP​64, 256 GPUs).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表量化展示 DeepSeek-V3 BF16 训练（PP4×VPP4×EP64，256 GPU）下每 GPU 显存分配：权重复制区 36.4 GB（PP/EP/TP 切分）、主权重与优化器状态 32.1 GB（分布式优化器 + BF16 moments）、激活 131.0 GB（低精度 + 重计算 + Offloading），合计 199.5 GB。

关键结论：激活占总显存约 65.7%，是绝对显存主体，验证了"激活侧低精度、重计算、Offloading"对 MoE 大模型训练降本的核心价值。

论文作用：承接 Figure 3 的 MoE 参数/计算扩展论述，为 Table 4 的重计算显存分析提供基线配额，构成"EP 分片→重计算→激活优化"的完整方法链。

### Table 4 (p.23) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab04.png]]
> [!quote] caption
> Memory reduction per GPU from fine-grained recomputation for DeepSeek-V3 (PP​4×VPP​4×EP​64, 256 GPUs).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读**

该表量化了 DeepSeek-V3 在 PP4×VPP4×EP64、256 GPU 并行配置下，细粒度重计算对每 GPU 显存的节省量：**MLA Up-Projection 省 30.4 GB（≈71.7%）**，LayerNorm 省 8.2 GB，SwiGLU 激活函数省 3.8 GB，**合计 42.4 GB**。

**关键技术结论：** MLA 的上投影激活是显存压力的首要来源，应作为优先重计算点；细粒度（按算子级）选择重计算目标可显著释放激活内存，而非粗粒度整层重算。

**链路作用：** 与 Fig.4 所示 EP all-to-all 专家分片策略协同，论证在 MoE+EP 大规模并行下，重计算是显存预算可行的关键手段，为 DeepSeek-V3 级 MoE 训练提供了可量化的内存优化依据。

### Table 5 (p.25) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab05.png]]
> [!quote] caption
> Memory and throughput impact of fine-grained activation offloading.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 联合解读：**

表5对比两模型启用细粒度activation offloading的效果。**DeepSeek-V3**（TP1PP8EP32VPP4, MXFP8）：内存169→151 GB（−10.7%），吞吐945→930 TF/s（−1.6%），表明在已用VPP压缩场景下，offload以极小吞吐代价换取显著内存节省。**Qwen3-235B**：结合offload重配并行（TP2→TP1 + EP16→EP64），吞吐由800→920 TF/s（+15%），内存仅+1.7%，说明offload释放的显存可支撑更高EP并行度从而大幅提速。

**作用**：论文以此论证fine-grained activation offloading不仅是被动内存优化手段，更是MoE训练中实现配置灵活性（与MoE Parallel Folding互补）的关键支撑组件，使大模型在不同硬件约束下都能找到更优的吞吐-显存平衡点。

### Table 7 (p.32) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab07.png]]
> [!quote] caption
> EP Scaling Performance for HybridEP and all-to-all (in µs).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 7 图文联合解读**

**1) 核心对象**：表7给出 HybridEP 与 all-to-all 在 dispatch/combine 两类通信上的延迟（μs），横轴为 EP size∈{8,16,32,64}，纵轴为 GB200 与 H100 两平台。量化看，H100 EP=64 dispatch：HybridEP 4626 vs A2A 9164（≈2.0× 加速）；GB200 EP=64 dispatch：675 vs 930（≈1.4×）；combine 同趋势。所有 EP 下 HybridEP 均快于 A2A。

**2）关键结论**：HybridEP 在所有规模/平台上均优于纯 all-to-all，且优势随 EP 扩大而显著放大（尤其 H100，EP=8→64 时 A2A 从 1265 涨至 9164 μs，HybridEP 仅 661→4626 μs，扩展性更优）。

**3）作用**：为 HybridEP 作为 MoE 可扩展通信骨干的论断提供端到端通信开销实测证据，支撑论文在大规模 EP 训练场景下"通信可控、可扩展"的核心论点。

（注：所给引用段落实为 Figure 7 解读，与 Table 7 无直接关联，故以上仅依据表格内容。）

### Table 8 (p.49) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab08.png]]
> [!quote] caption
> Summary of the impact from reduced-precision training on the Three

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 8 归纳降精度训练对大模型训练"三大墙"的量化收益：①**Memory墙**：FP8/FP4 激活存储分别降低 50%/75%，消除 BF16 权重复本，优化器状态转 BF16（§4.1.3/5.3.5/4.1.6）；②**Communication墙**：AllGather 参数通信量减半（§5.3.5）；③**Compute墙**：Tensor Core GEMM 加速，但引入量化 kernel overhead（§4.3.5/4.3.2）。技术结论：降精度可同时击穿内存、通信与算力三堵墙，代价是 compute 端存在量化开销权衡。该表在论文方法链路中充当全局收益清单，将 4.x/5.x 各章节的优化按"墙"维度归并，为读者提供一站式视图，是论证万亿 MoE 可扩展训练可行性的关键技术拼图。

### Table 9 (p.58) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab09.png]]
> [!quote] caption
> SDPA performance in cuDNN for DeepSeek-V3.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 9 联合解读**

**核心数据**：表9量化对比了Hopper与Blackwell两代GPU在DeepSeek-V3上cuDNN SDPA的吞吐性能。序列长度为4096时，Hopper前向/反向分别为553、422 TFLOPS，Blackwell跃升至1324、1083；序列扩至16384后，Hopper达638/523，Blackwell达1698/1298 TFLOPS。

**关键技术结论**：Blackwell相对Hopper实现约2.4倍前向、2.5倍反向加速；且序列从4096延至16384，两平台吞吐均显著提升（如Blackwell前向+28%），表明长序列下注意力计算利用率更高。

**论文链路作用**：作为Megatron-Core在最新硬件上的性能基准实验，支撑论文关于"全栈协同优化（算法+并行+硬件）"的核心主张，证明cuDNN SDPA能充分释放Blackwell算力，是模型端到端训练效率论证的关键一环。

### Table 10 (p.66) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab10.png]]
> [!quote] caption
> Layer distribution for DeepSeek-V3 with flexible asymmetric VPP (PP = 16 , VPP = 2 ).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**注意：图片与题目不匹配。** 用户要求解读 Table 10（DeepSeek-V3 层级分布在 PP=16, VPP=2 下），但提供的图实际是 **Figure 10**（细粒度 offloading/recomputation 流图）。以下按图像实际内容解读：

**1) 图示核心结构**（可量化）：
- 左支为注意力路径：RMSNorm → QKV Linear → Core Attn → Attn Proj，旁挂 Shared Experts；
- 右支为 MoE 路径：RMSNorm → Dispatch → Expert FC1 → MoE Act → Expert FC2 → Combine；
- 共标注 8 条 memory 优化指令：6 处 `--offload-modules=`（mlp_norm、core_attn、attn_proj、expert_fc1、moe_act 等），2 处 `--recompute-modules=`（layernorm、moe_act），combine 前输出标为 "Discard"。

**2) 论证结论**：同一 MoE block 内可按子模块颗粒度差异化选择 offload 与 recompute，二者互补（精度感知 vs CPU offloading）以压低显存峰值。

**3) 论文作用**：与 Table 10（VPP 不对称切分）并列，构成 Megatron-Core "细粒度显存优化"的两大支柱——切分+重计算/卸载共同支撑 DeepSeek-V3 级 MoE 训练。

（约 220 字）

### Table 11 (p.69) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab11.png]]
> [!quote] caption
> Unified throughput benchmarks (per-GPU figures) for two mixture-of-experts models on NVIDIA GB300, GB200, and H100. All configurations use force-balanced routing. The Dtype column specifies the FP8

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读（Table 11）**

**1) 核心对象与数据**：该表对比 DeepSeek-V3 与 Qwen3-235B 两个 MoE 模型在 GB300/GB200/H100 三代硬件上的单卡吞吐（Per-GPU TF 与 Tokens/s/GPU），均采用 force-balanced 路由，Seqlen 多为 4096，末行覆盖长序列 131,072。数据呈梯度递增：Qwen3-235B 在 H100（BF16）为 320 TF → GB200（MXFP8）919 TF → GB300（MXFP8）974 TF；DeepSeek-V3 同趋势，从 368 TF 升至 1233 TF。

**2) 关键技术结论**：a) 硬件代差显著——Blackwell（GB300/GB200）相比 Hopper（H100）吞吐提升约 2.5–3×；b) FP8 量化（MXFP8 vs BF16）带来 ~20% 增益；c) 长序列场景下 Tokens/s/GPU 下降（1556 vs 6583），暴露 attention 开销瓶颈。

**3) 论文链路作用**：作为最终端到端验证，证明 Megatron-Core 在最新 Blackwell 平台上对大规模 MoE 模型的统一吞吐竞争力，并量化 FP8/路由/硬件协同的工程收益。

### Table 12 (p.70) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab12.png]]
> [!quote] caption
> Impact of parallelism strategies on memory and communication. d = parallelism degree. †Requires distributed optimizer (--use-distributed-optimizer).

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 12 以并行度 d 为度量，量化 TP/EP/PP/CP/DP 五种策略在**峰值激活、权重内存、优化器状态、逐层通信**四项的影响：TP 三者均降至 1/d（配 SP）但通信最高；EP 仅切分 MoE 权重、激活近 1；PP 需 VPP 才抑制激活膨胀；CP 激活 1/d 但权重不切分；DP 仅分优化器状态（†需分布式优化器），通信最低。

论文借此论证：MoE+Transformer 万卡训练须**多策略复合**——TP/EP 削减权重复制与计算、PP 消除流水线气泡、CP/DP 配分布式优化器控制状态内存。

该表与 Figure 12（FSDP 双缓冲消除分配开销、启用 NCCL User Buffer）互补，共同构成大规模 MoE 训练**内存与通信基础设施**的系统级论证支撑。

### Table 13 (p.72) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab13.png]]
> [!quote] caption
> Memory bottleneck solutions.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 13 解读：**

Table 13 列出 5 种内存瓶颈优化方案，按 Overhead 分两组：

- **Low 组**（3 项）：FP8 Training（§4.1.3，命令 `--fp8-format --fp8-recipe`）、Selective Recomputation（§4.1.4，`--recompute-granularity --recompute-modules`）、Precision-Aware Optimizer（§4.1.6，`--use-precision-aware-optimizer`）；
- **Medium 组**（2 项）：Activation Offloading（§4.1.5，`--fine-grained-activation-offloading --offload-modules`）、Optimizer Offloading（§4.1.6，`--offload-optimizer-states`）。

每行附命令行配置与论文章节索引。

**关键结论**：论文据此论证内存优化存在清晰代价梯度——应优先采用低开销方案（精度压缩 / 选择性重计算），仅在内存仍受限时才启用 offload 类中等开销手段。

**论文作用**：与 Table 14（通信瓶颈）并列，构成 Megatron-Core MoE 可扩展训练中"profiling 识别瓶颈 → 对照查表 → CLI 配置落地"的调优决策链路，是性能优化章节的实操指南。

### Table 14 (p.72) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab14.png]]
> [!quote] caption
> Communication bottleneck solutions.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1）核心对象与结构：** 图像仅显示该表所在章节的标题"Communication Bottleneck (Communication Wall)"及症状描述（profile显示collective operations耗时显著），并指明需查Table 14定位对应优化方案。表格主体未在图像中呈现，仅可读到caption"Communication bottleneck solutions"，推测表格按"瓶颈类型（如all-to-all dispatch/combine、DP/TP/EP通信）→症状表现→对应优化手段（融合kernel、HybridEP、grouped GEMM等）"逐行列出。

**2）关键技术结论：** 作者主张MoE大规模训练中通信墙普遍存在，需先profile定位瓶颈（集合通信占比），再对症下药：dispatch/combine瓶颈用HybridEP融合调度，TP/DP瓶颈用张量并行融合，EP负载不均用token dropping或capacity factor调节。

**3）论文整体作用：** 该表是Megatron-Core的"排错速查表"，与前述各章节HybridEP、Expert Parallel、GroupedMLP等优化形成闭环——既给出理论方案，又提供实战调优路径，是将技术成果落地为可操作指南的关键桥梁。

### Table 15 (p.73) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab15.png]]
> [!quote] caption
> CPU overhead bottleneck solutions.

> [!tip] 表格解读（多模态）
> 【图文联合解读】## 图文联合解读

**核心对象与数据**：Table 15 列出 1 条 CPU 瓶颈诊断记录——**Symptom**："Nsight Systems 时间线显示 GPU kernel 间存在间隙，CPU 无法及时下发 kernel"；**Solutions**："通过减少 kernel launch 次数 + 启用 CUDA Graphs 来削减 host-side 开销"。

**关键技术结论**：当 profiler 揭示 CPU 是瓶颈（非 GPU）时，论文给出的双管齐下策略——① 算子融合减少 launch 次数；② CUDA Graph 捕获/重放，将多次 launch 合并为一次图提交，绕过 CPU launch latency。

**论文链路作用**：该表属于"性能诊断→根因定位→优化处方"方法学的一环，与前文 GPU 侧优化（如 Fig 15 HybridEP combine kernel）共同构成 MoE 端到端训练调优指南——既优化 GPU kernel 本身，也消除 CPU launch overhead 造成的 stall gap，二者缺一不可。

### Table 16 (p.73) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab16.png]]
> [!quote] caption
> Computation bottleneck solutions.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 16 图文联合解读：**

**1) 核心对象与结构：** 表列出三项针对"计算瓶颈（Compute Efficiency Wall）"的优化方案，三列分别为 Optimization / Config / Reference：(a) 关闭 Python GC，配置 `--manual-gc --manual-gc-interval 10`；(b) 减少 kernel 启动次数，方法是降低 TP 或增大 MBS；(c) 启用 CUDA Graphs，配置 `--cuda-graph-impl transformer_engine`，详见 §4.3.6。

**2) 关键结论：** 针对细粒度 MoE 架构因 GEMM 过小导致 GPU SM 利用率低下的问题，应从"批处理/融合/低精度"三方面提升 kernel 效率——通过减少 Python GC 与 kernel launch 开销、并以 CUDA Graphs 捕获 replay 整段计算图，可显著缓解主机侧与 launch 侧的 compute wall。

**3) 论文作用：** 该表隶属于 MoE 训练瓶颈排查手册，与 Figure 16（all-to-all 通信 overlap）并列，分别从"通信"与"计算"两端给出可落地的工程调优清单，构成 Megatron-Core MoE 训练栈的完整 performance recipe。

### Table 17 (p.74) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab17.png]]
> [!quote] caption
> DeepSeek-V3 final optimized configurations on GB200 and H100. † Parallel Folding is used; TP

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 17 解读**

**核心数据**：对比 GB200（256 卡）与 H100（1024 卡）上 DeepSeek-V3 最终配置——并行度分别为 TP/PP/EP=1/4/64 与 2/8/64，VPP=4，GBS/MBS/SeqLen=8192/1/4096；GB200 采 MXFP8+HybridEP+CUDA Graphs+仅 mlp 重算，性能 1048 TFLOPS/GPU；H100 采 FP8-Blockwise+DeepEP+扩展重算（mlp/mla_up_proj/moe_act/layernorm）+ EP all-to-all overlap，性能 368 TFLOPS/GPU。

**关键结论**：同一框架下两平台通过差异化组件组合分别逼近硬件最优——GB200 借助低通信开销与 CUDA Graph 捕获获得约 2.85× H100 的单卡吞吐，H100 须以更激进的算子重计算换取显存与以 all-to-all overlap 掩盖通信，体现 Megatron-Core 配置的可移植性。

**论文作用**：作为端到端实证 case，将并行策略、精度、调度、重计算等组件联合调优落地于真实 DeepSeek-V3 规模。

### Table 18 (p.74) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab18.png]]
> [!quote] caption
> DeepSeek-V3 optimization summary by platform.

> [!tip] 表格解读（多模态）
> 【图文联合解读】【对象与结构】Table 18 横比 GB200/H100 两平台在 DeepSeek-V3 上的五类优化配置（并行/精度/显存/通信/计算效率）。共性项：均用 Parallel Folding Flexible VPP、记忆高效 permutation、细粒度重计算、FP8 主权重、低精度 optimizer state。差异项：精度 GB200 为 MXFP8、H100 为 FP8-Blockwise；显存 GB200 额外支持 optimizer states offloading；通信 GB200 用 HybridEP、H100 用 DeepEP EP overlap；计算效率 GB200 叠加 CUDA Graphs 与 CPU 侧优化，H100 仅基础 kernel fusion。

【关键结论】Megatron Core 为 DeepSeek-V3 提供按平台定制的端到端优化栈——GB200 借新硬件（MXFP8/更大显存）实现更激进精度与存储优化，H100 以成熟方案保证吞吐可复现。

【链路作用】作为全栈配置清单，与 Figure 18（EP a2a overlap）互补，串联路由→通信→计算三层融合，共同支撑论文关于 MoE 大规模训练在高吞吐与扩展性上工程可达性的论证。

### Table 19 (p.86) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab19.png]]
> [!quote] caption
> Notation and abbreviations used throughout this report.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表19是全篇符号索引，非结果表。它定义E（每层专家数）、K（每token激活数，K≤E）、h（隐藏维）；Nactive∝K，Ntotal∝E。训练量含T（每GPU token）、B（每批token）、S（序列长）、L（MoE层数）；并行含TP/PP/CP/DP/EP/ETP/EDP/VPP，批配置为MBS/GBS/GA，精度为BF16、FP8-BLK、MXFP8。它统一容量、负载和性能口径，支撑交错PP的通信重叠、MFU对比与跨实验复现。

### Table 20 (p.87) ⭐深度解读
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-tab20.png]]
> [!quote] caption
> Parallelism and training configuration details for benchmark entries reported in Table 11 .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 20 图文联合解读**

**核心对象与数据：** 该表列出 Table 11 基准测试条目的并行策略与超参配置，涵盖两个 MoE 模型（DeepSeek-V3、Qwen3-235B）在三种硬件（GB300/GB200/H100）和三种精度（MXFP8/BF16/FP8-BLK）下的 9 组配置。表格纵向对比 TP、PP、CP、EP、VPP、MBS、GBS 等并行/批维组合，横向给出吞吐量（TF）。例如 DeepSeek-V3 在 GB300+256 GPU+MXFP8+4k seqlen 下峰值达 1233 TF（TP1 PP4 EP64），而 H100+1024 GPU+FP8-BLK 同模型仅 368 TF。

**关键技术结论：** MXFP8 精度普遍优于 BF16/FP8-BLK（如 GB200 上 DeepSeek-V3 从 857→1048 TF），GB300 吞吐领先；EP（专家并行）规模高达 32–64，是 MoE 扩展核心；长序列 128k 通过 CP=4 实现，仍保持 1150 TF，验证 Megatron-Core 在异构硬件与多精度下的 MoE 大规模训练可扩展性。

**论文链路作用：** 作为 Table 11 的"配置脚注"，提供可复现性细节，与正文吞吐数字互为佐证，共同支撑 Megatron-Core 支持 MoE 端到端高效训练的工程主张。

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