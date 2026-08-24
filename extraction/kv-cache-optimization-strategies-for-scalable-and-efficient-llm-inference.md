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

图示展示了自回归生成的两个连续步骤（Step 1、Step 2），序列由"The"、"apple"、"tas"等青色 token 框组成，曲线箭头表示当前新 token 对所有历史 token 的注意力依赖；右下方粉色框标注"KV Cache"，用于存储历史 token 的 K、V 矩阵。

**核心结论：** 图示直观论证 KV cache 的必要性——若无缓存，每步都需从头重算所有历史 token 的 K、V，时间复杂度为 O(n²)；借助缓存复用，仅需计算新增 token，使单步注意力降为 O(n)。

**论文作用：** 作为 Figure 1 置于引言，奠定全文优化动机，后续章节围绕"如何更高效地压缩/共享该缓存"展开，属于全文技术链路的问题定义与起点。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig02.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p03.png]]*
> [!quote] caption
> Data-flow of the KV cache within a single transformer layer. Input token xt fans into three projections; Kt and Vt are appended to their respective caches (teal); Qt attends over the full caches to produce output ot. Cache size grows as O(T) per head per layer.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

1) **核心对象与结构**：图示单层 Transformer 内 KV cache 的数据流。输入 token $x_t$（橙色）经三个投影 $W_Q, W_K, W_V$ 分流：$Q_t$（黄色，左侧）无需缓存；$K_t, V_t$（teal 蓝绿）依次 append 到各自的 cache $K_c=[K_1,\ldots,K_t]$、$V_c=[V_1,\ldots,V_t]$（teal 框标注缓存区）。底部给出注意力的完整计算式 $\mathrm{softmax}(Q_tK_c^\top/\sqrt{d_k})V_c$。右侧橙色标注明确指出缓存体量为 $t\times d_v$，每头每层线性增长。

2) **关键技术结论**：teal 色块直观看清"被缓存的对象"就是 K、V 两路；其大小随已解码 token 数 $t$ 以 $O(T)$ 增长，逐 token 累积、不可压缩释放。这正是后文所有 KV cache 优化策略（量化、淘汰、共享、压缩、分页等）共同针对的内存瓶颈来源。

3) **论文链路作用**：作为全文"问题定义"奠基图——在介绍任何优化方法之前，先建立 KV cache 的结构、大小与访存模式，为后续 5 大类优化技术的分类与实验对比提供统一的参照基线。

### Figure 3 (p.3) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig03.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p03.png]]*
> [!quote] caption
> KV cache memory as a function of context length for three LLaMA-2 model variants under fp16 precision.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图以32K–128K上下文为横轴、FP16 KV缓存显存为纵轴，展示LLaMA‑2 7B、13B、70B三条线性增长曲线；128K时缓存分别约64、80、40GB。虚线表示A100 80GB容量，点线表示FP16参数显存（约14、26GB）。KV缓存随序列长度持续膨胀：7B仅缓存就占64GB，计入14GB参数后几乎耗尽单卡显存，成为推理瓶颈。该图为后文缓存压缩、量化及调度卸载实验提供容量基线与必要性依据。

### Figure 4 (p.4) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig04.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p04.png]]*
> [!quote] caption
> Causal self-attention weight matrix for “The apple tastes sweet.” visualised with the Viridis colormap (dark purple = low, yellow = high). Gray cells are causally masked future tokens. Each row sums to 1 (post-softmax).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图以 4×4 因果自注意力矩阵呈现"The apple tastes sweet."的注意力分布，采用 Viridis 配色（深紫=低、黄=高），灰色表示被掩码的未来 token；右下"Query=sweet"行可读出对"apple"约 0.65（对应 caption 中 65%）、"tastes"约 0.20、"sweet"自注意约 0.10，行和归一为 1。

论文借此论证：**KV 条目重要性高度不均**——个别 token（如 sweet→apple）承载绝大部分注意力，其余条目贡献微弱。这正是 H₂O、SnapKV 等基于注意力分数驱动的 KV 淘汰策略的核心前提，为后文量化、淘汰与预算分配等优化章节提供直觉依据与动机锚点。

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

1）图示对象为KV cache矩阵X∈R^(l_prompt×d)：蓝色大矩形为完整缓存，红色虚框沿d维度（通道/列方向）取出一列，标注 s_X, z_X∈R^d，表明缩放因子与零点按"通道"逐列计算——即**per-channel quantization**沿token维度聚合统计量。

2）结合正文"K中某些维度幅度极大"的观察，该图论证：Key cache存在显著通道级异常值，故需**逐通道量化**以保留敏感维度精度；而Value无此模式，KIVI改用per-token量化，二者结合构成KIVI的核心设计。

3）该图为KIVI方法的关键可视化依据，支撑其"Key per-channel + Value per-token"非对称量化策略，为后续实验链路中实现4-bit近无损压缩提供理论直觉与方案锚点。

### Figure 9 (p.9) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig09.png]]
*整页渲染: ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p09.png]]*
> [!quote] caption
> Palu’s low-rank projection method for KV-cache reduction. A weight matrix W of linear projection is decomposed into two low-rank matrices. Input X is down-projected to a latent representation H, which is cached. Y can be reconstructed from H using the up-projection matrix B. [19]. 9

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心对象与结构**：图示 Palu 的低秩 KV-cache 压缩流——原始线性投影权重 W 被分解为下投影矩阵（左侧输入 X 块）与上投影矩阵 **B**（底部红块）；蓝色"Original KV"框中为完整输出 **Y**，红色文字"**Cache H instead of Y**"标示被替换的缓存对象。虚线箭头表示下投影到低维隐表示 **H**，实线箭头表示由 B 重建回 Y。

2) **关键结论**：推理时不再缓存完整 K/V 张量 Y，而只缓存经低秩压缩后的 H；Y 可通过 Y ≈ B·H 低成本重建，从而以 rank 比例缩减 KV-cache 显存，同时保持输出近似等价。

3) **论文作用**：作为 Palu 章节的方法示意图，为"低秩投影压缩 KV-cache"这一核心论点提供直观机制说明，支撑后续实验在长上下文、多 batch 推理场景下显存与吞吐收益的论证。

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
> 【图文联合解读】**图文联合解读：**

图示上方"标准线性注意力"为**单层顺序链**：每步接收Q、K、V——顶部为3维查询向量、底部为3×3键值矩阵，经单节点处理后水平传递历史状态，复杂度O(N)；下方"对数线性注意力"采用**双层分层结构**：底层K、V先经多个分桶节点并行聚集，再通过⊕加法运算合并至上层节点，形成对数级深度的递推架构。

该对比论证关键结论：标准线性注意力复杂度低但只能拟合全局线性关系、表达力受限；分层对数线性结构以近线性代价换来更强的近似能力。在论文中，此图位于**注意力机制综述**背景章节（[30]引文），用于引出"局部线性注意力"等改进思路，为后续KV-Cache压缩、稀疏化等核心方案奠定理论与结构基础。

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
> 【图文联合解读】表1将KV Cache优化技术归为5类、共计28种代表方法：Cache Eviction（H2O、SnapKV等9种）、Cache Compression（KIVI、MiniCache等4种）、Hybrid Memory（PagedAttention、InfiniGen等7种）、New Attention（KIMI Linear等4种）、Combination（FlexGen、ShadowKV等4种）。每类对应不同优化目标（内存/吞吐/TTFT/速度），并以精度、硬件需求、设计复杂度为代价，分别适用于长上下文单请求、边缘/超长上下文、多租户数据中心、智能体任务及消费级硬件等场景。承接图1对KV Cache必要性的阐述，该表构建了"目标—权衡—方法—适用场景"四维分类坐标，为后续逐节技术分析与本文方法的横向定位提供全局参照框架。

### Table 2 (p.0) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-tab02.png]]
> [!quote] caption
> Summary of KV Cache eviction techniques

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 2 以 Method/Mechanism/Phase/Overview 四列横向对比 9 种 KV Cache 淘汰技术，按执行阶段分布：Prefill 阶段 5 种（NACL、InfiniPot、KVzip 等），After Prefill 阶段 2 种（SnapKV、Ada-KV），Decoding 阶段 3 种（H2O、HASHEVICT、MorphKV），RocketKV 横跨两阶段。机制层面涵盖重要性评分（H2O、KVzip）、观察窗投票聚类（SnapKV）、LSH 哈希近似（HASHEVICT）、上下文蒸馏（InfiniPot）、相关性筛选（MorphKV）、代理-随机混合（NACL）、粗排+细选两阶段压缩（RocketKV）、跨头动态预算（Ada-KV）。

结合图 2 所示单层 KV cache 以 O(T) 线性膨胀的瓶颈，该表论证：单一固定策略难以兼顾精度与效率，淘汰须按 prefill/decoding 阶段、跨注意力头差异化设计，为论文后续提出阶段感知+预算自适应的统一框架奠定分类基准与对比基线。

### Table 3 (p.0) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-tab03.png]]
> [!quote] caption
> Cache Compression Methods Comparison Table

> [!tip] 表格解读（多模态）
> 【图文联合解读】表格横向对比KIVI、KVQuant、MiniCache、PALU四种KV cache压缩方案，沿**机制/粒度/异常值处理**三维度展开：KIVI与KVQuant均走量化路线（前者K/V非对称、后者Key在RoPE前per-channel NUQ），Value均per-token；MiniCache采用跨层合并，粒度NA；PALU用per-token per-head group低秩潜向量做隐维压缩。论文借此论证压缩策略多样（量化、合并、降维并行），且各方法均预留全精度"逃生通道"（残差缓存/稀疏fp16/不可合并对/关键层高秩）兜底异常值。该表作为综述型基线，为后文各方法实验对比提供分类依据。

### Table 4 (p.0) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-tab04.png]]
> [!quote] caption
> Hybrid Memory Solutions Comparison Table

> [!tip] 表格解读（多模态）
> 【图文联合解读】表4按"方法—卸载目标—机制—关键优化"四列对比7种KV-Cache混合内存方案：6/7方案卸载至CPU DRAM，唯INF2采用Host+NVMe SSD（CSDs）；机制涵盖分页、注意力推测、SLO分层、近存计算、异步重算重叠、参数重映射、零拷贝传输。该表论证混合内存核心瓶颈在于PCIe带宽与CPU开销，且部分机制（如InfiniGen的注意力推测）正建立在KV条目注意力分数高度不均的前提之上，与Figure 4结论相呼应；该表梳理出从分片→推测预取→近存计算的演进脉络，为本文新策略提供设计空间的定位基准。

### Table 5 (p.0) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-tab05.png]]
> [!quote] caption
> Attention Variants – Mechanisms, Complexities, and Features

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 解读**

**核心内容**：横向对比 5 种注意力变体的机制与复杂度——Softmax（SDP+MHA，O(T²)/O(T)/O(T)）、Linear（核点积替换 softmax，O(T)/O(1)/O(1)）、Log Linear（对数增长状态，O(TlogT)/O(logT)/O(logT)）、Local Linear（query 局部线性拟合，O(T²)/~O(T)/O(T)）、KIMI Linear（KDA+MLA 混合，主要 O(T)/O(1)/O(1)）。

**关键结论**：KV 缓存优化的底层在于按序列长 T 选择注意力机制——Linear/Log Linear/KIMI Linear 可将解码内存压至 O(1)，Softmax 高表达却伴 O(T) 内存开销；Local Linear 保留 O(T) 空间换取更优偏差-方差；KIMI Linear 需以 3:1 与 full attention 混合以维持全局信息流。

**论文作用**：与 Figure 5 分类法互为补充，作为"机制选择层"决策表，为后续量化、稀疏化等 KV 优化策略提供底层依据。

### Table 6 (p.18) ⭐深度解读
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-tab06.png]]
> [!quote] caption
> Comparison of KV Cache Optimization Techniques

> [!tip] 表格解读（多模态）
> 【图文联合解读】表6以"技术/内存/加速/精度/权衡"五列横向对比约30种KV Cache优化方法。关键数据：淘汰类——H2O内存减5–10×、吞吐↑29×；RocketKV压缩高达400×、加速3.7×；KIMI KV减75%、1M上下文加速6×。量化类——KIVI内存降2.6×；KVQuant省3.7–6.9×；PALU约50%。卸载类——FlexGen吞吐↑40–100×；LayerKV TBT改善69×；TailorKV省GPU 73.8%。架构类——LinearAttention长序列加速4000×。表中各列同时标注痛点：精度波动、反量化开销、PCIe瓶颈。

该表与Fig.6注意力图互补——图示策略原理、表给量化证据——为论文论证"无单一方案占优，需淘汰+量化+卸载融合以兼顾内存、吞吐与精度"提供关键实证支撑，是后续章节讨论混合方案与系统设计的依据。

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