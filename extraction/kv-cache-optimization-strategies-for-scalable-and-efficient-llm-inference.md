---
paper_num: "62"
title: "KV Cache Optimization Strategies for Scalable and Efficient LLM Inference"
authors: ""
date: "2026/3/20"
arxiv: "https://arxiv.org/abs/2603.20397"
pdf: "papers/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference.pdf"
slug: "kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference"
tags: [kv-cache]
---

# KV Cache Optimization Strategies for Scalable and Efficient LLM Inference

> [!abstract] 摘要（原文）
> The key-value (KV) cache is a foundational optimization in Transformer-based large language models (LLMs), eliminating redundant recomputation of past token representations during autoregressive generation. However, its memory footprint scales linearly with context length, imposing critical bottlenecks on GPU memory capacity, memory bandwidth, and inference throughput as production LLMs push context windows from thousands to millions of tokens. Efficient KV cache management has thus become a first-order challenge for scalable LLM deployment. This paper provides a systematic review of recent KV cache optimization techniques, organizing them into five principal directions: cache eviction, cache compression, hybrid memory solutions, novel attention mechanisms, and combination strategies. For each category we analyze the underlying mechanisms, deployment trade-offs, and empirical performance across memory reduction, throughput, and model accuracy metrics. We further map techniques to seven practical deployment scenarios, including long-context single requests, high-throughput datacenter serving, edge devices, multi-turn conversations, and accuracy-critical reasoning, providing actionable guidance for practitioners selecting among competing approaches. Our analysis reveals that no single technique dominates across all settings; instead, the optimal strategy depends on context length, hardware constraints, and workload characteristics, pointing toward adaptive, multi-stage optimization pipelines as a promising direction for future research.

## 元信息
- **发表日期**: 2026/3/20
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2603.20397
- **本地 PDF**: `papers/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference.pdf`
- **页数**: 24

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig01.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p02.png]]*
> [!quote] caption
> Autoregressive generation, at each step the new token (orange) attends to all prior tokens (cyan). Without caching, keys and values for every past token would be recomputed from scratch at each step. The KV cache avoids this by storing and reusing them.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）图示自回归两步生成过程：Step1序列"The apple tastes"（青色历史token），橙色"?"经attention对全部历史做预测，输出"sweet"；Step2扩展为"The apple tastes tastes sweet"再预测"."；底部粉色框标注KV Cache存储历史token的K/V。

2）论证结论：新token每步需attend全部历史K/V，无缓存时每步从零重算开销巨大；KV Cache通过存并复用历史K/V避免冗余计算，显著降低推理时延。

3）论文作用：作为引言Figure1奠定核心问题与优化动机，后续章节围绕KV Cache压缩、共享、淘汰等策略展开，构成全文方法链路的起点。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig02.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p03.png]]*
> [!quote] caption
> Data-flow of the KV cache within a single transformer layer. Input token xt fans into three projections; Kt and Vt are appended to their respective caches (teal); Qt attends over the full caches to produce output ot. Cache size grows as O(T) per head per layer.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图刻画单Transformer层KV Cache数据流：输入token $x_t$经$W_K$、$W_Q$、$W_V$三路投影得$K_t$、$Q_t$、$V_t$；$K_t$、$V_t$以"append"方式累入缓存$\mathbf{K}_c=[K_1..K_t]$（$t \times d_k$）与$\mathbf{V}_c=[V_1..V_t]$（$t \times d_v$），teal高亮；$Q_t$对完整缓存执行$o_t=\text{softmax}(Q_t\mathbf{K}_c^\top/\sqrt{d_k})\mathbf{V}_c$注意力运算。

原文借此论证关键结论：每头每层缓存随序列长度$T$以$O(T)$线性增长，构成LLM推理的显存与带宽瓶颈。

论文作用：该图为全篇"问题基线"，Table 2所列eviction、量化、共享、分页等优化策略均围绕缓解此$O(T)$增长展开。

### Figure 3 (p.3) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig03.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p03.png]]*
> [!quote] caption
> KV cache memory as a function of context length for three LLaMA-2 model variants under fp16 precision.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示LLaMA-2三种变体（7B、13B、70B-GQA）在fp16精度下KV缓存随上下文长度（0–128K）的线性增长，每token开销分别为0.50/0.78/0.31 MB。虚线标注GPU显存上限（RTX 4090:24 GB、A100:80 GB），点线标注参数权重（7B:14 GB、13B:26 GB）。关键发现：7B模型KV缓存在约48K token处即突破RTX 4090显存上限（图中"7B KV"箭头），128K时达~64 GB——长上下文场景下KV缓存已超越参数成为主存瓶颈。此图作为动机图，为后文Table 3所列KV压缩方法（量化、稀疏、共享等）的必要性提供量化论证。

### Figure 4 (p.4) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig04.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p04.png]]*
> [!quote] caption
> Causal self-attention weight matrix for “The apple tastes sweet.” visualised with the Viridis colormap (dark purple = low, yellow = high). Gray cells are causally masked future tokens. Each row sums to 1 (post-softmax).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

①**核心对象**：4×4 因果自注意力权重矩阵（Query="The/apple/tastes/sweet"×Key 同四词），行和归一为1。量化数据："sweet"行注意力分布为0.05/0.65/0.20/0.10，峰值0.65落于"apple"列（橙色框标注）；其余三行对角自注意分别为1.00、0.70、0.55。Viridis配色，深紫=低、黄=高，灰格为未来掩码。

②**关键结论**：注意力分布严重偏斜——后序 token（"sweet"）将65%权重集中于非自身的早期 token（"apple"），说明多数 KV 对仅承载低权重贡献，是 KV Cache 淘汰（eviction）的天然候选。

③**论文作用**：该图为后续所有缓存压缩/淘汰策略（如低权重 KV 驱逐、混合内存方案）提供动机与直觉支撑，是论证"KV Cache 可稀疏化而不损性能"的入门示例。

### Figure 5 (p.5) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig05.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p05.png]]*
> [!quote] caption
> Taxonomy of KV cache optimization techniques surveyed in this paper, organized into five major categories.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图以"KV Cache Optimization"为根节点，向下展开五条并列分支：①Cache Eviction（H₂O、SnapKV、NACL、Ada-KV）；②Cache Compression（KIVI、PALU、MiniCache、KVQuant）；③Hybrid Memory（PagedAttention、InfiniGen、LayerKV）；④New Attention Mechanism（Linear、Log-Linear、KIMI Linear）；⑤Combination Methods（FlexGen、ShadowKV、TailorKV）。原文借此论证：KV 缓存优化是从丢弃、压缩、存储分配、注意力改造到组合方案的多维系统化路径，而非单一手段。该分类法为后续各章节的方法对比、性能基准测试与综述分析提供了统一归类框架，是整篇 survey 的方法学骨架。

### Figure 6 (p.6) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig06.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p06.png]]*
> [!quote] caption
> Upper plots illustrate symbolic plots of an attention map deploying different KV cache policies in LLM generation. Lower right: contrasts their accuracy-memory trade-off. Left: the overview of H2O framework [1]. A key challenge in eviction-based methods is identifying which tokens carry long-range importance. One approach tracks accumulated attention scores and treats high-scoring tokens as essent

> [!tip] 技术解读（多模态）
> 【图文联合解读】图6以4个10×10因果注意力图比较动态、步幅、局部静态稀疏及带H2O的策略；H2O额外标出高注意力列，左下图以0.2、0.1、0.1、0.6（累加1.4、1.5、0.5、0.6）说明按累计注意力保留KV。右下示意约0–100%内存压缩、50–80%准确率的权衡：固定策略约60%后明显降精度，H2O到约90%仍接近80%。该图以“近期+高重要性远距token”的淘汰机制连接缓存结构与评测，作为框架概览和概念性权衡说明，并非完整实验表。

### Figure 7 (p.7) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig07.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p07.png]]*
> [!quote] caption
> The graph shows the simplified workflow of SnapKV, where the orange area represents the cluster of features per head selected by SnapKV. These features are then used to form new Key-Value pairs concatenated with the features in the observation window. Together, the selected prefix and observation windows constitute the new KV cache utilized for the generation. [2].

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图7图文联合解读：**

**1）核心对象与结构：** 图示SnapKV的三阶段压缩流程。输入序列KV按"层"维度展开，含白色Prefix与绿色Obs.window（观察窗）；中间通过Attention Weight Calc.（以观察窗为query）与Voting机制，在每层每个注意力头投票筛选出橙色重要特征；底部经Clustering聚类后拼接Obs.window，产出Compressed KVs。右侧以Q4财报问答为例，验证压缩后仍可定位"R&D expenses"等关键事实。

**2）关键技术结论：** Prefix中注意力权重具有高度集中性与可聚类性，仅保留每头重要特征簇即可近似全量KV，论证了"少而精"的KV即可支撑高质量生成。

**3）论文作用：** 作为SnapKV核心方法示意图，与全量KV基线对比，证明长上下文KV cache可大幅压缩而生成质量几乎无损，为高效推理链路提供方法支撑。

### Figure 8 (p.9) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig08.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p09.png]]*
> [!quote] caption
> Definition of per-token and per-channel quantization. X ∈Rlprompt×d is the key/value cache, where lprompt is the number of tokens and d is the number of channels. zX is the zero-point, and sX is the scaling factor.. [5]. whose magnitudes are very large”; whereas for value cache, “there is no obvious outlier pattern”. Based on this insight, KIVI applies per-channel quantization for keys and per-tok

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构**：图示KV缓存矩阵 X∈R^(l_prompt×d) 的两种量化粒度。左图 *per-token* 对每一行（一个 token）共享一组缩放因子与零点 s_X, z_X ∈ R^(l_prompt)；右图 *per-channel* 对每一列（一个通道）共享 s_X, z_X ∈ R^d；红色虚线框分别圈出被量化的行/列单元。

**2) 关键技术结论**：key cache 存在幅度很大的 outlier，而 value cache 无明显 outlier。KIVI 据此对 key 采用 per-channel、对 value 采用 per-token 量化，使 outlier 所在通道获得更细粒度的量化参数，从而保留关键信息并降低误差。

**3) 在论文中的作用**：作为 KIVI 混合量化策略的概念基础，为后续实验的精度–效率权衡提供设计依据。

### Figure 9 (p.9) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig09.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p09.png]]*
> [!quote] caption
> Palu’s low-rank projection method for KV-cache reduction. A weight matrix W of linear projection is decomposed into two low-rank matrices. Input X is down-projected to a latent representation H, which is cached. Y can be reconstructed from H using the up-projection matrix B. [19]. 9

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图9展示Palu低秩压缩的两条对比路径：上行为原始线性投影 X→W→Y（缓存完整KV Y）；下行为分解路径，将W离线分解为下投影A与上投影B，执行 X→A→H→B→Y，仅缓存低维隐层H而非Y。原文借此论证：W≈BA，rank远小于dim(d)，故|H|≪|Y|，可在推理时即时通过B重建Y，从而以极小算力开销换取KV-cache显存与带宽的大幅压缩。该图是Palu整篇方法的基石机制，后文实验均围绕"以H替Y"展开压缩率、吞吐与精度权衡的验证。

### Figure 10 (p.11) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig10.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p11.png]]*
> [!quote] caption
> vLLM system overview [22]. 11

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示vLLM分布式推理架构：1个**Scheduler**（绿色）调度N个**Worker**（Worker 0…N−1），每Worker含一个**Cache Engine**与一个**Model Shard**（各占一块GPU）；**KV Cache Manager**持有两张**Block tables**（图中以粉色列高亮，类比OS页表），下接**CPU Block Allocator**与**GPU Block Allocator**两级分配器，跨设备管理KV块。

原文据此论证三条关键技术结论：①KV缓存采用**块级（page-like）**粒度管理以消除碎片；②模型按Shard在多Worker间并行，调度与缓存解耦；③CPU↔GPU两级分配器支撑KV块在主存与显存间的灵活映射，是后续swap/offload/prefix-sharing等优化的前提。

该图位于论文第11页，作为后续PagedAttention、内存交换、跨设备卸载等KV优化策略讨论的**系统基线参照框架**，统一读者对vLLM组件边界的认知。

### Figure 11 (p.12) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig11.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p12.png]]*
> [!quote] caption
> Operation flow of the prefetching module of InfiniGen. [23]. A layer-wise KV cache management strategy is proposed in LayerKV [24]. The core concept is to split KV cache by layers, keeping only a subset of layers on the GPU during the prefill stage while offloading some layers to CPU memory to reduce Time to First Token (TTFT). Prefill time refers to the time for the GPU to compute the first token

> [!tip] 技术解读（多模态）
> 【图文联合解读】**核心对象与结构：** 图示InfiniGen预取模块三阶段操作流——Offline（Skewing离线分析token重要性）、Prefill（Partial Weight Idx Generation生成选中token索引）、Decoding（逐层推理）。GPU/CPU双时间轴并行：GPU执行Layer(i-1)的KV Sel.→Attention→FFN时，CPU同步Prefetching；Layer i改用Light Attention接收CPU回传的Selected Keys/Values。

**关键技术结论：** 离线Skewing识别重要token，Prefill阶段仅生成部分权重索引；Decoding利用层间计算间隙在CPU预取目标K/V，使数据传输与GPU计算重叠，隐藏访存延迟。

**论文作用：** 作为"预测式预取"代表方案，与LayerKV的层间切分策略形成对比，论证KV-cache优化机制多样化（重要token预测+CPU-GPU预取重叠），支撑长序列LLM推理降开销讨论。

### Figure 12 (p.15) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig12.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p15.png]]*
> [!quote] caption
> Standard linear attention (top) vs. loglinear attention (bottom). The input consists of query, key, and value vectors [30]. at nearby keys and averages their value; while Linear Attention is alike global linear regression because it fits a global straight line for all data. Based on such observation, the authors proposed Local Linear Attention, which is similar to local linear regression. This ena

> [!tip] 技术解读（多模态）
> 【图文联合解读】## Figure 12 图文联合解读

**1) 核心结构对比（具体、量化）：**
- **上图（Standard Linear Attention）**：8 个同质紫色方块水平链式串联，每个节点结构完全相同——上方接收 query（单列向量），下方接收 key 与 value（各 2 列向量），呈单层均匀网络。
- **下图（Log-Linear Attention）**：同样 8 个 token 位置，但节点呈**多层金字塔/树状层次结构**——底层连接 K/V，深蓝色中间节点通过 ⊕ 加法逐层聚合相邻邻域的表征，再传到上层浅色节点，实现分层归并。

**2) 关键技术结论：**
原文用此对比论证：标准线性注意力 ≈ "全局线性回归"（一条直线拟合所有数据，难以捕捉局部模式）；Log-Linear 通过分层邻域聚合 ≈ "局部线性回归"，天然引入**局部归纳偏置**，从而优于全局线性方案。

**3) 在论文整体链路中的作用：**
该图位于第 15 页综述部分，作为**替代注意力机制的动机图**，从"理论类比"过渡到"方法设计"，直接启发了论文提出的 **Local Linear Attention**——融合两者优势的折中方案，是从观察 → 方案推导的关键桥梁。

### Figure 13 (p.17) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig13.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p17.png]]*
> [!quote] caption
> During Pre-filling, ShadowKV offloads the value cache to the CPU while maintaining a low-rank key cache, landmarks, and outliers on the GPU. During decoding, it employs landmarks for sparse attention. [35].

> [!tip] 技术解读（多模态）
> 【图文联合解读】图13展示ShadowKV的GPU–CPU混合架构，分两阶段：

① **Pre-filling**：GPU对Pre-RoPE Key Cache并行三条路径——SVD生成Low-rank Key Cache、RoPE&Reduce生成Landmarks、Find Outliers标记Outliers，三者均Cached于GPU；Value Cache则Offload至CPU。

② **Decoding**：Landmarks经KV Sel.判别Cache Hit/Miss，Missed Chunk IDs下发CPU做Value Cache Fetching；Low-rank Key Cache经Reconstruction+RoPE，与Outliers共同汇入Sparse Attention。

**论文作用**：该图直观论证了"低秩Key+Landmarks+Outliers驻GPU、Value卸CPU"的存储分工，以及"Landmarks引导稀疏注意力"的访存机制，是ShadowKV将KV总占用压缩至单层约2.3GB、支撑百万级长上下文推理的核心设计，构成论文KV压缩方法链的关键一环。

### Figure 14 (p.17) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig14.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p17.png]]*
> [!quote] caption
> System overview of TailorKV. Offline identification categorizes the layers into quantization-friendly and sparsity-friendly. For quantization-friendly layers, we employ aggressive static quantization. For sparsity-friendly layers, we dynamically retrieve Top-K tokens. Critical current query and critical key cache represent the outliers in the query and key cache, respectively. [36]. A sparsity-awa

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示TailorKV系统全景，分三大模块：①**离线识别**——依据注意力分数与估计稀疏度，将各层划分为Quantization Friendly或Sparsity Friendly两类；②**Prompt Encoding**——量化友好路径对Keys做Per-Channel量化、Values做Per-Token量化，结果存入Quantized KV Cache Buffer；③**Token Generation**——量化层执行混合精度矩阵乘；稀疏层则通过Critical Key Buffer（writing/reading）检索Top-K Tokens，结合Critical Current Query完成全精度矩阵乘。CPU端KV Cache Memory Pool配合Offload(1)、Prefetch(2/5)、Fetch(4)实现GPU-CPU协同；右侧Layer 0→N示意按层异构调度。

**作用**：作为方法总图，支撑"按层特性差异化压缩"的核心结论，是TailorKV端到端推理流水线的可视化总纲。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.0) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-tab01.png]]
> [!quote] caption
> Comparison of KV Cache optimization techniques

> [!tip] 表格解读（多模态）
> 【图文联合解读】表1以"技术/优化目标/权衡/代表方法/适用场景"五列，对比五类KV Cache优化：①Cache Eviction（9种方法，如H2O、SnapKV）减显存与延迟，损精度；②Cache Compression（KIVI、MiniCache等4种）压KV大小，引入反量化开销；③Hybrid Memory（PagedAttention等7种）解决TTFT与系统效率，硬件依赖高；④New Attention（Linear、KIMI Linear等4种）改复杂度但需重训；⑤Combination Methods（FlexGen等4种）平衡吞吐与延迟。

**论证结论**：五类技术并非互斥，而是覆盖"显存—吞吐—算法"三层优化，各有不同的部署代价与适用边界。

**论文作用**：作为survey总纲，为后续各章节的方法分类、实验选型与对比分析提供统一坐标系。

### Table 2 (p.0) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-tab02.png]]
> [!quote] caption
> Summary of KV Cache eviction techniques

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读**

该表横向比较 9 种 KV Cache 淘汰方法，沿 *Method–Mechanism–Phase–Overview* 四列展开：H2O 保留 Heavy-Hitter 与近期 Token（Decoding），SnapKV 通过观察窗投票聚类关键特征（After Prefill），NACL 编码期全局混合随机淘汰（Prefill），InfiniPot 通过持续上下文蒸馏支持固定预算下的"无限"上下文（Prefill），HASHEVICT 以 LSH+汉明距无注意力估计重要性（Decoding），MorphKV 关联感知选择、消除早期偏差（Decoding），RocketKV 两阶段压缩（Prefill+Decoding），KVzip 用最大交叉注意力打分（Prefill），Ada-KV 按注意力头自适应分配预算（After Prefill）。Phase 分布显示三大触发时机：Prefill 3 项、After Prefill 2 项、Decoding 3 项、RocketKV 跨两阶段。

原文借此论证：淘汰策略在**触发时点**与**重要性度量**上呈多样化，无单一最优路线。论文中它定位为相关工作综述表，为后续提出兼顾 Prefill/Decoding 的统一优化框架奠定分类基础。

### Table 3 (p.0) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-tab03.png]]
> [!quote] caption
> Cache Compression Methods Comparison Table

> [!tip] 表格解读（多模态）
> 【图文联合解读】表格从机制、粒度、离群值处理三维度对比4种KV cache压缩方法：KIVI采用Key通道级+Value token级非对称量化并保留少量fp16残差；KVQuant使用NUQ非均匀量化，将top1%离群值隔离为稀疏fp16；MiniCache通过跨层KV合并保留不可合并状态对；PALU采用隐维低秩投影重建，关键层分配更高秩。

技术结论：四类方法分别针对量化、冗余、维度三类瓶颈，但共同保留关键/离群信息的高精度处理。该表为后续实验对比和方法选择提供分类基础，是KV cache优化技术综述的核心参考，支撑论文"可扩展高效LLM推理"的方法链路。

### Table 4 (p.0) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-tab04.png]]
> [!quote] caption
> Hybrid Memory Solutions Comparison Table

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读（Table 4）**

**1）核心结构与数据：** 表4以"Method / Offload destination / Mechanism / Key optimization"四列横向对比7种KV缓存混合内存方案。7种方法中，6种（Paged Attention、InfiniGen、LayerKV、KVPR、Oneiros、CLO）均以**CPU DRAM**为卸载目的地，仅**INF2 [8]**拓展至"Host Memory + NVMe SSDs (CSDs)"，借助计算存储设备内带宽服务长上下文。机制涵盖分页、注意力规范预取、分层SLO调度、ANS近存计算、异步传输重叠、参数重映射、头级近似缓存+零拷贝等。

**2）关键技术结论：** 各方案分别针对**碎片化**（Paged Attention）、**PCIe带宽瓶颈**（InfiniGen/KVPR/CLO）、**排队时延**（LayerKV→TTFT）、**多租户显存复用**（Oneiros）、**长上下文吞吐**（INF2）等不同痛点，体现混合内存策略的多样性与互补性。

**3）论文链路作用：** 作为分类学对照表，为后续章节中作者所提方法的定位、差异化与基线比较提供完整技术谱系。

### Table 5 (p.0) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-tab05.png]]
> [!quote] caption
> Attention Variants – Mechanisms, Complexities, and Features

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 联合解读**

该表横向对比 5 种注意力变体的机制与复杂度（训练 / 解码每步 / 解码空间）：
- **Softmax**：MHA 缩放点积，三项均为 O(T²/T/T)，表达力强但开销高；
- **Linear**：用核特征图线性点积替代 softmax，全部降至 O(1)，但表达力受限；
- **Log Linear**：对数增长的隐藏状态，三项均为 O(T·logT / logT / logT)，效率–表达力折中；
- **Local Linear**：逐查询局部线性回归，三项 O(T²/∼T/T)，偏置–方差更优但代价高；
- **KIMI Linear**：KDA+MLA 混合架构（约 3:1），主要项 O(T) 而解码/空间 O(1)。

**论证结论**：纯线性注意力虽实现 O(1) 解码与 KV，但牺牲表达力；Log/Local Linear 提供中间路径；**KIMI Linear 以 3:1 混合 KDA+MLA 同时实现 O(1) 复杂度与超越全注意力的性能**，是该类方法中最优工程方案。

**论文作用**：作为 Figure 5 分类法"Attention Variants"分支的量化支撑表，为后续 KV 缓存优化策略（共享、压缩、卸载等）的复杂度基线与设计动机提供理论依据。

### Table 6 (p.18) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-tab06.png]]
> [!quote] caption
> Comparison of KV Cache Optimization Techniques

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 图文联合解读**

该表横向对比 28 种 KV Cache 优化技术，覆盖驱逐类（H2O、SnapKV、NACL、RocketKV 压缩高达 400×）、量化类（KIVI 2.6×、KVQuant 3.7–6.9×）、卸载类（PagedAttention/InfiniGen/Oneiros 等无损方案）、线性注意力类（O(1)–O(logT) 内存）及混合类（KIMI、FlexGen、ShadowKV、TailorKV），按 Memory、Speedups、Accuracy loss、Tradeoffs 四列量化呈现。

原文借此论证：单一技术难以兼顾内存、速度与精度——驱逐类加速显著但存在注意力偏差，量化类吞吐提升有限，卸载类无损但依赖 PCIe/CPU-GPU 协同，线性注意力则牺牲精度换复杂度。该表作为综述实验链路的核心汇总，为读者按场景（长上下文、低显存、极致吞吐）选型提供量化依据，凸显"组合优化"是未来方向。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
KV_{per\ token} = 2 \times H\times D \times B \times L
$$

$$
KV_{cache\ size} = KV_{per\ token} \times \mathrm{Context Length}
$$

$$
\mathrm{Score}\left( Q_i, K_j\right) = \frac{Q_i \cdot K_j^{T}}{\sqrt{d_k}}
$$

$$
\alpha_{ij} = \mathrm{softmax}\!\left( \frac{Q_i \cdot K_j^{T}}{\sqrt{d_k}} \right)
$$

$$
\mathrm{output}_i = \sum_{j} \alpha_{ij} V_j
$$

$$
\tilde Q^{(\text{layer}+1)} = X^{(\text{layer})} \cdot M \cdot W_Q^{(\text{layer}+1)}
$$

$$
V_i' = \frac{\phi(Q_i)^T \sum_{j=1}^{i} \phi(K_j) V_j^T} {\phi(Q_i)^T \sum_{j=1}^{i} \phi(K_j)}
$$

$$
V_i' = \frac{\phi(Q_i)^T S_i}{\phi(Q_i)^T Z_i}
$$

$$
S_i = \sum_{j=1}^{i} \phi(K_j) V_j^T
$$

$$
Z_i = \sum_{j=1}^{i} \phi(K_j)
$$

$$
o_t = \sum_{\ell=0}^{L-1} \lambda_t^{(\ell)} q_t^T \left(\sum_{s \in B_t^{(\ell)}} v_s k_s^T \right) = \sum_{\ell=0}^{L-1} \lambda_t^{(\ell)} q_t^T S_t^{(\ell)}
$$

$$
S_t = (I - \beta_t k_t k_t^T)\,\mathrm{Diag}(\alpha_t)S_{t-1} + \beta_t k_t v_t^T \in \mathbb{R}^{d_k \times d_v}
$$

$$
o_t = S_t^T q_t \in \mathbb{R}^{d_v}
$$

## 相关论文

- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] — A Survey on Large Language Model Acceleration based on KV Cache Management
- [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] — CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion
- [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] — IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse
- [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] — Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter

## 技术点深读（DEEP）

![[deep/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference.txt`（91318 字符）供引用检索。